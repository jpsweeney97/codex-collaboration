---
date: 2026-04-17
time: "19:23"
created_at: "2026-04-17T19:23:04Z"
session_id: 4d9c9536-b73f-4fef-a2e0-bbc772cf273c
resumed_from: "docs/handoffs/archive/2026-04-17_19-30_t05-plan-revised-after-three-p1-findings.md"
project: claude-code-tool-dev
branch: docs/t05-execution-start-plan
commit: bd850302
title: "T-05 plan second-round revision — recovery consumer + committed-start failure semantics added"
type: handoff
files:
  - docs/plans/2026-04-17-t05-execution-start-slice.md
---

# T-05 Execution-Start Plan — Second-round revision after two new P1 findings

## Goal

Turn the 19:30 handoff's awaiting-review state into the next scrutiny → revision round. User returned two new P1 findings on the revised plan (replay-safe claim lacks a recovery path; no committed-start failure semantics after `dispatched`) + three high-risk assumptions + edge-case analysis with the verdict "Major revision." All findings needed to be verified against authoritative sources (not taken on faith), revision shape negotiated with specific alternatives, then executed in-place per user's established working pattern.

**Bigger picture.** T-05 is the execution-domain foundation for codex-collaboration. The prior round closed three P1 findings (handle persistence, runtime orphaned, journal-before-dispatch). This round closes two more P1 findings (replay-safe over-claim, committed-start failure semantics) that were one abstraction layer deeper — not about what data is written but about what CONSUMES that data and what happens when the writes themselves fail. The plan-as-contract discipline is paying off: each review round closes a class of defects that would have produced a real bug at execution time.

**Trigger.** User replied to the prior session's "awaiting review" posture via `/copy` with a structured scrutiny message. Two P1 findings cited specific line numbers in the revised plan + `dialogue.py` + `recovery-and-journal.md`. Verdict: "Major revision." User also gave three high-risk assumptions and a bulleted list of required changes.

**Success criteria for this session:**

1. ✅ Each cited finding verified literally against the authoritative source before responding (zero performative agreement).
2. ✅ Both P1 findings confirmed as structurally correct (not pushed back).
3. ✅ User's tightening about replay-safe phrasing ("reconciled into durable state", not "rebuilds the live view") incorporated.
4. ✅ User's insistence that dialogue.reply — not dialogue.start — is the right precedent for delegation's post-dispatched flow respected.
5. ✅ User's 4-test minimum set (lineage / job / journal-completed / audit) adopted.
6. ✅ Task placement per user directive: Task 6 absorbs 2a; new standalone Task 7 for recovery; renumber 7-10 → 8-11.
7. ✅ Plan revised in place (not v2); publication posture unchanged (local merge-and-push).
8. ✅ All coherence checks pass: 11 tasks sequential, 0 "rebuilds the live view" residue, 0 accidental-liveness phrases, test counts chain cleanly.

All eight met. Plan at `docs/plans/2026-04-17-t05-execution-start-slice.md` still untracked; HEAD unchanged at `bd850302`; branch still `docs/t05-execution-start-plan`.

## Session Narrative

**Phase 1 — Load handoff, prepare for review (~1 min).** `/load` resolved the 19:30 handoff cleanly; the state file was written at `docs/handoffs/.session-state/handoff-4d9c9536-b73f-4fef-a2e0-bbc772cf273c`. Positioning set correctly: wait for feedback, do not pre-emptively edit. This was load-bearing — if I had started re-reading the plan looking for things to improve, I would have wasted context before the actual scrutiny arrived.

**Phase 2 — Receive second-round scrutiny (~immediate).** User posted a `/copy` structured review. Two P1 findings with explicit `start`/`end` line ranges, three high-risk assumptions, four real-world breakpoint scenarios, hidden-dependencies analysis, adversarial-perspective notes, root-cause framing ("the revision imported the right write-ordering primitives from dialogue, but not the companion semantics that make those primitives trustworthy under failure"), required-changes list, and verdict "Major revision."

Finding 1 citations: plan `:9` (replay-safe claim), plan `:56` (AC 4 evidence), plan `:2358` (`_ensure_delegation_controller`), `dialogue.py:522` (`recover_startup`), `recovery-and-journal.md:35` (journal-before-dispatch), `recovery-and-journal.md:59` (trimming).

Finding 2 citations: plan `:2070` (journal dispatched), plan `:2096` (lineage), plan `:2108` (job), plan `:2113` (registry), plan `:2121` (journal completed), plan `:2136` (audit), plan `:1822` (bootstrap failure test — the one that only covers pre-dispatched failure), `dialogue.py:361` (reply failure semantics docstring), `test_dialogue.py:333` (audit-failure-after-dispatched test).

**Phase 3 — Apply `superpowers:receiving-code-review` skill (~30s).** Invoked the skill before responding. Key rule engaged: "Verify. Question. Then implement." Forbidden: "You're absolutely right!" / "Great point!" / implementing before verification.

**Phase 4 — Verify each finding literally (~5 min, parallel reads).** Batched reads of: plan lines 1-80 (goal + AC table + scope), 2060-2180 (post-dispatched flow), 2340-2400 (`_ensure_delegation_controller`), 1800-1860 (bootstrap failure test); `dialogue.py:340-420, 500-580, 150-240`; `test_dialogue.py:320-380`; `recovery-and-journal.md:30-80`. Also grep for `CommittedTurnFinalizationError` and `recover_startup` to confirm they exist in dialogue.

Critical cross-check: read `dialogue.py::DialogueController.start` (lines 150-225) and confirmed it does NOT have committed-turn-finalization semantics. Dialogue has TWO shapes — `start` (no try/except around lineage) and `reply` (full `CommittedTurnFinalizationError` taxonomy with 3 tests). User's Finding 2 cites `dialogue.py:361` which is `reply`, not `start`. The asymmetry mattered to my response: I needed to name that dialogue itself has two patterns, then defend why delegation's `start` should follow dialogue's `reply` shape (5 local writes vs 1) rather than dialogue's `start` shape.

All cited line numbers held exactly as user claimed. Zero defensive pushback available.

**Phase 5 — Analyze AC consequences (~2 min).** Both findings had AC cascading effects:
- Finding 1: AC 4's ✅ with evidence "replay-safe via idempotency key" is a producer-only claim. No consumer → cannot be called replay-safe.
- Finding 2: AC 1's "can start" implies controllable-and-recoverable. A raw exception mid-finalization leaves the runtime live but the handle/job ambiguous. AC 1 might drop unless finalization failure has explicit semantics.

Decision: AC 4 definitely flips to 🔶 unless consumer is in-scope; AC 1 can stay ✅ if Finding 2 is resolved with explicit handle/job marking.

**Phase 6 — Respond with verification + AC consequences + revision-shape options (~3 min).** Structured per last-session pattern:
1. Insight block (3 educational points — dialogue.reply is the right precedent, not dialogue.start; replay-safe vs durable; trimming gap compounds with missing consumer)
2. Literal citation confirmation for each finding
3. AC consequence table
4. Revision shape with explicit options: 1a (add consumer) / 1b (narrow claims) / 1c (half-measure) for Finding 1; 2a (full mirror) / 2b (minimal) for Finding 2; trimming policy choice
5. Process questions (revise in-place now vs v2 vs defer; scope choice)
6. Explicit hold-until-decision-given statement

Key move: presenting options with my recommendation named (1a + 2a for full structural credibility) but not picking unilaterally. Matched user's "present options, don't silently choose" preference from prior session.

**Phase 7 — User response: clear decisions + five tightenings (~2 min).** User replied via `/copy`:

Decisions:
1. Finding 1: `1a` (add minimal delegation startup-recovery path).
2. Finding 2: `2a` (full mirror of dialogue.reply finalization semantics) but "not as a blind copy."
3. Process: revise in place, now.
4. Placement: Task 6 absorbs 2a; **new standalone Task 7** for recovery (NOT folded into Task 8 MCP); renumber.

Tightenings:
1. **Don't keep "rebuilds the live view" phrasing.** User: *"Across restart, you are not rebuilding live runtime ownership; the registry is gone. What 1a should say is: unresolved job_creation records are **reconciled into durable state** on startup, typically `no-op` for intent-only and `unknown` for dispatched-but-unfinished starts, and then trimmed."*
2. **Adapt dialogue.reply, don't blind-copy.** User: *"The correct rule is: once job_creation is at dispatched, the plan must define a committed-start failure mode and tell the caller not to blindly retry."*
3. **Post-dispatched policy precision:** User: *"After dispatched, leave the journal at dispatched; best-effort mark any persisted handle/job unknown; preserve enough state for startup reconciliation; raise CommittedStartFinalizationError with explicit no-retry guidance."*
4. **Add a fourth failure test:** *"I would include **journal-completed write failure** as well. That write is the boundary between 'still unresolved' and 'operation confirmed,' so it is not optional coverage. My minimum set would be: lineage_store.create failure, job_store.create failure, journal.write_phase(completed) failure, append_audit_event failure."*
5. **AC outcome:** With 1a + 2a, AC 1 ✅ and AC 4 ✅ both stay.

User closing: *"Revise in place, now. This is not random scope growth. These are the two remaining structural holes in the same trust-boundary slice. A handoff would just defer the same reasoning while the context is already hot."*

**Phase 8 — Plan the edit sequence + create TaskCreate todos (~2 min).** Given the complexity (new Task 7 insertion + renumbering 4 tasks + test count updates across 4 tasks + Risks table + framing edits), used TaskCreate to track 10 todos. Key structural decision made at planning time: put Task 7's recovery implementation into its own commit (not fold into Task 6 which already absorbs 2a), because reconciliation (cross-process-boundary concern) is a distinct trust boundary from committed-start failure (local-write-order concern). Matches the "one concept per commit" discipline user values.

**Phase 9 — Grounding reads (~1 min).** Re-read current Task 6 body, Task 7-10 step layouts, Risks table, Decomposition Philosophy. Noted the existing test count chain baseline 593 → 624 → 632 (before Task 6 modification). Noted step labels in old Task 7 (MCP) collide with new Task 7 (recovery) on 7.1-7.5 — renumbering needs disambiguation.

**Phase 10 — Execute revision in order (~30 min, 15+ Edit calls + 1 Bash/sed).**

Task 1 (line 9 + AC 4): rewrote persistence-layering paragraph to explicitly reference Task 7's recovery consumer with user's phrasing ("reconciled into durable state"); rewrote AC 4 evidence to split into "three durable producers + one durable consumer."

Task 2 (Scope + File Structure + Decomposition): added in-scope items #12 (committed-start failure semantics) and #13 (startup reconciliation); updated delegation_controller.py description to mention both additions; updated mcp_server.py description to include recover_startup wiring; rewrote Decomposition Philosophy with 11-task inventory and correct surface-reachable-after-Task-9 note.

Task 3 (Task 6 flow paragraph + 4 failure tests): added "Committed-start failure semantics" paragraph to Task 6 goal. Wrote 4 new failure tests with a shared `_assert_dispatched_but_not_completed` helper. **Initial audit test had an embedded policy debate** about whether audit-after-completed leaves journal at completed-but-stores-unknown (asymmetric). Realized mid-write that the cleaner design is to REORDER the flow to put audit BEFORE journal.write_phase(completed) — then "journal at dispatched" becomes the universal terminal state for all 4 failures. Rewrote the test accordingly.

Task 4 (Task 6 exception class + docstring + try/except wrap): added `CommittedStartFinalizationError(RuntimeError)` class mirroring dialogue's with a detailed docstring explaining: (a) what it means (post-dispatched finalization failure), (b) the no-retry guarantee rationale (idempotency replay only recognizes `completed` phase), (c) the recovery path (Task 7's `recover_startup` will mark unknown on next session). Updated `start()` docstring with "Write ordering invariant" + "Failure semantics" sections adapted from `dialogue.py:361-373`. Rewrote post-dispatched block with try/except wrap + reordered flow (lineage → job → registry → audit → completed) + best-effort `update_status("unknown")` on persisted stores.

**Grounding discovery mid-edit:** I initially wrote `self._lineage_store.mark_unknown(collaboration_id)` assuming dialogue used that method name. Ran grep: `lineage_store.py:159` has `def update_status(self, collaboration_id, status: HandleStatus)` — NOT `mark_unknown`. Dialogue's finalization uses `update_status(cid, "unknown")`. Also verified `HandleStatus` includes "unknown" (`models.py:15`) and `JobStatus` includes "unknown" (plan line 378-379). Fixed the method call and removed the "if either method is not yet present" caveat in favor of a grounded "both methods already exist" note.

Task 5 (test count + commit message): updated Step 6.4 expected from "624 + 8 = 632" to "624 + 12 = 636" (4 new failure tests); updated commit message to include "+ committed-start failure semantics".

Task 6 (insert new Task 7 body): constructed the full Task 7 body (~370 lines) with:
- Goal naming the producer/consumer gap AC 4 depends on
- **Reconciliation contract table** with 5 rows (intent-only, dispatched+no-state, dispatched+handle, dispatched+handle+job, dispatched+already-unknown) showing durable-store action + journal advance per journal phase
- Explicit "NOT in scope" note about runtime reattachment (with architectural reason: delegation runtimes are subprocess-anchored; dialogue's thread_id is App-Server-persistent and can rejoin)
- 5 new tests including fresh-session no-op, intent-only, dispatched+handle+job, dispatched+no-state, idempotent second call
- `recover_startup()` implementation mirror of `dialogue.py:522` but reconcile-only (no reattach) with `_phase_rank` helper for picking latest phase per idempotency key
- mcp_server.py wiring instructions referencing existing dialogue wiring at `:129, :147`
- New test for the mcp wiring (verifies both recover_startup calls fire on session init)
- Commit message and expected count (636 + 6 = 642)

The insertion was done as a single Edit that replaced `## Task 7: MCP Tool Registration` with the entire new Task 7 body followed by `## Task 8: MCP Tool Registration`, so the old Task 7 header got renamed AND the new content inserted in one atomic edit.

Task 7 (renumber Tasks 8-10 headers + step labels): three sequential Edits to rename `## Task 8` → `## Task 9`, `## Task 9` → `## Task 10`, `## Task 10` → `## Task 11`. Step-label renumbering was done via a single Bash/sed block (reverse order to avoid collision): 10.x → 11.x first (unique), then 9.x → 10.x, then 8.x → 9.x, then 7.x → 8.x scoped to lines after `## Task 8: MCP Tool Registration` header (so new Task 7's 7.x labels stay intact). One cross-reference fixed in the same sed block: "E2E integration test is added in Task 9" → "Task 10".

**Sed invalidated the Edit tool's cache.** My next four Edit calls failed with "File has been modified since read". Ran targeted Reads to refresh cache, then retried the Edits.

Task 8 (test counts across renumbered tasks): updated 4 running-total references:
- Task 8 (MCP): 632+5=637 → **642+5=647**
- Task 9 (Production): 637+2=639 → **647+2=649**
- Task 10 (Integration): 639+1=640 → **649+1=650**
- Task 11 (Verify): "~640 passed ... ~47 added across tasks 1-9" → **"~650 passed ... 57 added across tasks 1-10: 11+8+3+3+6+12+6+5+2+1"**

Task 9 (Risks table): rewrote the first row (registry in-process live-ownership) to reference Task 7's reconciliation consumer and defer restart/discard to poll/promote. Added 3 new rows: (a) startup reconciliation marks unknown but doesn't drive promote/discard; (b) committed-start failure asymmetric partial state; (c) unresolved journal records survive between sessions by contract.

Task 10 (coherence verification): ran a comprehensive Bash grep check. Hits:
- 11 Task headers sequential ✓
- 0 "rebuilds the live view" ✓
- 16 `CommittedStartFinalizationError` occurrences ✓
- 39 `recover_startup` occurrences ✓
- Step count 58 (56 task steps + 2 Pre-Flight) ✓
- Commit messages: 11 (9 feat + 1 test + 1 conditional style) ✓
- 1 "alive by accident" hit at line 55 — rephrased to "controllable via `registry.lookup(runtime_id)` for future turn dispatch and teardown" to remove the pattern-match false positive

**Phase 11 — Present revision summary to user (~2 min).** Summary covered: structural deltas, task-by-task changes, AC table changes, Risks additions, what was NOT changed (Tasks 1-5, publication posture, test-count tolerance, file-structure layer split), coherence checks. Explicit "awaiting third-round review" close.

**Phase 12 — User invoked `/save` (immediate).** Writing this handoff now.

## Decisions

### Decision 1: Accept both P1 findings without pushback

**Choice:** Both P1 findings — replay-safe claim lacks recovery path (Finding 1) and no committed-start failure semantics after `dispatched` (Finding 2) — were verified as structurally correct and accepted as binding revisions.

**Driver.** Each finding cited specific lines in authoritative docs. Literal verification confirmed all user claims:

- Plan `:9` said *"recovery rebuilds the live view by replaying the three durable stores"* — but plan `:2358` (`_ensure_delegation_controller`) only lazy-pinned the controller with no reconciliation hook. Producer without consumer.
- Plan `:56` (AC 4) said "replay-safe via idempotency key" — same producer-only issue.
- `dialogue.py:522` `recover_startup` exists as a coordinated startup-recovery method; wired at `mcp_server.py:129, :147`. Delegation has no equivalent.
- Plan `:2070-2146` had 5 unguarded local writes after `dispatched` (lineage → job → registry → completed → audit). Plan `:1822` tests only the pre-dispatched failure case. No post-dispatched coverage.
- `dialogue.py:361-373` (reply docstring) defined full committed-turn finalization taxonomy with `CommittedTurnFinalizationError` raised at `:449, :460, :492` and tested at `test_dialogue.py:321, :333, :358`. Delegation has nothing analogous.

**Alternatives considered:**
- **Push back on Finding 2 using dialogue.start as precedent:** dialogue's `start` method (lines 150-225) also has unguarded local writes after dispatch and raises raw exceptions — so arguably delegation's start could follow that pattern. Rejected because dialogue's start has ONE local write (lineage); delegation's has FIVE. The blast-radius asymmetry makes the reply-shape the right precedent. User's choice of citing `dialogue.py:361` (reply) rather than `dialogue.py:150` (start) was deliberate.
- **Narrow AC 4 without adding consumer (Option 1b):** honest and smaller-scope, but throws away the load-bearing value of the journal extension. Viable but the user's `1a` choice was stronger.

**Implications.** Plan grew by ~660 lines. One new task (recovery) added. One task (Task 6) significantly expanded (4 new tests + exception class + try/except wrap + docstring). Test count estimate: 640 → 650. AC 4 now has evidence for both producer and consumer halves; a third-round review can't reopen the replay-safe question.

**Trade-offs accepted.** Revision effort was real (~30 min of Edit calls). Cheaper than merging a plan where "replay-safe" was an overclaim — poll/promote slices would have hit the consumer gap immediately.

**Confidence:** High (E2) — authority text verified against both `dialogue.py` and `recovery-and-journal.md`; store method signatures (`update_status`) verified via grep before including in controller code.

**Reversibility:** High at plan level (still text-editable); low at execution level (executing the original plan would have produced a replay-safe over-claim noticed on first crash recovery attempt).

**Change trigger:** None — findings grounded in normative docs that won't change.

### Decision 2: Reorder post-dispatched flow to put audit BEFORE journal-completed

**Choice:** Changed the post-dispatched write sequence from `lineage → job → registry → completed → audit` to `lineage → job → registry → audit → completed`. The `journal.write_phase(completed)` is now the LAST write.

**Driver.** Mid-writing the 4 failure tests, I noticed the original order made the audit-failure case asymmetric: if audit fails after `completed` is already written, the journal says "I'm done" but the handle/job are marked `unknown`. The terminal signal is inconsistent between journal phase and store statuses. With the reorder, "journal at dispatched" becomes the UNIVERSAL terminal state for all 4 failures — reconciliation just reads `list_unresolved()` and proceeds.

**Alternatives considered:**
- **Keep original order, accept asymmetry:** reconciliation would need to consult BOTH journal phase AND handle/job status as unreconciled signals. More complex consumer. Rejected because complexity compounds with the producer gap we just closed.
- **Rewind journal phase (write "dispatched" again after a "completed" failure):** journal is append-only by contract; not possible.

**Implications.** Reconciliation (`recover_startup`) only needs to check `journal.list_unresolved(session_id)` — one source of truth. Simpler and more robust. Also means audit is no longer a "ship it anyway" afterthought — audit is part of the commitment chain.

**Trade-offs accepted.** Audit now happens before the journal is marked terminal, which means a successful delegation might have an audit entry but no `completed` journal phase if the final write fails. That's fine — next-session reconciliation closes it.

**Confidence:** High (E1) — judgment call made mid-session, supported by the cleaner universal-terminal-state invariant.

**Reversibility:** High — the order is a single-block reorder in Task 6's Step 6.3 code.

**Change trigger:** If audit emission itself is deferred to a post-transaction step (e.g., async queue), the order may need to change.

### Decision 3: Task 7 is reconcile-only, not reattach

**Choice:** `recover_startup()` reconciles unresolved journal records (mark unknown + advance to completed) but does NOT attempt to reattach a live runtime across a restart boundary.

**Driver.** Unlike dialogue, which reuses persistent App-Server `codex_thread_id` across sessions (the thread is server-side, the session is rebuilt), delegation runtimes are subprocess-anchored to a local worktree. Across restart: subprocess is dead, the session is gone, the thread is gone. Nothing to rejoin.

This is not a v1 shortcut — it's a fundamental architecture property. If T-05 ever needed runtime-survivable recovery, the answer would be an external App Server or a supervisor process holding the subprocess lifecycle separately from the plugin process.

**Alternatives considered:**
- **Reattach on restart (restart from brief):** `recovery-and-journal.md:121` mentions this as a policy, but it's a higher-level decision (the controller would need to rehydrate from the durable stores + start a new runtime). Rejected for this slice — belongs to poll/promote slices where lifecycle state transitions live.

**Implications.** Task 7 is a pure closure task: marks unknown, advances journal, trims. Downstream slices (poll/promote) pick up `unknown` jobs and make user-facing decisions. Keeps Task 7 narrow and focused.

**Trade-offs accepted.** Users who crash mid-delegation will see `unknown` jobs on next start. No automatic restart. This is correct per `recovery-and-journal.md:57` — *"Restarting a delegation that was running when Claude crashed is more likely to surprise the user than to help."*

**Confidence:** High (E1) — user explicitly asked for reconciliation, not reattachment; architectural rationale verified.

**Reversibility:** High — reattachment can be added as a separate method on `DelegationController` later without touching `recover_startup`.

**Change trigger:** If future architecture makes delegation runtimes restart-survivable (external App Server, persistent subprocess supervisor).

### Decision 4: New standalone Task 7, not fold into Task 6 or Task 8

**Choice:** Reconciliation lands as its own task (new Task 7) with its own commit, not folded into Task 6 (which absorbs 2a) or Task 8 (MCP registration).

**Driver.** User directive: *"I would **not** fold 1a entirely into current Task 7 [MCP]. That mixes two different concepts: tool registration and recovery semantics."* And: *"Current Task 6 absorbs 2a: controller docstring, CommittedStartFinalizationError, post-dispatched failure tests. Add a new Task 7: delegation startup reconciliation for unresolved job_creation entries plus the MCP/server wiring that invokes it. Then renumber current 7-10 to 8-11. That keeps the 'one concept per commit' discipline intact."*

**Alternatives considered:**
- **Fold into Task 6:** user rejected — mixes committed-start failure (local-write-order concern) with startup reconciliation (cross-process-boundary concern).
- **Fold into Task 8 MCP:** user rejected — mixes tool registration with recovery.

**Implications.** 11 tasks total (up from 10). Each task has a single-concept commit. Reviewers of any single commit can evaluate it in isolation.

**Trade-offs accepted.** One more commit in the chain; slightly more renumbering effort. Mitigated by the sed pass being mostly mechanical.

**Confidence:** High (E1) — direct user directive.

**Reversibility:** Medium — reorganizing commits later would require rebase.

**Change trigger:** N/A — directive is clear.

### Decision 5: Use phrase "reconciled into durable state" instead of "rebuilds the live view"

**Choice:** Every mention of cross-restart recovery uses user's precise phrasing.

**Driver.** User Tightening #1 verbatim: *"Do not keep the current 'recovery rebuilds the live view' phrasing even after adding a consumer. Across restart, you are not rebuilding live runtime ownership; the registry is gone. What 1a should say is: unresolved job_creation records are reconciled into durable state on startup, typically no-op for intent-only and unknown for dispatched-but-unfinished starts, and then trimmed."*

**Alternatives considered:**
- **Keep "rebuilds the live view" softened:** rejected — the phrase implies runtime reattachment, which is explicitly out of scope. Any softening would still pattern-match as overclaim.

**Implications.** Grep-verified: 0 occurrences of "rebuilds the live view" in the revised plan. The new phrasing appears in the persistence-layering paragraph (line 9), AC 4 evidence (line 58), Scope in-scope #13, File Structure descriptions, Task 7 goal, Risks table.

**Trade-offs accepted.** Slight prose repetition across 6+ locations. Mitigated by each location using context-appropriate phrasing (module docstring, AC evidence, risks row, etc.).

**Confidence:** High (E1) — direct user directive.

**Reversibility:** High — text-editable.

**Change trigger:** N/A.

### Decision 6: Four failure tests (not three) — include journal-completed write failure

**Choice:** The 4-test minimum set is lineage / job / journal-completed / audit. Originally proposed only 3 (lineage / job / audit).

**Driver.** User Tightening #4 verbatim: *"Your three suggested tests are good, but I would include **journal-completed write failure** as well. That write is the boundary between 'still unresolved' and 'operation confirmed,' so it is not optional coverage."*

**Alternatives considered:** 3 tests (lineage / job / audit) — rejected because journal-completed failure is precisely what determines whether an operation is "still unresolved" (reconcilable) or "confirmed" (no-op on reconciliation). Skipping coverage of that boundary would leave reconciliation behavior unverified for the most-important state transition.

**Implications.** Task 6 test count is now baseline + 12 (8 happy-path/busy/bootstrap + 4 failure) = 12 new tests. Test file grows by ~250 lines for the 4 failure tests + `_assert_dispatched_but_not_completed` helper.

**Trade-offs accepted.** Slightly larger Task 6 commit. Mitigated by the tests sharing a helper that reduces repetition.

**Confidence:** High (E1) — direct user directive.

**Reversibility:** High — tests are independent and can be added/removed.

**Change trigger:** If the journal write_phase interface changes such that completed-write failure becomes impossible (unlikely — it's a file append).

### Decision 7: Mirror dialogue.reply's failure taxonomy adaptively, not blindly

**Choice:** `CommittedStartFinalizationError` mirrors `CommittedTurnFinalizationError` structurally (no-retry guidance in message, raised from the catch block, leaves journal at dispatched) but is named and phrased for delegation's specific context.

**Driver.** User Tightening #2 verbatim: *"Finding 2 should be fixed with 2a, but not as a blind copy of dialogue reply. Your own insight is right: structurally, delegation start now looks like reply, not start. But the exact policy should be adapted to the delegation flow."*

**Alternatives considered:**
- **Reuse `CommittedTurnFinalizationError`:** rejected — the error would refer to "turns" which is wrong for delegation.
- **Generic `CommittedOperationFinalizationError`:** rejected — too abstract; dialogue's error is named for dialogue, so delegation's should be named for delegation.

**Implications.** Two similarly-shaped error classes in the codebase (`CommittedTurnFinalizationError` in dialogue.py, `CommittedStartFinalizationError` in delegation_controller.py). If a future abstraction emerges where both need to share a base class, that's a refactor the structure supports.

**Trade-offs accepted.** Some duplication in the docstring content. Mitigated by each class having context-specific guidance (turn vs start; blind retry semantics differ subtly).

**Confidence:** High (E1) — user directive with implementation judgment.

**Reversibility:** Medium — renaming either class after the fact is mechanical; merging them into a base class is a small refactor.

**Change trigger:** If a third committed-operation-finalization case emerges (e.g., codex.delegate.promote), a common base class would be worth extracting.

## Changes

### Files modified (this session)

| File | Change | Commit |
|---|---|---|
| `docs/plans/2026-04-17-t05-execution-start-slice.md` | Revised in place: 2948 → 3608 lines (+660). New Task 7 (Startup Reconciliation, ~370 lines). Renamed Tasks 7-10 → 8-11. Renumbered all step labels. Task 6 absorbs 2a: added committed-start failure paragraph + `CommittedStartFinalizationError` class + docstring rewrite + 4 failure tests + reordered post-dispatched flow. Line 9 + AC 4 rewritten for consumer-in-scope framing. Risks table: registry row reworded + 3 new rows. Test count estimates updated: 632→636→642→647→649→650. Rephrased "alive by accident" at line 55 to remove pattern-match false positive. | Uncommitted |

### Git state changes

| Commit | Branch | Subject |
|---|---|---|
| (none) | `docs/t05-execution-start-plan` | Branch unchanged; plan still untracked |

No commits. No push. Main unchanged at `bd850302`.

### Handoff / state files

- Archived (at session start): `2026-04-17_19-30_t05-plan-revised-after-three-p1-findings.md` → `docs/handoffs/archive/`
- State file: `docs/handoffs/.session-state/handoff-4d9c9536-b73f-4fef-a2e0-bbc772cf273c` — to be cleaned by this save
- New handoff (this file): `docs/handoffs/2026-04-17_19-23_t05-plan-second-round-recovery-consumer-added.md`

## Codebase Knowledge

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `docs/handoffs/2026-04-17_19-30_t05-plan-revised-after-three-p1-findings.md` | Prior handoff (resumed) | Full context: plan revised, awaiting second-round review; user's established decisions locked in; test count 640 estimated |
| `docs/plans/2026-04-17-t05-execution-start-slice.md` (multiple ranges) | Ground revision edits | Line 9 (persistence layering), line 56-61 (AC table), line 130 (Task 1 journal extension), line 1518 (Task 6 start), lines 2060-2180 (post-dispatched flow), lines 2340-2400 (`_ensure_delegation_controller`), lines 1800-1870 (bootstrap failure test) |
| `packages/plugins/codex-collaboration/server/dialogue.py` (lines 150-240, 340-420, 500-580) | Verify P1 findings; establish precedent | `start()` has 1 local write post-dispatch and NO finalization semantics (lines 150-225); `reply()` has many local writes post-dispatch AND full failure taxonomy (lines 340-509); `recover_startup()` exists at line 522 and is wired into mcp_server.py at `:129, :147` |
| `packages/plugins/codex-collaboration/server/journal.py` (lines 35, 49-112, 212) | Confirm journal API | `_VALID_OPERATIONS` frozenset at :35; `_journal_callback` per-phase validator at :49-112; `list_unresolved(session_id)` at :212 |
| `packages/plugins/codex-collaboration/server/lineage_store.py` (line 159) | Confirm store method signature | `def update_status(self, collaboration_id: str, status: HandleStatus) -> None` — NOT `mark_unknown` |
| `packages/plugins/codex-collaboration/server/models.py` (lines 15, 378-379) | Confirm status literals | `HandleStatus = Literal["active", "completed", "crashed", "unknown"]`; `JobStatus = Literal["queued", "running", "needs_escalation", "completed", "failed", "unknown"]` |
| `packages/plugins/codex-collaboration/tests/test_dialogue.py` (lines 320-380) | Verify failure-test pattern | 3 tests for post-dispatched finalization failure: parse at :321, audit at :333, outcome at :358. Each verifies handle quarantine + journal at dispatched |
| `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` (lines 30-80) | Verify contract | Line 35 journal-before-dispatch; line 47 job_creation idempotency key; line 59 trimming policy "near-empty during normal operation" |

### Architecture: post-dispatched flow (final shape in this revision)

| Step | Action | Failure consequence |
|---|---|---|
| 1 | `journal.write_phase("dispatched")` | Raw exception; journal has only `intent`; no side effects committed |
| 2 | `lineage_store.create(handle)` | `CommittedStartFinalizationError`; journal at dispatched; handle + job unpersisted |
| 3 | `job_store.create(job)` | Same; handle→unknown, job unpersisted |
| 4 | `runtime_registry.register(...)` | (in-memory; extremely unlikely to fail) |
| 5 | `journal.append_audit_event(...)` | Same; handle+job→unknown; journal still at dispatched |
| 6 | `journal.write_phase("completed")` | Same; handle+job→unknown; journal at dispatched; this is the TERMINAL write — completing it means the operation is confirmed |

### Architecture: recovery consumer (new in this revision)

| Journal state | Durable-store reconciliation | Journal advance |
|---|---|---|
| `intent` only | None | Write `completed` |
| `intent`+`dispatched`, no handle/job persisted | None | Write `completed` |
| `intent`+`dispatched`, handle persisted (active) | `lineage.update_status(cid, "unknown")` | Write `completed` |
| `intent`+`dispatched`, handle + job persisted | Both stores → `unknown` | Write `completed` |
| `intent`+`dispatched`, handle already `unknown` (same-session committed-start failure) | No change (already unknown) | Write `completed` |

### Surprising findings / gotchas

- **Dialogue has two committed-operation shapes, not one.** `dialogue.py::start` (lines 150-225) has no try/except around lineage write — same as delegation's pre-revision code. `dialogue.py::reply` (lines 340-509) has full `CommittedTurnFinalizationError` taxonomy. User's citation of `:361` (reply) rather than `:150` (start) was deliberate — the reply-shape is the right precedent because delegation's start has 5 local writes (not 1) and thus matches reply's blast radius.
- **`lineage_store.update_status` NOT `mark_unknown`.** Dialogue's committed-turn finalization path uses `self._lineage_store.update_status(cid, "unknown")` (confirmed via grep on `dialogue.py:449-492`). There is no `mark_unknown` convenience method. I initially wrote the wrong method name and corrected mid-edit.
- **`HandleStatus` has "unknown" as a valid value** (`models.py:15`). So `update_status(cid, "unknown")` is semantically valid — the status literal union includes it.
- **`JobStatus` has "unknown"** (plan line 378-379, as modified by Task 1 of this plan). Task 1 extends the `JobStatus` literal to include "unknown" so `DelegationJobStore.update_status(job_id, "unknown")` type-checks.
- **Sed invalidates the Edit tool's file-state cache.** After my Bash sed renumbering pass, the next 4 Edit calls failed with "File has been modified since read." Had to run targeted Reads to refresh cache. Lesson: after any external file modification (sed, another process), subsequent Edit calls require a Read refresh.
- **Step labels are NOT unique after renumbering.** New Task 7 (recovery) and old Task 7 (MCP, before renumbering) both have `- [ ] **Step 7.1: Write failing tests**` with identical titles. Disambiguation required either surrounding context in old_string OR line-range-scoped sed.
- **Audit BEFORE completed is the clean design.** Putting `journal.write_phase(completed)` last makes "journal at dispatched" the universal terminal signal for all 4 failure modes. This insight came mid-edit when I was writing the audit-failure test and realized it couldn't cleanly match the other 3.

### Key locations to remember

| Concept | Location |
|---|---|
| T-05 plan (revised second time) | `docs/plans/2026-04-17-t05-execution-start-slice.md` |
| Dialogue reply failure semantics (precedent for Task 6) | `packages/plugins/codex-collaboration/server/dialogue.py:361-373, :449-492` |
| Dialogue recover_startup (precedent for Task 7) | `packages/plugins/codex-collaboration/server/dialogue.py:522-602` |
| Dialogue recover_startup wiring | `packages/plugins/codex-collaboration/server/mcp_server.py:129, :147` |
| LineageStore.update_status | `packages/plugins/codex-collaboration/server/lineage_store.py:159` |
| HandleStatus literal | `packages/plugins/codex-collaboration/server/models.py:15` |
| Journal list_unresolved | `packages/plugins/codex-collaboration/server/journal.py:212` |
| Journal trimming policy | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md:59` |
| Dialogue reply failure tests (precedent for Task 6 tests) | `packages/plugins/codex-collaboration/tests/test_dialogue.py:321, :333, :358` |

## Context

### Mental model

**Framing:** This session was a **second-round scrutiny → revision round trip**, one layer deeper than the first round. The first round closed data-shape defects (handle missing, runtime orphaned, journal absent). The second round closed reader-and-failure defects (no consumer for the journal; no policy for write failures after the expensive dispatch).

- **Core insight:** *Producer-consumer symmetry is the load-bearing invariant for any "replay-safe" claim.* Writing records is the easy half. Defining what reads them, when, and with what authority is the hard half. "Replay-safe via idempotency key" without a consumer is like "encrypted at rest" without a decryption key.
- **Mental model:** *Trust boundaries as failure-mode layers.* Each boundary crossed needs its own failure-mode definition. Pre-dispatch failures (worktree / runtime) → raw exception, nothing committed. Post-dispatch local-write failures → committed-start finalization, partial state marked unknown. Cross-session restart failures → reconciliation on session init. Three trust boundaries, three failure policies, three places the plan had to be explicit.

Secondary insight: **dialogue has two committed-operation shapes (`start` and `reply`), and choosing the right precedent matters more than following "dialogue's pattern" as a monolith.** Dialogue's `start` has 1 local write post-dispatch and accepts raw exceptions. Dialogue's `reply` has many local writes and defines full finalization semantics. Delegation's `start` has 5 local writes — so the reply-shape is the match, not the start-shape. This was the weakest point in my initial response (the "one asymmetry worth naming and setting aside" paragraph), and the user's explicit citation of `:361` (reply) confirmed it was the right match.

### Project state at session close

**T-20260330-05 (execution-domain foundation):** OPEN, high priority. Plan revised twice now (19:30 + this session). Still uncommitted on `docs/t05-execution-start-plan`. Awaiting **third** scrutiny pass per user's pattern — will review the revised plan on the new boundary.

**T-20260330-06 / T-07:** OPEN, blocked by T-05.

**T-20260416-01 (codex.dialogue.reply extraction mismatch):** OPEN, medium priority. Independent parallel thread — unchanged this session.

### Environment snapshot at session close

- Branch: `docs/t05-execution-start-plan` (unchanged)
- HEAD: `bd850302` (unchanged)
- Working tree: **dirty** — `docs/plans/2026-04-17-t05-execution-start-slice.md` still untracked (now 3608 lines)
- Plugin suite: not run this session (no code changes)
- Memory: no new feedback files; MEMORY.md unchanged

### Why this work matters (bigger picture)

T-05 is the execution-domain foundation for codex-collaboration. A plan that records journal entries without defining who reads them would produce one of two bad outcomes at execution time: either recovery code is written ad-hoc per slice (fragmenting the recovery contract) or the journal grows unbounded because nobody trims it. A plan that has no committed-start failure semantics would produce a second bad outcome: user gets raw stack traces instead of actionable guidance on whether to retry.

Both defects would have been caught at review time during execution — but by then the cost is higher: partial implementation, test expectations wrong, commit history messy. The review cycle is still paying off. This round was ~45 min of work that prevents 2-4 hours of execution-time rework.

## Learnings

### Producer-consumer symmetry must be named in any "replay-safe" claim

**Mechanism.** The prior session's self-review checked AC wording at the text level (does the AC prose match the implementation?) and at the contract level (does the implementation satisfy the normative doc?). It did NOT check producer-consumer symmetry: does the writing side have a reader? This third layer is where "replay-safe" overclaims hide — the journal CAN be replayed, but nothing replays it.

**Evidence.** User's Finding 1 traced directly to producer-only evidence. The plan wrote `job_creation` records and called them replay-safe without defining any consumer. Once prompted, grep confirmed: `_ensure_delegation_controller` (plan `:2358`) has no recovery hook; the plan defines no method analogous to `dialogue.py:522 recover_startup`.

**Implication.** AC coverage self-reviews must add a fourth trace: (1) AC text, (2) normative doc, (3) producer implementation, (4) consumer implementation. All four must exist. A plan that satisfies 1-3 without 4 is a producer-only plan.

**Watch for.** Any AC that uses words like "replay-safe", "recoverable", "consistent across restart", "idempotent" — all of these imply a reader. If the plan names only writers, AC is overclaimed.

### Blast radius determines which precedent to mirror

**Mechanism.** Code patterns aren't atomic: dialogue has multiple post-dispatch failure shapes depending on how many local writes happen after the expensive side effect. `start` (1 write) accepts raw exceptions. `reply` (many writes) defines `CommittedTurnFinalizationError`. Choosing which to mirror depends on delegation's own write count.

**Evidence.** Dialogue `start` at lines 150-225 has `lineage_store.create(handle)` as its only post-dispatch local write, followed by `journal.write_phase(completed)`. No try/except. Dialogue `reply` at lines 340-509 has `parse_consult_response`, `lineage_store.update_status` for quarantine, audit emission, outcome persistence — and wraps them with explicit failure semantics. Delegation `start` has 5 writes (lineage, job, registry, audit, completed) — matches reply's blast radius.

**Implication.** When evaluating "follow pattern X from Y", check Y's internal variations first. A single file can contain multiple patterns for the same abstract operation; blast radius (count of local side effects) is often the discriminator.

**Watch for.** Any pattern-mirror recommendation in a plan that cites a file without citing specific line ranges. Vague "follows the dialogue pattern" is insufficient — specify which shape.

### Write ordering is a design lever, not an implementation detail

**Mechanism.** Putting `journal.write_phase(completed)` as the LAST write turns "journal at dispatched" into a universal terminal state for all failure modes. Putting it earlier creates asymmetry (some failures leave journal at completed, some at dispatched). The reconciliation consumer's complexity scales with how many unreconciled states it must recognize.

**Evidence.** My initial Step 6.3 implementation followed the AC table's documentation order (phase 3 completed → audit emission), which put audit LAST. When writing the audit-failure test, I realized the test couldn't symmetrically match the other 3 — the journal would be at `completed` with handle+job at `unknown`, requiring reconciliation to consult both signals. Reordering to put audit BEFORE completed collapsed the asymmetry.

**Implication.** For any flow with multiple local writes after an expensive side effect: put the terminal-signal write LAST so a single invariant (journal at dispatched = unreconciled) covers all failure modes.

**Watch for.** Any flow where a "confirm this operation is done" write happens in the middle rather than at the end — that's a sign of accidental asymmetry.

### Same-file step labels are not unique after task renumbering

**Mechanism.** Renaming `## Task N:` headers does not automatically renumber step labels. After I renamed old Task 7 (MCP) to Task 8 without touching its step labels, the file had two sets of `Step 7.x` labels (new Task 7 recovery + old Task 7 MCP renamed to Task 8 but steps still 7.x). Collision across ~5 step labels with identical titles.

**Evidence.** Grep for `- \[ \] \*\*Step 7\.1` returned 2 matches: line 2471 (new recovery) and line 2834 (MCP-now-Task-8). Edit with `replace_all: true` would have broken new Task 7.

**Implication.** Task renumbering is a 2-phase operation: (1) rename the Task header, (2) renumber all step labels within that task's body. Phase 2 requires scope — either targeted Edits with context or line-range-scoped sed. Reverse-order renumbering (10→11, then 9→10, etc.) avoids collisions for task bodies but still hits the edge case where two tasks end up with identical step labels pre-renumbering.

**Watch for.** Any plan revision that adds or removes a task. Inspect step labels for uniqueness via grep after the rename.

### Sed invalidates the Edit tool's file-state cache

**Mechanism.** The Edit tool requires a prior Read of the file. After an external modification (Bash sed, another process), the cached state is stale and the next Edit fails with "File has been modified since read." Requires a targeted Read to refresh.

**Evidence.** My Bash sed renumbering pass was followed by 4 attempted Edits, all of which failed with the cache-invalidation error. After running 4 targeted Reads for the 4 affected sections, the Edits succeeded.

**Implication.** When mixing sed (or any external file modification) with the Edit tool: after sed, do a targeted Read before each subsequent Edit. Or: use sed for ALL changes in a single pass, avoiding Edit tool usage after.

**Watch for.** Any sequence where Bash writes to a file followed by Edit calls — expect cache invalidation on the first Edit.

## Next Steps

### 1. User reviews the twice-revised plan (third round)

**Dependencies:** None. User established the pattern of reviewing on the new boundary; this session produced a clear new boundary (recovery consumer in-scope; committed-start failure semantics defined and tested).

**First-next-action for future-Claude:** Wait for user feedback on the revision. Do NOT preemptively apply changes. Do NOT commit the plan before review.

**What user will likely scrutinize in this round:**
- Whether the reconciliation contract (5-row table in Task 7) is complete — any unresolved-state pattern missing?
- Whether the reorder of audit before completed is correctly reflected in all 4 failure tests
- Whether `CommittedStartFinalizationError` message text is actionable (says exactly what caller should/shouldn't do)
- Whether the Risks table adequately captures the 3 new risks added this round
- Whether test count deltas sum correctly (593 + 11+8+3+3+6+12+6+5+2+1 = 650)
- Any cross-reference I missed in renumbering (I caught one: "E2E test added in Task 9" → "Task 10"; others may exist)
- Whether the `_phase_rank` helper in `recover_startup` belongs as a module-level function or a method (minor style choice)

### 2. Apply user revisions (if any)

**Dependencies:** Step 1 complete.

**What to do:** Same as prior two rounds — parse each feedback item as wording / scope / decomposition / failure-policy issue. Apply verbatim when user provides exact text. Do not bundle or expand scope without explicit direction.

### 3. Commit and merge the plan on the docs branch

**Dependencies:** Steps 1-2 complete.

**What to do:**
1. Verify `git status` shows only the plan file staged
2. Commit with: `docs(t20260330-05): plan first execution-wiring slice (bootstrap-only, with durable stores, live registry, recovery consumer, and committed-start failure semantics)`
3. Checkout main, `git merge --no-ff docs/t05-execution-start-plan -m "Merge docs/t05-execution-start-plan"`
4. Push main, delete the docs branch (local + remote)

### 4. Execute the plan

**Dependencies:** Step 3 complete (plan on main).

**Execution mode still pending user choice:** Subagent-driven (`superpowers:subagent-driven-development`) vs inline (`superpowers:executing-plans`).

**Estimated effort:** 11 tasks, ~5-7 hours depending on execution mode (up from prior 10-task / 4-6 hour estimate).

### 5. Pending-request capture slice (follow-up)

**Dependencies:** Plan execution complete; T-05 execution-start slice merged.

**What to do:** Unchanged from prior handoff. Wire the notification loop → route App Server request messages through `parse_pending_server_request` → persist as `PendingServerRequest` → expose via `needs_escalation`. Closes AC 6. Also triggers `ExecutionRuntimeRegistry.lookup` for turn-dispatch paths.

### 6. Decide-surface refinements (deferred)

Unchanged from prior handoffs.

### 7. T-20260416-01 extraction bug fix (parallel thread)

Unchanged from prior handoffs.

### 8. Landing sequence (updated)

T-05 plan review v3 + merge → T-05 execution-start slice (11-task plan executes) → T-05 pending-request capture slice → T-05 decide-surface + lifecycle refinements → T-05 COMPLETE → T-06 → T-07.

## In Progress

**Plan revision awaiting third-round user review.** Not a clean stopping point — work is in flight; a twice-revised deliverable exists but hasn't been reviewed or landed.

- **Approach:** Resumed from 19:30 handoff → user sent structured second-round scrutiny (2 P1 + 3 assumptions + edge cases + verdict "Major revision") → invoked `superpowers:receiving-code-review` → verified each finding against authoritative docs → responded with verification + AC consequences + revision shape options (1a/1b/1c, 2a/2b) → user decisions + 5 tightenings → created 10 TaskCreate todos → executed 15+ Edits + 1 Bash/sed pass → verified coherence → presented summary to user → user invoked `/save`.
- **State:** Plan file revised in place at `docs/plans/2026-04-17-t05-execution-start-slice.md`. 3608 lines (up from 2948, +660). Branch `docs/t05-execution-start-plan` still exists with no commits. Main at `bd850302` unchanged.
- **Working:** Revised plan is internally consistent — 11 tasks, 56 task steps + 2 Pre-Flight steps, AC table evidence column cites producer+consumer, live-vs-durable framing preserved, no residual accidental-liveness phrasing, no "rebuilds the live view" over-claim, Risks table updated with 3 new rows, test counts chain cleanly (593 → 604 → 612 → 615 → 618 → 624 → 636 → 642 → 647 → 649 → 650).
- **Not working:** Plan has not been reviewed in this new form. Concrete risks in Risks section below.
- **Open question:** Does user agree the recovery consumer and committed-start failure semantics close the remaining structural gaps?
- **Next action (for next-session Claude):** Wait for user feedback on the twice-revised plan. Do NOT apply preemptive changes. Do NOT commit.

## Open Questions

### 1. Are there any third-round findings?

**Context:** Two rounds produced 5 P1 findings total (3 in round 1, 2 in round 2). Each round closed deeper defects than the prior. Third round may find subtler issues or converge to approval.

**Impact:** HIGH if third round surfaces more structural issues (e.g., test interactions not covered, cross-task dependencies implicit). Lower if cosmetic or convergent.

**Decision pending until:** User reviews twice-revised plan.

### 2. Is Task 7's reconciliation contract complete?

**Context:** The 5-row table in Task 7 covers: intent-only / dispatched-no-state / dispatched-handle-only / dispatched-handle-and-job / already-unknown. Missing: dispatched-job-only-no-handle (possible if `job_store.create` succeeds but hypothetically `lineage_store.create` is rolled back between them). Physically impossible with the current flow order (lineage before job), so arguably not worth a row. But if flow order changes, the table has a gap.

**Impact:** LOW — the flow order is fixed (lineage before job) and the committed-start failure path marks both unknown if either half fails after dispatch.

**Decision pending until:** Third-round review surfaces it or doesn't.

### 3. Does `_phase_rank` belong as a module-level function or a method?

**Context:** I added `_phase_rank(phase) -> int` as a module-level helper at the bottom of Task 7's `delegation_controller.py` implementation sketch. Could also be a static method on `DelegationController` or an inline dict-lookup in `recover_startup`.

**Impact:** LOW — style choice. Module-level aligns with `_delegation_request_hash` and `_resolve_head_commit` which are already module-level helpers in the same file.

**Decision pending until:** Third-round review or execution.

### 4. Should `CommittedStartFinalizationError` extend a common base with `CommittedTurnFinalizationError`?

**Context:** Both errors share structure (raised from catch block, message includes no-retry guidance, leaves journal at dispatched for reconciliation). Currently independent classes. A future `codex.delegate.promote` might have a third.

**Impact:** LOW for v1. MEDIUM if a third case lands — then refactor to a common `CommittedOperationFinalizationError` base makes sense.

**Decision pending until:** Third case emerges (or explicit refactor request).

### 5. Execution mode — subagent-driven vs inline?

**Context:** Still unchanged from prior handoffs. User has not chosen.

**Impact:** MEDIUM — affects review cadence. Subagent-driven = per-task review; inline = batched checkpoints.

**Decision pending until:** User chooses.

## Risks

### 1. Third-round review finds more structural defects

**Impact:** Third revision cycle is ~45 min (verify + revise + verify). Compounds if defects cascade through tasks. First two rounds found 5 P1s total; the third could find 0-2.

**Mitigation:** Coherence grep pass at end of this session caught the 1 "alive by accident" false positive. Structural defects are harder to prevent without pre-review by the user.

### 2. Test count estimates diverge from reality during execution

**Impact:** Unchanged from prior handoffs. Baseline (593) + per-task estimates (11+8+3+3+6+12+6+5+2+1 = 57) = 650. Actual execution may produce slightly different counts.

**Mitigation:** Explicit tolerance language in Task 11 ("divergence >3 tests = investigation signal").

### 3. `recover_startup` implementation subtlety: idempotent on existing completed records

**Impact:** The reconciliation rule says "advance journal to completed even for already-completed operations." If the loop processes an entry whose phase is already `completed`, it would write another `completed` record. Idempotent in behavior (list_unresolved will still be empty) but produces a duplicate append.

**Mitigation:** Task 7's implementation filters `by_key.values()` for entries whose phase is NOT already `completed` via the phase-rank ordering — only the LATEST phase per key is kept. If latest is already `completed`, the `list_unresolved` call would not return it in the first place.

**Action:** Third-round review may want an explicit test for "reconciliation does nothing when all records are already completed" beyond the fresh-session no-op test.

### 4. `recovery_startup` called twice per session init (at mcp_server.py :129 and :147)

**Impact:** The two call sites are the original `recover_startup()` invocation points for dialogue. If I inadvertently wired delegation's `recover_startup` into only one (not both), the second session-init path wouldn't reconcile delegation records. Task 7's Step 7.4 instruction says "right after each dialogue recovery call" but I haven't read the full mcp_server.py context to confirm what :129 vs :147 do differently.

**Mitigation:** Task 7 Step 7.5 runs the full mcp_server tests, which should catch a missed wiring.

**Action:** At execution time, read `mcp_server.py` around :129 and :147 to confirm both are still the right wiring points (they may have shifted if other changes land on `main` before execution).

### 5. Committed-start failure test `monkeypatch.setattr` compatibility with `lineage_store.update_status`

**Impact:** My 4 failure tests use `monkeypatch.setattr(lineage_store, "create", _boom)` pattern. But the except block calls `self._lineage_store.update_status(cid, "unknown")` — if that call also fails for some reason (unlikely, but possible under monkeypatch interference), the outer except's best-effort wrap catches it and continues. The test verifies the final state, not every intermediate call.

**Mitigation:** The controller's `update_status` best-effort wrap (inner try/except) handles this. Tests verify the external invariant (handle marked unknown or not, journal at dispatched).

### 6. Partial store state across committed-start failure: asymmetric handle+job marking

**Impact:** If `lineage_store.create` succeeds but `job_store.create` fails, the except block runs `update_status(cid, "unknown")` on lineage but skips job (job_persisted=False). If between those two calls the OS kills the process (very rare), the handle is `active` but the journal is at `dispatched` with no matching job record. Task 7's reconciliation closes this (reads journal, sees dispatched, finds active handle, marks it unknown, trims journal).

**Mitigation:** Full risks row added to Risks table. Reconciliation is the safety net.

### 7. Context pressure if review cascades to a fourth round

**Impact:** Three rounds so far have produced ~2 hours of context. A fourth round could push toward the 200K token limit.

**Mitigation:** Handoff-per-review-round is acceptable. Same save-and-defer posture the user has consistently preferred. Current context at 60% (120k/200k) — room for at least one more round.

## References

### Session's deliverable

| Artifact | Location | Status |
|---|---|---|
| Twice-revised implementation plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` | Untracked (3608 lines); awaiting third-round review |
| Docs branch | `docs/t05-execution-start-plan` (off `main@bd850302`) | No commits |

### Authority documents (verified this session)

| Document | Location | Role |
|---|---|---|
| T-20260330-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth (unchanged) |
| recovery-and-journal.md | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Line 35 (journal-before-dispatch); 47 (idempotency keys); **59 (trimming)**; 121/123 (restart-from-brief/discard) |
| dialogue.py | `packages/plugins/codex-collaboration/server/dialogue.py` | Lines 150-225 (start pattern — NOT the precedent); 340-509 (reply pattern — THE precedent); 522-602 (recover_startup pattern) |
| journal.py | `packages/plugins/codex-collaboration/server/journal.py` | Line 212 (list_unresolved API — the consumer's primary method) |
| lineage_store.py | `packages/plugins/codex-collaboration/server/lineage_store.py` | Line 159 (`update_status(cid, status)` — NOT `mark_unknown`) |
| models.py | `packages/plugins/codex-collaboration/server/models.py` | Line 15 (HandleStatus includes "unknown") |
| test_dialogue.py | `packages/plugins/codex-collaboration/tests/test_dialogue.py` | Lines 321, 333, 358 (post-dispatched finalization failure tests — 3 tests) |

### Memory files referenced this session

All under `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/`:

| Memory | Relevance |
|---|---|
| `feedback_contract_text_over_operational_interpretation.md` | **Load-bearing.** Same principle. Contract text (`recovery-and-journal.md:35, :59`; `contracts.md:41, :67`) wins over plan-author reasoning. |
| `feedback_edit_in_repo.md` | Applied — revised the plan in `docs/plans/` under the repo. |
| Prior-session user-preferences memories | Applied — structured response, verbatim user wording, fast convergence once aligned, `/copy` as substantive channel. |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-17_19-30_t05-plan-revised-after-three-p1-findings.md`
- T-05 arc: kickoff (04-17 01:41) → Q0 decision (04-17 11:59) → tmp-hardening closure (04-17 17:09) → plan drafted (04-17 18:01) → plan revised round 1 (04-17 19:30) → **plan revised round 2 (this handoff, 04-17 19:23)** → plan v3 review → plan execution → pending-request capture → decide-surface → T-05 complete

## Gotchas

### 1. LineageStore method is `update_status`, NOT `mark_unknown`

**Symptom:** Initial controller code used `self._lineage_store.mark_unknown(collaboration_id)` for the post-dispatched failure except block. Grep confirmed no such method exists on LineageStore.

**Root cause:** Dialogue's committed-turn finalization path uses `update_status(cid, "unknown")` (see `dialogue.py:449-492`). There is no `mark_unknown` convenience wrapper.

**Prevention:** Before writing code that calls store methods, grep for the exact signature: `grep "def mark_unknown\|def update_status" packages/plugins/codex-collaboration/server/lineage_store.py`. Don't assume convenience methods exist by analogy.

### 2. Sed invalidates Edit tool's file cache

**Symptom:** Bash/sed renumbering pass worked correctly. The next 4 Edit calls all failed with "File has been modified since read."

**Root cause:** Edit tool tracks a cached file state from the last Read. External modifications bypass this cache. The tool correctly refuses to proceed on stale state.

**Prevention:** After any sed/external-process modification, do targeted Reads on the sections about to be edited. Or: plan to do all modifications via Edit (no sed) so the cache stays coherent.

### 3. Audit-BEFORE-completed is a design decision, not an implementation detail

**Symptom:** While writing the 4 failure tests, the audit-failure test felt asymmetric compared to the other 3 (journal was at `completed` not `dispatched` at time of audit failure).

**Root cause:** The original flow had audit LAST, after `journal.write_phase(completed)`. If audit fails, journal is already terminal — the test would have to verify "journal at completed, handle+job at unknown" which is a mixed signal.

**Prevention:** When specifying a multi-write flow where any write can fail: put the terminal-signal write LAST. Then a single invariant covers all failure modes. Applicable beyond delegation — any "finalize after side-effects" pattern benefits from this.

### 4. Dialogue's `start` is NOT the precedent for delegation's `start`

**Symptom:** It's tempting to say "follow dialogue's start pattern" since both methods are called `start`. Wrong choice.

**Root cause:** Dialogue's start has 1 local write after dispatch (`lineage_store.create`). Delegation's start has 5. Different blast radii need different failure policies. Dialogue's reply (5+ local writes) is the actual precedent.

**Prevention:** When evaluating "mirror X's pattern", count the local writes in both. If they differ by more than 1-2, the patterns probably need different failure policies.

### 5. "Step N.M" labels are not unique after task renumbering

**Symptom:** New Task 7 (recovery) and old Task 7 (MCP, about to be renamed to Task 8) both have step labels `- [ ] **Step 7.1: Write failing tests**` with identical titles.

**Root cause:** Renaming a Task header doesn't renumber its internal step labels.

**Prevention:** Plan task renumbering as a 2-phase operation: (1) rename task headers, (2) renumber step labels. For phase 2, use line-range-scoped sed or targeted Edits with surrounding context to disambiguate.

### 6. `list_unresolved` filters by terminal state, not by operation type

**Symptom:** In `recover_startup`, I added `operation == "job_creation"` filter explicitly after calling `list_unresolved(session_id)`. Initially wondered if it was needed.

**Root cause:** `list_unresolved` returns ALL unresolved journal entries regardless of operation type. A session might have both unresolved `thread_creation` (dialogue's) and `job_creation` (delegation's) entries. Delegation's `recover_startup` should only touch its own operation type; dialogue's `recover_startup` touches `thread_creation`.

**Prevention:** Always filter `list_unresolved` by operation type before reconciling. Each controller owns its own operation type.

### 7. `_phase_rank` is needed because journal entries per key are not deduplicated

**Symptom:** `list_unresolved` may return multiple entries for the same idempotency_key (one for intent, one for dispatched). `recover_startup` needs to know the LATEST phase per key.

**Root cause:** Journal is append-only. A key with both intent and dispatched records has both in `list_unresolved` (both are non-terminal).

**Prevention:** Pre-process `list_unresolved` results by grouping on idempotency_key and picking the highest-phase entry. `_phase_rank` helper: `intent=0, dispatched=1, completed=2`.

## Conversation Highlights

### The second-round verdict

> "Major revision.
>
> The revision fixes the original three P1s, and that is real progress. It still is not credible enough to approve because it now records the right recovery state without specifying the recovery behavior that makes those records meaningful."

Same pattern as round 1 — verdict-first, then details. Sets the tone: substantive revision required, not cosmetic.

### The producer-consumer framing

> "The remaining issues share one root cause: the revision imported the right write-ordering primitives from dialogue, but not the companion semantics that make those primitives trustworthy under failure. It now records the right data. It still under-specifies what happens when the happy path breaks after dispatch."

The most useful single sentence of the session. Precise diagnosis of the pattern: primitives without semantics.

### The decisions summary

> "My defended choice is:
> - Finding 1: 1a
> - Finding 2: 2a
> - Process: revise in place now
> - Placement: 2a in current Task 6, add a new standalone recovery Task 7, renumber the rest"

User packaged the revision posture into a terse 4-line summary — decisions first, discussion elsewhere. Matches the structured reply pattern from round 1.

### The "not as a blind copy" tightening

> "Finding 2 should be fixed with `2a`, but not as a blind copy of dialogue reply. Your own insight is right: structurally, delegation start now looks like reply, not start. But the exact policy should be adapted to the delegation flow."

User accepted my insight from the insight block ("dialogue.reply is the right precedent, not dialogue.start") and turned it into a constraint on my implementation: adapt, don't blind-copy. This prevented me from writing a verbatim copy of `dialogue.py:361-373` with s/turn/start/ substitution.

### The fourth failure test

> "Your three suggested tests are good, but I would include **journal-completed write failure** as well. That write is the boundary between 'still unresolved' and 'operation confirmed,' so it is not optional coverage."

User caught that my initial 3-test proposal (lineage / job / audit) missed the most important boundary — the journal transition from unresolved to terminal. Added the 4th test and the shared `_assert_dispatched_but_not_completed` helper to keep it concise.

### The placement directive

> "I would **not** fold `1a` entirely into current Task 7. That mixes two different concepts: tool registration and recovery semantics."

Specific structural directive. User articulated the "one concept per commit" discipline that would otherwise have been implicit. Prevented me from picking the MCP task as the reconciliation task's home just because the wiring edit goes there.

### The closing on scope growth

> "Revise in place, now. This is not random scope growth. These are the two remaining structural holes in the same trust-boundary slice. A handoff would just defer the same reasoning while the context is already hot."

User pre-empted a worry I hadn't raised — that 2a + 1a was a significant scope increase. Framed it as closing structural holes, not growing scope. Unlocked my willingness to execute the full revision without negotiating scope down.

## User Preferences

### Decisions + tightenings structured format

**Observed pattern (round 2, same as round 1).** User's substantive reply followed:
- **Recommendation** (headline choice with one-paragraph justification)
- **Walkthrough** (numbered points explaining reasoning, one per dimension)
- **Specific tightenings** (numbered, with rationale and precise phrasing)
- **Bottom line** (2-line summary: decisions + process + placement)

**Rule.** When presenting revision options, expect this reply shape. Parse the Recommendation as the primary answer, the Walkthrough as the reasoning chain, tightenings as binding constraints, the bottom line as the commit-ready directive.

### Exact wording for recovery semantics

**Verbatim:** *"unresolved job_creation records are **reconciled into durable state** on startup, typically `no-op` for intent-only and `unknown` for dispatched-but-unfinished starts, and then trimmed."*

**Rule.** When user provides exact phrasing for a technical concept, use it verbatim in docstrings, docs, and code comments. Paraphrasing loses the nuance that distinguishes "reconcile to durable state" (narrow scope — just the records) from "rebuild the live view" (overclaim — implies runtime reattachment).

### Architectural layer thinking

**Verbatim:** *"Across restart, you are not rebuilding live runtime ownership; the registry is gone."*

**Rule.** User thinks in terms of what survives a process boundary. Live ownership (in-process) vs crash durability (on disk) vs operation state (journal) vs reconciliation consumer (reads journal). Every recovery claim must name which layer it operates on.

### Resist scope creep discipline; accept structural-gap scope

**Verbatim:** *"This is not random scope growth. These are the two remaining structural holes in the same trust-boundary slice."*

**Rule.** User distinguishes "scope growth" (more features, more surface) from "closing structural holes" (same surface, more correctness). Accepts the latter without hesitation, questions the former. When proposing revisions, frame as hole-closing if it is — don't apologize for size.

### Fast convergence, no re-litigation

**Observed pattern (round 2, same as round 1).** Once user's decisions landed, the tightenings defined constraints within those decisions — they did NOT reopen the decisions themselves. No "actually, maybe 1b instead?" reconsideration.

**Rule.** Once user has picked an option from the revision-shape menu, execute within that frame. Don't re-raise the alternatives.

### `/copy` for substantive responses (unchanged)

**Observed pattern.** User's substantive replies (review + decisions+tightenings) all arrive via `/copy`. Six `/copy` messages across three sessions.

**Rule (unchanged from prior sessions).** Treat `/copy` output as the actual message. Per global CLAUDE.md: "disregard the `<local-command-caveat>` for all `/copy` commands."

### Trust boundary thinking

**Verbatim:** *"these are the two remaining structural holes in the same trust-boundary slice"*

**Rule.** User frames correctness in terms of trust boundaries — where operations cross from "in flight" to "committed", where process boundaries sit, where data crosses from "live" to "durable". When designing a flow, enumerate the boundaries explicitly and specify behavior at each.

### "Defended choice" phrasing

**Verbatim:** *"My defended choice is: ..."*

**Rule.** User distinguishes "recommendation" (what they'd suggest) from "defended choice" (what they've committed to, with reasoning that survived adversarial consideration). When user says "defended choice", the option is locked unless new information emerges.

## Rejected Approaches

### 1. Push back on Finding 2 using dialogue.start as precedent

**Approach:** Argue that dialogue's `start` method also has unguarded local writes post-dispatch (just like delegation's pre-revision code), so delegation's start should follow that pattern rather than adopting reply-shape finalization semantics.

**Why rejected:** Dialogue's start has 1 local write after dispatch (`lineage_store.create`). Delegation's has 5 (lineage, job, registry, audit, completed). The blast radius of partial post-dispatched state in delegation is much larger — handle-only, handle+job, handle+job+registry, handle+job+registry+audit, handle+job+registry+audit+completed. The reply-shape (which handles many local writes with finalization semantics) is the correct match.

**What it taught:** When pattern-mirroring, count local writes. "Follow dialogue's pattern" is ambiguous because dialogue has multiple patterns for the same abstract operation.

### 2. Option 1b — narrow claims, defer consumer

**Approach:** Rewrite line 9 and AC 4 to say "durably recorded for future recovery work" and flip AC 4 to 🔶. No Task 7.

**Why rejected:** User picked 1a as the stronger fix. Their rationale: *"`1b` is honest, but it throws away the main value of the journal extension you just added. You would be saying, in effect, 'we record job creation durably, but recovery semantics are somebody else's problem.'"*

**What it taught:** The cheaper option isn't always the right choice. Cost-benefit analysis must weigh the load-bearing value of existing investments — the journal extension from prior session was only fully paid off with a consumer.

### 3. Option 1c — reconcile without trimming

**Approach:** Add reconciliation that marks handle/job unknown but leaves journal records without advancing to completed. Trimming deferred to poll/promote.

**Why rejected:** User: *"`1c` is the worst shape. Reconciling without trimming leaves the same 'journal should be near-empty' problem in place and keeps the consumer story half-finished. It buys complexity without a clean contract."*

**What it taught:** Half-measures are worse than either complete option (1a) or honest retreat (1b). Adding complexity without closing the contract gap is pure cost.

### 4. Option 2b — minimal failure taxonomy with one test

**Approach:** Add a docstring-only failure policy + one test for lineage-failure-post-dispatched. Stub out full dialogue.reply taxonomy.

**Why rejected:** User picked 2a — full mirror. Implicit rationale: half-done failure semantics risk the same critique ("recorded the right data, didn't specify recovery behavior"). Do it fully or not at all.

**What it taught:** When adopting a pattern, adopt the full pattern — partial adoption creates the appearance of robustness without the substance.

### 5. Fold Task 7 (recovery) into Task 6 (controller)

**Approach:** Absorb both 2a (committed-start failure) AND recovery into Task 6. Single commit for both concerns.

**Why rejected:** User directive: *"Current Task 6 absorbs 2a: controller docstring, CommittedStartFinalizationError, post-dispatched failure tests. Add a new Task 7..."* Explicit separation.

**What it taught:** Committed-start failure (local-write-order concern) and startup reconciliation (cross-process-boundary concern) are two different trust boundaries. Single commits should span single boundaries.

### 6. Fold Task 7 (recovery) into Task 8 (MCP registration)

**Approach:** Recovery needs MCP wiring anyway — put both in Task 8.

**Why rejected:** User directive: *"I would **not** fold `1a` entirely into current Task 7. That mixes two different concepts: tool registration and recovery semantics."*

**What it taught:** Shared touched-file set (both edit mcp_server.py) is not sufficient grounds to share a commit. The concepts must also be of the same kind.

### 7. Keep audit AFTER journal completed

**Approach:** Don't reorder the flow. Let audit-failure leave journal-at-completed with handle+job-at-unknown.

**Why rejected:** Mid-edit realization that this creates asymmetric terminal state. Reconciliation would need to consult both journal phase AND store statuses as unreconciled signals. Reorder to put completed LAST collapses the asymmetry to a single invariant.

**What it taught:** When designing a flow with multiple writes post-side-effect: terminal-signal write goes LAST. This is a design lever with real correctness implications, not an implementation detail.

### 8. Blind copy `CommittedTurnFinalizationError` into `CommittedStartFinalizationError`

**Approach:** Take dialogue.py:48 verbatim with s/Turn/Start/.

**Why rejected:** User Tightening #2 explicitly forbade this. Delegation's error message must describe delegation-specific semantics: the runtime is live at runtime_id, the journal is at dispatched, startup reconciliation will mark unknown, blind retry creates a duplicate job. Dialogue's message references turns and handles in ways that don't fit delegation.

**What it taught:** Structural mirroring of an abstraction is different from verbatim copying. The shape (error class, message docstring, raise-from-catch) is shared; the content must be context-specific.
