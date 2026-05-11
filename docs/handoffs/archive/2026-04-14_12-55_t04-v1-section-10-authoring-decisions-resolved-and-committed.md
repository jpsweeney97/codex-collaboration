---
date: 2026-04-14
time: "12:55"
created_at: "2026-04-14T16:55:59Z"
session_id: 3a341e19-1566-48b2-890f-59ef587cb6d5
resumed_from: docs/handoffs/archive/2026-04-13_23-12_t04-v1-plan-approved-merged-pushed-implementation-unblocked.md
project: claude-code-tool-dev
branch: feature/t04-v1-implementation
commit: 30edf38a
title: "T-04 v1 §10 authoring decisions resolved and committed"
type: handoff
files:
  - docs/plans/2026-04-14-t04-v1-authoring-decisions.md
  - docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md
---

# T-04 v1 §10 Authoring Decisions Resolved and Committed

## Goal

Resume from the 2026-04-13 23:12 handoff (plan approved, merged to `main@73f8c9c1`, pushed) and begin T-04 v1 implementation. Before authoring any of the four new v1 surfaces, close out the four authoring-time decisions the plan's §10 explicitly deferred to the implementation session.

**Trigger.** User's explicit directive at session start: *"Continue with T-04 v1 implementation. Start by reading the plan, then creating a task list."* After presenting the task list, user redirected to: *"I'd prefer to start with brainstorming the §10 decisions up front before authoring."* — converting what would have been a straight linear implementation into a decisions-first phase.

**Stakes.** §10 items directly shape the four v1 surfaces. The scouting budget pins a constant in `dialogue-orchestrator.md`. The flag vocabulary pins the `/dialogue` skill's invocation parser. The serialization choice pins the skill's surfacing body. Each is a single authoring moment with downstream cost if chosen poorly — a larger N silently reinvents the briefing-assembly layer §2.2 deferred; a flag vocabulary inflates the bootstrap-test surface; a serialization choice that loses the canonical JSON breaks future cross-model parser migration per §7.2.

**Success criteria achieved this session:**

1. Read the merged plan in full before proceeding — **achieved** (632 lines, §1 through §13 plus frontmatter).
2. Build a task list reflecting plan §12's seven implementation steps plus a branch-setup prefix — **achieved** (8 tasks created).
3. Resolve the three actionable §10 items (scouting budget, flags, serialization) and explicitly handle §10.4 (crash recovery) — **achieved**; four questions closed out.
4. Record resolutions in a form that preserves the plan's approved-baseline integrity — **achieved** (companion addendum, not inline plan edits).
5. Land on the feature branch — **achieved** (branch created, commit `30edf38a`).
6. Preserve the commit-merge-push-as-separate-authorizations discipline — **achieved** (committed only; merge and push not yet authorized).

**Bigger picture.** This session converts the approved scoping plan into an approved implementation frame. The plan is frozen as the contract; the addendum is the implementation-time ledger of what authoring decides against that contract. T-04 v1 packet sequence across three sessions is now: draft (pre-prior) → rewrite (prior-prior) → approve and land (prior) → **close implementation-time questions (this)** → author the four new surfaces (next).

## Session Narrative

**Phase 1 — Load and orientation (~5 min).**

Loaded `2026-04-13_23-12_t04-v1-plan-approved-merged-pushed-implementation-unblocked.md` via `/handoff:load`. Handoff archived; state file written at `.session-state/handoff-3a341e19-1566-48b2-890f-59ef587cb6d5`. Confirmed branch state: `main@73f8c9c1`, working tree clean, `origin/main` synced. Surfaced the continuation choice (T-04 v1 / Engram / something else). User selected T-04 v1 implementation and asked for plan read first, then task list.

**Phase 2 — Plan re-read and task list build (~10 min).**

Checked plan line count (`wc -l` → 632 lines; under the 2000-line chunking threshold) and read end-to-end. Already internalized from prior sessions but re-read to preserve intent alignment. Key sections re-confirmed: §4 ownership table (6 owned activities for `/dialogue`), §6.1 step 1 (preflight sweep before live-run check), §8.4 bootstrap-boundary invariant (`allowed-tools` must exclude `codex.dialogue.*`), §10 (four deferred questions).

Created 8 tasks via TaskCreate:
1. Branch creation (`feature/t04-v1-implementation` from main).
2. Extract turn-semantics reference doc from `dialogue-codex`.
3. Author `dialogue-orchestrator` agent body.
4. Author `/dialogue` user skill.
5. Extend `hooks.json` SubagentStart/SubagentStop matchers.
6. End-to-end verification per §8.2.
7. 14-item rubric inspection.
8. Confirm 566-test shakedown suite passes unchanged.

Task 1 is a prefix — the plan's §12 has 7 steps; the branch-creation step is necessary because `main` is protected (per `.claude/rules/workflow/git.md` the PreToolUse hook blocks Edit/Write on `main`).

**Phase 3 — User redirect to brainstorm-first (~2 min).**

User explicitly changed direction: *"I'd prefer to start with brainstorming the §10 decisions up front before authoring."* Invoked the `superpowers:brainstorming` skill. Framed a process adjustment up-front: the brainstorming skill's terminal state is "invoke writing-plans," but this session's deliverable is a lightweight addendum to an already-approved plan, not a fresh design spec. Proposed that the skill's spirit (one question at a time, alternatives with recommendations, YAGNI) applies while the output artifact shape deviates (addendum, not spec).

**Phase 4 — Flag vocabulary question (~3 min).**

First §10 decision, presented with 4 options (zero flags, one flag `--paths`, three flags, other). Recommended zero flags on YAGNI grounds, noting §3.1 already commits to flags being non-contractual. User chose **A (zero flags)** without friction.

**Phase 5 — Scouting budget question (~5 min).**

Presented N as three axes (what N, hard vs soft cap, which tools count). Options A (N=3 hard), B (N=5 hard), C (N=3 soft / 5 hard), D (structured). Recommended A on alignment-with-plan grounds.

User asked the clarifying question: *"what exactly is the scouting budget?"* — a meta-signal that they wanted the concept anchored before choosing. Delivered a phase-breakdown response with a concrete example (scouting a containment-guard question: Grep → Read → Read → prepend prose block to first `reply`). Also drew the explicit budget/non-budget line: inline scouting tool calls count; `codex.dialogue.*` calls, per-turn scouting inside the dialogue loop, and `Agent` dispatches do not.

User chose **B (N=5 hard cap on combined Read+Grep+Glob)**. This was a deliberate departure from the plan's initial N=3 target, grounded in the "locate → inspect → confirm" shape that N=3 truncates. Not a rejection of my recommendation but a calibration against a real-world scouting shape.

**Phase 6 — Synthesis serialization question (~5 min).**

Presented three options: raw JSON, Markdown only, hybrid prose-first-with-JSON-appendix. Recommended hybrid (C) on the grounds that v1's consumer is the user's eye (readability matters) but the artifact is canonically JSON per §3.2 (fidelity matters for §7.2-deferred consumers).

User replied with a refinement: *"C, with one refinement: make it a thin human wrapper over a canonical JSON appendix, not a second full rendering of every field."* Key authoring-time constraints added:
- *"Treat the JSON appendix as the source of truth. The Markdown above it is a view, not a second artifact."*
- *"Do not depend on 'collapsible' behavior unless the renderer is known to support it. In this environment, a plain fenced appendix is the safe default; `<details>` is optional sugar, not part of the contract."*

The refinement is structurally significant: it's the **authoring discipline** that keeps §3.2 schema enforceable. If the Markdown becomes a second artifact, downstream consumers (T-04 closure, cross-model parser migration per §7.2) have to decide which to parse. Treating JSON as canonical keeps that decision trivially closed.

**Phase 7 — Consolidation and artifact form (~3 min).**

Summarized the three resolutions plus the §10.4 deferral in a table. Flagged the process deviation: skip the brainstorming skill's terminal "invoke writing-plans" step because the existing plan + task list is already the implementation plan; a fresh writing-plans pass would duplicate §12. Presented two artifact forms:
- **P: Inline edits to plan §10** (co-located but modifies approved baseline).
- **Q: Separate companion doc** at `docs/plans/2026-04-14-t04-v1-authoring-decisions.md` with a pointer from the plan.

Recommended Q for baseline-integrity reasons. User chose **Q with a direct link from plan to companion** and confirmed skipping writing-plans.

**Phase 8 — Authoring the addendum and pointer edit (~8 min).**

Created `feature/t04-v1-implementation` from main. Wrote the addendum (104 lines) with frontmatter containing machine-readable `parent_plan`, `closes`, `defers` fields. Edited plan §10 header to add a "Resolutions recorded in..." note, preserving the four-item list as contract-closure context.

Ran self-review against the brainstorming skill's four checks (placeholder scan, internal consistency, scope, ambiguity). Flagged one borderline item during ambiguity check: the addendum's Decision 3 text *"No reliance on `<details>` collapsible behavior ... if used, it must remain cosmetic."* — read twice and confirmed coherent (may use for rendering, content invariants hold regardless). No inline fixes needed.

Presented both files for review. User approved both and instructed: *"Commit both changes, then save a handoff."*

**Phase 9 — Commit and handoff (~3 min).**

Verified working tree state (1 modified, 1 untracked — exactly the two intended files). Committed with HEREDOC message `docs(plan): record T-04 v1 authoring-time decisions addendum` following the repo's conventional-commits style. Commit landed as `30edf38a` on `feature/t04-v1-implementation`. No push; no merge. Began handoff save immediately per user's sequenced instruction.

## Decisions

### Decision 1: Inline scouting budget — N=5 hard cap (user-selected)

**Choice:** N=5 hard cap on combined `Read`+`Grep`+`Glob` tool calls during the inline initial scouting phase, not a soft target. Resolves plan §10.1.

**Driver:** User chose **B** over my recommended **A** (N=3). User's reasoning (implicit from the selection plus plan's §6.2 language about "locate → inspect → confirm" shapes): N=3 truncates realistic investigation shapes before a confirmation pass, forcing the first `codex.dialogue.reply` to ship with provisional context.

**Alternatives considered:**

- **A) N=3 hard cap** (plan's initial target and my recommendation). Rejected because it aligns poorly with real-world "locate → inspect → confirm" shapes.
- **C) N=3 soft target, cap at 5.** Rejected because soft targets erode §9.2's mitigation — growth past N becomes orchestrator discretion rather than a deliberate code change.
- **D) Structured budget (e.g., 1 Grep + 2 Reads + 1 Glob).** Rejected as prescriptive; doesn't match real investigation shapes.

**Implication:** Orchestrator body (task 3 in the task list) pins N=5 as a named constant. `scripts/clean_stale_shakedown.py` is unaffected. The inline scouting prose block the orchestrator produces is based on up to 5 read-surface tool calls before `codex.dialogue.start`.

**Trade-offs accepted:** Slightly more tokens consumed per dialogue run (up to 2 additional tool calls). §9.2 risk ("inline scouting grows into briefing subsystem") mitigation depends on the cap remaining hard — soft-target creep is the failure mode the cap prevents.

**Confidence:** Medium-high (E2) — reasoned through realistic investigation shapes + user's deliberate choice over my recommendation. Triangulated via concrete scouting example in Phase 5.

**Reversibility:** High. N is a single authoring-time constant in `dialogue-orchestrator.md`. Bumping to N=7 or reducing to N=3 post-v1 is a one-line edit.

**Change trigger:** If v1 objectives consistently terminate inline scouting short of usable prose at N=5, next packet raises N deliberately. If scouting routinely stops at 2-3 calls, the cap was non-binding and can be lowered.

### Decision 2: Flag vocabulary — zero flags in v1 (user-selected)

**Choice:** `/dialogue <objective>` is the entire invocation surface. No flags, no optional positional arguments. Resolves plan §10.2.

**Driver:** User chose **A** (my recommended option). Reasoning: plan §3.1 already commits to flags being implementation detail, not contract points. YAGNI — none of the §10.2 candidates (`--profile`, `--paths`, `--budget`) has a concrete consumer in v1.

**Alternatives considered:**

- **B) One flag — `--paths`.** Rejected because no concrete invocation friction has been observed. Pre-emptive flag vocabulary may lock in syntax we'd later regret.
- **C) All three flags.** Rejected because it inflates the bootstrap-test and skill-parsing surface without evidence of need.

**Implication:** The `/dialogue` skill's invocation handler (task 4) captures the full post-command string as `<objective>`. No flag tokenization. Skill's `allowed-tools` frontmatter stays minimal. Any future flag is additive — a new pattern with defaulted handler, no breaking change.

**Trade-offs accepted:** Users cannot override scouting budget, pin explicit paths, or select a profile for v1. Operator remediation for these is either "work within the defaults" or "wait for flags in post-v1 packets."

**Confidence:** High (E2) — plan §3.1 already committed to this posture; user confirmed; no dissenting evidence.

**Reversibility:** High. Adding a flag post-v1 is additive.

**Change trigger:** First real invocation friction — e.g., an objective where the inline scouting can't find the relevant surface blind, making `--paths` warranted. That friction identifies which flag is actually needed.

### Decision 3: Synthesis serialization — hybrid view-over-canonical-JSON (user-selected with refinement)

**Choice:** `/dialogue` skill surfaces the orchestrator's artifact as a human-readable summary followed by the full raw artifact in a `json` fence labeled "Canonical Artifact." The Markdown above is a view; the JSON is source of truth. Resolves plan §10.3.

**Driver:** User's verbatim refinement: *"C, with one refinement: make it a thin human wrapper over a canonical JSON appendix, not a second full rendering of every field."* And: *"Treat the JSON appendix as the source of truth. The Markdown above it is a view, not a second artifact."* And: *"Do not depend on 'collapsible' behavior unless the renderer is known to support it."*

**Alternatives considered:**

- **A) Raw JSON only.** Rejected because it optimizes for a parser that doesn't exist in v1 per §7.2.
- **B) Markdown only.** Rejected because it discards the canonical artifact, forcing any future consumer (including user's own downstream use) to reconstruct it.
- **C without refinement** (my original C): hybrid with full markdown rendering of every field. Implicitly rejected via the user's refinement — "second full rendering" creates two artifacts competing for authority.

**Implication:** The `/dialogue` skill body (task 4) specifies two things: (1) a Markdown summary section rendering key fields for readability, (2) a JSON appendix block containing the full artifact. The Markdown must be a projection of the JSON — never compute a field differently between the two. Plain fenced JSON, not `<details>`-wrapped (portable across terminal / piped output / plain text logs).

**Trade-offs accepted:** Slightly more chat-message verbosity (both views in one message). Authoring cost of specifying both views in the skill body.

**Confidence:** High (E3) — triangulated against plan §3.2 (artifact schema), §7.2 (deferred consumer migration), and user's explicit refinement. The canonical/view discipline preserves downstream optionality.

**Reversibility:** Medium. Reshaping the Markdown summary is cheap (skill edit). **Reversing the canonical/view discipline** (allowing Markdown to drift from JSON) is a contract change, not a stylistic change — any future cross-model parser would break.

**Change trigger:** First cross-model consumer ingests the artifact (the §7.2 deferral trigger). At that point, review whether JSON appendix shape still matches cross-model's `event_schema.VALID_MODES` and adjust.

### Decision 4: §10.4 crash recovery — explicit deferral with named remediation

**Choice:** No v1 design for orchestrator crash recovery. Happy-path targeting per §10.4's own framing. Operator remediation uses the pre-existing 24h stale-state sweep via `scripts/clean_stale_shakedown.py`.

**Driver:** Plan §10.4 itself: *"Recovery semantics on orchestrator crash (low-impact; v1 targets happy path)."* No user override.

**Alternatives considered:**

- **Design partial recovery in v1.** Rejected because it expands v1 scope with no concrete failure mode observed. Pattern-matches to §9.2's "growing into briefing subsystem" trap — solving a non-current problem.
- **Design full recovery semantics.** Rejected as explicit scope creep — remaining-T-04 work.

**Implication:** If orchestrator crashes mid-run, residual state (active-run pointer, possibly scope file, partial transcript) remains on disk. Operator deletes stale pointer manually or waits for the 24h sweep. Same remediation path shakedown-b1 already documents.

**Trade-offs accepted:** No automated recovery. Operators hitting a crash hit the manual path.

**Confidence:** High (E2) — plan §10.4 pre-established the deferral; session confirmed no trigger to revisit.

**Reversibility:** High. Recovery semantics can be designed post-v1 when a real crash surfaces.

**Change trigger:** First non-happy-path crash during v1 usage.

### Decision 5: Artifact form — separate companion doc, not inline plan edits

**Choice:** Write a companion addendum at `docs/plans/2026-04-14-t04-v1-authoring-decisions.md` and add a pointer from plan §10. Do NOT edit §10's item list inline.

**Driver:** User chose **Q** (my recommended option). *"Artifact form: Q (companion doc). Link directly to the companion doc from the plan."*

**Alternatives considered:**

- **P) Inline edits to plan §10.** Rejected because it modifies an already-approved, already-merged plan. The plan is the contract; the addendum is the ledger against that contract.

**Implication:** Plan stays frozen as the approved baseline. Companion carries authoring resolutions. Future tooling keys on the companion's machine-readable frontmatter (`parent_plan`, `closes`, `defers`).

**Trade-offs accepted:** Reader has to follow a one-hop pointer to find resolutions. Mitigated by the pointer being in §10's header.

**Confidence:** High (E2) — user validated the recommendation; consistent with the prior session's "preserve approved baseline" ethos.

**Reversibility:** Medium. Could be inlined later (rewriting §10 into its resolutions), but the separation is the load-bearing feature — reversing loses it.

**Change trigger:** A remaining-T-04 rewrite that naturally folds the addendum in or obsoletes it.

### Decision 6: Process deviation — skip writing-plans invocation

**Choice:** Do not invoke the brainstorming skill's terminal `writing-plans` step. The existing merged plan's §12 + the 8-task list already constitute the implementation plan.

**Driver:** Skill's "terminal state is invoking writing-plans" is framed for greenfield brainstorms producing fresh specs. Here the parent plan exists, is approved, and §12 sequences implementation. A fresh writing-plans pass would recompute the same seven steps. User agreed: *"I agree to skip the writing-plans invocation."*

**Alternatives considered:**

- **Run writing-plans.** Rejected as duplicative given existing §12 + task list.

**Implication:** Next action after this handoff is task 2 (extract reference doc), not a planning step. Brainstorming skill's spirit (one question at a time, alternatives, YAGNI) applied; its artifact shape (fresh spec) substituted with the lightweight addendum.

**Confidence:** High (E2) — user's explicit agreement plus the pre-existing §12 make this unambiguous.

**Reversibility:** Trivial — if a fresh plan is later desired, writing-plans is always available.

**Change trigger:** A scope expansion that breaks §12's sequence (unlikely in v1).

### Decision 7: Task list shape — §12 order with branch-setup prefix

**Choice:** Create 8 tasks: task 1 = create feature branch, tasks 2-8 = plan §12 steps 1-7.

**Driver:** Branch protection hook per `.claude/rules/workflow/git.md` blocks Edit/Write on `main`. Branch creation is a precondition, not a §12 step, so it's a prefix.

**Alternatives considered:**

- **Skip task 1; assume branch setup is "housekeeping."** Rejected because it silently breaks the first authoring task when Edit is blocked.
- **Embed branch creation in task 2.** Rejected because branch creation is a distinct preconditional gate with its own completion signal.

**Implication:** Task list mirrors §12 almost exactly. Easy to audit against the plan.

**Confidence:** High (E2) — aligned with plan §12.

**Reversibility:** Trivial — task list is session-scoped.

**Change trigger:** N/A.

## Changes

### `docs/plans/2026-04-14-t04-v1-authoring-decisions.md` (NEW, 104 lines)

**Purpose:** Authoring-time ledger recording resolutions of plan §10 items. Implementation-time authority for the four §10 decisions; parent plan remains authority for everything else.

**Approach:** Structured markdown with frontmatter including machine-readable `parent_plan`, `closes`, `defers` fields. Each of the three resolved decisions has: resolution, applies-to (authoring target file), rationale, alternatives-rejected with reasons, reversibility, change-trigger. Decision 4 (crash recovery) is explicit deferral with operator-remediation path. Cross-references table at the end lists every plan section touched and every authoring target file.

**Key authoring detail:** Decision 3's "canonical/view discipline" is the load-bearing constraint beyond v1 — it constrains any future consumer. Reversibility framed as "medium, with the discipline as foundational" to signal that reopening it is a contract change.

**Key authoring detail:** Decision 1's "What does NOT count against the budget" table explicitly enumerates the four non-budget call types (`codex.dialogue.*`, per-turn scouting, `Agent` dispatch, `codex.dialogue.start`) to prevent boundary drift when the orchestrator is authored.

### `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md` (MODIFIED, +5 lines net)

**Purpose:** Add a pointer from plan §10 to the companion addendum.

**Approach:** Minimally invasive — added a note at the §10 header, preserved the four-item list as contract-closure context. The items stay readable as the contract the companion closes against; the resolutions are one hop away.

**Diff:** 5 lines inserted at `§10` opening paragraph. Line 560 area. No other changes.

## Codebase Knowledge

### Files read this session

| File | Range | Purpose | Key finding |
|---|---|---|---|
| `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md` | full (632 lines) | Baseline for implementation | Approved plan; §12 is the 7-step order; §10 has four deferred authoring questions; §4 ownership table shows six owned activities for `/dialogue` |
| `docs/handoffs/archive/2026-04-13_23-12_*.md` | full | Session continuation context | Prior session landed plan at `main@73f8c9c1`; task-list handoff was captured but no task tracking started |
| `packages/plugins/handoff/skills/save/synthesis-guide.md` | full | Handoff authoring reference | 8-element decision template, 13 required sections, 500+ line target |
| `packages/plugins/handoff/references/handoff-contract.md` | full | Handoff frontmatter schema | `session_id`, `type: handoff`, `resumed_from` protocol; handoffs are gitignored local-only working memory |
| `packages/plugins/handoff/references/format-reference.md` | full | Section depth targets | 13 required sections; depth minimums per section |

### Plan structure (re-confirmed from §12)

| Step | What | Target file | Dependencies |
|---|---|---|---|
| 1 | Extract turn-semantics reference doc | `packages/plugins/codex-collaboration/references/dialogue-turn-contract.md` | None (source: current `dialogue-codex/SKILL.md`) |
| 2 | Author dialogue-orchestrator agent | `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md` | Reference doc (step 1); uses N=5 from addendum Decision 1 |
| 3 | Author `/dialogue` user skill | `packages/plugins/codex-collaboration/skills/dialogue/SKILL.md` | Orchestrator (step 2); zero-flag parser (addendum Decision 2); hybrid serialization (addendum Decision 3) |
| 4 | Extend `hooks.json` matchers | `packages/plugins/codex-collaboration/hooks/hooks.json` | Orchestrator (step 2) — matcher names it |
| 5 | End-to-end verification | - | All of 1-4 |
| 6 | 14-item rubric inspection | - | Verification transcript from step 5 |
| 7 | 566-test shakedown suite passes | - | All changes merged locally |

### Addendum frontmatter conventions

The addendum uses machine-readable frontmatter that future tooling can key on:

| Field | Value | Purpose |
|---|---|---|
| `parent_plan` | Path to the parent plan | Document relationship |
| `closes` | List of §10 items resolved | Scanning for "what resolved §10.X?" |
| `defers` | List of items explicitly deferred | Scanning for "what's still deferred?" |
| `status` | `Approved` | Consistency with parent-plan convention |

### Git state progression this session

| When | Branch | HEAD | Working tree |
|---|---|---|---|
| Session start | `main` | `73f8c9c1` | clean |
| After task 1 | `feature/t04-v1-implementation` | `73f8c9c1` | clean |
| After addendum write | same | `73f8c9c1` | 1 modified + 1 untracked |
| After commit | same | `30edf38a` | clean |

## Context

### Mental model for this session

This session exercised the **"implementation-time ledger against an approved plan"** pattern. The plan is frozen — authoritative, merged, signed. But plans inevitably defer implementation-time choices (flag vocabulary, budget constants, serialization). The naive approach inlines resolutions into the plan; the disciplined approach adds a companion doc with frontmatter that points back to the plan.

**Why the distinction matters.** Plans get reviewed. If §10 is inlined with resolutions, the plan's review evidence (three adversarial rounds plus clean-pass) no longer covers what's in the file. A companion doc keeps the review evidence intact and documents what *authoring* resolved separately.

**Analogy.** Legal: the plan is the contract; the addendum is a side letter that resolves contractually-ambiguous terms at execution-time. Neither invalidates the other; they compose.

### Position in the T-04 v1 packet arc

| Session | Role | Artifact |
|---|---|---|
| 2026-04-13 18:50 | Gap analysis + turn semantics closure | T-20260410-01/02 closed |
| 2026-04-13 19:45 | v1 scoping plan first draft | 518 lines (pending review) |
| 2026-04-13 22:09 | v1 scoping plan rewrite | 591 lines (three-round re-minimization) |
| 2026-04-13 23:12 | v1 scoping plan approval + merge + push | 632 lines, `main@73f8c9c1` |
| **2026-04-14 12:55 (this)** | **§10 authoring decisions resolved** | **addendum committed, `feature/t04-v1-implementation@30edf38a`** |
| Next | Author the four v1 surfaces | reference doc + orchestrator + skill + hooks edit |

### Environment state

- **Branch:** `feature/t04-v1-implementation` from `main@73f8c9c1`. Not pushed.
- **Commit:** `30edf38a` on the feature branch. Not merged.
- **Working tree:** clean.
- **Session state file:** will be cleaned up by this handoff via `trash`.
- **Task tracking:** 8 tasks, task 1 completed, tasks 2-8 pending.

### Why brainstorming-before-authoring was the right call

I framed this briefly in Phase 3 but it deserves a mental-model capture. The session's §10 items interact:

- Decision 2 (zero flags) influences Decision 1 (budget is not overridable by flag) and Decision 3 (serialization is not switchable by flag).
- Decision 3's canonical-JSON discipline influences what fields the orchestrator computes (Decision 1's scouting is reflected in the artifact's `final_synthesis`).

Sequential resolution without brainstorming would have meant authoring orchestrator → discovering Decision 2 constrains Decision 1 → revisiting Decision 1. Brainstorming-first collapses the interaction graph into one phase.

## Learnings

### The "approved plan + implementation addendum" pattern

**Mechanism.** An approved plan can legitimately have deferred authoring-time questions (§10 in this plan). Inlining resolutions into the plan post-approval dilutes review evidence — the plan's clean-pass review no longer covers what's in the file. A companion addendum with machine-readable `parent_plan` / `closes` / `defers` frontmatter keeps the plan's review-state intact and provides a scannable resolution trail.

**Evidence.** This session wrote `docs/plans/2026-04-14-t04-v1-authoring-decisions.md` and added a 5-line pointer to plan §10 rather than rewriting §10. User agreed: *"Link directly to the companion doc from the plan."* Pattern preserves the plan's three-round-adversarial + clean-pass review evidence while making resolutions one hop away.

**Implication.** Any future program in this repo with similar structure (approved plan + deferred authoring choices) should follow this pattern. The frontmatter key names (`parent_plan`, `closes`, `defers`) are worth standardizing across future addenda.

**Watch for.** If `closes` and `defers` frontmatter fields become common, consider a scanner script to verify every "deferred in plan X" has a matching "closed in addendum Y" — currently this requires manual pairing.

### Brainstorming skill's terminal-state instruction is greenfield-shaped

**Mechanism.** The brainstorming skill says "the terminal state is invoking writing-plans." This assumes a blank-slate brainstorm where no plan exists yet. For sessions that brainstorm *within* an already-approved plan (implementation-time decisions), a fresh writing-plans pass duplicates the existing plan's §12 sequencing.

**Evidence.** This session would have produced a redundant plan covering the same 7 §12 steps the approved plan already has. User agreed to skip: *"I agree to skip the writing-plans invocation."* The brainstorming skill's spirit (structured inquiry, alternatives, YAGNI) applies; the artifact shape does not.

**Implication.** Future sessions that invoke brainstorming for a sub-decision within an approved plan should explicitly flag the process deviation up-front rather than treating the terminal-state instruction as mandatory. The skill should perhaps distinguish "greenfield brainstorm" from "sub-decision brainstorm within existing spec" — an authoring improvement for the brainstorming skill itself, not a runtime concern.

**Watch for.** Over-applying the greenfield shape to sub-decision brainstorms. Signs: considering a "new design spec" alongside an existing approved plan, or producing writing-plans output that duplicates an existing §12.

### User's "refine my option" pattern beats "accept as offered"

**Mechanism.** When I offered options A/B/C for serialization, my recommendation (C) was directionally right but structurally incomplete. User replied: *"C, with one refinement..."* — accepting the direction while correcting a structural flaw. The refinement (canonical/view discipline) turned out to be load-bearing.

**Evidence.** User's original response captured explicitly: *"Treat the JSON appendix as the source of truth. The Markdown above it is a view, not a second artifact."* This wasn't in my option C as stated; my C allowed "second artifact" drift. The refinement eliminated that.

**Implication.** When presenting options, I should pre-surface structural constraints the user might reasonably add. For this decision: I could have said "C, and the Markdown is a projection of the JSON (canonical/view discipline)." Would have saved one turn.

**Watch for.** Multi-option presentations where an option's "natural" extension is omitted. If the user would reasonably refine the option, I should pre-include the refinement or explicitly flag it as a sub-decision.

### Protected-branch hook forces branch-creation as a discrete task

**Mechanism.** `.claude/rules/workflow/git.md` documents that the PreToolUse hook blocks Edit/Write on `main`. This means any implementation session starting from `main` must create a feature branch *before* any authoring tool call. It's not housekeeping — it's a precondition with its own completion signal.

**Evidence.** This session's task 1 = "Create working branch feature/t04-v1-implementation from main." If I'd tried to Write the addendum on `main`, the hook would have blocked. Creating the branch was a non-trivial distinct step.

**Implication.** Future implementation session task lists should always include branch-creation as task 1 when starting from a protected branch. Treating it as implicit risks a mid-task block.

**Watch for.** Task lists that begin with an Edit/Write task without a preceding branch check. If the current branch is `main` / `master`, task 1 must be branch creation.

## Next Steps

### 1. Extract turn-semantics reference doc from dialogue-codex (task 2)

**Dependencies:** None — parent plan's §12 step 1. Branch already set up.

**What to read first:**
1. `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md` (source of extraction; study full body).
2. Plan §4 ownership table row for reference doc (production-local authority in v1).
3. Plan §9.3 risk (zero-behavioral-edits discipline — reference doc must preserve current `dialogue-codex` turn semantics byte-for-byte).

**What to write:** `packages/plugins/codex-collaboration/references/dialogue-turn-contract.md`. Must capture: target selection, claim classification, status derivation, disposition enum, emission shape (13 fields per `dialogue-codex/SKILL.md:252-268`), terminalization with T1-enum `termination_code` values (lowercase literals `convergence`, `budget_exhausted`, `scope_breach`, `error`), budget semantics, Risk-F/G/J/K invariants, T1-T6 semantic adoption.

**Approach suggestion:** Read `dialogue-codex/SKILL.md` in full first. Identify the per-turn contract boundaries (likely sections on turn execution, state emission, terminalization). Extract those into the reference doc as normative prose. Leave behavioral text untouched — this is a literal extraction, not a rewrite.

**Acceptance criteria:** Reference doc cites all accepted T1-T6 semantics. No behavioral divergence from current `dialogue-codex` body. `dialogue-codex/SKILL.md` stays byte-for-byte unchanged (per plan §8.4 boundary invariant).

**Potential obstacles:**
- Risk of rewording semantics during extraction — must be literal.
- Current `dialogue-codex` body mingles shakedown-flow guidance with turn-semantics contract; extraction must not carry over shakedown-specific language.

### 2. Author dialogue-orchestrator agent body (task 3)

**Dependencies:** Reference doc (task 2) exists.

**What to read first:**
1. Reference doc from task 2.
2. `packages/plugins/codex-collaboration/agents/shakedown-dialogue.md` (precedent for agent-body structure).
3. Addendum Decision 1 (N=5 scouting budget, hard cap on combined Read+Grep+Glob).
4. Plan §6.2 (inline scouting rules).
5. Plan §3.2 (production synthesis artifact schema).

**What to write:** `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md`. Body cites the reference doc for per-turn loop. Includes inline initial scouting phase with N=5 hard cap. Emits production synthesis artifact per §3.2.

**Acceptance criteria:** Agent body references the reference doc (not `dialogue-codex`). N=5 constant is named explicitly in the body. Synthesis artifact schema matches §3.2 field list exactly.

**Potential obstacles:**
- Scouting budget must be a named constant, not hardcoded — makes future N-bump a one-line edit.
- Must NOT dispatch other agents during scouting (breaks single-contained-subagent invariant per §2.1.2).

### 3. Author /dialogue user skill (task 4)

**Dependencies:** Orchestrator agent exists (task 3).

**What to read first:**
1. Orchestrator agent body from task 3.
2. `packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md:35-45` (preflight cleanup precedent).
3. Addendum Decision 2 (zero flags) and Decision 3 (hybrid serialization with canonical JSON).
4. Plan §6.1 step 1 (preflight sweep, live-run check, seed write).
5. Plan §8.4 bootstrap-boundary invariant (`allowed-tools` must exclude `codex.dialogue.*`).

**What to write:** `packages/plugins/codex-collaboration/skills/dialogue/SKILL.md`. Body owns invocation parsing (zero flags), preflight cleanup via `clean_stale_shakedown.py`, shared-namespace single-run check, parent-owned active-run + seed write with `scope_directories=[<repo_root>]`, orchestrator dispatch via `Agent`, synthesis surfacing with Markdown summary + JSON appendix.

**Acceptance criteria:** `allowed-tools` frontmatter does NOT include any `codex.dialogue.*` MCP tools (plan §8.4 invariant). Invocation parser is a single capture — no flag tokenization. Surfacing section specifies both Markdown view and `json`-fenced Canonical Artifact.

**Potential obstacles:**
- `allowed-tools` frontmatter must be minimal. Current `test_bootstrap.py:256` is the repo-level gate.
- Must invoke `clean_stale_shakedown.py` BEFORE live-run check (mirror shakedown-b1 step 4) — otherwise stale state trips the check before cleanup can fire.

### 4. Extend hooks.json matchers (task 5)

**Dependencies:** Orchestrator agent named (task 3).

**What to read first:**
1. `packages/plugins/codex-collaboration/hooks/hooks.json` (current matcher lines 15 and 26).
2. Plan §7.1 (matcher extension detail with before/after).
3. Plan §9.1 (silent-defeat risk).

**What to write:** Edit `hooks.json`. Change both SubagentStart and SubagentStop matchers from `"shakedown-dialogue"` to `"shakedown-dialogue|dialogue-orchestrator"`.

**Acceptance criteria:** Both matchers updated. Running existing lifecycle tests still passes.

**Potential obstacles:**
- Silent defeat if missed — plan §9.1 mentions this explicitly.
- Regex form vs two-entry form — plan §7.1 allows either.

### 5-7. Verification steps (tasks 6-8)

**Dependencies:** All authoring tasks complete.

Per plan §8.2 and §8.3: representative `/dialogue <objective>` invocation, hook-firing verification, transcript inspection (13-field shape), production synthesis field checks (mode="agent_local", mode_source=null), scope-breach evidence paths, 14-item rubric pass, 566-test shakedown suite unchanged.

## In Progress

**Clean stopping point — §10 decisions resolved, addendum + pointer committed. No work in flight.**

- **Approach:** Brainstorm-first pattern closed out 4 of 4 §10 items (3 resolved, 1 explicitly deferred). Addendum captures resolutions; pointer from plan §10 keeps baseline intact.
- **State:** complete for this sub-phase. Commit `30edf38a` on `feature/t04-v1-implementation`; working tree clean.
- **Working:** addendum frontmatter machine-readable; pointer in plan §10 minimally invasive; commit follows conventional-commits style; self-review passed four brainstorming-skill checks.
- **Not working:** nothing broken.
- **Open question:** whether next session begins task 2 (reference doc extraction) immediately, or pauses for merge authorization first. Branch is unmerged and unpushed by design — user's commit-merge-push-separate-authorizations pattern.
- **Next action:** User decides — proceed to task 2 (reference doc extraction) on the feature branch, OR authorize merge of `feature/t04-v1-implementation` into `main` first, OR push the feature branch, OR pause.

## Open Questions

### 1. Merge and push timing for the addendum commit

**Context:** Commit `30edf38a` is on `feature/t04-v1-implementation` only. Parent session's handoff shows the user's pattern: three separate authorizations for commit, merge, push. Only the commit has been authorized so far this session.

**Impact:** Low — a feature branch commit is harmless. But the merge/push decision is a session-level authorization that shouldn't be assumed.

**Options:**
- Merge the addendum now (small, self-contained doc change) before authoring the four v1 surfaces.
- Hold all four authoring tasks + addendum under one merge at v1 completion.
- Keep addendum on the feature branch until merge authorization — next session asks.

### 2. Whether the bootstrap test should be renamed as part of v1

**Context:** Parent handoff flagged `test_bootstrap.py::test_no_user_invocable_dialogue_skill_exists` as reading broader than its body asserts. Plan §8.4 makes the boundary explicit but doesn't rename the test.

**Impact:** Low — v1 works without the rename. But the broad-name-vs-narrow-body asymmetry invites future misreading.

**Decision pending until:** v1 implementation done and user prioritizes post-v1 cleanup (plan §7.2 lists similar items).

## Risks

### 1. Hook-matcher extension silently omitted during implementation

**Impact:** Plan §9.1 risk — if the orchestrator is authored and the skill is authored but `hooks.json` matchers aren't extended, the containment lifecycle never fires for production runs. Silent defeat.

**Mitigation:** Task 5 is its own task (not a sub-step). §8.3 verification check 1 tests hook firing explicitly. Plan §7.1 names before/after for the edit.

### 2. Reference doc drifts from dialogue-codex during extraction

**Impact:** Plan §9.3 risk — reference doc is authored at task 2 start by extraction from current `dialogue-codex` body. Wording drift during extraction means shakedown and production run against semantically different contracts.

**Mitigation:** Zero-behavioral-edits discipline during extraction. Literal extraction, not rewrite. Plan §9.3 commits to this.

### 3. /dialogue allowed-tools drift trips bootstrap test

**Impact:** Plan §8.4 invariant — if `/dialogue` skill's `allowed-tools` gains any `codex.dialogue.*` entry, `test_bootstrap.py` trips.

**Mitigation:** Addendum Decision 2 (zero flags) keeps the skill's tool surface minimal. Task 4 acceptance criteria includes this explicit check. Plan §8.4 invariant naming.

### 4. Preflight cleanup call-site mismatch

**Impact:** Plan's `/dialogue` step 1 assumes `scripts/clean_stale_shakedown.py` invocation works the same from `/dialogue` as from `shakedown-b1`. If the script has caller-specific assumptions, `/dialogue` invocation could silently fail to sweep.

**Mitigation:** Task 4 implementation should test the preflight invocation in isolation before integrating. Parent handoff flagged this explicitly.

### 5. Stale run younger than 24h blocks live-run check

**Impact:** `clean_stale_shakedown.py` uses a 24h threshold. Crashed run younger than 24h won't be swept; subsequent live-run check fails fast. Inherited infrastructure behavior.

**Mitigation:** Plan §5.2 documents this. Not a new v1 risk.

### 6. §9.4 risk — zero-behavioral-edits discipline for dialogue-codex during v1

**Impact:** Any hotfix or clarification to per-turn semantics during v1 must land in both `dialogue-codex` and the reference doc in the same commit, or they diverge.

**Mitigation:** Plan §9.3 commits to this. V1 is a short packet — discipline is tractable. Remaining-T-04 closure factors `dialogue-codex` to an adapter, eliminating the risk structurally.

## References

### This session's commit

- `30edf38a` on `feature/t04-v1-implementation` — docs(plan): record T-04 v1 authoring-time decisions addendum

### Files authored or modified

- `docs/plans/2026-04-14-t04-v1-authoring-decisions.md` (NEW, 104 lines, Approved)
- `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md` (+5 lines net; §10 pointer)

### Parent plan + prior authority

- Parent plan: `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`
- Supersession ticket: `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md`
- T1 contract (termination): `docs/plans/2026-04-02-t04-t1-structured-termination-contract.md`
- T2-T8 prior plans cited in parent plan §13

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-13_23-12_t04-v1-plan-approved-merged-pushed-implementation-unblocked.md`
- Prior: `docs/handoffs/archive/2026-04-13_22-09_t04-v1-plan-rewritten-after-three-scrutiny-rounds.md`

### Code surfaces (read during plan re-read, not yet modified)

- `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md` (reference doc extraction source)
- `packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md` (preflight precedent + rubric source)
- `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py`
- `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py`
- `packages/plugins/codex-collaboration/scripts/containment_guard.py`
- `packages/plugins/codex-collaboration/hooks/hooks.json` (matcher extension target)
- `packages/plugins/codex-collaboration/tests/test_bootstrap.py` (boundary gate)

### Skill references used this session

- `superpowers:brainstorming` (invoked; process adjusted for sub-decision-within-existing-plan shape)
- `handoff:load` (session start)
- `handoff:save` (this handoff)

## Gotchas

### Addendum modifies baseline only via pointer, not inline rewrite

**Symptom:** Future-Claude or user expects to see §10 resolved in plan body.

**Root cause:** Deliberate design choice — plan stays frozen as approved baseline; addendum carries resolutions. Pointer in §10 header names the addendum.

**Prevention:** This handoff captures the decision explicitly. Future readers land on §10, see the pointer, follow it. If they miss the pointer, the list of four items (unresolved-looking) reads as if §10 is still open — which it isn't.

### N=5 differs from plan's N=3 initial target

**Symptom:** Future-Claude reads plan §6.2 ("initial target N=3"), assumes N=3, authors orchestrator with that constant. Would be mechanically wrong per addendum Decision 1.

**Root cause:** Plan §6.2 captures the initial target; addendum Decision 1 is the authoritative resolution.

**Prevention:** Addendum's frontmatter `closes: "§10.1 — inline scouting budget"` flags the resolution. Plan's §10 header points to addendum. Author of task 3 must read addendum before pinning N.

### Canonical/view discipline is load-bearing beyond v1

**Symptom:** Future-Claude authors the `/dialogue` skill's surfacing section with Markdown fields computed differently from the JSON artifact fields (e.g., rounding numbers, reformatting citations).

**Root cause:** Decision 3 says Markdown is a view; JSON is source of truth. Any computation divergence breaks the invariant.

**Prevention:** Addendum Decision 3 names "Markdown is projection of JSON" explicitly. Task 4 acceptance criteria should include a check: every Markdown field is a transparent rendering of the corresponding JSON field.

### Don't depend on `<details>` collapsible rendering

**Symptom:** Author wraps the JSON appendix in `<details><summary>...</summary> ... </details>` and assumes that's sufficient for the "appendix" framing.

**Root cause:** Claude Code's terminal, piped output, and plain-text logs may all strip collapsible sugar. Content invariants must hold regardless of rendering.

**Prevention:** Addendum Decision 3 says *"Plain fenced JSON is portable ... Collapsible sugar is a rendering hint at best — if used, it must remain cosmetic; the content inside must be the canonical artifact whether rendered collapsed or expanded."* Task 4 authoring should default to plain ` ```json ``` ` fence; `<details>` is optional cosmetic wrapping, not part of the contract.

### Feature branch unpushed and unmerged by design

**Symptom:** Someone pulls `main`, doesn't see the addendum. Worries the commit was lost.

**Root cause:** Per user's commit-merge-push-separate-authorizations pattern (captured from parent handoff), only commit has been authorized. Merge and push await next authorization.

**Prevention:** This handoff's "In Progress" section says so explicitly. Branch is `feature/t04-v1-implementation@30edf38a`; `main` still at `73f8c9c1`.

## Conversation Highlights

### User's scope reframe at session start

Verbatim:

> "I'd prefer to start with brainstorming the §10 decisions up front before authoring"

This single message changed the session shape from "read plan → create tasks → start task 1 (branch) → task 2 (authoring)" to "read plan → create tasks → brainstorm §10 → write addendum → commit → handoff, authoring deferred to next session." A scope-narrowing move that front-loaded the interacting decisions before any code-like authoring.

### User's deliberate override on scouting budget

Verbatim:

> "I want to go with B) N=5"

My recommendation was A (N=3) on alignment-with-plan grounds. User selected B on practical-scouting-shape grounds. Not a pushback — a calibration. Pattern (from parent handoff): user rewrites their own framing when evidence warrants; here they rewrote my recommendation when intuition about realistic scouting shapes warranted.

### User's refinement on serialization

Verbatim:

> "C, with one refinement: make it a thin human wrapper over a canonical JSON appendix, not a second full rendering of every field."
>
> "Treat the JSON appendix as the source of truth. The Markdown above it is a view, not a second artifact."
>
> "Do not depend on 'collapsible' behavior unless the renderer is known to support it. In this environment, a plain fenced appendix is the safe default; `<details>` is optional sugar, not part of the contract."

The refinement added a structural constraint (canonical/view discipline) that my option C didn't carry. The three paragraphs above are the addendum Decision 3 contract in miniature — added to the addendum essentially verbatim.

### User's clarifying question pattern

Verbatim:

> "what exactly is the scouting budget?"

Asked mid-decision-sequence. Revealed that the user wanted the concept anchored concretely before selecting. I delivered a phase-breakdown + concrete example + budget/non-budget table. User then chose deliberately. Pattern: when asked to choose among options for an underspecified concept, the right move is to over-explain the concept first (at moderate length), then re-offer the options.

### User's sequenced workflow instruction

Verbatim:

> "Artifact form: Q (companion doc). Link directly to the companion doc from the plan. Also, I agree to skip the writing-plans invocation"

One message, three decisions. Minimum-word, maximum-information. Aligns with the parent handoff's User Preferences observation ("User's commit-sequence pattern: three consecutive authorized steps, each explicit. Each step separately authorized. User does not bundle.") — here three decisions *are* bundled because they're all low-risk acceptances of my recommendations, not commit-style actions.

### User's commit + handoff authorization

Verbatim:

> "Both files are approved. Commit both changes, then save a handoff"

Two-step authorization: commit, then save. Not merge, not push — those await separate authorization. Matches the commit-merge-push separation pattern precisely.

## User Preferences

### Brainstorm before authoring when decisions interact

**Verbatim (this session):** *"I'd prefer to start with brainstorming the §10 decisions up front before authoring"*

**Pattern:** When multiple related implementation-time decisions exist, the user prefers to resolve them in a dedicated phase *before* any authoring. Reason (inferred from the shape of this session): authoring-then-revisiting creates churn; brainstorming-first collapses the interaction graph.

### Refine options rather than accept-as-stated

**Verbatim (this session):** *"C, with one refinement..."*

**Pattern:** When offered options, the user sometimes accepts the direction but corrects a structural flaw. Refinements from this session were load-bearing (canonical/view discipline is the most durable constraint in the addendum). Future sessions should pre-surface structural constraints to reduce refinement turns, but refinement is welcome and valuable.

### Override my recommendation with practical judgment

**Verbatim (this session):** *"I want to go with B) N=5"* (my recommendation was A)

**Pattern:** User's domain intuition about practical matters (realistic scouting shape) outweighs my alignment-with-plan default. When the user overrides with a short, deliberate choice, take it at face value — don't re-recommend, just record and move on.

### Direct links over prose cross-references

**Verbatim (this session):** *"Link directly to the companion doc from the plan"*

**Pattern:** When navigating between related documents, the user prefers explicit file-path links at the relevant location, not prose like "see also X" tucked away in a conclusion. The plan §10 pointer I added is at the section *header*, not at the end — matches this preference.

### Preserve approved baselines through addenda, not inline rewrites

**Inferred pattern (from artifact-form choice):** User chose Q (companion doc) over P (inline plan edits). The approved plan is frozen; the addendum is the ledger against the plan. This preserves review evidence and keeps the plan legible as its originally-approved form.

### Commit as discrete authorization step

**Verbatim (this session):** *"Commit both changes, then save a handoff"*

**Pattern:** Commit is authorized separately from merge and push. This session: commit authorized, merge and push NOT authorized. Consistent with parent handoff's observation: *"three consecutive authorized steps, each explicit. User does not bundle."*

### Positive terse acknowledgements signal calibration

**Verbatim (this session):** *"Both files are approved."*

**Pattern:** When approval comes as a flat statement rather than detailed critique, it means the work cleared the bar without notable defects. Tone-calibration signal: keep the current working bar.

### Prefer evidence-backed partial pushback over blanket framing

**Pattern carried from parent handoff, validated this session:** When my recommendation is directionally right but incomplete, user refines rather than rejects. The right response to partial validity is partial pushback with evidence — never full accept-as-stated (which propagates the flaw), never full rejection (which discards the correct direction).
