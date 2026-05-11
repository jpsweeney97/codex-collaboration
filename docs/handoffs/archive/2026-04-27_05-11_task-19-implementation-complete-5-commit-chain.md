---
date: 2026-04-27
time: "05:11"
created_at: "2026-04-27T05:11:36Z"
session_id: b46f0bb5-b223-4b86-8057-e65db47ff86c
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-27_00-10_task-19-dispatch-ready-after-8-review-rounds.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: c53a5199
title: "Task 19 implementation complete — 5-commit chain landed"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_finalize_turn_terminal_guard.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - packages/plugins/codex-collaboration/tests/test_handler_branches_integration.py
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-19-convergence-map.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-h-finalizer-consumers-contracts.md
---

# Task 19 implementation complete — 5-commit chain landed

## Goal

**Bigger picture:** Phase H of T-20260423-02 Packet 1 (Deferred-Approval Response). Phase G CLOSED at `844e6f97` with Tasks 17 and 18 landed (`start()` and `decide()` rewrites). Task 19 is the FIRST task of Phase H — rewrites the captured-request branch of `_finalize_turn` for the one-snapshot terminal guard per spec §`_finalize_turn` Captured-Request Terminal Guard (`design.md:1738-1827`).

**Stakes:** The `_finalize_turn` rewrite is the R14 one-snapshot rule focal point — the terminal invariant gate of the entire plan. Legacy kind-based derivation at `:2385-2390` and unconditional D4 write at `:2369-2371` replaced with snapshot-conditional logic. Three new job terminals (`completed`/`unknown`/`canceled`) now route through a 4-row mapping table instead of the legacy `else: final_status = "needs_escalation"` catch-all. Same-commit deliverables included 8 G18.1 + F16.1 skip-decorator removals with concrete bodies, 11 additive tests (L9 + L11), and 2 constant deletions.

**Trigger:** User loaded prior handoff (Task 19 dispatch-ready after 8 review rounds) and directed dispatch of the Task 19 implementer with explicit model policy: "Use Opus (1 million token context window) for each subagent dispatched in this session."

**Project arc context:** Task 19 is first of 4 Phase H tasks (19=finalizer guard, 20=poll projection, 21=discard canceled, 22=contracts). After Task 19 lands, Tasks 20-22 come into scope. This session completed Task 19 end-to-end: dispatch → implementation → dual review → closeout-fix → user independent review → P2 fix → closeout-docs.

## Session Narrative

**Step 1 — Load handoff and orient (HEAD `a7fa2d4a`).** Loaded `2026-04-27_00-10_task-19-dispatch-ready-after-8-review-rounds.md`. Confirmed both convergence map (563 lines, Round 6) and dispatch packet (354 lines, revision 2) committed at `a7fa2d4a`, working tree clean, dispatch-ready. Also found an older handoff from the prior session (`2026-04-26_15-45_task-18-opus-implementer-in-flight-after-sonnet-budget-failure.md`) — not loaded, left in place. Summarized key decisions carried forward: D4 pending-row "MUST" (stricter than spec's "may"), `lineage_store.update_status` as canonical `:1525` injection target, L9 anomalous-pending requires L2-specific substring, authority table split by artifact class.

**Step 2 — Read dispatch packet and dispatch implementer.** Read the full dispatch packet at `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-19-dispatch-packet.md`. The packet is self-contained — mission statement, 6 authority sources with pre-read guard (convergence map binding, spec §1738-1827, §1705-1736, §1663-1701, carry-forward, plan body informative-only), TDD ordering preamble, 8 CRITICAL sections (L3 terminal mapping, L1-L4 ordering, L2 D4 conditional, deny semantics, `:1525` injection, L9 warnings, L11 direct tests, G18.1/F16.1 body specs), bounded-poll + pytest discipline, acceptance checklists (code + tests + closeout-docs), reporting contract (DONE/BLOCKED templates with full repo-relative grep commands), boundaries (13 explicit prohibitions), begin instruction, and post-implementer review chain specification. Dispatched as `task-19-implementer` (opus, general-purpose, worktree isolation).

**Step 3 — Implementer reports DONE at `1f97b333`.** The implementer ran for ~23 minutes (1,374 seconds, 195K tokens, 144 tool uses). Suite: 1040 passed in 249.95s. All locks L1-L11 and watchpoints W1-W12 verified via the reporting contract's grep commands. Census: 1020 (pre-Task-19) + 12 (new L11+L9; dispatch anticipated 11 but L11-T5 parametrize produced 2 sub-cases) + 8 (unskipped G18.1+F16.1) = 1040. Three implementer judgment calls noted: (1) all G18.1 tests required `session.respond = lambda request_id, payload: None` stubbing — `_FakeSession` and `_ConfigurableStubSession` default `respond=None` causes `TypeError` when the worker dispatches; (2) deny audit event assertion updated from `action="approve"` to `action="deny"` matching Task 18's L7a incidental fix which changed the audit action to match the decision verb; (3) suite census difference explained by parametrize sub-case counting.

**Step 4 — Diagnostic triage.** Verified the worktree auto-cleaned and commit landed on the feature branch. New Pyright diagnostics surfaced: `delegation_controller.py:2615` (`PendingRequestKind` → `EscalatableRequestKind` type mismatch in `decide()`) and `delegation_controller.py:888` (`assert_never` unreachable in `start()`). Read both locations — confirmed pre-existing from Tasks 17/18, not introduced by Task 19 (W1/W2 boundary respected). Test file `reportMissingImports` are standard Pyright package resolution issues, also pre-existing.

**Step 5 — Spec compliance review.** Dispatched `task-19-spec-reviewer` (opus, general-purpose). The reviewer read the convergence map, spec sections, and full diff (`git diff a7fa2d4a..1f97b333`). Verified all 12 dispatch-packet-specific points methodically. Result: 0 Critical, 2 Important, 3 Minor.

- **I1 (Important — L8 PARTIAL):** F16.1 side-effect uniqueness assertions incomplete. Tests assert occurrence (`lookup is None`, `closed == True`, `lineage.status == "completed"`) but not *uniqueness*. The convergence map explicitly requires "side-effect uniqueness" as "the binding form" that "catches duplicate finalization." Non-deduped signals (runtime release, session close, lineage update, job transition) lack call-count or equivalent uniqueness proof.
- **I2 (Important — L11 note):** L11-T7b `get_call_count >= 1` trivially satisfied after the derivation read. Docstring describes intended assertion as `>= 2` (derivation + hydration re-read). The primary proof via `final_status == "needs_escalation"` assertion is sound, but the counting proxy assertion adds no discriminating power.
- **M1:** Deny audit event filter changed from `action="approve"` to `action="deny"` — correct for Task 18's fix but undocumented.
- **M2:** `test_decide_deny_emits_terminal_outcome` missing bounded-poll success assertion after poll loop — other poll sites have this guard.
- **M3:** `_CountingPendingRequestStore.__getattr__` delegation style — functional but fragile for future maintenance.

Verification summary: L1-L11 all PASS (L8 PARTIAL), W1-W12 all PASS.

**Step 6 — Code quality review.** Dispatched `task-19-quality-reviewer` (opus, general-purpose). The reviewer read the full diff and all modified test files. Result: 0 Critical, 4 Important, 4 Minor.

- **Quality I1:** T7b count assertion trivially true (same finding as spec I2 — independent corroboration).
- **Quality I2 (new finding):** F16.1 terminal outcome assertions guarded by `if outcomes_path.exists():` — silently passes if no outcome file is created. The G18.1 analogue at `test_delegation_controller.py:2018` correctly uses `assert outcomes_path.exists()`. This was NOT caught by the spec reviewer.
- **Quality I3:** F16.1 triple JSON parsing per outcome line — `json.loads(line)` called 3 times (once in output expression, twice in predicates).
- **Quality I4:** Missing bounded-poll success assertion in deny-emits-terminal-outcome (same as spec M2, upgraded to Important).
- Positive observations: L1 snapshot-read placement clean and well-commented (P1), L3 branching well-organized (P2), L2 warning substrings distinct (P3), `:1525` injection clean (P4), constant cleanup complete (P5), test docstrings informative (P6).

**Step 7 — Consolidated closeout-fix dispatch.** Consolidated 4 required fixes across both reviews: (1) F16.1 `if` → `assert` + side-effect uniqueness counting wrappers, (2) L11-T7b `>= 1` → `== 2`, (3) missing poll assert, (4) triple JSON parsing. Attempted to continue implementer via name `task-19-implementer` — failed with "No agent named 'task-19-implementer' is currently addressable." Agent names expire after the agent completes. Resumed via agent ID `af8456088cfaaea96` from the original dispatch result. Implementer applied all 4 fixes, ran full suite (1040/1040), and committed `4409b23c`.

**Step 8 — Closeout-docs dispatch.** Continued implementer via agent ID for the mandatory third commit. Implementer updated carry-forward (G18.1 CLOSED with commit `1f97b333` and date, F16.1 CLOSED, F16.2 CLOSED as lineage marker), Phase H plan (Task 19 COMPLETE with feat+fix+docs commit chain and stale-anchor disclaimer), convergence map (Round 7 addendum documenting implementation dispatch, 4 closeout fixes, and final suite status). Committed `a38df257`. The 1+1+1 chain complete.

**Step 9 — User independent review.** User conducted their own review (not delegated to an agent). Found no production-code defects — confirmed L1-L4 shape correct: "one derivation snapshot read before D4, D4 only on anomalous pending, terminal `resolved` / `canceled` mapping before kind fall-through, and the Task 17 unknown-kind carve-out preserved. `PendingServerRequest` is frozen and the store uses `replace()`, so the D4 write cannot mutate the frozen pre-D4 snapshot in place." Scope boundary clean: diff limited to `_finalize_turn`, Task 19 tests, and closeout docs; no `poll()`, `discard()`, contracts, `decide()`, or `start()` body expansion. `DelegationEscalation(` count still 2.

One P2 finding: F16.1 side-effect uniqueness counters (added in closeout-fix `4409b23c`) covered `session.close`, `runtime.release`, and `lineage.update_status` but NOT the job-store terminal transition — the 4th non-deduped signal required by L8.2. User's targeted verification: Task 19 focused pytest scope 20 passed in 0.92s, ruff clean, `_TASK_19_FINALIZER_GUARD_REASON` grep 0, skip grep 0, F16.1 pass-body audit 0.

**Step 10 — P2 fix applied directly (not delegated).** Added `job_store.update_status_and_promotion` counting wrapper to both F16.1 tests. First attempt counted ALL `update_status_and_promotion` calls — tests failed with counts of 2 (approve) and 4 (cancel) instead of the expected 1. Root cause: `update_status_and_promotion` is called at multiple lifecycle points in `_execute_live_turn`: `queued → running` at start (`:899`), then terminal transition in `_persist_job_transition` (`:1436`), plus intermediate transitions in the cancel path. Fixed by filtering the counter to the expected terminal status (`"completed"` for approve, `"canceled"` for cancel). Both tests passed. Full codex-collaboration suite: 1040/1040 in 249.83s. Lint clean. Committed `f1fd24ba`.

**Step 11 — Docs sync for P2 fix.** Updated convergence map Round 7 (added P2 fix paragraph about job-store terminal transition counter), carry-forward Task 19 entry (annotated P2 fix `f1fd24ba` alongside closeout-fix entry), and Phase H plan (added `f1fd24ba` to Task 19 commit chain). Committed `c53a5199`. Task 19 implementation-complete.

## Decisions

### Decision: Filter job-store transition counter by terminal status

- **Driver:** `update_status_and_promotion` is called multiple times during the full `_execute_live_turn` lifecycle — `queued → running` at start, then terminal transition in `_finalize_turn`. A blanket counter produces 2 (approve) or 4 (cancel) calls, not the expected 1.
- **Rejected: Count all calls and assert == N.** Couples the test to internal lifecycle transitions that aren't part of the finalizer contract. If an intermediate transition is added or removed, the count changes. The other three counters (close, release, lineage) didn't need filtering because those calls only happen in the non-escalation tail, not during earlier lifecycle phases.
- **Rejected: Don't count job-store transitions at all.** Would leave the 4th non-deduped signal uncounted, violating L8.2's binding side-effect uniqueness requirement. The user's independent review specifically identified this gap.
- **Implication:** Each F16.1 test filters for its specific terminal status: `"completed"` for approve, `"canceled"` for cancel. This means the counter only catches duplicate *terminal* transitions, not accidental intermediate re-runs. This is exactly the duplicate-finalization scenario L8.2 targets.
- **Trade-offs:** Slightly less coverage than counting ALL calls — won't catch a bug that adds an extra intermediate transition. Acceptable because the intermediate transitions are lifecycle management, not the finalizer's responsibility.
- **Confidence:** High (E2) — verified both the failure mode (unfiltered counter gets 2/4) and the fix (filtered counter gets 1/1) against the live code.
- **Reversibility:** High — single predicate change in the counter wrapper.
- **Change trigger:** None — filtering to the terminal status is semantically correct for the duplicate-finalization proof.

### Decision: Use agent ID (not name) for SendMessage continuity

- **Driver:** After the implementer reported DONE, `SendMessage({to: "task-19-implementer"})` returned "No agent named 'task-19-implementer' is currently addressable." Agent names expire when the agent completes its task.
- **Rejected: Spawn a new agent for the closeout-fix.** Would lose the implementer's full conversation context (195K tokens, 144 tool uses). The closeout-fix instructions reference specific line numbers and patterns from the implementer's work — a fresh agent would need to re-explore.
- **Implication:** Always capture the agent ID from the dispatch result (`agentId: af8456088cfaaea96`) for SendMessage continuity across the closeout chain. The agent ID persists beyond name expiration.
- **Trade-offs:** The agent ID is opaque and harder to track than the human-readable name. Acceptable because the dispatch result always includes both.
- **Confidence:** High (E2) — verified name failure and ID success empirically.
- **Reversibility:** N/A — operational pattern, not code.
- **Change trigger:** If Claude Code changes agent lifecycle so names persist beyond completion.

### Decision: Sequential (not parallel) spec + quality reviews

- **Driver:** The dispatch packet specifies "spec reviewer + code-quality reviewer (sequential, NOT parallel)." Each review layer catches a different defect class — the spec reviewer found convergence-map compliance gaps (L8 partial, T7b weak assertion), while the quality reviewer independently corroborated AND found new issues (silent `if` guard, triple parsing).
- **Rejected: Parallel reviews.** Would prevent the quality reviewer from seeing the spec reviewer's findings. In practice, the quality reviewer's prompt included "Context from spec compliance review (already completed)" with the I1/I2/M2 findings, which informed its analysis.
- **Implication:** The three-layer review chain (spec → quality → user) is load-bearing for convergence-map-grade work. No single reviewer caught all findings.
- **Trade-offs:** Sequential reviews take longer (~3 minutes total for both reviews vs ~2 minutes if parallel). Acceptable because the quality improvement justifies the time.
- **Confidence:** High (E2) — empirically validated across Tasks 17, 18, and 19 that sequential reviews catch more.
- **Reversibility:** High — can switch to parallel for simpler tasks.
- **Change trigger:** If reviews consistently produce zero cross-references (i.e., quality reviewer never uses spec reviewer's findings).

## Changes

### Commits landed this session (5)

| # | SHA | Type | Subject |
|---|-----|------|---------|
| 1 | `1f97b333` | feat | `feat(delegate): rewrite _finalize_turn with one-snapshot terminal guard (T-20260423-02 Task 19)` |
| 2 | `4409b23c` | fix | `fix(delegate): address Task 19 closeout review (T-20260423-02 Task 19 closeout)` |
| 3 | `a38df257` | docs | `docs(delegate): record Phase H Task 19 closeout (T-20260423-02)` |
| 4 | `f1fd24ba` | fix | `fix(delegate): add F16.1 job-store terminal transition counter (T-20260423-02 Task 19)` |
| 5 | `c53a5199` | docs | `docs(delegate): record P2 fix f1fd24ba in Task 19 closeout (T-20260423-02)` |

### Files modified

**`delegation_controller.py`** — 84 net lines changed. The `_finalize_turn` captured-request branch (`:2340-2483`) rewritten from legacy kind-based derivation to L1-L4 ordering: snapshot read → D4 conditional write + three-way warning discipline → terminal-status mapping (4-row table) → kind-based fall-through (preserving L11 unknown-kind carve-out). Non-escalation tail (`:2462-2467`) and no-capture branch (`:2469-2483`) byte-identical to pre-rewrite. `DelegationEscalation(` count remains 2 (W7).

**`test_finalize_turn_terminal_guard.py`** — **NEW**, 693 lines. L11 direct-guard tests (T1-T7b: 8 obligations, 12 collected via parametrize on T5 for resolved+canceled). L9 warning-discipline tests (3: tombstone with "tombstone" substring, anomalous-pending with "anomalous" L2-specific substring, parse-failed pending silence). `_CountingPendingRequestStore` proxy at `:123-135` wraps `PendingRequestStore` with `get_call_count` for one-snapshot verification — `__getattr__` delegates all other methods to the underlying store. `_setup_running_job` helper at `:68-120` returns 7-tuple (controller, job_store, lineage_store, journal, runtime_registry, pending_request_store, fake_session) matching the `_build_controller` pattern.

**`test_delegation_controller.py`** — 275 net lines changed. G18.1 body rewrites: `:1525` (`test_start_post_turn_finalization_failure_marks_job_unknown_and_cleans_up`) full rewrite with canonical `lineage_store.update_status` one-shot failure injection; `:1737` (`test_decide_approve_resumes_runtime_and_returns_completed_result`) 5-step approve protocol with bounded-poll; `:1881` renamed to `test_decide_deny_marks_job_completed_and_closes_runtime` with `job.status == "completed"` per deny→decline semantics; `:1927` (`test_decide_deny_emits_terminal_outcome`) deny terminal outcome with `terminal_status == "completed"`. `_TASK_19_FINALIZER_GUARD_REASON` constant deleted at `:45`. Missing bounded-poll success assertion added at `:2008` in closeout-fix.

**`test_delegate_start_integration.py`** — 99 net lines changed. G18.1 body rewrites: `:857` (`test_delegate_decide_approve_end_to_end_through_mcp_dispatch`) MCP E2E approve with bounded-poll 5s/50ms; `:934` (`test_delegate_decide_deny_end_to_end_through_mcp_dispatch`) MCP E2E deny with `job.status == "completed"` (NOT `"failed"`). `_TASK_19_FINALIZER_GUARD_REASON` constant deleted at `:33`.

**`test_handler_branches_integration.py`** — 296 net lines changed. F16.1 body rewrites: `test_happy_path_decide_approve_success` (resolved+completed→completed) and `test_timeout_cancel_dispatch_succeeded_for_file_change` (canceled+any→canceled). Both include side-effect uniqueness via 4 counting wrappers: `_counting_close` (session.close), `_counting_release` (runtime.release), `_counting_lineage_update` (lineage.update_status), `_counting_job_transition` (job_store.update_status_and_promotion filtered to terminal status). `if outcomes_path.exists():` changed to `assert outcomes_path.exists()` in closeout-fix. JSON pre-parsing applied in closeout-fix.

**`carry-forward.md`** — G18.1 CLOSED (all 6 tests unskipped in `1f97b333`), F16.1 CLOSED (both tests unskipped with concrete bodies), F16.2 CLOSED (lineage marker — G18.1 landed). TT.1/RT.1 UNCHANGED. P2 fix `f1fd24ba` recorded.

**`task-19-convergence-map.md`** — Round 7 addendum: implementation dispatch at `1f97b333`, 4 closeout fixes in `4409b23c`, P2 fix `f1fd24ba`, final suite 1040/0/0.

**`phase-h-finalizer-consumers-contracts.md`** — Task 19 status: COMPLETE with full commit chain (feat + fix + P2 fix + docs).

## Codebase Knowledge

### `_finalize_turn` post-Task-19 structure (`delegation_controller.py:2340-2483`)

The captured-request branch now follows L1-L4 ordering:

| Step | Line range | Behavior | Pre-Task-19 |
|------|-----------|----------|-------------|
| Step 1: D6 diagnostic | `:2360-2367` | `_verify_post_turn_signals` iff `not captured_request_parse_failed` | Unchanged |
| Step 2: Snapshot read (L1) | `:2369-2374` | `request_snapshot = self._pending_request_store.get(rid)` — single read, before any conditional | **NEW** — was no snapshot read |
| Step 3: D4 conditional (L2) | `:2376-2401` | Tombstone warning (`None`), anomalous-pending warning + D4 write (`pending`), skip for terminal (`resolved`/`canceled`) | **REPLACED** — was unconditional `update_status(rid, "resolved")` at `:2369-2371` |
| Step 4: Terminal mapping (L3) | `:2403-2417` | 4-row table: resolved+completed→completed, resolved+interrupted/failed→unknown, canceled+any→canceled, else fall-through | **REPLACED** — was kind-based derivation at `:2385-2390` |
| Step 5: Kind-based fall-through (L4) | `:2419-2427` | `interrupted_by_unknown → unknown` (FIRST per W5), cancel-capable → needs_escalation, completed → completed, else → needs_escalation | Preserved from Task 17's L11 carve-out |
| Step 6: Persist | `:2430` | `_persist_job_transition(job_id, final_status)` | Unchanged |
| Step 7: Tails | `:2432-2467` | Escalation tail (needs_escalation) or non-escalation tail (completed/unknown/canceled) — both byte-identical (W3/W6) | Unchanged |

### D6 warning contamination mechanism (`_verify_post_turn_signals` at `:3022-3031`)

D6 emits `"D6 signal missing: serverRequest/resolved not seen..."` and `"D6 signal missing: item/completed not seen..."` warnings for parseable paths BEFORE the snapshot read. This is why L9 anomalous-pending test uses `"anomalous"` as L2-specific substring — D6 produces `"D6 signal missing:"` which cannot match `"anomalous"`. The L11-T6 test also targets `"anomalous"` but additionally supplies D6-satisfying notifications (`serverRequest/resolved` and `item/completed`) at test lines 386-388 to prevent D6 warnings entirely.

### `_emit_terminal_outcome_if_needed` is best-effort (`:1403-1433`)

`try/except Exception` at `:1426` swallows all failures into `logger.warning`. Docstring at `:1404` explicitly says "Best-effort." Exceptions never escape to `_finalize_turn`'s caller. Cleanup wrapper at `:1352` only fires on exceptions that escape `_finalize_turn`. This is why `_emit_terminal_outcome_if_needed` is explicitly disqualified as a `:1525` failure-injection target — sabotaging it cannot trigger the cleanup path.

### Non-escalation tail structure (`delegation_controller.py:2462-2467`)

Fires for any `final_status` NOT `"needs_escalation"`. Under Task 19, three new job statuses route here: `"completed"`, `"unknown"`, and `"canceled"`. Sequencing:

1. `lineage_store.update_status(collaboration_id, "completed")` — lineage-handle closure (NOT job-status mirror; L6.1 Precedent A)
2. `runtime_registry.release(runtime_id)` — return runtime to pool
3. `entry.session.close()` — close the App Server session
4. `_emit_terminal_outcome_if_needed(job_id)` — best-effort analytics record

Step 1 (`lineage_store.update_status`) is the canonical `:1525` failure-injection target because it's the first direct call whose failure propagates. Steps 2-4 fire only if step 1 succeeds.

### `update_status_and_promotion` lifecycle calls

`_execute_live_turn` calls `update_status_and_promotion` at multiple lifecycle points:
- `queued → running` at `:899` (start of live turn)
- Terminal transition in `_persist_job_transition` at `:1436` (inside `_finalize_turn`)
- Various intermediate transitions in timeout/cancel paths (cancel path produces 4 total calls)

F16.1 side-effect uniqueness counters filter to the terminal status (`"completed"` / `"canceled"`) to isolate the duplicate-finalization proof from lifecycle transitions. The other three counters (close, release, lineage) don't need filtering because those calls only happen in the non-escalation tail.

### `append_delegation_outcome_once` dedupes by job ID (`journal.py:297`)

The `len(terminal_records) == 1` assertion in F16.1 is necessary but NOT sufficient for duplicate-finalization detection because the journal deduplicates by `(outcome_type, job_id)`. The non-deduped signals (close, release, lineage, job-store transition) are the load-bearing proof per L8.2.

### Test module layout post-Task-19

| Module | Tests | Purpose |
|--------|-------|---------|
| `test_finalize_turn_terminal_guard.py` | 12 (8 L11 + 2 T5 parametrize + 3 L9 - 1 overlap) | Direct-call tests invoking `_finalize_turn` with constructed fixtures |
| `test_delegation_controller.py` | ~800+ | Controller-level tests including 4 rewritten G18.1 bodies |
| `test_delegate_start_integration.py` | ~100+ | E2E start integration including 2 rewritten G18.1 MCP bodies |
| `test_handler_branches_integration.py` | ~40+ | Handler-branch integration including 2 rewritten F16.1 bodies |
| `test_delegate_start_async_integration.py` | 8 | Task 17 async start acceptance tests |
| `test_delegate_decide_async_integration.py` | 18 | Task 18 async decide acceptance tests |

### Key locations post-Task-19

| Anchor | Path |
|--------|------|
| `_finalize_turn` def | `delegation_controller.py:2340` |
| Snapshot read (L1) | `delegation_controller.py:2369-2374` |
| D4 conditional (L2) | `delegation_controller.py:2376-2401` |
| Terminal mapping (L3) | `delegation_controller.py:2403-2417` |
| Kind-based fall-through (L4) | `delegation_controller.py:2419-2427` |
| `_persist_job_transition` | `delegation_controller.py:1435` |
| Non-escalation tail | `delegation_controller.py:2462-2467` |
| Escalation audit emission | `delegation_controller.py:2432-2445` |
| `_emit_terminal_outcome_if_needed` (best-effort) | `delegation_controller.py:1403-1433` |
| Cleanup wrapper | `delegation_controller.py:1352` |
| `DelegationEscalation(` site #1 | `delegation_controller.py:833` |
| `DelegationEscalation(` site #2 | `delegation_controller.py:2454` |
| `JobStatus` definition | `models.py:30-38` |
| D6 `_verify_post_turn_signals` warnings | `delegation_controller.py:3022-3031` |
| `append_delegation_outcome_once` dedup | `journal.py:297` |
| `pending_request_store.get` API | `pending_request_store.py:40` |

## Context

### Spec sections governing Task 19

| Spec section | Lines | Key content |
|---|---|---|
| `_finalize_turn` Captured-Request Terminal Guard | `design.md:1738-1827` | One-snapshot invariant (`:1747-1756`), 4-row terminal mapping (`:1762-1767`), D4 suppression (`:1782-1788`), 9-path table (`:1792-1803`), anomalous-pending warning (`:1774`) |
| Unknown-kind contract | `design.md:1705-1736` | `interrupted_by_unknown → "unknown"` routing at `:1725-1727` — preserved as L4 Step 5a |
| Response payload mapping | `design.md:1663-1701` | Deny→decline semantics at `:1677, :1684, :1686`: deny does NOT abort the turn; `final_status` is `completed` not `failed` |

### Spec's 9-path table — which paths exercise the terminal guard

Only 2 of the spec's 9 worker paths actually exercise the L3 terminal-guard mapping. This is why F16.1 has exactly 2 tests:

| Path | Reaches `_finalize_turn`? | Guard outcome |
|---|---|---|
| Decide-success (any kind) | Yes | `resolved + completed → completed` (F16.1 test 1) |
| Timeout-cancel-dispatch-succeeded | Yes | `canceled + any → canceled` (F16.1 test 2) |
| Timeout-interrupt-succeeded | No — sentinel bypass | N/A |
| Timeout-interrupt-failed | No — sentinel bypass | N/A |
| Timeout-cancel-dispatch-failed | No — sentinel bypass | N/A |
| Dispatch-failed | No — sentinel bypass | N/A |
| Internal-abort | No — sentinel bypass | N/A |
| Unknown-kind parse failure | Yes (parse_failed=True) | Snapshot pending; L11 carve-out → `unknown` |
| No capture (analytical turn) | Yes (no-capture branch) | L5 unchanged |

The sentinel-bypass paths (rows 3-7) exit `_execute_live_turn` via `_WorkerTerminalBranchSignal` raise sites before `_finalize_turn` runs. The L11 direct-call tests cover the combinations unreachable via public paths (e.g., `resolved+failed → unknown`).

### Dispatch lifecycle pattern established across Tasks 17-19

The full dispatch lifecycle for convergence-map-grade tasks:

1. **Convergence map drafting** — adversarial review rounds until "defensible" (6 rounds for Task 19)
2. **Dispatch packet authoring** — self-contained implementer prompt with authority sources, acceptance criteria, reporting contract (2 review rounds for Task 19)
3. **Implementer dispatch** — opus in worktree isolation; reports DONE or BLOCKED per reporting contract
4. **Spec compliance review** — sequential; reads convergence map + spec + diff; reports Critical/Important/Minor
5. **Code quality review** — sequential after spec review; receives spec findings as context; code-quality perspective
6. **Closeout-fix** — consolidated review findings sent to implementer via SendMessage (agent ID, not name)
7. **User independent review** — user conducts their own review after automated chain
8. **P2 fix** — any user-identified gaps fixed directly (not delegated)
9. **Closeout-docs** — carry-forward closures, convergence map addendum, plan status update

### Carry-forward state at session end

| Item | Status | Notes |
|------|--------|-------|
| G18.1 | **CLOSED** | All 6 finalizer-dependent tests unskipped in `1f97b333` |
| F16.1 | **CLOSED** | Both handler-branch tests unskipped with concrete bodies in `1f97b333` |
| F16.2 | **CLOSED** | Lineage marker — closes when G18.1 closes |
| TT.1 | Open | `_FakeControlPlane` Pyright issues — end-of-Packet-1 typing polish |
| RT.1 | Open | `runtime.py` TurnStatus literal narrowing — end-of-Packet-1 typing polish |

### Mental model

**Subagent-driven development with layered adversarial review.** Each layer catches a different defect class:

| Layer | What it catches | Example from this session |
|-------|----------------|--------------------------|
| Implementer self-check | Operational issues (session stubbing, audit assertion staleness) | G18.1 `session.respond` stubbing, deny audit `action` fix |
| Spec compliance review | Convergence-map compliance gaps, weak assertions | L8 partial (uniqueness vs occurrence), T7b trivial count |
| Code quality review | Test robustness, silent-pass traps, code clarity | `if outcomes_path.exists()` silent pass, triple JSON parsing |
| User independent review | Gaps all reviewers missed | Job-store terminal transition counter |

**Production-to-test ratio (~1:15).** 84 lines of production code change drove ~1,200 lines of test changes. This ratio reflects the convergence map's emphasis on proving the spec contract rather than just implementing it.

### Project arc

Phase G (Tasks 17-18: `start()` and `decide()` rewrites) is CLOSED. Phase H is in progress:
- Task 19: `_finalize_turn` terminal guard — **COMPLETE** (this session)
- Task 20: `poll()` projection — NEXT
- Task 21: `discard()` canceled semantics — after Task 20
- Task 22: contracts/docs/API surface — after Task 21

## Learnings

### `update_status_and_promotion` is called at multiple lifecycle points — filter counters to terminal status

**Mechanism:** `_execute_live_turn` calls `update_status_and_promotion` for `queued → running` at start and for the terminal transition in `_persist_job_transition`. The cancel path additionally calls it for intermediate transitions (4 total calls). A blanket counter produces counts > 1 even without duplicate finalization.

**Evidence:** First attempt with unfiltered counter failed: approve got 2, cancel got 4. Filtering to `status == "completed"` / `status == "canceled"` isolates the terminal transition. Verified by running both F16.1 tests.

**Implication:** Any future side-effect uniqueness counter on a method called at multiple lifecycle stages must filter to the specific status being tested. The other three counters (close, release, lineage) didn't need filtering because those calls only happen in the non-escalation tail, not during earlier lifecycle phases.

### Agent name expiration requires agent ID for SendMessage continuity

**Mechanism:** After the implementer reported DONE, the agent name `task-19-implementer` was no longer addressable. The agent ID `af8456088cfaaea96` from the dispatch result continued to work.

**Evidence:** `SendMessage({to: "task-19-implementer", ...})` returned "No agent named 'task-19-implementer' is currently addressable." `SendMessage({to: "af8456088cfaaea96", ...})` succeeded and resumed the agent with full context.

**Implication:** Always capture the agent ID from dispatch results for SendMessage continuity across the closeout chain. The dispatch result format: `agentId: <id> (use SendMessage with to: '<id>' to continue this agent)`.

### Sequential reviews catch defect classes that parallel reviews miss

**Mechanism:** The spec reviewer found L8 partial compliance and T7b weak assertion from the convergence-map perspective. The quality reviewer independently corroborated AND found new issues (silent `if` guard, triple parsing) from the code-quality perspective. The user found the one gap both missed (job-store counter).

**Evidence:** Spec review: 0 Critical + 2 Important + 3 Minor. Quality review: 0 Critical + 4 Important + 4 Minor. User review: 1 P2. Quality reviewer's prompt included spec reviewer's findings as context, which informed the analysis (e.g., confirming I1/I2 independently).

**Implication:** The three-layer review chain (spec → quality → user) is load-bearing for convergence-map-grade work. For simpler tasks, parallel reviews may be acceptable.

### Side-effect uniqueness requires 4 non-deduped signal counters for duplicate-finalization proof

**Mechanism:** The F16.1 tests must prove single-finalization — that `_finalize_turn`'s non-escalation tail fires exactly once. Four non-deduped signals serve as the load-bearing proof: `session.close()`, `runtime_registry.release()`, `lineage_store.update_status()`, and `job_store.update_status_and_promotion()` (filtered to terminal status). The terminal outcome record (`append_delegation_outcome_once`) deduplicates by `(outcome_type, job_id)`, so `len(terminal_records) == 1` passes even under double-finalization.

**Evidence:** The closeout-fix (`4409b23c`) added the first three counters. The user's independent review caught the missing fourth (job-store transition). The P2 fix (`f1fd24ba`) completed the set with terminal-status filtering.

**Implication:** Any future test asserting single-finalization must counter all four non-deduped signals. The counting-wrapper pattern (capture original method, wrap with `nonlocal` counter, assign back with `# type: ignore[assignment]`) is established in both F16.1 tests and should be reused.

**Watch for:** If a fifth non-deduped signal is added to the non-escalation tail, the F16.1 tests need a corresponding counter.

### Worktree auto-cleanup simplifies the dispatch lifecycle

**Mechanism:** The implementer was dispatched with `isolation: "worktree"`. After it completed, the worktree was automatically cleaned up and the commit (`1f97b333`) landed directly on the `feature/delegate-deferred-approval-response` branch in the main working directory.

**Evidence:** `git worktree list` showed no Task-19-related worktree after completion. `git log` showed `1f97b333` on the feature branch.

**Implication:** Worktree isolation for implementers is the correct default — it prevents the implementer from affecting the main working tree during execution, and auto-cleanup means no manual worktree management.

## Next Steps

1. **Begin Task 20: `poll()` projection.** Task 20 now comes into scope. Before dispatching, follow the same pattern as Tasks 18/19: fresh read of live code at HEAD `c53a5199`, convergence map if nontrivial, then compact dispatch packet. Key starting concern: how `poll()` should project terminal, canceled, unknown, or missing pending-request states after Task 19's finalizer changes.

2. **Task 20 orientation starting points.** Read `DelegationController.poll`, `PollResult` / `DelegationPollResult` models, MCP response shaping in `mcp_server.py`, and spec/carry-forward rows mentioning poll projection. Check for `UnknownKindInEscalationProjection` catch + `signal_internal_abort` per the Phase H plan body. Read `_project_pending_escalation` and `_project_request_to_view` for the current projection helpers.

3. **Keep Tasks 20-22 separated.** Task 20: `poll` projection behavior only. Task 21: `discard` canceled semantics. Task 22: contracts/docs/API surface. User explicitly directed: "Do not let Task 20 sneak in discard or contract edits unless it hits a real blocker that needs explicit adjudication."

4. **Open carry-forward items.** TT.1 (`_FakeControlPlane` Pyright issues) and RT.1 (`runtime.py` TurnStatus literal narrowing) remain open — both end-of-Packet-1 typing polish.

5. **Context-metrics chore branch.** `chore/context-metrics-opus-4-7` at `727898c4` stays local per user directive from prior session. No PR.

## In Progress

**Status:** Clean stopping point. Task 19 implementation-complete with all 5 commits landed. No work in flight.

- **Approach:** Subagent-driven development — opus implementer in worktree isolation + sequential spec/quality reviews + closeout-fix via SendMessage + user independent review + direct P2 fix.
- **State:** All 5 commits on `feature/delegate-deferred-approval-response` at `c53a5199`. Working tree clean. Suite: 1040/1040 passed, 0 skipped, 0 failed.
- **Working:** Everything — Task 19 fully landed with all carry-forward items closed (G18.1, F16.1, F16.2).
- **Not working/incomplete:** Nothing — clean stopping point.
- **Next action:** Task 20 fresh-read orientation from live HEAD in a new session.

## Open Questions

- **L6.1 lineage decision stability.** Adopted Precedent A (lineage stays `"completed"` for all three new terminals: completed, unknown, canceled) with binding test obligation (L11-T2 verifies `lineage.status == "completed"` for `final_status == "unknown"`). Phase H Task 22 (contracts) may revisit. If Task 20 or 21 discovers contradicting spec authority during dispatch, surface BLOCKED.
- **L11-T7b proxy fixture feasibility.** The `_CountingPendingRequestStore` proxy worked for T7b (escalation path: `get_call_count == 2` for derivation + hydration re-read). If future tasks need similar proxies for other stores, consider a generic counting-proxy factory. Currently each proxy is hand-written.

## Risks

- **Task 20 may surface finalizer assumptions in `poll()`.** The `poll()` method now needs to handle all three new terminal states (`completed`/`unknown`/`canceled`). If `poll()` has assumptions about `final_status` values that don't include `canceled` or `unknown`, those will break or produce incorrect projections.
- **`UnknownKindInEscalationProjection` in `poll()`.** The Phase H plan mentions `poll()` needs a catch + `signal_internal_abort` for this exception. If `_project_request_to_view` in `poll()` encounters `kind="unknown"` on a job that's still `needs_escalation` (pre-Task-19 legacy state), it currently raises. Task 20 must handle this.
- **Branch distance from main.** `feature/delegate-deferred-approval-response` is now many commits ahead of main. If main evolves, merge conflicts increase. Not urgent but worth noting.

## References

### Active artifacts

| What | Where |
|------|-------|
| Convergence map (Round 7) | `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-19-convergence-map.md` |
| Dispatch packet | `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-19-dispatch-packet.md` |
| Phase H plan body | `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-h-finalizer-consumers-contracts.md` |
| Carry-forward state | `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` |
| Spec authority | `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` |

### Prior handoffs (chain)

- **Resumed from:** `docs/handoffs/archive/2026-04-27_00-10_task-19-dispatch-ready-after-8-review-rounds.md`
- Earlier: `docs/handoffs/archive/2026-04-26_23-36_task-19-convergence-map-round-4-and-context-metrics-fix.md`
- Earlier: `docs/handoffs/archive/2026-04-26_18-30_phase-g-task-18-closes-1plus1plus1-chain-with-round-7.md`

### Branches

| Branch | Status | Head |
|--------|--------|------|
| `feature/delegate-deferred-approval-response` | Active; Task 19 complete; Task 20 next | `c53a5199` |
| `chore/context-metrics-opus-4-7` | Local only; 1 commit ahead of main; no PR per user directive | `727898c4` |

## Gotchas

- **Agent names expire after completion.** `SendMessage({to: "task-19-implementer"})` fails after the agent completes. Use the agent ID from the dispatch result instead (e.g., `af8456088cfaaea96`).
- **`update_status_and_promotion` is called at multiple lifecycle points.** A blanket counter produces counts > 1 (approve=2, cancel=4) even without duplicate finalization. Filter to the specific terminal status being tested.
- **F16.1 `if outcomes_path.exists()` was a silent-pass trap.** The `if` guard let the test pass when no outcome file was written. Changed to `assert outcomes_path.exists()` in `4409b23c`.
- **L11-T7b `get_call_count >= 1` was trivially true.** Changed to `== 2` (derivation + hydration re-read) in `4409b23c`.
- **`_emit_terminal_outcome_if_needed` is NOT a valid failure-injection target.** Best-effort (`try/except Exception` at `:1426`); exceptions never escape `_finalize_turn`. Canonical target: `lineage_store.update_status` at `:2463`.
- **L9 anomalous-pending: generic `logger.warning` assertion is vacuous.** D6 at `:3022-3031` emits its own warnings before the snapshot read. L2-specific substring (`"anomalous"`) required.
- **`deny → decline` does NOT abort the turn.** Tests must assert `job.status == "completed"`, NOT `"failed"`. The pre-Packet-1 test name at `:1881` encoded defunct semantics — rename pre-authorized.
- **Pre-existing diagnostics not from Task 19.** `delegation_controller.py:2615` (PendingRequestKind in `decide()` — W1) and `:888` (`assert_never` in `start()` — W2) are from Tasks 17/18.
- **`uv run --package codex-collaboration pytest` without path collects other packages.** Use `uv run --package codex-collaboration pytest packages/plugins/codex-collaboration/` to scope to the codex-collaboration suite only.

## Conversation Highlights

**User's dispatch instruction:** "Continue with dispatching the Task 19 implementer. Use Opus (1 million token context window) for each subagent dispatched in this session." — Set the model policy for the entire session's subagent chain.

**User's independent review verdict:** "I did not find a production-code defect in the `_finalize_turn` rewrite. The core L1-L4 shape is right: one derivation snapshot read before D4, D4 only on anomalous pending, terminal `resolved` / `canceled` mapping before kind fall-through, and the Task 17 unknown-kind carve-out preserved. `PendingServerRequest` is frozen and the store uses `replace()`, so the D4 write cannot mutate the frozen pre-D4 snapshot in place." — Confirmed production code is sound.

**User's P2 finding framing:** "I'd treat the finding above as a closeout-test fix, not a reason to distrust the feature commit. It matters because the packet explicitly made non-deduped side-effect uniqueness the binding F16.1 proof." — Clear severity calibration: test gap, not production defect.

**User's action-item sequencing:** Five clear directives: (1) record P2 fix in closeout docs, (2) treat Task 19 as implementation-complete, (3) start Task 20 poll projection with convergence-map orientation, (4) keep Tasks 20-22 separated, (5) save handoff then begin Task 20 fresh-read in next session. User explicitly recommended: "do the tiny Task 19 docs sync first, then save a handoff, then open Task 20 with a fresh convergence-map orientation in the next session."

## User Preferences

- **Opus for all subagents in complex dispatch sessions.** User explicitly specified "Use Opus (1 million token context window) for each subagent dispatched." Per prior memory `feedback_handle_commits.md`: confirmed for complex work.
- **Independent review is load-bearing.** User conducted their own code review after the automated spec+quality chain and found a gap both reviewers missed. The three-layer review (spec → quality → user) is the full pattern for convergence-map-grade work.
- **Clean task boundaries.** User's next-steps explicitly separate Task 20 (poll) from Task 21 (discard) and Task 22 (contracts): "Do not let Task 20 sneak in discard or contract edits unless it hits a real blocker that needs explicit adjudication."
- **Docs sync before moving on.** User recommended recording the P2 fix in closeout docs before saving handoff: "This keeps the Task 19 audit trail clean before Phase H moves on."
- **Handoff before new task.** User's recommended sequence: docs sync → handoff → fresh Task 20 orientation in next session. Preserves session boundaries.
- **Severity calibration on review findings.** User explicitly frames test-proof gaps as "closeout-test fix, not a reason to distrust the feature commit." Production code is the primary trust target; test completeness is secondary.

## Rejected Approaches

### Unfiltered job-store transition counter (rejected by test failure)

- **Tried:** Wrapped `job_store.update_status_and_promotion` with a counter that incremented on every call, then asserted `== 1`.
- **Failed because:** `update_status_and_promotion` is called for non-terminal transitions too (`queued → running` at start, intermediate transitions in the cancel path). Approve path got count 2, cancel path got count 4.
- **Learned:** Side-effect uniqueness counters on methods with multiple lifecycle callsites must filter to the specific status being tested. The other three counters (close, release, lineage) didn't need filtering because those methods are only called from the non-escalation tail.

### Resume implementer by agent name after completion (rejected by runtime)

- **Tried:** `SendMessage({to: "task-19-implementer", ...})` to dispatch the closeout-fix.
- **Failed because:** Agent names expire when the agent completes its task. Error: "No agent named 'task-19-implementer' is currently addressable."
- **Learned:** Always capture the agent ID from the dispatch result for SendMessage continuity. The agent ID persists beyond name expiration.
