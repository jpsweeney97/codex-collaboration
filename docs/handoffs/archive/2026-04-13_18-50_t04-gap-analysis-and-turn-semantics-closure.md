---
date: 2026-04-13
time: "18:50"
created_at: "2026-04-13T18:50:03Z"
session_id: 237ea8dc-e2ec-4d4d-a80f-2bb56f710356
resumed_from: docs/handoffs/archive/2026-04-13_17-30_t02-t03-closed-t04-t05-unblocked.md
project: claude-code-tool-dev
branch: main
commit: 72c66714
title: "T-04 gap analysis complete, T-20260410-01 turn semantics closed"
type: handoff
files:
  - packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md
  - packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md
  - docs/plans/2026-04-07-t7-executable-slice-definition.md
  - docs/plans/2026-04-07-t8-minimum-runnable-shakedown-packet.md
  - docs/plans/2026-04-08-t8-shakedown-execution-plan-v3.md
  - docs/plans/2026-04-09-b4-dialogue-codex-conformance-checklist.md
  - docs/tickets/2026-04-10-dialogue-codex-turn-semantics-clarification.md
---

# T-04 Gap Analysis Complete, T-20260410-01 Turn Semantics Closed

## Goal

Two objectives this session: (1) perform a comprehensive gap analysis of T-20260330-04 (dialogue parity and scouting retirement) to determine whether it follows the pre-satisfied pattern of T-02/T-03 or requires real implementation, and (2) close any small open follow-up tickets before expanding the T-04 surface area.

**Trigger:** Prior session closed T-02 and T-03, unblocking T-04 and T-05. User recommended starting with T-04 over T-05 based on pre-existing scaffold (dialogue runtime, skills, shakedown harness) vs T-05's greenfield status.

**Stakes:** T-04 is the user-adoption gate for codex-collaboration — without a production dialogue surface, the plugin can't retire cross-model. The gap analysis determines whether T-04 is another verification-closure ticket or a genuine implementation sprint.

**Success criteria:** (1) Accurate gap matrix mapping all 7 acceptance criteria to implementation evidence, (2) clear understanding of what exists vs what's missing, (3) close T-20260410-01 if small enough to resolve in-session.

**Connection to project arc:** T-04 and T-05 are the fan-out pair after T-02/T-03 in the 6-ticket supersession chain. This session focused exclusively on T-04, which blocks T-07 (analytics reviewer and cutover).

## Session Narrative

**Phase 1 — Initial gap matrix (~20 min):**

Session loaded the prior handoff, which recommended T-04 over T-05. User arrived with a detailed pre-analysis of why T-04 was the better choice, citing specific file paths for existing scaffold (dialogue.py, mcp_server.py, dialogue-codex skill, shakedown-dialogue agent, shakedown-b1 skill) and noting that T-05 lacked delegate tool exposure, execution-runtime modules, or worktree manager code.

Read the T-04 ticket, the benchmark-first design plan (T0-T8 subtask structure), and the T4 scouting spec README. Then read all existing implementation files: DialogueController (989 lines), dialogue-codex skill (455 lines), shakedown-dialogue agent, shakedown-b1 skill (211 lines). Cross-referenced against cross-model semantic sources: dialogue skill, codex-dialogue agent, context-gatherer-code, context-gatherer-falsifier.

Produced initial gap matrix with 7 ACs classified as Partial/Missing/Not started.

**Phase 2 — Three rounds of user correction (~30 min):**

User provided three rounds of detailed corrections, each with specific file:line citations:

*Round 1 (3 findings):*
- T8 is not the gate to the full 8-task benchmark — it gates the broader T-04 implementation packet. The full corpus has its own prerequisite gates in benchmark-readiness.md.
- AC4 should be Partial, not Missing — dialogue-codex already has convergence/terminal machinery (SKILL.md:252, SKILL.md:307).
- Missing-work list underweights T7 harness/readiness work — benchmark-readiness.md defines transcript parser, diff engine, narrative inventory, methodology findings, etc.

*Round 2 (3 findings):*
- T8 dry-run column hard-requires more product surface than the plan commits to — the shakedown stack (shakedown-b1 + shakedown-dialogue + dialogue-codex) IS the T8 candidate loop, not a pre-T8 scaffold.
- T5 `agent_local` mode isn't just "scored-only" — benchmark-readiness.md:14 says `agent_local` runs without T5 migration surfaces are invalid.
- Gatherer port isn't just MCP rerouting — needs real scope/containment adaptation (containment.md:106, benchmark-readiness.md:267).

*Round 3 (3 findings):*
- The canonical T7/T8 docs (2026-04-07-t7-executable-slice-definition.md and 2026-04-07-t8-minimum-runnable-shakedown-packet.md) are the authoritative later artifacts — my earlier analysis was based on the design plan without finding these.
- T8 = shakedown, T5 is NOT a gate for T8. T7 boundary table explicitly says T5 migration is deferred.
- A successful live shakedown has already been run — B4 passed on commit `7f4eed41`, artifacts staged.

**Key pivot:** Each correction round narrowed the gap between my analysis and the repo's actual state. The final corrected assessment showed T-04 is much further along than the initial matrix suggested — the T8 shakedown is complete, not "not started."

**Phase 3 — T-20260410-01 closure (~15 min):**

User recommended starting with T-20260410-01 (turn-semantics clarification) before the broader packet. Chose model 2 (post-reply verification turn): first emitted state block is `turn: 2`, matching the validated B4 runtime and exemplars.

Made edits to dialogue-codex/SKILL.md (4 locations), conformance checklist (3 locations), and ticket closure. User ran code review and found P2: shakedown-b1 operator template still had no check for first emitted turn. Added checklist items 3-4, renumbered 12→14 items. Second review found P2: T7/T8 contract bodies still enumerated only 12 items. Fixed T7 checklist body, T8 downstream references, T8-v3 rubric reference. Third review: clean.

Committed at `72c66714`, merged to main, pushed to origin.

## Decisions

### Decision 1: Choose model 2 (post-reply verification turn) for `turn` semantics

**Choice:** First emitted state block is `turn: 2`. `turn: 1` is the opening send to Codex, which does not emit a state block. Emitted state begins only after a Codex reply exists to extract claims from.

**Driver:** Model 2 matches three independent evidence sources: (1) validated B4 runtime transcript emits turns 2-6, (2) both skill exemplars show `turn: 2` as first emitted block, (3) per-turn loop entry point says "after receiving a Codex reply" (`dialogue-codex/SKILL.md:38`).

**Alternatives considered:**
- **Model 1 (start at 1 with emitted non-scouting opening turn)** — would require inventing a synthetic opening emission with `scouted: false` and no claims to extract. Rejected because it adds complexity with no diagnostic value and contradicts the validated runtime. User also recommended model 2: "That fits the validated runtime and exemplars, and it avoids inventing an extra synthetic opening emission just to satisfy older prose."

**Trade-offs accepted:** The logical dialogue sequence and the emitted sequence now use different numbering — logical turn 1 is the opening send, but emitted state starts at 2. This is a minor conceptual gap, but it's well-documented and unambiguous.

**Confidence:** High (E2) — three independent evidence sources (runtime transcript, exemplars, loop entry point) all agree on model 2.

**Reversibility:** Medium — changing the turn origin would require updating 7 files (skill, conformance checklist, operator template, T7, T8, T8-v3, and any future artifacts that reference turn numbering). The contract is now locked to model 2.

**Change trigger:** If a future use case requires emitting state for the opening send (e.g., a pre-dialogue scouting phase), model 2 would need revision. Currently no such use case exists.

### Decision 2: Split parse-failure origin rule from monotonicity

**Choice:** Two separate parse-failure conditions: (1) first emitted state block has `turn != 2`, (2) non-monotonic `turn` counter on subsequent emitted turns.

**Driver:** User correction: "Make the start-value rule a separate invariant, not just a parenthetical on monotonicity. A validator could still treat first-emitted `turn: 3` as monotonic if it only sees one block."

**Alternatives considered:**
- **Single combined rule** — "Non-monotonic `turn` counter (first emitted value is 2...)". Rejected because it mixes two checks and a validator seeing only one block can't distinguish valid from invalid.

**Trade-offs accepted:** Two rules instead of one adds slight verbosity to the parse-failure section.

**Confidence:** High (E2) — the split makes both conditions independently checkable by a mechanical validator.

**Reversibility:** High — purely documentary.

**Change trigger:** If the emission protocol changes (e.g., variable start values for different shakedown types).

### Decision 3: Renumber checklist from 12 to 14 items

**Choice:** Add items 3 (first emitted turn is 2) and 4 (subsequent turn values strictly increasing) to the per-turn checks, renumber all downstream items.

**Driver:** User's code review finding: "The model-2 edits are consistent, but the actual shakedown inspection template generated by `/shakedown-b1` still has no check for the first emitted turn being `2`." The ticket's acceptance criteria claim future shakedown runs don't require operator judgment, but without explicit checklist items, that claim is overstated.

**Alternatives considered:**
- **Leave template at 12 items** — would leave a drift point where the skill contract defines model 2 but the operator template can't verify it. Rejected because the ticket's AC4 ("future shakedown runs do not require operator judgment") would not be satisfied.

**Trade-offs accepted:** Renumbering from 12 to 14 propagates through 7 files. The propagation is mechanical but easy to miss (and was missed on the first pass — required two review rounds to catch all references).

**Confidence:** High (E2) — verified all item-range references after completion.

**Reversibility:** Medium — the renumbering is now baked into multiple accepted design documents.

**Change trigger:** If checklist items are added or removed in future T-04 work.

## Changes

### `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md`

**What changed:** Four edits: (1) `turn` field rule updated from "starting at 1" to model 2 definition, (2) field table header "Every turn" → "Every emitted state block", (3) parse-failure conditions split into origin and monotonicity rules, (4) exemplar commentary clarified.

**Why:** Align contract prose with validated B4 runtime behavior. The only contradicting text was the "starting at 1" rule — everything else (loop entry point, exemplars) already implied model 2.

### `packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md`

**What changed:** Inspection template expanded from 12 to 14 items. Added items 3 (first emitted turn is 2) and 4 (subsequent strictly increasing). All downstream items renumbered. Three "12-item" string references updated to "14-item".

**Why:** The operator template is the runtime-facing enforcement surface. Without these items, the model 2 contract is documented but not operationally verifiable.

### `docs/plans/2026-04-07-t7-executable-slice-definition.md`

**What changed:** Per-turn checklist body expanded from items 1-6 to 1-8 (added turn origin and monotonicity). Terminal items renumbered 9-11 (was 7-9). Containment items renumbered 12-14 (was 10-12). Pass condition updated 12→14. Two inline checklist-item references updated (item 11→13, items 10-12→12-14).

**Why:** T7 is the accepted design authority for the inspection protocol. Its checklist body must match the operator template.

### `docs/plans/2026-04-07-t8-minimum-runnable-shakedown-packet.md`

**What changed:** Four "12-item" references updated to "14-item". Group range "(per-turn 1-6, terminal 7-9, containment 10-12)" updated to "(per-turn 1-8, terminal 9-11, containment 12-14)". Two inline references updated (items 10-12→12-14, items 1-12→1-14).

**Why:** T8 downstream references must match T7 authority.

### `docs/plans/2026-04-08-t8-shakedown-execution-plan-v3.md`

**What changed:** Single reference "12-item rubric" → "14-item rubric".

**Why:** V3 execution plan references the same checklist.

### `docs/plans/2026-04-09-b4-dialogue-codex-conformance-checklist.md`

**What changed:** Field table header "Every turn" → "Every emitted state block". `turn` field rule updated to model 2. Parse-failure section split into origin and monotonicity. B4 checks updated from single "monotonically increasing (1, 2, 3, ...)" to two items: "First emitted `turn` is 2" and "Subsequent `turn` values are strictly increasing".

**Why:** Conformance checklist is the verification duplicate of the skill contract. Must mirror the canonical source.

### `docs/tickets/2026-04-10-dialogue-codex-turn-semantics-clarification.md`

**What changed:** Frontmatter updated to `status: closed`, `closed_date: 2026-04-13`, `resolution: completed`. Resolution section added with model choice, rationale, change table (9 rows), and acceptance criteria verification (4 items).

**Why:** Ticket closure with full resolution evidence.

## Codebase Knowledge

### T-04 Design Plan Architecture (T0-T8)

The benchmark-first design plan at `docs/plans/2026-04-01-t04-benchmark-first-design-plan.md` defines a 9-step pipeline:

| Subtask | Status | Artifact |
|---------|--------|----------|
| T0: Benchmark contract pin | Done | Benchmark contract unchanged |
| T1: Structured termination | Accepted (design) | `2026-04-02-t04-t1-structured-termination-contract.md` |
| T2: Synthetic-claim handling | Accepted (design) | `2026-04-02-t04-t2-synthetic-claim-and-closure-contract.md` |
| T3: Referential continuity | Accepted (design) | `2026-04-02-t04-t3-deterministic-referential-continuity.md` |
| T4: Scouting & provenance | Accepted (design) — 10-file modular spec | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/` |
| T5: Mode strategy | Accepted (design) | `2026-04-02-t04-t5-mode-strategy.md` |
| T6: Consolidation | Closed | Composition review at `docs/reviews/2026-04-04-t04-t6-benchmark-first-design-composition-review.md` |
| T7: Executable slice definition | Defined (PR #98 merged) | `2026-04-07-t7-executable-slice-definition.md` (447 lines) |
| T8: Shakedown implementation | **Complete** — B4 passed | `2026-04-07-t8-minimum-runnable-shakedown-packet.md`, smoke log at `t8-t4-live-smoke-log.md` |

**Key insight:** T7 and T8 are the later authoritative artifacts. The design plan (T0-T6) sets the design contracts; T7 defines the executable slice; T8 implements and runs it. The design plan's session sketch (lines 71-79) estimated 6 sessions; T7/T8 compressed it.

### T-04 Naming Trap

In `benchmark-readiness.md:14`, "T5" refers to the **T-04 mode-strategy design subtask** (the 5th step in the T0-T8 pipeline), NOT supersession ticket T-20260330-05 (execution domain foundation). The two T5s are in different numbering systems. See memory file `project_t_sequence_vocabulary.md`.

### Shakedown Stack (Built and Validated)

| Component | Location | Purpose | Status |
|-----------|----------|---------|--------|
| shakedown-b1 skill | `skills/shakedown-b1/SKILL.md` | Operator-facing harness: preflight, seed, spawn, capture | Built (211 lines) |
| shakedown-dialogue agent | `agents/shakedown-dialogue.md` | Contained B1/B4 runner, loads dialogue-codex via `skills` frontmatter | Built |
| dialogue-codex skill | `skills/dialogue-codex/SKILL.md` | 7 core behaviors: claim extraction, registration, scouting, emission, failure termination | Built (455 lines) |
| Containment hooks | `hooks/hooks.json`, `scripts/containment_guard.py`, `scripts/containment_lifecycle.py` | PreToolUse guard + SubagentStart/Stop lifecycle | Built, 14 smoke scenarios passing |

The shakedown has been run successfully on B4 (commit `7f4eed41`), staging artifacts at `transcript-9f5da415-0a90-4863-a611-407d29e512f7.jsonl`.

### Benchmark Readiness Gate Structure

`benchmark-readiness.md` defines a three-tier run classification:

| Tier | Classification | Prerequisites | Can inform policy? |
|------|---------------|---------------|-------------------|
| T4-BR-08(a) | Exploratory shakedown | None | No — results non-evidentiary |
| T4-BR-08(b) | Policy-influencing calibration | All 8 T4-BR-07 prerequisites | Yes — shapes benchmark rules |
| Scored | Pass/fail comparison | All 8 prerequisites + T5 mode + F6/F7/F11 blockers | Yes — retirement decision |

The T8 shakedown is an exploratory shakedown (BR-08(a)). Scored runs require the 8-item prerequisite gate at `benchmark-readiness.md:185`:
1. Narrative-claim inventory and ledger completeness checker
2. Methodology-finding format in adjudication.json
3. Mode-mismatch invalid-run schema in runs.json
4. `methodology_finding_threshold` in benchmark contract
5. Scope configuration formalization
6. `max_evidence` parameter definition
7. Artifact auditability extensions
8. Transcript parser + mechanical diff engine producing omission-audit proof

### Turn Semantics Contract (Model 2)

The emission protocol defines two sequences:

| Sequence | Numbering | What happens |
|----------|-----------|-------------|
| Logical dialogue | Turn 1, 2, 3, ... | Turn 1 = opening send to Codex (no emission) |
| Emitted state blocks | Turn 2, 3, 4, ... | First block after Codex's first reply |

Parse-failure conditions (now split):
1. First emitted state block has `turn != 2`
2. Non-monotonic `turn` counter on subsequent emitted turns

This is enforced in the dialogue-codex skill contract, the conformance checklist, and the operator inspection template (items 3-4 of 14).

### Cross-Model Semantic Sources for Production Dialogue

| Component | Cross-model location | Purpose | Port complexity |
|-----------|---------------------|---------|-----------------|
| `/dialogue` skill | `packages/plugins/cross-model/skills/dialogue/SKILL.md` | User-invocable orchestration (200+ lines) | Medium — reroute MCP tools, drop context-injection |
| codex-dialogue agent | `packages/plugins/cross-model/agents/codex-dialogue.md` | Production orchestrator with convergence, synthesis, phase tracking | Medium-high — convergence + synthesis are new |
| context-gatherer-code | `packages/plugins/cross-model/agents/context-gatherer-code.md` | Question-driven codebase explorer, emits prefix-tagged lines | Low — already uses Glob/Grep/Read |
| context-gatherer-falsifier | `packages/plugins/cross-model/agents/context-gatherer-falsifier.md` | Assumption tester, repo-first approach | Medium — needs `allowed_roots` confinement adaptation |

**Key port challenge:** The falsifier is intentionally broad and repo-first (reads `docs/decisions/`, `docs/plans/`, etc.). Benchmark runs require `scope_envelope` with `allowed_roots`. This is not just MCP rerouting — it requires a real containment/scoping redesign.

## Context

### Branch and Repository State

- **Branch:** `main` at `72c66714`
- **Working tree:** Clean
- **Remote:** Synced with `origin/main`

### Mental Model

**T-04 as a three-phase progression.** The ticket reads like a single implementation sprint, but the repo reveals three distinct phases:

1. **Shakedown (T8) — complete.** Validates the loop integration on a single task with manual inspection.
2. **Broader implementation packet — not started.** Production dialogue skill, orchestration agent, gatherer agents, convergence/synthesis. This is the work that makes codex-collaboration usable as a replacement for cross-model `/dialogue`.
3. **Scored benchmark — not started.** Full 8-task corpus with mechanical validation. This produces the context-injection retirement decision.

The immediate next step is phase 2 (broader implementation packet), not phase 3 (scored benchmark). Phase 2 is gated by T8 passing — which it has.

### Supersession Chain Status

| Ticket | ID | Name | Status |
|--------|-----|------|--------|
| Packet 2a | T-20260330-02 | Plugin shell and consult parity | **Closed** |
| Packet 2b | T-20260330-03 | Safety substrate and benchmark contract | **Closed** |
| Packet 3 | T-20260330-04 | Dialogue parity and scouting retirement | **Open** — T8 shakedown complete, broader packet next |
| Packet 4 | T-20260330-05 | Execution domain foundation | **Open** — genuinely greenfield |
| Packet 5 | T-20260330-06 | Promotion flow and delegate UX | Open |
| Packet 6/7 | T-20260330-07 | Analytics reviewer and cutover | Open |

### Environment State

- macOS Darwin 25.3.0, Python 3.14.2
- `uv` for all Python tool invocations
- Working directory: `/Users/jp/Projects/active/claude-code-tool-dev`
- 566 tests passing in codex-collaboration package

## Learnings

### The T-04 design plan has a later authoritative layer (T7/T8 docs)

**Mechanism:** The design plan at `2026-04-01-t04-benchmark-first-design-plan.md` defines the T0-T8 pipeline structure. But T7 (`2026-04-07-t7-executable-slice-definition.md`, 447 lines, PR #98 merged) and T8 (`2026-04-07-t8-minimum-runnable-shakedown-packet.md`) are the later accepted artifacts that define and implement the executable slice. The design plan's session sketch was superseded by the actual T7/T8 execution.

**Evidence:** User correction: "The latest authoritative docs for this area are the later T7/T8 artifacts, not just the earlier benchmark-first plan." Three specific file:line citations provided.

**Implication:** When analyzing T-04 status, always check for T7/T8 artifacts first. The design plan is useful for understanding the pipeline structure but T7/T8 define what was actually built.

### Contract changes propagate through a reference chain of 4+ document layers

**Mechanism:** The turn-semantics fix touched 7 files across 4 layers: skill contract → conformance checklist → operator template → design plans. A single semantic decision (model 2) required mechanical alignment at every layer. Missing any link leaves a drift point where an operator or validator uses stale rules.

**Evidence:** Two code review rounds were needed to catch all stale references. First round caught the operator template (shakedown-b1 had no turn-origin check). Second round caught the T7/T8 contract bodies (still enumerated 12 items).

**Implication:** When making contract changes in dialogue-codex or the inspection protocol, grep for item-range references (`items? [0-9]+-[0-9]+`) across all plan docs, not just the immediate skill file.

### The `not_scoutable` rate report is corpus-wide calibration, not T8

**Mechanism:** `scouting-behavior.md:327` says the dry run must produce a `not_scoutable` rate report "broken down by task ID" and "against the benchmark corpus." This is multi-task, corpus-wide work — it requires all 8 T4-BR-07 prerequisites (T4-BR-08(b) calibration tier).

**Evidence:** T4-BR-08 explicitly distinguishes exploratory shakedowns (no prerequisites, non-evidentiary) from policy-influencing calibration (all 8 prerequisites, conclusions shape rules).

**Implication:** The `not_scoutable` rate report is post-T8 calibration work. Do not include it in T8 scope or immediate next steps.

### T5 `agent_local` mode creates a real gate for scored runs but not for shakedowns

**Mechanism:** The accepted T5 mode strategy (`2026-04-02-t04-t5-mode-strategy.md`) says T-04 benchmark-first runs emit `agent_local`. But `benchmark-readiness.md:14` says `agent_local` runs without T5 migration surfaces are invalid. T7's boundary table (`t7-executable-slice-definition.md:417`) explicitly lists T5 migration as "deferred / external."

**Evidence:** T7 boundary table, line 428: "T5 `agent_local` migration | Missing | No | External prerequisite for scored runs (T5-owned)."

**Implication:** Scored benchmark execution requires T5 surfaces to land in the cross-model plugin (event_schema.py, dialogue-synthesis-format.md, dialogue skill parser). This is T5-owned, not T-04 work. Shakedowns proceed without it.

## Next Steps

### 1. Start the broader T-04 implementation packet

**Dependencies:** T8 shakedown passed — this is unblocked.

**What to read first:**
1. Cross-model `/dialogue` skill at `packages/plugins/cross-model/skills/dialogue/SKILL.md` — semantic source for the user-facing skill
2. Cross-model `codex-dialogue.md` agent — semantic source for the production orchestrator
3. Cross-model gatherer agents (`context-gatherer-code.md`, `context-gatherer-falsifier.md`) — semantic sources for evidence gathering
4. `docs/plans/t04-t4-scouting-position-and-evidence-provenance/containment.md` — scope/containment requirements for gatherers

**Approach suggestion:** Port the production dialogue surface in this order:
1. User-invocable `/dialogue` skill (routes through `codex.dialogue.start/reply/read`)
2. Production dialogue orchestration agent (convergence detection, synthesis)
3. Code and falsifier gatherer agents (with `allowed_roots` containment adaptation)
4. End-to-end integration test

**Key challenge:** The falsifier's broad repo-first approach needs `allowed_roots` confinement. This is a real containment/scoping redesign, not just MCP rerouting.

### 2. Keep scored benchmark work parked

**Dependencies:** Requires all 8 T4-BR-07 prerequisites + T5 mode surfaces.

**Note:** Do not attempt scored benchmark execution until the production dialogue surface exists AND the harness prerequisites are operational. The scored benchmark is the third phase, not the second.

## In Progress

**Clean stopping point — T-20260410-01 closed, commit `72c66714` merged and pushed, no work in flight.**

- T-04 gap analysis complete with three rounds of user correction
- T-20260410-01 closed with model 2 turn semantics
- 7 files updated, all item-range references verified consistent
- `main` at `72c66714`, synced with `origin/main`

## Open Questions

### 1. Should the broader implementation packet be planned formally (T7-style) or executed directly?

**Context:** T-04's design phase (T0-T6) is complete and T8 has passed. The broader packet involves porting 4 components from cross-model. The question is whether this warrants a formal plan document or can proceed as direct implementation.

**Impact:** A formal plan adds documentation overhead but provides a reviewable scope boundary. Direct execution is faster but may miss containment/scoping interactions.

### 2. How should the falsifier's scope confinement work under `allowed_roots`?

**Context:** Cross-model's falsifier is intentionally broad (`docs/decisions/`, `docs/plans/`, `docs/learnings/`). Benchmark runs require `scope_envelope` with `allowed_roots`. The production dialogue surface needs to work within this constraint.

**Impact:** This is the hardest port challenge. The falsifier's value comes from broad exploration — confinement may reduce its effectiveness. The design needs to balance containment with evidence quality.

## Risks

### 1. Falsifier containment may reduce evidence quality

**Impact:** If the falsifier can only search within `allowed_roots`, it may miss contradicting evidence in docs, decisions, or other non-code directories. This could produce false positives (claims classified as `supported` that would be `contradicted` by out-of-scope evidence).

**Mitigation:** The benchmark contract's primary evidence anchors define the scored scouting surface. For non-benchmark production use, consider whether `allowed_roots` should be relaxed.

### 2. Production dialogue surface is genuinely new implementation

**Impact:** Unlike T-02/T-03 (verification-closure), the broader packet requires net-new code: a user-facing skill, production orchestrator, gatherer agents, and convergence/synthesis logic. This is the first real implementation sprint in the supersession chain.

**Mitigation:** The semantic sources (cross-model skill, agents) are well-defined. The port is adaptation, not greenfield design.

## References

**T-04 ticket:**
- `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md`

**Design plan and subtasks:**
- Design plan: `docs/plans/2026-04-01-t04-benchmark-first-design-plan.md`
- T1: `docs/plans/2026-04-02-t04-t1-structured-termination-contract.md`
- T2: `docs/plans/2026-04-02-t04-t2-synthetic-claim-and-closure-contract.md`
- T3: `docs/plans/2026-04-02-t04-t3-deterministic-referential-continuity.md`
- T4 scouting spec: `docs/plans/t04-t4-scouting-position-and-evidence-provenance/` (10 files)
- T5: `docs/plans/2026-04-02-t04-t5-mode-strategy.md`
- T7: `docs/plans/2026-04-07-t7-executable-slice-definition.md` (447 lines)
- T8: `docs/plans/2026-04-07-t8-minimum-runnable-shakedown-packet.md`

**Shakedown evidence:**
- Smoke log: `docs/plans/t8-t4-live-smoke-log.md` (14 scenarios, all passing)
- Execution plan: `docs/plans/2026-04-08-t8-shakedown-execution-plan-v3.md`
- Conformance checklist: `docs/plans/2026-04-09-b4-dialogue-codex-conformance-checklist.md`
- B4 transcript: `/Users/jp/.claude/plugins/data/codex-collaboration-inline/shakedown/transcript-9f5da415-0a90-4863-a611-407d29e512f7.jsonl`

**Cross-model semantic sources:**
- Dialogue skill: `packages/plugins/cross-model/skills/dialogue/SKILL.md`
- Codex-dialogue agent: `packages/plugins/cross-model/agents/codex-dialogue.md`
- Code gatherer: `packages/plugins/cross-model/agents/context-gatherer-code.md`
- Falsifier gatherer: `packages/plugins/cross-model/agents/context-gatherer-falsifier.md`

**Closed tickets this session:**
- T-20260410-01: `docs/tickets/2026-04-10-dialogue-codex-turn-semantics-clarification.md`

**Prior handoffs (session chain):**
- This session loaded: `docs/handoffs/archive/2026-04-13_17-30_t02-t03-closed-t04-t05-unblocked.md`

**Commits this session:**
| Commit | Description |
|--------|-------------|
| `72c66714` | fix(contract): align turn semantics to model 2 and close T-20260410-01 |

## Gotchas

### Contract changes propagate through 4+ document layers

**Symptom:** Updating the turn-semantics rule in dialogue-codex/SKILL.md leaves stale references in the conformance checklist, operator template, T7, T8, and T8-v3.

**Root cause:** The inspection protocol is defined in the skill contract, duplicated in the conformance checklist, generated by the operator template, and referenced by item number in T7/T8 design docs. Changing any item count ripples through all layers.

**Prevention:** After contract changes, grep for item-range references (`items? [0-9]+-[0-9]+`, `checklist item[s]? [0-9]`) across all `docs/plans/` and `packages/plugins/codex-collaboration/skills/`. Two review rounds were needed this session to catch all stale references.

### T7/T8 docs supersede the benchmark-first design plan for T8 scope

**Symptom:** Analyzing T-04 using only the design plan (`2026-04-01-t04-benchmark-first-design-plan.md`) produces an inaccurate gap matrix because it doesn't reflect what T7/T8 actually defined and built.

**Root cause:** T7 (PR #98, merged) and T8 are later accepted artifacts that narrowed and formalized the design plan's T7/T8 placeholders. The design plan's session sketch was superseded.

**Prevention:** When analyzing T-04 status, always check `docs/plans/2026-04-07-t7-*` and `docs/plans/2026-04-07-t8-*` first.

## Conversation Highlights

**User's pre-analysis methodology (confirmed this session):**
User arrived with detailed pre-analysis of why T-04 should precede T-05, including specific file paths and scaffold citations. This continues the established pattern of independent review before sessions.

**Three rounds of iterative correction:**
Each round sharpened the gap matrix with specific file:line citations. The user did not just say "that's wrong" — each correction included evidence and a specific alternative. This is the same pattern seen in T-03's analytics classification correction (prior session).

**User's code review integration:**
User ran code reviews after each patch and provided structured findings with priority tags ([P1], [P2]), confidence scores, and specific file:line locations. Two rounds were needed for the renumbering propagation.

**User's model 2 recommendation:**
User: "I would choose model 2 from the ticket: first emitted state block starts at `turn: 2`, meaning emitted state begins with the first post-reply verification turn. That fits the validated runtime and exemplars, and it avoids inventing an extra synthetic opening emission just to satisfy older prose."

**User's scope advice for checklist change:**
User: "Make the start-value rule a separate invariant, not just a parenthetical on monotonicity. A validator could still treat first-emitted `turn: 3` as monotonic if it only sees one block."

## User Preferences

**Evidence-based corrections with specific citations (confirmed again):**
When correcting analysis, user provides specific file:line evidence, not just assertions. Three correction rounds this session, each with 3+ citations. Example: "Your S2 stage does not match the project's later accepted T7/T8 contract" with three file:line citations to the T7 boundary table, T7 deferred items, and T8 implementation plan.

**Iterative refinement over single-pass analysis:**
User prefers to review and correct analysis iteratively rather than wait for a perfect first draft. Three rounds of correction produced a more accurate result than any single attempt would have.

**Structured code review with priority and confidence:**
User runs code reviews with `::code-comment` format including priority tags, confidence scores, and exact file:line ranges. Expects findings to be addressed before committing.

**Pre-analysis before sessions (confirmed again):**
User performs detailed pre-reading and arrives with structured findings. This session: full recommendation with 5 file path citations for T-04 over T-05.
