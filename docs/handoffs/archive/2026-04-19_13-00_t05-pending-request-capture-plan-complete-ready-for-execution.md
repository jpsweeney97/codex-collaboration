---
date: 2026-04-19
time: "13:00"
created_at: "2026-04-19T17:00:23Z"
session_id: 2fa9c0c6-5bcb-4e0c-ac33-5d268daee03e
resumed_from: "docs/handoffs/archive/2026-04-19_00-45_t05-execution-start-complete-p1-fixes-landed-pending-request-capture-next.md"
project: claude-code-tool-dev
branch: feature/t05-pending-request-capture
commit: 5ee7afb4
title: "T-05 pending-request capture slice — plan complete, ready for execution"
type: handoff
files:
  - docs/plans/2026-04-19-t05-pending-request-capture-slice.md
  - packages/plugins/codex-collaboration/server/jsonrpc_client.py
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/approval_router.py
  - packages/plugins/codex-collaboration/server/pending_request_store.py
  - packages/plugins/codex-collaboration/server/execution_prompt_builder.py
  - packages/plugins/codex-collaboration/server/delegation_job_store.py
  - packages/plugins/codex-collaboration/server/execution_runtime_registry.py
---

# T-05 Pending-Request Capture Slice — Plan Complete, Ready For Execution

## Goal

Complete the collaborative design and plan writing for the T-05 pending-request capture slice (AC 6). This session continued from the execution-start slice completion handoff. The session's work was design and planning, not implementation.

**Trigger:** Prior handoff identified AC 6 (pending-request capture) as the next T-05 slice. The handoff's next steps said: "Read AC 6 text and the plan's deferral notes. Start planning the pending-request capture slice."

**Stakes:** AC 6 is the remaining acceptance criterion for T-05. Without it, execution-domain server requests are silently dropped by the runtime, making the delegation surface unusable for any non-trivial execution task. T-06 (`codex.delegate.poll`, `.decide`, `.promote`) and T-07 (turn dispatch) are blocked until T-05 closes.

**Success criteria (all met):**
1. Deep collaborative design discussion identifying four transport/control-flow/state/surface blockers
2. 8 frozen design decisions reached through multi-round adversarial refinement
3. Implementation plan written with 8 tasks, bite-sized TDD steps, and exact code
4. Plan saved to `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` on `feature/t05-pending-request-capture` branch

## Session Narrative

**Phase 1 — Handoff load and substrate survey (~20 min).** Loaded prior handoff. Read three key files identified in the handoff's next steps: AC 6 text at `tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md:323`, the plan's notification-loop deferral at `plans/2026-04-17-t05-execution-start-slice.md:4172`, and the approval router at `approval_router.py:37`. Then expanded the read set to cover the full execution path: `runtime.py` (notification loop and `run_execution_turn`), `execution_runtime_registry.py` (live session lookup), `delegation_controller.py` (start flow), `jsonrpc_client.py` (transport), `delegation_job_store.py` (persistence), `models.py` (data types), and the vendored App Server schemas (`ServerRequest.json`, `ServerNotification.json`, `TurnStartParams.json`, response schemas). This survey identified the three key substrate components (approval router parser, execution turn method, registry lookup) and three missing primitives (JSON-RPC respond, pending store, execution prompt builder).

**Phase 2 — Independent analysis and initial proposal (~15 min).** Synthesized findings into an architecture overview: the `_run_turn()` notification loop, the server-request vs notification distinction in JSON-RPC, the `needs_escalation` status existing but unused, the missing pieces. Proposed a 6-task sequence and identified the "interrupt on first request" design as the only shape fitting all constraints (App Server protocol, serialized MCP server, T-05-before-T-06 sequencing, fail-closed escalation model). Misidentified some approval policy values (said "always" / "byTool" — these don't exist in the schema).

**Phase 3 — First collaborative refinement (~20 min).** User provided a deeply structured counter-analysis identifying four explicit blockers ordered by dependency: transport (no `respond()`), control flow (single-threaded blocking), durable state (no store), execution input surface (no objective on tool). User's analysis was more precise than mine in several areas: correctly identified that the execution input surface must expand in this slice (not deferred), correctly noted that `approvalPolicy: "never"` is the switch that makes the entire capture flow live or dead, and correctly identified that the prompt/result contract is advisory-biased. User proposed a 6-item scope that was larger than my initial read.

**Phase 4 — Approval policy correction and response-shape widening (~15 min).** Verified the vendored `TurnStartParams.json` schema: actual values are `untrusted | on-failure | on-request | never` plus experimental `granular`. My earlier "always"/"byTool" were invented. Agreed on `on-request` as the honest stable v1 target with a probe gate. User raised two additions: (1) `approvalPolicy` must change from `"never"` for execution turns — the linchpin that makes server requests actually appear on the wire; (2) first `run_execution_turn()` dispatch should live inside `codex.delegate.start` (matching the dialogue precedent where `start` dispatches the first turn synchronously). Proposed 7-task sequence.

**Phase 5 — Permissions gap and three-signal await (~15 min).** User identified the most important structural gap: `cancel` is not universal across request kinds. Verified against vendored schemas: `CommandExecutionRequestApprovalResponse.json` and `FileChangeRequestApprovalResponse.json` both have `cancel` in their `decision` enum. `PermissionsRequestApprovalResponse.json` has only `{ permissions: GrantedPermissionProfile, scope?: "turn" | "session" }` — no cancel/decline. User pushed back on my blanket `needs_escalation` for permissions requests: if the turn completes successfully after a denied permission, escalation would be wrong. Accepted this — job status should be derived from terminal turn state for no-cancel requests, not from request arrival.

User also added `item/completed` as a third authoritative signal after cancel (beyond `serverRequest/resolved` and `turn/completed`). The docs at `codex-app-server.md:988` confirm `item/completed` is the authoritative result state. Three-signal await is the complete approach.

User raised the turn-journaling gap: the spec at `recovery-and-journal.md:49` already defines `turn_dispatch` as a journaled operation. Letting the first turn happen unjournaled without an explicit decision is a recovery-contract decision by omission. Accepted — made it an explicit task (design checkpoint).

**Phase 6 — PendingServerRequest lifecycle and final sequence lock (~10 min).** User identified the deepest model distinction: after we respond `cancel`, the wire request is CLOSED. `serverRequest/resolved` confirms closure. The stored `PendingServerRequest` is not a live wire request — it's a causal record explaining why the job is in `needs_escalation`. User's recommendation: keep `PendingServerRequest.status` as wire lifecycle (per spec at `recovery-and-journal.md:125-127`), treat `DelegationJob.status` as the plugin escalation signal, and use `DelegationEscalation` as the third typed start result. This avoids a spec amendment and cleanly separates wire state from plugin state. Accepted.

Final sequence locked at 8 tasks with three frozen points: approval policy is probe-gated, first execution turn is intentionally unjournaled, two capture strategies (not one).

**Phase 7 — Plan writing (~30 min).** Created `feature/t05-pending-request-capture` branch. Read remaining files for exact code references: tool definition in `mcp_server.py:100-116`, `_build_controller` pattern in `test_delegation_controller.py:96-140`, `DelegationJobStore` JSONL pattern. Wrote the plan at 1902 lines covering all 8 tasks with TDD steps, exact code blocks, and a risks/deferrals table encoding all design decisions.

## Decisions

### Decision 1: Two capture strategies based on request kind

**Choice:** Cancel-capable requests (command approval, file change) use `{"decision": "cancel"}` which interrupts the turn and unconditionally moves the job to `needs_escalation`. No-cancel requests (permissions, user-input, unknown) use minimal denial responses and derive job status from terminal turn state.

**Driver:** The permissions request response schema (`PermissionsRequestApprovalResponse.json`) has no `cancel` or `decline` field — only `{ permissions: GrantedPermissionProfile, scope? }`. Denial is by omission (`codex-app-server.md:1063`: "Any permissions omitted from `result.permissions` are treated as denied"). User-input responses (`ToolRequestUserInputResponse.json`) have only `{ answers: { ... } }` — also no cancel. So universal `cancel` is structurally impossible.

**Alternatives considered:**
- **Universal cancel for all request kinds** — rejected because the protocol doesn't support it for permissions and user-input requests. Implementing it would require protocol-level changes.
- **Ignore no-cancel requests** — rejected because the spec at `recovery-and-journal.md:132` says execution-domain unknown requests push the job to `needs_escalation`. All requests must be captured.
- **Blanket `needs_escalation` on any request arrival** — my initial proposal. User pushed back: "If the turn completes successfully after a denied permission, a blanket `needs_escalation` transition would be wrong." Accepted because the push-back is correct — job status should reflect actual turn outcome for no-cancel requests.

**Implications:** The capture loop has two code paths, not one. The notification loop continues running after a no-cancel denial (the turn may complete normally). State derivation happens after `turn/completed`, not at request capture time.

**Trade-offs accepted:** Two code paths are more complex than one. The no-cancel path has a weaker interrupt invariant (the turn may or may not self-terminate). Accepted because protocol honesty outweighs implementation simplicity.

**Confidence:** High (E2) — verified against vendored response schemas for all four request kinds. The `cancel` field exists only in `CommandExecutionApprovalDecision` and `FileChangeApprovalDecision`.

**Reversibility:** High — if a future App Server version adds `cancel` to permissions/user-input responses, the two-strategy design narrows to one.

**Change trigger:** App Server protocol adding `cancel` to permissions or user-input response schemas.

### Decision 2: `PendingServerRequest.status` is wire lifecycle, not plugin escalation

**Choice:** The `status` field on `PendingServerRequest` tracks the App Server wire request lifecycle (per spec at `recovery-and-journal.md:125-127`). After capture, the stored status is `"resolved"` because the wire request was responded to and confirmed by `serverRequest/resolved`. Plugin escalation is tracked by `DelegationJob.status == "needs_escalation"`.

**Driver:** User identified a real contract edge: `contracts.md` says `PendingServerRequest.status` is governed by Pending Request Ordering at `recovery-and-journal.md:125`, which says `serverRequest/resolved` is authoritative for closing approval and user-input prompts at `recovery-and-journal.md:127`. Repurposing `status` to mean plugin escalation would be a spec amendment.

**Alternatives considered:**
- **Repurpose `status` for plugin escalation** — my initial implicit assumption. Rejected because it conflicts with the existing spec contract. The spec says `serverRequest/resolved` drives status transitions, which means `status` is wire-scoped.
- **Add a second field (`escalation_status`)** — viable but adds a field to the dataclass that serves no v1 purpose. The job status already carries the escalation signal.

**Implications:** The stored `PendingServerRequest` is a causal record, not a live wire request. `codex.delegate.decide` (T-06) operates on `DelegationJob.status + stored request context`, not on a live wire request. The decide surface sends a new response to the App Server (if needed), not a response to the original closed request.

**Trade-offs accepted:** Conceptual indirection — "pending" in the type name is misleading after the wire request is resolved. Accepted because renaming the type would be a larger refactor and the docstring makes the distinction explicit.

**Confidence:** High (E2) — user cited the exact spec location; verified the contract text.

**Reversibility:** High — if the spec changes, the field semantics can change without affecting other components.

**Change trigger:** Spec amendment to `recovery-and-journal.md` changing `PendingServerRequest.status` semantics.

### Decision 3: First execution turn is intentionally unjournaled

**Choice:** The first execution turn dispatched inside `codex.delegate.start` is NOT journaled. `job_creation.completed` means "all durable start writes landed," not "turn finished." Turn dispatch happens after the journal is terminal.

**Driver:** User identified that the spec at `recovery-and-journal.md:49` already defines `turn_dispatch` as a journaled operation with its own idempotency key (`runtime_id + thread_id + turn_sequence`). Letting the first turn happen unjournaled without an explicit decision is a recovery-contract decision by omission — "the slice will smuggle in a recovery-contract decision by omission."

**Alternatives considered:**
- **Add `turn_dispatch` journaling now** — viable but adds significant scope. The full turn-dispatch journal path requires replay safety, idempotency, and recovery logic. Multi-turn dispatch and replay become real requirements only with T-06.
- **Silent omission** — rejected. User: "Without that sentence, the slice will smuggle in a recovery-contract decision by omission."

**Implications:** If the process crashes during the first turn window, startup reconciliation marks the job `unknown` via the existing `job_creation` journal path. The first execution turn is bounded by interrupt-on-first-request (should be short-lived). Turn-dispatch journaling lands with T-06.

**Trade-offs accepted:** A crash during the first turn loses the turn state. The window is small (first approval request triggers interrupt quickly), and recovery is handled by the existing `job_creation` path.

**Confidence:** High (E2) — recovery path verified against existing `recover_startup()` logic in `delegation_controller.py:496-566`.

**Reversibility:** High — adding journaling is additive, not a refactor.

**Change trigger:** T-06 (`codex.delegate.poll`) — where multi-turn dispatch makes turn journaling load-bearing.

### Decision 4: `on-request` approval policy with probe gate

**Choice:** Use `on-request` as the v1 approval policy target for execution turns. But the vendored schema proves allowed values, not operational semantics. Default to `untrusted` for the first proof if `on-request` doesn't generate server requests in a `workspaceWrite` sandbox.

**Driver:** The vendored `TurnStartParams.json:16-24` enumerates `untrusted | on-failure | on-request | never` plus experimental `granular`. `granular` requires `experimentalApi` in `initialize()`, which the current runtime doesn't enable (`runtime.py:61`). So `on-request` is the honest non-experimental candidate. But the repo has no documentation of what `on-request` actually prompts for.

**Alternatives considered:**
- **`untrusted`** — fail-closed stable choice. Would generate approval requests for everything. Viable as fallback.
- **`granular`** — richer policy control (`sandbox_approval`, `mcp_elicitations`, `rules`, `request_permissions`). Rejected because it's behind `experimentalApi`.
- **`never`** — current default. Suppresses all approval prompts. Rejected because it makes AC 6 impossible.

**Implications:** The plan's Task 8 includes an approval-policy probe as an early gate. If `on-request` doesn't trigger command execution approvals, the implementation defaults to `untrusted`.

**Trade-offs accepted:** `untrusted` may generate more approval requests than desired (every action, not just dangerous ones). But for v1, over-prompting is safer than under-prompting.

**Confidence:** Medium (E1) — the values are schema-verified but operational semantics are unverified.

**Reversibility:** High — the `approval_policy` parameter is passed through the stack and can be changed at runtime.

**Change trigger:** Live probe result during Task 8. Or App Server docs adding semantic descriptions for each policy value.

### Decision 5: No structured output schema for execution turns

**Choice:** Omit `outputSchema` for execution turns. The execution agent operates freely within the sandbox; its "output" is worktree state plus server requests, not a structured JSON blob.

**Driver:** `context_assembly.py` has execution token budgets (`_SOFT_TARGETS["execution"] = 12 * 1024`) but its `expected_output_shape` is the advisory consult-style schema (`position/evidence/uncertainties/follow_up_branches`). That schema is meaningless for execution. User: "That is effectively worse than having none."

**Alternatives considered:**
- **Advisory output schema for execution** — the current code path. Rejected because it constrains the execution agent's behavior for no benefit.
- **Execution-specific output schema** — viable but no v1 use case. The turn result is captured through the pending request mechanism and terminal turn status.

**Implications:** `_run_turn()` must make `outputSchema` optional (currently always sent at `runtime.py:197`). Advisory turns continue to use `CONSULT_OUTPUT_SCHEMA`.

**Trade-offs accepted:** Without an output schema, Codex's execution responses are unstructured text. Parsing them is not needed for v1 (the agent's work is in the worktree, not in the response).

**Confidence:** High (E2) — verified that the advisory schema is meaningless for execution context. User independently confirmed.

**Reversibility:** Medium — adding an output schema later requires updating `run_execution_turn()` and adding a parser.

**Change trigger:** If artifact extraction from execution turns needs structured output (likely T-06 or later).

### Decision 6: Third typed start result (`DelegationEscalation`)

**Choice:** `codex.delegate.start` returns three possible types: `DelegationJob` (clean completion), `DelegationEscalation` (server request captured), `JobBusyResponse` (already busy). `DelegationEscalation` is a separate dataclass containing the job, the pending request (causal record), and optional agent context.

**Driver:** User: "I would not bolt pending-request fields onto `DelegationJob`; that blurs persisted job state and escalation state." This is the same class of issue as the P1a replay validation bug from the execution-start slice — write-path structure diverging from read-path expectations.

**Alternatives considered:**
- **Add fields to `DelegationJob`** — rejected because `DelegationJob` is documented as persisted job lifecycle state (`models.py:307`). Adding transient escalation state to it blurs two concerns.
- **Composite wrapper** — a single `DelegationStartResult` containing both job and optional escalation data. Viable but the three-type union is cleaner at the wire level (each variant is structurally distinct for `asdict()` serialization).

**Implications:** MCP dispatch needs to handle three return types. The `DelegationEscalation` serialization includes `escalated: True` as a discriminator.

**Trade-offs accepted:** Three return types are more complex than two. But each type has distinct wire shape and semantics.

**Confidence:** High (E2) — precedent from dialogue domain (`DialogueStartResult` is also a distinct type from the persisted handle).

**Reversibility:** Medium — changing the return type requires updating callers (MCP dispatch, tests).

**Change trigger:** If `codex.delegate.poll` (T-06) also needs escalation data, the `DelegationEscalation` type may need to be reusable across both tools.

### Decision 7: Three-signal await after cancel

**Choice:** After sending `cancel`, the notification loop awaits three authoritative boundaries: `serverRequest/resolved` (wire cleanup), `item/completed` for the target `itemId` (item outcome), and `turn/completed` (terminal turn state).

**Driver:** The App Server docs are explicit that `item/completed` is the authoritative result state for each item (`codex-app-server.md:920`), including command approvals (`codex-app-server.md:988`). Waiting only for `serverRequest/resolved` + `turn/completed` would miss the item outcome.

**Alternatives considered:**
- **Two-signal await** (`serverRequest/resolved` + `turn/completed`) — my initial proposal. Rejected because it misses the item-level outcome.
- **Fire-and-forget** (`turn/completed` only, `serverRequest/resolved` as optional) — simpler but means the resolution confirmation is not verified.

**Implications:** The loop tracks `request_id` and `item_id` from the server request. After `turn/completed`, it verifies both matching signals were seen. Missing signals are treated as protocol errors.

**Trade-offs accepted:** The ordering of the three signals is not formally guaranteed in the protocol. The loop uses `turn/completed` as the exit condition; the other two are captured in the notifications list and verified post-exit.

**Confidence:** High (E2) — verified against App Server docs for command approval (`codex-app-server.md:980-988`) and file change approval flow.

**Reversibility:** High — relaxing to two-signal is a code deletion.

**Change trigger:** If protocol ordering guarantees are added to the App Server spec.

### Decision 8: Agent context is best-effort from authoritative completed items

**Choice:** Capture pre-interrupt agent context from `item/completed` notifications with `type: "agentMessage"` accumulated before the server request arrives. Stored as nullable `agent_context` field on `DelegationEscalation`.

**Driver:** The runtime already accumulates `agentMessage` text from `item/completed` notifications at `runtime.py:221`. The docs confirm completed items are authoritative (`codex-app-server.md:888`). If the approval request fires before any `agentMessage` item completes, there may be nothing to preserve.

**Alternatives considered:**
- **Capture delta/transcript snippets** — rejected. User: "I would not widen scope to experimental transcript deltas just to get more of it."
- **Skip agent context entirely** — viable for v1 but loses useful information about WHY the agent wanted to run the command.
- **Call it "reasoning"** — rejected. User: "I would call it something like `completed_agent_output` or `agent_context`, not 'reasoning.'"

**Implications:** The field is nullable and treated as supplemental. The primary payload is the request itself.

**Trade-offs accepted:** If no `agentMessage` items complete before the server request, the field is `None`. This is a real scenario — the agent may issue a command before producing any visible output.

**Confidence:** High (E2) — verified the accumulation mechanism at `runtime.py:221-226`.

**Reversibility:** High — the field is additive and nullable.

**Change trigger:** If execution turns consistently produce no `agentMessage` before the first approval request, the field may need widening to include delta text (but this contradicts D7's "authoritative only" principle).

## Changes

### `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` — Implementation plan

**Purpose:** Complete implementation plan for the T-05 pending-request capture slice. 1902 lines, 8 tasks with TDD steps.

**Approach:** Plan follows the `superpowers:writing-plans` skill format with bite-sized steps, exact code blocks, and test-first discipline. Each task produces self-contained changes that make sense independently.

**Key details:**
- Tasks 1-5 are clean primitives (independent, parallelizable in pairs)
- Task 6 is a design checkpoint (docstring-only)
- Task 7 is the composition task (capture loop, job transitions, agent context)
- Task 8 is the integration proof (E2E tests + approval-policy probe)
- 8 frozen design decisions in a header table
- Risks/deferrals table with 7 entries encoding all discussed concerns

## Codebase Knowledge

### Files read / key findings this session

| File | Lines | Purpose | Key finding |
|---|---|---|---|
| `server/approval_router.py` | 91 | Server request parser | `parse_pending_server_request()` projects raw App Server requests into `PendingServerRequest`. Maps 3 methods to kinds. `_AVAILABLE_DECISIONS` has fallback decision sets. `file_change` and `request_user_input` have empty decision tuples. |
| `server/runtime.py` | 264 | App Server runtime session | `run_execution_turn()` exists at line 158 but is never called. `_run_turn()` at line 177 hardcodes `approvalPolicy: "never"` at line 193 and always sends `outputSchema` at line 197. Raises if `status != "completed"` at line 235. `agentMessage` accumulated from `item/completed` at line 221. |
| `server/jsonrpc_client.py` | 175 | JSON-RPC transport | Can send client-initiated requests via `request()` at line 61. Has NO `respond()` method for server-initiated requests. Messages with `method` go to `_notification_backlog` regardless of whether they also have `id` (server requests). |
| `server/models.py` | ~340 | Data types | `PendingServerRequest` at line 219 with `PendingRequestStatus = Literal["pending", "resolved", "canceled"]`. `TurnExecutionResult` at line 122 has NO status field. `JobStatus` at line 21 includes `"needs_escalation"` but nothing sets it. `DelegationJob` at line 308 with `status` and `promotion_state`. |
| `server/delegation_controller.py` | 570 | Delegation start controller | `start()` at line 159. Three-phase journal discipline (intent → dispatched → committed-start → completed). Busy check consults three sources at line 219. Returns `DelegationJob | JobBusyResponse`. Does NOT dispatch execution turns. |
| `server/delegation_job_store.py` | 150 | JSONL job persistence | Append-only JSONL with `_replay()`. `_ACTIVE_STATUSES` at line 22 includes `needs_escalation`. `update_status()` at line 65 already supports any `JobStatus`. |
| `server/execution_runtime_registry.py` | 98 | Live runtime lookup | `lookup()` at line 79 returns `ExecutionRuntimeEntry(runtime_id, session, thread_id, job_id)`. `release()` at line 84 removes entry. |
| `server/mcp_server.py` | 347 | MCP server | Tool definition for `codex.delegate.start` at line 100 — only `repo_root` and `base_commit`. Dispatch at line 326 calls `controller.start()`. Single-threaded serialized dispatch. |
| `server/prompt_builder.py` | 115 | Advisory prompt builder | Only `build_consult_turn_text()` at line 40. `CONSULT_OUTPUT_SCHEMA` at line 10 is advisory-specific (position/evidence/uncertainties/follow_up_branches). No execution prompt builder. |
| `server/context_assembly.py` | ~300 | Context trimming | Execution profile has `_SOFT_TARGETS["execution"] = 12 * 1024` at line 14 and trim order at line 30. But `expected_output_shape` is the advisory consult schema, not execution-specific. |
| `tests/test_approval_router.py` | 149 | Router tests | 4 tests covering command, file change, unknown, and permissions parsing. Permissions intentionally mapped to `kind="unknown"` at line 116. |
| `tests/test_delegation_controller.py` | 964 | Controller tests | `_FakeSession`, `_FakeControlPlane`, `_FakeWorktreeManager` fakes. `_build_controller()` helper at line 96 returns 7-tuple. |

### App Server server request protocol (from vendored schemas)

| Request kind | Schema method | Response schema | Has `cancel`? | Our response |
|---|---|---|---|---|
| Command approval | `item/commandExecution/requestApproval` | `{ decision: CommandExecutionApprovalDecision }` | Yes | `{"decision": "cancel"}` |
| File change | `item/fileChange/requestApproval` | `{ decision: FileChangeApprovalDecision }` | Yes | `{"decision": "cancel"}` |
| User input | `item/tool/requestUserInput` | `{ answers: { [id]: { answers: string[] } } }` | No | `{"answers": {}}` |
| Permissions | `item/permissions/requestApproval` | `{ permissions: GrantedPermissionProfile, scope? }` | No | `{"permissions": {}}` |

### Approval policy values (from `TurnStartParams.json:16-24`)

| Value | Type | Notes |
|---|---|---|
| `untrusted` | Stable enum | Fail-closed; prompts for everything |
| `on-failure` | Stable enum | Prompts on failure (unclear semantics for execution) |
| `on-request` | Stable enum | Our v1 target (probe-gated) |
| `never` | Stable enum | Current default; suppresses all prompts |
| `granular` | Experimental object | Requires `experimentalApi` in `initialize()` |

### Architecture: execution turn dispatch flow (planned)

```
codex.delegate.start(repo_root, objective, base_commit?)
  │
  ├─ [Existing] Busy check → worktree → runtime bootstrap → journal (intent→dispatched→committed→completed)
  │
  └─ [NEW — Task 7] Post-journal turn dispatch:
       ├─ update_status(job_id, "running")
       ├─ build_execution_turn_text(objective, worktree_path)
       ├─ run_execution_turn(thread_id, prompt_text, sandbox_policy, approval_policy="on-request")
       │    └─ _run_turn() notification loop:
       │         ├─ Detect server request (message has `id` + `method`)
       │         ├─ server_request_handler callback:
       │         │    ├─ parse_pending_server_request()
       │         │    ├─ pending_store.create()
       │         │    └─ return cancel or minimal denial
       │         ├─ client.respond(request_id, response_payload)
       │         ├─ Accumulate agent_message from item/completed
       │         └─ Exit on turn/completed
       │
       ├─ Derive job status from turn outcome + captured request
       │    ├─ Cancel-capable + interrupted → needs_escalation
       │    ├─ No-cancel + not completed → needs_escalation
       │    ├─ No-cancel + completed → completed
       │    └─ No request + completed → completed
       │
       └─ Return DelegationJob | DelegationEscalation | JobBusyResponse
```

### Key locations

| Concept | Location |
|---|---|
| AC 6 text | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md:323` |
| Plan deferral note | `docs/plans/2026-04-17-t05-execution-start-slice.md:4172` |
| Turn-dispatch journaling spec | `recovery-and-journal.md:49` |
| Pending request ordering spec | `recovery-and-journal.md:125-127` |
| `parse_pending_server_request` | `server/approval_router.py:37` |
| `run_execution_turn` | `server/runtime.py:158` |
| `_run_turn` notification loop | `server/runtime.py:177-244` |
| `approvalPolicy` hardcoded | `server/runtime.py:193` |
| `outputSchema` always sent | `server/runtime.py:197` |
| Status check raises | `server/runtime.py:235` |
| `DelegationController.start` | `server/delegation_controller.py:159` |
| `_delegation_request_hash` | `server/delegation_controller.py:90` |
| Idempotency hash risk note | `docs/plans/2026-04-17-t05-execution-start-slice.md:4178` |
| `TurnExecutionResult` (no status) | `server/models.py:122` |
| `PendingServerRequest` model | `server/models.py:219` |
| `JobStatus` (includes needs_escalation) | `server/models.py:21` |
| `_ACTIVE_STATUSES` | `server/delegation_job_store.py:22` |
| MCP tool definition | `server/mcp_server.py:100-116` |
| MCP dispatch | `server/mcp_server.py:326-332` |
| `_build_controller` test helper | `tests/test_delegation_controller.py:96-140` |
| Implementation plan | `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` |

## Context

### Mental model

**Framing:** This session was a design discussion, not implementation. The core problem is connecting three existing seams (approval router, execution turn method, registry lookup) through a transport layer that doesn't exist yet (JSON-RPC respond) and a persistence layer that doesn't exist yet (pending request store), while respecting a protocol that has asymmetric cancel support across request kinds.

**Core insight from the discussion:** The interrupt-on-first-request design is not just a v1 simplification — it establishes the execution domain's trust model. The delegation job can never silently modify the worktree without Claude's knowledge. The two-strategy capture (cancel-capable vs no-cancel) is the honest encoding of this trust model given the protocol's asymmetry.

**Second core insight:** `PendingServerRequest.status` is wire lifecycle, not plugin lifecycle. This distinction prevents a model-level design bug where "pending" means two different things (pending on the wire vs pending Claude's decision). The stored request is a causal record; the job status is the escalation signal.

### Project state

- **T-05 execution-start slice:** COMPLETE on main at `7714870b` (merge) + `5ee7afb4` (P1 fixes). 666 tests.
- **T-05 pending-request capture slice:** PLANNED. Plan at `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` on `feature/t05-pending-request-capture`.
- **AC 6:** Still open. Will close when this slice is implemented and merged.
- **Sequencing:** pending-request capture → decide-surface + lifecycle → T-05 COMPLETE → T-06 → T-07.

### Environment snapshot

- Branch: `feature/t05-pending-request-capture` (created this session for the plan)
- Main: `5ee7afb4` (unchanged)
- Plugin suite: 666 tests (no implementation changes this session)
- Ruff: clean
- Plan file: 1902 lines

## Learnings

### Collaborative design catches seam bugs that solo analysis misses

**Mechanism.** The user identified four structural gaps my solo analysis missed: (1) permissions request has no `cancel` path, (2) `PendingServerRequest.status` lifecycle needs explicit spec-alignment, (3) first turn journaling is a recovery-contract decision not an omission, (4) `item/completed` is a third authoritative signal after cancel.

**Evidence.** Each gap was surfaced through adversarial refinement: I proposed something, the user challenged it with protocol evidence, I verified and accepted or counter-argued. The multi-round structure (4 rounds of substantive push-back) produced a design that is more honest than either participant would have reached alone.

**Implication.** For future design-heavy slices, run a structured collaborative discussion before planning. The discussion cost (~90 minutes) prevented what would have been P1-class findings in post-merge review.

### Protocol schemas are the authority, not prose docs

**Mechanism.** I invented approval policy values ("always", "byTool") from general knowledge. The user corrected: the vendored `TurnStartParams.json` schema at line 16-24 enumerates the actual values. The prose docs at `codex-app-server.md` show `unlessTrusted` in an example — doc/schema drift.

**Evidence.** Schema says `untrusted | on-failure | on-request | never` + experimental `granular`. Prose example says `unlessTrusted`. User: "I would not code from the prose example."

**Implication.** Always verify protocol details against vendored schemas. Prose docs may have drift. Schema is repo authority.

### Wire lifecycle vs plugin lifecycle must be explicitly decided

**Mechanism.** After responding `cancel`, the wire request is closed. The stored `PendingServerRequest` is not a live wire request — it's a causal record. If the status field tracks wire lifecycle, it should be `"resolved"` immediately after capture. If it tracks plugin lifecycle, it should be `"pending"` until `codex.delegate.decide`. These are different models with different implications for the decide surface.

**Evidence.** The spec at `recovery-and-journal.md:125-127` says `serverRequest/resolved` is authoritative for closing pending state. User: "If the plan repurposes `status` to mean plugin escalation lifecycle, that is effectively a spec amendment."

**Implication.** When a model field has both wire and plugin semantics, make the choice explicit and document which lifecycle it tracks. Don't let the ambiguity leak into the store.

## Next Steps

### 1. Execute the pending-request capture plan

**Dependencies:** Plan complete on `feature/t05-pending-request-capture`. Branch already exists.

**What to read first:** `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` — all 8 tasks with exact code.

**Approach:** Use `superpowers:subagent-driven-development` with full two-stage review (spec compliance + code quality) per task, plus post-merge integration review against the full slice diff. Same execution pattern as the execution-start slice.

**Task dependency order:**
- Tasks 1, 2 are independent primitives (parallelizable)
- Tasks 3, 4, 5 depend on Tasks 1-2 but are independent of each other
- Task 6 is a design checkpoint (docstring only, can run any time)
- Task 7 depends on Tasks 1-5
- Task 8 depends on Task 7

**Approval-policy probe (Task 8 early gate):** Run a live probe with `on-request` before the full E2E test. If `on-request` doesn't generate server requests for command execution in a `workspaceWrite` sandbox, default to `untrusted`.

### 2. Post-merge integration review (after all tasks pass)

**Dependencies:** All 8 tasks implemented and merged.

**What to do:** Run a full-slice integration review against the complete diff (all commits). This is the third review round that caught P1 bugs in the execution-start slice. Specifically look for cross-task seam issues: capture/store consistency, job-status/request-status consistency, handler/loop boundary correctness.

### 3. Remaining T-05 sequencing

After AC 6 closes:
- T-05 decide-surface + lifecycle refinements → T-05 COMPLETE
- T-06 (`codex.delegate.poll`, `.decide`, `.promote`)
- T-07 (turn dispatch)

### 4. Independent: T-20260416-01 extraction bug

Unchanged from prior handoffs. Independent of T-05 execution.

## In Progress

**Clean stopping point.** Design complete, plan written, no implementation changes made.

- **Completed:** Collaborative design discussion (4 rounds), 8 frozen design decisions, implementation plan (1902 lines, 8 tasks).
- **Not in flight:** No code changes. Plan is ready for execution.
- **Next action for next-session Claude:** Read the plan at `docs/plans/2026-04-19-t05-pending-request-capture-slice.md`. Execute using `superpowers:subagent-driven-development`. Start with Task 1 (JSON-RPC respond) or Task 2 (turn widening) — they're independent.

## Open Questions

### 1. `on-request` operational semantics

**Context.** The vendored schema proves `on-request` is a valid approval policy value. But the repo has no documentation of which action classes it prompts for. Does `on-request` mean "prompt for every tool use in the sandbox" or "prompt only when the agent explicitly requests elevated permissions"?

**Impact:** Medium. Determines whether the first execution turn generates server requests at all.

**Decision pending until:** Live probe in Task 8. If `on-request` doesn't trigger command approval requests, default to `untrusted`.

### 2. Notification ordering after cancel

**Context.** After sending `cancel`, the protocol should emit `serverRequest/resolved`, `item/completed`, and `turn/completed`. The ordering of these three signals is not formally guaranteed.

**Impact:** Low. The loop uses `turn/completed` as the exit condition and verifies the other two post-exit. Missing signals are protocol errors.

**Decision pending until:** Implementation. The two-signal-then-verify approach handles any ordering.

## Risks

### 1. `on-request` may not generate server requests

**Impact.** If `on-request` means "only prompt for explicit permission requests," command execution approvals won't fire and the capture flow is dead code.

**Mitigation.** Probe-gated design (D1). Default to `untrusted` if `on-request` doesn't work.

**Action.** Live probe in Task 8 before full E2E test.

### 2. Plan is 1902 lines — may have mechanical plan-gaps

**Impact.** The execution-start plan had mechanical plan-gaps in Tasks 1, 6, 7 (missing imports, missing attribute declarations). This plan may have similar issues.

**Mitigation.** Pre-identification pass before each task dispatch (same pattern as execution-start). Composition tasks (Tasks 7-8) are more likely to have gaps than primitives (Tasks 1-5).

**Action.** Implementer should verify all referenced symbols exist before implementing each task.

### 3. `_FakeSession` test doubles may need significant updates

**Impact.** Task 7 adds `run_execution_turn()` to `_FakeSession` and configurable server requests to `_FakeControlPlane`. The existing 964-line test file may need extensive updates to all test helpers.

**Mitigation.** Plan's Task 7 includes updated `_FakeSession` and `_FakeControlPlane` code. But existing tests that construct these fakes may break.

**Action.** Run full suite after each Task 7 step to catch breaks early.

## References

### Authority documents

| Document | Location | Role |
|---|---|---|
| T-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth (AC 6 at line 323) |
| T-05 execution-start plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` | Deferrals at line 4172 |
| T-05 pending-request plan | `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` | This slice's implementation plan |
| Recovery spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Turn-dispatch journaling (line 49), pending request ordering (line 125) |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Data model authority |

### Vendored schemas consulted

| Schema | Location | What it proved |
|---|---|---|
| `TurnStartParams.json` | `tests/fixtures/codex-app-server/0.117.0/v2/` | Approval policy values: `untrusted \| on-failure \| on-request \| never` + `granular` |
| `ServerRequest.json` | `tests/fixtures/codex-app-server/0.117.0/` | Server request methods: command, file change, user input, permissions, MCP elicitation, dynamic tool call |
| `CommandExecutionRequestApprovalResponse` | `tests/fixtures/codex-app-server/0.117.0/` | Cancel decision exists for command approvals |
| `FileChangeRequestApprovalResponse.json` | `tests/fixtures/codex-app-server/0.117.0/` | Cancel decision exists for file change approvals |
| `PermissionsRequestApprovalResponse.json` | `tests/fixtures/codex-app-server/0.117.0/` | NO cancel — response is `{ permissions, scope? }` only |
| `ToolRequestUserInputResponse.json` | `tests/fixtures/codex-app-server/0.117.0/` | NO cancel — response is `{ answers: { ... } }` only |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-19_00-45_t05-execution-start-complete-p1-fixes-landed-pending-request-capture-next.md`
- T-05 arc: execution-start slice COMPLETE → **pending-request capture PLANNED (this handoff)** → execute plan → decide-surface + lifecycle → T-05 COMPLETE

## Gotchas

### 1. `approvalPolicy: "never"` suppresses ALL approval prompts

**Symptom.** Execution turns with `approvalPolicy: "never"` never generate server requests — the approval router is dead code.

**Root cause.** `_run_turn()` at `runtime.py:193` hardcodes `"never"`. This is correct for advisory turns (read-only sandbox) but defeats AC 6 for execution turns.

**Prevention.** Task 3 adds `approval_policy` parameter to `run_execution_turn()` and `_run_turn()`. Execution turns use `"on-request"` (or `"untrusted"` as fallback).

### 2. `cancel` is not universal across request kinds

**Symptom.** Attempting to send `{"decision": "cancel"}` for a permissions request would be a protocol error — the response schema expects `{ permissions: GrantedPermissionProfile }`.

**Root cause.** Only command approval and file change approval responses have a `decision` enum with `cancel`. Permissions and user-input responses have different shapes.

**Prevention.** Two-strategy capture in Task 7. The handler checks `request.kind` and sends the appropriate response shape.

### 3. `TurnExecutionResult` currently has no status field

**Symptom.** Cannot distinguish completed from interrupted turns. `_run_turn()` raises on non-completed status.

**Root cause.** The model was designed for advisory turns which always complete. Execution turns can be interrupted (by cancel response) or fail.

**Prevention.** Task 2 adds `status` field and makes `_run_turn()` accept `interrupted`/`failed` as first-class outcomes.

### 4. `_run_turn()` always sends `outputSchema`

**Symptom.** Execution turns would receive advisory output schema constraints, potentially confusing the execution agent.

**Root cause.** `params["outputSchema"] = output_schema` at `runtime.py:197` is unconditional.

**Prevention.** Task 3 makes `output_schema` optional — only sent when not None.

## Conversation Highlights

### User's structured blocker analysis

The user provided a deeply structured analysis identifying four blockers in dependency order: transport → control flow → durable state → execution input surface. This was more precise than my initial analysis, which lumped some concerns together. The blocker ordering also dictated the task dependency chain.

### Permissions gap discovery

User: "There are two missing seams in your synthesis. First, `cancel` is not universal across request kinds. Command/file/user-input requests have an explicit cancel path. Permissions requests do not. Their response schema is only `{ permissions, scope? }`, with denial by omission."

This was the most important correction in the session — it split the capture loop from one strategy to two.

### Wire lifecycle vs plugin lifecycle

User: "There is a deeper model mismatch you have not named yet: `PendingServerRequest` on disk is not the same thing as what `codex.delegate.decide` will later resolve. If we respond `cancel`, the App Server request is closed. `serverRequest/resolved` confirms that closure. But later `codex.delegate.decide` is not going to send a second response to that same closed wire request."

This reframe prevented a model-level design bug.

### Blanket escalation push-back

User: "I would not mark `needs_escalation` unconditionally on a denied permissions request. [...] For permissions, I would persist the request and keep reading until terminal turn state. Only then decide whether the job is actually blocked and needs escalation."

Accepted — job status should reflect actual turn outcome for no-cancel requests.

### Journaling decision by omission

User: "Without that sentence, the slice will smuggle in a recovery-contract decision by omission."

Made explicit as Task 6 — a design checkpoint, not code.

## User Preferences

### Design discussion style

User engages in multi-round adversarial refinement. Each round: I propose → user challenges with protocol evidence → I verify and accept or counter-argue. The user's corrections are precise and evidence-backed (specific schema paths, spec line numbers, doc quotes). The user expects the same precision in return.

### "Probe for gaps" as an explicit request

When the user says "Probe for gaps," they want genuine adversarial analysis — not agreement followed by additional suggestions. They want me to find things their analysis missed.

### Protocol authority hierarchy

User treats vendored schemas as repo authority over prose docs. User: "I would not code from the prose example. I'd treat the vendored schema as the repo authority unless a live probe disproves it."

### Explicit decisions over silent omissions

User requires design decisions to be stated explicitly, even when the choice seems obvious. "Without that sentence, the slice will smuggle in a recovery-contract decision by omission." Every deferral must be documented as a conscious choice.

### Terse confirmation style sustained

User's confirmations are brief and decisive: "Mostly agree. The two additions are real." "Your updated read is mostly right." "Yes, this is ready to become a plan, with one condition."

## Rejected Approaches

### Universal cancel across all request kinds

**Approach.** Send `{"decision": "cancel"}` for every server request regardless of kind.

**Why it seemed promising.** One code path, one interrupt invariant, one state transition. Simpler to implement and reason about.

**Why rejected.** The permissions request response schema has no `cancel` field — only `{ permissions, scope? }`. User-input response schema has only `{ answers: { ... } }`. Sending a decision-style response to a permissions request would be a protocol error.

**What it taught.** Protocol schemas must be verified per request kind. The App Server's response shapes are asymmetric across request types.

### Bolting pending-request fields onto `DelegationJob`

**Approach.** Add `pending_request: PendingServerRequest | None` and `agent_context: str | None` directly to `DelegationJob`.

**Why it seemed promising.** Avoids a new type. Keeps the return type as `DelegationJob | JobBusyResponse`.

**Why rejected.** User: "I would not bolt pending-request fields onto `DelegationJob`; that blurs persisted job state and escalation state." `DelegationJob` is documented as persisted lifecycle state (`models.py:307`). Adding transient escalation data to it would be the same class of design bug as the P1a replay validation issue.

**What it taught.** Separate persisted lifecycle state from transient escalation state. Same principle as the write-path/read-path consistency that P1a violated.

### Blanket `needs_escalation` on any request arrival

**Approach.** Mark the job `needs_escalation` as soon as any server request is captured, regardless of the turn outcome.

**Why it seemed promising.** Simple invariant: "request captured = job needs escalation."

**Why rejected.** User: "For permissions, I would persist the request and keep reading until terminal turn state. Only then decide whether the job is actually blocked." If a denied permission doesn't prevent the turn from completing successfully, `needs_escalation` would be wrong.

**What it taught.** Job status should reflect actual turn outcome for no-cancel requests. The invariant is: "every request is persisted; job status reflects the turn's terminal state."
