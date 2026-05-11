---
date: 2026-04-25
time: "17:50"
created_at: "2026-04-25T21:50:00Z"
session_id: 4f249288-dfea-4d18-bda2-80c2334fb7ff
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-25_16-43_phase-f-task-16-convergence-map-drafted.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: 475d0506
title: Phase F Task 16 implementer BLOCKED on 23-test deadlock — 3 options pending adjudication; uncommitted working tree; fresh-session dispatch required
type: handoff
files:
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-dispatch-packet.md
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_handler_branches_integration.py
---

# Handoff: Phase F Task 16 implementer BLOCKED on 23-test deadlock — 3 options pending adjudication; uncommitted working tree; fresh-session dispatch required

## Goal

Construct the Phase F Task 16 dispatch packet, dispatch the implementer agent, and drive the implementation to a feat commit. Task 16 is the LARGEST task in T-20260423-02 Packet 1 (Deferred-Approval Response): handler rewrite for async-decide model + 6 sentinel raise sites + 3 new helpers + registry init + module constant + 8 `update_parked_request` callsites + 4 `completion_origin="worker_completed"` writes.

**Trigger:** Resumed from `2026-04-25_16-43_phase-f-task-16-convergence-map-drafted.md` at commit `475d0506` on `feature/delegate-deferred-approval-response`. Prior session adjudicated option (b) and drafted the convergence map; this session was the dispatch-packet construction + dispatch + implementer execution.

**Stakes:** Task 16 commit is BLOCKED on a structural scope discovery the convergence map missed: `_server_request_handler` now calls `registry.wait()` synchronously, but `start()` is still synchronous pre-Task-17 (no worker thread, no `wait_for_parked()`). ~23 currently-passing tests deadlock indefinitely under the new handler. Adjudication of options A/B/C is required before the feat commit can land.

**Success criteria (achieved this session):**
- Dispatch packet drafted at `task-16-dispatch-packet.md` (212 lines), reviewed via two-read protocol, refined with 4 user corrections (autospec swap, `DecisionResolution` payload examples, fake-session invocation requirement, L6 grep precision; plus convergence-map row 2 fix)
- Pre-read BLOCKED guard added to packet
- Implementer dispatched in background (`task-16-implementer`, sonnet, general-purpose, no worktree isolation)
- Implementer ran ~47 minutes, wrote handler + helpers + tests, hit deadlock during `pytest` validation, reported BLOCKED with structured 3-option question

**Success criteria NOT achieved (deferred to fresh session):**
- Feat commit NOT landed (working tree uncommitted)
- Adjudication of options A/B/C
- Pyright diagnostics resolution (5 ✘, 7 ★)
- SendMessage continuation to implementer with adjudicated path

**Connection to project arc:** Phase F Task 15 closed Task 16's prerequisite scaffold. Task 16 closes A2 + C10.4 + audits A3, then Phase F closes. Phase G (Tasks 17-18) starts after that. The 23-test deadlock is a HORIZONTAL surface — option (a) reclassifies them as Task 17 unblock candidates (joining the 8 Task 14 skips), which means Task 17 unblocks ~31 tests at once, not 8.

## Session Narrative

**Stage 1 — Resumption + handoff load.** Started by `/handoff:load` (state file written at `docs/handoffs/.session-state/handoff-4f249288-...`). Prior handoff `2026-04-25_16-43_phase-f-task-16-convergence-map-drafted.md` resumed cleanly. Re-read convergence map (264 lines) + Task 16 plan body (`phase-f-worker.md:377-1189`, 813 lines) + spec sentinel section (`design.md:450-558`, 109 lines) + carry-forward (167 lines) + Task 15 convergence map as template (131 lines) — all in parallel.

**Stage 2 — Dispatch packet drafted.** Wrote `task-16-dispatch-packet.md` (206 lines initial; user-refined to 212 lines). Structure: metadata + agent invocation pattern + Implementer Prompt section (mission, authority sources, L4 critical fix, L9 stop-rule disposition, test harness pattern, code/tests/closeout-docs acceptance summaries, commit shape, reporting contract, boundaries, mid-task questions, begin) + Post-implementer review chain (controller-only; excluded from agent prompt).

Key drafting choices:
- Did NOT inline convergence map (264 lines) — pointed to it as binding authority. Implementer reads in-place.
- Did NOT pre-draft per-test scaffold (per D6 precedent)
- Inlined high-leverage items: L4 trap with full pseudocode delta, L9 disposition with verbatim skip-reason citation, 3 grep invariants in acceptance criteria
- Recommended `MagicMock(spec=ResolutionRegistry)` initially (one judgment call within lock-bounds)

**Stage 3 — User two-read refinement (third successive instance).** User performed independent `/copy`-output review and made 4 refinements:
1. **Test double swap (line 90):** `MagicMock(spec=ResolutionRegistry)` → `create_autospec(ResolutionRegistry, instance=True)`. Reasoning: plain `MagicMock(spec=...)` does NOT enforce kw-only argument signatures; `create_autospec` does. Converts L4 from soft guidance into hard test-failure enforcement.
2. **Harness guidance tightening (line 91):** Added explicit `DecisionResolution` payload+kind examples for each branch (dispatch-failure, timeout-cancel, timeout-interrupt, internal-abort), requirement to attach `respond` to `_FakeSession` (which only defines `interrupt_turn`), and explicit warning against making `run_execution_turn` raise `_WorkerTerminalBranchSignal` (would only retest Task 15 catch surface).
3. **L6 grep precision (line 105):** `grep "update_parked_request"` → `grep "self\\._job_store\\.update_parked_request"` returning exactly `8`, not `≥8`. Avoids counting the docstring reference at `_WorkerTerminalBranchSignal:208`.
4. **Convergence map row 2 fix:** Branch matrix row 2 (timeout cancel-success) updated to explicitly say `none (handler returns None)` in Sentinel column for symmetry with row 1 — was malformed.

User verdict: "I'd call the dispatch packet credible and ready to use, assuming the implementer agent can read the untracked files in this same worktree."

**Stage 4 — Untracked-file caveat adjudicated.** User flagged structural risk: convergence map + dispatch packet are untracked. Three paths considered:
- Path A: dispatch in-place, no commit, no inlining
- Path B: pre-commit the docs first (breaks Task 15 D4 precedent)
- Path C: inline convergence map in `Agent.prompt` (drift risk + 50% larger prompt)

User picked Path A (dispatch in-place) with one caveat: pass ONLY the Implementer Prompt section, not the controller-only review-chain section. Added a "missing file → BLOCKED" pre-read guard to the packet (lines 30-31).

**Stage 5 — Background dispatch.** Invoked `Agent({name: "task-16-implementer", subagent_type: "general-purpose", model: "sonnet", run_in_background: true})` with the Implementer Prompt section (lines 23-196 of dispatch packet) as the prompt. Agent ID: `a59d25972ffe55f77`. Background mode chosen because Task 16 is large and foreground streaming would consume controller context.

**Stage 6 — Implementer ran 47 minutes, then BLOCKED.** Agent ran 2,833 seconds and 167 tool uses, executed Steps 16.1-16.7, wrote production code + new test file, then hit a deadlock during the full-suite `pytest` validation. Confirmed hang on `test_start_with_command_approval_returns_escalation` at `tests/test_delegation_controller.py:1320` (>10s, no output). Reported BLOCKED with structured 3-option question (A/B/C below).

**Stage 7 — Diagnostics surfaced alongside BLOCKED.** Pyright reported 5 errors + 7 warnings on the implementer's working-tree changes:
- `delegation_controller.py:834` — `entry: ExecutionRuntimeEntry | None` not narrowed before passing to `_mark_execution_unknown_and_cleanup(entry: ExecutionRuntimeEntry)`
- `delegation_controller.py:1030` — `_FakeSession.respond` attribute unknown
- `delegation_controller.py:1349` — same
- `test_handler_branches_integration.py:27` — pytest import not resolved (pyright config issue, not real)
- `test_handler_branches_integration.py:227, 434, 718, 758` — `_FakeSession.respond` attribute not declared (test attaches at runtime)
- 2 unused-variable warnings + 5 unused-parameter warnings

**Stage 8 — Save trigger.** Context at 199k/200k tokens (100%). Controller flagged immediately and recommended /handoff:save without further analysis. User confirmed.

## Decisions

### D1: Dispatch packet construction completed in this resumed session despite 89%-start context

**Choice:** Drafted full 212-line dispatch packet in this session, dispatched implementer in background, monitored for completion.

**Driver:** Prior handoff Next Steps §1 explicitly directed "Fresh-session dispatch packet construction"; user confirmed by saying "Yes, start by re-reading `task-16-convergence-map.md` and the Phase F plan body for Task 16, then assemble the implementer prompt."

**Alternatives considered:**
- **Defer to even fresher session.** Rejected — user explicit ask; dispatch packet is one-time artifact (not a 264-line working doc); convergence map exists already.
- **Construct packet via parallel agent.** Rejected — controller-side packet construction needs full convergence-map context, which is in this session.

**Implications:** Dispatch packet exists as durable working artifact at `task-16-dispatch-packet.md`. Reusable by future tasks of similar shape (Task 16-class dispatches). Pattern: convergence-map drafting (one session) → dispatch-packet construction + dispatch + implementation (one or more sessions, depending on agent runtime).

**Trade-offs accepted:** Used ~110k context constructing + dispatching + handling BLOCKED; reached 100% before adjudication could happen. Adjudication deferred to fresh session.

**Confidence:** High (E2) — explicit user ask + Task 15 D5 precedent.

**Reversibility:** N/A — dispatch happened.

**Change trigger:** None.

### D2: Path A (dispatch in-place, no pre-commit, no inlining)

**Choice:** Dispatched `task-16-implementer` agent without `isolation: "worktree"`, with the convergence map + dispatch packet still untracked in working tree. Pre-read BLOCKED guard added as fail-fast safeguard.

**Driver:** User adjudication (verbatim): "I recommend **Path A: dispatch in-place, no pre-commit, no full inlining**. The belt-and-suspenders concern is real, but the failure mode is narrow here: you are not using worktree isolation, and the implementer needs to edit this same worktree."

**Alternatives considered:**
- **Path B (pre-commit docs first).** Rejected per user: "would also make the dispatch packet look like a durable task artifact before execution has tested whether it was fully sufficient. That weakens the Task 15 D4 precedent."
- **Path C (inline convergence map).** Rejected per user: drift risk + ~50% larger prompt + duplication.

**Implications:** Convergence map + dispatch packet stay untracked, will commit alongside Task 16 closeout-docs per Task 15 D4 precedent. Pre-read guard converts file-readability from soft assumption into fail-fast contract.

**Trade-offs accepted:** Dispatch packet's full sufficiency only verifiable post-execution — confirmed in this session by the BLOCKED report (which proves the packet's reporting contract worked as designed; see L1 below).

**Confidence:** High (E3) — explicit user adjudication + worked as designed.

**Reversibility:** N/A.

**Change trigger:** None.

### D3: Background mode for Agent dispatch

**Choice:** Invoked agent with `run_in_background: true`. Controller does NOT poll; runtime notifies on completion.

**Driver:** Task 16 is the largest task in the plan (~420 LoC + 12 tests + multiple commits). Foreground streaming would consume controller context for ~47 minutes of intermediate work that wasn't actionable.

**Alternatives considered:**
- **Foreground dispatch.** Rejected — context budget concern; intermediate streaming not useful.
- **Foreground with periodic monitoring.** Rejected — same context concern.

**Implications:** Controller stayed available for parallel work during agent execution (none requested by user). Notification fired on BLOCKED report. Agent transcript at `/private/tmp/claude-501/-Users-jp-Projects-active-claude-code-tool-dev/4f249288-dfea-4d18-bda2-80c2334fb7ff/tasks/a59d25972ffe55f77.output` (DO NOT read — context overflow).

**Trade-offs accepted:** Could not adjust mid-task (e.g., warn implementer about deadlock pattern earlier). Pays back as context preservation.

**Confidence:** High (E2).

**Reversibility:** N/A.

**Change trigger:** Future Task 16-class dispatches: continue background mode; add deadlock-aware acceptance criteria (see L2 below).

### D4: Save handoff at 100% context, defer adjudication to fresh session

**Choice:** /handoff:save NOW; do NOT attempt adjudication of options A/B/C in this session.

**Driver:** Context at 199k/200k (100%). Adjudication requires re-reading test_delegation_controller.py to count exact deadlock surface, evaluating option B's `__init__` signature change ripple effects, evaluating option C's mock-injection ergonomics across ~23 callsites. Each evaluation is multi-file; impossible at 100% context.

**Alternatives considered:**
- **Quick adjudication on instinct.** Rejected — high-stakes scope decision; affects ~23 tests + possibly `__init__` signature.
- **Send back to implementer with "pick A".** Rejected — implementer could not deliver feat commit if A is wrong choice; would burn another agent run.

**Implications:** Fresh session loads this handoff, adjudicates A/B/C, sends adjudicated path to `task-16-implementer` via SendMessage continuation. Implementer reuses its context to apply adjudication and land the feat commit.

**Trade-offs accepted:** One additional session boundary in Task 16 lifecycle (now 3 sessions: convergence map → dispatch → adjudication+land). Pays back as adjudication quality.

**Confidence:** High (E3) — context arithmetic is unambiguous.

**Reversibility:** N/A.

**Change trigger:** None.

## Changes

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-dispatch-packet.md` (NEW, 212 lines, untracked)

**Purpose:** Self-contained implementer prompt for Task 16 dispatch. Embedded into `Agent({prompt: ...})` call. Lines 23-196 are the Implementer Prompt section (passed to the agent); lines 198-210 are the controller-only post-implementer review chain (excluded from agent prompt).

**Approach:** Compact (~200 lines) vs convergence map's 264. Points to convergence map as binding authority + inlines high-leverage items (L4 fix, L9 disposition, acceptance grep invariants, reporting contract).

**Key implementation details:**
- Pre-read BLOCKED guard at lines 30-31 (added by user adjudication of untracked-file caveat)
- L4 fix in section "CRITICAL: L4 FIX" with full pseudocode delta (`kind=cast(EscalatableRequestKind, parsed.kind)` addition)
- L9 stop-rule with verbatim skip-reason citation
- Test harness section uses `create_autospec(ResolutionRegistry, instance=True)` (user refinement — autospec enforces L4 signature)
- 3 grep invariants in code acceptance: W7=6, L6=8 (precise, `self\._job_store\.update_parked_request` not loose), L7=4
- Reporting contract format: DONE / BLOCKED templates

**Future-Claude:** Dispatch packet is reusable for future Task 16-class dispatches. Pattern: pointer-to-convergence-map + inline critical-traps + grep invariants + reporting contract.

### `packages/plugins/codex-collaboration/server/delegation_controller.py` (MODIFIED, uncommitted)

**Purpose:** Implementer's handler rewrite per Task 16 plan + L4 fix. Production code per the implementer's BLOCKED report has all invariants satisfied:
- W7: 6 sentinel raise sites
- L6: 8 production `update_parked_request` callsites
- L7: 4 `completion_origin="worker_completed"` writes
- L4 fix at line 885 (`cast(EscalatableRequestKind, parsed.kind)`)

**Approach:** Per plan Step 16.3 + L4 fix. Includes 3 new helpers (`_handle_timeout_wake`, `_write_completion_and_audit_timeout`, `_repo_root_for_journal`), `self._registry: ResolutionRegistry = ResolutionRegistry()` in `__init__`, `_APPROVAL_OPERATOR_WINDOW_SECONDS = 900` module constant.

**Key implementation details (NEEDS VERIFICATION in fresh session):**
- 6 raise sites have caller-contract comments (closes A2 per L8)
- 8 update_parked_request callsites: 1 SET at capture + 7 CLEAR at terminal branches
- All 4 cleanup helpers (`_mark_execution_unknown_and_cleanup` + inline cancel sequence) wired correctly
- `_finalize_turn` body NOT modified (W1)

**Future-Claude:** Diff is uncommitted in working tree. Run `git diff packages/plugins/codex-collaboration/server/delegation_controller.py | head -200` to inspect. Pyright reports 3 errors + 2 warnings on this file (see Diagnostics below).

### `packages/plugins/codex-collaboration/tests/test_handler_branches_integration.py` (NEW, uncommitted)

**Purpose:** Integration test file per Task 16 plan Step 16.1. Implementer claims 11 pass + 3 skip (2 Task 19 finalizer-routed + 1 Task 17 L10 barrier — slightly different count than convergence map's 7+2; needs verification).

**Approach:** Module-local `_build_controller(tmp_path)` + `create_autospec(ResolutionRegistry, instance=True)` per dispatch packet recommended pattern. Mock injection bypasses real registry coordination.

**Key implementation details (NEEDS VERIFICATION):**
- Test count: implementer says 11 pass + 3 skip (≠ convergence map's 7 written + 2 skipped — extra 1 skip is "Task 17 L10 barrier" per implementer's report; may be the unknown-kind interrupt-success test)
- 4 `_FakeSession.respond` attribute issues from Pyright (test attaches at runtime; pyright doesn't see)
- Several unused-variable warnings (style; deferrable)

**Future-Claude:** New file uncommitted. Inspect via `git status` + `Read` on the file.

## Codebase Knowledge

### Pyright diagnostics (5 ✘ + 7 ★) on implementer's working tree

| Severity | File:line | Issue |
|----------|-----------|-------|
| ✘ | `delegation_controller.py:834` | `entry: ExecutionRuntimeEntry \| None` not narrowed before passing to `_mark_execution_unknown_and_cleanup(entry: ExecutionRuntimeEntry)`. **Fix:** narrow with `if interrupt_entry is not None:` guard OR change cleanup helper signature to accept `\| None`. |
| ✘ | `delegation_controller.py:1030` | `_FakeSession.respond` attribute unknown. **Likely cause:** the `entry.session.respond(...)` call in `_handle_timeout_wake` cancel-capable branch — `AppServerRuntimeSession` protocol doesn't declare `respond`. Need to add to protocol or cast. |
| ✘ | `delegation_controller.py:1349` | Same as :1030 — second `respond` callsite (likely the operator-decide branch). |
| ★ | `delegation_controller.py:1514` | `dispatch_result` parameter unused. |
| ★ | `delegation_controller.py:1515` | `dispatch_error` parameter unused. |
| ✘ | `test_handler_branches_integration.py:27` | `pytest` import not resolved. **Pyright config issue, not real** (per Task 15 G18 precedent). |
| ✘ | `test_handler_branches_integration.py:227, 434, 718, 758` | `_FakeSession.respond` attribute unknown. **Cause:** test attaches `mock_session.respond = MagicMock(...)` at runtime; Pyright doesn't see runtime attachment. **Fix:** declare `respond` on `_FakeSession` class OR use `setattr(mock_session, "respond", ...)` to bypass attribute check. |
| ★ | `test_handler_branches_integration.py:73` | `_file_change_request` not accessed (likely unused fixture/helper). |
| ★ | `test_handler_branches_integration.py:170, 187` | `tmp_path` not accessed in two tests (signature param, helper not called). |
| ★ | `test_handler_branches_integration.py:215, 216` | `_cp`, `_wm` not accessed (8-tuple unpack convention). |

The 5 ✘ errors must be addressed in the closeout-fix commit (or the feat commit if it can be pre-amended). The 7 ★ are cleanups (deferrable per per-task discipline).

### Architecture: Phase F worker-thread model post-implementer-changes

| Component | File | Status post-implementer (uncommitted) | Status post-Task-16-feat-commit (target) |
|---|---|---|---|
| `_WorkerTerminalBranchSignal` (sentinel exception) | `delegation_controller.py:201-223` | Defined | Defined |
| `_WorkerRunner` class | `worker_runner.py` | NEW (Task 15) | Unchanged |
| Sentinel catch in `_execute_live_turn` | `delegation_controller.py:845` | Task 15 | Unchanged |
| 6 sentinel raise sites in handler body | `delegation_controller.py` | **NEW (claimed by implementer)** | NEW |
| `self._registry: ResolutionRegistry` | `__init__` | **NEW (claimed)** | NEW |
| `_APPROVAL_OPERATOR_WINDOW_SECONDS` constant | module-level | **NEW (claimed)** | NEW |
| `update_parked_request(...)` callsites | various branches | **8 callsites (claimed)** | 8 |
| `completion_origin="worker_completed"` writes | various | **4 (claimed)** | 4 |
| 3 new helpers | `delegation_controller.py` | **NEW (claimed)** | NEW |
| `start()` spawns worker | `delegation_controller.py:start` | Pending | Pending — Task 17 |
| `wait_for_parked` blocking call from main thread in `start()` | `delegation_controller.py:start` | Pending | Pending — Task 17 |

### Critical scope gap discovered: ~23 existing tests deadlock

`_server_request_handler` now calls `registry.wait(parsed.request_id)` for any parkable request (`command_approval`, `file_change`, `request_user_input`). Pre-Task-17, `start()` is synchronous — no worker thread, no `wait_for_parked()` on the main side. With no main-thread waiter, `announce_parked` drops silently and `registry.wait()` blocks until the 900-second timer fires.

~23 currently-passing tests call `controller.start()` with parkable server requests. Confirmed deadlock: `test_start_with_command_approval_returns_escalation` at `test_delegation_controller.py:1320` hangs >10s with no output.

The convergence map W6 acknowledged this for Mode B (2 tests) but did NOT propagate the implication to the broader baseline of currently-passing tests. The `983 + N passing` target was wrong by ~23.

### Files explored this session (no need to re-read)

| File | Purpose | Key findings |
|------|---------|--------------|
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md` | Binding dispatch authority | 11 locks + 13 watchpoints + 8-row branch matrix; row 2 fixed mid-session |
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md:377-1189` | Task 16 plan body | Steps 16.1-16.7; pseudocode for handler + helpers |
| `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md:450-558` | Spec sentinel section | 6 reasons + invariant table |
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` | Packet 1 ledger | 17 open items; A3 still flagged Open (audit pending) |
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md` | Template structure (Task 15) | 8 locks + 11 watchpoints; section structure mirrored for Task 16 |
| `packages/plugins/codex-collaboration/tests/test_delegation_controller.py:199` | `_build_controller` helper definition | 8-tuple return; harness pattern locked |

## Context

### Project state

T-20260423-02 Packet 1 progress (post-Task-15 closed, Task 16 BLOCKED uncommitted):

| Phase | Tasks | Status |
|-------|-------|--------|
| A (types) | 1-5 | Complete |
| B (stores) | 6-9 | Complete (with closeout) |
| C (journal) | 10 | Complete (with closeout) |
| D (registry) | 11-12 | Complete (with closeouts) |
| E (serialization/projection) | 13-14 | Complete (with closeouts) |
| **F (worker)** | **15-16** | **15 COMPLETE — Task 16 implementer BLOCKED on 23-test deadlock; uncommitted working tree** |
| G (public API) | 17-18 | Not started |
| H (finalizer/consumers/contracts) | 19+ | Not started |

17 open carry-forward items at session start (unchanged — Task 16 hasn't committed yet). Anticipated 17 → 14 at Task 16 close (A2, C10.4, A3 close; F16.1 added) + potentially 17 → 14+M where M is the count of Task-17-tagged skip carry-forwards added per option (a) adjudication.

### Branch state

Branch: `feature/delegate-deferred-approval-response`. Uncommitted working tree (changes from implementer):
- Modified: `packages/plugins/codex-collaboration/server/delegation_controller.py`
- New: `packages/plugins/codex-collaboration/tests/test_handler_branches_integration.py`
- Untracked (from prior sessions, will commit alongside Task 16 closeout-docs):
  - `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md`
  - `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-dispatch-packet.md`

Last commit: `475d0506` — `docs(delegate): correct stale worker_runner.py line count in Task 15 closeout`

### Mental model

**Phase F = worker-side machinery, two slices:**
- Task 15 (DONE): scaffold — `worker_runner.py` + sentinel catch + canceled-tuple expansion. Purely additive, dead code under own scope.
- Task 16 (BLOCKED): handler rewrite — async-decide model + 6 sentinel raise sites + 3 helpers + registry init + 8 `update_parked_request` callsites + 4 `completion_origin="worker_completed"` writes.

**The 23-test deadlock is the central tension of Task 16 closeout.** Three options on the table:

- **Option A (skip + cite Task 17):** Mark ~23 currently-passing tests with `@pytest.mark.skip(reason="Phase G Task 17: synchronous start() blocks on registry.wait(); parkable-request tests require spawn_worker split")`. Per-test discipline preserved. Final count: `983 - 23 + 11 = 971 passing, 8 + 2 + 1 + 23 = 34 skipped`. Most expedient. Joins Task 14 Mode A/B in Task 17's unblock surface (8 → 31).
- **Option B (timeout injection):** Add `approval_window_seconds: float = _APPROVAL_OPERATOR_WINDOW_SECONDS` parameter to `__init__` and pass to `registry.register`. Tests set 0.001s; timer fires immediately via `is_timeout=True` path. Changes existing test SEMANTICS (assertions move from `status="needs_escalation"` to `status="unknown"` post-timeout). Most invasive — requires updating all 23 tests' assertion bodies, not just decorators.
- **Option C (mock registry inject):** Add `_registry: ResolutionRegistry | None = None` optional parameter to `__init__`. Existing tests pass `mock_registry = MagicMock(spec=ResolutionRegistry)` to bypass blocking. Code-minimal but spreads cutover surface across ~23 test files (or `_build_controller(tmp_path)` updated to inject by default).

**Adjudication considerations:**
- Option A pattern-matches against Task 14 Mode A/B disposition (defer with explicit Task-N citation). Established precedent.
- Option C pattern-matches against `_build_controller` harness pattern (single-helper update; tests don't change individually).
- Option B has the highest semantic-change cost — likely rejected.

### Environment

- Python 3.12, uv workspace, pytest test runner
- Run package suite: `uv run --package codex-collaboration pytest`
- Run lint: `uv run --package codex-collaboration ruff check packages/plugins/codex-collaboration/server/ packages/plugins/codex-collaboration/tests/`
- Branch protection hook: edits allowed on `feature/*`; blocked on `main`/`master`
- Current branch is `feature/delegate-deferred-approval-response` — edits allowed throughout

### Two-read protocol observed (fourth successive instance)

Tasks 13/14/15/16 all benefited from the user's two-read protocol. This session's instance applied to the DISPATCH PACKET (not just the convergence map, as in prior sessions):
- Controller's first draft: included `MagicMock(spec=ResolutionRegistry)` recommendation, loose L6 grep, sparse `DecisionResolution` examples.
- User's `/copy` independent read: surfaced 4 refinements (autospec swap, payload+kind examples, fake-session invocation requirement, L6 precision) + 1 convergence-map fix (row 2 symmetry).

Convergence achieved; user verdict was "credible and ready to use." Pattern: two-read protocol generalizes from convergence map to dispatch packet for high-stakes dispatches.

## Learnings

### L1: BLOCKED + question reporting contract worked exactly as designed — implementer caught a real structural gap

**Mechanism:** The dispatch packet's reporting contract explicitly required BLOCKED + question over DONE_WITH_CONCERNS + unilateral decision. Implementer hit the 23-test deadlock during the suite-validation step, recognized the convergence map's `983 + N` baseline was wrong, structured 3 options with clear trade-offs, and reported BLOCKED. Controller adjudicates from a fresh session with full context budget.

**Evidence:** Implementer's BLOCKED report includes 3 options with concrete trade-offs (count of tests, file scope, semantic-change cost) — exactly the structure needed for adjudication. Production code invariants (W7=6, L6=8, L7=4) all satisfied; the BLOCKED is purely about how to handle the test-suite fallout, not about the production code.

**Implication:** Future dispatch packets for Task 16-class tasks should preserve this contract verbatim. The `BLOCKED + 3 options` pattern is the gold standard — it preserves implementer momentum (production code shipped) while deferring scope decisions to controller.

**Watch for:** Any implementer report that just says "BLOCKED — please advise" without options. That's a process failure (implementer should always propose paths forward); send back asking for the option enumeration.

### L2: Convergence-map blind spot — `983 + N passing` baseline did not account for cross-task deadlock implications

**Mechanism:** The convergence map's W6 watchpoint correctly identified that Mode B tests would deadlock under the new handler ("synchronous `start()` blocks indefinitely on `registry.wait(...)`"), but did NOT extend the analysis to the FULL set of tests calling `start()` with parkable requests. Task 14 Mode A/B classified 8 tests; the actual deadlock surface is ~31 tests (8 Task 14 + ~23 newly-affected).

**Evidence:** Convergence map explicitly says W6 → "Both Mode A and Mode B unblock at Task 17." But the implementer found ~23 OTHER tests (not in the Mode A/B set) that ALSO call `start()` with parkable requests — and these were currently passing (because pre-Task-16 handler did synchronous interrupt+escalate, no `registry.wait`). Task 16's handler rewrite changes them ALL to deadlock.

**Implication:** Future convergence maps for handler-rewrite-scale tasks (those that change a function's blocking behavior) MUST audit the FULL caller surface for tests that exercise the changed function, not just tests already classified as deferred. This generalizes the Task 14 closeout learning ("when adding runtime guards, audit ALL callers in the call graph").

**Watch for:** Any task that introduces a new blocking call (`wait`, `acquire`, `join`, etc.) into a previously-synchronous code path. Convergence map drafting must include a "currently-passing-tests-that-touch-this-path" census before locking the `N + M passing` target.

### L3: `create_autospec` over `MagicMock(spec=...)` is a contract-enforcement primitive

**Mechanism:** `MagicMock(spec=cls)` checks attribute names but NOT function signatures (kw-only arguments, positional-only arguments, default values). `create_autospec(cls, instance=True)` introspects each method's signature and raises `TypeError` if a call violates the signature.

**Evidence:** L4 was specifically a kw-only-argument trap. Plain `spec=` would not have caught the missing `kind=` arg. Autospec turns the signature contract into a runtime test failure.

**Implication:** When a lock is a function-signature contract (kw-only args, required positional args, type-narrowed args), prefer `create_autospec` over `MagicMock(spec=...)`. The mock itself becomes the contract enforcer; test discipline doesn't have to do the work.

**Watch for:** Any lock that says "MUST pass `<kw_arg>=...`" or "MUST narrow `<param>` to type X" — these are signature contracts and benefit from autospec.

### L4: Two-read protocol generalizes from convergence map to dispatch packet

**Mechanism:** Prior sessions applied two-read to convergence maps (controller draft + user `/copy` independent read; refinements R1, R2, R3 merged). This session applied it to the DISPATCH PACKET — controller drafted; user `/copy` independent read surfaced 4 refinements + 1 convergence-map fix.

**Evidence:** All 4 user refinements were structurally valuable: autospec swap (L4 enforcement), payload examples (test realism), fake-session invocation requirement (avoids tautological tests), L6 grep precision (avoids docstring counting). Pattern continues across Task 13/14/15/16.

**Implication:** For Task 16-class dispatches (large + multi-helper + multi-branch), apply two-read to BOTH convergence map AND dispatch packet. The dispatch packet is the implementer's binding source — refinements there have higher leverage than convergence-map polish.

**Watch for:** Future dispatch packets where the controller skips the user-review pass. That's a regression against the two-read protocol's success rate.

## Next Steps

### 1. Adjudicate options A/B/C for the 23-test deadlock

**Dependencies:** This handoff loaded; implementer's BLOCKED report visible (in Open Questions §1 below).

**What to read first** (in order):
1. This handoff (loaded automatically via `/handoff:load`)
2. Implementer's BLOCKED report (Open Questions §1 below — full text preserved)
3. `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md` (binding authority; W6 watchpoint context)
4. `packages/plugins/codex-collaboration/tests/test_delegation_controller.py` (count exact deadlock surface)
5. Optionally: `git diff packages/plugins/codex-collaboration/server/delegation_controller.py` (inspect implementer's working-tree state)

**Approach:** Evaluate options A/B/C against criteria: (a) per-task scope discipline, (b) carry-forward overhead (option A adds ~23 carry-forward items vs option C adds 1), (c) Task 17 unblock-surface concentration (option A makes Task 17 unblock 31 tests in one commit vs option C's wired pattern), (d) test-semantic preservation (option B changes assertions; A/C don't).

**Recommendation lean (NOT binding):** Option A (skip + Task 17 cite) for per-task discipline match with Task 14 Mode A/B precedent. Option C (mock registry inject) is a credible second if the user prefers minimizing carry-forward overhead — `_build_controller(tmp_path)` could be updated once to inject a `MagicMock(spec=ResolutionRegistry)` by default, and individual tests inherit the bypass without touching their bodies.

**Acceptance criteria:** Adjudication recorded as a new D-decision in this handoff's chain, sent to `task-16-implementer` via SendMessage, implementer applies the path and lands the feat commit.

### 2. Resolve Pyright diagnostics in the closeout-fix commit (or pre-amend feat)

**Dependencies:** Task 1 adjudication; implementer continued via SendMessage.

**Scope:** 5 ✘ Pyright errors:
- `delegation_controller.py:834` — narrow `entry: ExecutionRuntimeEntry | None` before passing to cleanup helper
- `delegation_controller.py:1030, :1349` — `_FakeSession.respond` not declared on protocol; add or cast
- `test_handler_branches_integration.py:227, :434, :718, :758` — declare `respond` on `_FakeSession` or use `setattr` to bypass

**Approach:** Send to `task-16-implementer` via SendMessage with the diagnostic list. Implementer addresses in either the feat commit (if not yet landed) or a closeout-fix commit per Task 13/14/15 cadence.

### 3. Spec compliance + code quality review (sequential, after feat commit lands)

**Dependencies:** Feat commit landed.

**Approach:** Per dispatch packet's controller-only review chain section. Spec reviewer verifies L1-L11 + W1-W13 conformance against feat commit. Code-quality reviewer reviews the 3 new helpers + 6 raise-site comments + test harness. Findings consolidated and sent to implementer via SendMessage.

### 4. Closeout-docs commit

**Dependencies:** Feat + closeout-fix commits landed.

**Scope:** A2 + C10.4 + A3 carry-forward state moves; F16.1 added; Phase F closeout entry.

**Acceptance:** Per dispatch packet's closeout-docs acceptance summary. L11 audit (grep + verify) BEFORE moving A3.

### 5. (Subsequent) Phase G Task 17 dispatch

**Dependencies:** Task 16 complete + closeouts.

**Scope:** Worker spawn from `start()`, `wait_for_parked` blocking call from main thread. **Now unblocks ~31 tests at once** (8 Task 14 Mode A/B + ~23 new Task 16 deferrals per option A) instead of just 8. Task 17 convergence map MUST search carry-forward.md for ALL skip-decorator citations referencing Task 17, not just the original 8.

## In Progress

**Implementer agent `task-16-implementer` is in BLOCKED state.** Working tree has uncommitted changes from the implementer's execution; agent is paused waiting for SendMessage with adjudication. Agent ID: `a59d25972ffe55f77`. Continuation pattern: `SendMessage({to: "task-16-implementer", message: <adjudication + Pyright fixes>})`.

The fresh session loads this handoff, adjudicates A/B/C, sends the adjudicated path + Pyright fix instructions to the implementer via SendMessage, and waits for the resumed-agent's DONE report (or BLOCKED if a sub-question arises).

## Open Questions

### 1. Implementer's BLOCKED report (verbatim, preserved for adjudication)

```
BLOCKED
- Lock that cannot be honored: Test acceptance criterion "`983 + N` passing" from convergence map §Acceptance criteria → Tests
- Live observation: `_server_request_handler` now calls `registry.wait(parsed.request_id)` for any parkable request (`command_approval`, `file_change`, `request_user_input`). Pre-Task-17, `start()` is synchronous — no worker thread, no `wait_for_parked()` on the main side. With no main-thread waiter, `announce_parked` drops silently and `registry.wait()` blocks until the 900-second timer fires. ~23 existing passing tests call `controller.start()` with parkable server requests (e.g. `test_start_with_command_approval_returns_escalation` at test_delegation_controller.py:1320). All hang. Confirmed: that test takes >10s with no output, then times out. The convergence map §W6 notes "synchronous `start()` blocks indefinitely" but doesn't reduce the `983 + N` baseline.

All production code invariants are satisfied:
- W7: `grep -nF "_WorkerTerminalBranchSignal(reason=" ... | wc -l` = 6
- L6: `grep -n "self._job_store.update_parked_request" ... | wc -l` = 8
- L7: `grep -nF 'completion_origin="worker_completed"' ... | wc -l` = 4
- L4 fix: `cast(EscalatableRequestKind, parsed.kind)` at line 885
- New tests: 11 pass + 3 skip (2 Task 19 + 1 Task 17 L10 barrier)

- Question for controller (pick one):
  A. Skip the ~23 blocking tests at Task 16 with "Phase G Task 17: synchronous start() blocks on registry.wait(); parkable-request tests require spawn_worker split" citations — final count: `983 - 23 + 11 = 971` passing, `8 + 2 + 1 + 23 = 34` skipped
  B. Add `approval_window_seconds: float = _APPROVAL_OPERATOR_WINDOW_SECONDS` parameter to `DelegationController.__init__` (and pass it to `registry.register`), so tests can set 0.001s and the timer fires immediately via the `DecisionResolution(is_timeout=True)` path — this changes existing test semantics (they'd assert `status="unknown"` instead of `status="needs_escalation"` which requires additional test updates)
  C. Add a `_registry: ResolutionRegistry | None` optional inject parameter to `DelegationController.__init__` so existing tests can inject a pre-configured mock that never blocks — the most minimal fix: existing tests pass `mock_registry = MagicMock(spec=ResolutionRegistry)` to bypass the blocking, and the existing test assertions stay valid
```

### 2. Test count discrepancy — implementer says "11 pass + 3 skip" vs convergence map's "7 written + 2 skipped"

The convergence map per-test triage specified 9 plan integration tests (7 to write + 2 to skip with Task 19 citations) + 5 helper unit tests. Implementer reports 11 pass + 3 skip — math: 11 + 3 = 14 total. Where do the extra 5 tests come from? Likely the helper unit tests folded into `test_handler_branches_integration.py` rather than a separate file. The "1 Task 17 L10 barrier" skip is novel — likely the unknown-kind interrupt-success test (row 9 in branch matrix, L10) which the implementer judged required Task 17 finalization. Needs verification when fresh session inspects the file.

### 3. Should the dispatch packet's `983 + N passing` invariant be retroactively corrected?

After adjudication, the convergence map's Tests acceptance section becomes wrong. Should:
- (a) Update convergence map in the closeout-docs commit alongside Task 16's other doc changes
- (b) Leave convergence map as-is (it's a session artifact; the corrected baseline lives in carry-forward)
- (c) Add a "Convergence-map errata" note to carry-forward

Recommendation lean: (a) — convergence map is the binding authority; should be self-consistent with the actual landed scope.

## Risks

### R1: Implementer continuation may have lost context after 47-minute run

**Concern:** Agent ran 2,833 seconds + 167 tool uses. Even sonnet has context limits. By the time we send adjudication via SendMessage, implementer may not remember details from the early plan-reading phase.

**Mitigation:** Send adjudication with FULL context: state of working tree, the option chosen, the rationale, the specific test files to modify, the Pyright fixes. Don't assume implementer remembers anything from the convergence-map / spec / plan reads.

**Severity:** Medium — implementer needs to resume coherently; over-explaining is cheap insurance.

### R2: Working-tree state may have unintended changes

**Concern:** Implementer modified `delegation_controller.py` and created the test file. Could there be additional unintended changes (e.g., touched `_finalize_turn` against W1)? Implementer's BLOCKED report says invariants pass but doesn't enumerate ALL changed lines.

**Mitigation:** Fresh session runs `git diff --stat` first to see scope of changes, then `git diff packages/plugins/codex-collaboration/server/delegation_controller.py | head -300` to spot-check no W1/W10 violations.

**Severity:** Low — implementer is faithful by design; spot-check is cheap.

### R3: Adjudication of option B/C could expand into a multi-task refactor

**Concern:** Option B changes `__init__` signature; option C does too. Either could ripple into MCP server `decide_handler` instantiation, plus all test fixtures. Could grow Task 16 scope significantly.

**Mitigation:** Option A is the scope-discipline-preserving choice. If user picks B/C, fresh session must enumerate the full ripple before sending to implementer.

**Severity:** Medium — depends on adjudication.

### R4: Pyright `_FakeSession.respond` issues may indicate a deeper protocol gap

**Concern:** 4 test-file Pyright errors + 2 production-file Pyright errors all relate to `respond`. May indicate `AppServerRuntimeSession` protocol needs a `respond` method declared, OR the test's runtime attachment pattern is incompatible with the protocol's strict typing.

**Mitigation:** Inspect `AppServerRuntimeSession` definition during fresh-session adjudication. Likely fix is one-line protocol amendment.

**Severity:** Low — typing fix; not behavioral.

### R5: Context overrun risk during adjudication

**Concern:** Fresh session needs to: load this handoff (300+ lines), inspect implementer's working tree (`delegation_controller.py` partial diff is 280+ lines), evaluate ~23 deadlocked tests (need to grep test files), make adjudication decision. That's a meaningful context budget.

**Mitigation:** Be ruthless about not re-reading what's in this handoff. Use `wc -l` first; pull exact line ranges only.

**Severity:** Medium — mitigatable with discipline.

## References

- **Branch:** `feature/delegate-deferred-approval-response` @ `475d0506` (UNCOMMITTED working tree from implementer's run)
- **Implementer agent ID:** `a59d25972ffe55f77` (continuation: `SendMessage({to: "task-16-implementer", ...})`)
- **Implementer transcript (DO NOT READ — context overflow):** `/private/tmp/claude-501/-Users-jp-Projects-active-claude-code-tool-dev/4f249288-dfea-4d18-bda2-80c2334fb7ff/tasks/a59d25972ffe55f77.output`
- **Untracked files (will commit alongside Task 16 closeout-docs):**
  - `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md` (264 lines)
  - `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-dispatch-packet.md` (212 lines)
- **Prior session handoff (resumed_from):** `docs/handoffs/archive/2026-04-25_16-43_phase-f-task-16-convergence-map-drafted.md`
- **Phase F plan:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md` (1189 lines; Task 16 body lines 377-1189)
- **Phase G plan:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md`
- **Phase H plan (Task 19 owner):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-h-finalizer-consumers-contracts.md`
- **Manifest:** `docs/plans/2026-04-24-packet-1-deferred-approval-response.md`
- **Carry-forward tracker:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md`
- **Spec sentinel section:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md:450-558`
- **Recent commits (pre-Task-16):**
  - `94c4dab7` — feat: _WorkerRunner + sentinel catch scaffold
  - `6f23b745` — fix: address Task 15 code-quality review
  - `13b024ae` — docs: record Phase F Task 15 closeout
  - `475d0506` — docs: correct stale worker_runner.py line count

## Conversation Highlights

**Initial dispatch directive (binding):**
User: "Yes, start by re-reading `task-16-convergence-map.md` and the Phase F plan body for Task 16, then assemble the implementer prompt"

**User two-read review of dispatch packet (verbatim verdict):**
User: "I refined the packet and the one affected binding map row. After those edits, I'd call the dispatch packet credible and ready to use, assuming the implementer agent can read the untracked files in this same worktree."

**User Path A adjudication (verbatim):**
User: "I recommend **Path A: dispatch in-place, no pre-commit, no full inlining**. The belt-and-suspenders concern is real, but the failure mode is narrow here: you are not using worktree isolation, and the implementer needs to edit this same worktree. A pre-commit would buy reproducibility from a clean checkout, but it would also make the dispatch packet look like a durable task artifact before execution has tested whether it was fully sufficient. That weakens the Task 15 D4 precedent and muddies the clean `feat + fix + docs closeout` chain."

**User boundary-preservation directive (verbatim):**
User: "make sure the actual prompt passed is only the **Implementer Prompt** section, not the controller-only post-implementer review-chain section. That preserves the intended boundary: implementer lands the feat commit and reports; controller owns spec review, code-quality review, fix dispatch, and closeout-docs."

**Implementer BLOCKED report (key passages — full text in Open Questions §1):**
Implementer: "It's hanging after starting the test. Confirmed hang."
Implementer: "All production code invariants are satisfied: W7=6, L6=8, L7=4, L4 fix at line 885."
Implementer: "Question for controller (pick one): A/B/C..."

**Working style observed:** User produces tight, evidence-first refinements with explicit corrections (autospec swap example shows mechanic-aware test-double selection). Treats user `/copy` independent reads as VALIDATED EVIDENCE with same authority as controller analysis. Pre-empts structural risks (untracked-file caveat) before they manifest. Adjudicates with reasoning AND scope-discipline framing ("weakens the Task 15 D4 precedent and muddies the clean chain"). Defers complex adjudications to fresh session under context pressure.

## User Preferences

(All carry-over items from Tasks 13/14/15/16 still apply; reaffirmed this session.)

**Workflow:** `superpowers:subagent-driven-development` — controller does not implement; review subagents critique. Single fresh implementer + spec reviewer + code-quality reviewer per task, sequential not parallel. **Implementer continued via SendMessage for closeout-fix** (NOT spawned fresh) — preserves implementer's accumulated context.

**Two-read protocol generalized to dispatch packets (NEW this session):** For Task 16-class dispatches, two-read applies to BOTH convergence map AND dispatch packet. User's `/copy` independent reads are VALIDATED EVIDENCE.

**Test-double selection by mechanic match (NEW this session):** When a lock is a function-signature contract, prefer `create_autospec(cls, instance=True)` over `MagicMock(spec=cls)`. The mock becomes the contract enforcer.

**BLOCKED + question over DONE_WITH_CONCERNS (carried, reinforced):** Implementer's BLOCKED report this session demonstrates the value — controller adjudicates with full options; implementer doesn't make scope decisions unilaterally.

**Background dispatch for large tasks (NEW this session):** Task 16-class dispatches go via `run_in_background: true`. Foreground would consume controller context for ~47 minutes of intermediate work.

**Pre-read BLOCKED guard pattern (NEW this session):** Dispatch packets include "if file X is missing, BLOCKED" as the first authority-source instruction. Converts file-readability from soft assumption into fail-fast contract.

**Convergence map row-symmetry discipline (NEW this session):** Branch matrix rows must use parallel column structure. Asymmetric rows (row 1 has parenthetical, row 2 doesn't) get fixed.

**Context discipline (carried, reaffirmed):** At 100% context, save handoff immediately. Do NOT attempt complex adjudication under context pressure — fresh session restores full reasoning capacity.

**Per-task scope discipline (carried, reaffirmed):** Option A (skip + Task 17 cite) is the scope-discipline-preserving choice for the 23-test deadlock. Pull-forward (option B/C with `__init__` changes) is rejected by user precedent unless explicitly approved.

**Acceptance criteria style (carried):** Structural location, NOT post-edit line numbers. Split: Code + Tests + Closeout-docs.

**Commit discipline (carried):** New commits, never amend. Stage specific files only.

**Per-test triage style (carried):** No blanket migrations. Every old test gets per-case judgment. Triage table in dispatch packets is binding.

**Skip-reason rubric (carried):** Each `@pytest.mark.skip(reason=...)` must (a) cite specific Phase/Task as unblock owner, (b) explain structural mechanic, (c) point to real sibling for partial coverage OR honestly explain why no real sibling exists.

**Evidence density (carried):** File:line citations expected throughout; tables preferred over prose.

## Gotchas

(Carry-over from prior sessions: G1-G24 still apply. New this session: G25-G31.)

### G1-G24 (carry-forward from prior handoffs)

Apply identically. See `docs/handoffs/archive/2026-04-25_16-43_phase-f-task-16-convergence-map-drafted.md` and predecessors for full text. Highlights still binding:
- G9: `_WorkerTerminalBranchSignal` empty-args mechanic (use `signal.reason`, not `str(signal)`)
- G11: Plan-line numbers throughout `phase-f-worker.md` are stale
- G19: `kind=` argument trap in plan pseudocode (Task 16 specific) — addressed by L4 fix
- G24: `_finalize_turn`'s local `_CANCEL_CAPABLE_KINDS` at `:1628` is separate from handler's at `:757`

### G25: Pre-Task-17 `start()` is synchronous — `_server_request_handler` calling `registry.wait()` deadlocks ~23 tests

The convergence map's W6 watchpoint identified this for Mode B (2 tests). The actual deadlock surface is ~23 currently-passing tests + the 8 Task 14 Mode A/B already classified = ~31 tests total. Discovered by Task 16 implementer during full-suite validation. Confirmed at `test_delegation_controller.py:1320` (>10s hang).

### G26: Working tree has implementer's uncommitted changes — DO NOT discard

The Task 16 implementer wrote production code + new test file but did NOT commit (BLOCKED before commit). Fresh session must NOT run `git stash` or `git checkout .` — that destroys 47 minutes of implementer work. Inspect via `git status` + `git diff` only.

### G27: `_FakeSession` does not declare `respond` method

Pyright errors at `delegation_controller.py:1030, :1349` and `test_handler_branches_integration.py:227, :434, :718, :758` all relate to this. Fix options: (a) add `respond` to `AppServerRuntimeSession` protocol, (b) cast at usage sites, (c) `setattr(mock_session, "respond", ...)` to bypass attribute check in tests.

### G28: Background-mode agent transcript is JSONL — DO NOT read via Bash

Transcript path: `/private/tmp/claude-501/-Users-jp-Projects-active-claude-code-tool-dev/4f249288-dfea-4d18-bda2-80c2334fb7ff/tasks/a59d25972ffe55f77.output`. Reading it via `cat`/`Read` will overflow context. Use TaskOutput tool if you need partial output (but the BLOCKED report is preserved in this handoff's Open Questions §1 — TaskOutput should not be needed).

### G29: Implementer continuation pattern — SendMessage to agent NAME, not ID

Per Task 15 D5/R3 precedent: agents are addressable by `name` field for SendMessage. Use `SendMessage({to: "task-16-implementer", ...})` not the internal agent ID `a59d25972ffe55f77`.

### G30: Test count discrepancy needs verification

Implementer reports "11 pass + 3 skip" but convergence map specified "7 written + 2 skipped" + "5 helper unit tests" (9 + 5 = 14 tests). The math works (11 + 3 = 14) but the helper unit tests appear folded into the integration test file rather than a separate file. Fresh session should verify this is acceptable (probably yes — convergence map allowed "may collapse").

### G31: The "Task 17 L10 barrier" novel skip needs spec verification

Implementer reports a 3rd skip beyond the convergence map's 2 finalizer-routed skips, citing "Task 17 L10 barrier." Likely the unknown-kind interrupt-success test (row 9 in branch matrix) which spec L10 says is testable at Task 16 via the existing D4 carve-out at `_finalize_turn:1645`. If implementer judged it requires Task 17 work, that may be a third L9-class disagreement that needs adjudication. Verify by reading the implementer's actual skip decorator + reason.
