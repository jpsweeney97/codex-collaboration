---
date: 2026-04-22
time: "19:15"
created_at: "2026-04-22T23:15:00Z"
session_id: 856ad882-e12e-4232-a5dc-d90fc29724e2
resumed_from: "docs/handoffs/archive/2026-04-22_14-15_t07-7b-7c-landed-7d-next.md"
project: claude-code-tool-dev
branch: main
commit: 1f458bcf
title: "T-07 7d context-injection removed, merged — 7e next"
type: handoff
files:
  - packages/plugins/cross-model/context-injection/ (deleted)
  - packages/plugins/cross-model/.mcp.json
  - packages/plugins/cross-model/agents/codex-dialogue.md
  - packages/plugins/cross-model/skills/dialogue/SKILL.md
  - packages/plugins/cross-model/skills/codex/SKILL.md
  - packages/plugins/cross-model/tests/test_credential_parity.py
  - packages/plugins/cross-model/tests/test_mcp_surface_contract.py
  - packages/plugins/cross-model/tests/test_compute_stats.py
  - .github/workflows/cross-model-plugin.yml
  - scripts/validate_consultation_contract.py
  - tests/test_consultation_contract_sync.py
  - pyproject.toml
  - uv.lock
  - docs/plans/2026-04-22-t07-context-injection-removal-7d.md
---

# T-07 7d Context-Injection Removed, Merged — 7e Next

## Goal

Remove the context-injection MCP server package from the cross-model plugin
as T-07 slice 7d, per the T-04 demonstrated-not-scored retirement decision.

**Trigger:** Predecessor session completed 7a-7c (analytics, review skill,
migration docs). Context-injection removal was the next sequential slice with
its dependency (7c parity matrix) satisfied.

**Stakes:** Context-injection is a retired subsystem whose replacement
(codex-collaboration Claude-side scouting) has been live since T-04. Keeping
the dead package creates false signals: live MCP registration, workspace
member, test suite importing deleted-in-spirit code. Removal clears the path
for 7e (full cross-model package removal).

**Success criteria:** Context-injection package deleted, all operational
references cleaned, cross-model tests still passing, no live invocation path
to dead dialogue instructions.

**Connection to project arc:** Thirteenth session in the codex-collaboration
build sequence. T-07 has 5 slices (7a-7e); 7a-7d are now merged. 7e is the
final slice: cross-model removal + verification + live delegate smoke.

## Session Narrative

**Phase 0 — Handoff load and orientation (~15 min).** Loaded predecessor
handoff. Read three orientation documents in parallel: T-07 ticket for 7d
scope, T-04 retirement decision for removal authority, and 7c migration
artifact for the context-injection removal inventory. Initial `rg` search
for cross-model references to context-injection returned zero results —
later discovered this was a regex escaping issue (`rg` treats `.` as regex
wildcard; the actual references contained literal dots). User's ground truth
correction revealed the actual reference set was significantly larger than
the initial scan indicated.

**Phase 1 — Plan drafting (~20 min).** Drafted a 7d removal plan on branch
`feature/t07-context-injection-removal-7d`. Initial plan identified 3
change groups: package deletion, workspace/MCP cleanup, and dialogue
frontmatter cleanup. Plan was underspecified in several ways that the
scrutiny rounds exposed.

**Phase 2 — Scrutiny round 1 (major revision).** User found 5 issues:
wrong `uv --package` selector (`cross-model` vs `cross-model-plugin`),
missing `uv.lock` from change set, unexecutable verification commands,
undefined post-7d dialogue state, and README/HANDBOOK/CHANGELOG grep
self-failure. Root cause was scope ambiguity — the plan didn't decide what
the surviving cross-model package meant after context-injection removal.
Resolution: declared cross-model dialogue **retired** (not manually
rewritten), fixed all verification commands, added lockfile to change set.

**Phase 3 — Scrutiny round 2 (minor revision).** User found the declared
retirement was not operationally enforced — the dialogue skill was still
`user-invocable: true` with an active description. Added `user-invocable:
false` + `disable-model-invocation: true` frontmatter and replaced the skill
body with a retirement stub. Also fixed verification CWD drift and grep exit
semantics.

**Phase 4 — Scrutiny round 3 (major revision).** User found a second launch
path to `codex-dialogue`: the `/codex` skill's Step 2 "Subagent delegation"
branch (lines 116-160) could spawn `cross-model:codex-dialogue` for extended
consultations. Also found that verification check 4 would self-fail on the
unchanged agent body. Resolution: patched `/codex` delegation to redirect to
codex-collaboration `/dialogue`, narrowed check 4 to frontmatter/config only,
added check 5 for launch-path reachability.

**Phase 5 — Scrutiny round 4 (defensible).** Plan converged. No remaining
critical findings. User approved for implementation.

**Phase 6 — Implementation (~30 min).** Executed the 7-group build sequence:
`trash` + `git add -u` for package deletion, workspace/MCP edits, dialogue
skill stub, `/codex` delegation patch, agent frontmatter cleanup, test
cleanup, date-dependent test fix. All 8 verification checks passed. 825
cross-model tests passing.

**Phase 7 — Code review finding 1.** User review found the `codex-dialogue`
agent was still directly invocable via its description field — Claude Code
auto-delegates to plugin subagents based on description. The plan's
"unreachable" claim was false at the subagent layer. Resolution: replaced
the agent with a retirement stub (description says `[RETIRED]`, body stops
with redirect). Also fixed the pre-existing date-dependent test that made
the full suite fail.

**Phase 8 — Code review finding 2 (CI).** User found the GitHub Actions
workflow `cross-model-plugin.yml` still had a "Run Context-Injection Tests"
step targeting the deleted package. Also found the consultation contract
validator and sync test expected governance sections in the now-stubbed
agent. Resolution: removed CI step, added `[RETIRED]` skip logic to
validator and sync test.

**Phase 9 — Final review and merge (~5 min).** User verified all
CI-equivalent gates passed locally. Merged PR #122 at `1f458bcf`.

## Decisions

### D1: Retain `references/context-injection-contract.md` as historical/validation-only until 7e

**Choice:** Keep the context-injection contract file despite the implementation
being deleted.

**Driver:** The consultation contract §15 (line 408) references CI-SEC-1
through CI-SEC-6 by name and points to `context-injection-contract.md`. Two
validation paths check this cross-reference: `test_governance_content.py:28`
and `validate_consultation_contract.py:202`.

**Alternatives considered:**
- **Delete the reference file in 7d** — rejected because it would require
  editing the consultation contract's §15 governance section, which is scope
  creep into a core governance document.

**Trade-offs accepted:** The file contains present-tense governance text for
a system that no longer runs. Retained solely for cross-reference validation.

**Confidence:** High (E2) — verified both validation paths depend on the file.

**Reversibility:** High — file is deleted in 7e with the entire package.

**Change trigger:** 7e removes the entire cross-model package, making this
moot.

**Deviation from 7c:** The 7c migration artifact (line 112) lists this
contract as "Retired with context-injection." That describes the contract's
*authority status*. This plan retains the *file* for validation purposes.

### D2: Retire dialogue skill and agent with stubs, not rewrites

**Choice:** Replace both the dialogue `SKILL.md` and `codex-dialogue.md`
with retirement stubs rather than rewriting to manual-only mode.

**Driver:** The agent's per-turn loop (Steps 2-7, ~300 lines) is deeply
intertwined with `process_turn`/`execute_scout`. The `manual_legacy` fallback
(lines 205-220) was a 15-line path never designed for permanent use. Rewriting
for a one-slice lifespan is wasted effort.

**Alternatives considered:**
- **Rewrite codex-dialogue to manual-only** — rejected because it would
  require removing ~300 lines of server-assisted logic, verifying the manual
  pipeline end-to-end, and testing an unvalidated path, all for a surface
  being deleted in 7e.
- **Leave skill active with frontmatter cleanup only** — rejected after
  scrutiny round 2 revealed the skill was still user-invocable and the agent
  was still auto-delegatable via its description.

**Trade-offs accepted:** Cross-model `/dialogue` is non-functional between
7d and 7e. Accepted because codex-collaboration `/dialogue` (T-04) is the
active replacement.

**Confidence:** High (E2) — verified via Claude Code docs that
`user-invocable: false` hides from `/` menu and
`disable-model-invocation: true` removes from Claude's context entirely.

**Reversibility:** High — the stubs are one slice from deletion.

**Change trigger:** Nothing — 7e deletes the files entirely.

### D3: Patch `/codex` delegation branch to remove launch path

**Choice:** Replace `/codex`'s "Subagent delegation" section (lines 116-160)
with a short redirect to codex-collaboration `/dialogue`.

**Driver:** Scrutiny round 3 discovered that `/codex` could still launch
`cross-model:codex-dialogue` via its Step 2 delegation branch, even after
the dialogue skill was retired. The "unreachable" claim required patching
all consumers.

**Alternatives considered:**
- **Leave the delegation branch** — rejected because it would route users
  into a broken agent with stale context-injection instructions.
- **Remove the delegation branch entirely** — would leave `/codex` with no
  multi-turn guidance. Redirect is better.

**Trade-offs accepted:** `/codex` can no longer delegate to codex-dialogue.
Extended multi-turn consultations must use codex-collaboration `/dialogue`.

**Confidence:** High (E2) — verified no other skills reference
`cross-model:codex-dialogue` after the patch.

**Reversibility:** High — 7e removes `/codex` entirely.

**Change trigger:** 7e makes this moot.

### D4: Fix pre-existing date-dependent test

**Choice:** Replace hardcoded `"2026-03-06T12:00:00Z"` with
`(datetime.now(UTC) - timedelta(days=5)).isoformat()` in
`test_period_filtering_reduces_events`.

**Driver:** The test was a time-bomb — it hardcoded a "recent" timestamp with
a 30-day window, but `compute()` uses `datetime.now(UTC)`. On 2026-04-22,
the event was 47 days old and outside the window.

**Alternatives considered:**
- **Document as pre-existing waiver** — rejected because the plan's
  verification check 1 requires full suite passing.

**Trade-offs accepted:** Minimal scope expansion. The fix is 2 lines.

**Confidence:** High (E2) — verified the failure reproduced on `main` at
the same commit.

**Reversibility:** High — trivial test change.

**Change trigger:** None — the fix is strictly better.

### D5: Skip retired agent in governance validation

**Choice:** The consultation contract validator and sync test skip
`codex-dialogue.md` governance checks when the agent contains `[RETIRED]`.

**Driver:** The agent stub no longer contains the `## Governance` section
that both validation paths expect. Stubbing the agent for retirement (D2)
broke a cascading dependency: the validator script and sync test treated the
agent as a live governance surface.

**Alternatives considered:**
- **Add a `## Governance` section to the stub** — rejected because it
  implies the agent is still governed, contradicting its retired status.
- **Remove the checks entirely** — rejected because other agents
  (`codex-reviewer`, gatherers) still need governance validation.

**Trade-offs accepted:** The `[RETIRED]` sentinel is a convention, not a
contract-level field. If someone removes `[RETIRED]` from the description,
governance checks would re-activate against a stub that doesn't have a
Governance section and would fail.

**Confidence:** High (E2) — verified both validation paths pass with the
skip logic.

**Reversibility:** High — 7e deletes the agent and the checks.

**Change trigger:** 7e makes this moot.

## Changes

### `packages/plugins/cross-model/context-injection/` — Deleted (54 files)

| Aspect | Detail |
|--------|--------|
| **What** | Entire context-injection MCP server package |
| **Lines removed** | ~19,487 |
| **Key components** | MCP server (`server.py`), pipeline (`pipeline.py`), execution (`execute.py`), redaction (`redact.py`, `redact_formats.py`), state management (`state.py`, `checkpoint.py`), entities (`entities.py`), 22 test files |
| **Mechanics** | `trash` + `git add -u` — git history preserves all code |
| **PR** | #122, commit `28d840f0` |

### `packages/plugins/cross-model/skills/dialogue/SKILL.md` — Replaced with retirement stub

| Aspect | Detail |
|--------|--------|
| **What** | 524-line dialogue skill → 17-line retirement stub |
| **Frontmatter** | `user-invocable: false`, `disable-model-invocation: true`, `[RETIRED]` description |
| **Body** | Stop notice redirecting to codex-collaboration `/dialogue` |

### `packages/plugins/cross-model/agents/codex-dialogue.md` — Replaced with retirement stub

| Aspect | Detail |
|--------|--------|
| **What** | 522-line dialogue agent → 17-line retirement stub |
| **Frontmatter** | `[RETIRED]` description, context-injection tools removed from `tools` |
| **Body** | Stop notice redirecting to codex-collaboration `/dialogue` |

### `packages/plugins/cross-model/skills/codex/SKILL.md` — Delegation branch patched

| Aspect | Detail |
|--------|--------|
| **What** | Replaced "Subagent delegation" section (lines 116-160) with redirect to codex-collaboration `/dialogue` |
| **Lines changed** | -45, +6 |
| **Direct invocation path** | Unchanged — `/codex` still works for single-turn consultations |

### `packages/plugins/cross-model/.mcp.json` — Context-injection server removed

| Aspect | Detail |
|--------|--------|
| **What** | Removed `context-injection` MCP server entry; only `codex` server remains |

### `pyproject.toml` (root) + `uv.lock` — Workspace member removed

| Aspect | Detail |
|--------|--------|
| **What** | Removed `packages/plugins/cross-model/context-injection` from workspace members |
| **Lock diff** | Removed `context-injection v0.2.0` and exclusive dependency `pytest-asyncio v1.3.0` |

### `tests/test_mcp_surface_contract.py` — Removed context-injection assertion

| Aspect | Detail |
|--------|--------|
| **What** | Removed `test_context_injection_server_tools_referenced` (lines 80-85) |

### `tests/test_credential_parity.py` — Removed ingress/parity tests

| Aspect | Detail |
|--------|--------|
| **What** | Removed `TestIngressCorpus`, `TestPemParity`, `context_injection.redact` imports |
| **Retained** | `TestEgressCorpus` and `credential_scan` import |

### `tests/test_compute_stats.py` — Fixed date-dependent test

| Aspect | Detail |
|--------|--------|
| **What** | `test_period_filtering_reduces_events`: replaced hardcoded `"2026-03-06"` with `(now - 5 days)` |

### `.github/workflows/cross-model-plugin.yml` — Removed context-injection CI step

| Aspect | Detail |
|--------|--------|
| **What** | Removed "Run Context-Injection Tests" step targeting deleted package |

### `scripts/validate_consultation_contract.py` — Retired agent skip

| Aspect | Detail |
|--------|--------|
| **What** | Skip governance checks when `codex-dialogue.md` contains `[RETIRED]` |

### `tests/test_consultation_contract_sync.py` — Retired agent skip

| Aspect | Detail |
|--------|--------|
| **What** | `pytest.skip()` governance check when agent is `[RETIRED]` |

## Codebase Knowledge

### Files Read This Session

| File | Why | Key Finding |
|------|-----|-------------|
| T-07 ticket (lines 140-268) | 7d scope, ACs | AC: "Context-injection is removed as part of the cross-model cutover" with caveats |
| T-04 ticket (full) | Removal authority | Demonstrated-not-scored retirement; 3 caveats (T-20260416-01, L1/L2/L3, capture sequence) |
| 7c migration artifact (full, 326 lines) | Removal inventory | §2d: context-injection is 7d, cross-model is 7e; §5: deferred gates |
| Cross-model `.mcp.json` | MCP registration | Two servers: `codex` (kept) and `context-injection` (removed) |
| Root `pyproject.toml` | Workspace members | `context-injection` at line 8 as workspace member |
| Cross-model `pyproject.toml` (line 2) | Package name | `cross-model-plugin` (not `cross-model` — caused scrutiny finding) |
| Dialogue `SKILL.md` (524 lines) | Retirement target | `allowed-tools` line 6 and Preconditions lines 16-21 referenced context-injection tools |
| `codex-dialogue.md` (522 lines) | Retirement target | `tools` line 4 and Preconditions lines 16-18 referenced context-injection tools; body had `process_turn` calls at lines 270 and 354 |
| `/codex` `SKILL.md` (lines 100-165) | Launch path | Step 2 "Subagent delegation" section (lines 116-160) spawned `cross-model:codex-dialogue` |
| `test_mcp_surface_contract.py` (lines 60-110) | Test cleanup | `test_context_injection_server_tools_referenced` at lines 80-85 |
| `test_credential_parity.py` (full, 63 lines) | Test cleanup | `TestIngressCorpus` and `TestPemParity` imported `context_injection.redact` |
| `test_governance_content.py` (lines 20-50) | D1 dependency | `test_cross_contract_invariant_refs` at line 28 checks CI-SEC references |
| `validate_consultation_contract.py` (lines 195-355) | D1/D5 dependency | `check_cross_contract_invariant_refs` at line 202; agent governance check at line 335 |
| `test_consultation_contract_sync.py` (lines 230-265) | D5 dependency | `test_codex_dialogue_has_governance_section` at line 244 |
| Claude Code docs (skills frontmatter) | Retirement mechanism | `user-invocable: false` hides from `/` menu; `disable-model-invocation: true` removes from Claude's context |
| `.github/workflows/cross-model-plugin.yml` | CI cleanup | "Run Context-Injection Tests" step at lines 45-47 targeted deleted package |

### Key Cascade Pattern: Package Deletion Surfaces Dependencies in Layers

Removing `context-injection/` revealed operational dependencies in this order:

| Layer | Surface | Discovery |
|-------|---------|-----------|
| 1 | Workspace metadata (`pyproject.toml`, `uv.lock`) | Orientation |
| 2 | MCP registration (`.mcp.json`) | Orientation |
| 3 | Skill/agent frontmatter (`tools`, `allowed-tools`) | Plan drafting |
| 4 | Skill/agent body references (launch paths) | Scrutiny round 3 |
| 5 | Agent auto-delegation (description field) | Code review |
| 6 | CI workflows (`.github/workflows/`) | Post-commit review |
| 7 | Validation scripts + governance tests | CI-equivalent run |

Each layer only became visible after the previous one was resolved. Future
package removals should enumerate all 7 layers upfront.

### Cross-Model Post-7d State

| Surface | Status | Depends on context-injection? |
|---------|--------|-------------------------------|
| `/codex` (consult) | **Functional** | No — direct MCP path |
| `/delegate` | **Functional** | No — delegation controller |
| `/dialogue` | **Retired (stub)** | Was dependent; now redirects |
| `/consultation-stats` | **Functional** | No — reads flat event log |
| `codex-dialogue` agent | **Retired (stub)** | Was dependent; now stops |
| `codex-reviewer` agent | **Functional** | No — direct Codex calls |
| Gatherer agents | **Functional** | No — standard host tools |

## Context

### Mental Model

This session was a **systematic package excision with iterative reachability
analysis**. The core challenge was not the deletion itself (that was
mechanical) but ensuring every operational reference to the deleted package
was accounted for. The scrutiny rounds progressively widened the reference
surface: frontmatter → skill body → launch paths → agent auto-delegation →
CI workflows → governance validation.

The pattern mirrors the 7c migration document's over-smoothing lesson: it's
easy to say "delete the package," but the dependencies fan out across
machine-parsed config, instruction documents, test suites, CI pipelines,
and validation scripts. Each layer has its own coupling mechanism.

### Project State

| Ticket | Status | Key commit |
|--------|--------|------------|
| T-02 | Closed | `d4b4a988` |
| T-03 | Closed | `d4b4a988` |
| T-04 | Closed | demonstrated-not-scored |
| T-05 | Closed | `271f23aa` |
| T-06 | Closed | `85afab6b` |
| T-07 | **Open (7a-7d merged, 7e not started)** | `1f458bcf` |

### Slice Sequence for T-07

| Slice | Work | Status |
|---|---|---|
| **7a** | Analytics + DelegationOutcomeRecord + ConsultWorkflow + plumbing | **MERGED — PR #116, closeout PR #119** |
| **7b** | `codex-review` skill consuming `workflow="review"` | **MERGED — PR #117, closeout PR #118** |
| **7c** | Migration docs + parity matrix | **MERGED — PR #120, closeout PR #121** |
| **7d** | Context-injection removal | **MERGED — PR #122** |
| 7e | Cross-model removal + verification + live delegate smoke | Not started |

## Learnings

### Package deletion surfaces dependencies in 7 layers

**Mechanism:** A deleted package has operational references across workspace
metadata, MCP registrations, skill/agent frontmatter, skill/agent body
text, agent description-based auto-delegation, CI workflows, and validation
scripts. Each layer has a different coupling mechanism and a different
discovery method (grep for imports, grep for tool names, reachability
analysis for launch paths, runtime testing for auto-delegation, CI-equivalent
runs for workflows).

**Evidence:** The 7d plan went through 4 scrutiny rounds, each discovering
a new dependency layer. The initial plan identified 3 change groups; the
final implementation had 10 items across 4 groups plus 2 post-commit fixes.

**Implication:** Future package removals in this repo should enumerate all
7 layers before drafting a plan. A checklist: workspace metadata → MCP
registration → skill/agent frontmatter → skill/agent body (launch paths) →
agent description auto-delegation → CI workflows → validation scripts/tests.

### `rg` regex issues mask search results

**Mechanism:** `rg` (ripgrep) treats search patterns as regex by default.
Searching for `context.injection` matches any character in place of the
dots. The initial orientation search returned zero results for cross-model
references, which was false — `grep` with `--include` found 20+ files.

**Evidence:** `rg -rn 'context.injection' ... | head -20` returned empty
output. `grep -rl 'context.injection' ... --include='*.md' --include='*.py'`
found real references.

**Implication:** For literal string searches in this repo, use `grep` or
`rg -F` (fixed-string mode). The `-F` flag disables regex interpretation.

### Agent retirement requires description-level control, not just skill-level

**Mechanism:** Claude Code auto-delegates to plugin subagents based on the
`description` field in agent frontmatter. Removing all skill launch paths
to an agent does not make it unreachable — the description-based
auto-delegation is an independent reachability path.

**Evidence:** After retiring `/dialogue` and patching `/codex` delegation,
the code review found `codex-dialogue.md` still had an active "Use when..."
description at line 3. Per Claude Code docs: subagents are available by
scoped name and auto-delegated based on description.

**Implication:** Retiring an agent requires stubbing the agent itself (not
just its callers). Skills have `user-invocable` and
`disable-model-invocation` controls; agents do not — the only retirement
mechanism is changing the description to `[RETIRED]` and replacing the body
with a stop instruction.

## Next Steps

### 1. Start 7e: cross-model removal

**Dependencies:** 7d merged (done). Create a fresh branch from `main`.

**What to read first:**
- T-07 ticket for 7e scope and pre-removal gates
- 7c migration artifact §5 for 7e verification checklist
- The 7d plan for the "retained until 7e" list

**What to remove:**
- `packages/plugins/cross-model/` (entire package)
- Root workspace member in `pyproject.toml`
- `uv.lock` regeneration
- `.github/workflows/cross-model-plugin.yml` (entire workflow)
- `scripts/validate_consultation_contract.py` (validates cross-model contract)
- `tests/test_consultation_contract_sync.py` (sync tests for cross-model)
- Any remaining cross-model references in repo docs/scripts

**Pre-removal gates (from 7c §5):**
- Parity matrix verified (7c — done)
- Context-injection removed (7d — done)
- Live `/delegate` smoke passed (or explicit App Server deferral recorded)

**Approach:** This is the final deletion. The cascade pattern from 7d
applies at a larger scale — enumerate all 7 dependency layers for the
entire cross-model package before drafting the plan.

**Potential obstacles:**
- Live `/delegate` smoke requires Codex App Server. If unavailable, must
  document the gap explicitly as in T-06.
- `scripts/validate_consultation_contract.py` validates cross-model-specific
  governance; removing the package removes its subject.
- codex-collaboration may reference cross-model in its own docs/skills.

### 2. After 7e: T-07 closure

**Dependencies:** All 5 ACs checked on the ticket.

## In Progress

**Clean stopping point.** All work is merged. `main` is at `1f458bcf` with
PR #122 landed. No uncommitted changes, no open PRs, no stale branches.
T-07 ticket has 7a-7d ACs effectively complete (7d AC checkbox not yet
formally checked — that's a closeout PR for the next session).

## Open Questions

### 1. Abandoned cross-session delegation terminal outcomes (inherited)

**Context:** If a delegation job reaches terminal status in a session that
crashes before poll, and the next session has a different session ID, the
terminal outcome may be missing from `analytics/outcomes.jsonl`. The job
store retains the data.

**Decision pending until:** Beyond T-07 scope.

### 2. Live `/delegate` smoke availability for 7e

**Context:** The live delegate smoke was deferred from T-06 and placed as
a 7e pre-removal gate. It requires Codex App Server. If unavailable at 7e
time, the gap must be documented explicitly.

**Recommendation:** Attempt the smoke. If App Server is unavailable,
document the deferral as T-06 did and proceed with removal.

### 3-5. Inherited from predecessor handoff chain

Open questions from the predecessor chain (non-store busy sources in active
delegation summary, `git diff --binary` output stability,
`request_user_input` answer construction) remain unchanged.

## Risks

### 1. 7e cascade is larger than 7d

Cross-model has 4 skills, 4 agents, 3 hooks, 17 scripts, 5 contracts, 825
tests. The removal surface is ~10x larger than context-injection. The 7-layer
cascade pattern from 7d applies at scale.

### 2. Package-wide ruff format pre-existing violations (inherited)

25 files need reformatting in codex-collaboration. Not relevant for 7e
(deletion), but could affect any follow-up work.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-07 ticket | `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` | AC definitions |
| 7d plan | `docs/plans/2026-04-22-t07-context-injection-removal-7d.md` | Implementation plan (committed) |
| T-04 retirement decision | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Context-injection adjudication |
| 7c migration artifact | `docs/plans/2026-04-22-t07-cross-model-migration-and-parity-7c.md` | §2d removal inventory, §5 7e gates |
| Capability analysis | `docs/reviews/2026-03-17-cross-model-capability-analysis.md` | Cross-model surface inventory |

### PRs this session

| PR | Title | Status | Merge commit |
|----|-------|--------|-------------|
| #122 | chore(7d): remove context-injection package | Merged | `1f458bcf` |

### Prior handoffs (chain)

- Immediate predecessor: `docs/handoffs/archive/2026-04-22_14-15_t07-7b-7c-landed-7d-next.md`
- T-07 arc: ... → 7b review + merge + 7c draft + scrutiny + merge →
  **7d plan + scrutiny (4 rounds) + implementation + review + CI fix +
  merge (this handoff)** → 7e cross-model removal

## Gotchas

### 1. `rg` regex default masks literal searches

`rg` treats patterns as regex by default. `context.injection` matches any
character for the dots. Use `rg -F` for literal string searches, or `grep`
with `--include` globs.

### 2. Agent auto-delegation bypasses skill retirement

Retiring a skill (`user-invocable: false` + `disable-model-invocation:
true`) does not retire the agents it previously launched. Claude Code
auto-delegates to agents based on their `description` field. The agent
itself must be stubbed.

### 3. CI workflows are operational consumers of deleted packages

`.github/workflows/cross-model-plugin.yml` had a "Run Context-Injection
Tests" step. CI workflow files are easy to miss during package removal
because they live outside the package directory tree.

### 4. Validation scripts cascade from governance documents

The consultation contract → context-injection contract cross-reference chain
(`CI-SEC-*`) means removing context-injection's contract file would break
the validator and sync test. The reference file was retained until 7e per D1.

### 5. Pyright stale diagnostics after subagent writes (persistent, inherited)

Pyright reports methods as unknown even though they exist and tests pass.
Verify with test execution, not Pyright diagnostics.

### 6. `uv run --package` pytest path resolution (inherited)

Running `uv run --package codex-collaboration pytest tests/test_outcome_record.py`
from repo root fails. Only full paths work.

## User Preferences

### Systematic scrutiny before implementation

The user performed 4 scrutiny rounds on the plan before approving
implementation. Each round had a clear verdict (major revision / minor
revision / defensible). The user expects plans to be scrutinized for
completeness, consistency, and executability before any code is written.

### Facts over framing (continued)

The user's scrutiny focused on falsifiable claims: "the agent is
unreachable" was tested against actual repo state and found false. The
user values specific, verifiable assertions over architectural narratives.

### CI-equivalent verification before merge

The user ran all three CI-equivalent gates locally before approving merge:
`validate_consultation_contract.py`, full pytest suite, and sync test.
The user expects merge-readiness to be demonstrated, not asserted.

### Slice boundary discipline (continued)

Each slice gets its own branch from `main` after the predecessor merges.
7d was scoped to context-injection removal only, even when it would have
been convenient to also clean up cross-model references that are 7e scope.
