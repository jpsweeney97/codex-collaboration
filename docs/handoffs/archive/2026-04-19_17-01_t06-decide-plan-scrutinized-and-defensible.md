---
date: 2026-04-19
time: "17:01"
created_at: "2026-04-19T21:01:12Z"
session_id: 35f3b2f5-ce38-425f-8ad2-12ab4ba86ecf
resumed_from: "docs/handoffs/archive/2026-04-19_16-26_t05-closed-t06-scoped-review-fixes-merged.md"
project: claude-code-tool-dev
branch: main
commit: 271f23aa
title: "T-06 decide opening slice plan — scrutinized twice, verdict defensible"
type: handoff
files:
  - docs/plans/2026-04-19-t06-decide-opening-slice.md
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/journal.py
  - packages/plugins/codex-collaboration/server/consultation_safety.py
  - packages/plugins/codex-collaboration/server/execution_prompt_builder.py
  - docs/superpowers/specs/codex-collaboration/contracts.md
---

# T-06 Decide Opening Slice Plan — Scrutinized Twice, Verdict Defensible

## Goal

Produce and scrutinize an implementation plan for the T-06 opening slice: `codex.delegate.decide` for live same-session escalations. The prior session (loaded at start) had scoped the slice; this session was plan review and hardening only.

**Trigger:** Prior handoff said "Next action for next-session Claude: Write the T-06 opening slice plan per the scope in Context → T-06 Opening Slice Scope." The user wrote the plan between sessions and presented it for scrutiny.

**Stakes:** The plan governs the first consumer of the T-05 escalation substrate. Defects here would bake into the execution domain's approve/deny semantics, journal recovery, and MCP contract. Getting the crash-recovery semantics wrong means unresolvable zombie jobs.

**Success criteria (all met):**
1. Two-pass adversarial scrutiny completed
2. All critical and high findings addressed in revision
3. Final verdict: `Defensible`
4. No code written — this session was plan review only

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. T-05 (execution-domain foundation) is complete and merged at `271f23aa`. This plan is the implementation authority for the opening slice.

## Session Narrative

**Phase 1 — Handoff load and orientation (~5 min).** Loaded the prior handoff (`2026-04-19_16-26_t05-closed-t06-scoped-review-fixes-merged.md`), which documented: T-05 closed via PR #108, two Codex bot review findings fixed, 5-agent comprehensive review triaged, T-06 opening slice scoped. The handoff carried detailed user-defined scope for `codex.delegate.decide`, design locks (plugin-side decision not wire replay, approve reuses live runtime, deny maps to `failed`, same-session only), and recommended packet shape.

**Phase 2 — First scrutiny pass (~30 min).** User invoked `/scrutinize` with a description that the plan was complete and saved at `docs/plans/2026-04-19-t06-decide-opening-slice.md`. Read the full 2087-line plan and verified claims against authority documents: `contracts.md` (audit schema at line 180), `delegation_controller.py` (current `_finalize_turn` at lines 720-816, `recover_startup` at lines 818-898), `models.py` (existing `OperationJournalEntry` Literal at line 297, `DelegationEscalation` at line 345), `mcp_server.py` (current dispatch at lines 330-347), `journal.py` (current `_journal_callback` at lines 50-129), `consultation_safety.py` (existing `_TOOL_POLICY_MAP` at lines 50-54), `execution_prompt_builder.py` (full file, 31 lines), `delegation_job_store.py` (`_ACTIVE_STATUSES` at lines 22-24, `list_active` at lines 60-63), and test fixtures (`_build_controller` at lines 148-208, `_FakeSession` at lines 60-98, helper functions at lines 1124-1181).

Key discoveries during verification:

- No `DELEGATE_START_POLICY` exists in `consultation_safety.py` — `codex.delegate.start` has no scan policy in `_TOOL_POLICY_MAP`. This is a pre-existing gap from T-05 that the plan's new `DELEGATE_DECIDE_POLICY` does not close.
- `_lineage_store.update_status` is called only for `"unknown"` in current code (lines 508 and 860), never for `"completed"` — meaning the plan's handle lifecycle fix is filling a real T-05 gap where terminal jobs leave handles orphaned as `active`.
- The crash investigator perspective was the most productive lens. Walking through `decide()` line by line with "what if the process dies here?" exposed C3 — the plan's original recovery code closed the intent-only journal record but left the associated `needs_escalation` job active with no live runtime, creating a zombie that could never be decided or cleaned up.
- The UUID counter arithmetic was initially alarming (looked like exhaustion) but resolved on careful counting: `start()` with escalation consumes 4 UUIDs, `decide(approve)` consumes 1 for the audit event, and a follow-up re-escalation consumes 1 more — 6 of 8 in the original pool, or 6 of 10 in the revised pool. The real issue was semantic naming, not exhaustion.
- The `_FakeSession._interrupted` flag leaks across turns because `interrupt_turn()` sets it to `True` and nothing resets it. This was invisible in T-05 (single-turn tests only) but would cause the re-escalation test to pass for the wrong reason — the handler processes the new server request, but the interrupted status was already `True` from the first turn.

The scrutiny produced 7 findings across three severity tiers: 1 high (C3 zombie recovery), 4 medium (missing test, fixture leak, type safety, ambiguous insertion points), and 2 low (redundant cleanup, missing documentation).

**Phase 3 — User revision (~20 min).** User revised the plan to address all findings and presented the diff summary. The substantive changes were: `invalid_decision` rejection added, recovery code now demotes `needs_escalation` jobs to `unknown` on startup, `CommittedDecisionFinalizationError` test added, `_FakeSession._interrupted` reset per turn, UUID pool extended with semantic names, `_finalize_turn` insertion points clarified, redundant double-cleanup removed, and `delegate.start` policy gap documented as deferred.

**Phase 4 — Second scrutiny pass (~15 min).** Re-read the full revised plan (2216 lines). Verified each finding's resolution against the revised text. Checked recovery ordering: journal reconciliation (closes records unconditionally) runs before orphaned-job sweep (`running` + `needs_escalation` → `unknown`). Verified no double-demote: `update_status` appends to JSONL, so `list_active()` after first demote excludes already-demoted jobs. Traced the `test_decide_request_user_input_requires_answers` test through the handler to confirm `_next_turn_result` is necessary (without it, `request_user_input` completes normally — no escalation). No new correctness issues found.

## Decisions

### Decision 1: Verdict progression — Minor revision → Defensible

**Choice:** Upgraded the plan verdict from `Minor revision` to `Defensible` after the user addressed all 7 findings.

**Driver:** All critical and high findings resolved; no new issues introduced by revisions. The recovery semantics (the most important fix) are now correct — journal records close unconditionally, then orphaned-job sweep catches both `running` and `needs_escalation`.

**Alternatives considered:**
- **Hold at Minor revision** — would require additional changes. Rejected because every finding was addressed and second-pass review found no new issues.

**Trade-offs accepted:** The `DecisionAction | str` union at line 1184 is stylistically uncommon (a type annotation note, not a defect). Accepted because the runtime guard at line 1187 provides the actual safety regardless of the annotation.

**Confidence:** High (E2) — verified each fix against the live codebase, traced recovery ordering through JSONL semantics, and confirmed no double-demote risk.

**Reversibility:** N/A — this is a review verdict, not a code change.

**Change trigger:** If implementation reveals a flaw not visible at the plan level (e.g., the `_execute_live_turn` extraction creates a regression that tests don't catch).

### Decision 2: Recovery treats intent-only and dispatched uniformly — both close the journal, sweep demotes

**Choice:** The revised recovery code closes all unresolved `approval_resolution` journal entries unconditionally (regardless of phase), then a separate sweep demotes orphaned `running` and `needs_escalation` jobs to `unknown`.

**Driver:** The first scrutiny found that intent-only records were being closed without demoting the associated `needs_escalation` job, creating a zombie that could never be decided. User fixed by making the journal close unconditional and the state demote a separate sweep.

**Alternatives considered:**
- **Per-phase branching in the journal loop** (original plan) — intent-only = close journal + preserve job; dispatched = close journal + mark unknown. Rejected because it left intent-only `needs_escalation` jobs as zombies.
- **Mark everything unknown in the journal loop** — would over-demote intent-only records where the job is still cleanly decidable. Rejected because the sweep already handles this correctly by checking job status.

**Trade-offs accepted:** A `needs_escalation` job with an intent-only journal record is now demoted to `unknown` even though no side effects were committed. This is conservative — the job was technically still decidable if the runtime survived. But in a same-session-only design, if the process restarted, the runtime is gone, so the job is unresolvable anyway.

**Confidence:** High (E2) — traced recovery ordering through `list_active()` JSONL replay semantics, confirmed no double-demote, verified sweep only catches active-status jobs.

**Reversibility:** High — the sweep condition at plan line 1784 (`if job.status in ("running", "needs_escalation")`) can be narrowed back to `"running"` only if cross-session decide is added later.

**Change trigger:** When `codex.delegate.poll` or cross-session runtime reattach lands, the sweep must be re-evaluated — jobs that can be inspected or reattached should not be unconditionally demoted.

## Changes

No code changes this session. The only artifact modified was the plan document.

### `docs/plans/2026-04-19-t06-decide-opening-slice.md` — Revised after scrutiny

**Purpose:** Implementation plan for the T-06 opening slice (`codex.delegate.decide`).

**Revisions applied:**
- Added `invalid_decision` to the pinned contract rejection reasons (plan line 331, 354)
- Added runtime guard for invalid decision values at controller entry (plan line 1187-1196)
- Changed recovery to demote `needs_escalation` jobs on startup (plan lines 1780-1791)
- Added `CommittedDecisionFinalizationError` test (plan lines 1512-1549)
- Added `_FakeSession._interrupted = False` reset per turn (plan line 700)
- Extended UUID pool with semantic names for multi-turn tests (plan lines 717-731)
- Clarified `_finalize_turn` insertion points with exact old→new blocks (plan lines 925-958)
- Removed redundant double-cleanup from `decide()` exception path (plan lines 1363-1367)
- Added risk row for `delegate.start` PreToolUse policy gap (plan line 2200)
- Added callout that Task 3 is the highest-risk mechanical refactor (plan line 638)

## Codebase Knowledge

### Recovery Architecture (Post-Revision Understanding)

Recovery in `recover_startup()` uses a two-pass composable pattern:

```
recover_startup()
│
├─ Pass 1: Journal reconciliation (per-operation)
│   ├─ job_creation entries → mark handle/job unknown if dispatched (existing T-05)
│   └─ approval_resolution entries → close journal unconditionally (new T-06)
│
├─ Pass 2: Orphaned-job sweep (status-based)
│   └─ list_active() → demote running + needs_escalation → unknown (broadened from T-05)
│
└─ Each pass has a single responsibility:
    Pass 1 only writes journal entries
    Pass 2 only writes job/handle status
    Neither invalidates the other's preconditions
```

**Why two passes work without ordering hazards:** `list_active()` replays the JSONL log. After Pass 1 writes journal `completed` entries, `list_active()` doesn't see those (journal and job store are separate JSONL files). If Pass 1's `job_creation` branch already demoted a `running` job to `unknown`, Pass 2's `list_active()` won't return it (status is now terminal). So no double-demote.

### _finalize_turn Terminal Branches

Current code at `delegation_controller.py` has two terminal branches that need handle lifecycle updates:

| Branch | Line | Current code | Plan adds |
|--------|------|-------------|-----------|
| Captured-request, non-escalation | 794-797 | `release + close` | `lineage_store.update_status(collab, "completed")` before release |
| No captured-request, terminal | 807-809 | `release + close` | Same — `lineage_store.update_status(collab, "completed")` before release |

Both branches currently leave the execution handle as `active` after the job completes. The escalation branch (line 766-792) correctly keeps the handle `active` — decide will use it.

### _FakeSession Interrupt Semantics

`_FakeSession.run_execution_turn()` at `test_delegation_controller.py:67-92` iterates `self._server_requests`, dispatches to the handler, then checks `self._interrupted`. The interrupt flag is set by `interrupt_turn()` at line 94. **Before the plan's fix**, `_interrupted` leaked across turns — if the first turn triggered an interrupt, the second turn started pre-interrupted. **After the fix** (reset at top of `run_execution_turn`), each turn has fresh interrupt state.

No existing T-05 tests rely on cross-turn interrupt carryover — all T-05 tests are single-turn flows.

### UUID Consumption Map For Multi-Turn Tests

| Phase | UUIDs consumed | Names (post-revision) |
|-------|---------------|----------------------|
| `start()` with escalation | 4 | `job-1, collab-1, delegate-start-evt-1, escalation-evt-1` |
| `decide(approve)` audit | 1 | `decision-evt-1` |
| Follow-up re-escalation audit | 1 | `re-escalation-evt-1` |
| **Total for start→decide→re-escalate** | **6 of 10** | Leaves `job-2, collab-2, delegate-start-evt-2, escalation-evt-2` |

### Journal Validation Pattern

`_journal_callback` at `journal.py:50-129` enforces per-operation-per-phase conditional requirements. The pattern is: validate required string fields first (lines 53-56), then check operation/phase validity (lines 56-59), then apply conditional rules via `op == X and phase == Y` branches (lines 79-112). The plan extends this with `approval_resolution` branches for `intent` and `dispatched` phases, each requiring `job_id`, `request_id`, and `decision` as strings, with `dispatched` additionally requiring `runtime_id` and `codex_thread_id`.

The `completed` phase is intentionally excluded from conditional validation (comment at lines 72-76): production writers emit `completed` as a minimal resolution marker without all correlation fields. Requiring them would reject every completed record. This applies to all operations including the new `approval_resolution`.

The `_JOURNAL_OPTIONAL_STR` tuple at line 45 governs which fields are accepted but not required at the record level. The plan extends this from `("codex_thread_id", "runtime_id", "job_id")` to include `"request_id"` and `"decision"`.

### MCP Dispatch Pattern

`mcp_server.py` dispatches tool calls via a chain of `if name == "..."` blocks (lines 288-347), each importing specific types for `isinstance` checks on return values. The chain terminates at line 347 with `raise ValueError(f"Unknown tool: {name!r:.100}")`. The plan inserts the `codex.delegate.decide` branch before this terminal `raise`. The dispatch normalizes wire-format `answers` (nested `{"q1": {"answers": ["yes"]}}`) into controller-format tuples (`{"q1": ("yes",)}`), with defensive type checks at each nesting level.

### consultation_safety.py Policy Gap

`_TOOL_POLICY_MAP` at `consultation_safety.py:50-54` currently has policies for `codex.consult`, `codex.dialogue.start`, and `codex.dialogue.reply`. There is no entry for `codex.delegate.start` — the execution-domain start surface has no PreToolUse scan policy. The plan adds `DELEGATE_DECIDE_POLICY` for the new `codex.delegate.decide` tool but explicitly defers the `delegate.start` gap (risk row at plan line 2200).

### Plan Task Architecture

The plan at `docs/plans/2026-04-19-t06-decide-opening-slice.md` (2216 lines post-revision) has 6 tasks in dependency order. Understanding the task structure is essential for implementation — each task builds on the prior:

| Task | Purpose | Key files | Commit message |
|------|---------|-----------|----------------|
| 1 | Pin contract + journal vocabulary | `contracts.md`, `models.py`, `journal.py` | `feat(t20260330-06): pin decide contract and journal vocabulary` |
| 2 | Build resume prompt for approve | `execution_prompt_builder.py` | `feat(t20260330-06): add execution resume prompt builder` |
| 3 | Extract `_execute_live_turn` + fix terminal handle lifecycle | `delegation_controller.py` | `refactor(t20260330-06): share execution turn path and close terminal handles` |
| 4 | Implement `decide()` success paths | `delegation_controller.py` | `feat(t20260330-06): implement same-session decide success paths` |
| 5 | Add rejections, safety policy, recovery | `delegation_controller.py`, `consultation_safety.py` | `feat(t20260330-06): add decide recovery and safety policy` |
| 6 | MCP dispatch + end-to-end integration | `mcp_server.py`, `__init__.py` | `feat(t20260330-06): expose codex.delegate.decide through MCP` |

Tasks 1-2 are independent foundations with no cross-dependencies. Task 3 is the mechanical refactor risk — it must be green before Task 4 begins. Tasks 4 and 5 build on Task 3's extracted helper. Task 6 ties everything together through MCP dispatch and end-to-end tests.

Each task follows strict TDD: write failing tests → run and verify failure → implement → re-run and verify pass → commit. The plan specifies exact test code, production code, and `git add` + `git commit` commands for each step.

### Key Locations (Updated From This Session's Reads)

| Concept | Location |
|---------|----------|
| `_finalize_turn` escalation gate | `delegation_controller.py:766-792` |
| `_finalize_turn` non-escalation terminal | `delegation_controller.py:794-797` |
| `_finalize_turn` no-request terminal | `delegation_controller.py:799-816` |
| `recover_startup` orphaned-running sweep | `delegation_controller.py:885-898` |
| `_phase_rank` helper | `delegation_controller.py:934-936` |
| `_ACTIVE_STATUSES` definition | `delegation_job_store.py:22-24` |
| `list_active()` | `delegation_job_store.py:60-63` |
| `_journal_callback` validation | `journal.py:50-129` |
| `_VALID_OPERATIONS` | `journal.py:35` |
| `_TOOL_POLICY_MAP` | `consultation_safety.py:50-54` |
| `OperationJournalEntry.operation` Literal | `models.py:297` |
| `DelegationEscalation` dataclass | `models.py:345-359` |
| `HandleStatus` Literal | `models.py:15` |
| MCP dispatch fall-through | `mcp_server.py:347` (`raise ValueError`) |
| `_FakeSession.run_execution_turn` | `test_delegation_controller.py:67-92` |
| `_build_controller` UUID pool | `test_delegation_controller.py:174-185` |
| `_command_approval_request` helper | `test_delegation_controller.py:1124-1141` |
| `_request_user_input_request` helper | `test_delegation_controller.py:1144-1161` |

## Context

### Mental Model

This session was a **plan review cycle** — two adversarial passes against a 2000+ line implementation plan. The mental model is scrutiny-as-crash-analysis: at every point in the `decide()` method, ask "what if the process dies here?" and trace the recovery path. The crash investigator perspective uncovered the most important finding (zombie `needs_escalation` jobs). The other perspectives (type system skeptic, state machine auditor) confirmed correctness but didn't find new defects.

The three adversarial perspectives applied in Pass 1 were:

1. **Crash Investigator** — walk the crash timeline through every line of `decide()`. This found C3 (zombie jobs). At the point between journal `intent` and `dispatched`, the process dying leaves a `needs_escalation` job with a closed journal and no live runtime — permanently stuck.
2. **Type System Skeptic** — does the plan maintain type safety across MCP → controller → model boundaries? This found the `decision: str` widening gap — MCP dispatch passes an unvalidated string to a method expecting `DecisionAction`. No runtime guard existed.
3. **State Machine Auditor** — are all state transitions valid? This confirmed correctness: `needs_escalation → running → completed/needs_escalation/failed/unknown` and `needs_escalation → failed` (deny) are all valid per the `HandleStatus` and `JobStatus` Literals.

### Why This Session Matters

The plan is the implementation authority for the first consumer of the T-05 escalation substrate. Once approve/deny semantics are coded, they become the contract that `codex.delegate.poll`, skill UX, and cross-session recovery must respect. Getting the crash semantics wrong at the plan level would have propagated into production code that creates unrecoverable state — exactly what C3 caught.

### Project State

- **T-05:** COMPLETE. Both slices merged to main at `271f23aa`. 698 tests.
- **T-06:** Plan complete, scrutinized, verdict `Defensible`. Implementation not started.
- **Branch:** `main` at `271f23aa`. No feature branch created yet.
- **PR #108:** Merged. Feature branch `feature/t05-pending-request-capture` deleted.

### Scrutiny Findings Summary

| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| C3 | High | Zombie `needs_escalation` post-restart — intent-only recovery closed journal but left job unresolvable | **Fixed** — sweep demotes both `running` and `needs_escalation` |
| R4 | Medium | Missing `CommittedDecisionFinalizationError` test | **Fixed** — test at plan lines 1512-1549 |
| H1 | Medium | `_FakeSession._interrupted` carryover across turns | **Fixed** — reset at top of `run_execution_turn` |
| Type | Medium | No runtime guard for invalid `decision` values | **Fixed** — `invalid_decision` rejection added |
| C2 | Medium | Ambiguous `_finalize_turn` insertion points | **Fixed** — exact old→new blocks at plan lines 925-958 |
| R3 | Low | Double cleanup in `decide()` exception path | **Fixed** — `_execute_live_turn` handles cleanup internally |
| D2 | Low | Missing `delegate.start` policy gap documentation | **Fixed** — risk row at plan line 2200 |

## Learnings

### Two-pass recovery as a composable pattern

**Mechanism:** Separating journal reconciliation (close unresolved records) from state reconciliation (demote orphaned jobs) means each pass has a single responsibility. The journal pass only writes journal entries; the sweep only writes job/handle status. Neither invalidates the other's preconditions because they operate on separate JSONL files.

**Evidence:** Traced through JSONL replay semantics: `list_active()` replays the job store log. After the journal pass closes records, `list_active()` doesn't see those (different file). If `job_creation` reconciliation already demoted a job, the sweep's `list_active()` skips it (terminal status).

**Implication:** Future recovery operations (e.g., for `codex.delegate.poll` or promotion) should follow this same two-pass pattern: close journal records first, then sweep state. Mixing both in a single loop creates ordering hazards.

### Scrutiny iteration dynamics

**Mechanism:** First pass found 7 findings; second pass found 0 new correctness issues. The plan went from `Minor revision` to `Defensible` in one round. This is the expected pattern for a well-scoped plan — defects are local (recovery gap, missing test, fixture leak), not architectural, so they resolve cleanly without introducing new ones.

**Evidence:** All 7 findings were localized — none required rethinking the approve/deny contract, journal vocabulary, or MCP dispatch structure.

**Implication:** If a second scrutiny pass surfaces new correctness issues, the plan likely has a deeper structural problem. One-round convergence is a positive signal for architectural soundness.

### Crash-as-verification lens

**Mechanism:** Walking the crash timeline through every line of `decide()` — "what if the process dies here?" — exposed the zombie job finding that static analysis missed. The intent-only record looked harmless (no side effects committed), but the combination of "journal closed" + "job still active" + "runtime gone after restart" creates unresolvable state.

**Evidence:** C3 finding — the crash investigator perspective was the only one of three adversarial lenses that surfaced a real correctness issue. The type system skeptic and state machine auditor confirmed existing correctness.

**Implication:** For any method that writes to multiple stores (journal + job store + lineage store), systematically crash between each write and trace the recovery path. The crash between stores is where invariant violations hide.

## Next Steps

### 1. Execute the T-06 opening slice plan

**Dependencies:** Plan at `docs/plans/2026-04-19-t06-decide-opening-slice.md` is the implementation authority.

**What to read first:**
- Plan pre-flight (lines 104-134) — verify `main` is still at `271f23aa` and baseline tests pass
- Task 3 (lines 636-992) is the highest-risk mechanical step — extract `_execute_live_turn` helper and fix terminal handle lifecycle. Do this in its own commit and verify full suite passes before proceeding.

**Approach:** Follow the plan task-by-task using TDD discipline. The plan specifies exact test code, production code, and commit messages for each of 6 tasks.

**Acceptance boundary:** A `codex.delegate.start` escalation can be approved or denied through `codex.delegate.decide`; approve re-dispatches execution in the retained runtime, deny terminates cleanly, invalid decide attempts return typed rejections, and no promotion behavior is introduced.

### 2. Create feature branch and PR

**Dependencies:** Implementation complete (all 6 tasks landed).

**What to do:** Create `feature/t06-decide-opening-slice`, push, open PR for review. Follow the same review pattern as PR #108 — 5-agent comprehensive review, triage with user, fix before merge.

## In Progress

**Clean stopping point.** Plan written by user, scrutinized twice, all findings addressed. No code changes in flight.

- **Completed:** Two-pass adversarial scrutiny, verdict `Defensible`, user revision verified.
- **Not in flight:** No implementation started, no feature branch created.
- **Next action for next-session Claude:** Run the plan's pre-flight checks (Step P1 and P2), create a feature branch, then execute Task 1.

## Open Questions

### 1. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** The handler calls `entry.session.interrupt_turn()` from inside the `_server_request_handler` callback. This sends a `turn/interrupt` JSON-RPC request via the same transport that's reading notifications.

**Impact:** Medium. If the transport doesn't handle re-entrant reads, the handler will deadlock.

**Decision pending until:** Live testing against the real App Server.

### 2. `on-request` operational semantics (inherited from T-05)

**Context:** The vendored schema proves `on-request` is a valid `approvalPolicy` value, but operational semantics are not documented. Controller defaults to `untrusted` per D1.

**Decision pending until:** Live probe against the real App Server.

### 3. Approve turn prompt shape adequacy

**Context:** The plan defines `build_execution_resume_turn_text()` at plan lines 577-613. It tells the execution agent "the earlier server request has already been resolved at the wire layer" and includes the captured request scope. Whether this prompt produces reliable follow-up behavior (the agent picks up where it left off without re-requesting the same approval) is unverified until live testing.

**Decision pending until:** Implementation and live execution testing.

## Risks

### 1. Task 3 mechanical extraction is the highest-risk step

The `_execute_live_turn` extraction moves ~80 lines of handler-closure + turn-dispatch + finalization from `start()` into a helper. Any mis-transcription of the handler closure (wrong variable capture, missing `nonlocal`, wrong exception guard scope) would cause silent behavioral changes. The plan calls this out explicitly (line 638) and requires a passing full suite before proceeding to Task 4.

### 2. `_FakeSession` complexity continues to grow

Adding `decide` extends the fake session further. If the fake drifts from the real `AppServerRuntimeSession` interface, tests pass but production fails. The per-turn `_interrupted` reset (plan line 700) brings the fake closer to real semantics, but the fake now has: `run_execution_turn`, `interrupt_turn`, `close`, `_raise_on_turn`, `_interrupted` state, and configurable server requests + turn result.

### 3. Same-session-only constraint creates a hard boundary

If the process crashes between `codex.delegate.start` returning an escalation and `codex.delegate.decide` being called, the job is stuck. Recovery now correctly demotes to `unknown` (no more zombies), but the user's escalation decision is lost. `codex.delegate.poll` (future T-06 slice) would allow rediscovering and re-deciding these jobs.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 decide plan | `docs/plans/2026-04-19-t06-decide-opening-slice.md` | Implementation authority (scrutinized, defensible) |
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| T-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | Closed — context for the substrate |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Schema authority |
| Recovery spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Recovery semantics |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-19_16-26_t05-closed-t06-scoped-review-fixes-merged.md`
- T-05/T-06 arc: execution-start COMPLETE → pending-request capture PLANNED → scrutiny + amendments → execute + review + PR → review fixes + merge + T-06 scoping → **T-06 plan scrutinized (this handoff)**

## Gotchas

### 1. Recovery pass ordering matters even when passes are composable

**Symptom:** Assuming journal reconciliation and orphaned-job sweep can run in any order.

**Prevention:** Always run journal reconciliation first. If the sweep ran first and demoted a job, the journal pass would still close the record (harmless). But if a future operation writes a new journal entry based on job status, the order matters: sweep after journal ensures the journal is settled before state changes.

### 2. `_ACTIVE_STATUSES` governs the sweep scope — changes propagate silently

**Symptom:** Adding a new `JobStatus` value without updating `_ACTIVE_STATUSES` at `delegation_job_store.py:22-24` means the sweep might not catch orphaned jobs in the new status.

**Prevention:** The `_ACTIVE_STATUSES` definition has a comment at line 20-21 documenting this. When adding new job statuses, explicitly decide whether they are active or terminal.

### 3. `_CANCEL_CAPABLE_KINDS` defined in two places — drift risk from T-05

**Symptom:** `frozenset({"command_approval", "file_change"})` appears at both the handler and `_finalize_turn`. The plan's `_execute_live_turn` extraction copies both. If the sets drift, the handler might cancel a kind that finalization doesn't consider cancel-capable.

**Prevention:** Tracked since T-05 review (test gap I5). The extraction makes it slightly better (both in the same method now) but doesn't eliminate the duplication.

## Conversation Highlights

### User's plan-first workflow

The user wrote the T-06 plan between sessions and presented it for scrutiny rather than asking Claude to write the plan. This is consistent with the prior session's pattern: user defines scope, Claude reviews and implements. The scrutiny workflow (present → critique → revise → re-critique) was the user's chosen quality gate before handing the plan to an implementation worker.

### User's revision response

The user addressed all 7 findings in a single revision pass, including the most substantive change (recovery semantics). The revision summary distinguished "substantive changes" (recovery fix, new test, runtime guard) from "plan-hardening points" (fixture reset, insertion guidance, documentation).

User on finding severity: "Your C3 point was the real correctness issue. Leaving post-restart `needs_escalation` jobs active in a same-session-only design creates unresolvable state."

User on remaining risk: "The biggest remaining risk is still Task 3's mechanical extraction of the shared execution-turn helper. The plan now calls that out explicitly, but the implementation will still need disciplined execution there."

User on the delegate.start gap: "The other intentional open boundary is unchanged: `codex.delegate.start` still lacks its own dedicated PreToolUse scan policy, and this plan now states that gap is deferred rather than silently ignoring it."

### User's self-verification

User did a self-review pass on the revised document for "stale restart semantics, missing failure-path coverage, placeholder/hand-wave content, consistency between the contract text, controller pseudocode, and risks table." The user explicitly noted: "I did not run tests or implement code; this turn only revised the plan document."

### Scrutiny response pattern

User's revision workflow follows a clear pattern: acknowledge the real correctness issue explicitly, implement fixes for all findings in a single pass (not iteratively), present a structured diff summary mapping each finding to a concrete change, then request re-review. This is the same evidence-first pattern observed across T-05 sessions — the user treats review findings as a triage packet and addresses them in priority order within a single revision.

## User Preferences

### Plan scrutiny before implementation

User presents plans for adversarial review before handing to an implementation session. The scrutiny produces a verdict (`Reject` / `Major revision` / `Minor revision` / `Defensible`) that gates implementation.

### Evidence-first revision

User's revision addressed specific findings with traceable changes. The revision summary mapped each finding to a concrete change in the plan document, distinguishing substantive fixes from hardening.

### Self-verification discipline

User does their own review pass after revision, checking for specific defect categories (stale semantics, missing coverage, placeholder content, cross-document consistency) before requesting a second scrutiny.
