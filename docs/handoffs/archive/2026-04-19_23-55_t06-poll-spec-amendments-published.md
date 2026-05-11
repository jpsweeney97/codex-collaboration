---
date: 2026-04-19
time: "23:55"
created_at: "2026-04-20T03:55:21Z"
session_id: 7c129485-c471-4cf7-9b4f-14b0f287542e
resumed_from: "docs/handoffs/archive/2026-04-19_23-20_t06-decide-merged-poll-next.md"
project: claude-code-tool-dev
branch: feature/t06-poll-spec-amendments
commit: 47a1fbff
title: "T-06 poll spec amendments — contracts, promotion protocol, foundations amended and PR #110 opened"
type: handoff
files:
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/specs/codex-collaboration/promotion-protocol.md
  - docs/superpowers/specs/codex-collaboration/foundations.md
---

# T-06 Poll Spec Amendments — Contracts, Promotion Protocol, Foundations Amended and PR #110 Opened

## Goal

Amend the codex-collaboration spec with the typed response shapes, store API gaps, and semantic mismatches required before `codex.delegate.poll` implementation.

**Trigger:** Prior handoff said "Next action for next-session Claude: Begin the design/reconciliation pass for `codex.delegate.poll`. Read the contract, promotion protocol, and decide plan deferrals. The user will write the plan; Claude scrutinizes."

**Stakes:** Poll is the seam that reconnects runtime state, caller inspection, artifact review, and the promotion chain. Without these spec amendments, poll is under-specified and promote's hash contract has no credible backing. Every implementation decision would be made ad hoc against an incomplete contract.

**Success criteria (all met):**
1. Typed `PollResult`, `PollRejection`, `PendingEscalationView`, `ArtifactInspectionSnapshot` added to `contracts.md`
2. `promotion_state` nullability reconciled with backcompat note
3. Promotion preconditions split from 5 to 6 (`job_not_reviewed` separated from `artifact_hash_mismatch`)
4. Artifact hash integrity section rewritten with materialization, canonical review set, hash recipe, and promotion verification
5. Foundations delegation flow updated from 8 to 9 steps
6. PR #110 opened and scoped to docs-only commit

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. T-06 decide slice complete and merged at `e041c896` (PR #109). This session produced the spec amendments required before the poll implementation plan. Remaining T-06 slices: poll implementation plan → poll implementation → promote → delegate skill.

## Session Narrative

**Phase 1 — Handoff load and context gathering (~10 min).** Loaded the prior handoff (`2026-04-19_23-20_t06-decide-merged-poll-next.md`). Read all four authority documents in parallel: `contracts.md` (320 lines), `promotion-protocol.md` (99 lines), T-06 ticket (89 lines), and the decide plan's deferrals section (`docs/plans/2026-04-19-t06-decide-opening-slice.md:2170-2215`). Also read `recovery-and-journal.md:100-178` for crash recovery paths and retention defaults.

**Phase 2 — Reconciliation pass (~15 min).** Mapped what the contract specifies (poll exists as a named tool at `contracts.md:26` but has no typed response shape), what the promotion protocol requires from poll (artifact hash computation at review time per `promotion-protocol.md:38`), and what the decide plan explicitly deferred to poll (cross-session restart handling, follow-up turn inspectability, discard action, PreToolUse scan policy per decide plan lines 2196-2200). Checked existing store APIs: `DelegationJobStore` has `create()`, `get()`, `list()`, `list_active()`, `update_status()` — no artifact mutation path. `PendingRequestStore` has `list_by_collaboration_id()`. `ExecutionRuntimeRegistry` has `lookup()`.

Identified seven open design questions: response shape, artifact hash trigger, `unknown` status context, single-job vs list mode, running-job progress, discard action placement, and MCP dispatch shape.

**Phase 3 — User pushback and three seams (~5 min).** User pushed on the reconciliation, identifying three load-bearing seams rather than two:

1. **No artifact mutation API** — `DelegationJobStore` only has `update_status()`, no `update_artifact_hash()` or general field update.
2. **`promotion_state="pending"` semantic mismatch** — Controller assigns `promotion_state="pending"` at job creation (`delegation_controller.py:473`) but the promotion protocol defines `pending` as "Job completed; awaiting promotion decision" (`promotion-protocol.md:60`).
3. **No artifact snapshot persistence** — `artifact_paths` starts empty, no code path populates it or `artifact_hash`.

User made specific calls on all seven design questions: projection not raw store rows (to avoid leaking `codex_thread_id`/`codex_turn_id`/`item_id`), lazy-idempotent hash (not "first poll" semantics), `unknown` coarse in v1, `job_id` required, running-job progress deliberately thin, discard not in poll.

**Phase 4 — Amendment set design (~5 min).** User presented the minimum defensible amendment set: typed `DelegationPollResult`, normalized `PendingEscalationView`, `ArtifactInspectionSnapshot` contract, `unknown` granularity decision, `promotion_state` reconciliation. Renamed `ArtifactReviewSnapshot` to `ArtifactInspectionSnapshot` because poll serves both completed-job review and `unknown`-job inspection per `recovery-and-journal.md:116`.

**Phase 5 — Scrutiny and two additions (~10 min).** Verified all three user-identified seams against the code. Confirmed `promotion_state="pending"` at `delegation_controller.py:473` with `status="queued"`, `DelegationJobStore` has only `create` and `update_status` ops, and `artifact_paths` defaults to `()`. Added two items: (1) backcompat replay note for `promotion_state` nullability — existing JSONL records with `promotion_state="pending"` for non-completed jobs must not be rejected or interpreted as promotion-eligible, (2) pre-existing `PendingServerRequest` leak in start/decide MCP serialization (`mcp_server.py:371`, `mcp_server.py:428`) — both use raw `asdict()`, leaking internal Codex IDs. User agreed with both additions and tightened the backcompat phrasing.

**Phase 6 — Implementation (~15 min).** Created branch `feature/t06-poll-spec-amendments` from main. Applied amendments to three files: `contracts.md` (DelegationJob field changes, Promotion Rejection enum, 4 new typed shapes), `promotion-protocol.md` (preconditions table 5→6, Artifact Hash Integrity rewrite with 4 subsections), `foundations.md` (delegation flow 8→9 steps). Ran consistency verification via explore agent — all cross-references valid, no orphaned anchors.

**Phase 7 — User review findings and fixes (~5 min).** User identified two blocking issues:

1. **P1:** Promotion Verification section said "recomputes from current artifact files" — ambiguous between re-hashing stored snapshot (self-referential) and regenerating from worktree state (tamper-evident). Fixed: "regenerates the canonical review set from the current worktree state... Promote does not hash the persisted snapshot files — it independently regenerates and hashes."
2. **P2:** Foundations step 6 said "eligible for review and promotion" but `job_not_reviewed` means completion only enables review, not promotion. Fixed: "eligible for review via `codex.delegate.poll`. Promotion eligibility requires a reviewed snapshot to exist."

**Phase 8 — Commit and publication (~5 min).** Unstaged unrelated `test_execution_prompt_builder.py` change. Committed spec-only at `47a1fbff`. Pushed branch. Opened PR #110 scoped to the three spec files.

## Decisions

### Decision 1: `ArtifactInspectionSnapshot` naming over `ArtifactReviewSnapshot`

**Choice:** Name the artifact bundle `ArtifactInspectionSnapshot`, not `ArtifactReviewSnapshot`.

**Driver:** User identified that poll serves two contexts: completed-job review (hash-backed, feeds promotion) and `unknown`/`failed`-job inspection (no hash, informational only). `recovery-and-journal.md:118-123` says "Expose inspection data through `codex.delegate.poll`" — the recovery spec uses "inspection," not "review."

**Alternatives considered:**
- **`ArtifactReviewSnapshot`** — Claude's original naming. Rejected because it implies the snapshot is always review-quality (hash-backed), but `unknown` jobs produce inspection-only snapshots without hash backing.

**Trade-offs accepted:** The name is slightly less specific for the completed-job case. But it correctly covers both use cases without needing two separate types.

**Confidence:** High (E2) — both the recovery spec language and the type's `artifact_hash: string?` (null for inspection-only) confirm the dual purpose.

**Reversibility:** High — naming is a spec-level choice, not an implementation commitment.

**Change trigger:** If `unknown`-job inspection evolves into a separate tool or shape, the naming could split.

### Decision 2: `job_not_reviewed` precondition split from `artifact_hash_mismatch`

**Choice:** Add precondition 5 (`job_not_reviewed`: reviewed artifact hash must exist) separate from precondition 6 (`artifact_hash_mismatch`: hash must match).

**Driver:** Without this split, calling `promote` without first polling a completed job produces `artifact_hash_mismatch` (expected: reviewed hash, actual: null). This error is misleading — the problem is not a mismatch but that review never happened. The split gives an actionable rejection: "poll first" vs "artifacts changed."

**Alternatives considered:**
- **Overload `artifact_hash_mismatch`** — fewer rejection reasons, simpler enum. Rejected because the caller can't distinguish "I forgot to poll" from "something changed the artifacts" — fundamentally different failure modes requiring different remediation.

**Trade-offs accepted:** One more rejection reason in the enum. Requires `contracts.md` Promotion Rejection and `promotion-protocol.md` preconditions to stay in sync.

**Confidence:** High (E2) — the two failure scenarios are structurally different: one is a workflow ordering error, the other is an integrity violation.

**Reversibility:** High — a rejection reason can be merged back by mapping `job_not_reviewed` to `artifact_hash_mismatch` in the implementation.

**Change trigger:** If a future "auto-review" mode is added where promote implicitly materializes the snapshot, `job_not_reviewed` would become unreachable. Remove it then.

### Decision 3: Promote regenerates from worktree, does not re-hash stored snapshot

**Choice:** At promotion time, `codex.delegate.promote` regenerates the canonical review set from current worktree state and hashes that regenerated set, rather than re-hashing the persisted snapshot files.

**Driver:** User's P1 review finding. If promote hashed the persisted snapshot, it would always match — comparing a file's hash to itself is self-referential. The tamper-evidence guarantee requires promote to independently derive the same artifact set from the live worktree and compare that hash to the stored one. Same principle as content-addressable storage: the address (hash) is derived from the content, not stored alongside it.

**Alternatives considered:**
- **Re-hash persisted snapshot files** — simpler implementation. Rejected because it's self-referential: any modification to the worktree after review would be undetected, since promote would hash the snapshot (which hasn't changed) rather than the worktree (which has).

**Trade-offs accepted:** Promote must run the same artifact computation as poll, which adds compute cost. The canonical review set (diff, changed-files manifest, test results) must be derivable from `base_commit + worktree_path` — any non-reconstructable artifact (e.g., test results from a now-modified test) would produce a false mismatch.

**Confidence:** High (E2) — the self-referential flaw in re-hashing stored files is structural.

**Reversibility:** Low — this is an architectural choice about what the hash represents. Changing it would alter the integrity semantics of the entire delegation flow.

**Change trigger:** None — the regeneration approach is strictly more correct. The only scenario where re-hashing stored files would be acceptable is if the worktree is guaranteed immutable between review and promotion, which it is not.

### Decision 4: `promotion_state` nullable — fix semantics, don't broaden spec

**Choice:** Make `promotion_state` nullable (`enum?`), null until job reaches `status=completed`. Do not broaden the spec to match the current implementation's `promotion_state="pending"` at creation.

**Driver:** `promotion-protocol.md:60` defines `pending` as "Job completed; awaiting promotion decision." The implementation assigns `pending` at job creation (`delegation_controller.py:473`) before the job has even started. Broadening the spec to match this would weaken the state machine — losing the ability to distinguish "job is running" from "job completed and awaiting promotion."

**Alternatives considered:**
- **Broaden `pending` to mean "any job that exists"** — matches current implementation without code changes. Rejected because it's a spec hack that weakens expressiveness.
- **Add a new state like `not_applicable`** — more explicit than null. Rejected as unnecessary verbosity when null conveys the same semantics.

**Trade-offs accepted:** Implementation change required: `delegation_controller.py:473` must change from `promotion_state="pending"` to `promotion_state=None`. 14 test sites construct `DelegationJob` with `promotion_state="pending"` for non-completed jobs and will need updating. Backcompat: existing JSONL records with `promotion_state="pending"` on non-completed jobs must be accepted on replay and must not be interpreted as promotion-eligible.

**Confidence:** High (E2) — the semantic mismatch is structural: `pending` at creation directly contradicts the promotion protocol's definition.

**Reversibility:** Medium — the type change touches the store, model, controller, and 14+ test sites. But the JSONL backcompat note means existing data is preserved.

**Change trigger:** N/A — this is a correction, not a preference.

### Decision 5: Hash recipe canonicalization (SHA-256, sorted path + NUL + bytes)

**Choice:** Artifact hash computed over persisted files listed in `artifact_paths`, sorted by relative path. For each file: `relative_path + NUL + file_bytes`. The concatenation is hashed with SHA-256.

**Driver:** Without a canonical ordering and separator rule, the integrity promise is underspecified. Different iteration orders on different filesystems would produce different hashes for identical artifact sets. The NUL separator prevents path/content boundary ambiguity.

**Alternatives considered:**
- **Hash each file separately, then hash the hashes** — Merkle-tree style. More complex, enables partial verification. Rejected because partial verification is not needed in v1 — the integrity check is all-or-nothing.
- **No explicit canonicalization** — leave to implementation. Rejected because any implementation-level ordering difference between poll-time and promote-time computation silently produces false mismatches.

**Trade-offs accepted:** The NUL separator prevents the artifact set from including files with NUL bytes in their paths (unusual but possible on some filesystems). Acceptable constraint.

**Confidence:** High (E2) — the canonicalization requirement is a standard property of content-addressable systems. SHA-256 is the project's existing hash algorithm.

**Reversibility:** Medium — the hash recipe is committed to the spec. Changing it invalidates all existing reviewed snapshots. But v1 has no persisted snapshots yet, so changing before implementation is free.

**Change trigger:** If partial verification becomes needed (e.g., promoting only some artifacts), a Merkle-tree approach would be better.

### Decision 6: Pre-existing PendingServerRequest leak tracked, not fixed in this slice

**Choice:** Note the pre-existing leak of `codex_thread_id`, `codex_turn_id`, `item_id` through start/decide MCP serialization as a hardening sidecar item. Do not fix in the poll spec amendment slice.

**Driver:** The leak is pre-existing (`mcp_server.py:371` and `mcp_server.py:428` both use raw `asdict()` on `PendingServerRequest`). Poll introduces the `PendingEscalationView` projection that correctly hides internal IDs. Fixing start/decide to also use this projection is a separate concern that would scope-creep the docs-only amendment.

**Alternatives considered:**
- **Fix start/decide in this slice** — complete fix. Rejected because this is a docs-only spec amendment; adding implementation changes would mix concerns and delay the PR.
- **Ignore the leak** — simplest. Rejected because leaving it unnoted means it would be rediscovered and re-analyzed in a future session.

**Trade-offs accepted:** Inconsistency: poll projects internal IDs away while start/decide expose them. Acceptable because the leak is pre-existing and not introduced by poll.

**Confidence:** High (E2) — verified at `mcp_server.py:371` (`asdict(result.pending_request)` in start) and `mcp_server.py:428` (`asdict(result.pending_request)` in decide).

**Reversibility:** N/A — this is a triage decision (defer, not fix), not a code change.

**Change trigger:** When poll implementation lands, the sidecar should be scheduled.

## Changes

### `contracts.md` — DelegationJob field amendments

**Purpose:** Fix `promotion_state` nullability, tighten `artifact_paths` and `artifact_hash` descriptions to poll-materialized semantics.

**Key details:**
- `promotion_state` changed from `enum` to `enum?` with "Null until promotion lifecycle becomes applicable" and backcompat note: "Upgraded implementations must accept legacy records with `promotion_state="pending"` on non-completed jobs and must not interpret them as promotion-eligible solely from that legacy value."
- `artifact_paths` description changed from "Paths to produced artifacts" to "Absolute paths to persisted inspection artifacts materialized by `codex.delegate.poll`. Empty until poll first materializes inspection data."
- `artifact_hash` description changed from generic to "Hash of the reviewed artifact set for a completed job. Null until `codex.delegate.poll` has materialized a reviewable completed-job snapshot."

### `contracts.md` — Promotion Rejection enum extension

**Purpose:** Add `job_not_reviewed` to the `reason` enum for Promotion Rejection.

**Key details:** Enum now includes `head_mismatch`, `index_dirty`, `worktree_dirty`, `artifact_hash_mismatch`, `job_not_completed`, `job_not_reviewed`.

### `contracts.md` — Four new typed response shapes

**Purpose:** Define the poll tool's public contract surface.

**Key details:**
- **Poll Rejection** — `rejected: true`, `reason: "job_not_found"`, `detail`, `job_id?`. Minimal rejection for a read tool.
- **Pending Escalation View** — Projection of `PendingServerRequest` that hides internal Codex IDs. Fields: `request_id`, `kind`, `requested_scope`, `available_decisions`. Note about pre-existing leak in start/decide.
- **Artifact Inspection Snapshot** — `artifact_hash: string?` (null for inspection-only), `artifact_paths`, `changed_files`, `reviewed_at`. Hash present only for completed-job snapshots.
- **Poll Result** — `job` (DelegationJob), `pending_escalation?` (PendingEscalationView, present when `needs_escalation`), `inspection?` (ArtifactInspectionSnapshot, present when artifacts available), `detail?` (human-readable for `failed`/`unknown`).

### `promotion-protocol.md` — Preconditions table split

**Purpose:** Split precondition 4 into two: `job_not_completed` (precondition 4), `job_not_reviewed` (precondition 5), `artifact_hash_mismatch` (precondition 6).

**Key details:** Reordered so `job_not_completed` is checked first (must be completed), then `job_not_reviewed` (must have been polled), then `artifact_hash_mismatch` (hash must match). Logical dependency order.

### `promotion-protocol.md` — Artifact Hash Integrity rewrite

**Purpose:** Replace the 6-line summary with a fully specified section containing four subsections.

**Key details:**
- **Materialization:** Lazy-idempotent. First poll of completed job with no snapshot → compute, persist, return. Subsequent polls return persisted snapshot.
- **Canonical Review Set:** At least: full diff against `base_commit`, changed-files manifest, test-results record. Additional artifacts allowed but must participate in promote-time recomputation.
- **Hash Recipe:** SHA-256 over sorted `relative_path + NUL + file_bytes`.
- **Promotion Verification:** Promote regenerates canonical review set from current worktree state, hashes with same recipe, compares to stored hash. Does NOT re-hash persisted snapshot files.

### `foundations.md` — Delegation flow steps 6-9

**Purpose:** Fix the delegation flow narrative to match the amended contracts and promotion protocol.

**Key details:**
- Step 6: "When the job reaches `completed`, the job becomes eligible for review via `codex.delegate.poll`. Promotion eligibility requires a reviewed snapshot to exist."
- Step 7: "On first `codex.delegate.poll` of a completed job, the plugin materializes the inspection artifacts, computes the reviewed artifact hash, and returns the review snapshot."
- Step 8: "Claude reviews the result."
- Step 9: "If accepted, `codex.delegate.promote` applies the diff into the main workspace."

## Codebase Knowledge

### Spec File Architecture

| File | Lines | Purpose | Amendment scope |
|------|-------|---------|-----------------|
| `contracts.md` | 320→366 | All typed interfaces, data model, audit schema | DelegationJob fields, 4 new shapes, rejection enum |
| `promotion-protocol.md` | 99→126 | Promotion preconditions, state machine, rollback | Preconditions split, hash integrity rewrite |
| `foundations.md` | 323→324 | High-level flows, prompting contract, context assembly | Delegation flow steps only |
| `recovery-and-journal.md` | 178 | Crash recovery, journal, concurrency, retention | Not amended (referenced only) |
| `delivery.md` | ~250 | Build sequence, capability mapping | Not amended |

### Store API Surface (poll-relevant)

| Store | File | Key APIs | Poll gap |
|-------|------|----------|----------|
| `DelegationJobStore` | `delegation_job_store.py` | `create()`, `get()`, `list()`, `list_active()`, `update_status()` | No `update_artifact_hash()`, no `update_promotion_state()`, no general field update. `_replay()` only handles `op: "create"` and `op: "update_status"`. |
| `PendingRequestStore` | `pending_request_store.py` | `create()`, `get()`, `list_pending()`, `list_by_collaboration_id()`, `update_status()` | Adequate for poll reads |
| `ExecutionRuntimeRegistry` | `execution_runtime_registry.py` | `register()`, `lookup()`, `release()`, `active_runtime_ids()` | Adequate for liveness check |
| `LineageStore` | (not read this session) | `get()`, `list()`, `update_status()`, `update_runtime()` | Adequate for handle lookup |

### MCP Serialization Pattern

The MCP layer at `mcp_server.py:335-433` uses `dataclasses.asdict()` for all response serialization. This is fast but produces raw store-level fields in the Claude-visible response. Specific leak points:

- `mcp_server.py:371` — `asdict(result.pending_request)` in `codex.delegate.start` escalation response
- `mcp_server.py:428` — `asdict(result.pending_request)` in `codex.delegate.decide` re-escalation response

Both expose `codex_thread_id`, `codex_turn_id`, `item_id` — fields the contract says are "internal to the control plane" at `contracts.md:37`.

### `promotion_state` Usage Map

| Location | Current value | After amendment |
|----------|---------------|-----------------|
| `models.py:24` | `PromotionState = Literal[...]` (no None) | `PromotionState` stays, field type becomes `PromotionState \| None` |
| `models.py:346` | `promotion_state: PromotionState` | `promotion_state: PromotionState \| None = None` |
| `delegation_controller.py:473` | `promotion_state="pending"` | `promotion_state=None` |
| `delegation_job_store.py:43-46` | Rejects if not in `_VALID_PROMOTION_STATES` | Must accept `None` |
| `delegation_job_store.py:133` | Replay validation same check | Must accept `None` and legacy `"pending"` for non-completed jobs |
| 14 test sites | `promotion_state="pending"` for non-completed jobs | Update to `promotion_state=None` (or keep `"pending"` where testing legacy compat) |

### Key Locations

| Concept | Location |
|---------|----------|
| DelegationJob field definitions | `contracts.md:63-73` (amended) |
| Promotion Rejection enum | `contracts.md:230` (amended) |
| Poll Rejection shape | `contracts.md:271` (new) |
| Pending Escalation View | `contracts.md:282` (new) |
| Artifact Inspection Snapshot | `contracts.md:295` (new) |
| Poll Result shape | `contracts.md:306` (new) |
| Promotion preconditions table | `promotion-protocol.md:16-23` (amended) |
| Artifact Hash Integrity | `promotion-protocol.md:36-70` (rewritten) |
| Delegation flow | `foundations.md:180-188` (amended) |
| `DelegationJobStore._replay()` | `delegation_job_store.py:90-150` |
| MCP start escalation leak | `mcp_server.py:371` |
| MCP decide re-escalation leak | `mcp_server.py:428` |
| Job creation (promotion_state) | `delegation_controller.py:473` |
| `recover_startup()` unknown marking | `delegation_controller.py:1183-1202` |

## Context

### Mental Model

This session was **spec amendment as design verification**. The design pass was not about reading the code and writing a plan — it was about identifying where the existing spec was underspecified, semantically inconsistent, or silently assumed implementation details. The three seams the user identified (no artifact mutation API, `promotion_state` mismatch, no artifact persistence) were all cases where the spec said one thing and the code did another — or the spec said nothing and the code filled the gap with a convenient default.

The key insight: poll is not a "simple read tool." It has a critical side effect (artifact materialization and hash computation) that anchors the entire promotion chain's integrity guarantee. Getting the spec right before implementation prevents the same kind of ad hoc decisions that led to `promotion_state="pending"` at creation time.

### Why This Session Matters

The spec amendments are the load-bearing precondition for poll implementation. Without them:
- Poll's response shape would be invented during implementation, creating implicit contract commitments
- The `promotion_state` mismatch would propagate into poll's status interpretation
- The artifact hash integrity guarantee would be underspecified — promote could re-hash stored files (self-referential, no tamper detection) instead of regenerating from worktree state
- The `PendingServerRequest` leak would be duplicated in poll rather than caught and projected away

### Project State

- **T-05:** COMPLETE. Both slices merged to main at `271f23aa`. 698 tests.
- **T-06:** Decide slice COMPLETE AND MERGED at `e041c896`. 734 tests. Spec amendments on `feature/t06-poll-spec-amendments` at `47a1fbff`. PR #110 open.
- **Branch:** `feature/t06-poll-spec-amendments` at `47a1fbff` (1 commit ahead of main).
- **Worktree:** None. Working in primary checkout.
- **PR #110:** Open. Docs-only, 3 files, 88 insertions, 13 deletions.

## Learnings

### Three automated review agents converging does not mean the finding is real — but three spec documents diverging means the gap is real

**Mechanism:** In the prior session, three review agents converged on a false positive (`action="approve"` for deny decisions). In this session, three spec documents diverged on `promotion_state` semantics — contracts.md defined `pending` as promote-ready, delegation_controller.py assigned `pending` at creation, and promotion-protocol.md assumed completion-time artifact computation. Three-way divergence is a stronger signal than three-way convergence.

**Evidence:** `contracts.md:70` (pre-amendment): `promotion_state: enum` with `pending` listed first. `delegation_controller.py:473`: `promotion_state="pending"` at job creation with `status="queued"`. `promotion-protocol.md:60` (pre-amendment): `pending` means "Job completed; awaiting promotion decision."

**Implication:** When reading a spec, check each field's invariant against every site that writes it. A field defined in one document and written in another can silently diverge.

### Self-referential hash checks provide no tamper evidence

**Mechanism:** If promote hashes the persisted snapshot (the files poll wrote), it's comparing a file's hash to itself — the hash always matches regardless of worktree modifications. Tamper-evidence requires independent regeneration: derive the artifact set from the live worktree, hash that, compare to the stored hash.

**Evidence:** User's P1 review finding on `promotion-protocol.md:60-66`. The original wording ("recomputes the hash from the same recipe using the current artifact files") was ambiguous between "current snapshot files" (self-referential) and "current worktree state" (tamper-evident).

**Implication:** Any integrity-check system where the verifier reads the same stored artifact that the prover wrote is self-referential. The verifier must independently derive the content to be verified.

### Spec amendments before implementation prevent contract drift

**Mechanism:** The `promotion_state="pending"` mismatch was introduced when `delegation_controller.py` was implemented against a spec that hadn't been reconciled for the poll/promote lifecycle. The code picked a convenient default (`"pending"`) that happened to be a valid enum value but had the wrong semantic meaning. If the spec had been amended before implementation, the field would have been nullable from the start.

**Evidence:** 14 test sites and 1 production site all use `promotion_state="pending"` for non-completed jobs. None of these sites checked whether `"pending"` was semantically correct — they just needed a valid value.

**Implication:** When a field has lifecycle semantics (its meaning changes as the parent object transitions through states), the spec must define when each value becomes applicable. "Valid enum value" is not the same as "semantically correct value."

## Next Steps

### 1. Wait for PR #110 review

**Dependencies:** None — PR is open at https://github.com/jpsweeney97/claude-code-tool-dev/pull/110

**What to do:** If comments come in, address them on `feature/t06-poll-spec-amendments`. If approved, merge as-is.

### 2. Write the poll implementation plan

**Dependencies:** PR #110 merged.

**What to read first:**
- Amended `contracts.md` for the typed response shapes (Poll Result, Poll Rejection, Pending Escalation View, Artifact Inspection Snapshot)
- Amended `promotion-protocol.md` for the materialization, hash recipe, and verification semantics
- `delegation_controller.py` for the existing controller structure and store wiring
- `delegation_job_store.py` for the store extension points (new `update_artifact` operation needed)
- `mcp_server.py` for the dispatch pattern

**Design considerations:**
- Poll is the first pure-read tool in the T-06 arc — but it has one critical side effect: artifact materialization on first poll of a completed job
- `DelegationJobStore` needs a new operation (e.g., `update_artifact`) that appends `artifact_hash`, `artifact_paths`, and `promotion_state` updates. The replay loop must handle this new op type.
- `PendingEscalationView` projection function needed (shared by poll, and later by start/decide when the sidecar hardening lands)
- Artifact computation: diff against `base_commit`, changed-files manifest from `git diff --name-only`, test results from... where? Test results may not be persisted by the execution runtime. This is the biggest open implementation question.

**Approach:** User writes the plan, Claude scrutinizes. Same pattern as the decide slice.

### 3. Sidecar hardening (alongside poll)

**Dependencies:** Can be done alongside poll implementation.

**Items:**
- MCP-layer test for malformed-answers rejection path (from prior session)
- Approve-path finalization guard regression test (from prior session)
- `codex.delegate.start` PreToolUse scan policy (deferred from decide plan at `docs/plans/2026-04-19-t06-decide-opening-slice.md:2200`)
- Start/decide `PendingServerRequest` projection to `PendingEscalationView` (new from this session)

### 4. After poll: `codex.delegate.promote`

**Dependencies:** Poll merged, spec amendments merged.

**Scope:** HEAD/base-commit match, clean worktree/index, `job_not_reviewed` check, artifact hash regeneration and verification, completed-job precondition, typed rejection responses, rollback, advisory-stale signaling.

### 5. After promote: delegate skill

**Dependencies:** Poll + promote merged.

**Purpose:** Wraps `start` / `poll` / `decide` / `promote` into a coherent UX surface.

## In Progress

**Clean stopping point.** PR #110 open, branch pushed, no work in flight. All spec amendments are in the committed state on the feature branch.

- **Completed:** Design/reconciliation pass, spec amendments, user review, two fix rounds, commit, push, PR creation.
- **Not in flight:** No code changes pending, no review comments to address yet.
- **Next action for next-session Claude:** Check PR #110 status. If approved, merge. If review comments, address them on `feature/t06-poll-spec-amendments`. After merge, begin the poll implementation plan.

## Open Questions

### 1. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** The handler calls `entry.session.interrupt_turn()` from inside the `_server_request_handler` callback. Sends a `turn/interrupt` JSON-RPC request via the same transport reading notifications.

**Impact:** Medium. If the transport doesn't handle re-entrant reads, the handler will deadlock.

**Decision pending until:** Live testing against the real App Server.

### 2. `on-request` operational semantics (inherited from T-05)

**Context:** The vendored schema proves `on-request` is a valid `approvalPolicy` value, but operational semantics are not documented. Controller defaults to `untrusted` per D1.

**Decision pending until:** Live probe against the real App Server.

### 3. Approve turn prompt shape adequacy (inherited from decide)

**Context:** `build_execution_resume_turn_text()` tells the execution agent "the earlier server request has already been resolved at the wire layer." Whether this prompt produces reliable follow-up behavior is unverified.

**Decision pending until:** Live execution testing.

### 4. Test-results persistence in execution runtime

**Context:** The artifact inspection snapshot includes "test-results record" in the canonical review set (`promotion-protocol.md` Canonical Review Set). But the execution runtime's `TurnExecutionResult` only returns `turn_id`, `status`, `agent_message`, and `notifications` (`models.py:136`). There is no dedicated test-results persistence. If the execution agent ran tests, results may only be in the `agent_message` text — not structured or persisted.

**Impact:** High for poll implementation. Either: (a) poll extracts test results from agent messages (fragile), (b) the execution prompt instructs the agent to persist test results to a known location in the worktree (reliable but adds a prompt requirement), or (c) the canonical review set omits test results in v1 (simplifies but weakens the review).

**Decision pending until:** Poll implementation plan.

## Risks

### 1. `_decided_request_ids` is in-memory only (inherited)

If cross-session decide is added, the in-memory set won't persist across restarts. For same-session-only design, this is correct.

### 2. `_FakeSession` complexity continues to grow (inherited)

The fake session has multiple methods and configurable state. Drift from real `AppServerRuntimeSession` interface could mask production failures.

### 3. Backcompat replay for `promotion_state` nullability

The spec amendment requires existing JSONL records with `promotion_state="pending"` for non-completed jobs to be accepted on replay. If the implementation doesn't handle this correctly, a cold restart after the code change would silently drop pre-change job records. The `_replay()` loop at `delegation_job_store.py:90-150` must be updated.

### 4. Test-results persistence is unresolved

The canonical review set includes test results, but no persistence mechanism exists. This could simplify (omit tests from v1) or complicate (add execution prompt requirements) the poll implementation. See Open Question 4.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| T-06 decide plan | `docs/plans/2026-04-19-t06-decide-opening-slice.md` | Decide implementation authority |
| Contracts (amended) | `docs/superpowers/specs/codex-collaboration/contracts.md` | Schema authority |
| Promotion protocol (amended) | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | Promotion semantics |
| Foundations (amended) | `docs/superpowers/specs/codex-collaboration/foundations.md` | High-level flow |
| Recovery spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Recovery semantics |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-19_23-20_t06-decide-merged-poll-next.md`
- T-05/T-06 arc: execution-start → pending-request capture → T-05 closed → T-06 decide plan → T-06 decide implemented → T-06 decide merged → **T-06 poll spec amendments (this handoff)**

### Commit chain (this session)

| Commit | Message |
|--------|---------|
| `47a1fbff` | `spec(t20260330-06): amend contracts, promotion protocol, and foundations for codex.delegate.poll` |

### PR

| PR | Title | Status |
|----|-------|--------|
| #110 | `spec(t06): amend contracts and promotion protocol for codex.delegate.poll` | Open |

## Gotchas

### 1. `promotion_state="pending"` assigned at job creation, not completion

**Symptom:** Poll or promote logic that trusts `promotion_state == "pending"` to mean "promote-ready" would incorrectly treat running/queued/escalated jobs as promotion candidates.

**Root cause:** `delegation_controller.py:473` sets `promotion_state="pending"` at job creation because `DelegationJob` requires a `PromotionState` value and `"pending"` was the only semantically reasonable choice. But `promotion-protocol.md:60` defines `pending` as "Job completed; awaiting promotion decision."

**Prevention:** After the spec amendment lands, implementation must change `promotion_state` to `None` at creation. Poll sets it to `"pending"` only when the job is `completed` and the artifact snapshot is materialized. Check `promotion_state is None or promotion_state == "pending"` when reading legacy records.

### 2. Promote must regenerate, not re-hash

**Symptom:** Promote always succeeds even when the worktree was modified after review.

**Root cause:** If promote hashes the persisted snapshot files (what poll wrote to disk), the hash is self-referential — it always matches.

**Prevention:** Promote must regenerate the canonical review set from current worktree state (`base_commit + worktree_path`), hash that regenerated set, and compare to the stored hash. The spec at `promotion-protocol.md:60-66` (amended) is explicit about this.

### 3. `PendingServerRequest` leaks internal Codex IDs through start and decide

**Symptom:** Claude can see `codex_thread_id`, `codex_turn_id`, `item_id` in `codex.delegate.start` escalation responses and `codex.delegate.decide` re-escalation responses.

**Root cause:** `mcp_server.py:371` and `mcp_server.py:428` use raw `asdict(result.pending_request)` instead of projecting to `PendingEscalationView`.

**Prevention:** Poll uses `PendingEscalationView` projection from the start. Start/decide projection is tracked as a hardening sidecar item noted in `contracts.md` Pending Escalation View section.

### 4. Backcompat: JSONL records with `promotion_state="pending"` for non-completed jobs

**Symptom:** After code change to nullable `promotion_state`, cold restart silently drops pre-change job records.

**Root cause:** `delegation_job_store.py:133` validation rejects records where `promotion_state` is not in `_VALID_PROMOTION_STATES`. If `None` is not handled, records with the old schema are accepted (they have `"pending"` which is valid) but records written with the new schema (`promotion_state: null` → omitted from JSON) would fail.

**Prevention:** Spec amendment includes backcompat note. Implementation must handle: (a) records with `promotion_state="pending"` for non-completed jobs (treat as null), (b) records with `promotion_state: null` or absent (treat as null). Both produce `DelegationJob` with `promotion_state=None`.

## Conversation Highlights

### User's three-seams pushback

User: "The main thing I'd push on is that the repo shows three load-bearing seams, not two." — Identified the `promotion_state` mismatch and artifact persistence gap beyond Claude's initial two-seam analysis.

### User's `ArtifactInspectionSnapshot` naming correction

User: "I would call the artifact shape `ArtifactInspectionSnapshot`, not `ArtifactReviewSnapshot`, because `poll` has to serve both completed-job review and `unknown`-job inspection per recovery-and-journal.md." — Grounded naming in spec language over ad hoc labeling.

### User's backcompat tightening

User: "I'd tighten the backcompat note slightly. Instead of requiring one specific replay normalization strategy, I'd phrase it as: upgraded implementations must accept legacy records with `promotion_state='pending'` on non-completed jobs and must not interpret them as promotion-eligible solely from that legacy value." — Preserved implementation freedom while constraining semantics.

### User's P1 review finding

User: "The spec currently mixes 'hash the persisted snapshot in `artifact_paths`' with 'recompute from current artifact files at promote time.' Unless you pin that to 'regenerate the canonical review set from current worktree state, then hash that regenerated set with the same recipe,' the tamper-evidence guarantee is still underspecified." — Caught a self-referential integrity check before it became an implementation bug.

## User Preferences

### Spec amendment authority: user designs, Claude scrutinizes and implements

The user presented the complete amendment set (typed shapes, naming, semantic decisions, hash recipe, backcompat note) with specific code references. Claude's role was verification, consistency checking, and identifying additions (backcompat replay note, PendingServerRequest leak note). The user then reviewed Claude's implementation for correctness.

### Naming grounded in spec language, not ad hoc labeling

User corrected `ArtifactReviewSnapshot` to `ArtifactInspectionSnapshot` by citing the recovery spec's use of "inspection." Pattern: names should derive from the authoritative document's vocabulary, not from the most intuitive English word.

### Backcompat notes should constrain semantics, not prescribe implementation

User tightened the backcompat note to say "must accept" and "must not interpret" rather than specifying a replay normalization strategy. Pattern: the spec defines what implementations must and must not do, not how they do it.

### Review is structural: P1/P2 with confidence levels

User submitted review as two numbered findings with priorities (P1/P2), file/line references, and explicit bodies describing the problem and required fix. Pattern: review feedback follows the same structure as the codebase's own review conventions.
