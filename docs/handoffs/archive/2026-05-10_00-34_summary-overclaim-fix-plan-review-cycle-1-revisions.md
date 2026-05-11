---
date: 2026-05-10
time: "00:34"
created_at: "2026-05-10T04:34:00Z"
session_id: ef4420a6-48e1-46ac-83b3-5748ae3987ae
resumed_from: docs/handoffs/archive/2026-05-09_23-13_summary-codex-collab-orientation-and-overclaim-fix-plan.md
project: claude-code-tool-dev
branch: chore/codex-collab-envelope-diagnostic-overclaim-fix
commit: acda226a
title: "Summary: overclaim-fix plan review-cycle 1 revisions committed"
type: summary
files:
  - docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md
  - docs/diagnostics/2026-05-01-codex-app-server-server-request-envelope-probes.md
  - docs/diagnostics/codex-app-server-server-request-envelope-probes.json
  - docs/plans/2026-05-01-codex-app-server-server-request-envelope-probe-plan.md
  - docs/plans/2026-05-01-codex-app-server-client-platform-rebaseline-implementation-plan.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md
  - docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md
  - packages/plugins/codex-collaboration/server/approval_router.py
  - packages/plugins/codex-collaboration/server/runtime.py
---

# Summary: overclaim-fix plan review-cycle 1 revisions committed

## Goal

Resume yesterday's overclaim-fix plan work and apply review-driven revisions. The plan committed at `04a7fb43` (yesterday) reconciles the May-1 envelope-probe diagnostic with `approval_router.py:103-111` and the rebaseline plan — eliminating a docs-only contradiction. This session: receive a structured code review of that plan, evaluate findings with technical rigor (verify against codebase, not perform agreement), and apply approved dispositions as a single follow-up commit. The repaired plan still awaits re-approval before execution.

## Session Narrative

Loaded yesterday's summary. User pasted a structured "Reject" code review with 3 critical failures, 3 high-risk assumptions, real-world breakpoints, and patterns/root-causes analysis.

Invoked `superpowers:receiving-code-review`. Verified each finding against actual files: T-02 ticket lines 67-77+85,88, register row 67 cells, JSON lines ~895-913, `approval_router.py:20-28` for the fallback tuple, May-1 probe-plan lines 666-672 for vocabulary definition, runtime.py for the carve-outs.

All 6 findings verified out as valid. Wrote a per-finding evaluation with verification evidence:

- Critical 1 (T-02 sweep collision): real — even case-sensitive sweep hits T-02 lowercase line 85; case-insensitive would surface table rows 69-71 too.
- Critical 2 (register exit-condition stale): real — Task 4 only touched Current truth + priority line, not the Exit condition cell.
- Critical 3 (JSON supersession leaves stale data): real — `_superseded_by` is human-readable, not consumer-enforced.
- High-risk vocabulary succession: real — May-1 plan defined `supported` narrowly; the diagnostic was internally consistent against THAT vocabulary.
- High-risk fallback wording: real — `_AVAILABLE_DECISIONS["command_approval"]` includes BOTH `decline` AND `cancel`; "decline replaces cancel" framing was misleading. Lossiness is bidirectional.
- High-risk git proof: real — current Step 1.5 only reads files, doesn't prove `runtime.py:107-118` is reachable from `main`.

Also surfaced an additional finding the reviewer hadn't called out explicitly: case-sensitivity of the sweep itself was a bug — capital-S "Supported" wouldn't match without `-i`. Flagged it.

User accepted the evaluation and gave 6 specific dispositions: T-02 Option B (classification rule), case-insensitive sweeps, git proof via diff+show, fallback tuple enumeration, JSON patch-in-place default with consumer-discovery, exit-condition cell replacement.

Created task list (9 items). Worked through revisions in order: Authority Basis → Sweep Classification Rules → case-insensitive sweeps → fallback wording → JSON disposition flip → git proof → exit-condition replacement → Self-Review checklist. Made 23 Edit calls across the plan file. Each revision touched multiple sections to maintain cross-reference consistency.

Final consistency check via grep confirmed all 7 dispositions land: 8 rg sweeps with `-i`, Vocabulary Succession section present, `legacy-parser-route-vocabulary` referenced 16 times, git proof in 3 places (Step 1.5b + Files To Inspect + Self-Review), fallback tuple enumerated verbatim in 2 places (Step 2.2 + Step 3.2), patch-in-place default cited at 7 sites, new Step 4.4 for exit condition.

Committed at `acda226a` (217 insertions, 66 deletions; plan grew 613 → 763 lines). Working tree clean. Presented structured diff summary to user. Awaiting re-approval before plan execution.

## Decisions

### Plan revision strategy: follow-up commit vs amend

**Choice:** Apply revisions as a follow-up commit on top of `04a7fb43`, not amend.

**Driver:** User explicitly said "make one follow-up commit." Preserves plan-history audit trail (review-cycle 1 visible in git log). Revision is substantial (~25% growth) — amending would muddy the original-plan vs revision-cycle narrative.

**Alternatives:** Amend `04a7fb43` (loses the revision-cycle distinction; could destroy work if hook fails); rewrite plan from scratch (overkill, original structure was sound).

**Trade-offs:** Two plan-commits to merge through PR instead of one; trivial cost.

### T-20260429-02 sweep collision: Option B (classification rule)

**Choice:** Add `legacy-parser-route-vocabulary` classification with explicit bounding rules. Tag T-02 ticket parser-route table rows + May-1 probe-plan vocabulary definitions as legacy. Stop condition fires only when wording claims response-shape compatibility, lossless preservation, or ticket closability.

**Driver:** User chose Option B. Preserves sweep's overclaim-detection power without expanding T-02 method-by-method work into scope or narrowing the sweep glob (which would lose coverage for genuine overclaim sites).

**Alternatives:** Option A (bring T-02 lines into scope for patches — expands work and risks T-02-classification-creep); Option C (narrow sweep to exclude T-02 file — loses coverage of legitimate T-02 overclaims if any appear later).

**Trade-offs:** Adds a classification dimension the worker must learn, but documented exhaustively in new "Sweep Classification Rules" section with verified examples and bounding rules.

### JSON disposition default: patch-in-place when consumer status unclear

**Choice:** Flip the default. Patch-in-place is the new default when consumer-discovery surfaces no production consumer, when consumers don't honor `_superseded_by`, or when consumer status is unclear. Supersession-note reserved for documented machine consumers that honor the marker.

**Driver:** User-approved. Reviewer's argument was correct: `_superseded_by` is human-readable, not consumer-enforced; making it default-when-uncertain is backwards. Stale machine data is most dangerous when consumers are unknown.

**Alternatives:** Keep supersession-default with stronger framing; require explicit user-decision when unclear (more friction).

**Trade-offs:** Vocabulary expansion has its own risks (schema change might break unknown consumers), but bounded — patch-in-place adds explicit `parser_kind_compatible_methods` / `decision_shape_lossy_methods` siblings rather than mutating existing array semantics silently.

### Git proof folded into Step 1.5 vs new top-level step

**Choice:** Add Sub-step 1.5b inside the existing Step 1.5 rather than creating a new step.

**Driver:** Avoid renumbering churn (prior session caught issues with Tasks 2.3-2.5 renumbering). Git proof is logically a precondition for register-annotation correctness — natural fit inside Step 1.5 (register-annotation-need check).

**Alternatives:** New Step 1.6 / 1.3 (renumbering many cross-references); fold into Step 1.2 (parser semantics — different file, different purpose, conflation).

**Trade-offs:** Step 1.5 grows but stays focused (both sub-steps drive Task 4 disposition).

## Changes

### `docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md` (revised)

Plan revised from 613 to 763 lines (+150). Seven structural changes plus consistency fixes:

- New `### Vocabulary Succession` sub-section under Authority Basis. Frames the May-1 `supported` definition as a narrower vocabulary that the rebaseline supersedes with parser-kind / response-shape splitting.
- New `## Sweep Classification Rules` section (5-way classification table + bounding rules + verified examples). Adds `legacy-parser-route-vocabulary` classification.
- All 8 rg sweeps gained `-i` flag (Verification, Step 1.1, Step 1.4 jq pipe, new Step 1.4 consumer-discovery, Step 2.6, Step 3.5, Step 4.5, Step 5.1).
- Step 1.5 split into 1.5a (register inspection) and 1.5b (git proof via `git diff main..HEAD` + `git show main:`).
- Step 2.2 bullet 4 + Step 3.2 item 1 fallback wording rewritten with verbatim tuple enumeration; bidirectional lossiness framing.
- Step 1.4 expanded with consumer-discovery sub-step + flipped disposition default.
- New Step 4.4 replaces T-20260429-01 row's Exit condition cell; old 4.4/4.5 renumbered to 4.5/4.6. Step 4.5 sweep pattern extended to include `Land the Phase 1`.
- Files To Inspect table gained context-only rows (T-02 ticket, May-1 probe-plan vocabulary) and a runtime.py row keyed to `main`.
- Self-Review checklist gained 6 new items.
- Task 6.2 commit message body updated for new fallback framing and exit-condition replacement.

Committed at `acda226a` on `chore/codex-collab-envelope-diagnostic-overclaim-fix`.

## Codebase Knowledge

- **`packages/plugins/codex-collaboration/server/approval_router.py:20-28`**: `_AVAILABLE_DECISIONS["command_approval"]` is a 6-tuple — `("accept", "acceptForSession", "acceptWithExecpolicyAmendment", "applyNetworkPolicyAmendment", "decline", "cancel")`. Critical for the diagnostic correction: includes BOTH `decline` AND `cancel`. The "decline replaces cancel" framing in the original plan was wrong; lossiness is payload loss for `acceptWithExecpolicyAmendment` plus spurious additions of `acceptForSession`, `applyNetworkPolicyAmendment`, and `decline`.
- **`packages/plugins/codex-collaboration/server/approval_router.py:103-111`**: `_resolve_available_decisions` keeps wire `availableDecisions` only when `isinstance(wire_value, list) and all(isinstance(decision, str) for decision in wire_value)`. Mixed lists (string + dict) trigger fallback.
- **`packages/plugins/codex-collaboration/server/runtime.py:107-118` on `main`**: Phase 1 sandbox carve-outs (`~/.codex/memories`, `~/.codex/plugins/cache`, `~/.agents/skills`, `~/.agents/plugins`, dynamic gitdir resolution). Two-layer defense on gitdir merged at PR #127.
- **`docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md:67-77`**: T-02 ticket's parser-route classification table — three "Supported as `<kind>`" / "Supported (parked)" rows. This vocabulary is the May-1 narrower `supported` definition (route + correlation fields). NOT an overclaim against the rebaseline; classifies as `legacy-parser-route-vocabulary`.
- **`docs/plans/2026-05-01-codex-app-server-server-request-envelope-probe-plan.md:666-672`**: Original probe-plan vocabulary definitions — `supported` / `unsupported` / `unknown` / `unparseable` (4-state). The diagnostic was internally consistent against this vocabulary; the rebaseline introduces a stricter parser-kind / response-shape splitting.
- **ripgrep default is case-sensitive.** Without `-i` or smart-case config, `rg "supported"` does NOT match `Supported`. Plan's pre-existing sweep would have missed capital-S overclaims; switched to `-i` throughout.
- **JSON consumer status of `docs/diagnostics/codex-app-server-server-request-envelope-probes.json` is unverified.** Likely a one-shot human-review artifact (lives in `docs/diagnostics/`), but plan now requires explicit consumer-discovery via `rg --type-not md` before choosing disposition.

## Learnings

- **Verify-before-acknowledge pays off in code-review reception.** Reviewer's verdict was "Reject" but my verification showed every finding was correct on substance and didn't kill the plan. Functionally an "approve subject to substantive edits." Treating the verdict literally would have meant rewriting from scratch; treating findings as input meant a clean follow-up commit.
- **Single-signal trap repeats.** Yesterday's session was burned by `git branch --contains` ambiguity (`* main` line). Today's plan had a different single-signal trap: reading `runtime.py:107-118` on the *current branch* and assuming it equals `main`'s state. Plan now requires `git diff main..HEAD -- runtime.py` (empty) AND `git show main:runtime.py | sed -n '107,118p'` (carve-outs visible). Two independent checks for one claim.
- **Vocabulary-succession framing prevents retroactive blame.** The May-1 diagnostic was internally consistent against its own vocabulary. The rebaseline introduces a stricter classification. Framing this as "vocabulary succession" rather than "diagnostic was wrong" preserves epistemic accuracy and makes future readers see clean reclassification rather than guessing about old-Claude's mistakes.
- **Classification rules with bounded examples beat stop-condition examples.** Original plan tried to handle T-02 collision via "stop if X" examples in Stop Conditions. Better solution: dedicated `## Sweep Classification Rules` section with a 5-way table, explicit bounding rules between adjacent classifications, and verified examples. Stop conditions stay terminal; classification stays decisional.

## Next Steps

1. **Re-approval gate.** User reviews `acda226a` diff for execution-credibility. If approved, plan executes Tasks 1-6. If further revisions needed, another review-cycle commit on the same branch.
2. **Execute Tasks 1-6** of the revised plan. Six tasks; expected single commit at end of Task 6 covering diagnostic .md + JSON (conditional) + register (conditional). No code changes.
3. **PR back to main** when Task 6 commit lands. Three commits to merge: `04a7fb43` (original plan), `acda226a` (review-cycle 1 revisions), plus the future Task 6 execution commit.
4. **Then T-20260429-01 closure** — comparable `/delegate` smoke (AC #1), credential-boundary probe (AC #2), regression assertion update + suite pass (AC #3). Needs live App Server access.
5. **Then T-20260429-02 method matrix** — capability artifact + method-by-method classification + lossless parser/response branch implementation. Larger scope.
6. **Memory update candidate**: replace "NEXT: Roadmap Steps 2-6" with the corrected post-orientation framing once the plan executes and lands.

## Project Arc

### Accomplishments (across sessions)

- T-20260423-02 Packet 1 (Deferred-Approval Response): MERGED 2026-04-28 (PR #126).
- Codex-collaboration drift cleanup (D-01 through D-09): COMPLETE 2026-04-30.
- Step 0 roadmap cleanup: MERGED 2026-04-30.
- Step 1 (T-20260416-01 reply extraction): CLOSED 2026-04-30.
- Step 2 (T-20260429-01 sandbox carve-outs Options B + E + ~/.agents/): IMPLEMENTATION LANDED on `main` via PR #127, including two-layer gitdir defense after security review. Closure evidence outstanding.
- May-1 App Server rebaseline scope: 6 plans + 4 .md/4 .json diagnostics + 2 architecture notes committed on main. Capability matrix + method-classification artifacts NOT YET created.
- Public-skills-repo (separate workstream): PUBLISHED 2026-05-08 at https://github.com/jpsweeney97/claude-code-skills (22 skills, v0.1.0).
- 2026-05-09 session: orientation correction + approval-gated overclaim-fix plan committed at `04a7fb43`.
- This session (2026-05-10): review-cycle 1 revisions of the overclaim-fix plan committed at `acda226a`. Plan grew from 613 to 763 lines covering 7 substantive review findings.

### Current position

Branch: `chore/codex-collab-envelope-diagnostic-overclaim-fix` at `acda226a`. Plan twice-touched (initial + review-cycle 1), awaiting re-approval before execution. `main` still at `1ed3f3fc` for the latest codex-collab post-implementation state. Three feature worktrees clean but stale. Reconciliation register at `docs/status/codex-collaboration-reconciliation-register.md` still stale (last reconciled 2026-04-30).

### Load-bearing decisions still governing the work

- Don't raise version pins until v128 branch decision packet lands (`TESTED_CODEX_VERSION = MINIMUM_CODEX_VERSION = "0.117.0"`).
- Plan-first, approval-gated, **docs-only** for the contradiction fix. Implementation work (parser fix, response branch) deferred to T-20260429-02.
- **Patch-in-place** preferred for JSON disposition when consumer status is unclear (FLIPPED from prior supersession-note default).
- Sandbox `~/.codex/` carve-outs are subdirectory-scoped only; credential paths (`auth.json`, `config.toml`, `history.jsonl`, `sessions/`) remain blocked.
- T-20260429-02 method-by-method classification work is OUT of this plan's scope. T-02 ticket parser-route vocabulary is `legacy-parser-route-vocabulary` and not patched.

### Drift risks

- "Roadmap Steps 2-6" framing in memory pre-dates the May-1 rebaseline scope expansion. Update once overclaim-fix plan executes.
- Three stale feature branches (`...-exploration`, `...-rebaseline`, `unrelated-change`) still exist locally. Deletable.
- Reconciliation register still ranks "Implement T-20260429-01 Phase 1" as priority #1 — addressed by the plan's Task 4 when it executes.
- AC #3 (test suite pass) is unchecked; plan acknowledges rather than verifies.
- The committed envelope-probe diagnostic remains contradictory with the rebaseline plan and code reality on `main` until the plan executes.

### Downstream impacts of this session

- Memory "NEXT: Roadmap Steps 2-6" framing remains stale. Defer until plan executes.
- Reconciliation register update deferred to plan execution (Task 4).
- Plan branch `chore/codex-collab-...-overclaim-fix` now has TWO commits to merge (original + revision); future Task 6 execution adds a third.
- The new `legacy-parser-route-vocabulary` classification + bounding rules are codified in this plan only. If the same parser-route legacy vocabulary appears in other contradiction-fix plans later, that pattern is now reusable.
