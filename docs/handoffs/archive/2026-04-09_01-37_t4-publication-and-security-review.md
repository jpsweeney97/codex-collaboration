---
date: 2026-04-09
time: "01:37"
created_at: "2026-04-09T05:37:31Z"
session_id: adcdcdc2-2784-4187-a547-6cea9ea45181
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev-t8-impl/docs/handoffs/archive/2026-04-08_22-28_t4-live-smoke-complete-and-naming-convention.md
project: claude-code-tool-dev
branch: feature/t4-containment-publish
commit: e075b75f
title: T4 publication — branch split, security review, PRs 99 and 100 merged
type: handoff
files:
  - packages/plugins/codex-collaboration/scripts/containment_guard.py
  - packages/plugins/codex-collaboration/scripts/containment_lifecycle.py
  - packages/plugins/codex-collaboration/server/containment.py
  - packages/plugins/codex-collaboration/tests/test_containment_guard.py
  - packages/plugins/codex-collaboration/tests/test_containment_lifecycle.py
  - docs/plans/2026-04-08-t4-live-smoke-run-plan.md
  - docs/plans/t8-t4-live-smoke-log.md
  - docs/plans/2026-04-07-t8-minimum-runnable-shakedown-packet.md
  - docs/plans/2026-04-08-t8-shakedown-execution-plan-v3.md
  - docs/plans/2026-04-08-t8-execution-plan-v3-scrutiny.md
  - docs/plans/2026-04-07-t7-executable-slice-definition.md
---

# Handoff: T4 publication — branch split, security review, PRs 99 and 100 merged

## Goal

Publish the completed T4 containment work to `origin/main` via clean, reviewable PRs.
The prior session closed B3 (Containment + Live Coverage) with 13 live pass + 1
synthetic-covered across 14 smoke scenarios, but the work sat on a 25-commit feature
branch (`feature/t8-shakedown-implementation`) that also contained 12 unpublished
shared commits, handoff archives, and T3 ordering scaffolding. The branch was not
publishable as-is.

**Trigger:** The prior handoff identified this as the first next step: "Merge
documentation branches when ready." The user's recommendation was to not publish the
feature branch directly to `main`.

**Stakes:** Without publication, the T4 closure evidence exists only on a local feature
branch and a worktree. B4 (Agent + Skill + Harness Assembly) is next in the build
sequence and benefits from having T4's containment code on `main` as a stable base.

**Success criteria:**
- T4 containment code and evidence on `origin/main` via reviewable PRs
- No handoff artifacts, session-state files, or unrelated T3 scaffolding in the PRs
- V3 execution plan context published so T4 evidence references resolve for reviewers
- Clean commit history (no squash-merge noise, no 25-commit dumps)

**Connection to project arc:** At the design-program level, D8 (Minimum Runnable
Shakedown). At the runtime-delivery level, B3 is now closed and published, B4 is next.

## Session Narrative

### Phase 1: Publication strategy decision

Loaded the prior handoff (`2026-04-08_22-28_t4-live-smoke-complete-and-naming-
convention.md`). The user opened with a recommendation: do not publish
`feature/t8-shakedown-implementation` directly to `main`. The diagnosis was correct —
the branch was 25 commits ahead of `origin/main` with 26 files and 7555 insertions,
including 12 shared unpublished commits, handoff archives, and T3 scaffolding.

The user proposed cherry-picking 4 T4 commits (`9c660006`, `3ccf9183`, `b5b104aa`,
`9f7b5884`) onto a clean branch from `origin/main`. I pushed back on a dependency
claim — asserting that the T4 commits depended on T3 because the `codex-collaboration`
package was "new" against `origin/main`. This was wrong. The user corrected me: the
package already exists on `origin/main`, and they had empirically verified the
cherry-pick in a disposable clone (47/47 tests passing).

This was the key correction of the session. My error was reasoning from branch ancestry
instead of testing the actual cherry-pick. The user's empirical verification
invalidated the dependency claim.

After the correction, I identified three remaining gaps:
1. T3 is orphaned without a publication story
2. T4 evidence docs reference V3 execution plan files not on `origin/main`
3. `b5b104aa` carries a `.session-state/.gitignore` that isn't part of T4

The user ran a full decision analysis (5 options, sensitivity analysis, information
gaps) and recommended Option A: publish a V3 docs-coherence PR first, then the
reconstructed T4 PR, with `.gitignore` peeled and T3 intentionally deferred. Two open
questions held the recommendation at "best available" rather than "verifiably best":
whether T3 should be deferred (yes — diagnostic scaffolding whose value was consumed by
T4) and whether two PRs were worth it (yes — V3 docs PR is cheap and improves reference
coherence). Both resolved in Option A's favor, upgrading the recommendation to
"verifiably best."

### Phase 2: Branch preparation and verification

The user manually prepared both publication branches:
- `chore/t8-v3-execution-plan-publish` in the main repo (4 commits, 4 files, 987
  insertions)
- `feature/t4-containment-publish` in the worktree (4 commits, 12 files, 3237
  insertions)

I verified both branches: commit chains, file sets, exclusions (no handoffs, no
`.session-state/.gitignore`, no T3 artifacts), and the hooks.json diff (additive
containment hooks only).

### Phase 3: PR #99 — V3 docs review and merge

The user pushed `chore/t8-v3-execution-plan-publish` and opened PR #99. I ran two
review agents in parallel (code-reviewer, comment-analyzer). The review found one
actionable issue: the behavior count "6 behaviors" had not been propagated to "7
behaviors" in 3 of 4 locations in `2026-04-07-t8-minimum-runnable-shakedown-packet.md`,
despite a commit specifically intended to fix this count. Also found a phantom "T7 Scope
Directory Derivation amendment" reference (3 occurrences) pointing to a T7 section that
doesn't exist.

The user fixed both issues in commit `187dadf9`, pushed, and merged PR #99.

### Phase 4: PR #100 — T4 full review and security hardening

The user rebased `feature/t4-containment-publish` onto updated `main` (post-#99
merge), force-pushed with `--force-with-lease`, and opened PR #100. I ran 5 review
agents in parallel: code-reviewer, comment-analyzer, test-analyzer, silent-failure-
hunter, and type-design-analyzer.

The review produced a critical finding — a containment escape chain through three
interacting weaknesses:

1. `_enforce_active_scope` raised `ValueError` for invalid scope structure (e.g.,
   `file_anchors: 42`) instead of returning a deny
2. The top-level handler caught the exception and called `_payload_requires_fail_closed`
3. `_payload_requires_fail_closed` used non-strict state readers and could itself raise,
   causing the handler to exit with code 1 → PreToolUse treats non-2 as passthrough →
   containment bypassed

The test analyzer independently confirmed that `_payload_requires_fail_closed` had zero
test coverage across its 6 branches (criticality 10/10). Additional findings: Grep/Glob
out-of-scope deny paths had no telemetry and no tests, the guard and lifecycle had no
stderr logging for deployment misconfiguration (missing `CLAUDE_PLUGIN_DATA`, malformed
stdin), and `_try_append_branch_telemetry` swallowed all exceptions with no logging.

The user fixed the critical escape chain and the high-priority observability gaps in
commit `e075b75f`, adding 10 new tests (47 → 57). The fix changed `_enforce_active_scope`
to return `_deny()` instead of raising, wrapped `_payload_requires_fail_closed` in its
own try/except defaulting to `True`, switched the probe to strict state readers, and
added stderr logging throughout.

PR #100 merged to `main`.

## Decisions

### Decision 1: Publication strategy — Option A (V3 docs PR first, then T4 PR)

**Choice:** Publish two sequential PRs: V3 execution plan docs first, then
reconstructed T4 containment packet. T3 deferred, `.session-state/.gitignore` excluded.

**Driver:** The user diagnosed that the 25-commit feature branch was not publishable
as-is due to scope (handoffs, T3 scaffolding, shared unpublished commits). The user's
empirical cherry-pick test (47/47 passing on `origin/main`) proved the T4 packet was
self-contained.

**Alternatives considered:**
- **Option B (T4 PR only, no V3 docs)** — technically valid (user verified) but weaker
  reviewer story. T4 evidence docs reference V3 gate definitions that wouldn't exist on
  `origin/main`.
- **Option C (V3 docs → T3 → T4 stacked PRs)** — cleanest historical sequencing but
  highest overhead. T3 is diagnostic scaffolding, not a standalone deliverable.
- **Option D (combined T3+T4 PR)** — recreates the scope problem.
- **Option E (do nothing)** — defers the same hygiene problems into B4.

**Trade-offs accepted:** Two PRs instead of one. T3 remains on the feature branch and
will merge with B4 later, creating a trivial `hooks.json` merge conflict (additive
entries in different sections). The V3 docs PR is pure ceremony for reviewer context —
T4 is technically self-contained without it.

**Confidence:** High (E2) — user verified the T4 cherry-pick empirically, both branches
were independently verified before push.

**Reversibility:** High — PRs are on `main`, but the branch history is preserved and
squash-merge was not used.

**What would change this decision:** If the team later decides T3 ordering artifacts
need their own review record, Option C would have been better. If reviewers never
reference the V3 docs, Option B would have been sufficient.

### Decision 2: Fix containment escape chain before merge

**Choice:** Fix the critical escape path (invalid scope → `ValueError` → fail-closed
probe fails → passthrough) and add regression tests before merging PR #100.

**Driver:** The silent-failure-hunter identified a concrete attack chain where corrupted
scope files could cause the guard to pass through instead of deny. The test analyzer
confirmed the fail-closed probe had zero test coverage. In a containment system,
passthrough = agent escapes scope.

**Alternatives considered:**
- **Merge as-is, fix later** — rejected. The escape path is in security-critical code
  that determines whether a shakedown agent can access files outside its scope. Merging
  with a known escape vector undermines the T4 closure claim.
- **Partial fix (just the raise → deny change)** — insufficient. The fail-closed probe
  could still crash and cause passthrough through a different path.

**Trade-offs accepted:** Extra commit on the PR (5 commits instead of 4). The fix
commit adds 402 insertions across 7 files, expanding the review surface. Accepted
because correctness of the containment guard is the primary value proposition.

**Confidence:** High (E2) — the escape path was confirmed by code analysis from the
silent-failure-hunter, and the fix was verified by 10 new passing tests.

**Reversibility:** Low — this is a correctness fix, not a preference. Reverting would
reintroduce the escape path.

**What would change this decision:** Nothing — this corrects a security defect.

### Decision 3: Defer T3 ordering artifacts

**Choice:** T3's 4 commits (`7a7d0855` through `1a6351f9`) remain on
`feature/t8-shakedown-implementation` and will merge with B4 work later.

**Driver:** T3 is diagnostic scaffolding — it proved hook execution ordering, which
informed T4's design (the SubagentStart synchronicity discovery). Its value was consumed
by T4's design decisions. Publishing it as a standalone PR would over-formalize
temporary artifacts.

**Alternatives considered:**
- **Standalone T3 PR** — highest ceremony, lowest value. The ordering artifacts are not
  a product increment that benefits from standalone review.
- **Include T3 in the T4 PR** — recreates the scope problem (ordering test files mixed
  with containment code).

**Trade-offs accepted:** T3 rides along when B4 eventually merges to `main`. This
creates a trivial `hooks.json` merge conflict (T4 added containment hooks to
`origin/main`, T3 adds ordering hooks on the feature branch — both additive, different
sections). If B4 restructures hook registration, T3's entries may be reworked anyway.

**Confidence:** High (E1) — T3's role as scaffolding is clear from its commit messages
and file set (ordering test scripts, result collectors).

**Reversibility:** High — T3 can be published as its own PR at any time if needed.

**What would change this decision:** If T3's ordering artifacts are needed as evidence
for a separate gate, or if B4 restructures hooks in a way that makes T3's additions
incoherent.

## Changes

### PR #99 — `docs(plans): publish T8 execution plan v3 packet`

**Purpose:** Establish V3 gate vocabulary on `origin/main` so T4 evidence references
resolve for reviewers.

**Commits (5):**

| Commit | File(s) | Purpose |
|--------|---------|---------|
| `8ef8f5ce` | `2026-04-08-t8-shakedown-execution-plan-v3.md` | V3 execution plan — delivery sequence, gate logic, emission contract |
| `27cbd8ac` | `2026-04-07-t8-minimum-runnable-shakedown-packet.md`, `2026-04-08-t8-execution-plan-v3-scrutiny.md` | V3 scrutiny patches + scrutiny log |
| `5ee8e7c3` | `2026-04-07-t8-minimum-runnable-shakedown-packet.md` | Fix behavior count (7 not 6) and converged type (boolean not string) |
| `57857e2c` | `2026-04-08-t8-shakedown-execution-plan-v3.md` | Accept V3 — status Proposed → Accepted |
| `187dadf9` | `2026-04-07-t8-minimum-runnable-shakedown-packet.md`, `2026-04-07-t7-executable-slice-definition.md` | Fix remaining behavior count propagation (3 of 4 locations), replace phantom T7 amendment references, add T7 provenance note for 7th behavior |

### PR #100 — `feat(shakedown): add T4 containment enforcement and live smoke evidence`

**Purpose:** Land the T4 containment guard, lifecycle hooks, smoke harness, and evidence
on `main`.

**Commits (5):**

| Commit | File(s) | Purpose |
|--------|---------|---------|
| `dc18bdca` | `containment_guard.py`, `containment_lifecycle.py`, `containment.py`, `hooks.json`, `shakedown-dialogue.md`, `test_containment.py`, `test_containment_guard.py`, `test_containment_lifecycle.py` | T4 containment guard and lifecycle enforcement (core implementation) |
| `d97bc204` | `containment_smoke_setup.py`, `2026-04-08-t4-live-smoke-run-plan.md` | T4 live smoke harness and runbook |
| `b47634d2` | `2026-04-08-t4-live-smoke-run-plan.md` | Reclassify T4 smoke gate (8/8 live + 1 synthetic) |
| `18bf386a` | `t8-t4-live-smoke-log.md`, `t8-t4-poll-telemetry.jsonl` | Record T4 live smoke results |
| `e075b75f` | `containment_guard.py`, `containment_lifecycle.py`, `containment.py`, `2026-04-08-t4-live-smoke-run-plan.md`, `t8-t4-live-smoke-log.md`, `test_containment_guard.py`, `test_containment_lifecycle.py` | Fix containment escape chain + observability gaps |

## Codebase Knowledge

### Containment Guard — Fail-Closed Architecture (post-fix)

The guard at `containment_guard.py` has a three-layer defense:

| Layer | Location | Behavior |
|-------|----------|----------|
| Main evaluation | `evaluate_payload()` | Strict readers, ValueError on corrupt state → deny |
| Scope enforcement | `_enforce_active_scope()` | Invalid scope shape → `_deny()` (not raise) |
| Fail-closed probe | `_payload_requires_fail_closed()` | Strict readers, ValueError → `return True` (deny) |
| Probe wrapper | `main():515-519` | Probe crash → `require_fail_closed = True` (deny) |

Pre-fix, layer 2 raised `ValueError` instead of returning deny, and layer 4 did not
exist. A corrupt scope file with mismatched `agent_id` could cause the probe to return
`False` → passthrough. Post-fix, every layer defaults to deny when uncertain.

### Telemetry Branch IDs (complete set post-fix)

| Branch ID | Tool | Decision | Notes |
|-----------|------|----------|-------|
| `read_allow_anchor` | Read | allow | Path matches a file anchor |
| `read_allow_scope_directory` | Read | allow | Path within a scope directory |
| `read_deny_out_of_scope` | Read | deny | Path outside scope |
| `grep_allow_scope` | Grep | allow | Path rewritten to scope root |
| `grep_pathless_deny` | Grep | deny | No path provided |
| `grep_deny_out_of_scope` | Grep | deny | Path outside scope (added in fix) |
| `glob_allow_scope` | Glob | allow | Path rewritten to scope root |
| `glob_pathless_deny` | Glob | deny | No path provided |
| `glob_deny_out_of_scope` | Glob | deny | Path outside scope (added in fix) |
| `poll_success` | any | allow | Scope arrived during poll (synthetic-only) |
| `poll_timeout_deny` | any | deny | Scope not established within 2s |

`read_allow_unknown` was removed in the fix commit — the bare `except Exception`
fallback in branch classification was replaced with a narrower catch.

### Test Suite Growth

| Phase | Tests | What was added |
|-------|-------|----------------|
| Pre-review | 47 | Core containment guard, lifecycle, server module |
| Post-review fix | 57 | Fail-closed probe branches, Grep/Glob out-of-scope deny, lifecycle edge cases |

### Key File Locations

| Concept | Location |
|---------|----------|
| Guard main entry | `containment_guard.py:main()` |
| Scope enforcement | `containment_guard.py:_enforce_active_scope()` |
| Fail-closed probe | `containment_guard.py:_payload_requires_fail_closed()` |
| Scope shape validation | `containment_guard.py:_scope_has_valid_shape()` |
| Strict JSON reader | `containment.py:read_json_file_strict()` |
| Lenient JSON reader | `containment.py:read_json_file()` |
| Seed→scope promotion | `containment_lifecycle.py:_handle_subagent_start()` |
| Scope cleanup | `containment_lifecycle.py:_handle_subagent_stop()` |
| Smoke scenario defs | `containment_smoke_setup.py:_scenario_definition()` |
| Hook registration | `hooks/hooks.json` |
| V3 execution plan | `docs/plans/2026-04-08-t8-shakedown-execution-plan-v3.md` |
| T4 smoke run plan | `docs/plans/2026-04-08-t4-live-smoke-run-plan.md` |
| T4 smoke log | `docs/plans/t8-t4-live-smoke-log.md` |

### Review Agents — Corroborating Findings

The 5-agent parallel review on PR #100 produced cross-agent corroboration:

| Finding | Agents that flagged it |
|---------|----------------------|
| Grep/Glob out-of-scope deny path gap | code-reviewer (missing telemetry) + test-analyzer (untested) |
| `_payload_requires_fail_closed` zero coverage | test-analyzer (10/10 criticality) + silent-failure-hunter (escape chain) |
| `dict[str, Any]` pervasiveness | type-design-analyzer (systematic) |
| Bare `except Exception` in telemetry | silent-failure-hunter + comment-analyzer |

## Context

### Mental Model

**Framing:** This session was a publication engineering problem, not an implementation
problem. The T4 work was already done and tested — the challenge was decomposing a
noisy 25-commit branch into reviewable units while preserving evidence coherence.

**Core insight:** The correct decomposition axis was content type and reference
coherence, not commit range. Cherry-picking by ancestry (my initial instinct to require
T3 as a prerequisite) was wrong — the user's empirical cherry-pick test proved the T4
packet was portable. The right split was: (1) reference docs that T4's evidence cites,
(2) T4 implementation + evidence, (3) everything else deferred.

**Secondary insight:** Security review of containment code found a real escape path that
the implementation sessions missed. The fail-closed safety net had no safety net of its
own. This validates running the full review suite (5 agents) on security-critical code
even when the implementation passed all existing tests.

### Project State

| Item | Status | Where |
|------|--------|-------|
| B0-B2 | Complete | `feature/t8-shakedown-implementation` (worktree) |
| B3 Containment + Live Coverage | **Closed and published** | `main` (PRs #99, #100) |
| B4 Agent + Skill + Harness Assembly | **Next** | |
| T3 ordering artifacts | Deferred | `feature/t8-shakedown-implementation` (worktree) |
| D*/B* naming convention | Proposed (Defensible) | `chore/project-arc-runtime-buildout-plan` (main repo) |

### Two Repos / Two Branches

| Location | Branch | Content |
|----------|--------|---------|
| Main repo (`claude-code-tool-dev`) | `chore/t8-v3-execution-plan-publish` | Currently checked out; V3 docs PR already merged to `main` |
| Worktree (`claude-code-tool-dev-t8-impl`) | `feature/t4-containment-publish` | Currently checked out; T4 PR already merged to `main` |
| Worktree (`claude-code-tool-dev-t8-impl`) | `feature/t8-shakedown-implementation` | Original feature branch; still has T3 + B0-B2 commits not on `main` |

Note: Both repos need their local branches cleaned up. The publication branches
(`chore/t8-v3-execution-plan-publish`, `feature/t4-containment-publish`) can be deleted
since their PRs are merged. The main repo's local `main` is still 22 commits ahead of
`origin/main` (handoff archives and plan docs that accumulated without being pushed).

## Learnings

### Empirical cherry-pick testing beats ancestry reasoning

**Mechanism:** When determining whether commits are self-contained against a target
branch, actually cherry-picking them and running the test suite is definitive. Reasoning
from branch ancestry (which commits precede which) can produce false dependency claims —
a package may already exist on the target branch even if the feature branch's history
flows through earlier commits.

**Evidence:** I claimed T4 depended on T3 because the `codex-collaboration` package was
"new" against `origin/main` (12 files, 2968 insertions). The user corrected this by
cherry-picking the 4 T4 commits onto `origin/main` in a disposable clone — they applied
cleanly and 47/47 tests passed.

**Implication:** For future publication decisions, test the proposed cherry-pick set
rather than reasoning from the commit graph. The commit graph shows history; the
cherry-pick test shows portability.

**Watch for:** Even when cherry-picks apply cleanly, check for soft coupling: docs that
reference absent context, cleanup code that mentions absent artifacts, cross-references
to unpublished plans.

### Security review of containment code found a real escape path

**Mechanism:** The guard's fail-closed safety net (`_payload_requires_fail_closed`) used
non-strict state readers and was not wrapped in its own try/except. A corrupt scope file
could cause the probe to return `False` → passthrough. Additionally, if the probe itself
raised, the exception propagated to Python's default handler → exit code 1 → PreToolUse
treats non-2 as passthrough.

**Evidence:** Silent-failure-hunter finding 3 (corrupt scope → agent_id mismatch →
falls through to seed check → no seed → `False` → passthrough) + finding 4 (probe
crash → unhandled exception → exit 1 → fail-open). Test-analyzer independently
confirmed zero test coverage on `_payload_requires_fail_closed`.

**Implication:** For any PreToolUse hook that enforces security boundaries, the fail-
closed handler must itself be fail-closed. Every layer between a crash and the exit code
must default to deny, not passthrough.

**Watch for:** The same pattern in any future hooks: if the safety net uses lenient
readers or can crash without a catch, the net has a hole.

### Multi-agent review produces corroborating findings

**Mechanism:** Running 5 specialized review agents in parallel on PR #100 produced
cross-agent corroboration: the code-reviewer found missing telemetry on Grep/Glob
out-of-scope deny paths; the test-analyzer independently found those same paths were
untested; the silent-failure-hunter found the broader escape chain through the
fail-closed probe. Each agent saw a different facet of the same underlying gap.

**Evidence:** 4 cross-corroborations across agents (see Codebase Knowledge → Review
Agents — Corroborating Findings).

**Implication:** For security-critical code, running the full agent suite (not just
code-reviewer) produces higher-confidence findings because gaps that span concerns
(code quality + test coverage + error handling) are surfaced from multiple angles.

**Watch for:** Over-reliance on any single review agent. The code-reviewer alone would
not have found the escape chain — it took the silent-failure-hunter's analysis of the
fail-closed interaction + the test-analyzer's coverage gap confirmation.

## Next Steps

### 1. Clean up publication branches and local-main drift

**Dependencies:** None. Housekeeping.

**What to do:**
- Delete merged publication branches: `chore/t8-v3-execution-plan-publish` (main repo),
  `feature/t4-containment-publish` (worktree)
- The main repo's local `main` is 22 commits ahead of `origin/main` — mostly handoff
  archives and plan docs that accumulated without being pushed. These need a strategy:
  either push (makes handoff archives part of `main`'s history), or create a cleanup PR
  that excludes handoffs and publishes only the plan docs.
- The `chore/project-arc-runtime-buildout-plan` branch (D*/B* naming convention) is
  still open — 2 commits, separate from the T4 work.

### 2. Begin B4 Agent + Skill + Harness Assembly

**Dependencies:** B3 closed (this session published it).

**What to do:** Per the V3 execution plan (now on `main`), B4 is done when:
- `shakedown-dialogue` is spawnable (already verified in T4 smoke)
- `dialogue-codex` skill preloads
- `shakedown-b1` harness runs the full lifecycle (seed → scope → containment → cleanup
  → artifact write)

The shakedown-dialogue agent currently exists as a minimal 3-turn smoke agent. It needs
to be replaced with the real behavioral agent that emits structured turn state per the
machine-readable emission contract (V3 execution plan lines 84-199).

**Key context for B4:**
- The `dialogue-codex` skill is a preparatory task (P2 in the execution plan) that can
  overlap with runtime work
- The harness (`shakedown-b1`) must orchestrate the full lifecycle including transcript
  validation
- The emission contract requires `<SHAKEDOWN_TURN_STATE>` sentinels with JSON state
  blocks per turn

### 3. Build the schema validator (execution plan P3)

**Dependencies:** Can overlap with B4.

**What to do:** Build the validator that checks turn-state blocks against the emission
contract. 100% parseability is required for rehearsal acceptance (V3 execution plan
"Validator Success Bar" section).

## In Progress

**Clean stopping point.** No implementation work is in flight. Both PRs are merged to
`main`. The publication branches exist locally but are no longer needed.

The worktree is on `feature/t4-containment-publish` (the publication branch, now merged).
The main repo is on `chore/t8-v3-execution-plan-publish` (also merged). Both should be
switched to `main` or a new working branch before the next session.

## Open Questions

1. **Should the shakedown-dialogue agent be replaced or extended for B4?** The current
   agent is a minimal 3-turn smoke agent. B4 needs the real behavioral agent with
   structured turn-state emission. Replacing entirely is cleaner but loses the smoke
   agent for future containment testing. (Carried forward from prior handoff.)

2. **Where does the `dialogue-codex` skill live?** The execution plan lists it as
   preparatory task P2. It needs to map to T4 behaviors (scouting, evidence retention).
   Check the execution plan for scope. (Carried forward from prior handoff.)

3. **Should `chore/project-arc-runtime-buildout-plan` merge to main before B4 starts?**
   The D*/B* naming convention is Proposed status. Merging would make D*/B* vocabulary
   available in the implementation worktree. (Carried forward from prior handoff.)

4. **What to do with the 22-commit local-main drift?** These are handoff archives and
   plan docs that accumulated without being pushed. The plan docs may be worth
   publishing; the handoff archives are process artifacts.

## Risks

1. **Local-main drift.** The main repo's local `main` is 22 commits ahead of
   `origin/main`. If another branch is created from local `main`, it will carry those
   unpublished commits. Future publication work should start from `origin/main`, not
   local `main`.

2. **Deferred review findings.** The PR #100 review produced medium-priority findings
   that were not addressed: type design improvements (TypedDicts, discriminated unions),
   `_is_string_list` duplication, some lifecycle comment improvements, `_poll_for_scope`
   strict-reader behavior. These are code quality improvements, not bugs, but they
   accumulate technical debt if ignored across multiple build steps.

3. **T3 merge friction.** T3's ordering hooks will conflict with T4's containment hooks
   when the feature branch eventually merges. The conflict is trivially resolvable
   (additive entries in different `hooks.json` sections) but should be noted for the
   session that handles it.

4. **Publication branches still checked out.** Both repos are on merged publication
   branches. The next session should switch to `main` or create a new working branch
   before starting B4.

## References

| What | Where |
|------|-------|
| PR #99 (V3 docs) | https://github.com/jpsweeney97/claude-code-tool-dev/pull/99 |
| PR #100 (T4 containment) | https://github.com/jpsweeney97/claude-code-tool-dev/pull/100 |
| V3 execution plan | `docs/plans/2026-04-08-t8-shakedown-execution-plan-v3.md` (on `main`) |
| T4 smoke run plan | `docs/plans/2026-04-08-t4-live-smoke-run-plan.md` (on `main`) |
| T4 smoke log | `docs/plans/t8-t4-live-smoke-log.md` (on `main`) |
| D*/B* naming convention | `docs/plans/2026-04-08-project-arc-and-runtime-buildout-plan.md` (main repo, not on `origin/main`) |
| Containment guard | `packages/plugins/codex-collaboration/scripts/containment_guard.py` |
| Containment lifecycle | `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py` |
| Containment server module | `packages/plugins/codex-collaboration/server/containment.py` |
| Smoke setup script | `packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py` |
| Hook registration | `packages/plugins/codex-collaboration/hooks/hooks.json` |
| Test suite (guard) | `packages/plugins/codex-collaboration/tests/test_containment_guard.py` |
| Test suite (lifecycle) | `packages/plugins/codex-collaboration/tests/test_containment_lifecycle.py` |
| Prior handoff (archived) | `docs/handoffs/archive/2026-04-08_22-28_t4-live-smoke-complete-and-naming-convention.md` |
| Implementation worktree | `/Users/jp/Projects/active/claude-code-tool-dev-t8-impl` |

## Gotchas

1. **`origin/main` vs local `main`.** The main repo's local `main` is 22 commits ahead
   of `origin/main`. Always use `origin/main` as the base for new publication branches,
   not local `main`. The local drift contains handoff archives and plan docs that may
   not all be destined for publication.

2. **Publication branches still checked out.** Both repos are currently on merged
   publication branches (`chore/t8-v3-execution-plan-publish` and
   `feature/t4-containment-publish`). Switch to `main` or a new working branch before
   starting new work.

3. **Prior gotchas still apply.** See the prior handoff for: SubagentStart hooks are
   synchronous (containment_lifecycle.py:88-89 blocks agent startup), `disable` works
   for testing poll behavior but `delay` doesn't, lenient vs strict reader selection,
   Read `updatedInput` behavior, `_try_append_branch_telemetry` now logs to stderr (was
   silent pre-fix), `os.path.realpath` macOS `/var` → `/private/var` in tests,
   `CLAUDE_PLUGIN_DATA` `-inline` suffix.

## User Preferences

**Empirical over theoretical.** The user corrected a dependency claim by running the
actual cherry-pick rather than accepting ancestry-based reasoning. The user stated:
"I tested the proposed four-commit T4 packet directly instead of reasoning from ancestry
alone." Future sessions should verify publication claims by testing, not reasoning.

**Structured decision analysis.** The user ran a formal 5-option decision analysis with
sensitivity analysis, information gaps, and confidence levels before committing to a
publication strategy. The user expects recommendations to be structured with options,
trade-offs, and explicit ranking.

**Commit boundary design.** The user designed the split between review-fix commit and the
original T4 commits. The user expects deliberate commit boundaries that keep the repo
internally consistent at each point. (Carried forward from prior handoff.)

**Evidence integrity.** Per-scenario evidence references are mandatory in smoke logs.
Documentation must link claims to specific artifacts. (Carried forward from prior
handoff.)

**Naming precision.** The user expects D*/B* vocabulary for the two T-number namespaces.
T5 at the project level means mode strategy, not agent assembly. (Carried forward from
prior handoff.)
