---
date: 2026-04-15
time: "15:00"
created_at: "2026-04-15T19:00:00Z"
session_id: ada015f4-5d56-4e6f-82de-cb1127c6cb69
resumed_from: docs/handoffs/archive/2026-04-14_23-30_t04-gatherer-implementation-merged-and-e2e-smoke-run.md
project: claude-code-tool-dev
branch: main
commit: 1e08c397
title: "T-04 AC-4 closed, timeout bumped to 1200s, benchmark v1 contract rewrite landed"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/runtime.py
  - docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md
  - docs/plans/t04-t4-scouting-position-and-evidence-provenance/benchmark-readiness.md
  - docs/plans/t04-t4-scouting-position-and-evidence-provenance/foundations.md
  - docs/plans/t04-t4-scouting-position-and-evidence-provenance/state-model.md
---

# T-04 AC-4 Closed, Timeout Bumped to 1200s, Benchmark v1 Contract Rewrite Landed

## Goal

Validate the v2 `/dialogue` pipeline end-to-end with the 300s timeout fix from last session, then close AC-4 and advance toward AC-5 through AC-7.

**Trigger.** Resumed from `2026-04-14_23-30` handoff. Last session implemented the gatherer pipeline (PR #107), ran an E2E smoke test (pipeline passed but Codex dialogue timed out at 30s), and fixed the timeout to 300s (`e13a1b87`). The primary next step was: re-run E2E smoke test with 300s timeout to validate AC-4.

**Stakes.** AC-4 requires "dialogue runs produce a final synthesis with bounded evidence citations and a convergence result." Last session proved the pipeline mechanics work but lacked dialogue-tier citations because the Codex dialogue timed out before producing any. This session needed to demonstrate that the orchestrator's post-seed verification path actually exercises and tags evidence correctly.

**Success criteria achieved this session:**

1. E2E smoke test ran with 300s timeout — **achieved** (dialogue completed 3 Codex turns before timing out on turn 5).
2. Dialogue-tier citations produced — **achieved** (all 10 synthesis citations carry `citation_tier: "dialogue"`).
3. AC-4 closed — **achieved** (user confirmed based on contract wording analysis).
4. Timeout bumped to 1200s — **achieved** (`71f442ce`, merged to main, pushed).
5. Benchmark v1 contract rewrite — **achieved** (`1e08c397`, merged to main).

**Position in the T-04 arc:**

| Session | Role | Artifact |
|---|---|---|
| 2026-04-13 | v1 plan drafting and approval | Plan at `main@73f8c9c1` |
| 2026-04-14 12:55 | Section 10 authoring decisions | Addendum committed |
| 2026-04-14 16:30 | Four production surfaces authored | Committed `05b7db3a` |
| 2026-04-14 20:17 | E2E verified, report committed, PR #106 open | `7a1bd077`, PR #106 |
| 2026-04-14 22:45 | PR #106 merged, gatherer plan designed and committed | Merged `c3c11fa4`, plan at `99472736` |
| 2026-04-14 23:30 | Gatherer implementation merged, E2E smoke run, timeout fix | PR #107 merged `d478c0d7`, timeout fix `e13a1b87` |
| **2026-04-15 15:00 (this)** | **AC-4 closed, timeout 1200s, benchmark v1 rewrite** | **Timeout `71f442ce`, contract `1e08c397`** |
| Next | Scaffold benchmark artifacts, write operator procedure, execute benchmark | |

## Session Narrative

**Phase 1 — E2E smoke test (~20 min, ~15 min wall clock for orchestrator).**

Loaded the `2026-04-14_23-30` handoff. Session started with `/reload-plugins` already executed (visible in session init). Verified current state: `main` at `e13a1b87` (timeout fix), clean working tree. Invoked `/dialogue` with objective: "How does the codex-collaboration dialogue pipeline handle gatherer failure and retry? Trace the execution path from gatherer dispatch through assembly, including the retry mechanism for gatherers that produce insufficient tagged output."

Executed the full v2 procedure. Preflight (steps 1-4) passed — session ID read, stale cleanup ran (needed `CLAUDE_PLUGIN_DATA` env var, same gotcha as last session), no active run. Generated `run_id` `940c5039-87fc-4384-9027-c09f107f8c6d`, acquired lock.

Assumption extraction (step 5a) produced 4 assumptions: A1 (retry triggers before fallback), A2 (retry threshold based on line count), A3 (assembly is deterministic), A4 (failed gatherers don't block orchestrator). Plus 8 key terms.

Gatherer dispatch (step 5b) launched both in parallel. Code explorer returned 30 tagged lines (28 CLAIM, 2 OPEN) in ~78s. Falsifier returned 7 tagged lines (3 CONFIRM, 1 COUNTER, 3 OPEN) in ~74s. Key improvement: falsifier produced tagged output on first attempt (7 >= 4 threshold), no retry needed. Last session it produced 0 and required retry.

Assembly (step 5c) ran the 10-step pipeline: no retry needed (both gatherers above threshold), no fallback, 0 lines discarded, 1 COUNTER (no capping needed), no credential patterns, no cross-gatherer duplicates, 0 provenance unknowns. Final: 34 citations across 6 unique files, no warnings.

Orchestrator dispatch (step 7) received the assembled briefing prepended to the dispatch prompt. The orchestrator detected the briefing sentinel, ran Phase 1 scouting, and completed 3 successful Codex dialogue turns before timing out on turn 5. The production synthesis artifact was emitted with `termination_code: "error"`, `converged: false`, 15 claims (4 supported, 9 unverified, 1 not_scoutable, 0 contradicted), and 10 synthesis citations all carrying `citation_tier: "dialogue"`.

Lock released via `trash` in the finally block.

**Phase 2 — AC-4 assessment and timeout bump (~10 min).**

User assessed AC-4 status. User's analysis: the ticket requires "a final synthesis with bounded evidence citations and a convergence result," not `converged: true`. The dialogue contract defines budget exhaustion or tool failure as valid `converged: false` terminal states. The gatherer plan says convergence logic is unchanged and Codex-claim-only. So a valid `converged: false` artifact satisfies AC-4. The new evidence (dialogue-tier citations) was the missing piece — proves the orchestrator's post-seed verification path exercises and tags evidence correctly.

User directed: "AC-4 is done. But before we close it, we should increase the length of the timeout even more. To be safe, let's increase it to 1200."

Created `fix/codex-timeout-1200` branch. Changed both timeout sites in `runtime.py`: `request_timeout` 300.0 → 1200.0 (line 20) and notification timeout 300.0 → 1200.0 (line 144). 566 tests passed. Committed at `71f442ce`, merged to main (fast-forward, same pattern as last session's timeout fix — small fix, clear root cause, direct merge). Pushed to origin.

**Phase 3 — Ticket review and benchmark analysis (~20 min).**

Checked for closeable tickets. Four remain open: T-04 (dialogue parity), T-05 (execution domain), T-06 (promotion/delegate UX), T-07 (analytics). T-04 is closest but AC 5-7 (benchmark + retirement decision) are still open.

Reviewed the benchmark spec (`dialogue-supersession-benchmark.md`, 297 lines) and the T4-BR-07 prerequisite gate (`benchmark-readiness.md`). The old scored-run gate had 8 items, all required before any scored run. Key blocker items: mechanical omission-audit proof engine, validator-grade methodology schemas, narrative-claim inventory tooling, transcript parser/diff engine.

Assessed the situation: the old gate mixed two jobs — making the retirement decision and building future automation infrastructure. User agreed and directed a controlled contract rewrite rather than informal descoping or deferral.

**Phase 4 — Benchmark contract rewrite and review (~30 min).**

User authored the contract rewrite across three files (dialogue-supersession-benchmark.md, benchmark-readiness.md, foundations.md). I reviewed the changes and found 3 findings:

- P2: `max_evidence` referenced but never defined — value and unit needed
- P2: Pass rule doesn't clarify that scope violations cause invalidation not failure
- P3: "Runner or operator" ambiguous for v1

User addressed all three findings plus a follow-on stale cross-reference in state-model.md. Key additions: `max_evidence` defined using T4 state-model unit (completed evidence records), asymmetric values for v1 (`baseline_max_evidence = 5`, `candidate_max_evidence = 15`), invalidation clarification after pass rule, enforcement wording tightened to "operator."

Second-pass review: zero findings. Committed at `1e08c397` on `docs/benchmark-v1-contract-rewrite` branch, merged to main, branch deleted.

## Decisions

### Decision 1: AC-4 closed based on contract wording analysis

**Choice:** Close AC-4 despite `converged: false` in the smoke test.

**Driver:** User's contract analysis: ticket AC-4 requires "a final synthesis with bounded evidence citations and a convergence result" — not `converged: true`. The dialogue contract separately defines budget exhaustion or tool failure as valid `converged: false` terminal states. The gatherer plan explicitly states convergence logic is unchanged and remains Codex-claim-only. User quoted: "If we now insist on `converged: true` as the bar for AC-4, that would be a stricter criterion than the repo currently states."

**Alternatives considered:**
- **Require `converged: true`** — rejected because it imposes a stricter criterion than the ticket's own wording and conflates runtime reliability (Codex API latency) with pipeline correctness.
- **Defer AC-4 until a fully converged run** — rejected because the missing piece (dialogue-tier citations) is now demonstrated; the remaining gap is timeout tuning, not pipeline architecture.

**Trade-offs accepted:** AC-4 is closed without a fully converged run. If a future session discovers that dialogue-tier citations only appear in partial runs (not converged ones), AC-4's closure would be premature. Mitigated by the 1200s timeout bump, which should allow most runs to complete.

**Confidence:** High (E2) — based on both the contract text analysis and the observable evidence (dialogue-tier citations in production synthesis).

**Reversibility:** High — AC-4 is a ticket checkbox, not a code change. Can be reopened if evidence warrants it.

**Change trigger:** If the benchmark reveals that dialogue-tier citations behave differently in converged vs. non-converged runs.

### Decision 2: Bump timeout to 1200s

**Choice:** Increase both `request_timeout` and notification timeout from 300s to 1200s in `runtime.py`.

**Driver:** 300s was insufficient — the orchestrator completed 3 Codex turns but timed out on turn 5. User directed: "To be safe, let's increase it to 1200."

**Alternatives considered:**
- **Per-operation timeouts** (shorter for `dialogue_start`, longer for `dialogue_reply`) — more surgical but requires changes to the MCP tool implementation. Deferred to future work if 1200s proves problematic.
- **Keep 300s** — rejected because it demonstrably fails for complex dialogue turns.

**Trade-offs accepted:** A genuinely stuck Codex connection takes 20 minutes to time out instead of 5. Accepted because dialogue replies legitimately take 60+ seconds for complex prompts with full scouting context.

**Confidence:** High (E2) — root cause identified precisely. 300s was enough for 3/5 turns; 1200s provides 4x headroom.

**Reversibility:** High — single value change in two locations.

**Change trigger:** If 1200s causes unacceptable hang time when Codex is genuinely unavailable.

### Decision 3: Narrow benchmark contract for v1 retirement decision

**Choice:** Rewrite the benchmark contract to reduce the 8-task corpus to 4 high-signal rows (B1, B3, B5, B8), replace the 8-item scored-run gate with a 4-item v1 gate, switch to procedural scope enforcement, and demote `converged_within_budget` to a diagnostic metric.

**Driver:** User's analysis: "The old benchmark mixed two jobs: making the retirement decision, and building a future automation/reproducibility framework. That made AC-5 through AC-7 much more expensive than the decision warranted." The benchmark contract's own change-control rules (`dialogue-supersession-benchmark.md:281`) explicitly allow amendments with explanation.

**Alternatives considered:**
- **Build the full T4-BR-07 stack** — rejected as too expensive for the value of a one-time decision. User: "Building the full T4-BR-07 stack now is too expensive for the value of the decision."
- **Run an unscored calibration** — rejected because the benchmark spec classifies calibration runs as non-evidentiary that cannot drive the retirement decision.
- **Defer AC-5 through AC-7** — rejected because the rewrite makes the benchmark executable now without deferring the decision indefinitely.
- **Informal descoping** — rejected by user: "I would not 'descope the benchmark' informally. I would either defer AC-5 through AC-7, or do a deliberate contract rewrite."

**Trade-offs accepted:**
- Manual adjudication is still the dominant cost (4 tasks x 2 systems = 8 syntheses, ~80-160 claim adjudications).
- Scope compliance depends on operator discipline rather than runtime enforcement.
- Historical docs still reference the superseded 8-task, automation-heavy benchmark — left as historical artifacts.
- Asymmetric evidence budgets (`baseline_max_evidence = 5`, `candidate_max_evidence = 15`) preserve executability but don't normalize evidence-budget pressure.

**Confidence:** High (E2) — analysis grounded in both the contract text and the measured gap between the old gate's requirements and the decision's actual needs.

**Reversibility:** Medium — the contract has change-control rules that allow future revisions. However, reverting to the old 8-item gate would mean rebuilding the automation infrastructure.

**Change trigger:** If the benchmark becomes a repeated operational workflow rather than a one-time retirement decision, the automation-heavy proof surfaces become worthwhile.

### Decision 4: Define `max_evidence` as completed evidence records with asymmetric values

**Choice:** `max_evidence` uses the T4 state-model unit (`evidence_count = len(evidence_log)`, not raw tool calls). Fixed per-system: `baseline_max_evidence = 5`, `candidate_max_evidence = 15`.

**Driver:** My review finding: `max_evidence` was referenced operationally in the rewritten contract without defining the unit or value. User chose to align with the existing T4/runtime vocabulary rather than inventing a benchmark-only unit.

**Alternatives considered:**
- **Single shared cap for both systems** — rejected because baseline (cross-model with plugin-side context-injection) and candidate (codex-collaboration with Claude-side scouting) produce evidence records at different granularities. A shared cap would either starve the candidate or give the baseline unused budget.
- **Raw tool-call budget** — rejected because tool calls and evidence records are different units in the T4 model; aligning with the existing vocabulary prevents confusion.

**Trade-offs accepted:** Asymmetric values mean evidence-budget pressure is not normalized across systems. This is intentional for v1 — the comparison is "does the candidate produce adequate quality within its natural evidence budget," not "does the candidate match the baseline under identical budget constraints."

**Confidence:** High (E2) — grounded in both the T4 state model definition and the current implementations' actual evidence production patterns.

**Reversibility:** High — values are under benchmark change control. Changing requires editing the contract and rerunning comparisons.

**Change trigger:** If the asymmetry is shown to bias the comparison (e.g., candidate's extra budget inflates supported_claim_rate beyond what the evidence quality warrants).

### Decision 5: Demote convergence from pass rule to diagnostic metric

**Choice:** `converged_within_budget` remains in the artifact set but is excluded from the v1 pass rule.

**Driver:** My analysis, accepted by user: "shared Codex dialogue latency can dominate the result even when the evidence path is otherwise viable." Our smoke test demonstrated this — 3 successful turns with good evidence, then a timeout. The convergence failure measured infrastructure reliability, not scouting quality.

**Alternatives considered:**
- **Keep convergence in pass rule with matched timeout** — viable but adds a run-condition dependency (both systems must use identical timeout settings). Added `dialogue-timeout` to run condition 5 instead, so convergence is at least recordable under fair conditions.

**Trade-offs accepted:** Removing convergence from the pass rule means a candidate system that never converges but produces high-quality partial syntheses could pass. Mitigated because convergence is still recorded and visible in artifacts — the decision-maker can weigh it.

**Confidence:** High (E2) — grounded in observed behavior (our smoke test) and the Codex API's documented latency characteristics.

**Reversibility:** High — add convergence back to the pass rule in a future contract revision.

**Change trigger:** If Codex API latency stabilizes to the point where convergence failures reliably indicate scouting quality rather than infrastructure issues.

## Changes

### `packages/plugins/codex-collaboration/server/runtime.py` (MODIFIED, +2/-2)

**Purpose:** Bump Codex app server timeouts from 300s to 1200s.

**Approach:** Changed `request_timeout` default at line 20 and notification timeout at line 144. Same two-site pattern as the previous 30→300 bump.

### `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` (MODIFIED, +155/-73)

**Purpose:** Narrow the benchmark contract for v1 retirement decision.

**Approach:** Added Revision Note explaining the change rationale. Reduced corpus from 8 to 4 rows (B1, B3, B5, B8), added deferred-rows callout routing restoration through Change Control. Added Evidence Budget section defining `max_evidence` with asymmetric per-system values. Added run conditions 10-11 for `allowed_roots`/`max_evidence` recording. Added procedural enforcement description. Rewrote Scored-Run Prerequisite Status from blocking to ready. Added manual claim inventory with second-pass completeness review. Added Scope Compliance Review section. Demoted `converged_within_budget` to diagnostic. Reduced pass rule from 4 conditions to 3 with invalidation clarification.

### `docs/plans/t04-t4-scouting-position-and-evidence-provenance/benchmark-readiness.md` (MODIFIED, +69/-70)

**Purpose:** Replace 8-item scored-run gate with 4-item v1 gate.

**Approach:** Rewrote T4-BR-07 from "Eight-Item Prerequisite Gate" to "Four-Item v1 Prerequisite Gate." Changed enforcement wording from "runner or manifest validator" to "operator." Updated T4-BR-08 from "Policy-influencing calibration" to "Benchmark rehearsals." Reframed T4-BR-09's 10 amendment rows as "design inventory" rather than prerequisites. Updated F6/F7/F11 blocker language to explicitly allow manual v1 benchmark to proceed. Updated F11 Consumer Expectations scope to "future automation-heavy benchmark revisions."

### `docs/plans/t04-t4-scouting-position-and-evidence-provenance/foundations.md` (MODIFIED, +12/-13)

**Purpose:** Align transcript fidelity layers with v1 benchmark.

**Approach:** Renamed T4-F-13's two layers from "Spec sub-dependency" and "Operational readiness" to "v1 scored-benchmark layer" and "Future automation layer." Updated progression description to match the v1 gate.

### `docs/plans/t04-t4-scouting-position-and-evidence-provenance/state-model.md` (MODIFIED, +4/-2)

**Purpose:** Fix stale cross-reference to old prerequisite gate.

**Approach:** Updated `max_evidence` section to point to the benchmark contract's Evidence Budget section instead of the old "prerequisite item 6." Updated line number reference for benchmark change control.

## Codebase Knowledge

### Timeout chain architecture

| Level | Location | Value | What it bounds |
|---|---|---|---|
| Inner | `runtime.py:20` (`request_timeout`) | 1200.0 (was 300.0, was 30.0) | JSON-RPC client → Codex app server response time |
| Inner | `runtime.py:144` (notification timeout) | 1200.0 (was 300.0, was 60.0) | Wait for next notification from Codex during turn execution |
| Outer | Claude Code MCP transport | (system default) | Claude Code → codex-collaboration MCP server |

The error "JSON-RPC read failed: timed out waiting for message" is raised at `jsonrpc_client.py:142` when `_message_queue.get(timeout=effective_timeout)` returns `Empty`.

### Benchmark contract structure

The benchmark contract (`dialogue-supersession-benchmark.md`) is the single authority for the context-injection retirement decision. It defines:

- **Fixed corpus** (4 rows: B1 architecture, B3 code review, B5 policy audit, B8 supersession analysis)
- **Run conditions** (11 items including same commit, same model, scoped `allowed_roots`, `max_evidence`)
- **Evidence budget** (`baseline_max_evidence = 5`, `candidate_max_evidence = 15`, T4 state-model unit)
- **Pass rule** (3 conditions: safety = 0, false claims <= baseline, supported_claim_rate within 0.10)
- **Artifact set** (`manifest.json`, `runs.json`, `adjudication.json`, `summary.md`)

### T4-BR-07 v1 prerequisite gate

| # | Category | What it gates |
|---|----------|---------------|
| 1 | Comparability | Same conditions for baseline/candidate pair |
| 2 | Scope and evidence discipline | Controlled search space and evidence budget |
| 3 | Artifact reviewability | Post-hoc review possible |
| 4 | Manual adjudication | Claim inventory grounded in reviewed claim set |

The old 8-item gate's deferred items (items 5-8 of the old gate) are preserved in T4-BR-09 as "design inventory" for future automation-heavy revisions.

### E2E smoke test results (this session)

| Pipeline stage | Result | Detail |
|---|---|---|
| Preflight (steps 1-4) | Pass | Repo root, session ID, stale cleanup, no active run |
| Assumptions (step 5a) | Pass | 4 assumptions, 8 key terms |
| Gatherers (step 5b) | Pass (no retry) | Code explorer: 30 lines. Falsifier: 7 lines (first attempt) |
| Assembly (step 5c) | Pass | 34 citations, 6 unique files, no warnings |
| Orchestrator Phase 1 | Pass | Briefing detected, scouting completed |
| Codex dialogue | Partial | 3 turns completed, timeout at turn 5 |
| Synthesis artifact | Pass | 10 dialogue-tier citations, `converged: false` |
| Lock lifecycle | Pass | Acquired, held, released via `trash` |

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `packages/plugins/codex-collaboration/server/runtime.py:15-27,139-153` | Timeout sites | Two locations: `request_timeout` (line 20) and notification timeout (line 144) |
| `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` (full, 297→344 lines) | Benchmark contract | 8-task corpus, 8-item gate, 4-condition pass rule (pre-rewrite) |
| `docs/plans/t04-t4-scouting-position-and-evidence-provenance/benchmark-readiness.md` (full, 277 lines) | Prerequisite gate | T4-BR-07 had 8 items; all required before scored runs |
| `docs/plans/t04-t4-scouting-position-and-evidence-provenance/foundations.md:275-324` | Transcript fidelity | T4-F-13: two-layer dependency (spec + operational readiness) |
| `docs/plans/t04-t4-scouting-position-and-evidence-provenance/state-model.md:480-494` | max_evidence cross-ref | Stale reference to "prerequisite item 6" |
| `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` (full, 114 lines) | T-04 ticket | 7 ACs; AC 1-4 done, AC 5-7 open (benchmark + retirement) |
| `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md:1-50` | T-05 ticket | Execution domain infrastructure — unstarted, separate workstream |

## Context

### T-04 acceptance criteria status after this session

| AC | Description | Status | Evidence |
|---|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) | `skills/dialogue/SKILL.md` |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) | `agents/dialogue-orchestrator.md` |
| 3 | Gatherer agents exist and use Claude-side tools | Done (PR #107) | Both agents with Glob/Grep/Read |
| 4 | Synthesis with bounded citations and convergence | **Done** | Dialogue-tier citations + `converged: false` terminal artifact |
| 5 | Benchmark contract executed on fixed corpus | **Open** | Benchmark contract rewritten; execution next |
| 6 | Benchmark result recorded with per-task metrics | **Open** | Depends on AC-5 |
| 7 | Context-injection retirement decision explicit | **Open** | Depends on AC-6 |

### Mental model for this session

This session transitions from **building** to **evaluating**. AC 1-4 built the dialogue pipeline; AC 5-7 evaluate whether it's good enough. The benchmark contract rewrite was necessary to make that evaluation executable — without it, the evaluation was blocked by infrastructure prerequisites that served automation, not the decision.

### Open tickets

| Ticket | ID | Status | Next |
|---|---|---|---|
| Dialogue parity & scouting retirement | T-04 | Open (AC 1-4 done) | Benchmark execution |
| Execution-domain foundation | T-05 | Open (unstarted) | Separate workstream |
| Promotion flow & delegate UX | T-06 | Open (blocked by T-05) | — |
| Analytics reviewer & cutover | T-07 | Open | Separate workstream |

## Learnings

### Falsifier first-run reliability is stochastic, not structural

**Mechanism.** Last session the falsifier produced 0 tagged lines on first attempt (31 tool calls, all narrative exploration) and needed retry. This session it produced 7 tagged lines on first attempt — above the <4 retry threshold.

**Evidence.** Session comparison: 2026-04-14 falsifier first run = 0 tagged lines in 53s (retry needed). 2026-04-15 falsifier first run = 7 tagged lines in 74s (no retry needed). Same agent definition, same `maxTurns: 20`.

**Implication.** The retry mechanism is still valuable as a safety net, but the case for strengthening the falsifier's initial prompt is weaker than it appeared after a single failure. Worth monitoring across more runs before investing in prompt changes.

### Benchmark contract rewrite pattern: keep fairness, defer automation

**Mechanism.** The original benchmark contract bundled the retirement decision with automation-heavy proof surfaces (omission-audit engine, transcript parser, validator-grade schemas). Separating "is this comparison fair?" (scope equivalence, evidence budget control, manual adjudication) from "is this comparison repeatable by automation?" (parsers, validators, proofs) made AC-5 through AC-7 executable without building infrastructure whose value is primarily future repeatability.

**Evidence.** Old gate: 8 items, none satisfied, all required. New gate: 4 items, all achievable through operator procedure + manual review.

**Implication.** For one-time decisions, procedural enforcement with human review is sufficient. Mechanical enforcement is worthwhile when the procedure becomes a repeated operational workflow.

### `CLAUDE_PLUGIN_DATA` env var still required for manual script invocation

**Mechanism.** `clean_stale_shakedown.py` requires `CLAUDE_PLUGIN_DATA` to be set. When invoked via Bash rather than the plugin runtime, the env var isn't set.

**Evidence.** Step 4 (stale cleanup) failed with "CLAUDE_PLUGIN_DATA not set" until prefixed with `CLAUDE_PLUGIN_DATA=/Users/jp/.claude/plugins/data/codex-collaboration-inline`.

**Implication.** Same gotcha as last session. If this becomes a recurring pattern, consider a wrapper that sets the env var, or have the script derive the path from its own location.

## Next Steps

### 1. Scaffold benchmark artifact skeleton

**Dependencies:** Benchmark contract rewrite landed at `1e08c397`.

**What to do:**
1. Choose a stable repo path for benchmark artifacts (suggest `docs/benchmarks/v1/`)
2. Create initial `manifest.json` skeleton with: commit SHA placeholder, model settings, `baseline_max_evidence: 5`, `candidate_max_evidence: 15`, row-specific `allowed_roots` for B1, B3, B5, B8
3. Create empty `runs.json`, `adjudication.json`, `summary.md` scaffolds matching the contract's artifact spec
4. Write an operator procedure document that walks through: how to run a single baseline/candidate pair, how to record results, how to adjudicate claims, how to compute aggregate metrics

**What to read first:** `dialogue-supersession-benchmark.md` (current version at `1e08c397`), specifically the Required Benchmark Artifacts section (lines 224-244) and the Evidence Budget section (lines 188-203).

**Potential obstacles:** The `allowed_roots` for each row need to be transcribed from the corpus table into the manifest — some rows (especially B8's anchored decomposition) have multiple path groups that need careful mapping.

### 2. Execute benchmark v1

**Dependencies:** Artifact skeleton (#1) must exist.

**What to do:**
1. Fix a commit for the benchmark run
2. For each of the 4 rows (B1, B3, B5, B8): run baseline (cross-model `/dialogue`), run candidate (codex-collaboration `/dialogue`), under matching conditions
3. Retain raw transcripts and final syntheses
4. Manual claim adjudication with second-pass completeness review
5. Compute aggregate metrics and apply pass rule
6. Record result in `summary.md`

**Potential obstacles:** The benchmark requires 8 dialogue runs (4 rows x 2 systems). Each run involves a full dialogue lifecycle including Codex API calls. Total wall-clock time could be significant. The 1200s timeout should accommodate most turns, but complex rows (especially B8 with its multi-root decomposition) may push limits.

### 3. Close AC-5 through AC-7 based on benchmark result

**Dependencies:** Benchmark execution (#2).

**What to do:** Record the benchmark result, update the retirement decision from provisional to explicit, close the remaining ACs on the T-04 ticket.

## In Progress

**Clean stopping point — AC-4 closed, timeout bumped, benchmark contract rewritten. No work in flight.**

- **Approach:** E2E validation → contract analysis → contract rewrite → review → merge.
- **State:** Complete. Three commits on main: `71f442ce` (timeout), `1e08c397` (contract rewrite). Both pushed.
- **Working:** Full v2 pipeline with 1200s timeouts. Benchmark contract executable under the v1 gate.
- **Not working:** Nothing broken. Benchmark not yet executed.
- **Next action:** Scaffold benchmark artifact skeleton and write operator procedure.

## Open Questions

### 1. Is 1200s sufficient for all Codex dialogue turns?

**Context:** 300s was enough for 3/5 turns. 1200s provides 4x headroom. But complex rows (B8's multi-root decomposition) may generate longer Codex replies.

**Impact:** If 1200s is still insufficient, per-operation timeouts would be more surgical.

**Decision pending until:** Benchmark execution. If any run times out at 1200s, revisit.

### 2. Should the falsifier's initial prompt be strengthened?

**Context:** First-run failure was stochastic (0 lines last session, 7 lines this session). Retry mechanism handles it gracefully.

**Impact:** Low — retry works. ~60 seconds overhead when it triggers.

**Decision pending until:** After observing more `/dialogue` runs. If first-run failure rate exceeds ~30%, prompt strengthening is worthwhile.

### 3. Where should benchmark artifacts live?

**Context:** The contract says "under a stable repo path chosen by the implementing ticket." Options: `docs/benchmarks/v1/`, `docs/benchmarks/dialogue-supersession/`, or alongside the spec at `docs/superpowers/specs/codex-collaboration/benchmarks/`.

**Impact:** Cosmetic, but the path should be stable since the contract references it.

**Decision pending until:** Benchmark scaffold step.

## Risks

### 1. Manual adjudication is the dominant benchmark cost

**Impact:** 4 rows x 2 systems = 8 syntheses. At ~10-20 claims per synthesis, that's 80-160 individual claim adjudications with second-pass completeness review. This is significant manual labor.

**Mitigation:** Focus on high-signal rows first (B3 safety, B8 supersession). If early rows show clear pass/fail, the remaining rows provide confirmation rather than discovery.

### 2. Asymmetric evidence budgets may bias comparison

**Impact:** `candidate_max_evidence = 15` vs. `baseline_max_evidence = 5`. If the candidate's extra budget inflates `supported_claim_rate`, the comparison is unfair in the candidate's favor.

**Mitigation:** The values match the systems' natural evidence production patterns. The asymmetry preserves executability. If the adjudicator observes quality inflation from extra evidence, note it in `summary.md`.

### 3. Codex API latency during benchmark execution

**Impact:** Each dialogue run depends on Codex API availability and response times. 8 runs over potentially several hours means API instability could invalidate runs.

**Mitigation:** 1200s timeout provides headroom. Invalid runs are rerun, not failed. Consider running baseline and candidate for each row back-to-back to minimize temporal variance.

## References

### Commits this session

- `71f442ce` on `fix/codex-timeout-1200` — fix(codex-collaboration): bump Codex app server timeouts from 300s to 1200s (merged to main directly)
- `1e08c397` on `docs/benchmark-v1-contract-rewrite` — docs(codex-collaboration): narrow benchmark contract for v1 retirement decision (merged to main)

### Authority documents

| Document | Location | Role |
|---|---|---|
| Supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Acceptance authority |
| Benchmark contract (v1) | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Benchmark authority |
| Benchmark readiness | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/benchmark-readiness.md` | Prerequisite gate |
| Gatherer plan | `docs/plans/2026-04-14-t04-pre-dialogue-gatherers-and-briefing-assembly.md` | Gatherer design |

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-14_23-30_t04-gatherer-implementation-merged-and-e2e-smoke-run.md`
- Prior: `docs/handoffs/archive/2026-04-14_22-45_t04-gatherer-plan-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_20-17_t04-v1-e2e-verified-pr-106-open.md`
- Prior: `docs/handoffs/archive/2026-04-14_16-30_t04-v1-four-production-surfaces-authored-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_12-55_t04-v1-section-10-authoring-decisions-resolved-and-committed.md`

## Gotchas

### `CLAUDE_PLUGIN_DATA` not set for manual script invocation (recurring)

**Symptom:** `python3 scripts/clean_stale_shakedown.py` fails with "CLAUDE_PLUGIN_DATA not set."

**Root cause:** Plugin scripts expect environment variables set by the plugin runtime. Manual Bash invocations don't have these variables.

**Prevention:** Prefix manual invocations: `CLAUDE_PLUGIN_DATA=/Users/jp/.claude/plugins/data/codex-collaboration-inline python3 scripts/clean_stale_shakedown.py`

### Stale old-gate references in historical docs

**Symptom:** Searching for "8-task corpus" or "eight-item" finds references in `docs/reviews/`, `docs/plans/archive/`, `docs/plans/.../crosswalk.md`, and `docs/plans/2026-04-07-t7-executable-slice-definition.md`.

**Root cause:** The benchmark contract rewrite intentionally left historical docs as-is.

**Prevention:** These are historical artifacts, not live references. The current authority is `dialogue-supersession-benchmark.md` at `1e08c397`.

## Conversation Highlights

### User's AC-4 contract analysis

User provided a detailed analysis of the ticket's AC-4 wording, cross-referencing the ticket, the dialogue contract, and the gatherer plan to argue that `converged: false` satisfies the requirement. Key quote: "The key distinction is in the contract wording. The ticket requires that dialogue runs produce 'a final synthesis with bounded evidence citations and a convergence result,' not that every smoke run reaches `converged: true`."

### User's benchmark rewrite philosophy

User rejected informal descoping in favor of a controlled contract rewrite. Key quote: "I would not 'descope the benchmark' informally. I would either defer AC-5 through AC-7, or do a deliberate contract rewrite that replaces the current benchmark with a smaller one."

User's keep/cut framework was precise: keep fairness controls (scope equivalence, evidence budget), cut automation infrastructure (proof engine, validator schemas, transcript parser). Key insight: "not all eight prerequisite items are 'ceremony.' Scope equivalence, evidence-budget control, and invalid-run auditability are load-bearing for a fair comparison. The biggest removable cost is the proof/tooling layer, not the comparability layer."

### User's review discipline (continued)

User authored the contract rewrite, I reviewed with 3 findings (2 P2, 1 P3), user addressed all 3 plus a follow-on stale cross-reference. Second-pass review: zero findings. Same two-round pattern as previous sessions.

### User direction on merging patterns

User directed merge-to-main for the timeout fix ("merge to main directly") — same fast-path as last session's timeout fix. For the contract rewrite, user invoked `/merge-branch`. Both follow the established pattern: small, single-purpose changes with clear scope go through fast path.

## User Preferences

### Contract analysis before closure

User does not close acceptance criteria casually. AC-4 closure came with explicit contract wording analysis cross-referencing three documents. Future sessions should expect similar rigor for AC-5 through AC-7.

### Controlled rewrites over informal waivers

User strongly prefers deliberate contract amendments with documented rationale over informal descoping. Quote: "I would not 'descope the benchmark' informally."

### Keep/cut framework for scope reduction

When reducing scope, user distinguishes "load-bearing" constraints from "ceremony." Quote: "The biggest removable cost is the proof/tooling layer, not the comparability layer." Apply this framework to future scope discussions.

### Next steps specified by user

User explicitly stated the next practical step: "define the stable artifact path, create the initial `manifest.json` / `runs.json` / `adjudication.json` / `summary.md` scaffolds, and write the operator procedure for the four retained rows." This is specific enough to start immediately in the next session.
