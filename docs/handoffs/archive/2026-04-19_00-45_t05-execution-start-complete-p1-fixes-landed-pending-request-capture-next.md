---
date: 2026-04-19
time: "00:45"
created_at: "2026-04-19T04:45:58Z"
session_id: 26f7acde-5cd1-4d72-85cb-e028871e0896
resumed_from: "docs/handoffs/archive/2026-04-18_00-52_t05-tasks-6-7-landed-orchestrator-and-recovery-ready-for-task-8.md"
project: claude-code-tool-dev
branch: main
commit: 5ee7afb4
title: "T-05 execution-start slice COMPLETE + P1 fixes landed — pending-request capture is next T-05 slice"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/__init__.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/delegation_job_store.py
  - packages/plugins/codex-collaboration/server/worktree_manager.py
  - packages/plugins/codex-collaboration/scripts/codex_runtime_bootstrap.py
  - packages/plugins/codex-collaboration/tests/test_mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegation_job_store.py
---

# T-05 Execution-Start Slice COMPLETE + P1 Fixes — Pending-Request Capture Next

## Goal

Complete Tasks 8-11 of the T-05 execution-start plan (`docs/plans/2026-04-17-t05-execution-start-slice.md`) and merge the slice to main. This session continued from a prior handoff where Tasks 1-7 (primitives + orchestrator + recovery) were complete at commit `b1451654` on `feature/t05-execution-start` with 652 tests. The execution-start slice establishes the `codex.delegate.start` MCP tool — from primitives through production wiring — as the foundation for the delegation surface.

**Trigger:** Prior session landed Tasks 6-7 (orchestrator + startup reconciliation) and saved a handoff at the natural orchestrator/recovery completion boundary. This session picked up Task 8 (MCP tool registration) as the next task.

**Stakes:** T-05 is the execution-domain foundation for codex-collaboration. Without this slice, the delegation surface has no MCP tool, no production wiring, and no E2E proof of the AC 4 recovery contract. T-06 (`codex.delegate.poll`, `.decide`, `.promote`) and T-07 (turn dispatch) are blocked until T-05 closes.

**Success criteria (all met):**
1. Tasks 8-11 executed via `superpowers:subagent-driven-development` with full two-stage review
2. Slice merged to main with `--no-ff` at `7714870b`
3. Post-merge review caught 2 P1 bugs + 1 P2 observation
4. P1 fixes landed on separate fix branch, merged at `5ee7afb4`
5. 666 tests passing, ruff clean
6. Next slice identified: T-05 pending-request capture (AC 6)

## Session Narrative

**Phase 1 — Handoff load and Task 8 (~30 min).** Loaded prior handoff (`2026-04-18_00-52_t05-tasks-6-7-landed-orchestrator-and-recovery-ready-for-task-8.md`). Verified worktree at `.claude/worktrees/feature-t05-execution-start` with HEAD `b1451654`, 652 tests. Read Task 8 spec (plan lines 3109-3585, 476 lines). Pre-identified zero plan-gaps — all referenced symbols exist (unlike Tasks 1, 6, 7 which each had mechanical plan-gaps). Dispatched implementer (sonnet) with full spec + baseline correction (plan says ~647, actual 652). Implementer returned DONE in one pass: 652 → 660 tests (+8), commit `7a646657`. Spec review: ✅ compliant. Code quality review: ✅ approved, 1 suggestion (stale docstring "delegation lazy wiring lands with Task 8"). Option A cleanup: fixed stale docstring, commit `d2f8b650`.

**Phase 2 — Task 9 (~20 min).** Read Task 9 spec (plan lines 3587-3781, 195 lines). Pre-identified one plan-gap: `LineageStore` import already exists at line 29 of `codex_runtime_bootstrap.py` — plan's import list would create a duplicate. Dispatched implementer with plan-gap noted. Implementer returned DONE: 660 → 662 (+2 smoke tests), commit `168714f9`. Both reviews passed. Option A cleanup: updated module docstring to mention both dialogue and delegation deferred initialization, commit `38a962cd`.

**Phase 3 — Task 10 (~25 min).** Read Task 10 spec (plan lines 3783-4092, 310 lines). Verified less-obvious interfaces: `AccountState` (models.py:114), `RuntimeHandshake` (models.py:104), `ControlPlane.__init__` accepts `runtime_factory` + `compat_checker`, `REQUIRED_METHODS` (codex_compat.py:71). Zero plan-gaps. Dispatched implementer. Implementer returned DONE: 662 → 663 (+1 E2E test), commit `6f61bd3c`. Both reviews passed. Option A cleanup: added `capture_output=True` to `_init_repo` git config calls (matching `test_worktree_manager.py` pattern), added docstring to `_init_repo`, updated module docstring from "Smoke tests" to "Production wiring and end-to-end tests". Commit `32f535dc`.

**Phase 4 — Task 11 verification and merge (~15 min).** Ran full suite: 663 passed. Ran ruff: found E402s in `codex_runtime_bootstrap.py` (pre-existing `sys.path.insert` → imports pattern) and F401 in `test_credential_scan.py` (unused import). User challenged my initial "pre-existing = don't fix" reasoning — correctly pointed out that the verification pass is exactly where these should be addressed. Fixed all: added `# noqa: E402` to post-sys.path imports, removed unused `ScanResult` import. Commit `5ca5b3a3`. Ruff: All checks passed. Pushed feature branch. Merged to main with `--no-ff` at `7714870b`. Cleaned up worktree and feature branch.

**Phase 5 — Post-merge review and P1 fixes (~25 min).** User ran external post-merge review (likely Codex) against the full merged slice. Three findings:
- **P1a:** `DelegationJobStore._replay()` accepts invalid status literals from disk, bypassing the busy gate. Reproduced: `update_status` with `status="bogus"` makes `list_active()` return empty.
- **P1b:** Bootstrap failure leaks untracked worktree. `create_worktree` runs before `start_execution_runtime`; if bootstrap fails, worktree is left behind with no durable record.
- **P2:** `session.close()` masks bootstrap error (already tracked as T4 amendment).

Created `fix/t05-p1-replay-validation-and-worktree-leak` branch. Fixed P1a: added validation in `_replay()` for both `create` (check `status` + `promotion_state`) and `update_status` (check `status`) against literal type sets. 3 new tests. Fixed P1b: added `WorktreeManager.remove_worktree()` (best-effort, cleans up worktree leaf + empty parent directory), updated `_WorktreeManagerLike` protocol, added try/except in controller's `start()` around `start_execution_runtime()`. User reviewed, found residual: `remove_worktree` only removed worktree leaf, not per-job parent directory. Fixed: added parent-directory cleanup in `remove_worktree()`. Second review passed with no findings. Merged at `5ee7afb4`.

**Phase 6 — Next-step sequencing (~5 min).** User identified that T-05 is NOT complete — AC 6 (pending-request capture through approval routing) is still open. Verified against ticket (line 323) and plan (line 60: "AC 6 ❌ not closed"). Confirmed sequencing: T-05 pending-request capture → T-05 decide-surface + lifecycle → T-05 COMPLETE → T-06 → T-07.

## Decisions

### Decision 1: Fix pre-existing ruff violations during verification pass

**Choice:** Fixed all ruff findings during Task 11 verification, including pre-existing E402s and F401, rather than ignoring them as "pre-existing."

**Driver:** User challenged: "Does the fact that those errors are pre-existing mean that they shouldn't be addressed?" — correctly identifying that the verification pass is exactly the right time to clean up lint debt in files touched by the slice.

**Alternatives considered:**
- **Ignore pre-existing findings** — initially proposed by me, rejected by user's pushback. The reasoning "pre-existing = don't touch" conflates provenance with relevance.
- **Fix only new findings** — would leave 6 pre-existing E402s while fixing 4 new ones in the same import block. Creates an inconsistent partial fix.

**Implications:** The slice merged with a clean ruff pass. Future verification passes should apply the same standard: fix what's in scope (files touched by the slice), don't ignore findings just because they predate the current work.

**Trade-offs accepted:** 3 files modified beyond the slice's strict scope (bootstrap E402s, conftest E402, test_credential_scan F401). Minimal blast radius — all cosmetic.

**Confidence:** High (E2) — user's feedback was clear and the fix was non-controversial.

**Reversibility:** N/A — ruff annotations don't affect runtime behavior.

**Change trigger:** N/A.

### Decision 2: Address P1 findings on separate fix branch (not fold into next slice)

**Choice:** Created `fix/t05-p1-replay-validation-and-worktree-leak` for the two P1 bugs rather than deferring to the next T-05 slice.

**Driver:** User directive: "Please address them on a separate fix branch." Both bugs are correctness issues on code that just merged to main — the replay bypass and worktree leak are live on the production branch.

**Alternatives considered:**
- **Fold into next slice** — would leave known bugs on main during the inter-slice period. Rejected because both P1s affect runtime correctness (busy-gate bypass, untracked directory leak).
- **Hotfix on main** — could work but the fix branch pattern matches the project's git conventions (`fix/*` branch pattern per `.claude/rules/workflow/git.md`).

**Implications:** Main is clean with both P1s fixed. The amendment candidates list (8 items from Tasks 2-7) remains deferred — those are design-level concerns, not correctness bugs.

**Trade-offs accepted:** One extra merge cycle before the next slice. Small cost for clean main.

**Confidence:** High (E2) — user directed, bugs reproduced, fixes verified.

**Reversibility:** N/A — the fixes are strictly additive (validation + cleanup).

**Change trigger:** N/A.

### Decision 3: `remove_worktree` as best-effort with parent-directory cleanup

**Choice:** Made `WorktreeManager.remove_worktree()` best-effort (suppresses all exceptions from `git worktree remove`) and added parent-directory cleanup (removes empty `<job-id>/` dir after worktree leaf is gone).

**Driver:** The method is used in a failure path — if the cleanup itself fails, the original error must propagate, not be masked by a cleanup failure. User's reviewer caught the residual: initial implementation removed the worktree leaf but left the empty parent directory, which is still an untracked artifact.

**Alternatives considered:**
- **Raise on cleanup failure** — would mask the original bootstrap error (the same class of bug as the T4 amendment "session.close() during error cleanup can swallow original error"). Rejected.
- **Leave parent directory** — user's reviewer flagged this as not fully fixing the P1. Rejected.

**Implications:** The controller's pre-dispatched failure path now cleans up both the worktree and its parent directory. The `_WorktreeManagerLike` protocol was extended with `remove_worktree`. All existing fakes in tests were updated.

**Trade-offs accepted:** Best-effort suppression means a failed cleanup is invisible. Accepted because: (a) the failure path already has no durable record of the worktree, so there's nothing to retry against; (b) the alternative (raising) is worse (masks the real error).

**Confidence:** High (E2) — verified by reviewer against real git repos. Test asserts both leaf and parent are gone.

**Reversibility:** High — method is additive.

**Change trigger:** If a more sophisticated worktree lifecycle manager is introduced that needs cleanup visibility, add logging to the suppressed exceptions.

## Changes

### Commits landed on `main` (this session)

**Execution-start slice (merged via `--no-ff` at `7714870b`):**

| # | SHA | Subject | Lines | Tests |
|---|---|---|---|---|
| 15 | `7a646657` | feat(t20260330-05): register codex.delegate.start MCP tool + dispatch | +370 (3 files) | 652 → 660 (+8) |
| 16 | `d2f8b650` | fix(t20260330-05): address task-8 review findings | +1/-2 (1 file) | 660 |
| 17 | `168714f9` | feat(t20260330-05): wire DelegationController into production bootstrap | +133 (2 files) | 660 → 662 (+2) |
| 18 | `38a962cd` | fix(t20260330-05): address task-9 review findings | +3/-2 (1 file) | 662 |
| 19 | `6f61bd3c` | test(t20260330-05): end-to-end codex.delegate.start integration | +279 (1 file) | 662 → 663 (+1) |
| 20 | `32f535dc` | fix(t20260330-05): address task-10 review findings | +7/-2 (1 file) | 663 |
| 21 | `5ca5b3a3` | style(t20260330-05): ruff fixes | +12/-12 (3 files) | 663 |

**P1 fix branch (merged via `--no-ff` at `5ee7afb4`):**

| # | SHA | Subject | Lines | Tests |
|---|---|---|---|---|
| 22 | `55c13b61` | fix(codex-collaboration): validate replay literals + clean up worktree on bootstrap failure | +163/-4 (5 files) | 663 → 666 (+3) |

### Net session contribution

- 8 commits (7 slice + 1 fix), 2 merge commits
- 22 files changed across the full slice (+3,634 lines), 5 files in the fix (+163 lines)
- 4 new source files, 5 new test files
- 593 → 666 tests (+73 across full slice + fix)

## Codebase Knowledge

### Files read / written this session

| File | Purpose | Key finding |
|---|---|---|
| `server/mcp_server.py` | Task 8 modifications | `_ensure_delegation_controller` at line 178, `codex.delegate.start` dispatch at line 327. Mirrors dialogue pattern exactly. Constructor now accepts `delegation_controller` + `delegation_factory` as optional kwargs (lines 130-131). |
| `server/__init__.py` | Task 8 exports | Added 6 exports: `DelegationController`, `DelegationJob`, `DelegationJobStore`, `ExecutionRuntimeRegistry`, `JobBusyResponse`, `WorktreeManager`. |
| `scripts/codex_runtime_bootstrap.py` | Task 9 production wiring | `_build_delegation_factory` at line 89 mirrors `_build_dialogue_factory`. `main()` constructs shared `ExecutionRuntimeRegistry` at line 138 and passes `delegation_factory` to `McpServer`. Module docstring updated to mention both dialogue and delegation deferred initialization. |
| `tests/test_mcp_server.py` | Task 8 tests | 8 new tests in 3 classes: `TestDelegateToolRegistration` (2), `TestDelegateDispatch` (3), `TestDelegationRecoveryWiring` (3). The recovery retry-ordering test (`test_ensure_delegation_controller_does_not_pin_on_recovery_failure`) uses a 3-dispatch proof shape. |
| `tests/test_delegate_start_integration.py` | Tasks 9-10 | 2 factory smoke tests (Task 9) + 1 E2E integration test (Task 10). E2E test seeds a `dispatched` journal entry before dispatch, asserts recovery reconciles it — the AC 4 consumer proof. |
| `server/delegation_job_store.py` | P1a fix | `_replay()` now validates `status` against `_VALID_STATUSES` and `promotion_state` against `_VALID_PROMOTION_STATES` for both `create` and `update_status` ops. Invalid records silently skipped. |
| `server/delegation_controller.py` | P1b fix | `start()` now wraps `start_execution_runtime()` in try/except that calls `remove_worktree()` on failure. Protocol extended with `remove_worktree`. |
| `server/worktree_manager.py` | P1b fix | New `remove_worktree()` method — best-effort `git worktree remove --force` + empty parent directory cleanup. |

### Architecture: Task 8 MCP surface composition

```
McpServer.__init__(delegation_controller=..., delegation_factory=...)
  │
  ├─ _ensure_delegation_controller() [line 178]
  │    build from factory → recover_startup() → pin (only after recovery succeeds)
  │
  └─ _dispatch_tool("codex.delegate.start") [line 327]
       → _ensure_delegation_controller()
       → controller.start(repo_root, base_commit)
       → asdict(result)  # DelegationJob or JobBusyResponse
```

### Architecture: Production bootstrap wiring (Task 9)

```
main() [codex_runtime_bootstrap.py]
  ├─ plugin_data_path = default_plugin_data_path()
  ├─ journal = OperationJournal(plugin_data_path)
  ├─ control_plane = ControlPlane(...)
  ├─ runtime_registry = ExecutionRuntimeRegistry()  # NEW — shared across factory calls
  ├─ McpServer(
  │    control_plane=...,
  │    dialogue_factory=_build_dialogue_factory(...),
  │    delegation_factory=_build_delegation_factory(  # NEW
  │        plugin_data_path, control_plane, runtime_registry, journal
  │    ),
  │  )
  └─ server.run()  # startup() → stdin JSON-RPC loop
```

### Key locations to remember

| Concept | Location |
|---|---|
| T-05 plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` (4,191 lines) |
| T-05 ticket (AC 6 still open) | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md:323` |
| `_ensure_delegation_controller` | `server/mcp_server.py:178` |
| `codex.delegate.start` dispatch | `server/mcp_server.py:327` |
| `_build_delegation_factory` | `scripts/codex_runtime_bootstrap.py:89` |
| E2E test with AC 4 proof | `tests/test_delegate_start_integration.py:165` |
| Recovery retry-ordering test | `tests/test_mcp_server.py:917` (3-dispatch proof shape) |
| Replay validation fix | `server/delegation_job_store.py:124-131` (create), `:137` (update_status) |
| Worktree cleanup fix | `server/delegation_controller.py:332-340` |
| `remove_worktree` | `server/worktree_manager.py:62` |
| Approval router substrate (for next slice) | `server/approval_router.py::parse_pending_server_request` |
| Notification-loop deferral note | Plan line 4172 |

## Context

### Mental model

**Framing:** This session completed the "surface and merge" arc of the execution-start slice. Tasks 8-10 are outward-facing composition work — they expose and inject the controller (Task 8), wire it into production (Task 9), and prove the full path end-to-end (Task 10). They don't change the controller's semantics (that was Tasks 6-7). Task 11 is verification and merge.

**Core insight for the post-merge review:** The two-stage in-pipeline review (spec + code quality) catches intra-task concerns but misses cross-task seam issues. P1a (replay validation) spans the write path (Task 2's `create`/`update_status` with validation) vs the read path (Task 2's `_replay` without validation). P1b (worktree leak) spans Task 3's `create_worktree` and Task 6's `start()` composition. A third review round — post-merge integration review against the full slice — is needed to catch these seam bugs.

### Project state at session close

**T-20260330-05 (execution-domain foundation):**
- Execution-start slice: **COMPLETE** on main at `7714870b` (merge) + `5ee7afb4` (P1 fixes). 666 tests.
- AC 6 (pending-request capture): **NOT closed**. Next slice.
- Remaining T-05 sequencing: pending-request capture → decide-surface + lifecycle → T-05 COMPLETE → T-06 → T-07.

**Other tickets unchanged:**
- T-20260330-06 / T-07: OPEN, blocked by T-05.
- T-20260416-01 (codex.dialogue.reply extraction mismatch): OPEN, medium priority, independent.

### Environment snapshot at session close

- Branch: `main` at `5ee7afb4`
- No active worktrees
- Plugin suite: 666 passed in ~5s
- Ruff: All checks passed
- MEMORY.md: Updated (T-05 execution-start marked COMPLETE with merge commit)

### Why this work matters

The execution-start slice is the first half of the T-05 ticket. It makes `codex.delegate.start` reachable in production — from MCP tool registration through factory initialization, controller startup recovery, and dispatched worktree creation. The E2E test proves the AC 4 recovery contract is wired on the production (lazy factory) path. The P1 fixes ensure the busy gate isn't bypassable via corrupted replay and that pre-dispatched failures don't leak worktrees. The remaining T-05 work (pending-request capture) wires the notification loop and approval routing so execution-domain server requests are surfaced rather than silently dropped.

## Learnings

### Post-merge integration review catches seam bugs the in-pipeline review misses

**Mechanism.** The two-stage in-pipeline review (spec compliance + code quality) operates commit-by-commit with task-scoped context. Cross-task seam issues — where the write path of one task doesn't match the read path of another, or where two tasks compose in a way neither individually tests — are invisible to this review.

**Evidence.** P1a: `_replay()` accepts invalid status literals. The write path (`create`, `update_status`) validates at lines 38-47 and 77-81 (Task 2). The read path (`_replay`) doesn't validate (also Task 2). Both paths were reviewed, but neither reviewer checked write-vs-read consistency because their scope was the committed code, not the contract between write and read. P1b: worktree leak on bootstrap failure. `create_worktree` (Task 3) and `start_execution_runtime` composition in `start()` (Task 6) were reviewed independently. The failure path between them — worktree created but bootstrap fails — fell into the gap.

**Implication.** For future slices: schedule a post-merge integration review against the full slice diff (not individual commits) before considering the work done. The three-round pattern (in-pipeline spec + quality, then post-merge integration) is stronger than two rounds alone.

**Watch for.** The post-merge review cost is ~10-15 minutes. Worthwhile for slices with 5+ tasks and cross-module composition. May be overkill for single-task fixes.

### "Pre-existing" is not a reason to skip lint fixes during verification

**Mechanism.** User challenged: "Does the fact that those errors are pre-existing mean that they shouldn't be addressed?" The answer is no — the verification pass is the natural place to clean up lint debt in files touched by the slice.

**Evidence.** Initial ruff pass found 12 errors: 10 E402 (pre-existing `sys.path` pattern), 1 E402 in conftest (pre-existing), 1 F401 unused import (pre-existing). All fixed with `# noqa: E402` annotations and import removal. User's feedback was the right call.

**Implication.** Future verification passes: fix what's in scope (files touched by the slice), don't dismiss findings based on provenance.

### Plan-gap pre-identification: zero gaps in composition tasks

**Mechanism.** Tasks 1, 6, and 7 each had mechanical plan-gaps (missing imports, missing attribute declarations) — the plan author's code blocks referenced symbols not included in their own scope. Task 8, 9, and 10 had zero plan-gaps. The pattern: creation tasks (Tasks 1-7) introduce new symbols that the plan's import/declaration blocks can miss; composition tasks (Tasks 8-10) reference only existing symbols.

**Evidence.** Task 8: all referenced symbols verified (DelegationJob, JobBusyResponse, etc.). Task 9: one "gap" was actually a duplicate import (LineageStore already imported). Task 10: all interfaces verified (AccountState, RuntimeHandshake, ControlPlane constructor, REQUIRED_METHODS).

**Implication.** For future plan execution: spend pre-identification effort proportional to whether the task creates new symbols or composes existing ones. Composition tasks need less pre-work.

### Option A cleanup pattern at 10-for-10

**Mechanism.** Every task (1-10) followed Option A: fix plan-aligned items, defer plan-divergent items, preserve in commit body. Test count drift: plan predicted 655, actual 663 (+8 from cleanup test additions). This session's tasks (8-10) continued the pattern but contributed 0 new coverage tests (reviewers found no gaps) — only cosmetic fixes (docstring updates, lint).

**Evidence.** Task 8: stale docstring. Task 9: incomplete module docstring. Task 10: missing `capture_output`, missing docstring, stale module docstring. All cosmetic. No plan-divergent amendments added.

**Implication.** The Option A pattern scales. 10 consecutive tasks with the same classification workflow, zero user re-explanations needed.

## Next Steps

### 1. Plan the T-05 pending-request capture slice (AC 6)

**Dependencies:** Execution-start slice COMPLETE on main. ✓

**What to read first:**
1. `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md:323` — AC 6 text
2. Plan deferral note at `docs/plans/2026-04-17-t05-execution-start-slice.md:4172` — notification-loop and pending-request capture
3. `server/approval_router.py::parse_pending_server_request` — existing substrate
4. Plan deferral at line 4173 — first `run_execution_turn()` call not dispatched yet

**What this slice needs to deliver:**
- Wire `run_execution_turn()` from the registered runtime session
- Consume execution-runtime notifications / server requests (currently dropped)
- Route requests through the approval router and persist as pending state
- Move the job into the right escalation state so later `codex.delegate.decide` has something to act on

**Approach:** Use `superpowers:writing-plans` to draft the plan, then execute via `superpowers:subagent-driven-development` (same pattern as this slice).

### 2. Plan-divergent amendment candidates (separate decision post-T-05)

| Task | Amendment candidate | Status |
|---|---|---|
| T2 | `update_status` raise-on-missing (instead of silent orphan-append) | Open |
| T2 | Refactor `_replay` to use shared `replay_jsonl` infrastructure | Open |
| T3 | `CalledProcessError.Got:` carries process output instead of input | Open |
| T3 | `TimeoutExpired` shows `worktree_path` (output) not `base_commit` (input) | Open |
| T4 | `initialize()` handshake result discarded | Open |
| T4 | `_compat_checker` / `_runtime_factory` raise paths bypass error contract | Open |
| T4 | `session.close()` during error cleanup can swallow original error | Open (also P2 from post-merge review) |
| T6 | `journal.append_audit_event` missing fsync | Open |

Discoverable via `git log --grep="Deferred as separate amendment decisions"`. 8 items total. Resolution deferred to post-T-05 or when a downstream task blocks.

### 3. Independent thread: T-20260416-01 extraction bug

Unchanged from prior handoffs. Independent of T-05 execution.

## In Progress

**Clean stopping point.** Execution-start slice complete and merged. P1 fixes landed. No work in flight.

- **Completed:** Tasks 8-11 with full two-stage review + Option A cleanup. P1 replay validation + worktree leak fixes. Both merged to main.
- **Not in flight:** Pending-request capture slice planning (deferred to next session).
- **Next action for next-session Claude:** Read AC 6 text and the plan's deferral notes. Start planning the pending-request capture slice.

## Open Questions

### 1. Pending-request capture slice scope

**Context.** AC 6 requires "execution-domain server requests surfaced through an approval-routing layer." The approval-router substrate exists (`parse_pending_server_request`), but the notification loop, turn dispatch, and escalation state transitions are all not wired. How much of this belongs in one slice vs split into sub-slices?

**Impact:** Medium. Determines planning granularity.

**Decision pending until:** Next session reads the approval-router code and assesses the wiring surface.

### 2. `remove_worktree` test coverage in `test_worktree_manager.py`

**Context.** The post-merge reviewer noted: "Residual risk is small: the real `WorktreeManager.remove_worktree()` path is still not directly pinned in `test_worktree_manager.py`." The fix is tested via the controller test's `_FakeWorktreeManager`, but the real `git worktree remove` path isn't integration-tested.

**Impact:** Low. Best-effort method — failure is suppressed by design.

**Decision pending until:** Next slice or cleanup pass.

## Risks

### 1. Amendment backlog (8 items)

**Impact.** The backlog is stable at 8 items (no new additions from Tasks 8-10 or the P1 fixes). If the pending-request capture slice surfaces more, the post-T-05 cleanup may need its own planning session.

**Mitigation.** Each item is individually small. Bundled cleanup PR viable.

**Action.** Reassess after T-05 is fully closed (all ACs met).

### 2. AC 6 scope may be larger than expected

**Impact.** The pending-request capture requires notification-loop wiring, turn dispatch, approval routing, and escalation state transitions. This may be a 5-8 task slice rather than 2-3 tasks.

**Mitigation.** Plan before executing — use `superpowers:writing-plans` to scope properly.

**Action.** Read approval-router code and notification-loop substrate before estimating.

## References

### Session's deliverables

| Artifact | Location | Status |
|---|---|---|
| Execution-start slice merge | `main` at `7714870b` | 22 files, 663 tests |
| P1 fix merge | `main` at `5ee7afb4` | 5 files, 666 tests |

### Authority documents

| Document | Location | Role |
|---|---|---|
| T-05 plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` | Source of truth for all 11 tasks |
| T-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth (AC 6 still open) |
| Recovery + journal spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Referenced by plan |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-18_00-52_t05-tasks-6-7-landed-orchestrator-and-recovery-ready-for-task-8.md`
- T-05 arc: kickoff → Q0 → tmp-hardening → plan draft → plan rounds 1-7 → plan merge → primitives Tasks 1-5 → orchestrator + recovery Tasks 6-7 → **MCP surface + production wiring + E2E + merge + P1 fixes (this handoff)** → pending-request capture → decide-surface + lifecycle → T-05 COMPLETE

## Gotchas

### 1. Ruff E402 in bootstrap scripts is by design

**Symptom.** `codex_runtime_bootstrap.py` imports after `sys.path.insert`, triggering E402.

**Root cause.** The script must modify `sys.path` before importing `server.*` modules.

**Prevention.** `# noqa: E402` on each post-sys.path import line. Already applied in `5ca5b3a3`.

### 2. Post-merge integration review catches bugs the in-pipeline review misses

**Symptom.** Two P1 bugs on main after slice merge despite clean two-stage reviews on every task.

**Root cause.** In-pipeline review operates commit-by-commit with task scope. Cross-task seam issues (write-path validation vs read-path trust, worktree creation vs composition failure) are invisible at task scope.

**Prevention.** Schedule a post-merge integration review against the full slice diff for slices with 5+ tasks and cross-module composition.

### 3. `remove_worktree` must clean up both leaf and parent

**Symptom.** Initial P1b fix removed worktree leaf but left empty `<job-id>/` parent directory.

**Root cause.** `create_worktree` creates the parent via `worktree_path.parent.mkdir()`, but `git worktree remove` only removes the worktree leaf.

**Prevention.** `remove_worktree()` now also removes empty parent directory. Test asserts both `worktree_path` and `worktree_path.parent` are gone.

### 4. Pyright stale-cache diagnostics on modified files

**Symptom.** `reportCallIssue` on `delegation_controller`/`delegation_factory` parameters, `reportMissingImports` on new modules. All false positives.

**Root cause.** Pyright's in-process cache doesn't immediately re-read modified files.

**Prevention.** Runtime `pytest` is source of truth. Disregard pyright diagnostics for recently-modified files for several minutes.

## Conversation Highlights

### User challenged "pre-existing = don't fix" reasoning

User: "Does the fact that those errors are pre-existing mean that they shouldn't be addressed?"

This was a direct and correct challenge to my initial framing. The verification pass is exactly the right place to clean up lint debt in files the slice touched. The challenge shifted my approach from "provenance-based skip" to "scope-based fix."

### Post-merge review as a third review round

User ran an external post-merge review (likely Codex-powered) that caught 2 P1 bugs and 1 P2 observation. The review operated on the full merged slice diff rather than individual commits — this is what made cross-task seam issues visible. The findings were presented as structured `::code-comment` blocks with priority, confidence, file references, and reproduction evidence. The reviewer's framing — "I reproduced this" — elevated the findings from theoretical to behavioral.

### Terse confirmation style sustained

User's replies: "Continue with Task 8 dispatch", "Proceed with Option A" (×3), "Continue to Task 9/10/11", "Yes, proceed." Consistent with prior sessions. No re-explanation needed when the controller pre-categorizes correctly.

### Sequencing awareness

User identified the next build step proactively — not T-06 but another T-05 slice (pending-request capture). Provided the concrete sequencing: "T-05 execution-start slice → T-05 pending-request capture slice → T-05 decide-surface + lifecycle refinements → T-05 COMPLETE → T-06 → T-07." Verified against ticket and plan, both confirmed.

## User Preferences

### "Pre-existing" is not a free pass

User expects lint/quality findings to be fixed during verification passes, regardless of when they were introduced. The relevant question is scope (did we touch this file?), not provenance (who introduced the issue?).

### Post-merge review is expected

User ran (or had run) a post-merge integration review after the slice merged. This is a deliberate third review round beyond the in-pipeline two-stage review. The findings were actionable and well-evidenced. This is now an established pattern for future slices.

### Separate fix branches for post-merge bugs

User directive: "Please address them on a separate fix branch." Not folded into the next slice, not hotfixed on main directly — a proper `fix/*` branch with its own review cycle.

### Terse confirmation continues (10-for-10)

"Proceed with Option A" is the default. No elaboration needed when the controller pre-categorizes correctly. Option A pattern is structurally stable.

## Rejected Approaches

### 1. Ignoring pre-existing ruff violations

**Approach.** Report E402/F401 findings as "pre-existing, not introduced by this slice" and proceed with merge.

**Why it seemed promising.** The violations genuinely predate this slice — the bootstrap script had the same `sys.path → imports` pattern before Task 9 added imports.

**Why rejected.** User challenged the reasoning. The verification pass IS the right time to clean up lint debt in files touched by the slice. "Pre-existing" explains provenance but doesn't justify leaving known issues.

**What it taught.** Distinguish between "who introduced it" and "should we fix it now." The relevant question for verification is scope, not blame.

### 2. Deferring P1 fixes to the next slice

**Approach.** Track the P1s as known issues and fix them as part of the pending-request capture slice.

**Why it seemed promising.** Would avoid an extra merge cycle and keep the fix in the same work stream.

**Why rejected.** User directed separate fix branch. Both P1s are correctness bugs on main — replay bypass and untracked worktree leak. Leaving them live during the inter-slice period is wrong.

**What it taught.** Correctness bugs on main get immediate fixes. Design-level concerns (the 8 amendment candidates) can wait. The distinction is behavioral impact: P1s change runtime behavior; amendments improve design quality.
