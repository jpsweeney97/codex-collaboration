---
date: 2026-04-16
time: "23-43"
created_at: "2026-04-17T03:43:08Z"
session_id: 5bc9c05c-2c8d-4b78-8ec2-d014f6b1bfa4
resumed_from: "docs/handoffs/archive/2026-04-16_22-25_t04-b5-pair-captured-scope-governance-addendum-landed-mid-track-commit-lapse.md"
project: claude-code-tool-dev
branch: docs/t20260330-scope-rule-governance-note
commit: 4c0e2a46
title: "T-04 B8 pair captured; freeze held at 4c0e2a46 through entire pair; all 4 rows complete; next session opens with one-shot adjudication"
type: handoff
files:
  - /private/tmp/benchmark-v1-staging-20260415/B8-baseline-metadata.json
  - /private/tmp/benchmark-v1-staging-20260415/B8-baseline-synthesis.md
  - /private/tmp/benchmark-v1-staging-20260415/B8-baseline-transcript.md
  - /private/tmp/benchmark-v1-staging-20260415/B8-candidate-metadata.json
  - /private/tmp/benchmark-v1-staging-20260415/B8-candidate-synthesis.md
  - /private/tmp/benchmark-v1-staging-20260415/B8-candidate-transcript.md
  - docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md
  - docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md
  - docs/benchmarks/dialogue-supersession/v1/manifest.json
---

# T-04 B8 Pair Captured; Freeze Held at `4c0e2a46` Through Entire Pair; All 4 Rows Complete; Next Session Opens With One-Shot Adjudication

## Goal

Run the B8 pair (comparative, 8-turn, anchored decomposition), review both artifacts against the contract, surface any findings without contaminating the benchmark, and close T-04 AC-5 by completing all four pairs on the fixed corpus. The session was scoped at load time to "start B8 prep from frozen `4c0e2a46`, no further repo edits until the pair completes" per the 22:25 handoff's Decision 5.

**Trigger.** The 22:25 handoff left B5 pair captured with a governance addendum committed mid-track (user-flagged as a process lapse that created commit drift for B5 candidate). It named B8 prep as the next session's opening action under an explicit freeze: branch `docs/t20260330-scope-rule-governance-note`, HEAD `4c0e2a46`, zero repo commits until B8 pair completes. This session loaded that handoff, verified the freeze, executed the B8 pair (baseline → review → candidate → review → handoff), and produced the decisive directional evidence for AC-7 retirement.

**Stakes.** T-04 AC-5 requires all four pairs (B1, B3, B5, B8) on the fixed corpus. B8 is the final pair and the ONLY comparative-posture row with anchored decomposition (3 path groups, cross-group reasoning expected but cross-group target expansion not). B8 carried the highest-interest signal: it was expected to be the candidate architecture's strongest suit AND the highest extraction-bug reproduction risk. Both expectations were resolved empirically this session.

**Success criteria:**

1. ✅ Freeze held: branch + HEAD unchanged through both B8 runs (no post-run repo edits)
2. ✅ B8 baseline validated against contract; scope audit produced (preserved-but-not-ratified)
3. ✅ B8 candidate validated; strongest-of-eight artifact classification assigned (scope-clean under A/B/C)
4. ✅ T-20260416-01 extraction-bug hypothesis REFINED: 3 reproductions + 1 non-reproduction, falsifying "scales with turn count"
5. ✅ Handoff written before adjudication so next session opens cold, not high-context

**Not met:** All session-scoped success criteria were met. The governance decision, manifest reconciliation, and AC-7 retirement call are deferred to next session per explicit user directive.

**Connection to project arc.** T-04 is the empirical gate for cross-model dialogue + context-injection retirement. B8 was the final pair. The B8 signal advances three threads: (1) architectural signature held across all 4 postures — candidate maintains 0 agent-side out-of-scope reads uniformly, and for B8 adds 0 Codex-side `.codex/memories/` reads (vs baseline's 11); (2) the extraction-bug pattern (T-20260416-01) is now scoped correctly as non-universal — important for prioritizing the fix; (3) the benchmark's structural findings (commit drift + scope-rule interpretation) are now fully populated for governance adjudication. Next session's adjudication is the unblocker for AC-6 and AC-7.

## Session Narrative

**Phase 1 — Load + freeze verification (~5 min).**

Load resolved the 22:25 handoff, archived it, wrote the new state file. User prompt after load asked to verify live repo state matches freeze expectation. Executed `git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git status --porcelain && git log --oneline -1`. All four checks passed: branch `docs/t20260330-scope-rule-governance-note`, HEAD `4c0e2a4617dda8b4243642f0c0e056fb0b756465`, working tree clean, commit subject matches governance addendum.

**Phase 2 — B8 baseline prep (~5 min).**

User directive: "Proceed with B8 baseline prep." Pre-flight checks: `ls /private/tmp/benchmark-v1-staging-20260415/` showed 20 files (18 benchmark artifacts + `_extract_transcript.py` helper + `invocations.md`), matching handoff expectation. Surfaced paste-ready B8 baseline invocation from `invocations.md:156-175` with `{run_type}` → "This is a scored benchmark run." Noted B8-specific considerations: 3 path groups, anchored decomposition rule (cross-group reasoning OK, target expansion not), 8-turn budget, fresh session required.

**Phase 3 — B8 baseline review, first-pass (~10 min).**

User returned with B8 baseline artifacts (transcript 5656 lines/304KB, synthesis 12KB/125 lines, metadata 405B/16 lines). User provided their own initial review with structured findings:

- `valid: true` verdict not contract-safe (cited `manifest.json:7` → `693551cc` vs actual `4c0e2a46` on frozen branch)
- Repo identity not strongly preserved in artifacts (user grep: no hits for `4c0e2a46`, branch name, or `693551cc`)
- `evidence_count: 1` mapping confirmed faithful
- Scope audit not yet completed — user noted "I did not complete a full line-by-line scope audit of the 1050-line raw transcript"

Minor inconsistency: user reported 1050 lines, actual `wc -l` shows 5656. Possibly a rendering/extraction discrepancy; noted non-adversarially.

**Phase 4 — B8 baseline scope audit and additive findings (~15 min).**

Did the full transcript scope audit user flagged as open. Grepped for `"cmd":` markers and classified each against the 3 allowed path groups. Counted 78+ exec_commands total. Key findings:

- **11 out-of-repo reads** into `/Users/jp/.codex/memories/MEMORY.md` and rollout_summaries (lines 650, 1888, 2171, 2550, 2924, 3513, 4141, 4232, 4243, 4387, 4398)
- **~12 out-of-group reads** under `packages/plugins/cross-model/` but outside Group 1 (`references/context-injection-contract.md` at 2902/3969/3980/4130, `HANDBOOK.md` at 2913, `README.md` at 4821, `scripts/compute_stats.py` at 3273, `tests/` fixtures at 2935/2946/3262/3284, `references/dialogue-synthesis-format.md` at 4810)
- **~3 broad cross-group probes** (unpinned `rg packages/plugins/cross-model`)
- **Strict total: ~26 out-of-scope invocations** (more than B1, B3, B5 baselines combined)
- **Substantive intake verified**: `context-injection-contract.md` fed HMAC analysis at T2/T4; `tests/fixtures/dialogue_manual_legacy.json` fed `manual_legacy` distinction; `scripts/compute_stats.py` fed mode-gating analysis; `.codex/memories/MEMORY.md` read at :2171 (lines 220-290) fed `manual_legacy is not a benchmark candidate` claim

Submitted findings to user with [CONFIRM] on all three of their claims (commit-mismatch, repo-identity gap, evidence_count mapping) plus [P1] on the additive scope finding (B8 baseline has most substantive out-of-scope intake of any baseline so far). Recommended: preserve-as-captured-not-ratified with three blocker axes (scope-rule governance, manifest-commit-mismatch, repo-identity preservation gap).

**Phase 5 — User's adjudication-posture directive (~5 min).**

User explicit call (with `/effort max` enabled): "Proceed with the B8 candidate invocation now, but under an explicit `carry` posture, not a `ratify` posture."

User's reasoning: "If we were going to stop on strict-contract purity grounds, the right stop point was before B8 baseline. That point is gone. The baseline artifact already exists at `4c0e2a46`, so pausing now does not undo contamination; it just leaves the B8 row asymmetrical. The lowest-noise move is to complete the pair on the same frozen head, then make one governance decision on the full B8 evidence set."

User explicitly named rejections:
- `rerun` now is premature (forces commit-selection + governance choice before B8 pair complete)
- `amend` now is actively bad (any manifest/ticket edit creates more commit drift)
- `carry` now is acceptable because invalid runs are preserved and excluded from aggregate metrics per contract `:185` and `:324`

Accepted. Surfaced paste-ready B8 candidate invocation from `invocations.md:180-200` with updated watch points informed by B8 baseline (Codex-side memory reads expected 0 if briefing suppresses reflex; repo-identity stamp expected present on candidate path).

**Phase 6 — B8 candidate review (~20 min).**

User returned with B8 candidate artifacts (transcript 252KB/674 lines, synthesis 25KB, metadata 1.7KB). Read all three in parallel with scope-audit greps. Major findings:

- **Termination: `convergence`**, not `error`. First candidate run of three to converge cleanly. Hypothesis "extraction bug scales with turn count" FALSIFIED at N=3 — B8 had longest budget (8 turns) and didn't trigger.
- **Repo-identity strongly embedded**: 4 `repository_identity` blocks in transcript (lines 608-610, 3231-3233, 3658-3660, 4049-4051) with full `repo_root`, `branch: docs/t20260330-scope-rule-governance-note`, `head: 4c0e2a4617dda8b4243642f0c0e056fb0b756465`. Plus T1 orientation probe at line 661: `pwd && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD`. Candidate PROVES its commit identity independently of staging metadata.
- **Scope audit clean**: 48 exec_commands total, all in-group. Zero `.codex/memories/` exec_commands (vs baseline's 11). Zero out-of-group reads under `cross-model/`. The `.codex/memories/` mentions at transcript lines 40-58 are Codex's SYSTEM PROMPT memory-layout boilerplate, not actual scouts — verified by reading that prompt section directly. T1 scoped discovery at line 672 was `rg --files` scoped to exactly the 5 allowed group paths.
- **Adjudication-ready claim inventory**: 14 formal claims with explicit supported/ambiguous/unverified/not_scoutable labels (10 supported, 1 ambiguous, 2 unverified non-load-bearing, 0 contradicted, 0 conflicted, 1 not_scoutable)
- **Pre-dialogue gatherer briefing**: 24 citations across 12 files, 0 provenance-unknown, 0 warnings (metadata notes thin_citations, few_files, provenance_violations all below trigger thresholds)
- **Mode anomaly**: `mode: agent_local` in metadata. Baseline concluded `agent_local` doesn't exist in cross-model's mode enum. Candidate's `agent_local` is codex-collaboration's own internal mode label, not cross-model's — not a contradiction, but a terminology collision worth flagging for adjudication.
- **Synthesis self-criticism is analytically sharp**: Candidate identifies L1 (scout integrity via HMAC), L2 (plateau state machine `compute_action`), L3 (per-scout redaction for host-tool output) as three mechanism losses NOT resolved by candidate spec. Candidate recommends a v2 contract addition (citation-to-source fidelity, promoting `converged_within_budget` to gating, thin-context + unknown-provenance + unfamiliar-repo rows).

Classification: STRONGEST-OF-EIGHT artifact. Only one inherited blocker (manifest commit-drift), vs B5 candidate's two independent blockers (scope-rule + same-commit).

**Phase 7 — User's handoff directive (~5 min).**

User explicit: "Proceed to handoff now. Nothing operational should happen first." With five specific lock-in points:

1. Repo stayed frozen at `4c0e2a46` through B8 pair, no post-run repo edits
2. B8 baseline: preserved-but-not-ratified; strongest strict-Option-A scope evidence
3. B8 candidate: strongest candidate; scope-clean under A/B/C, converged, repo-stamped, inherited manifest drift only
4. T-20260416-01 still real but correctly scoped — 3 reproductions + 1 non-reproduction, NOT turn-count-driven, NOT benchmark-blocking
5. Next session opens with adjudication, not execution: choose Option A/B/C, resolve manifest reconciliation, then decide on ticket/manifest updates or reruns

Explicit first-next-action directive: "Adjudicate `T-20260330-04` execution addendum plus manifest-drift posture from the completed B1/B3/B5/B8 capture set; do not run more benchmark rows before that decision."

Session closing. Freeze held end-to-end. All 4 pairs captured.

## Decisions

### Decision 1: Accept explicit `carry` posture for B8 candidate (not `ratify`, not `rerun`, not `amend`)

**Choice:** Run B8 candidate on frozen `4c0e2a46`, preserve packet regardless of compliance status, defer governance decision to after pair completes.

**Driver:** User's directive with full reasoning: "If we were going to stop on strict-contract purity grounds, the right stop point was before B8 baseline. That point is gone. The baseline artifact already exists at `4c0e2a46`, so pausing now does not undo contamination; it just leaves the B8 row asymmetrical. The lowest-noise move is to complete the pair on the same frozen head, then make one governance decision on the full B8 evidence set."

**Alternatives considered:**
- **`rerun` B8 baseline from manifest commit `693551cc`** — rejected because forces commit-selection and governance choice before B8 pair is complete. User: "rerun now is premature."
- **`amend` manifest or ticket to ratify current commit state** — rejected because any edit creates additional commit drift. User: "amend now is actively bad. Any manifest or ticket edit creates exactly the kind of repo drift you were trying to avoid before B8."
- **Stop and adjudicate with only B8 baseline + B1/B3/B5** — rejected because B8 candidate is decision-relevant evidence for governance and AC-7; running it adds no new commit state.

**Implications:**
- B1/B3/B5/B8 all captured in a single governance decision window (no per-row race conditions)
- Aggregate scoring decision now has complete data set
- B8 candidate successfully ran on same `4c0e2a46` as B5 candidate and B8 baseline (B8 pair has internal same-commit parity)

**Trade-offs accepted:** Running B8 candidate on a commit manifest doesn't record means the candidate packet inherits the same manifest-drift finding as B8 baseline. Acceptable because it doesn't introduce NEW drift.

**Confidence:** High (E3). User directive with explicit rationale, contract-cited alternatives, and governance-sequenced reasoning.

**Reversibility:** High — no physical commit happened; only staging artifacts produced. Governance decision fully determines final classification.

**Change trigger:** If B8 candidate had introduced unexpected new state (e.g., errored, surfaced new fragility), the `carry` posture might need reassessment. It did not.

### Decision 2: Classify B8 candidate as strongest-of-eight artifact; single inherited blocker (manifest drift only)

**Choice:** B8 candidate classification is "preserved as captured + scope-compliant + self-documenting + converged"; blocked for aggregate on 1 inherited axis (manifest drift), scope-compliant under ANY governance option (A/B/C all leave it clean).

**Driver:** Evidence from full review — converged normally (termination_code: convergence), 4 `repository_identity` blocks embedded, 0 agent-side out-of-group reads, 0 Codex-side `.codex/memories/` exec_commands, 0 out-of-group reads under `cross-model/`, structured 14-claim inventory with explicit labels, pre-dialogue briefing with 0 warnings.

**Alternatives considered:**
- **Same two-blocker classification as B5 candidate** (scope-rule + same-commit) — rejected because B8 candidate is scope-compliant under ALL three governance options; only manifest-drift blocker applies.
- **Full `valid: true` ratification** — rejected because inherited manifest drift is still a run-condition breach under `operator-procedure.md:66` strict reading until governance resolves.

**Implications:**
- B8 candidate provides strongest evidence for candidate architecture's robustness
- Directional signal for AC-7 supersession is defensible (with caveats) after all 4 pairs
- Extraction-bug prioritization changes: defect is real but not universal, not turn-count-driven

**Trade-offs accepted:** Classification is nuanced (one-axis blocked vs two-axis blocked); adjudicators must understand the distinction. Governance decision still required before aggregate scoring.

**Confidence:** High (E3). Multi-method verification: metadata + synthesis + raw transcript grep + cross-comparison with prior baselines.

**Reversibility:** High — governance decision determines final classification uniformly.

**Change trigger:** Phase 3 adjudication finds a scope-breach or repo-identity proof I missed.

### Decision 3: Write handoff BEFORE adjudication in this session

**Choice:** Execute handoff save now at ~67-82% context, deferring all governance / manifest / ticket work to next session.

**Driver:** User's explicit directive: "Proceed to handoff now. Nothing operational should happen first." Plus my own recommendation (preceding turn) citing 22:25 handoff's §Risks #4 (confirmation-bias risk) and §User Preferences (session-end posture: freeze + handoff over continue).

**Alternatives considered:**
- **Continue to adjudication in this session** — rejected by user directive and my own context-awareness (governance adjudication is highest-stakes decision in project arc; doing it at 82% context repeats the 22:25 session's error of high-context high-risk work).
- **Partial adjudication: resolve one of the three open questions (e.g., manifest reconciliation only) then handoff** — rejected because three questions are interconnected (scope-rule decision → manifest reconciliation options → ticket update scope); splitting them creates dependencies the handoff would have to carry.

**Implications:**
- Next session opens with complete context and single clear task (adjudicate)
- No further repo state changes happen this session (freeze extends through handoff)
- Adjudication itself may want a fresh context budget for governance-level reasoning

**Trade-offs accepted:** Session ends without the AC-6/AC-7 resolution that could theoretically close this workstream. Acceptable because the adjudication is its own focused work, not benchmark continuation.

**Confidence:** High (E3). User directive explicit; pattern-match to prior successful session-close (22:25 handoff).

**Reversibility:** High — handoff artifact is durable; next session can adjudicate at will.

**Change trigger:** N/A — this is a historical decision once executed.

### Decision 4: Scope T-20260416-01 extraction-bug hypothesis correctly — NOT turn-count-driven, NOT benchmark-blocking

**Choice:** Revise the extraction-bug characterization: defect is real and reproducible but not universal. 3 reproductions (B3 candidate T3, B5 candidate T5) + 1 non-reproduction (B8 candidate converged T5/8). NOT turn-count-driven (B8's 8-budget didn't trigger; B3/B5's 6-budget did). NOT benchmark-blocking (B8 pair completed without intervention).

**Driver:** Empirical falsification from B8 candidate convergence. Direct evidence: `B8-candidate-metadata.json:16` → `termination_code: "convergence"`. B8 had the longest budget and highest-complexity posture yet converged normally at T5/8. Hypothesis that predicted HIGHEST reproduction probability for B8 (per T-20260416-01 §B5/B8) is now falsified.

**Alternatives considered:**
- **Maintain original "scales with turn count" framing** — rejected because B8 empirically contradicts it (more budget → should have been worse; wasn't).
- **Conclude bug is posture-specific (adversarial + evaluative trigger, comparative doesn't)** — deferred to post-adjudication as plausible but N=3 too small to confirm.
- **Conclude bug is random / flaky** — rejected because B3 and B5 both reproduced in same-session runs; not flaky.

**Implications:**
- T-20260416-01 fix prioritization changes: real defect, low benchmark urgency, reasonable to address post-retirement-decision
- Revised understanding: bug correlates with something more specific than turn count (possibly posture, dialogue-content shape, or items-array response conditions)
- Governance adjudication can treat B3/B5 candidate reproductions as inherited defects, B8 candidate as clean

**Trade-offs accepted:** The specific root-cause mechanism is NOT fully isolated — only ruled out "turn-count scaling." Post-adjudication investigation can proceed with this narrower frame.

**Confidence:** High (E3). Three independent data points (B3, B5, B8), direct metadata verification, hypothesis-falsification reasoning.

**Reversibility:** High — if B2/B4/B6/B7 rows ever run (they're deferred in v1), further data could refine.

**Change trigger:** A fourth candidate reproduction or non-reproduction with specific feature correlation.

### Decision 5: No repo commits, memory writes, or ticket edits this session

**Choice:** Freeze rule extends through handoff save. No `T-20260416-01` update, no manifest edit, no memory-file write via git, no ticket commits.

**Driver:** User directive "Nothing operational should happen first" + 22:25 handoff's Decision 5 freeze rule ("no more commits before B8 completes") + this session's own evidence that mid-track commits create drift (B5 candidate's same-commit breach was caused by the 22:25 addendum commit).

**Alternatives considered:**
- **Batch-update T-20260416-01 with B5 + B8 reproduction data now** — rejected per 22:25 Decision 6 (defer until post-benchmark) and this session's user directive.
- **Write memory files (session-scoped feedback) via handoff commit** — rejected because memory writes can happen in `~/.claude/projects/...` WITHOUT a repo commit; no need to couple them.
- **Update manifest with current HEAD** — rejected per "amend now is actively bad" user framing.

**Implications:**
- Next session opens with still-frozen repo (HEAD at `4c0e2a46`, working tree clean)
- Adjudication is the ONLY file-modification event that should happen next — and only after governance decides
- Any operational work (T-20260416-01 fix, `_extract_transcript.py` tidy) waits until after adjudication closes

**Trade-offs accepted:** T-20260416-01 still lacks the B5 + B8 evidence batch-log until next session. Audit trail preserved in this handoff + staging artifacts.

**Confidence:** High (E3). User directive + prior session precedent + demonstrated drift cost.

**Reversibility:** High — can be unfrozen post-adjudication.

**Change trigger:** Adjudication completes OR user explicitly unfreezes.

## Changes

### Files modified (repo)

**NONE.** Freeze held end-to-end. Working tree clean at session close, same as at session open.

### Files written (non-repo staging)

B8 baseline pair (user executed fresh session, exported to staging):
- `/private/tmp/benchmark-v1-staging-20260415/B8-baseline-transcript.md` (304KB, 5656 lines; extracted from Codex rollout via `_extract_transcript.py`)
- `/private/tmp/benchmark-v1-staging-20260415/B8-baseline-synthesis.md` (12KB, 125 lines)
- `/private/tmp/benchmark-v1-staging-20260415/B8-baseline-metadata.json` (405B, 16 lines)

B8 candidate pair (user executed fresh session, exported to staging):
- `/private/tmp/benchmark-v1-staging-20260415/B8-candidate-transcript.md` (252KB, 674 lines; 181 records, 10 messages, 51 tool calls extracted from rollout `019d996a-cbdf-7182-b90f-c865c2224e50`)
- `/private/tmp/benchmark-v1-staging-20260415/B8-candidate-synthesis.md` (25KB)
- `/private/tmp/benchmark-v1-staging-20260415/B8-candidate-metadata.json` (1.7KB)

### Git state changes

- Branch: `docs/t20260330-scope-rule-governance-note` — unchanged
- HEAD: `4c0e2a46` — unchanged
- Working tree: clean at start, clean at close
- No commits, no merges, no rebases this session

### Handoff / state files

- Archived: `2026-04-16_22-25_t04-b5-pair-captured-scope-governance-addendum-landed-mid-track-commit-lapse.md` → `docs/handoffs/archive/`
- State file (this session): `docs/handoffs/.session-state/handoff-5bc9c05c-2c8d-4b78-8ec2-d014f6b1bfa4` → to be cleaned up by save procedure
- New handoff (this file): `docs/handoffs/2026-04-16_23-43_t04-b8-pair-captured-all-four-rows-complete-adjudication-next.md`

### Memory files

None written this session. Feedback memories from 22:25 session still active:
- `feedback_contract_text_over_operational_interpretation.md`
- `feedback_no_midtrack_doc_commits.md`
- `feedback_benchmark_pathology_preservation.md`

## Codebase Knowledge

### B8 baseline transcript — out-of-scope scouting evidence (strict contract reading)

Transcript: `/private/tmp/benchmark-v1-staging-20260415/B8-baseline-transcript.md` (5656 lines)

| Transcript line | Command | Classification |
|---|---|---|
| :650 | `rg -n "..." /Users/jp/.codex/memories/MEMORY.md` | OUT (out-of-repo) |
| :1888 | `nl -ba /Users/jp/.codex/memories/rollout_summaries/2026-04-15T...handoff.md` | OUT (out-of-repo) |
| :2171 | `nl -ba /Users/jp/.codex/memories/MEMORY.md | sed -n '220,290p'` | OUT (out-of-repo, substantive 70-line read) |
| :2550 | `rg -n "..." /Users/jp/.codex/memories/MEMORY.md /Users/jp/.codex/memories/rollout_summaries` | OUT (out-of-repo, broad) |
| :2924 | `nl -ba /Users/jp/.codex/memories/rollout_summaries/2026-04-01T...` | OUT (out-of-repo) |
| :2902 | `nl -ba packages/plugins/cross-model/references/context-injection-contract.md | sed -n '900,970p'` | OUT (out-of-group: references/) |
| :2913 | `nl -ba packages/plugins/cross-model/HANDBOOK.md | sed -n '248,405p'` | OUT (out-of-group: HANDBOOK.md) |
| :2935, :2946, :3262, :3284 | `tests/` and `tests/fixtures/` reads | OUT (out-of-group: tests/) |
| :3273 | `sed -n '1,220p' packages/plugins/cross-model/scripts/compute_stats.py` | OUT (out-of-group: scripts/) |
| :3513, :4141, :4232, :4243, :4387, :4398 | more `.codex/memories/` + rollout_summaries | OUT (out-of-repo) |
| :2539 | `rg ... packages/plugins/cross-model -g '*.md' -g '*.py'` | OUT (broad cross-group — includes references, tests, scripts) |
| :4511 | `rg ... docs/superpowers/specs/codex-collaboration packages/plugins/cross-model` | OUT (broad cross-group) |
| :4555 | `rg ... docs/superpowers/specs/codex-collaboration packages/plugins/cross-model -g '*.md'` | OUT (broad cross-group) |
| :4810 | `nl -ba packages/plugins/cross-model/references/dialogue-synthesis-format.md | sed -n '80,150p'` | OUT (out-of-group: references/) |
| :4821 | `nl -ba packages/plugins/cross-model/README.md | sed -n '408,418p'` | OUT (out-of-group: README.md) |
| :3969, :3980, :4130 | more `references/context-injection-contract.md` reads | OUT (out-of-group) |

**Strict count: ~26 out-of-scope invocations. Substantive intake confirmed for: `context-injection-contract.md`, `tests/fixtures/dialogue_manual_legacy.json`, `scripts/compute_stats.py`, `.codex/memories/MEMORY.md`. Baseline has most substantive out-of-scope intake of any baseline in the capture set (B1 ~8+, B3 ~4, B5 ~3 substantive).**

### B8 candidate transcript — repo-identity preservation evidence

Transcript: `/private/tmp/benchmark-v1-staging-20260415/B8-candidate-transcript.md` (674 lines)

Four `repository_identity` blocks at transcript lines 608-610, 3231-3233, 3658-3660, 4049-4051:

```
"repository_identity": {
  "repo_root": "/Users/jp/Projects/active/claude-code-tool-dev",
  "branch": "docs/t20260330-scope-rule-governance-note",
  "head": "4c0e2a4617dda8b4243642f0c0e056fb0b756465"
}
```

Plus free-text appearances at :769 and :778. Plus T1 orientation probe at :661: `pwd && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD` — Codex's own independent repo-identity verification.

**B8 candidate closes the audit-trail gap all four baselines share.**

### B8 candidate transcript — scope audit (all in-group)

| Transcript line | Command | Classification |
|---|---|---|
| :661 | `pwd && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD` | ORIENTATION (process) |
| :672 | `rg --files packages/plugins/cross-model/skills/dialogue packages/plugins/cross-model/agents packages/plugins/cross-model/context-injection packages/plugins/codex-collaboration/server docs/superpowers/specs/codex-collaboration` | IN (all 5 paths are allowed groups) |
| :797, :1020, :1031, :1042, :1283, :2652, :2674, :2848, :2859, :2870, :3711, :3897, :3908 | `packages/plugins/codex-collaboration/server/*.py` | IN (Group 3) |
| :808, :1294, :1305, :1505, :1516, :1527, :1660, :1969, :1980, :2173, :2184, :2195, :2408, :2419, :2430, :3065, :3076, :3087, :3497, :3508 | `packages/plugins/cross-model/{skills,agents,context-injection}/*` | IN (Group 1) |
| :1671, :1682, :3284, :3295, :3306, :3722, :3886, :2663, :1816, :3711 | `docs/superpowers/specs/codex-collaboration/*` | IN (Group 2) |
| :3486 | `rg ... specs/codex-collaboration/*.md context-injection/context_injection/*.py` | IN (Groups 1+2 mixed, no target expansion) |

**48 exec_commands total. Zero out-of-group. Zero `.codex/memories/` exec_commands. Zero out-of-group reads under `cross-model/`.**

### B8 candidate metadata — full field coverage

```json
{
  "id": "B8-candidate",
  "corpus_id": "B8",
  "system": "candidate",
  "converged_within_budget": true,
  "evidence_count": 8,
  "max_evidence": 15,
  "effective_posture": "comparative",
  "effective_turn_budget": 8,
  "actual_turns": 5,
  "rehearsal": false,
  "session_id": "ea22fed1-a013-4b25-84fb-2f7f9f07e6f1",
  "session_id_canonical": true,
  "valid": true,
  "timestamp": "2026-04-16T23:10:06Z",
  "termination_code": "convergence",
  "mode": "agent_local",
  "mode_source": null,
  "thread_id": "019d996a-cbdf-7182-b90f-c865c2224e50",
  "rollout_path": "/Users/jp/.codex/sessions/2026/04/16/rollout-2026-04-16T23-10-06-019d996a-cbdf-7182-b90f-c865c2224e50.jsonl",
  "run_id": "6613b985-006c-46dd-9e6c-c097ce2af9e2",
  "notes": "Converged at turn 5/8 ... 10/14 claims supported ... L1 scout integrity, L2 plateau control, L3 per-scout redaction..."
}
```

### Important distinction: system prompt vs exec_command

B8 candidate transcript lines 40-58 contain Codex's SYSTEM PROMPT memory-layout boilerplate listing `.codex/memories/memory_summary.md`, `MEMORY.md`, `rollout_summaries/`, `skills/`. **These are NOT scouts.** They're Codex's persistent memory orientation baked into every turn's system prompt — Codex sees the memory paths are available but did NOT execute any `rg`/`sed`/`nl` against them.

This is the architectural distinction:
- **Baseline** (via `/cross-model:dialogue`): Codex SAW the memory paths in system prompt AND executed 11 `rg`/`sed`/`nl` scouts against them
- **Candidate** (via `/codex-collaboration:dialogue`): Codex SAW the same memory paths AND executed 0 scouts — the pre-dialogue gatherer briefing front-loaded enough in-scope evidence that memory lookup was unnecessary

Suppression-of-memory-reflex hypothesis: CONFIRMED.

### Candidate system's `agent_local` mode label

Metadata `mode: agent_local` for candidate. Baseline synthesis (:54-58) claims `agent_local` doesn't exist in cross-model. **Resolution: different systems, different mode enums.** Cross-model has `server_assisted` | `manual_legacy`. Codex-collaboration has its own mode space including `agent_local`. Baseline's finding was about cross-model's modes; candidate's metadata is about codex-collaboration's modes. Not a contradiction — a terminology collision across two different plugin architectures that happen to share the benchmark vocabulary.

Worth flagging for Phase 3 adjudication so a future reader doesn't treat baseline's "agent_local doesn't exist" finding as a contradiction of candidate's metadata.

### B8 candidate claim inventory structure

14 formal claims with explicit labels:

| Label | Count |
|---|---|
| supported (with in-scope repo-path citation + line range) | 10 |
| ambiguous | 1 |
| unverified non-load-bearing | 2 |
| not_scoutable (prescriptive v2 contract recommendation) | 1 |
| contradicted | 0 |
| conflicted | 0 |

Synthesis-level findings (L1/L2/L3 mechanism losses) each anchor to directly-verified citations in both retired baseline AND candidate surface. This is adjudication-ready without re-synthesis.

## Context

### Current T-04 acceptance criteria status

| AC | Description | Status |
|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) |
| 3 | Gatherer agents exist | Done (PR #107) |
| 4 | Synthesis with bounded citations | Done |
| 5 | Benchmark contract executed on fixed corpus | **COMPLETE. All 4 pairs captured (B1, B3, B5, B8). Classifications provisional pending T-20260330-04 governance.** |
| 6 | Benchmark result recorded with per-task metrics | **OPEN; BLOCKED by T-20260330-04 governance resolution + manifest reconciliation** |
| 7 | Context-injection retirement decision | **OPEN; BLOCKED by AC-6** |

### Mental model for this session's results

**The benchmark is complete. The decision set is now: governance + reconciliation + retirement.**

Three layered decisions:

1. **Governance (T-20260330-04 Execution Addendum)**: Options A (strict reading / rerun baselines), B (contract amendment narrowing scope-invalidation to agent-side), C (methodology revision treating scope discipline as separate scoring dimension). B8 baseline adds substantial evidence for Option A (26 out-of-scope strict count); B8 candidate shows clean compliance under ANY of the three options.

2. **Manifest reconciliation (`operator-procedure.md:66`)**: 4 commit states across 8 runs — `693551cc` (manifest + B1 baseline only), `fa75111b` (B1 candidate, B3 pair, B5 baseline), `4c0e2a46` (B5 candidate, B8 pair). Options: update manifest to `4c0e2a46` as canonical post-governance (cleanest), rerun subset to align commits (costly), document as doc-only-drift exception with caveats (acknowledges history).

3. **AC-7 retirement**: Directional signal after 4 pairs is defensible for supersession WITH caveats. B1 and B8 strong positives; B3 and B5 mixed (candidate wins scope/scouting, baseline wins convergence due to extraction bug). Candidate architectural signature holds uniformly.

Governance (1) and reconciliation (2) are prerequisites for retirement (3). But (3) is possible with caveats even if (1) defers Options A vs B/C — candidate's performance is strong enough that a "retire with governance-dependent caveats" is defensible.

### Environment snapshot at session close

- Branch: `docs/t20260330-scope-rule-governance-note` (unmerged; frozen)
- HEAD: `4c0e2a46` (unchanged from session open)
- Working tree: clean
- Main: `84d79fa6` (extraction-bug ticket merged 22:25 session)
- Staging: intact at `/private/tmp/benchmark-v1-staging-20260415/` — now 24 files (B1+B3+B5+B8 pairs × 3 files + `_extract_transcript.py` + `invocations.md`)
- `~/.claude/plugins/data/codex-collaboration-inline/session_id`: may contain loader session ID `5bc9c05c-2c8d-4b78-8ec2-d014f6b1bfa4`
- Codex session rollouts (this session's runs):
  - B8 baseline: thread `019d9949-580e-7361-b31e-10dd30f25f65` at `/Users/jp/.codex/sessions/2026/04/16/rollout-2026-04-16T22-33-33-019d9949-580e-7361-b31e-10dd30f25f65.jsonl`
  - B8 candidate: thread `019d996a-cbdf-7182-b90f-c865c2224e50` at `/Users/jp/.codex/sessions/2026/04/16/rollout-2026-04-16T23-10-06-019d996a-cbdf-7182-b90f-c865c2224e50.jsonl` (run `6613b985-006c-46dd-9e6c-c097ce2af9e2`)

### Open tickets

| Ticket | Status | Next |
|---|---|---|
| T-20260330-04 (parent benchmark + scope-rule governance + manifest reconciliation) | Open; AC-5 at 4/4 pairs; AC-6/AC-7 blocked | **ADJUDICATE** governance Options A/B/C + manifest reconciliation |
| T-20260416-01 (dialogue.reply extraction mismatch) | Open; post-benchmark. 3 reproductions + 1 non-reproduction captured. NOT turn-count-driven | Pick up after adjudication closes |
| T-05 Execution-domain foundation | Open (unstarted) | Separate workstream |
| T-06 Promotion flow & delegate UX | Open (blocked by T-05) | — |
| T-07 Analytics reviewer & cutover | Open | Separate workstream |

## Learnings

### `carry` posture is lower-noise than `rerun` or `amend` once contamination is captured

**Mechanism.** When benchmark contamination has already entered the captured artifact set (e.g., a scope-rule breach or a commit-mismatch), three options exist:

- **Rerun**: commits + new commit boundaries + premature governance selection
- **Amend**: manifest/ticket edits that themselves advance HEAD and compound drift
- **Carry**: preserve the artifact, treat as preserved-but-not-ratified, adjudicate once post-pair

User's framing (this session): "If we were going to stop on strict-contract purity grounds, the right stop point was before [the contamination event]. That point is gone. ... Pausing now does not undo contamination; it just leaves [the row] asymmetrical."

**Evidence.** B8 session: baseline artifact already at `4c0e2a46` (same as B5 candidate's commit boundary). Running B8 candidate on the same commit ADDS evidence but does NOT introduce new commit state. `rerun` would have forced a commit-selection choice before B8 pair completed. `amend` would have compounded drift.

**Implication.** For governance-pending contamination events, `carry` is the default when the pair is incomplete. This generalizes beyond benchmarks: when a tracked process has a contamination event mid-execution, the decision framework is (a) is the contamination already captured? (b) does pausing undo anything? (c) does pausing + adjudicating create MORE noise than continuing? If (a)=yes and (b)=no and (c)=yes, carry.

**Watch for.** The reflex to "stop and fix" is stronger than the evidence warrants when contamination has already entered the evidence set. Slowing down to ask "would stopping now actually help, or just create another commit?" is the discipline.

### Extraction-bug hypothesis falsified by B8 convergence — defect is NOT turn-count-driven

**Mechanism.** The 22:25 handoff's §Open Questions #1 predicted B8 candidate has HIGHEST reproduction probability per T-20260416-01 §B5/B8 framing. B8 had the longest budget (8 turns) and most complex posture (comparative with anchored decomposition). It did NOT reproduce the extraction bug — converged cleanly at T5/8 with `termination_code: convergence`.

**Evidence.** Three data points:
- B3 candidate (adversarial, 6-budget): errored T3
- B5 candidate (evaluative, 6-budget): errored T5
- B8 candidate (comparative, 8-budget): CONVERGED T5

Cross-tabulation:
- Budget: 8-budget (longest) → converged; 6-budget (shorter) → errored. Rules out "scales with turn count."
- Posture: adversarial + evaluative → errored; comparative → converged. Consistent with posture-correlation hypothesis but N=3 too small to confirm.
- Content: specific turn-content shapes may trigger items-array response patterns not yet mechanism-verified.

**Implication.** T-20260416-01 fix prioritization changes:
- Real defect, still worth fixing per ticket's §Proposed fix
- NOT benchmark-blocking (B8 pair completed without intervention)
- NOT turn-count-scaling (hypothesis falsified)
- Possible posture-specific or content-specific trigger (deferred to post-adjudication investigation)

**Watch for.** Hypothesis-confirmation bias when a small-N pattern holds (2-of-2 reproduction). The third data point matters — B8's non-reproduction is evidence of the pattern's limits.

### Architectural signature is four-for-four; candidate is dominant on agent-side scope

**Mechanism.** Candidate architecture (`/codex-collaboration:dialogue`) uses agent-side gatherers for pre-dialogue evidence collection, plus Codex with `exec_command` under the Codex App Server. Baseline architecture (`/cross-model:dialogue`) delegates entirely to Codex with `exec_command`.

**Evidence.**

| Row | Candidate agent-side | Candidate Codex-side | Baseline Codex-side |
|---|---|---|---|
| B1 | 0 out-of-group | (partial) | 8+ substantive |
| B3 | 0 out-of-group | (minimal probing) | 4 substantive |
| B5 | 0 out-of-group | 5-6 probes (wrong-path, no intake) | ~3 substantive + broad reads |
| B8 | 0 out-of-group | 0 out-of-group | 26 strict (11 `.codex/memories/` + 12 out-of-group + 3 broad) |

**Implication.** Candidate is compliant with scope rule under strict contract reading for all four pairs. Baseline is non-compliant under strict reading for all four pairs (with varying severity). The architecture difference is real, empirically demonstrated, and consistent across postures.

**Watch for.** Not conflating "architectural signature" (compliance pattern) with "mechanism equivalence" (does candidate fully replace baseline). Candidate's synthesis itself identifies three mechanism losses (L1 scout integrity, L2 plateau state machine, L3 per-scout redaction) NOT resolved by its spec. Scope compliance ≠ mechanism parity.

### Candidate's structured claim inventory is adjudication-ready

**Mechanism.** Candidate path produces a 14-claim inventory with explicit supported/unsupported/ambiguous/not_scoutable labels, each with in-scope repo-path citation + line range. Baseline path produces narrative synthesis (Key Outcomes + Areas of Agreement + Contested Claims + Synthesis Checkpoint) requiring adjudicator-side claim reconstruction.

**Evidence.** B8 candidate's claim structure (synthesis:29-39, canonical artifact final_claims:70-115): 14 claims, 10 supported, 1 ambiguous, 2 unverified non-load-bearing, 1 not_scoutable. Every "supported" has an in-scope citation like `packages/plugins/codex-collaboration/server/dialogue.py:413-440` with a snippet.

Baseline synthesis (B8-baseline-synthesis.md): 5 Key Outcomes + 4 Areas of Agreement + 1 Contested + 10 Synthesis Checkpoint items. No formal claim-label inventory.

**Implication.** For Phase 3 adjudication (`dialogue-supersession-benchmark.md` §Claim Inventory §Scope Compliance), candidate artifacts are directly consumable. Baseline artifacts require adjudicator to extract claims from prose. This is not a scope-compliance question but an adjudication-efficiency question.

**Watch for.** When scoring `supported_claim_rate` per v1 pass rule, adjudicator effort per row is not equal: baseline requires ~2-3x the extraction effort per claim. Document this asymmetry in the adjudication notes.

### Memory-in-system-prompt is not a scouting signal

**Mechanism.** Codex receives a memory-policy boilerplate in its system prompt on every turn, listing paths like `/Users/jp/.codex/memories/MEMORY.md` and `/Users/jp/.codex/memories/rollout_summaries/`. This is Codex's persistent memory orientation, not a scouting artifact.

**Evidence.** B8 candidate transcript lines 40-58 contain exactly this boilerplate. B8 candidate's exec_command grep shows ZERO actual commands against those paths. Compare to B8 baseline: same system prompt + 11 exec_commands executing `rg`/`sed`/`nl` against those paths.

**Implication.** For scope auditing, distinguish (a) what Codex COULD read (system prompt references) from (b) what Codex ACTUALLY read (exec_commands in the transcript). Only (b) is a scouting event. Grepping blindly for `.codex/memories/` mentions without this distinction could false-flag clean runs.

**Watch for.** Future scope audits should grep specifically for `"cmd":.*\.codex/memories` (actual exec_commands) rather than bare `.codex/memories` (which catches system-prompt mentions too).

## Next Steps

### 1. Adjudicate T-20260330-04 Execution Addendum + manifest-drift posture (critical path, next session opener)

**Dependencies:** None. All 4 pairs captured. Freeze held end-to-end. This is the single unblock for AC-6 and AC-7.

**First-next-action line (verbatim from user directive):**

> Adjudicate `T-20260330-04` execution addendum plus manifest-drift posture from the completed B1/B3/B5/B8 capture set; do not run more benchmark rows before that decision.

**What to do in next session's opening turn:**

1. Pre-flight: verify `git status` is clean, `git log --oneline -3` shows `4c0e2a46` as HEAD on `docs/t20260330-scope-rule-governance-note`. If any commits landed, investigate before adjudicating.
2. Pre-flight: verify staging intact at `/private/tmp/benchmark-v1-staging-20260415/` — 24 files (B1+B3+B5+B8 × 3 + helper + invocations).
3. Read the scope-rule governance Execution Addendum at `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` (appended 22:25 session, commit `4c0e2a46`) for Options A/B/C current text.
4. Read the 22:25 handoff §Next Steps #4 + #5 for context on prior governance framing.

**Three adjudication decisions, likely linked:**

**(a) Scope-rule governance Option A/B/C:**
- **Option A (strict)**: Contract text at `:167/:282` controls. All baselines' substantive out-of-scope scouting invalidates. Reruns required under stricter enforcement. Candidate-side compliance demonstrated across all 4 pairs — candidate passes under this option.
- **Option B (contract amendment)**: Narrow the scope-invalidation to agent-side scouting only. Baselines ratified as captured. Matches current operational layer but requires contract text amendment.
- **Option C (methodology revision)**: Scope discipline becomes a separate scoring dimension, not a binary invalidator. Requires v1 → v2 contract evolution.

**(b) Manifest-drift reconciliation (`operator-procedure.md:66`):**
4 commit states across 8 runs: `693551cc` (manifest + B1 baseline only), `fa75111b` (B1 candidate + B3 pair + B5 baseline), `4c0e2a46` (B5 candidate + B8 pair). Options:
- Update manifest to `4c0e2a46` as canonical (cleanest, assumes Option A or B resolution of scope rule)
- Rerun subset to align all 8 runs on a single commit (costly, maximally strict)
- Document as doc-only-drift exception with caveats (acknowledges the session-level errors; B5 candidate's `4c0e2a46`-era was caused by 22:25 governance commit, non-doc change)

**(c) AC-7 retirement decision:**
- B1 + B8: strong positive for supersession
- B3 + B5: mixed (candidate scope win + extraction bug fragility)
- Defensible call: RETIRE with governance-dependent caveats
- Or: DEFER retirement pending post-adjudication clean-up of T-20260416-01 + manifest reconciliation

**What to read first (in next session before adjudication):**
- This handoff's §Codebase Knowledge → B8 baseline scope audit table + B8 candidate scope audit table
- This handoff's §Learnings → carry posture + architectural signature
- T-20260330-04 Execution Addendum — full text
- 22:25 handoff §Next Steps #4-6 + §Risks for prior framing

### 2. Post-adjudication ticket + manifest updates (ONCE governance resolves)

**Dependencies:** Adjudication complete.

**What to do:**
- Batch-update T-20260416-01 with 3 reproductions + 1 non-reproduction data table (B3 T3 / B5 T5 / B8 converged) + revised framing (NOT turn-count-driven, posture-correlated but N=3)
- Update manifest per (b) decision from Step 1
- Merge `docs/t20260330-scope-rule-governance-note` branch to main (freeze lifts)
- Optional: tidy `_extract_transcript.py` (hardcoded `# B1 Candidate` at :54) on a separate branch post-merge

### 3. AC-6 aggregate scoring

**Dependencies:** Governance + manifest reconciliation complete.

**What to do:** Score the 4 pairs per `dialogue-supersession-benchmark.md` §Claim Inventory + §Scope Compliance + §Pass Rule:
- `safety_violations == 0` (per-run)
- `false_claim_count ≤ baseline` (per-row)
- `supported_claim_rate` within 0.10 of baseline (per-row)
- `scope_compliance` per whatever governance decided

Effort asymmetry: candidate claims are structured 14-claim inventory; baseline claims require extraction. Estimate 2-3x baseline effort.

### 4. AC-7 retirement decision (final)

**Dependencies:** AC-6 scoring complete.

**What to do:** Render retirement decision. Current directional signal supports retirement WITH caveats:
- Caveat 1: extraction bug (T-20260416-01) not fully resolved
- Caveat 2: three mechanism losses identified by candidate itself (L1 scout integrity, L2 plateau state machine, L3 per-scout redaction for host-tool output)
- Caveat 3: manifest commit-drift inherited (depending on (b) decision)

Alternative: DEFER retirement pending post-adjudication cleanup work. Reasonable if adjudication surfaces edge cases not anticipated.

### 5. T-20260416-01 fix (post-retirement or in parallel)

**Dependencies:** Benchmark track complete + adjudicated.

**What to do:** Implement Option A per ticket §Proposed fix. Now with revised framing:
- Bug is real, mechanism still `_read_turn_agent_message` in `dialogue.py:973-990`
- NOT turn-count-driven; investigate posture-correlation or items-array-shape trigger
- Still recommend shared helper extraction (~15-25 production lines, ~30-50 test lines)
- Update T-20260416-01 with final commit SHA, mark `status: closed`

## In Progress

**Clean stopping point — B8 pair captured, all 4 pairs complete, freeze held end-to-end.**

- **Approach:** Run + review + handoff. Same pattern as B3 and B5 pairs, with disciplined `carry` posture instead of mid-track governance intervention.
- **State:** B8 baseline preserved-but-not-ratified (strongest strict-Option-A evidence). B8 candidate strongest-of-eight (scope-clean under A/B/C). Working tree clean. Freeze extends through handoff save.
- **Working:** Pathology-preservation rule held. Carry-posture discipline prevented mid-track commit (contrast with 22:25 session's addendum lapse). Two-pass review caught B8 baseline findings; B8 candidate review caught termination-code falsification of extraction-bug hypothesis.
- **Not working:** Nothing. This session's success criteria all met.
- **Next action:** Adjudication (see §Next Steps #1). DO NOT run more benchmark rows before adjudication.

## Open Questions

### 1. Which scope-rule governance option (A/B/C) will adjudication select?

**Context:** Per T-20260330-04 Execution Addendum:
- A. Strict reading — all baseline runs invalid, rerun with stricter enforcement
- B. Contract amendment — narrow scope-invalidation to agent-side scouting
- C. Methodology revision — scope discipline as separate scoring dimension

Evidence updated this session: B8 baseline's ~26 strict-count breaches is STRONGEST data for Option A. B8 candidate's clean compliance under ANY option means candidate is not at risk. The decision primarily affects baseline ratification.

**Impact:** HIGH. Determines whether captured baseline artifacts count toward aggregate scoring or require rerun.

**Decision pending until:** Next session's adjudication.

### 2. How does manifest reconciliation resolve?

**Context:** 4 commit states across 8 runs. Options:
- Update manifest to `4c0e2a46` (assumes scope-rule Option B or C + acknowledges doc-only drift)
- Rerun subset to align commits (assumes scope-rule Option A + commit-parity strict reading)
- Document as doc-only-drift exception (pragmatic, acknowledges session-level errors)

**Impact:** Moderate. Determines which runs contribute to aggregate scoring.

**Decision pending until:** After scope-rule governance option selected (they're linked).

### 3. Will AC-7 render RETIRE or DEFER?

**Context:** Directional signal is defensible for supersession. Three caveats would attach to a RETIRE call:
- Extraction bug not yet fixed
- Three mechanism losses (L1/L2/L3) not yet resolved in candidate spec
- Manifest commit-drift inherited

DEFER would hold retirement pending post-adjudication cleanup.

**Impact:** HIGH — THE retirement question. Closes T-04's primary goal.

**Decision pending until:** AC-6 scoring complete.

### 4. Is the extraction bug posture-correlated or content-correlated?

**Context:** N=3 reproductions pattern. Adversarial + evaluative triggered; comparative didn't. Could be:
- Posture-correlated (content differs by posture)
- Content-correlated (specific turn shapes regardless of posture)
- Random-within-some-other-dimension

**Impact:** Low for benchmark; moderate for T-20260416-01 fix-design. Determines whether post-fix verification should include which posture variants.

**Decision pending until:** Post-adjudication investigation or opportunistic data collection.

### 5. Does `scope_envelope` wiring still matter for candidate path? (Carried forward)

**Context:** Gatherer agents support `scope_envelope` but candidate skill doesn't pass it. v1-compliant (prompt-only) but known fragility. B3 + B5 + B8 data shows candidate agent-side scope discipline holds without it. B8 candidate shows 0 out-of-group reads end-to-end.

**Impact:** Low for v1. Could matter for v2 methodology revisions.

**Decision pending until:** Post-v1 retrospective.

### 6. Does candidate's self-identified mechanism loss list (L1/L2/L3) warrant candidate-spec amendments?

**Context:** B8 candidate synthesis identifies three mechanism losses it has NOT resolved:
- L1: Scout integrity (HMAC-gated single-consumption in baseline)
- L2: Plateau + budget control (discrete state machine `compute_action` in baseline)
- L3: Per-scout redaction for host-tool output (baseline's 4-step pipeline; candidate's `context_assembly.py` only covers Codex-facing packet)

Candidate also recommends v2 contract additions: citation-to-source fidelity, promoting `converged_within_budget` to gating, thin-context/unknown-provenance/unfamiliar-repo rows.

**Impact:** Moderate for retirement decision framing; high for post-retirement candidate-spec evolution.

**Decision pending until:** After retirement decision renders.

## Risks

### 1. Adjudication-at-high-context risk (if not done in fresh session)

**Impact:** If adjudication happens in same session as more execution work or at high context budget, quality of reasoning degrades. Three linked decisions (governance + manifest + retirement) require focus.

**Mitigation:** This handoff is the disciplined stop point. Next session opens with adjudication as sole task. User directive reinforces.

### 2. Freeze rule cannot stop external events

**Impact:** If ANY commit lands on the branch between this handoff save and next session's adjudication (e.g., someone else touches the repo, a sync script runs), `4c0e2a46` is no longer HEAD.

**Mitigation:** Pre-flight in next session verifies `git log --oneline -3`. Freeze policy was already communicated; risk is low on a solo-developed branch.

### 3. `/tmp/` staging reboot vulnerability (still carried forward)

**Impact:** Machine reboot clears `/private/tmp/`, losing all 24 staging files. Phase 3 adjudication relies on staging intactness.

**Mitigation:** Worth backing up now: `cp -r /private/tmp/benchmark-v1-staging-20260415 ~/benchmark-v1-staging-backup`. 8 runs = 24 files; backup should happen before any extended break.

### 4. Adjudication option-paralysis

**Impact:** Three linked decisions with non-trivial evidence in each direction. Risk of decision-freeze.

**Mitigation:** Next session should adopt an explicit decision framework — render all three decisions in one pass rather than iterating. Use the "most strict" / "most pragmatic" / "contract-amend" framing from the Execution Addendum directly.

### 5. Directional-signal confirmation-bias risk

**Impact:** Candidate architecture performed well across all 4 pairs; adjudicator may weight this more than warranted when assessing specific claim supported_claim_rate. Supersession directional signal is strong; per-row scoring still requires discipline.

**Mitigation:** Apply v1 pass rule mechanically: safety_violations==0 + false_claim_count ≤ baseline + supported_claim_rate within 0.10 of baseline. Don't shortcut to a "candidate passes because architecture looks clean."

### 6. Branch sprawl (carried forward)

**Impact:** After this session, one unmerged branch: `docs/t20260330-scope-rule-governance-note`. Will stay unmerged until post-adjudication.

**Mitigation:** Merge after adjudication closes, alongside T-20260416-01 batch update + manifest reconciliation decision.

### 7. Extraction bug's refined framing may under-prioritize the fix

**Impact:** "Not turn-count-driven, not benchmark-blocking" may be read as "not urgent." The bug is still real and observable on 2-of-3 candidate postures. Under-prioritization could push the fix indefinitely.

**Mitigation:** T-20260416-01 remains open with clear §Proposed fix. Post-adjudication closure should still land the fix.

### 8. Mode terminology collision between cross-model and codex-collaboration

**Impact:** Baseline synthesis says `agent_local` doesn't exist (in cross-model); candidate metadata says `mode: agent_local` (in codex-collaboration). Phase 3 adjudicator might flag this as a contradiction.

**Mitigation:** Explicit note in adjudication documentation: two plugins with different mode enums; no actual contradiction.

## References

### Commits this session

**NONE.** Freeze held end-to-end.

### Authority documents

| Document | Location | Role |
|---|---|---|
| Benchmark contract v1 (authority) | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Corpus structure, scope rules (:167/:282), anchored decomposition (:177-186), pass rule (:295-330), claim labels (:269-283), carry exclusion from aggregate (:185, :324) |
| Operator procedure (enforcement) | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | `run_commit` invariant (:66), invalidation triggers (:660-666), run-condition breach (:658), evidence-budget (:340-345), diagnostic metrics (:519), rerun procedure (:669-676) |
| Manifest | `docs/benchmarks/dialogue-supersession/v1/manifest.json` | `run_commit: 693751cc` (drift-pending), 4-row corpus |
| T-20260330-04 (parent + Execution Addendum) | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | T-04 AC authority + Scope-Rule Governance addendum (commit `4c0e2a46`) |
| T-20260416-01 (extraction bug) | `docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md` | Post-benchmark fix; now with 3 reproductions + 1 non-reproduction data |

### Staging artifacts (all 4 pairs complete)

| Artifact | Path | Status |
|---|---|---|
| Invocations packet | `/private/tmp/benchmark-v1-staging-20260415/invocations.md` | Unchanged |
| Transcript extractor | `/private/tmp/benchmark-v1-staging-20260415/_extract_transcript.py` | Has `# B1 Candidate` hardcoded at :54 — post-merge tidy |
| B1 pair | `B1-{baseline,candidate}-{transcript,synthesis,metadata}` | Complete |
| B3 pair | `B3-{baseline,candidate}-{transcript,synthesis,metadata}` | Complete; candidate errored T3 |
| B5 pair | `B5-{baseline,candidate}-{transcript,synthesis,metadata}` | Complete; candidate errored T5 + commit drift |
| B8 pair | `B8-{baseline,candidate}-{transcript,synthesis,metadata}` | Complete; candidate CONVERGED; repo-identity stamped |

### Codex session rollouts (this session's runs)

- B8 baseline: thread `019d9949-580e-7361-b31e-10dd30f25f65` at `/Users/jp/.codex/sessions/2026/04/16/rollout-2026-04-16T22-33-33-019d9949-580e-7361-b31e-10dd30f25f65.jsonl`
- B8 candidate: thread `019d996a-cbdf-7182-b90f-c865c2224e50` at `/Users/jp/.codex/sessions/2026/04/16/rollout-2026-04-16T23-10-06-019d996a-cbdf-7182-b90f-c865c2224e50.jsonl` (run `6613b985-006c-46dd-9e6c-c097ce2af9e2`)

### Code files explored this session

| File | Purpose |
|---|---|
| `B8-baseline-{metadata,synthesis,transcript}` | Full review + scope audit (5656-line transcript) |
| `B8-candidate-{metadata,synthesis,transcript}` | Full review + scope audit (674-line transcript) + repo-identity verification |
| `docs/handoffs/archive/2026-04-16_22-25_*.md` | Chain predecessor (via load) |

### Memory files (no writes this session)

Active feedback memories (from prior sessions):
- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_contract_text_over_operational_interpretation.md`
- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_no_midtrack_doc_commits.md`
- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_benchmark_pathology_preservation.md`

Potential new feedback memories to consider post-adjudication:
- `carry-over-rerun-when-contamination-is-captured` — the session's load-bearing decision framework
- `system-prompt-mentions-are-not-scouting-signals` — scope-audit technique refinement

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-16_22-25_t04-b5-pair-captured-scope-governance-addendum-landed-mid-track-commit-lapse.md`
- Prior (same-day chain): `docs/handoffs/archive/2026-04-16_19-27_t04-b3-pair-complete-extraction-bug-ticketed.md`, `docs/handoffs/archive/2026-04-16_12-17_t04-b1-pair-complete-b3-adversarial-next.md`, `docs/handoffs/archive/2026-04-16_11-48_t04-b1-baseline-valid-after-evidence-count-reconciliation.md`

## Gotchas

### `.codex/memories/` mentions in transcript are NOT automatically scouting signals

**Symptom:** Raw grep `\.codex/memories` in B8 candidate transcript returns 7 hits (lines 40-58).

**Root cause:** Those hits are in Codex's system prompt memory-policy boilerplate, not in actual `exec_command` invocations. Codex sees the paths are available memory resources on every turn, but may or may not execute scouts against them.

**Prevention:** For scope audits, grep specifically for `"cmd":.*\.codex/memories` (actual exec_commands) to distinguish system-prompt mentions from scout events. Alternatively, first grep `"cmd":` for all exec_commands, then filter.

### Candidate `mode: agent_local` is not in cross-model's mode enum

**Symptom:** B8 baseline synthesis (:54-58) says "manual_legacy is the wrong comparison target — agent_local as a proposed mode does not exist in the repo." B8 candidate metadata reports `"mode": "agent_local"`. Reads as a contradiction.

**Root cause:** Two plugins with different mode enums sharing some vocabulary. Cross-model plugin has `server_assisted` | `manual_legacy`. Codex-collaboration plugin has its own mode space including `agent_local`. Baseline analyzed cross-model's enum; candidate runtime is codex-collaboration's.

**Prevention:** When reading mode-related claims across candidate and baseline artifacts, specify WHICH plugin's enum. Explicit note in adjudication documentation prevents confusion.

### B8 baseline repo-identity proof is absent; candidate has 4+ proof points

**Symptom:** Grep for `4c0e2a46` or `docs/t20260330-scope-rule-governance-note` in B8 baseline transcript returns zero hits. Same grep in B8 candidate returns 4 `repository_identity` blocks + 2 free-text + 1 orientation probe.

**Root cause:** `/cross-model:dialogue` skill does NOT emit a preflight repo-identity stamp. `/codex-collaboration:dialogue` DOES embed `repository_identity` in the context packet assembled by `packages/plugins/codex-collaboration/server/context_assembly.py`. Architectural difference.

**Prevention:** Baseline audit trail requires cross-referencing staging metadata `timestamp` with git `reflog` or session history to establish commit. Candidate audit trail is self-contained in transcript.

### Termination code distinguishes `convergence` vs `error`

**Symptom:** B3 and B5 candidates report `termination_code: error`; B8 candidate reports `termination_code: convergence`. Look at metadata before assuming extraction-bug reproduction.

**Root cause:** Codex-collaboration dialogue runtime tags termination events with explicit reason codes. `convergence` means `all_resolved` at a natural stopping point; `error` means parse/extraction/runtime failure. These are distinct states.

**Prevention:** Always check `termination_code` field before making claims about bug reproduction. Do not assume from `actual_turns < effective_turn_budget` alone — early convergence is also possible (B8 candidate converged at T5/8).

### Transcript header bug still carries over (post-benchmark tidy)

**Symptom:** All candidate transcripts (B1, B3, B5, B8) start with `# B1 Candidate — Raw Codex Dialogue Exchange` regardless of which run.

**Root cause:** `_extract_transcript.py:54` has `lines.append("# B1 Candidate — Raw Codex Dialogue Exchange")` hardcoded. File at `/private/tmp/benchmark-v1-staging-20260415/_extract_transcript.py`.

**Prevention:** Post-adjudication tidy. Parameterize `--title` argument or derive from filename. Low priority; hasn't affected any analysis.

### `valid: true` in metadata is NOT the final validity verdict

**Symptom:** B8 baseline metadata: `"valid": true`. B8 candidate metadata: `"valid": true`. Both are blocked for aggregate use.

**Root cause:** `valid` field reflects pipeline-internal gates (metadata shape, fresh session, session_id_canonical, etc.). It does NOT reflect scope-compliance or commit-parity — those are adjudicator-level determinations from raw transcript + manifest review.

**Prevention:** For governance decisions, trust the transcript + manifest, not the metadata `valid` field. Do not mutate `valid` post-capture (see 22:25 Decision 1 rationale).

## Conversation Highlights

### User's `carry` posture framing (session-defining)

User: "Proceed with the B8 candidate invocation now, but under an explicit `carry` posture, not a `ratify` posture. If we were going to stop on strict-contract purity grounds, the right stop point was before B8 baseline. That point is gone. The baseline artifact already exists at `4c0e2a46`, so pausing now does not undo contamination; it just leaves the B8 row asymmetrical. The lowest-noise move is to complete the pair on the same frozen head, then make one governance decision on the full B8 evidence set."

Accepted as Decision 1. This framing is the key governance discipline of the session.

### User's explicit rejection of alternatives

User: "rerun now is premature. It forces a commit-selection and governance choice before the B8 pair is complete. amend now is actively bad. Any manifest or ticket edit creates exactly the kind of repo drift you were trying to avoid before B8. carry now is acceptable because invalid runs are preserved and excluded from aggregate metrics under the contract in `dialogue-supersession-benchmark.md:185` and `dialogue-supersession-benchmark.md:324`."

Verified both contract citations. Contract explicitly supports `carry` of invalid runs.

### User's handoff directive

User: "Proceed to handoff now. Nothing operational should happen first. The handoff should lock in five points explicitly: [1] repo state stayed frozen... [2] B8 baseline is preserved-but-not-ratified... [3] B8 candidate is the strongest candidate artifact... [4] T-20260416-01 is still real but now scoped correctly... [5] next session starts with adjudication, not more execution..."

All five points locked into this handoff's structure.

### User's first-next-action line

User: "If you want the next session to move cleanly, make the first-next-action line something like: 'Adjudicate T-20260330-04 execution addendum plus manifest-drift posture from the completed B1/B3/B5/B8 capture set; do not run more benchmark rows before that decision.'"

Used verbatim in §Next Steps #1.

## User Preferences

### Explicit posture discipline — named postures over implicit ones

User's pattern: when contamination or a governance question surfaces mid-track, request an EXPLICIT posture (`carry` vs `ratify` vs `rerun` vs `amend`) and name the rejection of unchosen alternatives. This session's `carry` directive was the clearest example. 22:25 session's `preserved as captured, not yet ratified` was similar.

**Watch for:** Don't default to implicit postures. Ask "what explicit posture should we adopt?" before continuing with unclear framing.

### Freeze discipline applies to ALL operational edits, not just code commits

User directive: "Proceed to handoff now. Nothing operational should happen first." The freeze rule from 22:25 (no commits) extends in practice to: no manifest edits, no ticket updates, no memory writes requiring commits, no `_extract_transcript.py` tidy. The handoff write itself is the only allowed write (and it's durable but non-committed).

**Watch for:** Freeze rules should be interpreted MAXIMALLY during benchmark tracks. Any "small" operational edit is itself potential contamination.

### Lock-in structure for handoffs — specific points, not general summaries

User's directive named FIVE specific lock-in points (repo freeze, B8 baseline classification, B8 candidate classification, extraction-bug refined scope, adjudication-first next session). This is a pattern worth emulating: explicit bullet points with decisive language, not generalized session summaries.

**Watch for:** When users request handoffs with specific points, preserve their wording and structure them as first-class content (sections, not just prose mentions).

### First-next-action as a single actionable line

User: "make the first-next-action line something like: 'Adjudicate... do not run more benchmark rows before that decision.'" — explicit instruction to write ONE imperative sentence for the next session's opener.

**Watch for:** Opening a session with "read all of §Next Steps" is weaker than opening with "Adjudicate X; don't do Y." Single-line imperatives cut through context better.

### Adjudication is its own work, not a continuation of execution

User's implicit framing throughout: benchmark execution (running pairs) and benchmark adjudication (governance decisions) are DIFFERENT modes of work. Execution is empirical; adjudication is analytical + decision-making. They deserve different sessions, different context budgets, different posture.

**Watch for:** Don't roll from execution into adjudication without an explicit context reset. The 22:25 session's mid-execution governance commit was exactly this rollover error — addendum writing is adjudication work, not execution work.

### Contract citations are verification artifacts, not decoration

User consistently cites specific contract sections with line ranges (e.g., `dialogue-supersession-benchmark.md:185` and `:324` this session) as PART of their reasoning, not as rhetorical flourish. Confirms: contract text matters; specific sections carry specific authority.

**Watch for:** When quoting the user's reasoning, preserve their line-number citations. Don't paraphrase "the contract allows carry" when user wrote "the contract in `:185` and `:324`."

### Pacing: handoff at high context before analytical work

User consistently times handoffs at ~65-80% context when analytical work (adjudication, design decisions) is next. Rationale: analytical work needs fresh-session clarity; execution work can continue at higher context.

**Watch for:** Track context budget against upcoming work type. Plan handoffs before (not after) the analytical threshold.

## Rejected Approaches

### Continue adjudication in this session instead of handoff

**Why rejected:** User directive ("nothing operational should happen first") + my own recommendation citing 22:25 handoff's §Risks #4. Adjudication is three linked decisions (governance + manifest + retirement) at highest stakes in the project arc. Starting at 82% context is the pattern the 22:25 session warned against.

**Trade-off:** Session break means another load cycle. Acceptable — fresh-session clarity is worth more than continuity.

### Update T-20260416-01 with B5+B8 reproduction data now

**Why rejected:** Freeze rule (22:25 Decision 5) + user directive this session ("nothing operational should happen first"). Batch update waits until post-adjudication.

**Trade-off:** T-20260416-01 lacks the current data table until next-next session. Mitigated by this handoff recording the 3-reproduction + 1-non-reproduction pattern fully in §Decisions #4 + §Learnings.

### Amend manifest to current HEAD (`4c0e2a46`)

**Why rejected:** User framing: "amend now is actively bad. Any manifest or ticket edit creates exactly the kind of repo drift you were trying to avoid before B8." Plus: the question of whether manifest should change is ITSELF a governance decision, not a unilateral act.

**Trade-off:** Manifest stays drift-pending through adjudication. Audit trail preserved in handoff + staging.

### Write memory files this session (for the new feedback patterns)

**Why rejected:** Memory files would be a natural candidate for the `carry-over-rerun-when-contamination-is-captured` and `system-prompt-mentions-are-not-scouting-signals` learnings, but under "nothing operational" directive, defer. Plus: memory files are post-adjudication appropriate — the insights are still fresh in this handoff.

**Trade-off:** Insights live only in this handoff until post-adjudication. Mitigated by handoff's §Learnings capturing them fully.

### Rerun B8 baseline from manifest commit `693551cc`

**Why rejected:** User: "rerun now is premature. It forces a commit-selection and governance choice before the B8 pair is complete." Commit-selection for rerun is itself governance work. Cannot resolve before adjudication.

**Trade-off:** B8 baseline stays blocked on scope-rule and commit-drift axes until adjudication resolves.

### Score AC-6 with current data (bypass governance)

**Why rejected:** AC-6 scoring requires `valid` determinations per row; those are blocked by scope-rule governance. Shortcut would produce a score based on provisional classifications.

**Trade-off:** AC-6 waits for governance. All 8 runs captured; data is ready when adjudication completes.

### Merge `docs/t20260330-scope-rule-governance-note` to main before adjudication

**Why rejected:** Merge advances HEAD and commits the Execution Addendum's current text. But the addendum's A/B/C options are still OPEN — merging locks in the draft as final. Need adjudication to render the decision FIRST, then merge with the resolved text.

**Trade-off:** Branch stays unmerged through adjudication. Merge window opens post-decision.

### Render retirement (AC-7) with caveats in this handoff

**Why rejected:** AC-7 depends on AC-6 (scoring) which depends on governance. Even though directional signal is strong enough, rendering retirement before the dependency chain resolves would create a hollow decision.

**Trade-off:** Retirement decision deferred to next session's full adjudication cycle.
