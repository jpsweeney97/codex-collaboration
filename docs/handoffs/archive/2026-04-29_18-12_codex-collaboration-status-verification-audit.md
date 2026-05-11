---
date: 2026-04-29
time: "18:12"
created_at: "2026-04-29T22:12:21Z"
session_id: 30d246de-9ddf-438a-9357-55981b4cc615
project: claude-code-tool-dev
branch: main
commit: 65ff297b
title: codex-collaboration status documents verification audit
type: handoff
files:
  - docs/audits/2026-04-29-codex-collaboration-status-verification.md
  - docs/status/codex-collaboration-current-state.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md
  - docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md
---

# Handoff: codex-collaboration status documents verification audit

## Goal

Produce a reject-first, evidence-backed verification of the three current-facing `codex-collaboration` status artifacts so the team has a trustworthy basis for cleanup work that aligns code, specs, and operator-facing docs.

**Trigger:** User invoked `/effort max` and pasted explicit instructions to read three specific files (`docs/status/codex-collaboration-current-state.md`, `docs/status/codex-collaboration-reconciliation-register.md`, `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`) and treat every statement as a claim to verify, not as evidence. The user's prompt prescribed an exact output structure (`Verified TRUE`, `Verified FALSE`, `Unverified / Insufficient Evidence`, `Cross-Document Contradictions`, `Bottom Line`) and demanded distinction between current-facing truth and historical context.

**Stakes:** Output to be used as the basis for actual cleanup work. User explicitly stated: "Yes. Produce the revised full report - this is going to be used as the basis for cleanup work." This elevated the artifact from working note to repo-grade reference.

**Success criteria:**
- Each material claim from the three documents either verified, falsified, or marked unverified
- Evidence cited at file:line precision wherever possible
- Frame-sensitivity called out (snapshot vs current HEAD)
- Bottom-line verdicts proportional to evidence checked
- Final artifact saved in repo at `docs/audits/`

**Connection to project arc:** The drift-synthesis-recovery decision (`docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md`) established a status topology: a current-state synthesis doc + a bounded reconciliation register + an assessment-layer drift report. This audit verifies whether those three documents — produced under the new topology — actually function as the reader entry points the decision intended.

## Session Narrative

Started by invoking the `scrutinize` skill since the user explicitly requested a reject-first stance ("Adopt a reject-first review stance. Treat every statement in those documents as a claim, not as evidence"). Loaded the three target documents in parallel via Read.

First substantive observation came immediately from running `git rev-parse HEAD` and comparing to the drift report's declared snapshot at line 18: current HEAD was `19cd5183`, the drift report's snapshot was `88f098a1`. The drift report was 6 commits behind current HEAD, and the most recent commits had subjects like "docs(decisions): reflect landed drift topology" and "docs(decisions): ship drift synthesis recovery rationale" — direct signals that drift findings might have been addressed post-snapshot. This shaped the entire approach: every drift report claim had to be checked against current HEAD and (where evidence diverged) against the snapshot.

Key moment of understanding: examining `git log --oneline 88f098a1..HEAD -- docs/status/` revealed that commit `a5fd568d` ("docs(status): add codex-collaboration current-state entry point") had created the drift report file AND modified the reconciliation register simultaneously. This meant the drift report's D-04 finding ("the register omits T-20260429-02") might be true at snapshot but already addressed by the same commit that saved the report. Confirmed by `git diff 88f098a1..HEAD -- docs/status/codex-collaboration-reconciliation-register.md` showing the T-20260429-02 row added at line 69 in commit `a5fd568d`. This became the central frame-sensitive finding.

Verified the drift report's other findings systematically: fork drift (D-01) confirmed via foundations.md:174, contracts.md:23 listing fork as a tool while decisions.md:142 says it's deferred and mcp_server.py + tests enforce its absence. Unknown-request drift (D-02) confirmed via decisions.md:122-124 vs contracts.md:359 vs delegation_controller.py:984-1069. Advisory widening drift (D-03) confirmed via advisory-runtime-policy.md:32-118 (active behavior text) vs control_plane.py:154-158 + profiles.py:148-158 (hard rejection). Other findings (D-05 through D-09) similarly verified.

Discovered an under-counted skill enumeration in the drift report's Section 3 (line 40): the report claims 5 user-invocable + 1 non-user-invocable skills, but the package directory has 8 skill subdirectories. Verified `dialogue/SKILL.md:1-7` and `shakedown-b1/SKILL.md:1-6` both declare `user-invocable: true`. Initially classified as drift report omission; later (after critique) verified both skill trees existed at snapshot `88f098a1` via `git ls-tree 88f098a1 -- packages/plugins/codex-collaboration/skills/`, making the skill count wrong at both frames — properly classified as Verified FALSE.

Produced first report. User pasted a scrutinize critique via /copy paste-back: verdict `Major revision`. Key issue: D-04 classified as plain "FALSE" was too blunt — should be "true at snapshot, stale in saved artifact." Other issues: open-ticket verification standard inconsistent (didn't read frontmatter), bottom-line claims overstated. Pivoted to address each item: directly read ticket frontmatter for the three open tickets (T-20260416-01, T-20260429-01, T-20260429-02) and confirmed status/priority. Verified that D-04's "FALSE" classification could be refined to a new "Snapshot-True, Stale In Saved Artifact" category.

Produced Revision 2. User pasted second critique: verdict `Minor revision`. New issues: "internal contradiction" framing for D-04 was overstated (the contradiction is between saved artifact body and the register that ships in the same commit, not between Section 5 and D-04 logically); closed-ticket frontmatter table was less rigorous than the open-ticket table; D-08 wasn't clearly separated from the skill-enumeration falsehood; bottom-line `current-state.md` reliability claim implicitly verified the full deferred list when only 3 of 5 items had been checked. Addressed each.

Produced Revision 3. User pasted third critique: verdict `Defensible`. Three minor wording adjustments: "D-04 is the only finding..." → "D-04 is the only frame-sensitive finding identified during this targeted recheck"; closing insight about D-01/D-02/D-03 sequencing was too compressed (should distinguish doc-only from behavior-decision work); needed an explicit statement about the artifact relationship to the original drift report (replace/supersede vs patch). Addressed all three.

User then asked to save the final revision at `docs/audits/`. Ran into the project's branch-protection hook (per `.claude/rules/workflow/git.md`), which blocks Edit/Write on `main`. Created working branch `docs/codex-collaboration-status-verification`, wrote the file, committed with `docs(audits): ...` message style matching recent commit history, then merged to `main` per user's "fast-path merges for doc-only changes" instruction. Used the `merge-branch` skill which performed fast-forward merge to commit `65ff297b` and clean branch deletion.

User then asked for elaboration on "distinguish doc-only from behavior-decision work" — provided detailed explanation distinguishing the two categories with concrete examples from D-01 (doc-only), D-02 (behavior-decision in disguise), D-03 (behavior-decision in disguise), D-07 (multi-artifact regardless).

Set aside for later: actually executing the cleanup work the audit informs. The audit is the basis; the cleanup is the follow-on.

## Decisions

### Decision: Adopt the user's prescribed report structure verbatim instead of the scrutinize skill's default structure

**Choice:** Used the user's exact section structure (Verified TRUE / Verified FALSE / Unverified / Cross-Document Contradictions / Bottom Line) instead of the scrutinize skill's default (Premise Check / Critical Failures / etc.).

**Driver:** User's prompt explicitly prescribed the report structure with section headers and "For each item include:" sub-bullet templates. User said: "Adopt a reject-first review stance" but did not say "use the scrutinize skill's output format." The structure was a hard requirement of the request.

**Rejected alternative:** Use scrutinize skill's default structure with the user's required sections appended. Rejected because it would have duplicated content and obscured the requested verdict structure.

**Implication:** The scrutinize skill's reject-first posture informed the *stance* (treat every claim as suspect; demand evidence) but the *output* was user-defined. This separation is sustainable: skill = methodology; user prompt = interface.

**Trade-offs accepted:** Lost the scrutinize skill's "Adversarial Perspectives Applied" section, which can surface non-obvious failure modes. Compensated by being explicit about frame-sensitivity (snapshot vs current HEAD), which functioned as the equivalent perspective.

**Confidence:** High (E2) — both the scrutinize skill instructions and the user prompt were unambiguous; conflict was resolved by the user's prescribed structure being more specific to the task.

**Reversibility:** High — could regenerate with scrutinize structure if needed; no irreversible commitments made.

**Change trigger:** If a future request for a similar audit doesn't prescribe structure, default to scrutinize.

### Decision: Reclassify D-04 from "Verified FALSE" to a new "Snapshot-True, Stale In Saved Artifact" category

**Choice:** Created a new section between "Verified FALSE" and "Unverified / Insufficient Evidence" specifically for findings that were true at the report's declared analysis snapshot but became stale in the saved artifact.

**Driver:** First-round critique exposed that calling D-04 simply "FALSE" conflated two distinct questions: "Was the claim true at the declared snapshot commit?" and "Is the claim true in the saved/current-facing artifact?" The drift report's own line 12 declares: "The saved artifact itself is an assessment-layer document and is outside that pre-write snapshot." Honoring that frame required a separate category.

**Rejected alternatives:**
- **Keep in "Verified FALSE":** Rejected because it misrepresents the finding — the original assessor was not factually wrong; the artifact aged.
- **Move to "Unverified":** Rejected because the evidence is conclusive; "unverified" implies missing evidence.
- **Add an asterisk to "Verified FALSE":** Rejected because it would have created an asymmetric category that doesn't generalize.

**Implication:** The new category gives future drift reports a place for similar findings without forcing a binary true/false judgment. It also signals the cleanup type — for findings in this category, the repair is an addressed-status annotation rather than a logical correction.

**Trade-offs accepted:** Adds a fourth category to the report structure, slightly increasing reader load. Net positive because the category names the operational distinction the cleanup executor needs.

**Confidence:** High (E3) — verified via `git diff 88f098a1..a5fd568d` that the register row was added in the report's authoring commit; verified via direct read of current register that the row is present at line 69; the contradiction is in the saved artifact, not in the underlying claim.

**Reversibility:** High — could collapse back into "Verified FALSE" with an asterisk if the team prefers binary categorization.

**Change trigger:** If the assessment-layer document gets an addressed-status annotation, this finding becomes "no longer applicable" rather than needing reclassification.

### Decision: Verify both skill trees at snapshot before classifying skill enumeration as Verified FALSE

**Choice:** Ran `git ls-tree 88f098a1 -- packages/plugins/codex-collaboration/skills/` to confirm both `dialogue/` and `shakedown-b1/` skill directories existed at the report's declared snapshot, before classifying the skill enumeration as Verified FALSE rather than Snapshot-True-Stale.

**Driver:** Critique round 2 explicitly raised this: "Keep `Verified FALSE` for the skill enumeration undercount, assuming you verified `dialogue` and `shakedown-b1` existed before `88f098a1`." This made verification a precondition for the classification.

**Rejected alternative:** Classify by inference (the skills exist at current HEAD; the snapshot is recent so they probably existed). Rejected because the audit was being used as cleanup-work basis — inference-based classifications would be challenged by the cleanup executor.

**Implication:** The skill enumeration is solidly Verified FALSE at both frames. Future cleanup work should treat it as a current-and-snapshot error in the drift report, not as drift introduced after the snapshot.

**Trade-offs accepted:** One extra git command, ~10 seconds.

**Confidence:** High (E2) — `git ls-tree` is authoritative for tree contents at a commit; both skill directories present.

**Reversibility:** High — classification can be updated if new evidence emerges.

**Change trigger:** Nothing — this is a frozen historical fact.

### Decision: Save audit at `docs/audits/` with `YYYY-MM-DD-<descriptive>.md` naming

**Choice:** Saved as `docs/audits/2026-04-29-codex-collaboration-status-verification.md`.

**Driver:** User explicitly directed `docs/audits` location. CLAUDE.md describes `docs/audits/` as "Quality audits." Existing files in the directory (e.g., `2026-01-29-brainstorming-skills-redesign-review.md`) follow `YYYY-MM-DD-<descriptive-slug>.md` pattern.

**Rejected alternatives:**
- `docs/assessments/`: Already contains the original drift report; adding the audit there would conflate verification-of-assessment with assessment-itself.
- `docs/decisions/`: Audits are not decisions.
- Inline in a status doc: Status docs are routing layers per the drift-synthesis-recovery decision, not audit substrates.

**Implication:** Future status verifications have a precedent location and naming convention.

**Trade-offs accepted:** Slight visibility loss — `docs/audits/` is not as prominent as `docs/status/`. Acceptable because the audit is an evidence trail, not a reader entry point.

**Confidence:** High (E1) — directly directed by user.

**Reversibility:** High — could move file with a single `git mv` if needed.

**Change trigger:** If the audit becomes a standing reference rather than one-time verification, may merit promotion to `docs/status/` or absorption into a permanent reference doc.

### Decision: Use a `docs/*` working branch and fast-forward merge to main

**Choice:** Created `docs/codex-collaboration-status-verification` branch off main, committed there, then fast-forward merged to main and deleted the branch.

**Driver:** Project's `.claude/rules/workflow/git.md` enforces branch protection on `main` via a `PreToolUse` hook. `docs/*` is in the recognized branch pattern list. User explicitly authorized the fast-path merge: "This project allows fast-path merges for doc-only changes - merge this locally."

**Rejected alternatives:**
- Push directly to main: Blocked by hook.
- Open a PR: User explicitly opted out ("merge this locally").
- Use `feature/*` branch: `docs/*` is the more semantically correct pattern for docs-only changes.

**Implication:** Demonstrates the docs-only fast-path workflow that the project supports.

**Trade-offs accepted:** Linear history loses the "docs branch landed here" merge commit signal. Net acceptable for a single-commit docs change; merge commit would have added noise.

**Confidence:** High (E2) — workflow rules and user authorization both explicit.

**Reversibility:** Low for this specific commit (already on main), but no destructive change occurred.

**Change trigger:** If branch protection ever requires PRs for docs changes, switch to commit-push-pr workflow.

## Changes

### `docs/audits/2026-04-29-codex-collaboration-status-verification.md` — Verification audit (NEW, 191 lines)

**Purpose:** Repo-grade verification of the three current-facing `codex-collaboration` status artifacts. Provides the cleanup executor with verified findings, frame-sensitivity classification, and a sequencing insight that distinguishes doc-only from behavior-decision work.

**Approach:** Reject-first stance. Each material claim from the three documents either verified at file:line precision, classified as snapshot-true-stale-as-saved (D-04 only), classified as Verified FALSE (skill enumeration), or marked unverified with explicit "what was checked / what is missing" structure. Bottom-line verdicts narrowed to match the evidence actually checked.

**Key sections:**
- **Verification Frame:** States current HEAD (`19cd5183`), declares D-04 as the only frame-sensitive finding, names artifact relationship to the original drift report, and provides direct ticket-frontmatter table with file:line citations for all 6 tickets (3 open + 3 closed-in-root).
- **Verified TRUE:** 16 claims (5 from current-state, 7 from register, 8 drift findings).
- **Verified FALSE:** 1 claim (drift report skill enumeration undercount).
- **Snapshot-True, Stale In Saved Artifact:** D-04, with full snapshot/saved-artifact split.
- **Unverified / Insufficient Evidence:** 4 claims (live-runtime claims, 2 of 5 deferred items, register priority ordering, P1-MINOR-SWEEP enumeration).
- **Cross-Document Contradictions:** 4 contradictions, with explicit framing of D-04 as a stale saved-artifact contradiction (not a logical contradiction).
- **Bottom Line:** Three narrowed verdicts (current-state.md = code/spec-surface index reliable; register = best current index reliable for listed rows; drift report = useful supporting evidence with two required corrections before cleanup).
- **Cleanup Sequencing:** Distinguishes doc-only from behavior-decision work for D-01, D-02, D-03, D-07.

**Future-Claude note:** The audit is structured to be readable both top-to-bottom (executive flow) and as a reference (each finding has its own evidence and classification). The "Verification Frame" section is the most important orientation piece — read it first.

### Branch lifecycle

- **Created:** `docs/codex-collaboration-status-verification` from main at `19cd5183`
- **Committed:** `65ff297b docs(audits): add codex-collaboration status verification`
- **Merged:** Fast-forward to main (no merge commit)
- **Deleted:** Branch removed locally after merge

No other files modified.

## Codebase Knowledge

### Repository commit chain relevant to this session

```
65ff297b docs(audits): add codex-collaboration status verification     ← THIS SESSION
19cd5183 docs(decisions): reflect landed drift topology
bd489f78 docs(decisions): ship drift synthesis recovery rationale
a5fd568d docs(status): add codex-collaboration current-state entry point  ← drift report saved here
72d92b22 docs(codex-collaboration): distinguish failure paths in T-20260429-02 method table
6d0713fa docs(codex-collaboration): add nested definition tracking to schema delta
88f098a1 docs: capture codex app server schema delta evidence            ← drift report's snapshot HEAD
```

The drift report claims its snapshot HEAD is `88f098a1`. Five commits separate that from the commit (`a5fd568d`) that saved the drift report. Two commits separate `a5fd568d` from current HEAD as of session start (`19cd5183`). The audit's commit is `65ff297b`.

### `codex-collaboration` plugin surface (verified at session start)

| Tool | Source | Tests |
|---|---|---|
| `codex.status` | `mcp_server.py:20-29` | enforced |
| `codex.consult` | `mcp_server.py:31-50` | enforced |
| `codex.dialogue.start` | `mcp_server.py:52-83` | enforced |
| `codex.dialogue.reply` | `mcp_server.py:84-96` | enforced |
| `codex.dialogue.read` | `mcp_server.py:97-107` | enforced |
| `codex.dialogue.fork` | **NOT REGISTERED** | `test_no_fork_tool_in_r2` enforces absence |
| `codex.delegate.start` | `mcp_server.py:108-129` | enforced |
| `codex.delegate.poll` | `mcp_server.py:130-140` | enforced |
| `codex.delegate.promote` | `mcp_server.py:141-149` | enforced |
| `codex.delegate.discard` | `mcp_server.py:150-158` | enforced |
| `codex.delegate.decide` | `mcp_server.py:159-187` | enforced |

### Skills directory (8 entries; 7 user-invocable + 1 non-user-invocable)

| Skill | user-invocable | Purpose |
|---|---|---|
| `codex-analytics` | true | Compute analytics views from outcome and audit streams |
| `codex-review` | true | Review code through codex-collaboration advisory runtime |
| `codex-status` | true | Runtime health, auth, version diagnostics |
| `consult-codex` | true | One-shot advisory consultation with status preflight |
| `delegate` | true | Delegate coding tasks to Codex (start/poll/decide/promote/discard) |
| `dialogue` | true | Multi-turn dialogue against the codebase |
| `shakedown-b1` | true | B1 pre-benchmark integration shakedown |
| `dialogue-codex` | (no field — skill says "Do NOT invoke this skill directly") | Verification dialogue contract |

### Spec drift hot spots (per drift report findings, verified)

| Finding | Code-side truth | Spec-side claim | Conflict |
|---|---|---|---|
| D-01 (fork) | `mcp_server.py` registers no fork; tests enforce absence | `foundations.md:174` "Branches call codex.dialogue.fork"; `contracts.md:23` lists fork in tool surface | Spec text describes fork as live; code intentionally excludes |
| D-02 (unknown) | `delegation_controller.py:984-1069` terminalizes | `decisions.md:122-124` says escalate; `recovery-and-journal.md:159-166` says needs_escalation; `contracts.md:359` says terminalize | Spec internally inconsistent; code matches contracts.md only |
| D-03 (advisory widening) | `control_plane.py:154-158` rejects with "not implemented in R1"; `profiles.py:148-158` rejects widening | `advisory-runtime-policy.md:32-118` describes widening as live numbered behavior | Spec narrates active runtime that doesn't exist |
| D-07 (audit schema) | `models.py:202-217` AuditEvent missing artifact_hash, causal_parent | `contracts.md:188-217` includes both fields; `recovery-and-journal.md:104-120` requires artifact_hash for promote | Code dataclass and contract spec disagree on fields |

### Spec authority structure (`spec.yaml`)

8 authority owners:
- `foundation` (architecture rules, domains, trust model, terminology) → `foundations.md`
- `contracts` (MCP surface, data models, typed responses, audit schema) → `contracts.md`
- `promotion-contract` (promotion preconditions, state machine, rollback) → `promotion-protocol.md`
- `advisory-policy` (advisory lifecycle, widening/narrowing/rotation policy) → `advisory-runtime-policy.md`
- `recovery-contract` (journal, audit-log, crash recovery, concurrency) → `recovery-and-journal.md`
- `delivery` (build sequence, deployment, compatibility, test strategy) → `delivery.md`
- `decisions` (locked design decisions, open questions) → `decisions.md`
- `supporting` (overview, evidence maps, rewrite maps) → `README.md`

The `current-state.md` Authority Owners table reproduces all 8 correctly.

### Branch protection hook behavior

The hook (per `.claude/rules/workflow/git.md`) blocks `Edit`/`Write` operations on `main` / `master`. `docs/*`, `feature/*`, `feat/*`, `fix/*`, `hotfix/*`, `chore/*`, and several others are recognized working patterns. The hook fired silently when I created the docs branch (no warning emitted because `docs/*` is allowed).

### Project commit message style (from `git log --oneline -10`)

`docs(<scope>): <imperative>` for docs work. Recent examples:
- `docs(decisions): reflect landed drift topology`
- `docs(status): add codex-collaboration current-state entry point`
- `docs(codex-collaboration): distinguish failure paths in T-20260429-02 method table`

Followed this style for the audit commit: `docs(audits): add codex-collaboration status verification`.

## Context

### Drift-synthesis-recovery decision context

The status topology under which the three target documents were created is defined in `docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md`:
- Canonical reader entry point: a current-state synthesis doc under `docs/status/`
- Open/unreconciled-work index: the existing reconciliation register
- Supporting audit evidence only: the rejected drift assessment in `docs/assessments/`

Each document must declare its role explicitly. The current-state doc must say "Start here for current state" and "This document is not a behavioral tie-breaker." The reconciliation register must remain a bounded index, not a long-form synthesis. The drift report must be demoted to non-authoritative supporting evidence.

The audit verifies that all three documents implement the topology. They do, with the exceptions documented in the audit (D-04 stale-as-saved annotation missing; skill enumeration wrong in drift report).

### Mental model: drift findings have categorical shapes

The cleanup-sequencing insight that crystallized through the critique rounds: drift findings between code and docs look uniform on paper ("docs say X, code does Y") but split into two categories with very different cleanup costs.

- **Doc-only:** code is intentional, docs are stale → single-source spec edit
- **Behavior-decision:** disagreement is unresolved → requires a decision before cleanup; if decision goes against code, becomes code + tests + docs work

The test for which category a finding falls into: would I confidently edit the docs to match the code right now without confirmation? If yes → doc-only. If I'd want stakeholder confirmation → behavior-decision.

This framing was promoted to the audit's closing insight in Revision 3 because the cleanup executor needs it for cost estimation. Bundling all drift findings as "doc cleanup" can hide a 10x cost difference.

### Frame sensitivity: snapshot vs saved artifact vs current HEAD

The drift report has three temporal layers that must be kept distinct:
1. **Analysis snapshot** (`88f098a1`): when the analysis was performed
2. **Saved artifact commit** (`a5fd568d`): when the report file landed in the repo
3. **Current HEAD**: when the audit reads the file

A finding can be:
- True at all three frames → straightforward "Verified TRUE"
- False at all three frames → straightforward "Verified FALSE"
- True at snapshot, stale at saved artifact → new category needed (D-04)
- False at snapshot, true at current HEAD → would indicate aspirational claim that came true (none observed)

The skill enumeration falsehood is the only finding I checked at snapshot directly (via `git ls-tree`); other findings were checked at current HEAD only. The audit's Verification Frame statement is honest about this: "D-04 is the only frame-sensitive finding identified during this targeted recheck. Every finding was not replayed against the snapshot."

## Learnings

### Stale-saved-artifact findings are a real category, not a binary judgment

**Mechanism:** When an assessment commits in the same change as the repair it triggers, the saved file pairs a "still missing" claim with a "now present" downstream artifact. The claim is not factually wrong (it was true at the snapshot); the artifact has aged.

**Evidence:** D-04 in this session — `git diff 88f098a1..a5fd568d` showed the register row added in the same commit as the report file.

**Implication:** Future drift reports should ship with an addressed-status mechanism. The simplest implementation: a per-document "Findings status" appendix. The structural fix: a `addressed_at_commit` field parallel to the report's existing classification fields.

**Watch for:** Any assessment that catalogs status drift and may be repaired in the same or later commit. Without an addressed-status mechanism, the report ages into self-contradiction.

### Critique round verdicts converge if each round addresses the named issues

**Mechanism:** Round 1 verdict was Major revision; Round 2 was Minor revision; Round 3 was Defensible. Each round's required-changes list was specific and bounded; addressing them produced verdict improvement.

**Evidence:** Three /copy paste-back cycles in this session, each producing a tighter critique.

**Implication:** The scrutinize skill (or scrutinize-style critique) is well-suited to iterative refinement when the artifact has multiple distinct defects. The right pattern: address every named change verbatim; push back only on items that are genuinely wrong.

**Watch for:** Critique fatigue or scope creep across rounds. If round 4 introduces new categories of defect, the original artifact wasn't ready for critique. If round 4 just rewords prior items, the artifact is converging.

### Branch protection hooks shape merge workflow even for docs-only changes

**Mechanism:** The project's `PreToolUse` hook blocks Edit/Write on `main`. Even a docs-only change requires a working branch. The fast-path: `docs/*` branch + fast-forward merge.

**Evidence:** When I tried to write directly to main, the hook would have fired (verified path: I created the branch first per the rule).

**Implication:** All future docs work in this repo should use the `docs/*` branch + merge-locally pattern unless a PR is needed. The merge-branch skill handles this cleanly.

**Watch for:** If branch protection ever requires signed PRs for docs changes, the merge-branch skill's local fast-path won't work — switch to commit-push-pr.

### Skill enumeration discipline matters for audit credibility

**Mechanism:** A drift report that under-counts the artifact surface it's documenting becomes self-referentially questionable. Reader can't trust that the report's other claims are exhaustive if the basic surface inventory is wrong.

**Evidence:** The drift report's Section 3 line 40 listed 5 user-invocable skills. The package directory has 8 (7 user-invocable). The error appears at both snapshot and current HEAD.

**Implication:** Future status documents should enumerate exhaustively or use explicit "include" hedges. The current-state.md uses "include" correctly; the drift report's exhaustive "ships X, plus Y" framing is the wrong hedge for an enumeration error.

**Watch for:** Any drift report or current-state doc that lists artifacts without an explicit hedge ("include", "among", "such as"). Either the list must be exhaustive or it must be hedged.

## Next Steps

### 1. Apply the audit's required corrections to the drift report

**Dependencies:** None — corrections are inline edits to `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`.

**What to read first:** The audit's "Bottom Line" section ("Required corrections" subsection) and the drift report itself.

**Approach:**
1. Add an addressed-status note at Section 6 D-04: "Already addressed in commit `a5fd568d` — the same commit that saved this report — except the closed-ticket-path widening half."
2. Split Section 8 step 4 into "addressed: add T-20260429-02" and "still actionable: widen closed-ticket-path warning to include T-20260330-06 and T-20260327-01."
3. Correct Section 3 line 40 / Section 4 line 52: enumerate 7 user-invocable skills (`codex-analytics`, `codex-review`, `codex-status`, `consult-codex`, `delegate`, `dialogue`, `shakedown-b1`) plus 1 non-user-invocable (`dialogue-codex`).

**Acceptance criteria:** Drift report's saved body matches the register that ships in the same commit. Skill enumeration matches reality.

**Potential obstacles:** None — both are pure edits.

### 2. Land D-01 (fork drift) — doc-only

**Dependencies:** None.

**What to read first:** Audit's D-01 entry; `decisions.md:140-148` (existing deferral); `foundations.md:174`; `contracts.md:23, 141, 164`.

**Approach:** Edit `foundations.md:174` to remove the "Branches call codex.dialogue.fork" step from the dialogue flow (or annotate as future-scope). Edit `contracts.md:23` to mark fork as deferred in the MCP tool surface table (or move to a "Deferred" subsection). Resolve internal inconsistency in contracts.md between line 23 and lines 141/164.

**Acceptance criteria:** Spec text consistent with `decisions.md:142` deferral and `mcp_server.py` absence. `test_no_fork_tool_in_r2` still passes.

### 3. Decide D-02 (unknown request handling) — behavior-decision

**Dependencies:** Decision required before cleanup. Stakeholders should resolve: is current code's terminalization the intended contract, or is `decisions.md`/`recovery-and-journal.md`'s escalation the intended contract?

**What to read first:** T-20260429-02 ticket (`docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md`) — this may already be the ticket where the decision happens.

**Approach:** Confirm with stakeholders. If terminalize is canonical → doc-only fix. If escalate is canonical → code + tests + docs work spanning `delegation_controller.py:984-1069`, contracts spec, and operator-facing skill text.

### 4. Decide D-03 (advisory widening) — behavior-decision

**Dependencies:** Decision required. Is widening / freeze / rotate / reap meant to be live runtime behavior or future-scope?

**What to read first:** Audit's D-03 entry; `advisory-runtime-policy.md:32-118`; `control_plane.py:154-158`; `profiles.py:148-158`. The register's `ADVISORY-WIDENING-ROTATION` row already characterizes it as deferred — confirm that's the team's view.

**Approach:** If future-scope → mark `advisory-runtime-policy.md:32-118` as future-scope (heading change, callout block, or move to a "Future Behavior" appendix). If live → real implementation work for freeze-and-rotate.

### 5. Land D-07 (audit schema alignment) — multi-artifact

**Dependencies:** Most expensive cleanup item. Spans `contracts.md`, `recovery-and-journal.md`, `models.py`, `delegation_controller.py`, and `skills/codex-analytics/SKILL.md`.

**What to read first:** Audit's D-07 entry. Consider opening a new ticket if not already tracked.

**Approach:** Reconcile audit-event field set across spec and dataclass. Reconcile action enumeration (13 in contracts vs 7 in analytics skill). Decide which is canonical and align all artifacts.

### 6. Address other findings as time permits

D-05 (closed-in-root tickets), D-06 (delegate skill file_change visibility), D-08 (package README skill list), D-09 (diagnostic TTL prose) are lower-risk and can be batched.

## In Progress

Clean stopping point — all session work completed. Audit landed on main at `65ff297b`. Branch deleted. No work in flight.

## Open Questions

### Should the audit replace the drift report or coexist with it?

The audit's Verification Frame says: "If retained as a repo artifact, this revision should either supersede the prior verification note or be accompanied by edits to the original drift report." The cleanup executor should pick one path. Options:

- **Supersede:** add a "superseded by 2026-04-29-codex-collaboration-status-verification.md" note to the drift report's status header.
- **Patch:** apply the audit's required corrections inline to the drift report and keep both files (drift report = primary findings, audit = verification trail).
- **Both:** patch the drift report AND keep the audit as a separate verification record.

User has not yet answered this. The audit was saved without making the choice.

### Does the team accept the current code's behavior as canonical for D-02 and D-03?

This determines whether D-02 and D-03 are doc-only or behavior-decision work. The cleanup cost varies by 10x or more between the two outcomes.

### Is the deferred priority ordering at register lines 51-62 endorsed by anyone?

The audit notes the priority ordering has no ratifying authority artifact. If it's just the register author's judgment, that's fine but should be marked as such. If it represents a planning decision, a ticket or plan should reference it.

### Is the P1-MINOR-SWEEP 14-item enumeration accurate?

The audit didn't open `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` to verify the 14-item count. If the carry-forward tracker has more or fewer items, the register row needs updating.

## Risks

### The audit could become stale if cleanup work lands without addressing D-04's stale-as-saved finding

If the drift report remains unedited and other drift findings are addressed in code, the drift report becomes increasingly stale and the audit's "required corrections" become outdated themselves. **Mitigation:** Land the audit's required corrections (D-04 annotation + skill enumeration) as the first cleanup step, before tackling other findings.

### Behavior decisions for D-02 and D-03 may take time to resolve

The audit explicitly flags both as requiring a decision before cleanup. If decisions don't happen promptly, the drift between spec and code persists. **Mitigation:** Surface to stakeholders early; D-02 may already have a home in T-20260429-02.

### Future audits in this repo may not follow the same frame-sensitivity discipline

The audit established a precedent: drift assessments need explicit verification frames. If future verification work doesn't honor this, the cycle of "stale-as-saved" findings will recur. **Mitigation:** Capture the pattern in a project learning if it recurs.

### The "doc-only vs behavior-decision" framing may be over-applied

The framing is useful for drift findings but doesn't generalize to all status work. **Mitigation:** Keep the framing scoped to drift cleanup; don't promote it to a project-wide doctrine without more evidence.

## References

- **Audit:** `docs/audits/2026-04-29-codex-collaboration-status-verification.md` (this session's output)
- **Source documents reviewed:**
  - `docs/status/codex-collaboration-current-state.md`
  - `docs/status/codex-collaboration-reconciliation-register.md`
  - `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`
- **Decision context:** `docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md`
- **Spec authority:** `docs/superpowers/specs/codex-collaboration/spec.yaml` and the 8 owner files in same directory
- **Live tickets:** `docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md`, `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md`, `docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md`
- **Closed-in-root tickets:** `docs/tickets/2026-04-23-deferred-same-turn-approval-response.md`, `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`, `docs/tickets/2026-03-27-r1-carry-forward-debt.md`
- **Code:** `packages/plugins/codex-collaboration/server/mcp_server.py`, `runtime.py`, `control_plane.py`, `profiles.py`, `delegation_controller.py`, `models.py`
- **Tests:** `packages/plugins/codex-collaboration/tests/test_mcp_server.py:21-23` (fork absence enforcement)
- **Project workflow:** `.claude/rules/workflow/git.md` (branch protection)
- **Audit commit:** `65ff297b docs(audits): add codex-collaboration status verification`

## Gotchas

### The drift report's snapshot HEAD precedes its own commit

The drift report file at `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md` was added in commit `a5fd568d`, but the report's Section 1 declares the analysis snapshot as `88f098a1` (5 commits earlier). This is intentional per the report's own status header ("The saved artifact itself is an assessment-layer document and is outside that pre-write snapshot"), but it creates the stale-saved-artifact pattern that produced D-04.

**For future-Claude:** When verifying any assessment-layer document, compare the declared snapshot commit to the file's introducing commit (`git log --diff-filter=A --oneline -- <file>`). If they differ, expect snapshot-true-stale findings.

### The branch protection hook fires on Edit/Write, not on Bash for non-git operations

I initially worried the hook would block file creation entirely on main. The hook is specifically for Edit/Write tool calls; Bash commands that create files (e.g., `tee`, `cat <<EOF >`) would be a different code path. But since I should use Write tool for all file creation per the standard tool dispatch rules, the hook effectively enforces the branch protection.

**For future-Claude:** Don't try to circumvent the hook by using Bash to write files. Create the working branch first.

### `git ls-tree` is the right tool for "did this file/directory exist at commit X?"

I used `git ls-tree 88f098a1 -- packages/plugins/codex-collaboration/skills/` to verify both `dialogue/` and `shakedown-b1/` skill trees existed at the snapshot. `git log --diff-filter=A --oneline -- <path>/SKILL.md` confirmed which commit added each file. Both commands are essential for frame-sensitive verification.

**For future-Claude:** When the question is "did X exist at commit Y", reach for `git ls-tree` first; for "when was X added", reach for `git log --diff-filter=A`.

### Critique-round verdicts named the action level

The pasted critiques used scrutinize verdict labels: `Major revision` (round 1) → `Minor revision` (round 2) → `Defensible` (round 3). Each label set expectations for response scope. Major revision = restructure. Minor revision = tighten language. Defensible = optional polish. Don't over-respond to a minor revision verdict by re-doing work.

**For future-Claude:** When a critique's verdict is `Defensible`, the artifact is approved with optional polish. Apply the named changes and stop; don't volunteer additional revisions.

## Conversation Highlights

**On audit purpose:**
User: "Yes. Produce the revised full report - this is going to be used as the basis for cleanup work. The diff above is enough for us to reason from, but it is not enough for future readers because the existing saved report still contains the stale D-04 body, stale Section 8 action, and over-broad reliability framing."
— Established the audit as repo artifact, not working note. Drove the decision to save at `docs/audits/`.

**On revision style:**
User: "I would make the revision tight, not a rewrite."
— Anchored each revision pass to the named changes only; resisted scope expansion.

**On frame sensitivity:**
User: "Be careful with 'For all other findings, current-HEAD evidence and snapshot evidence agree.' That is a strong claim. Only include it if you actually checked the relevant files at `88f098a1`, not just current HEAD."
— Forced the safer "D-04 is the only frame-sensitive finding identified during this targeted recheck" wording in Revision 2.

**On D-04 reclassification:**
User (via critique): "Calling it simply 'FALSE' is too blunt. Required change: classify it as 'true at analysis snapshot, stale/uncorrected in saved artifact,' not plain false."
— Drove creation of the new "Snapshot-True, Stale In Saved Artifact" category in Revision 1.

**On merge path:**
User: "This project allows fast-path merges for doc-only changes - merge this locally"
— Authorized fast-forward merge; activated the merge-branch skill.

**On elaboration request:**
User: "Can you elaborate on what you mean by 'distinguish doc-only from behavior-decision work'?"
— Drove the substantive explanation of the framing with concrete D-01/D-02/D-03/D-07 examples.

## User Preferences

**Repo-grade artifacts over working notes.** User said: "this is going to be used as the basis for cleanup work. The diff above is enough for us to reason from, but it is not enough for future readers..." — establishes that artifacts saved to the repo must stand on their own without conversation context.

**Tight revisions over rewrites.** User said: "I would make the revision tight, not a rewrite." — preserve structure across revision rounds; only modify what the critique names.

**Honesty about verification scope.** User said: "Only include it if you actually checked the relevant files at `88f098a1`, not just current HEAD." — claim discipline matters; "all findings agree" is a stronger claim than "no frame-sensitive evidence found."

**Direct action over confirmation.** User said: "merge this locally" rather than asking for the steps. — when the user names a specific operation, execute it; don't restate the plan.

**Critique-driven iteration.** User uses the /copy paste-back pattern with scrutinize-format critiques to drive revision rounds. The pattern: produce → critique → tighten → re-critique → ship. Verdict label sets the response scope.

**Plain-language explanations on request.** When asked for elaboration on the "doc-only vs behavior-decision" framing, user got a substantive prose explanation with concrete examples, not a re-do of the audit. Explanation depth was calibrated to the question, not to a default verbosity.

**Proactive commits.** Per user's CLAUDE.md global config: "Commit completed chunks of requested implementation, fix, or edit work without asking for confirmation." Followed in this session — committed the audit immediately after writing without asking.

**Branch protection respect.** Project rules in `.claude/rules/workflow/git.md` are real constraints; the user doesn't expect them to be bypassed. When the rules say "create the right branch," that's the path even for trivial docs work.

## Rejected Approaches

### Treating the drift report as authoritative for the verification

**Approach attempted:** Initially considered treating the drift report as the definitive list of findings to verify, with the audit being a "did we cover all of them" check.

**Why it seemed promising:** The drift report has 9 findings (D-01 through D-09) with explicit categorization. It's tempting to treat that as the audit's structure.

**Specific failure:** The user's prompt explicitly demanded "treat every statement in those documents as a claim, not as evidence" and "Do not assume the documents are internally consistent or current." Following the drift report's structure would have imported its biases — including its stale D-04 finding.

**What it taught:** A reject-first audit must verify the assessment artifact itself, not just the underlying findings. The drift report's classification of its own findings is a claim to be verified, not a frame to adopt.

### Calling D-04 simply "FALSE" without the snapshot/saved-artifact split

**Approach attempted:** Round 1 audit classified D-04 in the "Verified FALSE" section because the current register at HEAD contains the row that the drift report says is missing.

**Why it seemed promising:** It's mechanically correct. The claim "the register omits T-20260429-02" is, against the saved register, false.

**Specific failure:** The drift report's own Section 1 declares its snapshot HEAD as `88f098a1`. The "FALSE" classification ignored that frame. The user's critique correctly pointed out: "the report still uses a few too-strong phrases that could mislead future cleanup work."

**What it taught:** Snapshot-bounded artifacts need a separate truth category. Binary true/false collapses the temporal frame and produces misleading verdicts.

### Producing a full re-do at each critique round

**Approach attempted:** Briefly considered restructuring the entire audit at each critique round.

**Why it seemed promising:** Each round had real defects; a clean re-do would address all of them.

**Specific failure:** User explicitly said "I would make the revision tight, not a rewrite." Re-do would have lost the structure that the user already accepted in earlier rounds.

**What it taught:** Once a structure is approved, revisions modify content within the structure. Don't restructure unless the structure itself was named as a defect.
