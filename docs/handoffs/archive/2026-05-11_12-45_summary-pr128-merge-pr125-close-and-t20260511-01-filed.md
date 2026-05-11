---
date: 2026-05-11
time: "12:45"
created_at: "2026-05-11T12:45:24Z"
session_id: 247a955e-a16b-491d-b2df-8ee868d981b5
resumed_from: docs/handoffs/archive/2026-05-10_20-37_summary-overclaim-fix-executed-and-pr-opened.md
project: claude-code-tool-dev
branch: main
commit: ecf6d6b3
title: "Summary: PR #128 merge, PR #125 closure, and T-20260511-01 filed"
type: summary
files:
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/tickets/2026-05-11-codex-collaboration-needs-escalation-discard-recovery.md
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/pending_request_store.py
  - packages/plugins/codex-collaboration/server/approval_router.py
  - packages/plugins/codex-collaboration/tests/test_finalize_turn_terminal_guard.py
---

# Summary: PR #128 merge, PR #125 closure, and T-20260511-01 filed

## Goal

Resume from prior handoff (PR #128 envelope-diagnostic overclaim fix in draft awaiting merge), audit MEMORY.md for drift, merge PR #128, then disposition the stale PR #125 (delegate hardening, opened 2026-04-23, 18 days unreviewed). Capture any residual operational value from PR #125 as a Packet-1-compatible follow-up rather than discard it silently. The codex-collaboration register's priority #1 (T-20260429-01 closure evidence) is downstream — landing PR #128 reconciles the vocabulary T-20260429-01 closure framing depends on.

## Session Narrative

Loaded summary handoff. First audited MEMORY.md for drift against current `main` — found 8 drift items across three tiers: one Tier 1 (load-bearing "Step 2 = T-20260429-01 Phase 1 implementation pending", but Phase 1 had already landed via PR #127 on 2026-05-01); five Tier 2 (missing context: May-1 rebaseline scope expansion, PR #128, PR #125, Page Turner extension, handoff `summary` skill); three Tier 3 (cosmetic: duplicate Writing-principles row, understated stale-branch count). Applied three-patch remediation: NEXT-line rewrite, items 6/7 add with new "In progress:" subsection, duplicate-row removal.

Pivoted to PR #128 review via the `implementation-review` skill. The PR had been through 13 scrutiny cycles on its plan text; the adversarial-verification cut against the actual cited resource caught a register cite error — `runtime.py:32-55` for the dynamic gitdir resolver should have been `27-72` (the full `_resolve_worktree_gitdir` function span, including the round-trip back-pointer security check at L62-72). Landed the one-line fix as commit `8561bc90` on the branch pre-merge, then squash-merged PR #128 at `d896b72e`. Updated memory to reflect.

Pivoted to PR #125 disposition. Initial scope-by-scope analysis showed full architectural supersession across all three areas (sandbox roots via #127, state machine via #126, command-approval boundary via #126's `_PLUGIN_DECISIONS`). User pushed for a spot-check of the empty-`available_decisions` scenario before closing. The spot-check inverted the conclusion: PR #125's Option B (auto-finalize empty `available_decisions` → `failed`) is architecturally incompatible with Packet 1's "trust terminal-status invariant" design, but Option A (widen `discard()` to admit `needs_escalation + None`) retains standalone defense-in-depth value — Packet 1's `_finalize_turn` Step 5b fall-through still produces `(needs_escalation, None)` for cancel-capable kinds under the anomalous-pending path, and the discard gate on `main` does not admit that state. User requested deeper investigation; mapped all 8 known worker-thread failure modes against the reachability of the stuck-state outcome. Confirmed only "defective terminal-status-write" + race scenarios produce it — low probability but high recovery cost (no operational recovery path).

Drafted ticket T-20260511-01 on a chore branch, opened PR #129 for review, then closed PR #125 with detailed scope-by-scope rationale referencing #129. Captured the supersession taxonomy (architectural / behavioral / partial) as a new feedback memory. Reviewed PR #129 (verified 5 technical claims against `main` code), squash-merged at `ecf6d6b3`. MEMORY.md was updated four times across the session — once for initial drift, then after each PR action.

## Decisions

### Apply cite-fix to PR #128 pre-merge rather than file as follow-up

**Choice:** Land the one-line register correction (`8561bc90`) on the branch and let the squash absorb it into `d896b72e`. **Driver:** The PR's whole purpose was accurate provenance; leaving the wrong cite in the merge commit would have been self-contradicting. **Alternatives:** File follow-up ticket and merge as-is (defensible — squash absorbs addendum anyway); investigate whether other line citations might also be wrong (overkill for one-cite scope). **Trade-off:** 23 commits squashed instead of 22; gain coherence between PR purpose and merge commit content.

### Spot-check PR #125 scenario before closing as fully superseded

**Choice:** Investigate the empty-`available_decisions` flow through Packet 1's `_finalize_turn` before pulling the close trigger. **Driver:** User explicitly requested it after the initial close recommendation; recognized that "superseded" hides three different supersession modes. **Alternatives:** Close with original "fully superseded" framing (would have misclassified Option A as architecturally superseded); accept the live-smoke evidence as sufficient (would not have captured the defense-in-depth gap). **Trade-off:** Longer investigation but caught partial supersession that close-comment would have erased.

### File T-20260511-01 as new PR rather than commit directly to main

**Choice:** Open small PR #129 with the ticket file. **Driver:** User said "draft" (not "merge"); PR creates a review surface; consistent with project's PR-flow pattern even for tiny docs additions. **Alternatives:** Commit on chore branch and reference path in close-comment without PR; use `merge-branch` skill for local fast-path. **Trade-off:** 2-PR juggle (close #125 + open #129) more visible than single atomic operation; small overhead acceptable for review traceability.

### Capture supersession taxonomy as feedback memory

**Choice:** Write `feedback_pr_disposition_supersession_taxonomy.md` and index in `MEMORY.md`. **Driver:** Session surfaced a reusable framework (architectural / behavioral / partial supersession + extract-residual-value discipline) that future sessions will encounter. **Alternatives:** Leave the learning in the closed-PR comment and ticket prose (would not surface in future sessions); commit a doc to `docs/learnings/` (would not auto-load). **Trade-off:** Adds one line to the always-loaded MEMORY.md index; high leverage given the recurring nature of stale-PR disposition.

## Changes

### `~/.claude/projects/.../memory/MEMORY.md`

Four editing passes. (1) Drift remediation: rewrote NEXT line, added items 6 (T-20260429-01 Phase 1 LANDED) + new "In progress:" subsection for PR #128, removed Writing-principles duplicate. (2) Post-PR-#128-merge: moved PR #128 to item 7 MERGED, corrected gitdir cite to 27-72 in item 6, removed "In progress:" subsection, updated NEXT. (3) Post-PR-#125-close: added item 8 with full architectural-vs-behavioral rationale, indexed feedback memory. (4) Post-PR-#129-merge: updated NEXT to promote T-20260511-01 implementation as small near-term task.

### `~/.claude/projects/.../memory/feedback_pr_disposition_supersession_taxonomy.md` (NEW)

Feedback memory capturing the 3-mode supersession taxonomy (architectural / behavioral / partial) plus the failure-mode-matrix verification discipline. PR #125 precedent included.

### `docs/status/codex-collaboration-reconciliation-register.md` (one-line edit)

Fixed `runtime.py:32-55` cite to `27-72` to reflect the full `_resolve_worktree_gitdir` function span (signature L27 → body end L72, including the L62-72 back-pointer security check). Committed as `8561bc90`, squashed into PR #128's `d896b72e`.

### `docs/tickets/2026-05-11-codex-collaboration-needs-escalation-discard-recovery.md` (NEW)

T-20260511-01 ticket file (112 lines). Captures PR #125's Option A (widen `discard()` admission to `needs_escalation + None`) as a Packet-1-compatible follow-up. Includes failure-mode matrix, AC1-AC4, explicit out-of-scope. Landed via PR #129 squash at `ecf6d6b3`.

## Codebase Knowledge

- **`_finalize_turn` at `delegation_controller.py:2431-2570`**: 5-step Captured-Request Terminal Guard. Step 3 logs "anomalous pending" warning + defensively writes `resolved` to the store when snapshot.status is `pending`, BUT the local snapshot variable retains the old `pending` value. Step 4's resolved/canceled branches don't match → Step 5b fires → `needs_escalation` for cancel-capable kinds.

- **Discard gate at `delegation_controller.py`** (`def discard`): admits `(failed, unknown, canceled) + None` and `(promotion_state in pending/prechecks_failed)`. Explicitly does NOT admit `needs_escalation`. The Packet-1-compatible defense-in-depth gap T-20260511-01 captures.

- **`_PLUGIN_DECISIONS = ("approve", "deny")` at `delegation_controller.py:1788`**: operator view always returns these two regardless of wire-level `availableDecisions`. Broader than PR #125's described `_DENY_ONLY_DECISIONS` (which was deny-only for cancel-capable kinds only). Operator always has decisions to make — the empty-`available_decisions` trigger is unreachable under Packet 1.

- **`record_timeout` in `pending_request_store.py`**: atomic single-`_append` write of `status: "canceled"` for all 4 timeout sub-branches. This is the guarantee that makes Packet 1's operator-no-show handling clean.

- **`_mark_execution_unknown_and_cleanup`** (around `delegation_controller.py:1430`): marks JOB as `unknown` but does NOT touch `pending_request_store`. Generic worker exceptions leave the job discardable (`unknown + None`) but the request-store record stale-but-irrelevant.

- **`test_finalize_turn_terminal_guard.py:599`** (`test_l9_anomalous_pending_warning`): explicitly tests the anomalous-pending path. Packet 1 authors knew about it and chose log+recover — a deliberate architectural decision, not an oversight. Lines 387, 501 cover related fall-through scenarios.

- **`_resolve_worktree_gitdir` at `runtime.py:27-72`** (full function span): signature L27 → body L72. L62-72 is the round-trip back-pointer security check — the "structural validation" the register cite is supposed to ground. PR #128's pre-merge fix `8561bc90` corrected this.

- **`_resolve_available_decisions` at `approval_router.py:103-111`**: empty wire `availableDecisions: []` returns empty tuple (vacuous all-strings check). Fallback to `_AVAILABLE_DECISIONS[kind]` only fires for non-list or non-string elements. This is the parser-kind-compatible-decision-shape-lossy behavior the May-1 diagnostic now documents (post PR #128).

## Learnings

- **Architectural vs behavioral supersession is load-bearing in stale-PR disposition.** "Superseded" is a single word that hides three different modes. Always run the failure-mode matrix before closing — partial supersessions are easy to misclassify as full.

- **Spot-checks against actual cited resources catch what plan-internal scrutiny misses.** PR #128 went through 13 review cycles examining the plan's internal consistency. The cite error (`32-55` vs `27-72`) was invisible to that style of scrutiny; only checking the cite against `runtime.py` on `main` surfaced it.

- **Memory drift compounds quickly.** 11 days produced 47 commits + 4 PRs of state changes invisible to `MEMORY.md`. The compounding asymmetry: drift audits are cheap; the cost of stale guidance misleading a future session is invisible until it fires.

- **Packet 1's "invariantize architecture, defensively log violation" pattern.** Anomalous fall-through isn't auto-recovered — it logs a warning, defensively updates the store, then lets the kind-based fall-through produce `needs_escalation`. The architectural intent: defects should be VISIBLE, not silently recovered. T-20260511-01 honors this by adding operational recovery (`discard` widening) without changing finalize semantics.

- **Two-PR shape for partial supersession.** Close-comment and follow-up-ticket are separate artifacts with separate review surfaces. Don't fold them.

## Next Steps

1. **T-20260511-01 implementation** — ~3-line discard-gate widen + unit test + `promotion-protocol.md` contract update. Small, well-scoped, ready to pick up. Ticket at `docs/tickets/2026-05-11-codex-collaboration-needs-escalation-discard-recovery.md`.

2. **T-20260429-01 closure evidence** (register priority #1) — Phase 1 implementation landed via PR #127; AC #1/#2/#3 closure requires live App Server access (smoke run, credential probe, test suite pass).

3. **T-20260429-02 method matrix** — Out-of-scope until T-20260429-01 closes. Classifies unsupported `ServerRequest` methods by reachability.

4. **Architecture doc deferred wording reconciliation** — `docs/architecture/2026-05-01-codex-app-server-current-client-platform-rebaseline.md:159` still uses stale "supported" wording per PR #128 plan's explicit deferral. Small follow-up.

5. **Page Turner browser extension** — Specs+plan on `main` (2026-05-05/06); implementation not yet scheduled.

6. **Stale local branches hygiene** — ~10 local, several `[gone]`. Pruning candidates.

## Project Arc

### Accomplishments (across sessions)

- T-20260423-02 Packet 1 (Deferred-Approval Response): MERGED 2026-04-28 (PR #126).
- Codex-collaboration drift cleanup (D-01 through D-09): COMPLETE 2026-04-30.
- Step 0 roadmap cleanup: MERGED 2026-04-30.
- Step 1 (T-20260416-01 reply extraction): CLOSED 2026-04-30.
- Step 2 (T-20260429-01 Phase 1 sandbox carve-outs): LANDED 2026-05-01 via PR #127.
- May-1 App Server rebaseline scope: 6 plans + 4 .md/4 .json diagnostics + 2 architecture notes on `main`.
- Public-skills-repo: PUBLISHED 2026-05-08.
- **Envelope-diagnostic overclaim fix: MERGED 2026-05-11 (PR #128, this session).**
- **PR #125 (delegate hardening) disposition: CLOSED 2026-05-11 (this session).**
- **T-20260511-01 (Option A discard widening) filed: PR #129 MERGED 2026-05-11 (this session).**

### Current position

All May-1 docs reconciliation complete and on `main` at `ecf6d6b3`. No open PRs. Register's priority #1 (T-20260429-01 closure evidence) is unblocked from a documentation standpoint but still blocked operationally on live App Server access. T-20260511-01 is a small, ready-to-implement defense-in-depth task. MEMORY.md is drift-free. Working directory clean.

### Load-bearing decisions still governing

- `TESTED_CODEX_VERSION = MINIMUM_CODEX_VERSION = "0.117.0"` until v128 branch decision packet lands.
- Edit-tool over jq for large JSON edits (cycle-5 precedent).
- Live-capture-wins precedence for hardcoded tuples (cycle-5 precedent).
- Packet 1's "invariantize architecture, defensively log violations" pattern (T-20260511-01 honors).
- Architectural-vs-behavioral supersession taxonomy (new this session, indexed in MEMORY.md feedback).

### Drift risks

- Reconciliation register `Last reconciled: 2026-04-30` is intentionally not bumped (row-local annotations only).
- Architecture doc's stale "supported" wording is a deliberate scope-defer; follow-up not yet ticketed.
- The PR #125 architectural-vs-behavioral analysis lives in the closed-PR comment, T-20260511-01 ticket, and feedback memory — three places that could drift independently if Packet 1 changes shape.
- T-20260429-01 still names "Options B + E" in some prose; actual landed scope is "Options B + E + ~/.agents/ + dynamic gitdir."

### Downstream impacts of this session

- PR #128 reconciles diagnostic vocabulary across `docs/diagnostics/`, `docs/plans/2026-05-01-*`, and the register; T-20260429-01 closure framing now grounded in rebaseline vocabulary.
- PR #129 introduces T-20260511-01 as the next-up small ticket in the codex-collaboration backlog.
- Supersession-taxonomy feedback memory will influence future PR disposition decisions across the project.
- Implementation-review's adversarial-against-cited-resource pattern is now a known cut; future doc reconciliation work should run it pre-merge.
