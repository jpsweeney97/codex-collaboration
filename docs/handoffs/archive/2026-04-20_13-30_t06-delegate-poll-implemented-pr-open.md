---
date: 2026-04-20
time: "13:30"
created_at: "2026-04-20T17:30:00Z"
session_id: b1bf0f4a-3e82-4a19-9418-85b13e46274f
resumed_from: "docs/handoffs/archive/2026-04-20_11-44_t06-poll-plan-scrutinized-ready-for-implementation.md"
project: claude-code-tool-dev
branch: feature/t06-delegate-poll
commit: a8ab1ca1
title: "T-06 delegate poll — implemented, reviewed, PR open"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/artifact_store.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/delegation_job_store.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/consultation_safety.py
  - packages/plugins/codex-collaboration/server/execution_prompt_builder.py
  - packages/plugins/codex-collaboration/server/__init__.py
  - packages/plugins/codex-collaboration/scripts/codex_runtime_bootstrap.py
  - packages/plugins/codex-collaboration/tests/test_artifact_store.py
  - packages/plugins/codex-collaboration/tests/test_models_r2.py
  - packages/plugins/codex-collaboration/tests/test_delegation_job_store.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_consultation_safety.py
  - packages/plugins/codex-collaboration/tests/test_codex_guard.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - packages/plugins/codex-collaboration/tests/test_execution_prompt_builder.py
---

# T-06 Delegate Poll — Implemented, Reviewed, PR Open

## Goal

Implement `codex.delegate.poll` following the approved implementation plan at `docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md`. The plan was scrutinized through two adversarial passes in the prior session and approved as "Defensible."

**Trigger:** Prior handoff (`2026-04-20_11-44`) said "Next action for next-session Claude: Execute the plan using `superpowers:subagent-driven-development`."

**Stakes:** `codex.delegate.poll` is the inspection and review mechanism for completed delegation jobs — without it, the caller cannot see what the agent produced, verify the review hash, or proceed to promotion. It gates the entire promote→verify→apply pipeline.

**Success criteria (all met):**
1. `codex.delegate.poll` MCP surface registered and dispatching — ✓
2. Typed poll result contract (job state, pending-escalation projection, inspection snapshot) — ✓
3. Nullable `promotion_state` lifecycle with atomic store op — ✓
4. Deterministic review-artifact materialization with spec-compliant hash — ✓
5. Safety policy wired for PreToolUse guard — ✓
6. 712 tests passing, ruff clean — ✓
7. PR open for review — ✓ (#111)

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. T-06 decide slice complete at `e041c896` (PR #109). Spec amendments merged at `db7fd1da` (PR #110). Poll plan scrutinized and approved (prior handoff). This session implemented the plan and opened PR #111. Remaining T-06 slices: promote, delegate skill UX.

## Session Narrative

**Phase 1 — Handoff load and pre-flight (~5 min).** Loaded the prior handoff (`2026-04-20_11-44`). Read the full 1788-line implementation plan. Created a worktree at `../claude-code-tool-dev-poll` on branch `feature/t06-delegate-poll` from `main` at `db7fd1da`. Ran baseline delegation tests — 106 passed. Pre-flight complete.

**Phase 2 — Subagent-driven implementation (~40 min).** Executed the plan using `superpowers:subagent-driven-development`. Each of the four tasks went through the full cycle: dispatch implementer → spec compliance review → code quality review → fix review findings → commit.

- **Task 1 (types + store contract):** Subagent implemented nullable `promotion_state`, 4 poll dataclasses, atomic `update_status_and_promotion` op. Code quality review caught `ArtifactInspectionSnapshot.artifact_hash` typed as `str` instead of `str | None` (would break Task 2's unknown-job path), `update_artifacts` signature wrong, replay missing guard for non-list `artifact_paths`, `PollRejectedReason` not exported. All four fixed before moving to Task 2. Commit: `f781c4c4`.

- **Task 2 (artifact materialization):** Subagent created `ArtifactStore` with `materialize_snapshot`/`load_snapshot`, canonical review set (`full.diff`, `changed-files.json`, `test-results.json`), SHA-256 hash recipe, `.codex-collaboration/` exclusion, `not_recorded` stub. Code quality review caught unused imports and a weak `in` assertion (should be `==` for exact match). Fixed. Commit: `bebe3705`.

- **Task 3 (controller poll flow):** Largest task — `DelegationController.poll()`, `_persist_job_transition` helper, lifecycle migration (7 `update_status` call sites replaced), pending-escalation projection, snapshot-store rehydration. Code quality review caught: concrete `ArtifactStore` type instead of Protocol pattern (existing codebase uses `_XxxLike(Protocol)` for all controller dependencies), and bare `assert` missing diagnostic message. Fixed with `_ArtifactStoreLike` Protocol and descriptive assertion. Commit: `9e360b01`.

- **Task 4 (MCP surface + safety):** Registered `codex.delegate.poll` in `TOOL_DEFINITIONS`, added dispatch branch, wired `DELEGATE_POLL_POLICY`. Code quality review caught dead `start` method on fake controller and local import inconsistency. Fixed. Commit: `8e7dee37`.

**Phase 3 — User review, round 1 (~15 min).** User performed an independent review against the merged poll contract and promotion protocol. Found three defects the subagent pipeline missed:

1. **Hash sort order (P1):** `_review_hash` iterated `artifact_paths` in insertion order (`full.diff`, `changed-files.json`, `test-results.json`), but `promotion-protocol.md:62` requires "sorted by relative path." Sorted order is `changed-files.json`, `full.diff`, `test-results.json`. The known-value hash test mirrored the same wrong order, creating a tautological check.

2. **Wire-layer decisions (P1):** `_project_pending_escalation` forwarded `PendingServerRequest.available_decisions` unchanged — values from `approval_router.py` like `accept`, `acceptForSession`, `decline`, `cancel`. The plugin surface only accepts `approve`/`deny` (`DecisionAction` at `models.py:34`). For some request kinds (file_change, request_user_input), `available_decisions` is `()`.

3. **Corrupt snapshot resilience (P2):** `load_snapshot` called `json.loads()` without error handling. Truncated `snapshot.json` would raise `JSONDecodeError` on every subsequent poll. Fixed with `try/except (JSONDecodeError, KeyError, TypeError): return None`.

All three fixed in commit `ddf90a96`.

**Phase 4 — User review, round 2 (~10 min).** User found that the corrupt-cache fallback interacted badly with already-reviewed jobs: once a completed job has a persisted `artifact_hash`, falling through to `materialize_snapshot` from a mutated worktree would silently replace the authoritative reviewed hash. The fix needed to distinguish "first poll, no prior artifacts" from "cache corrupt, artifacts exist in store."

Fix: added `if job.artifact_hash is not None:` guard in `_load_or_materialize_inspection`. When the store has a reviewed hash but the snapshot cache is corrupt, calls `reconstruct_from_artifacts` instead of rematerializing from the worktree. Commit: `ae480a92`.

**Phase 5 — User review, round 3 (~5 min).** User found `reconstruct_from_artifacts` didn't validate that the artifact files actually existed, and didn't handle malformed `changed-files.json` (valid JSON, wrong shape → `AttributeError`). Fix: validate all artifact files exist before reconstruction, `isinstance(payload, dict)` guard, broader except clause. Commit: `a8ab1ca1`.

**Phase 6 — PR (~2 min).** Pushed branch, created PR #111.

## Decisions

### Decision 1: Subagent-driven development with per-task review cycle

**Choice:** Used `superpowers:subagent-driven-development` with fresh subagent per task and two-stage review (spec compliance then code quality) after each.

**Driver:** The plan specified this approach. User explicitly requested: "Proceed via /subagent-driven-development." The plan has 4 independent tasks with clear boundaries.

**Alternatives considered:**
- **Sequential implementation in one thread** — would pollute context as the controller alone is 1240 lines. Rejected because context pollution leads to cross-task interference.
- **`superpowers:executing-plans`** (parallel session) — would require human-in-loop between tasks. Rejected for latency.

**Trade-offs accepted:** Subagent reviews can't cross-reference across tasks (each reviewer only sees its own task's changes). This is why the user's manual review caught issues the pipeline missed — the hash sort order required knowledge of `promotion-protocol.md`, and the wire-layer decisions required knowledge of `DecisionAction` and `approval_router.py`.

**Confidence:** High (E2) — the approach worked for all 4 tasks. The per-task review caught 12 issues across 4 tasks. The cross-cutting issues (3+1+1 from user reviews) were structural and required broader codebase knowledge that per-task reviewers can't have.

**Reversibility:** N/A — execution approach, not a code decision.

**Change trigger:** N/A.

### Decision 2: `_ArtifactStoreLike` Protocol instead of concrete `ArtifactStore` type

**Choice:** Defined `_ArtifactStoreLike(Protocol)` in the controller with `materialize_snapshot`, `load_snapshot`, and `reconstruct_from_artifacts` stubs, matching the existing pattern for `_ControlPlaneLike` and `_WorktreeManagerLike`.

**Driver:** Code quality review flagged the concrete import as inconsistent with the codebase's structural typing pattern. All other controller dependencies use Protocol classes.

**Alternatives considered:**
- **Concrete `ArtifactStore` type** — simpler import, but breaks the testability protocol pattern. `_FakeArtifactStore` in tests is a duck-typed double that doesn't inherit from the real class.

**Trade-offs accepted:** Protocol adds 8 lines to the controller. Acceptable for pattern conformance.

**Confidence:** High (E2) — established pattern in the codebase with two prior examples.

**Reversibility:** High — change the type annotation and remove the Protocol class.

**Change trigger:** If the codebase moves to ABC-based injection instead of structural typing.

### Decision 3: Reconstruct from artifact files when snapshot cache is corrupt

**Choice:** When `load_snapshot` returns None but `job.artifact_hash` exists in the store, call `reconstruct_from_artifacts` which reads `changed-files.json` from the persisted canonical artifacts (under the inspection directory), carries over the store's hash, and rewrites `snapshot.json` to heal the cache.

**Driver:** User's review found two issues: (1) rematerializing from a mutated worktree would silently overwrite the authoritative reviewed hash, and (2) returning `inspection=None` degrades the poll result contract which says inspection is present whenever artifacts are available.

**Alternatives considered:**
- **Return `None` for inspection** — safe for integrity but violates the poll result contract. `artifact_paths` in the job advertises files that the inspection snapshot should expose. User flagged: "The new test explicitly locks that behavior in with `assert second.inspection is None`."
- **Rematerialize from worktree** — the original code path. Breaks the review-to-promote integrity boundary if the worktree has changed since the original review.
- **Fail loudly (raise)** — too aggressive for a cache-corruption recovery path. Poll should be resilient.

**Trade-offs accepted:** `reviewed_at` timestamp is lost when reconstructing (uses current timestamp instead of original). Acceptable because `reviewed_at` is informational metadata, not part of the review hash.

**Confidence:** High (E2) — the artifact files are immutable under the inspection directory (written once by `materialize_snapshot`). The store's `artifact_hash` is the authoritative reviewed state. Reconstruction from these two sources is safe.

**Reversibility:** Medium — the `reconstruct_from_artifacts` method is now part of the `_ArtifactStoreLike` Protocol. Removing it requires updating the Protocol, the real class, and the fake.

**Change trigger:** If artifact files under the inspection directory become mutable (e.g., post-review amendment flow), reconstruction would need to re-validate the hash.

## Changes

### New production file

| File | Lines | Responsibility |
|------|-------|----------------|
| `server/artifact_store.py` | ~240 | Deterministic inspection artifact materialization, snapshot caching, review-hash computation, cache-corruption recovery |

### Modified production files

| File | What changed |
|------|-------------|
| `server/models.py` | `DelegationJob.promotion_state: PromotionState \| None`, `PollRejectedReason`, `PendingEscalationView`, `ArtifactInspectionSnapshot`, `DelegationPollResult`, `PollRejectedResponse` |
| `server/delegation_job_store.py` | `_is_valid_promotion_state()`, `update_status_and_promotion()`, `update_artifacts()`, extended `_replay()` for new ops |
| `server/delegation_controller.py` | `_ArtifactStoreLike` Protocol, `artifact_store` param, `_persist_job_transition()`, `_project_pending_escalation()`, `_load_or_materialize_inspection()`, `poll()`, lifecycle migration (7 call sites) |
| `server/mcp_server.py` | `codex.delegate.poll` tool definition + dispatch |
| `server/consultation_safety.py` | `DELEGATE_POLL_POLICY` + policy map entry |
| `server/execution_prompt_builder.py` | Test-results persistence instructions in both prompt builders |
| `server/__init__.py` | Export new types |
| `scripts/codex_runtime_bootstrap.py` | `ArtifactStore` construction and injection |

### New test file

| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_artifact_store.py` | 8 | Canonical files, hash verification, unknown omits hash, missing test-results stub, corrupt snapshot, reconstruction, missing artifacts, malformed manifest |

### Modified test files

| File | Tests added | What changed |
|------|-------------|-------------|
| `tests/test_models_r2.py` | 2 | Nullable promotion_state, poll result shapes |
| `tests/test_delegation_job_store.py` | 3 | Atomic status+promotion, artifact update, legacy replay |
| `tests/test_delegation_controller.py` | 7 | Promotion lifecycle, poll completed/escalation/not-found, rehydration, cache reconstruction |
| `tests/test_mcp_server.py` | 2 | Tool registration, MCP round-trip dispatch |
| `tests/test_consultation_safety.py` | 1 | Policy lookup for poll tool |
| `tests/test_codex_guard.py` | 1 | Clean-path guard test |
| `tests/test_delegate_start_integration.py` | 2 | E2E completed + escalation through MCP |
| `tests/test_execution_prompt_builder.py` | 2 | Test-results persistence instructions |

## Codebase Knowledge

### Files Read This Session

| File | Lines | Why read | Key finding |
|------|-------|----------|-------------|
| `delegation_controller.py` | 1240→1325 | Understand `__init__` params, `_finalize_turn_result` paths, `update_status` call sites, recovery paths | 7 `update_status` terminal calls to replace. Job creation at line 473 seeds `promotion_state="pending"`. Two finalization paths: with-request (escalation) and no-request (clean completion/failure). |
| `delegation_job_store.py` | 150→240 | Understand JSONL append/replay pattern | `_replay()` handles `create` and `update_status`. Added `update_status_and_promotion` and `update_artifacts` ops. `_VALID_PROMOTION_STATES` from `get_args(PromotionState)`. |
| `execution_prompt_builder.py` | 73→80 | Understand existing prompt shape | Two builders: `build_execution_turn_text` (initial) and `build_execution_resume_turn_text` (follow-up after escalation). Uses `json.dumps` for `requested_scope`. |
| `codex_runtime_bootstrap.py` | 162→170 | Understand DelegationController factory | Factory closure pattern — `session_id` only available after `_read_session_id`. Added `ArtifactStore(plugin_data_path, timestamp_factory=journal.timestamp)`. |
| `approval_router.py` | 35 | Understand wire-layer decisions | `_AVAILABLE_DECISIONS` maps request kinds to App Server vocabulary: `command_approval` → 6 values (`accept`, `acceptForSession`, etc.), `file_change` and `request_user_input` → `()`. These are NOT plugin-level decisions. |
| `models.py` | 401→460 | Understand `DelegationJob` shape, add poll types | `PromotionState = Literal[7 values]`. `DecisionAction = Literal["approve", "deny"]` — the plugin-level decision vocabulary. `PendingServerRequest` has `available_decisions: tuple[str, ...]` populated from wire layer. |
| `promotion-protocol.md` | (grep) | Verify hash recipe | Line 62: "sorted by relative path" — the hash must sort artifact_paths before iterating. This is the spec the original implementation violated. |
| `test_delegation_controller.py` | 2181→2350 | Understand `_build_controller` helper, existing test patterns | 8-tuple return. `_FakeControlPlane` and `_FakeWorktreeManager` already existed. Added `_FakeArtifactStore`. 5 `promotion_state="pending"` assertions on non-completed jobs needed updating to `None`. |

### Architecture: Poll Data Flow

```
caller → MCP "codex.delegate.poll" {job_id}
  → mcp_server.py: dispatch to controller.poll()
    → job_store.get(job_id) — load job from JSONL
    → IF needs_escalation: _project_pending_escalation()
        → pending_request_store.list_by_collaboration_id()
        → project to PendingEscalationView (plugin-level decisions only)
    → IF terminal (completed/failed/unknown): _load_or_materialize_inspection()
        → TRY artifact_store.load_snapshot() (snapshot.json cache)
        → IF cache hit: rehydrate store if stale, return
        → IF cache miss + store has hash: reconstruct_from_artifacts()
            → validate all artifact files exist
            → read changed-files.json manifest
            → rebuild snapshot, heal cache
        → IF cache miss + no hash: materialize_snapshot() (first poll)
            → git diff, git ls-files (worktree)
            → write full.diff, changed-files.json, test-results.json
            → compute SHA-256 hash (sorted by relative path)
            → write snapshot.json
            → update store with artifact_paths + hash
    → return DelegationPollResult or PollRejectedResponse
  → mcp_server.py: asdict(result) → JSON-RPC response
```

### Store Operation Replay Pattern (Updated)

JSONL ops after poll implementation:
1. `create` — full `DelegationJob` object (promotion_state=None for new jobs)
2. `update_status_and_promotion` — atomic status + promotion_state (terminal transitions)
3. `update_artifacts` — artifact_paths (list→tuple) + artifact_hash

All ops are append-only, last-write-wins for conflicting fields. Replay converts list-backed `artifact_paths` to tuples. `_is_valid_promotion_state()` accepts None or any valid PromotionState value.

### Safety Policy Pattern (Updated)

`consultation_safety.py` now has 5 entries in `_TOOL_POLICY_MAP`:
- `codex.consult` → CONSULT_POLICY
- `codex.dialogue.start` → DIALOGUE_START_POLICY
- `codex.dialogue.reply` → DIALOGUE_REPLY_POLICY
- `codex.delegate.decide` → DELEGATE_DECIDE_POLICY
- `codex.delegate.poll` → DELEGATE_POLL_POLICY (empty `content_fields`)

Pre-existing gap: `codex.delegate.start` has no policy entry (fail-closed via `codex_guard.py:49` catching `KeyError`).

### Promotion State Lifecycle (Implemented)

```
Job creation   → promotion_state=None   (status="queued")
Running        → promotion_state=None   (status="running")
Escalation     → promotion_state=None   (status="needs_escalation")
Failed         → promotion_state=None   (status="failed")
Unknown        → promotion_state=None   (status="unknown")
Completion     → promotion_state="pending" (atomic with status="completed")
First poll     → artifacts materialized, hash computed
Promotion      → promotion_state="prechecks_passed" → "applied" → "verified"
```

## Context

### Mental Model

This session was **plan execution with integrity verification**. The plan was the implementation authority — subagents executed it task-by-task. The user's manual reviews were the integrity layer, catching cross-cutting defects that per-task reviewers couldn't see:

- **Hash sort order** required knowledge of `promotion-protocol.md` (spec authority, not task scope)
- **Wire-layer decisions** required knowledge of `approval_router.py` + `DecisionAction` (cross-module boundary)
- **Corrupt cache** required reasoning about crash-safety across the materialize→cache→rehydrate lifecycle
- **Reconstruction vs degradation** required understanding the poll result contract (design-level concern)

The pattern: subagent reviews catch implementation-quality issues (wrong types, missing exports, pattern violations). User reviews catch design-integrity issues (spec conformance, boundary violations, lifecycle interactions).

### Why This Session Matters

`codex.delegate.poll` completes the inspection layer for delegated work. Without it:
- Callers cannot see what the execution agent produced
- There is no review hash to verify at promote time
- Pending escalations are invisible between start and decide
- Failed/unknown jobs have no diagnostic artifacts

With it, the full delegation lifecycle is: `start → (escalate → decide)* → poll → promote`.

### Project State

- **T-05:** COMPLETE. Both slices merged to main at `271f23aa`. 698 tests.
- **T-06 decide:** COMPLETE AND MERGED at `e041c896`. 734 tests.
- **T-06 spec amendments:** COMPLETE AND MERGED at `db7fd1da` (PR #110). Docs-only.
- **T-06 poll:** IMPLEMENTED. PR #111 open on `feature/t06-delegate-poll`. 712 tests. 7 commits.
- **Worktree:** `../claude-code-tool-dev-poll` on `feature/t06-delegate-poll` at `a8ab1ca1`.
- **Next T-06 slices:** promote, delegate skill UX.

## Learnings

### Subagent per-task reviewers cannot catch cross-cutting spec violations

**Mechanism:** Each spec reviewer only sees its own task's requirements and code. The hash sort-order bug required comparing `_review_hash` iteration order against `promotion-protocol.md:62` ("sorted by relative path"). The known-value hash test independently computed the expected hash by iterating `snapshot.artifact_paths` — the same insertion order as production — creating a tautological verification that couldn't detect the ordering error.

**Evidence:** All 4 spec reviews passed. The user's manual review caught 3 defects (hash order, wire-layer decisions, corrupt cache) plus 2 follow-up defects (reconstruction-vs-degradation, manifest validation). All required cross-module knowledge.

**Implication:** For spec-critical properties (hash recipes, protocol boundaries, crash-safety invariants), manual review against the authority documents is necessary even with automated review pipelines. The automated pipeline catches ~80% of issues (12 of 17 total findings); the remaining ~20% require broader context.

### Known-value tests must compute expected values independently from production code

**Mechanism:** The hash test at `test_artifact_store.py` was designed to catch `b"\\0"` vs `b"\0"` byte-level errors. It did this by independently computing the hash — but it iterated `snapshot.artifact_paths` which has the same insertion order as production code. The test could catch byte-level errors but not ordering errors because both sides used the same wrong order.

**Evidence:** The test passed with the wrong ordering. The fix: sort independently in the test by relative path, matching the spec's requirement.

**Implication:** When testing deterministic output (hashes, checksums, canonical formats), the test must derive the expected value from the spec, not from the production code's output. If the test mirrors the production code's approach, it can only catch implementation bugs, not design bugs.

### Projection boundaries must scrub value domains, not just field presence

**Mechanism:** `PendingEscalationView` was designed to scrub internal IDs (`codex_thread_id`, `codex_turn_id`, `item_id`) — and it did. The test `assert not hasattr(polled.pending_escalation, "codex_thread_id")` verified this. But `available_decisions` was forwarded unchanged from the wire layer, exposing `accept`/`decline`/`cancel` instead of the plugin's `approve`/`deny` vocabulary.

**Evidence:** `approval_router.py:20-34` defines wire-layer decisions. `models.py:34` defines `DecisionAction = Literal["approve", "deny"]`. The projection stripped structural internals but passed through semantic internals.

**Implication:** Projection boundaries need two checks: (1) field presence (are internal fields removed?) and (2) value domain (are remaining field values caller-appropriate?). The first is easier to test; the second requires knowing what values are valid at the caller boundary.

### Cache-corruption recovery must distinguish "never cached" from "previously cached but corrupt"

**Mechanism:** `load_snapshot` returning `None` has two meanings: (1) no snapshot exists yet (first poll), (2) snapshot exists but is corrupt. The recovery path for (1) is materialize from worktree. The recovery path for (2) must NOT materialize from the worktree because the worktree may have changed since the original review. The discriminant is `job.artifact_hash` in the store — if non-None, the job was previously materialized.

**Evidence:** User reproduced the issue: first poll → hash X, mutate worktree, corrupt snapshot.json, next poll → hash Y (different). The new hash would overwrite the store, silently breaking the review-to-promote integrity boundary.

**Implication:** Any cache-corruption recovery path that touches a secondary source (worktree, external API) must verify whether the cache was the authority for an already-committed state. If so, reconstruct from the committed state (store + immutable artifacts), not from the mutable source.

## Next Steps

### 1. Merge PR #111 after review

**Dependencies:** PR review approval.

**What to do:** Check PR #111 status. If approved, merge. After merge, clean up worktree and feature branch.

### 2. Implement `codex.delegate.promote`

**Dependencies:** Poll merged to main.

**Scope:** HEAD/base-commit match, clean worktree/index, `job_not_reviewed` check, artifact hash regeneration from worktree state (not re-hashing stored snapshot), completed-job precondition, typed rejection responses, rollback, advisory-stale signaling.

### 3. Sidecar hardening (can parallel with promote)

**Items:**
- MCP-layer test for malformed-answers rejection path
- Approve-path finalization guard regression test
- `codex.delegate.start` PreToolUse scan policy (the pre-existing gap)
- Start/decide `PendingServerRequest` projection to `PendingEscalationView`

## In Progress

**Clean stopping point.** All implementation done, PR open, no code changes in flight.

- **Completed:** 7 commits on `feature/t06-delegate-poll`. 712 tests passing. PR #111 open.
- **Not in flight:** No uncommitted changes. Worktree clean.
- **Next action for next-session Claude:** Check PR #111 status. If approved, merge. After merge, begin promote implementation.

## Open Questions

### 1. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** Handler calls `entry.session.interrupt_turn()` from inside `_server_request_handler`. Sends `turn/interrupt` via same transport reading notifications.

**Decision pending until:** Live testing against real App Server.

### 2. `on-request` operational semantics (inherited from T-05)

**Context:** Vendored schema proves `on-request` is a valid `approvalPolicy` value but operational semantics undocumented. Controller defaults to `untrusted`.

**Decision pending until:** Live probe against real App Server.

### 3. Test-results persistence in execution runtime

**Context:** The execution prompt instructs the agent to persist at `.codex-collaboration/test-results.json`. If the agent ignores this, all jobs degrade to `"not_recorded"` stubs. The deterministic fallback ensures poll works, but the promote hash includes the stub content.

**Decision pending until:** Live execution testing with the amended prompt.

## Risks

### 1. `_decided_request_ids` is in-memory only (inherited)

If cross-session decide is added, the in-memory set won't persist across restarts. For same-session-only design, this is correct.

### 2. `_FakeSession` complexity continues to grow (inherited)

The fake session has multiple methods and configurable state. Drift from real `AppServerRuntimeSession` interface could mask production failures.

### 3. `reviewed_at` timestamp lost during cache reconstruction

When `reconstruct_from_artifacts` rebuilds from stored artifacts, the original `reviewed_at` is lost (snapshot.json was corrupt). The reconstructed snapshot uses the current timestamp. This is informational-only and does not affect the review hash, but the timestamp no longer reflects the original review time.

### 4. Pre-existing `codex.delegate.start` missing from `consultation_safety.py`

The hook blocks `codex.delegate.start` calls (fail-closed via exit 2) because there's no policy entry. This is a pre-existing gap tracked as a sidecar hardening item.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| Poll implementation plan | `docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md` | Implementation authority |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Schema authority |
| Promotion protocol | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | Hash recipe, materialization, verification |
| Foundations | `docs/superpowers/specs/codex-collaboration/foundations.md` | High-level flow |
| Recovery spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Recovery semantics |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-20_11-44_t06-poll-plan-scrutinized-ready-for-implementation.md`
- T-05/T-06 arc: execution-start → pending-request capture → T-05 closed → T-06 decide plan → T-06 decide implemented → T-06 decide merged → T-06 poll spec amendments → T-06 poll plan scrutinized → **T-06 poll implemented (this handoff)**

### PR chain

| PR | Title | Status |
|----|-------|--------|
| #109 | T-06 decide opening slice | Merged (`e041c896`) |
| #110 | Spec amendments for codex.delegate.poll | Merged (`db7fd1da`) |
| #111 | feat(t20260330-06): implement codex.delegate.poll | **Open** (`a8ab1ca1`) |

### Commit chain on `feature/t06-delegate-poll`

| Commit | Message |
|--------|---------|
| `f781c4c4` | feat(t20260330-06): pin poll model and job-store contract |
| `bebe3705` | feat(t20260330-06): add delegation poll artifact materialization |
| `9e360b01` | feat(t20260330-06): implement delegation poll controller flow |
| `8e7dee37` | feat(t20260330-06): wire codex delegate poll mcp surface |
| `ddf90a96` | fix(t20260330-06): hash sort order, plugin-level decisions, corrupt snapshot resilience |
| `ae480a92` | fix(t20260330-06): guard reviewed hash from corrupt-cache rematerialization |
| `a8ab1ca1` | fix(t20260330-06): validate artifact files before reconstruction |

## Gotchas

### 1. Hash recipe must sort artifact_paths by relative path

**Symptom:** Hash mismatch at promote time despite clean review.

**Root cause:** `_review_hash` iterated in insertion order. The spec at `promotion-protocol.md:62` requires "sorted by relative path."

**Prevention:** The hash test now independently sorts by relative path. Any future changes to the hash recipe must update both the production sort and the test's independent computation.

### 2. `PendingEscalationView.available_decisions` must use plugin vocabulary

**Symptom:** Poll returns `("accept", "acceptForSession", "decline", "cancel")` but decide only accepts `("approve", "deny")`.

**Root cause:** `_project_pending_escalation` forwarded wire-layer values from `approval_router.py`.

**Prevention:** Controller now hardcodes `_PLUGIN_DECISIONS = ("approve", "deny")`. Test asserts exact tuple match.

### 3. `reconstruct_from_artifacts` must validate all artifact files exist

**Symptom:** Poll returns snapshot with `artifact_paths` referencing non-existent files.

**Root cause:** Original reconstruction only checked if the method was called, not if the underlying files were still present.

**Prevention:** Method now returns `None` if any `artifact_paths` entry doesn't exist on disk. Test covers both missing-file and malformed-manifest cases.

### 4. `snapshot.json` corruption must not trigger worktree rematerialization for reviewed jobs

**Symptom:** Reviewed hash silently changes after cache corruption.

**Root cause:** Original code didn't distinguish "never materialized" from "cache corrupt." Both fell through to `materialize_snapshot` from the worktree.

**Prevention:** `_load_or_materialize_inspection` checks `job.artifact_hash is not None` before falling through. If hash exists, calls `reconstruct_from_artifacts` instead.

## Conversation Highlights

### User's hash-order finding

User presented the finding with full evidence chain: "artifact_store.py:58 and artifact_store.py:181 compute the review hash in tuple order, not the sorted-relative-path order required by promotion-protocol.md:60. Because the tuple is built as full.diff, changed-files.json, test-results.json, the stored hash is off-spec. The test at test_artifact_store.py:141 repeats the same wrong order, so the suite stays green while the protocol is violated."

— Demonstrates the pattern: the test was designed to catch byte-level errors but structurally couldn't catch ordering errors.

### User's wire-layer decision finding

User: "delegation_controller.py:764 returns request.available_decisions directly, but those values are populated from the wire-layer parser in approval_router.py:20. That means poll can surface accept / decline / cancel for command approvals, or even () for request_user_input, while the plugin's decision tool only accepts approve / deny."

— Identified a projection boundary that stripped structural internals (field presence) but leaked semantic internals (value domain).

### User's reconstruction-vs-degradation pushback

User: "The new artifact_hash guard preserves the reviewed hash, but it does so by returning inspection=None for a completed job even when the persisted inspection files still exist and the job still advertises them through job.artifact_paths / job.artifact_hash. The contract says inspection is present whenever inspection artifacts are available."

— Pushed back on the minimal fix (return None) as a contract violation, requiring the fuller reconstruction approach.

## User Preferences

### Review-then-fix cycle

User performs independent review against authority documents after each implementation round, presenting findings as structured `::code-comment` annotations with priority, confidence, file locations, and reproduction evidence. Claude fixes, user re-reviews. This cycle repeated 3 times in this session (rounds 1-3).

### Evidence-first findings

Every finding includes: exact file:line, reference to the authority document, reproduction evidence ("I reproduced this on the branch"), and confidence rating. User expects the same evidence density in fixes.

### Plan-as-implementation-authority

User authored the plan externally, scrutinized it in the prior session, and expected implementation to follow it faithfully. Subagent-driven-development was explicitly requested as the execution method.

### Iterative hardening over scope expansion

User identified 5 defects across 3 review rounds, each time fixing the specific issue without expanding scope. No feature additions, no refactoring, no "while we're here" changes. Each fix was exactly scoped to the finding.
