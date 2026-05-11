---
date: 2026-05-07
time: "22:35"
created_at: "2026-05-08T02:35:08Z"
session_id: 6c71f197-8ec5-4104-a960-5533b28c2f8b
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-05-07_22-19_checkpoint-claude-code-skills-spec-v5-committed-awaiting-re-review.md
project: claude-code-tool-dev
branch: feature/public-skills-repo-design
commit: 7d748bb6
title: "Public-skills-repo build plan written and committed, execution deferred to next session"
type: handoff
files:
  - docs/superpowers/plans/2026-05-07-public-skills-repo-build.md
  - docs/superpowers/specs/2026-05-06-public-skills-repo-design.md
---

# Handoff: Public-skills-repo build plan written and committed, execution deferred to next session

## Goal

Convert the approved spec v5 (commit `9ab5a4ad`) of the public-skills-repo design into an executable build plan that takes the workflow from "approved spec on paper" to "verified-ready local artifact at `/Users/jp/Projects/active/claude-code-skills/`," halting before any GitHub-visible action.

**Trigger:** User opened the session by stating: "I approve of v5 of the spec. Evaluate proceeding to the planning phase." This was the verdict the prior session's checkpoint (v5-awaiting-re-review) was waiting on.

**Stakes:** The spec went through four scrutiny rounds (v1 → v2 → v3 → v4 → v5). Without an execution-binding plan, the spec stays advisory — it describes *what to do* and *why* but does not bind the workflow to dispatch points (which steps run inline vs as user gates), checkpoint points, or recovery procedures. The plan is the missing layer between approved-design and runnable-workflow.

**Success criteria for the planning phase (this session):**
- Plan file written, committed, and consistent with spec v5
- All 7 spec workflow steps mapped to tasks
- User gates identified explicitly (preflight + clean-machine validation)
- Recovery procedures (tarball, subshell trap) wired to the right tasks
- Scope clarified — what's in this plan vs. deferred to a follow-up

**Connection to project arc:** This is the second-to-last session in the public-skills-repo design track. Prior arc:
1. Initial design (v1) — 30c68a8e
2. Re-audit and rewrite (v2) — 095e2c70
3. Minor revision after scrutiny v2 (v3) — 66b19a5b
4. Major revision after scrutiny v3 (v4) — 7cd09882
5. Minor revision after scrutiny v4 (v5) — 9ab5a4ad
6. **Build plan (this session) — 7d748bb6**
7. Execution (next session) — pending

A separate follow-up plan will cover spec Steps 9-11 (gh repo create, push, tag, marketplace verify).

## Session Narrative

Session started by `/load`-ing the most recent handoff — a checkpoint from `2026-05-07_22-19` that captured "spec v5 committed, awaiting re-review." The checkpoint enumerated four branches the user could take: (a) approve, (b) revise, (c) re-scrutinize, (d) pivot. The user opened with: "I approve of v5 of the spec. Evaluate proceeding to the planning phase."

The phrasing "evaluate proceeding" rather than "proceed to planning" signaled that the user wanted reasoning before action, not just an automatic skill invocation. So the first response evaluated the readiness for planning along four axes: (1) is the spec saturated against the residual risks; (2) what does writing-plans add that the spec doesn't already have; (3) what's the right unit of work for this kind of spec (workflow vs. code-build); (4) what's the natural scope. The key observation: this spec is *structurally different* from the typical writing-plans input — it's a procedural document with a 7-step bash workflow already defined. The plan's value-add is not re-deriving steps but binding them to **dispatch / checkpoint / recovery decisions**.

Then asked the user one scope question via `AskUserQuestion`: should the plan cover (a) full publish through v0.1.0, (b) ready-to-publish state halting before repo creation, or (c) just audit+transform with publish entirely separate? User chose (b) — "Through ready-to-publish, halt before repo creation."

That answer made the plan scope concrete: spec Steps 0-8 in scope (preconditions, preflight, init, copy, sanitize, structural+lexical scans, manifests+docs, clean-machine validation, single local commit), spec Steps 9-11 deferred (gh repo create, push, tag, marketplace verify).

Invoked `superpowers:writing-plans` with that scope. The skill's procedure starts by reading the spec in full and checking if it should be split into sub-projects. The spec is one cohesive workflow — not splittable. Read all 554 lines of the spec to ground the plan against actual content (line numbers, regex patterns, JSON manifests, sanitize diffs).

Then drafted the plan structure. The natural breakpoints fell at: Task 1 (preconditions verification), Task 2 (Step 0 preflight), Task 3 (init repo), Task 4 (copy 22 skills via allowlist), Task 5 (sanitize 10 skills with 10 substeps), Task 6 (Step 4b structural scan), Task 7 (Step 5 lexical grep), Task 8 (write manifests + docs), Task 9 (Step 7 clean-machine validation), Task 10 (initial commit). Originally drafted as 11 tasks, then collapsed a placeholder Task 8 into 10 tasks total.

Key adaptation moment: the writing-plans skill is heavily TDD-oriented ("Write the failing test → run → fail → implement → pass → commit"). This plan has zero failing-test cycles because there's no code under test — the work is file copies, well-specified diffs, and automated scans. Decided to keep the bite-sized step structure but replace TDD's "test" steps with verification commands (`rg`, `ls`, file diff checks). Made this adaptation explicit in the plan's "Conventions" section so the next session understands it's a deliberate adaptation, not a deviation from the skill.

Wrote the plan file (1100 lines initially) covering all 10 tasks with:
- Exact bash blocks (preserving the spec's `set -euo pipefail` hardening at every multi-command block)
- File paths in absolute form (`/Users/jp/Projects/active/claude-code-skills/...`) per global preference
- 10 sanitize substeps with specific line-range diffs and per-substep `rg` verifications
- Two `[USER GATE]` markers (Task 2 preflight, Task 9 clean-machine validation) where the user runs `claude` in a separate session
- Recovery quick-reference table at the end mapping likely failures to recovery commands
- Self-review section mapping spec acceptance criteria to tasks

**Bug encountered during plan-writing:** mid-draft renumbering hit a sneaky `replace_all` interaction. Originally wrote 11 tasks with a placeholder Task 8. After deleting the placeholder, ran a `replace_all` for `# Task 9` → `# Task 8` to fix file-tree comments. Didn't anticipate that `# Task 9` is a substring of `## Task 9:` — so the validation heading shifted unintentionally from `## Task 9: Step 7` to `## Task 8: Step 7`. Combined with a subsequent sed-based placeholder-swap, this produced two `## Task 8` headings and a `## Task 9: Initial commit` (commit was supposed to be Task 10). Caught the bug in the post-edit grep; fixed by direct heading edits, then verified consistency with `rg '^## Task'`. Lesson captured in Learnings.

After the plan was consistent, committed at `7d748bb6` with a structured commit message that names the spec/plan binding ("binds spec v5 (commit 9ab5a4ad) to dispatch / checkpoint / recovery decisions"). Then offered three execution options via `AskUserQuestion`: inline now / subagent now / stop here. User chose "Stop here — execute in a separate session."

That's the right call given the gate-heavy structure: Tasks 2 and 9 require the user to run `claude` in a fresh session anyway, and the 10-substep sanitize task would consume meaningful context if executed inline. A fresh session for execution preserves context budget for the actual gate handling.

User then ran `/save` to capture this handoff.

## Decisions

### Plan covers spec Steps 0-8 (halt before publish)

**Choice:** Build plan ends at "verified-ready local artifact, single 'Initial release' commit on `main`." Spec Steps 9-11 (`gh repo create`, push, tag, marketplace verify) deferred to a follow-up plan.

**Driver:** User explicitly chose Option B from `AskUserQuestion`: "Through ready-to-publish, halt before repo creation. Plan ends with a verified-ready local state (audited, transformed, tarball saved). Repo creation, push, and tag handled as a separate manual step or a follow-up plan."

**Alternatives considered:**
- **Option A — full workflow through v0.1.0 publish.** Plan covers all 7 spec steps including repo creation, push, and tag. Rejected by user.
- **Option C — just audit+transform (Steps 1-6), defer publish workflow design + execution to a separate spec/plan cycle.** More aggressive scoping but loses the natural halt point at "verified-ready local."

**Implication:** Two-plan structure for the project. The build plan can be re-run safely (everything local, recoverable). The publish plan will inherit verified state from the build plan and only handle GitHub-visible actions.

**Trade-offs accepted:** The CHANGELOG.md `2026-MM-DD` placeholder remains un-replaced in this build phase — it gets replaced at publish time so the date matches the actual `gh repo create` / `git tag` event. Documented explicitly in the plan to prevent the next session from "fixing" it prematurely.

**Confidence:** High (E1 — explicit user choice with clear reasoning).

**Reversibility:** High — a follow-up "publish plan" can be written at any time using this build plan's terminal state as input.

**Change trigger:** Nothing; this is the canonical scope choice for this iteration.

### Plan adapts TDD framing to verification-gate model

**Choice:** Keep the writing-plans skill's bite-sized step structure (one action per step, 2-5 minutes) but replace "Write failing test → fail → implement → pass" with "Verify precondition → action → verify outcome." Tests become verification commands (`rg`, `ls`, file diff checks).

**Driver:** This isn't a code-build task. There's no system under test, no failing tests to make pass. The work is file copies, well-specified diffs (the spec's SANITIZE table), automated scans (lexical grep + structural rg), and a manual user gate (clean-machine `claude --plugin-dir` validation). Forcing TDD framing would produce awkward "test" steps that don't represent real verification.

**Alternatives considered:**
- **Strict TDD framing throughout.** Each step would need to invent a "failing test" — e.g., "verify the file doesn't exist yet, expect FAIL." Adds noise without adding rigor.
- **Freeform prose with no per-step structure.** Loses the bite-sized discipline that prevents under-specified plans.
- **Mixed framing per task.** Inconsistent and harder for the next session to predict.

**Implication:** Made the adaptation explicit in the plan's "Conventions" section so the next session understands the deviation from the skill's default TDD pattern is deliberate, not an oversight. The next session may freely substitute `pytest`-style assertions when applicable (e.g., if a future plan iteration includes the spec's preflight as a Python test rather than a bash scratch repo).

**Trade-offs accepted:** Readers expecting strict TDD may find the verification-gate model less rigorous-feeling. Mitigated by making every verification command exact (no "verify it works" hand-waving).

**Confidence:** Medium (E1 — single judgment call without independent validation).

**Reversibility:** High — could re-frame in a future iteration if execution feels under-rigorous.

**Change trigger:** If execution of this plan finds the verification gates inadequate (e.g., a corrupted sanitize edit slips through to validation undetected).

### Sanitize as one task with 10 substeps, not 10 separate tasks

**Choice:** Task 5 ("Sanitize the 10 SANITIZE skills") contains 10 substeps, one per affected skill (claude-md, git-hygiene, next-steps, merge-branch, making-recommendations, writing-principles, handbook, readme, design-review-team, explore-repo). Per-skill verification happens within the substep, not at task boundaries.

**Driver:** Each diff is well-specified by the spec's SANITIZE table (severity, file, line range, exact replacement text). The substeps are mechanically independent. Splitting into 10 tasks would multiply checkpoints without multiplying decision points.

**Alternatives considered:**
- **10 separate tasks.** More explicit checkpoints. Rejected because substeps already provide per-skill verification; per-task overhead would dominate. Also fragments the "sanitize phase" conceptually.
- **Single monolithic task with no per-skill verify.** Lose the safety net of catching a bad edit before the next skill. Rejected.

**Implication:** A failure in one substep (e.g., grep finds an unexpected hit) doesn't fail Task 5 wholesale — the substep is fixed in place, then Task 5 continues. A rollup verify at Task 5 Step 11 catches anything substep-level checks missed.

**Trade-offs accepted:** If execution needs to halt mid-Task-5, the resume point is "substep N of Task 5" — slightly less natural than "Task N." But the substeps are numbered, so the resume coordinate is unambiguous.

**Confidence:** Medium (E1).

**Reversibility:** High — can split into separate tasks in the next iteration if execution experience prefers it.

**Change trigger:** If a single sanitize substep fails repeatedly across resumed sessions, suggesting it warrants more checkpoint structure.

### Single commit at the end, no intermediate commits in target repo

**Choice:** Tasks 3-9 in `/Users/jp/Projects/active/claude-code-skills/` accumulate uncommitted state. Task 10 makes one commit on `main` with message "Initial release: 22 curated Claude Code skills (v0.1.0)."

**Driver:** Spec calls for the artifact to ship as a singular "Initial release." Multiple intermediate commits ("init", "add manifests", "sanitize claude-md", ...) would dilute that framing in `git log`.

**Alternatives considered:**
- **Commit per task.** More granular history; allows rollback to mid-build state. Rejected because `git log` of the new public repo should read as "released, evolved" not "constructed step-by-step."
- **Commit per phase (e.g., after sanitize, after manifests, after validation).** Halfway position. Same dilution issue at smaller scale.

**Implication:** If execution halts mid-stream, all uncommitted state is at risk of being lost on a `git reset` or repo deletion. Mitigated by the fact that the build is reproducible from the spec — re-running Tasks 3-9 produces identical output (modulo the CHANGELOG date placeholder).

**Trade-offs accepted:** No safety net of "rollback to last good state via `git reflog`" until Task 10 commits. The plan compensates with explicit recovery procedures (tarball backup before Task 9, subshell-scoped trap during validation).

**Confidence:** High — matches the spec exactly.

**Reversibility:** High — could change to per-task commits trivially if a future iteration prefers granular history.

**Change trigger:** Nothing; this matches spec.

### Stop session, execute in a separate one

**Choice:** Commit the plan, save handoff, end session. Next session loads handoff and invokes `executing-plans` or `subagent-driven-development`.

**Driver:** User explicitly chose "Stop here — execute in a separate session" from the execution-mode `AskUserQuestion`. Reasoning the user implicitly endorsed: the plan has two user gates (preflight and validation) that pause the autonomous flow regardless of execution mode, and the 10-substep sanitize task would consume meaningful context if executed inline.

**Alternatives considered:**
- **Inline execution now (Recommended in the AskUserQuestion).** Would have completed the build in this session. Rejected by user.
- **Subagent-driven now.** Adds dispatch overhead per task; user gates still pause back to main thread anyway. Rejected by user.

**Implication:** Introduces a session boundary. Resumption requires the next session to verify spec/plan integrity (no edits to either since their respective commits) before starting Task 1 — captured as a load-time check in this handoff's Next Steps.

**Trade-offs accepted:** Risk of context drift between sessions. Mitigated by the integrity-check requirement and by the plan being self-contained (every command is exact, every verification is bounded).

**Confidence:** High (E1 — explicit user choice).

**Reversibility:** High — next session can `/load` and proceed, or re-evaluate the plan freely.

**Change trigger:** Nothing.

## Changes

### Created: `docs/superpowers/plans/2026-05-07-public-skills-repo-build.md` (1100 lines, commit `7d748bb6`)

**Purpose:** Bind the approved spec v5 to executable workflow choreography. Spec Steps 0-8 mapped to 10 plan tasks with exact bash, exact verification, two named user gates, and a recovery quick-reference table.

**Approach:** 10-task decomposition, each task bite-sized (every step 2-5 minutes), with verification commands replacing TDD's failing-test cycles. Conventions section makes the TDD adaptation explicit. Spec ↔ plan mapping table at the top makes scope unambiguous.

**Key implementation details:**
- **Header:** Goal, Architecture, Tech Stack, Spec ↔ plan mapping (in/out of scope tables), Out-of-scope list.
- **File Structure section:** Tree of `/Users/jp/Projects/active/claude-code-skills/` with which task creates each file, so the next session can verify intermediate state visually.
- **Conventions section:** `set -euo pipefail` per multi-command block; no `rm`/`rm -rf` (deletions use `trash`); zero commits in Tasks 3-9; explicit `[USER GATE]` markers on Tasks 2 and 9.
- **10 sanitize substeps in Task 5:** each has the exact diff (or removal scope), the verification `rg` command, and the expected output (`CLEAN` or specific FP list).
- **Step 4b structural scan in Task 6:** five categories (a)-(e), one substep each, with the spec's PCRE regex preserved verbatim and the documented FP exclusions called out.
- **Step 5 lexical grep in Task 7:** the full 18+ token regex from spec line 406, with the two documented FPs (`writing-principles.md:54`, `:1025`) named explicitly.
- **Task 9 (Step 7 validation):** tarball backup BEFORE the destructive `mv`, subshell-scoped trap (so the empty-`~/.claude/skills/` window closes when the subshell exits, not the user's interactive shell), explicit precondition checks for concurrent claude sessions.
- **Acceptance criteria section:** mirrors spec lines 537-554 with deferred items marked clearly.
- **Recovery quick reference:** 8-row table mapping likely failure modes to one-command recovery procedures.
- **Self-review section:** maps every spec section to the task that covers it; flags the deliberate `2026-MM-DD` CHANGELOG placeholder.

**Pattern followed:** Matches the writing-plans skill's bite-sized + verification-gate + commit structure. Adapted from TDD ("write failing test → fail → impl → pass") to verification-gate ("precondition → action → verify outcome") because the work is workflow execution against existing files, not code-build.

**Future-Claude note (next session):** Before starting Task 1, verify integrity:
- `git log --oneline -1 -- docs/superpowers/specs/2026-05-06-public-skills-repo-design.md` should show `9ab5a4ad`.
- `git log --oneline -1 -- docs/superpowers/plans/2026-05-07-public-skills-repo-build.md` should show `7d748bb6`.
- If either has shifted, reconcile drift before executing.

### Archived: `docs/handoffs/2026-05-07_22-19_checkpoint-claude-code-skills-spec-v5-committed-awaiting-re-review.md`

Moved from `docs/handoffs/` to `docs/handoffs/archive/` by the `/load` skill at session start. State file written to `.session-state/handoff-6c71f197-...` for `resumed_from` tracking; this handoff's frontmatter `resumed_from` field points back to the archive path.

## Codebase Knowledge

### Spec / plan / handoff layout in this monorepo

| Path | Type | Authority |
|------|------|-----------|
| `docs/superpowers/specs/` | Spec documents | Approved spec (v5 → `9ab5a4ad`) |
| `docs/superpowers/plans/` | Implementation plans | This session's plan (`7d748bb6`) |
| `docs/handoffs/` | Active handoffs | This handoff |
| `docs/handoffs/archive/` | Resumed handoffs | Prior checkpoint (resumed) |
| `docs/handoffs/.session-state/` | Chain state files | 24-hour TTL |
| `extensions/skills/` | Dev-staged skills (~29) | Source for the public-repo build |
| `~/.claude/skills/` | Production skills (deployed via `scripts/promote`) | Affected by Task 9's stash |

The spec lives under `docs/superpowers/specs/` because the public-skills-repo design was a "superpowers"-style design effort (multi-round scrutiny, structured spec). The plan lives in the matching `docs/superpowers/plans/` subdir for proximity, even though `docs/plans/` also exists in this repo with similar content. Both subdirs are valid local convention.

### Public-skills-repo target structure

The plan creates `/Users/jp/Projects/active/claude-code-skills/` (new repo, **outside** this monorepo) with:

```
.git/                           # Task 3
.claude-plugin/
├── plugin.json                 # Task 8
└── marketplace.json            # Task 8
skills/                         # Task 4 (copy), Task 5 (sanitize)
├── adversarial-review/SKILL.md # PUBLISH AS-IS
├── claude-md/{SKILL.md, references/} # SANITIZE
├── ... (22 directories total)
└── writing-principles/{SKILL.md, writing-principles.md}  # SANITIZE (remove Composability)
README.md, LICENSE, CHANGELOG.md, CONTRIBUTING.md, .gitignore  # Task 8
```

**12 PUBLISH AS-IS:** `adversarial-review`, `exiting-worktrees`, `format-export`, `implementation-review`, `llm-reference`, `prompt-generator`, `review-code`, `review-plan`, `review-strategy`, `review-writing`, `scrutinize`, `system-design-review`.

**10 SANITIZE:** `claude-md`, `git-hygiene`, `next-steps`, `merge-branch`, `making-recommendations`, `writing-principles`, `handbook`, `readme`, `design-review-team`, `explore-repo`.

**Excluded from v1:** `cc-docs`, `claude-code-docs`, `openai-docs` (MCP deps), `evaluating-extension-adoption` (companion skill missing), `learn`, `promote` (paired-system semantics), `changelog` (handoff-archivist teammate dep). Total source set is ~29 skills; 22 ship, 7 deferred.

### Two-layer audit framework

The spec defines two complementary audits over the shipped content:

| Layer | What it catches | Mechanism |
|-------|-----------------|-----------|
| **Lexical residue** (Step 5) | Internal-vocab leakage in prose | `rg -i` over 18+ token categories (codex, cross-model, engram, superspec, jpsweeney97, etc.) |
| **Structural references** (Step 4b) | Dangling refs that lexical can't see (slash commands, named skills, env flags, sibling cross-refs, named protocols) | Manual checklist, 5 categories, PCRE regex for (a) and (e) |

The two layers address different threat models. Lexical = "internal-vocab leakage in prose"; structural = "references to things not in the published set." The structural layer was added in spec v4 after scrutiny v3 identified the failure class. Spec v5 added category (e) (named protocols/procedures/workflows) after scrutiny v4 found two real misses (`merge-branch:17` "the commit-push-pr workflow", `next-steps:21,28` "Next Steps protocol"). The lesson — "when an audit enumerates what it checks, the omitted categories are where bugs hide" — is captured in the prior session's checkpoint Key Finding.

### Step 7 (clean-machine validation) safety machinery

Three layers of defense against the destructive `mv ~/.claude/skills` operation:

1. **`set -euo pipefail`** at the top of the bash workflow — silent backup failure aborts before the destructive mv.
2. **Tarball snapshot** taken BEFORE the mv — recovery is one command if anything else fails (`tar xzf "$BACKUP" -C ~/.claude`).
3. **Subshell-scoped trap** — the `trap → mv → claude` sequence lives inside `( ... )` so the empty-skills window closes on subshell exit, not full shell exit. Without subshell scoping, `~/.claude/skills/` would remain empty for the rest of the user's main-shell lifetime; any concurrent claude session, new terminal, or scheduled hook firing during that window would see the empty directory and misbehave.

The plan's Task 9 preserves all three layers exactly as specified. The recovery quick-reference table calls out the tarball as the manual-fallback for trap-doesn't-fire cases (kill -9, system crash, terminal closed without Ctrl-D).

### Patterns observed in existing plans (`docs/superpowers/plans/`)

| Pattern | Example |
|---------|---------|
| Bite-sized step structure | Most plans use checkbox `- [ ]` with one action per step |
| Header block with REQUIRED SUB-SKILL note | Standard for plans intended for executing-plans / subagent-driven-development |
| Sequential task numbering | `Task 1`, `Task 2`, ... |
| Spec ↔ plan mapping for derived plans | Especially the engram remediation rounds |

This plan follows all four patterns.

### Key locations

| Concept | Location |
|---------|----------|
| Spec v5 | `docs/superpowers/specs/2026-05-06-public-skills-repo-design.md` (commit `9ab5a4ad`) |
| Build plan | `docs/superpowers/plans/2026-05-07-public-skills-repo-build.md` (commit `7d748bb6`) |
| Source skills | `extensions/skills/<name>/...` |
| Production skills (target of Task 9 stash) | `~/.claude/skills/` |
| Target repo (created by Task 3) | `/Users/jp/Projects/active/claude-code-skills/` |
| Writing-plans skill | `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-plans/SKILL.md` |

## Context

### Prior project arc (compressed)

- **2026-05-06 (`30c68a8e`):** v1 spec drafted from agent-summary audit. Status was "Approved for implementation" prematurely.
- **(`095e2c70`):** v2 — agent-summary audit was unsound; rewrote curated breakdown after direct-file-inspection re-audit. v1 reported 19 PUBLISH + 3 SANITIZE; v2 reported 13 PUBLISH + 9 SANITIZE.
- **(`66b19a5b`):** v3 — minor precision fixes after scrutiny v2. New counts 14 PUBLISH + 8 SANITIZE.
- **(`7cd09882`):** v4 — major revision after scrutiny v3. Added Step 4b structural scan, Step 0 preflight, README Requirements, `trash`-based deletion rule, moved `claude-md` from PUBLISH to SANITIZE.
- **(`9ab5a4ad`):** v5 — minor revision after scrutiny v4. Added category (e) named-protocols, narrowed Step 4b regex, subshell-scoped trap, `set -euo pipefail`, CHANGELOG.md spec, Success criteria section, README v2.1.32+ floor, `skillOverrides` primary in Trigger-shadow note. New counts 12 PUBLISH + 10 SANITIZE = 22.
- **2026-05-07 (`7d748bb6`):** Build plan written. (this session)
- **Pending:** Build execution (next session). Publish plan (deferred). Publish execution (further deferred).

### Mental model

This is a **workflow execution problem**, not a system-build problem. The spec is a procedural document — a 7-step bash workflow with audit machinery and risk register. The plan is the **execution choreography** for that workflow:

- **Dispatch decisions** — which steps run inline, which go to subagents, which require a manual user gate.
- **Checkpoint decisions** — where to stop and confirm with the user before proceeding.
- **Recovery decisions** — how to get back to a known-good state if a step fails.

Code-build templates fit awkwardly because there's no system under test. The right framing is "what makes this workflow safe and verifiable to execute" — the plan adds the safety/verifiability that the spec describes but doesn't bind.

A useful analogy: spec is the **recipe** (ingredients, steps, oven temp), plan is the **kitchen choreography** (mise en place, who plates what, when to taste, what to do if the soufflé falls). Both are needed; one without the other leaves either the *what* or the *how-to-execute-safely* unspecified.

### Environment

- **Working directory:** `/Users/jp/Projects/active/claude-code-tool-dev` (this monorepo)
- **Branch:** `feature/public-skills-repo-design`
- **Working tree:** clean as of session end
- **HEAD:** `7d748bb6` (build plan commit)
- **Tools needed for execution:** `bash`, `git` ≥ 2.28, `gh` (authenticated), `trash-cli`, `ripgrep` with PCRE2, `tar`, `claude` CLI ≥ 2.1.32

### Spec ↔ plan task mapping (compressed)

| Spec Step | Plan Task | What it does |
|-----------|-----------|--------------|
| Preconditions | Task 1 | Verify gh auth, trash, git, claude, rg PCRE |
| Step 0 (preflight) | Task 2 | Pre-validate `source: "./"` in scratch repo (USER GATE) |
| Step 1 (init) | Task 3 | `mkdir + git init -b main` |
| Step 2 (structure) + Step 3 (copy) | Task 4 | `.claude-plugin/`, `skills/`, allowlist copy of 22 skills, `.DS_Store` strip |
| Step 4 (sanitize) | Task 5 | 10 substeps, one per SANITIZE skill |
| Step 4b (structural scan) | Task 6 | 5 substeps, categories (a)-(e) (USER GATE) |
| Step 5 (lexical grep) | Task 7 | Single grep run, expect only 2 documented FPs (USER GATE) |
| Step 6 (manifests + docs) | Task 8 | plugin.json, marketplace.json, README, LICENSE, CHANGELOG, CONTRIBUTING, .gitignore |
| Step 7 (validation) | Task 9 | Tarball + subshell-stash + claude --plugin-dir (USER GATE) |
| Step 8 (commit) | Task 10 | Single "Initial release" commit; HALT |
| Steps 9-11 | **Deferred** | gh repo create, push, tag, marketplace verify |

## Conversation Highlights

**Approval signal opening the session:**
User: "I approve of v5 of the spec. Evaluate proceeding to the planning phase."
— Notable framing: "evaluate proceeding" rather than "proceed." User wanted reasoning before action, not just an automatic skill invocation. This shaped the first response (evaluation-then-recommendation) rather than going straight to writing-plans.

**Scope answer:**
Picked Option B from `AskUserQuestion`: "Through ready-to-publish, halt before repo creation. Plan ends with a verified-ready local state (audited, transformed, tarball saved). Repo creation, push, and tag handled as a separate manual step or a follow-up plan."
— Drove the spec Steps 0-8 in-scope / Steps 9-11 deferred decision.

**Execution-mode answer:**
Picked "Stop here — execute in a separate session" from execution-mode `AskUserQuestion`.
— Implicitly endorsed the reasoning that gate-heavy + 10-substep-sanitize → fresh context for execution. User did not push back on the recommendation that Inline was best for this plan; they preferred a session boundary regardless.

**Working pattern observed:** User responds with **option-letter** style answers when given multiple-choice questions, often without further commentary. Confirmation is the answer; explanation is in the option's `description` field. This is consistent with prior-session feedback that "user wants commits handled proactively" — they delegate execution decisions when the choice space is clear.

## User Preferences

**Decision style — recommendations + multiple-choice:**
User responded efficiently to `AskUserQuestion` calls but expected the question to be calibrated. The first call (scope) had three options; user picked the middle one (the most-conservative-with-still-finishing-the-build option). The second call (execution mode) had three options with a Recommended marker; user chose the non-recommended "Stop here" option, indicating they don't blindly follow the recommendation but use it as a starting point for their own decision.

**"Evaluate proceeding" not "proceed":**
The opening phrase signaled that the user wanted reasoning before action. Future-Claude should treat phrases like "evaluate," "consider," "think about" as signals that the user wants the reasoning made explicit, not just the conclusion. Distinct from "proceed," "do it," "continue" which signal direct execution.

**Plain language in conversation, formal structure in artifacts:**
Per the auto-memory note (`feedback_plain_language.md`), the user prefers plain accessible language for explanations and reserves formal structure for artifacts. The session followed this — reasoning was conveyed in prose, while the plan file uses structured headings, tables, and checklists.

**Handle commits proactively (per saved feedback):**
The plan was committed without asking, since it was a coherent buildable chunk. Commit message used a HEREDOC, ended with no `--no-verify`, no force, no amend. This matched the saved memory `feedback_handle_commits.md`.

**No `git add -A` / `git add .`:**
The plan's Task 10 explicitly stages by path even in a brand-new repo (where `git add .` would be safe technically). This honors the global rule even when the rule's typical motivation (avoiding sweeping in secrets) doesn't apply locally.

**No `rm` ever:**
The plan uses `trash` for every deletion, including in the Task 9 trap. Built into the plan's Conventions section as a first-class rule.

## Learnings

### `replace_all` on a markdown number-prefix can match across heading levels

**Mechanism:** Calling `replace_all` with `# Task 9` matches **every** occurrence of that substring — including `## Task 9:` (because `## Task 9:` contains `# Task 9` as a substring of length 7). When renumbering markdown, this silently shifts headings the user did not intend to touch.

**Evidence:** Mid-plan-write, ran `replace_all("# Task 9", "# Task 8")` to fix file-tree comments after deleting a placeholder Task 8. The replace_all also affected the validation heading `## Task 9: Step 7 — local clean-machine validation` (became `## Task 8: Step 7`). Caught by the post-edit grep `rg -n '^## Task'` showing two `## Task 8` headings simultaneously.

**Implication:** For markdown task-number renumbering, the safer pattern is sed with placeholder swap:

```bash
sed -i '' \
  -e 's/Task 11/__TASK_X11__/g' \
  -e 's/Task 10/__TASK_X10__/g' \
  -e 's/Task 9/__TASK_X9__/g' \
  file.md
sed -i '' \
  -e 's/__TASK_X9__/Task 8/g' \
  -e 's/__TASK_X10__/Task 9/g' \
  -e 's/__TASK_X11__/Task 10/g' \
  file.md
```

This avoids double-shift and is order-independent for the second stage. The first stage must order from highest-to-lowest to avoid prefix collision (`Task 11` contains `Task 1` as a prefix in some patterns, though not in this exact form).

**Watch for:** Any `replace_all` on a string that's a substring of a longer markdown structure (heading, comment, code block) is suspect. When renumbering, prefer placeholder swap or specific Edit calls with full surrounding context.

### Spec → plan binding adds dispatch / checkpoint / recovery, not duplicate steps

**Mechanism:** A spec describes *what to do* and *why*. A plan describes *how to execute it safely* — which steps need user gates, where to stop and verify, what happens when a step fails. The plan is **not** a re-derivation of the spec.

**Evidence:** This session's plan adds:
- Two `[USER GATE]` markers (Tasks 2 + 9) where the spec just says "verify in fresh claude session" without binding it as an execution checkpoint.
- A recovery quick-reference table mapping 8 likely failure modes to one-command recovery procedures, not present in the spec.
- A "Conventions" section calling out `set -euo pipefail` per block, no `rm`, single commit at end — these are *enforced* in the plan but only *described* in the spec.
- Specific verification commands (`rg`, `ls`, `find`) per task with expected output, where the spec leaves verification mostly implicit.

**Implication:** When writing-plans receives a spec that's already procedural (vs. a feature spec), the plan's value-add is the **execution layer**, not the procedural layer. Resist the urge to re-derive the workflow; instead ask "what bindings turn this from advisory into runnable?"

**Watch for:** A plan that reads as a verbose paraphrase of the spec is doing redundant work. A plan that adds new *prescriptive* content (gates, checkpoints, recovery) is doing the right work.

### TDD-style step structure adapts cleanly to verification-gate work

**Mechanism:** Writing-plans is heavily TDD-oriented but its core discipline (one action per step, exact command, expected output, commit at natural breakpoints) generalizes to non-code-build work. Replacing "failing test → fail → impl → pass" with "verify precondition → action → verify outcome" preserves the discipline while removing the awkward "test" framing.

**Evidence:** The plan applied this adaptation across 10 tasks and ~50+ steps. The result is consistent in shape with TDD plans (every step has expected output, every multi-step task has a roll-up verify, every task ends at a natural checkpoint) without the artificial "write a failing test for the file copy" awkwardness.

**Implication:** The writing-plans skill is more general than its TDD framing suggests. For workflow-execution plans, the verification-gate adaptation is the right framing; declare it explicitly in the Conventions section so the next session understands the deviation is deliberate.

**Watch for:** If a future workflow-plan tries strict TDD framing, expect awkwardness around "tests" for purely mechanical steps (file copies, environment checks). Verification-gate framing is cleaner.

### Manual user gates concentrate the risk in workflow plans

**Mechanism:** A workflow plan can automate most steps but cannot automate steps that require a fresh `claude` invocation (preflight, validation) or that require the user to execute a `/plugin` command in the UI. These gates are the load-bearing safety checkpoints.

**Evidence:** This plan has two gates (Tasks 2 + 9). Both are critical:
- Task 2 (preflight) catches a layout-incompatibility BEFORE the destructive mv in Task 9. If skipped, a `source: "./"` rejection would be discovered only at validation, when the user has already invested effort in copying + sanitizing 22 skills.
- Task 9 (validation) catches sanitization regressions, missing manifests, frontmatter corruption. If skipped, Task 10's commit would lock in an unverified artifact.

**Implication:** Plans with gates should weight the choice between inline / subagent / stop-here toward **stop-here** when the gates are dense. Subagent execution doesn't help (gates pause back to main thread anyway). Inline execution costs context.

**Watch for:** Future workflow plans should call out gate density up front so the next session can pick execution mode informed by the gate count.

## Next Steps

### 1. Resume in a new session and execute the plan

**Dependencies:** None — plan is committed.

**What to do first:** Run `/load` to resume from this handoff. Verify spec/plan integrity:

```bash
git log --oneline -1 -- docs/superpowers/specs/2026-05-06-public-skills-repo-design.md
# Expected: 9ab5a4ad

git log --oneline -1 -- docs/superpowers/plans/2026-05-07-public-skills-repo-build.md
# Expected: 7d748bb6
```

If either has shifted, reconcile drift before executing.

**Approach suggestion:** Use `superpowers:executing-plans` (inline mode) — best fit for the gate-heavy structure. Subagent mode is also viable if context budget is a concern.

**Acceptance criteria:** Plan's Task 10 commits a single "Initial release" commit on `main` in `/Users/jp/Projects/active/claude-code-skills/`. The plan's acceptance-criteria checklist (in-scope subset) is fully checked.

**Potential obstacles:**
- Step 0 preflight may fail (`source: "./"` rejected) — would require restructuring spec to nested layout BEFORE re-running.
- Task 9 validation may fail if a sanitize edit corrupted SKILL.md frontmatter — return to Task 5 substep, fix, re-verify.
- Tarball backup may run out of disk space — `set -euo pipefail` aborts before destructive mv.

### 2. Write the publish plan (post-build)

**Dependencies:** Build plan must execute successfully first.

**What to read first:** This handoff (for build-state context), the spec's Steps 9-11 (lines 469-489), the spec's Acceptance criteria (deferred items), the build plan's Acceptance criteria section (deferred items).

**Approach suggestion:** A separate plan covering: gh repo create, remote add, push -u origin main, git tag v0.1.0, push tag, gh repo edit --add-topic (×5), marketplace install verification in a separate clean-machine session, post-publish CHANGELOG date replacement.

**Acceptance criteria:** Repo public on GitHub, tagged `v0.1.0`, five discoverability topics applied, marketplace install verified end-to-end, post-publish success-criteria tracking initiated.

### 3. Track Success criteria for v0.1.0 (post-publish)

**Dependencies:** Publish plan must execute successfully.

**What to do:** Track the four post-publish criteria from spec lines 22-31 over the first month after release: discoverable via gh search, installable without contacting author, no "missing flag" support traffic, skill triggering works as described. Use observations to inform v1.x triage.

**Acceptance criteria:** Observations recorded somewhere durable (issue comment, separate notes file, or `docs/learnings/`).

## In Progress

Clean stopping point. No work in flight.

The session ended at a natural boundary: plan written, plan committed, execution mode chosen ("stop here"), handoff initiated.

## Open Questions

- **Will Step 0 preflight succeed?** Spec docs verification confirmed `source: "./"` should accept, but the running CLI may differ from docs. Plan halts the entire workflow if preflight fails — restructuring to nested layout is the contingency.
- **Will Task 9 clean-machine validation reveal any registration errors?** All 22 skills should register cleanly given the audit + sanitize, but a frontmatter corruption in any sanitize step could cause one to fail. Recovery is to fix the substep and re-validate.
- **Should the publish plan include the CHANGELOG date replacement?** Currently planned as a step within the publish plan (replace `2026-MM-DD` with the actual `gh repo create` date). Could alternatively be done in a separate "release-prep" task. Decide when writing the publish plan.
- **Whether to keep the tarball after Task 9 PASS.** Plan defaults to `trash`-ing it. Defense-in-depth argument for keeping it through Task 10. Low-stakes choice; defer to user at execution time.

## Risks

- **Spec/plan drift across sessions** — if the spec or plan is edited between this session and the execution session, the binding is broken. Mitigated by the integrity-check requirement in Next Steps #1.
- **Concurrent claude session during Task 9** — exposes the user's main shell to an empty `~/.claude/skills/`. Mitigated by subshell-scoped trap + tarball backup, but a kill -9 during the validation window still requires manual `tar xzf` recovery.
- **CHANGELOG `2026-MM-DD` placeholder accidentally "fixed" before publish** — the plan calls this out explicitly but a well-intentioned next-session edit could replace it prematurely. Plan's Self-review section flags this; the Acceptance criteria preserve the placeholder.
- **Auth-teams flag dependency at install time** — 5 of 22 skills hard-stop without `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. README Requirements section is the primary mitigation; spec Risk #7 documents the venue interrogation and "fail visibly, fix on bug report" stance.
- **`replace_all` regression** — the renumbering bug pattern from this session could recur in any plan with sequential task numbers if a future edit uses substring-prone replace_all. Plan-writing learning captured above; broader project hygiene would be to prefer placeholder swap or specific Edits for any task-number renumbering.

## References

| What | Where |
|------|-------|
| Approved spec v5 | `docs/superpowers/specs/2026-05-06-public-skills-repo-design.md` (commit `9ab5a4ad`) |
| Build plan | `docs/superpowers/plans/2026-05-07-public-skills-repo-build.md` (commit `7d748bb6`) |
| Resumed checkpoint | `docs/handoffs/archive/2026-05-07_22-19_checkpoint-claude-code-skills-spec-v5-committed-awaiting-re-review.md` |
| Spec v4 → v5 diff log | spec History section (lines 8-14) |
| Writing-plans skill | `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-plans/SKILL.md` |
| Handoff format reference | `packages/plugins/handoff/references/format-reference.md` |
| Handoff contract | `packages/plugins/handoff/references/handoff-contract.md` |
| Trigger Eval Findings (relevant to Task 9 design) | `MEMORY.md` "Trigger Eval Findings" section |
| Project arc commit chain | `30c68a8e → 095e2c70 → 66b19a5b → 7cd09882 → 9ab5a4ad → 7d748bb6` |

## Gotchas

- **Two-Task-8 bug from `replace_all`:** documented above. If the next session edits the plan, prefer specific Edits over replace_all on substring-prone strings. The renumbering placeholder-swap pattern is captured in Learnings #1.
- **CHANGELOG `2026-MM-DD` is intentional** — do NOT replace until publish time. Plan's Task 8 Step 5 and Self-review section both flag this.
- **`docs/superpowers/plans/` vs `docs/plans/`** — both exist with similar content in this repo. The plan went to the former for proximity to the spec, but either is valid local convention. Don't be confused if a future browse finds plans split across both.
- **`# Task N` vs `## Task N:` substring relationship** — `# Task 9` is a substring of `## Task 9:`. Any markdown manipulation that operates on `# Task ...` patterns must account for this.
- **Auto-memory `MEMORY.md` does not yet reflect this session** — the build plan being committed and the execution being deferred to the next session aren't recorded in memory. If the user runs `/promote` or other memory-curation skills, this session's facts may need to be added.
- **Handoff archive chain is now 2 deep** — this handoff resumes the v5-checkpoint, which itself resumed the v4-checkpoint. The `resumed_from` field only points to the immediate predecessor. The full chain is recoverable by walking archive files but isn't first-class.

## Rejected Approaches

### Full publish workflow in one plan

**Approach:** Plan covers all spec Steps 0-11 in a single document — preconditions through marketplace install verification.

**Why it seemed promising:** One plan = one execution session = no session boundary risk. Simpler resumption protocol.

**Specific failure (rejected by user choice):** User explicitly chose Option B ("halt before repo creation") in the scope `AskUserQuestion`. Reasoning implicit in their choice: GitHub-visible actions are irreversible (repo created, public, search-indexed) and warrant a separate session to set them up. The build plan can be re-run safely; the publish plan cannot.

**What it taught:** For plans with mixed reversible/irreversible phases, halting at the reversible/irreversible boundary is the natural scope. Don't pack both into one plan — the irreversible phase deserves its own plan with its own checkpoints.

### Inline execution this session

**Approach:** Pick up immediately after committing the plan; execute Task 1 onward in the same session.

**Why it seemed promising:** No session boundary risk. Plan and execution share context. Bug-fix learning fresh in mind.

**Specific failure (rejected by user choice):** User chose "Stop here — execute in a separate session" over the AskUserQuestion's Recommended option (Inline execution). Implicit reasoning: gate-heavy plan + 10-substep sanitize task = significant context consumption inline; fresh context for execution preserves headroom for handling gate responses without compaction.

**What it taught:** "Recommended" markers in `AskUserQuestion` are starting points, not endpoints. Users may have context (workflow rhythm, time-of-day, parallel work) that makes a non-recommended option correct. The plan's two-gate density was probably the deciding factor — the Recommended path would still pause back to main thread at each gate, so the savings from inline-vs-separate were smaller than the savings from fresh-context.

### Subagent-driven execution

**Approach:** Dispatch a fresh subagent per task with two-stage review. Plan execution proceeds task-by-task with subagent reports back to main thread.

**Why it seemed promising:** Subagent dispatch is the writing-plans skill's "Recommended" mode. Per-task isolation reduces context pollution.

**Specific failure (rejected by user choice):** Same `AskUserQuestion` answer ("Stop here"). Subagent mode shares the gate-heavy disadvantage with inline mode — both pause back to main thread at gates anyway, so the per-task isolation benefit is partially neutralized for this plan.

**What it taught:** Subagent mode is best for plans with high inter-task isolation and few gates. Workflow-execution plans with dense gates favor either inline (if context budget allows) or stop-here (if gate handling needs fresh thread).
