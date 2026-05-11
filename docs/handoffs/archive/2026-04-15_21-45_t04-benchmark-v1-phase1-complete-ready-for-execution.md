---
date: 2026-04-15
time: "21:45"
created_at: "2026-04-16T01:45:35Z"
session_id: 1ae919e0-3bba-4026-817a-7a718edd428f
resumed_from: docs/handoffs/archive/2026-04-15_21-11_t04-rc4-resolved-posture-and-turn-budget-wired-through-candidate.md
project: claude-code-tool-dev
branch: main
commit: fb2e931b
title: "T-04 benchmark v1 Phase 1 complete — ready for scored execution"
type: handoff
files:
  - docs/benchmarks/dialogue-supersession/v1/manifest.json
  - docs/benchmarks/dialogue-supersession/v1/operator-procedure.md
  - docs/benchmarks/dialogue-supersession/v1/summary.md
  - docs/benchmarks/dialogue-supersession/v1/runs.json
---

# T-04 Benchmark v1 Phase 1 Complete — Ready for Scored Execution

## Goal

Complete Phase 1 (Pre-Run Setup) of the dialogue supersession benchmark v1 operator procedure, resolving all prerequisites for scored execution.

**Trigger.** Resumed from `2026-04-15_21-11` handoff. The prior session resolved RC4 (posture and turn-budget wired through the candidate system) and identified scored benchmark execution as the next step. This session handles the Phase 1 setup checklist that the operator procedure requires before any runs begin.

**Stakes.** AC-5 requires "The benchmark contract is executed on the fixed corpus." Phase 1 is the gate between having a runnable benchmark and actually executing it. Without completing Phase 1, no runs (scored or rehearsal) can begin.

**Success criteria achieved this session:**

1. Stale section 2.3 in operator procedure fixed (candidate now uses `-p`/`-n` flags).
2. `codex_model` and `reasoning_effort` recorded in `manifest.json`.
3. `run_commit` recorded in `manifest.json` pointing to `425f7784` (the commit with all fixes).
4. All Phase 1 prerequisite checks verified or delegated to fresh-session confirmation.
5. External staging directory confirmed at `/tmp/benchmark-v1-staging-20260415`.

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
| **2026-04-15 21:45 (this)** | **Phase 1 complete — ready for scored execution** | **`425f7784`, `fb2e931b` on `main`** |
| Next | Execution mode gate + Phase 2 (per-row execution) | |

## Session Narrative

**Phase 1 — Handoff load and orientation (~5 min).**

Loaded the `2026-04-15_21-11` handoff. The prior session had completed the RC4 implementation (posture and turn-budget wired through the entire candidate stack) and identified scored benchmark execution as the immediate next step. The handoff's Next Steps section listed two items: (1) execute benchmark v1 in scored mode, and (2) after AC-5, record results and make retirement decision.

Summarized the handoff state: AC-1 through AC-4 done, AC-5 unblocked, branch clean on main at `afa55eac`, 586 tests passing. Offered to continue with scored benchmark execution.

**Phase 2 — User's pre-work and Phase 1 decomposition (~10 min).**

User provided a detailed decomposition of the operator procedure's pre-execution requirements, having already performed most Phase 1 checks independently. Their analysis identified three pre-execution stages:

1. T4-BR-07 Prerequisites at `operator-procedure.md:27` — comparability, scope/evidence controls, artifact directory, adjudicator availability.
2. Phase 1: Pre-Run Setup at `operator-procedure.md:62` — commit fixing, model settings, plugin verification, corpus path verification, staging directory.
3. Execution Mode Gate at `operator-procedure.md:146` — candidate `-p`/`-n` acceptance confirmation.

User reported the following Phase 1 checks already passing: git state clean on main at `afa55eac`, benchmark artifact set present, `manifest.json` has scope/evidence controls, `dialogue_timeout` is `1200`, all corpus paths exist, repo evidence for `-p`/`-n` in both skills and the candidate MCP/runtime stack. User had also created the staging directory at `/tmp/benchmark-v1-staging-20260415`.

User identified remaining items needing action: `run_commit` in manifest, `codex_model` and `reasoning_effort` in manifest, fresh-session plugin verification, fresh-session execution mode gate, human adjudicator confirmation, and `BENCH_STAGING` environment variable.

User also provided a correction to the prior handoff: `run_timestamp` and `operator` are Phase 5 fields (at `operator-procedure.md:614`), not Phase 1.

**Phase 3 — Stale section discovery and fix (~10 min).**

Read the manifest and full operator procedure (718 lines across multiple reads). Discovered a critical stale instruction: section 2.3 (Run the candidate) at lines 282-294 still said "The candidate skill does not accept `-p` or `-n` flags" and instructed operators to rely on prompt-only posture. This was written during the scaffold session before RC4 was resolved.

The staleness was dangerous: an operator following section 2.3 literally would run the candidate without `-p`/`-n` flags, producing posture/budget asymmetry that invalidates the run under RC4. The Quick Reference table at line 707 was already correct (updated during RC4), so only section 2.3 was stale.

Created branch `chore/benchmark-v1-phase1-prep`, fixed section 2.3 to mirror section 2.2's invocation pattern (symmetric `-p <posture> -n <turn_budget>` for both systems), updated `codex_model` to `gpt-5.4` and `reasoning_effort` to `high` in manifest. Committed and merged to main at `425f7784`.

**Phase 4 — run_commit recording and self-reference resolution (~5 min).**

Addressed the `run_commit` self-reference problem: manifest.json records a commit SHA, but writing that SHA into manifest creates a new commit, changing the SHA. The convention adopted: `run_commit` points to `425f7784` (the commit containing all the actual fixes, model settings, and corrected procedure). The HEAD at `fb2e931b` only differs by having that SHA written into the manifest. Both commits contain identical code, procedure, and settings. Runs execute against HEAD.

Created branch `chore/benchmark-v1-run-commit`, wrote `run_commit: "425f7784"`, committed with explanatory message, merged to main at `fb2e931b`.

**Phase 5 — Plugin verification and environment setup (~5 min).**

User ran `/reload-plugins` which reported: "26 plugins · 15 skills · 40 agents · 23 hooks · 5 plugin MCP servers · 3 plugin LSP servers." Both `cross-model:dialogue` and `codex-collaboration:dialogue` appeared in the session's skill list. This satisfied Phase 1.3 (plugin availability verification) without requiring a fresh session — `/reload-plugins` confirms plugins load correctly, which is the purpose of the 1.3 check.

Distinguished this from Phase 2.0's fresh-session requirement: Phase 1.3 is a verification check (are plugins installed?), while Phase 2.0 is a contamination control (no conversation-history carryover between runs, per RC6).

User corrected the execution mode gate approach: the gate should not wait for the first candidate scored run. Per `operator-procedure.md:146-166`, candidate `-p`/`-n` acceptance should be verified in a fresh session before Phase 2 starts, because failing it flips the entire benchmark into REHEARSAL.

**Phase 6 — Environment variable issue (~5 min).**

User ran `! export BENCH_STAGING=/tmp/benchmark-v1-staging-20260415` to set the staging directory. Subsequent verification via both the `!` prefix and the Bash tool showed the variable was not set. Root cause: the `!` prefix in Claude Code runs commands in a subshell — `export` sets the variable in the child process, which dies on exit, never propagating back to the parent shell.

Resolution: user should set `BENCH_STAGING` directly in their terminal (outside Claude Code) before launching fresh benchmark sessions, or simply use the literal path `/tmp/benchmark-v1-staging-20260415` when saving artifacts. The env var is a convenience, not a requirement.

## Decisions

### Decision 1: `/reload-plugins` satisfies Phase 1.3 (plugin availability)

**Choice:** Accept `/reload-plugins` output as sufficient evidence that both dialogue skills are installed and callable, without requiring a separate fresh session for Phase 1.3.

**Driver:** The purpose of the Phase 1.3 "fresh session" check is to confirm plugins load correctly — `/reload-plugins` achieves the same thing by reloading all plugins in the current session and reporting their count.

**Alternatives considered:**
- **Fresh session for 1.3 specifically** — would require starting a new Claude Code session just to check plugin availability, then another fresh session for the execution mode gate, then more fresh sessions for each run. Unnecessary overhead given `/reload-plugins` provides the same information.

**Trade-offs accepted:** We verified presence (skills appear in the list) but not full invocation (we didn't actually run either skill). The execution mode gate in the next fresh session will provide the invocation test as a natural side effect.

**Confidence:** High (E2) — `/reload-plugins` reported both skills present, and the skill list in the system context confirms both `cross-model:dialogue` and `codex-collaboration:dialogue` are registered.

**Reversibility:** High — if the next fresh session reveals a plugin loading issue, we simply re-verify.

**Change trigger:** If `/reload-plugins` ever shows a discrepancy with actual fresh-session behavior.

### Decision 2: Execution mode gate is a pre-run gate, not a mid-matrix discovery

**Choice:** Verify candidate `-p`/`-n` acceptance in a fresh session before Phase 2 starts, rather than discovering it on the first candidate run.

**Driver:** User corrected the approach: "Per operator-procedure.md:146, you should verify candidate `-p` and `-n` acceptance in a fresh session before Phase 2 starts, because failing that check flips the whole benchmark into REHEARSAL."

**Alternatives considered:**
- **Defer to first candidate run** — the gate would naturally resolve when the first candidate run either accepts or rejects the flags. Rejected because a gate failure after the first baseline run has been completed wastes that baseline run (it would need to be reclassified as rehearsal).

**Trade-offs accepted:** Requires one additional fresh session (the gate verification session) before runs begin. Minor overhead for correctness.

**Confidence:** High (E2) — the procedure is explicit at lines 146-166 about this being a pre-run gate.

**Reversibility:** N/A — this is a procedural sequencing decision, not a design choice.

**Change trigger:** None — this follows the procedure as written.

### Decision 3: `run_commit` self-reference convention

**Choice:** `run_commit` in `manifest.json` points to `425f7784` (the commit with all fixes), not to the commit that contains the `run_commit` value itself (`fb2e931b`). Both commits are code-identical.

**Driver:** Self-referential commit SHA is impossible — writing the SHA creates a new commit, which changes the SHA. The convention is that `run_commit` identifies the code state, and HEAD (`fb2e931b`) is the run commit by convention (it only adds the `run_commit` metadata).

**Alternatives considered:**
- **Leave `run_commit` null until after runs** — deferred recording. Rejected because the procedure says to record it during Phase 1 setup.
- **Use HEAD and accept the one-commit offset** — functionally equivalent to what we did, but without the explanatory commit message.

**Trade-offs accepted:** `run_commit` technically points one commit behind HEAD. The commit message at `fb2e931b` explicitly documents this: "run_commit necessarily points to the prior commit (self-reference is impossible)."

**Confidence:** High (E2) — this is a mathematical impossibility, not a judgment call.

**Reversibility:** High — if the convention is wrong, just update `run_commit` to `fb2e931b`.

**Change trigger:** If an auditor requires `run_commit` to equal the actual HEAD SHA.

## Changes

### `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` (+6/-11)

**Purpose:** Fix stale section 2.3 that still said the candidate does not accept `-p`/`-n` flags.

**Approach:** Replaced the candidate invocation template and surrounding text to mirror section 2.2's symmetric pattern. The old text (lines 287-294) instructed operators to rely on prompt-only posture and record "what actually happened, not what was requested." The new text uses the same invocation pattern as the baseline: `/codex-collaboration:dialogue "<scoped prompt>" -p <posture> -n <turn_budget>` with explicit reference to corpus row values.

**Key detail:** The Quick Reference table at line 707 was already correct (updated during the RC4 session). Only section 2.3 was stale — a reminder that stale instructions can survive alongside correct ones in the same document when updates target different sections.

### `docs/benchmarks/dialogue-supersession/v1/manifest.json` (+3/-3)

**Purpose:** Fill Phase 1 model settings and benchmark commit.

**Approach:** Three null fields updated:
- `codex_model`: `"gpt-5.4"` (user-provided)
- `reasoning_effort`: `"high"` (user-provided)
- `run_commit`: `"425f7784"` (recorded after the fix commit, pointing to the commit that contains all fixes)

**Key detail:** `run_timestamp` and `operator` remain null — these are Phase 5 fields per `operator-procedure.md:614`, not Phase 1 inputs. The prior handoff incorrectly suggested they might be Phase 1 fields; the user corrected this.

## Codebase Knowledge

### Operator procedure structure (718 lines total)

| Section | Lines | Purpose |
|---|---|---|
| Scoring Prerequisites | 14-25 | RESOLVED status of RC4 blockers |
| T4-BR-07 Prerequisites | 27-37 | Four pre-run gate items |
| Run Condition Status | 39-60 | 11 run conditions with status |
| Phase 1: Pre-Run Setup | 62-144 | Commit, model settings, plugins, corpus paths, staging |
| Execution Mode Gate | 146-166 | Pre-run check for candidate `-p`/`-n` acceptance |
| Phase 2: Per-Row Execution | 168-343 | Session isolation, prompt construction, baseline/candidate runs, metadata |
| Phase 3: Adjudication | 345-480 | Claim inventory, labeling, safety, completeness, scope compliance |
| Benchmark-Wide Mode | 482-495 | Recompute SCORED vs REHEARSAL from all runs |
| Phase 4: Aggregate Scoring | 497-533 | Metrics, pass rule (3 conditions) |
| Phase 5: Import and Finalize | 534-655 | Import from staging, assemble JSON, write summary, commit |
| Invalidation and Reruns | 656-674 | When/how to rerun |
| Known Limitations | 683-696 | Prompt-only scope enforcement |
| Quick Reference | 698-717 | Summary table |

### Key sections for next session

**Section 2.0 Session isolation (lines 174-197):** Each run MUST execute in a fresh Claude Code session. For scored runs, obtain canonical host session ID. If unavailable, reclassify to rehearsal.

**Section 2.1 Scoped prompt construction (lines 199-258):** Two templates — one for B1/B3/B5 (file-level anchors), one for B8 (directory-level anchored decomposition with groups). Scope instructions are identical for baseline and candidate except `max_evidence` (5 vs 15).

**Section 2.2 Baseline invocation (lines 260-280):**
```
/cross-model:dialogue "<scoped prompt>" -p <posture> -n <turn_budget>
```

**Section 2.3 Candidate invocation (lines 282-300, now fixed):**
```
/codex-collaboration:dialogue "<scoped prompt>" -p <posture> -n <turn_budget>
```

**Section 2.4 Run metadata (lines 305-337):** JSON template for each run including `rehearsal`, `session_id_canonical`, `effective_posture`, `effective_turn_budget`.

### Corpus rows from manifest

| Row | Type | Posture | Budget | Evidence (baseline/candidate) |
|---|---|---|---|---|
| B1 | Architecture review | evaluative | 6 | 5/15 |
| B3 | Code review | adversarial | 6 | 5/15 |
| B5 | Policy audit | evaluative | 6 | 5/15 |
| B8 | Supersession analysis | comparative | 8 | 5/15 |

B8 has special `allowed_roots_groups` decomposition with 3 groups (baseline evidence path, candidate normative surface, candidate runtime surface).

### Manifest state after this session

| Field | Value | Phase |
|---|---|---|
| `run_commit` | `425f7784` | Phase 1 |
| `codex_model` | `gpt-5.4` | Phase 1 |
| `reasoning_effort` | `high` | Phase 1 |
| `dialogue_timeout` | `1200` | Pre-existing |
| `run_timestamp` | `null` | Phase 5 |
| `operator` | `null` | Phase 5 |

### Execution flow for the next session

```
Fresh session #1: Execution mode gate
  → Verify /codex-collaboration:dialogue accepts -p and -n
  → If pass → SCORED mode
  → If fail → REHEARSAL mode (all runs)

Fresh session #2: B1 baseline
  → /cross-model:dialogue "<B1 scoped prompt>" -p evaluative -n 6
  → Save transcript + synthesis to $BENCH_STAGING/B1-baseline-*
  → Record metadata

Fresh session #3: B1 candidate
  → /codex-collaboration:dialogue "<B1 scoped prompt>" -p evaluative -n 6
  → Save transcript + synthesis to $BENCH_STAGING/B1-candidate-*
  → Record metadata

[Repeat for B3, B5, B8 — 6 more sessions]

Adjudication session: Phase 3
  → Claim inventory, labeling, safety, completeness, scope compliance
  → All from $BENCH_STAGING files

Scoring session: Phase 4 (if SCORED)
  → Aggregate metrics, pass rule evaluation

Import session: Phase 5
  → Import everything from staging to repo
  → Fill run_timestamp, operator
  → Commit
```

## Context

### T-04 acceptance criteria status after this session

| AC | Description | Status | Evidence |
|---|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) | `skills/dialogue/SKILL.md` |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) | `agents/dialogue-orchestrator.md` |
| 3 | Gatherer agents exist and use Claude-side tools | Done (PR #107) | Both agents with Glob/Grep/Read |
| 4 | Synthesis with bounded citations and convergence | Done | Dialogue-tier citations + `converged: false` terminal artifact |
| 5 | Benchmark contract executed on fixed corpus | **Phase 1 complete; execution next** | Manifest filled, procedure fixed, staging ready |
| 6 | Benchmark result recorded with per-task metrics | **Open** | Depends on AC-5 |
| 7 | Context-injection retirement decision explicit | **Open** | Depends on AC-6 |

### Mental model for this session

This session is a **pre-flight checklist** — methodical verification that all prerequisites are satisfied before committing to the expensive multi-session benchmark execution. The operator procedure is highly prescriptive (718 lines) because benchmark integrity depends on procedure adherence — any deviation (wrong commit, reused session, missing flags, unchecked scope) can invalidate runs.

The key insight this session produced: the operator procedure itself had a stale instruction that would have caused a run-invalidating error (section 2.3). Pre-flight verification caught it before it could affect actual runs.

### Open tickets

| Ticket | ID | Status | Next |
|---|---|---|---|
| Dialogue parity & scouting retirement | T-04 | Open (AC 1-4 done, Phase 1 complete) | Execution mode gate → Phase 2 |
| Execution-domain foundation | T-05 | Open (unstarted) | Separate workstream |
| Promotion flow & delegate UX | T-06 | Open (blocked by T-05) | — |
| Analytics reviewer & cutover | T-07 | Open | Separate workstream |

## Learnings

### Stale instruction sections survive alongside correct ones

**Mechanism.** The RC4 session updated the Scoring Prerequisites section, the Run Condition Status table, and the Quick Reference table — but missed section 2.3's invocation instructions. The document had both correct information (Quick Reference: "candidate `/dialogue` (`-p` posture, `-n` turn budget)") and stale information (section 2.3: "The candidate skill does not accept `-p` or `-n` flags") simultaneously.

**Evidence.** Section 2.3 at lines 287-294 retained pre-RC4 text. Quick Reference at line 707 was already updated. Both existed in the same document after the RC4 commits (`52a968e9`–`afa55eac`).

**Implication.** When updating a procedure document after a capability change, grep for all references to the changed capability across the entire document. Summary tables (Quick Reference) and operational sections (Phase 2 invocation) update independently — fixing one doesn't fix the other.

### `/reload-plugins` is sufficient for plugin availability verification but not session isolation

**Mechanism.** `/reload-plugins` reloads all plugin definitions and reports counts. Both dialogue skills appeared in the post-reload skill list, confirming installation and registration. However, it does not create a fresh conversation context — prior conversation history remains, which would violate RC6 (no supplemental context carryover between runs).

**Evidence.** Output: "26 plugins · 15 skills · 40 agents · 23 hooks · 5 plugin MCP servers · 3 plugin LSP servers." Both `cross-model:dialogue` and `codex-collaboration:dialogue` present in skill list.

**Implication.** For verification checks (are things installed?), `/reload-plugins` works. For contamination controls (are sessions isolated?), only fresh sessions suffice. Don't conflate the two purposes.

### `! export VAR=value` in Claude Code does not persist

**Mechanism.** The `!` prefix in Claude Code runs commands in a subshell. `export` sets the variable in the child process, which exits immediately, never propagating the variable to the parent shell. The Bash tool also runs in independent subprocesses that don't share the interactive shell's environment.

**Evidence.** `! export BENCH_STAGING=/tmp/benchmark-v1-staging-20260415` completed without error but `! echo $BENCH_STAGING` produced no output.

**Implication.** For environment variables needed across benchmark sessions, set them directly in the terminal (outside Claude Code) or use literal paths instead.

### `run_commit` self-reference is mathematically impossible

**Mechanism.** Writing a commit SHA into a tracked file creates a new commit with a different SHA. The file can never contain its own commit's SHA.

**Evidence.** Commit `425f7784` contains all fixes but `run_commit: null`. Commit `fb2e931b` contains `run_commit: "425f7784"` — pointing to the prior commit, not itself.

**Implication.** The convention is that `run_commit` points to the code-authoritative commit. HEAD (`fb2e931b`) is the actual run commit; it differs from `run_commit` only by the metadata recording. Both are code-identical.

## Next Steps

### 1. Execute the execution mode gate in a fresh session

**Dependencies:** None — Phase 1 is complete.

**What to do:**
1. Open a new terminal or tab
2. Set `export BENCH_STAGING=/tmp/benchmark-v1-staging-20260415` (or use the literal path)
3. Start a fresh `claude` session
4. Verify `/codex-collaboration:dialogue` accepts `-p` and `-n` flags (e.g., a quick test invocation or confirmation from the skill's help output)
5. If both pass → SCORED mode for all subsequent runs
6. If either fails → REHEARSAL mode

**What to read first:** `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md:146-166` — the execution mode gate section.

**Potential obstacles:** If the candidate skill rejects `-p` or `-n` at runtime despite the repo evidence showing support, the entire benchmark switches to REHEARSAL. The repo evidence is strong (MCP schema, resolver, skill frontmatter), so this is unlikely.

### 2. Begin Phase 2 per-row execution starting with B1 baseline

**Dependencies:** Execution mode gate (#1) must pass as SCORED.

**What to do:**
1. Fresh session for B1 baseline
2. Construct scoped prompt using template from `operator-procedure.md:208-226`:
   - Allowed paths: `docs/superpowers/specs/codex-collaboration/contracts.md`, `docs/superpowers/specs/codex-collaboration/delivery.md`, `packages/plugins/codex-collaboration/server/mcp_server.py`
   - Evidence budget: 5 (baseline)
   - Posture: evaluative
   - Run type: "This is a scored benchmark run." (or "rehearsal" if gate failed)
3. Invoke: `/cross-model:dialogue "<scoped prompt>" -p evaluative -n 6`
4. Save transcript + synthesis to `$BENCH_STAGING/B1-baseline-*`
5. Record run metadata

**What to read first:** `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md:168-343` — full Phase 2 procedure.

**Potential obstacles:** Session ID availability for RC6. The procedure requires canonical host session ID for scored runs. If unavailable, the run is forced to rehearsal. The procedure suggests checking the status bar or `~/.claude/session_id`.

### 3. (After all 8 runs) Adjudicate, score, and finalize

**Dependencies:** All 8 runs (4 rows × 2 systems) complete with artifacts in staging.

**What to do:** Follow Phases 3-5 in the operator procedure. Phase 3: claim inventory, labeling, safety, completeness, scope compliance for all 8 syntheses. Phase 4: aggregate scoring (if SCORED). Phase 5: import from staging, fill summary, commit.

**Potential obstacles:** Manual adjudication is the dominant cost — 80-160 individual claim adjudications estimated at 2-4 hours. High-signal rows first (B3 safety, B8 supersession).

## In Progress

**Clean stopping point — Phase 1 complete, ready for execution mode gate.**

- **Approach:** Methodical Phase 1 checklist execution following the operator procedure.
- **State:** Complete. Two commits on main (`425f7784`, `fb2e931b`). Manifest filled, procedure fixed, staging created, plugins verified.
- **Working:** All Phase 1 checks pass. Repo is clean on main.
- **Not working:** Nothing broken.
- **Next action:** Start a fresh session, run the execution mode gate, then begin B1 baseline if SCORED.

## Open Questions

### 1. What is the canonical way to obtain a Claude Code session ID?

**Context:** The operator procedure requires a canonical host session ID for scored runs (RC6). If unavailable, the run is forced to rehearsal. The procedure suggests checking the status bar or `! cat ~/.claude/session_id`, but these paths are not guaranteed.

**Impact:** If no canonical session ID is reliably available, scored runs may be impossible to audit for RC6, making all runs effectively rehearsal.

**Decision pending until:** The execution mode gate session — test whether a canonical session ID is obtainable.

### 2. Should `scope_envelope` be wired through the candidate skill?

**Context:** Both gatherer agents support `scope_envelope` but the skill doesn't pass it. Currently classified as "prompt-only" enforcement for both systems, which is v1-compliant but a known fragility.

**Impact:** Low for v1 (procedural enforcement is contract-compliant). Would strengthen scope control story if wired through.

**Decision pending until:** After benchmark execution — a nice-to-have, not blocking.

## Risks

### 1. Prompt-only scope enforcement is fragile

**Impact:** Neither system mechanically prevents out-of-scope scouting during benchmark runs. A scouting step that ignores the prompt instruction will only be caught during transcript review, not at runtime.

**Mitigation:** Contract-compliant for v1 (procedural enforcement provision at contract lines 177-183). Each violation invalidates the run and requires a rerun.

### 2. Manual adjudication is the dominant benchmark cost

**Impact:** 4 rows × 2 systems = 8 syntheses, each requiring claim inventory, labeling, safety review, and second-pass completeness review. At ~10-20 claims per synthesis: 80-160 individual adjudications (~2-4 hours).

**Mitigation:** Row-by-row adjudication keeps context fresh. High-signal rows first (B3 safety, B8 supersession).

### 3. Session ID availability for scored runs

**Impact:** If canonical session IDs cannot be reliably obtained, all runs default to REHEARSAL per the procedure, and AC-5 through AC-7 remain open.

**Mitigation:** Test in the execution mode gate session before committing to the full run matrix.

## References

### Commits this session

| Commit | Message | Scope |
|---|---|---|
| `425f7784` | fix(codex-collaboration): update benchmark procedure for RC4 and record model settings | Section 2.3 fix + codex_model + reasoning_effort |
| `fb2e931b` | docs(codex-collaboration): record benchmark v1 run_commit | run_commit: 425f7784 in manifest |

### Authority documents

| Document | Location | Role |
|---|---|---|
| Supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Acceptance authority |
| Benchmark contract (v1) | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Benchmark authority |
| Operator procedure | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | Execution procedure |
| Benchmark readiness | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/benchmark-readiness.md` | Prerequisite gate |

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-15_21-11_t04-rc4-resolved-posture-and-turn-budget-wired-through-candidate.md`
- Prior: `docs/handoffs/archive/2026-04-15_19-30_t04-benchmark-v1-scaffold-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-15_15-00_t04-ac4-closed-benchmark-v1-contract-rewrite.md`
- Prior: `docs/handoffs/archive/2026-04-14_23-30_t04-gatherer-implementation-merged-and-e2e-smoke-run.md`
- Prior: `docs/handoffs/archive/2026-04-14_22-45_t04-gatherer-plan-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_20-17_t04-v1-e2e-verified-pr-106-open.md`
- Prior: `docs/handoffs/archive/2026-04-14_16-30_t04-v1-four-production-surfaces-authored-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-14_12-55_t04-v1-section-10-authoring-decisions-resolved-and-committed.md`

## Gotchas

### `! export` in Claude Code does not persist environment variables

**Symptom:** `! export BENCH_STAGING=/tmp/...` completes without error but the variable is not set in any subsequent command.

**Root cause:** The `!` prefix runs commands in a subshell. `export` sets the variable in the child process, which exits immediately without propagating to the parent shell. The Bash tool also uses independent subprocesses.

**Prevention:** Set environment variables directly in the terminal (outside Claude Code) or use literal paths.

### Stale operator procedure sections after capability changes

**Symptom:** Section 2.3 said candidate doesn't accept `-p`/`-n` while Quick Reference correctly showed it does.

**Root cause:** RC4 implementation updated summary sections (Scoring Prerequisites, Run Condition Status, Quick Reference) but missed operational sections (Phase 2 invocation instructions). Independent sections update independently.

**Prevention:** After capability changes, grep the entire procedure document for references to the changed capability. Grep targets: the capability name, any synonyms, and any negation of the capability.

### `run_commit` self-reference is impossible

**Symptom:** `run_commit` in manifest.json cannot contain the SHA of the commit that contains it.

**Root cause:** Writing a SHA into a tracked file creates a new commit with a different SHA.

**Prevention:** Convention: `run_commit` points to the code-authoritative commit. HEAD is the actual run commit. Both are code-identical. Document this in the commit message.

## Conversation Highlights

### User's thorough pre-work

User independently performed most Phase 1 checks before the session, providing detailed line-number citations for each check and its result. This included reading the operator procedure structure, verifying git state, checking all corpus paths, creating the staging directory, and identifying the specific remaining items.

### User's correction on execution mode gate timing

User corrected the proposed approach of deferring the execution mode gate to the first candidate run: "The execution-mode gate should not wait for the first candidate scored run. Per operator-procedure.md:146, you should verify candidate `-p` and `-n` acceptance in a fresh session before Phase 2 starts, because failing that check flips the whole benchmark into REHEARSAL."

### User's correction on `run_timestamp` and `operator` timing

User noted: "One correction to the archived handoff: `run_timestamp` and `operator` are not Phase 1 fields. The current procedure fills those later in Phase 5 at operator-procedure.md:614."

## User Preferences

### Procedure adherence is strict

User treats the operator procedure as authoritative and enforces its sequencing. The execution mode gate correction demonstrates this: even when the outcome is predictable (repo evidence strongly suggests the gate passes), the procedure says to verify pre-run, so it must be verified pre-run.

### Pre-work with citations

User independently performs preparatory work with specific file:line citations, presenting results in structured tables. They expect the same citation precision in return.

### Contract text is authoritative (carried from prior sessions)

Run condition 4 vs. 5 distinction enforced exactly. Paraphrasing or extending contract provisions beyond their literal scope is rejected.

### Honest documentation over false confidence (carried from prior sessions)

The "prompt-only" scope enforcement label and the `run_commit` self-reference convention documentation are both instances — state what's true, don't rationalize limitations.
