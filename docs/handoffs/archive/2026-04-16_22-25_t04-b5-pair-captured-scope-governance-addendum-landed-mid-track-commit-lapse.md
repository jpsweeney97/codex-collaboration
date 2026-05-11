---
date: 2026-04-16
time: "22:25"
created_at: "2026-04-16T22:25:50Z"
session_id: f3cf5929-6d41-4dad-ae38-8b0e864d51c6
resumed_from: "docs/handoffs/archive/2026-04-16_19-27_t04-b3-pair-complete-extraction-bug-ticketed.md"
project: claude-code-tool-dev
branch: docs/t20260330-scope-rule-governance-note
commit: 4c0e2a46
title: "T-04 B5 pair captured; scope-governance addendum landed; mid-track commit lapse surfaced; B8 prep next (freeze repo state)"
type: handoff
files:
  - /private/tmp/benchmark-v1-staging-20260415/B5-baseline-metadata.json
  - /private/tmp/benchmark-v1-staging-20260415/B5-baseline-synthesis.md
  - /private/tmp/benchmark-v1-staging-20260415/B5-baseline-transcript.md
  - /private/tmp/benchmark-v1-staging-20260415/B5-candidate-metadata.json
  - /private/tmp/benchmark-v1-staging-20260415/B5-candidate-synthesis.md
  - /private/tmp/benchmark-v1-staging-20260415/B5-candidate-transcript.md
  - docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md
  - docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md
  - /Users/jp/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_contract_text_over_operational_interpretation.md
  - /Users/jp/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_no_midtrack_doc_commits.md
---

# T-04 B5 Pair Captured; Scope-Governance Addendum Landed; Mid-Track Commit Lapse Surfaced; B8 Prep Next (Freeze Repo State)

## Goal

Run the B5 pair (policy audit, evaluative), review both artifacts against the contract, triage any findings without contaminating the benchmark, and advance toward T-04 AC-5 completion (B8 pair next). The session was scoped at load time to "begin with B5 prep" per the 19:27 handoff's explicit directive.

**Trigger.** The 19:27 handoff left B3 pair complete with extraction-bug ticket committed, and named B5 prep as the next session's opening action. This session loaded that handoff, executed the B5 pair (baseline → review → candidate → review → governance addendum draft → landing), and surfaced a material contract-text finding that reclassified the previous two review sessions' "valid: true" classifications as provisional pending T-20260330-04 governance decision.

**Stakes.** T-04 AC-5 requires all four pairs (B1, B3, B5, B8) to execute on the fixed corpus. B5 is the second evaluative-posture pair and the cross-posture calibration against B1 — does baseline's scope-compliance profile correlate with topic or posture? The session produced consequential evidence: B5 baseline revealed that Codex-side out-of-scope scouting is topic-driven (not posture-driven) AND, under the benchmark contract's strict reading, retroactively invalidates all three baseline classifications so far. This forced a governance-level intervention mid-track.

**Success criteria:**

1. ✅ B5 baseline validated against contract; review produced (initially as valid, subsequently revised to provisional)
2. ✅ B5 candidate validated-as-recorded per pathology-preservation rule; extraction-bug reproduction documented
3. ✅ Contract-vs-architecture incompatibility surfaced; governance addendum drafted, reviewed (one P1/P2/P3 pass → three targeted edits → commit), landed in T-20260330-04
4. ✅ Benchmark-status vs product-defect split preserved across both axes (scope-rule dispute + same-commit breach)
5. ✅ Handoff prepared before B8 so context is preserved and session posture is fresh for the longest row

**Not met:**

1. ❌ Mid-track commit discipline. I committed the governance addendum at `4c0e2a46` during an active benchmark track, creating a new commit drift between B5 baseline (pre-commit) and B5 candidate (post-commit). The user flagged this as a run-condition breach in the B5 candidate packet. **This lapse is memory-worthy** and has been saved.

**Connection to project arc.** T-04 is the empirical gate for cross-model dialogue+context-injection retirement. B5 is the third of four pairs. The B5 signal advances two threads: (1) architectural signature continues to hold — candidate maintains 0 agent-side out-of-scope scouts across all three posture types so far; (2) the baseline's Codex-delegation architecture is now formally documented as contract-incompatible under strict reading, forcing an explicit governance decision before AC-6 can close. The governance addendum is the mechanism for that resolution.

## Session Narrative

**Phase 1 — Load + B5 baseline prep (~5 min).**

Load resolved the 19:27 handoff, archived it, wrote the state file. Pre-flight: HEAD at `84d79fa6` (ticket branch, not merged to main), staging intact at `/private/tmp/benchmark-v1-staging-20260415/` (12 files from B1 + B3 runs), `invocations.md` containing all 8 pre-built invocations. Surfaced the paste-ready B5 baseline invocation from `invocations.md:116-130` with `{run_type}` → "This is a scored benchmark run." Included pre-flight checks (git drift, staging integrity) and a recommendation to run from the ticket branch (one more doc-only commit, acceptable drift per T-20260330 reconciliation).

**Phase 2 — B5 baseline review (~10 min).**

User returned with baseline artifacts exported (transcript 3659 lines, synthesis 13 KB, metadata 404 B). Initial metadata snapshot clean: `evidence_count: 0, actual_turns: 5, converged_within_budget: true, session_id_canonical: true, valid: true, session_id: f3cf5929-6d41-4dad-ae38-8b0e864d51c6` (this loader session's ID, same pattern as B3 baseline — `/cross-model:dialogue` doesn't fire codex-collaboration's SessionStart hook).

Substantive review findings:
- Structurally richest baseline yet: 27 claims, clean 5/6-turn convergence, `delta_sequence: [advancing × 5]`, zero revised/conceded, 5 unresolved closed.
- Ranked weak-point list with specific code refs: `control_plane.py:432` (hardcoded fingerprint), `control_plane.py:147` (widening rejection), `lineage_store.py:169` (append-only last-wins), `runtime.py` startup literals.
- Baseline transcript header bug still present (`# B1 Candidate` at line 1, same `_extract_transcript.py:54` hardcoded issue from B3).
- **Scope audit findings:** `sed -n '1,220p' foundations.md` and `sed -n '220,340p' foundations.md` (line 856, 1058), `sed -n '1,260p' models.py` (line 1047), `rg -n` hits in `recovery-and-journal.md` and `profiles.py`. Codex was reading substantively out of scope.

Initial verdict: passed as valid. Framed Codex-side out-of-scope reads as "edge-case observation, not invalidation" — citing operator-procedure.md:660-666's agent-side invalidation triggers. Offered comparison table against B1 and B3 baselines, observed the narrowing trend from B3 was posture-correlated noise, recommended proceeding to B5 candidate.

**Phase 3 — Contract pushback and framing correction (~15 min).**

User returned a three-finding code-comment review:
- **[P1]** (0.98): `valid: true` verdict not contract-safe. Cited `dialogue-supersession-benchmark.md:167` ("any out-of-scope scouting in the raw transcript makes the run invalid"), `:282-283` ("Any scouting outside that scope invalidates the run"). My interpretation relied on operator-procedure.md (enforcement-side document) rather than the benchmark contract itself (authority document).
- **[P2]** (unstated confidence but equally sharp): `Run condition breach: PASS (inherited)` was unverified. B5 metadata records no `run_commit`; manifest records `693551cc`; current HEAD `84d79fa6`. I pre-asserted a governance-owned decision without artifact evidence.
- **[P3]** (unstated confidence): `_extract_transcript.py:54` source attribution unverified — I gave filename without path context, user searched repo and couldn't find it.

Verified all three. Contract text DOES say "any out-of-scope scouting in the raw transcript" — no agent-vs-Codex distinction. My prior framing was my own operational layer, not contract-authorized. Verified `_extract_transcript.py` is at `/private/tmp/benchmark-v1-staging-20260415/_extract_transcript.py` (staging helper, not repo) and line 54 matches.

Conceded all three. The retroactive implication is larger than B5: B1 baseline (8+ out-of-scope Codex reads) and B3 baseline (4 out-of-scope, self-flagged at synthesis:111) were both passed under the same flawed interpretation. The benchmark architecture has a contract-text problem, not a row-local problem.

Revised classification: B5 baseline staging metadata preserved as captured (valid: true field untouched), but treated as **preserved as captured, not yet ratified for aggregate use** pending governance decision.

**Phase 4 — Governance addendum drafting and scope (~20 min).**

User accepted the framing correction and directed: hold B5 baseline unclassified, continue to B5 candidate, route governance question inline to T-20260330 (not a new ticket). Explicit user refinements:
- Don't rewrite staging metadata to `valid: null` (contamination risk; procedure doesn't authorize post-hoc mutation for governance disputes)
- Write short inline note in T-20260330 BEFORE B5 candidate runs (architecture-level finding, prevent future sessions from re-leniently re-classifying)
- Keep note bounded: contract citations + retroactive impact + options A/B/C + explicit boundary

Drafted the addendum. User returned with structural + content edits:
- Change heading structure: `## Execution Addendum (2026-04-16)` then `### Open Governance Decision: Scope-enforcement scope` (instead of direct `## Open Governance Decisions`)
- Strengthen status line to explicitly name blocker semantics and candidate continuation
- Replace owner line to tie to AC-6/AC-7 closure boundary
- Change "provisional / superseded" → "preserved as captured, but not yet ratified for aggregate use" (the latter preserves the B-option path where ratification happens via contract amendment)
- User's explicit call: new branch (not the extraction-bug branch), append at end as addendum (not inline between AC and Verification)

User then invoked `/merge-branch` on the current branch (`docs/ticket-dialogue-reply-extraction-mismatch`). Skill executed cleanly: fast-forward `fa75111b` → `84d79fa6`, branch deleted. Created new branch `docs/t20260330-scope-rule-governance-note`, applied the Edit with user-specified text, staged, committed at `4c0e2a46` with descriptive commit message.

**Phase 5 — B5 candidate prep and review (~15 min).**

Provided paste-ready candidate invocation. User ran B5 candidate in fresh session, returned with artifacts:

```json
{"id": "B5-candidate", "evidence_count": 5, "max_evidence": 15,
 "actual_turns": 5, "converged_within_budget": false,
 "termination_code": "error", "valid": true,
 "session_id": "3cd5b5af-1c80-407b-bf03-5705a38a5487",
 "session_id_canonical": true,
 "thread_id": "019d9840-a2b4-72f1-b54d-2eca297b5478",
 "notes": "Terminated on turn 5 due to codex.dialogue.reply parse failure..."}
```

Reviewed:
- Agent-side scope: 0 out-of-scope scouts (all 5 evidence_count citations in-scope) — architectural signature holds across all 3 candidate runs so far.
- Extraction bug reproduced on T5 closing prompt. Different impact than B3: B3 errored at T3 with substantive dialogue incomplete; B5 errored at T5 AFTER Codex's T3 had durably delivered the severity ranking and minimum-amendment set. Only the closing yes/no verdict was lost.
- Codex-side scope (14 exec_command calls): counted 4 wrong-path probes (`packages/codex-collaboration/codex_collaboration/runtime.py` — tree doesn't exist) + 1 broad `rg --files | rg ...` discovery. No substantive out-of-scope evidence entered the synthesis.
- Claim structure: 5 final claims (4 supported + 1 not_scoutable). Sparser than baseline's 27 but severity-labeled (SEVERE / BOUNDED AMBIGUITY / THEORETICAL GAP).

Offered preliminary verdict: same as baseline — preserved as captured, pending governance. Proposed language "same mechanism" for the extraction-bug reproduction. Proposed ticket update options (a/b/c) and handoff posture.

**Phase 6 — Second review pass + three more findings (~10 min).**

User returned with sharper second-pass findings:
- **[P1]** Confirmed via transcript:594-596 that B5 candidate ran on branch `docs/t20260330-scope-rule-governance-note` at commit `4c0e2a4617dda8b4243642f0c0e056fb0b756465`. Manifest still records `run_commit: 693551cc`. Under operator-procedure.md:658, this is a run-condition breach — **independently invalidating** apart from the scope-rule dispute. B5 candidate has TWO blockers, not one.
- **[P2]** "Same mechanism" overstates verification. I only proved same failure signature (empty agent_message → parse failure). The specific B3 root cause (items-array response shape) was not re-proved from B5 artifacts. Honest statement: "same signature, mechanism likely same."
- **[P3]** Strict out-of-scope count undercounted. Transcript shows TWO broad discoveries (`rg --files -g 'AGENTS.md'` at :647 AND `rg --files | rg '...'` at :765), not one. Plus 3 wrong-path reads. Strict literal count is 6 (or 5 if AGENTS discovery is treated as orientation rather than evidentiary).

Verified P1 at transcript:594-596 — exactly matches the commit I made 10 minutes earlier for the governance addendum. This is the governance lapse: writing the scope-rule addendum that explicitly cites `:66` run_commit invariant, then committing it mid-track, creating another commit boundary between B5 baseline and B5 candidate.

Accepted all three. Updated B5 candidate classification: blocked for aggregate on **two independent axes** — scope-rule dispute + same-commit breach. More serious than B5 baseline.

**Phase 7 — User directives for session close (~5 min).**

User explicit direction:
- T-20260416-01 update → option B: defer until post-B8, batch any B5/B8 evidence
- Handoff posture → option A: write handoff NOW before B8
- B8 prep → freeze repo state at `docs/t20260330-scope-rule-governance-note` / `4c0e2a46`, NO more commits before B8 runs

User's rationale for freeze: "Another docs commit before B8 would introduce yet another benchmark commit boundary." The addendum commit already compromised B5 candidate; adding another commit would compromise B8 identically.

Session closing: save memories (pending), write this handoff, end session. B8 prep for next session opening.

## Decisions

### Decision 1: Hold B5 baseline classification as "preserved as captured, not ratified for aggregate"

**Choice:** Treat staging metadata `valid: true` as captured but provisional. Do not mutate the file. Defer scored-validity decision to T-20260330-04 governance addendum.

**Driver:** User's framing: "I would not rewrite the raw B5 staging metadata to `valid: null` unless the procedure explicitly defines post-hoc mutation for governance disputes. The safer move is to preserve the captured artifact as-is and add a governance note that the recorded `valid: true` is provisional / superseded for aggregate use pending T-20260330." Operator procedure does not define such mutation.

**Alternatives considered:**
- Mutate metadata to `valid: null` or `valid: false` — rejected because post-hoc mutation after review isn't procedurally authorized and contaminates audit trail
- Mark as fully valid and proceed — rejected because contract text at `:167-168` and `:282-283` does not distinguish agent-side from Codex-side scouting, and this baseline demonstrably has substantive out-of-scope Codex reads (foundations.md 2x, models.py, recovery-and-journal.md)
- Invalidate and rerun — rejected because this was a governance dispute, not a confirmed invalidation; rerun without governance decision would be premature

**Trade-offs accepted:** Aggregate scoring is now explicitly blocked pending governance decision. This applies uniformly to B1 and B3 baselines too (same contract violation retroactively).

**Confidence:** High (E3). Contract text read directly, staging artifact inspected, precedent preserved.

**Reversibility:** High — governance decision (A/B/C options in addendum) determines final classification.

**Change trigger:** T-20260330-04 renders governance decision.

### Decision 2: Write governance addendum as execution-era append to T-20260330-04

**Choice:** Append `## Execution Addendum (2026-04-16)` at end of ticket, containing `### Open Governance Decision: Scope-enforcement scope` subsection with contract citations, retroactive impact, options A/B/C, and explicit blocker semantics.

**Driver:** User's framing: "This note is not just 'open context'; it is a benchmark blocker. It should say exactly what it blocks." Also: "I would not place it directly under `## Open Governance Decisions` after `## References` with no framing. I would add `## Execution Addendum (2026-04-16)` then your governance subsection(s). This preserves the ticket's original planned shape while making the blocker visible as a later discovered benchmark-governance issue."

**Alternatives considered:**
- Inline insertion between AC and Verification — rejected because co-mingles original intent with mid-execution findings
- Separate ticket (e.g., `T-20260416-02`) — rejected per Decision 5 from 19:27 handoff (governance work belongs to T-20260330, not spawned tickets)
- Update manifest.json to reflect current commit + add governance note there — rejected because manifest is a structured data file; prose decision belongs in ticket

**Trade-offs accepted:** Ticket now has addendum section that may outlive its usefulness once resolved. Mitigation: governance decision closes the section when rendered.

**Confidence:** High (E3). User directive with specific heading structure, status wording, and owner line.

**Reversibility:** High — addendum can be restructured, absorbed into original sections, or migrated to a decision doc once resolved.

**Change trigger:** Governance option (A/B/C) selected and implemented.

### Decision 3: Merge extraction-bug ticket branch to main before governance-note branch

**Choice:** Run `/merge-branch` on `docs/ticket-dialogue-reply-extraction-mismatch` (fast-forward to `84d79fa6`). Then create `docs/t20260330-scope-rule-governance-note` off main for the addendum commit.

**Driver:** User's framing: "`docs/ticket-dialogue-reply-extraction-mismatch` is the wrong publication boundary for a benchmark-governance note. This belongs to T-20260330, not the extraction bug ticket, and the repo's recent pattern has been one branch per concern." The extraction-bug ticket was already approved and tested (committed at `84d79fa6` with two-round review); holding it on a branch indefinitely added no value.

**Alternatives considered:**
- Stay on extraction-bug branch and add addendum there — rejected per user's one-branch-per-concern rule
- Create governance branch off the extraction-bug branch instead of main — rejected because it ties governance to extraction-bug merge order

**Trade-offs accepted:** Extraction-bug ticket is now on main; any revisions to that ticket require a new branch. Acceptable.

**Confidence:** High (E3). User directive, merge-branch skill completed cleanly.

**Reversibility:** High — can create new branch from main for any future work on either concern.

**Change trigger:** N/A — this is a historical decision.

### Decision 4: Hold B5 candidate classification on TWO independent axes

**Choice:** Preserve staging metadata `valid: true` as captured; treat as blocked for aggregate use on (a) scope-rule dispute per governance addendum AND (b) same-commit breach per operator-procedure.md:658.

**Driver:** User's finding [P1] (verified): "B5 candidate is not just 'pending the scope-governance addendum.' It also has an explicit run-condition breach in the benchmark packet itself. The candidate transcript records the run on branch `docs/t20260330-scope-rule-governance-note` at commit `4c0e2a46…`, while `manifest.json` still records `run_commit: 693551cc`. Under operator-procedure.md, 'wrong commit' is a run-condition breach, which is independently invalidating apart from the scope-rule dispute."

Confirmed at transcript:594-596. This commit drift was caused by this session's Phase 4 addendum commit, which landed between B5 baseline (pre-commit) and B5 candidate (post-commit).

**Alternatives considered:**
- Single-axis framing (scope-rule only) — rejected because the commit breach is an independent contract violation, observable independent of governance dispute
- Invalidate and rerun B5 candidate on different commit — rejected because commit reconciliation is itself a governance question owned by T-20260330; reruns without governance would be premature

**Trade-offs accepted:** B5 candidate is the only row with two independent invalidation axes. Signal is preserved but the row is maximally constrained in aggregate scoring.

**Confidence:** High (E3). Transcript evidence at :594-596, contract text at :66 and :658.

**Reversibility:** Medium — requires both (a) governance decision on scope rule AND (b) governance decision on commit reconciliation. Two separate decision points, both owned by T-20260330-04.

**Change trigger:** Governance addendum resolves BOTH the scope rule AND the commit-reconciliation question.

### Decision 5: Freeze repo state at `4c0e2a46` before B8; no further commits before B8 pair completes

**Choice:** Branch stays at `docs/t20260330-scope-rule-governance-note`, HEAD stays at `4c0e2a46`. Zero commits between this handoff and B8 baseline + candidate completion.

**Driver:** User's explicit direction: "keep the repo frozen at `docs/t20260330-scope-rule-governance-note` / `4c0e2a46`, make no further repo commits, then run B8 baseline and candidate from that same commit." The addendum commit already introduced commit drift between B5 baseline and B5 candidate; further commits before B8 would repeat the error.

**Alternatives considered:**
- Merge governance branch to main before B8 — rejected because merge is a commit event that advances HEAD; B8 baseline and candidate should run against the same commit
- Update T-20260416-01 inline with B5 reproduction evidence before B8 — rejected per Decision 6 (defer)
- Commit any tidying work (e.g., `_extract_transcript.py` bug fix) — rejected by freeze rule

**Trade-offs accepted:** Governance decision cannot be edited into the addendum before B8 runs. Any new findings between now and B8 completion go to this handoff or next session's handoff, not to the ticket.

**Confidence:** High (E3). User directive with specific freeze point.

**Reversibility:** Medium — after B8 completes, freeze lifts; addendum can be revised, T-20260416-01 updated, branches merged.

**Change trigger:** B8 pair completes and artifacts exported.

### Decision 6: Defer T-20260416-01 inline update until post-B8

**Choice:** Do NOT update the extraction-bug ticket now with B5 candidate reproduction evidence. Wait until B8 completes, then batch B5 + B8 observations (if B8 also reproduces) in a single inline update.

**Driver:** User's call: "Because B5 candidate already ran on `4c0e2a46`, I would defer the `T-20260416-01` inline update until after B8 completes. Another docs commit before B8 would introduce yet another benchmark commit boundary." Also ties to Decision 5 (freeze).

**Alternatives considered:**
- Update now on a new small branch — rejected because any commit breaks B8 same-commit invariant
- Commit after B8 baseline but before B8 candidate — rejected same reason (B8 baseline AND candidate must share commit)
- Never update the ticket inline — rejected because the ticket's own §B5/B8 reproduction expectations explicitly instruct logging additional occurrences

**Trade-offs accepted:** B5 reproduction evidence lives in this handoff + staging artifacts until the post-B8 update batches it. Audit trail preserved.

**Confidence:** High (E3). User directive, consistent with Decision 5 freeze.

**Reversibility:** High — deferred work is straightforward to execute post-B8.

**Change trigger:** B8 pair complete and artifacts exported.

## Changes

### Files modified

**`docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md`** (+32 lines)

Appended `## Execution Addendum (2026-04-16)` section with `### Open Governance Decision: Scope-enforcement scope` subsection. Structure per user-specified edits:
- Status line: "Open. Blocks aggregate scoring (AC-6) and the retirement decision (AC-7) until resolved explicitly in this ticket. Candidate runs may continue for evidence collection, but current baseline artifacts must not be used for aggregate scoring unless this ticket ratifies or replaces them."
- Controlling contract citations block (3 refs: :167-168, :182-183, :282-283)
- Retroactive impact table (B1, B3, B5 baselines with out-of-scope counts)
- Phrasing: "preserved as captured, but not yet ratified for aggregate use"
- Options A/B/C (strict reading / contract amendment / methodology revision)
- Decision owner: `T-20260330-04`, explicitly tied to AC-6 closure boundary

Commit: `4c0e2a46` on branch `docs/t20260330-scope-rule-governance-note`. Branch NOT merged to main (frozen per Decision 5).

### Git state changes

- `docs/ticket-dialogue-reply-extraction-mismatch` → merged to `main` via fast-forward (`fa75111b` → `84d79fa6`). Branch deleted.
- `docs/t20260330-scope-rule-governance-note` created off main at `84d79fa6`; advanced to `4c0e2a46` with addendum commit.

### Memory files (pending at save time)

Per Decision 5 freeze, memory writes happen during handoff save (not as separate repo commits). Two files:

- `feedback_contract_text_over_operational_interpretation.md` — recurring pattern across three sessions: contract-text authority > operational-convenience interpretation. Save as feedback memory.
- `feedback_no_midtrack_doc_commits.md` — rule discovered this session: during active benchmark track, avoid ANY repo commits (including docs) between rows. Rules about the benchmark are themselves benchmark-affecting commits. Save as feedback memory.

### Benchmark staging artifacts

**B5 baseline pair:**
- `/private/tmp/benchmark-v1-staging-20260415/B5-baseline-transcript.md` (211 KB, 3659 lines)
- `/private/tmp/benchmark-v1-staging-20260415/B5-baseline-synthesis.md` (13 KB, 129 lines)
- `/private/tmp/benchmark-v1-staging-20260415/B5-baseline-metadata.json` (404 B)

**B5 candidate pair:**
- `/private/tmp/benchmark-v1-staging-20260415/B5-candidate-transcript.md` (127 KB, 1499 lines)
- `/private/tmp/benchmark-v1-staging-20260415/B5-candidate-synthesis.md` (19 KB)
- `/private/tmp/benchmark-v1-staging-20260415/B5-candidate-metadata.json` (1.3 KB)

No in-session edits to staging files. Review-only.

### Working tree state

Branch: `docs/t20260330-scope-rule-governance-note`. HEAD: `4c0e2a46`. Working tree clean. Main: `84d79fa6` (extraction-bug ticket merged). Both branches unmerged to remote.

## Codebase Knowledge

### Benchmark contract text (authority document)

| Location | Content |
|---|---|
| `dialogue-supersession-benchmark.md:167-168` | "any out-of-scope scouting in the raw transcript makes the run invalid" — critical. Does NOT narrow to agent-side. |
| `dialogue-supersession-benchmark.md:182-183` | "the adjudicator reviews the raw transcript and invalidates any run that scouts beyond the recorded `allowed_roots`" |
| `dialogue-supersession-benchmark.md:282-283` | "Any scouting outside that scope invalidates the run and requires rerun from the same commit" |
| `dialogue-supersession-benchmark.md:159-165` | "Conceptual scored tasks must satisfy the corpus-design constraint: the row must be single-root by construction..." |
| `dialogue-supersession-benchmark.md:170-175` | "For scored runs, the primary evidence anchors define the benchmark-scoped `allowed_roots` for that row. Scored scouting beyond those anchors is out of scope for this contract." |
| `dialogue-supersession-benchmark.md:177-186` | B8 anchored decomposition exception |

**Critical takeaway:** the contract text is the authority; operator-procedure.md is the enforcement implementation. If they diverge, contract wins. Prior sessions (this one and the 12:17 session) treated operator-procedure.md:660-666 invalidation triggers as exhaustive when they are actually an implementation of the contract's broader "any out-of-scope scouting" rule.

### Operator procedure provisions referenced this session

| Provision | Line | Content |
|---|---|---|
| `run_commit` invariant | :66 | "All runs must use the same commit." |
| Invalidation triggers | :660-666 | Scope violation, evidence-budget overflow, run-condition breach, missing artifacts |
| Run-condition breach | :658 | Breach conditions (commit mismatch is one) |
| Evidence-budget overflow | :340-345 | Invalidating |
| Diagnostic metrics | :519 | `converged_within_budget` is counted, not gated |
| Rerun procedure | :669-676 | Mark `valid: false`, `invalid_reason`, `superseded_by` |

### B5 baseline transcript evidence of Codex-side out-of-scope scouting

Transcript: `/private/tmp/benchmark-v1-staging-20260415/B5-baseline-transcript.md`

| Line | Content | Status |
|---|---|---|
| :856 | `"cmd": "sed -n '1,220p' ... foundations.md"` | OUT |
| :1058 | `"cmd": "sed -n '220,340p' ... foundations.md"` | OUT (second read) |
| :1047 | `"cmd": "sed -n '1,260p' ... models.py"` | OUT |
| :1015-1021 | `rg -n` results in `recovery-and-journal.md` | OUT |
| :1073-1086 | `rg -n` results in `profiles.py` | OUT |

Synthesis's "Key Spec/Code Paths Referenced" section (:116-128) additionally lists `contracts.md`, `delivery.md`, `lineage_store.py`, `mcp_server.py`, `dialogue.py` as referenced — 9 files out-of-scope total, 3 in-scope.

### B5 candidate transcript evidence

Transcript: `/private/tmp/benchmark-v1-staging-20260415/B5-candidate-transcript.md`

**Commit drift evidence (P1 from user's second-pass review):**

| Line | Content |
|---|---|
| :594 | `"repo_root": "/Users/jp/Projects/active/claude-code-tool-dev"` |
| :595 | `"branch": "docs/t20260330-scope-rule-governance-note"` |
| :596 | `"head": "4c0e2a4617dda8b4243642f0c0e056fb0b756465"` |

**Codex-side scope breach evidence:**

| Line | Command | Status |
|---|---|---|
| :647 | `rg --files -g 'AGENTS.md'` | ⚠ Orientation or broad discovery (ambiguous) |
| :696 | `nl -ba packages/codex-collaboration/codex_collaboration/runtime.py` | OUT (wrong path) |
| :707 | `nl -ba packages/codex-collaboration/codex_collaboration/control_plane.py` | OUT (wrong path) |
| :718 | `nl -ba docs/advisory-runtime-policy.md` | OUT (wrong path) |
| :765 | `rg --files \| rg '(^\|/)runtime\.py$\|...'` | OUT (broad discovery) |
| :813 | `nl -ba packages/plugins/codex-collaboration/server/runtime.py` | IN |
| :824 | `nl -ba packages/plugins/codex-collaboration/server/control_plane.py` | IN |
| :835 | `nl -ba docs/superpowers/specs/codex-collaboration/advisory-runtime-policy.md` | IN |
| :1041 | `rg -n "<patterns>" <allowed files>` | IN |
| :1052, :1168, :1179 | control_plane.py range reads | IN |

Strict literal count: 5 out-of-scope attempts (3 wrong-path + 2 broad discoveries, treating AGENTS as broad discovery) or 6 (treating AGENTS as evidentiary). Defensible range depending on interpretation of orientation probes.

### T-20260330-04 ticket structure

Location: `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md`

Original structure (pre-addendum): Frontmatter, Context, Problem, Scope, Decision Rule, Acceptance Criteria (7 items), Verification, Dependencies, References.

Post-addendum (this session): original structure preserved, `## Execution Addendum (2026-04-16)` appended at end after References. Addendum structure: Open Governance Decision subsection with Status / Controlling contract citations / Retroactive impact / Options A/B/C / Decision owner.

Decision-owner pattern: inline ownership (this ticket resolves it) rather than spawning separate tickets. Same pattern as the commit-reconciliation question from prior session.

### Handoff system context

| File | Role |
|---|---|
| `packages/plugins/handoff/skills/load/SKILL.md` | Load procedure |
| `packages/plugins/handoff/skills/save/SKILL.md` | Save procedure |
| `packages/plugins/handoff/skills/save/synthesis-guide.md` | Mandatory synthesis reading |
| `packages/plugins/handoff/references/handoff-contract.md` | Frontmatter schema, chain protocol |
| `packages/plugins/handoff/references/format-reference.md` | Section checklist, filename format |
| `docs/handoffs/.session-state/` | Per-session state files for chain tracking |

State file for this session: `docs/handoffs/.session-state/handoff-f3cf5929-6d41-4dad-ae38-8b0e864d51c6` → points to archived predecessor at `docs/handoffs/archive/2026-04-16_19-27_t04-b3-pair-complete-extraction-bug-ticketed.md`.

## Context

### Current T-04 acceptance criteria status

| AC | Description | Status |
|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) |
| 3 | Gatherer agents exist | Done (PR #107) |
| 4 | Synthesis with bounded citations | Done |
| 5 | Benchmark contract executed on fixed corpus | **3 of 4 pairs executed (B1, B3, B5); 1 remaining (B8). All classifications provisional pending T-20260330-04 governance resolution.** |
| 6 | Benchmark result recorded with per-task metrics | Open; **BLOCKED by T-20260330-04 Execution Addendum governance decision** |
| 7 | Context-injection retirement decision | Open; **BLOCKED by AC-6** |

### Mental model for this session's findings

**The benchmark has a structural contract-vs-architecture incompatibility, surfaced only by careful transcript review.**

Framing: baseline architecture (`/cross-model:dialogue`) delegates to Codex, which has autonomous `exec_command` via the Codex App Server. The contract text at :167/:282 says "any out-of-scope scouting in the raw transcript" is invalidating — not narrowed to agent-side. Baseline's Codex-side autonomy means prompt-only scope control can fail under breadth-inviting topics (B1: 8+, B3: 4, B5: 3+ substantive out-of-scope reads).

Candidate architecture (`/codex-collaboration:dialogue`) uses agent-side gatherers for pre-dialogue evidence; Codex still has exec_command but the pre-dialogue briefing reduces its need to scout. Observed effect: B3 candidate had 2 agent scouts (in-scope); B5 candidate had 5 agent scouts (in-scope) + Codex-side probes that were mostly wrong-path and returned empty.

**The key insight:** both systems violate the strict contract reading, but in very different ways. Baseline violates with substantive evidence intake. Candidate violates with probes that return nothing. The governance decision (A/B/C) needs to consider whether "breach with evidence intake" and "breach without evidence intake" should be treated equally.

### Extraction-bug status (T-20260416-01)

Reproduced in B5 candidate. Two data points now:
- B3 candidate (adversarial): errored T3, substantive dialogue incomplete
- B5 candidate (evaluative): errored T5, substantive dialogue complete — only closing yes/no verdict lost

Pattern hypothesis (NOT confirmed as mechanism): bug scales with turn count because longer dialogues increase probability of an items-array-shape response. Not yet mechanism-verified for B5 — only signature-verified.

B8 prediction per ticket §B5/B8: HIGHEST reproduction probability (8 turns, complex anchored decomposition, longest dialogue). If B8 errors, three data points in three candidate runs — high-confidence pattern.

### Environment snapshot

- Branch: `docs/t20260330-scope-rule-governance-note` (not merged to main; frozen per Decision 5)
- HEAD: `4c0e2a46` (this session's addendum commit)
- Working tree: clean
- Main: `84d79fa6` (extraction-bug ticket merged this session)
- Staging: intact at `/private/tmp/benchmark-v1-staging-20260415/` with 18 files (B1+B3+B5 all complete)
- `~/.claude/plugins/data/codex-collaboration-inline/session_id` should contain `f3cf5929-6d41-4dad-ae38-8b0e864d51c6` (this loader session; baseline's fresh session didn't fire the SessionStart hook that would have written a new ID)

### Open tickets

| Ticket | Status | Next |
|---|---|---|
| T-20260330-04 (parent benchmark + NEW scope-rule governance) | Open; AC-5 at 3/4 pairs; AC-6/AC-7 blocked | Run B8 pair; then resolve governance addendum |
| T-20260416-01 (dialogue.reply extraction mismatch) | Open; post-benchmark. Two reproductions to batch-log after B8 | Pick up after benchmark track completes |
| T-05 Execution-domain foundation | Open (unstarted) | Separate workstream |
| T-06 Promotion flow & delegate UX | Open (blocked by T-05) | — |
| T-07 Analytics reviewer & cutover | Open | Separate workstream |

## Learnings

### Contract text > operational interpretation (recurring pattern, third occurrence)

**Mechanism.** When a benchmark or contract document has both an authority layer (the contract itself) and an implementation layer (operator procedure, enforcement rules), the authority layer governs disputes. Over-relying on the implementation layer leads to interpretive leniency that the authority layer doesn't support.

**Evidence.**
- 11:48 session: "evidence_count=4 ≤ 5" passed on loose reading; contract text defined the unit differently. Corrected at `fa75111b`.
- 12:17 session: "mid-track patch + rerun" proposed on run-invalidation intuition; operator-procedure.md:66 said all runs must use same commit. Corrected to post-benchmark fix.
- This session (Phase 3): "Codex-side out-of-scope reads are edge-case observation" passed on operator-procedure.md:660-666 reading; contract text at :167 says "any out-of-scope scouting in the raw transcript" — no agent-vs-Codex distinction. Corrected mid-session.

**Implication.** Before a review verdict, re-check the contract text (authority layer) against the implementation text (enforcement layer). If they diverge or the implementation is a subset of the authority, the authority wins. This is captured as `feedback_contract_text_over_operational_interpretation.md` memory.

**Watch for.** Any review reasoning that cites only operator-procedure.md without also citing the benchmark contract. Any language like "under the operator procedure" without a parallel "under the benchmark contract" check.

### Rules about the benchmark are themselves benchmark-affecting commits

**Mechanism.** During an active benchmark track, any repo commit (even a doc-only commit about the benchmark itself) advances HEAD and creates a commit boundary. Under operator-procedure.md:66, runs must share a commit. Committing the scope-rule governance addendum mid-track created a new boundary between B5 baseline and B5 candidate — exactly the failure mode the addendum itself describes.

**Evidence.** Phase 4 this session: committed `4c0e2a46` addendum. Phase 5 user ran B5 candidate. Phase 6 user flagged that B5 candidate transcript records commit `4c0e2a46` while manifest records `693551cc`. Run-condition breach, caused by MY commit.

**Implication.** For any mid-benchmark decision document, either (a) defer the commit until a safe window (between pair runs has wider freedom; during a pair run is higher risk), or (b) log the decision in session chat/handoff and defer the commit to post-benchmark. This is captured as `feedback_no_midtrack_doc_commits.md` memory.

**Watch for.** Self-justifications like "this is just a doc commit, can't affect the benchmark." The commit itself is the mechanism; the content doesn't matter. Also watch for: writing about a rule while breaking it.

### "Same signature" vs "same mechanism" — verification discipline

**Mechanism.** Observing that two failures share a signature (same error text, same termination point, same empty-response) does NOT establish that they share a mechanism (same root-cause code path). Signature evidence comes from metadata + synthesis; mechanism evidence requires raw-turn shape inspection. Claiming mechanism without that inspection overstates.

**Evidence.** User's P2 this session: I said B5 extraction-bug reproduction was "same mechanism" as B3. B3's root cause was proved via code inspection of `dialogue.py` + transcript showing the items-array response shape. For B5, I observed the same signature but didn't re-prove the items-array shape from the rollout JSONL. User correctly called this out.

**Implication.** Distinguish evidence tiers in language: "same signature" (signature-verified), "mechanism likely same" (signature + prior-mechanism + pattern), "same mechanism" (signature + mechanism-verified). Do not conflate.

**Watch for.** My own language patterns that jump from signature to mechanism without explicit verification step. If I'm about to write "same X", ask: what evidence do I have vs. what am I inferring?

### Scope-breach counting has interpretive ambiguity

**Mechanism.** Not all non-file-read probes are equivalent. `rg --files -g 'PATTERN'` searches the whole repo's filename index — broad discovery. `pwd` reads current directory — orientation. `printf` isn't a read. Each has different scope-breach weight under strict contract reading.

**Evidence.** User's P3 this session: my initial count was "4 wrong-path + 1 broad discovery = 5 out-of-scope attempts." User counted TWO broad discoveries (`rg --files -g 'AGENTS.md'` at :647 AND `rg --files | rg '...'` at :765). Strict literal count is 6 if AGENTS is evidentiary; 5 if AGENTS is orientation.

**Implication.** In scope reviews, report strict literal count AND defensible interpretive count, naming which probes fall in each bucket. The governance decision (Option A/B/C) may turn on this distinction.

**Watch for.** Single counts without showing interpretive reasoning. "5 out-of-scope probes" is ambiguous; "5-or-6 depending on whether AGENTS broad discovery is treated as orientation" is actionable.

### User's second-pass reviews are usually sharper than first pass

**Mechanism.** User's initial review often addresses the surface framing (big-picture correctness). Second pass addresses detail, counting, evidence density. Treating first-pass approval as final approval under-uses the review signal.

**Evidence.** This session had two second-pass cycles:
- Phase 3: first pass treated B5 baseline as valid; second pass flagged the contract-text problem on agent-vs-Codex distinction
- Phase 6: first pass accepted the B5 candidate review; second pass flagged the three P1/P2/P3 findings including the same-commit breach I had caused

**Implication.** After any first-pass approval, explicitly expect and invite second-pass findings. The prior 12:17 and 19:27 sessions had the same pattern (P1/P2 two-pass review on ticket drafts). Structural.

**Watch for.** Rushing to commit after first-pass approval. Slow down and read the work critically one more time before declaring done.

## Next Steps

### 1. B8 baseline prep and run (critical path, next session opener)

**Dependencies:** None in this handoff. B5 pair complete and captured. Freeze rule applies: no more commits until B8 pair completes.

**What to do in next session's opening turn:**

1. Pre-flight: verify `git status` is clean, `git log --oneline -3` shows `4c0e2a46` as HEAD on `docs/t20260330-scope-rule-governance-note`. If any commits landed, investigate before running B8.
2. Pre-flight: verify staging intact: `ls /private/tmp/benchmark-v1-staging-20260415/` should show 18 files (B1/B3/B5 pairs × 3 files each).
3. Paste B8 baseline invocation from `/private/tmp/benchmark-v1-staging-20260415/invocations.md:154-176` with `{run_type}` → `This is a scored benchmark run.`
4. Fresh session required per operator-procedure.md:174.

**Pre-built B8 baseline invocation (from invocations.md:154-176):**

```
/cross-model:dialogue "BENCHMARK SCOPE CONSTRAINT: This is a scored benchmark run. Limit all evidence gathering (Glob, Grep, Read) to the following path groups only. Each scouting step must target a path within one of these groups. Cross-group reasoning is expected; cross-group target expansion is not.

Group 1 — Baseline evidence path:
- packages/plugins/cross-model/skills/dialogue/SKILL.md
- packages/plugins/cross-model/agents/
- packages/plugins/cross-model/context-injection/

Group 2 — Candidate normative surface:
- docs/superpowers/specs/codex-collaboration/

Group 3 — Candidate runtime surface:
- packages/plugins/codex-collaboration/server/

EVIDENCE BUDGET: Complete at most 5 evidence records.
POSTURE: comparative

---

Can Claude-side scouting replace cross-model context-injection for dialogue in this repo, or what concrete quality loss would remain?" -p comparative -n 8
```

**Special B8 considerations:**

- Anchored decomposition rule: each scout within one group; cross-group reasoning expected, cross-group target expansion is not
- Highest extraction-bug reproduction probability per T-20260416-01 §B5/B8
- 8-turn budget (longest); `max_evidence: 5` for baseline, `15` for candidate
- Phase 3 transcript review must verify no cross-group target expansion

**What to read first (in resume session before fresh session):**
- This handoff's §Codebase Knowledge → scope-breach evidence tables for B5 (informs B8 review)
- This handoff's §Learnings → contract text vs operational interpretation (apply to B8 review)
- `invocations.md:154-176` — B8 baseline + candidate

### 2. B8 candidate prep and run (after B8 baseline valid)

**Dependencies:** B8 baseline complete, freeze still in effect.

**What to do:** Paste B8 candidate invocation from `invocations.md:180-200`. Fresh session. Same 8-turn budget, `max_evidence: 15`.

**Specific watch:** HIGHEST-INTEREST run after B3 candidate + B5 candidate reproductions. Three outcomes:
- (a) Candidate converges normally (extraction bug doesn't reproduce) — B5 evaluative + B3 adversarial reproduction establishes a partial pattern; B8 non-reproduction suggests turn-budget-correlated, not inevitable
- (b) Candidate errors on extraction bug — third reproduction; high-confidence pattern (scales with turn count), log inline in T-20260416-01 POST-benchmark per Decision 6
- (c) Candidate errors on something new — new fragility data point, preserve per pathology-preservation rule, document separately

### 3. T-20260416-01 post-benchmark batch update

**Dependencies:** B8 pair complete.

**What to do:** Single commit (on a new branch after freeze lifts) appending `## Observed reproductions` section to T-20260416-01 with B3 + B5 (+ potential B8) evidence table. Do NOT commit during B8 pair run.

**Proposed table structure:**

| Run | Turn | Posture | Turn budget | Impact | Notes |
|---|---|---|---|---|---|
| B3 candidate | T3 | adversarial | 6 | Substantive dialogue incomplete | ~4000-char reply via shape 2 |
| B5 candidate | T5 | evaluative | 6 | Closing verdict lost; substantive synthesis preserved (delivered at T3) | Signature verified; mechanism inferred not re-proved |
| B8 candidate | TBD | comparative | 8 | TBD | TBD |

### 4. Governance resolution in T-20260330-04 Execution Addendum

**Dependencies:** B8 pair complete (for maximum decision evidence).

**What to do:** Render explicit decision between options A / B / C in the Execution Addendum. The decision owns whether aggregate scoring (AC-6) can proceed on captured artifacts or requires rerun(s) on a new commit.

**Decision evidence now available:**
- B1 baseline: 8+ out-of-scope Codex reads, substantive intake
- B3 baseline: 4 out-of-scope Codex reads, substantive intake
- B5 baseline: 3+ substantive out-of-scope Codex reads (foundations.md 2x, models.py, recovery-and-journal.md)
- B3 candidate: ~2 agent scouts in-scope, minimal Codex-side probe activity
- B5 candidate: 5 agent scouts in-scope, 5-6 Codex-side probes (4 wrong-path, 1-2 broad discoveries) — NO substantive out-of-scope intake
- B8 TBD

The asymmetry in out-of-scope BREACH (both systems) vs out-of-scope INTAKE (baseline only) is the key distinguishing data for Options A/B/C.

### 5. Commit-reconciliation resolution (carried forward)

**Dependencies:** Governance decision from Next Step #4.

**Context from prior session's Decision 5 + this session's new drift:**
- Manifest: `run_commit: 693551cc`
- B1 baseline ran on: `693551cc` era
- B1 candidate + B3 pair ran on: `fa75111b` (2 doc-only commits ahead)
- B5 baseline ran on: `fa75111b` (same as B3)
- B5 candidate ran on: `4c0e2a46` (my mid-track governance commit — 1 doc-only commit ahead of B5 baseline)
- B8 will run on: `4c0e2a46` (per freeze rule)

Four commit states across 8 runs (if B8 holds the freeze). Reconciliation options:
- Update manifest to reflect whatever is chosen as canonical
- Rerun subset of runs to align commits
- Document as procedural doc-only-drift exception (with caveats for the addendum commit which changed more than docs)

### 6. AC-7 retirement decision (final)

**Dependencies:** AC-6 aggregate scoring complete (which depends on governance + commit reconciliation).

**What to do:** Render retirement decision per T-04 AC-7. Current directional signal after 3 pairs:
- B1: positive for supersession (candidate dominates scope + scouting + structure)
- B3: mixed (candidate wins scope + scouting; baseline wins convergence due to fragility)
- B5: MORE mixed (candidate agent-side scope clean; candidate Codex-side has probes but no intake; baseline structurally richest output yet; candidate errors on extraction bug)

If B8 confirms candidate's agent-side scope-discipline advantage across all 4 postures + confirms no novel fragilities, supersession decision is defensible with documented caveats (extraction bug, commit reconciliation).

### 7. T-20260416-01 fix (post-benchmark)

**Dependencies:** Benchmark track complete + adjudicated + retired.

**What to do:** Implement Option A per ticket §Proposed fix. ~15-25 production lines + ~30-50 test lines. Specifically:
1. Move `_read_turn_agent_message` from `dialogue.py:973-990` to shared helper (`codex_compat.py` or new `turn_extraction.py`)
2. Call it from `runtime.py:173-177` when populating `agent_message`
3. Preserve commit-before-parse invariant
4. Add 5 tests per ticket's implementation-tests list
5. Update T-20260416-01 with final commit SHA, mark `status: closed`

## In Progress

**Clean stopping point — B5 pair captured, scope-governance addendum landed, repo frozen for B8.**

- **Approach:** Run + review + triage + governance intervention. Same pattern as B3 pair, with an added mid-session scope-rule governance addendum.
- **State:** B5 baseline preserved as captured (not ratified). B5 candidate preserved as captured (blocked on two axes: scope-rule + same-commit). Governance addendum committed at `4c0e2a46`. Branch `docs/t20260330-scope-rule-governance-note` frozen — no more commits until B8 completes.
- **Working:** Pathology-preservation rule held. Contract-first reasoning surfaced governance question. Two-pass review caught my Phase 4 governance lapse. Addendum landed cleanly.
- **Not working:** I committed mid-track, creating commit drift for B5 candidate. This is a process failure, not a code failure. Memory saved to prevent recurrence.
- **Next action:** Next session opens with freeze-state verification (`git log --oneline -3` shows `4c0e2a46` as HEAD), then surfaces B8 baseline invocation to operator for fresh-session run.

## Open Questions

### 1. Will B8 candidate reproduce the extraction bug?

**Context:** T-20260416-01 §B5/B8 predicts B8 has HIGHEST reproduction probability (8-turn budget, complex anchored decomposition). B3 reproduced at T3; B5 reproduced at T5. Both are data points toward "bug scales with turn count" but neither was mechanism-verified for B5.

**Impact:** HIGH for the extraction-bug prioritization AND for T-04 AC-7 retirement framing. Three reproductions in three runs → high-confidence systematic pattern. Two reproductions + one non-reproduction → turn-budget-correlated but not inevitable.

**Decision pending until:** B8 candidate runs.

### 2. Which governance option (A/B/C) will be selected?

**Context:** Per the Execution Addendum:
- A. Strict reading (all baseline runs invalid, rerun with stricter enforcement)
- B. Contract amendment (narrow scope-invalidation to agent-side scouting)
- C. Methodology revision (scope discipline as separate dimension)

Current directional data: baseline has substantive out-of-scope intake; candidate has probes without intake. Option B would ratify current artifacts; Option A invalidates them; Option C restructures scoring.

**Impact:** HIGH. Determines whether 3+ captured baseline runs become valid scored evidence or require rerun.

**Decision pending until:** After B8 (for maximum evidence) + governance discussion with user.

### 3. How does commit reconciliation resolve under 4 commit states across 8 runs?

**Context:** B1 baseline: `693551cc`. B1 candidate + B3 pair + B5 baseline: `fa75111b`. B5 candidate + B8 pair: `4c0e2a46`. Manifest: `693751cc`. Four distinct commits.

**Impact:** Moderate. Strict :66 reading says all runs must use same commit; four distinct commits means most runs are non-compliant. User's framing says this is governance (not invalidation). Resolution determines which runs contribute to aggregate.

**Decision pending until:** Governance decision from Open Question #2 (scope-rule decision may force or relax commit-reconciliation).

### 4. Does the `session_id` field semantic gap matter for Phase 3?

**Context:** Baseline runs (B1, B3, B5) all recorded `session_id` = loader session ID, not fresh-session ID. Candidate runs record fresh-session IDs correctly because `/codex-collaboration:dialogue` fires SessionStart hook. Thread_id is always separate.

**Impact:** Low for scoring; Phase 3 adjudicators should use `thread_id` for baseline cross-run audit, not `session_id`.

**Decision pending until:** Phase 3 starts.

### 5. Should `scope_envelope` be wired through the candidate skill? (Carried forward from 12:17 and 19:27)

**Context:** Gatherer agents support `scope_envelope` but candidate skill doesn't pass it. v1-compliant (prompt-only) but known fragility. B3 + B5 data shows candidate agent-side scope discipline holds without it, but Codex-side breaches are present (B5 candidate: 5-6 probes).

**Impact:** Low for v1. Could become higher if B8 shows Codex-side breaches worsen.

**Decision pending until:** Post-benchmark.

### 6. Does the "positive for supersession" directional signal hold across all 4 postures?

**Context:** B1 (evaluative): strong positive. B3 (adversarial): mixed. B5 (evaluative-policy): more mixed. B8 (comparative): pending.

**Impact:** HIGH — THE retirement question.

**Decision pending until:** All 4 pairs complete and adjudicated.

## Risks

### 1. B8 same-commit freeze may not survive accidental commits

**Impact:** If ANY commit lands between this handoff and B8 pair completion, B8 baseline and B8 candidate will run on different commits — same failure mode as B5 candidate this session. Aggregate scoring would then have FIVE commit states (current 4 + another).

**Mitigation:**
- Decision 5 explicitly forbids commits during B8 pair
- Memory `feedback_no_midtrack_doc_commits.md` saves the rule for next session
- Next-session pre-flight explicitly verifies `git log --oneline -3` shows `4c0e2a46` as HEAD
- Any proposed commits during B8 should be deferred to the next-next session's "post-benchmark batch" workflow

### 2. Mid-session governance decisions may compound

**Impact:** If B8 surfaces ANOTHER governance question (e.g., anchored-decomposition rule interpretation), the temptation to address it mid-benchmark would repeat this session's mid-track commit error.

**Mitigation:** For any new governance question during B8: LOG to handoff, do NOT commit. Add to Execution Addendum in a post-benchmark commit batch alongside other governance updates.

### 3. Extraction bug may strand B8 data before any substantive synthesis

**Impact:** B3 reproduction errored at T3 (substantive dialogue incomplete). If B8 errors similarly early in its 8-turn budget, B8 candidate data could be minimal. However, per §Pathology preservation: that's still valid benchmark signal.

**Mitigation:** Per pathology-preservation rule, whatever B8 produces is preserved. Even early-termination B8 candidate still validates the pattern and feeds governance decision.

### 4. Confirmation-bias risk on B8

**Impact:** Three runs' worth of mixed data now — hardest to interpret so far. High risk of unconsciously weighting B8 toward a retirement conclusion. Especially acute: B8 is the ONLY comparative-posture row and structurally most-expected-to-favor candidate (comparative posture is the candidate's strongest suit per B1 directional signal).

**Mitigation:** Next session opening should re-read this handoff's §Learnings + §Risks, plus the 19:27 handoff's §Risks #1. Apply pathology-preservation + contract-first-reasoning discipline uniformly regardless of data direction.

### 5. Branch sprawl (carried forward)

**Impact:** After this session, two unmerged branches exist in local tree:
- `docs/t20260330-scope-rule-governance-note` (this session's addendum, frozen per Decision 5)

Extraction-bug branch was merged to main this session. Governance branch will stay unmerged until post-B8.

**Mitigation:** Merge after B8 pair completes, alongside any T-20260416-01 updates. Single merge window simplifies tracking.

### 6. `/tmp/` staging reboot vulnerability (carried forward)

**Impact:** Machine reboot clears `/private/tmp/`, losing all 18 staging files. Phase 5 import relies on staging intactness.

**Mitigation:** Before extended breaks, `cp -r /private/tmp/benchmark-v1-staging-20260415 ~/benchmark-v1-staging-backup`. Worth doing NOW that 6 runs are staged.

### 7. Manual adjudication dominant cost (carried forward)

**Impact:** 4 rows × 2 systems = 8 syntheses. B5 baseline has 27 claims alone; B5 candidate 5. Claim-count asymmetry means adjudication effort is row-dependent.

**Mitigation:** Row-by-row, high-signal rows first. B3 + B5 candidate non-convergence changes scope per row.

### 8. `run_commit` drift now at four commit states

**Impact:** Compounded by my mid-track governance commit. If governance resolution requires commit alignment, multiple reruns may be needed.

**Mitigation:** Governance decision explicitly routes this to T-20260330-04. Options A (rerun all) / B (ratify via amendment) / C (methodology revision) each have different commit-reconciliation implications.

## References

### Commits this session

- `84d79fa6` merged `docs/ticket-dialogue-reply-extraction-mismatch` → main (fast-forward; ticket from 19:27 session)
- `4c0e2a46` on `docs/t20260330-scope-rule-governance-note`: `docs(t20260330): add scope-rule governance addendum blocking AC-6/AC-7` — this session's addendum commit (**mid-track commit error; freeze in effect**)

### Authority documents

| Document | Location | Role |
|---|---|---|
| Benchmark contract v1 (authority) | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Corpus structure, scope rules (:167/:282), prompt-only enforcement |
| Operator procedure (enforcement) | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | Execution procedure, `run_commit` (:66), invalidation triggers (:660-666), diagnostic metrics (:519), rerun procedure (:669-676) |
| Manifest | `docs/benchmarks/dialogue-supersession/v1/manifest.json` | `run_commit: 693751cc` (drift-pending), 4-row corpus structure |
| T-20260330-04 (parent + governance addendum) | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | T-04 AC authority + this session's Execution Addendum |
| T-20260416-01 (extraction-bug ticket) | `docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md` | Post-benchmark fix; two reproductions to batch-log |

### Staging artifacts (B1+B3+B5 complete, B8 pending)

| Artifact | Path | Status |
|---|---|---|
| Invocations packet | `/private/tmp/benchmark-v1-staging-20260415/invocations.md` | Unchanged; B8 at :154-200 |
| Transcript extractor | `/private/tmp/benchmark-v1-staging-20260415/_extract_transcript.py` | Has `"# B1 Candidate"` hardcoded on :54 — post-benchmark tidy |
| B5 baseline artifacts | `B5-baseline-{transcript,synthesis,metadata}` | Complete, preserved as captured pending governance |
| B5 candidate artifacts | `B5-candidate-{transcript,synthesis,metadata}` | Complete, blocked for aggregate on two axes pending governance |

### Codex session rollouts

- B5 baseline: thread `019d9811-b052-7163-b5e2-e91b9db26ffb`
- B5 candidate: `/Users/jp/.codex/sessions/2026/04/16/rollout-2026-04-16T17-44-26-019d9840-a2b4-72f1-b54d-2eca297b5478.jsonl` (thread `019d9840-a2b4-72f1-b54d-2eca297b5478`, run `24d0dabb-2a54-468f-83e0-8309d1e6e361`)

### Code files explored

| File | Lines read | Key findings |
|---|---|---|
| `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | 150-186, 270-300 | Contract text :167/:182-183/:282-283; scope compliance review section |
| `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | 1-113 | Ticket structure for addendum append location |
| B5 baseline synthesis (staging) | 1-129 | Claim structure, pipeline data, scope references |
| B5 baseline transcript (staging) | 1-80 + various | Codex exec_command patterns, out-of-scope reads |
| B5 candidate metadata (staging) | 1-24 | Error termination, evidence_count=5, session details |
| B5 candidate synthesis (staging) | 1-107 | Final claims, severity taxonomy, extraction-bug signature |
| B5 candidate transcript (staging) | 594-604 (commit evidence) + grep | Codex tool calls, commit drift evidence |

### Memory files

- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_benchmark_pathology_preservation.md` (from 19:27 session, still active)
- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_contract_text_over_operational_interpretation.md` (pending save this session)
- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_no_midtrack_doc_commits.md` (pending save this session)
- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/MEMORY.md` (update with new feedback pointers)

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-16_19-27_t04-b3-pair-complete-extraction-bug-ticketed.md`
- Prior (same-day chain): `docs/handoffs/archive/2026-04-16_12-17_t04-b1-pair-complete-b3-adversarial-next.md`, `docs/handoffs/archive/2026-04-16_11-48_t04-b1-baseline-valid-after-evidence-count-reconciliation.md`
- Earlier arc: multiple 2026-04 handoffs on T-04 scaffold / runtime gate / Phase 1 prep

## Gotchas

### Commit drift tracking now has four states

**Symptom:** Four distinct commits across 8 (expected) benchmark runs:

| Commit | Runs |
|---|---|
| `693751cc` (manifest-recorded) | B1 baseline only |
| `fa75111b` | B1 candidate, B3 pair, B5 baseline |
| `4c0e2a46` | B5 candidate, B8 pair (planned) |

**Root cause:** Three separate doc-only commits landed over the benchmark's execution window: `f0fde082` (before B1 candidate), `fa75111b` (before B3 pair), `4c0e2a46` (this session's governance addendum; I caused this one).

**Prevention:** No more commits before B8 pair completes (Decision 5 freeze). Post-benchmark: governance resolution (Next Step 4) determines how to reconcile.

### My governance addendum commit created the very drift it describes

**Symptom:** `4c0e2a46` — the scope-rule governance addendum commit — cites `:66` same-commit rule as load-bearing, then immediately violates it by landing between B5 baseline and B5 candidate.

**Root cause:** I viewed the addendum as "just docs about the benchmark" rather than "a commit on the repo during an active benchmark track." Content matters less than commit-timing matters.

**Prevention:** `feedback_no_midtrack_doc_commits.md` memory saves the rule. Next session's pre-flight verifies `4c0e2a46` is HEAD and no unplanned commits landed.

### B5 baseline `session_id` reflects loader session, not fresh session

**Symptom:** B5 baseline metadata: `session_id: f3cf5929-6d41-4dad-ae38-8b0e864d51c6` = this loader session's ID, not a fresh-session ID. Same pattern as B1 baseline and B3 baseline.

**Root cause:** `/cross-model:dialogue` skill does NOT fire codex-collaboration's SessionStart hook that writes `~/.claude/plugins/data/codex-collaboration-inline/session_id`. When the fresh baseline session reads that file, it returns whatever was last written — the loader session's ID.

**Prevention:** For baseline runs, use `thread_id` (captured in synthesis + transcript) as canonical identifier. Phase 3 adjudication notes this semantic gap.

### Candidate `session_id` is correct fresh-session ID

**Symptom:** B5 candidate metadata: `session_id: 3cd5b5af-1c80-407b-bf03-5705a38a5487` — new, distinct from loader session. `session_id_canonical: true` holds.

**Root cause:** `/codex-collaboration:dialogue` DOES fire the SessionStart hook. Candidate fresh session writes its own ID to the session_id file, so reads reflect the current session correctly.

**Prevention:** Trust candidate's `session_id`. Baseline's needs cross-reference to `thread_id`.

### Transcript header bug carries over to every extracted transcript

**Symptom:** All candidate transcripts (B1, B3, B5, and future B8) say `# B1 Candidate — Raw Codex Dialogue Exchange` at line 1 regardless of which run.

**Root cause:** `_extract_transcript.py:54` has `lines.append("# B1 Candidate — Raw Codex Dialogue Exchange")` hardcoded. File at `/private/tmp/benchmark-v1-staging-20260415/_extract_transcript.py` (staging, not repo).

**Prevention:** Post-benchmark tidy item. Parameterize the helper to accept a `--title` argument or derive from filename.

### Codex-side probe breaches are distinct from Codex-side substantive reads

**Symptom:** B5 baseline has SUBSTANTIVE out-of-scope reads (`sed -n` on foundations.md, models.py, recovery-and-journal.md — files with content Codex harvested). B5 candidate has PROBE breaches (wrong-path reads that returned empty + broad discovery probes).

**Root cause:** Baseline's Codex has extensive out-of-scope topic awareness and actively scouts beyond allowed_roots. Candidate's Codex has been primed with pre-dialogue gatherer briefing (21 citations across 3 files), reducing its need to scout substantively — but it still probes for orientation, some of which land out-of-scope.

**Prevention:** Governance Option B (contract amendment) could distinguish "breach with intake" from "breach without intake" — they carry different scope-discipline meaning. If governance treats them identically, candidate's "probe but no intake" pattern is still a breach.

### Run-condition breach is independently invalidating

**Symptom:** User's P1 this session: "Under operator-procedure.md, 'wrong commit' is a run-condition breach, which is independently invalidating apart from the scope-rule dispute."

**Root cause:** Operator-procedure.md:658 lists run-condition breach as one of the four invalidation triggers. Commit mismatch between manifest and transcript is a run-condition breach. This invalidates regardless of scope-rule status.

**Prevention:** Metadata should include `run_commit` field explicitly (currently absent). Transcript records commit in `relevant_repository_context.repository_identity`. Cross-check both against manifest.

### Second-pass reviews consistently catch what first-pass misses

**Symptom:** Both Phase 3 (scope-rule finding) and Phase 6 (commit-breach + same-mechanism + count findings) came as second-pass reviews after apparent first-pass approval.

**Root cause:** First-pass review addresses framing; second-pass addresses evidence density, counting accuracy, and overstatement.

**Prevention:** After first-pass approval, explicitly invite second-pass review. The 12:17 and 19:27 sessions show the same pattern on ticket drafts.

## Conversation Highlights

### User's contract-text pushback (session-defining)

User: "The `valid: true` verdict is not contract-safe under the current v1 benchmark text. The benchmark contract says 'any out-of-scope scouting in the raw transcript makes the run invalid' and that transcript review is the enforcement mechanism, not the pipeline's self-reported scope counter (dialogue-supersession-benchmark.md:167, dialogue-supersession-benchmark.md:282). The B5 raw transcript shows out-of-scope reads beyond the row's recorded `allowed_roots`, including `foundations.md`, a broad `rg` over the whole spec tree, and `models.py`. Your 'agent-side only' interpretation matches the pipeline metadata, but it conflicts with the benchmark authority as written."

Verified both contract citations. Recognized that operator-procedure.md:660-666 is an implementation of the contract's broader scope rule, not an exhaustive replacement. Conceded and revised classification.

### User's addendum structural edits

User: "I would **not** place it directly under `## Open Governance Decisions` after `## References` with no framing. I would add: `## Execution Addendum (2026-04-16)` then your governance subsection(s). This preserves the ticket's original planned shape while making the blocker visible as a later discovered benchmark-governance issue."

Used directly. The `Execution Addendum` framing makes it clear this is mid-execution governance, not original ticket content.

### User's same-commit breach finding (Phase 6)

User: "[P1] B5 candidate is not just 'pending the scope-governance addendum.' It also has an explicit run-condition breach in the benchmark packet itself. The candidate transcript records the run on branch `docs/t20260330-scope-rule-governance-note` at commit `4c0e2a46…` (B5-candidate-transcript.md:594), while `manifest.json` still records `run_commit: 693751cc`. Under operator-procedure.md, 'wrong commit' is a run-condition breach, which is independently invalidating apart from the scope-rule dispute."

Verified at transcript:594-596. The commit drift was caused by Phase 4's governance addendum commit. Conceded the governance lapse fully and saved memory.

### User's verification-discipline correction

User: "[P2] 'Same mechanism' is stronger than what I can verify from the B5 artifacts I reviewed. The metadata and synthesis prove the same failure signature: turn-5 `codex.dialogue.reply` parse failure with empty response, after the substantive position had already been delivered. What I did not re-prove from the B5 artifacts is the specific B3 root cause of an items-array response shape. So I would phrase this as 'same failure signature, mechanism likely same' unless you want to attach direct raw-turn evidence."

Correct. Updated language to distinguish signature from mechanism.

### User's count-discipline correction

User: "[P3] The strict out-of-scope count is understated. The raw transcript shows two broad repo-discovery commands, not one: `rg --files -g 'AGENTS.md'` and `rg --files | rg ...`, plus the three wrong-path `nl` reads. If you exclude the AGENTS lookup as non-evidentiary orientation, your '5 probes' count is defensible; under the literal contract, it is at least 6 out-of-scope probes."

Verified. Updated to report strict (6) and interpreted (5) counts with the distinction named.

### User's freeze directive

User: "On session posture, I would stop here and hand off before B8. You are already at high context, and B8 is the longest, highest-risk row. The clean resume boundary is: keep the repo frozen at `docs/t20260330-scope-rule-governance-note` / `4c0e2a46`, make no further repo commits, then run B8 baseline and candidate from that same commit."

Accepted. Applied as Decision 5. Preserved in §Next Steps and §Risks.

## User Preferences

### Contract text is the authority; operational documents are subordinate

When a question arises about what a rule allows, read the contract text FIRST before reasoning from operational interpretations. User's direct quote: "the benchmark contract says '...'" is the template — lead with contract citation, not with enforcement-document reasoning.

### Code-review-format findings with confidence scores

User consistently uses code-comment review format with explicit confidence (0.94-0.98 this session). Response pattern: treat every finding as a verified claim to be addressed. Verify the finding against current artifacts. Rewrite the affected analysis honestly with a structured response.

### "Same X" language must be verification-gated

Distinguish signature (observed data) from mechanism (verified cause). Do NOT claim mechanism without direct evidence. User's quote: "So I would phrase this as 'same failure signature, mechanism likely same' unless you want to attach direct raw-turn evidence."

### Count interpretations should be named, not hidden

When a count has interpretive ambiguity (e.g., 5 vs 6 depending on what counts as evidentiary), report both counts and the interpretive distinction. Single "5" or "6" hides judgment that should be explicit.

### One branch per concern

User's quote: "the repo's recent pattern has been one branch per concern." Don't co-mingle unrelated work on one branch even if it saves commits. For this session: extraction-bug ticket merged to main first, governance-note on its own separate branch.

### Do not mutate staging artifacts post-capture

User's quote: "I would **not** rewrite the raw B5 staging metadata to `valid: null` unless the procedure explicitly defines post-hoc mutation for governance disputes. The safer move is to preserve the captured artifact as-is and add a governance note." Audit trail integrity > cleanup convenience.

### Hold unresolved verdicts rather than force resolution

Rather than marking B5 baseline as "valid" or "invalid," user prefers "preserved as captured, not yet ratified for aggregate" — an explicit third classification that names the provisional status. Same pattern for B5 candidate (blocked on two axes).

### Decisions that are "not the ticket's to make" should route, not resolve

When a ticket surfaces a question that belongs to a different governance boundary, route the decision rather than encoding a specific outcome. User's prior quote (from 19:27 session): "It is benchmark-governance work, not a distinct product defect. Put it inline in T-20260330 as an explicit open decision or benchmark exception note."

### Strong preference for bounded notes over expansive prose

User explicitly scoped the addendum note: "a short inline note... Not a full decision, just a bounded note that records..." Resist the temptation to over-explain. The addendum's structure (Status / Contract citations / Retroactive impact / Options / Decision owner) is a template worth reusing.

### Pacing preference: thorough review over fast iteration

User consistently runs multiple review passes (two on each artifact this session). Don't rush to next-step after first-pass approval. Explicitly invite second-pass.

### Session-end posture: freeze + handoff over continue

User called for handoff before B8 despite having budget to continue. High-context, high-risk work deserves a fresh session. User's quote: "You are already at high context, and B8 is the longest, highest-risk row."

## Rejected Approaches

### Mutate B5 baseline metadata to `valid: null` or `valid: false`

**Why rejected:** Post-hoc mutation after review is not procedurally authorized and contaminates the audit trail. User explicitly: "I would **not** rewrite the raw B5 staging metadata to `valid: null` unless the procedure explicitly defines post-hoc mutation for governance disputes."

**Trade-off:** Staging artifact literally says `valid: true` while the session's classification is "provisional pending governance." Slight narrative inconsistency, but audit cleanliness matters more.

### Open separate ticket for scope-rule governance

**Why rejected:** User's framing (consistent with 19:27 decision): "benchmark-governance work, not a distinct product defect. Put it inline in T-20260330." Scattering across multiple tickets dilutes ownership.

**Trade-off:** Separate ticket would have its own lifecycle. Inline approach risks being overlooked if T-20260330-04 gets tidied up before governance resolves. Mitigated by §Next Steps flagging.

### Stay on extraction-bug branch and add addendum there

**Why rejected:** User's rule: one branch per concern. The extraction-bug ticket and the governance note have different owners, different review audiences, different merge timing.

**Trade-off:** Two unmerged branches in local tree. Mitigated by merging extraction-bug to main first, leaving only governance-note unmerged.

### Commit governance addendum before B5 candidate runs (BUT in a way that preserves commit freeze)

**Why attempted and rejected retroactively:** I did commit the addendum before B5 candidate runs — that was the mistake. Better alternatives:
- Defer commit until after B5 candidate completes
- Defer commit until after entire benchmark track completes
- Log governance decision in session chat + handoff only; commit later

**Trade-off:** The mid-track commit created the second invalidation axis for B5 candidate. Memory saved to prevent recurrence.

### Update T-20260416-01 inline now with B5 reproduction

**Why rejected:** Any commit before B8 pair completes breaks B8 same-commit invariant. User's call: "Another docs commit before B8 would introduce yet another benchmark commit boundary."

**Trade-off:** B5 reproduction evidence lives in handoff + staging until post-B8 batch update. Small audit-trail delay, avoids commit compounding.

### Merge governance branch to main before B8

**Why rejected:** Merge advances HEAD, same as any commit. B8 must run from current frozen state to be commit-parity with B5 candidate.

**Trade-off:** Governance branch stays unmerged through B8 execution. Post-B8 merge window simplifies tracking.

### Report scope breach as single count (5 or 6) without interpretive naming

**Why rejected:** User's P3: "If you exclude the AGENTS lookup as non-evidentiary orientation, your '5 probes' count is defensible; under the literal contract, it is at least 6 out-of-scope probes." Reporting only one count hides the interpretive call.

**Trade-off:** Slightly longer narrative. Required for governance decision (Option A vs B may turn on this distinction).

### Continue B8 in this session without handoff

**Why rejected:** 86% context usage + B8 is longest, highest-risk row. Fresh session for B8 review is safer. Handoff preserves decision context so next session opens cold without re-exploration.

**Trade-off:** Session break means another load cycle. Acceptable — the handoff investment pays back in fresh-session clarity.
