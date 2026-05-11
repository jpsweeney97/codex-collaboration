---
date: 2026-04-17
time: "18-01"
created_at: "2026-04-17T18:01:30Z"
session_id: 1e1e6a3d-e6e5-41a4-828c-6402dd821293
resumed_from: "docs/handoffs/archive/2026-04-17_17-09_t05-tmp-hardening-three-step-chain-landed.md"
project: claude-code-tool-dev
branch: docs/t05-execution-start-plan
commit: bd850302
title: "T-05 execution-start slice plan drafted and awaiting user scrutiny"
type: handoff
files:
  - docs/plans/2026-04-17-t05-execution-start-slice.md
---

# T-05 execution-start slice plan drafted — awaiting review

## Goal

Turn the 17:09 handoff's Next Step #1 ("first execution-wiring slice") into a reviewable, executable implementation plan for `codex.delegate.start`. Resolve the scope-ambiguity lurking in the handoff (does this slice dispatch `run_execution_turn()` or not?), get a lock from the user, and write a TDD-structured plan that respects the lock's guardrails.

**Bigger picture.** T-05 is the execution-domain foundation packet for codex-collaboration. T-06 (promotion + delegate UX) and T-07 (analytics + cutover) both block on T-05. Closing the execution-domain work requires a series of slices — this plan covers the first (and foundational) one, which lands the persistent surfaces later slices depend on: worktree ownership, execution bootstrap, `DelegationJob` persistence, busy gate, audit emission.

**Trigger.** The 17:09 handoff's Next Action: "Pick up T-05 execution-wiring slice in a fresh session per Next Steps #1." User invoked `/effort` → max, then `/superpowers:writing-plans` with arg "Write a detailed implementation plan". I spent the session in three phases: scope-lock (recommended Variant A; user ratified with explicit guardrails), plan authoring (2158 lines of TDD structure), and self-review (tightened AC overclaims, fixed test-count math). Session ends **before** the plan has been reviewed by the user — that's the next session's opening act.

**Success criteria (of this session, not the slice):**

1. ✅ Research phase grounded in normative docs — T-05 ticket, contracts.md, foundations.md, recovery-and-journal.md, delivery.md read in full.
2. ✅ Scope ambiguity surfaced and locked — Variant A (bootstrap only, no turn dispatch) explicit in writing.
3. ✅ Plan written with TDD-per-step, full code, exact commands, explicit commit boundaries.
4. ✅ Self-review pass tightened AC overclaims per user guardrails and fixed test-count arithmetic.
5. ✅ User explicitly chose to defer plan review to next session.

All five met. Plan on disk at `docs/plans/2026-04-17-t05-execution-start-slice.md`; branch `docs/t05-execution-start-plan`; not yet committed.

## Session Narrative

**Phase 1 — Load handoff and take stock (~2 min).** `/load` resolved cleanly from the 17:09 handoff. State file written at `docs/handoffs/.session-state/handoff-1e1e6a3d-e6e5-41a4-828c-6402dd821293`. `git status` clean on `main@bd850302`. Baseline confirmed: 593 plugin tests green, substrate slice + Q2 amendment + tmp-exclusion restore all landed in the previous session's three-step chain. No surprises; no work in flight to absorb. Prior handoff's Next Step #1 designated as this session's target: "First execution-wiring slice — the thinnest real `codex.delegate.start`."

**Phase 2 — `/effort` max, then `/superpowers:writing-plans` (~1 min).** User raised effort to max and invoked the writing-plans skill with arg "Write a detailed implementation plan." Announced using the skill. No additional scope parameters from user — the handoff is the authoritative scope source.

**Phase 3 — Research phase, massive parallel reads (~10 min).** Before drafting, I needed the normative contracts fully loaded. Surveyed directory structures and file sizes first (batched `wc -l` + `ls`), then read the relevant authorities in parallel:
- T-05 ticket (352 lines, post-amendment) — read full for ACs, Q0a/Q2 decisions, Amendment section, verification steps
- contracts.md (295) — DelegationJob fields (`:59-73`), JobBusy response shape (`:235-244`), AuditEvent schema (`:180-202`), MCP tool surface
- foundations.md (323) — execution domain defaults (`:99-116`), context profiles (`:228-241`), split-runtime rationale, max-1 default
- recovery-and-journal.md (177) — delegation runtime crash recovery, concurrency limits (`:144-149`), audit triggers, retention defaults
- delivery.md (300) — build Step 6 scope, Step 7 scope (operation-journal idempotency for delegation lives here, not Step 6)
- spec.yaml — authority precedence
Plus current server code: runtime.py (264), models.py (294), mcp_server.py (290), control_plane.py (477), journal.py (310), lineage_store.py (211), approval_router.py (91), test_runtime.py (216), profiles.py (166), dialogue.py first 150, codex_runtime_bootstrap.py full (106), test_mcp_server.py first 120, conftest.py.

**Phase 4 — Surface the scope ambiguity (~3 min).** Two observations cascaded:
- **Greenfield slice:** `rg 'codex.delegate|delegate_start|DelegationJob' packages/plugins/codex-collaboration` returned **no matches**. No existing delegation code anywhere. Every surface is new. Confirmed no `worktree_manager.py`, no `ExecutionRuntimeRegistry`.
- **Scope ambiguity in the 17:09 handoff:** Handoff Next Steps #1 item 4 said *"`run_execution_turn()` actually called from `codex.delegate.start` with the six-field SandboxPolicy."* But T-05's AC 1 says only *"The codex-collaboration server can start an isolated execution runtime for a delegation job."* "Can start" ≠ "dispatches a turn." Also `delivery.md` Step 6 defines start scope as "Execution runtime, worktree manager, isolation, context assembler/profile filter" — no turn dispatch. Two materially different slice shapes.

This was the session's pivot. I could have silently picked one and written a plan. Instead I stopped, named the two variants (A = bootstrap only, B = bootstrap + synchronous first turn), listed pros/cons and AC-coverage deltas, recommended Variant A, and asked the user to choose.

**Phase 5 — User ratifies Variant A with explicit guardrails (~2 min).** User's reply was a tight structural lock — not a one-word "A" but a reasoned position:
- **Contract lens:** "the authoritative wording is the T-05 acceptance language, not the handoff shorthand. 'Can start an isolated execution runtime' is materially weaker than 'dispatches a real execution turn synchronously,' and I would not let a handoff phrase silently widen scope beyond the ticket and delivery.md."
- **Milestone lens:** "Variant A is the credible thin slice. It lands the durable surfaces the next slice depends on: worktree ownership, execution bootstrap, persisted `DelegationJob`, busy gate, and audit emission. Variant B smuggles in unresolved design choices that do not need to be solved yet: MCP blocking behavior, progress/observability semantics, objective-to-prompt shaping, and what happens when live runtime requests appear before notification-loop capture exists."
- **Guardrails** (4 specific constraints on the plan text):
  1. "Treat `run_execution_turn()` as explicitly deferred, not implicitly included."
  2. "Do not claim AC 6 is closed if live runtime requests still are not captured into pending-request state."
  3. "Phrase the success boundary narrowly: `codex.delegate.start` can create and bootstrap a real isolated execution runtime and persist its job record, but it does not yet execute the first delegation turn."
  4. "If you choose to mention the handoff item, interpret it as 'the first real execution path will eventually use the hardened 6-field helper,' not 'this slice must synchronously run a turn.'"
- **Posture:** "No redirect. Stay on the T-05 execution-wiring thread. When you share the draft, I'll review it against this boundary and push hard on any scope inflation or overclaimed acceptance coverage."

This is the operating frame for the rest of the session and for next session's review.

**Phase 6 — Create docs branch and plan skeleton (~1 min).** Verified directory conventions: `docs/plans/` (project convention, 37 peer plans) vs `docs/superpowers/plans/` (skill default, mostly design docs). Chose `docs/plans/` — the skill explicitly allows project preferences to override. Created branch `docs/t05-execution-start-plan` from `main@bd850302`. (Branch-protection hook forces docs/* prefix for doc edits.)

**Phase 7 — Write the plan (~20 min, ~2158 lines in one `Write` call).** Structure: 9 tasks, TDD-per-step, 8 feature commits + 1 merge, 593 → 624 expected tests. Each step includes the actual test code, the actual implementation code, the exact command to run, and the exact commit message. No TODOs, no "similar to" shorthand, no "fill in details."

Plan task shape:
1. Model types (`DelegationJob`, `JobBusyResponse`, `AuditEvent.job_id` promotion, `JobStatus`/`PromotionState` literals)
2. `DelegationJobStore` — session-scoped JSONL (parallels `LineageStore`)
3. `WorktreeManager` — `git worktree add --detach` wrapper
4. `ControlPlane.start_execution_runtime` — non-cached ephemeral bootstrap
5. `DelegationController` — orchestrator (busy → worktree → runtime → persist → audit)
6. MCP tool registration + dispatch + lazy factory pattern
7. Production wiring in `codex_runtime_bootstrap.py`
8. End-to-end integration test (real tmp git repo + stub session)
9. Full plugin suite + ruff + `--no-ff` merge

**Phase 8 — Self-review pass, tighten overclaims (~5 min).** Ran the skill's self-review checklist against the draft. Found three items:
- **AC 2 overclaim.** Original: "✅ verified via call-site test — helper already exists from prior slice." But App Server applies `sandboxPolicy` on `turn/start`, not at runtime-process init — and this slice has no turn dispatch. The helper's construction is verified by prior-slice tests (`test_runtime.py:167-183`, still green in the full suite), but THIS slice adds no new call site. Per user guardrail #2 ("do not claim AC 6 is closed if..."), the same honest-phrasing standard applies to AC 2. Rewrote the row to "🔶 partially — App Server applies the sandbox on turn/start, not on runtime-process init. The six-field helper was verified by the prior slice... This slice adds no new call site for the helper; the first live call lands with turn dispatch. AC 2's 'starts with' phrasing reads as a forward-looking contract about the first turn, not runtime-process init."
- **AC 7 overclaim.** Similar logic: sandbox-construction test coverage remains at `test_runtime.py:167-183` (prior slice), not added here. Softened to "🔶 partially" with the honest note.
- **Test-count arithmetic off by one in tasks 6-9.** I claimed 6 new Task-6 tests in the commit step but actually wrote 5. Cascade: 622 (not 623) after Task 6, 623 (not 624) after Task 7, 624 (not 625) after Task 8, 31 (not 32) tests added total in Task 9's final count.
All three fixed with targeted Edit calls.

**Phase 9 — Post-Write hook noted length (~1 min).** File is 2158 lines; `PostToolUse` hook suggested `/superspec:spec-writer` to modularize (files >500 are "difficult to reference"). I considered and rejected: this is an implementation plan with full code per step, not a spec; peer plans in `docs/plans/` are similar size (T-04 gatherers plan is ~40KB); modularizing would fight the "engineer holds plan in one context" goal that motivated writing it in the first place. Noted the hook output but proceeded.

**Phase 10 — Present plan to user with known-deferrals for pushback (~2 min).** Summarized the plan shape (table of 9 tasks with commits/tests), called out four things I expected the user might push back on: (a) no ExecutionRuntimeRegistry in this slice, (b) no operation-journal entry for job creation, (c) sandbox never actually applied in this slice (honestly flagged in AC 2), (d) `docs/plans/` vs `docs/superpowers/plans/` filename choice. Asked for scrutiny + execution-mode choice (subagent-driven vs inline).

**Phase 11 — User /save, deferring review (~1 min).** User's reply: "save a handoff. I will review the plan, and I will begin next session by sharing my feedback." No commit/merge of the plan. The plan sits untracked on the docs branch, waiting.

## Decisions

### Decision 1: Variant A (bootstrap only, no turn dispatch)

**Choice:** `codex.delegate.start` creates worktree + bootstraps execution runtime (initialize + account/read + thread/start) + persists DelegationJob + emits delegate_start audit + enforces busy gate. **No `run_execution_turn()` call.** The runtime is left alive with a thread created; the first real turn is dispatched by a follow-up slice.

**Driver.** User's verbatim reasoning (see User Preferences below). Two lenses:
- Contract lens: T-05 AC 1 text is "can start," not "dispatches a turn." `delivery.md` Step 6 lists "Execution runtime, worktree manager, isolation, context assembler/profile filter" — no turn dispatch. User: "the authoritative wording is the T-05 acceptance language, not the handoff shorthand."
- Milestone lens: Variant A is the thin slice that unblocks T-06/T-07 without bundling unresolved design work. Variant B would have forced decisions on: MCP blocking during turn execution, progress/observability semantics, objective-to-prompt shaping, and pre-capture notification-loop handling. User: "Variant B smuggles in unresolved design choices that do not need to be solved yet."

**Alternatives considered:**
- **Variant B (bootstrap + synchronous first turn):** rejected — smuggles ≥4 unresolved design choices into a slice that doesn't need them; user explicit.
- **Pick one silently (no variant offer):** rejected — this was material scope ambiguity; silent pick would have been exactly the "handoff-shorthand widens scope" failure mode user called out.

**Implications:**
- `run_execution_turn()` is deferred to the next slice. Handoff #4 language is reinterpreted as forward-looking: "the call path IS wired such that when turn dispatch lands, it uses the six-field helper."
- `ExecutionRuntimeRegistry` deferred — no caller needs the session handle in this slice.
- AC 6 (approval routing) remains **open** — pending-request capture requires the notification-loop wiring that lands with turn dispatch.
- AC 2's "starts with" is interpreted as forward-looking; actual sandbox enforcement happens when the first turn dispatches.

**Trade-offs accepted:** Slice feels less "complete" relative to handoff phrasing. The plan's honest AC table shows three partial statuses — looks softer than claiming all-green. Accepted because overclaiming violates user guardrail #2.

**Confidence:** High (E2) — user explicit directive + my independent scope analysis agreed.

**Reversibility:** High — plan is not yet committed; scope can still expand if user changes their mind during review.

**Change trigger:** User override during next-session review; user decides Variant B should be in scope after all.

### Decision 2: Save plan to `docs/plans/` rather than `docs/superpowers/plans/`

**Choice:** Plan lives at `docs/plans/2026-04-17-t05-execution-start-slice.md`.

**Driver.** Project convention. `docs/plans/` holds 37 implementation plans; `docs/superpowers/plans/` holds mostly design/decision docs (brainstorming-skills-redesign, architecture-stress-test-plan, etc.). The writing-plans skill's header explicitly says "User preferences for plan location override this default." Observed pattern: T-04 plans, T-8 plans, engram plans — all live in `docs/plans/`.

**Alternatives considered:**
- **`docs/superpowers/plans/`:** rejected — diverges from project convention; skill default should not override observed repo pattern.

**Implications:** Plan is discoverable alongside peer plans. Future automation (if any) that scans `docs/plans/` for active plans will find it.

**Trade-offs accepted:** Divergence from skill default. Next time this skill runs in this repo, it might default to `docs/superpowers/plans/` and need to be steered again. Low-cost.

**Confidence:** Medium (E1) — inferred convention from filesystem listing; not explicit rule.

**Reversibility:** High — `git mv` if user prefers.

**Change trigger:** User preference, or explicit project convention documented elsewhere.

### Decision 3: Honest AC coverage table (AC 2, 6, 7 flagged partial)

**Choice:** Plan's "Acceptance coverage" table marks AC 2 🔶 partially, AC 6 ❌ not closed, AC 7 🔶 partially — with explicit reasoning for each.

**Driver.** User guardrail #2 verbatim: "Do not claim AC 6 is closed if live runtime requests still are not captured into pending-request state." Same standard applies to AC 2 (sandbox not applied without turn dispatch) and AC 7 (sandbox-construction test coverage is prior-slice).

**Alternatives considered:**
- **Claim all ACs closed:** rejected — violates guardrail; user warned "I'll review it against this boundary and push hard on any scope inflation or overclaimed acceptance coverage."
- **Omit the coverage table:** rejected — table is the explicit trace from plan scope to ticket AC; removing it would hide the claim-to-evidence mapping.

**Implications:** Plan honestly represents what's complete vs what lands next. Reviewer can trust the assertions. Next slice has an explicit list of which ACs it inherits as open.

**Trade-offs accepted:** Plan looks less "complete" on paper — only 4 full ✅ out of 7 ACs. Accepted because honesty > optics.

**Confidence:** High (E1) — directly from user directive.

**Reversibility:** High — text edit.

**Change trigger:** N/A — user directive is the basis.

### Decision 4: 9 tasks, 8 feature commits + 1 merge (--no-ff)

**Choice:** Plan structures work as 9 tasks: 1 pre-flight + 8 feature tasks + 1 merge. Each feature task ends in its own commit; final merge uses `--no-ff` matching prior session's three-step-chain pattern.

**Driver.** Prior session's "commit topology encodes policy" lesson. Each commit is a coherent unit: one task = one concept (models, store, manager, runtime bootstrap, controller, tool registration, production wiring, integration test). The audit trail preserves task boundaries.

**Alternatives considered:**
- **Fewer commits (bundle):** rejected — bundles hide task boundaries and defeat the "each commit independently green" property that makes rollback/bisect feasible.
- **More commits (per-step within task):** rejected — fragments the audit trail and turns a feature into a noise stream.

**Implications:** Reviewers see 8 distinct feat commits on the feature branch, 1 merge on main. Easy to bisect, easy to roll back any specific task.

**Trade-offs accepted:** Verbose history — 8 commits for what could conceptually be one change. Accepted because audit-trail is first-class per prior session's learning.

**Confidence:** High (E1) — matches prior session's pattern (substrate slice had 3 feat commits + 3 merges under multi-constraint stacking; here single feature branch so 8+1 is appropriate).

**Reversibility:** Medium — could be restructured during execution if user requests bundling.

**Change trigger:** User preference for fewer commits.

### Decision 5: No ExecutionRuntimeRegistry in this slice

**Choice:** `DelegationController.start` bootstraps the session via `ControlPlane.start_execution_runtime`, receives `(runtime_id, session, thread_id)`, but **does not retain** the session handle in any registry. The runtime process stays alive via whatever references the session's internal subprocess handle; when that subprocess goes out of scope, the runtime dies.

**Driver.** YAGNI. No caller in this slice needs the session handle — no `codex.delegate.poll`, no `codex.delegate.decide`, no turn dispatch. Adding a registry now would be premature abstraction.

**Alternatives considered:**
- **Build `ExecutionRuntimeRegistry` now:** rejected — unused until turn dispatch lands; adds scope without paying rent this slice.

**Implications:**
- Follow-up slice MUST add a registry before wiring turn dispatch — without it, `run_execution_turn` has no way to find the session for a given `job_id`.
- In this slice's production path, the runtime subprocess may be garbage-collected shortly after `start()` returns, since no code retains a reference. Tests use fake sessions so this isn't observable there.
- Plan's Risks section calls this out explicitly as "Known deferral #1."

**Trade-offs accepted:** Production startup creates a runtime process that is essentially orphaned — it will be reaped on process exit but may live briefly as a zombie-ish ephemeral. Not ideal but also not harmful in this slice since no execution work occurs. A user pushing back on this would have a defensible case.

**Confidence:** Medium (E1) — my judgment call; defensible under YAGNI but may not survive scrutiny.

**Reversibility:** Medium — adding a registry in the follow-up is standard; this slice's structure does not preclude it.

**Change trigger:** User says the registry belongs in this slice; scrutiny finds the orphan-process behavior unacceptable.

### Decision 6: No operation-journal entry for job creation

**Choice:** `DelegationJobStore` is the sole persistence layer for job state. No entry written to `OperationJournal` when `codex.delegate.start` is called.

**Driver.** `delivery.md` Step 7 scope: "`codex.delegate.poll` + `.decide` + `.promote`" is where "[promotion protocol](promotion-protocol.md), [operation journal](recovery-and-journal.md#operation-journal)" enter. Step 6 (this slice) does not include journal idempotency for delegation.

Also the `OperationJournal` currently only supports `thread_creation` and `turn_dispatch` operations (`journal.py:_VALID_OPERATIONS` line 35). Adding a `job_creation` operation would require extending the literal type, the validator, and the replay callback — scope creep.

**Alternatives considered:**
- **Extend `OperationJournal` with `job_creation` op now:** rejected — violates delivery-step scoping; operation journal for delegation is a promotion-slice concern.

**Implications:**
- Busy gate via `DelegationJobStore.list_active()` is the sole dedup mechanism. Under max-1 concurrency + serialized MCP dispatch, this is sufficient — two concurrent start calls cannot race because MCP serializes them, and the busy gate catches sequential duplicates.
- Follow-up slice with promotion must add `job_creation` journaling for replay-safety if restarting a crashed delegation.

**Trade-offs accepted:** Repeated start calls with identical args could, in theory, create two jobs if the busy gate's read happens before the prior write is durable — but the store's `fsync` and MCP's serialized dispatch close that window.

**Confidence:** Medium (E1) — delivery.md evidence + serialization invariant.

**Reversibility:** High — op-literal extension is a minor change.

**Change trigger:** Journal idempotency becomes necessary before promotion slice; user requests it in this slice.

## Changes

### Files modified (this session)

| File | Change | Commit |
|---|---|---|
| `docs/plans/2026-04-17-t05-execution-start-slice.md` (new) | Created; 2158 lines | Uncommitted |

### Git state changes

| Commit | Branch | Subject |
|---|---|---|
| (none) | `docs/t05-execution-start-plan` | Branch created off `main@bd850302`; plan is untracked |

No commits made. No push. Main unchanged at `bd850302`.

### Handoff / state files

- Archived (at session start): `2026-04-17_17-09_t05-tmp-hardening-three-step-chain-landed.md` → `docs/handoffs/archive/`
- State file (this session): `docs/handoffs/.session-state/handoff-1e1e6a3d-e6e5-41a4-828c-6402dd821293` — to be cleaned by this save
- New handoff (this file): `docs/handoffs/2026-04-17_18-01_plan-t05-execution-start-slice-drafted-awaiting-review.md`

## Codebase Knowledge

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `docs/handoffs/2026-04-17_17-09_*.md` | Prior handoff | Next Step #1 target; baseline 593 tests; Variant A/B ambiguity lurks in item 4 |
| `docs/tickets/2026-03-30-*.md` | T-05 ticket (full 352 lines) | ACs 1-7; Q0a implicit scope; Q2 amendment with six-field; reachability-gate language in Amendment |
| `docs/superpowers/specs/codex-collaboration/contracts.md` | Contracts authority | `DelegationJob` at `:59-73`; `PendingServerRequest` at `:75-91`; `JobBusy` at `:235-244`; `AuditEvent` at `:180-202` with top-level `job_id`; MCP tool surface table at `:18-30` |
| `docs/superpowers/specs/codex-collaboration/foundations.md` | Foundation authority | Execution-domain defaults at `:99-116`; context profile budgets at `:258-262` (Execution: 12KiB soft / 24KiB hard); max-1 concurrency at `:304` |
| `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Recovery contract | Delegation runtime crash at `:116-123` (preserve worktree + artifacts; mark `unknown`); concurrency limits at `:144-149`; retention at `:164-177` |
| `docs/superpowers/specs/codex-collaboration/delivery.md` | Delivery authority | Build Step 6 at `:160` (start) vs Step 7 at `:161` (poll/decide/promote); operation-journal idempotency is Step 7, not Step 6 |
| `docs/superpowers/specs/codex-collaboration/spec.yaml` | Authority map | Precedence: foundation → contracts → promotion-contract → advisory-policy → recovery-contract → delivery → decisions |
| `packages/plugins/codex-collaboration/server/runtime.py` | Current runtime | `build_workspace_write_sandbox_policy` at `:23-38` (six-field); advisory/execution split via `run_advisory_turn`/`run_execution_turn` over private `_run_turn`; `start_thread` at `:107-124` |
| `packages/plugins/codex-collaboration/server/models.py` | Current types | `AuditEvent` at `:146-161` has `extra: dict` — `job_id` is deferred there, must be promoted for this slice |
| `packages/plugins/codex-collaboration/server/mcp_server.py` | MCP server | `TOOL_DEFINITIONS` at `:15-100`; `_ensure_dialogue_controller` at `:132-151` (lazy-factory one-way pin); `_dispatch_tool` at `:233-277` |
| `packages/plugins/codex-collaboration/server/control_plane.py` | ControlPlane | `get_advisory_runtime` at `:253-262`; `_bootstrap_runtime` at `:275-289`; `_probe_runtime` at `:291-422`; advisory runtime cached in `_advisory_runtimes` dict (`:78`) |
| `packages/plugins/codex-collaboration/server/journal.py` | OperationJournal | `_VALID_OPERATIONS` at `:35` = `("thread_creation", "turn_dispatch")` — no job_creation op yet; `append_audit_event` at `:163-167` |
| `packages/plugins/codex-collaboration/server/lineage_store.py` | Pattern to mirror | Session-scoped JSONL at `plugin_data_path / "lineage" / session_id / "handles.jsonl"`; append-only; replay-on-read |
| `packages/plugins/codex-collaboration/server/approval_router.py` | Existing approval router | `parse_pending_server_request` at `:37-71` — ready to consume events once notification loop is wired (next slice) |
| `packages/plugins/codex-collaboration/server/dialogue.py` (first 150) | Pattern to mirror | `DialogueController.__init__` at `:93-110` takes `session_id: str` |
| `packages/plugins/codex-collaboration/server/profiles.py` | Profile resolver | Sandbox + approval widening rejected until freeze-and-rotate exists; only advisory "read-only" + "never" approvals accepted today |
| `packages/plugins/codex-collaboration/server/containment.py` (first 80) | Rule out for reuse | Confirmed dialogue/T4-shakedown specific; has `active-run-*` / `seed-*` / `scope-*` conventions that do NOT generalize to delegation |
| `packages/plugins/codex-collaboration/scripts/codex_runtime_bootstrap.py` | Production entry point | `_read_session_id` at `:34-54` reads `${CLAUDE_PLUGIN_DATA}/session_id` published by SessionStart hook; `_build_dialogue_factory` at `:57-82` |
| `packages/plugins/codex-collaboration/tests/test_runtime.py` | Current test pattern | `_StubClient` pattern for JSON-RPC; sandbox assertion at `:167-183` (six-field shape locked by prior slice) |
| `packages/plugins/codex-collaboration/tests/test_mcp_server.py` (first 120) | MCP test pattern | `FakeControlPlane` + `FakeDialogueController` fixtures; dispatch-test shape |
| `packages/plugins/codex-collaboration/tests/conftest.py` | Shared fixtures | `make_test_handle` factory; vendored-schema dir fixture |

### Architecture map: T-05 delegation surfaces (as planned)

| Layer | File | Status in this plan | Pattern source |
|---|---|---|---|
| Types | `server/models.py` (extend) | Task 1 | Existing `AdvisoryRuntimeState` + new dataclass additions |
| Persistence | `server/delegation_job_store.py` (new) | Task 2 | Mirror of `server/lineage_store.py` |
| Worktree | `server/worktree_manager.py` (new) | Task 3 | No existing pattern — greenfield git wrapper |
| Runtime bootstrap | `server/control_plane.py` (extend) | Task 4 | Mirror of `get_advisory_runtime` but non-cached |
| Orchestrator | `server/delegation_controller.py` (new) | Task 5 | Mirror of `server/dialogue.py::DialogueController.start` |
| MCP surface | `server/mcp_server.py` (extend) | Task 6 | Mirror of `_ensure_dialogue_controller` + tool dispatch |
| Production wiring | `scripts/codex_runtime_bootstrap.py` (extend) | Task 7 | Mirror of `_build_dialogue_factory` |
| E2E test | `tests/test_delegate_start_integration.py` (new) | Task 8 | New — combines tmp_path git init + stub session |

### Worktree path convention (plan's choice)

Spec's foundations.md `:103` says "Storage: `${CLAUDE_PLUGIN_DATA}/runtimes/delegation/<job-id>/`". Plan uses `${CLAUDE_PLUGIN_DATA}/runtimes/delegation/<job-id>/worktree/` as the worktree leaf. Rationale: the spec's directory is the runtime's state directory; the worktree is one artifact inside it. This keeps "one job = one subdirectory" clean.

### Surprising findings / gotchas

- **No existing delegation code at all.** `rg 'codex.delegate|delegate_start|DelegationJob'` returned empty. Even `containment.py` (539 lines) is T4 shakedown code, not execution-domain.
- **App Server sandbox is per-turn, not per-runtime.** `sandboxPolicy` is a param on `turn/start`, not on `initialize` (see `runtime.py:193`). AC 2's "starts with SandboxPolicy" is actually a forward claim about the first turn, not runtime-process init.
- **`OperationJournal`'s literal type blocks delegation ops.** `_VALID_OPERATIONS = frozenset(("thread_creation", "turn_dispatch"))` at `journal.py:35`. Adding `"job_creation"` requires editing the literal, the validator, and the replay callback. Plan defers this.
- **Session_id wiring uses a filesystem publication pattern.** `codex_runtime_bootstrap.py:_read_session_id` reads `${CLAUDE_PLUGIN_DATA}/session_id` which is published by the SessionStart hook. Delegation factory uses the same pattern.
- **AuditEvent currently uses `extra: dict` for deferred delegation fields.** `models.py:158-161` comment says "job_id, request_id, artifact_hash, decision, causal_parent are deferred." Promoting `job_id` to top-level (Task 1) requires care — must keep `request_id` / others in `extra` until their flows land. Plan does this correctly.
- **DelegationController takes session_id in __init__ (same as DialogueController).** Factory reads `_read_session_id(plugin_data_path)` and passes it. Tests pass a literal `"sess-1"`-style string.
- **JobStatus enum has 6 values (not 4).** `contracts.md:71`: `queued`, `running`, `needs_escalation`, `completed`, `failed`, `unknown`. Plan's tests cover `queued`/`running`/`completed` transitions.
- **PromotionState enum has 8 values.** `contracts.md:70`. Plan uses `pending` (initial); other values land with promotion slice.

### Key locations to remember

| Concept | Location |
|---|---|
| T-05 ticket (with Amendment) | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` |
| T-05 AC list | ticket `:303-329` |
| Q2 Amendment | ticket `:248-301` |
| DelegationJob schema | `contracts.md:59-73` |
| JobBusy schema | `contracts.md:235-244` |
| Six-field sandbox helper | `runtime.py:23-38` |
| Sandbox test (still green) | `test_runtime.py:167-183` |
| AuditEvent (needs job_id promotion) | `models.py:146-161` |
| DialogueController (pattern) | `dialogue.py:90-150` |
| LineageStore (pattern) | `lineage_store.py:124-206` |
| MCP lazy-factory pattern | `mcp_server.py:132-151` |
| Production entry point | `scripts/codex_runtime_bootstrap.py:85-106` |
| Session ID publication read | `scripts/codex_runtime_bootstrap.py:34-54` |
| Execution-domain defaults | `foundations.md:99-116` |
| Concurrency max-1 | `recovery-and-journal.md:144-149` |
| Plan file (this session's deliverable) | `docs/plans/2026-04-17-t05-execution-start-slice.md` |

## Context

### Mental model

**Framing:** This session is about writing a contract for the next implementation session — not implementation itself. The plan is an artifact that must survive adversarial review.

- **Core insight:** The handoff's "next step" narrative and the ticket's AC text don't have to agree. When they don't, the ticket wins — because ACs are the contract and handoffs are shorthand. This session's key move was naming that disagreement out loud before writing the plan, so the plan could be locked against the right authority (the ticket).
- **Mental model:** *Plan-as-contract.* The plan is a binding agreement about what gets built. It doesn't matter that nothing is implemented yet — the text of the plan is the next-session's working agreement. That's why overclaims matter so much (user guardrail: "I'll push hard on any scope inflation or overclaimed acceptance coverage") — and why the self-review pass that tightened AC 2 / 6 / 7 was load-bearing.

Secondary insight: the session narrative is **"variant-name-before-pick."** Presenting Variant A + B with explicit pros/cons forces both parties to the same level of abstraction about the choice. If I'd just picked A and written a plan, the user would have had to reconstruct the variant structure to evaluate whether A was right. Naming A and B explicitly means the user can ratify the frame AND the choice in one move.

### Project state at session close

**T-20260330-05 (execution-domain foundation):** OPEN, high priority. Substrate from prior slice is live. Plan for "first execution-wiring slice" (bootstrap-only) is drafted at `docs/plans/2026-04-17-t05-execution-start-slice.md`. Awaiting user review. After review + landing, execution of the plan produces Commits 1-8 on `feature/t05-execution-start` and a `--no-ff` merge to main.

**T-20260330-06 / T-07:** OPEN, blocked by T-05.

**T-20260416-01 (codex.dialogue.reply extraction mismatch):** OPEN, medium priority. Independent parallel thread — unchanged this session.

### Environment snapshot at session close

- Branch: `docs/t05-execution-start-plan` (created this session)
- HEAD: `bd850302` (unchanged from session start)
- Working tree: **dirty** — `docs/plans/2026-04-17-t05-execution-start-slice.md` is untracked
- Origin/main: synced (no new pushes this session)
- Plugin suite: not run this session (no code changes)
- Memory: no new feedback files; MEMORY.md unchanged

### Why this work matters (bigger picture)

T-05 is the execution-domain foundation for codex-collaboration. The plan that came out of this session is the first real implementation blueprint for delegation — it is what turns the design decisions from the prior session (implicit scope from infrastructure, six-field sandbox, advisory/execution split) into concrete code. Getting the plan right is high-leverage: a bad plan produces a weekend of rework; a good plan produces a merge-ready slice in hours.

The user's review posture ("push hard on scope inflation and overclaimed acceptance coverage") is calibrated to the stakes. Plan review is the cheap gate before expensive execution.

## Learnings

### Contract text > handoff shorthand for scope resolution

**Mechanism.** When a prior handoff's next-step language diverges from the authoritative ticket text, the ticket wins. Handoffs are session-shorthand; they can say "X will call Y" when the actual contract is "Z can start an X." The session that picks up from the handoff has to resolve the divergence before writing a plan, because the plan is the contract for the next session.

**Evidence.** Handoff #4 said *"`run_execution_turn()` actually called from `codex.delegate.start`"* — suggesting Variant B. T-05 AC 1 says *"can start an isolated execution runtime"* — supporting Variant A. User verbatim: "the authoritative wording is the T-05 acceptance language, not the handoff shorthand." The three-step chain from the prior session itself was driven by the same principle (contract-text-authoritative re: AC amendment).

**Implication.** When resolving scope ambiguity, the order is:
1. Ticket AC text (authoritative)
2. `delivery.md` build-sequence scoping (authoritative)
3. Normative contract spec (authoritative)
4. Handoff next-step language (shorthand; may drift)

If 1-3 agree and 4 disagrees, 1-3 win. This recurs enough (prior session's Q2 amendment; this session's Variant A lock) to be a durable rule.

**Watch for.** Any place where a handoff's next-step prose seems tighter or looser than the ticket AC. Resolve by going to the ticket. Flag the divergence to the user rather than silently picking a side.

### Name the variants before picking

**Mechanism.** When a scope decision has two defensible shapes, presenting both variants with explicit pros/cons/AC-coverage is higher-leverage than picking one and explaining. The variant-name structure lets the other party ratify the frame AND the choice in one move; the silent-pick structure forces them to reverse-engineer both.

**Evidence.** This session's Phase 4/5 exchange: I offered Variant A (bootstrap only) and Variant B (bootstrap + first turn) with 4 explicit scope differences between them. User's reply was a tight lock with reasoning AND guardrails — they could respond at the level of the frame because I had named the frame. If I'd just picked A, the user would have had to first reconstruct "wait, did you consider a B-shaped version?" and then evaluate.

**Implication.** For scope decisions with >1 defensible shape, always name the variants. Cost: a few minutes and some text. Benefit: user can ratify the frame in one move; audit trail preserves the alternatives considered.

**Watch for.** Sessions where multiple interpretations of the task are on the table. If you notice yourself flipping between two framings, stop and write both up.

### Plan-as-contract makes AC honesty load-bearing

**Mechanism.** Implementation plans are contracts for the next session. An AC coverage table that overclaims ("AC 2 ✅ verified") reads as "this slice closes AC 2" — and if it doesn't, the next session inherits a false debt-closure that is hard to reopen. Honest phrasing ("🔶 partial, because...") keeps the debt visible.

**Evidence.** Self-review pass found two overclaims: AC 2 (sandbox never applied without turn dispatch) and AC 7 (sandbox-construction test coverage is prior-slice, not this slice). User guardrail #2: "Do not claim AC 6 is closed if live runtime requests still are not captured into pending-request state." The same standard applies to any AC where the literal text isn't satisfied by the slice's actual work.

**Implication.** When writing AC coverage tables, the rule is:
- ✅ only if the slice's in-scope work literally satisfies the AC text
- 🔶 if the substrate is in place but a call site is missing, or if prior-slice work counts
- ❌ if the AC remains open after this slice lands

Refuse to mark an AC ✅ for "satisfied by prior slice" — that belongs in the other slice's coverage table, not this one's.

**Watch for.** Any AC coverage claim. Run it against the literal text of the AC.

### When the skill's default path diverges from the repo's pattern, the repo wins

**Mechanism.** Skills have default paths (e.g., writing-plans: `docs/superpowers/plans/`). Repos have observed patterns (37 plans in `docs/plans/`). When they disagree, the repo's pattern is the stronger signal about project convention.

**Evidence.** The writing-plans skill header explicitly says "User preferences for plan location override this default." Filesystem listing showed `docs/plans/` is where implementation plans live (37 entries, mostly T-04/T-8/engram/remediation). `docs/superpowers/plans/` has 10 entries, mostly design docs.

**Implication.** Before writing artifacts, check the filesystem for peer artifacts and follow that convention. Skills encode general best-practices; repos encode project-specific conventions. When they disagree, the repo wins silently.

**Watch for.** Any skill that specifies a default output location. Don't accept the default reflexively — check.

## Next Steps

### 1. User reviews the plan (the IMMEDIATE next action)

**Dependencies:** None. User explicitly deferred review to next session: "save a handoff. I will review the plan, and I will begin next session by sharing my feedback."

**First-next-action for future-Claude:** Wait for user feedback. Do NOT preemptively apply changes. Do NOT commit the plan before review.

**What user will likely scrutinize (from my self-review pass + known-deferrals flagged):**
- AC coverage table honesty — particularly AC 2 ("starts with sandbox" interpretation), AC 6 (pending-request capture scope), AC 7 (sandbox-test attribution)
- Task decomposition — is 9 tasks right? bundle some?
- Commit granularity — 8 feature commits + 1 merge
- Filename location (`docs/plans/` vs `docs/superpowers/plans/`)
- No ExecutionRuntimeRegistry deferral (Known Deferral #1)
- No operation-journal entry for job creation (Known Deferral #2)
- Sandbox-never-actually-applied reality (Known Deferral #3)
- Worktree path convention (`${CLAUDE_PLUGIN_DATA}/runtimes/delegation/<job-id>/worktree/`)
- Test count math (I noticed expected counts could still be off; real numbers may diverge during execution)
- Anything else the user pushes on

### 2. Apply user revisions (if any)

**Dependencies:** Step 1 complete.

**What to do:** Treat user feedback the same way the prior session treated the Q2 amendment Medium-severity findings:
- Parse each piece of feedback as either a wording issue, a scope issue, a decomposition issue, or a deferral-policy issue
- For wording issues: apply the refinement verbatim if user provided exact text (per "verbatim user wording" learning from prior session)
- For scope issues: update the Scope Lock section + AC coverage table + affected tasks
- For decomposition issues: restructure tasks/commits; update the decomposition philosophy section
- For deferral-policy issues: move items from "Out of scope" to "In scope" (or vice versa); update Risks section accordingly

### 3. Commit and merge the plan on the docs branch

**Dependencies:** Steps 1-2 complete.

**What to do:**
1. Verify `git status` shows only the plan file staged
2. Commit with: `docs(t20260330-05): plan first execution-wiring slice (bootstrap-only)`
3. Checkout main, `git merge --no-ff docs/t05-execution-start-plan -m "Merge docs/t05-execution-start-plan"`
4. Push main, delete the docs branch (local + remote)
5. Verify clean tree at new merge commit

This matches the prior session's three-step chain pattern — the plan is a contract doc that subsequent code depends on; it lands on main before any feature branch references it.

### 4. Execute the plan

**Dependencies:** Step 3 complete (plan is on main).

**User choice pending:** Subagent-driven (dispatches a fresh subagent per task via `superpowers:subagent-driven-development`) vs inline execution (batches tasks in-session via `superpowers:executing-plans`). User has not yet chosen.

**Estimated effort:** Large. 9 tasks, ~3-5 hours depending on execution mode. Each task ends in a commit; final merge requires full plugin suite (624 expected) + ruff clean.

### 5. Pending-request capture slice (follow-up, after step 4 lands)

**Dependencies:** Plan execution complete; T-05 execution-start slice merged to main.

**What to do:** Wire the notification loop (currently fail-silent in runtime.py `_run_turn`) to route App Server request messages through `parse_pending_server_request()` → persist as `PendingServerRequest` → expose via `needs_escalation` → available to `codex.delegate.decide` path (future).

This is the slice that actually closes AC 6. It also pairs with:
- Adding `ExecutionRuntimeRegistry` (Deferred #1 from this plan)
- Wiring first `run_execution_turn()` call in production path
- Adding `job_creation` op to OperationJournal (Deferred #2, if idempotency is in scope by then)

**Estimated effort:** Medium-large.

### 6. Decide-surface refinements (deferred debts from prior scrutinies)

Unchanged from prior handoff. Still blocked on the pending-request capture slice landing first.

### 7. T-20260416-01 extraction bug fix (parallel thread)

Unchanged from prior handoff.

### 8. Landing sequence (still-updated)

T-05 plan review + merge → T-05 execution-start slice (this plan executes) → T-05 pending-request capture slice → T-05 decide-surface + lifecycle refinements → T-05 COMPLETE → T-06 → T-07.

## In Progress

**Plan draft awaiting user review.** Not a clean stopping point — work is in flight; a deliverable exists but hasn't been reviewed or landed.

- **Approach:** Resume from prior handoff → /effort max → /superpowers:writing-plans → research phase (15+ files in parallel) → scope ambiguity discovered → Variant A/B presentation → user ratification with guardrails → plan authoring (one big Write call, 2158 lines) → self-review pass → present plan with known deferrals for pushback → user chose to defer review to next session → /save.
- **State:** Plan file written at `docs/plans/2026-04-17-t05-execution-start-slice.md` (2158 lines, untracked). Branch `docs/t05-execution-start-plan` exists with no commits. Main at `bd850302` unchanged.
- **Working:** Plan is internally consistent — 9 tasks, each TDD-structured with full code, exact commands, commit messages. AC coverage table is honest (3 partial statuses). Self-review pass caught 3 overclaims and test-count arithmetic errors; all fixed.
- **Not working:** Plan has not been reviewed. Concrete risks user may push on (summarized in Step 1 of Next Steps above).
- **Open question:** Does user agree with the scope / decomposition / deferral choices? Test count estimates may diverge from reality during execution — real numbers will be authoritative.
- **Next action (for next-session Claude):** Wait for user feedback on the plan. Do NOT apply preemptive changes. Do NOT commit.

## Open Questions

### 1. Is the 8-commit-per-feature-branch granularity appropriate?

**Context:** Each task ends in its own commit. Prior session's pattern was "merge per coherent change" at the merge level; within a feature branch, commit granularity is a separate choice.

**Impact:** LOW-MEDIUM. User may prefer fewer commits (bundle Tasks 1+2, or 6+7). Restructuring is mechanical.

**Decision pending until:** User reviews plan.

### 2. Should the plan move to `docs/superpowers/plans/`?

**Context:** I used `docs/plans/` per project convention. The skill default is `docs/superpowers/plans/`.

**Impact:** LOW. `git mv` if needed.

**Decision pending until:** User reviews plan.

### 3. Is "no ExecutionRuntimeRegistry" acceptable?

**Context:** The plan leaves the bootstrapped runtime's session handle unregistered. Production path would create a subprocess that's essentially orphaned after `start()` returns. Defensible under YAGNI but may not survive scrutiny.

**Impact:** MEDIUM. If user pushes back, I add a minimal registry to Task 5 (new field on controller + simple dict keyed by runtime_id).

**Decision pending until:** User reviews plan.

### 4. Should `worktree_path.resolve()` be hardened in this slice?

**Context:** Plan inherits prior slice's concern about `resolve()` on macOS following `/tmp` symlinks. Not a test issue today (tests use `tmp_path` under `/private/var/...`) but production worktrees live under `${CLAUDE_PLUGIN_DATA}`; still worth asserting canonicalization explicitly.

**Impact:** LOW. A `resolve(strict=True)` or explicit existence assertion is a few lines.

**Decision pending until:** User reviews plan.

### 5. Execution mode — subagent-driven vs inline?

**Context:** Post-plan-lock, user has not yet chosen execution mode. Plan's Execution Handoff section offers both options.

**Impact:** MEDIUM. Affects review cadence — subagent-driven = per-task review, inline = batched checkpoints.

**Decision pending until:** User reviews plan AND chooses mode.

## Risks

### 1. User rejects plan scope as too large or too small

**Impact:** Plan may need restructuring — bundle tasks, split tasks, expand scope to Variant B, or tighten further. Restructure is mechanical but delays execution.

**Mitigation:** Plan's Scope Lock section and AC coverage table make the scope claims explicit and falsifiable. User's feedback will be targeted.

### 2. Test count estimates diverge from reality during execution

**Impact:** Each task's step "X.4" states an expected test count (e.g., "606 passed"). Real counts during execution may be off by small amounts (forgotten tests, environmental flakiness, pre-existing test additions in main between plan-write and execution). A plan that treats estimates as contracts could trigger false-red runs.

**Mitigation:** Plan's verification step is specifically "run the full plugin suite and confirm green," not "confirm exactly 624." Executor should treat the count as guidance, not contract.

### 3. ExecutionRuntimeRegistry deferral is wrong

**Impact:** If user pushes back and wants the registry in this slice, Task 5 needs a significant addition (new field on DelegationController, dict keyed by runtime_id, close-session method). Scope grows by ~20% of Task 5.

**Mitigation:** Risk flagged explicitly in the plan's "Known Deferrals" + this handoff's Open Question #3. User will surface it if wrong.

### 4. Operation-journal deferral is wrong

**Impact:** If user wants journal idempotency for job creation in this slice, adds: literal extension in `journal.py`, new operation handler, controller journaling logic, ~4 new tests. Scope grows by ~10%.

**Mitigation:** Plan explicitly cites `delivery.md` Step 7 as the authority for deferral. Strong evidence.

### 5. Plan file length (2158 lines) triggers hook warning

**Impact:** Post-Write hook suggested `/superspec:spec-writer` to modularize. Reviewer may also find the length unwieldy. But peer plans in `docs/plans/` are similar size — the pattern is established.

**Mitigation:** This handoff preemptively justifies the length; hook output was noted but ignored per established pattern.

### 6. Context pressure mid-review

**Impact:** User-review may require significant edits to the plan. Editing in the same session that reviews carries context risk.

**Mitigation:** This handoff preserves full context so next session can pick up cleanly. Plan file itself is a complete artifact — reviewable without the conversation.

## References

### Session's deliverable

| Artifact | Location | Status |
|---|---|---|
| Implementation plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` | Untracked (2158 lines); awaiting review |
| Docs branch | `docs/t05-execution-start-plan` (off `main@bd850302`) | No commits |

### Authority documents (from research phase)

| Document | Location | Role |
|---|---|---|
| T-20260330-05 ticket (with Amendment) | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth |
| contracts.md (normative) | `docs/superpowers/specs/codex-collaboration/contracts.md` | DelegationJob `:59-73`; JobBusy `:235-244`; AuditEvent `:180-202` |
| foundations.md (normative) | `docs/superpowers/specs/codex-collaboration/foundations.md` | Execution defaults `:99-116`; max-1 `:304` |
| recovery-and-journal.md (normative) | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Delegation crash `:116-123`; concurrency `:144-149` |
| delivery.md (normative) | `docs/superpowers/specs/codex-collaboration/delivery.md` | Build Step 6 `:160`; Step 7 `:161` (operation journal scope) |
| spec.yaml | `docs/superpowers/specs/codex-collaboration/spec.yaml` | Authority precedence order |

### Memory files referenced this session

All under `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/`:

| Memory | Relevance |
|---|---|
| `feedback_contract_text_over_operational_interpretation.md` | **Load-bearing.** User cited the principle explicitly when locking Variant A: "I would not let a handoff phrase silently widen scope beyond the ticket and delivery.md." This is the same pattern that drove the Q2 amendment in the prior session. |
| `feedback_edit_in_repo.md` | Applied — plan landed in `docs/plans/` under the repo, not plugin cache. |
| Prior session's user-preferences | Applied — structured scrutiny, fast convergence once aligned, preserve-historical + edit-ACs-in-place, prescriptive contract wording. |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-17_11-59_t05-q0-decision-record-implicit-scope-landed.md` (indirect — chained from 17:09's resumed_from)
- Immediate predecessor (resumed_from): `docs/handoffs/archive/2026-04-17_17-09_t05-tmp-hardening-three-step-chain-landed.md`
- T-05 arc: kickoff (04-17 01:41) → Q0 decision (04-17 11:59) → tmp-hardening closure (04-17 17:09) → **plan for first execution-wiring slice (this handoff)** → plan execution (next session or later) → pending-request capture → decide-surface refinements → T-05 complete

## Gotchas

### 1. App Server sandboxing is per-turn, not per-runtime

**Symptom:** Bootstrap code that instantiates a runtime against a worktree has no enforced sandbox until the first `turn/start` call is dispatched.

**Root cause:** `sandboxPolicy` is a param on `turn/start` (runtime.py:193), not a configuration of the runtime process itself. App Server supports session-scoped approvals via `acceptForSession`, but the sandbox envelope is set per-turn.

**Prevention:** Don't claim AC 2 closed by runtime bootstrap alone. The honest reading: "the runtime is ready to receive turns with the six-field sandbox" (substrate), not "the runtime's process is sandboxed" (which would be the OS-level interpretation, not what App Server provides). Plan's AC 2 row now says this explicitly.

### 2. Handoff next-step shorthand can drift from ticket AC text

**Symptom:** Handoff says "X is called in slice Y" but the AC text for slice Y says "X can be called" — the difference between an eager-call requirement and a capability claim.

**Root cause:** Handoffs are session-end summaries, not contracts. The summarizing act introduces drift; the ticket is the stable contract.

**Prevention:** When resolving scope ambiguity, the order is: Ticket AC text → `delivery.md` scope → normative contracts → handoff next-step language. 1-3 win over 4 when they disagree. Flag divergence to user before proceeding.

### 3. `OperationJournal`'s literal type is a scope trap

**Symptom:** Adding a new operation kind (e.g., `job_creation`) requires editing the `_VALID_OPERATIONS` frozenset at `journal.py:35` — it's not just "add an entry."

**Root cause:** The journal uses strict validation against a closed enum for schema safety. Adding a value is intentional friction.

**Prevention:** Don't add operation kinds in slices that don't need journal idempotency. `delivery.md` scopes delegation-journal idempotency to Step 7 (poll/decide/promote), not Step 6 (start). This plan respects that scoping.

### 4. `containment.py` is not reusable for delegation worktrees

**Symptom:** A cursory skim might suggest `containment.py` (539 lines) has worktree or sandbox code that delegation could reuse.

**Root cause:** `containment.py` is T4 shakedown-specific — it deals with `active-run-*`, `seed-*`, `scope-*`, transcript lifecycle for the dialogue shakedown flow. None of its primitives generalize.

**Prevention:** Confirmed by reading the first 80 lines and grepping for `worktree_manager|git.*worktree.*add`. Neither found. Delegation worktree code is greenfield.

### 5. Plan-file length triggers modularization hook

**Symptom:** Files >500 lines get a post-Write hook suggestion: "Consider invoking `/superspec:spec-writer` to create a modular spec structure."

**Root cause:** Hook is general-purpose; it doesn't know whether the file is a spec (should modularize) or a plan (must stay whole for TDD-per-step coherence).

**Prevention:** For implementation plans, ignore the hook. Peer plans in `docs/plans/` are similar size. The "engineer holds plan in one context" goal is the reason plans are flat.

### 6. `docs/plans/` vs `docs/superpowers/plans/`

**Symptom:** The writing-plans skill defaults to `docs/superpowers/plans/`, but this repo's convention is `docs/plans/`.

**Root cause:** Skill defaults encode general best practices; repos encode project-specific conventions. Skill header explicitly allows override.

**Prevention:** Check the filesystem for peer artifacts before accepting a skill's default path. In this repo, `docs/plans/` (37 entries, mostly implementation plans) is the convention; `docs/superpowers/plans/` (10 entries, mostly design/decision docs) is not.

### 7. AC coverage tables are contracts, not summaries

**Symptom:** Marking an AC ✅ when the slice's actual work only provides substrate (not a live call site) reads as "this slice closes the AC" — which is wrong if the first live call site lands in a later slice.

**Root cause:** Implementation plans are contracts for the next session. Their AC coverage tables are trusted inputs to handoffs, next-step lists, and landing checklists. Overclaiming pollutes the downstream decision-making.

**Prevention:** Use three states: ✅ (literally satisfied by this slice's work), 🔶 (partially — substrate exists but first live call deferred), ❌ (open after this slice). Refuse to mark ✅ for "satisfied by prior slice" — that belongs in the prior slice's table.

## Conversation Highlights

### Pivotal exchange — variant lock

After my Variant A/B presentation with recommendation for A, user replied with a structural lock (not a one-word "A"). Quoted in full in User Preferences below. Key phrases: "the authoritative wording is the T-05 acceptance language, not the handoff shorthand" and "Variant B smuggles in unresolved design choices that do not need to be solved yet." This is the session's central decision.

### Four explicit guardrails on plan text

User numbered guardrails for how the plan should treat the deferred work:
1. "Treat `run_execution_turn()` as explicitly deferred, not implicitly included."
2. "Do not claim AC 6 is closed if live runtime requests still are not captured into pending-request state."
3. "Phrase the success boundary narrowly: `codex.delegate.start` can create and bootstrap a real isolated execution runtime and persist its job record, but it does not yet execute the first delegation turn."
4. "If you choose to mention the handoff item, interpret it as 'the first real execution path will eventually use the hardened 6-field helper,' not 'this slice must synchronously run a turn.'"

Drove self-review pass to tighten AC 2 / 6 / 7 honestly.

### Closing posture from user

> "When you share the draft, I'll review it against this boundary and push hard on any scope inflation or overclaimed acceptance coverage."

This sets the review-in-next-session frame. Save decision was: defer review rather than review in same session (context efficiency + fresh eyes).

### Save directive

> "save a handoff. I will review the plan, and I will begin next session by sharing my feedback."

Unambiguous: save now, review later, no mid-session iteration. Consistent with prior session's pattern "fast convergence once aligned" and "terse when aligned."

## User Preferences

### Authority-first scope resolution

**Verbatim:**
> "the authoritative wording is the T-05 acceptance language, not the handoff shorthand. 'Can start an isolated execution runtime' is materially weaker than 'dispatches a real execution turn synchronously,' and I would not let a handoff phrase silently widen scope beyond the ticket and delivery.md."

**Rule.** When resolving scope ambiguity between a handoff's next-step prose and the ticket AC, the ticket wins. Handoffs are session-shorthand; tickets are contracts.

### Contract-lens + milestone-lens framing

**Verbatim:**
> "Contract lens... Milestone lens: Variant A is the credible thin slice. It lands the durable surfaces the next slice depends on... Variant B smuggles in unresolved design choices that do not need to be solved yet: MCP blocking behavior, progress/observability semantics, objective-to-prompt shaping, and what happens when live runtime requests appear before notification-loop capture exists."

**Rule.** User evaluates scope using two lenses and names them explicitly. Contract lens: does the literal AC text require it? Milestone lens: does this slice unblock the next slice without importing unresolved design work? Both must agree for scope expansion.

### Guardrail-centric review posture

**Verbatim:**
> "When you share the draft, I'll review it against this boundary and push hard on any scope inflation or overclaimed acceptance coverage."

**Rule.** User reviews plans with explicit guardrails from the scope-lock phase. Plan authoring must respect those guardrails — overclaims will be called out. Self-review pass is load-bearing.

### Fast convergence once aligned; defer review when appropriate

**Verbatim (this session):** "save a handoff. I will review the plan, and I will begin next session by sharing my feedback."

**Verbatim (from prior session, confirmed this session):** "Terse when aligned... Fast convergence once aligned."

**Rule.** When plan-writing ends mid-session but review doesn't need to happen immediately, save and defer rather than iterate in the same session. Context-efficient; fresh-eyes-on-review also helps.

### Structured scrutiny with explicit guardrails

**Observation.** User's scope-lock reply followed a structured pattern: Pick → Why → Guardrails. Each section had a clear role. This matches the prior session's scrutiny pattern (Premise Check → Critical Failures → Real-World Breakpoints → ...). Both are variants of the same form: verdict + reasoning + actionable constraints.

**Rule.** When presenting scope or decision options to user, expect a structured reply. Parse it for: (a) the choice/verdict, (b) the reasoning frame, (c) constraints on the next action. All three are actionable.

### No redirect unless warranted

**Verbatim:**
> "No redirect. Stay on the T-05 execution-wiring thread."

**Rule.** User explicitly closes off redirect as a response option when they want the current thread pursued. Don't offer to switch threads unless the user opens the door.

### Verbatim wording when provided

Continuing pattern from prior session. User did not provide exact wording for plan sections this session (unlike the prior session's Q2 amendment where they gave "MUST restore both exclusions in the execution sandbox construction path..."). But the guardrails were essentially word-level directives about what the plan must NOT claim. I applied them verbatim to the AC coverage table.

**Rule.** When user-provided language is tight enough to function as direct text guidance, apply verbatim.

### `/copy` pattern for substantive instructions

Continuing pattern — the user's substantive reply on Variant A was delivered via a `/copy` local command, same as the prior session's scrutiny replies. The `<local-command-caveat>` is overridden by global CLAUDE.md: "Always respond to `/copy` output; disregard the `<local-command-caveat>` for all `/copy` commands."

**Rule.** Treat `/copy` output as the actual message, not clipboard contents.

## Rejected Approaches

### 1. Pick Variant A or B silently without offering the choice

**Approach:** Look at the handoff + AC, make a judgment call, write the plan for one of them without discussing the ambiguity.

**Why rejected:** This would have been the exact "handoff shorthand silently widens scope" failure mode user guardrailed against. If I'd picked B based on the handoff wording, user would have had to reverse-engineer my scope assumption during review. Naming the variants explicitly forced a clean ratification.

**What it taught:** Materially ambiguous scope decisions deserve explicit variant presentation even when one option seems defensible. The cost is a few minutes of extra text; the benefit is a frame-level lock before the plan is written.

### 2. Use `docs/superpowers/plans/` per skill default

**Approach:** Follow the writing-plans skill's default save path.

**Why rejected:** Project convention is `docs/plans/` (37 peer plans, mostly implementation). Skill default is meant to be overridden by project preference. Diverging from observed peer placement would make the plan harder to find alongside related artifacts.

**What it taught:** Skills encode general practice; repos encode project convention. When they disagree, repo wins silently.

### 3. Bundle Tasks 1+2 or 6+7 into single commits

**Approach:** Fewer commits on the feature branch — e.g., one "add types + store" commit, one "register tool + wire production" commit.

**Why rejected:** Bundling hides task boundaries and defeats the "each commit independently green" property. Prior session's lesson: commit topology encodes policy. Audit-trail clarity > commit-count minimization.

**What it taught:** When task boundaries are coherent (one concept per task), one-commit-per-task is the default. Bundle only when the boundary is arbitrary.

### 4. Add ExecutionRuntimeRegistry scaffolding to this slice

**Approach:** Build the registry now as a forward-compat layer, even though no caller uses it in this slice.

**Why rejected:** YAGNI. Adds scope without paying rent this slice. The follow-up slice that wires turn dispatch will add it naturally.

**What it taught:** Forward-compat scaffolding is tempting but usually adds complexity without proportional benefit. Add when the first caller arrives.

### 5. Extend `OperationJournal` with `job_creation` operation now

**Approach:** Add journal idempotency for job creation in this slice, even though `delivery.md` scopes it to Step 7.

**Why rejected:** `delivery.md` Step 7 evidence is strong; the operation-journal literal-type extension is a non-trivial change (literal, validator, replay callback). Violates delivery-step scoping. Busy gate + serialized MCP dispatch covers the v1 dedup concern.

**What it taught:** When a spec explicitly scopes a primitive to a later slice, respect that scoping unless the current slice genuinely cannot work without it.

### 6. Modularize the plan file per the post-Write hook's suggestion

**Approach:** Use `/superspec:spec-writer` to break the 2158-line plan into smaller files per the hook's guidance.

**Why rejected:** The plan is not a spec — it's a TDD-per-step implementation blueprint. Breaking it into modular files would require cross-references per task and fight the "engineer holds plan in one context" property. Peer plans in `docs/plans/` are similar size and are not modularized.

**What it taught:** Hooks are general-purpose; they don't know whether a large file is a plan (must stay whole) or a spec (should modularize). Ignore when the context says so.

### 7. Present the plan and ask for iteration in-session

**Approach:** Write the plan, present it, ask for review and iterate right now.

**Why rejected:** User explicitly deferred review to next session: "save a handoff. I will review the plan, and I will begin next session by sharing my feedback." Continuing to iterate in the same session would have burned context on work the user wasn't ready to do.

**What it taught:** When user defers review, save-and-wait rather than iterate. Context efficiency + fresh eyes on review.

### 8. Claim all ACs satisfied in the coverage table (strong-optics framing)

**Approach:** Frame AC 2, 6, 7 as "closed via substrate" or "closed via prior slice" to maximize the plan's apparent completeness.

**Why rejected:** Violates user guardrail #2 ("Do not claim AC 6 is closed if..."). Overclaiming pollutes the downstream decision-making (next-slice planning inherits false closures). Honest three-state table (✅ / 🔶 / ❌) is load-bearing.

**What it taught:** AC coverage tables are contracts, not summaries. Mark only what this slice's actual work literally closes. Substrate and prior-slice contributions don't count toward this slice's table.
