---
date: 2026-04-16
time: "12:17"
created_at: "2026-04-16T16:17:12Z"
session_id: ca75293e-7d93-4917-b1cb-4dff59b52c15
project: claude-code-tool-dev
branch: main
commit: fa75111b
title: "T-04 B1 pair complete after candidate review; B3 adversarial next (corpus-numbering resolved)"
type: handoff
files:
  - /private/tmp/benchmark-v1-staging-20260415/B1-candidate-metadata.json
  - /private/tmp/benchmark-v1-staging-20260415/B1-candidate-synthesis.md
  - /private/tmp/benchmark-v1-staging-20260415/B1-candidate-transcript.md
  - docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md
  - docs/handoffs/2026-04-16_11-48_t04-b1-baseline-valid-after-evidence-count-reconciliation.md
---

# T-04 B1 Pair Complete After Candidate Review; B3 Adversarial Next (Corpus-Numbering Resolved)

## Goal

Close the B1 pair by reviewing the candidate run (`/codex-collaboration:dialogue`) against the baseline, confirming metadata validity under the contract-authoritative reading, and setting the stage for B3 prep as the next session's opening action.

**Trigger.** This session's prior save (`2026-04-16_11-48_t04-b1-baseline-valid-after-evidence-count-reconciliation.md`) ended with B1 candidate "pending in fresh session." The user ran B1 candidate in a fresh session, exported three artifacts to `/private/tmp/benchmark-v1-staging-20260415/`, and returned to this session with "All three candidate artifacts now exported to /tmp/benchmark-v1-staging-20260415/" — the review request.

**Stakes.** Benchmark AC-5 (T-04 acceptance criteria) requires "benchmark contract executed on fixed corpus" — meaning every pair (B1, B3, B5, B8) must produce two valid runs. A contested B1 candidate `valid` status would either force a rerun or propagate ambiguity into Phase 4 aggregate scoring. Beyond validation, the B1 pair is the **first comparative data point** between the legacy `/cross-model:dialogue` and candidate `/codex-collaboration:dialogue` systems — the signal that informs the retirement decision (AC-7).

**Success criteria:**
1. B1 candidate metadata validated against contract (`evidence_count` unit per fa75111b amendment, no scope/overflow violations)
2. B1 candidate vs baseline comparison produced on the handoff's watch-list dimensions
3. Any ambiguity about next-row sequencing (B2 vs B3) resolved with contract reference
4. B3 prep package pre-materialized at a level that enables a clean next-session start
5. Clean commit state maintained; staging artifacts intact

**Connection to project arc.** T-04 is the empirical gate for cross-model dialogue+context-injection retirement. B1 is 1 of 4 pairs. The B1 signal (now preserved in this handoff) is **positive for supersession on three dimensions** — scope enforcement, scouting-tier behavior, machine-adjudicable output. Three pairs remain (B3/B5/B8) before the retirement decision can be rendered. This session **did not render the retirement decision**; it produced the first row of evidence.

## Session Narrative

**Phase 1 — Artifact inventory (~2 min).**

User: "All three candidate artifacts now exported to /tmp/benchmark-v1-staging-20260415/"

`ls -la` on the staging dir surfaced three new files plus a helper script: `B1-candidate-metadata.json` (407b), `B1-candidate-synthesis.md` (161 lines), `B1-candidate-transcript.md` (1736 lines), and `_extract_transcript.py` (a user-authored helper for transcript extraction from Codex session rollout JSONL). File mtimes: transcript 12:06, synthesis 12:08, metadata 12:10 — clean ~4-minute sequence from export to metadata write, consistent with a smooth run.

**Critical first comparison:** candidate transcript 1736 lines vs baseline 2091 — ~15% shorter despite the candidate having 3× the evidence budget. Suggests more efficient scouting or fewer Codex excursions, not less substantive dialogue.

**Phase 2 — Metadata and synthesis parallel read (~3 min).**

Metadata record showed: `evidence_count: 5, max_evidence: 15, valid: true, session_id_canonical: true, rehearsal: false, converged_within_budget: true, actual_turns: 5`. The `evidence_count: 5` is the key signal — the operator applied the fa75111b amendment cleanly, recording the pipeline-data `scout_count` value rather than (a) per-gatherer sum of briefing records, (b) aggregate briefing total, or (c) Codex exec call count. The fa75111b amendment from the prior half of this session has already proven its worth in its first post-commit operator action.

Synthesis opened with richer provenance metadata than baseline: `Thread ID`, `Collaboration ID`, `Claude Session ID`, and `Run ID` fields (baseline had just `Thread ID`). Pre-dialogue briefing metadata: "20 citations across 3 unique files, 0 provenance-unknown, warnings: `['few_files']` (expected — benchmark constrained scope to 3 files)." Candidate briefing is denser (20 citations vs baseline's implicit 10 from two cross-model gatherers) and explicitly quality-flagged.

**Phase 3 — Transcript scope-discipline audit (~5 min).**

Grepped for `cmd:` markers in the candidate transcript. Initial count showed 13 matches for the combined pattern — dramatically less than baseline's 53 — but direct `^cmd:` grep found 0, signaling the transcript format differs. Sampled transcript structure via `Read` and confirmed `cmd:` entries appear but with whitespace/quoting variations that the strict-anchor regex missed.

Ran a broader `cmd:` enumeration. 19 in-scope Codex exec calls visible, 1 initial file-discovery `rg --files -g 'contracts.md' -g 'delivery.md' -g 'mcp_server.py' .` that technically scanned repo-root but only named in-scope globs. **Zero sustained out-of-scope Codex excursions**, versus baseline's 8+ (models.py, dialogue.py, control_plane.py, repo-wide find/rg).

Two `Omitted long matching line` entries at transcript:1293 and :1630 turned out to be supplementary_context blocks carrying injected learning episodes from the briefing — not scope escapes.

The synthesis's "2 grep scope-escapes observed" refers to **agent-side** Grep tool calls where the `path` parameter was ignored and ripgrep searched repo-wide. These are Claude Code MCP tool quirks, not intentional out-of-scope scouting. The candidate's scouting framework explicitly tracked them and declared "below the 3-escape terminal threshold" — structural instrumentation the baseline had no equivalent of.

**Phase 4 — Two-lens framing recognition (~3 min).**

Reading the synthesis's final claims revealed the candidate had framed the question as "contract lens (NOT aligned — 5/10 tools) vs milestone lens (ALIGNED for R2)," directly mapping to the spec files' `authority:contracts` and `authority:delivery` frontmatter. This is structurally different from baseline's "3-way split by implementation status (missing names / present-but-partial / present-but-ambiguous)."

**Key re-read:** the baseline's sharpest finding — `codex.dialogue.read` present-but-partial — relied on Codex's out-of-scope reading of `dialogue.py:965`. The candidate's equivalent claim was marked `final_status: unverified` specifically because the relevant code was outside the 3-file scope. The candidate is making a **more epistemologically honest** claim: "I can tell you about the tool registration surface (in-scope), but I cannot verify response-shape conformance because it lives in the dialogue controller (out-of-scope)."

**Phase 5 — Review output delivered (~5 min).**

Produced the comparison matrix across 13 dimensions (evidence count, budget utilization, T1 scout timeout recurrence, Codex cmd: count, out-of-scope count, scope-escape tracking, terminal threshold, convergence, dialogue framing, claim structure, briefing density, mode, thread IDs, wall time). Bottom line: **valid, no edits needed, proceed to next row**.

Characterized the B1 signal for supersession as "positive on three dimensions": scope enforcement, scouting-tier behavior, machine-adjudicable output. Noted that one row can't carry the decision, but the data is consistent with the hypothesis the benchmark was designed to test.

**Phase 6 — User's B2-vs-B3 question (~5 min).**

User: "Why B3 and not B2?"

Good prompt — a moment where I had been using the shorthand "B3 is next" without calling out the corpus-numbering semantics. The prior handoff's §Next Steps #2 even said "proceed through B1-B8 pairs," which the user's question correctly identified as imprecise.

Grepped the benchmark contract and manifest for the corpus rationale. Found authoritative language at `dialogue-supersession-benchmark.md:86-87`:

> "Rows `B2`, `B4`, `B6`, and `B7` are deferred from benchmark v1. They may be restored only through contract amendment under Change Control."

And at :99-105:

> "B1, B3, and B5 are corpus-compliant as written. Their prompts either name or imply specific paths directly, or span explicit anchor groups that permit deterministic per-target scouting without inventing a benchmark-only root-selection rule. Deferred rows `B2`, `B4`, `B6`, and `B7` are outside benchmark v1."

And the corpus-compliance gate at :159-163:

> "Conceptual scored tasks must satisfy the corpus-design constraint: the row must be single-root by construction, deterministically cross-root under T4-CT-02, or executed through documented path-anchored decomposition from its primary evidence anchors."

Key insight surfaced: **the numbering preservation (B1-B8 with gaps) vs renumbering (B1-B4) is deliberate and semantically load-bearing**. It maintains identity of deferred rows for later Change Control restoration, and makes the deliberate-subset structure visible in every run artifact. T4's `scouting-behavior.md:330-331` even flagged the risk for cross-system/spec-interpretation tasks ("B1, B4, B5, B7, B8 are most susceptible to over-classification") — B4 and B7 didn't clear the compliance gate, B1 and B5 did (and B8 via explicit anchored decomposition).

**Phase 7 — Handoff request.**

User: `/copy` (copied the B2-vs-B3 explanation), followed by `/handoff:save` with args "save a handoff and pick up from here in the next session, beginning with B3 prep". Clear signal: save state now, next session's opening action is B3 prep.

## Decisions

### Decision 1: Accept B1 candidate metadata as-is, valid: true

**Choice:** Treat the candidate's recorded metadata (`evidence_count: 5, max_evidence: 15, valid: true`) as contract-correct without edits. Mark the B1 pair as complete for benchmark-v1 Phase 2 purposes.

**Driver:** The operator applied the fa75111b amendment cleanly — `evidence_count` is the synthesis's pipeline-data `scout_count`, not one of the three confused surfaces (briefing-gatherer sum, aggregate briefing total, Codex exec count). All validation fields are internally consistent: `converged_within_budget: true` matches the synthesis's convergence note; `actual_turns: 5` matches the canonical JSON's `turn_count`; `session_id_canonical: true` matches the host-provided session ID in `~/.claude/plugins/data/codex-collaboration-inline/session_id`. No invalidation triggers (operator-procedure.md:655-660) are met.

**Alternatives considered:**
- **Mark `valid: false` due to agent-side grep scope-escapes (2 of them)** — rejected because the candidate's own synthesis declares "below the 3-escape terminal threshold," and the threshold is the contract-authoritative invalidation boundary.
- **Mark `valid: false` due to the single Codex exec `rg --files -g ... .` at repo-root** — rejected because the `-g` globs explicitly name only in-scope files; this is file-discovery, not out-of-scope scouting. Per the contract's scope-compliance rule (operator-procedure.md:410-411), the envelope binds Glob/Grep/Read MCP tool calls on the agent side, not Codex's own sandbox commands. Edge-case flag for Phase 3, not invalidation.
- **Request a rerun for audit cleanliness** — rejected because no contract-defined invalidation condition is met; rerunning would consume operator time and introduce run-to-run variance without addressing any actual defect.

**Trade-offs accepted:** The B1 candidate carries 3 `unverified` claims in its `final_claims[]` array (R2 acceptance gate match, 5 missing tool ticket IDs, staged-completion framing). These are substantive claims with reinforcement-across-turns but marked unverified because the **direct-citation threshold** wasn't met within the 3-file scope. Accepted because this is the T4 state-model's calibration choice, not a defect — it's *more* honest than baseline's equivalent "High confidence" RESOLVED tags.

**Confidence:** High (E3). Triangulated across: metadata field-by-field validation, synthesis self-declaration, transcript audit, contract text (operator-procedure.md:336-339, :410-411, :655-660), and fa75111b amendment.

**Reversibility:** High — if Phase 3 adjudication surfaces an invalidating condition not visible here (none expected), reclassify to `valid: false` and rerun.

**Change trigger:** Adjudication evidence of session reuse (not the case — canonical ID), wrong-commit execution (not the case — candidate ran on `fa75111b` equivalent per transcript line 1288), missing artifact (not the case — all three present), or contract amendment redefining invalidation grounds.

### Decision 2: Interpret corpus numbering gaps as deliberate, not oversight

**Choice:** Treat the B1/B3/B5/B8 sequence as the canonical v1 corpus — a deliberate 4-row subset of an 8-row original design, pruned under T4-CT-02 corpus-compliance — rather than "B1 through B8 with operational skips" or "B1-B4 renumbered."

**Driver:** User question "Why B3 and not B2?" prompted contract archaeology. Found authoritative language at `dialogue-supersession-benchmark.md:86-87` and :99-105 explicitly deferring B2/B4/B6/B7 "from benchmark v1" with "restored only through contract amendment under Change Control." The deferral is contractual, not procedural.

**Alternatives considered:**
- **Treat as typo or skipped numbering** — rejected outright; the contract's explicit deferral language and Change Control gate preclude this.
- **Renumber the 4-row corpus to B1/B2/B3/B4** — rejected because it would lose identity of deferred rows (breaking future Change Control restoration) and erase the design intent visible in every artifact ("this is the pruned subset, not the original set").
- **Treat B2/B4/B6/B7 as out-of-scope permanently** — rejected because the contract explicitly reserves them as potentially-restorable ("may be restored only through contract amendment"). They're deferred, not abandoned.

**Trade-offs accepted:** Numbering gaps can confuse readers who haven't read the contract. Accepted because the corpus compliance rationale (single-root by construction / deterministically cross-root / anchored decomposition) is contractually load-bearing, and preserving the original numbering is how the benchmark documents that pruning choice was made.

**Confidence:** High (E2). Contract language + T4 corpus-compliance rationale + manifest structure all converge.

**Reversibility:** High — if the user or a future benchmark version restores B2/B4/B6/B7, they'll slot in with their original identities. No schema change needed.

**Change trigger:** Contract amendment restoring any deferred row; future benchmark version (v2) with a redesigned corpus.

### Decision 3: Capture B1 signal as "positive for supersession on three dimensions, pending confirmation"

**Choice:** Record in this handoff that B1 candidate outperforms baseline on (1) scope enforcement, (2) scouting-tier behavior, (3) machine-adjudicable output — the three dimensions the benchmark was designed to measure — but that **a single row cannot carry the retirement decision**. Phase 3 adjudication on all 4 pairs is required before AC-7.

**Driver:** The B1 comparison matrix produced strong evidence on each of those three dimensions (structured scope-escape tracking vs prose flagging; 5 scouts vs 0; `final_claims[]` array vs `Synthesis Checkpoint` tags). User hasn't yet asked for a retirement recommendation, but this session's output is the first concrete signal either direction.

**Alternatives considered:**
- **Declare the supersession decision preliminarily after B1** — rejected as overreach. The benchmark explicitly designed 4 rows × 2 postures to prevent single-row conclusions. A preliminary declaration would preempt Phase 4 aggregate scoring.
- **Defer all interpretation to Phase 4** — rejected as under-reporting. The signal is real; capturing it now as "positive, pending" helps shape subsequent row reviews (what to watch for, what would falsify).
- **Treat candidate's cleaner output as a documentation/observability advantage only** — rejected because the differences (scope discipline, scouting behavior) are architectural, not cosmetic. They reflect the supersession's hypothesis about MCP-native dispatch vs prompt-layer enforcement.

**Trade-offs accepted:** Recording a directional signal introduces a small anchoring risk for subsequent-row reviews (I might look for confirming evidence). Mitigated by explicitly naming the three dimensions, which keeps falsification criteria concrete: a row where baseline has cleaner scope discipline OR higher scout count OR more structured claims would falsify the direction.

**Confidence:** Medium (E1). One row of data, strong qualitative differences, but sample size is 1 of 4.

**Reversibility:** High — subsequent rows can shift the direction; Phase 4 aggregate scoring is the authoritative verdict.

**Change trigger:** B3 or B5 data showing the baseline outperforming the candidate on any of the three dimensions. Or B8 (supersession analysis posture) producing a direct counter-verdict.

## Changes

No file commits this session. Reading-and-review only; all the commits that would change repo state (`f0fde082` run_commit update, `fa75111b` operator-procedure amendment) landed in the first half of this session (captured in the 11:48 handoff).

Staging directory edits: none. B1 candidate metadata was recorded correctly by the operator — no `evidence_count` correction required (contrast with B1 baseline's 10→0 edit).

Working tree remains clean at `fa75111b`.

## Codebase Knowledge

### B1 candidate vs baseline — per-dimension comparison

| Dimension | Baseline | Candidate | Winner |
|---|---|---|---|
| `evidence_count` (pipeline-data `scout_count`) | 0 | 5 | Candidate exercises scouting; baseline doesn't |
| Budget utilization | 0/5 (0%) | 5/15 (33%) | Candidate uses larger budget meaningfully |
| T1 scout timeout | 1 attempted, timed out | 0 timeouts | Candidate avoids baseline's failure mode |
| Codex `cmd:` exec (in-scope) | ~12 | 18 | Candidate does more work in-scope |
| Codex `cmd:` exec (out-of-scope) | 8+ | 1 (file-discovery edge case) | **Candidate ~dramatically better** |
| Scope-escape tracking | Prose only | Structured + terminal threshold | **Candidate has instrumentation** |
| Convergence mode | Natural at T5 | Natural at T5 | Parity |
| Dialogue framing | 3-way split by impl status | Contract/milestone 2-lens | **Candidate semantically sharper** |
| Claim ledger | Synthesis Checkpoint tags | `final_claims[]` with `final_status` | **Candidate machine-adjudicable** |
| Pre-dialogue briefing | 10 citations (implicit) | 20 citations, 0 unknown | Candidate denser and quality-flagged |
| Mode | `server_assisted` | `agent_local` | Different (by design) |
| Wall time | ~20 min | ~20 min | Parity |
| Thread ID | `019d96d2-4397-79e0-9fd0-77877a44df5a` | `019d96ff-44b2-7dd3-ae9a-6fe16293f592` | Distinct (no session reuse) |

### The corpus structure (v1 canonical)

| Row ID | Category | Posture | Turn budget | Primary allowed_roots |
|---|---|---|---|---|
| B1 | Architecture review | evaluative | 6 | contracts.md, delivery.md, mcp_server.py |
| B3 | Code review | adversarial | 6 | context_assembly.py, test_context_assembly.py, ticket |
| B5 | Policy audit | evaluative | 6 | advisory-runtime-policy.md, control_plane.py, runtime.py |
| B8 | Supersession analysis | comparative | 8 | 3 anchored groups (baseline, candidate normative, candidate runtime) |

Gaps (B2, B4, B6, B7) are deferred per contract :86-87. Numbering preserved for Change Control restorability.

### Corpus compliance gate (T4-CT-02)

Per `dialogue-supersession-benchmark.md:159-163`, a row is v1-compliant only if one of:
1. **Single-root by construction** — the prompt names or implies a single anchor group (B1, B3, B5)
2. **Deterministically cross-root under T4-CT-02** — mechanical scope union without judgment calls (theoretical; none used)
3. **Path-anchored decomposition** — explicit groups with scouting allowed only within a single group at a time (B8)

The deferred rows failed all three. The contract explicitly rejects the alternative of "inventing a benchmark-only root-selection rule" (§99-102) that would have forced non-compliant rows into compliance via bespoke workarounds.

### Candidate architectural advantages (structural, not operational)

From the B1 candidate synthesis:

| Feature | Location in artifact | Role |
|---|---|---|
| `scope_envelope` declared | synthesis:12 | Binds agent-side Glob/Grep/Read to declared paths |
| Escape terminal threshold | synthesis:27 | 3 escapes = terminal (invalidating); 2 = below-threshold |
| `final_claims[]` array | synthesis JSON epilogue | Per-claim status (supported/ambiguous/unverified) + citation |
| `synthesis_citations[]` | synthesis JSON epilogue | Tier-labeled citations (`citation_tier: dialogue`) |
| `ledger_summary` | synthesis JSON epilogue | Aggregate metrics: total claims, supported, ambiguous, unverified, escape count |

These are T4-state-model-native artifacts. The baseline produces a looser `Synthesis Checkpoint` block with RESOLVED/UNRESOLVED/EMERGED tags in prose.

### B3 row specifics (next session's target)

From `invocations.md:72-107` (already pre-built, ready to paste after `{run_type}` substitution):

- **Category:** Code review
- **Posture:** adversarial
- **Turn budget:** 6
- **allowed_roots:**
  - `packages/plugins/codex-collaboration/server/context_assembly.py`
  - `packages/plugins/codex-collaboration/tests/test_context_assembly.py`
  - `docs/tickets/2026-03-30-context-assembly-redaction-hardening.md`
- **Prompt:** "Review the current context assembly redaction implementation for remaining coverage gaps or false-positive risks that still matter for Codex prompt safety."
- **Baseline max_evidence:** 5
- **Candidate max_evidence:** 15

### Relevant helper script

The user authored `/private/tmp/benchmark-v1-staging-20260415/_extract_transcript.py` (5733 bytes, 12:06 mtime) to extract the candidate transcript from Codex's session rollout JSONL (`/Users/jp/.codex/sessions/2026/04/16/rollout-2026-04-16T11-53-24-019d96ff-...jsonl`). For future rows, this script will be the canonical extraction mechanism. Details: 114 JSONL entries, 10 messages, 23 tool calls per the candidate transcript preamble.

## Context

### Current T-04 acceptance criteria status

| AC | Description | Status |
|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) |
| 3 | Gatherer agents exist | Done (PR #107) |
| 4 | Synthesis with bounded citations | Done |
| 5 | Benchmark contract executed on fixed corpus | **1 of 4 pairs complete (B1); 3 remaining (B3, B5, B8)** |
| 6 | Benchmark result recorded with per-task metrics | Open; depends on AC-5 |
| 7 | Context-injection retirement decision | Open; depends on AC-6. **Directional signal positive after B1.** |

### Mental model for this session

This was a **review + synthesis** session, not a **build** session. The work was interpreting existing artifacts against the contract, then synthesizing a comparative signal from them. Three things made it substantive despite no code changes:

1. **The B1 pair comparison is the first data point for the supersession hypothesis.** Qualitative differences (scope discipline, scouting behavior, output structure) map directly to the architectural thesis the benchmark was designed to test. Recording those differences now (in this handoff's §Codebase Knowledge → Candidate architectural advantages) creates the baseline for B3/B5/B8 comparison.

2. **The B2-vs-B3 question was a contract-integrity check.** The user's prompt exposed that the prior handoff had used shorthand ("B1-B8 pairs") where precision was warranted. Resolving it via contract archaeology prevented a potential ambiguity from propagating into later operator instructions.

3. **The fa75111b amendment had its first operator test.** B1 candidate's `evidence_count: 5` (correctly the pipeline-data scout count, not briefing-gatherer sum or Codex exec count) proves the amendment prevented the same reconciliation the first half of this session performed on B1 baseline's `evidence_count: 10`.

### Environment snapshot

- Branch: `main`
- HEAD: `fa75111b` (unchanged since 11:48 handoff)
- Working tree: clean
- Staging directory: `/private/tmp/benchmark-v1-staging-20260415/` intact with 6 files (baseline 3, candidate 3) plus helper script and `invocations.md`
- `~/.claude/plugins/data/codex-collaboration-inline/session_id` file exists and produces canonical session IDs on fresh session starts

### Open tickets

| Ticket | Status | Next |
|---|---|---|
| T-04 Dialogue parity & scouting retirement | Open; AC 1-4 done, AC-5 at 1/8 valid runs | Run B3 pair |
| T-05 Execution-domain foundation | Open (unstarted) | Separate workstream |
| T-06 Promotion flow & delegate UX | Open (blocked by T-05) | — |
| T-07 Analytics reviewer & cutover | Open | Separate workstream |

## Learnings

### Candidate architectural advantages are structural, not documentation

**Mechanism.** The candidate tracks scope-escapes as a structured metric with an explicit terminal threshold. It emits `final_claims[]` with per-claim `final_status` and citations. It reports `<!-- pipeline-data -->` `scout_count` identically to T4 state-model conventions. The baseline emits equivalent information in prose only. These differences reflect architectural choices (MCP-native dispatch, state-model-aligned emission) vs documentation verbosity.

**Evidence.** B1 candidate synthesis line 27: "2 grep scope-escapes observed (ripgrep `path` parameter ignored, searched repo-wide instead of restricted to allowed file) — below the 3-escape terminal threshold." Structured. B1 baseline synthesis line 84: "those citations function as *testimony*, not *verified evidence*. The core claims... are all defensible from `contracts.md` + `delivery.md` alone." Prose.

**Implication.** Phase 3 adjudication will be materially faster against the candidate's artifacts — claims are enumerated with status, citations are tier-labeled. For the supersession decision, the candidate's observability is itself a supersession argument (not just its behavior). The benchmark should surface this in Phase 4 aggregate scoring, not just individual claim adjudication.

**Watch for.** If B3/B5/B8 candidates also produce structured claim ledgers, the observability advantage is architectural. If one candidate row doesn't, it's a regression worth investigating before aggregation.

### Contract-authoritative definitions need to propagate to operator-visible surfaces

**Mechanism.** The fa75111b amendment (committed earlier this session) defined `evidence_count` at the point operators enter metadata values, explicitly excluding the three commonly-confused surfaces. The B1 candidate was the first operator action after the amendment — and the recorded `evidence_count: 5` matches the pipeline-data scout_count cleanly. No reconciliation needed.

**Evidence.** Baseline (pre-amendment): `evidence_count: 10` recorded, required a reconciliation session to discover this conflated briefing-gatherer sum with agent scout count. Candidate (post-amendment): `evidence_count: 5` recorded directly from pipeline-data. Delta = amendment value.

**Implication.** For other potentially-ambiguous fields in the metadata template (`actual_turns`, `effective_posture`, `session_id_canonical`), consider proactive amendment rather than waiting for ambiguity to surface. The pattern from fa75111b: bold the surface the field measures + "Do NOT include X, Y, Z — those are separate surfaces."

**Watch for.** Other fields that have "turn" or "session" or "evidence" in them without explicit surface binding. The ambiguity only surfaces under specific conditions (baseline had 0 scouts + 10 briefing citations; if B3 baseline has 1 scout + 7 briefing, the ambiguity on `evidence_count` would have been less obvious).

### Corpus numbering preservation is semantically load-bearing

**Mechanism.** The benchmark corpus is identified as B1/B3/B5/B8 (not B1-B4). The gap numbering preserves the original 8-row design intent and reserves deferred rows (B2, B4, B6, B7) for Change Control restoration with identity intact.

**Evidence.** Contract `dialogue-supersession-benchmark.md:86-87`: "Rows `B2`, `B4`, `B6`, and `B7` are deferred from benchmark v1. They may be restored only through contract amendment under Change Control." Contract :104-105: "Deferred rows... outside benchmark v1... no scored-run obligations under this contract revision." The language explicitly distinguishes "deferred" (restorable) from "rejected" (permanent).

**Implication.** Operator-facing instructions must reference the canonical IDs, not positional shorthand ("next row" works; "row 2" risks confusion with B2, which isn't in v1). The 11:48 handoff's §Next Steps #2 used shorthand "B1-B8 pairs" — this handoff corrects to "B1/B3/B5/B8 pairs."

**Watch for.** Any future benchmark whose corpus is a pruned subset of an intended design. Preserve identity numbering + explicit deferral language + Change Control gate = correct pattern. Do not renumber to close the gaps.

### One-row signal can be directionally strong without being conclusive

**Mechanism.** B1 produced strong qualitative differences on the three dimensions the benchmark cares about. But the benchmark's design (4 rows × 2 postures) is precisely what prevents single-row conclusions — row-specific effects can produce local differences that don't generalize.

**Evidence.** B1 is evaluative-posture architecture-review — the posture/category combination most favorable to the candidate's contract-lens framing (contracts.md and delivery.md have explicit authority frontmatter, which the candidate's "contract vs milestone" framing directly leverages). B3's adversarial posture tests whether the candidate's structural advantages hold under a different cognitive mode; B5 tests policy-audit; B8 tests comparative supersession-analysis.

**Implication.** Record B1's signal as directional and capture falsification criteria. Do not issue the retirement recommendation yet. The Phase 3-5 adjudication path is the authoritative verdict.

**Watch for.** Confirmation-bias risk in B3/B5/B8 reviews. Actively look for evidence that contradicts the B1 direction (e.g., baseline outperforming candidate on scope discipline in an adversarial posture). If such evidence appears, it's a valuable finding, not a defect.

## Next Steps

### 1. B3 baseline prep and run (critical path, session opener)

**Dependencies:** None. All prerequisites met — runtime gate cleared, `run_commit` at `693551cc` (manifest), amendment live, B1 pair complete.

**What to do in the next session's opening turn:**
1. Paste the B3 baseline invocation from `/private/tmp/benchmark-v1-staging-20260415/invocations.md:76-89` with `{run_type}` → `This is a scored benchmark run.`
2. **Exception to "this session" rule:** The B3 baseline run **requires a fresh Claude session** per operator-procedure.md:174 — it cannot happen in the session that resumes this handoff. Resume session should surface the invocation and cut the operator loose to run it in a *different* fresh session. Same pattern as B1 candidate handoff.

**Pre-built invocation (substitute `{run_type}` → `This is a scored benchmark run.`):**

```
/cross-model:dialogue "BENCHMARK SCOPE CONSTRAINT: {run_type} Limit all evidence gathering (Glob, Grep, Read) to the following paths only. Do not scout outside these paths.

Allowed paths:
- packages/plugins/codex-collaboration/server/context_assembly.py
- packages/plugins/codex-collaboration/tests/test_context_assembly.py
- docs/tickets/2026-03-30-context-assembly-redaction-hardening.md

EVIDENCE BUDGET: Complete at most 5 evidence records.
POSTURE: adversarial

---

Review the current context assembly redaction implementation for remaining coverage gaps or false-positive risks that still matter for Codex prompt safety." -p adversarial -n 6
```

**What to read first (in the resume session before handing off to fresh session):**
- This handoff's §Codebase Knowledge → B3 row specifics and Candidate architectural advantages tables
- `/private/tmp/benchmark-v1-staging-20260415/invocations.md:72-107` (baseline + candidate invocations pre-built)
- operator-procedure.md:168-343 (Phase 2 execution procedure, unchanged from B1)

**Per-session checklist (operator executes in the fresh session):**
1. Fresh `claude` session
2. `cat ~/.claude/plugins/data/codex-collaboration-inline/session_id` → record
3. Paste invocation (substituted)
4. Wait (~5-10 min expected; 693551cc stdin fix applies, so no 15-min hang)
5. Export transcript → `B3-baseline-transcript.md`, synthesis → `B3-baseline-synthesis.md`
6. Write metadata with `evidence_count` = pipeline-data `scout_count` (fa75111b amendment)

**Comparison targets (from B1 baseline, for watching divergence):**
- Did Codex exec stay in scope? (B1 baseline: 8+ out-of-scope; did B3 improve or worsen?)
- Did the agent scout? (B1 baseline: 0 scouts; B3 adversarial may push differently)
- Convergence mode? (B1 baseline: natural at T5; adversarial may exhaust budget)

**Potential obstacles:**
- **New baseline-system issue surfacing:** B3 is the first adversarial-posture run on the adversarial gatherer agent (`context-gatherer-falsifier` in particular). Issues may surface that didn't hit B1's evaluative flow. Budget 15 min for triage.
- **Context-assembly redaction is safety-critical:** B3's scope includes the ticket `2026-03-30-context-assembly-redaction-hardening.md` — any claimed "coverage gap" findings must be reviewed carefully in Phase 3, as they touch safety posture directly.

### 2. B3 candidate prep and run (after B3 baseline valid)

**Dependencies:** B3 baseline complete and valid.

**What to do:** Paste B3 candidate invocation from `invocations.md:92-107` (same scope, `/codex-collaboration:dialogue` skill, `max_evidence: 15`). Fresh session.

**What to read first:** Same as B3 baseline. B3 baseline's synthesis narrative will inform what falsification probes the adversarial posture produced against context-assembly redaction, which the candidate run may or may not reproduce.

**Comparison targets:** same three dimensions as B1 (scope, scouting, structure) plus posture-specific: does adversarial posture in the candidate produce structurally different counter-claims vs baseline?

### 3. B5 pair (policy audit, evaluative), then B8 pair (supersession, comparative)

**Dependencies:** Sequential; each pair after the prior is valid. B8 uses anchored decomposition (3 path groups).

**What to do:** Same pattern as B1/B3. Each pair: fresh session for baseline, fresh session for candidate, no repo writes between them in a pair.

**Special note for B8:** Anchored decomposition rule — "Each scouting step must target a path within one group. Cross-group reasoning is expected; cross-group target expansion is not" (invocations.md). Transcript review in Phase 3 must verify no cross-group target expansion.

### 4. Phase 3-5 adjudication after all 8 runs valid

**Dependencies:** All 4 pairs valid.

**What to do:** operator-procedure.md §3 (claim inventory, labeling, safety, completeness, scope compliance review) → §4 (aggregate scoring) → §5 (import to repo).

**Potential obstacles:** Manual adjudication dominant cost (2-4 hours). Row-by-row keeps context fresh; prefer high-signal rows first (B3 safety, B8 supersession).

### 5. Retirement decision (AC-7) after Phase 4

**Dependencies:** Phase 4 aggregate metrics recorded.

**What to do:** Render retirement decision per T-04 ticket's AC-7. Current directional signal is positive for supersession (B1 evidence). If B3/B5/B8 confirm, the decision is defensible. If one or more rows contradict, reassess.

## In Progress

**Clean stopping point — B1 pair complete, B3 ready for fresh session.**

- **Approach:** Review-and-validate pattern: consume out-of-session artifacts, validate against contract, produce comparison signal, prep next row.
- **State:** B1 pair both valid. B1 baseline metadata `evidence_count: 0, valid: true`; B1 candidate metadata `evidence_count: 5, valid: true`. Staging intact. No working-tree changes.
- **Working:** fa75111b amendment proved effective on first post-commit operator action. B1 comparison matrix produced. Corpus-numbering ambiguity resolved via contract archaeology.
- **Not working:** Nothing broken. Three pairs remaining (B3, B5, B8), but that's expected progress, not a defect.
- **Next action:** Operator opens fresh `claude` session, pastes B3 baseline invocation from this handoff's §Next Steps #1, runs to completion, exports artifacts, returns to a review session (this resume session or a new one).

## Open Questions

### 1. Will B3 baseline surface new baseline-system issues (analogous to B1's stdin hang)?

**Context:** B1 baseline first-run triggered the codex subprocess stdin hang, which required `693551cc` to fix. B3's adversarial posture exercises `context-gatherer-falsifier` — a different code path from B1's evaluative gatherer pair. Latent issues may exist.

**Impact:** Moderate. Each incident requires patch → commit → update `run_commit` → rerun.

**Decision pending until:** B3 baseline first-run.

### 2. Does the candidate maintain scope discipline under adversarial posture?

**Context:** B1 candidate (evaluative) had strong scope discipline (1 file-discovery edge case, 0 substantive out-of-scope). Adversarial posture pushes harder on falsification, which might incentivize Codex to search more broadly for counter-evidence.

**Impact:** High for supersession signal. This is a direct test of whether the candidate's scope enforcement is architectural (holds across postures) or incidental (breaks under pressure).

**Decision pending until:** B3 candidate review.

### 3. Should briefing-gatherer count be preserved as a non-contract metadata field? (Carried from 11:48 handoff)

**Context:** Corrected B1 baseline metadata no longer records the 10 per-gatherer count. Signal preserved in synthesis narrative and transcript. Adding `briefing_evidence_records` to metadata would preserve it structurally but introduces out-of-contract field surface.

**Impact:** Low. Phase 3 adjudicators can reconstruct from synthesis.

**Decision pending until:** Phase 3 reconstruction effort. If costly, add retroactively to all rows.

### 4. Should `scope_envelope` be wired through the candidate skill? (Carried forward)

**Context:** Both gatherer agents support `scope_envelope` but the candidate skill doesn't pass it. v1-compliant (prompt-only) but a known fragility.

**Impact:** Low for v1.

**Decision pending until:** After benchmark execution.

### 5. Does the "positive for supersession" directional signal persist across postures?

**Context:** B1 is evaluative — the posture most favorable to the candidate's contract/milestone two-lens framing because the spec has explicit authority frontmatter. B3 (adversarial), B5 (evaluative-policy), B8 (comparative) test different cognitive modes.

**Impact:** High. This is the actual question the benchmark is designed to answer.

**Decision pending until:** All 4 pairs complete and adjudicated.

## Risks

### 1. Confirmation bias risk in B3/B5/B8 reviews

**Impact:** Having recorded B1 as "positive for supersession," subsequent reviews may unconsciously weight evidence toward confirmation. Could produce a retirement recommendation that's not robust to contradictory signal.

**Mitigation:** Each row review should explicitly check for baseline-favorable evidence on the three dimensions (scope, scouting, structure). If a row shows baseline advantage, record it as-is — don't discount. Phase 4 aggregate scoring is the authoritative verdict.

### 2. `/tmp/` staging reboot vulnerability (carried forward)

**Impact:** Machine reboot clears `/private/tmp/`, losing B1 artifacts. Phase 5 import relies on staging intactness.

**Mitigation:** Before extended breaks, `cp -r /private/tmp/benchmark-v1-staging-20260415 ~/benchmark-v1-staging-backup`.

### 3. Codex-collaboration MCP server has latent issues not yet surfaced

**Impact:** `693551cc` fixes cross-model's subprocess path. The codex-collaboration server uses separate plumbing. Unknown whether analogous bugs exist.

**Mitigation:** Triage candidate-side hangs as separate bugs, not stdin-fix scope.

### 4. Baseline-system latent issues may surface during remaining runs (carried forward)

**Impact:** Each row's first-run is a gate for latent baseline-system bugs. Each incident = patch-commit-update-rerun cycle.

**Mitigation:** Time-box 15 min per incident.

### 5. Manual adjudication dominant cost (carried forward)

**Impact:** 4 rows × 2 systems = 8 syntheses, 80-160 claim adjudications, 2-4 hours.

**Mitigation:** Row-by-row, high-signal rows first.

### 6. `run_commit` drift if HEAD advances between sessions (carried forward)

**Impact:** Additional commits land, manifest `run_commit: 693551cc` falls behind HEAD.

**Mitigation:** Opening check of next session: `git log --oneline -10` vs `manifest.json:7`. Update only for materially benchmark-relevant changes.

## References

### Commits this session

No commits this half (the 11:48 handoff captured `f0fde082` and `fa75111b`).

### Authority documents

| Document | Location | Role |
|---|---|---|
| Benchmark contract v1 | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Corpus structure (§86-87, §99-105, §159-163); evidence_count unit (§188) |
| Operator procedure | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | Execution procedure; fa75111b amendment at §2.4 |
| Manifest | `docs/benchmarks/dialogue-supersession/v1/manifest.json` | `run_commit: 693551cc`; 4-row corpus structure |
| T4 state model | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/` | `evidence_log`/`scout_count` definitions; corpus-compliance rationale |
| Supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | T-04 acceptance authority |

### Staging artifacts (B1 pair complete)

| Artifact | Path | Status |
|---|---|---|
| Invocations packet | `/private/tmp/benchmark-v1-staging-20260415/invocations.md` | Unchanged; contains all 8 invocations |
| Transcript extractor | `/private/tmp/benchmark-v1-staging-20260415/_extract_transcript.py` | User-authored; 5733 bytes |
| B1 baseline transcript | `/private/tmp/benchmark-v1-staging-20260415/B1-baseline-transcript.md` | 2091 lines, intact |
| B1 baseline synthesis | `/private/tmp/benchmark-v1-staging-20260415/B1-baseline-synthesis.md` | 127 lines, intact |
| B1 baseline metadata | `/private/tmp/benchmark-v1-staging-20260415/B1-baseline-metadata.json` | `evidence_count: 0`, `valid: true` |
| B1 candidate transcript | `/private/tmp/benchmark-v1-staging-20260415/B1-candidate-transcript.md` | 1736 lines, intact |
| B1 candidate synthesis | `/private/tmp/benchmark-v1-staging-20260415/B1-candidate-synthesis.md` | 161 lines, intact |
| B1 candidate metadata | `/private/tmp/benchmark-v1-staging-20260415/B1-candidate-metadata.json` | `evidence_count: 5`, `valid: true` |

### Prior handoffs (chain)

- Immediate predecessor: `docs/handoffs/2026-04-16_11-48_t04-b1-baseline-valid-after-evidence-count-reconciliation.md` (same session; earlier save after baseline review + operator-procedure amendment)
- Prior: `docs/handoffs/archive/2026-04-16_00-18_t04-runtime-gate-cleared-b1-baseline-pending-rerun.md`
- Earlier arc: `docs/handoffs/archive/2026-04-15_*` and `2026-04-14_*` for T-04 scaffold / contract rewrite / Phase 1 prep

### Codex session rollout (B1 candidate)

- Path: `/Users/jp/.codex/sessions/2026/04/16/rollout-2026-04-16T11-53-24-019d96ff-44b2-7dd3-ae9a-6fe16293f592.jsonl`
- 114 JSONL entries, 10 messages, 23 tool calls per candidate transcript preamble
- Run ID: `31c68027-f74a-4343-a835-b8aa1e989f5d`
- Collaboration ID: `86f72ef2-8bb1-42e7-8131-d7cffb58607a`

## Gotchas

### Corpus IDs are non-contiguous by design (B1/B3/B5/B8, not B1-B4)

**Symptom:** Operator reading operator-procedure shorthand like "proceed through B1-B8 pairs" may expect to run B2, B4, B6, B7.

**Root cause:** The contract deliberately pruned the original 8-row design to 4 rows under T4-CT-02 corpus-compliance. Numbering preserved for Change Control restorability.

**Prevention:** Always reference canonical IDs (B1, B3, B5, B8), never positional ("next row" OK; "row 2 of 4" risks ambiguity with B2). Future benchmark instructions should enumerate explicitly.

### `evidence_count` unit is pipeline-data `scout_count`, not any of three tempting alternatives

**Symptom:** Operator may reasonably compute `evidence_count` as briefing-gatherer total (10 for baseline), aggregate CLAIM count, or Codex exec count — all wrong.

**Root cause:** Three evidence surfaces exist in `/cross-model:dialogue`; only the agent's `evidence_log` (= pipeline-data `scout_count`) is contract-bound.

**Prevention:** fa75111b amendment to operator-procedure.md §2.4. B1 candidate metadata (`evidence_count: 5`) is the first correctly-recorded instance; watch B3 metadata for reoccurrence of any confusion.

### Candidate transcript uses JSONL-derived format (not matching baseline's format)

**Symptom:** Regex patterns that worked on B1 baseline transcript (e.g., `^cmd:` anchor) return 0 matches on B1 candidate transcript.

**Root cause:** Candidate transcript is extracted from Codex session rollout JSONL via user's `_extract_transcript.py`. Format has leading whitespace, JSON quoting, etc. that breaks strict anchors.

**Prevention:** When analyzing candidate transcripts, use permissive patterns (`cmd:` not `^cmd:`, broader character classes). Or just read sections directly and enumerate manually.

### Agent-side scope-escapes and Codex-exec scope-escapes are different surfaces

**Symptom:** Candidate synthesis says "2 grep scope-escapes observed" but Codex exec calls touched 1 out-of-scope target too. Is that 2 or 3 escapes?

**Root cause:** The "2 escapes" count refers to agent-side Grep tool calls where the `path` parameter was ignored by the MCP tool implementation. Codex's autonomous `codex exec` sandbox is a separate surface (contract §51-52: "prompt-only" enforcement). The synthesis correctly tracks only the agent-side surface in its terminal-threshold count.

**Prevention:** For Phase 3 adjudication, review both surfaces independently. The agent's `scope_breach_count` field (pipeline-data, when the T4 state model is fully active) captures agent surface; Codex exec scope is reviewed via transcript audit.

### `resumed_from` chain breaks on multi-save-per-session

**Symptom:** This handoff has no `resumed_from` field even though it follows `2026-04-16_11-48_t04-b1-baseline-valid-after-evidence-count-reconciliation.md` in the same session.

**Root cause:** `resumed_from` is populated only when `/load` writes a state file that `/save` subsequently reads. The 11:48 save cleaned up the state file. A second save in the same session has no state file to read, so `resumed_from` is empty.

**Prevention:** Filename timestamps establish implicit ordering. When reconstructing a chain across multiple saves in a session, use the `files:` frontmatter field to reference the predecessor handoff.

## Conversation Highlights

### User's artifact handoff

User: "All three candidate artifacts now exported to /tmp/benchmark-v1-staging-20260415/"

Minimal, factual, implicit ask for review. Same pattern as "I ran baseline B1, the results are present at...". Pattern: runs happen out-of-session, artifacts land in known location, review happens in-session. The review ask is open-ended ("give me your feedback"), enabling definitional ambiguities or structural observations to surface rather than narrow pass/fail checks.

### User's B2-vs-B3 question

User: "Why B3 and not B2?"

The most valuable prompt of this session half. A four-word question that exposed imprecise shorthand in the prior handoff's §Next Steps ("B1-B8 pairs") and prompted contract archaeology to surface the corpus-compliance pruning rationale. Pattern: short open-ended questions from the user are often pointing at something imprecise in prior output, not asking for explanation of the obvious.

### User's handoff directive

User: `/copy` followed by `/handoff:save` with args "save a handoff and pick up from here in the next session, beginning with B3 prep"

`/copy` preserved the B2-vs-B3 explanation for potential reuse. `/handoff:save` with the explicit "beginning with B3 prep" sets the next session's opening action deterministically — the handoff's §Next Steps #1 needs to be B3 prep, not generic "next row."

## User Preferences

### Contract-first resolution over procedural reasoning

When the B2-vs-B3 question came up, the user-valued response path was contract archaeology (grep the benchmark contract for authoritative rationale) rather than procedural reasoning ("next integer") or improvisation ("let me check the invocations file"). This is consistent with prior-session patterns — contract text is authoritative, and operator questions should route through contract references rather than being answered from inference.

### Short open-ended questions signal imprecise prior output

"Why B3 and not B2?" / "it may actually be a more recent commit than 8243693b, it's worth checking" — both are four-to-twelve-word questions that exposed something subtly wrong in prior handoff state. Response pattern: treat these as correction prompts, check what the prior output said, and resolve via authoritative source.

### Explicit session-transition directives

User: "save a handoff and pick up from here in the next session, beginning with B3 prep"

Not a generic handoff — an explicit directive that the handoff's continuation point should be B3 prep. Response pattern: make sure §Next Steps #1 is specifically B3 prep with paste-ready invocation, not a generic "run next row."

### Copy-then-save pattern

User: `/copy` before `/handoff:save` in both saves this session. The `/copy` preserves operational artifacts (prep packages, explanations) for reuse in a fresh session. The `/handoff:save` then captures session state. Together they provide two forms of continuity: structured (handoff file) and operational (clipboard content for paste-in).

### Review-request openness

User: "Please review and give me your feedback" (for baseline) and "now exported..." (for candidate, implicit review request). Open-ended rather than narrow. Enables structural observations, definitional ambiguities, and architectural patterns to surface rather than reducing reviews to pass/fail checks. This is how the B1 candidate's structural advantages became visible — if the review had been "is this valid yes/no," the architectural signal would have been lost.

### Pace preference: substantive session halves rather than many short sessions

This session accumulated ~254k tokens before saving. Both saves occurred at natural completion points (B1 baseline valid + amendment committed; B1 pair complete + next row set up) rather than at context-pressure thresholds. Response pattern: don't save for save's sake; save when a stopping point makes sense for future-Claude continuity.

### Collaborative peer, not passive executor (global preference, exercised)

From `~/.claude/CLAUDE.md`: "Be a collaborative peer, not a passive executor."

This session's exercises:
- Surfacing three readings of `evidence_count` before picking one (first half)
- Producing a comparison matrix rather than a pass/fail verdict for B1 candidate (this half)
- Capturing the supersession signal as "positive, pending" with explicit falsification criteria rather than either (a) preemptively issuing a retirement recommendation or (b) deferring all interpretation to Phase 4
- Identifying and resolving the B2-vs-B3 corpus-numbering imprecision rather than waiting to be asked
