---
date: 2026-04-24
time: "00:53"
created_at: "2026-04-24T04:53:00Z"
session_id: 96e846f7-91e4-4212-9e6f-dc6f2015dcde
resumed_from: docs/handoffs/archive/2026-04-23_22-04_deferred-approval-spec-round-2-scrutiny-revised.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: fa4955b4
title: Deferred approval spec — rounds 7-10 scrutiny cycle
type: handoff
files:
  - docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md
---

# Handoff: Deferred approval spec — rounds 7-10 scrutiny cycle

## Goal

Drive Packet 1 design spec at `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` to approval through the user's iterative structured-scrutiny process. Spec unblocks ticket `T-20260423-02` (Packet 1 deferred same-turn approval response) which in turn unblocks `T-20260423-01 AC1`. The goal for this session specifically: advance from HEAD `1f2f1f72` (round-6 commit) through rounds 7/8/9/10 of scrutiny, with each round delivered by user via `/copy` and resolved as one coherent commit.

**Trigger:** Session resumed from `2026-04-23_22-04_deferred-approval-spec-round-2-scrutiny-revised.md`; the prior session had progressed through rounds 1-6 and ended mid-round-7 scrutiny.

**Stakes:** Packet 1 is the foundational design for deferred same-turn approval responses. Without spec approval, `superpowers:writing-plans` cannot decompose it into implementation phases, which blocks T-20260423-01 AC1. Five rounds in this session is itself a signal that spec is approaching settled shape.

**Success criteria:**
- Every scrutiny finding verified against file:line or code evidence before lock-in
- User /copy lock-ins executed in one coherent commit per round
- Spec line count tracked per round as "shape stability" signal
- Round 10 produces only mechanical propagation issues (per user's round-9 guideline)

**Connection to project arc:** Fifth consecutive session on this spec. Pattern established: each round surfaces fewer architectural issues and more prose drift. Round 9 was the last round to add new data-model surface (interrupt_error field); round 10 was pure propagation.

## Session Narrative

Session began at HEAD `1f2f1f72` after resuming from prior handoff. Previous session ended mid-round-7 scrutiny; the compacted summary indicated round-7 lock-ins for F1-F5 were in flight but not yet committed.

**Round 7 completion (commit `873d8470`).** Landed 5 findings from round 7: F1 dispatch_result admission (override to remove parameter entirely), F2 aborted state in registry, F3 helper-signature kwargs removal, F4 dispatch_error=None explicit, F5 poll-abort observation sequence. User had locked in "Option B" (remove parameter entirely) which was stricter than my recommendation — their rationale: "Python's type annotation is not a runtime authority boundary. Removing the parameter makes the failure state unrepresentable through that mutator." Key reasoning captured: structural impossibility (can't call the success method with a failure argument) is stronger than a type annotation that evaporates at runtime.

**Round 8 scrutiny (delivered via /copy).** 5 findings, Minor revision: H1 timer None-guard missing at 4 sites (I initially identified 3, user flagged the 4th at spec:823), H2 `signal_internal_abort` docstring listed `unknown` as a state (unknown is a job status, not a registry state), H3 observation sequence structure asymmetry, H4 rejection-literal overgeneralization, H5 replay bullet enumeration. User also introduced an "additional finding" cleanup: 4 sites still claimed `decide()` projects into `PendingEscalationView` even though Packet 1's new 3-field `DelegationDecisionResult` removed that behavior. This cross-section drift survived rounds 3-7 because each round focused on a specific slice; the additional-finding pattern became a meta-lesson about structured scrutiny limits. Committed as `5e041f90`.

**Round 9 scrutiny (delivered via /copy) — Major revision.** This was the most substantive round. 5 findings: F1 helper ownership drift (projection helper was signaling abort as side effect while callsites also signaled — dual-signal-dual-reason trap), F2 `interrupt_turn` transport failure unhandled on non-cancel timeout path, F3 `decision=None` taxonomy stale, F4 rejection-reason table too narrow, F5 worker-death diagram wrong decide-order. F1 and F2 were genuine architectural issues; F3-F5 were mechanical.

The Round-9 architectural work produced three new permanent features in the spec:
1. `_project_pending_escalation` is now **pure** — raises instead of catching internally; each callsite owns its own reason.
2. New nullable field `PendingServerRequest.interrupt_error` — forensic annotation for `session.interrupt_turn()` transport failure on the non-cancel timeout path.
3. Symmetric forensic treatment: respond() → dispatch_error, interrupt_turn() → interrupt_error, abort signal → internal_abort_reason.

Key decision at round 9: user chose to keep start()'s Parked-arm reason **broad** (`parked_projection_invariant_violation`) regardless of proximate cause. Rationale: "once Parked fired, any unconstructible view is a Parked/projection invariant mismatch, regardless of whether the proximate cause is missing request, resolved tombstone, or unexpected kind." This collapses both None-return and UnknownKindInEscalationProjection into one semantic at start(). poll() keeps distinct handling (None = no-op, exception = abort signal) because poll() has only one reason to use.

User also added a cross-round guardrail during round-9 lock-in: "With F2-A, add `interrupt_error` to the replay bullet and tests in the same sweep. Otherwise the data-model table will be correct but replay/test strategy will drift immediately." I executed the sweep across 8 sites: field table, orthogonality paragraph, record_timeout signature + docstring, non-cancel timeout pseudocode, unknown-kind path explicit asymmetry note, sanitization rules, replay bullet, two tests. Committed as `4211c408`. Net +41 lines — the largest single-round delta of the cycle.

**Round 10 scrutiny (delivered via /copy) — Minor revision.** User explicitly framed the scope: "Use this focus order: 1. interrupt_error completeness 2. Non-cancel timeout ordering 3. Helper purity 4. None vs exception semantics 5. Public/private contract boundary 6. Stale taxonomy 7. Tests as executable spec." I ran a targeted sweep matched to each focus area.

5 findings emerged: R10-1 three-mutator orthogonality paragraph kept "respectively" 1:1 mapping that became stale when record_timeout gained the interrupt_error sub-axis; R10-3 intent-durability-under-failure treatment only discussed dispatch_result, missing the symmetric crash-loss case for timed_out/interrupt_error; R10-5 poll()'s try/except wrapper was prose-only while start()'s was full pseudocode (asymmetric implementer guidance); R10 None-path at poll() was implicit (could be misread as signaling for both None and exception); R10-6 validator-relaxation setup sentence said only "timeout" even though the scope paragraph a few lines below correctly listed both timeout and internal-abort wakes.

One finding I raised was a false alarm — R10-4 about exception-clause inconsistency between `except Exception` and `except RuntimeError` — I re-verified and confirmed both paths actually use `except Exception`. Dropped it before presenting options to user.

User locked in all 5 findings, treating R10-5 as required (not optional as I had offered). Their rationale: "The spec has repeatedly shown that executable-looking pseudocode governs implementer behavior more strongly than prose." Committed as `fa4955b4`. Net +30 lines.

**Session ends.** User invoked `/handoff:save` with args "I will review the spec and then start the next session by sharing my findings" — signaling that they want to personally review the spec rather than continuing immediately to `superpowers:writing-plans` decomposition. This is a deliberate slow-down before plan handoff.

## Decisions

### F1 Option A — Make projection helper pure

**Choice:** `_project_pending_escalation` re-raises `UnknownKindInEscalationProjection` instead of catching-and-signaling internally. Each callsite owns its own catch + signal_abort + reason.

**Driver:** User's round-9 scrutiny identified the helper as having callsite-specific side effects while being shared by both `poll()` and `start()`. Quote: "start() projection failure caused by unknown-kind drift will first emit the poll-path abort reason, then start() will emit the parked-projection reason. The durable internal_abort_reason can disagree with the DelegationStartError.reason."

**Rejected alternatives:**
- **Option B (parameterize with `callsite_reason: str`):** rejected because single helper name with two behaviors via parameter is still a leaky abstraction. Reason should be callsite-local, not helper-parametric.
- **Option C (document-only):** rejected because prose alone doesn't prevent the helper from being called from start() — pseudocode is what implementers copy.
- **Option D (dedicated `_project_pending_escalation_pure` alongside existing):** rejected because two helper names with overlapping responsibility is worse than one helper with single responsibility.

**Trade-offs accepted:** Every projection callsite now needs its own try/except block — shifts complexity from producer to consumer. For two callsites this is acceptable; at scale the pattern might invert. User accepted this cost implicitly.

**Implications:** `_project_pending_escalation` docstring now includes "PURE — no side effects." The helper is safely callable from any future projection callsite (e.g., amendment-admission in Packet 2) without inheriting a pre-committed reason.

**Confidence:** High (E2) — verified by grep that helper body has no signal_internal_abort calls after F1 edit; pseudocode for both start() (full) and poll() (round-10 added) show symmetric wrapper pattern.

**Reversibility:** High — could re-absorb the catch into helper if future callsites share the same reason.

**What would change this decision:** 3+ projection callsites all using the same reason would justify re-absorbing.

### F2 Option A — Add `interrupt_error` forensic field

**Choice:** New nullable string field `PendingServerRequest.interrupt_error`, set by worker on non-cancel timeout path when `session.interrupt_turn()` raises. Threaded through `record_timeout` signature, replay bullet, sanitization rules, orthogonality paragraph, tests.

**Driver:** User's round-9 scrutiny: "leaves a transport failure path without the forensic persistence discipline the spec claims to enforce." The spec already treats `session.respond()` failures as auditable (dispatch_error + dispatch_result="failed"); `session.interrupt_turn()` was the remaining transport surface without a forensic annotation.

**Rejected alternatives:**
- **Option B (best-effort, no field):** rejected because "tried to interrupt, transport failed" is not observable without a durable annotation. Loses information.
- **Option C (propagate, let worker-death catch):** rejected because it silently loses `timed_out=True` forensic record, regressing round-9's OB-1 intent.

**Trade-offs accepted:** New data-model field (but nullable with safe default — no migration). New forensic axis that an implementer could misread as a peer primary axis. Mitigated by anchoring interrupt_error explicitly as a sub-axis of timed_out in spec:1140 (round 10) and spec:992 orthogonality paragraph.

**Implications:** The spec is now internally symmetric across all three transport surfaces:

| Surface | Forensic field | Terminal condition |
|---|---|---|
| `session.respond()` | `dispatch_error` | `dispatch_result="failed"` + `status="canceled"` |
| `session.interrupt_turn()` | `interrupt_error` | `timed_out=True` + `status="canceled"` |
| Plugin-invariant violation | `internal_abort_reason` | `status="canceled"` (decision axes all None) |

**Confidence:** High (E2) — verified by grep of `interrupt_error` across 12 distinct spec sites; all sibling sites for `dispatch_error` now have parallel treatment. Round-10 R10-1 and R10-3 edits close remaining drift.

**Reversibility:** Medium — field is nullable, so removal is backward-compatible, but replay code and tests would need to be rolled back. Call it Medium-High.

**What would change this decision:** If `session.interrupt_turn` transport failures prove so rare in production that a log warning suffices for forensic needs.

### Broad reason at start() Parked arm

**Choice:** start()'s catch of `UnknownKindInEscalationProjection` collapses both raised-exception and null-return into one signaling reason: `parked_projection_invariant_violation`.

**Driver:** User's round-9 lock-in: "My preference is to keep the start() reason broad: once Parked fired, any unconstructible view is a Parked/projection invariant mismatch, regardless of whether the proximate cause is missing request, resolved tombstone, or unexpected kind."

**Rejected alternatives:**
- **New reason `unknown_kind_in_parked_projection`:** rejected — adds vocabulary without changing caller-facing behavior.
- **Forward the helper's reason `unknown_kind_in_escalation_projection`:** rejected — would produce mismatch between start()'s raised reason and the durable internal_abort_reason.

**Trade-offs accepted:** Loses the ability to distinguish "parked but tombstone cleared" vs "parked but unknown kind" in the durable forensic record. User accepted because start()'s caller-facing contract doesn't need that granularity.

**Implications:** start() always signals `parked_projection_invariant_violation` at the F1 catch point. Tests at spec:1719 assert this across both sub-cases (null-return + raised-exception) — the round-9 test rewrite made this explicit.

**Confidence:** High (E2) — verified by grep that start() Parked arm has exactly one reason string after F1 edit.

**Reversibility:** High — could differentiate reasons later if forensic queries need the proximate-cause discriminator.

**What would change this decision:** Audit queries needing to distinguish the three null-projection causes. Currently no such query exists.

### R10-5 required (not optional)

**Choice:** Poll()'s try/except wrapper added as full pseudocode block, not prose-only, in round-10 commit.

**Driver:** I initially offered R10-5 as optional, then offered the same two framings to user. User overruled: "Required, not optional. The spec has repeatedly shown that executable-looking pseudocode governs implementer behavior more strongly than prose. Since start() now has explicit catch pseudocode, poll() should too."

**Rejected alternatives:**
- **Prose-only description** (my initial offer): rejected because asymmetric with start()'s full pseudocode, inviting implementer drift.

**Trade-offs accepted:** +18 lines in round 10; some duplication with start()'s pseudocode.

**Implications:** poll() and start() now have matched treatment. An implementer reading either callsite sees the same wrapper structure. This feeds forward to writing-plans decomposition — the "projection helper rewrite" phase can point at both pseudocode blocks for the wrapper pattern.

**Confidence:** High (E2) — pseudocode verified present at spec:1399 by grep.

**Reversibility:** High — could trim to prose-only if spec becomes too long.

**What would change this decision:** Spec total line count growing unmanageable (currently 1894).

### Whole-document pass deferred to user review

**Choice:** Instead of running the whole-document pass myself, defer to user's personal spec review.

**Driver:** User's explicit direction via `/save` command args: "I will review the spec and then start the next session by sharing my findings."

**Rejected alternatives:**
- **Run whole-document pass now as Round 11:** offered but user chose differently. My offer text: "Shall I run that now? If yes, I'd structure it as a single sweep producing a Round-11 scrutiny doc..." User responded by calling `/save`, effectively declining.
- **Proceed directly to writing-plans:** not offered by user; implicit rejection.

**Trade-offs accepted:** Risk that user's review surfaces issues I would have caught (and vice versa). Benefit: user brings fresh eyes after four rounds of my review, reducing echo-chamber effect.

**Implications:** Next session starts with user-driven findings rather than my automated sweep. Tone may shift from "lock-in/execute" toward "evaluate my findings, decide which to act on."

**Confidence:** Medium (E1) — single-session observation of user's preference for personal review at this stage.

**Reversibility:** High — user can always delegate review if they change their mind.

**What would change this decision:** User sharing findings and explicitly requesting I run a parallel automated sweep.

## Changes

### Commit `873d8470` — Round 7 normalization (pre-compact)

**Purpose:** Land round-7 findings F1-F5 + prose cleanups from round-6 scrutiny.

**Key points (reconstructed from compacted summary):**
- F1: removed `dispatch_result` parameter from `record_response_dispatch` signature entirely (user chose stricter Option B over my Option A)
- F2: added `aborted` canonical state to registry state machine + ASCII diagram
- F3: dropped `reason=`/`cause=` kwargs from 3 `_mark_execution_unknown_and_cleanup` callsites
- F4: explicit `dispatch_error=None` in non-cancel timeout's `record_timeout` call
- F5: observation-sequence prose split on `signal_internal_abort` CAS outcome
- F2 stale-timer contract paragraph added at spec:825

**Net:** +78 / -28 lines.

### Commit `5e041f90` — Round 8 normalization

**Purpose:** Land 5 round-8 findings + cross-round "additional finding" cleanup of stale decide()-projection claims.

**Files:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`

**Approach:** Six sites touched:
- H1 (spec:167, 738, 805, 832): `token is None` early-return guard at 4 timer sites
- H2 (spec:357-362): signal_internal_abort docstring — `aborted` and `missing/no entry` rows, removed spurious `unknown` state reference
- H3 (spec:1355-1367): two parallel CAS-branch numbered sequences instead of "numbered + caveat"
- H4 (spec:1369-1372): split rejection-literal paragraph — `request_already_decided` (live registry) vs `job_not_awaiting_decision` (post-terminal)
- H5 (spec:1128): explicit replay field enumeration
- AF (spec:352, 998, 1307, 1739): removed stale decide()-projects claims

**Net:** +38 / -21 lines. Spec line count 1806 → 1823.

### Commit `4211c408` — Round 9 major revision

**Purpose:** Land 5 round-9 findings — F1/F2 architectural, F3/F4/F5 mechanical.

**Files:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`

**Key implementation details:**
- **F1 (helper purity, 7 sites):** helper body (spec:1415-1437 area), poll() callsite description, start() Parked arm pseudocode (spec:525-546), observation-sequence sentence, §Projection helper rewrites prose, §start() decision table Parked row, F1 + projection-abort tests
- **F2 (interrupt_error, 8 sites):** field table (spec:985), orthogonality paragraph (spec:992), `record_timeout` signature (spec:1082), signature docstring (spec:1087-1097), non-cancel timeout pseudocode (spec:828-849), sanitization rules (spec:1545), replay bullet (spec:1171), unknown-kind asymmetry note (spec:475), 2 tests
- **F3 (taxonomy, 3 sites):** IO-3 bullet (spec:48), thread-role table worker row (spec:112), validator prose (spec:1596 area)
- **F4 (rejection table, 1 site):** predicate row (spec:1261)
- **F5 (worker-death diagram, 1 site):** status-guard-first reorder (spec:912-920)

**Design choice:** F2 adds `interrupt_error` as a nullable field with safe default None — no migration needed. Anchored explicitly as sub-axis of `timed_out` (not peer axis) in orthogonality paragraph.

**Net:** +82 / -41 lines. Spec line count 1823 → 1864.

### Commit `fa4955b4` — Round 10 normalization

**Purpose:** Land 5 round-10 findings — all prose/pseudocode propagation of round-9's new field and helper purity.

**Files:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`

**Key implementation details:**
- **R10-1 (mutator-orthogonality, spec:1140):** dropped "respectively" 1:1 mapping; anchor-axis framing + interrupt_error sub-axis note
- **R10-3 (intent durability, spec:867):** new "Intent durability under failure (timeout path)" paragraph parallel to the dispatch-failure statement at spec:921. Documents symmetric crash-loss window — worker crash between `approval_resolution.dispatched` and `record_timeout` loses both `timed_out=True` and `interrupt_error`; acceptable only as subset of worker-death recovery boundary. Includes forward-compat note (future packet could add `record_interrupt_error` to tighten).
- **R10-5 (poll pseudocode, spec:1399):** full poll() projection-handling pseudocode block matching start()'s F1 pattern
- **R10 None-path (spec:1396):** explicit sentence clarifying None-returns do NOT signal; only caught exception signals
- **R10-6 (validator setup, spec:1613):** broadened from "timeout" to "two non-operator wake paths — timeout wake and internal-abort wake"

**Net:** +33 / -3 lines. Spec line count 1864 → 1894.

## Codebase Knowledge

### Spec anatomy (1894 lines total)

| Section | Rough span | Post-Round-10 notes |
|---------|-----------|---------------------|
| IO-1 through IO-5 invariants | ~spec:30-60 | IO-3 now mentions abort-wake alongside timeout-wake |
| Thread roles and ownership | spec:107-114 | Worker row lists both non-operator wake paths |
| Resolution registry | spec:118-200 | States: `awaiting \| reserved \| consuming \| aborted` |
| Transactional registry protocol | spec:280-350 | Two-phase reserve → commit_signal |
| Internal abort coordination | spec:343-408 | Worker-coordinated via signal_internal_abort |
| start() semantics | spec:500-620 | Parked arm wraps projection call (F1 Option A) |
| Unknown-kind contract | spec:455-480 | Explicit asymmetry note with timeout path (F2) |
| Timeout paths (cancel + non-cancel) | spec:720-870 | Non-cancel now wraps interrupt_turn (F2) + intent-durability paragraph (R10-3) |
| Dispatch failure path | spec:870-925 | respond() raises → record_dispatch_failure |
| PendingServerRequest fields | spec:940-995 | Added interrupt_error; orthogonality paragraph updated |
| Store mutators | spec:1039-1141 | record_timeout accepts interrupt_error kwarg |
| Replay logic | spec:1166-1180 | record_timeout replay includes interrupt_error |
| DelegationDecisionResult | spec:1185-1205 | New 3-field shape: decision_accepted, job_id, request_id |
| Rejection reasons table | spec:1258-1265 | Predicate row for `job.status != "needs_escalation"` |
| Projection helper rewrites | spec:1305-1437 | Helper is now pure (F1) |
| Observation sequences | spec:1396-1430 | Two parallel CAS-branch sequences |
| Observability | spec:1505-1555 | 3 forensic string fields with sanitization |
| Journal validator relaxation | spec:1610-1645 | Both non-operator wake paths covered (R10-6) |
| Tests to add | spec:920-930, 1700-1760 | F1 projection test + F2 interrupt-failure test |
| Migration | spec:1790-1810 | All new fields nullable with safe defaults |

### Key cross-section invariants

- **Three transport surfaces, three forensic fields:** respond → dispatch_error; interrupt_turn → interrupt_error; abort signal → internal_abort_reason. All three are sanitized + bounded (256 chars, class-name prefix).
- **`decision=None` on two wake paths:** timeout-wake and internal-abort-wake both write `approval_resolution.intent/dispatched` with `decision=None`. Validator relaxation at spec:1613+ covers both.
- **Helper purity pattern:** `_project_pending_escalation` returns None for legitimate no-view states (terminal job, unparked, tombstone) and re-raises `UnknownKindInEscalationProjection` for invariant violations. Each callsite owns the catch + signal + reason.
- **interrupt_error orthogonality:** Sub-axis of `timed_out` axis, NOT a peer primary axis. Always paired with `timed_out=True`, never set alongside `dispatch_error` (different transport surfaces).

### Referenced controller code

Spec references this code (not modified by spec — spec is design doc):

| Concept | Controller location | Purpose |
|---------|--------------------|---------| 
| Job status guard | `delegation_controller.py:1577` | Rejects `decide()` when job.status != "needs_escalation" before registry lookup |
| Existing auth/audit guards | `:1620-1649`, `:1666-1692` | Validation and journal writes that `decide()` pseudocode preserves |
| `_mark_execution_unknown_and_cleanup` | `:759-766` | Worker-owned cleanup; takes `(*, job_id, collaboration_id, runtime_id, entry)` — no reason/cause kwargs |
| `_project_pending_escalation` existing | `:849-868` | Current impl; spec's §Projection helper rewrites replaces it |
| Transport failure point | `jsonrpc_client.py:75-103` | BrokenPipeError→RuntimeError, JsonRpcError, RuntimeError for malformed response |
| `session.interrupt_turn` | `runtime.py:185-192` | Delegates to `JsonRpcClient.request("turn/interrupt", ...)` |

### Pseudocode symmetry after round 10

Both start() and poll() callsites now have explicit try/except pseudocode matching the pattern:

```python
try:
    escalation_view = self._project_pending_escalation(job)
except UnknownKindInEscalationProjection as exc:
    # callsite-specific logging + signal_internal_abort + reason
    ...
    escalation_view = None
# escalation_view is None from both paths (no-view legitimate + caught exception)
```

start() collapses both paths to `parked_projection_invariant_violation`; poll() uses `unknown_kind_in_escalation_projection` only for the exception path (None pass-through is no-op).

## Context

### Workflow pattern observed this session

Each round followed this cadence:

1. User delivers scrutiny via `/copy` (tool command that copies the user's pre-drafted scrutiny content).
2. I verify each finding against file:line evidence in the spec and (when relevant) controller/runtime code.
3. I present options per finding (A vs B framings) where real choice exists; recommend one with reasoning.
4. User locks in via `/copy` (table of findings with decisions, sometimes with refinements or overrides).
5. I create TaskCreate items for each lock-in.
6. I execute edits in one coherent commit, sometimes batching related sub-edits.
7. I run verification sweep (git diff stat + grep for stale phrases + wc -l).
8. I commit with structured multi-finding body referencing round number and T-ticket.

Global CLAUDE.md auto-commit rule applies — completed chunks commit without asking. User confirmed this workflow by not overriding it across 4 commits.

### Spec shape-stability trajectory

| Round | Net delta | Interpretation |
|-------|-----------|----------------|
| 1-6 | ~±10 each | Prose tightening |
| 7 | +50 | New features: aborted state, internal-abort primitive |
| 8 | +17 | Diagram guards + cross-round drift cleanup |
| 9 | +41 | New field (interrupt_error) + helper refactor — biggest delta |
| 10 | +30 | Prose propagation of round-9 additions |

**User's rule:** if a round finds only mechanical propagation issues, fix them and then do one whole-document pass. Round 10 qualified for this threshold. The whole-document pass is now deferred to user's personal review.

### Related prior decisions (referenced by spec)

- OB-1 observation honesty (transport failure → `unknown`, not `failed`) — documented in §Observability.
- IO-1 session ownership (worker owns session; main does not touch it) — keeps cleanup worker-coordinated.
- IO-3 single-writer-per-store (enforced by singleton busy gate at `:328-349`).
- EscalatableRequestKind literal narrowing (3 of 4 PendingRequestKind literals) — excludes `"unknown"` from projection surface.

### Mental model for the work

**Framing:** This is a concurrency-semantics spec more than a feature spec. The architectural primitives (worker thread + transactional registry + internal-abort coordination) are what matter. The individual pseudocode flows are just instantiations of those primitives.

**Core insight from round 9:** Making failure states **structurally impossible** beats documenting them. F1 Option A removed signaling from the helper; F2 Option A removed the "interrupt failure loses timed_out" window. Both are structural corrections, not documentation fixes.

**Mental model:** Think of the spec as defining three **orthogonal transport surfaces** (respond, interrupt_turn, abort signal), each with a forensic field and a terminal condition. The surfaces cannot compose (you either respond or interrupt, not both), but the spec's role is to prove they are orthogonal — no audit query can conflate them.

## Learnings

### Structured-scrutiny cycle has emergent phases

Five rounds in this session (7-10 + partial earlier) showed a repeating pattern: each round's findings are classified into architectural (new field, new method, new semantic) vs mechanical (prose drift, stale counts, pseudocode/prose disagreement). The ratio shifts from round to round — round 7 was mixed, round 9 was mostly architectural, round 10 was purely mechanical. Rounds producing only mechanical issues are a signal the spec is converging.

### Cross-section drift survives section-local scrutiny

Round 8's "additional finding" was 4 sites claiming decide() projects — this claim was stale since round 3 but survived rounds 3-7 because each round focused on a specific slice of the spec. The lesson: structured-scrutiny with narrow per-round focus is efficient but incomplete; whole-document passes catch a different class of drift.

### "Respectively" is a staleness smell

R10-1 flagged a "respectively" 1:1 mapping (three mutators to three axes) that became stale when record_timeout gained a second output field. Whenever prose uses "respectively" across a list, that list implies completeness — which will be wrong as soon as any item gains an additional output. Treat "respectively" as a future-breakage marker.

### Broad reasons beat narrow reasons when semantic collapses

Round 9's broad-reason decision at start() Parked arm (collapse null-return + UnknownKindInEscalationProjection into one reason) proved cleaner than the alternative of two reasons. The rule: when two proximate causes lead to the same caller-visible outcome AND the durable discriminator is already captured elsewhere (internal_abort_reason field), one broad reason is better than two narrow ones.

### Pseudocode carries more implementer weight than prose

User's round-10 override (R10-5 required, not optional) was based on the observation that "The spec has repeatedly shown that executable-looking pseudocode governs implementer behavior more strongly than prose." Prose descriptions get paraphrased by implementers; pseudocode gets copied. For parallel callsites, both should have pseudocode OR both should have prose — never mixed.

### Forensic field orthogonality requires explicit framing

F2's interrupt_error field could have been framed as a peer axis alongside dispatch_error, timed_out, internal_abort_reason. Instead it was framed as a sub-axis of timed_out. This prevented an implementer from writing an audit query like "WHERE interrupt_error IS NOT NULL" that crosses transport surfaces. The R10-1 edit made this framing explicit in the three-mutator paragraph.

### Helper purity is a localization move

F1 Option A's consequence: every callsite's reason is localized to that callsite. This makes the helper callable from any future packet without the reason leaking through. The trade-off is that a generic pure helper is less "convenient" than a helper that absorbs ceremony — but convenience at the cost of reason-locality is a bad deal for a spec that will be extended.

## Next Steps

### 1. User reviews spec at HEAD `fa4955b4`

**Trigger:** User's explicit direction via /save args: "I will review the spec and then start the next session by sharing my findings."

**What to expect:** Next session likely opens with user-presented findings (their format, not /copy-scrutiny format). Could range from zero findings (spec approved) to another substantive round.

**Immediate response pattern:** Listen for framing first — "these are issues" vs "these are questions" vs "these are things to consider." User may have a different scrutiny register than /copy rounds.

### 2. Execute any round-11 findings (if surfaced)

**Dependencies:** Step 1 outcome.

**What to read first:** Current spec state at HEAD `fa4955b4` — specifically the round-9 additions (interrupt_error field propagation at spec:475, 828-849, 985, 992, 1082-1097, 1171, 1545, 1754-1755) and round-10 paragraphs (spec:867 intent durability, spec:1140 mutator orthogonality, spec:1396-1420 poll pseudocode).

**Approach suggestion:** Same workflow as rounds 7-10 — verify → options → lock-in → one commit. If user's findings are themselves minor-revision class, a single commit finishes the cycle.

**Acceptance criteria:** Spec passes user's review with verdict at or below Minor revision, no new fields/methods/public-contract shapes.

### 3. If spec approved: invoke `superpowers:writing-plans`

**Dependencies:** Steps 1-2 complete with user approval.

**What to read first:** Ticket `T-20260423-02` for acceptance criteria, then the spec in full. The spec is large (~1900 lines) — writing-plans decomposition may benefit from chapter-by-chapter approach.

**Approach suggestion:** Candidate phase clustering based on dependency order:
- Phase 1 (foundation): ResolutionRegistry + aborted state + Resolution sum type + new PendingServerRequest fields including interrupt_error
- Phase 2 (worker sequence): non-cancel timeout path wrapper, dispatch-failure path, internal-abort wake sequence
- Phase 3 (main-thread paths): decide() rewrite to use registry protocol, start() Parked arm with projection helper catch
- Phase 4 (contract surface): DelegationDecisionResult 3-field rewrite, contracts.md updates, public tests

**Acceptance criteria:** Writing-plans produces discrete implementable phases with explicit acceptance criteria per phase.

### 4. Backup: whole-document pass if user's review finds cross-section drift

**Dependencies:** Only if Step 1 surfaces issues I haven't caught.

**Approach suggestion:** I'd run the pass in the same focus-area format as round 10 (stale counts, stale "only" claims, stale parenthetical completeness lists, pseudocode/prose disagreement). Structure as Round-11 with verdict.

## In Progress

**State:** Clean stopping point — four commits landed, working tree clean at `fa4955b4`.

**Deferred to user:** Personal spec review + whole-document drift-check.

**No work in flight.** The /save was invoked at a natural cycle boundary (end of round 10, before user's personal review).

## Open Questions

1. **Will user's review surface any architectural issues?** Rounds 1-6 averaged ~3-5 findings; rounds 7-10 the same. If user's review surfaces 0-2 mechanical findings, spec is ready for writing-plans. If 3+ findings or any architectural issue, another cycle needed.

2. **How to decompose the spec for writing-plans?** 1894 lines is large for a single writing-plans invocation. Candidate: chapter-by-chapter per the "Spec anatomy" table above, with each chapter producing a phase. But writing-plans may have its own chunking logic worth trusting.

3. **Packet 2 scope still open.** Packet 2 was mentioned in earlier rounds as "amendment admission" — not yet ticketed or scoped. Blocks T-20260423-01 AC1 alongside Packet 1.

4. **Will F1 Option A cause friction for a future third projection callsite?** The pattern is clean for 2 callsites. Once a third exists (e.g., amendment-admission view from Packet 2), each will need its own try/except. If all three end up with the same reason, the pattern might invert.

## Risks

- **Scope creep from user review.** User's personal pass may surface issues I rationalized away (e.g., R10-4 false alarm). Spec growth past 2000 lines would be a signal to consider splitting into Packet-1a and Packet-1b.
- **Writing-plans output fidelity.** Large specs can produce flat plans that miss the spec's architectural hierarchy. Watch for phases that skip the coordination-primitive layer (registry, internal-abort signal) in favor of diving into pseudocode flows.
- **Session context usage.** This session reached ~26% of 1M context (per system telemetry). Future sessions resuming from this handoff start with just the handoff (much smaller). Context budget is fine for several more rounds.

## References

| Resource | Location |
|----------|----------|
| Spec (current HEAD) | `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` @ `fa4955b4` |
| Ticket | `docs/tickets/T-20260423-02-*.md` (Packet 1 deferred same-turn approval response) |
| Parent ticket | `T-20260423-01` AC1 (blocked by Packets 1 + 2) |
| Prior handoff (this session's `resumed_from`) | `docs/handoffs/archive/2026-04-23_22-04_deferred-approval-spec-round-2-scrutiny-revised.md` |
| Controller code | `packages/plugins/codex-collaboration/server/delegation_controller.py` (esp. :759-766, :1577, :849-868) |
| Runtime session API | `packages/plugins/codex-collaboration/server/runtime.py:185-192` (interrupt_turn) |
| JSON-RPC client | `packages/plugins/codex-collaboration/server/jsonrpc_client.py:61-104` (request) and :106+ (respond) |
| Commits this session (4 total) | `873d8470` (R7), `5e041f90` (R8), `4211c408` (R9), `fa4955b4` (R10) |

## Gotchas

- **R10-4 false alarm:** I drafted a finding about `except Exception` vs `except RuntimeError` inconsistency, then re-verified and found both paths actually use `except Exception`. Dropped before presenting. Lesson: always re-verify exception-clause claims against the actual pseudocode, not against memory of earlier rounds.
- **Cross-round drift like round-8's AF:** stale claims can survive many rounds if no round's focus touches them. Whenever a round adds a new shape (like round-9's interrupt_error field), search for sibling references to the pre-new-shape concept (like dispatch_error references) and check they're updated in parallel.
- **User's `/copy` content is pre-drafted:** the user runs `/copy` to paste scrutiny content they've drafted offline. Don't assume they're transcribing live — the scrutiny document is a complete artifact, and missing structure (e.g., no "Verdict" section) is meaningful, not an oversight.
- **Auto-commit per global CLAUDE.md:** completed chunks commit without asking. User confirmed this workflow across 4 commits by not overriding. Do not pause to ask "commit now?" for coherent work chunks.
- **State file path convention:** State file at `docs/handoffs/.session-state/handoff-<session_id>` contains the archive path of the handoff being resumed, relative to project root (not absolute). Read it for the `resumed_from` frontmatter value.

## Conversation Highlights

**F1 Option A rationale (round-9 lock-in):**
User: "F1: take Option A, but I would make the callsite behavior explicit: `_project_pending_escalation(job)` may return `None` for legitimate no-view states and may raise `UnknownKindInEscalationProjection`; it must not signal. `poll()` catches `UnknownKindInEscalationProjection` and signals `unknown_kind_in_escalation_projection`. `start()` catches it and should still treat it as `parked_projection_invariant_violation` unless you want a new, more specific start error reason."
— Drove the broad-reason decision at start().

**Broad reason at start() — explicit rationale:**
User: "My preference is to keep the `start()` reason broad: once Parked fired, any unconstructible view is a Parked/projection invariant mismatch, regardless of whether the proximate cause is missing request, resolved tombstone, or unexpected kind."
— Key semantic collapse justification.

**F2 guardrail (round-9 lock-in):**
User: "One extra guardrail for the edit: with F2-A, add `interrupt_error` to the replay bullet and tests in the same sweep. Otherwise the data-model table will be correct but replay/test strategy will drift immediately."
— Expanded F2 scope from 4 sites to 8 sites.

**R10-5 override (round-10 lock-in):**
User: "R10-5: Required, not optional. The spec has repeatedly shown that executable-looking pseudocode governs implementer behavior more strongly than prose. Since `start()` now has explicit catch pseudocode, `poll()` should too."
— Promoted pseudocode over prose as governance mechanism.

**Round-10 focus order:**
User: "Use this focus order: 1. `interrupt_error` completeness 2. Non-cancel timeout ordering 3. Helper purity 4. `None` vs exception semantics 5. Public/private contract boundary 6. Stale taxonomy 7. Tests as executable spec."
— User specified exact sweep scope rather than leaving it to my judgment. Implies future spec-review sessions may also have user-specified scope.

**User framing round 10 stopping condition:**
User: "If Round 10 finds only mechanical propagation issues, fix them and then do one final whole-document pass. If it finds another new field, new mutator, or new public-contract shape, treat the spec as still moving and hold off on implementation planning."
— Explicit threshold for when spec is "done enough" to hand to writing-plans.

**Save-time direction:**
User: "I will review the spec and then start the next session by sharing my findings."
— Deferred the whole-document pass from me to themselves. Slows the transition to implementation planning but brings fresh review.

## User Preferences

**Scrutiny-driven workflow:** User prefers `/copy`-delivered structured scrutiny over free-form "can you check X?" questions. Structured format: Premise Check → Critical Failures → High-Risk Assumptions → Real-World Breakpoints → Hidden Dependencies → Adversarial Perspectives → Required Changes → Verdict.

**Lock-in via `/copy` table:** Decisions are locked by user in tabular format:
> | Finding | Decision |
> | --- | --- |
> | F1 | Option A |
> ...
Sometimes with refinements: "F1: take Option A, but I would make the callsite behavior explicit..."

**Willingness to override recommendations:** User will override my recommendations with reasoning. Quote patterns: "Required, not optional" (R10-5); "I would make it even sharper" (round-7 F1 Option B over Option A). Never corrects silently — always states what and why.

**Auto-commit without asking:** Per global CLAUDE.md rule, completed chunks commit without confirmation. User confirmed by not overriding across 4 commits this session.

**Prefer one-commit-per-round:** User explicitly expects all round findings to land in one coherent commit, not split across multiple commits. Verified by commit structure across rounds 7-10.

**Prefer structural fixes over documentation fixes:** User's round-7 F1 override (remove parameter entirely, not just narrow its type) and round-9 F2 Option A (add interrupt_error field, not just document the loss) both chose structural impossibility over documented expectation.

**Spec-shape stability as cycle-termination signal:** User watches line delta per round. When deltas are small + purely propagation, willing to move toward writing-plans. When deltas are large or structural, keeps iterating.

**Personal review before hand-off to writing-plans:** User wants to personally read the spec after long scrutiny cycles rather than delegating the whole-document pass. Verified by /save args at end of this session.

**Terse, actionable communication style:** User's /copy-delivered scrutiny is dense and dense-packed; doesn't include niceties or hedge language. Responses should match register — terse verdict-driven summaries, explicit options, no performative agreement.

## Rejected Approaches

### F1 Option C (document-only) — rejected in round 9

**Approach:** Add a prose note at spec:1393 and spec:517 saying "start() MUST NOT call `_project_pending_escalation`; use `_project_request_to_view` directly." Smallest possible intervention.

**Why it seemed promising:** Minimal surface-area change. No refactoring. No new pseudocode to maintain.

**Specific failure (anticipated):** Prose alone doesn't prevent the helper from being called from start() in the future. The helper's name doesn't warn about the side effect. An implementer adding a third projection callsite (in Packet 2) would re-introduce the bug.

**What it taught:** Helper contracts should be enforced at the name/body level, not at the callsite-documentation level. The "helper purity" pattern from F1 Option A is a durable structural fix; Option C would rot as soon as the spec expanded.

### F2 Option C (propagate-and-let-worker-death-catch) — rejected in round 9

**Approach:** Don't wrap interrupt_turn in try/except. Let exceptions propagate to the outer worker-exception handler, which calls `_mark_execution_unknown_and_cleanup`. The job terminalizes as `unknown`.

**Why it seemed promising:** No new data-model field needed. Consistent with existing worker-death handling. Simplest pseudocode.

**Specific failure:** Silently loses `timed_out=True` forensic record. Regresses round-9's explicit OB-1 intent ("no transport failure is invisible"). Future auditors can't distinguish "crashed before interrupt" from "interrupt transport failed." The whole Packet 1 value prop of making failure paths observable collapses.

**What it taught:** Forensic persistence is a load-bearing feature, not a nice-to-have. When the spec claims a property ("no transport failure is invisible"), every transport surface must uphold that property or the spec's coherence breaks.

### R10-4 (exception-clause inconsistency) — dropped by me as false alarm

**Approach:** I drafted a round-10 finding about `except Exception` vs `except RuntimeError` inconsistency between non-cancel timeout path and dispatch-failure path.

**Why it seemed promising:** Initial grep suggested the two paths used different catch clauses. Would be a mechanical consistency fix.

**Specific failure:** Re-verification by direct read at spec:878 showed the dispatch-failure path actually uses `except Exception as exc:`, not `except RuntimeError`. I had misread. Dropped before presenting to user.

**What it taught:** Always verify exception-clause claims by direct Read of the pseudocode block, not grep. Grep can miss context — the clause type may be 5-10 lines away from the nearest identifier I'm searching. Evidence integrity matters more than finding count.

### Whole-document pass right after round 10 — declined by user

**Approach:** I offered to run a whole-document pass as Round 11 immediately after round 10 landed, matching the user's own round-9 guideline ("fix mechanical issues, then one final whole-document pass").

**Why it seemed promising:** Matched user's stated cadence. Would surface any remaining cross-section drift before writing-plans handoff. Kept me in the loop rather than waiting for user's review.

**Specific failure:** User chose to personally review instead, via /save args. Not a failure of the approach — a deliberate user preference for fresh-eyes review over automated sweep.

**What it taught:** Even when an approach matches a user-stated rule, the user may reserve final judgment for themselves. Don't assume rules are universal — treat them as defaults the user may override.
