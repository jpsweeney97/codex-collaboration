---
date: 2026-04-16
time: "00:18"
created_at: "2026-04-16T04:18:32Z"
session_id: 7bee005a-163d-4a57-bdd2-48f37f5a229b
resumed_from: docs/handoffs/archive/2026-04-15_22-38_t04-execution-mode-gate-cleared-invocations-prepared.md
project: claude-code-tool-dev
branch: main
commit: 8243693b
title: "T-04 runtime gate cleared — B1 baseline pending rerun after cross-model updates"
type: handoff
files:
  - docs/benchmarks/dialogue-supersession/v1/manifest.json
  - /tmp/benchmark-v1-staging-20260415/invocations.md
---

# T-04 Runtime Gate Cleared — B1 Baseline Pending Rerun After Cross-Model Updates

## Goal

Execute the T-04 benchmark Phase 2 per-row runs after confirming the live runtime gate. This session's scope was: (1) clear the live runtime execution-mode gate to confirm SCORED mode, (2) prepare the B1 baseline invocation package, (3) respond to mid-flight baseline-system issues that required code changes.

**Trigger.** Resumed from `2026-04-15_22-38` handoff. Prior session cleared the execution-mode gate at the code level only — a 4-layer trace through skill → orchestrator → MCP schema → profile resolver. The live runtime gate (does the plugin actually accept `-p`/`-n` at runtime?) was still an open risk, blocking AC-5 ("benchmark contract executed on fixed corpus").

**Stakes.** The execution mode gate determines whether runs are SCORED (evidentiary) or REHEARSAL (non-evidentiary). Only SCORED runs satisfy AC-5. A runtime failure to accept `-p` or `-n` would force all 8 runs to REHEARSAL, blocking the retirement decision.

**Success criteria achieved:**

1. Live runtime gate cleared: SCORED confirmed via MCP schema introspection (E1 runtime evidence) layered on top of prior 4-layer code trace (E2).
2. B1 baseline invocation package prepared with `{run_type}` substituted.
3. Cross-model timeout issue discovered during user's B1 baseline attempt → fixed and committed.
4. Cross-model dev-dependency cleanup committed.
5. `run_commit` field in manifest kept aligned with HEAD across two update cycles.
6. Clean state handed off: all edits committed, staging directory intact, invocations packet unchanged.

**Position in the T-04 arc:**

| Session | Role | Artifact |
|---|---|---|
| 2026-04-13 | v1 plan drafting and approval | Plan at `main@73f8c9c1` |
| 2026-04-14 (several) | Scaffold + production surfaces + gatherer + E2E | Merged through `d478c0d7` |
| 2026-04-15 15:00 | AC-4 closed, contract narrowed | `1e08c397` |
| 2026-04-15 19:30-22:38 | RC4 wiring, Phase 1 prep, code-level gate | Through `58bcd73b` |
| 2026-04-15 22:38 | Invocations packet + operator procedure fix | Prior handoff |
| **2026-04-16 00:18 (this)** | **Runtime gate cleared; baseline-system fixes during first B1 attempt** | **Commits `401db4d7`, `bfbaef14` (on main)** |
| Next | Rerun B1 baseline on current HEAD; proceed through B1-B8 pairs | |

**Connection to project arc.** T-04 benchmark is the empirical gate for retiring cross-model dialogue+context-injection in favor of the codex-collaboration candidate. T-05, T-06, T-07 are blocked on or downstream of the retirement decision rendered by AC-7. This session represents the transition from *gate-clearance* to *execution*, with one unscheduled detour (baseline-system timeout fix) consumed along the way.

## Session Narrative

**Phase 1 — Handoff load and runtime gate scoping (~5 min).**

Loaded the `2026-04-15_22-38` handoff. The prior handoff recorded code-level gate clearance (SCORED) via a 4-layer trace but flagged Risk #1: "Live runtime gate has not been cleared." Read operator-procedure.md:146-166 — the gate requires two checks: "Can the candidate system accept posture input matching the corpus row?" and "Can the candidate system accept turn-budget input matching the corpus row?"

The prior handoff's Open Question #1 asked whether the runtime gate needed a full dialogue or just flag-parsing confirmation. The answer that emerged: schema introspection is stronger than either.

**Phase 2 — Runtime gate via MCP schema introspection (~10 min).**

Chose schema introspection over test invocation. Called `mcp__plugin_codex-collaboration_codex-collaboration__codex_status` — returned version 0.121.0, authenticated, `thread_count=0`, all required methods (`thread/fork`, `thread/read`, `thread/resume`, `thread/start`, `turn/interrupt`, `turn/start`) and optional method (`turn/steer`) available, zero errors. Confirmed plugin data path: `/Users/jp/.claude/plugins/data/codex-collaboration-inline`.

Then fetched the `codex_dialogue_start` tool schema. The live runtime server advertises:

- `posture` parameter: `enum: ["collaborative", "adversarial", "exploratory", "evaluative", "comparative"]` — matches the 5 values from the code-level trace
- `turn_budget` parameter: `type: integer`, `minimum: 1`, `maximum: 15` — matches the code-level constraint

This is stronger evidence than a test invocation. A test invocation shows "one call worked." Schema introspection shows "the server is structurally advertising these capabilities with correct types and constraints." Universal statement vs sample-of-one. Mapped cleanly to layers 3-4 of the prior 4-layer code trace; layers 1-2 (skill flag parsing → orchestrator dispatch) are confirmed by the fact that the plugin system is loading tools at all.

**Gate result:** Both checks pass. Execution mode: **SCORED**. Evidence levels: E2 (code) + E1 (runtime schema introspection).

**Phase 3 — B1 baseline invocation package prep (~5 min).**

User confirmed the gate conclusion and added two important constraints I had under-emphasized: (1) "do not reuse the current gate-check session for a benchmark run" — each run needs a fresh Claude session; (2) "if any individual run cannot produce a canonical session ID, reclassify that run to rehearsal even though the benchmark-wide gate passed." Cited operator-procedure.md:166 for gate and :174 for fresh-session rule.

Read `/tmp/benchmark-v1-staging-20260415/invocations.md` (intact from prior session) and operator-procedure.md:168-228 (Phase 2 per-row execution procedure). Prepared the B1 baseline package with `{run_type}` substituted to `This is a scored benchmark run.` Surfaced the subtle point that B1 baseline uses `/cross-model:dialogue` (baseline system) while the candidate uses `/codex-collaboration:dialogue` — the two systems being compared.

**Phase 4 — User reports B1 baseline encountered an issue (~1 min).**

User: "The cross-model dialogue run (B1 baseline) encountered an issue that required updates to the cross-model plugin. so the commit SHA changed."

Ran `git log --oneline -10` and `git diff 58bcd73b..HEAD --stat`. One new commit: `47713384` — "fix(cross-model,claude-code-docs): increase Codex subprocess timeout to 15min and fix docs canary rejection." 8 files changed: 4 in claude-code-docs, 4 in cross-model.

**Phase 5 — Diagnose benchmark impact of the timeout fix (~5 min).**

Inspected the cross-model-specific diff (`git diff 58bcd73b..47713384 -- packages/plugins/cross-model/`):

- `codex_consult.py:82`: `_SUBPROCESS_TIMEOUT` 300s → 900s
- `codex_delegate.py:671`: `proc.wait(timeout=...)` 600s → 900s
- Two test files updated to match

This is timeout-only. No logic, output, or behavioral changes. The dialogue output a run produces is unchanged — the timeout just determines whether the subprocess has enough time to finish. Benchmark comparison fairness is preserved because the change is in infrastructure plumbing, not dialogue logic.

The claude-code-docs changes were similarly neutral (docs-search MCP server, not either dialogue system).

**Phase 6 — First run_commit reconciliation (~3 min).**

Raised two procedural questions to the user:
1. B1 baseline status — completed on new HEAD or still pending?
2. Should `run_commit` be updated from `425f7784` (current manifest value, set during RC4 session) to `47713384`?

User: "The B1 baseline needs to be rerun - I just made the changes and committed them. Update the `run_commit` field in the benchmark artifacts."

Grep for `run_commit` → `manifest.json:7` and a reference at `operator-procedure.md:74`. Edited `manifest.json:7` from `"run_commit": "425f7784"` to `"run_commit": "47713384"`. Committed as `401db4d7` with a message explaining the timeout fix lineage.

**Phase 7 — User reports further cross-model changes (~5 min).**

User: "I made further changes to the cross-model plugin so the commit SHA changed again."

Two new commits:
- `7ddcb418` — `fix(cross-model): remove workspace-only context-injection dev dependency`
- `7c283c39` — `chore: update uv.lock after cross-model dependency change`

Diff showed `pyproject.toml` losing the `context-injection` dev dependency and the `[tool.uv.sources]` section, plus corresponding `uv.lock` updates. Dev-dependency-only — no runtime change. The cross-model plugin's runtime behavior during a dialogue does not read `pyproject.toml` dev-deps or `uv.lock`.

Noted the infinite-regress concern — each `run_commit` update moves HEAD past the recorded value. But the convention established in the prior session (`fb2e931b` setting `run_commit` to `425f7784`, which was two commits earlier) tolerates this offset.

**Phase 8 — Second run_commit reconciliation (~3 min).**

User: "commit this change."

Edited `manifest.json:7` from `"run_commit": "47713384"` to `"run_commit": "7c283c39"`. Committed as `bfbaef14` with a message explaining the dev-dep cleanup lineage.

**Phase 9 — Discovery of additional post-handoff commit (~2 min).**

While gathering state for this handoff, ran `git log --oneline -15` and saw a third new commit not previously surfaced in conversation: `8243693b — chore(cross-model): lower default reasoning_effort from xhigh to high`. The commit message notes this was made by the user at 00:17 local time (just before the handoff request).

Inspected via `git show --stat 8243693b`. 13 files changed across HANDBOOK, README, agents, references, consultation-profiles.yaml, codex_consult.py, codex_shim.py, skills, tests. The commit message: "xhigh remains a valid enum value throughout — only the default changes."

**Important benchmark neutrality:** The benchmark's `manifest.json:12-14` explicitly sets `"reasoning_effort": "high"`. So the effective reasoning effort for benchmark runs is unchanged by this commit — it only changes the fallback default, which the benchmark overrides. But from strict `run_commit`-alignment-with-HEAD convention, this could warrant a third update cycle. Flagged as an open question for the next session rather than proactively updating.

**Phase 10 — User requests handoff.**

User: "save a handoff. we'll pick up from here in the next session."

## Decisions

### Decision 1: MCP schema introspection as runtime gate evidence

**Choice:** Accept the combination of `codex_status` health check + `codex_dialogue_start` tool schema introspection as runtime evidence for the execution-mode gate, without invoking a test dialogue.

**Driver:** The operator procedure at line 150-153 asks whether `/codex-collaboration:dialogue` "accepts" `-p` and `-n`. Schema introspection directly answers this: the running MCP server structurally advertises both parameters with the correct enum/integer types and constraints. A test invocation would add sample-of-one behavioral evidence at the cost of a full dialogue (API calls, turn budget, time).

**Alternatives considered:**
- **Test invocation** — `/codex-collaboration:dialogue "test" -p evaluative -n 2`. This was the approach suggested in the prior handoff's Next Steps. Rejected because schema introspection is a stronger structural claim ("the server is serving this capability") vs a behavioral sample ("one call succeeded"), and a test invocation would consume unnecessary API resources.
- **Rely on code-level trace alone** — prior session already had this (E2). Rejected because the handoff's Risk #1 explicitly flagged runtime environment differences (MCP server crash, plugin loading issue) as theoretically possible.

**Trade-offs accepted:** Schema introspection doesn't exercise the full dispatch path — skill flag parsing and orchestrator metadata-block injection are inferred from "plugin loads at all" rather than directly observed. Accepted because: (a) these layers are simple string manipulation with code-level evidence, (b) the first actual candidate run will exercise them end-to-end if a defect exists.

**Implication:** The "live runtime gate" as a distinct pre-flight check can be satisfied by schema introspection in future benchmarks, not just test invocations. Lower-cost pattern for any benchmark where the candidate exposes an MCP schema.

**Confidence:** High (E1+E2 combined). Layer-by-layer: schema introspection (E1 runtime) + code trace (E2) + process health (E1 via codex_status).

**Reversibility:** High — if the first candidate run fails at runtime, reclassify all runs to REHEARSAL per the invocations packet's built-in fallback.

**Change trigger:** If a first candidate run fails with flag-parsing errors, treat the gate as unreliable and document that schema introspection was insufficient in this case.

### Decision 2: Keep run_commit aligned with HEAD on each substantive commit

**Choice:** Update `manifest.json:7` `run_commit` field whenever baseline-system-relevant commits land, even knowing each update creates a new commit.

**Driver:** User's direct instruction after first cross-model fix: "Update the `run_commit` field in the benchmark artifacts." Repeated after the dev-dep cleanup with "commit this change."

**Alternatives considered:**
- **Leave run_commit as 425f7784 and use frontmatter/notes to document actual repo state** — simpler but creates audit friction (reader has to cross-reference two sources). Rejected because the manifest is the single source of truth for the benchmark and must be self-describing.
- **Update only after all baseline-system changes are complete, then record once at Phase 2 start** — avoids regress but creates a window where the manifest is stale. Rejected because benchmark-setup sessions are not guaranteed to be contiguous, and the cost of catching up later is higher than the cost of small updates now.
- **Defer manifest update to Phase 5 import** — standard practice for benchmark metadata. Rejected here because `run_commit` is a pre-run field (operator-procedure.md:74 says "Record the commit SHA in `manifest.json` under `run_commit`").

**Trade-offs accepted:** Each update creates a new commit that technically moves HEAD past the recorded `run_commit`. The convention tolerates this offset — prior session's `fb2e931b` set `run_commit` to `425f7784`, two commits earlier. Accepted because the semantic meaning is "which commit contains the last substantive benchmark-relevant change," not "which commit is HEAD right this second."

**Implication:** If additional cross-model commits land between this handoff and the first valid B1 baseline run, another `run_commit` update cycle will be warranted. The next session should reconcile against latest HEAD before starting runs.

**Confidence:** High (E2) — user gave direct instructions twice, and the convention was established in the prior session.

**Reversibility:** High — single-line edit per update.

**Change trigger:** If the user signals that `run_commit` should point to a specific commit rather than tracking HEAD, switch to that explicit target.

### Decision 3: Flag reasoning_effort commit as open question rather than updating run_commit proactively

**Choice:** Note the discovery of `8243693b` (reasoning_effort default change) in this handoff but do not update `run_commit` a third time in this session.

**Driver:** Three factors: (1) the benchmark's `manifest.json:12-14` explicitly sets `"reasoning_effort": "high"`, so the effective behavior is unchanged — the commit only modifies the default that the benchmark already overrides; (2) the user did not explicitly surface this commit in conversation; (3) making a third update during handoff-save is out of scope for "save a handoff" — that's an edit, not a save.

**Alternatives considered:**
- **Update run_commit to 8243693b proactively** — rejected because the user's directives so far have been explicit ("update the run_commit field"), and acting on implicit inference during a handoff-save would violate "solve the task that was asked for" (CLAUDE.md global).
- **Ignore the commit entirely** — rejected because a handoff must capture the full state, and an unreconciled HEAD vs `run_commit` gap is audit-relevant.

**Trade-offs accepted:** The next session will see a gap between `run_commit` (`7c283c39`) and current HEAD (`8243693b`) and will need to reconcile. This is a minor operational debt, not a correctness issue.

**Confidence:** Medium (E1). The benchmark explicitly overrides reasoning_effort, so the runtime impact is zero. But audit strictness might prefer strict HEAD tracking.

**Reversibility:** High — a third run_commit update is a single-line edit.

**Change trigger:** If the next session confirms HEAD-strict `run_commit` is expected (or the user requests it), update immediately.

## Changes

### `docs/benchmarks/dialogue-supersession/v1/manifest.json` — run_commit updated twice

**Purpose:** Keep the benchmark's recorded `run_commit` aligned with the repo state runs will execute against, as new baseline-system changes landed mid-session.

**Approach:** Single-line edits at `manifest.json:7`. Two cycles:
- Edit 1 (committed as `401db4d7`): `"run_commit": "425f7784"` → `"run_commit": "47713384"`
- Edit 2 (committed as `bfbaef14`): `"run_commit": "47713384"` → `"run_commit": "7c283c39"`

**Key detail:** Commit messages explain the lineage — which cross-model change prompted the update, whether the change was benchmark-relevant at runtime (timeouts only / dev-deps only), and why the update keeps audit reconstruction simple.

**Future-Claude note:** A third update to `8243693b` (reasoning_effort default) is a candidate but not mandatory — the benchmark explicitly sets `reasoning_effort: high`, so the default change has no runtime effect on benchmark runs.

## Codebase Knowledge

### MCP schema introspection as a runtime verification technique

| Capability | Tool | What it reveals | Evidence level |
|------------|------|-----------------|----------------|
| Server health | `codex_status` | version, auth, uptime, required/optional methods, errors | E1 runtime |
| Tool schema | `codex_dialogue_start` (via `ToolSearch` fetch) | parameter names, types, enums, min/max constraints | E1 runtime |
| Combined | Both | Server is live AND advertises these capabilities with correct constraints | E1 runtime (stronger than behavioral test) |

**Universal claim vs sample-of-one.** Schema introspection confirms "the server structurally supports this" — a universal claim. A test invocation confirms "this one call succeeded" — a sample-of-one. Schema introspection wins on generality; test invocation wins on end-to-end coverage. For flag-acceptance verification, the universal claim is sufficient.

**Where schema introspection is insufficient:** Anything involving runtime dispatch paths not captured in the schema. For example: does the posture value actually influence the dialogue behavior downstream? That's not a schema question — it requires a test run. For "does the server accept this input," schema suffices.

### Timeout values in cross-model plugin

Pre-`47713384` values and their rationale (inferred from git history, tests, and commit messages):

| Location | Old | New | Purpose |
|----------|-----|-----|---------|
| `codex_consult.py:82` (`_SUBPROCESS_TIMEOUT`) | 300s (5min) | 900s (15min) | Upper bound on a consult subprocess |
| `codex_delegate.py:671` (`proc.wait(timeout=...)`) | 600s (10min) | 900s (15min) | Upper bound on a delegate subprocess |

The previous values were tuned for typical Codex latency with lower reasoning effort. High reasoning effort + complex dialogues pushed into 5-15 minute ranges, which triggered the timeout during B1 baseline. The 15-minute window is generous — an actual real-world 10-12 minute dialogue now completes without clipping.

**Tests matched the timeouts:** `tests/test_codex_consult.py:285` and `tests/test_codex_delegate.py:518,723` had mocked `TimeoutExpired` instances with the old timeout values. Any future timeout change must update these fixtures.

### Manifest vs HEAD convention

From manifest.json and git log:

| Field | Source | Semantic meaning |
|-------|--------|------------------|
| `run_commit` (manifest.json:7) | Recorded by operator | Which commit contains the last substantive benchmark-relevant change |
| HEAD | git | Literal current commit |
| Delta | Always >= 0 | Convention tolerates small offset (1-2 commits) for the manifest-update commit itself |

The prior session's convention (established via commit `fb2e931b` setting run_commit to `425f7784`) accepts that the manifest-update commit is itself past the recorded value. This is semantically coherent because the manifest update doesn't change benchmark-relevant code — it only updates metadata.

### Reasoning effort configuration surfaces

From `8243693b` commit (inspected but not acted on this session):

| Surface | File | Role |
|---------|------|------|
| Contract §8 default | `packages/plugins/cross-model/references/consultation-contract.md` | Authoritative default |
| Runtime fallbacks | `codex_consult.py`, `codex_shim.py` | Used when no override present |
| Skill docs | `skills/codex/SKILL.md`, `skills/dialogue/SKILL.md` | User-visible default |
| Agent docs | `agents/codex-dialogue.md`, `agents/codex-reviewer.md` | Used in autonomous work |
| Reference docs | `HANDBOOK.md`, `README.md`, `references/contract-agent-extract.md` | Documentation |
| Profiles | `references/consultation-profiles.yaml` | Per-profile overrides |
| Tests | `tests/test_codex_consult.py`, `tests/test_codex_shim.py` | Fixture values |

The benchmark manifest overrides this at `manifest.json:12-14`, so the runtime effect on benchmark runs is zero — but the mirroring complexity across 13 files is notable. Any future default change must update all 13 surfaces for coherence.

### Benchmark staging state

| Artifact | Path | Status |
|----------|------|--------|
| Staging directory | `/tmp/benchmark-v1-staging-20260415/` | Intact |
| Invocations packet | `/tmp/benchmark-v1-staging-20260415/invocations.md` | Unchanged (no edits needed — `{run_type}` substitution is operator-side) |
| Manifest | `docs/benchmarks/dialogue-supersession/v1/manifest.json` | Updated twice (`run_commit`) |
| Operator procedure | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | Unchanged (session ID path fix from prior session still in place) |

## Context

### Current T-04 acceptance criteria status

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| 1 | `/dialogue` skill exists | Done (PR #106) | `skills/dialogue/SKILL.md` |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) | `agents/dialogue-orchestrator.md` |
| 3 | Gatherer agents exist | Done (PR #107) | Both agents with Glob/Grep/Read |
| 4 | Synthesis with bounded citations | Done | Dialogue-tier citations + convergence |
| 5 | Benchmark contract executed on fixed corpus | **Gate cleared (SCORED); B1 baseline pending rerun** | MCP schema + code trace |
| 6 | Benchmark result recorded with per-task metrics | **Open** | Depends on AC-5 |
| 7 | Context-injection retirement decision explicit | **Open** | Depends on AC-6 |

### Mental model for this session

This session was supposed to be Phase 2 execution kickoff (B1 baseline + B1 candidate). It became a **baseline-system hardening detour** — the first B1 baseline attempt exposed a latent timeout issue in cross-model, which required patching before rerun. The candidate system (codex-collaboration) was never exercised this session.

Two useful reframes emerged:

1. **Schema introspection > test invocation for flag-acceptance gates.** This is a pattern reusable beyond T-04.
2. **`run_commit` tracking is an iterative convention, not a one-shot record.** Each substantive commit triggers a potential update cycle. The cost of small updates is low; the cost of a stale `run_commit` at Phase 5 import is high.

### Commits landed this session

| Commit | Author | Message | Scope |
|--------|--------|---------|-------|
| `47713384` | User | fix(cross-model,claude-code-docs): increase Codex subprocess timeout to 15min and fix docs canary rejection | Baseline-system infrastructure |
| `401db4d7` | Me | docs(codex-collaboration): update run_commit to include cross-model timeout fix | Manifest metadata |
| `7ddcb418` | User | fix(cross-model): remove workspace-only context-injection dev dependency | Dev-deps only |
| `7c283c39` | User | chore: update uv.lock after cross-model dependency change | Dev-deps only |
| `bfbaef14` | Me | docs(codex-collaboration): update run_commit to include cross-model dev-dep cleanup | Manifest metadata |
| `8243693b` | User | chore(cross-model): lower default reasoning_effort from xhigh to high | Baseline-system default (benchmark overrides) |

### Open tickets

| Ticket | ID | Status | Next |
|--------|-----|--------|------|
| Dialogue parity & scouting retirement | T-04 | Open (AC 1-4 done, AC-5 in progress) | Rerun B1 baseline, continue through B8 |
| Execution-domain foundation | T-05 | Open (unstarted) | Separate workstream |
| Promotion flow & delegate UX | T-06 | Open (blocked by T-05) | — |
| Analytics reviewer & cutover | T-07 | Open | Separate workstream |

## Learnings

### MCP schema introspection is the lowest-cost flag-acceptance verification

**Mechanism.** When a candidate system exposes an MCP tool schema, the schema itself is a direct statement of "the server accepts these parameters with these types and constraints." Fetching the schema via `ToolSearch` (or the MCP client's equivalent) reveals this without any test call. Combined with a health check (`codex_status`), you get both "server is live" and "server advertises this capability."

**Evidence.** This session cleared the T-04 execution-mode gate using only two MCP reads: `codex_status` (health) and `codex_dialogue_start` schema (capability). Both returned in sub-second time. A test invocation would have cost one full Codex dialogue (minutes, API credits, a turn budget consumed).

**Implication.** For any future benchmark where the candidate exposes an MCP schema, prefer schema introspection over test invocations for pre-flight capability gates. Schema introspection is a structural/universal claim; test invocations are behavioral/sample-of-one claims. For "does the server accept X," structural wins.

**Watch for.** Schema introspection does not verify dispatch correctness — it only verifies "the server says it supports this." If a bug exists between schema advertisement and runtime handling, schema introspection won't catch it. Test invocations remain the canonical way to verify end-to-end behavior. Use schema introspection for gate-clearance, not for end-to-end correctness.

### `run_commit` tracking requires iterative update discipline

**Mechanism.** The manifest's `run_commit` field records "which commit contains the last substantive benchmark-relevant change." Each such change triggers a potential update. Each update is itself a commit, which creates a minor HEAD/`run_commit` offset. The convention (from `fb2e931b`) tolerates 1-2 commits of offset — the manifest-update commit doesn't change benchmark-relevant code.

**Evidence.** This session performed two update cycles (`401db4d7`, `bfbaef14`). A third update candidate (`8243693b` reasoning_effort change) was deferred as an open question because the benchmark explicitly overrides the affected default.

**Implication.** Sessions that span multiple cross-model changes should be prepared for multiple `run_commit` update cycles. Do not assume one-shot record-and-done.

**Watch for.** The decision of whether to update `run_commit` depends on whether the new commit changes benchmark-relevant code. Infrastructure/plumbing changes (timeouts, dev-deps) warrant updates to keep audit reconstruction simple. Behavioral changes (e.g., reasoning effort defaults where the benchmark overrides) are optional — note in handoff and defer if unclear.

### Benchmark baseline-system issues can surface during runs, not during setup

**Mechanism.** Pre-flight gates (code-level trace, schema introspection) verify the candidate accepts the run inputs. But they don't verify the baseline system's production-path robustness. The first B1 baseline attempt exercised real Codex consultation under the benchmark's reasoning_effort and evidence_budget, which tripped a timeout not previously hit.

**Evidence.** The cross-model timeouts were 5 minutes (consult) and 10 minutes (delegate) for months prior. The first benchmark run triggered a timeout because high reasoning effort + complex dialogues push into the 10-15 minute range. The fix was `47713384`.

**Implication.** A benchmark first-run is itself a gate — it exposes production-path edge cases that unit tests and routine usage don't hit. Plan for the first run of each row to potentially trigger baseline-system fixes. Don't assume the baseline is stable under benchmark conditions.

**Watch for.** Similar issues may surface during B3, B5, or B8 runs. Each row's posture and turn budget stresses the baseline differently. The timeout fix addresses one mode of failure; others may remain latent.

### Infinite regress concern for HEAD-aligned manifest metadata

**Mechanism.** Any manifest field tracking HEAD creates a regress: updating the field creates a new commit, which moves HEAD past the recorded value. The convention tolerates this via semantic reframing — `run_commit` means "last substantive change," not "literal HEAD." The manifest-update commits themselves don't change benchmark-relevant code, so they don't trigger further updates.

**Evidence.** Prior session's `fb2e931b` set `run_commit` to `425f7784` (two commits earlier). This session's updates preserved the same offset pattern.

**Implication.** Treat `run_commit` as a semantic marker, not a HEAD pointer. Only update when a substantive change lands. Accept the 1-2 commit offset as the normal state.

**Watch for.** If future conventions require strict HEAD alignment (e.g., "run_commit == HEAD at Phase 2 start"), the manifest update must happen as the literal last commit before the first run. This requires session discipline — no other edits after the manifest update.

## Next Steps

### 1. Reconcile `run_commit` with current HEAD (optional)

**Dependencies:** None.

**What to do:** Decide whether `8243693b` (reasoning_effort default change) warrants a third `run_commit` update. Factors: (a) the benchmark explicitly sets `reasoning_effort: high` at `manifest.json:12-14`, so the change has no runtime effect on benchmark runs; (b) strict HEAD alignment is a stylistic preference, not a correctness requirement.

**What to read first:** `manifest.json:7-15` — current state. Compare `run_commit` vs the `model_settings.reasoning_effort` value.

**Approach suggestion:** If the user wants strict HEAD alignment, update `run_commit` to whatever HEAD is at the start of the next session. If audit-neutral is fine, leave at `7c283c39`.

**Potential obstacles:** None — single-line edit + commit.

### 2. Rerun B1 baseline on current HEAD in a fresh session

**Dependencies:** Live runtime gate cleared (done), invocations packet intact (confirmed), baseline-system timeout fix in place (done).

**What to do:**
1. Open a new terminal; start a fresh `claude` session
2. Record session ID: `cat ~/.claude/plugins/data/codex-collaboration-inline/session_id`
3. Open `/tmp/benchmark-v1-staging-20260415/invocations.md`; substitute `{run_type}` with `This is a scored benchmark run.` in the B1 baseline invocation
4. Paste the invocation into the fresh session
5. After completion, export transcript + synthesis to `/tmp/benchmark-v1-staging-20260415/B1-baseline-transcript.md` and `B1-baseline-synthesis.md`
6. Record metadata per the template in `invocations.md:237-254`

**What to read first:** `/tmp/benchmark-v1-staging-20260415/invocations.md` (complete invocation strings and metadata template) and operator-procedure.md:168-343 (Phase 2 procedure).

**Potential obstacles:**
- Another cross-model issue may surface (beyond the timeout fix). If so, handle per the same pattern: patch, commit, update run_commit, rerun.
- Session ID availability: if the plugin data file is missing, assign manual label and set `rehearsal: true` for that run.
- Evidence budget overflow: if `evidence_count` > 5, the run is invalid — record `valid: false` and schedule rerun.

### 3. Continue through B1 candidate + B3/B5/B8 pairs

**Dependencies:** B1 baseline valid run complete.

**What to do:** Follow the run order in `invocations.md:208-215`. Each row: fresh session for baseline, fresh session for candidate, no repo writes between them in a pair.

**What to read first:** `invocations.md` (all 8 invocations pre-built) and operator-procedure.md Phase 2 (lines 168-343).

**Potential obstacles:** Repo state drift between runs in a pair. Solution: complete each pair in a single continuous operator session where possible, and avoid committing changes between baseline and candidate.

### 4. Phase 3-5 adjudication and scoring after all 8 runs

**Dependencies:** All 8 runs complete with artifacts in staging.

**What to do:** Follow Phases 3-5 in `operator-procedure.md`. Phase 3 (lines 340-480): claim inventory, labeling, safety, completeness. Phase 4 (lines 497-533): aggregate scoring. Phase 5 (lines 534-655): import from staging, fill `run_timestamp` and `operator`, commit.

**Potential obstacles:** Manual adjudication is the dominant cost (80-160 claim adjudications, 2-4 hours estimated). Row-by-row keeps context fresh. High-signal rows first (B3 safety, B8 supersession).

## In Progress

**Clean stopping point — runtime gate cleared, B1 baseline pending rerun on current HEAD.**

- **Approach:** Runtime gate via MCP schema introspection, followed by paced response to baseline-system fixes as they landed.
- **State:** Complete for gate clearance. B1 baseline pending rerun (first attempt produced a timeout that required the `47713384` fix). All edits committed.
- **Working:** Runtime gate (SCORED). Invocations packet intact. Manifest `run_commit` aligned with the most recent substantive cross-model change.
- **Not working:** Nothing broken. One open question — whether to update `run_commit` to `8243693b` for strict HEAD alignment.
- **Next action:** Open a fresh session, rerun B1 baseline using the package in `invocations.md`. Expect ~5-10 minutes for the dialogue.

## Open Questions

### 1. Should `run_commit` be updated to `8243693b` (reasoning_effort default change)?

**Context:** `8243693b` lowers the default reasoning_effort from `xhigh` to `high`. The benchmark manifest explicitly sets `reasoning_effort: high` at `manifest.json:12-14`, so the effective reasoning effort for benchmark runs is unchanged. But strict HEAD-alignment convention would warrant an update.

**Impact:** Low. A single-line edit + commit. No runtime effect on benchmark runs either way.

**Decision pending until:** Next session. Suggest asking the user or defaulting to "update for audit simplicity" if no blocker.

### 2. Will subsequent B runs (B3, B5, B8) trigger additional baseline-system issues?

**Context:** B1 baseline triggered the timeout fix. Each row exercises the baseline differently: B3 (adversarial, file-level), B5 (evaluative, file-level), B8 (comparative, directory-level decomposition, 8 turns). The 15-minute timeout should accommodate all of them, but other latent issues may exist.

**Impact:** Moderate. Each new fix requires a patch-commit-update-rerun cycle. Budget ~10-15 minutes per incident.

**Decision pending until:** Each run happens. No pre-emptive action warranted.

### 3. Should `scope_envelope` be wired through the candidate skill? (Carried forward)

**Context:** Both gatherer agents support `scope_envelope` but the skill doesn't pass it. Currently classified as "prompt-only" enforcement for both systems, which is v1-compliant but a known fragility.

**Impact:** Low for v1 (procedural enforcement is contract-compliant). Would strengthen scope control if wired through.

**Decision pending until:** After benchmark execution — a nice-to-have, not blocking.

## Risks

### 1. `/tmp/` staging vulnerable to reboot

**Impact:** `/tmp/` may be cleared on reboot. If the machine reboots between runs and before Phase 5 import, all staging artifacts are lost.

**Mitigation:** Complete runs continuously where possible. Back up staging periodically: `cp -r /tmp/benchmark-v1-staging-20260415 ~/benchmark-v1-staging-backup`.

### 2. Baseline-system latent issues may surface during remaining runs

**Impact:** As with B1 baseline's timeout, other rows may expose production-path issues in cross-model. Each incident requires patch → commit → update run_commit → rerun.

**Mitigation:** Time-box incident response. If a baseline fix grows beyond 15 minutes or requires significant logic changes, escalate to the user rather than absorbing into the benchmark session.

### 3. Manual adjudication remains the dominant cost (carried forward)

**Impact:** 4 rows x 2 systems = 8 syntheses, 80-160 individual adjudications, 2-4 hours estimated.

**Mitigation:** Row-by-row adjudication keeps context fresh. High-signal rows first.

### 4. `run_commit` drift if HEAD advances between sessions

**Impact:** If additional commits land between this handoff and the next session, `run_commit` will be behind HEAD. Audit reconstruction requires reading git log, not just the manifest.

**Mitigation:** Next session should reconcile `run_commit` vs HEAD as the first action. Simple single-line edit if reconciliation is needed.

## References

### Commits this session

| Commit | Message | Scope |
|--------|---------|-------|
| `401db4d7` | docs(codex-collaboration): update run_commit to include cross-model timeout fix | Manifest run_commit `425f7784` → `47713384` |
| `bfbaef14` | docs(codex-collaboration): update run_commit to include cross-model dev-dep cleanup | Manifest run_commit `47713384` → `7c283c39` |

User's commits during this session (for context):

| Commit | Message |
|--------|---------|
| `47713384` | fix(cross-model,claude-code-docs): increase Codex subprocess timeout to 15min and fix docs canary rejection |
| `7ddcb418` | fix(cross-model): remove workspace-only context-injection dev dependency |
| `7c283c39` | chore: update uv.lock after cross-model dependency change |
| `8243693b` | chore(cross-model): lower default reasoning_effort from xhigh to high |

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| Supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Acceptance authority |
| Benchmark contract (v1) | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Benchmark authority |
| Operator procedure | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | Execution procedure |
| Manifest | `docs/benchmarks/dialogue-supersession/v1/manifest.json` | Corpus and run conditions |

### Staging artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Invocations packet | `/tmp/benchmark-v1-staging-20260415/invocations.md` | Ready (no edits this session) |
| Staging directory | `/tmp/benchmark-v1-staging-20260415/` | Created (prior session), intact |
| B1 baseline artifacts | — | Not yet produced |

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-15_22-38_t04-execution-mode-gate-cleared-invocations-prepared.md`
- Prior: `docs/handoffs/archive/2026-04-15_21-45_t04-benchmark-v1-phase1-complete-ready-for-execution.md`
- Prior: `docs/handoffs/archive/2026-04-15_21-11_t04-rc4-resolved-posture-and-turn-budget-wired-through-candidate.md`
- Prior: `docs/handoffs/archive/2026-04-15_19-30_t04-benchmark-v1-scaffold-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-15_15-00_t04-ac4-closed-benchmark-v1-contract-rewrite.md`
- Prior (earlier arc): see `2026-04-14_*` handoffs in archive

## Gotchas

### MCP schema introspection vs `ToolSearch` deferred tools

**Symptom:** The codex-collaboration MCP tools are listed as "deferred" in the system reminder — they're not immediately in the tool list. Fetching them requires `ToolSearch` with `select:<tool_name>`.

**Root cause:** Deferred tools save context window space. They load on demand when needed.

**Prevention:** Use `ToolSearch` with `select:<exact_tool_name>` to fetch schema for named tools. Or use keyword search when unsure of the exact name.

### `run_commit` updates themselves advance HEAD

**Symptom:** After updating `run_commit` and committing, HEAD is ahead of the recorded `run_commit` by exactly one commit.

**Root cause:** The manifest update creates a new commit, which becomes the new HEAD.

**Prevention:** Accept the 1-2 commit offset as the convention. `run_commit` means "last substantive benchmark-relevant change," not "literal HEAD."

### Baseline first-run surfaces latent timeout issues

**Symptom:** B1 baseline first attempt timed out. Pre-flight gates did not catch this — it required an actual dialogue run.

**Root cause:** High reasoning effort + complex dialogues push completion times into the 10-15 minute range, exceeding the old 5-minute consult and 10-minute delegate timeouts.

**Prevention:** Expect first-run of each benchmark row to potentially expose latent baseline-system issues. Budget time for patch-commit-update-rerun cycles. Do not assume the baseline is stable under benchmark conditions just because it passes routine usage.

### Reasoning effort default change is benchmark-neutral only because of explicit override

**Symptom:** The `8243693b` commit changes the cross-model default reasoning_effort from `xhigh` to `high`, which looks like it might affect the benchmark.

**Root cause:** The benchmark manifest explicitly sets `reasoning_effort: high` at `manifest.json:12-14`. The override takes precedence, making the default change neutral.

**Prevention:** When reviewing cross-model changes during benchmark execution, always check whether the change is overridden by `manifest.json`'s `model_settings`. If overridden, the change is benchmark-neutral. If not, assess carefully.

## Conversation Highlights

### User constraint on runtime gate session usage

User: "One important constraint: do not reuse the current gate-check session for a benchmark run. The procedure requires each run to happen in a fresh Claude session."

Cited operator-procedure.md:166 (scored gate) and :174 (fresh-session rule). Reinforced that gate and run are distinct operational events, not combinable.

### User's first cross-model fix notification

User: "The cross-model dialogue run (B1 baseline) encountered an issue that required updates to the cross-model plugin. so the commit SHA changed."

Concise, factual. Implicit ask: investigate the change and assess benchmark impact.

### User's first run_commit update directive

User: "The B1 baseline needs to be rerun - I just made the changes and committed them. Update the `run_commit` field in the benchmark artifacts."

Two parallel directives in one message: (1) B1 baseline status (pending rerun); (2) update the manifest. Direct, actionable.

### User's second cross-model change notification

User: "I made further changes to the cross-model plugin so the commit SHA changed again"

Same pattern — concise notification, implicit ask to assess and potentially update manifest.

### User's second run_commit update directive

User: "commit this change"

Minimal directive. Consistent with prior pattern — update manifest, commit, continue.

### User's handoff request

User: "save a handoff. we'll pick up from here in the next session."

Clear request. "We'll pick up from here" signals the next session should continue Phase 2 execution, not rescope.

## User Preferences

### Concise notifications with implicit assessment ask (pattern observed this session)

User reports code changes as brief factual statements ("commit SHA changed"). The implicit ask is: assess the change against the benchmark's validity, surface impact, recommend action. This session, my response pattern was: diff → classify (runtime/neutral) → recommend (update run_commit) → act on confirmation.

### Direct action directives (pattern observed this session)

User switches from notification to directive with minimal ceremony: "Update the `run_commit` field" / "commit this change." Response pattern: execute, verify, report briefly.

### Procedure adherence is strict (carried from prior sessions)

User enforces operator procedure sequencing even when code evidence is strong. The prior session's P1 review finding (hardcoded SCORED mode) demonstrated this. This session reinforced via the fresh-session constraint — even a clearly cleared gate must not be combined with a run.

### Honest documentation over false confidence (carried from prior sessions)

Parameterized `{run_type}` over hardcoded "scored" is the prior-session example. This session: I flagged `8243693b` as an open question rather than proactively updating `run_commit`, consistent with "state what's known, defer what's uncertain."

### Pre-work with citations (carried from prior sessions)

User independently identifies file:line references in conversation. This session the user cited operator-procedure.md:166 and :174 in confirming the runtime gate and fresh-session rule. Expected response style: match citation precision when referencing code.

### Structured review findings (carried from prior sessions)

Prior sessions established that when the user provides review findings, they use priority (P1/P2/P3), confidence, title, body, file:line. This session did not have review findings — but the pattern is carried forward as a norm to expect.

### Contract text is authoritative (carried from prior sessions)

The distinction between "run conditions" and "field timing" is enforced exactly per contract text. This session: the semantics of "run_commit" as "last substantive benchmark-relevant change" (not "literal HEAD") comes from the contract-like treatment of the field.

### Collaborative peer, not passive executor (global preference)

From `~/.claude/CLAUDE.md`: "Be a collaborative peer, not a passive executor." This session's balance: I acted directly on explicit directives (run_commit updates, commits) but raised open questions when uncertainty warranted (`8243693b` as a third update candidate). The user's phrasing of directives (short, actionable) indicates trust in direct action.
