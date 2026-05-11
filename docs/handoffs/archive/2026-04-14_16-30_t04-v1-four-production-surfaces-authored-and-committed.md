---
date: 2026-04-14
time: "16:30"
created_at: "2026-04-14T20:30:00Z"
session_id: 4ab19c41-0342-4f98-827e-5d8b85734a19
resumed_from: docs/handoffs/archive/2026-04-14_12-55_t04-v1-section-10-authoring-decisions-resolved-and-committed.md
project: claude-code-tool-dev
branch: feature/t04-v1-implementation
commit: 05b7db3a
title: "T-04 v1 four production surfaces authored and committed"
type: handoff
files:
  - packages/plugins/codex-collaboration/references/dialogue-turn-contract.md
  - packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md
  - packages/plugins/codex-collaboration/skills/dialogue/SKILL.md
  - packages/plugins/codex-collaboration/hooks/hooks.json
---

# T-04 v1 Four Production Surfaces Authored and Committed

## Goal

Author the four new v1 surfaces named in the T-04 v1 scoping plan's §12 implementation order, close out §12 steps 1–4, and land them on the feature branch as a single commit ready for merge.

**Trigger.** User resumed from the prior handoff (`2026-04-14_12-55`) where §10 authoring-time decisions were resolved and committed. User's directive: "Proceed with task 2 (extract turn-semantics reference doc from dialogue-codex)." Then: "continue with the plan order" for tasks 3–5.

**Stakes.** These four surfaces constitute the entire code-level deliverable of the T-04 v1 first production slice. Without them, the `/dialogue` invocation path doesn't exist. The turn-semantics reference doc is the production-local authority that decouples production from shakedown. The hook matcher extension prevents silent containment defeat (plan §9.1). The orchestrator body is the largest single artifact — self-contained per-turn contract implementation with production synthesis emission.

**Success criteria achieved this session:**

1. Extract turn-semantics reference doc from `dialogue-codex` — **achieved** (406 lines, reviewed by background agent, 4 review findings fixed).
2. Author `dialogue-orchestrator` agent body — **achieved** (313 lines, reviewed by background agent, all 9 acceptance criteria passed).
3. Author `/dialogue` user skill — **achieved** (150 lines).
4. Extend `hooks.json` SubagentStart/SubagentStop matchers — **achieved** (2-line edit).
5. 566-test shakedown suite passes unchanged — **achieved** (ran 4 times across the session, green every time).
6. All four surfaces committed on feature branch — **achieved** (`05b7db3a`).

**Bigger picture.** This session converts the approved scoping plan + authoring decisions into implemented code surfaces. The plan is the contract; the addendum is the implementation-time ledger; these four surfaces are the implementation. T-04 v1 packet arc is now: draft → rewrite → approve → close §10 → **author the four surfaces (this)** → verify (next).

## Session Narrative

**Phase 1 — Load, merge, and orient (~5 min).**

Loaded `2026-04-14_12-55` handoff. User first directed: merge the addendum commit branch. Used `/merge-branch` skill — fast-forward merge of `feature/t04-v1-implementation` into `main`, branch deleted. `main` advanced to `30edf38a`. Then user directed: "Proceed with task 2."

**Phase 2 — Plan and source re-read (~10 min).**

Read three source files in parallel: `dialogue-codex/SKILL.md` (455 lines — the extraction source), the full plan (637 lines), and the authoring-decisions addendum (127 lines). Also read `shakedown-dialogue.md` (18 lines — agent body precedent for structural patterns). Created 8-task tracking list mirroring plan §12 plus branch-setup prefix. Created new `feature/t04-v1-implementation` from `main`.

**Phase 3 — Reference doc extraction (task 2, ~20 min).**

The core design question was what to extract vs. what to add. Extracted `dialogue-codex` §1–§9 (per-turn loop, claim classes, registration, target selection, scouting queries, status derivation, disposition enum, emission contract, terminal epilogue) as literal text. Added: T1–T6 adoption table, Risk F/G/J/K invariants table, TerminationCode enum (T1), scope-breach terminalization (Risk G). All additions marked inline with "*(Production addition — not in source)*" or "*(T1/Risk G addition — not in source)*" per the extraction discipline.

Key decision: kept the `<SHAKEDOWN_TURN_STATE>` sentinel name (inherited, for rubric compatibility per plan §8.3). Renamed §9 heading from "Terminal Epilogue" to "Terminalization" to accommodate additions — reviewer caught this; reverted to "Terminal Epilogue" for extraction fidelity.

Launched a background code-review agent for extraction fidelity verification. Agent found 4 findings:
1. Scope-breach row silently added to extracted table — fixed with addition marker.
2. Scope-Breach Terminalization subsection unlabeled — fixed with addition marker.
3. Epilogue schema `"converged": true` dropped `|false` — fixed to restore `true|false`.
4. §9 heading changed — fixed by reverting to "Terminal Epilogue."

**Phase 4 — Orchestrator authoring (task 3, ~15 min).**

Key design decision: self-contained body vs. runtime reference-doc loading. Three options considered:
- Load reference doc as a skill (would need to move to `skills/` or add skill frontmatter — contradicts plan's `references/` path).
- Read reference doc at runtime (fragile — path resolution differs between dev and prod contexts).
- Self-contained body authored from the reference doc, citing it for traceability.

Chose option 3. The reference doc is the normative authority (for humans and reviews); the orchestrator body is the executable implementation (for the agent). The plan says "cites" — citation is traceability, not a runtime dependency.

Authored 297-line body with five phases: inline scouting (N=5), dialogue initialization, per-turn loop (full claim handling, scouting, emission inline), terminalization (TerminationCode computation), production synthesis (artifact construction). Named constants table: `INLINE_SCOUTING_BUDGET=5`, `SCOPE_BREACH_THRESHOLD=3`, `DIALOGUE_TURN_BUDGET=10`, `MAX_EVIDENCE=15`, `MAX_SCOUT_ROUNDS=8`.

Launched a background code-review agent for acceptance criteria verification. All 9 criteria passed: N=5 named constant, §3.2 field match, no skills field, 13-field emission shape, T5 mode values, tools list match, TerminationCode lowercase literals, agent dispatch prohibition.

**Phase 5 — Hook matcher extension (task 5, ~5 min).**

Done in parallel while waiting for orchestrator review. Two-line edit: both `SubagentStart` and `SubagentStop` matchers changed from `"shakedown-dialogue"` to `"shakedown-dialogue|dialogue-orchestrator"`. Ran 566-test suite — green.

**Phase 6 — `/dialogue` skill authoring (task 4, ~10 min).**

Modeled after `shakedown-b1` steps 4–9 (preflight, seed, dispatch) but with key differences: zero-flag parser (single argument capture), coarse repo-root scope (`scope_directories=[<repo_root>]`), no metadata file or inspection template, synthesis surfacing instead of artifact staging. `allowed-tools: Bash, Read, Write, Agent` — no `codex.dialogue.*` tools (plan §8.4 bootstrap invariant). Ran bootstrap test and full suite — green.

**Phase 7 — User review and three-round fix cycle (~15 min).**

User performed manual review of all four surfaces. Three findings:

**Round 1 — Two findings:**
1. **P1: Terminal artifact return collision.** The orchestrator's terminal turn had to serve two incompatible consumers: the transcript (state block in `<SHAKEDOWN_TURN_STATE>`) and the parent skill (production synthesis as JSON). The emission contract forbids a second JSON fence. Fix: introduced `<PRODUCTION_SYNTHESIS>` sentinel for the synthesis artifact, placed in the same terminal message after the state block. Added explicit exception to §3.8's "no other JSON fence" rule for the terminal turn only.
2. **P3: Missing `mode_source`.** Summary line template omitted `mode_source`, contradicting addendum Decision 3's approved shape. Fix: added `mode_source: <mode_source>` to the summary line.

**Round 2 — One finding:**
1. **P1: Authority chain break.** The `<PRODUCTION_SYNTHESIS>` exception existed only in the orchestrator body — the reference doc still forbade it, so the orchestrator no longer executed the reference "verbatim." Fix: added the exception to the reference doc §8 (Sentinel Format) and updated the parse-failure condition, both marked as production additions.

**Round 3 — One finding:**
1. **P2: Overstated transcript behavior.** Docs claimed `<PRODUCTION_SYNTHESIS>` was "invisible to the transcript parser" and didn't "enter the transcript JSONL." But `SubagentStop` copies raw agent output verbatim — the sentinel IS in the transcript file. Fix: changed wording in reference doc and orchestrator to say rubric inspection "evaluates only `<SHAKEDOWN_TURN_STATE>` sentinels and ignores `<PRODUCTION_SYNTHESIS>` content," not that the content is absent.

After round 3: clean review — no findings.

**Phase 8 — Commit (~3 min).**

Staged all four files. Committed with conventional-commits message. Commit `05b7db3a` on `feature/t04-v1-implementation`. Not merged, not pushed.

## Decisions

### Decision 1: Self-contained orchestrator body over runtime reference-doc loading

**Choice:** The orchestrator body contains the full executable per-turn contract inline, citing the reference doc by path for traceability. The reference doc is the normative authority; the body is the implementation.

**Driver:** Claude Code's agent model has no mechanism to auto-load reference docs at runtime. The `skills` field loads skills by name, but the reference doc is at `references/`, not `skills/`. Reading the file at runtime via the Read tool is fragile — path resolution differs between dev (`packages/plugins/codex-collaboration/`) and prod (`~/.claude/plugins/cache/codex-collaboration/`).

**Alternatives considered:**
- **Load reference doc as a skill** — would require moving it to `skills/` or adding skill frontmatter. Rejected because it contradicts the plan's explicit `references/` path and mixes document types.
- **Read reference doc at runtime** — agent body says "read references/dialogue-turn-contract.md and execute it." Rejected because the path resolution problem makes this fragile across environments.
- **Create a wrapper skill** — thin skill at `skills/dialogue-turn-contract/SKILL.md` that says "read the reference doc." Rejected as an unnecessary indirection.

**Trade-offs accepted:** The per-turn contract is now in two places (reference doc and orchestrator body). They must stay in sync manually. Authoring discipline substitutes for a single-source mechanism.

**Confidence:** High (E2) — validated against Claude Code's skill-loading mechanism (shakedown-dialogue uses `skills` field; reference doc lacks skill frontmatter). Validated against path-resolution concern (dev vs prod contexts).

**Reversibility:** Medium — if a mechanism to load reference docs as skills is added to Claude Code, the body could be trimmed to "execute the reference doc" and the contract content removed. Would require a Claude Code feature change.

**Change trigger:** Claude Code adds a `references` field to agent frontmatter, or the plugin system supports auto-loading reference docs into agent context.

### Decision 2: `<PRODUCTION_SYNTHESIS>` sentinel for dual-consumer terminal turn

**Choice:** The terminal turn carries two sentinel-wrapped payloads: the state block in `<SHAKEDOWN_TURN_STATE>` (transcript consumer) and the production synthesis in `<PRODUCTION_SYNTHESIS>` (parent `/dialogue` skill consumer). An explicit exception in the emission contract permits this second sentinel on the terminal turn only.

**Driver:** User's P1 finding. The emission contract's "no other JSON fence" rule and Claude Code's agent mechanics (no tool calls → agent terminates → no next turn for Phase 5) meant the synthesis HAD to be in the same message as the terminal state block. Without a sentinel, the parent skill couldn't reliably extract the synthesis from the agent's output.

**Alternatives considered:**
- **Synthesis as prose, not JSON** — defeats the canonical-JSON discipline from addendum Decision 3.
- **Dummy tool call to get another turn** — orchestrator calls `codex.dialogue.read` to anchor a Phase 5 turn. Rejected as mechanically fragile (tool call might fail) and semantically dishonest.
- **Relax the parse-failure condition** — remove the "no other JSON fence" rule entirely. Rejected because the rule serves a real purpose (preventing accidental bare JSON that confuses transcript parsers).

**Trade-offs accepted:** The emission contract now has an exception, making it slightly more complex. The `<PRODUCTION_SYNTHESIS>` content is present in the raw transcript JSONL (SubagentStop copies verbatim), so rubric inspection must explicitly ignore non-state-block sentinels.

**Confidence:** High (E2) — validated against Claude Code agent mechanics (no tool calls → termination), validated against transcript contract (parse-failure conditions are per-turn; sentinel separation is deterministic).

**Reversibility:** Medium — removing the sentinel would require a different mechanism for the parent to receive the synthesis. The sentinel is now named in three surfaces (reference doc, orchestrator, `/dialogue` skill).

**Change trigger:** Claude Code adds multi-message agent returns (agent can produce a final message after the last tool-call-free message), eliminating the need for both payloads in one message.

### Decision 3: Coarse repo-root containment scope for `/dialogue` v1

**Choice:** `scope_directories=[<repo_root>]` in the seed. No file anchors. The orchestrator can Read/Grep/Glob anywhere in the repo.

**Driver:** Plan §5.1 specifies this explicitly. v1 objectives are open-ended (user provides arbitrary prose); the orchestrator can't know which directories are relevant before scouting. Narrow scope would cause false-positive breaches.

**Alternatives considered:**
- **Narrow scope per shakedown pattern** — `scope_directories` targeting specific package paths. Rejected because production objectives are unconstrained; any narrowing risks scope breaches on valid objectives.
- **User-specified scope via `--paths` flag** — would require flag vocabulary. Rejected per addendum Decision 2 (zero flags in v1).

**Trade-offs accepted:** The containment guard allows access to the entire repo, including potentially sensitive files. Plan §5.3 inherits T4-CT-05 explicitly — the production surface is safe for benchmark-corpus-like repos (curated, secret-free) but not for repos with tracked credentials.

**Confidence:** High (E2) — plan §5.1 specifies the choice; addendum Decision 2 closes the flag alternative.

**Reversibility:** High — changing `scope_directories` in the seed is a one-line edit in the `/dialogue` skill.

**Change trigger:** First `/dialogue` invocation where coarse scope causes a security concern, or when `--paths` flag is added post-v1.

### Decision 4: Orchestrator budget constants — DIALOGUE_TURN_BUDGET=10, MAX_EVIDENCE=15, MAX_SCOUT_ROUNDS=8

**Choice:** Three operational constants for the orchestrator that the plan and addendum didn't explicitly specify. Set at reasonable values for v1.

**Driver:** The reference doc references `max_evidence` and `max_scout_rounds` in skip conditions but doesn't define values (they're operator parameters). The orchestrator needs concrete values.

**Alternatives considered:**
- **Higher values (15 turns, 25 evidence, 12 rounds)** — more thorough but longer runs. Rejected as unnecessary for v1's "first production slice" scope.
- **Lower values (5 turns, 8 evidence, 4 rounds)** — faster but may truncate complex objectives. Rejected as too tight for open-ended production objectives.

**Trade-offs accepted:** These values may be too tight or too loose for some objectives. They're named constants — easy to tune post-v1.

**Confidence:** Medium (E1) — reasonable estimates without empirical production data. Will be calibrated by E2E verification (task 6).

**Reversibility:** High — single-line constant changes in the orchestrator body.

**Change trigger:** First `/dialogue` invocation where budget exhaustion truncates a productive dialogue (→ raise) or where the dialogue runs much longer than needed (→ lower).

### Decision 5: No runtime health check in `/dialogue` (unlike shakedown-b1)

**Choice:** The `/dialogue` skill does NOT call `codex.status` before dispatching the orchestrator.

**Driver:** Plan §6.1 doesn't include a health check in its 6-step lifecycle. The plan is the contract. If Codex is unavailable, the orchestrator's `codex.dialogue.start` will fail and the orchestrator terminates with `termination_code = "error"` — a clean failure mode.

**Alternatives considered:**
- **Mirror shakedown-b1's health check** — call `codex.status` first. Would give a clearer user-facing error. Rejected because it adds a tool to `allowed-tools` that the plan doesn't specify, and the orchestrator handles the failure gracefully.

**Trade-offs accepted:** User sees a less friendly error message on Codex unavailability (orchestrator error vs. explicit "Codex auth missing" message). Acceptable for v1.

**Confidence:** High (E2) — plan §6.1 is explicit about the lifecycle steps; the orchestrator's error-handling covers the failure mode.

**Reversibility:** High — adding `codex.status` is a 1-step addition to the skill.

**Change trigger:** User confusion from cryptic Codex-unavailability errors in production use.

### Decision 6: Addition-marking discipline for reference doc extractions

**Choice:** All additions to the reference doc (scope-breach terminalization, `<PRODUCTION_SYNTHESIS>` sentinel exception, TerminationCode enum) are marked inline with "*(Production addition — not in source)*" or "*(T1/Risk G addition)*" annotations. The preamble enumerates all additions.

**Driver:** Extraction fidelity reviewer found that scope-breach rows were inserted into the extracted "When to Terminate" table without visual distinction — a reader would treat them as carrying equal "extracted from dialogue-codex" authority. Maintaining trust in the extraction requires distinguishing extracted content from additions.

**Alternatives considered:**
- **Separate additions section** — all additions in a dedicated section after the extracted content. Rejected because it splits terminalization conditions across two locations.
- **No marking** — trust readers to check the source. Rejected because the extraction discipline is a verifiable claim only if additions are distinguishable.

**Trade-offs accepted:** Inline markers add visual noise. The preamble's additions list is a second thing to maintain.

**Confidence:** High (E2) — validated by the reviewer's finding that unmarked additions break the extraction discipline's verification path.

**Reversibility:** High — markers are cosmetic. Removing them doesn't change behavior.

**Change trigger:** Reference-doc unification (remaining-T-04) eliminates the extraction discipline entirely — the reference becomes the primary source, not an extraction.

## Changes

### `packages/plugins/codex-collaboration/references/dialogue-turn-contract.md` (NEW, 406 lines)

**Purpose:** Production-local authoritative turn contract for the per-turn verification loop. Extracted from `dialogue-codex/SKILL.md` with additions.

**Approach:** Literal extraction of §1–§9 (per-turn loop, claim classes, registration, target selection, scouting queries, status derivation, disposition enum, emission contract, terminal epilogue). Added: T1–T6 adoption table, Risk F/G/J/K invariants, TerminationCode enum, scope-breach terminalization, `<PRODUCTION_SYNTHESIS>` terminal sentinel exception. All additions marked inline.

**Key authoring detail:** The `SHAKEDOWN_TURN_STATE` sentinel name is preserved for rubric compatibility (plan §8.3). Post-v1 cleanup may rename it. The emission contract's parse-failure condition exempts `<PRODUCTION_SYNTHESIS>` on the terminal turn only.

**Key authoring detail:** The extraction discipline means future edits to per-turn semantics must land in BOTH `dialogue-codex/SKILL.md` and this reference doc in the same commit (plan §9.3 risk), until remaining-T-04 unification factors `dialogue-codex` to an adapter.

### `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md` (NEW, 313 lines)

**Purpose:** Production dialogue orchestrator — self-contained subagent that performs inline scouting, runs the per-turn verification loop, and emits a production synthesis artifact.

**Approach:** Five-phase procedure (inline scouting → dialogue init → per-turn loop → terminalization → production synthesis). Per-turn contract is implemented inline (authored from the reference doc), not loaded at runtime. Cites the reference doc by path for traceability.

**Key authoring detail:** Named constants table at the top: `INLINE_SCOUTING_BUDGET=5` (addendum Decision 1), `SCOPE_BREACH_THRESHOLD=3` (Risk G), `DIALOGUE_TURN_BUDGET=10`, `MAX_EVIDENCE=15`, `MAX_SCOUT_ROUNDS=8`. All are single-line changes to tune.

**Key authoring detail:** The terminal turn carries two sentinel-wrapped payloads: `<SHAKEDOWN_TURN_STATE>` (state block for transcript) and `<PRODUCTION_SYNTHESIS>` (synthesis artifact for parent skill). The §3.8 emission contract has an explicit exception for this.

**Key authoring detail:** Tools list is identical to `shakedown-dialogue.md` — Read, Grep, Glob + three `codex.dialogue.*` MCP tools. No Bash/Write/Edit/Agent. The `skills` field is absent (no skill loading — body is self-contained).

### `packages/plugins/codex-collaboration/skills/dialogue/SKILL.md` (NEW, 150 lines)

**Purpose:** User-invocable `/dialogue` skill — the production entry point for Codex dialogues.

**Approach:** 8-step procedure modeled after `shakedown-b1` steps 4–9 with production-specific differences. Zero-flag parser captures the full argument string as `<objective>`. Preflight cleanup via `clean_stale_shakedown.py`. Shared-namespace single-run check. Parent-owned seed write with `scope_directories=[<repo_root>]`. Orchestrator dispatch via Agent tool. Synthesis surfacing with Markdown view + canonical JSON appendix per addendum Decision 3.

**Key authoring detail:** `allowed-tools: Bash, Read, Write, Agent` — does NOT include any `codex.dialogue.*` MCP tools. The orchestrator owns those. This preserves `test_bootstrap.py::test_no_user_invocable_dialogue_skill_exists` unchanged (plan §8.4).

**Key authoring detail:** Synthesis extraction uses `<PRODUCTION_SYNTHESIS>` sentinel search, not raw JSON parsing. Summary line includes all Decision 3 fields: `termination_code`, `converged`, `turn_count/turn_budget`, `mode`, `mode_source`.

**Key authoring detail:** No `codex.status` health check (unlike shakedown-b1). Plan §6.1 doesn't specify one; Codex unavailability surfaces as `termination_code = "error"` from the orchestrator.

### `packages/plugins/codex-collaboration/hooks/hooks.json` (MODIFIED, +2 insertions, -2 deletions)

**Purpose:** Extend SubagentStart and SubagentStop matchers to fire for the production orchestrator.

**Approach:** Changed both matchers from `"shakedown-dialogue"` to `"shakedown-dialogue|dialogue-orchestrator"`. Regex alternation — the simplest form. Plan §7.1 allowed either regex or two-entry form.

**Key authoring detail:** Without this edit, the orchestrator runs completely uncontained — no scope file materialized, no transcript captured, no containment guard active. This is the "silent defeat" risk (plan §9.1). Plan §8.3 includes an explicit verification check for hook firing.

## Codebase Knowledge

### Files read this session

| File | Range | Purpose | Key finding |
|---|---|---|---|
| `skills/dialogue-codex/SKILL.md` | full (455 lines) | Extraction source | §1–§9 contain the per-turn contract; §10–§11 are exemplars (not extracted); tools table has MCP names (not extracted) |
| `agents/shakedown-dialogue.md` | full (18 lines) | Agent body precedent | 1-line body + `skills: dialogue-codex` loads the skill. Production can't replicate this because reference doc isn't a skill. |
| `skills/shakedown-b1/SKILL.md` | full (212 lines) | Preflight/seed/dispatch precedent | Steps 4–9 (stale cleanup → single-run check → seed write → spawn → transcript verify → capture) are the template for `/dialogue` steps 4–7 |
| `tests/test_bootstrap.py` | lines 256–283 | Bootstrap test verification | Test checks that no user-invocable skill's `allowed-tools` intersects `_DIALOGUE_MCP_TOOLS`. `/dialogue` passes because its `allowed-tools` has no dialogue MCP tools. |
| `hooks/hooks.json` | full (57 lines) | Matcher extension target | Lines 15 and 26 are the two matchers. PreToolUse hooks (lines 36–53) are unchanged. |
| `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md` | full (637 lines) | Plan re-read | §3.2 (synthesis artifact schema), §4 (ownership table), §6.1 (run model), §6.2 (inline scouting), §7.1 (hook matcher detail), §8.3 (verification checks), §8.4 (boundary invariants), §9.1 (silent defeat risk) |
| `docs/plans/2026-04-14-t04-v1-authoring-decisions.md` | full (127 lines) | Addendum re-read | Decision 1 (N=5), Decision 2 (zero flags), Decision 3 (hybrid serialization), Decision 4 (crash recovery deferred) |

### Architecture: production dialogue runtime path

| Step | Actor | What happens | File |
|---|---|---|---|
| 1 | User | `/dialogue <objective>` | `skills/dialogue/SKILL.md` |
| 2 | `/dialogue` skill | Preflight, seed write, dispatch | Same |
| 3 | Claude Code | Spawns `dialogue-orchestrator` | — |
| 4 | SubagentStart hook | Reads seed, writes scope, unlinks seed | `scripts/containment_lifecycle.py` |
| 5 | Orchestrator | Inline scouting (≤5 Read/Grep/Glob) | `agents/dialogue-orchestrator.md` |
| 6 | Orchestrator | `codex.dialogue.start` + first `reply` | Same |
| 7 | Orchestrator | Per-turn loop (claim extraction, scouting, emission) | Same, per `references/dialogue-turn-contract.md` |
| 8 | Orchestrator | Terminal state block + `<PRODUCTION_SYNTHESIS>` | Same |
| 9 | SubagentStop hook | Copies transcript to JSONL, writes `.done` | `scripts/containment_lifecycle.py` |
| 10 | `/dialogue` skill | Extracts `<PRODUCTION_SYNTHESIS>`, surfaces to user | `skills/dialogue/SKILL.md` |

### Key invariants verified

| Invariant | Verified how | Result |
|---|---|---|
| `dialogue-codex/SKILL.md` byte-for-byte unchanged | `git diff` (zero output) | Pass |
| `shakedown-b1` and `shakedown-dialogue` byte-for-byte unchanged | `git diff` (zero output) | Pass |
| Bootstrap test passes with new `/dialogue` skill | `uv run --package codex-collaboration pytest` (566 pass) | Pass |
| `/dialogue` `allowed-tools` excludes `codex.dialogue.*` | Manual inspection + test | Pass |
| Hook matchers fire for both agents | Regex `shakedown-dialogue\|dialogue-orchestrator` | Structural (E2E verification pending) |

### Dual-sentinel terminal emission pattern

The terminal turn of the orchestrator carries two sentinel-wrapped payloads:

```
[claim processing prose]

<SHAKEDOWN_TURN_STATE>
```json
{ terminal state block with epilogue }
```
</SHAKEDOWN_TURN_STATE>

[post-state-block prose]

<PRODUCTION_SYNTHESIS>
```json
{ production synthesis artifact }
```
</PRODUCTION_SYNTHESIS>
```

- Transcript consumer (rubric, SubagentStop): evaluates only `<SHAKEDOWN_TURN_STATE>` sentinels
- Parent consumer (`/dialogue` skill): extracts `<PRODUCTION_SYNTHESIS>` sentinel
- `<PRODUCTION_SYNTHESIS>` content IS present in raw transcript JSONL (SubagentStop copies verbatim) — rubric inspection ignores it

## Context

### Mental model for this session

This session executed the **"plan → addendum → implementation"** pipeline. The plan (frozen) defines what to build. The addendum (frozen) resolves authoring-time questions. The implementation (this session) authors the four surfaces faithful to both contracts.

The key tension was between **extraction fidelity** (the reference doc must preserve dialogue-codex's per-turn semantics literally) and **production additions** (the reference doc must also carry T1–T6 semantics, risk invariants, and the production synthesis sentinel that dialogue-codex doesn't have). The resolution was inline addition markers — clearly distinguishing what's extracted from what's added, so the "zero behavioral edits" claim is verifiable.

The second key tension was the **dual-consumer terminal turn** — the emission contract serves the transcript/rubric consumer, while Phase 5 serves the parent/user consumer. These compete for the same agent message (Claude Code agents terminate after a message with no tool calls). The `<PRODUCTION_SYNTHESIS>` sentinel resolves this by giving each consumer its own extraction target in the same message.

### Position in the T-04 v1 packet arc

| Session | Role | Artifact |
|---|---|---|
| 2026-04-13 18:50 | Gap analysis + turn semantics closure | T-20260410-01/02 closed |
| 2026-04-13 19:45 | v1 scoping plan first draft | 518 lines |
| 2026-04-13 22:09 | v1 scoping plan rewrite | 591 lines (three-round re-minimization) |
| 2026-04-13 23:12 | v1 scoping plan approval + merge + push | 632 lines, `main@73f8c9c1` |
| 2026-04-14 12:55 | §10 authoring decisions resolved | Addendum committed, `feature/t04-v1-implementation@30edf38a` |
| **2026-04-14 16:30 (this)** | **Four production surfaces authored** | **Committed `feature/t04-v1-implementation@05b7db3a`** |
| Next | E2E verification + rubric inspection | Live `/dialogue` invocation |

### Environment state

- **Branch:** `feature/t04-v1-implementation` from `main@30edf38a`. Not pushed.
- **Commit:** `05b7db3a` on the feature branch. Not merged.
- **Working tree:** clean.
- **Main:** at `30edf38a` (addendum commit merged earlier this session).
- **Task tracking:** 8 tasks, tasks 1–5 completed, tasks 6–8 pending (verification).

## Learnings

### Dual-sentinel pattern resolves single-message dual-consumer conflicts

**Mechanism.** When a Claude Code agent's final message must serve two consumers that expect different content (e.g., transcript parser expects one JSON structure, parent skill expects another), wrapping each payload in its own sentinel gives each consumer a deterministic extraction target. The agent terminates after the message (no tool calls → termination), so both payloads must be in the same message.

**Evidence.** User's P1 finding identified the collision. Three rounds of review refined the fix: (1) sentinel introduction, (2) authority-chain alignment, (3) transcript-behavior accuracy.

**Implication.** Any future orchestrator or contained agent that needs to return a result to its parent while also emitting contract-governed state blocks should use this pattern. The sentinel name convention (content-descriptive, uppercase, angle-bracketed) should be consistent across agents.

**Watch for.** Rubric inspection must explicitly ignore non-state-block sentinels. If a new rubric is written for production runs, it should be aware of `<PRODUCTION_SYNTHESIS>`.

### Self-contained agent bodies are more reliable than runtime reference loading

**Mechanism.** Claude Code's `skills` field loads skills by name resolution within the plugin. Reference docs don't participate in this mechanism. Reading a file at runtime requires the agent to know the absolute path, which differs between dev (`packages/plugins/...`) and prod (`~/.claude/plugins/cache/...`). A self-contained body avoids this path-resolution fragility.

**Evidence.** Explored three alternatives (skill loading, runtime reading, wrapper skill). All required either moving the reference doc, adding fragile path resolution, or introducing unnecessary indirection. The shakedown agent avoids the problem entirely via `skills: dialogue-codex` — but that mechanism isn't available for reference docs.

**Implication.** When an agent needs to follow a reference document's contract, author the executable instructions inline in the body and cite the reference for traceability. The reference doc's role is normative authority (for reviews and audits), not runtime loading.

**Watch for.** Keeping the orchestrator body and reference doc in sync. Any hotfix to per-turn semantics must land in both surfaces. Remaining-T-04 unification eliminates this by factoring `dialogue-codex` to an adapter over the reference.

### Extraction addition markers are a necessary trust mechanism

**Mechanism.** When extracting a behavioral contract from one document into another, any additions to the extracted text must be visually distinguishable from the original. Without markers, a reader executing the contract can't tell which rules are proven (tested by the source's existing test suite) and which are new (untested additions).

**Evidence.** Background reviewer found that the scope-breach row was inserted between two verbatim-extracted rows in the "When to Terminate" table with no distinction. A reader would treat all rows as having equal "extracted from source" authority. Fixing with inline markers restored the verifiable extraction claim.

**Implication.** Future extraction-based documents in this repo should use the same inline-marking convention. The preamble should enumerate all additions.

**Watch for.** Over-marking (marking things that are formatting changes, not semantic additions) dilutes the signal. Only mark semantic additions — things that change behavior.

### Claude Code agents terminate after a tool-call-free message

**Mechanism.** In Claude Code's agent model, an agent produces assistant messages. If a message contains tool calls, the tools execute and the agent gets another turn. If a message has NO tool calls, the agent terminates and its output is returned to the parent.

**Evidence.** This is why the production synthesis couldn't be in a separate Phase 5 message after the terminal state block — the terminal state block has no tool calls (no follow-up, terminal), so the agent terminates. Phase 5 must be in the same message.

**Implication.** Any agent phase that must run AFTER a tool-call-free message must be in the same message. Alternatively, the prior message can include a "dummy" tool call to keep the agent alive — but this is semantically dishonest and fragile.

**Watch for.** Future agents where "final processing" needs to happen after the main loop terminates. Design the loop to include the final processing in the terminal iteration's message, not as a separate step.

## Next Steps

### 1. End-to-end verification per plan §8.2 (task 6)

**Dependencies:** All authoring tasks complete. Requires a live Codex endpoint.

**What to do:**
1. Invoke `/dialogue` with a representative objective against the codebase.
2. Verify SubagentStart fires (scope file created).
3. Verify containment guard allows on-scope Read/Grep/Glob.
4. Verify orchestrator completes the loop and emits terminal state block + production synthesis.
5. Verify SubagentStop fires (transcript written to `transcript-<run_id>.jsonl`).
6. Verify `/dialogue` surfaces the synthesis with Markdown view + JSON appendix.

**What to check per §8.3:**
- Hook firing for `dialogue-orchestrator`
- Transcript state-block fields match 13-field shape exactly
- First emitted state block is `turn: 2`
- Production synthesis contains `mode="agent_local"`, `mode_source=null`
- Termination yielded a TerminationCode; `converged` is its projection
- No shakedown surface invoked

**Potential obstacles:**
- Codex endpoint availability. If Codex is unavailable, the orchestrator should terminate with `termination_code = "error"` — this is itself a verifiable behavior.
- Long running time. A 10-turn dialogue with scouting at each turn may take several minutes.

### 2. 14-item rubric inspection against the transcript (task 7)

**Dependencies:** E2E verification produces a transcript.

**What to do:** Apply the 14-item rubric from `shakedown-b1/SKILL.md:153-174` to the production transcript. All 14 items must pass.

**Note:** The rubric is used as a "prose inspection tool" (plan §8.1), not as a production user flow. The inspector should be aware that the raw transcript JSONL contains `<PRODUCTION_SYNTHESIS>` content that is NOT a state block — ignore it during inspection.

### 3. Merge and push authorization

**Dependencies:** E2E verification and rubric pass.

**Decision pending:** Whether to merge `feature/t04-v1-implementation` to `main` before or after verification. Prior session's pattern: merge after authoring, before verification. But verification is the acceptance gate — merging before it passes creates a window where `main` has unverified surfaces.

**Options:**
- Merge now (surfaces are committed, tests green, but E2E not done)
- Hold merge until E2E + rubric pass
- User decides

## In Progress

**Clean stopping point — four surfaces authored, committed, and review-clean. No work in flight.**

- **Approach:** Plan §12 steps 1–4 executed sequentially, with parallel hooks.json edit during orchestrator review. Three-round user review cycle resolved all findings.
- **State:** complete for the authoring sub-phase. Commit `05b7db3a` on `feature/t04-v1-implementation`; working tree clean. 566 tests pass.
- **Working:** all four surfaces pass static review. Authority chain is consistent across reference doc, orchestrator, and `/dialogue` skill. Emission contract coherent with dual-sentinel pattern.
- **Not working:** nothing broken. E2E verification not yet attempted.
- **Open question:** merge/push timing relative to verification.
- **Next action:** User decides — E2E verification (requires live Codex), or merge/push first, or pause.

## Open Questions

### 1. Merge and push timing

**Context:** Commit `05b7db3a` is on `feature/t04-v1-implementation` only. User's pattern from prior sessions: commit, merge, and push are separately authorized steps.

**Impact:** Low — a feature branch commit is harmless. The question is whether verification (tasks 6–7) should happen before or after merge.

**Options:**
- Merge now, verify on `main`.
- Verify on the feature branch, merge after pass.
- User decides.

### 2. Orchestrator budget constants need empirical calibration

**Context:** `DIALOGUE_TURN_BUDGET=10`, `MAX_EVIDENCE=15`, `MAX_SCOUT_ROUNDS=8` were chosen as reasonable defaults without production data. They may be too tight (truncating productive dialogues) or too loose (allowing unnecessarily long runs).

**Impact:** Low for v1 — constants are named and easily tunable. Medium for post-v1 if defaults become de facto standards.

**Decision pending until:** First few `/dialogue` invocations provide empirical data on typical turn counts, evidence counts, and scout rounds.

## Risks

### 1. Reference doc / dialogue-codex drift during v1

**Impact:** Plan §9.3 risk. If either `dialogue-codex/SKILL.md` or `references/dialogue-turn-contract.md` is edited without mirroring the other, shakedown and production run against different per-turn contracts.

**Mitigation:** Zero-behavioral-edits discipline. Any hotfix must land in both surfaces in the same commit. Remaining-T-04 closure eliminates the risk structurally (§2.2).

### 2. Orchestrator body / reference doc drift

**Impact:** The orchestrator body contains the per-turn contract inline (self-contained body decision). If the reference doc is updated without updating the orchestrator body, they diverge.

**Mitigation:** The reference doc is cited in the orchestrator's preamble. Any edit to the reference doc should trigger a corresponding orchestrator body edit. This is authoring discipline, not automated enforcement.

### 3. `<PRODUCTION_SYNTHESIS>` in raw transcript may confuse future tooling

**Impact:** The raw transcript JSONL contains `<PRODUCTION_SYNTHESIS>` content that is NOT a state block. Future tooling (e.g., automated rubric checks, transcript analyzers) that naively parses all JSON fences will misprocess this content.

**Mitigation:** The reference doc and orchestrator body both document this. Rubric inspection evaluates only `<SHAKEDOWN_TURN_STATE>` sentinels. Any future automated tooling should be sentinel-aware.

### 4. Budget constants may be miscalibrated

**Impact:** `DIALOGUE_TURN_BUDGET=10`, `MAX_EVIDENCE=15`, `MAX_SCOUT_ROUNDS=8` are untested defaults. Too tight → productive dialogues truncated. Too loose → unnecessary token cost.

**Mitigation:** Named constants, single-line changes. E2E verification (task 6) will provide first data point.

## References

### This session's commit

- `05b7db3a` on `feature/t04-v1-implementation` — feat(codex-collaboration): author T-04 v1 production dialogue surfaces

### Files authored this session

- `packages/plugins/codex-collaboration/references/dialogue-turn-contract.md` (NEW, 406 lines)
- `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md` (NEW, 313 lines)
- `packages/plugins/codex-collaboration/skills/dialogue/SKILL.md` (NEW, 150 lines)
- `packages/plugins/codex-collaboration/hooks/hooks.json` (MODIFIED, 2 insertions, 2 deletions)

### Prior authority

- Parent plan: `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`
- Addendum: `docs/plans/2026-04-14-t04-v1-authoring-decisions.md`
- Supersession ticket: `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md`

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-14_12-55_t04-v1-section-10-authoring-decisions-resolved-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-13_23-12_t04-v1-plan-approved-merged-pushed-implementation-unblocked.md`

### Code surfaces (existing, relied on unchanged)

- `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md` (extraction source — byte-for-byte unchanged)
- `packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md` (preflight precedent + rubric source — unchanged)
- `packages/plugins/codex-collaboration/agents/shakedown-dialogue.md` (agent body precedent — unchanged)
- `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py` (lifecycle hooks — unchanged)
- `packages/plugins/codex-collaboration/scripts/containment_guard.py` (PreToolUse guard — unchanged)
- `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py` (preflight cleanup — unchanged)
- `packages/plugins/codex-collaboration/tests/test_bootstrap.py` (boundary gate — unchanged, passes)

## Gotchas

### Self-contained body means dual-maintenance for per-turn contract

**Symptom:** Future-Claude edits the reference doc but forgets to update the orchestrator body (or vice versa).

**Root cause:** Decision 1 (self-contained body) means the per-turn contract is in two places. This is a deliberate trade-off for reliability over single-source elegance.

**Prevention:** The orchestrator preamble cites the reference doc by path. Any edit to the reference doc should prompt checking the orchestrator. Remaining-T-04 unification will eventually make the reference doc the sole authority.

### `<PRODUCTION_SYNTHESIS>` is in the raw transcript — don't treat it as a state block

**Symptom:** Future tooling parses all JSON fences in the transcript and hits an unexpected structure.

**Root cause:** SubagentStop copies the raw agent output verbatim. The `<PRODUCTION_SYNTHESIS>` content is present alongside `<SHAKEDOWN_TURN_STATE>` blocks.

**Prevention:** Documented in both the reference doc (§8 Sentinel Format) and the orchestrator body (§3.8). Rubric inspection and future tooling should be sentinel-aware.

### Feature branch has addendum + surfaces — two commits, one merge

**Symptom:** Someone reviews `feature/t04-v1-implementation` and sees two commits (`30edf38a` addendum + `05b7db3a` surfaces) that need separate context to understand.

**Root cause:** The addendum was merged to `main` earlier this session, then a new `feature/t04-v1-implementation` was created from `main`. The addendum commit is in `main` already; only the surfaces commit (`05b7db3a`) is unique to the feature branch.

**Prevention:** The feature branch has 1 commit ahead of `main` (only `05b7db3a`). Merging is a clean fast-forward.

### No health check means cryptic error on Codex unavailability

**Symptom:** User runs `/dialogue`, orchestrator fails at `codex.dialogue.start`, surfaces `termination_code = "error"` with a tool-error message instead of a friendly "Codex not available" message.

**Root cause:** Decision 5 (no health check). Plan §6.1 doesn't specify one.

**Prevention:** User can check Codex availability manually (`/codex-status`). Post-v1, adding a `codex.status` preflight check would improve UX.

## Conversation Highlights

### User's merge-first directive

User's first action after loading the handoff: "First, merge the addendum commit branch." Then `/merge-branch` skill invocation. Pattern: user treats merge as a discrete step, separately authorized from commit and push. Consistent with prior sessions' commit-merge-push separation pattern.

### User's "continue with the plan order" directive

After task 3 (orchestrator) completed, user said: "continue with the plan order." Single directive, no elaboration needed — trusting the task list to sequence the work. Minimal-word, maximum-information style.

### User's three-round review cycle

User performed manual review of all four surfaces after authoring. Three rounds, each surfacing one or two findings. Findings were presented as structured `::code-comment` blocks with priority, confidence, file paths, and line ranges. Review style: precise, evidence-backed, with explicit P1/P2/P3 priority.

Round 1 findings were architectural (terminal output collision, missing field). Round 2 finding was authority-chain consistency. Round 3 finding was factual accuracy of transcript behavior claims. Each round was narrower than the previous — converging on clean.

### User's review annotation format

User used `::code-comment{title="..." body="..." file="..." start=N end=N priority=N confidence=N}` format — structured annotations with file, line range, priority, and confidence. This is a consistent pattern across sessions.

## User Preferences

### Structured review annotations with priority and confidence

**Verbatim format:** `::code-comment{title="[P1] ..." body="..." file="..." start=N end=N priority=1 confidence=0.95}`

**Pattern:** User provides findings as structured annotations, not prose. Each has a title with priority prefix, body with rationale, file path, line range, and confidence score. This format is machine-parseable and prioritized.

### Three-round convergent review pattern

**Pattern observed:** User reviews, surfaces findings, waits for fixes, then re-reviews. Each round is narrower. Round 3's finding was a factual accuracy issue — the user checks whether claims about runtime behavior match the actual code (`containment_lifecycle.py` copies verbatim → the claim that content doesn't enter the transcript was wrong).

### Merge before verification is acceptable for doc-only changes

**Pattern:** User directed merging the addendum commit (a doc-only change) before starting implementation. But the implementation commit is held on the feature branch pending verification. Pattern: doc-only changes can merge eagerly; code-like changes (surfaces that affect runtime behavior) wait for verification.

### Trust task list sequencing

**Verbatim:** "continue with the plan order"

**Pattern:** User trusts the task list and plan §12 ordering. Doesn't re-specify what to do next — just says "continue." Minimal direction when the path is clear.
