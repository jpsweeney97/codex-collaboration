---
date: 2026-04-19
time: "16:26"
created_at: "2026-04-19T20:26:10Z"
session_id: da98f0d0-f080-4325-8b01-0e3873e95b4c
resumed_from: "docs/handoffs/archive/2026-04-19_15-13_t05-pending-request-capture-implemented-and-reviewed.md"
project: claude-code-tool-dev
branch: main
commit: 271f23aa
title: "T-05 closed — review fixes merged, T-06 decide-surface opening slice scoped"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md
  - docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md
  - docs/plans/2026-04-19-t05-pending-request-capture-slice.md
---

# T-05 Closed — Review Fixes Merged, T-06 Decide-Surface Opening Slice Scoped

## Goal

Close T-05 (execution-domain foundation) by addressing PR #108 review comments, merging to main, and scoping the T-06 opening slice. T-05 ticket: `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md`. T-06 ticket: `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`.

**Trigger:** Prior handoff said "plan amended through scrutiny, implemented, reviewed, PR published at jpsweeney97/claude-code-tool-dev#108." User opened this session with `/load` and directed review fix work.

**Stakes:** AC 6 (pending-request capture) was the final acceptance criterion for T-05. Merging PR #108 closes the ticket and unblocks T-06. The review comments from the Codex bot identified two real execution-semantic bugs that would have caused misrouted callers and stale state.

**Success criteria (all met):**
1. Both Codex bot review comments addressed with tested fixes
2. 5-agent comprehensive PR review run, findings triaged with user
3. Tier 1 findings (stale docs, D6 latent bug, observability, type hygiene) fixed
4. PR #108 merged to main at `271f23aa` (15 commits, 698 tests)
5. T-05 closed, feature branch deleted
6. T-06 opening slice scoped: `codex.delegate.decide` for live escalations

## Session Narrative

**Phase 1 — Handoff load and review comment triage (~10 min).** Loaded the prior handoff (T-05 pending-request capture implemented and reviewed). User said "there are a couple review comments on PR #108." Fetched PR state and both inline comments from the Codex bot (`chatgpt-codex-connector[bot]`).

Two P2 findings:
1. `_finalize_turn()` returns `DelegationEscalation` unconditionally when any request is captured, even for completed jobs. MCP layer's `isinstance` check then reports `escalated: true` for a completed job with a closed runtime.
2. `parse_failed` flag is turn-scoped but used as request-scoped — a later malformed message prevents resolution of a successfully-parsed first request.

Verified both against the code by reading `_finalize_turn()` at `delegation_controller.py:688`, the handler closure at `delegation_controller.py:559`, and the MCP serialization at `mcp_server.py:339-345`. Both are real: the code path for `request_user_input` + completed turn returns `DelegationEscalation` with a closed runtime, and `parse_failed = True` at line 591 is unconditional even when `captured_request` is already set.

**Phase 2 — Execution-semantic fixes (~15 min).** User approved implementation with specific guidance:
- In `_finalize_turn()`, only emit escalation audit, keep runtime live, and return `DelegationEscalation` when `final_status == "needs_escalation"`. Otherwise release/close and return `DelegationJob`.
- Replace `parse_failed` with `captured_request_parse_failed`, scoped to `captured_request is None` branch only.
- User: "I would not use this comment as license to redesign later-message interruption semantics unless you have explicit plan/contract authority for that."

Implemented both fixes. Added two regression tests:
- `test_start_with_request_user_input_completed_returns_delegation_job` — verifies `request_user_input` + completed turn returns `DelegationJob`, runtime closed, pending request resolved, no escalation audit.
- `test_later_parse_failure_does_not_prevent_captured_request_resolution` — verifies first parsed request is resolved even when a later message fails parse.

698 tests passing (696 baseline + 2 new). Committed as `526075b4`.

**Phase 3 — 5-agent comprehensive PR review (~8 min).** User requested `/pr-review-toolkit:review-pr`. Launched 5 agents in parallel:
- **code-reviewer**: No critical or important issues. Correctness verified across all 21 files.
- **silent-failure-hunter**: 2 critical (cleanup `except` blocks swallow errors, parse `except` too broad), 4 important (handler failures, JSONL replay, update_status, pre-existing drops).
- **pr-test-analyzer**: 3 critical (no failed/unknown turn test, no file_change test, handler responses not asserted), 4 important (D6 untested, UUID fallback untested, approval_policy not verified, MCP unit test gap).
- **type-design-analyzer**: 1 critical (`entry: Any` and `turn_result: Any` erase type checking), 3 important (TurnStatus invisible, update_status parameter type, str() widening).
- **comment-analyzer**: 3 critical (module docstring factually wrong, flow omits capture loop, DelegationJob docstring stale), 3 important (D6 correlation type mismatch, DelegationEscalation docstring, schema line number).

**Phase 4 — Triage with user (~5 min).** User reviewed the aggregate and re-prioritized:

User's P2 finding: "D6 request-id correlation has a real latent mismatch. `params.get('requestId')` is compared directly against the normalized stored `request_id`; `_require_request_id()` normalizes wire ids to `str`, so an on-wire integer `42` will never equal `'42'`."

User's overstated assessment: "C6 is only partially right. The lack of logging is real. The recommendation to narrow `except Exception` to `RuntimeError` is not obviously correct. That branch is implementing a fail-soft contract."

User's disposition:
- Fix before merge: C1, C2, C3, I2, I1, C5, C4
- Modify rather than accept: C6 — add logging, keep broad catch
- Defer: I3, I4, I5, I6, I7, and suggestions

User: "The packet is useful, but the right reading is: one real latent code defect in a non-fatal diagnostic path, several stale docstrings in authority surfaces, and a worthwhile observability cleanup. I do not see a new blocker in the execution semantics."

**Phase 5 — Tier 1 fixes (~10 min).** Implemented 7 changes:
1. I1: Null-safe `str()` normalization in `_verify_post_turn_signals` — `raw_request_id = params.get("requestId")` then `str(raw_request_id) == request_id` when present.
2. C1+C2: Rewrote module docstring — added "First-turn dispatch + capture" section, removed stale "does NOT dispatch" claim.
3. C3: Removed stale "later slices" paragraph from `DelegationJob` docstring.
4. I2: Qualified `DelegationEscalation` docstring for parse-failure carve-out (`status="pending"`).
5. C5: Added `logger.error(...)` with `exc_info=True` in 6 cleanup `except` blocks.
6. C6: Added `logger.warning(...)` with `exc_info=True` in parse-failure `except`, kept broad catch.
7. C4: Replaced `Any` with `ExecutionRuntimeEntry` and `TurnExecutionResult` in `_finalize_turn`.

698 tests, zero behavioral changes. User reviewed the diff: "No findings. The patch stayed bounded to the agreed surfaces." Committed as `f765a347`.

**Phase 6 — Merge and cleanup (~5 min).** Pushed both commits to update PR #108. User merged via GitHub UI. Fetched main at `271f23aa`, deleted feature branch locally and on remote.

**Phase 7 — T-05/T-06 boundary correction (~5 min).** I initially described next steps as "decide-surface + lifecycle → T-05 COMPLETE → T-06." User corrected this: T-05 ticket at `execution-domain-foundation.md:52` explicitly scopes out poll/decide/promote. Those are T-06 at `promotion-flow-and-delegate-ux.md:32`. AC 6 landing on main means T-05 is functionally complete.

User provided a detailed T-06 opening packet with scope, design locks, and recommended shape. Key design lock: `codex.delegate.decide` is not a late wire reply to the original App Server request. It consumes a plugin-side causal record and a `needs_escalation` job. Approve means resume execution in the retained runtime. Deny means terminate.

## Decisions

### Decision 1: Restructure _finalize_turn to gate escalation on final_status

**Choice:** Only emit escalation audit, keep runtime live, and return `DelegationEscalation` when `final_status == "needs_escalation"`. For completed jobs with captured requests: resolve the stored request, release+close, return `DelegationJob`.

**Driver:** Codex bot P2 review finding — `request_user_input` + completed turn returns `DelegationEscalation` with a closed runtime. MCP layer at `mcp_server.py:339` turns this into `"escalated": true` purely from the result type. User: "That is inconsistent with the `DelegationEscalation` contract in models.py and points callers at a dead `decide` path."

**Alternatives considered:**
- **Add a status field to DelegationEscalation** — would let MCP server check status rather than type. Rejected as over-engineering: the type itself should carry the semantic.
- **Change MCP serialization to check job.status** — moves the fix to the wrong layer; the controller should not return an escalation for a completed job.

**Trade-offs accepted:** Captured `request_user_input` requests that complete normally now lose the `pending_request` and `agent_context` from the return value. The caller gets a plain `DelegationJob` and must look up the pending request separately if needed. Acceptable because the job is completed — there's nothing to decide.

**Confidence:** High (E2) — user manually verified both `request_user_input` completion and escalation paths work correctly. Two regression tests confirm.

**Reversibility:** High — the method extraction is a refactor. If future callers need the pending_request for completed jobs, add it to `DelegationJob` or create a new return type.

**Change trigger:** If callers need the `pending_request` causal record even for completed jobs (e.g., for audit trail rendering).

### Decision 2: Scope parse_failed to captured request only

**Choice:** Renamed `parse_failed` to `captured_request_parse_failed` and moved the assignment inside the `if captured_request is None` branch, so only the first/captured request's parse failure affects the D4 resolution gate.

**Driver:** Codex bot P2 finding — `parse_failed` was turn-scoped but used as request-scoped. A later malformed message prevented resolution of a successfully-parsed first request. User: "The bug is exactly at 587-591: `parse_failed` is tracking 'any parse failure in the turn,' while `_finalize_turn()` uses it as if it meant 'the captured request was a parse failure.'"

**Alternatives considered:**
- **Track parse failure per-message in a list** — would require changing the handler's state model. Rejected by user as scope creep: "I would not use this comment as license to redesign later-message interruption semantics."

**Trade-offs accepted:** `interrupted_by_unknown` remains unconditional — a later parse failure still forces escalation (correct, because we interrupted the turn). Only the resolution gate is scoped to the captured request.

**Confidence:** High (E2) — regression test `test_later_parse_failure_does_not_prevent_captured_request_resolution` confirms the first request is resolved even when a later message fails parse.

**Reversibility:** High — naming change only, no behavioral model change.

**Change trigger:** If multiple server requests need independent parse-failure tracking (would require the list approach).

### Decision 3: Keep broad parse catch, add logging only

**Choice:** Keep `except Exception` in the parse-failure handler. Add `logger.warning(..., exc_info=True)` for observability. Do not narrow to `RuntimeError`.

**Driver:** User: "The recommendation to narrow `except Exception` to `RuntimeError` is not obviously correct. That branch is implementing a fail-soft contract: if request projection fails, preserve a minimal causal record and interrupt the turn. A broad catch supports that contract even if the parser later regresses with `TypeError` or `ValueError`."

**Alternatives considered:**
- **Narrow to RuntimeError** — recommended by silent-failure-hunter agent. Rejected by user because it would break the fail-soft contract if the parser evolves to raise different exceptions.

**Trade-offs accepted:** `MemoryError` and `RecursionError` are caught by the broad handler. In practice, these would be re-raised by the outer turn-dispatch guard, but the handler creates a minimal causal record first.

**Confidence:** High (E1) — user's reasoning is sound. The fail-soft contract is intentional.

**Reversibility:** High — narrowing the catch is a one-line change if the parser-failure contract is formalized and tested.

**Change trigger:** If the team wants to formalize and test a tighter parser-failure contract with explicit exception types.

### Decision 4: T-05 is complete, decide-surface is T-06

**Choice:** Close T-05 with AC 6 merged. The decide-surface, poll, promote, and lifecycle consumers are T-06.

**Driver:** User: "If we use the repo's formal ticket boundaries, `T-20260330-05` explicitly scopes `codex.delegate.poll`, `codex.delegate.decide`, and `codex.delegate.promote` out of T-05 in `execution-domain-foundation.md:52`. Those surfaces are in T-06 in `promotion-flow-and-delegate-ux.md:32`."

**Alternatives considered:**
- **Continue calling it "T-05 arc"** — would conflate implementation continuity with ticket boundaries. Rejected because "the tickets are the contract boundary."

**Trade-offs accepted:** None — this is a naming/boundary correction, not a behavioral choice.

**Confidence:** High (E2) — verified against both ticket documents.

**Reversibility:** N/A — naming convention.

**Change trigger:** N/A.

## Changes

### `server/delegation_controller.py` — Three categories of changes

**Execution-semantic fixes (commit `526075b4`):**
- `_finalize_turn()` restructured: escalation audit + `DelegationEscalation` return only when `final_status == "needs_escalation"`. Non-escalation path releases runtime, closes session, returns `DelegationJob`.
- `parse_failed` → `captured_request_parse_failed`, assignment scoped to `captured_request is None` branch.

**Review findings fixes (commit `f765a347`):**
- Module docstring rewritten: added "First-turn dispatch + capture" flow section, removed stale "does NOT dispatch" claim.
- `_finalize_turn` parameters: `entry: Any` → `ExecutionRuntimeEntry`, `turn_result: Any` → `TurnExecutionResult`. Both types added to imports.
- Parse-failure handler: added `logger.warning(...)` with `exc_info=True` preserving the parse reason.
- Turn-dispatch cleanup guard (lines 657-680): 3 `except Exception: pass` blocks → `logger.error(...)` with context and `exc_info=True`.
- Finalization cleanup guard (lines 695-710): same pattern, 3 blocks.
- `_verify_post_turn_signals()`: D6 correlation fixed with null-safe normalization — `raw_request_id = params.get("requestId")`, compare `str(raw_request_id) == request_id` only when present.

### `server/models.py` — Docstring corrections

- `DelegationJob` docstring: removed stale "This slice writes status at creation time only. Lifecycle transitions land in later slices" paragraph. Replaced with: "Status transitions are managed by DelegationController and recover_startup()."
- `DelegationEscalation` docstring: qualified status claim. For parsed requests `status == "resolved"` (D4). For parse failures `status == "pending"` (D4 carve-out).

### `tests/test_delegation_controller.py` — Two new tests + helper

- Added `_request_user_input_request()` helper (mirrors `_command_approval_request()` pattern).
- `test_start_with_request_user_input_completed_returns_delegation_job`: `request_user_input` + completed turn → `DelegationJob`, runtime closed, pending request resolved, no escalation audit.
- `test_later_parse_failure_does_not_prevent_captured_request_resolution`: first parsed request is resolved even when later message fails parse; job still escalates due to `interrupted_by_unknown`.

## Codebase Knowledge

### Architecture: _finalize_turn Exit Paths (Post-Fix)

```
_finalize_turn(captured_request, interrupted_by_unknown, captured_request_parse_failed)
│
├─ captured_request is not None:
│    ├─ D6 diagnostic (if not captured_request_parse_failed)
│    ├─ D4 update_status("resolved") (if not captured_request_parse_failed)
│    ├─ Status derivation:
│    │    ├─ cancel-capable OR interrupted_by_unknown → needs_escalation
│    │    ├─ turn completed → completed
│    │    └─ else → needs_escalation
│    │
│    ├─ IF needs_escalation:
│    │    ├─ Emit escalation audit
│    │    ├─ Re-read request from store (authoritative status)
│    │    ├─ Keep runtime live
│    │    └─ Return DelegationEscalation
│    │
│    └─ ELSE (completed):
│         ├─ Release runtime + close session
│         └─ Return DelegationJob
│
└─ captured_request is None:
     ├─ completed → "completed"
     ├─ failed → "failed"
     ├─ else → "unknown"
     ├─ Release + close
     └─ Return DelegationJob
```

### Key Locations (Post-Fix)

| Concept | Location |
|---------|----------|
| Escalation-gated return | `delegation_controller.py:740-770` |
| Non-escalation completion path | `delegation_controller.py:772-775` |
| D6 null-safe correlation | `delegation_controller.py:915-918` |
| Parse-failure logging | `delegation_controller.py:577-583` |
| Turn dispatch cleanup logging | `delegation_controller.py:657-680` |
| Finalization cleanup logging | `delegation_controller.py:695-710` |
| `_finalize_turn` typed parameters | `delegation_controller.py:724-725` |

### Patterns Observed

- **Cleanup guard pattern:** Both turn-dispatch and finalization failures use the same three-step best-effort cleanup: mark job "unknown", release runtime, close session. Each step is independently guarded and now logged. The primary exception is re-raised — cleanup is observability, not suppression.
- **First-capture semantics:** The handler stores only the first server request. Subsequent requests are handled inline but not persisted. `captured_request_parse_failed` applies only to the first capture.
- **Type erasure at method boundaries:** The `_finalize_turn` extraction originally used `Any` for `entry` and `turn_result` to avoid import complexity. Both types (`ExecutionRuntimeEntry`, `TurnExecutionResult`) were already transitively available — the `Any` was an oversight, not a design choice.

### D6 Correlation Fix Detail

The `_verify_post_turn_signals` function at `delegation_controller.py:905` compares `params.get("requestId")` against the stored `request_id`. The approval router's `_require_request_id()` at `approval_router.py:83` normalizes wire IDs to `str`. If the App Server sends `requestId: 42` (integer) in a `serverRequest/resolved` notification, the comparison `42 == "42"` is `False` in Python. The fix normalizes with `str(raw_request_id)` only when the value is present, avoiding `str(None)` → `"None"`.

## Context

### Mental Model

This session was a **review-fix-merge cycle** with a scope correction at the end. The two execution-semantic bugs (completed-job-returning-escalation and turn-scoped parse_failed) were the highest-value fixes. The 5-agent review surfaced one additional latent code defect (D6 type mismatch) plus doc/observability debt. The user's triage demonstrated a clear severity calibration: stale docs and type hygiene are maintenance debt, not critical defects.

### Project State

- **T-05:** COMPLETE. Both slices merged to main. 698 tests.
- **T-06:** Scoped but not started. Opening slice: `codex.delegate.decide` for live escalations.
- **PR #108:** Merged at `271f23aa`. 15 commits total (13 original + 2 review fixes).
- **Branch:** `main` at `271f23aa`. Feature branch `feature/t05-pending-request-capture` deleted.

### T-06 Opening Slice Scope (User-Defined)

**Goal:** Add `codex.delegate.decide` as the first consumer of the landed escalation substrate.

**In scope:**
- Add `codex.delegate.decide` to the MCP surface
- Resolve a live execution-domain escalation for a job in `needs_escalation`
- Reuse existing `DelegationJob` + `PendingServerRequest` causal record
- Emit approval-resolution audit records per `contracts.md:188`
- Move job out of `needs_escalation`: approve (resume execution) or deny (terminate)
- Typed rejection responses for invalid decide attempts

**Explicitly out of scope:**
- `codex.delegate.poll`
- Crash-restart inspection for `unknown` jobs
- Promotion prechecks, artifact hash, rollback, stale-advisory-context marking
- Delegate skill UX
- General worktree cleanup/discard flows beyond what deny needs immediately

**Critical design lock:** User: "`codex.delegate.decide` is not a late wire reply to the original App Server request. T-05 already treated `PendingServerRequest.status` as wire lifecycle, not plugin escalation lifecycle, and the pending-request plan explicitly deferred that distinction to T-06 at `2026-04-19-t05-pending-request-capture-slice.md:2364`."

**Semantic contract:**
- `approve` = resume execution in the still-live runtime with a follow-up turn carrying Claude's resolution
- `deny` = terminate the execution path, make job terminal
- `PendingServerRequest.status` does not change (already reflects wire resolution)
- `unknown` remains a crash/recovery state, not a denial state
- Denial maps to `failed`, not `unknown`

**Scope constraint:** User: "Decide-first only works cleanly if the packet explicitly limits itself to live same-session escalations. If you want cross-session rediscovery, inspection of `unknown` jobs, or restart-from-brief, that is no longer 'decide plus the lifecycle consumers it needs.' That becomes a combined `poll + decide` packet."

**Recommended packet shape:** User: "I would scope the first T-06 packet as: packet name `T-06 opening slice: codex.delegate.decide for live escalations`. Primary files: `mcp_server.py`, `delegation_controller.py`, `models.py`, `test_delegation_controller.py`, `test_mcp_server.py`. Acceptance boundary: a `codex.delegate.start` escalation can be approved or denied through `codex.delegate.decide`; approve re-dispatches execution in the retained runtime, deny terminates cleanly, invalid decide attempts return typed rejections, and no promotion behavior is introduced."

## Learnings

### Multi-agent reviews catch cross-subsystem bugs that single-pass reviews miss

**Mechanism:** The D6 correlation mismatch (I1) is a type-boundary bug hiding at the intersection of approval_router's normalization and the D6 diagnostic's comparison. The comment-analyzer spotted it via docstring accuracy ("docstring claims correlation works"). The type-design-analyzer spotted it via the Literal enforcement gap. Neither agent saw the full picture alone, but both independently flagged the same location.

**Evidence:** Comment-analyzer finding I1 and type-design-analyzer finding I1 both reference the `_require_request_id`/`_verify_post_turn_signals` interaction.

**Implication:** For code that crosses subsystem boundaries (normalization in one module, comparison in another), multi-agent reviews with different lenses are more effective than single comprehensive reviews.

### Review agent severity calibration requires human triage

**Mechanism:** The agents labeled 6 findings as "critical," but the user's assessment was: "The packet's 'critical issues' label is inflated. C1-C3 are stale docs, C4 is type hygiene, C5 is observability, and C6 is half observability / half debatable design guidance. None of those are critical in the same sense as the two real execution bugs you already fixed."

**Evidence:** User's triage re-prioritized: stale docs and type hygiene are P3 (fix before merge), not critical. The two Codex bot findings (execution-semantic bugs) were the actual P2s.

**Implication:** Agent review output should be presented as findings for human triage, not as a severity-ordered action list. The human's context (what constitutes "critical" for this project, this PR, this merge timeline) is necessary for correct prioritization.

### Ticket boundaries are contract boundaries, not implementation-arc boundaries

**Mechanism:** I described "decide-surface + lifecycle → T-05 COMPLETE" when the T-05 ticket explicitly scopes out poll/decide/promote at `execution-domain-foundation.md:52`. Those surfaces are T-06 at `promotion-flow-and-delegate-ux.md:32`.

**Evidence:** User: "If we use the repo's formal ticket boundaries, your earlier sequence is not the current contract."

**Implication:** When referencing "what's next," use the ticket's explicit scope boundary, not the implementation plan's deferred-work list. The deferred work is deferred *to the next ticket*, not within the current one. Getting this wrong in a handoff causes the next session to treat a closed ticket as incomplete.

## Next Steps

### 1. Write T-06 opening slice plan

**Dependencies:** None — scope is defined in the Context section above.

**What to read first:**
- T-06 ticket: `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`
- Existing substrate: `delegation_controller.py` (escalation return path at line 740-770), `mcp_server.py` (escalation serialization at line 339-345), `models.py` (`DelegationEscalation` at line 347)
- Contracts: `docs/superpowers/specs/codex-collaboration/contracts.md` (audit schema at line 188)
- Pending-request plan deferred items: `docs/plans/2026-04-19-t05-pending-request-capture-slice.md:2361-2364`

**Approach:** Write an implementation plan at `docs/plans/2026-04-19-t06-decide-surface-opening-slice.md` following the same structure as the T-05 plans. Define frozen design decisions for approve/deny semantics, MCP tool schema, controller method signature, and audit events.

**Acceptance criteria:** Plan covers all in-scope items from the user's packet, has frozen design decisions for the approve/deny contract, and explicitly defers out-of-scope items.

### 2. Execute T-06 opening slice

**Dependencies:** Plan written and reviewed.

**What:** Implement `codex.delegate.decide` with approve/deny for live `needs_escalation` jobs. Primary files: `mcp_server.py`, `delegation_controller.py`, `models.py`, tests.

## In Progress

**Clean stopping point.** T-05 closed, PR merged, branch deleted. T-06 scoped but plan not yet written.

- **Completed:** PR #108 review fixes (2 commits), merge, branch cleanup, memory update.
- **Not in flight:** No code changes pending.
- **Next action for next-session Claude:** Write the T-06 opening slice plan per the scope in Context → T-06 Opening Slice Scope.

## Open Questions

### 1. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** The handler calls `entry.session.interrupt_turn()` from inside the `_server_request_handler` callback. This sends a `turn/interrupt` JSON-RPC request via the same transport that's reading notifications.

**Impact:** Medium. If the transport doesn't handle re-entrant reads, the handler will deadlock.

**Decision pending until:** Live testing against the real App Server.

### 2. `on-request` operational semantics (inherited from T-05)

**Context:** The vendored schema proves `on-request` is a valid `approvalPolicy` value, but operational semantics are not documented. Controller defaults to `untrusted` per D1.

**Decision pending until:** Live probe against the real App Server.

### 3. Approve turn semantics for T-06

**Context:** When `codex.delegate.decide` approves an escalation, it needs to dispatch a follow-up execution turn in the retained runtime. The prompt for this turn needs to convey Claude's resolution of the escalated request. The exact prompt shape (how to encode "approved: command_approval for `rm -rf /`") is not yet designed.

**Decision pending until:** T-06 plan writing.

## Risks

### 1. Same-session-only decide constraint

The T-06 opening slice explicitly limits `decide` to live same-session escalations. If the process crashes between `codex.delegate.start` returning an escalation and `codex.delegate.decide` being called, the job is stuck in `needs_escalation` with no live runtime. `recover_startup()` currently only handles `running` jobs, not `needs_escalation`. This gap is intentional (out-of-scope for the opening slice) but should be documented in the T-06 plan.

### 2. `_FakeSession` complexity drift (inherited from T-05)

The fake session now has `run_execution_turn()`, `interrupt_turn()`, `close()`, `_raise_on_turn`, `_interrupted` state, and configurable server requests + turn result. Adding `decide` will extend this further. If the fake drifts from the real `AppServerRuntimeSession` interface, tests pass but production fails.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | Closed — AC 6 complete |
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Next ticket |
| T-05 pending-request plan | `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` | Implementation plan (untracked) |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Schema authority |
| Recovery spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Recovery semantics |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-19_15-13_t05-pending-request-capture-implemented-and-reviewed.md`
- T-05 arc: execution-start COMPLETE → pending-request capture PLANNED → scrutiny + amendments → execute + review + PR → **review fixes + merge + T-06 scoping (this handoff)**

### Pull Request

jpsweeney97/claude-code-tool-dev#108 — "feat(t20260330-05): pending-request capture slice (AC 6)" — MERGED at `271f23aa`

## Gotchas

### 1. Ticket boundaries are not implementation-arc boundaries

**Symptom:** Describing "decide-surface + lifecycle → T-05 COMPLETE" when T-05 explicitly scopes out decide.

**Prevention:** When describing next steps, check the ticket's explicit scope at the referenced line. The deferred items in a plan are deferred to the *next* ticket, not within the current one.

### 2. Review agent severity ≠ project severity

**Symptom:** 5-agent review labeled 6 findings as "critical" when only 1 was a real code defect (D6 correlation). The rest were stale docs, type hygiene, and observability.

**Prevention:** Present agent findings as a triage packet for human review. Do not treat agent severity labels as absolute — the human's context about what constitutes "critical" for the project is essential.

### 3. `_CANCEL_CAPABLE_KINDS` is defined in two places

**Symptom:** `frozenset({"command_approval", "file_change"})` appears at both `delegation_controller.py:556` (handler) and `delegation_controller.py:737` (`_finalize_turn`). If they drift, the handler might cancel a kind that finalization doesn't consider cancel-capable.

**Prevention:** Tracked in review findings (test gap I5). No `file_change` end-to-end test exists to catch drift. Deferred to a future test hardening pass.

## Conversation Highlights

### User's review triage style

User reviews agent output against project-specific severity, not generic labels. "The packet's 'critical issues' label is inflated. C1-C3 are stale docs, C4 is type hygiene, C5 is observability... None of those are critical in the same sense as the two real execution bugs you already fixed."

### User's scope discipline for review fixes

User: "I would not use this comment as license to redesign later-message interruption semantics unless you have explicit plan/contract authority for that." — Review comments address the identified defect, not adjacent design territory.

### User's C6 pushback

User: "The recommendation to narrow `except Exception` to `RuntimeError` is not obviously correct. That branch is implementing a fail-soft contract: if request projection fails, preserve a minimal causal record and interrupt the turn. A broad catch supports that contract even if the parser later regresses with `TypeError` or `ValueError`."

### User's ticket boundary correction

User: "If we use the repo's formal ticket boundaries, your earlier sequence is not the current contract. `T-20260330-05` explicitly scopes `codex.delegate.poll`, `codex.delegate.decide`, and `codex.delegate.promote` out of T-05... So from the ticket/contract point of view, AC 6 landing on `main` means T-05 is functionally complete and T-06 is the next ticket."

## User Preferences

### Evidence-first review

User reviews against the diff and reproduction, not commit messages or PR descriptions. Findings include reproduction evidence and specific file:line references.

### Bounded fix commits

User expects review fix patches to stay on the agreed surfaces with no scope creep. "No findings. The patch stayed bounded to the agreed surfaces in delegation_controller.py and models.py."

### Severity calibration

User distinguishes between real execution-semantic bugs (P2), real code defects in non-fatal paths (P2), stale docs in authority surfaces (P3), and type/observability hygiene (P3). Agent labels are input, not output.

### Design-lock respect

User: "I would not use this comment as license to redesign later-message interruption semantics unless you have explicit plan/contract authority for that." — Fixes address the identified defect within its existing design contract.
