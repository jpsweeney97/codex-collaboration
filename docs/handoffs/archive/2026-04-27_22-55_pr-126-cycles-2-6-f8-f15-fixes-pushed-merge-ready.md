---
date: 2026-04-27
time: "22:55"
created_at: "2026-04-28T02:55:00Z"
session_id: 81915c18-64bf-4f55-af62-ac4712fa14d4
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-27_22-53_pr-126-review-cycle-1-six-findings-addressed-locally-awaiting-push-approval.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: e0c2ed1d
title: PR #126 cycles 2-6 — F8-F15 fixes pushed, merge-ready
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/dialogue.py
  - packages/plugins/codex-collaboration/server/resolution_registry.py
  - packages/plugins/codex-collaboration/skills/delegate/SKILL.md
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_resolution_registry_capture_ready.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_async_integration.py
  - docs/superpowers/specs/codex-collaboration/contracts.md
---

# Handoff: PR #126 cycles 2-6 — F8-F15 fixes pushed, merge-ready

## Goal

Close out PR #126 (T-20260423-02 Packet 1: Deferred-Approval Response) by addressing all live reviewer feedback across multiple review cycles, then push to update the PR and request re-review.

**Trigger:** Resumed from cycle-1 handoff. The branch had 6 cycle-1 commits awaiting push approval. The user immediately surfaced cycle-2 review feedback (2 P2 findings: F8 lineage repair, F9 poll-after-decide) and continued surfacing findings cycle-by-cycle until the round was clean.

**Stakes:** Packet 1 closeout completes the deferred-approval response feature and unblocks downstream Packet 1 work. The PR has live GitHub reviewer threads from `chatgpt-codex-connector` that needed concrete commit coverage before merge consideration.

**Success criteria:**
- All cycle findings (F8-F15) addressed with commits
- 5-gate verification clean (deferred per cycle-4 directive until clean round)
- Push to origin, update PR #126
- Add PR comment summarizing the cycle responses
- User confirms merge-ready

**Connection to project arc:** Packet 1 (T-20260423-02) is the deferred-approval response feature — one of several packets in the codex-collaboration build. Packet 1 introduces the worker thread model, parked-projection invariants, and the ResolutionRegistry. The race fix (F14) is the first touch of the spawn_worker → wait_for_parked handshake since the original Packet 1 implementation. Per memory: "NEXT: Merge `feature/delegate-deferred-approval-response` to `main` (or create PR)."

## Session Narrative

Resumed via `/handoff:load`. Loaded the cycle-1 handoff (`2026-04-27_22-53_pr-126-review-cycle-1-six-findings-addressed-locally-awaiting-push-approval.md`) which documented 6 prior commits (`60bceda4..d97eb8e8`) addressing cycle-1 feedback.

**Cycle 2 (immediate):** User posted two `::code-comment` blocks:
- F8 (P2, conf 0.87): `recover_startup`'s terminal-outcome catch-up emits the missing outcome but doesn't repair the lineage half. Verified-cancel paths write job=canceled → outcome → lineage="completed"; a crash between job and lineage writes leaves an active handle.
- F9 (P2, conf 0.82): Skill stops immediately after `decision_accepted: true` even though contract says poll is the sole observation surface for post-decide state.

I verified F8 by reading `delegation_controller.py:1665-1668` (timeout_interrupt_succeeded write order), `:2466 + :2510` (D4 canceled finalizer), and `:3050` (orphaned-active sweep filter — only catches running/needs_escalation, not terminal). F9 by reading `SKILL.md:271-278` (verb procedures) vs `:224` (contract paragraph) — verb procedures had drifted from the contract.

Implemented both: F8 extended the catch-up sweep at `:3073-3075` to repair lineage for canceled jobs (commit `2e276211`); F9 replaced the stop-immediately verb procedures with a single-poll same-request-suppression flow (commit `1ea52fc3`). Ran 5-gate suite — clean.

**Cycle 3:** User pushed back on F9's "single poll" framing — the consuming window meant a single poll could land in a no-op state and the skill would stop. Also flagged F10 (P2, conf 0.86): mcp_server.py:220-223 calls `dialogue.recover_startup()` BEFORE `delegation.recover_startup()`. Dialogue recovery enumerates active/unknown handles without filtering capability_class, so it can consume the F8 crash state (active execution handle + canceled job) before delegation recovery's lineage repair fires.

Key moment: User explicitly closed the F8 broad-scope question I'd flagged: "I would not blindly expand to all terminal statuses in this patch... `unknown` is not derivable from `job.status` alone because live paths intentionally split between lineage `unknown` and `completed`."

Verified F10 by reading `dialogue.py:559-602` — `_lineage_store.list(status="active"|"unknown")` has no capability filter, the for-loop tries `get_advisory_runtime()` on every handle, the exception path calls `update_status(handle, "unknown")` corrupting the F8 crash state. Verified F11 (the cycle-2 F9 was now F11 reframed) by reading `SKILL.md:283-286` — single poll didn't observe state changes, contract guarantee at `:224` was violated.

Implemented F10 as a capability-class filter at `dialogue.py:561` plus an integrated startup test in `TestRecoveryCatchup` that wires both controllers. Implemented F11 as bounded polling (up to 5 attempts) with same-request suppression. Two commits: `8578b8f4` (F10), `2fc30b19` (F11). 5-gate clean.

**Cycle 4:** User flagged two P3 findings:
- F12 (conf 0.82): `contracts.md:157` says "all active handles and all eligible unknown handles" without naming capability_class — contradicts the F10 filter at the contract layer.
- F13 (conf 0.76): SKILL.md doesn't specify any pause between bounded poll attempts. F11 commit body cited "5 × 100-500ms" intent but committed text permits 5 immediate polls.

User also said: "Address these issues. Hold off on the 5-Gate Verification until we have a round with no findings." This deferred the gate suite until F12+F13 cleared.

Implemented F12 by scoping `contracts.md` step 2 to `capability_class: advisory` with MUST-exclude clause for execution handles, plus an ownership-partition paragraph (commit `715e19b7`). Implemented F13 by reframing the bound as "~2 seconds total wall time, capped at 5 attempts" plus explicit `sleep 0.3` via Bash between same-request attempts (commit `6e6d9a44`). No 5-gate run per directive.

**Cycle 5 (the big one):** User pivoted to live PR #126 review threads via `gh`. Two unresolved threads from `chatgpt-codex-connector`:
- F1 (already covered by `7e4ffd67` from cycle-1, just unpushed)
- F14 (P1-equivalent, GitHub thread): Capture-ready signal race. `start()` calls `spawn_worker(...)` at `:746` then `wait_for_parked(...)` at `:755`. The capture channel is created INSIDE wait_for_parked (`:389-390`), so a fast worker can call `announce_parked` before the channel exists — `_deliver_capture_outcome` drops the signal at `:359` (channel is None), and `start()` blocks until `START_OUTCOME_WAIT_SECONDS` elapses, incorrectly returning `StartWaitElapsed`.

User said: "Do not push yet as-is. Treat the second GitHub comment as a real P1 and fix it locally first." Provided a specific implementation shape: pre-register channel via `open_capture_channel(job_id)` before `spawn_worker`, add `waiter_attached` flag to distinguish pre-opened-no-waiter from in-use, change `wait_for_parked` to consume an existing pre-opened channel.

Verified the race deterministically by reading the four cited line numbers and tracing the exact sequence. Confirmed the existing tests at `test_resolution_registry_capture_ready.py:60,78,94,115,157,181` mask the race with `time.sleep(0.05)` before announce — production has no such sleep.

Implemented F14 following the user's design exactly:
1. Added `_CaptureReadyChannel.waiter_attached: bool = False`
2. Added `ResolutionRegistry.open_capture_channel(job_id)` method
3. Refactored `wait_for_parked` — pre-opened channel is NOT a duplicate, attached waiter IS
4. `DelegationController.start()` calls `open_capture_channel` before `spawn_worker`
5. Added 5 new registry unit tests + 1 start-level regression test

The start-level regression test (`test_start_handles_announce_parked_arriving_before_wait_for_parked`) was the trickiest — needed to monkeypatch `spawn_worker` to fire `announce_parked` synchronously in the main thread BEFORE returning, simulating a worst-case race. Required mimicking the worker's park persistence sequence (PSR create + update_parked_request + persist_job_transition + announce_parked) using the controller's internal seams. Patched `START_OUTCOME_WAIT_SECONDS=0.5` so a regression fails fast (without F14 the test blocks for the budget).

When running focused tests, hit a flaky failure pattern: 2-3 tests in `test_delegate_decide_async_integration.py` fail intermittently when run in combination with other test files, at a worker-drain assertion (`assert not this_test_worker.is_alive()`). Reproduced at pre-F14 HEAD with my changes stashed — confirmed PRE-EXISTING. Documented in commit body and PR comment but did not investigate.

Committed F14 as a single coherent commit: `702499b0`.

**Cycle 6:** User flagged one P3 (F15, conf 0.89): The `_CaptureReadyChannel.resolved` field's old comment said "True once wait_for_parked has returned any outcome" — but post-F14, `_deliver_capture_outcome` sets `resolved=True` when an early announce buffers an outcome BEFORE wait_for_parked attaches. Field semantics shifted from "wait returned" to "outcome recorded."

Verified the claim by reading `_deliver_capture_outcome` at `:362-377` — it sets `channel.resolved = True` on first outcome delivery (line 375), regardless of whether wait_for_parked is even running. Pre-F14 this was effectively coincident with wait returning; post-F14 they're decoupled.

Updated the comment to a 7-line description: WHEN set (announce buffering OR wait timeout) + WHY read (one-shot gate in `_deliver_capture_outcome`). Comment-only change. Committed as separate follow-up `e0c2ed1d` per global default ("prefer new commits over amend") even though the user offered amending as an option.

**Cycle 7 (clean):** User confirmed no findings. Said: "Push to update PR #126." This was the round with no findings — cycle-4 directive activated, ran the 5-gate suite. All gates green: 1063 pytest (+6 from cycle-3), 0 new mypy classes, structural unchanged, 78 dialogue, 38 integration. Pushed `5629876c → e0c2ed1d` (14 commits). Posted PR comment summarizing cycles 2-6 with finding/commit table and 5-gate results. User confirmed merge-ready.

Set aside for later: pre-existing flaky tests (separate RCA), post-merge polish (RT.1 runtime Pyright, TT.1 _FakeControlPlane Protocol). Both documented but not in scope.

## Decisions

### F10 — Capability-class filter at the recovery seam, not reordering

**Choice:** Add `if handle.capability_class != "advisory": continue` filter in `dialogue.recover_startup()` rather than swapping recovery order in `mcp_server.py:220-223`.

**Driver:** User offered both options ("Run delegation recovery before dialogue recovery, or make dialogue recovery ignore non-advisory handles"). Filter chosen because the bug is dialogue *treating* execution handles like advisory, not the *order* of recovery. Filter encodes the ownership boundary at the seam where it's actually enforced.

**Rejected:** Recovery reordering — would have closed the race but left a latent bug where dialogue's recovery would still try to consume execution handles in any future scenario where it ran first.

**Implication:** Each capability class owns its own recovery responsibility. Future capability classes (if added) must filter the lineage store by capability — encoded as a contract invariant in F12.

**Trade-offs:** None significant — filter is one line.

**Confidence:** High (E2) — verified by reading `dialogue.py:559-602` (no capability filter), `lineage_store.list()` signature (no capability_class kwarg), and the F8 crash state trace. Confirmed by integration test passing.

**Reversibility:** High — single-line guard, easy to revert.

**Change trigger:** If lineage store gets a built-in capability_class filter parameter, the inline guard could move to the call site (filter before iterating). That's a refactor, not a behavioral change.

### F11 — Bounded polling AND explicit pause (not OR)

**Choice:** Implement both options the reviewer offered for F13: time-window framing (~2 s total) AND explicit `sleep 0.3` via Bash between same-request attempts.

**Driver:** Either alone leaves a gap — time-window framing without pause means 5 immediate polls could exhaust the budget in <500 ms (the gap reviewer flagged). Pause without time-window means readers don't understand the budget magnitude. Combined, the time window is the primary bound and the pause makes it achievable when MCP latency is fast.

**Rejected:** Time-window only — readers wouldn't know how to enforce it. Pause only — unclear how many attempts is "small bounded."

**Implication:** Skill becomes more prescriptive (specifies Bash sleep), but Bash is already in `allowed-tools` (SKILL.md:11) with precedent at `:30`. No allowlist change.

**Trade-offs:** Slightly more verbose skill text. Each Bash call has overhead. Acceptable because pacing correctness matters more than skill length.

**Confidence:** High (E1) — design choice based on contract reading and reviewer's stated concern. Not empirically tested at production MCP latency.

**Reversibility:** High — skill changes only, no code commitment.

**Change trigger:** If MCP-call latency is consistently >500 ms in production, the explicit pause becomes redundant — could be removed.

### F14 — Pre-register channel before spawn (not buffer orphaned signals)

**Choice:** Pre-register the per-job capture channel via `open_capture_channel(job_id)` before `spawn_worker(...)`. Buffer arrives via the existing channel mechanism.

**Driver:** User explicitly recommended this approach: "Best fix: pre-register the per-job capture channel before spawning the worker, rather than buffering orphaned outcomes. Pre-registration preserves the existing late-signal no-op semantics after timeout; buffering would need extra lifecycle state to avoid storing truly late outcomes after the channel was already closed."

**Rejected:** Buffering orphaned outcomes — would require tracking which outcomes are "true late" (after wait popped channel) vs "racing early" (before wait attached). Adds lifecycle state without benefit.

**Rejected:** Reordering spawn_worker after wait_for_parked — wait_for_parked blocks; main thread couldn't proceed to spawn_worker.

**Implication:** Channel lifecycle gains a new state (pre-opened with `waiter_attached=False`). Future capture-related changes must consider both pre-opened and lazy-create paths.

**Trade-offs:** Slightly more complex `wait_for_parked` (two-branch entry), one new public method on the registry. Acceptable for race correctness.

**Confidence:** High (E3) — race verified by reading the 4 cited line numbers, design verified by tracing all lifecycle states, fix verified by passing both registry unit tests and start-level regression test.

**Reversibility:** Medium — public API change (`open_capture_channel` is exposed). Reverting requires removing the method and the start() call site. Backwards-compat guaranteed for direct `wait_for_parked` callers via the lazy-create branch.

**Change trigger:** None expected — race fix is correctness, not preference.

### F15 — Separate follow-up commit, not amend

**Choice:** Commit the comment correction as `e0c2ed1d` (separate follow-up), not amending into `702499b0`.

**Driver:** Global instruction default: "Always create NEW commits rather than amending, unless the user explicitly requests a git amend." User offered both options ("either as a tiny follow-up commit or by amending `702499b0` since it is still unpushed") but didn't *require* amend. Defaulted to safer choice.

**Rejected:** Amend `702499b0` — saves one commit but loses audit-trail granularity. The unpushed status made it technically safe but the global default still applies.

**Implication:** PR has 14 commits instead of 13. Reviewer can see the cycle-6 correction as its own atomic step.

**Trade-offs:** Slight commit-history noise. Acceptable for traceability.

**Confidence:** High (E2) — followed clear written rule.

**Reversibility:** N/A — committed and pushed.

**Change trigger:** N/A.

### Cycle-pattern: Stop-before-push discipline preserved across all cycles

**Choice:** After each cycle's commits, run focused verification, then STOP before pushing — wait for explicit user re-review approval.

**Driver:** Cycle-1 handoff established this pattern. User reinforced it across cycles 2-5 by NOT saying "push" until cycle-6 was clean.

**Rejected:** Push after each cycle's verification — would have shipped intermediate states with known follow-up issues to the PR.

**Implication:** Branch accumulated 14 unpushed commits before the single push at the end. The push delivered the entire stack at once.

**Trade-offs:** Reviewer doesn't see incremental progress until push. Acceptable because each cycle's commits are coherent fixes for specific findings.

**Confidence:** High (E3) — pattern explicitly confirmed by user across 6 cycles.

**Reversibility:** N/A — process pattern, not code.

**Change trigger:** N/A.

## Changes

### `packages/plugins/codex-collaboration/server/delegation_controller.py` — F8 lineage repair + F14 pre-open

**Purpose:** Two distinct changes across cycles:
- F8 (cycle-2, commit `2e276211`): extend `recover_startup`'s terminal-outcome catch-up sweep at `:3073-3075` to repair active handles for canceled jobs (verified-cancel write order: job=canceled → outcome → lineage="completed"). Mirrors the live-path lineage write so a crash between the job and lineage writes is recovered to "completed".
- F14 (cycle-5, commit `702499b0`): in `start()`, call `self._registry.open_capture_channel(job_id)` immediately before `spawn_worker(...)` at the line previously known as 746. Synchronously registers the per-job capture channel under the registry lock so a fast worker's `announce_parked` always lands on a live channel.

**Approach:** F8 uses an `if job.status == "canceled"` guard inside the existing `for job in self._job_store.list()` loop that already iterates terminal jobs for outcome catch-up. Calls `_lineage_store.update_status(collaboration_id, "completed")` only when the handle is still "active". F14 is a single line of new code at the start() flow with a substantial comment explaining the race.

**Key implementation details:**
- F8: The lineage value "completed" is hardcoded — recovery cannot distinguish the rare D4 canceled+interrupted_by_unknown variant that would have written "unknown". Accepted the dominant case explicitly. Documented in the inline comment.
- F8: Idempotent — handle status already "completed" stays at "completed" (no re-write).
- F14: `open_capture_channel` is called BEFORE `spawn_worker`, not after. If `spawn_worker` raises, the channel leaks — same severity as existing job_store leak on the same path; not worsened.

**Pattern followed:** F8 extends an existing same-session sweep pattern (line 3073-3095). F14 introduces a new synchronous-handshake pattern but encapsulates it inside the registry abstraction.

**Future-Claude note:** The inline comment at `:3076-3088` explicitly enumerates the two write-order paths (timeout_interrupt_succeeded `:1665-1668` + D4 canceled-snapshot `:2466 + :2510`). If new verified-cancel paths are added, they must follow the same write order OR the catch-up sweep must be updated.

### `packages/plugins/codex-collaboration/server/dialogue.py` — F10 capability filter

**Purpose:** Filter dialogue's recovery to advisory-only handles. The lineage store is shared across capability classes; without this filter, dialogue recovery enumerates execution handles owned by `DelegationController` and routes them through the advisory runtime — corrupting state.

**Approach:** Single-line guard inside the for-loop at `:561`: `if handle.capability_class != "advisory": continue`. Plus a 9-line comment explaining the F8 + F10 interaction so a future cleanup doesn't remove the filter as "unnecessary."

**Key implementation details:**
- The guard is the first thing in the loop body — runs before the existing `recovered_cids` skip check.
- Comment explicitly references `delegation_controller.py:3091` (the F8 active-only check) and `mcp_server.py:220-223` (the recovery order).

**Pattern followed:** Inline guard rather than adding a `capability_class` kwarg to `lineage_store.list()`. Simpler, doesn't expand API surface.

**Future-Claude note:** If `lineage_store.list()` gains a `capability_class` filter, the inline guard could be replaced by `_lineage_store.list(status=..., capability_class="advisory")`. That's a clean refactor preserving the same invariant.

### `packages/plugins/codex-collaboration/server/resolution_registry.py` — F14 pre-open + F15 comment

**Purpose:** Two changes:
- F14 (cycle-5, commit `702499b0`): add `open_capture_channel(job_id)` method, add `waiter_attached: bool` field to `_CaptureReadyChannel`, refactor `wait_for_parked` to consume pre-opened channels.
- F15 (cycle-6, commit `e0c2ed1d`): correct the stale `resolved` field comment — post-F14 the field can be set BEFORE wait attaches (when an early announce buffers).

**Approach:** F14 splits the previous "channel exists" predicate into two distinct states: pre-opened (waiter can attach) vs in-use (waiter already attached). The lazy-create branch in `wait_for_parked` is preserved for backwards compatibility with the 13 existing direct callers in tests. F15 is a 9-line docstring explaining WHEN set + WHY read.

**Key implementation details:**
- `open_capture_channel`: under the registry lock, raises if `job_id` already in `_capture_channels`. Creates a fresh `_CaptureReadyChannel` and stores it.
- `wait_for_parked`: under the lock, get-or-create the channel. If it exists with `waiter_attached=False`, attach (this is pre-open consume). If it exists with `waiter_attached=True`, raise duplicate-waiter. Set `waiter_attached=True` before releasing the lock.
- Lifecycle popping unchanged — `wait_for_parked` still pops on return.

**Pattern followed:** Mirrors the per-request channel's `register/wait` pattern (worker calls `register` BEFORE `announce_parked` BEFORE `wait`).

**Future-Claude note:** The two lifecycle states (pre-opened vs in-use) are intentionally separate. Don't collapse them — `waiter_attached` exists specifically to differentiate pre-open + first wait (legitimate) from open + first wait + second wait (duplicate). Comment at `:181-186` explains.

### `packages/plugins/codex-collaboration/skills/delegate/SKILL.md` — F9 → F11 → F13 evolution

**Purpose:** Post-acceptance flow after `decide_accepted: true`. Evolved across three cycles:
- F9 (cycle-2, commit `1ea52fc3`): replaced "Stop. Do NOT auto-poll" with single-poll same-request-suppression flow.
- F11 (cycle-3, commit `2fc30b19`): replaced single poll with bounded poll (up to 5 attempts), suppression sentinel, never-auto-chain.
- F13 (cycle-4, commit `6e6d9a44`): added time-window framing (~2 s) AND explicit `sleep 0.3` via Bash between same-request attempts.

**Approach:** The procedure section grew from 4 lines to ~10 lines across cycles. Each cycle preserved the contract invariants (decision_accepted is authoritative; never auto-chain decisions) while progressively tightening the polling discipline.

**Key implementation details:**
- Final version specifies budget as primary bound (~2 s) AND attempt cap (5 attempts) — whichever exhausts first.
- Suppression sentinel applies ONLY to the just-decided request_id. A different request_id is by definition a new escalation and routes via state router.
- Pause is called out as load-bearing — without it, fast MCP latency exhausts the attempt budget inside the consuming window.

**Pattern followed:** Procedural skill instructions with explicit MCP tool names and Bash references where needed.

**Future-Claude note:** If MCP-call latency consistently exceeds 500 ms, the explicit `sleep 0.3` becomes redundant overhead. Could be removed once measured. The 5-attempt cap and ~2 s budget should remain.

### `packages/plugins/codex-collaboration/tests/test_delegation_controller.py` — F8 + F10 tests

**Purpose:** Three new tests in `TestRecoveryCatchup`:
- F8 (cycle-2): `test_recover_startup_repairs_active_lineage_for_canceled_jobs` — seeds canceled job + active handle, asserts `repaired.status == "completed"` AND outcome record emitted.
- F8 idempotency: `test_recover_startup_does_not_disturb_already_terminal_handle_for_canceled_jobs` — handle already at "completed" stays at "completed".
- F10 + F8 integration: `test_dialogue_recovery_does_not_consume_execution_handle_before_delegation_repair` — wires both DialogueController and DelegationController on the same lineage_store + journal, runs recovery in production order (dialogue first, then delegation), asserts (a) `runtime_id` and `codex_thread_id` unchanged (proves F10 filter), (b) `status == "completed"` (proves F8 repair fired), (c) outcome record emitted with `terminal_status="canceled"`.

**Approach:** F8 tests use the existing `_build_controller(tmp_path)` helper. The integration test additionally constructs a real `ControlPlane` + `DialogueController` on the same plugin-data path so both controllers share storage.

**Key implementation details:**
- Integration test seeds an execution-class handle with distinctive `runtime_id="rt-execution-original"` and `codex_thread_id="thr-execution-original"`. If F10 filter is missing, dialogue's `update_runtime` call would overwrite both — assertion catches the corruption.
- Uses `FakeRuntimeSession` + `_compat_result` + `_repo_identity` from `tests.test_control_plane` for the dialogue-side setup.

**Pattern followed:** Same TestRecoveryCatchup structure as existing same-session catch-up tests (F8 series). Integration test follows the multi-controller wiring pattern from `_build_e2e_setup` (test_delegate_start_integration.py:255-301).

**Future-Claude note:** If a future capability_class is added (beyond advisory/execution), this integration test must be extended to verify the recovery boundary holds for the new class.

### `packages/plugins/codex-collaboration/tests/test_resolution_registry_capture_ready.py` — F14 registry tests

**Purpose:** 5 new unit tests covering the pre-open lifecycle:
- `test_open_then_announce_then_wait_preserves_early_signal` — primary race-fix invariant.
- `test_open_then_wait_then_announce_works` — pre-open + late announce (legacy timing shape).
- `test_open_capture_channel_duplicate_raises` — second pre-open raises.
- `test_open_then_double_wait_raises_duplicate_waiter` — pre-open + first wait + second wait raises duplicate-waiter.
- `test_open_then_announce_buffers_all_outcome_variants` — all 4 announce variants survive pre-open buffering (Parked, TurnCompletedWithoutCapture, TurnTerminalWithoutEscalation, WorkerFailed).

**Approach:** Each test instantiates a fresh `ResolutionRegistry()`, exercises the lifecycle path, and asserts on observable state (return values + `_capture_channels` membership for popping invariants).

**Key implementation details:**
- The "all variants" test pins variant-set coverage so a future variant addition forces explicit consideration of pre-open semantics.
- Tests use `timeout_seconds=0.1` for fast-fail when the pre-open path doesn't preserve the early signal.

**Pattern followed:** Same per-test setup style as existing tests. Pre-existing tests use `time.sleep(0.05)` to mask the race — new tests deliberately do NOT sleep, exercising the synchronous handshake.

**Future-Claude note:** Total test count is now 18 (was 13). If the registry adds new lifecycle states (e.g., a "discarded" state for explicit channel cancellation), these tests should be extended.

### `packages/plugins/codex-collaboration/tests/test_delegate_start_async_integration.py` — F14 race regression

**Purpose:** One new test: `test_start_handles_announce_parked_arriving_before_wait_for_parked`. The start-level regression that proves the race fix at the controller level.

**Approach:** Monkeypatches `server.delegation_controller.spawn_worker` to a synchronous fake (`synchronous_park_worker`) that mimics the worker's park persistence sequence in the calling thread BEFORE returning. This guarantees `announce_parked` arrives before `wait_for_parked` is called — the worst-case race scenario.

**Key implementation details:**
- The fake calls: `prs.create(...)` + `controller._job_store.update_parked_request(...)` + `controller._persist_job_transition(...)` + `registry.announce_parked(...)`. Returns a `MagicMock()` instead of a real Thread.
- Patches `START_OUTCOME_WAIT_SECONDS` to `0.5` so a regression fails fast (~0.5 s wait) rather than blocking the suite for 30 s.
- Without F14: announce drops, wait_for_parked blocks for the budget, returns StartWaitElapsed → `start()` returns running DelegationJob → test fails with "F14 broken: ..." message.
- With F14: pre-open creates channel, announce buffers outcome, wait returns immediately → `start()` returns DelegationEscalation → test passes in <100 ms.

**Pattern followed:** Mirrors `test_start_returns_escalation_on_parked` setup (uses `_build_controller`, sets up minimal pending request). Uses `monkeypatch.setattr` for both spawn_worker and START_OUTCOME_WAIT_SECONDS.

**Future-Claude note:** This is the canonical test for the spawn_worker → wait_for_parked handshake. Any future change to that handshake must keep this test passing. The synchronous fake mimics worst-case worker timing — production workers are slower (real codex turn execution).

### `docs/superpowers/specs/codex-collaboration/contracts.md` — F12 contract scope

**Purpose:** Update `§Crash Recovery Contract` step 2 to specify `capability_class: advisory` and add an ownership-partition paragraph after the existing "lineage store does not participate" sentence.

**Approach:** Two edits:
1. Step 2 reworded to: "all advisory-class handles (`capability_class: advisory`) ... Execution-class handles MUST be excluded — they are owned by `DelegationController` recovery." With cross-reference to `recovery-and-journal.md §Delegation Runtime Crash`.
2. New paragraph: "The lineage store is shared across capability classes ... Each recovery path MUST filter the lineage store by capability class — touching handles outside its scope corrupts state owned by the other recovery path."

**Key implementation details:**
- Brief inline explanation of the corruption modes (runtime_id remap on success path; "unknown" on exception path) so a future reader understands why the filter is load-bearing.
- Cross-reference link uses Markdown link syntax (`[text](path#anchor)`).

**Pattern followed:** Existing contracts.md prose style — declarative, MUST/MUST NOT for invariants, with cross-references.

**Future-Claude note:** Did NOT add to `recovery-and-journal.md §Delegation Runtime Crash` — would have been scope creep beyond the cycle-4 finding. If symmetric documentation is desired, that's a follow-up.

## Codebase Knowledge

### Architecture: Capture-Ready Channel Lifecycle (post-F14)

| State | Channel exists | waiter_attached | resolved | _deliver_capture_outcome behavior |
|-------|---------------|-----------------|----------|-----------------------------------|
| Not registered | No | N/A | N/A | Drops + warn (channel is None) |
| Pre-opened | Yes | False | False | Buffers outcome + sets event + sets resolved=True |
| Pre-opened, attached | Yes | True | False | Same — sets event so attached waiter wakes |
| Resolved (early) | Yes | False | True | Drops + warn (already resolved) |
| Resolved (post-wait) | Yes | True | True | Drops + warn (channel still in dict until pop) |
| Popped | No | N/A | N/A | Drops + warn (channel is None) |

The `waiter_attached` flag distinguishes pre-opened-no-waiter (legitimate; pre-open path) from in-use (duplicate-waiter error path). Pop happens on `wait_for_parked` return regardless of outcome variant.

### Architecture: Recovery Coordination

| Component | Path | Recovery owns |
|-----------|------|---------------|
| `DialogueController.recover_startup` | `dialogue.py:522-602` | `capability_class: advisory` only (post-F10) |
| `DelegationController.recover_startup` | `delegation_controller.py` (full recovery flow) | `capability_class: execution` (job_store + lineage repair for terminal-canceled) |
| `mcp_server.py:220-223` | (`McpServer.startup`) | Calls dialogue first, then delegation |

The lineage store is shared across capability classes. Each controller's recovery filters by capability_class at its own seam.

### Patterns Identified

- **Per-package pre-registration:** Both per-request channels (worker `register` before `announce_parked`) and per-job channels (controller `open_capture_channel` before `spawn_worker`) follow the same pattern: register the channel, fire the producer, attach the consumer. F14 is the application of this pattern to the previously-implicit per-job handshake.
- **Lazy-create + pre-open compatibility:** `wait_for_parked` supports both. The lazy-create branch protects existing direct unit-test callers; the pre-open branch protects the production race. This pattern is reusable for similar handshake refactors.
- **Inline guard for shared-store recovery:** F10's `if handle.capability_class != "advisory": continue` is a minimal-impact filter pattern. Alternative would be to add a `capability_class` kwarg to `lineage_store.list()`. Chose inline for simplicity.
- **Suppression sentinel for state-machine observation:** F11's bounded poll uses the just-decided `request_id` as a suppression sentinel. While the same `request_id` keeps appearing in poll results, it's the consuming window — suppress and continue. Different `request_id` = state changed = route via state router. Pattern works for any "wait for state change" loop.

### Conventions Observed

- **Inline comments reference line numbers explicitly:** F8 comment at `delegation_controller.py:3076-3088` lists `:1665-1668`, `:2466`, `:2510`, `:3050` — gives future readers exact pointers.
- **Test setup helpers re-imported from peer test files:** `test_delegate_start_async_integration.py` imports `_build_controller` and `_command_approval_request` from `tests.test_delegation_controller`. Same module pattern in `tests.test_control_plane`. Per W4: "use module-local helpers + built-in pytest fixtures + unittest.mock."
- **Pre-existing test sleeps mask races:** Multiple tests in `test_resolution_registry_capture_ready.py` use `time.sleep(0.05)` before `announce_*`. This was the masking pattern for the F14 race. New tests deliberately omit the sleep to exercise the synchronous handshake.
- **Frozen dataclasses for value types:** `Parked`, `WorkerFailed`, etc. all use `@dataclass(frozen=True)`. Mutable state types (`_CaptureReadyChannel`, `_RegistryEntry`) use plain `@dataclass`.

### Key Locations

| Concept | Location |
|---------|----------|
| `start()` flow with F14 pre-open | `delegation_controller.py:746` (the `open_capture_channel` line) |
| F8 catch-up sweep | `delegation_controller.py:3073-3095` |
| F10 capability filter | `dialogue.py:561` |
| `_CaptureReadyChannel` dataclass | `resolution_registry.py:174-186` |
| `open_capture_channel` method | `resolution_registry.py:380-409` (post-F14) |
| `wait_for_parked` (refactored) | `resolution_registry.py:411+` (post-F14) |
| `_deliver_capture_outcome` (one-shot gate) | `resolution_registry.py:362-377` |
| Worker park sequence (production) | `delegation_controller.py:1059-1073` |
| Verified-cancel write order (timeout path) | `delegation_controller.py:1665-1668` |
| Verified-cancel write order (D4 path) | `delegation_controller.py:2466 + :2510` |
| Orphaned-running sweep | `delegation_controller.py:3050-3058` |
| Recovery order in startup | `mcp_server.py:220-223` |
| Crash Recovery Contract (post-F12) | `docs/superpowers/specs/codex-collaboration/contracts.md:152-170` |

### Dependency Graph (Capture-Ready Path)

    DelegationController.start()
      |
      +-- registry.open_capture_channel(job_id)    # F14: pre-register
      |
      +-- spawn_worker(...)                         # spawns daemon thread
      |   |
      |   +-- _execute_live_turn (worker thread)
      |       |
      |       +-- handler parks
      |           +-- prs.create(...)
      |           +-- job_store.update_parked_request(...)
      |           +-- _persist_job_transition("needs_escalation")
      |           +-- registry.register(request_id, ...)
      |           +-- registry.announce_parked(job_id, request_id=...)
      |               +-- _deliver_capture_outcome (sets resolved=True, sets event)
      |
      +-- registry.wait_for_parked(job_id, ...)    # F14: consumes pre-opened OR creates lazy
          +-- waiter_attached = True
          +-- event.wait(timeout_seconds)            # already-set if early announce
          +-- read outcome, pop channel
          +-- return outcome

### Surprising Findings

- **`_lineage_store.list()` has no `capability_class` filter.** The store is shared across capability classes but has only `repo_root` and `status` filters. F10 fix is inline at the call site, not a store API change. Documented as a future refactor opportunity.
- **`time.sleep(0.05)` in registry tests masked the race for the entire Packet 1 history.** The race existed but was undetectable in unit tests. F14 regression test deliberately omits the sleep.
- **`wait_for_parked`'s pre-F14 second-lock check (`channel_now is None`) was documented as "defensive: unreachable under current code"** at `resolution_registry.py:395-401`. Still unreachable post-F14 — the comment remains accurate.
- **The pre-existing flaky test failure mode is non-deterministic.** Depending on test order, 2-3 different tests in `test_delegate_decide_async_integration.py` fail at a `threading.enumerate()`-based worker-drain assertion. Suspected cause: thread ident collision when `max(workers, key=ident)` picks a leaked worker from an earlier test. Did not investigate.
- **Pre-existing carry-forward Pyright/mypy items are stable.** RT.1 (`runtime.py:270` Literal narrowing), TT.1 (`_FakeControlPlane` Protocol mismatches at multiple test sites). Net mypy delta vs merge-base `005d4b44` is −3 (improved). No new errors introduced across all 14 commits.

## Conversation Highlights

**Cycle-2 acknowledgment of F8 broad-scope question (cycle-3 message):**

User: "On your F8 broad-scope question: I would not blindly expand to all terminal statuses in this patch. `completed`/`failed`/`canceled` can plausibly repair to lineage `completed`, but `unknown` is not derivable from `job.status` alone because live paths intentionally split between lineage `unknown` and `completed`. That needs either provenance or a separately documented conservative recovery rule. The immediate blocker is the recovery ordering/filtering issue above."

— Closed F8 broad-scope as decided (canceled-only). Drove F10 implementation focus.

**Cycle-4 directive on 5-gate timing:**

User: "Address these issues. Hold off on the 5-Gate Verification until we have a round with no findings."

— Established a clear cycle protocol: focused tests per cycle, full 5-gate only when clean. Activated at cycle-7 (cycle-6 was the clean round).

**Cycle-5 on F14 design (the user provided a complete implementation shape):**

User: "Best fix: pre-register the per-job capture channel before spawning the worker, rather than buffering orphaned outcomes. Pre-registration preserves the existing late-signal no-op semantics after timeout; buffering would need extra lifecycle state to avoid storing truly late outcomes after the channel was already closed.

Suggested implementation shape:
- Add a small `ResolutionRegistry.open_capture_channel(job_id)` or equivalent.
- Add a `waiter_attached` flag to `_CaptureReadyChannel`, so pre-opened/no-waiter is distinct from duplicate concurrent waiters.
- In `DelegationController.start()`, call the new open/register method immediately before `spawn_worker(...)`.
- Change `wait_for_parked()` to consume an existing pre-opened channel, return immediately if an early outcome already arrived, and still lazily create the channel for direct unit-test/backward-compatible callers if needed.
- Add at least one registry unit test for `open -> announce_parked -> wait` preserving the early signal.
- Add a start-level regression if practical by monkeypatching `spawn_worker` to emit a capture-ready outcome before `start()` calls `wait_for_parked()`."

— I followed this shape exactly. The user did the design work; my job was implementation fidelity. Implemented all 6 bullet points.

**Cycle-5 on push timing:**

User: "Do not push yet as-is. Treat the second GitHub comment as a real P1 and fix it locally first."

— Reinforced stop-before-push discipline. Confirmed F1 was already covered by `7e4ffd67` and only F14 needed work before push.

**Cycle-6 on commit choice (amend vs follow-up):**

User: "I would make the one-line comment fix above before pushing, either as a tiny follow-up commit or by amending `702499b0` since it is still unpushed."

— Offered both options. I chose follow-up commit per global default (prefer new commits over amend). User did not push back on the choice.

**Cycle-7 push directive:**

User: "Push to update PR #126"

— Single-line directive. Activated cycle-4's deferred 5-gate, ran it, all green, pushed.

**Cycle-7 final confirmation:**

User: "I agree: PR #126 is ready for re-review and merge consideration. The important boundary is clean: Both live GitHub reviewer threads have concrete commit coverage. Full gates are green after the pushed stack. Carry-forward items are explicitly post-merge polish, not merge blockers for Packet 1."

— Confirmed merge-readiness. Stop discipline preserved through to the final push.

**Working style observed:**
- User does verification independently each cycle (`git diff --check`, focused pytest, ruff). Reports their own results.
- User provides detailed `::code-comment` blocks with file paths, line numbers, priority, and confidence scores.
- User often provides specific implementation shapes (especially F14) — expects fidelity to the shape, not improvisation.
- User maintains stop-before-push discipline rigorously across cycles. Each push is explicit.
- User is comfortable with technical pushback when warranted (e.g., F8 broad-scope: "I would not blindly expand").

## Context

### Project State (post-push)

- PR #126: HEAD updated to `e0c2ed1d`. Two GitHub reviewer threads have commit coverage. Awaiting re-review and merge.
- Branch `feature/delegate-deferred-approval-response`: 14 commits ahead of origin's previous head `5629876c`, now matched.
- Packet 1 (T-20260423-02): All 22 tasks across 8 phases were complete pre-resume per memory. This session added 14 commits of cycle-driven fixes on top of that.
- Carry-forward items unchanged from cycle-3 baseline:
  - RT.1: `runtime.py:270` Pyright TurnStatus literal narrowing
  - TT.1: `_FakeControlPlane` Protocol mismatches at multiple test instantiation sites

### Environment

- Python 3.14.2 via mise
- pytest 9.0.2
- mypy + ruff via uv workspace at repo root
- Test runner: `PYTHONPATH=. uv run --package codex-collaboration pytest <path> -q`
- 1063-test full suite runs in ~250 s

### Mental Model

The PR review cycles are a **convergence loop**: reviewer surfaces findings → fix → reviewer re-checks. Each cycle tightens the implementation on a different axis (correctness → coverage → contract-language → comment-accuracy). The 5-gate verification is the meta-loop checkpoint — only run when the per-cycle loop has converged (no findings).

**Key insight:** The cycles' findings followed a predictable pattern — first cycles surfaced functional bugs (F8, F9, F10, F14), middle cycles surfaced contract/instruction precision gaps (F11, F12, F13), final cycle surfaced documentation drift (F15). This ordering reflects a healthy review process — defects shallow first, polish last.

**Mental model for F14 specifically:** The race is a **boundary fidelity loss** between the main thread and the worker thread. The pre-existing tests masked it with `sleep(0.05)`, which is the production race window. F14 closes the race by making the channel registration synchronous (under the registry lock) at a point that's strictly before the producer can fire — a rendezvous protocol.

## Learnings

### The "channel exists" predicate was overloaded; F14 split it correctly

**Mechanism:** Before F14, `wait_for_parked`'s duplicate-detection used `if job_id in self._capture_channels: raise`. This conflated "another waiter is in flight" with "channel was pre-registered". Splitting via `waiter_attached` resolves the conflict: pre-opened channels can have a waiter attach without being a duplicate; only attached-then-second-attach is a duplicate.

**Evidence:** Direct comparison of pre-F14 and post-F14 `wait_for_parked` (commit `702499b0`). Pre-F14: line 384-388 raises on dict membership. Post-F14: line ~395 raises on `channel.waiter_attached=True`.

**Implication:** Future channel-state predicates should be similarly explicit. "Channel exists" is too coarse — usually you want "channel exists in state X." Codify the lifecycle states as boolean flags.

**Watch for:** New `_CaptureReadyChannel` operations should consider all 4-5 lifecycle states explicitly. Don't assume "channel exists" means "ready to use" — check `waiter_attached` and `resolved` for the operation's invariants.

### Pre-existing `time.sleep` in tests is a yellow flag for hidden races

**Mechanism:** When a test does `thread.start(); time.sleep(0.05); produce_signal()`, the sleep is masking a thread-ordering assumption. The test passes because the consumer is reliably ready before the producer fires. Production has no such sleep — and a fast producer wins the race.

**Evidence:** All 6 pre-F14 announce-test variants in `test_resolution_registry_capture_ready.py:60,78,94,115,157,181` use `time.sleep(0.05)` before `announce_*`. The race existed for the lifetime of Packet 1 but was undetected.

**Implication:** When auditing test files, treat unconditional `time.sleep` between thread start and producer call as a smell. The test should pass without the sleep — if it doesn't, there's a race.

**Watch for:** Any new test that mirrors this pattern. Prefer the pre-open + synchronous handshake pattern (test_open_then_announce_then_wait_preserves_early_signal) over the sleep-and-hope pattern.

### Contract-text and runtime-code can drift; encode invariants at both layers

**Mechanism:** F12 caught a contract-text drift: `contracts.md:157` said "all handles" but the runtime filter at `dialogue.py:561` said "advisory only" (post-F10). The runtime was correct; the contract was stale. A future cleanup that read only the contract could remove the runtime filter as "unnecessary."

**Evidence:** Pre-F12 `contracts.md:157` made no mention of capability_class. Post-F12 step 2 explicitly scopes to `capability_class: advisory` with MUST-exclude clause for execution.

**Implication:** When fixing a runtime invariant, audit whether the contract layer encodes the same invariant. If not, the contract is a regression risk.

**Watch for:** Any future filter or guard added to recovery code should be reflected in `contracts.md §Crash Recovery Contract` or the equivalent contract section.

### Pre-existing test flakiness is real but separate

**Mechanism:** `test_delegate_decide_async_integration.py` worker-drain assertions fail intermittently when run combined with other test files. The failure pattern is `assert not this_test_worker.is_alive()` after a 10-s join timeout. Likely cause: `threading.enumerate()` + `max(workers, key=ident)` picks a leaked worker thread from an earlier test (thread idents can be reused).

**Evidence:** Reproduced at pre-F14 HEAD with my F14 changes stashed — 3 tests failed instead of 2 (without F14 added a new test that mostly succeeds). When run in isolation (only `test_delegate_decide_async_integration.py`), all 20 tests pass.

**Implication:** Not a Packet 1 blocker. A separate RCA is warranted for production CI stability. Likely fixes: filter `threading.enumerate()` results by thread ident range, or use a controller-internal thread tracker instead of name-based enumeration.

**Watch for:** If the flakiness lands in production CI gates, this is the entry point for investigation.

### Stop-before-push discipline scales across many cycles

**Mechanism:** User reinforced stop-before-push at every cycle. The branch accumulated 14 commits before the single push. Each commit was reviewable as a discrete fix.

**Evidence:** 6 cycle commits (cycle-1 from prior session) + 8 cycle commits (this session) = 14 unpushed commits. User explicitly directed push only after cycle-7 cleared.

**Implication:** For complex multi-cycle PR review, stop-before-push prevents the PR from getting noisy with intermediate states. Reviewer sees a coherent stack, not a bunch of WIP commits.

**Watch for:** Future multi-cycle reviews should preserve this pattern. Resist the urge to push after a "clean" cycle — wait for explicit user approval.

## Next Steps

### 1. Wait for cycle-7 reviewer re-run on `e0c2ed1d`

**Dependencies:** Push complete. PR comment posted. User confirmed merge-ready.

**What happens next:** `chatgpt-codex-connector` (or human reviewer) runs against the new HEAD. If clean, PR is ready to merge. If new findings surface, repeat the cycle protocol (focused fix → user re-review → push).

**Acceptance criteria:** No new P1/P2 findings. P3 findings are negotiable based on impact.

### 2. Merge to main

**Dependencies:** Reviewer approval.

**What to read first:** PR #126 final state at `https://github.com/jpsweeney97/claude-code-tool-dev/pull/126`.

**Approach:** Squash or merge-commit per project convention. Per memory: "NEXT: Merge `feature/delegate-deferred-approval-response` to `main` (or create PR)." The PR is already created (#126), so merge action.

**Acceptance criteria:** main updated, branch deleted (or kept for backref).

### 3. Post-merge polish (RT.1, TT.1) — optional

**Dependencies:** Merge complete.

**What to read first:**
- RT.1: `runtime.py:270` Pyright TurnStatus literal narrowing
- TT.1: `_FakeControlPlane` Protocol mismatches at multiple test instantiation sites in `test_delegation_controller.py`

**Approach:** Both are typing-only fixes with no behavioral impact. RT.1 needs a `cast(TurnStatus, ...)` or similar narrowing. TT.1 needs `_FakeControlPlane` to satisfy `_ControlPlaneLike` Protocol — likely add a `start_execution_runtime` overload returning `AppServerRuntimeSession` (or `tuple[str, AppServerRuntimeSession, str]`).

**Acceptance criteria:** Pyright clean for both surfaces. Mypy net delta improves further.

**Potential obstacles:** TT.1 may require updating multiple `_FakeSession` types across test files. Could be larger than expected.

### 4. Pre-existing flaky test RCA — optional

**Dependencies:** None (separate from Packet 1).

**What to read first:** `test_delegate_decide_async_integration.py:707-714` (the worker-drain assertion).

**Approach:** Hypothesis: `threading.enumerate()` + `max(workers, key=ident)` picks a leaked worker thread from an earlier test. Fix candidates: (a) filter `enumerate()` results by `is_daemon` + thread state, (b) use a controller-internal thread tracker instead of name-based enumeration, (c) ensure all test fixtures explicitly join their worker threads in teardown.

**Acceptance criteria:** Combined-suite runs stable across multiple invocations. No intermittent failures.

**Potential obstacles:** Race may be in test fixture lifecycle, not the assertion itself. Could require fixture rework across multiple test files.

## In Progress

Clean stopping point — push complete, PR comment posted, user confirmed merge-ready, no work in flight.

## Open Questions

None. All findings addressed. Cycle-7 reviewer re-run is awaited but does not block this handoff.

## Risks

### Pre-existing flaky tests

**Concern:** Combined-suite runs of `test_delegate_decide_async_integration.py` with other test files exhibit intermittent failures (2-3 tests, non-deterministic which ones).

**Likelihood:** Medium — reproduces in roughly half of combined-suite runs.

**Impact:** Low for Packet 1 (verified to pre-date F14). Could cause CI flakes if the combined-suite ordering hits the failure pattern.

**Mitigation:** Run `test_delegate_decide_async_integration.py` in isolation if needed. Separate RCA documented as next-steps item.

### Single-poll consuming-window edge case (post-F11/F13)

**Concern:** Bounded poll cap is 5 attempts at ~300 ms each = ~1.5 s. If MCP latency is consistently below 200 ms in production AND worker dispatch latency exceeds 1.5 s, the bounded poll always reports "still dispatching" and the user must re-run `/delegate`.

**Likelihood:** Low — production worker dispatch should be sub-second for normal operations.

**Impact:** UX degradation — user sees "worker is still dispatching" even when the system is functional. Not a correctness issue.

**Mitigation:** Increase cap if production telemetry shows the message firing frequently. Documented in F13 commit body.

### Carry-forward typing items (RT.1, TT.1)

**Concern:** Both items are pre-existing typing issues that weren't fixed in this session.

**Likelihood:** N/A (pre-existing).

**Impact:** Low — Pyright/mypy report errors but no runtime impact.

**Mitigation:** Documented as next-steps item. Optional post-merge polish.

## References

### Commits (cycles 2-6, this session)

| Commit | Subject | Cycle | Finding |
|--------|---------|-------|---------|
| `2e276211` | fix(delegate): repair active lineage handle for canceled jobs in catch-up sweep | 2 | F8 |
| `1ea52fc3` | fix(delegate): poll for next state after accepted decide instead of stopping | 2 | F9 |
| `8578b8f4` | fix(delegate): filter dialogue recovery to advisory-only handles | 3 | F10 |
| `2fc30b19` | fix(delegate): bounded poll-for-next-state instead of single poll after accepted decide | 3 | F11 |
| `715e19b7` | docs(codex-collab): scope crash-recovery contract to advisory handles + note execution-handle ownership | 4 | F12 |
| `6e6d9a44` | fix(delegate): explicit pause + time-window framing for bounded poll-for-next-state | 4 | F13 |
| `702499b0` | fix(delegate): pre-register capture-ready channel before spawn_worker to close announce-before-wait race | 5 | F14 |
| `e0c2ed1d` | docs(delegate): correct stale `resolved` field semantics on _CaptureReadyChannel | 6 | F15 |

### Cycle-1 commits (prior session, also in stack)

| Commit | Subject |
|--------|---------|
| `60bceda4` | fix(delegate): preserve raw JSON-RPC wire id through worker session.respond |
| `7e4ffd67` | fix(delegate): align decide() journal key with worker dispatched/completed key |
| `9b05cdce` | fix(delegate): migrate skill to async decide accepted-for-dispatch contract |
| `f4c971db` | fix(delegate): add canceled to skill Tier 4 routing + discard allowed states |
| `d221efff` | fix(delegate): include canceled in terminal-outcome catch-up sweep |
| `d97eb8e8` | docs(delegate): clean stale decide producer + strip phase-doc EOF blanks |

### PR and review threads

- PR #126: `https://github.com/jpsweeney97/claude-code-tool-dev/pull/126`
- PR cycles summary comment: `https://github.com/jpsweeney97/claude-code-tool-dev/pull/126#issuecomment-4332026993`
- Two GitHub reviewer threads (from `chatgpt-codex-connector`):
  - Approval journal key (covered by `7e4ffd67`)
  - Capture-ready signal race (covered by `702499b0` + `e0c2ed1d`)

### Files

- `packages/plugins/codex-collaboration/server/delegation_controller.py` — F8 + F14
- `packages/plugins/codex-collaboration/server/dialogue.py` — F10
- `packages/plugins/codex-collaboration/server/resolution_registry.py` — F14 + F15
- `packages/plugins/codex-collaboration/skills/delegate/SKILL.md` — F9 + F11 + F13
- `packages/plugins/codex-collaboration/tests/test_delegation_controller.py` — F8 + F10 tests
- `packages/plugins/codex-collaboration/tests/test_resolution_registry_capture_ready.py` — F14 unit tests
- `packages/plugins/codex-collaboration/tests/test_delegate_start_async_integration.py` — F14 regression
- `docs/superpowers/specs/codex-collaboration/contracts.md` — F12

### Key spec sections

- `contracts.md §Crash Recovery Contract` (post-F12)
- `contracts.md §Decide` ("poll is the sole observation surface for post-decide state" — drove F11)
- `recovery-and-journal.md §Advisory Runtime Crash`
- `recovery-and-journal.md §Delegation Runtime Crash`

## Gotchas

### `lineage_store.list()` has no capability_class filter

The store at `lineage_store.py:145-157` has `repo_root` and `status` filters but NOT `capability_class`. F10's fix is an inline guard at the call site, not a store API change. If you're auditing recovery code, remember that any iteration over `_lineage_store.list(...)` must filter by capability_class manually.

### `wait_for_parked` has TWO entry shapes (post-F14)

- Pre-opened (production): channel exists, `waiter_attached=False`, attach waiter.
- Lazy-create (legacy/tests): channel doesn't exist, create + attach.

Don't add code that assumes only one shape. The duplicate-waiter check uses `waiter_attached`, NOT channel existence.

### `_CaptureReadyChannel.resolved` is set BEFORE wait returns (post-F14)

Pre-F14, `resolved=True` happened at the same time as `wait_for_parked` returning. Post-F14, `resolved=True` can fire when an early `announce_*` buffers an outcome — BEFORE wait attaches. The F15 commit `e0c2ed1d` updated the comment to reflect this. Don't assume `resolved` correlates with wait state.

### F8 fix uses hardcoded "completed" lineage value

The F8 catch-up sweep at `delegation_controller.py:3089-3094` hardcodes the lineage repair value to "completed". This mirrors the dominant verified-cancel path (timeout_interrupt_succeeded + D4 canceled-snapshot finalizer). Recovery cannot distinguish the rare D4 canceled+interrupted_by_unknown variant that would have written "unknown". If new verified-cancel paths are added with different lineage values, the catch-up sweep needs updating.

### F14 race regression test is intentionally synchronous

`test_start_handles_announce_parked_arriving_before_wait_for_parked` monkeypatches `spawn_worker` to a synchronous fake that fires `announce_parked` BEFORE returning. This is NOT how production workers behave (they're async daemon threads). The test deliberately uses worst-case timing to exercise the race-fix surface deterministically.

### `START_OUTCOME_WAIT_SECONDS = 30` in production but tests must override

The race regression test patches `START_OUTCOME_WAIT_SECONDS` to `0.5` so a regression fails fast. If you copy this test pattern for new race scenarios, remember to patch the wait budget — otherwise a regression blocks the suite for 30 s.

### Combined-suite runs can hit pre-existing flakiness

When running multiple test files together (e.g., `test_resolution_registry_capture_ready.py + test_delegation_controller.py + test_delegate_start_async_integration.py + test_delegate_decide_async_integration.py`), 2-3 tests in `test_delegate_decide_async_integration.py` may fail at a worker-drain assertion. This is PRE-EXISTING (reproduces at pre-F14 HEAD). Run in isolation if hit.

### Bash `sleep 0.3` in SKILL.md is intentional, not improvisation

The F13 fix specifies `sleep 0.3` via Bash between same-request poll attempts. This is the canonical mechanism — Bash is in the skill's `allowed-tools` (SKILL.md:11) with precedent at `:30`. Don't replace with another sleep mechanism.

### Cycle-pattern: stop-before-push is mandatory unless user says push

The user explicitly directs push at the end of each cycle. Don't push after running tests "looks clean" — wait for the explicit push directive. This pattern was reinforced 6 times across cycles 2-7.
