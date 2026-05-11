---
date: 2026-04-23
time: "00:33"
created_at: "2026-04-23T04:33:01Z"
session_id: a78f76f0-23d2-41d7-82b5-a7c7ee84370c
resumed_from: "docs/handoffs/archive/2026-04-23_00-15_t07-merged-delegate-ticket-opened.md"
project: claude-code-tool-dev
branch: feature/delegate-remediation-sandbox-approval
commit: 005d4b44
title: "Delegate remediation — diagnostic complete, implementation plan approved"
type: handoff
files:
  - docs/plans/2026-04-23-delegate-remediation-implementation.md
  - docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/approval_router.py
  - packages/plugins/codex-collaboration/server/execution_prompt_builder.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - packages/plugins/codex-collaboration/tests/test_runtime.py
  - packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/CommandExecutionRequestApprovalResponse.json
  - packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/CommandExecutionRequestApprovalParams.json
  - packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/FileChangeRequestApprovalResponse.json
  - packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/FileChangeRequestApprovalParams.json
  - packages/plugins/codex-collaboration/skills/delegate/SKILL.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md
---

# Delegate Remediation — Diagnostic Complete, Implementation Plan Approved

## Goal

Complete Phase 1-3 of T-20260423-01 (delegate execution remediation): diagnose the
sandbox and approval defects blocking live `/delegate` artifact production, then produce
a scrutiny-tested implementation plan ready for execution.

**Trigger:** Predecessor handoff left PR #124 (delegate remediation ticket) open. This
session merged PR #124, then performed the diagnostic investigation and plan authoring
that the ticket's Phase 1-3 sequence requires.

**Stakes:** codex-collaboration has cut over as the sole Codex integration (T-02–T-07 arc
complete), but live `/delegate` still cannot produce artifacts because shell execution is
sandbox-blocked and approval responses use the wrong wire semantics. This session's plan
is the bridge between "infrastructure works" and "delegation actually produces results."

**Success criteria:** Diagnostic findings grounded in official docs and empirical tests;
implementation plan that survives adversarial scrutiny; plan addresses all caller-facing
surfaces (runtime, views, rejections, skill UX, contracts, tests).

**Connection to project arc:** Sixteenth session in the codex-collaboration build
sequence. Closes the T-02–T-07 arc's final gap (PR #124 merged) and produces the
execution plan for the post-T-07 remediation arc (T-20260423-01 Phases 4-5).

## Session Narrative

**Phase 0 — Handoff load and PR #124 merge (~5 min).** Loaded predecessor handoff from
the T-07 closeout session. Clean state: PR #124 open at `82121adf` on
`chore/delegate-remediation-ticket`. Merged PR #124 via `gh pr merge --merge
--delete-branch`, pulled to main at `005d4b44`, deleted local branch. Created working
branch `feature/delegate-remediation-sandbox-approval` from main.

**Phase 1 — Sandbox diagnostic (~20 min).** Read `runtime.py:22-37` to confirm
`includePlatformDefaults: False` in `build_workspace_write_sandbox_policy`. Searched
the vendored 0.117.0 schemas — `includePlatformDefaults` is NOT in the vendored
protocol schemas (it's a consumer-side config, not a published wire field). Found the
schemas had moved from `tests/fixtures/` to `packages/plugins/codex-collaboration/
tests/fixtures/` after cross-model removal.

Searched OpenAI developer docs via MCP: found the authoritative description at
`developers.openai.com/codex/app-server#sandbox-read-access-readonlyaccess`: "On macOS,
`includePlatformDefaults: true` appends a curated platform-default Seatbelt policy for
restricted-read sessions. This improves tool compatibility without broadly allowing all
of `/System`."

Ran empirical sandbox tests with `codex sandbox macos`:
- `--full-auto` mode (uses `readOnlyAccess: fullAccess` by default): allows reading
  `~/.ssh/`, `~/.config/gh/hosts.yml` — MORE permissive than our target
- `--full-auto` with explicit path tests: `/usr/bin` OK, `~/.config/gh` OK, `~/.ssh/`
  listable, `~/.aws/` DIR NOT FOUND (not denied)
- `--log-denials` showed only dtrace/mach-lookup write denials, no read denials

Key insight: the initial `~/.ssh: DENIED` result was file-not-found, not sandbox denial.
The `--full-auto` sandbox allows reading the entire filesystem because it uses
`readOnlyAccess: fullAccess` by default. Our `restricted` mode is more restrictive by
design — `includePlatformDefaults: True` adds a curated set, not full access.

**Phase 2 — Approval API diagnostic (~15 min).** Read
`delegation_controller.py:650-720` (the `_server_request_handler` closure),
`delegation_controller.py:1743-1754` (the `decide(approve)` path),
`execution_prompt_builder.py:41-77` (the resume prompt), and
`delegation_controller.py:246` (`approval_policy` defaults to `"untrusted"`).

Read the vendored approval response schemas:
- `CommandExecutionRequestApprovalResponse.json`: `accept` = "User approved the
  command", `cancel` = "User denied the command. The turn will also be immediately
  interrupted."
- `FileChangeRequestApprovalResponse.json`: same `accept`/`cancel` semantics.

Confirmed the wire-level flow: `runtime.py:245-248` sends the handler response
synchronously via `_client.respond(notification["id"], response_payload)`. Returning
`accept` resumes the action inline — no new turn needed.

Fetched OpenAI docs for `approval_policy` semantics:
`developers.openai.com/codex/config-reference` — `untrusted | on-request | never`.
`developers.openai.com/codex/agent-approvals-security#sandbox-and-approvals` — confirms
two-layer model: sandbox = what CAN be done, approval = when to ASK.

**Phase 3 — Initial implementation plan (~10 min).** Drafted a plan as "two one-line
changes" (sandbox flip + cancel→accept). User's first scrutiny found three critical
gaps:

1. `_finalize_turn` at line 1473 marks `needs_escalation` based on `captured_request.kind`,
   not turn outcome — so even with `accept` at the wire level, the job still gets marked
   as `needs_escalation`
2. Handler needs scope validation (worktree boundary, network context) — not blanket
   auto-accept
3. `decide(approve)` acceptance criterion is stale for inline-accepted requests

**Phase 4 — Plan revision cycle (~60 min, 5 scrutiny rounds).** Each round surfaced
contract-level issues the plan had missed:

Round 1 (major revision): Added three-category handler model (inline accept / fail closed /
unknown), `captured_request` decoupling, scope validation function, `available_decisions`
gating, file-change fallback update.

Round 2 (minor revision): User found `InvalidDecisionError` mismatches the existing typed
rejection contract (`DecisionRejectedResponse` with `DecisionRejectedReason` Literal).
`PendingEscalationView` still advertises `approve` for fail-closed requests. Audit
`actor="handler"` is not a valid `AuditEvent.actor` value.

Round 3 (minor revision): Integration test inventory incomplete — `test_delegate_start_
integration.py` has 7 uses of `_command_approval_request_msg()`. `_ConfigurableStubSession`
also discards handler responses. Missing `available_decisions` negative test and positive
in-worktree path tests.

Round 4 (minor revision): `contracts.md:297` lists the `DecisionRejectedReason` enum —
needs `request_not_approvable`. Audit placement wording contradictory (said both "after
state transitions" and "at the top"). Risk 2 count stale. Live-smoke objective collides
with existing files.

Round 5 (minor revision): Delegate skill `SKILL.md` hard-codes `approve, deny` — doesn't
respect `available_decisions` from the view. Design spec mirror is stale. Live-smoke
directory `docs/scratch/` doesn't exist.

Final verdict: **Defensible.** Two optional polish items applied (tuple→list wording,
build sequence dependency correction).

## Decisions

### D1: Three-category handler response model

**Choice:** Split handler responses into inline accept (in-boundary), fail closed
(out-of-boundary), and unknown/interrupt (existing), rather than binary accept/cancel.

**Driver:** User's scrutiny: "I would not implement this as only two one-line changes.
The sandbox change is clean. The approval change needs one additional state-machine
adjustment and a narrower auto-accept policy." Followed by: "Out-of-boundary command/
file approvals cannot safely keep the old approve path."

**Alternatives considered:**
- **Binary accept/cancel** — rejected because it doesn't distinguish in-boundary from
  out-of-boundary requests. A blanket auto-accept ignores `networkApprovalContext`,
  `grantRoot`, `cwd` — silently widens the sandbox boundary.
- **Keep all requests as cancel + escalate** — rejected because in-boundary requests
  create the cancel-retry loop. The handler CAN grant in-boundary requests inline; it
  SHOULD NOT grant out-of-boundary ones.

**Trade-offs accepted:** More complex handler logic (~30 lines vs. 2). Scope validation
adds a new function. Worth it: the alternative is a security regression or a broken
escalation model.

**Confidence:** High (E2) — grounded in vendored schemas (accept/cancel semantics),
OpenAI docs (sandbox read access, approval policy), and empirical sandbox tests.

**Reversibility:** Medium — handler logic is encapsulated in the closure, but
`_finalize_turn` and `decide` both depend on the `captured_request` semantics.

**Change trigger:** If App Server introduces a deferred-grant mechanism (accept after
cancel), the fail-closed category could be converted to deferred-approve. Currently no
such mechanism exists.

### D2: `decide(approve)` rejection for cancel-capable kinds

**Choice:** Return `DecisionRejectedResponse` with reason `"request_not_approvable"`
when `decide(approve)` is called for `command_approval` or `file_change` requests.

**Driver:** User's scrutiny: "Once the handler returns `cancel`, the original App
Server request is denied and interrupted. A later `decide(approve)` cannot grant that
original request; it can only start a new turn with natural-language instruction" —
which recreates the cancel-retry loop under a new name.

**Alternatives considered:**
- **Allow approve, start new turn** — rejected because the new turn retries the same
  action, App Server asks again, handler cancels again. The cancel-retry loop.
- **Raise `InvalidDecisionError`** — rejected because the existing `decide` contract
  returns typed rejections (`DecisionRejectedResponse`), not exceptions. Tests and MCP
  callers expect JSON responses.

**Trade-offs accepted:** `decide(approve)` is now rejected for the most common
escalation kinds. Callers who expect to approve must use `deny` or `discard`. This is
correct: the handler already resolved in-boundary requests; out-of-boundary ones are
not approvable.

**Confidence:** High (E2) — verified by tracing the cancel → new turn → re-cancel
loop in source code (`delegation_controller.py:1743-1754`) and confirming no
wire-level deferred-grant exists in vendored schemas.

**Reversibility:** High — the rejection is a guard in `decide`, not a structural change.
Removing it re-enables the loop but doesn't break state.

**Change trigger:** If App Server adds a mechanism to grant a previously-cancelled
request inline (not via new turn).

### D3: `PendingEscalationView.available_decisions` varies by request kind

**Choice:** Fail-closed command/file escalations advertise `("deny",)` only. Unknown/
user-input escalations advertise `("approve", "deny")`.

**Driver:** User's scrutiny: "The pending escalation view would still advertise
`approve` for requests where approve is intentionally rejected." Showing approve when
the server rejects it is "technically safe but user-hostile and semantically incoherent."

**Alternatives considered:**
- **Keep `("approve", "deny")` everywhere** — rejected for incoherent UX: user tries
  approve, gets rejection, doesn't understand why.
- **Remove `available_decisions` entirely** — rejected because it removes information
  the caller needs to render correct UI.

**Trade-offs accepted:** View projection now depends on request kind, adding a
conditional to `_project_request_to_view`. Minor complexity, worth the correct UX.

**Confidence:** High (E2) — `_project_request_to_view` currently uses a constant
`_PLUGIN_DECISIONS = ("approve", "deny")` at line 847. The change adds one conditional.

**Reversibility:** High — single line change in projection method.

**Change trigger:** If `decide(approve)` is re-enabled for command/file kinds.

### D4: `includePlatformDefaults: True` for sandbox policy

**Choice:** Change `runtime.py:33` from `False` to `True`.

**Driver:** OpenAI App Server docs: "On macOS, `includePlatformDefaults: true` appends
a curated platform-default Seatbelt policy for restricted-read sessions. This improves
tool compatibility without broadly allowing all of `/System`." The official documented
example for `workspaceWrite + restricted` mode uses `includePlatformDefaults: true`.

**Alternatives considered:**
- **Manual `readableRoots` additions** (e.g., `["/usr/bin", "/usr/lib"]`) — rejected
  because it's platform-dependent, fragile, and misses dynamic linker paths. The curated
  set IS the minimum viable grant, maintained by the App Server team.
- **`readOnlyAccess: fullAccess`** — rejected because it allows reading `~/.ssh/`,
  `~/.config/gh/hosts.yml` (empirically confirmed). Too permissive for delegation.
- **Keep `False`** — rejected because it blocks all shell execution (the original defect).

**Trade-offs accepted:** Delegates platform-default path curation to App Server. If a
future App Server version changes the curated set, the sandbox boundary changes
implicitly. Acceptable: the alternative is maintaining a manual path list.

**Confidence:** High (E2) — grounded in official docs AND empirical testing showing the
`--full-auto` sandbox allows secrets while `restricted` mode blocks them.

**Reversibility:** High — one-line change, fully backward-compatible.

**Change trigger:** If the curated platform defaults are found to include sensitive
user directories (would require App Server bug report and investigation).

### D5: Explicit field validation over fuzzy key-pattern matching

**Choice:** Validate scope using explicit checks on documented fields
(`networkApprovalContext`, `cwd`, `grantRoot`) rather than substring matching on
unknown keys.

**Driver:** User's scrutiny: "'any key matching `additionalPermissions`/`fileSystem`/
`network` patterns' is not a stable contract. Vendored command approval params include
`networkApprovalContext`, but I did not find a top-level `additionalPermissions` property."

**Alternatives considered:**
- **Fuzzy key-pattern matching** — rejected because it produces false positives on
  harmless fields and false negatives on renamed expanded-permission payloads.
- **No validation, accept all** — rejected for security reasons.

**Trade-offs accepted:** If App Server adds new scope-expanding fields in future
versions, they won't be caught until the vendored schemas are updated and the validator
is extended. Unknown request methods already escalate through the existing unknown-kind
path, which provides a safety net.

**Confidence:** High (E2) — verified against vendored `CommandExecutionRequestApproval
Params.json` and `FileChangeRequestApprovalParams.json`.

**Reversibility:** High — adding new field checks is additive.

**Change trigger:** New vendored schema version with additional scope-expanding fields.

## Changes

### `docs/plans/2026-04-23-delegate-remediation-implementation.md` — New

Implementation plan artifact (the primary deliverable of this session). 13-step build
sequence, 10 change groups, 19 new tests, 26 existing test updates, live-smoke
verification gate. Survived 5 rounds of adversarial scrutiny.

### PR #124 merged

`docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` landed
on main at `005d4b44`.

## Codebase Knowledge

### Files Read This Session

| File | Why | Key Finding |
|------|-----|-------------|
| `runtime.py:22-37` | Ground sandbox defect | `build_workspace_write_sandbox_policy`: `includePlatformDefaults: False`, `readableRoots: [worktree]`, `networkAccess: False` |
| `runtime.py:160-273` | Understand turn API | `run_execution_turn` passes `sandboxPolicy` and `approvalPolicy` to `turn/start`. Server request handler is synchronous (line 245-248) |
| `delegation_controller.py:650-720` | Understand handler | `_server_request_handler` closure: parses request, captures first one, returns `cancel` for `_CANCEL_CAPABLE_KINDS` |
| `delegation_controller.py:1439-1530` | Understand finalization | `_finalize_turn`: line 1473 marks `needs_escalation` if `captured_request.kind in _CANCEL_CAPABLE_KINDS` regardless of turn outcome |
| `delegation_controller.py:1590-1649` | Understand decide rejections | Typed rejection pattern via `_reject_decision` returning `DecisionRejectedResponse` |
| `delegation_controller.py:1743-1754` | Understand approve path | `decide(approve)` builds resume prompt and starts NEW turn — doesn't grant original request |
| `delegation_controller.py:246` | Approval policy default | `approval_policy="untrusted"` — always prompts |
| `delegation_controller.py:847-858` | View projection | `_PLUGIN_DECISIONS = ("approve", "deny")` used for all views unconditionally |
| `execution_prompt_builder.py:41-77` | Resume prompt | Natural-language-only: "treat the caller decision below as authoritative" |
| `approval_router.py:1-109` | Request parsing | `parse_pending_server_request` extracts `requested_scope` as params minus context keys. File-change `_AVAILABLE_DECISIONS` fallback is `()` |
| `models.py:37-47` | Rejection reasons | `DecisionRejectedReason` is a 9-value `Literal` — needs `request_not_approvable` |
| `models.py:187-202` | Audit event | `AuditEvent.actor` is `Literal["claude", "codex", "user", "system"]` — `"handler"` is invalid |
| `models.py:441-452` | Escalation view | `PendingEscalationView.available_decisions: tuple[str, ...] = ()` |
| `CommandExecutionRequestApprovalResponse.json` | Grant vocabulary | `accept`, `acceptForSession`, `acceptWithExecpolicyAmendment`, `applyNetworkPolicyAmendment`, `decline`, `cancel` |
| `CommandExecutionRequestApprovalParams.json` | Request shape | `command`, `cwd`, `networkApprovalContext`, `proposedExecpolicyAmendment`, `AdditionalPermissionProfile` definitions |
| `FileChangeRequestApprovalResponse.json` | Grant vocabulary | `accept`, `acceptForSession`, `decline`, `cancel` |
| `FileChangeRequestApprovalParams.json` | Request shape | `grantRoot` (UNSTABLE), `reason` |
| `test_delegation_controller.py:1260-1277` | Fixture shape | `_command_approval_request()`: `command: "rm -rf /"`, no `cwd`/`networkApprovalContext` — in-boundary under new model |
| `test_delegation_controller.py:43-110` | Test infrastructure | `_FakeSession` discards handler return values at line 95. `_interrupted` set by `interrupt_turn()` |
| `test_delegation_controller.py:199-261` | Controller builder | `_build_controller` uses fixed UUID iterator, `approval_policy="untrusted"` default |
| `test_delegate_start_integration.py:213-239` | Integration stub | `_ConfigurableStubSession` also discards handler responses at line 227 |
| `test_delegate_start_integration.py:514-531` | Integration fixture | `_command_approval_request_msg()`: same in-boundary shape as unit fixture |
| `test_runtime.py:167-183` | Sandbox policy test | Asserts `includePlatformDefaults: False` — must update to `True` |
| `contracts.md:297` | Contract enum | Lists `DecisionRejectedReason` values — needs `request_not_approvable` |
| `SKILL.md:200-216` | Skill UX | Hard-codes `approve, deny` in decision prompt, unconditional approve routing |

### Delegation Architecture (Updated Understanding)

| Component | File | Line | Purpose |
|-----------|------|------|---------|
| Sandbox policy builder | `runtime.py` | 22-37 | Constructs `workspaceWrite` policy — `includePlatformDefaults: False` is the defect |
| Turn API | `runtime.py` | 160-183 | `run_execution_turn` sends `sandboxPolicy` + `approvalPolicy` to App Server |
| Server request dispatch | `runtime.py` | 245-248 | Synchronous: handler response sent via `_client.respond()` inline |
| Handler closure | `delegation_controller.py` | 650-720 | Three strategies: cancel-capable cancel, unknown interrupt, user-input answers |
| Finalization | `delegation_controller.py` | 1439-1530 | `captured_request.kind` drives `needs_escalation` — not turn outcome |
| Decide approve | `delegation_controller.py` | 1743-1754 | Builds resume prompt + NEW turn — doesn't grant original wire request |
| View projection | `delegation_controller.py` | 849-858 | `_PLUGIN_DECISIONS` constant, no kind-based variance |
| Typed rejections | `delegation_controller.py` | `_reject_decision` | Returns `DecisionRejectedResponse` — never raises |
| Request parser | `approval_router.py` | 37-71 | Extracts `requested_scope`, resolves `available_decisions` |
| Approval decision enum | `approval_router.py` | 20-34 | File-change fallback is `()` — stale vs. vendored schema |

### Approval Flow (Current — Defective)

```
Agent requests command_approval/file_change
  → _server_request_handler returns {"decision": "cancel"}
  → App Server denies + interrupts the turn
  → Request captured in _pending_request_store
  → _finalize_turn: kind in _CANCEL_CAPABLE_KINDS → needs_escalation
  → Caller runs decide(approve)
    → build_execution_resume_turn_text constructs NL prompt
    → _execute_live_turn starts NEW turn with SAME sandbox
    → Agent retries action → sandbox blocks / App Server re-asks → re-escalates
    → Loop repeats
```

### Approval Flow (After Fix)

```
Agent requests command_approval/file_change
  → _server_request_handler validates scope
  → In-boundary + accept available:
      return {"decision": "accept"} → App Server resumes inline
      captured_request NOT set → _finalize_turn sees clean completion
      Job completes with artifacts
  → Out-of-boundary / accept unavailable:
      return {"decision": "cancel"} → turn interrupted
      captured_request set → _finalize_turn → needs_escalation
      View advertises ("deny",) only → decide(approve) returns rejection
```

### Three Tiers of Sandbox Read Access

| Tier | `readOnlyAccess` | Reads | Our use |
|------|-----------------|-------|---------|
| Full | `{ type: "fullAccess" }` | Everything including `~/.ssh`, `~/.config` | NOT for delegation (too permissive) |
| Curated | `{ type: "restricted", includePlatformDefaults: true, readableRoots: [...] }` | Declared roots + curated platform paths | TARGET — functional + secure |
| Locked | `{ type: "restricted", includePlatformDefaults: false, readableRoots: [...] }` | Only declared roots | CURRENT — blocks shell execution |

## Context

### Project State

T-02 through T-07 arc is complete. PR #124 merged. One open ticket:

| Ticket | Status | Phase | Key Artifact |
|--------|--------|-------|-------------|
| T-20260423-01 | Open | Phase 3 complete | Implementation plan at `docs/plans/2026-04-23-delegate-remediation-implementation.md` |

### Mental Model

This is a **security boundary calibration** problem, not a feature-add. The T-05
hardening chose maximally restrictive defaults for both sandbox and approval. That was
correct at the time (execution infrastructure was unverified). Now that the infrastructure
is verified (T-07 smoke proved the pipeline works), the boundary needs to shift from
"deny by default" to "allow within boundary."

The core insight: `cancel` is a **terminal** wire-level decision. Once cancelled, the
original request is gone — a later approve can only start a new turn that re-triggers
the same request, creating a loop. The fix must accept inline where safe and reject
approve where unsafe, rather than deferring everything.

### Two-Layer Security Model

From `developers.openai.com/codex/agent-approvals-security`:
- **Sandbox mode**: What Codex CAN do technically (filesystem, network)
- **Approval policy**: When Codex must ASK before acting

For delegation, the sandbox IS the approval — the agent operates in an isolated
worktree with no network. The caller's review happens at the **promote** step, not at
individual command approval.

## Learnings

### `includePlatformDefaults: True` is a curated Seatbelt set, not full filesystem

**Mechanism:** On macOS, App Server appends a platform-specific Seatbelt policy for
restricted-read sessions when `includePlatformDefaults: true`. The docs explicitly say
"without broadly allowing all of `/System`."

**Evidence:** OpenAI App Server docs at `developers.openai.com/codex/app-server#sandbox-
read-access-readonlyaccess`. Empirical: `codex sandbox macos --full-auto` (which uses
`fullAccess` default) allows reading `~/.config/gh/hosts.yml` — more permissive than
`restricted + true`.

**Implication:** Our delegation sandbox should use `restricted + includePlatformDefaults:
true` — the documented pattern for functional-but-secure sandboxes. The curated set is
maintained by the App Server team.

### `cancel` in App Server approval is terminal — not deferrable

**Mechanism:** `cancel` = "User denied the command. The turn will also be immediately
interrupted." It's semantically a deny + interrupt, not a deferral. Once cancelled,
the wire request is gone.

**Evidence:** Vendored `CommandExecutionRequestApprovalResponse.json:75-79` and
`FileChangeRequestApprovalResponse.json:28-32`.

**Implication:** The handler cannot use `cancel` as a "defer for later approval" mechanism.
`decide(approve)` starts a new turn — it doesn't grant the original cancelled request.
Any deferred approval model requires inline accept at the handler level.

### `_finalize_turn` couples escalation to request kind, not turn outcome

**Mechanism:** `delegation_controller.py:1473` checks
`captured_request.kind in _CANCEL_CAPABLE_KINDS` to derive `needs_escalation`. Even if
the handler returns `accept` and the turn completes, a captured request still triggers
escalation.

**Evidence:** Source at line 1473: `if captured_request.kind in _CANCEL_CAPABLE_KINDS or
interrupted_by_unknown: final_status = "needs_escalation"`.

**Implication:** The fix must NOT set `captured_request` for inline-accepted requests.
Only out-of-boundary requests that get `cancel` should be captured.

### Empirical sandbox tests can conflate file-not-found with sandbox denial

**Mechanism:** `cat ~/.ssh/id_rsa 2>/dev/null && echo OK || echo DENIED` conflates
ENOENT and sandbox denial. The `--log-denials` flag only shows Seatbelt denials, not
ENOENT.

**Evidence:** First test showed `~/.ssh: DENIED` but `--log-denials` had NO file-read
denials for `~/.ssh`. Second test explicitly checked `[ -d "$dir" ]` before listing.

**Implication:** Always distinguish file-not-found from sandbox-denied in empirical
tests. Check existence first, then test access. Use `--log-denials` for authoritative
denial evidence.

### File-change `available_decisions` fallback is stale

**Mechanism:** `approval_router.py:31` sets `_AVAILABLE_DECISIONS["file_change"] = ()`.
The vendored schema defines `accept`, `acceptForSession`, `decline`, `cancel`.

**Evidence:** `FileChangeRequestApprovalResponse.json` lists all four values.

**Implication:** The handler's `available_decisions` gating would fail for file-change
requests using the fallback. Must update to match schema.

## Next Steps

### 1. Execute implementation plan (T-20260423-01 Phases 4-5)

**Dependencies:** Plan approved (this session).

**What to read first:**
- Implementation plan: `docs/plans/2026-04-23-delegate-remediation-implementation.md`
- Build sequence is 13 steps; steps 1-5 are parallel

**Recommended approach:**
1. Start with steps 1-5 in parallel (sandbox policy, boundary validator, test
   infrastructure, model change)
2. Then steps 6-9 sequentially (handler, audit, decide guard, view projection)
3. Step 10: skill UX update
4. Step 11: ticket AC update
5. Step 12: all tests (19 new, 26 updated)
6. Step 13: live-smoke verification

**Key files to modify (from plan):**
- `runtime.py:33` — `includePlatformDefaults: True`
- `approval_router.py` — file-change fallback + `is_within_delegation_boundary()`
- `delegation_controller.py` — handler restructure, audit helper, decide guard, view
- `models.py` — `"request_not_approvable"` in `DecisionRejectedReason`
- `contracts.md:297` — add to rejection reason enum
- `SKILL.md` — dynamic `available_decisions`, approve guard
- `test_delegation_controller.py` — 20 fixture usages to update
- `test_delegate_start_integration.py` — 7 fixture usages to update
- `test_runtime.py:178` — expected value update

### 2. Fix T-20260416-01 (dialogue reply extraction mismatch)

**Dependencies:** Independent of delegate remediation.

**Context:** `codex.dialogue.reply` items-array extraction mismatch. Narrower and less
strategically blocking than delegate remediation.

## In Progress

**Clean stopping point.** Implementation plan written and approved. No code changes made
yet — the plan is the deliverable. Branch `feature/delegate-remediation-sandbox-approval`
is at `005d4b44` (same as main) with the untracked plan file.

**Immediate next action:** Begin executing the implementation plan, starting with the
parallel steps 1-5.

## Open Questions

### 1. What exactly does the curated platform-default Seatbelt set include?

**Context:** The docs say "curated" but don't enumerate the paths. Empirical testing
confirmed the `--full-auto` mode (which uses `fullAccess`) allows `~/.config/gh`. But
`restricted + includePlatformDefaults: true` may or may not include `~/.config`.

**Decision pending until:** Live-smoke verification (step 13). If the delegated agent
can execute shell commands, the curated set is sufficient. If not, investigate further.

### 2. Does `approval_policy="untrusted"` still emit requests after the sandbox fix?

**Context:** With `includePlatformDefaults: True`, the sandbox allows shell execution.
But `untrusted` policy may still prompt for every command. The handler auto-accepts
in-boundary requests inline, so this creates round-trips but is functional.

**Decision pending until:** Live-smoke verification.

### 3. Abandoned cross-session delegation terminal outcomes (inherited)

**Context:** If a delegation job reaches terminal status in a session that crashes before
poll, and the next session has a different session ID, the terminal outcome may be
missing from `analytics/outcomes.jsonl`.

**Decision pending until:** Beyond current scope.

## Risks

### 1. Existing test cascade is large

20 unit-test usages + 7 integration-test usages of `_command_approval_request()` /
`_command_approval_request_msg()` need updating. The plan has a full disposition checklist
(11 fixture swap, 3 inline-accept update, 5 redesign, 1 mixed, 7 integration). Risk is
implementation time and missed edge cases in redesigned tests (especially stale
request-cycle tests).

### 2. `includePlatformDefaults: True` behavior is platform-dependent

The OpenAI docs only describe macOS behavior. Linux sandbox may behave differently.
The plan targets macOS (current development environment). Cross-platform verification
is deferred.

### 3. Live smoke may reveal additional defects

The diagnostic identified sandbox and approval as the two compounding defects. But
the live smoke (step 13) may reveal other issues: App Server version incompatibilities,
authentication state, worktree initialization problems, or execution prompt deficiencies.
These would be new tickets, not scope for this remediation.

## References

### PRs this session

| PR | Title | Status | Commit |
|----|-------|--------|--------|
| #124 | chore: add delegate execution remediation ticket (T-20260423-01) | Merged | `005d4b44` |

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-20260423-01 ticket | `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` | Ticket scope and AC |
| Implementation plan | `docs/plans/2026-04-23-delegate-remediation-implementation.md` | Execution blueprint |
| Vendored command approval response | `tests/fixtures/codex-app-server/0.117.0/CommandExecutionRequestApprovalResponse.json` | Wire contract |
| Vendored command approval params | `tests/fixtures/codex-app-server/0.117.0/CommandExecutionRequestApprovalParams.json` | Request shape |
| Vendored file change response | `tests/fixtures/codex-app-server/0.117.0/FileChangeRequestApprovalResponse.json` | Wire contract |
| Vendored file change params | `tests/fixtures/codex-app-server/0.117.0/FileChangeRequestApprovalParams.json` | Request shape |
| OpenAI sandbox docs | `developers.openai.com/codex/app-server#sandbox-read-access-readonlyaccess` | `includePlatformDefaults` semantics |
| OpenAI approval docs | `developers.openai.com/codex/agent-approvals-security#sandbox-and-approvals` | Two-layer security model |
| OpenAI config reference | `developers.openai.com/codex/config-reference` | `approval_policy` values |
| Contracts spec | `docs/superpowers/specs/codex-collaboration/contracts.md` | Caller-facing rejection enum |
| Delegate skill UX design | `docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md` | Approve/deny UX flow |

### Prior handoffs (chain)

- Immediate predecessor: `docs/handoffs/archive/2026-04-23_00-15_t07-merged-delegate-ticket-opened.md`
- Arc: ... → T-07 7e PR → merge + delegate ticket → **diagnostic + plan (this handoff)**

## Gotchas

### 1. `cancel` is terminal, not deferrable

The `cancel` decision is not a neutral "defer for later" — it actively denies the
request and interrupts the turn. Using it for requests you intend to approve later
creates the cancel-retry loop. Use `accept` for inline approval.

### 2. `_finalize_turn` state derivation is kind-based, not outcome-based

Line 1473 checks `captured_request.kind in _CANCEL_CAPABLE_KINDS` — it does NOT check
`turn_result.status`. A completed turn with a captured command_approval request still
produces `needs_escalation`. The fix: only capture requests that are actually escalated.

### 3. Sandbox empirical tests conflate ENOENT and sandbox denial

`cat nonexistent_file 2>/dev/null || echo DENIED` is ambiguous. Always check file
existence first, and use `--log-denials` for authoritative Seatbelt denial evidence.

### 4. `_command_approval_request()` fixture is now in-boundary

Under the new model, this fixture (no `networkApprovalContext`, no `cwd`, no
`grantRoot`) is in-boundary and will be inline-accepted. Tests expecting escalation
must switch to boundary-crossing fixtures.

### 5. Two fake sessions, both discard handler responses

`_FakeSession` (unit) and `_ConfigurableStubSession` (integration) both call
`server_request_handler(req)` but discard the return value. Both must be extended to
record responses for wire-level assertion.

### 6. `available_decisions` file-change fallback is empty

`approval_router.py:31` has `"file_change": ()`. The handler's `accept in
parsed.available_decisions` check would always fail. Must update to match vendored
schema before the gating logic works.

## User Preferences

### Diagnostic-first over fix-first

User structures work as diagnostic phases before implementation — "frame it as an
API-contract discovery problem before choosing the implementation path." This session
continued that pattern: diagnostic phases produced grounded evidence, then the plan
was built on that evidence.

### Adversarial scrutiny as plan verification

User performed 5 rounds of scrutiny on the implementation plan, each revealing
contract-level issues. Format: structured assessment with premise check, high-risk
assumptions, required changes, and verdict (critical/major/minor revision or
defensible). User expects plans to survive this scrutiny before implementation begins.

### Explicit test fixture inventories

User caught incomplete test inventories in 3 of 5 rounds. Expectation: every usage of
affected fixtures must be listed with a concrete disposition (fixture swap, expectation
update, redesign), not described by count.

### Contract consistency across all caller surfaces

User's recurring theme: internal state changes must be reflected in ALL caller-facing
surfaces — runtime behavior, views, rejections, skill UX, contracts docs. "The plan
fixes the execution state machine, but some public contract surfaces still describe
the old model."

### Evidence over assertion

User caught several cases where the plan asserted facts without checking: `"handler"`
as a valid actor, `()` as the file-change fallback, `InvalidDecisionError` as the
rejection mechanism, `_command_approval_request()` as an escalation fixture. Each
required source verification.
