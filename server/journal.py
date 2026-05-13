"""Minimal operation journal and audit log support for R1."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from typing import Any, Callable

from .models import (
    AuditEvent,
    DelegationOutcomeRecord,
    OperationJournalEntry,
    OutcomeRecord,
    StaleAdvisoryContextMarker,
)
from .replay import ReplayDiagnostics, SchemaViolation, replay_jsonl


logger = logging.getLogger(__name__)

_AUDIT_TTL_DAYS = 30

_AuditDedupKey = tuple[str, str, str | None]
_DialogueOutcomeDedupKey = tuple[str, str, str]
_DelegationOutcomeDedupKey = tuple[str, str]


@dataclass(frozen=True)
class _PruneFileStats:
    retained: int
    dropped: int
    retained_malformed: int


@dataclass(frozen=True)
class PruneSummary:
    """Flat diagnostics for a single audit/outcome prune pass."""

    audit_retained: int
    audit_dropped: int
    audit_retained_malformed: int
    outcomes_retained: int
    outcomes_dropped: int
    outcomes_retained_malformed: int
    audit_quarantined_to: Path | None = None
    outcomes_quarantined_to: Path | None = None


def default_plugin_data_path() -> Path:
    """Resolve the plugin data root.

    Falls back to a local temp-style directory when CLAUDE_PLUGIN_DATA is not
    present, which keeps tests self-contained.
    """

    env_value = os.environ.get("CLAUDE_PLUGIN_DATA")
    if env_value:
        return Path(env_value).expanduser().resolve()
    return Path("/tmp/codex-collaboration").resolve()


_VALID_OPERATIONS = frozenset(
    (
        "thread_creation",
        "turn_dispatch",
        "job_creation",
        "approval_resolution",
        "promotion",
    )
)
_VALID_PHASES = frozenset(("intent", "dispatched", "completed"))
# Field names whose values are validated as str before reconstructing a
# StaleAdvisoryContextMarker. Update if the dataclass gains a non-str field.
_STALE_MARKER_FIELDS = (
    "repo_root",
    "promoted_artifact_hash",
    "job_id",
    "recorded_at",
)
_JOURNAL_REQUIRED_STR = (
    "idempotency_key",
    "operation",
    "phase",
    "collaboration_id",
    "created_at",
    "repo_root",
)
_JOURNAL_OPTIONAL_STR = (
    "codex_thread_id",
    "runtime_id",
    "job_id",
    "request_id",
    "decision",
    "completion_origin",
)
_JOURNAL_OPTIONAL_INT = ("turn_sequence", "context_size")
_VALID_COMPLETION_ORIGINS = frozenset(("worker_completed", "recovered_unresolved"))


def _coerce_aware_utc(value: datetime, *, source: str) -> datetime:
    """Validate timezone-aware datetimes and normalize them to UTC."""

    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError(f"{source} requires a timezone-aware datetime. Got: {value!r}")
    return value.astimezone(UTC)


def _parse_aware_iso8601(value: Any) -> datetime | None:
    """Return a timezone-aware UTC datetime, or None on any failure."""

    if not isinstance(value, str):
        return None
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        return None
    if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
        return None
    return timestamp.astimezone(UTC)


def _populate_from_audit_record(
    record: dict[str, Any],
    audit_seen: set[_AuditDedupKey],
) -> None:
    action = record.get("action")
    collaboration_id = record.get("collaboration_id")
    if not isinstance(action, str) or not isinstance(collaboration_id, str):
        return
    turn_id = record.get("turn_id")
    if turn_id is not None and not isinstance(turn_id, str):
        return
    audit_seen.add((action, collaboration_id, turn_id))


def _populate_from_outcome_record(
    record: dict[str, Any],
    dialogue_seen: set[_DialogueOutcomeDedupKey],
    delegation_seen: set[_DelegationOutcomeDedupKey],
) -> None:
    outcome_type = record.get("outcome_type")
    if not isinstance(outcome_type, str):
        return
    if outcome_type == "delegation_terminal":
        job_id = record.get("job_id")
        if isinstance(job_id, str):
            delegation_seen.add((outcome_type, job_id))
        return
    collaboration_id = record.get("collaboration_id")
    turn_id = record.get("turn_id")
    if isinstance(collaboration_id, str) and isinstance(turn_id, str):
        dialogue_seen.add((outcome_type, collaboration_id, turn_id))


def _journal_callback(
    record: dict[str, Any],
) -> tuple[str, OperationJournalEntry]:
    """Validate all fields and construct a journal entry."""
    for name in _JOURNAL_REQUIRED_STR:
        if not isinstance(record.get(name), str):
            raise SchemaViolation(f"{name} missing or not a string")
    if record["operation"] not in _VALID_OPERATIONS:
        raise SchemaViolation(f"unknown operation value: {record['operation']!r}")
    if record["phase"] not in _VALID_PHASES:
        raise SchemaViolation(f"unknown phase value: {record['phase']!r}")
    for name in _JOURNAL_OPTIONAL_STR:
        val = record.get(name)
        if val is not None and not isinstance(val, str):
            raise SchemaViolation(f"{name} is not a string")
    for name in _JOURNAL_OPTIONAL_INT:
        val = record.get(name)
        if val is not None and type(val) is not int:
            raise SchemaViolation(f"{name} is not an int")
    completion_origin = record.get("completion_origin")
    if completion_origin is not None and completion_origin not in _VALID_COMPLETION_ORIGINS:
        raise SchemaViolation(
            f"unknown completion_origin value: {completion_origin!r}"
        )
    # Per-operation+phase conditional requirements.
    # Recovery (dialogue.py:446-592) relies on these fields existing for
    # specific operation+phase combinations. Without enforcement, type-valid
    # but incomplete records survive to recovery and crash with RuntimeError.
    #
    # Completed phase is excluded: production writers (dialogue.py:300-309,
    # :588-595, :688-695) emit completed as a minimal resolution marker
    # without codex_thread_id or turn_sequence. Requiring those fields
    # would reject every completed record written by production code.
    op = record["operation"]
    phase = record["phase"]
    if op == "turn_dispatch" and phase in ("intent", "dispatched"):
        if not isinstance(record.get("codex_thread_id"), str):
            raise SchemaViolation(
                f"turn_dispatch at {phase} requires codex_thread_id (string)"
            )
        if phase == "dispatched":
            ts = record.get("turn_sequence")
            if ts is None or type(ts) is not int:
                raise SchemaViolation(
                    f"turn_dispatch at {phase} requires turn_sequence (int)"
                )
    elif op == "thread_creation" and phase == "dispatched":
        if not isinstance(record.get("codex_thread_id"), str):
            raise SchemaViolation(
                "thread_creation at dispatched requires codex_thread_id (string)"
            )
    elif op == "job_creation" and phase == "intent":
        if not isinstance(record.get("job_id"), str):
            raise SchemaViolation("job_creation at intent requires job_id (string)")
    elif op == "job_creation" and phase == "dispatched":
        if not isinstance(record.get("job_id"), str):
            raise SchemaViolation("job_creation at dispatched requires job_id (string)")
        if not isinstance(record.get("runtime_id"), str):
            raise SchemaViolation(
                "job_creation at dispatched requires runtime_id (string)"
            )
        if not isinstance(record.get("codex_thread_id"), str):
            raise SchemaViolation(
                "job_creation at dispatched requires codex_thread_id (string)"
            )
    elif op == "approval_resolution" and phase == "intent":
        if not isinstance(record.get("job_id"), str):
            raise SchemaViolation(
                "approval_resolution at intent requires job_id (string)"
            )
        if not isinstance(record.get("request_id"), str):
            raise SchemaViolation(
                "approval_resolution at intent requires request_id (string)"
            )
        decision = record.get("decision")
        if decision is not None and not isinstance(decision, str):
            raise SchemaViolation(
                "approval_resolution at intent requires decision to be a string or None"
            )
    elif op == "approval_resolution" and phase == "dispatched":
        if not isinstance(record.get("job_id"), str):
            raise SchemaViolation(
                "approval_resolution at dispatched requires job_id (string)"
            )
        if not isinstance(record.get("request_id"), str):
            raise SchemaViolation(
                "approval_resolution at dispatched requires request_id (string)"
            )
        decision = record.get("decision")
        if decision is not None and not isinstance(decision, str):
            raise SchemaViolation(
                "approval_resolution at dispatched requires decision to be a string or None"
            )
        if not isinstance(record.get("runtime_id"), str):
            raise SchemaViolation(
                "approval_resolution at dispatched requires runtime_id (string)"
            )
        if not isinstance(record.get("codex_thread_id"), str):
            raise SchemaViolation(
                "approval_resolution at dispatched requires codex_thread_id (string)"
            )
    elif op == "promotion" and phase in ("intent", "dispatched"):
        if not isinstance(record.get("job_id"), str):
            raise SchemaViolation(f"promotion at {phase} requires job_id (string)")
    # Compatibility decision: runtime_id on turn_dispatch is NOT required.
    # Missing runtime_id suppresses audit event emission (dialogue.py:592,689)
    # but does not crash recovery. Requiring it would reject records from
    # older writers that may not persist runtime_id on all turn_dispatch
    # entries. This is a data-quality gap, not a correctness failure.
    entry = OperationJournalEntry(
        idempotency_key=record["idempotency_key"],
        operation=record["operation"],
        phase=record["phase"],
        collaboration_id=record["collaboration_id"],
        created_at=record["created_at"],
        repo_root=record["repo_root"],
        codex_thread_id=record.get("codex_thread_id"),
        turn_sequence=record.get("turn_sequence"),
        runtime_id=record.get("runtime_id"),
        context_size=record.get("context_size"),
        job_id=record.get("job_id"),
        request_id=record.get("request_id"),
        decision=record.get("decision"),
        completion_origin=record.get("completion_origin"),
    )
    return (entry.idempotency_key, entry)


class OperationJournal:
    """Session-bounded journal for stale advisory context markers."""

    def __init__(
        self,
        plugin_data_path: Path | None = None,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._plugin_data_path = plugin_data_path or default_plugin_data_path()
        self._clock = clock or (lambda: datetime.now(UTC))
        self._journal_dir = self._plugin_data_path / "journal"
        self._markers_path = self._journal_dir / "stale_advisory_context.json"
        self._audit_dir = self._plugin_data_path / "audit"
        self._audit_path = self._audit_dir / "events.jsonl"
        self._journal_dir.mkdir(parents=True, exist_ok=True)
        self._audit_dir.mkdir(parents=True, exist_ok=True)
        self._analytics_dir = self._plugin_data_path / "analytics"
        self._outcomes_path = self._analytics_dir / "outcomes.jsonl"
        self._analytics_dir.mkdir(parents=True, exist_ok=True)
        self._audit_seen_initialized = False
        self._outcomes_seen_initialized = False
        self._audit_seen: set[_AuditDedupKey] = set()
        self._dialogue_outcomes_seen: set[_DialogueOutcomeDedupKey] = set()
        self._delegation_outcomes_seen: set[_DelegationOutcomeDedupKey] = set()

    @property
    def plugin_data_path(self) -> Path:
        return self._plugin_data_path

    def load_stale_marker(self, repo_root: Path) -> StaleAdvisoryContextMarker | None:
        """Return the persisted stale marker for `repo_root`, if present.

        Stale-marker state is ephemeral session-scoped data. Any per-record
        corruption (wrong type, old schema, missing fields, unknown fields,
        non-string field values) is treated as absent and dropped — the
        next promotion re-emits any marker that is genuinely needed.
        """

        markers = self._read_markers()
        key = _normalize_repo_root_key(repo_root)
        record = markers.get(key)
        if record is None:
            return None
        if not isinstance(record, dict):
            del markers[key]
            self._write_markers(markers)
            return None
        # Old-schema markers have "promoted_head" instead of
        # "promoted_artifact_hash" and lack "job_id".
        if "promoted_artifact_hash" not in record or "job_id" not in record:
            del markers[key]
            self._write_markers(markers)
            return None
        # StaleAdvisoryContextMarker is a plain dataclass; the constructor
        # catches missing/extra fields via TypeError but does not enforce
        # that field values are strings. A record like
        # {"job_id": {}, "promoted_artifact_hash": [], "recorded_at": null}
        # would otherwise pass through as a live marker and leak corrupt
        # state into the advisory stale-context prompt.
        if not all(
            isinstance(record.get(field), str)
            for field in _STALE_MARKER_FIELDS
        ):
            del markers[key]
            self._write_markers(markers)
            return None
        try:
            return StaleAdvisoryContextMarker(**record)
        except TypeError:
            # Record has unexpected fields, missing required fields, or
            # incompatible value types. Drop and return absent.
            del markers[key]
            self._write_markers(markers)
            return None

    def write_stale_marker(self, marker: StaleAdvisoryContextMarker) -> None:
        """Persist or replace a stale marker for its repo root."""

        markers = self._read_markers()
        normalized_repo_root = _normalize_repo_root_key(marker.repo_root)
        normalized_marker = StaleAdvisoryContextMarker(
            repo_root=normalized_repo_root,
            promoted_artifact_hash=marker.promoted_artifact_hash,
            job_id=marker.job_id,
            recorded_at=marker.recorded_at,
        )
        markers[normalized_repo_root] = asdict(normalized_marker)
        self._write_markers(markers)

    def clear_stale_marker(self, repo_root: Path) -> None:
        """Clear the stale marker for `repo_root` without deleting journal files."""

        markers = self._read_markers()
        markers.pop(_normalize_repo_root_key(repo_root), None)
        self._write_markers(markers)

    def append_audit_event(self, event: AuditEvent) -> None:
        """Append an audit event as JSONL."""

        with self._audit_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(asdict(event), sort_keys=True) + "\n")

    def append_dialogue_audit_event_once(self, event: AuditEvent) -> None:
        """Append a dialogue audit event unless the logical record already exists."""

        self._ensure_audit_seen_loaded()
        key: _AuditDedupKey = (event.action, event.collaboration_id, event.turn_id)
        if key in self._audit_seen:
            return
        self.append_audit_event(event)
        self._audit_seen.add(key)

    def append_outcome(self, record: OutcomeRecord) -> None:
        """Append an analytics outcome record as JSONL."""

        with self._outcomes_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")

    def append_dialogue_outcome_once(self, record: OutcomeRecord) -> None:
        """Append a dialogue outcome unless the logical record already exists."""

        self._ensure_outcomes_seen_loaded()
        key: _DialogueOutcomeDedupKey = (
            record.outcome_type,
            record.collaboration_id,
            record.turn_id,
        )
        if key in self._dialogue_outcomes_seen:
            return
        self.append_outcome(record)
        self._dialogue_outcomes_seen.add(key)

    def append_delegation_outcome(self, record: DelegationOutcomeRecord) -> None:
        """Append a delegation terminal outcome record as JSONL."""

        with self._outcomes_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")

    def append_delegation_outcome_once(self, record: DelegationOutcomeRecord) -> None:
        """Append a delegation outcome unless one exists for this job."""

        self._ensure_outcomes_seen_loaded()
        key: _DelegationOutcomeDedupKey = (record.outcome_type, record.job_id)
        if key in self._delegation_outcomes_seen:
            return
        self.append_delegation_outcome(record)
        self._delegation_outcomes_seen.add(key)

    def write_phase(self, entry: OperationJournalEntry, *, session_id: str) -> None:
        """Append a phased journal record with fsync."""
        path = self._operations_path(session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(entry), sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def list_unresolved(self, *, session_id: str) -> list[OperationJournalEntry]:
        """Return entries whose terminal phase is not 'completed'.

        Replays the full log, grouping by idempotency_key, and returns only
        the terminal-phase record for keys that are not yet completed.
        """
        terminal = self._terminal_phases(session_id)
        return [entry for entry in terminal.values() if entry.phase != "completed"]

    def check_idempotency(
        self, key: str, *, session_id: str
    ) -> OperationJournalEntry | None:
        """Return the terminal-phase record for this key, or None."""
        terminal = self._terminal_phases(session_id)
        return terminal.get(key)

    def compact(self, *, session_id: str) -> None:
        """Atomic rewrite: keep only unresolved keys, each as its terminal record.

        Completed keys are removed entirely. Stale intent/dispatched rows for
        unresolved keys are collapsed to a single terminal-phase record.
        Uses temp-file-rename with fsync for crash safety.
        """
        path = self._operations_path(session_id)
        if not path.exists():
            return
        terminal = self._terminal_phases(session_id)
        remaining = [entry for entry in terminal.values() if entry.phase != "completed"]
        tmp = path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            for entry in remaining:
                handle.write(json.dumps(asdict(entry), sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        tmp.rename(path)

    def _terminal_phases(self, session_id: str) -> dict[str, OperationJournalEntry]:
        """Replay the log and return the last record per idempotency key."""
        path = self._operations_path(session_id)
        results, _ = replay_jsonl(path, _journal_callback)
        return dict(results)

    def check_health(self, *, session_id: str) -> ReplayDiagnostics:
        """Replay and return diagnostics. Test and diagnostic support only."""
        path = self._operations_path(session_id)
        _, diagnostics = replay_jsonl(path, _journal_callback)
        return diagnostics

    def _operations_path(self, session_id: str) -> Path:
        return self._journal_dir / "operations" / f"{session_id}.jsonl"

    def _populate_seen_from_file(
        self,
        path: Path,
        on_record: Callable[[dict[str, Any]], None],
    ) -> None:
        if not path.exists():
            return
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    record = json.loads(stripped)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict):
                    on_record(record)

    def _ensure_audit_seen_loaded(self) -> None:
        if self._audit_seen_initialized:
            return

        new_audit_seen: set[_AuditDedupKey] = set()
        try:
            self._populate_seen_from_file(
                self._audit_path,
                lambda record: _populate_from_audit_record(record, new_audit_seen),
            )
        except UnicodeDecodeError as exc:
            self._quarantine_corrupt_jsonl(self._audit_path, reason=exc)
            new_audit_seen = set()
        self._audit_seen = new_audit_seen
        self._audit_seen_initialized = True

    def _ensure_outcomes_seen_loaded(self) -> None:
        if self._outcomes_seen_initialized:
            return

        new_dialogue_outcomes_seen: set[_DialogueOutcomeDedupKey] = set()
        new_delegation_outcomes_seen: set[_DelegationOutcomeDedupKey] = set()
        try:
            self._populate_seen_from_file(
                self._outcomes_path,
                lambda record: _populate_from_outcome_record(
                    record,
                    new_dialogue_outcomes_seen,
                    new_delegation_outcomes_seen,
                ),
            )
        except UnicodeDecodeError as exc:
            self._quarantine_corrupt_jsonl(self._outcomes_path, reason=exc)
            new_dialogue_outcomes_seen = set()
            new_delegation_outcomes_seen = set()
        self._dialogue_outcomes_seen = new_dialogue_outcomes_seen
        self._delegation_outcomes_seen = new_delegation_outcomes_seen
        self._outcomes_seen_initialized = True

    def prune_audit_logs(self) -> PruneSummary:
        now = self._now()
        cutoff = now - timedelta(days=_AUDIT_TTL_DAYS)

        self._audit_seen_initialized = False
        self._outcomes_seen_initialized = False

        new_audit_seen: set[_AuditDedupKey] = set()
        new_dialogue_outcomes_seen: set[_DialogueOutcomeDedupKey] = set()
        new_delegation_outcomes_seen: set[_DelegationOutcomeDedupKey] = set()
        audit_quarantined_to: Path | None = None
        outcomes_quarantined_to: Path | None = None

        try:
            audit_stats = self._prune_jsonl_pass(
                path=self._audit_path,
                cutoff=cutoff,
                populate=lambda record: _populate_from_audit_record(
                    record, new_audit_seen
                ),
            )
        except UnicodeDecodeError as exc:
            audit_quarantined_to = self._quarantine_corrupt_jsonl(
                self._audit_path,
                reason=exc,
            )
            audit_stats = _PruneFileStats(0, 0, 0)
            new_audit_seen = set()
        self._audit_seen = new_audit_seen
        self._audit_seen_initialized = True

        try:
            outcomes_stats = self._prune_jsonl_pass(
                path=self._outcomes_path,
                cutoff=cutoff,
                populate=lambda record: _populate_from_outcome_record(
                    record,
                    new_dialogue_outcomes_seen,
                    new_delegation_outcomes_seen,
                ),
            )
        except UnicodeDecodeError as exc:
            outcomes_quarantined_to = self._quarantine_corrupt_jsonl(
                self._outcomes_path,
                reason=exc,
            )
            outcomes_stats = _PruneFileStats(0, 0, 0)
            new_dialogue_outcomes_seen = set()
            new_delegation_outcomes_seen = set()
        self._dialogue_outcomes_seen = new_dialogue_outcomes_seen
        self._delegation_outcomes_seen = new_delegation_outcomes_seen
        self._outcomes_seen_initialized = True

        return PruneSummary(
            audit_retained=audit_stats.retained,
            audit_dropped=audit_stats.dropped,
            audit_retained_malformed=audit_stats.retained_malformed,
            outcomes_retained=outcomes_stats.retained,
            outcomes_dropped=outcomes_stats.dropped,
            outcomes_retained_malformed=outcomes_stats.retained_malformed,
            audit_quarantined_to=audit_quarantined_to,
            outcomes_quarantined_to=outcomes_quarantined_to,
        )

    def _quarantine_corrupt_jsonl(
        self,
        path: Path,
        *,
        reason: Exception,
    ) -> Path:
        """Rename a UTF-8-corrupt journal file to a forensic sibling."""

        timestamp = self._now().strftime("%Y%m%dT%H%M%SZ")
        quarantine_path = path.with_name(
            f"{path.stem}.corrupt-{timestamp}{path.suffix}"
        )
        counter = 0
        while quarantine_path.exists():
            counter += 1
            quarantine_path = path.with_name(
                f"{path.stem}.corrupt-{timestamp}.{counter}{path.suffix}"
            )

        path.rename(quarantine_path)
        logger.warning(
            "quarantined corrupt journal file: %s -> %s (reason: %r)",
            path,
            quarantine_path,
            reason,
        )
        return quarantine_path

    def _prune_jsonl_pass(
        self,
        *,
        path: Path,
        cutoff: datetime,
        populate: Callable[[dict[str, Any]], None],
    ) -> _PruneFileStats:
        if not path.exists():
            return _PruneFileStats(0, 0, 0)

        retained_lines: list[str] = []
        retained_count = 0
        dropped_count = 0
        retained_malformed_count = 0

        with path.open(encoding="utf-8") as handle:
            for raw_line in handle:
                stripped = raw_line.strip()
                if not stripped:
                    continue

                line_to_keep = raw_line if raw_line.endswith("\n") else raw_line + "\n"

                try:
                    record = json.loads(stripped)
                except json.JSONDecodeError:
                    retained_count += 1
                    retained_malformed_count += 1
                    retained_lines.append(line_to_keep)
                    continue

                if not isinstance(record, dict):
                    retained_count += 1
                    retained_malformed_count += 1
                    retained_lines.append(line_to_keep)
                    continue

                timestamp = _parse_aware_iso8601(record.get("timestamp"))
                if timestamp is None:
                    retained_count += 1
                    retained_malformed_count += 1
                    retained_lines.append(line_to_keep)
                    populate(record)
                    continue

                if timestamp < cutoff:
                    dropped_count += 1
                    continue

                retained_count += 1
                retained_lines.append(line_to_keep)
                populate(record)

        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.writelines(retained_lines)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)

        return _PruneFileStats(retained_count, dropped_count, retained_malformed_count)

    def _now(self) -> datetime:
        """Current time per the injected clock."""

        return _coerce_aware_utc(self._clock(), source="Journal clock")

    def timestamp(self) -> str:
        """Return the current UTC timestamp as ISO 8601."""

        return self._now().replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _read_markers(self) -> dict[str, dict[str, str]]:
        if not self._markers_path.exists():
            return {}
        try:
            with self._markers_path.open(encoding="utf-8") as handle:
                loaded = json.load(handle)
        except json.JSONDecodeError:
            self._clear_corrupt_markers_file()
            return {}
        if not isinstance(loaded, dict):
            # Valid JSON but the wrong top-level shape (e.g. list, scalar,
            # null). Stale-marker state is ephemeral; treat as absent and
            # clear so the next write starts fresh. Any needed marker
            # re-emits on the next promotion.
            self._clear_corrupt_markers_file()
            return {}
        return loaded

    def _clear_corrupt_markers_file(self) -> None:
        """Remove the markers file if present, swallowing missing-file errors."""
        try:
            self._markers_path.unlink()
        except OSError:
            pass

    def _write_markers(self, markers: dict[str, dict[str, str]]) -> None:
        # Spec classifies the marker file as crash-recovery state. Write
        # to a temp file, fsync, then atomically replace — same pattern
        # `compact()` uses for the operation journal. Direct truncate-then-
        # write leaves the file empty or partial on crash, which both
        # silently loses the marker AND breaks subsequent reads.
        tmp_path = self._markers_path.with_name(self._markers_path.name + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(markers, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, self._markers_path)


def _normalize_repo_root_key(repo_root: Path | str) -> str:
    """Canonicalize repo-root keys so read/write/clear use the same lookup."""

    return Path(repo_root).expanduser().resolve().as_posix()
