---
date: 2026-04-19
time: "23:20"
created_at: "2026-04-20T03:20:39Z"
session_id: 09c345fd-7e1b-44d2-8fc2-f22da17a162c
resumed_from: "docs/handoffs/archive/2026-04-19_22-25_t06-decide-implemented-reviewed-pr-opened.md"
project: claude-code-tool-dev
branch: main
commit: e041c896
title: "T-06 decide merged — review findings fixed, poll is next"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/journal.py
  - packages/plugins/codex-collaboration/server/execution_prompt_builder.py
  - packages/plugins/codex-collaboration/server/consultation_safety.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
---

# T-06 Decide Merged — Review Findings Fixed, Poll Is Next

## Goal

Merge the T-06 decide opening slice (PR #109) after addressing review findings, then establish the critical path for remaining T-06 work.

**Trigger:** Prior handoff said "Next action for next-session Claude: Check PR #109 status. If approved, merge and clean up worktree. If review comments, address them on the feature branch."

**Stakes:** The decide slice establishes the approve/deny semantics that `codex.delegate.poll`, skill UX, and cross-session recovery must respect. Getting the review right prevents downstream contract churn.

**Success criteria (all met):**
1. PR #109 review findings addressed (2 commits: approve-path finalization guard, type safety + validation + test coverage)
2. 734 tests passing (698 T-05 baseline + 29 original T-06 + 7 new from review fixes)
3. PR merged to main at `e041c896`
4. Worktree cleaned up, branch deleted
5. Critical path for remaining T-06 established: poll → promote → skill

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. T-05 complete at `271f23aa`. This session closed the decide opening slice. Remaining T-06 slices: `codex.delegate.poll`, `codex.delegate.promote`, promotion rejection/rollback, stale-advisory signaling, delegate skill.

## Session Narrative

**Phase 1 — Handoff load and PR status check (~5 min).** Loaded the prior handoff (`2026-04-19_22-25_t06-decide-implemented-reviewed-pr-opened.md`). PR #109 was open, mergeable (clean), no CI checks. One automated review from `chatgpt-codex-connector[bot]` with 2 inline comments: P1 on approve-path post-commit writes and P2 on dict key scanning in safety policy.

**Phase 2 — P1 triage and fix (~10 min).** Read the approve path at `delegation_controller.py:1044-1085` in the worktree. Verified the P1 finding was real: the journal `completed` write and `_decided_request_ids.add` were outside the `CommittedDecisionFinalizationError` try/except on the approve path, while the deny path had them inside. This was the same asymmetry class caught and fixed for the deny path in the prior session — the approve path was missed because `_execute_live_turn` (the "big" operation) was wrapped, but the bookkeeping writes after it were treated as infallible. Fixed by moving lines 1058-1085 inside the try block. 727 tests passing, ruff clean. Committed as `b371236a`.

**Phase 3 — Comprehensive PR review (~15 min active, ~40 min agents).** User requested `/pr-review-toolkit:review-pr`. Launched 5 specialized agents in parallel: code-reviewer, pr-test-analyzer, silent-failure-hunter, type-design-analyzer, comment-analyzer. All 5 completed within ~4 minutes of each other.

**Phase 4 — Review aggregation and user triage (~10 min).** Aggregated findings across all 5 agents. Three agents independently converged on the same top finding: `action="approve"` hardcoded for all audit events. Presented triage to user with severity ratings.

**Key pivot:** User pushed back on C1 (audit action naming), citing the contract definition at `contracts.md:211` where `approve` is defined as "Approval resolved" — an operation type, not a decision direction. The test at `test_delegation_controller.py:1656` already asserted `action == "approve"` with `decision == "deny"`. All three review agents misread the domain vocabulary. User reframed C2 from "add logging" to "explicit validation rejection at the MCP boundary." User also demoted C3 (stale docs) from critical to nit-level and demoted I4 (deny broad catch) as intentional design.

**Phase 5 — Implementing triaged fixes (~20 min).** Five items in one commit:
1. **I1:** Typed `_reject_decision(reason: DecisionRejectedReason)` — zero-cost compile-time verification of all 10 call sites.
2. **C2 (reframed):** Replaced silent answer dropping in MCP dispatch with explicit `ValueError` on malformed keys, values, or items. Leveraged the existing `_handle_tools_call` exception handler at `mcp_server.py:303` which returns `isError: true` MCP responses.
3. **I2:** Added 5 missing rejection tests: `job_not_found`, `job_not_awaiting_decision`, `request_not_found`, `request_job_mismatch`, `answers_not_allowed` (both deny-with-answers and non-request_user_input variants).
4. **I3:** Added orphaned `needs_escalation` cold-restart recovery test verifying both job and handle marked `unknown`.
5. **Comment nits:** Module docstring, recovery wording, `_finalize_turn` docstring.

Construction details: `PendingServerRequest` required `runtime_id`, `codex_thread_id`, `codex_turn_id` fields; `CollaborationHandle` used `capability_class: CapabilityProfile` (`Literal["advisory", "execution"]`), not a `mode` field. 734 tests, ruff clean. Committed as `73ef6501`.

**Phase 6 — User review and merge (~5 min).** User independently verified both commits, ran tests (`734 passed in 7.68s`), and confirmed no new blocking findings. PR #109 was already merged by the user before the `gh pr merge` command ran. Pulled main, resolved a trivial stash conflict (import placement in `test_execution_prompt_builder.py`), removed worktree, deleted branch.

**Phase 7 — Critical path discussion (~10 min).** User presented a detailed strategic analysis of remaining T-06 work. Agreed on sequencing: poll → promote → skill → T-07. Discussed poll's unique characteristics as the first pure-read tool in the arc, the artifact-hash coupling between poll and promote, and the `unknown` status inspectability requirement.

## Decisions

### Decision 1: C1 (audit action naming) rejected as finding — contract says "Approval resolved"

**Choice:** Keep `action="approve"` for all decide audit events. Do not change to `action="delegate_decide"` or similar.

**Driver:** User cited `contracts.md:211` which defines audit action `approve` as "Approval resolved" — an operation type meaning "an approval-resolution event was processed," not "approval was granted." The `decision` field carries the approve/deny distinction.

**Alternatives considered:**
- **`action="delegate_decide"`** — proposed by code-reviewer. Rejected because it would be a contract change, not a bugfix. The contract text is explicit and the deny-path test at `test_delegation_controller.py:1656` already asserts `action == "approve"` with `decision == "deny"`.
- **`action=decision`** — proposed by error-reviewer. Rejected for the same reason — changing the action would diverge from the normative contract.

**Trade-offs accepted:** The naming is ambiguous in isolation. Three independent review agents misread it. But the contract is authoritative, and changing it would affect all audit consumers.

**Confidence:** High (E2) — contract text at `contracts.md:211` is explicit: `approve | both | Approval resolved`. Test assertion confirms intentional design.

**Reversibility:** N/A — this is a triage decision (reject finding), not a code change.

**Change trigger:** If the audit action vocabulary is refactored codebase-wide, `approve` could be renamed to `approval_resolution` for clarity.

### Decision 2: C2 reframed — explicit validation rejection, not logging

**Choice:** Replace silent answer dropping in MCP dispatch with `ValueError` that propagates as `isError: true` MCP response.

**Driver:** User stated: "The problem is not 'missing logging'; it is that mcp_server.py does no schema validation and then silently drops malformed answers entries during normalization. If we touch it, the right fix is caller-visible rejection or explicit validation failure, not just a warning log."

**Alternatives considered:**
- **Add `logger.warning` calls** — proposed by error-reviewer. Rejected by user because "the caller never sees logs" — warnings are invisible to Claude, violating the "Explicit over Silent" tenet at the boundary where it matters.
- **Leave as-is** — the silent dropping is defensive and no real caller would send malformed answers. Rejected because validation at system boundaries is a project principle.

**Trade-offs accepted:** Stricter validation may reject inputs that the silent-drop approach would have "fixed" (e.g., answers with integer values that could arguably be coerced to strings). The user's position: if the input is malformed, reject it explicitly rather than guessing intent.

**Confidence:** High (E2) — the existing `_handle_tools_call` exception handler at `mcp_server.py:303` already returns `isError: true` for any exception from `_dispatch_tool`, so `ValueError` naturally produces caller-visible errors.

**Reversibility:** High — the validation is 20 lines that can be relaxed or removed without affecting the controller layer.

**Change trigger:** If a real caller sends answers in a non-standard but reasonable format (e.g., numbers instead of strings), the validation could be relaxed to coerce rather than reject.

### Decision 3: Critical path — poll → promote → skill → T-07

**Choice:** Build `codex.delegate.poll` next, then `codex.delegate.promote`, then the delegate skill. Only move to T-07 after T-06 is closed.

**Driver:** User's analysis: "poll is the seam that reconnects runtime state, caller inspection, artifact review, and the later promotion chain." The decide plan explicitly deferred follow-up-turn inspectability and restart/unknown job handling to poll at `docs/plans/2026-04-19-t06-decide-opening-slice.md:2196`. The promotion protocol assumes artifact hashing happens during poll at `docs/superpowers/specs/codex-collaboration/promotion-protocol.md:38`.

**Alternatives considered:**
- **Promote first** — could be built without poll using direct store reads. Rejected because promote's artifact-hash verification requires the caller to have inspected results through poll first. Building promote first would either skip hash verification or duplicate poll's inspection logic.
- **Skill first** — the delegate skill wraps all four tools. Rejected because it would "force churn in the UX wrapper" as tool response shapes stabilize during poll and promote implementation.

**Trade-offs accepted:** poll before promote means the promotion flow takes longer to complete. But building in dependency order prevents rework.

**Confidence:** High (E2) — the dependency chain is structural: promote consumes poll's artifact hashes, and the skill wraps all tools.

**Reversibility:** High — the ordering is a sequencing choice, not an architectural commitment. Each tool is independently implementable.

**Change trigger:** If a downstream consumer urgently needs promote before poll, the hash verification could be deferred and poll built afterward. But this would leave a verification gap.

## Changes

### `delegation_controller.py` — Approve-path finalization guard (commit `b371236a`)

**Purpose:** Moved journal `completed` write and `_decided_request_ids.add` inside the `CommittedDecisionFinalizationError` try/except on the approve path.

**Key details:** The try block now covers `_execute_live_turn`, journal write, decided-request-ids add, and both return branches. The except clause sits below all of them, matching the deny path's structure at lines 1006-1038.

### `delegation_controller.py` — Type `_reject_decision` reason parameter (commit `73ef6501`)

**Purpose:** Changed `reason: str` to `reason: DecisionRejectedReason` and added the import. Zero-cost compile-time verification of all 10 call sites against the 9-variant `Literal` union.

### `delegation_controller.py` — Stale comments (commit `73ef6501`)

**Purpose:** Updated module docstring (line 1: "Controller for codex.delegate.start and codex.delegate.decide"), recovery comment (line 44: "running" or "needs_escalation"), `_finalize_turn` docstring (line 747: "Called by _execute_live_turn").

### `mcp_server.py` — Explicit answers validation (commit `73ef6501`)

**Purpose:** Replaced silent `continue` drops with `ValueError` on malformed answer keys, values, or items. Each validation point raises with a specific message following the project's error format: `"codex.delegate.decide validation failed: {what}. Got: {input}"`.

**Key details:** Three validation points: non-string keys, non-dict values (or missing `answers` list), non-string items in answers list. Each raises `ValueError` which the existing exception handler at `mcp_server.py:303` catches and returns as `isError: true`.

### `test_delegation_controller.py` — 7 new tests (commit `73ef6501`)

**Purpose:** Added 5 missing rejection tests and 1 orphaned recovery test.

**Key details:**
- `test_decide_rejects_job_not_found` — no setup needed, calls decide with nonexistent job_id
- `test_decide_rejects_job_not_awaiting_decision` — starts a job that completes without escalation, then calls decide
- `test_decide_rejects_request_not_found` — starts with escalation, decides with nonexistent request_id
- `test_decide_rejects_request_job_mismatch` — starts with escalation, plants a foreign request via `prs.create()`, decides with that request_id
- `test_decide_rejects_deny_with_answers` — starts with escalation, denies with answers
- `test_decide_rejects_answers_for_non_request_user_input` — starts with command_approval escalation, approves with answers
- `test_recover_startup_marks_orphaned_needs_escalation_job_and_handle_unknown` — directly creates `needs_escalation` job + `active` handle, builds fresh controller, verifies both marked `unknown`

## Codebase Knowledge

### Decide Method Architecture (post-review fix)

The approve path now has both the journal write and `_decided_request_ids.add` inside the finalization guard, matching the deny path:

```
decide()
│
├─ Phase 1: Validation ladder (9 checks, early return DecisionRejectedResponse)
│
├─ Phase 2: Journal lifecycle (intent → audit → dispatched)
│
└─ Phase 3: Side effects
    ├─ Deny: try { job→failed, handle→completed, release, close, journal completed,
    │         _decided_request_ids.add } except → CommittedDecisionFinalizationError
    └─ Approve: try { _execute_live_turn, journal completed,
               _decided_request_ids.add, return result } except → CommittedDecisionFinalizationError
```

### MCP Answers Validation (post-review fix)

Wire format validation at `mcp_server.py:380-410` now rejects instead of dropping:

| Check | Error |
|-------|-------|
| `raw_answers` not dict | `ValueError: 'answers' must be an object` |
| Key not string | `ValueError: answer key must be a string` |
| Value not dict or missing `answers` list | `ValueError: answer entry {key} must have shape {"answers": ["..."]}` |
| Item in answers list not string | `ValueError: answer values for {key} must be strings` |

### Audit Action Vocabulary

`contracts.md:203-214` defines audit event actions. Key insight from this session:

| Action | Meaning | NOT |
|--------|---------|-----|
| `approve` | "Approval resolved" (the operation type) | "Approval granted" |
| `delegate_start` | "Delegation job started" | — |
| `escalate` | "Escalation surfaced to Claude" | — |

The `decision` field on `AuditEvent` carries the approve/deny distinction. The `action` field is the operation type.

### Test Fixture: `PendingServerRequest` Constructor

`PendingServerRequest` (frozen dataclass at `models.py:235`) requires these fields for test construction:
- `request_id`, `runtime_id`, `collaboration_id`, `codex_thread_id`, `codex_turn_id`, `item_id`, `kind` (PendingRequestKind), `requested_scope` (dict), `status`
- Store method is `prs.create()`, not `prs.store()`

### Test Fixture: `CollaborationHandle` Constructor

`CollaborationHandle` (frozen dataclass at `models.py:212`) requires:
- `collaboration_id`, `capability_class` (`Literal["advisory", "execution"]`), `runtime_id`, `codex_thread_id`, `claude_session_id`, `repo_root`, `created_at`, `status`
- No `mode` field — use `capability_class="execution"` for delegation handles

### Key Locations (Updated)

| Concept | Location |
|---------|----------|
| Approve-path finalization guard | `delegation_controller.py:1044-1085` |
| `_reject_decision` typed parameter | `delegation_controller.py:838` |
| `DecisionRejectedReason` import | `delegation_controller.py:73` |
| MCP answers validation | `mcp_server.py:380-410` |
| MCP exception handler | `mcp_server.py:303` |
| Audit action vocabulary | `contracts.md:203-214` |
| `PendingServerRequest` dataclass | `models.py:235` |
| `CollaborationHandle` dataclass | `models.py:212` |
| `CapabilityProfile` type | `models.py:13` |

## Context

### Mental Model

This session was **review-fix-merge with strategic planning**. The first half was reactive (address review findings), the second half was analytical (establish critical path). The review phase demonstrated a pattern: automated reviewers (both Codex bot and the 5-agent PR review) can converge on the same false positive when domain vocabulary is ambiguous. Three independent agents flagged `action="approve"` as a bug because "approve" reads as a decision direction in isolation — but the contract defines it as an operation type. The user's pushback was grounded in contract text, not preference.

### Why This Session Matters

The approve-path finalization guard fix (`b371236a`) prevents a real correctness gap: if the journal write failed after a successful follow-up turn, `_decided_request_ids` was never populated, allowing stale request_id retry to dispatch duplicate follow-up turns. This is the third instance of the "committed but not recorded" bug class across two sessions.

The critical path agreement (poll → promote → skill) shapes the remaining T-06 work. `poll` is the next load-bearing tool because it's the seam between runtime state inspection and the promotion chain.

### Project State

- **T-05:** COMPLETE. Both slices merged to main at `271f23aa`. 698 tests.
- **T-06:** Opening slice (decide) COMPLETE AND MERGED at `e041c896`. 734 tests.
- **Branch:** `main` at `e041c896`.
- **Worktree:** Removed. No active worktrees.
- **PR #109:** Merged. Branch `feature/t06-decide-opening-slice` deleted.

## Learnings

### Three independent reviewers converging on the same false positive signals domain vocabulary ambiguity

**Mechanism:** All three review agents (code-reviewer, type-reviewer, error-reviewer) flagged `action="approve"` for deny decisions as a bug. The word "approve" reads as a decision direction in isolation. But the contract at `contracts.md:211` defines it as "Approval resolved" — an operation type.

**Evidence:** The user cited the contract text and the existing test assertion at `test_delegation_controller.py:1656`. All three agents had access to `contracts.md` but didn't check the action vocabulary table.

**Implication:** When automated reviewers converge on a finding, verify against the normative contract before accepting. Convergence increases confidence that a pattern exists, but the pattern may be intentional design rather than a bug. The contract is authoritative, not the reviewer consensus.

### The "committed but not recorded" bug class recurs because the guard boundary is drawn around the "big" operation

**Mechanism:** The approve path's `CommittedDecisionFinalizationError` guard wrapped `_execute_live_turn` (the big, obviously-fallible call) but not the journal write and `_decided_request_ids.add` (small, seemingly-infallible calls). After the commit point (audit event), ALL writes must be inside the guard — not just the ones that "look" risky.

**Evidence:** Third instance across two sessions: (1) deny post-commit in prior session, (2) stale request_id in prior session, (3) approve post-commit in this session. The pattern: the "big" call gets wrapped, the bookkeeping calls don't.

**Implication:** For any method with a "committed" point, the guard boundary should be drawn at the commit point, not around individual fallible operations. Everything after the commit point is inside the guard by default; exceptions are only for operations that are truly safe to skip (there are none in the current code).

### Silent dropping at MCP boundaries violates "Explicit over Silent" where it matters most

**Mechanism:** The original MCP answers normalization used `continue` to skip malformed entries. The caller (Claude) never sees logs — only MCP responses. Silent dropping means Claude thinks it sent valid answers but the controller receives empty answers, triggering `answers_required` rejection. The debugging path is: "I sent answers, why does it say answers required?"

**Evidence:** The user's reframe: "the right fix is caller-visible rejection or explicit validation failure, not just a warning log." The existing exception handler at `mcp_server.py:303` already converts exceptions to `isError: true`, making `ValueError` the natural validation mechanism.

**Implication:** At MCP boundaries (the trust surface between Claude and the plugin), validation failures must be caller-visible. Logging is for operators, not callers. Use the existing exception-to-error pipeline instead of adding logs.

## Next Steps

### 1. Design/reconciliation pass for `codex.delegate.poll`

**Dependencies:** None — this is a read-and-plan step.

**What to read first:**
- `contracts.md` for the poll tool's contract surface (lines TBD — poll may not be fully specified yet)
- `docs/plans/2026-04-19-t06-decide-opening-slice.md:2196` for explicit deferrals from decide to poll
- `docs/superpowers/specs/codex-collaboration/promotion-protocol.md:38` for artifact-hash-at-poll-time requirement
- T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` for acceptance criteria

**Design considerations:**
- `poll` is the first pure-read tool in the T-06 arc — no journal lifecycle, no committed-finalization errors, no replay guards
- Must compose all stores (job, lineage, pending request, runtime registry) into a single coherent view
- Must surface artifact hashes that `promote` will verify
- Must handle `unknown` status meaningfully — after `recover_startup()` marks a job `unknown`, poll is the only way the caller discovers this. Whether poll returns enough context for the caller to understand *why* it's unknown matters for the skill's UX layer

**Approach:** The user writes the plan, Claude scrutinizes. Same pattern as the decide slice.

### 2. Sidecar hardening (alongside poll)

**Dependencies:** Can be done alongside poll, not a separate milestone.

**Items:**
- MCP-layer test for malformed-answers rejection path (the new `ValueError` validation has no dedicated MCP-level test)
- Targeted regression test for approve-path "follow-up succeeded, then journal write fails" (the finalization guard fix at `b371236a` has no direct test)
- `codex.delegate.start` PreToolUse scan policy (deferred from decide plan at `docs/plans/2026-04-19-t06-decide-opening-slice.md:2200`)

### 3. After poll: `codex.delegate.promote`

**Dependencies:** Poll merged.

**Scope:** HEAD/base-commit match, clean worktree/index, artifact-hash verification, completed-job precondition, typed rejection responses, rollback, advisory-stale signaling. All normed in `docs/superpowers/specs/codex-collaboration/promotion-protocol.md:12`.

### 4. After promote: delegate skill

**Dependencies:** poll + promote merged.

**Purpose:** Wraps `start` / `poll` / `decide` / `promote` into a coherent UX surface. Required by T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md:66`.

## In Progress

**Clean stopping point.** PR #109 merged, worktree cleaned up, main at `e041c896` with 734 tests. No work in flight.

- **Completed:** PR review, 2 fix commits, merge, worktree cleanup, critical path agreement.
- **Not in flight:** No code changes pending, no review comments to address.
- **Next action for next-session Claude:** Begin the design/reconciliation pass for `codex.delegate.poll`. Read the contract, promotion protocol, and decide plan deferrals. The user will write the plan; Claude scrutinizes.

## Open Questions

### 1. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** The handler calls `entry.session.interrupt_turn()` from inside the `_server_request_handler` callback. This sends a `turn/interrupt` JSON-RPC request via the same transport that's reading notifications.

**Impact:** Medium. If the transport doesn't handle re-entrant reads, the handler will deadlock.

**Decision pending until:** Live testing against the real App Server.

### 2. `on-request` operational semantics (inherited from T-05)

**Context:** The vendored schema proves `on-request` is a valid `approvalPolicy` value, but operational semantics are not documented. Controller defaults to `untrusted` per D1.

**Decision pending until:** Live probe against the real App Server.

### 3. Approve turn prompt shape adequacy (inherited from decide)

**Context:** `build_execution_resume_turn_text()` tells the execution agent "the earlier server request has already been resolved at the wire layer." Whether this prompt produces reliable follow-up behavior is unverified.

**Decision pending until:** Live execution testing.

### 4. Poll's `unknown` status inspectability

**Context:** After `recover_startup()` marks a job `unknown`, `poll` is the only way the caller discovers this. How much context poll provides about *why* a job is unknown (crashed mid-turn vs. crashed mid-decide vs. orphaned escalation) affects the skill's UX layer.

**Decision pending until:** Poll design pass.

## Risks

### 1. `_decided_request_ids` is in-memory only

If `codex.delegate.poll` or cross-session decide is added, the in-memory set won't persist across restarts. For the same-session-only design, this is correct — recovery demotes orphaned jobs. A durable equivalent would be needed for cross-session decide.

### 2. `_FakeSession` complexity continues to grow

The fake session has: `run_execution_turn` (with per-turn `_interrupted` reset), `interrupt_turn`, `close`, `_raise_on_turn`, `_interrupted` state, and configurable server requests + turn result. If the fake drifts from the real `AppServerRuntimeSession` interface, tests pass but production fails.

### 3. Two deferred test gaps from this session

The approve-path finalization guard fix (`b371236a`) and the MCP answers validation (`73ef6501`) each lack a targeted regression test exercising the specific failure scenario. These are real but non-critical — the code is correct but the fix's specific motivation isn't tested. Planned as sidecar hardening alongside poll.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| T-06 decide plan | `docs/plans/2026-04-19-t06-decide-opening-slice.md` | Implementation authority (2216 lines) |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Schema authority |
| Promotion protocol | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | Promotion semantics |
| Recovery spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Recovery semantics |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-19_22-25_t06-decide-implemented-reviewed-pr-opened.md`
- T-05/T-06 arc: execution-start COMPLETE → pending-request capture COMPLETE → T-05 closed + T-06 scoped → T-06 plan scrutinized → T-06 decide implemented + PR #109 → **T-06 decide merged + poll next (this handoff)**

### Commit chain (this session)

| Commit | Message |
|--------|---------|
| `b371236a` | `fix(t20260330-06): wrap approve post-commit writes in finalization guard` |
| `73ef6501` | `fix(t20260330-06): type safety, input validation, test coverage, stale docs` |
| `e041c896` | `Merge pull request #109 from jpsweeney97/feature/t06-decide-opening-slice` |

## Gotchas

### 1. Three review agents converging on a false positive

**Symptom:** All three review agents (code, type, error) independently flagged `action="approve"` for deny decisions as a critical bug.

**Root cause:** The word "approve" is ambiguous in isolation — reads as a decision direction, not an operation type.

**Prevention:** Check the audit action vocabulary table at `contracts.md:203-214` before accepting audit-related findings. The contract defines `approve` as "Approval resolved."

### 2. `PendingServerRequest` and `CollaborationHandle` have more required fields than expected

**Symptom:** Pyright errors when constructing these dataclasses in tests.

**Root cause:** `PendingServerRequest` requires `runtime_id`, `codex_thread_id`, `codex_turn_id` beyond the obvious fields. `CollaborationHandle` uses `capability_class: CapabilityProfile` (`Literal["advisory", "execution"]`), not a `mode` field.

**Prevention:** Check the dataclass definitions at `models.py:235` and `models.py:212` before constructing in tests.

### 3. `CapabilityProfile` is `Literal["advisory", "execution"]`, not `"delegate"`

**Symptom:** Pyright error: `Literal['delegate']` is not assignable to `CapabilityProfile`.

**Prevention:** Use `"execution"` for delegation handles.

### 4. Pre-session local changes on main can conflict with PR merge

**Symptom:** `git pull` fails because local changes to `execution_prompt_builder.py` and `test_execution_prompt_builder.py` overlap with the merged PR.

**Prevention:** Stash or commit local changes before pulling merged PRs. In this case, the conflict was trivial (import placement).

## Conversation Highlights

### User's C1 pushback: contract text over reviewer consensus

User: "C1 should be rejected, not fixed. The public contract defines audit action `approve` as 'approval resolved,' not 'approval granted' in contracts.md, and the deny-path test already asserts `action == 'approve'` with `decision == 'deny'` in test_delegation_controller.py. Changing it would be a contract change, not a bugfix."

This corrected a finding that three independent review agents agreed on — demonstrating that contract text is authoritative over reviewer consensus.

### User's C2 reframe: caller-visible rejection, not logging

User: "The problem is not 'missing logging'; it is that mcp_server.py does no schema validation and then silently drops malformed answers entries during normalization. If we touch it, the right fix is caller-visible rejection or explicit validation failure, not just a warning log."

This elevated the fix from "add warnings" to "validate and reject at the boundary."

### User's strategic analysis

User provided a detailed critical-path analysis with 4 doc references: contracts.md, decide plan deferrals, promotion protocol hash requirements, and T-06 ticket acceptance criteria. Concluded: "The concrete next move is a read-first design/reconciliation pass for codex.delegate.poll, because poll is the seam that reconnects runtime state, caller inspection, artifact review, and the later promotion chain."

## User Preferences

### Triage authority: user reviews agent findings against normative contracts

The user independently verified or rejected each finding by checking against the contract text, existing test assertions, and architectural intent. Three of the five review categories produced findings the user rejected or reframed. Pattern: present findings with evidence and severity, but expect the user to triage against their own understanding of the design intent.

### Validation at boundaries: explicit rejection over logging

The user's strong preference: when something fails at a system boundary (MCP tool inputs), the caller must see the failure. Logging is for operators; callers need structured error responses. Use existing error-propagation mechanisms (exception → `isError` response) rather than adding parallel logging.

### Strategic planning: user presents analysis, Claude validates

The user prepared the critical-path analysis between sessions and presented it for validation, not generation. Pattern: the user drives strategic direction; Claude provides technical assessment and flags considerations the user may have missed (e.g., poll's need to surface artifact hashes for promote, poll's unique characteristics as a pure-read tool).
