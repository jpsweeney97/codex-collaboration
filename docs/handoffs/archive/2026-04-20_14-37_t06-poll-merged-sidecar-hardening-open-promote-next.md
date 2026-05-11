---
date: 2026-04-20
time: "14:37"
created_at: "2026-04-20T18:37:00Z"
session_id: 050b3b25-7bf4-4ffc-ba51-f6374cace9ae
resumed_from: "docs/handoffs/archive/2026-04-20_13-30_t06-delegate-poll-implemented-pr-open.md"
project: claude-code-tool-dev
branch: main
commit: 8bae4dde
title: "T-06 poll merged, sidecar hardening open, promote design next"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/artifact_store.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/consultation_safety.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_artifact_store.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_consultation_safety.py
---

# T-06 Poll Merged, Sidecar Hardening Open, Promote Design Next

## Goal

Resume from the prior session's completed implementation of `codex.delegate.poll`, address PR review feedback, run a comprehensive 5-agent review, fix all findings, merge PR #111, then prepare for the next T-06 slice (`codex.delegate.promote`).

**Trigger:** Handoff from prior session said: "Next action for next-session Claude: Check PR #111 status. If approved, merge. After merge, begin promote implementation."

**Stakes:** `codex.delegate.poll` gates the entire promote/verify/apply pipeline. Without it merged, no further T-06 progress is possible. The sidecar hardening items close gaps identified during poll review that would otherwise be carried as tech debt into the promote slice.

**Success criteria (all met):**
1. PR #111 reviewed, all findings addressed, merged to main — done at `8bae4dde`
2. Sidecar hardening PR opened — PR #112 on `chore/t06-sidecar-hardening`
3. Promote sequencing agreed and documented — promote + discarded + rollback + stale-context first, then delegate skill UX
4. PendingEscalationView projection change excluded from sidecar chore — deferred to post-promote pre-skill window

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. T-06 decide merged at `e041c896` (PR #109). Spec amendments merged at `db7fd1da` (PR #110). Poll now merged at `8bae4dde` (PR #111). Remaining T-06 ACs: promote, rollback, stale-context invalidation, delegate skill UX.

## Session Narrative

**Phase 1 — Handoff load and PR review comments (~10 min).** Loaded the prior handoff (`2026-04-20_13-30`). Checked PR #111 status: open, mergeable state clean, 1447 additions across 18 files. Found 2 review comments from the Codex connector bot. Invoked the `receiving-code-review` skill to handle them properly.

Evaluated both comments against the actual code:
- **Comment 1 (P1):** Malformed `test-results.json` in `_test_results_record` causes `JSONDecodeError` propagation. Verified valid — `json.loads` at `artifact_store.py:242` had no error handling. The file-missing path returned a safe stub but file-exists-but-corrupt didn't. Fixed by wrapping `json.loads` in `except (JSONDecodeError, ValueError)` with a `"malformed"` stub.
- **Comment 2 (P2):** `reconstruct_from_artifacts` returns snapshot when `changed-files.json` is absent. Pushed back — the file-existence guard at lines 101-107 already prevents this. All canonical artifact files must exist before the manifest loop is reached. The reviewer missed the early-return guard.

Replied to both on the PR (accepted #1 with fix, pushed back on #2 with technical reasoning). Committed fix at `63da9604`, pushed.

**Phase 2 — Comprehensive 5-agent PR review (~15 min).** Launched all 5 review agents in parallel: code-reviewer, test-analyzer, error-hunter, type-analyzer, comment-analyzer. Results:

- **Code reviewer:** No high-confidence issues. Clean implementation.
- **Test analyzer:** 2 critical gaps (failed/unknown poll paths untested, no JSONL replay corruption tests), 3 important improvements.
- **Error hunter:** 3 HIGH (unguarded subprocess in poll, `_test_results_record` missing `OSError`, silent swallow in reconstruct), 4 MEDIUM (no subprocess timeout, silent `load_snapshot`, reconstruction failure detail, `update_artifacts` validation).
- **Type analyzer:** Strong design overall. Main findings: `DelegationPollResult` field validity not documented, `DelegationJobStore.update_status` still public despite no remaining callers.
- **Comment analyzer:** 2 critical (stale module/class docstrings missing "poll", misleading "manifest file" in docstring), 3 improvements (stale comments), 2 removals (restating-obvious docstrings).

**Phase 3 — User triage of findings (~5 min).** User reviewed the aggregate and triaged:

- **Kept:** #1 (unguarded subprocess — corrected to 4 `check=True` + 1 `check=False`), #2 (`_test_results_record` missing `OSError`).
- **Demoted:** #3 (silent swallow → intentional, tested), #4 (failed/unknown tests → overstated, `artifact_hash=None` already covered at store level), #5 (replay corruption → quality improvement not blocking).
- **Comments:** #6-8, #18 kept as cleanup, not merge-blocking.
- **Suggestions:** User considered #11 (reconstruction failure detail) worth doing in this PR, #17 (deprecate `update_status`) deferred to promote slice.

**Phase 4 — Fix implementation (~10 min).** Implemented all agreed fixes in commit `c5a29e15`:
- Wrapped `_load_or_materialize_inspection` in `poll()` with `except (CalledProcessError, OSError)` guard
- Added `OSError` to `_test_results_record` except clause
- Set diagnostic detail when `inspection is None` and `artifact_hash is not None`
- Updated all stale comments/docstrings (4 locations)
- Added 2 new tests

**Phase 5 — User found remaining gap (~5 min).** User reviewed commit `c5a29e15` and found: the diagnostic detail branch only fires when `artifact_hash` is already non-None. For a completed job whose first-ever materialization fails (worktree deleted before first poll), callers still get `completed + inspection=None + detail=None`. The test asserted `inspection is None` but didn't assert `detail is not None`.

Fixed with `materialization_failed` flag in the except block, distinct detail string ("Artifact materialization failed — worktree may have been deleted or is unreachable."), and tightened test assertion. Commit `a8088e2c`. User confirmed clean: "No findings."

**Phase 6 — Merge and cleanup (~3 min).** Merged PR #111 via `gh pr merge`. Pulled main to `8bae4dde`. Removed worktree at `../claude-code-tool-dev-poll`. Deleted feature branch. Updated memory.

**Phase 7 — Promote sequencing discussion (~5 min).** User laid out the next T-06 work: promote is not "just add one more MCP method" — it includes prechecks, regenerate-and-compare hash verification, rollback, stale advisory context marking, and typed rejection responses. User asked for agreement on sequencing:

Agreed on: promote + discarded + rollback + stale-context first, delegate skill UX after. Two nuances raised:
1. `discarded` should be in the promote packet (low complexity, completes action vocabulary, prevents skill UX from targeting incomplete surface).
2. Sidecar hardening items split into parallel-now (3 items) vs defer (1 item — `PendingEscalationView` projection is an API-shape change, not cleanup).

**Phase 8 — Sidecar hardening chore PR (~15 min).** Created `chore/t06-sidecar-hardening` branch. Implemented 3 hardening items:
1. `DELEGATE_START_POLICY` in `consultation_safety.py` — closes the pre-existing fail-closed gap where `codex.delegate.start` had no policy entry.
2. 3 MCP-layer malformed-answers rejection tests for `codex.delegate.decide`.
3. Approve-path finalization guard regression test (twin of the existing deny-path test). Initial attempt failed because `_FakeSession` re-fired the command_approval_request on the follow-up turn, keeping the job at `needs_escalation`. Fixed by clearing `session._server_requests` after `start()`.

All 771 tests passing. Pushed and opened PR #112.

## Decisions

### Decision 1: Accept P1, push back on P2 from Codex reviewer

**Choice:** Accepted Comment 1 (malformed `test-results.json` fix) and pushed back on Comment 2 (`reconstruct_from_artifacts` missing manifest guard).

**Driver:** Verified both claims against the actual code. Comment 1 identified a real unhandled error path. Comment 2 missed the file-existence guard at lines 101-107 that prevents the described scenario.

**Alternatives considered:**
- **Accept both** — would add a redundant check inside the manifest loop that is already structurally prevented. Rejected because the guard is already comprehensive and adding a second check would imply the first is insufficient.
- **Reject both** — Comment 1 was clearly valid (bare `json.loads` with no error handling on an external-process-written file). Rejected.

**Trade-offs accepted:** Pushing back on an automated reviewer risks the finding being re-raised. Mitigated by providing the specific line-number evidence for the existing guard.

**Confidence:** High (E2) — verified both code paths by reading the relevant functions and tracing the execution flow.

**Reversibility:** High — if the reviewer provides a counter-example that bypasses the guard, adding the check is trivial.

**Change trigger:** If `artifact_paths` is ever constructed without `changed-files.json` as a canonical member.

### Decision 2: Track `materialization_failed` flag for first-time poll failures

**Choice:** Added a `materialization_failed` boolean flag in the `poll()` except block to distinguish first-time materialization failures from missing artifacts on previously-reviewed jobs.

**Driver:** User review found that the initial fix (checking `artifact_hash is not None`) only covered previously-reviewed jobs. For first-time failures, the result was the ambiguous `completed + inspection=None + detail=None` shape. User: "First-time materialization failures on completed jobs are still not explained to the caller."

**Alternatives considered:**
- **Set detail inside the except block directly** — simpler but would be overridden by the status-based detail logic for failed/unknown jobs. Rejected because the ordering of detail assignment matters.
- **Merge both conditions into a single check** — `if inspection is None and (artifact_hash is not None or materialization_failed)` with a single message. Rejected because the two states have different meanings and should have distinct messages.

**Trade-offs accepted:** Two distinct detail messages for inspection unavailability adds API surface. Accepted because the distinction is meaningful to callers — "artifacts deleted" vs "worktree unreachable" suggest different remediation paths.

**Confidence:** High (E2) — user verified the fix and confirmed "No findings."

**Reversibility:** High — remove the flag and the `elif` branch.

**Change trigger:** If the poll result contract is redesigned to use structured error envelopes instead of string details.

### Decision 3: Include `discarded` in promote packet

**Choice:** Bundle `discarded` state transition with `codex.delegate.promote` in the same implementation slice.

**Driver:** User reasoning: "it completes the action vocabulary at low complexity cost, and it prevents the delegate skill from being designed against a knowingly incomplete execution surface."

**Alternatives considered:**
- **Separate follow-up** — would leave the skill UX targeting an incomplete action surface where completed jobs can only be promoted, not discarded. Rejected because: "If it ships separately, the delegate skill UX has to be designed around a temporarily incomplete surface, then revised."

**Trade-offs accepted:** Slightly larger promote PR scope. Accepted because `discarded` is a lightweight state transition with no worktree operations or hash verification.

**Confidence:** High (E1) — user explicitly stated the reasoning and confirmed agreement.

**Reversibility:** High — `discarded` is a terminal promotion_state value with no downstream dependencies.

**Change trigger:** If `discarded` turns out to require worktree cleanup or artifact deletion, it becomes more complex than expected.

### Decision 4: Split sidecar hardening into parallel-now vs defer

**Choice:** Three items land as a chore PR now (`codex.delegate.start` safety policy, malformed-answers rejection tests, approve-path finalization guard). One item deferred: `PendingServerRequest` → `PendingEscalationView` projection for start/decide.

**Driver:** User: "That is not just cleanup. It is an externally visible API-shape change ... and the contract already flags it as an unresolved hardening sidecar." The projection change "directly affects the surface the future delegate skill will consume."

**Alternatives considered:**
- **All 4 in the chore PR** — would churn the delegate-facing response contract before the skill UX is designed. User rejected: "avoids churning the delegate-facing response contract twice."
- **Defer all 4** — the safety policy gap, malformed-answers tests, and finalization guard are truly independent of promote design. User: "These are real hardening items, and they are largely orthogonal to promote design."

**Trade-offs accepted:** The safety policy gap continues to exist on `main` until PR #112 merges. The projection change remains an open sidecar until post-promote.

**Confidence:** High (E1) — user explicitly triaged each item with reasoning.

**Reversibility:** High — PR #112 is independent; the projection change can land whenever.

**Change trigger:** If the promote implementation needs the projection change as a prerequisite.

## Changes

### PR #111 — Additional commits this session (3 commits pushed, merged)

| Commit | What changed |
|--------|-------------|
| `63da9604` | `_test_results_record`: wrap `json.loads` in `except (JSONDecodeError, ValueError)` with `"malformed"` stub. New test: `test_malformed_test_results_produces_stub`. |
| `c5a29e15` | `poll()`: `try/except (CalledProcessError, OSError)` around `_load_or_materialize_inspection`. `_test_results_record`: add `OSError` to except. Diagnostic detail when `inspection=None` and `artifact_hash is not None`. 4 stale comment/docstring updates. 2 new controller tests. |
| `a8088e2c` | `poll()`: `materialization_failed` flag for first-time failures. Distinct detail string. Tightened test assertion on detail content. |

### PR #112 — Sidecar hardening (1 commit, open)

| Commit | What changed |
|--------|-------------|
| `4fff33b0` | `DELEGATE_START_POLICY` in `consultation_safety.py` with `_TOOL_POLICY_MAP` entry. 2 safety policy tests (lookup + objective scan). 3 MCP malformed-answers rejection tests. 1 approve-path finalization guard regression test. |

### Modified production files (this session)

| File | What changed |
|------|-------------|
| `server/artifact_store.py` | `_test_results_record` error handling: `except (JSONDecodeError, ValueError, OSError)` with malformed/unreadable stub. `reconstruct_from_artifacts` docstring: "manifest file" → "artifact_paths is empty or any artifact file is missing". |
| `server/delegation_controller.py` | Module docstring + class docstring: added "codex.delegate.poll". `poll()`: subprocess/OSError guard with `materialization_failed` flag, two-branch diagnostic detail. Stale comment updates (line 42: `update_status` → `_persist_job_transition`, line 49: turn-dispatch journaling deferred). |
| `server/consultation_safety.py` | New `DELEGATE_START_POLICY` (expected: `repo_root`, `base_commit`; content: `objective`). Added to `_TOOL_POLICY_MAP`. |

### Modified test files (this session)

| File | Tests added | What changed |
|------|-------------|-------------|
| `tests/test_artifact_store.py` | 1 | `test_malformed_test_results_produces_stub` |
| `tests/test_delegation_controller.py` | 3 | `test_poll_returns_structured_result_when_materialization_raises`, `test_poll_sets_detail_when_artifacts_unavailable_for_reviewed_job`, `test_decide_approve_post_turn_journal_failure_raises_committed_decision_finalization_error` |
| `tests/test_mcp_server.py` | 3 | `test_decide_rejects_non_dict_answers`, `test_decide_rejects_malformed_answer_entry`, `test_decide_rejects_non_string_answer_values` |
| `tests/test_consultation_safety.py` | 2 | `test_delegate_start_returns_start_policy`, `test_delegate_start_scans_objective_field` |

## Codebase Knowledge

### Files Read This Session

| File | Lines | Why read | Key finding |
|------|-------|----------|-------------|
| `artifact_store.py` | 253→262 | Verify Codex reviewer claims, fix error handling | `_test_results_record` had no error handling on `json.loads` for external-process-written files. `reconstruct_from_artifacts` has a two-layer defense: file-existence guard (101-107) then malformed-manifest catch (116). |
| `delegation_controller.py` | 1325→1360 | Fix poll error handling, update stale comments | `logger` (not `_log`) is the module-level logger. `_execute_live_turn` has two except branches: turn failure and finalization failure, both calling `_mark_execution_unknown_and_cleanup`. The approve-decide path calls `write_phase` 3 times: intent, dispatched, completed. |
| `consultation_safety.py` | 191 lines | Add `codex.delegate.start` policy | `_TOOL_POLICY_MAP` had 5 entries (consult, dialogue.start, dialogue.reply, delegate.decide, delegate.poll). `codex.delegate.start` was the only delegation tool missing. `policy_for_tool` raises `KeyError` for unknown tools → `codex_guard.py` catches as exit 2 (fail-closed). |
| `mcp_server.py` | 387→447 | Understand answers normalization for malformed-answers tests | Answer validation at lines 397-427: 4 `ValueError` paths (non-dict top-level, non-string keys, wrong entry shape, non-string values). `_handle_tools_call` catches `Exception` at line 314 and returns `isError: True`. |
| `test_delegation_controller.py` | ~2400 | Add poll and finalization tests | `_FakeSession._server_requests` persists across turns — the follow-up turn re-fires requests unless cleared. `_FakeControlPlane._next_session_requests` copies to session at creation. `_build_controller` returns 8-tuple. |

### Architecture: Poll Error Handling (Updated)

```
caller → MCP "codex.delegate.poll" {job_id}
  → mcp_server.py: dispatch to controller.poll()
    → TRY _load_or_materialize_inspection(job)
        → cache hit: return existing
        → cache miss + hash exists: reconstruct_from_artifacts()
        → cache miss + no hash: materialize_snapshot()
            → 4x subprocess.run(check=True) + 1x check=False
    EXCEPT (CalledProcessError, OSError):
        → logger.warning, inspection=None, materialization_failed=True
    
    → Detail assignment (ordered by specificity):
        1. status-based: "failed" or "unknown" → operational guidance
        2. artifact_hash present + inspection=None → "artifacts unavailable"
        3. materialization_failed + inspection=None → "materialization failed"
    
    → return DelegationPollResult or PollRejectedResponse
  → mcp_server.py: asdict(result) → JSON-RPC response
  EXCEPT Exception: → isError text (raw exception, no typed response)
```

### Safety Policy Map (Updated)

`consultation_safety.py` now has 6 entries in `_TOOL_POLICY_MAP`:
- `codex.consult` → CONSULT_POLICY
- `codex.dialogue.start` → DIALOGUE_START_POLICY
- `codex.dialogue.reply` → DIALOGUE_REPLY_POLICY
- `codex.delegate.start` → DELEGATE_START_POLICY (NEW — scans `objective`)
- `codex.delegate.decide` → DELEGATE_DECIDE_POLICY
- `codex.delegate.poll` → DELEGATE_POLL_POLICY

### `_FakeSession` Behavior Across Turns

`_FakeSession._server_requests` is set once at session creation from `_FakeControlPlane._next_session_requests`. The list persists across `run_execution_turn` calls — every turn re-fires the same requests. For tests where the follow-up turn should complete cleanly (no re-escalation), clear `session._server_requests = []` between the start and decide calls. Discovered when the approve-finalization test failed because the follow-up turn re-escalated.

## Context

### Mental Model

This session was **review-driven hardening of a completed implementation.** The poll code was already implemented and reviewed in the prior session (3 rounds of manual review caught 5 cross-cutting defects). This session's work was additive: automated multi-perspective review to find what manual review missed, user triage to separate real findings from noise, and targeted fixes.

The key pattern: automated review agents catch different categories than manual review. The code-reviewer (correctness) found nothing — the manual review had already fixed all correctness bugs. The error-hunter found unguarded system boundaries. The test-analyzer found coverage gaps. The comment-analyzer found stale docs. These are hardening categories, not design categories.

### Why This Session Matters

PR #111 is the last read-only inspection tool in the delegation pipeline. With poll merged, the full delegation lifecycle is: `start → (escalate → decide)* → poll → promote → verify → apply`. The promote slice is the first write operation — it applies the delegated agent's work to the codebase. Everything before poll is preparation; everything after is commitment.

### Project State

- **T-05:** COMPLETE. Both slices merged to main at `271f23aa`. 698 tests.
- **T-06 decide:** COMPLETE AND MERGED at `e041c896`. 734 tests.
- **T-06 spec amendments:** COMPLETE AND MERGED at `db7fd1da` (PR #110). Docs-only.
- **T-06 poll:** COMPLETE AND MERGED at `8bae4dde` (PR #111). 765 tests.
- **T-06 sidecar hardening:** PR #112 OPEN on `chore/t06-sidecar-hardening`. 771 tests.
- **Next T-06 slices:** promote (+ discarded + rollback + stale-context), delegate skill UX.

## Learnings

### Automated review agents and manual review catch orthogonal defect categories

**Mechanism:** The 5-agent review launched in parallel found 20+ findings, but the code-reviewer (bugs/correctness) found zero high-confidence issues. The prior session's manual review had already caught all correctness defects. The automated agents found: unguarded system boundaries (error-hunter), coverage gaps (test-analyzer), stale documentation (comment-analyzer), and type design observations (type-analyzer). These are hardening categories that manual spec-focused review doesn't target.

**Evidence:** 5 manual review findings in prior session (all P1-P2 correctness). 0 code-reviewer findings this session. 8 error-hunter + test-analyzer findings (all hardening). Pattern: manual review catches cross-cutting spec violations; automated review catches per-file quality gaps.

**Implication:** For spec-critical implementations like promote, the review pipeline should be: subagent per-task review (catches 80% implementation issues) → manual review against authority docs (catches spec violations) → automated multi-agent review (catches hardening gaps). Each layer catches what the others miss.

### `_FakeSession._server_requests` persists across turns — must clear for clean follow-up

**Mechanism:** `_FakeControlPlane.start_execution_runtime` copies `_next_session_requests` to `session._server_requests` at creation time. The list is not cleared between `run_execution_turn` calls. Every turn re-fires the same requests via the `_server_request_handler` callback.

**Evidence:** The approve-finalization guard test failed because the follow-up turn re-fired `_command_approval_request()`, causing re-escalation instead of clean completion. The test expected `job.status in ("completed", "unknown")` but got `needs_escalation`.

**Implication:** Any test that calls `decide(approve)` after a `start()` that used `_next_session_requests` must explicitly clear `session._server_requests = []` before the decide call to prevent the follow-up turn from re-escalating.

### First-time poll failure is a distinct error state from "previously reviewed, artifacts lost"

**Mechanism:** The initial fix for poll error handling checked `artifact_hash is not None` to detect "artifacts unavailable." But `artifact_hash` is `None` for jobs that have never been polled — first-time materialization failures produced the ambiguous `completed + inspection=None + detail=None` shape. The fix: track whether the except block fired (`materialization_failed` flag) and assign a distinct detail.

**Evidence:** User review of commit `c5a29e15` identified the gap. The test at the time asserted `inspection is None` but not `detail is not None`, so the gap was untested.

**Implication:** When adding error recovery paths, consider all states that lead to the recovery: "never attempted" vs "previously succeeded but now failed" may require distinct handling even though the recovery outcome (None/fallback) is the same.

## Next Steps

### 1. Merge PR #112 (sidecar hardening)

**Dependencies:** PR review approval.

**What to do:** Check PR #112 status. If approved, merge and clean up. This is independent of promote work and can happen in parallel.

### 2. Read-first design/reconciliation packet for `codex.delegate.promote`

**Dependencies:** Poll merged (done). Sidecar hardening merge is independent.

**What to read first:**
- `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` — hash recipe, materialization, verification, prechecks
- `docs/superpowers/specs/codex-collaboration/contracts.md` — poll result contract shape that promote consumes
- `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` — remaining ACs
- `docs/superpowers/specs/codex-collaboration/foundations.md` — high-level flow

**Scope (confirmed with user):** promote + discarded + rollback + stale advisory context marking. Includes: HEAD/base-commit/index/worktree prechecks, typed rejection responses, regenerate-and-compare artifact hash, promotion-state transitions, rollback-needed and rolled-back behavior, stale advisory context marking, discarded as terminal state.

**Explicit exclusion:** delegate skill UX is a separate slice after promote.

**Decision needed:** Whether `discarded` lands in the same PR as promote or as a tight follow-up. User recommended same PR; this Claude agreed.

### 3. Land PendingEscalationView projection change (post-promote, pre-skill)

**Dependencies:** Promote merged.

**What to do:** Scrub start/decide response shapes to project `PendingServerRequest` through `PendingEscalationView` (strip internal IDs, use plugin-level decisions). User recommended: "land it immediately after promote and before skill UX if you want the skill to target the cleaned-up response shape."

## In Progress

**Clean stopping point.** All implementation done, both PRs pushed, no code changes in flight.

- **Completed:** PR #111 merged to main at `8bae4dde`. PR #112 open with 1 commit.
- **Not in flight:** No uncommitted changes (aside from pre-existing local modification to `test_execution_prompt_builder.py`).
- **Next action for next-session Claude:** Check PR #112 status. If approved, merge. Then begin the read-first design packet for `codex.delegate.promote`.

## Open Questions

### 1. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** Handler calls `entry.session.interrupt_turn()` from inside `_server_request_handler`. Sends `turn/interrupt` via same transport reading notifications.

**Decision pending until:** Live testing against real App Server.

### 2. `on-request` operational semantics (inherited from T-05)

**Context:** Vendored schema proves `on-request` is a valid `approvalPolicy` value but operational semantics undocumented. Controller defaults to `untrusted`.

**Decision pending until:** Live probe against real App Server.

### 3. Test-results persistence in execution runtime (inherited from poll)

**Context:** The execution prompt instructs the agent to persist at `.codex-collaboration/test-results.json`. If the agent ignores this, all jobs degrade to `"not_recorded"` stubs (now also `"malformed"` for corrupt files). The deterministic fallback ensures poll works, but the promote hash includes the stub content.

**Decision pending until:** Live execution testing with the amended prompt.

## Risks

### 1. `_decided_request_ids` is in-memory only (inherited)

If cross-session decide is added, the in-memory set won't persist across restarts. For same-session-only design, this is correct.

### 2. `_FakeSession` complexity continues to grow (inherited)

The fake session has multiple methods and configurable state. `_server_requests` persistence across turns is a subtle behavior that caused a test failure this session. Drift from real `AppServerRuntimeSession` interface could mask production failures.

### 3. Pre-existing local modification to `test_execution_prompt_builder.py`

The git status shows `M packages/plugins/codex-collaboration/tests/test_execution_prompt_builder.py` on main. This was present at session start and was excluded from the chore PR commit. Origin unknown — may be from a prior session's uncommitted work.

### 4. `DelegationJobStore.update_status` still public (deferred)

The method has no remaining callers for status transitions in the controller (all 7 sites now use `_persist_job_transition` → `update_status_and_promotion`), but it remains on the public API. Direct call for `"completed"` would strand `promotion_state=None`. Deferred to promote slice for docstring warning or deprecation.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| Poll implementation plan | `docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md` | Implementation authority (poll) |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Schema authority |
| Promotion protocol | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | Hash recipe, materialization, verification |
| Foundations | `docs/superpowers/specs/codex-collaboration/foundations.md` | High-level flow |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-20_13-30_t06-delegate-poll-implemented-pr-open.md`
- T-05/T-06 arc: execution-start → pending-request capture → T-05 closed → T-06 decide plan → T-06 decide implemented → T-06 decide merged → T-06 poll spec amendments → T-06 poll plan scrutinized → T-06 poll implemented → **T-06 poll merged + hardening (this handoff)**

### PR chain

| PR | Title | Status |
|----|-------|--------|
| #109 | T-06 decide opening slice | Merged (`e041c896`) |
| #110 | Spec amendments for codex.delegate.poll | Merged (`db7fd1da`) |
| #111 | feat(t20260330-06): implement codex.delegate.poll | Merged (`8bae4dde`) |
| #112 | chore(t20260330-06): sidecar hardening for delegation tools | **Open** (`4fff33b0`) |

### Commit chain on PR #111 (final, merged)

| Commit | Message |
|--------|---------|
| `f781c4c4` | feat(t20260330-06): pin poll model and job-store contract |
| `bebe3705` | feat(t20260330-06): add delegation poll artifact materialization |
| `9e360b01` | feat(t20260330-06): implement delegation poll controller flow |
| `8e7dee37` | feat(t20260330-06): wire codex delegate poll mcp surface |
| `ddf90a96` | fix(t20260330-06): hash sort order, plugin-level decisions, corrupt snapshot resilience |
| `ae480a92` | fix(t20260330-06): guard reviewed hash from corrupt-cache rematerialization |
| `a8ab1ca1` | fix(t20260330-06): validate artifact files before reconstruction |
| `63da9604` | fix(t20260330-06): tolerate malformed test-results.json during materialization |
| `c5a29e15` | fix(t20260330-06): harden poll error handling, add diagnostic detail, update stale comments |
| `a8088e2c` | fix(t20260330-06): diagnostic detail for first-time materialization failures |

## Gotchas

### 1. `_FakeSession._server_requests` persists across turns

**Symptom:** Approve-path finalization guard test fails with `assert job.status in ("completed", "unknown")` getting `needs_escalation`.

**Root cause:** `_server_requests` is copied from `_FakeControlPlane._next_session_requests` at session creation. The list persists across `run_execution_turn` calls. The follow-up turn (triggered by decide approve) re-fires the same requests, causing re-escalation.

**Prevention:** Clear `session._server_requests = []` between `start()` and `decide()` in tests where the follow-up turn should complete cleanly.

### 2. First-time materialization failure needs a distinct detail from "artifacts lost"

**Symptom:** Completed job with `inspection=None` and `detail=None` after worktree deletion before first poll.

**Root cause:** The `artifact_hash is not None` check only catches previously-reviewed jobs. First-time failures have `artifact_hash=None`.

**Prevention:** `materialization_failed` flag in the except block, with a distinct detail message. Test asserts `detail is not None` and content match.

### 3. Error-hunter reported 5 `check=True` subprocesses — actual count is 4+1

**Symptom:** Review finding overstated the blast radius of the subprocess guard.

**Root cause:** `_full_diff` line 222 uses `check=False` (for `git diff --no-index` which returns exit code 1 for differences). The other 4 calls use `check=True`.

**Prevention:** When evaluating automated review findings, verify claims against the code before implementing fixes. The correction changed nothing about the fix approach but is important for accurate documentation.

## Conversation Highlights

### User's triage of automated review findings

User reviewed the 20+ findings from the 5-agent review and applied sharp triage: "Keep" for genuine gaps, "Demote" for findings that are intentional or overstated, and a clear separation of "suggestions" from "findings." The demotions were evidence-based — e.g., "#3 demote. The 'silent swallow' ... is now intentional degradation, not an unreviewed bug. The branch explicitly codifies 'malformed manifest => changed_files=()' in test_reconstruct_handles_malformed_manifest."

### User's sequencing reasoning for promote

User laid out that promote "is not just 'add one more MCP method'" and specified the full scope: "This packet should include the load-bearing parts, not defer them: HEAD/index/worktree prechecks, typed rejection responses, regenerate-and-compare artifact hash, promotion-state transitions, rollback-needed and rolled-back behavior, and stale advisory context marking on successful promotion."

### User's sidecar split rationale

User split the 4 sidecar items: "The PendingEscalationView projection is not just cleanup. It is an externally visible API-shape change ... and the contract already flags it as an unresolved hardening sidecar." Versus the other 3: "These are real hardening items, and they are largely orthogonal to promote design."

## User Preferences

### Evidence-first review reception

User provides findings with full evidence chains: exact file:line references, links to authority documents, reproduction evidence, and confidence ratings. Expects the same density in responses. Corrections are structured as `::code-comment` annotations with priority and confidence.

### Triage discipline over comprehensive fixing

User does not fix everything — triages findings by whether they represent broken behavior vs quality improvements, and whether they block merge. Demoted findings (#3, #4, #5) were all "quality improvement, not evidence of broken behavior." Only genuine gaps (#1, #2) and agreed-upon improvements (#11) were fixed.

### Read-first design over implementation-first

User explicitly called for "a read-first design/reconciliation packet for codex.delegate.promote" rather than jumping to implementation. The promote slice is treated as a design challenge, not just another MCP method.

### Iterative hardening over scope expansion

Consistent with the prior session: each fix is exactly scoped to the finding. No "while we're here" changes. The sidecar hardening PR is 3 discrete items with no feature additions or refactoring.
