---
date: 2026-04-13
time: "00:36"
created_at: "2026-04-13T04:36:05Z"
session_id: 2e85eaa0-5676-43d3-b12f-c312c05f2923
resumed_from: docs/handoffs/archive/2026-04-12_23-45_t02-spec-revised-plan-written.md
project: claude-code-tool-dev
branch: fix/t02-dialogue-first-turn-hardening
commit: 3de8eecc
title: "T-02 implementation complete, PR #105 open for review"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/turn_store.py
  - packages/plugins/codex-collaboration/server/dialogue.py
  - packages/plugins/codex-collaboration/tests/test_turn_store.py
  - packages/plugins/codex-collaboration/tests/test_dialogue.py
  - docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/plans/2026-04-12-dialogue-first-turn-fast-path-hardening.md
---

# T-02 Implementation Complete, PR #105 Open for Review

## Goal

Implement the dialogue first-turn fast path hardening design — harden `_next_turn_sequence()` and `recover_startup()` to use a shared prefix-completeness invariant, replacing the old cardinality-only check that missed gap bugs and skipped zero-turn handles.

**Trigger:** Prior session revised the spec (2 rounds of user scrutiny, 5 findings addressed) and wrote a 7-task implementation plan. This session reviewed the plan, revised it (6 critical findings), and executed it via subagent-driven development.

**Stakes:** `_next_turn_sequence()` is the turn-sequence derivation path used by `reply()`. An incorrect invariant allows dispatch on broken state (false negatives) or quarantines valid handles (false positives). The recovery path had the same exposure via `recover_startup()`.

**Success criteria:** (1) All 7 plan tasks executed with passing tests, (2) 15 new tests proving the invariant across both enforcement sites, (3) reply/recovery symmetry closed, (4) PR open for review. All met.

**Connection to project arc:** T-02 is the second dialogue hardening ticket. T-03 (observability) merged as PR #104. After T-02 closes, next is T-20260330-02 (codex-collaboration plugin shell), which unblocks the 6-ticket supersession chain.

## Session Narrative

Session opened by loading the prior handoff (`2026-04-12_23-45_t02-spec-revised-plan-written.md`) which contained the revised spec, updated `contracts.md`, and the 6-task implementation plan pending user review.

**Phase 1 — Plan scrutiny (~15 min):**

User presented a structured adversarial review of the implementation plan with 5 critical findings and a "Major revision" verdict. The findings shared a root cause: the plan was optimized for step-by-step code insertion, not for proving its central claim (the settled invariant).

I verified each finding against the actual code and plan before proposing fixes. All 5 confirmed:

1. **Recovery gap test doesn't hit the bug.** The test used local `{1, 3}` vs remote `3` completed. Old code checks `len(metadata) < completed_count` — `2 < 3` triggers quarantine. The test passes on old code. Verified at `dialogue.py:533-539`.

2. **Missing symmetry tests.** No reply-path zero-turn stale metadata test. No recovery-path extra-key acceptance test. A buggy implementation could diverge between reply and recovery while passing the planned suite.

3. **`recover_startup()` docstring/comments become false.** Lines 492-495 and 510-514 describe the old vacuous OR-branch eligibility. After implementation, these statements would be wrong.

4. **Verification section wrong.** `git log --oneline main..HEAD` returns nothing (both branches at same SHA `d5aa4038`). Plan says "5 commits" but no task commits the docs. Count is inconsistent.

5. **Required execution skill.** Plan says "REQUIRED SUB-SKILL" for skills that exist but shouldn't be mandatory.

**Phase 2 — Plan revision (~10 min):**

Applied all 6 required changes:
- Fixed recovery gap test to use cardinality-matching gap (remote 2, not 3)
- Added reply-path zero-turn stale metadata test
- Added recovery-path extra-key acceptance test
- Added explicit docstring/comment update step to Task 5
- Added Task 0 (docs commit), fixed verification base to `d5aa4038`
- Downgraded execution skill from required to recommended

Updated test counts throughout (file map, commit messages, verification criteria).

**Phase 3 — Second plan review (~5 min):**

User reviewed the revised plan and found 2 low-severity issues:
1. Unused `turn_store` binding in `test_empty_plus_diagnostics_remote_zero_completed` (Ruff F841)
2. Internal count/label drift (file map said `~14` tests, body described 12; commit prefix mismatch `feat(turn_store)` vs `feat(turn-store)`)

Applied all 4 fixes. User verdict: "Minor revision" → execution-ready.

**Phase 4 — Execution via subagent-driven development (~15 min):**

Created 7 tasks with dependency graph. Executed Task 0 (docs commit) directly. Dispatched Tasks 1-2 in parallel (independent files — `turn_store.py` and `dialogue.py`). Then Tasks 3-5 sequentially (integration dependencies). Task 6 (verification) ran directly.

| Task | Subagent | Model | Duration | Result |
|------|----------|-------|----------|--------|
| 0: Docs commit | Direct | — | 1 min | `7cbdb480` |
| 1: `get_all_checked()` | task1-implementer | sonnet | 43s | `6fd1d23d` — 19/19 tests |
| 2: Helper function | task2-implementer | sonnet | 29s | `0029a099` — 64/64 tests |
| 3: Rewrite `_next_turn_sequence()` | task3-implementer | sonnet | 43s | `47fbb7ed` — 64/64 tests |
| 4: Hardening tests (9 new) | task4-implementer | sonnet | 79s | `f156455a` — 11/11 class |
| 5: Recovery restructure (3 new) | task5-implementer | sonnet | 80s | `579c081d` — 76/76 tests |
| 6: Verification + lint | Direct | — | 2 min | 561/561, format fix `3de8eecc` |

All subagents reported DONE on first dispatch — no BLOCKED or NEEDS_CONTEXT escalations. Ruff format caught line wrapping in the new tests, fixed in a separate commit.

**Phase 5 — PR creation (~2 min):**

Pushed branch, created PR #105 via `gh pr create`. User requested PR for review rather than local merge.

## Decisions

### Decision 1: Skip two-stage review for Tasks 1-2

**Choice:** Skipped spec compliance and code quality reviewer subagents for Tasks 1 and 2. Proceeded directly from implementer DONE to next task.

**Driver:** Both tasks were purely mechanical — exact code provided in the plan, single-file changes, all tests passing. The plan itself had been through two rounds of user scrutiny.

**Alternatives considered:**
- **Full two-stage review per skill protocol** — would add 2 reviewer subagents per task (4 total). Rejected because the code was plan-verbatim with no judgment calls, and the tasks are additive (no existing behavior modified).

**Trade-offs:** Skipping reviews means any subtle issues in the plan-specified code wouldn't be caught. Acceptable because: (a) the plan was adversarially reviewed, (b) tests verify behavior, (c) the final verification step catches regressions.

**Confidence:** High (E2) — both subagents reported clean results, all tests pass.

**Reversibility:** High — issues would surface in the full-suite verification or PR review.

**Change trigger:** If a subagent had reported DONE_WITH_CONCERNS, would have dispatched reviewers.

### Decision 2: Parallel dispatch for Tasks 1-2

**Choice:** Dispatched Tasks 1 (`turn_store.py`) and 2 (`dialogue.py`) in parallel rather than sequentially.

**Driver:** The tasks modify different files with no code dependency. Task 1 adds a method to `turn_store.py`; Task 2 adds a function to `dialogue.py`. Neither reads the other's output.

**Alternatives considered:**
- **Sequential execution** — simpler but slower. No benefit since there's no dependency.

**Trade-offs:** Small risk of git merge conflicts if both touch overlapping regions. Acceptable because the files are completely different.

**Confidence:** High (E2) — verified file independence from the plan's file map.

**Reversibility:** N/A — already executed successfully.

**Change trigger:** If tasks shared a file, would execute sequentially.

### Decision 3: Separate format commit instead of amending

**Choice:** Created a separate `style(dialogue): ruff format test_dialogue.py` commit rather than amending the Task 4 or Task 5 commit.

**Driver:** The skill protocol says "prefer new commits over amending." The format changes are cosmetic (line wrapping) and don't affect behavior.

**Alternatives considered:**
- **Amend Task 4 commit** — cleaner history but risks modifying a commit that tests already verified against.
- **Include format step in each task** — would prevent the issue but adds overhead to every task dispatch.

**Trade-offs:** 7 commits instead of 6. Minor history noise for safety.

**Confidence:** High (E3) — all 561 tests pass after the format commit.

**Reversibility:** Could squash during merge if the extra commit is undesirable.

**Change trigger:** If the project adopts a "squash merge" PR strategy, this becomes moot.

## Changes

### `packages/plugins/codex-collaboration/server/turn_store.py`

**What changed:** Added `get_all_checked()` method between `get_all()` and `check_health()`.

**Why:** Existing `get_all()` discards diagnostics; existing `check_health()` discards results. The rewritten `_next_turn_sequence()` needs both in one pass to detect corruption without losing metadata.

**Key detail:** Returns `(dict[int, int], ReplayDiagnostics)`. Diagnostics are file-global (session-wide JSONL), not collaboration-scoped — corruption from an unrelated collaboration appears in the diagnostics. Callers treat any diagnostic as reason to distrust an otherwise-empty result.

### `packages/plugins/codex-collaboration/server/dialogue.py`

**What changed:** Three additions:

1. **`_local_metadata_complete_for_completed_turns()`** (module-level function after `_log_recovery_failure`): Prefix-completeness check. `completed_count == 0` → `not local_turns` (deliberate tightening). `completed_count > 0` → `set(range(1, N+1)).issubset(keys)`.

2. **`_next_turn_sequence()` rewrite**: Three-phase trust policy replacing the old two-branch logic. Phase 1: empty TurnStore + no diagnostics → fast path return 1. Phase 2: all other states require `read_thread()` with two error variants (empty-local-with-diagnostics, non-empty-local). Phase 3: validate prefix-completeness, quarantine handle on failure, stderr warning for extra-local keys.

3. **`recover_startup()` restructure**: Removed `if completed_count > 0:` guard. Now calls `_local_metadata_complete_for_completed_turns()` unconditionally. Updated docstring from vacuous OR-branches to explicit if/else form. Updated phase-2 comment to reference the shared helper.

### `packages/plugins/codex-collaboration/tests/test_turn_store.py`

**What changed:** Added `TestGetAllChecked` class with 3 tests: clean store, corrupt JSONL mid-file, and empty store.

### `packages/plugins/codex-collaboration/tests/test_dialogue.py`

**What changed:** Added 12 new tests across 2 classes:

**`TestFirstTurnFastPath` (9 new tests):**
- `test_empty_plus_diagnostics_remote_zero_completed` — corrupt JSONL + remote 0 → proceed as turn 1
- `test_empty_plus_diagnostics_remote_two_completed` — corrupt JSONL + remote 2 → integrity error
- `test_empty_plus_diagnostics_remote_fails` — corrupt JSONL + read_thread raises → error mentions diagnostics
- `test_gap_metadata_integrity_error` — gap `{2}` with remote 2 → integrity error
- `test_partial_tail_integrity_error` — partial `{1}` with remote 2 → integrity error
- `test_nonempty_local_remote_fails` — non-empty local + read_thread raises → error mentions sequences
- `test_zero_turn_stale_metadata_integrity_error` — stale `{1}` + remote 0 → integrity error (symmetry test)
- `test_extra_local_keys_prefix_complete` — extra `{1,2,3}` + remote 2 → succeeds, stderr warning
- `test_unrelated_collaboration_corruption_disables_fast_path` — file-global blast radius

**`TestRecoverStartupMetadataCompleteness` (3 new tests):**
- `test_gapped_metadata_quarantines_handle` — cardinality-matching gap `{1,3}` vs remote 2 → quarantine (old code misses this)
- `test_zero_turn_stale_metadata_quarantines_handle` — stale metadata + remote 0 → quarantine (old code skips)
- `test_extra_local_keys_allows_reattach` — extra `{1,2,3}` vs remote 2 → reattach allowed (symmetry test)

### `docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md`

**What changed:** Spec revisions from prior session (committed this session in Task 0). Relaxed invariant to prefix-completeness, labeled zero-turn check as deliberate tightening, removed path-mismatch overclaim, added preconditions section.

### `docs/superpowers/specs/codex-collaboration/contracts.md`

**What changed:** Rewrote crash-recovery eligibility clause from OR-branches to explicit if/else on `completed_count`. Eliminates vacuous-truth bypass.

### `docs/superpowers/plans/2026-04-12-dialogue-first-turn-fast-path-hardening.md`

**What changed:** 7-task implementation plan. Revised this session with 6 critical findings (recovery gap test, symmetry tests, docstring updates, verification section, execution skill preamble, test counts).

## Codebase Knowledge

### Architecture for the hardening work

| Component | Responsibility | Location |
|-----------|----------------|----------|
| `_next_turn_sequence()` | Turn-sequence derivation with three-phase trust policy | `dialogue.py` (find by method name — line shifted) |
| `TurnStore.get_all_checked()` | Single-pass metadata + diagnostics | `turn_store.py:73-91` |
| `_local_metadata_complete_for_completed_turns()` | Shared prefix-completeness check | `dialogue.py:69-86` |
| `recover_startup()` | Startup reattach with metadata check | `dialogue.py` (find by method name) |
| `read()` | Existing integrity enforcement (unchanged) | `dialogue.py:812-875` |
| `replay_jsonl()` | Shared JSONL replay with diagnostics | `replay.py:56-149` |
| `ReplayDiagnostics` | Diagnostic collection type | `replay.py:44-53` |
| `FakeRuntimeSession` | Test double with `read_thread_response` override | `test_control_plane.py:60-141` |
| `_build_dialogue_stack()` | Test factory returning 5-tuple | `test_dialogue.py:24-59` |

### Key patterns

**Stderr diagnostics:** `print(f"codex-collaboration: {operation} ...", file=sys.stderr)` — see `dialogue.py:63-67` and `control_plane.py:46-49`. Tests assert via `capsys.readouterr().err`.

**Store path in tests:** `tmp_path / "plugin-data" / "turns" / "sess-1" / "turn_metadata.jsonl"` — the `plugin-data` prefix comes from `_build_dialogue_stack()`.

**`read_thread_response` override:** Set `session.read_thread_response = {"thread": {"id": "...", "turns": [...]}}` to control what `read_thread()` returns.

**JSONL corruption in tests:** Append invalid JSON directly to the store path file.

### Dependency graph

```
get_all_checked()
    -> calls replay_jsonl() + filters by collaboration_id

_local_metadata_complete_for_completed_turns()
    -> pure function, no dependencies

_next_turn_sequence() [REWRITTEN]
    -> calls get_all_checked()
    -> calls _local_metadata_complete_for_completed_turns()
    -> calls runtime.session.read_thread()

recover_startup() [RESTRUCTURED]
    -> calls self._turn_store.get_all()
    -> calls _local_metadata_complete_for_completed_turns()
```

### Pyright pre-existing issues

The `dialogue.py` file has pre-existing Pyright issues with `runtime: object` typing — `reportPossiblyUnboundVariable`, `reportAttributeAccessIssue`, `reportArgumentType`. These are not from our changes and were present before the hardening work.

## Context

### Branch and repository state

- **Branch:** `fix/t02-dialogue-first-turn-hardening`
- **Base SHA:** `d5aa4038` (where branch was created from `main`)
- **HEAD:** `3de8eecc` (7 commits ahead)
- **PR:** jpsweeney97/claude-code-tool-dev#105
- **Test baseline:** 561 tests passing (546 existing + 15 new)
- **Lint/format:** Clean on all modified files

### Mental model

**Proof-oriented testing vs code-insertion testing.** The prior plan was optimized for step-by-step code insertion. The user's scrutiny exposed this: tests that pass on both old and new code prove nothing about the change. The fix was to construct inputs where the old predicate passes but the new one fails (cardinality-matching gaps), and to test both enforcement sites on the same disagreement cases (reply/recovery symmetry pairs).

The broader pattern: **a plan that treats verification as ceremony rather than as the primary artifact is exactly backwards for a ticket whose history is about semantic drift between enforcement sites.**

### Environment state

- macOS Darwin 25.3.0, Python 3.14.2
- `uv` for all Python tool invocations
- Working directory: `/Users/jp/Projects/active/claude-code-tool-dev`

## Learnings

### Cardinality-matching gaps defeat length-based metadata checks

**Mechanism:** The old `len(metadata) < completed_count` check misses gaps where the count matches but the keys don't. Local `{1, 3}` with `completed_count == 2` has `len == 2`, so `2 < 2` is False — gap undetected. Only prefix-completeness (`{1, 2}.issubset(keys)`) catches this.

**Evidence:** The plan's original recovery gap test used remote 3 completed, which `len == 2 < 3` catches. User's scrutiny exposed this: "the test passes on old code and does not prove the gap bug."

**Implication:** When writing regression tests, verify the test actually fails on old code. A test that passes on both old and new code is not a regression test.

### Symmetry tests must cover disagreement cases in both directions

**Mechanism:** A shared helper is necessary but not sufficient for reply/recovery symmetry. The two enforcement sites can diverge if one caller uses the helper differently (e.g., different parameters, different error handling). Testing must cover both directions of potential disagreement: (1) reply rejects what recovery should also reject, (2) recovery accepts what reply should also accept.

**Evidence:** User's scrutiny found the plan had no reply-path zero-turn stale metadata test and no recovery-path extra-key acceptance test: "A buggy implementation could still allow stale zero-turn reply state or reject extra-key recovery state and still pass this plan's suite."

**Implication:** When a plan claims symmetry between two enforcement sites, test the cross-product: {accept, reject} x {site A, site B}.

### Plan adversarial review catches proof gaps that self-review misses

**Mechanism:** The plan was self-reviewed before the prior session ended. The user's adversarial review (with explicit regression, symmetry, maintainer, and CI adversary lenses) found 5 critical issues the self-review missed. Root cause: self-review checked whether the plan would produce working code, not whether it would prove the invariant.

**Evidence:** User's summary: "The plan is optimized for step-by-step code insertion, not for proving the settled invariant. It treats verification as ceremony instead of as the primary artifact."

**Implication:** Self-review of implementation plans should apply adversarial lenses: (1) Does each test fail on old code? (2) Can the invariant diverge while the suite passes? (3) Do code-level docs stay true after implementation? (4) Do verification commands work in the actual repo state?

### Subagent-driven development works well for mechanically-specified plans

**Mechanism:** When plan tasks have exact code, clear file targets, and explicit test commands, sonnet-class subagents execute reliably without escalation. All 5 implementation subagents reported DONE on first dispatch (total wall-clock ~5 minutes).

**Evidence:** Tasks 1-5 all completed first-try. No BLOCKED, NEEDS_CONTEXT, or DONE_WITH_CONCERNS. The only post-execution fix was ruff formatting (cosmetic).

**Implication:** Invest more time in plan specificity (exact code, exact test commands, exact commit messages) and less in subagent capability selection. A well-specified plan makes model choice less critical.

## Next Steps

### 1. Review PR #105

**Dependencies:** None — PR is open at jpsweeney97/claude-code-tool-dev#105.

**What to review:**
- 7 commits on `fix/t02-dialogue-first-turn-hardening`
- 15 new tests (3 turn_store + 9 fast-path + 3 recovery)
- `recover_startup()` docstring/comment updates
- Spec and contract revisions (committed as first commit)

**Expected outcomes:** User may approve, request changes, or merge. The user stated "next session we will review the PR."

### 2. (After merge) Close T-20260410-02

**Dependencies:** PR #105 merged.

**What to do:** Update the ticket at `docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md` with status `closed`, resolution summary, and PR reference.

### 3. (After T-02) Begin T-20260330-02 planning

**Dependencies:** T-02 closed.

**What to read:** `docs/tickets/2026-03-30-codex-collaboration-plugin-shell-and-consult-parity.md`

## In Progress

**Clean stopping point — all implementation complete, PR open, no work in flight.**

- All 7 plan tasks executed successfully
- 561/561 tests passing
- PR #105 created and ready for review
- No uncommitted changes on the branch

## Open Questions

### 1. Should the extra-local warning also fire in `recover_startup()`?

**Context:** The `_next_turn_sequence()` rewrite emits a stderr warning when `len(local_turns) > completed_count` (extra-local keys). The `recover_startup()` restructure does not — it only calls the prefix-completeness helper. If extra-local keys in recovery are equally anomalous, they should get the same observability.

**Impact:** Low — extra-local keys during recovery are tolerated (reattach allowed), and the next `reply()` would emit the warning. But the recovery path silently accepts what the reply path warns about.

### 2. Should `recover_startup()` use `get_all_checked()` instead of `get_all()`?

**Context:** Task 5 replaces the old `get_all()` call with the same `get_all()` plus the new helper. It does NOT switch to `get_all_checked()` (which includes diagnostics). This means `recover_startup()` doesn't detect JSONL corruption — it only checks prefix-completeness of whatever metadata it can read.

**Impact:** A handle with corrupt JSONL but otherwise valid metadata would pass recovery. The `_next_turn_sequence()` path would catch it on the next `reply()`.

## Risks

### 1. Pre-existing Pyright issues may mask new type errors

**Impact:** The `dialogue.py` file has pre-existing Pyright issues with `runtime: object` typing. If any of our changes introduce a new type error in the same region, it would be hidden by the existing noise.

**Mitigation:** All behavioral verification is via pytest, not Pyright. The 561 passing tests are the primary correctness signal.

### 2. Format drift between plan code and committed code

**Impact:** The plan specifies exact code, but ruff formatting changed line wrapping in the tests. If someone reads the plan expecting it to match the committed code character-for-character, they'll see minor differences.

**Mitigation:** The format commit (`3de8eecc`) is clearly labeled. The plan should be treated as spec-level, not character-level.

## References

**PR:**
- jpsweeney97/claude-code-tool-dev#105

**Spec:**
- `docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md`

**Contract:**
- `docs/superpowers/specs/codex-collaboration/contracts.md:150-165`

**Plan:**
- `docs/superpowers/plans/2026-04-12-dialogue-first-turn-fast-path-hardening.md`

**Ticket:**
- T-20260410-02: `docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md`

**Prior handoffs:**
- Loaded: `docs/handoffs/archive/2026-04-12_23-45_t02-spec-revised-plan-written.md`
- Prior to that: `docs/handoffs/archive/2026-04-12_01-42_t02-fast-path-hardening-design-approved.md`

**Key source files:**
- `packages/plugins/codex-collaboration/server/dialogue.py` — rewritten `_next_turn_sequence()`, restructured `recover_startup()`, new helper
- `packages/plugins/codex-collaboration/server/turn_store.py:73-91` — new `get_all_checked()`
- `packages/plugins/codex-collaboration/server/replay.py:44-53` — `ReplayDiagnostics` type
- `packages/plugins/codex-collaboration/tests/test_dialogue.py` — 12 new tests
- `packages/plugins/codex-collaboration/tests/test_turn_store.py` — 3 new tests

## Gotchas

### `_build_dialogue_stack()` puts plugin data at `tmp_path / "plugin-data"`, not `tmp_path`

**Symptom:** Tests that construct JSONL paths manually get the wrong directory.

**Root cause:** `_build_dialogue_stack()` at `test_dialogue.py:33` creates `plugin_data = tmp_path / "plugin-data"` and passes that to `TurnStore`. So the JSONL file lives at `tmp_path / "plugin-data" / "turns" / "sess-1" / "turn_metadata.jsonl"`.

### `recover_startup()` still uses `get_all()`, not `get_all_checked()`

**Symptom:** Recovery path doesn't detect JSONL corruption — only checks prefix-completeness.

**Root cause:** The plan specified `get_all()` for recovery (matching the spec). This is intentional but means corruption detection is only on the reply path.

### Ruff format and plan-specified code may differ

**Symptom:** Committed test code doesn't match plan character-for-character.

**Root cause:** Plan-specified code uses the prior session's wrapping style. Ruff reformats to project standards. The format commit `3de8eecc` captures the diff.

## Conversation Highlights

### User's adversarial review methodology

The user applied 4 explicit adversary lenses to the plan: regression adversary (does each test fail on old code?), symmetry adversary (can reply/recovery diverge while the suite passes?), maintainer adversary (do code-level docs stay true?), CI/branch adversary (do verification commands work?). This methodology found 5 critical issues that self-review missed.

### User's root cause diagnosis

User's summary of the plan's weakness: "The plan is optimized for step-by-step code insertion, not for proving the settled invariant. It treats verification as ceremony instead of as the primary artifact. That is exactly backwards for a ticket whose whole history is about semantic drift between enforcement sites."

### User's revision protocol

User provided exact minimum changes: numbered list of 6 required changes, with explicit "after that, Minor revision territory." Clean protocol: findings → required changes → verdict → re-review cycle.

## User Preferences

**Plan adversarial review is non-negotiable (confirmed this session):**
User applies structured adversarial review to implementation plans with the same rigor as spec review. Self-reviewed plans are not execution-ready. The adversarial lenses (regression, symmetry, maintainer, CI) are a repeatable methodology.

**Proof-oriented testing over code-insertion testing (new this session):**
Tests must prove the new invariant adds value. A test that passes on both old and new code is not evidence of anything. User: "the test passes on old code and does not prove the gap bug described in the design."

**Minimum credible revision protocol (confirmed this session):**
User provides exact numbered changes required, states the target verdict ("Minor revision territory"), and offers immediate re-review. No open-ended "please fix the issues" — each change is specified.

**Execution approval is explicit (confirmed this session):**
User said "Yes. Apply all six before treating the plan as execution-ready." Implementation does not start until the plan passes review. This mirrors the spec review pattern from prior sessions.
