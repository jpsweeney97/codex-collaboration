from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import pytest

from server.journal import OperationJournal, PruneSummary
from server.models import (
    AuditEvent,
    DelegationOutcomeRecord,
    OperationJournalEntry,
    OutcomeRecord,
    StaleAdvisoryContextMarker,
)


def test_stale_marker_keys_are_normalized_on_write(tmp_path: Path) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    journal.write_stale_marker(
        StaleAdvisoryContextMarker(
            repo_root=str(tmp_path / "."),
            promoted_artifact_hash="hash-1",
            job_id="job-1",
            recorded_at="2026-03-27T15:00:00Z",
        )
    )

    marker = journal.load_stale_marker(tmp_path)
    assert marker is not None
    assert marker.repo_root == str(tmp_path.resolve())


def test_stale_marker_write_replaces_prior_hash_for_repo_root(tmp_path: Path) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    normalized_root = str(tmp_path.resolve())
    journal.write_stale_marker(
        StaleAdvisoryContextMarker(
            repo_root=normalized_root,
            promoted_artifact_hash="hash-1",
            job_id="job-1",
            recorded_at="2026-03-27T15:00:00Z",
        )
    )
    journal.write_stale_marker(
        StaleAdvisoryContextMarker(
            repo_root=normalized_root,
            promoted_artifact_hash="hash-2",
            job_id="job-2",
            recorded_at="2026-03-27T15:05:00Z",
        )
    )

    marker = journal.load_stale_marker(tmp_path)
    assert marker is not None
    assert marker.promoted_artifact_hash == "hash-2"


def test_clear_stale_marker_uses_normalized_repo_root(tmp_path: Path) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    journal.write_stale_marker(
        StaleAdvisoryContextMarker(
            repo_root=str(tmp_path.resolve()),
            promoted_artifact_hash="hash-1",
            job_id="job-1",
            recorded_at="2026-03-27T15:00:00Z",
        )
    )

    journal.clear_stale_marker(Path(str(tmp_path / ".")))

    assert journal.load_stale_marker(tmp_path) is None


def _make_intent(
    key: str = "sess-1:collab-1",
    operation: str = "thread_creation",
    collab: str = "collab-1",
) -> OperationJournalEntry:
    return OperationJournalEntry(
        idempotency_key=key,
        operation=operation,
        phase="intent",
        collaboration_id=collab,
        created_at="2026-03-28T00:00:00Z",
        repo_root="/repo",
    )


def _fixed_clock(at: datetime) -> Callable[[], datetime]:
    return lambda: at


def _mutable_clock(at: list[datetime]) -> Callable[[], datetime]:
    """Allow tests to advance the clock between prune calls."""
    return lambda: at[0]


def _audit_event(
    *,
    event_id: str = "event-1",
    timestamp: str = "2026-04-21T00:00:00Z",
    action: str = "dialogue_turn",
    collaboration_id: str = "collab-1",
    runtime_id: str = "rt-1",
    turn_id: str | None = "turn-1",
) -> AuditEvent:
    return AuditEvent(
        event_id=event_id,
        timestamp=timestamp,
        actor="claude",
        action=action,
        collaboration_id=collaboration_id,
        runtime_id=runtime_id,
        context_size=1024,
        turn_id=turn_id,
    )


def _dialogue_outcome(
    *,
    outcome_id: str = "outcome-1",
    timestamp: str = "2026-04-21T00:00:00Z",
    outcome_type: str = "dialogue_turn",
    collaboration_id: str = "collab-1",
    runtime_id: str = "rt-1",
    turn_id: str = "turn-1",
) -> OutcomeRecord:
    return OutcomeRecord(
        outcome_id=outcome_id,
        timestamp=timestamp,
        outcome_type=outcome_type,
        collaboration_id=collaboration_id,
        runtime_id=runtime_id,
        context_size=1024,
        turn_id=turn_id,
        turn_sequence=1,
    )


def _delegation_outcome(
    *,
    outcome_id: str = "delegation-outcome-1",
    timestamp: str = "2026-04-21T00:00:00Z",
    job_id: str = "job-1",
) -> DelegationOutcomeRecord:
    return DelegationOutcomeRecord(
        outcome_id=outcome_id,
        timestamp=timestamp,
        outcome_type="delegation_terminal",
        collaboration_id="collab-delegation",
        runtime_id="rt-delegation",
        job_id=job_id,
        terminal_status="completed",
        base_commit="abc123",
    )


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestAuditRetentionClock:
    def test_timestamp_uses_injected_clock(self, tmp_path: Path) -> None:
        now = datetime(2026, 5, 12, 20, 10, 39, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))

        assert journal.timestamp() == "2026-05-12T20:10:39Z"

    def test_prune_audit_logs_rejects_naive_clock(self, tmp_path: Path) -> None:
        journal = OperationJournal(
            tmp_path / "plugin-data",
            clock=lambda: datetime(2026, 5, 12, 20, 10, 39),
        )

        with pytest.raises(ValueError, match="Journal clock requires"):
            journal.prune_audit_logs()


class TestAuditRetentionPruning:
    def test_prune_audit_logs_drops_records_older_than_ttl(
        self, tmp_path: Path
    ) -> None:
        now = datetime(2026, 5, 12, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        journal.append_audit_event(
            _audit_event(event_id="old", timestamp="2026-04-11T23:59:59Z")
        )
        journal.append_audit_event(
            _audit_event(event_id="new", timestamp="2026-04-12T00:00:00Z")
        )

        summary = journal.prune_audit_logs()

        records = _read_jsonl(audit_path)
        assert [record["event_id"] for record in records] == ["new"]
        assert summary.audit_retained == 1
        assert summary.audit_dropped == 1

    def test_prune_audit_logs_retains_records_within_ttl(
        self, tmp_path: Path
    ) -> None:
        now = datetime(2026, 5, 12, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        journal.append_audit_event(
            _audit_event(event_id="recent-1", timestamp="2026-05-01T00:00:00Z")
        )
        journal.append_audit_event(
            _audit_event(event_id="recent-2", timestamp="2026-05-10T00:00:00Z")
        )

        summary = journal.prune_audit_logs()

        records = _read_jsonl(audit_path)
        assert [record["event_id"] for record in records] == ["recent-1", "recent-2"]
        assert summary.audit_retained == 2
        assert summary.audit_dropped == 0

    def test_prune_audit_logs_retains_record_exactly_at_ttl_boundary(
        self, tmp_path: Path
    ) -> None:
        """A record dated exactly `now - 30 days` must be retained."""
        now = datetime(2026, 5, 12, tzinfo=UTC)
        boundary_ts = (now - timedelta(days=30)).isoformat().replace("+00:00", "Z")
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        journal.append_audit_event(
            _audit_event(event_id="boundary", timestamp=boundary_ts)
        )

        summary = journal.prune_audit_logs()

        records = _read_jsonl(audit_path)
        assert [record["event_id"] for record in records] == ["boundary"]
        assert summary.audit_retained == 1
        assert summary.audit_dropped == 0

    def test_prune_audit_logs_prunes_outcomes_jsonl(self, tmp_path: Path) -> None:
        now = datetime(2026, 5, 12, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
        journal.append_outcome(
            _dialogue_outcome(outcome_id="old", timestamp="2026-04-11T23:59:59Z")
        )
        journal.append_outcome(
            _dialogue_outcome(outcome_id="new", timestamp="2026-04-12T00:00:00Z")
        )

        summary = journal.prune_audit_logs()

        records = _read_jsonl(outcomes_path)
        assert [record["outcome_id"] for record in records] == ["new"]
        assert summary.outcomes_retained == 1
        assert summary.outcomes_dropped == 1

    def test_prune_audit_logs_missing_files_are_noop(self, tmp_path: Path) -> None:
        now = datetime(2026, 5, 12, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))

        summary = journal.prune_audit_logs()

        assert summary == PruneSummary(0, 0, 0, 0, 0, 0)

    def test_prune_audit_logs_empty_file_is_noop(self, tmp_path: Path) -> None:
        now = datetime(2026, 5, 12, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text("", encoding="utf-8")
        outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
        outcomes_path.parent.mkdir(parents=True, exist_ok=True)
        outcomes_path.write_text("", encoding="utf-8")

        summary = journal.prune_audit_logs()

        assert summary == PruneSummary(0, 0, 0, 0, 0, 0)
        assert audit_path.read_text(encoding="utf-8") == ""
        assert outcomes_path.read_text(encoding="utf-8") == ""

    def test_prune_audit_logs_normalizes_non_utc_aware_timestamps(
        self, tmp_path: Path
    ) -> None:
        now = datetime(2026, 5, 12, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        journal.append_audit_event(
            _audit_event(
                event_id="us-cdt-retain",
                timestamp="2026-04-11T20:00:00-05:00",
                turn_id="turn-A",
            )
        )
        journal.append_audit_event(
            _audit_event(
                event_id="jp-drop",
                timestamp="2026-04-12T08:59:59+09:00",
                turn_id="turn-B",
            )
        )

        summary = journal.prune_audit_logs()

        records = _read_jsonl(audit_path)
        assert [record["event_id"] for record in records] == ["us-cdt-retain"]
        assert summary.audit_retained == 1
        assert summary.audit_dropped == 1


@pytest.mark.parametrize(
    "timestamp_value",
    [
        pytest.param(None, id="missing"),
        pytest.param(42, id="non-string"),
        pytest.param("not-a-date", id="unparseable"),
        pytest.param("2026-04-01T00:00:00", id="timezone-naive"),
    ],
)
def test_prune_audit_logs_retains_records_with_uncertain_timestamps(
    tmp_path: Path, timestamp_value: object
) -> None:
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    record = {
        "event_id": "uncertain",
        "timestamp": timestamp_value,
        "actor": "claude",
        "action": "dialogue_turn",
        "collaboration_id": "collab-1",
        "runtime_id": "rt-1",
        "turn_id": "turn-1",
    }
    if timestamp_value is None:
        record.pop("timestamp")
    audit_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    summary = journal.prune_audit_logs()

    assert _read_jsonl(audit_path)[0]["event_id"] == "uncertain"
    assert summary.audit_retained_malformed == 1


def test_prune_audit_logs_retains_malformed_json_line(tmp_path: Path) -> None:
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text("{not-valid-json\n", encoding="utf-8")

    summary = journal.prune_audit_logs()

    assert audit_path.read_text(encoding="utf-8") == "{not-valid-json\n"
    assert summary.audit_retained == 1
    assert summary.audit_retained_malformed == 1
    assert summary.audit_dropped == 0


def test_prune_audit_logs_retains_non_dict_record(tmp_path: Path) -> None:
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text('[1, 2, 3]\n"a-bare-string"\n42\n', encoding="utf-8")

    summary = journal.prune_audit_logs()

    assert audit_path.read_text(encoding="utf-8") == '[1, 2, 3]\n"a-bare-string"\n42\n'
    assert summary.audit_retained == 3
    assert summary.audit_retained_malformed == 3
    assert summary.audit_dropped == 0


def test_prune_audit_logs_drops_blank_lines(tmp_path: Path) -> None:
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    raw = (
        '{"event_id":"a","timestamp":"2026-05-01T00:00:00Z",'
        '"actor":"claude","action":"dialogue_turn",'
        '"collaboration_id":"collab-1","runtime_id":"rt-1"}\n'
        "\n"
        "   \n"
        '{"event_id":"b","timestamp":"2026-05-02T00:00:00Z",'
        '"actor":"claude","action":"dialogue_turn",'
        '"collaboration_id":"collab-1","runtime_id":"rt-1"}\n'
    )
    audit_path.write_text(raw, encoding="utf-8")

    summary = journal.prune_audit_logs()

    records = _read_jsonl(audit_path)
    assert [record["event_id"] for record in records] == ["a", "b"]
    assert summary.audit_retained == 2
    assert summary.audit_dropped == 0
    assert audit_path.read_text(encoding="utf-8").count("\n") == 2


def test_prune_audit_logs_preserves_retained_record_text_and_adds_final_lf(
    tmp_path: Path,
) -> None:
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    raw = (
        '{"event_id":"kept", "timestamp":"2026-05-01T00:00:00Z", '
        '"actor":"claude", "action":"dialogue_turn", '
        '"collaboration_id":"collab-1", "runtime_id":"rt-1"}'
    )
    audit_path.write_text(raw, encoding="utf-8")

    journal.prune_audit_logs()

    assert audit_path.read_text(encoding="utf-8") == raw + "\n"


def test_prune_audit_logs_pins_lf_only_file_format(tmp_path: Path) -> None:
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.write_bytes(
        (
            '{"event_id":"kept","timestamp":"2026-05-01T00:00:00Z",'
            '"actor":"claude","action":"dialogue_turn",'
            '"collaboration_id":"collab-1","runtime_id":"rt-1"}\r\n'
        ).encode("utf-8")
    )

    journal.prune_audit_logs()

    assert b"\r" not in audit_path.read_bytes()


def test_prune_audit_logs_preserves_original_on_fsync_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    original = (
        '{"event_id":"kept","timestamp":"2026-05-01T00:00:00Z",'
        '"actor":"claude","action":"dialogue_turn",'
        '"collaboration_id":"collab-1","runtime_id":"rt-1"}\n'
    )
    audit_path.write_text(original, encoding="utf-8")

    def fail_fsync(fd: int) -> None:
        raise OSError("fsync failed")

    monkeypatch.setattr(os, "fsync", fail_fsync)

    with pytest.raises(OSError, match="fsync failed"):
        journal.prune_audit_logs()

    assert audit_path.read_text(encoding="utf-8") == original


def test_prune_audit_logs_preserves_original_on_replace_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    original = (
        '{"event_id":"kept","timestamp":"2026-05-01T00:00:00Z",'
        '"actor":"claude","action":"dialogue_turn",'
        '"collaboration_id":"collab-1","runtime_id":"rt-1"}\n'
    )
    audit_path.write_text(original, encoding="utf-8")

    def fail_replace(src: str | Path, dst: str | Path) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        journal.prune_audit_logs()

    assert audit_path.read_text(encoding="utf-8") == original


def test_prune_audit_logs_evicts_newly_expired_keys_on_second_run(
    tmp_path: Path,
) -> None:
    t0 = datetime(2026, 5, 12, tzinfo=UTC)
    clock_state = [t0]
    journal = OperationJournal(tmp_path / "plugin-data", clock=_mutable_clock(clock_state))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    a_ts = "2026-04-13T00:00:00Z"
    journal.append_audit_event(_audit_event(event_id="A", timestamp=a_ts))

    summary1 = journal.prune_audit_logs()
    assert summary1.audit_retained == 1
    assert ("dialogue_turn", "collab-1", "turn-1") in journal._audit_seen

    clock_state[0] = t0 + timedelta(days=31)

    summary2 = journal.prune_audit_logs()
    assert summary2.audit_retained == 0
    assert summary2.audit_dropped == 1
    assert _read_jsonl(audit_path) == []
    assert ("dialogue_turn", "collab-1", "turn-1") not in journal._audit_seen


def test_prune_audit_logs_restores_per_file_flag_after_each_pass(
    tmp_path: Path,
) -> None:
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    journal.append_audit_event(_audit_event(timestamp="2026-05-01T00:00:00Z"))
    journal.append_outcome(_dialogue_outcome(timestamp="2026-05-01T00:00:00Z"))

    journal.prune_audit_logs()

    assert journal._audit_seen_initialized is True
    assert journal._outcomes_seen_initialized is True


def test_prune_audit_logs_partial_failure_keeps_outcomes_flag_cleared(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    journal.append_audit_event(_audit_event(timestamp="2026-05-01T00:00:00Z"))
    journal.append_outcome(_dialogue_outcome(timestamp="2026-05-01T00:00:00Z"))

    journal.prune_audit_logs()
    assert journal._audit_seen_initialized is True
    assert journal._outcomes_seen_initialized is True

    real_pass = journal._prune_jsonl_pass

    def selective_fail(*, path: Path, cutoff: datetime, populate: Callable[..., None]):
        if path == journal._outcomes_path:
            raise OSError("outcomes prune failed")
        return real_pass(path=path, cutoff=cutoff, populate=populate)

    monkeypatch.setattr(journal, "_prune_jsonl_pass", selective_fail)

    with pytest.raises(OSError, match="outcomes prune failed"):
        journal.prune_audit_logs()

    assert journal._audit_seen_initialized is True
    assert journal._outcomes_seen_initialized is False


class TestAuditRetentionSeenSets:
    def test_append_dialogue_audit_event_once_loads_audit_seen_on_first_call(
        self, tmp_path: Path
    ) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        journal.append_audit_event(_audit_event(event_id="existing"))

        journal.append_dialogue_audit_event_once(_audit_event(event_id="duplicate"))

        assert [record["event_id"] for record in _read_jsonl(audit_path)] == [
            "existing"
        ]
        assert journal._audit_seen_initialized is True
        assert journal._outcomes_seen_initialized is False

    def test_append_dialogue_outcome_once_loads_outcomes_seen_on_first_call(
        self, tmp_path: Path
    ) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
        journal.append_outcome(_dialogue_outcome(outcome_id="existing"))

        journal.append_dialogue_outcome_once(_dialogue_outcome(outcome_id="duplicate"))

        assert [record["outcome_id"] for record in _read_jsonl(outcomes_path)] == [
            "existing"
        ]
        assert journal._audit_seen_initialized is False
        assert journal._outcomes_seen_initialized is True

    def test_outcomes_seen_loaded_populates_dialogue_and_delegation_sets(
        self, tmp_path: Path
    ) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
        journal.append_outcome(_dialogue_outcome(outcome_id="dialogue"))
        journal.append_delegation_outcome(_delegation_outcome(outcome_id="delegation"))

        journal.append_dialogue_outcome_once(_dialogue_outcome(outcome_id="dupe-dialogue"))
        journal.append_delegation_outcome_once(
            _delegation_outcome(outcome_id="dupe-delegation")
        )

        assert [record["outcome_id"] for record in _read_jsonl(outcomes_path)] == [
            "dialogue",
            "delegation",
        ]

    def test_append_dialogue_audit_event_once_skips_when_key_in_seen_set(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        event = _audit_event()
        journal._audit_seen = {(event.action, event.collaboration_id, event.turn_id)}
        journal._audit_seen_initialized = True

        def must_not_be_called(event: AuditEvent) -> None:
            raise AssertionError("append_audit_event called despite seen-set hit")

        monkeypatch.setattr(journal, "append_audit_event", must_not_be_called)

        journal.append_dialogue_audit_event_once(event)

    def test_append_dialogue_outcome_once_skips_when_key_in_seen_set(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        record = _dialogue_outcome()
        journal._dialogue_outcomes_seen = {
            (record.outcome_type, record.collaboration_id, record.turn_id)
        }
        journal._outcomes_seen_initialized = True

        def must_not_be_called(record: OutcomeRecord) -> None:
            raise AssertionError("append_outcome called despite seen-set hit")

        monkeypatch.setattr(journal, "append_outcome", must_not_be_called)

        journal.append_dialogue_outcome_once(record)

    def test_append_delegation_outcome_once_skips_when_key_in_seen_set(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        record = _delegation_outcome()
        journal._delegation_outcomes_seen = {(record.outcome_type, record.job_id)}
        journal._outcomes_seen_initialized = True

        def must_not_be_called(record: DelegationOutcomeRecord) -> None:
            raise AssertionError(
                "append_delegation_outcome called despite seen-set hit"
            )

        monkeypatch.setattr(journal, "append_delegation_outcome", must_not_be_called)

        journal.append_delegation_outcome_once(record)


def test_append_dialogue_audit_event_once_updates_seen_only_after_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    event = _audit_event(event_id="event-1")

    def fail_append(event: AuditEvent) -> None:
        raise OSError("append failed")

    monkeypatch.setattr(journal, "append_audit_event", fail_append)
    with pytest.raises(OSError, match="append failed"):
        journal.append_dialogue_audit_event_once(event)

    assert (event.action, event.collaboration_id, event.turn_id) not in journal._audit_seen

    monkeypatch.undo()
    journal.append_dialogue_audit_event_once(event)

    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    assert len(_read_jsonl(audit_path)) == 1


def test_unreadable_outcomes_does_not_block_audit_append_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    original_populate = journal._populate_seen_from_file

    def fail_outcomes_only(
        path: Path, on_record: Callable[[dict[str, Any]], None]
    ) -> None:
        if path == journal._outcomes_path:
            raise OSError("outcomes unreadable")
        original_populate(path, on_record)

    monkeypatch.setattr(journal, "_populate_seen_from_file", fail_outcomes_only)

    journal.append_dialogue_audit_event_once(_audit_event())
    with pytest.raises(OSError, match="outcomes unreadable"):
        journal.append_dialogue_outcome_once(_dialogue_outcome())


def test_ensure_audit_seen_loaded_tolerates_corrupt_jsonl_line(
    tmp_path: Path,
) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    initial_content = (
        "{not-valid-json\n"
        '{"event_id":"valid","timestamp":"2026-05-01T00:00:00Z",'
        '"actor":"claude","action":"dialogue_turn",'
        '"collaboration_id":"collab-1","runtime_id":"rt-1",'
        '"turn_id":"turn-1"}\n'
    )
    audit_path.write_text(initial_content, encoding="utf-8")

    journal.append_dialogue_audit_event_once(_audit_event(event_id="duplicate"))

    assert audit_path.read_text(encoding="utf-8") == initial_content
    assert journal._audit_seen_initialized is True


def test_ensure_outcomes_seen_loaded_tolerates_corrupt_jsonl_line(
    tmp_path: Path,
) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
    outcomes_path.parent.mkdir(parents=True, exist_ok=True)
    initial_content = (
        "{not-valid-json\n"
        '{"outcome_id":"valid","timestamp":"2026-05-01T00:00:00Z",'
        '"outcome_type":"dialogue_turn","collaboration_id":"collab-1",'
        '"runtime_id":"rt-1","context_size":1024,"turn_id":"turn-1",'
        '"turn_sequence":1}\n'
    )
    outcomes_path.write_text(initial_content, encoding="utf-8")

    journal.append_dialogue_outcome_once(_dialogue_outcome(outcome_id="duplicate"))

    assert outcomes_path.read_text(encoding="utf-8") == initial_content
    assert journal._outcomes_seen_initialized is True


def test_ensure_audit_seen_loaded_does_not_mark_initialized_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")

    real_populate = journal._populate_seen_from_file
    call_count = {"n": 0}

    def fail_first_then_succeed(
        path: Path, on_record: Callable[[dict[str, Any]], None]
    ) -> None:
        call_count["n"] += 1
        if path == journal._audit_path and call_count["n"] == 1:
            raise OSError("transient io failure")
        real_populate(path, on_record)

    monkeypatch.setattr(journal, "_populate_seen_from_file", fail_first_then_succeed)

    with pytest.raises(OSError, match="transient io failure"):
        journal.append_dialogue_audit_event_once(_audit_event())

    assert journal._audit_seen_initialized is False
    assert journal._outcomes_seen_initialized is False

    journal.append_dialogue_audit_event_once(_audit_event())
    assert journal._audit_seen_initialized is True


def test_ensure_outcomes_seen_loaded_does_not_mark_initialized_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")

    real_populate = journal._populate_seen_from_file
    call_count = {"n": 0}

    def fail_first_then_succeed(
        path: Path, on_record: Callable[[dict[str, Any]], None]
    ) -> None:
        call_count["n"] += 1
        if path == journal._outcomes_path and call_count["n"] == 1:
            raise OSError("transient io failure")
        real_populate(path, on_record)

    monkeypatch.setattr(journal, "_populate_seen_from_file", fail_first_then_succeed)

    with pytest.raises(OSError, match="transient io failure"):
        journal.append_dialogue_outcome_once(_dialogue_outcome())

    assert journal._outcomes_seen_initialized is False
    assert journal._audit_seen_initialized is False

    journal.append_dialogue_outcome_once(_dialogue_outcome())
    assert journal._outcomes_seen_initialized is True


class TestPhasedJournal:
    def test_write_intent_and_list_unresolved(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.write_phase(_make_intent(), session_id="sess-1")
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 1
        assert unresolved[0].phase == "intent"

    def test_write_dispatched_updates_terminal_phase(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.write_phase(_make_intent(), session_id="sess-1")
        journal.write_phase(
            OperationJournalEntry(
                idempotency_key="sess-1:collab-1",
                operation="thread_creation",
                phase="dispatched",
                collaboration_id="collab-1",
                created_at="2026-03-28T00:00:00Z",
                repo_root="/repo",
                codex_thread_id="thr-1",
            ),
            session_id="sess-1",
        )
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 1
        assert unresolved[0].phase == "dispatched"
        assert unresolved[0].codex_thread_id == "thr-1"

    def test_write_completed_resolves_operation(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.write_phase(_make_intent(), session_id="sess-1")
        journal.write_phase(
            OperationJournalEntry(
                idempotency_key="sess-1:collab-1",
                operation="thread_creation",
                phase="completed",
                collaboration_id="collab-1",
                created_at="2026-03-28T00:00:00Z",
                repo_root="/repo",
            ),
            session_id="sess-1",
        )
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 0

    def test_check_idempotency_returns_terminal_entry(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.write_phase(_make_intent(), session_id="sess-1")
        found = journal.check_idempotency("sess-1:collab-1", session_id="sess-1")
        assert found is not None
        assert found.phase == "intent"

    def test_check_idempotency_returns_none_when_missing(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        assert journal.check_idempotency("no-such-key", session_id="sess-1") is None

    def test_write_phase_uses_fsync(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import os as _os

        fsynced: list[int] = []
        original = _os.fsync

        def tracking(fd: int) -> None:
            fsynced.append(fd)
            original(fd)

        monkeypatch.setattr(_os, "fsync", tracking)
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.write_phase(_make_intent(key="k1", collab="c1"), session_id="sess-1")
        assert len(fsynced) >= 1

    def test_compact_removes_completed_keeps_unresolved_terminal(
        self, tmp_path: Path
    ) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        # key-0: intent → dispatched → completed (should be removed entirely)
        journal.write_phase(_make_intent(key="key-0", collab="c0"), session_id="sess-1")
        journal.write_phase(
            OperationJournalEntry(
                idempotency_key="key-0",
                operation="thread_creation",
                phase="dispatched",
                collaboration_id="c0",
                created_at="2026-03-28T00:00:00Z",
                repo_root="/repo",
                codex_thread_id="thr-0",
            ),
            session_id="sess-1",
        )
        journal.write_phase(
            OperationJournalEntry(
                idempotency_key="key-0",
                operation="thread_creation",
                phase="completed",
                collaboration_id="c0",
                created_at="2026-03-28T00:00:00Z",
                repo_root="/repo",
            ),
            session_id="sess-1",
        )
        # key-1: intent → dispatched (unresolved — should keep only terminal "dispatched")
        journal.write_phase(_make_intent(key="key-1", collab="c1"), session_id="sess-1")
        journal.write_phase(
            OperationJournalEntry(
                idempotency_key="key-1",
                operation="thread_creation",
                phase="dispatched",
                collaboration_id="c1",
                created_at="2026-03-28T00:00:00Z",
                repo_root="/repo",
                codex_thread_id="thr-1",
            ),
            session_id="sess-1",
        )
        # key-2: intent only (unresolved — should keep the intent)
        journal.write_phase(_make_intent(key="key-2", collab="c2"), session_id="sess-1")

        journal.compact(session_id="sess-1")

        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 2
        by_key = {e.idempotency_key: e for e in unresolved}
        assert by_key["key-1"].phase == "dispatched"
        assert by_key["key-1"].codex_thread_id == "thr-1"
        assert by_key["key-2"].phase == "intent"

    def test_compact_uses_atomic_rename(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.write_phase(_make_intent(), session_id="sess-1")
        journal.write_phase(
            OperationJournalEntry(
                idempotency_key="sess-1:collab-1",
                operation="thread_creation",
                phase="completed",
                collaboration_id="collab-1",
                created_at="2026-03-28T00:00:00Z",
                repo_root="/repo",
            ),
            session_id="sess-1",
        )
        journal.compact(session_id="sess-1")
        # After compacting a fully-completed journal, file should be empty or minimal
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 0


class TestDialogueReplaySafeAppends:
    def test_append_dialogue_audit_event_once_skips_duplicate_logical_record(
        self, tmp_path: Path
    ) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.append_dialogue_audit_event_once(
            AuditEvent(
                event_id="event-1",
                timestamp="2026-04-01T00:00:00Z",
                actor="claude",
                action="dialogue_turn",
                collaboration_id="collab-1",
                runtime_id="rt-1",
                context_size=1024,
                turn_id="turn-1",
            )
        )
        journal.append_dialogue_audit_event_once(
            AuditEvent(
                event_id="event-2",
                timestamp="2026-04-01T00:00:01Z",
                actor="claude",
                action="dialogue_turn",
                collaboration_id="collab-1",
                runtime_id="rt-1",
                context_size=1024,
                turn_id="turn-1",
            )
        )

        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        lines = audit_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["event_id"] == "event-1"

    def test_append_dialogue_outcome_once_handles_missing_file_and_skips_duplicate(
        self, tmp_path: Path
    ) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.append_dialogue_outcome_once(
            OutcomeRecord(
                outcome_id="outcome-1",
                timestamp="2026-04-01T00:00:00Z",
                outcome_type="dialogue_turn",
                collaboration_id="collab-1",
                runtime_id="rt-1",
                context_size=1024,
                turn_id="turn-1",
                turn_sequence=1,
            )
        )
        journal.append_dialogue_outcome_once(
            OutcomeRecord(
                outcome_id="outcome-2",
                timestamp="2026-04-01T00:00:01Z",
                outcome_type="dialogue_turn",
                collaboration_id="collab-1",
                runtime_id="rt-1",
                context_size=1024,
                turn_id="turn-1",
                turn_sequence=1,
            )
        )

        outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
        lines = outcomes_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["outcome_id"] == "outcome-1"


class TestReplayHardening:
    def test_wrong_type_field_does_not_crash(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.write_phase(_make_intent(), session_id="sess-1")
        ops_path = tmp_path / "plugin-data" / "journal" / "operations" / "sess-1.jsonl"
        with ops_path.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "idempotency_key": "bad",
                        "operation": "thread_creation",
                        "phase": "intent",
                        "collaboration_id": "c1",
                        "created_at": "2026-01-01T00:00:00Z",
                        "repo_root": "/repo",
                        "turn_sequence": "not-an-int",
                    }
                )
                + "\n"
            )
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 1  # only the valid record

    def test_unknown_operation_value_skipped(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.write_phase(_make_intent(), session_id="sess-1")
        ops_path = tmp_path / "plugin-data" / "journal" / "operations" / "sess-1.jsonl"
        with ops_path.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "idempotency_key": "bad",
                        "operation": "future_operation",
                        "phase": "intent",
                        "collaboration_id": "c1",
                        "created_at": "2026-01-01T00:00:00Z",
                        "repo_root": "/repo",
                    }
                )
                + "\n"
            )
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 1

    def test_bool_as_int_rejected_in_journal(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        ops_path = tmp_path / "plugin-data" / "journal" / "operations" / "sess-1.jsonl"
        ops_path.parent.mkdir(parents=True, exist_ok=True)
        with ops_path.open("w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "idempotency_key": "k1",
                        "operation": "turn_dispatch",
                        "phase": "intent",
                        "collaboration_id": "c1",
                        "created_at": "2026-01-01T00:00:00Z",
                        "repo_root": "/repo",
                        "codex_thread_id": "thr-1",
                        "turn_sequence": True,
                    }
                )
                + "\n"
            )
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 0  # bad record skipped

    def test_extra_fields_ignored(self, tmp_path: Path) -> None:
        """Forward-compat: extra fields in a record must not crash replay."""
        journal = OperationJournal(tmp_path / "plugin-data")
        ops_path = tmp_path / "plugin-data" / "journal" / "operations" / "sess-1.jsonl"
        ops_path.parent.mkdir(parents=True, exist_ok=True)
        with ops_path.open("w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "idempotency_key": "k1",
                        "operation": "thread_creation",
                        "phase": "intent",
                        "collaboration_id": "c1",
                        "created_at": "2026-01-01T00:00:00Z",
                        "repo_root": "/repo",
                        "future_field": "some_value",
                    }
                )
                + "\n"
            )
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 1
        assert unresolved[0].idempotency_key == "k1"

    def test_check_health_reports_schema_violation(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.write_phase(_make_intent(), session_id="sess-1")
        ops_path = tmp_path / "plugin-data" / "journal" / "operations" / "sess-1.jsonl"
        with ops_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"idempotency_key": 123}) + "\n")
        diags = journal.check_health(session_id="sess-1")
        assert len(diags.diagnostics) == 1
        assert diags.diagnostics[0].label == "schema_violation"

    def test_check_health_clean_file(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "plugin-data")
        journal.write_phase(_make_intent(), session_id="sess-1")
        diags = journal.check_health(session_id="sess-1")
        assert diags.diagnostics == ()

    def test_turn_dispatch_without_codex_thread_id_skipped(
        self, tmp_path: Path
    ) -> None:
        """Per-operation requirement: turn_dispatch needs codex_thread_id for recovery.
        dialogue.py:534-538 raises RuntimeError if codex_thread_id is None."""
        journal = OperationJournal(tmp_path / "plugin-data")
        ops_path = tmp_path / "plugin-data" / "journal" / "operations" / "sess-1.jsonl"
        ops_path.parent.mkdir(parents=True, exist_ok=True)
        with ops_path.open("w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "idempotency_key": "k1",
                        "operation": "turn_dispatch",
                        "phase": "dispatched",
                        "collaboration_id": "c1",
                        "created_at": "2026-01-01T00:00:00Z",
                        "repo_root": "/repo",
                        "turn_sequence": 1,
                        # no codex_thread_id — would crash recovery
                    }
                )
                + "\n"
            )
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 0

    def test_thread_creation_dispatched_without_codex_thread_id_skipped(
        self, tmp_path: Path
    ) -> None:
        """Per-operation+phase: thread_creation at dispatched needs codex_thread_id.
        dialogue.py:469-473 raises RuntimeError if codex_thread_id is None."""
        journal = OperationJournal(tmp_path / "plugin-data")
        ops_path = tmp_path / "plugin-data" / "journal" / "operations" / "sess-1.jsonl"
        ops_path.parent.mkdir(parents=True, exist_ok=True)
        with ops_path.open("w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "idempotency_key": "k1",
                        "operation": "thread_creation",
                        "phase": "dispatched",
                        "collaboration_id": "c1",
                        "created_at": "2026-01-01T00:00:00Z",
                        "repo_root": "/repo",
                        # no codex_thread_id — would crash recovery
                    }
                )
                + "\n"
            )
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 0

    def test_thread_creation_intent_without_codex_thread_id_accepted(
        self, tmp_path: Path
    ) -> None:
        """Intent phase does not require codex_thread_id — dispatch hasn't happened."""
        journal = OperationJournal(tmp_path / "plugin-data")
        ops_path = tmp_path / "plugin-data" / "journal" / "operations" / "sess-1.jsonl"
        ops_path.parent.mkdir(parents=True, exist_ok=True)
        with ops_path.open("w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "idempotency_key": "k1",
                        "operation": "thread_creation",
                        "phase": "intent",
                        "collaboration_id": "c1",
                        "created_at": "2026-01-01T00:00:00Z",
                        "repo_root": "/repo",
                    }
                )
                + "\n"
            )
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 1

    def test_turn_dispatch_dispatched_without_turn_sequence_skipped(
        self, tmp_path: Path
    ) -> None:
        """turn_dispatch at dispatched requires turn_sequence for
        turn confirmation (dialogue.py:550-551). Completed phase is a
        resolution marker — production writers omit turn_sequence there."""
        journal = OperationJournal(tmp_path / "plugin-data")
        ops_path = tmp_path / "plugin-data" / "journal" / "operations" / "sess-1.jsonl"
        ops_path.parent.mkdir(parents=True, exist_ok=True)
        with ops_path.open("w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "idempotency_key": "k1",
                        "operation": "turn_dispatch",
                        "phase": "dispatched",
                        "collaboration_id": "c1",
                        "created_at": "2026-01-01T00:00:00Z",
                        "repo_root": "/repo",
                        "codex_thread_id": "thread-1",
                        # no turn_sequence — can never confirm turn
                    }
                )
                + "\n"
            )
        unresolved = journal.list_unresolved(session_id="sess-1")
        assert len(unresolved) == 0


def test_journal_accepts_job_creation_intent(tmp_path: Path) -> None:
    from server.journal import OperationJournal
    from server.models import OperationJournalEntry

    journal = OperationJournal(tmp_path)
    entry = OperationJournalEntry(
        idempotency_key="sess-1:hash-abc",
        operation="job_creation",
        phase="intent",
        collaboration_id="collab-1",
        created_at="2026-04-17T00:00:00Z",
        repo_root="/tmp/repo",
        job_id="job-1",
    )
    journal.write_phase(entry, session_id="sess-1")

    diagnostics = journal.check_health(session_id="sess-1")
    assert diagnostics.schema_violations == ()


def test_journal_accepts_job_creation_dispatched_with_outcome_correlation(
    tmp_path: Path,
) -> None:
    from server.journal import OperationJournal
    from server.models import OperationJournalEntry

    journal = OperationJournal(tmp_path)
    entry = OperationJournalEntry(
        idempotency_key="sess-1:hash-abc",
        operation="job_creation",
        phase="dispatched",
        collaboration_id="collab-1",
        created_at="2026-04-17T00:00:00Z",
        repo_root="/tmp/repo",
        job_id="job-1",
        runtime_id="rt-1",
        codex_thread_id="thr-1",
    )
    journal.write_phase(entry, session_id="sess-1")

    diagnostics = journal.check_health(session_id="sess-1")
    assert diagnostics.schema_violations == ()
    terminal = journal.check_idempotency("sess-1:hash-abc", session_id="sess-1")
    assert terminal is not None
    assert terminal.phase == "dispatched"
    assert terminal.job_id == "job-1"


def test_journal_rejects_job_creation_intent_missing_job_id(tmp_path: Path) -> None:
    import json as _json

    from server.journal import OperationJournal

    journal = OperationJournal(tmp_path)
    path = journal._operations_path("sess-1")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write a malformed record directly to exercise the validator.
    record = {
        "idempotency_key": "sess-1:hash-abc",
        "operation": "job_creation",
        "phase": "intent",
        "collaboration_id": "collab-1",
        "created_at": "2026-04-17T00:00:00Z",
        "repo_root": "/tmp/repo",
        # job_id missing intentionally
    }
    path.write_text(_json.dumps(record) + "\n")

    diagnostics = journal.check_health(session_id="sess-1")
    assert diagnostics.schema_violations != ()


def test_journal_rejects_job_creation_dispatched_missing_runtime_or_thread(
    tmp_path: Path,
) -> None:
    import json as _json

    from server.journal import OperationJournal

    journal = OperationJournal(tmp_path)
    path = journal._operations_path("sess-1")
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "idempotency_key": "sess-1:hash-abc",
        "operation": "job_creation",
        "phase": "dispatched",
        "collaboration_id": "collab-1",
        "created_at": "2026-04-17T00:00:00Z",
        "repo_root": "/tmp/repo",
        "job_id": "job-1",
        # runtime_id + codex_thread_id missing
    }
    path.write_text(_json.dumps(record) + "\n")

    diagnostics = journal.check_health(session_id="sess-1")
    assert diagnostics.schema_violations != ()


def test_journal_rejects_job_creation_dispatched_missing_job_id(tmp_path: Path) -> None:
    import json as _json

    from server.journal import OperationJournal

    journal = OperationJournal(tmp_path)
    path = journal._operations_path("sess-1")
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "idempotency_key": "sess-1:hash-abc",
        "operation": "job_creation",
        "phase": "dispatched",
        "collaboration_id": "collab-1",
        "created_at": "2026-04-17T00:00:00Z",
        "repo_root": "/tmp/repo",
        "runtime_id": "rt-1",
        "codex_thread_id": "thr-1",
        # job_id missing intentionally
    }
    path.write_text(_json.dumps(record) + "\n")

    diagnostics = journal.check_health(session_id="sess-1")
    assert diagnostics.schema_violations != ()


def test_approval_resolution_round_trips_as_unresolved_terminal_record(
    tmp_path: Path,
) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    journal.write_phase(
        OperationJournalEntry(
            idempotency_key="req-1:approve",
            operation="approval_resolution",
            phase="intent",
            collaboration_id="collab-1",
            created_at="2026-04-19T00:00:00Z",
            repo_root="/repo",
            job_id="job-1",
            request_id="req-1",
            decision="approve",
        ),
        session_id="sess-1",
    )

    unresolved = journal.list_unresolved(session_id="sess-1")
    assert len(unresolved) == 1
    assert unresolved[0].operation == "approval_resolution"
    assert unresolved[0].request_id == "req-1"
    assert unresolved[0].decision == "approve"


def test_check_health_reports_missing_request_id_for_approval_resolution(
    tmp_path: Path,
) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    path = journal._operations_path("sess-1")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "idempotency_key": "req-1:approve",
                "operation": "approval_resolution",
                "phase": "intent",
                "collaboration_id": "collab-1",
                "created_at": "2026-04-19T00:00:00Z",
                "repo_root": "/repo",
                "job_id": "job-1",
                "decision": "approve",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    diagnostics = journal.check_health(session_id="sess-1")
    assert len(diagnostics.schema_violations) == 1


def test_journal_accepts_promotion_operation(tmp_path: Path) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    journal.write_phase(
        OperationJournalEntry(
            idempotency_key="job-1:1",
            operation="promotion",
            phase="intent",
            collaboration_id="collab-1",
            created_at="2026-04-20T00:00:00Z",
            repo_root="/repo",
            job_id="job-1",
        ),
        session_id="sess-1",
    )
    unresolved = journal.list_unresolved(session_id="sess-1")
    assert unresolved[0].operation == "promotion"


def test_stale_marker_shape_uses_artifact_hash_and_job_id(tmp_path: Path) -> None:
    journal = OperationJournal(tmp_path / "plugin-data")
    journal.write_stale_marker(
        StaleAdvisoryContextMarker(
            repo_root=str(tmp_path.resolve()),
            promoted_artifact_hash="hash-1",
            job_id="job-1",
            recorded_at="2026-04-20T00:00:00Z",
        )
    )
    marker = journal.load_stale_marker(tmp_path)
    assert marker is not None
    assert marker.promoted_artifact_hash == "hash-1"
    assert marker.job_id == "job-1"


def test_load_stale_marker_handles_old_schema_gracefully(tmp_path: Path) -> None:
    """Old-schema markers (promoted_head, no job_id) are treated as absent.

    After the schema rename from promoted_head→promoted_artifact_hash and
    addition of job_id, persisted markers from prior sessions must not crash
    load_stale_marker with TypeError.
    """
    plugin_data = tmp_path / "plugin-data"
    plugin_data.mkdir(parents=True, exist_ok=True)
    journal = OperationJournal(plugin_data)

    # Write an old-schema marker directly to the storage file.
    journal_dir = plugin_data / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    markers_path = journal_dir / "stale_advisory_context.json"
    old_marker = {
        str(tmp_path): {
            "repo_root": str(tmp_path),
            "promoted_head": "abc123",
            "recorded_at": "2026-03-27T15:00:00Z",
        }
    }
    markers_path.write_text(json.dumps(old_marker), encoding="utf-8")

    # Should return None (not crash) and clear the stale record.
    result = journal.load_stale_marker(tmp_path)
    assert result is None

    # The old marker should be cleared from storage.
    loaded = json.loads(markers_path.read_text(encoding="utf-8"))
    assert str(tmp_path) not in loaded


def test_write_stale_marker_is_atomic(tmp_path: Path) -> None:
    """Marker writes must use temp-rename so crash mid-write cannot corrupt.

    Asserts the post-write disk state: target file present, valid JSON, no
    stray .tmp left behind. This is the durability contract recovery code
    depends on.
    """
    plugin_data = tmp_path / "plugin-data"
    journal = OperationJournal(plugin_data)
    journal.write_stale_marker(
        StaleAdvisoryContextMarker(
            repo_root=str(tmp_path.resolve()),
            promoted_artifact_hash="hash-1",
            job_id="job-1",
            recorded_at="2026-03-27T15:00:00Z",
        )
    )

    markers_path = plugin_data / "journal" / "stale_advisory_context.json"
    assert markers_path.exists()
    parsed = json.loads(markers_path.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    assert str(tmp_path.resolve()) in parsed

    tmp_marker = markers_path.with_name(markers_path.name + ".tmp")
    assert not tmp_marker.exists(), (
        f"temp file must be renamed away after atomic write; saw {tmp_marker}"
    )


def test_load_stale_marker_recovers_from_corrupt_file(tmp_path: Path) -> None:
    """A truncated/corrupt markers file must not hard-fail the advisory path.

    Reproduces the crash-mid-write failure mode from before the atomic-write
    fix: subsequent reads see invalid JSON. The fix treats this as an absent
    marker and clears the corrupt file so the next write starts fresh.
    """
    plugin_data = tmp_path / "plugin-data"
    plugin_data.mkdir(parents=True, exist_ok=True)
    journal_dir = plugin_data / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    markers_path = journal_dir / "stale_advisory_context.json"

    # Simulate crash mid-write: file truncated to a partial JSON prefix.
    markers_path.write_text('{"some-key": {"repo_root":', encoding="utf-8")

    journal = OperationJournal(plugin_data)
    result = journal.load_stale_marker(tmp_path)
    assert result is None
    assert not markers_path.exists(), (
        "corrupt marker file must be cleared so subsequent writes start fresh"
    )

    # Writing a fresh marker after corruption recovery still works.
    journal.write_stale_marker(
        StaleAdvisoryContextMarker(
            repo_root=str(tmp_path.resolve()),
            promoted_artifact_hash="hash-fresh",
            job_id="job-fresh",
            recorded_at="2026-03-27T15:00:00Z",
        )
    )
    marker = journal.load_stale_marker(tmp_path)
    assert marker is not None
    assert marker.promoted_artifact_hash == "hash-fresh"


@pytest.mark.parametrize(
    "payload",
    [
        "[]",  # valid JSON, top-level list
        '"a string"',  # valid JSON, top-level scalar
        "null",  # valid JSON, null
        "42",  # valid JSON, integer
    ],
)
def test_load_stale_marker_treats_wrong_top_level_shape_as_absent(
    tmp_path: Path, payload: str
) -> None:
    """Valid JSON with a non-dict top level is treated as ephemeral corruption.

    The F5 contract is that stale-marker corruption — however it occurred —
    must not crash recovery or advisory calls. The earlier fix only handled
    JSONDecodeError; this covers the valid-JSON-wrong-shape case.
    """
    plugin_data = tmp_path / "plugin-data"
    plugin_data.mkdir(parents=True, exist_ok=True)
    journal_dir = plugin_data / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    markers_path = journal_dir / "stale_advisory_context.json"
    markers_path.write_text(payload, encoding="utf-8")

    journal = OperationJournal(plugin_data)
    assert journal.load_stale_marker(tmp_path) is None
    assert not markers_path.exists(), (
        f"corrupt top-level payload {payload!r} must be cleared on read"
    )


def test_load_stale_marker_drops_non_dict_per_repo_record(tmp_path: Path) -> None:
    """A per-repo value that isn't a dict (e.g., int) is treated as absent."""
    plugin_data = tmp_path / "plugin-data"
    plugin_data.mkdir(parents=True, exist_ok=True)
    journal_dir = plugin_data / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    markers_path = journal_dir / "stale_advisory_context.json"
    repo_key = str(tmp_path.resolve())
    markers_path.write_text(
        json.dumps({repo_key: 42}), encoding="utf-8"
    )

    journal = OperationJournal(plugin_data)
    assert journal.load_stale_marker(tmp_path) is None

    # The corrupt entry must be dropped so subsequent reads start clean.
    loaded = json.loads(markers_path.read_text(encoding="utf-8"))
    assert repo_key not in loaded


def test_load_stale_marker_drops_record_with_invalid_fields(tmp_path: Path) -> None:
    """A per-repo dict missing required fields or carrying unknown ones is dropped.

    StaleAdvisoryContextMarker(**record) would raise TypeError; the fix
    catches it and treats the record as absent. Covers both missing
    `recorded_at` and unknown surplus keys.
    """
    plugin_data = tmp_path / "plugin-data"
    plugin_data.mkdir(parents=True, exist_ok=True)
    journal_dir = plugin_data / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    markers_path = journal_dir / "stale_advisory_context.json"
    repo_key = str(tmp_path.resolve())

    # Has the keys the schema-check looks for, but no recorded_at — the
    # dataclass constructor raises TypeError.
    markers_path.write_text(
        json.dumps(
            {
                repo_key: {
                    "repo_root": repo_key,
                    "promoted_artifact_hash": "hash-1",
                    "job_id": "job-1",
                    # recorded_at deliberately omitted
                }
            }
        ),
        encoding="utf-8",
    )

    journal = OperationJournal(plugin_data)
    assert journal.load_stale_marker(tmp_path) is None
    loaded = json.loads(markers_path.read_text(encoding="utf-8"))
    assert repo_key not in loaded


@pytest.mark.parametrize(
    "bad_record",
    [
        # Each field exists with the right key set, but the value is the
        # wrong runtime type. Dataclass constructor does not enforce types,
        # so without explicit validation these would pass through as
        # "live" markers and leak corrupt state into the advisory prompt.
        pytest.param(
            {
                "repo_root": [],
                "promoted_artifact_hash": "hash-1",
                "job_id": "job-1",
                "recorded_at": "2026-03-27T15:00:00Z",
            },
            id="repo_root_list",
        ),
        pytest.param(
            {
                "repo_root": "/repo",
                "promoted_artifact_hash": [],
                "job_id": "job-1",
                "recorded_at": "2026-03-27T15:00:00Z",
            },
            id="promoted_artifact_hash_list",
        ),
        pytest.param(
            {
                "repo_root": "/repo",
                "promoted_artifact_hash": "hash-1",
                "job_id": {},
                "recorded_at": "2026-03-27T15:00:00Z",
            },
            id="job_id_dict",
        ),
        pytest.param(
            {
                "repo_root": "/repo",
                "promoted_artifact_hash": "hash-1",
                "job_id": "job-1",
                "recorded_at": None,
            },
            id="recorded_at_null",
        ),
    ],
)
def test_load_stale_marker_drops_record_with_non_string_field_values(
    tmp_path: Path, bad_record: dict[str, object]
) -> None:
    plugin_data = tmp_path / "plugin-data"
    plugin_data.mkdir(parents=True, exist_ok=True)
    journal_dir = plugin_data / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    markers_path = journal_dir / "stale_advisory_context.json"
    repo_key = str(tmp_path.resolve())
    markers_path.write_text(json.dumps({repo_key: bad_record}), encoding="utf-8")

    journal = OperationJournal(plugin_data)
    assert journal.load_stale_marker(tmp_path) is None
    loaded = json.loads(markers_path.read_text(encoding="utf-8"))
    assert repo_key not in loaded


class TestDelegationOutcomeJournal:
    def test_append_delegation_outcome_writes_to_outcomes_jsonl(
        self, tmp_path: Path
    ) -> None:
        journal = OperationJournal(tmp_path / "data")
        record = DelegationOutcomeRecord(
            outcome_id="do-1",
            timestamp="2026-04-21T00:00:00Z",
            outcome_type="delegation_terminal",
            collaboration_id="collab-1",
            runtime_id="rt-1",
            job_id="job-1",
            terminal_status="completed",
            base_commit="abc123",
            repo_root="/tmp/repo",
        )
        journal.append_delegation_outcome(record)

        outcomes_path = tmp_path / "data" / "analytics" / "outcomes.jsonl"
        assert outcomes_path.exists()
        line = json.loads(outcomes_path.read_text(encoding="utf-8").strip())
        assert line["outcome_type"] == "delegation_terminal"
        assert line["job_id"] == "job-1"
        assert line["terminal_status"] == "completed"

    def test_append_delegation_outcome_once_skips_duplicate(
        self, tmp_path: Path
    ) -> None:
        journal = OperationJournal(tmp_path / "data")
        record = DelegationOutcomeRecord(
            outcome_id="do-1",
            timestamp="2026-04-21T00:00:00Z",
            outcome_type="delegation_terminal",
            collaboration_id="collab-1",
            runtime_id="rt-1",
            job_id="job-1",
            terminal_status="completed",
            base_commit="abc123",
        )
        journal.append_delegation_outcome_once(record)
        journal.append_delegation_outcome_once(record)

        outcomes_path = tmp_path / "data" / "analytics" / "outcomes.jsonl"
        lines = outcomes_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1

    def test_append_delegation_outcome_once_allows_different_jobs(
        self, tmp_path: Path
    ) -> None:
        journal = OperationJournal(tmp_path / "data")
        for jid in ("job-1", "job-2"):
            journal.append_delegation_outcome_once(
                DelegationOutcomeRecord(
                    outcome_id=f"do-{jid}",
                    timestamp="2026-04-21T00:00:00Z",
                    outcome_type="delegation_terminal",
                    collaboration_id=f"collab-{jid}",
                    runtime_id="rt-1",
                    job_id=jid,
                    terminal_status="completed",
                    base_commit="abc123",
                )
            )

        outcomes_path = tmp_path / "data" / "analytics" / "outcomes.jsonl"
        lines = outcomes_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2

    def test_delegation_and_advisory_outcomes_coexist(self, tmp_path: Path) -> None:
        journal = OperationJournal(tmp_path / "data")
        journal.append_outcome(
            OutcomeRecord(
                outcome_id="o-1",
                timestamp="2026-04-21T00:00:00Z",
                outcome_type="consult",
                collaboration_id="collab-1",
                runtime_id="rt-1",
                context_size=4096,
                turn_id="turn-1",
            )
        )
        journal.append_delegation_outcome(
            DelegationOutcomeRecord(
                outcome_id="do-1",
                timestamp="2026-04-21T00:00:00Z",
                outcome_type="delegation_terminal",
                collaboration_id="collab-2",
                runtime_id="rt-1",
                job_id="job-1",
                terminal_status="completed",
                base_commit="abc123",
            )
        )

        outcomes_path = tmp_path / "data" / "analytics" / "outcomes.jsonl"
        lines = outcomes_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        records = [json.loads(line) for line in lines]
        types = {r["outcome_type"] for r in records}
        assert types == {"consult", "delegation_terminal"}
