---
date: 2026-04-18
time: "00:52"
created_at: "2026-04-18T04:52:08Z"
session_id: 11c2ea46-ec26-4427-9f33-373ec0a543a5
resumed_from: "docs/handoffs/archive/2026-04-17_23-42_t05-primitives-tasks-1-5-landed-ready-for-task-6.md"
project: claude-code-tool-dev
branch: feature/t05-execution-start
commit: b1451654
title: "T-05 Tasks 6-7 landed — orchestrator (DelegationController) + startup reconciliation (recover_startup) — 4 commits, 652 tests, ready for Task 8 MCP surface"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
---

# T-05 Tasks 6-7 Landed — Orchestrator + Startup Reconciliation on Feature Branch

## Goal

Execute Tasks 6 and 7 of the T-05 execution-start plan (`docs/plans/2026-04-17-t05-execution-start-slice.md`) via `superpowers:subagent-driven-development`. These two tasks constitute the **orchestrator + recovery pair** per the plan's decomposition philosophy ("primitives first, orchestrator next, surface last, integration finally, verify + merge"). Task 6 is the largest single task in the slice (1,189 lines of plan text); Task 7 (385 lines) is smaller but completes the producer/consumer contract that Task 6 opens.

**Bigger picture.** T-05 is the execution-domain foundation for codex-collaboration. This session builds on the prior session's primitives layer (Tasks 1-5, commit chain from `cc387b15` to `e959f1a2`) and closes the orchestrator + recovery loop. The producer side (`DelegationController.start`) emits `CommittedStartFinalizationError` when a post-`dispatched` local write fails; the consumer side (`DelegationController.recover_startup`) reads unresolved `dispatched`-phase journal entries at next session init and closes them into terminal durable state. Without both halves, AC 4 would fail on any crash after journal-dispatched.

**Why this session boundary.** Context hit 98% of the short window after Task 7 cleanup (real 1M budget still had runway, but mid-session on the hardest remaining task — Task 8 at 476 lines — would push into Phase 2). The orchestrator + recovery pair is a clean natural boundary: everything that depends on the controller's internal contract is landed; the remaining tasks (MCP surface, production wiring, E2E, merge) are outward-facing composition work.

**Success criteria (all seven met):**

1. ✅ Worktree at `.claude/worktrees/feature-t05-execution-start` already established by prior session — re-used, not re-created.
2. ✅ Baseline verified at 631 tests on branch HEAD `e959f1a2` (Task 5 cleanup).
3. ✅ Task 6 landed as feat + fix pair (`de8c6391`, `72d4e161`) with full two-stage review.
4. ✅ Task 7 landed as feat + fix pair (`ce07a2c0`, `b1451654`) with full two-stage review.
5. ✅ Plan-aligned cleanup applied via Option A pattern (5-for-7 now sustained across Tasks 1-7).
6. ✅ Plan-divergent amendment candidates preserved (1 new: journal.append_audit_event fsync gap).
7. ✅ Branch left at 652 tests, clean stopping point before Task 8 (MCP tool registration).

## Session Narrative

**Phase 1 — Load prior handoff (~immediate).** `/handoff:load` resolved `2026-04-17_23-42_t05-primitives-tasks-1-5-landed-ready-for-task-6.md` and archived it. Read 749 lines of prior-session context: T-05 primitives complete at `e959f1a2`, 631 tests passing, MEMORY.md already updated, next action "dispatch Task 6 implementer with the verbatim spec + the context baseline correction note (plan's expected count stale by ~7)." Confirmed worktree still at `.claude/worktrees/feature-t05-execution-start`.

**Phase 2 — Task 6 implementer dispatch (~15 min).** Invoked `superpowers:subagent-driven-development`, read implementer + spec-reviewer + code-quality-reviewer prompt templates in parallel with Task 6 plan text (lines 1533-2721). Verified 8 primitive interfaces via grep before dispatch (journal.timestamp/list_unresolved/check_idempotency/plugin_data_path/_operations_path/write_phase/append_audit_event; lineage/job store create/get/update_status; registry register/lookup/active_runtime_ids). Pre-identified one plan-gap: test file imports block omits `OperationJournalEntry` but tests at plan lines 2004 and 2174 use the symbol (type annotation + construction). Dispatched implementer (sonnet) with full Task 6 spec + baseline-correction note (plan says 624, actual 631) + the pre-identified plan-gap + circular-import pre-check instruction.

**Phase 3 — Task 6 implementer return (~4 min).** Returned DONE: commit `de8c6391`, 2 files, 1,139 insertions, 631 → 646 (+15 tests exactly matching plan). Implementer pre-empted the `OperationJournalEntry` import (treated as plan-required per Task 1 precedent). No circular import issue — `runtime.py` only imports from `jsonrpc_client` and `models`, so direct `from .runtime import AppServerRuntimeSession` is safe (no TYPE_CHECKING guard needed). Pyright stale-cache `reportMissingImports` diagnostics emitted but disregarded (handoff Gotcha #3). Verified by running full suite: `646 passed in 4.62s`.

**Phase 4 — Task 6 spec review (~2 min).** Dispatched spec reviewer with the full task spec + "do not trust the implementer" framing. Reviewer independently verified: plan's verbatim test imports block at lines 1567-1576 DOES omit `OperationJournalEntry` while the test code uses it twice; `runtime.py` has zero imports from `delegation_controller.py`; every test + assertion + fixture from plan lines 1547-2205 present in committed file; every controller element from plan lines 2219-2700 present; exactly 2 files touched; commit message matches plan verbatim. Verdict: ✅ **Spec compliant**.

**Phase 5 — Task 6 code-quality review (~5 min).** Dispatched `superpowers:code-reviewer` with BASE_SHA `e959f1a2`, HEAD_SHA `de8c6391`, and review-specific-check list (register-FIRST invariant, error-format convention, TYPE_CHECKING pattern, `# type: ignore` vs pyright, test rigor, pre-existing class-wide concerns). Reviewer returned **APPROVED_WITH_FINDINGS**: 4 Minor plan-aligned findings + 1 pre-existing concern (`journal.append_audit_event` missing fsync — Task 1 primitive scope). Notably self-adjudicated finding #2 (mypy-style `# type: ignore[arg-type]`) — grepped repo, found 9+ test files use same pattern, invoked CLAUDE.md priority rule 4 (local pattern > general convention), flagged for awareness only. This is the kind of mature local-pattern recognition that prior Tasks 4-5 reviewers also exercised.

**Phase 6 — Task 6 cleanup (~5 min).** Presented Option A/B/C to user, pre-categorized. User: "Proceed with Option A". Applied 2 plan-aligned fixes: (a) comment symmetry on the job-store best-effort `pass` block (matching the lineage block's "Best-effort — reconciliation will close it." comment 2 lines up); (b) negative side-effect assertions on 3 busy-path tests (`_wm.calls`, `_cp.calls` assertions verifying the busy gate short-circuits before side effects). Had one Edit collision on the third test (two tests used identical `result.active_job_id == "job-prior"` snippet) — resolved by adding distinguishing prefix context. Commit `72d4e161`: 11 insertions, 2 files. Full suite: 646 passed. Added journal fsync gap to amendment candidates list in commit body.

**Phase 7 — Task 7 implementer dispatch (~3 min).** Read Task 7 spec (lines 2723-3107). Verified `mcp_server.py:119-130` `startup()` current state (`if self._dialogue_controller is not None:` on line 128, no delegation attribute yet). Pre-identified one plan-gap: plan's step 7.4 updates `startup()` body to reference `self._delegation_controller`, but the constructor at lines 110-117 does NOT yet set this attribute (Task 8 is what adds the full parameter plumbing). Without a pre-Task-8 stub (`self._delegation_controller = None` / `self._delegation_factory = None` in `__init__`), `startup()` would AttributeError. Dispatched Task 7 implementer (sonnet) with the full spec + this plan-gap + baseline-correction note (plan says 639, actual 646).

**Phase 8 — Task 7 implementer return (~3 min).** Returned DONE: commit `ce07a2c0`, 3 files, 312 insertions, 3 deletions, 646 → 651 (+5 tests exactly matching plan). Implementer handled the plan-gap stub as directed. `_phase_rank` at module scope (not nested in class). Full suite: `651 passed in 4.50s`.

**Phase 9 — Task 7 spec review (~1 min).** Reviewer independently verified the plan-gap stub necessity (pre-existing `__init__` had no `_delegation_controller` attribute; `startup()` body references it; without stub = AttributeError). All 5 test functions present. `recover_startup()` logic matches plan verbatim. `startup()` docstring matches. Exactly 3 files touched. Verdict: ✅ **Spec compliant**.

**Phase 10 — Task 7 code-quality review (~3 min).** Reviewer returned **APPROVED** with 4 plan-aligned findings. Notably investigated the `"running"` status guard (`job.status in ("queued", "running")`) and confirmed via codebase inspection that `"running"` is a valid `JobStatus` literal even though no code currently transitions `queued → running` — flagged as forward-looking defensive code, not over-anticipation. Also verified the idempotency mechanism by tracing `journal.list_unresolved` → `_terminal_phases` → replay-and-dict() — grouping + phase-rank is defensive redundancy (highest-phase entry wins dict-from-replay anyway), correct belt-and-suspenders.

**Phase 11 — Task 7 cleanup (~3 min).** User: "Proceed with Option A". Applied 3 plan-aligned fixes: (I1) new row-5 coverage test `test_recover_startup_does_not_downgrade_handle_already_unknown` exercising the `handle.status == "active"` guard's negation; (I2) startup() docstring clarification that delegation lazy wiring lands with Task 8; (M1) deleted dead `repo_root = tmp_path / "repo"; repo_root.mkdir()` from `test_recover_startup_noop_on_fresh_session`. Skipped M2 (stubs lack `Any | None` annotation) because Task 8's constructor parameter will naturally type them. Commit `b1451654`: 54 insertions, 4 deletions, 2 files. Full suite: `652 passed in 4.68s`.

**Phase 12 — Handoff save (this document).** Context at 98% of short window; decisive boundary for MCP surface work. No work in flight.

## Decisions

### Decision 1: Single-implementer dispatch for Task 6 (not decomposed)

**Choice:** Dispatched Task 6 as a single implementer call with the full 1,189-line plan spec, rather than decomposing into sub-phases (journal intent → worktree + runtime → register-FIRST → committed-start error paths → `recover_startup()` scaffold).

**Driver.** Prior handoff's Open Question #1 resolution: "Leaning (a) — the plan's own structure is already decomposed; dispatching the full Task 6 text is the literal match. If the implementer hits context pressure, pivot to (b)." The plan's 6.1 → 6.5 step structure IS the decomposition; forcing a second layer of decomposition would risk losing the register-FIRST invariant's end-to-end coherence.

**Alternatives considered:**
- **Decomposed into 5-6 sub-dispatches** — rejected because primitives-level decomposition was already Tasks 1-5; Task 6's code IS the composition that binds them. Decomposing Task 6 further would lose the committed-start error-path coherence (all 5 error modes share the same try/except envelope and `handle_persisted`/`job_persisted` flag machinery).
- **Opus-powered implementer** — not chosen; Task 6 is plan-verbatim transcription + one known plan-gap + one circular-import check. Sonnet is the right fit. Opus would be overkill and slower.

**Implications.** Implementer handled Task 6 in one pass (4 min from dispatch to DONE return). The full-suite green on first attempt confirmed the primitives' contracts were correctly encoded.

**Trade-offs accepted.** Prompt size ~6k tokens for the implementer dispatch. Accepted — well within sonnet's working range for verbatim-transcription tasks.

**Confidence:** High (E2) — validated by the outcome. Zero implementer-rework cycles.

**Reversibility:** N/A — Task 6 is complete.

**Change trigger:** If Task 8 (MCP surface, 476 lines) similarly cleanly decomposes in the plan, reuse the single-implementer pattern. If not, revisit.

### Decision 2: Apply pre-identified plan-gap stubs in dispatch prompt (not as BLOCKED escalation)

**Choice:** When the controller (me) pre-identifies a plan-gap while reading the plan (Task 6's `OperationJournalEntry` import omission; Task 7's `MCPServer.__init__` stub requirement), include the fix directly in the implementer dispatch prompt as "plan-required analogous to Task 1's `schema_violations` precedent." Don't force the implementer to re-discover and BLOCK.

**Driver.** The Task 1 `schema_violations` precedent established "plan-gap" as a distinct category from "scope creep." Pre-identifying saves a round-trip (implementer BLOCKED → controller provides context → implementer retries). User's Option A pattern (sustained for 5 prior tasks) would have applied anyway.

**Alternatives considered:**
- **Let implementer discover and BLOCK** — rejected because the plan-gaps here are mechanical (missing import, missing attribute declaration) and pre-discoverable via grep. The controller's job is precisely this kind of prep work.
- **Update the plan text itself to add the missing bits** — rejected because plan is merged and 7-round-hardened; post-merge plan edits on the active branch muddy the commit graph.

**Implications.** Both Task 6 and Task 7 landed DONE on first pass (no re-dispatches). Plan deviations documented in commit bodies + implementer reports — discoverable via `git log`.

**Trade-offs accepted.** Controller spends ~5 extra minutes per task reading plan text + checking primitives. Accepted — prevents mid-task blocker cycles.

**Confidence:** High (E2) — validated across Tasks 6 and 7. Implementer reports confirmed both pre-identifications were exactly what they needed.

**Reversibility:** High — revert to "let implementer discover" pattern if pre-identification ever misses a gap.

**Change trigger:** If pre-identified gap turns out to be wrong, re-dispatch with correction.

### Decision 3: Reject Option B on Task 7 docstring — let Task 8 type the stubs naturally

**Choice:** When reviewer flagged M2 (stubs `_delegation_controller = None` / `_delegation_factory = None` lack `Any | None` type annotation), deferred to Task 8's natural constructor-parameter annotation rather than speculatively annotating now.

**Driver.** User's Task 4 guidance: "If [Task N's cleanup] starts wrapping [pre-existing patterns] while [other methods] keep the older pattern, you create intra-class asymmetry under the banner of Task N cleanup." Task 8 will add `delegation_controller: Any | None = None` and `delegation_factory: Callable[[], Any] | None = None` parameters; pyright will naturally infer the attribute types at that point. Adding speculative annotations now would smuggle Task 8 work into Task 7 cleanup.

**Alternatives considered:**
- **Annotate now** — rejected for the reason above. Would also create a class-wide asymmetry if Task 8's `Any | None` ends up slightly different from a speculative `Optional[Any]` or similar.
- **Add `# type: ignore` comment** — rejected. No pyright error currently exists (attribute is narrowed to `None` type, not `X | None`, but no assignment anywhere conflicts yet).

**Implications.** Task 8 will smoothly add the constructor parameter without running into a pre-existing "narrowed to None" conflict. If pyright does fire on Task 8's assignment, that becomes Task 8's legitimate scope to address.

**Trade-offs accepted.** The stubs are technically over-constrained (narrowed to `None`) during the Task 7 → Task 8 window. Accepted as "interim state" per the plan's intentional split.

**Confidence:** High (E3) — validated by sustained pattern across Tasks 1-7 plus explicit user guidance from Task 4.

**Reversibility:** High — Task 8 adds the annotation.

**Change trigger:** If pyright actually blocks Task 8's parameter addition, revisit as a pre-Task-8 remediation.

### Decision 4: Preserve the journal.append_audit_event fsync gap as an amendment candidate (not fix now)

**Choice:** When Task 6 reviewer surfaced the pre-existing `OperationJournal.append_audit_event` fsync gap (audit events can be lost if a crash happens between `append_audit_event` and `write_phase(completed)`), added it to the plan-divergent amendment candidates list instead of fixing during Task 6 cleanup.

**Driver.** The gap is Task 1 primitive scope (OperationJournal was Task 1's modification), not Task 6 scope. Fixing it during Task 6 cleanup would:
1. Modify a file outside Task 6's declared file list (`journal.py`).
2. Create intra-class asymmetry with other journal methods that WOULD also benefit from audit-fsync review.
3. Re-open a merged/approved primitive.

Sustained Option A pattern (7-for-7 at this point): class-wide concerns belong in class-wide passes, not per-task cleanup.

**Alternatives considered:**
- **Fix in Task 6 cleanup** — rejected per above.
- **File a separate ticket / ADR** — could do, but commit-body tracking + handoff "amendment candidates" table has served Tasks 2-5 well. Keep the same mechanism.

**Implications.** Added to the tracked amendment candidates list (now 8 items: 2 from T2, 2 from T3, 3 from T4, 1 new from T6). Discoverable via `git log --grep="Deferred as separate amendment decisions"`. Resolution deferred to post-slice merge or when a downstream task hits it.

**Trade-offs accepted.** The gap persists on-branch. Accepted because: (a) it doesn't block downstream tasks; (b) T-05's AC specifications don't require audit-fsync atomicity; (c) fix is class-wide concern that wants its own pass.

**Confidence:** High (E3) — pattern sustained across 7 prior tasks.

**Reversibility:** High — candidate remains fixable.

**Change trigger:** If Task 8 or later actually depends on audit-fsync ordering, promote to explicit plan amendment.

### Decision 5: Stop at Task 7 for handoff save (orchestrator + recovery boundary)

**Choice:** Save handoff after Task 7 cleanup. Task 8 (MCP tool registration, 476 lines) to be fresh session.

**Driver.** Context at 98% of short window — Phase 2 crossover imminent. Task 8 is the next significant surface (476 lines of plan, modifies `mcp_server.py` with new lazy-factory path + tool registration + `_ensure_delegation_controller` + recovery wiring). Mid-session execution on the MCP surface risks cognitive fatigue on integration-heavy code. The orchestrator + recovery pair is a natural completion boundary — producer/consumer contract is closed.

**Alternatives considered:**
- **Push into Task 8** — rejected because Task 8 composes Task 6 (controller) + Task 7 (recovery wiring on eager path) + introduces `_ensure_delegation_controller()` with lazy-path recovery call. Deserves own fresh context budget.
- **Quicksave + continue** — rejected because quicksave is for context-pressure preservation without full synthesis; this is a clean boundary deserving a full handoff.

**Implications.** Next session will load this handoff, read Task 8 in full (plan lines 3109-3585), dispatch implementer. The stubs added in Task 7's `__init__` will be naturally typed when Task 8 adds the constructor parameter.

**Trade-offs accepted.** +1 handoff save/load cycle (~5 min overhead). Accepted — small price for Task 8 getting a fresh budget.

**Confidence:** High (E1) — boundary matches plan's own decomposition ("surface last").

**Reversibility:** High.

**Change trigger:** N/A.

### Decision 6: Kept `_FakeControlPlane` / `_FakeWorktreeManager` real stores pattern (per plan)

**Choice:** Task 6's `_build_controller` test fixture uses real `DelegationJobStore`, `LineageStore`, `OperationJournal`, `ExecutionRuntimeRegistry` — not mocks. Verified and accepted as-is; no reviewer or user pushback on this choice.

**Driver.** Plan's explicit note at line 2703: "The `_build_controller` test fixture uses real stores (not fakes), so the committed-start-failure tests exercise the actual `update_status` path." Reviewer affirmed: "Real stores in failure tests: `_build_controller` uses real stores, not mocks. The committed-start-failure tests therefore exercise the actual `update_status` path end-to-end, which is exactly what the plan required."

**Alternatives considered:** None — plan decided, reviewer confirmed value.

**Implications.** Tests are somewhat slower (real JSONL writes) but catch real integration bugs. 5 committed-start failure tests landed green, each verifying durable state changes — not mocked state.

**Confidence:** High (E3) — aligned across plan, implementer, reviewer.

**Reversibility:** Low (would require rewriting 5 failure tests).

**Change trigger:** If test suite performance degrades meaningfully (currently 4.68s for 652 tests — fine).

## Changes

### Commits landed on `feature/t05-execution-start` (this session)

| # | SHA | Subject | Lines | Tests |
|---|---|---|---|---|
| 11 | `de8c6391` | feat(t20260330-05): add DelegationController with journal/handle/registry discipline + committed-start failure semantics | +1,139 (2 files) | 631 → 646 (+15) |
| 12 | `72d4e161` | fix(t20260330-05): address task-6 review findings | +11 (2 files) | 646 → 646 (coverage tightening) |
| 13 | `ce07a2c0` | feat(t20260330-05): add delegation startup reconciliation for unresolved job_creation | +312/-3 (3 files) | 646 → 651 (+5) |
| 14 | `b1451654` | fix(t20260330-05): address task-7 review findings | +54/-4 (2 files) | 651 → 652 (+1 row-5) |

**Net session contribution:** 4 commits, +21 new tests (631 → 652), 1 new source file (`delegation_controller.py`), 1 modified source file (`mcp_server.py`), 1 modified test file (`test_delegation_controller.py`).

### Handoff / state files

- Archived at session start: `2026-04-17_23-42_t05-primitives-tasks-1-5-landed-ready-for-task-6.md` → `docs/handoffs/archive/`
- State file created at load: `docs/handoffs/.session-state/handoff-11c2ea46-ec26-4427-9f33-373ec0a543a5` (to be cleaned by this save)
- New handoff (this file): `docs/handoffs/2026-04-18_00-52_t05-tasks-6-7-landed-orchestrator-and-recovery-ready-for-task-8.md`

### Memory files

- MEMORY.md already updated in prior session (T-05 active, Engram deferred); no changes this session.

## Codebase Knowledge

### Files read / written this session

| File | Range | Purpose | Key finding |
|---|---|---|---|
| `docs/handoffs/2026-04-17_23-42_*.md` | full | Prior handoff (resumed) | Tasks 1-5 at `e959f1a2`, 631 baseline, Option A pattern established |
| `docs/plans/2026-04-17-t05-execution-start-slice.md` | 1533-2721 | Task 6 full spec | Plan-gap: test imports missing `OperationJournalEntry` |
| `docs/plans/2026-04-17-t05-execution-start-slice.md` | 2723-3107 | Task 7 full spec | Plan-gap: `MCPServer.__init__` needs pre-Task-8 stub |
| `packages/plugins/codex-collaboration/server/journal.py` | 22, 137-279 | Primitive interface verification | timestamp/append_audit_event/list_unresolved/check_idempotency/plugin_data_path/_operations_path/write_phase all present |
| `packages/plugins/codex-collaboration/server/lineage_store.py` | 137, 141, 159 | Primitive interface verification | create/get/update_status all present |
| `packages/plugins/codex-collaboration/server/delegation_job_store.py` | 35, 50, 60, 65 | Primitive interface verification | create/get/list_active/update_status all present |
| `packages/plugins/codex-collaboration/server/execution_runtime_registry.py` | 39, 79, 95 | Primitive interface verification | register/lookup/active_runtime_ids all present |
| `packages/plugins/codex-collaboration/server/mcp_server.py` | 110-135 | Task 7 integration point + stub addition | startup() at line 119, dialogue guard at 128; stub attributes added at 116-117 |
| `packages/plugins/codex-collaboration/server/delegation_controller.py` | new | Task 6 creation | 481 lines — orchestrator implementation |
| `packages/plugins/codex-collaboration/tests/test_delegation_controller.py` | new → 900+ | Tasks 6+7 tests | 20 tests total after Task 7 cleanup |

### Patterns observed

- **Producer/consumer pair on the committed-start contract**: Task 6's `CommittedStartFinalizationError` path is specifically designed to leave the journal at `dispatched` with best-effort `unknown` state on durable records. Task 7's `recover_startup()` is the *only* path that closes this state. The pair is load-bearing for AC 4 — neither half works alone.
- **Register-FIRST invariant inside committed-start try block**: `runtime_registry.register(...)` is the FIRST write inside the `try:` envelope. This is enforced by write-ordering comments and by the busy gate's registry consultation (which rejects retries after register-but-before-completed failures). The invariant is what makes committed-start failures safe (ownership retained) rather than merely visible (subprocess leaks).
- **Three-source busy gate**: The controller consults `job_store.list_active()` (healthy jobs), `registry.active_runtime_ids()` (committed-start-failed same-session retry), and filtered `journal.list_unresolved()` (cross-session residue pre-reconciliation). Each source covers a distinct retry-window failure mode.
- **Idempotent reconciliation via journal advance**: `recover_startup()` advances every processed key to `completed`. Since `list_unresolved` filters on "latest phase NOT terminal," a second call finds empty list. Idempotency is structural, not algorithmic.
- **Module-level `_phase_rank` helper**: Plan correctly placed ordering helper at module scope — it doesn't need `self`. Matches project convention (e.g., similar `_compute_*` helpers in other modules).
- **Mypy-style `# type: ignore[arg-type]` tolerated by pyright**: Despite project using pyright, mypy-style category specifiers are the established local convention (9+ test files use them). CLAUDE.md priority rule 4 (local pattern > general convention) governs. Reviewers have now self-adjudicated this twice (Tasks 5 and 6).
- **Plan-gap stub additions are a recurring pattern**: Three Tasks (1, 6, 7) now have plan-gap fixes where plan verbatim code references symbols/attributes not declared in the plan's own scope. Precedent established: adjudicate via independent code inspection, document as "plan-required analogous to [prior task's] precedent."

### Architecture: orchestrator + recovery composition

```
DelegationController (Task 6+7)
  │
  ├─ start() [Task 6] ─→ busy-gate (3 sources) → journal intent → worktree → runtime → journal dispatched → [register FIRST → lineage → job → audit → journal completed] in committed-start try/except
  │    │
  │    └─ on post-dispatched failure ─→ best-effort mark unknown → raise CommittedStartFinalizationError
  │
  └─ recover_startup() [Task 7] ─→ list_unresolved filter job_creation → group by idempotency_key via _phase_rank → for each: mark handle/job unknown (guard on "active"/"queued"+"running") → write completed

MCPServer.startup() [Task 7 eager-path wiring]
  │
  ├─ if self._dialogue_controller is not None: recover_startup()
  └─ if self._delegation_controller is not None: recover_startup()  # NEW
         (lazy-path wiring via _ensure_delegation_controller lands in Task 8)
```

### Key locations to remember

| Concept | Location |
|---|---|
| T-05 plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` (4,191 lines, on main `f154c682`) |
| Task 8 spec range | `docs/plans/2026-04-17-t05-execution-start-slice.md:3109-3585` (476 lines) |
| DelegationController.start | `packages/plugins/codex-collaboration/server/delegation_controller.py:156` |
| Committed-start try block | `packages/plugins/codex-collaboration/server/delegation_controller.py:~246-407` |
| CommittedStartFinalizationError | `packages/plugins/codex-collaboration/server/delegation_controller.py:99` |
| DelegationController.recover_startup | `packages/plugins/codex-collaboration/server/delegation_controller.py:484` |
| _phase_rank helper | `packages/plugins/codex-collaboration/server/delegation_controller.py:556` (module scope) |
| MCPServer.startup (eager wiring) | `packages/plugins/codex-collaboration/server/mcp_server.py:121` |
| MCPServer.__init__ (stubs for Task 8) | `packages/plugins/codex-collaboration/server/mcp_server.py:116-117` |
| DialogueController.recover_startup (precedent) | `packages/plugins/codex-collaboration/server/dialogue.py:522` |
| _ensure_dialogue_controller (Task 8 model) | `packages/plugins/codex-collaboration/server/mcp_server.py:132` |

## Context

### Mental model

**Framing:** This session was the **orchestrator/recovery arc** — binding the primitives (Tasks 1-5) into a single controller that implements `codex.delegate.start` with full committed-start failure semantics + idempotent recovery. The producer (start) and consumer (recover_startup) form a closed loop; neither is complete without the other.

**Core insight:** *The hard part of Task 6 was not the happy path but the failure-mode discipline.* The plan specified 5 distinct committed-start failure modes (register / lineage / job / audit / journal-completed) each with precise expectations about which durable state should be marked unknown, whether the registry entry should be retained, and whether the journal should advance. The plan's 7 review rounds closed *design* defects here — the execution-time reviewer closed the *convention/coverage* layer (plan-aligned), mirroring the pattern from Tasks 1-5.

**Mental model:** *Plan-gap pre-identification as controller's job.* Tasks 1, 6, and 7 all had plan-required stub additions that the controller pre-identified during spec-reading and folded into the dispatch prompt. This saves implementer round-trips and keeps implementer reports clean (no BLOCKED cycles). Precedent: Task 1's `schema_violations`, Task 6's `OperationJournalEntry` import, Task 7's `MCPServer.__init__` stubs.

### Project state at session close

**T-20260330-05 (execution-domain foundation):** Plan merged on `main` at `f154c682`. Primitives (Tasks 1-5) at `e959f1a2`; orchestrator (Task 6) at `72d4e161`; recovery (Task 7) at `b1451654`. Ready for Task 8 (MCP tool registration, 476 lines). Chain: plan kickoff → Q0 → tmp-hardening → plan rounds 1-7 → plan merge → primitives Tasks 1-5 → **orchestrator Task 6 (this session)** → **recovery Task 7 (this session)** → MCP surface Task 8 → production wiring Task 9 → E2E Task 10 → verify+merge Task 11.

**Other tickets unchanged:**
- T-20260330-06 / T-07: OPEN, blocked by T-05 execution.
- T-20260416-01 (codex.dialogue.reply extraction mismatch): OPEN, medium priority, independent parallel thread.

### Environment snapshot at session close

- Branch: `feature/t05-execution-start` (at worktree `.claude/worktrees/feature-t05-execution-start`)
- HEAD: `b1451654`
- `main` unchanged at `f154c682`
- Worktree directory: `/Users/jp/Projects/active/claude-code-tool-dev/.claude/worktrees/feature-t05-execution-start`
- Primary working directory: `/Users/jp/Projects/active/claude-code-tool-dev` (main repo root, on `main`)
- Plugin suite: 652 passed in 4.68s as of last run
- Context at session close: ~195k/200k short-window (98%); real 1M budget well under

### Why this work matters (bigger picture)

T-05's orchestrator + recovery arc is the semantic core of the delegation surface. Every downstream operation (turn dispatch, polling, promotion, discard) assumes: (a) a `DelegationJob` can be created durably with committed-start failure semantics; (b) any crash mid-commit is closed at next session init; (c) busy invariants are upheld across the full producer/consumer loop. This session closes all three. The MCP surface (Task 8) and production wiring (Task 9) that follow are composition work — they expose and inject the controller but don't change its semantics.

## Learnings

### Pre-identification of plan-gaps saves implementer round-trips

**Mechanism.** When the controller reads the plan in full before dispatch, mechanical plan-gaps (missing imports, missing attribute declarations, etc.) are pre-discoverable via grep. Including the fix directly in the dispatch prompt ("plan-required analogous to Task 1's `schema_violations` precedent") avoids the BLOCKED → context-provide → retry cycle.

**Evidence.** Task 1 had `schema_violations` plan-gap (caught by implementer, adjudicated post-hoc). Tasks 6 and 7 had comparable plan-gaps (caught by controller, folded into dispatch — no BLOCKED cycle). Implementer reports for Tasks 6 and 7 confirmed both pre-identifications matched exactly what was needed.

**Implication.** For Task 8+, reading the full spec + grep for referenced symbols/attributes/interfaces before dispatch is a ~5-minute controller-side investment that saves ~10-15 minutes of implementer iteration.

**Watch for.** Not every plan-gap is mechanical. Design-level plan-gaps (e.g., conflicting AC, semantic ambiguity) must go through user round-trip, not controller shortcut.

### Reviewer self-adjudicates local-pattern conflicts via grep

**Mechanism.** When a reviewer surfaces a finding that *could* conflict with a general convention (e.g., CLAUDE.md global rules), the reviewer increasingly self-validates by grepping the repo for the actual pattern and invoking CLAUDE.md priority rule 4 (local pattern > general convention). This happened twice this session (Task 6 `# type: ignore[arg-type]`, Task 7 `"running"` status guard) without needing user input.

**Evidence.** Task 6 reviewer: "Reviewer grepped the repo and found 9+ other test files use the same pattern; project priority rule 4 (local pattern > general convention) wins." Task 7 reviewer: "`running` is a valid `JobStatus`. It's in the type literal and in `_ACTIVE_STATUSES`. No no-write path yet touches it in this slice (Task 6 only writes `queued`), but future turn-dispatch slices will transition `queued → running`."

**Implication.** Reviewers are increasingly capable of self-validating "local pattern vs global rule" conflicts. Controller should trust these self-adjudications when pre-categorizing Option A/B/C (don't force them into Option A as "findings requiring action").

**Watch for.** If a self-adjudication is wrong (rare), user can still override during Option selection. Pattern of silent over-correction would erode value — monitor.

### Pyright stale-cache `reportMissingImports` on newly-created modules is predictable noise

**Mechanism.** Pyright's in-process cache doesn't immediately re-read new files. Whenever a new module (`delegation_controller.py`) is created, test files importing it show `reportMissingImports` diagnostics for several minutes. Runtime passes (`pytest`) are the source of truth.

**Evidence.** Handoff Gotcha #3 documented this pattern. This session confirmed across two new-file commits (Task 6 `delegation_controller.py`, Task 7 `recover_startup` addition). Diagnostic emission was noisy but zero impact on runtime correctness.

**Implication.** Do not treat new-module `reportMissingImports` as actionable. Full-suite test run is the verification gate.

**Watch for.** If pyright cache settles but the diagnostics persist after 10+ minutes, check for actual import errors (circular import, missing `__init__.py`, etc.) — then it's real.

### Same-commit invariant across session boundaries: handoff load + file edit doesn't trigger it

**Mechanism.** User feedback memory "No mid-track doc commits" applies to benchmark tracks. Regular development doesn't have same-commit invariant concerns. The `/handoff:load` mv operation and the worktree's edits both avoid the main branch entirely — all commits on `feature/t05-execution-start`.

**Evidence.** Load archived handoff to `docs/handoffs/archive/` (untracked by design, gitignored). Worktree on `feature/t05-execution-start`. Main branch (`main`) unchanged from `f154c682` for the entire session.

**Implication.** The benchmark-invariant feedback memory applies to its benchmark context; standard development doesn't need this consideration.

**Watch for.** If work ever spans a protected-branch commit (e.g., accidentally editing on main), the branch protection hook will block — GITFLOW_BYPASS isn't needed.

### The `"running"` job status guard is forward-looking defensive code

**Mechanism.** Task 7's `recover_startup()` guards job-status updates on `status in ("queued", "running")`. Task 6 only writes `"queued"` on the happy path. Why include `"running"`? Because `JobStatus` literal includes it, and future turn-dispatch slices will transition `queued → running` before a crash. Including both statuses in the guard means Task 7's recovery works for T-05 AND for future queued/running transitions.

**Evidence.** Task 7 reviewer explicitly investigated: "`running` is a valid `JobStatus`. It's in the type literal and in `_ACTIVE_STATUSES`. The guard `status in ("queued", "running")` is therefore defensively forward-looking and correct."

**Implication.** This is the project's "future-proof over minimal" tenet applied narrowly (one extra literal in a tuple, not a whole extension hook). Appropriate scope.

**Watch for.** When future slices (T-07 turn dispatch) actually do transition `queued → running`, verify the guard still covers that transition without widening.

## Next Steps

### 1. Execute Task 8 — MCP Tool Registration (`codex.delegate.start` surface)

**Dependencies:** Task 6 (DelegationController) and Task 7 (recover_startup + eager wiring) complete. ✓

**What to read first (next-session Claude):**
1. `docs/plans/2026-04-17-t05-execution-start-slice.md:3109-3585` (Task 8, ~476 lines). This is the third-largest task in the slice.
2. `packages/plugins/codex-collaboration/server/mcp_server.py:132-200` — `_ensure_dialogue_controller` existing pattern (Task 8 mirrors this for delegation).
3. `packages/plugins/codex-collaboration/server/dialogue.py` — for the MCP tool surface pattern (tool decorator, error wrapping).

**Approach:** Invoke `superpowers:subagent-driven-development` + dispatch Task 8. Task 8 will:
- Add `delegation_controller` / `delegation_factory` constructor parameters to `MCPServer.__init__` (naturally types the stubs added in Task 7).
- Implement `_ensure_delegation_controller()` mirroring `_ensure_dialogue_controller()` at line 132, including the lazy-path `recover_startup()` BEFORE pinning.
- Register `codex.delegate.start` MCP tool with error-contract wrapper at `mcp_server.py:207-231`.
- Add tests for both eager-path and lazy-path recovery wiring.

**Key invariants Task 8 must preserve:**
- REGISTER-FIRST ordering in controller (unchanged from Task 6).
- `recover_startup()` called exactly once before first tool call, regardless of construction path.
- `JobBusyResponse` serialization to MCP tool response format.
- `CommittedStartFinalizationError` → MCP tool error response format.

**Pre-dispatch plan-gap check:** Before dispatching, grep the plan's verbatim code for references to attributes/methods not yet declared. Likely areas:
- Does Task 8's test file import anything not already imported?
- Does Task 8's tool handler reference any `DelegationJob` fields not yet covered?
- Does the `codex.delegate.start` MCP tool schema reference Pydantic models not yet defined?

**Expected test count:** Plan says "~647 (~639 + 8)". Actual baseline is 652, so expected is **~660** (652 + 8). May drift with reviewer coverage findings.

### 2. Execute Tasks 9-11 after Task 8

Sequentially: production wiring (T9, ~195 lines), E2E integration test (T10, ~310 lines), verification + merge (T11, ~98 lines). Each is smaller than Task 8; could potentially bundle into a single session if context allows.

### 3. Plan-divergent amendment candidates (separate decision post-slice)

| Task | Amendment candidate | Status |
|---|---|---|
| T2 | `update_status` raise-on-missing (instead of silent orphan-append) | Open |
| T2 | Refactor `_replay` to use shared `replay_jsonl` infrastructure | Open |
| T3 | `CalledProcessError.Got:` carries process output instead of input | Open |
| T3 | `TimeoutExpired` shows `worktree_path` (output) not `base_commit` (input) | Open |
| T4 | `initialize()` handshake result discarded | Open |
| T4 | `_compat_checker` / `_runtime_factory` raise paths bypass error contract | Open |
| T4 | `session.close()` during error cleanup can swallow original error | Open |
| **T6** | **`journal.append_audit_event` missing fsync** (new this session) | **Open** |

Discoverable via `git log --grep="Deferred as separate amendment decisions"`. 8 items total. Resolution deferred to post-slice merge or when a downstream task blocks.

### 4. MEMORY.md — no update needed this session

(Already up-to-date from prior session. No new user directives.)

### 5. Independent thread: T-20260416-01 extraction bug

Unchanged from prior handoffs. Independent of T-05 execution.

## In Progress

**Clean stopping point.** Orchestrator + recovery arc complete. No work in flight.

- **Completed:** Tasks 6 + 7 with full two-stage review + Option A cleanup each. 4 commits on `feature/t05-execution-start`. 652 tests passing.
- **Not in flight:** Task 8 execution (deferred to next session per Decision 5). Plan-divergent amendments (deferred per Decision 4).
- **Next action for next-session Claude:** Load this handoff via `/handoff:load`. Read `docs/plans/2026-04-17-t05-execution-start-slice.md:3109-3585` (Task 8 spec in full). Invoke `superpowers:subagent-driven-development`. Pre-identify any plan-gaps via grep. Dispatch Task 8 implementer with the verbatim spec + baseline correction note (plan says 639, actual 652) + any pre-identified plan-gaps.

## Open Questions

### 1. Task 8 dispatch strategy — single implementer or decomposed?

**Context.** Task 8 is 476 lines — third-largest task. Modifies `mcp_server.py` (constructor + lazy-factory + tool registration + error wrappers). Previous single-implementer dispatch worked for Task 6 (1,189 lines). Decomposition may or may not help here.

**Impact:** Medium. Similar tradeoffs as Task 6's open question.

**Decision pending until:** Next session reads Task 8 spec and can assess internal decomposition.

### 2. Will Task 8's constructor parameter naturally type the stubs?

**Context.** Task 7 added `self._delegation_controller = None` and `self._delegation_factory = None` without type annotations. Task 8 should add parameters with `Any | None` and `Callable[[], Any] | None` annotations mirroring the dialogue equivalents. If pyright fires on the narrowed-from-None assignment, that's Task 8's scope.

**Impact:** Low. If pyright does fire, simple annotation fix.

**Decision pending until:** Task 8 execution.

### 3. Test-count baseline recalibration for Task 11

**Context.** Plan's Task 11 verification step says "baseline of 593 + per-task estimates = 655. Divergence >3 tests = investigation signal." Actual cumulative drift is now +8 by end of Task 7. Expected final count may be ~665-670, not 655.

**Impact:** Low. Task 11's check just needs recalibration note.

**Decision pending until:** Task 11 execution.

## Risks

### 1. Task 8 integration surface area

**Impact.** Task 8 modifies the heaviest integration file in the plugin (`mcp_server.py`). It adds new constructor parameters, new lazy-factory path, new MCP tool registration with error wrapping, and wires lazy-path recovery. Any subtle divergence from the dialogue pattern could cause surface-area bugs (registration name collisions, schema mismatches, error-format drift).

**Mitigation.** Plan's verbatim code mirrors `_ensure_dialogue_controller` exactly. Reviewer will cross-check. Plan's 7-round review arc already handled these.

**Action.** Dispatch Task 8 with explicit reference to the dialogue precedent. Pre-grep plan for method/symbol references to catch plan-gaps.

### 2. `JobStatus` literal coverage drift

**Impact.** `"running"` is covered by Task 7's recover guard but no test explicitly exercises a `running → unknown` transition (since no Task 6/7 path writes `"running"`). Future turn-dispatch slice will introduce this; the guard should Just Work, but untested.

**Mitigation.** When T-07 turn dispatch lands, its test coverage should include a recover_startup test where job was in `"running"`.

**Action.** Note for T-07 implementation — not a Task 8 concern.

### 3. Plan-divergent amendment backlog (now 8 items)

**Impact.** The backlog has grown from 7 → 8 with the addition of the journal.append_audit_event fsync gap. If Tasks 8-11 surface another 3-5 amendments, the post-slice cleanup PR will be sizeable. Some items may become blocking if Task 8 hits unexpected behavior.

**Mitigation.** Each amendment candidate is individually small. Bundled post-slice PR is still viable. Commit-body tracking keeps them discoverable.

**Action.** Continue deferring unless a specific item blocks downstream work. At Task 11, reassess whether to resolve before merge or file as follow-up slice.

### 4. Worktree accumulation

**Impact.** Worktree at `.claude/worktrees/feature-t05-execution-start` will remain after slice merge. Same as prior handoff — not blocking, just housekeeping.

**Mitigation.** `.claude/worktrees/` gitignored. Cleanup via `git worktree remove` post-merge.

**Action.** Add cleanup step to Task 11 merge finalization (already tracked in prior handoff).

### 5. Context management on Task 8+9+10 in single session

**Impact.** If next session bundles Task 8 with 9 or 10, context pressure rebuilds quickly (Task 8 is 476 lines of spec, 9 and 10 add ~505 more). Short-window crossover before slice complete.

**Mitigation.** Default to one task per session until slice is closer to merge. Task 11 is small (98 lines) and can bundle with Task 10.

**Action.** Recommend next session do Task 8 alone, then assess.

## References

### Session's deliverable

| Artifact | Location | Status |
|---|---|---|
| Feature branch with orchestrator + recovery | `feature/t05-execution-start` at `b1451654` | 14 commits total, 652 tests passing |
| Worktree | `.claude/worktrees/feature-t05-execution-start` | Active, ready for Task 8 |

### Authority documents

| Document | Location | Role |
|---|---|---|
| T-05 plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` (4,191 lines) | Source of truth for all 11 tasks |
| Recovery + journal spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Referenced by plan |
| T-20260330-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-17_23-42_t05-primitives-tasks-1-5-landed-ready-for-task-6.md`
- T-05 arc: kickoff → Q0 → tmp-hardening → plan draft → plan rounds 1-7 → plan merge → primitives Tasks 1-5 → **orchestrator + recovery Tasks 6-7 (this handoff)** → MCP surface Task 8 → …

## Gotchas

### 1. Plan-verbatim test code can reference symbols not in its own imports block

**Symptom.** Task 6's plan test code uses `OperationJournalEntry` in two tests but omits it from the `from server.models import (...)` block.

**Root cause.** Plan author forgot to update imports when adding the tests.

**Prevention.** Controller grep-check before dispatch. If a plan-verbatim code block uses `X`, grep `X` in the plan's imports. Pre-fold into dispatch prompt.

### 2. Plan-verbatim body changes can reference attributes not yet declared in the target file

**Symptom.** Task 7's plan `startup()` update references `self._delegation_controller` but the constructor at target location didn't have that attribute (Task 8 is what adds it via parameter).

**Root cause.** Plan's task split means Task N's body changes may reference Task N+1's constructor additions. Intentional decomposition but creates interim-state plan-gaps.

**Prevention.** Controller checks target file's current state vs plan's updated state. Where plan references attributes not yet declared, add minimal stub as pre-Task-N fix.

### 3. Edit collisions in test files with near-identical assertions

**Symptom.** Two tests with `result.active_job_id == "job-prior"` snippet triggered "Found 2 matches" on Edit.

**Root cause.** Test fixtures for registry-based busy and journal-based busy paths return identical `JobBusyResponse` shapes → identical assertion blocks.

**Prevention.** When editing in test files with similar-shape test functions, include distinguishing preceding context (e.g., the `journal.write_phase(...)` block vs the `registry.register(...)` block) in the `old_string`.

### 4. `_phase_rank` at module scope, not nested in class

**Symptom.** Plan specifies `_phase_rank` at zero indentation (module scope). If nested as class method by an over-eager implementer, `self` would be needed and all callers would break.

**Root cause.** Ordering helper doesn't need instance state. Module scope is correct.

**Prevention.** Implementer dispatch prompt explicitly calls this out. Reviewer verifies indentation.

### 5. Pyright stale-cache `reportMissingImports` on new modules persists several minutes

**Symptom.** After creating `delegation_controller.py` and test files importing from it, pyright shows `reportMissingImports` for the module and for `pytest` for several minutes.

**Root cause.** Pyright in-process cache doesn't immediately re-read new files.

**Prevention.** Ignore `reportMissingImports` for newly-created modules. Runtime `pytest` is source of truth. If diagnostic persists >10 minutes, check for actual import errors.

### 6. Option A cleanup commits grow test count by +1 consistently

**Symptom.** Every task's cleanup adds exactly ~1 coverage test. Plan's expected baselines drift by cumulative cleanup additions (+8 by end of Task 7).

**Root cause.** Reviewer consistently surfaces one coverage gap worth tightening per task.

**Prevention.** Baseline-correction note in each dispatch prompt. Task 11's verification script will need recalibration from "~655" to "~665-670" by end of slice.

### 7. Plan's expected test-count drift compounds per task

**Symptom.** Plan said Task 6 would produce 639, actual was 646. Plan said Task 7 would produce 644, actual was 652. Plan said Task 11 target is 655.

**Root cause.** Plan's estimates didn't account for Option A cleanup test additions.

**Prevention.** Track actual count per task, carry the +1-to-+2 drift forward in every dispatch prompt.

### 8. Mypy-style `# type: ignore[arg-type]` is the LOCAL convention, not a violation

**Symptom.** Reviewer saw `# type: ignore[arg-type]` (mypy-style error codes) on test:317 and flagged as potentially at odds with project's pyright-based type checker.

**Root cause.** Global CLAUDE.md advises pyright; repo has 9+ test files using mypy-style codes; local pattern wins.

**Prevention.** Reviewers now self-adjudicate this via grep + CLAUDE.md priority rule 4. Don't auto-flag as actionable.

## Conversation Highlights

### The "1M context" carryover

Prior handoff's conversation highlight ("We have a 1 million-token context window, so we are safe to continue") carried over this session. Context at 98% of short window at session close; continued working through because real budget was still under. Save triggered by the "clean decomposition boundary" concern, not the context indicator alone.

### Option A sustained at 7-for-7

User replies this session: "Proceed with Option A" (Task 6), "Proceed with Option A" (Task 7). Seven tasks in a row chose Option A. Pattern is now structurally stable — controller pre-categorizes; user confirms with minimal framing.

### The register-FIRST invariant framing (from plan)

Plan's inline code comments for the `try` block are load-bearing: "ORDER MATTERS: 1. runtime_registry.register goes FIRST so the runtime is controllable in-process from the moment the journal records dispatched..." This is encoded into the codebase now; future readers will see the invariant without needing to cross-reference the plan.

### Reviewer self-adjudication on `"running"` status

Task 7 reviewer went into the codebase to determine: "`running` is a valid `JobStatus`. It's in the type literal and in `_ACTIVE_STATUSES`. No no-write path yet touches it in this slice (Task 6 only writes `queued`), but future turn-dispatch slices will transition `queued → running`. The guard `status in ("queued", "running")` is therefore defensively forward-looking and correct." This is the reviewer doing their own evidence-gathering rather than rubber-stamping or flagging — the value the two-stage review pattern reliably delivers.

## User Preferences

### Option A continues to be the sustained default (7-for-7)

Consistent across all 7 tasks now. Mechanism unchanged from prior handoff: fix plan-aligned items, defer plan-divergent, preserve in commit body.

### Terse confirmation ("Proceed with Option A")

User's replies this session were extremely terse: "Continue with Task 6 dispatch", "Proceed with Option A", "Continue to Task 7 in this session", "Proceed with Option A". No re-explanation needed when the controller pre-categorizes correctly. Pattern: crisp "X" + optional 1-sentence motivation is sufficient.

### Budget awareness — 1M not short-window

Carryover from prior session; no further user clarification needed this session. Controller heeded the 98% short-window indicator only to trigger a clean-boundary save, not as a hard context cap.

### No memory update without directive

MEMORY.md is already up-to-date from prior session. No user directive to update this session; controller didn't proactively update. Pattern: only update on explicit directive OR clear auto-memory moment.

## Rejected Approaches

### 1. Decomposing Task 6 into sub-phases

**Approach.** Split Task 6's 1,189-line spec into 5-6 implementer dispatches (journal intent → worktree + runtime → register-FIRST + durable writes → committed-start error paths → recover_startup scaffold → etc.).

**Why rejected.** Plan's own structure is already decomposed by steps 6.1-6.5. Second-layer decomposition would risk losing the committed-start error-path coherence (all 5 error modes share the same try/except envelope + `handle_persisted`/`job_persisted` flag machinery). Single implementer handled it cleanly in one pass.

**What it taught.** Plan-verbatim dispatch works well when the plan's code is tightly coupled internally. Decomposition value comes from breaking *loose* coupling, not from artificial size limits.

### 2. Speculatively annotating `_delegation_controller` / `_delegation_factory` stubs in Task 7

**Approach.** Add `Any | None` type annotations to the stubs now (rather than waiting for Task 8's constructor parameter).

**Why rejected.** Smuggles Task 8 work into Task 7 cleanup. Creates Option B-style class-wide asymmetry (Task 7 would pre-declare types that Task 8's parameters then "set," which is weird). User's Task 4 framing: "If Task N starts [pattern X] while other code keeps the older pattern, you create intra-class asymmetry under the banner of Task N cleanup."

**What it taught.** The plan-divergence test extends beyond "does it change runtime behavior" — it also covers "does it pre-empt work in a later task?" Both signals point to Option A deferral.

### 3. Fixing the journal.append_audit_event fsync gap in Task 6 cleanup

**Approach.** Add fsync to `OperationJournal.append_audit_event` as part of Task 6's cleanup commit.

**Why rejected.** Gap is in Task 1's primitive scope, not Task 6's. Fixing it would:
1. Modify `journal.py` (not in Task 6's file list).
2. Create intra-class asymmetry with other journal methods.
3. Re-open a merged/approved primitive.

Added to amendment candidates instead.

**What it taught.** Pre-existing gaps surfaced during a task's review don't automatically become that task's scope. The "which file does this belong to?" question + "is it class-wide?" question together determine cleanup-vs-amendment.

### 4. Pushing into Task 8 in this session

**Approach.** Continue past Task 7 to execute Task 8's 476-line spec before saving handoff.

**Why rejected.** (a) Task 8 is integration-heavy (modifies heaviest file in the plugin); (b) context at 98% short-window; (c) orchestrator + recovery pair is a natural boundary — Task 8's work (MCP surface composition) is meaningfully different from Task 7's recovery closure.

**What it taught.** Handoff boundaries at natural decomposition points (producer/consumer pairs, primitive/orchestrator splits) produce cleaner resumption context than purely context-budget-driven boundaries.
