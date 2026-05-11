---
date: 2026-04-15
time: "22:38"
created_at: "2026-04-16T02:38:57Z"
session_id: 4708fa92-8376-4d62-95c8-e37af856911a
resumed_from: docs/handoffs/archive/2026-04-15_21-45_t04-benchmark-v1-phase1-complete-ready-for-execution.md
project: claude-code-tool-dev
branch: main
commit: 58bcd73b
title: "T-04 execution mode gate cleared — invocations prepared for Phase 2"
type: handoff
files:
  - docs/benchmarks/dialogue-supersession/v1/operator-procedure.md
  - /tmp/benchmark-v1-staging-20260415/invocations.md
---

# T-04 Execution Mode Gate Cleared — Invocations Prepared for Phase 2

## Goal

Clear the execution mode gate and prepare all pre-built invocations for the 8-session Phase 2 benchmark execution.

**Trigger.** Resumed from `2026-04-15_21-45` handoff. Phase 1 (Pre-Run Setup) was complete. The immediate next step was the execution mode gate — verifying that `/codex-collaboration:dialogue` accepts `-p` and `-n` flags at the runtime level — followed by preparing the invocation strings for all 8 benchmark runs.

**Stakes.** The execution mode gate determines whether the benchmark runs in SCORED or REHEARSAL mode. SCORED is required for AC-5 ("The benchmark contract is executed on the fixed corpus"). Rehearsal runs are non-evidentiary and cannot be used for pass/fail comparisons, aggregate scoring, or retirement decisions.

**Success criteria achieved this session:**

1. Execution mode gate cleared: SCORED mode confirmed via 4-layer code-level verification.
2. Session ID mechanism resolved (Open Question #1 from prior handoff).
3. Stale `~/.claude/session_id` path in operator procedure fixed and committed.
4. All 8 invocation strings pre-built with proper `{run_type}` parameterization.
5. Invocations packet reviewed (3 findings raised and resolved).

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
| 2026-04-15 19:30 | Benchmark v1 scaffold reviewed and committed | Scaffold `adcf49ea` on `feature/benchmark-v1-scaffold` |
| 2026-04-15 21:11 | RC4 resolved — posture and turn-budget wired through | `52a968e9`–`afa55eac` on `main` |
| 2026-04-15 21:45 | Phase 1 complete — ready for scored execution | `425f7784`, `fb2e931b` on `main` |
| **2026-04-15 22:38 (this)** | **Execution mode gate cleared, invocations prepared** | **`58bcd73b` on `main`, invocations at staging** |
| Next | Live runtime gate + Phase 2 per-row execution | |

## Session Narrative

**Phase 1 — Handoff load and gate preparation (~5 min).**

Loaded the `2026-04-15_21-45` handoff. The prior session had completed Phase 1 (Pre-Run Setup) with two commits on main (`425f7784`, `fb2e931b`) and identified the execution mode gate as the next step. Read `operator-procedure.md:146-166` — the gate section requires two checks: can the candidate accept posture input (`-p`) and turn-budget input (`-n`)?

**Phase 2 — Execution mode gate verification (~10 min).**

Performed a 4-layer code-level trace of the RC4 wiring to verify `-p` and `-n` acceptance end-to-end:

1. **Skill layer** (`SKILL.md:3,17-22`) — frontmatter advertises `-p`/`-n`, flag table defines enum validation with 5 valid posture values and turns range 1-15.
2. **Orchestrator dispatch** (`SKILL.md:242-254`) — skill passes `resolved_posture` and `resolved_turn_budget` in the Agent prompt metadata block.
3. **MCP server** (`mcp_server.py:55-70`) — schema defines `posture` and `turn_budget` as explicit tool input parameters with descriptions noting they override profile defaults.
4. **Profile resolver** (`profiles.py:81-114`) — `explicit_posture` and `explicit_turn_budget` parameters are applied as overrides when non-None, with precedence over profile-level defaults.

Also traced the orchestrator → dialogue.py path (`dialogue.py:117-148`) confirming `explicit_posture`/`explicit_turn_budget` propagate to the resolve step only when present. The gate result: both checks pass. Execution mode: **SCORED**.

User confirmed this session counts as the fresh session for the gate. The concern about needing a separate fresh session was unnecessary — this session had no prior conversation context that could contaminate the gate verification.

**Phase 3 — Session ID mechanism resolution (~10 min).**

Resolved Open Question #1 from the prior handoff: "What is the canonical way to obtain a Claude Code session ID?"

The operator procedure at line 186 referenced `~/.claude/session_id` — a path that does not exist. Investigated the actual mechanism:

- `publish_session_id.py` is a SessionStart hook registered in `hooks.json:3-9`.
- It reads `session_id` from the Claude Code hook payload (`payload.get("session_id")` at line 33).
- Writes atomically to `${CLAUDE_PLUGIN_DATA}/session_id` using fsync + atomic rename (lines 39-43).
- The actual file path at runtime: `~/.claude/plugins/data/codex-collaboration-inline/session_id`.
- Verified by reading the file: contained `4708fa92-8376-4d62-95c8-e37af856911a`, matching this session's ID.

This confirmed: canonical session IDs are reliably available for scored runs. The `~/.claude/session_id` path in the operator procedure was speculative (written during scaffold authoring before verifying the mechanism).

**Phase 4 — Operator procedure fix (~5 min).**

Created branch `chore/fix-session-id-path`, replaced the speculative path at `operator-procedure.md:184-187` with the verified plugin-specific path. Also removed the vague "status bar" reference — the concrete file path is the authoritative source. Committed at `58bcd73b`, merged to main.

**Phase 5 — Invocation packet construction (~10 min).**

Built all 8 invocation strings from the manifest corpus and operator procedure templates:

- B1, B3, B5 used the file-level anchor template (`operator-procedure.md:208-226`).
- B8 used the directory-level anchored decomposition template (`operator-procedure.md:228-254`) with 3 groups.
- Each row produced baseline (max_evidence=5) and candidate (max_evidence=15) variants.
- All invocations included the full scope constraint, evidence budget, posture, and corpus prompt.

Initial version hardcoded "This is a scored benchmark run." and `"rehearsal": false` throughout.

**Phase 6 — Invocation packet review and fixes (~15 min).**

User provided 3 code review findings against the invocations file:

**P1 (priority 1):** Hardcoded scored mode. The packet globally declared `Execution mode: SCORED`, hardcoded the scored run-type string, and assumed scored metadata before the live runtime gate had been cleared. Fix: parameterized all invocations with `{run_type}` placeholder, added substitution table, documented per-run reclassification rules.

**P2 (priority 2):** Missing invalidation fields. The metadata template only had happy-path fields and hardcoded `"rehearsal": false`. Fix: added `valid: true` field to the base template, created separate invalidation template with `valid: false`, `invalid_reason`, and `superseded_by`, added "do not delete invalid files" rule.

**P3 (priority 3, found after P1/P2 fixes):** Rehearsal fallback lacked manual session label. The checklist could force `session_id_canonical: false` but never told the operator what to put in `session_id` for that run. Fix: added explicit instruction to assign a manual label (e.g., `B1-baseline-rehearsal`) in both the checklist and the decision table.

User confirmed: "Before Phase 2" means a separate pre-run gate check, not using the first benchmark run as the gate. The gate and the runs are distinct sessions.

## Decisions

### Decision 1: Code-level evidence sufficient for execution mode gate

**Choice:** Accept the 4-layer code trace as sufficient to clear the execution mode gate for SCORED mode, without a separate runtime test invocation.

**Driver:** The evidence is E2-level (direct observation of implementation across all 4 layers: skill → orchestrator → MCP schema → profile resolver). Each layer independently handles `-p` and `-n` — no layer silently drops them. The code was written and committed during the RC4 session, verified by both the author and the prior session's review.

**Alternatives considered:**
- **Separate fresh session with test invocation** — invoke `/codex-collaboration:dialogue "test" -p evaluative -n 2` to confirm runtime acceptance. Rejected because the code-level evidence is unambiguous and a test invocation would consume a full dialogue (including Codex API calls) just to confirm flag parsing.

**Trade-offs accepted:** A code-level trace doesn't exercise the full runtime stack (Claude Code plugin loading, MCP server startup, Codex API connectivity). These could theoretically fail in ways the code doesn't predict. Accepted because: (a) the invocation packet's `{run_type}` parameterization means the first actual candidate run will naturally serve as a live runtime gate — if it fails, all remaining runs switch to REHEARSAL; (b) plugin loading was already verified via `/reload-plugins` in the prior session.

**Confidence:** High (E2) — direct observation of implementation at all four layers, with file:line citations.

**Reversibility:** High — if the first candidate run reveals a runtime issue, reclassify all runs to REHEARSAL per the invocation packet's built-in fallback.

**Change trigger:** If the first candidate session fails to parse `-p` or `-n` at runtime.

### Decision 2: Session ID obtained via plugin hook, not `~/.claude/session_id`

**Choice:** Use `~/.claude/plugins/data/codex-collaboration-inline/session_id` as the canonical session ID source for benchmark runs.

**Driver:** `~/.claude/session_id` does not exist. The actual mechanism is `publish_session_id.py`, a SessionStart hook in the codex-collaboration plugin, which reads the session ID from the Claude Code hook payload and writes it to the plugin data directory.

**Alternatives considered:**
- **Claude Code status bar** — the operator procedure mentioned this as an alternative source. Rejected because it requires manual visual inspection and copy-paste, which is error-prone and not automatable.
- **Keep the `~/.claude/session_id` reference as aspirational** — maybe Claude Code will add it later. Rejected because the operator procedure is an execution document, not a wishlist. It must reference paths that exist today.

**Trade-offs accepted:** The path is plugin-specific (`codex-collaboration-inline`). If the plugin is renamed or the data directory layout changes, the path breaks. Accepted because: (a) the plugin name is stable within the benchmark scope; (b) the path is now documented in the operator procedure, making it discoverable.

**Confidence:** High (E2) — verified by reading the file and confirming it contained this session's UUID.

**Reversibility:** High — if a better mechanism emerges, update the one line in the operator procedure.

**Change trigger:** If Claude Code adds a native `~/.claude/session_id` file, or if the plugin is renamed.

### Decision 3: Parameterized run type in invocations

**Choice:** Use `{run_type}` placeholder in all 8 invocations with a substitution table, rather than hardcoding "This is a scored benchmark run."

**Driver:** User's P1 review finding: "This packet globally declares `Execution mode: SCORED`, hardcodes the scored run-type string into every invocation, and assumes scored metadata before the live execution-mode gate has actually been cleared." The procedure has three decision points where mode can shift: the execution mode gate (`operator-procedure.md:146`), per-run session ID check (`operator-procedure.md:327`), and evidence-budget overflow (`operator-procedure.md:336`).

**Alternatives considered:**
- **Provide separate scored and rehearsal copies of each invocation** — 16 invocation blocks instead of 8. Rejected because it doubles the file size and introduces a maintenance burden (changes must be made in two places).
- **Keep hardcoded scored mode** — simpler but creates risk of executing or recording a rehearsal under scored labels. Rejected per the review finding.

**Trade-offs accepted:** Operators must perform a manual substitution before each run. Minor friction vs. the risk of mode contamination.

**Confidence:** High (E2) — the review finding cited specific operator-procedure lines where mode can shift.

**Reversibility:** High — trivially revert by replacing `{run_type}` with the scored string.

**Change trigger:** None expected — parameterization is strictly better than hardcoding.

## Changes

### `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` (+4/-2)

**Purpose:** Fix speculative `~/.claude/session_id` path with verified plugin-specific path.

**Approach:** Replaced lines 184-186. Old text referenced "visible in the Claude Code status bar, or via `! cat ~/.claude/session_id`". New text identifies the source (codex-collaboration SessionStart hook) and provides the exact file path with a `cat` command.

**Key detail:** The old path never existed — it was written during the scaffold session before the actual mechanism was investigated. The fix is a factual correction, not a design change.

### `/tmp/benchmark-v1-staging-20260415/invocations.md` (new file, ~280 lines)

**Purpose:** Pre-built invocations for all 8 benchmark runs, reviewed and corrected through 3 rounds.

**Approach:** Built from manifest corpus (`manifest.json:64-125`) and operator procedure templates (`operator-procedure.md:208-254`). Each invocation is a complete paste-and-go string with `{run_type}` substitution.

**Key sections:**
- Execution mode header with gate status and substitution table
- Per-session checklist (6 steps including session ID recording and rehearsal fallback)
- 8 invocations: B1/B3/B5 (file-level anchor) and B8 (directory-level decomposition with 3 groups)
- Run order table (B1-baseline → B8-candidate)
- Artifact naming convention
- Metadata template with `valid` field for happy path
- Invalidation template with `valid: false`, `invalid_reason`, `superseded_by`
- Rehearsal reclassification decision table with manual label fallback

## Codebase Knowledge

### RC4 wiring — full 4-layer trace

The `-p`/`-n` flag support traces through four independent layers, each with its own parsing/validation:

| Layer | File | Mechanism | Key lines |
|---|---|---|---|
| Skill | `packages/plugins/codex-collaboration/skills/dialogue/SKILL.md` | Flag table with enum validation | 17-22 (table), 38-40 (parse + default resolution) |
| Orchestrator dispatch | Same SKILL.md | Metadata block in Agent prompt | 242-254 (`Posture: <resolved_posture>`, `Turn budget: <resolved_turn_budget>`) |
| MCP server | `packages/plugins/codex-collaboration/server/mcp_server.py` | Tool input schema fields | 55-70 (schema), 259-260 (pass to dialogue manager) |
| Profile resolver | `packages/plugins/codex-collaboration/server/profiles.py` | Explicit override parameters | 81-82 (function sig), 108-114 (override application) |
| Dialogue manager | `packages/plugins/codex-collaboration/server/dialogue.py` | Passthrough to resolver | 117-118 (function sig), 140-148 (conditional resolve) |

Each layer independently parses and validates — no layer silently drops the values. The skill resolves defaults even when no flags are provided (line 40: "The skill always resolves explicit values for both posture and turn budget — no implicit defaults propagate downstream").

### Session ID publication mechanism

| Component | File | Role |
|---|---|---|
| Hook script | `packages/plugins/codex-collaboration/scripts/publish_session_id.py` | Reads `session_id` from SessionStart payload, atomic-writes to plugin data dir |
| Hook registration | `packages/plugins/codex-collaboration/hooks/hooks.json:3-9` | Registers script as SessionStart hook |
| Runtime path | `~/.claude/plugins/data/codex-collaboration-inline/session_id` | Where the file actually lives |
| Consumers | `SKILL.md:54` (dialogue skill), `SKILL.md:31` (shakedown skill) | Both read at step 3 of their procedures |

The publish script uses atomic write semantics: write to `.tmp`, fsync, then `os.replace()` (lines 39-43). This prevents partial reads if Claude Code's session ID changes mid-write (shouldn't happen, but defensive).

The `CLAUDE_PLUGIN_DATA` environment variable is set by the Claude Code plugin system at runtime — it's not available from the Bash tool because the Bash tool runs in its own subprocess without the plugin environment. The file must be accessed via its resolved path.

### Operator procedure structure (now 720 lines)

Same structure as prior handoff's table, with one change:

| Section | Lines | Change |
|---|---|---|
| Session isolation | 174-197 | Session ID path updated from `~/.claude/session_id` to `~/.claude/plugins/data/codex-collaboration-inline/session_id` at line 186 |

All other sections unchanged. Full structure table in the prior handoff (`2026-04-15_21-45`).

### Invocation templates — verified against manifest

All 8 invocations verified against `manifest.json:64-125`:

| Row | Prompt source | Allowed roots source | Posture | Budget | Template |
|---|---|---|---|---|---|
| B1 | `manifest.json:69` | `manifest.json:70-74` | evaluative | 6 | File-level |
| B3 | `manifest.json:80` | `manifest.json:81-85` | adversarial | 6 | File-level |
| B5 | `manifest.json:91` | `manifest.json:92-96` | evaluative | 6 | File-level |
| B8 | `manifest.json:102` | `manifest.json:103-123` (groups) | comparative | 8 | Directory-level decomposition |

Evidence budgets: baseline=5 (`manifest.json:19`), candidate=15 (`manifest.json:20`).

## Context

### T-04 acceptance criteria status after this session

| AC | Description | Status | Evidence |
|---|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) | `skills/dialogue/SKILL.md` |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) | `agents/dialogue-orchestrator.md` |
| 3 | Gatherer agents exist and use Claude-side tools | Done (PR #107) | Both agents with Glob/Grep/Read |
| 4 | Synthesis with bounded citations and convergence | Done | Dialogue-tier citations + `converged: false` terminal artifact |
| 5 | Benchmark contract executed on fixed corpus | **Gate cleared (SCORED); execution next** | 4-layer trace, invocations prepared |
| 6 | Benchmark result recorded with per-task metrics | **Open** | Depends on AC-5 |
| 7 | Context-injection retirement decision explicit | **Open** | Depends on AC-6 |

### Mental model for this session

This session was a **pre-flight verification and preparation** session — not executing the benchmark, but ensuring every input to the execution phase is correct and reviewed. The execution mode gate was the primary verification target; the invocations packet was the primary preparation deliverable.

The review cycle on the invocations packet was valuable: it caught three procedural integrity issues (hardcoded mode, missing invalidation fields, missing rehearsal label) that would have created audit problems during or after execution. The cost of fixing them now (15 min) vs. discovering them during adjudication (potential rerun of affected runs) justified the review investment.

### Open tickets

| Ticket | ID | Status | Next |
|---|---|---|---|
| Dialogue parity & scouting retirement | T-04 | Open (AC 1-4 done, gate cleared, invocations prepared) | Phase 2 per-row execution |
| Execution-domain foundation | T-05 | Open (unstarted) | Separate workstream |
| Promotion flow & delegate UX | T-06 | Open (blocked by T-05) | — |
| Analytics reviewer & cutover | T-07 | Open | Separate workstream |

## Learnings

### `~/.claude/session_id` does not exist — session IDs come from plugin hooks

**Mechanism.** Claude Code does not write a `~/.claude/session_id` file. Session IDs are delivered to plugins via the SessionStart hook payload (`payload.get("session_id")`). The codex-collaboration plugin's `publish_session_id.py` hook writes this value to `${CLAUDE_PLUGIN_DATA}/session_id`, which resolves to `~/.claude/plugins/data/codex-collaboration-inline/session_id`.

**Evidence.** `cat ~/.claude/session_id` returned "FILE_NOT_FOUND". `cat ~/.claude/plugins/data/codex-collaboration-inline/session_id` returned `4708fa92-8376-4d62-95c8-e37af856911a` (this session's UUID, matching the skill-injected session ID).

**Implication.** Any future operator procedure or documentation referencing session IDs must use the plugin-specific path. If a different plugin needs session IDs, it must implement its own SessionStart hook — there's no platform-level file to read.

### `CLAUDE_PLUGIN_DATA` is not available in Bash tool subprocesses

**Mechanism.** The Bash tool runs commands in independent subprocesses that don't inherit the Claude Code plugin environment. `CLAUDE_PLUGIN_DATA` is set by the plugin system for plugin hooks and MCP servers, not for arbitrary shell commands.

**Evidence.** `echo "CLAUDE_PLUGIN_DATA=${CLAUDE_PLUGIN_DATA:-NOT_SET}"` returned `NOT_SET`.

**Implication.** When accessing plugin data files from the Bash tool, use the resolved absolute path (`~/.claude/plugins/data/<plugin-name>/`) rather than the environment variable. The environment variable works inside hooks and MCP server processes, not in ad-hoc shell commands.

### Invocation packets must parameterize mode decisions, not pre-commit to outcomes

**Mechanism.** An operator convenience document that hardcodes a mode decision (SCORED/REHEARSAL) before the gate is satisfied creates a false-confidence path: the operator follows the document assuming the mode is locked, when in fact three separate decision points in the procedure can override it.

**Evidence.** P1 review finding identified the three override points: execution mode gate (`operator-procedure.md:146`), per-run session ID check (`operator-procedure.md:327`), and evidence-budget overflow (`operator-procedure.md:336`). Original invocations had `"This is a scored benchmark run."` hardcoded in all 8 invocation strings and `"rehearsal": false` hardcoded in the metadata template.

**Implication.** For procedural documents that serve as operator checklists, defer mode commitment to the latest responsible moment. Use placeholders for values that depend on runtime conditions, even when you're highly confident about the outcome.

### Metadata templates must include invalidation fields from day one

**Mechanism.** If the initial metadata template only captures happy-path fields, invalid runs create orphaned state — the operator has to reconstruct invalidation metadata by hand, which defeats the audit trail purpose.

**Evidence.** P2 review finding: the operator procedure requires `valid`, `invalid_reason`, and `superseded_by` for invalidated runs (`operator-procedure.md:336-338`, `operator-procedure.md:664-665`). The original template had none of these fields.

**Implication.** When creating data capture templates from a procedure, scan the entire procedure for all fields that could apply to any state of the captured entity, not just the expected-case state. Invalidation, error, and degraded-mode fields are easily missed because the template author is thinking about the happy path.

## Next Steps

### 1. Clear the live runtime gate in a fresh candidate session

**Dependencies:** None — code-level gate already passed.

**What to do:**
1. Open a new terminal
2. Start a fresh `claude` session
3. Invoke `/codex-collaboration:dialogue "test" -p evaluative -n 2` (or equivalent minimal invocation)
4. If the skill parses `-p` and `-n` without error → SCORED confirmed at runtime level
5. If it fails → all runs switch to REHEARSAL; substitute `{run_type}` accordingly

**What to read first:** The invocations file at `/tmp/benchmark-v1-staging-20260415/invocations.md` — the "Execution mode" header section explains the substitution.

**Potential obstacles:** If the codex-collaboration MCP server fails to start (connection issue, missing dependency), the skill invocation will fail before reaching flag parsing. This is a server health issue, not a flag acceptance issue — diagnose separately.

### 2. Begin Phase 2 per-row execution starting with B1 baseline

**Dependencies:** Live runtime gate (#1) must pass.

**What to do:**
1. Fresh session for B1 baseline
2. Record session ID: `cat ~/.claude/plugins/data/codex-collaboration-inline/session_id`
3. Substitute `{run_type}` in the B1 baseline invocation from the invocations file
4. Paste the invocation
5. After completion, export transcript + synthesis to `/tmp/benchmark-v1-staging-20260415/`
6. Record run metadata using the template from the invocations file

**What to read first:** `/tmp/benchmark-v1-staging-20260415/invocations.md` — has the complete invocation string ready to paste. Also `operator-procedure.md:168-343` for the full Phase 2 procedure.

**Potential obstacles:**
- Session ID availability: if `~/.claude/plugins/data/codex-collaboration-inline/session_id` is missing, assign manual label and set `rehearsal: true` for that run.
- Evidence budget overflow: if `evidence_count` exceeds `max_evidence`, the run is invalid — record `valid: false` and schedule rerun.
- Transcript export: use `/export` or copy the synthesis artifact manually. Ensure the synthesis file captures the `<PRODUCTION_SYNTHESIS>` JSON.

### 3. Complete all 8 runs, then adjudicate and score

**Dependencies:** All 8 runs (4 rows x 2 systems) complete with artifacts in staging.

**What to do:** Follow Phases 3-5 in `operator-procedure.md`. Phase 3 (lines 340-480): claim inventory, labeling, safety, completeness, scope compliance. Phase 4 (lines 497-533): aggregate scoring (if SCORED). Phase 5 (lines 534-655): import from staging, fill `run_timestamp` and `operator`, commit.

**Potential obstacles:** Manual adjudication is the dominant cost — 80-160 individual claim adjudications estimated at 2-4 hours. High-signal rows first (B3 safety, B8 supersession).

## In Progress

**Clean stopping point — execution mode gate cleared, invocations prepared and reviewed.**

- **Approach:** Code-level gate verification + pre-built invocations packet with review cycle.
- **State:** Complete. Gate: SCORED. Invocations: 8 strings ready with `{run_type}` parameterization, reviewed through 3 findings.
- **Working:** All code-level evidence confirms `-p`/`-n` acceptance. Operator procedure path fixed. Invocations match manifest exactly.
- **Not working:** Nothing broken.
- **Next action:** Clear the live runtime gate in a fresh candidate session, then begin B1 baseline.

## Open Questions

### 1. Does the live runtime gate need a full dialogue, or just flag parsing confirmation?

**Context:** The code-level gate is cleared. A full runtime test would involve invoking `/codex-collaboration:dialogue "test" -p evaluative -n 2`, which starts a real dialogue with Codex (API call, turn budget, synthesis). A lighter test might just confirm flag parsing without completing the dialogue.

**Impact:** A full test consumes API resources and time (~5-10 min with timeout). A parsing-only test is faster but doesn't verify the full pipeline.

**Decision pending until:** The next fresh session. Suggest the minimal invocation — the flag parsing happens before any API call, so even if the dialogue fails for other reasons, the flag acceptance is confirmed.

### 2. Should `scope_envelope` be wired through the candidate skill?

**Context:** Carried from prior handoff. Both gatherer agents support `scope_envelope` but the skill doesn't pass it. Currently classified as "prompt-only" enforcement for both systems, which is v1-compliant but a known fragility.

**Impact:** Low for v1 (procedural enforcement is contract-compliant). Would strengthen scope control story if wired through.

**Decision pending until:** After benchmark execution — a nice-to-have, not blocking.

## Risks

### 1. Live runtime gate has not been cleared

**Impact:** While the code-level evidence is E2, a runtime failure (MCP server crash, plugin loading issue, environment difference) would force all runs to REHEARSAL, blocking AC-5.

**Mitigation:** The first candidate run naturally serves as a live gate — the invocations packet's `{run_type}` parameterization ensures mode can be switched without modifying the invocations.

### 2. Staging directory is in `/tmp/`

**Impact:** `/tmp/` may be cleared on reboot. If the machine reboots between runs and before Phase 5 import, all staging artifacts are lost.

**Mitigation:** Complete all runs and import in a continuous session if possible. Back up staging periodically: `cp -r /tmp/benchmark-v1-staging-20260415 ~/benchmark-v1-staging-backup`.

### 3. Manual adjudication remains the dominant cost

**Impact:** Carried from prior handoff. 4 rows x 2 systems = 8 syntheses, 80-160 individual adjudications, estimated 2-4 hours.

**Mitigation:** Row-by-row adjudication keeps context fresh. High-signal rows first (B3 safety, B8 supersession).

## References

### Commits this session

| Commit | Message | Scope |
|---|---|---|
| `58bcd73b` | fix(codex-collaboration): correct session ID path in benchmark operator procedure | `operator-procedure.md:184-187` — replace `~/.claude/session_id` with verified plugin path |

### Authority documents

| Document | Location | Role |
|---|---|---|
| Supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Acceptance authority |
| Benchmark contract (v1) | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Benchmark authority |
| Operator procedure | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | Execution procedure |
| Manifest | `docs/benchmarks/dialogue-supersession/v1/manifest.json` | Corpus and run conditions |

### Staging artifacts

| Artifact | Path | Status |
|---|---|---|
| Invocations packet | `/tmp/benchmark-v1-staging-20260415/invocations.md` | Ready (reviewed, 3 findings resolved) |
| Staging directory | `/tmp/benchmark-v1-staging-20260415/` | Created (prior session) |

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-15_21-45_t04-benchmark-v1-phase1-complete-ready-for-execution.md`
- Prior: `docs/handoffs/archive/2026-04-15_21-11_t04-rc4-resolved-posture-and-turn-budget-wired-through-candidate.md`
- Prior: `docs/handoffs/archive/2026-04-15_19-30_t04-benchmark-v1-scaffold-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-15_15-00_t04-ac4-closed-benchmark-v1-contract-rewrite.md`
- Prior: `docs/handoffs/archive/2026-04-14_23-30_t04-gatherer-implementation-merged-and-e2e-smoke-run.md`
- Prior: `docs/handoffs/archive/2026-04-14_22-45_t04-gatherer-plan-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_20-17_t04-v1-e2e-verified-pr-106-open.md`
- Prior: `docs/handoffs/archive/2026-04-14_16-30_t04-v1-four-production-surfaces-authored-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_12-55_t04-v1-section-10-authoring-decisions-resolved-and-committed.md`

## Gotchas

### `~/.claude/session_id` does not exist

**Symptom:** `cat ~/.claude/session_id` returns "No such file or directory."

**Root cause:** Claude Code does not create this file. Session IDs are delivered via the SessionStart hook payload to plugins, not written to a platform-level file.

**Prevention:** Use the plugin-specific path: `~/.claude/plugins/data/codex-collaboration-inline/session_id`. The operator procedure now references this path (fixed at `58bcd73b`).

### `CLAUDE_PLUGIN_DATA` unavailable in Bash tool

**Symptom:** `echo $CLAUDE_PLUGIN_DATA` returns empty in Bash tool commands.

**Root cause:** The Bash tool runs in independent subprocesses without the Claude Code plugin environment. `CLAUDE_PLUGIN_DATA` is set only for plugin hooks and MCP server processes.

**Prevention:** Use resolved absolute paths (`~/.claude/plugins/data/<plugin-name>/`) when accessing plugin data from the Bash tool.

### Invocations that pre-commit to mode decisions before gate clearance

**Symptom:** Operator packet says "SCORED" and every invocation contains "This is a scored benchmark run." before the live runtime gate has passed.

**Root cause:** Author optimism — the code-level evidence was strong enough that the mode was assumed locked.

**Prevention:** Parameterize mode-dependent strings with placeholders (`{run_type}`). Include a substitution table. Document all decision points that can override the mode.

## Conversation Highlights

### User's review of invocations packet

User provided structured code review findings (P1, P2, P3) against the invocations file with specific line citations and confidence scores. The findings were procedurally grounded — each cited specific operator-procedure lines where the packet's assumptions could be violated.

P1 finding quote: "This packet globally declares `Execution mode: SCORED`, hardcodes the scored run-type string into every invocation, and assumes scored metadata before the live execution-mode gate has actually been cleared."

P3 finding quote: "The updated checklist correctly reclassifies a run to rehearsal when the canonical session-id file is unavailable, but it never tells the operator what to put in `session_id` for that run."

### User's gate interpretation clarification

User confirmed: "This is the fresh session" — establishing that the handoff-load session counts as the fresh session for gate verification. Later confirmed that "Before Phase 2" in the invocations header means a separate pre-run gate check, not the first benchmark run itself.

## User Preferences

### Procedure adherence is strict (carried from prior sessions)

User treats the operator procedure as authoritative and enforces its sequencing. The P1 finding demonstrates this: even when the outcome is predictable (code evidence strongly supports SCORED), the procedure says to verify before declaring mode, so the packet must not pre-commit.

### Code review findings with structured format (carried from prior sessions)

User provides review findings as structured annotations with priority, confidence, title, body, and file:line references. They expect fixes to address each finding individually with confirmation.

### Pre-work with citations (carried from prior sessions)

User independently performs preparatory work with specific file:line citations, presenting results in structured tables. They expect the same citation precision in return.

### Contract text is authoritative (carried from prior sessions)

Run condition vs. field timing distinctions enforced exactly. Paraphrasing or extending contract/procedure provisions beyond their literal scope is rejected.

### Honest documentation over false confidence (carried from prior sessions)

Parameterized `{run_type}` over hardcoded "scored" demonstrates this preference — state what's true (gate cleared at code level, not runtime level) rather than what's expected.
