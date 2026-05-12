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
- Pruning is a pure filter: retained records are written back as their original raw lines, byte-for-byte, never re-serialized.
- Records with missing, non-string, unparseable, or timezone-naive `timestamp` fields are retained (retain-on-uncertainty principle — ambiguous records are not silently erased). These records are **TTL-exempt by design**: the 30-day TTL applies only to records with parseable, timezone-aware timestamps, so a sufficiently corrupt audit or outcome line can survive past the 30-day window indefinitely. `PruneSummary.audit_retained_malformed` and `PruneSummary.outcomes_retained_malformed` count these records each pass; they share the observability conditional described in the bootstrap bullet below.
- Records that fail to parse as JSON, or parse as non-dict shapes, are retained as raw lines.
- Blank lines are removed during pruning (not records; not subject to retain-on-uncertainty).
- The three `append_*_once` methods consult an in-memory dedup set keyed on natural fields. Set membership replaces the previous linear file scan. Sets are atomically rebuilt during prune and atomically loaded on first direct-construction use.
- A clock seam (`OperationJournal(..., clock=Callable[[], datetime])`) governs every "now" the journal uses. Naive clock outputs fail fast with `ValueError`. Production code does not pass concrete `now=` values; tests inject fake clocks.
- Atomic file replacement guarantees: target file untouched on pre-replace failure; POSIX-atomic swap on `os.replace` success. Does *not* directory-fsync — post-rename durability across power-fail is not asserted, matching the existing `compact()` and `_write_markers` pattern.
- **Atomicity is per file, not pair-wise.** A successful prune of `events.jsonl` followed by a failed prune of `outcomes.jsonl` leaves the canonical files in a mixed-prune state. Both files are independent retention surfaces; the next startup re-runs the full prune. Append correctness is preserved across the mixed state because `_ensure_seen_sets_loaded()` reads disk as the source of truth when the in-memory atomic swap is skipped.
- **Single-writer assumption.** Exactly one MCP process owns a given `plugin_data_path` at a time. Concurrent prune from two processes against the same data directory is undefined and unsupported — the fixed-suffix temp file `<path>.tmp` would collide. This matches the existing `compact()` and `_write_markers` patterns in `OperationJournal`.
- The plugin bootstrap invokes pruning. Prune failure (`OSError`) invokes `logger.warning(..., exc_info=True)` and does not block startup. **Warning-level output reaches stderr via Python's `logging.lastResort` handler (the unconfigured-logger fallback), so the failure signal is observable to whoever sees the MCP server's stderr unless the host suppresses it.** The success-summary call (`logger.info(...)` in §6.1) is below the lastResort threshold and is discarded by Python's default logging configuration; operator visibility into success metrics requires F18 (or `caplog` in tests). Append correctness is preserved through `_ensure_seen_sets_loaded()` regardless of logging state.

## 3. Scope

### In

- Pruning for `audit/events.jsonl` and `analytics/outcomes.jsonl` at startup.
- Replacement of linear `_jsonl_contains` dedup with in-memory seen-sets.
- Clock seam added to `OperationJournal` constructor.
- Spec amendments to `docs/specs/recovery-and-journal.md` §Audit Log → Retention and §Retention Defaults.
- New tests in `tests/test_journal.py` covering all pruning, dedup, atomic-rewrite, and bootstrap-integration invariants.
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
from datetime import UTC, datetime, timedelta

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
```

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
    self._seen_sets_initialized = False
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
      - Calls _ensure_seen_sets_loaded() before the dedup check; direct-
        construction paths get correct dedup automatically.
      - The seen-set is updated only after append_audit_event() succeeds.
        If append raises, the key is not added so a retry can still write.
    """
```

Same invariant for `append_dialogue_outcome_once` and `append_delegation_outcome_once`.

### Private methods

- `_ensure_seen_sets_loaded()` — populate from on-disk files without rewriting. Atomic rebuild semantics (local sets, assigned only on full success). Does not flip `_seen_sets_initialized` if either file's population raises.
- `_prune_jsonl_pass(*, path, cutoff, populate)` — single linear scan; produces retained raw lines and per-file stats.
- `_populate_seen_from_file(path, on_record)` — read-only population helper used by `_ensure_seen_sets_loaded`.
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
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        handle.writelines(retained_lines)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)

    return _PruneFileStats(retained_count, dropped_count, retained_malformed_count)
```

`prune_audit_logs` orchestrates:

```python
def prune_audit_logs(self, now: datetime | None = None) -> PruneSummary:
    now = (
        self._now()
        if now is None
        else _coerce_aware_utc(now, source="prune_audit_logs(now=...)")
    )
    cutoff = now - timedelta(days=_AUDIT_TTL_DAYS)

    # Invalidate seen-set initialization before any disk mutation. If any
    # prune pass raises after we've started rewriting files, the flag stays
    # False and the next append_*_once triggers a fresh read from disk —
    # load-bearing for re-runnable prune on an already-initialized journal.
    self._seen_sets_initialized = False

    new_audit_seen: set[_AuditDedupKey] = set()
    new_dialogue_outcomes_seen: set[_DialogueOutcomeDedupKey] = set()
    new_delegation_outcomes_seen: set[_DelegationOutcomeDedupKey] = set()

    audit_stats = self._prune_jsonl_pass(
        path=self._audit_path,
        cutoff=cutoff,
        populate=lambda r: _populate_from_audit_record(r, new_audit_seen),
    )
    outcomes_stats = self._prune_jsonl_pass(
        path=self._outcomes_path,
        cutoff=cutoff,
        populate=lambda r: _populate_from_outcome_record(
            r, new_dialogue_outcomes_seen, new_delegation_outcomes_seen,
        ),
    )

    # Atomic assignment — only after both files completed without raising.
    self._audit_seen = new_audit_seen
    self._dialogue_outcomes_seen = new_dialogue_outcomes_seen
    self._delegation_outcomes_seen = new_delegation_outcomes_seen
    self._seen_sets_initialized = True

    return PruneSummary(
        audit_retained=audit_stats.retained,
        audit_dropped=audit_stats.dropped,
        audit_retained_malformed=audit_stats.retained_malformed,
        outcomes_retained=outcomes_stats.retained,
        outcomes_dropped=outcomes_stats.dropped,
        outcomes_retained_malformed=outcomes_stats.retained_malformed,
    )
```

If `_prune_jsonl_pass` for `outcomes.jsonl` raises after `events.jsonl` has been successfully replaced, the journal's in-memory seen-sets are *not* reassigned (the `self._audit_seen = new_audit_seen` lines are unreached) **and** the `_seen_sets_initialized` flag — cleared at prune entry — is not restored to `True`. On disk, `events.jsonl` reflects the prune; `outcomes.jsonl` is untouched. The next `append_*_once` consults `_ensure_seen_sets_loaded()`, which (because the flag is now `False`) reads disk as the source of truth and populates from the mixed state correctly. The next prune cycle re-runs both files. This per-file-not-pair-wise transaction boundary is named in §2 Contract; the flag-clear-at-entry discipline is what keeps the boundary correct when prune is re-run on a journal whose seen-sets were previously initialized — without it, stale in-memory keys could silently skip valid appends.

### 5.2a Population helpers

The `populate` callback used by `_prune_jsonl_pass` (and the equivalent reader path in `_ensure_seen_sets_loaded`) is one of two module-level free functions:

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

Both `prune_audit_logs` and `_ensure_seen_sets_loaded` follow the rebuild-and-swap pattern: local sets are constructed during the pass, and `self._audit_seen` / `self._dialogue_outcomes_seen` / `self._delegation_outcomes_seen` are reassigned only after the full pass succeeds.

`prune_audit_logs` clears `_seen_sets_initialized` to `False` as the first step of the call (before any disk mutation), and sets it back to `True` only after the atomic reassignment block. If any sub-step raises, the in-memory sets retain whatever values they held — but because the flag is now `False`, the next `append_*_once` triggers `_ensure_seen_sets_loaded()`, which reads disk as the source of truth and rebuilds. **This invalidate-before-disk-mutation discipline is load-bearing for re-runnable pruning:** without it, a partial cross-file prune on an already-initialized journal would leave the in-memory sets out of sync with disk, causing later appends to silently skip records that no longer exist on disk.

`_ensure_seen_sets_loaded` is no-op when `_seen_sets_initialized` is `True`. If it raises mid-load, the flag stays `False` and the next `append_*_once` retries.

### 5.7 `_ensure_seen_sets_loaded` semantics

```python
def _ensure_seen_sets_loaded(self) -> None:
    if self._seen_sets_initialized:
        return

    new_audit_seen: set[_AuditDedupKey] = set()
    new_dialogue_outcomes_seen: set[_DialogueOutcomeDedupKey] = set()
    new_delegation_outcomes_seen: set[_DelegationOutcomeDedupKey] = set()

    # If either population raises, exception propagates and the seen-set
    # state stays as it was. append_*_once will then surface the IO error
    # rather than silently appending a possibly-duplicate record.
    self._populate_seen_from_file(
        self._audit_path,
        lambda r: _populate_from_audit_record(r, new_audit_seen),
    )
    self._populate_seen_from_file(
        self._outcomes_path,
        lambda r: _populate_from_outcome_record(
            r, new_dialogue_outcomes_seen, new_delegation_outcomes_seen,
        ),
    )

    self._audit_seen = new_audit_seen
    self._dialogue_outcomes_seen = new_dialogue_outcomes_seen
    self._delegation_outcomes_seen = new_delegation_outcomes_seen
    self._seen_sets_initialized = True
```

`_populate_seen_from_file` tolerates malformed lines exactly as the legacy `_jsonl_contains` did: blank lines, `json.JSONDecodeError`, and non-dict records are skipped. A corrupt historical line never disables future writes.

### 5.8 Append-once update-after-success invariant

```python
def append_dialogue_audit_event_once(self, event: AuditEvent) -> None:
    self._ensure_seen_sets_loaded()
    key: _AuditDedupKey = (event.action, event.collaboration_id, event.turn_id)
    if key in self._audit_seen:
        return
    self.append_audit_event(event)   # may raise — do NOT add key on failure
    self._audit_seen.add(key)
```

The seen-set is mutated only after the underlying append IO returns successfully. If `append_audit_event` raises, the key remains absent from the set; a later retry can still write the record. Same shape for `append_dialogue_outcome_once` and `append_delegation_outcome_once`.

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
        logger.warning(
            "audit prune failed; continuing without startup retention cleanup",
            exc_info=True,
        )
    else:
        logger.info(
            "audit prune complete: audit_retained=%d audit_dropped=%d "
            "audit_retained_malformed=%d outcomes_retained=%d "
            "outcomes_dropped=%d outcomes_retained_malformed=%d",
            summary.audit_retained,
            summary.audit_dropped,
            summary.audit_retained_malformed,
            summary.outcomes_retained,
            summary.outcomes_dropped,
            summary.outcomes_retained_malformed,
        )

    # ... rest of bootstrap (ControlPlane, registries, McpServer) unchanged ...
```

No concrete `now` argument is passed — production consumes `journal._clock()` via `_now()`. The catch is narrowed to `OSError`; parse-side or implementation-bug exceptions are not swallowed and would surface as bootstrap failures.

Without `logging.basicConfig` (which F18 will provide), Python's logging defaults dispatch `logger.warning(...)` through `logging.lastResort` to stderr — so the prune-failure signal is observable to whatever process sees the MCP server's stderr (typically Claude Code), even before F18. `logger.info(...)` is below the lastResort threshold and is discarded; operator visibility into the success-summary `info` call requires F18 or `caplog`. Both calls are testable via `caplog` or a monkeypatched logger.

### 6.2 Factory-deferred reality

`OperationJournal` is constructed eagerly in `bootstrap.main()`. Both `_dialogue_factory` and `_delegation_factory` receive the same instance. Controllers may be lazy-initialized via `McpServer._ensure_*_controller`, but the journal — and therefore the prune — runs once at process startup regardless. F4's lifecycle is decoupled from F12's lifecycle question.

### 6.3 Re-runnable prune

`prune_audit_logs()` is safe to call multiple times. Each invocation:
- Recomputes `cutoff` from the current `_now()` (or explicit `now=`).
- Rebuilds local seen-sets from scratch.
- Atomically reassigns sets and writes rewritten files only on success.

A second prune after time has advanced correctly evicts newly-expired keys.

### 6.4 Test fixture pattern

| Test scenario | Construction |
|---|---|
| Default dedup behavior, no time-sensitivity | `OperationJournal(plugin_data_path=tmp_path)` |
| Pruning correctness with fake clock | `OperationJournal(plugin_data_path=tmp_path, clock=lambda: aware_datetime)` |
| Explicit cutoff override | Pass `now=aware_datetime` to `prune_audit_logs()` |
| Direct-construction dedup safety | Construct without calling prune; first `append_*_once` exercises `_ensure_seen_sets_loaded` |

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

### 7.2 §Audit Log → Retention subsection

Replace the existing three bullets with:

> Operational retention for audit and outcome JSONL records uses the same 30-day TTL. Outcomes are treated as **operational diagnostics with a 30-day operational horizon**, not long-term analytics history; if a future feature consumes outcomes for long-term analytics, a separate retention class must be introduced before the consuming feature ships.
>
> - **Default TTL:** 30 days from event timestamp.
> - **Storage:** `${CLAUDE_PLUGIN_DATA}/audit/events.jsonl` (audit events) and `${CLAUDE_PLUGIN_DATA}/analytics/outcomes.jsonl` (dialogue and delegation outcomes).
> - **Cleanup:** Pruned at plugin startup. Pruning is a pure filter — retained records are written back as their original raw lines, never re-serialized.
> - **Timestamp parsing:** Pruning compares timezone-aware ISO 8601 timestamps. Records with missing, non-string, unparseable, or timezone-naive `timestamp` fields are retained (retain-on-uncertainty: ambiguous records are never silently erased). These malformed-timestamp records are **TTL-exempt by design** — the 30-day TTL applies only to records with parseable, timezone-aware timestamps; sufficiently corrupt records can survive past the 30-day window indefinitely.
> - **Per-file atomicity:** Pruning is atomic per file (`events.jsonl` and `outcomes.jsonl` are independent retention surfaces), not pair-wise. A failure of one file's prune after the other has already been rewritten leaves a mixed-prune state; the next startup re-runs both files.
> - **Ownership model:** Exactly one MCP process owns a given `${CLAUDE_PLUGIN_DATA}` directory at a time. Concurrent prune from two processes against the same data directory is undefined and unsupported (matches the existing operation-journal ownership model).
> - **Blank lines** are not audit/outcome records and may be removed during pruning.
>
> *Future scope:* periodic-during-session pruning is not implemented in v1. The startup cadence is sufficient for the supported session lifecycle (hours-scale, not multi-day). If future deployments hold the MCP process alive long enough for same-session expiry to matter, a periodic trigger can be added without changing the TTL contract.

### 7.3 §Retention Defaults table

Replace the single "Audit log records" row with two rows:

| Resource | TTL | Trigger |
|---|---|---|
| Audit log records (`events.jsonl`) | 30 days | From event timestamp |
| Outcome records (`outcomes.jsonl`) | 30 days | From event timestamp |

All other rows unchanged.

### 7.4 No changes

Operation Journal, Stale Advisory Context Marker, Crash Recovery Paths, Pending Request Ordering, Unknown Request Handling, Concurrency Limits sections are unchanged by this slice. F12's reserved-event semantics will be addressed in a sibling slice and may then amend the Audit Log → Write Triggers tables.

## 8. Testing Strategy

All tests in `tests/test_journal.py`.

### 8.1 Pruning correctness — happy path
- `test_prune_audit_logs_drops_records_older_than_ttl`
- `test_prune_audit_logs_retains_records_within_ttl`
- `test_prune_audit_logs_retains_record_exactly_at_ttl_boundary` — record dated exactly `now - 30 days`; per the contract (`ts < cutoff`), it is retained. Pins against accidental `<=` inversion.
- `test_prune_audit_logs_empty_file_is_noop`
- `test_prune_audit_logs_missing_file_is_noop`
- `test_prune_audit_logs_returns_correct_summary_counts`

### 8.2 Retain-on-uncertainty (parametrized)
- `test_prune_audit_logs_retains_record_with_malformed_timestamp` — parametrized over (missing field, non-string, unparseable ISO, timezone-naive)
- `test_prune_audit_logs_retains_malformed_json_line` — invalid JSON; raw line preserved byte-for-byte
- `test_prune_audit_logs_retains_non_dict_record` — array or scalar JSON line
- `test_prune_audit_logs_drops_blank_lines`

### 8.3 Raw-line retention invariant
- `test_prune_audit_logs_preserves_byte_for_byte_for_retained_records` — write a record with unsorted keys / extra whitespace; after prune, retained line is byte-identical to input.

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
- `test_prune_audit_logs_invalidates_seen_set_flag_on_partial_failure` — initialize seen-sets via a successful first prune; patch outcomes pass to raise OSError mid-pass; second prune raises but `_seen_sets_initialized` becomes False; next `append_*_once` triggers reload via `_ensure_seen_sets_loaded()` and dedup reflects post-events-pruned disk state. Pins F1 (new-review): without the flag-clear-at-entry, stale in-memory keys would silently skip valid appends.

### 8.7 Dedup-set construction
- `test_append_dialogue_audit_event_once_loads_seen_set_on_first_call` (no prune)
- `test_ensure_seen_sets_loaded_tolerates_corrupt_jsonl_line` — corrupt line in source file does not block population.
- `test_ensure_seen_sets_loaded_does_not_mark_initialized_on_failure` — patch population to raise; assert `_seen_sets_initialized` remains `False` and second call retries.

### 8.8 Dedup-set update invariant
- `test_append_dialogue_audit_event_once_skips_when_key_in_seen_set`
- `test_append_dialogue_audit_event_once_updates_seen_set_only_after_successful_append` — patch `append_audit_event` to raise; assert key NOT added; assert retry with functional IO succeeds.
- Mirror tests for `append_dialogue_outcome_once` and `append_delegation_outcome_once`.

### 8.9 Bootstrap integration
- `test_bootstrap_logs_prune_summary_when_prune_succeeds` — patch `McpServer.run` to no-op; patch `default_plugin_data_path` to `tmp_path`; capture log via `caplog`; assert `logger.info` with summary fields fired.
- `test_bootstrap_warns_when_prune_raises_oserror` — patch `OperationJournal.prune_audit_logs` to raise `OSError`; assert `logger.warning` fired and bootstrap continues to `server.run()` (which is itself patched).

### 8.10 Legacy test migration
- `rg "_jsonl_contains" tests/` to inventory.
- Any test that exercised the linear-scan dedup is reframed against the in-memory set behavior.
- Tests asserting "this `*_once` method skips a duplicate" stay valid; only the underlying mechanism changes.

## 9. Verification

Before claiming complete:

```bash
uv run pytest tests/test_journal.py -v     # new + existing journal tests pass
uv run pytest -q                            # full suite passes
uv run ruff check .                         # no lint regressions across server/ scripts/ tests/
rg "_jsonl_contains" server/ scripts/       # zero hits in production code
```

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
