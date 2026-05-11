---
date: 2026-04-23
time: "21:14"
created_at: "2026-04-23T21:14:48Z"
session_id: 11a401f1-80dd-4ade-a9c0-bc33f56e004c
resumed_from: "docs/handoffs/archive/2026-04-23_18-24_exec-policy-rejection-packet-1-carve-off.md"
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: 41b4c1aa
title: "Packet 1 deferred-approval design spec drafted, awaiting user review"
type: handoff
files:
  - docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md
  - docs/tickets/2026-04-23-deferred-same-turn-approval-response.md
  - .gitignore
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/pending_request_store.py
  - packages/plugins/codex-collaboration/server/jsonrpc_client.py
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/journal.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
---

# Handoff: Packet 1 deferred-approval design spec drafted, awaiting user review

## Goal

Produce an approved design spec for Packet 1 (deferred same-turn approval response) — the control-plane mechanism that lets a Codex App Server turn stay live across operator delay and receive an approval response in the same turn. This unblocks T-20260423-01 (parent acceptance-gap ticket, AC1 = end-to-end delegation with platform-tool verification).

**Trigger:** User invoked `/load` at session start, which resumed from the predecessor scope-reconciliation handoff. Predecessor had created T-20260423-02 seed ticket with 7 brainstorm questions and carved Packet 1 off from a rejected 805-line unified spec. User then said "start the Packet 1 brainstorm via /brainstorming" — direct invocation of the design work.

**Stakes:** High. The rejected spec (`edff9c07` on `feature/delegate-exec-policy-amendment`) was the second attempt to design this closure path. Third rejection would indicate a structural problem with how this team/me approaches the packet. Getting scope + design right THIS time prevents a third attempt from repeating either the "transport prerequisite as afterthought" failure or a new class of honesty failure.

**Success criteria:**
- All 7 brainstorm questions from T-20260423-02 resolved with user's explicit approval per question
- Named invariants (IO-1 through IO-4, OB-1) extracted and made load-bearing for the spec
- Single-file design spec produced, matching user's predecessor-session preference (<1000 lines)
- All 8 ticket acceptance criteria addressed
- No contradictions between spec and the codebase's actual shape (previous spec's failure mode)

**Connection to project arc:** This handoff closes the design phase of T-20260423-02 (spec drafted, awaiting user review → commit). Task 9 (invoke writing-plans skill) follows after user approval. Implementation is a separate phase. T-20260423-01 AC1 closes when Packet 1's implementation lands AND Packet 2 (amendment admission, not yet ticketed) lands on top.

## Session Narrative

Session began with `/load` — predecessor handoff archived, state file written. Predecessor's immediate-next-action was "invoke superpowers:brainstorming targeting the 7 questions in T-20260423-02, after spot-checking 2-3 cited line numbers for drift."

**Phase 1 — Brainstorming setup (Tasks 1-2).** Invoked the brainstorming skill via Skill tool. Created 9-item TaskList matching the skill's checklist. Task 1: read T-20260423-02 ticket, spot-checked three cited references (controller:618-624 for sync return, controller:639/685-687/702-704/714-716 for capture, pending_request_store.py:29-69 for store API). All matched current HEAD — no drift since predecessor's verification pass.

Task 2: offered Visual Companion because Q1 (start lifecycle) had strong visual candidates (sequence diagrams). User accepted. Started browser server at http://localhost:55560, added `.superpowers/` to .gitignore (wasn't previously listed).

**Phase 2 — Q1-Q7 brainstorm (Task 3).** Drove all seven questions sequentially. Pattern at each question: I proposed, user accepted the framing but added 2-4 substantive sharpenings cited by file:line, I revised, user confirmed closure. Every round produced one or more named invariants or design rules.

Q1 (start lifecycle): presented in browser with two options (threading vs asyncio). User chose A (threading) with a sharpened argument — the transport is already multi-threaded at `jsonrpc_client.py:8,35-59` (background reader threads + queue.Queue). This reframed the decision from "introduce concurrency" to "extend existing concurrency pattern." User added three load-bearing ownership rules that I codified as IO-1 (session ownership), IO-2 (cross-thread API = registry only), IO-3 (store locking is design question, not checkbox).

Q2 (capture cardinality): presented in terminal after pushing a waiting screen to the browser. Proposed singleton-at-a-time with reset-after-respond. User accepted the reframing but pushed back on three specifics: (1) "store behavior unchanged" was false — current projection at `controller:860-868` uses `requests[-1]` which breaks under multi-capture; (2) name `captured_request` → `parked_request`; (3) reset boundary "after respond succeeds" is transport-honest only, not semantic. Added `parked_request_id` durable selector on `DelegationJob` with tombstone-guarded projection.

Q3 (persisted state): proposed 6-part solution. User's major correction: the `consuming` window between `decide()` CAS success and worker's respond+cleanup was not reflected in persisted state. An immediate poll would still return the same escalation. Fix: worker transitions `job.status: needs_escalation → running` BEFORE respond. Also corrected three framings: (a) `abandoned_by_crash` too narrow — use `completion_origin` with `completed_normally/recovered_unresolved`; (b) don't build durability on free-form audit events — use operation journal's existing `approval_resolution` pattern at `controller:1666`; (c) rename `resolution_payload` → `response_payload`, reserve `resolved_at` for success-only. Locked me to dispatch-shaped mutator `record_response_dispatch` + separate `mark_resolved`.

Q4 (synchronization): proposed worker-death cleanup via Option A (exception handler discards registry). User accepted and simplified further (registry states drop to `awaiting/consuming` only, no `resolved`). Two new corrections: (1) `action_applied: true` in decide() response overclaims when decide returns before respond — lock constraint to `decision_accepted` for Q5; (2) "only lock is registry CAS" is literally false because main + worker both write `approval_resolution` journal phases now — need explicit stance. Added IO-4 as a named invariant for the journal's shared append pattern.

Q5 (contract): proposed `closure_reason="abandoned_by_crash"` on OperationJournalEntry. User corrected three ways: (1) rename to `completion_origin` with values `completed_normally/recovered_unresolved` (narrower than crash-specific); (2) no `decision_recorded_at` on decide() — `job_id/request_id` are sufficient correlation + journal has `created_at`; (3) **important framing correction** — output contract is the DelegationDecisionResult dataclass + serializer + docs + tests, NOT MCP tool-schema (which only declares inputSchema). Restructured migration scope accordingly.

Q6 (observability): proposed four-tier taxonomy (transport/continuation/turn-terminal/subsequent-capture). User corrected the tiers — current code at `controller:2079-2108` (`_verify_post_turn_signals`) already matches `serverRequest/resolved` by `requestId` and `item/completed` by `item_id`. This is the **protocol echo** tier, stronger than my generic "continuation" and specifically request-scoped. Replaced continuation with protocol echo. Promoted that existing warning-only code to persistent observation on the request record. Also: keep `PendingEscalationView` minimal (no diagnostic fields); don't add turn-scoped audit event (duplicates existing `DelegationOutcomeRecord`).

Q7 (timeouts): proposed 900s operator window + synthetic timeout → cancel. User corrected four ways: (1) 900s is product policy, NOT transport-derived — App Server's server-request timeout is external and unknown; (2) `resolution_action="deny"` for synthetic timeouts conflates operator-fact with circumstance — keep `resolution_action` strict (operator-decided only); timeout is `timed_out: bool`; (3) don't overload `completion_origin` — it's recovery provenance, not timeout origin; (4) kind-sensitive timeout handling — current code at `controller:640-720` already distinguishes cancel-capable kinds; defer `request_user_input` timeout automation until its response contract is pinned. Added one more field `timed_out: bool = False` on PendingServerRequest.

**Phase 3 — Synthesis + outline approval (Tasks 4-5).** Summarized converged approach with named invariants, rejected alternatives, and sections the Q&A hadn't covered (testing, migration). Asked user to choose structural-preview vs. full-walkthrough vs. write-directly. User picked Option A (structural preview) with an explicit 10-section outline. Outline approved verbatim.

**Phase 4 — Write + self-review (Tasks 6-7).** Wrote 713-line spec at `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`. PostToolUse hook suggested modularization (>500 lines trigger); held single-file per user preference (<1000 line threshold). Self-review found one gap: the new `AppServerRuntimeSession.respond()` wrapper method was implied by lifecycle diagrams but not stated in Data Model. Added inline as §§Session API addition. Cross-checked 8 ticket ACs against spec sections — all addressed.

**Phase 5 — Awaiting user review (Task 8, current state).** Spec written and self-reviewed. NOT committed (per global "only commit when explicitly asked" instruction). Presented user with three next-step options (review-then-commit, commit-then-iterate, no-commit-until-plan-time). Waiting for user response before proceeding to Task 9 (writing-plans skill).

## Decisions

### D1: Worker-thread execution model (Option A over asyncio)

**Choice:** Spawn a worker thread from `start()` to run `_execute_live_turn`. Worker blocks on a resolution registry while waiting for `decide()`. Main thread returns escalation to MCP caller immediately after worker registers.

**Driver:** User quote (verbatim): "A is the right answer for Q1. The decisive evidence is that `jsonrpc_client.py` already uses background reader threads plus `queue.Queue`, while `runtime.py:233` has one synchronous consumer pulling notifications. So A extends the existing transport shape; B smuggles in an async transport rewrite."

**Rejected alternatives:**
- **asyncio task + awaitable future.** Rejected because `JsonRpcClient` uses `subprocess.Popen` + thread-backed blocking queue reads — none awaitable. Converting would cascade async through every sync caller (`_run_turn`, `run_execution_turn`, MCP dispatch). Scope explosion unrelated to Packet 1.

**Implication:** The codebase gets one more threading pattern (worker per turn), coordinated through one new mechanism (resolution registry with `threading.Lock` CAS). Existing sync call paths above/below remain sync.

**Trade-offs accepted:** Concurrency test coverage grows. Stores that were single-writer by architecture (pending_request, delegation_job, journal) still need single-writer discipline — enforced by thread-ownership rules IO-1/2/3, not locks.

**Confidence:** High (E2) — verified against transport code at `jsonrpc_client.py:8,35-59` (reader threads), `runtime.py:232-248` (serial consumer), `mcp_server.py:460-463` (dispatch).

**Reversibility:** Medium — the worker thread is encapsulated in `_execute_live_turn`, so the DECISION could be reversed by reverting to inline execution. But the design implications (registry, new fields, contract shape) would need to be backed out separately.

**Change trigger:** If transport itself gets rewritten to async (separate ticket not in sight), reconsider worker-thread vs. async task.

### D2: Singleton-at-a-time capture with `parked_request_id` durable selector

**Choice:** In-memory `parked_request: PendingServerRequest | None` reset per handler invocation. Durable selector `parked_request_id: str | None` on `DelegationJob`. Projection helper rewritten from `requests[-1]` (at `controller:860-868`) to job-anchored `job.parked_request_id` with tombstone + terminal-status guards.

**Driver:** User quote: "Your tombstone guard is correct. It fixes the exact bug in the current projection path, which still does 'last-ever request wins' via `requests[-1]`." Also: "`parked_request_id` belongs on `DelegationJob`; that is the right durable anchor." Instantaneous-vs-cumulative cardinality split is proof-by-construction from serial handler loop at `runtime.py:245-248`.

**Rejected alternatives:**
- **Multi-capture collection** (list or dict keyed by request_id). Rejected because serial handler loop prevents concurrent captures by construction — collection would be dead state.
- **Extend `PendingRequestStatus` enum with `parked` literal.** Rejected — status enum tracks wire lifecycle (`pending/resolved/canceled`); adding a plugin-runtime concept mixes axes.
- **Separate `parked_requests` store.** Rejected — the invariant ("one parked request per job") is job-scoped; putting it on the job matches ownership.
- **"Prove single-capture-per-turn"** (the ticket's AC3 alternative). Rejected — amendment-triggered continuation legitimately issues further approvals. Can't prove away the path.

**Implication:** `_project_pending_escalation` signature changes from `(collaboration_id)` to `(job: DelegationJob)` — matches poll's `job_id` authority chain at `controller:901-902`. Projection reads: terminal-status guard first, then `job.parked_request_id`, then store lookup with `status != "pending"` tombstone guard.

**Trade-offs accepted:** One new field on `DelegationJob`. One new store mutator (`update_parked_request`). Projection helper complexity grows from 9 lines to ~15 lines but with much stronger invariants.

**Confidence:** High (E2) — verified `_project_pending_escalation` uses `requests[-1]` at `controller:868`; verified projection is gated by `status == "needs_escalation"` at `controller:924`; verified `DelegationJobStore` has no `find_by_collaboration_id` method.

**Reversibility:** Medium — the durable selector is additive. Removing would require going back to `requests[-1]` with whatever its bugs entail.

**Change trigger:** If multi-capture cardinality invariant breaks (e.g., handler loop becomes non-serial), revisit.

### D3: Consuming-window closure via `job.status → running` before respond

**Choice:** Worker's first durable action on wake from registry is `delegation_job_store._persist_job_transition(job_id, "running")`. Happens BEFORE respond() call. poll()'s existing guard at `controller:924` (`if refreshed.status == "needs_escalation":`) then stops surfacing `pending_escalation` automatically.

**Driver:** User quote: "When the worker consumes the registry result, persist `job.status = 'running'` before returning the payload back to the runtime loop. `running` already exists in `models.py:21`, and this is honest: the job is no longer awaiting user input, even though `respond()` has not yet proven semantic acceptance."

**Rejected alternatives:**
- **New persisted `parked_request_state` or `resolution_state` on job** with `parked/consuming` values. Rejected — adds new state enum for information already carried by `job.status`.
- **Let poll() read the registry directly.** Rejected — breaks "projection is store-based" boundary; gives up persistence.
- **Keep status at `needs_escalation` throughout respond.** Rejected — poll during consuming window returns stale escalation; violates Q2's "poll is sole observation surface."

**Implication:** Reuses existing `_persist_job_transition` helper at `controller:833-844` (generic transition API, not terminal-only). `parked_request_id` stays set through the respond cycle for audit/tombstone purposes.

**Trade-offs accepted:** One additional store write in the critical path (job_store update before respond). Minimal overhead.

**Confidence:** High (E2) — verified `_persist_job_transition` is generic (used for "running" at `controller:635`, "unknown" at `2038`, "failed" at `1712`); verified poll gating at `controller:924`.

**Reversibility:** High — if problematic, could add explicit status enum value later.

**Change trigger:** If poll behavior semantics change (e.g., must show pending_escalation even during consuming), reconsider.

### D4: Journal phase split across threads — intent on main, dispatched/completed on worker

**Choice:** `decide()` (main thread) writes `approval_resolution.intent` — same as existing code at `controller:1666-1679`. The existing inline `approval_resolution.dispatched` write at `:1693-1708` MOVES to the worker thread. Worker writes `dispatched` before respond(), `completed` after respond() succeeds.

**Driver:** User quote: "Do not make your new critical-path durability depend on free-form audit events. The existing durable pattern is already `approval_resolution` with `intent/dispatched/completed`." Phases already exist in `_VALID_PHASES` at `journal.py:45`; operation already exists in `_VALID_OPERATIONS` at `journal.py:36`.

**Rejected alternatives:**
- **Store all durable intent in free-form audit events via `append_audit_event`.** Rejected — audit events are narrative; operation journal is recovery-critical. Mixing them forces replay/ordering complexity onto audit consumers.
- **Introduce new phase (e.g., `abandoned`).** Rejected — requires extending `_VALID_PHASES` and updating `_phase_rank`. More invasive than one optional field (`completion_origin`).
- **Keep decide()'s phase=dispatched write; duplicate on worker.** Rejected — creates idempotency ambiguity.

**Implication:** Journal `approval_resolution` operation now has cross-thread phase ownership. Main writes `intent`; worker writes `dispatched` and `completed`. Both threads append to the same JSONL file — relies on IO-4 (inherited JSONL append pattern) for atomicity.

**Trade-offs accepted:** Multi-writer journal acknowledged explicitly as a design commitment (previously single-writer). Named as IO-4.

**Confidence:** High (E2) — verified operation + phases already present; verified `journal.write_phase` at `journal.py:300-307` uses same `open("a")` + fsync pattern as store appenders.

**Reversibility:** Medium — phase-split is structural. Reverting would require synchronizing dispatched write back to main thread (losing the async property).

**Change trigger:** If future operation patterns need phase-splitting across more threads, consolidate the pattern explicitly.

### D5: IO-4 as inherited JSONL append assumption (not proof-grade)

**Choice:** Name IO-4 as a design invariant: "All JSONL writers inherit the repo's existing assumption that `open('a')` + single-line write + fsync is safe under concurrent callers on supported platforms. Not a proof-grade claim; the repo's platform assumption."

**Driver:** User quote: "I would not freeze `IO-4` as a POSIX/`PIPE_BUF` proof. `PIPE_BUF` is the pipe/FIFO guarantee, not the regular-file guarantee. So the rigorous version is narrower: this repo already relies on append-only JSONL behavior on its supported platforms, and the journal now shares that implementation assumption. If you want a proof-grade claim, you need a hardened append primitive or a lock. If you are comfortable inheriting the repo's existing assumption, say exactly that and stop short of citing `PIPE_BUF` as if it settled regular files."

**Rejected alternatives:**
- **Journal-local `threading.Lock` mutex.** Rejected — inconsistent with stores' pattern; adds complexity without matching semantics.
- **Centralize phase writes onto one thread.** Rejected — sacrifices main-thread durable intent (worker slow to wake → crash loses operator intent).
- **Cite PIPE_BUF as proof.** Rejected per user — PIPE_BUF applies to pipes/FIFOs, not regular files. Overclaims correctness.

**Implication:** IO-4 is an honest design invariant with a named dependency (platform assumption). Future multi-process writers or Windows support require upgrading to explicit lock or hardened append primitive.

**Trade-offs accepted:** Design correctness depends on OS-level behavior (Linux/macOS). Platform assumption is explicit, not hidden.

**Confidence:** Medium (E1) — repo's existing pattern relies on this; no explicit test of multi-writer behavior under concurrent load.

**Reversibility:** High — upgrading to a lock is additive.

**Change trigger:** Any future platform expansion (Windows), multi-process plugin architecture, or integration testing that stresses concurrent journal writes.

### D6: Minimal `DelegationDecisionResult` shape — no live status

**Choice:** `DelegationDecisionResult` becomes `{decision_accepted: bool, job_id: str, request_id: str}`. All five previous fields (`job`, `decision`, `resumed`, `pending_escalation`, `agent_context`) are removed. Breaking change for external callers.

**Driver:** User quote: "`decide()` should not return raw job `status` if it returns before the worker persists `running`. Under your own design, the main thread can accept the decision and return while the durable job status is still `needs_escalation`. That would make a success payload internally contradictory. So for Q5 I would either omit live job status from `decide()` success entirely, or return a decision-local field like `decision_accepted: true` plus maybe `job_id`/`request_id`, and leave all live execution state to `poll()`."

**Rejected alternatives:**
- **Include `status` in success response.** Rejected — can be internally contradictory (durable status still `needs_escalation` while response says `decision_accepted: true`).
- **Include `pending_escalation` in success.** Rejected by Q2 rule (poll is sole observation surface).
- **Include `decision_recorded_at` timestamp.** Rejected — `job_id` + `request_id` sufficient correlation; journal intent record already has `created_at`.
- **Keep `resumed: bool`.** Rejected — no such property under async model; decide returns before worker resumes anything.

**Implication:** Breaking migration. Callers reading `pending_escalation` from decide's success payload must switch to `poll()`. Tests at `test_mcp_server.py:1202` that assert on `decision`/`resumed`/`pending_escalation` need rewriting.

**Trade-offs accepted:** One additional MCP round-trip for callers who previously got state in decide's response. Justified by honesty — decide's response cannot honestly report state that's in flight.

**Confidence:** High (E2) — verified `DelegationDecisionResult` shape at `models.py:418-426`; verified serialization via `asdict(result)` at `mcp_server.py:460-463`.

**Reversibility:** Medium — once external callers migrate, reversing would break them again.

**Change trigger:** None anticipated.

### D7: `completion_origin` provenance field (narrowed scope)

**Choice:** Add optional `completion_origin: Literal["completed_normally", "recovered_unresolved"] | None = None` to `OperationJournalEntry`. Scoped strictly to journal-terminal-marker provenance. Worker-written completions use `"completed_normally"`; recovery-written completions at `controller:1856-1884` use `"recovered_unresolved"`.

**Driver:** User quotes: "Do not overload `completion_origin` with timeout. `completion_origin` is about provenance of the terminal `approval_resolution.completed` marker: normal worker completion versus recovery closure. A worker-driven timeout cancel is still a normal worker completion, not a recovery-origin terminal marker."

**Rejected alternatives:**
- **`closure_reason: Literal["completed_normally", "abandoned_by_crash"]`.** Rejected — "abandoned_by_crash" is too crash-specific; also covers `CommittedDecisionFinalizationError` case which isn't crash-driven.
- **New phase `abandoned` or `aborted`.** Rejected — invasive schema change.
- **Additional value for timeouts (e.g., `origin_timeout_synthetic`).** Rejected — timeouts are worker-normal completions, not recovery. Don't overload.
- **Leave unresolved rows unresolved.** Rejected — `list_unresolved()` at `journal.py:309` grows unbounded without recovery closure.

**Implication:** Journal schema gains one optional string field. Back-compat: old records without the field read as `None`. Recovery code at `controller:1856-1884` sets `"recovered_unresolved"`; worker writes set `"completed_normally"`.

**Trade-offs accepted:** One more optional field on `OperationJournalEntry`. Readers that interpret phase=completed as "success" were already wrong (current recovery blind-closes rows); the new field gives them a correct signal.

**Confidence:** High (E2) — verified `OperationJournalEntry` at `models.py:337-359`; verified recovery pattern at `controller:1856-1884`.

**Reversibility:** High — additive; back-compat read semantics.

**Change trigger:** None.

### D8: Protocol echo tier in observability taxonomy (promoting existing code)

**Choice:** Four-tier observation taxonomy: transport write → **protocol echo** → turn terminal → subsequent capture. Protocol echo tier persists observations from `_verify_post_turn_signals` at `controller:2079-2108` (currently warning-only logging) onto the request record via new fields `protocol_echo_signals: tuple[str, ...]` and `protocol_echo_observed_at: str | None`.

**Driver:** User quote: "The taxonomy is missing the strongest request-scoped signal the repo already knows about. Current code explicitly looks for `serverRequest/resolved` for the matching `requestId` and `item/completed` for the matching `item_id` in `_verify_post_turn_signals()` at `delegation_controller.py:2088`. That is stronger than your generic 'continuation' level and weaker than semantic application."

**Rejected alternatives:**
- **Skip protocol echo, use generic "continuation" tier.** Rejected per user — protocol echo is specifically request-scoped and keyed by `requestId`/`item_id`; continuation is just "next message arrived" which is weaker.
- **Turn-scoped `turn_observed_terminal` audit event.** Rejected — duplicates existing `DelegationOutcomeRecord` emission via `_emit_terminal_outcome_if_needed` at `controller:801`.
- **Include all new fields in `PendingEscalationView`.** Rejected — view is minimal "current action needed"; diagnostic/historical fields blur its role.

**Implication:** Two new fields on `PendingServerRequest`. Refactor `_verify_post_turn_signals` to return observed signals (not just log); worker persists via new `record_protocol_echo` mutator.

**Trade-offs accepted:** Post-turn observation latency: protocol echo fields populated only AFTER turn/completed. Before then, fields are default empty.

**Confidence:** High (E2) — verified `_verify_post_turn_signals` at `controller:2079-2108`; verified it's invoked as D6 diagnostic after turn/completed.

**Reversibility:** High — fields additive.

**Change trigger:** If protocol echo signals become unreliable (e.g., App Server stops emitting them consistently), demote back to warnings.

### D9: Kind-sensitive timeout dispatch (not universal)

**Choice:** Synthetic timeout handling differs by request kind:
- `command_approval` / `file_change` (cancel-capable): dispatch `{"decision": "cancel"}` via respond()
- `request_user_input` (known-denial at `:720`): call `interrupt_turn`, no respond dispatch
- `unknown` (D4 carve-out at `:690-695`): call `interrupt_turn`, no respond dispatch

Mirrors existing capture-time dispatch logic at `controller:640-643, 698-720`.

**Driver:** User quote: "Packet 1 should not specify a universal timeout→cancel rule unless it also narrows the request-kind scope. The clean options are: scope synthetic timeout handling to cancel-capable kinds only; use turn interruption as the fallback for non-cancel-capable kinds; defer timeout automation for `request_user_input` until its response contract is explicitly pinned."

**Rejected alternatives:**
- **Universal timeout → `{"decision": "cancel"}`.** Rejected — `request_user_input` timeout-response contract is not pinned in the docs at `docs/codex-app-server.md`. Unsafe to assume cancel semantics carry over.
- **Skip timeout automation entirely.** Rejected — leaves the system hanging on abandoned operator sessions.

**Implication:** Kind-sensitive dispatch table in spec. For non-cancel-capable kinds: `response_payload=None, response_dispatch_at=None, dispatch_result=None`; worker calls interrupt_turn instead.

**Trade-offs accepted:** `request_user_input` timeout semantics remain TBD. If a future packet expands deferred approval to `request_user_input`, its timeout path needs to be designed then.

**Confidence:** High (E2) — verified existing kind dispatch at `controller:640-720`; verified `_CANCEL_CAPABLE_KINDS = frozenset({"command_approval", "file_change"})` and `_KNOWN_DENIAL_KINDS = frozenset({"request_user_input"})`.

**Reversibility:** High — expanding to more kinds is additive.

**Change trigger:** `request_user_input` timeout-response contract being documented in codex-app-server.md.

### D10: Operator window as local policy (not transport-derived)

**Choice:** `APPROVAL_OPERATOR_WINDOW_SECONDS = 900` (provisional default, configurable). Spec framing: "local abandonment budget, chosen conservatively, not justified as an upstream contract match."

**Driver:** User quote: "The `900s` default is not actually 'matched to real transport limits.' The App Server's own server-request timeout is still unknown in repo authority. So `900s` can be a product-policy default, but not a transport-derived one. I would write it that way explicitly."

**Rejected alternatives:**
- **Match to client-side 1200s `request_timeout`.** Rejected — that's the timeout for OUR outbound requests (`turn/start`, `turn/interrupt`), not the parked handler.
- **Match to notification-loop 1200s.** Rejected — notification loop timeout is not active during parked handler (loop is inside `server_request_handler(notification)` at `runtime.py:246`; timeout resets after handler returns).
- **Lock 900s as empirically justified.** Rejected per user — "default configurable, value TBD by empirical probe" is more honest for a value without upstream authority.

**Implication:** Spec honestly frames the value as product policy. Implementation makes the constant env-var configurable. Integration testing can refine empirically.

**Trade-offs accepted:** No transport-derived justification for the number. Honesty over false precision.

**Confidence:** Medium (E1) — 1200s transport timeouts are verified at `runtime.py:49, 233`; App Server's server-request timeout is external and not repo-verifiable.

**Reversibility:** High — configurable constant.

**Change trigger:** Empirical evidence from integration testing showing operator patterns or App Server timeout boundaries.

## Changes

### `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` — new file, 723 lines

**Purpose:** Deliver the Packet 1 design spec per T-20260423-02 acceptance criteria. Owns the control-plane redesign; defers implementation to a separate phase (Task 9 / writing-plans skill).

**Approach:** Single-file markdown spec (per user's predecessor preference for <1000 lines; 723 lines fits). Twelve sections following user's approved 10-section outline:

1. Overview — ticket + branch + rejected-spec provenance
2. Scope and Non-Goals — 8 in-scope, 3 non-goals
3. Named Invariants — IO-1 through IO-4, OB-1 with one paragraph each
4. Runtime Architecture and Thread Ownership — current vs new arch diagrams, thread role table, Resolution registry sketch
5. Deferred-Resolution Lifecycle — five ASCII flow diagrams (happy, timeout cancel-capable, timeout non-cancel, worker-death, cold-start)
6. Data Model and Store Mutations — parked_request_id, 8 PendingServerRequest fields, completion_origin, 5 new store mutators, session API addition (post-self-review), replay logic
7. `decide()` / `poll()` Contract Changes — breaking DelegationDecisionResult shape, migration scope, no new rejection reasons, `_project_pending_escalation` rewrite
8. Observability and Honesty Rules — four-tier taxonomy table, OB-1 restated, channels, what we don't claim
9. Recovery and Reconciliation — orphan demotion + completion_origin + tombstone guards
10. Timeout Policy — operator window framing, expiry mechanics, kind-sensitive dispatch table
11. Testing and Migration — unit/integration/E2E/concurrency test plan, back-compat notes
12. Rejected Alternatives (Rationale Appendix) — 15 rejected alternatives across Q1-Q7 with reasoning

**Key implementation details:**
- All named invariants (IO-1, IO-2, IO-3, IO-4, OB-1) have explicit definitions and rationale references
- Every factual claim includes file:line citation
- ASCII diagrams for lifecycle flows show thread ownership explicitly
- Breaking change set itemized in §§decide()/poll() Contract Changes as a table
- Field addition tables show: field name, type, default, set-by, set-when
- Rejected alternatives appendix has 15 entries, one per discarded option, each with reasoning

**Future-Claude note:** §§Rejected Alternatives is the honesty trail. Future proposals re-raising asyncio, transport-derived timeouts, "applied vs error" observability, etc., will find them documented with reasoning. Defends against scope-creep patching the spec later.

### `.gitignore` — modified

**Purpose:** Prevent Visual Companion's `.superpowers/brainstorm/` output from being committed.

**Approach:** Added `# Superpowers visual companion (brainstorm mockups, server state)` + `.superpowers/` after the existing "Skill eval artifacts" block.

**Key detail:** Matches existing style (comment-prefixed category block, directory with trailing slash).

### `/Users/jp/Projects/active/claude-code-tool-dev/.superpowers/brainstorm/16228-1776974274/content/q1-start-lifecycle.html` — Visual Companion mockup

**Purpose:** Presented Q1 to user with two sequence diagrams + option cards + pros/cons.

**Approach:** Content fragment (not full HTML) with `<div class="options">` using data-choice attributes + toggleSelect helper. Included a "what's already true" note calling out the transport's existing multi-threading.

**Ephemeral:** Lives in gitignored `.superpowers/` directory; exists only for this session's interactive presentation. Not durable.

### `/Users/jp/Projects/active/claude-code-tool-dev/.superpowers/brainstorm/16228-1776974274/content/waiting-q2.html` — Visual Companion waiting screen

**Purpose:** Cleared the browser after Q1 closed; indicated terminal-mode continuation.

**Ephemeral:** Same as above.

## Codebase Knowledge

### Architecture mapped this session

| Concept | File | Line range | Purpose |
|---|---|---|---|
| Delegation entry | `delegation_controller.py` | 577-624 | `start()` → sync call to `_execute_live_turn` |
| Handler closure | `delegation_controller.py` | 650-720 | `_server_request_handler` captures, interrupts, or returns payload |
| Capture cardinality | `delegation_controller.py` | 639, 685-687, 702-704, 714-716 | `captured_request` singleton, three is-None-guarded sites |
| Post-turn finalization | `delegation_controller.py` | 1440-1515 | `_finalize_turn` — DelegationEscalation construction post-turn |
| Projection helper | `delegation_controller.py` | 860-868 | Currently uses `requests[-1]` — broken for multi-capture |
| Poll helper | `delegation_controller.py` | 901-935 | Starts at `job_store.get(job_id)`; gates pending_escalation on `status=="needs_escalation"` at 924 |
| Decide() — existing inline | `delegation_controller.py` | 1666-1708 | Journal intent + audit event + journal dispatched (inline) |
| Decide deny path | `delegation_controller.py` | 1712 | `_persist_job_transition(job_id, "failed")` |
| Controller `_persist_job_transition` helper | `delegation_controller.py` | 833-844 | Generic transition (not terminal-only); wraps `update_status_and_promotion` |
| Orphan demotion | `delegation_controller.py` | 2036-2038 | Iterates `list_active()`; demotes `running`/`needs_escalation` → `unknown` |
| Recovery reconciliation (approval_resolution) | `delegation_controller.py` | 1856-1884 | Blind-closes unresolved rows to phase=completed — overstates success under new design |
| `_verify_post_turn_signals` | `delegation_controller.py` | 2079-2108 | D6 diagnostic: matches `serverRequest/resolved` by `requestId` + `item/completed` by `item_id`; currently warning-only |
| `_phase_rank` | `delegation_controller.py` | 2121-2123 | `{"intent": 0, "dispatched": 1, "completed": 2}.get(phase, -1)` |
| Transport reader threads | `jsonrpc_client.py` | 8, 35-59 | Background `threading.Thread` for stdout/stderr; `queue.Queue` as message channel |
| Transport respond | `jsonrpc_client.py` | 106-130 | Fire-and-forget stdin write; only error is `BrokenPipeError` |
| Transport notification timeout | `jsonrpc_client.py` | 163-170 | `_get_message(timeout)` via `self._message_queue.get(timeout=...)` |
| Runtime session | `runtime.py` | 41-273 | `AppServerRuntimeSession`; `request_timeout=1200.0` default at 49 |
| Turn loop | `runtime.py` | 232-273 | `while True: next_notification(timeout=1200.0)`; server-request dispatch at 245-248 |
| `pending_request_store` API | `pending_request_store.py` | 29-69 | `create / get / list_pending / list_by_collaboration_id / update_status`; no generic update |
| `_append` pattern | `pending_request_store.py` | 71-75 | `open("a")` + `write(...)` + `flush()` + `os.fsync(fileno())` |
| Operation journal writes | `journal.py` | 300-307 | `write_phase` uses identical append pattern to stores |
| `_VALID_OPERATIONS` | `journal.py` | 36-44 | `thread_creation, turn_dispatch, job_creation, approval_resolution, promotion` |
| `_VALID_PHASES` | `journal.py` | 45 | `intent, dispatched, completed` |
| Journal optional string fields | `journal.py` | 54-60 | `codex_thread_id, runtime_id, job_id, request_id, decision` |
| `DelegationDecisionResult` | `models.py` | 418-426 | `job, decision, resumed, pending_escalation, agent_context` |
| `DecisionRejectedReason` | `models.py` | 37-47 | Existing rejection enum values |
| `OperationJournalEntry` | `models.py` | 337-359 | Dataclass with phase literal + optional correlation fields |
| `PendingRequestStatus` | `models.py` | 20 | `pending, resolved, canceled` |
| `PendingEscalationView` | `models.py` | 441 | Minimal caller-visible subset |
| MCP dispatch — decide | `mcp_server.py` | 460-463 | `asdict(controller.decide(...))` — flow-through for dataclass changes |
| MCP — inputSchema only | `mcp_server.py` | (tool registration) | No outputSchema declared; output contract lives elsewhere |

### Patterns identified

- **Transport is already multi-threaded.** `JsonRpcClient` at `jsonrpc_client.py:8,35-59` uses background reader threads feeding a `queue.Queue`. Introducing worker threads at the controller level extends this pattern; it doesn't invent one. Load-bearing finding from Q1.
- **JSONL append pattern is universal.** Stores (`pending_request_store._append` at `71-75`, `delegation_job_store._append`) and journal (`journal.write_phase` at `300-307`) all use `open("a")` + single-line write + fsync. IO-4 is the name for this shared platform assumption.
- **Operation journal with validated phases.** Existing `approval_resolution/intent/dispatched/completed` pattern is reusable for the thread-split. Discovered at `controller:1666` + `journal.py:45`. Avoids inventing new phases.
- **Serial handler loop.** `runtime.py:245-248` runs `server_request_handler(notification)` inline; loop doesn't iterate until handler returns. This makes "at most one parked capture" provable by construction.
- **`PendingEscalationView` minimal projection.** At `models.py:441`. Has a clear role — "what does the caller need to render an escalation prompt" — that would be blurred by adding diagnostic fields.
- **Kind-sensitive request dispatch.** Existing `_CANCEL_CAPABLE_KINDS` vs `_KNOWN_DENIAL_KINDS` distinction at `controller:640-643`. Timeout handling extends this existing taxonomy rather than inventing a new one.

### Conventions observed

- **Dedicated store mutators over generic update.** Stores expose specific methods (`update_status`, `update_status_and_promotion`, `update_artifacts`, `update_promotion_state`) rather than generic `update(**fields)`. Matches replay's explicit op-dispatch (at `pending_request_store.py:115-136`).
- **File:line citations in prose.** Every factual claim in the codebase gets an inline `file.py:lineno` reference. Habit visible in existing CLAUDE.md rules and the rejected-spec scrutiny.
- **Journal validation.** `_journal_callback` at `journal.py:64-*` validates operation + phase + required/optional field types before accepting a record.
- **Status enums as Literals.** All lifecycle enums at `models.py:13-57` use `Literal[...]` for exhaustiveness, not `Enum` classes.

### Surprising findings

- **`_persist_job_transition` is a generic helper, not terminal-only.** Despite its usage for `failed`/`unknown` transitions, it's a wrapper for all status transitions including `running` (evidenced by its docstring-level comment at `controller:42` and existing use at `controller:635` via lower-level `update_status_and_promotion`).
- **`_verify_post_turn_signals` already matches protocol echo signals.** The strongest observability tier for deferred approval is already half-built — just needs promotion from warning-only to persistence.
- **MCP tool schema is inputSchema-only.** The `codex.delegate.decide` output contract lives in the `DelegationDecisionResult` dataclass + serializer + docs + tests, NOT in a JSON schema. Misunderstanding this led me to mis-scope Q5's migration.
- **Current recovery blindly closes unresolved `approval_resolution` rows.** At `controller:1856-1884`, writes phase=completed for every unresolved idempotency_key. This overstates success under the new model where worker-never-woke is a legitimate crash state.
- **`_project_pending_escalation` uses `requests[-1]`.** At `controller:868`. Fine for single-ever capture model; broken for multi-capture-per-turn.

### Key locations for Task 9 (writing-plans) / implementation

| Concept | Entry point |
|---|---|
| `start()` call path | `delegation_controller.py:577-624` |
| Worker execution | `delegation_controller.py:626-737` (becomes worker thread body) |
| Handler closure | `delegation_controller.py:650-720` (parking logic inserts here) |
| Projection rewrite | `delegation_controller.py:860-868` (replace `requests[-1]`) |
| Poll behavior | `delegation_controller.py:901-935` |
| Decide path | `delegation_controller.py:1640-1720` (move dispatched phase to worker) |
| Store mutators | `pending_request_store.py:29-69` (add 4 new methods) |
| Job store mutators | `delegation_job_store.py` (add `update_parked_request`) |
| Session wrapper | `runtime.py` (add `AppServerRuntimeSession.respond()` method) |
| Journal schema | `journal.py:36-61` (add `completion_origin` optional field) |
| Models | `models.py:20-47, 418-426` (DelegationDecisionResult shape + PendingServerRequest fields + OperationJournalEntry field) |

## Context

### Mental model

**This is a concurrency-and-coordination design, not a feature addition.** The code already has multi-threaded transport, a validated operation journal, a kind-sensitive dispatch taxonomy, a JSONL-append convention, and a `_verify_post_turn_signals` observation helper. Packet 1 assembles these primitives under a new coordination surface (the resolution registry) and adds one more thread (worker-per-turn).

**The design principle that emerged: extend what exists, name what you assume.** Where a pattern is already in the codebase (transport threading, journal phases, JSONL atomicity, kind-sensitive dispatch), the design reuses it and names the inheritance as a design invariant (IO-1, IO-2, IO-3, IO-4). Where a new primitive is needed (resolution registry), it's small, bounded, and has a single responsibility.

**OB-1 (observation honesty) is the design's organizing principle for the data layer.** The rejected spec's fundamental failure was claiming observations ("applied vs error") that the protocol doesn't provide. The new design names four observation tiers, explicitly states what each claims and doesn't claim, and keeps record-level verbs tied to the layer of observation.

### Environment state

- Branch: `feature/delegate-deferred-approval-response` at commit `41b4c1aa`. Not pushed to origin.
- Working tree: dirty with the spec file + `.gitignore` modification + `.superpowers/` directory (gitignored).
- Visual Companion server: running at `http://localhost:55560` (pid 16228). Session auto-expires after 30 min of inactivity.
- `main` branch: `005d4b44` (per predecessor handoff).
- Rejected spec: preserved dormant on `feature/delegate-exec-policy-amendment` at `edff9c07`.

### Project arc

| Milestone | Status |
|---|---|
| T-20260423-01 parent ticket | Open — AC1 still blocked |
| T-20260423-02 Packet 1 ticket | Open — spec drafted (this session) |
| First amendment spec attempt (`edff9c07`) | Rejected (predecessor session) |
| Packet 1 spec write | **Done (this session, 713→723 lines, uncommitted)** |
| Packet 1 spec approval | Awaiting user review |
| Packet 1 plan (writing-plans skill) | Not started — Task 9 pending |
| Packet 1 implementation | Not started |
| Packet 2 (amendment admission) ticket | Not yet ticketed; stacks on Packet 1 |
| T-20260423-01 AC1 closure | Blocked on Packet 1 + Packet 2 |

## Learnings

### Named invariants extracted from implementation work are load-bearing

**Mechanism:** Each Q1–Q7 user correction surfaced a design rule that traveled to subsequent questions. Q1 produced IO-1/2/3; Q4 added IO-4; Q6 crystallized OB-1. By Q7, these five invariants formed a coherent design language that the spec uses as its spine.

**Evidence:** The spec's §§Named Invariants section is explicitly the "spine" per §Rejected Alternatives conclusion; every decision in §Architecture/Data Model/Contracts/Observability traces to verification against one or more named invariants.

**Implication:** For complex design work, naming invariants as they emerge — and explicitly checking every subsequent decision against them — makes the design reviewable and survivable. Future changes are forced to verify-against or explicitly-revise the invariants, not silently drift.

**Watch for:** Invariant inflation. Five is manageable; ten would be cognitive overload. Only promote something to an invariant if it's violated by at least two candidate alternatives.

### Honest framing protects future maintenance

**Mechanism:** Several Q&A rounds collapsed proposals that were technically true but overstated. Q5's `decision_accepted` (not "applied") preserves honesty about what decide() can know. Q6's four-tier taxonomy separates what's observable at each layer. Q7's `timed_out: bool` (not `resolution_action="deny"`) keeps operator-fact and circumstance-fact on separate axes.

**Evidence:** User corrected me at Q5 ("`action_applied: true` now overclaims"); at Q6 ("taxonomy is missing the strongest request-scoped signal"); at Q7 ("`resolution_action=\"deny\"` for synthetic timeout is the wrong field semantics"). Each correction tightened honesty without weakening the design.

**Implication:** Field names and API verbs encode epistemic claims. Conflating dispatch-fact with semantic-fact (applied vs respond-succeeded) creates bugs at the data layer. Separating them into orthogonal axes (operator-action, circumstance, dispatch-result, resolution-status) makes audit and analytics queries precise.

**Watch for:** Synthesized fields ("effective_status" computed from two sources). These re-introduce the conflation the axes separate. Keep axes independent.

### Scope-discipline via existing-taxonomy reuse

**Mechanism:** Q7's kind-sensitive timeout dispatch reuses the existing capture-time kind distinctions at `controller:640-720` (`_CANCEL_CAPABLE_KINDS` vs `_KNOWN_DENIAL_KINDS`). Rather than inventing a new taxonomy for timeout handling, the spec extends the existing one — narrowing Packet 1's scope to only what the existing kinds already support.

**Evidence:** User explicitly raised the `request_user_input` contract gap. The existing distinction at `controller:640-643` provided the natural narrowing: kinds the codebase already handles get timeout automation; others get interrupt_turn.

**Implication:** When a new feature must be narrowed, prefer narrowing that reuses existing taxonomy boundaries over introducing new boundaries. The existing ones already have tests, callers, and documentation.

**Watch for:** Taxonomy that EXISTS but is incomplete for the current need. Don't extend it invisibly — extend it explicitly or narrow around it.

### Spec-as-rejected-input creates a citable artifact

**Mechanism:** The rejected spec at `edff9c07` on its dormant branch remained a citable reference throughout this session. Every time the user pushed back or I reconsidered an approach, we could compare to the rejected spec's text at specific line numbers without needing to re-derive its failures.

**Evidence:** Multiple references in the current spec's §Rejected Alternatives point to specific rejected-spec decisions. The `edff9c07` commit hash lets anyone load that exact state if needed.

**Implication:** Rejected design work is high-value historical artifact. Never patch-forward over a rejection; always preserve the rejected input as dormant branch + spec file. Cost of one extra ticket is lower than cost of archaeology to recover "what was rejected and why."

**Watch for:** "Just update the rejected spec with the new decisions" temptation. Blends validated and rejected content; future readers can't tell which parts were approved vs. corrected.

## Next Steps

### 1. User reviews committed spec

**Dependencies:** None — spec is on working tree at `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`.

**What to read first:** Full spec (723 lines, 12 sections including rationale appendix).

**Approach suggestion:** Section-by-section review, focusing on §§Named Invariants and §§Runtime Architecture (the load-bearing design commitments). §§Rejected Alternatives is the rationale trail and may be cross-referenced against the Q1-Q7 conversation if anything seems wrong.

**Acceptance criteria:** User explicit approval OR itemized change list.

**Potential obstacles:**
- User may find a contradiction between sections that self-review missed
- Field naming may need tightening (especially the 8 new `PendingServerRequest` fields)
- Schema additions may need re-framing if user sees better abstractions

### 2. Commit the spec

**Dependencies:** User approval (#1).

**Approach:** `git add docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md .gitignore` + commit. Message: "feat(7a): draft Packet 1 deferred-approval design spec (T-20260423-02)" or similar. The `.gitignore` change for `.superpowers/` rides along (one commit).

**Note:** NOT committed this session per user's "only commit when explicitly asked" global instruction.

### 3. Invoke superpowers:writing-plans (Task 9)

**Dependencies:** Spec committed (#2).

**Approach:** Per brainstorming skill's terminal state — invoke `superpowers:writing-plans` with the committed spec as input. Plan decomposes implementation into phases.

**Acceptance criteria:** Phase-by-phase implementation plan committed.

**Potential obstacles:** Plan may reveal ambiguity in the spec that requires spec revision before implementation begins.

### 4. Implement Packet 1 per plan

**Dependencies:** Plan approved.

**Scope:** Execute plan phase-by-phase. Candidate phase-breakdown from the spec:
- Phase 1: Foundational data model additions (field additions, store mutator skeletons). Non-functional but wire-safe.
- Phase 2: Resolution registry + worker-thread spawn (mechanism core).
- Phase 3: Handler parking + CAS + worker wake (cross-thread coordination).
- Phase 4: Protocol-echo promotion + completion_origin annotation (observability + recovery).
- Phase 5: Timeout handling (operator window + kind-sensitive dispatch).
- Phase 6: Contract migration (decide shape break + tests rewrite).

**Each phase:** Commit group with passing tests before advancing.

### 5. Packet 2 (amendment admission) ticket + design

**Dependencies:** Packet 1 merged to main.

**Scope:** Revise the rejected spec into admission-only. Reuse D1, D2, D3, D4, D5, D6, D9, D11, D12 (per predecessor handoff's tally of surviving decisions). Build on Packet 1's primitives.

## In Progress

**State:** Task 8 of brainstorming checklist in progress — spec written and self-reviewed; awaiting user review before commit.

- Tasks 1-7 complete (explore, offer companion, Q1-Q7 brainstorm, propose approaches, present outline, write doc, self-review)
- Task 8 in progress (user review)
- Task 9 (invoke writing-plans) pending user approval + commit

**What's working:**
- Spec file exists and is internally consistent
- All 8 ticket ACs addressed (cross-checked in Task 7)
- Named invariants extracted and woven through design sections
- §§Rejected Alternatives captures 15 rejected options with reasoning

**What's not working / what's incomplete:**
- Not yet committed (working tree has uncommitted changes: `.gitignore`, the spec file, `.superpowers/` contents which are gitignored)
- Plan (Task 9) not started — depends on spec commit

**Open question:**
- Will user approve as-is, or request changes? If changes, whether changes are small (inline edit) or structural (re-draft section)?

**Immediate next action on resume:** Wait for user review response. When user says "looks good" or equivalent: commit per guidance in §Next Steps step 2, then invoke `superpowers:writing-plans` with the spec.

## Open Questions

1. **Will user accept the 8 new `PendingServerRequest` fields?** This is the design's biggest schema surface. Justified as cohesive (all describe one request's dispatch lifecycle). If user wants a sub-record abstraction, that's a spec revision.
2. **Is the `APPROVAL_OPERATOR_WINDOW_SECONDS=900` provisional default acceptable?** Could user prefer a different value or prefer the spec NOT to lock any default?
3. **Does the Resolution registry sketch (class signature) need tightening?** Spec currently uses `Future` return type for `register()`; actual implementation might use `concurrent.futures.Future` or a custom `RegistryEntry`. User may want more precision before implementation planning.
4. **`completion_origin` field on `OperationJournalEntry` vs. a separate entry type?** Current choice is one optional field on existing dataclass. Alternative: dedicated `CompletionMarker` record. Spec picked the lighter option; worth confirming.

## Risks

1. **Eight new fields on `PendingServerRequest` is borderline.** If Packet 2 adds more, a sub-record becomes warranted. Packet 1 is justifiable (all on one axis: dispatch lifecycle of one request) but the trend matters.
2. **IO-4 relies on OS platform assumption.** Honest framing but still a latent risk if the plugin ever moves to Windows or multi-process architecture. Upgrade path to explicit locks exists.
3. **Operator window is provisional.** 900s default without empirical grounding may prove wrong in production. Configurable so can be tuned; but initial deployment uses a number that's not evidence-based.
4. **`request_user_input` timeout path uses `interrupt_turn`.** Safer than timeout→cancel but may need expansion later. If deferred-approval flows ever expand to `request_user_input`, timeout contract needs designing.
5. **Breaking `DelegationDecisionResult` shape.** External callers reading `pending_escalation` from decide's response will break. Intentional migration-forcing, but coordination with callers required if any exist downstream.
6. **Self-review is an imperfect substitute for user review.** Task 7 caught the Session API addition gap but may have missed others. User review is still necessary.

## References

| What | Where |
|---|---|
| Design spec (this session's artifact) | `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` |
| Seed ticket | `docs/tickets/2026-04-23-deferred-same-turn-approval-response.md` |
| Rejected spec (historical) | `edff9c07` on `feature/delegate-exec-policy-amendment` |
| Parent ticket | `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` |
| Predecessor handoff (archived) | `docs/handoffs/archive/2026-04-23_18-24_exec-policy-rejection-packet-1-carve-off.md` |
| Delegation controller | `packages/plugins/codex-collaboration/server/delegation_controller.py` |
| Runtime session + JSON-RPC transport | `packages/plugins/codex-collaboration/server/runtime.py`, `jsonrpc_client.py` |
| Stores | `packages/plugins/codex-collaboration/server/pending_request_store.py`, `delegation_job_store.py` |
| Journal | `packages/plugins/codex-collaboration/server/journal.py` |
| Models | `packages/plugins/codex-collaboration/server/models.py` |
| MCP server | `packages/plugins/codex-collaboration/server/mcp_server.py` |
| contracts.md (update target) | `docs/superpowers/specs/codex-collaboration/contracts.md:297-310` |

## Gotchas

- **Spec NOT committed.** Working tree is dirty. Resuming-Claude should check `git status` before proceeding.
- **`.superpowers/` directory lives in gitignore now**, so brainstorm mockups won't accidentally commit if server is still running when someone stages changes.
- **Visual Companion server still running** at `http://localhost:55560` (pid 16228) unless timed out. 30-min inactivity auto-close. Future session can restart if needed, or ignore if text-only.
- **`_persist_job_transition` is a generic helper, not terminal-only** — used throughout spec for the running transition. Reuses existing code at `controller:833-844`.
- **Output contract is dataclass + serializer, not MCP schema.** Don't reach for JSON-schema files for the decide() contract change; it's in `models.py` + docs + tests.
- **`completion_origin` is strictly recovery provenance.** Do NOT overload with timeout, failure, or other outcomes — timeouts are `timed_out: bool` on request record; failures are via existing `_mark_execution_unknown_and_cleanup`.
- **PendingRequestStatus `canceled` covers timeouts.** No new status literal needed; no `timed_out` status value.
- **Protocol echo signals observed post-turn only.** Before `turn/completed`, protocol_echo_signals is default empty tuple. Projection code should not expect pre-turn population.
- **Session API addition (`AppServerRuntimeSession.respond()`)** is in §§Data Model §§Session API addition — added during self-review, not in initial draft. Lifecycle diagrams implicitly require it.

## Conversation Highlights

**User's Q1 confirmation with sharpening (verbatim):**
> "A is the right answer for Q1, with the design rule 'single live-turn owner; registry is the only cross-thread API' made explicit before moving to Q2/Q4."
— Drove IO-1, IO-2, IO-3 promotion to named invariants.

**User's Q2 pushback on "store unchanged" (verbatim):**
> "The part I would push back on is 'store behavior unchanged.' That is not true if poll() becomes authoritative. Current poll() does not project 'the request the worker is parked on now'; it projects 'the last request ever seen for this collaboration' via requests[-1] in _project_pending_escalation. That is fine in the single-ever world, but it is not enough once one request can be resolved and a later one can appear in the same turn."
— Drove the durable selector (parked_request_id) decision.

**User's Q3 consuming-window pushback (verbatim):**
> "The consuming window is real, and right now it is not reflected in persisted live state... An immediate poll() can therefore still return the same escalation even though the caller has already decided. That is not a harmless detail, because you are also making poll() the sole observation surface."
— Drove the job.status→running early transition (D3).

**User's Q4 correction on locking (verbatim):**
> "Your 'only lock is the registry CAS' line is no longer literally true unless you explicitly accept concurrent journal writers. Under your split, main writes approval_resolution.intent and worker writes approval_resolution.dispatched/completed to the same operation journal file. write_phase() is append+fsync with no lock."
— Drove IO-4 naming and honesty framing.

**User's Q5 correction on decide() return (verbatim):**
> "decide() should not return raw job status if it returns before the worker persists running. Under your own design, the main thread can accept the decision and return while the durable job status is still needs_escalation. That would make a success payload internally contradictory."
— Drove minimal DelegationDecisionResult shape (D6).

**User's Q6 protocol echo finding (verbatim):**
> "The taxonomy is missing the strongest request-scoped signal the repo already knows about. Current code explicitly looks for serverRequest/resolved for the matching requestId and item/completed for the matching item_id in _verify_post_turn_signals() at delegation_controller.py:2088. That is stronger than your generic 'continuation' level and weaker than semantic application."
— Drove the protocol echo tier in observability taxonomy (D8).

**User's Q7 correction on IO-4 framing (verbatim):**
> "I would not freeze IO-4 as a POSIX/PIPE_BUF proof. PIPE_BUF is the pipe/FIFO guarantee, not the regular-file guarantee... So the rigorous version is narrower: this repo already relies on append-only JSONL behavior on its supported platforms, and the journal now shares that implementation assumption."
— Drove IO-4 to honest-framing (D5).

**User's Task 5 path choice (verbatim):**
> "Option A. B is mostly redundant now. Q1-Q7 already did the real substance review. C is workable, but it skips the one cheap remaining check that still matters for a dense design packet: section order, what stays in the main body versus appendix, and where the invariants live. A gives you that check without reopening settled content."
— Drove structural-preview-then-write-directly approach.

**User's 10-section outline (verbatim):**
> "1. Scope, non-goals, named invariants / 2. Runtime architecture and thread ownership / 3. Deferred-resolution lifecycle / 4. Data model and store mutations / 5. decide() / poll() contract changes / 6. Observability and honesty rules / 7. Recovery and reconciliation / 8. Timeout policy / 9. Testing and migration / 10. Rejected alternatives / rationale appendix"
— Implemented verbatim as spec structure.

## User Preferences

Validated from this session (consistent with predecessor):

**Codebase-authority-first scrutiny.** Every user correction cited file:line evidence. User pattern: accept the framing, then verify claims against specific code locations, then sharpen where specifics don't match. Future sessions: cite `file.py:lineno` for every factual claim; don't hand-wave.

**Honesty over convenience.** Recurring pattern across Q3/Q4/Q5/Q6/Q7 — user preferred names and field semantics that reflect what's honestly observable, even when it meant breaking changes or more fields. E.g., "timed_out as circumstance, not resolution_action=deny"; "inherited assumption, not proof-grade claim"; "decision_accepted not action_applied."

**Scope discipline via narrowing.** User's framing at Q7 — "Packet 1 should not specify a universal timeout→cancel rule unless it also narrows the request-kind scope." Preference: narrow around uncertainty rather than over-specify. Applied to `request_user_input` timeout handling (defer).

**Breaking changes are acceptable when forcing correctness.** User on Q5: "... every downstream caller of decide that currently reads pending_escalation is in the bug class 'observing decide() as if it's atomic with dispatch.' Silencing that class by returning empty/null to current callers would trap the bug in a different form. A hard schema break forces the fix." Accept breaking changes when the alternative is silent bugs.

**Minimal surfaces.** PendingEscalationView stays minimal (no diagnostic fields). Extension surfaces (future inspection) added explicitly; don't bloat current surfaces for speculative consumers.

**Precise naming matters.** `captured_request` → `parked_request` (semantics-matching). `closure_reason` → `completion_origin` (narrower scope). `resolution_payload` → `response_payload` (transport-honest). User sharpens names to preserve epistemic tension rather than resolve it falsely.

**Section-by-section approval pattern.** User engages deeply with each Q1-Q7 question; never accepts a round on first pass without adding 2-4 specific corrections. Future sessions with design work: expect substantive pushback per section, budget time accordingly.

**Option-A-pattern for structural decisions.** User chose Option A (structural preview) at Task 5 when offered three paths. Prior pattern (predecessor session): Option A (fresh session) when offered session-split choice. Preference for the middle-ground option that preserves a cheap check without reopening settled content.

**Artifact preservation protocol.** Rejected specs preserved on dormant branches; ticket seeds establish parent/child relationships; handoff chain carries session-specific context across sessions. User values citable artifacts over re-derivable content.

**Structured multi-choice delivery.** User's corrections typically cite alternatives, reject them with reasoning, and name the concrete action. Future sessions: offer this shape when presenting choices back.

**Verbatim quote preservation.** When capturing user preferences or pushbacks, user pattern rewards verbatim quotation over paraphrase. Paraphrase loses the precision that made the correction actionable.
