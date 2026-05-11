---
date: 2026-05-10
time: "01:47"
created_at: "2026-05-10T05:47:47Z"
session_id: b2a14397-4eb7-4377-a620-1b3b933cac84
resumed_from: docs/handoffs/archive/2026-05-10_01-10_summary-overclaim-fix-cycles-2-3-committed.md
project: claude-code-tool-dev
branch: chore/codex-collab-envelope-diagnostic-overclaim-fix
commit: 0732ac01
title: "Summary: overclaim-fix plan cycle-4 revisions committed"
type: summary
files:
  - docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md
  - docs/diagnostics/codex-app-server-server-request-envelope-probes.json
  - docs/diagnostics/2026-05-01-codex-app-server-server-request-envelope-probes.md
---

# Summary: overclaim-fix plan cycle-4 revisions committed

## Goal

Continue the multi-day review-cycle work on the envelope-diagnostic overclaim-fix plan. This session: receive cycle-4 review feedback, verify each finding against codebase, get user disposition, apply edits, commit. The plan must be execution-credible before workers run it; cycle-4 surfaced a structural disposition gap (architecture-readiness section missed by cycles 1-3) plus two enforcement gaps (raw-evidence preservation only asserted, commit-body unconditionally narrating conditional outcomes).

## Session Narrative

Loaded cycle 2+3 summary handoff via `/handoff:load` (state file restored chain). User pasted a structured cycle-4 "Major revision" code review with 3 critical failures, 3 high-risk assumptions, real-world breakpoints, hidden dependency, and required changes. Invoked `superpowers:receiving-code-review` skill.

Verified all reviewer-cited line numbers against codebase: diagnostic .md lines 195+202 (parseable + architecture-spec-can-proceed wording confirmed), JSON line 45580-45591 (`architecture_spec_readiness_delta` block with `"ready": true` confirmed), plan line 587+595 (Step 3.3+3.4 verification only does syntax check + narrow grep), plan line 765+809 (hard-coded commit body + co-author trailer confirmed). Surfaced one beyond-reviewer finding during verification: the JSON readiness block is a structural mirror of the .md section (parallel pair like `compatibility_classification`) — making F1 a missed disposition site requiring full preserve-and-add treatment, not just a sweep-pattern gap.

Recommended 4 dispositions (F1-c4 + F2-c4 + F3-c4 + hidden-dep self-review) with options. User approved with two tightening modifications: F1-c4 mandatory not optional, with `architecture_spec_readiness_delta.ready` becoming `false` under rebaseline vocabulary; F2-c4 use `/private/tmp` not bare `/tmp` + derive jq projection in Task 1.4 against live JSON, not lift schematic. Kept canonical-key preserve-and-add (cycle 2's choice) with explicit external-consumer-scope caveat.

Applied edits via 18+ Edit tool calls spanning 8 areas: front matter, sweep patterns, Step 1.4, Task 2 renumber + new Step 2.5, Task 3 renumber + new Steps 3.2/3.6 + items 7+8, Step 6.2 commit-message restructure, Step 6.3 grep self-checks, Self-Review additions + renumbering updates. Plan grew 860→1050 lines (+251 −61). Verified post-edit: 35 step labels in clean sequence (0.1; 1.1-1.6; 2.1-2.8; 3.1-3.7; 4.1-4.6; 5.1-5.4; 6.1-6.3). Committed at `0732ac01`. Working tree clean.

## Decisions

### F1-c4: architecture-readiness as 5th .md / 3rd JSON site

**Choice:** Mandatory disposition site (not optional, not sweep-only). Apply preserve-and-add to JSON `architecture_spec_readiness_delta` block: rename to `_legacy_*` (preserve verbatim including `ready: true`), add new canonical block with `ready: false`, qualified `newly_satisfied_items[2]`, extended `still_missing_items` (lossless parser/response branch as a remaining requirement). Apply narrative correction to .md lines 195+202.

**Driver:** User reasoning: leaving `ready: true` standing keeps the diagnostic's strongest remaining overclaim. Reviewer's "expand the sweep" framing understated the structural fix needed.

**Alternatives:** Sweep-pattern-only fix (rejected — leaves structural site standing); F1-b out-of-scope tracking ticket (rejected — same artifact, same family); F1-c non-canonical key approach (rejected — keeping cycle 2's preserve-and-add at canonical key with external-consumer-scope caveat).

**Trade-off:** Bigger plan diff (+251 −61) but no missed disposition site.

### F2-c4: /private/tmp deterministic path + Task 1.4 projection derivation

**Choice:** Pre-edit `jq` projection captured to `/private/tmp/codex-collab-overclaim-fix-raw-evidence-pre.json`; post-edit re-extraction + `diff`. Projection MUST be derived against live JSON in Task 1.4, NOT lifted from schematic illustration.

**Driver:** User reasoning: macOS `/tmp` symlink ambiguity, plan-execution determinism, projection correctness against actual JSON shape vs the cycle-2-enumerated raw-observation list (which may have drifted).

**Alternatives:** SHA256 hash over projection (rejected — diff format more diagnostic); structured JSON-diff library (rejected — adds dependency); surgical edit constraint (rejected — too restrictive).

**Trade-off:** Pre-edit snapshot persists across Steps 3.2-3.5 (extra coordination concern but worker-instruction explicit; Step 3.6 cleans up).

### F3-c4: HTML-comment markers + executor-aware co-author placeholder + Step 6.3 grep self-checks

**Choice:** `<!-- CONDITIONAL: ... -->` / `<!-- END CONDITIONAL -->` markers wrap the JSON-disposition (Task 3) and register-annotation (Task 4) paragraphs in the Step 6.2 heredoc. Worker-instruction text above the heredoc names the editing protocol. Co-author trailer becomes placeholder `<executing model identity, e.g., Claude Opus 4.7 (1M context)>` with replacement instruction. Step 6.3 grows two grep self-checks fail-loud on marker leak or placeholder leak.

**Driver:** Heredoc text is literal; can't use shell conditionals. Need visible-but-removable markers. Plans are designed to be re-executable; hard-coded provenance lies under different-model execution.

**Alternatives:** Per-conditional shell-branched commits (rejected — complexity); template substitution with envsubst (rejected — adds tooling); section-header-based delete-this-section instructions (rejected — less clear).

**Trade-off:** Workers must edit body manually; Step 6.3 catches the failure mode; "OK: ..." positive-signal pattern makes absence salient on review.

### Hidden-dependency: keep canonical-key preserve-and-add; document external-consumer scope

**Choice:** Cycle 2's canonical-key preserve-and-add stays. New Self-Review item documents repo-internal-artifact assumption explicitly. External consumers (other projects, Codex sessions, hand-written analyses) explicitly out of scope.

**Driver:** Cycle 2's "canonical key carries current truth" reasoning still sound; cycle 3's stop condition catches repo-local breakage; reverting is larger semantic change for a hypothetical concern.

**Alternatives:** Reverse to non-canonical `compatibility_classification_rebaseline` keys (rejected by user — defensible but unnecessary); silent-on-external-consumers (rejected — explicit assumption better).

**Trade-off:** External consumer breakage path stays as future-discovery-but-not-pre-blocking; Self-Review item names the assumption.

## Changes

### `docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md` (revised once)

Cycle 4 (`0732ac01`): 860 → 1050 lines (+251 −61). Eight structural areas:

- **Front matter:** Architecture + Boundary updated for 5 sites + raw-evidence enforcement + conditional commit template.
- **Sweep patterns:** Added 5 new terms (`architecture_spec_readiness_delta`, `architecture spec readiness delta`, `architecture spec can proceed`, `parseable against`, `newly_satisfied_items`) at Verification section + Step 1.1 + Step 5.1 (and narrower additions at Step 1.4, Step 2.7, Step 3.5).
- **Step 1.4:** Added third bullet (architecture_spec_readiness_delta JSON path), updated vocabulary caveat to mention readiness block, new sub-section "Derive raw-evidence projection paths" with INCLUDE/EXCLUDE lists + temp-file path convention.
- **Step 1.1:** Verification anchors gained 5th .md site + JSON readiness block + readiness-delta vocabulary anchor.
- **Task 2:** Files section updated, new Step 2.5 (architecture-readiness .md patch), renumbered 2.5→2.6, 2.6→2.7, 2.7→2.8; Step 2.7 sweep adds architecture-readiness patterns.
- **Task 3:** New Step 3.2 (pre-edit snapshot), renumber 3.2→3.3 (Apply preserve-and-add gains items 7+8 for architecture-readiness; existing items 7-9 → 9-11; classification_supersedes.legacy_blocks adds third entry), renumber 3.3→3.4, 3.4→3.5 (rg verification gains architecture-readiness expected outputs + sweep additions), new Step 3.6 (post-edit diff), renumber 3.5→3.7.
- **Step 6.2 + 6.3:** Heredoc rewritten with conditional markers + co-author placeholder + worker-instruction text; Step 6.3 grew two grep self-checks; expected reference updated 3.5 → 3.7.
- **Self-Review:** Updated 5 existing items for renumbering + new architecture-readiness mentions; appended 4 new cycle-4 items.

## Codebase Knowledge

- **`docs/diagnostics/2026-05-01-codex-app-server-server-request-envelope-probes.md:189-202`** — "Architecture Spec Readiness Delta" section. Header at 189; three-bullet "Newly satisfied items" list (line 195: parseable-against-boundary); two-bullet "Still missing" list; closing sentence at 202 ("architecture spec can proceed only if it scopes server-request support to the observed methods"). Mirrors the JSON readiness block.
- **`docs/diagnostics/codex-app-server-server-request-envelope-probes.json:45580-45591`** — `architecture_spec_readiness_delta` block at top level. Contains `"ready": true` at line 45581, `newly_satisfied_items` array (line 45585 = parseable-against-boundary verbatim from .md line 195), `still_missing_items` array. Total JSON file is 45,592 lines including raw envelope captures.
- **JSON line 26** `"previous_architecture_ready": false` and **line 302** `"status": "ready"` — pre-existing, unrelated to architecture_spec_readiness_delta block. NOT overclaims.
- **ripgrep behavior**: `rg -i "supported"` matches the literal sequence `supported` (case-insensitive); does NOT match the bare word `support`. Confirmed empirically with line 202 verification.
- **Plan section structure** (cycles 1-3 → cycle 4): bare-word terms (`supported`, `preserved`, `lossy`) + phrase patterns (`proves compatibility`, `compatibility for the observed`, plus cycle-4: `architecture spec can proceed`, `architecture spec readiness delta`, `parseable against`) + JSON-key patterns (`local_compatibility`, `supported_methods`, plus cycle-4: `architecture_spec_readiness_delta`, `newly_satisfied_items`). Cycle-4 added 1 JSON-key + 4 phrases; no new bare-word terms (would generate noise — `support` and `ready` matched by intent).
- **Plan structure**: 35 step labels in clean sequence (0.1; 1.1-1.6; 2.1-2.8; 3.1-3.7; 4.1-4.6; 5.1-5.4; 6.1-6.3). Step 1.5 / 4.1a use letter-suffix sub-step convention; cycle-4-added Steps 3.2 and 3.6 use integer positions via renumbering.
- **`/private/tmp` vs `/tmp`** on macOS: `/tmp` is a symlink to `/private/tmp`; using `/private/tmp` directly avoids edge cases where shell rewrites or comparisons might surprise (deterministic paths preferred for plan-execution reproducibility).

## Learnings

- **Verify-before-acknowledge pays off — fourth cycle in a row.** Cycles 1, 2, 3, 4 all read as harsh ("Major revision" twice, "Minor revision" once, "Major revision" again). Verifying each finding against codebase showed each was real. Cycle 4 even surfaced a beyond-reviewer finding (JSON readiness block as structural mirror, not just .md prose gap). Reviewer verdict + disposition path are independent.
- **Reviewer framing can understate the fix.** Cycle-4 reviewer described F1 as "the sweep misses a likely surviving overclaim" — implying a sweep-pattern fix. But the JSON's `architecture_spec_readiness_delta` block is structurally parallel to `compatibility_classification` (same .md/.json mirror pattern), making F1 a missed disposition site requiring full preserve-and-add treatment. Surface beyond-reviewer findings during verification; don't accept reviewer framing as the disposition scope.
- **Asserted-not-proven is a self-replicating defect mode.** Cycle 3's root-cause framing was "verification vocabulary narrower than reader-facing claim." Cycle 4 found Step 3.3/3.4 verification has the exact same pattern: assertions about raw-evidence preservation are not enforced by the verification commands. Plans accumulate assertions before verification mechanisms; without explicit "what command would catch a violation here" review, the gap recurs.
- **Hard-coded provenance is brittle by execution context.** Plans are designed to be re-executable. Hard-coded `Co-Authored-By: <specific model>` is fine when this model authors, lies under different-model execution. Fix: placeholder + replacement instruction + post-commit grep self-check. Generalizes — any plan-text that depends on execution context (model identity, today's date, branch name) should use placeholder + replacement, not literal value.
- **Step renumbering carries cross-reference debt.** Inserting steps in the middle of Tasks 2 and 3 forced 8 cross-references to update (Self-Review, Task 6 staged-set, Step 6.3 expected output, branch matrix, conditional refs). Monolithic plans have this fragility built in. Modular plans (one file per task) would not. The 35-step sweet spot may be an upper bound for monolithic plans.

## Next Steps

1. **Re-approval gate** (cycles 1+2+3+4 cumulative diff). User reviews and decides approve / further-revise.
2. **Cycle 5 may emerge** if external scrutiny finds more gaps. Pattern from cycles 1-4 says yes-or-no probabilities are roughly even; verify-each-finding posture remains the right default.
3. **Execute Tasks 0-6** of the revised plan. Task 0 → Task 1 (discovery + projection derivation) → Task 2 (.md, 5 sites) → Task 3 (JSON preserve-and-add, conditional, with pre/post raw-evidence diff) → Task 4 (register, conditional) → Task 5 (verification sweep) → Task 6 (commit with conditional template + executor-aware co-author + Step 6.3 self-checks).
4. **PR back to main** when Task 6 lands. Six commits to merge: original (`04a7fb43`), cycle 1 (`acda226a`), cycle 2 (`1468ff9e`), cycle 3 (`c0c21285`), cycle 4 (`0732ac01`), Task 6 execution. May want to squash on PR-merge.
5. **T-20260429-01 closure** (smoke + credential probe + regression + suite pass; needs live App Server access).
6. **T-20260429-02 method matrix** (capability artifact + method-by-method classification + lossless parser/response branch).
7. **Memory update candidate**: replace "NEXT: Roadmap Steps 2-6" framing once the plan executes and lands.

## Project Arc

### Accomplishments (across sessions)

- T-20260423-02 Packet 1 (Deferred-Approval Response): MERGED 2026-04-28 (PR #126).
- Codex-collaboration drift cleanup (D-01 through D-09): COMPLETE 2026-04-30.
- Step 0 roadmap cleanup: MERGED 2026-04-30.
- Step 1 (T-20260416-01 reply extraction): CLOSED 2026-04-30.
- Step 2 (T-20260429-01 sandbox carve-outs): IMPLEMENTATION LANDED on `main` via PR #127. Closure evidence outstanding.
- May-1 App Server rebaseline scope: 6 plans + 4 .md/4 .json diagnostics + 2 architecture notes committed on main. Capability matrix + method-classification artifacts NOT YET created.
- Public-skills-repo (separate workstream): PUBLISHED 2026-05-08.
- 2026-05-09: orientation correction + plan committed (`04a7fb43`).
- 2026-05-10 cycle 1 (`acda226a`, 7 findings).
- 2026-05-10 cycles 2+3 (`1468ff9e` + `c0c21285`, 6 + 4 findings).
- This session 2026-05-10 cycle 4 (`0732ac01`, 3 critical + 1 architectural; +251 −61).

### Current position

Branch `chore/codex-collab-envelope-diagnostic-overclaim-fix` at `0732ac01`. Plan four-times-revised (initial + cycles 1-4), 1050 lines, 35 step labels, awaiting re-approval before execution. `main` still at `1ed3f3fc` for the latest codex-collab post-implementation state. Three stale feature branches still exist locally (`...-exploration`, `...-rebaseline`, `unrelated-change`). Reconciliation register at `docs/status/codex-collaboration-reconciliation-register.md` still stale (last reconciled 2026-04-30).

### Load-bearing decisions still governing the work

- `TESTED_CODEX_VERSION = MINIMUM_CODEX_VERSION = "0.117.0"` until v128 branch decision packet lands.
- Plan-first, approval-gated, **docs-only** for the contradiction fix.
- **Preserve-and-add at canonical key** (cycle 2 + 3 + 4 stable).
- **Architecture-readiness as fifth/third disposition site** (cycle 4 addition; was missed by cycles 1-3).
- **Programmatic raw-evidence preservation** via `/private/tmp` jq-projection diff (cycle 4 addition).
- **Conditional commit-message template** with `<!-- CONDITIONAL -->` markers + executor-aware co-author placeholder (cycle 4 addition).
- **External consumers explicitly out of scope** for this plan's preserve-and-add (cycle 4 addition; cycle 2's canonical-key choice retained).
- Sandbox `~/.codex/` carve-outs are subdirectory-scoped only; credential paths remain blocked.
- T-20260429-02 method-by-method classification is OUT of scope.
- Sweep additional-paths default is STOP, not in-scope (cycle 2; narrow mechanical-mirror exception bounded).

### Drift risks

- "Roadmap Steps 2-6" framing in memory pre-dates the May-1 rebaseline scope expansion.
- Three stale feature branches still exist locally. Deletable.
- Reconciliation register still ranks "Implement T-20260429-01 Phase 1" as priority #1 — addressed by Task 4 when plan executes.
- AC #3 (test suite pass) is unchecked; plan acknowledges rather than verifies.
- The committed envelope-probe diagnostic remains contradictory with rebaseline plan and code reality on `main` until the plan executes.
- Cycle 4 itself is unreviewed — cycle 5 possible.

### Downstream impacts of this session

- Plan branch now carries 5 commits to merge through PR (original + cycles 1-4); future Task 6 execution adds a 6th. May squash on PR-merge.
- Cycle 4's preserve-and-add expansion to `architecture_spec_readiness_delta` means JSON's canonical readiness key shape changes (`ready: true` → `ready: false` + new `still_missing_items` semantics). Workers MUST exclude the readiness block from the raw-evidence projection (it's expected to mutate); Task 1.4's INCLUDE/EXCLUDE list explicitly names this.
- The `<!-- CONDITIONAL: ... -->` marker pattern + Step 6.3 grep self-checks introduce a new convention for conditional plan-execution; reusable for future plans where Task 6 narrative depends on conditional task outcomes.
- The `<projection from Task 1.4>` placeholder in Step 3.2 + 3.6 heredocs requires worker substitution; Step 3.2's expected-exit-0 verification catches missed substitution immediately, but the literal-placeholder leak is a sharp edge — workers must derive the projection in Task 1.4 BEFORE running Step 3.2.
- Self-Review now has 4 items labeled `(review-cycle 4)` — visible audit trail of what each cycle added beyond the original plan structure; consistent with the cycle-3 pattern.
