---
date: 2026-04-21
time: "23:53"
created_at: "2026-04-22T03:53:21Z"
session_id: d5ee359e-8a9a-4efc-9add-9edd07b532cd
resumed_from: "docs/handoffs/archive/2026-04-21_21-44_t07-scope-reconciliation-complete.md"
project: claude-code-tool-dev
branch: feature/t07-analytics-7a
commit: 0e837e5a
title: "T-07 7a plan scrutinized and committed"
type: handoff
files:
  - docs/superpowers/plans/2026-04-21-t07-analytics-7a.md
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/journal.py
  - packages/plugins/codex-collaboration/server/control_plane.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_outcome_shape_consistency.py
  - docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md
---

# T-07 7a Plan Scrutinized and Committed

## Goal

Write and scrutinize a TDD implementation plan for T-07 slice 7a — the
analytics schema, workflow plumbing, and analytics skill that form the first
concrete implementation step of the T-07 cutover ticket.

**Trigger:** The preceding session completed T-07 scope reconciliation (PR #115
merged at `57d89874`). The handoff prescribed: "Implement slice 7a: analytics
skill + schema changes. Dependencies: None — can start immediately." The
`feature/t07-analytics-7a` branch already existed with the plan file as the
sole untracked content.

**Stakes:** Slice 7a owns the shared `workflow` contract that both analytics
(7a) and review (7b) depend on. A defective plan would propagate errors into
all five downstream slices. The plan must be execution-ready for a subagent —
every command, file path, and test assertion must be literally correct.

**Success criteria (all met):**
1. An 8-task TDD plan covering all T-07 7a handoff requirements.
2. Plan passes scrutiny review with "Defensible" verdict.
3. Every command runs from repo root with full package-relative paths.
4. Per-view analytics assertions match T-07 ticket named views.
5. Known gaps (credential blocks, promotion rejections) explicitly deferred via
   ticket amendment task.
6. Plan committed to feature branch.

**Connection to project arc:** Seventh session in the codex-collaboration build
sequence. T-06 delivered the last implementation work. The preceding session
reconciled T-07 scope. This session bridges from "scope is specified" to
"implementation plan is scrutinized and ready for execution." Next: execute the
plan with subagent-driven-development.

## Session Narrative

**Phase 0 — Handoff load (~1 min).** Loaded the T-07 scope reconciliation
handoff (`2026-04-21_21-44`). Clean state: `feature/t07-analytics-7a` branched
from `main` at `57d89874`, 845 tests, plan file untracked.

**Phase 1 — Plan review (~5 min).** Read the full plan file
(`docs/superpowers/plans/2026-04-21-t07-analytics-7a.md`, 1892 lines, 7
tasks). The plan was pre-written — this session's job was scrutiny review and
revision, not authoring from scratch.

**Phase 2 — Round 1 scrutiny (~15 min).** User submitted a structured scrutiny
review with 6 findings: 3 P1, 3 P2. I verified each against the actual
codebase before adjudicating.

Key investigation: P1 #1 claimed pytest commands fail from repo root. I tested
`uv run --package codex-collaboration pytest packages/plugins/codex-collaboration/tests/test_outcome_record.py`
and it resolved correctly via `testpaths = ["tests"]` in `pyproject.toml`. But
the user then provided evidence that the bare `tests/...` form actually fails —
`uv run --package codex-collaboration pytest tests/test_outcome_record.py` →
`ERROR: file or directory not found`. This overrode my initial finding. The
user was right: pytest path resolution is fragile and the plan must use full
paths deterministically.

Remaining findings confirmed via code inspection: `_dispatch_tool` calls
`asdict()` (real dataclass needed, not MagicMock),
`test_outcome_shape_consistency.py` asserts all records share exact same keys
(breaks with `DelegationOutcomeRecord`), fixture count was 10 not 11, and
`user-invocable: true` was missing from the skill frontmatter.

Applied all 6 fixes: replace_all for pytest paths and repeated git-add
patterns, targeted edits for the MagicMock test, shape consistency step, count
correction, and frontmatter addition.

**Phase 3 — Round 2 scrutiny (~10 min).** User found 3 more issues:

1. P1: Task 3's shape-consistency step used `journal.append_delegation_outcome()`
   which doesn't exist until Task 4. Fix: direct JSONL write via `asdict()`.

2. P1: `audit_actions["delegate_start"]` uses double quotes inside the
   `python3 -c "..."` shell string — would terminate the outer string. Fix:
   assign to variable with single quotes, then print the variable.

3. P2: The ticket AC-1 amendment was described in the plan's Known Limitations
   but had no executable task. Fix: added Task 8 with explicit steps to amend
   the T-07 ticket.

**Phase 4 — Round 3 scrutiny (~10 min).** User found 3 more:

1. P1: Nested triple-backtick fences inside the SKILL.md block broke Markdown
   rendering. The outer ` ```markdown ` fence was terminated by the first inner
   ` ``` `. Fix: changed outer fence to quadruple backticks.

2. P2: The "Known Limitations — Requires Ticket AC Deferral" section was inside
   the user-facing skill, leaking governance text that becomes stale after Task
   8 runs. Fix: replaced with runtime-appropriate Known Limitations in the
   skill, moved adjudication prose to a "Plan note" paragraph outside the skill
   block.

3. P3: File structure table was stale — didn't list
   `test_outcome_shape_consistency.py`, `test_analytics_skill.py`, or the
   Task 8 ticket edit. Fix: updated all three file tables.

**Phase 5 — Round 4 scrutiny (~10 min).** User found 2 more:

1. P1: Delegation view omitted escalation count. T-07 ticket line 108 requires
   it. The recipe had `esc_count` in Reliability/Security but not in Delegation
   Lifecycle. Fix: added `| escalations | {esc_count} |` to Delegation, added
   test assertion.

2. P2: Review view relied on Usage section for workflow-source distribution
   instead of showing it explicitly. T-07 ticket line 109 requires workflow
   source in the Review view. Fix: moved `workflow=consult` and
   `workflow=review` rows from Usage to Review. Usage now shows a single
   `reviews` count.

The root cause pattern across rounds 2-4: "metric exists somewhere in the
output" was treated as "view requirement satisfied." The T-07 ticket names
metrics under specific views, and the plan must match those boundaries.

**Phase 6 — Round 5 scrutiny (~5 min).** User found 2 final issues:

1. P2: Per-view tests used global `in output` assertions, which don't prove
   section placement. Fix: added `_extract_section(output, header)` helper,
   updated delegation and review tests to assert against section-scoped text.

2. P3: `ConsultRequest` snippet showed `network_access` after `workflow`, but
   the real dataclass has `network_access` before `profile`. Fix: showed only
   the `profile` → `workflow` insertion with explicit "do NOT move
   `network_access`" prohibition.

**Phase 7 — Final verdict: Defensible.** Two copyediting nits (test count
"5" → "7", "reviews from audit" → "reviews from workflow_counts"). Fixed and
committed at `0e837e5a`.

## Decisions

### Use full package-relative paths for all plan commands

**Choice:** Every pytest and git command uses full paths from repo root:
`packages/plugins/codex-collaboration/tests/...` and
`packages/plugins/codex-collaboration/server/...`.

**Driver:** User provided direct evidence that bare paths fail: "the exact
command from repo root failed: `uv run --package codex-collaboration pytest
tests/test_outcome_record.py` → `ERROR: file or directory not found`."

**Alternatives considered:**
- **Bare paths with a `cd` preamble.** Rejected: user preferred deterministic
  commands that "future agents won't have to infer cwd."
- **Bare paths relying on `testpaths` resolution.** Rejected: I initially
  believed this worked based on a `--co` test, but the user's actual execution
  disproved it.

**Trade-offs accepted:** Commands are more verbose. Lines like
`git add packages/plugins/codex-collaboration/server/models.py
packages/plugins/codex-collaboration/tests/test_outcome_record.py` are long
but unambiguous.

**Confidence:** High (E2) — confirmed by direct execution from repo root.

**Reversibility:** High — path convention is a documentation choice.

**Change trigger:** If the workspace adopts a monorepo tool that normalizes
test paths, bare paths might become safe.

### Section-scoped test assertions for view-specific metrics

**Choice:** Analytics recipe tests use `_extract_section(output, header)` to
slice output by `##` headers, then assert against the section text rather than
the full output.

**Driver:** The last two rounds of scrutiny defects (delegate-start missing from
Delegation, workflow-source missing from Review, escalation missing from
Delegation) were all view-placement bugs. Global `in output` assertions cannot
catch these — a metric in the wrong section passes.

**Alternatives considered:**
- **Global `in output` assertions only.** Rejected: proven insufficient by
  three placement bugs across two scrutiny rounds.
- **Snapshot testing (exact output comparison).** Rejected: too brittle for a
  recipe that may evolve its formatting.

**Trade-offs accepted:** The `_extract_section` helper adds ~5 lines of test
infrastructure. Section extraction is index-based (`output.index(marker)`),
which would raise `ValueError` if a section header is missing — this is
actually desirable as it would surface a recipe regression immediately.

**Confidence:** High (E2) — the helper logic is simple (find `## Header`, take
text until next `## ` or end), and the recipe's section headers are verified by
the `test_data_header_with_paths_and_counts` test.

**Reversibility:** High — changing from section-scoped to global assertions is
trivial.

**Change trigger:** If the recipe output format changes away from `## Header`
sections, the helper needs updating.

### Explicitly defer credential and promotion-rejection metrics

**Choice:** Add Task 8 to amend T-07 ticket AC-1 with an explicit deferral note
for credential blocks/shadows and promotion rejections. The analytics skill
surfaces them as `unavailable (not emitted to audit stream)`.

**Driver:** These two metrics are named in the T-07 ticket's Reliability/security
view (lines 104-105) but are structurally unreachable by the analytics recipe.
Credential interception logs to the operation journal (recovery), not audit.
Promotion rejections return response objects but don't emit audit records.

**Alternatives considered:**
- **Add audit emission for these events as part of 7a.** Rejected: this is new
  instrumentation in the credential interception and promotion precondition
  paths, not analytics skill work. It expands 7a's scope beyond schema/plumbing.
- **Silently omit the metrics.** Rejected: user instructed "I would not silently
  leave them as 'unavailable' while the self-review claims full T-07 coverage."

**Trade-offs accepted:** The analytics skill's Reliability/security view is
incomplete — two named metrics show `unavailable`. This is honest but means 7a
does not fully satisfy AC-1 without the deferral amendment.

**Confidence:** High (E2) — verified by searching for audit emission sites in
`delegation_controller.py` (7 `append_audit_event` call sites, none in
credential interception or promotion precondition paths).

**Reversibility:** High — adding the audit emission later and removing the
`unavailable` labels is additive.

**Change trigger:** When a future enhancement adds audit emission for credential
events and promotion rejections.

### Quadruple-backtick fencing for embedded SKILL.md

**Choice:** The SKILL.md content block in Task 7 uses quadruple backticks
(` ```` `) as the outer fence, allowing inner triple-backtick code blocks to
render correctly.

**Driver:** The skill contains both a code example block and a bash recipe block,
each using triple-backtick fences. With a triple-backtick outer fence, the
first inner fence terminates the outer block, corrupting the rendered Markdown.

**Alternatives considered:**
- **Escape inner fences.** Rejected: non-standard and fragile.
- **Indent inner blocks instead of fencing.** Rejected: loses language-specific
  syntax highlighting needed for the bash recipe.

**Trade-offs accepted:** Quadruple-backtick fencing is less common and may
surprise readers unfamiliar with CommonMark's fence nesting rules.

**Confidence:** High (E2) — verified by counting fence markers: 2 quadruple
(outer pair), 4 triple (2 inner pairs). All balanced.

**Reversibility:** High — purely formatting.

**Change trigger:** None foreseeable.

## Changes

### `docs/superpowers/plans/2026-04-21-t07-analytics-7a.md` — implementation plan

| Aspect | Detail |
|--------|--------|
| **What** | 8-task TDD implementation plan for T-07 slice 7a |
| **Structure** | Task 1: ConsultWorkflow + workflow on OutcomeRecord. Task 2: Thread workflow through MCP → control plane → outcome. Task 3: DelegationOutcomeRecord model + shape consistency update. Task 4: Journal delegation outcome helpers. Task 5: Terminal outcome emission in delegation controller. Task 6: Recovery catch-up. Task 7: Analytics skill with executable recipe. Task 8: Ticket AC-1 amendment. |
| **Key patterns** | TDD red-green per task; all commands from repo root with full paths; section-scoped test assertions; quadruple-backtick fencing for embedded skill |
| **Self-review** | Covers spec coverage table, open questions, type consistency checks, and ticket cross-reference |

## Codebase Knowledge

### Analytics Emission Architecture (verified this session)

```
codex.consult request
  → control_plane.codex_consult()
       → append_audit_event(action="consult")           # audit/events.jsonl
       → append_outcome(OutcomeRecord(type="consult"))   # analytics/outcomes.jsonl

codex.dialogue.reply request
  → dialogue.dispatch_turn()
       → append_dialogue_audit_event_once(action="dialogue_turn")
       → append_dialogue_outcome_once(OutcomeRecord(type="dialogue_turn"))

codex.delegate.start request
  → delegation_controller.start()
       → append_audit_event(action="delegate_start")
       [no OutcomeRecord — terminal outcome emitted later on poll]

delegation terminal discovery (poll or recovery)
  → [T-07 7a will add: append DelegationOutcomeRecord(type="delegation_terminal")]

codex.delegate.promote / discard
  → delegation_controller.promote() / discard()
       → append_audit_event(action="promote" / "discard")
       [disposition is audit-only, not outcome]
```

### Key File Shapes (from handoff, verified against live code)

| Concept | Location | Shape |
|---------|----------|-------|
| `OutcomeRecord` | `models.py:202-219` | `outcome_id`, `timestamp`, `outcome_type: Literal["consult", "dialogue_turn"]`, `collaboration_id`, `runtime_id`, `context_size`, `turn_id`, `turn_sequence`, `policy_fingerprint`, `repo_root` |
| `ConsultRequest` | `models.py:~78-96` | `repo_root`, `objective`, many context fields, `network_access: bool`, `profile: str \| None` (last field — `workflow` goes after it) |
| `ConsultResult` | `models.py` (after ConsultRequest) | `collaboration_id`, `runtime_id`, `position`, `evidence: tuple[ConsultEvidence, ...]`, `uncertainties`, `follow_up_branches`, `context_size` |
| `_dispatch_tool` (codex.consult) | `mcp_server.py:386-398` | Constructs `ConsultRequest`, calls `codex_consult()`, returns `asdict(result)` — **must return real dataclass, not mock** |
| Audit event actions (7 distinct) | `delegation_controller.py`, `dialogue.py`, `control_plane.py` | `consult`, `dialogue_turn`, `delegate_start`, `escalate`, `approve`, `promote`, `discard` |
| Journal path setup | `journal.py:186-196` | Creates `journal/` (recovery), `audit/` (trust boundary), `analytics/` (outcomes) |
| Sandbox policy | `runtime.py:23-38` | 6 fields including `excludeSlashTmp: true`, `excludeTmpdirEnvVar: true` |

### Shape Consistency Test

`tests/test_outcome_shape_consistency.py` — asserts all outcome records share
the exact same key set (line 196: `assert len(set(key_sets)) == 1`). This will
break when `DelegationOutcomeRecord` lands in `outcomes.jsonl`. Task 3 of the
plan updates it to a union-aware invariant: group by `outcome_type`, assert
consistency within each group.

### Skill Frontmatter Convention

All 5 user-facing skills in the codex-collaboration plugin use
`user-invocable: true`: `shakedown-b1`, `dialogue`, `delegate`, `consult-codex`,
`codex-status`. The new `codex-analytics` skill must include it.

### T-07 Ticket Per-View Metrics (from lines 101-109)

| View | Required Metrics |
|------|-----------------|
| Usage | consult, dialogue turns, delegate starts, reviews |
| Reliability/security | credential blocks/shadows, escalation count, promotion rejections |
| Context/runtime | context size, policy fingerprint distribution |
| Delegation | started/completed/failed/unknown, promoted/discarded, escalation count |
| Review | count, workflow source (`"review"` vs `"consult"`) |

The plan's analytics recipe maps to these boundaries with per-view sections and
section-scoped test assertions. Credential blocks/shadows and promotion
rejections are deferred (Task 8).

## Context

### Mental Model

This session was a **plan verification session**, not implementation. The
mental model: a TDD plan for a subagent must be literally executable — every
command, path, assertion, and code snippet must be correct as written. The
scrutiny process treated the plan as code: find bugs, verify against the
codebase, and fix. Five rounds of scrutiny revealed a consistent pattern:
"metric exists somewhere" ≠ "view requirement satisfied." The plan needed
per-view assertions matching the T-07 ticket's named view boundaries.

### Project State

| Ticket | Status | Tests | Key commit |
|--------|--------|-------|------------|
| T-02 | Closed | 566 | `d4b4a988` |
| T-03 | Closed | 566 | `d4b4a988` |
| T-04 | Closed | 566 | demonstrated-not-scored |
| T-05 | Closed (retroactive) | 698 | `271f23aa` |
| T-06 | Closed | 845 | `85afab6b` |
| T-07 | **Open (reconciled, 7a plan committed)** | — | `0e837e5a` |

### Slice Sequence for T-07 Implementation

| Slice | Work | Dependencies |
|---|---|---|
| **7a** | Analytics skill + `DelegationOutcomeRecord` + `ConsultWorkflow` + `workflow` plumbing | None — **plan committed, ready for execution** |
| 7b | `codex-review` skill consuming `workflow="review"` | 7a (shared workflow contract) |
| 7c | Migration docs + parity matrix document | 7a + 7b |
| 7d | Context-injection removal | 7c |
| 7e | Cross-model removal + verification + live delegate smoke | 7c + 7d |

## Learnings

### Plan scrutiny reveals a consistent class of defect: view-placement ambiguity

**Mechanism:** When a plan says "print metric X in the output" and tests assert
`"| X | N |" in output`, the metric can appear in any section and the test
passes. But when the ticket specifies metrics under named views, the assertion
must prove the metric is in the correct view.

**Evidence:** Three rounds of scrutiny (2, 4, and 5) found placement bugs:
delegate-start missing from Delegation and Usage (round 2), escalation count
missing from Delegation (round 4), workflow-source in Usage instead of Review
(round 4), and global assertions not proving placement (round 5). All were the
same class.

**Implication:** For analytics/dashboard plans, test assertions should be
section-scoped from the start. The `_extract_section` pattern (extract text
between `## Header` markers, assert within) is a reusable recipe.

### Nested Markdown fences require quadruple-backtick outer wrapping

**Mechanism:** CommonMark's fence nesting rule: a code fence closes only when a
line has the same or more backticks as the opening fence. Triple-backtick inner
blocks inside a quadruple-backtick outer block are treated as literal content.

**Evidence:** Task 7's SKILL.md contained two inner triple-backtick blocks (an
example snippet and a bash recipe). With a triple-backtick outer fence, the
first inner close marker terminated the outer block, corrupting all subsequent
plan content when rendered.

**Implication:** Any plan embedding a skill or Markdown file that contains code
blocks must use quadruple-backtick outer fencing.

### Shell quoting inside `python3 -c "..."` prohibits double-quoted dict access

**Mechanism:** The `python3 -c "..."` wrapper means all Python code inside must
avoid double quotes. Dict access like `d["key"]` terminates the shell string.
The variable-assignment pattern (`count = d['key']` then `f'{count}'`) avoids
both shell escaping and f-string quoting issues.

**Evidence:** Round 2 scrutiny caught `audit_actions["delegate_start"]` inside
the recipe. The executable test runs `python3 -c` directly (via
`subprocess.run`) so it would not catch the shell quoting failure — the real
skill invocation through Bash would fail silently.

**Implication:** Recipe code inside `python3 -c "..."` should use single quotes
exclusively for string literals. For f-string dict access, always assign to a
variable first.

## Next Steps

### 1. Execute the 7a plan with subagent-driven-development

**Dependencies:** None — plan is committed and ready.

**What to read first:** The plan at
`docs/superpowers/plans/2026-04-21-t07-analytics-7a.md`. Then the T-07 ticket
at `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md`
(lines 85-165 for design reconciliation context).

**What to do:**
1. Invoke `superpowers:subagent-driven-development` or
   `superpowers:executing-plans` with the plan path.
2. Execute Tasks 1-8 in order (TDD red-green cycle per task).
3. Run full test suite after each task (expected: 845+ passing, 0 failed).
4. Commit per-task as specified in the plan.

**Approach:** The plan has explicit test-first steps with expected failure
messages and exact file paths. Follow literally — the scrutiny process ensured
commands are correct from repo root.

### 2. Implement slice 7b: codex-review skill

**Dependencies:** 7a must be complete (shared `workflow` contract).

**What to do:** Create `codex-review` skill that gathers diff, calls
`codex.consult` with `workflow="review"`, synthesizes findings. Test with a
real diff.

### 3. Implement slices 7c-7e: migration docs, removal, verification

**Dependencies:** 7a + 7b complete.

**What to do:** Write migration docs, formalize parity matrix, remove
context-injection, remove cross-model, run live delegate smoke (or document
deferral).

## In Progress

**Clean stopping point.** The 7a plan is scrutinized and committed at
`0e837e5a`. No code changes in flight. No implementation started — the plan is
the deliverable of this session. Next session starts execution.

## Open Questions

### 1. Abandoned cross-session delegation terminal outcomes (inherited)

**Context:** If a delegation job reaches terminal status in a session that
crashes before poll, and the next session has a different session ID, the
terminal outcome may be missing from `analytics/outcomes.jsonl`. The job store
retains the data.

**Decision pending until:** T-07 7a implementation — documented as a known
limitation. A broader stale-session analytics sweep would be a separate design
choice.

### 2-4. Inherited from predecessor handoff

Open questions #2-4 from the predecessor handoff (non-store busy sources in
active delegation summary, `git diff --binary` output stability,
`request_user_input` answer construction) remain unchanged. See predecessor
handoff for details.

## Risks

### 1. Plan may require adjustment during execution

The plan was scrutinized against the codebase as of `0e837e5a`, but execution
involves modifying files across 8 tasks. Later tasks may encounter unexpected
interactions with earlier changes — especially Task 5 (wiring terminal emission
into 3 code paths in `delegation_controller.py`) and Task 6 (recovery catch-up
in `recover_startup()`). The plan includes explicit test suites after each task
to catch regressions, but some adjustment may be needed.

### 2. UUID consumption shift in delegation controller tests

Task 5 adds `_emit_terminal_outcome_if_needed` which calls
`self._uuid_factory()` for `outcome_id`. This consumes one additional UUID per
terminal `start()` call. Existing tests with tight UUID iterator assertions may
break after Task 5. The plan notes this and says to extend the iterator, but
the specific tests affected are not enumerated — the executor must check after
the full suite run.

### 3. Live delegate smoke may still be deferred (inherited)

The live delegate smoke requires Codex App Server. If unavailable during 7e,
the removal AC allows explicit deferral (matching T-06's pattern), but this
means cross-model removal happens without end-to-end product verification.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-07 ticket (reconciled) | `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` | Scope and ACs |
| 7a implementation plan | `docs/superpowers/plans/2026-04-21-t07-analytics-7a.md` | Execution blueprint |
| Analytics/review decision | `docs/superpowers/specs/codex-collaboration/decisions.md` | Architecture decision |
| Delivery spec | `docs/superpowers/specs/codex-collaboration/delivery.md` | Build sequence |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Tool surface, response shapes |
| Recovery and journal | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Two-log architecture |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-21_21-44_t07-scope-reconciliation-complete.md`
- T-07 arc: T-06 closure → T-07 scope reconciliation → **7a plan scrutiny (this handoff)** → 7a implementation

### Commits this session

| Commit | Title |
|--------|-------|
| `0e837e5a` | docs(7a): add scrutinized implementation plan for analytics schema and workflow plumbing |

## Gotchas

### 1. `uv run --package` pytest path resolution is not deterministic

Despite `testpaths = ["tests"]` in the package's `pyproject.toml`, running
`uv run --package codex-collaboration pytest tests/test_outcome_record.py` from
repo root fails with "file or directory not found." Only the full path works:
`uv run --package codex-collaboration pytest packages/plugins/codex-collaboration/tests/test_outcome_record.py`.

**Discovered when:** I initially believed bare paths worked based on a `--co`
(collect-only) test, but the user provided direct execution evidence of failure.

### 2. `_dispatch_tool` calls `asdict()` — return values must be real dataclasses

`mcp_server.py:398` calls `asdict(result)` on the return value of
`codex_consult()`. A `MagicMock` will raise `TypeError` because `asdict()`
requires a dataclass instance. Tests that mock the control plane must return a
real `ConsultResult` dataclass.

**Discovered when:** Round 1 scrutiny identified this. Verified by reading
`mcp_server.py:386-398`.

### 3. Pyright stale diagnostics after subagent writes (inherited)

Pyright reports methods as unknown even though they exist and tests pass. LSP
server doesn't get real-time file-change notifications from subprocess edits.
Verify with test execution, not Pyright diagnostics.

### 4. `rg` misses dict-literal field names (inherited)

`rg "excludeSlashTmp"` returns no results for Python dict-literal string keys.
Use exact string search: `rg '"excludeSlashTmp"'`.

## User Preferences

### Plan must be literally executable from repo root

User: "I would make the plan deterministic instead of depending on `uv`/pytest
cwd behavior. Pick one convention and apply it everywhere."

User: "all commands run from repo root, so use full package paths in both pytest
and git commands... That is more verbose, but future agents won't have to infer
cwd."

### Explicit deferral over silent gap

User: "I would add one extra plan fix: the 'credential blocks/shadows' and
'promotion rejections' treatment needs an explicit adjudication... I would not
silently leave them as 'unavailable' while the self-review claims full T-07
coverage."

### Executable ticket amendments, not governance prose

User: "The plan now correctly says credential blocks/shadows and promotion
rejections are not satisfied... But the plan has no task, file entry, test, or
commit step for editing the T-07 ticket. An executor can finish every checkbox
and still fail the plan's own close condition."

### Structured review before merge (inherited)

User reviews drafts with structured findings (priority, confidence, file
locations, specific fix instructions). All findings addressed before declaring
work reviewable. Pattern: thorough review pass before merge.

### Design reconciliation before coding (inherited)

User explicitly prescribes reconciliation sessions before implementation when
scope may have drifted across a multi-ticket build sequence.
