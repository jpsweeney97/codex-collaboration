---
date: 2026-04-26
time: "18:30"
created_at: "2026-04-26T22:30:00Z"
session_id: 71645c2a-2bb0-43db-93e7-ce6bc4541a0c
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-26_15-45_task-18-opus-implementer-in-flight-after-sonnet-budget-failure.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: 844e6f97
title: "Phase G CLOSES: Task 18 1+1+1 chain landed; Round-7 supersession; W16 narrow adjudication"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/resolution_registry.py
  - packages/plugins/codex-collaboration/tests/test_delegate_decide_async_integration.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-convergence-map.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-dispatch-packet.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md
---

# Phase G CLOSES: Task 18 1+1+1 chain landed; Round-7 supersession; W16 narrow adjudication

## Goal

**Bigger picture:** Phase G of T-20260423-02 Packet 1 (Deferred-Approval Response) is the public-API rewrite phase. Task 17 rewrote `start()` for capture-ready handshake. Task 18 — the SECOND and FINAL task of Phase G — rewrote `DelegationController.decide()` post-validation block at `delegation_controller.py:2560-2675` for the `reserve()` + journal-intent + `commit_signal()` two-phase reservation protocol per spec §Transactional registry protocol. This session closed Task 18 with the full 1+1+1 commit chain (feat + fix + docs) and CLOSES Phase G entirely.

**Stakes:** Phase G CLOSES on Task 18 land. Phase H Task 19 (`_finalize_turn` Captured-Request Terminal Guard) inherits the carry-forward set: F16.1 (2 unchanged) + RT.1 (typing polish) + TT.1 (newly promoted) + G18.1 (newly introduced; 6 finalizer-dependent tests) + F16.2 (lineage marker only; closes via G18.1). The session was structurally complex — 4 implementer dispatches across 2 models with 3 distinct termination modes, 4 user adjudications (recovery option A; Adjudication D for Mode A re-escalation; Path 4 contract-focused fix; Path A direct closeout-docs with Round-6 supersession preservation), 7 convergence map review rounds total (Rounds 5/6/7 added this session).

**Trigger:** User loaded prior handoff (`task-18-dispatch-packet-ready-after-round-5-correction.md`) at session start, then invoked `/superpowers:subagent-driven-development "Dispatch the Task 18 implementer"`. The dispatch fail-and-recover cycle exposed three runtime traps (context exhaustion, transient API faults, pytest hang/output-buffering) that became part of the session's process precedent.

**Project arc context:** T-20260423-02 Packet 1 Phase H Task 19 is queued behind Phase G's close. Phase H's convergence map authoring + dispatch packet construction begins in a fresh session. Task 19 inherits G18.1's pre-authorization spec verbatim (6-test list, renames at `:1881/:1927`, body rewrite for `:1525`, L12 assertion review for 3 others, constant deletion).

## Session Narrative

**Step 1 — Load prior handoff (HEAD `c5829049`):** Loaded `task-18-dispatch-packet-ready-after-round-5-correction.md` with both convergence map (566 lines, post-Round-5) and dispatch packet (468 lines) untracked and dispatch-ready. Carry-forward state: G17.1 (9 F16.2 Bucket B), RT.1 proposed, TT.1 proposed.

**Step 2 — User invoked `/superpowers:subagent-driven-development`:** Created 5 TaskCreate entries for the workflow (implementer + spec review + code-quality review + closeout-fix + closeout-docs), dispatched Sonnet implementer with full Implementer Prompt (~40K tokens) inlined.

**Step 3 — Sonnet "Prompt is too long" failure (97 tool uses, ~15 min):** Agent terminated with context exhaustion. Made partial unstaged edits to `delegation_controller.py` (222-line diff, 94 net deletions; controller rewrite mostly correct per invariants) and `test_delegation_controller.py` (157-line diff, 98 net deletions). NEVER created the new test file. NEVER modified `test_delegate_start_integration.py`. NEVER committed. Diagnosis: prompt + 7 authority-source pre-reads consumed ~95K tokens; per-tool-call results accumulated to ~700K-1.5M total tokens, well beyond Sonnet's 200K window.

**Step 4 — User adjudication: Option A (reset + Opus + TDD preamble):** User explicit verbatim: *"Honestly, using opus (1M context) for subagents is usually the best when we are working on complex projects such as this."* Reset working tree via `git restore` on the 2 modified files; verified clean state via invariant baseline (W17=2, W3=6, L6=4 pre-Task-18 callsites baseline, 10 old-constant references). Both untracked dispatch artifacts preserved.

**Step 5 — Opus retry (`task-18-implementer-opus`) — ConnectionRefused at 46 tool uses (~9.6 min):** Different failure mode from Sonnet — transient runtime fault, NOT context exhaustion. Agent created `test_delegate_decide_async_integration.py` at 674 lines (the 10 acceptance tests per L9, with the L9 test #3 wrapper-on-`update_status_and_promotion` mechanism). Controller untouched (TDD ordering honored per the new preamble). Runtime returned agentId `a5a54a1ea12f3c026` with explicit hint: "use SendMessage with to: 'a5a54a1ea12f3c026' to continue this agent."

**Step 6 — SendMessage by name FAILED, by agent ID succeeded:** Tried `to: "task-18-implementer-opus"` — runtime: "No agent named '...' is currently addressable." Switched to `to: "a5a54a1ea12f3c026"` — succeeded with: "Agent had no active task; resumed from transcript in the background." Discovered: idle-but-resumable agents lose name addressability but remain reachable via agentId. Active agents are name-addressable; transient-fault agents are ID-only.

**Step 7 — Continuation message included diagnostic signals:** `:204:28` JobStatus typing trap, `:510:32` `_worker_thread` attribute access doesn't resolve, several unused imports/vars. Agent processed these in background.

**Step 8 — Watchdog stall (Opus round 2 — 600s of no progress):** Agent fell into pytest-hang trap. The convergence map's L9 test #3 explicitly warns: getting the wrapper-on-`update_status_and_promotion` wrong produces tests that hang on teardown OR pass coincidentally. My preamble's Step 3 instructed "run failing-test verification" via `pytest packages/plugins/codex-collaboration/tests/test_delegate_decide_async_integration.py -v`. Against the un-rewritten controller, no `commit_signal` ever fires to release the worker thread → L9 test #3 deadlocks → pytest hangs. Compounded by: agent backgrounded pytest with `| tail -3` (which buffers stdin entirely until pytest finishes), then fell back to `until` loop checking output file size (recommended by parent harness's `sleep 30 && tail` block). 600s elapsed; watchdog killed.

**Step 9 — Mid-session save (`2026-04-26_15-45_task-18-opus-implementer-in-flight-after-sonnet-budget-failure.md`):** Saved with substantial state recap. Then surfaced 3 recovery paths to user.

**Step 10 — User adjudication: corrected continuation dispatch (NOT replay) with hard guardrails:** User authored the narrowed execution-order block: "Pre-rewrite verification is collect-only only" + "All pytest commands must be synchronous and timeout-wrapped" + "Preserve the 662-line test file" (the agent had cleaned it down 12 lines from 674). User explicitly: *"I would also not take over manually unless the next dispatch fails for a new non-instruction reason. The latest failure is explainable and preventable."*

**Step 11 — 4th dispatch (`task-18-implementer-opus-3`) — BLOCKED at 91 tool uses (~13 min):** Agent reached the implementer's BLOCKED protocol cleanly. Discovered Python's `for x in self._server_requests:` binds the iterator to the list object at iteration start; the 3 Mode A tests' pattern of reassigning `_server_requests = [next_req]` after the worker is parked is invisible to the active iterator. Concrete failures: `assert poll.job.status == "needs_escalation"` got `'running'`; `'NoneType' object is not subscriptable` (`pending_escalation` is None); captured warning `late capture-ready signal ignored. kind=TurnCompletedWithoutCapture`. Agent proposed 3 dispositions (A: reclassify to G18.1; B: global FakeSession `for`→`while pop(0)` change; C: broader scope expansion) and recommended A.

**Step 12 — User adjudication: Adjudication D (NEW; not in agent's options):** User authored: "Patch only the three re-escalation tests — mutate active list (`_server_requests.append`) instead of replace; use bounded polling for `poll().pending_escalation`. FakeSession class UNCHANGED. Mode A row stays as Task-18-closing." Reasoning: the captured warning `TurnCompletedWithoutCapture` proved the failure was *test-double simulation mismatch*, not finalizer dependency. Reclassifying to G18.1 (which is finalizer-guard territory) would be semantically wrong. Mandate: convergence map Round-6 addendum to record the discovery + L12 was substantively right but operationally incomplete.

**Step 13 — SendMessage continuation with Adjudication D:** Agent applied the 3 patches (mutate-not-replace + bounded polling), added Round-6 addendum at convergence map `:568`, then attempted full-suite verification. Backgrounded pytest with `| tail -3` (instructional pattern that's the same anti-pattern). The runtime marked the agent "completed" at 35 minutes (last visible: "Empty output? Strange. Let me re-run more carefully."). Agent transcripts showed it was waiting on Monitor + until loop on `[ -s file ]` while pytest hung.

**Step 14 — Controller takes mechanical verification:** With my own context now expanded to 1M, ran targeted tests synchronously: `timeout 60 uv run --package codex-collaboration pytest <3 specific tests> -v` → all 3 pass in 0.37s. Full suite: `timeout 180 uv run --package codex-collaboration pytest packages/plugins/codex-collaboration/tests/` → 1017 passed, 8 skipped, 0 failed in 124s. Verified Adjudication D's patches work end-to-end.

**Step 15 — User chose: dispatch focused commit agent:** Agent `task-18-feat-commit` with tightly-scoped responsibilities (no pytest debugging; only stage + commit + grep audits). Used file-redirect pattern (`pytest > /tmp/log 2>&1; tail -10 /tmp/log`) to avoid pipe buffering. ~5-10 tool uses target.

**Step 16 — Feat commit landed: `2606fb03` (11 tool uses, ~5.5 min):** Suite (W5 forward order): 124p/6s in 105.68s; reverse order: 124p/6s in 105.51s (3-file scope). All grep audits pass. **L4 Path A artifact discovery:** agent identified pinned-version Codex App Server v0.117.0 fixture at `packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/ToolRequestUserInputResponse.json` with parameterized regression in `test_build_response_payload_per_kind_decision` — Path A option 3 (pinned-version integration ground-truth check). Branch 5 commits ahead of main.

**Step 17 — Spec-compliance review (`task-18-spec-reviewer`, Opus):** APPROVED — NO FIX COMMIT NEEDED. All 14 locks PASS, all 18 watchpoints PASS, Round-6 adjudication D applied. 3 Minor findings (M1: incidental unused-import removal of `build_execution_resume_turn_text`; M2: Step 2/3/4/5 comment labels with no Step 1 anchor; M3: `_build_response_payload` parameter type `decision: DecisionAction | str` wider than necessary).

**Step 18 — User adjudication: proceed to code-quality review (Path A):** Agreed sequential review chain matters; spec reviewer passed clean.

**Step 19 — Code-quality review (initial dispatch wrong agent):** Initially dispatched `pr-review-toolkit:code-reviewer`. User interrupted: *"Wait that's the wrong code quality reviewer. Use the code reviewer specified in /superpowers:subagent-driven-development."* Read the canonical template at `superpowers/5.0.7/skills/subagent-driven-development/code-quality-reviewer-prompt.md` which specifies `superpowers:code-reviewer` agent type with template format `Use template at requesting-code-review/code-reviewer.md` + WHAT_WAS_IMPLEMENTED/PLAN_OR_REQUIREMENTS/BASE_SHA/HEAD_SHA/DESCRIPTION fields.

**Step 20 — Code-quality review (correct agent, 46 tool uses):** Verdict: "Ready to merge: Yes." 7 Minor findings + 2 carry-forward observations. Critical: the 2 carry-forward observations were `delegation_controller.py:1160-1161` worker reads `resolution.payload.get("response_payload", {})` (returns `{}`; worker dispatches `respond(rid, {})`) and `:1029-1031` re-park gate defect. Reviewer framed these as out-of-Task-18.

**Step 21 — User adjudication: Path 4 contract-focused fix (NOT Path 1/2/3 minor-only):** User identified the framing error: the worker stale-wrapper-keys is NOT a Phase H polish item — it contradicts spec §1665, §1699 (`DecisionResolution.payload` IS the App Server payload); convergence map at `:286` says worker dispatches `respond({"decision": ...})`. Verbatim: *"Path 1 is too light... Path 4 is the right cut. It focuses on contract truth, not cosmetic perfection."*

**Step 22 — SendMessage fix-commit dispatch to `task-18-feat-commit`:** Path 4 instruction with 5 parts (A-E): worker payload fix, regression test, re-park defect disposition (fix inline if W2-fixable, else BLOCKED), Round-7 addendum, CQ Minor #3 if trivial.

**Step 23 — Fix commit landed: `b8e7f9ce` (67 tool uses, ~11 min):** Worker payload fix at `:1160-1172` (reads `resolution.payload` directly + `resolution.action`). Operator action preservation: added optional `action: Literal["approve", "deny"] | None = None` field to `DecisionResolution` (`resolution_registry.py:33-65`). Regression test added: parameterized `test_decide_worker_dispatches_l4_payload_end_to_end` with 3 sub-cases (approve-accept, deny-decline, approve-RUI). Re-park defect FIXED INLINE within W2: lifted `if captured_request is None` gate at `:1025-1037`; removed test-side PSR.create pre-seed workarounds at 3 sites. CQ Minor #3 applied. Round-7 addendum at convergence map `:608-650`. Suite: 1017 → 1020 (+3). NEW permanent invariant: old-wrapper-key reads = 0.

**Step 24 — User adjudication: Path A direct closeout-docs with Round-6 preservation:** Verbatim: *"I would not erase the Round-6 history; mark it as adjudicated/superseded so the project record shows why W16 was narrowly pierced and why Mode A still fully retires."*

**Step 25 — SendMessage closeout-docs dispatch to `task-18-feat-commit`:** Comprehensive 4-file commit instruction with verbatim commit message body draft.

**Step 26 — Closeout-docs commit landed: `844e6f97` (30 tool uses, ~9 min):** Files staged: `carry-forward.md` (modified), `phase-g-public-api.md` (modified), `task-18-convergence-map.md` (newly tracked), `task-18-dispatch-packet.md` (newly tracked). Phase G Task 18 closeout entry at `phase-g-public-api.md:542-580`. Convergence map: Round-6 preserved verbatim with explicit supersession-marker block at start of Round-7 (`:612-618`); Round-7 addendum at `:610-655` includes 9-row fix-summary table + L15 candidate. Final invariants: W3=6, W17=2, L6=0, old constant=0, new constant=8, decorators=6, **NEW: old wrapper-key reads=0**.

**Step 27 — Phase G CLOSES.** Branch 68 commits ahead of main cumulative; 6 in Task 17+18 sub-chain.

## Decisions

### Decision: Reset Sonnet's partial work + re-dispatch on Opus (Option A)

- **Driver:** Sonnet's "Prompt is too long" at 97 tool uses is terminal context exhaustion; SendMessage cannot recover. The 222-line partial controller diff was structurally correct (W17=2, W3=6, L6=0 invariants matched) but Sonnet violated TDD ordering (rewrote controller without writing tests first), introduced typing defects (`:2591:18 PendingRequestKind` vs `EscalatableRequestKind`), and missed L10 in the second test file. User's verbatim preference: *"using opus (1M context) for subagents is usually the best when we are working on complex projects such as this."*
- **Rejected: Continue Sonnet via SendMessage.** Failure mode is terminal — context exhausted; even if delivered, agent has no budget to process.
- **Rejected: Patch Sonnet's partial work in-session.** Violates skill's "subagent does the work" principle; doesn't validate rewrite against (then-missing) acceptance tests.
- **Implication:** Sonnet's 222-line diff thrown away. Opus's 1M context handles the full prompt + 7 authority sources + 100+ tool-call results without budget pressure. TDD preamble forced test-first ordering.
- **Trade-offs:** ~15 min wasted on Sonnet attempt; cleaner ground for Opus.
- **Confidence:** High (E2) — user explicitly approved.
- **Reversibility:** High — `git restore` was clean (verified via invariant baseline grep).
- **Change trigger:** None.

### Decision: SendMessage continuation via agent ID (not name) for transient-fault recovery

- **Driver:** Opus round 1 terminated with `ConnectionRefused` after 46 tool uses + 674-line test file written. Runtime returned agentId `a5a54a1ea12f3c026` with explicit hint to use SendMessage. Tried name-based first (`to: "task-18-implementer-opus"`) — failed with "No agent named '...' is currently addressable." Switched to agent ID — succeeded with "Agent had no active task; resumed from transcript in the background."
- **Rejected: Spawn fresh Opus agent.** Would lose all in-context state — 7 authority-source reads, 674-line test file mental model.
- **Implication:** Discovered the active vs idle-but-resumable agent addressability distinction. Active agents = name-addressable. Idle-but-resumable agents (transient fault) = ID-addressable only. Context-exhausted agents = unreachable by either.
- **Trade-offs:** ID is less human-readable than name; can't easily verify which agent is being addressed without runtime context.
- **Confidence:** High (E2) — runtime hint authoritative; observed success.
- **Reversibility:** N/A — addressing is per-call.
- **Change trigger:** None.

### Decision: Adjudication D (NEW — narrow test-mechanics patch on 3 Mode A tests; NOT reclassification to G18.1)

- **Driver:** Round-6 BLOCKED report identified Python for-loop iterator binding constraint: `for x in self._server_requests:` binds at iteration start; later reassignment is invisible. Captured warning `TurnCompletedWithoutCapture` proved the failure was test-double simulation mismatch, not finalizer dependency. Reclassifying to G18.1 (which is `_finalize_turn` Captured-Request Terminal Guard / Phase H Task 19 territory) would be semantically wrong — these tests assert same-turn re-escalation, not post-resume terminal state.
- **Rejected: Option A (reclassify to G18.1).** Conflates test-infrastructure issue with finalizer dependency. Would muddy carry-forward record.
- **Rejected: Option B (global FakeSession `for`→`while pop(0)`).** Bigger blast radius than evidence requires; only these 3 tests need dynamic queue semantics.
- **Rejected: Option C (broader production scope expansion).** The stale `resolution.payload` issue is real but orthogonal to this specific BLOCKED.
- **Implication:** Patch surface is exactly 3 tests. Mutate-not-replace via `_server_requests.append(...)`; bounded polling for `poll().pending_escalation` (5s budget, 50ms intervals, 100 iter). FakeSession class definition UNCHANGED. Mode A row stays as Task-18-closing.
- **Trade-offs:** None — patch is surgical; production semantics preserved.
- **Confidence:** High (E2) — user explicitly authored the disposition.
- **Reversibility:** High — patches are localized to 3 tests.
- **Change trigger:** None.

### Decision: Path 4 contract-focused fix (NOT Path 1/2/3)

- **Driver:** Code-quality review framed `delegation_controller.py:1160-1161` worker stale-wrapper-keys as out-of-Task-18 carry-forward. User identified the framing error: spec §1665, §1699 say `DecisionResolution.payload` IS the App Server payload; convergence map at `:286` says worker dispatches `respond({"decision": ...})` / `respond({"answers": ...})`. The current code reads `resolution.payload.get("response_payload", {})` returning `{}` — worker dispatches `respond(rid, {})`. This is a Task 18 *correctness gap*, not a Phase H polish item.
- **Rejected: Path 1 (minor-only fix commit).** Improves quality but misses the highest-value finding. Tightening audit-log substring is good; leaving `respond(rid, {})` is not acceptable.
- **Rejected: Path 2 (skip fix; docs-only).** Papers over a direct mismatch with spec.
- **Rejected: Path 3 (comprehensive fix all 10 Minors).** Too much churn for a bounded fix commit.
- **Implication:** Worker payload fix at `:1160-1172`; new `DecisionResolution.action` field for operator action preservation; regression test that asserts EXACT respond payload (not just rid); re-park defect investigated (fixable inline within W2 → fix inline; if not → BLOCKED with Mode A reclassification proposal); CQ Minor #3 if trivial. W16 narrow adjudication required (def signature unchanged; body fix bounded to resume-path payload reads).
- **Trade-offs:** Touches W16-adjacent territory but stays within def-signature scope.
- **Confidence:** High (E2) — user authored the disposition with concrete spec citations.
- **Reversibility:** High — fix isolated; could revert.
- **Change trigger:** None.

### Decision: Operator action preservation via explicit `DecisionResolution.action` field (NOT payload-shape inference)

- **Driver:** Worker resume path needs to know whether the original `decide` verb was `approve` or `deny` for `record_response_dispatch` / `record_dispatch_failure`. Two options: (a) add explicit `action` field to `DecisionResolution`; (b) discriminate from `resolution.payload` shape. Agent's reasoning quoted: "approve × RUI with empty answers and deny × RUI both yield `{"answers": {}}` (ambiguous)."
- **Rejected: Payload-shape inference.** approve×RUI-with-empty-answers and deny×RUI both produce `{"answers": {}}`; payload-shape discrimination would silently misroute one of them.
- **Implication:** Added `action: Literal["approve", "deny"] | None = None` to `DecisionResolution` (`resolution_registry.py:33-65`). Default `None` covers timeout (`is_timeout=True`) and test-held uncommitted-resolution fixtures. `decide()` at `:2549` explicitly passes `action=decision`. Worker assertion-checks non-None for the operator-decide branch.
- **Trade-offs:** Slightly wider dataclass; clearer semantics.
- **Confidence:** High (E2) — agent's discrimination-ambiguity case is concrete.
- **Reversibility:** High — could revert if needed.
- **Change trigger:** None.

### Decision: Re-park defect fixed INLINE within W2 (NOT BLOCKED for Mode A reclassification)

- **Driver:** The re-park gating defect at `:1025-1037` (`if captured_request is None` gate around `_pending_request_store.create(parsed)`) needed disposition. Agent investigated: fixable by lifting the gate so `captured_request` always tracks the most-recent capture; `_finalize_turn` body is NOT touched (W2 holds). 3 test-side PSR.create pre-seed workarounds removed at `test_delegation_controller.py:1820-1836, :2460-2472` and `test_delegate_start_integration.py:1127-1138`.
- **Rejected: BLOCKED + Mode A partial-retirement.** Would force Mode A row to retire only 3/6; carry-forward debt for Phase H. The fix was structurally clean within W2.
- **Implication:** Mode A row FULLY retires (6 of 6). The 3 Task-18-closed tests now exercise the PRODUCTION re-park code path post-fix (test-side workarounds removed). Coverage improvement layered onto the fix.
- **Trade-offs:** Slightly broader fix-commit scope; better Phase G close.
- **Confidence:** High (E2) — verified by agent's diff + suite run.
- **Reversibility:** High — single gate-lift is reversible.
- **Change trigger:** None.

### Decision: Path A direct closeout-docs with Round-6 supersession-marker preservation

- **Driver:** After fix commit landed cleanly, two paths: (A) proceed directly to closeout-docs; (B) re-review the fix; (C) narrow W16/W2/W17 verification only. User adjudicated A with precision requirement: *"I would not erase the Round-6 history; mark it as adjudicated/superseded so the project record shows why W16 was narrowly pierced and why Mode A still fully retires."*
- **Rejected: Path B (re-review fix commit).** Both reviewers' feat-commit verdicts still valid for surfaces outside the worker-resume / re-park edits. Re-reviewing is brittleness-prevention for brittleness that hasn't manifested.
- **Rejected: Path C (narrow W2/W17 verification).** W16 concern is already explicitly adjudicated in Round-7; narrow patch.
- **Implication:** Round-6 framing ("out-of-Task-18 carry-forward observations") preserved verbatim. Round-7 has explicit supersession-marker block at start (`:612-618`) — Round-6 → Round-7 transition is auditable, not silently rewritten.
- **Trade-offs:** None.
- **Confidence:** High (E2) — user authored the precision requirement.
- **Reversibility:** N/A — supersession-marker pattern is already standard for Rounds 1-5.
- **Change trigger:** None.

### Decision: Pytest discipline — synchronous + timeout-wrapped + file-redirect (NOT pipe-to-tail)

- **Driver:** Opus round 2 (watchdog stall) and the second SendMessage agent both fell into the `pytest ... | tail -3` buffering trap: `tail` consumes ALL stdin before output, so if pytest hangs, tail blocks waiting forever; the agent then polls the empty output file and watchdog kills.
- **Rejected: `run_in_background: true` with Monitor + until loop.** Same anti-pattern variant; runtime hooks redirect away from `sleep` to Monitor, but Monitor + `until [ -s file ]` is still polling.
- **Implication:** All pytest invocations use `pytest ... > /tmp/file.log 2>&1` synchronous-foreground (no background, no pipe), then `tail -10 /tmp/file.log` SEPARATELY. `timeout N` shell wrapper bounds any hang to a known cap (60-180s depending on scope).
- **Trade-offs:** Agent waits up to 180s on a single pytest call; cheaper than 600s + watchdog kill.
- **Confidence:** High (E2) — observed agent failure mode + verified pattern works in subsequent dispatches.
- **Reversibility:** N/A — discipline.
- **Change trigger:** None.

## Changes

### Commits landed this session (3)

1. **`2606fb03` feat(delegate): rewrite decide() with reservation two-phase protocol (T-20260423-02 Task 18)**
   - 358 insertions, 295 deletions across 3 modified files + 1 new file (671 lines test scaffolding)
   - Files: `delegation_controller.py`, `test_delegation_controller.py`, `test_delegate_start_integration.py`, `test_delegate_decide_async_integration.py` (new)
   - Includes Round-6 Adjudication D test-mechanics patches (Mode A unskips with mutate-not-replace + bounded polling)
   - L4 Path A artifact citation in commit message body

2. **`b8e7f9ce` fix(delegate): address Task 18 closeout review (T-20260423-02 Task 18 closeout)**
   - Worker payload fix at `delegation_controller.py:1160-1172` (read `resolution.payload` directly + `resolution.action`)
   - New `DecisionResolution.action` field at `resolution_registry.py:33-65`
   - Re-park defect FIXED INLINE at `delegation_controller.py:1025-1037` (lifted gate); removed test-side PSR.create workarounds at 3 sites
   - New parameterized regression `test_decide_worker_dispatches_l4_payload_end_to_end` with 3 sub-cases
   - CQ Minor #3 applied (audit-log substring tightening with `getMessage()`)
   - Round-7 addendum to convergence map `:608-650` (W16 narrow adjudication + 9-row fix-summary + L15 candidate)
   - Suite delta: 1017 → 1020 (+3 from new regression)
   - NEW permanent invariant: old-wrapper-key reads = 0

3. **`844e6f97` docs(delegate): record Phase G Task 18 closeout (T-20260423-02)**
   - 4 files staged: `carry-forward.md` (modified), `phase-g-public-api.md` (modified), `task-18-convergence-map.md` (newly tracked), `task-18-dispatch-packet.md` (newly tracked)
   - `carry-forward.md`: G17.1 closed, Mode A fully retired, F16.2 lineage annotated, G18.1 introduced verbatim, TT.1 promoted, RT.1 unchanged
   - `phase-g-public-api.md`: Phase G Task 18 closeout entry at `:542-580` per Phase E/F precedent
   - `task-18-convergence-map.md`: Round-6 preserved verbatim; Round-7 supersession-marker block at `:612-618`; Round-7 addendum at `:610-655`; Verification artifacts section at `:604-606`
   - Phase G CLOSES; Phase H Task 19 inherits the carry-forward set

### Files modified

| File | Purpose |
|---|---|
| `packages/plugins/codex-collaboration/server/delegation_controller.py` | `decide()` rewrite + `_build_response_payload` helper + worker payload dispatch fix + re-park gate lift |
| `packages/plugins/codex-collaboration/server/resolution_registry.py` | `DecisionResolution.action` field added |
| `packages/plugins/codex-collaboration/tests/test_delegate_decide_async_integration.py` | NEW — 671 lines (initial) + new parameterized regression test_decide_worker_dispatches_l4_payload_end_to_end (post-fix) |
| `packages/plugins/codex-collaboration/tests/test_delegation_controller.py` | L10 constant rename + L11 deletions + Mode A unskips with Round-6 patches + L12 reclassifications + Round-7 PSR-pre-seed workarounds removed |
| `packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py` | L10 constant rename + Mode A unskip with Round-6 patches + Round-7 PSR-pre-seed workaround removed |
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-convergence-map.md` | Round-6 + Round-7 addenda; supersession-marker block; Verification artifacts section; newly tracked |
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-dispatch-packet.md` | Newly tracked (no edits this session) |
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` | G17.1 closed; Mode A retired; F16.2 lineage; G18.1 introduced; TT.1 promoted |
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md` | Phase G Task 18 closeout entry at `:542-580` |

## Codebase Knowledge

### Worker resume path payload contract (post-Round-7)

**Pre-Round-7:** Worker at `delegation_controller.py:1160-1161` read `resolution.payload.get("resolution_action", "approve")` and `resolution.payload.get("response_payload", {})`. Under Task 18's new flow, `resolution.payload` IS the bare App Server payload (e.g. `{"decision": "accept"}`); the wrapper keys don't exist; worker dispatched `respond(rid, {})`.

**Post-Round-7:** Worker reads `resolution.payload` directly + `resolution.action` (operator verb). `_build_response_payload` produces App-Server-shape; worker dispatches verbatim to `session.respond(...)`.

### `DecisionResolution.action` field semantics

- Field signature: `action: Literal["approve", "deny"] | None = None`
- `decide()` always passes `action=decision`
- Default `None` for timeout (`is_timeout=True`) and test-held uncommitted resolutions
- Worker assertion-checks non-None for operator-decide branch; uses for `record_response_dispatch` / `record_dispatch_failure`

### L4 Path A verification artifact

- **Fixture:** `packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/ToolRequestUserInputResponse.json` (committed 2026-03-27)
- **Wire shape:** `{"answers": {<qid>: {"answers": [<string>...]}}}`
- **Ground-truth verification:** `test_build_response_payload_per_kind_decision` at `test_delegate_decide_async_integration.py:612-669` parameterizes the 6-row binding contract; approve × RUI row at `:624-629` asserts EXACT payload `{"answers": {"q1": {"answers": ["yes"]}}}`
- **Path A option:** 3 (pinned-version integration test against versioned fixture)

### Re-park gate (post-Round-7)

- **Pre-Round-7:** `if captured_request is None: pending_request_store.create(parsed)` at `:1025-1037` — gate prevented re-park PSR.create on subsequent captures within same turn; tests had to pre-seed PSR via test-side workarounds.
- **Post-Round-7:** Gate lifted; `captured_request` always tracks most-recent capture; `_pending_request_store.create()` runs unconditionally for new captures. Test-side PSR.create workarounds removed at 3 sites; tests now exercise production re-park path.

### Permanent invariants (post-Phase-G)

| Invariant | Expected | Audit |
|---|---|---|
| W3 (sentinel raises) | 6 | `grep -nF "_WorkerTerminalBranchSignal(reason=" delegation_controller.py \| wc -l` |
| W17 (DelegationEscalation sites) | 2 | `grep -c "DelegationEscalation(" delegation_controller.py` |
| L6 (`_decided_request_ids` retired) | 0 | `grep -n "_decided_request_ids" delegation_controller.py \| wc -l` |
| Old constant (`_TASK_18_DECIDE_SIGNAL_REASON`) | 0 | `grep -rn "_TASK_18_DECIDE_SIGNAL_REASON" packages/plugins/codex-collaboration/tests/ \| wc -l` |
| New constant (`_TASK_19_FINALIZER_GUARD_REASON`) | 8 | `grep -rn "_TASK_19_FINALIZER_GUARD_REASON" packages/plugins/codex-collaboration/tests/ \| wc -l` |
| New constant decorators | 6 | `grep -rn "@pytest.mark.skip(reason=_TASK_19_FINALIZER_GUARD_REASON)" packages/plugins/codex-collaboration/tests/ \| wc -l` |
| **NEW: Old wrapper-key reads** | 0 | `grep -rn "resolution\.payload\.get" delegation_controller.py \| wc -l` |
| F16.1 decorators preserved | 2 | `grep -c "@pytest.mark.skip" test_handler_branches_integration.py` |

### Convergence map structural anatomy (post-Round-7)

| Section | Lines | Purpose |
|---|---|---|
| Top revision marker | 1-3 | Round chronology with supersession trail |
| Scope | 5 | Task 18 vs Task 19 boundary |
| Authority order (9 layers) | 7-17 | Spec > plan > carry-forward > live code |
| Live anchors table | 19-54 | File:line citations verified at HEAD |
| Locks L1-L14 | 56-230 | Binding positive scope |
| Watchpoints W1-W18 | 232-281 | Binding negative scope |
| Branch matrix | 283-296 | 10 rows decision × kind × outcome |
| Per-test triage | 298-338 | Bucket B disposition |
| G18.1 carry-forward record | 340-367 | Pre-authorizations Task 19 inherits |
| Out-of-scope | 369-383 | Plan/spec citations |
| Acceptance criteria | 385-429 | Code/Tests/Closeout-docs checkboxes |
| Pre-dispatch checklist | 431-456 | 16 items |
| Commit shape | 458-466 | 1+1+1 anticipated |
| Carry-forward expectations | 468-485 | Net change matrix |
| Pre-dispatch warnings | 489-498 | High-risk loci |
| Restructure Record + Round 2/3/4 addenda | 500-548 | Rounds 1-4 history |
| Round-5 addendum | 550-566 | W17/`:2400` mechanical-impossibility |
| Round-6 addendum (preserved verbatim) | 568-606 | For-loop iterator binding + Adjudication D |
| Verification artifacts section | 604-606 | L4 Path A citation |
| Round-7 supersession-marker block | 612-618 | Round-6 → Round-7 transition (NEW) |
| Round-7 addendum | 610-655 | W16 narrow adjudication + 9-row fix table + L15 candidate |

### Termination mode taxonomy (3 distinct kinds observed)

| Mode | Recovery? | Strategy |
|---|---|---|
| `Prompt is too long` (context exhaustion) | NO | Reset + fresh dispatch with bigger-context model |
| `Unable to connect to API (ConnectionRefused)` (transient fault) | YES via SendMessage by agent ID | Resume from preserved transcript; agentId-only addressable |
| Watchdog stall (no progress for 600s; pytest hang or output buffering) | NO (process killed) | Fresh dispatch with hardened pytest discipline |

### Agent addressability

- **Active agents:** name-addressable via SendMessage
- **Idle-but-resumable (transient fault):** agentId-addressable only; runtime returns ID with explicit hint
- **Context-exhausted or watchdog-killed:** unreachable; fresh dispatch required

### Pytest discipline (post-Round-7 binding pattern)

- `pytest ... > /tmp/file.log 2>&1` synchronous-foreground (NO `| tail` pipe; NO `run_in_background: true`)
- `timeout N` shell wrapper for hang bounding (60s collect-only; 120s targeted; 180s full suite)
- `tail -N /tmp/file.log` SEPARATELY after pytest completes
- pytest-timeout plugin NOT installed; only shell `timeout` works
- Forbidden: `sleep N && tail`, `until [ -s file ]`, `.done` markers, Monitor + until on file size

## Context

**Mental model:** This session is a textbook example of a *complex multi-agent dispatch executing across multiple runtime fault classes*. Each fault required a different recovery strategy. The convergence map's structural integrity (binding authority preserved across all 7 rounds) was the dispatch chain's anchor — every adjudication stayed grounded in spec authority + live-code evidence + carry-forward state. The user's pattern of authoring concrete dispositions (Adjudication D, Path 4) rather than picking from agent-proposed options is itself a valuable signal: the agent identified the structural defect class but the user identified the right correction class.

**Core insight:** Round-7's W16 narrow adjudication establishes the third process-precedent extension this session (Round-5 W17/`:2400` mechanical impossibility; Round-6 for-loop iterator binding; Round-7 worker payload contract correctness). Each round identified a defect that earlier rounds couldn't have seen — Round-5 was an asymptotic constraint (live grep ownership analysis); Round-6 surfaced during Bucket B unskip verification; Round-7 surfaced during code-quality review. The pattern is robust: each review layer catches different defect classes; the convergence map's addenda chain preserves chronology so future task readers see the discovery ordering.

**Framing analogy:** Multi-round review on complex dispatch is like layered fault injection in distributed systems — each layer has its own error mode, and you only catch all of them by running every layer. The Task 18 implementer dispatch went through 4 implementer rounds + 2 review rounds + 1 fix round + 1 docs round = 8 layers of execution, each catching distinct issues that earlier layers couldn't have seen by definition.

## Learnings

### Patterns

- **Termination mode dictates recovery strategy.** "Prompt is too long" = terminal (context full); fresh dispatch needed. "ConnectionRefused" = transient (idle agent); SendMessage by ID. Watchdog stall = process-killed (resource issue OR hang); fresh dispatch with hardened discipline.
- **Round-N supersession-marker pattern extends indefinitely.** Each round's addendum chains chronologically; superseded earlier text gets in-place "superseded by round-N+1" cross-refs. Robust through 7 rounds this packet (5 + 6 + 7 added this session).
- **Producer-consumer contract assertion is essential for L-class locks.** L4 verified producer side (helper output matches 6-row table); was only verified at consumer side (worker dispatches verbatim) in Round-7's regression test. Future convergence maps should explicitly assert producer-consumer end-to-end at lock specification time. (L15 candidate per Round-7 addendum.)
- **Test-side workarounds for production bugs hide test-coverage gaps.** Pre-Round-7, the 3 Mode A tests had test-side `pending_request_store.create()` pre-seeds because the production gate at `:1025-1037` was broken. Removing both (production fix + test workarounds) gave the tests production-path coverage.
- **Operator action preservation should be explicit, not inferred.** When two valid states yield the same payload shape (approve × RUI with empty answers ≡ deny × RUI), discrimination via shape is structurally ambiguous. Add an explicit field.
- **Synchronous + timeout-wrapped pytest is the only safe pattern for subagent dispatches.** Background runs + polling loops + Monitor + until are all variants of the same anti-pattern: hidden hangs. File-redirect + foreground + `timeout` bounds the failure mode.
- **TDD ordering needs explicit reinforcement under context pressure.** A single mention buried in a 400-line prompt is insufficient. A dedicated DISPATCH NOTE preamble + numbered concrete sequence (1-14) with the test-write step at Step 1 of N is needed to override the visible-artifact-bias.

### Gotchas

- **Python `for x in self._server_requests:` binds the iterator to the list object at iteration start.** Reassigning `self._server_requests = [new_list]` is INVISIBLE to the active iterator. Mutate (`.append`, `.extend`) instead of replace if dynamic semantics are needed during iteration.
- **`pytest ... | tail -N` buffers stdin entirely until pytest finishes.** If pytest hangs, `tail` blocks waiting; you can't see incremental progress. Use `pytest > /tmp/file.log 2>&1` then `tail -N /tmp/file.log` separately.
- **`pytest-timeout` plugin is NOT installed in this project.** `--timeout=N` flag fails with "unrecognized arguments". Use shell `timeout N` wrapper.
- **`_worker_thread` is NOT a public attribute on `DelegationController`.** It's a local in `start()`. Tests use thread-enumeration-by-name for teardown sync.
- **`resolution.payload` is the BARE App Server payload under Task 18's new flow.** No wrapper keys. Reading `.get("response_payload", {})` returns `{}`; reading `.get("resolution_action", "approve")` returns `"approve"` always. The audit `grep "resolution\.payload\.get" delegation_controller.py | wc -l = 0` is the permanent invariant.
- **PendingRequestKind includes `'unknown'`; EscalatableRequestKind does NOT.** Naive `DecisionResolution(kind=request.kind, ...)` fails Pyright. Need branch narrowing or `cast()` after validation guarantees the request is escalatable.
- **Pyright's `pytest` import unresolved at test files is pre-existing TT.1 noise; ignore.**
- **Agent name lookup fails for idle-but-resumable agents.** Use agentId for SendMessage continuation after transient faults.

### Conventions

- **Subagent dispatch chain:** implementer → spec-compliance reviewer → code-quality reviewer → user adjudication → closeout-fix (via SendMessage to implementer agent) → closeout-docs (via SendMessage). Each step has a focused agent with tight scope.
- **Commit shape 1+1+1:** feat (Step 1) + fix (Step 2, optional but anticipated) + docs (Step 3, mandatory). All staged with explicit `git add <path>` per file.
- **Round-N addendum format:** Append to convergence map after prior round's addendum; preserve earlier text with in-place supersession markers when round-N supersedes; document discovery + classification + future-prevention pattern.
- **Authority hierarchy in adjudications:** spec > plan body > carry-forward > live code (when live code is the legacy flow being replaced).

### Connections

- **Round-5 (W17/`:2400` mechanical impossibility) → Round-6 (for-loop iterator binding) → Round-7 (worker payload contract):** all three are layered fault discoveries that no single review layer could have caught alone.
- **Sonnet's TDD violation → Opus's test-first approach:** TDD ordering is a discipline that scales with model context; under pressure, smaller-context models prioritize visible artifact (controller) over scaffolding (tests).
- **Adjudication D (Round-6) → Path 4 (Round-7):** both are user-authored corrections to agent-proposed options. Pattern: user identifies the structural class while agent proposes within enumerated options.
- **W16 narrow adjudication → L15 candidate:** Round-7 surfaced a producer-consumer contract assertion as a candidate for binding lock status in future Tasks. Phase H may formally promote.

## Next Steps

1. **Phase H Task 19 dispatch — fresh session.** Convergence map authoring + dispatch packet construction for `_finalize_turn` Captured-Request Terminal Guard rewrite per spec §1738-1808. Inherits G18.1 carry-forward verbatim (6-test list, renames at `:1881/:1927`, body rewrite for `:1525`, L12 assertion review for 3 others, constant `_TASK_19_FINALIZER_GUARD_REASON` deletion).

2. **Carry forward into Phase H Task 19's convergence map:**
   - F16.1 (2 unchanged at `tests/test_handler_branches_integration.py:161, :179`)
   - RT.1 unchanged (`runtime.py:270` TurnStatus literal narrowing; end-of-Phase-G or end-of-Packet-1 typing polish)
   - TT.1 newly promoted (`_FakeControlPlane` Pyright issues at `test_delegation_controller.py:259, 2878, 3075, 3205, 3429, 3786`)
   - G18.1 newly introduced verbatim per Task 18 closeout-docs
   - F16.2 lineage marker only; closes via G18.1 when Phase H Task 19 lands

3. **Process precedent to bake into Phase H Task 19's convergence map authoring:**
   - L15 candidate (producer-consumer contract assertion) — promote to binding lock if Phase H wants
   - Round-N supersession-marker pattern continues; Round-1 of Phase H Task 19 starts fresh
   - Pytest discipline (synchronous + timeout-wrapped + file-redirect) is now binding for all subagent dispatches
   - W18 BLOCKED protocol is mandatory for any test reclassification beyond pre-authorization

4. **Optional housekeeping:**
   - Update memory entries to reflect Phase G CLOSES + Phase H Task 19 next
   - `git log -p 2606fb03..844e6f97` review of full Task 18 chain end-to-end before next session (optional)
   - Promote applicable session learnings to feedback memories: termination-mode taxonomy, pytest discipline, supersession-marker pattern, agent addressability

## In Progress

**Status:** Phase G CLOSES. Task 18 1+1+1 chain landed (`2606fb03` feat + `b8e7f9ce` fix + `844e6f97` docs). Branch 68 commits ahead of main cumulative; 6 in Task 17+18 sub-chain. Working tree clean. All invariants pass.

- **Approach:** Done — no in-flight work. Phase H Task 19 dispatch is a separate session.
- **State:** Suite 1020p/8s/0f in 123.70s. W5 hang verification 3-file scope passes both orderings 124p/6s in ~105s. All 14 locks (L1-L14) PASS, all 18 watchpoints (W1-W18) PASS, Round-7 W16 narrow adjudication documented. L4 Path A artifact verified. Old wrapper-key reads = 0 NEW permanent invariant.
- **Working:** Phase G complete. Phase H carry-forward set fully prepared.
- **Not working/incomplete:** N/A — session complete.
- **Open question:** None for Task 18. Task 19's L15 candidate (producer-consumer contract assertion) is an open future decision but not blocking.
- **Next action:** Fresh session for Phase H Task 19 convergence map + dispatch packet authoring.

## Open Questions

- **L15 candidate promotion.** Round-7 surfaced producer-consumer contract assertion as a candidate for binding lock status. Phase H Task 19 convergence map can either adopt it as L15 (binding) or keep it as informal future-prevention pattern. User decision when authoring Phase H convergence map.
- **CQ Minor #1 (`assert_never` for `_build_response_payload`).** Deferred to RT.1/TT.1 typing polish. May surface as a separate cleanup task in Phase H or end-of-Packet-1.
- **CQ Minor #5 (duplicated inline imports).** Promoted to top of file is the cleanup, but defer to a future test-cleanup sweep.
- **Spec reviewer M2 (Step labels)** + **CQ Minor #6 (stale comment about helper naming).** Documentation precision; defer to Phase H or future doc sweep.

## Risks

- **Phase H Task 19 may surface additional L-class locks via deeper review rounds.** Round-N supersession is well-established; expect Phase H to take 3-5 rounds for convergence map dispatch-readiness.
- **TT.1 `_FakeControlPlane` Pyright issues are now formal carry-forward.** If Phase H or end-of-Packet-1 typing polish doesn't address them, they accumulate. Track in carry-forward.md.
- **The Round-7 W16 narrow adjudication is precedent.** Future tasks may try to invoke "narrow adjudication" to pierce other watchpoints. Each pierce should be evidence-based (specific defect + spec citation) and explicitly documented in a Round-N addendum, not silently applied.
- **Agent runtime instability observed this session (3 termination modes).** Phase H dispatches should default to Opus (per user preference) and adopt pytest discipline + 14-step concrete sequence preamble pattern from the start.
- **PendingRequestKind / EscalatableRequestKind narrowing.** Multiple sites in the codebase pass `request.kind` to constructors expecting narrower types. The agent navigated this via `Literal` annotations + careful branch narrowing, but there may be additional sites surfaced as Phase H code lands.

## References

### Prior handoffs (chain)

- **Resumed from (mid-session):** `docs/handoffs/archive/2026-04-26_15-45_task-18-opus-implementer-in-flight-after-sonnet-budget-failure.md`
- Earlier in chain: `docs/handoffs/archive/2026-04-26_13-52_task-18-dispatch-packet-ready-after-round-5-correction.md`
- Earlier: `docs/handoffs/archive/2026-04-26_13-26_task-18-convergence-map-dispatch-ready.md`
- Earlier: `docs/handoffs/archive/2026-04-26_07-02_phase-g-task-17-dispatch-and-closure.md`

### Active artifacts (now committed)

- **Convergence map (committed):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-convergence-map.md` (655 lines post-Round-7; previously 606 post-Round-6)
- **Dispatch packet (committed):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-dispatch-packet.md` (468 lines, unchanged from prior session)
- **Plan body:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md` (Phase G Task 18 closeout entry at `:542-580`)
- **Carry-forward state:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (G17.1 closed; Mode A retired; F16.2 lineage; G18.1 introduced verbatim; TT.1 promoted; RT.1 unchanged)
- **Spec authority:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`

### Live code

- `packages/plugins/codex-collaboration/server/delegation_controller.py` @ HEAD `844e6f97` (post-Round-7 fix in place; W17=2 + W3=6 invariants hold)
- `packages/plugins/codex-collaboration/server/resolution_registry.py` @ HEAD `844e6f97` (post-Round-7; new `action: Literal["approve", "deny"] | None` field)
- New file: `packages/plugins/codex-collaboration/tests/test_delegate_decide_async_integration.py` (~700 lines post-fix; 10 named tests + 1 parameterized 6× + new parameterized 3× regression)
- L4 Path A fixture: `packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/ToolRequestUserInputResponse.json`

### Agent metadata (this session)

| Agent | Model | Termination | Tool uses | Outcome |
|---|---|---|---|---|
| `task-18-implementer` (Sonnet) | sonnet | Prompt is too long | 97 | Reset; partial diff discarded |
| `task-18-implementer-opus` (Opus 1) | opus | ConnectionRefused | 46 | 674-line test file landed |
| `task-18-implementer-opus` (Opus 1, resumed via SendMessage) | opus | Watchdog stall | ~70 | Test file refined; Round-6 BLOCKED + adjudication |
| `task-18-implementer-opus-3` (Opus 2) | opus | BLOCKED on 3 Mode A tests | 91 | Adjudication D produced |
| `task-18-implementer-opus-3` (resumed for Adj-D) | opus | "completed" with stall artifact | 112 | Mode A patches landed; suite verified manually |
| `task-18-feat-commit` (focused) | opus | DONE | 11 | Feat commit `2606fb03` |
| `task-18-spec-reviewer` | opus | DONE | 49 | APPROVED with 3 Minor |
| `task-18-code-reviewer` (`superpowers:code-reviewer`) | (default) | DONE | 46 | "Ready to merge: Yes" with 7 Minor + 2 carry-forward |
| `task-18-feat-commit` (resumed for fix) | opus | DONE | 67 | Fix commit `b8e7f9ce` |
| `task-18-feat-commit` (resumed for docs) | opus | DONE | 30 | Docs commit `844e6f97` |

### Memory entries (existing; relevant)

- `feedback_subagent_driven_development_meaning.md` — full review chain workflow
- `feedback_bucket_reclassification_requires_blocked.md` — L11/L12/W18 BLOCKED protocol
- `feedback_assertion_shape_implementer_discretion.md` — L13 precedent
- `feedback_no_midtrack_doc_commits.md` — commit boundaries

## Gotchas

- **`for x in self._server_requests:` iterator binding:** binds at iteration start; reassignment is invisible. Mutate (`.append`, `.extend`) for dynamic semantics.
- **`pytest ... | tail -N` buffering trap:** tail consumes ALL stdin before output. Use `pytest > /tmp/file.log 2>&1` then `tail -N /tmp/file.log` separately.
- **`pytest-timeout` plugin NOT installed.** Only shell `timeout N` works.
- **`resolution.payload.get(...)` is now FORBIDDEN in production code:** `grep -rn "resolution\.payload\.get" delegation_controller.py = 0` is a NEW permanent invariant from Round-7.
- **`_worker_thread` is NOT public on DelegationController.** Use thread-enumeration-by-name for teardown sync.
- **`PendingRequestKind` includes `'unknown'`; `EscalatableRequestKind` does NOT.** Branch narrowing or `cast()` required at boundaries.
- **Round-6 framing is preserved verbatim with supersession markers; do NOT silently rewrite to retroactively claim issues were always in-scope.** The Round-6 → Round-7 transition is auditable.
- **Mode A row FULLY retires in Task 18.** Phase H readers should NOT assume any partial-retirement caveat — Round-7's inline fix made it complete.
- **G18.1 has `_TASK_19_FINALIZER_GUARD_REASON` constant deletion as pre-authorized when Task 19 lands.** The constant + 6 decorators are scaffolding; Task 19's final state has them removed.
- **The Sonnet's `:2591:18 PendingRequestKind` typing trap recurred in Opus dispatches at different line numbers.** It's a real wiring issue at the `decide() → DecisionResolution(kind=request.kind, ...)` boundary; will reappear in any naive rewrite.
- **L4 Path A artifact pinning to v0.117.0 means the fixture file path is version-locked.** If codex-app-server upgrades, the fixture path must be updated AND the test's expected payload re-verified against the new version's schema.

## Conversation Highlights

User's framing across the session was decisive on adjudication points and forensically grounded on technical disputes:

**Recovery framing (Step 4):**
> "Honestly, using opus (1M context) for subagents is usually the best when we are working on complex projects such as this."

**Continuation correction (Step 10):**
> "Yes. Proceed with the **4th Opus dispatch**, but do it as a **corrected continuation dispatch**, not a replay of the original packet. ... I would also not take over manually unless the next dispatch fails for a new non-instruction reason. The latest failure is explainable and preventable."

**Adjudication D (Step 12) — user authored the disposition not in agent's options:**
> "Patch only the three re-escalation tests... The correction is test mechanics only: the active FakeSession/_ConfigurableStubSession worker turn already holds an iterator over the original _server_requests list. Do not replace that list after start(); append/mutate the active list..."

**Path 4 framing (Step 21) — user identified the misclassification:**
> "I would not take Path 1 as written. The option set changed once the 'carry-forward observations' were named: at least the stale `resolution.payload` wrapper issue is not a Phase H polish item; it contradicts Task 18's core dispatch contract."
> "Path 4 is the right cut. It focuses on contract truth, not cosmetic perfection."

**Round-6 preservation precision (Step 24):**
> "I would not erase the Round-6 history; mark it as adjudicated/superseded so the project record shows why W16 was narrowly pierced and why Mode A still fully retires."

**Code-quality review correction (Step 19):**
> "Wait that's the wrong code quality reviewer. Use the code reviewer specified in /superpowers:subagent-driven-development"

## User Preferences

- **Opus default for complex multi-file dispatches.** Verbatim: *"using opus (1M context) for subagents is usually the best when we are working on complex projects such as this."*
- **Adjudicate between rounds — don't auto-proceed.** Per `feedback_subagent_driven_development_meaning.md`. User explicitly chooses paths between dispatch rounds (recovery option, adjudication D, Path 4, Path A).
- **Authoritative dispositions over agent-proposed options.** When agent proposes A/B/C/D, user often authors a NEW option that better matches the structural defect class. Pattern: agent identifies symptoms; user identifies correct correction class.
- **Forensic technical framing.** User cites specific spec sections (§1665, §1699), file:line locations (`:286`, `:1160-1161`), and concrete code semantics (Python for-loop iterator binding) when adjudicating.
- **Process precedent preservation.** Round-N supersession-marker pattern, addenda chain chronology, "do NOT silently rewrite" precision requirements.
- **Don't take over manually unless agent fails for a NEW non-instruction reason.** Reset gate is conservative; user wants subagent workflow honored even through multiple failures.
- **Save-on-major-state-transitions cadence.** Mid-session save when implementer chain reaches a turning point; final save when phase closes. Pattern observed across this and prior sessions.
- **Multi-round review with /copy paste.** P1/P2/P3 priorities; file:line citations; confidence scores. (Not exercised this session because the dispatch was the focus; carries over from prior sessions.)
- **Architectural precision over speed.** User found the Path 4 framing error after both reviewers had passed the feat commit; the additional fix-commit cycle was the right call despite both reviewers' "ready to merge" verdicts.
- **Sequential review chain matters.** User explicitly chose Path A (proceed to code-quality review) after spec-compliance APPROVED, even though Path B (skip) was defensible.

## Rejected Approaches

### Sonnet retry via SendMessage (rejected at Step 4)

- **Tried (considered):** SendMessage to dead Sonnet agent with reset state.
- **Failed because:** Context exhaustion is terminal; even if SendMessage delivered, agent has no budget. Different from ConnectionRefused (transient).
- **Learned:** Termination cause is the recovery key. Match strategy to fault class.

### Inspect Sonnet partial work and patch in-session (rejected at Step 4)

- **Tried (considered):** Read 222-line controller diff; fix `:2591:18` typing manually; commit; dispatch focused agent for tests.
- **Failed because:** Violates skill's "subagent does the work" principle. Doesn't validate rewrite against (then-missing) acceptance tests. User TDD preference would be violated.
- **Learned:** Controller-side patching is last resort. Reset + re-dispatch is cleaner.

### SendMessage to Opus by name after ConnectionRefused (rejected at Step 6)

- **Tried:** `to: "task-18-implementer-opus"`.
- **Failed because:** Idle-but-resumable agents lose name addressability.
- **Learned:** Use agentId for resume; runtime hint is authoritative.

### Spawn fresh Opus agent for resume (rejected at Step 6)

- **Tried (considered):** Dispatch new agent with full prompt + state recap.
- **Failed because:** Wastes in-context state from first Opus run (authority-source reads, test file mental model). SendMessage by ID achieves the same outcome at far lower cost.
- **Learned:** Resume > re-dispatch when transcript is preserved.

### Send minimal "continue" message (rejected at Step 7)

- **Tried (considered):** Bare resume message: "Continue from where you left off."
- **Failed because:** Agent doesn't see new-diagnostics from main session. Would re-discover defects by burning tool uses.
- **Learned:** Inject observable defects in resume messages; agent retains discretion.

### Reclassify 3 Mode A tests to G18.1 (Option A; rejected at Step 12)

- **Tried (considered):** Reclassify per agent's recommendation.
- **Failed because:** Conflates test-infrastructure issue with finalizer dependency. Captured warning `TurnCompletedWithoutCapture` proved test-double simulation mismatch, not finalizer dependency. G18.1 is finalizer-guard territory; semantically wrong.
- **Learned:** Bucket B reclassification needs test-mechanism analysis, not just "this fails so defer it."

### Global FakeSession `for`→`while pop(0)` change (Option B; rejected at Step 12)

- **Tried (considered):** Change all FakeSession iteration semantics globally.
- **Failed because:** 27 existing usages; bigger blast radius than evidence requires; only 3 tests need dynamic queue.
- **Learned:** Surgical fix > global infrastructure change when surface is bounded.

### Path 1 minor-only fix commit (rejected at Step 21)

- **Tried (considered):** Address CQ Minor #2/#3/#4 only.
- **Failed because:** Misses the highest-value finding (worker stale-wrapper-keys = correctness gap, not polish).
- **Learned:** Triage findings by *contract correctness* vs *style*, not by "the reviewer marked it Minor."

### Path 2 docs-only closeout (rejected at Step 21)

- **Tried (considered):** Skip fix; record findings in closeout-docs.
- **Failed because:** Papers over a direct mismatch with spec §1665, §1699.
- **Learned:** Documentation cannot substitute for correctness fix.

### Path 3 comprehensive fix all 10 Minors (rejected at Step 21)

- **Tried (considered):** Address every finding.
- **Failed because:** Too much churn for a bounded fix commit; both reviewers approved 7 of 10 as "no fix needed."
- **Learned:** Scope discipline applies to fix commits too.

### Path B / C re-review fix commit (rejected at Step 24)

- **Tried (considered):** Run another spec-compliance + code-quality round on the fix.
- **Failed because:** Both reviewers' feat-commit verdicts still valid for surfaces outside the worker-resume / re-park edits. Re-reviewing is brittleness-prevention for brittleness that hasn't manifested.
- **Learned:** Review chain rigor has a saturation point; trust reviewers' approval and the fix's own regression test.

### Initial code-quality review with `pr-review-toolkit:code-reviewer` (rejected at Step 19)

- **Tried:** Dispatched `pr-review-toolkit:code-reviewer`.
- **Failed because:** User identified it as the wrong reviewer; the canonical workflow uses `superpowers:code-reviewer` per the skill template at `code-quality-reviewer-prompt.md`.
- **Learned:** Skill templates specify exact agent types; honor the canonical workflow rather than substituting similar-named agents.
