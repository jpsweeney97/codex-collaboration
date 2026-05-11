---
date: 2026-04-15
time: "19:30"
created_at: "2026-04-16T00:30:00Z"
session_id: dad088b4-edd7-4419-9b5b-81f9ea1f706c
resumed_from: docs/handoffs/archive/2026-04-15_15-00_t04-ac4-closed-benchmark-v1-contract-rewrite.md
project: claude-code-tool-dev
branch: feature/benchmark-v1-scaffold
commit: adcf49ea
title: "T-04 benchmark v1 scaffold reviewed through 7 adversarial rounds and committed"
type: handoff
files:
  - docs/benchmarks/dialogue-supersession/v1/manifest.json
  - docs/benchmarks/dialogue-supersession/v1/runs.json
  - docs/benchmarks/dialogue-supersession/v1/adjudication.json
  - docs/benchmarks/dialogue-supersession/v1/summary.md
  - docs/benchmarks/dialogue-supersession/v1/operator-procedure.md
---

# T-04 Benchmark v1 Scaffold Reviewed Through 7 Adversarial Rounds and Committed

## Goal

Scaffold the benchmark v1 artifact set and operator procedure so that the dialogue supersession benchmark (AC-5 through AC-7) can be executed.

**Trigger.** Resumed from `2026-04-15_15-00` handoff. Last session closed AC-4, bumped the Codex timeout to 1200s, and rewrote the benchmark contract to a 4-row corpus with a 4-item v1 gate. The primary next step was: "define the stable artifact path, create the initial `manifest.json` / `runs.json` / `adjudication.json` / `summary.md` scaffolds, and write the operator procedure for the four retained rows."

**Stakes.** AC-5 requires "The benchmark contract is executed on the fixed corpus." The scaffold is a prerequisite — without it, there is no artifact structure, no operator procedure, and no defined execution flow. The scaffold also surfaces implementation prerequisites that block scored execution, which must be resolved before AC-5 can close.

**Success criteria achieved this session:**

1. Artifact skeleton created with all four required files plus operator procedure.
2. Artifact path placed outside all scored `allowed_roots` surfaces — no B8 self-referential contamination.
3. Run-condition compliance documented honestly — blockers identified, not rationalized.
4. Rehearsal/scored execution mode gate implemented with full bifurcation.
5. Reviewed through 7 adversarial rounds, progressing from Reject to Defensible.

**Position in the T-04 arc:**

| Session | Role | Artifact |
|---|---|---|
| 2026-04-13 | v1 plan drafting and approval | Plan at `main@73f8c9c1` |
| 2026-04-14 12:55 | Section 10 authoring decisions | Addendum committed |
| 2026-04-14 16:30 | Four production surfaces authored | Committed `05b7db3a` |
| 2026-04-14 20:17 | E2E verified, report committed, PR #106 open | `7a1bd077`, PR #106 |
| 2026-04-14 22:45 | PR #106 merged, gatherer plan designed and committed | Merged `c3c11fa4`, plan at `99472736` |
| 2026-04-14 23:30 | Gatherer implementation merged, E2E smoke run, timeout fix | PR #107 merged `d478c0d7`, timeout fix `e13a1b87` |
| 2026-04-15 15:00 | AC-4 closed, timeout 1200s, benchmark v1 contract rewrite | Timeout `71f442ce`, contract `1e08c397` |
| **2026-04-15 19:30 (this)** | **Benchmark v1 scaffold reviewed and committed** | **Scaffold `adcf49ea` on `feature/benchmark-v1-scaffold`** |
| Next | Resolve RC4 blockers (implementation or contract amendment), then merge scaffold and execute benchmark | |

## Session Narrative

**Phase 1 — Initial scaffold (~15 min).**

Loaded the `2026-04-15_15-00` handoff. Started by reading the benchmark contract (`dialogue-supersession-benchmark.md`, 366 lines) and the benchmark readiness document (`benchmark-readiness.md`, 278 lines) to ground the scaffold in the actual artifact specifications. Also read the T-04 ticket to confirm AC status.

Chose `docs/superpowers/specs/codex-collaboration/benchmark-v1/` as the initial artifact path. Created the feature branch `feature/benchmark-v1-scaffold`. Scaffolded all five files: `manifest.json` (with corpus `allowed_roots` extracted from the contract), `runs.json`, `adjudication.json`, `summary.md`, and `operator-procedure.md`. The operator procedure covered pre-run setup, per-row execution with scope instruction templates, adjudication workflow, aggregate scoring, and finalization.

To write the operator procedure, read both dialogue skills (`codex-collaboration/skills/dialogue/SKILL.md` and `cross-model/skills/dialogue/SKILL.md`) and both plugin manifests to understand how the systems are invoked and disambiguated. Also read the candidate orchestrator agent (`dialogue-orchestrator.md`) and both gatherer agents to understand control surfaces for posture, turn budget, and scope envelope.

**Phase 2 — Round 1 review: Reject (~30 min).**

User provided a detailed adversarial review identifying five critical failures:

1. **B8 self-referential contamination.** The artifact path (`docs/superpowers/specs/codex-collaboration/benchmark-v1/`) was inside B8's `allowed_roots` (`docs/superpowers/specs/codex-collaboration/`). The benchmark packet and prior benchmark outputs would be legal evidence for B8 — self-referential contamination.
2. **Working tree state violation.** The procedure saved baseline artifacts to the repo before running the candidate, violating the contract's "same working tree state" requirement for each pair.
3. **Candidate posture/turn-budget not actually controlled.** The candidate skill has no `-p`/`-n` flags. The procedure stuffed text into the prompt with no parser or control surface to turn it into execution settings.
4. **Schema inconsistency.** B8 used `allowed_roots_groups` but the contract and procedure referred to `allowed_roots`. `scope_compliant` typed as boolean but initialized to null. "8 entries when complete" didn't account for reruns.
5. **Missing clean-session isolation.** No fresh-session requirement per run.

User identified two root-cause patterns: mixing normative and execution artifacts in the same tree, and optimizing for slash-skill convenience over actual control parity.

**Phase 3 — Round 2 revision: Reject again (~30 min).**

Moved artifacts to `docs/benchmarks/dialogue-supersession/v1/` (outside all scored roots). Added staging protocol (`$BENCH_STAGING` outside repo). Documented control surface asymmetry with a `run_condition_parity` table in `manifest.json`. Added fresh-session requirement. Fixed schema with nullable types and rerun retention.

User's second review found three remaining critical failures:

1. **Contract breach on posture/turn-budget.** I misapplied the "when the host allows" caveat — it applies only to run condition 5 (model, reasoning-effort, timeout), not run condition 4 (posture, turn budget). RC4 is unconditional.
2. **scope_envelope parity claim was false.** The gatherer agents support `scope_envelope` but the candidate slash skill doesn't pass it. I claimed mechanical parity that didn't exist.
3. **Baseline evidence-budget overflow treated as advisory.** The contract fixes the values; overflow should invalidate.
4. **Post-import reruns violate working tree state.** Importing per-row means reruns discover a different repo.

**Phase 4 — Round 3 revision: Reject to Major revision (~20 min).**

Reclassified RC4 as a **blocker** (not permitted asymmetry). Added "Scoring Prerequisites — BLOCKING" section. Removed false `scope_envelope` parity claim — both systems now documented as "prompt-only" scope enforcement. Evidence-budget overflow now invalidates. Deferred ALL repo imports to Phase 5.

User's third review gave "Major revision" — first non-reject. Remaining issues: Phase 3 still referenced repo files despite staging-only guarantee. Scoring path was unconditional despite RC4 being blocked. Session isolation was self-attested.

**Phase 5 — Rounds 4-5: Major revision to Minor revision (~20 min).**

Fixed all Phase 3 repo-file references. Added **Execution Mode Gate** between Phase 1 and Phase 2 with explicit REHEARSAL/SCORED determination. Downgraded RC6 from "Matched" to "Operator-attested." Round 5 added `rehearsal` and `session_id_canonical` fields to `runs.json` schema, made missing canonical session ID force rehearsal mode, and gave `summary.md` an explicit rehearsal state.

User's round 5 review gave "Minor revision" — rehearsal schema was in `runs.json` but not in the Phase 5 example. Closeout didn't branch by mode. Mixed-mode policy undefined.

**Phase 6 — Rounds 6-7: Minor revision to Defensible (~15 min).**

Updated Phase 5 example with `rehearsal` and `session_id_canonical`. Split Phase 5 closeout into explicit SCORED and REHEARSAL paths. Defined benchmark-wide mode: any single rehearsal run makes the entire benchmark non-evidentiary. Added staging metadata example with mode fields. Moved mode determination before Phase 4 so scoring gates on the recomputed result. Made RC6 in `summary.md` mode-dependent instead of hardcoded.

Round 7 review: "Defensible."

## Decisions

### Decision 1: Artifact path at `docs/benchmarks/dialogue-supersession/v1/`

**Choice:** Place benchmark execution artifacts at `docs/benchmarks/dialogue-supersession/v1/`, outside all scored `allowed_roots`.

**Driver:** Round 1 review identified that the original path (`docs/superpowers/specs/codex-collaboration/benchmark-v1/`) was inside B8's `allowed_roots` (`docs/superpowers/specs/codex-collaboration/`), making the benchmark packet and prior outputs legal evidence for the very row being scored.

**Alternatives considered:**
- **`docs/superpowers/specs/codex-collaboration/benchmark-v1/`** — alongside the authority document. Rejected because it's inside B8's scored evidence root, creating self-referential contamination.
- **`docs/benchmarks/v1/`** — too generic, ambiguous alongside existing skill benchmark infrastructure in `docs/benchmarks/`.

**Trade-offs accepted:** Artifacts are no longer co-located with the benchmark contract. The contract lives at `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md`, the artifacts at `docs/benchmarks/dialogue-supersession/v1/`. Path is longer but unambiguous.

**Confidence:** High (E2) — verified programmatically that the artifact path has zero overlap with any scored `allowed_roots` across all four corpus rows.

**Reversibility:** Medium — path is referenced in manifest, procedure, and would be in all transcripts. Moving requires updating all references.

**Change trigger:** If a future benchmark version changes B8's `allowed_roots` to include `docs/benchmarks/`, the artifact path would need to move again.

### Decision 2: RC4 (posture/turn-budget) classified as a scoring blocker

**Choice:** Classify the candidate's inability to match posture and turn budget as a blocker that prevents scored runs, not as an acceptable asymmetry.

**Driver:** The benchmark contract's run condition 4 says "Same posture and turn budget from the fixed corpus" — unconditional. The "when the host allows them to be matched" caveat applies only to run condition 5 (model, reasoning-effort, dialogue-timeout). The first draft misapplied this caveat to RC4.

**Alternatives considered:**
- **Document as "acceptable asymmetry"** — rejected because it contradicts the contract's plain text. Round 2 review caught this: the candidate runs B1/B3/B5 with 10 turns against a corpus budget of 6, which is a direct contract breach.
- **Run at MCP layer to bypass skill limitations** — rejected because the benchmark compares the systems (including the skill), not just the Codex dialogue layer.

**Trade-offs accepted:** This means the scaffold cannot produce scored results in its current state. The benchmark requires either (a) adding `-p`/`-n` flags to the candidate skill and passing them to the orchestrator, or (b) amending the contract through change control. The scaffold is ready for rehearsals (T4-BR-08(b)) but not scored execution.

**Confidence:** High (E2) — grounded in the contract text (run condition 4 vs. 5 distinction) and verified against the candidate system's actual control surface (orchestrator hardcodes `DIALOGUE_TURN_BUDGET = 10`, no posture input).

**Reversibility:** High — once RC4 is resolved (implementation or amendment), the blocker is lifted. The execution mode gate in the procedure will pass, and scored execution proceeds.

**Change trigger:** Candidate skill gains `-p`/`-n` flags, or the contract is amended to allow documented asymmetry.

### Decision 3: All repo imports deferred to Phase 5

**Choice:** Stage all run artifacts, adjudication data, and metadata outside the repo (`$BENCH_STAGING`) throughout execution and adjudication. Import everything to the repo in a single batch in Phase 5, after the benchmark is fully complete.

**Driver:** Multiple review rounds exposed working-tree contamination. Round 1: saving baseline artifacts before running the candidate violated "same working tree state" per pair. Round 3: per-row import meant reruns discovered a different repo state. Deferring all imports eliminates both problems.

**Alternatives considered:**
- **Import per-pair** — rejected in round 3 because adjudication-discovered scope violations require reruns, and post-import reruns execute against a different repo state.
- **Import per-row after adjudication** — rejected for the same reason: late-discovered invalidity still requires reruns.
- **Git worktree for reruns** — more complex, and unnecessary once all imports are deferred.

**Trade-offs accepted:** All work-in-progress metadata lives in `/tmp/` during execution. If the staging directory is lost (machine restart, disk cleanup), the run data is lost and must be re-executed. Mitigated by the relatively short benchmark duration (~3-6 hours).

**Confidence:** High (E2) — the deferred-import approach provably satisfies the "same working tree state" requirement for all runs including reruns, because the repo is never modified until everything is done.

**Reversibility:** High — the import timing is a procedure change, not an artifact format change.

**Change trigger:** If a future benchmark version adds a dedicated harness with worktree management, per-pair import could be re-enabled safely.

### Decision 4: Benchmark-wide mode determination (any rehearsal → all rehearsal)

**Choice:** If any valid run is classified as rehearsal (RC4 blockers, missing canonical session ID), the entire benchmark is non-evidentiary. No mixed-mode packets.

**Driver:** Round 6 review exposed that per-run rehearsal fallback creates undefined mixed-mode state. Phase 4 scoring doesn't know how to handle a packet with 7 scored runs and 1 rehearsal. The simplest and safest policy: benchmark-wide rehearsal.

**Alternatives considered:**
- **Exclude rehearsal runs from aggregates** — creates a partial benchmark that may not cover all corpus rows, making aggregate metrics unreliable.
- **Allow mixed-mode with caveats** — operationally dangerous. A partially-scored packet is easy to misinterpret.

**Trade-offs accepted:** A single run losing canonical session ID downgrades the entire benchmark to rehearsal. This is operationally expensive — the operator must fix the issue and rerun that single run to restore scored status. But the alternative (mixed-mode ambiguity) is worse for benchmark credibility.

**Confidence:** High (E2) — grounded in the contract's requirement that aggregate metrics come from comparable runs under matched conditions. A mixed-mode packet violates comparability.

**Reversibility:** High — policy is documented in the procedure, not encoded in the schema. The `rehearsal` field is per-run, so the policy could be relaxed without schema changes.

**Change trigger:** If a future benchmark version adds a harness that can mechanically guarantee session isolation (making canonical session ID always available), per-run mode becomes safe.

### Decision 5: Scope enforcement classified as "prompt-only" for both systems

**Choice:** Document that neither system uses mechanical `scope_envelope` enforcement during benchmark runs. Both rely on prompt-level scope instructions plus post-hoc transcript review.

**Driver:** Round 3 review exposed a false parity claim. The original draft said `allowed_roots` were matched via `scope_envelope`. But the candidate slash skill doesn't pass `scope_envelope` to gatherers (even though the agents support it). The baseline's `codex-dialogue` agent accepts `scope_envelope` in its delegation envelope, but the cross-model slash skill's passthrough is also not verified for all paths.

**Alternatives considered:**
- **Claim envelope parity** — rejected as false. The gatherer agents support `scope_envelope` but the skill doesn't pass it.
- **Wire `scope_envelope` into the candidate skill** — correct fix but implementation work beyond the scaffold scope.

**Trade-offs accepted:** Scope compliance is a post-hoc discovery, not a runtime prevention. A scouting step that ignores the prompt instruction will only be caught during adjudication. The contract permits procedural enforcement for v1 (contract lines 177-183).

**Confidence:** High (E2) — verified by reading the candidate skill's gatherer dispatch code (`SKILL.md:81-96`, gatherers receive `objective`, `key_terms`, and `assumptions` — no `scope_envelope`).

**Reversibility:** High — updating the candidate skill to pass `scope_envelope` to gatherers would upgrade this to mechanical enforcement.

**Change trigger:** When `scope_envelope` is wired through both systems' slash skills to their gatherer/agent dispatch.

## Changes

### `docs/benchmarks/dialogue-supersession/v1/manifest.json` (NEW, 139 lines)

**Purpose:** Benchmark manifest recording contract commit, model settings, evidence budget, per-row `allowed_roots`, and run-condition parity classification.

**Approach:** Corpus rows transcribed from the benchmark contract (`dialogue-supersession-benchmark.md`). `allowed_roots` extracted from primary evidence anchors for B1/B3/B5 and from the anchored decomposition for B8. B8 has both flat `allowed_roots` (union for transcript review) and `allowed_roots_groups` (per-group for adjudication), validated as consistent. Run-condition parity organized into `matched`, `blocked`, `prompt_only`, and `asymmetric_by_design` categories.

### `docs/benchmarks/dialogue-supersession/v1/runs.json` (NEW, 29 lines)

**Purpose:** Schema for per-run entries with mode markers (`rehearsal`, `session_id_canonical`), rerun chain (`superseded_by`), and diagnostic metrics.

**Approach:** Schema-in-file via `_entry_schema` key (v1 doesn't require formal JSON Schema). Nullable types for fields that are pending review. `rehearsal` boolean distinguishes scored from non-evidentiary runs in the persisted artifact.

### `docs/benchmarks/dialogue-supersession/v1/adjudication.json` (NEW, 30 lines)

**Purpose:** Schema for per-run adjudication entries with claims, safety findings, completeness review, and scope compliance.

**Approach:** Claims carry `added_in_review` boolean to track second-pass completeness additions. Safety is binary per run. Scope compliance records specific violations (tool call, target path, violated root).

### `docs/benchmarks/dialogue-supersession/v1/summary.md` (NEW, 94 lines)

**Purpose:** Mode-aware summary template with explicit SCORED/REHEARSAL states.

**Approach:** Execution Mode section determines whether scored sections (Pass Rule Evaluation, Retirement Decision) are filled or marked "Skipped — rehearsal." Run-Condition Status table has mode-dependent RC6 entry. Per-Row Results table includes actual turns and diagnostic metrics.

### `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` (NEW, 724 lines)

**Purpose:** Step-by-step operator procedure implementing the benchmark contract's v1 execution flow.

**Approach:** Organized into Scoring Prerequisites (blockers), T4-BR-07 Prerequisites, Run Condition Status, Phase 1 (setup + staging), Execution Mode Gate, Phase 2 (per-row execution in fresh sessions), Phase 3 (adjudication from staging), Benchmark-Wide Mode Determination, Phase 4 (scoring, skipped for rehearsal), Phase 5 (batch import and bifurcated closeout). All writes go to `$BENCH_STAGING` until Phase 5. Control Surface Parity section documents what is matchable vs. blocked vs. prompt-only.

## Codebase Knowledge

### Candidate system control surfaces

| Control | Where defined | Value | Configurable? |
|---|---|---|---|
| `DIALOGUE_TURN_BUDGET` | `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md:27` | 10 | No — hardcoded constant |
| `MAX_EVIDENCE` | `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md:28` | 15 | No — hardcoded constant |
| `MAX_SCOUT_ROUNDS` | `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md:29` | 8 | No — hardcoded constant |
| `INLINE_SCOUTING_BUDGET` | `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md:25` | 5 | No — hardcoded constant |
| Posture | Not exposed | N/A | No control surface |
| `scope_envelope` (gatherers) | `context-gatherer-code.md:23`, `context-gatherer-falsifier.md:23` | Optional input | Supported by agents but not passed by skill |
| `scope_envelope` (orchestrator) | `dialogue-orchestrator.md:17` | Via containment guard | Constrained by hook, not by dispatch parameter |

### Baseline system control surfaces

| Control | Where defined | Configurable? |
|---|---|---|
| Posture | `/cross-model:dialogue` `-p` flag → `codex-dialogue` agent (line 41-42) | Yes |
| Turn budget | `/cross-model:dialogue` `-n` flag → `codex-dialogue` agent (line 43, default 8, max 15) | Yes |
| `scope_envelope` | `codex-dialogue` agent delegation envelope (line 46) | Yes, in the agent dispatch |

### Benchmark contract structure (current state at `1e08c397`)

| Section | Lines | Key content |
|---|---|---|
| Fixed Corpus | 74-84 | 4 rows: B1 architecture, B3 code review, B5 policy audit, B8 supersession |
| B8 Anchored Decomposition | 110-131 | 3 path groups, cross-group reasoning OK, cross-group target expansion not |
| Run Conditions | 144-186 | 11 conditions; RC4 (posture/turn-budget) is unconditional; RC5 has "when host allows" caveat |
| Evidence Budget | 188-203 | `baseline_max_evidence = 5`, `candidate_max_evidence = 15` |
| Required Artifacts | 224-245 | `manifest.json`, `runs.json`, `adjudication.json`, `summary.md` |
| Adjudication Rules | 248-293 | Claim inventory, labels (supported/unsupported/false), safety, scope compliance |
| Metrics | 295-311 | `converged_within_budget` is diagnostic, not pass/fail |
| Pass Rule | 313-331 | 3 conditions: safety=0, false<=baseline, supported_rate within 0.10 |
| Change Control | 352-366 | Requires editing contract, explaining why, rerunning affected comparisons |

### Plugin disambiguation

Both plugins have a `/dialogue` skill. They're disambiguated by plugin name: `/cross-model:dialogue` (baseline) and `/codex-collaboration:dialogue` (candidate). Plugin manifests at:
- `packages/plugins/cross-model/.claude-plugin/plugin.json` — name: `cross-model`, version `3.1.3`
- `packages/plugins/codex-collaboration/.claude-plugin/plugin.json` — name: `codex-collaboration`, version `0.2.0`

### Existing `docs/benchmarks/` contents

`docs/benchmarks/` already contains skill benchmark infrastructure (`bench-skill-bodies_v0.1.0.md`, `bench-skill-bodies_v1.0.0.md`, `control-bodies_v0.1.0.md`, `operations/`, `runs/`, `scenarios/`, `suites/`). The dialogue supersession benchmark is a separate benchmark system, hence the `dialogue-supersession/` subdirectory to avoid collision.

## Context

### T-04 acceptance criteria status after this session

| AC | Description | Status | Evidence |
|---|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) | `skills/dialogue/SKILL.md` |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) | `agents/dialogue-orchestrator.md` |
| 3 | Gatherer agents exist and use Claude-side tools | Done (PR #107) | Both agents with Glob/Grep/Read |
| 4 | Synthesis with bounded citations and convergence | Done | Dialogue-tier citations + `converged: false` terminal artifact |
| 5 | Benchmark contract executed on fixed corpus | **Open** | Scaffold ready; blocked on RC4 |
| 6 | Benchmark result recorded with per-task metrics | **Open** | Depends on AC-5 |
| 7 | Context-injection retirement decision explicit | **Open** | Depends on AC-6 |

### Mental model for this session

This session transitions from **contract rewriting** to **execution scaffolding**. The benchmark contract (rewritten last session) defines *what* the benchmark measures. The scaffold defines *how* it is executed. The key insight that emerged through the review cycle: a benchmark scaffold's first obligation is to prevent itself from producing artifacts that misrepresent what happened. Every other concern (operator convenience, schema elegance, template aesthetics) is subordinate.

### The review cycle as a design process

The 7-round review cycle was not rework — it was the design process. Each round exposed a class of integrity issue that was then resolved:

| Round | Verdict | Class of issue exposed |
|---|---|---|
| 1 | Reject | Contamination (artifact path inside scored evidence), working-tree violation, false parity claims |
| 2 | Reject | Contract misreading (RC4 vs RC5 caveat scope), false `scope_envelope` claim, soft evidence budget |
| 3 | Major revision | Incomplete staging propagation (repo writes in Phase 3), no mode gate |
| 4 | Minor revision | Schema didn't carry mode markers, closeout not bifurcated, session ID not gating |
| 5 | Minor revision | Phase 5 example stale, mixed-mode undefined, summary hardcoded |
| 6 | Minor revision | Mode determination sequencing (after scoring instead of before) |
| 7 | Defensible | No remaining defects |

### Open tickets

| Ticket | ID | Status | Next |
|---|---|---|---|
| Dialogue parity & scouting retirement | T-04 | Open (AC 1-4 done) | Resolve RC4, merge scaffold, execute benchmark |
| Execution-domain foundation | T-05 | Open (unstarted) | Separate workstream |
| Promotion flow & delegate UX | T-06 | Open (blocked by T-05) | — |
| Analytics reviewer & cutover | T-07 | Open | Separate workstream |

## Learnings

### Run condition 4 vs. 5: the "when the host allows" caveat is narrow

**Mechanism.** The benchmark contract's run conditions 1-4 are unconditional. Only run condition 5 ("Same Codex model, reasoning-effort, and dialogue-timeout settings **when the host allows them to be matched**") has the host caveat. The first draft misapplied this caveat to posture and turn budget (RC4), rationalizing the candidate's lack of controls as "acceptable asymmetry."

**Evidence.** Contract lines 146 (RC4, no caveat) vs 152-153 (RC5, caveat). Round 2 review caught the misapplication.

**Implication.** When a contract has graduated requirements (some unconditional, some with caveats), read the graduation literally. Don't extend a caveat from one condition to another.

### Benchmark scaffolds must prevent self-referential contamination

**Mechanism.** B8's `allowed_roots` includes `docs/superpowers/specs/codex-collaboration/`. If benchmark artifacts live under that path, the scouting system can read the benchmark manifest, operator procedure, and prior outputs as "evidence" for the very row being scored. This is self-referential contamination.

**Evidence.** First draft placed artifacts at `docs/superpowers/specs/codex-collaboration/benchmark-v1/`. Round 1 review caught the contamination by checking B8's `allowed_roots_groups.candidate_normative_surface` against the artifact path.

**Implication.** Always verify that benchmark execution artifacts live outside every scored evidence surface before committing the path. This check should be mechanical (script or assertion), not manual.

### Deferred batch import eliminates working-tree contamination class

**Mechanism.** If run artifacts are written to the repo between runs, reruns discover a different repo state than the originals. Deferring ALL imports to a single batch after the entire benchmark is complete (including adjudication and reruns) means every run executes against the same clean repo.

**Evidence.** Rounds 1, 2, and 4 each found a working-tree contamination variant. The per-pair import fix (round 2) was insufficient because adjudication-discovered scope violations require reruns. The deferred-batch-import fix (round 3) eliminated the entire class.

**Implication.** For any benchmark where runs must share working-tree state, stage everything externally and import only once, not progressively.

### Mode-gate propagation requires full artifact pass

**Mechanism.** Adding a rehearsal/scored mode gate to the procedure is necessary but not sufficient. The mode distinction must propagate to: the run schema (per-run `rehearsal` field), the staging metadata format (so mode determination can consume it), the examples (so operators following them literally produce correct artifacts), the scoring phase (skip for rehearsal), the closeout path (bifurcated by mode), and the summary template (explicit rehearsal state).

**Evidence.** Rounds 4-6 each found a location where mode propagation was incomplete: schema (round 4), examples (round 5), mode determination sequencing (round 6).

**Implication.** When adding a mode/state to a procedure, enumerate every artifact, example, and downstream consumer before implementing. Check each one.

### `scope_envelope` support vs. wiring are different

**Mechanism.** The candidate gatherer agents accept `scope_envelope` as an optional input (`context-gatherer-code.md:23`, `context-gatherer-falsifier.md:23`). But the candidate dialogue skill dispatches gatherers with only `objective`, `key_terms`, and `assumptions` (`SKILL.md:81-96`). Support without wiring is not a control surface.

**Evidence.** Round 2 review caught the false parity claim. The procedure said `scope_envelope` was matched; the skill never passes it.

**Implication.** When claiming control-surface parity between systems, verify the full wiring path from user-invocable surface through dispatch to agent consumption, not just whether the receiving end supports the parameter.

## Next Steps

### 1. Resolve RC4 blockers (posture and turn-budget control)

**Dependencies:** None — this is a prerequisite for scored benchmark execution.

**What to do:** Choose one resolution path:

**(a) Implementation path** — add `-p` (posture) and `-n` (turn-budget) flags to the codex-collaboration dialogue skill. Pass them through to the orchestrator agent's dispatch prompt. The orchestrator's hardcoded `DIALOGUE_TURN_BUDGET = 10` would need to become a configurable parameter accepted from the dispatch.

**(b) Contract amendment path** — amend run condition 4 in `dialogue-supersession-benchmark.md` through change control to allow documented posture/turn-budget asymmetry with mandatory recording of effective values. This requires editing the contract, explaining why, and documenting the trade-off.

**What to read first:** Benchmark contract run condition 4 (line 146) and run condition 5 (lines 152-153) for the exact requirement. Candidate orchestrator constants at `dialogue-orchestrator.md:22-29`. Candidate skill dispatch at `SKILL.md:218-234`.

**Potential obstacles:** Implementation path requires modifying the orchestrator agent, which has a complex procedure (30+ maxTurns, multiple phases). The posture change may be straightforward (add to Phase 1 setup) but the turn budget change affects the core dialogue loop. Contract amendment path requires change-control compliance (contract lines 352-366).

### 2. Merge scaffold to main

**Dependencies:** RC4 resolution (#1) is preferred but not strictly required — the scaffold is valid and useful in its blocked state.

**What to do:** Merge `feature/benchmark-v1-scaffold` to main. The scaffold is at `adcf49ea`, reviewed through 7 rounds, verdict "Defensible."

**Potential obstacles:** Branch protection. Will need a PR or direct merge depending on the workflow.

### 3. Execute benchmark v1

**Dependencies:** RC4 resolution (#1) and scaffold merged (#2).

**What to do:**
1. Follow the operator procedure from Phase 1 (fix commit, verify plugins, create staging)
2. Execution mode gate should pass (after RC4 resolution)
3. Execute 4 rows x 2 systems = 8 runs with fresh sessions, stage everything
4. Adjudicate row-by-row from staging
5. Benchmark-wide mode determination, aggregate scoring
6. Batch import and finalize

**What to read first:** `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` — the full procedure.

**Potential obstacles:** Manual adjudication is the dominant cost. At ~10-20 claims per synthesis and 8 syntheses, expect 80-160 individual claim adjudications with second-pass completeness reviews. Total wall-clock time ~3-6 hours.

## In Progress

**Clean stopping point — scaffold committed on feature branch, nothing in flight.**

- **Approach:** Iterative scaffold → adversarial review → fix cycle (7 rounds).
- **State:** Complete. Scaffold committed at `adcf49ea` on `feature/benchmark-v1-scaffold`.
- **Working:** All five artifact files valid and internally consistent. Rehearsal/scored mode gate functional. Staging protocol sound. Contamination eliminated.
- **Not working:** Nothing broken. Scored execution blocked on RC4 (by design — the scaffold correctly identifies the blocker).
- **Next action:** Resolve RC4 blockers, then merge scaffold and execute benchmark.

## Open Questions

### 1. Implementation or contract amendment for RC4?

**Context:** The candidate skill lacks `-p`/`-n` flags, and the orchestrator hardcodes `DIALOGUE_TURN_BUDGET = 10`. RC4 requires "Same posture and turn budget from the fixed corpus."

**Impact:** Implementation is more work but satisfies the contract as written. Amendment is faster but weakens the comparison's matched-conditions story. The scaffold supports either path — the execution mode gate checks for control-surface availability, and would need updating if RC4 is resolved by amendment instead.

**Decision pending until:** Next session, likely user direction.

### 2. Should `scope_envelope` be wired through the candidate skill?

**Context:** Both gatherer agents support `scope_envelope` but the skill doesn't pass it. Currently classified as "prompt-only" enforcement for both systems, which is v1-compliant but a known fragility.

**Impact:** Low for v1 (procedural enforcement is contract-compliant). Would strengthen the benchmark's scope control story and make adjudication less dependent on transcript review.

**Decision pending until:** After RC4 is resolved, as a nice-to-have.

### 3. What is the canonical way to obtain a Claude Code session ID?

**Context:** The procedure requires a canonical host session ID for scored runs. If unavailable, the run is forced to rehearsal. The procedure suggests checking the status bar or `~/.claude/session_id`, but these paths are not guaranteed.

**Impact:** If no canonical session ID is reliably available, scored runs may be impossible to audit for RC6, making all runs effectively rehearsal.

**Decision pending until:** Investigating Claude Code's session identity mechanism.

## Risks

### 1. RC4 resolution path affects scaffold update scope

**Impact:** If RC4 is resolved by contract amendment (not implementation), the execution mode gate in the operator procedure needs updating. The gate currently checks for control-surface availability (does the candidate accept `-p`/`-n`?). An amendment-based resolution would require the gate to check "is scored execution permitted under the current contract" instead.

**Mitigation:** The scaffold is modular — the execution mode gate is a discrete section that can be updated without affecting the rest of the procedure.

### 2. Manual adjudication is the dominant benchmark cost

**Impact:** 4 rows x 2 systems = 8 syntheses, each requiring claim inventory, labeling, safety review, and second-pass completeness review. At ~10-20 claims per synthesis: 80-160 individual adjudications. This is significant manual labor (~2-4 hours).

**Mitigation:** Row-by-row adjudication (rather than all-at-once) keeps adjudicator context fresh. High-signal rows first (B3 safety, B8 supersession) — if early rows show clear pass/fail, remaining rows provide confirmation.

### 3. Prompt-only scope enforcement is fragile

**Impact:** Neither system mechanically prevents out-of-scope scouting during benchmark runs. A scouting step that ignores the prompt instruction will only be caught during transcript review, not at runtime.

**Mitigation:** Contract-compliant for v1 (procedural enforcement provision). Transcript review catches violations post-hoc. Each violation invalidates the run and requires a rerun.

## References

### Commits this session

- `adcf49ea` on `feature/benchmark-v1-scaffold` — feat(codex-collaboration): scaffold benchmark v1 artifact set and operator procedure

### Authority documents

| Document | Location | Role |
|---|---|---|
| Supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Acceptance authority |
| Benchmark contract (v1) | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Benchmark authority |
| Benchmark readiness | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/benchmark-readiness.md` | Prerequisite gate |
| Gatherer plan | `docs/plans/2026-04-14-t04-pre-dialogue-gatherers-and-briefing-assembly.md` | Gatherer design |

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-15_15-00_t04-ac4-closed-benchmark-v1-contract-rewrite.md`
- Prior: `docs/handoffs/archive/2026-04-14_23-30_t04-gatherer-implementation-merged-and-e2e-smoke-run.md`
- Prior: `docs/handoffs/archive/2026-04-14_22-45_t04-gatherer-plan-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_20-17_t04-v1-e2e-verified-pr-106-open.md`
- Prior: `docs/handoffs/archive/2026-04-14_16-30_t04-v1-four-production-surfaces-authored-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_12-55_t04-v1-section-10-authoring-decisions-resolved-and-committed.md`

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `dialogue-supersession-benchmark.md` (full, 366 lines) | Benchmark contract | RC4 is unconditional; RC5 has host caveat; 4-row corpus; evidence budget |
| `benchmark-readiness.md` (full, 278 lines) | Prerequisite gate | 4-item v1 gate; deferred automation surfaces |
| `T-20260330-04 ticket` (full, 114 lines) | T-04 ticket | 7 ACs; AC 1-4 done, AC 5-7 open |
| `codex-collaboration/skills/dialogue/SKILL.md` (170 lines) | Candidate skill | No `-p`/`-n` flags; gatherer dispatch at lines 81-96 |
| `cross-model/skills/dialogue/SKILL.md` (50 lines) | Baseline skill | `-p`/`-n` flags supported |
| `codex-collaboration/agents/dialogue-orchestrator.md` (60 lines) | Candidate orchestrator | Hardcoded constants: turn budget 10, max evidence 15 |
| `cross-model/agents/codex-dialogue.md` (70 lines) | Baseline orchestrator | Accepts posture, turn budget, `scope_envelope` from dispatch |
| `codex-collaboration/agents/context-gatherer-code.md` (40 lines) | Candidate code explorer | Supports `scope_envelope` at line 23 |
| `codex-collaboration/agents/context-gatherer-falsifier.md` (50 lines) | Candidate falsifier | Supports `scope_envelope` at line 23 |
| `codex-collaboration/server/mcp_server.py` (80 lines) | MCP tools | `codex.dialogue.start` accepts `profile` but not posture/turn-budget directly |
| `cross-model/.claude-plugin/plugin.json` | Plugin manifest | Name: `cross-model`, v3.1.3 |
| `codex-collaboration/.claude-plugin/plugin.json` | Plugin manifest | Name: `codex-collaboration`, v0.2.0 |

## Gotchas

### RC4 vs RC5 caveat scope — easy to misread

**Symptom:** Treating posture/turn-budget asymmetry as permitted by the "when the host allows" caveat.

**Root cause:** The caveat appears in run condition 5, but it's easy to mentally extend it to RC4 which is written adjacently. RC4 and RC5 are separate conditions with different graduation.

**Prevention:** Read run conditions individually. The caveat text is specific to its condition.

### B8 `allowed_roots` includes directories that contain benchmark-adjacent paths

**Symptom:** Artifact path contamination — benchmark files becoming legal scouting evidence for the row being scored.

**Root cause:** B8's `candidate_normative_surface` group includes `docs/superpowers/specs/codex-collaboration/` — a broad directory. Any file under that path is in-scope for B8 scouting.

**Prevention:** Always verify `artifact_path` has zero overlap with any corpus row's `allowed_roots` before committing the path. The validation script in this session's narrative can be reused.

### `scope_envelope` support ≠ `scope_envelope` wired

**Symptom:** Claiming mechanical scope enforcement when it's actually prompt-only.

**Root cause:** Agent definitions accepting `scope_envelope` as optional input doesn't mean the slash skill passes it. Support without wiring is not a control surface.

**Prevention:** When claiming control-surface parity, trace the full wiring path from user-invocable surface through dispatch to agent consumption.

## Conversation Highlights

### User's review methodology

The user provided 7 rounds of structured adversarial review, each with: premise check, critical failures (with severity, mechanism, and fix requirements), high-risk assumptions, real-world breakpoints, hidden dependencies, adversarial perspectives applied, patterns and root causes, required changes, and verdict. Verdicts progressed: Reject → Reject → Major revision → Minor revision → Minor revision → Minor revision → Defensible.

### User's review philosophy

The user applied multiple adversarial lenses per round: contract lawyer (exposed RC4/RC5 misreading), contamination attacker (exposed B8 self-referential path), tired operator (exposed contradictory write targets and scoring cues), runtime skeptic (exposed timeout and control-surface parity overstatements), future auditor (exposed artifact misclassification risk), procedure literalist (exposed sequencing contradictions), artifact auditor (exposed schema/example drift), boundary-case operator (exposed mixed-mode gap).

### Key user direction patterns

User provided the adversarial review findings as structured code comments (file, line range, priority, confidence) followed by a full review document. Every finding included: what's wrong, why it matters, how it fails in practice, severity, and what needs to change. This pattern produced precise, actionable feedback that could be implemented without interpretation.

## User Preferences

### Review-driven development for benchmark artifacts

User strongly prefers structured adversarial review for benchmark-integrity artifacts. Each round was a complete review with multiple adversarial lenses, not a casual glance. This pattern should be expected for any future benchmark-related work — the user will review thoroughly and reject until the artifact is defensible.

### Contract text is authoritative

User treats contract text literally and precisely. The RC4/RC5 distinction (unconditional vs. caveated) was enforced exactly. Paraphrasing or extending contract provisions beyond their literal scope is not acceptable — the user will catch it and reject.

### Honest documentation over false confidence

User prefers documents that state what is blocked, unknown, or unimplemented rather than rationalizing limitations as acceptable. The "prompt-only" scope enforcement label was preferred over the false "matched via scope_envelope" claim. The "blocked" posture/turn-budget classification was preferred over the rationalized "acceptable asymmetry."

### Artifacts must be self-identifying

User requires that persisted artifacts carry their own mode/status markers. Rehearsal runs must be distinguishable from scored runs in the schema, not just in the procedure prose. Summary templates must have explicit rehearsal states. The principle: a future reader opening the repo artifacts without conversation context must be able to determine the artifact's evidentiary status.
