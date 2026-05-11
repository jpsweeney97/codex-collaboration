---
date: 2026-04-22
time: "22:04"
created_at: "2026-04-23T02:04:25Z"
session_id: 7c193a58-d48c-4e8a-84fc-b6cf57e3d9b5
resumed_from: "docs/handoffs/archive/2026-04-22_19-15_t07-7d-context-injection-removed-7e-next.md"
project: claude-code-tool-dev
branch: feature/t07-cross-model-removal-7e
commit: 2255b066
title: "T-07 7e cross-model removed, T-07 closed"
type: handoff
files:
  - packages/plugins/cross-model/ (deleted — 79 files)
  - .github/workflows/cross-model-plugin.yml (deleted)
  - scripts/validate_consultation_contract.py (deleted)
  - tests/test_consultation_contract_sync.py (deleted)
  - tests/test_e_planning_spec_sync.py (deleted)
  - pyproject.toml
  - uv.lock
  - .claude-plugin/marketplace.json
  - .claude/CLAUDE.md
  - .claude/skills/making-recommendations/SKILL.md
  - .claude/skills/making-recommendations/references/codex-delta.md
  - .claude/skills/next-steps/SKILL.md
  - docs/references/README.md
  - docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md
  - docs/plans/2026-04-23-t07-cross-model-removal-7e.md
---

# T-07 7e Cross-Model Removed, T-07 Closed

## Goal

Remove the entire `packages/plugins/cross-model/` package from the repo
as T-07 slice 7e — the final cutover slice in the codex-collaboration
build sequence.

**Trigger:** Predecessor session completed 7d (context-injection removal,
PR #122). All 7e pre-removal gates satisfied: parity matrix (7c), context-
injection removed (7d), live `/delegate` smoke (attempted with deferral).

**Stakes:** Cross-model is a retired plugin whose replacement
(codex-collaboration) has been delivered across T-02 through T-07/7b. The
package remaining in the repo creates false signals: live MCP registration,
workspace member, CI workflow, marketplace entry, test suite, and
validation infrastructure all targeting deleted or retired surfaces.

**Success criteria:** Cross-model package deleted, all operational
references cleaned, codex-collaboration added to marketplace, replacement
surfaces verified, T-07 ticket closed.

**Connection to project arc:** Fourteenth session in the codex-collaboration
build sequence. T-07 has 5 slices (7a-7e); all are now complete. T-07 is
closed. This concludes the T-02 through T-07 arc that built
codex-collaboration as the successor to cross-model.

## Session Narrative

**Phase 0 — Handoff load and orientation (~20 min).** Loaded predecessor
handoff from the 7d session. Read three orientation documents in parallel:
T-07 ticket for 7e scope, 7c migration artifact §5 for verification
checklist, and 7d plan for the "retained until 7e" list. Surveyed the
cross-model package structure (80 tracked files) and ran repo-wide grep
for cross-model references across all file types. Identified 7 external
dependency layers matching the 7d cascade model: workspace metadata, CI
workflow, marketplace, validator script, repo-level tests, CLAUDE.md
entries, and live skill references.

**Phase 1 — Live `/delegate` smoke (~15 min).** The ticket requires a live
delegate smoke before cross-model removal. Ran `codex.delegate.start` with
a narrow file-creation objective. App Server bootstrapped successfully —
runtime ID assigned, job reached `completed` with `promotion_state:
"pending"`, artifact hash computed. However, the sandbox produced no
artifacts (empty diff). Root-cause analysis by the user identified two
codex-collaboration defects: (1) `build_workspace_write_sandbox_policy()`
at `runtime.py:23` sets `includePlatformDefaults: False`, blocking all
shell execution; (2) the approval flow at `delegation_controller.py:718`
cancels `command_approval`/`file_change` requests then starts new turns
with text instructions, creating a cancel-retry loop. Verified both claims
against the code. Recorded as execution-domain deferral (not App Server
unavailability). Discarded the empty delegation.

**Phase 2 — Plan drafting (~15 min).** Created branch
`feature/t07-cross-model-removal-7e` and drafted a 9-group removal plan
with 5 decisions, using the 7-layer dependency model from 7d. Initial
inventory was category-based ("docs/ is historical").

**Phase 3 — Scrutiny round 1 (major revision).** User found 5 issues:
wrong replacement MCP tool names (underscore vs dot), 7c live-state parity
check not executed, inventory boundary under-scoped (missed `.planning/`,
handoff skills, test fixtures), CLAUDE.md scripts table not updated, and
verification too narrow (missing root tests, lint, diff check). Root cause
was category-based inventory instead of exhaustive scan + allowlist.
Resolution: replaced D3 with explicit allowlist, fixed tool names with
source citations, added parity verification section B, expanded
verification to 5 sections (A-E).

**Phase 4 — Scrutiny round 2 (minor revision).** User found 4 issues:
Codex Delta migration ambiguity (one-shot vs multi-turn), missing ticket
closeout, string-based residual scan suppressions, and `docs/archived/`
not in allowlist. Resolution: chose one-shot `codex.consult` for Codex
Delta, added Group 7/8 for ticket closeout, rewrote D1 scan with
path-only exclusions, added `docs/archived/` to D3.

**Phase 5 — Scrutiny round 3 (minor revision).** User found 4 issues:
wrong Codex Delta profile (`code-review` vs `adversarial-challenge`),
residual scan missing `--hidden` flag, ticket closeout after verification,
and marketplace check not source-derived. Resolution: corrected profile,
added `--hidden` with explicit `.git/**` exclusions, moved ticket closeout
before verification, bound marketplace source via `jq -r`.

**Phase 6 — Scrutiny round 4 (minor revision).** User found 2 issues:
`docs/prompts/cross-model-*.md` unclassified, and duplicate Group 8
numbering. Resolution: added prompt artifacts to allowlist, renumbered to
Group 9.

**Phase 7 — Scrutiny round 5 (minor revision).** User found 1 issue:
`docs/superpowers/**` and `docs/references/README.md` unclassified.
Resolution: added `docs/superpowers/**` to allowlist, added Group 7 for
reference index cleanup.

**Phase 8 — Scrutiny round 6 (defensible).** Plan converged. No remaining
findings. User approved for implementation.

**Phase 9 — Implementation (~20 min).** Executed 9 groups: `trash` +
`git add -u` for package deletion, workspace/lock cleanup, CI/marketplace
edits, validator/test deletion, CLAUDE.md updates, live skill reference
updates (including full Codex Delta rewrite), reference index cleanup,
ticket closeout. All verification passed: 881 codex-collaboration tests,
47 root tests, all deletion/parity/reference/residual checks clean. One
surprise: residual scan caught `CLAUDE.md:32` "Cross-model consultation
insights" directory comment — updated to "Codex consultation insights."

**Phase 10 — Commit and PR (~5 min).** Single commit at `2255b066`.
Pushed to `origin/feature/t07-cross-model-removal-7e`. PR #123 created.

## Decisions

### D1: Delete validator and sync tests, don't add skip logic

**Choice:** Delete `scripts/validate_consultation_contract.py`,
`tests/test_consultation_contract_sync.py`, and
`tests/test_e_planning_spec_sync.py` entirely.

**Driver:** These files validate the cross-model consultation contract
against cross-model surfaces. Once the package is gone, they have no
subject.

**Alternatives considered:**
- **Port to validate codex-collaboration contracts** — rejected because
  codex-collaboration uses server-enforced contracts, not Claude-cognitive
  documents.
- **Add skip logic** — rejected because 7d's skip was justified by a
  one-slice liminal state; in 7e the subject is deleted.

**Trade-offs accepted:** Repo loses consultation contract validation
tooling. Accepted because the contract itself is deleted with the package.

**Confidence:** High (E2) — all three files reference cross-model paths
exclusively.

**Reversibility:** High — git history preserves all code.

**Change trigger:** If codex-collaboration develops a Claude-cognitive
contract requiring validation, a new validator would be built from scratch.

### D2: Add codex-collaboration to marketplace in the same change

**Choice:** Replace cross-model entry in `.claude-plugin/marketplace.json`
with `codex-collaboration`.

**Driver:** Removing cross-model without adding codex-collaboration would
leave the turbo-mode marketplace without a Codex integration install path.
User's explicit call: "A: add codex-collaboration to marketplace.json in
7e while removing cross-model."

**Alternatives considered:**
- **Remove only, add later** — rejected because it creates an avoidable
  installability gap.

**Trade-offs accepted:** Couples marketplace promotion with package
removal. Accepted because 7e is explicitly the cutover slice.

**Confidence:** High (E2) — codex-collaboration's `.claude-plugin/`
exists and follows the same plugin structure.

**Reversibility:** High — one-line JSON change.

**Change trigger:** Nothing — this is a delivery, not a risky choice.

### D3: Live `/delegate` smoke recorded as execution-domain deferral

**Choice:** Record the smoke as a deferral with full root-cause evidence
rather than a simple "App Server unavailable" statement.

**Driver:** User's root-cause analysis identified two specific
codex-collaboration defects: sandbox `includePlatformDefaults: False` at
`runtime.py:23` and cancel-then-prompt approval loop at
`delegation_controller.py:718`. User: "I would not carry forward the claim
that this would affect cross-model equally."

**Alternatives considered:**
- **Claim partial pass** — rejected because the pipeline is functional
  but execution is not, and the AC requires the smoke to pass.
- **Retry with simpler objective** — rejected because the root cause is
  structural (sandbox and approval flow), not objective-specific.
- **Block 7e on fixing defects** — rejected because the defects are in
  codex-collaboration's execution domain, independent of cross-model
  removal.

**Trade-offs accepted:** T-07 closes with an explicitly deferred gate.
The deferral is transparent (full root-cause evidence in the plan).

**Confidence:** High (E2) — both defects verified against source code.
User performed the root-cause analysis independently.

**Reversibility:** N/A — the deferral is a documentation choice.

**Change trigger:** When the sandbox and approval defects are fixed, a
follow-up smoke should be run to validate full end-to-end delegation.

### D4: Rewrite Codex Delta from two-phase codex-dialogue to one-shot codex.consult

**Choice:** Collapse the Codex Delta protocol from a two-phase
`codex-dialogue` subagent flow to a single `codex.consult` call with
`profile="adversarial-challenge"`.

**Driver:** codex-collaboration's `codex.consult` is one-shot
(`consult-codex/SKILL.md:11`). The dialogue orchestrator is too
heavyweight for an adversarial check (spawns gatherer agents, bounded
scouting phases). Scrutiny finding: user identified that the plan's D5
used ambiguous "agent or skill" language and mixed tool naming.

**Alternatives considered:**
- **Migrate to `/codex-collaboration:dialogue`** — rejected because
  dialogue spawns gatherers and has multi-phase orchestration, far heavier
  than an adversarial stress-test.
- **Simple name substitution** — rejected by scrutiny because the old
  protocol has a thread-continuation shape that can't be mapped to
  one-shot by search-and-replace alone.

**Trade-offs accepted:** The two-phase reveal loses its separate-message
bias-mitigation property. The single-prompt structure mitigates this
structurally (options first, frontrunner after) but is weaker than
sequential reveal with an independent response in between.

**Confidence:** High (E2) — verified `codex.consult` is one-shot,
verified `adversarial-challenge` profile exists and is semantically
correct for decision stress-testing
(`consultation-profiles.yaml:73`).

**Reversibility:** High — the protocol is in a single reference doc.

**Change trigger:** If codex-collaboration adds a lightweight multi-turn
consultation path (lighter than the full dialogue orchestrator), the
two-phase shape could be restored.

### D5: Exhaustive residual scan + explicit allowlist

**Choice:** Run a case-insensitive repo-wide `rg --hidden` scan for
cross-model references with path-based exclusions only. Every hit
classified as delete, update, or allowlist. No content-based suppressions.

**Driver:** Scrutiny round 1 exposed that category-based exclusion
("docs/ is historical") missed tracked live surfaces (`.planning/`,
plugin-local skills, test fixtures). User: "the plan claims 'all live
operational references' are cleaned, but its scan boundary omits tracked,
non-doc live surfaces."

**Alternatives considered:**
- **Category-based exclusion** — rejected after scrutiny found `.planning/
  codebase/` (7 files, ~40 references) outside the exclusion boundary.
- **Content-based grep suppressions** — rejected after scrutiny round 2
  found they could accidentally suppress unrelated future references.

**Trade-offs accepted:** Path-based allowlist requires manual review of
output after each scan. Accepted because the scan only runs once during
verification.

**Confidence:** High (E2) — every allowlisted path verified by grep;
post-fix residual scan produced exactly 7 expected hits.

**Reversibility:** N/A — verification methodology, not a code decision.

**Change trigger:** N/A.

## Changes

### `packages/plugins/cross-model/` — Deleted (79 files, ~21,113 lines)

| Aspect | Detail |
|--------|--------|
| **What** | Entire cross-model plugin package |
| **Key components** | 4 skills, 4 agents, 3 hooks, 17 scripts, 9 reference docs, 26 test files + 5 fixtures + 1 testdata, config files, README/HANDBOOK/CHANGELOG |
| **Mechanics** | `trash` + `git add -u` |
| **PR** | #123, commit `2255b066` |

### `.github/workflows/cross-model-plugin.yml` — Deleted

CI workflow targeting the deleted package.

### `scripts/validate_consultation_contract.py` — Deleted (392 lines)

Validated cross-model consultation contract against skills/agents/profiles.
Subject deleted with the package.

### `tests/test_consultation_contract_sync.py` — Deleted (531 lines)

Sync tests for the cross-model consultation contract. Subject deleted.

### `tests/test_e_planning_spec_sync.py` — Deleted (95 lines)

Cross-file consistency tests for E-PLANNING. 3 of 8 tests were already
failing on main due to 7d dialogue retirement. Subject deleted.

### `pyproject.toml` + `uv.lock` — Workspace member removed

Removed `packages/plugins/cross-model` from workspace members.
Lock regenerated — removed `cross-model-plugin` package metadata
and exclusive dependencies.

### `.claude-plugin/marketplace.json` — Marketplace cutover

Replaced `cross-model` entry with `codex-collaboration` pointing to
`./packages/plugins/codex-collaboration`.

### `.claude/CLAUDE.md` — Package and scripts tables updated

Removed cross-model and context-injection rows from Packages table.
Removed `validate_consultation_contract.py` from Scripts table.
Updated learnings directory comment from "Cross-model consultation
insights" to "Codex consultation insights."

### `.claude/skills/making-recommendations/SKILL.md` — Header updated

Changed "Codex Delta (cross-model adversarial check)" to
"Codex Delta (codex-collaboration adversarial check)".

### `.claude/skills/making-recommendations/references/codex-delta.md` — Full rewrite

Collapsed two-phase `codex-dialogue` protocol to single `codex.consult`
call with `profile="adversarial-challenge"`. Updated all tool names to
`mcp__plugin_codex-collaboration_codex-collaboration__codex.consult`.
Removed `codex-reply`/`codex-dialogue`/thread continuation references.
Updated availability detection, troubleshooting, and anti-patterns.

### `.claude/skills/next-steps/SKILL.md` — Slash command updated

Changed `/cross-model:dialogue` to `/codex-collaboration:dialogue`.

### `docs/references/README.md` — Stale entries removed

Removed context-injection contract entry (line 50-53, pointed to deleted
file) and cross-model handbook entry (lines 55-58, pointed to nonexistent
file). Retained consultation contract and profiles entries. Updated
consultation contract description to remove cross-model skill/agent
references.

### `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` — T-07 closed

Set `status: closed`. Checked both remaining ACs: cross-model removal
with delegate smoke deferral evidence, context-injection removal citing
PR #122.

## Codebase Knowledge

### Files Read This Session

| File | Why | Key Finding |
|------|-----|-------------|
| T-07 ticket (295 lines) | 7e scope, ACs, pre-removal gates | Two unchecked ACs: cross-model removal (with smoke gate), context-injection removal (already done in 7d) |
| 7c migration artifact (325 lines) | §5 for 7e verification checklist | 7e must execute parity against live state, not just cite matrix |
| 7d plan (266 lines) | Retained-until-7e list, post-7d state | Cross-model is "deprecated shell" — `/dialogue` retired, `/codex`+`/delegate`+`/consultation-stats` still functioning |
| `runtime.py:23-38` | Verify sandbox defect | `includePlatformDefaults: False` with `readableRoots` limited to worktree only |
| `delegation_controller.py:700-720` | Verify approval defect | `_CANCEL_CAPABLE_KINDS = {"command_approval", "file_change"}` → returns `{"decision": "cancel"}` |
| `delegation_controller.py:1743-1754` | Verify resume path | `build_execution_resume_turn_text` starts new turn with text prompt, not a real approval |
| `execution_prompt_builder.py:41-67` | Verify resume prompt shape | "treat the caller decision below as authoritative" — instruction, not a grant |
| `mcp_server.py:20-160` | Get exact MCP tool names | 10 tools registered with dot naming: `codex.consult`, `codex.status`, `codex.dialogue.*`, `codex.delegate.*` |
| `consult-codex/SKILL.md:40` | Verify tool name usage | Uses `mcp__plugin_codex-collaboration_codex-collaboration__codex.consult` |
| `consultation-profiles.yaml:73` | Verify adversarial profile | `adversarial-challenge`: "Challenge assumptions and stress-test decisions" |
| `codex-delta.md` (220 lines) | Understand two-phase protocol | Phase 1 (neutral labels), Phase 2 (frontrunner reveal), both in single `codex-dialogue` consultation |
| `docs/references/README.md` (58 lines) | Check for stale entries | Lines 50-58: context-injection contract path (deleted) and handbook path (nonexistent) |

### Key Cascade Pattern: 6-Round Scrutiny Convergence

The 7e plan went through 6 scrutiny rounds. Issue severity dropped
monotonically: Major → Minor → Minor → Minor → Minor → Defensible. The
13 issues found across rounds would have surfaced as post-commit fixes
without the scrutiny process:

| Round | Issues | Root cause |
|-------|--------|-----------|
| 1 | 5 | Category-based inventory instead of exhaustive scan |
| 2 | 4 | Migration semantics (Codex Delta) + bookkeeping gaps |
| 3 | 4 | Verification command mechanics weaker than prose claims |
| 4 | 2 | Last unclassified residual buckets |
| 5 | 1 | More unclassified residual buckets (`docs/references/`) |
| 6 | 0 | Plan converged |

### Residual Reference Allowlist (Post-Removal)

After cross-model deletion, exactly 7 hits remain in the repo-wide
residual scan. All are in the explicit D3 allowlist:

| File | Reference | Category |
|------|-----------|----------|
| `codex-collaboration/server/secret_taxonomy.py:3` | "Ported from cross-model" | Attribution |
| `codex-collaboration/skills/codex-review/SKILL.md:8,27` | "cross-model code review" / "Do NOT use" guard | Inert guard |
| `codex-collaboration/skills/consult-codex/SKILL.md:19` | "Do NOT port cross-model" | Inert guard |
| `codex-collaboration/skills/delegate/SKILL.md:24` | "Do NOT port cross-model" | Inert guard |
| `handoff/skills/defer/SKILL.md:38` | "cross-model consultations" | Historical signal |
| `tests/test_validate_episode.py:62` | `keywords: [cross-model]` | Test fixture metadata |

## Context

### Mental Model

This session was a **systematic package excision with upfront inventory
enumeration**. Unlike 7d (which discovered dependency layers iteratively
through 4 scrutiny rounds), 7e enumerated all 7 layers before drafting
the plan. The remaining scrutiny rounds focused on inventory completeness
(residual scan boundary) and migration semantics (Codex Delta protocol),
not on discovering new dependency layers.

The key insight from the 7d handoff — "enumerate all 7 layers upfront" —
was applied successfully. The 7-layer model (workspace → MCP → CI →
validation → tests → docs → live skills) held.

### Project State

| Ticket | Status | Key commit |
|--------|--------|------------|
| T-02 | Closed | `d4b4a988` |
| T-03 | Closed | `d4b4a988` |
| T-04 | Closed | demonstrated-not-scored |
| T-05 | Closed | `271f23aa` |
| T-06 | Closed | `85afab6b` |
| **T-07** | **Closed** | **`2255b066`** |

### T-07 Slice Summary

| Slice | Work | Status | PR |
|---|---|---|---|
| 7a | Analytics + DelegationOutcomeRecord + ConsultWorkflow | Merged | #116 |
| 7b | `codex-review` skill | Merged | #117 |
| 7c | Migration docs + parity matrix | Merged | #120 |
| 7d | Context-injection removal | Merged | #122 |
| **7e** | **Cross-model removal + marketplace cutover** | **PR open** | **#123** |

## Learnings

### Exhaustive scan + explicit allowlist is the only credible inventory boundary

**Mechanism:** Category-based exclusion ("docs/ is historical") misses
tracked live surfaces outside the expected categories. The 7e plan's
initial D3 excluded `docs/**` but missed `.planning/codebase/` (7 files,
~40 references), `docs/superpowers/**` (~30 references), `docs/prompts/
cross-model-*.md` (2 files), and `docs/references/README.md` (active
index with stale entries).

**Evidence:** Each scrutiny round found a new unclassified bucket that the
previous round's allowlist missed. Convergence required switching from
category-based to `rg --hidden` repo-wide scan with path-only exclusions.

**Implication:** Future removal operations in this repo should use
exhaustive `rg --hidden` scans from the start, not grep with category-
based exclusions. List expected hits explicitly; any unexpected hit is a
plan defect.

### Live `/delegate` smoke exposed two compounding execution-domain defects

**Mechanism:** (1) `build_workspace_write_sandbox_policy()` at
`runtime.py:23` sets `includePlatformDefaults: False`, preventing the
sandbox from reading platform binaries. All shell commands fail with
exit code -1. (2) The approval flow at `delegation_controller.py:718`
cancels `command_approval`/`file_change` requests, then `decide(approve)`
starts a new turn with a text prompt. The new turn hits the same sandbox
restriction and re-escalates.

**Evidence:** Live smoke job `23347703-673a-419f-b1f5-01ca16cfe1f6`
completed with empty diff after 5 escalation cycles. User verified both
defects against source code independently.

**Implication:** Fixing either alone won't fix delegation. Suggested
remediations: (1) `includePlatformDefaults: True` while keeping worktree-
only file access, (2) redesign `approve` to grant or resume a real
executable path, (3) add regression test that fails when an approved
request re-escalates with the same shape.

### Codex Delta migration requires protocol redesign, not name substitution

**Mechanism:** The old Codex Delta protocol uses `codex-dialogue`'s thread
continuation (`codex`/`codex-reply`) for a two-phase reveal within one
consultation. codex-collaboration's `codex.consult` is one-shot, and
`/codex-collaboration:dialogue` is too heavyweight (spawns gatherers).
Simple name substitution leaves ambiguous invocation instructions.

**Evidence:** Scrutiny round 2 found the plan mixed "agent or skill"
language and three different tool naming conventions.

**Implication:** When migrating protocol documents between systems,
verify that the replacement surface supports the same interaction pattern.
If not, consciously redesign the protocol rather than mapping names.

## Next Steps

### 1. Merge PR #123

**Dependencies:** None — all verification passed, T-07 ticket closed in
the commit.

**What to review:** 93 files changed, 575 additions, 22,925 deletions.
The additions are the 7e plan, ticket closeout text, and live skill
reference updates.

### 2. Fix codex-collaboration delegation sandbox and approval defects

**Dependencies:** Independent of T-07 / PR #123.

**What to fix:**
- `runtime.py:23`: Change `includePlatformDefaults: False` to `True`
  while keeping `excludeSlashTmp` and `excludeTmpdirEnvVar`
- `delegation_controller.py:718`: Redesign approval so it grants or
  resumes a real executable path instead of canceling and prompting
- Add regression test: approved `command_approval`/`file_change` request
  should not re-escalate with the same shape

**Potential obstacles:** `includePlatformDefaults: True` may expose
platform binaries to the delegated agent. Need to verify the worktree-
only write restriction is sufficient security boundary.

### 3. Run full `/delegate` smoke after defect fixes

**Dependencies:** Delegation defect fixes merged.

**What to verify:** Start → poll → promote lifecycle with a real file-
creation objective. Confirm non-empty diff, successful promotion, and
correct post-promote workspace state.

## In Progress

**Clean stopping point.** All 7e work is committed at `2255b066` on
branch `feature/t07-cross-model-removal-7e`. PR #123 is open. No
uncommitted changes, no stale branches, no work in flight.

## Open Questions

### 1. Abandoned cross-session delegation terminal outcomes (inherited)

**Context:** If a delegation job reaches terminal status in a session that
crashes before poll, and the next session has a different session ID, the
terminal outcome may be missing from `analytics/outcomes.jsonl`. The job
store retains the data.

**Decision pending until:** Beyond T-07 scope.

### 2. Delegation sandbox/approval defects — remediation priority

**Context:** Two codex-collaboration defects block full delegation
execution. Not blocking 7e (deferred with evidence), but blocking any
future `/delegate` use that requires real file production.

**Recommendation:** Fix before any user-facing delegation promotion.

### 3-5. Inherited from predecessor handoff chain

Open questions from the predecessor chain (non-store busy sources in
active delegation summary, `git diff --binary` output stability,
`request_user_input` answer construction) remain unchanged.

## Risks

### 1. Delegation defects reduce codex-collaboration's usable surface

The delegation pipeline infrastructure works, but actual execution is
blocked. Until the sandbox and approval defects are fixed, `/delegate`
can only produce empty diffs. This is documented in the T-07 deferral
but limits codex-collaboration's practical capability.

### 2. Codex Delta protocol weaker without two-phase reveal

The rewrite to one-shot `codex.consult` loses the separate-message bias
mitigation. The structural mitigation (options before frontrunner in the
same prompt) is weaker. If adversarial quality degrades, consider
restoring two-phase via a lightweight multi-turn path if one becomes
available.

### 3. Package-wide ruff format pre-existing violations (inherited)

25 files need reformatting in codex-collaboration. Not relevant for 7e
(which only changes reference docs and config, not Python files), but
affects any follow-up Python work in codex-collaboration.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-07 ticket | `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` | AC definitions (now closed) |
| 7e plan | `docs/plans/2026-04-23-t07-cross-model-removal-7e.md` | Implementation plan (committed) |
| 7c migration artifact | `docs/plans/2026-04-22-t07-cross-model-migration-and-parity-7c.md` | Parity matrix, removal inventory |
| 7d plan | `docs/plans/2026-04-22-t07-context-injection-removal-7d.md` | Predecessor plan |
| T-04 retirement decision | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Context-injection authority |

### PRs this session

| PR | Title | Status | Commit |
|----|-------|--------|--------|
| #123 | chore(7e): remove cross-model package and cut marketplace to codex-collaboration | Open | `2255b066` |

### Prior handoffs (chain)

- Immediate predecessor: `docs/handoffs/archive/2026-04-22_19-15_t07-7d-context-injection-removed-7e-next.md`
- T-07 arc: ... → 7d plan + scrutiny + implementation + review + merge →
  **7e smoke + plan + scrutiny (6 rounds) + implementation + PR (this
  handoff)**

## Gotchas

### 1. `rg` regex default masks literal searches (inherited from 7d)

`rg` treats patterns as regex by default. `context.injection` matches any
character for the dots. Use `rg -F` for literal string searches.

### 2. Agent auto-delegation bypasses skill retirement (inherited from 7d)

Claude Code auto-delegates to plugin subagents based on the `description`
field. Retiring a skill does not retire agents it previously launched.

### 3. `rg` without `--hidden` misses `.claude/` and `.claude-plugin/`

The default `rg` scan excludes hidden directories. For residual reference
scans after package removal, use `--hidden` with explicit `.git/**`
exclusion. The 7e plan's D1 scan caught a `.claude/CLAUDE.md:32`
reference that would have been missed without `--hidden`.

### 4. Codex Delta protocol migration is not name substitution

When the underlying tool surface changes interaction patterns (one-shot
vs multi-turn), embedded protocol documents need protocol redesign, not
search-and-replace of tool names. The two-phase Codex Delta protocol
could not map to one-shot `codex.consult` by name substitution alone.

### 5. Pyright stale diagnostics after subagent writes (inherited)

Pyright reports methods as unknown even though they exist and tests pass.
Verify with test execution, not Pyright diagnostics.

### 6. `uv run --package` pytest path resolution (inherited)

Running `uv run --package codex-collaboration pytest tests/test_outcome_record.py`
from repo root fails. Only full paths work.

## User Preferences

### Systematic scrutiny before implementation (continued)

The user performed 6 scrutiny rounds on the plan before approving
implementation. Pattern: user identifies specific falsifiable claims in
the plan and tests them against the repo state. The scrutiny rounds
naturally converge (Major → Minor → Minor → Minor → Minor → Defensible).

### Facts over framing (continued)

User's scrutiny focused on verifiable claims: tool names verified against
source, residual scan boundary tested by running it, profile names checked
against the YAML. The user values specific, verifiable assertions over
architectural narratives.

### Root-cause analysis ownership

User performed the `/delegate` smoke root-cause analysis independently —
reading source code, identifying both defects, and presenting the analysis
for verification rather than asking Claude to diagnose. User: "I ran a
root-cause analysis to diagnose the issue. Please verify or refute my
analysis."

### CI-equivalent verification before merge (continued)

All verification sections (A-E) run before commit. The user expects
merge-readiness to be demonstrated, not asserted.

### Slice boundary discipline (continued)

7e was scoped to cross-model removal only. Codex Delta protocol redesign
was included because the old protocol references dead surfaces, but the
user drew the line at fixing the delegation sandbox/approval defects
(independent remediation, not 7e scope).
