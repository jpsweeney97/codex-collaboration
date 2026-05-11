---
date: 2026-04-25
time: "01:51"
created_at: "2026-04-25T05:51:40Z"
session_id: 8f18b8c8-ef53-4c76-a2b7-14b802638e69
resumed_from: /Users/jp/.codex/handoffs/claude-code-tool-dev/.archive/2026-04-25_00-25_phase-c-complete-phase-d-next.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: bf3f8b19
title: Phase D complete; Phase E serialization and projection next
type: handoff
files:
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-d-registry.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-e-serialization-projection.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md
  - docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md
  - packages/plugins/codex-collaboration/server/resolution_registry.py
  - packages/plugins/codex-collaboration/tests/test_resolution_registry_per_request.py
  - packages/plugins/codex-collaboration/tests/test_resolution_registry_capture_ready.py
---

# Handoff: Phase D complete; Phase E serialization and projection next

## Goal

Preserve the Phase D closeout boundary for Packet 1 of `T-20260423-02`, the
deferred same-turn approval-response implementation for the `codex-collaboration`
plugin.

The session started by loading the Phase C handoff:

`/Users/jp/.codex/handoffs/claude-code-tool-dev/2026-04-25_00-25_phase-c-complete-phase-d-next.md`.

That handoff established that Phase C had completed at `ee143b25` and that the
immediate next action was Phase D orientation around the cross-thread
`ResolutionRegistry`.

The user asked:

> "Continue with a read-only Phase D orientation"

Codex stayed read-only at first, oriented on the Phase D plan and live code,
then acted as advisor through the user's Claude/coordinator-dispatched
implementation of Phase D Tasks 11 and 12.

The goal of Phase D was narrow: land `ResolutionRegistry` as an IO-2 in-memory
coordination primitive, with no controller integration, no store/journal/audit
writes, no C10.4 worker provenance wiring, and no production callsite rewrites.

At save time, Phase D is complete at `bf3f8b19`.

The next phase is Phase E, covering Tasks 13-14: `DelegationDecisionResult`
serialization shape and projection helper rewrites.

## Session Narrative

The session began with an explicit handoff load request. Codex loaded the Phase C
handoff, displayed its contents, archived the source handoff to:

`/Users/jp/.codex/handoffs/claude-code-tool-dev/.archive/2026-04-25_00-25_phase-c-complete-phase-d-next.md`

and wrote the chain state file:

`/Users/jp/.codex/.session-state/handoff-claude-code-tool-dev`.

The loaded handoff established the Phase C boundary:

- Phase C complete at `ee143b25`;
- branch `feature/delegate-deferred-approval-response`;
- `completion_origin` added and validator-covered;
- `decision=None` accepted on `approval_resolution.intent` and `.dispatched`;
- recovery-written completions annotate `completion_origin="recovered_unresolved"`;
- C10.4 worker-side `completion_origin="worker_completed"` wiring remains future work.

The user then asked for a read-only Phase D orientation. Codex first searched for
Phase D authority in `docs/plans/2026-04-24-packet-1-deferred-approval-response`
and found `phase-d-registry.md`. The orientation also read the deferred approval
response spec sections around `ResolutionRegistry`, the carry-forward tracker,
and live pre-Phase-D controller/store code.

The initial broad search for "reserve" was too noisy because it matched
"preserve" across the repo. Codex narrowed the search to `Phase D`,
`ResolutionRegistry`, `commit_signal`, `worker_completed`, and C10.4 in the
Packet 1 plan and spec.

The read-only orientation concluded that Phase D is a standalone registry phase:
Task 11 creates the per-request channel; Task 12 adds the per-job capture-ready
channel. It explicitly does not wire the controller or worker callsites.

Key orientation evidence:

- `phase-d-registry.md:1-6` defines Phase D scope and landing invariant.
- `phase-d-registry.md:10-16` defines Task 11 as the per-request channel.
- `phase-d-registry.md:551-557` defines Task 12 as the per-job capture-ready
  channel.
- `2026-04-23-deferred-approval-response-design.md:1214-1218` defines the timer
  as pure in-memory coordination, with no journal/store/audit writes.
- `carry-forward.md:48-50` shows C10.2-C10.4 are the only open Phase C items,
  and C10.4 belongs to future worker-side provenance wiring.

The orientation also read live code and verified Phase D had not yet landed:
`packages/plugins/codex-collaboration/server/resolution_registry.py` did not
exist then, and `delegation_controller.py:736-875` still showed the pre-deferred
single-thread `_execute_live_turn` handler returning cancel/empty-answer payloads.
`delegation_controller.py:1661-1878` still showed `decide()` writing
`approval_resolution.intent`, audit, `dispatched`, and `completed` in the older
synchronous/follow-up-turn shape.

Codex's first advisory output after orientation named three watchpoints:

1. Registry/timer must remain pure in-memory coordination.
2. `wait_for_parked()` storage lifecycle needed disambiguation between the plan
   template's "leave channel in place" and the spec's pop/discard-on-return
   lifecycle.
3. The timer placeholder `kind="command_approval"` in the plan template was
   semantically fragile.

The user then brought a coordinator pre-audit convergence map and asked for
decisions on O1/O2/O3. Codex chose:

- O1 = spec-aligned pop on return for `wait_for_parked()`;
- O2 = refactor `_timer_fire` to the spec pattern using `reserve()` and
  `commit_signal()`;
- O3 = dispatch Task 11 and Task 12 separately, with review between them.

The next pivot was the timeout-kind stop rule. The O2 decision made the fake
`DecisionResolution(kind="command_approval", is_timeout=True)` unacceptable:
the timer must construct a timeout resolution before `reserve()`, but the plan
template did not give the registry a real kind source.

The user presented three options:

- Option A: store kind on `register()`;
- Option B: make `DecisionResolution.kind` optional with a runtime XOR invariant;
- Option C: split the variant type into `OperatorDecision` and `TimeoutDecision`.

Codex recommended Option A, with an additional narrowing preference: if a repo
alias existed for parkable/escalatable kinds, use it rather than broad
`PendingRequestKind`. That became Task 11 DEV-6.

Claude/coordinator then dispatched Task 11. The spec reviewer reported
SPEC-COMPLIANT and the quality reviewer reported four Minor findings:

- F1: duplicate-register error format lacked `"failed:"`;
- F2: late-timer test intent was confused by an internal `_entries` membership
  assertion;
- F3: `wait()` docstring did not document caller obligation to `discard()`;
- F4: `ReservationToken.generation` did not increment, so the advertised stale
  token protection after discard/re-register was inert.

The key disposition fork was F4. The coordinator recommended Path B (docstring
only), citing the spec's "reserve is the sole coordination primitive" phrase.
Codex rejected Path B and chose Path D: make generation protection real and
tighten the docstring. The reasoning was that the spec line governs stale timer
races, but the implemented `ReservationToken` docstring explicitly promised
stale-token-after-re-register protection. Leaving an inert generation field would
be worse than either removing it or making it real.

The user accepted that disposition and Task 11 closed with three commits:

- `55444d94` feature;
- `8d4f9b96` closeout fix;
- `04421cba` closeout docs.

The user then asked whether to proceed with Task 12 or save. Codex recommended
proceeding in the same session because the Task 12 design locks were fresh, Task
11 was cleanly closed, and Task 12 remained standalone.

Task 12 then dispatched independently. The spec reviewer reported
SPEC-COMPLIANT and the quality reviewer reported four Minor findings:

- F1: late-signal log should be `WARNING`, not `INFO`, for symmetry with Task 11
  stale-token discard;
- F2: threading tests should assert `not t.is_alive()` after joins;
- F3: duplicate `wait_for_parked(job_id)` error path needed a test;
- F4: the defensive `channel_now is None` branch in `wait_for_parked()` needed
  an honest future-proofing comment.

Codex recommended bundling all four into a single Task 12 closeout fix commit,
with F4 handled by strengthening the comment rather than replacing the branch
with `assert False`.

Task 12 then closed with three commits:

- `6aa623c0` feature;
- `becbb124` closeout fix;
- `bf3f8b19` closeout docs and Phase D complete.

The user reported final verification:

> "Working tree clean. 974 tests passing in codex-collaboration package"

and:

> "Phase D fully closed"

Codex verified during save that the live branch is
`feature/delegate-deferred-approval-response`, `git rev-parse --short HEAD`
returns `bf3f8b19`, and `git status --short --branch` showed the branch with no
dirty files.

Codex did not rerun the 974-test suite during this handoff save. The 974-pass
result is user-reported.

## Decisions

### Decision 1: Keep Phase D orientation read-only until dispatch decisions

**Choice:** Codex performed read-only Phase D orientation before advising on
dispatch shape or implementation details.

**Driver:** The user explicitly asked: "Continue with a read-only Phase D
orientation."

**Rejected alternative:** Start editing or drafting Task 11 code immediately.

**Why rejected:** The user asked for orientation, not implementation. Also the
Phase C handoff emphasized respecting advisory boundaries when Claude dispatches
implementation.

**Implication:** Future Codex should treat this session as Codex advisory/review
and user/Claude-coordinator implementation, not as Codex authoring the Phase D
source code directly.

**Trade-offs:** Codex relied on user/coordinator-reported full-suite and reviewer
results instead of executing every verification gate itself.

**Confidence:** High (E3). Evidence combines the user quote, the actual action
sequence, and final commit ownership narrative supplied by the user.

**Reversibility:** High. Future user can explicitly ask Codex to implement a
phase directly.

**Change trigger:** Reconsider only if the user says Codex should stop being
advisory and take over implementation.

### Decision 2: Use spec-aligned pop-on-return for `wait_for_parked()`

**Choice:** `wait_for_parked()` owns the capture-channel lifecycle by popping
`_capture_channels[job_id]` before returning.

**Driver:** The user highlighted a divergence between the plan's line 871-872
comment and spec wording: plan-literal leaves the channel in place until a future
external discard, while the spec says discard/pop on return.

**Rejected alternative:** Plan-literal lifecycle: leave channel in place with
`resolved=True` and rely on `start()` or a future explicit discard to clean it.

**Why rejected:** Task 12 is a standalone primitive and the plan did not define
that external discard method. Leaving state behind creates an unnecessary hidden
lifecycle dependency.

**Rejected alternative:** Defer the lifecycle decision to Phase G/H.

**Why rejected:** The Task 12 tests and implementation shape necessarily choose
a lifecycle now. Deferring would leave a contradiction in the standalone
registry primitive.

**Implication:** Late `announce_*` calls after `wait_for_parked()` returns see
`channel is None` in `_deliver_capture_outcome()` and warn-no-op. This is now
documented in `resolution_registry.py:351-360` and implemented at
`resolution_registry.py:382-389`.

**Trade-offs:** A late outcome that races after the start-wait budget can be
discarded in favor of `StartWaitElapsed`. This is accepted under O1=(b);
durable worker state remains authoritative and poll observes it later.

**Confidence:** High (E3). Evidence includes the spec lifecycle, user-provided
divergence analysis, and final implementation/tests at
`test_resolution_registry_capture_ready.py:123-142`.

**Reversibility:** Medium. Changing to plan-literal retention would require
changing implementation, tests, and likely introducing a real discard method.

**Change trigger:** Reconsider if Phase G/H introduces an explicit
`discard_capture_channel(job_id)` method that needs to preserve channel state
after `wait_for_parked()`.

### Decision 3: Refactor `_timer_fire()` to reuse `reserve()` and `commit_signal()`

**Choice:** The timer path uses the same CAS primitive as operator decisions:
construct timeout resolution, call `reserve()`, and call `commit_signal()` only
if the token is non-None.

**Driver:** The spec says the timer callback does only in-memory state changes
and wake signal via `token = reserve(...); if token is None: return;
commit_signal(token)`. See `2026-04-23-deferred-approval-response-design.md:1214-1218`.

**Rejected alternative:** Keep the plan-template inline state mutation in
`_timer_fire()`, with `entry.state = "reserved"` followed by
`entry.state = "consuming"` in one lock.

**Why rejected:** That duplicated the CAS logic and made `reserve()` less clearly
the primitive. It also carried a dead duplicate guard and made future behavior
drift more likely.

**Rejected alternative:** Inline cleanup only: remove dead guard and collapse to
direct `entry.state = "consuming"`.

**Why rejected:** It would still shadow-copy the transition instead of using the
primitive being tested.

**Implication:** `resolution_registry.py:393-408` now documents and implements
the pure timer path: no stores, no journal, no audit, no controller/session
touches.

**Trade-offs:** The timer uses more than one lock acquisition because it leaves
the lock to call `reserve()`/`commit_signal()`. This is acceptable because the
timeout path is not hot and clarity wins.

**Confidence:** High (E3). Evidence includes spec text, final code at
`resolution_registry.py:393-408`, and tests at
`test_resolution_registry_per_request.py:172-223`.

**Reversibility:** Medium. Reverting to inline mutation is technically easy but
would weaken the phase-defining invariant.

**Change trigger:** Reconsider only if profiling proves timer lock acquisition is
a real bottleneck, which is unlikely for an operator-window timeout path.

### Decision 4: Store request kind on `register()` instead of fake placeholder or nullable kind

**Choice:** `ResolutionRegistry.register()` accepts `kind: EscalatableRequestKind`
and stores it on `_RegistryEntry`; timer-generated `DecisionResolution` uses that
authoritative kind.

**Driver:** The user surfaced a stop-rule: timeout `DecisionResolution.kind`
could not be represented without a fake placeholder once `_timer_fire()` reused
`reserve()`/`commit_signal()`.

**Rejected alternative:** Hardcoded placeholder `kind="command_approval"` with
documentation saying the worker re-reads kind on wake.

**Why rejected:** That is a documentation-only invariant and future consumers
could misuse the fake kind as authoritative.

**Rejected alternative:** `kind: PendingRequestKind | None` plus `__post_init__`
XOR invariant.

**Why rejected:** It pushes nullable-kind handling to every consumer and still
requires runtime discipline.

**Rejected alternative:** Variant split (`OperatorDecision` + `TimeoutDecision`).

**Why rejected:** It is the cleanest abstract type model but too much API churn
for Phase D's standalone primitive. It can be revisited if Phase F consumers find
`is_timeout` awkward.

**Implication:** `DecisionResolution.kind` is authoritative for timeout and
operator decisions. It is narrowed to `EscalatableRequestKind` at
`resolution_registry.py:24` and `:38-40`. `_RegistryEntry.kind` is defined at
`resolution_registry.py:135-147`; `register()` stores it at `:173-207`; timer
uses it at `:399-405`.

**Trade-offs:** Phase F callsites must pass `kind=` when calling `register()`.
This is a small API cost but the worker has the request kind in scope when it
registers.

**Confidence:** High (E3). Evidence includes the user-provided O4 options, final
implementation, and timer test assertion at
`test_resolution_registry_per_request.py:172-188`.

**Reversibility:** Medium. Moving to the variant split would require test and
consumer rewrites.

**Change trigger:** Reconsider if Phase F shows consumers branching so heavily
on `is_timeout` that a variant split becomes clearer and lower risk.

### Decision 5: Separate Task 11 and Task 12 dispatches with review between

**Choice:** Phase D used two independent dispatches and review boundaries:
Task 11 per-request channel, then Task 12 per-job capture-ready channel.

**Driver:** Codex recommended O3 = separate dispatches because Task 11 is the
load-bearing coordination primitive and Task 12 introduces a separate lifecycle
table and late-signal behavior.

**Rejected alternative:** One combined dispatch for all Phase D code.

**Why rejected:** Combining would enlarge the review surface and risk masking a
bug in one channel with passing behavior in the other.

**Implication:** Phase D landed as six commits: Task 11 feature/fix/docs and
Task 12 feature/fix/docs.

**Trade-offs:** More commits and more review overhead. Accepted because the
branch has already established per-task closeout discipline in Phases B/C/D.

**Confidence:** High (E3). Evidence is final commit sequence from
`git log --oneline b6dbaa3c..HEAD`, with Phase D commits `55444d94`,
`8d4f9b96`, `04421cba`, `6aa623c0`, `becbb124`, and `bf3f8b19`.

**Reversibility:** Low for this phase; history is already shaped. High for
future phases if the user explicitly chooses larger batches.

**Change trigger:** Reconsider if a later phase has tiny tasks with no separate
review value, but default remains per-task discipline.

### Decision 6: Escalate Task 11 F4 to Path D, not docstring-only Path B

**Choice:** Make `ReservationToken.generation` protection real and tighten the
docstring.

**Driver:** Quality review found the generation counter never incremented while
the docstring claimed stale-token protection. Codex concluded this was an
implementation-promise mismatch, not merely defensive cruft.

**Rejected alternative:** Path B: rewrite the docstring to admit generation is
reserved/future and current protection relies on CAS-only semantics.

**Why rejected:** The implemented token already had a generation field and guard,
and the docstring claimed it protected stale tokens after discard/re-register.
Retreating the docstring would leave dead state and make the code harder to
reason about.

**Rejected alternative:** Carry F4 forward as Minor.

**Why rejected:** The fix was small and directly improved the phase artifact.

**Implication:** `_next_generation` exists at `resolution_registry.py:165-169`,
increments under lock in `register()` at `:184-191`, and is documented at
`ReservationToken` lines `111-123`. The regression test at
`test_resolution_registry_per_request.py:226-280` pins the exploit path.

**Trade-offs:** Generation protection is now load-bearing beyond the minimum
timer-CAS spec. Accepted because it matches the advertised token contract and
costs little.

**Confidence:** High (E3). Evidence includes quality finding, user/coordinator
discussion, final code, and regression test.

**Reversibility:** Medium. Removing generation would require deleting the guard,
docstring claim, and test.

**Change trigger:** Reconsider only if future registry lifecycle forbids
request_id reuse entirely and a simpler invariant is formally documented.

### Decision 7: Bundle minor closeout findings instead of carrying them forward

**Choice:** Both Task 11 and Task 12 bundled all Minor quality findings into
single closeout fix commits.

**Driver:** Earlier authorization said: "If only minor surgical findings surface,
use the same closeout-fix pattern rather than carry-forward by default."

**Rejected alternative:** Carry all Minor findings forward.

**Why rejected:** The findings were local, low-cost, and improved the phase's
own artifact clarity and tests.

**Rejected alternative:** Split each minor into separate commits.

**Why rejected:** That would create unnecessary commit noise for tightly related
review-discovered polish.

**Implication:** No new open carry-forward items were added during Phase D.
`carry-forward.md:74-90` records both Phase D Task 12 and Task 11 closeout
entries under Closed items.

**Trade-offs:** Phase D has more commits than a pure feature-only phase, but
the closeout trail is explicit and reviewable.

**Confidence:** High (E3). Evidence includes final carry-forward tracker state
and commit list.

**Reversibility:** Low for Phase D history; high as a future policy if user
changes preference.

**Change trigger:** Reconsider if a future finding is truly unrelated or large
enough to distract from the phase objective.

## Changes

Codex did not directly edit repository files in this session. Claude/user
implementation produced the Phase D commits. Codex advised on decisions,
review-disposition choices, and handoff save.

Live `git log --oneline b6dbaa3c..HEAD` at save time shows 20 commits from the
Phase A baseline `b6dbaa3c`. Phase D added six commits on top of Phase C:

- `55444d94 feat(delegate): add ResolutionRegistry per-request channel + CAS protocol (T-20260423-02 Task 11)`
- `8d4f9b96 fix(delegate): tighten ResolutionRegistry generation guard + closeout polish (T-20260423-02 Task 11 closeout)`
- `04421cba docs(delegate): record Phase D Task 11 closeout (T-20260423-02)`
- `6aa623c0 feat(delegate): add ResolutionRegistry capture-ready channel (T-20260423-02 Task 12)`
- `becbb124 fix(delegate): tighten ResolutionRegistry capture-ready closeout polish (T-20260423-02 Task 12 closeout)`
- `bf3f8b19 docs(delegate): record Phase D Task 12 closeout — Phase D complete (T-20260423-02)`

### `packages/plugins/codex-collaboration/server/resolution_registry.py`

New file introduced by Phase D.

Purpose: in-memory cross-thread coordination for deferred approval. The module
docstring states the registry is the only in-memory mutable state crossing
threads and defines two independent channels: per-request and per-job
capture-ready (`resolution_registry.py:1-14`).

Per-request channel:

- `DecisionResolution` carries `payload`, authoritative
  `EscalatableRequestKind`, and `is_timeout` at `resolution_registry.py:32-40`.
- `InternalAbort` carries `reason` and documents that worker owns all durable
  state writes at `resolution_registry.py:43-51`.
- `ReservationToken` carries `request_id` and generation, with docstring
  explaining stale-token-after-re-register protection at
  `resolution_registry.py:111-127`.
- `_RegistryEntry` stores `request_id`, `job_id`, `kind`, timeout, state,
  generation, event, pending resolution, and timer at
  `resolution_registry.py:135-147`.
- `register()` creates awaiting entries, increments `_next_generation`, and
  starts a daemon timer at `resolution_registry.py:173-207`.
- `reserve()` is the CAS `awaiting -> reserved` and returns `None` if the
  entry is absent or not awaiting at `resolution_registry.py:209-223`.
- `commit_signal()` checks generation, transitions `reserved -> consuming`,
  cancels the timer, and fires the event at `resolution_registry.py:225-248`.
- `abort_reservation()` returns `reserved -> awaiting` if the token is current
  at `resolution_registry.py:250-259`.
- `wait()` blocks and documents the caller's obligation to call `discard()` at
  `resolution_registry.py:261-281`.
- `discard()` is idempotent and cancels the timer if present at
  `resolution_registry.py:283-288`.
- `signal_internal_abort()` transitions `awaiting -> aborted`, sets
  `InternalAbort(reason)`, cancels timer, and wakes worker at
  `resolution_registry.py:290-306`.
- `_timer_fire()` reuses `reserve()`/`commit_signal()` and writes no stores,
  journal, audit, session, or controller state at `resolution_registry.py:393-408`.

Per-job capture-ready channel:

- `Parked`, `TurnCompletedWithoutCapture`, `TurnTerminalWithoutEscalation`,
  `WorkerFailed`, and `StartWaitElapsed` are defined at
  `resolution_registry.py:60-105`.
- `_CaptureReadyChannel` stores the channel event/outcome/resolved flag at
  `resolution_registry.py:153-158`.
- `announce_parked`, `announce_turn_completed_empty`,
  `announce_turn_terminal_without_escalation`, and `announce_worker_failed`
  delegate to `_deliver_capture_outcome()` at `resolution_registry.py:310-332`.
- `_deliver_capture_outcome()` warning-logs late signals and otherwise stores
  the outcome and wakes the waiter at `resolution_registry.py:334-349`.
- `wait_for_parked()` creates the channel, waits with timeout, synthesizes
  `StartWaitElapsed` on budget expiry, pops the channel under lock before
  return, and documents O1=(b) lifecycle at `resolution_registry.py:351-389`.

Important design boundary: this file still has no imports of journal/store/
controller/session surfaces. It imports only `logging`, `threading`,
`dataclass`, `field`, typing helpers, and `EscalatableRequestKind`.

### `packages/plugins/codex-collaboration/tests/test_resolution_registry_per_request.py`

New Task 11 test file.

It covers:

- value types (`DecisionResolution`, `InternalAbort`, `Resolution`) at lines
  `16-34`;
- register/reserve CAS at lines `37-74`;
- worker wait wake on `commit_signal` at lines `77-99`;
- abort reservation at lines `102-119`;
- internal abort wake/idempotency/race with operator decide at lines `122-162`;
- discard idempotency at lines `165-169`;
- timer synthetic timeout resolution with authoritative kind at lines `172-188`;
- late timer no-op with observable worker result at lines `191-223`;
- F4 closeout stale-token-after-discard-and-reregister regression at lines
  `226-280`.

The final test is especially important: it proves old token generation cannot
commit into a re-registered entry with the same request id.

### `packages/plugins/codex-collaboration/tests/test_resolution_registry_capture_ready.py`

New Task 12 test file.

It covers:

- five `ParkedCaptureResult` variants at lines `21-48`;
- `announce_parked` wake at lines `51-66`;
- `announce_turn_completed_empty` wake at lines `69-82`;
- `announce_turn_terminal_without_escalation` wake at lines `85-103`;
- `announce_worker_failed` wake at lines `106-120`;
- `StartWaitElapsed` plus O1=(b) channel pop assertion at lines `123-128`;
- late announce no-raise behavior at lines `131-142`;
- per-job independence with two threads at lines `145-165`;
- duplicate `wait_for_parked` error path at lines `168-190`.

Task 12 closeout added the `assert not t.is_alive()` pattern to threading tests
and added the duplicate-job-id test.

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md`

Phase D added no open items.

Open items remain exactly 12:

- A1-A5 (`carry-forward.md:17-21`);
- B6.1-B6.2 (`carry-forward.md:27-28`);
- B7.1-B7.2 (`carry-forward.md:34-35`);
- B8.1-B8.2 (`carry-forward.md:41-42`);
- C10.2-C10.4 (`carry-forward.md:48-50`).

Closed entries now include Phase D Task 12 and Task 11 closeout records:

- Task 12 closeout at `carry-forward.md:74-82`;
- Task 11 closeout at `carry-forward.md:84-90`.

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-e-serialization-projection.md`

Read during save to establish the next boundary.

Phase E scope is Tasks 13-14:

- Task 13 rewrites `DelegationDecisionResult` to three fields and fixes MCP
  serialization (`phase-e-serialization-projection.md:10-20`);
- Task 14 rewrites projection helpers, including
  `UnknownKindInEscalationProjection`, `_project_request_to_view`, and
  `_project_pending_escalation` (`phase-e-serialization-projection.md:190-197`).

Task 13 is explicitly a breaking contract change:

> "Callers that read `pending_escalation` or `agent_context` from `decide`'s
> response must switch to `poll()`" (`phase-e-serialization-projection.md:20`).

Task 14's core helper rule is purity:

`_project_pending_escalation` returns `None` for legitimate no-view states and
re-raises `UnknownKindInEscalationProjection` for invariant violations; it does
not signal internal abort itself (`phase-e-serialization-projection.md:403-429`).

## Codebase Knowledge

### Registry is pure in-memory coordination

`resolution_registry.py:1-14` states the module's charter: it is the only
in-memory mutable state crossing threads, with a registry-wide lock and
per-entry events.

There are no durable writes in the registry. `_timer_fire()` explicitly says
"No store, journal, or audit writes here" and implements only
`DecisionResolution` construction, `reserve()`, and `commit_signal()`
(`resolution_registry.py:393-408`).

This matters because future Phase F/G integration must not put store/journal/
audit/session side effects inside registry methods. Those belong to worker or
controller callsites.

### Two independent channels

Per-request channel:

`request_id -> _RegistryEntry`, state machine:

```
awaiting -> reserved -> consuming
awaiting -> aborted
```

Per-job capture-ready channel:

`job_id -> _CaptureReadyChannel`, one-shot outcome:

```
Parked | TurnCompletedWithoutCapture | TurnTerminalWithoutEscalation |
WorkerFailed | StartWaitElapsed
```

These are independent. A late `announce_parked` after `wait_for_parked()` has
popped the capture-ready channel does not remove the per-request entry.
Future poll/decide integration must preserve this separation.

### Timer semantics

The timer is not a store writer and not an audit surface. It uses the stored
`EscalatableRequestKind` from `_RegistryEntry.kind` to create a timeout
`DecisionResolution` (`resolution_registry.py:399-405`) and then goes through
the same `reserve()`/`commit_signal()` path as other resolutions.

The timer test pins that timeout resolution is real and carries the registered
kind (`test_resolution_registry_per_request.py:172-188`).

### Generation guard is real

Task 11 closeout made generation counter load-bearing. `_next_generation` is
initialized at `resolution_registry.py:165-169`, incremented under the registry
lock at `resolution_registry.py:184-191`, stored in entries at
`resolution_registry.py:193-200`, and checked in `commit_signal()` and
`abort_reservation()` at `resolution_registry.py:229-255`.

Regression test `test_stale_token_after_discard_and_reregister_is_rejected`
walks the exact stale-token exploit shape at
`test_resolution_registry_per_request.py:226-280`.

### Capture-ready lifecycle

`wait_for_parked()` owns channel cleanup. It pops `_capture_channels[job_id]`
under lock before return (`resolution_registry.py:386-388`). Late `announce_*`
calls see no channel and log a warning in `_deliver_capture_outcome()`
(`resolution_registry.py:337-345`).

The channel pop is pinned by `test_start_wait_elapsed_when_budget_expires_without_signal`
at `test_resolution_registry_capture_ready.py:123-128`.

### Error format convention

Task 11 and Task 12 closeouts normalized registry error messages to the project
format:

- `register()` duplicate request: `"ResolutionRegistry.register failed:
  duplicate request_id. Got: ..."` at `resolution_registry.py:184-189`;
- `wait_for_parked()` duplicate job id:
  `"ResolutionRegistry.wait_for_parked failed: duplicate job_id. Got: ..."` at
  `resolution_registry.py:362-367`.

Future registry errors should follow the same format.

### Threading test pattern

Threading tests should call `join(timeout=...)` and immediately assert
`not t.is_alive()` before inspecting result lists. Task 11 uses this at
`test_resolution_registry_per_request.py:95-99`, `:136-140`, `:183-188`,
`:213-223`, and `:276-280`. Task 12 closeout aligned its tests at
`test_resolution_registry_capture_ready.py:62-66`, `:80-82`, `:98-103`,
`:117-120`, `:160-165`, and `:189-190`.

### Phase E live targets

`phase-e-serialization-projection.md:10-20` defines Task 13:

- rewrite `DelegationDecisionResult` in `models.py`;
- fix the MCP serializer branch in `mcp_server.py`;
- add tests for dataclass shape and MCP serialization.

`phase-e-serialization-projection.md:190-197` defines Task 14:

- rewrite projection helpers in `delegation_controller.py`;
- add a new `test_projection_helpers.py`.

Task 14 is the natural resolution point for carry-forward item A3:
`carry-forward.md:19` says Task 14 `_project_request_to_view` rewrite will
resolve the expected Pyright error around `PendingRequestKind` vs
`EscalatableRequestKind`.

## Context

Packet 1 is deferred same-turn approval response for `codex-collaboration`.

Broader mental model now locked:

- registry = in-memory coordination only;
- stores = durable forensic/recovery surfaces;
- worker = session-bound cleanup and transport owner after wake;
- main = accepted operator intent before commit;
- audit = best-effort, never a gate for durable or wake transitions.

Phase D adds the missing in-memory coordination primitive. It does not yet make
public API behavior asynchronous. That comes later:

- Phase E prepares serialization/projection surfaces;
- Phase F introduces worker runner and handler sentinel paths;
- Phase G rewrites `start()` and `decide()` public API behavior;
- Phase H updates finalizer guard, consumers, and contracts.

At the end of Phase D, `ResolutionRegistry` is available as a standalone unit
with complete unit coverage. It is not yet injected into `DelegationController`.

Important sequence from the Phase D final user report:

> "Phase D fully closed"

and:

> "Working tree clean. 974 tests passing in codex-collaboration package"

Codex verified clean branch state and HEAD during save but did not rerun the
full test suite.

## Learnings

### Spec lines can be narrower than implementation promises

Task 11 F4 showed that a spec sentence can govern one race class while an
implementation docstring promises a broader guarantee. The coordinator cited
spec §1216 ("reserve is the sole coordination primitive") as a reason to
docstring-retreat generation protection. Codex rejected that because §1216
governs stale timer races; `ReservationToken` explicitly promised stale-token
protection after discard/re-register.

Implication: future reviews should distinguish "spec minimum" from
"implementation promise already made in code." If the code advertises a
stronger invariant, either make it true or remove it deliberately.

### Fake placeholder values should be treated as type-design blockers

The original plan template's timeout placeholder `kind="command_approval"` was
not merely an implementation wart. It would have let consumers misuse a fake
kind as authoritative. The chosen fix was to make `register(kind=...)` supply
the authoritative kind once and carry it through the registry.

Implication: when a placeholder is used because "the consumer will ignore it,"
ask whether the type can make misuse impossible or unnecessary.

### Pop-on-return changes observability but not durable truth

Under O1=(b), a late `announce_*` after `wait_for_parked()` returns logs a
warning and does not deliver a capture-ready result to start. This can discard
the late in-memory outcome, but durable state written before the announce remains
authoritative and poll observes it later. This is documented in the spec's late
start-outcome signal model and implemented at `resolution_registry.py:351-389`.

Implication: Phase G start/poll integration must rely on durable state for late
outcomes, not on capture channel persistence.

### Closeout fixes are now the default for local surgical findings

Phase D matched the Phase B/C pattern: minor findings with direct phase-artifact
impact were fixed in closeout commits, not carried forward. The carry-forward
tracker remains at 12 open items; no Phase D opens were added.

Implication: future phase reviews should continue using the three-axis severity
heuristic, but local cheap fixes should generally close in-scope.

## Next Steps

### 1. Start Phase E orientation with Task 13

Read:

- `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-e-serialization-projection.md`
- `packages/plugins/codex-collaboration/server/models.py`
- `packages/plugins/codex-collaboration/server/mcp_server.py`
- tests that currently assert `DelegationDecisionResult` old shape.

Task 13 scope from `phase-e-serialization-projection.md:10-20`:

- rewrite `DelegationDecisionResult` to exactly
  `{decision_accepted, job_id, request_id}`;
- remove or collapse the custom MCP serializer branch;
- update existing tests that assert `decision`, `resumed`, `job`,
  `pending_escalation`, or `agent_context`.

Acceptance criteria:

- `asdict(DelegationDecisionResult(...))` emits exactly three keys;
- MCP decide response emits exactly the same three keys;
- callers that need post-dispatch state switch to `poll()`.

### 2. Then dispatch/review Task 14 separately

Task 14 scope from `phase-e-serialization-projection.md:190-197`:

- add `_ESCALATABLE_REQUEST_KINDS`;
- make `_project_request_to_view` raise `UnknownKindInEscalationProjection` for
  non-escalatable kinds;
- rewrite `_project_pending_escalation(job)` as job-anchored, pure, and
  tombstone-aware.

Watch the helper-purity invariant in `phase-e-serialization-projection.md:403-429`:
helpers do not call `signal_internal_abort`, do not log critical errors, and do
not write stores. Callers own semantics.

### 3. Preserve C10.4 for Phase F

C10.4 remains open at `carry-forward.md:50`. It says
`completion_origin="worker_completed"` is schema-valid but not production-wired.

Default action:

Do not wire it in Phase E. It belongs naturally in Phase F worker callsites,
where worker-written completed records become real.

### 4. Use broad verification at phase close

The user reported Phase D final suite:

> "974 tests passing in codex-collaboration package"

For Phase E, run targeted tests for each task and then broad package tests before
phase closeout if implementation changes shared models, MCP serialization, or
projection helpers.

## In Progress

Clean stopping point.

Phase D is complete at `bf3f8b19`.

No repository edits are in progress by Codex.

Working tree was clean when Codex checked `git status --short --branch` during
save; output showed only:

`## feature/delegate-deferred-approval-response`

The immediate next action is Phase E Task 13 orientation in a fresh session.

No blocker is active.

Operational caution:

The full `974 tests passing` result was reported by the user, not rerun by Codex
during handoff save.

## Open Questions

### Should Phase E follow the same 3-commit-per-task shape?

Default answer: yes if review surfaces closeout findings. If Task 13 or Task 14
lands cleanly with no real fix, do not force a fix commit. But the Phase D
pattern reinforces per-task feature, closeout fix when needed, and closeout docs.

### Should Task 13 and Task 14 be dispatched separately?

Default answer: yes. Task 13 changes public decision result shape and MCP
serialization. Task 14 changes projection helper semantics. They are related but
reviewable independently.

### Does Task 14 close A3?

Likely yes. `carry-forward.md:19` explicitly says Task 14 rewrite resolves the
expected Pyright error at the `PendingRequestKind` vs `EscalatableRequestKind`
construction site. Confirm during Task 14 closeout before moving A3 to closed.

### Does Phase E need to update contracts?

Task 13 is a breaking contract change, but the plan says it is flagged for Phase
H contracts update (`phase-e-serialization-projection.md:5-6`). Do not expand
Phase E into contract docs unless the plan or user says to.

## Risks

### Risk 1: Phase E may accidentally wire controller async behavior early

Task 13 changes the result shape, but it does not fully implement Phase G
`decide()` async behavior. Watch for implementation that starts using the
registry in controller callsites during Phase E.

Mitigation: keep Phase E scoped to model serialization and projection helpers.

### Risk 2: Removing old decision result fields will break many tests

The plan anticipates failures where tests assert `result.decision`,
`result.resumed`, `result.pending_escalation`, or `result.agent_context`
(`phase-e-serialization-projection.md:150-164`).

Mitigation: update tests according to new async contract. For post-dispatch
state, use `poll()`, not `decide()` response fields.

### Risk 3: Projection helper purity can be violated

Task 14 helper rewrite must not call `signal_internal_abort`, log critical
errors, or mutate stores. Callsite ownership is explicit at
`phase-e-serialization-projection.md:403-429`.

Mitigation: review helper implementation for pure return/raise only.

### Risk 4: C10.4 may tempt premature worker provenance wiring

`completion_origin="worker_completed"` remains open and adjacent, but Phase E
does not write worker completions.

Mitigation: defer to Phase F, where worker paths are in scope.

### Risk 5: Pyright harness divergence can distract from production diagnostics

The user reported a locked pattern: CLI pyright on production source is ground
truth; harness pyright on test files may lag. This surfaced across Phase B and
Phase D.

Mitigation: for Phase E, do not over-investigate known harness-only divergence
unless production-source diagnostics are affected.

## References

- Archived source handoff:
  `/Users/jp/.codex/handoffs/claude-code-tool-dev/.archive/2026-04-25_00-25_phase-c-complete-phase-d-next.md`
- Current branch:
  `feature/delegate-deferred-approval-response`
- Current HEAD:
  `bf3f8b19`
- Phase A baseline:
  `b6dbaa3c`
- Phase D plan:
  `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-d-registry.md`
- Phase E plan:
  `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-e-serialization-projection.md`
- Phase F plan:
  `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md`
- Carry-forward tracker:
  `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md`
- Deferred approval response spec:
  `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`
- Resolution registry:
  `packages/plugins/codex-collaboration/server/resolution_registry.py`
- Task 11 tests:
  `packages/plugins/codex-collaboration/tests/test_resolution_registry_per_request.py`
- Task 12 tests:
  `packages/plugins/codex-collaboration/tests/test_resolution_registry_capture_ready.py`

Verification commands Codex ran during save:

- `git status --short --branch`
- `git rev-parse --short HEAD`
- `git log --oneline b6dbaa3c..HEAD`
- `git diff --name-only b6dbaa3c..HEAD`

User-reported verification after Phase D close:

- `974 tests passing` in codex-collaboration package
- working tree clean
- branch tip `bf3f8b19`
- 20 commits from Phase A baseline `b6dbaa3c`

## Gotchas

### `field` import belongs to Task 12

Task 11 intentionally deferred `field`; final `resolution_registry.py` now imports
`field` because `_CaptureReadyChannel.event` uses
`field(default_factory=threading.Event)` at `resolution_registry.py:153-158`.

### `resolved` flag is less observable under O1=(b)

Because `wait_for_parked()` pops the channel before return, `_CaptureReadyChannel.resolved`
is not externally observable after normal return. It still protects against
double-delivery inside a live channel. Carry-forward closed note at
`carry-forward.md:82` says a future touch can add a comment if needed.

### `wait()` requires `discard()`

The caller obligation is now documented at `resolution_registry.py:261-267`.
Future worker integration must call `discard(request_id)` after consuming a
per-request resolution; otherwise entries persist.

### `wait_for_parked()` pops; do not add external cleanup blindly

O1=(b) means the channel is removed before return. A future `start()` integration
should not assume it needs a separate cleanup method after `wait_for_parked()`.

### `DecisionResolution.kind` is authoritative

The timeout path no longer uses a fake `"command_approval"` kind. The registry
stores `kind` from `register()` and uses that in `_timer_fire()`. Future Phase F
callsites must pass the real request kind.

### Phase E is breaking by design

Task 13 removes old `DelegationDecisionResult` fields. Do not preserve old fields
just to keep tests easy. The plan says callers must switch to `poll()`.

## Conversation Highlights

The user established the Phase D orientation boundary:

> "Continue with a read-only Phase D orientation"

Codex reported the first read-only orientation and named the main watchpoints:

> "The Phase D file exists at `docs/plans/.../phase-d-registry.md`"

The user then supplied a convergence map and asked three open questions:

> "O1 (Watchpoint 2 disambiguation)"
> "O2 (DEV-3 timer pattern)"
> "O3 (Task 11+12 dispatch shape)"

Codex chose:

> "O1: Choose (b), spec-aligned pop on return."

and:

> "O2: Choose (a), refactor `_timer_fire` to the spec pattern."

and:

> "O3: Dispatch Task 11 and Task 12 separately, with review in between."

The user surfaced the timeout-kind blocker:

> "STOP-RULE TRIGGERED: timeout `DecisionResolution.kind` cannot be represented without a fake placeholder"

Codex recommended Option A:

> "Recommend Option A, with one tightening: make the stored kind as narrow as the existing model allows."

Task 11 quality review then created the key F4 fork. The user asked:

> "What's your call?"

Codex answered:

> "My call: Path D for F4, bundled closeout fix for all four findings."

After Task 11 closed, the user asked whether to proceed or save:

> "Want me to proceed with the Task 12 pre-dispatch audit + dispatch in this session, or save a handoff here?"

Codex recommended proceeding:

> "Proceed in this session. I would not save a handoff yet unless you are intentionally trying to keep Task 12 review in a fresh context."

Task 12 quality review surfaced only Minor findings. The user asked whether to
proceed with bundled closeout fix. Codex answered:

> "Proceed with the bundled closeout fix as proposed."

The final user closeout said:

> "Phase D fully closed"

and:

> "This is a natural save point — Phase D closes cleanly, Phase E is a fresh dispatch boundary in a new session."

## User Preferences

The user values read-only orientation when requested. Evidence:

> "Continue with a read-only Phase D orientation"

The user values convergence maps between coordinator and Codex review surfaces.
Evidence:

> "Convergence Map: Coordinator Pre-Audit ⟷ Your Dispatch-Watch-Outs"

The user wants explicit option selection and defended recommendations. Evidence:

> "Make a recommendation and defend it."

The user treats stop rules as real dispatch blockers, not implementation details
to rationalize around. Evidence:

> "STOP-RULE TRIGGERED: timeout `DecisionResolution.kind` cannot be represented without a fake placeholder"

The user values the Phase B/C closeout discipline: local minor findings can be
fixed in closeout commits when cheap and phase-local. Evidence:

> "Per earlier authorization ('If only minor surgical findings surface, use the same closeout-fix pattern rather than carry-forward by default')"

The user wants C10.4 kept out of Phase D and Phase E unless naturally in worker
callsite scope. Evidence:

> "No C10.4 wiring in Task 12 — that's Phase F worker-callsite scope"

The user tracks exact commit shape and test deltas. Evidence:

> "Phase D fully closed"

and:

> "974 tests passing in codex-collaboration package (was 944 at session start; +30 = 16 Task 11 + 1 Task 11 closeout regression + 12 Task 12 + 1 Task 12 closeout coverage)."

The user considers Phase E a fresh session boundary. Evidence:

> "This is a natural save point — Phase D closes cleanly, Phase E is a fresh dispatch boundary in a new session."

