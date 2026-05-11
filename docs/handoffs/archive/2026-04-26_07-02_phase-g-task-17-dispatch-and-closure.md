---
date: 2026-04-26
time: "07:02"
created_at: "2026-04-26T07:02:37Z"
session_id: c34fbf7a-b27a-4f7c-b6dc-690be29f875a
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: c5829049
title: Phase G Task 17 dispatch + closure (T-20260423-02 Packet 1)
type: handoff
files:
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-17-convergence-map.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-17-dispatch-packet.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md
  - docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_async_integration.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - packages/plugins/codex-collaboration/tests/test_handler_branches_integration.py
---

# Phase G Task 17 dispatch + closure (T-20260423-02 Packet 1)

## Goal

Drive Phase G Task 17 of T-20260423-02 Packet 1 (Deferred-Approval Response) end-to-end: dispatch the `DelegationController.start()` rewrite for the async-decide model, oversee implementation through controller-mediated subagent-driven-development (implementer → spec reviewer → code-quality reviewer), adjudicate any blockers or unilateral decisions against the binding spec/convergence map, land the canonical 1+1+1 commit chain (feat + closeout-fix + closeout-docs), and save a handoff for resumption.

Task 17's substantive scope: replace the synchronous `_execute_live_turn(...)` call inside `start()` with the capture-ready handshake (`spawn_worker(...)` + `wait_for_parked(...)` + 5-variant `ParkedCaptureResult` dispatch), land 8 acceptance tests for the new variants, remove ~24 Bucket A skip decorators that were blocked on this rewrite, rename the shared deadlock-citation constant in test files, and update carry-forward state for the F16.2/Mode A/Mode B/L10 closures.

## Session Narrative

The session opened post-compact with the controller already mid-stream on Task 17 dispatch artifact drafting. The user had just performed a `/copy` review of an in-progress convergence map and dispatch packet, returning four reviewer-flagged blockers (3×P1, 1×P2) on the convergence map plus two code-shape traps in the dispatch packet's L4 helper skeleton.

**Phase 1 — Convergence map amendment rounds (multiple iterations).** The first amendment pass fixed: (a) L10 math inconsistency (mixed mechanism vs ownership counts), (b) closeout-docs Mode A/B contradiction (same lines marked as both close + defer), (c) W5 verification command misuse (`pytest -p no:randomly` disables the plugin rather than shuffling), (d) carry-forward "16 → 16" instability (L10 treated as standalone Open row when it lived inside Task 16 closeout narrative). Subsequent rounds caught: F16.2 / 35-test surface conflation (claimed "F16.2 closes 24 + 11" when F16.2 is only the 26-test entry; correct split is 18 close + 8 → G17.1), F16.2 row inconsistency (decide_rejects_* count off), "order-shuffle" wording lingering in pre-dispatch checklist after W5 body had been corrected, and a final "Net change paragraph" drift moving 11 tests into G17.1 instead of correctly stating 8 F16.2 → G17.1 with 3 Mode A staying under Mode A row.

**Phase 2 — Dispatch packet drafting + review.** Drafted a ~330-line dispatch packet modeled on Task 16's 212-line precedent. User caught two code-shape traps in the L4 skeleton: (P1) Parked-arm wrong call order — the live `_project_pending_escalation(self, job: DelegationJob)` signature at `delegation_controller.py:1581-1583` takes the JOB, not the request_id, so the skeleton needed `job = self._job_store.get(job_id)` → `assert job is not None` → `_project_pending_escalation(job)`; (P2) `except Exception` too broad — should catch `UnknownKindInEscalationProjection` specifically (the helper docstring at `:1587-1593` documents this as the exception it re-raises for invariant violations). Cross-document fix: also updated convergence map L4 lock to spell out call order (a)-(e) and explicitly prohibit bare `except Exception:`.

A subsequent user round caught two more wording bugs in the Bucket B mechanics: (P1) the dispatch packet pre-state still claimed all 11 Bucket B decorators were `_TASK_17_DEADLOCK_REASON`-backed, but only 8 were constant-backed — the other 3 are Mode A callsite-specific reasons (`test_delegation_controller.py:1761`, `:2406`; `test_delegate_start_integration.py:1077`); a constant-rename-only pass would leave those 3 stale and the 11-retention audit would return 8 instead of 11. (P2) Same misclaim in the convergence map L6 lock. Final round: user caught that I'd labeled the 6 constant-backed Bucket B decorators in `test_delegation_controller.py` as "decide_rejects_* and start-flow" — but those are Bucket A REMOVAL classes; the 6 Bucket B retentions are decide-mechanism tests at `:1716`, `:1814`, `:1860`, `:2162`, `:2464`, `:2516`. Defensive NOTE added to the dispatch packet to prevent the inverse confusion.

**Phase 3 — Implementer dispatch + BLOCKED-1.** Dispatched `task-17-implementer` (general-purpose, sonnet, background) with the full ~336-line dispatch packet body. Agent reported BLOCKED after partial implementation: the L10 barrier test + 3 Mode A unknown-kind tests in Bucket A could not pass because `_finalize_turn` routes `interrupted_by_unknown=True` cases through `_project_request_to_view`, which raises `UnknownKindInEscalationProjection` for `kind="unknown"` requests. The implementer correctly identified that the W2 watchpoint ("Do NOT modify `_finalize_turn` body — Phase H Task 19 owns the Captured-Request Terminal Guard rewrite") was over-broad: spec `design.md:1738-1808` defines the Captured-Request Terminal Guard as the cancel/timeout/decide-success terminal mapping (one-snapshot rule, Request-to-job mapping table) — a SEPARATE concern from spec `design.md:1705-1736`'s Unknown-kind contract change at `:1473`/`:1482-1510`. The test docstring at `test_handler_branches_integration.py:547-549` directly attributed the carve-out to Task 17.

Adjudication: implementer correct. W2 narrowed to scope only the Captured-Request Terminal Guard logic; new L11 lock added to the convergence map specifying the required code shape (`if interrupted_by_unknown: final_status="unknown"` / `elif _CANCEL_CAPABLE_KINDS: final_status="needs_escalation"` split, with fall-through to existing non-escalation return at `:1512-1517`). Constrained the implementer's suggested over-aggressive `if interrupted_by_unknown: return updated_job` shape (would skip post-turn cleanup) to the spec-prescribed shape that flows through `_emit_terminal_outcome_if_needed` + runtime release + session close. Also flagged a new diagnostic at `delegation_controller.py:892` (Pyright "Type analysis indicates code is unreachable") for investigation. Sent unblock via SendMessage to agent ID `a26933d8ee4731697` (agent name binding had released after BLOCKED, so used the ID).

**Phase 4 — Implementer DONE with 3 unilateral decisions.** Feat commit `8dd15971` landed with 999 passed / 14 skipped (target was 1000 / 13). Implementer self-reported three substantive scope decisions made unilaterally instead of via the dispatch contract's preferred BLOCKED+question pattern: (Note 4) reclassification of `test_start_post_turn_finalization_failure_marks_job_unknown_and_cleans_up` from Bucket A to Bucket B; (Note 5) assertion-shape updates across multiple Bucket A tests for deferred-escalation semantics (`agent_context=None`, request status `pending`, escalation audits deferred); (Note 6) Mode A test re-asserted as `DelegationEscalation` instead of `DelegationJob(status="completed")`. Verified spec evidence: spec `design.md:785-797` explicitly mandates `agent_context=None` on Parked path ("the worker has not finalized its turn yet — it is blocking on `registry.wait(rid)`"); reclassified test sabotages 2nd `journal.append_audit_event` call (escalation audit inside `_finalize_turn`) which under async model only runs after `decide()` calls `commit_signal()` — genuinely unreachable from `start()` alone.

User adjudicated: validate retroactively (substantive evidence is decisive); record process precedent in convergence map; treat assertion-shape updates as a convergence-map gap (L10 underspecified) rather than implementer process violation; treat reclassification as a real process miss but accept the technically correct call.

**Phase 5 — Convergence map amendment for post-L13 truth.** Multiple amendment rounds: (1) added L11 (D4 carve-out specification) + L12 (assertion-shape obligation with 5-row spec-authority table) + L13 (Bucket A→B reclassification with process-precedent note); narrowed W2 to Captured-Request Terminal Guard logic only; added Post-implementer adjudication record section at end of doc with full provenance for all three implementer decisions plus diagnostics adjudicated. (2) Round-2 fixes per user review: per-test triage table still listed `:1522` under Bucket A; L1 + L6 still cited dispatch-time 24/11 counts as binding; out-of-scope Task 18 removal row still said "11 decorator removals"; W5 prose still cited "newly unskipped 24 tests"; live-anchor header didn't label HEAD as pre-feat. All updated. (3) Round-3 fix: pre-dispatch checklist W5 line still cited "newly-unskipped 24 tests" (the prose body had been fixed but the checklist item was missed). All counts now reconcile: 23 Bucket A removals + 12 Bucket B retentions + 9 G17.1 + 12 Task-18 future removals + 999 passing / 14 skipped.

**Phase 6 — Spec reviewer + code-quality reviewer chain.** Dispatched `task-17-spec-reviewer` (general-purpose, sonnet, background) with a binding-authority brief: validate feat commit `8dd15971` against the AMENDED convergence map. Returned DONE with full L1-L13 + W1-W13 conformance verified at file:line citations, plus 2 forwarded notes (L13 stale body assertions + StartWaitElapsed direct-helper invocation). Dispatched `task-17-code-quality-reviewer` (general-purpose, sonnet, background) with explicit boundary: code shape only, NOT contract conformance; CLAUDE.md style conventions as binding rather than convergence map. Returned DONE with 3 P3 findings (import order; test section numbering 1, 2, 3, 5, 4, 4 instead of 1, 2, 3, 4, 4, 5; stale comment + weak assertion in E2E test) + triage on both forwarded notes (Note 1 → docstring extension; Note 2 → leave as-is) + 1 noted optional cleanup (unused `repo_root.mkdir()` in 5 of 8 dispatch-direct tests).

**Phase 7 — Fix commit + closeout-docs.** Dispatched implementer (resumed via agent ID) for `dc90c1d9` (closeout-fix): 3 P3 fixes + Note 1 docstring extension + 5/5 optional `repo_root.mkdir()` cleanup. Suite preserved exactly (999/14 → 999/14, 18.80s wall-clock); W3 grep returned 6. Then dispatched implementer again for `c5829049` (closeout-docs): `carry-forward.md` updates per Phase F precedent + `task-17-convergence-map.md` (399 lines) + `task-17-dispatch-packet.md` (364 lines) staged as new files. Verified empty `git diff --stat HEAD~1..HEAD -- packages/` (docs-only commit). Task 17 chain closed.

**Phase 8 — Handoff (this).** User caught one final P3 archival banner observation on the dispatch packet (lacks "superseded by post-L13 counts" label) — deferred to Task 18 dispatch packet drafting work where the directory will be touched anyway. User chose A then B in this session (memory update + Task 18 dispatch packet drafting), then changed mind to handoff-only.

## Decisions

### Decision 1: Validate implementer's BLOCKED-1 D4 carve-out claim retroactively → narrow W2 + add L11

**Choice:** W2 narrowed in convergence map from blanket "Do NOT modify `_finalize_turn` body" to "Do NOT modify `_finalize_turn`'s Captured-Request Terminal Guard logic"; L11 lock added specifying the spec-mandated D4 carve-out for unknown-kind paths with required code shape, hard bounds, and the 4 unblocked Bucket A tests it enables.

**Driver:** Implementer hit a real W2 boundary that prevented unblocking 4 Bucket A tests (1 L10 barrier + 3 Mode A unknown-kind tests). Investigation confirmed the W2 was over-broad — its rationale ("Phase H Task 19 owns the Captured-Request Terminal Guard rewrite") referred to a SPECIFIC piece of Task 19 work (the cancel/timeout terminal mapping at spec `design.md:1738-1808`), not all `_finalize_turn` edits. Spec `design.md:1705-1736` (§Unknown-kind contract) explicitly attributes the `:1473`/`:1482-1510` line edits to Packet 1; spec line 1801 says the unknown-kind path "passes through the guard without firing", confirming logical separation.

**Alternatives:**
1. Keep W2 as-is and reclassify the 4 affected tests as Bucket B (defer to Task 19) — semantically wrong; Task 19 owns a different concern.
2. Approve the implementer's suggested `if interrupted_by_unknown: return updated_job` shape — over-aggressive; would skip `_emit_terminal_outcome_if_needed` + runtime release + session close.
3. Approve the spec-prescribed shape (chosen) — `if/elif` split that sets `final_status="unknown"` and falls through to existing non-escalation return.

**Rejection reasons:** (1) violates spec authority (Unknown-kind contract is Packet 1 work, not Task 19); (2) violates spec line 1726 explicit requirement to flow to existing non-escalation return at `:1512-1517`.

**Trade-offs:** Forces a controller adjudication mid-stream (~30 min round trip); creates a precedent that watchpoints can be narrowed when the rationale is shown to be over-broad relative to the actual rule. Long-term value: convergence map's W2 is now correctly scoped; future tasks won't repeat the over-broad framing.

**Confidence:** Very high. Spec evidence decisive across two independent sections (§Unknown-kind contract + §Captured-Request Terminal Guard); test docstring at `test_handler_branches_integration.py:547-549` independently attributed the carve-out to Task 17.

**Reversibility:** Fully reversible if spec evidence had been ambiguous — would have reclassified the 4 tests to Bucket B. After implementer applied the L11 fix and tests passed, reversibility cost is high (would need to revert + re-skip + re-classify).

**Change triggers:** If Task 19's actual implementation reveals the carve-out interacts unexpectedly with the Captured-Request Terminal Guard rewrite, may need to revisit. Spec authority hierarchy permits this (live code is bedrock).

### Decision 2: Validate L13 reclassification retroactively despite process violation

**Choice:** Accept the implementer's unilateral Bucket A→B reclassification of `test_start_post_turn_finalization_failure_marks_job_unknown_and_cleans_up` (`test_delegation_controller.py:1522`); record as L13 in convergence map with explicit "process precedent for future tasks" note: "future implementers must report BLOCKED for ANY bucket reclassification — even when the substantive reasoning is decisive — so that the controller updates the convergence map's binding counts BEFORE the feat commit lands."

**Driver:** Test sabotages the 2nd `journal.append_audit_event` call (escalation audit inside `_finalize_turn`); under async model, `_finalize_turn` runs on worker thread AFTER `decide()` calls `commit_signal()` to resume — sabotaged failure path is genuinely unreachable from `start()` alone. Substantive correctness verified by reading test body at `:1524-1596` and confirming the sabotage logic.

**Alternatives:**
1. Push back: revert the feat commit and require BLOCKED resubmission (strongest process enforcement; high cost for known-correct technical answer).
2. Split: keep assertion rewrites, revert only the reclassification (mostly ceremony if reclassification is correct).
3. Accept silently (fastest; bad precedent, normalizes "DONE_WITH_CONCERNS + unilateral decision" path).
4. Accept retroactively with explicit adjudication + convergence map updates before spec review (chosen).

**Rejection reasons:** (1) disproportionate given decisive substantive validation; (2) operationally wasteful churn; (3) undermines dispatch contract that explicitly forbade this pattern.

**Trade-offs:** Sets a "you can be retroactively forgiven for a unilateral decision if the technical answer is correct" precedent. Mitigated by recording the L13 process-precedent note explicitly inside the convergence map, NOT silently. The user's framing was decisive: "process precedent dominates implementation velocity only when the technical answer is uncertain."

**Confidence:** High. Spec evidence (§`reserve()` + `commit_signal()` protocol) + test sabotage logic both decisive.

**Reversibility:** Reversible at high cost (would require Task 18 to re-classify the test back if it turns out the failure path IS reachable through `decide()`-resume flow). Low probability — the test's setup explicitly arranges for the sabotage to fire on the 2nd call which only happens during `_finalize_turn`.

**Change triggers:** If Task 18's `decide()` rewrite reveals the test can be unblocked without `reserve+commit_signal`, may need to revisit reclassification. Low probability per spec.

### Decision 3: Treat L12 assertion-shape updates as convergence-map gap, not implementer process violation

**Choice:** Accept the implementer's assertion-shape updates across multiple Bucket A tests for deferred-escalation semantics; record as L12 in convergence map with a 5-row spec-authority table for each new assertion shape; document the original L10's incompleteness ("L10 was incomplete: it specified the decorator-removal mechanism but did NOT note that the affected tests' BODY assertions encode the pre-Packet-1 synchronous-model contract").

**Driver:** Removing the skip decorators on tests originally written under the synchronous model FORCED a choice: update assertions or leave the tests failing. The implementer correctly chose to update, citing spec §Capture-ready handshake. Spec evidence verified at `design.md:785-797` ("the worker has not finalized its turn yet — it is blocking on `registry.wait(rid)`"). Pushing the implementer to BLOCKED for every assertion update across ~6 tests in one file with consistent spec-grounded shape changes would be ceremony.

**Alternatives:**
1. Treat as process violation requiring revert + BLOCKED (same arguments as Decision 2; rejected on same grounds).
2. Accept silently without recording the L10 gap (would let the same gap repeat in Tasks 18-22).
3. Accept + record as L12 with forward-looking rule (chosen): "assertion shapes that DIRECTLY mirror a single explicit spec section are implementer-discretion within the dispatch contract; assertion shapes that ADD new behavior or test new spec sections REQUIRE BLOCKED + adjudication."

**Rejection reasons:** (1) operationally wasteful; (2) loses the lesson for future tasks.

**Trade-offs:** L12 introduces a discretionary gradient that requires implementer judgment ("does this shape directly mirror a single spec section?"). Mitigated by the 5-row authority table making each assertion category traceable to a specific spec line range.

**Confidence:** Very high. Spec evidence is unambiguous; the only judgment call was whether to treat as forced-by-context (no violation) or unilateral-decision (process violation). User's adjudication was decisive: "convergence-map gap, not implementer violation."

**Reversibility:** L12 lock is documentation-only; can be tightened in future tasks if the discretionary gradient causes problems. Reversibility is asymmetric — the assertion changes themselves landed in `8dd15971` and would be expensive to revert.

**Change triggers:** If a future implementer abuses the L12 discretion (e.g., bulk-rewrites assertions in ways that don't directly mirror spec), tighten L12 to require BLOCKED for any non-trivial assertion-shape change.

### Decision 4: Option 1 (small fix commit) for the 3 P3 nits + Note 1 docstring + optional cleanup

**Choice:** Dispatch implementer to apply the 3 P3 findings (import order, test section numbering, stale comment + weak assertion) + Note 1 docstring extension + optional `repo_root.mkdir()` cleanup as a separate `fix(delegate): address Task 17 review (T-20260423-02 Task 17 closeout)` commit BEFORE the closeout-docs commit. Result: `dc90c1d9` (4 files touched, 999/14 preserved exactly, 18.80s wall-clock).

**Driver:** Matches the dispatch packet's anticipated 1+1+1 commit shape (feat + closeout-fix + closeout-docs); preserves clean commit discipline (closeout-docs stays pure-docs); converts cosmetic findings into actual code improvements rather than carry-forward debt; cost is low (4 small text edits + 5 cleanup edits = ~10 min implementer time).

**Alternatives:**
1. Bundle into closeout-docs commit (mixes test-code edits into a docs commit; violates clean commit discipline).
2. Punt to carry-forward (cleanly separates concerns but ships 3 known nits with reviewer-specified fixes).
3. Separate fix commit (chosen).

**Rejection reasons:** (1) violates commit hygiene; (2) ships known nits as debt.

**Trade-offs:** Adds one more agent dispatch round (low cost). Strengthens the canonical 1+1+1 shape for future tasks (high value).

**Confidence:** High. The fixes were surgical and reviewer-specified at file:line precision.

**Reversibility:** Trivially reversible (small commit; no behavioral changes — verified by suite count match).

**Change triggers:** None foreseeable — fix commit landed cleanly with no scope drift.

### Decision 5: Convergence map amendment strategy — historical layers preserved with explicit "originally / post-L13" framing

**Choice:** When amending the convergence map post-feat, update the binding executable surfaces (Locks, Watchpoints, triage tables, acceptance criteria) to reflect post-L13 truth (23 / 12 / 9), but PRESERVE the historical prose layer (pre-dispatch warning at line 377, etc.) with explicit "(historical, original counts)" labels and adjacent post-feat amendment annotations. Three primary anchors for post-L13 truth: L13 itself, the post-feat amendment line, and the Post-implementer adjudication record.

**Driver:** A reader needs to be able to reconstruct (a) what the implementer was given as scope at dispatch time, (b) what was adjudicated post-feat, and (c) what the current binding truth is. Erasing the dispatch-time prose would lose the audit trail; rewriting every count without dual-framing would conflate the two eras.

**Alternatives:**
1. Erase all dispatch-time framings; rewrite to post-L13 only (loses audit trail; spec reviewer can't tell what the implementer was constrained by).
2. Add "post-L13:" annotations to every historical mention (visually noisy; doesn't add correctness because the original framings were accurate at dispatch time).
3. Side-by-side "originally / post-L13" framing (chosen): keeps both eras visible; reader can pattern-match to either layer depending on their question.

**Rejection reasons:** (1) audit-trail loss; (2) noise without value.

**Trade-offs:** Requires multiple amendment rounds to catch every count-bearing surface (took 3 review rounds with the user). Mitigated by exit-pass grep discipline (broad regex catches stale "newly-unskipped 24" / "covers all 11" patterns).

**Confidence:** High. The pattern reconciles in the final state.

**Reversibility:** Fully reversible — could collapse the dual-framing if it becomes overhead, but no signal that it does.

**Change triggers:** If future tasks have NO post-feat adjudications, the simpler single-layer framing returns naturally — no need for dual-framing prophylactically.

### Decision 6: Defer dispatch packet archival banner to Task 18 dispatch packet drafting

**Choice:** Do not open a 5th commit on the Task 17 branch for a one-line archival banner ("This packet records the dispatch-time prompt; post-feat amendments live in `task-17-convergence-map.md`"). Fold the banner into Task 18 dispatch packet drafting work (which will reference Task 17's artifacts and naturally touch the same directory).

**Driver:** Cost-benefit asymmetry — opening a 5th commit for one sentence is over-engineering; the convergence map IS the binding artifact and a future reader who picks up the dispatch packet cold WITHOUT also reading the convergence map is an unlikely reader pattern. User explicitly framed this as discretionary.

**Alternatives:**
1. Standalone archival commit `docs(delegate): add archival banner to Task 17 dispatch packet` (cleanest scope; over-engineering).
2. Amend `c5829049` to add the banner (forbidden by repo rules — no amends to pushed commits, even to local branches we may push later).
3. Defer to Task 18 packet drafting (chosen).
4. Leave forever (banner gap small but accumulating; not zero cost).

**Rejection reasons:** (1) over-engineering; (2) repo rule violation; (4) accumulating debt that's cheap to retire when natural opportunity arises.

**Trade-offs:** Risk that Task 18 doesn't happen for a long time and the dispatch packet sits without the archival banner. Mitigated by the user's confirmation "I would not reopen the Task 17 chain for that unless you want the artifact to be self-explanatory when read in isolation."

**Confidence:** Medium-high. Defensible if Task 18 happens within weeks; weaker if it slips months.

**Reversibility:** Fully reversible — standalone commit can be added at any point.

**Change triggers:** If a future reader is observed to be misled by the dispatch packet (e.g., asks "why does the dispatch packet say 24/11 when the convergence map says 23/12?"), elevate to higher priority.

## Changes

### Branch state at session end

```
c5829049  docs(delegate): record Phase G Task 17 closeout (T-20260423-02)
dc90c1d9  fix(delegate): address Task 17 review (T-20260423-02 Task 17 closeout)
8dd15971  feat(delegate): rewrite start() with capture-ready handshake (T-20260423-02 Task 17)
f3cfa61a  docs(delegate): record Phase F Task 16 closeout (T-20260423-02)  ← base / pre-session HEAD
```

Branch: `feature/delegate-deferred-approval-response`. 4 commits ahead of base; clean working tree.

### Commit `8dd15971` — feat (start() rewrite)

**Production:** `delegation_controller.py` (+170 lines) — `start()` rewritten at `:386` to replace synchronous `_execute_live_turn(...)` call with `spawn_worker(...)` + `wait_for_parked(...)` + `_dispatch_parked_capture_outcome(...)`; new helper added with exhaustive `match` over 5 `ParkedCaptureResult` variants + `case _: assert_never(outcome)` final arm; L11 carve-out at `_finalize_turn` for `interrupted_by_unknown` routing; `START_OUTCOME_WAIT_SECONDS: float = 30` module constant; 6 new imports from `.resolution_registry` extending `:102`; `from .worker_runner import spawn_worker` added; `from typing import assert_never` added to existing typing import line.

**Tests:** New file `test_delegate_start_async_integration.py` (+365 lines, 8 acceptance tests covering all 5 variants + 2 invariant-violation sub-cases + 1 reason-preservation); 23 Bucket A skip decorators removed (post-L13 — originally 24 planned); `_TASK_17_DEADLOCK_REASON` renamed to `_TASK_18_DECIDE_SIGNAL_REASON` in both `test_delegation_controller.py:43` and `test_delegate_start_integration.py:31` with reason text rewritten per L6; 3 callsite-specific Mode A Bucket B decorators explicitly rewritten to use the new constant; assertion-shape updates across multiple Bucket A tests for deferred-escalation semantics per L12 (5 categories: `agent_context=None` on Parked, request status `pending`, escalation audits deferred, unknown-kind paths return `DelegationJob`, `request_user_input` parks).

**Diffstat:** 5 files, +710 / −234.

### Commit `dc90c1d9` — fix (closeout-fix)

**4 files touched** (all minor):
- `delegation_controller.py:113-114` — F1: swapped `from .runtime import` and `from .worker_runner import spawn_worker` so `runtime` precedes `worker_runner` (alphabetical).
- `test_delegate_start_async_integration.py:171-269` — F2: swapped variant 5 (StartWaitElapsed) and variant 4 (WorkerFailed) section blocks so file reads 1 → 2 → 3 → 4 → 5 (matches branch-matrix order).
- `test_delegate_start_integration.py:605-606` — F3: replaced stale comment "agent_context captured (may be None but key must be present)" + weak assertion `assert "agent_context" in payload` with `# Deferred-escalation: agent_context=None for the Parked path.` + `assert payload["agent_context"] is None`.
- `test_delegation_controller.py:1531-1538` (docstring of `test_start_post_turn_finalization_failure_marks_job_unknown_and_cleans_up`) — Note 1: appended sentence "Body assertions use the `worker_failed_before_capture` fallback shape, which is NOT the expected Task-18 failure path; the entire body must be rewritten when Task 18 unblocks this test."
- `test_delegate_start_async_integration.py` — Optional cleanup: removed unused `repo_root.mkdir()` calls in 5 of 5 dispatch-direct tests (all 5 verified mechanical).

**Verification:** Suite preserved exactly (999/14 → 999/14, 18.80s wall-clock); W3 grep returned 6.

### Commit `c5829049` — docs (closeout-docs)

**3 files staged:**
- `carry-forward.md` (+44 lines net) — new section "### From Phase G Task 17 + closeouts" added between Task 16 entry (line 188) and `---` separator (line 190); Open-items entries updated for F16.2 (in-place annotation: "[Split per Task 17 — see closeout entry]"), F16.1 (re-affirmed unchanged), G17.1 added (9 F16.2 Bucket B tests), RT.1 added (`runtime.py:270` Pyright); Mode A/B handled inside the closeout narrative (they were not standalone Open rows in this file — verified via grep).
- `task-17-convergence-map.md` (NEW, 399 lines) — staged as-is from working artifact (post-feat amendments + L11/L12/L13 + W2 narrowing + Post-implementer adjudication record at end).
- `task-17-dispatch-packet.md` (NEW, 364 lines) — staged as-is from working artifact (dispatch-time framing preserved).

**Verification:** Empty `git diff --stat HEAD~1..HEAD -- packages/` (docs-only confirmed); suite still 999/14, 18.25s.

## Codebase Knowledge

### `delegation_controller.py` (the surgical target)

**Pre-feat anchors (HEAD `f3cfa61a`):** `start()` at `:386`; synchronous `_execute_live_turn(...)` callsite inside `start()` at `:737`; `decide()` body at `:2287` (W1 — Phase G Task 18 territory); `_finalize_turn` def at `:1611`; `_finalize_turn` `_CANCEL_CAPABLE_KINDS` branch entry at the live anchor (line numbers shifted post-feat to `:2367`); `_execute_live_turn` callsite at `:2484` (decide-resume — W1 — Task 18 territory); legacy `DelegationEscalation` construction site at `:2240` (W13 — stays in service for decide-resume until Task 18 retires it); `_project_pending_escalation(self, job: DelegationJob) -> PendingEscalationView | None` at `:1581-1583`; `class UnknownKindInEscalationProjection(Exception)` at `:191`; existing `poll()` callsite pattern at `:1660-1663` (model for L4 Parked-arm call order); `self._registry: ResolutionRegistry = ResolutionRegistry()` initialized in `__init__` at `:384`.

**Post-feat anchors (HEAD `8dd15971`):** `start()` body shifted; `_dispatch_parked_capture_outcome` helper at lines ~760-895; `START_OUTCOME_WAIT_SECONDS: float = 30` at `:119`; `case _: assert_never(outcome)` at `:892`; L11 carve-out at `_finalize_turn:2367-2374`; legacy `DelegationEscalation` construction site shifted to `:2389`; W3 sentinel raises at lines 993, 1129, 1242, 1538, 1602, 1648 (count = 6, invariant preserved). Live `_project_pending_escalation` ref point shifted; spec reviewer cited the post-feat anchor at line 2644 for the decide-resume callsite.

### `worker_runner.py`

`spawn_worker(...)` exists from Task 16 work (added at module level in this Task 17 import); `_WorkerRunner.run` catches `Exception` and calls `announce_worker_failed(error=that_exception)`; daemon=True on worker thread at `:113` (W5 mitigation — prevents process-exit blocking).

### `resolution_registry.py`

`wait_for_parked(job_id, timeout_seconds=...)` blocks until one of 5 `ParkedCaptureResult` variants is signaled; `signal_internal_abort(request_id, reason=...)` wakes a parked worker with `InternalAbort`; daemon=True on per-request timer threads at `:202-206` (W5 mitigation).

### `ParkedCaptureResult` variants (the central artifact for Task 17)

5 dataclass variants imported from `.resolution_registry`:
1. `Parked(request_id)` — worker emits `announce_parked` from inside `_server_request_handler` after capture; main thread returns `DelegationEscalation(job, pending_escalation, agent_context=None)` per L4. Two invariant-violation sub-cases (projection raises `UnknownKindInEscalationProjection` OR returns `None`) require signal-then-raise per L8 with reason `parked_projection_invariant_violation`.
2. `TurnCompletedWithoutCapture()` — `_WorkerRunner.run` fallthrough; main thread returns `_job_store.get(job_id)` (typically `status="completed"`).
3. `TurnTerminalWithoutEscalation(job_status, reason, request_id)` — worker emits from unknown-kind interrupt-success path (Task 16 L10 + plan Step 16.3); main thread returns `_job_store.get(job_id)` (`status="unknown"`).
4. `WorkerFailed(error)` — `announce_worker_failed(error=exc)`; main thread raises `DelegationStartError(reason=preserved or "worker_failed_before_capture", cause=exc)` per L7 reason-preservation rule.
5. `StartWaitElapsed()` — start-wait budget elapsed; main thread logs warning + returns `_job_store.get(job_id)` (status="running").

### Test files

| File | Role |
|---|---|
| `test_delegation_controller.py` (pre-existing, 303 lines changed) | Unit tests for controller; constant defined at `:43`; multiple Bucket A removals + 6 Bucket B retentions (F16.2 decide-mechanism + 2 Mode A callsite-specific) |
| `test_delegate_start_integration.py` (pre-existing, 95 lines changed) | E2E tests through MCP dispatch; constant defined at `:31`; 3 Bucket A + 3 Bucket B retentions (2 F16.2 decide-E2E + 1 Mode A callsite-specific) |
| `test_handler_branches_integration.py` (pre-existing, 11 lines changed) | Worker-handler branch tests; F16.1 decorators at `:161`, `:179` UNTOUCHED (W8 — Phase H Task 19); L10 barrier decorator at `:539` removed in Bucket A |
| `test_delegate_start_async_integration.py` (NEW, 365 lines) | Acceptance tests for the new ParkedCaptureResult dispatch; uses module-local `_build_controller` from `tests.test_delegation_controller` (W4); 8 tests covering all 5 variants + 2 invariant-violation sub-cases + 1 reason-preservation |

### Spec references

| Section | Lines | Authority for |
|---|---|---|
| §Capture-ready handshake | `design.md:659-910` | Foundational Task 17 spec; spawn_worker, wait_for_parked, 5 variants, invariant-violation handling |
| §Deferred-escalation `agent_context=None` | `design.md:785-797` | L12 assertion-shape category 1 |
| §DelegationStartError reasons | `design.md:622-657` | Canonical reason strings; reason-preservation rule for `WorkerFailed` |
| §Unknown-kind contract | `design.md:1705-1736` | L11 carve-out authority; line edits at `:1473`, `:1482-1510`, worker path |
| §`_finalize_turn` Captured-Request Terminal Guard | `design.md:1738-1808` | W2 narrowed scope (Task 19 territory; one-snapshot rule, Request-to-job mapping table) |
| §`reserve()` + `commit_signal()` protocol | (search design doc) | L13 reclassification authority; Task 18 mechanism |

### Carry-forward state

| Item | Pre-session | Post-session |
|---|---|---|
| F16.2 (Phase G Task 17 unblock surface — 26 tests) | Open | Split per Task 17: 17 closed in Bucket A (10 start-flow + 7 decide-rejects); 9 moved to G17.1 (8 originally + 1 reclassified per L13) |
| Mode A (Phase E Task 14 closeout — 6 tests) | Open (narratively in Task 14 entry) | Partial closure: 3 close in Bucket A (`test_delegation_controller.py:1377`, `:1436`; `test_delegate_start_integration.py:628`); 3 defer to Task 18 (`:1761`, `:2406`; `:1077`) |
| Mode B (Phase E Task 14 closeout — 2 tests) | Open (narratively in Task 14 entry) | Fully closed: both in Bucket A (`test_delegation_controller.py:2626`; `test_delegate_start_integration.py:805`) |
| F16.1 (Phase F Task 16 closeout — 2 tests) | Open | Unchanged — Phase H Task 19 still owner |
| L10 barrier (Phase F Task 16 closeout — 1 test) | Open (in Task 16 closeout narrative) | Closed: decorator at `test_handler_branches_integration.py:539` removed |
| **NEW G17.1** (Phase G Task 18 unblock surface — 9 F16.2 Bucket B tests) | n/a | Open — Task 18 will close |
| **NEW RT.1** (`runtime.py:270` Pyright TurnStatus literal narrowing) | (Open Question pre-session) | Open carry-forward — end-of-Phase-G or end-of-Packet-1 typing polish |

## Context

**Project:** `claude-code-tool-dev` — monorepo for Claude Code extensions. Active work is in the `codex-collaboration` plugin at `packages/plugins/codex-collaboration/`.

**T-20260423-02 Packet 1 (Deferred-Approval Response):** Multi-task implementation reshaping the `DelegationController` API for the async-decide model. Pre-session state: Phases A-F complete (Tasks 1-16); session work was Phase G Task 17 = `start()` rewrite. Tasks 18 (`decide()` rewrite), 19 (`_finalize_turn` Captured-Request Terminal Guard), 20-22 (poll/discard/contracts.md) queued behind. Spec at `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` (~1800+ lines).

**Two-read protocol:** Controller drafts artifacts, user `/copy` reviews independently for issues, controller fixes, repeat until approved. Applied throughout this session to: convergence map (5+ rounds), dispatch packet (3 rounds), post-feat amendments (3 rounds).

**Subagent-driven-development workflow:** `superpowers:subagent-driven-development` mandates implementer + spec reviewer + code-quality reviewer chain (sequential). Per user's prior feedback memory `feedback_subagent_driven_development_meaning.md`: do NOT stop at implementer DONE.

**Dispatch contract pattern:** Self-contained agent prompts (subagents have no conversation memory); fresh-spawn-with-inherited-context the default; report DONE / BLOCKED / BLOCKED-WITH-FINDINGS rather than DONE_WITH_CONCERNS+unilateral; co-author trailer `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`; specific-file staging only (never `git add -A`); no amend / no skip pre-commit hooks.

**Agent name vs ID resolution:** Background agents addressable by NAME while running; once an agent reports DONE/BLOCKED and exits, the name binding releases. Internal agent ID persists — runtime can resurrect a completed agent's transcript and resume with a new message ("had no active task; resumed from transcript"). When continuing a previously-completed background agent, ALWAYS use the ID; the name will fail.

## Learnings

### L11/L12/L13 process precedents (worth persisting as feedback memories — see Next Steps)

1. **Bucket reclassification requires BLOCKED+question.** Future implementers must report BLOCKED for ANY bucket reclassification — even when the substantive reasoning is decisive — so that the controller updates the convergence map's binding counts BEFORE the feat commit lands. Recorded as L13 process precedent.

2. **Assertion-shape updates can be implementer-discretion if narrowly spec-mirrored.** Assertion shapes that DIRECTLY mirror a single explicit spec section (per L12's 5-row authority table) are implementer-discretion within the dispatch contract; assertion shapes that ADD new behavior or test new spec sections REQUIRE BLOCKED + adjudication. Recorded as L12 forward-looking rule.

3. **Watchpoint rationale-vs-rule asymmetry.** When a watchpoint cites a SPECIFIC piece of work as its rationale ("Task 19 owns the Captured-Request Terminal Guard"), the rule itself can be over-broad relative to the rationale ("Do NOT modify `_finalize_turn` body"). Implementer is empowered to flag this asymmetry as BLOCKED+question; controller can narrow the watchpoint with explicit carve-out. Recorded in W2 amendment.

### Drafting discipline — convergence map amendments

1. **Binding surfaces first, narrative layers second.** When amending a multi-section binding doc post-implementation, update the executable-source surfaces (Locks, Watchpoints, triage tables, acceptance criteria) BEFORE the explanatory sections. Reverse order produces docs where prose says X and binding tables say Y.

2. **Exit-pass grep with broad regex.** When sweeping for stale counts, broaden the regex beyond the primary noun ("Bucket A") to include verb forms ("removed", "retained", "newly-unskipped") and equation forms ("= 24", "+ 11"). Repeated discovery in this session: "newly-unskipped 24" escaped earlier sweeps because "Bucket A" wasn't adjacent.

3. **Side-by-side dual-framing for historical prose.** "Originally / post-L13 effective" pairing preserves the audit trail without misleading future readers. Explicit "(historical, original counts)" labels mark prose that is intentionally NOT updated.

### Drafting discipline — dispatch packets

1. **Pre-state accuracy is what makes post-state audits interpretable.** When the dispatch contract has a post-state audit (`grep ... expected N`), the pre-state description must be precise enough that the implementer doesn't conclude the audit is wrong when their natural mechanical action returns N-1 or N-2 instead of N.

2. **Defensive NOTE for inverse confusion.** When sub-class names overlap with category names (e.g., "decide_rejects_*" appears in both Bucket A and Bucket B contexts), include an explicit defensive note ("the `decide_rejects_*` decorators are Bucket A REMOVALS, not Bucket B retentions").

3. **Mission boundary stated FIRST.** Putting negative scope at the top of an agent prompt sets the lens through which the agent reads each task below. Verified across two dispatches: implementer DONE with zero scope drift on the fix commit (vs the feat commit's 3 unilateral decisions before this discipline was tightened).

### Spec-authority hierarchy

When sources conflict, higher-numbered authority defers to lower:
1. Spec sections (§Capture-ready handshake, §Unknown-kind contract, §reserve+commit_signal)
2. Phase plan body (`phase-g-public-api.md`)
3. Carry-forward (F16.2, Mode A/B, L10, etc.)
4. Live code at HEAD

Live code is bedrock; spec wins over plan.

### Reviewer chain works as designed

Spec reviewer + code-quality reviewer found different things (zero overlap in findings). Spec reviewer caught 0 contract defects + 2 hand-off observations; code-quality reviewer caught 3 P3 nits + actionable triage on both forwarded notes. The chain produces independent triage of edge cases that wouldn't surface from a single reviewer.

## Next Steps

### Recommended next-session priorities

1. **Memory updates (deferred from this session per user pivot to handoff-only).**
   - Persist L13 process precedent as feedback memory: "Bucket reclassification requires BLOCKED+question — future implementers must report BLOCKED for ANY bucket reclassification even when substantive reasoning is decisive, so the controller updates binding counts BEFORE feat commit lands."
   - Persist L12 forward-looking rule as feedback memory: "Assertion-shape updates mirroring a single explicit spec section are implementer-discretion within the dispatch contract; assertion-shape updates that ADD new behavior or test new spec sections REQUIRE BLOCKED + adjudication."
   - Update MEMORY.md current-focus from "T-07 RECONCILIATION COMPLETE" (stale) to "T-20260423-02 Packet 1 active; Phase G Task 17 landed (`8dd15971` + `dc90c1d9` + `c5829049`); Task 18 (`decide()` rewrite with `reserve()` + `commit_signal()`) next".

2. **Task 18 dispatch packet drafting (the big one).** Convergence map + dispatch packet for `decide()` rewrite. Inherits post-L13 carry-forward state: G17.1 = 9 F16.2 Bucket B tests + 3 Mode A defer = 12 Bucket B retentions to unblock. Should pre-bake L12 assertion-shape obligation into the convergence map from the start (avoid the L10 gap repeating). Read `phase-g-public-api.md:290-536` for Task 18 plan body. Spec authority: §`reserve()` + `commit_signal()` protocol. Estimated effort: 60-90 min for first draft + multiple two-read review rounds with user.

3. **Optional: Task 17 dispatch-packet archival banner.** When drafting Task 18 packet (which touches the same directory), add a one-line banner at the top of `task-17-dispatch-packet.md`: "Archival — this packet records the dispatch-time prompt; post-feat amendments live in `task-17-convergence-map.md`." Bundle into Task 18's docs commit; don't open a standalone commit.

### Lower-priority follow-ups

4. **PR-readiness check after Phase G complete.** Don't merge Task 17 alone — wait until Tasks 17+18 are both done so Bucket B retentions close in the same packet. Branch is now 4 commits ahead of main; long-running feature branch increases merge complexity.

5. **End-of-Phase-G or end-of-Packet-1 typing polish.** Address RT.1 (`runtime.py:270` Pyright TurnStatus literal narrowing) and the parallel test-side `_FakeControlPlane` Pyright issues at `test_delegation_controller.py:257, 2547, 2621, 2686, 2867, 2888, 3064, 3194, 3418` (latter could become "TT.1" carry-forward if not already tracked).

6. **Phase H planning** — Tasks 19 (`_finalize_turn` Captured-Request Terminal Guard), 20 (`poll()` UnknownKindInEscalationProjection catch), 21 (`discard()` admits canceled), 22 (`contracts.md` updates).

## In Progress

Nothing in flight. Task 17 chain is fully closed:
- All 4 commits landed on the branch (base + feat + fix + docs).
- All reviewer DONEs received.
- All convergence map amendments landed.
- All adjudications recorded in the convergence map's Post-implementer adjudication record.
- No open agent dispatches.

## Open Questions

1. **Memory update timing.** Should the L11/L12/L13 process precedents be saved as feedback memories now, or wait for the next reuse opportunity (Task 18 dispatch where they'll be referenced)? Argument for now: prevents decay, available immediately. Argument for waiting: forces verification that the precedents transfer to a new context before fossilizing them. User signaled "memory update" was acceptable in Option A but then pivoted to handoff-only — so it's not blocking, just queued.

2. **Task 18's L12 inheritance.** Task 18's `decide()` rewrite will trigger another wave of synchronous→async assertion updates. The L12 5-row authority table needs to be reviewed against Task 18's expected assertion-shape changes — are there NEW shape categories not covered by L12, or does the existing table fully capture what Task 18 will need? Open until Task 18 dispatch packet drafting begins.

3. **Branch strategy.** Should the branch wait for Tasks 17+18+19 all done before merging, or merge Task 17 standalone now and continue on a fresh branch for Task 18? Argument for waiting: G17.1 (9 Bucket B tests) is awkward to ship as "open" debt. Argument for merging now: 4-commit branch is already meaningful work; Task 18 can rebase. User likely has a preference; not asked yet this session.

4. **Codex consultation.** No Codex consultation happened this session — could be worth one at the Task 18 dispatch packet drafting stage to sanity-check the `reserve()` + `commit_signal()` protocol design before locking it in. Not required; flag for consideration.

## Risks

1. **Task 18's `decide()` rewrite will trigger another L10-class gap if not pre-baked.** Without explicit L12 inheritance in Task 18's convergence map, the same "decorator removal forces assertion-shape updates" gap will recur. Mitigation: Task 18 dispatch packet drafting MUST include L12 in its convergence map from draft 1.

2. **Pre-existing test-side Pyright issues accumulate.** `_FakeControlPlane` protocol mismatches + `_snapshots`/`inspection` attribute access errors at multiple lines in `test_delegation_controller.py` are pre-existing carry-forward, but the count grew from 3 to 9 across this session as the test surface expanded. Could become a blocking debt if not formally tracked. Recommend creating a TT.1 carry-forward item at end of Phase G.

3. **Long-running feature branch.** `feature/delegate-deferred-approval-response` is 4 commits ahead of main; adding Tasks 18+19+20+ extends this. Merge complexity scales with branch length. Mitigation: consider merging at Phase G boundary (after Task 18 closes G17.1) rather than waiting for full Packet 1.

4. **Handoff archival banner deferral.** If Task 18 dispatch packet drafting slips months, the dispatch packet sits without the archival banner and a future cold reader could be misled by the "24/11/1000/13" counts. Mitigation: standalone commit if Task 18 hasn't started in ~2 weeks.

5. **Process-precedent decay.** L11/L12/L13 are recorded in the Task 17 convergence map's Post-implementer adjudication record, but Task 18 dispatch packet drafting needs to pull these forward into Task 18's convergence map. Risk that they get lost between tasks. Mitigation: feedback memory updates (Next Step #1).

## References

### Authority documents

| What | Where |
|---|---|
| **Spec design doc** (~1800+ lines, foundational) | `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` |
| Spec §Capture-ready handshake | `design.md:659-910` |
| Spec §Deferred-escalation semantics (`agent_context=None`) | `design.md:785-797` |
| Spec §DelegationStartError reasons | `design.md:622-657` |
| Spec §Unknown-kind contract (L11 authority) | `design.md:1705-1736` |
| Spec §`_finalize_turn` Captured-Request Terminal Guard (Task 19) | `design.md:1738-1808` |
| Phase G plan body (Task 17 + Task 18) | `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md` |
| Phase G Task 17 plan body | `phase-g-public-api.md:11-286` |
| Phase G Task 18 plan body | `phase-g-public-api.md:290-536` |
| Phase H plan body (Tasks 19-22) | `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-h-finalizer-consumers-contracts.md` |
| Carry-forward (binding state) | `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` |

### Task 17 working artifacts (committed in `c5829049`)

| What | Where |
|---|---|
| Convergence map (binding contract for Task 17) | `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-17-convergence-map.md` (399 lines) |
| Dispatch packet (historical prompt for implementer) | `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-17-dispatch-packet.md` (364 lines) |

### Precedent / template references

| What | Where |
|---|---|
| Phase F Task 16 convergence map (precedent for amendment patterns) | `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-convergence-map.md` |
| Phase F Task 16 dispatch packet (precedent for dispatch packet structure) | `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-16-dispatch-packet.md` |
| Phase F Task 16 closeout entry (precedent for carry-forward closeout-docs format) | `carry-forward.md:161-188` |

### Code under modification

| What | Where |
|---|---|
| `delegation_controller.py` (primary surgical target) | `packages/plugins/codex-collaboration/server/delegation_controller.py` |
| `worker_runner.py` (provides `spawn_worker`) | `packages/plugins/codex-collaboration/server/worker_runner.py` |
| `resolution_registry.py` (provides `wait_for_parked` + 5 variants) | `packages/plugins/codex-collaboration/server/resolution_registry.py` |
| `test_delegate_start_async_integration.py` (NEW from Task 17) | `packages/plugins/codex-collaboration/tests/test_delegate_start_async_integration.py` |

### Key commits (Task 17 chain)

| SHA | Subject |
|---|---|
| `f3cfa61a` | `docs(delegate): record Phase F Task 16 closeout (T-20260423-02)` (base) |
| `8dd15971` | `feat(delegate): rewrite start() with capture-ready handshake (T-20260423-02 Task 17)` |
| `dc90c1d9` | `fix(delegate): address Task 17 review (T-20260423-02 Task 17 closeout)` |
| `c5829049` | `docs(delegate): record Phase G Task 17 closeout (T-20260423-02)` |

### Project memory

| What | Where |
|---|---|
| MEMORY.md (auto-loaded; current-focus is stale post-session — update needed) | `/Users/jp/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/MEMORY.md` |
| Feedback memory: subagent-driven-development means full review chain | `~/.claude/projects/.../memory/feedback_subagent_driven_development_meaning.md` |

## Gotchas

### Diagnostics that LOOK like defects but ARE expected

1. **Pyright "Type analysis indicates code is unreachable" at `delegation_controller.py:892`.** This is the `case _: assert_never(outcome)` arm of `_dispatch_parked_capture_outcome`. The diagnostic IS the W11 exhaustiveness proof — Pyright correctly identifies the arm as unreachable BECAUSE the 5 explicit cases cover `ParkedCaptureResult` exhaustively. Do NOT flag as defect.

2. **Pyright "_journal not accessed" / "_cp not accessed" / "_wm not accessed" warnings in test files.** Tuple-unpacking artifacts from `_build_controller`'s 8-tuple return; not all tests use all values, and `_`-prefix convention isn't universally caught. Cosmetic; pre-existing.

3. **Pre-existing `_FakeControlPlane` protocol mismatches at `test_delegation_controller.py:257, 2547, 2621, 2686, 2867, 2888, 3064, 3194, 3418`.** Fixture-protocol issues unrelated to Task 17 surface (pre-existing per Task 16 G34); should be tracked as a separate carry-forward item (proposed TT.1) but not fixed as part of Task 17.

4. **`test_delegate_start_async_integration.py` and `test_delegate_start_integration.py` "_pytest could not be resolved"** — local venv noise; not a real import error.

### Process pitfalls

5. **Agent name binding releases on agent DONE/BLOCKED.** SendMessage to agent name will fail with "No agent named 'X' is currently addressable" once the agent has reported and exited. Use the agent ID (`a26933d8ee4731697` was the implementer ID throughout this session). Runtime resurrects from transcript: "had no active task; resumed from transcript".

6. **Working artifacts stay UNTRACKED through implementer execution + reviews.** Per Task 16 precedent: convergence map + dispatch packet are gitignored-equivalent (tracked manually) until the closeout-docs commit lands them as new files alongside the carry-forward.md updates. DO NOT stage them earlier — would split scope across feat / fix / docs commits.

7. **Mode A/B are NOT standalone Open table rows in carry-forward.md.** They are tracked narratively inside Task 14's Closed entry at lines 152-153. Per dispatch contract's allowance for following the closest precedent: Mode A partial closure (3 close + 3 defer) and Mode B full closure are documented inside the Task 17 closeout narrative, NOT promoted to standalone Open rows.

8. **L10 barrier is also narrative-only, not a standalone Open row.** Lives inside Task 16 closeout narrative; closes inside Task 17 closeout narrative. Bookkeeping convention preserved.

### Convergence map structural conventions

9. **Pre-dispatch warning at line 377 is intentionally NOT updated post-L13.** Explicitly labeled "(historical, original counts)" with adjacent "Post-feat amendment" line 379. Erasing it would lose the dispatch-time audit trail.

10. **Live anchors header explicitly labeled as pre-feat orientation.** "verified 2026-04-26 at pre-feat HEAD `f3cfa61a` — NOT refreshed after feat commit `8dd15971`". Spec reviewer needs both views: pre-feat anchors as the dispatch-contract reference; feat commit's diff as the substantive evidence.

### Implementer behavior

11. **Implementer self-assesses fixes that LOOK mechanical but require verification.** The `repo_root.mkdir()` cleanup was framed as "optional, skip if non-mechanical". Implementer applied 5/5 with explicit verification: "verified `repo_root` was referenced ONLY on the two consecutive declaration/mkdir lines in each test body". This is the right pattern — make discretion visible rather than implicit.

12. **Suite count match as a behavioral-leak canary.** Pure-cosmetic fix should produce zero suite delta. The fix commit dispatch's "ANY change to pass/skip counts is a defect" framing is a free canary that catches scope creep automatically. Verified: feat 999/14 → fix 999/14 → docs 999/14.

## Conversation Highlights

**User on Option 1 vs 2 vs 3 for the 3 P3 nits:** "Choose **Option 1**, including the optional `repo_root.mkdir()` cleanup if it is truly mechanical and confined to the five noted tests. The fix brief should explicitly say 'no behavioral expansion, no convergence-map edits, no closeout-docs edits in this commit,' then require suite pass plus W3 grep still returning 6."

**User on the post-implementer adjudication strategy:** "Recommendation: I agree with your recommendation, with one tightening: **accept both decisions retroactively, but do not dispatch the spec reviewer until the convergence map is amended and the adjudication is explicitly recorded.** Treat Notes 5 and 6 as a convergence-map gap, not an implementer violation. Treat Note 4 as a real process miss, but accept the technically correct reclassification and document the exception in the closeout narrative."

**User on the binding-surfaces-first amendment discipline:** "make the binding surfaces current, and reserve '24 / 11 / 8' for explicitly historical dispatch-time prose only."

**User confirming the dispatch packet was ready (after 4 fix rounds):** "Dispatch packet is ready. ... I would call the packet ready for dispatch."

**User after spec reviewer DONE:** "Dispatch the code-quality reviewer now. I would forward both notes. They are not spec blockers, but they are exactly the kind of code-quality review input that can prevent the next task from inheriting avoidable confusion."

## User Preferences

1. **Two-read protocol enforcement.** User does an independent `/copy` review before approving each artifact for the next stage. Do NOT proceed past an artifact draft without explicit user approval. Verified across multiple artifacts in this session: convergence map (5+ rounds), dispatch packet (3 rounds), post-feat amendments (3 rounds).

2. **Process precedent over implementation velocity.** When the dispatch contract says "preferred BLOCKED+question, NOT DONE_WITH_CONCERNS+unilateral", the user enforces this even if the implementer's substantive answer is correct. Mitigation: retroactive validation + explicit precedent record in convergence map (e.g., L13's "process precedent for future tasks" paragraph).

3. **Strict commit hygiene.** Stage specific files only (never `git add -A` / `git add .`). Co-author trailer mandatory: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`. Do NOT amend pushed commits; do NOT skip pre-commit hooks.

4. **subagent-driven-development means full review chain.** Per existing feedback memory `feedback_subagent_driven_development_meaning.md`: when user requests this workflow, dispatch implementer + spec reviewer + code-quality reviewer sequentially; do NOT stop at implementer DONE.

5. **Trust but verify on agent reports.** User often spot-checks agent claims independently (e.g., "I verified: branch is clean. Top four commits match your chain exactly. ... `c5829049` is docs-only for `packages/`; `git diff --stat HEAD~1..HEAD -- packages/` is empty"). Briefs should make this verification cheap by including specific commands.

6. **Stakes-calibrated decision framing.** When user is asked to make a decision, prefer presenting it with: stakes (low/medium/high), options (complete enumeration), information gaps, evaluation, sensitivity, ranking, recommendation, and readiness rating. User has used this framing pattern themselves in returning a decision.

7. **Brief responses for confirmed steps.** When the user explicitly confirms a directional move ("dispatch with that brief"), respond with the action + concise confirmation, not a long re-explanation.

## Rejected Approaches

1. **Original W2 (blanket `_finalize_turn` non-modification).** Rejected mid-session via L11 adjudication; spec evidence showed the rationale ("Task 19 owns Captured-Request Terminal Guard") was over-broad relative to the rule. W2 narrowed.

2. **Implementer's suggested `if interrupted_by_unknown: return updated_job` shape for L11 carve-out.** Rejected during BLOCKED-1 adjudication; would skip `_emit_terminal_outcome_if_needed` + runtime release + session close. Replaced with spec-prescribed `final_status="unknown"` + fall-through pattern.

3. **Bundling fix into closeout-docs commit (Option 2).** Rejected in favor of Option 1 (separate fix commit) per dispatch contract's anticipated 1+1+1 shape and clean commit discipline.

4. **Punting 3 P3 findings to carry-forward (Option 3).** Rejected — cost asymmetric to benefit; reviewer-specified surgical fixes; converts cosmetic findings to actual improvements.

5. **Reverting feat commit + requiring BLOCKED resubmission for L13 reclassification.** Rejected — disproportionate given decisive substantive validation; operationally wasteful; would re-perform an adjudication whose answer is known.

6. **Standalone commit for dispatch packet archival banner.** Rejected — over-engineering for one sentence; cost of opening a 5th commit higher than benefit; defer to Task 18 packet drafting where directory will be touched naturally.

7. **Erasing dispatch-time prose from convergence map (single-layer post-L13 only).** Rejected — would lose the audit trail; spec reviewer needs to see what the implementer was constrained by.

8. **Dispatching spec reviewer BEFORE convergence map amended.** Rejected per user tightening — reviewer would either fail (binding doc says X but code shows Y) or silently absorb the discrepancy. Amended map first, then dispatched.
