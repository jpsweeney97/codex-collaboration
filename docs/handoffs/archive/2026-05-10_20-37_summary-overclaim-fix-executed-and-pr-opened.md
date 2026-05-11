---
date: 2026-05-10
time: "20:37"
created_at: "2026-05-10T20:37:17Z"
session_id: 3fdae7d9-85ab-4105-8b02-754aafda6b7c
resumed_from: docs/handoffs/archive/2026-05-10_02-01_summary-overclaim-fix-cycle-5-committed.md
project: claude-code-tool-dev
branch: chore/codex-collab-envelope-diagnostic-overclaim-fix
commit: d410fbe6
title: "Summary: overclaim-fix plan executed and PR #128 opened"
type: summary
files:
  - docs/diagnostics/2026-05-01-codex-app-server-server-request-envelope-probes.md
  - docs/diagnostics/codex-app-server-server-request-envelope-probes.json
  - docs/plans/2026-05-01-codex-app-server-client-platform-rebaseline-implementation-plan.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md
---

# Summary: overclaim-fix plan executed and PR #128 opened

## Goal

Execute the envelope-diagnostic overclaim-fix plan (Tasks 0-6) and land the docs-only correction that reconciles the May-1 diagnostic's interpretive claims with the parser's actual decision-shape-lossy behavior. This is the culmination of a multi-session arc: plan creation → 5 review cycles → 13 scrutiny follow-ups → approval → execution → PR.

The fix matters because the diagnostic is a load-bearing truth source for downstream work (rebaseline plan, architecture spec decisions, T-20260429-02 ticket narrowing). Leaving it overclaiming "supported" when the parser is decision-shape lossy under the observed `availableDecisions` would smuggle false response-shape compatibility into downstream artifacts.

## Session Narrative

Loaded the cycle-5 summary handoff. User provided a final scrutiny review (verdict: Defensible, no mandatory changes). Two optional improvements identified: (1) epistemic consistency for "parseable" → "inferred to be parseable" in Steps 2.5 and 3.3; (2) `compatibility_classification.status` semantic-change note documenting the shift from probe-pass/fail to classification label.

User chose "apply optionals then execute." Committed follow-up 13 at `3710d14e` (+6 −3, net +3 lines — the smallest cycle yet, confirming plan convergence).

Then executed Tasks 0-6 sequentially:
- Task 0: pre-edit snapshot (clean working tree)
- Task 1: full inventory and discovery (rg sweep, code reads, consumer check, projection derivation, register inspection, git proof for "landed on main")
- Task 2: patched 5 overclaim sites + 1 downstream qualifier in the diagnostic `.md`
- Task 3: in-place JSON correction (3 sites), with pre/post jq-projection diff and 8 canonical-value assertions all passing
- Task 4: register annotation (T-20260429-01 work-shape change from "implement" to "record closure evidence")
- Task 5: final verification sweep, cross-doc consistency, rebaseline-plan reconciliation
- Task 6: commit at `d410fbe6` (4 files, +35 −24)

No stop conditions fired. No contradictions found. All verification mechanisms passed on first attempt. User pushed and opened draft PR #128.

## Decisions

### Scrutiny verdict acceptance: apply optionals then execute

**Choice:** Apply both low-priority optional improvements before execution rather than executing as-is or committing scrutiny-only.

**Driver:** The improvements cost 3 net lines and strengthen internal consistency — the plan's own Step 2.4 used inferential language but Steps 2.5/3.3 didn't carry it through.

**Alternatives:** Execute as-is (would have been fine — both optionals are below-threshold); commit scrutiny as follow-up 13 only (defers execution to another session).

**Trade-off:** One extra commit on the branch (22 total instead of 21), but the plan is now epistemically consistent throughout.

### Register line references use actual line numbers from main (111-114, 32-55)

**Choice:** Used the actual line numbers verified via `git show main:runtime.py | rg -n` rather than the plan's approximate `107-118` references.

**Driver:** Step 1.5b's procedure explicitly says to record actual lines and propagate them. The carve-outs are at 111-114 on current `main`, not 107-118 as the plan approximated.

**Alternatives:** Use the plan's approximate references (would be slightly misleading); add "approximately" qualifier (unnecessary — we verified).

**Trade-off:** Minor divergence from plan template text, but more accurate.

## Changes

### `docs/diagnostics/2026-05-01-codex-app-server-server-request-envelope-probes.md`

Five overclaim sites patched from binary "supported/preserved" vocabulary to rebaseline vocabulary (parser-kind compatible, decision-shape lossy). One downstream qualifier added to "Remaining Blockers" section. Raw observation sections unchanged.

### `docs/diagnostics/codex-app-server-server-request-envelope-probes.json`

Three in-place corrections: `local_compatibility` value changed, `compatibility_classification` block rewritten with rebaseline key-set, `architecture_spec_readiness_delta` changed to `ready: false` with expanded `still_missing_items` and new `notes` array. Pre/post raw-evidence projection diff verified empty.

### `docs/plans/2026-05-01-codex-app-server-client-platform-rebaseline-implementation-plan.md`

Lines 216-219 evidence-check bullets updated to reflect new canonical vocabulary (`parser_kind_compatible_decision_shape_lossy` and `ready: false`).

### `docs/status/codex-collaboration-reconciliation-register.md`

T-20260429-01 row annotated: Phase 1 has landed on main, work shape changes from "implement" to "record closure evidence." Priority #1 and Exit condition cell both updated.

### `docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md`

Two self-review items added for scrutiny follow-up 13 (epistemic consistency + status-field semantics note).

## Codebase Knowledge

- **`_AVAILABLE_DECISIONS["command_approval"]`** at `approval_router.py:21-28` — the 6-tuple that the parser falls back to when `availableDecisions` contains non-string entries. This is the factual basis for the entire overclaim fix.
- **`_resolve_available_decisions`** at `approval_router.py:103-111` — the all-strings condition is `isinstance(wire_value, list) and all(isinstance(decision, str) for decision in wire_value)`. This is the exact code the diagnostic's corrected wording references.
- **Diagnostic JSON is 45,592 lines** — the `architecture_spec_readiness_delta` block is near the end (line 45580). The `compatibility_classification` is near the top (line 911). The raw-evidence `probes` array spans the bulk of the file.
- **Rebaseline plan's "Command Approval Decision-Shape Boundary"** at lines 905-925 — this is the authority source. It uses rebaseline vocabulary and names the exact wire shape. The diagnostic now mirrors this framing.
- **Register T-20260429-01 row** — the Phase 1 carve-outs are at `runtime.py:111-114` (readable-roots append) and `runtime.py:32-55` (gitdir resolver). Both verified on `main` at `1ed3f3fc`.

## Learnings

- **Plan convergence is measurable by cycle delta:** Cycle 1: +60 lines. Cycle 4: +190 lines (structural miss). Cycle 5: +8 lines. Follow-up 13: +3 lines. Execution: no plan changes needed. The plan was stable when it mattered.
- **Projection-diff technique works for raw-evidence preservation:** Extract only the fields that should be immutable before and after mutation, diff them. Empty diff = correctness. This is a lightweight form of property testing for document edits.
- **1,154-line plan executed without triggering a single stop condition.** The plan's verification machinery (8 assertions, projection diff, 6 anchor spot-checks, hunk review, sweep classification) all passed first-attempt. The machinery's value was proven during the 12 revision cycles, not during execution.

## Next Steps

1. **Merge PR #128** — squash-on-merge recommended. 22 commits collapse to one clean entry on `main`.
2. **T-20260429-01 closure evidence** — now the register's priority #1. Requires live App Server access for AC #1 (smoke), AC #2 (credential probe), AC #3 (test regression assertion).
3. **T-20260429-02 method matrix** — remains explicitly out of scope. Method-by-method classification of unsupported server-request methods is the next major work item after T-20260429-01 closure.
4. **Stale local branches** — at least 3 stale feature branches exist locally. Deletable.

## Project Arc

### Accomplishments (across sessions)

- T-20260423-02 Packet 1 (Deferred-Approval Response): MERGED 2026-04-28 (PR #126).
- Codex-collaboration drift cleanup (D-01 through D-09): COMPLETE 2026-04-30.
- Step 0 roadmap cleanup: MERGED 2026-04-30.
- Step 1 (T-20260416-01 reply extraction): CLOSED 2026-04-30.
- Step 2 (T-20260429-01 sandbox carve-outs): IMPLEMENTATION LANDED on `main` via PR #127.
- May-1 App Server rebaseline scope: 6 plans + 4 .md/4 .json diagnostics + 2 architecture notes on main.
- Public-skills-repo: PUBLISHED 2026-05-08 (https://github.com/jpsweeney97/claude-code-skills).
- **Envelope-diagnostic overclaim fix: EXECUTED and PR #128 opened (this session).**

### Current position

PR #128 is a draft awaiting merge. Once squash-merged, the diagnostic doc set is internally consistent with the rebaseline vocabulary and the actual parser behavior. The project's focus shifts to closure evidence for T-20260429-01 (live App Server access required).

### Load-bearing decisions still governing

- `TESTED_CODEX_VERSION = MINIMUM_CODEX_VERSION = "0.117.0"` until v128 branch decision packet lands.
- Preserve-and-add replaced by in-place correction (scrutiny follow-up 11).
- Edit-tool over jq transforms for large JSON edits (cycle 5).
- External consumers explicitly out of scope.
- Live-capture-wins precedence for hardcoded tuples (cycle 5).

### Drift risks

- "Roadmap Steps 2-6" framing in memory pre-dates the May-1 rebaseline scope expansion.
- Reconciliation register `Last reconciled` date is intentionally not bumped (row-local annotation only).
- AC #3 (test suite pass) remains unchecked — the plan acknowledges rather than verifies.
- T-20260429-01 and T-20260429-02 both need live App Server access; that bottleneck governs the next two milestones.
