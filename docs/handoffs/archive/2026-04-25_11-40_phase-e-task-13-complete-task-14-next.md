---
date: 2026-04-25
time: "11:40"
created_at: "2026-04-25T15:40:52Z"
session_id: bd5848b8-0505-49e8-9df4-28af446cc9d9
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-25_01-51_phase-d-complete-phase-e-next.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: f0ea603b
title: Phase E Task 13 complete (5+1 commit chain) — Task 14 next
type: handoff
files:
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegation_decision_result_shape.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - packages/plugins/codex-collaboration/tests/test_mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_models_r2.py
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-e-serialization-projection.md
---

# Handoff: Phase E Task 13 complete (5+1 commit chain) — Task 14 next

## Goal

Complete Phase E Task 13 of T-20260423-02 Packet 1 (deferred-approval-response refactor): rewrite `DelegationDecisionResult` from the pre-Packet-1 5-field shape to the new 3-field shape, plus delete the custom MCP serializer branch. Wire-shape only; no Phase G timing semantics.

**Trigger:** Prior session (resumed from `2026-04-25_01-51_phase-d-complete-phase-e-next.md`) closed at Phase D complete with Phase E read-only orientation produced. User had pre-locked decisions L1-L7 and watchpoints W1-W7 via a convergence map, and the dispatch packet was already drafted. This session executed the dispatch.

**Stakes:** Task 13 is a wire-contract change — every test that asserts on `decide()`'s return shape needs migration. The interregnum framing (synchronous `decide()` with new return shape, async control-flow deferred to Phase G Task 18) is load-bearing: any drift toward documenting Phase G timing semantics in Task 13's docstring or tests would create the F4-pattern docstring-runtime mismatch that the Phase D Task 11 closeout already corrected.

**Success criteria:**
- `DelegationDecisionResult` ships exactly `{decision_accepted: bool, job_id: str, request_id: str}`
- `mcp_server.py`'s custom serializer branch deleted; `return asdict(result)` fallthrough handles new shape
- All three `decide()` construction sites use the 3-field shape
- Per-test migration honesty (no blanket `result.X → poll().X` substitution)
- Full `codex-collaboration` package suite green
- L1-L7 + W1-W7 honored end-to-end

**Connection to project arc:** Task 13 is the first half of Phase E (the second is Task 14, projection-helper rewrite). Phase E is the wire-contract slice between Phase D (`ResolutionRegistry` standalone primitive, complete) and Phase F (worker runner) / Phase G (async public API). The full Packet 1 manifest sequences A→B→C→D→E→F→G→H; Phase E is the midpoint.

## Session Narrative

Started by `/handoff:load` resuming the prior session at commit `bf3f8b19` on branch `feature/delegate-deferred-approval-response`. The prior handoff had completed Phase D Task 12 closeout and produced a Task 13 dispatch packet with locked decisions and per-test triage table.

User invoked the subagent-driven-development workflow with `/subagent-driven-development` skill, providing the full Task 13 dispatch packet inline as the implementer's task text. This established a workflow where the controller (me) does not implement directly — only the implementer subagent writes code; spec compliance and code quality are reviewed by separate subagents.

**Stage 1 — Implementer dispatch (sonnet, general-purpose):** Sent the implementer with the full L1-L7 / W1-W7 / triage-table dispatch packet inline. Implementer reported DONE with one commit `4ed54097`, 9 files changed, 978 tests passing (was 974). Per-test triage produced zero `# Phase G:` deferral comments — all migrated assertions were observable state, not timing-bound. Implementer's report claimed all locks honored.

**Stage 2 — First diagnostics round caught one real regression.** Pyright surfaced ~12 issues. Triage discriminator: `git diff bf3f8b19 HEAD -- <file>` shows whether the diagnostic line was inside a Task 13 hunk. Inside = signal; outside = noise. Result: most issues were stale-cache (Pyright daemon hadn't refreshed) or pre-existing (line 965 `PendingRequestKind` mismatch, lines 116/197 unused names). Real regression: `delegation_controller.py:1822 "updated_job" is not accessed` — the deny path's `updated_job =` binding became orphaned after the L4 rewrite consumed only `job_id` (already in scope as parameter). Sent implementer back; closeout commit `7b85b503` dropped the binding while preserving the `_persist_job_transition()` side-effect call.

**Stage 3 — Second diagnostics round caught another real regression.** New Pyright errors at `test_delegation_controller.py:1711, 1712, 1752, 1753, 1754, 1785, 1786, 2373, 2374`: `Cannot access attribute "job"/"pending_escalation" for class "PollRejectedResponse"`. The migrations did `poll = controller.poll(job_id=...)` followed by direct `poll.X` access without isinstance narrowing. But `controller.poll()` returns `DelegationPollResult | PollRejectedResponse` (verified at `delegation_controller.py:1011`); only the success type carries those attributes. Tests passed at runtime because `poll` always resolved to `DelegationPollResult` in those scenarios, but type-system hygiene required the assert. Pattern matches the package's existing idiom at `:1705` (decide-result narrowing) and `:2514` (poll-result narrowing). Sent implementer back; closeout commit `1187e8c4` added `assert isinstance(poll, DelegationPollResult)` before each `poll.X` access in the four migrated tests.

**Stage 4 — Spec compliance review (sonnet, general-purpose).** Verdict: ✅ Spec compliant. All L1-L7 honored, all W1-W7 watchpoints clean, all acceptance criteria met, no scope leaks (no `completion_origin`, no `contracts.md` edits, no `ResolutionRegistry` wiring), per-test migration honesty preserved (no `# Phase G:` deferral comments needed because all migrated assertions were observable state). Suite: 978 passing.

**Stage 5 — Code quality review (superpowers:code-reviewer).** Verdict: Ready to merge **with fixes**. Surfaced 2 Important findings + 4 Minor findings:
- Important 1: `delegation_controller.py:1879-1890` had a vestigial `if isinstance(follow_up, DelegationEscalation):` branch in the approve path. Both arms returned literally identical `DelegationDecisionResult(decision_accepted=True, job_id=job_id, request_id=request_id)` post-rewrite. The conditional only existed because the pre-Packet-1 shape extracted `follow_up.pending_escalation` / `follow_up.agent_context` per-branch.
- Important 2: `test_mcp_decide_response_shape_integration.py` was misnamed — the filename claimed `_integration` but the single test only called `asdict()` on a freshly-constructed dataclass, not driving the MCP boundary. The `_integration.py` suffix is a load-bearing convention in the package for tests that drive `server.handle_request(...)` end-to-end.
- Minor 3-6: redundant shape test in `test_models_r2.py`, "Breaking change" docstring paragraph belongs in CHANGELOG/contracts.md, repeated `# Post-dispatch ... (Packet 1)` comments, `decision_accepted` always-True observation.

**Stage 6 — Iterative closeouts.** Sent implementer back with both Important fixes. Closeout commit `da46efa9` collapsed the vestigial branch; bonus catch — the implementer also dropped the orphan `follow_up =` binding, recognizing it as the symmetric counterpart to closeout-1's `updated_job` cleanup. Closeout commit `e9955ec7` folded the misnamed shape test into `test_delegation_decision_result_shape.py` as `test_asdict_emits_exactly_three_keys` (strengthened — now also asserts each value, not just the key set), and deleted the misnamed file.

**Stage 7 — Code quality re-review.** Verdict: ✅ Ready to merge. Both Important issues resolved. Minor recommendations 3-6 remain explicitly deferred per controller's deferral.

**Stage 8 — Independent third-party verification (user-driven via `/copy`).** User ran an external verification pass on the full Task 13 diff. Reported: "None. I found no correctness, boundary, or test-honesty issues in the Task 13 closeout." Confirmed the in-session two-stage review held under independent inspection — convergence on "Ready to merge" from two independent assessments.

**Stage 9 — Closeout-docs commit.** Updated `docs/plans/.../carry-forward.md` with: (a) 3 new Open items entries (E13.1-E13.3) for deferred minors, (b) C10.4 row clarified to point to Phase F worker-runner work, (c) full Closed items entry under "From Phase E Task 13 + closeouts" with the 5-commit chain narrative, the defect-class pattern observation, lock conformance summary, and severity disposition rationale. Commit `f0ea603b` matches the bf3f8b19 Phase D Task 12 closeout-docs pattern (only carry-forward.md touched; phase-e-serialization-projection.md plan-template unchecked-boxes deliberately left as-is, matching Phase D precedent).

**Set aside for later:** Task 14 (projection helpers — `_project_request_to_view`, `_project_pending_escalation`, `_ESCALATABLE_REQUEST_KINDS`) deferred to fresh session. Three E13.x carry-forward items deferred to Task 14 / Phase H per their landing-point rows.

## Decisions

### D1: Use subagent-driven-development workflow

**Choice:** Execute Task 13 via the `subagent-driven-development` skill with implementer + spec-reviewer + code-quality-reviewer subagents, rather than implementing in the main session.

**Driver:** User explicitly said: "Use subagent-driven-development". Workflow choice was a hard constraint, not a recommendation.

**Alternatives considered:**
- **Direct in-session implementation** — controller writes code itself. Rejected because user explicitly directed the subagent workflow.
- **Single-stage subagent** (implement only, no review subagents) — rejected because the workflow contract requires both spec compliance AND code quality review per task.

**Implications:** Each commit has at least one review pass; controller's main-context stays clean (delegated implementation context lives in subagent contexts); review-found issues round-trip via SendMessage to the same implementer subagent (preserves implementer's context across iterations).

**Trade-offs accepted:** More subagent invocations (1 implementer + multiple review rounds + 1 spec reviewer + 1 code quality reviewer + 1 re-review = 5+ subagent calls). Two-stage review adds latency vs. faster direct implementation. Accepted because: workflow contract requires it, AND review caught issues that would otherwise have shipped (vestigial branch, misnamed file).

**Confidence:** High (E2) — workflow executed end-to-end; both review stages found real issues that informed closeouts.

**Reversibility:** N/A — workflow choice was per-session.

**Change trigger:** None — user-directed workflow.

### D2: Sonnet model for implementer subagent

**Choice:** Dispatched implementer with `model: "sonnet"` (general-purpose subagent type), not Haiku or Opus.

**Driver:** Skill documentation tier guidance — "Touches multiple files with integration concerns → standard model"; "Requires design judgment or broad codebase understanding → most capable model". Task 13 touches 4-5 files (models.py, mcp_server.py, delegation_controller.py, plus 4-5 test files) with per-test triage judgment calls (which `result.X` migrate to `poll().X` vs. defer to `# Phase G:`).

**Alternatives considered:**
- **Haiku** — cheap-model territory. Rejected because the per-test triage table requires judgment, not just mechanical substitution. Haiku's failure mode on judgment calls is to either over-migrate (blanket substitution) or under-migrate (skip per-case decisions).
- **Opus** — overkill. Rejected for cost; the task is integration-not-architecture.

**Implications:** Implementer hit clean implementation on first try; missed two dead-binding catches (deny-arm `updated_job`, approve-arm `follow_up`) that surfaced under iterative review. Standard model is calibrated for catch-most, not catch-all.

**Trade-offs accepted:** Two extra closeout commits (7b85b503, da46efa9) for the dead-binding cleanups vs. the alternative of using Opus for the feat commit and possibly catching both up-front. Cost-vs-thoroughness trade-off.

**Confidence:** High (E2) — calibration matched workflow guidance and produced a workable result.

**Reversibility:** N/A — model choice was per-dispatch.

**Change trigger:** If iterative-review counts ever exceeded 3 closeouts per task, escalate to Opus for the feat commit.

### D3: New commits for closeouts, never amend

**Choice:** Each review-surfaced fix went to a separate `fix(...)` or `test(...)` commit, never amend the previous commit.

**Driver:** Project's CLAUDE.md global rules: "Always create NEW commits rather than amending, unless the user explicitly requests a git amend." User has not requested amend.

**Alternatives considered:**
- **Amend each closeout into its preceding commit** — rejected per CLAUDE.md.
- **Soft reset + recommit to squash all closeouts into the feat** — rejected as a destructive history-rewrite that the user's CLAUDE.md says to avoid.

**Implications:** Task 13 chain became 5 commits (feat + 4 closeouts) before the docs commit (6 total). Long but transparent history; each closeout commit message explains what it fixed.

**Trade-offs accepted:** Longer commit chain than canonical 3-commit shape (feat + 1 closeout-fix + 1 closeout-docs, per Phase D Tasks 11 and 12). Accepted because rule is non-negotiable.

**Confidence:** High (E3) — CLAUDE.md is authoritative, project pattern is consistent (becbb124 + 8d4f9b96 closeouts in Phase D were also new commits, not amends).

**Reversibility:** N/A — commits are durable.

**Change trigger:** User explicitly requesting amend on a future task.

### D4: Branch-collapse fix despite L4 saying "three construction sites"

**Choice:** Closeout 3 collapsed the vestigial `if isinstance(follow_up, DelegationEscalation):` branch in `decide()` approve path, leaving 2 construction sites instead of 3.

**Driver:** Code quality review surfaced that both arms returned literally identical `DelegationDecisionResult(decision_accepted=True, job_id=job_id, request_id=request_id)` values — the conditional was dead structure post-rewrite.

**Alternatives considered:**
- **Leave the branch + add a comment marking it Phase G territory** — rejected because the structure implies a behavior difference that doesn't exist; the F4-pattern (docstring-runtime mismatch) applies to code structure too.
- **Treat L4 as prescriptive about count** — rejected because L4's spirit was "all sites use 3 fields", not "preserve site count". The site count was descriptive, not a contract.

**Implications:** Phase G Task 18 may add NEW conditionals for genuinely different reasons (reservation timing, registry signals), but those won't be preserved versions of this branch. Removing dead structure now keeps the pre-Phase-G state clean.

**Trade-offs accepted:** Possible Phase G churn if it re-introduces branching for different reasons. Accepted because: (a) dead structure is worse than minor potential churn, (b) Phase G Task 18 will rewrite `decide()` substantially anyway per phase-g plan.

**Confidence:** High (E2) — verified both arms returned identical values via diff; verified no consumer of `follow_up` after the conditional.

**Reversibility:** High — Phase G Task 18 can re-introduce conditionals if needed.

**Change trigger:** If Phase G Task 18 needs to differentiate the approve+escalation vs approve+completed cases at the `decide()` return level, the branch can be re-introduced.

### D5: Fold misnamed shape test rather than rename + retain

**Choice:** Closeout 4 folded `test_mcp_decide_response_shape_integration.py`'s single test into `test_delegation_decision_result_shape.py` (as `test_asdict_emits_exactly_three_keys`, strengthened to assert each value); deleted the misnamed file.

**Driver:** Code quality review surfaced two issues conflated in the misnamed file: (a) misnomer (filename claims `_integration` but test doesn't drive MCP boundary), (b) redundancy (the asdict test is essentially a 4th case of the shape test). Genuine MCP-boundary coverage of the new shape already exists at `test_mcp_server.py:1192-1199` (drives `handle_request`) and `test_delegate_start_integration.py:898+` (full e2e for approve/deny/re-escalation).

**Alternatives considered:**
- **Rename only (keep file, drop `_integration` suffix)** — rejected because the asdict test is redundant with the shape test file.
- **Rewrite the test to actually drive `McpServer.handle_request` end-to-end** — rejected as scope creep; existing coverage already drives MCP at the integration tests.

**Implications:** Single canonical home for shape assertions (`test_delegation_decision_result_shape.py`); the `_integration.py` filename convention discriminator is preserved (no false positives).

**Trade-offs accepted:** None significant — the fold strengthened the assertion (now also asserts each value), so coverage actually improved.

**Confidence:** High (E2) — verified existing MCP-boundary coverage at the cited locations.

**Reversibility:** High — could be split back if a genuine MCP-boundary integration test specifically for `decide()` shape is needed (none currently identified).

**Change trigger:** If a future task adds MCP-boundary tests specifically for shape contracts (different from current end-to-end coverage), folding could be undone.

### D6: Defer minor findings 3-6, with explicit landing points

**Choice:** Of the 4 Minor findings from code quality review, 3 were deferred to Task 14 / Phase H (added as carry-forward items E13.1-E13.3); 1 was declined as intentional convention preservation.

**Driver:** Scope discipline — Task 13 was wire-shape-only. Minors are non-blocking by definition. Each deferred minor has a natural landing point that's already in the plan (Task 14 will touch test_models_r2.py via projection-helper rewrites; Phase H owns contracts.md).

**Specific dispositions:**
- E13.1 (redundant `test_models_r2.py:287-300`) → Task 14 cleanup pass
- E13.2 (docstring "Breaking change" paragraph) → Phase H trim alongside contracts.md
- E13.3 (`decision_accepted` always-True comment) → Phase H
- Minor 5 (repeated `# Post-dispatch ... (Packet 1)` comments) → declined; per-site comments preserve grep-ability and match the package's existing `# C10.4:` / `# Phase G:` style markers

**Implications:** Carry-forward tracker grows by 3 items (now 12 + 3 = 15 open). Phase H scope formalizes; Task 14 absorbs E13.1.

**Trade-offs accepted:** Slight carry-forward accumulation. Mitigated by: explicit landing points (no orphans), upcoming task naturally touches the same files (Task 14 → test_models_r2.py).

**Confidence:** High (E2) — landing points verified against plan structure.

**Reversibility:** High — items can be promoted to in-scope on the landing task.

**Change trigger:** If Phase H or Task 14 doesn't naturally touch these files, items become "end-of-Packet-1 polish" instead.

## Changes

### `packages/plugins/codex-collaboration/server/models.py` (modified)

**Purpose:** Rewrote `DelegationDecisionResult` from 5-field shape to 3-field shape (`decision_accepted: bool`, `job_id: str`, `request_id: str`). Added shape-only docstring.

**Approach:** Frozen dataclass, no defaults, no Optional fields. Docstring describes wire shape and points callers to `poll()` for post-dispatch state. NO mention of async timing (W7 lock).

**Key location:** `models.py:457-472` — class definition.

**Future-Claude:** Task 14 will likely reference this shape from `_project_pending_escalation` (out of scope for Task 13).

### `packages/plugins/codex-collaboration/server/mcp_server.py` (modified)

**Purpose:** Deleted the custom `isinstance(result, DelegationDecisionResult)` serializer branch from the `codex.delegate.decide` handler. Removed the function-local `from .models import DelegationDecisionResult` import (orphan after deletion).

**Approach:** Let the existing `return asdict(result)` fallthrough handle the new shape — symmetric with how `poll`, `promote`, `discard` already work.

**Key location:** `mcp_server.py:460-510` — decide handler. Fallthrough at `:503`.

**Future-Claude:** This is a deletion-not-replacement change. Do not re-introduce custom branches; the generic fallthrough is the correct pattern for the new shape.

### `packages/plugins/codex-collaboration/server/delegation_controller.py` (modified)

**Purpose:** Rewrote `decide()` success construction sites to use the 3-field shape. Initial commit had three sites (deny, approve+escalation, approve+completed); closeout-3 collapsed the latter two into one because both returned identical values. Net: 2 sites.

**Approach:**
- Deny path (~line 1842-1846): `return DelegationDecisionResult(decision_accepted=True, job_id=job_id, request_id=request_id)`. Closeout-1 dropped the dead `updated_job =` binding above it; the `_persist_job_transition(job_id, "failed")` call still executes for its side-effect.
- Approve path (~line 1880-1884): single `return DelegationDecisionResult(decision_accepted=True, job_id=job_id, request_id=request_id)` after the shared `write_phase` and `_decided_request_ids.add()` side-effects. Closeout-3 collapsed the vestigial `if isinstance(follow_up, DelegationEscalation):` branch and dropped the orphan `follow_up =` binding from `_execute_live_turn`.

**Key locations:**
- `delegation_controller.py:1820-1851` — deny path try/except
- `delegation_controller.py:1853-1895` — approve path try/except

**Future-Claude:** Phase G Task 18 will rewrite `decide()` with reservation context manager + new return semantics. Phase F (C10.4) will add `completion_origin="worker_completed"` to the `write_phase` calls. Both are explicitly out of Task 13 scope.

### `packages/plugins/codex-collaboration/tests/test_delegation_decision_result_shape.py` (new)

**Purpose:** Canonical home for `DelegationDecisionResult` shape assertions.

**Approach:** Four tests:
1. `test_has_exactly_three_fields` — `dataclasses.fields()` returns exactly `{"decision_accepted", "job_id", "request_id"}`
2. `test_decision_accepted_is_bool` — value type
3. `test_no_pending_escalation_or_agent_context` — explicit `assert not hasattr(r, X)` for each of 5 removed field names
4. `test_asdict_emits_exactly_three_keys` (added in closeout-4) — exact key set + each value preserved through `asdict()`

**Key location:** All 4 tests in this file.

**Future-Claude:** Add a 5th test if you discover a new shape invariant. The `assert not hasattr` pattern in test 3 will catch accidental field re-additions.

### `packages/plugins/codex-collaboration/tests/test_delegation_controller.py` (modified)

**Purpose:** Migrated 4 decide-success tests to assert on `controller.poll(job_id=...)` instead of `decide()` return shape.

**Migrated tests (with key locations):**
- `test_decide_approve_resumes_runtime_and_returns_completed_result` (~line 1660-1716)
- `test_decide_approve_can_reescalate_with_new_pending_request` (~line 1718-1758)
- `test_decide_deny_marks_job_failed_and_closes_runtime` (~line 1760-1800)
- `test_decide_rejects_stale_request_id_after_reescalation` (~line 2330-2384)

**Approach:** Each migration:
1. Deleted `result.decision == ...` and `result.resumed is ...` assertions (input echo + timing flag, removed from contract)
2. Migrated `result.job.X` and `result.pending_escalation.X` to `controller.poll(job_id=...).X` for observable state
3. Added `assert isinstance(poll, DelegationPollResult)` (closeout-2) before each `poll.X` access — `poll()` returns `DelegationPollResult | PollRejectedResponse`; type-system narrowing required
4. Added `# Post-dispatch state observed via poll(), not decide() result (Packet 1).` comments

**Future-Claude:** No `# Phase G:` deferral comments needed — all migrated assertions were observable state, not timing-bound. The narrowing pattern matches `:1705` (decide-result) and `:2514` (poll-result, pre-existing).

### `packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py` (modified)

**Purpose:** Migrated 3 MCP-level integration tests to use `codex.delegate.poll` for observable state, asserting only the 3-field wire shape on `decide_payload`.

**Migrated tests (with key locations):**
- `test_delegate_decide_approve_end_to_end_through_mcp_dispatch` (~line 894-941)
- `test_delegate_decide_deny_end_to_end_through_mcp_dispatch` (~line 943-980)
- `test_decide_reescalation_uses_pending_escalation_key` (~line 1077-1145)

**Approach:** Each migration adds `set(decide_payload.keys()) == {"decision_accepted", "job_id", "request_id"}` exact-shape assertion, then dispatches a separate `codex.delegate.poll` MCP call to assert `poll_payload["job"]["status"]` or `poll_payload["pending_escalation"]`.

**Future-Claude:** JSON-payload accesses (`poll_payload[...]`) don't need isinstance narrowing — `json.loads()` returns `dict[str, Any]`, duck-typed.

### `packages/plugins/codex-collaboration/tests/test_mcp_server.py` (modified)

**Purpose:** Updated `FakeDelegationControllerWithDecide.decide()` stub to construct the new shape; updated `test_handle_tools_call_delegate_decide` assertions from `payload["decision"]` / `payload["resumed"]` to the 3-field shape.

**Key location:** ~line 1196 (test) + fake stub.

### `packages/plugins/codex-collaboration/tests/test_models_r2.py` (modified)

**Purpose:** Rewrote `test_delegation_decision_result_shape` to construct the new 3-field shape and assert on new fields only.

**Key location:** ~line 287-300.

**Future-Claude:** Carry-forward item E13.1 — this test is now redundant with the new dedicated `test_delegation_decision_result_shape.py`. Remove or repurpose during Task 14 cleanup pass.

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (modified)

**Purpose:** Phase E Task 13 closeout-docs commit (`f0ea603b`). Three changes:
1. C10.4 row "Lands at" updated from "When the worker-side provenance story is wired (post-Phase-C task)" to "Phase F worker-runner work (worker-side provenance)" — clarification, not scope change
2. New "Open items → From Phase E Task 13" subsection with 3 entries: E13.1, E13.2, E13.3 (deferred minors)
3. New "Closed items → From Phase E Task 13 + closeouts" entry with full 5-commit chain narrative, defect-class pattern observation, lock conformance summary, and severity disposition rationale

**Key location:** Open items at lines ~52-58; Closed items at lines ~110-130 (after Phase D Task 11 closeout entry).

## Codebase Knowledge

### `DelegationDecisionResult` shape (post-Task-13)

```python
@dataclass(frozen=True)
class DelegationDecisionResult:
    """Returned by codex.delegate.decide.

    Packet 1 (T-20260423-02) result shape: decision_accepted, job_id,
    request_id. Post-dispatch state, including any re-escalation that
    follows an approve, is observed via codex.delegate.poll, not embedded
    in this result.

    Breaking change from the pre-Packet-1 shape. Callers that previously
    read `pending_escalation` or `agent_context` from decide's response
    must switch to poll().
    """

    decision_accepted: bool
    job_id: str
    request_id: str
```

Key location: `packages/plugins/codex-collaboration/server/models.py:457-472`.

### `decide()` construction-site map (post-Task-13)

| Site | File:Line | Path | Returns |
|------|-----------|------|---------|
| Deny | `delegation_controller.py:~1842-1846` | After `_persist_job_transition(job_id, "failed")` + journal write_phase | `DelegationDecisionResult(decision_accepted=True, job_id=job_id, request_id=request_id)` |
| Approve | `delegation_controller.py:~1880-1884` | After `_execute_live_turn(...)` + journal write_phase + `_decided_request_ids.add()` | Same |

Pre-Task-13 there were 3 sites; closeout-3 collapsed approve+escalation and approve+completed into one because they returned identical values.

### `controller.poll()` return-type union

```python
def poll(self, *, job_id: str) -> DelegationPollResult | PollRejectedResponse:
    ...
```

Key location: `packages/plugins/codex-collaboration/server/delegation_controller.py:1011`.

`DelegationPollResult` carries `.job` (with `.status`), `.pending_escalation`, `.inspection`. `PollRejectedResponse` carries `.reason` only. Direct attribute access on the union requires isinstance narrowing — Pyright will flag missing narrowing.

Established narrowing pattern in tests:
- `tests/test_delegation_controller.py:1705` — `assert isinstance(result, DelegationDecisionResult)`
- `tests/test_delegation_controller.py:2514` — `assert isinstance(first, DelegationPollResult)`
- `tests/test_delegation_controller.py:1711, 1751, 1784, 2372` — added in closeout-2 for `poll`/`re_esc_poll`

### MCP serializer pattern (post-Task-13)

`codex.delegate.decide` MCP tool handler at `packages/plugins/codex-collaboration/server/mcp_server.py:460-510`. Success path:

```python
result = self._controller.decide(...)
if isinstance(result, DecisionRejectedResponse):
    return {...rejection-specific payload...}
return asdict(result)  # generic fallthrough — handles DelegationDecisionResult
```

This is symmetric with `poll`, `promote`, `discard` handlers — they all use `asdict(result)` fallthrough for success types. Custom serializer branches (like the one Task 13 deleted) are an anti-pattern when the dataclass shape is JSON-friendly.

### `_integration.py` test-file naming convention

In this package, `test_<thing>_integration.py` files specifically drive `server.handle_request(...)` end-to-end. The discriminator is load-bearing — code reviewers and PR readers use the filename to triage MCP-boundary coverage.

Examples:
- `test_delegate_start_integration.py` — drives full e2e MCP flow (start → decide → poll)
- `test_mcp_server_initialize_integration.py` — drives MCP initialize handshake

A test that just calls `asdict()` on a dataclass is a unit test, not an integration test, and must not squat the convention.

### Carry-forward.md structure

```
# Packet 1 Carry-Forward Tracker
...
## Open items
### From Phase A
### From Phase B Task 6
### From Phase B Task 7
### From Phase B Task 8
### From Phase C Task 10
### From Phase E Task 13   <-- added f0ea603b
---
## Closed items
### From Phase B Task 6
### From Phase B Task 7
### From Phase B Task 9 + closeout
### From Phase C Task 10 + closeout
### From Phase D Task 12 + closeout
### From Phase D Task 11 + closeout
### From Phase E Task 13 + closeouts   <-- added f0ea603b
---
## How to add an item
```

Phase ordering at section level is forward (A → B → C → D → E); within phase, most-recent-task-first for D (D12 before D11). Open and Closed sections follow this convention.

### Phase E plan structure

`docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-e-serialization-projection.md` has Tasks 13 and 14. Task 13 occupies lines 10-189 (approx); Task 14 starts at line 190. Plan-template checkboxes (`- [ ]`) are deliberately left unchecked even after closure — matches Phase D precedent (`phase-d-registry.md` also has all-unchecked boxes despite Tasks 11+12 being complete). The plan is a template; the carry-forward.md is the canonical "what was actually closed" record.

### Task 13 commit chain (final)

| SHA | Type | Subject |
|-----|------|---------|
| `4ed54097` | feat | rewrite DelegationDecisionResult to 3-field shape + fix MCP serializer |
| `7b85b503` | fix closeout 1 | drop dead updated_job binding after deny-path rewrite |
| `1187e8c4` | fix closeout 2 | narrow poll() return type in migrated decide tests |
| `da46efa9` | fix closeout 3 | collapse vestigial decide approve branch (+ symmetric follow_up cleanup) |
| `e9955ec7` | test closeout 4 | fold misnamed shape integration test into shape test file |
| `f0ea603b` | docs closeout | record Phase E Task 13 closeout (carry-forward.md) |

### Defect-class pattern observed

Closeouts 1 and 3 share a root cause: dead local bindings left over after the result-shape rewrite.

| Closeout | Arm | Dead binding | Pre-Packet-1 use |
|----------|-----|--------------|------------------|
| 1 | Deny | `updated_job = self._persist_job_transition(...)` | Used as `job=updated_job` in old constructor |
| 3 | Approve | `follow_up = self._execute_live_turn(...)` | Used as `follow_up.pending_escalation` / `.agent_context` in old constructor; also gated `if isinstance(follow_up, DelegationEscalation):` |

Both arms surfaced this in their own closeout commits because the pattern emerged only after the 3-field shape consumed only `job_id` and `request_id` (already in scope as `decide()` parameters). A single up-front "what was this binding/branch for?" pass during the feat commit would have caught both. This is a generalizable trap for shape-rewrite tasks: the bindings/branches that fed the old constructor often become orphaned but don't error out — they require a deliberate audit.

## Context

### Project state

T-20260423-02 Packet 1 progress (post-Task-13):

| Phase | Tasks | Status |
|-------|-------|--------|
| A (types) | 1-5 | Complete |
| B (stores) | 6-9 | Complete (with Task 9 closeout) |
| C (journal) | 10 | Complete |
| D (registry) | 11-12 | Complete (with closeouts) |
| **E (serialization/projection)** | **13-14** | **Task 13 complete; Task 14 next** |
| F (worker) | 15-16 | Not started |
| G (public API) | 17-18 | Not started |
| H (finalizer/consumers/contracts) | 19+ | Not started |

12 + 3 (E13.x) = 15 open carry-forward items at start of Task 14.

### Branch state

Branch: `feature/delegate-deferred-approval-response`. Clean working tree at `f0ea603b`. 6 commits on this branch beyond what was on the prior session's `bf3f8b19`.

### Mental model

**Wire-shape vs timing-semantics separation.** Phase E ships the wire contract (what fields are returned, what JSON shape is emitted); Phase G ships the timing semantics (when does `decide()` return — synchronously after dispatch, or async after reservation). These are orthogonal axes and must not be conflated. Task 13's docstring is shape-only deliberately — any timing language would create the F4-pattern docstring-runtime mismatch (per Phase D Task 11's closeout, where `ReservationToken.generation` was advertised but inert; the docstring described a contract that wasn't delivered until the closeout fix).

**Synchronous interregnum.** Between Phase E (Task 13 ships shape) and Phase G (Task 18 ships timing), `decide()` has the new return shape but pre-Phase-G synchronous control flow internally. This is intentional, not a bug. Tests must not assert anything that would only be true under Phase G timing (e.g., "decide() returns before dispatch completes"). The W7 watchpoint guarded against this drift.

**Per-test triage discipline.** Old assertions like `result.job.status == "completed"` could be migrated to `controller.poll(job_id=...).job.status == "completed"` — but only if the test was about observable state. If the assertion was about timing (e.g., "the new shape exists because of async dispatch"), it must defer to Phase G with a `# Phase G:` comment naming the specific async observable. Task 13's migrations didn't need any such deferrals — all migrated assertions were observable state.

### Environment

- Python 3.12, uv workspace, pytest test runner
- Run package suite: `cd /Users/jp/Projects/active/claude-code-tool-dev && uv run --package codex-collaboration pytest`
- Pyright in IDE for type-checking; daemon cache lags behind file edits — use `git diff <base> HEAD -- <file>` to discriminate stale-cache from real regressions
- Branch protection hook (`.claude/rules/workflow/git.md`): edits allowed on `feature/*` branches, blocked on `main`/`master`
- Branch is on `feature/delegate-deferred-approval-response` — edits allowed throughout

## Conversation Highlights

**Workflow choice (definitive):**
User: "Use subagent-driven-development"
— Drove the entire stage-by-stage implementer + spec-reviewer + code-quality-reviewer pipeline.

**Independent verification after Task 13 closeouts (via `/copy 2`):**
User: "Findings: None. I found no correctness, boundary, or test-honesty issues in the Task 13 closeout."
— Confirmed the in-session two-stage review held under independent inspection. Convergence on "Ready to merge" from two independent assessments.

**Closeout pattern preference:**
User: "I would treat Task 13 as review-complete and ready for the Phase E Task 13 closeout-docs commit then saving a handoff, so the next Task 14 dispatch can take place in a fresh session."
— Set the closeout-docs-then-handoff sequence and the fresh-session intent for Task 14.

**Sequencing:**
User: "closeout-docs commit first, then handoff"
— Confirmed sequence after I offered to do both.

**Pre-dispatch (from session start, prior session's locks):**
- L1-L7 + W1-W7 hard constraints, locked in convergence map (prior session)
- "If the map tries to land Phase G timing language or treats every old `resumed` assertion as a simple `poll()` migration, stop there and correct it before implementation" (prior session) — applied throughout this session as the W3 + W7 enforcement principle

**Working style observed:** User produces tight, evidence-first input (tables, file:line citations) and expects similar in return. Defends recommendations explicitly when challenged. Treats locks as non-negotiable scaffolding, not advice. Uses `/copy` to extract specific responses for external verification — this session, that produced the third-party "Findings: None" verdict that closed the Task 13 work.

## User Preferences

**Workflow:** "Use subagent-driven-development" — when this skill is invoked, the controller (Claude) does not implement; only review subagents critique. Each task has implementer + spec-reviewer + code-quality-reviewer stages, with the implementer round-tripping fixes via SendMessage.

**Closeout cadence:** Closeout-fix commits (one or more `fix(...)` after the `feat(...)`) followed by a closeout-docs commit (`docs(...)`) updating carry-forward.md only. Plan-template checkboxes are not ticked. Pattern matches Phase D (commits `bf3f8b19`, `04421cba`).

**Commit discipline:** New commits, never amend. Project's CLAUDE.md (global): "Always create NEW commits rather than amending, unless the user explicitly requests a git amend." Match this rule strictly.

**Scope discipline:** Locked decisions (L1-L7) and watchpoints (W1-W7) are hard constraints, not advice. Out-of-scope items have explicit landing points (Task 14, Phase F, Phase G Task 18, Phase H). Carry-forward items track deferred minors with landing points; never orphans.

**Per-test triage style:** No blanket migrations. Every old assertion gets per-case judgment: delete (input echo, timing flag), migrate to `poll()` (observable state), or defer with `# Phase G:` comment naming the specific async observable. The triage table in dispatch packets is binding, not advisory.

**Evidence density:** File:line citations expected throughout. Tables preferred over prose for relationships and decisions. Quotes preferred over paraphrase for user statements.

**External verification:** User frequently runs `/copy <N>` to extract specific responses for independent (out-of-session) review. The convergence test is whether the in-session two-stage review and the external pass agree.

## Next Steps

### 1. Phase E Task 14 dispatch — projection helpers rewrite

**Dependencies:** Task 13 complete (✅).

**What to read first:**
- `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-e-serialization-projection.md` — Task 14 plan section starts at ~line 190
- `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` — `_project_pending_escalation` job-anchored pattern; tombstone projection; `_ESCALATABLE_REQUEST_KINDS` definition
- `packages/plugins/codex-collaboration/server/delegation_controller.py:~960-1010` — current `_project_request_to_view` (needs `UnknownKindInEscalationProjection` guard)
- `packages/plugins/codex-collaboration/server/delegation_controller.py:~750-780` — current `_project_pending_escalation`
- Carry-forward A3 (related: line 965 `PendingRequestKind`/`EscalatableRequestKind` mismatch resolved by Task 14)

**Approach suggestion:** Construct a fresh dispatch packet matching Task 13's structure: locked decisions (L*), watchpoints (W*), out-of-scope items, acceptance criteria, expected commit shape. The carry-forward item E13.1 (redundant test in `test_models_r2.py:287-300`) can be folded into Task 14's cleanup if Task 14 naturally touches that file.

**Acceptance criteria:** TBD — derive from plan section. Likely includes:
- `_project_request_to_view` raises `UnknownKindInEscalationProjection` for non-escalatable kinds (vs. current silent coercion)
- `_project_pending_escalation` switches to job-anchored lookup
- Tombstone-projection for purged rows
- `_ESCALATABLE_REQUEST_KINDS` defined
- Pyright error at `delegation_controller.py:965` resolved (A3 carry-forward closure)

**Potential obstacles:**
- Task 14 may surface additional carry-forward items if projection-helper refactor uncovers more shape-rewrite-related dead code
- C10.4 (worker-side `completion_origin`) is still open at Phase F; Task 14's projection helpers may need to coordinate with the eventual Phase F change but should NOT pre-wire it (same L5 discipline as Task 13)

**Workflow:** Use `subagent-driven-development` skill again — match Task 13's stage pipeline (implementer + spec-reviewer + code-quality-reviewer). Re-create todos for the 4-stage workflow. Use sonnet for implementer.

### 2. Carry-forward sweep candidates (later)

Three Phase E Task 13 carry-forward items + earlier-phase items naturally sweep at known landing points:

| Item | Landing point | Trigger |
|------|---------------|---------|
| E13.1 | Task 14 cleanup pass | Task 14 touches `test_models_r2.py` |
| E13.2 | Phase H | Phase H owns contracts.md + docstring trim alongside |
| E13.3 | Phase H | Phase H docstring/comment polish |
| A3 | Task 14 | Task 14's projection-helper rewrite resolves line 965 Pyright error |
| A4, B6.x, B7.x, B8.x, C10.2-C10.3 | End-of-Packet-1 polish | Per landing-point rows |
| C10.4 | Phase F worker-runner work | Worker-side provenance wiring |

No immediate action — these are deferred by design.

## In Progress

Clean stopping point — Phase E Task 13 fully complete (5 implementation/test commits + 1 closeout-docs commit at `f0ea603b`), 978 tests passing, all reviews ✅, all carry-forward items captured. No work in flight.

## Open Questions

None pending action. Two questions surfaced during review and were resolved:

1. **Should the deferred minor 5 (repeated `# Post-dispatch ... (Packet 1)` comments) become a carry-forward item?** Resolved: declined as intentional convention preservation. The per-site comments match the package's existing `# C10.4:` / `# Phase G:` markers and provide grep-ability that a single docstring would lose.

2. **Should the Phase E plan template's Task 13 checkboxes be ticked in the closeout-docs commit?** Resolved: no — matching Phase D precedent (`phase-d-registry.md` has all-unchecked boxes despite Tasks 11+12 complete). The plan is a template; the carry-forward.md is the canonical close record.

## Risks

### R1: Phase G Task 18 may re-introduce the collapsed branch (closeout-3)

**Concern:** Closeout-3 collapsed the approve-path `if isinstance(follow_up, DelegationEscalation):` branch because both arms returned identical values post-rewrite. Phase G Task 18 will rewrite `decide()` with reservation context manager + new return semantics — it may need to differentiate the approve+escalation vs. approve+completed cases at a different layer (e.g., for reservation-channel signaling).

**Mitigation:** Phase G Task 18's plan should specify what differentiation it needs. If branching is needed for Phase G reasons, it can be re-introduced — closeout-3's removal was about pre-Phase-G dead structure, not Phase G's eventual structure. Document this expectation in the Phase G dispatch packet.

**Severity:** Low — the trade-off (clean pre-Phase-G structure now, possibly re-introduced for Phase G reasons later) is the right one.

### R2: Pyright daemon cache staleness recurs in future sessions

**Concern:** Five rounds of diagnostics in this session each surfaced 5-10 pre-existing or stale-cache issues. The triage discriminator is `git diff <base> HEAD -- <file>` (inside hunk = signal; outside = noise). If a future session forgets this rule, real regressions could be lost in the noise floor.

**Mitigation:** Captured in the dispatch packet pattern — every Task 13-style dispatch should include "Pyright noise vs. real regression triage" as a reviewer instruction. The discriminator rule generalizes.

**Severity:** Medium — recurring noise floor, but the rule works.

### R3: Carry-forward accumulation if late-phase landing points don't trigger

**Concern:** E13.2 and E13.3 are slated for Phase H. If Phase H's contracts.md scope doesn't naturally touch the docstring or `decision_accepted` comment, they become orphans.

**Mitigation:** Phase H plan should explicitly absorb these. If Phase H scope is too narrow, sweep them as end-of-Packet-1 polish.

**Severity:** Low — ~3 items max, tracked, with explicit landing points.

## References

- **Branch:** `feature/delegate-deferred-approval-response` @ `f0ea603b`
- **Phase E plan:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-e-serialization-projection.md`
- **Carry-forward tracker:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md`
- **Design spec:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`
- **Phase D Task 12 closeout-docs (style reference):** `bf3f8b19`
- **Phase D Task 11 closeout-fix (F4 Path D pattern, style reference):** `8d4f9b96`
- **Prior session handoff (resumed_from):** `docs/handoffs/archive/2026-04-25_01-51_phase-d-complete-phase-e-next.md`
- **Phase G plan (Task 18 owns async decide() rewrite):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md` — Task 17 = `start()`, Task 18 = `decide()`
- **Phase F plan (worker-runner; C10.4 lands here):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md`
- **Phase H plan (contracts.md + docstring trim):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-h-finalizer-consumers-contracts.md`

## Learnings

### L1: Shape-rewrite tasks have a generalizable dead-binding trap

**Mechanism:** When a dataclass shape is reduced (e.g., 5 fields → 3 fields), every local binding or conditional branch that existed solely to extract attributes from the old shape becomes orphaned. Python doesn't error on unused bindings; tests pass at runtime; the dead code lingers until type-checker or review surfaces it.

**Evidence:** Task 13 surfaced this in two arms separately — closeout-1 (`updated_job =` in deny path) and closeout-3 (`follow_up =` + `if isinstance(follow_up, DelegationEscalation):` in approve path). Each was caught by a different review pass.

**Implications:** Future shape-rewrite tasks should include an explicit "what was this binding/branch for?" audit pass during the feat commit. The audit question: for every local variable assignment and conditional branch in the rewritten function, what consumer reads it? If the only consumer was the old constructor call, the binding/branch is dead.

**Watch for:** Symmetric arms of conditional logic. If one arm has dead code, the other arm probably does too.

### L2: Pyright daemon cache staleness has a deterministic discriminator

**Mechanism:** When Pyright reports a class field doesn't exist, but the file on disk has the field defined and runtime tests pass, the daemon's cache is stale. The cache lags behind file edits.

**Evidence:** Task 13's first diagnostics round showed `test_delegation_decision_result_shape.py:16-31` reporting old shape errors; verified `models.py:457-472` had the new shape on disk; verified suite was green at 978. Stale cache, not real regression.

**Discriminator:** `git diff <base> HEAD -- <file>` — if the diagnostic line is inside a Task hunk, it's potentially real; if outside, it's noise (pre-existing or stale-cache).

**Implications:** Every multi-file shape-rewrite task should triage diagnostics through this rule. The rule is portable across IDEs (works for any type-checker with caching).

**Watch for:** Line-number shifts after the rewrite. If a known pre-existing diagnostic surfaces at `old_line + N` after the edit, it shifted with the added lines (still pre-existing, not regressed).

### L3: Two-stage review converges with independent verification

**Mechanism:** The subagent-driven-development workflow runs spec compliance review (verifies spec match) followed by code quality review (verifies cleanness). Each catches different defect classes.

**Evidence:** Task 13's spec review found nothing (correctly — implementation matched spec); code review found 2 Important issues (vestigial branch + misnamed file) that the implementer's self-review missed. After closeouts, an independent third-party verification pass agreed: "None. I found no correctness, boundary, or test-honesty issues."

**Implications:** Two-stage review's coverage matches independent verification's coverage. The cost (extra subagent invocations) buys real defect-density reduction. Trust the convergence: if both stages plus independent verification agree, the artifact is ready to merge.

**Watch for:** Single-stage review (e.g., only code quality, no spec compliance) loses coverage on "did the implementer build the right thing?" Spec review caught zero this round, but its zero-finding is itself signal.

### L4: Closeout-docs commit pattern matches across phases

**Mechanism:** Each task's closeout sequence is `feat(...)` + N `fix(...)` closeouts + `docs(...)` closeout-docs commit. The docs commit only touches `carry-forward.md` (deferred minors → Open items, completed work → Closed items). Plan templates stay unchecked.

**Evidence:** Phase D Task 11 (`8d4f9b96` closeout-fix + `04421cba` closeout-docs), Phase D Task 12 (`becbb124` closeout-fix + `bf3f8b19` closeout-docs), Phase E Task 13 (`7b85b503/1187e8c4/da46efa9/e9955ec7` closeout-fixes + `f0ea603b` closeout-docs).

**Implications:** Future tasks in this Packet should match the pattern. Discrepancies (e.g., updating the plan template's checkboxes) deviate from precedent and should be flagged.

**Watch for:** Task 13's 5-commit closeout chain (longer than canonical 3-commit shape) is acceptable when iterative review surfaces multiple closeout-worthy issues. Don't squash to 3 commits artificially.

## Gotchas

### G1: `decide()` parameter scope vs. local binding scope

When rewriting result-shape construction sites, parameters in scope (`job_id`, `request_id`) are usable directly — no need to bind locally. Pre-Packet-1 code had `updated_job = self._persist_job_transition(job_id, "failed")` because it needed `updated_job.X` in the constructor. After 3-field shape reduction, `job_id` (the parameter) is sufficient. Don't preserve local bindings whose only consumer was the old constructor.

### G2: `controller.poll()` is a discriminated union

Tests that migrate from `decide()` return-shape assertions to `poll()` calls must narrow the union before attribute access. The package convention: `assert isinstance(poll, DelegationPollResult)`. Match `:1705` and `:2514` patterns. Pyright will catch missing narrowing; runtime tests will pass without it (because the success branch is hit in those scenarios) — but type hygiene requires the assert.

### G3: `_integration.py` filename is a load-bearing convention

In this package, files named `test_<thing>_integration.py` specifically drive `server.handle_request(...)` end-to-end. Don't squat the convention with a unit test that just calls `asdict()` or constructs a fake. Code reviewers and PR readers use the suffix to triage MCP-boundary coverage.

### G4: Plan templates have permanent unchecked boxes

`phase-d-registry.md` and `phase-e-serialization-projection.md` have `- [ ]` checkboxes that stay unchecked even after task closure. The plan is a template-form artifact; the carry-forward.md is the canonical "what was actually closed" record. Don't tick checkboxes in closeout-docs commits — match precedent.

### G5: `# Phase G:` deferral comments must name a specific observable

If you must defer a test assertion to Phase G (because the assertion is timing-bound rather than observable-state), the comment must name the concrete Phase G observable to assert later. Example: `# Phase G: assert reservation channel signals capture-ready before this point`. A bare `# Phase G: defer` is incomplete and creates orphan work.

### G6: F4-pattern docstring-runtime mismatch is a recurring trap

Phase D Task 11's closeout (`8d4f9b96`) corrected a `ReservationToken.generation` docstring that advertised a contract not delivered until the closeout fix. Phase E Task 13's docstring is shape-only deliberately to avoid the same trap — the W7 watchpoint guarded against drift toward Phase G timing language. Future task docstrings should be audited against this pattern: does the docstring describe the current implementation, or does it describe a future implementation?

### G7: Carry-forward landing points must be plan-anchored

Every carry-forward item has a "Lands at / How to resolve" column. Items without a plan-anchored landing point (e.g., "End-of-phase polish" only) become orphans if no phase ever sweeps them. Task 13's E13.1-E13.3 each have specific landing points (Task 14, Phase H, Phase H) — that's the right shape.
