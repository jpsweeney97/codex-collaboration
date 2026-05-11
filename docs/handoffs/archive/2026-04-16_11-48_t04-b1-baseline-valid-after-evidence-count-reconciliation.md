---
date: 2026-04-16
time: "11:48"
created_at: "2026-04-16T15:48:26Z"
session_id: ca75293e-7d93-4917-b1cb-4dff59b52c15
resumed_from: docs/handoffs/archive/2026-04-16_00-18_t04-runtime-gate-cleared-b1-baseline-pending-rerun.md
project: claude-code-tool-dev
branch: main
commit: fa75111b
title: "T-04 B1 baseline valid after evidence_count reconciliation and operator-procedure amendment"
type: handoff
files:
  - docs/benchmarks/dialogue-supersession/v1/manifest.json
  - docs/benchmarks/dialogue-supersession/v1/operator-procedure.md
  - /private/tmp/benchmark-v1-staging-20260415/B1-baseline-metadata.json
---

# T-04 B1 Baseline Valid After evidence_count Reconciliation and Operator-Procedure Amendment

## Goal

Move T-04 from "gate cleared" to "B1 pair valid" by (a) reconciling `run_commit` against any cross-model changes landed since the last handoff, (b) reviewing the B1 baseline run the user produced between sessions, (c) resolving any metadata/contract mismatches uncovered by the review, and (d) prepping the B1 candidate package for a fresh session.

**Trigger.** Resumed from `2026-04-16_00-18` handoff, which recorded the runtime gate cleared but flagged B1 baseline as "pending rerun after cross-model updates" because the first attempt hit a subprocess hang that forced `47713384` (timeout bump to 15 min). Between that handoff and this session the user re-ran B1 baseline and invoked `/handoff:load` to resume — so the session opened with an unreviewed baseline run sitting in `/private/tmp/benchmark-v1-staging-20260415/`.

**Stakes.** AC-5 in the T-04 ticket requires "benchmark contract executed on fixed corpus" — that means every B row must produce valid paired runs. A baseline run with contested `valid` status (due to apparent evidence-budget overflow) would either force a rerun (costing another full dialogue cycle and potentially masking the comparison's fidelity) or would leave an unresolved ambiguity in the adjudication phase. Either outcome propagates into Phase 4 aggregate scoring and Phase 5 import.

**Success criteria:**
1. `run_commit` reflects the latest materially benchmark-relevant baseline-system change
2. B1 baseline `valid` status determined per contract, with any metadata corrections committed to staging
3. Any definitional ambiguity exposed by the review is closed via operator-procedure clarification (not contract change), so B3/B5/B8 don't relitigate it
4. B1 candidate invocation package prepped for a fresh session with operator-ready steps
5. Clean commit state on `main`; no uncommitted work

**Connection to project arc.** This is the empirical gate for the codex-collaboration supersession (cross-model dialogue+context-injection retirement). T-04 is the last T-sequence item before retirement decisions (AC-7) and downstream tickets (T-05, T-06, T-07). This session moves from "gate cleared" through "B1 baseline valid" — **1 of 4 paired rows toward AC-5 completion**.

## Session Narrative

**Phase 1 — Handoff load and run_commit reconciliation check (~5 min).**

Loaded the `2026-04-16_00-18` handoff. Prior Open Question #1 asked whether `run_commit` should advance from `7c283c39` to `8243693b` (reasoning_effort default change — benchmark-neutral because the benchmark manifest explicitly overrides). User responded: "update run_commit — it may actually be a more recent commit than 8243693b, it's worth checking." Running `git log --oneline -10` surfaced a new commit `693551cc — fix(cross-model): close codex subprocess stdin in consult and delegate`, landed 10:59 local (between handoff save at 00:18 and session start).

Inspected via `git show --stat 693551cc`: 2 files, 11 insertions, adding `stdin=subprocess.DEVNULL` to Popen calls in `codex_consult.py` and `codex_delegate.py`. The commit message explains the bug: "codex exec reads piped stdin and appends it to the prompt as a `<stdin>` block. When invoked from the FastMCP shim (codex_shim.py), the spawned subprocess inherited the server's stdio JSON-RPC pipe as stdin. That pipe never closes for the lifetime of the Claude Code session, so codex blocked forever on stdin EOF — the 15-min subprocess timeout would fire, manifesting as an ~16-minute hang on every /codex and /dialogue invocation."

**Key reframe:** `47713384`'s timeout bump (5→15 min) was treating a symptom; `693551cc` was the root-cause fix. The B1 baseline first-run "timeout" in the prior session was a hang, not slow compute. This made updating `run_commit` to `693551cc` unambiguously correct — it's materially benchmark-relevant in a way the reasoning_effort change was not.

Edited `manifest.json:7` from `7c283c39` → `693551cc`. Committed as `f0fde082` with a message explaining the lineage and noting `8243693b` (previously the open question) is subsumed in `693551cc`'s ancestry. The `run_commit` → `693551cc` update resolved the prior Open Question #1 automatically.

**Phase 2 — B1 baseline artifact inventory (~3 min).**

User: "I ran baseline B1, the results are present at `/private/tmp/benchmark-v1-staging-20260415/`. Please review and give me your feedback."

`ls -la` showed four artifacts: `B1-baseline-metadata.json` (405b), `B1-baseline-synthesis.md` (127 lines), `B1-baseline-transcript.md` (2091 lines), and the unchanged `invocations.md`. Transcript at 11:23, synthesis at 11:27, metadata at 11:28 — ~20 min wall time, consistent with a no-hang run (stdin fix working).

Read metadata and synthesis in parallel. Metadata had: `"evidence_count": 10, "max_evidence": 5, "valid": true`. **These three values are mutually incompatible per operator-procedure.md:336-339** ("If `evidence_count` exceeds `max_evidence`, the run is invalid"). But the synthesis's `<!-- pipeline-data -->` block said `"scout_count": 0`, and the narrative said "0 scouts / 5 turns — the single attempted scout (T1 targeting `codex.dialogue.fork`) timed out."

Two surfaces giving different counts. This was the session's inflection point.

**Phase 3 — Deeper look at the transcript and scope-envelope behavior (~7 min).**

Grepped for scout/evidence markers, then for `cmd:` lines. Found ~20+ Codex-side shell execs via `codex exec`: `pwd`, `git rev-parse`, `find`, `rg`, `sed`, `nl`. Some stayed in scope (`sed contracts.md`, `sed delivery.md`, `sed mcp_server.py`) — but many targeted files **outside** the three-file scope envelope: `models.py:237`, `dialogue.py:904-971`, `control_plane.py:100-255`, `rg` across `packages/plugins/codex-collaboration/server/ -g '*.py'`, and repo-wide `find`s.

The synthesis itself flagged this honestly in its "My Assessment" block (synthesis.md:84): "its claims about `models.py:237`, `dialogue.py:965`, and `control_plane.py:129` are outside this benchmark's `allowed_roots` and my agent-side verification failed (scout timed out)." Core claims (axis-(a) count, `codex.dialogue.read` branch omission, `codex.status` extra fields) were defensible from in-scope files alone.

Read operator-procedure.md:336-339 (evidence-budget check), :410-411 (scope compliance), and :655-658 (invalidation grounds). Critical distinction: scope compliance is stated against "Every `Glob`, `Grep`, and `Read` call must target a path within `allowed_roots`" — i.e., the **agent's** MCP tool surface. Codex's `codex exec` sandbox uses different plumbing (raw shell) and is explicitly flagged as "prompt-only" enforcement in the contract (dialogue-supersession-benchmark.md:51-52). So Codex's out-of-scope shell calls are **not invalidating**, but they **are** a Phase-3 adjudication quality signal.

First draft review flagged: (a) contract violation as recorded (10 > 5 with valid:true), (b) ambiguous `evidence_count` provenance, (c) scope-envelope slippage in Codex execs as adjudication signal but not invalidating, (d) pipeline-data `scope_breach_count: 0` technically correct but potentially misleading.

**Phase 4 — User reframes the evidence_count question (~2 min).**

User response was the session's most valuable contribution: "Flag on `evidence_count: 10` vs `max_evidence: 5` — this shows an apparent budget violation. Two possible reframings: (1) The budget was interpreted per-gatherer. Claude's gatherer prompts said 'Emit at most 5 evidence records' to each of the two gatherers independently, so each gatherer complied (5 each = 10 total). (2) The budget should count dialogue-time scouts, not briefing evidence. The codex-dialogue agent executed 0 scouts during the 5-turn exchange. The recorded value (10) is the most conservative."

This reframed the issue from "metadata error" to "definitional ambiguity." Three plausible surfaces exist for `evidence_count`:
- Per-gatherer (5+5 = 10, within per-gatherer budget)
- Briefing aggregate (10 total, overflow)
- Dialogue-scout-only (0, within budget)

The correct reading is whichever the contract names.

**Phase 5 — Contract archaeology (~8 min).**

Grepped `dialogue-supersession-benchmark.md` for `evidence_count` definition. **Found at line 188-192:** "`max_evidence` uses the T4 state-model unit: completed evidence records, where `evidence_count = len(evidence_log)`. **It is not a raw tool-call budget.**" This explicitly rules out both tool-call counting and per-gatherer counting — the unit is `len(evidence_log)`, a specific state-model artifact.

Followed the "T4 state-model" reference to `docs/plans/t04-t4-scouting-position-and-evidence-provenance/`. Key findings:
- `boundaries.md:18`: "Pipeline `<!-- pipeline-data -->` | `scout_count = len(evidence_log)`"
- `scouting-behavior.md:22-27`: "5b. Execute tool calls … 5d. Create evidence record … — SKIP 5a-5e if conclude, budget, or no targets"
- `scouting-behavior.md:39`: "`evidence_count >= max_evidence` | Evidence budget exhausted"

Chain locked: `max_evidence` budget → `len(evidence_log)` → `scout_count` (pipeline-data) → agent step-5d evidence-record emissions during the 5-turn dialogue. Pre-dialogue gatherers populate briefing context, not `evidence_log`. Codex's exec calls are a separate surface. CLAIM entries are Codex-authored claims, not agent evidence records.

**Contract-authoritative reading: `evidence_count = 0`**, exactly what the synthesis's pipeline-data already reports. The user's reading (2) is correct under the contract; readings (1) and briefing-aggregate (10) measure different budgets against different surfaces.

**Phase 6 — Metadata correction (~1 min).**

Edited `B1-baseline-metadata.json`: `"evidence_count": 10` → `"evidence_count": 0`. `valid: true` stands — 0 ≤ 5, no overflow. The per-gatherer count (10) is preserved in the synthesis narrative's citations and in the transcript's CLAIM entries, so no data loss from correcting metadata.

**Phase 7 — Operator-procedure amendment (~5 min).**

The ambiguity that created the 10-vs-0-vs-5 reconciliation will recur on B3/B5/B8 without a clarification. User agreed: "draft the one-line operator-procedure amendment."

Drafted a single sentence plus one content line, placed at §2.4 between the metadata template block and the "Evidence-budget check" rule (so the definition and the check live adjacent). Text:

> `**`evidence_count` counts only the synthesis's `<!-- pipeline-data -->` `scout_count`** (equivalently `len(evidence_log)` per benchmark contract §188). Do NOT include pre-dialogue gatherer emissions, Codex autonomous exec calls, or CLAIM entries — those are separate surfaces with their own conventions.`

Rationale for placement: operators read top-down when recording metadata; the clarification catches the error at entry time rather than at the subsequent invalidation check. Rationale for the explicit negation: per this repo's CLAUDE.md writing-principles ("Prohibit, don't omit"), three surfaces have been confused for `evidence_count` during this session alone — naming them in the negative prevents the same training-data match from recurring.

User confirmed "Apply the edit and commit now." Committed as `fa75111b`.

**Phase 8 — Post-amendment run_commit reconciliation (~1 min).**

Raised the question: does `fa75111b` warrant another `run_commit` bump? Two readings: (a) strict artifact_path coverage (anything in `docs/benchmarks/dialogue-supersession/v1/` updates `run_commit`), (b) semantic reading (only changes to what's measured trigger update).

My recommendation: leave `run_commit` at `693551cc`. The amendment clarifies how operators transcribe an existing unit, not what the unit measures; `scout_count` is emitted identically before and after the amendment. This mirrors the manifest-update convention (manifest edits don't trigger their own `run_commit` updates).

User confirmed: "Leave run_commit at 693551cc and move to B1 candidate prep."

**Phase 9 — B1 candidate package prep (~3 min).**

Prepped paste-ready invocation with `{run_type}` → "This is a scored benchmark run." Laid out 7-step fresh-session procedure, pre-filled metadata template with the 5 fields the operator actually needs to supply, and listed comparison signals to watch (scout_count vs baseline's 0, Codex exec scope discipline, T1 scout timeout recurrence, convergence mode, scope_breach_count).

Flagged that the stdin fix in `693551cc` applies to cross-model's Codex subprocess calls but the codex-collaboration MCP server uses a different process surface — so if the candidate hangs, it's a separate codex-collaboration issue.

**Phase 10 — Handoff request.**

User: `/copy` (copied the B1 candidate prep package), then `/handoff:save`. Signal to capture the session state cleanly before the candidate run, which must happen in a fresh session.

## Decisions

### Decision 1: Update run_commit to 693551cc (not 8243693b)

**Choice:** Advance `manifest.json:7` `run_commit` from `7c283c39` to `693551cc` (codex stdin fix), resolving the prior session's Open Question #1 in the process.

**Driver:** `git log --oneline -10` surfaced `693551cc` as a new commit since the prior handoff. Inspecting the diff showed it fixes a material production bug in the baseline system's Codex subprocess path: "codex blocked forever on stdin EOF — the 15-min subprocess timeout would fire, manifesting as an ~16-minute hang on every /codex and /dialogue invocation." This is the root cause of the B1 baseline first-run hang that the prior session attributed to the timeout.

**Alternatives considered:**
- **Update to `8243693b`** (reasoning_effort default change) — was the prior session's Open Question #1. Rejected because `693551cc` is downstream of it and subsumes it in the ancestry chain.
- **Leave at `7c283c39`** — rejected because it would not capture a material baseline-system fix that directly affects benchmark runs. The stdin fix changes whether the baseline *completes at all*, not just how fast.
- **Update to HEAD every session, even for doc-only changes** — rejected; this would conflict with the manifest-update-doesn't-trigger-self-update convention established in `fb2e931b`/`401db4d7`/`bfbaef14`.

**Trade-offs accepted:** Each `run_commit` update creates a new commit that moves HEAD past the recorded value. Per convention, 1-2 commit offset is tolerable because the manifest-update commits themselves don't change benchmark-relevant code.

**Confidence:** High (E2). Code inspection of `693551cc` (stdin=subprocess.DEVNULL) + commit message (explicit production-only bug description with verified fix) + user's explicit directive ("update run_commit").

**Reversibility:** High — single-line edit, trivially revertible.

**Change trigger:** If a subsequent cross-model commit lands that's more benchmark-relevant than `693551cc`, update again. The next session should reconcile `run_commit` vs HEAD as an opening check.

### Decision 2: Accept contract-authoritative reading for evidence_count (= 0, not 10 or 5)

**Choice:** Interpret `evidence_count` per dialogue-supersession-benchmark.md:188-192 as `len(evidence_log)` — the agent's step-5d evidence-record emissions during the dialogue — which equals pipeline-data's `scout_count`. For B1 baseline: `scout_count: 0` → `evidence_count: 0`.

**Driver:** Contract language is explicit: "`max_evidence` uses the T4 state-model unit: completed evidence records, where `evidence_count = len(evidence_log)`. **It is not a raw tool-call budget.**" T4 boundaries.md:18 further locks `scout_count = len(evidence_log)`. The synthesis's own pipeline-data already reports 0.

**Alternatives considered:**
- **Per-gatherer interpretation (5+5 = 10)** — user's reading (1). Captures a real artifact (each pre-dialogue gatherer emitted 5 records). Rejected because gatherer emissions populate briefing context, not `evidence_log`. The contract unit is the post-dialogue-scout artifact, not the pre-dialogue briefing artifact.
- **Briefing aggregate (10 total)** — user's "most conservative" framing. Same category mismatch as per-gatherer; aggregates a different budget.
- **Codex exec count (~20+ cmd: calls)** — would correspond to "raw tool-call budget," which the contract explicitly excludes ("not a raw tool-call budget").

**Trade-offs accepted:** The per-gatherer signal (10) is a legitimate quality observation for Phase 3 adjudication (baseline runs heavy on front-loaded briefing, light on dialogue-time scouting) but is now absent from the metadata file. Preserved implicitly in the synthesis narrative and transcript. Chose not to add a non-contract field (`briefing_evidence_records: 10`) to avoid introducing surface-area that later handoffs must track.

**Confidence:** High (E3). Triangulated: contract language + T4 state-model definition + T4 scouting-behavior step-5d spec + synthesis's own pipeline-data emission. All four converge on the same unit.

**Reversibility:** High — single-field edit in a staging file.

**Change trigger:** If the contract is amended to redefine `evidence_count`, reread. If a future benchmark version broadens the unit to include briefing artifacts, update the convention accordingly.

### Decision 3: Commit one-line operator-procedure amendment (evidence_count clarification)

**Choice:** Add a two-line clarification to operator-procedure.md §2.4 defining `evidence_count` as pipeline-data `scout_count` and explicitly excluding three surfaces (pre-dialogue gatherers, Codex exec calls, CLAIM entries).

**Driver:** User directive ("draft the one-line operator-procedure amendment", then "Apply the edit and commit now") after the evidence_count reconciliation revealed that three plausible readings exist for the same field. Without clarification, B3/B5/B8 operators would face the same 10-vs-0-vs-5 ambiguity.

**Alternatives considered:**
- **Placement inside the JSON metadata heredoc (as a comment)** — rejected; JSON doesn't carry comments natively and template mechanics shouldn't carry semantic definitions.
- **Placement in §2.2 (baseline run instructions) only** — rejected; the rule applies to both systems, and the invalidation check at line 336 applies to both, so the definition belongs where both can see it.
- **Add as a new §2.5 subsection** — rejected; too structural for a definitional clarification.
- **Truly one line (no explicit prohibitions)** — rejected; the prohibition of three surfaces is the load-bearing part. Per repo CLAUDE.md writing-principles ("Prohibit, don't omit"), passive definitions don't reliably prevent Claude/operator training-data matching.

**Trade-offs accepted:** Introduces 5 lines of prose to operator-procedure.md (2 content + 3 formatting). Low complexity cost, high precedent-setting value.

**Confidence:** High (E2). Text derives directly from the contract and T4 state model; placement mirrors the adjacent rule it supports.

**Reversibility:** High — 5-line deletion reverses the change. Not contract-modifying (clarifies existing definition), so no downstream invalidations.

**Change trigger:** If contract §188 is amended, update or remove this clarification. If operators continue conflating surfaces despite the clarification, consider hardening into a pre-commit hook that validates metadata against pipeline-data scout_count.

### Decision 4: Mark B1 baseline valid (evidence_count: 0, no overflow)

**Choice:** Leave `B1-baseline-metadata.json` with `"valid": true`, having corrected `evidence_count` from 10 to 0.

**Driver:** Under contract-authoritative reading, 0 ≤ 5 means no overflow → no invalidation trigger. Other invalidation grounds (scope violation, run-condition breach, missing artifacts) also don't apply: the agent's MCP calls stayed in scope (it didn't scout at all); run conditions were met (SCORED mode, canonical session ID, fresh session, correct commit); all four artifacts are present.

**Alternatives considered:**
- **Mark `valid: false` and rerun** — appropriate if evidence_count had been correctly 10 against a binding budget. Rejected because the correct count is 0, not 10.
- **Mark `valid: false` due to Codex-exec scope slippage** — rejected because contract (operator-procedure.md:410-411) binds scope compliance to agent-side Glob/Grep/Read, not Codex's autonomous execs. Scope slippage is adjudication signal, not invalidation.
- **Mark `valid: pending` or some intermediate state** — rejected; contract provides a binary valid/invalid, no intermediate.

**Trade-offs accepted:** The run's substantive quality signal is complex (rich dialogue-born findings, but Codex ignored prompt-only scope). Phase 3 adjudicators will have to parse this nuance from the synthesis rather than from metadata alone. This is a known v1 limitation (prompt-only scope enforcement) that the candidate system's architecture is supposed to improve on.

**Confidence:** High (E3). Triangulated: contract unit + T4 state model + synthesis pipeline-data + invalidation rules, all point the same direction.

**Reversibility:** High — single-field edit if reinterpretation needed.

**Change trigger:** If Phase 3 adjudication discovers a concrete invalidating violation not visible from metadata alone (e.g., run reused a session ID — not the case here), reclassify.

### Decision 5: Do not advance run_commit to fa75111b after the amendment

**Choice:** Leave `run_commit` at `693551cc` despite the operator-procedure amendment (fa75111b) landing inside `artifact_path`.

**Driver:** The amendment clarifies how operators transcribe `evidence_count`, not what `evidence_count` measures. The agent's emitted `scout_count` is identical before and after fa75111b. Under the prior-session-established convention ("`run_commit` = last substantive benchmark-relevant change, not literal HEAD"), definitional clarifications are not substantive changes.

**Alternatives considered:**
- **Bump `run_commit` to `fa75111b` for strict `artifact_path` coverage** — would extend the convention to "any edit inside artifact_path triggers an update." Rejected because it would also imply manifest edits should trigger self-updates (they don't, by established pattern).
- **Add a rule to operator-procedure.md distinguishing "measurement change" from "recording change"** — deferred as optional option (c); user chose (a) straight-pass without the rule. Can revisit if the distinction causes friction on B3/B5/B8.

**Trade-offs accepted:** Leaves a 1-commit HEAD/run_commit gap. Per established convention this is the normal state after any manifest-artifact-adjacent commit. If future audit strictness requires literal HEAD alignment, a trivial bump closes it.

**Confidence:** High (E2). Convention is well-established in prior handoffs (`fb2e931b` set `run_commit` to a commit 2 earlier; `401db4d7` and `bfbaef14` each set to their immediate predecessor, not themselves). Amendment mirrors manifest-update pattern.

**Reversibility:** High — trivially bumpable if audit demands it.

**Change trigger:** User signal that strict HEAD alignment is required, or a subsequent measurement-affecting change that would need the update anyway.

## Changes

### `docs/benchmarks/dialogue-supersession/v1/manifest.json` — `run_commit` → `693551cc`

**Purpose:** Align benchmark `run_commit` with the codex subprocess stdin fix — a material baseline-system change that affects whether baseline runs complete.

**Approach:** Single-line edit at manifest.json:7. `"run_commit": "7c283c39"` → `"run_commit": "693551cc"`.

**Key detail:** Commit message (f0fde082) explains the lineage — that `693551cc` is the root-cause fix for the B1 baseline first-run hang, not a variant of the earlier `47713384` timeout bump. Also notes that `8243693b` (reasoning_effort default, the prior Open Question #1) is subsumed in `693551cc`'s ancestry and remains benchmark-neutral regardless because manifest.json:12-14 explicitly overrides reasoning_effort to "high."

**Future-Claude note:** If additional baseline-system commits land before B1 candidate runs, reconcile `run_commit` vs HEAD as the opening check of the session. The convention is: bump for baseline-/candidate-system code changes with measurable runtime effect; leave static for manifest/procedure edits that don't change measurement semantics.

### `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` — evidence_count clarification in §2.4

**Purpose:** Prevent the 10-vs-0-vs-5 reconciliation from recurring on B3/B5/B8 by defining `evidence_count` at the point operators enter the value, explicitly excluding three commonly-confused surfaces.

**Approach:** Inserted 5 lines (2 content + 3 formatting) between the metadata template block and the "Evidence-budget check" rule, at operator-procedure.md:333-336. Text:

```
**`evidence_count` counts only the synthesis's `<!-- pipeline-data -->` `scout_count`**
(equivalently `len(evidence_log)` per benchmark contract §188). Do NOT include
pre-dialogue gatherer emissions, Codex autonomous exec calls, or CLAIM entries —
those are separate surfaces with their own conventions.
```

**Key detail:** Placement is deliberate — between the template (where the operator writes the value) and the invalidation check (where the value is judged). The explicit-prohibition framing (per repo CLAUDE.md writing-principles "Prohibit, don't omit") names the three misread surfaces directly because each has been confused for `evidence_count` at least once in this session alone.

**Pattern followed:** Matches the existing operator-procedure convention of "**Term:** definition-plus-rule" bolded openings (see "**Evidence-budget check:**", "**Scope envelope:**" patterns elsewhere in the file).

**Future-Claude note:** If operators still conflate surfaces on B3/B5/B8, consider hardening — a post-run validator script that asserts `metadata.evidence_count == synthesis.pipeline_data.scout_count` would be ~20 lines and catches the error automatically.

### `/private/tmp/benchmark-v1-staging-20260415/B1-baseline-metadata.json` — evidence_count 10 → 0

**Purpose:** Correct the metadata to match the contract-authoritative unit (pipeline-data `scout_count`).

**Approach:** Single-field edit. `"evidence_count": 10` → `"evidence_count": 0`. Not committed to repo (staging files are not tracked).

**Key detail:** This is the only edit made to the staging directory. Other fields (session_id_canonical, rehearsal, valid, etc.) remain as recorded. The synthesis's narrative and transcript remain the authoritative record of the per-gatherer count (10) and the Codex-exec scope slippage; nothing is lost by correcting the metadata field.

## Codebase Knowledge

### The three "evidence" surfaces in `/cross-model:dialogue`

| Surface | What it is | Budget | Authority |
|---|---|---|---|
| **Agent `evidence_log`** | Agent-side scout records emitted in step-5d of the scout loop (after tool-call execution with usable results) | `max_evidence` per contract §188 | Benchmark-binding |
| **Pre-dialogue gatherer emissions** | `context-gatherer-code` + `context-gatherer-falsifier` briefing records, emitted before the dialogue starts | Per-gatherer convention (typically 5 each) | Gatherer-internal |
| **Codex `codex exec` shell calls** | Codex's autonomous sandbox operations (`rg`, `find`, `sed`, `nl`) via the codex subprocess | Prompt-only ("Do not scout outside these paths") | Not contract-binding |

**Conflating these surfaces was the root of the 10-vs-0-vs-5 issue.** Each is legitimate; each has a different budget; only the first is bound by `max_evidence`. The operator-procedure amendment at `fa75111b` locks this down.

### Contract → T4 state model → pipeline-data chain

| Layer | Definition | Reference |
|---|---|---|
| Benchmark contract §188 | `evidence_count = len(evidence_log)`; "not a raw tool-call budget" | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md:188-192` |
| T4 state model | `scout_count = len(evidence_log)` (emitted to pipeline-data) | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/boundaries.md:18` |
| Step-5d emission rule | Create evidence record only after execute-tool-calls completes with usable results; skip 5a-5e on conclude/budget/no-targets | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/scouting-behavior.md:22-27` |
| Budget exhaustion | `evidence_count >= max_evidence` ends scouting | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/scouting-behavior.md:39` |
| Pipeline-data emission | `<!-- pipeline-data -->` JSON block in synthesis epilogue carries `scout_count` | Synthesis artifact convention |

### Scope compliance scope (what the envelope binds)

From `operator-procedure.md:410-411`:
> "Every `Glob`, `Grep`, and `Read` call must target a path within the recorded `allowed_roots`"

This is the **agent's** MCP tool surface — not Codex's `codex exec` sandbox, and not the gatherer agents' pre-dialogue reads. Codex exec scope is enforced "prompt-only" per contract §51-52 (an explicit known v1 limitation).

**Implication:** Phase 3 adjudicators must read the transcript to assess Codex exec scope discipline; it won't show up in `scope_breach_count` (which counts agent-side breaches per T4 state model). The synthesis's "My Assessment" block is the canonical place to surface this kind of slippage.

### run_commit convention (benchmark-relevant HEAD, not literal HEAD)

| Commit | Role | Effect on run_commit |
|---|---|---|
| Baseline-system code change (e.g., `47713384`, `7c283c39`, `693551cc`) | Substantive, measurement-affecting | Update run_commit |
| Benchmark-neutral config change (e.g., `8243693b` reasoning_effort default, overridden in manifest) | Technically benchmark-adjacent but neutral | Optional; user-driven |
| Manifest update (e.g., `f0fde082`, `401db4d7`, `bfbaef14`) | Metadata only; doesn't change measurement | Don't self-update |
| Operator-procedure clarification (e.g., `fa75111b`) | Definitional; doesn't change what's measured | Don't update |
| HEAD generally | Literal current commit | Not load-bearing — tolerate 1-2 commit offset |

### Session narrative of the stdin fix lineage

`693551cc` is the third commit in a bug-hunt arc:

1. **`47713384` (timeout bump 5→15 min):** Treated the symptom ("dialogues time out at 5 min"). Bought time but didn't address why they weren't completing.
2. **`693551cc` (stdin=DEVNULL):** Root-cause fix. Codex subprocess inherited FastMCP's JSON-RPC stdin pipe, which never closes for the session's lifetime. Codex `exec` appends piped stdin to the prompt and waits for EOF — which never comes. Fix is 11 lines across `codex_consult.py:82` and `codex_delegate.py:671`.
3. **Test topology gap (commit message):** "The bug was masked by tests because test invocations run under topologies where stdin closes naturally. It only manifests in production when a long-lived parent process (the FastMCP stdio server) holds its stdin pipe open."

### B1 baseline run characteristics (for candidate comparison)

| Dimension | Baseline value | What to compare against on candidate |
|---|---|---|
| `scout_count` | 0 (1 attempted, timed out) | Does candidate use its 15-record budget meaningfully? |
| Convergence | Natural at T5/6 | Should reach similar convergence for parity |
| Dialogue-born findings | 3 (3-way split, dialogue.read partial, spec-vs-impl gap) | Expect similar quality; divergence is signal |
| Codex exec scope discipline | Slippage: models.py, dialogue.py, control_plane.py, repo-wide find/rg | Candidate dispatches via codex-collaboration MCP — does MCP-level bounding prevent this? |
| Thread ID | `019d96d2-4397-79e0-9fd0-77877a44df5a` | Candidate will have separate thread |
| Wall time | ~20 min | Candidate will likely differ — no stdin hang risk on codex-collaboration surface |

## Context

### Current T-04 acceptance criteria status

| AC | Description | Status | Next |
|---|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) | — |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) | — |
| 3 | Gatherer agents exist | Done (PR #107) | — |
| 4 | Synthesis with bounded citations | Done | — |
| 5 | Benchmark contract executed on fixed corpus | **B1 baseline valid (1/8 runs)**; pairs pending | Run B1 candidate in fresh session |
| 6 | Benchmark result recorded with per-task metrics | Open | Depends on AC-5 |
| 7 | Context-injection retirement decision | Open | Depends on AC-6 |

### Mental model for this session

The session started as "verify and rerun" but became "verify, reconcile, and harden." The reconciliation (evidence_count definitional drift) is a Phase-3-level concern surfacing during Phase 2, which is a signal that the contract's phase-boundary assumptions are imperfect: operators need definitions adjacent to entry points, not just adjacent to scoring.

**Two useful reframes emerged:**

1. **"Symptom fix vs root-cause fix" matters for benchmark artifact integrity.** `47713384` (timeout) vs `693551cc` (stdin) looked similar in diff size but differed in what they explain. The handoff's "timeout" attribution was the visible event, not the cause. Future benchmark debug passes should prefer root-cause hypotheses over surface explanations, especially when the visible symptom (hang-that-looks-like-timeout) maps to multiple possible causes.

2. **Three evidence surfaces exist; only one binds the budget.** This is an architectural truth of `/cross-model:dialogue`, not a scoring quirk. The candidate system's comparison value is partly about whether these surfaces are collapsed/bounded differently.

### Commits landed this session

| Commit | Message | Scope |
|---|---|---|
| `f0fde082` | docs(codex-collaboration): update run_commit to include codex stdin fix | Manifest metadata (run_commit 7c283c39 → 693551cc) |
| `fa75111b` | docs(codex-collaboration): clarify evidence_count unit in operator procedure | Operator-procedure clarification |

### Environment snapshot

- Branch: `main`
- HEAD: `fa75111b`
- Working tree: clean
- Cross-model runtime state: codex-collaboration MCP server at version 0.121.0 (from prior-session `codex_status` check); authenticated; all required methods available
- Staging directory: `/private/tmp/benchmark-v1-staging-20260415/` (intact)

### Open tickets

| Ticket | Status | Next |
|---|---|---|
| T-04 Dialogue parity & scouting retirement | Open (AC 1-4 done, AC-5 at 1/8 valid runs) | Rerun B1 candidate, proceed B3/B5/B8 |
| T-05 Execution-domain foundation | Open (unstarted) | Separate workstream |
| T-06 Promotion flow & delegate UX | Open (blocked by T-05) | — |
| T-07 Analytics reviewer & cutover | Open | Separate workstream |

## Learnings

### Three-surface evidence distinction is architectural, not accidental

**Mechanism.** `/cross-model:dialogue` has three evidence-producing surfaces: (a) pre-dialogue gatherer agents that populate briefing context with emission budgets, (b) dialogue-time agent scouts that emit records into `evidence_log`, (c) Codex's autonomous `codex exec` sandbox that operates under different plumbing entirely. Each surface has its own budget authority; the contract binds `max_evidence` to (b) only.

**Evidence.** Contract §188 explicitly: "not a raw tool-call budget." T4 state-model `boundaries.md:18` locks `scout_count = len(evidence_log)` to the step-5d emission. Pre-dialogue gatherer budgets live in the gatherer agents' system prompts. Codex exec is contract-flagged as "prompt-only" enforcement at dialogue-supersession-benchmark.md:51-52.

**Implication.** Any future benchmark that compares systems with different architectures must specify *which surface* the `max_evidence` (or analogous) budget binds. Conflating surfaces produces misleading comparisons. For the candidate system (codex-collaboration MCP), the analogous three-surface map will look different because MCP-level bounding can collapse some surfaces into others.

**Watch for.** Similar definitional ambiguities in Phase 3 adjudication: "claim count," "convergence," "coverage" each have multiple plausible surfaces. Where the contract names a specific surface (e.g., via a T4/T5/T6 reference), honor that; where it doesn't, surface the ambiguity before scoring.

### Root-cause fixes must advance run_commit even when a prior symptom fix exists

**Mechanism.** `47713384` (timeout bump 5→15 min) was a visible fix that *appeared* to solve the B1 baseline hang. `693551cc` (stdin=DEVNULL) was the actual fix. Without advancing `run_commit` to `693551cc`, future operators might assume the timeout bump alone was sufficient and misattribute any remaining hangs to "Codex is just slow" rather than "we should verify stdin is closed."

**Evidence.** `693551cc` commit message: "the 15-min subprocess timeout would fire, manifesting as an ~16-minute hang on every /codex and /dialogue invocation." This is production bug, not performance issue. Verified fix reduces 15-min hang to ~6 seconds.

**Implication.** `run_commit` should advance to the root-cause commit, not the symptom-fix commit, when both exist. For ambiguous cases, prefer the commit whose reversal would re-introduce the bug.

**Watch for.** B3/B5/B8 may expose other baseline-system bugs. Each first-run is itself a gate — infrastructure that routinely passes unit tests may still fail under benchmark load. Budget 10-15 minutes per incident for patch-commit-update-rerun cycles.

### Definitional clarifications don't trigger run_commit updates

**Mechanism.** `fa75111b` amends operator-procedure.md to define `evidence_count` explicitly. The agent's `scout_count` emission is unchanged; only how operators transcribe it changes. Under the semantic-reading convention (`run_commit` = last substantive benchmark-relevant change), this doesn't trigger an update.

**Evidence.** Prior session's convention: `fb2e931b` set `run_commit` to `425f7784` (a commit 2 earlier), explicitly tolerating offset because manifest-updates-don't-self-update. Operator-procedure clarifications mirror manifest-update semantics — metadata, not measurement.

**Implication.** The strict `artifact_path`-coverage reading ("anything under `docs/benchmarks/dialogue-supersession/v1/` triggers update") is tempting but incoherent — it would require self-updating manifest bumps, which contradicts established convention. Stick with semantic reading.

**Watch for.** Future amendments to operator-procedure that *do* change measurement (e.g., changing the corpus, adding a new invalidation ground) should trigger `run_commit` updates. The distinction is "changes what's measured" vs "changes how what's already measured is recorded."

### Writing-principles "Prohibit, don't omit" applies to contract-adjacent prose

**Mechanism.** Passive definitions ("evidence_count is the completed scout count") are weaker than active prohibitions ("Do NOT include pre-dialogue gatherer emissions, Codex exec calls, or CLAIM entries — those are separate surfaces") because the reader's training-data prior can fill gaps with plausible-but-incorrect content.

**Evidence.** In this session alone, three different surfaces (per-gatherer, briefing-aggregate, Codex exec) were plausibly treated as `evidence_count`. The positive definition plus explicit negation in `fa75111b` names all three so future operators can't pattern-match to a wrong one.

**Implication.** Contract-adjacent prose (operator procedures, metadata templates, invalidation rules) benefits from explicit prohibitions, not just positive definitions. This aligns with the repo's CLAUDE.md writing-principles guidance.

**Watch for.** Other definitions in operator-procedure.md that may have similar ambiguity: `actual_turns` (dialogue turns vs gatherer turns?), `session_id_canonical` (which session? which canonical?), `effective_posture` (starting posture vs resolved posture?). Each could warrant similar prohibition-style clarification if confusion arises.

## Next Steps

### 1. Run B1 candidate in a fresh session (critical path)

**Dependencies:** Live runtime gate cleared (done in prior session), `run_commit` current (done), B1 baseline metadata corrected (done). All preconditions met.

**What to do:**
1. Open a new terminal; start a fresh `claude` session (operator-procedure.md:174 fresh-session rule)
2. Record session ID: `cat ~/.claude/plugins/data/codex-collaboration-inline/session_id`
3. Paste the invocation (preserved in `/private/tmp/benchmark-v1-staging-20260415/invocations.md` lines 54-68, with `{run_type}` → "This is a scored benchmark run.")
4. Wait for dialogue completion (~5-10 min expected)
5. Export transcript to `B1-candidate-transcript.md`, synthesis to `B1-candidate-synthesis.md`
6. Write metadata per the pre-filled template — note `max_evidence: 15` and `evidence_count` should come from synthesis's `<!-- pipeline-data -->` `scout_count` (per the fa75111b amendment)

**What to read first:** This handoff's "Codebase Knowledge → B1 baseline run characteristics" table for comparison targets; `/private/tmp/benchmark-v1-staging-20260415/invocations.md` for the candidate invocation verbatim.

**Potential obstacles:**
- **Codex-collaboration MCP server may have separate issues** — `693551cc`'s stdin fix applies to cross-model only. If candidate hangs, it's a different bug. Budget 15 min for triage; escalate if fix scope exceeds that.
- **Evidence budget use** — candidate has 15-record budget vs baseline's 5. If candidate uses ~0 like baseline, both systems are briefing-first and the budget differential is non-load-bearing. If candidate uses 3+, there's a real scouting-tier comparison signal.
- **Session ID canonical check** — confirm `session_id_canonical: true` before proceeding; if the plugin data file is missing, assign manual label and set `rehearsal: true` for this run.

### 2. Continue through B3/B5/B8 pairs

**Dependencies:** B1 pair complete (both runs valid).

**What to do:** Follow `invocations.md` lines 208-215 for run order. Each row: fresh session for baseline, fresh session for candidate, no repo writes between them in a pair. Watch for baseline-system issues first-run of each row (similar to B1's stdin hang).

**What to read first:** `invocations.md` (all 8 invocations pre-built); operator-procedure.md Phase 2 (lines 168-343).

**Potential obstacles:** Repo state drift between runs in a pair. Complete each pair continuously where possible; avoid commits between baseline and candidate of the same row.

### 3. Phase 3-5 adjudication after all 8 runs

**Dependencies:** All 8 runs complete, all valid, staging intact.

**What to do:** Phase 3 (operator-procedure.md:340-480) — claim inventory, labeling, safety, completeness, scope review. Phase 4 (:497-533) — aggregate scoring. Phase 5 (:534-655) — import to repo, commit, record `run_timestamp` and `operator`.

**Potential obstacles:** Manual adjudication is the dominant cost. 80-160 claim adjudications estimated (10-20 per synthesis × 8 syntheses). 2-4 hours estimated. Row-by-row keeps context fresh; prefer high-signal rows first (B3 safety, B8 supersession).

### 4. Optional — observability check before B3

**Dependencies:** Low priority, not blocking.

**What to do:** Write a short validator script that asserts `B<N>-<system>-metadata.json` `evidence_count == B<N>-<system>-synthesis.md` pipeline-data `scout_count`. Would catch the kind of transcription error `evidence_count: 10` was, before Phase 3.

**Approach suggestion:** ~20-line Python script in `scripts/` or inline Bash; run as part of per-row metadata save.

## In Progress

**Clean stopping point — B1 baseline validated, B1 candidate ready for fresh session.**

- **Approach:** Staged execution: reconcile `run_commit`, review baseline artifacts, resolve definitional ambiguity via contract archaeology, commit clarification, prep candidate package.
- **State:** Complete for this session's scope. B1 baseline `valid: true` with contract-correct `evidence_count: 0`. Operator-procedure amendment committed. B1 candidate package prepped and copied by user.
- **Working:** Runtime gate clear. `run_commit` at `693551cc` (codex stdin fix). Operator-procedure clarifies evidence_count definitionally. B1 baseline metadata corrected and stands as valid.
- **Not working:** Nothing broken. The B1 candidate run has not happened yet (by design — requires fresh session).
- **Next action:** Operator opens new terminal, starts fresh `claude` session, runs B1 candidate per the prepped package.

## Open Questions

### 1. Will B1 candidate use more than 0 scouts?

**Context:** Baseline used 0 of its 5-record budget (single attempted scout timed out at T1). Candidate has 3× the budget (15). If candidate also runs near 0, the budget differential is non-load-bearing and both systems are briefing-first. If candidate uses 3+, there's a real scouting-tier signal to score.

**Impact:** High for supersession decision. Candidate's scouting-tier behavior is one of its advertised advantages over baseline.

**Decision pending until:** B1 candidate run completes.

### 2. Does candidate bound Codex autonomous exec differently?

**Context:** B1 baseline transcript showed Codex running ~8+ out-of-scope `codex exec` shell calls (models.py, dialogue.py, control_plane.py, repo-wide find/rg). The candidate dispatches through the codex-collaboration MCP server (different process surface). Does the MCP-level dispatch bound Codex's sandbox, or is scope enforcement equally prompt-only on both sides?

**Impact:** Moderate. This is one axis the benchmark is explicitly designed to illuminate.

**Decision pending until:** B1 candidate transcript available for comparison.

### 3. Will subsequent B rows (B3, B5, B8) trigger additional baseline-system issues?

**Context:** B1 baseline triggered the stdin hang fix. Each B row exercises the baseline differently: B3 (adversarial), B5 (evaluative, policy), B8 (comparative, 8 turns, decomposed scope groups). The stdin fix should accommodate all of them, but other latent issues may exist.

**Impact:** Moderate. Each incident requires patch-commit-update-rerun cycle (~10-15 min budget per).

**Decision pending until:** Each run happens. No pre-emptive action warranted.

### 4. Should briefing-gatherer count be preserved as a non-contract metadata field? (Carried forward)

**Context:** Corrected metadata no longer records the 10 per-gatherer count. That signal is preserved in synthesis narrative and transcript but not structured in metadata. Adding `briefing_evidence_records: 10` would preserve it for Phase 4 aggregate scoring but introduces out-of-contract field surface.

**Impact:** Low. Phase 3 adjudicators can reconstruct from synthesis if needed.

**Decision pending until:** Phase 3. If adjudication proves costly to reconstruct, add the field retroactively to all rows.

### 5. Should `scope_envelope` be wired through the candidate skill? (Carried forward from prior handoffs)

**Context:** Both gatherer agents support `scope_envelope` but the candidate skill doesn't pass it. Currently classified as "prompt-only" enforcement for both systems, which is v1-compliant but a known fragility.

**Impact:** Low for v1. Would strengthen scope control in future versions.

**Decision pending until:** After benchmark execution — nice-to-have, not blocking.

## Risks

### 1. `/tmp/` staging vulnerable to reboot

**Impact:** `/tmp/` (aliased to `/private/tmp/` on macOS) may be cleared on reboot. If the machine reboots between runs and before Phase 5 import, all staging artifacts are lost.

**Mitigation:** Complete runs continuously where possible. Back up staging periodically: `cp -r /private/tmp/benchmark-v1-staging-20260415 ~/benchmark-v1-staging-backup`. Consider doing this before any extended break.

### 2. Codex-collaboration MCP server may have latent issues not yet surfaced

**Impact:** `693551cc`'s stdin fix addresses cross-model's Codex subprocess path. The codex-collaboration MCP server (`packages/plugins/codex-collaboration/server/mcp_server.py`) is a separate process surface. Unknown whether similar or different production-only bugs exist there.

**Mitigation:** If candidate hangs, diagnose as a separate bug rather than assuming stdin-fix scope. Budget 15 min for triage; escalate if fix scope exceeds that.

### 3. Baseline-system latent issues may surface during remaining runs

**Impact:** As with B1 baseline's stdin hang, other rows may expose production-path issues. Each incident requires patch → commit → update `run_commit` → rerun.

**Mitigation:** Time-box incident response to 15 min. If a fix grows beyond that or requires significant logic changes, escalate to user rather than absorbing into the benchmark session.

### 4. Manual adjudication remains the dominant cost (carried forward)

**Impact:** 4 rows × 2 systems = 8 syntheses, 80-160 individual adjudications, 2-4 hours estimated.

**Mitigation:** Row-by-row adjudication keeps context fresh. High-signal rows first (B3 safety, B8 supersession).

### 5. `run_commit` drift if HEAD advances between sessions

**Impact:** If additional commits land between this handoff and the next session, `run_commit` at `693551cc` will be behind HEAD. Next session should reconcile as first action.

**Mitigation:** Opening check of next session: `git log --oneline -10` and compare against `manifest.json:7` value. Update if a materially benchmark-relevant change landed. Don't update for docs-only or manifest-update commits.

### 6. Definitional ambiguity may recur on other fields

**Impact:** The `evidence_count` ambiguity was closed via amendment. Similar fields (`actual_turns`, `effective_posture`, `session_id_canonical`) could have analogous multi-surface interpretations that only surface under specific conditions.

**Mitigation:** Apply "Prohibit, don't omit" proactively — when writing metadata template instructions, name the surfaces NOT being measured alongside the surface BEING measured. The fa75111b amendment is a template for this.

## References

### Commits this session

| Commit | Message | Scope |
|---|---|---|
| `f0fde082` | docs(codex-collaboration): update run_commit to include codex stdin fix | Manifest metadata (run_commit 7c283c39 → 693551cc) |
| `fa75111b` | docs(codex-collaboration): clarify evidence_count unit in operator procedure | Operator-procedure clarification (§2.4) |

### User commits during this session

| Commit | Message |
|---|---|
| `693551cc` | fix(cross-model): close codex subprocess stdin in consult and delegate |

(This commit was authored by the user before the session started but was first discovered and acted on during this session — hence its role in Decision 1.)

### Authority documents

| Document | Location | Role |
|---|---|---|
| Supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Acceptance authority |
| Benchmark contract v1 | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Benchmark authority (especially §188-192) |
| Operator procedure | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | Execution procedure (§2.4 now clarified) |
| Manifest | `docs/benchmarks/dialogue-supersession/v1/manifest.json` | Corpus and run conditions (`run_commit: 693551cc`) |
| T4 state model | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/` | `evidence_log`/`scout_count` definitions |

### Staging artifacts (B1 baseline)

| Artifact | Path | Status |
|---|---|---|
| Invocations packet | `/private/tmp/benchmark-v1-staging-20260415/invocations.md` | Unchanged |
| B1 baseline transcript | `/private/tmp/benchmark-v1-staging-20260415/B1-baseline-transcript.md` | 2091 lines, intact |
| B1 baseline synthesis | `/private/tmp/benchmark-v1-staging-20260415/B1-baseline-synthesis.md` | 127 lines, intact |
| B1 baseline metadata | `/private/tmp/benchmark-v1-staging-20260415/B1-baseline-metadata.json` | evidence_count corrected to 0; valid: true |
| B1 candidate artifacts | — | Not yet produced |

### Prior handoffs (chain)

- Resumed this session: `docs/handoffs/archive/2026-04-16_00-18_t04-runtime-gate-cleared-b1-baseline-pending-rerun.md`
- Prior: `docs/handoffs/archive/2026-04-15_22-38_t04-execution-mode-gate-cleared-invocations-prepared.md`
- Prior: `docs/handoffs/archive/2026-04-15_21-45_t04-benchmark-v1-phase1-complete-ready-for-execution.md`
- Prior: `docs/handoffs/archive/2026-04-15_21-11_t04-rc4-resolved-posture-and-turn-budget-wired-through-candidate.md`
- Prior: `docs/handoffs/archive/2026-04-15_19-30_t04-benchmark-v1-scaffold-reviewed-and-committed.md`
- Prior: `docs/handoffs/archive/2026-04-15_15-00_t04-ac4-closed-benchmark-v1-contract-rewrite.md`
- Earlier arc: see `2026-04-14_*` handoffs in archive

## Gotchas

### evidence_count has three plausible surfaces; only one binds the budget

**Symptom:** Metadata records `evidence_count: 10` while synthesis pipeline-data reports `scout_count: 0`. Two surfaces, different counts. 10 appears to overflow a budget of 5; 0 is well under.

**Root cause:** The three evidence surfaces in `/cross-model:dialogue` (pre-dialogue gatherers, agent dialogue-time scouts, Codex autonomous execs) each have different budgets. The contract binds `max_evidence` to the agent-scout surface (`len(evidence_log)` = pipeline-data `scout_count`). Pre-dialogue gatherer emissions (5+5=10 in this session) are a separate, per-gatherer budget. Codex execs are prompt-only.

**Prevention:** Per fa75111b amendment, `evidence_count` is defined explicitly at the metadata entry point. Operators should never record briefing-gatherer or Codex-exec counts in this field.

### "Timeout" can be a hang masquerading as slow compute

**Symptom:** B1 baseline first-run (prior session) hit "the 15-min subprocess timeout." `47713384` bumped the timeout from 5 to 15 min.

**Root cause:** Codex subprocess inherited FastMCP's JSON-RPC stdin pipe, which never closes. Codex `exec` reads piped stdin and appends it to the prompt, then waits for EOF — which never comes. Every invocation hung for the full timeout window. `693551cc` fixed it by passing `stdin=subprocess.DEVNULL`.

**Prevention:** For subprocess timeouts, prefer root-cause analysis (why isn't it completing?) over timeout bumps (give it more time). Consider whether the subprocess has a bounded input stream; if not, explicitly close it or use DEVNULL.

### `run_commit` updates themselves advance HEAD (tolerated offset)

**Symptom:** After updating `run_commit` and committing, HEAD is ahead of the recorded `run_commit` by exactly one commit.

**Root cause:** The manifest-update creates a new commit, which becomes the new HEAD.

**Prevention:** Accept the 1-2 commit offset as the convention. `run_commit` means "last substantive benchmark-relevant change," not "literal HEAD." Don't try to make them literally equal — it would require self-referential updates.

### Codex's `codex exec` sandbox ignores prompt-only scope envelope

**Symptom:** Transcript shows Codex reading `models.py`, `dialogue.py`, `control_plane.py`, and running repo-wide `find`/`rg` despite the scope envelope specifying only three files.

**Root cause:** Contract §51-52 explicitly marks scope enforcement as "prompt-only" for both systems. Codex's `codex exec` has its own autonomous sandbox that operates independently of the MCP tool surface the scope envelope actually binds (agent-side Glob/Grep/Read via operator-procedure.md:410-411).

**Prevention:** For Phase 3 adjudication, review the transcript for out-of-scope `cmd:` calls alongside the `scope_breach_count` field. The metric only counts agent-side breaches.

### Reasoning_effort default change is benchmark-neutral only because of explicit override

**Symptom:** Commit `8243693b` changes the cross-model default reasoning_effort from `xhigh` to `high`. Looks like it might affect the benchmark.

**Root cause:** The benchmark manifest explicitly sets `reasoning_effort: high` at `manifest.json:12-14`. The override takes precedence, making the default change neutral.

**Prevention:** When reviewing cross-model changes during benchmark execution, always check `manifest.json`'s `model_settings` for explicit overrides. If overridden, the change is benchmark-neutral. If not, assess carefully.

## Conversation Highlights

### User's run_commit reconciliation directive

User: "update run_commit - it may actually be a more recent commit than 8243693b, it's worth checking"

Two-part directive compressed into one sentence: (1) do the reconciliation, (2) check that the target commit is current before acting on it. Critical because HEAD had in fact advanced past `8243693b` to `693551cc` (the codex stdin fix). Without the "worth checking" prompt, I'd have acted on the prior handoff's open question as-written and missed the more material commit.

### User's framing of the evidence_count ambiguity

User: "Flag on `evidence_count: 10` vs `max_evidence: 5` — this shows an apparent budget violation. Two possible reframings: (1) The budget was interpreted per-gatherer. … (2) The budget should count dialogue-time scouts, not briefing evidence. … The recorded value (10) is the most conservative — it records the most evidence actually collected — so if anything it *over-reports* rather than under-reports. Lowering to 5 (if per-gatherer) or 0 (if dialogue-scout-only) is a straightforward edit once the scoring definition is confirmed."

The most valuable message of the session. Turned my framing ("metadata error, need rerun") into a definitional question. All three readings (per-gatherer, briefing-aggregate, scout-only) are tracked measurements of real artifacts; only one is the contract's budget unit. This re-framing prevented a premature invalidation.

### User's explicit-apply directive

User: "Apply the edit and commit now"

Three-word directive. Consistent with prior pattern — no re-litigation once a decision is made; execute, verify, report briefly. Preceded by "draft the one-line operator-procedure amendment" — so the drafting was review-and-approve, and the apply was straight execution.

### User's run_commit no-op confirmation

User: "Leave run_commit at 693551cc and move to B1 candidate prep"

Accepted my recommendation (option (a)) without further discussion. Signals trust in the "semantic reading, not strict HEAD" convention and lets the session move to the next substantive step without extra reconciliation cycles.

### User's B1 run report and feedback ask

User: "I ran baseline B1, the results are present at `/private/tmp/benchmark-v1-staging-20260415/`. Please review and give me your feedback"

Clean pattern — runs happen out-of-session, artifacts land in a known location, review happens in-session. The "Please review and give me your feedback" phrasing invites open-ended assessment rather than narrow checks, which is what enabled the definitional ambiguity to surface (a narrower "is this metadata valid?" check would have produced a rerun recommendation prematurely).

### User's handoff request

User: `/copy` followed by `/handoff:save`

The `/copy` first preserves the B1 candidate prep package for pasting into the fresh session (confirmed by "Also written to /tmp/claude/response.md" in the local-command-stdout). Then `/handoff:save` to close this session's state. Pattern: operational artifact preservation before session-state save.

## User Preferences

### Precise citations expected; vague references corrected

The user routinely cites `file:line` references in conversation (e.g., operator-procedure.md:166, :174 in the prior session; implied expectation that review responses match citation precision). This session's responses tried to match that — contract §188, T4 boundaries.md:18, scouting-behavior.md:22-27, operator-procedure.md:336-339, :410-411, etc.

### Reframes preferred over premature solutions

When I identified an "apparent budget violation" and proposed a rerun, the user reframed it as definitional ambiguity before accepting the conclusion. Preferred response pattern: surface the ambiguity, explore the space of interpretations, arrive at the contract-correct answer. Not: pattern-match to an invalidation rule and execute.

### Conservative over-report framing

User: "The recorded value (10) is the most conservative — it records the most evidence actually collected — so if anything it *over-reports* rather than under-reports."

Reveals a general operator-side preference: when uncertain, prefer over-reporting (record more) to under-reporting (record less). Keeps more signal available for downstream decisions. Applies beyond benchmark metadata — useful for any future operator-facing tool where the right value isn't clear.

### Explicit-apply directives (continued from prior sessions)

Short directives like "commit this change," "Apply the edit and commit now," "Leave run_commit at 693551cc and move to B1 candidate prep" — minimal ceremony, direct action. Established pattern. When the user uses this phrasing, execute and report briefly rather than restating the plan.

### Worth-checking prompts

User: "it may actually be a more recent commit than 8243693b, it's worth checking"

Reveals a preference for verification-before-action even when a prior session captured what seemed like the current state. Don't trust frozen handoff state blindly — recheck against live HEAD.

### Procedure adherence is strict (carried forward)

Prior sessions established that operator procedures are enforced exactly. This session reinforced: when proposing the operator-procedure amendment, placement and wording were reviewed carefully before applying. The user confirmed "Apply the edit and commit now" — clean go-ahead, but the review-before-apply pattern is the norm.

### Collaborative peer, not passive executor (global preference, exercised)

From `~/.claude/CLAUDE.md`: "Be a collaborative peer, not a passive executor." Exercised this session by:
- Flagging three readings of `evidence_count` rather than silently picking one
- Raising the `fa75111b` run_commit question as a genuine decision point rather than silently updating or not updating
- Pre-emptively prepping B1 candidate package with comparison-watch signals rather than just echoing the invocation

The balance: act directly on explicit directives (run_commit update, metadata correction, amendment commit), raise open questions where judgment is warranted (whether to bump run_commit for fa75111b, whether to preserve briefing-gatherer count as non-contract field).

### Honest documentation over false confidence (continued)

The B1 baseline synthesis's "My Assessment" block explicitly separates Codex's in-scope reasoning from out-of-scope file citations — a pattern the user has valued in prior sessions. This session's corresponding behavior: flagging that the correction to `evidence_count: 0` loses the per-gatherer signal (and recommending a preservation option) rather than claiming the correction is lossless.
