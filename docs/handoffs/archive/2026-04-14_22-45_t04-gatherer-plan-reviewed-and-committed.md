---
date: 2026-04-14
time: "22:45"
created_at: "2026-04-15T02:45:30Z"
session_id: 19092f34-eb31-4c02-ab41-8a33b7ace581
resumed_from: docs/handoffs/archive/2026-04-14_20-17_t04-v1-e2e-verified-pr-106-open.md
project: claude-code-tool-dev
branch: feature/t04-pre-dialogue-gatherers
commit: 99472736
title: "T-04 gatherer plan reviewed through 6 rounds and committed"
type: handoff
files:
  - docs/plans/2026-04-14-t04-pre-dialogue-gatherers-and-briefing-assembly.md
  - docs/plans/2026-04-14-t04-v1-first-live-dialogue-report.md
  - packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md
---

# T-04 Gatherer Plan Reviewed Through 6 Rounds and Committed

## Goal

Review and merge PR #106 (T-04 v1 surfaces), then design the next T-04 slice: pre-dialogue gatherer agents and briefing assembly for codex-collaboration.

**Trigger.** Resumed from `2026-04-14_20-17` handoff. User directed: "Review PR #106, then move to the next codex-collaboration build item." The handoff's next steps were explicit: review PR, merge, consult supersession ticket.

**Stakes.** PR #106 is the entire code-level deliverable of T-04 v1 — four production surfaces plus a verification report. The design plan is the second production slice under T-04, advancing acceptance criteria 3 (gatherer agents) and 4 (synthesis with bounded citations and convergence). Without this design, implementation would start without locked decisions on lock lifecycle, containment scope, briefing assembly, and artifact schema.

**Success criteria achieved this session:**

1. PR #106 reviewed by three specialized agents, two fixes applied, pushed, merged — **achieved** (merged `c3c11fa4`).
2. Supersession ticket read and next build item identified — **achieved** (gatherer agents, criterion 3).
3. Design discussion completed and all architectural decisions locked — **achieved** (10 decisions).
4. Design plan drafted, reviewed through 6 rounds (11 findings), and committed — **achieved** (`99472736`).

**Position in the T-04 arc:**

| Session | Role | Artifact |
|---|---|---|
| 2026-04-13 | v1 plan drafting and approval | Plan at `main@73f8c9c1` |
| 2026-04-14 12:55 | §10 authoring decisions | Addendum committed |
| 2026-04-14 16:30 | Four production surfaces authored | Committed `05b7db3a` |
| 2026-04-14 20:17 | E2E verified, report committed, PR #106 open | `7a1bd077`, PR #106 |
| **2026-04-14 22:45 (this)** | **PR #106 merged, gatherer plan designed and committed** | **Merged `c3c11fa4`, plan at `99472736`** |
| Next | Implement gatherer plan: tag grammar, agents, skill/orchestrator changes | |

## Session Narrative

**Phase 1 — PR #106 review and merge (~20 min).**

Loaded the `2026-04-14_20-17` handoff. User directed continuation with PR #106 review. Launched three review agents in parallel: code-reviewer (project guidelines, writing principles), comment-analyzer (documentation accuracy against codebase), and silent-failure-hunter (hooks.json error handling).

Code-reviewer found 2 important issues: (1) orchestrator at 313 lines exceeds the ~100-line subagent guidance (confidence 85), and (2) normative authority statement inverted — the orchestrator pointed to the reference doc as normative, but per standalone-layers rules the agent body is the operative instruction at runtime (confidence 82). Comment-analyzer found 1 critical issue: verification report Finding 2 incorrectly stated non-terminal blocks should have 12 fields, when the emission contract specifies 13 fields with `epilogue: null` for non-terminal turns. Silent-failure-hunter confirmed hooks.json change is clean — no new silent failure paths.

Fixed the critical issue (Finding 2 reframed as contract-compliant behavior) and the authority statement ("Normative authority" → "Operative authority"). Committed as `79d03d09`, pushed, user merged PR #106 via GitHub UI. Synced local main to `c3c11fa4`, deleted feature branch.

**Phase 2 — Next build item identification (~10 min).**

User asked about the multiple dialogue-related artifacts before proceeding. Provided a grounded explanation of the two parallel stacks (shakedown vs production) sharing the `dialogue-codex` verification core. User confirmed understanding.

Read the supersession ticket (`T-20260330-04`) — 7 acceptance criteria, 2 done (v1), 5 remaining. User provided a detailed analysis correcting my initial three-phase decomposition to four phases, noting: (a) `T-20260330-03` is already closed (dependency resolved), (b) benchmark scored runs are blocked by 8 T4-BR-07 prerequisites, (c) the benchmark candidate definition doesn't require gatherer subagents specifically. User chose Option A (pre-dialogue gatherers) and directed a design discussion.

**Phase 3 — Design discussion (~30 min).**

Presented three invocation model options (pre-dialogue, per-turn dispatch, hybrid). User chose Option A with rationale: "this was one of the highest value components in the cross-model plugin."

Read cross-model semantic sources to ground the discussion: `context-gatherer-code.md` (112 lines), `context-gatherer-falsifier.md` (158 lines), cross-model `/dialogue` SKILL.md (524 lines), `tag-grammar.md` (116 lines). Identified the key design elements: two-agent complementary lenses, structured tagged-line output, deterministic non-LLM assembly, briefing injection at dialogue start.

Proposed positions on 5 design questions: tag grammar reuse, assembly pipeline scope, assumption extraction, briefing injection, seed evidence vs ledger. User agreed at the architectural level and pushed harder on two points: (1) keep briefing quality/provenance validation even without analytics coupling, and (2) give seed evidence a typed home in the production artifact via `citation_tier`. User offered three options for citation tier; I recommended Option A (`citation_tier: "seed" | "dialogue"` on `synthesis_citations[]`); user agreed.

**Phase 4 — Plan writing and review (~60 min).**

Wrote the plan at `docs/plans/2026-04-14-t04-pre-dialogue-gatherers-and-briefing-assembly.md` (initially 667 lines, 12 sections). User conducted 6 rounds of review with 11 total findings:

**Round 1 (3 findings):**
- P1: TOCTOU race between single-run check and active-run write — gatherer window up to 120s before lock exists. Fix: split active-run from seed write, move active-run before gatherers.
- P2: Gatherer contracts need optional `scope_envelope` for future benchmark runs. Fix: added optional `{allowed_roots: string[]}` input.
- P2: "Skip files already covered by gatherer CLAIMs" lets seed suppress Phase 1 validation. Fix: changed to "reprioritize targets" with explicit prohibition on suppression.

**Round 2 (2 findings):**
- P1: Lock outlives both success and failure — no cleanup owner defined. Fix: added §8.3 Lock Lifecycle with try/finally pattern.
- P2: `representative_citation` in `final_claims` can blur seed/dialogue provenance. Fix: constrained to dialogue-tier only, `null` when no dialogue-tier citation exists.

**Round 3 (2 findings):**
- P1: Crash-abandoned lock blocks until 24h stale sweep. Fix: added three-tier liveness check with mtime-based age tiebreaker (`MAX_GATHER_AGE = 300s`).
- P2: `run_id` generation point unspecified. Fix: added §8.2 generating one UUID4 at procedure start, carried through all artifacts.

**Round 4 (2 findings):**
- P1: Active-run JSON format `{run_id, created_at}` breaks existing plain-text readers (`read_active_run_id()` uses `.read_text().strip()`). Fix: reverted to plain-text `run_id`, use file mtime for age check.
- P2: Step 5 searches `active-run-*` (global) but plan describes "session lock." Verified containment code is fully session-scoped (`active_run_path()` takes `session_id`). Fix: removed false global-lock rationale.

**Round 5 (2 findings):**
- P1: Session-scoped recovery means no concurrent-gathering race — mtime check unnecessary. Collapsed three-tier to two-tier (seed/scope present → block, absent → clean up). Removed `MAX_GATHER_AGE`.
- P2: `representative_citation` nullable but §7.3 says "Structure unchanged." Fix: updated to "Schema changed."

**Round 6 (2 findings):**
- P1: Stale references to old three-tier/mtime design in §8.2, §8.4, v1-change note. Fix: cleaned all 4 locations.
- P2: §7.3 `final_claims` still says "unchanged." Fix: updated to "Schema changed: `representative_citation` is now nullable."

After round 6: no findings. User confirmed ready for commit.

## Decisions

### Decision 1: Pre-dialogue gatherers (Option A)

**Choice:** Two gatherer agents (code explorer + falsifier) dispatched by the `/dialogue` skill before the Codex dialogue starts. Cross-model pattern.

**Driver:** User stated: "this was one of the highest value components in the cross-model plugin." The pre-dialogue gathering pattern provides breadth (wide codebase exploration) that complements the orchestrator's inline scouting (depth, targeted reads).

**Alternatives considered:**
- **Option B: Per-turn gatherer dispatch.** Orchestrator dispatches gatherers during each turn's scouting phase. Rejected: requires `Agent` in the orchestrator's tools list, containment changes for subagent scope propagation, and restructures the orchestration contract.
- **Option C: Hybrid.** Pre-dialogue + per-turn dispatch. Rejected: unnecessary complexity for this slice; inline scouting already provides per-turn depth.

**Trade-offs accepted:** The `/dialogue` skill grows significantly (~80-100 lines for steps 5a-5d). Gatherers add ~120s of latency before the dialogue starts.

**Confidence:** High (E2) — cross-model pattern is proven in production; design discussion explored all three options.

**Reversibility:** High — gatherer agents are additive; removing them restores v1 behavior.

**Change trigger:** If gatherer latency is unacceptable, or if evidence shows inline scouting alone achieves equivalent synthesis quality.

### Decision 2: Assembly in the skill, not the orchestrator

**Choice:** The `/dialogue` skill owns gatherer dispatch, assumption extraction, deterministic assembly, health checking, and briefing injection. The orchestrator receives the assembled briefing.

**Driver:** Keeps the orchestrator focused on the dialogue loop. Avoids giving it the `Agent` tool. The skill is the integration surface; the orchestrator is the execution engine.

**Alternatives considered:**
- **Assembly in the orchestrator.** Orchestrator dispatches gatherers in a new Phase 0. Rejected: requires `Agent` tool, containment changes.

**Trade-offs accepted:** The skill takes on more complexity. The orchestrator can't adjust gathering based on dialogue context (it only sees the assembled briefing).

**Confidence:** High (E2) — clear separation of concerns confirmed by user agreement.

**Reversibility:** Medium — moving assembly to the orchestrator would require restructuring both surfaces.

**Change trigger:** If the orchestrator needs to request additional gathering mid-dialogue (adaptive scouting).

### Decision 3: Session-scoped lock with seed/scope liveness recovery

**Choice:** Active-run pointer is session-scoped (checked per `session_id`, not global `active-run-*`). Plain-text `run_id` content (unchanged format). Two-tier liveness check: seed/scope present → block, absent → clean up immediately. Try/finally release in the skill.

**Driver:** The containment architecture is fully session-scoped — `active_run_path()` takes `session_id`, `read_active_run_id()` does exact per-session lookup (`server/containment.py:36-39, 84-92`). Two sessions running concurrently have completely disjoint file sets.

**Alternatives considered:**
- **Global lock.** Search `active-run-*` to prevent any concurrent dialogue. Rejected: containment code is already session-scoped, no namespace conflicts exist.
- **Enriched pointer `{run_id, created_at}`.** Rejected: breaks `read_active_run_id()` which reads `.read_text().strip()` as plain-text `run_id`.
- **Three-tier liveness with mtime.** Rejected: within a single sequential session, the only stale-pointer scenario is a prior crash, and seed/scope absence is sufficient to detect it without timing heuristics.

**Trade-offs accepted:** Crash that leaves both pointer AND seed/scope (rare: crash mid-containment) requires the 24h stale sweep. Accepted because this edge case is uncommon and the sweep handles it.

**Confidence:** High (E2) — verified against `server/containment.py:36-39` and `containment_lifecycle.py:76-82`.

**Reversibility:** High — lock mechanism is entirely in the skill procedure.

**Change trigger:** If the session runtime changes to allow concurrent `/dialogue` invocations within a session.

### Decision 4: `citation_tier: "seed" | "dialogue"` on `synthesis_citations[]`

**Choice:** Add `citation_tier` to each entry in `synthesis_citations[]`. Constrain `final_claims[].representative_citation` to dialogue-tier only (null when no dialogue-tier citation exists). Render null as `—` in the claims table.

**Driver:** User pushed: "give seed evidence a typed home in the production artifact, not just prose." Without typed distinction, seed-only factual propositions in the synthesis have no audit trail for whether they came from Codex-turn verification or pre-dialogue exploration.

**Alternatives considered:**
- **Separate `seed_evidence[]` field.** Rejected: parallel array duplicates the citation shape, consumers look in two places.
- **`seed_context_summary` + `seed_citations[]`.** Rejected: prose summary can drift from actual citations.
- **No `representative_citation` constraint.** Rejected by user: "a seed-sourced citation could become the representative citation for a Codex-claim row, making unverified seed evidence look like the support for a dialogue-tier claim."

**Trade-offs accepted:** `null` representative citation means some claims show `—` in the user-facing table. This is honest (no dialogue-tier evidence) but may look sparse.

**Confidence:** High (E2) — clean schema extension, minimal backward compatibility impact (absence implies `"dialogue"`).

**Reversibility:** Medium — field addition is backward compatible; removing it would require consumer updates.

**Change trigger:** If consumer tooling needs richer provenance than binary tier.

### Decision 5: Tag grammar reused but independently owned

**Choice:** Reuse the cross-model tag grammar format (`CLAIM:`, `COUNTER:`, `CONFIRM:`, `OPEN:` with `@ path:line`, `AID:`, `TYPE:`, `SRC:`). Create a codex-collaboration-owned frozen copy, NOT a live dependency.

**Driver:** User stated: "reuse the grammar and parse semantics, but make it a codex-collaboration-owned reference, not a live dependency on the cross-model file."

**Alternatives considered:**
- **Live dependency on cross-model file.** Rejected: candidate system needs its own frozen contract surface that evolves independently.
- **Redesigned grammar.** Rejected: no deficiency in the existing format warrants redesign cost.

**Trade-offs accepted:** Two copies of the grammar exist (cross-model and codex-collaboration). They may diverge over time.

**Confidence:** High (E2) — grammar is proven in production, reuse is low-risk.

**Reversibility:** High — the grammar is a reference document, not executable code.

**Change trigger:** If codex-collaboration needs tags or metadata fields that don't fit the existing grammar.

## Changes

### `docs/plans/2026-04-14-t04-v1-first-live-dialogue-report.md` (MODIFIED, -5/+5)

**Purpose:** Fix factual error in Finding 2. The original stated non-terminal blocks should have 12 fields; the emission contract specifies 13 fields with `epilogue: null` for non-terminal turns.

**Approach:** Reframed from "structural variation from contract" to "contract-compliant behavior." Removed the incorrect claim.

### `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md` (MODIFIED, -1/+1)

**Purpose:** Fix authority direction. Changed from "Normative authority... authored from that contract" to "Operative authority... this body is the operative instruction at runtime."

**Approach:** The agent body is what Claude executes — it IS the authority. The reference document serves humans, not runtime.

### `docs/plans/2026-04-14-t04-pre-dialogue-gatherers-and-briefing-assembly.md` (NEW, 888 lines)

**Purpose:** Design plan for the second T-04 production slice: pre-dialogue context-gathering agents, deterministic briefing assembly, and production synthesis extension.

**Approach:** 12 sections covering goal/scope, locked decisions, gatherer contracts, assembly pipeline, briefing format, orchestrator integration, artifact schema delta, skill procedure changes, file inventory, verification plan, deferred work, references.

**Key design elements:**
- Two gatherer agents (code explorer + falsifier) adapted from cross-model semantic sources
- 10-step deterministic assembly pipeline (parse → retry → fallback → discard → cap → sanitize → dedup → provenance → group → health check)
- Briefing injection via `<!-- dialogue-orchestrated-briefing -->` sentinel with `<!-- briefing-meta: {...} -->` metadata
- `citation_tier: "seed" | "dialogue"` on `synthesis_citations[]`
- Session-scoped lock with seed/scope two-tier liveness recovery
- Try/finally lock lifecycle in the skill

## Codebase Knowledge

### Containment architecture is fully session-scoped

Every function in `server/containment.py` takes `session_id` as a parameter:
- `active_run_path(data_dir, session_id)` → `shakedown_dir / f"active-run-{session_id}"` (line 36-39)
- `read_active_run_id(data_dir, session_id)` → exact per-session lookup, reads `.read_text().strip()` (lines 84-92)
- `read_active_run_id_strict(data_dir, session_id)` → strict variant with ValueError on empty (lines 95-104)

All run artifacts (seed, scope, transcript) are keyed by `run_id` which is unique per invocation. Two sessions running dialogues concurrently have completely disjoint file sets. The containment lifecycle script (`containment_lifecycle.py`) reads `run_id` from the session-scoped active-run pointer (line 76), then locates the seed/scope by `run_id`.

**Implication:** The single-run check in the `/dialogue` skill should be session-scoped, not global. A global `active-run-*` wildcard search would impose unnecessary serialization.

### Cross-model gatherer architecture

Two complementary lenses running in parallel on Sonnet:

| Agent | Domain | Tags | Focus |
|---|---|---|---|
| `context-gatherer-code` | Code, tests, config | `CLAIM`, `OPEN` | What EXISTS in the codebase |
| `context-gatherer-falsifier` | Docs, decisions, plans, AND code | `COUNTER`, `CONFIRM`, `OPEN` | Whether ASSUMPTIONS hold |

Output is prefix-tagged lines (`TAG: <content> [@ path:line] [AID:id] [TYPE:type] [SRC:source]`). Assembler is deterministic (no LLM). Cross-model's `/dialogue` skill has a 7-step pipeline: arguments → assumptions → parallel gatherers → deterministic assembly → health check → delegate → present.

The briefing is injected at dialogue start via `<!-- dialogue-orchestrated-briefing -->` sentinel. The dialogue agent detects the sentinel and skips its own briefing assembly.

### Active-run file format constraint

The active-run file must be plain-text `run_id` (just a UUID string). Cannot be JSON. `read_active_run_id()` at `server/containment.py:84-92` reads with `.read_text(encoding="utf-8").strip()` and returns the value directly. Any format change would break `containment_lifecycle.py` which calls this function in both `_handle_subagent_start` (line 76) and `_handle_subagent_stop` (line 125).

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md` | PR review target, integration point | Authority statement was inverted; 313 lines exceeds ~100-line subagent guidance |
| `packages/plugins/codex-collaboration/skills/dialogue/SKILL.md` | PR review target, integration point | 150-line lightweight procedure — will grow ~80-100 lines with gatherer steps |
| `packages/plugins/codex-collaboration/references/dialogue-turn-contract.md` | PR review target | 402-line extracted contract, correctly cross-referenced |
| `packages/plugins/codex-collaboration/hooks/hooks.json` | PR review target | Clean matcher expansion, fail-open policy documented |
| `docs/plans/2026-04-14-t04-v1-first-live-dialogue-report.md` | PR review target, Finding 2 fix | Finding 2 was factually incorrect about 12-field expectation |
| `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Supersession ticket | 7 acceptance criteria; 2 done, 5 remaining; builds gatherer agents and benchmark |
| `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` (lines 40-53, 150-180) | Benchmark candidate definition | Candidate = Claude-side Glob/Grep/Read; doesn't mandate gatherer subagents specifically |
| `docs/plans/t04-t4-scouting-position-and-evidence-provenance/benchmark-readiness.md` (lines 180-234) | T4-BR-07 prerequisites | 8-item prerequisite gate blocks scored runs |
| `packages/plugins/cross-model/agents/context-gatherer-code.md` | Semantic source for gatherer design | 112 lines; CLAIM + OPEN tags, code/test/config domain, 40-line cap |
| `packages/plugins/cross-model/agents/context-gatherer-falsifier.md` | Semantic source for gatherer design | 158 lines; COUNTER/CONFIRM/OPEN tags, repo-first exploration, 3 COUNTER cap |
| `packages/plugins/cross-model/skills/dialogue/SKILL.md` | Semantic source for assembly pipeline | 524 lines; 7-step pipeline, assumption extraction, analytics coupling |
| `packages/plugins/cross-model/skills/dialogue/references/tag-grammar.md` | Semantic source for tag grammar | 116 lines; line format, parse rules, assembly processing order |
| `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md` (lines 1-115) | Plan format precedent | Frontmatter, section structure, is/is-not pattern |
| `packages/plugins/codex-collaboration/agents/shakedown-dialogue.md` | Architecture comparison | 17 lines — thin shell delegating to `dialogue-codex` skill |
| `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md` (lines 1-30) | Architecture comparison | Shared behavioral core for per-turn verification loop |
| `packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md` (lines 1-30) | Architecture comparison | Shakedown harness — preflight, seed, spawn, capture |
| `server/containment.py` (lines 36-39, 84-104) | Lock design verification | Confirmed session-scoped architecture |
| `scripts/containment_lifecycle.py` (lines 76-82, 125) | Lock design verification | Confirmed `read_active_run_id()` usage pattern |

## Context

### Mental model for this session

This session bridges **closure of v1** and **design of v2**. The first half (PR review, merge) proved the v1 surfaces work end-to-end. The second half (design discussion, plan) designed the next capability layer. The plan itself went through an unusually rigorous review cycle (6 rounds, 11 findings) because the lock lifecycle design space was larger than initially apparent — each fix exposed new constraints in the containment architecture.

The key insight was the **session-scoped containment architecture.** The initial plan incorrectly assumed a global namespace conflict that the code already prevents. Once verified against `server/containment.py`, the lock design simplified dramatically: from a three-tier mtime-based global check to a two-tier seed/scope check within the current session.

### Review convergence pattern

The 6-round review showed a convergence pattern:
- Rounds 1-2: Architectural gaps (TOCTOU, provenance blur, suppression risk)
- Rounds 3-4: Lock lifecycle mechanics (crash recovery, format compatibility, scope)
- Rounds 5-6: Internal consistency (stale references, schema accuracy)

Each round's fixes were smaller and more precise. The final lock model (session-scoped, two-tier, try/finally) is simpler than intermediate designs (global, three-tier, mtime-based).

### Git state

```
origin/main ─── c3c11fa4 (PR #106 merge) ─── 79d03d09 (review fixes)
                ↑ both local and remote main
                                              └── 99472736 (gatherer plan)
                                                  ↑ HEAD (feature/t04-pre-dialogue-gatherers)
```

- `origin/main` and local `main` are in sync at `c3c11fa4`.
- `feature/t04-pre-dialogue-gatherers` is 1 commit ahead of `main`.
- Feature branch has NOT been pushed to origin.

## Learnings

### Session-scoped containment simplifies lock design

**Mechanism.** The containment architecture keys everything by `session_id` at the path level. `active_run_path()` returns `shakedown_dir / f"active-run-{session_id}"`. Within a single Claude Code session, the skill runs sequentially — you cannot invoke `/dialogue` while a previous invocation is running. The only stale-pointer scenario within a session is a prior crash.

**Evidence.** `server/containment.py:36-39` uses `f"active-run-{session_id}"`. `read_active_run_id()` at lines 84-92 does exact per-session lookup. `containment_lifecycle.py:76` passes the current session's `session_id` to locate the active-run.

**Implication.** The liveness check for abandoned pointers only needs to check whether seed/scope files exist for the pointer's `run_id`. If neither exists, the prior invocation either never reached seed-writing (crash during gathering) or completed its lifecycle (SubagentStop cleaned scope). No timing heuristics needed.

**Watch for.** If Claude Code ever allows concurrent skill invocations within a session, the sequential assumption breaks and the lock model needs another pass.

### Active-run file format is a shared contract

**Mechanism.** The active-run file is read by `server/containment.py`, `containment_lifecycle.py`, and the `/dialogue` skill. All three assume plain-text `run_id` content. Changing the format to JSON would break readers that use `.read_text().strip()`.

**Evidence.** `read_active_run_id()` at `server/containment.py:84-92`: `path.read_text(encoding="utf-8").strip()`. `containment_lifecycle.py:76`: `run_id = read_active_run_id(data_dir, session_id)`.

**Implication.** Any enhancement to the active-run file (e.g., embedded timestamp) must either use a separate metadata file or modify all readers. File mtime is the zero-cost alternative for age information.

**Watch for.** If `read_active_run_id()` or `read_active_run_id_strict()` are refactored, verify the file is still treated as plain text.

### Review rounds converge when each fix is smaller than the last

**Mechanism.** Round 1 found architectural gaps (TOCTOU, provenance). Fixing those introduced lock lifecycle complexity (round 2-3). Fixing that introduced format compatibility issues (round 4). Realizing session-scoped containment simplified everything (round 5). Final round was pure cleanup.

**Evidence.** Finding severity: P1, P1, P2, P2, P2 → P1, P2 → P1, P2 → P1, P2 → P1, P2 → clean. Each round's findings were more narrow and the fixes more surgical.

**Implication.** For design documents, expect 3-6 review rounds. Convergence is real — the plan gets simpler as incorrect assumptions are stripped. If fixes keep growing in scope, the design may have a structural problem.

## Next Steps

### 1. Implement the gatherer plan

**Dependencies:** Plan committed and reviewed at `99472736`.

**What to do:**
Build order from the plan's §9 file inventory:
1. Tag grammar reference (`packages/plugins/codex-collaboration/references/tag-grammar.md`) — frozen copy of cross-model tag grammar
2. Code explorer agent (`packages/plugins/codex-collaboration/agents/context-gatherer-code.md`) — adapted from cross-model semantic source
3. Falsifier agent (`packages/plugins/codex-collaboration/agents/context-gatherer-falsifier.md`) — adapted from cross-model semantic source
4. `/dialogue` skill updates — steps 5a-5d, modified dispatch, try/finally lock lifecycle
5. Orchestrator updates — briefing detection, `citation_tier` emission, nullable `representative_citation`

Steps 1-3 are independent and can be done in parallel. Steps 4-5 depend on agents existing.

**What to read first:**
- The plan: `docs/plans/2026-04-14-t04-pre-dialogue-gatherers-and-briefing-assembly.md`
- Cross-model semantic sources (listed in plan frontmatter `semantic_source`)

**Potential obstacles:** The `/dialogue` skill grows substantially (~80-100 lines). The try/finally lock lifecycle is the most complex procedural change.

### 2. Push and optionally PR the plan

**Dependencies:** None — plan is committed locally.

**What to do:** Push `feature/t04-pre-dialogue-gatherers` to origin. Decide whether to PR the plan separately or include it with implementation.

## In Progress

**Clean stopping point — plan reviewed and committed, implementation not started. No work in flight.**

- **Approach:** Design-first workflow: design discussion → locked decisions → written plan → iterative review → commit → then implement.
- **State:** Complete. Plan at `99472736`, all review findings resolved.
- **Working:** Plan passes 6 rounds of review with zero remaining findings.
- **Not working:** Nothing broken.
- **Open question:** None blocking.
- **Next action:** Start implementation from the plan's build order (§9 file inventory).

## Open Questions

### 1. Should the plan be PRed separately or with implementation?

**Context:** The plan is on `feature/t04-pre-dialogue-gatherers` which will also hold the implementation. User could PR the plan alone (like v1's plan PR), or include it with the implementation artifacts.

**Impact:** Low — this is a publication boundary question, not a technical one.

**Options:**
- PR the plan alone for separate review, then implementation PR.
- Bundle plan + implementation in one PR (more coherent as a packet).

**Decision pending until:** Next session start — user may have a preference.

## Risks

### 1. Plan is 888 lines — may be hard to reference from implementation

**Impact:** The PostToolUse hook flagged the file as >500 lines. Future sessions implementing from the plan will need to read specific sections rather than the whole document.

**Mitigation:** The plan has clear section numbering (§1-§12) and the build sequence is in §9. Implementation can target specific sections.

### 2. Lock lifecycle is the most complex procedural change

**Impact:** The try/finally pattern in the skill, combined with the two-tier liveness check, is the most intricate part of the implementation. Getting the release path wrong could strand the session.

**Mitigation:** The plan specifies the pattern precisely (§8.4) with explicit success/failure/crash paths. Unit-level verification includes a liveness check test (§10.1).

## References

### Commits this session

- `79d03d09` on `feature/t04-v1-implementation` — fix(codex-collaboration): correct report finding and authority framing (pushed, merged via PR #106)
- `99472736` on `feature/t04-pre-dialogue-gatherers` — docs(plan): add T-04 pre-dialogue gatherers and briefing assembly plan

### PR

- PR #106: merged at `c3c11fa4` — feat(codex-collaboration): T-04 v1 production dialogue surfaces

### Authority documents

| Document | Location | Role |
|---|---|---|
| Supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Acceptance authority |
| Benchmark contract | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Evaluation authority |
| v1 scoping plan | `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md` | Prior slice design |
| Gatherer plan | `docs/plans/2026-04-14-t04-pre-dialogue-gatherers-and-briefing-assembly.md` | This slice design |

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-14_20-17_t04-v1-e2e-verified-pr-106-open.md`
- Prior: `docs/handoffs/archive/2026-04-14_16-30_t04-v1-four-production-surfaces-authored-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_12-55_t04-v1-section-10-authoring-decisions-resolved-and-committed.md`

## Gotchas

### Active-run file is a shared plain-text contract

**Symptom:** Changing the active-run file format (e.g., to JSON with `{run_id, created_at}`) silently breaks `containment_lifecycle.py` and `containment_guard.py` which read it as plain-text `run_id`.

**Root cause:** `read_active_run_id()` at `server/containment.py:84-92` uses `.read_text().strip()`. Any content beyond a bare UUID string would be passed as the `run_id` to all downstream consumers.

**Prevention:** Keep active-run content as plain-text `run_id`. Use file mtime for age information. If richer metadata is needed, write a separate file.

### Containment architecture is session-scoped, not global

**Symptom:** Designing a global lock (`active-run-*` wildcard check) when the containment code only does per-session lookups.

**Root cause:** `active_run_path()` takes `session_id` and returns an exact path. There is no function that searches for all active-run files.

**Prevention:** Always check `server/containment.py` before making assumptions about lock scope. The containment namespace is per-session by design.

### `representative_citation` is now nullable

**Symptom:** `/dialogue` rendering code assumes `representative_citation` is always present and tries to format it.

**Root cause:** The v1 schema had `representative_citation` as required. The gatherer plan makes it nullable for claims where no dialogue-tier citation exists.

**Prevention:** Check for `null` before rendering. Display `—` in the claims table.

## Conversation Highlights

### User's four-phase correction

User corrected my initial three-phase decomposition to four phases, providing a detailed analysis with file references: "The benchmark contract itself does not require gatherer subagents specifically. It defines the candidate as codex-collaboration dialogue using Claude-side `Glob`/`Grep`/`Read`, and only forbids plugin-side scouting."

### User's two pushes on the design

User agreed with all 5 architectural positions but pushed harder on two points: (1) "keep a small notion of briefing quality/provenance validation even if you drop analytics coupling" and (2) "give seed evidence a typed home in the production artifact, not just prose." Both pushes strengthened the design.

### User's review discipline

Six rounds of review, each finding narrower and more precise than the last. User explicitly called out when findings were fixed vs. when residual issues remained: "The earlier three findings are fixed... I would not commit yet because the lock lifecycle is a real blocker."

### User's final verdict

User's closing assessment: "The two issues from the prior round are fixed cleanly... Residual risk is low and mostly implementation-side rather than plan-side... This is ready for commit."

## User Preferences

### Publication boundary awareness (continued)

User again demonstrated precise git state tracking. Chose PR over direct merge for v1 (prior session), and this session tracked `origin/main...HEAD` divergence when deciding to merge PR #106 via GitHub UI.

### Design-before-implementation discipline

User directed a design discussion before any code, then a full plan document, then 6 rounds of review — all before any implementation. Verbatim: "I'd name it something like `2026-04-14-t04-pre-dialogue-gatherers-and-briefing-assembly.md`." User treated the plan as a first-class deliverable with the same review rigor as code.

### Review rigor on plans

User reviewed the plan 6 times, each round surfacing 2-3 findings. Not a rubber stamp — findings included genuine architectural issues (TOCTOU, format compatibility, scope semantics). User's approach: "I would not commit yet" until all findings are resolved.

### Explicit commit gates

User stated "This is ready for commit" only after the final review round returned zero findings. Did not conflate "close enough" with "done."
