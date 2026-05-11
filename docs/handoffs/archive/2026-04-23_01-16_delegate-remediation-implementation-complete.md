---
date: 2026-04-23
time: "01:16"
created_at: "2026-04-23T05:16:04Z"
session_id: 710b8418-4415-4215-8bf5-b04ce359d548
resumed_from: "docs/handoffs/archive/2026-04-23_00-33_delegate-remediation-plan-approved.md"
project: claude-code-tool-dev
branch: feature/delegate-remediation-sandbox-approval
commit: 005d4b44
title: "Delegate remediation — implementation complete, live smoke pending MCP restart"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/approval_router.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - packages/plugins/codex-collaboration/tests/test_runtime.py
  - packages/plugins/codex-collaboration/tests/test_approval_router.py
  - packages/plugins/codex-collaboration/skills/delegate/SKILL.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md
  - docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md
  - docs/plans/2026-04-23-delegate-remediation-implementation.md
---

# Delegate Remediation — Implementation Complete, Live Smoke Pending MCP Restart

## Goal

Execute the 13-step implementation plan from T-20260423-01 (delegate execution remediation)
to fix two compounding defects blocking live `/delegate` artifact production:

1. **Sandbox defect** — `includePlatformDefaults: False` in `runtime.py:33` blocks all shell
   execution in delegated Codex sessions
2. **Approval defect** — handler returns `cancel` (terminal) for all command/file approval
   requests, creating a cancel-retry loop when the caller later runs `decide(approve)`

**Trigger:** Predecessor session produced a scrutiny-tested implementation plan (5 rounds of
adversarial review, survived with "defensible" verdict). This session executes that plan.

**Stakes:** codex-collaboration has completed the T-02-T-07 arc (sole Codex integration), but
live `/delegate` cannot produce artifacts. This remediation is the bridge between
"infrastructure works" and "delegation actually produces results."

**Success criteria:** All plan steps executed, 901 tests passing, code review clean (one
blocker found and fixed), live-smoke verification pending MCP server restart.

**Connection to project arc:** Seventeenth session in the codex-collaboration build sequence.
Executes Phase 4-5 of T-20260423-01 (implementation + verification), following the diagnostic
and plan authoring of the sixteenth session.

## Session Narrative

**Phase 1 — Handoff load and plan review (~5 min).** Loaded predecessor handoff from the
diagnostic/plan session. Verified branch state: `feature/delegate-remediation-sandbox-approval`
at `005d4b44` (same as main), only the untracked plan file present. Read the full 645-line
implementation plan. No concerns raised — the plan was well-structured with explicit build
dependencies and code snippets.

**Phase 2 — Parallel execution of steps 1-5 (~3 min).** Created a 13-task dependency graph
matching the plan's build sequence. Launched 5 parallel agents for the independent steps:

- **Step 1 (sandbox policy):** One-line change in `runtime.py:33` (`False` -> `True`) + test
  update. Agent completed in 21s, 11 tests passing.
- **Step 2 (boundary validator):** Fixed stale `file_change` fallback from `()` to
  `("accept", "acceptForSession", "decline", "cancel")`. Added `is_within_delegation_boundary()`
  and `_is_path_within_boundary()` functions. Agent completed in 38s.
- **Step 3 (unit test fixtures):** Extended `_FakeSession` to record handler responses. Added
  3 new fixtures: `_command_approval_with_network_context`, `_file_change_request`,
  `_file_change_with_out_of_worktree_grant_root`. Agent completed in 54s.
- **Step 4 (integration test fixtures):** Extended `_ConfigurableStubSession` response recording.
  Added `_command_approval_with_network_context_msg`. Agent completed in 45s.
- **Step 5 (rejection reason):** Added `"request_not_approvable"` to `DecisionRejectedReason`
  Literal and contracts enum. 881 tests passing. Agent completed in 51s.

All 5 verified — spot-checked boundary validator logic, confirmed test counts.

**Phase 3 — Sequential execution of steps 6-9 (~15 min).** These required direct implementation
due to cross-file dependencies:

- **Step 6 (handler restructure):** Core change. Promoted `_CANCEL_CAPABLE_KINDS` and
  `_KNOWN_DENIAL_KINDS` to module level. Restructured `_server_request_handler` closure: added
  `inline_accepted_requests` list, implemented boundary check + accept/cancel decision tree.
  Key invariant: `captured_request` only set when handler escalates (cancel). Inline-accepted
  requests tracked separately.
- **Step 7 (finalize-turn audit):** Added `_emit_inline_accept_audit` helper method and
  `inline_accepted_requests` parameter to `_finalize_turn`. Audit emitted at top of
  `_finalize_turn` before state-transition logic.
- **Step 8 (decide guard):** Added cancel-capable guard in `decide()`: if `decision == "approve"`
  and `request.kind in _CANCEL_CAPABLE_KINDS`, return `_reject_decision` with reason
  `"request_not_approvable"`. Placed after answers validation, before runtime lookup.
- **Step 9 (view projection):** Added `_DENY_ONLY_DECISIONS = ("deny",)` class variable.
  Updated `_project_request_to_view` to use `_DENY_ONLY_DECISIONS` for cancel-capable kinds.

Each step verified with syntax check and import validation.

**Phase 4 — Parallel execution of steps 10-11 (~2 min).** Launched two agents:

- **Step 10 (skill UX):** Updated SKILL.md decision prompt to render dynamically from
  `available_decisions`. Added approve pre-call guard. Updated Gate 2 description. Mirrored
  changes in design spec. Agent completed in 95s.
- **Step 11 (ticket AC):** Updated acceptance criterion 2 to reflect inline-accept model.
  Agent completed in 19s.

**Phase 5 — Test execution, step 12 (~12 min).** The largest step. Launched two parallel agents:

- **Step 12a (unit tests):** 20 existing tests updated (12 fixture swaps, 2 inline-accept
  expectation updates, 5 redesigns switching to `_permissions_request()` for approve path,
  1 additional fix discovered by agent). 18 new tests added (T2-T19 from plan, minus T1
  which was step 1, plus T11 already existed). 116 unit tests passing. Agent completed in ~10 min.
- **Step 12b (integration tests):** 7 existing tests updated (6 fixture swaps, 1 redesign
  switching to `_permissions_request_msg()` for re-escalation approve path). 1 test renamed
  to reflect new behavior. 18 integration tests passing. Agent completed in ~3 min.

Full suite: 898 tests passing (881 → 898, +17 net).

**Phase 6 — Code review and parser fix (~5 min).** User ran a code review that found one
blocker: malformed `availableDecisions` (e.g., string instead of list) now falls through to
the permissive schema defaults containing `accept`, which is safety-relevant now that `accept`
gates inline approval.

Fixed `_resolve_available_decisions` in `approval_router.py:102-110`: distinguished "field
absent" (use schema defaults) from "field present but malformed" (fail closed with empty tuple).
Added 2 new parser tests and 1 new handler-level test. Full suite: 901 tests passing.

**Phase 7 — Live smoke attempt (~3 min).** Started a live delegation with a file-creation
objective. The delegation ESCALATED with a `command_approval` — but the request was in-boundary
(cwd = worktree path, no networkApprovalContext). The escalation view showed
`available_decisions: ["approve", "deny"]` instead of `["deny"]`.

**Diagnosis:** `/reload-plugins` refreshes plugin metadata but does NOT restart MCP server
processes. The codex-collaboration MCP server is a long-running Python process that imported
modules at session start. Code changes require MCP server restart to take effect. Denied the
escalation, discarded the job, saved this handoff.

## Decisions

### D1: Subagent-parallel execution for independent plan steps

**Choice:** Dispatched steps 1-5 as 5 parallel background agents, steps 10-11 as 2 parallel
agents, and step 12 as 2 parallel agents (unit + integration tests).

**Driver:** The plan explicitly identified steps 1-5 as independent with no cross-dependencies.
Parallelization reduced wall-clock time from ~15 min sequential to ~3 min.

**Alternatives considered:**
- **Sequential execution** — rejected for time efficiency; no shared state between steps 1-5.
- **Single agent for all 5** — rejected because each step touches different files with no
  coordination needed.

**Trade-offs accepted:** Higher token cost (5 agent contexts vs 1). Accepted because wall-clock
savings were substantial and the task descriptions were precise enough to avoid rework.

**Confidence:** High (E2) — all 5 agents completed successfully with zero conflicts.

**Reversibility:** N/A — execution strategy, not code design.

**Change trigger:** If agents produce conflicting edits to the same file.

### D2: Malformed availableDecisions fails closed (empty tuple)

**Choice:** When `availableDecisions` is present in the wire payload but malformed (not a
list of strings), return empty tuple instead of schema defaults.

**Driver:** Code review finding — the handler now uses `"accept" in parsed.available_decisions`
as a security gate. Malformed values falling through to permissive defaults would bypass the
gate. Reviewer: "A bad or drifted App Server payload like `availableDecisions: 'cancel'`
therefore becomes a tuple containing accept."

**Alternatives considered:**
- **Keep existing behavior (fall through to defaults)** — rejected because defaults contain
  `accept`, which is now safety-relevant. A drifted App Server payload would silently auto-approve.
- **Raise an exception** — rejected because parse failures already have an escalation path
  (the unknown-kind handler). Empty tuple makes the handler fail closed (cancel) without
  interrupting the parse pipeline.

**Trade-offs accepted:** If the App Server legitimately sends a non-standard
`availableDecisions` format, the handler will fail closed (cancel instead of accept). This is
the correct behavior for a security gate.

**Confidence:** High (E2) — confirmed with test that `availableDecisions: "cancel"` (string)
previously produced the permissive fallback. New test confirms empty tuple.

**Reversibility:** High — one conditional change in `_resolve_available_decisions`.

**Change trigger:** If App Server documentation defines additional valid formats for
`availableDecisions` beyond JSON array of strings.

## Changes

### `server/runtime.py:33` — Sandbox policy

One-line change: `"includePlatformDefaults": False` → `True`. Enables curated platform-default
Seatbelt policy for restricted-read sessions. Shell execution now functional in delegated
sessions.

### `server/approval_router.py` — Boundary validator + parser fix

1. Fixed stale `file_change` fallback from `()` to `("accept", "acceptForSession", "decline", "cancel")`
2. Added `is_within_delegation_boundary(parsed, worktree_path)` — checks `networkApprovalContext`,
   `cwd`, and `grantRoot` against worktree boundary
3. Added `_is_path_within_boundary(value, worktree_path)` — path validation helper
4. Fixed `_resolve_available_decisions` to fail closed on malformed `availableDecisions`

### `server/delegation_controller.py` — Handler restructure + state machine

1. Promoted `_CANCEL_CAPABLE_KINDS` and `_KNOWN_DENIAL_KINDS` to module level (line 110-111)
2. Restructured `_server_request_handler` closure with three-category response model
3. Added `inline_accepted_requests` list in handler closure
4. Added `_emit_inline_accept_audit` helper method
5. Added `inline_accepted_requests` parameter to `_finalize_turn`
6. Added `decide(approve)` guard for cancel-capable kinds (returns `request_not_approvable`)
7. Added `_DENY_ONLY_DECISIONS` class variable
8. Updated `_project_request_to_view` for kind-based available_decisions

### `server/models.py` — Rejection reason

Added `"request_not_approvable"` to `DecisionRejectedReason` Literal (10th value).

### `contracts.md:297` — Contract enum

Added `request_not_approvable` to the caller-facing `Decision Rejection.reason` enum.

### `SKILL.md` — Dynamic available_decisions

1. Decision prompt renders dynamically from `pending_escalation.available_decisions`
2. Approve verb has pre-call guard checking availability
3. Gate 2 updated to note decisions depend on escalation kind

### Design spec — Mirrored skill UX changes

`docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md` updated to match SKILL.md.

### Ticket AC — Criterion 2 updated

Acceptance criterion 2 now reflects inline-accept model instead of `decide(approve)` grant.

### Test files — 20 net new tests

| File | Existing Updated | New Tests | Total |
|------|-----------------|-----------|-------|
| `test_delegation_controller.py` | 21 | 19 | 116 |
| `test_delegate_start_integration.py` | 7 | 0 | 18 |
| `test_runtime.py` | 1 | 0 | 11 |
| `test_approval_router.py` | 0 | 3 | 7 |

## Codebase Knowledge

### Files Read This Session

| File | Why | Key Finding |
|------|-----|-------------|
| `runtime.py:22-37` | Confirm sandbox defect target | `build_workspace_write_sandbox_policy`: `includePlatformDefaults: False` is the one-line fix |
| `approval_router.py:1-110` | Understand decision resolution | `_AVAILABLE_DECISIONS["file_change"]` was `()` — stale. `_resolve_available_decisions` falls through to defaults for any non-list value |
| `models.py:37-48` | Locate rejection reason enum | `DecisionRejectedReason` is a 9-value Literal at module level |
| `delegation_controller.py:640-760` | Handler restructure target | `_server_request_handler` closure, `_CANCEL_CAPABLE_KINDS` local, unconditional cancel for all cancel-capable kinds |
| `delegation_controller.py:1450-1535` | Finalize-turn logic | `_finalize_turn`: line 1473 checks `captured_request.kind in _CANCEL_CAPABLE_KINDS` — kind-based, not outcome-based |
| `delegation_controller.py:1551-1760` | Decide method | Full approve/deny path. Approve starts NEW turn (line 1748-1754), doesn't grant original request |
| `delegation_controller.py:847-870` | View projection | `_PLUGIN_DECISIONS = ("approve", "deny")` used unconditionally for all views |
| `contracts.md:289-301` | Contract enum location | Line 297: `reason` enum in markdown table format (grep misses it) |
| `test_delegation_controller.py:43-112` | `_FakeSession` infrastructure | `run_execution_turn` dispatches fake server requests, discards handler return values |
| `test_delegation_controller.py:1260-1320` | Fixture shapes | `_command_approval_request()` (request_id=42), `_permissions_request()` (request_id=99) |
| `test_delegate_start_integration.py:191-239` | `_ConfigurableStubSession` | Same pattern — dispatches requests, discards responses |
| `test_runtime.py:167-183` | Sandbox policy test | Asserts `includePlatformDefaults: False` — needed update to `True` |

### Handler Architecture (After Fix)

| Component | File:Line | Purpose |
|-----------|-----------|---------|
| Module constants | `delegation_controller.py:110-111` | `_CANCEL_CAPABLE_KINDS`, `_KNOWN_DENIAL_KINDS` (promoted from local) |
| Handler closure | `delegation_controller.py:652-730` | Three-category: inline accept, fail closed, unknown/interrupt |
| Inline accept list | `delegation_controller.py:645` | `inline_accepted_requests: list[PendingServerRequest]` |
| Boundary validator | `approval_router.py:113-138` | `is_within_delegation_boundary(parsed, worktree_path)` |
| Path validator | `approval_router.py:141-157` | `_is_path_within_boundary(value, worktree_path)` |
| Audit helper | `delegation_controller.py:1451-1479` | `_emit_inline_accept_audit` — best-effort, actor="system" |
| Decide guard | `delegation_controller.py:1698-1708` | Rejects approve for cancel-capable kinds |
| View projection | `delegation_controller.py:858-876` | Kind-based `_DENY_ONLY_DECISIONS` vs `_PLUGIN_DECISIONS` |

### Approval Flow (After Fix)

```
Agent requests command_approval/file_change
  -> _server_request_handler validates scope via is_within_delegation_boundary()
  -> In-boundary + accept in available_decisions:
      return {"decision": "accept"} -> App Server resumes inline
      Request appended to inline_accepted_requests (NOT captured_request)
      _finalize_turn: captured_request is None -> completed
      Job completes with artifacts
  -> Out-of-boundary OR accept not available:
      return {"decision": "cancel"} -> turn interrupted
      captured_request set -> _finalize_turn -> needs_escalation
      View advertises ("deny",) only
      decide(approve) returns DecisionRejectedResponse(reason="request_not_approvable")
```

### Test Fixture Disposition Pattern

When a security boundary changes, every test using the old fixture needs explicit triage:

| Disposition | Count | Pattern |
|-------------|-------|---------|
| Fixture swap (escalation preserved) | 12 unit + 6 integ | `_command_approval_request()` -> `_command_approval_with_network_context()` |
| Inline-accept expectation flip | 2 unit | Result changes from `DelegationEscalation` to `DelegationJob` |
| Redesign (approve path invalid) | 6 unit + 1 integ | Switch to `_permissions_request()` (unknown kind, approve valid) |
| Mixed (first accepted, second escalates) | 1 unit | Parse-failure test with inline-accept first request |

## Context

### Project State

T-02 through T-07 arc complete. T-20260423-01 Phase 4 (implementation) complete. Phase 5
(live verification) blocked on MCP server restart.

| Ticket | Status | Phase | Key Artifact |
|--------|--------|-------|-------------|
| T-20260423-01 | Open | Phase 4 complete, Phase 5 blocked | Implementation plan + all code changes |

### Mental Model

This is a **security boundary calibration** problem. The T-05 hardening chose maximally
restrictive defaults for both sandbox and approval. That was correct when execution was
unverified. Now that T-07 proved the pipeline works, the boundary shifts from "deny by
default" to "allow within boundary."

The core insight: `cancel` in App Server approval is **terminal** — it denies and interrupts
the turn. Using it for requests intended for later approval creates the cancel-retry loop.
The fix accepts inline where safe and rejects approve where unsafe, rather than deferring
everything.

### Two-Layer Security Model

- **Sandbox mode**: What Codex CAN do (filesystem, network)
- **Approval policy**: When Codex must ASK before acting

For delegation, the sandbox IS the approval — the agent operates in an isolated worktree with
no network. The caller's review happens at **promote**, not at individual command approval.

## Learnings

### `/reload-plugins` does not restart MCP server processes

**Mechanism:** `/reload-plugins` refreshes plugin metadata (skills, hooks, commands, agent
definitions) but does NOT restart long-running MCP server subprocesses. The codex-collaboration
MCP server imports Python modules at startup; source changes don't take effect until restart.

**Evidence:** Live smoke attempt showed old handler behavior (unconditional cancel,
`available_decisions: ["approve", "deny"]` instead of `["deny"]`) after `/reload-plugins`
reported success.

**Implication:** After changing plugin MCP server source code, restart the Claude Code session
or use `claude mcp remove` + `claude mcp add-json` to restart the specific server.

### Malformed `availableDecisions` is now safety-relevant

**Mechanism:** Before the handler restructure, `available_decisions` was informational — the
handler always returned `cancel`. Now it's a security gate: `"accept" in parsed.available_decisions`
gates inline approval. A malformed value falling through to permissive schema defaults would
bypass the gate.

**Evidence:** Code review finding confirmed by test: `availableDecisions: "cancel"` (string
instead of list) previously produced the fallback tuple containing `accept`.

**Implication:** The parser must distinguish "field absent" (use defaults) from "field present
but malformed" (fail closed). Applied this principle to `_resolve_available_decisions`.

### grep misses markdown table content

**Mechanism:** `rg -n "pattern"` and `rg -in "pattern"` returned no results for the
`DecisionRejectedReason` enum in `contracts.md` because the enum values are inline in a
markdown table cell on a single long line.

**Evidence:** Five `rg` attempts with different patterns returned empty. Only reading the
file at the known line offset (280-300) found the content.

**Implication:** When searching markdown specs for enum values or inline content, read the
known section rather than relying on grep.

## Next Steps

### 1. Restart MCP server and retry live smoke

**Dependencies:** Fresh Claude Code session (MCP server restart).

**What to do:**
1. Start new Claude session (restarts MCP server with updated code)
2. Run `/delegate` with the same objective: "Create `docs/scratch/T-20260423-01-smoke.md`
   with heading 'Delegate Smoke Test' and date description"
3. Verify job completes WITHOUT `command_approval`/`file_change` escalation
4. Poll for artifacts: `full.diff` non-empty, `changed_files` non-empty, `artifact_hash` stable
5. Promote or discard (artifacts prove execution capability)

**Expected outcome:** Job completes inline (handler returns `accept` for in-boundary commands).
No escalation for shell commands within the worktree.

**If escalation still occurs:** Check the escalation kind and `cwd`/`networkApprovalContext` —
the request may be out-of-boundary for a reason not anticipated. Record the diagnostic evidence.

### 2. Commit changes and create PR

**Dependencies:** Live smoke passing (step 1).

**What to commit:** All modified files are unstaged. The plan file `docs/plans/2026-04-23-delegate-remediation-implementation.md` should also be committed (it's the implementation blueprint).

**PR title:** `fix(delegate): inline-accept in-boundary approvals, reject approve for cancel-capable kinds`

### 3. Fix T-20260416-01 (dialogue reply extraction mismatch)

**Dependencies:** Independent of delegate remediation.

**Context:** `codex.dialogue.reply` items-array extraction mismatch. Narrower and less
strategically blocking than delegate remediation.

## In Progress

**Clean stopping point.** All code changes implemented and tested. 901 tests passing. Code
review blocker fixed. No code changes in flight.

**Immediate next action:** Restart Claude session to get the MCP server running with updated
code, then retry the live smoke.

**State:** All changes are unstaged (no commits made this session). Branch is at `005d4b44`
(same as main). The only untracked file present at session start was the plan; now there are
many modified files.

## Open Questions

### 1. Does `approval_policy="untrusted"` still emit approval requests after the sandbox fix?

**Context:** With `includePlatformDefaults: True`, the sandbox allows shell execution. But
`untrusted` policy may still prompt for every command. The handler auto-accepts in-boundary
requests inline, so this creates round-trips but is functional.

**Decision pending until:** Live-smoke verification.

### 2. What exactly does the curated platform-default Seatbelt set include?

**Context:** OpenAI docs say "curated" but don't enumerate the paths. If the delegated agent
can execute shell commands (proven by live smoke), the curated set is sufficient.

**Decision pending until:** Live-smoke verification.

## Risks

### 1. MCP server restart may reveal additional issues

The live smoke was the first real test of the new code against the App Server. The old-code
escalation confirmed the wire protocol works (request came through, handler responded). But
the new code path (inline accept) hasn't been tested against a live App Server yet. Potential
issues: App Server version incompatibilities, authentication state, worktree initialization.

### 2. Unstaged changes are at risk

All changes are unstaged. If the worktree is accidentally reset or the branch is force-pushed,
the work would be lost. Recommend committing after live smoke passes.

### 3. Platform-dependent sandbox behavior

`includePlatformDefaults: True` behavior is macOS-specific. Linux sandbox may behave
differently. Cross-platform verification is deferred.

## References

### Authority Documents

| Document | Location | Role |
|----------|----------|------|
| Implementation plan | `docs/plans/2026-04-23-delegate-remediation-implementation.md` | Execution blueprint (13 steps) |
| T-20260423-01 ticket | `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` | Ticket scope and AC |
| Contracts spec | `docs/superpowers/specs/codex-collaboration/contracts.md` | Caller-facing rejection enum |
| Delegate skill UX design | `docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md` | Approve/deny UX flow |

### Prior Handoffs (Chain)

- Immediate predecessor: `docs/handoffs/archive/2026-04-23_00-33_delegate-remediation-plan-approved.md`
- Arc: ... -> T-07 7e PR -> merge + delegate ticket -> diagnostic + plan -> **implementation (this handoff)**

## Gotchas

### 1. `/reload-plugins` does not restart MCP server processes

Plugin metadata refreshes but MCP server subprocesses keep running with stale code. Must
restart the Claude session or the specific MCP server to pick up Python changes.

### 2. `_command_approval_request()` fixture is now in-boundary

Under the new model, this fixture (no `networkApprovalContext`, no `cwd`, no `grantRoot`) is
in-boundary and will be inline-accepted. Tests expecting escalation must use
`_command_approval_with_network_context()`.

### 3. `decide(approve)` is now rejected for command_approval and file_change

Tests that test the approve-resume path must use `_permissions_request()` (unknown kind,
approve still valid). The approve path still works for unknown and request_user_input kinds.

### 4. grep misses markdown table inline content

`rg` returns empty for enum values embedded in markdown table cells. Read the known section
offset instead of grepping.

### 5. Unstaged changes — commit after live smoke

All 901-test-passing changes are unstaged. Branch is at the same commit as main. Do not reset
the worktree before committing.

## User Preferences

### Code review before live smoke

User ran a code review before the live smoke, catching the malformed `availableDecisions`
parser issue. This aligns with the prior session's pattern: diagnostic-first, scrutiny before
execution.

### Commit after verification, not during implementation

User did not ask to commit during implementation — the plan was to complete all steps, verify,
then commit. Live smoke is the final verification gate before commit/PR.
