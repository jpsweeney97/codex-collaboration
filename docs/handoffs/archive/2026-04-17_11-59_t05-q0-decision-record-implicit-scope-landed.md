---
date: 2026-04-17
time: "11-59"
created_at: "2026-04-17T15:59:27Z"
session_id: 5b921e23-e308-44a2-a550-866acb2952a6
resumed_from: "docs/handoffs/archive/2026-04-17_01-41_t04-closed-ac7-direct-and-t05-kickoff-note-merged.md"
project: claude-code-tool-dev
branch: main
commit: b468e86f
title: "T-05 Q0 design decision landed — implicit scope from infrastructure; Pre-Design reconciliation closed"
type: handoff
files:
  - docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/specs/codex-collaboration/foundations.md
  - docs/superpowers/specs/codex-collaboration/recovery-and-journal.md
  - docs/superpowers/specs/codex-collaboration/promotion-protocol.md
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/codex_app_server_protocol.v2.schemas.json
  - packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/ServerRequest.json
  - packages/plugins/codex-collaboration/hooks/hooks.json
---

# T-05 Q0 Design Decision Landed — Implicit Scope from Infrastructure

## Goal

Complete the design pass on T-20260330-05 that was primed by the prior session's kickoff note, closing Question 0 (and the dependent Q1-Q4) so the ticket's AC-locking gate can be released and implementation can begin in a fresh session.

**Trigger.** The 01:41 (2026-04-17) handoff's Next Steps #1 named T-05 as the next critical-path packet and specified: "First move on T-05 is NOT implementation — it's a design reconciliation pass to answer the inherited multi-agent scope-transport question." User explicitly requested "Continue with T-05 design pass" after `/load` resolved the prior handoff.

**Stakes.** T-05 is the execution-domain foundation packet on the cross-model → codex-collaboration supersession arc. T-06 (promotion + delegate UX) and T-07 (analytics, reviewer, cutover) both block on T-05. Q0 had been explicitly gating AC-locking per the kickoff note's instruction "Do not lock ACs until the design pass closes the five questions above." Until Q0 closed, nothing downstream could start.

**Broader context.** The question inherited from T-04 v1 plan §2.2.3 (multi-agent scope-transport design) is narrower for delegation than for dialogue — delegation is a one-shot parent→child handoff at job creation, not a coexistence problem among co-resident agents. The dialogue path's workaround ("gatherers are outside containment" via `hooks.json:14-22`) does not generalize to contained execution subjects.

**Success criteria:**

1. ✅ Answer Q0 with a defensible position (descriptor type / reuse / implicit)
2. ✅ Derive Q1-Q4 answers from Q0's resolution
3. ✅ Update T-05's ticket to record the decision without erasing the design-pass history
4. ✅ Update ACs to match the chosen design (so AC-locking is unblocked)
5. ✅ Commit/merge/push under the project's branch-protection + "create new commit, not amend" rules
6. ✅ Identify the narrow Q2/Q4 implementation-time verification needed before T-05 execution begins

All six met. The session also produced a memorable correction: the initial Option C recommendation was materially wrong, caught by user scrutiny with verified repo citations.

**Connection to project arc.** This session converts T-05 from "open with gating Q0 question" to "open with Q0 resolved, ACs unlocked, implementation ready to start." The cross-model supersession arc now has its execution-domain design foundation settled; the remaining work is plumbing (runtime, worktree, persistence, approval-routing) per the updated ACs.

## Session Narrative

**Phase 1 — Resume from 01:41 handoff (~3 min).** The `/handoff:load` resolved the prior session's handoff cleanly. Branch was `main` at `2813e469`, working tree clean — exactly matching the freeze state. Loaded handoff was archived; new state file written at `docs/handoffs/.session-state/handoff-5b921e23-e308-44a2-a550-866acb2952a6`.

**Phase 2 — User directs T-05 design pass (~1 min).** User said simply "Continue with T-05 design pass." Pre-flight: verified `git status --short` clean, HEAD still at `2813e469`, branch still `main`. Then planned the reading: T-05 ticket + the four cited files from the kickoff note's "Existing material to reconcile against" subsection. Size-checked all six target files — none over 300 lines — then read in parallel (T-05 ticket, contracts.md, manifest.json, gatherer-code, gatherer-falsifier, hooks.json).

**Phase 3 — Add Q3/Q4 context reads (~3 min).** After absorbing the kickoff material, identified that Q3 (mutation) and Q4 (enforcement) would depend on contracts I hadn't yet read: `promotion-protocol.md` and `recovery-and-journal.md`. Both cited in the kickoff note's existing-material list. Size-checked (99 + 177 lines), read both in parallel. The load-bearing finding from `recovery-and-journal.md:116-123`: delegation-crash recovery requires reconstructing state from the DelegationJob record — "restart from brief" creates a new execution runtime in the existing worktree and re-delegates with the original prompt. This means ANY scope the job carries MUST be durable state on the DelegationJob, not ephemeral prompt data.

**Phase 4 — Invoke making-recommendations for Q0 (~20 min).** Q0 is explicitly a compare-and-choose decision with real trade-offs (dialogue adopt vs. distinct descriptor vs. implicit vs. deferral). Invoked `making-recommendations` skill to structure the recommendation per the project's decision-making framework. Walked the full 9-step workflow (stakes calibration came out High — hard to reverse, wide blast radius; required full workflow). Generated 6 options explicitly (A adopt as-is, B extend in place, C new DelegationScope, D implicit, E deferral, Null). Evaluated against 8 criteria. Recommended Option C: new `DelegationScope` type with 4 fields (`allowed_roots`, `writable_roots`, `exec_policy`, `mutation_policy`), positioned as "minimum viable for v1 with forward-compat reserved slots."

**Phase 5 — User runs /scrutinize on Option C (~25 min).** User returned with a structured scrutiny containing 5 Critical Failures (3 High severity, 2 Medium), High-Risk Assumptions, Real-World Breakpoints, Required Changes, and verdict `Major revision`. The scrutiny's systemic finding was load-bearing: "the recommendation jumps from 'delegation is different from dialogue' to 'therefore freeze a rich new permission descriptor now.' The distinction is probably real. The proposed contract shape and ranking are not yet disciplined enough by the actual runtime substrate or by the v1 workload assumptions."

**Phase 6 — Verify every cited claim (~15 min).** Applied the project pattern recorded in memory: verify citations before propagating. Size-checked files I hadn't read (foundations.md at 323 lines, the App Server schema fixture at 12,681 lines, ServerRequest.json at 1,824 lines, runtime.py at 197 lines). Read foundations.md and runtime.py in full; read narrow windows around `schemas.json:6840-6920` (ReadOnlyAccess shape), `schemas.json:8010-8090` (workspaceWrite sandbox), `ServerRequest.json:355-415` (CommandExecutionRequestApprovalParams), `ServerRequest.json:595-655` (FileChangeRequestApprovalParams). All five critical failures VERIFIED:

- Schema does have `readableRoots` (schemas.json:6871) and `writableRoots` (:8050); has NO exec-policy field
- `runtime.py:126` confirms only `{"type": "readOnly"}` is used today — advisory only
- `foundations.md:228-241` confirms the foundation already treats "worktree identity and writable scope" as an execution-profile source category
- `contracts.md:88` (the line numbered by my earlier read) has `requested_scope | object` — bare, untyped
- `ServerRequest.json:367` (command) and `:608` (file change) confirm divergent approval payload shapes; grantRoot at :610-611 is explicitly `[UNSTABLE]`
- T-05 ticket `:134-139` confirms mutation semantics are still open

**Phase 7 — Major revision: withdraw Option C, recommend Option D (~5 min).** With all 5 failures verified, the revised position was straightforward: delegation IS different from dialogue (the narrow thesis survives), but the foundation already expresses the scope concept infrastructurally (`worktree_path` + sandbox defaults). Adding a new contracts.md type would reinvent what's already there. Presented the revision with full section structure: acknowledgment that Option C was wrong on substance, revised Q0a recommendation (Option D), explicit "what was wrong with my dismissal of D" (I conflated worktree with a narrow subdirectory — a worktree IS a full checkout, so docs/specs ARE in the worktree by construction), revised Q1-Q4 implications under D, and residual trade-off note (future sub-worktree restriction would require an additive contract extension, opposite direction from my original "reserved slot" instinct but fine).

**Phase 8 — User approves Option D with 3 refinements (~5 min).** User responded: "The draft is substantively approved with those three refinements. The main one is non-optional: add `includePlatformDefaults: false` if you want the sandbox AC to match the claimed behavior."

The three refinements:
1. **High (non-optional):** `includePlatformDefaults: false` must be set everywhere, because the schema defaults it to `true`. Without the override, `restricted` `readOnlyAccess` with `readableRoots: [worktree_path]` still leaks platform-default readable roots — AC would overclaim the read boundary.
2. **Medium:** Q3 wording pins too much on `foundations.md:112` alone. The stronger claim about session-widening impossibility is defensible from the broader split-runtime contract at `:73` and `:116`. Rephrase to avoid overcommitting to a single citation.
3. **Medium:** "raw server-request payload is preserved" is too strong — `requested_scope` is "what the request is asking for," and other payload fields (`threadId`, `turnId`, `itemId`) live elsewhere. Soften to "request-relevant approval payload preserved opaquely through `requested_scope`; v1 performs no normalized comparison."

**Phase 9 — Final draft + review before execution (~10 min).** Drafted the replacement text for the Pre-Design Reconciliation section with all three refinements applied. Used the T-04 closeout pattern: preserve the historical block verbatim (it's the design-pass history), append a new "Design Decision: Scope-Transport Resolved (v1)" section before the AC list. Proposed two AC modifications: (1) insert a new sandbox-construction AC with the full `SandboxPolicy` shape including `includePlatformDefaults: false`, (2) modify the existing approval-routing AC with the v1 surfacing-only clarification, (3) extend the Tests AC to cover sandbox-policy construction. User approved with terse "With those changes, I would not ask for another pre-edit review round" — explicit permission to proceed without another cycle.

**Phase 10 — Execute: branch + edit + commit + merge + push (~2 min).** Created `docs/t05-q0-decision-record` branch. Applied the Edit in one call (`old_string` covered "Do not lock ACs..." through the last AC bullet; `new_string` was the expanded form with the Design Decision section + updated AC list). Single chained Bash call: `git add` → commit with HEREDOC message → checkout main → `git merge --no-ff` with explicit merge-commit message → `git branch -d` → `git push origin main` → verification log + status.

All steps succeeded:
- Commit `cf8ecc79` on feature branch (90 insertions, 3 deletions)
- Merge `b468e86f` to main with `--no-ff`
- Feature branch deleted
- Push: `2813e469..b468e86f main -> main`
- `git status` clean

**Session ended at ~22% context (1M model) — handoff saved after clean deliverable landing.**

## Decisions

### Decision 1: Q0a = implicit scope from infrastructure (Option D), not new DelegationScope type

**Choice:** v1 scope is expressed by `DelegationJob.worktree_path` + execution-domain sandbox defaults documented at `foundations.md:99-116, :228-241`. No new `contracts.md` type. No new field on `DelegationJob`.

**Driver:** Multiple lines of verified evidence converged:
- `foundations.md:228-241` already treats "Worktree identity and writable scope" as a required execution-profile source category, populated at assembly time from `worktree_path` + profile defaults
- App Server sandbox exposes exactly the shape needed: `workspaceWrite.writableRoots` (`schemas.json:8050`) plus `readOnlyAccess.readableRoots` with `includePlatformDefaults: false` (`:6867-6870`)
- Initial Option C's `exec_policy` field had no enforcement substrate — App Server sandbox has `networkAccess: bool` and that's it for exec-flavored control
- User's scrutiny of Option C identified (and I verified) that the case for a new type was overstated relative to existing infrastructure

**Alternatives considered:**
- **A. Adopt dialogue `scope_envelope` as-is:** rejected — cooperative enforcement, ephemeral lifecycle, name collision with different purpose. Delegation needs durable mechanical enforcement.
- **B. Extend `scope_envelope` in place:** rejected — damages dialogue's simple ephemeral contract by forcing it to carry execution-domain fields; mixes conceptual levels.
- **C. New `DelegationScope` descriptor with 4 fields:** rejected after verification — `exec_policy` invented beyond substrate; C5 interop criterion presupposed a normalized `requested_scope` shape that doesn't exist; `mutation_policy: immutable` was premature contract freeze for open semantics.
- **E. Deferral stance (v1 has no scope descriptor):** rejected — approval-routing AC becomes hollow; every op becomes an escalation.
- **Null (defer Q0 entirely):** rejected — blocks T-05 progress with no new information available.

**Implications:**
- No `contracts.md` change within T-05 scope
- `runtime.py` will need extension to construct `workspaceWrite` shape (currently only constructs `{"type": "readOnly"}` at `:126`)
- T-06 (promotion + UX) inherits a simpler abstraction boundary
- Future typed descriptor remains a clean additive change if post-v1 work surfaces the need
- The foundation's safety envelope (`foundations.md:241`) becomes the canonical locus of "writable scope" for execution

**Trade-offs accepted:**
- If post-v1 work discovers sub-worktree path restriction is needed (e.g., `docs/sensitive/` excluded from some jobs), adding a `DelegationScope` type THEN is the path — this is opposite direction of compatibility from my original "reserved slot" argument, but acceptable per project rule "don't add features beyond what the task requires"
- No pre-emptive state slot for future mutation policy; v1 prose rule ("immutable") must be re-visited as a spec change if/when widening-via-approval becomes real

**Confidence:** High (E3) — triangulated across foundations.md, App Server schema (readable/writable roots + includePlatformDefaults), runtime.py (current sandbox construction), ServerRequest.json (approval payload shapes), contracts.md (requested_scope as bare object). One-round scrutiny convergence.

**Reversibility:** High — the decision is recorded as a v1 commitment; adding a `DelegationScope` type later is a clean additive change, explicitly pre-authorized in the recorded ticket text.

**Change trigger:** Post-v1 use case for sub-worktree path scoping; cross-job scope policies; T-06 UX requiring programmatic comparison of approval payloads against job scope.

### Decision 2: Record as v1 decision, not permanent rejection of a future typed descriptor

**Choice:** Ticket text explicitly states "This is a v1 decision, not a permanent rejection of a future typed descriptor. If post-v1 work surfaces a need for sub-worktree path restriction or cross-job scope policies, adding a `DelegationScope` type to `contracts.md` is a clean additive change at that point — it is not precluded by this decision."

**Driver:** User stipulation verbatim: "Record this as a v1 decision, not a permanent rejection of a future typed descriptor." Preserves forward-path option without forcing future work to fight a "we rejected this" signal.

**Alternatives considered:**
- **Silent decision (no hedge):** rejected — loses the time-scoping, risks reading as permanent
- **Permanent rejection framing:** rejected — would preclude future T-N work

**Implications:** Future implementers see the hedge and understand the decision is contextual, not absolute.

**Trade-offs accepted:** A few lines of additional ticket text.

**Confidence:** High (E1) — direct user directive.

**Reversibility:** High — text edit.

**Change trigger:** N/A.

### Decision 3: v1 approval routing preserves request-relevant payload opaquely; no normalized comparison

**Choice:** Ticket text explicitly states "v1 approval routing does NOT compare a normalized request scope against job scope. The control plane preserves the request-relevant approval payload opaquely through `PendingServerRequest.requested_scope` and relies on sandbox enforcement plus escalation via `codex.delegate.decide`. Normalized request-scope comparison is deferred beyond v1."

**Driver:** User stipulation: "Be precise that v1 approval routing does not compare a normalized request scope against job scope." Backed by verified substrate evidence:
- `contracts.md:88` types `requested_scope` as bare `object` — no normalized shape
- Upstream App Server payloads diverge: `CommandExecutionRequestApprovalParams` at `ServerRequest.json:367` has `command/cwd/proposedExecpolicyAmendment`; `FileChangeRequestApprovalParams` at `:608` has `grantRoot/reason/threadId/turnId`. `grantRoot` is marked `[UNSTABLE]`.

**Alternatives considered:**
- **Allow comparison language:** rejected — presupposes normalized shape that doesn't exist; would force T-05 to invent one
- **Skip language entirely:** rejected — leaves approval-routing AC ambiguous about comparison scope

**Implications:**
- T-05 stays tight; no normalization work required
- T-06 UX / T-07 analytics may need the normalization when they're picked up — at that point, the plugin-side shape can be defined deliberately

**Trade-offs accepted:** Future work will need the normalized shape when comparison becomes necessary.

**Confidence:** High (E2) — scrutiny established the substrate divergence; verification confirmed contract-level + protocol-level evidence.

**Reversibility:** High.

**Change trigger:** T-06 or T-07 requires programmatic comparison of approval payloads against job scope.

### Decision 4: Preserve Pre-Design Reconciliation section verbatim; append Design Decision section

**Choice:** Keep the existing "Pre-Design Reconciliation: Inherited Scope-Transport Question" section (lines 62-169 of the pre-edit ticket) unchanged as design-pass history. Add a new "Design Decision: Scope-Transport Resolved (v1)" section before the Acceptance Criteria header.

**Driver:** Mirrors the T-04 closeout pattern recorded in the prior handoff (the addendum was edited from "**Status:** Open" to "**Historical status at addendum authoring time:** Open" — preserving historical wording). User explicit approval: "The 'preserve historical block, append a later decision record' approach is the right one. Rewriting the pre-design section would erase the design-pass history."

**Alternatives considered:**
- **Rewrite Pre-Design Reconciliation to reflect resolution:** rejected — erases the design-pass history; violates audit-trail preservation pattern
- **Delete Pre-Design Reconciliation and keep only Resolution:** rejected, same reason

**Implications:** Ticket grows from ~200 to ~300 lines. Readers see the history first, then the current decision.

**Trade-offs accepted:** Longer ticket; readers must scroll past historical material to reach the current state. Acceptable because audit trail is first-class.

**Confidence:** High (E1) — user directive + precedent.

**Reversibility:** High.

**Change trigger:** N/A.

### Decision 5: Apply all three scrutiny refinements before commit

**Choice:** Include `includePlatformDefaults: false` in both the Resolution section's Q2 answer and the sandbox-construction AC. Rephrase Q3 to cite `foundations.md:73, :116, :112` together (broader) instead of `:112` alone. Rephrase approval-routing language to "request-relevant approval payload preserved opaquely" instead of "raw server-request payload preserved."

**Driver:** User scrutiny findings:
- **High-severity:** The `includePlatformDefaults` default-to-true catch (schema `:6867-6870`) — without override, restricted readableRoots still leaks platform-default readable roots. AC would overclaim behavior.
- **Medium:** Q3 wording overstated what `foundations.md:112` proves alone — `:112` says approvals are disabled in execution-domain defaults but doesn't directly spell out `acceptForSession` is disabled. The broader conclusion is defensible from `:73` (split-runtime rationale) + `:116` (no session-scoped approval or write state can leak between jobs).
- **Medium:** "raw server-request payload is preserved through `requested_scope`" is too strong — `requested_scope` is "what the request is asking for" per contracts.md, while other payload fields (`threadId`, `turnId`, `itemId`) live on separate fields.

**Alternatives considered:**
- **Apply partial refinements:** rejected — each holds on verification, all three have substantive merit
- **Reject refinements:** rejected — would leave material errors in spec text

**Implications:**
- AC precisely specifies the full `SandboxPolicy` shape future implementers need
- Q3 reasoning stands on broader evidence
- Approval-routing language accurately describes what the control plane does (preserve opaquely through one field) without overclaiming what's in that field

**Trade-offs accepted:** AC is slightly more verbose. Accepted for precision.

**Confidence:** High (E2) — each refinement verified against the cited lines; user is authoritative on wording precision.

**Reversibility:** High (text edit).

**Change trigger:** N/A.

## Changes

### Files modified (this session)

- `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` — New "Design Decision: Scope-Transport Resolved (v1)" section inserted between "Pre-Design Reconciliation" (preserved verbatim) and "Acceptance Criteria"; new sandbox-construction AC inserted at position 2; existing approval-routing AC clarified with v1 surfacing-only wording; Tests AC extended. Net: 90 insertions, 3 deletions. Ticket grew from ~206 to ~293 lines.

### Git state changes

| Commit | Branch | Change |
|---|---|---|
| `cf8ecc79` | `docs/t05-q0-decision-record` | Q0 design decision record (1 file, 90/3) |
| `b468e86f` | `main` (merge) | Merge via `--no-ff`, consistent with prior style |

Feature branch deleted post-merge. Origin/main pushed: `2813e469..b468e86f`.

### Handoff / state files

- Archived (at session start): `2026-04-17_01-41_t04-closed-ac7-direct-and-t05-kickoff-note-merged.md` → `docs/handoffs/archive/`
- State file (this session): `docs/handoffs/.session-state/handoff-5b921e23-e308-44a2-a550-866acb2952a6` — cleaned up by this save
- New handoff (this file): `docs/handoffs/2026-04-17_11-59_t05-q0-decision-record-implicit-scope-landed.md`

## Codebase Knowledge

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `docs/handoffs/2026-04-17_01-41_*.md` | Prior handoff (resumed_from) | Starting state established; "signature is sufficient" T-04 closeout context; T-05 kickoff note with 5 gating questions |
| `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | T-05 ticket (target of this session's edit) | Pre-Design Reconciliation section with 5 gating questions; ACs blocked on Q0 |
| `docs/superpowers/specs/codex-collaboration/contracts.md` | Normative data model | `DelegationJob` at `:59-73` has 9 fields, NO scope field. `PendingServerRequest.requested_scope: object` at `:88` — bare, untyped |
| `docs/benchmarks/dialogue-supersession/v1/manifest.json` | Operational scope_envelope status | `:53-56` shows dialogue baseline carries `scope_envelope` in the delegation envelope; candidate gatherers support it but the slash skill doesn't pass it |
| `packages/plugins/codex-collaboration/agents/context-gatherer-code.md` | Dialogue scope_envelope schema | `:23` — `optional {allowed_roots: string[]}`. Read-only cooperative. Reserved for benchmark-scored runs. |
| `packages/plugins/codex-collaboration/agents/context-gatherer-falsifier.md` | Same | Same shape |
| `packages/plugins/codex-collaboration/hooks/hooks.json` | Gatherer containment status | `:14-22` — SubagentStart matcher `shakedown-dialogue\|dialogue-orchestrator` EXCLUDES gatherers; containment seed never materializes for them. Durable repo evidence. |
| `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | Promotion state machine | Preconditions (HEAD match, clean workspace, artifact hash, completion); state machine pending→prechecks_passed→applied→verified |
| `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Pending-request semantics | `:116-123` delegation crash path: worktree preserved, job marked unknown, "restart from brief" possible. `:139` unknown requests are NEVER auto-approved (fail-closed default). |
| `docs/superpowers/specs/codex-collaboration/foundations.md` | Execution domain defaults (load-bearing) | `:99-116` execution domain policy defaults: workspace-write inside isolated worktree, network disabled, approvals disabled. `:228-241` context assembly profiles: "Worktree identity and writable scope" is a required execution-profile source category. `:73, :116` split-runtime design prevents session-scoped approval bleeding. |
| `packages/plugins/codex-collaboration/server/runtime.py` | Current runtime wrapper | `:126` advisory sandbox is `{"type": "readOnly"}`. No execution-path wrapper yet. JSON-RPC transport via `JsonRpcClient`. |
| `.../0.117.0/codex_app_server_protocol.v2.schemas.json` | App Server sandbox schema | `:6863` ReadOnlyAccess (oneOf: `restricted` with `readableRoots`+`includePlatformDefaults` OR `fullAccess`). `:6867-6870` `includePlatformDefaults` defaults to `true`. `:8019-8062` WorkspaceWriteSandboxPolicy with `writableRoots`, `readOnlyAccess` (allOf ReadOnlyAccess, default `fullAccess` at `:8039-8041`), `networkAccess`, `excludeSlashTmp`, `excludeTmpdirEnvVar`. NO exec-policy field anywhere in sandbox. |
| `.../0.117.0/ServerRequest.json` | Approval payload shapes | `:367` `CommandExecutionRequestApprovalParams` — `command`, `cwd`, `proposedExecpolicyAmendment`, `commandActions`, `networkApprovalContext`. `:608` `FileChangeRequestApprovalParams` — `grantRoot` (marked `[UNSTABLE]` at `:611`), `reason`, `threadId`, `turnId`, `itemId`. Shapes diverge; no unified "scope being requested" payload. |

### Architecture Map: Scope in the Execution Domain

| Layer | Expression | Location |
|---|---|---|
| Plugin-side state | `DelegationJob.worktree_path` | `contracts.md:69` |
| Execution profile | "Worktree identity and writable scope" (required source category) | `foundations.md:228` |
| Safety envelope | Runtime states "isolated worktree path, writable scope, network status, escalation behavior" | `foundations.md:241` |
| Runtime start | Control plane constructs `SandboxPolicy` from worktree_path + profile defaults | (to be implemented in T-05; currently only advisory path in `runtime.py`) |
| Sandbox enforcement | App Server enforces `workspaceWrite.writableRoots` + `readOnlyAccess.readableRoots` | Mechanical at the sandbox layer |
| Out-of-scope ops | Produce `CommandExecutionRequestApprovalParams` / `FileChangeRequestApprovalParams` | App Server emits server requests |
| Plugin routing | `PendingServerRequest.requested_scope: object` (opaque) → control plane surfaces as `needs_escalation` | `contracts.md:75-91` |
| Claude resolution | `codex.delegate.decide` | Existing MCP surface |

Under Q0a=D, NO new DelegationJob field is added for scope. Scope is expressed distributively across these layers.

### Surprising findings / gotchas

- **`includePlatformDefaults: true` by default (schemas.json:6867-6870)** — a `restricted` `readOnlyAccess` with `readableRoots: [worktree_path]` STILL includes platform-default readable roots unless explicitly set to `false`. Without the override, the sandbox is silently looser than intended.
- **`grantRoot` is marked `[UNSTABLE]` (ServerRequest.json:611)** — the schema docstring says "unclear if this is honored today." Don't design v1 approval routing around automatic grantRoot honoring.
- **Command and file-change approval payloads diverge** — `CommandExecutionRequestApprovalParams` has `command/cwd/proposedExecpolicyAmendment`; `FileChangeRequestApprovalParams` has `grantRoot/reason/threadId/turnId`. No unified shape exists; the plugin's `requested_scope: object` is the opaque carrier.
- **`runtime.py:126` hardcodes `{"type": "readOnly"}`** — the advisory sandbox. T-05 implementation extends this to construct `workspaceWrite` with restricted `readOnlyAccess` (the richer shape) for the execution path.
- **Branch-protection hook blocks edits on main** — must checkout the feature branch BEFORE the Edit operation, not after. Recorded in `.claude/rules/workflow/git.md`.
- **The schema file is ~12.7K lines** — targeted reads with `offset`/`limit` are necessary, per project CLAUDE.md "Reading Large Files" rule.

### Key locations to remember

| Concept | Location |
|---|---|
| T-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` |
| DelegationJob spec | `contracts.md:59-73` |
| PendingServerRequest | `contracts.md:75-91` |
| Execution domain policy defaults | `foundations.md:99-116` |
| Execution profile source categories | `foundations.md:223-241` |
| Split-runtime rationale (session-scope isolation) | `foundations.md:71-75, :152-156` |
| Delegation crash recovery | `recovery-and-journal.md:116-123` |
| Unknown requests fail-closed | `recovery-and-journal.md:132-141` |
| Current runtime wrapper | `runtime.py:78-134` (advisory only) |
| Sandbox: WorkspaceWritePolicy | `schemas.json:8019-8062` |
| Sandbox: ReadOnlyAccess (with includePlatformDefaults default) | `schemas.json:6863-6907` |
| Approval: command | `ServerRequest.json:367` |
| Approval: file change | `ServerRequest.json:608` |

## Context

### Mental model

Framing: **This is a decision-decomposition problem, not a description problem.** The scrutiny's Q0a/Q0b split shifted my frame. Initially I was answering "what's the right shape?" — but that bundled two layers: "do we need a new concept?" (Q0a) and "if so, what fields?" (Q0b). Once decomposed, the answer to Q0a is "the foundation already expresses scope; don't invent a new concept" — and Q0b is then N/A.

Core insight: **The foundation spec + App Server schema together ARE the scope descriptor.** I don't need to invent one. I just needed to recognize what's already there. The execution profile (`foundations.md:228-241`) already treats "writable scope" as a first-class source category; the sandbox schema (`schemas.json:8019-8062, :6863-6907`) already gives mechanical enforcement primitives. Writing a new `DelegationScope` type would have been creating a new concept where one already existed implicitly.

Mental model: **Foundation-as-shape.** For the execution domain, the foundation spec is more load-bearing than the contracts.md data model for this particular concept. The contracts.md types tell you *what state is persisted*; the foundation tells you *what properties the runtime must have*. Scope happens to be better expressed in the second language for v1.

### Project state at session close

**T-20260330-05 (execution-domain foundation):** OPEN, high priority. Q0 RESOLVED via design pass this session. Pre-Design Reconciliation section preserved as history; Design Decision section landed; ACs updated (new sandbox-construction AC + approval-routing clarification + tests extension). AC-locking gate released. Ready for implementation.

**T-20260330-04 (dialogue parity and scouting retirement):** CLOSED (prior session).

**T-20260330-06 (promotion flow + delegate UX):** OPEN. Blocked by T-05.

**T-20260330-07 (analytics, reviewer, cutover):** OPEN. Blocked by T-05/T-06. Has known wording mismatch (carried forward from prior session).

**T-20260416-01 (codex.dialogue.reply extraction mismatch):** OPEN, medium priority. Independent of T-05 — can run as parallel thread.

### Environment snapshot at session close

- Branch: `main`
- HEAD: `b468e86f` (Q0 decision record merge)
- Working tree: clean
- Origin/main: synced (pushed this session `2813e469..b468e86f`)
- Memory: no new feedback files; MEMORY.md unchanged
- Context: ~22% of 1M (session ended well before threshold)

### Why this work matters (bigger picture)

The codex-collaboration plugin is the intended successor to the cross-model plugin; the full supersession completes when T-05, T-06, and T-07 land. T-05 is the execution-domain foundation — without it, Codex cannot autonomously execute code in isolation. Delivering T-05 unblocks the "execution" half of the plugin's capability surface (the "advisory" half landed earlier in D-prime). Design-gate closure on Q0 is what makes T-05 implementable.

## Learnings

### Schema defaults are load-bearing; read them, don't trust names

**Mechanism.** Sandbox policies carry implicit defaults in their schema. `includePlatformDefaults: true` by default means a "restricted" readable-roots list silently includes platform defaults. The override is required, not optional, for true worktree-only reads.

**Evidence.** `schemas.json:6867-6870` shows the default. The scrutiny's High-severity finding flagged this. Had I shipped the AC without `includePlatformDefaults: false`, the sandbox would have overclaimed its behavior.

**Implication.** When reading a schema's type definitions, always check `default` fields. "Type is restricted" is not the same as "behavior is restrictive" — the default-populated fields determine actual behavior.

**Watch for.** Future sandbox/policy work. Any field with a `default` in the schema is a place where implicit behavior diverges from the type's name.

### Substrate-aligned naming > historical-lineage naming

**Mechanism.** When designing a plugin-side type that maps to enforcement-layer fields, name the plugin fields to match the enforcement layer's vocabulary — not some prior concept's vocabulary. The translation burden compounds across every codebase interaction.

**Evidence.** My initial Option C used `allowed_roots` (dialogue vocabulary from gatherer agents). The App Server sandbox uses `readableRoots`/`writableRoots`. User push: "Reusing `allowed_roots` as a subfield in a supposedly distinct execution contract preserves a translation layer instead of removing one."

**Implication.** Naming matters most at the layer where future-Claude spends time. For a delegation-execution concept, that's the enforcement layer. For a dialogue-prompt concept, it's the prompt layer. Pick based on where the concept lives.

**Watch for.** Future cases where a new type maps to an external enforcement surface. Start with the substrate's vocabulary, then decide if lineage-naming adds or subtracts.

### Decomposing bundled decisions surfaces overreach

**Mechanism.** "What descriptor do we need?" is often two decisions in one: (a) "do we need a new concept?" and (b) "if so, what fields?" Bundling them conceals the possibility that the answer to (a) is "no, the foundation already expresses it."

**Evidence.** The scrutiny's Q0a/Q0b split turned a `Major revision` verdict into actionable guidance. My initial framing had argued "delegation is different from dialogue, therefore freeze this rich descriptor now" — the "therefore" hid a second decision.

**Implication.** When making recommendations on multi-layer questions, explicitly name the sub-decisions. "Here's Q0a (conceptual) and here's Q0b (specific). My answer to Q0a is X; conditional on X, my answer to Q0b is Y."

**Watch for.** Any design recommendation that starts "therefore we should..." — the "therefore" is often the hidden decision boundary.

### "Reserved slot" patterns can be over-specification in disguise

**Mechanism.** Adding a typed enum field with only one valid value for v1 ("reserved slot for future expansion") commits to a vocabulary for a concept whose semantics haven't been defined. The commitment looks forward-compatible but pre-binds decisions that will feel wrong later.

**Evidence.** My initial Option C included `mutation_policy: immutable` as a single-valued enum. T-05's Q3 explicitly treats mutation semantics as open (`:134-139`). Freezing a vocabulary before the state-transition model exists is premature.

**Implication.** For genuinely future-open decisions, prose rules ("v1 scope is immutable") are safer than typed enums. Add the enum when the state model actually emerges. Field-level forward-compat isn't always compat.

**Watch for.** Any type with "reserved," "default only value," or "single-valued enum for now" smells.

### Verify citations before propagating — even in your own recommendations

**Mechanism.** When citing substrate evidence (schema files, spec lines), verify the exact content at those lines. Line numbers and named fields are often close-but-not-exact; verifying catches overclaims.

**Evidence.** This session's scrutiny cited `schemas.json:6867` for `includePlatformDefaults`; the actual default is at `:6868`. The broader claim was correct, but the precise cite was off-by-one. Same pattern: my own initial recommendation confidently described sandbox fields I hadn't verified against the schema.

**Implication.** Before recommending, verify every cited substrate claim against the actual file content. Close-to-right citations can hide wholly-wrong claims.

**Watch for.** Recommendations that cite schema fields, line numbers, or API shapes. These are the most likely places for overclaim-by-imprecision.

### One-round convergence with structured scrutiny + citation verification

**Mechanism.** When user scrutiny comes with numbered findings, severity, and specific file:line citations, the response pattern is: verify each cite in parallel, then either concede (all verified, adopt revised position) or push back with counter-evidence. This converges in one round.

**Evidence.** This session's arc: my Option C → 5-critical-failures scrutiny → verification → revised Option D → 3-refinement approval → commit. One review cycle, not multiple. Prior session (T-04 closeout) showed the same pattern.

**Implication.** User's "iterative refinement with fast convergence" preference is enabled by structured input. The format's load-bearing property is evidence-citability — without citations to verify, scrutiny would take multiple cycles to converge.

**Watch for.** Future sessions where scrutiny is less structured. Consider asking for citations explicitly if scrutiny arrives as unstructured prose.

### "Create new commit, not amend" applies to decision records too

**Mechanism.** Even for a decision record that's conceptually one change, project rule says create a new commit rather than amend. This session landed the decision as `cf8ecc79` (feature branch commit) + `b468e86f` (--no-ff merge). Two commits on main, not one.

**Evidence.** Prior session's `b6e9ef5e` (review fixes separate from `6ed5f731`) is the direct precedent. Project CLAUDE.md rule is uniform.

**Implication.** Don't look for "clean single commit" aesthetics when the project rule prefers visible history. Audit trail > cosmetic tidiness.

**Watch for.** Temptation to `--amend` on feature branches when adding refinements. Default: new commit.

## Next Steps

### 1. T-05 implementation — first task is narrow Q2/Q4 verification (next critical-path work)

**Dependencies:** None. T-05 AC-locking is unblocked via the new Design Decision section. Branch-protection rules apply (create a working branch before edits).

**First-next-action:** Before building the worktree + runtime plumbing, confirm the narrow Q2/Q4 prerequisites:
1. `runtime.py` can be extended to construct `workspaceWrite` sandbox with restricted `readOnlyAccess` (including `includePlatformDefaults: false`) per the App Server schema. Today's code at `:121-134` only builds `{"type": "readOnly"}` for advisory — the execution path needs the richer shape.
2. The approval path preserves the request-relevant payload cleanly through `PendingServerRequest.requested_scope: object` without shape-coercion. Grep for existing control-plane code that handles server-requests and confirm the plugin's handling is opaque-carrier, not normalizing.

**What to do:**
1. Pre-flight: `git status` clean on main at `b468e86f`; create `feature/t05-execution-runtime` (or similar per branch conventions)
2. Read T-05 ticket in full (includes Pre-Design Reconciliation + new Design Decision section + updated ACs)
3. Read `runtime.py` end-to-end; trace through the advisory `sandboxPolicy` construction at `:121-134`; plan the execution-path extension
4. Search for existing control-plane code that handles `PendingServerRequest` — confirm payload preservation is opaque (likely in `control_plane.py`)
5. Grep for any existing test fixture that uses `workspaceWrite` sandbox construction
6. Implement execution runtime wrapper + worktree creation + job persistence (ACs 1-3)
7. Implement sandbox-policy construction per the new AC 2 (full `workspaceWrite` + restricted `readOnlyAccess` with `includePlatformDefaults: false`)
8. Implement Job Busy response + max-1 concurrent enforcement (AC 4)
9. Implement approval-routing surface (AC 5) — preserve raw payloads opaquely; no normalization
10. Write tests per AC 6 (worktree, busy, runtime lifecycle, sandbox construction)

**Estimated effort:** Large. T-05 is the execution-domain foundation packet — multiple build items, several files modified.

### 2. T-20260416-01 extraction bug fix (parallel thread)

**Dependencies:** None. Independent of T-05.

**What to do:** Implement Option A from the ticket — canonicalize `agent_message` extraction at runtime dispatch (`runtime.py:173-177`), moving `_read_turn_agent_message` from controller to a shared helper. Estimated: ~15-25 production lines + ~30-50 test lines.

**Unchanged from prior handoff.** The 3-reproduction + 1-non-reproduction pattern (B3, B5 reproduced; B8 didn't) documented in the ticket. NOT turn-count-driven.

### 3. T-07 wording mismatch patch (when T-07 is picked up)

**Dependencies:** T-07 becomes active.

**What to do:** Reconcile T-07's "removal only if T-04 records a passing benchmark result" at `:41`, `:59` with T-04's actual closure (demonstrated-not-scored). Either rephrase T-07's gate or add an interpretive note pointing to T-04's Resolution section.

**Unchanged from prior handoff.**

### 4. Reference unification (still-open T-04 §2.2 item)

**Dependencies:** None; low priority.

**What to do:** Factor `dialogue-codex` skill to a thin adapter over the production-local extracted reference doc. Natural home: T-07 migration work, or standalone cleanup.

**Unchanged from prior handoff.**

### 5. Landing sequence

T-05 → T-06 (promotion + UX) → T-07 (analytics, reviewer, cutover). Cross-model supersession completes when T-07 lands. Still several weeks of work total.

## In Progress

**Clean stopping point.** Q0 decision record committed, merged, pushed. No work in flight in git or in conversation.

- **Approach:** Design pass → structured recommendation → scrutiny → verification → revised recommendation → refinement → commit → merge → push.
- **State:** main at `b468e86f`, working tree clean. T-05 AC-locking released.
- **Working:** All verified citations confirmed; all three scrutiny refinements landed; commit + merge + push succeeded.
- **Not working:** Nothing. All session-scoped success criteria met.
- **Next action:** Pick up T-20260330-05 implementation in a fresh session. Start with narrow Q2/Q4 verification per Next Steps #1.

## Open Questions

### 1. Will T-05 implementation reveal gaps in infrastructure-only scope?

**Context:** The Design Decision records v1 commitment to "no new DelegationScope type." Implementation may surface use cases (sub-worktree path restriction, cross-job policies) not foreseen in the design pass. The decision's v1-scoping hedge anticipates this.

**Impact:** HIGH if gaps surface. MEDIUM otherwise — adding a typed descriptor later is a clean additive change.

**Decision pending until:** T-05 implementation is well underway; gaps would surface during worktree+runtime+approval work.

### 2. Does the existing control plane code preserve `requested_scope` opaquely?

**Context:** The Design Decision commits to "v1 performs no normalized comparison." If the current plugin code happens to coerce `PendingServerRequest.requested_scope` payloads somewhere (e.g., during deserialization), the v1 commitment becomes a fix-and-preserve, not just a spec.

**Impact:** MODERATE. Verification is part of Next Steps #1.

**Decision pending until:** First implementation step (the narrow Q2/Q4 verification).

### 3. Will Q3 mutation policy need to change before T-07?

**Context:** v1 prose rule is "scope immutable." If T-06 UX introduces scope-widening-via-approval (e.g., "allow this job to write outside its worktree just this once"), the immutability becomes a blocker.

**Impact:** MODERATE. Probably handled in T-06 scope if it comes up; T-05 doesn't need to commit to mutation semantics.

**Decision pending until:** T-06 scope is picked up.

### 4. Is `grantRoot` likely to be honored or dropped in future App Server versions?

**Context:** `FileChangeRequestApprovalParams.grantRoot` is marked `[UNSTABLE]` in the schema docstring. Future App Server versions may behave differently.

**Impact:** LOW for v1 (we escalate; Claude decides via `codex.delegate.decide`). MODERATE if post-v1 automatic grantRoot honoring becomes desirable.

**Decision pending until:** schema versions beyond 0.117.0 clarify the marker.

## Risks

### 1. Implementation surfaces reveal infrastructure-only scope is insufficient

**Impact:** If T-05 implementation shows that `workspaceWrite` + restricted reads don't express everything needed (e.g., per-directory write permissions within the worktree), the v1 decision would need revisiting.

**Mitigation:** The Design Decision explicitly records this as a v1 commitment with a forward-path hedge. Adding a typed `DelegationScope` later is pre-authorized.

### 2. `includePlatformDefaults: false` forgotten in implementation

**Impact:** If the runtime wrapper constructs `workspaceWrite` without explicitly setting `includePlatformDefaults: false`, the sandbox silently includes platform-default readable roots. AC would be unmet; sandbox would leak.

**Mitigation:** Explicit in the new sandbox-construction AC. Resolution section shows the full `SandboxPolicy` shape with the override. First-task verification in Next Steps #1 catches this.

### 3. Approval path shape-coercion risk

**Impact:** If existing plugin code coerces `requested_scope` payloads (e.g., strips fields, normalizes shapes), the v1 "preserve opaquely" commitment becomes a fix-and-preserve not just a spec.

**Mitigation:** Next Steps #1's narrow Q2/Q4 verification includes this check. If coercion exists, it's a single-file fix before main implementation begins.

### 4. Ticket review burden grows

**Impact:** T-05 ticket grew from ~206 to ~293 lines. Readers must scroll past Pre-Design Reconciliation history + Design Decision record to reach ACs.

**Mitigation:** Section structure is clear (Problem → Scope → Pre-Design Reconciliation → Design Decision → ACs → Verification → Dependencies → References). Table of contents isn't necessary at this length.

### 5. Schema version drift

**Impact:** App Server schema at `0.117.0/` is the pinned version. If a newer schema changes sandbox shape semantics, the v1 decision may need re-verification.

**Mitigation:** Project uses pinned schemas for contract tests. Any schema upgrade would trigger explicit verification.

## References

### Commits this session

| Commit | Branch | Subject |
|---|---|---|
| `cf8ecc79` | `docs/t05-q0-decision-record` | docs(t20260330-05): record Q0 design decision (implicit scope from infrastructure) (1 file, 90/3) |
| `b468e86f` | `main` (merge) | Merge branch 'docs/t05-q0-decision-record': T-05 Q0 design decision record |

Pushed to origin/main: `2813e469..b468e86f`.

### Authority documents

| Document | Location | Role |
|---|---|---|
| T-20260330-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | Design Decision landed here this session; ACs updated |
| contracts.md (normative) | `docs/superpowers/specs/codex-collaboration/contracts.md` | DelegationJob at `:59-73`; PendingServerRequest at `:75-91` (`requested_scope: object` at `:88`) |
| foundations.md (normative) | `docs/superpowers/specs/codex-collaboration/foundations.md` | Execution domain at `:99-116`; context profiles at `:223-241`; trust boundaries at `:118-148`; split-runtime rationale at `:71-75`, `:152-156` |
| recovery-and-journal.md (normative) | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Delegation crash at `:116-123`; unknown requests fail-closed at `:132-141` |
| promotion-protocol.md (normative) | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | Promotion state machine; preconditions |
| App Server schema (fixture, v0.117.0) | `packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/codex_app_server_protocol.v2.schemas.json` | ReadOnlyAccess at `:6863`; `includePlatformDefaults` default at `:6867-6870`; WorkspaceWriteSandboxPolicy at `:8019-8062`; `readOnlyAccess: fullAccess` default at `:8039-8041`; `writableRoots` at `:8050` |
| App Server ServerRequest (fixture, v0.117.0) | `packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/ServerRequest.json` | `CommandExecutionRequestApprovalParams` at `:367`; `FileChangeRequestApprovalParams` at `:608` with `grantRoot` marked `[UNSTABLE]` at `:610-611` |
| Runtime wrapper | `packages/plugins/codex-collaboration/server/runtime.py` | Current sandbox construction at `:121-134` (advisory only); JSON-RPC transport |
| Hooks | `packages/plugins/codex-collaboration/hooks/hooks.json` | SubagentStart matcher at `:14-22` (gatherers excluded) |

### Memory files referenced this session

All under `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/`:

| Memory | Relevance |
|---|---|
| `feedback_edit_in_repo.md` | Applied — edits landed in `packages/plugins/codex-collaboration/` paths (though only for reads this session; no package code changed) |
| `feedback_contract_text_over_operational_interpretation.md` | Applied — verified contract text (foundations.md, contracts.md, schema) over my initial operational reasoning |
| `feedback_system_prompt_mentions_not_scouting_signals.md` | Not directly applicable this session (no transcript auditing) |
| Prior session's user-preferences captures | Applied — structured-review pattern, fast convergence, "preserve historical" pattern from T-04 closeout |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-17_01-41_t04-closed-ac7-direct-and-t05-kickoff-note-merged.md`
- T-04 closeout chain (same-day 04-16): archived sequence
- T-05 kickoff note: committed via prior session's `6ed5f731` + `b6e9ef5e`; merged at `2813e469`

## Gotchas

### 1. `includePlatformDefaults` default is `true` — must be explicitly overridden

**Symptom:** Constructing `readOnlyAccess: {type: "restricted", readableRoots: [worktree_path]}` without `includePlatformDefaults: false` still includes platform-default readable roots. Sandbox is looser than the code reads.

**Root cause:** Schema at `schemas.json:6867-6870` defaults `includePlatformDefaults: true`. Absence of the field means "true," not "default omitted."

**Prevention:** The new sandbox-construction AC (ticket line in AC block) explicitly specifies `includePlatformDefaults: false`. Any future code setting sandbox policy must include the override.

### 2. `grantRoot` is `[UNSTABLE]` — don't design around it

**Symptom:** Reading the file-change approval schema, `grantRoot` looks like a useful field for automatic sandbox widening.

**Root cause:** `ServerRequest.json:610-611` — the docstring says "unclear if this is honored today." Schema-level warning.

**Prevention:** v1 approval routing preserves the field in the opaque payload but doesn't design automatic honoring. Escalate to Claude via `codex.delegate.decide`.

### 3. Command and file-change approval payloads diverge

**Symptom:** Expecting a unified "what's being requested?" shape across approval types.

**Root cause:** `CommandExecutionRequestApprovalParams` (`ServerRequest.json:367`) and `FileChangeRequestApprovalParams` (`:608`) have different fields. `PendingServerRequest.requested_scope: object` is the plugin's opaque carrier that absorbs either shape.

**Prevention:** v1 performs no normalized comparison. The Design Decision explicitly records this. Future normalization work must define the shape deliberately.

### 4. `runtime.py` currently hardcodes `{"type": "readOnly"}` for advisory

**Symptom:** Looking at `runtime.py` for how to construct the execution sandbox — the only `sandboxPolicy` construction is advisory.

**Root cause:** The execution runtime path hasn't been implemented yet. `runtime.py:78-134` handles advisory (`AppServerRuntimeSession` with `readOnly` sandbox); execution wrapper is part of T-05 implementation.

**Prevention:** Next Steps #1 starts with this verification. The execution path needs the richer `workspaceWrite` shape, constructed fresh — not a copy-paste-and-tweak of the advisory path.

### 5. Branch protection hook blocks edits on main

**Symptom:** Trying to Edit a file while on `main` produces a hook block.

**Root cause:** `.claude/rules/workflow/git.md` enforces this; `PreToolUse` hook rejects Edit/Write on protected branches.

**Prevention:** Checkout a working branch BEFORE any Edit tool call. Pattern: `git checkout -b docs/...` or `feature/...` first, then Edit.

### 6. Reading large schema files requires `offset`/`limit`

**Symptom:** The App Server schema fixture is ~12.7K lines. Reading it whole per the default Read behavior (2K lines) would be truncated and slow.

**Root cause:** Schema fixtures are large. Project CLAUDE.md's "Reading Large Files" rule applies.

**Prevention:** `wc -l` first. For files >2000 lines, use `offset`/`limit` targeting specific sections. This session used narrow windows around `:6863-6920`, `:8010-8090`, `:355-415`, `:595-655`.

### 7. T-05 ticket grew to ~300 lines — scroll past history for current state

**Symptom:** Reader lands on the ticket and sees Pre-Design Reconciliation text at line 62; has to scroll past ~100 lines of history to reach the current Design Decision.

**Root cause:** Preserved historical block + appended Decision = cumulative ticket size.

**Prevention:** Section headers are explicit. The "Design Decision: Scope-Transport Resolved (v1)" section is clearly labeled and bracketed. Table of contents isn't necessary but could be added later if the ticket grows further.

## Conversation Highlights

### User's "Continue with T-05 design pass" (session start)

Terse directive matching the "two-word approvals" pattern from prior session. Triggered the full design-pass arc. No elaboration needed — the prior handoff's Next Steps #1 was explicit enough to interpret.

### User's /scrutinize output on Option C

Structured format: `Premise Check` → `Critical Failures` (5 items, each with `Severity: High/Medium` and "What must change") → `High-Risk Assumptions` → `Real-World Breakpoints` → `Hidden Dependencies` → `Adversarial Perspectives` → `Patterns And Root Causes` → `Required Changes Before This Is Credible` → `Verdict`. The systemic finding:

> "The findings are mostly one systemic problem, not five independent mistakes: the recommendation jumps from 'delegation is different from dialogue' to 'therefore freeze a rich new permission descriptor now.' The distinction is probably real. The proposed contract shape and ranking are not yet disciplined enough by the actual runtime substrate or by the v1 workload assumptions."

Verdict: `Major revision`.

### User's three refinements (post-verification)

Delivered compactly after I presented the revised Option D position. The High-severity catch:

> "the new sandbox AC is still slightly wrong as written. `readOnlyAccess: {type: 'restricted', readableRoots: [worktree_path]}` does **not** mean 'reads restricted to `worktree_path` only' unless you also set `includePlatformDefaults: false`; the schema defaults that flag to `true`. Without that, the AC overclaims the read boundary."

The Medium-severity refinements (Q3 citation scope, approval-routing wording) were delivered in the same structure. Each refinement came with an exact-wording suggestion in a code block — easier to apply verbatim than paraphrase.

### User's approval to proceed without another review

> "With those changes, I would not ask for another pre-edit review round."

Explicit permission matching the "fast convergence" pattern — signals alignment has been reached and further review would be friction. Enabled the single-message branch+edit+commit+merge+push execution.

### User's "preserve historical, append Resolution" confirmation

> "The 'preserve historical block, append a later decision record' approach is the right one. Rewriting the pre-design section would erase the design-pass history."

Matches the T-04 closeout pattern verbatim. Reinforces the audit-trail-preservation preference.

### Session pacing

User's prior-session pattern of "lock in handoffs before analytical thresholds" not applicable here — session ended at ~22% context after clean deliverable landing, not under context pressure. The /save was user-initiated for the next-session-primed pattern, not an emergency capture.

## User Preferences

### Structured review with exact citations and severity labels

User's scrutiny came as `Critical Failures` with numbered items, severity labels (`High`/`Medium`), file:line citations, and explicit "What must change" text per finding. Pattern: treat the format as load-bearing. Verify cites in parallel. Either concede (all verified, adopt revised position) or push back with counter-evidence. One-round convergence when scrutiny is evidence-cited.

### Decomposing bundled decisions

User said: "Split the decision in two: Q0a distinct descriptor vs reuse/implicit shape, then Q0b exact v1 fields." Preference for separating abstract from specific when recommendations bundle them. Transferable to future decision-presentation.

### Substrate-aligned naming

User pushed naming toward `readableRoots`/`writableRoots` (App Server schema vocabulary) rather than `allowed_roots` (dialogue vocabulary). Preference: align plugin-side types with the enforcement substrate they map to, not with historical-lineage vocabulary.

### Explicit v1 hedges

User said: "Record this as a v1 decision, not a permanent rejection of a future typed descriptor." Preference for time-scoping decisions explicitly in spec text — keep forward paths open without fighting a "we rejected this" signal.

### Fast convergence once aligned

User said: "With those changes, I would not ask for another pre-edit review round." Explicit permission to execute without another review cycle once the three refinements were applied. Pattern: don't over-review after agreement reached.

### Preserve historical records

User said: "The 'preserve historical block, append a later decision record' approach is the right one. Rewriting the pre-design section would erase the design-pass history." Preference: never retcon audit trails. Matches the T-04 closeout pattern ("Status: Open" → "Historical status at addendum authoring time: Open").

### Exact wording in code blocks for corrections

User's refinements came with exact-wording code blocks (e.g., the `readOnlyAccess: { ... includePlatformDefaults: false }` block). Preference: when correcting someone's draft, provide the exact replacement rather than paraphrased guidance. Easier to apply verbatim.

### Terse when aligned

Short responses like "Standing by for your review" / "Continue with T-05 design pass" / "merge and push" continue to signal alignment — terseness is a feature. Expanded responses come only when content requires it (scrutiny, refinements).

### /copy followed by substantive instruction

User's `/copy` invocations (3 this session) were followed by real instructions in subsequent messages. Pattern matches prior session memory: `/copy` captures to clipboard; standing by for the actual instruction is the right move. Don't engage with clipboard contents unless explicitly asked.

## Rejected Approaches

### Initial Option C: New DelegationScope type with 4 fields

**Approach:** Introduce a new `DelegationScope` type in contracts.md with `allowed_roots: string[]`, `writable_roots: string[]`, `exec_policy: enum`, `mutation_policy: enum`. Add as a field on `DelegationJob`. Present as "minimum viable for v1 with reserved slots for future expansion."

**Why it seemed promising:** Delegation's divergence from dialogue (durability, operation types, mutation policy) did motivate a distinct concept. Reusing `allowed_roots` as a subfield preserved naming lineage to dialogue. The reserved-slot pattern looked forward-compatible.

**Why it failed (per verified scrutiny):**
1. `exec_policy` invented beyond verified substrate — App Server sandbox has `networkAccess: bool` and that's it for exec-flavored control; no exec-policy field exists
2. C5 "interop with `requested_scope`" criterion presupposed a normalized shape that doesn't exist; `requested_scope: object` is deliberately untyped
3. Case against Option D was weak — "jobs routinely need to read docs/specs outside worktree" was false (worktree IS a full checkout)
4. Naming aligned to dialogue vocabulary (`allowed_roots`) rather than substrate vocabulary (`readableRoots`/`writableRoots`) — preserves translation layer
5. `mutation_policy: immutable` was premature contract freeze — T-05 explicitly treats mutation semantics as open

**What it taught:** For decisions spanning contract + runtime + approval-routing, verify enforcement substrate BEFORE committing to shape. Substrate-aligned naming > lineage-aligned naming when purposes differ. Decomposing Q0a/Q0b surfaces overreach. "Reserved slot" patterns can be over-specification in disguise.

### Option B: Extend `scope_envelope` in place

**Approach:** Modify the canonical `scope_envelope` shape to add operation-types + mutation fields. Dialogue gatherers keep using the subset they need.

**Why rejected:** Damages dialogue's simple ephemeral contract. Gatherers must tolerate fields that don't apply to them. Mixes conceptual levels (ephemeral prompt hint vs. durable state). Not just conceptually awkward — would force changes to gatherer agents that don't need them.

**Trade-off:** One concept system-wide. Acceptable only if dialogue and delegation converge toward the same enforcement model, which they don't.

### Option A: Adopt dialogue shape as-is

**Approach:** Put `scope_envelope: {allowed_roots: string[]}` directly on DelegationJob — same shape as dialogue.

**Why rejected:** Shape has no durability semantics, no mechanical-enforcement hook, and collides on name with a different-purpose concept in dialogue. Under-specified for delegation on every criterion.

**Trade-off:** Name-reuse signals conceptual continuity. But the continuity is wrong — cooperative vs. mechanical is a different kind of scope.

### Option E: Deferral stance (no descriptor for v1)

**Approach:** Spec'd "v1 delegation jobs have no scope descriptor; approval routing escalates on every out-of-worktree operation."

**Why rejected:** Makes the existing approval-routing AC hollow — with no scope to compare against, every server request is an escalation. Kills UX. Doesn't actually answer the T-05 kickoff question; it's skipping.

**Trade-off:** Clear and honest. But operationally untenable.

### Null option: Defer Q0 decision

**Approach:** Don't answer Q0 this session; T-05 stays blocked pending external input or more design work.

**Why rejected:** Handoff's Next Steps #1 was "pick up T-05 with the design pass"; deferring undoes that. Doesn't match user's stated goal. No new information available that would change the substrate.

**Trade-off:** Buys time. At the cost of project progress.

### Rewrite Pre-Design Reconciliation section to reflect resolution

**Approach:** Replace the existing "Pre-Design Reconciliation: Inherited Scope-Transport Question" block with a new "Design Decision" block — single section instead of two.

**Why rejected:** Erases the design-pass history. Violates the audit-trail-preservation pattern from T-04 closeout. User explicit rejection: "Rewriting the pre-design section would erase the design-pass history."

**Trade-off:** Shorter ticket. Accepted as not worth the audit cost.

### Amend the single commit with refinement fixes

**Approach:** Use `git commit --amend` instead of creating separate commits for the decision + any review fixes.

**Why rejected:** Violates project rule "Prefer to create a new commit rather than amending." Applies even on unmerged feature branches per prior-session memory.

**Trade-off:** Cleaner single commit on feature branch. Not worth fighting the rule.

### Another Codex Delta round on the revised position

**Approach:** Run a cross-model check (`codex.consult`) on the revised Option D recommendation before executing.

**Why rejected:** User explicit permission to proceed: "With those changes, I would not ask for another pre-edit review round." The user's own scrutiny had already performed the cross-perspective check; a Codex round would have been redundant.

**Trade-off:** One more verification round. Explicitly declined by user.

### Create a separate prerequisite ticket for scope-transport

**Approach (considered by prior session, referenced here):** Open T-04.5 or T-05-pre as a scope-transport ticket separate from T-05 proper.

**Why rejected (prior session, upheld here):** The design question only matters in T-05's context; separating creates artificial coupling and governance overhead. The inline Design Decision section keeps the resolution where it belongs.

**Trade-off:** T-05 ticket grows. Accepted.
