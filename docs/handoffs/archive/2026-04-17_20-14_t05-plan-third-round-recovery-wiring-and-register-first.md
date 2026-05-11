---
date: 2026-04-17
time: "20:14"
created_at: "2026-04-17T20:14:17Z"
session_id: 4252cf98-936f-4978-87ab-2648012c728a
resumed_from: "docs/handoffs/archive/2026-04-17_19-23_t05-plan-second-round-recovery-consumer-added.md"
project: claude-code-tool-dev
branch: docs/t05-execution-start-plan
commit: bd850302
title: "T-05 plan third-round revision — recovery wiring on lazy path + register-FIRST committed-start ordering"
type: handoff
files:
  - docs/plans/2026-04-17-t05-execution-start-slice.md
---

# T-05 Execution-Start Plan — Third-round revision after two new P1 findings

## Goal

Turn the 19:23 handoff's awaiting-review state into the next scrutiny → revision round. User returned two new P1 findings on the twice-revised plan: (1) the lazy delegation path never runs `recover_startup` (production deploys via factory, so the consumer-half of AC 4 is structurally unwired), and (2) the lineage-failure case still leaves a live runtime subprocess unreachable from the in-process registry — recreating the original orphan-runtime bug inside what was supposed to be the committed-start failure mode. Plus three weak assumptions (one of which — "trimmed" overstates physical compaction — was structurally correct and required a 6-location wording sweep). Verdict: "Major revision."

**Bigger picture.** T-05 is the execution-domain foundation for codex-collaboration. Each scrutiny round closes a deeper class of defects. Round 1 closed data-shape defects (handle missing, runtime orphaned, journal absent). Round 2 closed reader-and-failure defects (no consumer for the journal; no policy for write failures after dispatch). Round 3 closed integration defects: defining a consumer is not the same as wiring it on the production path; defining a failure-mode taxonomy is not the same as making sure the in-process owner is established BEFORE the first fallible write. The remaining problems are no longer conceptual — they're integration-grade.

**Trigger.** User replied to the prior session's "awaiting third-round review" posture via `/copy` with two `code-comment` tags (P1 findings citing exact line ranges) followed by a structured "Scrutiny" message (premise check, critical failures with verbatim citations, weak assumptions, real-world breakpoints, hidden dependencies, adversarial perspectives, root cause framing, required-changes list, verdict).

**Success criteria for this session:**

1. ✅ Each cited finding verified literally against the plan + dialogue precedent + journal.py before responding (zero performative agreement).
2. ✅ Both P1 findings confirmed as structurally correct (not pushed back).
3. ✅ User's calibration about `OperationJournal.compact()` already existing acknowledged but NOT used to widen the slice (3a not 3b).
4. ✅ User's specific implementation guidance respected: busy gate consults `journal.list_unresolved` filtered by operation in the controller (do NOT invent a new journal API parameter).
5. ✅ User's bonus catch (line 74 stale flow summary) folded into the revision.
6. ✅ Plan revised in place; publication posture unchanged (local merge-and-push, no remote yet).
7. ✅ All coherence checks pass: 11 tasks sequential, 0 "trimmed per :59" residue, 0 "rebuilds the live view" residue, test counts chain cleanly through 654, no `registry_persisted` unused-flag risk.

All seven met. Plan at `docs/plans/2026-04-17-t05-execution-start-slice.md` still untracked; HEAD unchanged at `bd850302`; branch still `docs/t05-execution-start-plan`.

## Session Narrative

**Phase 1 — Load handoff (~immediate).** `/load` resolved the 19:23 handoff cleanly from the active directory; archived to `docs/handoffs/archive/`; state file written at `.session-state/handoff-4252cf98-936f-4978-87ab-2648012c728a`. Positioning set correctly per the handoff's "next action": wait for user review, do not pre-emptively edit.

**Phase 2 — Receive third-round scrutiny (~immediate).** User posted via `/copy`: two `code-comment` tags (Finding 1 at plan:2793-2805, Finding 2 at plan:1902-1931) followed by a Scrutiny message with premise check ("This is finally the correct slice"), critical failures with verbatim citations to plan AND `mcp_server.py:122, :132`, three weak assumptions (trimming overclaim, register failure asymmetry, same-session-retry-after-lineage-failure unsafe), real-world breakpoints, hidden dependencies, adversarial perspectives, root-cause framing ("the remaining problems share one root cause: integration failures, not conceptual ones"), and required-changes list. Verdict: "Major revision."

**Phase 3 — Apply `superpowers:receiving-code-review` skill (~30s).** Invoked the skill before responding. Key rule engaged: "Verify. Question. Then implement." Forbidden: performative agreement, blind implementation.

**Phase 4 — Verify each finding literally (~5 min, batched parallel reads).** Eight parallel reads to ground every cited line:
- Plan `:1-75` (line 9 prose, AC 1, AC 4, file structure)
- Plan `:1880-1970` (line 1902 lineage-failure test)
- Plan `:2225-2385` (lines 2236-2245 controller docstring + lines 2330-2382 try block)
- Plan `:2760-2835` (line 2772 trim wording + Step 7.4 wiring)
- Plan `:3000-3050` (line 3015 `_ensure_delegation_controller`)
- Plan `:3180-3230` (line 3201 production wiring via factory)
- `mcp_server.py:110-185` (dialogue precedent — eager `startup()` at line 122-130 AND lazy `_ensure_dialogue_controller` at line 132-151)
- `recovery-and-journal.md:50-80` (line 61 trimming contract — "near-empty during normal operation")

Every cited line held exactly. The dialogue precedent at `mcp_server.py:147` was the load-bearing confirmation: dialogue runs `controller.recover_startup()` BEFORE pinning inside `_ensure_dialogue_controller`. The plan's `_ensure_delegation_controller` had no such call — and Task 9's production wiring uses `delegation_factory`, so the lazy path is exclusively how production runs. Finding 1 verified.

For Finding 2: plan `:2330-2367` shows the try-block writes lineage FIRST, registry THIRD; plan `:1931` lineage-failure test asserts `registry.lookup("rt-1") is None`; busy gate at `:2249-2261` consults `job_store.list_active()` only. So lineage failure → no handle, no job, no registry, journal at dispatched, busy gate cleared → same-session retry spawns another runtime subprocess. The "registry entry is retained" docstring claim at `:2243-2244` is structurally false for the lineage-failure mode. Finding 2 verified.

**Phase 5 — Analyze AC consequences (~2 min).** AC 1 currently ✅ with text claiming "registry entry and at least an unknown-marked handle are always present on disk + in memory." False for lineage-failure path. AC 4 currently ✅ with "Wired into mcp_server.py session init alongside dialogue.recover_startup." False on the production path. Both ACs need either: (a) reorder + busy-gate widening (Finding 2) and lazy-path wiring (Finding 1), OR (b) downgrade with text noting the gap.

**Phase 6 — Respond with verification + AC consequences + revision-shape options (~3 min).** Structured response:
1. Insight block (3 educational points: lazy-vs-eager precedent, blast-radius asymmetry between dialogue and delegation, "trimmed" vs "no longer returned by list_unresolved")
2. Literal citation confirmation for each finding (table format with quotes from each cited file)
3. Weak-assumption verification (trim, register-no-test, same-session-retry-unsafe)
4. AC consequence table (current / Finding-1-only / Finding-2-only / both-fixed)
5. Revision shape with explicit options:
   - Finding 1: only 1a (mirror dialogue exactly) is credible — no real choice
   - Finding 2: 2a-A (reorder + 3-source busy gate) / 2a-B (busy gate only, no reorder) / 2b (narrow AC, keep code as-is)
   - Trimming: 3a (wording-only, 3 edits) / 3b (implement compaction)
6. Process question + scope cap + explicit hold-until-decision

Recommended `1a + 2a-A + 3a` (named the recommendation, did not choose unilaterally).

**Phase 7 — User response: clear decisions + 6 specific tightenings (~2 min via `/copy`).** User confirmed `1a + 2a-A + 3a`, revise in place now. Six tightenings:

1. **Finding 1 fix shape:** Two distinct call sites (eager in `startup()`, lazy inside `_ensure_delegation_controller` BEFORE pinning). Test must exercise the factory route, since production goes through `delegation_factory` not directly-injected controller.

2. **Finding 2 amendment:** 2a-A is correct AND requires repairing the wording it invalidates. The plan currently says "registry entry and at least an unknown-marked handle are always present on disk + in memory" at line 55 (AC 1), line 2236 (docstring), and line 9 (top-level prose). False after reorder for the register-failure case. Keep AC 1 as a **live ownership** claim; durable identity / recovery truth stays under AC 4. Split `runtime_registry.register` failure out of the generic "registry entry is retained" bucket.

3. **Busy gate guidance:** Consult three things — `job_store.list_active()`, `runtime_registry.active_runtime_ids()`, and unresolved `job_creation` entries filtered from the existing `journal.list_unresolved(session_id=...)` call. **Do not invent a new journal API parameter** — Task 7 already filters by `operation` in the controller; mirror that pattern.

4. **Trimming sweep is bigger than 3 edits:** User identified 6 locations: lines 9, 36, 58, 2180, 2772, 3588. Replace all with "resolved" / "no longer returned by `list_unresolved()`" semantics.

5. **Calibration: `compact()` already exists** at `journal.py:228`. So 3b is not impossible — but no controller currently calls `compact()`, and bundling it now would widen the slice and create a new behavior surface. Wording-only is the right boundary for this round.

6. **Bonus stale-summary fix:** Line 74 still says `journal completed → audit emit`, contradicting Task 6's audit-before-completed invariant. Not a new blocker but should not survive the next revision.

User closing: *"Bottom line: revise in place now with `1a + 2a-A + 3a`, plus the AC/docstring wording repair and the stale line-74 summary fix, then bring the revised plan back for another harsh pass."*

**Phase 8 — Plan the edit sequence (~1 min).** Identified ~13 logical edit groups across 6 phases:
- Phase 1: 6 trimming wording edits
- Phase 2: CommittedStartFinalizationError + Failure semantics docstrings
- Phase 3: Step 6.3 docstring flow order + remaining 2 trim mentions
- Phase 4: Busy gate extension to 3 sources
- Phase 5: Try-block reorder (register FIRST) + catch block update
- Phase 6: Existing failure tests assertion flips
- Phase 7: NEW register-failure test + NEW busy-gate widening tests
- Phase 8: Step 7.4 restructure (eager-only)
- Phase 9: Task 8 `_ensure_delegation_controller` recover_startup() addition
- Phase 10: Task 8 test additions (TestDelegationRecoveryWiring)
- Phase 11-12: Test count cascade across Tasks 6-11
- Phase 13: Risks table addition (register-failure orphan row)
- Phase 14-15: Coherence verification + post-edit cleanup

**Phase 9 — Execute revision (~40 min, ~25 Edit calls + 4 grep verification calls).**

Phase 1 (6 trim edits): line 9 (live-vs-durable prose with register-FIRST framing), line 36 (Scope #13 — mentioned eager + lazy wiring split), line 58 (AC 4 evidence — same wiring split), line 55 (AC 1 evidence — honest register-failure carve-out), line 74 (file structure — full reorder), line 2772 (recover_startup comment).

Phase 2 (docstrings): CommittedStartFinalizationError class docstring rewritten to handle both lineage/job/audit/completed AND register-failure paths separately; controller `start()` `Failure semantics` block restructured into 3 bullets (pre-dispatched / register-failure / lineage+job+audit+completed).

Phase 3 (Step 6.3 controller docstring at 2069-2089): rewrote flow order with `runtime_registry.register` listed FIRST and audit BEFORE completed; updated 3-source busy-gate description in the flow comment. Line 3588 Risk row updated for trimming wording.

Phase 4 (busy gate at 2249-2261): expanded from 13 lines to ~50 lines. Added registry consultation (`registry.active_runtime_ids()` + `lookup` for response detail) and journal consultation (filtered for `operation == "job_creation"`). Each branch produces a `JobBusyResponse` with appropriate `active_job_id` and detail string.

Phase 5 (try block reorder at 2390-2500): moved `runtime_registry.register` to FIRST in try block; added new ORDER MATTERS comment with 3 numbered invariants (register first / completed last / audit before completed); rewrote catch-block comment to handle the register-failure case (no flag-branch needed since handle_persisted/job_persisted both False); updated `CommittedStartFinalizationError` message to mention "if registry registration was the failure, will simply advance the journal with no durable identity to mark."

Phase 6 (existing failure tests): flipped 2 assertions (`assert registry.lookup("rt-1") is None` → `is not None`) at lines 1931 (lineage failure) and 1966 (job-store failure). Comment updated for both. Other 2 tests (journal-completed at line 2010 and audit at line 2053) already asserted `is not None` correctly — no change needed.

Phase 7 (NEW tests, ~110 lines added to Step 6.1 test code block):
- 5th committed-start failure test: `test_start_raises_committed_start_finalization_error_on_register_failure` — uses `monkeypatch.setattr(registry, "register", _boom)`, asserts `CommittedStartFinalizationError` raised, journal at dispatched, NO entry in registry/lineage/job (all three None).
- Busy-gate widening test 1: `test_start_returns_busy_when_registry_has_entry_but_job_store_empty` — pre-registers a runtime in the registry, calls `controller.start`, asserts `JobBusyResponse` returned with active_job_id matching pre-registered job_id.
- Busy-gate widening test 2: `test_start_returns_busy_when_unresolved_journal_entry_present` — writes intent + dispatched journal entries directly, calls `controller.start`, asserts `JobBusyResponse` returned. (Caught a minor bug mid-edit: forgot to close the markdown code fence after the new tests; verified with grep + targeted fix.)

Phase 8 (Step 7.4 restructure): rewrote to be eager-only (only modifies `startup()`, not `_ensure_delegation_controller`). Added explicit "Why only the eager path here" paragraph explaining the chicken-and-egg with Task 8. Updated Step 7.5 expected count from 6 to 5 tests, baseline 642 → 644. Updated Step 7.6 git add to remove `test_mcp_server.py` (no longer touched in Task 7). Updated Task 7 Goal text + Task 7 Files section to reflect the eager+lazy split.

Phase 9 (Task 8 `_ensure_delegation_controller` code block): added `controller.recover_startup()` call BEFORE pin (matches dialogue precedent at `mcp_server.py:147`). Added load-bearing docstring explaining why production lazy-factory path needs it.

Phase 10 (Task 8 test additions): added `TestDelegationRecoveryWiring` class with 2 tests after `TestDelegateDispatch`. Test 1 (lazy): factory yields a recording controller; first dispatch triggers `_ensure_delegation_controller` → `recover_startup` → pin; second dispatch reuses pinned controller (no second `recover_startup`). Test 2 (eager): controller injected directly; `startup()` triggers `recover_startup` once; idempotent on second `startup()` call.

Phase 11 (Step 8.4 + 8.2 expected): updated to reflect 7 new tests (5 dispatch/registration + 2 wiring) and baseline 644 → 651. Step 8.2 pytest command extended to include the new TestDelegationRecoveryWiring class.

Phase 12 (Task 9, 10, 11 cascade): updated running totals — Task 9: 651 → 653; Task 10: 653 → 654; Task 11 verify: ~654 with breakdown 11+8+3+3+6+15+5+7+2+1=61 added across Tasks 1-10.

Phase 13 (Task 6 + 7 + 8 Goal cleanups): updated Step 6.4 expected (12 → 15 tests, 624+12=636 → 624+15=639). Updated Task 6 Goal flow paragraph (registered runtime first, audit before completed). Updated Task 7 Goal (eager+lazy wiring split). Updated Task 8 Goal (mentions lazy-path wiring landing here).

Phase 14 (Risks table): added new row for register-failure orphan after the asymmetric-partial-state row. Documents the leak (subprocess persists until parent exits), mitigations (register is in-memory dict on uuid; collision structurally impossible), and reopen trigger (if registry adds external state).

Phase 15 (coherence verification + cleanup):
- Grep for `trimmed per recovery-and-journal.md:59`: 0 occurrences ✓
- Grep for `rebuilds the live view`: 0 occurrences ✓
- Grep for `alive by accident`: 0 occurrences ✓
- Grep for `^## Task \d`: 11 sequential headers ✓
- Grep for `registry.lookup.*is None`: 4 occurrences (3 expected + 1 register-failure test) ✓
- Removed unused `registry_persisted` flag (would trigger ruff F841 in implementation)
- Found and updated 2 stale "session init" references at line 88 (modified files table) + line 2700 (Task 7 Files)
- Updated "all four committed-start failure modes" → "all five" at line 2023
- Updated `Write ordering invariant` docstring to enumerate 3 invariants (register first / completed last / audit before completed)
- Final line count: 3947 (was 3608 → +339; total +999 across 3 revision rounds)
- Test count chain verified: 593 → 604 → 612 → 615 → 618 → 624 → 639 → 644 → 651 → 653 → 654

**Phase 10 — Present revision summary to user (~2 min).** Structured summary covering: structural deltas, task-by-task changes (deltas vs prior round), AC table impact, test count chain (with explicit sum verification), coherence checks (with hit counts), what was NOT changed, and explicit fourth-round scrutiny anticipation (4 likely vectors: busy-gate race semantics / test ordering / `_ensure_delegation_controller` exception handling / JobBusyResponse `active_job_status="unknown"` populate).

**Phase 11 — User invoked `/save` (immediate).** Writing this handoff now.

## Decisions

### Decision 1: Accept both P1 findings without pushback

**Choice:** Both Finding 1 (lazy delegation path never runs `recover_startup`) and Finding 2 (lineage-failure path leaves orphan runtime) verified as structurally correct and accepted as binding revisions.

**Driver.** Each finding cited specific lines that held literally:
- Plan `:2793-2803` (Step 7.4) only modified `startup()` (eager). Plan `:3015-3030` (`_ensure_delegation_controller`) had no `recover_startup()` call. Dialogue precedent at `mcp_server.py:147` shows dialogue runs recovery in BOTH places.
- Plan `:2330-2367` shows lineage as the FIRST post-dispatched write; plan `:1931` test asserts `registry.lookup is None`; plan `:2249-2261` busy gate consults `job_store.list_active()` only. End state: subprocess live, no entry anywhere, busy gate clears, retry duplicates.

**Alternatives considered:**
- **Push back on Finding 1 by claiming the eager-side wiring is sufficient:** rejected because Task 9 production wiring uses `delegation_factory` (plan `:3201`); the lazy path is the ONLY production path. Eager-side wiring covers test fixtures, not production.
- **Push back on Finding 2 by claiming the busy gate's job_store consultation suffices:** rejected because lineage failure means no job in store; busy gate clears; retry succeeds.

**Implications.** Plan grows by ~339 lines (3608 → 3947). Try block reorders. Busy gate widens to 3 sources. 5th failure test added. 2 new busy-gate widening tests added. Step 7.4 + Task 8 split-wiring. AC 1 evidence text rewritten to be honest about the register-failure exception. AC 4 evidence text rewritten to mention both eager + lazy wiring.

**Trade-offs accepted.** Larger Task 6 (15 tests vs 12). Slightly more complex busy gate (3 branches vs 1). One more invariant (register-FIRST) for implementers to remember. Outweighed by AC 1 + AC 4 becoming truthful instead of overclaim.

**Confidence:** High (E2) — verified against authoritative source (`mcp_server.py` + `journal.py` + plan); user-cited line numbers all held exactly.

**Reversibility:** High at plan level (still text-editable); low at execution level (executing the original would have produced two real bugs at first crash recovery + first lineage-failure scenario).

**Change trigger:** None — findings grounded in normative code that won't change.

### Decision 2: Reorder try block to put register FIRST (was lineage first)

**Choice:** New post-dispatched ordering: `runtime_registry.register` → `lineage_store.create` → `job_store.create` → `journal.append_audit_event` → `journal.write_phase(completed)`.

**Driver.** The registry is the in-process owner of the runtime subprocess. If any subsequent write fails before register, the subprocess is unreachable — no busy-gate signal, no teardown path, no future turn-dispatch handle. User Tightening #2: *"either register live ownership before the first fallible post-`dispatched` write and make the busy gate consult that live state... or narrow the failure guarantee."*

**Alternatives considered:**
- **Register OUTSIDE the try block:** rejected because register can theoretically raise (RuntimeError on duplicate runtime_id). Putting it outside means an unwrapped exception path with the journal at dispatched and subprocess live.
- **Register-as-special-case (separate try with separate handler):** rejected as over-engineered. The existing `Exception as exc:` catch handles it cleanly; both `handle_persisted` and `job_persisted` are False so no `update_status` calls fire.
- **Generate `runtime_id` independently of `start_execution_runtime`** so register can happen BEFORE journal-dispatched: rejected because `runtime_id` semantically requires runtime bootstrap to have succeeded.

**Implications.** Task 6 Goal flow paragraph + Step 6.3 docstring + line 74 file structure description all updated to show register-FIRST. AC 1 evidence updated. Two existing failure-test assertions flipped (`is None` → `is not None`). New 5th failure test for register itself raising. Risks table gains a register-failure orphan row.

**Trade-offs accepted.** One additional state to reason about: register failure leaves the subprocess permanently unreachable in the current process. Documented in the new risk row + the controller docstring's failure-mode bullet. Mitigation: register is in-memory dict insertion on uuid-generated key — collision structurally impossible.

**Confidence:** High (E2) — verified by reading the existing registry implementation at plan `:1450-1499` (`register()` raises only on duplicate; `lookup()` returns the entry with `job_id`; both confirmed in plan).

**Reversibility:** High — single-block reorder in Step 6.3 implementation pseudocode.

**Change trigger:** If the registry adds external state (e.g., persistence layer) that introduces non-trivial failure modes, the register-failure risk row would need expansion.

### Decision 3: Busy gate consults THREE sources (not 2 or new API)

**Choice:** New busy gate consults `job_store.list_active()` (existing), `runtime_registry.active_runtime_ids()` (new), and unresolved `job_creation` journal entries via `journal.list_unresolved(session_id=...)` filtered in the controller (new).

**Driver.** Each source covers a distinct case:
- `job_store.list_active`: healthy in-flight jobs (`queued`/`running`/`needs_escalation`).
- `registry.active_runtime_ids`: same-session retry after lineage/job/audit/completed failure (where register succeeded but downstream failed).
- `journal.list_unresolved` filtered by `operation == "job_creation"`: cross-session retry while the journal still has dispatched entries (registry is fresh; durable state is the only signal). Also covers the register-failure case in the same session (no registry, no job, but journal at dispatched).

User Tightening #3: *"I would make the busy gate consult three things: `job_store.list_active()`, `runtime_registry.active_runtime_ids()`, and unresolved `job_creation` entries filtered from the existing `journal.list_unresolved(session_id=...)` call. Do not invent a new journal API just for this; the plan already filters by `operation` in Task 7."*

**Alternatives considered:**
- **Add an `operation` parameter to `journal.list_unresolved`:** rejected by user directive — Task 7's `recover_startup` already does this filtering in the controller; mirror that pattern for consistency.
- **Two-source busy gate (job_store + registry, no journal):** rejected because cross-session leftover entries wouldn't block retry until `recover_startup()` advances them.
- **Single-source busy gate (journal only):** rejected because it would mean reading the JSONL on every start call (slower than in-memory checks).

**Implications.** Busy gate code grew from ~13 lines to ~50 lines. Two new tests cover the new sources. `JobBusyResponse` now produced from registry/journal sources too — uses `active_job_status="unknown"` (the literal includes `"unknown"` per Task 1's status extension).

**Trade-offs accepted.** Three sources mean three lookups per `start` call. All in-memory (job_store and registry) or single JSONL replay (journal). Negligible overhead.

**Confidence:** High (E1) — direct user directive; pattern mirrored from Task 7.

**Reversibility:** High — independent branches; can collapse if profiling shows them unnecessary.

**Change trigger:** N/A — directive is clear.

### Decision 4: Split Step 7.4 (eager) and Task 8 (lazy) for recovery wiring

**Choice:** Step 7.4 wires only the eager-side `startup()` recovery call. The lazy-factory wiring (`controller.recover_startup()` inside `_ensure_delegation_controller` BEFORE pinning) lands inside Task 8.

**Driver.** Task 8 is what introduces `_ensure_delegation_controller`. Task 7 cannot edit code that does not yet exist. The dialogue precedent is split this way too — `mcp_server.py:128-129` (eager) + `mcp_server.py:147` (lazy). Production deploys via `delegation_factory` (Task 9), so the Task-8 lazy wiring is the load-bearing one for AC 4's consumer half.

**Alternatives considered:**
- **Reorder Tasks: MCP first, then recovery:** rejected because it violates the user's prior directive ("Add a new Task 7 for recovery; renumber MCP to Task 8").
- **Both wiring calls in Step 7.4 (Task 7 introduces both `startup()` mod AND a forward-reference to Task 8's `_ensure_delegation_controller`):** rejected as confusing — Task 7's commit would be incomplete because the lazy-path code doesn't exist yet.

**Implications.** Step 7.4 stays minimal. Task 8 grows by ~50 lines (the `controller.recover_startup()` call + the docstring update + 2 new wiring tests). Task 7 test count drops from +6 to +5 (mcp wiring test moved to Task 8). Task 8 test count rises from +5 to +7. Test count chain end-to-end: 593→604→612→615→618→624→639→644→651→653→654.

**Trade-offs accepted.** Cross-task coordination — anyone reading Task 7 alone might wonder where the lazy-path wiring is. Mitigated by explicit "Why only the eager path here" paragraph in Step 7.4.

**Confidence:** High (E1) — direct chicken-and-egg constraint; structural.

**Reversibility:** Medium — reorganizing across tasks would require rebase if executed.

**Change trigger:** N/A.

### Decision 5: 3a (wording-only) over 3b (implement compaction), despite `compact()` existing

**Choice:** Replace all "trimmed per recovery-and-journal.md:59" mentions with "no longer returned by `list_unresolved()`" / "physical compaction via `OperationJournal.compact()` is a separate operation not invoked in this slice."

**Driver.** User Tightening #5: *"`OperationJournal` already has `compact()` in journal.py:228. That means `3b` is not impossible, but it is still the wrong move here. No controller recovery path currently calls `compact()`, so bundling it now would widen the slice and create a new behavior surface. For this round, wording-only is the right boundary."*

**Alternatives considered:**
- **3b (implement compaction):** call `journal.compact()` from `recover_startup` after advancing all phases. Rejected because it widens scope into "when do we trim" policy questions that belong elsewhere (likely poll/promote slices or a periodic background sweep).
- **Mixed (some "trimmed", some "resolved"):** rejected for inconsistency; user wants all 6 locations swept uniformly.

**Implications.** 6 locations updated: lines 9, 36, 58, 2180, 2772, 3588. Plus 2 secondary mentions found during coherence check (line 3007 in recover_startup comment — already in updated context; line 3925-3926 in Risks table — explicitly mentions "compact() is not invoked in this slice"). Total: 8 wording locations clarified.

**Trade-offs accepted.** Slight verbosity — every mention now needs to clarify what's NOT done. Mitigated by consistent phrasing.

**Confidence:** High (E1) — direct user directive supported by codebase verification (`compact()` exists at `journal.py:228`; no controller calls it currently).

**Reversibility:** High — text-editable; compact() can be wired in any future slice.

**Change trigger:** If the journal grows unbounded in practice and steady-state "near-empty" is no longer maintained, a compact-wiring pass would be needed.

### Decision 6: Remove unused `registry_persisted` flag (clean code)

**Choice:** After initial implementation included a `registry_persisted` boolean flag for documentation purposes, removed it because the catch block doesn't branch on it (the catch block only checks `handle_persisted` and `job_persisted`).

**Driver.** Internal coherence — the implementation pseudocode in the plan is meant to compile cleanly. An unused variable would trigger ruff F841 in any sane linter. Better to inline the explanation in comments than to keep a non-load-bearing flag.

**Alternatives considered:**
- **Keep the flag and use it in the error message** (e.g., `f"...registry_persisted={registry_persisted}..."`) — rejected as superficial use; the message already mentions "if registry registration was the failure" via the chained exception.
- **Use the flag in a logging statement** — rejected because the plan doesn't use logging in this controller block.

**Implications.** Catch block comment updated from "If `registry_persisted` is True (the common case)..." to "If register succeeded (the common case)..." — same information, no flag.

**Confidence:** High (E1) — straightforward refactor.

**Reversibility:** High.

**Change trigger:** If implementation needs to branch on register success (e.g., to decide whether to release the registry entry on failure), the flag should be re-introduced.

## Changes

### Files modified (this session)

| File | Change | Commit |
|---|---|---|
| `docs/plans/2026-04-17-t05-execution-start-slice.md` | Revised in place: 3608 → 3947 lines (+339). Try-block reorder (register FIRST). Busy gate widened to 3 sources. New 5th committed-start failure test (register failure). Two new busy-gate widening tests (registry-only / journal-only busy). Step 7.4 restructured to eager-only. Task 8 `_ensure_delegation_controller` adds `controller.recover_startup()` before pin. Task 8 adds `TestDelegationRecoveryWiring` class with 2 tests (lazy + eager). 6 trim-wording fixes (lines 9, 36, 58, 2180, 2772, 3588) + 2 secondary mentions (lines 3007, 3925-3926) clarified. AC 1 evidence rewritten (honest register-failure carve-out). AC 4 evidence rewritten (eager+lazy wiring split). CommittedStartFinalizationError docstring restructured. `start()` docstring's `Failure semantics` block restructured into 3 bullets. Line 74 stale flow summary fixed. Line 88 modified-files description updated. Line 2700 Task 7 Files updated. Line 2023 audit-test docstring (4 → 5 failure modes). Risks table gains register-failure orphan row. Cleanup: `registry_persisted` unused flag removed (ruff F841 prevention). Test count chain: 593→604→612→615→618→624→**639**→**644**→**651**→**653**→**654**. | Uncommitted |

### Git state changes

| Commit | Branch | Subject |
|---|---|---|
| (none) | `docs/t05-execution-start-plan` | Branch unchanged; plan still untracked |

No commits. No push. Main unchanged at `bd850302`.

### Handoff / state files

- Archived (at session start): `2026-04-17_19-23_t05-plan-second-round-recovery-consumer-added.md` → `docs/handoffs/archive/`
- State file: `docs/handoffs/.session-state/handoff-4252cf98-936f-4978-87ab-2648012c728a` — to be cleaned by this save
- New handoff (this file): `docs/handoffs/2026-04-17_20-14_t05-plan-third-round-recovery-wiring-and-register-first.md`

## Codebase Knowledge

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `docs/handoffs/2026-04-17_19-23_t05-plan-second-round-recovery-consumer-added.md` | Prior handoff (resumed) | Full context: plan revised twice, awaiting third-round review |
| `docs/plans/2026-04-17-t05-execution-start-slice.md` (multiple ranges) | Ground revision edits | All cited line numbers held literally |
| `packages/plugins/codex-collaboration/server/mcp_server.py` (lines 110-185) | Verify dialogue precedent | TWO recovery call sites: `startup()` at :128-129 (eager) AND `_ensure_dialogue_controller` at :147 (lazy, BEFORE pin). User's :122 cite was eager; :132 was the lazy method header. |
| `packages/plugins/codex-collaboration/server/journal.py` (lines 200-289) | Verify journal API | `list_unresolved(*, session_id) -> list[OperationJournalEntry]` — no `operation` parameter. `compact(*, session_id)` exists at line 228 with atomic temp-file-rename + fsync. `_terminal_phases` groups by idempotency_key, returns latest phase per key. `list_unresolved` filters `phase != "completed"`. |
| `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` (lines 50-80) | Verify trimming contract | Line 61: "Completed operations are trimmed from the journal after their outcome is confirmed. The journal should be near-empty during normal operation and only accumulate records for in-flight operations." Silent on HOW trimming happens — `list_unresolved` returns terminal records that are `phase != "completed"`. Compact is separate. |

### Architecture: dialogue precedent for recovery wiring (verified literally)

| Call site | File:line | What it does |
|---|---|---|
| Eager startup | `mcp_server.py:122-130` | `startup()` checks `if self._dialogue_controller is not None: self._dialogue_controller.recover_startup()`. Idempotent via `_recovery_completed` guard. |
| Lazy factory | `mcp_server.py:132-151` | `_ensure_dialogue_controller`: builds from factory, runs `controller.recover_startup()`, then pins. Pin happens AFTER recovery so transient failures allow retry. |

The plan's `_ensure_delegation_controller` (Task 8 at plan `:3015-3030` post-revision) now mirrors this exactly.

### Architecture: post-dispatched flow (final shape after this revision)

| Step | Action | Failure consequence |
|---|---|---|
| 1 | `journal.write_phase("dispatched")` | Raw exception; journal at `intent`; no committed state |
| 2 | `runtime_registry.register(...)` | `CommittedStartFinalizationError`; journal at dispatched; NO entry, no handle, no job; subprocess leaks until parent exits |
| 3 | `lineage_store.create(handle)` | `CommittedStartFinalizationError`; journal at dispatched; registry HAS entry (busy gate blocks retry); no handle, no job |
| 4 | `job_store.create(job)` | Same; registry has entry; handle marked unknown; no job |
| 5 | `journal.append_audit_event(...)` | Same; registry has entry; handle + job both marked unknown |
| 6 | `journal.write_phase("completed")` | Same; this is the TERMINAL write — completing it means the operation is replay-safe |

### Architecture: 3-source busy gate (new in this revision)

| Source | Catches | Implementation |
|---|---|---|
| `job_store.list_active()` | Healthy queued/running/needs_escalation jobs | Existing — unchanged |
| `registry.active_runtime_ids()` | Same-session retry after committed-start failure where register SUCCEEDED | New — calls `lookup` for response detail |
| `journal.list_unresolved(session_id=...)` filtered in-controller for `operation == "job_creation"` | Cross-session leftover dispatched entries; same-session register-failure case (no registry, no job, but journal at dispatched) | New — uses existing journal API; filter is in the controller per Task 7 pattern |

### Surprising findings / gotchas

- **`journal.compact()` already exists.** At `journal.py:228-246`. Atomic temp-file-rename + fsync. No controller calls it currently. User explicitly said NOT to wire it in this round (3a not 3b) — bundling would widen slice scope.
- **Dialogue runs recovery in TWO places.** User's Finding 1 cited `mcp_server.py:122` (eager) and `:132` (lazy method header — the actual `recover_startup` call is at `:147`). The plan only mirrored the eager pattern. Production deploys via factory, so the lazy wiring is exclusively load-bearing.
- **`list_unresolved` has no `operation` parameter.** Filter is done in the controller. Per Task 7 pattern; user explicitly forbade adding a parameter.
- **`ExecutionRuntimeRegistry.register` raises `RuntimeError` on duplicate.** Verified at plan `:1468-1472`. The new register-failure test uses `RuntimeError` for boom, consistent with the registry's actual error type.
- **`ExecutionRuntimeRegistry.lookup` returns `ExecutionRuntimeEntry | None`.** The entry has `job_id` field (plan `:1477`). Used by the new busy-gate's registry branch to populate `JobBusyResponse.active_job_id`.
- **Stale-summary lines accumulate across revision rounds.** Line 74's flow summary survived round 2 because that round didn't touch file structure ordering. User caught it in round 3. Lesson: a coherence grep for "register" + "audit" + "completed" sequence patterns would catch flow-summary drift earlier.
- **Markdown code-fence closure is fragile during multi-block insertions.** When I added the new failure test + 2 busy-gate tests inside Step 6.1's code block, I inadvertently dropped the closing ``` because it was part of the `old_string` surrounding the Step 6.2 marker. Caught via grep + targeted Edit.
- **Unused vars in plan code blocks trip ruff F841.** Initial implementation used `registry_persisted = True/False` as a documentation-only flag. Removed because the catch block doesn't branch on it; the explanation lives in comments instead.

### Key locations to remember

| Concept | Location |
|---|---|
| T-05 plan (revised third time) | `docs/plans/2026-04-17-t05-execution-start-slice.md` |
| Dialogue eager startup recovery | `packages/plugins/codex-collaboration/server/mcp_server.py:122-130` |
| Dialogue lazy factory recovery (the load-bearing precedent) | `packages/plugins/codex-collaboration/server/mcp_server.py:132-151` (the call is at `:147`) |
| Journal `list_unresolved` (no operation param) | `packages/plugins/codex-collaboration/server/journal.py:212-219` |
| Journal `compact` (exists, NOT invoked in this slice) | `packages/plugins/codex-collaboration/server/journal.py:228-246` |
| Recovery contract trimming spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md:59-61` |
| ExecutionRuntimeRegistry register/lookup signatures | Plan lines 1450-1499 |

## Context

### Mental model

**Framing:** This was a **third-round integration scrutiny round trip**, one layer deeper than rounds 1 and 2. Round 1 was about data shapes. Round 2 was about reader-and-failure semantics. Round 3 was about whether the consumer is wired on the production path AND whether the in-process owner is established before any fallible write.

- **Core insight:** *Defining a consumer is not the same as wiring it on the production path. Defining a failure-mode taxonomy is not the same as making the in-process owner exist before any fallible write.* Both findings exposed the gap between "the code is documented to do X" and "the production path actually invokes X." Plans can have correct components and incorrect integration.
- **Mental model:** *Layered integration check.* For any "X is wired" claim: (1) X exists, (2) X is correct in isolation, (3) X is invoked, (4) X is invoked on the load-bearing path. The plan-as-contract review process catches (1) and (2) trivially. Catching (3) and especially (4) requires reading the actual code paths that production deploys.

Secondary insight: **the registry-FIRST ordering for committed-start writes is delegation-specific, not a dialogue-mirror.** Dialogue's `start` has 1 post-dispatched local write (lineage); ordering doesn't matter much. Delegation's `start` has 4-5 post-dispatched writes; the FIRST one becomes the load-bearing ownership establishment point. Following dialogue's `start` ordering blindly would import the bug.

### Project state at session close

**T-20260330-05 (execution-domain foundation):** OPEN, high priority. Plan revised THREE times now (round 1, round 2, round 3). Still uncommitted on `docs/t05-execution-start-plan`. Awaiting **fourth** scrutiny pass per user's pattern — will review the revised plan on the new boundary.

**T-20260330-06 / T-07:** OPEN, blocked by T-05.

**T-20260416-01 (codex.dialogue.reply extraction mismatch):** OPEN, medium priority. Independent parallel thread — unchanged this session.

### Environment snapshot at session close

- Branch: `docs/t05-execution-start-plan` (unchanged)
- HEAD: `bd850302` (unchanged)
- Working tree: **dirty** — `docs/plans/2026-04-17-t05-execution-start-slice.md` still untracked (now 3947 lines)
- Plugin suite: not run this session (no code changes)
- Memory: no new feedback files; MEMORY.md unchanged

### Why this work matters (bigger picture)

T-05 is the execution-domain foundation for codex-collaboration. A plan that defines a recovery consumer but doesn't wire it on the production path would produce a real bug at first crash recovery: unresolved journal records accumulate; AC 4's "state persisted strongly enough for promotion to inspect" is structurally false because nothing reads the records. A plan that orders committed-start writes with lineage first would produce a real bug at first lineage-failure: orphan runtime, busy gate cleared, retry duplicates the runtime. Both bugs would be caught at execution time — by then the cost is partial implementation, test expectations wrong, commit history messy.

This round was ~50 min of work that prevents 2-4 hours of execution-time rework. The review process is still paying off, three rounds in. The remaining defects are now integration-grade rather than conceptual — likely round 4 finds 0-2 issues; round 5 may converge to approval.

## Learnings

### Defining a consumer ≠ wiring it on the production path

**Mechanism.** Round 2's plan added `recover_startup()` and wired it via "session init alongside dialogue.recover_startup". The eager-side wiring fires only if the controller is provided directly — fine for tests but not production. Production deploys via factory; the lazy path was structurally unwired. The plan's text said "wired" but the code path proved otherwise.

**Evidence.** User's Finding 1 traced the literal call sites: `mcp_server.py:122-130` (eager) calls only if `_dialogue_controller is not None`; `mcp_server.py:147` (lazy, inside `_ensure_dialogue_controller`) is what production exercises. Plan's `_ensure_delegation_controller` had no `recover_startup()` call. AC 4's "consumer wired" claim was unwired in production.

**Implication.** AC verification self-reviews must add a fifth check beyond text/contract/producer/consumer: **path verification** — is the consumer invoked on the production code path? For lazy-factory patterns, this means tracing through the factory invocation, not just the eager session-init.

**Watch for.** Any AC that claims a behavior is "wired" or "invoked" — verify the lazy/production path actually invokes it, not just the eager/test path.

### Blast radius determines whether ordering of committed-start writes matters

**Mechanism.** A controller with N post-dispatched local writes has N points where partial failure can leave inconsistent durable state. If N=1 (dialogue's `start`), only one ordering question exists: completed-write-failure leaves the operation unresolved. If N=4-5 (delegation's `start`), each write between dispatched and completed is a potential failure point — and the ORDER determines which intermediate states are reachable.

**Evidence.** Round 2's plan ordered lineage→job→registry→audit→completed (matching dialogue's mental model where "ownership is local-only"). Round 3 reordered to registry→lineage→job→audit→completed because registry is the in-process owner of the runtime subprocess; without registry registered FIRST, lineage failure leaves the subprocess unreachable AND the busy gate clear.

**Implication.** When mirroring a pattern from a sibling controller, count the post-side-effect local writes in BOTH. If they differ, the ordering rules need to be re-derived for the larger N. Don't import dialogue's order; derive delegation's from first principles.

**Watch for.** Any plan that says "mirrors X's pattern" without enumerating the writes both sides perform. Pattern-mirroring is a rough sketch, not a substitute for ordering analysis.

### `list_unresolved` filter belongs in the caller, not the API

**Mechanism.** The journal stores entries for multiple operations (`thread_creation`, `turn_dispatch`, `job_creation`, etc.). Each consumer (dialogue's `recover_startup`, delegation's `recover_startup`, delegation's busy gate) wants only its own operation type. Adding an `operation` parameter to `list_unresolved` would be a leaky abstraction — the journal doesn't need to know about caller semantics.

**Evidence.** User Tightening #3 explicitly forbade adding the parameter: *"Do not invent a new journal API just for this; the plan already filters by `operation` in Task 7."* Task 7's `recover_startup` already does `[e for e in entries if e.operation == "job_creation"]` after calling `list_unresolved`. Mirror that pattern in the busy gate.

**Implication.** When introducing a new consumer for an existing API, default to filtering in the consumer. Adding parameters to shared APIs is a last resort — they accumulate combinatorially across caller types.

**Watch for.** Any temptation to "just add an operation filter" or similar caller-specific parameter to a shared journal/store/registry API. Check whether the existing caller already filters; if so, mirror it.

### Stale-summary lines accumulate across revision rounds

**Mechanism.** When a plan is revised in place, prose summaries of the flow are easy to update LOCALLY but hard to track GLOBALLY. Round 2 reordered audit-before-completed in the Step 6.3 implementation but missed line 74's file-structure description (still showed `journal completed → audit emit`). Round 3's reorder (register-FIRST) creates new opportunities for the same drift.

**Evidence.** User Tightening #6 caught line 74 — explicitly noted as "not a new blocker, but it should not survive the next revision." Confirmed via grep: line 74 said `register runtime → journal completed → audit emit` (round 2's old order). Updated to `register runtime → persist handle → persist job → audit emit → journal completed` (round 3's new order with register-first).

**Implication.** Coherence verification after a flow reorder MUST grep for prose summaries of the flow (look for "→" arrow patterns or sequential write enumeration). Code blocks are easy to update; prose mirrors are easy to miss.

**Watch for.** After any reorder, grep for the affected step names in sequence. If they appear in summary form anywhere outside the changed code block, update or flag.

### Plan code blocks should compile-check (ruff F841 et al.)

**Mechanism.** When writing illustrative pseudocode in a plan, it's tempting to introduce documentation-only variables ("a flag named `X` indicates that Y happened, used in the message below..."). If the variable isn't actually used in a branch or expression, ruff F841 will trigger when implementers copy the pseudocode verbatim. The plan pseudocode is a contract; it should be lintable.

**Evidence.** Initial Phase 5 implementation introduced `registry_persisted = False / True` as a flag for the catch block to "know" whether register succeeded. The catch block doesn't branch on it (the explanation is in a comment). Removed during Phase 15 cleanup; replaced with "If register succeeded (the common case)..." comment.

**Implication.** Plan code blocks should pass the same linters as production code. Comments are free; flags must earn their keep.

**Watch for.** Any variable assigned in plan pseudocode that doesn't appear on a right-hand side or in a branch condition. If it's documentation-only, inline the documentation as a comment.

## Next Steps

### 1. User reviews the thrice-revised plan (fourth round)

**Dependencies:** None. User established the pattern of reviewing on the new boundary; this session produced a clear new boundary (recovery wired on lazy path; register-FIRST committed-start ordering; 3-source busy gate; trimming wording sweep complete).

**First-next-action for future-Claude:** Wait for user feedback on the revision. Do NOT preemptively apply changes. Do NOT commit the plan before review.

**What user will likely scrutinize in this round:**
- Whether the busy-gate's 3-source consultation has any race semantics worth naming (all three are local reads in the same controller call; no race in practice)
- Whether the test ordering in Step 6.1 should be reordered to match write order (currently: lineage / job / journal-completed / audit / register / busy-registry / busy-journal; write order: register / lineage / job / audit / journal-completed)
- Whether `_ensure_delegation_controller`'s recover_startup call should also handle exceptions (dialogue's at :147 doesn't — it lets them propagate; matching is correct, but worth confirming)
- Whether `JobBusyResponse.active_job_status="unknown"` is correctly typed (the literal accepts "unknown" per Task 1's status extension; verified)
- Whether the new `_RecordingDelegationController` test fixture in `TestDelegationRecoveryWiring` should mirror existing `FakeDelegationController` patterns more closely (currently it adds a `recover_startup` method — minimal addition; could be merged with FakeDelegationController if user prefers)

### 2. Apply user revisions (if any)

**Dependencies:** Step 1 complete.

**What to do:** Same as prior three rounds — parse each feedback item as wording / scope / decomposition / failure-policy issue. Apply verbatim when user provides exact text. Do not bundle or expand scope without explicit direction.

### 3. Commit and merge the plan on the docs branch

**Dependencies:** Steps 1-2 complete (plan converged).

**What to do:**
1. Verify `git status` shows only the plan file staged
2. Commit with: `docs(t20260330-05): plan first execution-wiring slice (bootstrap-only, with durable stores, live registry register-FIRST, recovery consumer wired on lazy path, 3-source busy gate, and committed-start failure semantics)`
3. Checkout main, `git merge --no-ff docs/t05-execution-start-plan -m "Merge docs/t05-execution-start-plan"`
4. Push main, delete the docs branch (local + remote)

### 4. Execute the plan

**Dependencies:** Step 3 complete (plan on main).

**Execution mode still pending user choice:** Subagent-driven (`superpowers:subagent-driven-development`) vs inline (`superpowers:executing-plans`).

**Estimated effort:** 11 tasks, ~5-7 hours depending on execution mode (unchanged from prior estimate; new tests are mostly mechanical).

### 5. Pending-request capture slice (follow-up)

**Dependencies:** Plan execution complete; T-05 execution-start slice merged.

**What to do:** Unchanged from prior handoffs. Wire the notification loop → route App Server request messages through `parse_pending_server_request` → persist as `PendingServerRequest` → expose via `needs_escalation`. Closes AC 6. Also triggers `ExecutionRuntimeRegistry.lookup` for turn-dispatch paths.

### 6. Decide-surface refinements (deferred)

Unchanged from prior handoffs.

### 7. T-20260416-01 extraction bug fix (parallel thread)

Unchanged from prior handoffs.

### 8. Landing sequence (updated)

T-05 plan review v4 + merge → T-05 execution-start slice (11-task plan executes) → T-05 pending-request capture slice → T-05 decide-surface + lifecycle refinements → T-05 COMPLETE → T-06 → T-07.

## In Progress

**Plan revision awaiting fourth-round user review.** Not a clean stopping point — work is in flight; a thrice-revised deliverable exists but hasn't been reviewed or landed.

- **Approach:** Resumed from 19:23 handoff → user sent third-round scrutiny (2 P1 + 3 weak assumptions + bonus stale-summary catch + verdict "Major revision") → invoked `superpowers:receiving-code-review` → verified each finding literally against `mcp_server.py` + `journal.py` + plan → responded with verification + AC consequences + revision shape options (1a, 2a-A/B/2b, 3a/b) → user decisions + 6 tightenings → executed ~25 Edits + 4 grep verification calls → coherence verification + cleanup → presented summary to user → user invoked `/save`.
- **State:** Plan file revised in place at `docs/plans/2026-04-17-t05-execution-start-slice.md`. 3947 lines (up from 3608, +339). Branch `docs/t05-execution-start-plan` still exists with no commits. Main at `bd850302` unchanged.
- **Working:** Revised plan is internally consistent — 11 tasks, 56 task steps + 2 Pre-Flight steps, AC table evidence column has truthful claims for both AC 1 and AC 4, committed-start failure semantics covers 5 modes (was 4), busy gate covers 3 sources (was 1), trimming wording uniformly accurate, test counts chain cleanly (593 → 604 → 612 → 615 → 618 → 624 → 639 → 644 → 651 → 653 → 654 with sum 11+8+3+3+6+15+5+7+2+1=61 verified).
- **Not working:** Plan has not been reviewed in this new form. Concrete concerns in Risks section below.
- **Open question:** Does user agree the lazy-path wiring + register-FIRST ordering close the remaining integration gaps? Does the 3-source busy gate satisfy AC 1's live-ownership claim?
- **Next action (for next-session Claude):** Wait for user feedback on the thrice-revised plan. Do NOT apply preemptive changes. Do NOT commit.

## Open Questions

### 1. Are there any fourth-round findings?

**Context:** Three rounds produced 5 P1 findings total (3 in round 1, 2 in round 2, 2 in round 3). Each round closed deeper defects than the prior. Round 4 may find subtler issues or converge to approval.

**Impact:** HIGH if round 4 surfaces more structural issues (e.g., race between busy-gate sources, test fixture issues, unverified type assumptions). Lower if cosmetic or convergent.

**Decision pending until:** User reviews thrice-revised plan.

### 2. Should the busy gate's 3 sources be checked under a single lock?

**Context:** Each source is a local lookup (in-memory dict for job_store + registry; JSONL replay for journal). No race exists in single-threaded Python flow. But if the controller is ever called concurrently (unlikely — MCP serializes), there's a window between checking source A and source B where state could change.

**Impact:** LOW for v1 (MCP serializes dispatch). MEDIUM if dispatch ever becomes concurrent.

**Decision pending until:** Concurrency model changes (not in this slice).

### 3. Should `TestDelegationRecoveryWiring._RecordingDelegationController` be merged with the existing `FakeDelegationController`?

**Context:** I added a new fixture class with `recover_startup` + `start` methods. The existing `FakeDelegationController` has `start` only. Could either: (a) extend `FakeDelegationController` with `recover_startup`, or (b) keep `_RecordingDelegationController` separate.

**Impact:** LOW — style choice. Separate is currently used; extension would reduce fixture count by 1.

**Decision pending until:** Round 4 review or execution.

### 4. Should the test order in Step 6.1 match the write order in Step 6.3?

**Context:** Step 6.1 lists tests in document-order (lineage / job / journal-completed / audit / register / busy-registry / busy-journal). Step 6.3 implementation has write order (register / lineage / job / audit / completed). They differ for the failure tests.

**Impact:** LOW — readability. Reordering the test definitions to match the write order would help readers cross-reference.

**Decision pending until:** Round 4 or execution.

### 5. Execution mode — subagent-driven vs inline?

**Context:** Still unchanged from prior handoffs. User has not chosen.

**Impact:** MEDIUM — affects review cadence. Subagent-driven = per-task review; inline = batched checkpoints.

**Decision pending until:** User chooses.

## Risks

### 1. Fourth-round review finds more integration defects

**Impact:** Fourth revision cycle is ~30-45 min (verify + revise + verify). Compounds if defects cascade through tasks. First three rounds found 5 P1s total; the fourth could find 0-2.

**Mitigation:** Coherence grep pass at end of this session caught 2 additional stale "session init" mentions (lines 88, 2700) and 1 stale "four committed-start" reference (line 2023). Pattern-grep before delivery is now habitual.

### 2. Test count estimates diverge from reality during execution

**Impact:** Unchanged from prior handoffs. Baseline (593) + per-task estimates (11+8+3+3+6+15+5+7+2+1 = 61) = 654. Actual execution may produce slightly different counts.

**Mitigation:** Explicit tolerance language in Task 11 ("divergence >3 tests = investigation signal").

### 3. Register-failure orphan subprocess persists until parent exits

**Impact:** If `runtime_registry.register` raises after `dispatched`, the runtime subprocess is unreachable from any in-process structure. Subprocess-discovery teardown is out of scope for this slice. Mitigation: register is in-memory dict insertion on uuid-generated key — collision is structurally impossible (P ≈ 2^-122). The failure mode exists for completeness (e.g., monkeypatched in tests).

**Action:** Documented in Risks table row + controller docstring. If the registry ever adds external state (e.g., persistence layer), the failure modes broaden and this becomes a real concern.

### 4. Busy gate's three sources could disagree

**Impact:** If `job_store.list_active()` returns one job_id and `registry.active_runtime_ids()` returns a different runtime_id (e.g., after a poll/promote slice updates one but not the other), the busy gate returns the FIRST signal it finds. Caller sees inconsistent identifiers in the response across calls.

**Mitigation:** In-slice (T-05), this can't happen because only `start` writes to registry/job_store. Out-of-slice (poll/promote), the sources will be co-managed. Not a v1 concern.

**Action:** None this round. Worth a comment in poll/promote slices to maintain co-management.

### 5. New `_RecordingDelegationController` fixture in test_mcp_server.py may need import adjustments

**Impact:** The fixture class is defined inline within Step 8.1's pytest module. References `Path` from `pathlib`, `DelegationJob` from `server.models`. Both already imported at the top of the file (verified by checking other fixture classes use them).

**Mitigation:** The fixture is structurally identical to `FakeDelegationController` plus a `recover_startup` method; if the existing one compiles, the new one will too.

### 6. Context pressure if review cascades to a fifth round

**Impact:** Three rounds + this session has produced ~250k tokens of context (current usage 252k/1M). A fifth round could push toward 400-500k. Still within 1M model context, but cache pressure increases.

**Mitigation:** Handoff-per-review-round is the sustained pattern. Each handoff captures the full state so resume is clean. Current context at 25% — comfortable headroom for at least one more round, possibly two.

### 7. Stale prose summaries during reorder cycles

**Impact:** Round 2 missed line 74; round 3 caught it via user observation. Future reorders carry the same risk if the coherence grep doesn't enumerate prose summary patterns.

**Mitigation:** Lesson logged in Learnings. Habit: after any flow reorder, grep for "→" arrow patterns and sequential-write enumerations across the entire plan.

## References

### Session's deliverable

| Artifact | Location | Status |
|---|---|---|
| Thrice-revised implementation plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` | Untracked (3947 lines); awaiting fourth-round review |
| Docs branch | `docs/t05-execution-start-plan` (off `main@bd850302`) | No commits |

### Authority documents (verified this session)

| Document | Location | Role |
|---|---|---|
| T-20260330-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth (unchanged) |
| recovery-and-journal.md | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Line 35 (journal-before-dispatch); 47 (idempotency keys); **59-61 (trimming as steady-state, no compact requirement)** |
| mcp_server.py | `packages/plugins/codex-collaboration/server/mcp_server.py` | Lines 119-130 (eager `startup()`); 132-151 (lazy `_ensure_dialogue_controller` — recovery at :147 BEFORE pin). Both call sites mirrored in delegation across Step 7.4 (eager) and Task 8 (lazy). |
| journal.py | `packages/plugins/codex-collaboration/server/journal.py` | Line 212-219 (`list_unresolved` — no operation parameter); 228-246 (`compact` — exists with atomic temp-file-rename + fsync; NOT invoked in this slice) |

### Memory files referenced this session

All under `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/`:

| Memory | Relevance |
|---|---|
| `feedback_contract_text_over_operational_interpretation.md` | Applied — verified each finding against authoritative source code/contract before responding |
| `feedback_edit_in_repo.md` | Applied — revised the plan in `docs/plans/` under the repo |
| Prior-session user-preferences memories | Applied — structured response, verbatim user wording, fast convergence once aligned, `/copy` as substantive channel, "defended choice" phrasing |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-17_19-23_t05-plan-second-round-recovery-consumer-added.md`
- T-05 arc: kickoff (04-17 01:41) → Q0 decision (04-17 11:59) → tmp-hardening closure (04-17 17:09) → plan drafted (04-17 18:01) → plan revised round 1 (04-17 19:30) → plan revised round 2 (04-17 19:23) → **plan revised round 3 (this handoff, 04-17 20:14)** → plan v4 review → plan execution → pending-request capture → decide-surface → T-05 complete

## Gotchas

### 1. Dialogue runs recovery in TWO places, not one

**Symptom:** Round 2 plan only mirrored the eager-side recovery wiring. The lazy factory path was structurally unwired. Production deploys via factory.

**Root cause:** Initial reading of dialogue's recovery focused on `startup()` at line 122-130 (eager). Missed `_ensure_dialogue_controller` at line 132-151 (lazy, recovery at :147 BEFORE pin).

**Prevention:** When mirroring a controller pattern, enumerate ALL call sites of the method being mirrored. Grep for `recover_startup` in the source file, not just the most-visible site.

### 2. `journal.list_unresolved` has no `operation` parameter — filter in caller

**Symptom:** Initial busy-gate design considered passing `operation="job_creation"` to `list_unresolved`. The API doesn't accept it.

**Root cause:** Confused with how Task 7's `recover_startup` filters — that does `[e for e in entries if e.operation == "job_creation"]` AFTER calling the API.

**Prevention:** Before adding parameters to shared APIs, check whether existing callers do filtering themselves. If yes, mirror.

### 3. Plan code blocks need to be lint-clean (ruff F841)

**Symptom:** Initial implementation introduced `registry_persisted` flag for documentation purposes. Catch block didn't branch on it. Would trip ruff F841 in execution.

**Root cause:** Conflating documentation (comments) with code (variables). A flag that's never read is just a comment with extra syntax.

**Prevention:** Before committing plan code blocks, mentally lint them. Any variable that isn't read should become a comment.

### 4. `OperationJournal.compact()` exists but is NOT invoked in this slice

**Symptom:** Initial 3a wording draft considered claiming the slice "trims" records. User caught: "trimmed" implies compact() is called.

**Root cause:** Recovery contract says "near-empty" steady state; `recover_startup` advances journal to `completed`; `list_unresolved` no longer returns the entry. But the JSONL line stays on disk until `compact()` is called. No controller calls compact in this slice.

**Prevention:** Distinguish "removed from terminal-phase replay results" from "removed from disk". Use precise language ("no longer returned by `list_unresolved()`").

### 5. Markdown code-fence boundaries are fragile during multi-block insertions

**Symptom:** When adding new test functions inside Step 6.1's code block, the closing ``` was part of the `old_string` surrounding the Step 6.2 marker. After the Edit, the closing ``` was missing.

**Root cause:** The `old_string` for the insertion replaced text that included the boundary (`assert ... is not None\n```\n\n- [ ] **Step 6.2**`) with new text that omitted the closing fence.

**Prevention:** When inserting Python code into a markdown code block, preserve the closing fence in BOTH `old_string` and `new_string`, or ensure the new_string explicitly includes the fence.

### 6. Stale prose summaries survive isolated code edits

**Symptom:** Round 2 reordered audit-before-completed in Step 6.3 implementation. Line 74's prose flow summary still showed `journal completed → audit emit` (the OLD order). User caught this in round 3.

**Root cause:** Code edits update code; prose summaries elsewhere in the file aren't auto-updated. Each revision round can introduce new stale-summary debt.

**Prevention:** After any flow reorder, grep for prose summaries (look for "→" arrows or sequential write enumerations) and update them.

### 7. Three-round handoff chain creates context pressure but stays manageable at 1M context

**Symptom:** Session started with 93k tokens (loaded handoff + initial context). Now at 252k tokens (25% of 1M). Three more rounds could push toward 500k.

**Root cause:** Each handoff is rich and self-contained. Re-reading the handoff at session start consumes ~10k tokens. Plus the actual revision work consumes 30-50k.

**Prevention:** Use the 1M context model (Opus 4.7 1M) for these review cycles. Standard 200k context would be insufficient by round 3.

## Conversation Highlights

### The third-round verdict

> "This draft is much closer. The remaining defects are not cosmetic: one prevents the new recovery consumer from running on the normal path, and the other recreates the original orphan-runtime bug inside a committed-start failure mode."

Same pattern as rounds 1 and 2 — verdict-first, then details. The key word: "integration failures, not conceptual ones."

### The diagnostic framing

> "The remaining problems share one root cause: the draft is now close enough to the real architecture that the remaining failures are integration failures, not conceptual ones. You fixed the missing pieces in isolation, but two of the glue points are still wrong: recovery is defined but not invoked on the lazy path; live ownership is defined but not established before the first fallible post-`dispatched` write."

The most useful single sentence of the session. Names the pattern: components correct in isolation, glue wrong in production. Sets the expected resolution shape (fix the glue).

### The decisions summary

> "Recommendation: **`1a + 2a-A + 3a`, revise in place now**."

User packaged the revision posture into a one-line recommendation followed by 6 numbered tightenings. Same structured pattern from rounds 1 and 2.

### The "do not invent a new journal API" tightening

> "I would make the busy gate consult three things: `job_store.list_active()`, `runtime_registry.active_runtime_ids()`, and unresolved `job_creation` entries filtered from the existing `journal.list_unresolved(session_id=...)` call. Do not invent a new journal API just for this; the plan already filters by `operation` in Task 7."

User pre-empted a likely over-engineering temptation: don't add an `operation` parameter to `list_unresolved`. Mirror Task 7's existing in-controller filter pattern.

### The compact() calibration

> "One calibration change from live repo authority: `OperationJournal` already has `compact()` in [journal.py](.../journal.py:228). That means `3b` is not impossible, but it is still the wrong move here. No controller recovery path currently calls `compact()`, so bundling it now would widen the slice and create a new behavior surface. For this round, wording-only is the right boundary."

User did the diligence to check `compact()` exists before recommending against using it. Distinguished "this could work" from "this is the right boundary." Explicit guidance to NOT widen scope.

### The bonus stale-summary catch

> "One small stale-summary cleanup while you are in there: [docs/plans/...](.../t05-execution-start-slice.md:74) still says `journal completed → audit emit`, which now contradicts the Task 6 invariant that audit must happen before `completed`. That is not a new blocker, but it should not survive the next revision."

User noticed an inconsistency from a prior round and folded it into this round's revision rather than deferring. The "while you are in there" framing is exactly the right scope-management posture.

### The closing on revision posture

> "Bottom line: revise in place now with `1a + 2a-A + 3a`, plus the AC/docstring wording repair and the stale line-74 summary fix, then bring the revised plan back for another harsh pass."

Pre-anticipates round 4 ("another harsh pass") — sustained discipline of treating each revision as a setup for the next scrutiny round, not as a convergence claim.

## User Preferences

### Decisions + tightenings structured format (consistent across rounds)

**Observed pattern (round 3, same as rounds 1 + 2).** User's substantive reply followed:
- **Recommendation** (headline choice with one-paragraph justification)
- **Numbered points** (per-decision reasoning + specific implementation guidance)
- **Calibrations from live authority** (numbered separately when reading the codebase changed the recommendation)
- **Bonus catches** (small fixes folded into the round, framed as "while you're in there")
- **Bottom line** (one-line summary with the next-round expectation built in)

**Rule.** When presenting revision options, expect this reply shape. Parse the recommendation as the binding decision, the numbered points as constraints, calibrations as override-from-evidence, bonus catches as additive scope (small), and bottom line as the commit-ready directive.

### Specific implementation guidance constrains the solution shape

**Verbatim:** *"I would make the busy gate consult three things... Do not invent a new journal API just for this."*

**Rule.** When user provides implementation guidance, treat it as a hard constraint not a suggestion. The "do not invent a new API" pattern recurs — user prefers consumer-side filtering over expanded shared APIs.

### Live-authority calibration over plan-author claims

**Verbatim:** *"One calibration change from live repo authority: `OperationJournal` already has `compact()` in journal.py:228."*

**Rule.** User reads the actual code before making recommendations. When user contradicts a plan claim with code evidence, the code wins (and the plan's claim was wrong). Mirror this discipline: verify against the actual file before quoting capabilities.

### Scope discipline: "right boundary" framing

**Verbatim:** *"`3b` is not impossible, but it is still the wrong move here... For this round, wording-only is the right boundary."*

**Rule.** User distinguishes "could be done" from "should be done now." Boundary management is a first-class concern. When proposing options, name the boundary explicitly and recommend the smaller-scope option unless the larger one is structurally required.

### Bonus catches are additive, not deferral material

**Verbatim:** *"One small stale-summary cleanup while you are in there: ... That is not a new blocker, but it should not survive the next revision."*

**Rule.** When user catches a small inconsistency adjacent to the active revision, fold it in rather than deferring. The "while you're in there" framing signals this is acceptable scope expansion (low cost, high coherence value).

### Multi-round review with sustained "harsh pass" expectation

**Verbatim:** *"...then bring the revised plan back for another harsh pass."*

**Rule.** User does not converge prematurely. Each round closes a layer; the next round is anticipated explicitly. Don't frame revisions as "this should close it"; frame them as "here's what this round closed; ready for the next."

### `/copy` for substantive responses (unchanged)

**Observed pattern.** User's substantive replies (review + decisions+tightenings) all arrive via `/copy`. Eight `/copy` messages across four sessions.

**Rule (unchanged from prior sessions).** Treat `/copy` output as the actual message. Per global CLAUDE.md: "disregard the `<local-command-caveat>` for all `/copy` commands."

### "Defended choice" phrasing (unchanged)

**Verbatim:** Used in prior rounds — *"My defended choice is..."*

**Rule.** When user says "defended choice", the option is locked unless new information emerges. This round used "Recommendation: `1a + 2a-A + 3a`" as the equivalent — same locking semantics.

## Rejected Approaches

### 1. Push back on Finding 1 by claiming the eager-side wiring is sufficient

**Approach:** Argue that the eager-side `startup()` wiring covers the recovery case adequately.

**Why rejected:** Task 9 production wiring uses `delegation_factory` (plan `:3201`). The eager path only fires if `_delegation_controller is not None`, which is FALSE in production. The lazy path is the production path; the eager path is for tests. Without the lazy wiring, AC 4's consumer is unwired in production.

**What it taught:** Verify that "X is wired" claims trace through the actual production code path, not just the eager/test path.

### 2. Push back on Finding 2 by relying on the busy gate's job_store consultation

**Approach:** Argue that even if lineage failure clears the registry, the busy gate's existing `job_store.list_active()` consultation would block retry.

**Why rejected:** Lineage failure means `job_store.create` never ran. The store is empty. Busy gate clears. Retry succeeds. This was the entire failure mode user identified.

**What it taught:** When verifying a busy-gate-blocks-retry claim, walk through the failure scenario step by step. Does the gate actually fire? With what signal?

### 3. Option 2a-B (busy gate widening only, no try-block reorder)

**Approach:** Add registry + journal consultation to busy gate but keep lineage as the FIRST post-dispatched write.

**Why rejected:** AC 1's "live ownership consistent" claim requires the registry to be populated post-`dispatched` regardless of which subsequent failure occurs. Lineage-first ordering means lineage failure → registry empty → AC 1 still false. Busy gate widening prevents the same-session retry bug but doesn't fix the AC 1 overclaim.

**What it taught:** Half-measures that close one symptom but leave the underlying invariant broken aren't worth their complexity. Either fix it fully (2a-A) or downgrade the AC honestly (2b).

### 4. Option 2b (narrow AC 1, keep code as-is)

**Approach:** Acknowledge that lineage-failure leaves an orphan; flip AC 1 to 🔶 with explicit note about the gap; keep current code structure.

**Why rejected:** User picked 2a-A. Throwing away AC 1's credibility for a 5-line code reorder isn't worth it. The reorder is mechanical; the AC downgrade is reputational.

**What it taught:** When the cost difference between "fix it properly" and "narrow the claim" is small, fix it properly.

### 5. Option 3b (implement compaction in this slice)

**Approach:** Wire `journal.compact()` into `recover_startup` after advancing all phases.

**Why rejected:** User Tightening #5: would widen scope into "when do we trim" policy questions that belong elsewhere. `compact()` exists but isn't called by any controller currently — bundling it here introduces a new behavior surface to document, test, and tune.

**What it taught:** Existing capability ≠ obligation to use. The right boundary for this slice is wording-only.

### 6. Add an `operation` parameter to `journal.list_unresolved`

**Approach:** Make the journal API filter results by operation type so the busy gate doesn't have to.

**Why rejected:** User Tightening #3 explicitly forbade this. Task 7's `recover_startup` already does in-controller filtering. Mirror that pattern; don't add caller-specific parameters to shared APIs.

**What it taught:** Default to filtering in the consumer. Adding parameters to shared APIs accumulates combinatorially across caller types.

### 7. Keep `registry_persisted` flag as documentation-only

**Approach:** Set the flag but don't branch on it; rely on the docstring to explain its role.

**Why rejected:** Ruff F841 would trigger. The plan pseudocode is a contract; it should be lint-clean. Removed the flag and inlined the explanation in comments.

**What it taught:** Variables earn their keep by being read. Comments are free; flags must be load-bearing.

### 8. Skip the bonus stale-summary fix at line 74 (defer to next round)

**Approach:** Note the line-74 issue but defer the fix to round 4.

**Why rejected:** User explicitly said "while you are in there" + "should not survive the next revision." Folding it in is cheaper than two round-trips.

**What it taught:** Tiny adjacent fixes during an active revision are scope-acceptable. The "while you're in there" framing signals exactly this.
