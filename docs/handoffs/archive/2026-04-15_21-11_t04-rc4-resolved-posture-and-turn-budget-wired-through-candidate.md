---
date: 2026-04-15
time: "21:11"
created_at: "2026-04-16T01:11:00Z"
session_id: 9e4a5925-c98d-461e-8a07-d9bc80a0cc94
resumed_from: docs/handoffs/archive/2026-04-15_19-30_t04-benchmark-v1-scaffold-reviewed-and-committed.md
project: claude-code-tool-dev
branch: main
commit: afa55eac
title: "T-04 RC4 resolved — posture and turn-budget wired through candidate system"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/profiles.py
  - packages/plugins/codex-collaboration/server/dialogue.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/consultation_safety.py
  - packages/plugins/codex-collaboration/skills/dialogue/SKILL.md
  - packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md
  - packages/plugins/codex-collaboration/tests/test_profiles.py
  - packages/plugins/codex-collaboration/tests/test_dialogue_profiles.py
  - packages/plugins/codex-collaboration/tests/test_mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_consultation_safety.py
  - docs/benchmarks/dialogue-supersession/v1/operator-procedure.md
  - docs/benchmarks/dialogue-supersession/v1/manifest.json
  - docs/benchmarks/dialogue-supersession/v1/summary.md
---

# T-04 RC4 Resolved — Posture and Turn-Budget Wired Through Candidate System

## Goal

Resolve the RC4 benchmark blocker by implementing posture and turn-budget control surfaces in the candidate dialogue system (`codex-collaboration`), enabling scored benchmark execution.

**Trigger.** Resumed from `2026-04-15_19-30` handoff. The benchmark v1 scaffold was committed and reviewed through 7 adversarial rounds, but two scoring blockers remained: (1) the candidate had no posture control, and (2) the orchestrator hardcoded `DIALOGUE_TURN_BUDGET = 10`. The benchmark contract's run condition 4 requires "Same posture and turn budget from the fixed corpus" — unconditional (no host caveat). Without these controls, scored execution was impossible.

**Stakes.** AC-5 requires "The benchmark contract is executed on the fixed corpus." RC4 was the last blocker between the scaffold and scored execution. Resolving it unblocks the entire benchmark execution path (AC-5 through AC-7).

**Success criteria achieved this session:**

1. Candidate skill accepts `-p` (posture) and `-n` (turn budget) flags.
2. Values wired through MCP schema, controller, profile resolver, and safety policy.
3. Orchestrator parses dispatched metadata, uses parsed budget for loop termination, and applies posture-aware follow-up framing.
4. All 586 existing tests pass with 30 new tests added.
5. Operator procedure, manifest, and summary artifacts updated from BLOCKED to RESOLVED.
6. Feature branch merged to main.

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
| **2026-04-15 21:11 (this)** | **RC4 resolved — posture and turn-budget wired through** | **`52a968e9`, `e2057f2b`, `c36b56c7`, `afa55eac` on `main`** |
| Next | Scored benchmark execution (AC-5) | |

## Session Narrative

**Phase 1 — Analysis and discovery of dormant plumbing (~20 min).**

Loaded the `2026-04-15_19-30` handoff. The prior session's next step was "Resolve RC4 blockers." User directed: implementation, not contract amendment. Started by reading the candidate skill (`SKILL.md`, 330 lines), the orchestrator (`dialogue-orchestrator.md`, 330 lines), the baseline skill (`cross-model/skills/dialogue/SKILL.md`, 524 lines), and the baseline orchestrator (`codex-dialogue.md`, 522 lines) to understand the control surface gap.

Initial analysis framed posture as something the candidate needed "invented from scratch." User corrected this with a detailed read showing the candidate runtime already has dormant posture plumbing: `mcp_server.py:45` accepts `profile` on `codex.dialogue.start`, `dialogue.py:112-133` resolves posture/effort/budget from profiles and stores on the handle, `dialogue.py:368` reads `handle.resolved_posture` and passes to `prompt_builder.py:40-44`, which injects `"Adopt a {posture} posture for this advisory turn."` on every Codex turn. Tests at `test_dialogue_profiles.py:78-95` pin this behavior. The gap was narrower than initially assessed — wiring, not capability.

User also identified that the profile resolver at `profiles.py:78-86` already accepts `explicit_posture` and `explicit_turn_budget` kwargs but the MCP schema and dispatch don't expose them. And that the consultation profiles YAML covers adversarial/6 and comparative/8 but no evaluative/6 preset — explicit flags are cleaner than benchmark-only profile names.

**Phase 2 — Design alignment (~30 min).**

Collaborative design discussion converged on 7 discrete changes across 5 files plus tests. Three challenge points were raised and resolved:

1. **Resolver path:** Option (a) — expand the resolution gate in `dialogue.py` to enter `resolve_profile()` when any of profile/posture/budget is present. Keeps resolver as single validation authority. User added: move the 1-15 budget upper bound into the resolver too, not just the skill parser.

2. **Posture depth:** Compact patterns table in the orchestrator, but posture must influence actual Step 6 question framing (priorities 1-4), not just the last-resort fallback (priority 5). Otherwise posture is barely observable during benchmark adjudication.

3. **`DialogueStartResult` echo:** Don't widen — orchestrator sends explicit values, controller validates or rejects. No ambiguity about what was resolved.

Two hidden seams were identified by the user: (a) dispatch prompt parsing — new metadata must go after `Repository root:`/`Scope directories:` to avoid corrupting objective extraction, and (b) three competing default numbers (baseline 8, resolver 6, orchestrator 10) need a single authority — resolver wins, skill always dispatches explicit values, orchestrator constant gets deleted.

**Phase 3 — Implementation plan review (~10 min).**

User drafted a 7-step implementation order with explicit ordering rationale: backend first (prevents skill from advertising unsupported fields), within the instruction patch update skill before orchestrator (old orchestrator tolerates extra metadata; new orchestrator should not be exposed to old dispatch shape). Three flags were added: steps 4+5 must land atomically, shakedown-b1 also calls `codex.dialogue.start` (additive change is safe), and the Phase 5 artifact projection at orchestrator line 310 is a second `DIALOGUE_TURN_BUDGET` reference easy to miss.

**Phase 4 — Implementation (~30 min).**

Backend patch first: `profiles.py` (budget bounds 1-15), `dialogue.py` (expanded start() signature and resolution gate), `mcp_server.py` (schema + dispatch), `consultation_safety.py` (expected_fields). All four test files updated. 95 backend tests passing, 586 full suite passing.

Instruction patch second: skill (`-p`/`-n` flags, argument-hint frontmatter, always-explicit dispatch, metadata after `Repository root:`), then orchestrator (Dispatch Parameters section, parsed budget for loop termination and Budget Exhaustion Window, Step 6 posture-aware framing table, `DIALOGUE_TURN_BUDGET` deleted from both lines 27 and 310).

**Phase 5 — Review and P1/P2 fixes (~10 min).**

User reviewed and found two issues:

P1 (critical): Parsed turn budget was cosmetic — it was parsed and echoed into the synthesis artifact but never tied to Phase 3/4 loop termination. The old constant was implicitly referenced by "budget exhaustion" but removing it without adding an explicit rule broke the loop constraint. Fixed by adding a step 4 turn budget check and an explicit trigger definition in the Budget Exhaustion Window.

P2 (design): Bare `codex.dialogue.start` callers (shakedown-b1) still bypass resolution. Documented as intentional — bare callers own their own defaults. Pushing resolver defaults into shakedown handles would inject posture instructions into turns that have their own posture management.

**Phase 6 — Merge and artifact alignment (~10 min).**

Operator procedure Scoring Prerequisites updated from BLOCKING to RESOLVED. Run Condition Status table updated (posture and turn budget → Matched). Feature branch merged to main (fast-forward, 4 commits). Final consistency pass found stale "Blocked" references in `manifest.json` and `summary.md` — fixed and committed.

## Decisions

### Decision 1: Implementation over contract amendment for RC4

**Choice:** Add `-p` and `-n` flags to the candidate system rather than amending run condition 4 to allow documented asymmetry.

**Driver:** User directed: "My decision for RC4 is implementation, not amendment."

**Alternatives considered:**
- **Contract amendment** — change RC4 to allow documented posture/turn-budget asymmetry with mandatory recording of effective values. Rejected because user wanted to keep the contract clean — amendment weakens the comparison's matched-conditions story.

**Trade-offs accepted:** More implementation work (10 files, 397 lines) vs. a one-paragraph contract amendment. The implementation path also benefits normal `/dialogue` use beyond the benchmark.

**Confidence:** High (E2) — grounded in user directive and verified by complete implementation with 586 passing tests.

**Reversibility:** N/A — implementation is strictly additive. The contract remains unmodified.

**Change trigger:** None — this was a direction decision, not a trade-off that could flip.

### Decision 2: Route everything through `resolve_profile()` as single validation authority

**Choice:** Expand the resolution gate in `dialogue.py:start()` to fire when any of `profile_name`, `explicit_posture`, or `explicit_turn_budget` is present. Resolver handles precedence, validation, and defaults.

**Driver:** User said the precedence rule and type/enum validation already exist in `profiles.py:78-86`. Bypassing the resolver for the explicit-only path would duplicate validation logic. Also: `codex.dialogue.start` is a real MCP surface — if validation only lives in the skill, direct tool callers can inject bad values.

**Alternatives considered:**
- **Option (b):** Skip `resolve_profile()` for explicit-only path, set handle fields directly. Rejected because it duplicates validation and misses the MCP surface argument.

**Trade-offs accepted:** Resolution gate now has a 3-way OR condition (`profile_name is not None or explicit_posture is not None or explicit_turn_budget is not None`) which is slightly more complex than the original single check. Acceptable for the validation guarantee.

**Confidence:** High (E2) — verified by tests covering explicit-only, profile-only, and mixed paths.

**Reversibility:** High — the gate condition is a single `if` statement.

**Change trigger:** If a future caller needs `start()` to always resolve defaults (even with no arguments), the gate would expand to "always enter."

### Decision 3: Bare callers stay on None/legacy semantics

**Choice:** `codex.dialogue.start` with only `repo_root` (no profile, posture, or budget) continues to persist `None` for all resolved fields on the handle. No posture injection, no budget metadata.

**Driver:** The shakedown-b1 system has its own orchestrator and turn management. Pushing resolver defaults would inject `"Adopt a collaborative posture for this advisory turn."` into every shakedown Codex turn, silently altering shakedown behavior.

**Alternatives considered:**
- **Always resolve defaults** — every `start()` call enters resolution, bare callers get `collaborative/6`. Rejected because it changes existing behavior for callers that manage their own dialogue loop.

**Trade-offs accepted:** Design inconsistency: the resolver "owns" defaults, but bare callers don't get them. The `/dialogue` skill papers over this by always dispatching explicit values.

**Confidence:** High (E2) — verified by existing `test_start_without_profile_stores_none_fields_on_handle` test (pre-existing, still passes).

**Reversibility:** High — expanding the gate to "always enter" is a one-line change.

**Change trigger:** If a new caller needs defaults without explicit flags, or if the shakedown system is updated to accept posture.

### Decision 4: Posture affects question framing in all Step 6 branches, not just fallback

**Choice:** The orchestrator's posture-aware follow-up framing applies to all active Step 6 priority branches (1-4: scout evidence, unresolved items, unprobed claims, weakest claim), not only the last-resort posture-driven probe (priority 5).

**Driver:** User identified that the orchestrator's follow-up selection usually comes from scout evidence, unresolved items, or unprobed claims. If posture only matters when all of those are absent, the benchmark would barely observe posture differences between runs.

**Alternatives considered:**
- **Fallback-only posture** — posture table at priority 5 only. Rejected because it would rarely execute, making posture effectively invisible in benchmark adjudication.
- **Full server-side parity** — posture-aware template ranking in the MCP server. Rejected because even the baseline's context-injection server documents posture as "stored but not used in template ranking or convergence detection" at `enums.py:53`.

**Trade-offs accepted:** The orchestrator instructions are more complex (a 5-row × 2-column table plus a framing rule). Acceptable because the alternative is posture that exists in config but not in observable behavior.

**Confidence:** High (E2) — grounded in baseline analysis (the baseline's posture behavior also lives primarily at the agent layer, not in the server).

**Reversibility:** High — the framing table is a discrete section in the orchestrator Markdown.

**Change trigger:** If benchmark adjudication shows that posture framing is indistinguishable between runs despite the table.

### Decision 5: Metadata placed after `Repository root:` / `Scope directories:`

**Choice:** The skill dispatches `Posture:` and `Turn budget:` after the existing metadata fields in the dispatch prompt, not before them or in the objective region.

**Driver:** User identified a hidden seam: the orchestrator extracts the canonical objective as "text after the briefing block and before `Repository root:`." Inserting metadata between objective and `Repository root:` would corrupt objective extraction.

**Alternatives considered:**
- **Before `Repository root:`** — corrupts objective extraction. Rejected.
- **Separate sentinel block** — introduces parsing complexity for two metadata fields. Rejected as over-engineered.

**Trade-offs accepted:** The metadata block grows from 2 lines to 4 lines. The orchestrator's parsing is slightly more complex (parse 4 lines from the metadata block instead of 2). Acceptable.

**Confidence:** High (E2) — the objective extraction rule is explicit in the orchestrator (`dialogue-orchestrator.md:51`); verified that the new fields are below the extraction boundary.

**Reversibility:** High — field position is a single-line change in the skill dispatch template.

**Change trigger:** If a future metadata field needs to be placed before `Repository root:`, the extraction rule would need updating.

### Decision 6: Single default authority — resolver at `collaborative/6`, delete orchestrator constant

**Choice:** The profile resolver default (`collaborative/6` at `profiles.py:43-44`) is the single authority. The skill always dispatches explicit values, even for defaults. The orchestrator's `DIALOGUE_TURN_BUDGET = 10` constant is deleted — the orchestrator parses the budget from the dispatch prompt and fails if it's missing.

**Driver:** User identified three competing defaults: baseline `8`, resolver `6`, orchestrator `10`. Having three numbers that silently disagree is a latent bug. The skill should always dispatch explicit values so the orchestrator never needs a local fallback.

**Alternatives considered:**
- **Keep orchestrator constant as fallback** — rejected because it creates a divergence risk if someone changes the resolver default.
- **Use baseline default 8** — rejected because the candidate system's own default should come from its own resolver, not from the baseline.

**Trade-offs accepted:** The orchestrator now requires `Turn budget:` in the dispatch prompt — if missing, it fails loudly. This is intentional: a missing field is a skill bug, not a condition to silently recover from.

**Confidence:** High (E2) — verified that the constant is deleted from both references (lines 27 and 310), and the parsed budget is used for loop termination, Budget Exhaustion Window, and synthesis artifact.

**Reversibility:** Low — adding back a fallback constant would re-introduce the divergence risk. The design is intentionally non-reversible.

**Change trigger:** None — this is a correctness fix, not a preference.

## Changes

### `packages/plugins/codex-collaboration/server/profiles.py` (+4/-1)

**Purpose:** Tighten turn_budget validation from `> 0` to `1 <= x <= 15`.

**Approach:** Changed the validation predicate at line 142 from `turn_budget > 0` to `1 <= turn_budget <= 15`. Error message updated to reflect the range. The upper bound 15 comes from the baseline's `MAX_CONVERSATION_TURNS` and the orchestrator's effective dialogue turn limit. The resolver is now the single validation authority for budget bounds.

### `packages/plugins/codex-collaboration/server/dialogue.py` (+25/-3)

**Purpose:** Accept and forward explicit posture and turn budget through the resolution gate.

**Approach:** `start()` signature at line 112 gains `explicit_posture: str | None = None` and `explicit_turn_budget: int | None = None` kwargs. Resolution gate at line 132 expanded from `if profile_name is not None` to a 3-way OR. When any of the three parameters is present, `resolve_profile()` is called with explicit overrides forwarded. Comment block documents bare-caller None semantics as intentional.

### `packages/plugins/codex-collaboration/server/mcp_server.py` (+22/-3)

**Purpose:** Expose posture and turn_budget in the `codex.dialogue.start` MCP schema and dispatch.

**Approach:** Added `posture` (string enum with 5 values) and `turn_budget` (integer, min 1, max 15) as optional properties in the `inputSchema`. Dispatch at line 239 forwards both to `controller.start()`. Both fields are optional — bare callers (shakedown-b1) are unaffected.

### `packages/plugins/codex-collaboration/server/consultation_safety.py` (+2/-1)

**Purpose:** Register new fields with the safety policy so they don't trigger unexpected-field warnings.

**Approach:** Added `posture` and `turn_budget` to `DIALOGUE_START_POLICY.expected_fields`. Both are structural values (enum, integer), not user-authored content, so they belong in `expected_fields` (not scanned for credentials), not `content_fields` (scanned).

### `packages/plugins/codex-collaboration/skills/dialogue/SKILL.md` (+38/-6)

**Purpose:** Add `-p`/`-n` flag parsing, always-explicit dispatch, metadata placement after existing fields.

**Approach:** Invocation line changed from "No flags" to `[-p posture] [-n turns]`. Arguments section added with validation rules and defaults. Step 1 changed from "Capture objective" to "Parse arguments and resolve defaults." Step 7 dispatch template gains `Posture:` and `Turn budget:` lines after `Repository root:` and `Scope directories:`. Frontmatter gains `argument-hint` field. Description updated to mention flags.

### `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md` (+54/-11)

**Purpose:** Parse dispatch metadata, delete hardcoded constant, add posture-aware follow-up framing, tie parsed budget to loop termination.

**Approach:** Six changes: (1) `DIALOGUE_TURN_BUDGET` deleted from constants table. (2) New "Dispatch Parameters" section documents parsing `Posture:` and `Turn budget:` from the metadata block with validation rules and fail-if-missing policy. (3) Phase 2 updated to pass posture and turn_budget to `codex.dialogue.start`. (4) New "Step 6: Compose follow-up" section with 5-row posture-aware framing table applied to all active branches (1-4) plus fallback (5), with target-lock guardrail. (5) Phase 3 step 4 gains explicit turn budget check (`current_turn >= parsed_turn_budget` → Budget Exhaustion Window). (6) Phase 5 artifact `turn_budget` field references parsed value instead of deleted constant.

### `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` (+13/-20)

**Purpose:** Update scoring prerequisites and run condition status for resolved RC4.

**Approach:** Scoring Prerequisites section changed from BLOCKING to RESOLVED with resolution commit references and evidence. Run Condition Status table: posture and turn budget rows changed from **Blocked** to Matched. Quick-reference table: candidate system description updated to include `-p`/`-n` flags; scoring blockers row changed to "None (RC4 resolved)."

### `docs/benchmarks/dialogue-supersession/v1/manifest.json` (+4/-13)

**Purpose:** Move posture and turn_budget from `blocked` to `matched` in run_condition_parity.

**Approach:** The `blocked` key (containing posture and turn_budget objects with resolution_options) was removed entirely. Two new entries added to the `matched` object with resolution commit references. The `_note` updated to remove the "blocked items must be resolved" clause.

### `docs/benchmarks/dialogue-supersession/v1/summary.md` (+3/-4)

**Purpose:** Update RC4 status from Blocked to Matched.

**Approach:** Posture and turn budget rows in the Run-Condition Status table changed from `**Blocked**` to `Matched` with "Both systems accept `-p`/`-n` flag." Scoring blockers line changed to "None. RC4 resolved at `52a968e9`/`e2057f2b`."

### Test files (4 files, +274 lines total)

| File | New tests | Key coverage |
|---|---|---|
| `test_profiles.py` | +61 lines | Upper bound (16, 100 rejected; 15 accepted), explicit-override-without-profile, all 4 corpus combinations |
| `test_dialogue_profiles.py` | +62 lines | Explicit posture/budget on handle, explicit-beats-profile, invalid posture/budget rejection |
| `test_mcp_server.py` | +119 lines | Fake controller signatures updated (3 classes), MCP dispatch forwarding, schema assertion |
| `test_consultation_safety.py` | +32 lines | Posture/turn_budget as expected fields (no unexpected warning, no credential scan) |

## Codebase Knowledge

### Candidate system parameter flow (now complete)

| Layer | File | What happens |
|---|---|---|
| User invocation | `/codex-collaboration:dialogue -p evaluative -n 6 "objective"` | Flags parsed, defaults resolved |
| Skill dispatch | `skills/dialogue/SKILL.md:221-254` | Posture and Turn budget emitted in metadata block after Repository root / Scope directories |
| Orchestrator parsing | `agents/dialogue-orchestrator.md` Dispatch Parameters section | Posture and Turn budget parsed from metadata block; fail if missing |
| MCP call | `codex.dialogue.start` with `posture` and `turn_budget` | Forwarded from orchestrator to server |
| MCP dispatch | `mcp_server.py:249-254` | Posture and turn_budget forwarded to `controller.start()` |
| Controller resolution | `dialogue.py:132-152` | Resolution gate fires; `resolve_profile()` called with explicit overrides |
| Profile resolver | `profiles.py:78-86` | Precedence: explicit > profile > default. Validation: posture enum, budget 1-15 |
| Handle persistence | `models.py:198-200` | `resolved_posture`, `resolved_effort`, `resolved_turn_budget` stored on `CollaborationHandle` |
| Per-turn injection | `dialogue.py:368` → `prompt_builder.py:40-44` | `"Adopt a {posture} posture for this advisory turn."` on every Codex turn |
| Loop termination | `dialogue-orchestrator.md` Phase 3 step 4 | `current_turn >= parsed_turn_budget` → Budget Exhaustion Window |
| Synthesis artifact | `dialogue-orchestrator.md` Phase 5 | `turn_budget` field reflects parsed value |

### Baseline system parameter flow (for comparison)

| Layer | File | What happens |
|---|---|---|
| User invocation | `/cross-model:dialogue -p evaluative -n 6 "question"` | Flags parsed at `skills/dialogue/SKILL.md:25-33` |
| Skill dispatch | `skills/dialogue/SKILL.md:338-351` | Posture and Budget in delegation envelope to `codex-dialogue` agent |
| Agent parsing | `codex-dialogue.md:34-46` | Posture, Turn budget, scope_envelope parsed from prompt |
| Conversation loop | `codex-dialogue.md:457` | `effective_budget = min(max(1, user_budget), 15)` |
| Process turn | `codex-dialogue.md:270` | Posture passed to `process_turn` MCP call |
| Follow-up framing | `codex-dialogue.md:439-447` | 5-row posture patterns table |

### Key files and their roles

| File | Purpose | Key location |
|---|---|---|
| `profiles.py:78-86` | Profile resolver — single validation authority | `resolve_profile()` signature with explicit override kwargs |
| `profiles.py:142-146` | Budget bounds validation | `1 <= turn_budget <= 15` |
| `profiles.py:43-44` | Default authority | `_DEFAULT_POSTURE = "collaborative"`, `_DEFAULT_TURN_BUDGET = 6` |
| `dialogue.py:112-120` | Start signature | `explicit_posture` and `explicit_turn_budget` kwargs |
| `dialogue.py:132-152` | Resolution gate | 3-way OR with documentation of bare-caller semantics |
| `dialogue.py:368` | Posture read from handle | `posture = handle.resolved_posture` |
| `prompt_builder.py:40-44` | Per-turn posture injection | `"Adopt a {posture} posture for this advisory turn."` |
| `mcp_server.py:48-72` | `codex.dialogue.start` schema | `posture` (enum), `turn_budget` (int 1-15) |
| `mcp_server.py:249-254` | Dispatch forwarding | `explicit_posture=`, `explicit_turn_budget=` |
| `consultation_safety.py:38-41` | Safety policy | `posture` and `turn_budget` in `expected_fields` |
| `test_dialogue_profiles.py:78-95` | Posture-in-prompt pin test | Verifies posture string appears in prompt text |
| `consultation-profiles.yaml:18-94` | Bundled profiles | 8 non-phased profiles; evaluative/8 and evaluative/4 exist but no evaluative/6 |

### Dormant plumbing pattern

The candidate runtime had a significant amount of pre-built posture infrastructure that was never exposed through the MCP schema:
- `resolve_profile()` already accepted `explicit_posture` and `explicit_turn_budget` (just never called with them)
- `CollaborationHandle` already carried `resolved_posture`, `resolved_effort`, `resolved_turn_budget` (just always stored as `None` for non-profile callers)
- `build_consult_turn_text()` already injected posture into every turn (just never received a non-None posture from a non-profile start)
- Tests at `test_dialogue_profiles.py` already pinned this behavior

The wiring gap was in 4 places: MCP schema (didn't expose fields), dispatch (didn't forward them), resolution gate (didn't fire without profile name), and orchestrator (didn't parse or use them).

## Context

### T-04 acceptance criteria status after this session

| AC | Description | Status | Evidence |
|---|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) | `skills/dialogue/SKILL.md` |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) | `agents/dialogue-orchestrator.md` |
| 3 | Gatherer agents exist and use Claude-side tools | Done (PR #107) | Both agents with Glob/Grep/Read |
| 4 | Synthesis with bounded citations and convergence | Done | Dialogue-tier citations + `converged: false` terminal artifact |
| 5 | Benchmark contract executed on fixed corpus | **Unblocked** | RC4 resolved; scaffold ready; execution is the next step |
| 6 | Benchmark result recorded with per-task metrics | **Open** | Depends on AC-5 |
| 7 | Context-injection retirement decision explicit | **Open** | Depends on AC-6 |

### Mental model for this session

This session transitions from **execution scaffolding** to **control surface implementation**. The prior session built the benchmark artifact structure and identified what was missing. This session filled the gap: posture and turn-budget control surfaces throughout the candidate system's multi-layer stack (skill → MCP → controller → resolver → handle → prompt builder → orchestrator).

The key design insight: the runtime already had the capability (profile resolution, handle persistence, prompt injection). The gap was in the wiring — 4 specific points where values needed to flow through but didn't. This made the implementation much lighter than building posture from scratch would have been.

### Benchmark contract structure (unchanged from prior session)

| Section | Lines | Key content |
|---|---|---|
| Fixed Corpus | 74-84 | 4 rows: B1 architecture, B3 code review, B5 policy audit, B8 supersession |
| Run Conditions | 144-186 | 11 conditions; RC4 (posture/turn-budget) is unconditional; RC5 has "when host allows" caveat |
| Pass Rule | 313-331 | 3 conditions: safety=0, false<=baseline, supported_rate within 0.10 |

### Open tickets

| Ticket | ID | Status | Next |
|---|---|---|---|
| Dialogue parity & scouting retirement | T-04 | Open (AC 1-4 done, AC 5-7 unblocked) | Scored benchmark execution |
| Execution-domain foundation | T-05 | Open (unstarted) | Separate workstream |
| Promotion flow & delegate UX | T-06 | Open (blocked by T-05) | — |
| Analytics reviewer & cutover | T-07 | Open | Separate workstream |

## Learnings

### Dormant plumbing can reduce implementation scope by 80%+

**Mechanism.** The candidate runtime had profile resolution, handle persistence, and per-turn prompt injection all built and tested — but the MCP schema never exposed the fields. What looked like a "build posture from scratch" task turned out to be a "wire 4 connection points" task.

**Evidence.** Initial analysis proposed 3 implementation depths (prompt-only, structured, full parity). After user correction showing the dormant plumbing, the actual implementation was 397 lines total (274 test, 123 production) — much lighter than any of the proposed depths.

**Implication.** Before estimating implementation scope, grep for the target concept in the codebase. If the concept already exists but isn't wired through, the scope is "expose and connect," not "design and build."

### Instruction documents need explicit operative rules, not implicit constant references

**Mechanism.** The orchestrator Markdown defined `DIALOGUE_TURN_BUDGET = 10` in a constants table and referenced "budget exhaustion" in Phase 4. The connection between the constant and the termination condition was implicit — the orchestrator agent was expected to connect them via training knowledge. When the constant was deleted, the implicit connection broke silently.

**Evidence.** P1 review finding: "The parsed turn budget is accepted and reported without ever limiting the dialogue length." The loop continued indefinitely because no operative instruction said "when `current_turn >= parsed_turn_budget`, enter Budget Exhaustion Window."

**Implication.** When deleting a constant or default from an instruction document, grep for every place the document references the concept the constant served. Add explicit rules at each reference point. Implicit connections in Markdown are fragile — they depend on the reader (the agent) making the same inference every time.

### MCP schema changes require synchronized safety policy updates

**Mechanism.** The `codex_guard.py` PreToolUse hook uses `consultation_safety.py` to scan tool inputs. New fields not in `expected_fields` or `content_fields` trigger `unexpected_fields` warnings. Adding fields to the MCP schema without updating the safety policy causes the hook to flag every call with the new fields.

**Evidence.** User identified this as an incidental surface: "Adding new start fields means updating that policy and its tests, alongside the MCP schema." The `DIALOGUE_START_POLICY.expected_fields` update was included in the same patch.

**Implication.** When adding fields to any codex-collaboration MCP tool schema, always update the corresponding policy in `consultation_safety.py` in the same commit. The safety policies are at lines 33-48 (consult, start, reply).

### Budget upper bounds should live below the skill layer

**Mechanism.** The candidate skill validates `-n` in the 1-15 range for UX, but the authoritative validation must be in `resolve_profile()` because `codex.dialogue.start` is a real MCP surface. Direct tool callers bypass the skill — if bounds validation only lives in the skill, the server silently accepts out-of-range values.

**Evidence.** User pointed this out: "If you validate only in SKILL.md, direct tool callers can still inject bad values." Budget bounds were moved to `profiles.py:142`.

**Implication.** For any parameter exposed in an MCP schema: validate at the server layer (authoritative) and optionally at the skill layer (UX). Never validate only at the skill layer.

## Next Steps

### 1. Execute benchmark v1 in scored mode

**Dependencies:** None — RC4 is resolved, scaffold is on main, all prerequisites met.

**What to do:**
1. Follow the operator procedure from Phase 1 (fix commit on main, verify plugins, create staging)
2. Execution mode gate should now pass (both checks return Yes)
3. Execute 4 rows × 2 systems = 8 runs with fresh sessions, stage everything
4. Adjudicate row-by-row from staging
5. Benchmark-wide mode determination, aggregate scoring
6. Batch import and finalize

**What to read first:** `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` — the full procedure.

**Potential obstacles:** Manual adjudication remains the dominant cost (~80-160 individual claim adjudications, ~2-4 hours). Session ID availability for RC6 is still operator-attested (open question 3 from prior session). All other obstacles (RC4, staging protocol, mode gate) are resolved.

### 2. (After AC-5) Record benchmark result (AC-6) and make retirement decision (AC-7)

**Dependencies:** Scored benchmark execution (#1).

**What to do:** Fill in `summary.md` with scored results, evaluate pass rule (3 conditions: safety=0, false<=baseline, supported_rate within 0.10), and make explicit retirement decision for context-injection.

## In Progress

**Clean stopping point — RC4 implementation complete, merged to main, nothing in flight.**

- **Approach:** Bottom-up implementation guided by user-drafted implementation order and adversarial review.
- **State:** Complete. All 5 commits on main (`adcf49ea` through `afa55eac`).
- **Working:** Posture and turn-budget flow end-to-end from skill flags through MCP, controller, resolver, handle, prompt builder, and orchestrator loop termination. 586 tests passing. All benchmark artifacts aligned with resolved state.
- **Not working:** Nothing broken.
- **Next action:** Scored benchmark execution per the operator procedure.

## Open Questions

### 1. What is the canonical way to obtain a Claude Code session ID?

**Context:** The operator procedure requires a canonical host session ID for scored runs. If unavailable, the run is forced to rehearsal. The procedure suggests checking the status bar or `~/.claude/session_id`, but these paths are not guaranteed.

**Impact:** If no canonical session ID is reliably available, scored runs may be impossible to audit for RC6, making all runs effectively rehearsal.

**Decision pending until:** Investigating Claude Code's session identity mechanism (carried from prior session).

### 2. Should `scope_envelope` be wired through the candidate skill?

**Context:** Both gatherer agents support `scope_envelope` but the skill doesn't pass it. Currently classified as "prompt-only" enforcement for both systems, which is v1-compliant but a known fragility.

**Impact:** Low for v1 (procedural enforcement is contract-compliant). Would strengthen scope control story if wired through.

**Decision pending until:** After benchmark execution — a nice-to-have, not blocking.

## Risks

### 1. Prompt-only scope enforcement is fragile

**Impact:** Neither system mechanically prevents out-of-scope scouting during benchmark runs. A scouting step that ignores the prompt instruction will only be caught during transcript review, not at runtime.

**Mitigation:** Contract-compliant for v1 (procedural enforcement provision). Each violation invalidates the run and requires a rerun.

### 2. Manual adjudication is the dominant benchmark cost

**Impact:** 4 rows × 2 systems = 8 syntheses, each requiring claim inventory, labeling, safety review, and second-pass completeness review. At ~10-20 claims per synthesis: 80-160 individual adjudications (~2-4 hours).

**Mitigation:** Row-by-row adjudication keeps context fresh. High-signal rows first (B3 safety, B8 supersession).

## References

### Commits this session

| Commit | Message | Scope |
|---|---|---|
| `52a968e9` | feat(codex-collaboration): add explicit posture and turn-budget to dialogue start | Backend: profiles, dialogue, MCP, safety, tests |
| `e2057f2b` | feat(codex-collaboration): wire posture and turn-budget through skill and orchestrator | Instructions: skill flags, orchestrator parsing + framing |
| `c36b56c7` | docs(codex-collaboration): update operator procedure for resolved RC4 blockers | Operator procedure: BLOCKING → RESOLVED |
| `afa55eac` | docs(codex-collaboration): align benchmark artifacts with resolved RC4 state | Manifest + summary consistency |

### Authority documents

| Document | Location | Role |
|---|---|---|
| Supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Acceptance authority |
| Benchmark contract (v1) | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Benchmark authority |
| Operator procedure | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | Execution procedure |
| Benchmark readiness | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/benchmark-readiness.md` | Prerequisite gate |

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-15_19-30_t04-benchmark-v1-scaffold-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-15_15-00_t04-ac4-closed-benchmark-v1-contract-rewrite.md`
- Prior: `docs/handoffs/archive/2026-04-14_23-30_t04-gatherer-implementation-merged-and-e2e-smoke-run.md`
- Prior: `docs/handoffs/archive/2026-04-14_22-45_t04-gatherer-plan-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_20-17_t04-v1-e2e-verified-pr-106-open.md`
- Prior: `docs/handoffs/archive/2026-04-14_16-30_t04-v1-four-production-surfaces-authored-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_12-55_t04-v1-section-10-authoring-decisions-resolved-and-committed.md`

## Gotchas

### Objective extraction boundary is fragile

**Symptom:** Metadata injected between the objective and `Repository root:` line corrupts the orchestrator's objective extraction.

**Root cause:** The orchestrator defines the canonical objective as "text after the briefing block and before `Repository root:`." Any new dispatch metadata in that region becomes part of the objective string.

**Prevention:** Always place new metadata fields AFTER `Repository root:` and `Scope directories:`, not before them.

### `DIALOGUE_TURN_BUDGET` deletion requires two updates

**Symptom:** Orchestrator constant deleted but loop keeps running past the intended budget.

**Root cause:** The constant appeared in two places (constants table at line 27 and Phase 5 artifact projection at line 310) and was implicitly referenced by Phase 3/4 termination. Deleting the constant without adding explicit operative rules at all reference points breaks the loop constraint silently.

**Prevention:** When deleting a constant from an instruction document, grep for ALL references and add explicit rules at each.

### MCP schema changes need safety policy sync

**Symptom:** New `codex.dialogue.start` fields trigger `unexpected_fields` warnings from the PreToolUse hook.

**Root cause:** `consultation_safety.py` has per-tool policies listing expected and content fields. New fields not registered in either category are treated as unknown and flagged.

**Prevention:** Always update `consultation_safety.py` in the same commit as MCP schema changes.

## Conversation Highlights

### User's correction of the dormant plumbing model

The user provided a detailed correction of my initial analysis showing the candidate runtime already has posture plumbing:
- "The correction is: the candidate does not need posture invented from scratch. It needs posture **wired through**."
- Cited 5 specific locations with file:line references where posture was already implemented but not exposed.
- Identified the `resolve_profile()` explicit override signature as the key enabler: "The resolver already supports explicit overrides in `profiles.py:78`; the MCP schema just doesn't expose them yet."

### User's implementation order rationale

"Backend first prevents the worst failure mode: updating the skill contract to promise flags before the MCP/runtime path can actually honor them."

"The second reason is debugging clarity. If you patch the skill and orchestrator before the server path exists, failures can appear as prompt-shape issues when the real problem is schema rejection or missing persistence on the handle."

### User's P1 finding

"The file now parses `Turn budget` and reports it, but there is still no operative instruction that uses that parsed value to stop after N turns or to enter the `budget_exhausted` window. That means the core benchmark parity change for `-n` is only partial."

### User's design consistency philosophy

On bare callers and defaults: "If keeping bare `codex.dialogue.start` on legacy semantics is intentional, P2 is just a design inconsistency. If the goal was one default authority across all callers, it still needs one more backend step."

## User Preferences

### Review-driven development with adversarial rigor

User performs structured reviews with specific file:line citations, priority ratings, and confidence scores. Each finding includes mechanism, impact, and required resolution. The P1/P2 review format (`::code-comment` with file, start/end lines, priority, confidence) is the standard review template.

### Implementation order matters as much as implementation content

User drafted the implementation order themselves, with explicit rationale for each step's position. They care about which file gets patched first and why, not just that all files get patched.

### Contract text is authoritative (carried from prior session)

Run condition 4 vs. 5 distinction enforced exactly. Paraphrasing or extending contract provisions beyond their literal scope is rejected.

### Honest documentation over false confidence (carried from prior session)

The "prompt-only" scope enforcement label and the "None semantics for bare callers" documentation are both instances of this preference — state what's true, don't rationalize limitations.
