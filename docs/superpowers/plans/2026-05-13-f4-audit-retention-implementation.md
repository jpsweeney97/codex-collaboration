# F4 Audit Retention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement F4 audit/outcome retention and dedup replacement exactly as specified by `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md` at `HEAD=977b962`.

**Architecture:** `OperationJournal` owns startup pruning, UTF-8 quarantine, and in-memory dedup seen-sets for `audit/events.jsonl` and `analytics/outcomes.jsonl`. `scripts/codex_runtime_bootstrap.py` invokes pruning once after journal construction and reports summary diagnostics. Owner specs and the analytics skill are updated so readers understand that audit and outcome streams are 30-day operational diagnostics, not unbounded history.

**Tech Stack:** Python 3.11+, pytest, ruff, JSONL files, pathlib, dataclasses, Python logging.

---

## Current Anchors

- Repo: `/Users/jp/Projects/active/codex-collaboration`
- Current branch at plan creation: `main...origin/main [ahead 25]`
- Current HEAD at plan creation: `977b962 docs(design): add analytics.py to F4 consumer-doc update scope`
- Design authority: `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md`
- Boundary: F4 only. Do not implement F12 reserved `crash` / `restart` audit events.

## Hard Assumptions

These assumptions are inherited from the design (`HEAD=977b962`) and are not defended by this plan. Implementation pressure that would erode them is out of scope and triggers a stop condition.

- **Single-writer per `${CLAUDE_PLUGIN_DATA}` root.** Exactly one MCP server process owns the prune writer for `events.jsonl` and `outcomes.jsonl` at a time. Multi-session / path-aliased deployments are unsupported. Do not add advisory locks, file locks, or `multiprocessing` primitives in this slice to defend the envelope - that is design Section 2 trade-off territory, not implementation work.
- **Python 3.11+ runtime.** `datetime.fromisoformat` handles the `Z` form natively; the strict parser in `_parse_aware_iso8601` depends on this. Older runtimes are not targeted.
- **Stdio MCP server lifecycle.** The bootstrap runs once per Claude Code session and exits with the session. Same-session expiry (records becoming TTL-eligible mid-session) is not a v1 concern - periodic-during-session pruning is explicitly future scope.

## Carry-Forward Checklist

Items handed from rounds 7-10 of the design adversarial review to this implementation plan. Each is addressed before invoking `superpowers:subagent-driven-development`.

- [x] **(a) Mutable-clock fixture pattern (round-7 Section 6.4).** A `_mutable_clock(at: list[datetime])` helper is added in Task 1 Step 1 alongside `_fixed_clock`. The Section 8.6 second-prune eviction test in Task 2 uses it to advance time between prune calls.
- [x] **(b) String-typed timestamp generation (round-7 Section 6.4).** Test helpers `_audit_event`, `_dialogue_outcome`, `_delegation_outcome` accept `timestamp: str` with literal Z-form defaults. Fixtures do not call `journal.timestamp()`.
- [x] **(c) Section 9 manual review-gate as process item, not CI (round-7 F5).** Task 9 Step 5 runs `rg "glob|rglob|iterdir|scandir|listdir"` as a manual reader-classification step, not a structural grep gate.
- [x] **(d) Single-writer / no-lock envelope as visible hard assumption (round-8 F4).** Surfaced as the first Hard Assumption above and as a Stop Condition below. Not deferred to the Completion Report.
- [x] **(e) Consumer-doc updates for `decisions.md`, `SKILL.md`, `analytics.py` (rounds 8-9 F2).** Task 6 covers the spec docs; Task 7 covers the analytics skill and script.
- [x] **(f) Analytics timestamp-range semantics (round-10 F4).** Task 7's `_timestamp_range` filters via `_parse_aware_iso8601` (parseable timezone-aware only), reports a missing-or-malformed count, and per-file ranges (audit and outcomes reported independently). Test fixture includes a malformed-timestamp record.

## Files And Responsibilities

- Modify `server/journal.py`
  - Add `_AUDIT_TTL_DAYS`, `PruneSummary`, `_PruneFileStats`, clock seam, timestamp parser, prune pass, quarantine helper, per-file seen-set flags, and append-once set membership.
  - Remove production use of `_jsonl_contains`.
- Modify `scripts/codex_runtime_bootstrap.py`
  - Add module logger.
  - Call `journal.prune_audit_logs()` immediately after `OperationJournal` construction.
  - Catch `OSError` only and log successful summaries at `INFO` or `WARNING` depending on malformed/quarantine counts.
- Modify `docs/specs/recovery-and-journal.md`
  - Add operational outcomes owner-spec text.
  - Update audit/outcome retention, quarantine, UTF-8, LF-only, per-file atomicity, and retention-default trigger wording.
- Modify `docs/specs/decisions.md`
  - Clarify that `analytics/outcomes.jsonl` and `audit/events.jsonl` are retention-window sources after F4.
- Modify `skills/codex-analytics/SKILL.md`
  - Replace append-only/unbounded history language with 30-day operational-window language.
  - Document that `*.corrupt-*` siblings are forensic inputs, not live analytics sources.
- Modify `skills/codex-analytics/scripts/analytics.py`
  - Label counts as retention-window counts.
  - Include observed timestamp range for outcomes and audit records.
- Modify `tests/test_journal.py`
  - Add journal retention, quarantine, seen-set, and append-once tests.
- Modify `tests/test_bootstrap.py`
  - Add bootstrap prune/logging tests using the existing importlib loader.
- Modify `tests/test_analytics_skill.py`
  - Add assertions for retention-window count labels and observed timestamp ranges.

## Stop Conditions

- Stop if live `HEAD` is no longer the design state this plan targets and the design doc changed materially. Re-read the design before continuing.
- Stop if implementation pressure starts pulling in F12 `crash` / `restart` emission semantics.
- Stop if a proposed fix broadens dialogue exception handling to hide journal failures. F4 handles UTF-8 corruption inside journal read paths, not by swallowing finalization failures.
- Stop if an `OSError` from quarantine rename is being swallowed. Rename failure is an IO-class failure.
- Stop if implementation pressure introduces a file lock, advisory lock, or `multiprocessing` primitive to defend the prune writer. The single-writer envelope is the design-level assumption; defending it inside F4 is out of scope.
- Stop if final grep gates do not match the design's expected structural shape.

---

### Task 0: Preflight And Branch Boundary

**Files:**
- Read: `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md`
- Read: `server/journal.py`
- Read: `scripts/codex_runtime_bootstrap.py`
- Read: `tests/test_journal.py`
- Read: `tests/test_bootstrap.py`

- [ ] **Step 1: Re-anchor on live state**

Run:

```bash
git status --short --branch
git rev-parse --short HEAD
git log --oneline -8
```

Expected:

```text
Branch is based on the current local F4 design stack.
HEAD is at or intentionally supersedes 977b962.
No unexpected worktree changes in files this plan will touch.
```

- [ ] **Step 2: Create an implementation branch if still on main**

Run only if currently on `main`. The script picks the next free numeric suffix if `fix/f4-audit-retention` is already taken so a second-attempt run does not fail mid-Task-0:

```bash
branch="fix/f4-audit-retention"
if git show-ref --verify --quiet "refs/heads/$branch"; then
    n=2
    while git show-ref --verify --quiet "refs/heads/$branch-$n"; do
        n=$((n+1))
    done
    branch="$branch-$n"
fi
git switch -c "$branch"
```

Expected:

```text
Switched to a new branch 'fix/f4-audit-retention' (or fix/f4-audit-retention-2, etc.)
```

Do not commit directly to `main`.

- [ ] **Step 3: Confirm baseline targeted tests**

Run:

```bash
uv run pytest tests/test_journal.py tests/test_bootstrap.py tests/test_analytics_skill.py -q
```

Expected:

```text
All selected baseline tests pass before edits.
```

If this fails before edits, stop and classify baseline failure separately from F4 implementation.

---

### Task 1: Add Journal Retention Test Helpers And Clock-Seam Tests

**Files:**
- Modify: `tests/test_journal.py`
- Modify later: `server/journal.py`

- [ ] **Step 1: Add imports and local test helpers**

In `tests/test_journal.py`, extend imports:

```python
from datetime import UTC, datetime, timedelta
from typing import Any, Callable
```

Add helpers after `_make_intent`:

```python
def _fixed_clock(at: datetime) -> Callable[[], datetime]:
    return lambda: at


def _mutable_clock(at: list[datetime]) -> Callable[[], datetime]:
    """One-element list container so tests can advance the clock between
    `prune_audit_logs()` calls without rebuilding the journal.

    Usage:
        clock_state = [t0]
        journal = OperationJournal(..., clock=_mutable_clock(clock_state))
        journal.prune_audit_logs()
        clock_state[0] = t1
        journal.prune_audit_logs()  # uses t1 as cutoff anchor
    """
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
```

If mypy or ruff rejects `outcome_type: str` for `OutcomeRecord`, narrow that helper parameter to the literal-compatible values needed by tests.

- [ ] **Step 2: Write failing clock seam tests**

Add:

```python
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
```

- [ ] **Step 3: Run the new tests and verify failure**

Run:

```bash
uv run pytest tests/test_journal.py::TestAuditRetentionClock -q
```

Expected:

```text
FAIL because OperationJournal does not accept clock and prune_audit_logs is missing.
```

- [ ] **Step 4: Implement minimal clock seam and summary types**

In `server/journal.py`, update imports:

```python
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
```

Add near module constants:

```python
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
```

Add helper:

```python
def _coerce_aware_utc(value: datetime, *, source: str) -> datetime:
    """Validate timezone-aware datetimes and normalize them to UTC."""

    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError(f"{source} requires a timezone-aware datetime. Got: {value!r}")
    return value.astimezone(UTC)
```

Change the constructor signature and initialize the clock plus per-file flags:

```python
def __init__(
    self,
    plugin_data_path: Path | None = None,
    *,
    clock: Callable[[], datetime] | None = None,
) -> None:
    self._plugin_data_path = plugin_data_path or default_plugin_data_path()
    self._clock = clock or (lambda: datetime.now(UTC))
    ...
    self._audit_seen_initialized = False
    self._outcomes_seen_initialized = False
    self._audit_seen: set[_AuditDedupKey] = set()
    self._dialogue_outcomes_seen: set[_DialogueOutcomeDedupKey] = set()
    self._delegation_outcomes_seen: set[_DelegationOutcomeDedupKey] = set()
```

Replace `timestamp()` with:

```python
def _now(self) -> datetime:
    """Current time per the injected clock."""

    return _coerce_aware_utc(self._clock(), source="Journal clock")


def timestamp(self) -> str:
    """Return the current UTC timestamp as ISO 8601."""

    return self._now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
```

Add a temporary `prune_audit_logs()` that only computes `now` and returns zero counts. This makes the naive-clock test pass and will be replaced in Task 2:

```python
def prune_audit_logs(self) -> PruneSummary:
    self._now()
    return PruneSummary(0, 0, 0, 0, 0, 0)
```

- [ ] **Step 5: Run the clock tests**

Run:

```bash
uv run pytest tests/test_journal.py::TestAuditRetentionClock -q
```

Expected:

```text
PASS
```

- [ ] **Step 6: Commit Task 1**

Run:

```bash
git add server/journal.py tests/test_journal.py
git commit -m "fix(journal): add retention clock seam"
```

---

### Task 2: Implement Pruning, Raw-Line Retention, And Atomic Rewrite

**Files:**
- Modify: `tests/test_journal.py`
- Modify: `server/journal.py`

- [ ] **Step 1: Add happy-path prune tests**

Add:

```python
class TestAuditRetentionPruning:
    def test_prune_audit_logs_drops_records_older_than_ttl(self, tmp_path: Path) -> None:
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

    def test_prune_audit_logs_retains_records_within_ttl(self, tmp_path: Path) -> None:
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
        """Pins the contract `if ts < cutoff` (strict less-than) against an
        accidental `<=` inversion. A record dated exactly `now - 30 days`
        must be RETAINED.
        """
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
        """File exists with zero bytes - distinct from missing-file edge case
        (handled by the `if not path.exists()` short-circuit in _prune_jsonl_pass).
        """
        now = datetime(2026, 5, 12, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        audit_path.parent.mkdir(parents=True)
        audit_path.write_text("", encoding="utf-8")
        outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
        outcomes_path.parent.mkdir(parents=True)
        outcomes_path.write_text("", encoding="utf-8")

        summary = journal.prune_audit_logs()

        assert summary == PruneSummary(0, 0, 0, 0, 0, 0)
        assert audit_path.read_text(encoding="utf-8") == ""
        assert outcomes_path.read_text(encoding="utf-8") == ""

    def test_prune_audit_logs_normalizes_non_utc_aware_timestamps(
        self, tmp_path: Path
    ) -> None:
        """Two records flip classification under naive-lexical / strip-tz
        comparison vs correct UTC normalization. Pins design Section 5.4
        parser semantics: the strict comparison must happen in UTC.

        Cutoff is 2026-04-12T00:00:00Z (now - 30 days).

        Record A: local "2026-04-11T20:00:00-05:00" == UTC 2026-04-12T01:00:00Z
          - Correct (UTC compare):     01:00 > cutoff -> RETAIN.
          - Buggy (strip-tz or lex):   "2026-04-11..." < "2026-04-12..." -> DROP.

        Record B: local "2026-04-12T08:59:59+09:00" == UTC 2026-04-11T23:59:59Z
          - Correct (UTC compare):     04-11 < cutoff -> DROP.
          - Buggy (strip-tz or lex):   "2026-04-12T08..." > "2026-04-12T00..." -> RETAIN.

        A correct implementation produces {retained=1, dropped=1, kept=A}.
        Any buggy implementation produces {retained=1, dropped=1, kept=B},
        which the assertion catches.
        """
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
```

Add `PruneSummary` to the existing `from server.journal import ...` import.

- [ ] **Step 2: Add retain-on-uncertainty and line-format tests**

Add:

```python
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
    """A line that fails json.loads is retained as raw bytes (no re-serialize)
    and counted as retained_malformed. Pins Section 5.3 retain-on-uncertainty for the
    "Not valid JSON" row.
    """
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.parent.mkdir(parents=True)
    audit_path.write_text("{not-valid-json\n", encoding="utf-8")

    summary = journal.prune_audit_logs()

    assert audit_path.read_text(encoding="utf-8") == "{not-valid-json\n"
    assert summary.audit_retained == 1
    assert summary.audit_retained_malformed == 1
    assert summary.audit_dropped == 0


def test_prune_audit_logs_retains_non_dict_record(tmp_path: Path) -> None:
    """Valid JSON but not a dict (array or scalar) - retained as raw line,
    counted as retained_malformed. Pins Section 5.3 retain-on-uncertainty for the
    "Valid JSON but not a dict" row.
    """
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.parent.mkdir(parents=True)
    audit_path.write_text('[1, 2, 3]\n"a-bare-string"\n42\n', encoding="utf-8")

    summary = journal.prune_audit_logs()

    assert audit_path.read_text(encoding="utf-8") == '[1, 2, 3]\n"a-bare-string"\n42\n'
    assert summary.audit_retained == 3
    assert summary.audit_retained_malformed == 3
    assert summary.audit_dropped == 0


def test_prune_audit_logs_drops_blank_lines(tmp_path: Path) -> None:
    """Blank lines are not records and are dropped on rewrite. Not counted
    as retained or dropped (per Section 5.3 table: "neither").
    """
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.parent.mkdir(parents=True)
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
    # Blank-line drops are NOT counted in dropped (which is reserved for
    # TTL expiry).
    assert summary.audit_retained == 2
    assert summary.audit_dropped == 0
    # Result file must contain exactly 2 lines (the 2 records), no blanks.
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
```

- [ ] **Step 3: Add atomic replacement and re-runnable prune tests**

Add:

```python
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
```

Add `import os` to `tests/test_journal.py`.

Then add re-runnable prune tests. These exercise the mutable-clock fixture pattern (carry-forward (a)) and per-file flag lifecycle from design Section 6.3 / Section 5.6. They are module-level (not in a class) to match the existing module-level retain-on-uncertainty tests:

```python
def test_prune_audit_logs_evicts_newly_expired_keys_on_second_run(
    tmp_path: Path,
) -> None:
    """Mutable-clock fixture pattern (carry-forward (a)). Record A at T0 is
    retained on first prune; advance the clock past TTL; prune again; A is
    dropped AND removed from the in-memory dedup set, so a third append-once
    with A's key would write again.
    """
    t0 = datetime(2026, 5, 12, tzinfo=UTC)
    clock_state = [t0]
    journal = OperationJournal(
        tmp_path / "plugin-data", clock=_mutable_clock(clock_state)
    )
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    a_ts = "2026-04-13T00:00:00Z"  # 29 days before t0 - inside window
    journal.append_audit_event(_audit_event(event_id="A", timestamp=a_ts))

    summary1 = journal.prune_audit_logs()
    assert summary1.audit_retained == 1
    assert ("dialogue_turn", "collab-1", "turn-1") in journal._audit_seen

    # Advance to t1 = t0 + 31 days. A's timestamp (2026-04-13) is now > 30
    # days old relative to t1 (2026-06-12) and must be dropped.
    clock_state[0] = t0 + timedelta(days=31)

    summary2 = journal.prune_audit_logs()
    assert summary2.audit_retained == 0
    assert summary2.audit_dropped == 1
    assert _read_jsonl(audit_path) == []
    assert ("dialogue_turn", "collab-1", "turn-1") not in journal._audit_seen


def test_prune_audit_logs_restores_per_file_flag_after_each_pass(
    tmp_path: Path,
) -> None:
    """Successful prune restores both per-file flags to True. Pins Section 5.6:
    each flag is restored independently after its file's atomic seen-set
    reassignment.
    """
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
    """Audit pass succeeds; outcomes pass raises OSError mid-pass on the
    second run. Audit flag stays True (audit pass committed); outcomes flag
    stays False (cleared at entry, never restored). Pins round-4 PA F1
    per-file flag invalidation discipline (Section 5.6).
    """
    now = datetime(2026, 5, 12, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    journal.append_audit_event(_audit_event(timestamp="2026-05-01T00:00:00Z"))
    journal.append_outcome(_dialogue_outcome(timestamp="2026-05-01T00:00:00Z"))

    # First prune is clean - both flags become True.
    journal.prune_audit_logs()
    assert journal._audit_seen_initialized is True
    assert journal._outcomes_seen_initialized is True

    # Patch _prune_jsonl_pass to fail when called for outcomes_path on the
    # second run. Audit pass still succeeds.
    real_pass = journal._prune_jsonl_pass

    def selective_fail(*, path: Path, cutoff: datetime, populate):
        if path == journal._outcomes_path:
            raise OSError("outcomes prune failed")
        return real_pass(path=path, cutoff=cutoff, populate=populate)

    monkeypatch.setattr(journal, "_prune_jsonl_pass", selective_fail)

    with pytest.raises(OSError, match="outcomes prune failed"):
        journal.prune_audit_logs()

    assert journal._audit_seen_initialized is True
    assert journal._outcomes_seen_initialized is False
```

- [ ] **Step 4: Run the new prune tests and verify failure**

Run (the `-k` filter catches every Step 1-3 test name pattern - class methods and module-level alike - without listing each one):

```bash
uv run pytest tests/test_journal.py -k "prune_audit_logs" -q
```

Expected:

```text
FAIL because prune_audit_logs still returns zero counts and does not rewrite files.
```

- [ ] **Step 5: Implement timestamp parsing, prune pass, and orchestration**

In `server/journal.py`, add:

```python
def _parse_aware_iso8601(value: Any) -> datetime | None:
    """Return a timezone-aware UTC datetime, or None on any failure."""

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

Add private population stubs now; Task 3 will make their effects observable:

```python
def _populate_from_audit_record(
    record: dict[str, Any],
    audit_seen: set[_AuditDedupKey],
) -> None:
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

Add to `OperationJournal`:

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

            ts = _parse_aware_iso8601(record.get("timestamp"))
            if ts is None:
                retained_count += 1
                retained_malformed_count += 1
                retained_lines.append(line_to_keep)
                populate(record)
                continue

            if ts < cutoff:
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
```

Replace the temporary `prune_audit_logs()` with:

```python
def prune_audit_logs(self) -> PruneSummary:
    now = self._now()
    cutoff = now - timedelta(days=_AUDIT_TTL_DAYS)

    self._audit_seen_initialized = False
    self._outcomes_seen_initialized = False

    new_audit_seen: set[_AuditDedupKey] = set()
    new_dialogue_outcomes_seen: set[_DialogueOutcomeDedupKey] = set()
    new_delegation_outcomes_seen: set[_DelegationOutcomeDedupKey] = set()

    audit_stats = self._prune_jsonl_pass(
        path=self._audit_path,
        cutoff=cutoff,
        populate=lambda record: _populate_from_audit_record(record, new_audit_seen),
    )
    self._audit_seen = new_audit_seen
    self._audit_seen_initialized = True

    outcomes_stats = self._prune_jsonl_pass(
        path=self._outcomes_path,
        cutoff=cutoff,
        populate=lambda record: _populate_from_outcome_record(
            record,
            new_dialogue_outcomes_seen,
            new_delegation_outcomes_seen,
        ),
    )
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
    )
```

This is not final because UTF-8 quarantine is added in Task 4.

- [ ] **Step 6: Pin append writers to LF-only**

Change these three opens in `server/journal.py`:

```python
with self._audit_path.open("a", encoding="utf-8", newline="\n") as handle:
...
with self._outcomes_path.open("a", encoding="utf-8", newline="\n") as handle:
...
with self._outcomes_path.open("a", encoding="utf-8", newline="\n") as handle:
```

Do not change operation-journal `write_phase()` or marker writes in this task; the F4 LF-only contract is specifically for audit/outcome JSONL surfaces plus the prune temp-file write.

- [ ] **Step 7: Run Task 2 tests**

Run (Clock class + every `prune_audit_logs` test name):

```bash
uv run pytest tests/test_journal.py -k "TestAuditRetentionClock or prune_audit_logs" -q
```

Expected:

```text
PASS
```

- [ ] **Step 8: Commit Task 2**

Run:

```bash
git add server/journal.py tests/test_journal.py
git commit -m "fix(journal): prune audit and outcome logs"
```

---

### Task 3: Replace Linear Dedup With Per-File Seen Sets

**Files:**
- Modify: `tests/test_journal.py`
- Modify: `server/journal.py`

- [ ] **Step 1: Add tests for direct-construction seen-set loading**

Add:

```python
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
        """Direct dedup-skip pin (Section 5.8). Pre-populates the seen-set, then
        monkeypatches `append_audit_event` to fail loudly - confirms the
        underlying IO is NEVER called when the key is already known.
        """
        journal = OperationJournal(tmp_path / "plugin-data")
        event = _audit_event()
        journal._audit_seen = {(event.action, event.collaboration_id, event.turn_id)}
        journal._audit_seen_initialized = True

        def must_not_be_called(event: AuditEvent) -> None:
            raise AssertionError("append_audit_event called despite seen-set hit")

        monkeypatch.setattr(journal, "append_audit_event", must_not_be_called)

        journal.append_dialogue_audit_event_once(event)  # must not raise

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
```

- [ ] **Step 2: Add tests for failure isolation and update-after-success**

Add:

```python
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

    def fail_outcomes_only(path: Path, on_record: Callable[[dict[str, Any]], None]) -> None:
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
    """A line-local malformed JSON line in events.jsonl does NOT block
    seen-set population. Pins Section 5.7 read-path tolerance - the legacy
    `_jsonl_contains` did this too.
    """
    journal = OperationJournal(tmp_path / "plugin-data")
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.parent.mkdir(parents=True)
    initial_content = (
        '{not-valid-json\n'
        '{"event_id":"valid","timestamp":"2026-05-01T00:00:00Z",'
        '"actor":"claude","action":"dialogue_turn",'
        '"collaboration_id":"collab-1","runtime_id":"rt-1",'
        '"turn_id":"turn-1"}\n'
    )
    audit_path.write_text(initial_content, encoding="utf-8")

    journal.append_dialogue_audit_event_once(
        _audit_event(event_id="duplicate")  # same dedup key as the valid line
    )

    # The corrupt line was skipped during populate; the valid line populated
    # the seen-set; the new event was deduped (file content unchanged - no
    # new line appended). Cannot use `_read_jsonl` here because it is strict
    # and the malformed line on disk would raise JSONDecodeError; instead
    # assert the raw file is byte-equal to the input.
    assert audit_path.read_text(encoding="utf-8") == initial_content
    assert journal._audit_seen_initialized is True


def test_ensure_outcomes_seen_loaded_tolerates_corrupt_jsonl_line(
    tmp_path: Path,
) -> None:
    """Mirror for outcomes.jsonl - line-local malformed JSON tolerated."""
    journal = OperationJournal(tmp_path / "plugin-data")
    outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
    outcomes_path.parent.mkdir(parents=True)
    initial_content = (
        '{not-valid-json\n'
        '{"outcome_id":"valid","timestamp":"2026-05-01T00:00:00Z",'
        '"outcome_type":"dialogue_turn","collaboration_id":"collab-1",'
        '"runtime_id":"rt-1","context_size":1024,"turn_id":"turn-1",'
        '"turn_sequence":1}\n'
    )
    outcomes_path.write_text(initial_content, encoding="utf-8")

    journal.append_dialogue_outcome_once(_dialogue_outcome(outcome_id="duplicate"))

    # `_read_jsonl` is strict; assert raw file content instead so the
    # corrupt line does not raise during the assertion.
    assert outcomes_path.read_text(encoding="utf-8") == initial_content
    assert journal._outcomes_seen_initialized is True


def test_ensure_audit_seen_loaded_does_not_mark_initialized_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Non-UTF-8 exception (e.g., OSError) in the populate path leaves the
    audit flag False so the next append-once retries. Outcomes flag is
    untouched. Pins Section 5.7 retry semantics - distinct from the UTF-8
    quarantine path which DOES flip the flag to True (Task 4).
    """
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
    assert journal._outcomes_seen_initialized is False  # never attempted

    # Second call retries - succeeds.
    journal.append_dialogue_audit_event_once(_audit_event())
    assert journal._audit_seen_initialized is True


def test_ensure_outcomes_seen_loaded_does_not_mark_initialized_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mirror for outcomes flag. Audit flag remains unaffected."""
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
    assert journal._audit_seen_initialized is False  # never attempted

    journal.append_dialogue_outcome_once(_dialogue_outcome())
    assert journal._outcomes_seen_initialized is True
```

If direct private-field assertions are rejected during review, keep the tests but assert public disk behavior plus targeted monkeypatch call counts.

- [ ] **Step 3: Run seen-set tests and verify failure**

Run (the `-k` filter catches the class + the four `_ensure_*` resilience tests + the two append-once isolation tests):

```bash
uv run pytest tests/test_journal.py -k "TestAuditRetentionSeenSets or test_ensure_ or test_append_dialogue_audit_event_once_updates or test_unreadable_outcomes" -q
```

Expected:

```text
FAIL while append-once still uses _jsonl_contains and _populate_seen_from_file is missing.
```

- [ ] **Step 4: Implement read-only seen-set population**

Add to `OperationJournal`:

```python
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
    self._populate_seen_from_file(
        self._audit_path,
        lambda record: _populate_from_audit_record(record, new_audit_seen),
    )
    self._audit_seen = new_audit_seen
    self._audit_seen_initialized = True


def _ensure_outcomes_seen_loaded(self) -> None:
    if self._outcomes_seen_initialized:
        return

    new_dialogue_outcomes_seen: set[_DialogueOutcomeDedupKey] = set()
    new_delegation_outcomes_seen: set[_DelegationOutcomeDedupKey] = set()
    self._populate_seen_from_file(
        self._outcomes_path,
        lambda record: _populate_from_outcome_record(
            record,
            new_dialogue_outcomes_seen,
            new_delegation_outcomes_seen,
        ),
    )
    self._dialogue_outcomes_seen = new_dialogue_outcomes_seen
    self._delegation_outcomes_seen = new_delegation_outcomes_seen
    self._outcomes_seen_initialized = True
```

Task 4 will add UTF-8 quarantine handling to both `_ensure_*` methods.

- [ ] **Step 5: Replace append-once implementations**

Replace the three append-once methods:

```python
def append_dialogue_audit_event_once(self, event: AuditEvent) -> None:
    """Append a dialogue audit event unless the logical record already exists."""

    self._ensure_audit_seen_loaded()
    key: _AuditDedupKey = (event.action, event.collaboration_id, event.turn_id)
    if key in self._audit_seen:
        return
    self.append_audit_event(event)
    self._audit_seen.add(key)


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


def append_delegation_outcome_once(self, record: DelegationOutcomeRecord) -> None:
    """Append a delegation outcome unless one exists for this job."""

    self._ensure_outcomes_seen_loaded()
    key: _DelegationOutcomeDedupKey = (record.outcome_type, record.job_id)
    if key in self._delegation_outcomes_seen:
        return
    self.append_delegation_outcome(record)
    self._delegation_outcomes_seen.add(key)
```

- [ ] **Step 6: Remove `_jsonl_contains` after tests pass**

Run (legacy classes + Task 3 additions):

```bash
uv run pytest tests/test_journal.py -k "TestDialogueReplaySafeAppends or TestDelegationOutcomeJournal or TestAuditRetentionSeenSets or test_ensure_ or test_append_dialogue_audit_event_once_updates or test_unreadable_outcomes" -q
```

Expected:

```text
PASS
```

Then delete `_jsonl_contains` from `server/journal.py` and remove unused `Callable` only if no other code in the file uses it. It will still be used by the clock seam and helpers, so it should remain.

- [ ] **Step 7: Structural check for production `_jsonl_contains`**

Run:

```bash
rg "_jsonl_contains" server/ scripts/
```

Expected:

```text
No output.
```

- [ ] **Step 8: Commit Task 3**

Run:

```bash
git add server/journal.py tests/test_journal.py
git commit -m "fix(journal): replace audit dedup scans"
```

---

### Task 4: Add UTF-8 Quarantine At Startup And Runtime Read Paths

**Files:**
- Modify: `tests/test_journal.py`
- Modify: `server/journal.py`

- [ ] **Step 1: Add quarantine tests for startup prune**

Add:

```python
class TestAuditRetentionQuarantine:
    def test_prune_audit_logs_quarantines_audit_on_invalid_utf8(
        self, tmp_path: Path
    ) -> None:
        now = datetime(2026, 5, 12, 19, 37, 15, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        audit_path.write_bytes(
            (
                '{"event_id":"pre-corrupt","timestamp":"2026-05-01T00:00:00Z",'
                '"actor":"claude","action":"dialogue_turn",'
                '"collaboration_id":"collab-1","runtime_id":"rt-1",'
                '"turn_id":"turn-1"}\n'
            ).encode("utf-8")
            + b"\x80abc\n"
        )

        summary = journal.prune_audit_logs()

        quarantine_path = audit_path.with_name(
            "events.corrupt-20260512T193715Z.jsonl"
        )
        assert not audit_path.exists()
        assert quarantine_path.read_bytes().endswith(b"\x80abc\n")
        assert summary.audit_quarantined_to == quarantine_path
        assert journal._audit_seen == set()
        assert journal._audit_seen_initialized is True

    def test_prune_audit_logs_quarantines_only_affected_file(
        self, tmp_path: Path
    ) -> None:
        now = datetime(2026, 5, 12, 19, 37, 15, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
        audit_path.write_bytes(b"\x80abc\n")
        journal.append_outcome(_dialogue_outcome(outcome_id="kept"))

        summary = journal.prune_audit_logs()

        assert summary.audit_quarantined_to is not None
        assert summary.outcomes_quarantined_to is None
        assert [record["outcome_id"] for record in _read_jsonl(outcomes_path)] == [
            "kept"
        ]

    def test_quarantine_uses_deterministic_suffix_on_target_collision(
        self, tmp_path: Path
    ) -> None:
        now = datetime(2026, 5, 12, 19, 37, 15, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        first_collision = audit_path.with_name("events.corrupt-20260512T193715Z.jsonl")
        second_collision = audit_path.with_name(
            "events.corrupt-20260512T193715Z.1.jsonl"
        )
        first_collision.write_text("occupied\n", encoding="utf-8")
        second_collision.write_text("occupied\n", encoding="utf-8")
        audit_path.write_bytes(b"\x80abc\n")

        summary = journal.prune_audit_logs()

        assert summary.audit_quarantined_to == audit_path.with_name(
            "events.corrupt-20260512T193715Z.2.jsonl"
        )

    def test_quarantine_rename_oserror_propagates_as_oserror(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        now = datetime(2026, 5, 12, 19, 37, 15, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
        audit_path.write_bytes(b"\x80abc\n")

        def fail_rename(self: Path, target: Path) -> Path:
            raise OSError("rename failed")

        monkeypatch.setattr(Path, "rename", fail_rename)

        with pytest.raises(OSError, match="rename failed"):
            journal.prune_audit_logs()

    def test_prune_audit_logs_quarantines_outcomes_on_invalid_utf8(
        self, tmp_path: Path
    ) -> None:
        """Mirror of the audit version, but exercising `outcomes.jsonl` so
        `summary.outcomes_quarantined_to` is independently pinned. Same
        partial-population scenario (valid records before the bad byte) -
        the post-quarantine in-memory outcomes sets must be empty.
        """
        now = datetime(2026, 5, 12, 19, 37, 15, tzinfo=UTC)
        journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
        outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
        outcomes_path.parent.mkdir(parents=True)
        outcomes_path.write_bytes(
            (
                '{"outcome_id":"pre-corrupt","timestamp":"2026-05-01T00:00:00Z",'
                '"outcome_type":"dialogue_turn","collaboration_id":"collab-1",'
                '"runtime_id":"rt-1","context_size":1024,"turn_id":"turn-1",'
                '"turn_sequence":1}\n'
            ).encode("utf-8")
            + b"\x80abc\n"
        )

        summary = journal.prune_audit_logs()

        quarantine_path = outcomes_path.with_name(
            "outcomes.corrupt-20260512T193715Z.jsonl"
        )
        assert not outcomes_path.exists()
        assert quarantine_path.read_bytes().endswith(b"\x80abc\n")
        assert summary.outcomes_quarantined_to == quarantine_path
        assert summary.audit_quarantined_to is None
        assert journal._dialogue_outcomes_seen == set()
        assert journal._delegation_outcomes_seen == set()
        assert journal._outcomes_seen_initialized is True
```

- [ ] **Step 2: Add quarantine tests for runtime `_ensure_*` paths**

Add:

```python
def test_ensure_audit_seen_loaded_quarantines_on_invalid_utf8(
    tmp_path: Path,
) -> None:
    now = datetime(2026, 5, 12, 19, 37, 15, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.write_bytes(
        (
            '{"event_id":"ghost","timestamp":"2026-05-01T00:00:00Z",'
            '"actor":"claude","action":"dialogue_turn",'
            '"collaboration_id":"collab-1","runtime_id":"rt-1",'
            '"turn_id":"turn-1"}\n'
        ).encode("utf-8")
        + b"\x80abc\n"
    )

    journal.append_dialogue_audit_event_once(_audit_event(event_id="fresh"))

    quarantine_path = audit_path.with_name("events.corrupt-20260512T193715Z.jsonl")
    assert quarantine_path.exists()
    assert [record["event_id"] for record in _read_jsonl(audit_path)] == ["fresh"]
    assert journal._audit_seen == {("dialogue_turn", "collab-1", "turn-1")}


def test_ensure_outcomes_seen_loaded_quarantines_on_invalid_utf8(
    tmp_path: Path,
) -> None:
    now = datetime(2026, 5, 12, 19, 37, 15, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    outcomes_path = tmp_path / "plugin-data" / "analytics" / "outcomes.jsonl"
    outcomes_path.write_bytes(
        (
            '{"outcome_id":"ghost","timestamp":"2026-05-01T00:00:00Z",'
            '"outcome_type":"dialogue_turn","collaboration_id":"collab-1",'
            '"runtime_id":"rt-1","context_size":1024,"turn_id":"turn-1"}\n'
        ).encode("utf-8")
        + b"\x80abc\n"
    )

    journal.append_dialogue_outcome_once(_dialogue_outcome(outcome_id="fresh"))

    quarantine_path = outcomes_path.with_name(
        "outcomes.corrupt-20260512T193715Z.jsonl"
    )
    assert quarantine_path.exists()
    assert [record["outcome_id"] for record in _read_jsonl(outcomes_path)] == ["fresh"]
    assert journal._dialogue_outcomes_seen == {
        ("dialogue_turn", "collab-1", "turn-1")
    }
    assert journal._delegation_outcomes_seen == set()


def test_append_after_quarantine_reappends_once_then_resumes_dedup(
    tmp_path: Path,
) -> None:
    now = datetime(2026, 5, 12, 19, 37, 15, tzinfo=UTC)
    journal = OperationJournal(tmp_path / "plugin-data", clock=_fixed_clock(now))
    audit_path = tmp_path / "plugin-data" / "audit" / "events.jsonl"
    audit_path.write_bytes(
        (
            '{"event_id":"ghost","timestamp":"2026-05-01T00:00:00Z",'
            '"actor":"claude","action":"dialogue_turn",'
            '"collaboration_id":"collab-1","runtime_id":"rt-1",'
            '"turn_id":"turn-1"}\n'
        ).encode("utf-8")
        + b"\x80abc\n"
    )
    event = _audit_event(event_id="fresh")

    journal.append_dialogue_audit_event_once(event)
    journal.append_dialogue_audit_event_once(_audit_event(event_id="fresh-second"))

    assert [record["event_id"] for record in _read_jsonl(audit_path)] == ["fresh"]
```

- [ ] **Step 3: Run quarantine tests and verify failure**

Run:

```bash
uv run pytest tests/test_journal.py::TestAuditRetentionQuarantine tests/test_journal.py::test_ensure_audit_seen_loaded_quarantines_on_invalid_utf8 tests/test_journal.py::test_ensure_outcomes_seen_loaded_quarantines_on_invalid_utf8 tests/test_journal.py::test_append_after_quarantine_reappends_once_then_resumes_dedup -q
```

Expected:

```text
FAIL with UnicodeDecodeError propagation or missing quarantine helper.
```

- [ ] **Step 4: Implement `_quarantine_corrupt_jsonl`**

Add to `OperationJournal`:

```python
def _quarantine_corrupt_jsonl(
    self,
    path: Path,
    *,
    reason: Exception,
) -> Path:
    """Rename a UTF-8-corrupt journal file to a forensic sibling."""

    ts = self._now().strftime("%Y%m%dT%H%M%SZ")
    quarantine_path = path.with_name(f"{path.stem}.corrupt-{ts}{path.suffix}")
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

- [ ] **Step 5: Add quarantine handling to `prune_audit_logs()`**

Change audit pass:

```python
audit_quarantined_to: Path | None = None
outcomes_quarantined_to: Path | None = None

try:
    audit_stats = self._prune_jsonl_pass(
        path=self._audit_path,
        cutoff=cutoff,
        populate=lambda record: _populate_from_audit_record(record, new_audit_seen),
    )
except UnicodeDecodeError as exc:
    audit_quarantined_to = self._quarantine_corrupt_jsonl(self._audit_path, reason=exc)
    audit_stats = _PruneFileStats(retained=0, dropped=0, retained_malformed=0)
    new_audit_seen = set()

self._audit_seen = new_audit_seen
self._audit_seen_initialized = True
```

Change outcomes pass similarly:

```python
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
    outcomes_stats = _PruneFileStats(retained=0, dropped=0, retained_malformed=0)
    new_dialogue_outcomes_seen = set()
    new_delegation_outcomes_seen = set()
```

Replace the Task 2 Step 5 six-kwarg return with the eight-kwarg form so quarantine paths surface in `PruneSummary`. Missing either keyword keeps `summary.audit_quarantined_to` / `summary.outcomes_quarantined_to` at the dataclass default of `None`, silently breaking the round-1 mirror tests:

```python
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

- [ ] **Step 6: Add quarantine handling to `_ensure_*_seen_loaded()`**

Change `_ensure_audit_seen_loaded()`:

```python
try:
    self._populate_seen_from_file(
        self._audit_path,
        lambda record: _populate_from_audit_record(record, new_audit_seen),
    )
except UnicodeDecodeError as exc:
    self._quarantine_corrupt_jsonl(self._audit_path, reason=exc)
    new_audit_seen = set()
```

Change `_ensure_outcomes_seen_loaded()`:

```python
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
```

Do not catch `OSError` in these methods.

- [ ] **Step 7: Run all journal-targeted tests**

Run:

```bash
uv run pytest tests/test_journal.py -q
```

Expected:

```text
PASS
```

- [ ] **Step 8: Commit Task 4**

Run:

```bash
git add server/journal.py tests/test_journal.py
git commit -m "fix(journal): quarantine corrupt audit jsonl"
```

---

### Task 5: Wire Startup Prune Into Bootstrap

**Files:**
- Modify: `tests/test_bootstrap.py`
- Modify: `scripts/codex_runtime_bootstrap.py`

- [ ] **Step 1: Add bootstrap prune tests**

In `tests/test_bootstrap.py`, add:

```python
def _patch_bootstrap_run(
    monkeypatch: pytest.MonkeyPatch,
    mod: object,
    tmp_path: Path,
) -> list[object]:
    runs: list[object] = []
    monkeypatch.setattr(mod, "default_plugin_data_path", lambda: tmp_path)

    def fake_run(self: object) -> None:
        runs.append(self)

    monkeypatch.setattr(mod.McpServer, "run", fake_run)
    return runs
```

Add tests:

```python
class TestBootstrapRetentionPrune:
    def test_bootstrap_logs_info_summary_when_prune_succeeds_with_zero_malformed(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mod = _import_bootstrap()
        runs = _patch_bootstrap_run(monkeypatch, mod, tmp_path)

        with caplog.at_level("INFO"):
            mod.main()

        assert len(runs) == 1
        assert "audit prune complete:" in caplog.text
        assert "audit_quarantined_to=None" in caplog.text

    def test_bootstrap_warns_summary_when_prune_succeeds_with_nonzero_audit_malformed(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mod = _import_bootstrap()
        _patch_bootstrap_run(monkeypatch, mod, tmp_path)
        audit_path = tmp_path / "audit" / "events.jsonl"
        audit_path.parent.mkdir(parents=True)
        audit_path.write_text('{"timestamp": "not-a-date"}\n', encoding="utf-8")

        with caplog.at_level("WARNING"):
            mod.main()

        assert "audit_retained_malformed=1" in caplog.text

    def test_bootstrap_warns_when_prune_raises_oserror(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mod = _import_bootstrap()
        runs = _patch_bootstrap_run(monkeypatch, mod, tmp_path)

        def fail_prune(self: object) -> object:
            raise OSError("prune failed")

        monkeypatch.setattr(mod.OperationJournal, "prune_audit_logs", fail_prune)

        with caplog.at_level("WARNING"):
            mod.main()

        assert len(runs) == 1
        assert "startup retention cleanup failed or incomplete; continuing" in caplog.text

    def test_bootstrap_does_not_swallow_unicode_decode_error_directly(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mod = _import_bootstrap()
        _patch_bootstrap_run(monkeypatch, mod, tmp_path)

        def fail_prune(self: object) -> object:
            raise UnicodeDecodeError("utf-8", b"\x80", 0, 1, "invalid start byte")

        monkeypatch.setattr(mod.OperationJournal, "prune_audit_logs", fail_prune)

        with pytest.raises(UnicodeDecodeError):
            mod.main()
```

Add mirror tests for:

- nonzero `outcomes_retained_malformed`
- `audit_quarantined_to` warning summary
- `outcomes_quarantined_to` warning summary
- `ValueError` propagation

- [ ] **Step 2: Run bootstrap tests and verify failure**

Run:

```bash
uv run pytest tests/test_bootstrap.py::TestBootstrapRetentionPrune -q
```

Expected:

```text
FAIL because bootstrap does not call prune_audit_logs or log summaries yet.
```

- [ ] **Step 3: Implement bootstrap logging and prune call**

In `scripts/codex_runtime_bootstrap.py`, add:

```python
import logging
```

After imports:

```python
logger = logging.getLogger(__name__)
```

In `main()`, immediately after `journal = OperationJournal(plugin_data_path)`:

```python
try:
    summary = journal.prune_audit_logs()
except OSError:
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
        logger.warning(summary_msg, *summary_args)
    else:
        logger.info(summary_msg, *summary_args)
```

Do not catch `UnicodeDecodeError` or `ValueError`.

- [ ] **Step 4: Run bootstrap tests**

Run:

```bash
uv run pytest tests/test_bootstrap.py::TestBootstrapRetentionPrune -q
```

Expected:

```text
PASS
```

- [ ] **Step 5: Structural bootstrap catch check**

Run:

```bash
rg "except \(OSError, UnicodeDecodeError\)" scripts/
```

Expected:

```text
No output.
```

- [ ] **Step 6: Commit Task 5**

Run:

```bash
git add scripts/codex_runtime_bootstrap.py tests/test_bootstrap.py
git commit -m "fix(bootstrap): prune audit logs on startup"
```

---

### Task 6: Update Owner Specs For F4 Retention Semantics

**Files:**
- Modify: `docs/specs/recovery-and-journal.md`
- Modify: `docs/specs/decisions.md`

- [ ] **Step 1: Patch `docs/specs/recovery-and-journal.md` two-log table**

Change:

```markdown
| Retention | Trim on operation completion | TTL-based (30 days) |
```

to:

```markdown
| Retention | Trim on operation completion | TTL-based (30 days from event timestamp), pruned at plugin startup |
```

- [ ] **Step 2: Add `Operational Outcomes` subsection after `Why Two Logs`**

Insert:

```markdown
### Operational Outcomes

A third file, `${CLAUDE_PLUGIN_DATA}/analytics/outcomes.jsonl`, holds delegation and dialogue terminal outcome records (`OutcomeRecord` and `DelegationOutcomeRecord`). It shares the Audit Log's retention class - best-effort append, 30-day TTL, startup-pruned, single-writer ownership - but uses a different record format (typed terminal outcomes rather than per-event audit entries) and a different consumer (retrospective diagnostics rather than incident reconstruction).

**Outcomes are operational diagnostics with a 30-day operational horizon, not long-term analytics history.** A future feature that consumes outcomes for long-term analytics must introduce a separate retention class before shipping.
```

- [ ] **Step 3: Replace `Audit Log` retention bullets**

Replace the current three bullets under `### Retention` with the text from design sections 7.2 and 7.3. Required phrases that must appear:

```text
Operational retention for audit and outcome JSONL records uses the same 30-day TTL.
outcomes.jsonl
retain-on-uncertainty
TTL-exempt by design
atomic per file
UTF-8 with LF-only line endings
automatic quarantine
<stem>.corrupt-<utc-ts><suffix>
periodic-during-session pruning is not implemented in v1
```

- [ ] **Step 4: Patch `Retention Defaults` preamble and rows**

Replace:

```markdown
Canonical retention values. All TTLs are measured from `last_touched_at`, not creation time.
```

with:

```markdown
Canonical retention values. TTL triggers vary by resource: see the Trigger column. Most TTLs are measured from `last_touched_at`; audit log and outcome records use their event timestamp.
```

Replace:

```markdown
| Audit log records | 30 days | From event timestamp |
```

with:

```markdown
| Audit log records (`events.jsonl`) | 30 days | From event timestamp |
| Outcome records (`outcomes.jsonl`) | 30 days | From event timestamp |
```

- [ ] **Step 5: Patch `docs/specs/decisions.md` analytics source bullet**

Change the analytics source bullet to:

```markdown
- **Analytics source:** `analytics/outcomes.jsonl` (advisory and delegation
  terminal outcomes) plus `audit/events.jsonl` (lifecycle and security), both
  interpreted as retention-window operational diagnostics after F4 audit
  retention. No new cross-model-style flat emitter. No raw-store walking as the
  primary analytics contract.
```

- [ ] **Step 6: Verify docs phrases**

Run:

```bash
rg -n "Operational Outcomes|TTL-exempt by design|automatic quarantine|Outcome records|retention-window operational diagnostics" docs/specs/recovery-and-journal.md docs/specs/decisions.md
```

Expected:

```text
All required terms appear in the intended owner/spec files.
```

- [ ] **Step 7: Commit Task 6**

Run:

```bash
git add docs/specs/recovery-and-journal.md docs/specs/decisions.md
git commit -m "docs(specs): document audit retention semantics"
```

---

### Task 7: Update Analytics Skill And Script Output

**Files:**
- Modify: `skills/codex-analytics/SKILL.md`
- Modify: `skills/codex-analytics/scripts/analytics.py`
- Modify: `tests/test_analytics_skill.py`

- [ ] **Step 1: Add analytics script tests for retention-window labels**

In `tests/test_analytics_skill.py`, update `test_data_header_with_paths_and_counts` assertions:

```python
assert "retention-window records" in output
assert "observed timestamp range" in output
```

Add a focused test:

```python
def test_data_header_reports_observed_timestamp_ranges(self, tmp_path: Path) -> None:
    output = _run_analytics(tmp_path)

    assert "Outcomes observed timestamp range:" in output
    assert "2026-01-01T00:00:00Z" in output
    assert "2026-04-21T00:00:00Z" in output
    assert "Audit observed timestamp range:" in output
```

Add a test that pins the round-1 F2 parseable-only filter - malformed string timestamps must NOT define the range endpoints, and the count of skipped records must surface separately. This test bypasses `_run_analytics()` because that helper calls `_write_fixtures()` against `tmp_path / "data"` and would overwrite anything written elsewhere; instead invoke the analytics script directly with custom fixture paths so the malformed records are actually read:

```python
def test_data_header_excludes_malformed_timestamps_from_range(
    self, tmp_path: Path
) -> None:
    """Round-1 F2 amendment. Records with non-string, unparseable, or
    timezone-naive `timestamp` fields must NOT participate in the range
    computation; they appear instead in a per-file missing/malformed count.

    Bypasses `_run_analytics()` (which rebuilds fixtures under
    `tmp_path/"data"`) and invokes the script directly with flat paths so
    the malformed-timestamp fixture is the actual input to the script.
    """
    outcomes_path = tmp_path / "outcomes.jsonl"
    audit_path = tmp_path / "events.jsonl"
    outcomes_path.write_text(
        '{"outcome_id":"valid","timestamp":"2026-04-01T00:00:00Z",'
        '"outcome_type":"dialogue_turn","collaboration_id":"c",'
        '"runtime_id":"r","context_size":1024,"turn_id":"t",'
        '"turn_sequence":1}\n'
        '{"outcome_id":"unparseable","timestamp":"not-a-date",'
        '"outcome_type":"dialogue_turn","collaboration_id":"c",'
        '"runtime_id":"r","context_size":1024,"turn_id":"t2",'
        '"turn_sequence":2}\n'
        '{"outcome_id":"naive","timestamp":"2026-04-01T00:00:00",'
        '"outcome_type":"dialogue_turn","collaboration_id":"c",'
        '"runtime_id":"r","context_size":1024,"turn_id":"t3",'
        '"turn_sequence":3}\n',
        encoding="utf-8",
    )
    audit_path.write_text("", encoding="utf-8")

    result = subprocess.run(
        ["python3", str(ANALYTICS_SCRIPT), str(outcomes_path), str(audit_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Script failed:\n{result.stderr}"
    output = result.stdout

    # The well-formed timestamp is the only parseable one - appears as both
    # endpoints of the displayed range.
    assert "2026-04-01T00:00:00Z" in output
    # The malformed/naive strings MUST NOT appear in the displayed range.
    assert "not-a-date" not in output
    assert "2026-04-01T00:00:00 " not in output  # naive form (no trailing Z)
    # Missing/malformed count is surfaced per file.
    assert "2 records with missing or malformed timestamps" in output
```

- [ ] **Step 2: Run analytics tests and verify failure**

Run:

```bash
uv run pytest tests/test_analytics_skill.py -q
```

Expected:

```text
FAIL because analytics.py does not label retention-window counts or timestamp ranges yet.
```

- [ ] **Step 3: Implement timestamp range reporting**

In `skills/codex-analytics/scripts/analytics.py`, add the `datetime` imports if not present:

```python
from datetime import UTC, datetime
```

Then add the helper. **Round-1 F2 amendment** - the helper filters to timezone-aware ISO 8601 strings only (matching `_parse_aware_iso8601` semantics in `server/journal.py`) so a malformed string like `"not-a-date"` cannot become a range endpoint. The helper returns a tuple `(range_string, missing_or_malformed_count)` so the data-source header can surface per-file counts separately:

```python
def _timestamp_range(records: list[dict[str, object]]) -> tuple[str, int]:
    """Return (range_string, missing_or_malformed_count).

    Only timezone-aware ISO 8601 timestamps participate in the range -
    matches the journal's `_parse_aware_iso8601` strictness. Records with
    missing, non-string, unparseable, or timezone-naive `timestamp` fields
    are counted as missing/malformed and reported alongside the range so
    the user understands the displayed window is parseable-only.
    """
    parseable: list[datetime] = []
    missing_or_malformed = 0
    for record in records:
        value = record.get("timestamp")
        if not isinstance(value, str):
            missing_or_malformed += 1
            continue
        try:
            ts = datetime.fromisoformat(value)
        except ValueError:
            missing_or_malformed += 1
            continue
        if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
            missing_or_malformed += 1
            continue
        parseable.append(ts.astimezone(UTC))
    if not parseable:
        return "n/a", missing_or_malformed
    parseable.sort()
    earliest = parseable[0].isoformat().replace("+00:00", "Z")
    latest = parseable[-1].isoformat().replace("+00:00", "Z")
    return f"{earliest} to {latest}", missing_or_malformed
```

Replace data-source prints with:

```python
outcomes_range, outcomes_missing = _timestamp_range(outcome_records)
audit_range, audit_missing = _timestamp_range(audit_records)
print(
    f"- Outcomes: `{outcomes_path}` "
    f"({total_outcome_records} retention-window records{outcomes_note})"
)
print(
    f"- Audit: `{audit_path}` "
    f"({total_audit_records} retention-window records{audit_note})"
)
print(
    f"- Outcomes observed timestamp range: {outcomes_range} "
    f"({outcomes_missing} records with missing or malformed timestamps)"
)
print(
    f"- Audit observed timestamp range: {audit_range} "
    f"({audit_missing} records with missing or malformed timestamps)"
)
```

- [ ] **Step 4: Update analytics skill prose**

In `skills/codex-analytics/SKILL.md`, replace:

```markdown
Both are append-only JSONL. Use the analytics script (see below) for aggregation, or `Read` for ad-hoc inspection of small files.
```

with:

```markdown
Both are startup-pruned operational JSONL streams with a 30-day retention horizon after F4. Use the analytics script (see below) for retention-window aggregation, or `Read` for ad-hoc inspection of small live files. Forensic `*.corrupt-*` siblings may exist after UTF-8 quarantine; do not treat them as live analytics inputs unless the user explicitly asks for forensic inspection.
```

Add under `## Output Format`:

```markdown
Counts are retention-window counts, not all-time totals. Include the observed timestamp range from each live input file in the data-source header so the user can see the covered window. Only records with timezone-aware ISO 8601 timestamps participate in the range; records with missing, non-string, unparseable, or timezone-naive timestamps are surfaced separately as a missing/malformed count alongside each range so the user sees both the parseable window AND how many records were excluded from it.
```

- [ ] **Step 5: Run analytics tests**

Run:

```bash
uv run pytest tests/test_analytics_skill.py -q
```

Expected:

```text
PASS
```

- [ ] **Step 6: Commit Task 7**

Run:

```bash
git add skills/codex-analytics/SKILL.md skills/codex-analytics/scripts/analytics.py tests/test_analytics_skill.py
git commit -m "docs(analytics): label retention-window data"
```

---

### Task 8: Legacy Test Migration And Targeted Verification

**Files:**
- Modify as needed: `tests/test_journal.py`
- Modify as needed: `server/journal.py`

- [ ] **Step 1: Inventory stale `_jsonl_contains` tests or comments**

Run:

```bash
rg "_jsonl_contains" tests/ server/ scripts/
```

Expected:

```text
No output from server/ or scripts/.
Tests should also have no references unless intentionally discussing removed legacy behavior.
```

- [ ] **Step 2: Run targeted test files**

Run:

```bash
uv run pytest tests/test_journal.py tests/test_bootstrap.py tests/test_analytics_skill.py -q
```

Expected:

```text
PASS
```

- [ ] **Step 3: Run code formatting/lint on touched files**

Run:

```bash
uv run ruff check server/journal.py scripts/codex_runtime_bootstrap.py tests/test_journal.py tests/test_bootstrap.py tests/test_analytics_skill.py skills/codex-analytics/scripts/analytics.py
```

Expected:

```text
All checks pass.
```

If ruff reports import ordering or line-length issues, fix those exact issues. Do not broaden the task.

- [ ] **Step 4: Commit any verification fixes**

Run only if Step 2 or Step 3 required edits:

```bash
git add server/journal.py scripts/codex_runtime_bootstrap.py tests/test_journal.py tests/test_bootstrap.py tests/test_analytics_skill.py skills/codex-analytics/scripts/analytics.py
git commit -m "test(journal): align retention verification"
```

---

### Task 9: Final Full-Suite Verification And Structural Gates

**Files:**
- Read: full repo

- [ ] **Step 1: Run final targeted tests verbosely**

Run:

```bash
uv run pytest tests/test_journal.py tests/test_bootstrap.py tests/test_analytics_skill.py -v
```

Expected:

```text
PASS for all selected tests.
```

- [ ] **Step 2: Run full test suite**

Run:

```bash
uv run pytest tests -q
```

Expected:

```text
PASS for the full suite.
```

This suite is expected to take several minutes. If unrelated baseline failures appear, stop and classify them with exact failing tests before changing code.

- [ ] **Step 3: Run full ruff**

Run:

```bash
uv run ruff check .
```

Expected:

```text
All checks pass.
```

- [ ] **Step 4: Run structural grep gates**

Run:

```bash
rg "_jsonl_contains" server/ scripts/
rg "_seen_sets_initialized" server/ scripts/
rg "except \(OSError, UnicodeDecodeError\)" scripts/
rg 'newline="\\n"' server/journal.py
rg "_quarantine_corrupt_jsonl" server/journal.py
```

Expected:

```text
First command: no output.
Second command: no output.
Third command: no output.
Fourth command: exactly 4 hits unless a new audit/outcome writer was deliberately added and explained.
Fifth command: at least 5 hits: 1 definition plus 4 call sites.
```

If `_quarantine_corrupt_jsonl` has fewer than 5 hits, do not claim completion. Read call sites and patch missing startup/runtime coverage.

- [ ] **Step 5: Manual reader-classification review**

Run:

```bash
rg -n "glob|rglob|iterdir|scandir|listdir" server/ scripts/ skills/codex-analytics
```

Expected:

```text
No new audit/analytics directory enumeration introduced by F4.
Existing unrelated hits are classified as unrelated to audit/events.jsonl and analytics/outcomes.jsonl live readers.
```

If F4 introduced a directory enumeration over `${CLAUDE_PLUGIN_DATA}/audit/` or `${CLAUDE_PLUGIN_DATA}/analytics/`, patch it to exact-name reads or explicit `*.corrupt-*` exclusion before proceeding.

- [ ] **Step 6: Check git diff**

Run:

```bash
git status --short
git diff --check
git diff --stat
```

Expected:

```text
Only F4 files are modified.
No whitespace errors.
Diff stat matches the planned surfaces.
```

- [ ] **Step 7: Commit final verification/docs cleanup if needed**

Run only if final cleanup edits were necessary:

```bash
git add server/journal.py scripts/codex_runtime_bootstrap.py tests/test_journal.py tests/test_bootstrap.py tests/test_analytics_skill.py docs/specs/recovery-and-journal.md docs/specs/decisions.md skills/codex-analytics/SKILL.md skills/codex-analytics/scripts/analytics.py
git commit -m "chore(f4): finalize audit retention gates"
```

If a final cleanup touched a smaller set, stage only those exact files. Never stage unrelated local work.

---

## Completion Report Template

Use this shape when reporting implementation completion:

```markdown
What changed
- Implemented startup pruning for `audit/events.jsonl` and `analytics/outcomes.jsonl`.
- Replaced append-once linear scans with per-file in-memory seen sets.
- Added UTF-8 quarantine for startup and runtime read paths.
- Updated bootstrap logging plus owner/analytics docs.

Why it changed
- F4 required retention enforcement and removal of O(n) dedup scans while preserving diagnostic evidence.

Verification performed
- `uv run pytest tests/test_journal.py tests/test_bootstrap.py tests/test_analytics_skill.py -v`
- `uv run pytest tests -q`
- `uv run ruff check .`
- Structural grep gates for `_jsonl_contains`, `_seen_sets_initialized`, bootstrap catch narrowing, `newline="\n"`, and `_quarantine_corrupt_jsonl`.

Remaining risks
- F12 crash/restart audit emission remains deferred.
- Malformed timestamp records remain TTL-exempt and require operator attention.
- Concurrent MCP processes sharing one plugin data root remain unsupported.
```

## Self-Review Checklist For The Plan Executor

- [ ] Every design-section behavior has a task:
  - Clock seam: Task 1.
  - Startup prune for audit/outcomes: Task 2.
  - Retain-on-uncertainty: Task 2.
  - LF-only file output: Task 2 and Task 9.
  - In-memory seen sets: Task 3.
  - UTF-8 quarantine: Task 4.
  - Bootstrap logging and catch narrowing: Task 5.
  - Owner spec updates: Task 6.
  - Analytics consumer updates: Task 7.
  - Structural verification: Task 9.
- [ ] No F12 implementation appears in the diff.
- [ ] The final report includes actual command outputs or exact pass/fail status, not inferred success.
