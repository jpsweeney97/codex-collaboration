---
date: 2026-04-19
time: "14:02"
created_at: "2026-04-19T18:02:19Z"
session_id: e3defb30-8d1f-4f59-bf81-840e79c9d79d
resumed_from: "docs/handoffs/archive/2026-04-19_13-00_t05-pending-request-capture-plan-complete-ready-for-execution.md"
project: claude-code-tool-dev
branch: feature/t05-pending-request-capture
commit: 5ee7afb4
title: "T-05 pending-request capture plan — amended through 5 rounds of adversarial scrutiny"
type: handoff
files:
  - docs/plans/2026-04-19-t05-pending-request-capture-slice.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
---

# T-05 Pending-Request Capture Plan — Amended Through 5 Rounds of Adversarial Scrutiny

## Goal

Amend the T-05 pending-request capture implementation plan to pass adversarial scrutiny before execution begins. The plan was written in the prior session (design + planning only, no implementation). This session's job was to review, verify, and fix plan-level issues so the execution packet is internally consistent and contract-aligned.

**Trigger:** Prior handoff said "plan complete, ready for execution." User opened this session by running the plan through structured adversarial review rather than executing it directly.

**Stakes:** AC 6 (pending-request capture) is the remaining acceptance criterion for T-05. The plan is the execution guide for a 2300-line, 8-task implementation with cross-cutting contract, recovery, and protocol dependencies. Plan-level contradictions that survive into execution produce P1-class post-merge findings — the execution-start slice had exactly this problem (P1a replay validation bug traced to plan-code divergence).

**Success criteria (all met):**
1. Plan passes adversarial scrutiny with verdict "Defensible" (no Critical or High findings remaining)
2. All frozen design decisions (D1-D9) are self-consistent and contract-aligned
3. Every handler code path produces correct state transitions
4. Contract amendments are explicitly scoped (D9 for `request_id`, D4 carve-out for parse failures)

## Session Narrative

**Phase 1 — Handoff load and initial review (~5 min).** Loaded the prior handoff. The plan was at 1903 lines on `feature/t05-pending-request-capture`. No code had been written — the plan was the only artifact.

**Phase 2 — Round 1 scrutiny: control-flow failures (~30 min).** User provided a comprehensive adversarial review identifying 5 findings (3 Critical, 2 High). I verified each against the actual code and specs before responding.

Confirmed findings:
- **Critical: Crash recovery claim false.** The plan at D2 and Task 6 claimed `job_creation` replay covered the unjournaled first-turn window. False — `recover_startup()` at `delegation_controller.py:496` only reconciles unresolved `intent`/`dispatched` entries. A crash after `update_status(job_id, "running")` leaves the job stuck.
- **Critical: No terminal runtime release.** Task 7 updated job status but never called `registry.release(runtime_id)` or closed the session. Completed/failed jobs leak runtimes and trip the busy gate.
- **High: Three-signal await unimplemented.** D6 declared three authoritative signals but the code only set unused booleans.
- **Critical: Unknown request auto-response.** The handler sent `{"permissions": {}}` for unknown requests, violating `recovery-and-journal.md:134` ("unknown requests are never auto-approved").
- **High: Second-request deadlock.** Handler returned `None` for request 2+, but the App Server blocks until it gets a response.

Partially confirmed: the `permissions` kind claim (4a) was wrong — the plan was consistent with the contract. The review misread the handler comment as adding a new kind.

Additionally identified mechanical defects: `journal._read_all` (nonexistent API), `delegate_escalate` (wrong audit action name), Task 3 description claiming dispatch before Task 7.

**Phase 3 — Round 1 amendments (~45 min).** 1903 → 2242 lines. Major changes:
- D2: replaced false recovery claim with orphaned-running-job detection
- Task 6: expanded from docstring-only to include `recover_startup()` implementation for orphaned `running` jobs
- Task 7 handler: complete rewrite with three strategies (cancel-capable, known no-cancel, `turn/interrupt` for unknown/parse-failures), always-respond for subsequent requests, terminal cleanup (release + close for completed/failed, keep live for `needs_escalation`)
- D6: added `_verify_post_turn_signals()` helper
- Task 2: added `interrupt_turn()` and `close()` to `AppServerRuntimeSession`
- Fixed all mechanical defects

**Phase 4 — Round 2 scrutiny: implementation contradictions (~20 min).** User identified 3 P1 and 2 P2 findings:
- **P1: Parse-failure path never reaches `needs_escalation`.** Handler returned `None` on parse failure (no `captured_request`), so the else branch turned it into `status="unknown"` + terminal cleanup instead of escalation.
- **P1: Integer request-id inconsistent in store.** Task 1 widened the parser but Task 5's store `_replay()` dropped non-string IDs.
- **P1: Bootstrap depends on nonexistent `control_plane.session_id`.** Regressed the existing `_read_session_id()` boundary.
- **P2: Objective-hash test assumes replay path that doesn't exist.** Busy gate fires before replay.
- **P2: Audit event missing `request_id`.** Contract requires it as a top-level field.

**Phase 5 — Round 2 amendments (~30 min).** Fixed all 5:
- Parse failure: creates minimal causal record from raw message envelope, returns `DelegationEscalation(pending_request=minimal)`
- Integer IDs: widened store types to `str | int`
- Bootstrap: restored `_read_session_id()` pattern
- Objective test: changed to direct `_delegation_request_hash()` verification
- Audit: added `request_id` via `extra` field

**Phase 6 — Round 3 scrutiny: contract-level contradictions (~15 min).** User identified 4 findings — no criticals, all contract-semantic:
- D6 says "MUST verify" but implementation only logs warnings
- `AuditEvent.request_id` is a top-level field in `contracts.md:196`, not an `extra` workaround
- Parse-failure `pending_request=None` has no `delegate.decide` story
- Integer `RequestId` contradicts contract's "plugin-assigned string"

**Phase 7 — Round 3 amendments (~25 min).** Contract closure:
- D6: downgraded to diagnostic-only observability (not a state-derivation gate)
- `AuditEvent`: added real `request_id: str | None = None` field (Step 5.1a)
- Parse failure: rewrote to preserve minimal causal record instead of `None`; `DelegationEscalation.pending_request` stays non-nullable
- Integer IDs: **normalize to string at parse boundary** instead of widening types. Eliminates type bifurcation entirely. Reverted all store type changes.
- Added D9 (frozen decision): `request_id` is the normalized wire id, not plugin-generated. Added contract amendment step (Step 6.7).
- Added D4 carve-out: parse-failure records stay `status="pending"` (no wire confirmation possible)
- Architecture summary, D3, Task 7 intro all aligned to three-strategy model

**Phase 8 — Round 4 scrutiny: last-mile consistency (~10 min).** User identified 3 findings:
- **P2: Step 3 test stale after Task 7.** `status == "queued"` assertion breaks when Task 7 adds dispatch.
- **P2: `request_id` semantic mismatch.** Contract says "plugin-assigned" but D9 says wire id.
- **P2: Parse-failure records weaken D4.** Synthetic IDs can't be confirmed by `serverRequest/resolved`.

Fixed: Step 3 test changed to `not isinstance(result, JobBusyResponse)`, D9 added to decisions table with contract amendment step, D4 carved out for parse failures with `parse_failed` flag.

**Phase 9 — Round 5 scrutiny: closure bug (~5 min).** User identified 1 P1:
- **P1: `parse_failed` not in `nonlocal` declaration.** The flag was a new local variable inside the handler closure, so the outer flag stayed `False`. D4 carve-out and D6 skip would not fire.

Also P2: Step 1.5 docstring still said "plugin-assigned" instead of D9 semantics.

Fixed: added `parse_failed` to `nonlocal`, rewrote docstring to match D9, strengthened parse-failure test to verify persisted store state.

**Phase 10 — Final scrutiny: Defensible.** No critical failures, no high-risk assumptions at the plan level. Remaining risks are runtime (nested `turn/interrupt` transport behavior, App Server cleanup ordering) — not plan coherence.

## Decisions

### Decision 1: Orphaned-running-job recovery via `recover_startup()`

**Choice:** After a cold restart, `recover_startup()` scans for jobs persisted as `"running"` and marks them `"unknown"`. The registry is fresh after restart — no live runtimes exist — so any running job is orphaned.

**Driver:** The plan's D2 says the first execution turn is intentionally unjournaled. A crash after `update_status(job_id, "running")` but before post-turn writes leaves the job `"running"` with no replay anchor. The existing `job_creation` journal path only reconciles unresolved `intent`/`dispatched` entries (`delegation_controller.py:496-566`).

**Alternatives considered:**
- **Journal the first turn** — adds `turn_dispatch` operation with idempotency key per `recovery-and-journal.md:49`. Rejected as excessive scope for v1 — multi-turn dispatch and replay become real requirements only with T-06.
- **Do nothing (original plan claim)** — claimed existing `job_creation` path covers it. Rejected because `job_creation.completed` is already resolved, so `list_unresolved()` won't return it.

**Trade-offs accepted:** A crash during the first turn loses the turn state. The job is marked `"unknown"`, not `"failed"` — `poll/discard/promote` can operate on it but the turn outcome is lost.

**Confidence:** High (E2) — verified against `recover_startup()` code and `list_unresolved()` semantics.

**Reversibility:** High — adding turn-dispatch journaling is additive.

**Change trigger:** T-06 (`codex.delegate.poll`), where multi-turn dispatch makes turn journaling load-bearing.

### Decision 2: Downgrade D6 from required boundary to diagnostic-only

**Choice:** `_verify_post_turn_signals()` logs warnings if `serverRequest/resolved` or target `item/completed` are missing from `turn_result.notifications`. This is observability, not a state-derivation gate. Job/request terminal state is derived from `turn/completed` status only.

**Driver:** Making state derivation depend on signal presence introduces complexity without clear v1 value: what do you DO when `serverRequest/resolved` is missing but the turn completed? The protocol doesn't guarantee signal ordering.

**Alternatives considered:**
- **Required boundary (original D6)** — block terminal state until all three signals seen. Rejected because the plan would need to define behavior for missing signals, adding a recovery path for a protocol edge case that may not occur.
- **Skip verification entirely** — no diagnostic. Rejected because protocol anomalies during development should be visible.

**Trade-offs accepted:** If `serverRequest/resolved` is genuinely missing (protocol bug), the plan marks the request "resolved" anyway based on the turn result. This could mask a protocol issue. Accepted because the diagnostic log catches it.

**Confidence:** High (E2) — verified that `turn/completed` is the reliable terminal signal per `codex-app-server.md:88`.

**Reversibility:** High — upgrading from diagnostic to required is additive (add conditional logic after the check).

**Change trigger:** If protocol ordering guarantees are added to the App Server spec, or if diagnostic logs show persistent signal absence in production.

### Decision 3: Normalize wire `RequestId` to string at parse boundary (D9)

**Choice:** `_require_request_id()` in `approval_router.py` accepts `str | int` from the wire and returns `str(value)`. The stored `request_id` is always a string. The normative contract at `contracts.md:81` is amended from "plugin-assigned unique identifier" to "wire request id, normalized to string."

**Driver:** The wire `RequestId` is `anyOf [string, integer]` per `ServerRequest.json:1475`. The contract says `request_id` is a `string`. Rather than widening the type everywhere (which would propagate into store, replay, and all consumers), normalize at the boundary.

**Alternatives considered:**
- **Widen to `str | int` everywhere** — attempted in Round 2. Created type bifurcation across store, replay, and consumers. Reverted in Round 3.
- **Keep `request_id` plugin-generated, add separate `wire_id`** — adds a field, creates a mapping layer. Rejected as over-engineering for v1.

**Trade-offs accepted:** Stringified integer IDs (e.g., `"42"`) are no longer wire-identical. The `respond()` transport layer still accepts `str | int` and preserves the original wire type for the response. The D6 diagnostic compares against the stored normalized string, which matches because `serverRequest/resolved` params are also parsed through the same normalizer.

**Confidence:** High (E2) — verified that `respond()` is wire-facing and the store is plugin-internal.

**Reversibility:** High — changing the normalization strategy only touches `_require_request_id()`.

**Change trigger:** If the App Server emits `serverRequest/resolved` with integer `requestId` that doesn't match the stored string — would require comparing both forms.

### Decision 4: Parse-failure causal records with D4 carve-out

**Choice:** When `parse_pending_server_request()` throws, the handler creates a minimal `PendingServerRequest` with `kind="unknown"`, whatever raw `id` and `method` could be extracted, and `status="pending"`. D4 (wire lifecycle → "resolved") does NOT apply to these records. D6 diagnostic does NOT run for them. The `parse_failed` flag (in `nonlocal`) governs both.

**Driver:** Parse-failure records have no wire response (the handler returns `None` and calls `turn/interrupt` instead). There is no `serverRequest/resolved` that can confirm closure. Marking them "resolved" would be semantically false.

**Alternatives considered:**
- **`pending_request=None`** — attempted in Round 2. Rejected because `needs_escalation` with no causal record gives `delegate.decide` nothing to operate on.
- **Skip persistence entirely** — rejected because the fail-closed contract says unknown requests must be captured and escalated.

**Trade-offs accepted:** The causal record is degraded — empty `codex_thread_id`, `codex_turn_id`, `item_id`. The `requested_scope` carries `{"raw_method": ...}` for diagnostics. If the raw message has no `id`, a plugin-generated fallback is used (not wire-correlated).

**Confidence:** High (E2) — verified that parse failure path now correctly toggles `parse_failed` via `nonlocal`, and the test checks persisted store state.

**Reversibility:** High — if the parser is later improved to extract more fields, the causal record gets richer.

**Change trigger:** If `delegate.decide` (T-06) needs richer context for parse-failure escalations.

### Decision 5: Three-strategy handler with `turn/interrupt` for unknowns

**Choice:** D3 amended from two strategies to three: (a) cancel-capable (`{"decision": "cancel"}`), (b) known no-cancel (`{"answers": {}}`), (c) unknown/unparseable (`turn/interrupt` → fail closed). Subsequent requests after the first always get a response (no deadlock) but are not persisted.

**Driver:** The original two-strategy design sent `{"permissions": {}}` for unknown requests, violating `recovery-and-journal.md:134` ("unknown requests are never auto-approved"). `turn/interrupt` is already in the required methods set (`codex_compat.py:78`) and produces the clean `status: "interrupted"` terminal state.

**Alternatives considered:**
- **Universal cancel** — not available across all request kinds (permissions has no `cancel` field).
- **Fabricated response for unknowns** — the original plan. Rejected because it auto-responds to requests the plugin doesn't understand.
- **Two strategies + skip unknowns** — the `return None` deadlock path. Rejected because the App Server blocks until it gets a response.

**Trade-offs accepted:** `turn/interrupt` is a heavier operation than a direct response — it's a client-initiated JSON-RPC request, not a response to the server request. The notification loop must handle the interrupt response arriving in-band.

**Confidence:** Medium (E1) — verified that `turn/interrupt` exists in the protocol and produces `interrupted` status. Not verified that it works correctly when called from inside the notification-handling loop (runtime risk, not plan risk).

**Reversibility:** Medium — changing the unknown-request strategy requires updating the handler, status derivation, and tests.

**Change trigger:** If live testing shows `turn/interrupt` from inside the notification loop causes transport issues. Fallback: use a sentinel response and interrupt after the loop.

## Changes

### `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` — Implementation plan

**Purpose:** Full implementation plan for the T-05 pending-request capture slice. Amended through 5 rounds of scrutiny from 1903 lines (original) to 2369 lines (final).

**Approach:** Surgical amendments to each finding — not a rewrite. Each round fixed specific issues, then the next round verified the fixes and caught new problems introduced by the amendments.

**Key changes by round:**

| Round | Verdict | Key fixes |
|-------|---------|-----------|
| 1 | Reject | Orphaned-job recovery, terminal runtime release, three-strategy handler, `turn/interrupt` for unknowns, deadlock fix |
| 2 | Reject | Parse-failure escalation path, integer ID end-to-end, bootstrap boundary, objective test, audit `request_id` |
| 3 | Major revision | D6 → diagnostic-only, `AuditEvent.request_id` real field, minimal causal record, normalize to string at boundary, D9 + contract amendment |
| 4 | Major revision | Step 3 test sequencing, D9 contract semantics, D4 carve-out for parse failures, prose alignment |
| 5 | Defensible | `nonlocal parse_failed`, D9-aligned docstring, persisted-state test assertion |

**Final plan state:** 2369 lines, 9 frozen decisions (D1-D9), 8 implementation tasks, all proof steps valid post-Task-7.

## Codebase Knowledge

### Files read / key findings this session

No new code files were read beyond what the prior session covered — this session operated on the plan and its cited authorities. The key locations are unchanged from the prior handoff.

| File | Purpose | Why read |
|---|---|---|
| `server/delegation_controller.py:496-566` | `recover_startup()` | Verified the recovery code only reconciles `intent`/`dispatched` — confirmed Finding 1 |
| `server/delegation_controller.py:219-228` | Busy check sources | Verified registry source (b) would trip for leaked runtimes — confirmed Finding 2 |
| `server/execution_runtime_registry.py:84` | `release()` method | Verified the seam exists but the plan never called it |
| `server/approval_router.py:45` | `_require_string(message, "id")` | Verified integer IDs would be rejected |
| `server/models.py:159-172` | `AuditEvent` dataclass | Verified `request_id` was missing (contract requires it at `contracts.md:196`) |
| `server/jsonrpc_client.py:82-87` | Notification routing | Verified server requests (with both `id` and `method`) route to `_notification_backlog` — the seam the handler operates on |
| `server/runtime.py:177-244` | `_run_turn()` notification loop | Verified the loop structure and where server request detection fits |
| `contracts.md:81` | `PendingServerRequest.request_id` | Verified contract says "plugin-assigned unique identifier" (amended by D9) |
| `contracts.md:196` | `AuditEvent.request_id` | Verified it's a top-level `string?` field, not an `extra` workaround |
| `recovery-and-journal.md:134` | Unknown request handling | Verified "unknown requests are never auto-approved" — drove the `turn/interrupt` fix |
| `codex-app-server.md:975-1000` | Approval flow protocol | Verified server request lifecycle, `serverRequest/resolved` semantics |
| `codex_compat.py:78` | Required methods | Verified `turn/interrupt` is in the required methods set |
| `ServerRequest.json:1475-1484` | `RequestId` schema | Verified `anyOf [string, integer]` |
| `codex_runtime_bootstrap.py:112-127` | Delegation factory | Verified `_read_session_id()` pattern — the bootstrap boundary the plan must preserve |

### Key locations (unchanged from prior handoff)

| Concept | Location |
|---|---|
| `recover_startup()` | `server/delegation_controller.py:496` |
| Busy check (3 sources) | `server/delegation_controller.py:219-228` |
| `_delegation_request_hash` | `server/delegation_controller.py:90` |
| `_run_turn` notification loop | `server/runtime.py:177-244` |
| `parse_pending_server_request` | `server/approval_router.py:37` |
| `_require_string` (needs replacement) | `server/approval_router.py:74` |
| `ExecutionRuntimeRegistry.release()` | `server/execution_runtime_registry.py:84` |
| `AuditEvent` dataclass | `server/models.py:159` |
| `PendingRequestKind` type | `server/models.py:16` |
| `JsonRpcClient.close()` | `server/jsonrpc_client.py:113` |
| `_build_delegation_factory` | `scripts/codex_runtime_bootstrap.py:112` |
| `_read_session_id` | `scripts/codex_runtime_bootstrap.py:113` |
| Implementation plan | `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` |

### Architecture: server request handler flow (amended)

```
_server_request_handler(message) — called from _run_turn() notification loop
  │
  ├─ try: parse_pending_server_request(message)
  │    │
  │    ├─ EXCEPT (parse failure):
  │    │    ├─ Create minimal PendingServerRequest(kind="unknown", raw id/method)
  │    │    ├─ Store if first capture
  │    │    ├─ Set interrupted_by_unknown=True, parse_failed=True (nonlocal)
  │    │    ├─ Call entry.session.interrupt_turn()
  │    │    └─ Return None (no wire response — turn/interrupt handles cleanup)
  │    │
  │    ├─ kind == "unknown" (parseable but unrecognized):
  │    │    ├─ Store if first capture
  │    │    ├─ Set interrupted_by_unknown=True (nonlocal)
  │    │    ├─ Call entry.session.interrupt_turn()
  │    │    └─ Return None
  │    │
  │    ├─ kind in cancel-capable (command_approval, file_change):
  │    │    ├─ Store if first capture
  │    │    └─ Return {"decision": "cancel"} (always, even for subsequent)
  │    │
  │    └─ kind in known no-cancel (request_user_input):
  │         ├─ Store if first capture
  │         └─ Return {"answers": {}} (always, even for subsequent)
  │
  POST-TURN STATUS DERIVATION:
  │
  ├─ captured_request is not None:
  │    ├─ D6 diagnostic (only if not parse_failed): _verify_post_turn_signals()
  │    ├─ D4 update_status("resolved") (only if not parse_failed)
  │    ├─ Derive job status: cancel-capable → needs_escalation
  │    │                      interrupted_by_unknown → needs_escalation
  │    │                      no-cancel + not completed → needs_escalation
  │    │                      no-cancel + completed → completed
  │    ├─ Emit audit: action="escalate", request_id=captured_request.request_id
  │    ├─ Terminal cleanup: completed/failed → release + close
  │    │                     needs_escalation → keep live
  │    └─ Return DelegationEscalation(job, pending_request, agent_context)
  │
  └─ captured_request is None:
       ├─ Derive job status: completed/failed/unknown from turn_result.status
       ├─ Terminal cleanup: release + close
       └─ Return DelegationJob
```

## Context

### Mental model

**Framing:** This session was an adversarial review loop, not implementation. The core problem was: "is this plan internally consistent and contract-aligned, or will it produce the same class of P1 bugs as the execution-start slice?"

**Core insight:** Plan-level contradictions cluster at three seams: (1) the boundary between the handler closure and the outer status derivation block (nonlocal state), (2) the boundary between the plan's code sketches and the normative contract (type semantics, field presence), and (3) the boundary between early-task proof steps and late-task behavior changes (test sequencing).

**Second insight:** Amendments introduce new contradictions. Each round of fixes was verified by the next round of scrutiny, which consistently found 1-3 new issues introduced by the fixes. The only reliable termination condition is "no remaining findings above P2."

### Project state

- **T-05 execution-start slice:** COMPLETE on main at `5ee7afb4`.
- **T-05 pending-request capture slice:** PLAN AMENDED. Plan at `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` on `feature/t05-pending-request-capture`. No implementation code written.
- **AC 6:** Still open. Will close when this slice is implemented and merged.
- **Sequencing:** pending-request capture → decide-surface + lifecycle → T-05 COMPLETE → T-06 → T-07.

### Environment snapshot

- Branch: `feature/t05-pending-request-capture`
- Main: `5ee7afb4` (unchanged — no implementation this session)
- Plugin suite: 666 tests (no code changes)
- Plan file: 2369 lines (was 1903 at start of session)

## Learnings

### Amendments introduce new contradictions at closure seams

**Mechanism.** Each round of fixes created 1-3 new issues. Round 1 fixes introduced: parse-failure path that never escalated, integer ID type bifurcation, bootstrap regression. Round 2 fixes introduced: D6 semantic contradiction, audit field mismatch, nullable `pending_request` decidability gap. Round 3 fixes introduced: nonlocal scope bug, stale docstring.

**Evidence.** 5 rounds, 15+ total findings. Roughly half were in the original plan; the other half were introduced by amendments.

**Implication.** Plan amendments need their own scrutiny cycle. Applying fixes without re-review is not safe. The "fix-review-fix" loop should be expected, not surprising.

### Normative contracts must be amended explicitly, not overridden in code

**Mechanism.** The plan repeatedly fixed code-level behavior while leaving the normative contract unchanged. Examples: `request_id` type widened in code but contract still said `string`; `AuditEvent` used `extra` workaround when the contract already defined a top-level field; D6 said "MUST verify" while the implementation logged warnings.

**Evidence.** Three rounds of scrutiny identified contract drift. Each time, the fix was either to update the contract or to explicitly state the code-level departure as a design decision.

**Implication.** When a plan changes code semantics that touch a contract, the amendment must include the contract update. Code-first, contract-later creates exactly the drift this repo's design philosophy prohibits.

### Python closures require explicit `nonlocal` for mutable outer state

**Mechanism.** Assigning to a variable inside a nested function creates a new local binding. Without `nonlocal`, the outer variable is shadowed, not mutated.

**Evidence.** The `parse_failed = True` assignment inside `_server_request_handler` created a local variable. The outer `parse_failed` stayed `False`, so the D4 carve-out and D6 skip never fired.

**Implication.** Any closure that needs to mutate outer state must declare all mutated names in `nonlocal`. This is a mechanical check, not a design judgment — should be caught by review.

## Next Steps

### 1. Execute the pending-request capture plan

**Dependencies:** Plan complete and scrutiny-passed on `feature/t05-pending-request-capture`.

**What to read first:** `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` — all 8 tasks with exact code. Pay attention to the D1-D9 frozen decisions table (lines 19-30) and the Risks and Known Deferrals table (lines 2214+).

**Approach:** Use `superpowers:subagent-driven-development` with full two-stage review (spec compliance + code quality) per task. Same pattern as the execution-start slice.

**Task dependency order:**
- Tasks 1, 2 are independent primitives (parallelizable)
- Tasks 3, 4, 5 depend on Tasks 1-2 but are independent of each other
- Task 6 is the design checkpoint + orphaned-job recovery
- Task 7 depends on Tasks 1-6
- Task 8 depends on Task 7

**Known plan-level risks that remain:**
- `turn/interrupt` from inside the notification loop is untested at the transport level. If it doesn't work, the fallback is to use a sentinel response and interrupt after the loop.
- The approval-policy probe (Task 8) gates the core slice behavior. If `on-request` doesn't generate server requests, default to `untrusted`.

### 2. Post-merge integration review (after all tasks pass)

Same as prior handoff — full-slice integration review against the complete diff.

### 3. Remaining T-05 sequencing

After AC 6 closes: decide-surface + lifecycle refinements → T-05 COMPLETE → T-06 → T-07.

## In Progress

**Clean stopping point.** Plan amendments complete, scrutiny passed with "Defensible" verdict. No implementation code written or in flight.

- **Completed:** 5 rounds of adversarial scrutiny, 15+ findings addressed, plan expanded from 1903 to 2369 lines, 9 frozen design decisions (D1-D9).
- **Not in flight:** No code changes.
- **Next action for next-session Claude:** Read the plan. Execute using `superpowers:subagent-driven-development`. Start with Task 1 (JSON-RPC respond + integer ID fix) or Task 2 (turn widening + `interrupt_turn` + `close`) — they're independent.

## Open Questions

### 1. `turn/interrupt` transport re-entrancy

**Context.** The handler calls `entry.session.interrupt_turn()` from inside the `_server_request_handler` callback, which is called from inside the `_run_turn()` notification loop. `interrupt_turn()` sends a `turn/interrupt` JSON-RPC request via `self._client.request()`, which reads from the same stdout stream. The notification loop is also reading from stdout.

**Impact:** Medium. If the transport doesn't handle this re-entrant read pattern, the handler will deadlock or produce garbled messages.

**Decision pending until:** Implementation and testing in Task 7. The `_FakeSession` tests don't exercise the real transport. If it fails, the fallback is to return a sentinel from the handler and call `interrupt_turn()` after the loop exits.

### 2. `on-request` operational semantics (unchanged)

Same as prior handoff. Live probe in Task 8.

## Risks

### 1. Nested `turn/interrupt` transport safety

**Impact.** If `turn/interrupt` from inside the notification handler causes transport issues, the entire unknown-request strategy breaks.

**Mitigation.** The fallback (documented in D5's "change trigger") is to return a sentinel response from the handler and interrupt after the loop. This is a code change, not a design change.

**Action.** Test during Task 7 implementation. If the fake tests pass but real transport fails, switch to sentinel approach.

### 2. Plan mechanical gaps

**Impact.** The execution-start plan had mechanical gaps in Tasks 1, 6, 7 (missing imports, missing attribute declarations). This plan is longer (2369 lines) and has been through more amendments, so mechanical gaps are likely.

**Mitigation.** Pre-identification pass before each task dispatch (same pattern as execution-start).

**Action.** Implementer should verify all referenced symbols exist before implementing each task.

### 3. `_FakeSession` complexity

**Impact.** The fake session now has `run_execution_turn()`, `interrupt_turn()`, `close()`, and interrupt-aware turn result override. This is significantly more complex than the prior session fake. Existing tests may need updates.

**Mitigation.** Task 7 includes explicit steps for updating `_FakeSession` and `_FakeControlPlane`. Run the full suite after each step.

**Action.** Run full suite after Step 7.6 (`_build_controller` update) — this is where existing test breakage surfaces.

## References

### Authority documents

| Document | Location | Role |
|---|---|---|
| T-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth (AC 6 at line 323) |
| T-05 pending-request plan | `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` | This slice's implementation plan (amended) |
| Recovery spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Pending request ordering (line 125), unknown request handling (line 134) |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | `PendingServerRequest` schema (line 77), `AuditEvent` schema (line 188) |
| App Server docs | `docs/codex-app-server.md` | Approval flow (line 975), `turn/interrupt` (line 158) |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-19_13-00_t05-pending-request-capture-plan-complete-ready-for-execution.md`
- T-05 arc: execution-start slice COMPLETE → pending-request capture PLANNED → **scrutiny + amendments (this handoff)** → execute plan → decide-surface + lifecycle → T-05 COMPLETE

## Gotchas

### 1. `nonlocal` required for closure state mutation

**Symptom.** `parse_failed = True` inside the handler doesn't affect the outer scope. D4 carve-out and D6 skip silently fail.

**Root cause.** Python closures can read outer variables without `nonlocal`, but assignment creates a new local binding.

**Prevention.** The handler's `nonlocal` declaration now includes `captured_request, interrupted_by_unknown, parse_failed`. Any future additions to the handler's mutable outer state must be added to this declaration.

### 2. Contract amendments must be explicit plan steps

**Symptom.** Code changes that widen types or add fields don't match the normative contract. Scrutiny catches the drift rounds later.

**Root cause.** Plan amendments focus on code behavior and forget the corresponding contract text.

**Prevention.** When a plan amendment touches a type, field, or semantic that is defined in `contracts.md` or `recovery-and-journal.md`, add a contract amendment step in the same task.

### 3. Early proof steps may be invalidated by later tasks

**Symptom.** Step 3.1 asserts `status == "queued"`, but Task 7 changes `start()` to dispatch a turn, making the returned status `"completed"`.

**Root cause.** Tests written for pre-dispatch behavior don't account for post-dispatch changes.

**Prevention.** When writing early proof steps, assert only the property being tested (e.g., "objective is accepted") and explicitly note that status depends on later tasks.

## Conversation Highlights

### Scrutiny-driven amendment loop

The session was structured as a review loop: user provides adversarial scrutiny → I verify each finding against the code → fix confirmed findings → user scrutinizes the fixes → repeat. Five rounds. The user's scrutiny was evidence-based (specific line numbers, schema references, control-flow traces) and the findings consistently improved quality.

### Verdicts progression

Round 1: Reject (3 Critical, 2 High) → Round 2: Reject (3 P1, 2 P2) → Round 3: Major revision (0 Critical, 4 High) → Round 4: Major revision (0 Critical, 3 P2) → Round 5: Defensible (1 P1 closure bug, 1 P2 stale text).

### Key corrections from user

- Round 1: "For Finding 1, phrase the fix as startup orphan reconciliation for persisted `running` jobs after a cold restart, not 'check for no live registry entry' in the normal live path."
- Round 1: "For Findings 4c/4d, the amendment cannot just say 'fail closed better.' It needs an explicit mechanism. The only credible fail-closed path is probably to introduce an interrupt path."
- Round 3: "Fix the `request_id` semantic story explicitly. Either amend the contract so `request_id` is the normalized wire id, or keep `request_id` plugin-assigned and add a separate wire request id field."

## User Preferences

### Adversarial review precision

User provides deeply structured adversarial reviews with specific file:line citations, schema references, and control-flow traces. Findings are prioritized (Critical/High/Medium/P1/P2) and each includes "how it fails in practice" and "what would need to change."

### Contract authority

User treats normative contracts (`contracts.md`, `recovery-and-journal.md`) as the authority layer. Code that disagrees with the contract is a bug, even if the code is operationally correct. "That is exactly the kind of quiet drift this repo tries to prevent."

### Explicit mechanism over general guidance

When user says "the amendment cannot just say 'fail closed better,'" they mean: name the specific mechanism, not the principle. In this case: `turn/interrupt`, not "an explicit fail-closed strategy."

### Prose alignment matters

User catches and flags wording drift across sections — architecture summary, decision tables, task descriptions, and commit messages must all describe the same behavior. "The operator-facing prose is still inconsistent" is a real finding, not a nit.

## Rejected Approaches

### Widening `request_id` to `str | int` everywhere

**Approach.** Accept integer request IDs as-is through the entire stack — parser, store, model, tests.

**Why it seemed promising.** Direct wire fidelity. No information loss from normalization.

**Why rejected.** Created type bifurcation across 6+ touchpoints. The store's `_replay()` dict key type, `get()` parameter, `update_status()` parameter, all consumers, and the contract all needed updating. User: "Stop carrying both models at once." The contract says `request_id` is a `string`.

**What it taught.** Normalize at the boundary, not at every consumer. The plugin owns the stored representation; the wire type doesn't dictate the storage type.

### `DelegationEscalation.pending_request = None` for parse failures

**Approach.** Return `DelegationEscalation` with `pending_request=None` when the server request couldn't be parsed.

**Why it seemed promising.** Simple — no need to construct a minimal record from a malformed message.

**Why rejected.** Creates a `needs_escalation` state with no decidable payload. `codex.delegate.decide` has nothing to operate on. User: "A `needs_escalation` state with `pending_request=None` needs an explicit operator/decide story."

**What it taught.** Even for degraded paths, preserve whatever causal context exists. The raw message still has `id` and `method` — those are enough for a minimal record.

### D6 as a required state-derivation boundary

**Approach.** Make missing `serverRequest/resolved` or `item/completed` signals block terminal state transitions.

**Why it seemed promising.** Matches the original design session's intent — "all three are authoritative boundaries."

**Why rejected.** Introduces complexity without v1 value. The plan would need to define behavior for missing signals: wait? timeout? mark unknown? Each option adds recovery logic for a protocol edge case. User: "either make missing D6 signals affect state derivation, or explicitly downgrade D6."

**What it taught.** "MUST verify" in a design decision must be backed by implementation that actually gates behavior on the result. If the implementation only logs, the decision should say "diagnostic," not "required."
