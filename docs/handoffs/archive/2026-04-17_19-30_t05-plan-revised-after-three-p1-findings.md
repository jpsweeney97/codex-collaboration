---
date: 2026-04-17
time: "19-30"
created_at: "2026-04-17T19:30:00Z"
session_id: d6c261fb-4f97-4dd4-b5ad-f305cd3c58b2
resumed_from: "docs/handoffs/archive/2026-04-17_18-01_plan-t05-execution-start-slice-drafted-awaiting-review.md"
project: claude-code-tool-dev
branch: docs/t05-execution-start-plan
commit: bd850302
title: "T-05 plan revised after three P1 findings; awaiting review on new boundary"
type: handoff
files:
  - docs/plans/2026-04-17-t05-execution-start-slice.md
---

# T-05 Execution-Start Plan — Revised after three P1 findings; awaiting review

## Goal

Turn the 18:01 handoff's pending review cycle into a concrete scrutiny → revision round trip on the T-05 execution-start plan. User reviewed the plan and returned three P1 findings (handle persistence missing, runtime orphaned, journal-before-dispatch violated). All three needed to be verified against normative authority docs (not taken on faith), the revision shape negotiated with the user, then executed in-place.

**Bigger picture.** T-05 is the execution-domain foundation for codex-collaboration. This session's plan-review round is the cheap gate before expensive execution — getting the plan right turns a potential weekend of rework into a merge-ready slice in hours. The prior session's "plan-as-contract" framing was load-bearing: the plan must survive adversarial review before execution begins.

**Trigger.** Resumed from the 18:01 handoff explicitly waiting on user feedback. User's review arrived as a structured `/copy` message with three P1 findings + an open question + a minimum fix set, plus the verbatim verdict: "I would not approve the plan as written." That verdict drove the session: all three findings had to be resolved with literal evidence, not discussion.

**Success criteria for this session:**

1. ✅ Each cited finding verified against the authoritative source before responding (no performative agreement).
2. ✅ All three P1 findings confirmed as structurally correct (not pushed back).
3. ✅ User's additional tightenings (journal surface, registry framing) accepted and incorporated.
4. ✅ Open question on publication posture resolved through explicit options, not silent choice.
5. ✅ Plan revised in place (not v2 file), all 10 tasks coherent, AC evidence rewritten.
6. ✅ No accidental-liveness reasoning remaining in plan text.

All six met. Plan file on `docs/t05-execution-start-plan` still untracked; HEAD unchanged at `bd850302`.

## Session Narrative

**Phase 1 — Load handoff, prepare for review (~2 min).** `/load` resolved the 18:01 handoff cleanly; the state file was written at `docs/handoffs/.session-state/handoff-d6c261fb-4f97-4dd4-b5ad-f305cd3c58b2`. Git clean on `main@bd850302`. Summary noted: plan is untracked at `docs/plans/2026-04-17-t05-execution-start-slice.md`, user has explicitly deferred review to this session. Positioning set correctly: **wait for feedback, do not pre-emptively edit**.

**Phase 2 — Receive scrutiny (~immediate).** User posted a `/copy` structured review. Three P1 findings, one open question, a five-item minimum fix set, and the verdict "I would not approve the plan as written." Each finding cited specific lines:

- `contracts.md:41` and `:67` — lineage-store for delegation handles, DelegationJob's `collaboration_id` presupposes the handle
- plan `:1429`, `:1398` — the `_session` / `_thread_id` discard + busy-gate write combination
- `recovery-and-journal.md:35` + `:47` — journal-before-dispatch + explicit `Job creation` idempotency key
- `dialogue.py:192`, `:157` — reference implementation for handle persistence + journal-before-dispatch
- `jsonrpc_client.py:21` — subprocess ownership

**Phase 3 — Apply `superpowers:receiving-code-review` skill (~30s).** Invoked the skill before responding. The skill's core discipline: technical verification before implementation; no performative agreement; verify each claim against the codebase; push back only if wrong. Key rule engaged: "Verify. Question. Then implement."

**Phase 4 — Verify each finding against the authority docs (~5 min, parallel reads).** Batched reads of:
- `contracts.md` lines 1-100 — confirmed `:41` literal: *"Dialogue and delegation handles are persisted by the lineage store"*; confirmed `:67` schema (`collaboration_id` = "Associated CollaborationHandle")
- `recovery-and-journal.md` full — confirmed `:35` literal: *"Journal before dispatch"*; confirmed `:47` explicit `Job creation` → `claude_session_id + delegation_request_hash`
- `dialogue.py` lines 130-250 — confirmed three-phase discipline pattern (intent at `:157`, dispatched at `:178`, handle persist at `:192-205`, completed at `:207`)
- `jsonrpc_client.py` lines 1-80 — confirmed `JsonRpcClient` owns `subprocess.Popen`; confirmed the session wraps the client
- Plan at lines 30-60 (AC table + intro), 1380-1470 (Task 5 body including `_session` discard + accidental-liveness note), 2090-2160 (Task 9 merge)

All three citations held exactly as user claimed. None could be pushed back.

**Phase 5 — Analyze downstream AC consequences (~2 min).** Recognized the findings extend beyond the cited ACs:
- Finding 1 (handle missing) weakens AC 4 ✅ to 🔶 — "Job state persisted" cannot be claimed when the handle layer is missing
- Finding 2 (orphaned runtime) weakens AC 1 ✅ to 🔶 — "Can start" implies controllable; orphan isn't
- Finding 3 (journal) reinforces the AC 4 weakening — replay-safety depends on journal records

This analysis was load-bearing: the initial response needed to name these cascading impacts, not just the direct findings. The prior session's self-review checked AC wording at the text level but missed the contract level — a self-review discipline hole.

**Phase 6 — Respond with verification + revision shape + open questions (~3 min).** Response structure per the skill:
1. Verification of each finding (terse citations, not "you're right")
2. AC table consequences (ACs 1 + 4 need to flip to 🔶 pre-fix)
3. Revision shape (6 concrete changes, labeled)
4. Step-9 publication open question (local merge vs PR) — options (a)/(b)/(c)
5. Process questions (revise in-place vs v2; now vs defer)
6. Explicit hold-until-direction-given statement

Key choice: presenting the step-9 open question as three options rather than picking silently. Same "name the variants before picking" discipline from the prior session.

**Phase 7 — User response: three decisions + two tightenings (~2 min).** User replied via `/copy` with:
- **Decision 1:** Keep local merge-and-push (option a) — cited project guardrail
- **Decision 2:** Revise in-place (not v2)
- **Decision 3:** Revise now (not handoff-and-defer)
- **Tightening 1:** Journal fix is broader than `_VALID_OPERATIONS` — must also extend `OperationJournalEntry` (model literal + `job_id` field) and `_journal_callback` (per-phase validator rules). Use recovery-contract idempotency key `claude_session_id + delegation_request_hash`, not dialogue-style `session_id + collaboration_id`.
- **Tightening 2:** Registry is live ownership only, NOT crash durability. Plan must say this explicitly so AC 1 + 4 are not overclaimed on the basis of the wrong layer.

Plus explicit expectations:
- Task 6 creates both `CollaborationHandle` + `DelegationJob`
- Task 6 follows dialogue pattern deliberately (journal intent → side effects → persist handle + job → register runtime → mark completed)
- AC table flips AC 1 + 4 to ✅ only if changes are in task text, not just risks/notes
- Remove "runtime stays alive because subprocess handle exists somewhere" reasoning (the accidental-liveness claim)

User closing: *"Proceed with an in-place revision now. When you've updated the draft, send it back and I'll review the revised plan on the new boundary."*

**Phase 8 — Ground in current plan structure and journal model (~3 min).** Before executing, batched reads of:
- Current plan task headings (grep `^## Task \d`)
- `models.py:250-295` — confirmed `OperationJournalEntry.operation: Literal["thread_creation", "turn_dispatch"]` (only two ops — user's claim about limited current shape is correct)
- `journal.py` full — confirmed `_VALID_OPERATIONS` frozenset, `_journal_callback` per-phase validator structure, `_JOURNAL_OPTIONAL_STR` list. Confirmed validator has branches for `turn_dispatch` at intent/dispatched and `thread_creation` at dispatched. Adding `job_creation` needs its own branches.

This grounding prevented me from specifying journal extensions in a way that would fail validator construction at runtime.

**Phase 9 — Execute edit series (~25 min, 15+ Edit calls).** Serial edits because Edit tool works on one file at a time with stateful matching:

1. **Edit 1 — Goal + Architecture (lines 5-11):** Restructured goal to enumerate all durable surfaces. Architecture paragraph mirrors dialogue pattern explicitly. Added "Persistence layering — live vs. durable" paragraph making the registry's limited role explicit.

2. **Edit 2 — Scope Lock in-scope (11 items) + out-of-scope (8 items):** Added handle persistence, journal extension (4 sub-items), registry. Removed "no operation-journal entries for job creation" from out-of-scope. Added runtime teardown deferral.

3. **Edit 3 — AC table rewritten with Evidence column:** 3-column table (AC / Status / Evidence). Every ✅ cites the specific task and implementation step. AC 1 now cites `ExecutionRuntimeRegistry.register` retaining session. AC 4 cites all three durable stores.

4. **Edit 4 — File Structure:** Added `execution_runtime_registry.py` + test file to new-files table. Added `journal.py` + `test_journal.py` to modified-files table. Updated controller description to mention three-phase discipline.

5. **Edit 5 — Decomposition Philosophy:** Updated to reference new Task 5 position and added test-count tolerance note.

6. **Edit 6 — Task 1 full replacement:** Title → "Delegation Model Types + Journal Extension". Added Step 1.2 (journal validator tests, 4 new). Added Step 1.5 (journal.py extension — `_VALID_OPERATIONS`, `_JOURNAL_OPTIONAL_STR`, `_journal_callback` branches). Extended Step 1.4 to modify `OperationJournalEntry.operation` literal + add `job_id` field. Commit message: `feat(t20260330-05): add DelegationJob types and extend journal for job_creation`. Expected count: baseline + 11 → 604.

7. **Edits 7-9 — Tasks 2/3/4 cumulative count updates** (3 edits). 606→612, 609→615, 612→618.

8. **Edit 10 — Big Task 5 replacement:** This was the largest edit. Replaced old Task 5 (DelegationController, 426 lines of content) with new Task 5 (ExecutionRuntimeRegistry, ~220 lines) + new Task 6 (DelegationController, heavily rewritten, ~600 lines). The Edit tool matched only the opening of old Task 5 (header through Step 5.1), inserting new content after. That left leftover content. Fixed with Edit 11.

9. **Edit 11 — Cleanup leftover:** Deleted the ~420 lines of residual old Task 5 body that was now sandwiched between the new Task 7 header I'd inserted and the original Task 6 header. Consolidated into a single `## Task 7: MCP Tool Registration` header.

10. **Edits 12-15 — Task 7 (MCP) step renumbering:** Step 6.1 → 7.1, 6.2 → 7.2, 6.3 → 7.3. And combined step 6.4/6.5 update with `ExecutionRuntimeRegistry` added to `__init__.py` exports + expected count updated to 637.

11. **Edit 16 — Task 8 (Production Wiring) full rewrite:** Renumbered 7.x → 8.x. Added second smoke test (`test_delegation_factory_passes_shared_runtime_registry`) that verifies main()'s registry reference is the one the controller receives. Factory signature gains `runtime_registry` parameter, constructs `LineageStore` inside the factory closure (matches dialogue pattern — session-scoped). main() constructs `ExecutionRuntimeRegistry` once. Expected count: 639.

12. **Edit 17 — Task 9 (Integration) full rewrite:** Renumbered 8.x → 9.x. Integration test now constructs LineageStore + ExecutionRuntimeRegistry and passes them to controller. Verifies: handle persisted (`capability_class="execution"`, `runtime_id` matches), registry lookup returns entry with correct `job_id`, all three journal phases present (`intent`/`dispatched`/`completed`), idempotency key matches `sha256(repo_root + head)` form. Expected count: 640.

13. **Edit 18 — Task 10 (Verify+Merge) rewrite:** Renumbered 9.x → 10.x. Ruff target list extended with `journal.py` + `execution_runtime_registry.py`. Test count guidance with "~640 passed" + "divergence >3 tests = investigation signal".

14. **Edit 19 — Risks and Known Deferrals:** Removed "no registry" row (now closed). Removed "no operation-journal entries" row (now closed). Added explicit "registry is live-ownership only" row with `recovery-and-journal.md:121,123` citations for restart/discard paths. Added runtime teardown deferral row. Added forward-compat risk row for `delegation_request_hash` input shape.

**Phase 10 — Verify revision coherence (~2 min).** Post-revision verification:
- `grep ^## Task \d` → 10 tasks sequential (1-10)
- `grep Step \d\.\d` → 45 step labels, consistent with task numbers
- `grep accidental|kept alive by the caller|garbage-collected` → 0 matches (removed successfully)
- `grep live ownership|crash durability|durable stores` → framing present in 11 locations (goal, architecture, persistence layering, in-scope, AC 7, file structure, registry module docstring, registry class docstring, controller comment, smoke test docstring, risks row)
- `wc -l` → 2948 lines (up from 2162; +786 lines for three P1 fixes + tightenings)
- `grep "git add packages/plugins/codex-collaboration"` → 9 commit commands, each correctly scoped to its task's files

**Phase 11 — Present summary to user (~2 min).** Summary covered: structural deltas, task map with changes per task, AC table changes, framing verification, what was NOT changed (Tasks 2/3/4 content, publication posture, test-count guidance language). Explicit statement: draft ready for review; same save-and-wait posture.

**Phase 12 — User invoked `/save` (~immediate).** Saving this handoff now. No commit, no merge.

## Decisions

### Decision 1: Accept all three P1 findings without pushback

**Choice:** All three P1 findings (handle persistence missing, runtime orphaned, journal-before-dispatch violated) were verified as structurally correct and accepted as binding revisions to the plan.

**Driver.** Each finding cited specific lines in authoritative docs. I read each cited line and confirmed the user's interpretation was literal:
- `contracts.md:41` literal: *"Dialogue and delegation handles are persisted by the lineage store"*
- `recovery-and-journal.md:35` literal: *"Journal before dispatch. Every dispatched operation is written to the journal before the corresponding App Server request is sent."*
- plan `:1429` code literally discarded `_session` and `_thread_id`, plan `:1398` wrote `DelegationJob.status="queued"` which makes `list_active()` return it forever (busy-gate deadlock)

**Alternatives considered:**
- **Push back on any finding:** rejected — each finding was backed by literal spec text. `superpowers:receiving-code-review` rule: "Push back with technical reasoning if wrong" — none was wrong.
- **Accept but minimize:** rejected — user's closing verdict "I would not approve the plan as written" was unambiguous. Minimization would have been performative "fix" without genuine repair.

**Implications.** Plan requires substantive, not cosmetic, revision. New task added (Registry), one major task rewritten (Controller), others renumbered. Plan grew ~36% in line count. Test count estimate goes from 624 → ~640. Commit count goes from 8 → 9.

**Trade-offs accepted.** Revision effort was real (~25 minutes of editing). Cheaper than the alternative: merging a broken plan that would have produced a deadlock bug on the second integration test call.

**Confidence:** High (E2) — authority text verified directly; codebase pattern cross-checked via `dialogue.py`.

**Reversibility:** High at plan level (plan is a doc; text-editable). Low at execution level (shipping the original plan would have created a structural bug).

**Change trigger:** None — findings are grounded in normative docs that won't change.

### Decision 2: Registry as separate module `execution_runtime_registry.py`

**Choice:** The `ExecutionRuntimeRegistry` class lives in its own file `server/execution_runtime_registry.py`, not embedded in `control_plane.py`.

**Driver.** Matches the repo's one-concept-per-file convention (`lineage_store.py`, `worktree_manager.py`, `approval_router.py` all follow this). User's phrasing "control-plane-owned registry" describes ownership/access, not file location.

**Alternatives considered:**
- **Embed in `control_plane.py`:** rejected — `control_plane.py` is already 477 lines; embedding would push concerns together that are cleanly separable.
- **Embed as nested class in `DelegationController`:** rejected — the registry has its own lifecycle (per-plugin-instance, not per-controller-call) and should be testable independently.

**Implications.** Import hygiene: controller imports from `execution_runtime_registry`, production bootstrap constructs registry directly. Registry can be shared across multiple controllers in the same plugin process if that ever becomes needed.

**Trade-offs accepted.** One more file in `server/`. Mitigated by the file being small and focused.

**Confidence:** High (E1) — matches repo convention, no one contested the placement.

**Reversibility:** High — mechanical file move if needed.

**Change trigger:** If the registry needs privileged access to control-plane internals (it doesn't today), embedding would be revisited.

### Decision 3: Journal extension bundled into Task 1

**Choice:** `OperationJournalEntry.operation` literal extension + `job_id` field + `journal.py` validator extension all land in Task 1 (previously "Delegation Model Types", now "Delegation Model Types + Journal Extension").

**Driver.** Journal model and delegation model are both "type vocabulary for delegation" — one concept at the commit level. Separating journal extension into its own task would produce a commit that can only be reviewed in isolation from the model additions that depend on it (Literal type, `job_id` field).

**Alternatives considered:**
- **Separate journal-extension task (Task 2, shifting all others):** rejected — would renumber Tasks 2-9 → 3-10, doubling the renumbering workload. The commit-coherence benefit is marginal because the journal extensions logically couple to the model changes.
- **Split journal model changes from validator changes across two commits:** rejected — the model Literal and validator `_VALID_OPERATIONS` must stay in sync; splitting risks an intermediate commit with a broken validator.

**Implications.** Task 1 grows from 5 tests / ~200 lines to 11 tests / ~440 lines. Single commit covers: models.py (4 additions/changes) + journal.py (3 changes) + 2 test files.

**Trade-offs accepted.** Larger single commit than the rest of the plan. Mitigated by all changes being additive type-vocabulary work.

**Confidence:** Medium (E1) — judgment call, user didn't explicitly dictate task count.

**Reversibility:** Medium — splitting later would require re-cleaving the commit.

**Change trigger:** User preference for finer-grained commits on journal-extension review.

### Decision 4: Registry framed as "live ownership, not crash durability" in 11+ locations

**Choice:** The live-vs-durable distinction is repeated across the plan: goal, architecture, dedicated "Persistence layering" paragraph, scope in-scope #7, AC 7 evidence, file structure description, Task 5 goal, registry module docstring, registry class docstring, controller comment at `registry.register` step, factory smoke-test docstring, E2E integration test comment, risks table row.

**Driver.** User Tightening #2 verbatim: *"Treat `ExecutionRuntimeRegistry` as **live ownership**, not crash durability. It solves the orphaned-runtime problem inside the running process. It does not replace lineage/job persistence or journaled recovery state. The revised plan should say that explicitly so AC 1 and AC 4 are not overclaimed for the wrong reason."*

**Alternatives considered:**
- **State once in the module docstring:** rejected — one location is easily overlooked. User explicitly asked for the plan to say this "explicitly" — implies repeated, not one-off.
- **State in the risks table only:** rejected — that's where the wrong layer would be noticed after the error was made. The framing must be preventative, placed at every touch point.

**Implications.** Future-Claude reviewing the plan hits this framing at every decision point (what to test, what to persist, how to recover). Nearly impossible to accidentally rely on the registry for durability.

**Trade-offs accepted.** Some prose repetition. Mitigated by each location having a slightly different phrasing appropriate to context (e.g., module docstring talks about implementation, AC table cites evidence, risks row cites recovery paths).

**Confidence:** High (E1) — directly from user directive, verified by grep that framing appears in 11 locations.

**Reversibility:** High — text-editable.

**Change trigger:** If the registry evolves to have durability (it shouldn't), framing would be revised.

### Decision 5: Idempotency key `claude_session_id + delegation_request_hash`

**Choice:** The `job_creation` operation's idempotency key is `f"{claude_session_id}:{delegation_request_hash}"` where `delegation_request_hash = sha256(f"{repo_root}:{base_commit}")`.

**Driver.** User Tightening #1 verbatim: *"Also use the recovery-contract idempotency key, which is `claude_session_id + delegation_request_hash`, not the dialogue-style `session_id + collaboration_id`."*

Verified at `recovery-and-journal.md:47` — row reads: `Job creation | claude_session_id + delegation_request_hash | Check if job already exists`.

**Alternatives considered:**
- **`session_id + collaboration_id`** (dialogue-style): rejected — `collaboration_id` is random per call; can't recognize replay of the same underlying request.
- **`session_id + job_id`:** rejected — `job_id` is also random per call; same failure mode as above.
- **`session_id + repo_root`:** rejected — doesn't capture base_commit, so two calls with same repo but different base would collide.

**Implications.** Replay of the same `(repo_root, base_commit)` pair during crash recovery recognizes the same key. Different `base_commit` → different key → treated as a new job. This is correct semantics because each worktree is base-commit-anchored.

**Trade-offs accepted.** If `codex.delegate.start` ever accepts additional inputs (objective, profile, brief), they must be folded into the hash. Called out as forward-compat risk #7 in the Risks table.

**Confidence:** High (E2) — literal spec citation + pattern logic agree.

**Reversibility:** Medium — changing the hash input shape breaks replay for already-created jobs. Not a concern in v1 because no jobs exist yet.

**Change trigger:** MCP surface adds input parameters to `codex.delegate.start`.

### Decision 6: Publication stays local merge-and-push (not PR)

**Choice:** Task 10 keeps `git checkout main; git merge --no-ff; git push origin main`. No PR flow.

**Driver.** User Decision #1 verbatim: *"(a) Keep local merge-and-push for this plan. The earlier Step 9 flag is not a blocker. Given the established T-05 chain and your explanation that this repo's effective guardrail is 'don't edit/write directly on main,' I would not force a one-off PR convention change inside this plan revision. If we want to change publication posture, that should be an explicit repo-level decision, not an incidental side effect of this fix round."*

**Alternatives considered:**
- **PR flow:** rejected by user — cited scope discipline (don't shift repo convention inside a plan fix)
- **PR flow as new standing convention:** rejected by user — same reasoning

**Implications.** Publication matches prior T-05 chain (substrate slice, tmp-hardening merge). Branch-protection hook guards `Edit`/`Write` on main; local `merge` is unaffected. CI runs post-push, not pre-merge.

**Trade-offs accepted.** No pre-merge CI signal. Mitigated by Task 10.1 full plugin suite + Task 10.2 ruff check before merge.

**Confidence:** High (E1) — explicit user directive.

**Reversibility:** High — Task 10 steps are text-editable.

**Change trigger:** Repo-level decision on publication posture (explicitly out of scope for this session).

### Decision 7: Revise in-place, not as v2 file

**Choice:** Modifications applied directly to `docs/plans/2026-04-17-t05-execution-start-slice.md`.

**Driver.** User Decision #2 verbatim: *"revise in place on `docs/t05-execution-start-plan`. The file is uncommitted, and these are corrective changes to the same plan, not a second durable artifact. A parallel `v2` file would add churn without preserving anything valuable."*

**Alternatives considered:** `docs/plans/2026-04-17-t05-execution-start-slice-v2.md` preserving v1 — rejected by user as churn-generating without value.

**Implications.** Git history shows only the revised plan. No way to `diff v1 v2` after the fact — but the plan was never committed, so v1 content is gone.

**Trade-offs accepted.** If the user later wants to compare original scope vs revised scope, the only reference is conversation history.

**Confidence:** High (E1) — explicit user directive.

**Reversibility:** Low — original plan text is no longer accessible via git.

**Change trigger:** N/A — directive is clear.

### Decision 8: Revise now, not handoff-and-defer

**Choice:** Revision executed in the same session that received the scrutiny.

**Driver.** User Decision #3 verbatim: *"revise now in this session. The defects are concrete and bounded. No handoff is needed just to repair the draft and run one more scrutiny pass."*

**Alternatives considered:** Save handoff, defer revision — rejected by user because the fix set is bounded.

**Implications.** Session scope expanded from "answer review" to "answer review + full revision." Context used: ~80k tokens for verification + revision. Still well under budget.

**Trade-offs accepted.** No fresh-eyes pass between scrutiny and revision. Mitigated by the revision being mechanical (user's fix set was prescriptive) and by grep-verification of the result.

**Confidence:** High (E1) — explicit user directive.

**Reversibility:** N/A — the revision is done.

**Change trigger:** N/A.

## Changes

### Files modified (this session)

| File | Change | Commit |
|---|---|---|
| `docs/plans/2026-04-17-t05-execution-start-slice.md` | Revised in place: 2162 → 2948 lines (+786). New Task 5 (Registry), rewritten Task 6 (Controller), renumbered Tasks 7-10, extended Task 1 (journal), expanded Task 8 (factory), extended Task 9 (integration), rewritten AC table, rewritten Risks table. | Uncommitted |

### Git state changes

| Commit | Branch | Subject |
|---|---|---|
| (none) | `docs/t05-execution-start-plan` | Branch unchanged; plan still untracked |

No commits. No push. Main unchanged at `bd850302`.

### Handoff / state files

- Archived (at session start): `2026-04-17_18-01_plan-t05-execution-start-slice-drafted-awaiting-review.md` → `docs/handoffs/archive/`
- State file: `docs/handoffs/.session-state/handoff-d6c261fb-4f97-4dd4-b5ad-f305cd3c58b2` — to be cleaned by this save
- New handoff (this file): `docs/handoffs/2026-04-17_19-30_t05-plan-revised-after-three-p1-findings.md`

## Codebase Knowledge

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `docs/handoffs/2026-04-17_18-01_plan-t05-execution-start-slice-drafted-awaiting-review.md` | Prior handoff (resumed) | Full context: plan drafted but awaiting review; Variant A scope lock; 4 user guardrails |
| `docs/superpowers/specs/codex-collaboration/contracts.md` (lines 1-100) | Verify P1 finding #1 | Line 41 literal confirms lineage-store persistence; line 67 confirms `collaboration_id` presupposes handle |
| `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` (full) | Verify P1 finding #3 | Line 35 literal confirms "journal before dispatch"; line 47 confirms `Job creation` idempotency key structure |
| `packages/plugins/codex-collaboration/server/dialogue.py` (lines 130-250) | Verify reference pattern | Three-phase discipline at 157/178/207; handle persistence at 192-205 — the mirror target for the delegation controller |
| `packages/plugins/codex-collaboration/server/jsonrpc_client.py` (lines 1-80) | Verify P1 finding #2 | `JsonRpcClient` owns `subprocess.Popen`; session wraps client — orphan analysis correct |
| `packages/plugins/codex-collaboration/server/models.py` (lines 250-295) | Ground journal extension | Confirmed `OperationJournalEntry.operation` is `Literal["thread_creation", "turn_dispatch"]` — only 2 ops; no `job_id` field |
| `packages/plugins/codex-collaboration/server/journal.py` (full) | Ground journal extension | `_VALID_OPERATIONS` frozenset; `_journal_callback` per-phase required-fields pattern; `_JOURNAL_OPTIONAL_STR` tuple |
| Plan file (multiple section reads) | Ground revision edits | Precise old_strings for each Edit call |

### Architecture: where live and durable layers sit

| Layer | File | Purpose | Crash-durable? |
|---|---|---|---|
| Identity (handles) | `server/lineage_store.py` | `LineageStore` — per-session JSONL of `CollaborationHandle` | Yes |
| Job lifecycle | `server/delegation_job_store.py` (new) | `DelegationJobStore` — per-session JSONL of `DelegationJob` | Yes |
| Replay-safe recovery | `server/journal.py` | `OperationJournal` — per-session operation journal with idempotency | Yes |
| Live ownership | `server/execution_runtime_registry.py` (new) | `ExecutionRuntimeRegistry` — in-process dict of `(session, thread_id, job_id)` | **No** — by design |

The user's tightening #2 is a rule about this layer split: the registry is the ONLY non-durable layer. All three others must be populated before `register` is called.

### Architecture: T-06 Controller flow (mirror of dialogue)

| Step | Dialogue (`dialogue.py`) | Delegation (revised plan) |
|---|---|---|
| Idempotency key | `f"{session_id}:{collaboration_id}"` | `f"{session_id}:{delegation_request_hash}"` |
| Phase 1 (intent) | `:157-169` | Task 6 Step 6.3 |
| Side effect | `runtime.session.start_thread()` `:172` | `worktree_manager.create_worktree` + `control_plane.start_execution_runtime` |
| Phase 2 (dispatched) | `:178-190` | Task 6 Step 6.3 |
| Persist identity | `lineage_store.create(handle)` `:205` | `lineage_store.create(handle)` in Task 6 |
| Persist lifecycle | (none — dialogue is stateless turn-by-turn) | `job_store.create(job)` in Task 6 |
| Register live | (none — runtime registered by ControlPlane cache) | `runtime_registry.register(...)` in Task 6 |
| Phase 3 (completed) | `:208-218` | Task 6 Step 6.3 |
| Audit emit | Via `finalize_confirmed_turn` (after turn, not in `start`) | `journal.append_audit_event` with `delegate_start` in Task 6 |

### Surprising findings / gotchas

- **The user's claim `OperationJournalEntry` has no `job_id` field was precisely correct.** `models.py:273-294` shows the dataclass ending with `context_size` — no `job_id`. Adding it is a structural extension, not a cosmetic one.
- **`journal.py::_journal_callback` has a specific pattern for per-phase required fields.** The existing branches (lines 79-94 in `journal.py`) use `op == "turn_dispatch" and phase in ("intent", "dispatched")` conditionals. The `job_creation` branches must follow this pattern to be validator-consistent.
- **The old `_session` discard at plan `:1429` + the busy-gate write at `:1398` was a two-line construction that created a deadlock.** One line alone would have been OK; in combination, the path could never transition out of "busy". This is why the user's framing emphasized permanence of the deadlock ("can become permanently `Job Busy` after the first successful start").
- **`dialogue.py:192-205` does NOT set `capability_class="advisory"` explicitly** — it writes it implicitly as part of the `CollaborationHandle(..., capability_class="advisory", ...)` construction. The delegation mirror must use `capability_class="execution"` — easy to miss.
- **`LineageStore` is session-scoped (takes `session_id` at init)**. This means it can't be constructed in `main()` before `_read_session_id` succeeds. The factory must construct it inside the factory closure. The dialogue factory follows this pattern, and the delegation factory must mirror it.
- **`_journal_callback` constructs an `OperationJournalEntry` at the end, forwarding all known fields**. Adding `job_id` means both the validator branches AND the `OperationJournalEntry(...)` call at line 100-111 must forward it. Easy to forget the second.

### Key locations to remember

| Concept | Location |
|---|---|
| T-05 plan (revised) | `docs/plans/2026-04-17-t05-execution-start-slice.md` |
| Lineage-store contract | `docs/superpowers/specs/codex-collaboration/contracts.md:39-57` |
| DelegationJob schema | `docs/superpowers/specs/codex-collaboration/contracts.md:59-73` |
| Journal-before-dispatch rule | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md:33-39` |
| Job creation idempotency key | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md:47` |
| Dialogue controller three-phase pattern | `packages/plugins/codex-collaboration/server/dialogue.py:154-225` |
| Dialogue handle persistence | `packages/plugins/codex-collaboration/server/dialogue.py:192-205` |
| Operation journal validator | `packages/plugins/codex-collaboration/server/journal.py:49-112` |
| `_VALID_OPERATIONS` | `packages/plugins/codex-collaboration/server/journal.py:35` |
| `OperationJournalEntry` | `packages/plugins/codex-collaboration/server/models.py:273-294` |
| `JsonRpcClient` subprocess ownership | `packages/plugins/codex-collaboration/server/jsonrpc_client.py:21-60` |

## Context

### Mental model

**Framing:** This session is a **verify-before-agree** round trip on a plan-as-contract. The review is a scrutiny gate; the revision is the reconciliation step; the handoff is the pause that waits for the next scrutiny pass.

- **Core insight:** Every claim in the plan (especially AC coverage) is backed by a literal implementation step. "AC 4 ✅" means exactly "Task 6's Step 6.3 writes these three records to these three stores". The evidence column in the AC table turns the status into a traceable assertion.
- **Mental model:** *Plan-as-contract with adversarial review gate.* The plan's role isn't to describe what will be built — it's to be *unbreakable under scrutiny*. Every sentence in the plan has to survive "but why not X?" questions from a skeptical reader. The revised plan is the result of that gate catching three things the draft missed.

Secondary insight: the live/durable split is a **type-theoretic observation** about what kinds of data can cross a process boundary. `AppServerRuntimeSession` holds `subprocess.Popen` — non-serializable, process-bound. `CollaborationHandle` holds string IDs and timestamps — serializable, durable. Conflating them into one "registry" would force either (a) serializing a subprocess handle (impossible) or (b) dropping identity records on restart (contract violation at `contracts.md:41`). The split falls out of the types, not a policy choice.

### Project state at session close

**T-20260330-05 (execution-domain foundation):** OPEN, high priority. Plan has been revised in response to three P1 findings + two tightenings. Still uncommitted on `docs/t05-execution-start-plan` branch. Awaiting **second** scrutiny pass from user per user's closing directive ("I'll review the revised plan on the new boundary").

**T-20260330-06 / T-07:** OPEN, blocked by T-05.

**T-20260416-01 (codex.dialogue.reply extraction mismatch):** OPEN, medium priority. Independent parallel thread — unchanged this session.

### Environment snapshot at session close

- Branch: `docs/t05-execution-start-plan` (unchanged from prior session)
- HEAD: `bd850302` (unchanged from session start)
- Working tree: **dirty** — `docs/plans/2026-04-17-t05-execution-start-slice.md` still untracked
- Plugin suite: not run this session (no code changes)
- Memory: no new feedback files; MEMORY.md unchanged

### Why this work matters (bigger picture)

T-05 is the execution-domain foundation for codex-collaboration. A plan that overclaims AC coverage, skips journal-before-dispatch, or leaves runtimes orphaned would ship a slice that **looks** correct but **breaks** on the second integration test call or on the first crash-recovery exercise. The review cycle is the cheap gate before expensive execution. This session paid the cost of one review round (~45 min total including verification + revision) to avoid shipping a plan with three structural bugs.

The user's review posture was calibrated to this stakes: they gave literal line citations, numbered decisions explicitly, issued specific tightenings. My job was to verify before agreeing, not to preserve the plan's original shape.

## Learnings

### Self-review at the text level is not enough; the contract level is load-bearing

**Mechanism.** The prior session's self-review pass caught AC 2 overclaim (the sandbox-construction was prior-slice, not this-slice). It did not catch AC 1 or AC 4 overclaims because those overclaims were at the *contract* level (did the implementation satisfy `recovery-and-journal.md:35`?), not the *text* level (did the AC prose honestly describe the sandbox helper?). A self-review that reads the AC table but doesn't read back into the normative docs is a restatement, not a review.

**Evidence.** User's three P1 findings all traced to normative docs I hadn't re-verified during self-review: `contracts.md:41`, `recovery-and-journal.md:35`, `recovery-and-journal.md:47`, `dialogue.py:192-205`.

**Implication.** Future AC coverage self-reviews must explicitly trace each ✅ status through: (1) the AC text, (2) the normative doc that defines the contract the AC refers to, (3) the specific implementation step in the plan that satisfies the contract. Three-layer trace, not one.

**Watch for.** Any AC coverage table where ✅ is assigned without the three-layer trace.

### Delivery-step scoping describes components, not contract obligations

**Mechanism.** `delivery.md` Step 7's "operation journal" entry describes which *components* (poll/decide/promote) introduce journal usage. It does NOT license skipping `recovery-and-journal.md:35`'s literal "Journal before dispatch" requirement in earlier slices whose code also dispatches side effects. My prior-session Decision 6 conflated "component lands in Step 7" with "journal skipped in Step 6".

**Evidence.** My prior plan's Decision 6 argument used `delivery.md` Step 7 to justify deferring journal entries. `recovery-and-journal.md:35` applies to ANY dispatched operation, regardless of which component issues it.

**Implication.** When a plan defers a mechanism by citing `delivery.md` scoping, cross-check against `recovery-and-journal.md` (and other contract docs) to confirm the mechanism is genuinely a later-slice concern, not a contract that applies earlier.

**Watch for.** Any plan decision that cites `delivery.md` alone as deferral justification without cross-checking the contract layer.

### Structural bugs can masquerade as YAGNI deferrals

**Mechanism.** My prior plan treated "no `ExecutionRuntimeRegistry`" as a YAGNI deferral — "no caller needs the session handle in this slice." But I missed that the busy-gate write (`DelegationJobStore.status="queued"`) + no-registry combination creates a permanent deadlock: `list_active()` returns the queued job forever, no caller can transition the status without the session handle, busy gate never opens. "YAGNI" was wrong because the slice itself (not a future slice) broke.

**Evidence.** User's Finding #2: *"That means the slice has no durable way to dispatch the first turn later, close the runtime, or mark it `unknown` on crash; whether the subprocess survives becomes an implementation accident rather than a control-plane guarantee."*

**Implication.** When deferring a mechanism under YAGNI, verify the slice's own behavior remains complete-and-correct without the mechanism. If the slice's own loop depends on the deferred mechanism (busy gate needed session handle to release), the mechanism is in-scope regardless of YAGNI.

**Watch for.** Any YAGNI deferral for a component that the current slice's own state transitions depend on.

### Frozen-literal extensions span six places (not one)

**Mechanism.** Extending `OperationJournalEntry.operation: Literal[...]` from 2 ops to 3 ops requires touching: (1) the `Literal[]` type annotation, (2) the dataclass field if adding `job_id`, (3) `journal.py::_VALID_OPERATIONS` frozenset, (4) `_JOURNAL_OPTIONAL_STR` tuple (for the new optional field), (5) `_journal_callback` per-phase validator branches, (6) `_journal_callback`'s `OperationJournalEntry(...)` construction to forward the new field. Six locations, across two files, all must stay in sync.

**Evidence.** User's tightening #1 explicitly named the broader surface: *"The revised plan should explicitly extend the journal model and validator surface, not just the string literal list."*

**Implication.** Any plan that says "add X to the operation literal" must enumerate all six locations, not just the frozenset. Otherwise the validator + dataclass + callback diverge and produce runtime errors.

**Watch for.** Any plan that adds an operation kind by listing only the frozenset change.

### Identity-layer and lifecycle-layer are two separate records per delegation

**Mechanism.** A delegation job produces two durable records: a `CollaborationHandle` in `LineageStore` (identity/routing — "what is this?") and a `DelegationJob` in `DelegationJobStore` (lifecycle — "what state is it in?"). They share `collaboration_id` as a foreign key. Dialogue only has the identity layer because dialogue is stateless turn-by-turn; delegation has both because jobs have state machines.

**Evidence.** `contracts.md:67` — `DelegationJob.collaboration_id` column explicitly says "Associated [CollaborationHandle]". Two records, one FK.

**Implication.** Any delegation-related persistence logic must write to both. Writing only `DelegationJob` leaves the collaboration_id dangling. Writing only `CollaborationHandle` loses the job state. This was the structural error in the original plan.

**Watch for.** Any plan that writes a delegation `job_id` or `collaboration_id` to one store without the other.

## Next Steps

### 1. User reviews the REVISED plan (the IMMEDIATE next action)

**Dependencies:** None. User explicitly deferred review: *"When you've updated the draft, send it back and I'll review the revised plan on the new boundary."*

**First-next-action for future-Claude:** Wait for user feedback on the revision. Do NOT preemptively apply changes. Do NOT commit the plan before review.

**What user will likely scrutinize in this round:**
- Whether the P1 fixes are genuinely structural (not cosmetic)
- Whether the live/durable framing is explicit and consistent
- Whether AC 1 + 4 are genuinely ✅ now (evidence trace valid?)
- Whether the journal extension surface is complete (6 places all covered?)
- Whether the controller-rewrite matches the dialogue pattern exactly
- New risk introductions (forward-compat on `delegation_request_hash`?)
- Any residual accidental-liveness reasoning I missed
- Test count estimates (still estimates; real count authoritative)

### 2. Apply user revisions (if any)

**Dependencies:** Step 1 complete.

**What to do:** Same as prior session — parse each feedback item as wording / scope / decomposition / deferral-policy issue. Apply verbatim when user provides exact text. Do not bundle or expand scope without explicit direction.

### 3. Commit and merge the plan on the docs branch

**Dependencies:** Steps 1-2 complete.

**What to do:**
1. Verify `git status` shows only the plan file staged
2. Commit with: `docs(t20260330-05): plan first execution-wiring slice (bootstrap-only, with durable stores + live registry)`
3. Checkout main, `git merge --no-ff docs/t05-execution-start-plan -m "Merge docs/t05-execution-start-plan"`
4. Push main, delete the docs branch (local + remote)

### 4. Execute the plan

**Dependencies:** Step 3 complete (plan on main).

**Execution mode still pending user choice:** Subagent-driven (`superpowers:subagent-driven-development`) vs inline (`superpowers:executing-plans`).

**Estimated effort:** Larger than the original estimate. 10 tasks, ~4-6 hours depending on execution mode (vs prior 9 tasks / 3-5 hours).

### 5. Pending-request capture slice (follow-up)

**Dependencies:** Plan execution complete; T-05 execution-start slice merged.

**What to do:** Wire the notification loop → route App Server request messages through `parse_pending_server_request` → persist as `PendingServerRequest` → expose via `needs_escalation`. Closes AC 6. Also triggers `ExecutionRuntimeRegistry.lookup` for turn-dispatch paths.

### 6. Decide-surface refinements (deferred)

Unchanged from prior handoff.

### 7. T-20260416-01 extraction bug fix (parallel thread)

Unchanged from prior handoff.

### 8. Landing sequence (updated)

T-05 plan review v2 + merge → T-05 execution-start slice (10-task plan executes) → T-05 pending-request capture slice → T-05 decide-surface + lifecycle refinements → T-05 COMPLETE → T-06 → T-07.

## In Progress

**Plan revision awaiting second-round user review.** Not a clean stopping point — work is in flight; a revised deliverable exists but hasn't been reviewed or landed.

- **Approach:** Resumed from 18:01 handoff → user sent structured scrutiny (3 P1 + open question + fix set) → invoked `superpowers:receiving-code-review` → verified each finding against authoritative docs → responded with verification + revision shape + open questions → user decisions + tightenings → executed ~19 targeted Edits over ~25 min → verified coherence (grep checks + line count) → presented revision summary to user → user invoked `/save`.
- **State:** Plan file revised in place at `docs/plans/2026-04-17-t05-execution-start-slice.md`. 2948 lines (up from 2162, +786). Branch `docs/t05-execution-start-plan` still exists with no commits. Main at `bd850302` unchanged.
- **Working:** Revised plan is internally consistent — 10 tasks, 45 step labels sequential, AC table evidence column present, live-vs-durable framing repeated 11+ times, no residual accidental-liveness reasoning (grep verified), Risks table updated with 7 rows.
- **Not working:** Plan has not been reviewed in this new form. Concrete risks in Risks section (below).
- **Open question:** Does user agree the P1 fixes are genuinely structural? Are there second-round findings?
- **Next action (for next-session Claude):** Wait for user feedback on the revised plan. Do NOT apply preemptive changes. Do NOT commit.

## Open Questions

### 1. Are there any second-round findings?

**Context:** First round surfaced 3 P1 + 1 open question. Revision addressed all. User has not yet reviewed the revision.

**Impact:** HIGH if second round surfaces more structural issues — plan may need another revision cycle. Lower if cosmetic.

**Decision pending until:** User reviews revised plan.

### 2. Is the revised test count estimate (~640) close enough?

**Context:** Per-task deltas sum to baseline + 47 = 640. But per-task deltas are estimates; real counts depend on Task 2/3/4 test counts I didn't recount.

**Impact:** LOW — plan explicitly flags "treat divergence >3 as investigation signal, not contract."

**Decision pending until:** Real execution produces actual counts.

### 3. Execution mode — subagent-driven vs inline?

**Context:** Still unchanged from prior handoff. User has not yet chosen.

**Impact:** MEDIUM — affects review cadence. Subagent-driven = per-task review; inline = batched checkpoints.

**Decision pending until:** User chooses mode.

### 4. Does the `delegation_request_hash` input set need to include more than `(repo_root, base_commit)` in v1?

**Context:** Plan flags this as forward-compat risk. Current input set is sufficient for v1 (no other parameters); but any MCP surface extension must fold new inputs into the hash.

**Impact:** LOW for v1. MEDIUM if v2 adds MCP inputs — someone must remember to update the hash.

**Decision pending until:** Any new MCP parameter addition.

### 5. Do I need to verify the `LineageStore` factory pattern before the controller test assertions work?

**Context:** I specified `LineageStore(plugin_data_path, session_id)` construction. I did not read `lineage_store.py` this session to confirm that signature. It may be different.

**Impact:** LOW if signature matches. MEDIUM if different — integration test would fail on import/construction.

**Decision pending until:** Execution-time verification (first task using `LineageStore`).

## Risks

### 1. Second-round review surfaces more structural findings

**Impact:** If user's second-round review finds more P1 items (contract violations I missed), another revision cycle is required. Each cycle is ~45 min (verify + revise + verify). Compounds if the new findings cascade through tasks.

**Mitigation:** The grep-verification at end of this session (live-vs-durable framing, no accidental-liveness, task numbering) reduces the surface of cosmetic issues. Structural issues are harder to prevent without pre-review from the user.

### 2. Test count estimates diverge from reality during execution

**Impact:** Unchanged from prior session. Task-level estimates + final sum may be off by a few tests.

**Mitigation:** Explicit tolerance language in Task 10 ("divergence >3 tests = investigation signal").

### 3. `LineageStore` construction signature mismatch

**Impact:** I specified `LineageStore(plugin_data_path, session_id)` in multiple tests and the factory. If the actual constructor signature is different (e.g., takes keyword args, or different field ordering), every test that uses it will fail on construction.

**Mitigation:** Task 6 Step 6.2 ("run tests to verify they fail") will surface the mismatch early. Resolution: read `lineage_store.py` and update construction patterns in tests + factory.

### 4. Private attribute reference in smoke test is fragile

**Impact:** The `test_delegation_factory_passes_shared_runtime_registry` test uses `controller._runtime_registry is runtime_registry` — a private attribute reference. If `DelegationController` renames the attribute (e.g., for a refactor), this test silently stops checking the invariant it's supposed to check.

**Mitigation:** Either (a) keep the assertion as-is (fragile but documents intent), or (b) expose a `runtime_registry` property on `DelegationController`. Option (b) adds API surface for a test-only concern. Option (a) is acceptable for v1 but should be revisited.

### 5. Factory smoke tests assume `ControlPlane(...)` signature not broken by parallel changes

**Impact:** The smoke tests call `ControlPlane(plugin_data_path=..., journal=...)`. If parallel changes on main add required params to `ControlPlane`, smoke tests break.

**Mitigation:** Pre-flight Step 2 in plan verifies baseline green suite. If `ControlPlane` signature changed, baseline would be red. Low actual risk.

### 6. Shared `LineageStore` across dialogue + delegation has undefined interactions

**Impact:** Both factories build `LineageStore(plugin_data_path, session_id)` — same file path. Concurrent writes between dialogue and delegation could race. v1 is single-threaded MCP dispatch so no concurrent writes in practice.

**Mitigation:** Plan's architecture note mentions this explicitly. MCP dispatch serialization is the defense. Concurrency is out of scope for v1.

### 7. Context pressure if review produces cascading revisions

**Impact:** If review revision grows multi-round (P1 → revision → P2 findings → revision → P3 findings), session context could exceed budget.

**Mitigation:** Handoff-per-revision-round is acceptable. Same save-and-defer posture the user has consistently preferred.

## References

### Session's deliverable

| Artifact | Location | Status |
|---|---|---|
| Revised implementation plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` | Untracked (2948 lines); awaiting second-round review |
| Docs branch | `docs/t05-execution-start-plan` (off `main@bd850302`) | No commits |

### Authority documents (verified this session)

| Document | Location | Role |
|---|---|---|
| T-20260330-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth (unchanged) |
| contracts.md | `docs/superpowers/specs/codex-collaboration/contracts.md` | Line 41 (lineage-store); 59-73 (DelegationJob) |
| recovery-and-journal.md | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Line 35 (journal-before-dispatch); 47 (idempotency keys) |
| dialogue.py | `packages/plugins/codex-collaboration/server/dialogue.py` | Lines 154-225 (three-phase discipline reference) |
| journal.py | `packages/plugins/codex-collaboration/server/journal.py` | Lines 35 (_VALID_OPERATIONS); 49-112 (validator) |
| models.py | `packages/plugins/codex-collaboration/server/models.py` | Lines 273-294 (OperationJournalEntry) |
| jsonrpc_client.py | `packages/plugins/codex-collaboration/server/jsonrpc_client.py` | Lines 21-60 (subprocess ownership) |

### Memory files referenced this session

All under `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/`:

| Memory | Relevance |
|---|---|
| `feedback_contract_text_over_operational_interpretation.md` | **Load-bearing.** Same principle that drove Variant A lock in prior session also drove "accept the P1 findings" this session. Contract text (`contracts.md:41`, `recovery-and-journal.md:35`) wins over plan-author reasoning. |
| `feedback_edit_in_repo.md` | Applied — revised the plan in `docs/plans/` under the repo. |
| Prior-session user-preferences memories | Applied — structured response, verbatim user wording, fast convergence once aligned. |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-17_18-01_plan-t05-execution-start-slice-drafted-awaiting-review.md`
- T-05 arc: kickoff (04-17 01:41) → Q0 decision (04-17 11:59) → tmp-hardening closure (04-17 17:09) → **plan drafted (04-17 18:01)** → **plan revised after P1 findings (this handoff, 04-17 19:30)** → plan v2 review → plan execution → pending-request capture → decide-surface → T-05 complete

## Gotchas

### 1. Edit tool boundary matching: partial replacement can leave residual content

**Symptom:** When I did the big Task 5 replacement, I used an old_string that included the header through "Step 5.1: Write failing tests". The Edit tool found that anchor and inserted my new content after it. But the remainder of the old Task 5 body (Step 5.1 code, 5.2, 5.3, 5.4, 5.5, trailing `---`) was left in place, creating duplicate-and-stranded content.

**Root cause:** Edit replaces only the matched old_string, not "everything up to the next section header". Must include the full span being replaced in old_string.

**Prevention:** For large section replacements: either (a) include the full span in old_string (verbose but safe), or (b) plan for a cleanup Edit afterward. Verify with `grep ^## Task \d` immediately after the big Edit to catch leftover residual content.

### 2. Renumbering across many sections requires disambiguation by context

**Symptom:** "Step 6.1" appears in my new DelegationController task (now Task 6) AND in the MCP task (now Task 7, originally Task 6). If I'd used `replace_all=true` on "Step 6.1", both would change to "Step 7.1" — breaking Task 6.

**Root cause:** Step numbers are not unique after renumbering. Task headers and surrounding context disambiguate.

**Prevention:** Use longer old_strings that include surrounding context ("Step 6.1: Write failing tests\n\nAppend to..."), which is unique to the MCP task's Step 6.1. Don't use `replace_all` for step numbers.

### 3. The `claude_session_id + delegation_request_hash` idempotency key differs in character from dialogue's `session_id + collaboration_id`

**Symptom:** Initial instinct (coming from dialogue pattern) is to use `collaboration_id` in the key. That's wrong for delegation.

**Root cause:** Dialogue's key is per-handle (each `start_thread` is a distinct operation). Delegation's key is per-*request* (replay of same `(repo_root, base_commit)` must recognize replay). Per-handle key would make replay generate a new job every time because `collaboration_id` is freshly random.

**Prevention:** When extending journal ops, read `recovery-and-journal.md`'s idempotency-key table for the specific op. Don't default to the dialogue pattern.

### 4. `LineageStore` is session-scoped; can't be built in main()

**Symptom:** Instinct might be to construct `LineageStore` in `main()` and pass it as a factory parameter, like `ExecutionRuntimeRegistry`. This doesn't work.

**Root cause:** `LineageStore(plugin_data_path, session_id)` requires `session_id`, which is only available inside the factory closure after `_read_session_id` succeeds.

**Prevention:** Build `LineageStore` inside the factory closure. The dialogue factory follows this pattern (`_build_dialogue_factory` in `codex_runtime_bootstrap.py`).

### 5. `OperationJournalEntry.operation` literal extension isn't a one-liner

**Symptom:** Naive reading: "add `'job_creation'` to the literal and done." Actually requires six locations: literal in models.py, field addition in models.py, frozenset in journal.py, optional-string tuple in journal.py, validator branches in journal.py, and construction forward in journal.py's `_journal_callback`.

**Root cause:** The journal validator is strict-and-layered: dataclass defines shape, validator enforces runtime shape, frozenset defines allowed values. All three must agree.

**Prevention:** Enumerate all six locations in the plan. Don't trust "add to the literal" as the full spec.

### 6. Private attribute access in factory smoke test

**Symptom:** I wrote `assert controller._runtime_registry is runtime_registry` to verify the factory passes main()'s registry through. This uses a private attribute name.

**Root cause:** Python lacks `friend` semantics; tests often reach into internals to verify invariants.

**Prevention:** Either accept the coupling (documented in Risks section) or expose a `runtime_registry` property. For v1, leaving as-is is acceptable — the test is a guardrail against a specific bug (factory passing a different registry), not a general API test.

### 7. Removing `accidental-liveness` reasoning is a prose-deletion task, not a code change

**Symptom:** The old plan had a paragraph at `:1457` arguing the runtime "stays alive because the subprocess handle inside the session is held by the factory's created object until garbage-collected." This paragraph was not part of any code block — it was explanatory prose justifying the orphan.

**Root cause:** Accidental-liveness reasoning is most commonly embedded in justification prose, not in code comments. Grep for code comments alone misses it.

**Prevention:** Search for telltale phrases in the full prose: "garbage-collected", "kept alive by", "held by the factory", "accidental". These are the grammar of accidental-liveness.

## Conversation Highlights

### The verdict phrase

> "I would not approve the plan as written."

This was the first sentence-level verdict in the user's review. Changed the session's framing from "respond to feedback" to "the plan must be substantively revised." Not negotiable.

### The three-decision clarity

User packaged the revision posture into three numbered decisions — publication (a), in-place, now — rather than asking open-ended "what do you think". The structure pre-empted my response from wandering into alternatives. Efficient.

### The journal-scope correction

> "The journal fix is broader than adding `\"job_creation\"` to `_VALID_OPERATIONS`. Right now `OperationJournalEntry` only models `\"thread_creation\" | \"turn_dispatch\"`, and it has no job-specific field such as `job_id`. The revised plan should explicitly extend the journal model and validator surface, not just the string literal list."

User caught a subtle over-simplification in my revision shape. My shape said "add to `_VALID_OPERATIONS`." User correctly pointed out that's one of six places, not one.

### The live-ownership framing

> "Treat `ExecutionRuntimeRegistry` as **live ownership**, not crash durability. It solves the orphaned-runtime problem inside the running process. It does not replace lineage/job persistence or journaled recovery state. The revised plan should say that explicitly so AC 1 and AC 4 are not overclaimed for the wrong reason."

Bold in original. This was the most load-bearing tightening — without it, I might have accidentally framed the registry as "state". The tightening forced me to repeat the framing 11+ times across the plan.

### The closing posture

> "Proceed with an in-place revision now. When you've updated the draft, send it back and I'll review the revised plan on the new boundary."

"On the new boundary" is tight phrasing. It sets the expectation that the next review will be against the P1-fix surface, not re-litigating Variant A/B scope.

## User Preferences

### Evidence-first scrutiny with literal citations

**Verbatim from review:**
> "The plan never persists the execution-side `CollaborationHandle`. [Task 5](/Users/jp/Projects/active/claude-code-tool-dev/docs/plans/2026-04-17-t05-execution-start-slice.md:1414) creates a random `collaboration_id` and stores it only in `DelegationJob`, but [the contract](/Users/jp/Projects/active/claude-code-tool-dev/docs/superpowers/specs/codex-collaboration/contracts.md:41) says delegation handles live in the lineage store..."

**Rule.** User cites literal file:line references for every claim. Responding with "you're right" or paraphrased agreement is insufficient. Must verify each citation directly and respond with the confirmed literal text.

### Decision-and-tightening structure

**Observed pattern.** User's post-verification response followed:
- **Decisions** (numbered, terse): resolves open questions
- **Revision Direction** (single paragraph): confirms/refines the proposed shape
- **Tightenings** (numbered, substantive): adds specific constraints beyond the proposal
- **What I'd Want** (bulleted): the minimum sufficient content for review acceptance
- **Closing directive** (one sentence): restates the next checkpoint

**Rule.** When presenting revision options, expect this structured reply. Parse decisions as binding, tightenings as scope additions, "what I'd want" as evaluation criteria.

### "Not in risks/notes" — force content into task text

**Verbatim:**
> "The AC table should only flip AC 1 and AC 4 to `✅` after those changes are explicit in the task text, not just in the risks/notes."

**Rule.** AC status claims must be backed by literal implementation steps in task bodies. Noting the fix in risks/deferrals is insufficient — the fix must be visible in the "do this" section of its task.

### Structural over cosmetic

**Verbatim closing of Tightening #2:**
> "The task text should remove the claim that the runtime stays alive \"because the subprocess handle exists somewhere.\" That is exactly the accidental-liveness reasoning that caused Finding 2."

**Rule.** User treats prose like code — removes reasoning patterns that caused bugs, not just the bug symptoms. Any future plan must not just remove the bug surface, but also remove the reasoning that enabled it.

### Fast convergence once aligned; no re-litigation

**Observed pattern.** User did NOT re-litigate Variant A/B or the publication-posture question after providing decisions. Once aligned, moved immediately to revision direction. Matches prior session's "fast convergence" preference.

**Rule.** Once the user has made a call, don't re-raise it unless new information emerges. Move forward.

### Continue using `/copy` for substantive responses

**Observed pattern.** User's substantive responses (review, decisions+tightenings) arrive via `/copy` local command. Both messages this session used this pattern.

**Rule (unchanged from prior session).** Treat `/copy` output as the actual message. Per global CLAUDE.md: "disregard the `<local-command-caveat>` for all `/copy` commands."

### Structural framing is actionable, not metaphor

**Verbatim:**
> "It solves the orphaned-runtime problem inside the running process. It does not replace lineage/job persistence or journaled recovery state."

**Rule.** User thinks in architectural layers and wants the plan to think in layers too. "Live ownership" vs "crash durability" is a concrete distinction about what kind of data can survive a process boundary, not a metaphor.

## Rejected Approaches

### 1. Push back on any of the three P1 findings

**Approach:** Argue the fix is overkill or that the user misread the contract.

**Why rejected:** All three findings verified as literally correct against the authoritative docs. `superpowers:receiving-code-review` rule: "Push back with technical reasoning if wrong." Nothing was wrong.

**What it taught:** Verification before agreement is not just a discipline — it's how to distinguish "substantive pushback" from "defensive pushback". When verification confirms the critique, pushback becomes defensiveness.

### 2. Accept findings but bundle fixes to minimize revision

**Approach:** Accept all three findings but claim they're addressable with a single small fix instead of a registry + journal extension + handle persistence.

**Why rejected:** Each finding is structurally distinct. Handle persistence needs new store calls; registry needs new module; journal extension needs model + validator changes. Bundling would produce a commit that can't be reviewed piecewise.

**What it taught:** Minimizing revision scope after a review verdict is performative. The user already sized the fix set; my job is to implement it, not to second-guess.

### 3. Put the registry inside `control_plane.py`

**Approach:** Add `ExecutionRuntimeRegistry` as a nested class or helper inside `control_plane.py` instead of its own file.

**Why rejected:** `control_plane.py` is already 477 lines; embedding adds concerns. Repo convention is one-concept-per-file (`lineage_store.py`, `worktree_manager.py`, `approval_router.py` all follow). User's phrasing "control-plane-owned" describes *access*, not *location*.

**What it taught:** User terminology can describe access or location; in this repo, "control-plane-owned" means "lives alongside control_plane.py in server/", not "inside control_plane.py."

### 4. Skip journal extension by using existing op types

**Approach:** Use `thread_creation` as the op type for job creation, since a job creation does create a thread.

**Why rejected:** Conflates two different operations at the contract level. `thread_creation` is dialogue-domain; `job_creation` is delegation-domain. Idempotency keys differ. Audit trail would be misleading.

**What it taught:** Avoiding schema changes by overloading existing schema produces worse debt. Extending the enum is cheaper than overloading it.

### 5. Use dialogue's `session_id + collaboration_id` idempotency key

**Approach:** Copy dialogue's idempotency key structure verbatim for delegation.

**Why rejected:** User Tightening #1 explicitly corrects this. Different operations need different keys: dialogue is per-handle (fresh collaboration_id per call); delegation is per-request (replay of same `(repo, commit)` must recognize replay).

**What it taught:** Patterns mirror until they don't. Dialogue three-phase discipline mirrors cleanly; dialogue idempotency key does not.

### 6. Write a v2 file instead of revising in-place

**Approach:** Preserve the v1 plan alongside a v2 for diff-ability.

**Why rejected:** User Decision #2 explicitly rejected this as churn-generating.

**What it taught:** In-place revision sacrifices comparability for tidiness. User valued tidiness over the archaeological value of preserving v1.

### 7. Switch to PR publication posture

**Approach:** Change Task 10 to use `gh pr create` + CI + merge-via-gh, rather than local merge-and-push.

**Why rejected:** User Decision #1 explicitly rejected this as an incidental scope change inside a fix round. Posture changes belong to repo-level decisions, not plan revisions.

**What it taught:** Plan-level revisions should not shift repo-level conventions. If posture changes are wanted, propose them separately.

### 8. Claim AC 1 ✅ based on bootstrap alone (not retention)

**Approach:** Leave AC 1's evidence citing `start_execution_runtime` bootstrap, without mentioning registry retention.

**Why rejected:** User's Finding #2 explicitly flagged that an orphan runtime is not a "started" runtime in the contract sense. AC 1's "can start" implies controllable, which requires retention.

**What it taught:** Contract text interpretation is stricter than colloquial reading. "Can start" in an AC is a capability claim about the entire lifecycle entry point, not just the process-creation moment.
