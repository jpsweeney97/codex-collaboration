---
date: 2026-04-19
time: "22:25"
created_at: "2026-04-20T02:25:43Z"
session_id: d88aa18a-6bb3-43c4-82aa-8f4341779d3f
resumed_from: "docs/handoffs/archive/2026-04-19_17-01_t06-decide-plan-scrutinized-and-defensible.md"
project: claude-code-tool-dev
branch: feature/t06-decide-opening-slice
commit: 02d2f1ed
title: "T-06 decide opening slice — implemented, reviewed, PR #109 opened"
type: handoff
files:
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/journal.py
  - packages/plugins/codex-collaboration/server/execution_prompt_builder.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/consultation_safety.py
  - packages/plugins/codex-collaboration/server/__init__.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_models_r2.py
  - packages/plugins/codex-collaboration/tests/test_journal.py
  - packages/plugins/codex-collaboration/tests/test_execution_prompt_builder.py
  - packages/plugins/codex-collaboration/tests/test_mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - packages/plugins/codex-collaboration/tests/test_consultation_safety.py
  - packages/plugins/codex-collaboration/tests/test_codex_guard.py
---

# T-06 Decide Opening Slice — Implemented, Reviewed, PR #109 Opened

## Goal

Implement the T-06 opening slice: `codex.delegate.decide` for live same-session escalation resolution (approve or deny), following the scrutinized plan at `docs/plans/2026-04-19-t06-decide-opening-slice.md`.

**Trigger:** Prior handoff said "Next action for next-session Claude: Run the plan's pre-flight checks, create a feature branch, then execute Task 1." The user had prepared the worktree at `/Users/jp/Projects/active/claude-code-tool-dev/.claude/worktrees/t06-decide-opening-slice` on `feature/t06-decide-opening-slice` before the session started.

**Stakes:** This is the first consumer of the T-05 escalation substrate. The approve/deny semantics, journal recovery, and MCP contract established here become the foundation that `codex.delegate.poll`, skill UX, and cross-session recovery must respect.

**Success criteria (all met):**
1. `codex.delegate.decide` MCP tool registered and dispatching through McpServer
2. Approve reuses retained runtime to dispatch follow-up execution turn
3. Deny terminates job as `failed` with clean lifecycle cleanup
4. Typed rejections for all invalid inputs (9 rejection reasons)
5. Journal-backed crash recovery for approval-resolution operations
6. PreToolUse safety policy scanning `answers` field
7. 727 tests passing (698 baseline + 29 new), 0 regressions, ruff clean
8. PR #109 opened for review

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. T-05 (execution-domain foundation) is complete and merged at `271f23aa`. This slice implements the first consumer. Remaining T-06 slices: `codex.delegate.poll`, promotion flow, `/delegate` skill UX.

## Session Narrative

**Phase 1 — Handoff load and orientation (~5 min).** Loaded the prior handoff (`2026-04-19_17-01_t06-decide-plan-scrutinized-and-defensible.md`) which documented: plan written by user, scrutinized twice with adversarial lens, all 7 findings addressed, verdict `Defensible`. The user confirmed the worktree was ready and invoked `/subagent-driven-development` to orchestrate the implementation.

**Phase 2 — Pre-flight and setup (~5 min).** Verified worktree at `271f23aa` on `feature/t06-decide-opening-slice`. Ran plan pre-flight P2: 70 baseline delegation tests passing in 0.84s. Created 6 task tracking items with dependency chain (1→2→3→4→5→6 with 1-2 independent, 3 blocked by both, 4-6 sequential).

**Phase 3 — SDD execution of 6 tasks (~90 min).** Each task followed the same cycle: dispatch implementer subagent with full task text → spec compliance review → code quality review → mark complete. Model selection optimized cost: Tasks 1-2 (mechanical vocabulary/prompt additions) used sonnet; Tasks 3-6 (extraction, integration, recovery) used opus.

Task 3 was the critical inflection point — extracting `_execute_live_turn()` from `start()`. This ~90-line extraction moved the entire server-request handler closure (with `nonlocal` captures, interrupt handling, parse failure carve-outs) into a reusable helper that both `start()` and `decide()` call. The spec reviewer verified extraction fidelity line by line: all three `nonlocal` declarations preserved, handler closure's `entry` re-lookup pattern preserved, exception handler scope matched. The code quality reviewer confirmed the extraction was faithful and noted one minor log message clarity issue (deferred to final review).

Task 4 brought `decide()` to life — the core ~130-line method with validation ladder, journal lifecycle (intent → audit → dispatched → side effects → completed), and both approve/deny paths. The code quality reviewer raised a concern about deny-path ordering (journal `completed` written after `session.close()`), but analysis confirmed the ordering was intentional and correct: deny writes `job.status="failed"` before close, and recovery's orphaned-job sweep only catches `running`/`needs_escalation` — a `failed` job is terminal and untouched.

Tasks 5-6 added the defensive layers (rejections, recovery, safety policy) and wired everything through MCP dispatch. The spec reviewer caught a ruff E402 in Task 2's test file (import after function defs) — fixed with a separate commit.

**Phase 4 — Post-implementation review (~15 min).** The user ran an external code review on the complete branch. Two real findings:

1. **P1 (High): Stale request_id acceptance.** `decide()` validated `request.collaboration_id == job.collaboration_id` but didn't check that the request was the *currently active* escalation. Reproduction: `42(command_approval) → approve → 55(request_user_input) → approve(request_id='42', answers=None)` bypassed `answers_required` because request "42" is `command_approval`. Fixed with an in-memory `_decided_request_ids: set[str]` on the controller and a new `request_already_decided` rejection reason.

2. **P2 (Medium): Deny-path post-commit failures leaked raw exceptions.** The approve path wrapped `_execute_live_turn` failures in `CommittedDecisionFinalizationError`, but the deny path's post-audit writes could raise raw exceptions. Fixed by wrapping the deny path's post-dispatched operations in try/except → `CommittedDecisionFinalizationError`.

Both fixes committed with regression tests. Final state: 8 commits, 727 tests, ruff clean.

**Phase 5 — PR creation (~5 min).** Pushed branch, opened PR #109 with structured summary and test plan.

## Decisions

### Decision 1: In-memory set for stale request_id detection

**Choice:** Track decided request_ids in `self._decided_request_ids: set[str]` on the controller instance, not in the journal or pending request store.

**Driver:** The post-implementation review found that `decide()` accepted any request whose `collaboration_id` matched the job, including requests from prior escalation cycles. The reproduction: `42(command_approval) → approve → 55(request_user_input) → approve(request_id='42', answers=None)` returned `DelegationDecisionResult` instead of `answers_required`.

**Alternatives considered:**
- **Journal-based check** — query journal for completed `approval_resolution` entries with the given `request_id`. Rejected because `list_unresolved()` only returns non-completed entries, and a separate query method would add complexity for the same-session-only case.
- **Store-based check** — add `update_status()` to `PendingRequestStore` to mark requests as "decided". Rejected because it requires schema changes to a frozen dataclass store for a problem that only exists within a single session.
- **Track current request_id on DelegationJob** — add `escalation_request_id` field. Rejected because `DelegationJob` is frozen and the store would need update support for a field that's only relevant within the same session.

**Trade-offs accepted:** The set is cleared on controller recreation (restart). This is correct for the same-session-only design: after restart, recovery demotes all orphaned `needs_escalation` jobs to `unknown`, so the `job_not_awaiting_decision` check catches stale decides. If cross-session decide is added later, this approach would need revisiting.

**Confidence:** High (E2) — the reviewer's reproduction confirmed the gap, and the fix was verified with a regression test that reproduces the exact scenario.

**Reversibility:** High — the set is a single field and 4 lines of validation code. Can be replaced with a store-based approach when cross-session decide lands.

**Change trigger:** When `codex.delegate.poll` or cross-session runtime reattach lands, the in-memory approach may need a durable equivalent.

### Decision 2: Wrap deny path in CommittedDecisionFinalizationError

**Choice:** Wrap the deny path's post-dispatched operations in try/except → `CommittedDecisionFinalizationError`, matching the approve path's pattern.

**Driver:** The post-implementation review identified asymmetry: the approve path wrapped `_execute_live_turn` failures in `CommittedDecisionFinalizationError`, but the deny path's post-audit writes (status/release/close/journal-completed) could raise raw exceptions after the deny was already committed (audit event emitted).

**Alternatives considered:**
- **Leave as-is** — deny's post-audit operations are simple sequential writes, unlikely to fail. Rejected because the approve path already established the principle that committed decisions must not leak raw exceptions.
- **Per-operation try/except** — wrap each deny operation individually with separate error handling. Rejected as overengineering for a path where any failure means "committed but local state is uncertain."

**Trade-offs accepted:** The wrapping catches all post-dispatched exceptions including harmless ones (e.g., redundant close on an already-closed session). This is the same trade-off the approve path makes.

**Confidence:** High (E2) — the reviewer reproduced the issue by forcing `session.close()` to fail after the deny was committed.

**Reversibility:** N/A — this is a bug fix, not a design choice.

**Change trigger:** None — this corrects an asymmetry, not a preference.

### Decision 3: SDD model selection — sonnet for mechanical, opus for integration

**Choice:** Used sonnet for Tasks 1-2 (type/prompt additions with exact code specified) and opus for Tasks 3-6 (extraction, integration, recovery, MCP dispatch).

**Driver:** Task complexity signals: Tasks 1-2 touch 1-2 files with complete spec and no judgment calls. Tasks 3-6 require multi-file coordination, pattern matching against existing code, and understanding of the handler closure's variable capture semantics.

**Alternatives considered:**
- **All opus** — maximum quality everywhere. Rejected for cost/speed — Tasks 1-2 are verbatim implementations that don't benefit from stronger reasoning.
- **All sonnet** — maximum speed. Rejected because Task 3's extraction requires careful reading of the existing closure and Task 4's `decide()` method has complex multi-store interactions.

**Trade-offs accepted:** Sonnet occasionally produces less precise self-review commentary, but the two-stage review (spec + quality) catches any issues regardless of implementer model.

**Confidence:** Medium (E1) — model capability differences are empirical. Both models produced correct code in this session.

**Reversibility:** Per-task — model choice is independent for each dispatch.

**Change trigger:** If sonnet quality improves sufficiently for multi-file integration work, use it uniformly.

## Changes

### `docs/superpowers/specs/codex-collaboration/contracts.md` — Pin decide contract

**Purpose:** Added "Decision Rejection" and "Decide Result" typed-response sections after "### Job Busy". These define the caller-facing contract for `codex.delegate.decide`.

**Key details:** Decision Rejection has 9 rejection reasons (expanded from original 8 after review finding added `request_already_decided`). Decide Result includes optional `pending_request` (present only when approve triggers re-escalation) and `agent_context` (best-effort agent message).

### `packages/plugins/codex-collaboration/server/models.py` — Decide types

**Purpose:** Added `DecisionAction`, `DecisionRejectedReason` Literals, `DelegationDecisionResult` and `DecisionRejectedResponse` frozen dataclasses, `AuditEvent.decision` optional field, `OperationJournalEntry` extended with `approval_resolution` operation and `request_id`/`decision` fields.

**Key details:** `DecisionRejectedReason` includes `request_already_decided` (added in review fix commit). `AuditEvent.decision` is typed as `str | None` (not `DecisionAction`) — deliberate choice so audit replay doesn't fail validation on future or unknown decision values.

### `packages/plugins/codex-collaboration/server/journal.py` — Approval-resolution validation

**Purpose:** Extended `_VALID_OPERATIONS` with `approval_resolution`, `_JOURNAL_OPTIONAL_STR` with `request_id` and `decision`, and added conditional validation branches for `approval_resolution` at `intent` and `dispatched` phases.

**Key details:** Intent phase requires `job_id`, `request_id`, `decision`. Dispatched phase additionally requires `runtime_id` and `codex_thread_id`. The `completed` phase intentionally has no conditional validation (existing pattern — production writers emit minimal resolution markers).

### `packages/plugins/codex-collaboration/server/execution_prompt_builder.py` — Resume prompt

**Purpose:** Added `build_execution_resume_turn_text()` that constructs the follow-up prompt used after `decide(approve)`. Tells the execution agent the earlier server request was resolved at the wire layer and includes escalation context.

**Key details:** JSON-dumps `requested_scope` (indent=2, sort_keys=True) and optional `answers` payload. The prompt explicitly says "Do not re-ask for the same approval; treat the caller decision below as authoritative."

### `packages/plugins/codex-collaboration/server/delegation_controller.py` — Core decide implementation

**Purpose:** The largest change — extracted `_execute_live_turn()`, added `_mark_execution_unknown_and_cleanup()`, implemented `decide()` with full validation and journal lifecycle, extended `recover_startup()` with approval-resolution reconciliation and broadened orphaned-job sweep.

**Key changes:**
- `_execute_live_turn()` (lines 551-677): Extracted from `start()`. Contains handler closure with `nonlocal` captures, parse failure carve-out, interrupt handling, turn execution, and finalization call. Both exception paths route through `_mark_execution_unknown_and_cleanup()`.
- `_mark_execution_unknown_and_cleanup()` (lines 679-718): Consolidates failure handling — marks job unknown, handle unknown, releases runtime, closes session — each in its own try/except with `logger.error`.
- `_finalize_turn()` terminal branches: Added `lineage_store.update_status(collaboration_id, "completed")` in both non-escalation terminal paths. Escalation branch unchanged (handles stay active for decide).
- `decide()` (lines 852-1030): Validation ladder (9 rejection reasons), journal lifecycle (intent → audit → dispatched → side effects → completed), deny path (wrapped in CommittedDecisionFinalizationError), approve path (resume prompt → `_execute_live_turn` → wrap in CommittedDecisionFinalizationError).
- `_decided_request_ids: set[str]` — in-memory tracking of already-decided request_ids to prevent stale request reuse.
- `recover_startup()` extended: approval-resolution journal reconciliation (close unresolved entries), then orphaned-job sweep broadened to catch `needs_escalation` (not just `running`).

### `packages/plugins/codex-collaboration/server/mcp_server.py` — MCP dispatch

**Purpose:** Registered `codex.delegate.decide` tool and added dispatch branch with defensive answers normalization.

**Key details:** Wire format `{"q1": {"answers": ["yes"]}}` normalized to controller format `{"q1": ("yes",)}` with `isinstance` checks at every nesting level (key, value, answers list, individual items). Serialization handles both `DelegationDecisionResult` (manual payload with optional fields) and `DecisionRejectedResponse` (via `asdict`).

### `packages/plugins/codex-collaboration/server/consultation_safety.py` — Safety policy

**Purpose:** Added `DELEGATE_DECIDE_POLICY` with `expected_fields={"job_id", "request_id", "decision"}` and `content_fields={"answers"}`. The `answers` field is recursively scanned for credential leakage.

### `packages/plugins/codex-collaboration/server/__init__.py` — Public exports

**Purpose:** Exported `DecisionRejectedResponse` and `DelegationDecisionResult`.

## Codebase Knowledge

### Decide Method Architecture

The `decide()` method at `delegation_controller.py:852-1030` follows a three-phase pattern:

```
decide()
│
├─ Phase 1: Validation ladder (9 checks, early return DecisionRejectedResponse)
│   ├─ invalid_decision (not approve/deny)
│   ├─ job_not_found
│   ├─ job_not_awaiting_decision (status != needs_escalation)
│   ├─ request_not_found
│   ├─ request_job_mismatch (collaboration_id mismatch)
│   ├─ request_already_decided (in _decided_request_ids set)
│   ├─ answers_not_allowed (deny + answers)
│   ├─ answers_required (request_user_input + approve - no answers)
│   ├─ answers_not_allowed (non-request_user_input + answers)
│   └─ runtime_unavailable (handle or registry entry missing)
│
├─ Phase 2: Journal lifecycle
│   ├─ intent phase (pre-commit marker)
│   ├─ audit event (decision committed — point of no return)
│   └─ dispatched phase (correlates with runtime)
│
└─ Phase 3: Side effects (wrapped in CommittedDecisionFinalizationError)
    ├─ Deny: job→failed, handle→completed, release, close, journal completed
    └─ Approve: resume prompt → _execute_live_turn → journal completed
```

### Recovery Architecture (Post-T-06)

```
recover_startup()
│
├─ Pass 1: Journal reconciliation (per-operation)
│   ├─ job_creation entries → mark handle/job unknown if dispatched (T-05)
│   └─ approval_resolution entries → close journal unconditionally (T-06)
│
├─ Pass 2: Orphaned-job sweep (status-based)
│   └─ list_active() → demote running + needs_escalation → unknown (broadened in T-06)
│
└─ Each pass has a single responsibility:
    Pass 1 only writes journal entries
    Pass 2 only writes job/handle status
    Neither invalidates the other's preconditions
```

### Key Locations (Updated)

| Concept | Location |
|---------|----------|
| `decide()` method | `delegation_controller.py:852-1030` |
| `_execute_live_turn()` | `delegation_controller.py:551-677` |
| `_mark_execution_unknown_and_cleanup()` | `delegation_controller.py:679-718` |
| `_reject_decision()` helper | `delegation_controller.py:834-846` |
| `CommittedDecisionFinalizationError` | `delegation_controller.py:170-176` |
| `_decided_request_ids` initialization | `delegation_controller.py` in `__init__` |
| `_finalize_turn` non-escalation handle fix | `delegation_controller.py:797` |
| `_finalize_turn` no-request handle fix | `delegation_controller.py:811` |
| `recover_startup` approval_resolution reconciliation | `delegation_controller.py:1135-1161` |
| `recover_startup` orphaned sweep (broadened) | `delegation_controller.py:1174-1182` |
| `build_execution_resume_turn_text` | `execution_prompt_builder.py:40-72` |
| `DELEGATE_DECIDE_POLICY` | `consultation_safety.py:50-53` |
| `codex.delegate.decide` tool definition | `mcp_server.py:122-150` |
| `codex.delegate.decide` dispatch | `mcp_server.py:376-411` |
| `DelegationDecisionResult` dataclass | `models.py:381-389` |
| `DecisionRejectedResponse` dataclass | `models.py:392-400` |
| `DecisionAction` Literal | `models.py:34` |
| `DecisionRejectedReason` Literal | `models.py:35-45` |

### Test Fixture Architecture

| Fixture | Location | Purpose |
|---------|----------|---------|
| `_build_controller()` | `test_delegation_controller.py:148-208` | Creates DelegationController with fakes; returns 8-tuple |
| `_FakeSession` | `test_delegation_controller.py:60-98` | Simulates AppServerRuntimeSession with configurable requests/results |
| `_FakeControlPlane` | `test_delegation_controller.py:100-146` | Creates FakeSession instances; stores in `_sessions` list |
| UUID pool | `test_delegation_controller.py:173-185` | 10 semantic names: job-1, collab-1, delegate-start-evt-1, ... |
| `_command_approval_request()` | `test_delegation_controller.py:1124-1141` | Returns command_approval server request dict (id=42) |
| `_request_user_input_request()` | `test_delegation_controller.py:1144-1161` | Returns request_user_input server request dict (id=55) |
| `_permissions_request(request_id, item_id)` | `test_delegation_controller.py:1164-1181` | Configurable permissions server request |
| `FakeDelegationControllerWithDecide` | `test_mcp_server.py:1035-1090` | MCP dispatch test fake with decide() |
| `_build_e2e_setup()` | `test_delegate_start_integration.py` | Full McpServer setup with configurable session factory |

### `_FakeSession` Multi-Turn Semantics

`_FakeSession.run_execution_turn()` now resets `self._interrupted = False` at the start of each turn (line 82), preventing cross-turn interrupt carryover. This was critical for multi-turn decide tests where the first turn triggers an interrupt (escalation) and the second turn (follow-up after approve) must start with fresh interrupt state.

To configure a session for a follow-up turn after `start()` escalates: access `control_plane._sessions[0]` and set `_server_requests` (list of server request dicts) and `_turn_result` (TurnExecutionResult).

### MCP Answers Normalization

Wire format → controller format transformation at `mcp_server.py:376-411`:
- Wire: `{"q1": {"answers": ["yes", "confirmed"]}}` (JSON object with string arrays)
- Controller: `{"q1": ("yes", "confirmed")}` (dict with tuples)
- Defensive: non-dict raw_answers → None, non-string keys skipped, non-dict values skipped, non-list answers skipped, non-string items cause entire entry to be skipped

## Context

### Mental Model

This session was **plan execution with orchestrated quality gates**. The SDD (Subagent-Driven Development) pattern separated concerns: the controller (me) held the full plan context and assessed review findings against plan design decisions, while implementer subagents received self-contained prompts and never read the plan file. The two-stage review (spec compliance → code quality) caught issues at the right abstraction level — spec review caught the E402 lint issue early, and the post-implementation external review caught the two correctness gaps (stale request_id, deny post-commit).

The decide method itself follows a "validation → journal → side effects" phase pattern where the journal lifecycle creates crash-recovery markers at each transition. The "committed" point is the audit event emission — after that, both approve and deny paths wrap failures in `CommittedDecisionFinalizationError` to prevent callers from blindly retrying.

### Why This Session Matters

The approve/deny semantics established here are the contract that `codex.delegate.poll`, skill UX, and cross-session recovery must respect. The two review findings (stale request_id, deny post-commit) would have been correctness issues in production — the stale request_id gap allowed resolving a `request_user_input` escalation without providing answers, and the deny post-commit gap could have caused a caller to retry a deny that already tore down the runtime.

### Project State

- **T-05:** COMPLETE. Both slices merged to main at `271f23aa`. 698 tests.
- **T-06:** Opening slice IMPLEMENTED. PR #109 opened. 727 tests.
- **Branch:** `feature/t06-decide-opening-slice` at `02d2f1ed`. Worktree at `.claude/worktrees/t06-decide-opening-slice`.
- **PR #109:** Open, awaiting review.

## Learnings

### Stale request_ids are a cross-turn state interaction that single-task TDD doesn't catch

**Mechanism:** `decide()` validates `request.collaboration_id == job.collaboration_id` but doesn't verify the request is from the *current* escalation cycle. After approve → re-escalation, old requests remain in `PendingRequestStore` and pass the collaboration check.

**Evidence:** Post-implementation review reproduced: `42(command_approval) → approve → 55(request_user_input) → approve(request_id='42', answers=None)` returned success instead of `answers_required`. The stale request "42" was `command_approval`, not `request_user_input`, bypassing the answers validation.

**Implication:** When a method accepts identifiers that can become stale across cycles, validate currency — not just ownership. The in-memory `_decided_request_ids` set is the right fix for same-session-only, but cross-session decide would need a durable equivalent.

### Deny-path asymmetry is easy to miss because the approve path has a natural wrapping point

**Mechanism:** The approve path calls `_execute_live_turn()` — a single method call that's easy to wrap in try/except. The deny path is inline sequential operations (update status, release, close, journal) that don't "look" like they need wrapping. But once the audit event is emitted, both paths have committed and must not leak raw exceptions.

**Evidence:** Post-implementation review identified the gap. The fix was wrapping all deny post-dispatched operations in try/except → `CommittedDecisionFinalizationError`.

**Implication:** For any method with a "committed" point, systematically verify that both branches (and all future branches) wrap post-commit failures. The "committed" point is the audit event emission, not the journal dispatched phase.

### SDD model selection saves cost without sacrificing quality when the plan specifies exact code

**Mechanism:** Tasks with verbatim code in the plan (types, prompts, test assertions) are mechanical — the implementer's job is faithful transcription, not design judgment. Cheaper models handle this well. Tasks requiring code comprehension (extraction, integration) benefit from stronger reasoning.

**Evidence:** All 6 tasks produced correct implementations on first dispatch. No re-dispatches were needed. The two correctness gaps were found by post-implementation review, not by implementer failures.

**Implication:** When the plan is well-specified (exact code, exact insertion points), implementer model selection can be optimized by task complexity. The quality gates (spec + code review) catch any issues regardless of implementer model.

## Next Steps

### 1. Merge PR #109 after review

**Dependencies:** PR #109 at `feature/t06-decide-opening-slice`. Awaiting review.

**What to do:** Follow the same review pattern as PR #108 — 5-agent comprehensive review, triage with user, fix before merge. The two review findings from this session are already fixed in the branch.

**Acceptance boundary:** 727 tests pass, ruff clean, no review findings above informational severity.

### 2. Plan the next T-06 slice: `codex.delegate.poll`

**Dependencies:** PR #109 merged.

**What to read first:**
- T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` for remaining scope
- The decide opening slice plan's "Risks And Known Deferrals" section (plan lines 2192-2202) for deferred items that `poll` would address
- `contracts.md` for the job lifecycle states that `poll` needs to expose

**Approach:** The user writes the plan, Claude scrutinizes. Same pattern as the decide slice.

### 3. Clean up the worktree after merge

**Dependencies:** PR #109 merged.

**What to do:** Use the `exiting-worktrees` skill to clean up `.claude/worktrees/t06-decide-opening-slice`.

## In Progress

**Clean stopping point.** All implementation complete, all review findings fixed, PR #109 opened. No work in flight.

- **Completed:** 6-task implementation via SDD, two-pass review per task, post-implementation review with 2 findings fixed, PR opened.
- **Not in flight:** No code changes pending, no review comments to address.
- **Next action for next-session Claude:** Check PR #109 status. If approved, merge and clean up worktree. If review comments, address them on the feature branch.

## Open Questions

### 1. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** The handler calls `entry.session.interrupt_turn()` from inside the `_server_request_handler` callback. This sends a `turn/interrupt` JSON-RPC request via the same transport that's reading notifications.

**Impact:** Medium. If the transport doesn't handle re-entrant reads, the handler will deadlock.

**Decision pending until:** Live testing against the real App Server.

### 2. `on-request` operational semantics (inherited from T-05)

**Context:** The vendored schema proves `on-request` is a valid `approvalPolicy` value, but operational semantics are not documented. Controller defaults to `untrusted` per D1.

**Decision pending until:** Live probe against the real App Server.

### 3. Approve turn prompt shape adequacy

**Context:** `build_execution_resume_turn_text()` tells the execution agent "the earlier server request has already been resolved at the wire layer." Whether this prompt produces reliable follow-up behavior (the agent picks up where it left off without re-requesting the same approval) is unverified.

**Decision pending until:** Live execution testing.

## Risks

### 1. `_decided_request_ids` is in-memory only

If `codex.delegate.poll` or cross-session decide is added, the in-memory set won't persist across restarts. A durable equivalent (store-based or journal-based) would be needed. For the same-session-only design, this is correct — recovery demotes orphaned jobs.

### 2. `_FakeSession` complexity continues to grow

The fake session now has: `run_execution_turn` (with per-turn `_interrupted` reset), `interrupt_turn`, `close`, `_raise_on_turn`, `_interrupted` state, and configurable server requests + turn result. If the fake drifts from the real `AppServerRuntimeSession` interface, tests pass but production fails.

### 3. Same-session-only constraint creates a hard boundary

If the process crashes between `codex.delegate.start` returning an escalation and `codex.delegate.decide` being called, the job is stuck. Recovery correctly demotes to `unknown` (no zombies), but the user's escalation decision is lost. `codex.delegate.poll` would allow rediscovering these jobs.

### 4. `codex.delegate.start` still has no dedicated PreToolUse scan policy

This plan added `DELEGATE_DECIDE_POLICY` only. The existing start-surface guard gap predates T-06 and is intentionally left out of scope (risk row at plan line 2200).

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 decide plan | `docs/plans/2026-04-19-t06-decide-opening-slice.md` | Implementation authority (2216 lines, scrutinized twice) |
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| T-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | Closed — substrate context |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Schema authority |
| Recovery spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Recovery semantics |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-19_17-01_t06-decide-plan-scrutinized-and-defensible.md`
- T-05/T-06 arc: execution-start COMPLETE → pending-request capture COMPLETE → T-05 closed + T-06 scoped → T-06 plan scrutinized → **T-06 decide implemented + PR #109 (this handoff)**

### Commit chain

| Commit | Message |
|--------|---------|
| `8b1aeceb` | `feat(t20260330-06): pin decide contract and journal vocabulary` |
| `c04fcb54` | `feat(t20260330-06): add execution resume prompt builder` |
| `36bf451d` | `refactor(t20260330-06): share execution turn path and close terminal handles` |
| `3debda25` | `feat(t20260330-06): implement same-session decide success paths` |
| `b8846bf4` | `feat(t20260330-06): add decide recovery and safety policy` |
| `33e91090` | `feat(t20260330-06): expose codex.delegate.decide through MCP` |
| `0da41b1b` | `fix: move module-level import to top of test_execution_prompt_builder.py` |
| `02d2f1ed` | `fix(t20260330-06): reject stale request IDs and wrap deny post-commit failures` |

## Gotchas

### 1. Stale request_ids pass collaboration validation but bypass kind-specific checks

**Symptom:** `decide(approve, request_id=<old_command_approval>)` succeeds even when the current escalation is `request_user_input` (which requires answers).

**Prevention:** `_decided_request_ids` set added in commit `02d2f1ed`. Any request_id that has been decided is rejected with `request_already_decided`.

### 2. Deny path must wrap post-commit failures just like approve path

**Symptom:** Raw exception bubbles from deny path after the decision is committed (audit event emitted), causing callers to see a retriable-looking error for a non-retriable operation.

**Prevention:** Try/except → `CommittedDecisionFinalizationError` added in commit `02d2f1ed`.

### 3. `_FakeSession._interrupted` leaked across turns before the fixture fix

**Symptom:** If the first turn triggered an interrupt (escalation), the second turn started pre-interrupted. The handler processes the new server request, but the interrupted status was already `True` from the first turn.

**Prevention:** `self._interrupted = False` reset at top of `run_execution_turn()` (commit `36bf451d`). No existing T-05 tests relied on cross-turn interrupt carryover.

### 4. Two-pass recovery coupling — journal close relies on orphaned sweep for state demotion

**Symptom:** `approval_resolution` journal reconciliation closes journal entries but does NOT demote job/handle status. It relies on the orphaned-job sweep (Pass 2) to handle the demotion.

**Prevention:** This is intentional design per the plan's Decision 2. The change trigger: when `codex.delegate.poll` lands, the sweep must be re-evaluated — jobs that can be inspected should not be unconditionally demoted.

## Conversation Highlights

### User's workflow: pre-built worktree + SDD invocation

The user prepared the worktree before the session: `feature/t06-decide-opening-slice` at `.claude/worktrees/t06-decide-opening-slice`. The first message was: "Yes, continue with the pre-flight checks and Task 1. Use /subagent-driven-development. The isolated workspace is ready." This is the most autonomous implementation session in the T-06 arc — previous sessions were plan writing and scrutiny.

### External code review as the final quality gate

The user ran an external code review tool on the complete branch and `/copy`'d the findings. The review found 2 issues (P1 stale request_id, P2 deny post-commit) that the per-task SDD reviews missed. This demonstrates the value of layered review: task-level reviews catch spec deviations and code quality issues, while cross-cutting reviews catch state-interaction bugs that span multiple tasks.

### Clean approval for PR

After the fixes, the user's second review returned: "No findings. Approval to push and open the PR is warranted." The user noted: "make sure you push from `feature/t06-decide-opening-slice`, not the `main` worktree."

## User Preferences

### Implementation workflow: plan → scrutinize → SDD → external review → PR

The user's established pattern: write the plan between sessions, present for adversarial scrutiny, hand to implementation session with pre-built worktree, run external review on complete branch, fix findings, then PR. This session followed the pattern exactly.

### Pre-built worktrees

The user creates feature branch worktrees before the implementation session starts. This session received the worktree ready to go — no branch creation or worktree setup was needed.

### External review as final gate

The user relies on an external review tool (not the SDD per-task reviews) as the final quality gate before PR. The two findings it caught (stale request_id, deny post-commit) validated this approach — the SDD reviews focus on spec compliance and code quality per-task, while the external review finds cross-cutting interaction bugs.
