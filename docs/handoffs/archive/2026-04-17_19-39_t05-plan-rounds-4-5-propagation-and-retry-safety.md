---
date: 2026-04-17
time: "19:39"
created_at: "2026-04-17T23:39:08Z"
session_id: a5f5e327-3e39-46b6-b8af-c752aab7e3c1
resumed_from: "docs/handoffs/archive/2026-04-17_20-14_t05-plan-third-round-recovery-wiring-and-register-first.md"
project: claude-code-tool-dev
branch: docs/t05-execution-start-plan
commit: bd850302
title: "T-05 plan rounds 4 + 5 — AC/docstring propagation + lazy-path retry safety"
type: handoff
files:
  - docs/plans/2026-04-17-t05-execution-start-slice.md
---

# T-05 Execution-Start Plan — Rounds 4 + 5 revision (propagation + retry safety)

## Goal

Continue the multi-round scrutiny → revision arc on the T-05 execution-start plan. This session absorbed **two** distinct review rounds back-to-back:

- **Round 4 (Minor revision verdict):** Four findings of propagation weakness — claims that outran evidence in the prior round. Included F1 (Task 10 E2E bypassed production factory path), F2 (Task 5 `register()` docstring contradicted the new register-FIRST ordering), F3 (bullet 13 + AC 4 overclaimed durable state for the register-failure branch), F4 (registry busy-branch encoded an impossible `None` into the typed `JobBusyResponse.active_job_id: str`). Plus a fold-in of the same type-narrowing pattern on the journal busy-branch. Plus a pre-delivery grep sweep user directed.

- **Round 5 (Minor revision verdict):** One finding about proof-shape mismatch — the happy-path test at `:3270` was named `..._before_pinning` and its docstring claimed ordering, but its assertions could not falsify a pin-first-recover-second bug. User directed **Option A** (add a negative-path test) with three cleanup amendments: keep the 3-dispatch shape, don't assert exact error message surface, inline the new fixture alongside the existing one. Plus a rename of the happy-path test ("even under A, the existing name is still misleading") and a narrowing of Task 10's wording to delegate retry-ordering proof to Task 8.

**Bigger picture.** T-05 is the execution-domain foundation for codex-collaboration. The plan is a 4,188-line contract that implementers (subagent-driven or inline) will execute task-by-task. Each review round closes a deeper defect class. Rounds 1-2 closed data-shape + reader/failure defects. Round 3 closed integration-wiring defects. Rounds 4-5 closed propagation + proof-shape defects — the "plan says X is wired but the production path doesn't actually invoke it" class of bug, and the "test name makes a guarantee the assertions don't falsify" class.

**Trigger.** User replied to the prior session's 20:14 handoff via `/copy` with two successive reviews (rounds 4 and 5), each a structured scrutiny: premise check, critical failures with verbatim citations to exact plan line numbers, high-risk assumptions, real-world breakpoints, hidden dependencies, adversarial perspectives, required-changes list, verdict.

**Success criteria for this session:**

1. ✅ Each cited line in both rounds verified literally against the plan + dialogue precedent + journal implementation before responding (zero performative agreement).
2. ✅ All 4 round-4 findings confirmed structurally correct and accepted.
3. ✅ Round-4 journal-branch fold-in applied as user directed (not left for round 5).
4. ✅ Pre-delivery grep sweep (user directive) executed — no stale "AFTER successful bootstrap / persistence" residues.
5. ✅ Round-5 finding accepted; Option A chosen over Option B.
6. ✅ Task-name rename applied even though not strictly required by Option A — user caught that the name was still misleading.
7. ✅ Task 10 wording narrowed to delegate retry-ordering proof to Task 8 (not Task 10).
8. ✅ Test count chain re-verified after round 5: 593 → 604 → 612 → 615 → 618 → 624 → 639 → 644 → **652** → **654** → **655**, sum 11+8+3+3+6+15+5+**8**+2+1 = **62**.
9. ✅ Publication posture unchanged: plan still untracked; HEAD unchanged at `bd850302`; branch still `docs/t05-execution-start-plan`.

All nine met.

## Session Narrative

**Phase 1 — Load prior handoff (~immediate).** `/load` resolved the 20:14 handoff cleanly from the active directory; archived to `docs/handoffs/archive/`; state file written at `.session-state/handoff-a5f5e327-3e39-46b6-b8af-c752aab7e3c1`. Positioning set correctly per the handoff's "next action": wait for user review, do not pre-emptively edit. Read 866 lines of prior-session context including the full round-3 synthesis.

**Phase 2 — Receive round-4 scrutiny via `/copy` (~immediate).** User posted a structured scrutiny message with 4 critical failures, each citing specific plan line numbers:
- F1 at plan `:3757-3760` — Task 10 E2E uses `McpServer(..., delegation_controller=controller)` (direct injection). Task 8 at `:3077` and Task 9 at `:3597` say production deploys via `delegation_factory`. The E2E test bypasses the exact production path the round-3 fix established as load-bearing.
- F2 at plan `:1461-1465` — Task 5's `register()` docstring says "the controller calls this AFTER successful bootstrap + persistence," which contradicts Task 6's register-FIRST invariant at `:1522` and Step 6.3 write order at `:2567`.
- F3 at plan `:36` (bullet 13) and `:58` (AC 4) — both summarize dispatched recovery as "handle + job marked unknown," but the register-failure docstring at `:2326` and risks row at `:3932` explicitly state that branch has no handle / no job / no registry entry. Summaries overclaim the durable-state guarantee.
- F4 at plan `:2452` — registry busy branch computes `entry.job_id if entry is not None else None`, but `JobBusyResponse.active_job_id` at `:470` is declared `str` (not `str | None`). The fallback is both structurally unreachable and a typed-contract violation.

Verdict: "Minor revision."

**Phase 3 — Invoke `superpowers:receiving-code-review` (~30s).** Skill engaged before responding. Core rule: "Verify. Question. Then implement." Forbidden: performative agreement, blind implementation.

**Phase 4 — Verify each round-4 finding literally (~5 min, parallel reads).** Six parallel reads to ground every cited line:
- Plan `:30-99` (bullet 13, AC 1, AC 4, modified-files table)
- Plan `:1450-1500` (Task 5 register() docstring + class impl)
- Plan `:455-495` (JobBusyResponse dataclass definition)
- Plan `:2300-2379` (CommittedStartFinalizationError docstring + controller start() docstring)
- Plan `:3060-3150` (Step 7.4-7.6 + Task 8 Goal + Step 8.1 opening)
- Plan `:3590-3820` (Task 9 wiring + Task 10 E2E test in full)
- Plan `:2420-2500` (new 3-source busy gate from round 3)
- Plan `:3900-3945` (Risks table, register-failure row)

All cited lines held literally. Each finding confirmed. Notably F4: `active_runtime_ids()` returns dict keys; `lookup(rt_id)` on a live key cannot return None, so the `None` fallback was defensive but structurally unreachable AND contradicted the typed contract simultaneously.

**Phase 5 — Spot the adjacent journal-branch issue (~2 min).** While reading the busy-gate code for F4, noticed the journal branch at `:2470-2479` has the same pattern: `earliest.job_id` where `OperationJournalEntry.job_id` is declared `str | None` (per `:85`), but the per-phase validator (`:86`) requires `job_id` at both intent and dispatched phases for `job_creation`. Same by-convention narrowing, different branch, no explicit `None` fallback. Decided to flag for user awareness, not auto-fold.

**Phase 6 — Respond with verification + revision-shape options (~3 min).** Structured response:
1. Insight block (3 educational points: integration proof principle, docstring drift on primitives, typed contract vs by-convention narrowing)
2. Verification table — literal citations per finding
3. Adjacent issue flag (journal branch) — named but not proposed
4. Revision-shape options per finding with tradeoffs:
   - F1: **1a** (minimal factory-path refactor) / **1b** (add seed-and-assert proof, recommended) / **1c** (narrow the claim)
   - F2: **2a** (single-edit docstring rewrite, no alternative)
   - F3: **3a** (mirror AC 1 carve-out pattern, no alternative)
   - F4: **4a** (assert + drop fallback, recommended) / **4b** (raise RuntimeError) / **4c** (widen typed contract)
5. Scope cap + hold-until-decision

Recommended `1b + 2a + 3a + 4a`. Asked user explicitly about the journal-branch fold-in (3 options: fold now, defer, leave).

**Phase 7 — User decisions via `/copy` (~2 min).** User confirmed recommendations plus directives:
- F1 = 1b (seed-and-assert) — "proves the lazy-path recovery claim literal"
- F2 = 2a — one rewrite is enough
- F3 = 3a — anything less leaves the AC table internally inconsistent
- F4 = 4a — "encode the invariant, not an impossible `None` payload"
- **Journal-branch fold-in: YES, fold now.** "Same optional-by-type / required-by-invariant pattern, just without the explicit `None` fallback. If you leave it, round 5 is likely to hand you back the same class of finding one branch later."
- **Pre-delivery grep sweep:** "Do a quick grep for the exact stale phrasing class you already found in `register()` such as `AFTER successful bootstrap` / `AFTER persistence`. That is the other cheap place a harsh review could still nick you."

User also specified F1 behavioral proof shape: "seed an unresolved `job_creation` record, route through `delegation_factory`, then assert that seeded key is advanced to `completed` or no longer appears in `list_unresolved()`."

**Phase 8 — Plan the round-4 edit sequence (~1 min).** Identified 6 primary edits + 1 adjacent fold-in + grep sweep + 1 Task-10-goal tightening. Before F1, read `recover_startup()` implementation at `:2952-3031` and existing recovery tests at `:2804-2940` to verify seed viability — confirmed `recover_startup` handles "dispatched with no persisted handle/job" cleanly (journal-only advance), so a seeded entry without corresponding handle/job is safe.

**Phase 9 — Execute round-4 revision (~15 min, ~7 Edit calls + coherence verification).**

Edit 1 (F2): Rewrite Task 5 `register()` docstring at `:1461-1479`. Old: "AFTER successful bootstrap + persistence". New: "the FIRST committed-start write, IMMEDIATELY after `journal.write_phase(dispatched)` and BEFORE any other durable local write" + rationale paragraph + duplicate-id error note.

Edit 2 (F3 bullet 13): Update line 36 to match AC 1's carve-out shape. New wording distinguishes three reconciliation branches: intent-only no-op / dispatched with persisted state / dispatched with no persisted state (register-failure or crash-before-first-durable-write).

Edit 3 (F3 AC 4): Update line 58 evidence column with the same three-branch breakdown. Kept coherent with bullet 13.

Edit 4 (F4 + journal fold-in): Single combined edit replacing registry-branch `:2447-2462` and journal-branch `:2463-2479`. Registry: assert invariant `entry is not None` (documents that active_runtime_ids + lookup is a closed dict loop); remove None fallback; use `entry.job_id` unconditionally. Journal: assert invariant `earliest.job_id is not None` (documents the validator-enforced job_id presence on job_creation entries); use `earliest.job_id` unconditionally. Both preserve typed `JobBusyResponse.active_job_id: str`.

Edit 5 (F1 import): Add `OperationJournalEntry` to the import list in Task 10 E2E at `:3681`.

Edit 6 (F1 main): Restructure the E2E test body. Changes:
- Seed an unresolved `job_creation` entry at `dispatched` phase with distinct idempotency key (`sess-e2e:seeded-leftover-hash`) before any dispatch
- Sanity-check the seed IS unresolved pre-dispatch (`pre_unresolved_seeds` assertion)
- Wire through `delegation_factory=lambda: controller` instead of direct injection
- After dispatch, assert seed is reconciled: `post_unresolved_seeds == []` and `check_idempotency(seeded_key).phase == "completed"`
- Added load-bearing-proof comment block explaining why this catches the exact regression class

Edit 7 (Task 10 goal tightening): Noticed Task 10's Goal still said "exercises the entire slice" and "→ pin" — rewrote to explicitly name the factory-path traversal and the seed-and-assert proof shape.

**Phase 10 — Grep sweep + coherence verification (~3 min, ~6 parallel greps + 1 bash).**

Grep 1: `AFTER successful bootstrap|AFTER persistence` (case-insensitive) — 0 matches ✓
Grep 2: `delegation_controller=controller` — 3 matches at Task 8 unit tests (lines 3163, 3189, 3318), intentional eager-path tests, not E2E
Grep 3: `delegation_factory=lambda` — 1 match at line 3851 (E2E test, factory path) ✓
Grep 4: `after ... bootstrap|AFTER the` — 1 match at line 2440 (busy-gate comment saying "failed AFTER the registry registration that always happens FIRST" — correct register-FIRST phrasing)
Grep 5: `handle + job marked` — 2 matches at lines 1989, 2033, both scoped to specific failure modes (journal-completed-failure, audit-failure) where register DID succeed, so not overclaiming
Grep 6: `entry.job_id if entry is not None else None` — 0 matches ✓

Coherence: Task headers 11 sequential (1-11) ✓. Line count: 3947 → 4063 (+116 net).

**Phase 11 — Present round-4 summary (~2 min).** Structured response with insight block, revision summary table, grep sweep results table, coherence verification table, what-did-NOT-change list, and anticipated round-5 scrutiny vectors (seed-and-assert proof shape, invariant assertion style, pre_unresolved_seeds sanity check, import coupling).

**Phase 12 — Receive round-5 scrutiny via `/copy` (~immediate).** User returned with single finding (Medium severity):

> "The lazy-path tests still do not prove the 'before pinning' guarantee they claim to prove."

Cited lines:
- `:3270` (test name `..._before_pinning`)
- `:3394`, `:3405` (implementation docstring + comment claiming retry semantics)
- `:3660`, `:3918` (Task 10 goal + E2E comment overclaiming)

User's argument: The success-path test only proves `recover_startup` was called once and not twice. A pin-first-recover-second implementation would still pass as long as recovery succeeds. The exact regression class the prose claims to defend against is NOT falsifiable by the current assertions.

Two options given:
- **A:** Add one Task 8 negative-path test. Assertions: no pin on failed recovery; `start()` not reached; second dispatch retries recovery.
- **B:** Narrow wording at 4 locations to say "recovery runs on the lazy path" instead of "before pinning."

User also validated that the F2/F3/F4 fixes hold and closed my anticipated round-5 vector about production-assert style: "the existing repo already uses production asserts in jsonrpc_client.py:65 and control_plane.py:261. So the new invariant-assert style matches local precedent."

Verdict: "Minor revision."

**Phase 13 — Verify round-5 finding (~3 min, 4 parallel reads).** Read each cited line:
- `:3270` test name + `:3271` docstring ("recover_startup fires once on first dispatch, then pin")
- `:3385-3408` `_ensure_delegation_controller` implementation + docstring
- `:3910-3920` E2E comment
- `mcp_server.py` dialogue precedent grep for "pin"

Finding verified. The test at `:3270-3308` asserts `recover_startup_calls == 1` after first dispatch, `== 1` after second dispatch, and `len(start_calls) == 2`. None of those assertions distinguish factory → recover → pin from factory → pin → recover. User is correct.

**Phase 14 — Respond with verification + option recommendation (~2 min).** Presented both options with trade-offs. Recommended **Option A**: "Option B abandons [the retry semantics claim] rather than proving it. Option A costs ~30 lines (fixture + test) and catches the exact pin-first-recover-second regression."

Drafted the proposed test and fixture inline for user review. Suggested 3-dispatch shape: dispatch 1 fails recovery, dispatch 2 retries and succeeds, dispatch 3 uses pinned controller. Flagged questions about error-response assertion detail and fixture placement.

**Phase 15 — User decisions + cleanup amendments via `/copy` (~2 min).** User confirmed Option A with amendments:
1. Keep 3-dispatch shape ✓
2. **Do not** assert exact error message — only assert error exists (message surface is transport detail)
3. Inline `_FailOnceDelegationController` next to `_RecordingDelegationController` (no shared fixtures file)
4. **Rename the existing happy-path test** from `..._before_pinning` → `..._on_first_dispatch` ("even under A, that individual test does not prove the ordering")
5. **Narrow Task 10 wording at `:3660` and `:3918`** ("Task 10 should claim 'recovery runs on the lazy path,' not 'before pinning.' The ordering proof belongs in Task 8 after this new negative-path test lands.")
6. Accept test-count cascade to 655

User explicitly did NOT direct narrowing of Task 8 "before pinning" language — it's load-bearing now that the new test proves it.

**Phase 16 — Plan round-5 edit sequence (~1 min).** Identified 9 edits:
1. Insert `_FailOnceDelegationController` fixture at module level
2. Rename happy-path test + update its docstring with honest scope
3. Insert new negative-path test inside `TestDelegationRecoveryWiring` class
4. Update Step 8.4 expected count (7 → 8 new tests; 644+7=651 → 644+8=652)
5. Update Task 9 expected (~653 → ~654)
6. Update Task 10 expected (~654 → ~655)
7. Update Task 11 chain (sum 61 → 62; chain ends at 655)
8. Narrow Task 10 goal at `:3660`
9. Narrow Task 10 E2E comment at `:3918`

**Phase 17 — Execute round-5 revision (~15 min, 8 Edit calls + coherence verification).**

Edit 1: Insert fixture after `_RecordingDelegationController`. Mirrors fixture's shape; adds `recovery_fails_remaining` int parameter; raises `RuntimeError` for configured count of calls.

Edit 2: Rename test method; docstring now references the new negative-path test by name and clarifies scope (happy-path first-dispatch only).

Edit 3: Add `test_ensure_delegation_controller_does_not_pin_on_recovery_failure` inside `TestDelegationRecoveryWiring`, before the eager-path test. Uses a closure-captured `factory_controllers: list` so the factory returns a new controller each call, and the first controller's `recover_startup` raises. Asserts (a) error in response1, (b) factory_controllers has length 1 after dispatch 1, (c) start_calls empty on first controller, (d) factory_controllers has length 2 after dispatch 2 (proving retry), (e) factory_controllers still has length 2 after dispatch 3 (proving pin after success), (f) second controller's start_calls has length 2.

Edit 4-7: Cascade test count updates. Each `Expected: ... ~NNN passed` line updated. Task 11's sum line rewritten with 62 instead of 61.

Edit 8: Task 10 goal narrowing. Removed "→ pin" phrasing. Added explicit cross-reference: "The separate pin-only-after-successful-recovery retry-ordering invariant is proven by Task 8's `test_ensure_delegation_controller_does_not_pin_on_recovery_failure`, NOT by this integration test."

Edit 9: E2E comment narrowing. Changed "refactor drops the recover_startup call before pinning" to "refactor drops the recover_startup call from _ensure_delegation_controller". Added Task 8 cross-reference.

**Phase 18 — Coherence verification + final greps (~3 min, ~5 parallel greps).**

Grep: "before pin" / "Pin only after" — 8 matches, each classified:
- `:88` (mcp_server.py modified-files table) ✓ Keep — describes code proven by Task 8
- `:3089` (Task 7 "Why only the eager path here") ✓ Keep — cross-references Task 8 (proven)
- `:3111` (Task 8 Goal) ✓ Keep — Task 8 contains the proof
- `:3307` (renamed test docstring) ✓ Keep — references new negative-path test
- `:3355` (new test docstring) ✓ Keep — quotes implementation docstring
- `:3512-3527` (implementation docstring + comment) ✓ Keep — proven by new test
- `:3782` (Task 10 Goal, narrowed) ✓ Keep — explicitly delegates to Task 8
- `:4043` (E2E comment, narrowed) ✓ Keep — explicitly delegates to Task 8

Grep: stale test name `test_ensure_delegation_controller_runs_recover_startup_before_pinning` — 0 matches ✓

Grep: test count chain — verified 9 expected-count lines all consistent, sum matches 62.

Line count: 4063 → 4188 (+125 for round 5; +241 total across rounds 4+5).

**Phase 19 — Present round-5 summary (~2 min).** Insight block (3 educational points: rename as propagation fix, error-response surface as transport detail, fixture purpose scaling), revision summary table with 6 changes, Task 8 test-count breakdown (8 total: 5 dispatch/reg + 2 lazy recovery-wiring + 1 eager recovery-wiring), coherence verification table, what-did-NOT-change list, round-6 anticipation with 4 vectors including the error-response surface question flagged honestly.

**Phase 20 — User invoked `/save` (immediate).** Writing this handoff now.

## Decisions

### Decision 1: Accept all 4 round-4 findings without pushback

**Choice:** All of F1, F2, F3, F4 confirmed structurally correct and accepted as binding revisions.

**Driver.** Each finding cited specific lines that held literally when verified:
- F1: plan `:3757-3760` uses direct-injection; Task 8 `:3077` and Task 9 `:3597` say production uses factory. No test exercises the factory→recover→pin path.
- F2: plan `:1463-1465` says "AFTER successful bootstrap + persistence"; Task 6 invariant at `:1522` and Step 6.3 write order at `:2371` are register-FIRST.
- F3: plan `:36` and `:58` say "dispatched → handle + job marked unknown"; docstring at `:2326` and risks row at `:3932` say register-failure has no handle/job/registry entry.
- F4: plan `:470` declares `active_job_id: str`; `:2454` computes `entry.job_id if entry is not None else None`.

**Alternatives considered:**
- **Push back on F1 by claiming the eager-side wiring + round-3 unit tests suffice.** Rejected because the unit tests use direct controller injection too; production path remained unproven.
- **Push back on F3 by claiming the register-failure case is "extremely unlikely" per AC 1 line 55's existing carve-out.** Rejected because probability doesn't change the AC's text-level honesty; summaries should not overclaim.
- **Accept F4 narrowly (just widen `active_job_id` to `str | None`).** Rejected for ripple cost — the external `JobBusyResponse` contract would propagate uncertainty into consumers who reasonably expect a job_id when busy.

**Implications.** Plan grows +116 lines (3947 → 4063). Task 10 E2E test gains seed+assert proof shape. Task 5 `register()` docstring gets a 6-line-longer rewrite with rationale. Bullet 13 and AC 4 pick up register-failure carve-outs matching AC 1. Both busy-gate branches use invariant-asserts documenting the closed-loop / validator-enforced guarantees.

**Trade-offs accepted.** Larger plan. One additional state (`assert entry is not None`) the implementer must understand. Register-failure carve-out adds nuance to AC summaries (less quotable, more precise).

**Confidence:** High (E2) — verified against plan, dialogue precedent (`mcp_server.py`), and validator implementation (`journal.py`); all cited line numbers held exactly.

**Reversibility:** High at plan level; low at execution level (shipping round-3 text would have produced 2 real bugs at first crash recovery + register-failure scenario).

**Change trigger:** None — findings grounded in normative code that won't change.

### Decision 2: Option 1b (seed-and-assert) over 1a (factory-path traversal only) or 1c (narrow claim)

**Choice:** Task 10 E2E test refactored to (a) route through `delegation_factory=lambda: controller` instead of direct injection, AND (b) seed an unresolved `job_creation` journal entry at `dispatched` phase before the first dispatch, AND (c) assert the seed is reconciled to `completed` after dispatch.

**Driver.** User directive: "seed an unresolved `job_creation` record, route through `delegation_factory`, then assert that seeded key is advanced to `completed` or no longer appears in `list_unresolved()`. That makes the lazy-path recovery claim literal."

**Alternatives considered:**
- **1a (minimal factory-path traversal):** Change only `delegation_controller=controller` → `delegation_factory=lambda: controller`. Proves factory-path invocation by call-count but doesn't prove `recover_startup()` actually reconciled anything. Rejected because the same regression (factory traversed, but recovery dropped inside `_ensure_delegation_controller`) would still pass.
- **1c (narrow the AC 4 claim):** Rename Task 10 to drop "end-to-end" pretense; keep direct injection. Rejected because it abandons the integration proof rather than strengthening it.

**Implications.** Added ~90 lines to Task 10 including pre-dispatch sanity check (`pre_unresolved_seeds` asserts the seed IS unresolved before dispatch — invariant for proof shape). Added `OperationJournalEntry` import. Added explicit Task 8 cross-reference to distinguish the wiring proof (Task 10) from the retry-ordering proof (Task 8).

**Trade-offs accepted.** ~10 lines more than 1a. The seed setup requires understanding `OperationJournalEntry` field requirements, which is more test-code to maintain.

**Confidence:** High (E1) — direct user directive; implementation of `recover_startup` at `:2952-3031` confirms it handles "dispatched with no persisted handle/job" cleanly.

**Reversibility:** High — text-editable at plan level; at execution level, a simpler version could be swapped in if seed complexity proves brittle.

**Change trigger:** If `recover_startup()` semantics change (e.g., to raise on orphaned dispatched entries), the seed shape would need updating.

### Decision 3: Option 4a (assert + drop None fallback) over 4b (raise) or 4c (widen contract)

**Choice:** Replace `entry.job_id if entry is not None else None` with `assert entry is not None, "..." ; entry.job_id`.

**Driver.** User directive: "encode the invariant, not an impossible `None` payload. `4c` weakens the external contract. `4b` is directionally acceptable, but for this plan pass `4a` is the tighter correction."

Additional confidence: round-5 user validation — "the anticipated 'asserts are illegitimate in production' objection is weak here. The existing repo already uses production asserts in `jsonrpc_client.py:65` and `control_plane.py:261`."

**Alternatives considered:**
- **4b (raise RuntimeError):** Replace the None path with an explicit raise. Rejected as over-engineered — the invariant is internal to the registry; a structural violation should crash loud via assert, not surface a new production error type requiring a dedicated test.
- **4c (widen `JobBusyResponse.active_job_id` to `str | None`):** Rejected because F3 already forced bullet 13 + AC 4 to acknowledge register-failure produces no entry; widening the type would propagate "busy but unknown job_id" into the external contract.

**Implications.** Registry busy branch: ~5 lines added (assert message). Journal busy branch folded in: ~8 lines added (assert + message). Implementation-style precedent set for invariant documentation in this plan.

**Trade-offs accepted.** Asserts are disabled under `python -O`, but repo doesn't use `-O` (confirmed by dialogue precedent using asserts). Negligible.

**Confidence:** High (E2) — user directive + repo precedent verified.

**Reversibility:** High — single-line changes in two locations.

**Change trigger:** If the repo adopts `-O` for production builds, asserts would need upgrading to explicit raises.

### Decision 4: Fold journal-branch narrowing into round 4 (vs defer to round 5)

**Choice:** Apply the same invariant-assert pattern to the journal busy-branch (`:2470-2479`) in round 4.

**Driver.** User directive: "Fold it in now. The branch is the same optional-by-type / required-by-invariant pattern, just without the explicit `None` fallback. If you leave it, round 5 is likely to hand you back the same class of finding one branch later."

**Alternatives considered:**
- **Defer to round 5:** Flag only, let user decide if worth fixing. Rejected because user is explicitly pre-empting the round-5 re-raise cost.
- **Narrow fix (no assert):** Just use `earliest.job_id` without asserting. Rejected — the whole point of the fix pattern is documenting the invariant.

**Implications.** +12 lines in the journal branch. Establishes pattern across both branches consistently. Pre-empts a round-5 finding (which in fact did NOT re-raise this issue — confirming the user's prediction).

**Trade-offs accepted.** None beyond the registry-branch cost already accepted.

**Confidence:** High (E1) — direct user directive.

**Reversibility:** High.

**Change trigger:** N/A.

### Decision 5: Pre-delivery grep sweep for "AFTER successful bootstrap / persistence" patterns

**Choice:** Run explicit grep for the stale phrasing class found in F2 (Task 5 docstring) across the entire plan before returning round 4.

**Driver.** User directive: "Do a quick grep for the exact stale phrasing class you already found in `register()` such as `AFTER successful bootstrap` / `AFTER persistence`. That is the other cheap place a harsh review could still nick you."

**Alternatives considered:**
- **Assume the docstring was the only location:** Rejected — user's directive was explicit about the class of phrasing, not the specific occurrence.

**Implications.** Grep found 0 additional matches. Ran 5 additional greps (`delegation_controller=controller`, `delegation_factory=lambda`, `handle + job marked`, `registry_persisted`, `entry.job_id if entry is not None else None`) as sanity-check sweep. All clean or scoped to intentional locations.

**Trade-offs accepted.** ~1 min of grep time.

**Confidence:** High (E1) — systematic coverage of the phrasing class.

**Reversibility:** N/A (no edits made from the sweep itself).

**Change trigger:** N/A.

### Decision 6: Round 5 — Option A (add negative-path test) over Option B (narrow wording)

**Choice:** Add `test_ensure_delegation_controller_does_not_pin_on_recovery_failure` to `TestDelegationRecoveryWiring` in Task 8. 3-dispatch shape: fail / retry / reuse.

**Driver.** User directive: "The load-bearing claim is retry safety on the lazy path, and the current success-path test at line 3270 does not prove it. Adding the negative-path Task 8 test is the right fix; narrowing the wording would just retreat from a claim the plan should still make."

**Alternatives considered:**
- **Option B (narrow wording):** Update 4 locations to claim only "recovery runs on the lazy path." Rejected because the retry semantics is load-bearing — the implementation docstring at `:3394` explicitly says "Pin only after recovery succeeds — transient failures allow retry." Narrowing would abandon a claim the plan should defend.
- **Inline into existing test:** Add failure assertion to the existing success-path test. Rejected because proof shapes are different; a single test would muddy both invariants.

**Implications.** +89 lines for new test + ~33 lines for new fixture + test count cascade +1 across Tasks 8-11 (final suite: 655). Explicit Task 8 / Task 10 split: ordering proof in Task 8, wiring proof in Task 10.

**Trade-offs accepted.** Plan grows 4063 → 4188 (+125 lines). One more test to execute. Slight coupling to the factory-controller-retry implementation: if `_ensure_delegation_controller` semantics change, both tests need updating.

**Confidence:** High (E1) — direct user directive + independent verification that current assertions cannot falsify pin-first-recover-second.

**Reversibility:** Medium — removing the negative-path test later would require either reinstating Option B's wording narrowing OR making the plan's retry-safety claim unproven again.

**Change trigger:** If the factory-controller-retry mechanism is redesigned (e.g., dialogue's pattern changes in a way we need to mirror), the test shape may need updating.

### Decision 7: Rename happy-path test (even under Option A)

**Choice:** Rename `test_ensure_delegation_controller_runs_recover_startup_before_pinning` → `test_ensure_delegation_controller_runs_recover_startup_on_first_dispatch` + update its docstring to honestly scope what it proves.

**Driver.** User directive: "Even under A, `test_ensure_delegation_controller_runs_recover_startup_before_pinning` is still misleading because that individual test does not prove the ordering. Rename it to something honest like `test_ensure_delegation_controller_runs_recover_startup_on_first_dispatch`."

**Alternatives considered:**
- **Keep the name:** Rely on the new negative-path test to carry the ordering claim at the module level. Rejected because test names ARE contract at the per-test level; a reader looking at the single test in isolation should not be misled.
- **Different rename:** `_happy_path` or similar. User's specific phrasing preferred — grounds the name in what the test assertions actually check.

**Implications.** Test name honestly reflects the assertions. Docstring updated to reference the new negative-path test by name ("pin-only-after-successful-recovery retry ordering invariant is covered separately by `test_ensure_delegation_controller_does_not_pin_on_recovery_failure`").

**Confidence:** High (E1) — direct user directive.

**Reversibility:** High — renames are text-only.

**Change trigger:** If Option B is ever adopted instead (unlikely), name could revert.

### Decision 8: Narrow Task 10 wording; keep Task 8 "before pinning" language

**Choice:** Task 10 goal (`:3660`) and E2E comment (`:3918`) narrowed to claim "recovery runs on the lazy path" and explicitly delegate retry-ordering proof to Task 8. Task 8 language (Goal at `:3111`, implementation docstring at `:3512/3516/3527`, modified-files table at `:88`, Task 7 cross-reference at `:3089`) kept as-is.

**Driver.** User directive: "The ordering proof belongs in Task 8 after this new negative-path test lands." Task 10 is a successful end-to-end path; it's the wrong place to prove retry-on-recovery-failure semantics.

**Alternatives considered:**
- **Narrow everywhere (including Task 8):** Rejected because Task 8 now actually proves the ordering invariant via the new negative-path test. Narrowing Task 8 would leave the claim weaker than the evidence supports.
- **Keep Task 10 claims:** Rejected because Task 10's seed-and-assert proof doesn't falsify pin-first-recover-second; leaving the claim in Task 10 would relocate the same lie.

**Implications.** Task 8 and Task 10 now have clean responsibility split: Task 8 = retry-ordering proof; Task 10 = wiring+reconciliation proof. Future-readers of either task won't see overclaim outside its proof scope.

**Confidence:** High (E1) — direct user directive; responsibility split is structural.

**Reversibility:** High — all narrowing is text-only.

**Change trigger:** N/A — split is stable.

## Changes

### Files modified (this session)

| File | Change | Commit |
|---|---|---|
| `docs/plans/2026-04-17-t05-execution-start-slice.md` | **Round 4:** Task 5 `register()` docstring rewritten (6 lines → 13 lines) with register-FIRST rationale. Bullet 13 (line 36) + AC 4 evidence (line 58) updated with three-branch reconciliation breakdown matching AC 1's carve-out pattern. Registry busy-branch (`:2447-2470`) uses `assert entry is not None` invariant + unconditional `entry.job_id`; journal busy-branch (`:2478-2495`) uses `assert earliest.job_id is not None` invariant + unconditional `earliest.job_id`. Both preserve typed `JobBusyResponse.active_job_id: str`. Task 10 E2E test restructured: added `OperationJournalEntry` import; pre-seeded unresolved `job_creation` entry at `dispatched` phase before first dispatch; pre-dispatch sanity check asserts seed IS unresolved; wiring changed from `delegation_controller=controller` to `delegation_factory=lambda: controller`; post-dispatch assertions prove seed reconciled to `completed` and removed from `list_unresolved`. Task 10 goal prose tightened to name factory-path traversal and seed-and-assert proof shape. **Round 5:** New `_FailOnceDelegationController` fixture (33 lines) at module level next to `_RecordingDelegationController`. Renamed `test_ensure_delegation_controller_runs_recover_startup_before_pinning` → `test_ensure_delegation_controller_runs_recover_startup_on_first_dispatch`; docstring updated to cross-reference the new negative-path test. New `test_ensure_delegation_controller_does_not_pin_on_recovery_failure` (89 lines) inside `TestDelegationRecoveryWiring`. Test count cascade updated at 4 locations: Step 8.4 (7 new → 8 new; 651 → 652), Task 9 (653 → 654), Task 10 (654 → 655), Task 11 sum (61 → 62). Task 10 goal (`:3782`) and E2E comment (`:4041`) narrowed to delegate retry-ordering proof to Task 8. Line count: **3947 → 4188 (+241 net across rounds 4+5)**. Test count chain: 593 → 604 → 612 → 615 → 618 → 624 → 639 → 644 → **652** → **654** → **655**. | Uncommitted |

### Git state changes

| Commit | Branch | Subject |
|---|---|---|
| (none) | `docs/t05-execution-start-plan` | Branch unchanged; plan still untracked |

No commits. No push. Main unchanged at `bd850302`.

### Handoff / state files

- Archived (at session start): `2026-04-17_20-14_t05-plan-third-round-recovery-wiring-and-register-first.md` → `docs/handoffs/archive/`
- State file: `docs/handoffs/.session-state/handoff-a5f5e327-3e39-46b6-b8af-c752aab7e3c1` — to be cleaned by this save
- New handoff (this file): `docs/handoffs/2026-04-17_19-39_t05-plan-rounds-4-5-propagation-and-retry-safety.md`

## Codebase Knowledge

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `docs/handoffs/2026-04-17_20-14_t05-plan-third-round-recovery-wiring-and-register-first.md` | Prior handoff (resumed) | Full round-3 context: plan revised three times, awaiting round-4 review |
| `docs/plans/2026-04-17-t05-execution-start-slice.md` (multiple ranges, ~1200 lines total across session) | Ground every round-4 and round-5 edit | All cited line numbers held literally |
| `packages/plugins/codex-collaboration/server/mcp_server.py` (grep for "pin") | Verify dialogue precedent for Option A test design | `_dialogue_controller._ensure_dialogue_controller` pins after recovery — confirmed at line 135 comment "One-way pin: the factory is called at most once" |

### Architecture: proof-shape split between Task 8 and Task 10

After rounds 4-5, the proof responsibilities are cleanly partitioned:

| Claim | Proof location | Mechanism |
|---|---|---|
| `_ensure_delegation_controller()` runs recovery on first dispatch | Task 8: `test_..._runs_recover_startup_on_first_dispatch` | Calls recover_startup; asserts count == 1 after 1st and after 2nd dispatch |
| `startup()` runs recovery when controller injected directly | Task 8: `test_startup_runs_delegation_recover_startup_when_controller_provided_directly` | Calls startup(); asserts count == 1; idempotent on 2nd call |
| **Recovery failure doesn't pin; next dispatch retries** | Task 8: `test_..._does_not_pin_on_recovery_failure` (NEW in round 5) | 3-dispatch shape: fail → retry → reuse |
| **Recovery actually reconciles pre-existing unresolved entries on production path** | Task 10: E2E (restructured in round 4) | Seed unresolved dispatched entry; route through delegation_factory; assert seed advanced to completed |
| Lineage + job + audit + completed all written on happy path | Task 10: E2E | Full durable-state assertions |

### Architecture: 3-source busy gate invariants (post-round-4)

| Source | Result type | Invariant documented by assert |
|---|---|---|
| `job_store.list_active()` | `JobBusyResponse` with `active.job_id` | N/A — `DelegationJob.job_id` is non-optional |
| `runtime_registry.active_runtime_ids()` + `lookup(rt_id)` | `JobBusyResponse` with `entry.job_id` | `assert entry is not None` — active_runtime_ids + lookup is a closed in-process dict loop |
| `journal.list_unresolved(session_id=...)` filtered for `operation == "job_creation"` | `JobBusyResponse` with `earliest.job_id` | `assert earliest.job_id is not None` — validator-enforced: `job_creation` at intent/dispatched requires `job_id` |

Both asserts document invariants that are structurally guaranteed by adjacent code but not by types alone.

### Architecture: test-count chain (final)

`593 → 604 → 612 → 615 → 618 → 624 → 639 → 644 → 652 → 654 → 655`

Per-task deltas: `11 + 8 + 3 + 3 + 6 + 15 + 5 + 8 + 2 + 1 = 62`

Task 8 breakdown (post-round-5): **+8 total**
- 5 dispatch/registration (`test_delegate_start_tool_registered`, `test_delegate_start_input_schema_requires_repo_root`, `test_delegate_start_dispatch_returns_job_fields`, `test_delegate_start_forwards_optional_base_commit`, `test_delegate_start_returns_busy_response_payload`)
- 2 recovery-wiring (lazy): happy-path first-dispatch + pin-deferral-on-recovery-failure
- 1 recovery-wiring (eager): `test_startup_runs_delegation_recover_startup_when_controller_provided_directly`

### Surprising findings / gotchas this session

- **The `_FailOnceDelegationController` fixture design required care with factory semantics.** The factory closure captures a list and returns a new controller each call — first one fails recovery, rest succeed. This is what makes the test sensitive to pin-first-recover-second bugs (the factory MUST be called twice to prove no pin on first failure).
- **`_ensure_delegation_controller` implementation is safe-by-construction for retry.** Looking at the pseudocode at plan `:3395-3408`: the pin happens at line :3406 (`self._delegation_controller = controller`) and the factory-cleared happens at :3407. Both are AFTER `controller.recover_startup()` at :3404. So if recover_startup raises, `_delegation_controller` stays None AND `_delegation_factory` stays set — exactly the state the retry semantics requires.
- **Journal's `OperationJournalEntry.job_id` is declared `str | None` but always required for `job_creation` at intent/dispatched.** The validator (Task 1 extension) enforces this. The dataclass type is loose for multi-operation compatibility; consumers must narrow via assert or context. This is the same pattern that motivated F4's adjacent-issue fold-in.
- **`recover_startup()` handles "dispatched with no persisted handle/job" cleanly.** Reading `:2952-3031`: the implementation only calls `update_status("unknown")` if `handle is not None` and `job is not None`. For the register-failure case (no handle, no job), it only advances the journal. This is what made F1's seed design safe — no error on the seeded entry that has no corresponding stores.
- **Line count growth rate across rounds:** Round 1 +~500, Round 2 +~499, Round 3 +339, **Round 4 +116, Round 5 +125**. Total +1,579 lines across 5 review rounds. Growth rate is decelerating — likely signal of approaching convergence.

### Key locations to remember

| Concept | Location |
|---|---|
| T-05 plan (5x revised) | `docs/plans/2026-04-17-t05-execution-start-slice.md` (4,188 lines) |
| Dialogue lazy-factory precedent | `packages/plugins/codex-collaboration/server/mcp_server.py:132-151` (call at :147) |
| `_ensure_delegation_controller` impl (plan) | plan `:3385-3408` |
| `recover_startup()` impl (plan) | plan `:2952-3031` |
| New `_FailOnceDelegationController` fixture (plan) | plan `:3265-3297` |
| New negative-path test (plan) | plan `:3349-3437` |
| Task 10 E2E with seed-and-assert | plan `:3780-4070` |
| 3-source busy gate with invariant asserts | plan `:2447-2495` |

## Context

### Mental model

**Framing:** Rounds 4 and 5 were both **propagation + proof-shape rounds**, one layer shallower than round 3 (integration-wiring). The session pattern confirms:

- **Design rounds** (1-2): "Is this the right architecture?" Closed by structural changes.
- **Integration rounds** (3): "Does the design actually connect?" Closed by wiring + failure-mode rules.
- **Propagation rounds** (4): "Do all the prose, docstrings, AC summaries match the design?" Closed by careful sweeps + matching the claim strength across documents.
- **Proof-shape rounds** (5): "Do the tests actually falsify the claims?" Closed by negative-path tests or narrowed wording.

- **Core insight:** *Each round closes a different defect class. Defect classes are ordered by abstraction — design defects prevent anything working; integration defects prevent production working; propagation defects mislead readers; proof-shape defects leave load-bearing claims unfalsifiable.* The fact that rounds 4 and 5 are increasingly narrow (lines delta: 339 → 116 → 125) is signal of convergence.
- **Mental model:** *Converging review series.* Each round has a verdict (Major / Minor / Approve); each Minor verdict signals narrowing scope; approval happens when a round finds ≤0 new defects. The plan has now sustained 5 Minor-verdict rounds with findings count 3 → 2 → 2 → 4+1fold → 1 → ? (round 6 or approval).

### Project state at session close

**T-20260330-05 (execution-domain foundation):** OPEN, high priority. Plan revised FIVE times now. Still uncommitted on `docs/t05-execution-start-plan`. Awaiting **sixth** scrutiny pass or approval per user's sustained pattern.

**T-20260330-06 / T-07:** OPEN, blocked by T-05.

**T-20260416-01 (codex.dialogue.reply extraction mismatch):** OPEN, medium priority. Independent parallel thread — unchanged this session.

### Environment snapshot at session close

- Branch: `docs/t05-execution-start-plan` (unchanged)
- HEAD: `bd850302` (unchanged)
- Working tree: **dirty** — `docs/plans/2026-04-17-t05-execution-start-slice.md` still untracked (4,188 lines)
- Plugin suite: not run this session (no code changes)
- Memory: no new feedback files; MEMORY.md unchanged
- Context usage at session close: ~21% of 1M context window (comfortable headroom for 1-2 more rounds)

### Why this work matters (bigger picture)

T-05 is the execution-domain foundation for codex-collaboration. A plan that shipped round-3 text would have produced real bugs at:
1. First crash recovery: Task 10's "end-to-end" test bypassing the factory path means a `recover_startup` regression inside `_ensure_delegation_controller` wouldn't be caught (F1).
2. First register-failure scenario: AC 1 / AC 4 / bullet 13 summarizing handle+job as "always marked unknown" would mislead implementers about what state to expect for the register-failure branch (F3).
3. First time a reader reads Task 5 in isolation: `register()` docstring would teach the pre-round-3 ordering and reintroduce the orphan-runtime bug in the primitive meant to support the controller (F2).
4. First type-check: `JobBusyResponse.active_job_id=None` is statically inconsistent with the declared `str` type (F4).
5. First transient recovery failure: Task 8's success-path test would pass even if a refactor reordered to pin-first-recover-second, silently breaking the retry-semantics guarantee (Round 5 finding).

This session was ~60 min of work that prevents 3-5 hours of execution-time rework. The multi-round review pattern continues to pay off, now 5 rounds in. Decelerating line-count delta (116, 125) suggests convergence may be close.

## Learnings

### Propagation defects are distinct from design defects

**Mechanism.** A design can be correct (registry-FIRST ordering invariant at :1522) but prose summaries elsewhere (register() docstring at :1461, bullet 13 at :36, AC 4 at :58) can still teach the pre-fix design. Propagation is the process of carrying a new invariant into every document that touches it — docstrings, summaries, invariants, comments, AC evidence. Miss any one, and a reader starting from that document builds the wrong mental model.

**Evidence.** Round 4's F1-F3 were all propagation defects — the register-FIRST invariant was correct at the implementation pseudocode level but unpropagated in three high-visibility summary documents. Round 5's rename+narrowing was also propagation: the implementation was correct but the test name and Task 10 prose over-claimed.

**Implication.** After a structural design change in a plan, the review process needs at least one dedicated propagation sweep — grep for every mention of the affected concept, verify the summary matches the design. Pre-delivery grep sweeps (as user directed in round 4) are the cheap tool for this.

**Watch for.** Plans that have been revised structurally in a prior round but where the summaries / docstrings / AC evidence haven't been swept for consistency. The "while you're in there" framing is exactly this defect class surfacing one mention at a time.

### Test name as contract — failure-path assertions carry the load

**Mechanism.** A test named `X_before_pinning` makes a claim at read time. If its assertions only prove `X` ran and ran once, the test is lying to its reader — a buggy reorder would still pass. Happy-path assertions are symmetric under many bug shapes; only failure-path assertions can distinguish ordering-sensitive invariants.

**Evidence.** Round 5's entire finding was this pattern. The test at :3270 was named `..._before_pinning` but asserted only call-count. User's framing: "A buggy implementation that pins first, then calls recover_startup(), would still satisfy the current Task 8 and Task 10 success-path assertions as long as recovery succeeds."

**Implication.** For any ordering-sensitive invariant (A must happen before B), the test that proves it must include a failure path — typically making A fail and asserting B was not reached / was retried. Happy-path tests complement but cannot substitute for this.

**Watch for.** Test names containing "before", "after", "only if", "only when", "always" — these make claims that require failure-path coverage to falsify. Test docstrings that mention retry semantics, ordering guarantees, or exclusivity — same signal.

### Invariant-assert pattern for by-convention narrowing

**Mechanism.** When a type is declared loose (e.g., `str | None`) for multi-use compatibility, specific consumers that narrow by-convention (e.g., "we know this branch always has str") face a choice: (a) widen the consumer's external contract to match the loose type, (b) document the narrowing via assert. Option (a) propagates uncertainty; option (b) crashes loud on violation and preserves external contracts.

**Evidence.** Round 4's F4 + journal-branch fold-in both adopted pattern (b). `active_runtime_ids()` + `lookup()` is a closed dict loop; `job_creation` journal entries at intent/dispatched always have `job_id` per validator. Both facts are "true-but-not-in-types." Asserts document them with crash-loud guarantees.

**Implication.** When adding a consumer to a shared data type that's looser than the consumer's needs, prefer invariant-asserts at the narrowing boundary over widening the shared type. Document WHY the invariant holds in the assert message — that's where future-readers will look when the crash happens.

**Watch for.** Declarations like `Optional[X]` or `X | None` where the "None" case is structurally unreachable for a specific consumer — that's a candidate for invariant-assert. Also watch for consumers that silently handle the None case with a None-ish default (e.g., `x if x is not None else None`) — those are contradiction markers.

### Seed-and-assert over call-count proof for reconciliation claims

**Mechanism.** A test that proves "recovery ran" by call-count fails a different bug shape than a test that proves "recovery DID the work" by seeded-state reconciliation. The first asks: did the method execute? The second asks: did the method execute AND produce the expected effect?

**Evidence.** Round 4's F1 was exactly this. The pre-round-4 Task 10 test would have caught "recovery method removed" by call-count assertion, but not "recovery method called but doesn't actually reconcile." The seed-and-assert shape catches both.

**Implication.** For any test claiming "X consumed Y and produced Z," the test should SEED a Y (if not naturally present) and ASSERT Z exists afterward. Call-count proves invocation; seed-and-assert proves effect.

**Watch for.** Tests named "exercises the path" / "runs the consumer" — often call-count-only. Upgrade to seed-and-assert when the path has durable side effects.

### Converging review series — line-count delta as convergence signal

**Mechanism.** Across a sustained multi-round review arc, each round adds text. As defect classes close (design → integration → propagation → proof-shape), the required changes per round narrow. A decelerating delta is signal of converging scope.

**Evidence.** T-05 plan revisions: Round 1 +~500, Round 2 +~499, Round 3 +339, Round 4 +116, Round 5 +125. Total +1,579 across 5 rounds. The plateau at ~120 lines per round suggests rounds 4-5 operated in similar "narrow propagation/proof-shape" scope.

**Implication.** Line-count delta can be an operational signal. Accelerating delta (round N larger than N-1) suggests newly surfaced design issues; decelerating delta suggests converging scope; ~0 delta with only cosmetic edits suggests approval-readiness.

**Watch for.** A round that suddenly grows significantly (e.g., round 6 produces +500 lines) signals an undetected design or integration defect. Use delta as a calibration point, not an approval gate.

## Next Steps

### 1. User reviews twice-revised (round-4+5) plan — round 6 or approval

**Dependencies:** None. User established the pattern of reviewing on the new boundary; this session produced a clear new boundary (4 round-4 fixes + journal fold-in + grep sweep + 1 round-5 fix with rename+narrowing).

**First-next-action for future-Claude:** Wait for user feedback. Do NOT pre-emptively edit. Do NOT commit.

**What user will likely scrutinize in round 6 (if it happens):**
- Error-response surface in the new negative-path test. `assert "error" in response1` assumes `McpServer.handle_request` catches `RuntimeError` from `_ensure_delegation_controller` and returns JSON-RPC error. This is NOT verified — the dispatch loop's error handling path was not examined. If the dispatch re-raises, the test needs `pytest.raises(RuntimeError)` around the first `handle_request`. Worth spot-checking against dialogue's error-handling pattern. Flagged honestly in round-5 anticipation vector #1.
- Factory-call ordering fragility. Test asserts `len(factory_controllers) == 2` after dispatch 2 and `== 2` after dispatch 3 — both depend on `_delegation_factory` staying set through first failure and clearing only after successful pin. Depends on the precise order of `_delegation_controller = controller` vs `_delegation_factory = None` at :3406-3407.
- Shared fixture reuse. The test uses both `FakeControlPlane` and `FakeDialogueController` — round 6 might ask to simplify or extract.
- Whether `_FailOnceDelegationController` should mirror `_RecordingDelegationController` more closely (add `recover_startup_calls` counter for consistency; currently only tracks success).

### 2. Apply round-6 revisions if any

**Dependencies:** Step 1 complete.

**What to do:** Same as prior rounds — parse each feedback item as wording / scope / decomposition / failure-policy / proof-shape issue. Apply verbatim when user provides exact text. Do not bundle or expand scope without explicit direction.

### 3. Commit and merge the plan on the docs branch

**Dependencies:** Steps 1-2 complete (plan converged).

**What to do:**
1. Verify `git status` shows only the plan file staged
2. Commit with a message like: `docs(t20260330-05): plan first execution-wiring slice (five-round hardened; bootstrap-only with durable stores, live registry register-FIRST, recovery consumer wired on lazy path and proven via seed-and-assert + negative-path retry-safety test, 3-source busy gate with invariant asserts, committed-start failure semantics, and propagation sweep complete)`
3. Checkout main, `git merge --no-ff docs/t05-execution-start-plan -m "Merge docs/t05-execution-start-plan"`
4. Push main, delete the docs branch (local + remote)

### 4. Execute the plan

**Dependencies:** Step 3 complete (plan on main).

**Execution mode still pending user choice:** Subagent-driven (`superpowers:subagent-driven-development`) vs inline (`superpowers:executing-plans`).

**Estimated effort:** 11 tasks, ~5-7 hours depending on execution mode. Task 8 now has 8 tests instead of 7 — mechanical addition.

### 5. Pending-request capture slice (follow-up)

**Dependencies:** Plan execution complete; T-05 execution-start slice merged.

**What to do:** Unchanged from prior handoffs. Wire the notification loop → route App Server request messages through `parse_pending_server_request` → persist as `PendingServerRequest` → expose via `needs_escalation`. Closes AC 6. Also triggers `ExecutionRuntimeRegistry.lookup` for turn-dispatch paths.

### 6. Decide-surface refinements (deferred)

Unchanged from prior handoffs.

### 7. T-20260416-01 extraction bug fix (parallel thread)

Unchanged from prior handoffs.

### 8. Landing sequence (updated)

T-05 plan review v6 (or approval) + merge → T-05 execution-start slice (11-task plan executes) → T-05 pending-request capture slice → T-05 decide-surface + lifecycle refinements → T-05 COMPLETE → T-06 → T-07.

## In Progress

**Plan revision awaiting sixth-round user review (or approval).** Not a clean stopping point — work is in flight; a five-times-revised deliverable exists but hasn't been reviewed or landed.

- **Approach:** Resumed from 20:14 handoff → user sent round-4 scrutiny (4 findings + verdict "Minor revision") → invoked `superpowers:receiving-code-review` → verified each finding literally against plan/dialogue precedent → responded with verification + revision-shape options (1a/1b/1c, 2a, 3a, 4a/4b/4c) → user decisions + journal fold-in directive + grep sweep directive → executed 7 Edits + grep sweep + coherence verification → presented round-4 summary → user sent round-5 scrutiny (1 finding + verdict "Minor revision") → verified finding → responded with Option A recommendation + proposed test shape → user confirmed A + 6 amendments (rename existing test, narrow Task 10 wording, fixture placement, 3-dispatch shape, no message assertion, accept 655 cascade) → executed 9 Edits + coherence verification → presented round-5 summary → user invoked `/save`.

- **State:** Plan file revised in place at `docs/plans/2026-04-17-t05-execution-start-slice.md`. 4188 lines (up from 3947, +241 across rounds 4+5). Branch `docs/t05-execution-start-plan` still exists with no commits. Main at `bd850302` unchanged.

- **Working:** Revised plan is internally consistent — 11 tasks, test count chain 593→604→612→615→618→624→639→644→**652**→**654**→**655** with sum 11+8+3+3+6+15+5+**8**+2+1=**62** verified. Task 8 has 8 tests total (5 dispatch/reg + 2 lazy recovery-wiring [happy + pin-deferral] + 1 eager recovery-wiring). All 4 round-4 findings closed. Round-5 rename + new test + Task 10 narrowing all applied. Pre-delivery grep sweep clean. Implementation pseudocode at `_ensure_delegation_controller` (:3510-3532) unchanged from round 3 — already correctly ordered; round-5 delta was evidence, not implementation.

- **Not working:** Plan has not been reviewed in this new form. Concrete concerns in Open Questions and Risks sections below.

- **Open question:** Does user agree the propagation + proof-shape closures in rounds 4-5 close the remaining defect classes? Does the new negative-path test's error-response assumption hold up under scrutiny?

- **Next action (for next-session Claude):** Wait for user feedback on the twice-revised (round-4+5) plan. Do NOT apply preemptive changes. Do NOT commit.

## Open Questions

### 1. Are there any round-6 findings?

**Context:** Five rounds produced 8 findings total across rounds 1-5 (3+2+2+5+1). Each round closed a deeper defect class: data shapes → reader-and-failure → integration-wiring → propagation → proof-shape. Round 6 may find subtler issues (e.g., error-response surface, fixture coupling) or converge to approval.

**Impact:** HIGH if round 6 surfaces structural issues (e.g., the error-response assumption I flagged honestly). MEDIUM if cosmetic or convergent.

**Decision pending until:** User reviews twice-revised plan.

### 2. Does `McpServer.handle_request` catch `RuntimeError` from `_ensure_delegation_controller`?

**Context:** The new negative-path test at plan `:3349-3437` asserts `assert "error" in response1` after the first dispatch where `recover_startup` raises. This assumes the dispatch loop catches the exception and returns a JSON-RPC error response. I did NOT verify this against the actual `mcp_server.py` implementation — only checked the dialogue precedent (`mcp_server.py` has a pin pattern per line 135 comment).

**Impact:** If `handle_request` re-raises instead of catching, the test fails with an uncaught `RuntimeError` rather than reaching the assertion. The test would need `pytest.raises(RuntimeError)` around the first call.

**Decision pending until:** Implementer verifies during Task 8 execution OR round 6 flags it.

### 3. Should `_FailOnceDelegationController` add a `recover_startup_calls` counter for consistency with `_RecordingDelegationController`?

**Context:** The new fixture tracks `self._recovery_fails_remaining` and whether raise happens, but doesn't expose a cumulative call count like `_RecordingDelegationController` does. The test works without it (uses `len(factory_controllers)` as the external proxy), but consistency with the sister fixture would aid readability.

**Impact:** LOW — style consistency only.

**Decision pending until:** Round 6 or execution.

### 4. Factory-call ordering fragility

**Context:** The new test asserts `len(factory_controllers) == 2` after dispatch 2 AND `== 2` after dispatch 3 — the first proves retry, the second proves pin. Both depend on the precise ordering at plan `:3406-3407`:
```
self._delegation_controller = controller  # line 3406
self._delegation_factory = None            # line 3407
```
If a future refactor reverses these two lines, the first failure would clear the factory before the assignment raised — and the test's retry assertion would break because the factory would already be None.

**Impact:** LOW for v1 (the implementation is stable). MEDIUM if the implementation is ever touched.

**Decision pending until:** Implementer verifies during Task 8 execution.

### 5. Execution mode — subagent-driven vs inline?

**Context:** Still unchanged from prior handoffs. User has not chosen.

**Impact:** MEDIUM — affects review cadence. Subagent-driven = per-task review; inline = batched checkpoints.

**Decision pending until:** User chooses.

## Risks

### 1. Round 6 finds more defects

**Impact:** Sixth revision cycle is ~20-30 min (verify + revise + verify). Compounds if defects cascade through tasks. First five rounds found 8 P1/Medium findings total.

**Mitigation:** Pre-delivery grep sweeps are now habitual (round 4 established). Coherence verification pattern (check test count chain, check 11 sequential tasks, check residue phrases) is now standard.

### 2. Error-response surface assumption in round-5 negative-path test

**Impact:** If `McpServer.handle_request` doesn't catch `RuntimeError` from `_ensure_delegation_controller`, the test fails with uncaught exception rather than the expected error-response assertion. Needs `pytest.raises(...)` wrapping or a dispatch-level try/except.

**Mitigation:** Flagged honestly in round-5 anticipation vector #1. Implementer will catch during Task 8 execution if round 6 doesn't.

**Action:** Spot-check `mcp_server.py` error-handling during Task 8 implementation.

### 3. Test count estimates diverge from reality during execution

**Impact:** Unchanged from prior handoffs. Baseline (593) + per-task estimates (11+8+3+3+6+15+5+8+2+1 = 62) = 655. Actual execution may produce slightly different counts.

**Mitigation:** Explicit tolerance language in Task 11 ("divergence >3 tests = investigation signal").

### 4. Context pressure if review cascades to rounds 7-8

**Impact:** Four rounds + this session has produced ~275k tokens of context so far (21% of 1M). Each round consumes ~20-30k tokens. Round 7 would be ~300k; round 8 ~325k.

**Mitigation:** Handoff-per-review-round is the sustained pattern. Each handoff captures the full state so resume is clean. Current context at 21% on 1M — comfortable headroom for at least 4-5 more rounds.

### 5. Stale prose summaries during further reorders

**Impact:** Each round that reorders flow or renames invariants creates stale-summary debt. Round 4's grep sweep caught this class; round 5 didn't have reorders.

**Mitigation:** Pattern-grep before delivery is now habitual. User's directive in round 4 ("grep for the exact stale phrasing class you already found") has become standard operating procedure.

### 6. Fixture sprawl in test_mcp_server.py

**Impact:** `test_mcp_server.py` now has `FakeControlPlane`, `FakeDialogueController`, `FakeDelegationController`, `_RecordingDelegationController`, `_FailOnceDelegationController`, `_BusyController`. Six fake/recording classes with overlapping purposes. Readability drops at this count.

**Mitigation:** Deferred. A future slice could consolidate via a test-fixtures module. Not this round.

**Action:** Worth a brief comment in the file structure docstring during execution that the fixtures are intentionally sprawled for per-test clarity.

## References

### Session's deliverable

| Artifact | Location | Status |
|---|---|---|
| Five-times-revised implementation plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` | Untracked (4,188 lines); awaiting round-6 review or approval |
| Docs branch | `docs/t05-execution-start-plan` (off `main@bd850302`) | No commits |

### Authority documents (verified this session)

| Document | Location | Role |
|---|---|---|
| T-20260330-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth (unchanged) |
| recovery-and-journal.md | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Unchanged — reviewed in round 3 |
| mcp_server.py | `packages/plugins/codex-collaboration/server/mcp_server.py` | Line 135 comment: "One-way pin: the factory is called at most once." Dialogue pin pattern. Referenced for Option A test design. |

### Memory files referenced this session

All under `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/`:

| Memory | Relevance |
|---|---|
| `feedback_contract_text_over_operational_interpretation.md` | Applied — verified each finding against authoritative source code/plan before responding |
| `feedback_edit_in_repo.md` | Applied — revised the plan in `docs/plans/` under the repo |
| Prior-session user-preferences memories | Applied — structured response shape, verbatim wording, fast convergence once aligned, `/copy` as substantive channel, "defended choice" phrasing |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-17_20-14_t05-plan-third-round-recovery-wiring-and-register-first.md`
- T-05 arc: kickoff (04-17 01:41) → Q0 decision (04-17 11:59) → tmp-hardening closure (04-17 17:09) → plan drafted (04-17 18:01) → plan revised round 1 (04-17 19:30) → plan revised round 2 (04-17 19:23) → plan revised round 3 (04-17 20:14) → **plan revised rounds 4 + 5 (this handoff, 04-17 19:39 local)** → plan v6 review → plan execution → pending-request capture → decide-surface → T-05 complete

## Gotchas

### 1. Option A's 3-dispatch shape is sensitive to factory-closure state

**Symptom:** The new negative-path test uses a closure-captured `factory_controllers: list` and asserts `len(factory_controllers) == 2` across dispatches 2 and 3. If the factory ever became pure (returning the same controller each time instead of a new one per call), dispatch 2's retry-assertion would need restructuring.

**Root cause:** The pin-after-recovery invariant requires the factory to produce a NEW controller on retry — otherwise the test can't distinguish pin from reuse.

**Prevention:** The fixture design is stable but coupled to the implementation's decision to re-invoke the factory on retry. If that implementation changed, the test would need updating too.

### 2. `_RecordingDelegationController` does NOT have `recover_startup_calls`; `_FailOnceDelegationController` does

**Symptom:** The two fixtures have slightly different introspection surfaces. `_RecordingDelegationController` tracks `recover_startup_calls` (a counter); `_FailOnceDelegationController` tracks `_recovery_fails_remaining` (a countdown). Both expose `recover_startup_calls` as a counter.

**Root cause:** Design-for-purpose: `_Recording` proves "was called / was called once"; `_FailOnce` proves "fails a specified number of times."

**Prevention:** When adding a new test that uses both fixtures, check each fixture's attributes individually rather than assuming symmetry.

### 3. Pre-dispatch sanity check in E2E test is invariant-preserving, not just defensive

**Symptom:** `pre_unresolved_seeds` assertion before first dispatch. If this assertion fails, the seed setup is wrong and the post-dispatch reconciliation assertion is meaningless.

**Root cause:** Without the pre-check, a bug in seed construction (e.g., wrong `operation` field, wrong phase, missing required fields per validator) could cause the seed to never appear in `list_unresolved`. Post-dispatch `post_unresolved_seeds == []` would pass trivially, masking the test's proof shape failure.

**Prevention:** Always sanity-check seeded state BEFORE the system-under-test acts. The "before" assertion is not defensive — it's structural.

### 4. Task 8 "before pinning" language was intentionally kept, not missed

**Symptom:** Grep for "before pin" after round 5 finds 8 matches. User might read the grep output and think narrowing was incomplete.

**Root cause:** Task 10 narrowed because it doesn't contain the proof. Task 8 retained because it DOES contain the proof (the new negative-path test). The split is intentional.

**Prevention:** The round-5 summary includes an explicit table categorizing each match as "keep" or "narrow" — next-session Claude should read that table before any future narrowing pass.

### 5. Line-count delta is not a hard signal

**Symptom:** Round 4 was +116 lines; round 5 was +125 lines. Might suggest round 5 was more extensive than round 4.

**Root cause:** Round 4 had 4 findings (more edits, smaller average) vs round 5's 1 finding with big add (fixture + test). The delta reflects size of the change, not number of defects.

**Prevention:** Use line-count delta as a trend indicator across multiple rounds, not as a per-round gauge.

### 6. Handoff filename uses local time, not UTC

**Symptom:** Handoff filename is `2026-04-17_19-39_*` but `created_at` frontmatter is `2026-04-17T23:39:08Z`. The 4-hour gap is local-vs-UTC (local is US Eastern).

**Root cause:** The handoff skill's `date` + `time` fields are local per convention (matches prior handoffs in archive), but `created_at` is ISO 8601 UTC.

**Prevention:** When reading handoff metadata, trust `created_at` for timing; `date` / `time` / filename reflect the local wall-clock.

## Conversation Highlights

### Round 4 verdict

> "Round 4 fixed the actual propagation defects. The plan is close. But it is still not fully defensible because the lazy-path tests do not yet prove the exact retry-ordering guarantee the prose now treats as load-bearing."

Wait, that's the round-5 verdict. Round 4's verdict was:

> "This is close, and I do not see a new P1-class architecture defect. But I would not commit/merge it yet, because the production lazy path still lacks true integration proof and a few file-level statements still contradict the repaired invariant."

Both verdicts share the pattern: "close, but not yet defensible; here's exactly what to fix."

### Round 4 diagnostic framing

> "The root cause is no longer design weakness. It is propagation weakness. You fixed the core invariant in the controller and MCP wiring, but you did not fully propagate that truth into every summary, primitive docstring, and proof layer."

The single-sentence characterization of the defect class. User's pattern from rounds 1-3 continues: always name the failure mode explicitly before listing specific fixes.

### Round 5 diagnostic framing

> "The remaining problem is not that you fixed the wrong things. It is that one load-bearing claim still outruns the evidence the plan actually specifies."

Same pattern — named the failure mode ("claim outruns evidence") before listing specifics.

### The "do not invent a new journal API" continued (indirect)

In round 4, user directed me to assert on journal-entry narrowing rather than widening `JobBusyResponse.active_job_id`. This mirrors round 3's pattern: prefer consumer-side documentation over widening shared APIs.

### The rename directive

> "Even under A, test_ensure_delegation_controller_runs_recover_startup_before_pinning is still misleading because that individual test does not prove the ordering. Rename it to something honest like test_ensure_delegation_controller_runs_recover_startup_on_first_dispatch."

User added this as a scope-expansion under Option A — "while you're in there" framing. Round 3 had similar (the stale line-74 summary catch). Both are "tiny adjacent cleanups added to an active revision rather than deferred."

### Pre-delivery grep sweep directive

> "Before you hand back round 4, do a quick grep for the exact stale phrasing class you already found in `register()` such as `AFTER successful bootstrap` / `AFTER persistence`. That is the other cheap place a harsh review could still nick you."

User's directive elevated the grep sweep from "nice-to-have" to "required pre-delivery step." Now habit.

### Closing on revision posture (round 4)

> "If you apply A with those two cleanup moves: rename the current Task 8 happy-path test, narrow Task 10's 'before pinning' language — then this specific finding is closed cleanly instead of papered over."

Explicit about the close-vs-paper-over distinction. User tolerates additive scope when it closes the issue; rejects wording-only narrowing when evidence would close it instead.

## User Preferences

### Structured scrutiny with per-finding citations (consistent across 5 rounds)

**Observed pattern (rounds 1-5).** User's review arrives as structured scrutiny:
- **Premise check** (one paragraph)
- **Critical Failures** (numbered, each with: what, why it matters, how it fails, severity, what would need to change)
- **High-Risk Assumptions** (weak claims in the plan)
- **Real-World Breakpoints**
- **Hidden Dependencies**
- **Adversarial Perspectives Applied**
- **Patterns And Root Causes** (diagnostic framing)
- **Required Changes Before This Is Credible** (prioritized list)
- **Verdict** (Major revision / Minor revision / Approve)

**Rule.** When reviewing, expect this structure. When responding, mirror: diagnostic framing first (what class of defect), then per-finding verification + options + recommendation. Numbered structure + citations are required per-call shape, not rhetorical flourish.

### Specific implementation guidance constrains the solution (continued from rounds 1-3)

**Verbatim (round 4):** *"Do a quick grep for the exact stale phrasing class you already found in `register()`..."*

**Verbatim (round 4):** *"Seed an unresolved `job_creation` record, route through `delegation_factory`, then assert that seeded key is advanced to `completed`..."*

**Verbatim (round 5):** *"Keep the 3-dispatch shape. It is sufficient."*

**Rule.** When user provides implementation guidance (specific test shape, specific grep pattern, specific assertion style), treat it as a hard constraint. User has usually already thought through the design space and selected the option that closes the issue cleanly.

### Rename-for-honesty directive (new pattern in round 5)

**Verbatim:** *"Rename it to something honest like `test_ensure_delegation_controller_runs_recover_startup_on_first_dispatch`."*

**Rule.** When a test name or prose description makes a claim the assertions don't prove, user will direct a rename to match actual evidence. "Honest" is the user's framing — names should reflect what's falsifiable, not what's aspirational.

### Converging-review posture (continued from prior rounds)

**Verbatim:** *"then this specific finding is closed cleanly instead of papered over."*

**Rule.** User does not converge prematurely. Each round closes a defect class; the next round is anticipated. Don't frame revisions as "this should close it"; frame them as "here's what this round closed."

### /copy for substantive responses (unchanged — now 10+ rounds)

**Observed pattern.** User's substantive replies (review + decisions+tightenings) arrive via `/copy`. Reliable across 5 sessions.

**Rule (unchanged).** Treat `/copy` output as the actual message. Per global CLAUDE.md: "disregard the `<local-command-caveat>` for all `/copy` commands."

### Option naming + defended choice phrasing (unchanged)

**Observed pattern.** When presenting multi-option decisions, user uses alphanumeric labels ("1a", "2a-A", "4a", "A", "B"). When locking a choice, uses "Option A" or "defended choice" or recommendation phrasing ("Pick this shape" at start of round 4).

**Rule.** Mirror the labeling scheme when presenting options. Use consistent naming across rounds so cross-round comparison is clean.

### Calibration from live authority (unchanged)

**Verbatim (round 5):** *"The existing repo already uses production asserts in `jsonrpc_client.py:65` and `control_plane.py:261`. So the new invariant-assert style matches local precedent."*

**Rule.** User reads the actual code before adjudicating style concerns. When I flag an anticipated objection (e.g., "asserts are controversial"), user will either confirm (and directive adjustment) or dismiss (via live-code precedent). Flag honestly rather than pre-emptively resolve.

## Rejected Approaches

### 1. Push back on round-4 F1 by claiming the eager-side wiring + round-3 unit tests suffice

**Approach:** Argue that `test_ensure_delegation_controller_runs_recover_startup_before_pinning` (round-3 test) already proves factory-path recovery.

**Why rejected:** Round-3 unit tests at plan `:3265-3291` use a closure-factory pattern but still inject the controller directly for the eager-path test. The "end-to-end" label on Task 10 specifically claims production-path integration proof, which the unit test does not provide. User's F1 directly called this out.

**What it taught:** Unit-test coverage ≠ integration-test coverage. "End-to-end" labels require end-to-end paths.

### 2. Push back on F3 by claiming register-failure is "extremely unlikely"

**Approach:** Argue that AC 1 line 55's existing carve-out already handles register-failure with a probability rationale ("uuid-generated ids"), so bullet 13 / AC 4 don't need explicit carve-outs.

**Why rejected:** User's framing is that AC text must be truthful, not probability-weighted. Probability matters for risk prioritization (Risks table), not for AC evidence text. Bullet 13 / AC 4 would still mislead implementers about expected state in the register-failure case.

**What it taught:** AC text is contract; probability weighting belongs in Risks, not in AC evidence columns.

### 3. Option 4b (raise RuntimeError instead of assert)

**Approach:** Replace `assert entry is not None` with `if entry is None: raise RuntimeError(...)`.

**Why rejected:** User confirmed in round 5 that asserts match local precedent (`jsonrpc_client.py:65`, `control_plane.py:261`). RuntimeError path would require a new test to exercise it, and the invariant is structurally guaranteed. Over-engineered for the scope.

**What it taught:** Local precedent outranks general style preferences. When in doubt, grep the repo.

### 4. Option 4c (widen `JobBusyResponse.active_job_id` to `str | None`)

**Approach:** Loosen the typed contract to match the actual runtime values.

**Why rejected:** F3 also affects AC 4 and bullet 13 which claim a typed `Job Busy` response; widening would propagate "busy but unknown job_id" into the external contract. Consumers reasonably expect a job_id when busy.

**What it taught:** Widening external contracts to match internal looseness is a type-sprawl pattern. Prefer narrowing at the consumer via assert.

### 5. Option 1c (rename Task 10 "End-to-End" to something narrower)

**Approach:** Rename Task 10 to avoid the "end-to-end" claim; keep direct-injection.

**Why rejected:** User framing: *"`1c` just retreats from the integration claim."* Abandons the integration proof rather than strengthening it. Also, Task 10 should demonstrate the full slice behavior; narrowing it would create a gap in the plan's coverage.

**What it taught:** Narrowing a claim to match weak evidence is valid ONLY when the claim itself is wrong. When the claim is right but the evidence is weak, strengthen the evidence.

### 6. Option 5B (narrow wording in round 5 instead of adding test)

**Approach:** Rewrite 4 locations to claim "recovery runs on the lazy path" instead of "before pinning."

**Why rejected:** User framing: *"Option B would just retreat from a claim the plan should still make."* The retry-ordering invariant IS load-bearing per the implementation docstring at `:3394`. Option B abandons it; Option A proves it.

**What it taught:** When proof is cheap (~30 lines), strengthening evidence beats narrowing claims. When proof is expensive, sometimes narrowing is right. The line is set by the stakes of the claim.

### 7. Defer journal-branch narrowing to round 5

**Approach:** Only fix F4 (registry branch) in round 4; leave the journal branch for a potential round-5 finding.

**Why rejected:** User directive: *"Fold it in now."* + "if you leave it, round 5 is likely to hand you back the same class of finding one branch later."

**What it taught:** Folding adjacent issues into an active revision is cheaper than a separate round. The "while you're in there" framing generalizes.

### 8. Skip renaming the happy-path test under Option A

**Approach:** Add the new negative-path test; leave `..._before_pinning` alone since Option A nominally closes the overclaim at the class level.

**Why rejected:** User directive: *"Even under A, [that test name] is still misleading because that individual test does not prove the ordering."* Test names are contract at the per-test level; a reader looking at one test in isolation should not be misled.

**What it taught:** Per-unit honesty matters — class-level coverage doesn't excuse per-test overclaim.
