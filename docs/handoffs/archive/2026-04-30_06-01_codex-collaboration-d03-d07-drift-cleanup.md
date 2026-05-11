---
date: 2026-04-30
time: "06:01"
created_at: "2026-04-30T06:01:36Z"
session_id: ec6cfcef-1dfa-43e3-b49f-17eb56a589a1
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-30_00-53_codex-collaboration-d02-unknown-request-terminalization.md
project: claude-code-tool-dev
branch: main
commit: ed2e6de6
title: codex-collaboration D-03 + D-07 drift cleanup — advisory future-scope and audit schema alignment
type: handoff
files:
  - docs/superpowers/specs/codex-collaboration/advisory-runtime-policy.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/specs/codex-collaboration/recovery-and-journal.md
  - docs/superpowers/specs/codex-collaboration/foundations.md
  - docs/superpowers/specs/codex-collaboration/decisions.md
  - docs/superpowers/specs/codex-collaboration/delivery.md
  - docs/superpowers/specs/codex-collaboration/README.md
  - docs/superpowers/specs/codex-collaboration/spec.yaml
  - docs/superpowers/specs/codex-collaboration/promotion-protocol.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md
  - packages/plugins/codex-collaboration/skills/codex-analytics/SKILL.md
  - packages/plugins/codex-collaboration/skills/codex-analytics/scripts/analytics.py
  - packages/plugins/codex-collaboration/tests/test_analytics_skill.py
---

# Handoff: codex-collaboration D-03 + D-07 drift cleanup — advisory future-scope and audit schema alignment

## Goal

Resolve D-03 (advisory widening) and D-07 (audit schema alignment) from the codex-collaboration verified drift report, continuing the prioritized sequence from D-01 and D-02.

**Trigger:** Continuation of the drift cleanup sequence. D-01 (fork drift) and D-02 (unknown request terminalization) were resolved in the previous two sessions. D-03 was next per the handoff's prioritized order, followed by D-07 which had an explicit dependency on D-03 (advisory policy scope affects audit actions).

**Stakes:** D-03: advisory-runtime-policy.md described widening/rotation/freeze/reap as active runtime behavior, but code explicitly rejects all widening. A reader would build or expect the wrong runtime behavior. D-07: audit contract claimed fields and actions that didn't exist in code, and the analytics script undercounted denials. The denial undercount is a live correctness bug affecting any operator running analytics.

**Success criteria:**
- D-03: spec restructured so current Packet 1 behavior and future-scope design are clearly separated
- D-07: AuditEvent contract matches the actual `models.py` dataclass; all emitted actions documented; analytics script counts denials correctly from both legacy and current event shapes
- Both findings' drift report entries addressed via the six-surface treatment pattern
- Test suite passes after all changes

**Connection to project arc:** Third and fourth findings in the drift cleanup sequence (D-01 done, D-02 done, D-03 done, D-07 done). After this session, all four spec contradictions are resolved. Remaining findings (D-05, D-06, D-08, D-09) are lighter doc/ticket cleanup.

## Session Narrative

Loaded the D-02 handoff which outlined four next steps: D-03, D-07, batch D-05/D-06/D-08/D-09, and an open question about D-03 vs D-07 ordering. Started with D-03 per the handoff's priority order.

Read the six primary sources for D-03 in parallel: the drift report D-03 entry, `advisory-runtime-policy.md` (full 146 lines), `control_plane.py:151-158` (network widening rejection), `profiles.py:148-158` (sandbox/approval widening rejection), the reconciliation register's `ADVISORY-WIDENING-ROTATION` row, and D-02's advisory deferral note at `recovery-and-journal.md:160`.

Initial analysis identified three enforcement gates that reject widening: `control_plane.py:154` ("advisory widening is not implemented in R1"), `profiles.py:149` ("sandbox widening requires freeze-and-rotate"), `profiles.py:154` ("approval widening requires freeze-and-rotate"). All three say "not implemented" or "not yet implemented" — framing the absence as temporal, not architectural. This matched the reconciliation register's `deferred` state.

Presented the analysis with three resolution options: (A) future-scope annotation, (B) cancellation, (C) partial. My read was strongly (A). User agreed with two important corrections:

**Correction 1: Advisory approval scope is not per-request — it's disabled entirely.** I had called the per-request advisory approval scope "implemented." User corrected: the current implementation prevents advisory approval persistence by disabling approvals entirely (`approval_policy="never"`, no server-request handler installed at `runtime.py:175`, `control_plane.py:194`). Lines 51-61 of the policy doc describe a future invariant, not current machinery.

**Correction 2: `contracts.md` does define `rotate`, `freeze`, and `reap` audit actions at lines 220-222.** I had said these weren't in the contract. User corrected: they exist but aren't emitted by current code. The D-03 fix should mark them as reserved/not-currently-emitted, matching the `fork` annotation pattern at line 212. User noted this is D-03-adjacent but D-07-scoped for the broader audit schema alignment.

User also identified four additional surfaces I had missed: `foundations.md:154` (per-request approval claim), `contracts.md:138` (`update_runtime` rotation use case), `recovery-and-journal.md:117` (write triggers for rotate/freeze/reap), and `delivery.md:299,312` (test strategy items for fingerprint comparison and rotation).

User proposed a structural split for `advisory-runtime-policy.md`: current Packet 1 behavior section (fixed posture, fingerprint, post-promotion coherence, recovery) + future-scope section (widening, narrowing, rotation, reap, turn invariants). Also corrected that the policy fingerprint is not wholly future-scope — `build_policy_fingerprint()` at `control_plane.py:521` computes a real SHA-256 hash from hardcoded material. The computation is live; comparison across rotation boundaries is future.

Created `chore/d03-advisory-future-scope` branch. Drafted the anchor file (`advisory-runtime-policy.md` structural rewrite), then worked outward through 9 cross-reference surfaces. Used a consistent phrase: "Future-scope freeze-and-rotate design; not currently emitted / not current Packet 1 runtime behavior." Fixed a broken anchor (`#policy-fingerprint-model` → `#policy-fingerprint` after header rename).

**First scrutiny round (user, 4 findings):**
1. **P2 High:** Drift report D-03 body still says "Current claim" — contradicts the addressed annotation. Fix: relabel as "Original finding at report snapshot."
2. **P2 High:** Fingerprint section says "recorded in audit events and collaboration handles" — but `CollaborationHandle` has no `policy_fingerprint` field (`models.py`, `lineage_store.py`). Fix: narrow to "audit events and outcome records."
3. **P3 Medium:** README reading order line 48 still advertises widening without future-scope qualifier.
4. **P3 Medium:** Recovery write triggers table lists reserved rows inline without annotation.

All four fixed. Verified with `rg` sweep for unqualified widening/rotation/freeze/reap references. Fixed one more: outcome-record link pointed to `contracts.md#audit-event-schema` (which documents `AuditEvent`), not `decisions.md#analytics-and-review-cutover-model` (which describes `OutcomeRecord`).

Committed at `301f95d7`. Fast-forward merged to main. Branch deleted.

Proceeded to D-07. User's guidance: "start from contract follows code unless there is a concrete consumer that needs the richer fields now." Read the four D-07 primary sources in parallel: `contracts.md:187-223` (AuditEvent schema + actions), `recovery-and-journal.md:102-125` (write triggers), `models.py:200-217` (AuditEvent dataclass), and the analytics SKILL.md.

Then traced all audit emission sites across `delegation_controller.py`, `control_plane.py`, and `dialogue.py`. Built a four-way comparison table: contract spec vs recovery spec vs code emissions vs analytics skill docs. Found a three-way disagreement:

**Field divergence:** Contract claims `artifact_hash` and `causal_parent` — neither exists on `AuditEvent` dataclass (`models.py:202-217`). Code uses `extra: dict` catch-all (not in contract). Decision enum includes `escalate` — never emitted as a decision value in code.

**Action divergence:** Contract lists 13 actions. Code emits 11 (after including 4 undocumented ones). Analytics skill lists 7.

**Key discovery: the `action=decision` pattern.** At `delegation_controller.py:2784`, the decide flow sets `action=decision` (the caller's `"approve"` or `"deny"`). This means denials produce `action="deny"` events — a 9th (later 11th) undocumented action. The comment says this intentionally fixed a "pre-existing hardcoded `action="approve"` bug." Two regression tests pin it: `test_delegate_decide_async_integration.py:786` and `test_delegation_controller.py:1965`.

**Analytics correctness bug:** `analytics.py:72` only counts decisions when `action == "approve"`. With current code emitting `action="deny"` for denials, the script undercounts denials. The test fixture at `test_analytics_skill.py:135` uses the old schema (`action: "approve"` with `decision: "deny"`), so tests pass against stale fixtures despite the real-data bug.

User confirmed: "do not revert `action=decision`." Treat `deny` as intended current behavior. Also added: analytics script should handle both old compatibility shape and current shape (legacy JSONL rows may already exist). Expanded scope to include analytics script/test fixes, not just docs alignment.

User identified one additional surface: `promotion-protocol.md:133` claims rollback emits `action: promote` with `decision: deny` — but code only emits the promote audit on success. No rollback audit event exists.

Created `chore/d07-audit-schema-alignment` branch. Applied the contract-follows-code alignment: removed `artifact_hash` and `causal_parent` from AuditEvent schema, added `extra`, narrowed `decision` to `approve|deny`, added `deny` and `approval_timeout` as new documented actions, marked `crash` and `restart` as reserved. Split recovery write triggers into current/reserved tables. Fixed analytics script (one-line: `if action in ("approve", "deny")`). Updated test fixture. Fixed promotion-protocol.md rollback claim. Applied six-surface drift report treatment.

Committed at `3ae67d90`. Fast-forward merged to main. Branch deleted.

**D-07 scrutiny round 1 (user, 3 findings):**
1. **P2:** Two more emitted audit actions found: `internal_abort` at `delegation_controller.py:1184` and `dispatch_failed` at `delegation_controller.py:1311`. The D-07 patch described "9 actions" but code actually emits 11. User's verification: action-literal sweep across all three server files.
2. **P2:** Promotion transition table at `promotion-protocol.md:118` still says `rollback_needed -> rolled_back` emits an audit event — contradicting the corrected rollback paragraph.
3. **P3:** Broken cross-link in rollback paragraph (`../../../packages/...` resolves under `docs/packages/` which doesn't exist).

Created `fix/d07-scrutiny-fixes` branch. Added `internal_abort` and `dispatch_failed` to all three audit surfaces (contracts.md, recovery-and-journal.md, SKILL.md). Fixed the transition table row. Removed the broken cross-link. Did an exhaustive `grep -rn 'action="'` sweep to verify no other undocumented actions exist — found `allow`/`block`/`shadow` but confirmed they're `ScanResult` actions on `credential_scan.py`, not `AuditEvent` emissions.

Committed at `e4bea95f`. Fast-forward merged to main. Branch deleted.

**D-07 scrutiny round 2 (user, 2 findings):**
1. **P3:** Drift report addressed note still says "9-action" — should be "11-action."
2. **P3:** SKILL.md `request_id` description says "escalation/approval/timeout only" — misses internal abort and dispatch failure.

Created `fix/d07-closure-note-counts` branch. Fixed both. Committed at `ed2e6de6`. Fast-forward merged to main. Branch deleted.

User verified clean: action-literal sweep, stale count wording sweep, `git show --check`, analytics tests (9 passed).

## Decisions

### D-03: Future-scope annotation — preserve freeze-and-rotate design, annotate implementation boundary

**Choice:** Restructure `advisory-runtime-policy.md` into two sections: current Packet 1 fixed-posture behavior and future-scope freeze-and-rotate design. Keep all widening/rotation/freeze/reap text but clearly scope it as designed-but-not-yet-implemented.

**Driver:** Code error messages explicitly say "not implemented" and "not yet implemented" (`control_plane.py:156`, `profiles.py:151,156`). Reconciliation register says `deferred`. Nobody said the design is wrong — it's not built yet. User: "Evidence points strongly against cancellation. The implementation says 'not implemented,' not 'unsupported by design.'"

**Rejected alternatives:**
- **Cancellation (B)** — remove the widening/rotation text entirely. Rejected because the code's error messages frame the absence as temporal, the register says `deferred`, and the current-state doc lists advisory widening as "intentionally deferred." User: "The implementation says 'not implemented,' not 'unsupported by design.'"
- **Line-by-line tense pass** — edit 86 lines individually to change "is" → "will be." Rejected because it would be ugly, error-prone, and miss structural context. User agreed with the structural-split approach: "I would not do a line-by-line tense pass."
- **Docs-only fix (no decision record)** — just relabel the text. Rejected for the same reason as D-01 and D-02: the spec describes safety/architectural properties, not just names, so the fix is a behavior-decision.

**Implication:** The `ADVISORY-WIDENING-ROTATION` reconciliation register row retains `deferred` state but its exit condition narrows — the doc-rewrite half is complete, only "implement advisory widening/rotation" remains. Future implementers have a clear current-vs-future boundary to work from.

**Trade-offs accepted:** The future-scope section is normative spec text that describes unimplemented behavior. A reader must read the section heading to know it's future. The preamble sentence ("The following sections describe designed-but-not-yet-implemented behavior") mitigates this, but it's weaker than having no future-scope text at all.

**Confidence:** High (E2) — verified across code (3 rejection gates), spec (reconciliation register, current-state doc), and code error messages. User independently confirmed.

**Reversibility:** High — the design text is preserved intact. When freeze-and-rotate is implemented, move the future-scope content back to current.

**Change trigger:** Advisory widening is implemented.

### D-07: Contract follows code for AuditEvent schema

**Choice:** Narrow the AuditEvent contract to match the actual `models.py` dataclass. Remove `artifact_hash` and `causal_parent` (never implemented). Add `extra` (catch-all dict). Narrow `decision` from `approve|deny|escalate` to `approve|deny`. Add four undocumented actions (`deny`, `approval_timeout`, `internal_abort`, `dispatch_failed`). Mark `crash` and `restart` as reserved/not-currently-emitted.

**Driver:** User: "start from contract follows code unless there is a concrete consumer that needs the richer fields now." The `AuditEvent`/`OutcomeRecord`/`DelegationOutcomeRecord` split was intentional (`decisions.md §Analytics and Review Cutover Model`). Widening `AuditEvent` to carry richer fields goes against the split's design intent.

**Rejected alternatives:**
- **Code follows contract (add `artifact_hash` and `causal_parent` to model)** — rejected because no current consumer needs them, and the intentional split to `OutcomeRecord`/`DelegationOutcomeRecord` already carries richer analytics fields. Adding fields to `AuditEvent` just to satisfy stale contract prose is yak-shaving.
- **Keep `escalate` as a decision value** — rejected because `escalate` is only an `action` value in current code, never a `decision` value. Code emits `decision="approve"` or `decision="deny"` only.

**Implication:** The AuditEvent contract is now a faithful record of trust-boundary crossings. Richer analytics data lives in outcome records. Future audit schema work should not widen AuditEvent — route new fields to the appropriate outcome record type.

**Trade-offs accepted:** Removing `artifact_hash` and `causal_parent` from the contract means they can't be used for forensic correlation without re-adding them later. Accepted because they were never emitted — the "removal" removes only a promise, not a capability.

**Confidence:** High (E2) — verified every AuditEvent emission site across `control_plane.py`, `dialogue.py`, and `delegation_controller.py`. Exhaustive `grep -rn 'action="'` sweep confirmed 11 distinct action values. Two regression tests pin the `deny` action behavior.

**Reversibility:** High — adding fields to AuditEvent is straightforward. The model uses `extra: dict` as a catch-all, so new fields can be prototyped there before promotion to typed fields.

**Change trigger:** A concrete consumer needs `artifact_hash` or `causal_parent` for forensic reconstruction.

### Deny is a distinct audit action, not a bug to revert

**Choice:** Treat `action="deny"` as intended current behavior. Update all docs and analytics to match.

**Driver:** `delegation_controller.py:2775` comment explicitly says `action=decision` "fixes a pre-existing hardcoded `action="approve"` bug." Two independent regression tests pin the behavior: `test_delegate_decide_async_integration.py:786` ("Test 9 — audit action='deny' for deny decisions (L7a regression)") and `test_delegation_controller.py:1965`. User: "I verified the code and tests on current main."

**Rejected alternatives:**
- **Revert to `action="approve"` for both arms** — rejected because the code explicitly marks the old behavior as a bug, and two tests pin the fix. Reverting would re-introduce a known bug.

**Implication:** The analytics script must handle both legacy JSONL rows (old `action="approve"` with `decision="deny"`) and current rows (`action="deny"` with `decision="deny"`). The fix is backward-compatible: `if action in ("approve", "deny"): decisions[decision] += 1`.

**Trade-offs accepted:** Old JSONL data has `action="approve"` for denials. The script handles both shapes, but a reader of old data must know the schema changed. The SKILL.md documents this with a legacy-compatibility note.

**Confidence:** High (E2) — two independent tests, explicit bug-fix comment in code, user independently verified on current main.

**Reversibility:** Low — the deny action is pinned by regression tests and the code comment marks the old behavior as a bug. Reverting would require removing the tests and re-introducing the bug.

**Change trigger:** None foreseeable — the old behavior was explicitly a bug.

### Analytics script backward-compatible deny handling

**Choice:** Count denials from both `action=="approve"` (legacy) and `action=="deny"` (current) by changing the filter from `if action == "approve"` to `if action in ("approve", "deny")`.

**Driver:** User: "I'd prefer compatibility handling because old JSONL rows may already exist." Existing `events.jsonl` files from pre-Packet-1 sessions contain legacy-format deny events.

**Rejected alternatives:**
- **Count only current shape** — rejected because existing JSONL data would lose deny counts.
- **Migration script to rewrite old events** — rejected as unnecessary complexity. The two-branch check is simpler and handles both shapes permanently.

**Implication:** The analytics script is now resilient to schema evolution in the deny action. Future action-value changes should follow the same pattern: add the new value to the filter rather than replacing the old one.

**Trade-offs accepted:** The `audit_actions` counter shows both `approve` and `deny` as separate action counts. A reader must know that denials appear as `action="deny"` in current data and `action="approve"` with `decision="deny"` in legacy data. The SKILL.md documents this.

**Confidence:** High (E1) — user requirement, straightforward implementation, test passes with current-format fixture.

**Reversibility:** High — the filter is a single line.

**Change trigger:** If legacy JSONL data is no longer a concern (all old data aged out past retention), the `"approve"` branch could be narrowed to only count events where `decision=="approve"`.

## Changes

### `advisory-runtime-policy.md` — Structural split into current + future

**Purpose:** Separate current Packet 1 fixed-posture behavior from future-scope freeze-and-rotate design so readers know which is implemented.

**Approach:** New structure: preamble noting the file contains both current and future sections → `## Current Packet 1 Behavior` (fixed posture, fingerprint, post-promotion coherence, current recovery) → `## Future-Scope: Freeze-and-Rotate Design` (widening, approval scope, narrowing, freeze/rotate/reap, turn invariants, future recovery). Section headings demoted one level within the future-scope block.

**Key details:**
- Fixed advisory posture table uses actual values (`read-only`, `never`, `disabled`) not `e.g.` examples
- Three enforcement gates documented with exact error messages from code
- Policy fingerprint split: computation is current (`build_policy_fingerprint()` at `control_plane.py:521`), comparison across rotation boundaries is future
- Advisory approval scope rewritten: "When advisory-domain server-request handling is implemented, server requests will use per-request scope only" (future tense, not present)
- Post-promotion coherence and stale marker recovery are current — kept in the current section
- Rotation recovery moved to future section

### `contracts.md` — AuditEvent schema alignment

**Purpose:** Narrow the AuditEvent contract to match the actual `models.py:202-217` dataclass.

**Approach:** Removed `artifact_hash` and `causal_parent` (never in model). Added `extra: dict?` (in model, not in old contract). Narrowed `decision` from `approve|deny|escalate` to `approve|deny`. Added provenance note pointing to `OutcomeRecord`/`DelegationOutcomeRecord` for richer analytics. Split actions table into current (11 emitted) and reserved (6 not emitted). Added actor column. Marked `update_runtime` rotation use case as future-scope.

**Key details:**
- 11 currently emitted actions: `consult`, `dialogue_turn`, `delegate_start`, `approve`, `deny`, `escalate`, `promote`, `discard`, `approval_timeout`, `internal_abort`, `dispatch_failed`
- 6 reserved actions: `crash`, `restart`, `fork`, `rotate`, `freeze`, `reap`
- `deny` has actor `claude`, carries `decision="deny"` and `request_id`
- `approval_timeout`, `internal_abort`, `dispatch_failed` have actor `system`, carry `job_id` and `request_id`

### `recovery-and-journal.md` — Write triggers alignment

**Purpose:** Align write trigger table with actual emissions and mark reserved triggers.

**Approach:** Split into two tables: currently emitted (11 rows) and reserved (6 rows). Updated required fields to match actual emissions (e.g., `promote` requires `job_id, decision` — removed `artifact_hash`; `escalate` requires `collaboration_id, job_id, request_id`). Added `deny`, `approval_timeout`, `internal_abort`, `dispatch_failed`. Advisory crash section updated: `crash`/`restart` are reserved, not currently emitted. D-02 advisory deferral note updated from "unresolved divergence" to "future-scope advisory policy."

### `promotion-protocol.md` — Rollback audit correction

**Purpose:** Fix two stale audit claims: rollback paragraph said no audit event but transition table said audit event emitted, and paragraph had a broken cross-link.

**Approach:** Updated transition table row `rollback_needed -> rolled_back` from "Audit event emitted" to "Job state updated; no rollback-specific audit event." Removed broken `../../../packages/...` cross-link from rollback paragraph (wrong path depth, semantically incomplete target).

### `analytics.py` — Backward-compatible deny handling

**Purpose:** Fix denial undercount bug.

**Approach:** Changed `if action == "approve"` to `if action in ("approve", "deny")`. This counts decisions from both legacy (`action="approve"`, `decision="deny"`) and current (`action="deny"`, `decision="deny"`) shapes.

### `test_analytics_skill.py` — Fixture update

**Purpose:** Update test fixture to match current emission format.

**Approach:** Changed deny event fixture from `action: "approve"` to `action: "deny"` (current code behavior). The `decision: "deny"` field is unchanged. Analytics script handles both shapes, so existing tests continue to pass.

### `SKILL.md` (codex-analytics) — Action table and field update

**Purpose:** Align analytics skill docs with the 11-action audit stream.

**Approach:** Updated from 7-action to 11-action table. Added actor column. Added `policy_fingerprint`, `turn_id`, `context_size` to field table. Updated `request_id` description to cover all server-request-related actions. Added legacy-compatibility note for deny counting. Removed stale "There is no `action="deny"`" guidance.

### Cross-reference surfaces (9 files for D-03, drift report for both)

All D-03 cross-references aligned: `decisions.md:61` (rotation mitigation wording), `foundations.md:97,154` (lifecycle rules note, approval invariant), `contracts.md:138,220-222` (update_runtime, reserved actions), `delivery.md:299,312` (test strategy), `README.md:33,48` (authority table, reading order), `spec.yaml:27-32` (authority description), reconciliation register (exit condition update). Drift report six-surface treatment for both D-03 and D-07.

## Codebase Knowledge

### Advisory widening enforcement — three gates

| Gate | File:Line | Error message | Scope |
|------|-----------|---------------|-------|
| Network access | `control_plane.py:154-158` | "advisory widening is not implemented in R1" | Blocks `codex.consult` with `network_access=True` |
| Sandbox widening | `profiles.py:148-153` | "sandbox widening requires freeze-and-rotate (not yet implemented)" | Blocks any `sandbox != read-only` |
| Approval widening | `profiles.py:154-158` | "approval widening requires freeze-and-rotate (not yet implemented)" | Blocks any `approval_policy != never` |

Test pinning the network rejection: `test_control_plane.py:631-647`.

### Advisory runtime posture — what's actually fixed

The advisory runtime runs with:
- `approval_policy="never"` hardcoded at `runtime.py:175`
- No server-request handler installed (advisory turns use `run_advisory_turn` which calls `_run_turn` without handler installation — `runtime.py:159-177`)
- `control_plane.py:194` calls `run_advisory_turn` directly, not `run_execution_turn`
- `dialogue.py:435` does the same for dialogue turns

### Policy fingerprint — live but fixed

`build_policy_fingerprint()` at `control_plane.py:521-534` computes a SHA-256 hash from hardcoded material:
```
transport_mode: stdio, sandbox_level: read_only, network_access: disabled, approval_mode: never, app_connectors: disabled
```
Used at `control_plane.py:494` when creating `AdvisoryRuntimeState`. The fingerprint is recorded in:
- `AuditEvent.policy_fingerprint` (`models.py:212`) — consult events
- `OutcomeRecord.policy_fingerprint` (`models.py:236`) — consult and dialogue outcomes
- NOT on `CollaborationHandle` — no `policy_fingerprint` field in `lineage_store.py` or the contracts

### Post-promotion coherence — fully implemented

Stale marker exists in code: `control_plane.py:163` (load), `201` (clear), `333` (write method), `343` (journal write). `StaleAdvisoryContextMarker` dataclass at `models.py:191-198`. Journal operations at `journal.py`. Recovery spec section at `recovery-and-journal.md §Stale Advisory Context Marker` is accurate.

### Complete AuditEvent emission map

| Action | File:Line | Actor | Key fields |
|--------|-----------|-------|------------|
| `consult` | `control_plane.py:218` | `claude` | `context_size`, `policy_fingerprint`, `turn_id` |
| `dialogue_turn` | `dialogue.py:268` | `claude` | `context_size`, `turn_id` |
| `delegate_start` | `delegation_controller.py:717` | `claude` | `job_id` |
| `approve` | `delegation_controller.py:2784` (when `decision="approve"`) | `claude` | `job_id`, `request_id`, `decision` |
| `deny` | `delegation_controller.py:2784` (when `decision="deny"`) | `claude` | `job_id`, `request_id`, `decision` |
| `escalate` | `delegation_controller.py:2530` | `claude` | `job_id`, `request_id` |
| `promote` | `delegation_controller.py:2279` | `claude` | `job_id`, `decision="approve"` |
| `discard` | `delegation_controller.py:2421` | `claude` | `job_id` |
| `approval_timeout` | `delegation_controller.py:1777` | `system` | `job_id`, `request_id` |
| `internal_abort` | `delegation_controller.py:1184` | `system` | `job_id`, `request_id` |
| `dispatch_failed` | `delegation_controller.py:1311` | `system` | `job_id`, `request_id` |

The `action=decision` pattern at line 2784 is the key: `action` is dynamically set to the caller's decision (`"approve"` or `"deny"`). The comment at line 2775 says this intentionally fixes a pre-existing hardcoded `action="approve"` bug.

### `ScanResult` actions are NOT `AuditEvent` actions

`credential_scan.py` uses `action` on a different dataclass (`ScanResult`): `allow`, `block`, `shadow`. These are credential-scan results, not audit events. The exhaustive action sweep must filter by dataclass context.

### `spec.yaml` cross-review dependencies for advisory-policy changes

Per `spec.yaml:83-88`, changes to `advisory-policy` require review of `recovery-contract` and `contracts`. This was triggered for D-03 (both reviewed). `foundation` changes trigger all owners per `spec.yaml:94` — not triggered for D-03 or D-07 because `foundations.md` received targeted fixes only.

### Six-surface drift report update pattern

When addressing a drift finding, update these surfaces:

1. **Subsection annotation** — addressed-status blockquote with commit citations
2. **Executive verdict** (Section 2) — overall consistency assessment
3. **Highest-risk drifts** (Section 2) — bullet naming the finding
4. **Findings table** (Section 6) — row with severity/status/action
5. **Section 7 stale docs list** — bullet listing the finding
6. **Repair order** (Section 8) — step referencing the finding
7. **Subsection body text** — fix-type line and any stale action guidance (learned from D-02)

The finding body should be relabeled as "Original finding at report snapshot (`hash`)" with past tense, not left as "Current claim" which contradicts the addressed annotation.

## Context

### Drift-synthesis-recovery status topology

Same as previous sessions. Three current-facing status documents operate under the topology defined in `docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md`:

- **Current-state synthesis** (`docs/status/codex-collaboration-current-state.md`): reader entry point
- **Reconciliation register** (`docs/status/codex-collaboration-reconciliation-register.md`): bounded index of unresolved work
- **Drift report** (`docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`): supporting evidence, not authoritative

### D-03 compared to D-01 and D-02 — a third resolution shape

| Dimension | D-01 (fork drift) | D-02 (unknown requests) | D-03 (advisory widening) |
|-----------|-------------------|------------------------|--------------------------|
| Outcome shape | Keep property, change surface | Keep invariant, align mechanism | Keep design, annotate boundary |
| Resolution type | behavior-decision | behavior-decision | future-scope annotation |
| Critique rounds | 3 | 3 | 2 |
| Authority owners touched | 5 of 8 | 4 of 8 + SKILL.md | 7 of 8 + README + spec.yaml |
| Commits | 6 | 1 | 3 (initial + 2 scrutiny) |

D-07 adds a fourth shape: **contract-follows-code alignment** — narrowing spec to match implementation, plus fixing a live analytics bug.

### The "right safety property, wrong mechanism" pattern extends

D-02 established this pattern. D-03 shows a variant: "right design, wrong implementation status." The spec describes the correct future architecture but presents it as current behavior. The fix is not to change the architecture or the code, but to annotate the temporal boundary.

### AuditEvent / OutcomeRecord / DelegationOutcomeRecord topology

Three artifact types serve different purposes:
- `AuditEvent` — trust-boundary crossings, forensic reconstruction (`events.jsonl`)
- `OutcomeRecord` — advisory analytics: consult and dialogue outcomes (`outcomes.jsonl`)
- `DelegationOutcomeRecord` — delegation terminal analytics (`outcomes.jsonl`)

The split is intentional per `decisions.md §Analytics and Review Cutover Model`. AuditEvent should NOT be widened with richer analytics fields — route those to the appropriate outcome record type.

## Learnings

### Exhaustive grep sweep is essential for audit action documentation

**Mechanism:** Manual code reading of specific emission sites (the lines the drift report pointed to) missed `internal_abort` and `dispatch_failed` — they're in the same file but in error-handling branches I didn't trace. An exhaustive `grep -rn 'action="'` sweep across the server directory found all 11 action values plus the credential-scan false positives.

**Evidence:** First D-07 commit documented 9 actions. Scrutiny found 2 more via the same sweep technique.

**Implication:** For any future contract-vs-code alignment where the contract enumerates values (actions, states, fields), do the exhaustive grep before the first commit, not after scrutiny.

**Watch for:** False positives from same-named fields on different dataclasses (the `ScanResult.action` vs `AuditEvent.action` confusion).

### Test fixtures can be stale in a way tests don't catch

**Mechanism:** The analytics test fixture used old-schema deny events (`action="approve"`, `decision="deny"`). The analytics script was written to match this fixture. Both were wrong relative to current code emissions, but the test passed because it only validated script-against-fixture consistency, not fixture-against-live-emission accuracy.

**Evidence:** `test_analytics_skill.py:135` fixture, `analytics.py:72` filter, `delegation_controller.py:2784` emission. The fixture and script agreed with each other but disagreed with the code they document.

**Implication:** When a code behavior changes (like the `action=decision` fix), downstream fixtures should be updated even if the tests still pass. The test verifies the script, not the schema.

**Watch for:** Any test that uses hand-written fixtures for serialized data formats (JSONL, JSON, YAML). If the producer changes its output shape, the fixture becomes stale silently.

### The current/future boundary must be forced through every sentence

**Mechanism:** D-03's first draft was structurally correct (two sections) but individual sentences inherited pre-patch truth. The fingerprint section said "recorded in collaboration handles" (false — no `policy_fingerprint` on `CollaborationHandle`). The drift report body said "Current claim" (contradicts the addressed annotation). Each sentence that references a pre-patch concept must be individually validated against the new boundary.

**Evidence:** Four scrutiny findings on the D-03 initial commit, all from sentences that survived the structural reorganization without being forced through the current/future frame.

**Implication:** After any structural reorganization, re-read every sentence and ask: "Does this claim describe current or future behavior? Is the answer correct?" The structural reorganization creates the boundary; per-sentence validation enforces it.

**Watch for:** This pattern recurred in D-07: the first commit said "9 actions" when the code emits 11. Same root cause — the count was derived from the manually traced emissions, not the exhaustive sweep.

## Next Steps

### 1. Batch D-05 + D-09 — status/ticket/diagnostic historical cleanup

**Dependencies:** None — independent of D-03 and D-07.

**What to read first:** Drift report D-05 (`drift-report.md:113-119`) and D-09 (`drift-report.md:145-149`). Then: `docs/tickets/` root directory listing, the register's `T02-CLOSED-TICKET-PATH` row, and the T-01 diagnostic TTL claim.

**Approach:** D-05 is ticket-status mismatch — closed tickets in root `docs/tickets/` that should be in `closed-tickets/`. D-09 is a stale diagnostic claiming TTL env support is future work when code already supports it. Both are low-risk moves and doc edits.

**Acceptance criteria:** Closed tickets moved or superseded. TTL diagnostic corrected. Six-surface drift report treatment for both.

### 2. Batch D-06 + D-08 — operator/package docs cleanup

**Dependencies:** None — independent.

**What to read first:** Drift report D-06 (`drift-report.md:125-129`) and D-08 (`drift-report.md:139-144`). Then: `skills/delegate/SKILL.md` escalation rendering, package `README.md`, `delivery.md` component inventory.

**Approach:** D-06 is `/delegate` skill promising file-change visibility the runtime doesn't provide. D-08 is the package README/delivery.md understating the live skill/tool surface. Both are doc edits.

**Acceptance criteria:** SKILL.md rendering guidance matches actual escalation payload capabilities. Package README and delivery inventory reflect all shipped skills and MCP tools. Six-surface drift report treatment for both.

### 3. After all findings: update the drift report executive verdict

**Dependencies:** D-05, D-06, D-08, D-09 must be addressed first.

**Approach:** When all 9 findings are addressed (D-01 through D-09), the executive verdict at Section 2 can be updated to reflect full resolution. Currently it says "No remaining spec contradictions in the original P1 finding set" — after the batch, all findings (P1-P3) will be resolved.

## In Progress

Clean stopping point — all D-03 and D-07 work completed, committed, merged to main, and verified. No work in flight.

## Open Questions

### Should D-04's closed-ticket-path widening be addressed during D-05?

D-04 was partially addressed (register row added at `a5fd568d`). Its remaining work — closed-ticket-path widening — overlaps with D-05's ticket-status mismatch. It may be natural to complete D-04's remaining half during the D-05 batch rather than treating it separately.

### Are there other audit actions the exhaustive sweep might still miss?

The `grep -rn 'action="'` sweep found all 11 actions across static string literals. But `action=decision` at `delegation_controller.py:2784` is dynamic — it doesn't appear as a literal. If other dynamic action values exist (e.g., `action=some_variable`), they would be missed by literal grep. A more thorough check would grep for `action=` (without quotes) in AuditEvent construction sites.

## Risks

### D-05/D-06 batch may touch the same files as D-03/D-07

D-06 touches `skills/delegate/SKILL.md`. D-07 already touched the analytics SKILL.md but not the delegate SKILL.md. The risk is low since the edits are in different files, but if D-06 changes escalation rendering guidance, it should verify consistency with D-02's unknown-kind escalation fix at SKILL.md line 197.

### Analytics script backward compatibility may accumulate

Each schema change adds another branch to the backward-compatible filter. If the deny pattern repeats for future action-value changes, the filter conditions grow. The current `if action in ("approve", "deny")` is clean, but if a third value is added later, consider refactoring to a set membership check.

## References

- **Drift report:** `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`
- **D-03 spec anchor:** `docs/superpowers/specs/codex-collaboration/advisory-runtime-policy.md`
- **D-07 contract anchor:** `docs/superpowers/specs/codex-collaboration/contracts.md §AuditEvent`
- **D-07 write triggers:** `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md §Write Triggers`
- **D-07 analytics skill:** `packages/plugins/codex-collaboration/skills/codex-analytics/SKILL.md`
- **D-07 analytics script:** `packages/plugins/codex-collaboration/skills/codex-analytics/scripts/analytics.py`
- **Spec authority model:** `docs/superpowers/specs/codex-collaboration/spec.yaml`
- **Reconciliation register:** `docs/status/codex-collaboration-reconciliation-register.md`
- **Previous handoff:** `docs/handoffs/archive/2026-04-30_00-53_codex-collaboration-d02-unknown-request-terminalization.md`
- **D-03 commit:** `301f95d7` (initial) + `scrutiny fixes in same merge`
- **D-07 commits:** `3ae67d90` (initial), `e4bea95f` (scrutiny 1), `ed2e6de6` (scrutiny 2)

## Gotchas

### Exhaustive action sweep must filter by dataclass context

The `grep -rn 'action="'` sweep across the server directory returns `ScanResult.action` values (`allow`, `block`, `shadow`) from `credential_scan.py` alongside `AuditEvent.action` values. These are different dataclasses with different `action` fields. Always verify that a found `action=` literal is inside an `AuditEvent()` construction, not an unrelated dataclass.

### Test fixtures can be stale when the test still passes

The analytics test fixture used old-schema deny events. The test passed because it only validates script-against-fixture consistency. Update fixtures when the producing code changes its output format, even if tests continue to pass.

### Drift report "Current claim" paragraphs must be snapshot-bounded after addressing

Adding an addressed-status annotation does not neutralize the finding's body text. Phrases like "Current claim:" and present-tense descriptions become misleading once the finding is resolved. Relabel as "Original finding at report snapshot (`hash`):" with past tense.

### Policy fingerprint cross-link anchor changed

The `advisory-runtime-policy.md` restructure renamed the fingerprint section from `## Policy Fingerprint Model` (anchor: `#policy-fingerprint-model`) to `### Policy Fingerprint` (anchor: `#policy-fingerprint`). All cross-links from `foundations.md` were updated, but if other files add links to the old anchor, they'll break.

## Conversation Highlights

**On the D-03 resolution direction:**
User: "Evidence points strongly against cancellation. The implementation says 'not implemented,' not 'unsupported by design.'"
— Confirmed (A) future-scope annotation as the correct resolution.

**On the advisory approval scope correction:**
User: "Advisory approval scope is not really implemented as per-request-only. The current runtime prevents advisory approval persistence by disabling approvals, not by resolving advisory server requests per-request."
— Corrected my overclaim that per-request advisory approvals were "implemented."

**On the D-07 deny semantics:**
User: "Do not revert `action=decision`. Treat `deny` as intended current behavior."
— Confirmed the code fix is intentional, not a bug.

**On analytics backward compatibility:**
User: "I'd prefer compatibility handling because old JSONL rows may already exist."
— Drove the `if action in ("approve", "deny")` approach.

**On exhaustive sweep:**
User's scrutiny found `internal_abort` and `dispatch_failed` — actions I had missed because I traced specific emission sites rather than sweeping all `action=` literals.
— Taught the "grep before first commit" lesson.

**On the promotion rollback audit claim:**
User: "promotion-protocol.md still says rollback emits `action: promote` with `decision: deny`, but code has only the successful promote audit emission."
— Identified a surface I hadn't checked.

## User Preferences

**Exhaustive verification before commit:** User ran independent action-literal sweeps, `git show --check`, targeted doc searches, and analytics tests before approving each round. Provided specific line citations for every finding.

**Consistent phrasing across patches:** User suggested: "keep one explicit phrase consistent across the patch, something like: 'Future-scope freeze-and-rotate design; not currently emitted / not current Packet 1 runtime behavior.'" Applied this uniformly.

**Contract follows code as default direction:** User: "start from contract follows code unless there is a concrete consumer that needs the richer fields now." Clear directional guidance that saved a D-07 deliberation step.

**Scope containment over completeness:** Same as D-02 sessions. User chose to mark `rotate`/`freeze`/`reap` audit actions as reserved during D-03 without trying to solve the broader D-07 audit schema drift in the same patch.

**Scrutiny-driven iteration:** Same pattern as D-01 and D-02 — produce → scrutinize → fix → re-scrutinize. D-03 had 2 scrutiny rounds (4 findings + 1 link fix). D-07 had 3 scrutiny rounds (3 findings, then 2 more, total 5 findings across rounds).

**Direct action after alignment:** User: "Findings: none." followed by verification evidence and clean closure. No hedging or re-confirmation.

## Rejected Approaches

### Line-by-line tense editing for advisory-runtime-policy.md

**Approach:** Edit each of the 86 lines individually to change present tense ("is") to future tense ("will be") for widening/rotation behavior.

**Why it seemed promising:** Minimal structural change. Preserves the existing document organization.

**Specific failure:** Would be ugly, error-prone, and miss the structural context that readers need. A line that says "rotation will create a new runtime" without a section-level boundary leaves the reader uncertain whether this is current or future until they read surrounding context. The structural split provides an unambiguous visual and semantic boundary.

**What it taught:** When the fix is "this whole section describes a different temporal scope," a structural boundary is clearer than per-sentence tense changes.

### Widening AuditEvent to match the contract (code follows contract)

**Approach:** Add `artifact_hash` and `causal_parent` fields to the `AuditEvent` dataclass. Wire up promote to emit `artifact_hash`. Wire up crash/restart to use `causal_parent`.

**Why it seemed promising:** Would make the contract truthful without changing it. Adds forensic reconstruction capability.

**Specific failure:** No current consumer needs these fields. The intentional `AuditEvent`/`OutcomeRecord`/`DelegationOutcomeRecord` split already routes richer data to the appropriate record type. Adding fields to `AuditEvent` just to satisfy stale prose goes against the split's design intent. The work would be scope expansion with no product value.

**What it taught:** "Contract follows code" is the right default when the code's design is intentional and the contract is stale. The cost of narrowing the contract is zero; the cost of widening the code to match an outdated contract is real engineering work with no consumer.
