---
date: 2026-04-23
time: "17:55"
created_at: "2026-04-23T17:55:24Z"
session_id: 772acaa7-baf7-4b6d-8faf-ffc9ed5d404c
resumed_from: "docs/handoffs/archive/2026-04-23_16-23_delegate-boundary-tightening-shipped.md"
project: claude-code-tool-dev
branch: feature/delegate-exec-policy-amendment
commit: edff9c07
title: "Exec-policy amendment design — brainstorm synthesis committed to fresh branch"
type: handoff
files:
  - docs/superpowers/specs/2026-04-23-exec-policy-amendment-design.md
---

# Handoff: Exec-policy amendment design — brainstorm synthesis committed to fresh branch

## Goal

Execute the "exec-policy design packet" queued by the predecessor handoff (`2026-04-23_16-23_delegate-boundary-tightening-shipped.md`) as the next major work on delegation. Trigger: user explicitly confirmed "This IS the fresh session" after `/load` surfaced the predecessor's recommended next action ("Start the exec-policy design packet in a fresh session").

**Stakes:** High — ticket T-20260423-01's AC1 (end-to-end delegation with platform-tool verification) is blocked on this design. PR #125 merged the state-machine hardening + boundary tightening but explicitly deferred `acceptWithExecpolicyAmendment` handling to a follow-up trust-boundary design. This session IS that trust-boundary design.

**Success criteria:**
- Brainstorm through all 5 open questions from the predecessor handoff (+ additional questions that surface).
- Resolve scope, eligibility, approval affordance, persistence, audit, state-machine integration, diagnostic-gate shape.
- Produce a coherent, internally-consistent design document on a fresh branch off `main`.
- Reach a clean stopping point for user review before writing the implementation plan.

**Connection to project arc:** This design is the actual T-20260423-01 closure path. PR #125 produced the invariants (deny-only contract, resolution-class-ready state machine); this packet adds the narrow amendment exception that lets happy-path delegation execute its verification commands. If Phase 1's diagnostic gate confirms App Server accepts the amendment response, Phases 2-3 close AC1.

## Session Narrative

### 1. Resume, intent confirmation, brainstorming skill

Session started with `/load`, archived `2026-04-23_16-23_delegate-boundary-tightening-shipped.md` from the handoffs directory. The predecessor's "Immediate next action on resume" was to start the exec-policy design packet in a fresh session. Offered two paths to the user: start the design work in this session, or spin up a fresh branch and session. User's response: **"This IS the fresh session."** Clear mandate.

Invoked `superpowers:brainstorming` before any other work, per the skill-discipline protocol. This was unambiguously creative design work, not implementation. Skill required: explore context → clarifying questions (one at a time, multiple choice preferred) → 2-3 approaches with trade-offs → present design sections → write spec → self-review → user review → transition to `writing-plans`.

### 2. Context exploration (Task 1)

Read in parallel: PR #125 body via `gh pr view`, `approval_router.py` (current state post-PR #125), ticket T-20260423-01 (including Scope Limitations), `delegation_controller.py:640-760` (request handler), and git state. All read to ground the design in the actual repo state, not predecessor-handoff inferences.

Key facts absorbed:
- Post–PR #125, `is_within_delegation_boundary` for `command_approval` always returns `False` (unconditional).
- `_AVAILABLE_DECISIONS["command_approval"]` defaults include `acceptWithExecpolicyAmendment` and `applyNetworkPolicyAmendment` but the wire may emit any subset, including `[]`.
- Ticket's Scope Limitations section explicitly names `acceptWithExecpolicyAmendment` handling + amendment persistence + `available_decisions` representation + `/delegate approve` semantics as "out of scope, deferred to a follow-up trust-boundary design" — this session IS that follow-up.
- Wire evidence from predecessor live smoke: `command_approval` with `available_decisions: []` + `proposedExecpolicyAmendment: ["rg", "--files", ...]`. App Server parses the `/bin/zsh -lc` wrapper and names the inner command as the amendment target.

### 3. Seven brainstorming questions with iterative refinement

Drove through seven clarifying questions, each offering 2-4 options with a recommended choice and trade-offs. User refined every recommendation and frequently cited repo files with line numbers to push back.

| # | Question | Options offered | My recommendation | User's decision |
|---|---|---|---|---|
| 1 | Scope of packet | A (minimum auto-accept) / B (medium: auto + operator-approved) / C (broad full framework) | A | **Narrower-B** (drop auto-accept entirely; operator-approved only, prompt-allowlist-bounded) |
| 2 | Contract interpretation | X (explicit revision) / Y (hold fixed, upstream-ticket) | X + diagnostic gate | **X** accepted with diagnostic gate — with the user's refinement that live wire evidence is a "provisional signal" that justifies the gate, not a resolved reading |
| 3 | Eligibility model | A (exact-argv allowlist) / B (path-prefix) / C (prompt-subset verbatim) / D (trust App Server's proposal) | A | **C-prime** (structured plugin-owned allowlist distinct from but aligned with prompt; exact `argv[0]` match; reject trampolines/pivots/path-escapes) |
| 4 | Approval affordance | X (same `/delegate approve` + warning) / Y (distinct verb) / Z (flag gate) | Y | **Y** — distinct `approve_amendment` decide verb |
| 5 | Amendment persistence | A (trust App Server cache) / B (per-job) / C (per-session) / D (cross-session) | A | **A-plus** — trust App Server as only policy cache; plugin memory audit-only, not decision-making |
| 6 | Audit shape | X (distinct decision in existing stream) / Y (dedicated structured record) | Y | **Y** — dedicated `AmendmentApprovalRecord`, with user's refinement to drop `operator_identity` (not sourceable) and use `allowlist_entry_id + allowlist_version` (not full snapshot) |
| 7 | State-machine integration | A (branch inside Option B's empty-decisions path) / B (new job status) / C (decide-time-only dispatch) | A | **A-prime** — shared resolution-class classifier used by `_finalize_turn`, `_project_request_to_view`, `decide()`; no new job status; explicit routing rule |
| 8 | Diagnostic gate observations | A (1 observation) / B (2) / C (3) | B | **B-plus** — 2 observations + negative control if cheap |

Every user correction came with cited repo lines (e.g., `delegation_controller.py:1547`, `contracts.md:325`, `CommandExecutionRequestApprovalResponse.json:13`). This was not hand-waving pushback — it was codebase-authority-grounded sharpening.

### 4. Design presentation in six sections

Presented the design in sections per the brainstorming skill's section-by-section-approval pattern. User made substantive corrections to every section:

**Section 1 (Goal, scope, contract revision):** Three wording corrections — soften goal ("contingent on Phase 1"), frame contract revision as "conditional exception" not "narrowed rule," describe interpretation basis as "provisional signal" to preserve tension with docs.

**Section 2 (Architecture):** Four corrections — classifier returns `ResolutionResult` struct not bare enum (or downstream sites recompute); `_project_request_to_view` uses fresh re-classification not capture-time; classifier lives in its own module (not controller-local helper); soften "drift structurally impossible" to "drift directly testable" + make routing invariant explicit.

**Section 3 (Components):** Four corrections — store layout is session-scoped at `plugin_data_path / amendment_approvals / <session_id> / records.jsonl` (mirroring existing `pending_request_store` pattern, not per-job); collapse `wire_request_id + captured_request_id` to one `request_id`; path-safety needs to handle relative `..` traversal (adopted "preferred" path: resolve absolute AND relative against request cwd, shrink v1 allowlist to 4 precisely-validatable entries); version-bump enforcement needs content fingerprint (SHA-256), not entry count.

**Section 4 (Data flow + state machine):** Five corrections — (P1) `_finalize_turn` needs handler-disposition signal on `PendingServerRequest`, not just classifier output; (P1) explicit job-status transitions for blocking path (`running → needs_escalation` before block, `needs_escalation → running` on approve, `→ failed + null` on deny/timeout, `→ failed + discarded` on discard); (P2) deny signal is `{"decision": "cancel"}` not `"decline"` (matches existing `/delegate deny` terminal-fail contract); (P2) transport-prerequisite subsection added to acknowledge the blocking-resolution gap explicitly.

**Section 5 (Failure modes):** Two small corrections — drop the "schema-validated before send" row (no such layer); cold-start reconciliation currently produces `unknown` not `failed` (if amendment wants different, that's a separate recovery-contract change); narrow `AmendmentApprovalRecord` emission to `{applied, error}` only — timeouts/deny/discard flow through existing audit streams, not amendment records.

**Section 6 (Testing + rollout):** Three substantive corrections — Phase 0 must include a minimal vertical slice (not just infrastructure) so Phase 1 gate has something to drive through; drop feature-flag mechanism (no existing plugin-local flag pattern; git-as-gate is cleaner); soften ticket-update wording ("AC matrix + Scope Limitations updated with diagnostic outcome" not "closing AC1"). Two bookkeeping — integration file is `test_delegate_start_integration.py` not `test_delegate_integration.py`; MCP tool schema change requires naming `mcp_server.py` + `test_mcp_server.py` in deliverables.

### 5. Spec write

After Section 6's corrections landed, user confirmed: "the design is coherent enough to write the spec."

Branched from `main` at HEAD (current: 5 commits ahead of `main`'s previous state from earlier merges). Created `feature/delegate-exec-policy-amendment`. Wrote single spec file at `docs/superpowers/specs/2026-04-23-exec-policy-amendment-design.md` — 805 lines, covering goal/scope/contract-revision, architecture, components, data flow + state machine, transport prerequisite, failure modes + invariants, testing plan, phased rollout, deliverables, open questions, non-goals, references.

Self-review pass per brainstorming skill (placeholder scan, internal consistency, scope check, ambiguity check) found no issues to fix inline:
- No placeholders except the legitimate "implementation plan path TBD" (set by `writing-plans` skill later) and the implementation-plan scoping flagged in Open Questions #5.
- Cross-section consistency checks passed: classifier scope cancel-capable-only, capture-time-vs-fresh-reclassification split, record emission rule (`applied`/`error` only), v1 allowlist of 4 entries, `approve_amendment` verb — all aligned.
- Scope check: single implementation plan's worth of work; Phases 0-3 sequenced.
- Ambiguity check: typed callables, named defaults with configuration mechanisms, no interpretable-two-ways phrasing.

Committed as `edff9c07` — *design: exec-policy amendment support for delegation*.

### 6. Post-write handoff option

Hook emitted additional context noting the file's 805 lines exceed 500 and suggesting `/superspec:spec-writer` for modularization. Presented this to the user as Option 2 (modularize before review) vs Option 1 (review single-file as-is). User selected **Option 1** and requested `/save`. Handoff initiated for clean fresh-session resumption.

## Decisions

### D1: Narrower-B scope (not A, not C)

**Choice:** Operator-approved amendment path only, bounded by a prompt-allowlist-aligned subset of platform-default inner commands. No auto-accept under any conditions. No `acceptForSession`, no custom amendment editing, no Homebrew/mise/developer-tool support.

**Driver:** User's framing after initial A recommendation: *"Operator-in-the-loop is the right posture when the decision has durational effect."* `acceptWithExecpolicyAmendment` is a policy-change with durational effect ("future matching commands can run without prompting" per schema), which is materially different from `file_change`'s inline-accept (which is bounded to a single request's `grantRoot`). Conflating them was my error; narrower-B correctly separates them.

**Rejected:**
- **A (auto-accept for narrow allowlist):** User push-back: *"silently turns a future-matching trust change into implicit plugin behavior."* Rejected because auto-accept bypasses operator awareness for a policy-mutating decision.
- **C (full trust framework with cross-session persistence):** User push-back: *"explodes the surface area before the trust boundary is even reconciled."* Rejected because durable policy is a product-level trust surface, not a follow-up to PR #125.

**Implication:** Every amendment approval requires an explicit `/delegate approve_amendment` invocation. The operator is in the loop for each distinct amendment shape; App Server's session cache (if observed in Phase 1) handles same-shape subsequent commands without re-prompting.

**Trade-offs accepted:** Higher operator touch per job. Accepted because the first-approval-per-shape is the explicit trust event; subsequent matches (if cached) are invisible.

**Confidence:** High (E2). Two independent angles: (a) schema comment explicitly names the durational effect on future matching commands; (b) existing repo posture ("one job, one runtime") exists specifically to prevent session-scoped decisions from leaking across jobs — plugin-side auto-accept would reintroduce exactly that leakage.

**Reversibility:** High. Adding auto-accept later is an additive change gated by a new classification branch; removing auto-accept from a shipped design would be harder (regression).

**Change trigger:** If operator-touch-per-amendment proves painful in practice and Phase 1 confirms App Server session-caching works, a v2 could introduce a narrow auto-accept path for specific patterns. Requires its own design packet.

### D2: Explicit contract revision with diagnostic gate (not fixed-contract + upstream-ticket)

**Choice:** Plugin-local, diagnostics-gated exception to the post–PR #125 empty-decisions terminal-failure rule: when `command_approval + available_decisions == () + proposedExecpolicyAmendment` matches allowlist, reclassify as `AMENDMENT_ESCALATION`. All other empty-decisions cases remain terminal-failed.

**Driver:** `docs/codex-app-server.md:985` says `availableDecisions` is the exact exposed set when present — but doesn't specify the `availableDecisions == [] + proposedExecpolicyAmendment != null` combination. The combination is a case the docs don't fully specify; the repo's current interpretation ("empty → terminal-failed") is a plugin choice in the face of ambiguity, not a contract reading. Treating App Server's presence-of-proposal as informative is a more faithful reading of its intent.

**Rejected:**
- **Fixed contract + upstream ticket:** No forward path for AC1 without upstream resolution of unknown duration. Not a design — a dependency.

**Implication:** The spec's Section "Contract revision" names the exact condition that admits the exception and explicitly preserves the tension with App Server docs ("provisional signal justifies the diagnostic gate for this narrow case"). Phase 1 is the empirical check.

**Trade-offs:** The revision is an interpretive choice that could later conflict with upstream clarification. Accepted; if App Server publishes explicit guidance contradicting the revision, it's one edit to reverse.

**Confidence:** Medium-high. Interpretive choice grounded in wire evidence. Phase 1's two observations (amendment accepted + subsequent command stops prompting) convert it to high-confidence or shelve the packet.

**Reversibility:** High. The revision is a single branch in `_classify_empty_decisions_command_approval`.

**Change trigger:** Phase 1 outcome. If observation (1) fails, the revision is wrong and the packet shelves. If upstream later publishes authoritative guidance, re-evaluate.

### D3: C-prime eligibility (structured plugin-owned allowlist, not prompt-as-source)

**Choice:** Plugin-owned structured allowlist (`request_resolution_allowlist.py`) with per-entry tail validators, explicit trampoline/pivot blocklist, fingerprint-pinned versioning. Initial v1 set: `/bin/test`, `/bin/mkdir`, `/bin/true`, `/bin/cat` — scoped to AC1's verification path.

**Driver:** User's framing: *"I would not make the prose prompt itself the canonical policy source. execution_prompt_builder.py is English guidance with examples, not a machine-stable contract."* C-prime keeps the policy surface typed and testable; prompt is derivative or explicitly kept aligned.

**Rejected:**
- **A (exact-argv allowlist over full command spellings):** Too brittle; policy pins to whole spellings not command families, rots fast.
- **B/D (absolute-path prefix / App Server-trust):** Too broad; every platform binary becomes eligible including shell trampolines.
- **C as written (prompt verbatim):** Prose, not machine-stable.

**Implication:** The spec defines `AllowlistEntry` with `(entry_id, argv0, description, validate_tail)`. Each entry's validator enforces argv-shape constraints and path-escape resistance (resolving absolute AND relative argv tokens against request `cwd` + worktree). `_TRAMPOLINE_BINARIES` is a disjoint blocklist enforced before allowlist lookup.

**Trade-offs:** Initial v1 allowlist is tight (4 entries) — `grep`, `find`, `ls` deferred to v2 because multi-path / pattern-vs-path disambiguation isn't precise under the current simple validator approach. Accepted because covering AC1 is the priority; v2 can widen.

**Confidence:** High (E2). User cited `approval_router.py:125` (repo's existing posture of treating command payloads as opaque and high-risk) as the pattern to extend.

**Reversibility:** High. Allowlist entries are additive; removal requires version bump + fingerprint update, caught by test.

**Change trigger:** New user request patterns that require command shapes v1 doesn't cover. Any expansion is a named v2 ticket with its own allowlist-entry diff + justification.

### D4: Distinct `approve_amendment` verb (not same `approve` + warning)

**Choice:** `codex.delegate.decide` tool's `decision` enum gains `approve_amendment` as a new value. Plain `approve` continues to reject `command_approval` with PR #125's typed reason. `approve_amendment` is valid iff the captured request still classifies as `AMENDMENT_ESCALATION` under the current allowlist (drift guard via re-classification at decide time).

**Driver:** Wire protocol already separates string-enum accept (`"accept"`) from object-enum amendment (`{"acceptWithExecpolicyAmendment": {"execpolicy_amendment": [...]}}`). Surfacing that distinction at the operator interface mirrors the wire contract. Grep-ability of `approve_amendment` events in audit logs is load-bearing for the "explicit audit trail" AC.

**Rejected:**
- **Same `approve` verb + rich warning:** Collapses two structurally different wire responses into one operator action; relies on the operator reading the warning carefully every time. Weaker audit trail.
- **Flag-gated approve:** Worst-of-both-worlds; distinct-command-with-worse-ergonomics.

**Implication:** MCP tool schema change in `mcp_server.py`; new verb handling in decide path; existing `approve` path unchanged (still rejects for `command_approval`).

**Trade-offs:** One more decision verb in the operator surface. Accepted — surface is small and names-as-distinctions fits the codebase's existing posture (`command_approval` vs `file_change`, `_CANCEL_CAPABLE_KINDS` vs `_KNOWN_DENIAL_KINDS`).

**Confidence:** High (E2). Three reinforcing arguments: wire-structure mirror, audit grep-ability, codebase naming pattern.

**Reversibility:** Medium. Removing the verb later would require migration of in-flight audit records that reference it. Not hard, but non-trivial.

**Change trigger:** None anticipated.

### D5: A-plus persistence (trust App Server cache; plugin memory audit-only)

**Choice:** Plugin sends amendment response on operator approval. After that, App Server is the only authority on whether matching commands prompt again. Plugin does not cache amendments; if App Server re-prompts for a previously-approved shape, plugin re-escalates. Plugin writes `AmendmentApprovalRecord`s for observability only; the records are never consulted for automatic future approval.

**Driver:** User citation: *"acceptForSession explicitly names a 'same session-scoped approval cache.' The amendment form only says 'future matching commands.' That is not enough to justify inventing plugin-side lifetime rules."* And: *"One job, one runtime is load-bearing against plugin-side caching."*

**Rejected:**
- **B (per-job plugin cache):** Makes plugin guess App Server match semantics within a job. Two policy engines can drift.
- **C (per-session plugin cache):** Worse; extends the guessed policy across distinct jobs despite the isolation model.
- **D (cross-session durable):** Out of bounds; durable policy is a product-level trust surface.

**Implication:** Simpler plugin-side state (no cache invalidation rules, no stale-amendment failure modes). Every amendment approval is a single wire response; plugin has no durational policy state to reason about.

**Trade-offs:** If App Server doesn't cache amendments for subsequent matching commands, operator must approve each one. Accepted because the alternative (plugin-side caching) adds risk of drift. Phase 1's observation (2) adjudicates which regime holds.

**Confidence:** High (E2). Three reinforcing cites: wire schema distinction between `acceptForSession` and `acceptWithExecpolicyAmendment`, existing repo boundary-ownership norms in `contracts.md:325`, and "one job, one runtime" isolation model at `foundations.md:155`.

**Reversibility:** High. Adding a plugin-side cache later is additive; no existing state to migrate.

**Change trigger:** If Phase 1 shows App Server doesn't cache AND operator-touch-per-command proves painful, a narrow per-job cache could be added. Requires its own design packet.

### D6: Dedicated `AmendmentApprovalRecord` (not distinct-decision-in-existing-stream)

**Choice:** Two records per amendment approval. (1) Existing action audit stream gets a new `decision == "approve_amendment"` event, same shape as other decide() actions. (2) A new dedicated store (`amendment_approval_store.py`) writes a structured `AmendmentApprovalRecord` with amendment-specific fields: request_id, inner_command, proposed_amendment, allowlist_entry_id_at_capture, allowlist_version_at_capture, allowlist_entry_id_at_approval, allowlist_version_at_approval, wire_response_outcome, wire_response_detail, created_at.

**Driver:** AC1 explicitly asks for "explicit audit trail." A dedicated record makes this trivially provable — one record per amendment, one query lists them all. Without the dedicated store, an auditor must join audit events with the pending-request store, parse `proposedExecpolicyAmendment` from each, and cross-check against the allowlist at the time — multi-step reconstruction vs single-record read.

**Rejected:**
- **X (distinct decision in existing stream only):** Sufficient but forces multi-step audit reconstruction; doesn't satisfy the AC's "explicit trail" standard cleanly.

**Implication:** New module `amendment_approval_store.py`. Session-scoped JSONL layout mirroring `pending_request_store.py` + `delegation_job_store.py` patterns (per user correction in Section 3 review). Read API supports per-job, per-runtime, per-entry-id filters as read-time projections over session JSONLs.

**Trade-offs:** New data surface (though small). Accepted because AC clarity is load-bearing.

**Confidence:** High (E2).

**Reversibility:** Medium. Removing the dedicated store later would lose historical audit records unless migrated.

**Change trigger:** None anticipated.

### D7: A-prime resolution-class classifier (not new job status)

**Choice:** Single pure function `classify_request_resolution(parsed, ctx) -> ResolutionResult` in `request_resolution.py`. Four outcomes: `INLINE_ACCEPT`, `AMENDMENT_ESCALATION`, `ORDINARY_ESCALATION`, `TERMINAL_FAILED`. Four consumer sites: `_server_request_handler` (wire response + capture), `_finalize_turn` (capture-time resolution_result), `_project_request_to_view` (fresh re-classification), `decide()` (fresh re-classification).

**Driver:** PR #125's review finding was a two-site drift bug — boundary function answered spatial, call site asked semantic. Centralizing trust classification in one pure function makes drift directly testable. User's framing: *"A single classifier makes drift much harder and directly testable."* Plus an explicit routing invariant: "All cancel-capable request handling routes through the classifier."

**Rejected:**
- **B (new `needs_amendment` job status):** Semantically too expensive. Existing generic attention-required state in `contracts.md:354` already handles the semantics; adding a new status ripples through job status enums, `codex.status`, skill routing, busy-gate semantics, tests, migration logic.
- **C (decide-time-only dispatch):** Understates where change lives. `_finalize_turn` must stop mapping amendment-backed captures to `failed`; runtime must remain live; `_project_request_to_view` must expose real decision surface — that's controller state-machine behavior, not dispatch plumbing.

**Implication:** Classifier is pure/stateless/side-effect-free. `ResolutionResult` struct carries `(resolution_kind, allowlist_entry_id, allowlist_version, reason_code, detail)` — not a bare enum — so downstream consumers are one-line projections and `AmendmentApprovalRecord` has a clean source for entry/version. `is_within_delegation_boundary` becomes an internal helper called only from inside the classifier for the `file_change` branch.

**Trade-offs:** New module, slightly more scaffolding than inline controller logic. Accepted — centralization is the whole point.

**Confidence:** High (E2). Reinforced by user's explicit routing-invariant framing (classifier is necessary, invariant makes it sufficient).

**Reversibility:** Medium. Inlining classifier back into controller later would be regressive but straightforward.

**Change trigger:** None anticipated.

### D8: Capture-time classification for `_finalize_turn`; fresh re-classification for poll/decide

**Choice:** `_server_request_handler` stores `ResolutionResult` on the `PendingServerRequest` at capture time. `_finalize_turn` reads that stored result (no re-classification). `_project_request_to_view` (poll) and `decide()` re-classify under current allowlist.

**Driver:** User's framing: *"_finalize_turn is still processing the same in-flight turn that just emitted the request and got the handler response. Using the stored resolution_result there makes the outcome deterministic and consistent with what the handler actually did."* Reclassification at finalize would allow classifier changes mid-turn (implausible given timing but structurally possible) to produce non-deterministic terminal states.

**Rejected:**
- **Fresh re-classification at all sites:** Produces deterministic vs consistent-with-handler trade-off on the wrong side.

**Implication:** `PendingServerRequest` gains `resolution_result: ResolutionResult | None` AND `handler_disposition: Literal["cancel", "accept", "amendment_applied", "amendment_denied", "timeout"] | None`. Both fields in `models.py`; replay in `pending_request_store.py` round-trips them. `_finalize_turn` reads both fields to derive terminal state for amendment-path captures (see Section 4 of the spec for the full matrix).

**Trade-offs:** Slightly more persistent state on captured requests. Accepted.

**Confidence:** High (E2).

**Reversibility:** High.

**Change trigger:** None anticipated.

### D9: B-plus diagnostic gate (2 observations + cheap negative control)

**Choice:** Phase 1 live smoke captures three observations: (1) amended command resumes + completes to `item/completed`, (2) second matching command re-prompts or not, (3) non-matching/disallowed command still fails closed (if cheap to include without destabilizing primary observations).

**Driver:** User framing: *"Negative control is not necessary to prove the contract revision, but it is high-value safety evidence because it tells us the amendment did not silently widen more than intended."*

**Rejected:**
- **A (observation 1 only):** Under-specified; answers wire-response shape validity but not cache-semantics claim.
- **C (add App Server cache-state introspection):** Depends on undocumented observability surface. User: *"making the gate depend on undocumented observability"* would be "silent spec-fragility."

**Implication:** Phase 1 records all three observations where possible; Phase 2 proceeds only on (1)✅ + (3)✅. (2)❌ adapts design to re-escalate per matching command; doesn't shelve.

**Trade-offs:** Slightly more complex gate. Accepted — cost is ~1 extra command in the smoke.

**Confidence:** High (E2).

**Reversibility:** High.

**Change trigger:** Phase 1 execution.

### D10: Phased rollout — minimal slice → gate → generalize → verify; no feature flag

**Choice:** Phase 0 builds transport prerequisite + minimal hardcoded amendment-response path for one specific request shape. Phase 1 drives gate against that minimal slice. Phase 2 generalizes (classifier, allowlist, stores). Phase 3 AC verification + merge. No feature flag; git branch IS the gate.

**Driver:** User correction: *"Phase 1 cannot run before enough of the amendment path exists to actually send acceptWithExecpolicyAmendment. The current sequence says diagnostic gate happens before the classifier/stores/approve_amendment implementation, but the gate itself depends on that path existing."* My original ordering was causally inverted. User also: *"I don't see an existing plugin-local feature-flag pattern in the repo."*

**Rejected:**
- **Phase 1 before any code (my original):** Causally impossible.
- **Feature-flag-gated rollout:** Invents infrastructure the repo doesn't have.

**Implication:** Spec Section "Rollout sequence" uses the corrected order; Phase 0's minimal slice is enough to send ONE amendment response end-to-end, no generalization. All work stays on `feature/delegate-exec-policy-amendment` until Phase 1 clears.

**Trade-offs:** None substantive.

**Confidence:** High (E2).

**Reversibility:** High.

**Change trigger:** None.

### D11: Branch `feature/delegate-exec-policy-amendment` from `main`

**Choice:** Fresh branch off `main` (not continuing on `feature/delegate-remediation-sandbox-approval` which carries PR #125).

**Driver:** Scope discipline — PR #125's branch is for that PR's work. This design packet is a distinct concern with its own ticket AC path.

**Implication:** Branch created at `main`'s HEAD after `git pull --ff-only`. Spec committed as first artifact.

**Trade-offs:** None.

**Confidence:** High (E1).

**Reversibility:** N/A.

**Change trigger:** None.

### D12: Single-file spec (not modularized via superspec)

**Choice:** Keep `2026-04-23-exec-policy-amendment-design.md` as a single 805-line file for user review.

**Driver:** User selected Option 1 when presented with the modularize-vs-single-file choice after the `PostToolUse:Write` hook flagged the 805-line length.

**Rejected:**
- **Modular via `/superspec:spec-writer`:** User's choice; no additional rationale given in chat but the preference is to review as-is.

**Implication:** Future references to subsections use page-anchor within the single file rather than distinct modular files. If modularization is later desired, `superspec:spec-writer` can convert the single file.

**Trade-offs:** Less ergonomic cross-session referencing for future sessions that cite specific design decisions. Accepted per user preference.

**Confidence:** High (E1).

**Reversibility:** High — modularization is a post-hoc tooling operation.

**Change trigger:** If future sessions find single-file referencing painful, `/superspec:spec-writer` can be invoked retroactively.

## Changes

### `docs/superpowers/specs/2026-04-23-exec-policy-amendment-design.md` — new file, 805 lines

**Purpose:** The exec-policy amendment design spec — comprehensive design document compiling the brainstorming synthesis across 7 questions, 6 design sections, and 12 design decisions.

**Approach:** Single-file spec following the structure of existing `docs/superpowers/specs/*-design.md` conventions. Sections: Overview + ticket/prerequisites/provenance, Goal, Scope (in/out), Contract revision, Architecture (classifier + routing invariant + statelessness + capture-time-vs-fresh-reclassify table), Components (6 subsections covering classifier module, allowlist, versioning, record store, blocking resolution registry, field additions to existing types), Transport prerequisite, Data flow and state machine (classify pseudocode, wire dispatch, job-status transitions, per-operation flows), Failure modes and fail-closed rules (8 invariants + failure-mode table), Testing plan, Rollout sequence (Phases 0-4), Deliverables, Branch, Open questions, Non-goals, References.

**Key details:**
- Contract revision framed as "plugin-local, diagnostics-gated exception" preserving tension with App Server docs.
- `ResolutionResult` struct with `resolution_kind`, `allowlist_entry_id`, `allowlist_version`, `reason_code`, `detail` — not bare enum.
- v1 allowlist: `/bin/test`, `/bin/mkdir`, `/bin/true`, `/bin/cat` with per-entry tail validators.
- Fingerprint-pinned versioning via SHA-256 over `(entry_id, argv0)` tuples + sorted trampolines.
- Session-scoped store layout: `plugin_data_path / amendment_approvals / <session_id> / records.jsonl`.
- `AmendmentApprovalRecord` emission narrowed to `applied`/`error` only (not `timeout`).
- Transport prerequisite: blocking resolution registry + background-turn execution.
- Deny signal on blocked path = `{"decision": "cancel"}` (matches existing `/delegate deny` terminal-fail contract).
- Cold-start reconciliation: amendment-pending jobs → `unknown` (matches existing behavior at `delegation_controller.py:2117`).

**Future-Claude note:** Spec is self-contained; reading it top-to-bottom gives a complete picture of what Phase 0 needs. Start the implementation plan (via `superpowers:writing-plans` skill) by reading the spec first; decisions D1-D12 in this handoff give supplemental reasoning but aren't strictly required if the spec is consulted directly.

### Branch `feature/delegate-exec-policy-amendment` created from `main`

**Purpose:** Isolate exec-policy amendment design work from PR #125's branch. Work stays on this branch through Phases 0-3 until merge.

**Approach:** `git checkout main && git pull --ff-only && git checkout -b feature/delegate-exec-policy-amendment`. Standard feature-branch creation.

**Key detail:** Branch matches the repo's `feature/*` convention from `.claude/rules/workflow/git.md`.

### Commit `edff9c07` on `feature/delegate-exec-policy-amendment`

**Purpose:** Durable record of the spec synthesis.

**Approach:** Single-file commit with detailed message naming key design decisions. Message structure borrowed from `.claude/rules/workflow/git.md` conventions.

**Key detail:** Committed pre-user-review. User may request changes; handle via amendment or follow-up commit as appropriate.

## Codebase Knowledge

### Current repo state (post-PR #125, pre-this-session)

| Concept | Location | Behavior |
|---------|----------|----------|
| `is_within_delegation_boundary` (command_approval) | `approval_router.py:123-130` | Returns `False` unconditionally. Comment cites opaque command payloads as reason. |
| `is_within_delegation_boundary` (file_change) | `approval_router.py:131-139` | Returns `False` if `grantRoot` outside worktree; `True` otherwise. |
| Inline-accept gate | `delegation_controller.py:716-722` | `"accept" in available_decisions AND is_within_delegation_boundary`. Now only `file_change` can satisfy both. |
| `_AVAILABLE_DECISIONS["command_approval"]` defaults | `approval_router.py:21-29` | Includes `acceptWithExecpolicyAmendment`, `applyNetworkPolicyAmendment`, `accept`, `acceptForSession`, `decline`, `cancel`. |
| `_AVAILABLE_DECISIONS["file_change"]` defaults | `approval_router.py:32` | `("accept", "acceptForSession", "decline", "cancel")`. |
| Server request handler | `delegation_controller.py:652-731` | Parses wire, decides capture/wire response. Current logic inlines trust checks at call site. |
| `_finalize_turn` empty-decisions path | `delegation_controller.py:~1547` | Post–PR #125 Option B: empty `available_decisions + cancel-capable` → `failed + null promotion_state`. |
| `_project_request_to_view` | `delegation_controller.py:~864` | Projects stored request to operator view; forces `("deny",)` for cancel-capable kinds. |
| `decide()` approve/deny | `delegation_controller.py:~1731, ~1802` | Approve rejects `command_approval`/`file_change` with typed reason (current). Deny is terminal-fail + runtime release/close. |
| Cold-start reconciliation | `delegation_controller.py:2117` | Orphaned `running`/`needs_escalation` jobs → `unknown`. |
| MCP tool schema | `mcp_server.py:160` | Current `decision` enum for `codex.delegate.decide`. |
| `pending_request_store.py` replay | `pending_request_store.py:94` | JSONL serialization/deserialization for `PendingServerRequest`. |
| Existing session-scoped store pattern | `pending_request_store.py:24`, `delegation_job_store.py:33` | Top-level `plugin_data_path / <kind> / <session_id> / records.jsonl`. |
| App Server runtime inline-respond | `runtime.py:285-287`, `jsonrpc_client.py:106` | Handler returns inline; `respond()` sends to in-flight request. |

### Wire schema facts (from `CommandExecutionRequestApprovalResponse.json`)

Discriminated-union decision shape:
- **String enums:** `"accept"`, `"acceptForSession"`, `"decline"`, `"cancel"` — simple decisions
- **Nested objects:** `{"acceptWithExecpolicyAmendment": {"execpolicy_amendment": [...]}}`, `{"applyNetworkPolicyAmendment": {"network_policy_amendment": {...}}}` — payload-carrying decisions

The `execpolicy_amendment` field is snake_case in the schema (not camelCase). `acceptForSession` schema comment explicitly says "same session-scoped approval cache"; `acceptWithExecpolicyAmendment` says "future matching commands can run without prompting" — materially different semantics.

### Boundary-check surface (unchanged from PR #125)

Post–PR #125, `command_approval` is uniformly out-of-boundary. `file_change` is boundary-checked via `grantRoot`. This spec keeps both behaviors intact; it only introduces a narrow *exception* for amendment-eligible `command_approval` captures that goes through a new path (not the old boundary check).

### Ticket T-20260423-01 current state

- Status: **open**.
- AC1 (end-to-end delegation + verification): **not met** — shell-wrapper exec-policy gap is the blocker this design addresses.
- AC5: **met** — amended in PR #125 to admit `failed + null promotion_state` as a valid terminal for deferred-scope exec-policy ops.
- Scope Limitations section explicitly defers exec-policy widening to a follow-up trust-boundary design (this packet).

## Context

### Mental model

**Framing:** Exec-policy amendment is a *durational policy change*, not a one-shot approval. App Server's response contract distinguishes single-request decisions (`accept`, `decline`) from session-or-longer-scoped decisions (`acceptForSession`, `acceptWithExecpolicyAmendment`). Conflating these is dangerous because a single operator action in the durational case sets standing policy for future matching commands.

**Kind-level trust classification extended:** The predecessor handoff established that `file_change` has an honest scope field (`grantRoot`); `command_approval` has opaque payloads. This packet adds: for amendment-backed `command_approval`, the *inner command* (from `proposedExecpolicyAmendment`) is the thing the plugin reasons about. The allowlist is a plugin-owned judgment about which inner commands the plugin is willing to negotiate a standing policy concession for.

**Architectural seam:** The resolution-class classifier is a single authoritative source of trust classification. Four consumer sites are pure projections. The routing-rule invariant ("all cancel-capable handling routes through the classifier") converts the architecture from a convention into a seam.

**Transport layer gap:** Today's handler returns inline, freeing the JSON-RPC transport immediately. Amendment responses must go back through the *same* in-flight request App Server is blocked on. This requires a blocking-resolution primitive and a background-turn execution model. The design names this as "transport prerequisite" — Phase 0 must build it.

### Environment state

- Branch `feature/delegate-exec-policy-amendment` at commit `edff9c07`, NOT pushed to origin yet (user hasn't requested push).
- Working tree clean.
- Ticket T-20260423-01 still open; spec exists on branch but not yet merged.
- Spec file at `docs/superpowers/specs/2026-04-23-exec-policy-amendment-design.md`, 805 lines.
- Handoff state file at `docs/handoffs/.session-state/handoff-772acaa7-baf7-4b6d-8faf-ffc9ed5d404c` will be cleaned up by this handoff's save procedure.

### Project context — what this closes / enables

This spec is the design packet for the predecessor's queued next action. Once user review lands (Option 1 path), the next session uses `superpowers:writing-plans` to produce an implementation plan. Phases 0-3 execute against that plan. On Phase 3 AC verification success, PR #125's deferred-scope closes and T-20260423-01's AC1 is met.

## Conversation Highlights

**User confirming fresh-session mandate:**
> "This IS the fresh session."
— Clear directive. No ambiguity about whether to start the design work here or elsewhere.

**User's scope pushback on Option A (auto-accept):**
> "I would not choose A as written. It looks operationally minimal, but it silently turns a future-matching trust change into implicit plugin behavior, and it assumes an undocumented reinterpretation of availableDecisions: []."
— Precise critique naming both the trust-change-silence and the contract-interpretation-assumption in one framing. My original A was blind to the durational-effect distinction.

**User's contract-interpretation framing:**
> "Live-wire evidence is treated as a provisional signal that justifies the diagnostic gate for this narrow case."
— Epistemically honest phrasing. Not "we resolved the tension"; instead "we gated on the tension." This became the spec's "Interpretation basis" section.

**User correcting the wire response shape:**
> "the App Server response shape is not {"decision": "acceptWithExecpolicyAmendment", "amendment": ...}. The schema requires the nested form..."
— Factual correction with schema citation. My flat-shape draft was wrong.

**User on persistence:**
> "acceptForSession is defined as approving the command and future prompts in the same session-scoped approval cache should run without prompting. The amendment form only says 'future matching commands.'"
— Direct schema comparison that grounded the A-plus decision.

**User on classifier scope:**
> "Narrow classify_request_resolution() to cancel-capable kinds only. Keeps this packet focused."
— Scope discipline. Unknown / parse-failure / request_user_input paths keep their existing handling.

**User on drift framing:**
> "'Makes drift structurally impossible' is too strong. A single classifier makes drift much harder and directly testable, which is the right claim."
— Epistemic precision. Also required adding the explicit routing invariant to convert the architecture into an actual seam.

**User on transport gap:**
> "The current transport cannot do Step 6 as written. Right now the runtime only sends a response to a server-initiated request inline while the turn/start loop is active."
— Named the architecture's most substantive omission. Without this correction the rest of the design would have been implementable only via a silent architecture change.

**User on phase ordering:**
> "Phase 1 cannot run before enough of the amendment path exists to actually send acceptWithExecpolicyAmendment. The current sequence says diagnostic gate happens before the classifier/stores/approve_amendment implementation, but the gate itself depends on that path existing."
— Causal correction. My ordering was inverted.

**User on option choice:**
> "Option 1 is my choice. I will review the single-file spec as-is, then share my feedback with you. Save a handoff now, we will resume in a fresh session /save"
— Clean stopping point directive. Triggered this handoff.

## User Preferences

**Codebase-authority-first corrections.** Every correction cited specific repo files with line numbers. Paraphrasing: *"repo authority points this way"* — user's framing throughout. Future sessions should read repo state before proposing designs, not infer from handoff context.

**Epistemic honesty in design language.** User consistently sharpened my phrasing to preserve tension rather than resolve it falsely. "Structurally impossible" → "directly testable"; "contract signal" → "provisional signal that justifies the gate"; "closes AC1" → "intended to clear the gap, contingent on Phase 1."

**Scope discipline — narrow packet > broad framework.** Rejected auto-accept (broader than needed), rejected cross-session state (out of bounds), rejected feature flags (infrastructure invention). Preferred operator-approved narrow path with precisely-validatable allowlist entries.

**Names-as-distinctions > warnings-as-barriers.** `approve_amendment` distinct verb over enriched-approve-with-warning. Mirrors codebase's existing posture of separating kinds, decision types, and approval flows by name.

**Architecture: central source, pure projections.** Resolution-class classifier as single trust source; all four consumer sites as pure projections; explicit routing-rule invariant to convert architecture into seam.

**Content fingerprint over entry-count pin.** Low-resolution proxies fail to catch value-level edits that preserve cardinality. Fingerprint covers value edits, reorderings, structural changes. *"Same cost to implement, strictly higher detection power."*

**Evidence-first verification.** User pushed back on every design decision by reading repo files. Future sessions should expect pushback unless design claims are grounded in citable code.

**Design-doc structure: completed-before-pending ordering.** Applied in PR body structure (predecessor handoff). Likely applicable to future spec writing as well.

**Handoff chain protocol maintenance.** User ran `/save` at clean stopping point; expects handoff chain continuity for next session's `/load` to pick up. Predecessor handoff's pattern: complete the immediate work, then commit durable artifact, then handoff.

## Learnings

### App Server's `availableDecisions: []` + `proposedExecpolicyAmendment` is a contract-interpretation choice, not a resolved reading

**Mechanism:** Wire evidence shows App Server emits `command_approval` with empty `availableDecisions` + non-empty `proposedExecpolicyAmendment` for shell-wrapped commands. The static docs (`docs/codex-app-server.md:985`) say `availableDecisions` is the exact exposed set when present, but don't specify the combination. The plugin's interpretation is a choice under ambiguity.

**Evidence:** Raw wire from predecessor live smoke; ticket Scope Limitations explicitly names this as "out of scope, deferred to follow-up design"; PR #125 deliberately preserved the fail-closed reading pending this design's adjudication.

**Implications:** Any design that treats the wire combination as informative (i.e., responds with `acceptWithExecpolicyAmendment`) is a deliberate contract revision. It must be gated on live verification, not shipped on assumption.

**Watch for:** If upstream Codex/App Server later publishes explicit guidance contradicting the revision, the design reverts. The spec names this reversal path.

### Discriminated-union decision shapes enforce kind-separation at parse time

**Mechanism:** Wire schema uses `{"decision": "<string>"}` for simple decisions and `{"decision": {"<kindName>": {...}}}` for payload-carrying decisions. Can't accidentally produce one when you meant the other.

**Evidence:** `CommandExecutionRequestApprovalResponse.json:5-81` in the vendored 0.117.0 schemas.

**Implications:** Surfacing the distinction at the operator interface (distinct verb `approve_amendment`) mirrors the wire contract. Collapsing to one verb would be the only place in the codebase where one operator action maps to two structurally different wire responses.

**Watch for:** New decision kinds added upstream with payload shapes — same pattern of distinct verbs applies.

### "One job, one runtime" is load-bearing against plugin-side caching

**Mechanism:** The delegation runtime isolates each job; session-scoped decisions don't leak across jobs by design. A plugin-side amendment cache would reintroduce exactly that leakage through a different door.

**Evidence:** `foundations.md:155` + `2026-03-27-codex-collaboration-plugin-design.md:441` establish the isolation model.

**Implications:** Plugin must not maintain its own amendment cache. App Server is the only policy cache. Plugin memory is audit-only.

**Watch for:** Any future design proposing plugin-side caching must explicitly re-reason about the isolation model or it silently breaks it.

### Transport-layer assumption: handlers respond inline, freeing JSON-RPC immediately

**Mechanism:** Current runtime (`runtime.py:285-287`) invokes approval handlers inline; the handler's return value is immediately sent via `respond()` to the in-flight request. decide() today starts a *new* turn via resume prompt — it doesn't answer the original request.

**Evidence:** `jsonrpc_client.py:106` is the `respond()` call site; `delegation_controller.py:1835` is the current decide() resume-prompt path.

**Implications:** Amendment responses require a new primitive — blocking resolution registry — because the amendment must go back through the same in-flight request. This is the transport prerequisite the spec names.

**Watch for:** Any future design that wants wire-level response carriage for deferred operator decisions will need the same primitive. Worth designing the registry as a reusable facility, not amendment-specific.

### Content fingerprint is the right enforcement signal for policy artifacts

**Mechanism:** Monotonic version integers plus entry counts catch only edits that change cardinality. SHA-256 over `(entry_id, argv0)` tuples plus sorted trampoline set catches value-level edits, reorderings, and structural changes.

**Evidence:** User's framing: *"Someone can change /bin/test to /usr/bin/test, or change the trampoline set, without changing the count."*

**Implications:** Any future policy artifact (allowlists, blocklists, trust-set definitions) that needs change-tracking should use fingerprint-pinned tests, not count-pinned.

**Watch for:** Copy-paste of the allowlist pattern for other trust surfaces should bring the fingerprint mechanism with it.

## Next Steps

### 1. User review of the single-file spec (IMMEDIATE)

**Dependencies:** None. User will initiate review in the next session after `/load`.

**What user reviews:** `docs/superpowers/specs/2026-04-23-exec-policy-amendment-design.md` on `feature/delegate-exec-policy-amendment`.

**Expected feedback categories:**
- Wording precision (likely — matches user's pattern of sharpening phrasing)
- Additional corrections around fields, flows, or invariants
- Possible push-back on specific design decisions if on reflection user sees issues
- Possible request to modularize via `/superspec:spec-writer` after all (user chose Option 1 but may revise)

**Next action after user review:** Address feedback inline (possibly another iteration of the brainstorm-section-corrections loop), then transition to `superpowers:writing-plans` to produce the implementation plan.

### 2. Implementation plan via `superpowers:writing-plans`

**Dependencies:** Spec reviewed and approved.

**What to read first:**
- The spec itself (`docs/superpowers/specs/2026-04-23-exec-policy-amendment-design.md`)
- This handoff's Decisions section for supplemental reasoning on D1-D12
- Ticket T-20260423-01 for AC framing
- Existing plans in `docs/plans/` to match repo conventions

**Approach suggestion:** Phase 0 first (transport prerequisite + minimal slice). Each phase is its own sub-plan. Phase 1's diagnostic-gate verification is partly manual (live smoke observation), so the plan should name the observation recording mechanism.

**Acceptance criteria:** Plan is dependency-ordered, phases map to spec's rollout sequence, each task has concrete file touches and verification steps.

**Potential obstacles:**
- Background-turn execution model is novel; implementation plan may need to investigate `runtime.py` for feasible shapes.
- Phase 1 live smoke requires an operator to drive the `/delegate` flow manually; plan should cover the recording and adjudication mechanism.

### 3. Phase 0 implementation (starts after plan lands)

**Dependencies:** Implementation plan approved.

**Scope:** Transport prerequisite (blocking resolution registry + background-turn execution) + minimal hardcoded amendment-response path for one specific request shape. No classifier, no full allowlist, no `AmendmentApprovalRecord` store.

**Watch for:** The minimal slice is *intentionally* narrow. Scope creep toward "might as well add a bit of the classifier here" should be resisted — Phase 0's purpose is the gate driver, nothing more.

### 4. Phase 1 live smoke (after Phase 0 lands)

**Dependencies:** Phase 0 merged to branch.

**What to read first:** Spec's "Phase 1 — Diagnostic gate" subsection.

**Approach:** Controlled live delegation with a single command shape matching the hardcoded path. Record observations per B-plus (turn resumes + subsequent command re-prompt or not + negative control).

**Outcomes:**
- (1)❌ → shelve; document in ticket; packet closes as "upstream clarification needed."
- (1)✅ + (2)❌ → adapt spec note; proceed to Phase 2.
- (1)✅ + (2)✅ → proceed as designed.
- (3)❌ → tighten approach before Phase 2.

### 5. Phases 2-3 after Phase 1 clears

**Dependencies:** Phase 1 observations favorable.

**Scope:** Generalize (Phase 2) + AC verification (Phase 3) + merge.

### 6. Push branch to origin (when ready)

**Dependencies:** At least Phase 1 clearance (otherwise branch may be abandoned).

**Approach:** `git push -u origin feature/delegate-exec-policy-amendment` when user decides; open PR then or after Phase 2.

## In Progress

**State:** Clean stopping point. Spec committed (`edff9c07`); user will review in next session.

**Immediate next action on resume:** `/load` will surface this handoff. User's announced intent is to review the spec as-is (Option 1) and share feedback. Session should: (1) be ready to accept corrections/questions on the spec, (2) iterate inline if needed, (3) transition to `superpowers:writing-plans` after approval.

## Open Questions

1. **Does App Server actually cache `acceptWithExecpolicyAmendment` across matching commands?** Phase 1 observation (2) adjudicates. Until then, design is agnostic — plugin re-escalates if cache doesn't exist.

2. **Does App Server return an error or silently reject `acceptWithExecpolicyAmendment` when `availableDecisions: []`?** Phase 1 observation (1) adjudicates. Design shelves on rejection.

3. **Background-task lifecycle: does existing runtime already support it, or is it new work?** Implementation-plan scoping question. Determines Phase 0 effort scope.

4. **`AMENDMENT_DECIDE_TIMEOUT` default of 30 minutes — is that right for operator response time?** Operational question; may tune based on Phase 3 experience.

5. **Does `proposedExecpolicyAmendment` ever appear with non-empty `available_decisions`?** Not observed. Current design treats that case as `ORDINARY_ESCALATION` (non-empty decisions path). If evidence emerges, gate may need widening.

6. **Will user request modularization via `/superspec:spec-writer` after all?** User chose Option 1 for now; may revise after reading 805-line file.

## Risks

1. **Phase 1 diagnostic-gate outcome uncertainty.** The whole design assumes App Server accepts the amendment response. If (1) fails, packet shelves and AC1 remains blocked. Mitigation: Phase 0 is deliberately minimal so a failed gate has minimal sunk cost.

2. **Spec user-review may trigger substantive re-design.** Each section had corrections; cumulative reflection may surface more. Mitigation: iteration capacity is built in (brainstorming skill's review-and-correct loop).

3. **Transport prerequisite is larger than expected.** Background-task execution model may require deeper runtime changes than the spec estimates. Implementation-plan phase will scope this.

4. **v1 allowlist (4 entries) may not cover AC1's actual flow.** Design assumes `mkdir`, `test`, `cat`, `true` cover verification-path commands. If real delegation needs multi-path `cat` or a `ls`, v1 is insufficient and AC1 requires v2 before closure.

5. **The resolution-class classifier adds a new module and routing invariant; implementation drift is possible if the invariant isn't enforced by tests or review.** Mitigation: spec names the invariant explicitly; implementation plan should include a test or review checklist that enforces it.

6. **In-memory blocking-resolution registry loses state on process restart.** Cold-start reconciliation routes amendment-pending jobs to `unknown`, not a graceful recovery. Acceptable per design but could surprise operators. Mitigation: follow-up ticket scope (D4 in Follow-ups).

7. **Orphan delegation worktrees still accumulating.** Inherited from predecessor; not this session's work. Still non-blocking.

## References

| What | Where |
|------|-------|
| Design spec (this session's product) | `docs/superpowers/specs/2026-04-23-exec-policy-amendment-design.md` |
| Commit | `git show edff9c07` |
| Branch | `feature/delegate-exec-policy-amendment` |
| Predecessor handoff | `docs/handoffs/archive/2026-04-23_16-23_delegate-boundary-tightening-shipped.md` |
| Ticket | `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` |
| PR #125 | https://github.com/jpsweeney97/claude-code-tool-dev/pull/125 |
| App Server wire schema | `packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/CommandExecutionRequestApprovalResponse.json` |
| App Server docs | `docs/codex-app-server.md:978-990` |
| Plugin design foundations (one-job-one-runtime) | `docs/superpowers/specs/2026-03-27-codex-collaboration-plugin-design.md:441` |
| Contracts doc | `docs/superpowers/specs/codex-collaboration/contracts.md:284, 289, 325, 354` |
| Current approval router | `packages/plugins/codex-collaboration/server/approval_router.py:115-158` |
| Current request handler | `packages/plugins/codex-collaboration/server/delegation_controller.py:652-731` |
| Current finalize (PR #125 Option B) | `packages/plugins/codex-collaboration/server/delegation_controller.py:1540-1555` |
| Runtime inline-response surface | `packages/plugins/codex-collaboration/server/runtime.py:285-287` |
| Session-scoped store pattern exemplar | `packages/plugins/codex-collaboration/server/pending_request_store.py:24` |
| Cold-start reconciliation | `packages/plugins/codex-collaboration/server/delegation_controller.py:2117` |
| MCP tool schema | `packages/plugins/codex-collaboration/server/mcp_server.py:160` |

## Gotchas

- **Spec is on a branch, not pushed.** `feature/delegate-exec-policy-amendment` exists locally with commit `edff9c07`; remote is unaware. If future-Claude needs to reference the spec from another context (e.g., a CI system), push will be needed.
- **`resumed_from` chain:** This handoff's `resumed_from` points to the predecessor archive path. The state file mechanism under `docs/handoffs/.session-state/` handles this; if the state file is missing in the next session, manually set the frontmatter field to the archive path for chain continuity.
- **Single-file spec was user's explicit choice.** Option 2 (modularize via `/superspec:spec-writer`) was offered and declined. Future sessions should not re-modularize without user approval.
- **Ticket AC matrix hasn't been updated yet.** D3 in Rollout's Phase 3 calls for AC matrix + Scope Limitations update; that's a Phase 3 task, not done this session.
- **Phase 0's minimal slice scope-creeps easily.** The spec names "just enough to send one amendment response end-to-end" — implementation plan should enforce this boundary.
- **`handler_disposition` field on `PendingServerRequest` is new.** Existing stored requests (pre-this-packet) deserialize with `None`; classifier re-invocation on poll/decide computes fresh results. Ensure replay logic handles this gracefully.
- **Background-task execution model is implicit prerequisite.** Spec names it but doesn't design it. Implementation plan must choose threading/asyncio/subprocess shape and handle signal-safety, lifecycle, timeout, crash recovery.
- **Transport prerequisite is the single most architecturally novel piece.** Plugin doesn't currently have blocking-response-carriage primitive; this is new. Plan accordingly — Phase 0 effort is dominated by this.
- **`AMENDMENT_DECIDE_TIMEOUT` default (30 min) is a guess.** Operational experience may require adjustment. Make it configurable via env var from the start.
- **Cold-start reconciliation for amendment-pending jobs is not a graceful recovery.** Existing `→ unknown` mapping applies; operator discard via existing path is the only recovery. Follow-up ticket (D4) may address this.
