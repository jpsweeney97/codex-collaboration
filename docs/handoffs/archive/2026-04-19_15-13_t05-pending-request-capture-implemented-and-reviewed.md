---
date: 2026-04-19
time: "15:13"
created_at: "2026-04-19T19:13:03Z"
session_id: 7027966d-1a1c-45f6-b582-899a1b674dac
resumed_from: "docs/handoffs/archive/2026-04-19_14-02_t05-pending-request-capture-plan-amended-through-scrutiny.md"
project: claude-code-tool-dev
branch: feature/t05-pending-request-capture
commit: 14b349a1
title: "T-05 pending-request capture slice — implemented, reviewed, PR published"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/jsonrpc_client.py
  - packages/plugins/codex-collaboration/server/approval_router.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/pending_request_store.py
  - packages/plugins/codex-collaboration/server/execution_prompt_builder.py
  - packages/plugins/codex-collaboration/server/__init__.py
  - packages/plugins/codex-collaboration/scripts/codex_runtime_bootstrap.py
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - packages/plugins/codex-collaboration/tests/test_runtime.py
  - packages/plugins/codex-collaboration/tests/test_jsonrpc_respond.py
  - packages/plugins/codex-collaboration/tests/test_pending_request_store.py
  - packages/plugins/codex-collaboration/tests/test_execution_prompt_builder.py
  - packages/plugins/codex-collaboration/tests/test_approval_router.py
  - packages/plugins/codex-collaboration/tests/test_mcp_server.py
---

# T-05 Pending-Request Capture Slice — Implemented, Reviewed, PR Published

## Goal

Execute the T-05 pending-request capture implementation plan (2369 lines, 8 tasks, 9 frozen design decisions) that was written and scrutinized in two prior sessions. Close AC 6 — execution-domain server requests are surfaced through an approval-routing layer rather than being silently auto-approved.

**Trigger:** Prior handoff said "plan amended through 5 rounds of adversarial scrutiny, verdict Defensible, ready for execution." User opened this session with `/load` and immediately directed execution with implementation guardrails (preserve D3/D4/D6/D9, treat the D9 contract amendment as part of the slice, keep D1 probe-gated).

**Stakes:** AC 6 (pending-request capture) is the remaining acceptance criterion for T-05. This is the core behavioral change — `codex.delegate.start` goes from "bootstrap runtime and return queued job" to "bootstrap, dispatch a turn, intercept approval requests, capture them, and return an escalation or completion."

**Success criteria (all met):**
1. 696 tests passing (666 baseline + 30 new)
2. All 9 frozen design decisions preserved
3. PR published as ready for review (jpsweeney97/claude-code-tool-dev#108)
4. Review findings addressed: turn-dispatch failure guard, resolved snapshot, D1 default

## Session Narrative

**Phase 1 — Handoff load and setup (~5 min).** Loaded the prior handoff (amended plan after 5 scrutiny rounds). User confirmed execution with specific guardrails: preserve D3/D4/D6/D9 exactly as written, treat Step 6.7 (contract amendment) as part of the slice, keep D1 probe-gated.

**Phase 2 — Plan extraction and task tracking (~10 min).** Read the full 2381-line plan in chunks, extracting all 8 tasks with their complete step descriptions, code sketches, test specifications, and commit messages. Created 8 tasks with dependency edges: Tasks 1,2 independent → Tasks 3,4,5,6 depend on 1-2 → Task 7 depends on 3-6 → Task 8 depends on 7. Read the four source files that Tasks 1-2 would modify (`jsonrpc_client.py`, `approval_router.py`, `models.py`, `runtime.py`) plus their test files.

**Phase 3 — Tasks 1-2 parallel dispatch (~3 min).** Dispatched two sonnet-model subagents in parallel for the independent primitive tasks. Task 1 (JSON-RPC `respond()` + integer ID normalization) completed in 85s with 671 tests. Task 2 (turn status widening + interrupt_turn) completed in 121s with 673 tests. Both passed spec review (background sonnet reviewers). Fixed unused imports in `test_jsonrpc_respond.py` (removed `subprocess`, `threading`).

**Phase 4 — Tasks 3-6 parallel dispatch (~4 min).** With 1-2 complete, dispatched four sonnet-model subagents for the independent building-block tasks. All four completed successfully:
- Task 3 (objective + idempotency) — 683 tests, updated `_delegation_request_hash` and MCP tool schema
- Task 4 (execution prompt builder) — 3 new tests, created `execution_prompt_builder.py`
- Task 5 (PendingRequestStore + DelegationEscalation) — 7 new tests, created store and result type, added `AuditEvent.request_id`
- Task 6 (recovery + contract) — 1 new test, orphaned-running-job recovery, D9 contract amendment

Fixed one integration gap: the existing E2E test in `test_delegate_start_integration.py` didn't pass `objective` (now required) and its hash computation didn't include the objective component.

**Phase 5 — Task 7 opus dispatch (~10 min).** The heavyweight integration task — wiring turn dispatch, the three-strategy capture handler, D6 diagnostic, terminal cleanup, and MCP dispatch. Dispatched with opus model due to multi-file integration complexity and the critical `nonlocal` closure pattern. Completed with 691 tests.

**Phase 6 — Spec review catch (~5 min).** The Task 7 spec reviewer (background sonnet) found two real issues:
1. `file_change` was misclassified in `_KNOWN_DENIAL_KINDS` instead of `_CANCEL_CAPABLE_KINDS` — D3 explicitly says "(a) Cancel-capable (command/file): `{\"decision\": \"cancel\"}`"
2. Parse-failure causal records used `""` for missing wire `id` instead of `self._uuid_factory()` per D9

Both fixed in commit `6e46a2a9`.

**Phase 7 — Task 8 dispatch (~4 min).** Integration tests + bootstrap wiring. Sonnet subagent added 3 new E2E tests (command approval escalation, unknown request escalation, busy gate with needs_escalation) plus `_ConfigurableStubSession` and `_build_e2e_setup` helpers. 694 tests.

**Phase 8 — User review (~10 min).** User reviewed the 12-commit diff against the plan and found 3 findings:
- **P1:** Turn-dispatch path has no committed-finalization guard — exception from `run_execution_turn()` or post-turn writes leaves job stuck "running" with registered runtime and open session. User reproduced with a fake session that raises.
- **P2:** Returned `DelegationEscalation.pending_request` is the stale capture snapshot — `status="pending"` even though D4 and the docstring say parsed requests are resolved. User reproduced.
- **P2:** D1 probe gate missing — controller defaults to `"on-request"` instead of `"untrusted"`.

**Phase 9 — Review fixes (~10 min).** Fixed all three:
1. Extracted `_finalize_turn()` method and wrapped both dispatch and finalization in `try/except` with best-effort cleanup (mark unknown, release, close).
2. Re-read request from store after `update_status("resolved")` so returned object has authoritative status.
3. Changed `approval_policy` default from `"on-request"` to `"untrusted"`.

Added two regression tests: dispatch failure cleanup and post-turn finalization failure cleanup. 696 tests.

**Phase 10 — User re-review and PR.** User verified the follow-up commit closed all three findings. Recommended publishing as a reviewable PR. Created jpsweeney97/claude-code-tool-dev#108 as ready for review.

## Decisions

### Decision 1: Subagent-driven development with model tiering

**Choice:** Used `superpowers:subagent-driven-development` to dispatch fresh subagents per task with two-stage review (spec compliance then code quality). Used sonnet for mechanical tasks (1-6, 8) and opus for the integration task (7).

**Driver:** The plan had 8 well-specified tasks with clear boundaries. Subagent isolation prevents context pollution between tasks.

**Alternatives considered:**
- **Inline execution** — implementing all tasks in the main session. Rejected because 8 tasks with code sketches would consume too much context.
- **All opus** — using the most capable model for everything. Rejected as wasteful for mechanical tasks (Tasks 1-4 are straight TDD with exact code sketches).

**Trade-offs accepted:** Subagents can't see each other's work during parallel dispatch, so shared files may need reconciliation. This happened: Tasks 3 and 6 both modified `delegation_controller.py`, and the integration test needed hash/objective fixes.

**Confidence:** High (E2) — 10 of 12 subagent dispatches succeeded without intervention. The 2 that needed follow-up (spec reviewer findings on Task 7) were exactly the kind of issue the two-stage review was designed to catch.

**Reversibility:** N/A — execution decision, not architectural.

**Change trigger:** If the plan were less precisely specified (no code sketches), more tasks would need opus.

### Decision 2: Extract `_finalize_turn()` for failure guard symmetry

**Choice:** Extracted post-turn processing into `_finalize_turn()` method so both the dispatch failure and finalization failure paths share the same best-effort cleanup pattern.

**Driver:** User's P1 review finding: "once `start()` flips the job to `running`, the new turn-dispatch path has no equivalent to dialogue's committed-finalization handling."

**Alternatives considered:**
- **Inline try/except around the entire block** — would work but creates a single massive try block mixing dispatch and finalization. Harder to reason about which cleanup applies.
- **No guard (original implementation)** — the implementer didn't add one. Rejected after user reproduced the failure with a fake session that raises.

**Trade-offs accepted:** `_finalize_turn()` uses `Any` type hints for `entry` and `turn_result` parameters because importing the precise types would create circular dependencies or require Protocol definitions. Acceptable for an internal method.

**Confidence:** High (E2) — user manually verified both dispatch failure and finalization failure paths work correctly.

**Reversibility:** High — the method extraction is a refactor, not a behavioral change.

**Change trigger:** If the failure guard needs to distinguish between dispatch and finalization failures (e.g., different recovery strategies), the combined guard may need to split.

### Decision 3: Re-read from store for resolved status

**Choice:** After `update_status("resolved")` in the finalization path, re-read the `PendingServerRequest` from the store and use that in the returned `DelegationEscalation`.

**Driver:** User's P2 finding: "`PendingServerRequest` is frozen (`@dataclass(frozen=True)`), so the captured variable can't be mutated in place. Callers see `status='pending'` even though D4 says parsed requests are already resolved."

**Alternatives considered:**
- **Construct a new PendingServerRequest with status="resolved"** — would work but duplicates the dataclass construction logic and doesn't use the store as source of truth.
- **Make PendingServerRequest mutable** — rejected as it violates the existing frozen convention and adds mutation concerns.

**Trade-offs accepted:** One extra store read per escalation (negligible — JSONL replay).

**Confidence:** High (E2) — the fix is straightforward and the integration test now asserts `pending_request.status == "resolved"`.

**Reversibility:** High — trivial to change the source of the returned request object.

**Change trigger:** If the store read becomes a performance concern (unlikely with JSONL).

## Changes

### `server/delegation_controller.py` — Capture loop + failure guard

**Purpose:** Core behavioral change. `start()` now dispatches an execution turn after the committed-start phase, intercepts server requests via a closure-based handler, derives job status from the turn result, and returns `DelegationEscalation` or `DelegationJob`.

**Approach:** Three-strategy handler (`_server_request_handler` closure) with `nonlocal captured_request, interrupted_by_unknown, parse_failed`. Post-turn processing extracted to `_finalize_turn()` wrapped in failure guards. Turn dispatch also wrapped.

**Key implementation details:**
- Handler uses `nonlocal` for three mutable outer variables (Round 5 scrutiny catch)
- `_CANCEL_CAPABLE_KINDS = frozenset({"command_approval", "file_change"})` — D3
- `_KNOWN_DENIAL_KINDS = frozenset({"request_user_input"})` — D3
- Parse failures create minimal `PendingServerRequest(kind="unknown")` with raw envelope fields — D4 carve-out
- D6 diagnostic and D4 `update_status("resolved")` gated by `not parse_failed`
- `_verify_post_turn_signals()` module-level function checks `serverRequest/resolved` and `item/completed` in notifications
- Failure guard: dispatch or finalization exceptions → best-effort mark job "unknown", release runtime, close session
- `approval_policy` defaults to `"untrusted"` per D1 probe gate

### `server/jsonrpc_client.py` — `respond()` method

**Purpose:** Send JSON-RPC 2.0 responses back to server-initiated requests. Accepts `str | int` for `request_id` to preserve the original wire type on the response (D9: normalization happens at the parse boundary, not the transport layer).

**Key detail:** Error handling mirrors the existing `request()` method — guards against unstarted client, wraps `BrokenPipeError` with context including the request_id.

### `server/approval_router.py` — Integer request ID normalization (D9)

**Purpose:** Add `_require_request_id()` that accepts `str | int` wire IDs and normalizes to `str`. `parse_pending_server_request` now calls this instead of `_require_string` for the `"id"` field.

**Key detail:** `_require_string()` remains unchanged — only the `id` field uses the new extractor. All other fields (`method`, `itemId`, etc.) remain string-only.

### `server/runtime.py` — Turn status widening + interrupt

**Purpose:** Make `interrupted` and `failed` first-class terminal outcomes for execution turns. Add `interrupt_turn()` for `turn/interrupt` JSON-RPC calls. Make `output_schema` optional for execution turns (D5).

**Key details:**
- `TurnExecutionResult` gains `status: TurnStatus` field (breaking change — all constructors updated)
- `run_execution_turn()` gains `approval_policy`, `server_request_handler`, optional `output_schema`
- `_run_turn()` uses `approval_policy` parameter instead of hardcoded `"never"`, conditionally includes `outputSchema`, checks `allowed_terminal_statuses`
- `run_advisory_turn()` unchanged: requires `output_schema`, only allows `"completed"`, hardcodes `approval_policy="never"`

### `server/pending_request_store.py` — JSONL persistence (new file)

**Purpose:** Session-scoped append-only store for `PendingServerRequest` records. Mirrors `DelegationJobStore` pattern.

**Key detail:** `_replay()` silently skips invalid records (corrupt JSON, unknown status, missing fields). Status validation uses `get_args(PendingRequestStatus)` to stay in sync with the type alias.

### `server/execution_prompt_builder.py` — Prompt construction (new file)

**Purpose:** Build the text input for execution turns. Conveys the objective and worktree scope boundary. No structured output schema (D5).

### `server/models.py` — New types and fields

**Purpose:** `TurnStatus` type alias, `status` field on `TurnExecutionResult`, `DelegationEscalation` dataclass, `request_id: str | None` on `AuditEvent`.

### `docs/superpowers/specs/codex-collaboration/contracts.md` — D9 amendment

**Purpose:** Replace "Plugin-assigned unique identifier" with wire-id semantics for `request_id`.

**Line 81 changed to:** "Wire request id from the App Server, normalized to string. Used for `serverRequest/resolved` correlation. Parse-failure causal records may use a plugin-generated fallback id (not wire-correlated)."

## Codebase Knowledge

### Architecture: Server Request Handler Flow (Implemented)

```
_server_request_handler(message) — closure inside start()
  │
  ├─ try: parse_pending_server_request(message)
  │    │
  │    ├─ EXCEPT (parse failure):
  │    │    ├─ Create minimal PendingServerRequest(kind="unknown", raw id/method)
  │    │    ├─ Store if first capture
  │    │    ├─ Set interrupted_by_unknown=True, parse_failed=True (nonlocal)
  │    │    ├─ Call entry.session.interrupt_turn()
  │    │    └─ Return None (no wire response)
  │    │
  │    ├─ kind NOT in cancel-capable AND NOT in known-denial:
  │    │    ├─ Store if first capture
  │    │    ├─ Set interrupted_by_unknown=True
  │    │    ├─ Call entry.session.interrupt_turn()
  │    │    └─ Return None
  │    │
  │    ├─ kind in cancel-capable (command_approval, file_change):
  │    │    ├─ Store if first capture
  │    │    └─ Return {"decision": "cancel"}
  │    │
  │    └─ kind in known no-cancel (request_user_input):
  │         ├─ Store if first capture
  │         └─ Return {"answers": {}}
  │
  POST-TURN (_finalize_turn):
  │
  ├─ captured_request is not None:
  │    ├─ D6 diagnostic (only if not parse_failed)
  │    ├─ D4 update_status("resolved") (only if not parse_failed)
  │    ├─ Derive job status: cancel-capable/interrupted → needs_escalation
  │    │                      no-cancel + completed → completed
  │    │                      no-cancel + not completed → needs_escalation
  │    ├─ Emit audit: action="escalate", request_id=captured_request.request_id
  │    ├─ Terminal cleanup: completed/failed → release + close
  │    │                     needs_escalation → keep live
  │    ├─ Re-read request from store (authoritative status)
  │    └─ Return DelegationEscalation(job, pending_request, agent_context)
  │
  └─ captured_request is None:
       ├─ Derive job status: completed/failed/unknown from turn_result.status
       ├─ Terminal cleanup: release + close
       └─ Return DelegationJob
```

### Key Locations (Post-Implementation)

| Concept | Location |
|---------|----------|
| `respond()` method | `server/jsonrpc_client.py:106` |
| `_require_request_id()` (D9) | `server/approval_router.py:83` |
| `TurnStatus` type | `server/models.py:19` |
| `TurnExecutionResult.status` field | `server/models.py:128` |
| `run_execution_turn()` (widened) | `server/runtime.py:160` |
| `interrupt_turn()` | `server/runtime.py:185` |
| `_run_turn()` (rewritten) | `server/runtime.py:194` |
| Server request handling in turn loop | `server/runtime.py:245-248` |
| `build_execution_turn_text()` | `server/execution_prompt_builder.py:14` |
| `PendingRequestStore` | `server/pending_request_store.py:22` |
| `DelegationEscalation` dataclass | `server/models.py:342` |
| `AuditEvent.request_id` field | `server/models.py:171` |
| `_server_request_handler` closure | `server/delegation_controller.py:550` |
| `_finalize_turn()` | `server/delegation_controller.py:639` |
| `_verify_post_turn_signals()` (D6) | `server/delegation_controller.py:720` |
| Orphaned-running-job recovery | `server/delegation_controller.py:768` |
| D9 contract amendment | `docs/superpowers/specs/codex-collaboration/contracts.md:81` |
| Bootstrap factory (PendingRequestStore) | `scripts/codex_runtime_bootstrap.py:117` |

### Patterns Observed

- **JSONL append-only stores:** Both `DelegationJobStore` and `PendingRequestStore` use the same pattern — append operations to a JSONL file, replay on read, last record per key wins. See `pending_request_store.py` mirroring `delegation_job_store.py`.
- **Committed-finalization guard:** `start()` now has two failure guard layers — one for the committed-start phase (journal dispatched → completed) and one for the turn-dispatch phase (running → terminal). Both use the same pattern: best-effort mark records "unknown", leave cleanup for `recover_startup()`.
- **`_FakeSession` and `_FakeControlPlane`:** Test infrastructure for delegation controller tests supports configurable server requests, turn results, and failure injection via `_raise_on_turn` and `_next_raise_on_turn`.

## Context

### Mental Model

The capture loop is a **synchronous interceptor** inside the notification loop. The runtime's `_run_turn()` calls the `server_request_handler` callback for each notification that has both `id` and `method` (server-initiated requests). The handler closure captures state via `nonlocal` and can either respond inline (cancel/deny) or trigger an interrupt (unknown/parse-failure). After the loop exits, the outer code derives job status from the combination of captured request + turn result status.

### Project State

- **T-05 execution-start slice:** COMPLETE on main at `5ee7afb4` (21 commits, 663 tests)
- **T-05 pending-request capture slice:** IMPLEMENTED, REVIEWED, PR PUBLISHED at jpsweeney97/claude-code-tool-dev#108
- **AC 6:** Will close when this PR merges
- **Sequencing:** pending-request capture (this slice) → decide-surface + lifecycle → T-05 COMPLETE → T-06 → T-07

### Environment

- Branch: `feature/t05-pending-request-capture`
- Main: `5ee7afb4` (unchanged)
- Tests: 696 passed (666 baseline + 30 new)
- Commits: 13 on branch (12 implementation + 1 hardening test)
- PR: jpsweeney97/claude-code-tool-dev#108 (ready for review)

## Learnings

### Spec reviewers catch real bugs that tests miss

**Mechanism:** The sonnet spec reviewer for Task 7 found `file_change` misclassified in `_KNOWN_DENIAL_KINDS` (returns `{"answers": {}}`) when D3 says it's cancel-capable (returns `{"decision": "cancel"}`). No test covered `file_change` requests, so the misclassification was invisible to the test suite.

**Evidence:** Spec reviewer output identified the deviation at `delegation_controller.py:547-548` with the exact plan reference (D3, Task 7 header, Risks table).

**Implication:** Two-stage review (spec then quality) is justified even when tests pass. The spec reviewer catches semantic deviations that tests — constrained to the test cases the implementer wrote — cannot detect.

### Parallel subagent dispatch needs shared-file reconciliation

**Mechanism:** When multiple subagents modify the same file (e.g., Tasks 3 and 6 both touch `delegation_controller.py`), their changes merge cleanly at the git level but may introduce cross-cutting inconsistencies. The integration test needed `objective` added to its MCP arguments and `objective` added to its hash computation — both changes from Task 3 that Task 6's subagent didn't see.

**Evidence:** 1 test failure after merging Tasks 3-6, fixed by adding `"objective": "E2E test"` to arguments and `:E2E test` to the hash string.

**Implication:** After parallel dispatch of tasks that touch shared files, always run the full suite and fix integration gaps before proceeding.

### Frozen dataclasses require re-read for updated state

**Mechanism:** `PendingServerRequest` is `@dataclass(frozen=True)`. After `update_status("resolved")` writes to the store, the captured variable still holds the original object with `status="pending"`. The returned `DelegationEscalation` therefore has a stale snapshot unless the request is re-read from the store.

**Evidence:** User's P2 finding — reproduced locally: returned object stayed `pending` while stored record was `resolved`.

**Implication:** Any path that mutates store state and then returns an object from that store must re-read rather than reuse the captured variable.

## Next Steps

### 1. Merge PR and close AC 6

**Dependencies:** PR approval (jpsweeney97/claude-code-tool-dev#108).

**Action:** Merge to main. This closes AC 6 for T-05.

### 2. Decide-surface + lifecycle refinements

**Dependencies:** PR merged.

**What:** The `codex.delegate.decide` tool that allows Claude to act on the escalation. The pending request has been captured and the job is in `needs_escalation` — now Claude needs a way to make a decision (approve, deny, etc.).

### 3. Remaining T-05 sequencing

After AC 6 closes: decide-surface + lifecycle → T-05 COMPLETE → T-06 → T-07.

## In Progress

**Clean stopping point.** All implementation complete. PR published. No work in flight.

- **Completed:** 8 implementation tasks, spec review fixes, user review fixes, hardening test, PR published.
- **Not in flight:** No code changes pending.
- **Next action for next-session Claude:** Check PR status. If approved, merge to main. If review comments, address them.

## Open Questions

### 1. `turn/interrupt` transport re-entrancy (unchanged)

**Context:** The handler calls `entry.session.interrupt_turn()` from inside the `_server_request_handler` callback. This sends a `turn/interrupt` JSON-RPC request via the same transport that's reading notifications. The `_FakeSession` tests don't exercise the real transport.

**Impact:** Medium. If the transport doesn't handle re-entrant reads, the handler will deadlock.

**Decision pending until:** Live testing against the real App Server. The fallback (documented in D5's change trigger) is to return a sentinel and call `interrupt_turn()` after the loop.

### 2. `on-request` operational semantics (unchanged)

**Context:** The vendored schema proves `on-request` is a valid `approvalPolicy` value, but operational semantics (which actions trigger prompts) are not documented. The controller defaults to `untrusted` per D1, but `on-request` may be needed for the right approval behavior.

**Decision pending until:** Live probe against the real App Server.

## Risks

### 1. Nested `turn/interrupt` transport safety (unchanged)

Same as prior handoff. Live testing in Task 7 implementation didn't exercise the real transport. The fake tests pass because `_FakeSession.interrupt_turn()` just sets a flag.

### 2. `_FakeSession` complexity

The fake session now has `run_execution_turn()`, `interrupt_turn()`, `close()`, `_raise_on_turn`, `_interrupted` state, and configurable server requests + turn result. It's significantly more complex than the prior session fake. If it drifts from the real `AppServerRuntimeSession` interface, tests may pass against the fake but fail against reality.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth (AC 6) |
| T-05 pending-request plan | `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` | Implementation plan (2381 lines, untracked) |
| Recovery spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Pending request ordering, unknown request handling |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | `PendingServerRequest` schema, `AuditEvent` schema |
| App Server docs | `docs/codex-app-server.md` | Approval flow, `turn/interrupt` |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-19_14-02_t05-pending-request-capture-plan-amended-through-scrutiny.md`
- T-05 arc: execution-start slice COMPLETE → pending-request capture PLANNED → scrutiny + amendments → **execute plan + review + PR (this handoff)** → merge → decide-surface + lifecycle → T-05 COMPLETE

### Pull Request

jpsweeney97/claude-code-tool-dev#108 — "feat(t20260330-05): pending-request capture slice (AC 6)"

## Gotchas

### 1. `nonlocal` required for closure state mutation

**Symptom:** `parse_failed = True` inside the handler doesn't affect the outer scope. D4 carve-out and D6 skip silently fail.

**Prevention:** The handler's `nonlocal` declaration includes `captured_request, interrupted_by_unknown, parse_failed`. Any future additions to the handler's mutable outer state must be added to this declaration.

### 2. Frozen dataclasses require re-read after store mutation

**Symptom:** The returned `DelegationEscalation.pending_request` has `status="pending"` even though the store record is `"resolved"`.

**Prevention:** After `update_status("resolved")`, re-read from `PendingRequestStore.get()` and use that object in the return value.

### 3. Parallel subagent dispatch needs reconciliation

**Symptom:** Tests fail because one subagent's changes aren't visible to another's test assumptions (e.g., hash includes `objective` but test doesn't).

**Prevention:** After parallel dispatch, always run the full suite and fix cross-cutting inconsistencies before proceeding.

### 4. Spec reviewer catches strategy misclassification

**Symptom:** `file_change` in the wrong kind set (denial instead of cancel-capable). Tests pass because no test exercises `file_change`.

**Prevention:** Spec reviewer explicitly checks kind membership against the plan's D3 table. Add `file_change` tests if not present.

## Conversation Highlights

### User's implementation guardrails

User provided four specific guardrails at session start:
- "Preserve D3, D4, D6, and D9 exactly as written. Do not 'simplify' them during coding."
- "Treat the docs amendment for `request_id` semantics in Step 6.7 as part of the slice, not optional cleanup."
- "Keep D1 probe-gated. Do not silently lock `approvalPolicy` to `on-request` unless the live probe in Task 8 proves that behavior."
- "Use the plan as the execution packet. If you diverge from it, that should be a conscious, reviewable decision."

### User's review style

User's review was against the full diff, not individual commits. Findings were structured as P1/P2 with reproduction evidence ("I reproduced this locally with a fake session that raises from `run_execution_turn()`"). Re-review was efficient: "No new findings" with verification of both failure modes.

### PR recommendation

User: "I recommend publishing this as a reviewable PR now, not doing more branch-local churn." — Explicit signal that the implementation was ready to ship, not to iterate further locally.

## User Preferences

### Evidence-first review

User reviews against the diff and reproduction, not against the commit messages or PR description. Findings include reproduction evidence and specific file:line references. "I reproduced this locally" is the standard of proof.

### Implementation guardrails as review contract

User provides frozen decisions and guardrails before execution begins, then reviews against them. This is a contract: the user defines the constraints, Claude executes within them, and the review verifies compliance.

### Ship early, review in PR

User prefers publishing PRs as "ready for review" rather than iterating locally. "I recommend publishing this as a reviewable PR now, not doing more branch-local churn."
