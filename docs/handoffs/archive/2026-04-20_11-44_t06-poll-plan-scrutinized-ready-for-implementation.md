---
date: 2026-04-20
time: "11:44"
created_at: "2026-04-20T15:44:29Z"
session_id: e1613b2e-135d-46c7-badc-201eaf1e8a04
resumed_from: "docs/handoffs/archive/2026-04-19_23-55_t06-poll-spec-amendments-published.md"
project: claude-code-tool-dev
branch: main
commit: db7fd1da
title: "T-06 poll implementation plan — scrutinized, revised, and approved for implementation"
type: handoff
files:
  - docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/specs/codex-collaboration/promotion-protocol.md
  - docs/superpowers/specs/codex-collaboration/foundations.md
---

# T-06 Poll Implementation Plan — Scrutinized, Revised, and Approved for Implementation

## Goal

Scrutinize the user-authored `codex.delegate.poll` implementation plan against the live codebase, iterate revisions to close all findings, and produce an approved plan ready for subagent-driven implementation.

**Trigger:** Prior handoff said "Next action for next-session Claude: Check PR #110 status. If approved, merge. After merge, begin the poll implementation plan." User wrote the plan externally and requested scrutiny.

**Stakes:** The poll plan is the first implementation authority document for `codex.delegate.poll`. If approved with latent defects (spec-divergent hash recipes, crash-window store ops, incomplete code snippets), the implementation agent would propagate those defects into production code. Scrutiny before implementation catches design-level errors when they're cheap to fix.

**Success criteria (all met):**
1. PR #110 (spec amendments) merged to main — ✓ at `db7fd1da`
2. Plan scrutinized through two full passes with adversarial perspectives — ✓
3. All critical and high-severity findings resolved in plan revisions — ✓
4. Plan approved as "Defensible" with no remaining findings — ✓
5. Plan ready for `superpowers:subagent-driven-development` execution — ✓

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. T-06 decide slice complete and merged at `e041c896` (PR #109). Spec amendments merged at `db7fd1da` (PR #110). This session produced the approved implementation plan. Remaining T-06 slices: poll implementation → promote → delegate skill.

## Session Narrative

**Phase 1 — Handoff load and PR merge (~5 min).** Loaded the prior handoff (`2026-04-19_23-55_t06-poll-spec-amendments-published.md`). Checked PR #110 status — open, mergeable, no reviews or comments. User approved merge. Merged PR #110 at `db7fd1da` and updated local main. Feature branch `feature/t06-poll-spec-amendments` is now merged and can be deleted.

**Phase 2 — Plan receipt and initial codebase cross-referencing (~10 min).** User presented the complete plan at `docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md` (1611 lines) and requested `/scrutinize`. Before issuing findings, verified the plan's assumptions against live codebase state:
- `DelegationController.__init__` signature at `delegation_controller.py:183-211` — confirmed no `artifact_store` parameter yet
- `promotion_state` type at `models.py:346` — confirmed `PromotionState` (non-nullable)
- `_VALID_PROMOTION_STATES` at `delegation_job_store.py:18` — confirmed `frozenset(get_args(PromotionState))` with no `None` handling
- `_replay()` loop at `delegation_job_store.py:90-150` — confirmed only handles `create` and `update_status` ops
- `consultation_safety.py` policy map — confirmed 4 entries, no `delegate.start` or `delegate.poll`
- `codex_runtime_bootstrap.py:113-128` — confirmed `DelegationController` construction without `artifact_store`
- `execution_prompt_builder.py` — confirmed 73 lines, no test-results persistence instructions
- Promotion state usage in controller at line 473 — confirmed `promotion_state="pending"` at creation
- 18 test-site occurrences of `promotion_state.*pending` across 5 test files (plan claimed 14)

**Phase 3 — First scrutiny pass (~15 min).** Issued full scrutiny with two passes and three adversarial perspectives:
- **Replay safety auditor** — exposed the two-write `_persist_job_transition` crash window (F1)
- **Spec-implementation conformance checker** — exposed `b"\\0"` vs `b"\0"` NUL byte divergence (A2, high severity)
- **Implementation agent perspective** — exposed incomplete `build_execution_resume_turn_text` snippet (B2)

Additional findings: dual-source-of-truth fragility between `snapshot.json` and `job.artifact_paths` (F2), `.codex-collaboration/test-results.json` appearing in `changed_files` (B1), `codex.delegate.start` pre-existing policy gap (A4). Verdict: `Minor revision`.

**Phase 4 — User pushback and tier calibration (~5 min).** User agreed with the verdict but pushed on three points:
1. **F1 is worse than stated** — `_load_or_materialize_inspection` only writes artifacts, not `promotion_state`. A `completed + None` crash state would be a permanent wedge, not self-healing. User demanded a single atomic store op, not just a comment.
2. **Fail-closed correction** — User corrected my claim that `codex.delegate.start` "silently approves." The hook at `codex_guard.py:49` catches `policy_for_tool()` failures and returns exit 2. The test at `test_codex_guard.py:148` already asserts unknown plugin tools block. My framing was incorrect.
3. **Mixed diff format** — Not a blocker for this packet. `full.diff` is a review artifact in the poll slice, not an apply surface.

User also added lower-severity revisions: snapshot-store rehydration (make `snapshot.json` authoritative, rehydrate store from it), `.codex-collaboration/` exclusion design lock, blast-radius file enumeration instead of counts.

**Phase 5 — User applies revisions externally (~10 min).** User edited the plan directly (not through Claude) and reported changes matching all agreed revisions. Plan grew from 1611 to 1775 lines (+164).

**Phase 6 — Second scrutiny pass (~10 min).** Verified all mandatory fixes:
- Atomic `update_status_and_promotion` at plan line 406-430 — single JSONL record, no crash window ✓
- NUL byte `b"\0"` at plan lines 630 and 901 — correct ✓
- Known-value hash test at plan lines 623-633 — independently computes expected hash ✓
- Prompt builder `requested_scope` via `json.dumps()` at plan lines 931-935, returns `"\n".join(lines)` ✓
- Snapshot-store rehydration at plan lines 1295-1306 — `snapshot.json` authoritative, store reconciled ✓
- `_FakeArtifactStore` at plan lines 1009-1032 — controller tests isolated from git ✓
- `.codex-collaboration/` exclusion from `_changed_files` at plan line 847 ✓

Found one remaining medium-severity issue: `_full_diff` starts with a blanket `git diff ... <base_commit> --` that includes ALL tracked changes including `.codex-collaboration/test-results.json` if the agent `git add`ed it. The `changed_files` exclusion only applies to the untracked-append section.

**Phase 7 — User applies final fix.** User added pathspec exclusion (`:!{TEST_RESULTS_RECORD_RELATIVE_PATH}`) at plan line 866 and a test assertion at plan line 590. Final verdict: `Defensible`, no remaining findings.

## Decisions

### Decision 1: Atomic `update_status_and_promotion` store op over two-write sequence

**Choice:** Replace the planned two-call sequence (`update_status` + `update_promotion_state`) with a single `update_status_and_promotion` JSONL append that carries both fields.

**Driver:** User identified that the crash window between two writes is worse than the initial scrutiny stated: `completed + promotion_state=None` is not self-healing because `_load_or_materialize_inspection` only writes artifacts, never `promotion_state`. A job stuck in this state would be permanently wedged — promote's `job_not_reviewed` precondition gates on `promotion_state == "pending"`.

**Alternatives considered:**
- **Two writes with a comment** — Claude's initial suggestion. Rejected because the comment doesn't prevent the crash-window defect, and "self-healing" was incorrect.
- **Store-level transaction wrapper** — add a general transaction mechanism. Rejected as over-engineering for a single compound op.

**Trade-offs accepted:** One more op type in `_replay()`. The replay loop grows from 2 to 3 branch arms (`create`, `update_status_and_promotion`, `update_artifacts`). Existing `update_status` calls in non-promotion paths (e.g., `recover_startup()` marking `unknown`) also use the compound op to keep the interface uniform.

**Confidence:** High (E2) — the crash-window analysis is structural. The wedge state is demonstrable from the code.

**Reversibility:** Low — once implemented, the JSONL records contain compound ops. Splitting them later requires a migration.

**Change trigger:** None — this is a correctness fix, not a preference.

### Decision 2: `snapshot.json` as poll-cache authority with store rehydration

**Choice:** Make `snapshot.json` the single source of truth for cached inspection data. If `snapshot.json` exists but the JSONL store's `artifact_paths`/`artifact_hash` fields are empty or divergent, poll rehydrates the store from the snapshot rather than re-materializing from the worktree.

**Driver:** User said the dual-source guard was "too hand-wavy" and that "if it exists while the store fields are empty, rehydrate the store from the snapshot instead of recomputing from the worktree." This eliminates the re-materialization-on-divergence path.

**Alternatives considered:**
- **Store as authority, re-materialize if snapshot missing** — inverts the polarity. Rejected because the store can lose records (truncated JSONL) while the snapshot file is more durable once written.
- **Check both, re-materialize if either is missing** — original plan approach. Rejected because it creates redundant computation and duplicate store writes.

**Trade-offs accepted:** If `snapshot.json` is corrupted, poll has no fallback — it cannot re-materialize without an explicit "re-poll" action. Acceptable because file corruption is rare and the snapshot is written atomically (`write_text` on a short JSON payload).

**Confidence:** High (E2) — the divergence scenarios are enumerable and the rehydration path is simpler than re-materialization.

**Reversibility:** High — the authority model is expressed in controller logic, not in the store schema.

**Change trigger:** If promote needs to invalidate snapshots (e.g., after a post-review worktree modification), a "snapshot version" or deletion mechanism would be needed.

### Decision 3: Exclude `.codex-collaboration/test-results.json` from `changed_files` and `full.diff`

**Choice:** Add a design lock (lock 7) that `.codex-collaboration/test-results.json` is instrumentation output, not a user-facing changed file. Exclude it from the `changed_files` manifest, the `full.diff` tracked section (via git pathspec `:!`), and represent test results only through the canonical persisted `test-results.json` inspection artifact.

**Driver:** Without exclusion, the review set double-counts infrastructure output: the test-results file appears both as a tracked change in `full.diff` and as the dedicated `test-results.json` canonical artifact. This muddies later promote behavior — if the promote hash regeneration includes the test-results file in the diff, any re-run of tests between review and promotion would produce a false hash mismatch.

**Alternatives considered:**
- **Include it in changed_files and full.diff** — original plan approach. Rejected because it produces double-counting and pollutes the "what did the agent change" review surface with instrumentation.
- **Exclude only from changed_files but keep in full.diff** — partial fix. Rejected because the design lock says both must be excluded and the hash-mismatch risk applies to the diff content.

**Trade-offs accepted:** If the agent introduces bugs in the test-results persistence logic, those bugs won't appear in the review diff. Acceptable because the test-results record is separately visible as the canonical artifact.

**Confidence:** High (E2) — the double-counting and promote-time hash mismatch are structural.

**Reversibility:** High — removing the pathspec exclusion and filter is a one-line change each.

**Change trigger:** If the canonical review set definition changes to include "all worktree state" rather than "deliverable changes + instrumentation artifacts separately."

## Changes

No code changes this session. The sole artifact is the implementation plan.

### `docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md` — Implementation plan (not committed)

**Purpose:** Complete, scrutinized implementation plan for `codex.delegate.poll` — the four-task TDD plan covering model/store contract, artifact materialization, controller flow, and MCP surface.

**Key changes across three revision rounds:**
1. `_persist_job_transition` → `update_status_and_promotion` atomic store op (design lock 10)
2. `snapshot.json` as poll-cache authority with store rehydration (design lock 6)
3. `.codex-collaboration/test-results.json` exclusion from diff and manifest (design lock 7)
4. NUL byte fix (`b"\0"` not `b"\\0"`) in hash recipe
5. Known-value hash test added (independently computes expected hash)
6. `build_execution_resume_turn_text` repaired with `json.dumps(...)` and complete return
7. `_FakeArtifactStore` added to controller tests for git isolation
8. Pathspec exclusion (`:!`) added to `_full_diff` tracked diff command

## Codebase Knowledge

### Files Read This Session

| File | Lines | Why read | Key finding |
|------|-------|----------|-------------|
| `delegation_controller.py` | 1240 | Verify `__init__` signature, `promotion_state` usage, `update_status` call sites | No `artifact_store` param. `promotion_state="pending"` at creation (line 473). 12 `update_status` call sites spanning start, decide, recover_startup. |
| `delegation_job_store.py` | 150 | Verify replay ops, promotion-state validation | Only `create` and `update_status` in `_replay()`. `_VALID_PROMOTION_STATES` is `frozenset(get_args(PromotionState))` — no None handling. |
| `models.py` | 401 | Verify `DelegationJob` shape, `PromotionState` type | `PromotionState = Literal["pending", "prechecks_passed", "applied", "verified", "prechecks_failed", "rollback_needed", "rolled_back"]`. `promotion_state: PromotionState` (non-nullable). |
| `execution_prompt_builder.py` | 73 | Verify current prompt content | No test-results persistence instructions. Clean `json.dumps` pattern for `requested_scope` at lines 44-48. |
| `mcp_server.py` | (grep only) | Verify dispatch pattern, `asdict` usage | All serialization via `dataclasses.asdict()`. Dispatch uses `if name == "codex.delegate.start":` pattern. |
| `consultation_safety.py` | (grep only) | Verify policy map completeness | 4 entries: consult, dialogue.start, dialogue.reply, delegate.decide. No delegate.start or delegate.poll. |
| `codex_runtime_bootstrap.py` | (grep only) | Verify DelegationController construction | Lines 118-128: constructs without `artifact_store`. |
| `pending_request_store.py` | (grep only) | Verify `list_by_collaboration_id` existence | Method exists at line 48. Returns list of `PendingServerRequest`. |

### Architecture: DelegationController Dependency Injection

```
codex_runtime_bootstrap.py:113 (factory)
  → DelegationController(
      control_plane=control_plane,        # App Server connection
      worktree_manager=WorktreeManager(), # Git worktree lifecycle
      job_store=DelegationJobStore(...),   # JSONL append-only job state
      lineage_store=LineageStore(...),     # Collaboration handle tracking
      runtime_registry=...,               # In-process runtime lookup
      journal=journal,                    # Operation journal (crash recovery)
      session_id=...,
      plugin_data_path=...,
      pending_request_store=PendingRequestStore(...),
      # NEW (after poll):
      artifact_store=ArtifactStore(...),  # Inspection artifact materialization
    )
```

### Store Operation Replay Pattern

The JSONL store pattern used by `DelegationJobStore` (and shared with `PendingRequestStore`):

1. Write: `_append()` serializes a dict with `"op"` key and flushes + fsyncs
2. Replay: `_replay()` reads all lines, applies ops in order, returns final state dict
3. Ops are: `create` (full object), `update_status` (status field only)
4. After poll: adds `update_status_and_promotion` (status + promotion_state compound) and `update_artifacts` (artifact_paths + artifact_hash)
5. All ops are append-only, last-write-wins for conflicting fields

### Safety Policy Pattern

`consultation_safety.py` provides a total lookup function `policy_for_tool(tool_name)` that returns `ToolScanPolicy` or raises `KeyError`. The codex guard hook (`codex_guard.py`) catches `KeyError` and returns exit 2 (block). This means:
- Known tools: scanned against their policy's `content_fields`
- Unknown tools: blocked (fail-closed)
- Missing entry for a known tool = blocked until added

The plan adds `DELEGATE_POLL_POLICY` with `expected_fields=frozenset({"job_id"})` and empty `content_fields` (job_id is an identifier, not free-form content).

### Promotion State Lifecycle (After Implementation)

```
Job creation  → promotion_state=None  (status="queued")
Running       → promotion_state=None  (status="running")
Escalation    → promotion_state=None  (status="needs_escalation")
Completion    → promotion_state="pending" (atomic with status="completed")
First poll    → artifacts materialized, hash computed
Promotion     → promotion_state="prechecks_passed" → "applied" → "verified"
```

### Key Implementation Seams for Poll

| Seam | Current state | After poll |
|------|---------------|------------|
| `DelegationJob.promotion_state` | `PromotionState` (non-nullable) | `PromotionState \| None` |
| `DelegationJobStore` ops | `create`, `update_status` | `create`, `update_status_and_promotion`, `update_artifacts` |
| `_replay()` branches | 2 (`create`, `update_status`) | 3 (+`update_status_and_promotion`, `update_artifacts`) |
| `DelegationController.__init__` | 11 params | 12 (+`artifact_store`) |
| `execution_prompt_builder` | No test-results instructions | Instructs agent to persist `.codex-collaboration/test-results.json` |
| `consultation_safety.py` map | 4 entries | 5 (+`delegate.poll`) |

## Context

### Mental Model

This session was **plan review as defect prevention**. The plan is not code — it's a specification for an implementation agent. Defects in the plan propagate through the agent into code. The scrutiny process applied the same rigor to the plan that would be applied to a spec: conformance checking against the authority documents, crash-safety analysis of the store operations, and verification that code snippets are compilable.

The key insight from this session: **illustrative code in a plan is still code** — a NUL byte typo or an undefined variable in a plan snippet becomes a NUL byte typo or undefined variable in production if the implementation agent copies it. The plan must be executable, not just directionally correct.

### Why This Session Matters

The poll implementation plan is the first document that connects the merged spec amendments (typed shapes, hash recipe, materialization semantics) to concrete file locations, test assertions, and commit boundaries. Without scrutiny:
- The `b"\\0"` NUL byte typo would produce spec-noncompliant hashes
- The two-write `_persist_job_transition` would create a permanent wedge state for crash-interrupted completions
- The incomplete prompt-builder snippet would cause implementation-time failures that look like Claude errors rather than plan errors
- The `.codex-collaboration/` double-counting would produce false hash mismatches at promote time

### Project State

- **T-05:** COMPLETE. Both slices merged to main at `271f23aa`. 698 tests.
- **T-06 decide:** COMPLETE AND MERGED at `e041c896`. 734 tests.
- **T-06 spec amendments:** COMPLETE AND MERGED at `db7fd1da` (PR #110). Docs-only.
- **T-06 poll plan:** APPROVED. Ready for implementation at `docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md`.
- **Branch:** `main` at `db7fd1da`. No feature branch yet — plan instructs creating `feature/t06-delegate-poll` in a worktree.
- **Worktree:** None. Working in primary checkout.
- **Untracked:** Plan file + two prior plan files (decide, t05).

## Learnings

### NUL byte escape in Python bytes literals is a common plan-level typo

**Mechanism:** In markdown source, `b"\\0"` renders as `b"\0"` (visually indistinguishable from the correct single-byte version). But in Python, `b"\\0"` is two bytes (0x5C 0x30) while `b"\0"` is one byte (0x00). Plans that specify hash recipes with NUL separators are vulnerable to this rendering ambiguity.

**Evidence:** Plan line 831 (pre-fix) had `sha.update(b"\\0")` which would produce a spec-divergent hash. The spec at `promotion-protocol.md` prescribes "relative_path + NUL + file_bytes" meaning the 0x00 byte.

**Implication:** Any plan specifying byte-level operations should include a known-value test that independently verifies the output matches expected. The hash test at plan lines 623-633 catches this class of error. For future plans: always add an assertion that pins the exact output value, not just `is not None`.

### Crash-window analysis must trace the full recovery path, not just the immediate caller

**Mechanism:** The initial scrutiny said `_persist_job_transition`'s crash window was "medium" because "poll would self-heal." But tracing the actual recovery path showed that `_load_or_materialize_inspection` only calls `update_artifacts`, never `update_promotion_state`. The "self-healing" claim was wrong — it would heal artifacts but leave `promotion_state=None`, creating a permanent wedge.

**Evidence:** User's correction: "`_load_or_materialize_inspection()` only writes artifacts... so a crash after `update_status(..., 'completed')` and before `update_promotion_state(..., 'pending')` leaves `completed + None` until some later code fixes it."

**Implication:** When analyzing crash windows in append-only store architectures, trace every possible reader of the inconsistent state — not just the "obvious" recovery path. A field that looks like it would be fixed by a later write may not be in any later write's responsibility.

### Fail-open vs fail-closed must be verified against the actual hook, not the gotcha documentation

**Mechanism:** The CLAUDE.md gotcha says "PreToolUse hooks are fail-open — unhandled exceptions don't produce exit code 2." This is true for unhandled exceptions in generic hooks. But the specific `codex_guard.py` hook catches the `KeyError` from `policy_for_tool()` and explicitly returns exit 2. The gotcha describes the framework default; the specific hook overrides it.

**Evidence:** User corrected: "`codex_guard.py:49` catches `policy_for_tool()` failures and returns exit 2, and `test_codex_guard.py:148` already asserts unknown plugin tools block."

**Implication:** When reasoning about hook behavior, check the specific hook implementation, not just the framework documentation. A hook's actual behavior may be stricter than the framework default.

## Next Steps

### 1. Implement poll using `superpowers:subagent-driven-development`

**Dependencies:** None — plan is approved, spec is merged, baseline is on main.

**What to do:**
1. Create worktree: `git worktree add ../claude-code-tool-dev-poll -b feature/t06-delegate-poll main`
2. Run pre-flight verification (Step P2): baseline tests green
3. Execute Tasks 1-4 following the plan's TDD sequence
4. Each task: write failing tests → implement → verify → commit

**Plan location:** `docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md`

**Expected outcome:** 4 commits on `feature/t06-delegate-poll`, full test suite green, PR opened.

**Critical implementation notes for the implementing agent:**
- The plan has code snippets that are illustrative — always run the tests and let failures guide implementation, don't just copy-paste
- `_FakeArtifactStore` in controller tests isolates from git; real `ArtifactStore` tests in `test_artifact_store.py` use `_init_repo` to create real git repos
- The `update_status_and_promotion` op replaces ALL existing `update_status` calls in lifecycle-transition paths (not just completion — also `recover_startup` marking `unknown`)
- Existing test sites with `promotion_state="pending"` for non-completed jobs need updating to `promotion_state=None` — there are 18 across 5 test files

### 2. After poll merges: `codex.delegate.promote`

**Dependencies:** Poll implemented and merged.

**Scope:** HEAD/base-commit match, clean worktree/index, `job_not_reviewed` check, artifact hash regeneration from worktree state (not re-hashing stored snapshot), completed-job precondition, typed rejection responses, rollback, advisory-stale signaling.

### 3. Sidecar hardening (can parallel with promote)

**Items:**
- MCP-layer test for malformed-answers rejection path
- Approve-path finalization guard regression test
- `codex.delegate.start` PreToolUse scan policy (the pre-existing gap)
- Start/decide `PendingServerRequest` projection to `PendingEscalationView`

## In Progress

**Clean stopping point.** Plan approved, no implementation started. All spec amendments merged. No code changes in flight.

- **Completed:** PR #110 merged, plan scrutinized through two full passes, three revision rounds applied, final verdict "Defensible."
- **Not in flight:** No worktree created, no feature branch, no code changes.
- **Next action for next-session Claude:** Execute the plan using `superpowers:subagent-driven-development`. The plan at `docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md` is the implementation authority.

## Open Questions

### 1. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** Handler calls `entry.session.interrupt_turn()` from inside `_server_request_handler`. Sends `turn/interrupt` via same transport reading notifications.

**Decision pending until:** Live testing against real App Server.

### 2. `on-request` operational semantics (inherited from T-05)

**Context:** Vendored schema proves `on-request` is a valid `approvalPolicy` value but operational semantics undocumented. Controller defaults to `untrusted`.

**Decision pending until:** Live probe against real App Server.

### 3. Approve turn prompt shape adequacy (inherited from decide)

**Context:** `build_execution_resume_turn_text()` tells agent request was resolved. Whether this prompt reliably produces follow-up behavior is unverified.

**Decision pending until:** Live execution testing.

### 4. Test-results persistence in execution runtime (PARTIALLY RESOLVED)

**Context:** The plan resolves this by instructing the execution agent to persist at `.codex-collaboration/test-results.json` with a deterministic stub fallback for older jobs. The open question shifts to: will the execution agent reliably follow the prompt instruction to persist test results? If not, all jobs degrade to `"not_recorded"` stubs.

**Decision pending until:** Live execution testing with the amended prompt.

## Risks

### 1. `_decided_request_ids` is in-memory only (inherited)

If cross-session decide is added, the in-memory set won't persist across restarts. For same-session-only design, this is correct.

### 2. `_FakeSession` complexity continues to grow (inherited)

The fake session has multiple methods and configurable state. Drift from real `AppServerRuntimeSession` interface could mask production failures.

### 3. 18 test sites need `promotion_state` updates

The plan instructs changing `promotion_state="pending"` to `promotion_state=None` for non-completed jobs across 18 occurrences in 5 test files. If any are missed, tests will fail — which is self-correcting (the failing test catches the miss). But it's a wide blast radius that could produce noisy intermediate states during implementation.

### 4. Execution agent may not follow test-results persistence instruction

The amended `build_execution_turn_text` instructs the agent to write `.codex-collaboration/test-results.json`. If the execution agent ignores or misinterprets this, all inspection snapshots get `"not_recorded"` stubs. The deterministic fallback ensures poll still works, but the promotion hash would include a stub instead of real results — meaning any future re-poll after the agent does persist results would produce a hash mismatch.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| Poll implementation plan | `docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md` | Implementation authority |
| Contracts (merged) | `docs/superpowers/specs/codex-collaboration/contracts.md` | Schema authority |
| Promotion protocol (merged) | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | Hash recipe, materialization, verification |
| Foundations (merged) | `docs/superpowers/specs/codex-collaboration/foundations.md` | High-level flow |
| Recovery spec | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Recovery semantics |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-19_23-55_t06-poll-spec-amendments-published.md`
- T-05/T-06 arc: execution-start → pending-request capture → T-05 closed → T-06 decide plan → T-06 decide implemented → T-06 decide merged → T-06 poll spec amendments → **T-06 poll plan scrutinized (this handoff)**

### PR chain

| PR | Title | Status |
|----|-------|--------|
| #109 | T-06 decide opening slice | Merged (`e041c896`) |
| #110 | Spec amendments for codex.delegate.poll | Merged (`db7fd1da`) |

## Gotchas

### 1. `b"\\0"` vs `b"\0"` in markdown-rendered Python code

**Symptom:** Hash computation produces wrong values that don't match the spec.

**Root cause:** In markdown source, `\\0` and `\0` can render identically. In Python bytes literals, `b"\\0"` is two bytes (backslash + zero), `b"\0"` is one byte (NUL). The spec requires NUL (0x00).

**Prevention:** The plan now includes a known-value hash test (lines 623-633) that independently computes the expected hash and compares. Any escape-level error is caught immediately.

### 2. `_full_diff` needs explicit pathspec exclusion, not just `_changed_files` filtering

**Symptom:** `.codex-collaboration/test-results.json` appears in the diff even though it's excluded from `changed_files`.

**Root cause:** `_changed_files` filtering only applies to the untracked-file append loop. The tracked `git diff` section uses a blanket `--` pathspec that includes all tracked changes.

**Prevention:** Design lock 7 + pathspec `:!{TEST_RESULTS_RECORD_RELATIVE_PATH}` added to the tracked diff command at plan line 866. Test assertion at plan line 590 verifies the file doesn't appear in `full.diff` output.

### 3. Pre-existing `codex.delegate.start` missing from `consultation_safety.py` policy map

**Symptom:** The hook blocks `codex.delegate.start` calls (fail-closed via exit 2).

**Root cause:** `_TOOL_POLICY_MAP` has no entry for `codex.delegate.start`. `policy_for_tool()` raises `KeyError`, caught by `codex_guard.py:49` which returns exit 2.

**Prevention:** This is a pre-existing gap tracked as a sidecar hardening item (Next Steps #3). The plan only adds poll's policy entry and explicitly does not fix start's gap in this slice.

### 4. `promotion_state="pending"` at creation is the wrong semantic value

**Symptom:** Any code that trusts `promotion_state == "pending"` to mean "promote-ready" would incorrectly treat running/queued jobs as promotion candidates.

**Root cause:** `delegation_controller.py:473` sets `promotion_state="pending"` at creation because `DelegationJob` required a non-nullable `PromotionState` value. After the nullable migration, creation uses `None` and only completion sets `"pending"`.

**Prevention:** The plan's atomic `update_status_and_promotion` op couples the status transition with the correct promotion state. Poll reads `promotion_state` to determine materialization eligibility.

## Conversation Highlights

### User's F1 severity escalation

User: "The `_persist_job_transition()` gap is real, and one part is actually worse than your writeup: the current plan would not self-heal `promotion_state`. `_load_or_materialize_inspection()` only writes artifacts... so a crash after `update_status(..., 'completed')` and before `update_promotion_state(..., 'pending')` leaves `completed + None` until some later code fixes it."

— Caught an incorrect "self-healing" claim and escalated to demand a real fix (atomic op), not just a comment.

### User's fail-closed correction

User: "The `codex.delegate.start` policy-map gap is real, but the current hook is fail-closed, not fail-open. `codex_guard.py:49` catches `policy_for_tool()` failures and returns exit `2`, and `test_codex_guard.py:148` already asserts unknown plugin tools block."

— Corrected an incorrect framing about hook behavior. The framework default (fail-open on unhandled exceptions) does not apply when the hook explicitly catches and blocks.

### User's scope-appropriate deferral of mixed diff format

User: "I accept your `git diff --no-index` caveat, but I would not treat mixed diff format as a blocker for this packet. In the poll slice, `full.diff` is a review artifact, not yet an apply surface."

— Correctly deferred a cosmetic concern that only becomes load-bearing if promote tries to `git apply` the review diff directly.

## User Preferences

### Plan authorship: user writes, Claude scrutinizes

User authored the complete plan externally and presented it for scrutiny. Claude's role was adversarial review, finding defects, and verifying revisions. This matches the pattern established in the spec amendment session (user designs, Claude scrutinizes and implements).

### Severity tiering in review feedback

User organized feedback into "Required Revisions" (mandatory, blocking) and "Revisions I'd Make, But Lower Severity" (recommended, non-blocking). Pattern: structured review with explicit priority ordering.

### Pushback as calibration, not rejection

User's pushback items ("Pushback / Calibration") didn't reject findings outright — they refined severity and framing while accepting the underlying observation. Pattern: "the finding is real but your framing/severity is wrong" is a correction, not a dismissal.

### Implementation via subagent-driven-development

User explicitly specified: "next session proceed to implementation with subagent-driven-development." This means the next session should use the `superpowers:subagent-driven-development` skill to execute the plan task-by-task, not implement sequentially in a single thread.
