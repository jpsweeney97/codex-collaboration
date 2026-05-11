---
date: 2026-04-22
time: "00:56"
created_at: "2026-04-22T04:56:10Z"
session_id: 4905a29a-4fbe-43b9-8fe2-fb8727bc510c
resumed_from: "docs/handoffs/archive/2026-04-21_23-53_t07-7a-plan-scrutinized-and-committed.md"
project: claude-code-tool-dev
branch: feature/t07-analytics-7a
commit: a4c2c4f4
title: "T-07 7a implementation complete — analytics schema, workflow plumbing, and codex-analytics skill"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/journal.py
  - packages/plugins/codex-collaboration/server/control_plane.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/skills/codex-analytics/SKILL.md
  - packages/plugins/codex-collaboration/tests/test_outcome_record.py
  - packages/plugins/codex-collaboration/tests/test_outcome_shape_consistency.py
  - packages/plugins/codex-collaboration/tests/test_control_plane.py
  - packages/plugins/codex-collaboration/tests/test_mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_journal.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_analytics_skill.py
  - docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md
---

# T-07 7a Implementation Complete

## Goal

Execute the scrutinized 8-task TDD implementation plan for T-07 slice 7a —
analytics schema, workflow plumbing, and the codex-analytics skill for the
codex-collaboration plugin.

**Trigger:** The preceding session completed plan scrutiny (5 rounds, final
verdict "Defensible") and committed the plan at `0e837e5a` on
`feature/t07-analytics-7a`. The handoff prescribed: "Invoke
subagent-driven-development with the plan path. Execute Tasks 1-8 in order."

**Stakes:** Slice 7a owns the shared `workflow` contract that both analytics
(7a) and review (7b) depend on. It also introduces `DelegationOutcomeRecord`
and the terminal outcome emission pipeline that makes delegation analytics
possible. These are structural foundations — downstream slices 7b-7e build
on them.

**Success criteria (all met):**
1. All 8 plan tasks executed with TDD red-green cycles.
2. Each task passes two-stage review (spec compliance + code quality).
3. Full test suite green after each task (845 → 876, 0 regressions).
4. PR created for the slice.

**Connection to project arc:** Eighth session in the codex-collaboration build
sequence. The preceding session scrutinized the plan. This session executes it.
T-07 is the final ticket in the build sequence, with 5 slices (7a-7e). This
session completes 7a. Next: 7b (codex-review skill), then 7c-7e (migration
docs, context-injection removal, cross-model removal).

## Session Narrative

**Phase 0 — Handoff load and setup (~5 min).** Loaded the plan scrutiny
handoff (`2026-04-21_23-53`). Verified baseline: `feature/t07-analytics-7a`
at `0e837e5a`, 845 tests passing. Invoked `subagent-driven-development` skill,
read the full 2027-line plan in 5 chunks (lines 1-200, 200-500, 500-800,
800-1100, 1100-1400, 1400-1700, 1700-2027), and read the three prompt
templates (implementer, spec reviewer, code quality reviewer). Created 8
tasks with dependency tracking and confirmed base SHA.

**Phase 1 — Tasks 1-4: Schema and persistence layer (~40 min).** These were
mechanical tasks — adding types, fields, and journal methods that follow
established patterns. Each was dispatched to a Sonnet implementer subagent
with the full plan task text.

Task 1 (ConsultWorkflow type + workflow on OutcomeRecord) went smoothly — 3
tests, `ee31b1f9`. The spec reviewer noted the implementer used a separate
`TestOutcomeRecordWorkflow` class instead of appending to `TestOutcomeRecord`;
flagged as cosmetic (pytest collects both identically). Code quality reviewer
suggested updating the OutcomeRecord docstring; declined per project comment
policy ("write comments only for key decisions").

Task 2 (workflow threading through MCP → control plane → outcome) was the
first multi-file task. The spec reviewer caught a real issue: the implementer
accidentally deleted a pre-existing assertion (`assert payload["job_id"] ==
"job-rej"` from `test_delegate_discard_returns_discard_policy`). I restored
the assertion and amended the commit (`5031b46e`). This was the single actual
bug caught by the review process across all 8 tasks.

Task 3 (DelegationOutcomeRecord model) added the separate dataclass and
updated the shape consistency test from a flat invariant to a union-aware
`by_type` grouping. The test now writes a delegation terminal record directly
as JSONL (since the journal helper didn't exist yet — Task 4). Both reviews
clean.

Task 4 (journal delegation outcome helpers) added `append_delegation_outcome`
and `append_delegation_outcome_once`. The code quality reviewer noted the
`outcome_type` clause in the idempotency predicate is technically redundant
(only one valid value), but correctly identified it as defensively correct
since `outcomes.jsonl` is a shared file.

**Phase 2 — Tasks 5-6: Emission and recovery (~30 min).** These were the
integration-heavy tasks touching `delegation_controller.py`.

Task 5 (terminal outcome emission) added `_emit_terminal_outcome_if_needed`
and wired it into 3 code paths: `_finalize_turn` non-escalation, `_finalize_turn`
no-captured-request, and `_mark_execution_unknown_and_cleanup`. The plan
warned about UUID consumption shift — but the 10-entry iterator had sufficient
headroom, no tests broke. The code quality reviewer flagged that UUID generation
happens before the idempotency check (wasteful on duplicate calls). I assessed
this as matching the existing `append_dialogue_outcome_once` pattern and not
worth refactoring — in production, `uuid4()` is essentially free.

Task 6 (recovery catch-up) added a sweep at the end of `recover_startup()`.
The critical design choice — `list()` not `list_user_attention_required()` —
was verified by the spec reviewer and specifically exercised by
`test_recover_startup_catches_up_verified_promoted_jobs` (a job with
`promotion_state="verified"` that `list_user_attention_required()` would miss).

**Phase 3 — Tasks 7-8: Presentation layer (~25 min).**

Task 7 (analytics skill + tests) was the capstone. The implementer had to
debug 3 issues: (1) the recipe's inner `bash` block needed a closing triple-
backtick line inside the quadruple-backtick outer fence, (2) escaped backticks
in the fingerprint print needed to be plain backticks, and (3) `allowed-tools`
needed comma-separated format (not YAML list) to match local convention. All
7 fixture tests passed after iteration. The code quality reviewer verified
fixture count math (10 outcomes, 10 audit events) and confirmed the recipe
extraction logic was unambiguous.

Task 8 (ticket amendment) was a direct edit — I did it myself rather than
dispatching a subagent. Appended the deferral note to AC-1 in the T-07
ticket.

**Phase 4 — Finishing (~5 min).** Ran final verification (876 tests, 0
failures), invoked `finishing-a-development-branch`, pushed to remote, and
created PR #116.

## Decisions

### Use subagent-driven-development for plan execution

**Choice:** Dispatched a fresh Sonnet subagent per task with two-stage review
(spec compliance then code quality), rather than executing the plan manually
or using the `executing-plans` parallel-session approach.

**Driver:** The plan was well-specified (8 tasks, each with literal TDD steps),
and all tasks needed sequential execution (dependency chain). Subagent-driven
development keeps the controller's context clean while giving each implementer
exactly the context it needs.

**Alternatives considered:**
- **Manual execution** — would pollute the coordinator context with large
  file reads and test output. Rejected for context efficiency.
- **executing-plans** — requires a parallel session. Rejected because the
  plan was sequential (each task builds on the previous) and the user was
  present.

**Trade-offs accepted:** More agent invocations (24 total: 8 implementers +
8 spec reviewers + 8 code quality reviewers). ~30% overhead for the review
stages. Justified by catching the deleted-assertion bug in Task 2.

**Confidence:** High (E2) — the process completed all 8 tasks with one real
bug caught by review, no regressions, and consistent 845+ test counts.

**Reversibility:** High — purely a workflow choice for this session.

**Change trigger:** If tasks become tightly coupled (requiring mid-task
coordination), manual execution would be more appropriate.

### Accept implementer's allowed-tools format deviation

**Choice:** Used comma-separated `allowed-tools: Bash, Read, mcp__...` in the
SKILL.md instead of the plan's YAML list format.

**Driver:** All 5 existing skills in the codex-collaboration plugin use
comma-separated format. The plan's YAML list format would have broken the
`_parse_allowed_tools` test helper.

**Alternatives considered:**
- **Follow the plan's YAML list format** — would be spec-correct but break
  with local convention and cause test failures.

**Trade-offs accepted:** Minor spec deviation. The deviation is actually a
correction — the plan's template format was inconsistent with the codebase.

**Confidence:** High (E2) — verified all 5 peer skills use comma-separated.

**Reversibility:** High — formatting only.

**Change trigger:** If the plugin framework adds native YAML list support.

### Do not refactor UUID generation to defer past idempotency check

**Choice:** Left UUID generation before the `_jsonl_contains` check in
`_emit_terminal_outcome_if_needed`, accepting that duplicate calls consume
a UUID that's discarded.

**Driver:** The existing `append_dialogue_outcome_once` follows the same
pattern (fully constructed record passed to the once-method). Changing the
journal API to accept a factory callable would break symmetry for negligible
benefit — in production, `uuid4()` is essentially free.

**Alternatives considered:**
- **Defer UUID behind idempotency check** — would require changing
  `append_delegation_outcome_once` to accept a factory callable or exposing
  a `has_delegation_outcome` predicate. Rejected as overengineering.
- **Guard UUID call in the helper** — partial fix that still requires
  reading the JSONL file before constructing the record.

**Trade-offs accepted:** In tests with deterministic UUID iterators, duplicate
calls advance the counter silently. The plan anticipated this ("extend the
iterator if tests fail") and no tests failed.

**Confidence:** High (E2) — matches established pattern, tests pass.

**Reversibility:** High — the journal interface can be extended later.

**Change trigger:** If a future task chains many duplicate emission calls and
exhausts the test iterator.

## Changes

### `server/models.py` — Type definitions (Tasks 1, 2, 3)

| Aspect | Detail |
|--------|--------|
| **What** | Added `ConsultWorkflow = Literal["consult", "review"]`, `DelegationTerminalStatus = Literal["completed", "failed", "unknown"]`, `workflow` field on `OutcomeRecord` (default "consult") and `ConsultRequest` (last field, after `profile`), `DelegationOutcomeRecord` frozen dataclass |
| **Pattern** | Follows existing `DecisionAction` type alias pattern; `DelegationOutcomeRecord` parallels `OutcomeRecord` structure but with delegation-specific fields |
| **Key locations** | `ConsultWorkflow`: line 35, `DelegationTerminalStatus`: line 36, `OutcomeRecord.workflow`: line 221, `ConsultRequest.workflow`: line 94, `DelegationOutcomeRecord`: lines 227-239 |

### `server/control_plane.py` — Advisory runtime (Task 2)

| Aspect | Detail |
|--------|--------|
| **What** | Added `workflow=request.workflow` to `OutcomeRecord` construction in `codex_consult()` |
| **Key location** | Line 241 |
| **Impact** | Every consult outcome now carries the workflow discriminator for analytics slicing |

### `server/mcp_server.py` — MCP tool definitions (Task 2)

| Aspect | Detail |
|--------|--------|
| **What** | Added `workflow` to `codex.consult` input schema (enum, not required) and handler (defaults to "consult") |
| **Key locations** | Schema: lines 43-47, handler: line 401 |

### `server/journal.py` — JSONL persistence (Task 4)

| Aspect | Detail |
|--------|--------|
| **What** | Added `append_delegation_outcome()` and `append_delegation_outcome_once()` |
| **Pattern** | Mirrors existing `append_outcome`/`append_dialogue_outcome_once` pattern exactly |
| **Key locations** | `append_delegation_outcome`: lines 281-285, `append_delegation_outcome_once`: lines 287-300 |
| **Idempotency key** | `(outcome_type, job_id)` via `_jsonl_contains` predicate |

### `server/delegation_controller.py` — Delegation lifecycle (Tasks 5, 6)

| Aspect | Detail |
|--------|--------|
| **What** | Added `_TERMINAL_STATUS_MAP` module-level dict, `_emit_terminal_outcome_if_needed` helper, wired into 3 terminal paths, added recovery catch-up sweep at end of `recover_startup()` |
| **Helper** | Best-effort (try/except, logged warnings), idempotent (delegates to `append_delegation_outcome_once`) |
| **Wire points** | `_finalize_turn` non-escalation (line 1514), `_finalize_turn` no-request (line 1529), `_mark_execution_unknown_and_cleanup` (line 775) |
| **Recovery** | `recover_startup()` lines 2043-2054 — sweeps `self._job_store.list()` (NOT `list_user_attention_required()`) |
| **Key design** | `_TERMINAL_STATUS_MAP.get(job.status)` provides type-safe narrowing without `cast()` |

### `skills/codex-analytics/SKILL.md` — Analytics skill (Task 7)

| Aspect | Detail |
|--------|--------|
| **What** | New skill computing 5 analytics views from outcome + audit JSONL streams |
| **Frontmatter** | `name: codex-analytics`, `user-invocable: true`, `allowed-tools: Bash, Read, codex.status` |
| **Recipe** | Inline Python via `python3 -c "..."`, quadruple-backtick outer fence |
| **Views** | Usage, Reliability/Security, Context/Runtime (with policy fingerprints), Delegation Lifecycle, Review |
| **Known limitations** | Credential blocks/shadows and promotion rejections shown as `unavailable (not emitted to audit stream)` |

### `docs/tickets/...analytics-reviewer-and-cutover.md` — Ticket amendment (Task 8)

| Aspect | Detail |
|--------|--------|
| **What** | Appended deferral note to AC-1 for credential blocks/shadows and promotion rejection metrics |
| **Location** | After line 199 (first acceptance criterion) |

### Test files — 31 new tests across 7 files

| File | Tests Added | Coverage |
|------|-------------|----------|
| `test_outcome_record.py` | +7 | Workflow default/explicit/asdict, ConsultRequest workflow, DelegationOutcomeRecord fields/frozen/roundtrip |
| `test_outcome_shape_consistency.py` | +0 (modified) | Union-aware key-set invariant (group by outcome_type) |
| `test_control_plane.py` | +2 | Workflow threading to outcome record (explicit + default) |
| `test_mcp_server.py` | +2 | MCP schema includes workflow, dispatch passes workflow |
| `test_journal.py` | +4 | Delegation outcome write, once-skip, different-jobs, coexistence |
| `test_delegation_controller.py` | +7 | Terminal emission (completed/failed/unknown/idempotent), recovery catch-up (missing/verified/skip) |
| `test_analytics_skill.py` | +7 | Recipe views: data header, usage, unknown types, reliability, delegation, review, fingerprints |

## Codebase Knowledge

### Analytics Emission Architecture (verified and extended this session)

```
codex.consult MCP request
  → mcp_server._dispatch_tool()
       → arguments.get("workflow", "consult")
       → ConsultRequest(workflow=...)
       → control_plane.codex_consult(request)
            → OutcomeRecord(workflow=request.workflow)
            → journal.append_outcome()                      # analytics/outcomes.jsonl

delegation terminal discovery (poll or recovery)
  → delegation_controller._emit_terminal_outcome_if_needed(job_id)
       → job_store.get(job_id) → _TERMINAL_STATUS_MAP.get(status)
       → DelegationOutcomeRecord(terminal_status=...)
       → journal.append_delegation_outcome_once()           # analytics/outcomes.jsonl (shared)

recover_startup() catch-up
  → for job in job_store.list():                           # NOT list_user_attention_required()
       if status in ("completed", "failed", "unknown"):
            _emit_terminal_outcome_if_needed(job.job_id)
```

### Key File Shapes (verified this session)

| Concept | Location | Shape |
|---------|----------|-------|
| `ConsultWorkflow` | `models.py:35` | `Literal["consult", "review"]` |
| `DelegationTerminalStatus` | `models.py:36` | `Literal["completed", "failed", "unknown"]` |
| `OutcomeRecord.workflow` | `models.py:221` | `ConsultWorkflow = "consult"` (last field) |
| `ConsultRequest.workflow` | `models.py:94` | `ConsultWorkflow = "consult"` (last field, after `profile`) |
| `DelegationOutcomeRecord` | `models.py:227-239` | 9 fields, `outcome_type: Literal["delegation_terminal"]`, `repo_root` optional |
| `_TERMINAL_STATUS_MAP` | `delegation_controller.py:104-108` | Module-level dict for type-safe narrowing |
| `_emit_terminal_outcome_if_needed` | `delegation_controller.py:801-829` | Best-effort, idempotent, 3 wire points |
| `append_delegation_outcome_once` | `journal.py:287-300` | Keyed on `(outcome_type, job_id)` via `_jsonl_contains` |
| Recovery sweep | `delegation_controller.py:2043-2054` | End of `recover_startup()`, uses `list()` |
| Analytics skill | `skills/codex-analytics/SKILL.md` | 5 views, quadruple-backtick recipe |
| MCP workflow schema | `mcp_server.py:43-47` | `enum: ["consult", "review"]`, not required |

### Shape Consistency Test (updated this session)

`tests/test_outcome_shape_consistency.py` — previously asserted all outcome
records share identical keys (`len(set(key_sets)) == 1`). Updated to group by
`outcome_type` and assert consistency within each group. The delegation terminal
record is written directly as JSONL (not via journal helper) since the test
needs to exercise the shape invariant independently of the persistence layer.

### Skill Frontmatter Convention (verified this session)

All 6 user-facing skills in the codex-collaboration plugin now use
`user-invocable: true` and comma-separated `allowed-tools`. The new
`codex-analytics` skill follows this convention exactly.

## Context

### Mental Model

This session was a **plan execution session** using subagent-driven
development. The mental model: an 8-task TDD plan, already scrutinized over 5
rounds, is mechanically correct — the execution job is to dispatch
implementers, verify their output, and handle edge cases. The two-stage review
(spec compliance then code quality) acts as a quality gate, catching one real
bug (Task 2 deleted assertion) and surfacing valid observations (UUID
consumption, docstring gaps, test placement) that were assessed and
appropriately deferred.

### Project State

| Ticket | Status | Tests | Key commit |
|--------|--------|-------|------------|
| T-02 | Closed | 566 | `d4b4a988` |
| T-03 | Closed | 566 | `d4b4a988` |
| T-04 | Closed | 566 | demonstrated-not-scored |
| T-05 | Closed (retroactive) | 698 | `271f23aa` |
| T-06 | Closed | 845 | `85afab6b` |
| T-07 | **Open (7a complete, PR #116 created)** | 876 | `a4c2c4f4` |

### Slice Sequence for T-07 Implementation

| Slice | Work | Status |
|---|---|---|
| **7a** | Analytics skill + `DelegationOutcomeRecord` + `ConsultWorkflow` + workflow plumbing | **COMPLETE — PR #116** |
| 7b | `codex-review` skill consuming `workflow="review"` | Not started (depends on 7a merge) |
| 7c | Migration docs + parity matrix document | Not started (depends on 7a + 7b) |
| 7d | Context-injection removal | Not started (depends on 7c) |
| 7e | Cross-model removal + verification + live delegate smoke | Not started (depends on 7c + 7d) |

## Learnings

### Two-stage review catches implementer collateral damage

**Mechanism:** Implementer subagents edit test files by inserting new tests
near existing code. When the insertion point is adjacent to a test's last
line, the implementer may accidentally delete or modify the existing assertion.
Spec reviewers catch this because they independently read the diff against
the spec requirements.

**Evidence:** Task 2 spec reviewer flagged: "The removed line was
`assert payload["job_id"] == "job-rej"` at the end of
`test_delegate_discard_returns_discard_policy`. This assertion was factually
correct and was checking real behavior."

**Implication:** When dispatching implementers that insert code adjacent to
existing tests, explicitly warn: "Do not modify or remove any pre-existing
assertions."

### Subagent-driven development with Sonnet handles mechanical TDD well

**Mechanism:** For well-specified tasks (exact file paths, literal code
snippets, specific test expectations), Sonnet implementers consistently
followed TDD steps correctly and produced clean commits. The key: the plan
must be literally executable — every command, path, and assertion must be
correct as written.

**Evidence:** 8 tasks, 8 successful implementations, 1 real bug caught by
review (not by the implementer). No task required re-dispatch with a more
capable model or escalation. Full suite green after every task.

**Implication:** For future plan execution, invest in plan scrutiny (the
preceding session's 5 rounds) rather than using more expensive models for
implementation. The plan quality is the bottleneck, not the model capability.

### Recipe quoting discipline is critical for skill embedded code

**Mechanism:** The analytics skill recipe runs inside `python3 -c "..."`.
All Python strings must use single quotes. Backtick escaping (`\``) is
interpreted by Python (not shell) and produces literal backticks in output
because `\`` is not a recognized escape sequence. The outer fence must be
quadruple backticks when inner blocks use triple backticks.

**Evidence:** Task 7 implementer debugged 3 quoting/fencing issues before
all 7 tests passed. The `_read_recipe_from_skill()` test helper extracts
the recipe between `python3 -c "` and `\n```\n`, which only works correctly
with quadruple-backtick outer fencing.

**Implication:** Future skills with embedded code recipes need explicit
quoting constraints in the plan. Test the extraction path, not just the
recipe execution.

## Next Steps

### 1. Merge PR #116 and start slice 7b

**Dependencies:** PR #116 review and merge.

**What to read first:** PR #116 at
`https://github.com/jpsweeney97/claude-code-tool-dev/pull/116`. Then the
T-07 ticket at
`docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md`
(lines 200-203 for the codex-review AC).

**What to do:**
1. Review and merge PR #116 (or wait for CI).
2. Branch from merged main for `feature/t07-review-7b`.
3. Create the `codex-review` skill that gathers diff, calls `codex.consult`
   with `workflow="review"`, and synthesizes findings.

**Approach:** The `workflow="review"` contract is already in place from 7a.
The review skill needs to: (a) gather a diff, (b) construct a
`codex.consult` call with `workflow="review"`, (c) synthesize the Codex
response into a review format. Test with a real diff.

### 2. Implement slices 7c-7e: migration docs, removal, verification

**Dependencies:** 7a + 7b complete.

**What to do:** Write migration docs, formalize parity matrix, remove
context-injection, remove cross-model, run live delegate smoke (or document
deferral).

## In Progress

**Clean stopping point.** All 8 tasks complete. PR #116 created and pushed.
876 tests passing, 0 failures. No code changes in flight.

## Open Questions

### 1. Abandoned cross-session delegation terminal outcomes (inherited)

**Context:** If a delegation job reaches terminal status in a session that
crashes before poll, and the next session has a different session ID, the
terminal outcome may be missing from `analytics/outcomes.jsonl`. The job store
retains the data.

**Decision pending until:** Beyond T-07 scope — documented as a known
limitation in the plan and the analytics skill.

### 2-4. Inherited from predecessor handoff

Open questions #2-4 from the predecessor handoff (non-store busy sources in
active delegation summary, `git diff --binary` output stability,
`request_user_input` answer construction) remain unchanged.

## Risks

### 1. PR review may surface plan-level issues

The plan was scrutinized over 5 rounds, but PR review may identify patterns
or conventions the scrutiny missed. The implementation follows the plan
literally — if the plan has a structural issue, 8 commits carry it.

### 2. UUID consumption shift is latent

The `_emit_terminal_outcome_if_needed` helper consumes a UUID before the
idempotency check. This doesn't cause failures today (the 10-entry test
iterator has headroom), but future tests chaining multiple `start()` calls
could exhaust it. The fix is to extend the iterator — not to refactor the
journal API.

### 3. Live delegate smoke may still be deferred (inherited)

The live delegate smoke requires Codex App Server. If unavailable during 7e,
the removal AC allows explicit deferral (matching T-06's pattern).

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-07 ticket (reconciled) | `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` | Scope and ACs |
| 7a implementation plan | `docs/superpowers/plans/2026-04-21-t07-analytics-7a.md` | Execution blueprint |
| PR #116 | `https://github.com/jpsweeney97/claude-code-tool-dev/pull/116` | Implementation PR |

### Prior handoffs (chain)

- Immediate predecessor: `docs/handoffs/archive/2026-04-21_23-53_t07-7a-plan-scrutinized-and-committed.md`
- T-07 arc: T-06 closure → T-07 scope reconciliation → 7a plan scrutiny → **7a implementation (this handoff)** → 7b implementation

### Commits this session

| Commit | Title | Tests After |
|--------|-------|-------------|
| `ee31b1f9` | feat(7a): add ConsultWorkflow type and workflow field on OutcomeRecord | 848 |
| `5031b46e` | feat(7a): thread ConsultWorkflow through MCP → control plane → outcome | 854 |
| `2850b9a9` | feat(7a): add DelegationOutcomeRecord model for terminal delegation outcomes | 858 |
| `b6e67267` | feat(7a): add delegation outcome journal helpers with append-once idempotency | 862 |
| `f33adb73` | feat(7a): emit DelegationOutcomeRecord on terminal delegation transitions | 866 |
| `0098863b` | feat(7a): add same-session terminal outcome recovery catch-up | 869 |
| `636fb698` | feat(7a): add codex-analytics skill with executable recipe and fixture tests | 876 |
| `a4c2c4f4` | docs(7a): amend AC-1 to defer credential and promotion-rejection analytics | 876 |

## Gotchas

### 1. Pyright stale diagnostics after subagent writes (persistent)

Pyright reports methods as unknown even though they exist and tests pass.
LSP server doesn't get real-time file-change notifications from subprocess
edits. Every task in this session triggered stale Pyright diagnostics. Verify
with test execution, not Pyright diagnostics.

### 2. `allowed-tools` must be comma-separated, not YAML list

The plan's SKILL.md template used YAML list format for `allowed-tools`. All
existing codex-collaboration skills use comma-separated inline format. The
`_parse_allowed_tools` test helper only handles strings, not lists. The
implementer correctly deviated from the plan.

### 3. Implementer subagents may delete adjacent assertions

When inserting new test methods at the end of a test file, implementer
subagents can accidentally delete the last assertion of the preceding test.
The Task 2 implementer removed `assert payload["job_id"] == "job-rej"` from
`test_delegate_discard_returns_discard_policy`. The spec reviewer caught it.

### 4. `uv run --package` pytest path resolution (inherited)

Running `uv run --package codex-collaboration pytest tests/test_outcome_record.py`
from repo root fails with "file or directory not found." Only full paths work:
`packages/plugins/codex-collaboration/tests/test_outcome_record.py`.

## User Preferences

### Autonomous execution with minimal prompts

The user invoked `/load`, confirmed continuation, then invoked
`subagent-driven-development`. From that point, no questions were asked —
all 8 tasks executed with reviews, and the user only re-engaged when asked
which finishing option to choose (option 2: push and PR).

### Structured review before merge (inherited)

User reviews drafts with structured findings. All findings addressed before
declaring work reviewable. Pattern confirmed by the plan scrutiny session
(5 rounds of structured review).
