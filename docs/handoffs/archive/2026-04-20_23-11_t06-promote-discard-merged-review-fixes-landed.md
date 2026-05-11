---
date: 2026-04-20
time: "23:11"
created_at: "2026-04-21T03:11:47Z"
session_id: 3c95dd64-2c03-4d49-ad07-18f5bd38b376
resumed_from: "docs/handoffs/archive/2026-04-20_21-39_t06-promote-discard-implemented-pr-open.md"
project: claude-code-tool-dev
branch: main
commit: 27505cc0
title: "T-06 promote/discard merged — 7 review findings fixed, 816 tests"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/journal.py
  - packages/plugins/codex-collaboration/scripts/codex_runtime_bootstrap.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_journal.py
  - docs/superpowers/specs/codex-collaboration/recovery-and-journal.md
---

# T-06 Promote/Discard Merged — 7 Review Findings Fixed, 816 Tests

## Goal

Merge PR #113 (codex.delegate.promote and discard) after addressing all review findings. The prior session implemented the 5-task TDD plan and opened the PR. This session's job was: check review status, address findings, get to merge.

**Trigger:** Handoff from prior session said: "Check PR #113 review status. If approved, merge. Then begin PendingEscalationView projection change."

**Stakes:** Promote is the first write operation in the delegation pipeline — the point where isolated worktree safety translates into workspace-level correctness. Review findings in crash-recovery semantics must be addressed before merge because silent corruption of the primary workspace is the highest-risk failure mode in the system.

**Success criteria (all met):**
1. All review findings addressed with TDD (tests first, then fix) — done (7 findings, 3 commits)
2. Full suite green after each commit — done (807 → 814 → 816)
3. PR merged to main — done (`27505cc0`)
4. Feature branch cleaned up — done

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. Remaining T-06 ACs after this merge: `PendingEscalationView` projection change, delegate skill UX.

## Session Narrative

**Phase 1 — Handoff load and PR status check (~5 min).** Loaded the prior handoff (`2026-04-20_21-39`). Checked PR #113 status via `gh pr view`: open, mergeable, no human review (only automated Codex bot comment). No CI checks configured.

**Phase 2 — User presents first review findings (~5 min).** User presented 3 findings: two P1s and one P2. All three were real correctness bugs confirmed by code inspection:
1. P1: WAL ordering — `git apply` runs before `promotion:dispatched` is journaled
2. P1: Recovery rollback failure swallowed — `git checkout` failure still writes `rolled_back`
3. P2: Bootstrap factory never wires `promotion_callback`

User also verified the PR independently: 281 tests passing on the touched slice.

**Phase 3 — First fix round (d96c2424, ~20 min).** User provided specific direction on all three fixes plus a scope expansion decision: add the spec-mandated `prechecks_passed` and `applied` intermediate states since we were already in the code. User's key instruction: "Do not add `rollback_failed` — use the simpler approach of leaving the journal unresolved." I wrote 3 tests first (TDD red), confirmed all failed for the right reasons, then implemented fixes. All tests passed. Also updated the recovery-and-journal spec wording: `dispatched` now reads "Crossed the mutation boundary; `git apply` may have run."

**Phase 4 — User presents second review delta (~5 min).** User found 2 more issues introduced or exposed by the intermediate-state additions:
1. P1: `promote()` never checks `promotion_state` — terminal states can be overwritten
2. P2: `prechecks_passed` written before `intent` journal creates a crash window

User confirmed the first round fixes were correct but would not approve until these were addressed.

**Phase 5 — Second fix round (5e85ab33, ~15 min).** Wrote 7 new tests (parametrized across 3 terminal + 3 in-flight states + 1 ordering verification). Implemented: (1) state-machine entry gate at top of `promote()` rejecting anything not in `(pending, prechecks_failed)`, (2) swapped `prechecks_passed` and intent ordering so journal entry precedes state write. 814 tests passing.

**Phase 6 — User presents third review delta (~5 min).** Two more findings:
1. P2: `load_stale_marker()` crashes on old-schema markers (`promoted_head` → `promoted_artifact_hash` rename)
2. P3: Intent recovery doesn't preserve `promotion_attempt`, causing idempotency key reuse

User said P2 must fix before merge, P3 is hygiene but worth fixing since trivial.

**Phase 7 — Third fix round (e3ec549b, ~10 min).** Wrote 2 tests. Fixes: (1) defensive field check in `load_stale_marker()` treating old-schema records as absent, (2) recovery parses attempt from idempotency key format. 816 tests passing.

**Phase 8 — Final approval and merge (~5 min).** User confirmed no blocking findings remain. Squash-merged via `gh pr merge 113 --squash`. Checked out main, pulled, deleted feature branch. Clean state.

## Decisions

### Decision 1: Use `job_not_completed` reason for state-machine gate rejection

**Choice:** Reuse the existing `job_not_completed` rejection reason for the state-machine entry gate rather than adding a new `PromotionRejectedReason` value.

**Driver:** The spec's `PromotionRejectedReason` enum at `contracts.md` defines exactly 6 values. Adding a seventh widens the contract surface for what is semantically "you can't promote from here" — a subcase of "job not in promotable state."

**Alternatives considered:**
- **New `state_not_promotable` reason** — more precise semantically. Rejected because it widens the model, store, tests, and contract surface for a case that `job_not_completed` covers adequately. The detail message provides the specificity.

**Trade-offs accepted:** Callers checking `reason == "job_not_completed"` can't distinguish "status isn't completed" from "promotion_state isn't promotable" without parsing the detail string. Acceptable because the detail message includes the actual `promotion_state` value.

**Confidence:** Medium (E1) — pragmatic choice. The spec doesn't define this scenario's rejection reason.

**Reversibility:** High — changing a single Literal string in one return path.

**Change trigger:** If callers need to programmatically distinguish "wrong job status" from "wrong promotion state" for retry logic.

### Decision 2: Leave journal unresolved on rollback failure (no new state)

**Choice:** On failed rollback during recovery, leave `promotion_state="rollback_needed"` and the journal entry unresolved. Do not introduce `rollback_failed` as a new state.

**Driver:** User stated: "Do not add `rollback_failed` in this PR. That widens the model, store, tests, and contract surface for a case you can handle without new state. The simpler correct behavior is: set or keep `rollback_needed`, do not write `rolled_back`, do not write `promotion:completed`, log loudly and leave the journal entry unresolved."

**Alternatives considered:**
- **New `rollback_failed` state** — explicit representation. Rejected per user direction: "The key rule is: if rollback did not succeed, do not close the only truthful replay anchor."

**Trade-offs accepted:** The journal entry remains permanently unresolved if recovery can never succeed. In practice, the next startup re-attempts rollback, and manual intervention is expected for persistent failures.

**Confidence:** High (E2) — user's reasoning is sound: closing the journal removes the truthful anchor, making the system believe it recovered when it didn't.

**Reversibility:** Medium — adding `rollback_failed` later requires model + store changes.

**Change trigger:** If production experience shows that "forever unresolved" journal entries accumulate and need distinct handling.

### Decision 3: Treat old-schema stale markers as absent (not migrate)

**Choice:** `load_stale_marker()` checks for required fields and returns `None` (clearing the record) if old-schema markers are found.

**Driver:** Stale markers are ephemeral session-scoped data (spec: "trimmed after the first successful advisory turn or session end"). An old marker is from a dead session — it's irrelevant.

**Alternatives considered:**
- **Schema migration** — read `promoted_head`, map to `promoted_artifact_hash`, synthesize `job_id`. Rejected because the data is ephemeral and the old marker is semantically invalid (from a pre-promotion-aware session).
- **Crash with TypeError** — the status quo. Rejected because it breaks the consult/status paths on upgrade.

**Trade-offs accepted:** A theoretical loss of stale-context signal if a session upgrades mid-flight. Acceptable because the marker would only exist if a promotion happened in the old schema, which is impossible (promote didn't exist before this branch).

**Confidence:** High (E2) — the old schema predates promote/discard entirely, so no valid marker can exist in the old format after this branch merges.

**Reversibility:** High — trivial to add migration logic later.

**Change trigger:** If future schema changes produce old-but-valid markers that should be migrated rather than dropped.

### Decision 4: Parse attempt from idempotency key for recovery

**Choice:** Recovery extracts `promotion_attempt` from the idempotency key format (`promotion:{job_id}:{attempt}`) rather than storing it as a dedicated journal entry field.

**Driver:** The entry format (`OperationJournalEntry`) doesn't have an `attempt` field, and adding one would widen the model for a single consumer. The key format is stable and parseable.

**Alternatives considered:**
- **Add `attempt` field to `OperationJournalEntry`** — more explicit but wider model change. Rejected as over-engineering for this single use case.
- **Don't preserve attempt** — status quo. Rejected because it violates the monotonic `promotion_attempt` contract and reuses idempotency keys.

**Trade-offs accepted:** Parsing from a string format is fragile if the key format changes. Mitigated by a try/except with fallback to no-op.

**Confidence:** Medium (E1) — pragmatic. The key format is well-established and documented in the spec.

**Reversibility:** High — can add the field later without migration (old entries just won't have it).

**Change trigger:** If the idempotency key format changes or if more fields need to be recovered from journal entries.

## Changes

### Production files (3 modified)

| File | What changed |
|------|--------------|
| `server/delegation_controller.py` | State-machine entry gate (rejects terminal/in-flight states). WAL ordering (dispatched before apply). Intermediate states (prechecks_passed after intent, applied after apply). Recovery: rollback_needed before attempt + continue on failure. Attempt preservation from idempotency key. |
| `server/journal.py` | `load_stale_marker()` defensive field check — old-schema records treated as absent and cleared. |
| `scripts/codex_runtime_bootstrap.py` | Added `promotion_callback=control_plane` to `DelegationController` construction. |

### Spec files (1 modified)

| File | What changed |
|------|--------------|
| `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | `dispatched` phase meaning updated to "Crossed the mutation boundary; `git apply` may have run." Replay rules updated for rollback failure leaving unresolved. |

### Test files (2 modified)

| File | Tests Added | Coverage |
|------|------------|----------|
| `tests/test_delegation_controller.py` | +10 | WAL ordering verification, recovery rollback failure truthfulness, bootstrap callback wiring, 3 terminal state rejections, 3 in-flight state rejections, prechecks_passed ordering verification, recovery attempt preservation |
| `tests/test_journal.py` | +1 | Old-schema stale marker backward compat |

## Codebase Knowledge

### Architecture: Full Promote Ordering (After Fixes)

```
caller → MCP "codex.delegate.promote" {job_id}
  → STATE-MACHINE GATE: reject if promotion_state not in (pending, prechecks_failed)
  → load job, validate status == completed
  → increment promotion_attempt
  → PRECHECKS (6):
      1. artifact_hash present
      2. collaboration handle exists → resolve primary repo root
      3. HEAD == base_commit
      4. git status --porcelain empty
      5. git diff --cached clean
      6. regenerate artifacts → compare hash to reviewed hash
  → ON PRECHECK FAILURE: update_promotion_state("prechecks_failed") → response
  → journal Phase 1: intent  (WAL — journal before state)
  → STATE: prechecks_passed  (safe — journal entry exists)
  → journal Phase 2: dispatched  (WAL — journal before mutation)
  → git apply --binary full.diff  (THE MUTATION)
  → STATE: applied  (safe — dispatched in journal)
  → VERIFY (_verify_promotion):
      1. generate_canonical_artifacts → compare full.diff bytes
      2. compare changed-file set
      3. git status --porcelain → expected modifications only (rstrip, not strip)
  → ON VERIFY FAILURE:
      → STATE: rollback_needed
      → git checkout -- . → unlink new files
      → STATE: rolled_back
      → journal Phase 3: completed → response
  → STATE: verified
  → on_promotion_verified callback → stale_advisory_context
  → audit event → journal Phase 3: completed → response
```

### Key Implementation Locations (Updated)

| Concept | Location |
|---------|----------|
| State-machine entry gate | `delegation_controller.py:~926` |
| `prechecks_passed` write | `delegation_controller.py:~1076` (after intent journal) |
| `dispatched` write (before apply) | `delegation_controller.py:~1100` |
| `applied` write (after apply) | `delegation_controller.py:~1140` |
| Recovery: attempt preservation | `delegation_controller.py:~1840` |
| Recovery: rollback failure → continue | `delegation_controller.py:~1900` |
| `load_stale_marker` compat check | `journal.py:~206` |
| Bootstrap callback wiring | `codex_runtime_bootstrap.py:134` |

### Dependency Graph (Review Fix Slice)

```
delegation_controller.py (promote, recover_startup)
  → delegation_job_store.py (update_promotion_state)
  → journal.py (write_phase, load_stale_marker)
  → artifact_store.py (generate_canonical_artifacts)
  → control_plane.py (on_promotion_verified)

codex_runtime_bootstrap.py
  → delegation_controller.py (DelegationController constructor)
  → control_plane.py (passed as promotion_callback)
```

### Recovery Replay Rules (Corrected)

| Journal State | Workspace | Recovery Action |
|---|---|---|
| intent only | Not mutated | Normalize to pending, preserve attempt, close journal |
| dispatched (no completed) | May be mutated | Re-verify. If passes → verified. If fails → rollback_needed → attempt rollback. If rollback fails → leave unresolved + continue |
| completed | Already resolved | Read terminal state from job store |

## Context

### Mental Model

The review process crystallized a pattern: **every state write must be preceded by its journal anchor**. The journal is the WAL (write-ahead log) for the state machine. Without this invariant, a crash can strand the system in a state that recovery can't reach via journal traversal.

The full ordering principle:
- Journal `intent` → state `prechecks_passed` (anchor: intent)
- Journal `dispatched` → `git apply` → state `applied` (anchor: dispatched)
- State `verified` → journal `completed` (anchor: completed closes the entry)

This is analogous to database WAL: log the intent before the mutation, so crash recovery can determine what was in flight.

### Why This Session Matters

This was the final gate between "code works" and "code is correct under failure." The 7 findings all clustered around crash-recovery semantics — the boundary between "what the journal says happened" and "what actually happened to the workspace." This is exactly where promote's risk lives: it's the only operation that mutates shared state.

### Project State

- **T-05:** COMPLETE. Both slices merged to main at `271f23aa`. 698 tests.
- **T-06 decide:** COMPLETE AND MERGED at `e041c896`. 734 tests.
- **T-06 spec amendments:** COMPLETE AND MERGED at `db7fd1da` (PR #110).
- **T-06 poll:** COMPLETE AND MERGED at `8bae4dde` (PR #111). 765 tests.
- **T-06 sidecar hardening:** COMPLETE AND MERGED at `f9a40366` (PR #112). 771 tests.
- **T-06 promote/discard:** COMPLETE AND MERGED at `27505cc0` (PR #113). 816 tests.
- **Next T-06 slices:** `PendingEscalationView` projection change (post-promote, pre-skill), delegate skill UX.

## Learnings

### Every state write must be preceded by its journal anchor

**Mechanism:** The journal is the WAL for the state machine. Recovery traverses journal entries to determine what was in flight. If a state write exists without a corresponding journal entry, recovery can't find it and the state strands.

**Evidence:** Finding P2 in second review delta — `prechecks_passed` was written before `intent`, creating a gap where the job could strand at `prechecks_passed` with no journal entry for recovery. Fixed by swapping ordering: intent → prechecks_passed.

**Implication:** Any future state addition to the promote lifecycle must follow this rule. The ordering is: journal entry first, then state write. Not the reverse.

### State-machine gates prevent re-entrancy corruption

**Mechanism:** Without an entry gate, `promote()` accepts any job in `completed` status regardless of `promotion_state`. A second call on a `verified` job would hit `worktree_dirty` (workspace is now modified) and overwrite `verified` with `prechecks_failed` — corrupting the terminal state.

**Evidence:** Finding P1 in second review delta confirmed by parametrized tests across 3 terminal and 3 in-flight states.

**Implication:** Any operation that mutates state must gate on valid entry states before touching anything. The gate must come before any state-writing logic, including prechecks.

### Old-schema markers are ephemeral — treat as absent, not migrate

**Mechanism:** `StaleAdvisoryContextMarker` was renamed from `promoted_head` to `promoted_artifact_hash` with a new `job_id` field. `load_stale_marker()` uses `**record` to construct the dataclass, which crashes on unknown/missing fields.

**Evidence:** Finding P2 in third review delta. `git show main:` confirmed old schema on main vs new schema on branch.

**Implication:** Stale markers are session-scoped ephemera. No valid old-schema marker can exist after this merge (promote didn't exist before). Future schema changes should consider whether the data is ephemeral (treat old as absent) or durable (requires migration).

### Review rounds are efficient at catching crash-recovery bugs

**Mechanism:** 7 findings across 3 rounds, all in crash-recovery semantics. Each round used TDD: write failing test → implement fix → verify full suite. No regressions across any commit.

**Evidence:** 3 commits (d96c2424, 5e85ab33, e3ec549b), 12 new tests total, suite grew from 804 to 816 with zero regressions.

**Implication:** For write operations that cross isolation boundaries, plan for 2-3 review rounds focused on crash semantics. The implementation may be correct for the happy path but incorrect for the crash window between state transitions.

## Next Steps

### 1. `PendingEscalationView` projection change

**Dependencies:** PR #113 merged (done).

**What to do:** Scrub start/decide response shapes to project `PendingServerRequest` through `PendingEscalationView`. User recommendation from prior session: "land it immediately after promote and before skill UX."

**Where to start:** Read the current `PendingServerRequest` and `PendingEscalationView` types in `models.py`, then trace how `start()` and `decide()` responses project through to callers.

### 2. Delegate skill UX

**Dependencies:** Promote merged (done), `PendingEscalationView` change landed.

**What to do:** The delegate skill (Claude-facing UX) for the full delegation lifecycle: start → poll → decide → promote/discard. This is the remaining T-06 AC.

## In Progress

**Clean stopping point.** All review findings addressed, PR merged, branch cleaned up. On `main` at `27505cc0` with 816 tests. No work in flight.

## Open Questions

### 1. `git diff --binary` output stability across invocations (inherited)

**Context:** Post-apply verification relies on byte-for-byte comparison of regenerated `full.diff`. The spec noted this may not be stable across git versions. Precheck 6 (hash-based from execution worktree) is the strong guarantee; diff comparison is defense-in-depth.

**Decision pending until:** Production testing reveals whether byte comparison is reliable.

### 2. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** Handler calls `entry.session.interrupt_turn()` from inside `_server_request_handler`. Sends `turn/interrupt` via same transport reading notifications.

**Decision pending until:** Live testing against real App Server.

### 3. `on-request` operational semantics (inherited from T-05)

**Context:** Vendored schema proves `on-request` is a valid `approvalPolicy` value but operational semantics undocumented. Controller defaults to `untrusted`.

**Decision pending until:** Live probe against real App Server.

### 4. Test-results persistence in execution runtime (inherited from poll)

**Context:** The execution prompt instructs the agent to persist at `.codex-collaboration/test-results.json`. If the agent ignores this, all jobs degrade to `"not_recorded"` stubs.

**Decision pending until:** Live execution testing with the amended prompt.

## Risks

### 1. Pre-existing `test_execution_prompt_builder.py` modification

The git status shows `M packages/plugins/codex-collaboration/tests/test_execution_prompt_builder.py` on main. This has been carried across 6+ handoffs. Origin unknown. Not committed. Causes `ruff check` to fail when run on the full worktree (vs PR-scoped files).

### 2. Byte-for-byte diff comparison may be fragile

The post-apply verification compares `full.diff` bytes between the execution worktree and primary workspace. If `git diff` output isn't stable across invocations (line endings, hunk headers, binary encoding), verification could produce false failures.

### 3. `DelegationJobStore.update_status` still public (inherited from poll session)

No remaining callers for status-only transitions — all sites use `_persist_job_transition` → `update_status_and_promotion`. Direct `update_status("completed")` would strand `promotion_state=None`.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| Promotion protocol | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | State machine, preconditions, verification |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Tool surface, DelegationJob, typed responses |
| Recovery and journal | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Journal phases, WAL ordering, replay rules |
| Advisory runtime policy | `docs/superpowers/specs/codex-collaboration/advisory-runtime-policy.md` | Post-promotion coherence |
| Implementation plan | `docs/superpowers/plans/2026-04-20-codex-delegate-promote-discard.md` | Original 5-task TDD plan |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-20_21-39_t06-promote-discard-implemented-pr-open.md`
- T-05/T-06 arc: execution-start → pending-request capture → T-05 closed → T-06 decide → T-06 poll → T-06 sidecar hardening → T-06 promote/discard spec+plan → T-06 promote/discard implementation → **T-06 promote/discard review fixes + merge (this handoff)**

### PR chain

| PR | Title | Status |
|----|-------|--------|
| #109 | T-06 decide opening slice | Merged (`e041c896`) |
| #110 | Spec amendments for codex.delegate.poll | Merged (`db7fd1da`) |
| #111 | feat: implement codex.delegate.poll | Merged (`8bae4dde`) |
| #112 | chore: sidecar hardening | Merged (`f9a40366`) |
| #113 | feat: implement codex.delegate.promote and discard | Merged (`27505cc0`) |

## Gotchas

### 1. WAL ordering: journal before state, journal before mutation

**Symptom:** Recovery can't find a stranded state, or treats a mutated workspace as unmodified.

**Root cause:** State writes or mutations preceding their journal anchor.

**Prevention:** The ordering is always: journal entry → state write or mutation. Specifically: intent → prechecks_passed; dispatched → git apply → applied.

### 2. Recovery must not close truthful anchors on failure

**Symptom:** Next startup doesn't re-enter recovery for a still-broken workspace.

**Root cause:** Writing `rolled_back` and closing the journal even when rollback failed.

**Prevention:** `continue` on `CalledProcessError` — leave both the state (`rollback_needed`) and journal entry unresolved.

### 3. State-machine gate must precede all state-writing logic

**Symptom:** Terminal states overwritten by precheck failure responses.

**Root cause:** `promote()` running prechecks (which write `prechecks_failed`) on jobs in terminal states.

**Prevention:** Entry gate at the top of `promote()` before any precheck logic. Check `promotion_state in ("pending", "prechecks_failed")`.

### 4. `strip()` vs `rstrip()` on porcelain output (inherited)

**Prevention:** Always use `.rstrip()` on `git status --porcelain` output. The leading characters are semantic (XY format).

### 5. Post-apply verification cannot use full artifact hash (inherited)

**Prevention:** Compare only the applyable subset (`full.diff` + `changed-files.json`). Use `generate_canonical_artifacts` for the comparison.

## User Preferences

### Review-driven development style

The user performs independent code review between sessions and presents findings as structured comments with file/line references, priority, and confidence. The user expects fixes to be addressed with TDD discipline (tests first) and committed incrementally (one commit per review round).

### Specific direction on implementation choices

User provides implementation direction, not just findings. Example: "Do not add `rollback_failed` in this PR. The simpler correct behavior is: set or keep `rollback_needed`, do not write `rolled_back`, do not write `promotion:completed`."

### Scope expansion accepted when cheap

User offered the `prechecks_passed` + `applied` intermediate states as optional: "If you want the smallest fix set, I would not block PR #113 on it. If you want the runtime to match the spec cleanly while you are already touching this code, now is the cheapest time to add." Accepted because the states were already in the type/spec and the code touch was minimal.

### Doc updates as part of behavioral fixes

User explicitly requested: "If you move `dispatched` earlier, update the normative wording too. The current docs still describe `dispatched` as 'diff applied,' but after this fix it really means 'crossed the mutation boundary.' I would treat that doc correction as part of the same patch, not optional cleanup."
