---
date: 2026-04-14
time: "23:30"
created_at: "2026-04-15T03:30:00Z"
session_id: 2023b247-0133-4f75-aa67-724e9fd8a89f
resumed_from: docs/handoffs/archive/2026-04-14_22-45_t04-gatherer-plan-reviewed-and-committed.md
project: claude-code-tool-dev
branch: main
commit: e13a1b87
title: "T-04 gatherer implementation merged, E2E smoke run completed, timeout fix landed"
type: handoff
files:
  - packages/plugins/codex-collaboration/agents/context-gatherer-code.md
  - packages/plugins/codex-collaboration/agents/context-gatherer-falsifier.md
  - packages/plugins/codex-collaboration/references/tag-grammar.md
  - packages/plugins/codex-collaboration/skills/dialogue/SKILL.md
  - packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md
  - packages/plugins/codex-collaboration/server/runtime.py
---

# T-04 Gatherer Implementation Merged, E2E Smoke Run Completed, Timeout Fix Landed

## Goal

Implement the T-04 gatherer plan (`99472736`), merge it, run an E2E smoke test of the full v2 `/dialogue` pipeline, and resolve any issues uncovered.

**Trigger.** Resumed from `2026-04-14_22-45` handoff. User directed: "Continue with implementing the build order from the plan. Start by reading the plan and the relevant files. Then, create a task list." The prior session designed and committed the plan; this session implements it.

**Stakes.** The gatherer plan is the second T-04 production slice, advancing acceptance criteria 3 (gatherer agents) and 4 (synthesis with bounded citations and convergence). Without implementation, the plan is a design document with no runtime path. The E2E smoke test validates the entire v2 pipeline — gatherer dispatch, assembly, briefing injection, orchestrator integration, and `citation_tier` provenance.

**Success criteria achieved this session:**

1. All 5 files from the plan's §9 file inventory implemented — **achieved** (3 new, 2 modified).
2. 566 existing tests pass unchanged — **achieved** (`566 passed in 4.08s`).
3. Implementation reviewed through 2 rounds (5 findings, all resolved) — **achieved**.
4. PR #107 merged — **achieved** (`d478c0d7`).
5. E2E `/dialogue` smoke test executed with v2 pipeline — **achieved** (gatherers, assembly, briefing injection all worked; Codex dialogue timed out but pipeline was fully validated).
6. Timeout root cause identified and fixed — **achieved** (`e13a1b87`, `request_timeout` 30→300, notification timeout 60→300).

**Position in the T-04 arc:**

| Session | Role | Artifact |
|---|---|---|
| 2026-04-13 | v1 plan drafting and approval | Plan at `main@73f8c9c1` |
| 2026-04-14 12:55 | §10 authoring decisions | Addendum committed |
| 2026-04-14 16:30 | Four production surfaces authored | Committed `05b7db3a` |
| 2026-04-14 20:17 | E2E verified, report committed, PR #106 open | `7a1bd077`, PR #106 |
| 2026-04-14 22:45 | PR #106 merged, gatherer plan designed and committed | Merged `c3c11fa4`, plan at `99472736` |
| **2026-04-14 23:30 (this)** | **Gatherer implementation merged, E2E smoke run, timeout fix** | **PR #107 merged `d478c0d7`, timeout fix `e13a1b87`** |
| Next | Re-run E2E smoke with 300s timeout to complete AC-4 verification | |

## Session Narrative

**Phase 1 — Implementation (~30 min).**

Loaded the `2026-04-14_22-45` handoff. Read the full 888-line plan in chunks (§1-§12) plus all four cross-model semantic sources: `context-gatherer-code.md` (112 lines), `context-gatherer-falsifier.md` (158 lines), cross-model `/dialogue` SKILL.md (524 lines), and `tag-grammar.md` (116 lines). Created a 7-task dependency graph: tasks 1-3 (independent foundation: tag grammar, code explorer, falsifier) → task 4 (skill updates, blocked by 1-3) → task 5 (orchestrator updates, independent) → task 6 (regression tests, blocked by 4+5) → task 7 (acceptance criteria verification, blocked by 6).

Wrote all three foundation files in parallel: tag-grammar reference (frozen copy, codex-collaboration-owned), context-gatherer-code agent (adapted from cross-model with `scope_envelope`, `objective` input, `maxTurns: 20`), context-gatherer-falsifier agent (adapted similarly with TYPE whitelist, no-assumptions fallback).

The skill update was the largest change: restructured steps 5-7 into the gatherer pipeline (5 → revised single-run check with two-tier liveness, 5-lock → acquire, 5a → assumption extraction, 5b → parallel gatherer dispatch, 5c → 10-step assembly pipeline, 5d → quality log, 6 → seed write, 7 → modified dispatch with briefing prepend, 8 → surface synthesis with nullable citation handling). Added try/finally lock lifecycle.

Orchestrator update was surgical (~25 lines): briefing detection in Phase 1, deterministic objective extraction rule, `citation_tier` emission in Phase 5, `representative_citation` constraint (dialogue-tier only, null when no dialogue-tier evidence).

566 tests passed unchanged on first run.

**Phase 2 — Review rounds (~20 min).**

User conducted two review rounds with 5 total findings:

**Round 1 (3 findings):**
- P1: Gatherer launches have no timeout while session lock is held. Plan specified 120s timeouts; Agent tool has no `timeout` parameter. Fix: added `maxTurns: 20` to both agent definitions, documented as the bounding mechanism, added explicit failure-during-gathering handling.
- P1: Orchestrator no longer gets explicit raw objective. The dispatch replaced the original prompt instead of prepending the briefing. Fix: restored original v1 dispatch format after the briefing, with authority guidance for which copy is operative.
- P2: Retry prompt hardcodes `[SRC:code]` for all CLAIMs, conflicting with falsifier's `[SRC:docs]` domain. Fix: split retry prompt into gatherer-specific variants.

**Round 2 (2 findings):**
- P2: Objective authority rule exists only in the skill, not in the orchestrator body. The orchestrator needs its own extraction rule since it doesn't read the skill. Fix: added deterministic extraction rule to orchestrator Phase 1 — "text after briefing, before `Repository root:`."
- P3: Abandoned-pointer cleanup uses `rm`, violating repo's no-`rm` rule. Fix: changed to `trash` in all cleanup paths.

After round 2: zero findings. User confirmed: "From a review standpoint, this is ready to commit."

**Phase 3 — Merge and E2E smoke (~40 min).**

Committed at `fd4b6a53`, pushed, PR #107 created and merged by user via GitHub UI (`d478c0d7`). Synced local main, deleted feature branch.

Attempted E2E smoke test. First invocation loaded v1 skill (plugin cache not updated). Discovered the dev-vs-production deployment gap: the codex-collaboration plugin is an **inline plugin** loaded from the repo path, but the skill cache needed `/reload-plugins` to pick up changes. After user ran `/reload-plugins`, re-invoked `/dialogue` and the v2 skill loaded successfully.

Executed the full v2 procedure:
- Steps 1-4: repo root, session ID, stale cleanup — all passed
- Step 5: generated `run_id` (`d84219d0-b5a4-460f-bf59-5574d4cf90ba`), no existing active-run pointer
- Step 5-lock: wrote active-run pointer
- Step 5a: extracted 3 assumptions (A1: SubagentStart fires for orchestrator, A2: seed exists when hook reads it, A3: scope materialization happens during SubagentStart) + 6 key terms
- Step 5b: dispatched gatherers in parallel. Code explorer returned 22 tagged lines (20 CLAIM, 2 OPEN) on first attempt. Falsifier **exhausted `maxTurns`** on first attempt (31 tool calls, 0 tagged lines — all narrative). Retry with format-reinforcing prompt produced 9 tagged lines (1 COUNTER, 3 CONFIRM, 5 OPEN).
- Step 5c: ran 10-step assembly. 31 total lines, 27 citations, 6 unique files, 0 provenance violations, no warnings.
- Step 5d: logged quality summary
- Step 6: wrote containment seed
- Step 7: dispatched orchestrator with assembled briefing prepended + raw objective after briefing
- Orchestrator ran Phase 1 (briefing detection worked), but Codex dialogue failed: `codex.dialogue.reply` returned "JSON-RPC read failed: timed out waiting for message" on both attempts
- Step 8: surfaced synthesis (error termination, `converged: false`, all 8 `synthesis_citations` entries carry `citation_tier: "seed"`)
- Finally block: released active-run pointer via `trash`

**Phase 4 — Timeout investigation and fix (~15 min).**

User asked why the Codex dialogue failed. Checked MCP server status — healthy, authenticated, no errors. Traced the timeout chain: the error at `jsonrpc_client.py:142-143` fires when `_message_queue.get(timeout=effective_timeout)` times out. The inner timeout was `request_timeout=30.0` at `runtime.py:20`, and a secondary notification timeout was `60.0` at `runtime.py:144`. User directed bumping both to 300. Created `fix/codex-request-timeout` branch, changed both values, 566 tests passed, merged to main at `e13a1b87`.

## Decisions

### Decision 1: `maxTurns: 20` as gatherer execution bound

**Choice:** Add `maxTurns: 20` to both gatherer agent definitions as the primary execution bounding mechanism.

**Driver:** Review finding P1 — the plan specified 120-second wall-clock timeouts, but the Agent tool has no `timeout` parameter. The skill was claiming timeout recovery it couldn't deliver.

**Alternatives considered:**
- **Wall-clock timeout on Agent calls.** Not available — the Agent tool schema has no `timeout` parameter.
- **No bound.** Rejected: a stuck gatherer would hold the session lock indefinitely.

**Trade-offs accepted:** `maxTurns` bounds computation (tool calls), not wall time. A gatherer doing many small reads could still take significant time, but the practical bound for Glob/Grep/Read agents is reasonable (~60-90 seconds for 20 turns).

**Confidence:** Medium (E1) — `maxTurns` is the only available mechanism. Verified that the falsifier's first run exhausted ~20 turns in ~53 seconds, validating the bound is in the right range.

**Reversibility:** High — frontmatter field, trivial to adjust.

**Change trigger:** If the Agent tool adds a `timeout` parameter in the future, that would be the proper mechanism.

### Decision 2: Explicit objective in orchestrator prompt (dual placement)

**Choice:** The objective appears twice in the orchestrator prompt: once inside the briefing's `## Objective` section (structural) and once as the top-level field after the briefing (operative). The orchestrator uses the top-level copy.

**Driver:** Review finding P1 — the initial implementation replaced the v1 dispatch prompt with the briefing, losing the explicit raw objective. The plan §8.3 step 7 explicitly specified `"{assembled_briefing}\n\n{original_dispatch_prompt}"` — prepend, don't replace.

**Alternatives considered:**
- **Single objective inside briefing only.** Rejected: the orchestrator would have to infer which part of the prompt is "the objective" vs. seed evidence.
- **Remove objective from briefing.** Rejected: the briefing's `## Objective` section serves the assembler's record for structural completeness.

**Trade-offs accepted:** Duplication — the objective appears twice. Mitigated by explicit authority guidance in both the skill (step 7) and the orchestrator (Phase 1 extraction rule).

**Confidence:** High (E2) — matches the plan's specification and was validated by review round 2 (objective authority rule placed in both surfaces).

**Reversibility:** High — prompt structure change only.

**Change trigger:** If the orchestrator's Phase 2 consistently misidentifies the objective, simplify to single placement with a more explicit delimiter.

### Decision 3: Bump Codex app server timeouts to 300 seconds

**Choice:** Changed `request_timeout` from 30.0 to 300.0 and notification timeout from 60.0 to 300.0 in `server/runtime.py`.

**Driver:** E2E smoke test failed with "JSON-RPC read failed: timed out waiting for message." Traced to `jsonrpc_client.py:142` — the 30-second default was insufficient for Codex dialogue replies that involve a full OpenAI API round-trip.

**Alternatives considered:**
- **Environment variable configuration.** More flexible but adds complexity for a single-value change. Could be added later if different deployments need different values.
- **Per-call timeout.** The Codex app server protocol supports `timeoutMs` and `disableTimeout` on requests. More surgical but requires changes to the MCP tool implementation, not just the runtime default.

**Trade-offs accepted:** A 300-second timeout means a genuinely stuck Codex connection takes 5 minutes to time out instead of 30 seconds. Accepted because dialogue replies legitimately take 30+ seconds for complex prompts.

**Confidence:** High (E2) — root cause identified precisely at `jsonrpc_client.py:142`, fix is a default value change with no behavioral side effects.

**Reversibility:** High — single line change in `runtime.py`.

**Change trigger:** If 300 seconds proves too long for failure detection, consider per-operation timeouts (shorter for `dialogue_start`, longer for `dialogue_reply`).

## Changes

### `packages/plugins/codex-collaboration/references/tag-grammar.md` (NEW, 111 lines)

**Purpose:** Codex-collaboration-owned frozen copy of the prefix-tagged line grammar. Contract surface between gatherer agents and the assembly pipeline.

**Approach:** Adapted from cross-model semantic source (`packages/plugins/cross-model/skills/dialogue/references/tag-grammar.md`). Same grammar, parse rules, and edge cases. Updated assembly step crosswalk references to point to codex-collaboration's SKILL.md. Independently owned and versioned per plan D5.

### `packages/plugins/codex-collaboration/agents/context-gatherer-code.md` (NEW, 119 lines)

**Purpose:** Code explorer gatherer agent. Question-driven codebase exploration, emitting prefix-tagged lines for assembly.

**Approach:** Adapted from cross-model semantic source. Key adaptations: input field `question` → `objective`, added `key_terms` input, added `scope_envelope` (optional, reserved for benchmark runs), `maxTurns: 20`, 8-file read cap, references codex-collaboration-owned tag grammar. Tools: Glob, Grep, Read. Model: Sonnet.

### `packages/plugins/codex-collaboration/agents/context-gatherer-falsifier.md` (NEW, 165 lines)

**Purpose:** Falsifier gatherer agent. Repo-first assumption tester with no-assumptions fallback.

**Approach:** Adapted from cross-model semantic source. Same adaptations as code explorer plus: TYPE whitelist (5 types), 3 COUNTER cap, no-assumptions fallback with `[SRC:docs]` provenance, `maxTurns: 20`. Tools: Glob, Grep, Read. Model: Sonnet.

### `packages/plugins/codex-collaboration/skills/dialogue/SKILL.md` (MODIFIED, +197/-26)

**Purpose:** Add gatherer pipeline, revised lock lifecycle, briefing assembly, and `citation_tier` rendering.

**Approach:** Restructured steps 5-7 per plan §8.3:
- Step 5: revised single-run check with two-tier liveness (seed/scope present → block, absent → clean up)
- Step 5-lock: acquire active-run pointer before gatherer work
- Steps 5a-5d: assumption extraction, parallel gatherer dispatch, 10-step deterministic assembly pipeline, quality log
- Step 6: seed write (separated from active-run pointer)
- Step 7: briefing prepended to original dispatch prompt; explicit objective after briefing
- Step 8: nullable `representative_citation` rendering (shows `—`); `citation_tier` in citations
- Lock lifecycle: try/finally guard with `trash`-based cleanup
- Failure handling: gatherer-specific retry prompts, graceful degradation on gatherer failure

### `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md` (MODIFIED, +25/-3)

**Purpose:** Briefing detection, objective extraction, `citation_tier` emission, `representative_citation` constraint.

**Approach:** Surgical additions to Phase 1 and Phase 5:
- Phase 1: briefing sentinel detection, `briefing-meta` JSON parsing, Phase 1 adjustment guidance (reprioritize targets, don't suppress reads), deterministic objective extraction rule ("text after briefing, before `Repository root:`")
- Phase 5: `citation_tier: "seed" | "dialogue"` on `synthesis_citations[]`, `representative_citation` constraint (dialogue-tier only, null when no dialogue-tier evidence), assignment rules

### `packages/plugins/codex-collaboration/server/runtime.py` (MODIFIED, +2/-2)

**Purpose:** Bump Codex app server timeouts from 30s/60s to 300s/300s.

**Approach:** Changed `request_timeout` default at line 20 and notification timeout at line 144. No behavioral change beyond timeout duration.

## Codebase Knowledge

### Codex-collaboration plugin is an inline plugin

The codex-collaboration plugin is NOT in the turbo-mode marketplace (`marketplace.json`). It's deployed as an **inline plugin** with MCP server via `.mcp.json`. The plugin loads skills and agents from the repo path (`packages/plugins/codex-collaboration/`), but skill content is cached by Claude Code. After modifying skill files, `/reload-plugins` is required to pick up changes. Plugin data is at `~/.claude/plugins/data/codex-collaboration-inline/`.

### Timeout chain: two levels

| Level | Location | Default | What it bounds |
|---|---|---|---|
| Inner | `runtime.py:20` (`request_timeout`) | 300.0 (was 30.0) | JSON-RPC client → Codex app server response time |
| Inner | `runtime.py:144` (notification timeout) | 300.0 (was 60.0) | Wait for next notification from Codex during turn execution |
| Outer | Claude Code MCP transport | (system default) | Claude Code → codex-collaboration MCP server |

The error "JSON-RPC read failed: timed out waiting for message" is raised at `jsonrpc_client.py:142` when `_message_queue.get(timeout=effective_timeout)` returns `Empty`.

### Falsifier retry path exercised in smoke test

The falsifier's first run used 31 tool calls in 53 seconds but produced 0 tagged lines (all narrative exploration). The `maxTurns: 20` bound was hit. The assembly pipeline's retry mechanism (step 2) re-launched with the format-reinforcing prompt, which produced 9 well-formed tagged lines. This validates: (1) `maxTurns` bounds execution, (2) retry detects low output (<4 parseable lines), (3) gatherer-specific retry prompts work (falsifier got `[SRC:docs]` guidance).

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `docs/plans/2026-04-14-t04-pre-dialogue-gatherers-and-briefing-assembly.md` (888 lines, full) | Implementation blueprint | 12 sections, 10 decisions, build order in §9 |
| `packages/plugins/cross-model/agents/context-gatherer-code.md` | Semantic source for code explorer | 112 lines; CLAIM + OPEN tags, code domain, 40-line cap |
| `packages/plugins/cross-model/agents/context-gatherer-falsifier.md` | Semantic source for falsifier | 158 lines; COUNTER/CONFIRM/OPEN, no-assumptions fallback |
| `packages/plugins/cross-model/skills/dialogue/references/tag-grammar.md` | Semantic source for tag grammar | 116 lines; parse rules, assembly processing order |
| `packages/plugins/codex-collaboration/skills/dialogue/SKILL.md` | Integration target (modified) | v1 was 151 lines; v2 is ~250 lines |
| `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md` | Integration target (modified) | Phase 1 and Phase 5 extended |
| `packages/plugins/codex-collaboration/.mcp.json` | Plugin deployment config | stdio transport, uv run, CODEX_SANDBOX=seatbelt |
| `packages/plugins/codex-collaboration/server/runtime.py` | Timeout investigation | `request_timeout=30.0` at line 20 was the bottleneck |
| `packages/plugins/codex-collaboration/server/jsonrpc_client.py:137-144` | Timeout error source | `_get_message` raises TimeoutError from `Empty` queue |

## Context

### Mental model for this session

This session bridges **design** and **runtime validation**. The first half (implementation, review, merge) turned the 888-line plan into 5 production files. The second half (E2E smoke) proved the pipeline works at runtime — not just as markdown contracts but as an actual execution path. The timeout discovery and fix was unplanned but high-value: without it, every future `/dialogue` run would fail.

### T-04 acceptance criteria status after this session

| AC | Description | Status | Evidence |
|---|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) | `skills/dialogue/SKILL.md` |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) | `agents/dialogue-orchestrator.md` |
| 3 | Gatherer agents exist and use Claude-side tools | **Done (PR #107)** | Both agents with Glob/Grep/Read |
| 4 | Synthesis with bounded citations and convergence | **Substantially done** | `citation_tier` emitted in smoke test; full validation needs successful Codex dialogue |
| 5 | Benchmark candidate scored runs | Blocked by T4-BR-07 | |
| 6 | Context-injection retirement decision | Depends on benchmark evidence | |
| 7 | Reference unification | Open, separate | |

### E2E smoke test results

| Pipeline stage | Result | Detail |
|---|---|---|
| Steps 1-4 (preflight) | Pass | Repo root, session ID, stale cleanup all worked |
| Step 5 (single-run check) | Pass | No active-run, generated `run_id`, acquired lock |
| Step 5a (assumptions) | Pass | 3 assumptions extracted, 6 key terms |
| Step 5b (gatherers) | Pass (with retry) | Code explorer: 22 lines first attempt. Falsifier: 0 lines → retry → 9 lines |
| Step 5c (assembly) | Pass | 10-step pipeline, 27 citations, 6 unique files, no warnings |
| Step 7 (orchestrator) | Partial | Briefing detected, Phase 1 ran, but Codex dialogue timed out |
| Step 8 (synthesis) | Pass (degraded) | Terminal synthesis with all `citation_tier: "seed"` |
| Lock lifecycle | Pass | Lock acquired, held through pipeline, released in finally |

## Learnings

### Plugin reload required after modifying inline plugin skills

**Mechanism.** The codex-collaboration plugin loads from the repo path (`packages/plugins/codex-collaboration/`) as an inline plugin. Claude Code caches skill content at session start. After committing and merging skill changes, the running session still serves the cached (pre-merge) version. `/reload-plugins` forces a re-read.

**Evidence.** First `/dialogue` invocation loaded v1 procedure (no gatherer steps). After `/reload-plugins`, the v2 procedure loaded correctly.

**Implication.** After modifying codex-collaboration skills in the repo, always run `/reload-plugins` before testing.

### Falsifier needs format reinforcement for first-run reliability

**Mechanism.** The falsifier explored the codebase for 31 tool calls but emitted zero tagged lines — all output was narrative exploration text. The `maxTurns: 20` bound stopped it, and the retry with format-reinforcing prompt produced 9 well-formed tagged lines.

**Evidence.** Smoke test: falsifier first run = 0 tagged lines in 53s. Retry = 9 tagged lines in 64s.

**Implication.** The retry mechanism is load-bearing for the falsifier, not just a safety net. Consider strengthening the falsifier's initial prompt to emphasize output format more heavily, or adding examples of tagged output at the end of the prompt.

### JSON-RPC timeout is the dialogue bottleneck, not the MCP transport

**Mechanism.** The `codex.dialogue.reply` tool sends a message to the Codex app server, which calls the OpenAI API and waits for a response. The JSON-RPC client (`jsonrpc_client.py`) has a `request_timeout` that governs how long it waits. The MCP transport timeout (Claude Code → MCP server) is separate and was not hit.

**Evidence.** MCP server status was healthy (authenticated, no errors) after the timeout. The error message "JSON-RPC read failed: timed out waiting for message" matches `jsonrpc_client.py:142-143` exactly.

**Implication.** The 300s timeout should accommodate most Codex responses. If specific operations need shorter timeouts (e.g., `dialogue_start` vs. `dialogue_reply`), per-operation timeouts would be more surgical.

## Next Steps

### 1. Re-run E2E smoke test with 300s timeout

**Dependencies:** Timeout fix landed at `e13a1b87`. Requires a fresh session (or `/reload-plugins`) for the runtime to pick up the new timeout values.

**What to do:**
1. Start a fresh session or run `/reload-plugins`
2. Invoke `/dialogue <objective>` with a meaningful objective
3. Verify: gatherers dispatch, briefing assembles, orchestrator receives briefing, Codex dialogue completes, synthesis includes both `"seed"` and `"dialogue"` tier citations
4. If successful, AC-4 can be marked complete

**What to read first:** This handoff's E2E smoke test results table (shows which stages passed).

**Potential obstacles:** The Codex app server or OpenAI API could still be slow. If 300s is still insufficient, investigate per-operation timeouts or async notification handling.

### 2. Consider strengthening falsifier initial prompt

**Dependencies:** None — independent improvement.

**What to do:** The falsifier's first run produced 0 tagged lines despite 31 tool calls. The retry mechanism saved it, but the initial prompt could be stronger. Consider adding 2-3 tagged-line examples at the end of the prompt to prime the output format.

**Potential obstacles:** Adding examples increases prompt size, which may reduce the agent's exploration budget within `maxTurns: 20`.

## In Progress

**Clean stopping point — implementation merged, E2E smoke exercised, timeout fix landed. No work in flight.**

- **Approach:** Build-order implementation from plan §9, then E2E validation, then runtime issue fix.
- **State:** Complete. PR #107 merged (`d478c0d7`), timeout fix merged (`e13a1b87`).
- **Working:** Full v2 pipeline (gatherer dispatch, assembly, briefing injection, lock lifecycle). 566 tests pass.
- **Not working:** Codex dialogue timed out at 30s during smoke test. Fixed by bumping to 300s, but not yet re-tested.
- **Open question:** Whether 300s is sufficient for production dialogue replies.
- **Next action:** Re-run E2E smoke test in a fresh session with 300s timeouts.

## Open Questions

### 1. Is 300 seconds sufficient for Codex dialogue replies?

**Context:** The 30s default was clearly too short. 300s is generous but untested under the new value. The OpenAI API latency for complex prompts could vary.

**Impact:** If still insufficient, per-operation timeouts (shorter for `dialogue_start`, longer for `dialogue_reply`) would be more surgical.

**Decision pending until:** Next E2E smoke test.

### 2. Should the falsifier's initial prompt be strengthened?

**Context:** The falsifier produced 0 tagged lines on its first attempt despite 31 tool calls. The retry mechanism saved it, but this wastes one gatherer dispatch worth of time (~53 seconds).

**Impact:** Low — retry works. But if strengthening the prompt eliminates the need for retry in most cases, it saves ~60 seconds per `/dialogue` invocation.

**Decision pending until:** After observing a few more `/dialogue` runs to see if the first-run failure is consistent.

## Risks

### 1. Codex dialogue may still time out at 300s

**Impact:** AC-4 cannot be fully verified without a successful Codex dialogue. If 300s is still insufficient, the E2E verification remains incomplete.

**Mitigation:** Per-operation timeouts. The Codex app server protocol supports `timeoutMs` and `disableTimeout` on requests — these could be used for more granular control.

### 2. Falsifier retry adds ~60s to every dialogue invocation where it triggers

**Impact:** If the falsifier consistently needs retry, every `/dialogue` run takes ~60 seconds longer than necessary. Across many invocations, this accumulates.

**Mitigation:** Strengthen the falsifier's initial prompt. Or reduce `maxTurns` from 20 to 15 to trigger the retry sooner.

## References

### Commits this session

- `fd4b6a53` on `feature/t04-pre-dialogue-gatherers` — feat(codex-collaboration): add pre-dialogue gatherer agents and briefing assembly (merged as PR #107)
- `e13a1b87` on `fix/codex-request-timeout` — fix(codex-collaboration): bump Codex app server timeouts from 30s/60s to 300s (merged to main directly)

### PRs

- PR #107: merged at `d478c0d7` — feat(codex-collaboration): T-04 pre-dialogue gatherers and briefing assembly

### Authority documents

| Document | Location | Role |
|---|---|---|
| Supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Acceptance authority |
| Gatherer plan | `docs/plans/2026-04-14-t04-pre-dialogue-gatherers-and-briefing-assembly.md` | This slice design |
| Cross-model code explorer | `packages/plugins/cross-model/agents/context-gatherer-code.md` | Semantic source |
| Cross-model falsifier | `packages/plugins/cross-model/agents/context-gatherer-falsifier.md` | Semantic source |

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-14_22-45_t04-gatherer-plan-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_20-17_t04-v1-e2e-verified-pr-106-open.md`
- Prior: `docs/handoffs/archive/2026-04-14_16-30_t04-v1-four-production-surfaces-authored-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_12-55_t04-v1-section-10-authoring-decisions-resolved-and-committed.md`

## Gotchas

### Inline plugins need `/reload-plugins` after file changes

**Symptom:** `/dialogue` loads the v1 skill procedure despite the v2 version being committed and merged to main.

**Root cause:** Claude Code caches plugin skill content at session start. Inline plugins (loaded from repo path via `.mcp.json`) are cached like marketplace plugins. The cache doesn't auto-refresh on file changes.

**Prevention:** After modifying codex-collaboration skills in the repo, always run `/reload-plugins` before testing. A fresh session also works.

### `CLAUDE_PLUGIN_DATA` not set for manual script invocation

**Symptom:** `python3 scripts/clean_stale_shakedown.py` fails with "CLAUDE_PLUGIN_DATA not set."

**Root cause:** Plugin scripts expect environment variables set by the plugin runtime. Manual Bash invocations don't have these variables.

**Prevention:** Prefix manual invocations with the env var: `CLAUDE_PLUGIN_DATA=/Users/jp/.claude/plugins/data/codex-collaboration-inline python3 scripts/clean_stale_shakedown.py`

### Codex app server 30s default timeout is too short for dialogue replies

**Symptom:** `codex.dialogue.reply` returns "JSON-RPC read failed: timed out waiting for message."

**Root cause:** `request_timeout=30.0` at `runtime.py:20` is the default for the JSON-RPC client to the Codex app server. Dialogue replies involve a full OpenAI API round-trip that can exceed 30 seconds for complex prompts.

**Prevention:** Fixed by bumping to 300.0 at commit `e13a1b87`. If this recurs, investigate per-operation timeouts via the Codex app server protocol's `timeoutMs` parameter.

## Conversation Highlights

### User's review discipline continues

Two rounds, 5 findings (3 P1, 1 P2, 1 P3), each progressively narrower. User's first round caught the three most impactful issues (timeout bounds, lost objective, provenance corruption). Second round caught the orchestrator-side authority gap and a repo policy violation. Clean after round 2.

### User confirmed pipeline success despite Codex failure

User's assessment of the E2E smoke: "I also agree that the next natural build item is the E2E smoke run. It is the highest-signal next step because it validates the new runtime path before you spend time on benchmark execution or reference-unification work. If that smoke run passes, you can likely mark AC-4 complete."

### User's timeout investigation

User asked "Why did the Codex dialogue fail?" — a direct diagnostic question. After seeing the healthy MCP status and the timeout chain analysis, user directed: "Yes bump it to 300." Then: "yes commit, merge, and clean up" — decisive, no discussion needed once root cause was clear.

## User Preferences

### Review-then-commit discipline (continued)

User continues the pattern from prior sessions: implementation → review → fix → re-review → commit only when findings reach zero. This session's two-round pattern is consistent with prior sessions (v1 had 6 rounds for the plan, 2 rounds for code).

### Direct action on clear root causes

When the timeout root cause was traced to a specific line (`jsonrpc_client.py:142`), user directed the fix immediately without exploring alternatives: "Yes bump it to 300." For clear root causes, user prefers direct action over design discussion.

### Merge-to-main for small fixes

User directed commit-merge-cleanup for the timeout fix rather than a PR. Small, single-purpose fixes on clear root causes go through the fast path. Contrast with the gatherer implementation which went through a full PR (#107).
