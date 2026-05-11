---
date: 2026-04-26
time: "23:36"
created_at: "2026-04-27T03:36:28Z"
session_id: 6627ed41-15d5-4809-a93d-eabfa54fc012
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-26_18-30_phase-g-task-18-closes-1plus1plus1-chain-with-round-7.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: 844e6f97
title: "Task 19 convergence map Round 4 and context-metrics opus-4-7 fix"
type: handoff
files:
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-19-convergence-map.md
  - packages/plugins/context-metrics/scripts/config.py
  - packages/plugins/context-metrics/README.md
  - packages/plugins/context-metrics/tests/test_config.py
  - packages/plugins/context-metrics/CHANGELOG.md
---

# Task 19 convergence map Round 4 and context-metrics opus-4-7 fix

## Goal

**Bigger picture:** Phase H of T-20260423-02 Packet 1 (Deferred-Approval Response). Phase G CLOSED at HEAD `844e6f97` with Task 18's 1+1+1 chain landed. Task 19 opens Phase H — the `_finalize_turn` Captured-Request Terminal Guard rewrite per spec §1738-1827. This session authored the Task 19 convergence map through 4 rounds of adversarial review, bringing it from first-draft to near-dispatch-ready.

**Stakes:** The convergence map is the binding authority document for Task 19's implementer dispatch. Defects in the map propagate directly to implementation — as demonstrated by Rounds 2-4 catching 5+3+3 defects respectively.

**Trigger:** User loaded prior handoff (Phase G Task 18 CLOSES) and provided their own independent orientation read of the live codebase, identifying the Task 19 kernel and proposing an initial lock structure. Session then iterated through drafting and adversarial review.

**Secondary deliverable:** Fixed a bug in the `context-metrics` plugin where `claude-opus-4-7` was missing from the `MODEL_WINDOWS` prefix table (`config.py:19-22`), causing incorrect 200k context window reporting until the auto-upgrade fallback triggered at >200k occupancy.

**Project arc context:** Task 19 is first of 4 Phase H tasks (19=finalizer guard, 20=poll projection, 21=discard canceled, 22=contracts). After Task 19 dispatches and lands, Phase H close enters scope.

## Session Narrative

**Step 1 — Load prior handoff (HEAD `844e6f97`).** Loaded `2026-04-26_18-30_phase-g-task-18-closes-1plus1plus1-chain-with-round-7.md`. Established that Phase G CLOSED, Task 19 was next in queue, and the carry-forward set was fully prepared (F16.1 2 tests, G18.1 6 tests, RT.1, TT.1, F16.2 lineage marker).

**Step 2 — User delivered independent orientation read.** Via `/copy`, the user shared a detailed orientation analysis identifying: the Task 19 kernel (one-snapshot terminal guard, not "make 6 skipped tests pass"), live anchors for `_finalize_turn` at `:2340` (not the stale `:1439-1533` from Phase H plan body), the D4 unconditional write defect at `:2368`, the G18.1 and F16.1 test line numbers, and a proposed 10-lock structure with specific challenge points.

**Step 3 — Independent convergence-map orientation.** Verified all user-claimed live anchors against HEAD via grep. All confirmed: `_finalize_turn` at `:2340`, `DelegationEscalation(` count=2 at `:833, :2416`, D4 at `:2369-2371`, G18.1 decorators at the listed lines, F16.1 at `:161, :179`. Read spec §1738-1827 verbatim to ground L3's mapping table. Reported alignment on 4 points and divergence/refinement on 3: L2's parse-failed composition, L3's `resolved+failed→unknown` row, and W2's inversion precedent.

**Step 4 — User endorsed alignment + proposed convergence map structure.** Via `/copy`, user endorsed the three refinements and proposed a concrete convergence-map structure with 10 sections. Also adjudicated poll/discard scope: keep Task 19 narrow to `_finalize_turn` only; classify poll/discard as Phase H follow-on tasks (Task 20/21). User authored the L2 shape, the L3 dispatch-clarity split (4-concept rows into 5 presentation rows), the W2 inversion language, and the stale-plan-anchors authority downgrade.

**Step 5 — Round 1 draft (388 lines).** Authored `task-19-convergence-map.md` with 14 sections: scope, authority order, live anchors, L1-L10, W1-W12, branch matrix, per-test triage, acceptance criteria, pre-dispatch checklist, commit shape, carry-forward expectations, pre-dispatch warnings, restructure record. Spec `:1738-1827` read verbatim before locks. `pending_request_store.get` confirmed returns `PendingServerRequest | None` at `pending_request_store.py:40`.

**Step 6 — Round 2 adversarial review via `/copy`.** User shared detailed review identifying 5 Critical defects: (C1) G18.1 line→test mapping wrong — carry-forward.md labels were stale; live code showed `:1525` is `test_start_post_turn_finalization_failure_marks_job_unknown_and_cleans_up`, not the approve test; (C2) Parse-failed model factually false — L1 claimed "no store record" but `delegation_controller.py:947-961` creates minimal `PendingServerRequest` and writes to store; (C3) L4 ordering block self-contradictory — "D4 before snapshot" is impossible since D4 is snapshot-conditional; (C4) Direct finalizer tests were only "recommended" (too weak); (C5) F16.1 tests have `pass` bodies — decorator removal is vacuous closure. Plus 3 high-risk under-specifications: lineage for `unknown`, anomalous-pending warning, "exactly one get" imprecision.

**Step 7 — Round 2 corrections (388→499 lines).** Verified all 5 Criticals against live code. All confirmed. Applied targeted edits: G18.1 table corrected with live-grepped test names; L1 rewritten per `delegation_controller.py:947-961`; L2 expanded to four-row table with three-way warning split; L4 ordering rewritten as 7-step sequence; L9 restructured for cross-cutting only; L11 added as binding lock with 7 specific test obligations (L11-T1 through L11-T7); L8 split into L8.1 (no-pass-body audit) + L8.2 (binding body assertions); L6.1 added with explicit lineage adjudication.

**Step 8 — Round 3 adversarial review via `/copy`.** User identified 3 more defects: (C1) Deny terminal expectations — L7 asserts `job.status == "failed"` for deny tests, but L3's own table maps `resolved + completed → completed`, never `failed`; deny→decline doesn't abort the turn per spec `:1677, :1684, :1686`. (C2) Branch Matrix and Pre-Dispatch Warnings still said "Snapshot read SKIPPED" for parse-failed paths despite L1's correction. (C3) Commit shape said "recommended direct-derivation tests" despite L11 being binding.

**Step 9 — Round 3 corrections (499→526 lines).** Read spec §Response payload mapping (`design.md:1663-1701`) to ground the deny adjudication. Confirmed: `deny → decline` is per-action, not per-turn; App Server processes decline and continues; turn completes normally; item carries `status: "declined"`. All deny assertions corrected from `failed` to `completed`. Test name `test_decide_deny_marks_job_failed_and_closes_runtime` rename pre-authorized to `..._completed_...`. Branch Matrix and Pre-Dispatch Warnings corrected for parse-failed paths. Commit shape language updated.

**Step 10 — Round 4 adversarial review via `/copy`.** User identified 3 more defects: (C1) L11-T7 specified impossible scenario — snapshot=`resolved` + `final_status="needs_escalation"` contradicts L3 (resolved maps to completed/unknown, never needs_escalation). (H1) Rename policy contradicted itself (authorized at `:54, :232, :477` but "no rename anticipated" at `:59`). (H2) F16.1 "at least once" too weak — permits double-finalization regressions. (H3) L6.1 "we DO know" overstated for `resolved+failed→unknown`.

**Step 11 — Round 4 corrections.** L11-T7 split into T7a (terminal-snapshot single-read) and T7b (pending fall-through with mid-flight store mutation). Rename policy single-sourced. F16.1 invocation assertion replaced with side-effect uniqueness (one terminal outcome + one job transition + one release + one close + one lineage update). L6.1 wording corrected.

**Step 12 — Context metrics discovery.** Noticed `UserPromptSubmit` hook was reporting context at 198k/200k (99%) while system prompt says Opus 4.7 (1M context). Investigated: `packages/plugins/context-metrics/scripts/config.py:19-22` only has `claude-opus-4-6` and `claude-sonnet-4-6` in `MODEL_WINDOWS`. `claude-opus-4-7` prefix doesn't match `claude-opus-4-6` (trailing `-6` breaks it). The `maybe_upgrade_window` fallback only triggers once observed occupancy exceeds 200k.

**Step 13 — Context metrics fix.** Added `"claude-opus-4-7": 1_000_000` to `MODEL_WINDOWS`. Updated README model table, added `test_opus_4_7_detects_1m` test case, updated CHANGELOG. Full suite: 97/97 pass.

**Step 14 — Clean branch separation (Path 1).** Stashed untracked convergence map → checkout main → create `chore/context-metrics-opus-4-7` → commit `727898c4` with context-metrics fix → return to feature branch → pop stash. Both branches verified clean.

**Step 15 — User pauses for own review.** User will review the Round-4 convergence map independently and share feedback at the start of the next session. Handoff saved.

## Decisions

### Decision: Task 19 scope limited to `_finalize_turn` only (not poll/discard/contracts)

- **Driver:** User authored the scope split: "I would not bundle poll() and discard() into Task 19." Phase H plan clearly separates Task 19 (finalizer guard), Task 20 (poll), Task 21 (discard), Task 22 (contracts). G18.1 tests' bounded `controller.poll(job_id)` use is observation-only, not Task-20-level projection-catch behavior.
- **Rejected: Bundle poll/discard into Task 19.** Would expand scope beyond the finalizer guard; loses governance discipline that made Task 18 close cleanly.
- **Implication:** Task 19 convergence map explicitly classifies poll/discard as L10 out-of-scope boundaries. If a Task 19 unskip exposes a poll-projection dependency, it's BLOCKED — not unilateral scope expansion.
- **Trade-offs:** May require additional dispatch round if a test surfaces a dependency.
- **Confidence:** High (E2) — user authored the disposition with concrete spec citations.
- **Reversibility:** High — scope can be expanded via convergence map addendum.
- **Change trigger:** A Task 19 unskip that cannot pass without Task 20/21 changes.

### Decision: Deny terminal status is `completed`, not `failed`

- **Driver:** Spec `:1677, :1684, :1686` — `deny → decline` does NOT abort the turn. App Server processes decline and continues; turn completes normally; `item/completed` carries `status: "declined"` (item-level). L3's mapping table: `resolved + completed → completed`. The pre-Packet-1 test name `test_decide_deny_marks_job_failed_and_closes_runtime` encoded a defunct mental model where deny aborted the turn.
- **Rejected: Carry forward `failed` expectation from G18.1 test names.** Contradicts L3; would force implementer to either break L3 or break the test.
- **Rejected: Amend spec/mapping to route deny to `failed`.** Spec semantics are clear — deny is per-action, not per-turn.
- **Implication:** Deny path asserts `job.status == "completed"` + audit trail differentiation via `resolution_action == "deny"` field. Test `:1881` rename pre-authorized from `..._failed_...` to `..._completed_...`.
- **Trade-offs:** None — corrects a stale-contract artifact.
- **Confidence:** High (E2) — spec citations unambiguous; verified against live code.
- **Reversibility:** N/A — spec is the authority.
- **Change trigger:** Spec revision that redefines deny as turn-aborting.

### Decision: Direct finalizer-guard tests promoted from recommendation to binding lock (L11)

- **Driver:** Adversarial review (Round 2) identified that G18.1/F16.1 public-path unskips don't cover: one-snapshot enforcement, D4 suppression on terminal snapshots, `resolved+failed→unknown`, anomalous-pending warning, or pre-D4 derivation invariant. These are the spec's hardest guarantees.
- **Rejected: Keep as recommendation.** "Recommended" is a copy-prone downgrade — implementer might omit them under time pressure. The spec explicitly attributes the guard to these 5+ guarantees.
- **Implication:** 7 binding test obligations (L11-T1 through L11-T7) plus 3 warning-discipline tests (L9). Direct-call tests construct snapshot state explicitly, bypassing `start()`/`decide()`.
- **Trade-offs:** Increases implementer scope — 10 additive tests on top of 8 unskips.
- **Confidence:** High (E2) — adversarial review's reasoning is structurally sound; spec citations for each obligation.
- **Reversibility:** High — tests can be removed if found redundant by future review.
- **Change trigger:** Discovery that public-path tests fully cover all spec guarantees (unlikely given the `resolved+failed` path is unreachable via normal public flows).

### Decision: Lineage stays `"completed"` for `final_status="unknown"` (Precedent A over Precedent B)

- **Driver:** Existing non-escalation tail at `delegation_controller.py:2425` writes `lineage_store.update_status(collaboration_id, "completed")` for ALL non-escalation paths. Sibling unknown-paths at `:710, :995, :1379` write lineage `"unknown"` — but those are sentinel-bypass paths that never reach `_finalize_turn`. Under the finalizer guard, `final_status="unknown"` for `resolved + non-completed` means "operator's decision was accepted and dispatched, but post-dispatch turn resolution is uncertain." Lineage `"completed"` means the collaboration handle is closed, not a claim about job-outcome certainty.
- **Rejected: Precedent B (mirror job status to lineage).** Would require additional edits to the non-escalation tail — broader scope than W3/L6 promise. Also conflates lineage-handle closure with job-outcome semantics.
- **Implication:** Binding test obligation for `lineage_store.get(cid).status == "completed"` post-finalizer for `final_status="unknown"`. If implementer discovers contradicting spec authority, surface BLOCKED.
- **Trade-offs:** Existing lineage "unknown" paths (`:710, :995, :1379`) create a semantic divergence — two kinds of "unknown" paths with different lineage writes.
- **Confidence:** Medium (E1) — spec silent on lineage under new finalizer guard; decision based on non-escalation-tail precedent + scope preservation.
- **Reversibility:** High — single-line change in the non-escalation tail.
- **Change trigger:** Spec revision or Task 22 contracts review that explicitly governs lineage for finalizer-derived unknown.

### Decision: F16.1 invocation assertion is side-effect uniqueness (not method-call count)

- **Driver:** Round 3 softened "exactly once" to "at least once"; Round 4 adversarial review identified that "at least once" permits double-finalization regressions (duplicate outcome emission, repeated release/close, duplicate audit records). Side-effect uniqueness catches the regression class without over-coupling to method-call mechanics.
- **Rejected: "Exactly once" method spy.** Brittle under non-mutating helper extraction; would break on harmless refactors.
- **Rejected: "At least once."** Too weak — doesn't catch duplicate finalization.
- **Implication:** Assert exactly ONE terminal outcome record + ONE final job transition + ONE runtime release + ONE session close + ONE lineage update. Implementer authority for instrumentation pattern.
- **Trade-offs:** More complex test assertions; but guards against a non-obvious regression class.
- **Confidence:** High (E2) — adversarial review's reasoning is structurally sound.
- **Reversibility:** High — assertion style only.
- **Change trigger:** None — this is strictly better than both alternatives.

### Decision: Context-metrics fix on separate `chore/` branch

- **Driver:** User asked for the fix; project convention separates unrelated changes by branch scope. The fix is to `packages/plugins/context-metrics/` while the feature branch is `feature/delegate-deferred-approval-response`.
- **Rejected: Mix chore and feature changes.** Muddies branch scope; the fix is independently mergeable.
- **Implication:** `chore/context-metrics-opus-4-7` at `727898c4`, 1 commit ahead of main. Feature branch clean except untracked convergence map. User explicitly declined PR.
- **Trade-offs:** The feature branch still sees the un-fixed context-metrics code (the chore fix is on its own branch). Switching to the chore branch gives the corrected behavior.
- **Confidence:** High (E2) — git operations verified.
- **Reversibility:** N/A — clean separation.
- **Change trigger:** None.

## Changes

### Commits landed this session (1)

1. **`727898c4` fix(context-metrics): detect claude-opus-4-7 1M context window** — on `chore/context-metrics-opus-4-7` branch.
   - `config.py:21` — added `"claude-opus-4-7": 1_000_000` to `MODEL_WINDOWS`.
   - `README.md:149` — added `claude-opus-4-7` row to model table.
   - `test_config.py:63-66` — added `test_opus_4_7_detects_1m`.
   - `CHANGELOG.md:11,16-17` — updated Unreleased Added entry; added Fixed entry.

### Files modified (uncommitted)

| File | Purpose |
|---|---|
| `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-19-convergence-map.md` | **NEW (untracked)** — Task 19 convergence map at Round 4 (526 lines). 11 locks (L1-L11), 12 watchpoints (W1-W12), 8 Bucket A tests, 10 binding additive tests. |

## Codebase Knowledge

### `_finalize_turn` structure at HEAD `844e6f97` (`:2340-2445`)

The captured-request branch of `_finalize_turn` is the Task 19 rewrite target. Current flow:

| Line range | Current behavior | Task 19 change |
|---|---|---|
| `:2359` | `if captured_request is not None:` entry | Unchanged |
| `:2362-2367` | D6 diagnostic (`_verify_post_turn_signals`) gated by `not captured_request_parse_failed` | Unchanged |
| `:2369-2371` | **D4 unconditional `update_status(rid, "resolved")`** | REPLACE with snapshot-conditional per L2 |
| `:2383-2384` | L11 unknown-kind carve-out: `if interrupted_by_unknown: final_status = "unknown"` | PRESERVE (L4) |
| `:2385-2390` | Kind-based derivation: `_CANCEL_CAPABLE_KINDS → "needs_escalation"`, `completed → "completed"`, else `"needs_escalation"` | REPLACE with L3 terminal-guard mapping table (snapshot-based, not kind-based) |
| `:2392` | `_persist_job_transition(job_id, final_status)` | Unchanged |
| `:2395-2407` | Escalation audit emission | Unchanged (W6) |
| `:2411-2413` | Post-audit re-read for `DelegationEscalation` shape | Permitted hydration read (L1 exclusion) |
| `:2416` | `DelegationEscalation(` construction site #2 | Unchanged (W7 count=2) |
| `:2424-2429` | Non-escalation tail: lineage update → release → close → emit terminal outcome | Unchanged (W3); lineage stays `"completed"` (L6.1) |
| `:2431-2445` | No-capture branch | Unchanged (L5) |

### Parse-failed path creates minimal store record (`delegation_controller.py:947-961`)

When server-request parsing fails, the controller creates a minimal `PendingServerRequest(kind="unknown", ...)` at `:947-957`, calls `_pending_request_store.create(minimal)` at `:960`, and sets `captured_request_parse_failed=True` at `:962`. The audit-trail contract requires this record. Snapshot status is `"pending"` (worker never writes a terminal status for unknown-kind parse failures). This was the factual error in Round 1's L1 — the claim "no store record" was false.

### Spec §`_finalize_turn` Captured-Request Terminal Guard (`design.md:1738-1827`)

The binding 4-row mapping table (spec `:1762-1767`):

| `request_snapshot.status` | `turn_result.status` | `final_status` |
|---|---|---|
| `"resolved"` | `"completed"` | `"completed"` |
| `"resolved"` | `"interrupted"` or `"failed"` | `"unknown"` |
| `"canceled"` | any | `"canceled"` |
| `"pending"` OR `None` | any | fall through to kind-based logic |

Key spec guarantees: one-snapshot invariant (spec `:1747-1756`); D4 blind-write suppression (`:1778-1787`); anomalous-pending warning (`:1774`); tombstone warning (`:1786`); parse-failed pending falls through (`:1801, :1826`).

### Deny semantics under Packet 1 (`design.md:1663-1701`)

`deny → decline` is per-action, not per-turn. Spec `:1677`: `{"decision": "decline"}` — operator declined this specific action; App Server does not execute it but does not abort the turn. The terminal `item/completed` carries `status: "declined"`. This means deny paths reach `_finalize_turn` with `request_snapshot.status == "resolved"` and `turn_result.status == "completed"`, mapping to `final_status == "completed"` — NOT `"failed"`. The pre-Packet-1 test name `test_decide_deny_marks_job_failed_and_closes_runtime` encodes defunct semantics.

### `pending_request_store.get` API (`pending_request_store.py:40`)

Signature: `def get(self, request_id: str) -> PendingServerRequest | None`. Returns `None` for tombstone race (record deleted between check and read). The `PendingServerRequest` has a `status` field with values in `{"pending", "resolved", "canceled"}`.

### Context-metrics plugin model detection (`config.py:19-45`)

`MODEL_WINDOWS` is the prefix-matching table. `detect_window_from_model` iterates prefixes via `model.startswith(prefix)`. `claude-opus-4-7` did NOT match `claude-opus-4-6` because the trailing `-6` broke the prefix. The `maybe_upgrade_window` fallback auto-upgrades to 1M when `observed_occupancy > DEFAULT_WINDOW (200_000)` — this is why the hook readouts changed mid-session from `/200k` to `/1M`.

### Convergence map structural anatomy (Round 4, 526 lines)

The convergence map follows the same structural pattern established in Task 17 and Task 18:

| Section | Line range | Purpose |
|---|---|---|
| Revision marker | 1-3 | Round chronology with supersession trail |
| Scope | 5-15 | Task 19 vs Task 20/21/22 boundary; poll/discard explicitly excluded |
| Authority order (5 layers) | 17-26 | Spec > Unknown-kind spec > carry-forward > live code > Phase H plan body (informative-only) |
| Live anchors table | 28-70 | File:line citations verified at HEAD; G18.1 decorator + constant sites; F16.1 sites |
| Locks L1-L11 | 72-300 | L1 one-snapshot, L2 D4 conditional + three-way warning, L3 terminal mapping, L4 L11-preserve, L5 no-capture-preserve, L6 tails + lineage decision, L7 G18.1 closure, L8 F16.1 closure + body, L9 assertion-shape + warning tests, L10 out-of-scope, L11 direct guard tests |
| Watchpoints W1-W12 | 302-318 | Binding negative scope: no decide/start edits, tail sequencing, carve-out preservation, escalation shape, invariant counts, BLOCKED protocol |
| Branch matrix | 320-340 | 9-path table from spec `:1791-1804` with L3 outcome per path |
| Per-test triage | 342-380 | Bucket A (8 tests), Bucket B (zero expected), New additive (10 binding: 3 L9 + 7 L11) |
| Acceptance criteria | 382-408 | Code + Tests + Closeout-docs checklists |
| Pre-dispatch checklist | 410-430 | 16 items |
| Commit shape | 432-440 | 1 + 1 + 1 anticipated |
| Carry-forward expectations | 442-458 | F16.1 closed, F16.2 closed, G18.1 closed, TT.1/RT.1 unchanged |
| Pre-dispatch warnings | 460-472 | 7 high-risk loci |
| Restructure record | 474-526 | Rounds 1-4 with full defect/fix tables per round |

### Spec §`_finalize_turn` path table (spec `:1791-1804`)

9 worker paths; only 2 reach the terminal-guard mapping:

| Path | Reaches `_finalize_turn`? | Guard outcome |
|---|---|---|
| Decide-success (any kind) | Yes | `resolved + completed → completed` (or `unknown` on rare post-dispatch fault) |
| Timeout-cancel-dispatch-succeeded | Yes | `canceled + any → canceled` |
| Timeout-interrupt-succeeded | No (sentinel bypass) | N/A |
| Timeout-interrupt-failed | No (sentinel bypass) | N/A |
| Timeout-cancel-dispatch-failed | No (sentinel bypass) | N/A |
| Dispatch-failed | No (sentinel bypass) | N/A |
| Internal-abort | No (sentinel bypass) | N/A |
| Unknown-kind parse failure | Yes (parse_failed=True) | Snapshot pending; L11 carve-out → `unknown` |
| No capture (analytical turn) | Yes (no-capture branch) | L5 unchanged |

F16.1's two tests map directly to the two "Yes" load-bearing rows (decide-success and timeout-cancel-success).

## Context

**Mental model:** This session is fundamentally about **adversarial review as a load-bearing process**. The convergence map went through 4 rounds of review, each catching a structurally distinct defect class: Round 1 had 5 Criticals (stale anchors, false parse-failed model, self-contradictory ordering, weak direct-test binding, vacuous F16.1 closure). Round 2 had 3 Criticals (deny-status contradiction, residual stale language, copy-prone downgrade). Round 3 had 1 Critical + 2 High (impossible test scenario, rename contradiction, weak invocation assertion). Each round found defects the prior round could not have seen because corrections from the prior round exposed new surfaces.

**Core insight:** Carry-forward contamination is the dominant defect class in Phase H convergence-map authoring. Round 2 caught stale line numbers (from carry-forward.md that didn't re-grep after fix commit shifted lines). Round 3 caught stale test names + stale terminal-status expectations (from pre-Packet-1 test semantics surviving a contract change). The pattern: test artifacts encode prior contracts; only spec-table cross-checks catch them.

**Framing analogy:** Each adversarial review round is like a different test-suite layer in a CI pipeline — unit tests (structural correctness), integration tests (cross-section consistency), E2E tests (spec-vs-implementation alignment). No single round catches everything.

**Defect taxonomy across 4 rounds:**

| Round | Defect class | Example | Root cause |
|---|---|---|---|
| 1→2 | Stale line numbers | G18.1 `:1525` mapped to wrong test name | carry-forward.md not re-grepped after fix commit shifted lines |
| 1→2 | False factual model | L1 claimed parse-failed has no store record | Assumed semantics from name without grepping actual code path |
| 1→2 | Self-contradictory ordering | L4 ordering block put D4 before snapshot | Drafted ordering from current-code memory, not from redesigned lock semantics |
| 2→3 | Stale contract expectation | Deny tests assert `job.status == "failed"` | Pre-Packet-1 test names encode defunct contract; spec says deny→decline doesn't abort |
| 2→3 | Residual stale language | Branch Matrix still said "Snapshot read SKIPPED" | L1 corrected but downstream sections not propagated |
| 2→3 | Copy-prone downgrade | Commit shape said "recommended" for L11 binding tests | Summary section used weaker language than the lock itself |
| 3→4 | Impossible test scenario | L11-T7 required resolved+needs_escalation | Test scenario derived from the obligation without checking L3 compatibility |
| 3→4 | Self-contradicting guidance | Rename authorized in 3 places, denied in 1 | Round-3 correction added the authorization without removing the Round-1 denial |
| 3→4 | Weak invariant | F16.1 "at least once" permits double finalization | Round-3 softened too far to avoid Round-2's over-coupling |

## Learnings

### Carry-forward.md is informative-only below live code in convergence-map authoring

**Mechanism:** Task 18's closeout-docs commit (`844e6f97`) claimed "post-Task-18-fix line numbers" but the `b8e7f9ce` fix commit's removal of test-side PSR.create workarounds shifted lines without re-verifying the carry-forward entry. The convergence map inherited stale line→test mappings.

**Evidence:** Live grep showed `:1525` is `test_start_post_turn_finalization_failure_marks_job_unknown_and_cleans_up` — carry-forward.md said it was the approve test. 4-line discrepancy across all controller test mappings.

**Implication:** Every convergence map MUST verify carry-forward claims against `grep` before authoring locks. Future closeout-docs MUST re-grep line numbers before recording.

### Test names encode contracts — stale names are stale contracts

**Mechanism:** `test_decide_deny_marks_job_failed_and_closes_runtime` encoded the pre-Packet-1 semantic that deny aborted the turn. Under Packet 1, deny→decline doesn't abort; the turn completes; finalizer maps `resolved+completed→completed`. The name is a stale-contract artifact.

**Evidence:** Spec `:1677, :1684, :1686` unambiguously define deny as per-action, not per-turn. Round-3 adversarial review caught the contradiction between L3's table and the G18.1 deny test assertions.

**Implication:** When convergence maps inherit test expectations from carry-forward, cross-check every assertion against the binding spec mapping table, not just the test name.

### L11-T7's impossibility was a structural-thinking failure

**Mechanism:** Round-3 specified a scenario requiring `snapshot="resolved"` AND `final_status="needs_escalation"` to test the hydration re-read path. But L3 maps resolved to completed/unknown — never needs_escalation. The escalation tail's hydration re-read is only reachable via `pending`/`None` fall-through.

**Evidence:** L3's own table in the same document. The contradiction was self-contained.

**Implication:** When designing test scenarios, verify the scenario's inputs and outputs against the lock tables in the SAME document. Don't assume a scenario is valid because the test obligation is valid.

### Context-metrics hook 200k vs 1M mismatch

**Mechanism:** `MODEL_WINDOWS` at `config.py:19-22` only knew `claude-opus-4-6` and `claude-sonnet-4-6`. `claude-opus-4-7` model ID doesn't match `claude-opus-4-6` prefix (trailing `-6`). Default window stayed at 200k until observed occupancy exceeded 200k and `maybe_upgrade_window` fallback triggered.

**Evidence:** Hook readouts went from `198k/200k (99%)` to `210k/1M (21%)` mid-session. System prompt explicitly states "Opus 4.7 (1M context)." The model's behavior (rushed Round-4 edits, premature "cannot do more work" declarations) was a direct consequence of trusting the hook's readout over the system prompt's binding authority.

**Implication:** Added `claude-opus-4-7` to `MODEL_WINDOWS`. Test added. Fix committed on `chore/context-metrics-opus-4-7` at `727898c4`.

## Next Steps

1. **User reviews Round-4 convergence map independently.** User has the file at `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-19-convergence-map.md` (untracked, 526 lines). They will share feedback at the start of the next session. Expect Round 5 corrections based on their review.

2. **After Round-5 review settles, author `task-19-dispatch-packet.md`.** The dispatch packet is the Implementer Prompt — ~468 lines per Task 18 precedent. Must incorporate L9/L11 binding tests, pytest discipline, stale-anchors disclaimer, deny→completed correction, BLOCKED protocol, and out-of-scope (Task 20/21/22) warnings.

3. **Commit convergence map + dispatch packet together as `chore(plan)`.** Single commit on `feature/delegate-deferred-approval-response`.

4. **Dispatch Task 19 implementer.** Opus default per user preference. TDD ordering preamble. Bounded-poll budget 5s/50ms. Pytest discipline (synchronous + timeout + file-redirect; no pipe-to-tail).

5. **Context-metrics chore branch.** `chore/context-metrics-opus-4-7` at `727898c4` stays local per user directive. No PR. Available for merge to main whenever user chooses.

## In Progress

**Status:** Task 19 convergence map at Round 4 — user is reviewing independently before the next session. Working tree has one untracked file. All other state is clean.

- **Approach:** Adversarial review cycle (user reviews map, shares findings, Claude corrects). 4 rounds completed in this session.
- **State:** Convergence map is at Round 4 (526 lines, 11 locks, 12 watchpoints). Not yet committed. User will determine whether Round 5 corrections are needed.
- **Working:** All 4 rounds of corrections applied. Context-metrics fix committed on separate branch.
- **Not working/incomplete:** The convergence map may have additional defects that Round 5 catches — the pattern across 4 rounds is that each round surfaces new defect classes.
- **Open question:** Whether the user's independent review will yield "defensible" or "another major revision."
- **Next action:** Wait for user's Round-5 feedback. Apply corrections if needed. Then author dispatch packet.

## Open Questions

- **L6.1 lineage decision stability.** Adopted Precedent A (lineage stays `"completed"` for all three new terminals) with binding test obligation. Phase H Task 22 (contracts) may revisit. If implementer discovers contradicting spec authority during dispatch, surface BLOCKED.
- **L11-T7 proxy fixture feasibility.** The `_CountingPendingRequestStore` proxy mechanism specified for T7b may be harder to implement than anticipated if the controller's store dependency doesn't support clean injection. If so, implementer should surface BLOCKED and propose alternative verification.
- **Round-5 findings.** User is reviewing independently. Unknown scope of corrections.

## Risks

- **Carry-forward contamination may recur in Round 5.** Each of the 4 rounds caught a different surface of carry-forward contamination (stale line numbers → stale test names → stale terminal expectations → stale rename guidance). The pattern may have more surfaces.
- **Context budget was misunderstood mid-session.** I trusted the hook's 200k readout and rushed Round-4 corrections. The 1M context window was available the whole time. Future sessions: trust system prompt model declaration over hook readouts when they diverge.
- **The convergence map has been revised 4 times.** Each revision adds supersession-marker history and increases document complexity. If Round 5 yields further corrections, consider whether a clean Round-5 rewrite (collapsing history) is cleaner than another addendum layer.

## References

### Prior handoffs (chain)

- **Resumed from:** `docs/handoffs/archive/2026-04-26_18-30_phase-g-task-18-closes-1plus1plus1-chain-with-round-7.md`
- Earlier in chain: `docs/handoffs/archive/2026-04-26_15-45_task-18-opus-implementer-in-flight-after-sonnet-budget-failure.md`
- Earlier: `docs/handoffs/archive/2026-04-26_13-52_task-18-dispatch-packet-ready-after-round-5-correction.md`

### Active artifacts

- **Convergence map (untracked):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-19-convergence-map.md` (526 lines, Round 4)
- **Plan body:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-h-finalizer-consumers-contracts.md` (informative-only per authority order)
- **Carry-forward state:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md`
- **Spec authority:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`

### Live code (key locations)

| Anchor | Path |
|---|---|
| `_finalize_turn` def | `delegation_controller.py:2340` |
| D4 unconditional write (REPLACE) | `delegation_controller.py:2369-2371` |
| L11 unknown-kind carve-out (PRESERVE) | `delegation_controller.py:2383-2384` |
| Kind-based derivation (REPLACE) | `delegation_controller.py:2385-2390` |
| `DelegationEscalation(` site #1 | `delegation_controller.py:833` |
| `DelegationEscalation(` site #2 | `delegation_controller.py:2416` |
| Parse-failed minimal record | `delegation_controller.py:947-961` |
| `pending_request_store.get` | `pending_request_store.py:40` |

### Branches

| Branch | Status | Head |
|---|---|---|
| `feature/delegate-deferred-approval-response` | Active; 68 commits ahead of main; 1 untracked file | `844e6f97` |
| `chore/context-metrics-opus-4-7` | Local only; 1 commit ahead of main; no PR per user directive | `727898c4` |

### Memory entries written this session

- `feedback_handle_commits.md` — user wants Claude to author + execute commits proactively

## Gotchas

- **Carry-forward.md G18.1 line numbers are stale.** The entry says `:1525::test_decide_approve_...` but live code shows `:1525` is `test_start_post_turn_finalization_failure_marks_job_unknown_and_cleans_up`. Task 18's closeout-docs did not re-grep after the fix commit shifted lines. **Live grep outranks carry-forward text.**
- **`deny → decline` does NOT abort the turn.** Any test asserting `job.status == "failed"` for a deny path is wrong under Packet 1. The correct assertion is `job.status == "completed"`. Differentiation is via `resolution_action == "deny"` in the audit trail.
- **`resolved + completed → completed` and `resolved + failed → unknown` are different spec rows but map to the same request status (`resolved`).** The distinguishing input is `turn_result.status`, not `request_snapshot.status`. Direct-call tests MUST construct both combinations explicitly.
- **The non-escalation tail's post-audit re-read at `:2411-2413` only fires in the ESCALATION branch.** Terminal-snapshot paths (resolved/canceled) route to the non-escalation tail, which does NOT re-read the store. L11-T7a should assert `get_call_count == 1` for this path; only T7b (pending fall-through → needs_escalation → escalation tail) exercises the hydration re-read.
- **F16.1 tests are `pass` stubs.** Decorator removal alone is vacuous. L8.1 audit invariant: zero `pass`-bodied unskipped tests in Task 19's commit.
- **`MODEL_WINDOWS` uses prefix matching with `model.startswith(prefix)`.** `claude-opus-4-7` does NOT match `claude-opus-4-6` (trailing `-6`). Each model family needs its own entry.
- **Hook readouts can report against a wrong denominator.** The context-metrics hook defaulted to 200k until occupancy crossed the threshold. Always cross-reference the system prompt's model declaration.

## Conversation Highlights

**User's independent orientation read (Step 2):**
The user delivered a comprehensive read-only orientation covering the Task 19 kernel, live anchors, and a proposed lock structure. This set the quality bar for the session — the convergence map was evaluated against this level of specificity.

**User's Round-2 verdict — "The draft is not acceptable in its current state":**
Identified 5 Critical defects that blocked dispatch. The G18.1 line-to-test mapping error was the most consequential — an implementer would have rewritten the wrong test. The parse-failed model being "factually false" was the most diagnostic — I had assumed "parse failed = no store record" without grepping the actual code path.

**User's Round-3 deny-status discovery — "Deny terminal expectations contradict the binding L3/spec mapping":**
This was the most important finding of the session. The deny→completed revelation was not a typo or stale label — it was a substantive contract correction that changes what 4 of the 8 Bucket A tests assert. The user traced it through spec `:1677, :1684, :1686` and identified that carry-forward contamination can encode stale CONTRACT semantics, not just stale LINE NUMBERS.

**User's context window question — "We are only at 21% context. Why do you think we are at 99%?":**
Surfaced the context-metrics bug. The fix was straightforward (one-line addition to `MODEL_WINDOWS`) but the behavioral impact was significant — I had rushed Round-4 edits and prematurely declined to continue work.

**User's branching preference — "Execute path 1 (Cleanest)":**
Confirmed that the user values clean branch separation for unrelated changes. The stash → checkout → commit → return → pop dance was executed cleanly.

**User on commits — "I generally want you to handle commits for me, you do a good job with them which I greatly appreciate":**
Saved as `feedback_handle_commits.md`. User trusts commit-message style and branch-hygiene judgment; default to authoring + executing without asking.

**User on chore branch — "Do not open a PR for `chore/context-metrics-opus-4-7`":**
Branch stays local. Available for merge whenever user chooses.

## User Preferences

- **Handle commits proactively.** Verbatim: "I generally want you to handle commits for me, you do a good job with them which I greatly appreciate." Default to action for coherent buildable chunks; still pause for push/PR/amend/force-push.
- **Clean branch separation for unrelated changes.** User chose Path 1 (cleanest) over Path 2 (pragmatic). Stash + checkout + commit + return is preferred over mixing scopes on a feature branch.
- **Independent review before dispatch-ready claims.** User paused convergence map work to do their own review. Pattern: user adjudicates at each round, not delegating convergence judgment.
- **Adversarial review is load-bearing.** The 4-round cycle was driven by user-provided reviews via `/copy`. Each round caught defects the prior round couldn't have seen.
- **Don't assert "dispatch-ready."** After Rounds 2 and 3, user pushed back twice on "dispatch-ready" claims. Better framing: describe what changed and what remains uncertain.
- **No PR for local-only chore work.** User explicitly declined PR for context-metrics fix. Branch stays local.
- **Opus default for complex work.** Confirmed per prior memory (`feedback_subagent_driven_development_meaning.md`).

## Rejected Approaches

### Mix context-metrics fix into feature branch commit (rejected at Step 14)

- **Tried (considered):** Commit chore fix directly on `feature/delegate-deferred-approval-response` as a separate `chore(context-metrics)` commit.
- **Failed because:** User chose Path 1 (clean branch separation). Mixing unrelated chore changes into a feature branch muddies scope and makes independent merge harder.
- **Learned:** Always separate unrelated changes by branch when the changes are independently mergeable.

### Push `chore/context-metrics-opus-4-7` to origin and open PR (rejected at Step 14)

- **Tried (offered):** Offered to push and open PR.
- **Failed because:** User explicitly: "Do not open a PR for `chore/context-metrics-opus-4-7`."
- **Learned:** Respect user's directive on publication timing. Local branches are valid endpoints.

### Claim "dispatch-ready" after Round 2 (rejected at Step 7)

- **Tried:** Stated "Round 2 looks dispatch-ready against live code."
- **Failed because:** Round 3 adversarial review found 3 more Criticals (deny contradiction, residual stale language, copy-prone downgrade).
- **Learned:** Don't assert dispatch-readiness — describe what changed and what remains uncertain. The adversarial review cycle is the validation mechanism, not self-assessment.

### Claim "dispatch-ready" after Round 3 (rejected at Step 9)

- **Tried:** Did not explicitly claim, but offered "another review pass, commit, or hold."
- **Failed because:** Round 4 found 1 Critical + 2 High (impossible L11-T7 scenario, rename contradiction, weak invocation assertion).
- **Learned:** Pattern confirmed: each round catches defects prior rounds couldn't see. Multi-round review is structural, not overhead.
