---
date: 2026-04-23
time: "02:09"
created_at: "2026-04-23T06:09:17Z"
session_id: 40271cdd-a22e-4371-9fb7-bde4c4d44958
resumed_from: "docs/handoffs/archive/2026-04-23_01-41_checkpoint-sandbox-support-roots-implemented.md"
project: claude-code-tool-dev
branch: feature/delegate-remediation-sandbox-approval
commit: 005d4b44
title: "Delegate sandbox — state machine fix for empty available_decisions + execution prompt tuning"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/execution_prompt_builder.py
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - docs/scratch/T-20260423-01-escalation-diagnostic.md
---

# Handoff: Delegate sandbox — state machine fix for empty available_decisions + execution prompt tuning

## Goal

Fix the delegate execution sandbox policy gap discovered during live smoke testing. The
predecessor session implemented sandbox support roots (Codex skill/plugin read access) and
passed 906 unit tests. This session needed to:

1. Run live smoke to verify no escalations for Codex support file reads
2. If smoke passes, commit all changes and create PR

**Trigger:** Predecessor session couldn't complete live smoke because MCP server was serving
stale code. This session started fresh to restart the MCP process.

**Stakes:** Delegate execution is non-functional in production until the sandbox policy allows
the agent to actually work within its worktree. Every smoke so far has escalated and died.

**Connection to project arc:** This is part of the delegate execution remediation ticket
(T-20260423-01). The original ticket covers three handler fixes (already landed in
predecessor sessions), sandbox support roots (predecessor session), and live smoke
verification (this session). The smoke revealed two additional issues not in the original
ticket scope: exec-policy gaps for developer tools and a state-machine bug for
empty-decisions escalations.

## Session Narrative

Session resumed from a checkpoint that said: "sandbox support roots code complete, 906 tests
passing, MCP server needs restart for live smoke." The predecessor had implemented
`_CODEX_SUPPORT_READ_SUBROOTS`, `_resolve_codex_support_roots()`, and the `codex_home`
plumbing through session/controller/sandbox-builder.

### Smoke #1: `rg` exec-policy failure

Ran `/delegate start` with objective "Create docs/scratch/T-20260423-01-smoke.md". The
delegation started and immediately escalated with `command_approval` kind. The agent tried
`rg --files -g 'AGENTS.md'` and the sandbox blocked execution. The `reason` field said
"command failed; retry without sandbox?" and `available_decisions` from the projected view
was `["deny"]`.

User immediately identified this was NOT the support-root issue we fixed — it was an
exec-policy issue for developer tools. `rg` lives at `/opt/homebrew/bin/rg`, outside the
sandbox's platform-default executable paths. User provided a clear analysis with hypotheses
and recommended discarding, preserving the escalation payload, and investigating.

### Discovering the projection layer

User corrected a critical misunderstanding: the `available_decisions: ["deny"]` shown to
the caller is NOT what the App Server sent. The `_project_request_to_view` method at
`delegation_controller.py:864-878` unconditionally forces `_DENY_ONLY_DECISIONS = ("deny",)`
for all `command_approval` and `file_change` kinds (the `_CANCEL_CAPABLE_KINDS`). The raw
wire payload needed inspection.

Read the pending request store JSONL file at
`~/.claude/plugins/data/codex-collaboration-inline/pending_requests/<session_id>/requests.jsonl`.
The raw wire `available_decisions` was `[]` — **empty**, not `["deny"]`. The App Server
offered no decisions at all. The `("deny",)` was entirely the projection layer's invention.

### State-machine stuck state

Tried to discard the first job — rejected: `job_not_discardable` because
`status="needs_escalation"` with `promotion_state=None` wasn't in the discard gate's allowed
set. Denied instead to transition to `failed`, then discarded successfully.

### Smoke #2: Worktree boundary escape

Added platform-tool constraint to execution prompt (prefer `/bin`/`/usr/bin` tools, avoid
Homebrew/mise binaries). Smoke #2: the agent used `/usr/bin/find` (tool guidance worked!) but
navigated above the worktree with `find .. -name AGENTS.md -print`. The `..` resolved outside
the sandbox boundary. Same escalation pattern: `available_decisions: []`, cancel at wire, job
stuck in `needs_escalation`.

Tried to deny — got `request_already_decided` because both jobs used wire `request_id: "0"`
and the in-memory `_decided_request_ids` set (session-scoped, not job-scoped) already
contained `"0"` from the first job's deny. Namespace collision.

### Diagnosing the root cause

Traced the full state-machine flow. The bug: when a cancel-capable request has empty
`available_decisions` (App Server offers no decisions), the `_finalize_turn` method at
line 1528 still sets `final_status = "needs_escalation"` because the kind is in
`_CANCEL_CAPABLE_KINDS`. But with no available decisions, there's nothing for the user to
decide — the job is stuck.

User recommended implementing both fixes:
- **Option B (root cause):** Empty `available_decisions` on cancel-capable requests → finalize
  as `failed`, not `needs_escalation`. Release runtime, close session, complete lineage.
- **Option A (defensive):** Allow discard for `needs_escalation + promotion_state=None` with
  full cleanup (atomic `failed + discarded`, runtime release, session close, lineage
  completion, terminal outcome emission).

User explicitly rejected my initial Option A framing ("just add needs_escalation to the
discard gate") because a `needs_escalation` job owns a live runtime that must be cleaned up.
The discard path needed full lifecycle cleanup, not just a state flag change.

### Implementation and testing

Implemented both fixes. Modified `_finalize_turn` status derivation to check
`captured_request.available_decisions` — empty → `failed`. Modified `discard()` to accept
`needs_escalation + promotion_state=None` with atomic `update_status_and_promotion(failed,
discarded)` plus runtime release, session close, lineage completion, and terminal outcome.

Updated 1 existing test (`test_malformed_available_decisions_fails_closed_at_handler` — now
expects `DelegationJob` with `status="failed"` instead of `DelegationEscalation`). Wrote 7
new tests covering all scenarios user specified. 913 tests passing, ruff clean.

Also strengthened the execution prompt with worktree-boundary prohibition: "Do NOT navigate
above the worktree with '..' or absolute paths outside the workspace."

### Live smoke blocked by stale MCP server

The stuck job `c382b5dc` from smoke #2 still blocks new delegations via the busy gate. The
MCP server process loaded old code at session start — our fixes are on disk but not in the
running process. Cannot test live smoke in this session. Next session restart will load the
new code.

## Decisions

### D1: Tune execution prompt rather than add exec-policy amendment handling

**Choice:** Add platform-tool constraint and worktree-boundary prohibition to the execution
prompt. Defer `acceptWithExecpolicyAmendment` handling to a separate ticket.

**Driver:** User stated: "The original ticket was about making normal delegated execution work
under a restricted sandbox. Running `rg` from `/opt/homebrew/bin` is outside the
platform-default executable set. That is a real limitation, but it is not the same failure as
'cannot run shell commands at all.'"

**Rejected:** `acceptWithExecpolicyAmendment` handling now — user said: "it is an
execution-policy widening mechanism... That needs its own contract: Which binaries are
eligible? Absolute path allowlist or command-pattern amendment? Does it persist for the
session, the job, or only the current turn?"

**Implication:** The delegated agent must use POSIX tools only. Tasks requiring `rg`, `fd`,
`node`, `python`, `uv`, or `ruff` will fail until exec-policy support is added.

**Trade-offs:** Limits the agent's capability — POSIX tools are less powerful than developer
tools for code exploration. Accepted because the sandbox's purpose is tight containment, and
the live-smoke gate doesn't need developer tools.

**Confidence:** High (E2) — confirmed `rg` at `/opt/homebrew/bin/rg` is outside sandbox
defaults; POSIX tools at `/bin`/`/usr/bin` work within sandbox.

**Reversibility:** High — prompt text change, no structural impact. Adding exec-policy
support later only expands capability.

**Change trigger:** If a delegation objective structurally requires developer tools (e.g.,
"run the test suite with pytest"), exec-policy support becomes blocking.

### D2: Empty available_decisions → failed, not needs_escalation (Option B)

**Choice:** In `_finalize_turn`, when a captured cancel-capable request has empty
`available_decisions`, set `final_status = "failed"` instead of `"needs_escalation"`.

**Driver:** User stated: "`needs_escalation` means 'Claude/user can do something.' Empty
decisions means there is nothing useful to ask the user to decide."

**Rejected:** Keeping `needs_escalation` for all cancel-capable kinds — creates irrecoverable
stuck state because deny rejects (`request_already_decided` from wire cancel), discard
rejects (wrong state), busy gate blocks new starts.

**Implication:** The failed path runs full cleanup: release runtime, close session, mark
lineage completed, emit terminal outcome. No orphaned resources.

**Trade-offs:** A `failed` job cannot be retried without starting a new delegation. If the
App Server ever sends empty `available_decisions` when a decision IS possible (edge case),
the job would fail unnecessarily. Considered unlikely — empty decisions is the App Server
saying "this is not decidable."

**Confidence:** High (E2) — traced the full state-machine flow, verified with two
independent live smoke failures, confirmed with raw JSONL store inspection.

**Reversibility:** Medium — changing back to `needs_escalation` would reintroduce the stuck
state. Would need the discard safety valve (Option A) as prerequisite.

**Change trigger:** If the App Server changes semantics and sends empty `availableDecisions`
for decidable requests. Monitor wire payloads during live smoke.

### D3: Defensive discard for needs_escalation (Option A)

**Choice:** Allow `/delegate discard` for `status == "needs_escalation" and
promotion_state is None` with full lifecycle cleanup.

**Driver:** User stated: "Option B prevents this exact trigger, but it does not give you a
safety valve for the current stuck job class or future state-machine mistakes. The busy gate
is intentionally broad, so the system needs a cleanup path for active escalation states that
cannot be resumed."

**Rejected:** Only Option B — doesn't provide escape hatch for future state-machine bugs.
Rejected Option A alone — "treats the symptom" without fixing the root cause.

**Implication:** Any `needs_escalation` job can now be cleaned up via discard, including crash
recovery scenarios where the runtime entry is already gone. The discard path handles missing
runtime entries gracefully.

**Trade-offs:** Widens the discard gate — a `needs_escalation` job that COULD be decided via
deny can also be discarded. User considered this acceptable: "the system needs a cleanup
path for active escalation states that cannot be resumed."

**Confidence:** High (E2) — tested with 2 new tests including crash-recovery scenario
(missing runtime entry).

**Reversibility:** High — additive change to the discard gate. Removing it would only matter
if it's used incorrectly.

**Change trigger:** If discard of `needs_escalation` jobs causes resource leaks or audit
gaps. Monitor outcomes and audit events after enabling.

## Changes

### `server/delegation_controller.py` — State machine fixes

**Option B (line ~1528):** Status derivation in `_finalize_turn` now checks
`captured_request.available_decisions` for cancel-capable kinds. Empty → `"failed"` (flows
to existing non-escalation cleanup path). Non-empty → `"needs_escalation"` (existing
behavior). `interrupted_by_unknown` takes priority over both (still `"needs_escalation"`).

**Option A (line ~1409):** `discard()` gate expanded. New `_needs_escalation_cleanup` flag.
When True: uses `update_status_and_promotion(status="failed", promotion_state="discarded")`
for atomic transition, then `lineage_store.update_status(completed)`,
`runtime_registry.release()`, `session.close()`, `_emit_terminal_outcome_if_needed()`.
Runtime entry lookup is guarded (`if entry is not None`) for crash-recovery scenarios.

### `server/execution_prompt_builder.py` — Sandbox constraints in prompt

Added two constraint blocks to `build_execution_turn_text()`:

1. **Worktree boundary:** "Do NOT navigate above the worktree with '..' or absolute paths
   outside the workspace. The worktree IS a full repository copy."
2. **Tool constraint:** "Use only platform-default executables from /bin and /usr/bin. Do NOT
   use Homebrew, mise, or developer-tool binaries such as rg, fd, uv, node, python, or ruff."

### `tests/test_delegation_controller.py` — 7 new tests + 1 updated

1. `test_empty_available_decisions_command_approval_finalizes_as_failed` — verifies Option B
   for `command_approval` with empty decisions: job failed, runtime released, session closed,
   lineage completed, terminal outcome emitted.
2. `test_empty_available_decisions_file_change_finalizes_as_failed` — same for `file_change`.
3. `test_command_approval_with_wire_decisions_still_escalates` — non-empty decisions still
   produce `needs_escalation`, runtime kept live.
4. `test_decide_deny_works_for_ordinary_escalation_with_nonempty_decisions` — deny on normal
   escalation works: job failed, runtime released, lineage completed.
5. `test_discard_accepts_needs_escalation_and_clears_busy_gate` — Option A: discard
   transitions to `failed + discarded`, releases runtime, closes session, emits audit +
   outcome. Verifies busy gate cleared by starting a new delegation after discard.
6. `test_discard_needs_escalation_handles_missing_runtime_entry` — crash recovery: runtime
   entry already gone, discard still succeeds.
7. `test_decide_does_not_reject_on_resolved_request_status` — wire-level "resolved" on
   `PendingServerRequest.status` does not prevent plugin-level deny.
8. Updated `test_malformed_available_decisions_fails_closed_at_handler` — now expects
   `DelegationJob(status="failed")` instead of `DelegationEscalation`.

### `docs/scratch/T-20260423-01-escalation-diagnostic.md` — Diagnostic evidence

Raw escalation payloads from smokes #1 and #2 with analysis. Includes the raw stored
`PendingServerRequest` from JSONL with `available_decisions: []`, the
`proposedExecpolicyAmendment` field, and the critical finding that the projection layer
invents `("deny",)` for all cancel-capable kinds.

## Codebase Knowledge

### Escalation State Machine (as understood this session)

| Wire Event | Parser | Handler Decision | Finalize Status | User-Facing |
|------------|--------|-----------------|-----------------|-------------|
| `command_approval`, `available_decisions: ["decline", "cancel"]` | Kind `command_approval`, `available_decisions=("decline", "cancel")` | `accept` in decisions? If yes AND in-boundary → accept. Else → cancel | `needs_escalation` | Projected `("deny",)` |
| `command_approval`, `available_decisions: []` | Kind `command_approval`, `available_decisions=()` | `accept` not in () → cancel | **`failed`** (NEW) | Plain `DelegationJob` |
| `file_change`, `available_decisions: []` | Kind `file_change`, `available_decisions=()` | Same as above | **`failed`** (NEW) | Plain `DelegationJob` |
| Unknown method | Kind `unknown` | Interrupt turn | `needs_escalation` | Projected `("approve", "deny")` |

### Key Code Locations

| Concept | Location |
|---------|----------|
| Sandbox policy builder | `server/runtime.py:49-71` (`build_workspace_write_sandbox_policy`) |
| Codex support root resolver | `server/runtime.py:31-46` (`_resolve_codex_support_roots`) |
| Server request handler (in start) | `server/delegation_controller.py:~650-731` |
| Finalize turn status derivation | `server/delegation_controller.py:~1527-1539` |
| Projection to caller view | `server/delegation_controller.py:~864-878` (`_project_request_to_view`) |
| Discard gate | `server/delegation_controller.py:~1409-1478` |
| Deny cleanup pattern | `server/delegation_controller.py:~1777-1808` |
| Execution prompt builder | `server/execution_prompt_builder.py:17-42` |
| Pending request store (JSONL) | `~/.claude/plugins/data/codex-collaboration-inline/pending_requests/<session_id>/requests.jsonl` |
| `_CANCEL_CAPABLE_KINDS` | `server/delegation_controller.py:110` — `{"command_approval", "file_change"}` |
| `_DENY_ONLY_DECISIONS` | `server/delegation_controller.py:862` — `("deny",)` |
| `_PLUGIN_DECISIONS` | `server/delegation_controller.py:861` — `("approve", "deny")` |
| `_decided_request_ids` | `server/delegation_controller.py:268` — in-memory set, session-scoped |
| `_resolve_available_decisions` | `server/approval_router.py:102-112` — normalizes wire to tuple |
| Job store atomic update | `server/delegation_job_store.py:110-140` (`update_status_and_promotion`) |

### Patterns Identified

- **Projection layer separates wire from plugin semantics:** The `_project_request_to_view`
  method at `delegation_controller.py:864` is the boundary. Raw `PendingServerRequest` has
  wire `available_decisions`. `PendingEscalationView` has plugin-level decisions. For
  cancel-capable kinds, plugin always exposes only `("deny",)` because auto-accept handles
  the in-boundary case and cancel handles the out-of-boundary case at the wire level.

- **D4 signal marks wire lifecycle:** `_finalize_turn` at line 1523 marks the pending request
  as `"resolved"` — this is the **wire lifecycle** (controller answered the App Server).
  Plugin-level `deny` is a separate concept operating on the same request. The guard
  `_decided_request_ids` tracks plugin decisions, not wire status.

- **JSONL append-log stores:** Both job store and pending request store use JSONL append with
  `op` field (`create`, `update_status`, `update_status_and_promotion`). The `get()` method
  replays the log to reconstruct current state. Session-scoped by directory.

### Architecture: Request Handler Flow in `_execute_live_turn`

```
_execute_live_turn
  → _server_request_handler (closure, called per server request)
      → parse_pending_server_request (approval_router.py)
      → check: kind in _CANCEL_CAPABLE_KINDS?
          YES → check: "accept" in available_decisions AND is_within_delegation_boundary?
              YES → return {"decision": "accept"} (inline_accepted)
              NO  → store request, return {"decision": "cancel"} (captured_request)
          NO  → check: known denial kind?
              YES → store request, return {"answers": {}}
              NO  → store request, interrupt_turn, return None
  → turn completes (or interrupted)
  → _finalize_turn
      → if captured_request:
          → D6 diagnostic (verify wire signals)
          → D4: mark request "resolved"
          → status derivation (NEW: checks available_decisions for cancel-capable)
          → if needs_escalation: keep runtime live, return DelegationEscalation
          → else: release runtime, close session, return DelegationJob
```

## Context

### Mental Model

This is a **state-machine completeness problem**. The delegation controller's state machine
had an unreachable-but-expected terminal state: when the App Server offers no decisions on a
cancel-capable request, the job enters `needs_escalation` but has no valid transition out.
The fix adds the missing transitions: immediate failure (Option B) and forced cleanup
(Option A).

The sandbox itself has two orthogonal enforcement layers:
1. **File access** (readableRoots/writableRoots) — fixed in predecessor session
2. **Command execution** (exec policy / platform defaults) — NOT in this remediation scope

The execution prompt is a soft control that steers the agent away from the exec-policy
boundary. It's not enforcement — the sandbox is. But it prevents the agent from wasting a
turn on a doomed command.

### Environment State

- Branch: `feature/delegate-remediation-sandbox-approval`
- All changes uncommitted (no commits this session)
- 913 tests passing, ruff clean
- MCP server running old code — new code not testable via live smoke this session
- Stuck job `c382b5dc` blocking new delegations via busy gate (will be clearable after
  session restart with new discard code)
- `rg` at `/opt/homebrew/bin/rg` (Homebrew-installed, outside sandbox platform defaults)

## Learnings

### Wire `available_decisions: []` means "not decidable" — do not escalate

**Mechanism:** The App Server sends `availableDecisions: []` when a command fails in sandbox
and there's no approval path. The `_resolve_available_decisions` parser normalizes this to
an empty tuple. The handler correctly returns `{"decision": "cancel"}`, but finalization
incorrectly treated the captured request as a user-decidable escalation.

**Evidence:** Raw JSONL store at `pending_requests/<session_id>/requests.jsonl` showed
`"available_decisions": []` for both smoke runs. The projected `("deny",)` was entirely from
`_project_request_to_view` forcing `_DENY_ONLY_DECISIONS` for `_CANCEL_CAPABLE_KINDS`.

**Implications:** Any future wire request with empty decisions should be treated as
informational, not as an escalation. The handler's cancel response is the final disposition.

**Watch for:** If the App Server changes semantics and sends empty `availableDecisions`
for requests that ARE decidable, this would cause false job failures.

### The `deny` decision finalizes the job as failed — it is not adaptive

**Mechanism:** `deny` in the current `decide` model calls `_persist_job_transition(failed)`,
releases runtime, closes session, and completes lineage. The agent does not get a chance to
try a different approach. This is by design — escalations are binary.

**Evidence:** User correction: "In the current decide model, deny does not resume the agent
and let it try another path. For a pending escalation, deny finalizes the job as failed and
closes the runtime."

**Implications:** When presenting escalation options, frame deny as terminal ("deny and fail
the job"), not as adaptive ("deny and see if the agent adapts"). If the user wants the agent
to succeed, the underlying issue must be fixed before re-delegating.

### `_decided_request_ids` is session-scoped, not job-scoped — namespace collision risk

**Mechanism:** The in-memory set `_decided_request_ids` at `delegation_controller.py:268`
tracks plugin-level decisions across all jobs in a session. Wire request IDs (JSON-RPC `id`
field) are not globally unique — both jobs in this session used `request_id: "0"`. After
denying the first job's request `"0"`, the second job's deny attempt found `"0"` already in
the set and rejected with `request_already_decided`.

**Evidence:** Observed during smoke #2 cleanup. The first job's deny succeeded and added
`"0"` to `_decided_request_ids`. The second job's deny for its own request `"0"` was
blocked.

**Implications:** This is a latent bug. In normal operation (one job at a time, deny
transitions to failed, discard, start new), the collision is unlikely. But if two jobs
share a session and both escalate with the same wire request ID, the second can't be denied.
The new discard gate (Option A) provides an escape hatch.

**Watch for:** If Codex App Server starts using sequential integer request IDs (0, 1, 2...),
which resets per runtime, this collision becomes systematic for multi-job sessions.

## Conversation Highlights

**User's correction on deny semantics:**
"Important correction: in the current decide model, deny does not resume the agent and let
it try another path. For a pending escalation, deny finalizes the job as failed and closes
the runtime. So 'deny and see if the agent adapts' is not a real path unless the
implementation has changed since the review."

**User's recommendation on prompt tuning vs exec-policy:**
"For this ticket: prompt/objective tuning is the right path. For later: exec-policy amendment
support is worth designing, but only as a separate trust-boundary feature with explicit
approval semantics and tests."

**User's insistence on inspecting raw wire data:**
"Be careful saying the wire offered only deny. In the implementation we reviewed, the
caller-facing projection forces all command_approval and file_change escalations to
available_decisions == ('deny',). That means the /delegate rendering does not prove the raw
App Server availableDecisions was only deny."

**User's design criteria for Option A:**
"Allow /delegate discard for status == 'needs_escalation' and promotion_state is None.
But when discarding such a job, also: transition job to status='failed',
promotion_state='discarded' atomically if possible; release the runtime registry entry;
close the session if still present; mark lineage completed; emit discard audit."

**User's contract check on request status:**
"Do not equate PendingServerRequest.status == 'resolved' with plugin-level 'already
decided.' resolved is the wire lifecycle... Plugin-level deny can still be valid as the
user's local disposition."

## User Preferences

**Precision about state-machine semantics:** User insists on distinguishing wire lifecycle
from plugin-level semantics. Corrections were specific and technically precise.

**Both root-cause and defensive fixes:** User rejected "only Option B" and "only Option A"
in favor of both. Quote: "Option B prevents this exact trigger, but it does not give you a
safety valve for the current stuck job class or future state-machine mistakes."

**Explicit test requirements:** User provided a specific 8-test list with exact scenarios and
expected behaviors. Tests are not optional and must cover all edge cases.

**Scope discipline — fix the state machine, defer the trust model:** User cleanly separated
"state machine completeness" (in scope for this remediation) from "exec-policy amendment
handling" (separate design packet with its own contract questions).

## Next Steps

### 1. Clear stuck job and rerun live smoke (next session)

**Dependencies:** New session (restarts MCP server with updated code).

**Procedure:**
1. Run `/delegate` — should find stuck job `c382b5dc`
2. Run `/delegate discard` — new discard gate clears `needs_escalation` job
3. Run `/delegate Create docs/scratch/T-20260423-01-smoke.md with heading "Delegate Smoke
   Test" and one sentence with today's date`
4. Verify: no escalations for platform-tool commands within worktree
5. If agent still escapes worktree boundary (`find .. -name AGENTS.md`): that's the sandbox
   correctly blocking it, and with Option B the job fails cleanly. May need further prompt
   tuning or acceptance that the agent needs behavioral adjustment.

### 2. If smoke passes: commit and create PR

**Dependencies:** Successful live smoke (#1).

**Scope:** All uncommitted changes on `feature/delegate-remediation-sandbox-approval`:
- `server/runtime.py` — support roots (from predecessor)
- `server/delegation_controller.py` — state machine fixes
- `server/execution_prompt_builder.py` — prompt constraints
- `tests/test_delegation_controller.py` — 7 new + 1 updated tests
- `tests/test_runtime.py` — 5 support root tests (from predecessor)
- Plus test stubs and model changes from predecessor sessions

### 3. File separate ticket: exec-policy amendment support

**Dependencies:** None (can be filed now or after PR).

**Scope questions (from user):** Which binaries are eligible? Absolute path allowlist or
command-pattern amendment? Does it persist for session/job/turn? How is it represented in
`available_decisions`? Can `/delegate approve` become valid for command approvals? How to
prevent precedent for arbitrary Homebrew tools?

## In Progress

**State:** Code complete, tests passing, live smoke blocked by stale MCP server.

**Approach:** Both root-cause (Option B) and defensive (Option A) state-machine fixes
implemented in `delegation_controller.py`. Execution prompt tuned with platform-tool and
worktree-boundary constraints.

**Working:** 913 tests passing, ruff clean. Both fixes verified by unit tests covering all
specified scenarios. Diagnostic evidence preserved.

**Not working:** Live smoke cannot be verified this session — MCP server has old code.
Stuck job `c382b5dc` blocks new delegations via busy gate.

**Next action:** Start new session → discard stuck job → rerun live smoke.

## Open Questions

1. **Will the agent respect worktree-boundary instructions?** Smokes #1 and #2 both showed
   the agent trying to navigate above the worktree (`find .. -name AGENTS.md`). The prompt
   now prohibits this, but agent compliance is not guaranteed. If the agent continues
   escaping, the sandbox correctly blocks it and (with Option B) the job fails cleanly —
   but the delegation won't succeed.

2. **Should `_decided_request_ids` be scoped to collaboration_id, not session?** The
   namespace collision between jobs sharing `request_id: "0"` is a latent bug. The current
   discard gate provides an escape hatch, but the underlying collision remains.

3. **What is the `proposedExecpolicyAmendment` field for?** The wire payload includes this
   array of command tokens. It suggests the App Server has a mechanism for exec-policy
   amendments, but `available_decisions: []` means it's not offering amendment as an option.
   Understanding this field's semantics would inform the exec-policy ticket.

## Risks

1. **Agent worktree escape:** If the agent consistently tries to navigate above the worktree
   despite prompt instructions, every delegation will fail. Mitigated by: sandbox blocks the
   escape (correct behavior), Option B fails the job cleanly (no stuck state), and the
   objective can be further constrained.

2. **Stale MCP server pattern:** Every code change to the plugin requires a session restart
   to take effect. This is known (documented in memory) but makes iterative live testing
   slow. Each smoke attempt requires a new session.

## References

| What | Where |
|------|-------|
| Escalation diagnostic (raw payloads) | `docs/scratch/T-20260423-01-escalation-diagnostic.md` |
| Delegate remediation ticket | `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` |
| Implementation plan | `docs/plans/2026-04-23-delegate-remediation-implementation.md` |
| Predecessor checkpoint | `docs/handoffs/archive/2026-04-23_01-41_checkpoint-sandbox-support-roots-implemented.md` |
| Feedback: deny finalizes job | `memory/feedback_deny_finalizes_job.md` |
| Pending request store (this session) | `~/.claude/plugins/data/codex-collaboration-inline/pending_requests/40271cdd-a22e-4371-9fb7-bde4c4d44958/requests.jsonl` |

## Gotchas

- **Projection layer hides wire truth:** `_project_request_to_view` forces
  `_DENY_ONLY_DECISIONS` for `_CANCEL_CAPABLE_KINDS`. The `available_decisions` shown to the
  caller/user does NOT reflect what the App Server sent. Always check the raw
  `PendingServerRequest.available_decisions` (from the pending request store) for diagnostic
  purposes.

- **`_decided_request_ids` namespace collision:** Session-scoped set + non-unique wire
  request IDs (both jobs used `"0"`) = second job's deny blocked. The discard gate (Option A)
  is the escape hatch.

- **MCP server stale code:** Plugin Python process loads code at session start. Edits to
  `delegation_controller.py` (or any server file) require session restart to take effect.
  Live smoke testing always needs a fresh session after code changes.

## Verification Snapshot

```
uv run pytest packages/plugins/codex-collaboration/ → 913 passed in 18.70s
ruff check (changed files) → All checks passed!
git diff --check → clean (all changes uncommitted)
```
