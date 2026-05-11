---
date: 2026-04-25
time: "16:43"
created_at: "2026-04-25T20:43:31Z"
session_id: 00a60b8a-36cd-4be8-a4ee-535ab70d4709
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-25_15-42_phase-f-task-15-complete-task-16-next.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: 475d0506
title: Phase F Task 16 convergence map drafted — option (b) scope locked, ready for fresh-session dispatch packet
type: handoff
files:
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md
---

# Handoff: Phase F Task 16 convergence map drafted — option (b) scope locked, ready for fresh-session dispatch packet

## Goal

Construct a binding convergence map for Phase F Task 16 of T-20260423-02 Packet 1 (Deferred-Approval Response) via the user's two-read protocol, then save a handoff for fresh-session dispatch-packet construction. Task 16 is the LARGEST task in Packet 1 — handler rewrite for async-decide model + 6 sentinel raise sites + 3 new helpers (`_handle_timeout_wake`, `_write_completion_and_audit_timeout`, `_repo_root_for_journal`) + registry init + module constant + 8 `update_parked_request` callsites + 4 `completion_origin="worker_completed"` writes + carry-forward closures (A2 + C10.4 + A3 audit).

**Trigger:** Resumed from `2026-04-25_15-42_phase-f-task-15-complete-task-16-next.md` at commit `475d0506` on `feature/delegate-deferred-approval-response`. Prior session deferred Task 16 dispatch to a fresh session per user's "Phase F Task 16 dispatch (FRESH session)" Next Steps directive — Task 16 anticipated 2-3× larger than Task 15's convergence map.

**Stakes:** Task 16 dispatch is blocked until convergence-map scope adjudication is locked. The L9 stop-rule (cancel-success / decide-success rely on Task 19's `_finalize_turn` rewrite) creates a real sequencing conflict that needs explicit resolution before any code can be written.

**Success criteria (achieved):**
- Convergence map drafted at `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md` (264 lines, 2.0× Task 15's 131)
- Two-read protocol convergence achieved (controller + user independently identified L9 stop-rule)
- Option (b) scope locked: Task 16 lands ALL code; 2 finalizer-routed integration tests skip with Task 19 citations
- 11 locks (L1-L11) + 13 watchpoints (W1-W13) + 8-row branch matrix
- 17 → 14 carry-forward open-item arithmetic verified (A2 closes, C10.4 closes, A3 audits/closes; F16.1 added)
- Handoff saved before context budget exhaustion (89% at save trigger)

**Connection to project arc:** Phase F Task 15 complete (Task 15 closed A1 by L4); Task 16 closes A2 + C10.4 + audits A3. Phase F closes after Task 16. Phase G (Tasks 17-18) starts after that.

## Session Narrative

**Stage 1 — Resumption + handoff load.** Started by `/handoff:load` (state file written at `docs/handoffs/.session-state/handoff-00a60b8a-...`). Prior handoff `2026-04-25_15-42_phase-f-task-15-complete-task-16-next.md` resumed cleanly. Re-read Task 15's convergence map at `task-15-convergence-map.md` as the structural template for Task 16's drafting.

**Stage 2 — User confirmed orientation pass.** Initial response offered to start drafting; user confirmed: "Continue with the read-only Task 16 orientation and convergence-map drafting pass."

**Stage 3 — Task list + foundational reads in parallel.** TaskCreate set up 9 tasks. Issued 5 parallel reads + 2 parallel grep batches: anchor grep over `delegation_controller.py` (top-level + key symbols), anchor grep over `resolution_registry.py`, file size check, plus parallel reads of: Task 15 convergence map (template, 131 lines), Phase F plan body lines 377-826 (Task 16 main body), current `_server_request_handler` body at `delegation_controller.py:740-908`, `ResolutionRegistry.register` signature at `resolution_registry.py:160-260`, `carry-forward.md` (full).

**Stage 4 — Independent orientation findings (controller's read).**
- `_server_request_handler` body is at `delegation_controller.py:765-835` — plan cites stale `:650-720` (Task 15 added ~+27 lines)
- `_finalize_turn` is at `:1611` (Task 19 territory; W-locked)
- `ResolutionRegistry.register` signature at `resolution_registry.py:173-180` REQUIRES `kind: EscalatableRequestKind` as kw-only — plan pseudocode at `phase-f-worker.md:663-667` OMITS this; identified as the highest-leverage implementer trap (would TypeError on first register call)
- `_handle_timeout_wake` is a NEW helper introduced by Task 16 plan (delegation pattern for 4 timeout sub-branches)
- `update_parked_request`: zero callsites in production code at HEAD; Task 16 lands first 8 (1 SET + 7 CLEAR)
- `completion_origin="worker_completed"`: zero callsites at HEAD; Task 16 lands first 4 literal occurrences (3 inline + 1 in helper)
- A3 in carry-forward.md is still listed Open at line 18, but Task 14 closeout `65f270ab` (per its own carry-forward.md entry at line 142) already added `cast(EscalatableRequestKind, request.kind)` at `:985` — A3 was missed in Task 14 closeout-docs
- **Critical scope discovery:** cancel-capable-success path returns None from handler → turn proceeds → `_finalize_turn` runs. But `_finalize_turn` STILL has pre-Packet-1 logic (projects from `captured_request.kind` without the Captured-Request Terminal Guard). At Task 16 commit time, this path will misclassify canceled jobs. Phase H Task 19 owns the guard rewrite.
- **Mode B test analysis:** Mode B tests use synchronous `controller.start(...)` returning `DelegationEscalation`. Under Task 16's new handler, `start()` will block on `registry.wait(...)` forever (no decide() caller in test scope). Conclusion: BOTH Mode A AND Mode B remain skipped at Task 16; both unblock at Task 17.

**Stage 5 — User two-read /copy submission (mid-orientation).** User pasted independent /copy-output orientation pass with VERDICT, draft authority order, draft live anchors, draft locks (L1-L10), draft watchpoints (W1-W8), branch matrix (8 rows), and acceptance criteria. User's read independently identified the SAME L9 stop-rule from a different angle (their L9: "If decide-success and timeout-cancel-success are in Task 16 acceptance, the minimal R14 finalizer guard must land in Task 16 too"). Two-read convergence achieved on the most critical scope issue.

**Stage 6 — Refinement exchange (controller → user).** Surfaced 3 refinements:
- **R1 (Mode B unblock timing):** User said "Mode B is the natural unblock candidate because parked_request_id wiring lands here." My analysis disagreed mechanically — synchronous test shape under new handler causes deadlock. Proposed correction: BOTH Mode A AND Mode B remain skipped at Task 16; both unblock at Task 17.
- **R2 (A3 audit catch):** A3 should already be Closed (Task 14 closeout `65f270ab` added the cast). Audit at L11 should verify with live-repo evidence (grep), not memory.
- **R3 (option (c) for L9):** Added a third option to user's two — "land all Task 16 code at full scope, defer the 2 finalizer-routed integration tests with `Phase H Task 19` skip citations." This preserves Phase F/H boundary AND keeps W7 invariant `0 → 6 sentinel raises` clean.

**Stage 7 — User adjudication.** User adjudicated **(b), with one tightening**:
> Keep the Phase F/H boundary intact. Task 16 should land the handler, helper structure, registry-kind narrowing, `update_parked_request` writes, `completion_origin="worker_completed"` writes, and all six sentinel raise sites. The two finalizer-routed rows should be represented as explicit skipped tests with Task 19 citations, not silently omitted and not forced through a premature `_finalize_turn` pull-forward.

The tightening: lock as "All 6 sentinel raise branches are Task 16-testable; the 2 non-sentinel finalizer-routed rows are skipped until Task 19" — categorizes deferred tests as finalizer-coverage gaps (NOT sentinel-coverage gaps), keeping W7 invariant categorically clean. User confirmed R1 and R2.

**Stage 8 — Convergence map drafting.** Wrote `task-16-convergence-map.md` (264 lines). Sections: Authority order (5 sources) → Live anchors (28-row table grep-verified at HEAD `475d0506`) → Locks L1-L11 (option (b) at L9; A3 audit at L11) → Watchpoints W1-W13 (W6 corrected per R1 — both Mode A AND Mode B stay skipped) → 8-row Branch matrix (rows 1-2 finalizer-routed; rows 3-8 sentinel-bypass) → Per-test triage (9 plan integration tests: 7 written + 2 skipped with Task 19 citations; 5 helper unit tests suggested; 8 Task 14 skips kept) → Out of scope (12 items with plan-line citations) → Acceptance criteria (Code + Tests + Closeout-docs) → Pre-dispatch checklist (12 items) → Commit shape (1+1+1 anticipated) → Carry-forward expectations (17 → 14 open).

**Stage 9 — User instruction at save trigger.** Context at 89% (178k/200k tokens). User explicit guidance:
> Save the handoff now. Do **not** push into dispatch-packet construction at 89% context. Task 16 is large enough that the dispatch packet itself needs fresh-session attention, and this is a clean boundary.

User specified next-session anchors verbatim, plus explicit non-action: "I would not draft the per-test harness scaffold now. Let the fresh implementer session derive it from the map plus `_build_controller`; otherwise we risk creating a half-context artifact that looks authoritative but was written under context pressure."

## Decisions

### D1: Draft Task 16 convergence map in this session despite 89% context

**Choice:** Complete the convergence-map draft in this resumed session rather than deferring to a fresh session.

**Driver:** User explicit directive: "Continue with the read-only Task 16 orientation and convergence-map drafting pass." Then after the two-read exchange + adjudication, user said "Draft `task-16-convergence-map.md` with option **(b)**" — the drafting was the explicit ask, not a Claude-initiated stretch.

**Alternatives considered:**
- **Defer convergence-map drafting to fresh session.** Rejected — user explicitly asked for it this session; the two-read protocol momentum (controller + user reads converged in this session) would be lost.
- **Draft a shorter "outline" convergence map and defer the full version.** Rejected — half-context artifacts are exactly what the user later warned against ("half-context artifact that looks authoritative but was written under context pressure"); a full 264-line map is more durable than a stub.

**Implications:** Convergence map exists as durable working artifact. Fresh session can load and reference without re-deriving. Pattern aligns with Task 15 D4 (convergence map as durable working doc, committed alongside closeout-docs).

**Trade-offs accepted:** Context budget consumed (89% at save trigger). Limited remaining capacity for any additional work this session — confirmed by user's "do not push into dispatch-packet construction" directive.

**Confidence:** High (E2) — drafting was the user's explicit ask, and the convergence-map structure was validated by two-read agreement.

**Reversibility:** N/A — file written.

**Change trigger:** None.

### D2: Option (b) for L9 stop-rule — Task 16 lands all code; 2 finalizer-routed integration tests skip with Task 19 citations

**Choice:** Task 16 lands the FULL handler rewrite + all 3 helpers + registry init + module constant + 8 `update_parked_request` callsites + 4 `completion_origin="worker_completed"` writes + 6 sentinel raise sites at full scope. The 2 finalizer-routed integration tests (`test_happy_path_decide_approve_success`, `test_timeout_cancel_dispatch_succeeded_for_file_change`) are SKIPPED with explicit `Phase H Task 19: requires Captured-Request Terminal Guard rewrite of _finalize_turn` citations.

**Driver:** User adjudication (verbatim): "**(b), with one tightening.** Keep the Phase F/H boundary intact ... The two finalizer-routed rows should be represented as explicit skipped tests with Task 19 citations, not silently omitted and not forced through a premature `_finalize_turn` pull-forward."

**Alternatives considered:**
- **Option (a) — pull minimal Task 19 finalizer guard forward into Task 16.** Rejected. Conflates Phase F and Phase H scope; Phase H Task 19 was specifically designed as the finalizer guard slice; pulling forward weakens the per-task scope discipline that has worked since Task 13. User explicitly rejected: "not forced through a premature `_finalize_turn` pull-forward."
- **Option (c) — defer Task 16 entirely until Task 19 lands first.** Rejected. Re-sequences plan phases; breaks "Phase F → Phase G → Phase H" ordering documented across `phase-f-worker.md`, `phase-g-public-api.md`, `phase-h-finalizer-consumers-contracts.md`. User explicitly preferred preserving the boundary.

**Implications:** W7 invariant `0 → 6 sentinel raises` stays categorically clean (the 2 deferred tests are FINALIZER-coverage gaps, NOT sentinel-coverage gaps — distinct categories). When Task 19 lands the guard, those 2 tests un-skip in the SAME commit as the rewrite. Task 16's commit chain is `feat + closeout-fix + closeout-docs` per Task 13/14/15 cadence. Carry-forward gains a new entry F16.1 (cross-phase test-coverage handoff to Task 19).

**Trade-offs accepted:** Task 16 commit looks "incomplete" without the 2 happy-path E2E tests, BUT the 6 sentinel-bypass branches are fully tested. Better to ship clean partial than mixed-scope full. Compensated by F16.1 carry-forward documenting the deferred test contract.

**Confidence:** High (E3) — user adjudication + my own option-(c) recommendation + user's explicit tightening converged. Branch matrix validates option (b) cleanly (rows 1-2 finalizer-routed; rows 3-8 sentinel-bypass).

**Reversibility:** Medium — could pull in Task 19 guard later if pain emerges. Per-task discipline is harder to reverse than per-task scope.

**Change trigger:** If Task 19 timing slips significantly (e.g., 3+ tasks past where it's planned), reconsider pulling the guard forward into a Phase F/G interim task.

### D3: W6 correction — both Mode A AND Mode B skip-decorators stay skipped at Task 16

**Choice:** All 8 Task 14 skip-decorators (6 Mode A + 2 Mode B) remain skipped at Task 16. Both unblock at Task 17.

**Driver:** Mechanical analysis of test bodies: Mode B tests use `controller.start(repo_root=...)` → `assert isinstance(start_result, DelegationEscalation)`. Under Task 16's new handler, `start()` calls `_execute_live_turn()` → `run_execution_turn()` → new `_server_request_handler()` → blocks on `registry.wait(parsed.request_id)` forever (no decide() caller in synchronous test scope). Test would deadlock.

User confirmation (verbatim): "I agree with R1. Both Mode A and Mode B should remain skipped at Task 16. Mode B's *data dependency* lands in Task 16, but its *test execution shape* needs Task 17's worker spawn / `wait_for_parked` split."

**Alternatives considered:**
- **Unskip Mode B at Task 16** (per prior handoff's expectation). Rejected on mechanical grounds — synchronous-deadlock under new handler.
- **Refactor Mode B tests to use threading harness in-scope at Task 16.** Rejected — substantial refactoring outside Task 16's scope; pattern-matches against the W2 directive "no fictional fixtures, use module-local helpers."

**Implications:** Convergence map's W6 reflects the corrected understanding. Carry-forward.md entry for Mode B tests will note "data dependency closed at Task 16; test-execution-shape unblock at Task 17." Both Mode A and Mode B fall out of skip in Task 17's same commit.

**Trade-offs accepted:** Mode B's data dependency is satisfied at Task 16 but unobservable until Task 17. Documented in F16.1-adjacent carry-forward note.

**Confidence:** High (E2) — verified by reading both Mode B test bodies (`test_delegation_controller.py:2598+` and `test_delegate_start_integration.py:802+`); user confirmed R1 verbatim.

**Reversibility:** N/A — convergence-map text.

**Change trigger:** None.

### D4: L11 — Task 16 closeout-docs MUST audit A3 with live-repo verification

**Choice:** Closeout-docs commit MUST run `grep -n "cast(EscalatableRequestKind" packages/plugins/codex-collaboration/server/delegation_controller.py` BEFORE moving A3 from Open → Closed. Memory-based moves are forbidden.

**Driver:** A3 audit catch — A3 should already be Closed (Task 14 closeout `65f270ab` added the cast at `:985`, per `carry-forward.md:142`). User confirmation (verbatim): "I also agree with R2. Add **L11**: Task 16 closeout-docs must audit A3 and move it to Closed with the Task 14 commit reference, if live repo evidence confirms `cast(EscalatableRequestKind, request.kind)` already landed."

**Alternatives considered:**
- **Move A3 to Closed without verification.** Rejected — this is exactly the failure mode that left A3 Open in the first place (Task 14 closeout missed the move based on memory).
- **Defer A3 audit to a separate carry-forward sweep.** Rejected — Task 16 is touching `_project_request_to_view`'s neighborhood (it's at `:991` post-Task-15, and the Task 15-introduced sentinel catch is its caller via `_load_or_materialize_inspection`). Natural audit point.

**Implications:** Pattern locks: ANY future closeout-docs that moves carry-forward items to Closed MUST verify with live-repo evidence (grep, file check, etc.). Generalizes beyond A3 to all carry-forward state moves.

**Trade-offs accepted:** Slightly more verbose closeout-docs commit (extra grep step). Pays back as ledger accuracy across remaining 14 open items.

**Confidence:** High (E2) — both my read (A3 should be Closed) and user agreement (R2) converged.

**Reversibility:** N/A — convergence-map text.

**Change trigger:** None.

### D5: Defer Task 16 dispatch-packet construction to fresh session

**Choice:** Stop after convergence-map drafting + handoff save. Do NOT construct the dispatch packet (full implementer prompt) in this session.

**Driver:** Context at 89% (178k/200k) at save trigger. User explicit directive: "Save the handoff now. Do **not** push into dispatch-packet construction at 89% context. Task 16 is large enough that the dispatch packet itself needs fresh-session attention, and this is a clean boundary."

**Alternatives considered:**
- **Construct dispatch packet now.** Rejected per user explicit directive. Also matches Task 15 D2 precedent (deferred to fresh session at 90% context).
- **Construct an outline-only dispatch packet.** Rejected for the same "half-context artifact" risk user later explicitly warned against.

**Implications:** Fresh session loads this handoff via `/handoff:load`, reads `task-16-convergence-map.md` (which now exists as durable artifact), constructs the dispatch packet, then dispatches via `superpowers:subagent-driven-development`. Pattern: convergence-map drafting and dispatch-packet construction are SEPARATE sessions for Task 16-class tasks.

**Trade-offs accepted:** One extra session boundary in the Task 16 lifecycle. Pays back as dispatch-packet quality (full context budget for prompt construction).

**Confidence:** High (E3) — user explicit directive + Task 15 D2 precedent + obvious context arithmetic.

**Reversibility:** N/A.

**Change trigger:** None.

### D6: Do NOT draft per-test harness scaffold in this session

**Choice:** Convergence map describes the per-test triage but does NOT include a draft scaffold for `_TestRegistryHarness` or similar shared test fixture. Implementer derives from convergence map + `_build_controller` import (per Task 14 W4 / Task 15 L8 precedent).

**Driver:** User explicit guidance: "I would not draft the per-test harness scaffold now. Let the fresh implementer session derive it from the map plus `_build_controller`; otherwise we risk creating a half-context artifact that looks authoritative but was written under context pressure."

**Alternatives considered:**
- **Draft scaffold inline in convergence map.** Rejected per user directive. Would compound context pressure.
- **Draft scaffold in a separate working file.** Rejected for same reason.

**Implications:** Implementer has more freedom in test design; fresh session can produce a scaffold that fits the current code shape. Pattern: convergence maps describe per-test triage (what to write, what to skip) but NOT test scaffolding (how the helpers are structured).

**Trade-offs accepted:** Implementer must derive harness from primitives; small risk of harness drift between Task 16 tests. Mitigated by `_build_controller` precedent locking the construction pattern.

**Confidence:** High (E2) — user explicit directive + Task 15 precedent of letting implementer derive structure within the convergence map's lock-bounds.

**Reversibility:** N/A.

**Change trigger:** None.

## Changes

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md` (NEW, 264 lines, untracked)

**Purpose:** Binding dispatch authority for Phase F Task 16. Drafted via two-read protocol (controller's read + user's `/copy`-output independent read converged). Encodes scope adjudication (option (b)) + lock structure (L1-L11) + watchpoint structure (W1-W13) + 8-row branch matrix + per-test triage (9 plan + 5 helper + 8 keep-skipped) + acceptance criteria split (Code + Tests + Closeout-docs) + carry-forward expectations.

**Approach:** Section structure mirrors Task 15's convergence map (Authority order → Live anchors → Locks → Watchpoints → Per-test triage → Out of scope → Acceptance → Pre-dispatch checklist → Commit shape → Carry-forward). New for Task 16: 8-row Branch matrix between Watchpoints and Per-test triage, making the L9 stop-rule observable in code (rows 1-2 finalizer-routed; rows 3-8 sentinel-bypass).

**Key implementation details:**
- Live anchors table is 28 rows; every Task-16-relevant symbol grep-verified at HEAD `475d0506`. Plan-cited line numbers (`phase-f-worker.md:561` cites `_server_request_handler` at `:650-720`) are stale; live anchors override.
- L4 prominently locks `kind=cast(EscalatableRequestKind, parsed.kind)` at `register()` callsite — plan pseudocode at `phase-f-worker.md:663-667` OMITS the kw arg; live API requires it.
- L9 stop-rule formalized with option (b) adjudication inline: "Task 16 lands the handler code at full scope (all 6 sentinel raises + 2 finalizer-routed return paths), but the 2 finalizer-routed integration tests are SKIPPED with `Phase H Task 19: requires Captured-Request Terminal Guard rewrite of _finalize_turn` citations."
- L11 audit step requires live-repo grep verification: `grep -n "cast(EscalatableRequestKind" packages/plugins/codex-collaboration/server/delegation_controller.py`.
- W6 reflects both-Mode-A-AND-Mode-B-stay-skipped correction.
- Per-test triage table includes verbatim `@pytest.mark.skip(reason="...")` citation strings for the 2 deferred tests.
- F16.1 added as new carry-forward entry shape (cross-phase test-coverage handoff with same-commit unskip contract at Task 19).

**Future-Claude:** This file is the dispatch authority. Embed verbatim (or read inline) into the dispatch packet. Convergence map will be committed alongside Task 16's closeout-docs (per Task 15 D4 precedent — durable working artifact, not session ephemera).

## Codebase Knowledge

### Live anchors verified at HEAD `475d0506` (Task-16-relevant subset)

| Symbol | File:line |
|--------|-----------|
| `_WorkerTerminalBranchSignal` def | `delegation_controller.py:201-223` (Task 15, unchanged) |
| `DelegationStartError` def | `delegation_controller.py:153-185` |
| `UnknownKindInEscalationProjection` def | `delegation_controller.py:188` |
| `_execute_live_turn` def | `delegation_controller.py:741` |
| **`_server_request_handler` def** (REWRITE TARGET) | `delegation_controller.py:765-835` (plan stale at `:650-720`) |
| Local `_CANCEL_CAPABLE_KINDS` (handler scope) | `delegation_controller.py:757` |
| Local `_KNOWN_DENIAL_KINDS` (handler scope) | `delegation_controller.py:758` |
| First try/except (Task 15 sentinel catch) | `delegation_controller.py:837-879` |
| Second try/except (around `_finalize_turn`) | `delegation_controller.py:881-899` (Task 19 territory; W-locked) |
| `_mark_execution_unknown_and_cleanup` def | `delegation_controller.py:901` |
| `_finalize_turn` def | `delegation_controller.py:1611` (Task 19 territory) |
| `_finalize_turn` local `_CANCEL_CAPABLE_KINDS` | `delegation_controller.py:1628` (separate from handler's; W10) |
| Module-level `logger` | `delegation_controller.py:104` |
| `cast` import | `delegation_controller.py:64` |
| `EscalatableRequestKind` import | `delegation_controller.py:90` |
| `ResolutionRegistry.register` signature | `resolution_registry.py:173-180` (kw-only `kind: EscalatableRequestKind` REQUIRED) |
| `ResolutionRegistry.wait` | `resolution_registry.py:261` |
| `ResolutionRegistry.discard` | `resolution_registry.py:283` |
| `ResolutionRegistry.announce_parked` | `resolution_registry.py:310` |
| `DelegationJobStore.update_parked_request` | `delegation_job_store.py:187` (zero callsites in production today) |
| `OperationJournalEntry.completion_origin` Literal | `models.py:368` (zero `worker_completed` callsites today) |

### Architecture: Phase F worker-thread model post-Task-15

| Component | File | Status post-Task-15 | Status post-Task-16 |
|---|---|---|---|
| `_WorkerTerminalBranchSignal` (sentinel exception) | `delegation_controller.py:201-223` | Defined | Unchanged |
| `_WorkerRunner` class | `worker_runner.py` | NEW (Task 15 scaffold) | Unchanged at Task 16 |
| Sentinel catch in `_execute_live_turn` | `delegation_controller.py:845` | NEW (Task 15) | Unchanged at Task 16 |
| 6 sentinel raise sites in handler body | `delegation_controller.py:_server_request_handler` + `_handle_timeout_wake` | None | **NEW (Task 16)** — 6 raises |
| `self._registry: ResolutionRegistry` | `delegation_controller.py:DelegationController.__init__` | Pending | **NEW (Task 16 step 16.4)** |
| `_APPROVAL_OPERATOR_WINDOW_SECONDS` constant | `delegation_controller.py` (module-level) | Pending | **NEW (Task 16 step 16.4)** |
| `update_parked_request(...)` callsites | various handler branches | Zero | **8 total: 1 SET + 7 CLEAR (Task 16)** |
| `completion_origin="worker_completed"` writes | various worker-side persistence calls | Zero | **4 literal occurrences (Task 16; closes C10.4)** |
| `_handle_timeout_wake` helper method | `delegation_controller.py` | None | **NEW (Task 16)** |
| `_write_completion_and_audit_timeout` helper method | `delegation_controller.py` | None | **NEW (Task 16)** |
| `_repo_root_for_journal(job_id)` helper | `delegation_controller.py` | Inline | **NEW one-liner (Task 16)** |
| `start()` spawns worker via `spawn_worker(...)` | `delegation_controller.py:start` | Pending | Pending — Task 17 (Phase G) |
| `wait_for_parked` blocking call from main thread in `start()` | `delegation_controller.py:start` | Pending | Pending — Task 17 (Phase G) |
| `_finalize_turn` Captured-Request Terminal Guard | `delegation_controller.py:_finalize_turn` | Pending | Pending — Task 19 (Phase H) |

### Branch matrix (8 rows; spec §549-557 cross-reference)

| # | Branch | Mutator | Job result | Through finalizer? | Sentinel? |
|---|--------|---------|------------|--------------------|-----------|
| 1 | decide-success | `record_response_dispatch` + `mark_resolved` | varies via finalizer | YES | none |
| 2 | timeout cancel-success | `record_timeout(... dispatch_result="succeeded")` | `canceled` via finalizer | YES | none |
| 3 | dispatch-failed | `record_dispatch_failure(...)` | `unknown` | NO | `dispatch_failed` |
| 4 | timeout cancel-dispatch-failed | `record_timeout(... dispatch_result="failed")` | `unknown` | NO | `timeout_cancel_dispatch_failed` |
| 5 | timeout interrupt-succeeded | `record_timeout(... interrupt_error=None)` | `canceled` | NO | `timeout_interrupt_succeeded` |
| 6 | timeout interrupt-failed | `record_timeout(... interrupt_error=<sanitized>)` | `unknown` | NO | `timeout_interrupt_failed` |
| 7 | internal-abort | `record_internal_abort(reason=)` | `unknown` | NO | `internal_abort` |
| 8 | unknown-kind interrupt-failure | minimal `PendingServerRequest(kind="unknown")` | n/a — `DelegationStartError` | NO | `unknown_kind_interrupt_transport_failure` |

Rows 1-2: finalizer-routed (no sentinel). **Integration tests SKIPPED at Task 16 with Task 19 citations.**
Rows 3-8: sentinel-bypass. **Integration tests written at Task 16.**

### Files explored this session (no need to re-read)

| File | Purpose | Key findings |
|------|---------|--------------|
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md` | Template structure | 8 locks + 11 watchpoints + 5-test triage; section structure mirrored for Task 16 |
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md:377-1189` | Task 16 plan body | Steps 16.1-16.7; pseudocode for handler + helpers; 9 placeholder integration tests |
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` | Packet 1 ledger | 17 open items; A3 incorrectly still Open; Task 14 closeout entry confirms `cast` was added |
| `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md:450-558` | Spec sentinel section | 6 reasons + invariant table at §549-557; pre-capture vs post-decide/post-Parked distinction |
| `packages/plugins/codex-collaboration/server/delegation_controller.py:740-908` | `_execute_live_turn` + `_server_request_handler` body | Current handler at `:765-835` to be wholesale rewritten |
| `packages/plugins/codex-collaboration/server/resolution_registry.py:160-260` | Registry API | `register` requires kw-only `kind: EscalatableRequestKind` (L4 trap) |
| `packages/plugins/codex-collaboration/tests/test_delegation_controller.py:2598+` | Mode B test 1 | Synchronous `start()` shape — would deadlock under new handler (R1) |
| `packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py:802+` | Mode B test 2 | Same shape; same conclusion |
| `packages/plugins/codex-collaboration/tests/test_delegation_controller.py:1360, 1418, 1737, 2372` | Mode A skip-decorators | All cite Task 17 unblock (unknown-kind handling at L6 callsite) |
| `packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py:617, 1062` | Mode A skip-decorators | Same Task 17 citation |

## Context

### Project state

T-20260423-02 Packet 1 progress (post-Task-15, pre-Task-16):

| Phase | Tasks | Status |
|-------|-------|--------|
| A (types) | 1-5 | Complete |
| B (stores) | 6-9 | Complete (with closeout) |
| C (journal) | 10 | Complete (with closeout) |
| D (registry) | 11-12 | Complete (with closeouts) |
| E (serialization/projection) | 13-14 | Complete (with closeouts) |
| **F (worker)** | **15-16** | **15 COMPLETE — Task 16 convergence map drafted, dispatch deferred to fresh session** |
| G (public API) | 17-18 | Not started |
| H (finalizer/consumers/contracts) | 19+ | Not started |

17 open carry-forward items at end of this session (unchanged from Task 15 closeout — convergence-map drafting doesn't change carry-forward state). Anticipated 17 → 14 at Task 16 close (A2 closes by L8, C10.4 closes by L7, A3 audits/closes by L11; F16.1 added as cross-phase test-coverage handoff to Task 19).

### Branch state

Branch: `feature/delegate-deferred-approval-response`. Clean tree at `475d0506`. One untracked file:
- `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md` (264 lines; will be committed alongside Task 16 closeout-docs per Task 15 D4 precedent)

### Mental model

**Phase F = worker-side machinery, two slices:**
- Task 15 (DONE): scaffold — `worker_runner.py` + sentinel catch + canceled-tuple expansion. Purely additive, dead code under own scope.
- Task 16 (NEXT): handler rewrite — async-decide model + 6 sentinel raise sites + 3 helpers + registry init + 8 `update_parked_request` callsites + 4 `completion_origin="worker_completed"` writes.

**The L9 stop-rule is the central tension of Task 16.** Two of the 8 branches (decide-success + timeout-cancel-success) return None from the handler → turn continues → `_finalize_turn` runs. But `_finalize_turn` rewrite (Captured-Request Terminal Guard) is owned by Phase H Task 19. Option (b) resolution: Task 16 lands the handler code at full scope; the 2 finalizer-routed integration tests are SKIPPED with explicit Task 19 citations. W7 invariant `0 → 6 sentinel raises` stays categorically clean.

**The L4 trap is the highest-leverage implementer mistake to prevent.** Plan pseudocode at `phase-f-worker.md:663-667` calls `registry.register(parsed.request_id, job_id=job_id, timeout_seconds=...)` — but live API at `resolution_registry.py:173-180` requires `kind: EscalatableRequestKind` as kw-only. A fresh implementer reading the plan verbatim would skip the kw arg and hit a runtime TypeError on first register call. Convergence map locks this as L4 with explicit live-API citation + suggested fix `kind=cast(EscalatableRequestKind, parsed.kind)`.

### Environment

- Python 3.12, uv workspace, pytest test runner
- Run package suite: `uv run --package codex-collaboration pytest`
- Run lint: `uv run --package codex-collaboration ruff check packages/plugins/codex-collaboration/server/ packages/plugins/codex-collaboration/tests/`
- Branch protection hook: edits allowed on `feature/*`; blocked on `main`/`master`
- Current branch is `feature/delegate-deferred-approval-response` — edits allowed throughout

### Two-read protocol observed (third successive instance)

Tasks 13/14/15/16 all benefited from the user's two-read protocol. This session's instance:
- Controller's read identified: L4 (`kind=` argument trap), L9 (cancel-success `_finalize_turn` dependency, framed as my Insight), R1 (Mode B unblock-timing correction), R2 (A3 audit catch).
- User's `/copy` independent read identified: L9 (formalized as stop-rule, with the tightening framing about W7-invariant cleanliness), L10 (unknown-kind interrupt-success stays `TurnTerminalWithoutEscalation`, NOT a sentinel branch), 8-row branch matrix structure, L11 audit step shape (`if live repo evidence confirms`).

Convergence achieved at the L9 question; refinement R1 + R2 + R3 (option (c)) merged into option (b) per user adjudication.

## Learnings

### L1: Two-read protocol surfaces structural traps from independent angles — third successive instance of the value

**Mechanism:** Controller's read tends to surface mechanical/lower-level traps (line numbers, API signature mismatches, fictional fixture names). User's `/copy`-output independent read tends to surface structural/higher-level traps (phase-boundary tensions, formal stop-rules, durable artifact patterns). Both are valuable; neither alone catches the full set.

**Evidence:** Task 16 session: my read flagged L4 (kind= trap, mechanical) and the cancel-success/`_finalize_turn` dependency (Insight, structural-but-incomplete framing). User's read flagged L9 (formalized stop-rule), L10 (TurnTerminalWithoutEscalation distinction), branch matrix (8-row central artifact), L11 audit shape.

**Implication:** For Task 16-class tasks (large, multi-helper, multi-branch), the two-read protocol is load-bearing — single-read drafts would miss either the mechanical OR the structural traps. Pattern continues across Task 13/14/15/16. Future-Claude: ALWAYS solicit user `/copy` independent read before drafting convergence maps for tasks ≥3 helpers or ≥6 distinct exit paths.

**Watch for:** User `/copy` submissions mid-orientation — these are VALIDATED INDEPENDENT EVIDENCE, not just suggestions. Treat as a parallel orientation that converges with the controller's read at the dispatch boundary.

### L2: Branch matrix is the right central artifact for Task 16-class tasks

**Mechanism:** When a task has N exit paths with M distinct contracts (M < N because some paths share contracts), encoding them as a matrix table makes the contract structure observable in a way that prose cannot. Specifically: the L9 stop-rule (cancel-success / decide-success rely on `_finalize_turn` rewrite) becomes a CATEGORY DISTINCTION in the matrix (rows 1-2 vs rows 3-8) that any reviewer can spot.

**Evidence:** Without the matrix, the L9 issue would have been buried in prose under L9's lock entry. With the matrix as a top-level section, the 2 finalizer-routed rows are visually distinct from the 6 sentinel-bypass rows, and the per-test triage can reference rows by number ("row 1 → skip", "row 5 → write").

**Implication:** For any future task with ≥6 distinct exit paths, draft a branch matrix as a top-level convergence-map section. Use the matrix to identify which exit paths share contracts (collapse rows where possible) and which split (separate rows). Then the per-test triage table maps tests to row numbers, making coverage gaps observable.

**Watch for:** Tasks with implicit categorical distinctions in their exit paths (sentinel-bypass vs finalizer-routed; cleanup-required vs cleanup-not-required; etc.). The matrix's COLUMNS encode the distinctions; the ROWS encode the exit paths.

### L3: F16.1 is a structurally new carry-forward shape — cross-phase test-coverage handoff

**Mechanism:** Prior carry-forward items have been minor cleanups (line counts, docstrings, test parity). F16.1 is different — it documents 2 specific tests deferred to a known phase boundary (Task 19) with a same-commit unskip contract. The Task 19 implementer MUST recognize the handoff and unskip in the same commit as the `_finalize_turn` rewrite.

**Evidence:** The 2 tests (`test_happy_path_decide_approve_success`, `test_timeout_cancel_dispatch_succeeded_for_file_change`) are NOT skipped because of test infrastructure problems or unrelated dependencies; they're skipped because Task 19's `_finalize_turn` rewrite is the SOLE missing piece for them to pass. Once Task 19 lands, they pass by definition.

**Implication:** Future tasks that adjudicate option-(b)-style scope partitions should add F-task-N.x carry-forward entries explicitly documenting same-commit unskip contracts. Task 19's convergence map MUST include F16.1 in scope, otherwise tests stay skipped indefinitely. Future-Claude drafting Task 19's convergence map: search carry-forward.md for `F16.1` and include it as an L-locked closeout requirement.

**Watch for:** Skipped tests with Task-N citations in their skip reason. These represent latent same-commit unskip contracts. Future task convergence maps should grep for their own task ID in carry-forward.md and pre-empt orphaning.

### L4: Closeout-docs MUST audit carry-forward state moves with live-repo evidence (L11 generalization)

**Mechanism:** Memory-based moves (e.g., "Task 14 closeout said it added `cast`, so A3 is closed") are unreliable across multi-task chains. Live-repo verification (grep, file check) is cheap and catches both genuine misses (A3 case: cast was added but ledger move was missed) AND inadvertent regressions (cast added then later removed by a tangential commit).

**Evidence:** A3 was supposed to be Closed during Task 14 closeout (`65f270ab` added the cast at `:985`), but the carry-forward.md move was missed. Discovered during Task 16 orientation by grep-verifying live state vs ledger.

**Implication:** Pattern locks: ANY closeout-docs that moves a carry-forward item to Closed MUST include a verification step (grep / file check) BEFORE the move. Convergence maps should include the verification step as an explicit lock (L11-style). Generalizes beyond carry-forward to ANY ledger-state-vs-codebase-state synchronization.

**Watch for:** Future closeout-docs commits that move carry-forward items to Closed. Always verify with command, never with memory.

## Next Steps

### 1. Fresh-session dispatch packet construction

**Dependencies:** Convergence map drafted ✅. This handoff exists. Fresh session has full context budget.

**What to read first** (in order):
1. This handoff (loaded automatically via `/handoff:load`)
2. `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md` (binding dispatch authority)
3. `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md:377-1189` (Task 16 plan body — embed in dispatch packet)
4. `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md:450-558` (spec sentinel section — embed in dispatch packet)

**Approach:**
- Construct dispatch packet by embedding convergence map verbatim + spec sentinel section + plan Step 16.1-16.7 + branch matrix + per-test triage + acceptance criteria + reporting contract.
- Name the implementer agent explicitly: `Agent({name: "task-16-implementer", subagent_type: "general-purpose", model: "sonnet", ...})` per Task 15 R3.
- Workflow: `superpowers:subagent-driven-development` — single fresh implementer + spec reviewer + code-quality reviewer (sequential).
- Anticipated 1+1+1 commit chain (feat + closeout-fix + closeout-docs).

**Acceptance criteria:** see convergence map's Acceptance section. Highlights:
- W7 invariant: `grep -nF "_WorkerTerminalBranchSignal(reason=" delegation_controller.py | wc -l` returns `6`
- L6 invariant: `grep -n "update_parked_request" delegation_controller.py | wc -l` returns `≥8` (excluding docstring at `:208`)
- L7 invariant: `grep -nF 'completion_origin="worker_completed"' delegation_controller.py | wc -l` returns `4`
- 8 Task 14 skip-decorators stay skipped
- 2 finalizer-routed integration tests have explicit `Phase H Task 19: requires Captured-Request Terminal Guard rewrite of _finalize_turn` citations
- L11 audit: `cast(EscalatableRequestKind, request.kind)` confirmed in `_project_request_to_view`; A3 moved to Closed

**Potential obstacles:** Task 16 is the LARGEST task in the plan (~280 lines handler + ~140 lines helpers + ~200 lines tests = ~620 lines of new code). Implementer agent context budget should be high. If the implementer needs intermediate `BLOCKED` checkpoints, controller adjudicates per-question.

### 2. (Subsequent) Phase F closeout

**Dependencies:** Task 16 complete + closeouts.

**Scope:** No additional Phase F tasks (Task 16 is Phase F's final task per `phase-f-worker.md:1186` — "Phase F complete. The worker runs on its own thread and terminalizes through all 6 sentinel branches."). Phase G starts next.

### 3. (Subsequent) Phase G Task 17 dispatch

**Dependencies:** Task 16 complete.

**Scope:** Worker spawn from `start()`, `wait_for_parked` blocking call from main thread. Closes 6 Mode A unblock tests + 2 Mode B unblock tests (per W6 correction).

## In Progress

Clean stopping point — convergence map drafted at `task-16-convergence-map.md` (264 lines, untracked, will be committed alongside Task 16 closeout-docs). No implementation started. No test changes. No `delegation_controller.py` edits.

The pending work (Task 16 dispatch packet construction + dispatch + implementation) requires a fresh session per D5. This handoff is the entry point.

## Open Questions

None blocking. One open question for fresh session, NOT blocking dispatch:

**Should the per-test harness scaffold be drafted as part of dispatch packet, or left for implementer to derive?**
- **Resolved per D6:** NOT draft scaffold; let implementer derive from `_build_controller(tmp_path)` import (per Task 14 W4 / Task 15 L8 precedent). User explicit guidance: "Let the fresh implementer session derive it from the map plus `_build_controller`; otherwise we risk creating a half-context artifact that looks authoritative but was written under context pressure."

## Risks

### R1: Task 16 plan-line drift will be larger than Task 15's

**Concern:** Plan body at `phase-f-worker.md:377-1189` cites line numbers throughout `_server_request_handler` body which is INSIDE `_execute_live_turn`. Task 15 added ~+27 lines post-`_execute_live_turn`. Tasks 6-14 added more drift. Plan citation `:561` ("Edit `_server_request_handler` at `delegation_controller.py:650-720`") is the most prominent stale reference, but ALL plan-cited line numbers throughout the Task 16 body are stale.

**Mitigation:** Convergence map's Live anchors table (28 rows) is grep-verified at HEAD `475d0506` and overrides plan citations. W13 explicitly directs implementer to use live anchors over plan line numbers. Convergence map is the dispatch authority; plan is reference.

**Severity:** Low — drift is mechanical; convergence map captures it.

### R2: L4 trap (`kind=` argument omission) is highest-leverage implementer mistake

**Concern:** Plan pseudocode at `:663-667` calls `registry.register(parsed.request_id, job_id=job_id, timeout_seconds=...)`. Live API at `resolution_registry.py:173-180` requires `kind: EscalatableRequestKind` as kw-only. A fresh implementer reading the plan verbatim would skip the kw arg → runtime TypeError on first register call → BLOCKED.

**Mitigation:** Convergence map locks L4 prominently with explicit live-API citation + suggested fix `kind=cast(EscalatableRequestKind, parsed.kind)`. Pre-dispatch checklist requires "L4 fix prominent in dispatch packet" as a checkbox.

**Severity:** Low if dispatch packet honors L4; high otherwise. Defense-in-depth: spec reviewer should catch on independent verification of L4.

### R3: F16.1 cross-phase handoff to Task 19 risks orphaning

**Concern:** F16.1 documents 2 tests deferred to Task 19 with same-commit unskip contract. If Task 19's implementer doesn't recognize the handoff (e.g., doesn't grep for F16.1 in carry-forward.md), the tests stay skipped indefinitely.

**Mitigation:** Convergence map's Carry-forward expectations section explicitly notes F16.1 as a NEW Open carry-forward item with "Phase H Task 19 — same-commit un-skip" landing point. Task 19's convergence map (drafted later) should grep carry-forward.md for `F16.1` and include in scope. Future-Claude drafting Task 19's map: this handoff documents the contract.

**Severity:** Low — Task 19 is later in the plan; convergence-map-drafting protocol should catch.

### R4: A3 audit at L11 may fail if `cast` was inadvertently lost

**Concern:** A3 is supposedly resolved by Task 14 closeout `65f270ab`. If a tangential commit between Task 14 and Task 16 removed the cast, L11 audit grep returns no match → A3 stays Open + flagged as Task 14 closeout regression.

**Mitigation:** Convergence map's L11 explicitly handles both cases ("if live repo evidence confirms ... move to Closed; if not found, A3 stays Open and is flagged as Task 14 closeout regression"). Closeout-docs commit captures the audit result either way.

**Severity:** Low — audit is cheap; either outcome is recorded.

### R5: Context budget at convergence-map drafting was tight (89% at save)

**Concern:** 89% is well within "save handoff" territory but close to the typical 90% rule-of-thumb. If unforeseen drafting work had been required (e.g., user requesting major restructuring), context overrun was possible.

**Mitigation:** D5 deferred dispatch-packet construction to fresh session per user explicit directive. Pattern locks: convergence-map drafting and dispatch-packet construction are SEPARATE sessions for Task 16-class tasks.

**Severity:** Low post-hoc — handoff saved successfully at 89%.

## References

- **Branch:** `feature/delegate-deferred-approval-response` @ `475d0506` (clean tree, one untracked file)
- **Untracked file (NEW):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md` (264 lines; will be committed alongside Task 16 closeout-docs)
- **Prior session handoff (resumed_from):** `docs/handoffs/archive/2026-04-25_15-42_phase-f-task-15-complete-task-16-next.md`
- **Task 15 convergence map (template):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md` (131 lines, committed `13b024ae`)
- **Phase F plan:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md` (1189 lines; Task 16 body lines 377-1189)
- **Phase G plan:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md`
- **Phase H plan (Task 19 owner):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-h-finalizer-consumers-contracts.md`
- **Manifest:** `docs/plans/2026-04-24-packet-1-deferred-approval-response.md`
- **Carry-forward tracker:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md`
- **Spec sentinel section:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md:450-558`
- **Spec finalizer path table:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md:1790+`
- **Recent commits (Task 15 chain):**
  - `94c4dab7` — feat: _WorkerRunner + sentinel catch scaffold + canceled-inspection tuple
  - `6f23b745` — fix: address Task 15 code-quality review
  - `13b024ae` — docs: record Phase F Task 15 closeout
  - `475d0506` — docs: correct stale worker_runner.py line count

## Conversation Highlights

**Initial drafting directive (binding):**
User: "Continue with the read-only Task 16 orientation and convergence-map drafting pass."

**User two-read submission (verbatim, mid-drafting):**
User: "Task 16 is **not dispatch-credible as a straight implementation packet yet**. The handler rewrite plan is mostly concrete, but there is a real sequencing conflict ... My recommendation: **Task 16 convergence map should mark this as a stop-rule dependency and pull the minimal Task 19 finalizer guard into Task 16 if Task 16 is expected to pass its own happy-path/timeout-success tests.** Otherwise Task 16 becomes a knowingly incomplete bridge commit."

**User L9 adjudication (verbatim):**
User: "**(b), with one tightening.** Keep the Phase F/H boundary intact. Task 16 should land the handler, helper structure, registry-kind narrowing, `update_parked_request` writes, `completion_origin='worker_completed'` writes, and all six sentinel raise sites. The two finalizer-routed rows should be represented as explicit skipped tests with Task 19 citations, not silently omitted and not forced through a premature `_finalize_turn` pull-forward."

**User L9 tightening (verbatim):**
User: "**All 6 sentinel raise branches are Task 16-testable** at the handler / `_execute_live_turn` boundary. **The 2 non-sentinel finalizer-routed rows are skipped** until Task 19: decide-success, timeout-cancel-dispatch-succeeded. That keeps the invariant clean: Task 16's W7 is still exactly `0 → 6` production sentinel raise sites, and every sentinel reason has coverage. The skipped rows are not sentinel coverage gaps; they are finalizer guard coverage gaps."

**User R1 confirmation (verbatim):**
User: "I agree with R1. Both Mode A and Mode B should remain skipped at Task 16. Mode B's *data dependency* lands in Task 16, but its *test execution shape* needs Task 17's worker spawn / `wait_for_parked` split. So the convergence map should say: 'Task 16 wires `parked_request_id`, but does not unskip the 8 Task 14 tests.'"

**User R2 confirmation (verbatim):**
User: "I also agree with R2. Add **L11**: Task 16 closeout-docs must audit A3 and move it to Closed with the Task 14 commit reference, if live repo evidence confirms `cast(EscalatableRequestKind, request.kind)` already landed."

**User dispatch-shape directive (verbatim):**
User: "So the dispatch shape I'd approve is: 1. Draft `task-16-convergence-map.md` with option **(b)**. 2. Include the branch matrix, split into: 6 sentinel-bypass rows: in-scope, tested. 2 finalizer-routed rows: code can land, integration assertions skipped until Task 19. 3. Add explicit skip reasons for the two finalizer-dependent tests. 4. Add a carry-forward item for Task 19 finalizer-routed integration coverage. 5. Preserve all 8 Task 14 skips until Task 17. 6. Include L11 for A3 closeout-doc audit."

**User save directive (verbatim):**
User: "Save the handoff now. Do **not** push into dispatch-packet construction at 89% context. Task 16 is large enough that the dispatch packet itself needs fresh-session attention, and this is a clean boundary: the convergence map exists, the scope adjudication is locked, and no implementation has started."

**User scaffold-deferral directive (verbatim):**
User: "I would not draft the per-test harness scaffold now. Let the fresh implementer session derive it from the map plus `_build_controller`; otherwise we risk creating a half-context artifact that looks authoritative but was written under context pressure."

**Working style observed:** User produces tight, evidence-first refinements with explicit corrections. Uses two-read protocol with `/copy` for independent orientation passes — treats them as VALIDATED INDEPENDENT EVIDENCE, not just suggestions. Pre-locks structural decisions (option (b) vs (a) vs (c)). Distinguishes data-dependency closure from test-shape unblock (R1 framing). Tolerates documented workflow deviations (D6 scaffold deferral) when justified by context pressure. Categorizes test gaps (sentinel-coverage vs finalizer-coverage) for invariant cleanliness. Treats convergence-map-as-durable-artifact pattern (D4 from Task 15) as load-bearing.

## User Preferences

(All carry-over items from Tasks 13/14/15 still apply; new this session as below.)

**Workflow:** `superpowers:subagent-driven-development` — controller does not implement; review subagents critique. Single fresh implementer + spec reviewer + code-quality reviewer per task, sequential not parallel. One implementer per task, continued via SendMessage for closeout-fix.

**Convergence-map structure:** Live-anchors table + Locks (L1-Lₙ) + Watchpoints (W1-Wₙ) + **Branch matrix (NEW for Task-16-class tasks)** + Per-test triage table + Out-of-scope table with plan-line citations + Acceptance criteria (split: Code + Tests + Closeout-docs) + Pre-dispatch checklist + Commit shape + Carry-forward expectations table.

**Stop-rule pattern (NEW):** When dependency between phases creates correctness gap, formalize as a lock (e.g., L9). Don't smudge phase boundaries by pulling forward; defer with explicit citations. Categorize test deferrals by GAP CATEGORY (sentinel-coverage vs finalizer-coverage) for invariant cleanliness.

**Cross-phase test-coverage handoff pattern (NEW):** F16.1-style. Tests deferred to a known phase boundary with same-commit unskip contract recorded in carry-forward. Future task convergence maps must grep for their own task ID in carry-forward.md to pre-empt orphaning.

**Closeout-doc audit pattern (NEW):** L11. Before moving carry-forward items to Closed, verify with live-repo evidence (grep, file check), not memory. Generalizes beyond A3 to all ledger-state-vs-codebase-state synchronization.

**Context discipline (carried, reaffirmed):** At 89% context, do NOT push into dispatch-packet construction. Save handoff, defer to fresh session. Pattern: convergence-map drafting and dispatch-packet construction are SEPARATE sessions for Task 16-class tasks.

**Scaffold caution (NEW):** At high context pressure, do NOT pre-draft scaffolds (per-test harnesses, etc.). Let fresh implementer derive from convergence map + primitives like `_build_controller`. Half-context artifacts that "look authoritative" are a risk.

**Test-execution-shape vs data-dependency distinction (NEW):** Skipped tests can have multiple unblock conditions. Mode B tests have BOTH a data dependency (`update_parked_request` wiring, lands at Task 16) AND a test-execution shape requirement (synchronous `start()` returning `DelegationEscalation`, requires Task 17's `spawn_worker` + `wait_for_parked`). Convergence maps should distinguish between condition types when noting unblock points.

**Invariant categorization (NEW):** Categorize coverage gaps by type. The 2 deferred Task 16 tests are FINALIZER-coverage gaps (NOT sentinel-coverage gaps). The 8 Task 14 skips are TEST-EXECUTION-SHAPE gaps (NOT data-dependency gaps post-Task-16). Categorical distinctions keep invariants clean — W7's `0 → 6 sentinel raises` stays observable without ambiguity.

**Branch-matrix-as-central-artifact pattern (NEW for Task-16-class tasks):** When a task has ≥6 distinct exit paths, draft a branch matrix as a top-level convergence-map section. Use rows for exit paths, columns for distinguishing contracts (mutator, job result, finalizer-routed?, sentinel?). Per-test triage references rows by number; coverage gaps become observable.

**Two-read protocol (carried, reaffirmed third successive instance):** Controller's read + user's `/copy` independent read. Both produce drafts; convergence happens at the dispatch boundary. Refinements (R1, R2, R3...) merge user's read into the final draft. Adjudication questions arise at structural divergence points (option (a) vs (b) vs (c)) and require user resolution.

**Locks vs watchpoints (carried):** Locks are positive scope (mandatory things); watchpoints are negative scope (forbidden things). Both binding. Per-task discipline since Task 13.

**Acceptance criteria style (carried):** Structural location, NOT post-edit line numbers. Split: Code + Tests + Closeout-docs.

**Commit discipline (carried):** New commits, never amend. Stage specific files only.

**Per-test triage style (carried):** No blanket migrations. Every old test gets per-case judgment. Triage table in dispatch packets is binding.

**Skip-reason rubric (carried):** Each `@pytest.mark.skip(reason=...)` must (a) cite specific Phase/Task as unblock owner, (b) explain structural mechanic, (c) point to real sibling for partial coverage OR honestly explain why no real sibling exists.

**Evidence density (carried):** File:line citations expected throughout; tables preferred over prose.

**Process gap signaling (carried):** BLOCKED + question preferred over DONE_WITH_CONCERNS + unilateral decision. Controller adjudicates scope; implementer faithfully executes.

## Gotchas

(Carry-over from prior session: G1-G18 still apply. New this session: G19-G24.)

### G1-G18 (carry-forward from prior handoff)

Apply identically. See `docs/handoffs/archive/2026-04-25_15-42_phase-f-task-15-complete-task-16-next.md` for full text. Highlights still binding:
- G9: `_WorkerTerminalBranchSignal` empty-args mechanic (use `signal.reason`, not `str(signal)`)
- G11: Plan-line numbers throughout `phase-f-worker.md` are stale (Task 15 drift ~+27 lines; Tasks 6-14 added more)
- G13: `ResolutionRegistry.register(..., kind=...)` requires `kind: EscalatableRequestKind` kw arg (Task 16 trap — REMAINS)
- G16: `MagicMock(spec=type(controller._artifact_store))` is the pyright-friendly pattern for spying on private types

### G19: `kind=` argument trap in plan pseudocode (Task 16 specific)

Plan `:663-667` calls `registry.register(parsed.request_id, job_id=job_id, timeout_seconds=...)` — but live API at `resolution_registry.py:173-180` requires `kind: EscalatableRequestKind` as kw-only. Fresh implementer reading plan verbatim would skip the kw arg → runtime TypeError. Convergence map L4 locks this as `kind=cast(EscalatableRequestKind, parsed.kind)`.

### G20: Cancel-success / decide-success path goes through OLD `_finalize_turn` at Task 16 commit time

For rows 1-2 of the branch matrix (decide-success + timeout-cancel-success), handler returns None → turn proceeds → `_finalize_turn` runs. But `_finalize_turn` rewrite (Captured-Request Terminal Guard) is owned by Phase H Task 19. At Task 16 commit, this path will misclassify canceled jobs. Per option (b) adjudication: integration tests for these 2 rows are SKIPPED with explicit Task 19 citations. The CODE lands; the E2E TESTS defer.

### G21: Mode B test execution shape requires Task 17, not just Task 16

Mode B tests (2 tests at `test_delegation_controller.py:2598`, `test_delegate_start_integration.py:802`) use synchronous `controller.start(...)` → `assert isinstance(start_result, DelegationEscalation)`. Under Task 16's new handler, `start()` blocks on `registry.wait(...)` indefinitely → test deadlocks. Mode B's DATA dependency (`update_parked_request` wiring) lands at Task 16, but TEST-EXECUTION-SHAPE requires Task 17's `spawn_worker` + `wait_for_parked` split. Both Mode A AND Mode B unblock at Task 17.

### G22: A3 carry-forward was already resolved by Task 14 closeout `65f270ab` but not moved to Closed

Task 14 closeout `65f270ab` added `cast(EscalatableRequestKind, request.kind)` at the construction site (per `carry-forward.md:142` Task 14 closeout entry text). The carry-forward.md ledger move was missed. A3 still appears at line 18 of the Open items section. L11 audit at Task 16 closeout-docs corrects this.

### G23: F16.1 cross-phase test-coverage handoff is novel shape

F16.1 documents 2 tests deferred to Task 19 with same-commit unskip contract. Future Task 19 convergence map MUST include F16.1 in scope (search carry-forward.md for `F16.1` during drafting), otherwise tests stay skipped indefinitely. Pattern: convergence-map drafting protocol must grep for own-task-ID references in carry-forward.md to pre-empt orphaning.

### G24: `_finalize_turn`'s local `_CANCEL_CAPABLE_KINDS` at `:1628` is separate from handler's at `:757`

Both shadow the absent module-level constant. Don't consolidate at Task 16 (W10). Task 19 may consolidate them when rewriting `_finalize_turn`; Task 16 must not. Renaming or deleting either constant would break the other's logic.
