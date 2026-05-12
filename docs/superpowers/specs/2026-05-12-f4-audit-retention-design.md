---
title: F4 audit retention design
status: design
date: 2026-05-12
authority: design
slice: Bucket 2b — F4 (audit retention + dedup-scan replacement)
defers: F12 reserved crash/restart audit events (sibling slice)
---

# F4 Audit Retention Design

## 1. Context

The 2026-05-12 codex-collaboration plugin design review surfaced **F4 — Audit log retention specified but not implemented; O(n) dedup compounds with growth** as a P1 with three-reviewer convergence (data, reliability-operational, behavioral). The spec contractually states a 30-day TTL with pruning "on plugin startup and periodically during session" for `audit/events.jsonl`. No pruning code exists. Compounding the storage gap, `OperationJournal.append_dialogue_audit_event_once`, `append_dialogue_outcome_once`, and `append_delegation_outcome_once` linear-scan the full file before each append to deduplicate, producing per-write cost that grows proportionally with total history.

This document specifies the design for closing F4 by implementing startup pruning for both `events.jsonl` and `analytics/outcomes.jsonl`, and replacing the linear dedup scan with an in-memory seen-set populated during the same startup pass.

**Slice boundary:** This design is F4 only. F12's reserved `crash` and `restart` audit events are deferred to a sibling slice (Bucket 2b-2) because emission semantics depend on a separate open design question — controller-scoped versus process-startup-aggregate detection — that interacts with the lazy-factory bootstrap path. Bundling that decision into F4 would expand the review surface without strengthening either fix.

## 2. Contract

After this slice lands, the following hold:

- `audit/events.jsonl` and `analytics/outcomes.jsonl` are pruned at plugin startup. Records with parseable timezone-aware ISO 8601 timestamps older than 30 days from the current time are dropped.
- Outcomes (`analytics/outcomes.jsonl`) are treated in this slice as **operational diagnostics with a 30-day operational horizon**, not as long-term analytics history. This is an explicit data-class decision: if a future feature consumes outcomes for long-term analytics, a separate retention class must be introduced **before** the consuming feature ships. Records dropped by this slice's prune are not recoverable.
- Pruning is a pure filter: retained record bytes are preserved, with a single `\n` appended to the final retained line if absent (to keep the file JSONL-append-safe for the next `append_*` call). Records are never re-serialized through `json.dumps`. File format is LF-only by construction across all Python-supported platforms: every `append_*` writer and the prune temp-file write open with `newline="\n"`, which suppresses Python's default platform-dependent text-mode newline translation (which would otherwise emit `\r\n` on Windows). A hypothetical CRLF input file is normalized to LF by the text-mode read pass; "record bytes preserved" applies to record content, not non-LF line-ending bytes.
- Records with missing, non-string, unparseable, or timezone-naive `timestamp` fields are retained (retain-on-uncertainty principle — ambiguous records are not silently erased). These records are **TTL-exempt by design**: the 30-day TTL applies only to records with parseable, timezone-aware timestamps, so a sufficiently corrupt audit or outcome line can survive past the 30-day window indefinitely. `PruneSummary.audit_retained_malformed` and `PruneSummary.outcomes_retained_malformed` count these records each pass; they share the observability conditional described in the bootstrap bullet below.
- Records that fail to parse as JSON, or parse as non-dict shapes, are retained as raw lines.
- Blank lines are removed during pruning (not records; not subject to retain-on-uncertainty).
- The three `append_*_once` methods consult an in-memory dedup set keyed on natural fields. Set membership replaces the previous linear file scan. Sets are atomically rebuilt during prune and atomically loaded on first direct-construction use.
- A clock seam (`OperationJournal(..., clock=Callable[[], datetime])`) governs every "now" the journal uses. Naive clock outputs fail fast with `ValueError`. Production code does not pass concrete `now=` values; tests inject fake clocks.
- Atomic file replacement guarantees: target file untouched on pre-replace failure; POSIX-atomic swap on `os.replace` success. Does *not* directory-fsync — post-rename durability across power-fail is not asserted, matching the existing `compact()` and `_write_markers` pattern.
- **Atomicity is per file, not pair-wise.** A successful prune of `events.jsonl` followed by a failed prune of `outcomes.jsonl` leaves the canonical files in a mixed-prune state. Both files are independent retention surfaces; the next startup re-runs the full prune. **Seen-set loading is per source file**, not journal-wide: `_ensure_audit_seen_loaded()` depends only on `events.jsonl` readability, and `_ensure_outcomes_seen_loaded()` depends only on `outcomes.jsonl` readability. After a partial-failure prune, each `append_*_once` reloads only its own file's seen-set from disk. Audit appends do not share fate with outcomes appends, and vice versa.
- **File-level encoding is UTF-8 by construction.** An invalid UTF-8 byte sequence in `events.jsonl` or `outcomes.jsonl` is treated as **file-level corruption with automatic quarantine**. Both `prune_audit_logs` (startup) and `_ensure_*_seen_loaded` (runtime append-once paths) catch `UnicodeDecodeError` per file and invoke the shared `_quarantine_corrupt_jsonl` helper (§5.2c), which renames the affected file to a sibling `<stem>.corrupt-<utc-ts><suffix>` (with deterministic `.1`, `.2`, ... numeric suffix on existing-target collision), logs at `WARNING` with both paths plus the reason exception, and returns the quarantine path. The relevant in-memory seen-set(s) become empty and that file's initialized flag is set to `True`; the next `append_*` call writes a fresh JSONL record into a newly-created file. This is *not* retain-on-uncertainty (which applies at JSONL-record granularity, not byte granularity), but it shares the principle that corrupt content is preserved on disk under a forensic name rather than silently erased. JSONL-line-level `json.JSONDecodeError` is *not* in the quarantine class because malformed records are line-local retained data, not byte-level corruption.
- **Quarantine duplicate-record trade-off.** After a file is quarantined, any records that existed *only* in the quarantined file are no longer represented in the in-memory seen-set. A subsequent `append_*_once` call carrying a logical record that matched a quarantined-file record will succeed (not deduped). This is an explicit accepted trade-off: corrupt diagnostic data does not block live workflow finalization, and the quarantined file remains available for forensic inspection.
- **Single-writer assumption.** Exactly one MCP process owns a given `plugin_data_path` at a time. Concurrent prune from two processes against the same data directory is undefined and unsupported — the fixed-suffix temp file `<path>.tmp` would collide. This matches the existing `compact()` and `_write_markers` patterns in `OperationJournal`.
- The plugin bootstrap invokes pruning. Prune failure (`OSError` only — `UnicodeDecodeError` is now handled inside `prune_audit_logs` via quarantine) invokes `logger.warning(..., exc_info=True)` and does not block startup. **Warning-level output reaches stderr via Python's `logging.lastResort` handler (the unconfigured-logger fallback), so the failure signal is observable to whoever sees the MCP server's stderr unless the host suppresses it.** The success-summary call is at `INFO` (discarded by Python's default logging configuration) **when both `retained_malformed` counts are zero AND no file was quarantined**, and is **escalated to `WARNING` when any of those is nonzero / non-None** — so the silent-accumulation case AND the quarantine case both have default operator visibility before F18 lands. Quarantine itself fires a `WARNING` from inside `_quarantine_corrupt_jsonl` at the moment of rename; the bootstrap summary `WARNING` ties the per-file event to the run-level summary for log correlation. Routine success metrics still require F18 (or `caplog` in tests). Append correctness is preserved through `_ensure_audit_seen_loaded()` / `_ensure_outcomes_seen_loaded()` regardless of logging state.

## 3. Scope

### In

- Pruning for `audit/events.jsonl` and `analytics/outcomes.jsonl` at startup.
- Replacement of linear `_jsonl_contains` dedup with in-memory seen-sets (per-source-file initialization — see §5.7).
- Clock seam added to `OperationJournal` constructor.
- Spec amendments to `docs/specs/recovery-and-journal.md`: §Two-Log Architecture table retention row, new §Operational Outcomes subsection, §Audit Log → Retention subsection rewrite, and §Retention Defaults table.
- New tests in `tests/test_journal.py` (journal-internal: pruning, dedup, atomic-rewrite, per-file lifecycle) and `tests/test_bootstrap.py` (§8.9 bootstrap-integration invariants).
- Migration of any existing tests that exercised `_jsonl_contains` semantics.

### Out (deferred)

- **F12 reserved `crash`/`restart` audit events** — sibling slice. That slice's own design must first resolve controller-scoped versus process-startup-aggregate detection given the production lazy-factory bootstrap reality.
- **Env-configurable TTL** (`CODEX_COLLAB_AUDIT_TTL_DAYS`) — belongs to a future F19 config-inventory slice if/when introduced. The TTL stays a module constant in this slice.
- **Periodic-during-session pruning** — future scope. Documented in the spec as such; not implemented in v1.
- **Audit-log fsync, hash chain, HMAC** (F12's other sub-recommendations) — not in this slice. The audit log remains "best-effort append" per the existing spec.

## 4. Module Surface

All changes are in `server/journal.py` unless noted.

### Constants and types

```python
import logging
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)  # used by _quarantine_corrupt_jsonl (§5.2c)

# Audit-log retention. Spec contract: recovery-and-journal.md §Audit Log Retention.
_AUDIT_TTL_DAYS = 30

# Dedup key shapes. Each tuple matches the legacy _jsonl_contains predicate
# verbatim — current observable behavior is preserved.
_AuditDedupKey = tuple[str, str, str | None]          # (action, collaboration_id, turn_id)
_DialogueOutcomeDedupKey = tuple[str, str, str]       # (outcome_type, collaboration_id, turn_id)
_DelegationOutcomeDedupKey = tuple[str, str]          # (outcome_type, job_id)


@dataclass(frozen=True)
class PruneSummary:
    """Flat diagnostics for a single prune pass. Returned to bootstrap for logging."""
    audit_retained: int
    audit_dropped: int
    audit_retained_malformed: int
    outcomes_retained: int
    outcomes_dropped: int
    outcomes_retained_malformed: int
    audit_quarantined_to: Path | None = None
    outcomes_quarantined_to: Path | None = None
```

`audit_quarantined_to` / `outcomes_quarantined_to` are `None` on every normal run and contain the destination `Path` of the quarantined file when invalid-UTF-8 corruption forced a quarantine on that file's pass (§5.2c).

### Helper

```python
def _coerce_aware_utc(value: datetime, *, source: str) -> datetime:
    """Validate that a datetime is timezone-aware and normalize to UTC.

    The journal's persistence relies on unambiguous UTC; naive datetimes are
    rejected at injection time so corrupt records are not silently retained
    under the retain-on-uncertainty rule.
    """
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError(
            f"{source} requires a timezone-aware datetime; got naive {value!r}"
        )
    return value.astimezone(UTC)
```

### Constructor

```python
def __init__(
    self,
    plugin_data_path: Path | None = None,
    *,
    clock: Callable[[], datetime] | None = None,
) -> None:
    # ... existing path setup unchanged ...
    self._clock = clock or (lambda: datetime.now(UTC))
    # Two flags, one per source file. Audit appends depend only on
    # _audit_seen_initialized; outcomes appends (dialogue + delegation,
    # both stored in outcomes.jsonl) depend only on _outcomes_seen_initialized.
    # This decoupling is load-bearing: an unreadable outcomes.jsonl must not
    # block audit appends.
    self._audit_seen_initialized = False
    self._outcomes_seen_initialized = False
    self._audit_seen: set[_AuditDedupKey] = set()
    self._dialogue_outcomes_seen: set[_DialogueOutcomeDedupKey] = set()
    self._delegation_outcomes_seen: set[_DelegationOutcomeDedupKey] = set()
```

### Public methods

```python
def _now(self) -> datetime:
    """Current time per the injected clock. Fails fast on naive clocks."""
    return _coerce_aware_utc(self._clock(), source="Journal clock")

def timestamp(self) -> str:
    """Return the current UTC timestamp as ISO 8601 (Z form)."""
    return (
        self._now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )

def prune_audit_logs(self, now: datetime | None = None) -> PruneSummary:
    """Single-pass prune for events.jsonl and outcomes.jsonl.

    For each file: drop records older than _AUDIT_TTL_DAYS; rewrite the
    file atomically with retained records as their original raw lines;
    populate this journal's dedup seen-sets from retained records.

    `now` is normally None — production callers consume the injected clock.
    Tests may pass an explicit timezone-aware `now`; naive values raise
    `ValueError`. Idempotent: re-running rebuilds the sets from scratch,
    so newly-expired keys disappear.

    Returns PruneSummary for diagnostic logging.
    """

def append_dialogue_audit_event_once(self, event: AuditEvent) -> None:
    """Append unless the logical record already exists.

    Invariants:
      - Calls _ensure_audit_seen_loaded() before the dedup check (per-file
        load: only events.jsonl is read). Direct-construction paths get
        correct dedup automatically without coupling to outcomes.jsonl.
      - The seen-set is updated only after append_audit_event() succeeds.
        If append raises, the key is not added so a retry can still write.
    """
```

Same shape for `append_dialogue_outcome_once` and `append_delegation_outcome_once`, except both call `_ensure_outcomes_seen_loaded()` (per-file load: only outcomes.jsonl is read).

### Private methods

- `_ensure_audit_seen_loaded()` — populate `_audit_seen` from `events.jsonl` without rewriting. Atomic rebuild semantics (local set, assigned only on success or quarantine). Catches `UnicodeDecodeError` from the read, quarantines the corrupt file via `_quarantine_corrupt_jsonl`, and assigns the relevant set to empty before flipping the flag to `True` (§5.7). Does not flip `_audit_seen_initialized` if population raises a non-UTF-8 exception (e.g., `OSError`).
- `_ensure_outcomes_seen_loaded()` — populate both `_dialogue_outcomes_seen` and `_delegation_outcomes_seen` from `outcomes.jsonl` in a single read pass (one disk read, two sets). Same UTF-8 quarantine handling as `_ensure_audit_seen_loaded`. Does not flip `_outcomes_seen_initialized` if population raises a non-UTF-8 exception.
- `_prune_jsonl_pass(*, path, cutoff, populate)` — single linear scan; produces retained raw lines and per-file stats. Pins `newline="\n"` on the temp-file write (§5.2). Raises `UnicodeDecodeError` on byte-level corruption — caller (`prune_audit_logs`) catches and quarantines per file.
- `_populate_seen_from_file(path, on_record)` — read-only population helper used by the two `_ensure_*_seen_loaded` methods. Raises `UnicodeDecodeError` on byte-level corruption — caller catches and quarantines.
- `_quarantine_corrupt_jsonl(path, *, reason)` — rename a UTF-8-corrupt file to a forensic sibling `<stem>.corrupt-<utc-ts><suffix>`; resolve target collisions with deterministic `.1`, `.2`, ... numeric suffix; log at `WARNING` with original path, quarantine path, and reason exception; return the quarantine path. `OSError` from the rename propagates (IO-class failure, not UTF-8 class). Called from both `prune_audit_logs` and the two `_ensure_*_seen_loaded` methods (§5.2c).
- `_parse_aware_iso8601(value: Any) -> datetime | None` — strict timestamp parser.
- `_populate_from_audit_record(record, audit_seen)` — module-level helper; adds the dedup key to `audit_seen` if the record has all comparable-key fields.
- `_populate_from_outcome_record(record, dialogue_seen, delegation_seen)` — module-level helper; dispatches on `outcome_type` to populate the right outcomes set.

### Removed

- `_jsonl_contains` — three append-once callers migrated; no remaining production callers. Removal verified by `rg "_jsonl_contains" server/ scripts/` returning zero hits before deletion.

## 5. Algorithms

### 5.1 Clock seam

The journal's only source of "now" is `self._clock()`. Both `timestamp()` and `prune_audit_logs(now=None)` flow through `_now()`, which calls `_coerce_aware_utc` to fail-fast on naive clocks. Explicit `now=` arguments to `prune_audit_logs` flow through the same helper, ensuring identical validation semantics on both paths.

### 5.2 Pruning pass

For each file, `_prune_jsonl_pass` performs one linear scan:

```python
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
                continue  # blank lines are not records; drop on rewrite

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

            ts = _parse_aware_iso8601(record.get("timestamp"))
            if ts is None:
                # Missing / non-string / unparseable / naive — retain.
                retained_count += 1
                retained_malformed_count += 1
                retained_lines.append(line_to_keep)
                populate(record)  # populate seen-set if record has the comparable shape
                continue

            if ts < cutoff:
                dropped_count += 1
                continue

            retained_count += 1
            retained_lines.append(line_to_keep)
            populate(record)

    # Atomic replacement: temp file + fsync + os.replace.
    # newline="\n" pins LF on disk on all platforms (default text mode would
    # translate \n → \r\n on Windows). The read side (path.open above) uses
    # default text mode for universal-newlines CRLF→LF normalization.
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.writelines(retained_lines)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)

    return _PruneFileStats(retained_count, dropped_count, retained_malformed_count)
```

`_prune_jsonl_pass` itself does not catch `UnicodeDecodeError`. Byte-level corruption raises out of the linear-scan loop; the caller (`prune_audit_logs` below) catches it per file and invokes the quarantine helper (§5.2c).

`prune_audit_logs` orchestrates:

```python
def prune_audit_logs(self, now: datetime | None = None) -> PruneSummary:
    now = (
        self._now()
        if now is None
        else _coerce_aware_utc(now, source="prune_audit_logs(now=...)")
    )
    cutoff = now - timedelta(days=_AUDIT_TTL_DAYS)

    # Invalidate BOTH per-file flags before any disk mutation. Each is
    # restored independently after its file's seen-set is atomically
    # reassigned. A partial failure on outcomes leaves _audit_seen_initialized
    # restored to True (audit pass succeeded) but _outcomes_seen_initialized
    # still False, so the next outcomes append reloads from disk while audit
    # appends remain served from in-memory state.
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
            populate=lambda r: _populate_from_audit_record(r, new_audit_seen),
        )
    except UnicodeDecodeError as exc:
        # File-level corruption: quarantine and continue with an empty
        # seen-set. The next append_*_once for audit writes a fresh file.
        audit_quarantined_to = self._quarantine_corrupt_jsonl(
            self._audit_path, reason=exc,
        )
        audit_stats = _PruneFileStats(retained=0, dropped=0, retained_malformed=0)
        # new_audit_seen remains empty; subsequent appends are deduped against
        # an empty set, allowing records present only in the quarantined file
        # to re-append as duplicates (§2 Contract quarantine trade-off).

    # Atomic per-file commit: audit seen-set assigned and flag restored
    # immediately after its pass completes (or after quarantine). Independent
    # of outcomes.
    self._audit_seen = new_audit_seen
    self._audit_seen_initialized = True

    try:
        outcomes_stats = self._prune_jsonl_pass(
            path=self._outcomes_path,
            cutoff=cutoff,
            populate=lambda r: _populate_from_outcome_record(
                r, new_dialogue_outcomes_seen, new_delegation_outcomes_seen,
            ),
        )
    except UnicodeDecodeError as exc:
        outcomes_quarantined_to = self._quarantine_corrupt_jsonl(
            self._outcomes_path, reason=exc,
        )
        outcomes_stats = _PruneFileStats(retained=0, dropped=0, retained_malformed=0)
        # Both outcomes seen-sets remain empty for the same reason as audit.

    # Atomic per-file commit: both outcomes seen-sets assigned and flag
    # restored after the single outcomes pass completes (or after quarantine).
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
```

**Failure narrative — outcomes pass fails after audit pass succeeds.** If `_prune_jsonl_pass` for `outcomes.jsonl` raises after `events.jsonl` has been successfully replaced and the audit seen-set has been committed, the journal's in-memory state shows: `_audit_seen_initialized == True` (audit pass committed); `_outcomes_seen_initialized == False` (cleared at entry, never restored because the outcomes commit lines are unreached). On disk, `events.jsonl` reflects the prune; `outcomes.jsonl` is untouched. The next `append_dialogue_audit_event_once` is served directly from the in-memory audit seen-set — no disk reload needed because the audit pass succeeded. The next `append_dialogue_outcome_once` or `append_delegation_outcome_once` consults `_ensure_outcomes_seen_loaded()`, which (because `_outcomes_seen_initialized == False`) reads `outcomes.jsonl` and populates both outcomes seen-sets from the untouched file. **Audit appends do not share fate with outcomes IO.**

**Failure narrative — audit pass fails first.** If `_prune_jsonl_pass` for `events.jsonl` raises, both flags remain `False` (cleared at entry, never restored), the outcomes pass is unreached, and both files on disk are unchanged. The next `append_dialogue_audit_event_once` reloads `events.jsonl` via `_ensure_audit_seen_loaded()`; outcomes appends reload `outcomes.jsonl` via `_ensure_outcomes_seen_loaded()`. Both files are eligible for prune retry on the next call to `prune_audit_logs()`.

This per-file-not-pair-wise transaction boundary is named in §2 Contract; the **per-file flag-clear-at-entry discipline** is what keeps the boundary correct when prune is re-run on a journal whose seen-sets were previously initialized — without per-file flag invalidation, stale in-memory keys could silently skip valid appends after a partial-failure re-run.

**Invalid UTF-8 is file-level corruption — quarantined automatically.** The `with path.open(encoding="utf-8") as handle:` block uses Python's default `errors="strict"`. An invalid UTF-8 byte sequence raises `UnicodeDecodeError` during the linear scan, exiting `_prune_jsonl_pass` immediately. The orchestrator (`prune_audit_logs` above) catches the exception per file and invokes `_quarantine_corrupt_jsonl` (§5.2c), which renames the corrupt file to a forensic sibling, logs at `WARNING`, and returns the quarantine path. The audit-pass and outcomes-pass try/except blocks are independent: a UTF-8 corruption on one file does not block the other from pruning normally. After quarantine, the corresponding in-memory seen-set is empty (the local `new_*_seen` builders were never populated by the failed scan), the per-file flag is set to `True`, and the next `append_*_once` for that domain writes a fresh JSONL record into a newly-created file (§2 Contract quarantine trade-off: records present only in the quarantined file may re-append as duplicates). Retain-on-uncertainty does not apply at byte granularity — it is a record-level discipline. `json.JSONDecodeError` is **not** in the quarantine class because malformed-JSON records are line-local retained data (per the §5.3 retain-on-uncertainty table).

**Line endings are LF-only by construction (§2 Contract) — across all platforms.** The read path uses default text mode (`newline=None`), which performs universal-newlines translation: CRLF input is normalized to LF in the Python string `raw_line` on read. The write path **explicitly pins `newline="\n"`** on the temp-file `open(...)` so Python's default platform-dependent newline translation does not emit CRLF on Windows. The journal's own `append_*` writers in `server/journal.py` apply the same `newline="\n"` discipline (round-6 F3) so every file the journal produces is LF-only on disk regardless of platform. A CRLF input file is a hypothetical hand-edited scenario — the prune pass normalizes it back to the documented LF JSONL format on read, and the write side never produces CRLF. The format-boundary pin in §8.3 prevents future regressions of either property.

### 5.2a Population helpers

The `populate` callback used by `_prune_jsonl_pass` (and the equivalent reader path in `_ensure_audit_seen_loaded` / `_ensure_outcomes_seen_loaded`) is one of two module-level free functions:

```python
def _populate_from_audit_record(
    record: dict[str, Any],
    audit_seen: set[_AuditDedupKey],
) -> None:
    """Add the dedup key to `audit_seen` if the record has the comparable
    shape. No-op on missing or non-string action/collaboration_id. turn_id
    may be None; matches the legacy `_jsonl_contains` predicate.
    """
    action = record.get("action")
    collab = record.get("collaboration_id")
    if not isinstance(action, str) or not isinstance(collab, str):
        return
    turn_id = record.get("turn_id")
    if turn_id is not None and not isinstance(turn_id, str):
        return
    audit_seen.add((action, collab, turn_id))


def _populate_from_outcome_record(
    record: dict[str, Any],
    dialogue_seen: set[_DialogueOutcomeDedupKey],
    delegation_seen: set[_DelegationOutcomeDedupKey],
) -> None:
    """Dispatch on outcome_type to populate the right outcomes set.

    - outcome_type == "delegation_terminal": key = (outcome_type, job_id).
    - any other string outcome_type (e.g., "consult", "dialogue_turn"):
      key = (outcome_type, collaboration_id, turn_id).

    No-op on non-string outcome_type or any missing/non-string required
    field. Records that don't fit either shape are silently skipped — the
    record is retained as a raw line, but cannot dedup-collide with future
    well-shaped writes through the typed contract.
    """
    outcome_type = record.get("outcome_type")
    if not isinstance(outcome_type, str):
        return
    if outcome_type == "delegation_terminal":
        job_id = record.get("job_id")
        if isinstance(job_id, str):
            delegation_seen.add((outcome_type, job_id))
        return
    collab = record.get("collaboration_id")
    turn_id = record.get("turn_id")
    if isinstance(collab, str) and isinstance(turn_id, str):
        dialogue_seen.add((outcome_type, collab, turn_id))
```

Both helpers are pure (read the record, mutate only the passed-in set) and free of journal state. They are testable in isolation if helpful, but the integration tests in §8.7 and §8.8 cover their behavior through the public surface.

### 5.2c Quarantine helper for UTF-8 corruption

`_quarantine_corrupt_jsonl` is the single point of "this file is unreadable UTF-8; preserve evidence and move out of the way." It is called from two sites — once per file from `prune_audit_logs` (§5.2) on startup and once per file from `_ensure_audit_seen_loaded` / `_ensure_outcomes_seen_loaded` (§5.7) at runtime. Both call sites share identical semantics so the failure-class boundary between startup and runtime is closed (round-6 F1).

```python
def _quarantine_corrupt_jsonl(
    self,
    path: Path,
    *,
    reason: Exception,
) -> Path:
    """Rename a UTF-8-corrupt journal file to a forensic sibling.

    Naming: <stem>.corrupt-<utc-ts><suffix>, e.g.
    events.corrupt-20260512T193715Z.jsonl. If the chosen target already
    exists, append a deterministic numeric suffix (.1, .2, ...) until a
    free name is found. Returns the quarantine path.

    Logs at WARNING with the original path, quarantine path, and the
    reason exception so operators can correlate the rename to the
    triggering decode failure.

    Only UnicodeDecodeError is the upstream trigger for this helper.
    An OSError from the underlying rename propagates as an IO-class
    failure — it is not a UTF-8 corruption case and the caller treats
    it like any other prune-pass OSError.
    """
    ts = self._now().strftime("%Y%m%dT%H%M%SZ")
    quarantine_path = path.with_name(
        f"{path.stem}.corrupt-{ts}{path.suffix}"
    )
    counter = 0
    while quarantine_path.exists():
        counter += 1
        quarantine_path = path.with_name(
            f"{path.stem}.corrupt-{ts}.{counter}{path.suffix}"
        )

    path.rename(quarantine_path)

    logger.warning(
        "quarantined corrupt journal file: %s -> %s (reason: %r)",
        path,
        quarantine_path,
        reason,
    )
    return quarantine_path
```

**Naming rationale.** The `<stem>.corrupt-<utc-ts><suffix>` shape preserves the original file extension so existing log-analysis tooling that filters on `.jsonl` still matches the quarantined file. The `corrupt-` infix is explicit so an `ls` on the data directory makes the meaning obvious without consulting documentation. UTC seconds-precision gives enough uniqueness for the same-startup case; the deterministic numeric suffix handles sub-second repeats and idempotency on accidental re-quarantine.

**No best-effort `OSError` swallowing inside the helper.** If the rename itself raises `OSError` (permission denied, ENOSPC, EBUSY, etc.), the exception propagates to the caller. From the caller's perspective, this is the *same* IO-failure class as any other read/write/replace error in `_prune_jsonl_pass` — it surfaces at the bootstrap `OSError` catch (§6.1) as a `WARNING` and the plugin continues. The runtime `_ensure_*_seen_loaded` callers do not catch quarantine-rename `OSError`; the exception propagates through `append_*_once` and is caught by whatever wraps that call (e.g., `dialogue._finalize_confirmed_turn`'s blanket-Exception envelope). This is acceptable: a quarantine-rename `OSError` represents a filesystem-level inability to recover, distinct from the UTF-8 corruption class that the quarantine policy targets.

**Quarantine is not idempotent against accidental re-call.** A second `_quarantine_corrupt_jsonl(path, ...)` call on a path that no longer exists (because the first call renamed it away) would raise `FileNotFoundError` (an `OSError` subclass) from `path.rename(...)`. This is fine because both call sites (`prune_audit_logs` and `_ensure_*_seen_loaded`) only invoke quarantine after a `UnicodeDecodeError` from reading the same path — which proves the file existed at read time. The helper is single-shot per detection.

### 5.3 Retain-on-uncertainty table

| Line type | Decision | Counted as |
|---|---|---|
| Empty / blank (`stripped == ""`) | Drop on rewrite (not a record) | neither |
| Not valid JSON | **Retain** raw line, do not populate seen-set | retained + retained_malformed |
| Valid JSON but not a dict | **Retain** raw line, do not populate seen-set | retained + retained_malformed |
| Dict, `timestamp` missing / non-string | **Retain** raw line; populate seen-set if record has comparable-key shape | retained + retained_malformed |
| Dict, `timestamp` unparseable as ISO 8601 | **Retain** raw line; populate seen-set if shape matches | retained + retained_malformed |
| Dict, `timestamp` is timezone-naive | **Retain** raw line; populate seen-set if shape matches | retained + retained_malformed |
| Dict, `timestamp` is aware AND `ts < cutoff` | Drop | dropped |
| Dict, `timestamp` is aware AND `ts >= cutoff` (including exact boundary) | **Retain** raw line; populate seen-set | retained |

**Records retained but not populated** in the seen-set are intentionally ignored for dedup because they lack the comparable key shape (e.g., a dict missing `action` or `collaboration_id`). They remain on disk as audit evidence; they cannot collide with future writes through the typed dedup contract.

### 5.4 Strict timestamp parser

```python
def _parse_aware_iso8601(value: Any) -> datetime | None:
    """Return a timezone-aware UTC datetime, or None on any failure mode.

    Accepts only timezone-aware ISO 8601 strings, including the `Z` form
    (Python 3.11+ datetime.fromisoformat handles `Z` natively). Returns
    None for: non-string input, parse failure, timezone-naive results.
    """
    if not isinstance(value, str):
        return None
    try:
        ts = datetime.fromisoformat(value)
    except ValueError:
        return None
    if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
        return None
    return ts.astimezone(UTC)
```

### 5.5 Atomic file replacement — precise guarantee

The rewrite pattern (`tmp.write` → `flush` → `os.fsync` → `os.replace`) delivers:

- **Pre-replace failure path** (exception during write, flush, or fsync): the canonical target file is untouched. The orphaned `.tmp` sibling is not referenced by any subsequent read path.
- **Replace operation**: POSIX-atomic; the target either contains the old bytes or the new bytes, never partial.

This guarantee does **not** include directory-fsync after `os.replace`. Post-rename durability across power-fail is therefore not asserted — the rename may revert on power loss between `os.replace` returning and the directory entry committing to disk. This matches the existing `compact()` and `_write_markers` patterns in this module.

### 5.6 Atomic seen-set rebuild

Both `prune_audit_logs` and the two `_ensure_*_seen_loaded` methods follow the rebuild-and-swap pattern: local sets are constructed during the pass, and the corresponding `self._*_seen` field(s) are reassigned only after the read succeeds.

**Two per-file flags govern the lifecycle.** `_audit_seen_initialized` tracks whether `_audit_seen` reflects `events.jsonl`; `_outcomes_seen_initialized` tracks whether `_dialogue_outcomes_seen` and `_delegation_outcomes_seen` reflect `outcomes.jsonl`. The two flags are flipped independently so audit and outcomes lifecycle events do not couple.

`prune_audit_logs` clears **both** flags as the first step of the call (before any disk mutation), then restores each one immediately after its file's atomic seen-set reassignment. If the audit pass succeeds but the outcomes pass raises, `_audit_seen_initialized` is `True` (audit committed) while `_outcomes_seen_initialized` remains `False` (cleared at entry, unrestored). The next `append_dialogue_audit_event_once` is served from the freshly-committed in-memory audit seen-set with no disk read; the next outcomes append triggers `_ensure_outcomes_seen_loaded()` and reloads from the untouched `outcomes.jsonl`. **This invalidate-before-disk-mutation discipline is load-bearing for re-runnable pruning:** without per-file flag invalidation, a partial cross-file prune on an already-initialized journal would leave one file's in-memory set out of sync with disk, causing later appends to silently skip records that no longer exist on disk.

`_ensure_audit_seen_loaded()` is a no-op when `_audit_seen_initialized` is `True`. If it raises mid-load, that flag stays `False` and the next audit append retries.

`_ensure_outcomes_seen_loaded()` is a no-op when `_outcomes_seen_initialized` is `True`. If it raises mid-load, that flag stays `False` and the next outcomes append (dialogue or delegation) retries. Because both outcomes seen-sets share a source file, a single read pass populates both — no double-read in steady state.

### 5.7 Per-file seen-set load semantics

Two private methods, one per source file. Each is independently triggered by the relevant `append_*_once` site and independently flag-gated. **Audit appends do not depend on `outcomes.jsonl` readability, and vice versa.**

```python
def _ensure_audit_seen_loaded(self) -> None:
    if self._audit_seen_initialized:
        return

    new_audit_seen: set[_AuditDedupKey] = set()

    # UnicodeDecodeError → quarantine + empty set, flag True (round-6 F1).
    # OSError or other exceptions propagate; flag stays False; the next
    # audit append retries the load. Outcomes appends remain unaffected —
    # they consult their own flag and file.
    try:
        self._populate_seen_from_file(
            self._audit_path,
            lambda r: _populate_from_audit_record(r, new_audit_seen),
        )
    except UnicodeDecodeError as exc:
        self._quarantine_corrupt_jsonl(self._audit_path, reason=exc)
        # new_audit_seen remains empty; next append_dialogue_audit_event_once
        # writes a fresh events.jsonl (§2 Contract quarantine trade-off:
        # records present only in the quarantined file may re-append as
        # duplicates).

    self._audit_seen = new_audit_seen
    self._audit_seen_initialized = True


def _ensure_outcomes_seen_loaded(self) -> None:
    if self._outcomes_seen_initialized:
        return

    new_dialogue_outcomes_seen: set[_DialogueOutcomeDedupKey] = set()
    new_delegation_outcomes_seen: set[_DelegationOutcomeDedupKey] = set()

    # Single read pass over outcomes.jsonl populates BOTH outcomes seen-sets
    # (dialogue and delegation) via _populate_from_outcome_record's dispatch
    # on outcome_type. No double-read; the two sets are reassigned together
    # under the single _outcomes_seen_initialized flag.
    #
    # UnicodeDecodeError → quarantine + both empty sets, flag True
    # (round-6 F1). OSError or other exceptions propagate.
    try:
        self._populate_seen_from_file(
            self._outcomes_path,
            lambda r: _populate_from_outcome_record(
                r, new_dialogue_outcomes_seen, new_delegation_outcomes_seen,
            ),
        )
    except UnicodeDecodeError as exc:
        self._quarantine_corrupt_jsonl(self._outcomes_path, reason=exc)
        # Both outcomes seen-sets remain empty for the same reason as audit.

    self._dialogue_outcomes_seen = new_dialogue_outcomes_seen
    self._delegation_outcomes_seen = new_delegation_outcomes_seen
    self._outcomes_seen_initialized = True
```

`_populate_seen_from_file` tolerates malformed lines exactly as the legacy `_jsonl_contains` did: blank lines, `json.JSONDecodeError`, and non-dict records are skipped. A corrupt historical line never disables future writes. **Invalid UTF-8 is byte-level corruption and triggers quarantine on this path, not propagation.** Each `_ensure_*_seen_loaded` catches `UnicodeDecodeError` from `_populate_seen_from_file`, invokes `_quarantine_corrupt_jsonl` (§5.2c), leaves the local seen-set builders empty, and flips the per-file flag to `True`. The next `append_*_once` writes a fresh JSONL record to a newly-created file. This handling is **identical** to the startup-prune handling in `prune_audit_logs`, closing the failure-class boundary that round-6 F1 identified: there is no longer a runtime path where a corrupt file at startup leaks `UnicodeDecodeError` into `dialogue._finalize_confirmed_turn` and becomes `CommittedTurnFinalizationError`. The explicit duplicate-record trade-off (§2 Contract) applies on this path too — records present only in the quarantined file may re-append as duplicates on subsequent calls.

### 5.8 Append-once update-after-success invariant

Each `append_*_once` method triggers only its own source file's seen-set load.

```python
def append_dialogue_audit_event_once(self, event: AuditEvent) -> None:
    self._ensure_audit_seen_loaded()   # only events.jsonl is read
    key: _AuditDedupKey = (event.action, event.collaboration_id, event.turn_id)
    if key in self._audit_seen:
        return
    self.append_audit_event(event)   # may raise — do NOT add key on failure
    self._audit_seen.add(key)


def append_dialogue_outcome_once(self, record: OutcomeRecord) -> None:
    self._ensure_outcomes_seen_loaded()   # only outcomes.jsonl is read
    key: _DialogueOutcomeDedupKey = (
        record.outcome_type, record.collaboration_id, record.turn_id,
    )
    if key in self._dialogue_outcomes_seen:
        return
    self.append_outcome(record)
    self._dialogue_outcomes_seen.add(key)


def append_delegation_outcome_once(self, record: DelegationOutcomeRecord) -> None:
    self._ensure_outcomes_seen_loaded()   # only outcomes.jsonl is read
    key: _DelegationOutcomeDedupKey = (record.outcome_type, record.job_id)
    if key in self._delegation_outcomes_seen:
        return
    self.append_delegation_outcome(record)
    self._delegation_outcomes_seen.add(key)
```

The seen-set is mutated only after the underlying append IO returns successfully. If `append_audit_event` / `append_outcome` / `append_delegation_outcome` raises, the key remains absent from the set; a later retry can still write the record.

**Cross-file failure isolation:** an unreadable `outcomes.jsonl` blocks `append_dialogue_outcome_once` and `append_delegation_outcome_once` (both call `_ensure_outcomes_seen_loaded()`), but `append_dialogue_audit_event_once` succeeds — it only depends on `events.jsonl` being readable. The symmetric isolation holds for an unreadable `events.jsonl`. This matches the API surface: audit and outcomes are independent retention domains.

### 5.9 Dedup-key semantic note

`_AuditDedupKey` allows `turn_id=None`. Two audit events with `(action, collaboration_id, None)` collapse to one. This **preserves current `_jsonl_contains` behavior** (`None == None` in Python equality). It is not a generally safe dedup model — future audit event types that need `turn_id`-independent dedup should be modeled as a contract addition with their own test, not an emergent property of `None`-equality.

## 6. Wiring & Lifecycle

### 6.1 Bootstrap call site

In `scripts/codex_runtime_bootstrap.py`, immediately after `OperationJournal` construction inside `main()`:

```python
import logging

logger = logging.getLogger(__name__)


def main() -> None:
    plugin_data_path = default_plugin_data_path()
    journal = OperationJournal(plugin_data_path)

    try:
        summary = journal.prune_audit_logs()
    except OSError:
        # UnicodeDecodeError is no longer in this catch list — invalid UTF-8
        # is handled inside prune_audit_logs via _quarantine_corrupt_jsonl
        # (§5.2c) and surfaces in PruneSummary.audit_quarantined_to /
        # outcomes_quarantined_to. OSError still covers IO failures from
        # read/write/replace, AND a quarantine-rename OSError (permission
        # denied, ENOSPC, etc.) that propagates from the quarantine helper.
        logger.warning(
            "startup retention cleanup failed or incomplete; continuing",
            exc_info=True,
        )
    else:
        summary_msg = (
            "audit prune complete: audit_retained=%d audit_dropped=%d "
            "audit_retained_malformed=%d outcomes_retained=%d "
            "outcomes_dropped=%d outcomes_retained_malformed=%d "
            "audit_quarantined_to=%s outcomes_quarantined_to=%s"
        )
        summary_args = (
            summary.audit_retained,
            summary.audit_dropped,
            summary.audit_retained_malformed,
            summary.outcomes_retained,
            summary.outcomes_dropped,
            summary.outcomes_retained_malformed,
            summary.audit_quarantined_to,
            summary.outcomes_quarantined_to,
        )
        if (
            summary.audit_retained_malformed > 0
            or summary.outcomes_retained_malformed > 0
            or summary.audit_quarantined_to is not None
            or summary.outcomes_quarantined_to is not None
        ):
            # Either: TTL-exempt malformed records exist on disk, OR a file
            # was quarantined this pass (round-6 F1). Escalate the summary
            # so the signal is visible via logging.lastResort before F18
            # lands. The quarantine helper already fired its own WARNING at
            # the moment of rename; this summary WARNING ties the per-file
            # event to the run-level summary for log correlation.
            logger.warning(summary_msg, *summary_args)
        else:
            logger.info(summary_msg, *summary_args)

    # ... rest of bootstrap (ControlPlane, registries, McpServer) unchanged ...
```

No concrete `now` argument is passed — production consumes `journal._clock()` via `_now()`. The catch is narrowed to **`OSError` only** as of round-6 — `UnicodeDecodeError` is handled inside `prune_audit_logs` per file via `_quarantine_corrupt_jsonl` (§5.2c) and never propagates from the orchestrator. `OSError` still covers IO-level failures (read/write/replace errors) and quarantine-rename failures (the helper does not swallow its own `OSError`). `json.JSONDecodeError` is *not* in this catch list because malformed-JSON records are line-local retained data (§5.3 retain-on-uncertainty), never raised out of the prune pass. Programming errors (`ValueError` from naive clocks, `AttributeError`, etc.) are not caught and surface as bootstrap failures.

Without `logging.basicConfig` (which F18 will provide), Python's logging defaults dispatch `logger.warning(...)` through `logging.lastResort` to stderr — so the prune-failure signal **and** the malformed-retained-nonzero signal are both observable to whatever process sees the MCP server's stderr (typically Claude Code), even before F18. `logger.info(...)` is below the lastResort threshold and is discarded by default; operator visibility into the *routine* success-summary `info` call requires F18 or `caplog`. All paths are testable via `caplog` or a monkeypatched logger.

### 6.2 Factory-deferred reality

`OperationJournal` is constructed eagerly in `bootstrap.main()`. Both `_dialogue_factory` and `_delegation_factory` receive the same instance. Controllers may be lazy-initialized via `McpServer._ensure_*_controller`, but the journal — and therefore the prune — runs once at process startup regardless. F4's lifecycle is decoupled from F12's lifecycle question.

### 6.3 Re-runnable prune

`prune_audit_logs()` is safe to call multiple times. Each invocation:
- Recomputes `cutoff` from the current `_now()` (or explicit `now=`).
- Clears **both** `_audit_seen_initialized = False` and `_outcomes_seen_initialized = False` before any disk mutation (per-file invalidate-before-disk-mutation discipline — see §5.6).
- Rebuilds the per-file seen-sets from scratch in two passes (one per file).
- Restores each per-file flag to `True` **independently**, immediately after its file's seen-set is atomically reassigned. The audit flag is restored after the audit pass; the outcomes flag is restored after the outcomes pass.
- Rewrites each file atomically per file (§5.5). A failed later-file prune can leave an earlier-file already rewritten, putting the canonical files in a mixed-prune state (§2 Contract — per-file, not pair-wise). Append correctness across that state is preserved because each file's flag is restored only on that file's success: the next `append_*_once` for the failed-file domain reloads from disk via its own `_ensure_*_seen_loaded()`, while the succeeded-file domain serves appends from in-memory state.

A second prune after time has advanced correctly evicts newly-expired keys from both files independently.

### 6.4 Test fixture pattern

| Test scenario | Construction |
|---|---|
| Default dedup behavior, no time-sensitivity | `OperationJournal(plugin_data_path=tmp_path)` |
| Pruning correctness with fake clock | `OperationJournal(plugin_data_path=tmp_path, clock=lambda: aware_datetime)` |
| Explicit cutoff override | Pass `now=aware_datetime` to `prune_audit_logs()` |
| Direct-construction dedup safety | Construct without calling prune; first `append_*_once` exercises `_ensure_audit_seen_loaded` or `_ensure_outcomes_seen_loaded` (per source file) |

A small fixture helper keeps tests tight:

```python
def fixed_clock(at: datetime) -> Callable[[], datetime]:
    return lambda: at
```

### 6.5 Operating envelope

This design optimizes for the following deployment shape:

- Single-user, single MCP process per `plugin_data_path` (see §2 Contract — single-writer assumption).
- Hours-scale sessions, not multi-day.
- Low-to-moderate volume: estimated steady-state per 30-day window is ~1k–10k records each for `events.jsonl` and `outcomes.jsonl`.
- Resident dedup sets across all three types: ~1 MB upper bound at the high end of the volume estimate.
- Startup prune + population: single linear pass per file, expected milliseconds at this volume.

Deployments outside this envelope (multi-user, multi-day sessions, sustained high-volume traffic) may need a different retention substrate (incremental prune, paged dedup, on-disk seen-set persistence). The current design intentionally optimizes for the named envelope; the seen-set substrate is the first refactor target if those limits are hit. No volume or latency metrics are emitted in v1 — operator visibility into envelope adherence rides F18 alongside the prune-summary logging.

## 7. Spec Changes to `docs/specs/recovery-and-journal.md`

### 7.1 §Two-Log Architecture table

Update the "Retention" row of the Audit Log column to read:

> TTL-based (30 days from event timestamp), pruned at plugin startup

The "Write discipline" row is unchanged ("Best-effort append").

### 7.1a Add §Operational Outcomes subsection after §Why Two Logs

Insert a new subsection so `analytics/outcomes.jsonl` has an architecture-level mention in the owner spec (currently it appears only as a retention bullet, hidden under "Audit Log"). The "Two-Log Architecture" title remains — outcomes is a *sibling* of the Audit Log in retention behavior, not a third equally-distinct log.

> ### Operational Outcomes
>
> A third file, `${CLAUDE_PLUGIN_DATA}/analytics/outcomes.jsonl`, holds delegation and dialogue terminal outcome records (`OutcomeRecord` and `DelegationOutcomeRecord`). It shares the Audit Log's retention class — best-effort append, 30-day TTL, startup-pruned, single-writer ownership — but uses a different record format (typed terminal outcomes rather than per-event audit entries) and a different consumer (retrospective diagnostics rather than incident reconstruction).
>
> **Outcomes are operational diagnostics with a 30-day operational horizon, not long-term analytics history.** A future feature that consumes outcomes for long-term analytics must introduce a separate retention class before shipping.

### 7.2 §Audit Log → Retention subsection

Replace the existing three bullets with:

> Operational retention for audit and outcome JSONL records uses the same 30-day TTL. Outcomes are treated as **operational diagnostics with a 30-day operational horizon**, not long-term analytics history; if a future feature consumes outcomes for long-term analytics, a separate retention class must be introduced before the consuming feature ships.
>
> - **Default TTL:** 30 days from event timestamp.
> - **Storage:** `${CLAUDE_PLUGIN_DATA}/audit/events.jsonl` (audit events) and `${CLAUDE_PLUGIN_DATA}/analytics/outcomes.jsonl` (dialogue and delegation outcomes).
> - **Cleanup:** Pruned at plugin startup. Pruning is a pure filter — retained record bytes are preserved (with a single `\n` appended to the final retained line if absent, to keep the file JSONL-append-safe). Records are never re-serialized through `json.dumps`.
> - **Timestamp parsing:** Pruning compares timezone-aware ISO 8601 timestamps. Records with missing, non-string, unparseable, or timezone-naive `timestamp` fields are retained (retain-on-uncertainty: ambiguous records are never silently erased). These malformed-timestamp records are **TTL-exempt by design** — the 30-day TTL applies only to records with parseable, timezone-aware timestamps; sufficiently corrupt records can survive past the 30-day window indefinitely.
> - **Per-file atomicity:** Pruning is atomic per file (`events.jsonl` and `outcomes.jsonl` are independent retention surfaces), not pair-wise. A failure of one file's prune after the other has already been rewritten leaves a mixed-prune state; the next startup re-runs both files.
> - **Encoding and line endings:** Files are UTF-8 with LF-only line endings by construction across all Python-supported platforms — every appender and the prune temp-file write open with `newline="\n"`, which suppresses Python's default platform-dependent text-mode newline translation (which would otherwise emit `\r\n` on Windows). An invalid UTF-8 byte sequence in either file is treated as **file-level corruption with automatic quarantine**: both the startup prune path and the runtime append-once readers catch `UnicodeDecodeError` per file, rename the affected file to a sibling `<stem>.corrupt-<utc-ts><suffix>` (deterministic `.1`, `.2`, ... numeric suffix on collision), log at `WARNING`, and proceed with an empty in-memory dedup set for that file. The next `append_*` call writes a fresh JSONL record into a newly-created file; the other file is unaffected. Records present only in the quarantined file may re-append as duplicates on subsequent calls — this is the explicit accepted trade-off: corrupt diagnostic data does not block live workflow finalization, and the quarantined file remains available for forensic inspection. JSONL-record-level malformed-JSON is *not* in this corruption class — see Timestamp parsing for the record-level retain-on-uncertainty rule.
> - **Ownership model:** Exactly one MCP process owns a given `${CLAUDE_PLUGIN_DATA}` directory at a time. Concurrent prune from two processes against the same data directory is undefined and unsupported (matches the existing operation-journal ownership model).
> - **Blank lines** are not audit/outcome records and may be removed during pruning.
>
> *Future scope:* periodic-during-session pruning is not implemented in v1. The startup cadence is sufficient for the supported session lifecycle (hours-scale, not multi-day). If future deployments hold the MCP process alive long enough for same-session expiry to matter, a periodic trigger can be added without changing the TTL contract.

### 7.3 §Retention Defaults table and preamble

**Preamble (round-6 F2).** Replace the §Retention Defaults preamble sentence:

> Canonical retention values. All TTLs are measured from `last_touched_at`, not creation time.

with:

> Canonical retention values. TTL triggers vary by resource: see the Trigger column. Most TTLs are measured from `last_touched_at`; audit log and outcome records use their event timestamp.

This closes the contradiction the round-6 review surfaced: the preamble's "All TTLs are measured from `last_touched_at`" sentence contradicted two of its own rows once the audit and outcome rows changed to "From event timestamp."

**Table.** Replace the single "Audit log records" row with two rows:

| Resource | TTL | Trigger |
|---|---|---|
| Audit log records (`events.jsonl`) | 30 days | From event timestamp |
| Outcome records (`outcomes.jsonl`) | 30 days | From event timestamp |

All other rows unchanged.

### 7.4 No changes

Operation Journal, Stale Advisory Context Marker, Crash Recovery Paths, Pending Request Ordering, Unknown Request Handling, Concurrency Limits sections are unchanged by this slice. F12's reserved-event semantics will be addressed in a sibling slice and may then amend the Audit Log → Write Triggers tables.

## 8. Testing Strategy

All journal-internal tests in `tests/test_journal.py`. **Bootstrap-integration tests (§8.9) live in `tests/test_bootstrap.py`** and use that module's established importlib-based loader pattern for `scripts/codex_runtime_bootstrap.py`.

### 8.1 Pruning correctness — happy path
- `test_prune_audit_logs_drops_records_older_than_ttl`
- `test_prune_audit_logs_retains_records_within_ttl`
- `test_prune_audit_logs_retains_record_exactly_at_ttl_boundary` — record dated exactly `now - 30 days`; per the contract (`ts < cutoff`), it is retained. Pins against accidental `<=` inversion.
- `test_prune_audit_logs_empty_file_is_noop`
- `test_prune_audit_logs_missing_file_is_noop`
- `test_prune_audit_logs_returns_correct_summary_counts`

### 8.2 Retain-on-uncertainty (parametrized)
- `test_prune_audit_logs_retains_record_with_malformed_timestamp` — parametrized over (missing field, non-string, unparseable ISO, timezone-naive)
- `test_prune_audit_logs_retains_malformed_json_line` — invalid JSON; raw line preserved (record bytes unchanged; final-newline normalization only applied to the file's last line if it lacked one — see §8.3).
- `test_prune_audit_logs_retains_non_dict_record` — array or scalar JSON line
- `test_prune_audit_logs_drops_blank_lines`
- `test_prune_audit_logs_quarantines_audit_on_invalid_utf8` — pre-populate `events.jsonl` with an invalid UTF-8 byte sequence (e.g., `b"\x80abc\n"`); inject a fixed UTC clock; call `prune_audit_logs()`; assert it does **not** raise; assert `events.jsonl` no longer exists at the original path; assert a sibling `events.corrupt-<expected-utc-ts>.jsonl` exists with the original byte sequence preserved; assert `summary.audit_quarantined_to` equals that quarantine path; assert `_audit_seen` is empty and `_audit_seen_initialized == True`. Pins F1 (round-6): byte-level corruption triggers quarantine, not pass abort. Mirror test (`test_prune_audit_logs_quarantines_outcomes_on_invalid_utf8`) for `outcomes.jsonl`.
- `test_prune_audit_logs_quarantines_only_affected_file` — corrupt `events.jsonl` with invalid UTF-8; populate `outcomes.jsonl` with a single well-formed record; call `prune_audit_logs()`; assert audit was quarantined (`summary.audit_quarantined_to is not None`); assert outcomes pruned normally (`summary.outcomes_quarantined_to is None`, `summary.outcomes_retained == 1`). Pins F1 (round-6): quarantine isolation between files.
- `test_quarantine_uses_deterministic_suffix_on_target_collision` — inject a fixed UTC clock; pre-create a file at the exact quarantine path the helper would generate (`events.corrupt-<fixed-utc-ts>.jsonl`); pre-populate `events.jsonl` with invalid UTF-8; call `prune_audit_logs()`; assert the new quarantine file uses the `.1` numeric suffix (`events.corrupt-<fixed-utc-ts>.1.jsonl`). Repeat with two pre-existing collisions to assert `.2`. Pins F1 (round-6): deterministic collision handling.
- `test_quarantine_rename_oserror_propagates_as_oserror` — pre-populate `events.jsonl` with invalid UTF-8; monkey-patch `Path.rename` (or `os.rename`) to raise `OSError`; call `prune_audit_logs()`; assert it raises `OSError`, not `UnicodeDecodeError`. Pins F1 (round-6): quarantine itself does not catch broad exceptions; rename failure is an IO-class failure.

### 8.3 Raw-line retention invariant
- `test_prune_audit_logs_preserves_record_bytes_for_retained_records` — write a record with unsorted keys / extra whitespace; after prune, retained record bytes are identical to input (`json.dumps` is not invoked on retained records).
- `test_prune_audit_logs_appends_trailing_newline_to_missing_eof_newline` — write a file whose final retained record lacks a trailing newline; assert the rewritten file ends with `\n` so the next `append_*` call produces a valid JSONL record boundary. Pins F2 (round-4): the contract is "record bytes preserved + final-newline normalization for append safety," not strict byte-for-byte.
- `test_prune_audit_logs_pins_lf_only_file_format` — write a small file with `\r\n` line endings; assert the rewritten file uses `\n` exclusively (no `\r` bytes remain). Pins F2 (round-5) and F3 (round-6): file format is LF-only by construction across all Python-supported platforms (§2 Contract). The prune temp-file write pins `newline="\n"` so the assertion passes on Windows too; without the pin, default text-mode `open("w", ...)` would emit `\r\n` on Windows. The test is therefore a **double pin**: it catches a future implementer who switches to `newline=""` (preserves CRLF) AND a future implementer who removes `newline="\n"` (re-introduces platform-dependent emission).

### 8.4 Atomic replacement
- `test_prune_audit_logs_preserves_original_on_pre_replace_failure` — patch `os.fsync` (or the temp-file open) to raise; assert original file unchanged.
- `test_prune_audit_logs_preserves_original_on_replace_failure` — patch `os.replace` to raise; assert original file unchanged. Separate test because the failure mode is replace-time, not pre-replace.

### 8.5 Clock seam
- `test_prune_audit_logs_uses_injected_clock`
- `test_prune_audit_logs_rejects_naive_clock` — `clock=lambda: datetime(2026, 5, 12)`; first `_now()` raises `ValueError`.
- `test_prune_audit_logs_rejects_naive_explicit_now` — `now=datetime(2026, 5, 12)`; raises `ValueError`.
- `test_prune_audit_logs_normalizes_non_utc_aware_timestamps` — record timestamp at `+09:00` offset, cutoff in UTC; assert correct comparison.

### 8.6 Re-runnable prune (atomic rebuild)
- `test_prune_audit_logs_evicts_newly_expired_keys_on_second_run` — record A at T0 retained; advance clock past TTL; prune again; A is dropped AND removed from `_audit_seen`.
- `test_prune_audit_logs_restores_per_file_flag_after_each_pass` — successful prune. After audit pass completes, assert `_audit_seen_initialized == True`; after outcomes pass completes, assert `_outcomes_seen_initialized == True`. Pins per-file lifecycle: each flag is restored independently, not as a final batch.
- `test_prune_audit_logs_partial_failure_keeps_outcomes_flag_cleared` — initialize seen-sets via a successful first prune (both flags True); patch outcomes pass to raise `OSError` mid-pass on the second run. Assert: second prune raises; `_audit_seen_initialized == True` (audit pass committed); `_outcomes_seen_initialized == False` (never restored). Next `append_dialogue_audit_event_once` consults in-memory state directly (no disk read needed). Next `append_dialogue_outcome_once` triggers `_ensure_outcomes_seen_loaded()` and reloads from disk. Pins F1 (round-4 PA): per-file flag invalidation enables partial-failure isolation between domains.
- `test_unreadable_outcomes_does_not_block_audit_append_once` — patch `_outcomes_path.open` to raise `OSError` on read; call `append_dialogue_audit_event_once` (which only triggers `_ensure_audit_seen_loaded()`); assert the audit append succeeds. Then call `append_dialogue_outcome_once` and assert it raises `OSError` (since outcomes file is unreadable). Pins F1 (round-4): cross-file failure isolation at the append-once boundary.

### 8.7 Dedup-set construction
- `test_append_dialogue_audit_event_once_loads_audit_seen_on_first_call` (no prune) — only `events.jsonl` is read; `_outcomes_seen_initialized` remains `False`.
- `test_append_dialogue_outcome_once_loads_outcomes_seen_on_first_call` (no prune) — only `outcomes.jsonl` is read; `_audit_seen_initialized` remains `False`.
- `test_outcomes_seen_loaded_populates_both_dialogue_and_delegation_sets` — single read of `outcomes.jsonl` populates both `_dialogue_outcomes_seen` and `_delegation_outcomes_seen` in one pass; pins the shared-read invariant.
- `test_ensure_audit_seen_loaded_tolerates_corrupt_jsonl_line` — corrupt line in `events.jsonl` does not block population.
- `test_ensure_outcomes_seen_loaded_tolerates_corrupt_jsonl_line` — same for `outcomes.jsonl`.
- `test_ensure_audit_seen_loaded_does_not_mark_initialized_on_failure` — patch population to raise a non-UTF-8 exception (e.g., `OSError`); assert `_audit_seen_initialized` remains `False` and second call retries; `_outcomes_seen_initialized` is unaffected.
- `test_ensure_outcomes_seen_loaded_does_not_mark_initialized_on_failure` — same for outcomes flag with a non-UTF-8 exception; `_audit_seen_initialized` unaffected.
- `test_ensure_audit_seen_loaded_quarantines_on_invalid_utf8` — construct journal without calling prune; pre-populate `events.jsonl` with an invalid UTF-8 byte sequence; call `append_dialogue_audit_event_once(...)` with a valid event; assert the corrupt file was renamed to a `events.corrupt-<utc-ts>.jsonl` sibling; assert the audit append succeeded against a fresh `events.jsonl` containing exactly one record; assert `_audit_seen_initialized == True` and `_audit_seen` contains exactly the newly-appended key (not any pre-quarantine ghost). Pins F1 (round-6): runtime path shares the same quarantine policy as startup, closing the failure-class boundary that would otherwise leak `UnicodeDecodeError` into `dialogue._finalize_confirmed_turn`.
- `test_ensure_outcomes_seen_loaded_quarantines_on_invalid_utf8` — mirror for outcomes, using `append_dialogue_outcome_once`.
- `test_append_after_quarantine_can_re_append_quarantined_record_as_duplicate` — quarantine `events.jsonl` via the runtime path with a record `R` present only in the corrupt file (so `R` is unrecoverable from disk); call `append_dialogue_audit_event_once(R)` twice; assert both calls add records to disk (no dedup because the in-memory seen-set was emptied by quarantine and the pre-quarantine seen state was lost with the file). Pins F1 (round-6) explicit trade-off: post-quarantine records can re-append as duplicates — corrupt diagnostic data does not block live workflow finalization.

### 8.8 Dedup-set update invariant
- `test_append_dialogue_audit_event_once_skips_when_key_in_seen_set`
- `test_append_dialogue_audit_event_once_updates_seen_set_only_after_successful_append` — patch `append_audit_event` to raise; assert key NOT added; assert retry with functional IO succeeds.
- Mirror tests for `append_dialogue_outcome_once` and `append_delegation_outcome_once`.

### 8.9 Bootstrap integration

**Location: `tests/test_bootstrap.py`** (not `test_journal.py`). Use that module's existing importlib-based loader pattern for `scripts/codex_runtime_bootstrap.py`.

- `test_bootstrap_logs_info_summary_when_prune_succeeds_with_zero_malformed` — patch `McpServer.run` to no-op; patch `default_plugin_data_path` to `tmp_path`; populate journal with well-formed records only; capture log via `caplog`; assert `logger.info` (level `INFO`) with summary fields fired.
- `test_bootstrap_warns_summary_when_prune_succeeds_with_nonzero_audit_malformed` — same setup but with one malformed-timestamp record in `events.jsonl`; assert summary fires at level `WARNING`, not `INFO`. Pins F3 (round-4): default-visible operator signal for the silent-accumulation case.
- `test_bootstrap_warns_summary_when_prune_succeeds_with_nonzero_outcomes_malformed` — mirror for `outcomes.jsonl`.
- `test_bootstrap_warns_when_prune_raises_oserror` — patch `OperationJournal.prune_audit_logs` to raise `OSError`; assert `logger.warning` fired and bootstrap continues to `server.run()` (which is itself patched).
- `test_bootstrap_warns_summary_when_audit_quarantined` — pre-populate `events.jsonl` with an invalid UTF-8 byte sequence; run bootstrap with `caplog`; assert the summary message fires at `WARNING` (not `INFO`); assert the formatted message includes `audit_quarantined_to=` with the quarantine path. Pins F1 (round-6): quarantine surfaces in the bootstrap summary as a default-visible WARNING.
- `test_bootstrap_warns_summary_when_outcomes_quarantined` — mirror for outcomes.
- `test_bootstrap_does_not_swallow_unicode_decode_error_directly` — patch `OperationJournal.prune_audit_logs` to raise `UnicodeDecodeError` directly (i.e., from a non-quarantine code path that escapes the helper); assert bootstrap re-raises (UTF-8 errors are no longer in the catch list — they should be handled inside `prune_audit_logs` via quarantine; any `UnicodeDecodeError` that escapes is a contract bug). Pins F1 (round-6): catch list is `OSError` only.
- `test_bootstrap_does_not_swallow_value_error` — patch `OperationJournal.prune_audit_logs` to raise `ValueError`; assert bootstrap re-raises (programming errors are not caught). Pins the precise catch list `OSError`.

### 8.10 Legacy test migration
- `rg "_jsonl_contains" tests/` to inventory.
- Any test that exercised the linear-scan dedup is reframed against the in-memory set behavior.
- Tests asserting "this `*_once` method skips a duplicate" stay valid; only the underlying mechanism changes.

## 9. Verification

Before claiming complete:

```bash
uv run pytest tests/test_journal.py tests/test_bootstrap.py -v  # new + existing tests pass
uv run pytest -q                                                # full suite passes
uv run ruff check .                                             # no lint regressions across server/ scripts/ tests/
rg "_jsonl_contains" server/ scripts/                           # zero hits in production code
rg "_seen_sets_initialized" server/ scripts/                    # zero hits — the unified flag was split into per-file flags
rg "except \(OSError, UnicodeDecodeError\)" scripts/            # zero hits — round-6 narrowed the bootstrap catch to OSError only
```

The `_quarantine_corrupt_jsonl` helper (round-6 F1) must be called from exactly four sites in `server/journal.py`: two from `prune_audit_logs` (audit and outcomes try/except blocks) and one each from `_ensure_audit_seen_loaded` and `_ensure_outcomes_seen_loaded`. A `rg "_quarantine_corrupt_jsonl" server/journal.py` returning fewer than 5 matches (1 def + 4 call sites) means the failure-class-boundary closure did not land everywhere. Spot-check by reading the four call sites for the `except UnicodeDecodeError` catch.

Per the verification-before-completion discipline, the implementation plan must include this block as its final step and report the actual output before any "done" claim.

## 10. Open Questions and Future Scope

- **F12 reserved `crash`/`restart` audit events** — deferred to a sibling slice. Open design questions there:
  - Controller-scoped emission (each `recover_startup` independently emits) versus process-startup-aggregate emission (one pair per startup, regardless of how many controllers detected conditions).
  - Lazy-factory bootstrap implications: `McpServer.startup()` may run with controllers still `None`. Aggregate emission needs a coordination model.
  - Required-field shape: `AuditEvent.runtime_id` is `str` (required); aggregate events may not have a single owning runtime. The `extra: dict` field is the natural escape hatch but the model design is the sibling slice's call.

- **Env-configurable TTL** — out of scope this slice. Belongs to a future F19 config-inventory effort that establishes the README config-inventory norm before adding new env knobs.

- **Periodic-during-session pruning** — out of scope this slice. Spec records it as future scope. A future trigger mechanism (opportunistic-during-write or scheduled callback) can be added without changing the TTL contract.

- **Audit-log fsync, hash chain, HMAC** — F12's other sub-recommendations. Not in this slice. The audit log remains "best-effort append".

- **Outcome-record retention policy** — this slice applies the 30-day TTL to `outcomes.jsonl` because F4 explicitly names both files as having the unbounded-growth problem. If long-term analytics ever become a goal, a separate retention class for outcomes can be added without touching audit log semantics.
