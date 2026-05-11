---
date: 2026-04-12
time: "23:45"
created_at: "2026-04-13T03:45:48Z"
session_id: 1f3aca14-8a9b-4de0-bffe-0ac3b04a8fec
resumed_from: docs/handoffs/archive/2026-04-12_01-42_t02-fast-path-hardening-design-approved.md
project: claude-code-tool-dev
branch: fix/t02-dialogue-first-turn-hardening
commit: d5aa4038
title: T-02 spec revised (3 findings), contracts.md updated, implementation plan written
type: handoff
files:
  - docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/plans/2026-04-12-dialogue-first-turn-fast-path-hardening.md
  - packages/plugins/codex-collaboration/server/dialogue.py
  - packages/plugins/codex-collaboration/server/turn_store.py
  - packages/plugins/codex-collaboration/tests/test_dialogue.py
  - packages/plugins/codex-collaboration/tests/test_turn_store.py
---

# T-02 Spec Revised (3 Findings), Contracts.md Updated, Implementation Plan Written

## Goal

Revise the dialogue first-turn fast path hardening design spec based on user review feedback, then produce an implementation plan ready for execution.

**Trigger:** Prior session wrote the initial spec (`d5aa4038`) and the user took it offline for review. This session opened by loading the prior handoff and receiving three structured findings from the user's review.

**Stakes:** The spec governs correctness for `_next_turn_sequence()` — the turn-sequence derivation path used by `reply()`. An incorrect invariant would either quarantine valid handles (false positives) or allow dispatch on broken state (false negatives). The findings exposed a real coherence gap: the spec's "shared invariant" claim was not true.

**Success criteria:** (1) All three user findings addressed with coherent spec changes, (2) crash-recovery contract updated to match, (3) implementation plan written with complete code in every step. All three met.

**Connection to project arc:** T-02 continues the dialogue hardening arc (T-03 observability merged as PR #104). After T-02 closes, next work is T-20260330-02 (codex-collaboration plugin shell), which unblocks the 6-ticket supersession chain.

## Session Narrative

Session opened by loading two handoffs from the prior session via `/load`. The `01-42` handoff (spec-writing session) was already in the archive; the `01-40` handoff (design-review session) was in the active directory. Both were archived and the state file created.

The user immediately presented three findings from their offline spec review, structured as `::code-comment` annotations with priority, confidence, and exact line references.

**Phase 1 — Analyzing the three findings (~5 min):**

Read the spec at `docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md` to verify each finding against the actual text. Then read the three reference points in the codebase:
- `dialogue.py:495-555` — `recover_startup()` and the session-ID stability docstring
- `dialogue.py:845-875` — `read()` integrity enforcement
- `contracts.md:148-167` — crash recovery contract

All three findings confirmed:

1. **P2: Path-mismatch overclaim.** The spec's problem statement listed "path mismatches" as a case the design hardens against, but the mechanism can't detect them. A wrong `session_id` produces a clean empty store with zero diagnostics — Phase 1 returns `1`, same as today. The code explicitly documents session-ID stability as an external contract at `dialogue.py:502-505`.

2. **P1: Exact-key invariant diverges from `read()`.** The spec claimed `_local_metadata_consistent()` "encodes the invariant that `read()` already enforces via its strict left-join." But `read()` at `:853-862` only rejects **missing** keys (iterates completed remote turns, checks `metadata.get(seq)`). It accepts extra local keys. The spec's `set(keys) == set(range(1, N+1))` rejects extra keys — a stricter invariant than any existing enforcement site.

3. **P1: `recover_startup()` skips zero-turn case.** The spec's Section 5 replaces the predicate at the existing `if completed_count > 0:` site, so a handle with `completed_count == 0` and stale local metadata never hits the check. Startup would reattach, and the next `reply()` would immediately quarantine.

**Phase 2 — Invariant choice: A vs B (~5 min):**

Presented two paths for the P1 invariant divergence:
- **(A) Relax to prefix-completeness:** `set(range(1, N+1)).issubset(keys)`. Matches `read()` and the contract.
- **(B) Tighten all three sites to exact equality:** Update `read()` and the contract too.

Initially justified A partly on "write-ordering windows" producing extra keys — the user pushed back on this rationale. User's reasoning: `_finalize_confirmed_turn()` at `dialogue.py:206` writes metadata only after turn confirmation, so the ordinary success path doesn't produce extra-local state. The stronger justification is contract alignment: A matches `read()` and `contracts.md` as they exist today.

User chose A with precise framing: *"A is the right default for this ticket... justify it as 'aligned with existing contract and sufficient for turn-sequence safety,' not as 'extra keys are definitely benign.'"* They also noted that extra keys, while not blocking derivation, are still anomalous and may deserve logging.

**Phase 3 — First revision round (~10 min):**

Created the feature branch `fix/t02-dialogue-first-turn-hardening` and made all spec changes:
- Removed "path mismatches" from origin, added `## Preconditions` section
- Renamed helper to `_local_metadata_complete_for_completed_turns()`, changed from `==` to `.issubset()`
- Updated consistency table: `{1, 2, 3}` vs remote 2 is now "Yes" (prefix-complete)
- Updated `recover_startup()` section: moved check outside `if completed_count > 0:` guard
- Updated error messages from "Expected" to "Required"
- Updated decision log and risk sections
- Added `logger.warning()` for extra-local keys
- Updated `contracts.md:156-158` with "AND no stale local TurnStore metadata"

**Phase 4 — Second scrutiny round (~5 min):**

User applied a second scrutiny pass and found two remaining issues:

1. **Contract text ambiguity.** The two-branch eligibility rule in `contracts.md` could still be read to allow zero-turn stale metadata via the second branch. The required key set `{1..completed_count}` is vacuously empty when `completed_count == 0`, so "all present" is trivially true. An implementer could bypass the zero-turn tightening by reading the second clause.

2. **Logger mismatch.** The spec used `logger.warning()` but the package has no Python `logging` module — it uses `print(..., file=sys.stderr)` via dedicated helpers like `_log_recovery_failure` at `dialogue.py:63-67`.

Both findings confirmed by checking the code:
- Grepped for `logger\.|logging\.|sys\.stderr|print\(|_log_` in the server directory — found only `print(f"codex-collaboration: ...", file=sys.stderr)` patterns
- Read `_log_recovery_failure` at `dialogue.py:63-67` to confirm the exact pattern

**Phase 5 — Second revision round (~5 min):**

Made two targeted fixes:
- Rewrote `contracts.md:156-158` from OR-branches to explicit if/else on `completed_count`. Zero-turn stale metadata is now explicitly ineligible; the second branch only applies when `completed_count > 0`.
- Replaced `logger.warning()` with `print(..., file=sys.stderr)` matching the package's existing pattern. Test assertion via `capsys.readouterr().err`.
- Tightened headline wording at spec line 3 to not claim `read()` already enforces the zero-turn half.

**Phase 6 — Implementation plan (~15 min):**

User said "Proceed to implementation planning." Invoked the `writing-plans` skill. Read all target files to write exact code:
- `turn_store.py` (82 lines) — full class, `_replay()` internals, `replay_jsonl` call pattern
- `replay.py` (149 lines) — `ReplayDiagnostics` type, diagnostic classification
- `dialogue.py:725-753` — current `_next_turn_sequence()` 
- `dialogue.py:520-558` — current `recover_startup()` metadata check
- `test_turn_store.py` (161 lines) — existing test patterns, store path construction
- `test_dialogue.py:0-70` — imports, `_build_dialogue_stack()` factory
- `test_dialogue.py:1835-1955` — existing `TestFirstTurnFastPath` and `TestRecoveryOutcomeEmission`
- `test_control_plane.py:95-149` — `FakeRuntimeSession.read_thread()` behavior

Wrote 6-task plan to `docs/superpowers/plans/2026-04-12-dialogue-first-turn-fast-path-hardening.md`:
1. `TurnStore.get_all_checked()` — test and implement
2. `_local_metadata_complete_for_completed_turns()` — helper function
3. `_next_turn_sequence()` rewrite — three-phase trust policy
4. `_next_turn_sequence()` hardening tests (8 new tests)
5. `recover_startup()` restructure + recovery tests (2 new tests)
6. Final verification and lint

Self-reviewed for spec coverage, placeholder scan, and type consistency — no issues found.

User chose to save a handoff: *"I will review the implementation plan and then share my findings with you in the next session."*

## Decisions

### Decision 1: Prefix-completeness (A) over exact-key equality (B)

**Choice:** Relax the shared helper to prefix-completeness: `set(range(1, completed_count + 1)).issubset(local_turns.keys())`. Extra local keys beyond `completed_count` are not rejected.

**Driver:** User stated: *"A is the right default for this ticket... The strongest reason is not 'extra keys are harmless noise,' it is that A matches the system's current contract and enforcement surface."* `read()` at `dialogue.py:853-862` only rejects missing keys. `contracts.md:156-158` requires "complete TurnStore metadata for every completed turn" — a one-way rule.

**Alternatives considered:**
- **(B) Exact-key equality** — `set(keys) == set(range(1, N+1))`. Would reject extra keys. User rejected: *"B is only defensible if you want to deliberately tighten the product invariant to exact remote/local parity. That is a broader policy change than T-02 currently claims."*

**Trade-offs:** Extra local keys pass without blocking derivation. The next `reply()` reuses that sequence number and overwrites the stale slot, destroying evidence. Mitigated by adding a stderr diagnostic (see Decision 3).

**Confidence:** High (E2) — verified against `read()` enforcement at `dialogue.py:853-862` and the crash-recovery contract at `contracts.md:156-158`.

**Reversibility:** High — change `.issubset()` to `==` and update `read()` and the contract.

**Change trigger:** If the project explicitly decides to tighten to exact remote/local parity as a broader policy change. User: *"B is viable only as an explicit follow-on tightening."*

### Decision 2: Zero-turn stale metadata is a deliberate tightening, not alignment

**Choice:** When `completed_count == 0`, `_local_metadata_complete_for_completed_turns()` returns `not local_turns` — rejects any stale local metadata. This is explicitly labeled as a tightening beyond `read()` and the prior crash-recovery contract.

**Driver:** User identified that the original spec framed this as "matching existing policy" when it was actually extending it. User stated: *"The zero-turn fix is still presented as alignment with `read()` and the crash-recovery contract, but it is not."* Also: *"Either update the spec and contracts.md to say zero-turn stale metadata is a deliberate tightening, or back that rule out."*

**Alternatives considered:**
- **Back out the zero-turn check** — make `completed_count == 0` unconditionally pass. Rejected because stale local metadata with zero completed remote turns is genuinely anomalous — startup would reattach, and the next `reply()` would immediately quarantine.
- **Present it as alignment** — the original framing. User explicitly rejected this as inaccurate.

**Trade-offs:** The crash-recovery contract (`contracts.md`) has been updated, so this is now documented policy. But the tightening means zero-turn handles with stale metadata are no longer eligible for recovery reattach — a real behavior change.

**Confidence:** High (E2) — user reviewed the contract text twice and confirmed the final wording is unambiguous.

**Reversibility:** Medium — would need to update the contract, the helper, and both enforcement sites.

**Change trigger:** If legitimate stale local metadata for zero-turn handles can occur in production (e.g., from a race condition in handle creation). Currently no known path produces this state.

### Decision 3: Stderr diagnostic for extra-local anomaly, not logger.warning

**Choice:** Emit `print(f"codex-collaboration: _next_turn_sequence anomaly: ...", file=sys.stderr)` when prefix-complete but `len(local_turns) > completed_count`. Test via `capsys.readouterr().err`.

**Driver:** User identified two concerns: (1) extra-local keys should have observability, and (2) the mechanism must match the package's existing pattern. User stated on observability: *"Extra local keys are safe to tolerate without any observability... The next successful turn will reuse that sequence and overwrite the stale local slot, which makes derivation safe but destroys evidence."*

On mechanism: *"This package does not otherwise use [Python logging]... the implementation either introduces a new logger pattern ad hoc, or relies on Python fallback logging behavior."*

**Alternatives considered:**
- **`logger.warning()`** — initially proposed. User rejected: introduces a new dependency pattern in a package that uses `print(..., file=sys.stderr)` exclusively. See `_log_recovery_failure` at `dialogue.py:63-67` and `_log_local_append_failure` at `control_plane.py:46-49`.
- **No observability** — rejected because the next `reply()` overwrites the stale slot, destroying the forensic signal.

**Trade-offs:** Stderr diagnostics are less structured than Python logging (no log levels, no handlers). Acceptable because the package consistently uses this pattern and tests already assert via `capsys`.

**Confidence:** High (E2) — confirmed by grepping `server/` for all logging patterns.

**Reversibility:** Trivial — change `print()` to `logger.warning()` if the package adopts logging.

**Change trigger:** If the package introduces Python `logging` module for other purposes.

### Decision 4: Contract text rewritten as explicit if/else on completed_count

**Choice:** Rewrote `contracts.md:156-158` from OR-branches (`zero completed turns OR complete metadata`) to explicit if/else: `if completed_count == 0: no stale metadata; if completed_count > 0: prefix-complete`.

**Driver:** User's second scrutiny found that the original revision's OR-branches could still be read to allow zero-turn stale metadata via the second branch (vacuously true). User stated: *"An implementer or future reviewer can reasonably treat the second clause as satisfied for `completed_count == 0` because the required key set is empty."*

**Alternatives considered:**
- **Keep OR-branches with a clarifying note** — rejected because the ambiguity is structural, not just unclear. An explicit if/else eliminates the vacuous-truth bypass entirely.

**Trade-offs:** The if/else is slightly more verbose than the original OR form. Worth it for unambiguity.

**Confidence:** Very high (E3) — the vacuous-truth issue is a logical property of the prior text, not an interpretation question.

**Reversibility:** Trivial — rewrite the clause.

**Change trigger:** None foreseeable.

## Changes

### Spec: `docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md`

**Not yet committed** — file modified on branch `fix/t02-dialogue-first-turn-hardening`.

Changes across two revision rounds:

**Round 1 (3 user findings):**
- Removed "path mismatches" from origin (line 7)
- Added `## Preconditions` section documenting session-ID stability as external contract
- Renamed helper from `_local_metadata_consistent()` to `_local_metadata_complete_for_completed_turns()`
- Changed invariant from exact equality (`==`) to prefix-completeness (`.issubset()`)
- Updated docstring to distinguish `completed_count > 0` (alignment) from `completed_count == 0` (tightening)
- Updated consistency table: `{1, 2, 3}` vs remote 2 changed from "No" to "Yes"
- Updated error messages from "Expected" to "Required"
- Updated `recover_startup()` section: moved check outside `if completed_count > 0:` guard
- Added zero-turn stale metadata test to test plan
- Updated decision log entry 6 to say "prefix-completeness"
- Updated risk section for expanded `recover_startup()` scope
- Updated "Unchanged" section to accurately describe `read()` relationship

**Round 2 (2 scrutiny findings):**
- Tightened headline (line 3) to distinguish alignment from tightening
- Replaced `logger.warning()` with `print(..., file=sys.stderr)` matching package pattern
- Updated extra-local test to assert via `capsys.readouterr().err`
- Added file-global blast radius test for unrelated-collaboration corruption
- Labeled zero-turn check as "deliberate tightening" in Sections 2 and 5

### Contract: `docs/superpowers/specs/codex-collaboration/contracts.md`

**Not yet committed** — modified on branch `fix/t02-dialogue-first-turn-hardening`.

Rewrote crash-recovery eligibility clause at lines 156-158:

Before (OR-branches):
```
- zero completed turns, OR
- complete TurnStore metadata for every completed turn
```

After (explicit if/else):
```
- if completed_count == 0: the TurnStore must have no metadata for this collaboration
- if completed_count > 0: metadata keys {1, 2, ..., completed_count} must all be present
```

### Plan: `docs/superpowers/plans/2026-04-12-dialogue-first-turn-fast-path-hardening.md`

**New file** on branch `fix/t02-dialogue-first-turn-hardening`. 6 tasks, ~788 lines, complete code in every step:
1. `TurnStore.get_all_checked()` — 3 tests + implementation
2. `_local_metadata_complete_for_completed_turns()` — helper function
3. `_next_turn_sequence()` rewrite — three-phase trust policy
4. 8 new `_next_turn_sequence()` tests
5. `recover_startup()` restructure + 2 recovery tests
6. Final verification and lint

## Codebase Knowledge

### Files read and why

| File | Lines read | Why | Key findings |
|------|-----------|-----|--------------|
| `dialogue.py:495-555` | 60 | Verify `recover_startup()` guard structure | `if completed_count > 0:` at `:533` skips zero-turn case. Session-ID stability documented as external contract at `:502-505` |
| `dialogue.py:845-875` | 30 | Verify `read()` integrity enforcement | Only rejects **missing** keys via `metadata.get(seq)` at `:854`. Does NOT reject extra keys |
| `dialogue.py:0-15` | 15 | Check imports | `sys` already imported — no new import needed for stderr pattern |
| `dialogue.py:57-67` | 10 | Check existing stderr pattern | `_log_recovery_failure` uses `print(f"codex-collaboration: ...", file=sys.stderr)` |
| `dialogue.py:720-810` | 90 | Current `_next_turn_sequence()` and `_best_effort_repair_turn()` | Two-branch logic, method signature, `runtime.session.read_thread()` call pattern |
| `contracts.md:148-167` | 20 | Verify crash-recovery eligibility wording | OR-branches allowed vacuous-truth bypass of zero-turn tightening |
| `turn_store.py:1-82` | 82 | Full file for implementation plan | `_replay()` discards diagnostics, `check_health()` discards results, `replay_jsonl` returns `(tuple[T, ...], ReplayDiagnostics)` |
| `replay.py:1-149` | 149 | `ReplayDiagnostics` type for plan code | `diagnostics` field is `tuple[ReplayDiagnostic, ...]`, `has_warnings` excludes trailing truncation |
| `test_turn_store.py:1-161` | 161 | Existing test patterns for plan | Store path construction: `tmp_path / "turns" / "sess-1" / "turn_metadata.jsonl"`, `TurnStore(tmp_path, "sess-1")` |
| `test_dialogue.py:0-70` | 70 | `_build_dialogue_stack()` factory, imports | Returns `(controller, plane, store, journal, turn_store)`, `FakeRuntimeSession` from `test_control_plane` |
| `test_dialogue.py:1000-1090` | 90 | Existing read/recovery test patterns | `session.read_thread_response` override, `pytest.raises(RuntimeError, match=...)` |
| `test_dialogue.py:1835-1955` | 120 | Existing `TestFirstTurnFastPath` | `TrackingSession` subclass with `read_thread_calls` counter, `capsys` usage in adjacent tests |
| `test_control_plane.py:95-149` | 55 | `FakeRuntimeSession` behavior | `read_thread()` returns turns from `completed_turn_count` unless `read_thread_response` is set |
| `control_plane.py:46-49` | 4 | Confirm stderr pattern in second file | `_log_local_append_failure` also uses `print(f"codex-collaboration: ...", file=sys.stderr)` |

### Architecture for the hardening work

| Component | Responsibility | Location |
|-----------|----------------|----------|
| `_next_turn_sequence()` | Turn-sequence derivation with trust policy | `dialogue.py:725-753` (to be rewritten) |
| `TurnStore.get_all_checked()` | Single-pass metadata + diagnostics | `turn_store.py` (to be added after line 71) |
| `_local_metadata_complete_for_completed_turns()` | Prefix-completeness check | `dialogue.py` (to be added after line 67) |
| `recover_startup()` | Startup reattach with metadata check | `dialogue.py:510-558` (guard restructure) |
| `read()` | Existing integrity enforcement (unchanged) | `dialogue.py:812-875` |
| `replay_jsonl()` | Shared JSONL replay with diagnostics | `replay.py:56-149` |
| `ReplayDiagnostics` | Diagnostic collection type | `replay.py:44-53` |
| `FakeRuntimeSession` | Test double with `read_thread_response` override | `test_control_plane.py:60-141` |
| `_build_dialogue_stack()` | Test factory returning 5-tuple | `test_dialogue.py:24-59` |

### Key patterns for implementation

**Stderr diagnostics:** `print(f"codex-collaboration: {operation} failed: {reason}. Got: {got!r:.100}", file=sys.stderr)` — see `dialogue.py:63-67` and `control_plane.py:46-49`. Tests assert via `capsys.readouterr().err`.

**Store path construction in tests:** `tmp_path / "plugin-data" / "turns" / "sess-1" / "turn_metadata.jsonl"` — the `plugin-data` prefix comes from `_build_dialogue_stack()` which creates `plugin_data = tmp_path / "plugin-data"`.

**`read_thread_response` override:** Set `session.read_thread_response = {"thread": {"id": "thr-start", "turns": [...]}}` to control what `read_thread()` returns. When `None` (default), `FakeRuntimeSession` synthesizes turns from `completed_turn_count`.

**JSONL corruption in tests:** Append invalid JSON or schema-violating records directly to the store path file. See `test_turn_store.py:61-68` for the pattern.

**Error assertion pattern:** `with pytest.raises(RuntimeError, match="pattern") as exc_info:` — check `exc_info.value.__cause__` for `from exc` chains.

### Dependency graph for implementation

```
get_all_checked() [Task 1]
    └─ calls replay_jsonl() + filters
    └─ no dependencies on other new code

_local_metadata_complete_for_completed_turns() [Task 2]
    └─ pure function, no dependencies

_next_turn_sequence() rewrite [Task 3]
    ├─ calls get_all_checked() [Task 1]
    └─ calls _local_metadata_complete_for_completed_turns() [Task 2]

_next_turn_sequence() tests [Task 4]
    └─ tests Task 3 behavior

recover_startup() restructure [Task 5]
    └─ calls _local_metadata_complete_for_completed_turns() [Task 2]
```

## Context

### Branch and repository state

- **Branch:** `fix/t02-dialogue-first-turn-hardening` (created from `main` this session)
- **HEAD commit:** `d5aa4038` (original spec commit, still on `main`)
- **Working tree:** 3 modified/new files (spec, contract, plan) — not yet committed
- **Test baseline:** 546 tests passing (verified in prior sessions, no code changes)

### Mental model

**Invariant alignment problem.** The session's core work was aligning a spec's claimed invariant with what the codebase actually enforces. The original spec proposed exact-key equality (`set(keys) == set(range(1, N+1))`), but `read()` and the crash-recovery contract only require prefix-completeness (every completed turn has metadata; extra keys are ignored).

The subtlety: the zero-turn case (`completed_count == 0`) is genuinely different. For positive counts, the rule aligns with existing enforcement. For zero counts, the rule is new policy — stale local metadata with zero completed remote turns is anomalous state that the existing code doesn't check for. The spec must label this distinction honestly.

The broader pattern: **a function that handles two regimes under one name can smuggle a policy change into one regime while appearing to "align" with the other.** The fix is to label each regime's relationship to existing enforcement separately.

### Environment state

- macOS Darwin 25.3.0, Python 3.14.2
- `uv` for all Python tool invocations
- Working directory: `/Users/jp/Projects/active/claude-code-tool-dev`

## Learnings

### Exact equality and prefix-completeness are different invariants with different contracts

**Mechanism:** `set(keys) == set(range(1, N+1))` rejects extra keys. `set(range(1, N+1)).issubset(keys)` does not. The difference matters when a function claims to "encode what `read()` already enforces" — `read()` uses the second form (iterates completed turns, checks each key exists).

**Evidence:** `read()` at `dialogue.py:853-862` does `metadata.get(seq)` for each completed turn. Extra keys in `metadata` are never checked. `contracts.md:156-158` says "complete TurnStore metadata for every completed turn" — a one-way requirement.

**Implication:** When claiming a shared invariant across enforcement sites, verify the exact predicate form, not just the intent. "Both check that metadata is complete" can hide a divergence in what "complete" means.

**Watch for:** Other places where "shared invariant" claims mask predicate divergence between sites.

### Vacuous truth can bypass contract clauses

**Mechanism:** In the two-branch eligibility rule `(zero turns) OR (complete metadata for completed turns)`, the second branch is vacuously true when `completed_count == 0` because an empty required set is trivially satisfied. An implementer reading the contract could bypass the first branch's stale-metadata restriction via the second.

**Evidence:** `contracts.md:156-158` originally used OR-branches. User's second scrutiny caught this: *"An implementer or future reviewer can reasonably treat the second clause as satisfied for `completed_count == 0` because the required key set is empty."*

**Implication:** Normative contract text should use explicit conditional branches (if/else) when different count values require different behavior. OR-branches create bypass paths via vacuous truth.

### Spec framing must distinguish alignment from tightening

**Mechanism:** The original spec presented the zero-turn stale-metadata check as "matching what `read()` already enforces." User's scrutiny exposed this as inaccurate — `read()` has nothing to say about the zero-turn case, and the prior contract listed zero turns as unconditionally eligible.

**Evidence:** User stated: *"The zero-turn fix is still presented as alignment with `read()` and the crash-recovery contract, but it is not."* And: *"Either update the spec and contracts.md to say zero-turn stale metadata is a deliberate tightening, or back that rule out."*

**Implication:** When a spec changes behavior, label it as new policy, not as encoding existing behavior. The distinction matters for reviewers who check claims against code.

### Package observability patterns are not interchangeable

**Mechanism:** This package uses `print(f"codex-collaboration: ...", file=sys.stderr)` for diagnostics, not Python's `logging` module. Specifying `logger.warning()` would introduce a new dependency pattern.

**Evidence:** Grep of `server/` found only `print(..., file=sys.stderr)` via `_log_recovery_failure` (`dialogue.py:63-67`) and `_log_local_append_failure` (`control_plane.py:46-49`). No `import logging` or `logger =` anywhere.

**Implication:** Spec-level observability claims must match the package's actual infrastructure. Tests assert via `capsys.readouterr().err`, not log capture fixtures.

## Next Steps

### 1. User reviews implementation plan, shares feedback

**Dependencies:** None — async review by user.

**What to read:** `docs/superpowers/plans/2026-04-12-dialogue-first-turn-fast-path-hardening.md`

**Expected outcomes:** User may approve as-is, request changes to task structure, or identify gaps in the test code. The plan has complete code in every step, so most feedback will likely be about implementation specifics (e.g., error message wording, test setup patterns) rather than structural issues.

**Next action after review:** Incorporate feedback, then choose execution approach (subagent-driven or inline).

### 2. Execute the implementation plan (after plan approval)

**Dependencies:** Plan approval from step 1.

**Execution options:**
- **Subagent-driven (recommended):** Fresh subagent per task, review between tasks
- **Inline execution:** Execute tasks in current session with checkpoints

**Build order (from plan):**
1. `get_all_checked()` on TurnStore (self-contained, testable independently)
2. `_local_metadata_complete_for_completed_turns()` (pure function)
3. `_next_turn_sequence()` rewrite (depends on 1 and 2)
4. Tests for `_next_turn_sequence()` (8 new tests)
5. `recover_startup()` update + tests (2 new tests)
6. Final verification

### 3. Commit spec and contract changes before implementation

**Dependencies:** Plan approval (step 1). The spec and contract changes should be committed before implementation code so the git history shows design evolution clearly.

**Suggested commit:** `docs(spec): revise fast-path hardening design — prefix-completeness, contract update`

### 4. (After T-02) Begin T-20260330-02 planning

**Dependencies:** T-02 closed.

**What to read:** `docs/tickets/2026-03-30-codex-collaboration-plugin-shell-and-consult-parity.md`

## In Progress

**Clean stopping point — spec revision and plan writing complete, no code in flight.**

- Spec revised (2 rounds of scrutiny, all findings addressed)
- Contract updated (eligibility clause rewritten)
- Implementation plan written (6 tasks, complete code)
- All three artifacts are uncommitted modifications on `fix/t02-dialogue-first-turn-hardening`
- Plan pending user review before execution
- No code changes made to production or test files

## Open Questions

### 1. Should the implementation plan's test for `test_empty_plus_diagnostics_remote_two_completed` create a focus file?

**Context:** Most tests in `TestFirstTurnFastPath` create a `focus.py` file because `reply()` needs `explicit_paths` to exist. The `test_empty_plus_diagnostics_remote_two_completed` test in the plan doesn't create one because it expects to fail before reaching the dispatch path. However, if the error occurs after path validation, the missing file might cause a different error.

**Impact:** Might need to add `focus.py` creation to integrity-error tests in the plan. Worth checking during implementation.

### 2. Are there other callers of `recover_startup()` that depend on the zero-turn handle being reattached?

**Context:** The zero-turn stale-metadata tightening means handles with `completed_count == 0` and stale local metadata are no longer eligible for recovery reattach. If any code path depends on a zero-turn handle being reattached despite stale metadata, this change would break it.

**Impact:** Low risk — the only known caller is session startup. But worth verifying during implementation by grepping for `recover_startup` callers.

## Risks

### 1. Spec and contract changes are uncommitted

**Impact:** If the branch is lost or reset, the two revision rounds of spec changes and the contract update would need to be re-done. The implementation plan would also be lost.

**Mitigation:** Commit the spec, contract, and plan changes before starting implementation.

### 2. Implementation plan has complete code that may not compile

**Impact:** The plan contains exact code for every step, written from reading the source files. If any file has changed since reading (or if line numbers have shifted from Task 2's additions), the code may not apply cleanly.

**Mitigation:** Each task has a "run tests" step that catches this. The subagent-driven execution approach reviews between tasks.

### 3. The extra-local warning test depends on capsys ordering

**Impact:** If other stderr output occurs between test start and the extra-local warning, the `assert "..." in capsys.readouterr().err` may include unrelated output. This is acceptable (the assertion checks containment, not equality) but could make debugging harder if the assertion fails for other reasons.

**Mitigation:** The `in` check is robust against extra output. Only a concern if the substring appears in unrelated stderr output, which is unlikely.

## References

**Spec:**
- `docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md` (revised this session)

**Contract:**
- `docs/superpowers/specs/codex-collaboration/contracts.md:150-165` (revised this session)

**Plan:**
- `docs/superpowers/plans/2026-04-12-dialogue-first-turn-fast-path-hardening.md` (new this session)

**Ticket:**
- T-20260410-02: `docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md`

**Handoffs:**
- Prior (loaded): `docs/handoffs/archive/2026-04-12_01-42_t02-fast-path-hardening-design-approved.md`
- Prior (also loaded): `docs/handoffs/archive/2026-04-12_01-40_t-20260410-02-design-review-complete-spec-draft-next.md`

**Key source files:**
- `packages/plugins/codex-collaboration/server/dialogue.py` — `:725-753` (rewrite target), `:533-539` (recovery restructure), `:63-67` (stderr pattern)
- `packages/plugins/codex-collaboration/server/turn_store.py` — new `get_all_checked()` after `:71`
- `packages/plugins/codex-collaboration/server/replay.py` — `ReplayDiagnostics` at `:44-53`
- `packages/plugins/codex-collaboration/tests/test_dialogue.py` — existing fast-path tests at `:1839-1910`
- `packages/plugins/codex-collaboration/tests/test_turn_store.py` — 3 new tests to add

## Gotchas

### `_build_dialogue_stack()` puts plugin data at `tmp_path / "plugin-data"`, not `tmp_path`

**Symptom:** Tests that construct JSONL paths manually get the wrong directory.

**Root cause:** `_build_dialogue_stack()` at `test_dialogue.py:33` creates `plugin_data = tmp_path / "plugin-data"` and passes that to `TurnStore`. So the JSONL file lives at `tmp_path / "plugin-data" / "turns" / "sess-1" / "turn_metadata.jsonl"`, not `tmp_path / "turns" / ...`.

**Mitigation:** All test code in the plan uses the correct `tmp_path / "plugin-data" / "turns" / "sess-1" / "turn_metadata.jsonl"` path.

### `FakeRuntimeSession.read_thread()` synthesizes turns from `completed_turn_count` unless overridden

**Symptom:** Tests that need specific turn counts may be surprised that `run_turn()` increments `completed_turn_count`.

**Root cause:** When `read_thread_response` is `None`, `read_thread()` at `test_control_plane.py:125-137` builds turns from `self.completed_turn_count`. Each `run_turn()` call increments this counter at `:113`.

**Mitigation:** Tests that need to control remote turn state should set `session.read_thread_response` explicitly. Tests that rely on the auto-increment behavior (like the existing happy-path test) should be aware that `controller.start()` calls `run_turn()` internally, which sets `completed_turn_count = 1`.

### Spec, contract, and plan are all uncommitted

**Symptom:** `git status` shows 3 modified/new files on the feature branch.

**Root cause:** The session focused on revision and plan writing, not committing. The user wants to review the plan before any commits.

**Mitigation:** Commit all three files before starting implementation. Suggested message: `docs(spec): revise fast-path hardening design — prefix-completeness, contract update`

## Conversation Highlights

### User's structured review format

The user presented findings as `::code-comment` annotations with title, body, file reference, line range, priority, and confidence — a structured review format that enables precise response. Each finding was self-contained with enough evidence to verify independently.

### User's invariant-reasoning precision

When choosing between exact-key equality (B) and prefix-completeness (A), the user rejected the initial rationale ("extra keys are harmless noise") and supplied a stronger one: *"The strongest reason is not 'extra keys are harmless noise,' it is that A matches the system's current contract and enforcement surface."* They also rejected the "write-ordering windows" justification because `_finalize_confirmed_turn()` writes metadata only after confirmation.

This pattern: the user accepts the conclusion but requires the reasoning to be precise. Sloppy justifications for correct choices are still rejected.

### User's multi-round scrutiny pattern

The user applied two scrutiny passes, each finding issues the prior round missed:
- Round 1: invariant divergence, path-mismatch overclaim, recovery zero-turn gap
- Round 2: contract vacuous-truth bypass, logger pattern mismatch, headline wording

Each round had a verdict: "Major revision" → "Minor revision." The pattern: scrutiny continues until all claims are internally consistent and match the codebase.

### User's explicit deferral of plan review

User stated: *"I will review the implementation plan and then share my findings with you in the next session."* This mirrors the prior session's spec review deferral. The pattern: design artifacts (specs, plans) are reviewed offline before execution begins. Don't start execution without explicit approval.

## User Preferences

**Invariant justification precision (confirmed this session):**
The user rejects sloppy rationale for correct choices. When the correct invariant (prefix-completeness) was justified with "write-ordering windows" and "extra keys are harmless," the user pushed back: *"I would not lean on 'write-ordering windows' as the main justification for A."* The right justification is contract alignment, not hand-waving about harmlessness.

**Alignment vs tightening honesty (new this session):**
When a spec changes behavior beyond what existing code enforces, the user requires explicit labeling: *"The zero-turn fix is still presented as alignment with `read()` and the crash-recovery contract, but it is not."* Don't present policy changes as encoding existing behavior.

**Contract text precision (new this session):**
Normative contract text must be unambiguous. OR-branches with vacuous-truth bypasses are not acceptable: *"An implementer or future reviewer can reasonably treat the second clause as satisfied."* Use explicit conditionals.

**Multi-round scrutiny pattern (confirmed this session):**
The user applies structured scrutiny passes until the spec is internally consistent. Each round has a verdict. Two rounds this session: "Major revision" → "Minor revision." Expect this pattern for future specs.

**Offline review before execution (confirmed this session):**
Design artifacts (specs, plans) are reviewed offline. Don't start execution without explicit approval. This session mirrored the prior session's pattern exactly.

**Package pattern conformance (new this session):**
New observability mechanisms must match the package's existing patterns. Don't introduce `logger.warning()` in a package that uses `print(..., file=sys.stderr)`.
