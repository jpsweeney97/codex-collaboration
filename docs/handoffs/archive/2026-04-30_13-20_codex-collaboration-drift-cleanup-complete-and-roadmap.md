---
date: 2026-04-30
time: "13:20"
created_at: "2026-04-30T17:20:08Z"
session_id: cbec3959-c961-4fde-a558-f9726ab567c2
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-30_06-01_codex-collaboration-d03-d07-drift-cleanup.md
project: claude-code-tool-dev
branch: main
commit: 11207241
title: codex-collaboration drift cleanup complete (D-05/D-06/D-08/D-09) and short-term roadmap
type: handoff
files:
  - docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md
  - docs/audits/2026-04-29-codex-collaboration-status-verification.md
  - docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/superpowers/specs/codex-collaboration/delivery.md
  - docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md
  - docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md
  - docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md
  - docs/tickets/closed-tickets/2026-04-23-deferred-same-turn-approval-response.md
  - docs/tickets/closed-tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md
  - docs/tickets/closed-tickets/2026-03-27-r1-carry-forward-debt.md
  - docs/tickets/closed-tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md
  - docs/tickets/closed-tickets/2026-03-30-context-assembly-redaction-hardening.md
  - packages/plugins/codex-collaboration/.claude-plugin/plugin.json
  - packages/plugins/codex-collaboration/README.md
  - packages/plugins/codex-collaboration/skills/delegate/SKILL.md
  - packages/plugins/codex-collaboration/skills/codex-analytics/SKILL.md
---

# Handoff: codex-collaboration drift cleanup complete (D-05/D-06/D-08/D-09) and short-term roadmap

## Goal

Resolve the remaining drift findings (D-05, D-06, D-08, D-09) from the codex-collaboration verified drift report, completing all 9 findings. Then produce and scrutinize a short-term roadmap for the remaining codex-collaboration backlog.

**Trigger:** Continuation of the drift cleanup sequence from the D-03/D-07 session. Four findings remained: D-05 (ticket-status mismatch), D-06 (`/delegate` rendering promises), D-08 (package docs understate live surface), D-09 (diagnostic TTL stale claims).

**Stakes:** The drift report's executive verdict cannot credibly say "all findings addressed" until every finding's source-owner document is fixed, every cross-reference is updated, and the status/audit layer agrees with the closure claim.

**Success criteria:**
- All 9 drift findings marked addressed in the findings table, executive verdict, Section 7, and repair order
- Source-owner documents fixed for each finding
- No current-facing status surface contradicts the closure state
- Scrutinized short-term roadmap for remaining codex-collaboration backlog

**Connection to project arc:** Fourth and final session in the drift cleanup sequence. D-01/D-02 resolved in session 2, D-03/D-07 in session 3, D-05/D-06/D-08/D-09 in this session. The drift report is now fully resolved. Remaining codex-collaboration work is implementation backlog (T-20260416-01, T-20260429-01, T-20260429-02), carry-forward debt, and spec decisions — not drift cleanup.

## Session Narrative

Loaded the D-03/D-07 handoff, which outlined four remaining findings: D-05 + D-09 as one batch, D-06 + D-08 as another, with an executive verdict update after all were done.

Started with a read-only orientation pass for D-05 + D-09. Read the drift report D-05/D-09 entries, the reconciliation register, the 11 root ticket files, the T-06 ticket's deferred live-smoke text, the T-01 diagnostic at lines 1374/1399/1409/1462/1465, and the delegation controller's env-tunable TTL implementation. Presented the orientation to the user with a scope question about non-codex-collaboration closed tickets.

User reviewed the orientation and provided five corrections/additions:
1. Scope: keep the 5 non-codex closed tickets out of this batch — D-05 is anchored in codex-collaboration drift, not general ticket hygiene.
2. Naming: T-20260327-01 is "R1 carry-forward," not "T-01 carry-forward" — T-01 means the delegate execution remediation ticket.
3. T-06 needs a supersession note for the deferred live-smoke text, not just relocation.
4. `git mv` creates link debt — user listed 5 specific reference files that need path updates.
5. Reference-update policy: update current-facing docs, leave archived handoffs and benchmark transcripts alone.

Created `chore/d05-d09-ticket-diagnostic-cleanup` branch. Executed D-05 (3 ticket moves, 5 reference updates, T-06 supersession note, register row widening) and D-09 (3 inline supersession annotations in the diagnostic) in the initial commit at `e3d19bbe`. Applied six-surface drift report treatment for both findings plus D-04's remaining closed-ticket-path half.

**Scrutiny round 1 (user, 4 findings):**
1. **P1:** D-09 not actually resolved — diagnostic lines 1399 and 1409 (optional-timeout-probe table and implications bullet) still contained unannotated stale TTL/env claims.
2. **P2:** Register `T02-CLOSED-TICKET-PATH` row left with out-of-vocabulary `resolved` state — register indexes open/deferred/unreconciled work only.
3. **P2:** Drift report inventory line 48 still cited old root paths for T-06 and T-02.
4. **P2:** Retained status verification audit still said tickets are in root and all 8 findings are actionable.

Fixed all four at `f9845fe6`: added 2 more supersession annotations (total 5), removed the register row, updated drift report paths, added audit supersession note with updated path cells.

**Scrutiny round 2 (user, 2 findings):**
1. **P3:** Drift report still said removed register row was "marked resolved" — should say "removed after resolution."
2. **P3:** Audit supersession note contradicted updated path cells — said "paths reflect verification time" while showing current paths.

Fixed both at `3a1809b8`. Merged to main. Proceeded to D-06.

User provided a thorough D-06 read-only orientation with RCA checkpoint. I verified all claims against source files and pushed back on one point: the fix direction was unambiguous doc-narrowing, not an open fork between "doc edit" and "payload-visibility implementation," because `FileChangeRequestApprovalParams` doesn't carry file path, change type, or diff at the wire level. User agreed and narrowed the framing.

Created `chore/d06-file-change-rendering-alignment` branch. Narrowed SKILL.md line 195 from "Show the file path and change type" to describing actual wire fields. Added investigation result to friction ticket's Option F gate. Fixed stale fixture path. Applied six-surface drift report treatment. Committed at `bc5882d9`.

**D-06 scrutiny (user, 1 finding):**
1. **P2:** Register row for T-20260429-01 still described Option F as unresolved investigation-first work.

Fixed at `74192e38`: updated register to record Option F investigation as complete, narrowed exit condition to Phase 1 sandbox carve-outs only. Drive-by: fixed D-09 fix-type line from "three" to "five" stale claims. Merged to main.

Proceeded to D-08. User provided a read-only orientation identifying 4 stale surfaces (README skill table, README architecture text, delivery.md component tree, delivery.md server listing). I verified all claims and found 4 additional surfaces: `plugin.json` description/keywords, stale `references/` tree, stale `scripts/` listing, and 20+ missing server modules in delivery.md.

User evaluated the scope options with a structured decision. Chose full tree rebuild (Option A) because narrower options leave known drift behind, and delivery.md is active/normative per the spec authority model. Created `chore/d08-package-docs-inventory-alignment` branch. Updated `plugin.json`, README (tagline, 7-skill table, architecture text), and delivery.md (complete tree rebuild from live inventory). Applied six-surface drift report treatment with "all 9 addressed" executive verdict. Committed at `5f89e58f`.

**D-08 scrutiny (user, 2 findings):**
1. **P2:** Drift report artifact inventory line still said spec is "internally inconsistent" — contradicts all-9-addressed verdict.
2. **P2:** Status audit still said all 8 findings are "genuinely actionable against current HEAD."

Fixed at `11207241`: snapshot-bounded the spec-inconsistency claim, superseded audit bottom line and cleanup sequencing section. Merged to main.

After all 9 findings were closed, the session shifted to roadmap planning. User produced a short-term roadmap (6 steps). I scrutinized it and found 4 issues: T-20260429-01 AC #4 still listed Option F as open, register timestamp stale, `<=2` escalation target unrealistic for the total escalation count, and `CONTRACTS-T02-TEMPORAL-MARKER` should be separated from the design-level Step 6.

User revised the roadmap to v2 incorporating all 4 findings. I scrutinized v2 and found it defensible with 4 edge-level clarifications (premature `turn_extraction.py` file list, live-access bottleneck shared across Steps 1-3, underspecified temporal-marker fix approach, and "avoidable" vs "legitimate" escalation definition). User accepted the verdict and folded in the final 4 adjustments.

## Decisions

### D-05: Move closed codex-collaboration tickets to `closed-tickets/`

**Choice:** `git mv` three closed tickets (T-20260423-02, T-20260330-06, T-20260327-01) from `docs/tickets/` root to `docs/tickets/closed-tickets/`.

**Driver:** D-05 finding: "`docs/tickets/` is not an authoritative open-ticket set." Three closed codex-collaboration tickets remained in root, making directory-based "open ticket" scans wrong.

**Rejected alternatives:**
- **Move all 8 non-open tickets** — rejected because the 5 non-codex tickets are separate general hygiene. User: "Keep them out unless you intentionally create a separate housekeeping pass."
- **Supersession notes only (no moves)** — rejected because the physical directory split is the mechanism D-05 identified as broken.

**Implication:** `docs/tickets/` root still has 5 non-codex closed tickets (T-010, T-20260319-01, T-20260403-01, T-20260410-03, T-20260410-04). These are tracked as separate general ticket hygiene, not codex-collaboration drift.

**Trade-offs accepted:** `git mv` creates reference-update burden. 5 current-facing references updated; historical/snapshot-bounded documents (plans, audits, benchmark transcripts) left with original paths.

**Confidence:** High (E2) — verified all ticket statuses, updated all current-facing references, swept for remaining stale paths.

**Reversibility:** High — `git mv` back if needed, though all references have been updated.

**Change trigger:** None foreseeable for the moves themselves. The 5 remaining non-codex tickets in root may prompt a separate housekeeping pass.

### D-06: SKILL.md rendering is a doc-narrowing fix, not an implementation fork

**Choice:** Narrow `/delegate` SKILL.md `file_change` rendering from "Show the file path and change type" to describing actual wire-level fields (`grantRoot` and `reason`).

**Driver:** `FileChangeRequestApprovalParams` schema defines only `grantRoot` (nullable string), `reason` (nullable string), and context IDs. Live T-01 smoke confirmed `{grantRoot: null, reason: null}`. The plugin cannot render data that doesn't exist at the wire level.

**Rejected alternatives:**
- **Code enrichment via `applyPatchApproval` support** — rejected because `applyPatchApproval` lacks `itemId`/`threadId`/`turnId` (would fail `_require_string` at `approval_router.py:54-56`) and is classified as unsupported parser shape in the schema delta (line 238).
- **Upstream request to enrich `FileChangeRequestApprovalParams`** — outside plugin scope; recorded as a future design item in friction ticket.

**Implication:** D-06's investigation is sufficient for doc closure. T-20260429-01 can still track upstream/protocol follow-up, but it no longer blocks correcting the operator-facing skill. The register's T-20260429-01 exit condition is now narrowed to Phase 1 sandbox carve-outs only.

**Trade-offs accepted:** Operators still see opaque `file_change` approvals with only `grantRoot`/`reason`. Worktree isolation + Gate 1 (review-before-promote) preserves safety, but per-file visibility remains absent.

**Confidence:** High (E2) — vendored schema, live smoke evidence, and schema delta all agree. The wire does not carry the data.

**Reversibility:** High — if upstream enriches the schema, the SKILL.md guidance can be expanded back.

**Change trigger:** `FileChangeRequestApprovalParams` gains file path/change type fields, or `applyPatchApproval` becomes the current delegation approval method.

### D-08: Full package docs rebuild, not narrow skill-table fix

**Choice:** Rebuild README skill table (2 → 7), README architecture text, `plugin.json` description/keywords, and delivery.md component tree (complete tree from live inventory).

**Driver:** User's structured decision evaluation: "once we know delivery.md misstates scripts, references, and server modules, marking D-08 addressed would recreate the split-state problem this reconciliation pass is meant to eliminate."

**Rejected alternatives:**
- **Narrow D-08 fix (README + skill names only)** — rejected because delivery.md's stale tree would remain. User: "delivery.md is active/normative per the spec authority model."
- **Replace static tree with a reference command** — rejected because the annotated tree has reader value. User: "the section is called 'Plugin Component Structure,' not 'How to inspect the package.'"
- **Null option** — non-viable because package identity is false by omission.

**Implication:** delivery.md now has a 30-module server listing that will drift if new modules are added without updating the tree. No automated drift prevention was added (out of scope for this reconciliation).

**Trade-offs accepted:** The tree is a point-in-time snapshot. Future module additions must update it manually.

**Confidence:** High (E2) — built from `find` output against live package directory. Every entry verified.

**Reversibility:** High — the tree is documentation, not code.

**Change trigger:** Any new server module, script, skill, or reference file added to the package.

### Roadmap: escalation metric reframed as "avoidable sandbox-friction"

**Choice:** Change T-20260429-01 acceptance metric from absolute `<=2 operator escalations` to `avoidable sandbox-friction escalations <=2`, counting legitimate operator-gated approvals separately.

**Driver:** T-01 smoke evidence (lines 229-236) shows ~10 "legitimate" escalations remain even after B+E+F. The old absolute `<=2` target was unrealistic.

**Rejected alternatives:**
- **Keep absolute `<=2`** — rejected because the smoke evidence shows the target is unachievable with B+E alone. Legitimate command approvals (pyright, pytest, git diff) are expected operator gates, not sandbox friction.

**Implication:** The acceptance smoke must separately count avoidable sandbox-friction escalations (Option B `~/.codex/` reads, Option E worktree gitdir pointer reads) vs legitimate operator-gated approvals vs D-06 `file_change` opacity approvals.

**Trade-offs accepted:** The metric is more nuanced. "Avoidable" needs a clear definition before the smoke.

**Confidence:** Medium (E1) — the reframing is well-grounded in evidence, but the exact boundary between "avoidable" and "legitimate" has not been tested against a live smoke.

**Reversibility:** High — the metric is a documentation/acceptance change, not a code change.

**Change trigger:** If a live smoke reveals that the boundary is wrong or that the `<=2` target is still too tight for avoidable-only escalations.

## Changes

### D-05: Ticket moves and reference updates

**Commits:** `e3d19bbe` (initial), `f9845fe6` (scrutiny 1), `3a1809b8` (scrutiny 2)

Three `git mv` operations moved closed codex-collaboration tickets to `closed-tickets/`. Five current-facing path references updated in delivery.md, delegate-skill-ux-design, deferred-approval-response-design, and two closed-ticket cross-references. T-06 supersession note added for deferred live-smoke item satisfied by T-01 closure. Register row `T02-CLOSED-TICKET-PATH` removed (not marked resolved — resolved rows don't belong in the open-work index).

### D-09: Diagnostic TTL supersession annotations

**Commits:** `e3d19bbe` (initial 3 annotations), `f9845fe6` (2 more annotations)

Five inline supersession annotations added to T-01 diagnostic at: carry-forward item (4) at line 1374, optional-timeout-probe TTL table row at line 1399, implications bullet at line 1409, approval-policy follow-up row at line 1462, T-02 closure conditional at line 1465. Each stale claim struck through with supersession pointing to `delegation_controller.py:117-157` and README-documented `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS`.

### D-06: SKILL.md file_change rendering narrowed

**Commit:** `bc5882d9` (source fix), `74192e38` (register update)

SKILL.md line 195 changed from "Show the file path and change type" to describing actual wire fields (`grantRoot` and `reason` from `requested_scope`). Investigation result added to friction ticket's Option F gate section. Stale fixture path corrected in friction ticket source-location table. Register T-20260429-01 row updated to record Option F as complete upstream schema limitation.

### D-08: Full package docs rebuild

**Commit:** `5f89e58f` (source fix), `11207241` (scrutiny closure propagation)

`plugin.json` description expanded to include delegation. Keywords added `delegation`. README tagline expanded, skill table expanded from 2 to 7 rows, architecture text updated to describe delegation surface. delivery.md component tree completely rebuilt: skills corrected (`delegate-codex` → `delegate`, 5 new skills added, `dialogue-codex` marked non-user-invocable), `agents/` directory added, `server/` expanded from 10 to 30 modules (removed stale `runtime_supervisor.py`), `scripts/` expanded from 2 to 9, `references/` corrected to actual contents.

### Drift report closure propagation (all findings)

**Across all commits:** Executive verdict updated to "all 9 addressed." Findings table shows all rows marked addressed. Section 7 stale docs list shows all items struck through. Repair order shows all steps struck through. Artifact inventory spec-inconsistency claim snapshot-bounded. Status verification audit bottom line superseded. Cleanup sequencing section superseded.

## Codebase Knowledge

### Drift report six-surface update pattern

When addressing a drift finding, update these surfaces in the drift report:

1. **Subsection annotation** — addressed-status blockquote with commit citations
2. **Finding body text** — relabel as "Original finding at report snapshot (`hash`):" with past tense
3. **"Why it matters/mattered"** — past tense
4. **"Fix type"** — "resolved via [method]"
5. **Findings table** — strikethrough severity/confidence/category, update recommended action
6. **Executive verdict, highest-risk bullets, Section 7 stale docs, repair order** — update all four to reflect the new closure state

**Recurring failure mode:** Fixing surfaces 1-4 but leaving 5-6 stale. Each scrutiny round caught at least one surface left behind.

### Closure propagation surfaces

Beyond the drift report itself, closure claims must propagate to:
- **Reconciliation register** — remove resolved rows, update related rows' current truth and exit conditions
- **Status verification audit** — supersede bottom-line and per-finding actionability claims
- **Drift report artifact inventory** — snapshot-bound any present-tense inconsistency claims
- **Source-owner tickets** — update acceptance criteria for resolved investigation gates

The pattern across D-05/D-06/D-08: the source fix was always correct, but one or more status surfaces still contradicted the closure claim. Scrutiny caught all instances.

### T-20260429-01 Option F evidence chain

The `file_change` escalation payload opacity is confirmed as an upstream schema limitation, not a plugin gap:

| Evidence source | What it shows |
|-----------------|---------------|
| `FileChangeRequestApprovalParams.json:3-10` | Schema defines only `grantRoot` (nullable string), `reason` (nullable string), and context IDs |
| `approval_router.py:58-60` | Parser preserves all non-context params opaquely — no enrichment, no field dropping |
| `delegation_controller.py:1809-1814` | `_project_request_to_view` passes `requested_scope` unchanged to `PendingEscalationView` |
| T-01 smoke (friction ticket lines 119-128) | Live capture: `{grantRoot: null, reason: null}` |
| Schema delta line 238 | `applyPatchApproval` carries `fileChanges` but lacks context IDs — unsupported parser shape |

### Package inventory (as of `11207241`)

| Surface | Count | Key items |
|---------|-------|-----------|
| MCP tools | 10 | `codex.status`, `codex.consult`, `codex.dialogue.{start,reply,read}`, `codex.delegate.{start,poll,promote,discard,decide}` |
| User-invocable skills | 7 | `codex-status`, `consult-codex`, `delegate`, `codex-review`, `codex-analytics`, `dialogue`, `shakedown-b1` |
| Non-user-invocable skills | 1 | `dialogue-codex` |
| Server modules | 30 | See `delivery.md` rebuilt tree |
| Scripts | 9 | See `delivery.md` rebuilt tree |
| Agents | 4 | `context-gatherer-code`, `context-gatherer-falsifier`, `dialogue-orchestrator`, `shakedown-dialogue` |

### Reply extraction bug location (for Step 1)

The bug is in `runtime.py:268-273` — the live-turn notification loop extracts `agent_message` only from `item/completed` notifications where `item.type == "agentMessage"`. When the App Server doesn't fire `item/completed` for agent messages (observed in B3/B5 benchmark runs), `agent_message` stays empty and downstream `parse_consult_response` fails.

The `thread/read` API exists at `runtime.py:294-299` and is already used extensively by `dialogue.py` for crash recovery. The fallback mechanism would call `read_thread` after `turn/completed` if `agent_message` is still empty, then extract using `dialogue.py:984-1001` (`_read_turn_agent_message`) or equivalent.

Key constraint: the fallback must use turn-ID lookup (not latest-turn), and `run_execution_turn()` must not trigger the fallback (execution turns don't return agent messages the same way).

## Context

### Drift cleanup completion topology

All 9 drift findings are now addressed across 4 sessions:

| Session | Findings | Resolution shapes | Commits |
|---------|----------|-------------------|---------|
| 2 (2026-04-29) | D-01, D-02 | Behavior-decisions | `7429e470`, `8a316262`, `c55aeff9`, `129b7e3d` |
| 3 (2026-04-30 AM) | D-03, D-07 | Future-scope annotation, contract-follows-code | `301f95d7`, `3ae67d90`, `e4bea95f`, `ed2e6de6` |
| 4 (2026-04-30 PM) | D-05, D-09, D-06, D-08 | Ticket moves, supersession notes, doc narrowing, inventory rebuild | `e3d19bbe` through `11207241` |

Session 1 was the initial drift assessment that produced the report itself.

### Drift-synthesis-recovery status topology

Same three current-facing status documents under the topology defined in `docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md`:

- **Current-state synthesis** (`docs/status/codex-collaboration-current-state.md`): reader entry point
- **Reconciliation register** (`docs/status/codex-collaboration-reconciliation-register.md`): bounded open-work index (now fully updated through D-08)
- **Drift report** (`docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`): supporting evidence, all 9 findings addressed

### Short-term roadmap (scrutinized, v2 with adjustments)

Fully captured in the user's final message. The roadmap has 7 steps (0-6) and operating rules. Key details:

**Step 0: Roadmap cleanup** — single docs commit on `chore/codex-collaboration-roadmap-cleanup`. Mark friction ticket AC #4 satisfied by D-06. Rewrite Phase 2/3 Option F language. Change `<=2` to `avoidable sandbox-friction escalations <=2`. Update `Last reconciled:` to `2026-04-30`. Fix `CONTRACTS-T02-TEMPORAL-MARKER` with non-ticket-specific rewrite (not `(closed)` annotation — normative contract text should not use a closed ticket as a temporal marker).

**Steps 1-3: Runtime work.** Three-commit pattern per step: implementation/tests → evidence artifact → ticket/register closeout. All require live Codex App Server for closure-grade verification. If blocked, land implementation only, keep tickets open.

**Steps 4-6: Backlog decisions.** Independent of live access. Can proceed in parallel with blocked Steps 1-3 verification.

**Escalation metric:** `avoidable sandbox-friction escalations` = escalations caused by plugin sandbox policy being too narrow (Option B `~/.codex/` reads, Option E worktree gitdir reads). Count separately: legitimate command approvals, file-write approvals, D-06 `file_change` opacity approvals, deliberate security-probe denials.

## Learnings

### Incomplete sweep before first commit is the recurring root cause

**Mechanism:** In D-09, I annotated the 3 stale locations I'd already read but didn't sweep for semantic equivalents across the full 1465-line diagnostic. In D-08, I updated the drift report's executive verdict but not its artifact inventory or the status audit's bottom line.

**Evidence:** The D-07 handoff documented this exact lesson: "For any future contract-vs-code alignment, do the exhaustive grep before the first commit, not after scrutiny." I failed to apply it to D-09 and D-08.

**Implication:** Before claiming any drift finding is addressed, run a semantic sweep for all related phrases/claims across the full closure-propagation surface set (drift report, register, audit, source tickets), not just the lines the finding cited.

**Watch for:** The sweep must be semantic, not just path-based. Old TTL references used phrases like "configurable in code only" and "env tuning is not implemented today" — not the env var name itself.

### Closure propagation is a systematic failure mode, not a point defect

**Mechanism:** Every finding in this session (D-05, D-06, D-08) required at least one scrutiny round to fix closure-propagation issues. The source fix was always right; the status-layer updates lagged.

**Evidence:** D-05 scrutiny: audit still said tickets in root. D-06 scrutiny: register still described Option F as unresolved. D-08 scrutiny: drift report artifact inventory still said "inconsistent," audit still said "actionable."

**Implication:** After fixing a drift finding's source-owner document, systematically check: register row, audit bottom line, drift report artifact inventory, any ticket acceptance criteria that referenced the finding. This is a checklist, not a judgment call.

**Watch for:** New status surfaces added after the initial drift report (e.g., the status verification audit was not in the original six-surface pattern but was caught by scrutiny).

### Register rows have a lifecycle: open → work → remove

**Mechanism:** The register defines five states (blocking, open, drift, missing-artifact, deferred). "Resolved" is not one of them. When work is done, the row should be removed, not marked with an out-of-vocabulary state.

**Evidence:** Initial D-05 fix marked `T02-CLOSED-TICKET-PATH` as `resolved`. Scrutiny caught it as a P2: "a state not listed in the State Vocabulary."

**Implication:** When closing a register row, remove it entirely. The drift report's addressed annotations serve as the historical record.

**Watch for:** Future temptation to keep resolved rows for "completeness" — the register is for open work, not history.

## Next Steps

### 1. Execute Step 0: Roadmap cleanup

**Dependencies:** None.

**What to read first:** The roadmap adjustments in this handoff's Context section. Then: friction ticket AC #4 at line 192, register line 68, contracts.md line 338.

**Approach:** Single docs commit on `chore/codex-collaboration-roadmap-cleanup`. The exact `rg` verification checks are in the user's v2 roadmap (5 commands, final 2 should return no matches after edits).

**Acceptance criteria:** AC #4 marked satisfied. Phase 2/3 headings rewritten. Escalation metric reframed. Register timestamp updated. Temporal marker rewritten as non-ticket-specific.

### 2. Execute Step 1: T-20260416-01 reply extraction fix

**Dependencies:** Step 0 should land first (it's a clean docs commit). Step 1 is the register's priority #1 for runtime work.

**What to read first:** Ticket closure criteria at lines 338-358. The reply extraction bug at `runtime.py:268-273`. The existing `thread/read` infrastructure at `runtime.py:294-299` and `dialogue.py:394,659,918,986`. The vendored `ThreadReadResponse.json` schema.

**Approach:** Three-commit pattern. Implementation must use turn-ID lookup, preserve best-effort failure semantics, and prove execution-turn isolation. Live verification requires App Server access.

### 3. Execute Steps 2-6 per roadmap

Steps 2-6 follow the roadmap sequence. Steps 1-3 share the live-access bottleneck. Steps 4-6 can proceed independently.

## In Progress

Clean stopping point — all drift cleanup committed and merged to main, roadmap scrutinized and accepted with adjustments. No work in flight.

## Open Questions

### Should the 5 non-codex closed tickets in root be moved?

After D-05, `docs/tickets/` root still has 5 non-codex closed tickets (T-010, T-20260319-01, T-20260403-01, T-20260410-03, T-20260410-04). This is separate general ticket hygiene, not codex-collaboration drift. No decision has been made on whether or how to address it.

### Is `thread/read` response shape stable across App Server versions?

The vendored schema is `0.117.0`. The schema delta covers `0.125.0` but `ThreadReadResponse` was not explicitly compared. Before implementing the Step 1 fallback, verify the response shape against the current tested version.

### What is the right commit-order discipline for Steps 4-6?

The three-commit pattern (implementation → evidence → closeout) was defined for runtime Steps 1-3. Steps 4-6 are decision/disposition work, not runtime implementation. The user's v2 roadmap does not specify commit patterns for these steps.

## Risks

### Delivery.md tree drift

The delivery.md component tree is now a 30-module server listing that will drift when new modules are added. No automated enforcement exists. The tree was rebuilt to match current state, but future changes will silently diverge unless someone remembers to update it.

### Live App Server access bottleneck

Steps 1-3 all require live Codex App Server access for closure-grade verification. If access is unavailable for an extended period, three tickets stay open despite potentially complete implementations. Steps 4-6 can proceed independently.

### Roadmap Step 0 is prerequisites for Steps 1-2

Step 0 (roadmap cleanup) updates the T-20260429-01 acceptance criteria and escalation metric. If Step 2 starts before Step 0 lands, the smoke validation will use the old unrealistic `<=2` target.

## References

- **Drift report (all 9 addressed):** `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`
- **Reconciliation register:** `docs/status/codex-collaboration-reconciliation-register.md`
- **Status verification audit:** `docs/audits/2026-04-29-codex-collaboration-status-verification.md`
- **T-01 diagnostic:** `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md`
- **Friction ticket (T-20260429-01):** `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md`
- **Reply extraction ticket (T-20260416-01):** `docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md`
- **Unsupported request ticket (T-20260429-02):** `docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md`
- **Carry-forward tracker:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md`
- **Previous handoff:** `docs/handoffs/archive/2026-04-30_06-01_codex-collaboration-d03-d07-drift-cleanup.md`
- **D-05/D-09 commits:** `e3d19bbe`, `f9845fe6`, `3a1809b8`
- **D-06 commits:** `bc5882d9`, `74192e38`
- **D-08 commits:** `5f89e58f`, `11207241`

## Gotchas

### Register state vocabulary is a hard constraint

The register defines exactly 5 states: `blocking`, `open`, `drift`, `missing-artifact`, `deferred`. Using `resolved` or any other state is out-of-vocabulary and will be caught in scrutiny. When work is done, remove the row — don't invent a new state.

### Six-surface drift report treatment has grown beyond six surfaces

The original six-surface pattern (subsection, verdict, highest-risk, table, Section 7, repair order) is necessary but not sufficient. Closure also requires checking: artifact inventory line, status verification audit, register rows, and source-ticket acceptance criteria. The "six-surface" name is legacy — treat it as "all current-facing status surfaces."

### `plugin.json` description is a visible identity surface

The plugin description shows up in `/mcp` output and plugin listings. It's not just documentation — it's the plugin's identity string. Keep it aligned with the actual capability surface.

### Historical reference paths are intentionally preserved

When ticket files are moved, historical/snapshot-bounded documents (plans, audits, benchmark transcripts, handoff archives) keep the original paths. These are factually correct citations at time of writing. Only current-facing references (specs, delivery docs, cross-ticket cross-references) get updated paths.

## Conversation Highlights

**On D-06 fix direction:**
User: "I would not argue against the main point: D-06 should be treated as a doc-only alignment fix, not an open fork between 'doc edit' and 'payload-visibility implementation.'"
— Narrowed the scope from investigation to direct doc fix.

**On D-08 scope decision:**
User: "Choose the scope for D-08 package README / delivery inventory reconciliation" followed by a structured decision evaluation ranking 4 options with sensitivity analysis.
— Chose full tree rebuild because narrower options leave known drift.

**On escalation metric:**
User: "Define the metric as: `avoidable sandbox-friction escalations` means escalations caused by plugin sandbox policy being too narrow for expected Codex/delegation operation."
— Resolved the `<=2` realism problem with a clear categorical definition.

**On temporal marker fix:**
User: "Choose the non-ticket-specific rewrite, not a `(closed)` annotation. Reason: `contracts.md` is normative contract text."
— Directional guidance for Step 0.

## User Preferences

**Structured decision format:** User evaluates scope decisions using a formal structure (stakes, options, information gaps, evaluation, sensitivity, ranking, recommendation). Expects Claude to scrutinize the decision, not just accept it.

**Scrutiny-then-fix cycle:** Same pattern as D-01 through D-07 sessions. User produces work, scrutinizes Claude's output with specific line citations and confidence scores, expects fixes in a follow-up commit. Two rounds of scrutiny per finding is typical; three rounds rare.

**Closure propagation as a hard requirement:** User treats any contradiction between the source fix and a status surface as a merge blocker. "I would not merge yet because the reconciliation register was left behind."

**Plain language for roadmap items:** User writes roadmap steps with explicit file paths, acceptance criteria, and verification commands — not abstract descriptions. Expects the same specificity in scrutiny responses.

**Evidence-first orientation:** User's D-06 orientation included vendored schema paths, specific line numbers, and a formal RCA checkpoint with hypotheses/evidence/tests. Expects Claude to verify claims against source files before accepting.
