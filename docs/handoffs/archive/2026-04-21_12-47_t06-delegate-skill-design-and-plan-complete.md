---
date: 2026-04-21
time: "12:47"
created_at: "2026-04-21T16:47:08Z"
session_id: 7afc1ae4-b2b6-4f2b-9d95-b712b9791ee8
resumed_from: "docs/handoffs/archive/2026-04-21_10-37_t06-pending-escalation-view-projection-merged.md"
project: claude-code-tool-dev
branch: chore/delegate-skill-design
commit: ff193f00
title: "T-06 delegate skill UX — design spec and implementation plan complete, ready for execution"
type: handoff
files:
  - docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md
  - docs/superpowers/plans/2026-04-21-delegate-skill-ux-implementation.md
  - packages/plugins/codex-collaboration/server/delegation_job_store.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/control_plane.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegation_job_store.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/specs/codex-collaboration/promotion-protocol.md
  - docs/superpowers/specs/codex-collaboration/recovery-and-journal.md
---

# T-06 Delegate Skill UX — Design Spec and Implementation Plan Complete

## Goal

Design and plan the delegate skill UX — the Claude-facing skill that orchestrates the full delegation lifecycle: start → poll → decide → promote/discard. This is the remaining T-06 acceptance criterion from `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md:66`.

**Trigger:** The prior session completed the PendingEscalationView projection (the contract-hardening prerequisite), leaving the delegate skill as the last T-06 AC. User instructed to "continue with discussing the design."

**Stakes:** Without this skill, the 5 delegate MCP tools (`start`, `poll`, `decide`, `promote`, `discard`) have no Claude-facing UX. The user would have to invoke MCP tools directly. The skill is the product surface that makes delegation usable.

**Success criteria (all met this session):**
1. Design spec written, reviewed, and approved at defensible quality — done.
2. Implementation plan written, reviewed, and approved at minor-revision quality — done.
3. Ready for execution via subagent-driven-development — done.

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. This session produced the design and plan. Next session: execute the plan.

## Session Narrative

**Phase 0 — Handoff load (~2 min).** Loaded the prior session's handoff (`2026-04-21_10-37`). Clean state: `main` at `57c6466a`, 818 tests, no in-flight work.

**Phase 1 — Context exploration (~10 min).** Read the T-06 ticket, contracts.md (full MCP tool surface and response shapes), existing skill patterns (consult-codex, dialogue, cross-model delegate), and the promotion protocol. Key finding: the existing cross-model `/delegate` skill wraps `codex exec` (single-shot subprocess), while the new codex-collaboration delegate needs to orchestrate 5 stateful MCP tools with an interactive lifecycle. The cross-model skill is a UX reference but architecturally different.

**Phase 2 — Invocation scope design (~15 min).** Proposed 3 invocation scopes:
- (A) Single-invocation orchestrator — runs entire lifecycle in one skill invocation
- (B) Phase-oriented commands — separate commands per tool
- (C) Single entry with resume — `/delegate` starts or resumes

User chose none of these, instead proposing **(D) Resume-first with explicit verb escape hatches**: C as primary UX (bare `/delegate` resumes), B available for precision (`/delegate poll`, `/delegate promote`), A only as an inner loop for immediate escalation chains. User provided detailed analysis of each option with grounding constraints from the codebase.

**Phase 3 — Pointer vs stateless debate (~10 min).** The design initially assumed a skill-owned active-job pointer file (like the dialogue skill's active-run lock). Pushed back: `codex.status` already has an `active_delegation` field (currently hardcoded to None in `control_plane.py:135`). If populated, the skill becomes stateless — no pointer file, no cleanup lifecycle. User agreed this is the right design but noted it requires a server change (Slice 0). User identified that `list_active()` on `DelegationJobStore:63` is too narrow (runtime-active only), and a new `list_user_attention_required()` is needed.

**Phase 4 — Verb parsing (~5 min).** User proposed strict subcommand grammar with `start`/`--` as objective escape hatches. Reserved words (`poll`, `approve`, `deny`, `promote`, `discard`) are checked before objective parsing. Ambiguous input rejected loudly. User: "If the user says `/delegate promote 12345`, I do not want the skill guessing whether `12345` is a job id, issue number, or objective fragment."

**Phase 5 — Review rendering and ceremony (~5 min).** Agreed on (b) Summary + selective read for completed-job review: read canonical artifacts (`full.diff`, `test-results.json`, `changed-files.json`), summarize large diffs, Claude assessment. User added key ceremony rule: "the skill must not promote in the same invocation that first materializes the review artifact." Keys off pre-poll `active_delegation.artifact_hash`.

**Phase 6 — Design spec writing and first review (~15 min).** Wrote full design spec on `chore/delegate-skill-design` branch. User conducted adversarial review. **Critical finding: failed/unknown jobs create permanent resume poison.** The spec included them in `active_delegation` but provided no discard path, and a user could start a new job alongside a failed one (since the busy gate only checked runtime-active). This broke the singular `active_delegation` assumption.

**Phase 7 — Singleton invariant design (~10 min).** Resolution: widen the busy gate from `list_active()` to `list_user_attention_required()`, widen `discard` to accept failed/unknown with `promotion_state is None`, establish hard singleton invariant. User approved. Also resolved: MCP-side enrichment (picked explicitly), `request_user_input` explicit answer flow via `/delegate approve`, promote locked to `active_delegation` only, large-diff review calibration.

**Phase 8 — Second adversarial review (~10 min).** User found 3 more issues:
1. Discard widening too broad (included post-mutation states like `applied`, `rollback_needed`)
2. Explicit job-id promote bypassed ceremony
3. Lazy controller recovery blind spot in status enrichment

Resolved: narrowed discard to `promotion_state is None` only for failed/unknown, locked promote to `active_delegation` route only, status enrichment uses recovery-capable `_ensure_delegation_controller()`. User approved at "Defensible" verdict.

**Phase 9 — Implementation plan (~15 min).** Wrote 7-task plan: Tasks 1-5 (Slice 0: server enrichment), Task 6 (Slice 1: SKILL.md), Task 7 (verification). User conducted adversarial review. **Critical finding: Task 4 had broken code (missing return after `if job is None:`) and no diagnostics.** Also found: `completed + promotion_state=None` trap (unterminalizable state that poisons busy gate), test helper defaults wrong (`_make_job` defaults `promotion_state="pending"` not `None`).

**Phase 10 — Plan revisions (~10 min).** Fixed broken code, added `completed+None` exclusion to `list_user_attention_required()`, fixed test helpers, added factory-failure test, added bounded skill verification to Task 7.

**Phase 11 — Third review and final fixes (~5 min).** User found 3 more issues:
1. Delegation diagnostics in global `errors` would block consult/dialogue preflights
2. Multiple pre-migration attention jobs collapsed silently to index 0
3. Missing Job Busy contract update

Resolved: `delegation_status_error` field instead of `errors`, `get_active_delegation_summary()` returns `(job, count)` with last-by-replay-order, Job Busy added to Task 5.

## Decisions

### Decision 1: Stateless skill with server-owned truth (D1)

**Choice:** The delegate skill holds no state files. `codex.status.active_delegation` is the resume source.

**Driver:** User: "Your pointer objection is directionally right. D should be stateless at the skill layer, with `codex.status.active_delegation` as the resume source." The `active_delegation` field already exists on the contract (hardcoded to None). Populating it is a small server change vs. a skill-owned pointer with its own cleanup/staleness lifecycle.

**Alternatives considered:**
- **Skill-owned pointer file** (like dialogue's active-run lock) — rejected because the server already owns job lifecycle. The dialogue skill owns state because it manages containment seeds and subagent orchestration; the delegate skill does not. User: "The skill-owned pointer should be the fallback only if we refuse to touch server code."
- **Server-side `codex.delegate.active` discovery tool** — rejected as unnecessary when `codex.status` already has the field.

**Trade-offs accepted:** Requires server-side Slice 0 work before the skill can function. Acceptable because Slice 0 also establishes the singleton invariant (safety-critical).

**Confidence:** High (E2) — both stateless resume and pointer approaches analyzed against the codebase. Stateless avoids the staleness/cleanup problems that dialogue's pointer already demonstrates.

**Reversibility:** High — could add a pointer file later if `codex.status` proves insufficient.

**Change trigger:** If status enrichment recovery proves unreliable across server restarts, a local pointer as fallback would be reconsidered.

### Decision 2: Resume-first with explicit verb escape hatches (D2, Option D)

**Choice:** `/delegate` (no args) resumes. Verbs (`poll`, `approve`, `deny`, `promote`, `discard`) are escape hatches. `start`/`--` disambiguate objectives from reserved words.

**Driver:** User provided detailed analysis of options A through D. User: "I would not choose pure A, B, or C." Key insight: delegation is not a single bounded operation — it can span minutes to hours with escalations, polling, and promotion. The skill should be a state router, not a long-running script.

**Alternatives considered:**
- **(A) Single-invocation orchestrator** — rejected as invocation contract because delegation can span multiple turns. User: "The biggest risk is promotion. If A means 'run through review → promote-or-discard automatically,' that blurs the highest-risk boundary."
- **(B) Phase-oriented commands** — rejected as primary UX because it "leaks too much machinery into the user experience." But retained as escape hatches.
- **(C) Single entry with resume** — closest but needed explicit verbs for precision.

**Trade-offs accepted:** More complex grammar (parse order, disambiguation rules) than a simple wrapper. Acceptable because the complexity is in the skill definition, not the user experience.

**Confidence:** High (E2) — all four options analyzed against the MCP tool surface and promotion protocol.

**Reversibility:** Medium — the grammar is in SKILL.md and could be changed, but downstream muscle memory is hard to retrain.

**Change trigger:** If live usage shows users never use the verb escape hatches, simplify to pure C.

### Decision 3: Singleton user-attention invariant via widened busy gate (D4/D5)

**Choice:** Widen `codex.delegate.start`'s busy gate from `list_active()` (runtime-active only) to `list_user_attention_required()` (any non-terminal job). Widen `discard` to accept failed/unknown with `promotion_state is None`.

**Driver:** First adversarial review discovered that failed/unknown jobs would permanently poison the resume UX — they'd show in `active_delegation` but couldn't be discarded, and the user could start a new job alongside them (since the old busy gate only blocked runtime-active). User: "the failed/unknown lifecycle hole is not a polish issue."

**Alternatives considered:**
- **Return a list `active_delegations`** — rejected because it complicates the singular resume UX and the skill is stateless.
- **Exclude failed/unknown from resume** — rejected because it loses UX value; the user needs to know about and clear failed jobs.
- **Auto-retire on new start** — rejected because it silently discards state the user might want to inspect.

**Trade-offs accepted:** Users must explicitly discard/promote before starting new work. This is also a safety feature: it prevents abandoning reviewed artifacts. Discard is narrowed to `promotion_state is None` for failed/unknown — post-mutation states require recovery handling.

**Confidence:** High (E2) — the resume-poison scenario was demonstrated by the adversarial review. The singleton invariant eliminates it.

**Reversibility:** Medium — widening the busy gate is behavioral. Narrowing it back would reintroduce the resume-poison problem.

**Change trigger:** If multi-job concurrency enters scope (v2), the invariant would need to be relaxed and `active_delegation` would become a list.

### Decision 4: Promotion locked to active_delegation (D3)

**Choice:** `/delegate promote` only promotes via `active_delegation`. Explicit `/delegate promote <job_id>` where `job_id` doesn't match `active_delegation` is read-only inspection — renders review but does not call `promote`.

**Driver:** Second adversarial review found that explicit job-id promote weakened the review-before-promote ceremony. The skill is stateless and can't confirm a non-active job was reviewed in a prior flow. User: "Fix: for explicit non-active job IDs, render review and require a second explicit promote."

**Alternatives considered:**
- **Allow explicit job_id promote with artifact_hash check** — rejected because `artifact_hash` present proves prior materialization, not that THIS user saw the review.
- **Add `/delegate promote-reviewed <job_id>` bypass** — rejected as unnecessary complexity given the singleton invariant (the promotable job IS always the active delegation).

**Trade-offs accepted:** Users can't promote arbitrary job IDs. Non-issue in v1 with singleton invariant — the active delegation is the only promotable job.

**Confidence:** High (E2) — the singleton invariant makes this restriction cost-free.

**Reversibility:** High — could relax to allow explicit job_id promote if needed.

**Change trigger:** If multi-job concurrency enters scope and users need to promote specific jobs by ID.

### Decision 5: Delegation diagnostics in `delegation_status_error`, not global `errors`

**Choice:** When delegation status enrichment fails (factory recovery error, query error), set a dedicated `delegation_status_error` field on the status response. Do not append to global `errors`.

**Driver:** Third plan review found that existing skills (`consult-codex` at `SKILL.md:31`) treat non-empty `errors` as blocking. Appending delegation diagnostics would block advisory consults even when the advisory runtime is healthy.

**Alternatives considered:**
- **Append to global `errors`** — rejected because it creates cross-surface coupling. A delegation recovery hiccup should not block consults.
- **Use a `warnings` field** — viable but no existing `warnings` field. `delegation_status_error` is more specific.

**Trade-offs accepted:** Adds a new field to the status response. The delegate skill must check `delegation_status_error` separately from `errors`.

**Confidence:** High (E2) — the consult skill's blocking behavior on `errors` is documented and verified.

**Reversibility:** High — field is additive; removing it later only requires the delegate skill to stop checking it.

**Change trigger:** If a general-purpose `warnings` field is added to status, delegation diagnostics could move there.

### Decision 6: `completed + promotion_state=None` excluded from attention set

**Choice:** `list_user_attention_required()` excludes jobs with `status=completed` and `promotion_state is None`. This is an impossible state (the atomic `update_status_and_promotion` always sets both) that, if encountered via corruption/legacy, cannot be promoted or discarded.

**Driver:** Plan review found that the initial `list_user_attention_required()` implementation included this state, which would create an unterminalizable attention-active job, poisoning the busy gate.

**Alternatives considered:**
- **Include and let state router handle** — rejected because the state router can render it but can't terminalize it (promote and discard both reject it).
- **Normalize to `completed + pending`** — rejected because normalizing in a read-only query feels wrong; the store should reflect truth.

**Trade-offs accepted:** If a `completed + None` job exists, it's invisible to the resume UX. Accessible only via explicit `/delegate poll <job_id>`. Acceptable because the state should never occur.

**Confidence:** High (E2) — `update_status_and_promotion` atomicity is verified by existing tests.

**Reversibility:** High — single-line exclusion in the predicate.

**Change trigger:** If a code path is discovered that can create `completed + None`, it must be fixed at the source rather than accommodated in the predicate.

## Changes

### Design spec (1 file created)

| File | What changed |
|------|-------------|
| `docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md` | Full design spec: architecture (stateless state router), invocation grammar (parse order, disambiguation, verb escapes), state router (4-tier precedence), review rendering (canonical artifacts, ~200-line diff heuristic), escalation rendering (per-kind, `request_user_input` flow), ceremony gates (review-before-promote, approve requires escalation, never auto-promote), failure handling, skill frontmatter, 2 implementation slices, 6 design decisions. Revised 3 times based on adversarial reviews. |

### Implementation plan (1 file created)

| File | What changed |
|------|-------------|
| `docs/superpowers/plans/2026-04-21-delegate-skill-ux-implementation.md` | 7-task plan: Task 1 (`list_user_attention_required` store method + 11 tests), Task 2 (widened discard + 4 tests), Task 3 (widened busy gate + 3 tests), Task 4 (MCP-side status enrichment + 5 tests), Task 5 (normative contract updates), Task 6 (SKILL.md), Task 7 (final verification). Revised 3 times based on adversarial reviews. |

### Housekeeping (1 commit)

| Commit | What |
|--------|------|
| `012fce44` (from prior session) | chore: add completed plan docs for T-05 capture, T-06 decide, and T-06 poll |

## Codebase Knowledge

### Architecture: Delegation Control Flow

```
Skill (/delegate) → [stateless]
  ├── codex.status(repo_root) → ControlPlane.codex_status() + MCP-side delegation enrichment
  │     └── _ensure_delegation_controller() → DelegationController.get_active_delegation_summary()
  │           └── DelegationJobStore.list_user_attention_required()
  │
  ├── codex.delegate.start(repo_root, objective) → DelegationController.start()
  │     └── busy check: list_user_attention_required() (widened from list_active())
  │
  ├── codex.delegate.poll(job_id) → DelegationController.poll()
  │     └── materializes inspection artifacts on first completed-job poll
  │
  ├── codex.delegate.decide(job_id, request_id, decision, answers?) → DelegationController.decide()
  │     └── resolves pending_escalation via PendingEscalationView
  │
  ├── codex.delegate.promote(job_id) → DelegationController.promote()
  │     └── preconditions: HEAD match, clean workspace, artifact hash, job completed+reviewed
  │
  └── codex.delegate.discard(job_id) → DelegationController.discard()
        └── allowed: promotion_state in (pending, prechecks_failed) OR
            status in (failed, unknown) and promotion_state is None
```

### Key Implementation Locations

| Concept | Location |
|---------|----------|
| `DelegationJobStore` | `server/delegation_job_store.py` |
| `list_active()` (runtime-active) | `delegation_job_store.py:63` |
| `_ACTIVE_STATUSES` constant | `delegation_job_store.py:22` |
| `DelegationController.start()` busy check | `delegation_controller.py:320-390` |
| `DelegationController.discard()` | `delegation_controller.py:1335-1378` |
| `_ensure_delegation_controller()` | `mcp_server.py:239-262` |
| `_dispatch_tool` for `codex.status` | `mcp_server.py:350-351` |
| `ControlPlane.codex_status()` | `control_plane.py:81-146` |
| `active_delegation: None` hardcode | `control_plane.py:135` |
| `DelegationJob` model | `server/models.py:340-362` |
| `JobStatus` type | `server/models.py:21-23` |
| `PromotionState` type | `server/models.py:24-33` |
| `JobBusyResponse` model | `server/models.py:366-375` |
| `DiscardRejectedResponse` model | `server/models.py:494-500` |
| Existing discard tests | `test_delegation_controller.py:2993-3021` |
| Existing busy gate tests | `test_delegation_controller.py:415-448` |
| `_make_job` helper (defaults `promotion_state="pending"`) | `test_delegation_job_store.py:13-27` |

### Dependency Graph (Slice 0 Changes)

```
DelegationJobStore (Task 1)
  ├── New: list_user_attention_required()
  ├── New: _TERMINAL_PROMOTION_STATES constant
  └── Existing: list_active() (unchanged, still used for runtime-active queries)

DelegationController (Tasks 2-3)
  ├── Modified: discard() — widened predicate
  ├── Modified: start() — busy check uses list_user_attention_required()
  └── New: get_active_delegation_summary() → (DelegationJob | None, int)

McpServer (Task 4)
  ├── Modified: _dispatch_tool codex.status branch — inline enrichment
  └── Uses: _ensure_delegation_controller() (recovery-capable, lazy init)

ControlPlane (no changes)
  └── codex_status() — still returns active_delegation: None; MCP overrides it

Normative docs (Task 5)
  ├── contracts.md — active_delegation, Job Busy
  ├── promotion-protocol.md — discard eligibility
  └── recovery-and-journal.md — concurrency text
```

### Existing Skill Patterns

| Skill | Pattern | Relevance |
|-------|---------|-----------|
| `consult-codex` | Thin wrapper: preflight → dispatch → relay. `allowed-tools` lists Bash + MCP tools. | Frontmatter format reference. |
| `dialogue` | Heavy orchestrator: gatherers → assembly → subagent. Owns containment seed lifecycle. | UX complexity reference (delegate is between consult and dialogue in weight). |
| `cross-model delegate` | Single-invocation `codex exec` wrapper. Parse flags → write JSON → run adapter → review. | UX precedent for "delegate" concept, but architecturally different (subprocess, not MCP). |

### Test Patterns

- `_build_controller(tmp_path)` returns `(controller, control_plane, worktree_manager, job_store, lineage_store, journal, registry, pending_request_store)` — the standard test fixture for controller tests.
- `_build_promote_scenario(tmp_path)` returns `(controller, job_store, journal, repo, job_id, hash, cb)` — creates a completed job with artifact hash, ready for promote/discard.
- Tests use stubs: `_FakeControlPlane`, `_FakeWorktreeManager`, etc.
- `_make_job()` in `test_delegation_job_store.py` defaults `promotion_state="pending"` — tests needing null must pass `promotion_state=None` explicitly.

## Context

### Mental Model

This is a **state-router UX** problem. The delegate skill is not a pipeline (like the cross-model delegate) or an orchestrator (like the dialogue skill). It's a thin rendering layer over server-owned state. Each invocation: read state → render → exit with guidance. The skill's complexity is in the grammar (disambiguating user intent) and the ceremony (preventing promotion without review), not in lifecycle management (which the server owns).

The key architectural insight: **the server already owns the full job lifecycle**. The skill's job is translating server state into user-facing UX, not duplicating lifecycle control.

### Project State

- **T-05:** COMPLETE. Both slices merged at `271f23aa`. 698 tests.
- **T-06 decide:** COMPLETE at `e041c896`. 734 tests.
- **T-06 spec amendments:** COMPLETE at `db7fd1da` (PR #110).
- **T-06 poll:** COMPLETE at `8bae4dde` (PR #111). 765 tests.
- **T-06 sidecar hardening:** COMPLETE at `f9a40366` (PR #112). 771 tests.
- **T-06 promote/discard:** COMPLETE at `27505cc0` (PR #113). 816 tests.
- **T-06 PendingEscalationView projection:** COMPLETE at `57c6466a`. 818 tests.
- **T-06 delegate skill UX:** DESIGN AND PLAN COMPLETE. Ready for execution.
- **Next:** Execute the plan via subagent-driven-development.

## Learnings

### Adversarial review as a design refinement tool

**Mechanism:** The user conducted 3 rounds of adversarial review on the design spec and 3 rounds on the implementation plan. Each round found genuine issues that would have caused implementation problems. The reviews converged from "Major revision" → "Minor revision" → "Defensible" (spec) and "Major revision" → "Minor revision" (plan).

**Evidence:** First spec review found the resume-poison lifecycle hole (failed/unknown jobs with no terminalization path). First plan review found the broken Task 4 code, the `completed+None` trap, and missing skill verification. Third plan review found cross-surface semantics (global `errors` blocking consults, pre-migration multi-job state).

**Implication:** Safety-bearing changes (promotion, busy gate, discard) benefit from explicit adversarial review. The reviews caught issues that testing alone would have surfaced much later (the `completed+None` trap, the `errors` cross-surface coupling).

### Singleton invariants simplify UX but require lifecycle completeness

**Mechanism:** The singular `active_delegation` field is simple to consume but requires every non-terminal state to have a terminalization path. Without it, attention-active states become permanent blockers.

**Evidence:** The original design had failed/unknown jobs in the attention set with no discard path. The widened busy gate then made them permanent blockers — a user couldn't start new work.

**Implication:** When introducing a singleton invariant, audit every possible state for terminalization paths before committing to the invariant. The audit should include impossible states (like `completed + promotion_state=None`) since they can appear via corruption.

### Status response fields have cross-surface coupling

**Mechanism:** The global `errors` field in `codex.status` is consumed by multiple skills with different interpretations. The consult skill treats non-empty `errors` as blocking. Adding delegation diagnostics to `errors` would block advisory operations.

**Evidence:** `consult-codex/SKILL.md:31` explicitly stops when `errors` is non-empty.

**Implication:** New diagnostic fields should use dedicated names (e.g., `delegation_status_error`) to avoid cross-surface coupling. Review all status consumers before modifying shared response fields.

## Next Steps

### 1. Execute the implementation plan with subagent-driven-development

**Dependencies:** None. Design spec and plan are approved.

**What to read first:** `docs/superpowers/plans/2026-04-21-delegate-skill-ux-implementation.md` — the complete 7-task plan with exact code, test snippets, and commands.

**Execution approach:** User requested subagent-driven-development. Dispatch a fresh subagent per task, review between tasks. Slice 0 (Tasks 1-5) is safety-bearing and must be fully green before Slice 1 (Task 6: SKILL.md).

**Where to start:** Task 1 (`list_user_attention_required` on DelegationJobStore). First step: write the 11 failing tests.

**Branch:** Continue on `chore/delegate-skill-design`. The design spec and plan are already committed here.

**Acceptance criteria:** All 7 tasks complete, full suite green (818 + new tests), ruff clean, SKILL.md structurally valid, bounded lifecycle verification passing.

## In Progress

**Clean stopping point.** Design spec and implementation plan complete, committed on `chore/delegate-skill-design` at `ff193f00`. No implementation work started. No code changes beyond the two spec/plan documents.

## Open Questions

### 1. `git diff --binary` output stability across invocations (inherited)

**Context:** Post-apply verification relies on byte-for-byte comparison of regenerated `full.diff`. The spec noted this may not be stable across git versions.

**Decision pending until:** Production testing reveals whether byte comparison is reliable.

### 2. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** Handler calls `entry.session.interrupt_turn()` from inside `_server_request_handler`. Sends `turn/interrupt` via same transport reading notifications.

**Decision pending until:** Live testing against real App Server.

### 3. `on-request` operational semantics (inherited from T-05)

**Context:** Vendored schema proves `on-request` is a valid `approvalPolicy` value but operational semantics undocumented. Controller defaults to `untrusted`.

**Decision pending until:** Live probe against real App Server.

### 4. Test-results persistence in execution runtime (inherited from poll)

**Context:** The execution prompt instructs the agent to persist at `.codex-collaboration/test-results.json`. If the agent ignores this, all jobs degrade to `not_recorded` stubs.

**Decision pending until:** Live execution testing with the amended prompt.

### 5. `request_user_input` answer construction in live skill

**Context:** The design specifies that `/delegate approve` for `request_user_input` escalations requires Claude to construct the `answers` parameter from conversation context. This is untestable without a live skill invocation.

**Decision pending until:** First live `request_user_input` escalation through the delegate skill.

## Risks

### 1. Byte-for-byte diff comparison may be fragile (inherited)

The post-apply verification compares `full.diff` bytes. If `git diff` output isn't stable across invocations, verification could produce false failures.

### 2. `DelegationJobStore.update_status` still public (inherited from poll session)

No remaining callers for status-only transitions. Direct `update_status("completed")` would strand `promotion_state=None`.

### 3. Skill rendering behavior untestable without live session

The delegate skill's rendering (diff display, escalation formatting, ceremony gates) cannot be tested via Python unit/integration tests. Only a live Claude session invoking `/delegate` can verify the skill works end-to-end. The bounded verification in Task 7 covers server-side behavior but not skill UX.

### 4. Pre-migration multi-attention-job state

Sessions started before the widened busy gate may have multiple attention-active jobs. The `attention_job_count` field in `active_delegation` surfaces this, but the skill should warn and the state is self-resolving (widened gate prevents new multi-attention states).

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| Design spec | `docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md` | Normative design |
| Implementation plan | `docs/superpowers/plans/2026-04-21-delegate-skill-ux-implementation.md` | Execution plan |
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Tool surface, response shapes |
| Promotion protocol | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | State machine, preconditions |
| Recovery and journal | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Journal phases, concurrency |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-21_10-37_t06-pending-escalation-view-projection-merged.md`
- T-06 arc: ... → PendingEscalationView projection → **delegate skill design + plan (this handoff)**

### Commits this session

| Commit | Title |
|--------|-------|
| `c5d0dc39` | docs(t20260330-06): delegate skill UX design spec |
| `7cc7d04a` | docs(t20260330-06): delegate skill UX implementation plan |
| `9f631dce` | fix(t20260330-06): revise implementation plan per review findings |
| `ff193f00` | fix(t20260330-06): address cross-surface semantics in plan and design spec |

## Gotchas

### 1. `_make_job` helper defaults `promotion_state="pending"`, not `None`

**Symptom:** Tests that claim "null promotion_state" would create jobs with `promotion_state="pending"` unless explicitly passing `promotion_state=None`.

**Root cause:** The test helper at `test_delegation_job_store.py:17` defaults to `"pending"` for convenience (most tests need pending jobs).

**Prevention:** Always pass `promotion_state=None` explicitly in tests that need null promotion_state. The plan's test snippets already do this.

### 2. `codex.status` `errors` field is blocking for consult/dialogue

**Symptom:** Appending delegation diagnostics to `errors` would cause `/consult-codex` to stop even when the advisory runtime is healthy.

**Root cause:** `consult-codex/SKILL.md:31` explicitly stops when `errors` is non-empty. The `errors` field is treated as a global health indicator, not a domain-specific diagnostic.

**Prevention:** Use `delegation_status_error` for delegation diagnostics. Never append domain-specific diagnostics to global `errors`.

### 3. `active_delegation` is null from `ControlPlane.codex_status()` — MCP overrides it

**Symptom:** The `control_plane.py:135` hardcodes `active_delegation: None`. This is correct — the MCP layer overrides it with delegation state.

**Root cause:** `ControlPlane` owns advisory runtime state. Delegation state is owned by `DelegationController`, which lives at the MCP server level.

**Prevention:** The MCP-side enrichment in `_dispatch_tool` is the only place `active_delegation` gets populated. Do not try to populate it in `ControlPlane`.

### 4. `build_execution_resume_turn_text` still takes `PendingServerRequest` (inherited)

**Symptom:** Future developer sees `pending_request=request` in `delegation_controller.py:1682` and thinks it's a missed rename from the PendingEscalationView projection.

**Root cause:** Intentional — the prompt builder is internal and needs the authoritative request payload. The projection boundary is at response construction, not internal helpers.

**Prevention:** Don't rename this parameter. It's correct.

## User Preferences

### Detailed upfront analysis before implementation

User consistently provided detailed problem statements with specific file:line references, ranked options, and recommended approaches before any code was written. The session was entirely design/analysis — zero implementation. User verbatim: "continue with discussing the design."

### Adversarial review as quality gate

User conducted adversarial reviews after each major artifact (design spec, implementation plan). Reviews used a structured format: premise check, critical failures, high-risk assumptions, real-world breakpoints, hidden dependencies, adversarial perspectives, patterns, required changes, verdict. Three severity levels: major revision, minor revision, defensible.

### Contract hardening before consumer implementation

Consistent pattern from prior sessions: "It's important to do [prerequisite] before starting [consumer]." In this session: design spec and plan must be defensible before execution starts. In prior session: PendingEscalationView projection before delegate skill.

### Direct merge for small reviewed slices, PR for larger work

User declined PRs for the PendingEscalationView projection (small, reviewed in-session). The delegate skill implementation (7 tasks, safety-bearing server changes) is likely PR-worthy. User hasn't specified — ask when implementation is complete.

### Subagent-driven development for execution

User explicitly chose subagent-driven-development: "next session execute with subagent-driven-development." This matches the plan's task structure — independent tasks with review between each.
