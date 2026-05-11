---
date: 2026-04-25
time: "12:40"
created_at: "2026-04-25T16:40:39Z"
session_id: 8b4b92cd-0563-4bb0-886f-d772a6f77020
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-25_11-40_phase-e-task-13-complete-task-14-next.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: d8f1911b
title: Phase E Task 14 complete (3+1 commit chain) — Phase F Task 15 next
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_projection_helpers.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-e-serialization-projection.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-h-finalizer-consumers-contracts.md
---

# Handoff: Phase E Task 14 complete (3+1 commit chain) — Phase F Task 15 next

## Goal

Complete Phase E Task 14 of T-20260423-02 Packet 1 (deferred-approval-response refactor): rewrite the projection helpers in `delegation_controller.py` (`_project_request_to_view` adds `UnknownKindInEscalationProjection` runtime guard for non-escalatable kinds; `_project_pending_escalation` switches from collaboration-anchored to job-anchored signature with terminal/unparked/tombstone guards) and add `_ESCALATABLE_REQUEST_KINDS` runtime constant. Helpers stay pure; abort-signaling and exception-catch logic owned by callsites (Task 17 for `start()`, Task 20 for `poll()`).

**Trigger:** Prior session (resumed from `2026-04-25_11-40_phase-e-task-13-complete-task-14-next.md`) closed at Phase E Task 13 complete (5+1 commit chain) with branch at `f0ea603b`. Three open carry-forward items E13.1-E13.3 deferred. The handoff explicitly named Task 14 as the next work, with the user's expectation that Task 14 take place in a fresh session under the `subagent-driven-development` workflow.

**Stakes:** Task 14 is the second half of Phase E (Task 13 was the wire-shape rewrite of `DelegationDecisionResult`). Phase E is the wire-contract slice between Phase D (`ResolutionRegistry` standalone primitive, complete) and Phase F (worker runner). Adding a runtime guard on a helper called from multiple sites (including the synchronous `_finalize_turn` escalation-return path) had load-bearing transitive effects that the convergence map originally undercounted; the dispatch executed an honest disposition with 8 tracked-debt skipped tests rather than a forced fix that would have leaked Task 17 / Phase F-G scope into Task 14.

**Success criteria:**
- `_project_request_to_view` raises `UnknownKindInEscalationProjection` for non-escalatable kinds (belt-and-suspenders runtime guard)
- `_project_pending_escalation(self, job: DelegationJob)` with terminal/unparked/tombstone guards
- `_ESCALATABLE_REQUEST_KINDS: frozenset[str]` module-level constant matching `EscalatableRequestKind` Literal
- Single production callsite in `poll()` updated to pass `refreshed` (the `DelegationJob`)
- New `tests/test_projection_helpers.py` with helper-isolated unit tests
- Pre-existing breaking tests dispositioned with substantive Phase G/F citations
- Full `codex-collaboration` package suite green
- L1-L7 + W1-W7 honored end-to-end

**Connection to project arc:** Phase E (Tasks 13 + 14) is now structurally complete. Packet 1 manifest sequences A→B→C→D→E→F→G→H. With Phase E shipped, Phase F (worker runner — Tasks 15 + 16) is the next major slice. Phase F is the largest phase per the plan structure and owns the worker-driven authority chain (`update_parked_request` wiring, capture-ready handshake integration, worker thread lifecycle) that will resume normal operation of the 8 tests skipped in Task 14.

## Session Narrative

Started by `/handoff:load` resuming the prior session at commit `f0ea603b` on branch `feature/delegate-deferred-approval-response`. The prior handoff completed Phase E Task 13 closeout-docs and named Task 14 as the next work item with a specific dispatch suggestion (use `subagent-driven-development`, sonnet implementer, fresh dispatch packet).

**Stage 1 — Read-only orientation pass.** Before drafting the convergence map, the user provided their own initial Task 14 read (paste of /copy output), naming the main watchpoint as "tombstone guard fires on resolved-after-D4 requests" and identifying disposition (c) "direct-store assertion" as their lean for two of the three originally-known breaking tests. The user explicitly asked: "Do your own read-first pass and share your findings + feedback."

I executed an independent read of: plan §Task 14 (lines 190-477), Task 17 plan section (Phase G, lines 75-211), Task 20 plan section (Phase H, lines 325-446), `carry-forward.md`, `conftest.py` (52 lines, full read), `models.py:1-80` (Literal definitions), and the controller's helper bodies + `_finalize_turn` body + the three triage-target test bodies. Findings extended the user's read in three directions:

1. **The user's "tombstone" framing was secondary, not primary.** The PRIMARY cause of breakage was `job.parked_request_id` being structurally unset in the current production path (no `update_parked_request` callsites exist in `delegation_controller.py`; only definition at `delegation_job_store.py:187`). The new job-anchored helper short-circuits at the unparked guard before ever consulting the request store.
2. **The breakage scope was at least three tests, not one.** Two of the three (`:1755-1756` and `:2377-2378`) were Task 13's own migrations. Skipping them under Task 14 would partially un-do Task 13's just-landed `poll()`-migration work.
3. **Two additional dispatch corrections beyond the user's three:** `pending_request_store_factory.insert(request)` should be `create()` (the real API; `insert()` doesn't exist), and the unused `from typing import cast` import should be dropped from the generated test file template (W6).

User accepted refinements, supplied a per-test triage table (Test 1 → (b) skip; Tests 2+3 → (c) direct-store assertion via `prs.get(...)` strengthened) and a phase-aware-narrowing acknowledgment paragraph for the closeout-docs commit, and commanded "draft the convergence map now."

**Stage 2 — Convergence map drafting.** Wrote the binding convergence map: 7 locks (L1-L7) for positive scope, 7 watchpoints (W1-W7) for negative scope, the per-test triage table with binding dispositions, an out-of-scope table citing plan-line locations for each item, acceptance criteria, and a pre-dispatch checklist. The map was deliberately structured to match Task 13's dispatch packet shape so the implementer could rely on the same conventions.

**Stage 3 — Implementer dispatch (sonnet, general-purpose).** Sent the implementer with the full convergence map + plan §14.1-14.7 verbatim + the three triage-target test bodies inline + reporting contract. Implementer reported `DONE_WITH_CONCERNS` with one feat commit `becfc316`, 4 files changed, 978 passing + 8 skipped + 0 failed. Self-review claimed all locks honored.

**Stage 4 — DONE_WITH_CONCERNS analysis surfaced a convergence-map gap.** The implementer flagged that disposition (c) for Tests 2+3 was unreachable: `_finalize_turn:1614-1620` calls `_project_request_to_view` directly on the captured request, and under the new L4 guard, that call raises `UnknownKindInEscalationProjection` for any unknown-kind capture. `_permissions_request(99)` in Tests 2+3 produces `kind="unknown"` (its `method` `item/permissions/requestApproval` is not one of the three recognized methods), so `decide()` raises (wrapped in `CommittedDecisionFinalizationError`) before any post-decide assertion executes — `prs.get("99")` is never reached. The implementer upgraded Tests 2+3 from (c) to (b) skip and discovered 5 more pre-existing tests with the same structural failure, skipping all 8 tests with substantive Phase G/F citations.

**Stage 5 — Adjudication.** Verified the implementer's analytical claim by reading `_finalize_turn:1607-1620`, confirming the direct `_project_request_to_view` call. Confirmed all 8 skipped tests fall into one of two failure modes: Mode A (6 tests — `_finalize_turn` raises on unknown-kind capture; owner Phase G Task 17) or Mode B (2 tests — `parked_request_id` unset in current path; owner Phase F/G + W1). Skip reasons were substantive — each cited a specific Task/Phase as unblock and (where applicable) a sibling test for partial coverage.

The convergence map's L4 contained a transitive-effects gap I missed: adding a runtime raise to `_project_request_to_view` silently changed every caller's behavior, including `_finalize_turn`'s synchronous escalation-return callsite. The map's W3 originally enumerated 3 breaking tests; the actual count was 8. I considered three options: (α) accept the 8-test skip set, (β) soften L4 to NOT raise in `_project_request_to_view`, only in the helper, (γ) add a try/except at `_finalize_turn`. Picked α: option β would weaken the spec's belt-and-suspenders intent for unknown-kind on JSONL replay paths; option γ would Phase-G-creep. The 8 skipped tests are honest deferrals with explicit unblock owners and preserved bodies for unskip post-Task-17.

Process note logged: the implementer flagged DONE_WITH_CONCERNS rather than BLOCKED — acceptable here because the analysis was correct and the decision was honest, but BLOCKED + question would have been the cleaner pathway (controller adjudicates scope; implementer faithfully executes). Recorded in the round-trip dispatch as guidance for next time.

**Stage 6 — Closeout-1 dispatch (Pyright fixes).** Sent the same implementer back via SendMessage with two targeted Edit operations: (a) add `cast(EscalatableRequestKind, request.kind)` plus imports at `delegation_controller.py:984` to satisfy Pyright's narrowing complaint at the construction site, and (b) tighten `test_projection_helpers.py:27` return type from `tuple[DelegationController, object]` to `tuple[DelegationController, PendingRequestStore]` (the `object` annotation was erasing the `prs` type, causing Pyright failures on all four `prs.create()` callsites). Implementer reported DONE with commit `65f270ab`, 2 files changed, suite still 978/8/0.

**Stage 7 — Spec compliance review (sonnet, general-purpose).** Verdict: ✅ Spec compliant. All L1-L7 honored, all W1-W7 navigated, 8 skip decorators substantive, signature change correct, single callsite update verified via `grep -n "_project_pending_escalation" packages/plugins/codex-collaboration/server/delegation_controller.py`, no scope drift. Spec review found nothing — its zero-finding is itself signal that the convergence map's L/W structure was tight.

**Stage 8 — Code quality review (`superpowers:code-reviewer`).** Verdict: Ready to merge **with fixes**. Surfaced 1 Important (I1) + 4 Minor:
- Important I1: Two skip-reason citations cite fabricated sibling tests. `tests/test_delegation_controller.py:1424` cited `test_start_with_unparseable_request_creates_causal_record_status` (doesn't exist; the actual skipped test is `_creates_minimal_causal_record`). `tests/test_delegation_controller.py:2380` cited `test_decide_rejects_stale_request_id_after_escalation` without `re-` (doesn't exist; only `_after_reescalation` exists, which IS the skipped test). Both verified absent via grep.
- Minor M1-M4: M1 (no test docstrings — declined as local-style-match), M2 (`# type: ignore[arg-type]` on test helper status param — acceptable as-is), M3 (Mode-B skip reasons solid — no action), M4 (`_ESCALATABLE_REQUEST_KINDS` and `EscalatableRequestKind` define same strings in two places; `frozenset(get_args(EscalatableRequestKind))` would derive — deferred as E14.1).

**Stage 9 — Closeout-2 dispatch (fabricated citation fixes).** Sent the implementer back with two targeted Edit operations replacing the false sibling citations with honest "no current sibling coverage" framing. The replacement explains why no real sibling could exist (the D4 carve-out and `request_already_decided` invariant both intrinsically require Mode A flows in the pre-Phase-G interregnum, so no non-Mode-A coverage path exists). Implementer reported DONE with commit `b66d838f`, 1 file changed, suite still 978/8/0.

**Stage 10 — Code quality re-review.** Verdict: ✅ Ready to merge. Both fabricated names confirmed removed via grep; replacement framings honest (claim no sibling, explain Mode A mechanic, retain Task 17 unblock owner); no collateral changes (diff: 6 insertions / 4 deletions, two skip decorators only).

**Stage 11 — Closeout-docs commit.** Updated `docs/plans/.../carry-forward.md` with three changes: (1) E13.1's "Lands at" updated to remove the "Task 14 will likely touch test_models_r2.py" expectation (W7 confirmed it didn't, so E13.1 reroutes to end-of-Packet-1 polish), (2) new Open items entry E14.1 (M4 from code review — `get_args` derivation), (3) new Closed items entry under "From Phase E Task 14 + closeouts" with full 3-commit chain narrative, convergence-map gap recording, 8-test skip-set classification, triage-table evolution, lock conformance, and independent verification dimension. Commit `d8f1911b` matches the Phase D + Task 13 closeout-docs precedent (only carry-forward.md touched; plan-template checkboxes left unchecked).

**Set aside for later:** Phase F Task 15 (worker runner step 1 — likely worker thread + capture-ready handshake integration) deferred to fresh session per the user's standing cadence preference. Three E13.x carry-forward items still deferred (E13.1 to end-of-Packet-1, E13.2-E13.3 to Phase H). New E14.1 deferred to end-of-Packet-1.

## Decisions

### D1: Use subagent-driven-development workflow (Task 13 precedent)

**Choice:** Execute Task 14 via the `subagent-driven-development` skill with implementer + spec-reviewer + code-quality-reviewer subagents, identical to Task 13's pipeline.

**Driver:** User invoked `/superpowers:subagent-driven-development` after the convergence map was drafted. Workflow choice was a hard constraint, not a recommendation. Continuity with Task 13's process (which produced the user's preferred two-stage review pattern).

**Alternatives considered:**
- **Direct in-session implementation** — controller writes code itself. Rejected because user explicitly directed the subagent workflow.
- **Single-stage subagent (implement only, no review subagents)** — rejected because the workflow contract requires both spec compliance AND code quality review.

**Implications:** Each commit gets at least one review pass; controller's main-context stays clean (delegated implementation context lives in subagent contexts); review-found issues round-trip via SendMessage to the same implementer. Reviews caught one Important issue (closeout-2 fabricated citations) that would otherwise have shipped.

**Trade-offs accepted:** More subagent invocations (1 implementer + closeout-1 round-trip + spec reviewer + code quality reviewer + closeout-2 round-trip + code quality re-reviewer = 6 subagent calls). Two-stage review adds latency vs. faster direct implementation. Accepted because: workflow contract requires it, AND review caught real issues.

**Confidence:** High (E2) — workflow executed end-to-end; both reviews surfaced real or near-real issues that informed closeouts.

**Reversibility:** N/A — workflow choice was per-session.

**Change trigger:** None — user-directed workflow.

### D2: Sonnet model for implementer subagent (Task 13 precedent)

**Choice:** Dispatched implementer with `model: "sonnet"` (general-purpose subagent type).

**Driver:** Skill documentation tier guidance — Task 14 touches 4 files with integration concerns + helper-rewrite judgment. Task 13 used sonnet successfully with two closeouts surfacing dead-binding issues. Same calibration profile.

**Alternatives considered:**
- **Haiku** — cheap-model territory. Rejected because the per-test triage table requires judgment, not just mechanical substitution. Haiku's failure mode on judgment calls is to over-migrate or under-migrate.
- **Opus** — overkill. Task is integration-not-architecture.

**Implications:** Implementer hit clean implementation on first try AND caught the convergence-map L4 transitive-effects gap during execution — better-than-expected diagnostic surface for sonnet. Did NOT escalate via BLOCKED, however; flagged DONE_WITH_CONCERNS instead, which is a process gap.

**Trade-offs accepted:** None significant — sonnet performed at the high end of its calibration band.

**Confidence:** High (E2) — calibration matched workflow guidance and produced workable result.

**Reversibility:** N/A — model choice was per-dispatch.

**Change trigger:** If iterative-review counts exceed 3 closeouts per task on a future task, escalate to Opus for the feat commit.

### D3: Accept the 8-test skip set as the disposition for the convergence-map L4 gap

**Choice:** All 8 skipped tests stand. 6 Mode A (Phase G Task 17 unblock) + 2 Mode B (Phase F/G + W1 unblock).

**Driver:** Implementer's analysis of `_finalize_turn:1614-1620` calling `_project_request_to_view` with unknown-kind requests is correct. The new L4 guard raises during the synchronous escalation return path, which propagates up `start()` (raises) or wraps to `CommittedDecisionFinalizationError` in `decide()`. The original disposition (c) "direct-store assertion via `prs.get(...)`" is structurally unreachable for Mode A tests because `decide()` raises before the post-decide assertion executes.

**Alternatives considered:**
- **Option β: Soften L4 to raise only in `_project_pending_escalation`, not in `_project_request_to_view`** — rejected because L4's spec docstring explicitly describes the runtime guard as "belt-and-suspenders against dynamic construction paths (JSONL replay of pre-Packet-1 records, future callsites that bypass the type system)." Softening it would weaken the long-term invariant; future tasks may not remember to add the guard back.
- **Option γ: Add a try/except at `_finalize_turn:1614-1620`** that catches `UnknownKindInEscalationProjection` and returns either a synthetic null-projection variant or terminalizes the job — rejected as Phase G Task 17 territory. Task 17's plan section at `phase-g-public-api.md:95-211` already specifies this catch behavior at the `start()` layer.
- **Option (c) original: Direct-store assertion** — rejected because the failing call (`controller.decide(...)`) raises before any post-decide observation can be made.

**Implications:** 8 tests added to the carry-forward debt ledger. Each has a named Phase/Task unblock owner. When Task 17 lifts the L6 callsite guard (adding Phase G unknown-kind handling at `start()` and `decide()` callsites), 6 Mode A tests will unskip. When Phase F/G wires `update_parked_request` at capture time, 2 Mode B tests will unskip. Skipped tests preserve their bodies (only decorator added), so unskip is a single-decorator-removal commit.

**Trade-offs accepted:** Significant tracked debt (8 tests = ~2x Phase B+C+D combined skipped-tests count). Mitigated by: (a) explicit unblock owners — no orphans, (b) preserved bodies — unskip is mechanical, (c) substantive skip reasons — future readers understand the structural mechanic without re-investigation.

**Confidence:** High (E3) — implementer's analysis verified by independent read of `_finalize_turn` body; both spec review and code review approved; independent third-party reading would surface no new issues (the failure mechanic is structural).

**Reversibility:** High — disposition can be revisited at Task 17 (the natural unblock point). If Task 17 elects a different unknown-kind handling strategy, the skip reasons can be updated.

**Change trigger:** If Task 17 doesn't terminalize unknown-kind captures (e.g., decides to allow them through with a synthetic null-projection variant), the skip reasons need to point to the new mechanism.

### D4: Replace fabricated sibling-test citations with honest "no current sibling coverage" framing

**Choice:** Closeout-2 replaced two `@pytest.mark.skip(reason=...)` decorator strings citing nonexistent sibling tests with explicit "no current sibling coverage" framing that explains the structural reason.

**Driver:** Code-quality review I1 surfaced two false citations:
- `test_delegation_controller.py:1424` cited `test_start_with_unparseable_request_creates_causal_record_status` (doesn't exist; only `_creates_minimal_causal_record` exists, which IS the skipped test).
- `test_delegation_controller.py:2380` cited `test_decide_rejects_stale_request_id_after_escalation` without `re-` (doesn't exist; only `_after_reescalation` exists, which IS the skipped test).

Both verified absent via grep. The implementer's intent was likely to point at "a sibling that covers part of this," but neither sibling exists. False confidence about coverage continuity is exactly the failure mode the skip-reason rubric exists to prevent.

**Alternatives considered:**
- **Find a real sibling that genuinely covers part of the invariant** — rejected because no such sibling exists. The `request_already_decided` invariant intrinsically requires multi-decide flow which hits Mode A. The D4 carve-out has no non-Mode-A coverage path.
- **Drop the partial-coverage clause entirely** — rejected because the skip-reason rubric requires "either point to sibling for partial coverage, OR explain why no real sibling exists." Dropping it would just delete information without honesty.

**Implications:** Skip-reason rubric is enforced uniformly across all 8 decorators. Future readers see honest "no current sibling" framing where applicable.

**Trade-offs accepted:** None significant.

**Confidence:** High (E3) — verified by re-review.

**Reversibility:** High — if Task 17 lands a non-Mode-A coverage path that genuinely covers either invariant, the skip reasons can be updated to cite that real sibling.

**Change trigger:** Task 17 introduces non-Mode-A coverage of either invariant.

### D5: Defer M4 (`get_args` derivation) as E14.1 carry-forward

**Choice:** Code-quality review's Minor M4 finding (suggest `frozenset(typing.get_args(EscalatableRequestKind))` derivation instead of duplicating the literal set) was deferred to end-of-Packet-1 polish as E14.1.

**Driver:** M4 is style/declarativeness, not correctness. The new test `test_escalatable_set_has_three_literals` would catch a drift if a fourth literal is added. The explicit `frozenset({"command_approval", "file_change", "request_user_input"})` is arguably MORE readable than `frozenset(get_args(EscalatableRequestKind))` because the literal values are visible inline.

**Alternatives considered:**
- **Bundle into closeout-2** — rejected because closeout-2 was scoped to fabricated-citation fixes only; bundling would Phase-G-creep on the closeout-fix discipline.
- **Decline as a non-issue** — rejected because the suggestion has merit (single source of truth) even if the current form is acceptable.

**Implications:** Carry-forward grows by 1 item (12 prior + E14.1 = 13). End-of-Packet-1 polish absorbs.

**Trade-offs accepted:** Slight carry-forward accumulation. Mitigated by: explicit landing point (no orphans), trivial fix when the time comes (one-line change).

**Confidence:** High (E2) — M4 reviewer reasoning is sound; the deferral landing point is plan-anchored.

**Reversibility:** High — could be picked up in any Phase E/F polish window.

**Change trigger:** Add a fourth `EscalatableRequestKind` literal (would force the derivation form to keep `_ESCALATABLE_REQUEST_KINDS` in sync without manual edit).

## Changes

### `packages/plugins/codex-collaboration/server/delegation_controller.py` (modified)

**Purpose:** Rewrote both projection helpers and added module-level constant. Updated single production callsite of `_project_pending_escalation` in `poll()`.

**Approach:**
- Added `_ESCALATABLE_REQUEST_KINDS: frozenset[str]` module-level constant at line 113 (near `_TERMINAL_STATUS_MAP`-style siblings)
- `_project_request_to_view` (lines 963-987): added runtime guard at the top — `if request.kind not in _ESCALATABLE_REQUEST_KINDS: raise UnknownKindInEscalationProjection(...)`. Construction site uses `cast(EscalatableRequestKind, request.kind)` for Pyright narrowing (added in closeout-1).
- `_project_pending_escalation` (lines 989-1009): full rewrite. New signature `(self, job: DelegationJob)`. Three early-return guards: terminal status (`completed/failed/canceled/unknown`), unparked (`parked_request_id is None`), tombstone (`request is None or request.status != "pending"`). Re-raises `UnknownKindInEscalationProjection` from inner projector for invariant violations. Pure — zero side effects.
- `poll()` callsite at line 1067 changed from `self._project_pending_escalation(refreshed.collaboration_id)` to `self._project_pending_escalation(refreshed)`.
- Imports: added `cast` to `from typing import` block at line 64; added `EscalatableRequestKind` to the `from .models import` block.

**Key locations:**
- `delegation_controller.py:113` — `_ESCALATABLE_REQUEST_KINDS` constant
- `delegation_controller.py:963-987` — `_project_request_to_view` (with runtime guard)
- `delegation_controller.py:989-1009` — `_project_pending_escalation` (job-anchored + tombstone)
- `delegation_controller.py:1067` — single production callsite update
- `delegation_controller.py:1644-1650` — `_finalize_turn` escalation-return path (NOT modified, but calls `_project_request_to_view` directly — load-bearing for Task 17)
- `delegation_controller.py:1608-1610` — D4 `update_status(captured_request.request_id, "resolved")` write (NOT modified)

**Future-Claude:** Task 17 (Phase G) will rewrite `start()` and the `_finalize_turn` callsite to handle unknown-kind captures gracefully (terminalize the job before reaching projection, or wrap the L4 raise into a Phase G abort signal). Task 20 (Phase H) will wrap `poll()`'s `_project_pending_escalation` call in try/except for `UnknownKindInEscalationProjection`, calling `signal_internal_abort(reason="unknown_kind_in_escalation_projection")` on catch. Both are explicitly out of Task 14 scope.

### `packages/plugins/codex-collaboration/tests/test_projection_helpers.py` (new, 162 lines)

**Purpose:** Canonical home for projection-helper unit tests.

**Approach:** Module-local helpers (no conftest factory fixtures, per W4 lock against fabricated precedent). Imports `_build_controller` from `tests.test_delegation_controller` for thin reuse. Local helper `_build_controller_for_helpers(tmp_path) -> tuple[DelegationController, PendingRequestStore]` returns just the controller + pending request store. Local helper `_build_simple_job(*, status, parked_request_id=None) -> DelegationJob` constructs minimal jobs directly via the dataclass.

**Test cases (8 total):**
1. `test_escalatable_set_has_three_literals` — `_ESCALATABLE_REQUEST_KINDS == frozenset({"command_approval", "file_change", "request_user_input"})`
2. `test_project_request_to_view_raises_for_unknown_kind` — explicit `pytest.raises(UnknownKindInEscalationProjection)` on `kind="unknown"`
3. `test_project_request_to_view_admits_escalatable_kinds` — iterates the three escalatable kinds
4. `test_project_pending_escalation_returns_none_for_terminal_job` — iterates four terminal statuses
5. `test_project_pending_escalation_returns_none_when_unparked` — `parked_request_id=None`
6. `test_project_pending_escalation_returns_none_on_tombstone` — request is `status="resolved"` (worker mark_resolved landed before update_parked_request(None))
7. `test_project_pending_escalation_raises_for_unknown_kind_request` — request stored with `kind="unknown"` and `status="pending"`, parked_request_id wired
8. `test_project_pending_escalation_returns_view_on_happy_path` — full end-to-end positive case

**Key location:** All 8 tests in this file.

**Future-Claude:** Add a 9th test if a new helper invariant is discovered. The pattern of constructing requests via `prs.create()` and jobs via `_build_simple_job(...)` is the package's helper-isolation idiom under W4. If a future task adds factory fixtures to conftest.py, this file can migrate, but until then the local-helper pattern is the binding precedent.

### `packages/plugins/codex-collaboration/tests/test_delegation_controller.py` (modified)

**Purpose:** Added `@pytest.mark.skip(reason=...)` decorators to 5 pre-existing tests dispositioned via the convergence map's triage table + adjudication. Closeout-2 replaced two fabricated sibling-test citations.

**Disposition table (5 skipped tests in this file):**
- `:1360` `test_start_with_unknown_request_interrupts_and_escalates` — Mode A, cites Task 17. Skip reason explains `_finalize_turn` L6 callsite raises `UnknownKindInEscalationProjection` for `kind="unknown"` (permissions request).
- `:1418` `test_start_with_unparseable_request_creates_minimal_causal_record` — Mode A (D4 carve-out), cites Task 17. Closeout-2 replaced fabricated sibling citation with "No current sibling coverage for the D4 parse-failure carve-out (any path exercising unknown-kind capture hits the same Mode A break); coverage restored at Task 17."
- `:1737` `test_decide_approve_can_reescalate_with_new_pending_request` — Mode A (re-escalation produces unknown-kind), cites Phase G/F. Was originally Test 2 in the convergence map's triage table (disposition (c) direct-store), upgraded to (b) skip during adjudication.
- `:2372` `test_decide_rejects_stale_request_id_after_reescalation` — Mode A, cites Phase G/F. Was originally Test 3 in the triage table (disposition (c)), upgraded to (b). Closeout-2 replaced fabricated sibling citation with "No current sibling coverage for the request_already_decided rejection invariant (which intrinsically requires multi-decide flow that hits Mode A in the interregnum); coverage restored at Task 17."
- `:2588` `test_poll_needs_escalation_projects_pending_request_without_raw_ids` — Mode B (parked_request_id unset in current path, command_approval kind so no Mode A trigger). Was originally Test 1 in the triage table (disposition (b) skip — unchanged through adjudication).

**Future-Claude:** Each skipped test preserves its body. When Task 17 lands the unknown-kind handling at the L6 callsite, a single-decorator-removal commit unskips Mode A tests. When Phase F/G wires `update_parked_request` at capture time, the same for Mode B tests.

### `packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py` (modified)

**Purpose:** Added `@pytest.mark.skip(reason=...)` decorators to 3 pre-existing integration tests dispositioned via the same Mode A / Mode B classification.

**Disposition table (3 skipped tests in this file):**
- `:617` `test_e2e_unknown_request_kind_interrupts_and_escalates` — Mode A (e2e via MCP), cites Task 17.
- `:793` `test_delegate_poll_needs_escalation_returns_projected_request` — Mode B (e2e poll, command_approval kind, parked_request_id never wired in interregnum), cites Phase F/G + W1.
- `:1062` `test_decide_reescalation_uses_pending_escalation_key` — Mode A (decide() re-escalation → MCP isError), cites Task 17. Skip reason notes that the `pending_escalation` key contract is preserved by `test_projection_helpers.py`.

**Future-Claude:** Same unskip pattern as the controller-test file's skips.

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (modified)

**Purpose:** Phase E Task 14 closeout-docs commit (`d8f1911b`). Three changes:
1. E13.1 row "Lands at" updated from "Task 14 cleanup pass — Task 14 will likely touch test_models_r2.py via projection-helper rewrites" to "End-of-Packet-1 polish — Task 14 W7 confirmed scope was helper-only and did not touch test_models_r2.py" (clarification, not scope change)
2. New "Open items → From Phase E Task 14" subsection with 1 entry: E14.1 (`get_args(EscalatableRequestKind)` derivation, deferred from M4 code review)
3. New "Closed items → From Phase E Task 14 + closeouts" entry with full 3-commit chain narrative (`becfc316` feat + `65f270ab` Pyright closeout + `b66d838f` fabricated-citation closeout), the convergence-map gap recording (L4 transitive effects), 8-test skip-set classification (6 Mode A + 2 Mode B), triage-table evolution (3 → 8 dispositions), lock conformance summary (L1-L7 + W1-W7), and independent verification dimension

**Key location:** Open items at lines ~52-66 (after Phase E Task 13's E13.x); Closed items at lines ~115-135 (after Phase E Task 13 + closeouts entry).

## Codebase Knowledge

### Projection helpers (post-Task-14)

```python
_ESCALATABLE_REQUEST_KINDS: frozenset[str] = frozenset(
    {"command_approval", "file_change", "request_user_input"}
)


class DelegationController:
    # ...

    def _project_request_to_view(
        self, request: PendingServerRequest
    ) -> PendingEscalationView:
        """Project a PendingServerRequest to the caller-visible PendingEscalationView.

        Raises UnknownKindInEscalationProjection if request.kind is not in the
        escalatable set. ..."""
        if request.kind not in _ESCALATABLE_REQUEST_KINDS:
            raise UnknownKindInEscalationProjection(...)
        return PendingEscalationView(
            request_id=request.request_id,
            kind=cast(EscalatableRequestKind, request.kind),
            requested_scope=request.requested_scope,
            available_decisions=self._PLUGIN_DECISIONS,
        )

    def _project_pending_escalation(
        self, job: DelegationJob
    ) -> PendingEscalationView | None:
        """Project a job's parked request into a view. PURE — no side effects.

        Returns None for legitimate no-view states (terminal, unparked, tombstone).
        Re-raises UnknownKindInEscalationProjection for invariant violations."""
        if job.status in ("completed", "failed", "canceled", "unknown"):
            return None
        if job.parked_request_id is None:
            return None
        request = self._pending_request_store.get(job.parked_request_id)
        if request is None or request.status != "pending":
            return None
        return self._project_request_to_view(request)
```

Key locations:
- `delegation_controller.py:113` — constant
- `delegation_controller.py:963-987` — `_project_request_to_view`
- `delegation_controller.py:989-1009` — `_project_pending_escalation`

### Callsite map for `_project_request_to_view` (load-bearing for Task 17)

| Callsite | File:line | Path | Behavior under Task 14 L4 guard |
|----------|-----------|------|---------------------------------|
| Inside `_project_pending_escalation` | `delegation_controller.py:1009` | `return self._project_request_to_view(request)` | Re-raises through outer helper for invariant violations (correct — outer helper documents this). |
| `_finalize_turn` escalation return | `delegation_controller.py:1644-1650` | `pending_escalation=self._project_request_to_view(resolved_request or captured_request)` | **Raises for unknown-kind captures**, propagating up `start()` (raises) or wrapping into `CommittedDecisionFinalizationError` in `decide()`. This is the Mode A failure source for 6 of the 8 skipped tests. |

Pre-Task-14 there was only the `_project_pending_escalation` callsite (the helper called the inner projector). The `_finalize_turn` callsite always existed but didn't raise pre-Task-14 because the inner helper didn't have a runtime guard.

### `_finalize_turn` D4 + escalation-return invariant

```python
# _finalize_turn at delegation_controller.py:1577-1650
if captured_request is not None:
    if not captured_request_parse_failed:
        # D4: mark wire request resolved (parse failures stay pending).
        self._pending_request_store.update_status(
            captured_request.request_id, "resolved"
        )

    # ... Job status derivation ...
    updated_job = self._persist_job_transition(job_id, final_status)

    if final_status == "needs_escalation":
        self._journal.append_audit_event(...)
        # Re-read so the returned object reflects the authoritative status.
        resolved_request = self._pending_request_store.get(
            captured_request.request_id
        )
        return DelegationEscalation(
            job=updated_job,
            pending_escalation=self._project_request_to_view(
                resolved_request or captured_request
            ),
            agent_context=turn_result.agent_message or None,
        )
```

Two key invariants:
- D4 marks every parseable captured request `status="resolved"` BEFORE the escalation returns (line 1608-1610). Parse failures stay `"pending"` (D4 carve-out).
- The escalation return path uses `_project_request_to_view` DIRECTLY (line 1647), not `_project_pending_escalation`. This bypasses the new job-anchored helper but goes through the new L4 guard.

Phase G Task 17 will rewrite this section to handle unknown-kind captures (terminalize the job vs. raise a synthetic null-projection variant).

### `controller.poll()` post-Task-14

```python
# delegation_controller.py:1066-1067
pending_escalation = None
if refreshed.status == "needs_escalation":
    pending_escalation = self._project_pending_escalation(refreshed)
```

Single production callsite of `_project_pending_escalation`. Currently `pending_escalation` evaluates to `None` for every legitimate flow because `parked_request_id` is structurally unset (W1). Phase F worker-runner work will wire `update_parked_request(job_id, request_id)` at capture time, restoring the helper's intended behavior.

Phase H Task 20 will wrap this call in try/except for `UnknownKindInEscalationProjection`, calling `signal_internal_abort` on catch.

### `EscalatableRequestKind` vs `PendingRequestKind` (load-bearing for L4 cast)

```python
# models.py:16-27
PendingRequestKind = Literal[
    "command_approval", "file_change", "request_user_input", "unknown"
]
# PendingRequestKind stays 4 literals — "unknown" is still a valid PERSISTED kind
# (parse-failure audit record). EscalatableRequestKind is the narrower subset
# that may appear in PendingEscalationView. Under Packet 1, kind="unknown"
# terminalizes the job before reaching any escalation projection.
EscalatableRequestKind = Literal[
    "command_approval",
    "file_change",
    "request_user_input",
]
```

The two-Literal split is the type-system half of the L4 invariant. Runtime guard (`_ESCALATABLE_REQUEST_KINDS` membership check) is the other half. `_ESCALATABLE_REQUEST_KINDS` and `EscalatableRequestKind` define the same three strings in two places — E14.1 carry-forward suggests `frozenset(get_args(EscalatableRequestKind))` derivation, deferred to end-of-Packet-1 polish.

`cast(EscalatableRequestKind, request.kind)` at the construction site (line 985) is required because Pyright cannot narrow the runtime guard's `if request.kind not in _ESCALATABLE_REQUEST_KINDS: raise` into the type system. The cast is annotated-only — runtime behavior unchanged.

### Test factory-fixture inventory (W4 binding)

```bash
$ grep -rn "@pytest.fixture" packages/plugins/codex-collaboration/tests/
tests/conftest.py:14:@pytest.fixture            # vendored_schema_dir
tests/conftest.py:22:@pytest.fixture            # client_request_schema
tests/test_runtime.py:268:@pytest.fixture       # local to test_runtime.py
```

3 fixtures package-wide; 2 in conftest, 1 file-local. **No factory fixtures.** The package's prevailing pattern is the module-local `_build_controller(tmp_path)` helper used 30+ times in `test_delegation_controller.py`. The plan's "if not, add them following existing fixture patterns" guidance was misleading — the implementer correctly used module-local helpers (W4 enforcement).

### Cross-test-file helper imports (idiomatic in this package)

```bash
$ grep -rn "from tests.test_delegation_controller import" packages/plugins/codex-collaboration/tests/
tests/test_dialogue.py:N:from tests.test_delegation_controller import _build_controller
tests/test_dialogue_integration.py:N:...
# (6 other files import _build_controller from test_delegation_controller)
tests/test_projection_helpers.py:22:from tests.test_delegation_controller import _build_controller
```

Cross-test-file imports of helpers are a package idiom. Not a fragile coupling.

### Skip-decorator format (post-Task-14)

```python
@pytest.mark.skip(
    reason=(
        "Phase G (Task 17): _finalize_turn L6 callsite calls _project_request_to_view "
        "directly with kind='unknown'; ... "
        "Task 17 will add unknown-kind handling at the L6 callsite. "
        "[Sibling-coverage clause OR honest 'no current sibling coverage' framing]."
    )
)
def test_X(...) -> None:
    ...  # body preserved verbatim
```

8 decorators package-wide post-Task-14 — 5 in `test_delegation_controller.py`, 3 in `test_delegate_start_integration.py`. Each cites a specific Phase/Task as unblock. Each preserves the test body for one-decorator-removal unskip.

### Carry-forward.md structure (post-Task-14)

```
# Packet 1 Carry-Forward Tracker
...
## Open items
### From Phase A
### From Phase B Task 6
### From Phase B Task 7
### From Phase B Task 8
### From Phase C Task 10
### From Phase E Task 13     <-- E13.1 reroute via d8f1911b
### From Phase E Task 14     <-- added d8f1911b
---
## Closed items
### From Phase B Task 6
### From Phase B Task 7
### From Phase B Task 9 + closeout
### From Phase C Task 10 + closeout
### From Phase D Task 12 + closeout
### From Phase D Task 11 + closeout
### From Phase E Task 13 + closeouts
### From Phase E Task 14 + closeouts   <-- added d8f1911b
---
## How to add an item
```

13 open items now (12 prior + E14.1). 8 closed-section entries (the 8 closed phases/tasks).

### Task 14 commit chain (final)

| SHA | Type | Subject |
|-----|------|---------|
| `becfc316` | feat | rewrite projection helpers with guard + job-anchored + tombstone |
| `65f270ab` | fix closeout 1 | narrow request.kind to EscalatableRequestKind at projection construction site (Pyright) |
| `b66d838f` | fix closeout 2 | replace fabricated sibling-test citations with honest no-coverage framing |
| `d8f1911b` | docs closeout | record Phase E Task 14 closeout (carry-forward.md) |

3+1 commits, matching canonical shape (Task 13's 5+1 stretched because the same defect-class surfaced on both arms separately; Task 14 had no symmetric arms).

### Defect-class pattern: convergence-map L4 transitive-effects gap

L4 specified the new RAISE behavior of `_project_request_to_view` but only audited the function's role as inner-projector for `_project_pending_escalation`. It missed the OTHER callsite at `_finalize_turn:1644-1650`, which calls `_project_request_to_view` directly during the synchronous escalation return path. Adding a runtime raise to a function silently changes the behavior of every caller in the call graph; the convergence map's reviewer pass should have enumerated all callers, not just the explicit signature-change callsite.

The implementer caught this during execution. The map's W3 originally enumerated 3 breaking tests (the post-decide poll-projection cases via `_project_pending_escalation`); the actual count was 8 (5 additional via `_finalize_turn`'s `_project_request_to_view` direct callsite). Generalizable trap captured in the closeout-docs entry: **when adding runtime guards or behavioral changes to a helper, audit ALL callers in the call graph, not just the explicit signature-change callsite.**

## Context

### Project state

T-20260423-02 Packet 1 progress (post-Task-14):

| Phase | Tasks | Status |
|-------|-------|--------|
| A (types) | 1-5 | Complete |
| B (stores) | 6-9 | Complete (with Task 9 closeout) |
| C (journal) | 10 | Complete (with closeout) |
| D (registry) | 11-12 | Complete (with closeouts) |
| E (serialization/projection) | 13-14 | **Complete** (with closeouts) |
| **F (worker)** | **15-16** | **Not started — next** |
| G (public API) | 17-18 | Not started |
| H (finalizer/consumers/contracts) | 19+ | Not started |

13 open carry-forward items (12 prior + E14.1) at start of Phase F. Of those, 8 are the newly-skipped tests with explicit unblock owners (6 Mode A → Task 17; 2 Mode B → Phase F/G).

### Branch state

Branch: `feature/delegate-deferred-approval-response`. Clean working tree at `d8f1911b`. 4 commits on this branch beyond the prior session's `f0ea603b` (feat + 2 closeout-fixes + 1 closeout-docs).

### Mental model

**Wire-shape vs timing-semantics vs causal-flow separation.** Phase E Task 13 shipped the wire shape (`DelegationDecisionResult` 3-field). Phase E Task 14 shipped the projection authority chain (job-anchored, tombstone-guarded). Phase G Task 18 will ship the timing semantics (async `decide()` rewrite). Phase F will ship the worker causal flow (parked_request_id wiring, capture-ready handshake integration). These are orthogonal axes and must not be conflated:
- Task 14 must not wire `update_parked_request` to "fix" the interregnum — that's Phase F's authority.
- Task 14 must not catch `UnknownKindInEscalationProjection` at `_finalize_turn` to "fix" the start/decide path — that's Task 17 (Phase G)'s authority.
- Task 14 must not modify the D4 write order — that's Phase G Task 18's authority.

**Convergence-map locks/watchpoints structure.** Locks are positive scope contracts (what the implementer MUST do). Watchpoints are negative scope contracts (pre-known traps). Reviewers triage differently: spec-compliance reviewers map locks; code-quality reviewers walk watchpoints. Per-test triage tables eat the worst defect class in shape-rewrite tasks (blanket migration) by binding dispositions before code is written, shifting the implementer from "decide what to do" to "execute the decision." This calibration matched sonnet's strengths in Task 13 and again in Task 14.

**Tracked debt vs. silent breakage distinction.** The 8 skipped tests are tracked debt: each has a named unblock owner, an explicit phase/task target, and a substantive skip reason. Silent breakage (tests that quietly stop verifying their invariant) is the failure mode this skill suite exists to prevent. The two-stage review caught one instance of silent breakage in disguise (closeout-2's fabricated sibling citations) — that's the rubric working as designed.

### Environment

- Python 3.12, uv workspace, pytest test runner
- Run package suite: `cd /Users/jp/Projects/active/claude-code-tool-dev && uv run --package codex-collaboration pytest`
- Pyright in IDE for type-checking; daemon cache lags behind file edits — use `git diff <base> HEAD -- <file>` to discriminate stale-cache from real regressions (L2 from Task 13 learnings, applied throughout this session)
- Branch protection hook (`.claude/rules/workflow/git.md`): edits allowed on `feature/*` branches, blocked on `main`/`master`
- Branch is on `feature/delegate-deferred-approval-response` — edits allowed throughout

## Conversation Highlights

**Workflow choice (definitive):**
User invoked `/superpowers:subagent-driven-development` after the convergence map was drafted.
— Drove the entire stage-by-stage implementer + spec-reviewer + code-quality-reviewer pipeline. Same pattern as Task 13.

**Pre-dispatch orientation request (definitive):**
User: "Continue with read-only Phase E Task 14 orientation. Here is my initial read: ... Do your own read-first pass and share your findings + feedback."
— Established the convergence-map drafting protocol: independent read first, share findings, refine, then dispatch.

**Adjudication triage table (binding):**
User: "My disposition recommendation: ... [table with Test 1 → (b) skip, Tests 2+3 → (c) direct-store assertion]"
— Pre-locked the per-test dispositions before dispatch. The implementer's later upgrade of Tests 2+3 to (b) skip was an adjudication, not a unilateral override.

**Convergence-map structure (binding):**
User: "For the convergence map, I'd structure it as: Locks L1-L7, Watchpoints W1-W7, Per-test triage table, Out of scope. I'd dispatch only after that map is in the prompt."
— Set the L/W/triage/out-of-scope structure verbatim. Eliminated guesswork on the dispatch packet shape.

**Phase-aware narrowing acknowledgment (binding for closeout-docs):**
User: "And yes, include the one-sentence acknowledgment: Task 13's poll migration was honest for the then-current projection surface, but Task 14 deliberately hardens projection around the future parked-request authority chain; moving two assertions to direct store checks is phase-aware narrowing, not a rollback."
— This text was paste-included verbatim in the implementer's feat commit message. Even though the disposition shifted from (c) to (b) skip during adjudication, the framing concept (phase-aware progression, not rollback) carried over to the closeout-docs commit's narrative.

**Closeout cadence preference (Task 13 carry-over):**
User from prior handoff: "I would treat Task 13 as review-complete and ready for the Phase E Task 13 closeout-docs commit then saving a handoff, so the next Task 14 dispatch can take place in a fresh session."
— Confirmed in this session's closing exchange: "Yes, save a handoff so the next Phase F Task 15 dispatch can take place in a fresh session." Cadence: closeout-docs → handoff → fresh session for next task.

**Working style observed:** User produces tight, evidence-first input (tables, file:line citations) and expects similar in return. Pre-locks decisions in convergence maps. Uses `/copy` to extract specific responses for external verification. Treats locks as non-negotiable scaffolding. Defends recommendations explicitly when challenged. Distinguishes process gaps from analytical correctness (the implementer's DONE_WITH_CONCERNS vs. BLOCKED choice was flagged as a process note for next time, not a re-work trigger).

## User Preferences

**Workflow:** "Use subagent-driven-development" — when this skill is invoked, the controller (Claude) does not implement; only review subagents critique. Each task has implementer + spec-reviewer + code-quality-reviewer stages, with the implementer round-tripping fixes via SendMessage.

**Convergence-map structure:** Locks (L1-Lₙ) for positive scope contracts + Watchpoints (W1-Wₙ) for negative scope contracts + Per-test triage table for binding dispositions + Out-of-scope table with plan-line citations + Acceptance criteria. The structure is binding — dispatch only after the full map is in the prompt.

**Closeout cadence:** Closeout-fix commits (one or more `fix(...)` after the `feat(...)`) followed by a closeout-docs commit (`docs(...)`) updating carry-forward.md only. Plan-template checkboxes not ticked. Pattern matches Phase D + Task 13 (commits `bf3f8b19`, `04421cba`, `f0ea603b`, `d8f1911b`).

**Commit discipline:** New commits, never amend. Project's CLAUDE.md (global): "Always create NEW commits rather than amending, unless the user explicitly requests a git amend." Match this rule strictly.

**Scope discipline:** Locked decisions and watchpoints are hard constraints, not advice. Out-of-scope items have explicit plan-line landing points. Carry-forward items track deferred minors with named landing points; never orphans.

**Per-test triage style:** No blanket migrations. Every old assertion gets per-case judgment: skip (with substantive reason), migrate to alternative observable, or defer with phase-aware framing. The triage table in dispatch packets is binding, not advisory.

**Skip-reason rubric:** Each `@pytest.mark.skip(reason=...)` must (a) cite a specific Phase/Task as unblock owner, (b) explain the structural mechanic (not just "skip this"), and (c) either point to a real sibling test for partial coverage OR honestly explain why no real sibling exists. Fabricated sibling citations are the failure mode the rubric exists to prevent.

**Evidence density:** File:line citations expected throughout. Tables preferred over prose for relationships and decisions. Quotes preferred over paraphrase for user statements.

**External verification:** User frequently runs `/copy <N>` to extract specific responses for independent (out-of-session) review. The convergence test is whether the in-session two-stage review and the external pass agree.

**Process gap signaling:** When the implementer encounters scope deviations beyond the convergence map, BLOCKED + question is preferred over DONE_WITH_CONCERNS + unilateral decision. The controller adjudicates scope; the implementer faithfully executes. (Logged as guidance, not re-work — Task 14's implementer's analysis was correct even if the escalation pathway was process-imperfect.)

## Next Steps

### 1. Phase F Task 15 dispatch — worker runner (step 1 of 2)

**Dependencies:** Phase E complete (Task 13 + 14 ✅).

**What to read first:**
- `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md` — Task 15 + 16 plan sections (entire file ~unknown line count; read with `wc -l` first)
- `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` — worker thread + capture-ready handshake design
- `packages/plugins/codex-collaboration/server/delegation_controller.py:1-200` — current `start()` and `_execute_live_turn` (Phase G Task 17 will rewrite these; Phase F Task 15 likely lays foundational infrastructure)
- `packages/plugins/codex-collaboration/server/resolution_registry.py` — `ResolutionRegistry.wait_for_parked` and `ParkedCaptureResult` 5-variant sum (Phase D Task 12 — load-bearing for Phase F integration)
- Carry-forward C10.4 (worker-side `completion_origin` provenance — lands at Phase F worker-runner work)
- W1 (parked_request_id structurally unset) — Phase F is the natural unblock for `update_parked_request` wiring

**Approach suggestion:** Construct a fresh dispatch packet matching Task 13/14's structure: locked decisions (L*), watchpoints (W*), out-of-scope items, acceptance criteria, expected commit shape. **This time, include "audit ALL callers in the call graph for any helper modified" as a standing W item** — that's the generalizable trap captured in Task 14's closeout-docs entry.

Two carry-forward items naturally sweep at Phase F if Task 15 or Task 16 touches the relevant areas:
- C10.4 (worker-side `completion_origin="worker_completed"` writes) — Phase F worker-runner work is the explicit landing point
- The 2 Mode B skipped tests (`:2588`, `:793`) unblock when Phase F wires `update_parked_request` at capture time

**Acceptance criteria:** TBD — derive from plan section. Likely includes:
- Worker thread spawn / lifecycle primitives
- Capture-ready handshake integration with `ResolutionRegistry`'s `wait_for_parked` + `ParkedCaptureResult` 5-variant sum
- `update_parked_request(job_id, request_id)` callsite wiring in worker capture path (Mode B unblock)
- `OperationJournalEntry.completion_origin="worker_completed"` writes at worker completion (C10.4 close)

**Potential obstacles:**
- Phase F is the largest phase per the plan structure; Task 15 may need to be split if it exceeds the convergence-map's "feasibly bound" threshold
- Phase F worker work touches the same `_finalize_turn` body that Task 17 (Phase G) will rewrite — coordination required to avoid prematurely committing to Phase G semantics
- The 6 Mode A skipped tests will NOT unblock at Phase F (they need Task 17); only the 2 Mode B tests unblock here

**Workflow:** Use `subagent-driven-development` skill again — match Task 13/14's stage pipeline (implementer + spec-reviewer + code-quality-reviewer). Re-create todos for the workflow stages. Use sonnet for implementer unless Task 15 turns out to require Opus-tier architectural judgment (e.g., if it spans 5+ files with non-trivial threading concerns).

### 2. Carry-forward sweep candidates (later)

Open items at start of Phase F (13 total):

| Item | Landing point | Trigger |
|------|---------------|---------|
| C10.4 | Phase F worker-runner work | Worker-side `completion_origin` provenance wiring |
| 2 Mode B tests (`:2588` + `:793`) | Phase F worker-runner work | `update_parked_request` callsite wiring |
| 6 Mode A tests (`:1360` + `:1418` + `:1737` + `:2372` + `:617` + `:1062`) | Phase G Task 17 | Unknown-kind handling at L6 callsite |
| E13.2, E13.3 | Phase H | Phase H owns contracts.md + docstring trim |
| E14.1 | End-of-Packet-1 polish | `get_args` derivation refactor |
| A4, B6.x, B7.x, B8.x, C10.2-C10.3, A5 | End-of-Packet-1 polish | Per landing-point rows |

E13.1 was rerouted from "Task 14 cleanup" to "End-of-Packet-1 polish" by `d8f1911b` because Task 14's W7 confirmed scope was helper-only.

No immediate action — these are deferred by design.

## In Progress

Clean stopping point — Phase E Task 14 fully complete (3 implementation/test commits + 1 closeout-docs commit at `d8f1911b`), 978 tests passing + 8 newly skipped + 0 failed, all reviews ✅, all carry-forward items captured. No work in flight.

## Open Questions

None pending action. Three questions surfaced during review and were resolved:

1. **Should the implementer have flagged BLOCKED instead of DONE_WITH_CONCERNS when discovering the convergence-map L4 gap?** Resolved: yes, but not re-work-triggering. The analysis was correct; the decision was honest. Logged as process guidance for next dispatch.

2. **Should L4 be softened to NOT raise in `_project_request_to_view` (only in the helper)?** Resolved: no. The runtime guard's belt-and-suspenders intent for unknown-kind on JSONL replay paths is load-bearing for the long-term invariant. Softening would create a cruft path that future tasks might not remember to repair.

3. **Should `_finalize_turn` be modified to catch `UnknownKindInEscalationProjection` and handle unknown-kind captures gracefully?** Resolved: no. That's Phase G Task 17 territory per `phase-g-public-api.md:95-211`. Task 14's helper-only scope is preserved.

## Risks

### R1: Phase F Task 15 may pull Mode B skipped tests' assertions back into the wrong observable surface

**Concern:** When Phase F wires `update_parked_request` at capture time, the 2 Mode B skipped tests (`:2588`, `:793`) become unskippable. But the skip decorators were added with the expectation that the unskip would be a single-decorator-removal commit. If Phase F also moves the assertions to a different observable (e.g., a new helper that takes a different argument), the unskip becomes more invasive.

**Mitigation:** Phase F's plan should specify which exact `update_parked_request` callsite lands and what the resulting `_project_pending_escalation(job)` happy path looks like. The skip decorators preserve the test bodies; if a body needs to change post-Phase-F, it can be edited at unskip time without losing the original assertion intent.

**Severity:** Low — the unskip mechanic is well-defined and the skip reasons cite the specific unblock condition.

### R2: Phase G Task 17's unknown-kind handling may introduce a third failure mode

**Concern:** The 6 Mode A skipped tests assume Task 17 will route unknown-kind captures gracefully (terminalize the job, raise a synthetic null-projection variant, or wrap the L4 raise into a Phase G abort signal). If Task 17's actual mechanism is different (e.g., synchronously coercing unknown-kind to one of the three escalatable kinds, which would violate the spec's belt-and-suspenders intent), the skip reasons become inaccurate.

**Mitigation:** Task 17's dispatch packet should explicitly cite the 6 Mode A skipped tests in scope as unblock targets and verify the mechanism aligns with their assertion intent. Skip reasons can be updated in Task 17's closeout-docs commit if the mechanism shifts.

**Severity:** Medium — Task 17 is in the future; the alignment requires deliberate handoff between phases.

### R3: Convergence-map drafting may continue to miss transitive call-graph effects

**Concern:** The convergence-map L4 gap (audit only the explicit signature-change callsite, miss other callers) is a generalizable trap that's now captured in the closeout-docs entry. But future shape-rewrite tasks may still walk into it if the drafter forgets to enumerate ALL callers.

**Mitigation:** Add "audit ALL callers in the call graph for any helper modified" as a standing W item in future dispatch packets. The grep pattern `grep -rn "self\._<helper_name>\|controller\._<helper_name>" packages/.../server/` should be a pre-dispatch checklist item.

**Severity:** Medium — recurring trap, but the rule is now captured.

## References

- **Branch:** `feature/delegate-deferred-approval-response` @ `d8f1911b`
- **Phase E plan (Task 14):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-e-serialization-projection.md` (lines 190-477)
- **Phase F plan (Task 15 + 16 — next):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md`
- **Phase G plan (Task 17 owns Mode A unblock):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md` (lines 75-211)
- **Phase H plan (Task 20 owns poll catch+signal):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-h-finalizer-consumers-contracts.md` (lines 325-446)
- **Carry-forward tracker:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md`
- **Design spec:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`
- **Phase E Task 14 commits:** `becfc316` (feat) → `65f270ab` (closeout 1) → `b66d838f` (closeout 2) → `d8f1911b` (closeout-docs)
- **Phase E Task 13 closeout-docs (style reference):** `f0ea603b`
- **Phase D Task 12 closeout-docs (style reference):** `bf3f8b19`
- **Prior session handoff (resumed_from):** `docs/handoffs/archive/2026-04-25_11-40_phase-e-task-13-complete-task-14-next.md`
- **`_project_request_to_view` callsites (Task 17 will modify the second):**
  - `delegation_controller.py:1009` (inner-projector for `_project_pending_escalation`)
  - `delegation_controller.py:1644-1650` (`_finalize_turn` synchronous escalation return)
- **Mode A skipped tests (Phase G Task 17 unblock):** `test_delegation_controller.py:1360, 1418, 1737, 2372`; `test_delegate_start_integration.py:617, 1062`
- **Mode B skipped tests (Phase F/G unblock):** `test_delegation_controller.py:2588`; `test_delegate_start_integration.py:793`

## Learnings

### L1: Convergence-map drafting must include a transitive-call-graph audit pass

**Mechanism:** When adding runtime guards or behavioral changes to a helper function, the convergence map must enumerate ALL callers in the call graph, not just the explicit signature-change callsite. Adding a runtime raise to `_project_request_to_view` silently changed every caller's behavior, including `_finalize_turn`'s synchronous escalation-return path.

**Evidence:** Task 14's L4 specified the new RAISE behavior of `_project_request_to_view` and L5 specified the signature change of `_project_pending_escalation`. The map's W3 enumerated 3 breaking tests (only those that go through `_project_pending_escalation` from `poll()`). The actual count was 8 — 5 additional tests broke because `_finalize_turn:1644-1650` calls `_project_request_to_view` directly. The implementer caught this during execution.

**Implications:** Future shape-rewrite or guard-addition tasks should include "audit ALL callers in the call graph" as a standing W item. The grep pattern `grep -rn "self\._<helper_name>\|controller\._<helper_name>" packages/.../server/` is a concrete pre-dispatch checklist item.

**Watch for:** Helpers called from multiple sites with different control-flow paths. The "fast path" callsite (e.g., `poll()`) is usually the explicit one; the "slow path" callsite (e.g., `_finalize_turn`) is the one that gets missed.

### L2: Per-test triage tables eat the worst defect class in shape-rewrite tasks

**Mechanism:** Without binding per-test dispositions before code is written, the implementer's natural attractor is "make the test pass" — which silently breaks the assertion's intent. Pre-locking dispositions in a triage table shifts the implementer's job from "decide what to do" to "execute the decision," which is calibrated for sonnet-tier judgment.

**Evidence:** Task 13 caught zero blanket migrations because the triage table was binding. Task 14's triage table caught the same defect class — but also surfaced the convergence-map L4 gap because the implementer's faithful attempt to execute the (c) disposition revealed it was unreachable. The triage table didn't prevent the gap, but it provided the structure for the implementer to recognize and report the gap.

**Implications:** Future shape-rewrite tasks should always include a per-test triage table. The table is the load-bearing artifact; the locks/watchpoints provide the conceptual frame, but the table provides the binding execution contract.

**Watch for:** Tasks that lack a triage table when one is needed. If three or more pre-existing tests have assertions that may shift under the rewrite, a triage table is mandatory.

### L3: Skip-reason fabrication is a recurring failure mode the rubric must defend against

**Mechanism:** When skipping pre-existing tests, implementers may fabricate sibling-test names as "partial coverage" because they remember the invariant should be covered somewhere but don't verify the specific test name. The fabrication creates false confidence about coverage continuity.

**Evidence:** Task 14's closeout-2 fixed two fabricated citations (`test_start_with_unparseable_request_creates_causal_record_status` and `test_decide_rejects_stale_request_id_after_escalation`). Both verified absent via grep. Both were caught by code-quality review (I1).

**Implications:** Skip-reason rubric must include "if you cite a sibling test for partial coverage, verify it exists via grep before committing." Code-quality reviewers should grep-verify every cited sibling. Honest "no current sibling coverage" framing is preferable to false confidence.

**Watch for:** Skip reasons that name a sibling test without a file:line reference. If the sibling has no anchor, it's likely fabricated.

### L4: Two-stage review converges on cleaner artifacts than single-stage review

**Mechanism:** Spec-compliance review verifies the implementer built what was asked. Code-quality review verifies what was built is well-built. The two stages catch different defect classes; compressing to single-stage loses coverage on whichever dimension wasn't reviewed.

**Evidence:** Task 14's spec review found nothing (correctly — implementation matched spec). Code review found 1 Important + 4 Minor. Two of the four Minor findings (M1 docstrings, M3 Mode B skip reasons) were declined; M2 was acceptable as-is; M4 was deferred to carry-forward. Important I1 (fabricated citations) drove closeout-2. Without code-quality review, the fabricated citations would have shipped.

**Implications:** Two-stage review is the load-bearing pipeline. Single-stage review (spec only) loses code-quality coverage; single-stage review (quality only) loses spec-compliance coverage. The cost (extra subagent invocation per task) buys real defect-density reduction.

**Watch for:** Tasks where one of the two reviews returns zero findings. That's signal — it means the OTHER review's defect class was the load-bearing one for this task. Don't compress the pipeline based on "this round was clean."

### L5: 3+1 closeout chain is canonical; 5+1 is acceptable but indicates symmetric-defect-class

**Mechanism:** The canonical closeout shape is `feat + 1 closeout-fix + 1 closeout-docs` (3 commits). Stretches to 4-5 commits are acceptable when iterative review surfaces multiple closeout-worthy issues, especially when the defect class has symmetric arms (Task 13's deny-arm + approve-arm dead-binding).

**Evidence:** Task 13's chain: 5+1 commits (feat + 4 closeout-fixes + 1 docs) due to symmetric arms. Task 14's chain: 3+1 commits (feat + 2 closeout-fixes + 1 docs) — closeout-1 was Pyright hygiene, closeout-2 was code-quality I1. No symmetric defect class.

**Implications:** Closeout chain length is signal. If a chain runs 6+ commits, the defect class likely has symmetric arms or the convergence map missed structural issues. If a chain runs 3-4 commits, the convergence map was tight.

**Watch for:** Chains that grow during review iterations. If closeout-3 surfaces a third issue, audit whether the convergence map's W items captured the defect class. If not, document the gap in closeout-docs (as Task 14 did with the L4 transitive-effects gap).

## Gotchas

### G1: `job.parked_request_id` is structurally unset in the current production path

`delegation_job_store.update_parked_request` exists at `:187` but has zero production callsites in `delegation_controller.py`. The new job-anchored `_project_pending_escalation` short-circuits at the unparked guard for every legitimate flow. **Phase F worker-runner work will wire `update_parked_request(job_id, captured_request.request_id)` at capture time.** Until then, `poll().pending_escalation` is structurally `None` for every legitimate flow.

### G2: D4 marks captured request `status="resolved"` BEFORE escalation returns

`_finalize_turn:1608-1610` calls `update_status(captured_request.request_id, "resolved")` before the `DelegationEscalation` return. So even if `parked_request_id` were wired, the tombstone guard (`request.status != "pending"` → None) would null out the projection in the interregnum. Both unparked and tombstone guards converge on None for the entire pre-Phase-G synchronous flow. **Do NOT "fix" this by reordering the D4 write — that's Phase G Task 18 territory.**

### G3: `_finalize_turn:1644-1650` calls `_project_request_to_view` directly

This is the load-bearing transitive callsite that Task 14's L4 guard introduced new RAISE behavior into. Under Task 14, every unknown-kind capture (e.g., `_permissions_request` producing `kind="unknown"`) now raises `UnknownKindInEscalationProjection` during `start()` or `decide()` execution itself. **Phase G Task 17 owns the unknown-kind handling at this callsite** — see `phase-g-public-api.md:95-211` for the spec.

### G4: `cast(EscalatableRequestKind, request.kind)` at line 985 is annotated-only

The cast is a Pyright narrowing aid at the construction site. The runtime guard at `:975-981` ensures only escalatable kinds reach this point, so the cast is structurally safe. **Do NOT remove the cast** — Pyright will fail without it. Do NOT add additional runtime checks alongside the cast — the guard above is the runtime invariant.

### G5: `pending_request_store_factory.insert(...)` doesn't exist; use `create()`

The plan template at §14.1 used `pending_request_store_factory.insert(request)`. The real API is `pending_request_store.create(request)` at `pending_request_store.py:29`. Future plans should use `create()` to avoid this trap.

### G6: `from typing import cast` was correctly added in Task 14 (production code only)

The unused-import trap from W6 was about the test file template; the production code legitimately needs `cast` for the L4 narrowing fix. **Do not drop the `cast` import from `delegation_controller.py`** — it's load-bearing.

### G7: Skipped tests preserve their bodies for one-decorator-removal unskip

When Task 17 (Mode A) or Phase F/G (Mode B) lands the unblock, unskipping is a single `@pytest.mark.skip(...)` decorator removal. **Do NOT modify the skipped test bodies during the unskip** unless the underlying assertion intent has shifted. If a body needs to change, that's a separate diff with its own review pass.

### G8: Convergence-map W items must be enumerated for ALL callers, not just signature-change callsites

This is the generalizable trap captured in Task 14's closeout-docs entry. **For future shape-rewrite or guard-addition tasks, include "audit ALL callers in the call graph for any helper modified" as a standing W item.** The grep pattern `grep -rn "self\._<helper_name>\|controller\._<helper_name>" packages/.../server/` is a concrete pre-dispatch checklist item.
