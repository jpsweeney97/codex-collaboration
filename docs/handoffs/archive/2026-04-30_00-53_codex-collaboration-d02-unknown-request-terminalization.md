---
date: 2026-04-30
time: "00:53"
created_at: "2026-04-30T04:53:09Z"
session_id: 1723f9aa-01d8-4e5d-937d-a13262aff698
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-29_23-59_codex-collaboration-drift-cleanup-d01-resolution.md
project: claude-code-tool-dev
branch: main
commit: 129b7e3d
title: codex-collaboration D-02 — unknown request terminalization decision and spec alignment
type: handoff
files:
  - docs/superpowers/specs/codex-collaboration/decisions.md
  - docs/superpowers/specs/codex-collaboration/recovery-and-journal.md
  - docs/superpowers/specs/codex-collaboration/foundations.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - packages/plugins/codex-collaboration/skills/delegate/SKILL.md
  - docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md
  - docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md
---

# Handoff: codex-collaboration D-02 — unknown request terminalization decision and spec alignment

## Goal

Resolve D-02 (unknown request handling drift) from the codex-collaboration verified drift report. D-02 was identified in the previous session's verification audit as a P1 current-facing contradiction: `decisions.md` and `recovery-and-journal.md` said unknown requests are "held and surfaced to Claude as escalations," while `contracts.md` and the actual code terminalize them.

**Trigger:** Continuation of the drift cleanup sequence from the status verification audit (`docs/audits/2026-04-29-codex-collaboration-status-verification.md`). D-01 (fork drift) was resolved in the previous session. D-02 was next in the prioritized sequence.

**Stakes:** The disagreement affects operator and reviewer expectations about safe failure handling. If the spec says escalation but the code terminalizes, a future implementer or reviewer could build/expect the wrong behavior.

**Success criteria:**
- D-02 classified as behavior-decision (not docs-only)
- Decision record in `decisions.md` naming the Packet 1 mechanism
- All spec authority owners aligned on the resolved behavior
- Drift report summary surfaces updated (five-surface pattern from D-01)
- T-20260429-02 preserved as the per-method classification forward reference
- Advisory-domain server-request handling explicitly deferred to D-03

**Connection to project arc:** This is the second of four prioritized findings from the drift cleanup sequence (D-01 done, D-02 done, D-03 next, D-07 after). The three-document status topology (current-state synthesis, reconciliation register, drift report) established in `docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md` governs how these findings flow through to operator-facing docs.

## Session Narrative

Loaded the handoff from the D-01 resolution session. The handoff outlined four next steps: D-02, D-03, D-07, and batch remaining findings. Started with D-02 per the priority order.

Read the six primary sources in parallel: the T-20260429-02 ticket (`docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md`), `decisions.md:122-124`, `contracts.md:354-360`, `recovery-and-journal.md:159-166`, the drift report's D-02 subsection, and the actual code at `delegation_controller.py:975-1089` and `approval_router.py`.

Initial analysis surfaced a three-way disagreement, not two-way:
1. `decisions.md:122-124` — "held and surfaced to Claude as escalations, never auto-approved"
2. `recovery-and-journal.md:160-163` — execution unknowns → `needs_escalation` → `codex.delegate.decide`
3. `contracts.md:358` — `unknown` cannot appear in `PendingEscalationView` under Packet 1, terminalizes instead

The code agreed with surface 3. Both code paths (parse failure at line 984 and known-parsed non-parkable at line 1072) terminalize as `unknown`. Neither transitions to `needs_escalation`.

Presented the three-way analysis to the user with the core question: "Is terminalization or escalation the intended contract?" Framed each side's case with code evidence.

**Key pivot:** User said the ticket (T-20260429-02) is closest to the intended behavior. This reframed the decision: neither blanket-terminalize nor blanket-escalate — the answer is per-method, and blanket terminalization is the correct Packet 1 default while per-method classification (the ticket) determines future dispositions.

User then proposed a tightening: "The durable D-02 decision should not be 'blanket terminalization forever.' It should be 'under Packet 1, persisted kind=unknown terminalizes; future work classifies each method.'" User's key insight: `decisions.md` preserves the right safety property (never auto-approved) but names the wrong mechanism (escalation instead of terminalization).

User provided extensive evidence including specific line citations across 8 files, the `DelegationOutcomeRecord` vs `AuditEvent` distinction (the code emits `DelegationOutcomeRecord(terminal_status="unknown")`, not an `action: escalate` audit event), and the request-status-differs-by-path nuance (parse-failure unknowns may stay `pending`; known-parsed non-parkable unknowns can be resolved by the finalizer).

I probed the user's reasoning for gaps and found four:
1. Advisory-domain reachability — advisory turns don't install a `server_request_handler`, so the advisory-domain clause in `recovery-and-journal.md` was speculative
2. What audit action the code actually emits (not `action: escalate` — it's a `DelegationOutcomeRecord`)
3. Replacement text shape for `recovery-and-journal.md` (needs positive claims, not just removals)
4. `spec.yaml` cross-review dependencies for the affected authorities

User closed all four gaps with additional evidence, plus discovered two surfaces I had missed:
- `foundations.md:113,184` still said unknowns → `needs_escalation` (P1 architecture-layer drift)
- `contracts.md:93` framed unknowns as "future App Server versions" only, missing current unsupported methods

User also found `SKILL.md:197` still had live unknown-kind escalation rendering guidance.

Created branch `docs/d02-unknown-request-terminalization`. Drafted the two anchor files first (`decisions.md` and `recovery-and-journal.md`), then applied the user's scrutiny findings to those drafts (P3 advisory reachability wording, P3 `requested_scope` filtering clarification). Then fixed P1 `foundations.md` (both lines 113 and 184), P2 `contracts.md:93` (broadened to current+future methods), and P2 `SKILL.md:197` (invariant-violation handling).

Second scrutiny round found three more issues: `contracts.md:304` only named one unknown path (parse failure), `contracts.md:358` still referenced the historical design spec instead of current owner docs, and `SKILL.md:197` advised premature `/delegate discard` while the job might still be in `needs_escalation`.

Third scrutiny round (full edit set) found two final issues: the D-02 drift report subsection had a stale fix-type line and smart quotes in `kind="unknown"`. Both fixed.

Committed at `129b7e3d`. Fast-forward merged to main. Branch deleted.

## Decisions

### D-02: Packet 1 intentionally terminalizes unknown requests

**Choice:** Under Packet 1, a persisted `kind="unknown"` `PendingServerRequest` terminalizes the delegation job as `unknown`. The request does not enter `PendingEscalationView` and is not resolved via `codex.delegate.decide`. The fail-closed invariant (never auto-approved) is preserved; the mechanism is terminalization, not escalation.

**Driver:** User: "My read: decisions.md is preserving the right safety property but the wrong mechanism. The architectural property is 'unknown requests are never auto-approved / fail closed.' The stale part is 'held and surfaced to Claude as escalations.'" Combined with ticket T-20260429-02 which frames terminalization as "can be safe as an intentional terminal state" and does not require escalation in its acceptance criteria.

**Rejected alternatives:**
- **Blanket escalation** (`decisions.md` + `recovery-and-journal.md` original) — would require per-method classification first to be useful. You can't usefully escalate to Claude until you know what Claude should do with each method kind. The escalation language overspecified for Packet 1.
- **Blanket terminalization forever** — too narrow. User tightened: "The durable D-02 decision should not be 'blanket terminalization forever.' It should be 'under Packet 1, persisted kind=unknown terminalizes; future work classifies each method.'"

**Implication:** T-20260429-02 remains open for per-method classification. Classified methods may be promoted to the parkable/supported set, proven as intentionally safe-terminal, or proven non-reachable in current flows. The decision does not foreclose escalation for specific methods that are later classified as needing it.

**Trade-offs accepted:** Terminalization is fail-safe (job stops) but not fail-closed-with-recovery (operator can't intervene). For Packet 1 this is acceptable because the unsupported methods haven't been classified yet — there's no actionable recovery path to offer.

**Confidence:** High (E2) — verified across 8+ code and spec surfaces. Both code paths (parse failure and known-parsed non-parkable) terminalize. Tests pin the behavior (`test_delegate_start_integration.py:614`). `PendingRequestKind` and `EscalatableRequestKind` are explicitly split in `models.py:19`.

**Reversibility:** High — the decision is recorded in `decisions.md §Unknown Request Kinds`. When T-20260429-02 classifies a specific method as needing escalation rather than terminalization, that method moves into the parkable set via a new `PendingRequestKind` value.

**Change trigger:** T-20260429-02 classifies a method that requires operator intervention rather than safe terminalization. The method would need a new kind value, supported escalation rendering in SKILL.md, and test coverage.

### Advisory-domain server-request handling deferred to D-03

**Choice:** D-02 does not resolve advisory-domain server-request handling. The `recovery-and-journal.md` replacement text explicitly says "Advisory-domain server-request handling described in advisory-runtime-policy.md is not validated by this contract and remains an unresolved spec-code divergence."

**Driver:** User: "I'd avoid touching advisory-runtime-policy.md in the D-02 draft, for the scope reasons you gave." D-03 spans 86 lines of `advisory-runtime-policy.md` (widening, narrowing, freezing, rotation, reap conditions). Advisory server-request resolution at lines 49 and 61 is woven into that larger policy narrative. Surgically removing it during D-02 risks leaving the surrounding text incoherent.

**Rejected alternative:** Fix `advisory-runtime-policy.md` during D-02. Rejected because D-02 decides "what happens to unknown requests" (terminalization vs escalation) while D-03 decides "is advisory policy widening/rotation active or deferred" (active spec text vs code rejection). The advisory-domain unknown handling falls under D-02, but the advisory server-request resolution in `advisory-runtime-policy.md` falls under D-03.

**Implication:** D-03 must account for the advisory-domain non-validation note when it resolves. A future reader of `recovery-and-journal.md` is explicitly told not to infer D-02 validated the advisory-policy text.

**Trade-offs accepted:** One more session of advisory-policy drift remaining. Contained by the explicit deferral note.

**Confidence:** High (E1) — directly driven by user's scope analysis. Verified that advisory turns do not install a `server_request_handler` (`control_plane.py:194`, `runtime.py:160`, `runtime.py:262`).

**Reversibility:** High — D-03 will resolve this.

**Change trigger:** D-03 work begins.

### Record D-02 decision in spec-local `decisions.md`

**Choice:** Revise the existing "Unknown Request Kinds" section in `decisions.md` with the full decision record, following the D-01 precedent.

**Driver:** Same routing as D-01: `current-state.md:16` routes behavioral truth to the spec, `current-state.md:44` maps `decisions` authority to the spec-local file.

**Rejected alternative:** Create a standalone `docs/decisions/` record. Rejected for the same reason as D-01 — it would be orphaned for codex-collaboration readers whose discovery path goes through the spec.

**Implication:** Consistent with D-01 routing. Future codex-collaboration decisions continue to use the spec-local `decisions.md`.

**Trade-offs accepted:** Monorepo-wide decision search misses this record unless someone reads the spec. Acceptable because the decision is codex-collaboration-specific.

**Confidence:** High (E1) — follows established routing from D-01 decision.

**Reversibility:** High — could move to `docs/decisions/` with a cross-link if needed.

**Change trigger:** If a monorepo-wide decision index is created.

## Changes

### `docs/superpowers/specs/codex-collaboration/decisions.md` — §Unknown Request Kinds revision

**Purpose:** Replace the stale 3-line "held and surfaced as escalations" text with the full Packet 1 terminalization decision.

**Approach:** Three paragraphs: (1) invariant statement (never auto-approved, mechanism-independent), (2) Packet 1 mechanism (terminalize, not escalate, with artifact chain), (3) forward reference to T-20260429-02 and cross-link to `recovery-and-journal.md`.

**Key details:**
- Kept `**Resolved.**` prefix per user's shape guidance
- Named the artifact chain explicitly: `PendingServerRequest(kind="unknown")` + `DelegationOutcomeRecord(outcome_type="delegation_terminal", terminal_status="unknown")`
- Named what `unknown` does NOT do: does not enter `PendingEscalationView`, not resolved via `codex.delegate.decide`

### `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` — §Unknown Request Handling rewrite

**Purpose:** Replace the stale escalation-based handling with the actual terminalization behavior, including the two-path diagnostic distinction.

**Approach:** Five paragraphs: (1) execution-only scoping with advisory N/A note, (2) terminal behavior statement, (3) two code paths as bullet points, (4) fail-closed invariant (preserved verbatim), (5) artifact correction + forward reference.

**Key details:**
- Advisory scoping: "server-request handling is implemented only in execution-domain turns" (not "received only in" — P3 fix for overstatement)
- Advisory non-validation note: "not validated by this contract and remains an unresolved spec-code divergence"
- Parse failure path: minimal record, empty context, `raw_method` only, may remain `pending`
- Known-parsed non-parkable path: full context, "non-context `requested_scope` (context keys are stripped by the parser into dedicated fields)" (P3 fix for filtering)
- No `action: escalate` audit event — explicitly stated

### `docs/superpowers/specs/codex-collaboration/foundations.md` — Architecture-layer alignment

**Purpose:** Fix the `foundation` authority owner (which owns architecture rules per `spec.yaml:5`) so it no longer says unknowns become `needs_escalation`.

**Approach:** Two edits:
- Line 113 capability table: "become `needs_escalation` job state" → "terminalize job as `unknown`" with decision cross-link
- Line 184 delegation flow step 5: now distinguishes supported kinds (parked for `codex.delegate.decide`) from unsupported kinds (terminalize as `unknown`)

**Key detail:** Because `foundation` triggers cross-review of all contract/policy owners per `spec.yaml:94`, this edit validates the consistency of the other authority owners. The delegation flow now accurately describes both paths in a single sentence.

### `docs/superpowers/specs/codex-collaboration/contracts.md` — Three targeted fixes

**Purpose:** Align contracts with the terminalization decision across three locations.

**Approach:**
- Line 93 (`PendingServerRequest` kind description): Broadened from "Unrecognized server request types from future App Server versions" to "Unsupported or unrecognized server request methods — whether from the current App Server schema or future versions." Added explicit Packet 1 terminalization statement.
- Line 304 (start outcomes table): Renamed from "Unknown-kind parse failure" to "Unknown-kind terminalization" noting it covers both paths, with cross-link to `recovery-and-journal.md`.
- Line 358 (`PendingEscalationView` kind field): Replaced stale "see §Unknown-kind contract in the design spec" with cross-links to current owner docs (`decisions.md` and `recovery-and-journal.md`).

### `packages/plugins/codex-collaboration/skills/delegate/SKILL.md` — Escalation rendering fix

**Purpose:** Mark the unknown-kind escalation rendering row as unreachable under Packet 1.

**Approach:** Changed from normal rendering guidance ("Render raw requested_scope JSON") to invariant-violation handling. The guidance now says: unreachable under Packet 1, if encountered treat as invariant violation, do NOT approve or deny, poll/inspect until terminal state, then advise `/delegate discard`.

**Key detail:** Original P2 fix advised immediate `/delegate discard`, but the user's scrutiny caught that if an unknown kind somehow reached the escalation renderer, the job would likely still be in `needs_escalation` — making `discard` reject. The final guidance waits for terminal state before advising discard.

### `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md` — Six-surface treatment

**Purpose:** Apply the D-01/D-04 five-surface update pattern (plus subsection annotation = six surfaces) to mark D-02 as addressed.

**Approach:** Six edits:
1. D-02 subsection: addressed-status annotation with commit list and scope
2. Executive verdict (line 28): D-02 added to addressed list, D-03 now the sole remaining contradiction
3. Highest-risk drifts (line 30): D-02 struck with resolution note
4. Findings table (line 66): D-02 row updated to `addressed`/`resolved` with expanded files list
5. Section 7 stale docs (line 156): D-02 struck from open list
6. Repair order (line 163): D-02 struck with resolution note

**Key details:**
- Fix-type line updated from stale "possible code/test follow-up if escalation is intended" to "resolved via behavior-decision"
- Smart quotes in `kind="unknown"` replaced with straight quotes (byte-level fix via sed)

## Codebase Knowledge

### The three-way D-02 disagreement — where each claim lived

| Surface | Claim | Location |
|---------|-------|----------|
| `decisions.md` | "held and surfaced to Claude as escalations" | line 124 (now revised) |
| `recovery-and-journal.md` | execution unknowns → `needs_escalation` → `codex.delegate.decide` | lines 160-163 (now rewritten) |
| `contracts.md` | `unknown` cannot appear in `PendingEscalationView`, terminalizes instead | line 358 (was correct, back-reference updated) |
| Code (parse failure) | minimal `PendingServerRequest(kind="unknown")`, interrupt, terminalize | `delegation_controller.py:984-1070` |
| Code (known-parsed non-parkable) | full-context `PendingServerRequest(kind="unknown")`, interrupt, terminalize | `delegation_controller.py:1072-1089` |
| Test | pins unknown permissions as terminal `status="unknown"` | `test_delegate_start_integration.py:614` |
| Models | `PendingRequestKind` and `EscalatableRequestKind` explicitly split | `models.py:19` |

### Terminal artifact chain for unknown requests

The code does NOT emit an `action: escalate` `AuditEvent` for unknown terminalization. The actual terminal evidence is:
1. Persisted `PendingServerRequest(kind="unknown")` — the causal record
2. `DelegationOutcomeRecord(outcome_type="delegation_terminal", terminal_status="unknown")` — emitted by `_emit_terminal_outcome_if_needed` at `delegation_controller.py:1472`

This distinction matters for D-07 (audit schema alignment): the audit event model and the outcome record model are separate artifact types. The D-02 replacement text correctly names the outcome record, not an audit event.

### Request-status lifecycle differs by code path

| Path | Diagnostic quality | `PendingServerRequest` status |
|------|--------------------|-------------------------------|
| Parse failure | Minimal: empty context, `raw_method` only | May remain `pending` (`test_delegate_start_async_integration.py:163`) |
| Known-parsed non-parkable | Full: preserved context fields, filtered `requested_scope` | Finalizer may mark `resolved` (`test_delegate_start_integration.py:653`) |

The `requested_scope` in the known-parsed path is NOT the raw `params` object — `approval_router.py:14` strips `_REQUEST_CONTEXT_KEYS` (`itemId`, `threadId`, `turnId`, `availableDecisions`) into dedicated fields on the `PendingServerRequest`.

### Advisory-domain server-request handling is not implemented

Advisory turns do not install a `server_request_handler`:
- `control_plane.py:194` — consult path starts read-only turn
- `runtime.py:160` — advisory `_run_turn` has no handler installation
- `runtime.py:262` — only execution `_run_turn` installs handlers

`advisory-runtime-policy.md:49,61` still describes advisory server-request resolution. This text is not validated by D-02 and remains an unresolved spec-code divergence for D-03.

### `spec.yaml` cross-review dependencies applied

| Authority changed | Cross-review triggered | Verified |
|-------------------|----------------------|----------|
| `decisions` | No explicit cross-review rule in `spec.yaml:49` | N/A |
| `foundation` | All contract/policy owners per `spec.yaml:94` | Yes — checked `contracts`, `recovery-contract`, `advisory-policy` |
| `contracts` | `recovery-contract`, `advisory-policy`, `promotion` per `spec.yaml:89` | Yes — `recovery-contract` co-edited; `advisory-policy` deferred to D-03 |
| `recovery-contract` | `contracts` per `spec.yaml:89` | Yes — `contracts` co-edited |

### Five-surface drift report update pattern (now six-surface)

When addressing a drift finding, update these surfaces in the same commit:

1. **Subsection annotation** — addressed-status blockquote with commit citations
2. **Executive verdict** (Section 2) — overall consistency assessment
3. **Highest-risk drifts** (Section 2) — bullet naming the finding
4. **Findings table** (Section 6) — row with severity/status/action
5. **Section 7 stale docs list** — bullet listing the finding
6. **Repair order** (Section 8) — step referencing the finding

Plus the fix-type line inside the subsection (learned from D-02 critique round 3 — the subsection body can contain stale action guidance even after the annotation is added).

## Context

### Drift-synthesis-recovery status topology

Same as previous session. Three current-facing status documents operate under the topology defined in `docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md`:

- **Current-state synthesis** (`docs/status/codex-collaboration-current-state.md`): reader entry point
- **Reconciliation register** (`docs/status/codex-collaboration-reconciliation-register.md`): bounded index of unresolved work
- **Drift report** (`docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`): supporting evidence, not authoritative

### D-02 compared to D-01

Both D-01 and D-02 were behavior-decisions, not docs-only cleanup. The shared diagnostic: when code and spec disagree, check whether the spec describes a tool name (docs-only) or a safety/architectural property (behavior-decision).

| Dimension | D-01 (fork drift) | D-02 (unknown request handling) |
|-----------|-------------------|----------------------------------|
| Outcome shape | Keep architectural property, change implementation surface | Keep safety invariant, align mechanism |
| Decision | Branchable via copy-and-diverge | Terminalize under Packet 1 |
| Critique rounds | 3 (Major → Minor → Minor) | 3 (Minor: P3s → P2+P3s → P2+P3) |
| Authority owners touched | 5 of 8 | 4 of 8 (plus SKILL.md) |
| Commits | 6 | 1 (single commit after all critique rounds) |
| Advisory-domain impact | None | Explicitly deferred to D-03 |

### The "right safety property, wrong mechanism" pattern

User's framing for D-02: `decisions.md` preserves the right safety property (never auto-approved) but names the wrong mechanism (escalation). The code implements a different mechanism (terminalization) that also satisfies the invariant. The decision records which mechanism Packet 1 uses without foreclosing the other for future methods that T-20260429-02 classifies.

This pattern may recur: when a spec text names a specific mechanism for a safety property, verify that the mechanism is current, not just the property.

## Learnings

### The same drift class repeats — but this session caught it earlier

**Mechanism:** D-01 took three critique rounds to catch current-vs-deferred tense leaks. D-02 took three critique rounds too, but the tense issues were caught earlier (P3 severity, not P1/P2). The improvement came from applying the D-01 tense test proactively: "does this replacement text describe only what exists today?"

**Evidence:** The P3 advisory reachability wording and `requested_scope` filtering were caught in the first scrutiny pass, not after commit.

**Implication:** The tense test is becoming internalized. Future findings should have even fewer tense-related critique issues.

**Watch for:** D-03 will have the highest tense-leak risk — 86 lines of `advisory-runtime-policy.md` describe active behavior that code rejects.

### `DelegationOutcomeRecord` is the terminal artifact, not `AuditEvent`

**Mechanism:** Unknown terminalization emits `DelegationOutcomeRecord(outcome_type="delegation_terminal", terminal_status="unknown")` via `_emit_terminal_outcome_if_needed`. The spec's claim of `action: escalate` `AuditEvent` was doubly wrong: wrong action AND wrong artifact type.

**Evidence:** `delegation_controller.py:1472`, `models.py:242`. The Packet 1 design spec confirms at `2026-04-23-deferred-approval-response-design.md:1726,1740`.

**Implication:** D-07 (audit schema alignment) must account for this distinction. The audit event model and the outcome record model are separate artifact types with different emission patterns.

**Watch for:** Any future spec text that says "an audit event is emitted" — verify which artifact type the code actually produces.

### Stale fix-type guidance persists even after annotation

**Mechanism:** Adding an addressed-status annotation to a drift report subsection does not update the subsection's local body text. The D-02 fix-type line still said "possible code/test follow-up if escalation is intended" after the annotation was added. A reader scanning the subsection (not just the annotation) would get stale action guidance.

**Evidence:** Caught in scrutiny round 3 at `drift-report.md:93`.

**Implication:** The five-surface checklist should be expanded: after updating the five summary surfaces, also check the subsection's local body for stale action/guidance text. This is now a six-surface checklist.

**Watch for:** D-03 and D-07 subsection bodies when they're addressed.

### Smart quotes in code literals

**Mechanism:** The Edit tool's string comparison can normalize smart quotes (`“`, `”`) to straight quotes, making the replacement silently match even when the file contains the wrong characters. The file on disk retains the smart quotes unless fixed via byte-level sed.

**Evidence:** `kind="unknown"` in the addressed-status note had `e2 80 9d` (U+201D) bytes, but `Edit` reported "no changes" when given the straight-quote version.

**Implication:** After any Edit that writes code literals inside markdown, verify with `xxd` or `grep -P` that quote characters are straight, not curly.

**Watch for:** Any handoff or annotation text that includes code identifiers in backtick spans.

## Next Steps

### 1. Decide D-03 (advisory widening) — behavior-decision

**Dependencies:** None — independent of D-02, though D-02's advisory non-validation note feeds into it.

**What to read first:** Audit's D-03 entry at `drift-report.md:95`. Then: `advisory-runtime-policy.md:32-118`, `control_plane.py:151-158`, `profiles.py:148-158`. The register's `ADVISORY-WIDENING-ROTATION` row. D-02's advisory non-validation note at `recovery-and-journal.md:160`.

**Approach:** Same pattern as D-01 and D-02 — the advisory-widening text describes active policy behavior but code rejects it. Is this deferred-future-scope (edit docs to mark as future, keep the spec text for when it lands) or cancelled (remove the spec text)?

**Acceptance criteria:** Decision record in `decisions.md`, spec edits across affected authority owners (check `spec.yaml` cross-review deps), five-surface + fix-type update in drift report. Advisory-domain server-request handling from D-02's deferral note resolved.

**Potential obstacles:** D-03 spans 86 lines of `advisory-runtime-policy.md` (lines 32-118). If the decision is "mark as future-scope," the edit scope is large — 86 lines of active-behavior prose that needs annotation or restructuring. More complex than D-02's surgery.

### 2. Land D-07 (audit schema alignment) — most expensive

**Dependencies:** Should account for D-02's `DelegationOutcomeRecord` vs `AuditEvent` distinction. Should also account for D-03 if resolved (may affect audit actions).

**What to read first:** Audit's D-07 entry. `contracts.md:188-223` (audit schema), `recovery-and-journal.md:104-120` (write triggers), `models.py:202-217` (AuditEvent dataclass), `delegation_controller.py` (emission sites), `skills/codex-analytics/SKILL.md` (consumer docs).

**Approach:** Reconcile audit-event field set across spec and dataclass. Reconcile action enumeration (13 in contracts vs 7 in analytics skill). Decide which is canonical and align all artifacts.

**Acceptance criteria:** AuditEvent dataclass, contract spec, recovery write triggers, and analytics skill all agree on field set and action enumeration.

**Potential obstacles:** Multi-artifact and touches code (`models.py`, `delegation_controller.py`). May require tests. Most expensive cleanup item by far. The D-02 outcome-vs-audit distinction adds a new reconciliation dimension.

### 3. Batch remaining findings (D-05, D-06, D-08, D-09)

**Dependencies:** D-05 (closed-in-root tickets) is independent. D-06 (delegate skill file_change visibility) is independent. D-08 (package README skill list) is independent. D-09 (diagnostic TTL prose) is independent.

**Approach:** Lower-risk, can be batched. D-05 requires ticket moves or supersession notes. D-06 and D-08 are doc edits. D-09 is a supersession note or doc edit.

## In Progress

Clean stopping point — all D-02 work completed, committed, and merged to main. No work in flight.

## Open Questions

### Should D-03 be resolved before D-07?

Same question from the previous handoff, now with D-02 evidence. D-07 touches `contracts.md` audit actions and `recovery-and-journal.md` write triggers — the same surfaces that D-03 may affect. If D-03 changes the advisory-policy scope, that could add or modify audit actions relevant to advisory-domain events. D-02's advisory deferral note explicitly says the advisory text "remains an unresolved spec-code divergence," which D-03 must resolve.

The handoff's ordering already puts D-03 before D-07. The D-02 outcome reinforces this as a hard dependency: D-03 must resolve the advisory-domain server-request handling before D-07 can reconcile the full audit schema.

### Is the six-surface update pattern worth codifying?

Updated from previous handoff: now six surfaces, not five (subsection fix-type line added after D-02 critique). The pattern was learned by failure three times (D-04, D-01, D-02). The drift report is a one-time artifact, but D-03 and D-07 still need the same treatment. At minimum it should be a mental checklist for the remaining findings.

## Risks

### D-03 edit scope is larger than D-01 or D-02

D-03 spans 86 lines of `advisory-runtime-policy.md`. If the decision is "mark as future-scope," each of those lines needs annotation or restructuring. D-01 touched ~20 lines across 5 files. D-02 touched ~30 lines across 6 files. D-03 could be 86+ lines in a single file plus cross-review surfaces. **Mitigation:** Consider whether the file's structure allows sectional annotation (e.g., a "Future-scope: this section describes planned behavior not yet implemented" header) rather than line-by-line editing.

### D-07 scope growth from D-02's outcome-vs-audit distinction

D-02 established that unknown terminalization emits a `DelegationOutcomeRecord`, not an `AuditEvent`. D-07 must reconcile the audit schema — but now it also needs to reconcile the boundary between audit events and outcome records. If these two artifact types have overlapping fields or action values, D-07's scope grows. **Mitigation:** The D-02 text explicitly names both artifact types, giving D-07 a stable target.

### Advisory-domain drift accumulation across three findings

D-02 deferred advisory-domain server-request handling to D-03. But D-07 may also affect advisory-domain audit events. If D-03 and D-07 both touch advisory-policy surfaces, there's a risk of editing the same lines in sequence with different assumptions. **Mitigation:** Resolve D-03 first (hard dependency now, not preference). D-07 gets a stable advisory-policy baseline to work from.

## References

- **Verification audit:** `docs/audits/2026-04-29-codex-collaboration-status-verification.md`
- **Drift report:** `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`
- **Decision record:** `docs/superpowers/specs/codex-collaboration/decisions.md §Unknown Request Kinds`
- **Operational contract:** `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md §Unknown Request Handling`
- **Spec authority model:** `docs/superpowers/specs/codex-collaboration/spec.yaml`
- **T-20260429-02 ticket:** `docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md`
- **Previous handoff:** `docs/handoffs/archive/2026-04-29_23-59_codex-collaboration-drift-cleanup-d01-resolution.md`
- **Commit:** `129b7e3d` (D-02 resolution, all 6 files, single commit)

## Gotchas

### Smart quotes survive Edit tool normalization

The Edit tool's string comparison normalizes Unicode quote characters, so `old_string` and `new_string` can appear identical even when the file has smart quotes and you're providing straight quotes. The edit succeeds with "no changes" — the file on disk retains the wrong characters.

**For future-Claude:** After any Edit that writes code identifiers (function names, enum values, status strings) inside markdown backtick spans, verify with `sed -n '<line>p' <file> | xxd | grep 'e2.80'` that no smart quotes leaked in. Fix with `sed -i ''` using hex escapes if found.

### `spec.yaml` cross-review has no `decisions` trigger

Unlike `foundation` (which triggers all owners) and `contracts` (which triggers recovery/advisory/promotion), `decisions` has no `on_change_to` boundary rule in `spec.yaml:49`. This means editing `decisions.md` alone does NOT trigger automated cross-review. The cross-review obligation falls on the author to check whether the decision affects other authority owners.

**For future-Claude:** When adding or revising a decision record in `decisions.md`, manually check all authority owners whose behavior the decision governs. For D-02, this was `foundation`, `contracts`, `recovery-contract`, and the operator skill.

### Stale body text inside addressed drift-report subsections

Adding an addressed-status annotation (blockquote at the top of a subsection) does not neutralize the subsection's local body text. Lines like "Fix type: source doc edit plus possible code/test follow-up if escalation is intended" remain as stale action guidance that a reader scanning the full subsection will encounter.

**For future-Claude:** After adding an addressed-status annotation, also update the fix-type line and any other action guidance in the subsection body. This is now part of the six-surface checklist, not a separate step.

## Conversation Highlights

**On the three-way disagreement:**
Claude surfaced a three-layer analysis (decisions.md, recovery-and-journal.md, contracts.md all saying different things). User confirmed: "Yes. I agree with your shape, with one tightening: the durable D-02 decision should not be 'blanket terminalization forever.'"

**On the ticket as the intended behavior:**
User: "The ticket is closest to the intended behavior."
— Reframed D-02 from a binary (terminalize vs escalate) to per-method classification with Packet 1 terminalization as the default.

**On the safety property vs mechanism distinction:**
User: "My read: decisions.md is preserving the right safety property but the wrong mechanism. The architectural property is 'unknown requests are never auto-approved / fail closed.' The stale part is 'held and surfaced to Claude as escalations.'"
— This framing anchored the entire decision.

**On the DelegationOutcomeRecord discovery:**
User: "The current replacement artifact is not an AuditEvent. For unknown terminalization, the code calls _emit_terminal_outcome_if_needed, which writes a DelegationOutcomeRecord(outcome_type='delegation_terminal', terminal_status='unknown'), not an audit event action."
— Caught a gap I had not identified, with specific line citations to `delegation_controller.py:1472` and `models.py:242`.

**On probing for gaps:**
User provided evidence across 8 files in a single message, including the `foundations.md` surfaces I had missed and the advisory-domain non-validation boundary. User: "Probe for gaps in my reasoning. Where is it weak? What nuances did I overlook?"
— Collaborative gap-finding pattern: Claude probes first, user closes gaps with code evidence.

**On the advisory-domain boundary:**
User accepted the D-03 deferral: "I'd avoid touching advisory-runtime-policy.md in the D-02 draft, for the scope reasons you gave. The only caveat is that the D-02 change should explicitly say that advisory-policy server-request text remains unresolved under D-03."

**On critique methodology:**
Three scrutiny rounds with structured findings (priority, confidence, title, body, file, start line). Each round was more surgical than the previous. Verdict labels: implied Minor → Minor → Minor (no Major revision needed, unlike D-01).

## User Preferences

**Collaborative gap-finding:** User explicitly asked "Probe for gaps in my reasoning. Where is it weak?" then closed every gap with code evidence. This is a collaborative investigation pattern: Claude identifies structural gaps, user provides implementation evidence.

**Evidence-dense proposals:** User's messages included specific file:line citations for every claim, often across 8+ files in a single message. Proposals are grounded in code, not reasoning alone.

**Shape guidance before drafting:** User said "For decisions.md, I'd target this shape: [5 bullet points]" and "For recovery-and-journal.md, the replacement should be positive and operational: [6 bullet points]." Prefers setting the target shape, then reviewing the draft against it.

**Scrutiny-driven iteration:** Same pattern as D-01 sessions — produce → scrutinize → fix → re-scrutinize. Findings use structured format with priority, confidence, file, and line number.

**Scope containment over completeness:** User chose to defer advisory-policy cleanup to D-03 rather than touching it during D-02, even though the advisory-domain text was known to be stale. Prefers clean scope boundaries over opportunistic fixes.

**Single-commit preference (D-02 vs D-01):** D-01 took 6 commits across 3 critique rounds. D-02 was a single commit after all critique rounds resolved. Not explicitly stated as a preference, but user approved the commit only after all findings were closed, suggesting a preference for atomic commits when possible.

**Direct action after alignment:** User: "Approved to commit" with a clean summary of what was checked. No hedging or re-confirmation — same pattern as D-01 sessions.

## Rejected Approaches

### Treating D-02 as a docs-only fix

**Approach:** Edit `decisions.md` and `recovery-and-journal.md` to say "terminalize" instead of "escalate," treating it as stale docs matching to current code.

**Why it seemed promising:** The code terminalizes. Tests pin it. `contracts.md` already says terminalize. Simple find-and-replace.

**Specific failure:** The escalation language in `decisions.md` describes a safety property ("never auto-approved") via a specific mechanism ("held and surfaced as escalations"). Just swapping "escalation" for "terminalization" would miss the architectural distinction: the invariant is the safety property, and the decision is about which mechanism implements it. A docs-only fix would not record why terminalization was chosen over escalation, what T-20260429-02 preserves, or how per-method classification evolves the contract.

**What it taught:** Same lesson as D-01: when the spec text describes a safety/architectural property, not just a tool name, the fix is a behavior-decision, not a docs-only cleanup.

### Editing advisory-runtime-policy.md during D-02

**Approach:** Surgically remove advisory server-request resolution from `advisory-runtime-policy.md:49,61` during the D-02 edit set.

**Why it seemed promising:** D-02 established that advisory turns don't install a `server_request_handler`. The advisory server-request text is demonstrably unreachable. Why leave it stale?

**Specific failure:** Advisory server-request resolution is woven into the larger advisory-policy narrative (widening, narrowing, freezing, rotation — lines 32-118). Removing lines 49 and 61 without the D-03 decision on the surrounding text would leave the policy narrative incoherent — a partial fix that creates a new drift class.

**What it taught:** Scope containment is more valuable than completeness when the surrounding text requires its own behavior-decision. The deferral note ("not validated by this contract") is cheaper and safer than a partial surgical fix.
