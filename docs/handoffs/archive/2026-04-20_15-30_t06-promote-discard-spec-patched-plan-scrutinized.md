---
date: 2026-04-20
time: "15:30"
created_at: "2026-04-20T19:30:10Z"
session_id: 1d547648-1633-4d7e-be32-1adf8353d609
resumed_from: "docs/handoffs/archive/2026-04-20_14-37_t06-poll-merged-sidecar-hardening-open-promote-next.md"
project: claude-code-tool-dev
branch: main
commit: f9a40366
title: "T-06 promote/discard spec patched, plan scrutinized, ready for implementation"
type: handoff
files:
  - docs/superpowers/specs/codex-collaboration/promotion-protocol.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/specs/codex-collaboration/advisory-runtime-policy.md
  - docs/superpowers/specs/codex-collaboration/recovery-and-journal.md
  - docs/superpowers/plans/2026-04-20-codex-delegate-promote-discard.md
  - packages/plugins/codex-collaboration/server/consultation_safety.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
---

# T-06 Promote/Discard Spec Patched, Plan Scrutinized, Ready for Implementation

## Goal

Merge PR #112 (sidecar hardening), then design and specify `codex.delegate.promote` and `codex.delegate.discard` before implementation. The session's scope was read-first design, spec patching, plan writing, and scrutiny — no runtime implementation.

**Trigger:** Handoff from prior session said: "Check PR #112 status. If approved, merge. Then begin the read-first design/reconciliation packet for codex.delegate.promote."

**Stakes:** Promote is the highest-risk boundary in the delegation pipeline — the point where isolated worktree safety must translate into workspace-level correctness. The spec had a fundamental contradiction ("changes HEAD" vs. `git apply` semantics) that would have produced inconsistent implementation if not resolved before code.

**Success criteria (all met):**
1. PR #112 merged with one review finding addressed — done at `f9a40366`
2. Spec contradiction identified and resolved (apply-only promotion) — 4 normative files patched
3. 10 design decisions locked with user agreement — all documented in spec and plan
4. Implementation plan written and scrutinized — 2 critical findings addressed
5. Clean stopping point for implementation start in next session

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. T-06 decide merged at `e041c896`. Spec amendments merged at `db7fd1da`. Poll merged at `8bae4dde`. Sidecar hardening merged at `f9a40366`. Remaining T-06 ACs: promote, discard, rollback, stale-context invalidation, delegate skill UX.

## Session Narrative

**Phase 1 — Handoff load and PR #112 merge (~5 min).** Loaded the prior handoff (`2026-04-20_14-37`). The prior session's code review had flagged one P3 finding in PR #112: the approve-path finalization regression test at `test_delegation_controller.py:2246` asserted `job.status in ("completed", "unknown")` when the test's stated invariant demanded exactly `"completed"`. Switched to `chore/t06-sidecar-hardening`, tightened the assertion to `== "completed"`, verified the test passes (771/771), committed at `4aa9a7d9`, pushed, and merged PR #112 via `gh pr merge`. Main advanced to `f9a40366`. Cleaned up local branch and returned to main.

**Phase 2 — Authority document read-through (~15 min).** Read 6 normative spec files in parallel: `promotion-protocol.md` (127 lines), `contracts.md` (366 lines), `recovery-and-journal.md` (177 lines), `advisory-runtime-policy.md` (146 lines), the T-06 ticket (89 lines), and `foundations.md` (324 lines). Then read 4 implementation files: `delegation_controller.py` (focus on `poll()`, `_persist_job_transition`, `__init__`, `recover_startup`), `delegation_job_store.py` (240 lines), `artifact_store.py` (262 lines), and `mcp_server.py` (dispatch pattern for `delegate.poll` and `delegate.decide`).

**Phase 3 — Initial design synthesis (~10 min).** Produced a first design read-through covering what exists vs. what's needed, scope mapping to spec, and 5 design decisions. Key observations: `_review_hash` in `ArtifactStore` must be reused at promote-time, `StaleAdvisoryContextMarker` and journal infrastructure already exist, `_persist_job_transition` auto-sets `promotion_state="pending"` on completion.

**Phase 4 — User's first round of corrections (~15 min).** User identified the fundamental spec contradiction: `promotion-protocol.md:125` says "A successful promotion changes HEAD" but `git apply` does not move HEAD. The state machine (multi-step `prechecks_passed → applied → verified`) and rollback semantics (`git checkout -- .`) both assume apply-only. The "changes HEAD" wording was from an earlier design that assumed commit-producing promotion.

User also identified 7 additional design breaks: stale-marker model has wrong truth anchor (`promoted_head` meaningless if HEAD unchanged), controller boundary can't check advisory runtime existence, `recompute_hash()` is too narrow an abstraction, post-apply verification is too weak, precheck contract underspecified on untracked files, journaling needs explicit phase mapping, and crash-after-apply recovery is underspecified.

User recommended: preserve apply-only promotion, amend stale-marker/HEAD docs to match.

**Phase 5 — Design lock (~10 min).** Locked D1-D8: apply-only promotion, stale marker redesign, control-plane callback, factor `generate_canonical_artifacts`, strong verification, precheck tightening, journal authority, separate `codex.delegate.discard` tool.

**Phase 6 — User's second round of amendments (~10 min).** User refined 8 more points: (1) drop `base_commit` from stale marker (stale-on-read hazard), (2) split execution-side canonicalization from primary-workspace verification (test-results.json is execution-only), (3) structured `CanonicalArtifactBundle` dataclass, (4) tighten `worktree_dirty` contract text, (5) narrow discard to `pending` and `prechecks_failed` only, (6) lock result shapes now, (7) explicit journal phase mapping, (8) journal authoritative when it disagrees with job store.

Locked the discard legal state set: `pending` and `prechecks_failed` (both pre-mutation states). `prechecks_passed` is recovery-normalized to `pending` first.

**Phase 7 — Spec patching and plan writing (user, out-of-band).** User patched 4 normative spec files and wrote the implementation plan. User also made one additional design lock: `promotion_attempt` as a persisted monotonic field on `DelegationJob`, and gave `codex.delegate.discard` a minimal typed rejection surface.

**Phase 8 — Scrutiny (~15 min).** Ran a reject-until-proven-credible review of all 5 files. Found 2 critical failures:

- **F1:** Stale marker breaking rename not traced through existing code. The spec changed `promoted_head` → `promoted_artifact_hash` + added `job_id`, but the plan treated this as additive when it's a breaking change across 4 production files and 3 test files (`models.py:169`, `journal.py:207`, `control_plane.py:167`, `test_journal.py:22,38,45,52,60`, `test_control_plane.py:360`).

- **F2:** `OperationJournalEntry.operation` Literal at `models.py:311` doesn't include `"promotion"`. Plan added it to `_VALID_OPERATIONS` in `journal.py` but missed the type annotation.

Also found: backward-compatible default needed for `promotion_attempt`, `git apply --binary` flag needed for binary diffs, rollback must identify and remove untracked files produced by the diff, missing rollback test for new-file creation, and spec-commit ordering relative to implementation branch.

**Verdict:** Minor revision. Spec patch is clean and internally consistent. Plan is structurally sound but blind to breaking changes in existing code.

**Phase 9 — User addressed findings.** User patched the plan to cover all critical and high-risk findings. Also tightened the spec: `promotion:completed` is now a resolution marker written only after the job store already says `verified` or `rolled_back`, eliminating the replay ambiguity.

## Decisions

### Decision 1: Apply-only promotion, not commit-producing

**Choice:** Promotion applies the reviewed diff to the primary workspace without creating a commit. Claude decides when to commit.

**Driver:** Three spec-internal evidence lines: (1) state machine has multi-step `prechecks_passed → applied → verified` — a commit would collapse these; (2) rollback at `promotion-protocol.md:118` specifies `git checkout -- .` (working-tree rollback, not `git revert`); (3) trust model at `foundations.md:116` says "Claude stays primary."

**Alternatives considered:**
- **Commit-producing promotion** — would make the "changes HEAD" wording literal. Rejected because it widens scope (commit message, author info), changes the trust model (plugin silently commits), and contradicts the rollback semantics.

**Trade-offs accepted:** The user must explicitly commit after promotion. An uncommitted promotion can be lost if the session crashes without committing. Accepted because the alternative (plugin committing silently) is a worse trust violation.

**Confidence:** High (E2) — verified against 3 independent spec sections (state machine, rollback, trust model).

**Reversibility:** Medium — making it commit-producing later would require changing the state machine, rollback semantics, and audit semantics.

**Change trigger:** If users consistently forget to commit after promotion and lose work.

### Decision 2: Stale marker carries artifact hash + job_id, not base_commit

**Choice:** `StaleAdvisoryContextMarker` fields: `repo_root`, `promoted_artifact_hash`, `job_id`, `recorded_at`. No `base_commit`.

**Driver:** User: "The next advisory turn already reloads live repo identity in `control_plane.py:160`. If the user commits after promote but before the next advisory turn, a stored `base_commit` becomes stale and misleading."

**Alternatives considered:**
- **Keep `promoted_head` (old design)** — meaningless with apply-only promotion since HEAD doesn't change. Rejected.
- **Add `base_commit` alongside `promoted_artifact_hash`** — rejected because "the marker should carry the fact of workspace mutation, not try to cache repo identity."
- **`promoted_artifact_hash` + `base_commit`** (my initial proposal) — user rejected the `base_commit` component.

**Trade-offs accepted:** The advisory turn's stale summary must combine marker data with live `HEAD` at dispatch time (slight implementation complexity). Accepted because it avoids stale-on-read.

**Confidence:** High (E1) — user explicitly specified with reasoning.

**Reversibility:** High — add `base_commit` to the marker if needed.

**Change trigger:** If the advisory turn's summary generation needs the original `base_commit` to explain what changed.

### Decision 3: Stale marker via control-plane callback

**Choice:** Controller fires `on_promotion_verified(repo_root, artifact_hash, job_id) -> bool` callback. Control plane implements it and decides whether to write the marker based on advisory runtime existence.

**Driver:** User: "The controller boundary is not neutral here. `DelegationController` only knows about the execution-side control-plane hook; it has no way to ask 'does an advisory runtime exist for this repo root right now?'" Spec at `advisory-runtime-policy.md:136`: "If no advisory runtime exists for the repo root, no stale marker is created."

**Alternatives considered:**
- **Controller writes marker directly** — rejected because the controller can't check advisory runtime existence and would bypass the spec policy.

**Trade-offs accepted:** Callback adds an interface seam. The boolean return means the controller can report `stale_advisory_context` to the caller without coupling to advisory internals.

**Confidence:** High (E1) — user explicitly specified.

**Reversibility:** High — collapse the callback into the controller if the boundary changes.

**Change trigger:** If the controller gains advisory runtime awareness for other reasons.

### Decision 4: Factor `generate_canonical_artifacts` with `CanonicalArtifactBundle`

**Choice:** Single artifact-generation method in `ArtifactStore` returning a structured bundle. Both poll (`materialize_snapshot`) and promote call it. Promote uses a temp dir; poll persists to the inspection dir.

**Driver:** User: "The honest abstraction is to factor `ArtifactStore` so both poll and promote call the same 'generate canonical review artifacts' path, with poll persisting and promote using a temp dir. A narrow `recompute_hash()` still leaves two independent artifact-generation paths that can drift."

**Alternatives considered:**
- **Make `_review_hash` public** — too narrow; centralizes the hash but not the artifact generation.
- **`recompute_hash(job) -> str`** — user rejected: "That only centralizes the hash combiner, not the canonical-artifact generation."

**Trade-offs accepted:** `CanonicalArtifactBundle` lives in `artifact_store.py` (not `models.py`), which deviates from the pattern of all typed shapes in `models.py`. Accepted per user's reasoning that it's an internal implementation type, not a contract type.

**Confidence:** High (E1) — user explicitly specified with reasoning.

**Reversibility:** High — mechanical refactor either direction.

**Change trigger:** If the bundle becomes part of the MCP response surface.

### Decision 5: Post-apply verification is diff byte-comparison + changed-files set, not artifact hash recompute

**Choice:** Verify the primary workspace by: (1) byte-compare `git diff --binary base_commit` to the reviewed `full.diff`, (2) compare changed-file set to `changed-files.json`, (3) confirm `git status --porcelain` shows only expected modifications.

**Driver:** User: "The canonical review set includes execution-side material that is not part of the promoted workspace." Specifically, `test-results.json` (at `artifact_store.py:22`) is in the artifact set but never applied to the primary workspace.

**Alternatives considered:**
- **Recompute full artifact hash on primary workspace** — rejected because the hash includes `test-results.json` which doesn't exist in the primary workspace.
- **Check only `git status` for expected files** (my initial proposal) — user: "Does not prove that the reviewed diff landed exactly."

**Trade-offs accepted:** Byte-for-byte diff comparison is fragile across git versions and line-ending normalization. The scrutiny review noted this (finding B2). Precheck 6 (regenerate-and-compare hash) is the strong integrity guarantee; post-apply byte comparison is a defense-in-depth check.

**Confidence:** Medium (E1) — user's reasoning is sound but `git diff` output stability across invocations is an empirical question.

**Reversibility:** High — loosen to set-comparison only if byte comparison proves flaky.

**Change trigger:** If `git diff` output instability produces false verification failures in testing.

### Decision 6: Precheck requires `git status --porcelain` empty (including untracked)

**Choice:** Any non-empty `git status --porcelain` output blocks promotion, including `??` untracked files.

**Driver:** User: "If untracked files are allowed, your rollback snapshot idea is required. If they are disallowed, the packet is much safer and simpler."

**Alternatives considered:**
- **Allow untracked files** — would require pre-apply snapshot of untracked files to identify which ones were produced by the diff during rollback. Rejected for complexity.

**Trade-offs accepted:** Users must stash or remove untracked files before promoting. This adds friction but eliminates an entire class of rollback ambiguity.

**Confidence:** High (E1) — user explicitly specified with reasoning.

**Reversibility:** High — relax the precheck and add snapshot tracking.

**Change trigger:** If users frequently have untracked files that block promotion and find the UX unacceptable.

### Decision 7: Journal authority for workspace mutation

**Choice:** When journal and job store disagree, the journal wins for "has workspace mutation occurred?" The `promotion` operation uses phases: `intent` (prechecks passed, no mutation), `dispatched` (diff applied), `completed` (verified or rolled_back). `completed` is a resolution marker written after the job store already shows the terminal state.

**Driver:** User: "You need to say which store is authoritative when journal and job-store disagree." The journal is written before the mutation (per write-ordering discipline), so it's the only reliable source for "did the mutation happen?"

**Alternatives considered:**
- **Job store authoritative** — rejected because the job store update may fail after the mutation, creating an inconsistency where the workspace has been modified but the store doesn't reflect it.

**Trade-offs accepted:** Recovery must re-run verification when journal says `dispatched` but store says `prechecks_passed`. This is safe because verification is read-only.

**Confidence:** High (E1) — user explicitly specified with reasoning.

**Reversibility:** Low — changing the authority model would require redesigning the recovery path.

**Change trigger:** None foreseeable — this is a correctness invariant, not a preference.

### Decision 8: Separate `codex.delegate.discard` tool

**Choice:** Discard is a separate MCP tool, not a parameter on `codex.delegate.promote`.

**Driver:** User: "`discard` has different semantics, no prechecks, and a separate audit action."

**Alternatives considered:**
- **Overload `promote` with a `decision` parameter** — rejected because promote and discard have fundamentally different risk profiles, precondition sets, and audit semantics.

**Trade-offs accepted:** One more MCP tool to register, validate, and dispatch. Minimal complexity cost.

**Confidence:** High (E1) — user explicitly specified.

**Reversibility:** Medium — collapsing back into promote would change the MCP surface.

**Change trigger:** If the tool surface becomes too fragmented.

### Decision 9: Discard valid from `pending` and `prechecks_failed` only

**Choice:** `codex.delegate.discard` accepts `promotion_state` of `pending` or `prechecks_failed`. All other states are rejected with `job_not_discardable`.

**Driver:** The state machine defines `pending → discarded`. `prechecks_failed` is also pre-mutation. States at or after `applied` have mutated the workspace — discard is not semantically honest after mutation.

**Alternatives considered:**
- **Discard from any non-terminal state** — user: "`applied` and `verified` are already past the point where 'discard' is semantically honest."
- **Discard from `pending` only** — user: "`prechecks_failed` is also pre-mutation; requiring normalization back to `pending` first is a UX fiction."

**Trade-offs accepted:** `prechecks_passed` (transient crash state) requires recovery normalization to `pending` before discard. Adds a recovery step but keeps the discard contract clean.

**Confidence:** High (E1) — user explicitly triaged each state.

**Reversibility:** High — widen the legal set if needed.

**Change trigger:** If `rolled_back` jobs need a discard path (currently terminal).

### Decision 10: Lock result shapes before implementation

**Choice:** `PromotionResult(job, artifact_hash, changed_files, stale_advisory_context: bool)` and `DiscardResult(job)`.

**Driver:** User: "The contracts currently define promotion rejection, but not success results. That will create avoidable churn if left open."

**Alternatives considered:**
- **Define during implementation** — user rejected to avoid churn.

**Trade-offs accepted:** Locking the shape before implementation means discovering missing fields during implementation requires a spec amendment. Accepted because the risk of over-specification is lower than the risk of implementation-driven contract drift.

**Confidence:** High (E1) — user explicitly specified.

**Reversibility:** Medium — changing the MCP response shape is a contract change.

**Change trigger:** If implementation reveals a missing field needed by the delegate skill UX.

## Changes

### PR #112 — Additional commit, merged

| Commit | What changed |
|--------|-------------|
| `4aa9a7d9` | Tightened approve-path finalization guard assertion: `job.status in ("completed", "unknown")` → `job.status == "completed"`. |

PR #112 merged at `f9a40366`. Branch `chore/t06-sidecar-hardening` deleted.

### Spec patches (4 normative files, unstaged on main)

| File | What changed |
|------|-------------|
| `promotion-protocol.md` | Tightened precheck 2 to `git status --porcelain` empty (including untracked). Added Post-Apply Verification section (byte-compare diff, changed-files set, porcelain check). Added `prechecks_failed → discarded` arc to state machine. Added Discard Semantics section. Changed "changes HEAD" → "changes primary-workspace content." Added `prechecks_passed` recovery normalization note. |
| `contracts.md` | Added `codex.delegate.discard` to tool surface. Added `promotion_attempt` to `DelegationJob`. Added `PromotionResult`, `DiscardRejection`, `DiscardResult` response shapes. |
| `advisory-runtime-policy.md` | Changed "changes HEAD" → "applies reviewed workspace content." Updated stale marker to record artifact hash + job id instead of promoted HEAD. Updated summary anchoring to use marker + live repo identity. |
| `recovery-and-journal.md` | Added `promotion` to idempotency key table with `promotion_attempt` explanation. Added Promotion Replay section with phase meanings and journal-authoritative replay rules. Updated stale marker payload to `repo_root`, `promoted_artifact_hash`, `job_id`, `recorded_at`. Changed "changes HEAD" → "applies reviewed workspace content." Made `promotion:completed` a resolution marker written after job store shows terminal state. |

### Implementation plan (new file)

| File | Purpose |
|------|---------|
| `docs/superpowers/plans/2026-04-20-codex-delegate-promote-discard.md` | 5-task TDD implementation plan. Task 1: models + job store + journal vocabulary. Task 2: factor canonical artifact generation. Task 3: promote/discard controller logic. Task 4: advisory stale-context callback. Task 5: MCP surface + safety policies. |

## Codebase Knowledge

### Files Read This Session

| File | Lines | Why read | Key finding |
|------|-------|----------|-------------|
| `promotion-protocol.md` | 127 | Authority for preconditions, state machine, rollback | "changes HEAD" at line 125 contradicted apply-only semantics of state machine and rollback. Now amended. |
| `contracts.md` | 366 | Authority for DelegationJob, tool surface, typed responses | `PromotionRejection` existed but no `PromotionResult` or `DiscardResult`. `promotion_attempt` not defined. Now amended. |
| `recovery-and-journal.md` | 177→200 | Authority for journal, stale marker, crash recovery | `stale_advisory_context` marker had `promoted_head` field — meaningless with apply-only. `promotion` not in the idempotency key table. Now amended. |
| `advisory-runtime-policy.md` | 146 | Authority for post-promotion coherence | "changes HEAD" wording carried the same assumption as promotion-protocol. Now amended. |
| `foundations.md` | 324 | High-level delegation flow, trust model | Line 116: "Claude stays primary" — key evidence for apply-only decision. |
| `T-06 ticket` | 89 | Remaining ACs | promote, rollback, stale-context, delegate skill UX still open. |
| `delegation_controller.py` | 1353 | Existing controller structure | `_persist_job_transition` at line 755 auto-sets `promotion_state="pending"` on completion. `_ControlPlaneLike`, `_WorktreeManagerLike`, `_ArtifactStoreLike` protocols. `__init__` takes 12 dependencies. `recover_startup()` reconciles `job_creation` and `approval_resolution` journal records — needs `promotion` added. |
| `delegation_job_store.py` | 240 | Existing store structure | Append-only JSONL with `_replay()`. Has `update_status`, `update_status_and_promotion`, `update_artifacts`. Needs `update_promotion_state`. `DelegationJob` at `models.py:332` has no `promotion_attempt` field. |
| `artifact_store.py` | 262 | Existing artifact generation | `materialize_snapshot()` generates canonical artifacts (full.diff, changed-files.json, test-results.json) and computes SHA-256 hash. `_review_hash()` is private. `_changed_files()`, `_full_diff()`, `_test_results_record()` are separate private methods. All need to be extracted into `generate_canonical_artifacts()`. |
| `mcp_server.py` | 460 | Existing MCP dispatch pattern | Tool dispatch is a linear `if name ==` chain. `delegate.poll` at line 387 calls `controller.poll()` and returns `asdict()`. Same pattern for promote/discard. |
| `models.py` | ~460 | Existing model definitions | `StaleAdvisoryContextMarker` at line 165 has `promoted_head` (needs rename). `OperationJournalEntry.operation` at line 311 is a 4-value Literal (needs `"promotion"` added). No `PromotionResult`, `DiscardResult`, `PromotionRejectedReason`, `DiscardRejectedReason` exist yet. |
| `journal.py` | ~300 | Existing journal structure | `_VALID_OPERATIONS` at line 35 is a 4-value frozenset (needs `"promotion"`). `write_stale_marker()` at line 200 constructs `StaleAdvisoryContextMarker` with `promoted_head` (needs update). |
| `control_plane.py` | ~180 | Existing stale summary | Line 167 formats stale summary referencing `stale_marker.promoted_head` (needs update to `promoted_artifact_hash` + live HEAD). |
| `consultation_safety.py` | 191 | Existing policy structure | `_TOOL_POLICY_MAP` has 6 entries after sidecar hardening. Needs `codex.delegate.promote` and `codex.delegate.discard` entries. |

### Architecture: Promote Data Flow (Designed, Not Yet Implemented)

```
caller → MCP "codex.delegate.promote" {job_id}
  → mcp_server.py: dispatch to controller.promote()
    → increment promotion_attempt on DelegationJob
    → journal Phase 1: intent (prechecks passed, no mutation)
    → PRECHECKS:
        1. HEAD == base_commit (git rev-parse HEAD)
        2. git status --porcelain empty
        3. index clean (git diff --cached --exit-code)
        4. job.status == "completed"
        5. job.artifact_hash is not None
        6. regenerate artifacts in temp dir, compare hash to reviewed hash
    → ON PRECHECK FAILURE:
        → update_promotion_state("prechecks_failed")
        → return PromotionRejectedResponse
    → git apply --binary full.diff
    → journal Phase 2: dispatched (mutation happened)
    → VERIFY:
        1. git diff --binary base_commit byte-compare to reviewed full.diff
        2. changed-file set compare to reviewed changed-files.json
        3. git status --porcelain shows only expected modifications
    → ON VERIFY FAILURE:
        → rollback: git checkout -- . + remove new untracked files
        → update_promotion_state("rolled_back")
        → journal Phase 3: completed
        → return PromotionRejectedResponse
    → update_promotion_state("verified")
    → invoke on_promotion_verified callback → stale_advisory_context boolean
    → emit audit event (action: promote, decision: approve)
    → journal Phase 3: completed
    → return PromotionResult
```

### Breaking Change Blast Radius (From Scrutiny)

The stale-marker rename (`promoted_head` → `promoted_artifact_hash` + add `job_id`) touches:

| File | What changes |
|------|-------------|
| `models.py:165` | `StaleAdvisoryContextMarker`: rename field, add `job_id` |
| `journal.py:200-211` | `write_stale_marker`: construct with new fields |
| `journal.py:195-198` | `load_stale_marker`: deserialize new shape |
| `control_plane.py:167` | Stale summary formatting: use `promoted_artifact_hash` + live HEAD |
| `test_journal.py:22,38,45,52,60` | All marker constructions use `promoted_head=` |
| `test_control_plane.py:360` | Marker construction uses `promoted_head=` |

The `OperationJournalEntry.operation` expansion touches:

| File | What changes |
|------|-------------|
| `models.py:311` | Add `"promotion"` to `Literal` type |
| `journal.py:35` | Add `"promotion"` to `_VALID_OPERATIONS` |

## Context

### Mental Model

This session was **contract-first design reconciliation.** The existing spec had evolved incrementally and contained a fundamental contradiction (apply-only state machine + "changes HEAD" workspace effects). The session's work was: identify the contradiction, lock the correct semantics, trace the implications through 4 normative files, patch the spec, then plan implementation.

The key insight: the spec's state machine and rollback semantics were the more constrained (and therefore more trustworthy) artifacts. They were designed later and with more detail. The "changes HEAD" wording was aspirational text from an earlier design phase that was never updated.

### Why This Session Matters

Promote is the first write operation in the delegation pipeline. Everything before it (start, decide, poll) is preparation and inspection. Promote crosses the isolation boundary — it takes changes from a sandboxed worktree and applies them to the user's primary workspace. Getting the contract wrong here would be expensive to fix after implementation.

### Project State

- **T-05:** COMPLETE. Both slices merged to main at `271f23aa`. 698 tests.
- **T-06 decide:** COMPLETE AND MERGED at `e041c896`. 734 tests.
- **T-06 spec amendments:** COMPLETE AND MERGED at `db7fd1da` (PR #110). Docs-only.
- **T-06 poll:** COMPLETE AND MERGED at `8bae4dde` (PR #111). 765 tests.
- **T-06 sidecar hardening:** COMPLETE AND MERGED at `f9a40366` (PR #112). 771 tests.
- **T-06 promote/discard:** SPEC PATCHED, PLAN WRITTEN AND SCRUTINIZED. Implementation next.
- **Next T-06 slices after promote:** delegate skill UX. `PendingEscalationView` projection change deferred to post-promote, pre-skill window.

## Learnings

### Spec archaeology: constrained artifacts are more trustworthy than aspirational text

**Mechanism:** When a spec evolves incrementally, later design decisions can invalidate earlier assumptions without the text being updated. The state machine (added later, with detailed state/transition tables) contradicted the workspace effects section (written earlier, with aspirational "changes HEAD" wording).

**Evidence:** `promotion-protocol.md` had: state machine with `applied → verified` multi-step (line 75), rollback with `git checkout -- .` (line 118), AND "changes HEAD" (line 125). The first two are structurally constrained (they define behavior precisely). The third is a prose claim that was never verified against the detailed design.

**Implication:** When specs contradict themselves, trust the more constrained artifact. State machines and formal contracts constrain more than prose descriptions.

### Plan blindness to breaking changes when written spec-outward

**Mechanism:** The implementation plan was written from the spec's new shape outward to the code. This missed that the stale-marker rename and journal operation expansion are breaking changes to existing code and tests. The plan treated them as additive.

**Evidence:** Scrutiny F1 and F2. The plan's Task 1 didn't list the 4 production files and 3 test files that need breaking changes for the stale-marker rename.

**Implication:** When writing implementation plans for spec patches, trace the blast radius inward (from spec changes to existing code) before planning outward (from new spec to new code). The existing code is the ground truth; the spec is the target.

### Post-apply verification cannot honestly use the full artifact hash

**Mechanism:** The canonical review set includes execution-side inspection data (`test-results.json` at `artifact_store.py:22`) that is intentionally not applied to the primary workspace. Recomputing the full artifact hash on the primary workspace would always fail because one artifact is missing.

**Evidence:** User: "Your `generate_canonical_artifacts()` refactor is right, but it should only be the authority for the execution worktree. It should not be reused to verify the primary workspace after apply."

**Implication:** Execution-side canonicalization and primary-workspace verification are separate codepaths with different scopes. Factor accordingly.

## Next Steps

### 1. Commit spec amendments and plan

**Dependencies:** None. This is a prerequisite for the implementation branch.

**What to do:** The 4 spec files and implementation plan are unstaged on main. The spec changes need to be committed before creating the implementation branch, so the implementation branch starts from the corrected spec baseline. Consider whether to commit them to main directly (they're docs-only, no runtime changes) or via a short-lived branch + PR.

**Decision needed:** Commit directly to main (fast, docs-only) or branch + PR (consistent with workflow). User's preference from prior sessions: docs-only changes are low-risk and can go direct.

### 2. Create implementation branch and begin Task 1

**Dependencies:** Spec committed (Step 1).

**What to read first:** The implementation plan at `docs/superpowers/plans/2026-04-20-codex-delegate-promote-discard.md`. It has 5 tasks with TDD structure.

**What to do:**
1. Create `feature/t06-delegate-promote-discard` branch from main.
2. Run pre-flight checks (plan Steps P1 and P2).
3. Begin Task 1: models, job store, and journal vocabulary. This includes the breaking `StaleAdvisoryContextMarker` rename.

**Potential obstacles:** The `test_execution_prompt_builder.py` modification on main (origin unknown, carried across 4+ handoffs) — ensure it doesn't interfere with the implementation branch.

### 3. PendingEscalationView projection change (post-promote, pre-skill)

**Dependencies:** Promote merged.

**What to do:** Scrub start/decide response shapes to project `PendingServerRequest` through `PendingEscalationView`. User recommendation from prior session: "land it immediately after promote and before skill UX."

## In Progress

**Clean stopping point.** Spec patches and plan are written and scrutinized. No code changes in flight beyond the spec diffs and plan. 771 tests passing on main at `f9a40366`.

- **Completed this session:** PR #112 merged. 10 design decisions locked. 4 spec files patched. Implementation plan written. Scrutiny performed and findings addressed.
- **Not in flight:** No implementation code changes. Spec diffs and plan are unstaged on main.
- **Next action for next-session Claude:** Commit the spec amendments and plan. Create the implementation branch. Begin Task 1 of the plan.

## Open Questions

### 1. `git diff --binary` output stability across invocations (inherited from this session)

**Context:** Post-apply verification relies on byte-for-byte comparison of `git diff --binary base_commit` output. Scrutiny finding B2 noted this may not be stable across git versions or configurations. Precheck 6 (hash-based) is the strong guarantee; byte comparison is defense-in-depth.

**Decision pending until:** Implementation testing reveals whether byte comparison is reliable in practice.

### 2. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** Handler calls `entry.session.interrupt_turn()` from inside `_server_request_handler`. Sends `turn/interrupt` via same transport reading notifications.

**Decision pending until:** Live testing against real App Server.

### 3. `on-request` operational semantics (inherited from T-05)

**Context:** Vendored schema proves `on-request` is a valid `approvalPolicy` value but operational semantics undocumented. Controller defaults to `untrusted`.

**Decision pending until:** Live probe against real App Server.

### 4. Test-results persistence in execution runtime (inherited from poll)

**Context:** The execution prompt instructs the agent to persist at `.codex-collaboration/test-results.json`. If the agent ignores this, all jobs degrade to `"not_recorded"` stubs. The promote hash includes the stub content.

**Decision pending until:** Live execution testing with the amended prompt.

## Risks

### 1. Pre-existing `test_execution_prompt_builder.py` modification

The git status shows `M packages/plugins/codex-collaboration/tests/test_execution_prompt_builder.py` on main. This has been carried across 4+ handoffs. Origin unknown. May interfere with implementation branch commits if accidentally staged.

### 2. Byte-for-byte diff comparison may be fragile

The post-apply verification (finding B2 from scrutiny) relies on `git diff` output stability. If this proves unreliable, verification falls back to changed-files set comparison and porcelain check only, which is weaker.

### 3. `DelegationJobStore.update_status` still public (inherited from poll session)

No remaining callers for status-only transitions — all 7 sites use `_persist_job_transition` → `update_status_and_promotion`. Direct `update_status("completed")` would strand `promotion_state=None`. Deferred to promote slice for docstring warning or deprecation.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| Promotion protocol | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | Preconditions, state machine, verification, rollback, discard |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Tool surface, DelegationJob, typed responses |
| Advisory runtime policy | `docs/superpowers/specs/codex-collaboration/advisory-runtime-policy.md` | Post-promotion coherence |
| Recovery and journal | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Journal phases, stale marker, replay rules |
| Foundations | `docs/superpowers/specs/codex-collaboration/foundations.md` | Trust model, delegation flow |
| Implementation plan | `docs/superpowers/plans/2026-04-20-codex-delegate-promote-discard.md` | 5-task TDD plan |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-20_14-37_t06-poll-merged-sidecar-hardening-open-promote-next.md`
- T-05/T-06 arc: execution-start → pending-request capture → T-05 closed → T-06 decide plan → T-06 decide implemented → T-06 decide merged → T-06 poll spec amendments → T-06 poll plan scrutinized → T-06 poll implemented → T-06 poll merged + hardening → **T-06 promote/discard spec + plan (this handoff)**

### PR chain

| PR | Title | Status |
|----|-------|--------|
| #109 | T-06 decide opening slice | Merged (`e041c896`) |
| #110 | Spec amendments for codex.delegate.poll | Merged (`db7fd1da`) |
| #111 | feat(t20260330-06): implement codex.delegate.poll | Merged (`8bae4dde`) |
| #112 | chore(t20260330-06): sidecar hardening for delegation tools | Merged (`f9a40366`) |

## Gotchas

### 1. Stale-marker rename is a breaking change, not an additive one

**Symptom:** Plan treats `StaleAdvisoryContextMarker` field changes as new-type additions.

**Root cause:** `promoted_head` → `promoted_artifact_hash` + add `job_id` requires updating 4 production files and 3 test files. Plan was written spec-outward and missed the inward blast radius.

**Prevention:** When patching specs that change existing model shapes, trace the blast radius through existing code before planning new code.

### 2. `OperationJournalEntry.operation` Literal and `_VALID_OPERATIONS` must both be updated

**Symptom:** Adding `"promotion"` to `_VALID_OPERATIONS` in `journal.py` but not to the `Literal` type in `models.py` passes runtime validation but fails static analysis.

**Root cause:** Dual validation — the `Literal` constrains the type system, `_VALID_OPERATIONS` constrains runtime. Both must agree.

**Prevention:** When adding new journal operation types, update both `models.py:311` and `journal.py:35`.

### 3. `git apply` needs `--binary` for binary diffs

**Symptom:** Binary file changes silently fail to apply without the flag.

**Root cause:** `artifact_store.py` generates diffs with `git diff --binary` (lines 192, 223). The apply command must match.

**Prevention:** Always pair `git diff --binary` with `git apply --binary`.

## Conversation Highlights

### User's identification of the spec contradiction

User: "The normative docs are contradictory. `promotion-protocol.md` says promotion advances when `git apply` succeeds, but the same file says successful promotion changes `HEAD` at line 125, and `advisory-runtime-policy.md` carries that same assumption. `git apply` does not move `HEAD`. So before code, the contract needs to choose."

This was the pivotal moment — it reframed the session from "design the implementation" to "fix the contract first."

### User's stale-marker reasoning

User: "Don't store `base_commit` in the stale marker. The next advisory turn already reloads live repo identity in `control_plane.py:160`. If the user commits after promote but before the next advisory turn, a stored `base_commit` becomes stale and misleading. The marker should carry the fact of workspace mutation, not try to cache repo identity."

### User's verification scope correction

User: "Your proposed post-apply verification is too weak. ... For v1, I would verify the primary workspace by recomputing `git diff --binary` against `base_commit` and comparing it byte-for-byte to the reviewed `full.diff`, plus comparing the changed-file set to `changed-files.json`. That is the real `applied -> verified` proof."

Followed by: "Do not try to prove `verified` by recomputing the reviewed `artifact_hash` on the primary workspace. That hash includes execution-side material that is not part of the promoted workspace."

### User's discard scope tightening

User: "I would not let `codex.delegate.discard` operate on 'any non-terminal promotion_state.' The current state machine only defines `pending -> discarded`. `applied` and `verified` are already past the point where 'discard' is semantically honest."

## User Preferences

### Evidence-first design review

User provides findings with full evidence chains: exact `file:line` references, links to authority documents, reproduction evidence, and confidence ratings. Expects the same density in responses. Every design claim must be grounded in spec text or code.

### Contract-first, implementation-second

User explicitly called for "a read-first design/reconciliation packet" and insisted on resolving spec contradictions before writing code. User: "Before code, the contract needs to choose."

### Triage discipline over comprehensive fixing

Consistent with prior sessions: the scrutiny review found findings at multiple severity levels. User addressed the 2 critical findings and the spec ambiguity, not every medium/low finding. Design decisions are triaged by whether they block implementation.

### Iterative refinement through multiple rounds

User provided corrections across 3 rounds (initial 7 breaks, then 8 amendments, then scrutiny response), each building on the prior round. Each round was more specific than the last. User expects engagement with the substance of corrections, not just acceptance.
