---
date: 2026-04-17
time: "01-41"
created_at: "2026-04-17T05:41:30Z"
session_id: d99184cb-74c8-4300-94fb-5d0a63841707
resumed_from: "docs/handoffs/archive/2026-04-16_23-43_t04-b8-pair-captured-all-four-rows-complete-adjudication-next.md"
project: claude-code-tool-dev
branch: main
commit: 2813e469
title: "T-04 closed via AC-7-direct demonstrated-not-scored closeout; T-05 pre-design reconciliation note merged"
type: handoff
files:
  - docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md
  - docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md
  - docs/benchmarks/dialogue-supersession/v1/manifest.json
  - docs/benchmarks/dialogue-supersession/v1/runs.json
  - docs/benchmarks/dialogue-supersession/v1/adjudication.json
  - docs/benchmarks/dialogue-supersession/v1/summary.md
  - docs/benchmarks/dialogue-supersession/v1/transcripts/
---

# T-04 Closed via AC-7-Direct Demonstrated-Not-Scored Closeout; T-05 Pre-Design Reconciliation Note Merged

## Goal

Adjudicate the open T-04 governance and manifest questions on the completed B1/B3/B5/B8 capture set without running more benchmark rows, then close T-04 cleanly and surface what's blocking the next critical-path packet (T-05). The session's first-next-action was inherited verbatim from the prior handoff: "Adjudicate `T-20260330-04` execution addendum plus manifest-drift posture from the completed B1/B3/B5/B8 capture set; do not run more benchmark rows before that decision."

**Trigger.** The 23:43 (2026-04-16) handoff left the repo frozen at `4c0e2a46` with all 4 benchmark pairs captured but three open governance questions: (a) Scope-Rule Governance Options A/B/C, (b) manifest reconciliation across 4 commit states, (c) AC-7 retirement decision. The handoff explicitly named adjudication — not execution — as the next session's sole task.

**Stakes.** T-04 is the empirical gate for the context-injection retirement decision (AC-7), which is itself a major architectural decision in the cross-model → codex-collaboration supersession arc. The choice of closeout path determined: (1) whether 6-10 hours of rerun work was needed; (2) whether contracts.md / operator-procedure.md needed amendment; (3) whether the captured evidence would be ratified, reframed, or replaced; (4) what the next workstream looked like.

**Success criteria:**

1. ✅ Render the three linked decisions in one pass (governance, manifest, retirement)
2. ✅ Close T-04 with a defensible audit trail
3. ✅ Identify and unblock the next critical-path packet
4. ✅ Capture durable patterns from the closeout (memory writes)
5. ✅ Surface T-05 design questions before implementation begins

**All five met.** The session also accomplished one bonus: drafted and landed a T-05 pre-design reconciliation note that documents the inherited multi-agent scope-transport question and gates AC-locking on its resolution.

**Connection to project arc.** This session converted T-04 from "open with three blocking governance questions + 8 captured runs" to "closed, retirement decision rendered, capture set imported as demonstrated-not-scored evidence." The cross-model supersession arc now has its empirical evidence layer formally complete and its next packet (T-05 execution-domain foundation) primed with a kickoff design note rather than starting cold.

## Session Narrative

**Phase 1 — Resume from 23:43 handoff (~3 min).** The /handoff:load resolved the prior session's handoff cleanly. Branch was `docs/t20260330-scope-rule-governance-note`, HEAD `4c0e2a46`, working tree clean — exactly as the freeze specified. Loaded handoff was archived; new state file written at `docs/handoffs/.session-state/handoff-d99184cb-74c8-4300-94fb-5d0a63841707`.

**Phase 2 — Initial scrutiny pass on Codex's recommendation (~25 min).** User invoked `/scrutinize` on a "Read-First Result" produced by Codex. The recommendation was: "Choose Option A for scope governance; treat manifest reconciliation as rerun territory; pick `4c0e2a46` as the rerun anchor because it's docs-only drift from `693551cc`." First action was verifying every cited line — 11 specific line-level claims across the contract, operator procedure, manifest, transcript stamps, and ticket. All citations checked out (Read calls in parallel, then a git diff confirmed inter-commit history really was docs-only). Contract reading was solid; the prescriptive section had four problems the scrutiny pass identified:

- **Critical Failure 1:** "Rerun at `4c0e2a46` self-reference" — `4c0e2a46` IS the addendum-introducing commit; rerunning under it means decision-of-record commit will diverge from rerun-anchor commit, recreating the manifest-drift class of problem
- **Critical Failure 2:** "Option A is uniquely contract-clean" framing — incorrect; the contract's Change Control section (`:350-357`) explicitly defines amendment as a procedure
- **Critical Failure 3:** Recommendation never engages T-20260330-04:141's own analysis that baseline scope-control may be structurally fragile (rerun could be circular)
- Cost not quantified; B3 extraction-bug risk in adversarial rerun not acknowledged

Verdict: `Major revision`. Output presented with the 9-section /scrutinize template.

**Phase 3 — Codex rebuttal and convergence (~30 min).** User pasted Codex's revised assessment (delivered through dialogue not directly callable from the session). Codex partially conceded: my recursion objection was deflated by `operator-procedure.md:140-144` (the procedure already expects `run_commit ≠ import_commit` per the staging-then-import-later model — a citation I had missed). Codex also conceded T4-BR-09 was overstated (`benchmark-readiness.md:239-241` calls the 10 amendment rows "design inventory, not prerequisites for the manual benchmark v1 contract") and conceded the corpus-wide commit anchoring point. Codex pushed back on my "2-of-2 adversarial" framing as a strawman (fair — my actual text said "Adversarial-posture rerun is one extraction-bug reproduction away," singular B3).

Verified Codex's new citations directly. All checked out. My second pass conceded the recursion and T4-BR-09 points and reframed the residual disagreement as a 2-D matrix: scope governance × commit governance. Codex agreed; verdict converged at `Defensible`.

**Phase 4 — The "goal question" pivot (~20 min).** With the four paths (A+1, B+1, B+2, C) on the table, the ranking depended on the user's actual goal — was the formal aggregate score the deliverable, or was the AC-7 retirement decision the deliverable with the score as instrument? Surfaced this as "the goal question" and added a fifth option not previously named: **AC-7-direct** (render retirement on architectural signature + caveats, treat AC-6 as instrumental).

User asked me to clarify what "the goal question" meant. I answered with two framings:
- **Framing 1:** AC-6 is load-bearing → the retirement decision needs a formal pass-rule rendering → B+1 or B+2 wins
- **Framing 2:** AC-6 is instrumental → the captured artifacts already DEMONSTRATE the architectural signature → AC-7-direct wins

Provided a "useful test exercise": try writing the opening paragraph of the AC-7 retirement decision under each framing. The one you'd actually write is the path you should pick.

**Phase 5 — User commits to "signature is sufficient" (~5 min).** Two-word answer that collapsed the matrix. With AC-7-direct chosen, the entire scope-rule governance debate (A/B/C) became moot (no formal scoring → no rule to apply), and manifest reconciliation became a documentation question (no aggregate scoring → no commit-parity requirement). Outlined what AC-7-direct commits to (4 things: signature-based AC-7 text, AC-6 reclassification, addendum closed-as-moot, manifest preserved as historical record) and what stays open (T-20260416-01 extraction bug, L1/L2/L3 mechanism losses).

Proposed an 8-step closeout sequence and asked two clarifying questions: (a) inline AC-7 text in the ticket vs standalone decision record; (b) where to promote staging artifacts.

**Phase 6 — User implements; I review (~25 min).** User stated "I'll handle the implementation and then I will share it with you for review." Then returned with: ticket marked closed, AC-6 reclassified, scope-rule addendum resolved-as-moot, retirement decision text inline, summary.md replaced with closeout summary, manifest closeout block added, runs.json imported with `_closeout_note`, adjudication.json explicitly empty, 16 transcript files promoted into v1/transcripts/, staging backup completed at `~/benchmark-v1-staging-backup`.

Read all 5 modified files + ls of the transcripts directory + git status, in parallel. Found the implementation strong — preserved capture-time metadata over retconning, kept `adjudications: []` empty rather than faked, addendum closed honestly with "resolved as moot" framing. Three issues worth fixing before commit:

1. **Verification section** (lines 93-102 of T-04 ticket) used future-tense imperatives ("Run at least one end-to-end dialogue...") on a closed ticket — read as outstanding work
2. **Manifest `run_timestamp`/`operator`** filled in with import-time values without disambiguation note
3. **AC-6 wording** said "aggregate pass/fail not rendered" but should also mention per-task metrics

Three follow-up items: branch handling, memory writes, AC-6 precision (optional).

**Phase 7 — User applies cleanup edits; I verify diffs (~5 min).** User applied all three pre-commit fixes. Verified via `git diff` — all clean: Verification section converted to past-tense satisfied checks with citations; manifest `import_metadata_note` field added to closeout block; AC-6 wording mentions both per-task and aggregate. Bonus catch worth noting: original addendum text edited from `**Status:** Open` to `**Historical status at addendum authoring time:** Open` — preserved historical wording without making it false.

**Phase 8 — Commit + merge + push (~3 min).** Committed at `1fd8f3e2` on `docs/t20260330-scope-rule-governance-note` (21 files, 24,762 insertions). Switched to main, merged with `--no-ff` (matching prior style), got merge commit `9767dc1c`. Deleted feature branch. Memory writes followed: 3 new feedback files (carry posture, signature-sufficient, system-prompt-vs-cmd) plus MEMORY.md index update. User then said "push it." Pushed `71f442ce..9767dc1c` to origin/main.

**Phase 9 — Next-step sequencing (~15 min).** User pasted analysis from Codex naming T-20260330-05 as next critical-path packet. Asked me about the wording mismatch between T-04's actual closure (demonstrated-not-scored) and T-07's gate text ("passing benchmark result"). Read T-05, T-06, T-07, T-20260416-01 in parallel + dispatched Explore agent to mine archived handoffs for context relevant to the post-T-04 sequencing decision.

Confirmed the T-07 wording mismatch with direct line citations. Explore agent surfaced a deeper finding: the T-04 v1 scoping plan (`docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md:80-107`) explicitly carved out "Remaining T-04 acceptance" work that included **multi-agent scope-transport extension** as deferred. The PR-107 merge handoff at 23:51 listed that as still-open at merge time. So the question wasn't "is T-05 unblocked?" (it formally was) but "did T-04's closure resolve what T-05 actually needs?"

**Phase 10 — Reconciliation reading pass (~15 min).** User explicitly authorized the bounded reconciliation: read v1 plan §2.2 + the PR-107 handoff. Verified the four deferred items individually:

- Pre-dialogue gatherer agents: **absorbed** in PR #107
- Deterministic briefing assembly: **absorbed** in PR #107
- Multi-agent scope-transport extension: **dodged, not solved** — PR-107 handoff line 596-603 documents the workaround "gatherers are not containment subjects"
- Shakedown-to-production reference unification: **still open** — PR-107 handoff line 70 explicitly lists it as open at merge

Critical realization: the dialogue path's workaround (gatherers run OUTSIDE containment as read-only scouts) does NOT generalize to delegation jobs (which are contained execution subjects by definition). T-05 inherits the unsolved problem in a form where the dialogue workaround isn't available. Verified by reading hooks.json:14-22 (SubagentStart matcher excludes gatherers) and checking contracts.md:59-73 (DelegationJob has NO scope field — only `requested_scope` exists, on PendingServerRequest, for mid-job approval asks).

**Phase 11 — Codex narrows the question; I refine + draft kickoff note (~20 min).** Codex sharpened the framing: delegation isn't general multi-agent scope transport; it's a one-shot parent→child handoff at job creation. Proposed four design questions for a T-05 kickoff note. I added a fifth (#0: reference reconciliation against existing scope_envelope material — because answering 1-4 without first deciding "adopt or replace the existing concept" risks rework). Drafted the full kickoff note as text for review before editing the ticket. User approved with two refinements: (a) soften "cannot read the parent's containment seed" to "must not depend on the parent session's containment state" (avoid overcommitting to mechanism); (b) add explicit consequence in Question 1 about contracts.md + persisted job model needing to change together.

**Phase 12 — Land kickoff note + review fixes (~10 min).** Created branch `docs/t05-kickoff-design-note`. Inserted the note between `## Scope` and `## Acceptance Criteria` in T-05's ticket. Committed at `6ed5f731` (1 file, 101 insertions). User reviewed the rendered ticket and surfaced two findings via structured code-comment format:
- **P2 (high confidence):** the manifest cite at `:36-43` doesn't actually mention `scope_envelope` — first references are at `:53-56`, and the concrete schema lives in the gatherer agent docs
- **P3 (lower confidence):** the note cited an off-repo handoff (in `~/.codex/`) for the "gatherers outside containment" claim — should use repo-visible evidence instead

Both verified. Manifest `scope_envelope` references are at lines 52-53 (within the prompt_only.allowed_roots block); the concrete schema (`{allowed_roots: string[]}`) IS documented at `agents/context-gatherer-{code,falsifier}.md:23`. Hooks.json:14-22 shows the SubagentStart matcher excludes gatherers — durable repo evidence. Applied both fixes as a separate commit (`b6e9ef5e`) per the "create new commit, not amend" project rule. Merged feature branch with `--no-ff` (commit `2813e469`), pushed `9767dc1c..2813e469` to origin, pruned the branch.

**Session ended at 96% context (1M model) — well above the prior session's threshold but with deliverables landed cleanly.**

## Decisions

### Decision 1: AC-7-direct closeout (signature is sufficient)

**Choice:** Resolve T-04 by rendering the AC-7 retirement decision on the captured architectural signature plus three explicit caveats, without producing a formal aggregate score. AC-6 reclassifies as "demonstrated-not-scored, scoring instrument not applied." The Scope-Rule Governance Addendum (Options A/B/C) closes as moot because there's no aggregate scoring for the rule to govern.

**Driver:** User's explicit goal-selection: "signature is sufficient." Made after I framed two interpretations of T-04's deliverable structure: (1) AC-6 is load-bearing → score is the deliverable; (2) AC-6 is instrumental → architectural signature + caveats is the deliverable. The captured evidence (4-for-4 candidate scope discipline; baseline B1: 8+, B3: 4, B5: multiple, B8: 26 out-of-scope reads) already established the architectural signature. The pass-rule rendering would have formalized what the captures already showed.

**Alternatives considered:**
- **A+1 (no amendment + corpus-wide rerun on post-decision commit `X`):** rejected because T-20260330-04:141 predicts baseline prompt-only scope control is structurally fragile under breadth-inviting topics. Rerun would likely reproduce breaches at lower magnitude, ending at the same governance question with another 6-10 hours burned.
- **B+1 (amendment narrowing scope-invalidation to agent-side + corpus-wide rerun):** valid path under the contract's Change Control (`:350-357`). Rejected because rerun cost is high and the amended-rule rerun's value depends on whether scoring rigor is itself a deliverable — which it isn't under the user's goal selection.
- **B+2 (amendment + retroactive ratification of existing captures):** valid but reads as motivated reasoning to skeptical future readers unless amendment text explicitly addresses retroactive coverage with rigor; sets precedent that amendments can ratify existing captures. Rejected because AC-7-direct gives the same closure with cleaner audit-trail framing.
- **C (methodology revision into v2):** months of work; doesn't close T-04. Rejected as wrong fit for closeout.
- **Null (defer freeze indefinitely):** doesn't unblock anything. Rejected.

**Implications:**
- Saved 6-10 hours of rerun work
- Avoided forcing a contract amendment for an instrument that wasn't load-bearing for the decision
- T-04 closes in one session
- Capture artifacts preserved as evidence in their natural shape (capture-time metadata kept; not retconned)
- Three caveats become first-class content of the AC-7 decision text rather than asterisks on a score

**Trade-offs accepted:**
- AC-6 doesn't close as "passed" — it reclassifies. Future readers see "score not rendered" rather than a checkbox green
- T-07's existing wording ("removal only if T-04 records a passing benchmark result") becomes a wording mismatch that will need to be addressed when T-07 is picked up
- The lenient interpretation that produced the captures is acknowledged but not formally amended away

**Confidence:** High (E3). User directive explicit, multiple independent verifications of the captured evidence, two-round dialogue with Codex converged at `Defensible`.

**Reversibility:** Medium-Low. Once the AC-7 decision text is written and the manifest carries the closeout block, reopening would require explicit ticket reactivation and rationale. No physical state change is irreversible, but the audit-trail framing is durable.

**Change trigger:** Discovery that a downstream consumer (e.g., compliance audit, external stakeholder) actually requires the formal aggregate score. None known to exist.

### Decision 2: Don't reopen T-04 to fix T-07 wording mismatch

**Choice:** Carry the T-07 wording mismatch forward as a deferred cleanup; address when T-07 is picked up rather than reopening T-04 retroactively.

**Driver:** My own analysis (Codex agreed) — T-07 says "remove context-injection only if T-04 records a passing benchmark result" (`:41`, `:59`). T-04 closed as `demonstrated-not-scored`, not as "passing." But the wording mismatch is the same inherited-formal-score assumption that AC-7-direct itself addresses. Substantively, T-04 produced exactly the evidence the gate exists to require, just in a different shape than the wording assumed.

**Alternatives considered:**
- **Reopen T-04 to retroactively rephrase ACs to match T-07's language:** rejected because reopening a closed ticket is heavier-weight than the actual problem warrants, and the alignment is conceptual not literal
- **Add a closing addendum to T-04 stating "this satisfies T-07's intent":** rejected because the relevant readership is whoever picks up T-07, and the natural place to do the reframing is in T-07 itself
- **Open a small reconciliation ticket now:** rejected because T-07 is medium-priority and not yet active; addressing the wording when T-07 picks up has zero cost and avoids governance overhead

**Implications:**
- Whoever picks up T-07 sees the mismatch as their first task — they can either rephrase T-07's gate to "T-04 records an explicit retirement decision" or add an interpretive note pointing to T-04's Resolution section
- T-04 stays cleanly closed without retroactive edits
- No new ticket created (governance overhead avoided)

**Trade-offs accepted:** The mismatch sits on main visibly until T-07 is active. Future readers cross-referencing T-04 and T-07 might be momentarily confused; the T-04 closeout text is clear enough that the resolution is obvious.

**Confidence:** High (E2). My analysis + Codex agreement + the wording mismatch being a known pattern (same as AC-7-direct's reason for existing).

**Reversibility:** High. If a stakeholder needs the alignment NOW, a 5-minute T-07 amendment lands it.

**Change trigger:** T-07 becomes actively contested or a stakeholder demands the alignment before T-07 is picked up.

### Decision 3: T-05 is the next critical-path packet, with design reconciliation as the first move

**Choice:** Sequence T-20260330-05 as the next packet on the supersession critical path. First move on T-05 is NOT implementation — it's a design reconciliation pass to answer the inherited multi-agent scope-transport question deferred from T-04 v1. T-20260416-01 (extraction bug) runs as a parallel side thread.

**Driver:** Multiple verified facts converge:
- T-05 is `open` and `high` priority with `blocked_by: [T-20260330-03]`, which is closed
- T-05 directly blocks T-06, which blocks T-07
- The Explore agent's mining of archived handoffs found that T-04 v1 plan §2.2.3 explicitly deferred multi-agent scope-transport, and the PR-107 merge handoff still listed reference unification as open at merge — so the deferred list was not obviously absorbed before T-04 closed
- Verified: the dialogue path's workaround for scope-transport ("gatherers are not containment subjects" per `hooks.json:14-22`) does NOT generalize to delegation jobs because delegation is contained execution by definition
- Verified: contracts.md:59-73 has NO scope field on `DelegationJob`; only `requested_scope` exists on `PendingServerRequest` (different shape, mid-job approval ASK not initial scope)

**Alternatives considered:**
- **T-20260416-01 first:** rejected because the bug fix is medium-priority post-benchmark cleanup; T-05 is on the supersession critical path and unblocks T-06 + T-07
- **Treat T-05 as pure greenfield (skip reconciliation):** rejected because the contracts.md spec gap is real and the inherited design question is non-trivial; jumping to implementation risks designing delegation around an envelope shape that turns out to be wrong
- **Open a separate "T-04.5" prerequisite ticket for scope-transport:** rejected because the design question only matters in T-05's context; separating creates artificial coupling and governance overhead. The kickoff design note inside T-05 keeps the issue where it belongs
- **C (methodology revision):** wrong fit; T-05 isn't a benchmark methodology question

**Implications:**
- T-05's existing 6 ACs may need to change after the design pass (additional AC for scope-transport mechanism, possible spec update for `DelegationJob`)
- contracts.md may need a scope field added to `DelegationJob` as part of T-05's implementation
- Reference unification (the other still-open T-04 §2.2 item) is orthogonal to T-05; can land under T-07 or as standalone cleanup

**Trade-offs accepted:**
- T-05 starts with an inherited design debt rather than as a clean greenfield packet
- The kickoff note adds ~100 lines to T-05's ticket (98 → 199 lines) — substantial but proportionate

**Confidence:** High (E3). Verified contracts.md, hooks.json, manifest.json, gatherer agent files, and the v1 plan deferral block. Two-round dialogue with Codex converged on the same sequencing.

**Reversibility:** High. The kickoff note is text in a ticket; can be revised or removed in a single commit.

**Change trigger:** Discovery that scope-transport was actually solved somewhere I didn't look (e.g., in the orchestrator code rather than the documented contracts), OR a stakeholder decision to defer T-05 in favor of a different workstream.

### Decision 4: Scope kickoff note inside T-05, not a separate prerequisite ticket

**Choice:** Add a "Pre-Design Reconciliation" section to T-05's ticket between `## Scope` and `## Acceptance Criteria`. The section names the inherited question, lists existing material to read first, poses 5 design questions that gate AC-locking, and explicitly states what the note is NOT (not a re-opening of T-04, not a contract change in itself, not a general multi-agent scope-transport solution).

**Driver:** The threshold question is "is the missing contract small enough for a design note vs big enough for its own prerequisite ticket?" My read: design note is the right size because (a) the scope-transport question only matters in T-05's context; (b) separating creates artificial coupling; (c) the dialogue workaround is a clear negative reference point worth keeping inside T-05's reasoning trail; (d) a separate ticket adds governance overhead for what is essentially "T-05 must specify how scope works."

**Alternatives considered:**
- **Separate prerequisite ticket (e.g., T-04.5 or T-05-pre):** rejected per the threshold reasoning above
- **Free-floating design doc under `docs/plans/` referenced from T-05:** rejected because the ticket itself is the natural authority for what blocks AC-locking; offloading to a plan doc adds indirection
- **Just verbal handoff to whoever picks up T-05 (no ticket change):** rejected because verbal context is fragile; the ticket should be self-sufficient

**Implications:**
- T-05's ticket gains explicit gating language: "Do not lock ACs until the design pass closes the five questions above"
- Whoever picks up T-05 walks into the reconciliation question on their first read of the ticket
- The kickoff section becomes the reasoning anchor for the eventual design choice

**Trade-offs accepted:**
- T-05 ticket grew from ~98 to ~199 lines; readers see more before reaching ACs
- Some redundancy between the kickoff note and the eventual design that resolves it

**Confidence:** High (E2). My analysis + Codex agreement.

**Reversibility:** High. The note can be edited or removed in a single commit if it turns out to mislead.

**Change trigger:** The design pass reveals the question is bigger than expected (genuinely needs its own ticket), OR the design is so trivial that the kickoff note is overhead.

### Decision 5: Use the "create new commit, not amend" rule even within a feature branch

**Choice:** Apply the user's "create new commit rather than amending" preference even when the feature branch hasn't merged yet. Review fixes for the kickoff note landed as a separate commit (`b6e9ef5e`) rather than `git commit --amend` on the original `6ed5f731`.

**Driver:** Global CLAUDE.md says "Prefer to create a new commit rather than amending an existing commit." Doesn't qualify based on whether the branch has merged. Explicit preference > convenience.

**Alternatives considered:**
- **Amend the original commit:** would have produced a single clean commit on the feature branch, but violates the explicit rule
- **Force-push after amend:** doubly violates (amend + force-push)

**Implications:**
- The merge commit on main contains 2 squashed commits visible in history
- Audit trail clearly shows "kickoff note" → "review fixes per P2/P3"
- Slightly more verbose history for a 1-file change

**Trade-offs accepted:** History verbosity vs. rule conformance. The rule wins because it's explicit and reflects a strong preference.

**Confidence:** High (E1). Direct CLAUDE.md text.

**Reversibility:** N/A (history-shaped; not worth rewriting for cosmetics).

**Change trigger:** User explicitly authorizes amending in a future case.

## Changes

### Files modified (T-04 closeout, by user; reviewed by me)

- `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` — status closed, AC-5/6/7 marked complete with reclassification, Resolution section added (lines 156-192), Closeout Notes section added (194-220), Verification section converted to past-tense satisfied checks
- `docs/benchmarks/dialogue-supersession/v1/manifest.json` — `closeout` block added (multi-commit history preserved as `captured_commits` array; `aggregate_scoring: not_rendered`); top-level `run_timestamp`/`operator` populated with import-time values (disambiguated by `import_metadata_note`)
- `docs/benchmarks/dialogue-supersession/v1/runs.json` — all 8 runs imported with `_closeout_note` disclaiming `valid: true` as capture-time metadata, not final scored verdict; `execution_mode: demonstrated_not_scored`
- `docs/benchmarks/dialogue-supersession/v1/adjudication.json` — `_closeout_note` explicit; `adjudications: []` empty (not faked); schema preserved
- `docs/benchmarks/dialogue-supersession/v1/summary.md` — full closeout summary with capture set table, retirement decision, three caveats; replaces blank scored template
- `docs/benchmarks/dialogue-supersession/v1/transcripts/` — 16 new files (B1/B3/B5/B8 × {baseline,candidate} × {transcript,synthesis}) imported from `/private/tmp/benchmark-v1-staging-20260415/`

### Files modified (T-05 kickoff note, by me)

- `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` — new "Pre-Design Reconciliation: Inherited Scope-Transport Question" section inserted between Scope and Acceptance Criteria (101 insertions in initial commit; 14 insertions / 6 deletions in review-fix commit); ticket grew from ~98 to ~199 lines

### Memory writes (in `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/`)

- `feedback_carry_posture_when_contamination_captured.md` — when contamination has entered the captured set AND pausing won't undo it AND pausing+adjudicating creates more noise than continuing → carry, adjudicate once on full evidence set
- `feedback_signature_sufficient_for_decision.md` — for retirement/supersession decisions with clear directional evidence, signature + caveats can be the deliverable instead of formal aggregate score (AC-7-direct pattern)
- `feedback_system_prompt_mentions_not_scouting_signals.md` — when grep-auditing transcripts for scope compliance, distinguish system-prompt boilerplate (what tools COULD read) from `exec_command` invocations (what they DID read); use `"cmd":.*<path>` pattern
- `MEMORY.md` — index updated with three new feedback entries

### Git state changes

| Commit | Branch | Change |
|---|---|---|
| `1fd8f3e2` | `docs/t20260330-scope-rule-governance-note` | T-04 closeout artifacts (21 files, 24,762 insertions) |
| `9767dc1c` | `main` (merge) | Merge T-04 closeout via `--no-ff` |
| `6ed5f731` | `docs/t05-kickoff-design-note` | T-05 kickoff note initial draft (1 file, 101 insertions) |
| `b6e9ef5e` | `docs/t05-kickoff-design-note` | T-05 kickoff note review fixes per P2/P3 (1 file, 14 insertions / 6 deletions) |
| `2813e469` | `main` (merge) | Merge T-05 kickoff note via `--no-ff` |

Both feature branches deleted post-merge. Origin/main pushed twice: once after T-04 closeout (`71f442ce..9767dc1c`), once after T-05 kickoff note (`9767dc1c..2813e469`).

### Handoff / state files

- Archived: `2026-04-16_23-43_t04-b8-pair-captured-all-four-rows-complete-adjudication-next.md` → `docs/handoffs/archive/`
- State file (this session): `docs/handoffs/.session-state/handoff-d99184cb-74c8-4300-94fb-5d0a63841707` — to be cleaned up by save procedure
- New handoff (this file): `docs/handoffs/2026-04-17_01-41_t04-closed-ac7-direct-and-t05-kickoff-note-merged.md`

## Codebase Knowledge

### contracts.md — DelegationJob has no scope field

Path: `docs/superpowers/specs/codex-collaboration/contracts.md:59-73`

```
### DelegationJob
A unit of autonomous execution work. One job = one execution runtime = one worktree.

| Field | Type | Description |
|---|---|---|
| job_id | string | Plugin-assigned unique identifier |
| runtime_id | string | Execution runtime identifier |
| collaboration_id | string | Associated CollaborationHandle |
| base_commit | string | Git commit SHA the worktree was created from |
| worktree_path | path | Absolute path to the isolated worktree |
| promotion_state | enum | ... |
| status | enum | queued, running, needs_escalation, completed, failed, unknown |
| artifact_paths | list[path] | Paths to produced artifacts |
| artifact_hash | string? | Hash of the reviewed artifact set |
```

**Critical observation:** No scope/allowed_roots field. The only scope-related field anywhere in this spec area is `requested_scope` on `PendingServerRequest` at line 88, which is the shape of a runtime-issued approval ASK (e.g., "may I write to /this/path?"), NOT the initial allowed scope of the job.

This is the load-bearing finding for T-05's kickoff note. T-05 either needs to add a scope field to `DelegationJob` (contracts.md change) or design scope as derivable from another source (worktree_path? collaboration_handle?).

### scope_envelope schema lives in gatherer agents, not in contracts

Paths:
- `packages/plugins/codex-collaboration/agents/context-gatherer-code.md:23`
- `packages/plugins/codex-collaboration/agents/context-gatherer-falsifier.md:23`

Both files document: `scope_envelope — optional {allowed_roots: string[]}. When set, confine all Glob/Grep/Read operations to paths under allowed_roots. Paths outside are skipped, not errored. When absent (normal production), explore the full repository. Reserved for benchmark-scored runs.`

The manifest at `docs/benchmarks/dialogue-supersession/v1/manifest.json:53-56` references `scope_envelope` operationally:
- `:53` — "scope_envelope available in delegation envelope for codex-dialogue agent" (baseline)
- `:54` — "Gatherer agents support scope_envelope but the slash skill does not pass it" (candidate)

So the concept exists, the schema is documented in agent files, but it's not formalized as a contract — and it's a benchmark-only concept on the dialogue side. Question 0 of the T-05 kickoff note is whether to formalize this as a contract or design a new descriptor for delegation.

### hooks.json — gatherers excluded from containment lifecycle

Path: `packages/plugins/codex-collaboration/hooks/hooks.json:14-22`

```json
"SubagentStart": [
  {
    "matcher": "shakedown-dialogue|dialogue-orchestrator",
    "hooks": [{ "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/containment_lifecycle.py\"" }]
  }
]
```

The `SubagentStart` matcher only triggers for `shakedown-dialogue` or `dialogue-orchestrator`. Gatherers (`context-gatherer-code`, `context-gatherer-falsifier`) are NOT in the matcher, so the containment seed lifecycle does not apply to them. This is the durable repo evidence for the "gatherers are outside containment" claim — replaces the off-repo handoff citation that the P3 review flagged.

The `PreToolUse` matcher at `:46` (`^(Read|Grep|Glob)$`) DOES apply to gatherers' tool calls, but `containment_guard.py` presumably no-ops when no containment seed exists for the agent. The architectural claim "gatherers are not containment subjects" is therefore accurate in the seed-materialization sense.

### v1 plan §2.2 — what was deferred from T-04 v1

Path: `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md:80-107`

```
### 2.2 Remaining T-04 Acceptance (explicitly not v1)
1. Production context-gatherer-code and context-gatherer-falsifier agents adapted from cross-model semantic sources.
2. Deterministic briefing assembly composing gatherer output into a structured pre-dialogue briefing block.
3. Multi-agent scope-transport design sufficient to contain gatherers alongside the orchestrator (phased scope rewrites within one run, or multi-run aggregation semantics).
4. Shakedown-to-production reference unification: dialogue-codex factored to a thin adapter over the production-local extracted reference doc, making the reference true shared authority.
5. Whatever further items the ticket's closure bar names that are not in §2.1.

### 2.3 Explicitly Out of v1
| Out of scope | Why |
|---|---|
| Pre-dialogue gatherer agents | §2.2 remaining T-04 acceptance |
| Deterministic briefing assembly | §2.2 remaining T-04 acceptance |
| Multi-agent scope-transport extension | §2.2 remaining T-04 acceptance |
| Shakedown-to-production reference unification | §2.2 remaining T-04 acceptance |
| ...
```

**Reconciliation result (verified this session):**
- Items 1-2: absorbed via PR #107 (handoff 23:51:64-66 confirms)
- Item 3: dodged by architectural choice (gatherers outside containment), NOT solved
- Item 4: still open at PR-107 merge per handoff 23:51:70

T-04's AC-7-direct closeout did not absorb Items 3-4. They carry forward.

### operator-procedure.md — load-bearing citations for benchmark closure

Path: `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md`

Key lines for closure logic:
- `:66` — "All runs must use the same commit." (corpus-wide invariant; not per-pair)
- `:140-144` — staging-then-import-later model: "All transcripts, syntheses, run metadata, and adjudication data are written here first. Nothing is imported to the repo until the entire benchmark is complete... This guarantees that all runs — including any reruns — execute against the same clean repo state." This was Codex's load-bearing citation that deflated my "recursion" objection — `run_commit ≠ import_commit` is the EXPECTED normal state.
- `:536-539` — Phase 5 import target (`docs/benchmarks/dialogue-supersession/v1/transcripts/`)
- `:660-666` — invalidation triggers (scope violation, evidence-budget overflow, run condition breach, missing artifacts)

### benchmark-readiness.md — T4-BR-09 is design inventory, not blocker

Path: `docs/plans/t04-t4-scouting-position-and-evidence-provenance/benchmark-readiness.md:239-241`

> "Ten amendment rows defining future automation-focused obligations. They are retained as design inventory, but they are not prerequisites for the manual benchmark v1 contract."

This was the citation that deflated my "T4-BR-09 makes Option B a multi-week T7 blocker" claim. The 10 amendment rows are NOT prerequisites for v1; they become load-bearing only if v2 reintroduces typed methodology thresholds. So Option B's mandatory cross-spec REVIEW per `dialogue-supersession-benchmark.md:359-363` is a review obligation, not an implement-all-10-rows obligation.

### contract Change Control section

Path: `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md:350-367`

```
## Change Control
The benchmark corpus, adjudication labels, metrics, and pass rule are fixed for this contract version. Any future change to them requires:
1. editing this contract,
2. explaining why the previous contract was insufficient, and
3. rerunning any comparison that relied on the changed rule.

Changes that affect scouting scope, evidence provenance requirements, or benchmark-readiness assumptions must also review T-04 T4 and T4-BR-09. This cross-spec review requirement is mandatory.
```

This was Codex's load-bearing citation that the contract itself defines amendment as a procedure (Option B is procedurally legitimate, not an off-book escape hatch).

### Architecture: dialogue path's contained-vs-outside split

| Component | Containment status | Source |
|---|---|---|
| Orchestrator (`dialogue-orchestrator`) | INSIDE containment (matcher hits SubagentStart) | `hooks.json:14-22` |
| Code gatherer (`context-gatherer-code`) | OUTSIDE containment (matcher excludes) | `hooks.json:14-22` |
| Falsifier gatherer (`context-gatherer-falsifier`) | OUTSIDE containment (matcher excludes) | `hooks.json:14-22` |
| Tool calls (Read/Grep/Glob) | PreToolUse guard applies always | `hooks.json:46` |

Implication for T-05: this split worked for dialogue because gatherers are read-only scouts. Delegation jobs are NOT scouts; they're contained execution subjects. T-05 cannot reuse the "outside containment" workaround.

## Context

### Mental model for the AC-7-direct closeout

Frame: **the benchmark is an instrument, not a deliverable.** The deliverable is the AC-7 retirement decision. The benchmark exists to produce evidence that supports/refutes retirement. Once enough evidence exists in any defensible form, the instrument has done its job — even if the formal pass-rule rendering wasn't applied.

This framing is what collapsed the four-option matrix. A+1 / B+1 / B+2 / C all assumed scoring was load-bearing. AC-7-direct says "the captured evidence is already conclusive enough; rendering the score adds rigor for its own sake."

### Mental model for T-05's inherited question

Frame: **delegation isn't general multi-agent scope transport; it's a one-shot parent→child handoff.** The dialogue path needed coexistence semantics (gatherer + orchestrator + Codex sharing one run with consistent scope). Delegation needs handoff semantics (parent passes scope to a contained child once at job creation).

This narrowing was Codex's contribution. It made the kickoff note tractable — five concrete questions instead of "design general multi-agent scope transport from scratch."

### Project state at session close

**T-04 (codex-collaboration dialogue parity and scouting retirement):** CLOSED via AC-7-direct demonstrated-not-scored resolution. All 7 ACs marked complete with appropriate framing. Scope-Rule Governance Addendum closed as moot. Three caveats attached to the retirement decision (T-20260416-01 open, L1/L2/L3 mechanism losses, multi-commit history).

**T-20260416-01 (codex.dialogue.reply extraction mismatch):** OPEN. Medium priority. Real product defect with 3 reproductions (B3 candidate, B5 candidate) + 1 non-reproduction (B8 candidate). NOT turn-count-driven (falsified by B8). Possibly posture-correlated; Option A fix recommended (canonicalize at runtime dispatch).

**T-20260330-05 (execution-domain foundation):** OPEN, high priority. Now has a Pre-Design Reconciliation section forcing the design pass to answer 5 inherited questions before AC-locking. The first action when this packet is picked up is to read the kickoff note + the existing material it cites, then close the 5 questions.

**T-20260330-06 (promotion flow + delegate UX):** OPEN. Blocked by T-05.

**T-20260330-07 (analytics, reviewer, cutover):** OPEN. Has a known wording mismatch ("removal only if T-04 records a passing benchmark result" at `:41`/`:59`). Patch when T-07 is picked up.

### Environment snapshot at session close

- Branch: `main`
- HEAD: `2813e469` (T-05 kickoff note merge)
- Working tree: clean
- Origin/main: synced (pushed twice this session)
- All staging artifacts now in-repo at `docs/benchmarks/dialogue-supersession/v1/transcripts/` (16 files); staging backup at `~/benchmark-v1-staging-backup` retained as belt-and-suspenders
- Memory: 3 new feedback files added; MEMORY.md index updated
- T-04 closure freeze fully released

## Learnings

### Architectural workarounds don't always generalize — and that matters for the next packet

**Mechanism.** When a deferred design question gets resolved by an architecture choice that exploits the local context (e.g., "these agents are read-only, so they don't need containment"), the workaround can be MORE durable than the original question — because the underlying problem doesn't recur in that context. But it ALSO means the next consumer of that question may not be able to use the same workaround.

**Evidence.** T-04's dialogue path resolved scope-transport by keeping gatherers outside containment (`hooks.json:14-22`). It worked because gatherers are read-only scouts. T-05's delegation jobs cannot use the same workaround — they're contained execution subjects by definition.

**Implication.** When inheriting work, examine not just "was the deferred question answered?" but "was it answered in a way that generalizes to my context?" Workarounds that are local to one context can hide unsolved problems for the next context.

**Watch for.** Future architectural inheritance situations. If T-N solved problem X with workaround Y, and T-N+1 inherits X, ask: does Y apply here, or does T-N+1 need to actually solve X?

### "What is closure FOR?" is the load-bearing question for benchmark closeouts

**Mechanism.** Benchmark adjudication frames the question as "which scoring path do we choose?" That question presumes the score is the deliverable. If the project deliverable is a decision (retirement, selection, supersession), the score may be instrumental rather than load-bearing. Asking "what is closure FOR?" surfaces this distinction explicitly.

**Evidence.** This session's four-option matrix (A+1/B+1/B+2/C) collapsed to a fifth option (AC-7-direct) the moment the user committed to "signature is sufficient." Saved 6-10 hours of rerun work and avoided forcing a contract amendment.

**Implication.** For benchmark/evaluation closeouts, the goal-clarification step is upstream of the path-selection step. Don't choose between scoring paths before establishing whether the score is the deliverable.

**Watch for.** Future evaluation-style decisions where the scoring instrument is assumed to be the deliverable. If the project goal can be served by the captured evidence alone, the formal score becomes optional rigor rather than required output.

### Distinguish capture-time metadata from final scored verdicts in import artifacts

**Mechanism.** When importing benchmark captures in a "demonstrated-not-scored" mode, the temptation is to either (a) rewrite capture-time validity flags to `null` (erases history) or (b) leave them as-is without disclaimers (misleads future readers). The right move is to PRESERVE the capture-time metadata + add explicit disclaimers that the values are not final verdicts.

**Evidence.** This session's `runs.json` keeps `valid: true` for all 8 runs as captured, with a top-level `_closeout_note`: "AC-7-direct closeout imported the captured run metadata for auditability, but did not render a formal aggregate score. `valid` values below preserve capture-time metadata and are not a final scored-validity verdict." Same pattern in `adjudication.json` with `adjudications: []` empty + explicit `_closeout_note`.

**Implication.** For future demonstrated-not-scored or reclassification-style closeouts, follow the "preserve + disclaim" pattern rather than "rewrite + claim" or "preserve + ambiguous." The pattern produces an honest audit trail.

**Watch for.** Other artifacts where capture-time metadata might be tempting to retcon (manifest fields, ticket ACs, status flags). The disclaimer-based approach scales.

### "Create new commit, not amend" applies even on unmerged feature branches

**Mechanism.** The CLAUDE.md rule reads: "Prefer to create a new commit rather than amending an existing commit." It doesn't qualify based on whether the branch has merged. The rule reflects a strong preference for visible history over clean history.

**Evidence.** This session's review fixes for the T-05 kickoff note landed as `b6e9ef5e` (separate commit) rather than `git commit --amend` on `6ed5f731`. The merge commit on main now contains 2 squashed commits visible in history.

**Implication.** Don't use "the branch hasn't merged yet" as license to amend. The rule applies uniformly. The audit trail benefit (clearly seeing "initial draft" → "review fixes per P2/P3") outweighs the cosmetic benefit of a single commit.

**Watch for.** Future cases where amend feels convenient on unmerged branches. Default to separate commits unless explicitly authorized otherwise.

### Verify cited line numbers before propagating; reviewer's confidence isn't always a guarantee

**Mechanism.** When acting on review feedback (especially structured code-comment format with confidence scores), verify the cited line numbers point at the claimed content before fixing. The confidence score reflects the reviewer's belief, not ground truth.

**Evidence.** This session's P2 review comment cited "manifest.json:36-43" for `scope_envelope` references at confidence 0.97. Verification showed `scope_envelope` references are at lines 52-53 (reviewer was off by ~10 lines but the substantive critique was correct — the original cite at `:36-43` was wrong). The fix was correct in spirit even though the reviewer's specific cite was also off.

**Implication.** Verify both the original claim AND the reviewer's correction. The reviewer being right that "X is wrong" doesn't mean their proposed "X should be Y" is right. In this case, the correct anchor was `:53-56` (slightly different from reviewer's `:36-43`). Three-step verification: (1) is the original wrong? (2) is the reviewer's framing of why it's wrong correct? (3) what's the actually-correct value?

**Watch for.** Future review-driven edits with cited line numbers. Don't trust confidence scores as a substitute for verification.

### Memory writes capture patterns, not status — and they cross-reference each other

**Mechanism.** This session's three feedback memories (carry-posture, signature-sufficient, system-prompt-vs-cmd) each capture a transferable decision-framework pattern, not a status snapshot. They implicitly cross-reference: carry-posture is the discipline that produces the evidence; signature-sufficient is the decision that resolves it without forcing more work; system-prompt-vs-cmd is the audit technique that establishes the architectural-signature claim defensibly.

**Evidence.** Each memory file leads with the rule, then `Why:` and `How to apply:` per the auto-memory schema. None of them captures "T-04 closed" (which is derivable from git log + ticket status). All capture insights that future-Claude wouldn't re-derive from artifacts alone.

**Implication.** Memory should hold non-derivable insights. Status snapshots that go stale don't belong; pattern-level lessons that survive across sessions do. When writing memory, ask: "Could future-me derive this from reading current files?" If yes, don't store.

**Watch for.** Temptation to memory-ify session summaries or status updates. Those belong in git history or handoffs.

## Next Steps

### 1. Pick up T-20260330-05 with the kickoff design pass (next critical-path packet)

**Dependencies:** None. T-05 is unblocked (T-03 closed) and now has the kickoff design note as the first reading.

**First-next-action:** Read T-05's "Pre-Design Reconciliation: Inherited Scope-Transport Question" section, then read the existing material it cites (contracts.md:59-73, manifest.json:53-56, gatherer agents:23, hooks.json:14-22). Close the five design questions in order (Question 0 first — adopt or replace `scope_envelope` shape).

**What to do:**
1. Pre-flight: confirm `git status` clean on main, HEAD at `2813e469`
2. Read T-05's kickoff note in full
3. Read existing material (4 files cited in the "Existing material to reconcile against" subsection)
4. Answer Question 0 (reference reconciliation): adopt scope_envelope as the delegation job's scope descriptor, OR design a different shape, with documented reasoning
5. Answer Questions 1-4 in light of Question 0's answer
6. Update T-05's ACs to match the chosen design (may need additional AC for scope-transport mechanism; may need spec-update note for `DelegationJob`)
7. Begin implementation per updated ACs

**Estimated effort:** 2-4 hours for the design pass alone, then T-05 implementation per its existing scope (large effort, multiple build items).

### 2. Address T-20260416-01 in parallel (post-benchmark bug fix)

**Dependencies:** None. Independent of T-05.

**What to do:** Implement Option A from the ticket — canonicalize `agent_message` extraction at runtime dispatch (`runtime.py:173-177`), moving `_read_turn_agent_message` from controller to a shared helper. Estimated effort: ~15-25 production lines + ~30-50 test lines.

**Note from this session:** The 3-reproduction + 1-non-reproduction pattern (B3, B5 reproduced; B8 didn't) was added to the ticket through prior session work. NOT turn-count-driven. Possibly posture-correlated — investigation can refine the trigger as a side benefit of the fix.

### 3. Patch T-07 wording mismatch when T-07 is picked up

**Dependencies:** T-07 becomes active.

**What to do:** When T-20260330-07 is picked up, the first task is to reconcile the wording at `:41` and `:59` ("removal only if T-04 records a passing benchmark result") with T-04's actual closure (demonstrated-not-scored). Either rephrase to "T-04 records an explicit retirement decision" or add an interpretive note pointing to T-04's Resolution section.

**Why deferred:** T-07 is medium-priority and not yet active. Patching now adds governance overhead without urgency.

### 4. Reference unification (still-open T-04 §2.2 item)

**Dependencies:** None, but low priority.

**What to do:** Factor `dialogue-codex` skill (`packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md`) to a thin adapter over the production-local extracted reference doc. Natural homes: T-07's migration documentation work, OR a small standalone cleanup ticket whenever convenient.

**Note:** Not a T-05 dependency. Orthogonal to execution-domain work.

### 5. T-05 → T-06 → T-07 sequence

**Dependencies cascade:**
- T-06 (promotion flow + delegate UX) blocks on T-05
- T-07 (analytics, reviewer, cutover) blocks on T-04 (closed) AND T-06

The full cross-model supersession completes when T-07 lands. Estimated total remaining: T-05 (large) + T-06 (large) + T-07 (medium) = several weeks of work depending on scope-transport design depth.

## In Progress

**Clean stopping point.** T-04 closed, T-05 primed with kickoff note, both merged and pushed to origin/main. No work in flight in git or in conversation.

- **Approach:** Adjudication → goal-question framing → user implementation → review → commit → merge → push → memory writes → next-step sequencing → reconciliation → design note draft → review → commit → merge → push.
- **State:** main is at `2813e469`, working tree clean, all deferred work documented in T-05 kickoff note + T-20260416-01 + T-07 wording mismatch note.
- **Working:** Two-round dialogue with Codex converged at `Defensible` for the closeout posture. Implementation review caught Verification-section tense issue, manifest semantic shift, and AC-6 wording precision. Kickoff note review caught manifest cite error (P2) and off-repo handoff cite (P3). All review fixes landed.
- **Not working:** Nothing. All session-scoped success criteria met.
- **Next action:** Pick up T-20260330-05 in a fresh session per Next Steps #1. Start with the kickoff design pass.

## Open Questions

### 1. Will T-05's design pass adopt scope_envelope or design a new shape?

**Context:** Question 0 of the kickoff note. The dialogue side's `scope_envelope` is `optional {allowed_roots: string[]}`, prompt-time guidance for read-only scouts. Delegation jobs need durable state-modeled scope that survives runtime restarts and feeds approval routing. The shapes may diverge enough to warrant a new descriptor.

**Impact:** HIGH. Determines whether contracts.md needs a new `DelegationJob` field, whether `scope_envelope` becomes a contract concept (currently informal), and whether the existing gatherer agent docs need updating.

**Decision pending until:** T-05 design pass.

### 2. Is T-20260416-01's extraction bug posture-correlated or content-correlated?

**Context:** Carried forward from prior session. 3 reproductions + 1 non-reproduction. Adversarial + evaluative reproduced; comparative didn't. Could be:
- Posture-correlated (content differs by posture)
- Content-correlated (specific turn shapes regardless of posture)
- Some other correlation

**Impact:** Low for benchmark closure (already done); moderate for T-20260416-01 fix verification (post-fix testing should cover the right posture variants).

**Decision pending until:** Post-fix investigation.

### 3. Will the T-07 wording fix be a rephrase or an interpretive note?

**Context:** T-07's gate at `:41`/`:59` says "removal only if T-04 records a passing benchmark result." Could be:
- Rephrased to "T-04 records an explicit retirement decision"
- Left intact with an interpretive note ("T-04's AC-7-direct closure satisfies this gate")

**Impact:** Low. Either approach works.

**Decision pending until:** T-07 is picked up.

### 4. Does L1/L2/L3 mechanism-loss list warrant candidate-spec amendments before T-07?

**Context:** Carried forward. Three mechanism losses self-identified in B8 candidate's synthesis: L1 (scout integrity via HMAC), L2 (plateau state machine), L3 (per-scout redaction for host-tool output). Candidate spec doesn't currently address them.

**Impact:** Moderate for retirement decision framing (already documented as caveats); HIGH for post-retirement candidate-spec evolution.

**Decision pending until:** Post-retirement candidate-spec roadmap is set.

## Risks

### 1. T-05 design pass may discover the kickoff note's framing is too narrow

**Impact:** If the design pass reveals that the scope-transport question is tangled with other delegation concerns (concurrency, escalation, runtime restart), the 5-question framing may need expansion.

**Mitigation:** The kickoff note is editable. If discoveries warrant expansion, adding more questions (or noting that the original 5 are necessary-but-not-sufficient) is a single commit.

### 2. T-07 wording mismatch causes confusion before T-07 is picked up

**Impact:** A future reader cross-referencing T-04 (closed, demonstrated-not-scored) and T-07 (gate says "passing benchmark") might misread the relationship.

**Mitigation:** T-04's Resolution section explicitly addresses what was satisfied. The mismatch is visible but the resolution path is clear from the artifacts.

### 3. Reference unification stays unscheduled and gets forgotten

**Impact:** The shakedown-to-production reference unification is a known T-04 §2.2 deferral that didn't get absorbed. If T-07 doesn't pick it up and no one opens a standalone cleanup, it could rot.

**Mitigation:** Documented in this handoff's Next Steps #4. T-07's migration documentation scope is the natural home.

### 4. Memory writes get too granular over time

**Impact:** Adding 3 feedback memories per session would bloat MEMORY.md fast. Distinction between "durable pattern" and "session-specific learning" matters.

**Mitigation:** This session's three additions are pattern-level, not status-level. Future sessions should apply the same calibration: rule + Why + How to apply, not session summaries.

### 5. Staging backup at `~/benchmark-v1-staging-backup` becomes stale

**Impact:** Now that captures are in-repo at `docs/benchmarks/dialogue-supersession/v1/transcripts/`, the backup is redundant. Eventually it should be removed (`trash`) to avoid stale-cache confusion.

**Mitigation:** Low priority. The backup is harmless until disk pressure becomes a concern. Can be cleaned up opportunistically.

### 6. T-05 picked up cold without reading the kickoff note

**Impact:** If a future session jumps to T-05 implementation without reading the kickoff section first, they'll start designing delegation without addressing the inherited scope-transport question. Result: late-stage rework.

**Mitigation:** The kickoff note is structurally placed before Acceptance Criteria with explicit gating language: "Do not lock ACs until the design pass closes the five questions above." A diligent reader will hit it before reaching ACs.

## References

### Commits this session

| Commit | Branch | Subject |
|---|---|---|
| `1fd8f3e2` | `docs/t20260330-scope-rule-governance-note` | T-04 closeout artifacts (21 files, 24,762 insertions) |
| `9767dc1c` | `main` (merge) | Merge T-04 closeout to main |
| `6ed5f731` | `docs/t05-kickoff-design-note` | T-05 kickoff note initial draft |
| `b6e9ef5e` | `docs/t05-kickoff-design-note` | T-05 kickoff note review fixes |
| `2813e469` | `main` (merge) | Merge T-05 kickoff note to main |

Pushed to origin/main twice: `71f442ce..9767dc1c` and `9767dc1c..2813e469`.

### Authority documents

| Document | Location | Role |
|---|---|---|
| Benchmark contract v1 (authority) | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Contract text, Change Control (`:350-367`), scope rules (`:166-186`), pass rule (`:295-330`) |
| Operator procedure | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | Same-commit rule (`:66`), staging-then-import (`:140-144`), Phase 5 import (`:536-539`), invalidation (`:660-666`) |
| Manifest (closeout) | `docs/benchmarks/dialogue-supersession/v1/manifest.json` | Historical run_commit + closeout block with captured_commits array |
| Summary (closeout) | `docs/benchmarks/dialogue-supersession/v1/summary.md` | Demonstrated-not-scored summary, capture set table, retirement decision |
| T-20260330-04 (closed) | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | AC-7-direct resolution, Closeout Notes, addendum closed-as-moot |
| T-20260330-05 (kickoff note) | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | Pre-Design Reconciliation section with 5 gating questions |
| T-20260416-01 (open) | `docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md` | Post-benchmark fix; 3 reproductions + 1 non-reproduction documented |
| T-04 v1 plan | `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md` | §2.2 deferred items list (`:80-107`); §2.3 explicitly out of v1 (`:100-115`) |
| Benchmark readiness | `docs/plans/t04-t4-scouting-position-and-evidence-provenance/benchmark-readiness.md` | T4-BR-09 design inventory framing (`:239-241`) |
| contracts.md | `docs/superpowers/specs/codex-collaboration/contracts.md` | DelegationJob spec (`:59-73`) — no scope field |
| hooks.json | `packages/plugins/codex-collaboration/hooks/hooks.json` | SubagentStart matcher excluding gatherers (`:14-22`) |
| Gatherer agents (scope_envelope schema) | `packages/plugins/codex-collaboration/agents/context-gatherer-{code,falsifier}.md:23` | `optional {allowed_roots: string[]}` |

### Memory files written this session

| Path | Type | Purpose |
|---|---|---|
| `feedback_carry_posture_when_contamination_captured.md` | feedback | Decision framework for contamination response |
| `feedback_signature_sufficient_for_decision.md` | feedback | AC-7-direct pattern (signature + caveats over score) |
| `feedback_system_prompt_mentions_not_scouting_signals.md` | feedback | Scope-audit grep technique |
| `MEMORY.md` | (index update) | Added 3 new entries to Feedback section |

All under `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/`.

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-16_23-43_t04-b8-pair-captured-all-four-rows-complete-adjudication-next.md`
- Same-day chain: `2026-04-16_22-25_*`, `2026-04-16_19-27_*`, `2026-04-16_12-17_*`, `2026-04-16_11-48_*` (all archived)
- Earlier T-04 work: `2026-04-15_*` series (benchmark v1 contract scaffold), `2026-04-14_*` series (PR #106 + PR #107)
- T-04 v1 plan approval: `2026-04-13_23-12_*` (in archive)

### External references

- PR #106: T-04 v1 production dialogue surfaces (AC-1, AC-2)
- PR #107: T-04 pre-dialogue gatherers + briefing assembly (AC-3, most of AC-4)
- Codex thread for closeout dialogue: not directly callable; user mediated via /copy

## Gotchas

### 1. The dialogue path's "gatherers outside containment" workaround does NOT generalize to delegation

**Symptom:** A future implementer reads T-04's PR-107 patterns ("gatherers are not containment subjects") and assumes T-05 can use the same approach for delegation jobs.

**Root cause:** Delegation jobs are CONTAINED execution subjects by definition (own worktree, own runtime, own state). The dialogue workaround relied on gatherers being read-only scouts — that's not what delegation does. The workaround is dialogue-local, not architectural.

**Prevention:** T-05's kickoff note explicitly flags this distinction. Read the kickoff note section before starting T-05 implementation.

### 2. `scope_envelope` is named in the manifest but not formalized in any contract

**Symptom:** Searching contracts.md for `scope_envelope` returns no hits; only the gatherer agent files document the shape.

**Root cause:** `scope_envelope` is an operational concept used in the dialogue path but has never been promoted to a contract-level definition. The manifest at `:53-56` references it as a benchmark-only enforcement mechanism. The gatherer agents at `:23` document the shape (`optional {allowed_roots: string[]}`).

**Prevention:** When designing T-05's scope-transport, treat `scope_envelope` as a candidate descriptor to adopt/adapt, not as an existing contract. Question 0 of the T-05 kickoff note covers this.

### 3. `DelegationJob` has NO scope field

**Symptom:** A future implementer reads the contracts.md `DelegationJob` spec and assumes scope is handled elsewhere.

**Root cause:** It's not. The spec (contracts.md:59-73) doesn't include a scope/allowed_roots field. The only scope-related field is `requested_scope` on `PendingServerRequest` at line 88, which is the shape of mid-job approval ASKS, not initial job scope.

**Prevention:** T-05's kickoff note flags this explicitly. Question 1 of the kickoff note frames the choice: add a scope field to DelegationJob (contracts.md change) OR design scope as derivable from another source.

### 4. Capture-time `valid: true` is NOT a final scoring verdict

**Symptom:** `runs.json` shows `valid: true` for all 8 imported runs, including ones with known scope contamination (e.g., B8 baseline with 26 out-of-scope reads).

**Root cause:** `valid` reflects pipeline-internal gates (metadata shape, fresh session, session_id_canonical) at capture time. It does NOT reflect scope-compliance or commit-parity. Under the AC-7-direct closeout, these were preserved as capture-time metadata with explicit `_closeout_note` disclaimer rather than rewritten.

**Prevention:** The `_closeout_note` at the top of `runs.json` and `adjudication.json` makes this explicit. Don't read `valid: true` as a scoring conclusion.

### 5. T-07's "passing benchmark result" gate doesn't match T-04's actual closure

**Symptom:** T-07 at `:41` and `:59` says context-injection removal is conditional on T-04 recording a "passing benchmark result." T-04 closed as `demonstrated-not-scored`.

**Root cause:** T-07 was authored before the architectural mismatch became visible; the gate inherited the formal-scoring assumption that AC-7-direct subsequently rejected.

**Prevention:** When T-07 is picked up, the first task is reconciling this wording. T-04's Resolution section provides the substantive answer; T-07's text needs to be reframed to match.

### 6. Two handoff streams exist for this project

**Symptom:** Personal plugin handoffs live at `~/.codex/handoffs/claude-code-tool-dev/`; repo-local handoffs live at `docs/handoffs/`. The PR-107 merge handoff cited in T-05 kickoff note's first draft was at the personal location, not the repo-local one.

**Root cause:** Two separate handoff systems coexist. The save skill in this repo writes to `docs/handoffs/`. The personal handoff stream is independent.

**Prevention:** When citing handoffs from main-branch tickets, prefer repo-visible evidence (hooks.json, code files) over off-repo handoffs. The P3 review fix this session corrected exactly this issue.

### 7. The "create new commit, not amend" rule applies even on unmerged feature branches

**Symptom:** Tempting to amend a single-commit feature branch when applying review fixes for a clean history.

**Root cause:** The CLAUDE.md rule doesn't qualify based on merge status. Visible audit trail > clean cosmetic history.

**Prevention:** Default to separate commits unless explicitly authorized. This session's `b6e9ef5e` review-fix commit is the right pattern.

## Conversation Highlights

### User's "signature is sufficient" — the load-bearing decision

User's two-word answer that collapsed the four-option matrix: "signature is sufficient."

This came after I framed the goal question with two interpretations (Framing 1: AC-6 is load-bearing → score is the deliverable; Framing 2: AC-6 is instrumental → architectural signature is the deliverable). The user committed to Framing 2 in the shortest possible way. Saved 6-10 hours of rerun work and reframed T-04's closure shape entirely.

### User's two refinements to the kickoff note draft

> "Change 'cannot read the parent's containment seed' to 'must not depend on the parent session's containment state' unless you've already proven the exact technical impossibility. That keeps the note contract-level instead of overcommitting to one mechanism story."

> "In Question 1, explicitly name the likely consequence: 'If `DelegationJob` needs an initial scope field, `contracts.md` and the persisted job model must change together.' That makes the spec/data-model coupling unmistakable."

Both refinements applied verbatim before commit. The first kept the note implementation-agnostic; the second made the contracts.md ↔ data model coupling explicit.

### User's review feedback in structured code-comment format

The P2/P3 review came as `::code-comment{...}` markdown directives with title, body, file path, line range, priority, and confidence. This was distinctly more structured than freeform review. Examples:

- P2 confidence 0.97: "The note currently sends the design pass to `manifest.json:36-43`, but those lines do not mention `scope_envelope` at all."
- P3 confidence 0.76: "This note relies on 'the 2026-04-14 PR-107 merge handoff' to support the 'gatherers are not containment subjects' claim. That handoff lives outside the repo..."

I verified both before fixing — confirmed P2's substantive critique was correct (though the reviewer's specific cite was also slightly off; correct anchor was `:53-56`, not `:36-43`). Both fixes landed in `b6e9ef5e`.

### User's directive on commits and pushes

> "merge and push"

Two-word approval pattern repeated several times this session. Used for both T-04 closeout merge and T-05 kickoff note merge. Each came after explicit review confirmation. Pattern: discuss → draft/implement → review → "merge and push" / "push it."

### Codex's narrowing of the multi-agent question

Codex (mediated through user) sharpened the inherited question:

> "Delegation jobs do not need the same shape of solution dialogue would have needed... The real T-05 question is less: 'How do multiple agents share one scope seed?' and more: 'What is the authoritative scope descriptor for a delegation job, and how is that descriptor materialized into the job's isolated runtime at job creation and mutated, if ever, by approval decisions?'"

This narrowing made the kickoff note tractable. Without it, the section would have been "general multi-agent scope transport" — too broad to gate AC-locking on.

### Session pacing

User maintained discipline around session-end timing throughout. The 23:43 prior handoff explicitly said "next session opens with adjudication, not execution." This session honored that — adjudication first, execution (closeout artifacts) was triggered by user implementation, not by me jumping ahead. The /save invocation came after both deliverables (T-04 closure + T-05 kickoff note) landed cleanly on main.

## User Preferences

### Goal-first decision framing

User's pattern: when presented with a multi-option matrix, the load-bearing question is "what is the goal?" not "which option is best?" Surfaces the prior question explicitly rather than letting the option-comparison drive the decision.

**Evidence:** This session's matrix collapsed when the goal question got asked. User's response was "signature is sufficient" — two words that resolved everything downstream.

**Watch for:** When future sessions present option matrices, surface the goal question BEFORE running comparison analysis. Comparison analysis is downstream of goal selection.

### Explicit posture discipline (carry, ratify, rerun, amend)

User's pattern from prior sessions (carried forward): when contamination or governance questions surface mid-track, name an EXPLICIT posture and reject unchosen alternatives in plain language. This session's "signature is sufficient" extended the pattern — explicit goal-selection rejecting unchosen alternatives (formal scoring as deliverable).

**Watch for:** Don't default to implicit postures. Ask "what explicit posture should we adopt?" before continuing with unclear framing.

### Iterative refinement with fast convergence

User's pattern: pose review feedback in structured form (P2/P3 priority, confidence scores, exact line citations); apply user's refinements verbatim; commit; verify diff; report briefly. The cycle is tight — one review round usually suffices.

**Evidence:** Both the T-04 closeout review and the T-05 kickoff note review converged in single review-and-fix cycles.

**Watch for:** When user provides structured review feedback, treat the format as load-bearing. Don't reformat to "looser" prose; preserve the structure (priority, confidence, exact citations).

### Verification before propagation

User's pattern: cite exact line numbers; verify the cited lines say what was claimed before acting. Applied across both directions — when user reviews my work AND when I receive review feedback to apply.

**Evidence:** This session's P2 review correctly identified that `manifest.json:36-43` doesn't mention `scope_envelope`, but the reviewer's implied "where the actual references live" was also slightly off. Three-step verification confirmed: (1) original cite was wrong; (2) reviewer's framing of why was right; (3) actually-correct anchor was `:53-56`.

**Watch for:** Verify both the original claim AND the reviewer's framing. Confidence scores reflect the reviewer's belief, not ground truth.

### "Create new commit, not amend" applies uniformly

User's preference (per CLAUDE.md): prefer separate commits over amend, regardless of merge status. Visible audit trail beats clean cosmetic history.

**Evidence:** This session's `b6e9ef5e` (review fixes for T-05 kickoff note) landed as a separate commit on the unmerged feature branch rather than as `git commit --amend` on `6ed5f731`.

**Watch for:** Don't use "branch hasn't merged yet" as license to amend. The rule applies uniformly.

### Standing-by acknowledgment after /copy

User's pattern: when invoking /copy (which copies prior assistant response to clipboard), they often follow with the same content as a real prompt or with a different instruction. The right move is minimal acknowledgment ("Copy noted") and waiting for the actual instruction. This session repeated the pattern at least 6 times.

**Watch for:** Don't engage with /copy clipboard contents unless explicitly asked. The clipboard capture is a local action; the actual instruction comes separately (or doesn't, in which case standing by is correct).

### Lock-in handoffs at high context for analytical work

User's pattern (carried forward from prior session): handoff before analytical work that needs fresh-session clarity. This session ended at 96% context with deliverables landed and the next session primed to pick up T-05 cold.

**Watch for:** Track context budget against upcoming work type. Plan handoffs before analytical thresholds, not after.

### Two-word approvals signal full alignment

> "merge and push" / "push it" / "Proceed" / "signature is sufficient"

Pattern: when alignment is complete, user commits via shortest possible affirmation. The terseness is a feature, not a sign of disengagement — it indicates the prior context did the work and no further discussion is needed.

**Watch for:** Don't treat short approvals as ambiguous. They're decisive. Execute promptly without re-asking.

## Rejected Approaches

### Rerun the corpus to apply the contract's strict scope reading (Option A+1)

**Why rejected:** T-20260330-04:141 (the addendum's own analysis) predicts baseline prompt-only scope control may be structurally fragile under breadth-inviting topics. Rerun would likely reproduce breaches at lower magnitude, ending at the same governance question with another 6-10 hours burned. AC-7-direct gives the same closure with no rerun cost.

**Trade-off:** No fresh empirical data on whether stricter prompting can salvage baseline. Not pursued because the question wasn't load-bearing for AC-7.

### Amend the contract to narrow scope-invalidation to agent-side scouting + corpus-wide rerun (Option B+1)

**Why rejected:** Cost (amendment + cross-spec T4 review + rerun) is high. Defensible and rigorous, but only worth the cost if scoring rigor is itself a deliverable. Under the user's "signature is sufficient" goal, scoring rigor isn't load-bearing.

**Trade-off:** No formally-amended contract that matches the architecture under test. Acceptable because the AC-7 decision text + summary.md make the architectural mismatch explicit without requiring contract change.

### Amend the contract + retroactive ratification of existing captures (Option B+2)

**Why rejected:** Sets a precedent that amendments can ratify existing captures; reads as motivated reasoning unless amendment text rigorously addresses retroactive coverage. AC-7-direct produces cleaner audit-trail framing.

**Trade-off:** Some captured work goes unscored. Acceptable because the architectural-signature evidence is sufficient.

### Methodology revision into v2 (Option C)

**Why rejected:** Months of work; doesn't close T-04. Wrong fit for closeout when the project goal is the retirement decision, not methodology design.

**Trade-off:** v2 methodology design isn't initiated this session. If/when it's needed, it can spawn its own ticket.

### Reopen T-04 to fix T-07 wording mismatch retroactively

**Why rejected:** Reopening a closed ticket is heavier-weight than the actual problem warrants. The mismatch is conceptual, not literal — T-04 produced exactly the evidence the gate exists to require. Patch when T-07 is picked up.

**Trade-off:** Mismatch sits visibly on main until T-07 is active. Acceptable because T-04's Resolution section makes the resolution path obvious.

### Open a separate "T-04.5" prerequisite ticket for scope-transport before T-05

**Why rejected:** The design question only matters in T-05's context; separating creates artificial coupling and governance overhead. The kickoff design note inside T-05 keeps the issue where it belongs.

**Trade-off:** T-05's ticket is longer; readers see the design context before the ACs. Acceptable because the gating effect on AC-locking justifies the inline placement.

### Free-floating design doc under `docs/plans/` referenced from T-05

**Why rejected:** The ticket itself is the natural authority for what blocks AC-locking; offloading to a plan doc adds indirection. Inline section in the ticket is more discoverable.

**Trade-off:** T-05 ticket grew from ~98 to ~199 lines. Acceptable.

### Amend `6ed5f731` with the review fixes instead of separate commit

**Why rejected:** Global CLAUDE.md says "Prefer to create a new commit rather than amending an existing commit." Doesn't qualify based on merge status.

**Trade-off:** Merge commit on main contains 2 squashed commits visible in history. Acceptable for the audit-trail benefit.
