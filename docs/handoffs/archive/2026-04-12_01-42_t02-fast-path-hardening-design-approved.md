---
date: 2026-04-12
time: "01:42"
created_at: "2026-04-12T05:42:26Z"
session_id: 7c98167f-b1ea-4a0f-82ae-aaa655ccfd82
resumed_from: docs/handoffs/archive/2026-04-12_00-52_s1-refactor-pr-merge-ticket-triage.md
project: claude-code-tool-dev
branch: main
commit: d5aa4038
title: T-02 first-turn fast path hardening — design complete, spec pending user review
type: handoff
files:
  - docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md
  - packages/plugins/codex-collaboration/server/dialogue.py
  - packages/plugins/codex-collaboration/server/turn_store.py
  - packages/plugins/codex-collaboration/server/replay.py
  - packages/plugins/codex-collaboration/tests/test_dialogue.py
---

# T-02 First-Turn Fast Path Hardening — Design Complete, Spec Pending User Review

## Goal

Design the hardening of `_next_turn_sequence()` in `DialogueController` to distinguish "genuinely empty TurnStore" from "metadata unreadable or structurally suspect," and unify the local-metadata consistency invariant across three enforcement sites: `_next_turn_sequence()`, `recover_startup()`, and `read()`.

**Trigger:** Session resumed from a handoff where ticket triage had identified T-20260410-02 (dialogue first-turn hardening) and T-20260330-02 (plugin shell) as the top two next-work candidates. The user chose T-02 first for its better risk/reward profile: *"It has the better risk/reward profile right now: it's unblocked, scoped, and adjacent to the same hardening work we just finished, so the code context is still warm."*

**Stakes:** The fast path vulnerability is a correctness gap, not a runtime bug — it only manifests under replay corruption, which is rare but not impossible. The real value is bringing `_next_turn_sequence()` into alignment with `read()`'s strict integrity invariant, closing a gap where `reply()` could dispatch a turn that `read()` would later reject.

**Success criteria (from ticket T-20260410-02):**
- Empty TurnStore + corruption diagnostics → don't trust fast path
- Regression test: turn 1 succeeds without `read_thread` on healthy path
- Regression test: turn 1 `read_thread` failure not masked by fast path
- Regression test: partial/gapped/inconsistent turn metadata handled
- Error messages distinguish local metadata ambiguity from remote thread-read failure

**Connection to project arc:** T-02 continues the hardening arc that began with T-03 (observability, merged as PR #104 in the prior session). After T-02 closes, the recommended next work is T-20260330-02 (codex-collaboration plugin shell), which unblocks the entire 6-ticket supersession chain.

## Session Narrative

Session opened by loading the prior handoff via `/load`. The handoff described a clean stopping point: S-1 FileFailure refactor merged, PR #104 landed, ticket triage complete, working tree clean on `main`. Two next-work candidates had been identified — T-20260410-02 (dialogue hardening) and T-20260330-02 (plugin shell). The user chose T-02 for its tighter scope and warm code context from the T-03 work.

**Phase 1 — Codebase exploration (~10 min):**

Read the ticket at `docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md` to understand acceptance criteria. Then read the target method `_next_turn_sequence()` at `dialogue.py:725-753`, the `TurnStore` at `turn_store.py:32-82`, the replay infrastructure at `replay.py:1-149`, and the existing fast-path tests at `test_dialogue.py:1840-1910`.

Key finding from exploration: `TurnStore.get_all()` calls `_replay()` which calls `replay_jsonl()` but discards the second return value (`ReplayDiagnostics`). The diagnostics are already computed — just not surfaced to the fast path. The existing `check_health()` method does return diagnostics but requires a separate replay pass.

Also discovered three `get_all()` callers in production code: `_next_turn_sequence()` at `:742`, `recover_startup()` at `:534`, and `read()` at `:834`. This informed the blast-radius analysis for API changes.

**Phase 2 — Approach proposals and first iteration (~10 min):**

Proposed three approaches:
- **A:** Use existing `check_health()` as secondary check when `get_all()` returns empty. Zero TurnStore API changes, double-replays on corruption path.
- **B:** New `get_all_checked()` method returning `(results, diagnostics)` in one pass. Additive API, no existing caller changes.
- **C:** Change `_replay()` to always return diagnostics. Propagate through all methods. Most "correct" but breaks all callers.

Recommended A for its minimal footprint. The user pushed back and chose B with a significant addition: the ticket isn't solved by replay diagnostics alone — it also needs a **controller-side structural check** for gapped/non-contiguous turn metadata.

User's reasoning for B over A: *"A is acceptable as a spike, not as the final shape. It replays the same JSONL twice, splits one logical read into two store calls, and pushes storage-health interpretation into dialogue.py."*

User's reasoning for the structural check: *"The more important case is the 'partial tail': local metadata `{1}`, remote completed turns `2`. That state is contiguous locally, but still inconsistent."*

**Phase 3 — Design refinement through two iterations (~15 min):**

After the first design proposal (v1), the user identified five specific adjustments:

1. **File-global diagnostics contract:** `get_all_checked()` diagnostics are file-global (session-wide JSONL), not collaboration-scoped. Must be explicitly documented as a fail-closed tradeoff.

2. **Contiguity isn't sufficient.** Need a post-`read_thread()` remote/local consistency check: local keys must equal exactly `{1..completed_count}`. Without this, `reply()` can dispatch on a handle that `read()` at `:853` would later reject as an integrity failure.

3. **Policy for non-empty broken state.** Don't just "fall through and continue" — raise a deterministic integrity error before dispatch. The user said: *"Non-empty + gaps / missing tail / extra local turns is different: that is already evidence that local state for this handle is inconsistent."*

4. **Error message precision.** Include diagnostic labels (not just counts), `collaboration_id`, `completed_count`, and `actual_sequences`. Use the repo's error format with causal chaining (`from exc`).

5. **Asymmetry with `recover_startup()`.** Line 535 checks `len(metadata) < completed_count`, which misses gaps (`{1, 3}` with `completed_count=2` has `len==2`). Same invariant should be shared as a reusable function.

Incorporated all five into v2. The user then identified a **material correction** to v2: the Phase 3 consistency table had an "n/a" for empty local metadata after remote read, which left one bad path open — empty metadata + diagnostics + remote says 2 completed should fail the same invariant. The fix: apply `_local_metadata_consistent()` uniformly to ALL non-fast-path states after remote read, including the empty case.

This produced the final simplified rule:
1. Empty + no diagnostics → fast path `return 1`
2. Otherwise → `read_thread()` → compute `completed_count` → `_local_metadata_consistent()` → raise if false → `return completed_count + 1`

User also specified three clarifications for the final spec:
- Error wording: "session turn metadata file has replay diagnostics (...)" not "local turn metadata file is ambiguous" — because diagnostics are session-file-wide
- Handle status on inconsistency: mark "unknown" before raising, consistent with `recover_startup()` quarantine pattern
- Error payload: include `collaboration_id`, `completed_count`, AND `actual_sequences`

**Phase 4 — Spec writing (~5 min):**

Wrote the design spec to `docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md`. Self-reviewed for placeholders, internal consistency, scope, and ambiguity — no issues found. Committed as `d5aa4038`. The user indicated they would review the spec file and share feedback in the next session.

## Decisions

### Decision 1: Approach B (get_all_checked) over A or C

**Choice:** Add a new `get_all_checked()` method to TurnStore returning `(dict[int, int], ReplayDiagnostics)` in a single replay pass.

**Driver:** User stated: *"B is the cleanest additive API. A `get_all_checked()` on turn_store.py keeps existing callers untouched, gives `_next_turn_sequence()` a single-pass view of both metadata and replay state, and lets DialogueController own the trust policy."*

**Alternatives considered:**
- **(A) Secondary `check_health()` call** — recommended initially. User rejected: *"A is acceptable as a spike, not as the final shape. It replays the same JSONL twice, splits one logical read into two store calls, and pushes storage-health interpretation into dialogue.py. It also still leaves the gap case unresolved unless we add more logic anyway."*
- **(C) Change `_replay()` everywhere** — rejected by both: user said *"C is too broad for the problem"*; it would break 3 production callers and 2 test callers of `get_all()` and `get()`.

**Trade-offs:** B adds a new public method to TurnStore, creating a second way to read metadata. The existing `get_all()` remains for callers that don't need diagnostics. This is acceptable because the codebase already has this pattern: `check_health()` exists alongside `_replay()` for the diagnostic case.

**Confidence:** High (E2) — analyzed all three approaches against the 3 production callers and the diagnostic surfacing requirement. B is the only approach that satisfies single-pass, additive API, and zero-impact on existing callers simultaneously.

**Reversibility:** High — remove the method, revert `_next_turn_sequence()`.

**Change trigger:** If a fourth caller needs diagnostics, approach C may become more economical. But for one caller (plus a consistency check reuse in `recover_startup()`), B is right-sized.

### Decision 2: Any diagnostic distrusts fast path (not just has_warnings)

**Choice:** Treat ANY `ReplayDiagnostics` entry (including trailing truncation) as reason to distrust the fast path.

**Driver:** User stated: *"I would not use `has_warnings` as the fast-path gate. I would treat any replay diagnostics on an otherwise-empty result as 'ambiguous, do not trust fast path.' A trailing-truncated final line in replay.py is benign for generic replay, but it is not benign for 'prove this collaboration has never completed turn 1.' That truncated line could be the missing metadata for this exact handle."*

**Alternatives considered:**
- **`has_warnings` only** (non-trailing diagnostics) — initially considered. Rejected because trailing truncation means data existed but was incomplete. For the specific question "has turn 1 completed?", a truncated record is ambiguous, not benign.
- **No diagnostics check** (status quo) — the vulnerability being fixed.

**Trade-offs:** More conservative than `has_warnings`. A truncated line from another collaboration can disable the fast path for this one. This is fail-closed by design — the cost is one `read_thread()` call, which is the normal path for non-first turns.

**Confidence:** High (E2) — the reasoning is sound (trailing truncation IS ambiguous for the "prove zero completed" question) and the cost is negligible.

**Reversibility:** Trivial — change `diagnostics.diagnostics` to `diagnostics.has_warnings` in one condition.

**Change trigger:** If latency analysis shows the extra `read_thread()` calls are measurable in multi-dialogue sessions with benign trailing truncation. Unlikely — trailing truncation is already rare.

### Decision 3: Post-read_thread consistency check with integrity error

**Choice:** After `read_thread()` returns, validate `_local_metadata_consistent(local_turns, completed_count)` — keys must equal exactly `{1..completed_count}`. If false: mark handle "unknown", raise integrity error before dispatch.

**Driver:** User identified the "partial tail" case that contiguity alone misses: local `{1}` with remote completed count 2 is contiguous but inconsistent. *"Without that, `reply()` can continue on a handle that `read()` would later reject as an integrity failure."*

User also specified the error policy: *"empty + diagnostics is a reasonable case for fallback to remote authority. Non-empty + gaps / missing tail / extra local turns is different: that is already evidence that local state for this handle is inconsistent."* And the quarantine behavior: set handle "unknown" before raising, consistent with `recover_startup()`.

**Alternatives considered:**
- **Contiguity check only** (v1 proposal) — rejected because it misses partial tail and extra-local cases. `{1}` with remote 2 is contiguous but `read()` would reject it.
- **Fall through to `read_thread()` silently** — rejected: *"you can silently self-heal bad state or keep dispatching on a dialogue that is already semantically broken."*
- **Raise without quarantine** — rejected: marking "unknown" aligns with existing `recover_startup()` behavior.

**Trade-offs:** The consistency check applies to ALL non-fast-path states, including the empty + diagnostics case after remote read. This means empty metadata + remote says 2 completed → integrity error, even though "self-healing" by just returning 3 would seem harmless. The user explicitly requested this: the invariant is `read()`'s invariant, applied uniformly.

**Confidence:** High (E2) — the invariant matches what `read()` already enforces at `:853-862`, and the user explicitly designed the policy across three iterations.

**Reversibility:** Medium — removing the consistency check would loosen the invariant. The "unknown" quarantine is non-destructive (handle can be reattached after repair).

**Change trigger:** If the consistency check causes false positives in production (e.g., a timing window where `read_thread()` returns a turn that hasn't been locally finalized yet). This would require understanding the write-ordering guarantee more deeply.

### Decision 4: Shared `_local_metadata_consistent()` for both enforcement sites

**Choice:** Extract a single function `_local_metadata_consistent(local_turns, completed_count) -> bool` used by both `_next_turn_sequence()` and `recover_startup()`.

**Driver:** User identified the asymmetry at `recover_startup()` line 535: `len(metadata) < completed_count` misses gaps. *"If the spec says gaps are invalid in `reply()`, then either: reuse the same local-metadata validation in `recover_startup()`, or explicitly accept that startup may reactivate a handle that `reply()` will then reject. I would prefer reuse. It is the same invariant."*

**Alternatives considered:**
- **Inline checks in both sites** — rejected: drift risk between the two sites; the invariant is identical.
- **Accept the asymmetry** — rejected: user explicitly preferred reuse: *"It is the same invariant."*

**Trade-offs:** The `recover_startup()` behavior change is strictly more conservative — it quarantines handles that the old `len < count` check would have allowed through (e.g., `{1, 3}` with `completed_count=2`). This could cause existing dialogues with gap states to be quarantined on session restart instead of being reactivated.

**Confidence:** High (E2) — the invariant is provably the same one `read()` enforces. Sharing it is mechanically correct.

**Reversibility:** High — inline the check back into each site.

**Change trigger:** None foreseeable. The invariant is correct.

### Decision 5: File-global diagnostics (explicit contract)

**Choice:** `get_all_checked()` diagnostics are file-global (session-wide JSONL), not per-collaboration. Document this as a deliberate fail-closed tradeoff.

**Driver:** User stated: *"`get_all_checked()` should explicitly document that its diagnostics are file-global, not collaboration-scoped. The turn store is session-wide JSONL, so one corrupt line from another dialogue can disable the first-turn fast path for this collaboration. That is a valid fail-closed choice, but it is a real blast-radius tradeoff and the spec should say so."*

**Alternatives considered:**
- **Per-collaboration diagnostics** — impossible for unparseable lines (can't determine which collaboration they belong to).
- **Undocumented behavior** — rejected: the blast-radius tradeoff is real and should be explicit.

**Trade-offs:** A corrupt line from collaboration A can cause an extra `read_thread()` call for collaboration B in the same session. Cost: one `read_thread()` call. Benefit: no false negatives on corruption.

**Confidence:** Very high (E3) — the JSONL format makes per-collaboration diagnostics impossible for corrupt lines (by definition, corrupt lines can't be attributed to a collaboration).

**Reversibility:** Medium — would require per-collaboration JSONL files (larger TurnStore refactor, out of scope).

**Change trigger:** If multi-dialogue sessions become common and store corruption causes measurable latency from extra `read_thread()` calls.

### Decision 6: Error wording uses "session turn metadata file" not "local turn metadata file"

**Choice:** Error messages say "session turn metadata file has replay diagnostics" rather than "local turn metadata file is ambiguous."

**Driver:** User clarification: *"Avoid 'local turn metadata file is ambiguous,' because the diagnostics are session-file-wide and may come from another collaboration. Better: 'session turn metadata file has replay diagnostics (...)'"*

**Alternatives considered:**
- "local turn metadata file is ambiguous" (v2 wording) — rejected because it implies the diagnostics are specific to this collaboration.

**Trade-offs:** None — this is a wording improvement with no functional impact.

**Confidence:** High — user specified the wording directly.

**Reversibility:** Trivial — string change.

**Change trigger:** None.

### Decision 7: Handle marked "unknown" on consistency failure, not on remote read failure

**Choice:** When `_local_metadata_consistent()` returns false, mark handle "unknown" before raising. When `read_thread()` fails, raise without changing handle status.

**Driver:** User specified: *"`read_thread()` fails: raise, leave handle status unchanged. `read_thread()` succeeds but `_local_metadata_consistent(...)` is false: set handle to `unknown`, then raise. This aligns better with the existing quarantine behavior in `recover_startup()`."*

**Alternatives considered:**
- **Mark "unknown" on all failures** — rejected because a remote read failure is transient; the local metadata may be fine. Quarantining on a transient remote failure is wrong.
- **Never mark "unknown"** — rejected because confirmed inconsistency is exactly what quarantine is for.

**Trade-offs:** A transient remote failure leaves the handle in its current status. If the handle is "active" but local metadata is actually inconsistent, the inconsistency won't be caught until the next successful `read_thread()`. Acceptable because: (a) the next call to `_next_turn_sequence()` will retry, (b) `recover_startup()` catches it on session restart.

**Confidence:** High (E2) — aligns with existing `recover_startup()` pattern and user's explicit specification.

**Reversibility:** Trivial — add/remove the `update_status` call.

**Change trigger:** None foreseeable.

## Changes

### Commit `d5aa4038` — `docs(spec): dialogue first-turn fast path hardening design`

**`docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md`** (207 lines, new file):

Design spec for T-20260410-02. Covers:
- Problem statement (fast path vulnerability + `recover_startup()` asymmetry)
- `TurnStore.get_all_checked()` method design with file-global diagnostics contract
- Shared `_local_metadata_consistent()` invariant
- Three-phase trust policy for `_next_turn_sequence()`
- Error message shapes for three failure modes
- `recover_startup()` update to use shared invariant
- Test plan (12 tests across 3 files)
- Risk analysis (file-global blast radius, recover_startup behavior change)
- Decision log (7 decisions)

**Status:** Committed to `main`, pending user review. User said: *"I will review the spec and then share my feedback with you in the next session."*

## Codebase Knowledge

### `_next_turn_sequence()` at `dialogue.py:725-753` — the target method

Current two-branch logic:
```
get_all() → if empty: return 1 (fast path)
                else: read_thread() → count completed → return count + 1
```

The fast path trusts `not local_turns` as proof of zero completed turns. But `get_all()` discards `ReplayDiagnostics` — corrupt records produce `{}` indistinguishable from genuinely empty.

Called from `reply()` at `:358`, which uses the result for the `turn_sequence` field in `OperationJournalEntry` (`:389`). An incorrect turn_sequence would corrupt the journal's idempotency key (`:378`).

### `TurnStore` at `turn_store.py:32-82` — session-scoped JSONL metadata store

- Per-session storage: `plugin_data_path / "turns" / session_id / "turn_metadata.jsonl"`
- `get_all(collaboration_id)` at `:63` — replays JSONL, filters by collaboration_id prefix, returns `{turn_sequence: context_size}`
- `_replay()` at `:78` — calls `replay_jsonl()`, discards diagnostics
- `check_health()` at `:73` — calls `replay_jsonl()`, discards results, returns diagnostics
- Both `_replay()` and `check_health()` call `replay_jsonl` but discard opposite halves of the result

Three production callers of `get_all()`:
| Caller | Line | Purpose |
|--------|------|---------|
| `_next_turn_sequence()` | `:742` | Fast path check |
| `recover_startup()` | `:534` | Metadata completeness check |
| `read()` | `:834` | Left-join for context_size enrichment |

### `replay_jsonl()` at `replay.py:56-149` — shared replay infrastructure

Returns `tuple[tuple[T, ...], ReplayDiagnostics]`. Single-pass with deferred trailing-truncation classification. Classifies each issue as:
- `trailing_truncation` — last line(s) with invalid JSON, no valid JSON follows
- `mid_file_corruption` — invalid JSON with valid JSON after it
- `schema_violation` — valid JSON but wrong/missing fields
- `unknown_operation` — valid record but unrecognized operation type

`ReplayDiagnostics.has_warnings` at `:51-53` returns True if any non-trailing diagnostic exists. The design spec explicitly chose to NOT use `has_warnings` — any diagnostic distrusts the fast path.

### `read()` at `dialogue.py:812-874` — the integrity reference

Performs a strict left-join: for every completed turn from `read_thread()`, the TurnStore MUST have a metadata entry. Missing entry → `RuntimeError` at `:856-862`:
```
"Turn metadata integrity failure: no context_size for
collaboration_id=..., turn_sequence=... This indicates a
write-ordering violation or missing recovery repair."
```

This is the invariant that `_next_turn_sequence()` and `recover_startup()` should also enforce. Currently only `read()` enforces it.

### `recover_startup()` at `dialogue.py:490-555` — the asymmetry site

Checks metadata completeness at `:533-539`:
```python
if completed_count > 0:
    metadata = self._turn_store.get_all(handle.collaboration_id)
    if len(metadata) < completed_count:
        self._lineage_store.update_status(collaboration_id, "unknown")
        continue
```

`len(metadata) < completed_count` catches "fewer entries than expected" but misses gaps. Example: `{1, 3}` with `completed_count=2` has `len==2`, passes the check, but `read()` would reject because it expects keys `{1, 2}`.

### Existing fast-path tests at `test_dialogue.py:1839-1910`

Two existing tests in `TestFirstReplyFastPath`:
- `test_first_reply_skips_read_thread` (`:1842`) — proves empty TurnStore → `turn_sequence=1` without `read_thread` call. Uses `TrackingSession` with `read_thread_calls` counter.
- `test_second_reply_uses_read_thread` (`:1873`) — proves after one completed turn, `read_thread` IS called. Asserts `read_thread_calls == 1`.

These verify the current two-branch logic. The design adds ~9 new tests for the expanded trust policy.

### Test helper `_build_dialogue_stack()` at `test_dialogue.py:26-60`

Factory wiring a full dialogue stack with test doubles:
```python
def _build_dialogue_stack(
    tmp_path, *, session=None, session_id="sess-1"
) -> tuple[DialogueController, ControlPlane, LineageStore, OperationJournal, TurnStore]:
```

Returns all 5 components. Uses `FakeRuntimeSession` from `test_control_plane.py`. The `TurnStore` is returned as the 5th element, which is needed for the new tests that pre-populate corrupt/gapped metadata.

### Files read this session

| File | Lines read | Why | Key findings |
|------|-----------|-----|--------------|
| `dialogue.py:340-390` | 50 | `reply()` context for `_next_turn_sequence()` call | Turn sequence used in idempotency key at `:378` |
| `dialogue.py:490-555` | 65 | `recover_startup()` completeness check | `len(metadata) < completed_count` misses gaps |
| `dialogue.py:725-810` | 85 | `_next_turn_sequence()` + `_best_effort_repair_turn()` | Two-branch logic, `read_thread` count pattern |
| `dialogue.py:825-875` | 50 | `read()` integrity check | Strict left-join, `RuntimeError` on missing metadata |
| `turn_store.py:1-82` | 82 | Full TurnStore class | Per-session JSONL, `_replay()` discards diagnostics |
| `replay.py:1-149` | 149 | Full replay infrastructure | `ReplayDiagnostics`, classification labels, `has_warnings` |
| `test_dialogue.py:1-120` | 120 | Test helpers, `_build_dialogue_stack()`, imports | Factory pattern, `FakeRuntimeSession` |
| `test_dialogue.py:1840-1910` | 70 | Existing fast-path tests | `TrackingSession`, call-count assertions |
| T-02 ticket | 39 | Acceptance criteria | 5 ACs, PR #101 source, deferred status |
| Prior handoff (archived) | ~586 | Session resume context | Clean stopping point, next-work candidates |

## Context

### Branch and repository state

- **Branch:** `main` (no feature branch created yet — design phase only)
- **HEAD commit:** `d5aa4038` (design spec commit)
- **Origin:** spec commit on main (committed directly since it's a doc, not code)
- **Working tree:** clean

### Test baseline

- **546 tests passing** (verified in prior session, no code changes this session)
- Ruff clean on all production files

### Mental model

**Invariant unification problem.** `read()` already enforces a strict invariant: every completed turn must have metadata. `_next_turn_sequence()` and `recover_startup()` are two other enforcement sites that should enforce the same invariant but currently don't — they use weaker checks (emptiness for `_next_turn_sequence`, length for `recover_startup`). The design extracts the invariant into a shared function and applies it uniformly.

The trust policy in `_next_turn_sequence()` follows a classic "trust but verify" pattern with an optimization: trust empty + clean (fast path), verify everything else against the remote.

### Environment state

- macOS Darwin 25.3.0
- Python 3.14.2
- `uv` for all Python tool invocations
- Working directory: `/Users/jp/Projects/active/claude-code-tool-dev`

## Learnings

### File-global JSONL diagnostics are a deliberate blast-radius tradeoff

**Mechanism:** TurnStore uses a session-wide JSONL file. `replay_jsonl()` processes the entire file and returns diagnostics for all records, not just those matching the requested `collaboration_id`. Corrupt records from one collaboration appear in the diagnostics for all collaborations in the same session.

**Evidence:** `turn_store.py:36-38` shows the store path is `plugin_data_path / "turns" / session_id / "turn_metadata.jsonl"` — one file per session, not per collaboration. `replay_jsonl()` at `replay.py:77-78` iterates all lines.

**Implication:** For the fast-path check, this is fail-closed by design. A corrupt line from collaboration A can cause an extra `read_thread()` call for collaboration B. The cost is one `read_thread()` call (the normal path for non-first turns). Per-collaboration diagnostics would require per-collaboration JSONL files — a larger refactor.

**Watch for:** If multi-dialogue sessions become common and store corruption causes measurable latency, per-collaboration JSONL is the mitigation path.

### NamedTuple's tuple compatibility was the right pattern — and this session's TurnStore work is its natural successor

**Mechanism:** The prior session's S-1 refactor used NamedTuple's tuple compatibility to upgrade bare `(Path, str)` tuples to named fields without breaking iteration patterns. This session's design uses the same "additive, non-breaking" philosophy: `get_all_checked()` adds a new method rather than changing `get_all()`, and `_local_metadata_consistent()` adds a new function rather than changing `recover_startup()` inline.

**Evidence:** Three `get_all()` callers (`:534, :742, :834`) would need updating under Approach C. Approach B leaves them untouched — same pattern as NamedTuple leaving iteration/comparison patterns untouched.

**Implication:** This codebase consistently prefers additive APIs over breaking changes. Future hardening should follow the same pattern: new methods/functions, existing signatures unchanged.

### `len(metadata) < completed_count` is a subtly wrong invariant check

**Mechanism:** `recover_startup()` at `:535` checks `len(metadata) < completed_count`. This catches "fewer entries than expected" but misses gaps where `len` equals the expected count but keys don't match. Example: `{1, 3}` with `completed_count=2` has `len==2`, passes the check.

**Evidence:** `read()` at `:854` uses a per-turn existence check (`context_size = metadata.get(seq)` → raise if None), which catches gaps. The shared `_local_metadata_consistent()` checks `set(keys) == set(range(1, completed_count + 1))`, which also catches gaps.

**Implication:** When checking structural properties of keyed collections, check key identity, not just cardinality. `len(d) == n` does not imply `d.keys() == expected_keys`.

**Watch for:** Other places in the codebase that use length checks as proxies for structural checks.

### User iterates designs through specific corrections, not open-ended feedback

**Mechanism:** Across three design iterations (v1 → v2 → final), the user's feedback was structured as numbered corrections with specific code references and exact wording changes. The corrections built on each other: v1 feedback added structural checks, v2 feedback unified the invariant and fixed the empty-case gap.

**Evidence:** The user's v1 feedback had 1 main nuance ("contiguity is not sufficient") and 5 sub-points. The v2 feedback had 1 material correction and 3 clarifications. Each correction included a code reference (e.g., `dialogue.py:725`, `dialogue.py:853`).

**Implication:** Present designs in structured form (tables, numbered items, explicit assumptions) so corrections can be precise. Avoid prose-heavy descriptions that are hard to correct incrementally.

## Next Steps

### 1. User reviews design spec, shares feedback

**Dependencies:** None — async review by user.

**What to read:** `docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md` — the committed spec.

**Expected outcomes:** User may approve as-is, request changes, or identify gaps. The spec has been through three design iterations and addresses all five of the user's specific corrections, so major structural changes are unlikely. Clarifications or edge-case additions are possible.

**Next action after review:** Incorporate any feedback, then invoke `writing-plans` skill to create implementation plan.

### 2. Create implementation plan (after spec approval)

**Dependencies:** Spec approval from step 1.

**What to read:** The approved spec, plus `dialogue.py:725-753` and `turn_store.py:63-81` (the implementation targets).

**Approach suggestion:** The spec's test plan maps directly to implementation steps. Natural build order:
1. `get_all_checked()` on TurnStore (self-contained, testable independently)
2. `_local_metadata_consistent()` function (pure logic, no dependencies)
3. `_next_turn_sequence()` rewrite (depends on 1 and 2)
4. `recover_startup()` update (depends on 2)
5. Tests for all of the above

**Potential obstacles:** The feature branch needs to be created from `main`. The ticket's `branch:` field is stale (`feature/b4-agent-skill-harness-assembly`). Use something like `fix/t02-dialogue-first-turn-hardening`.

### 3. (After T-02) Begin T-20260330-02 planning

**Dependencies:** T-02 closed.

**What to read:** `docs/tickets/2026-03-30-codex-collaboration-plugin-shell-and-consult-parity.md` for the full ticket. This is the root blocker for the 6-ticket supersession chain.

**Approach suggestion:** Start with a planning session before implementation. The supersession plan may need updating given D-prime's completion and the shim being kept. User confirmed in the prior session that codex-collaboration is still the intended successor.

## In Progress

**Clean stopping point — design phase complete, no code in flight.**

- Design spec written and committed (`d5aa4038`)
- Spec pending user review
- No feature branch created (will be created when implementation starts)
- No code changes made this session
- Implementation planning blocked on spec approval

## Open Questions

### 1. Are there edge cases in the timing window between turn dispatch and metadata write?

**Context:** The consistency check validates `local_keys == {1..completed_count}` after `read_thread()` returns. But there's a window between when `run_turn()` completes (remote says N completed) and when `TurnStore.write()` persists the metadata. If `_next_turn_sequence()` runs during this window (e.g., concurrent `reply()` calls), the check would fail because the latest turn's metadata hasn't been written yet.

**Mitigated by:** The spec mentions serialized dispatch for the R1/R2 rollout posture (comment at `dialogue.py:356-357`). But if dispatch serialization changes, this edge case becomes real.

**Impact:** Could cause false-positive integrity errors on valid state.

### 2. Should the test for "empty + diagnostics + remote 0 completed" assert turn_sequence == 1?

**Context:** When local is empty, diagnostics are present, but remote confirms 0 completed turns, `_local_metadata_consistent({}, 0) == True` → returns `completed_count + 1 = 1`. This is correct. But it means the consistency check "self-heals" the suspicious empty state by confirming with the remote. Is this the intended behavior, or should empty + diagnostics always raise regardless of remote state?

**Current spec says:** It's consistent (returns 1). The diagnostics caused us to check the remote, and the remote confirmed no turns — the right answer.

**Impact:** None if spec is correct. Worth confirming during implementation.

## Risks

### 1. Spec committed to main directly

**Impact:** The design spec was committed directly to `main` rather than on a feature branch. This is consistent with doc-only changes (no code, no tests), but differs from the branch-protection workflow used for code changes.

**Mitigation:** If the spec needs revision after user review, amendments can be committed directly to `main` (still doc-only) or on the feature branch when implementation starts.

### 2. recover_startup() behavior change is strictly more conservative

**Impact:** The updated `_local_metadata_consistent()` check will quarantine handles that the old `len < count` check allowed through. Existing dialogues with gap states (e.g., `{1, 3}` with `completed_count=2`) will be quarantined on session restart instead of being reactivated.

**Mitigation:** The quarantine is non-destructive — handle becomes "unknown", eligible for reattach after repair. And gap states are already evidence of corruption, so quarantining them is correct.

### 3. File-global diagnostic blast radius

**Impact:** A corrupt line from collaboration A can cause an extra `read_thread()` call for collaboration B in the same session.

**Mitigation:** The cost is one `read_thread()` call per affected collaboration — negligible. And per-collaboration diagnostics are impossible for unparseable lines.

## References

**Commits this session:**
- `d5aa4038` — docs(spec): dialogue first-turn fast path hardening design

**Spec:**
- `docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md`

**Ticket:**
- T-20260410-02: `docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md`

**Handoffs:**
- Prior: `docs/handoffs/archive/2026-04-12_00-52_s1-refactor-pr-merge-ticket-triage.md`
- This: `docs/handoffs/2026-04-12_01-42_t02-fast-path-hardening-design-approved.md`

**Key source files:**
- `packages/plugins/codex-collaboration/server/dialogue.py` — target: `:725-753` (`_next_turn_sequence`), `:534-539` (`recover_startup` check), `:853-862` (`read()` integrity reference)
- `packages/plugins/codex-collaboration/server/turn_store.py` — target: new `get_all_checked()` method
- `packages/plugins/codex-collaboration/server/replay.py` — `ReplayDiagnostics` at `:44-53`
- `packages/plugins/codex-collaboration/tests/test_dialogue.py` — existing fast-path tests at `:1840-1910`

## Gotchas

### TurnStore `_replay()` and `check_health()` discard opposite halves of the same result

**Symptom:** You might think `check_health()` is a lightweight probe. It's not — it replays the entire JSONL file, same as `_replay()`.

**Root cause:** `replay_jsonl()` returns `(results, diagnostics)`. `_replay()` keeps results, discards diagnostics. `check_health()` keeps diagnostics, discards results. Both do the same IO work.

**Mitigation:** The new `get_all_checked()` returns both in one pass. Use it when you need diagnostics alongside results.

**Discovered when:** Evaluating Approach A (secondary `check_health()` call) — realized it would double-replay the file.

### `len(dict) == expected_count` does not mean `dict.keys() == expected_keys`

**Symptom:** `recover_startup()` passes the completeness check despite gap states.

**Root cause:** `len({1: a, 3: b}) == 2` is True even though keys `{1, 3}` don't equal `{1, 2}`. Length checks are cardinality checks, not identity checks.

**Mitigation:** The shared `_local_metadata_consistent()` uses `set(keys) == set(range(1, n+1))` — an identity check.

**Discovered when:** User identified the asymmetry between `recover_startup()` and `read()`'s invariants during v1 design review.

### Ticket T-20260410-02 branch field is stale

**Symptom:** Ticket says `branch: feature/b4-agent-skill-harness-assembly` — that branch doesn't exist and is from a different work stream.

**Root cause:** The ticket was filed during PR #101 review, which was on a different branch. The branch field was never updated.

**Mitigation:** Create a new branch when implementation starts (e.g., `fix/t02-dialogue-first-turn-hardening`). Update the ticket's branch field.

**Discovered when:** Reading the ticket during initial exploration.

## Conversation Highlights

### User's structured correction style

The user provides feedback as numbered corrections with specific code references. The v1 feedback had 5 numbered points, each with a file reference and exact reasoning. The v2 feedback had 1 material correction and 3 clarifications, again with code references.

Example of the correction precision:
> "After a successful remote `read_thread()`, we should validate **all** local states against `completed_count`, including the empty case. The Phase 3 table in the current draft still treats empty local metadata as 'n/a,' and that leaves one bad path open..."

This correction was followed by the exact bad state (empty local, diagnostics present, remote 2 completed) and the simplified rule that fixes it.

### User's "material correction" framing

The user distinguishes between "material corrections" and "clarifications" in their feedback. The Phase 3 empty-case gap was framed as a **material correction** (changes behavior), while error wording and handle status were framed as **clarifications** (refine the spec without changing behavior). This framing helps prioritize attention during iteration.

### User's design authority pattern

The user doesn't just evaluate proposals — they reshape them. The initial proposal was Approach A; the user chose B and added the structural check. The initial consistency check was contiguity-only; the user added the post-remote validation. The initial error wording was "ambiguous"; the user specified "session turn metadata file has replay diagnostics."

Each iteration tightened the design. The user operates as the design authority, with Claude proposing and the user refining to the final shape.

### User's explicit deferral strategy

When choosing between T-02 and T-20260330-02, the user explicitly stated the sequencing rationale:
> "I would do T-20260330-02 immediately after T-20260410-02 is closed. T-20260330-02 is strategically important, but it's broader and will need substantial planning and discussion before implementation."

The pattern: sequence quick wins before strategic work, but name the strategic work explicitly so it's not lost.

## User Preferences

**Design iteration style (confirmed this session):**
The user iterates through numbered corrections with code references. They distinguish "material corrections" from "clarifications." Present designs in structured form (tables, numbered items) to enable precise corrections.

**Approach selection authority (confirmed this session):**
The user reshapes proposals rather than choosing from the menu. The initial recommendation (A) was overridden with a modified B. Future proposals should present options as starting points, not final candidates.

**Invariant unification preference (new this session):**
User strongly prefers shared functions for shared invariants: *"It is the same invariant."* When the same check appears in multiple sites, extract it. Don't inline and risk drift.

**Fail-closed over fail-open for safety checks (confirmed this session):**
Any diagnostic distrusts the fast path, not just `has_warnings`. User: *"A trailing-truncated final line... is benign for generic replay, but it is not benign for 'prove this collaboration has never completed turn 1.'"*

**Quarantine consistency (new this session):**
When a handle is confirmed inconsistent, mark it "unknown" before raising. Aligns with `recover_startup()` pattern. Don't leave handles in stale states.

**Error message precision (confirmed this session):**
Include diagnostic labels, not counts. Include all relevant identifiers (`collaboration_id`, `completed_count`, `actual_sequences`). Use "session turn metadata file" not "local turn metadata file."

**Spec review as async gate (new this session):**
User explicitly chose to review the spec file before proceeding to implementation planning: *"I will review the spec and then share my feedback with you in the next session."* Don't skip the review gate.
