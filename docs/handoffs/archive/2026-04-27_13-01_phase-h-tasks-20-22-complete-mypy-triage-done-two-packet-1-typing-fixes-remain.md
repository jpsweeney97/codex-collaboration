---
date: 2026-04-27
time: "13:01"
created_at: "2026-04-27T17:01:01Z"
session_id: e1d0486a-f581-4a68-bdb9-3ab580baed3f
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-27_01-53_task-20-convergence-map-and-dispatch-packet-reviewed-dispatch-ready.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: f9b7f9bc
title: "Phase H Tasks 20-22 complete, mypy triage done — two Packet 1 typing fixes remain"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_poll_projection_guard_integration.py
  - packages/plugins/codex-collaboration/tests/test_discard_canceled_integration.py
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-20-convergence-map.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-20-dispatch-packet.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-21-convergence-map.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-21-dispatch-packet.md
---

# Handoff: Phase H Tasks 20-22 complete, mypy triage done — two Packet 1 typing fixes remain

## Goal

Complete Phase H of Packet 1 (Deferred-Approval Response) — the final phase. Phase H covers "Finalizer + Consumers + Contracts" and contains Tasks 19-22. Task 19 was completed in a prior session chain. This session completed Tasks 20, 21, and 22, then ran the plan-wide final verification checklist.

**Trigger:** Resumed from the prior session's handoff where Task 20's convergence map and dispatch packet had passed 3 rounds of user scrutiny with verdict "Defensible." The handoff's next step was "Dispatch the Task 20 implementer."

**Stakes:** Phase H is the last phase of Packet 1. After Task 22, the parent manifest's final verification checklist determines whether Packet 1 is complete. Without the `poll()` projection guard (Task 20), an `UnknownKindInEscalationProjection` from `_project_request_to_view` escapes the controller boundary as an unhandled exception. Without the `discard()` gate expansion (Task 21), canceled jobs pile up on the attention surface with no close path. Without contracts.md updates (Task 22), downstream consumers operate against stale public contracts.

**Success criteria:** All Phase H tasks landed, suite green, plan-wide final verification passes.

**Connection to project arc:** T-20260423-02 Packet 1 (Deferred-Approval Response). Phase H is the last of 8 phases (A through H). After Phase H, the parent manifest's final verification determines Packet 1 closure.

## Session Narrative

Resumed from the prior handoff at `c3b310cd`. The starting state was: Task 20's convergence map (9 locks, 5 watchpoints) and dispatch packet were dispatch-credible after 3 rounds of user scrutiny. No production code for Task 20 existed yet.

### Task 20: poll() projection guard

Dispatched the Task 20 implementer as an opus subagent in worktree isolation. The implementer read all 5 authority sources, implemented the exact `try/except UnknownKindInEscalationProjection` catch in `poll()` at `:1826-1828`, and wrote 3 integration tests in `test_poll_projection_guard_integration.py`. Reported DONE at `cb43a499` with 1043/0/0 suite (1040 baseline + 3 new).

Ran the review chain sequentially:
- **Spec reviewer** (opus): PASS — all 9 locks, 5 watchpoints, acceptance criteria, and 11 boundary prohibitions clean. Only deviations were convergence-map-governed (signal-before-log ordering, "signaled" past tense, defense-in-depth guard, `abort_signaled` capture).
- **Code-quality reviewer** (opus): PASS WITH NOTES — two P1 findings: unused `ExecutionRuntimeRegistry` import, and `kind: str` parameter should be `kind: PendingRequestKind`.

Closeout: fixed both P1s directly (per feedback memory: do closeout work directly). User then ran their own review and found a P3: the new test file wasn't ruff-formatted (two list comprehensions). Fixed and committed as `47628f20`. User verdict: "Defensible."

### Task 21: discard() gate expansion

Drafted the convergence map (7 locks, 3 watchpoints) and dispatch packet. Task 21 is notably simpler than Task 20 — one-line production change (add `"canceled"` to a tuple) plus tests. The convergence map corrected 3 stale plan anchors: line numbers shifted by 920 lines (`:1404` → `:2324`), plan placeholder fixtures, and test filename.

User performed 3 rounds of scrutiny:
- **Round 1 ("Minor revision"):** L1 forbade the required docstring update (lock said "no other line changes" but W1 required the docstring). Also: pytest pipeline masked failures (exit code from `tail`, not pytest), and convergence map test strategy still used private `journal._audit_path`.
- **Round 2 ("Minor revision"):** DONE template used basename-only pathspecs for verification commands (`delegation_controller.py` instead of full path). Also: `--exit-code` on the controller diff would fail on correct implementations (the controller IS expected to change). And the `rg | grep` pipeline couldn't match across multiline formatting.
- **Round 3 ("Defensible"):** All findings resolved.

Dispatched implementer (opus, worktree isolation). Reported DONE at `cbf60a7e` with 1046/0/0. Ran spec + quality reviewers in parallel (safe given the simplicity). Both PASS, quality reviewer found one P1: missing `rollback_needed` rejection test for symmetry. Closeout added the 4th test. Suite: 1047/0/0. User verdict: "Defensible."

### Task 22: contracts.md updates

User and I agreed to skip the full dispatch process for Task 22 (docs-only, no production code, no tests). Made 5 contract update groups directly:
1. §Decide Result — rewritten to async acceptance model (3-field response: `decision_accepted`, `job_id`, `request_id`)
2. §Start Success Outcomes — new section with 6-row success/raise union table
3. §Pending Escalation View — `kind` narrowed from 4 to 3 literals (removed `"unknown"`)
4. §DelegationJob.status + §active_delegation.status — added `"canceled"` (6→7 literals)
5. §discard — admissibility rule added with rationale and migration guidance

User scrutiny found two issues:
- **P2:** Decide Result field descriptions said "applied" and "resolved" — synchronous vocabulary that contradicts the async acceptance model. Fixed to "associated with the accepted decision" and "whose decision was accepted for dispatch."
- **P3:** `active_delegation.status` lacked a `canceled` definition or cross-reference. Added cross-reference to `DelegationJob.status`.

Committed at `e07402b2` (initial) + `f9b7f9bc` (review fixes).

### Plan-wide final verification

User ran the parent manifest's 5-gate final verification:

| Gate | Result |
|------|--------|
| Final 1: full pytest | PASS — 1047 passed in 251s |
| Final 2: server mypy | FAIL — 31 errors in 10 files |
| Final 3: structural invariants | PASS |
| Final 4: dialogue regressions | PASS — 102 passed |
| Final 5: integration smoke | PASS — 74 passed |

**Mypy triage result:** 28 errors on feature branch, 24 on main. Only 2 are genuinely new Packet 1 deltas (the 4-count difference includes line-shifted pre-existing errors that sort differently). Both new errors are in `decide()` at `delegation_controller.py:2636-2637`:

1. `:2636` — `request.kind` is `PendingRequestKind` (4 literals) but `DecisionResolution.kind` expects `EscalatableRequestKind` (3 literals). Safe at runtime because `decide()` validates `kind ∈ _ESCALATABLE_REQUEST_KINDS` before reaching this line.
2. `:2637` — `decision` parameter is `str` but `DecisionResolution.action` expects `Literal["approve", "deny"] | None`. Safe at runtime because `decide()` validates `decision ∈ {"approve", "deny"}` before reaching this line.

User directed: fix both now, not carry forward.

## Decisions

### Skip full dispatch process for Task 22

**Choice:** Edit contracts.md directly with lightweight post-edit scrutiny rather than convergence map + dispatch packet + worktree cycle.

**Driver:** User said: "I would not do the full convergence map + dispatch packet + worktree cycle for Task 22. Rationale: Task 22 is single-file, documentation-only, and the authoritative spec text is already concrete."

**Alternatives considered:**
- **Full dispatch process** — rejected because it adds more process than risk reduction for a docs-only change. No production code, no tests, no CAS race semantics.

**Trade-offs accepted:** Slightly less formal review structure. Compensated by user's direct scrutiny of the diff.

**Confidence:** High (E2) — user explicitly recommended the lighter process after evaluating the scope.

**Reversibility:** N/A — process decision, not code decision.

**Change trigger:** If a docs-only task has cross-cutting implications (e.g., contracts that downstream code validates against), the full process may be warranted.

### Run Task 21 reviewers in parallel

**Choice:** Dispatched spec reviewer and code-quality reviewer concurrently for Task 21, unlike Task 20's sequential chain.

**Driver:** Task 21 is simple enough that spec review findings wouldn't invalidate quality review. No CAS, no signal coordination, no helper chains — just a gate expansion.

**Alternatives considered:**
- **Sequential (Task 20 pattern)** — rejected because the simplicity made parallel safe and saved ~2 minutes.

**Trade-offs accepted:** If the spec reviewer had found a fundamental issue, the quality reviewer's work would be wasted. Acceptable given the low probability for this task's scope.

**Confidence:** High (E2) — both reviewers returned independently, findings were non-overlapping.

**Reversibility:** N/A — process decision.

**Change trigger:** For complex tasks (CAS races, signal coordination), revert to sequential.

### Fix mypy errors now rather than carry forward

**Choice:** Fix the 2 Packet-1-introduced mypy errors in `decide()` immediately rather than adding them to the carry-forward register.

**Driver:** User said: "If we carry them forward, the final summary has to say 'mypy fails with two Packet-introduced errors,' which weakens the Packet 1 closeout even if runtime behavior is safe."

**Alternatives considered:**
- **Carry forward** — rejected because it weakens the closeout narrative despite being safe at runtime.

**Trade-offs accepted:** Small code change in `decide()` (likely `cast()` or typed local assignment). No behavioral change.

**Confidence:** High (E2) — both errors have clear fix paths per user guidance.

**Reversibility:** High — `cast()` is trivially removable.

**Change trigger:** N/A — this corrects a gap, not a preference.

## Changes

### Task 20: `delegation_controller.py:1826-1847` — poll() projection guard

**Purpose:** `try/except UnknownKindInEscalationProjection` around `_project_pending_escalation` call in `poll()`. On catch: signal `signal_internal_abort` (capture CAS return as `abort_signaled`), log CRITICAL with `job_id`, `request_id`, `cause`, `abort_signaled` in extra, set `pending_escalation = None`.

**Key design:** Signal-before-log ordering (diverges from `start()` precedent at `:788-813`). `start()` logs before signaling because it raises unconditionally; `poll()` signals first to capture the CAS outcome for the log. Spec §436 requires logging the return value.

**Commits:** `cb43a499` (feat) → `c46a8e44` (type fix) → `47628f20` (ruff format)

### Task 20: `test_poll_projection_guard_integration.py` — 3 integration tests

**Purpose:** Prove the callsite catch: abort-wins (signal returns True), CAS-loss (signal returns False), and normal-kind regression.

**Pattern:** Direct store seeding via `_build_controller(tmp_path)` + `_make_needs_escalation_job` + `_seed_pending_request`. `start()` cannot produce `kind="unknown"` + `needs_escalation` under Task 17's L11 carve-out.

### Task 21: `delegation_controller.py:2312-2326` — discard() gate expansion

**Purpose:** Add `"canceled"` to the `_discardable` status tuple. Update docstring.

**Change:** One line in the gate tuple (`:2325`), plus docstring update (`:2312-2314`). No other lines in `discard()` change.

**Commits:** `cbf60a7e` (feat) → `006d296f` (closeout: rollback_needed test)

### Task 21: `test_discard_canceled_integration.py` — 4 integration tests

**Purpose:** Prove the gate expansion: canceled+null succeeds, canceled+applied rejects, canceled+rollback_needed rejects, audit event written.

**Pattern:** `_build_promote_scenario(tmp_path)` + `update_status_and_promotion`. Audit event test reads `journal.plugin_data_path / "audit" / "events.jsonl"` (public path, not `journal._audit_path`).

### Task 22: `contracts.md` — 5 contract update groups

**Purpose:** Update public contracts to reflect Packet 1 changes.

**Groups:**
1. §Decide Result → async acceptance model (3-field response)
2. §Start Success Outcomes → new 6-row union table
3. §Pending Escalation View → kind narrowed to 3 literals
4. §DelegationJob.status + §active_delegation.status → "canceled" added
5. §discard → admissibility rule with migration guidance

**Commits:** `e07402b2` (initial) → `f9b7f9bc` (review fixes)

## Codebase Knowledge

### poll() method — the Task 20 change site

| Component | Location | Purpose |
|-----------|----------|---------|
| `poll()` method def | `delegation_controller.py:1804` | Returns `DelegationPollResult \| PollRejectedResponse` |
| Try/except guard (NEW) | `:1828-1847` | Catches `UnknownKindInEscalationProjection`, signals abort, logs, nulls escalation |
| `refreshed` job fetch | `:1825` | Post-artifact-materialization re-fetch (W1: use this, not pre-materialization `job`) |
| `detail` assembly | `:1849-1858` | Downstream of catch block (W4: must remain downstream) |

### Exception propagation chain

```
poll() calls _project_pending_escalation(refreshed)
  _project_pending_escalation checks 4 guard states (terminal, unparked, tombstone, non-pending)
    if all pass → calls _project_request_to_view(request)
      _project_request_to_view checks kind ∈ _ESCALATABLE_REQUEST_KINDS
        if NOT in set → raises UnknownKindInEscalationProjection
          WITH Task 20: caught at poll() callsite → signal + log + null escalation
```

### discard() method — the Task 21 change site

| Component | Location | Purpose |
|-----------|----------|---------|
| `discard()` method def | `delegation_controller.py:2309` | Returns `DiscardResult \| DiscardRejectedResponse` |
| `_discardable` gate | `:2324-2326` | Now: `status in ("failed", "unknown", "canceled") and promotion_state is None` |
| Audit event | `:2344-2354` | `append_audit_event(AuditEvent(..., action="discard"))` written to `<plugin_data_path>/audit/events.jsonl` |

### contracts.md — the Task 22 change site

| Section | Location | Change |
|---------|----------|--------|
| Decide Result | `:322-337` | 5-field sync → 3-field async, acceptance language |
| Start Success Outcomes | `:295-310` | NEW section: 6-row union table |
| Pending Escalation View | `:354` | kind: 4→3 literals, unknown excluded with note |
| DelegationJob.status | `:73` | 6→7 literals, canceled definition + migration |
| active_delegation.status | `:404` | 6→7 literals, cross-ref to DelegationJob |
| Discard Result | `:266-272` | Admissibility rule + rationale + migration |

### Test infrastructure patterns

| Pattern | Example | Used by |
|---------|---------|---------|
| 8-tuple destructuring | `_build_controller(tmp_path)` | Task 20 tests |
| 7-tuple destructuring | `_build_promote_scenario(tmp_path)` | Task 21 tests |
| Direct store seeding | `job_store.update_status()` + `pending_request_store.create()` | Task 20 unknown-kind tests |
| Status + promotion override | `job_store.update_status_and_promotion(job_id, status=..., promotion_state=...)` | Task 21 tests |
| Cross-import | `from tests.test_delegation_controller import _build_controller` | Both Task 20 and 21 |
| Audit event assertion | `journal.plugin_data_path / "audit" / "events.jsonl"` (public path) | Task 21 Test 3 |

### DecisionResolution — the mypy fix site

| Component | Location | Purpose |
|-----------|----------|---------|
| `DecisionResolution` class | `resolution_registry.py:33-61` | Dataclass delivered to worker by `decide()` |
| `kind` field | `:59` | `EscalatableRequestKind` (3 literals: command_approval, file_change, request_user_input) |
| `action` field | `:61` | `Literal["approve", "deny"] \| None` |
| `decide()` construction site | `delegation_controller.py:2634-2638` | Where `request.kind` (4 literals) and `decision` (str) are passed |
| `_ESCALATABLE_REQUEST_KINDS` guard | `:2600-2605` (approx.) | Validates `request.kind` before reaching `:2634` — mypy can't trace |

## Context

### Mental model

Phase H is **boundary completion work**: closing the gaps between what the implementation does and what the public contracts promise. Task 20 catches an exception that was designed to never escape the controller boundary. Task 21 opens a close path that the attention surface promises. Task 22 updates contracts to match the implementation. The mypy fix narrows types at a construction site where runtime validation already guarantees safety but the type system can't see it.

### Phase H task map (final state)

| Task | Description | Status | Commits |
|------|-------------|--------|---------|
| 19 | `_finalize_turn` terminal guard | Complete | Prior session chain |
| 20 | `poll()` projection catch | Complete | `cb43a499`, `c46a8e44`, `47628f20` |
| 21 | `discard()` gate expansion | Complete | `cbf60a7e`, `006d296f` |
| 22 | `contracts.md` updates | Complete | `e07402b2`, `f9b7f9bc` |

### Plan-wide final verification (5 gates)

| Gate | Result | Detail |
|------|--------|--------|
| Final 1: full pytest | PASS | 1047/0/0 in 251s |
| Final 2: server mypy | FAIL (pre-existing baseline + 2 new) | 28 errors on feature, 24 on main. 2 genuinely new at `:2636-2637` |
| Final 3: structural invariants | PASS | 6 terminal signal raise sites, 4 request_snapshot.status refs, 21 canceled touch points |
| Final 4: dialogue regressions | PASS | 102/0/0 in 0.35s |
| Final 5: integration smoke | PASS | 74 passed, 973 deselected |

### Suite baseline

1047 tests passing (1040 at session start + 3 from Task 20 + 4 from Task 21).

### Mypy baseline comparison

| Source | Error count | Notes |
|--------|-------------|-------|
| `main` | 24 | Pre-Packet-1 baseline |
| Feature branch | 28 | 24 shifted pre-existing + 2 genuinely new + 2 line-shifted |

The 2 genuinely new errors:
- `:2636` — `PendingRequestKind` (4 literals) passed where `EscalatableRequestKind` (3 literals) expected
- `:2637` — `Literal["approve", "deny"] | str` passed where `Literal["approve", "deny"] | None` expected

Both safe at runtime. `decide()` validates before reaching the construction site.

### Carry-forward register (updated)

| Item | Description | When |
|------|-------------|------|
| TT.1 | `_FakeControlPlane` Pyright issues at `test_delegation_controller.py:257, 2547, 2621, 2686, 2867, 2888, 3064, 3194, 3418` | End-of-Packet-1 typing polish |
| RT.1 | `runtime.py:270` Pyright TurnStatus literal narrowing | End-of-Packet-1 typing polish |

**Removed from carry-forward:** The `:2636`/`:2637` mypy errors — user directed fix now, not carry forward.

## Learnings

### Dispatch packet DONE templates need exit-code-correct verification commands

**Mechanism:** Verification commands in the DONE template are executed literally by the implementer. If a command's exit semantics don't match the expected state (e.g., `--exit-code` on a file that IS expected to change), the implementer reports a false failure.

**Evidence:** Task 21 Round 2 found that `git diff --exit-code` on the controller would fail for a correct implementation (the controller has the gate change). Round 3 found that `rg | grep` pipeline couldn't match across multiline formatting.

**Implication:** Future dispatch packets should test every DONE verification command against the expected post-implementation state before dispatching. `--exit-code` only for files expected to be unchanged.

### Convergence map locks must explicitly account for all allowed hunks

**Mechanism:** When a lock says "no other line changes," it must explicitly list ALL allowed hunks — not just the primary change. A docstring update is a different hunk from the gate change.

**Evidence:** Task 21 Round 1 found L1 forbade the W1 docstring update. The implementer would face a contradictory authority.

**Implication:** When drafting locks that restrict changes to specific lines, enumerate all allowed hunks including docstrings, comments, and imports.

### Parallel reviewers are safe for simple tasks

**Mechanism:** Running spec and quality reviewers concurrently saves wall time. Safe when the task is simple enough that spec findings wouldn't invalidate quality findings.

**Evidence:** Task 21 ran both in parallel; findings were independent (spec: PASS, quality: one P1 symmetry gap).

**Implication:** For tasks with CAS races, signal coordination, or helper chain integrity, keep reviewers sequential.

### Pre-existing mypy baseline must be measured before attributing failures to new work

**Mechanism:** `mypy` on the full server directory includes transitive errors from all imported modules. New code that shifts line numbers causes pre-existing errors to appear at new locations, inflating the apparent delta.

**Evidence:** Feature branch: 28 errors. Main: 24. But only 2 are genuinely new — the other 4 are line-shifted pre-existing errors that sort differently.

**Implication:** Always diff mypy output between feature and main sorted by error message (not line number) to isolate genuinely new errors.

## Conversation Highlights

**User's review methodology:** The user performs formal scrutiny with graduated verdicts: "Major revision" → "Minor revision" → "Defensible" → "Clean pass." Each round has structured sections (Premise Check, Critical Failures, etc.) with named adversarial perspectives.

**Task 22 process decision:**
User: "I recommend making the edits directly, with a lightweight contract-review checklist afterward. I would not do the full convergence map + dispatch packet + worktree cycle for Task 22."
— Set the process boundary for docs-only tasks.

**Async vocabulary catch:**
User found that `job_id` described as "Job the decision was applied to" and `request_id` as "Request that was resolved" used synchronous vocabulary. "That wording undercuts the core async acceptance model."
— Showed that field descriptions in contract tables are what consumers implement against; the explanatory paragraphs below don't override a misleading table.

**Mypy fix directive:**
User: "Fix them now. If we carry them forward, the final summary has to say 'mypy fails with two Packet-introduced errors,' which weakens the Packet 1 closeout even if runtime behavior is safe."
— The fix is about closeout narrative strength, not behavioral risk.

**Suite flake observation:**
User noted a transient failure in an unrelated async decide integration test during full-suite run: "first run hit one transient failure; isolated rerun passed, and a second full-suite run passed." Not attributed to Task 21 but noted as suite flake risk.

## Next Steps

### 1. Fix 2 mypy errors in decide() at delegation_controller.py:2636-2637

**Dependencies:** None — fix is straightforward typing narrowing.

**What to do:**
- `:2636` — Narrow `request.kind` after the `_ESCALATABLE_REQUEST_KINDS` guard. Use `cast(EscalatableRequestKind, request.kind)` or assign to a typed local.
- `:2637` — Narrow `decision` after the `{"approve", "deny"}` validation. Use `cast(Literal["approve", "deny"], decision)` or assign to a typed local.
- Add no behavioral changes.

**Verify:**
```bash
uv run --package codex-collaboration mypy packages/plugins/codex-collaboration/server/delegation_controller.py
```
Expected: same errors as main baseline (24), not 28. The 2 new Packet 1 errors should be gone.

Also run focused decide tests:
```bash
uv run --package codex-collaboration pytest packages/plugins/codex-collaboration/ -k decide -x
```

**Potential obstacles:** If `cast()` introduces import (`typing.cast`), verify it doesn't conflict with existing imports.

### 2. Write plan-wide final verification summary

**Dependencies:** Mypy fix landing (step 1).

**What to do:** Rerun all 5 gates. Expected: all PASS (mypy still shows pre-existing baseline errors but no Packet 1 deltas). Write the summary as "all runtime/test gates pass; mypy remains blocked by pre-existing baseline only."

### 3. Packet 1 closeout

**Dependencies:** Final verification summary (step 2).

**What to do:** Per the manifest, Phase H completion + final verification = Packet 1 closure. Update the carry-forward register. Update MEMORY.md to reflect Packet 1 status.

### 4. Carry-forward items (end-of-Packet-1 typing polish)

| Item | Description |
|------|-------------|
| TT.1 | `_FakeControlPlane` Pyright issues |
| RT.1 | `runtime.py:270` TurnStatus literal narrowing |

## In Progress

**In Progress:** Phase H is complete (Tasks 19-22 all landed). Mypy triage is complete — 2 new Packet 1 errors identified and fix path clear.

- **Approach:** `cast()` or typed local assignment in `decide()` to narrow types at the `DecisionResolution` construction site.
- **State:** Not yet started — user directed to save handoff first.
- **Working:** All 5 final verification gates except mypy. 1047/0/0 suite. contracts.md updated.
- **Not working:** mypy has 28 errors (26 pre-existing, 2 Packet 1 deltas).
- **Open question:** None — fix path is clear.
- **Next action:** Apply `cast()` narrowing at `:2636-2637`, rerun mypy, verify decide tests pass.

## Open Questions

No open questions. The mypy fix path is clear (user provided specific guidance). The plan-wide final verification will confirm Packet 1 readiness after the fix.

## Risks

### Transient suite flake in async decide integration test

User observed one failure in an unrelated async decide integration test during a full-suite run. It did not reproduce on isolated rerun or second full run. Not attributed to any Phase H change, but noted as suite flake risk. If it recurs, investigate the async timing in the decide integration test.

### Pre-existing mypy baseline (24 errors on main)

The 24 pre-existing mypy errors are not Packet 1 scope, but they mean the mypy gate in the final verification checklist cannot fully pass. The Packet 1 closeout should document this as "pre-existing baseline, not Packet 1 regression."

## References

| Resource | Location | Purpose |
|----------|----------|---------|
| Phase H plan | `docs/plans/.../phase-h-finalizer-consumers-contracts.md` | Tasks 19-22 plan body |
| Packet manifest | `docs/plans/.../2026-04-24-packet-1-deferred-approval-response.md` | Parent manifest with final verification checklist |
| Spec design | `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` | Authority for all Packet 1 changes |
| Task 20 convergence map | `docs/plans/.../task-20-convergence-map.md` | 9 locks, 5 watchpoints (binding) |
| Task 20 dispatch packet | `docs/plans/.../task-20-dispatch-packet.md` | Implementer prompt |
| Task 21 convergence map | `docs/plans/.../task-21-convergence-map.md` | 7 locks, 3 watchpoints (binding) |
| Task 21 dispatch packet | `docs/plans/.../task-21-dispatch-packet.md` | Implementer prompt |
| Carry-forward register | `docs/plans/.../carry-forward.md` | TT.1, RT.1 open items |
| Spec §contracts.md updates | `design.md:2023-2051` | Authority for Task 22 |
| Spec §discard gate row | `design.md:1377` | Authority for Task 21 |
| Spec §Projection helper rewrites | `design.md:1888-1988` | Authority for Task 20 poll callsite |
| Spec §Internal abort coordination | `design.md:347-440` | Authority for Task 20 CAS semantics |

## Gotchas

### pytest pipeline masks exit codes

The default shell returns the exit code of the last command in a pipeline. `pytest ... | tail -20` returns `tail`'s exit code (always 0), not pytest's. Use `bash -c 'set -o pipefail; ...'` to propagate pytest's exit code through pipes. This was caught during Task 21 review and is now part of the dispatch packet template.

### Convergence map locks must be hunk-complete

A lock that says "only X changes" must explicitly allow ALL expected hunks, including docstrings. Otherwise the implementer faces a contradictory authority (lock forbids the change, watchpoint requires it). Caught during Task 21 Round 1.

### DONE template verification commands must be exit-code-correct

`git diff --exit-code` is for files expected to be UNCHANGED. For files expected to change, use `git diff` (no `--exit-code`) and describe what to look for. `rg | grep` pipelines may not match across multiline formatting. Use `rg -C 2` for context-aware searches.

### contracts.md field descriptions are what consumers implement against

Explanatory paragraphs below a field table don't override the table itself. If the table says "applied" but the paragraph says "accepted for dispatch," consumers will implement "applied" because they read the table. Field descriptions must use the correct vocabulary from the first occurrence.

## User Preferences

**Review methodology:** Formal scrutiny with graduated verdicts and named adversarial perspectives. Verdicts: "Major revision" → "Minor revision" → "Defensible" → (presumably) "Clean pass." Each round uses structured sections.

**Process calibration:** Scales the dispatch process to task complexity. Full convergence map + dispatch packet + worktree for Tasks 20-21 (production code). Direct edits with lightweight scrutiny for Task 22 (docs-only).

**Mypy expectations:** Packet-introduced typing errors should be fixed before closeout, even if runtime-safe. "The final summary has to say 'mypy fails with two Packet-introduced errors,' which weakens the Packet 1 closeout."

**Citation standard:** Field descriptions in contract tables must use exact async vocabulary. "That wording undercuts the core async acceptance model." — synonymous with the prior session's citation hygiene standard, applied to contracts.
