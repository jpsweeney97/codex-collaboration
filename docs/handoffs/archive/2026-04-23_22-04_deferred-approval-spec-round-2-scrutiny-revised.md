---
date: 2026-04-23
time: "22:04"
created_at: "2026-04-24T02:04:59Z"
session_id: c16cedb1-0a58-47b8-bd19-2cba033afa48
resumed_from: "docs/handoffs/archive/2026-04-23_21-14_packet-1-deferred-approval-spec-drafted.md"
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: a0d58408
title: "Packet 1 deferred-approval spec — rounds 1+2 scrutiny addressed; awaiting round 3"
type: handoff
files:
  - docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md
  - .gitignore
  - packages/plugins/superspec/scripts/spec-size-nudge.sh
  - /Users/jp/.claude/CLAUDE.md
---

# Handoff: Packet 1 deferred-approval spec — rounds 1+2 scrutiny addressed; awaiting round 3

## Goal

Drive the Packet 1 (deferred same-turn approval response) design spec to the point where it closes on approved design — spec is review-ready, all identified defects are fixed, and the next step (writing-plans) can begin. Unblocks T-20260423-01 (parent acceptance-gap ticket; AC1 = end-to-end delegation with platform-tool verification) via T-20260423-02 (the Packet 1 design ticket).

**Trigger:** User invoked `/load` at session start, then pasted round-1 scrutiny via `/copy`. Later in the session pasted round-2 scrutiny via `/copy`. Session ends after round 2 fixes committed; user is about to produce round-3 scrutiny to start the next session.

**Stakes:** High. This is the third design attempt at the live-turn approval mechanism (first was rejected at commit `edff9c07`; second draft was the round-1 starting point). Every round of scrutiny that ships identifies real structural defects. Shipping a round-3-untested spec risks another rejection cycle or — worse — letting implementation begin on a contract that still has transactional holes.

**Bigger picture:** Packet 1 closes the design phase for T-20260423-02; Packet 2 (amendment admission) stacks on top; T-20260423-01 AC1 needs both. The `/dialogue` and `/delegate` codex-collaboration features depend on T-20260423-01 AC1 being unblocked to actually reach end-to-end delegation.

**Session's progress:** Round 1 closed (8 findings, all fixed, commit `2ab19836`). Round 2 closed (5 findings, all fixed, commit `a0d58408`). Spec went from 971 → 1206 lines across rounds. Now awaiting round 3.

## Session Narrative

**Session began with `/handoff:load`.** Predecessor handoff `2026-04-23_21-14_packet-1-deferred-approval-spec-drafted.md` archived. State file written. Immediate context: 971-line spec on working tree, uncommitted, awaiting user review.

**Phase 1 — Round 1 scrutiny (8 findings).** User pasted structured scrutiny via `/copy` listing 3 critical + 3 high-risk + 2 edge findings. I invoked `superpowers:receiving-code-review` skill to enforce the "verify before implementing" pattern, then ran 8 parallel reads to check each finding against file:line evidence. All 8 verified:

- F1 (start handshake missing) — spec:116-119 defined only register/publish/discard; no capture-ready primitive
- F2 (payload mapping missing) — spec:153 had generic `session.respond(rid, payload)` with no kind→App Server payload table for approve/deny
- F3 (journal ordering race) — spec:146 diagram and spec:401 prose contradicted each other on publish=CAS+signal vs CAS-separate-from-publish
- F4 (singleton gate not named) — IO-3 relied implicitly on controller:328-349 busy gate
- F5 (MCP custom serializer wrong) — mcp_server.py:505-516 has custom branch reading 5 soon-to-be-removed fields
- F6 (fsync overclaim) — jsonrpc_client.py:123 only flushes, doesn't fsync; the fsync claim at spec:478 was doubly wrong (code doesn't do it + pipes have no backing store)
- F7 (timeout mutator contradicts diagram) — spec:185 called `record_response_dispatch` which requires `action=approve|deny`, incompatible with timeout's `resolution_action=None`
- F8 (protocol echo overstated) — docs/codex-app-server.md:987, 1004 say `serverRequest/resolved` fires on lifecycle cleanup too, not just our response

**Phase 2 — Round 1 execution.** User chose Path A (in-place revision) with design call: `deny → decline` for command/file kinds; `cancel` reserved for timeout/abort; `request_user_input + deny` uses known-denial `{"answers": {}}` fallback with explicit limitation note. Created 10 tasks (F1-F8 plus F3 split into registry/diagram/prose). Executed sequentially. Key addition: `wait_for_parked` capture-ready primitive with `ParkedCaptureResult` sum type (`Parked` / `TurnCompletedWithoutCapture` / `WorkerFailed` / `CaptureTimeout`). Mid-edit I caught myself adding a speculative `origin: Literal["decide", "timeout"]` field to `OperationJournalEntry` — pulled it back as scope creep since `action="approval_timeout"` audit event + `timed_out=True` already discriminate. Spec grew to 971 lines.

**Phase 3 — Commit #1 (2ab19836).** Committed spec + `.gitignore` bundle: `docs: draft Packet 1 deferred-approval design spec (T-20260423-02)`. Not yet pushed.

**Phase 4 — Configuration archaeology tangent.** User asked: "Where is my <1000 line preference encoded? I want to loosen that restriction." Ran grep against memory, CLAUDE.md files, hooks, and plugin configs. Found **the `<1000` preference is NOT encoded anywhere** — it's only in session memory carried via handoff chain. The actual encoded threshold is the 500-line nudge at `packages/plugins/superspec/scripts/spec-size-nudge.sh:35`. User chose "Bump threshold from 500 to 3000" — executed (Edit changed both the `-gt 500` guard AND the user-visible message text "Files over 500 lines..." to stay in sync).

**Phase 5 — Commit #2 (533f015a).** `chore(superspec): raise spec-size-nudge threshold from 500 to 3000`.

**Phase 6 — Commit rule archaeology.** User asked: "Where are those standing instructions regarding commits?" Same pattern: verified the "only commit when explicitly asked" rule is in Claude Code's built-in system prompt, NOT in the user's global CLAUDE.md (grep for "commit\|Committing" returned nothing from `/Users/jp/.claude/CLAUDE.md`). User's own Git section only covered branch protection. User chose Option 1 (scoped relaxation) and asked me to draft + add to global CLAUDE.md. Wrote a new `### Commits` subsection under the existing `## Git` section (matching the Environment-section sub-structure pattern). Includes explicit override language: "This overrides the default commit-gating behavior from the Claude Code system prompt."

**Phase 7 — Round 2 scrutiny (5 findings).** User pasted second scrutiny via `/copy`: 3 critical (claim-deadlock, decision=None invalid, timer violates thread model) + 2 high-risk (poll window overclaim, unknown-kind gap). Verified all 5. Key discoveries:

- `journal.py:241-245` `append_audit_event`: just `open("a") + write`, NO `flush()`, NO `os.fsync()`. Compared to `:300-307` `write_phase` with `flush() + os.fsync()`. Durability gap is real.
- `journal.py:124-136` validator requires `isinstance(decision, str)` — REJECTS `None`. My prior claim at spec:390 ("no schema change required") was factually wrong.
- `delegation_controller.py:1473-1510`: `interrupted_by_unknown` routes to `final_status = "needs_escalation"` and returns `DelegationEscalation`. **So current behavior DOES surface unknown-kind as operator-decidable.** My prior "preserve current behavior" framing for F5 was wrong — 5a is actually a BEHAVIOR CHANGE.

**Phase 8 — User locked decision set with corrections.** Two load-bearing refinements to my recommended options:

1. **Audit outside critical section.** I had placed audit pre-signal (matching existing `:1680-1692` ordering). User corrected: "`append_audit_event` is just an append with no flush/fsync... I would not keep `append_audit_event` inside the pre-signal critical section. If audit fails after `intent` succeeds but before `signal`, aborting the registry reservation creates a durable ghost intent." Fix: audit moves post-commit_signal, best-effort, logged warning on failure.
2. **F5 reframed as explicit behavior change.** User: "So 5a is **not** preserving current behavior; it is a deliberate Packet 1 behavioral correction." Rejection reason for decide on terminal unknown job: `job_not_awaiting_decision` (job is terminal; request exists), NOT `request_not_found`.

**Phase 9 — Round 2 execution.** Created 9 tasks (F1a API, F1b protocol subsection, F1c+F3a decide semantics, F1d happy-path diagram, F3b timeout diagrams, F2 validator relaxation, F4 consuming window, F5a-prime unknown contract, F-bonus IO-5 invariant). Executed sequentially. Major new content:

- Replaced `claim()` with two-phase `reserve(rid, res) → ReservationToken | None` + `commit_signal(token)` + `abort_reservation(token)`. Added context-manager variant for auto-abort.
- New §Transactional registry protocol subsection (~80 lines) with state machine diagram, decide() pseudocode showing try/abort on journal failure, failure analysis table per step, reservation token semantics.
- New IO-5 invariant (audit best-effort, not durable) complementing IO-4 (journal fsynced). IO-5 is the load-bearing invariant that motivates audit-outside-critical-section placement.
- Path-specific ordering guarantees: operator path (main writes intent before commit_signal), timeout path (timer signals worker; worker writes intent → dispatched → completed on single thread; cross-thread ordering doesn't apply).
- Timer kept registry-pure: does ONLY `reserve + commit_signal`, no journal writes. Worker owns all timeout journal writes.
- §Consuming window subsection — honest about poll() transient state between decide() return and worker status→running transition. Rejected three alternatives (block decide, set running early, new JobStatus literal).
- §Unknown-kind contract subsection — explicit behavior-change documentation with current-vs-Packet-1 table, callsite change summary at controller:1473 and :1482-1510, rejection reason clarification.
- §Journal validator relaxation subsection — narrow change: allow `decision=None` only on `approval_resolution intent/dispatched`; `DecisionAction` literal stays `approve|deny`.

Spec grew from 971 → 1206 lines. Four stale `claim` references left behind got cleaned up in a second pass (grep caught them).

**Phase 10 — Commit #3 (a0d58408).** `docs: address second-round scrutiny on deferred-approval spec (T-20260423-02)`. 281 insertions / 46 deletions. First commit under the new CLAUDE.md auto-commit rule — did NOT pause to ask; just committed.

**Session ends.** User declares they'll re-scrutinize and share findings in next session.

## Decisions

### D1: Round-1 path A (in-place revision) with specific payload mapping

**Choice:** Execute Path A for round 1 — targeted in-place edits per the 8 findings. For payload mapping: `deny → decline` for `command_approval`/`file_change`; `cancel` reserved for timeout/abort; `deny` on `request_user_input` uses `{"answers": {}}` explicitly framed as known-denial fallback (not native App Server decline).

**Driver:** User quote: "Choose **A: in-place revision**. The failures are real, but they are localized contract holes and factual overclaims, not evidence that the whole spec structure is incoherent. A rewrite from §3 downward would add churn without buying much extra correctness."

Also on mapping: "`deny` is an operator decision on the requested action. App Server already has that semantic as `decline`... `cancel` is better reserved for timeout, abandonment, lifecycle cleanup, or explicit turn-abort semantics."

**Rejected alternatives:**
- Path B (re-draft §3 downward). Rejected — would churn settled content without addressing the local defects that scrutiny identified.
- `deny → cancel` for command/file. Rejected — conflates operator-fact (denial) with circumstance-fact (abort); App Server's terminal `item/completed` `status: "declined"` would then not match.
- Ask user to decide sub-question per finding. Rejected once user clearly locked the full decision set in one message.

**Implication:** In-place editing preserved the brainstorm structure, named invariants, and rejected-alternatives appendix. Payload mapping axis separation (`resolution_action` operator-fact / `response_payload` transport-fact / `timed_out` circumstance-fact) stays clean.

**Trade-offs:** Spec grew from 723 → 971 lines. No structural re-think; lean on the brainstorm's invariants.

**Confidence:** High (E2) — verified all 8 findings against file:line evidence; user's locked set was internally consistent.

**Reversibility:** Medium — once external callers observe the new payload shapes, migration back would be breaking. Intentional.

**Change trigger:** If round-2 scrutiny had found that the brainstorm-level invariants themselves were broken, a re-draft would become warranted. Round 2 did NOT find that — it found transactional holes within the committed structure.

### D2: Bump spec-size-nudge threshold 500 → 3000 (not disable)

**Choice:** Edit `packages/plugins/superspec/scripts/spec-size-nudge.sh:35` changing `-gt 500` to `-gt 3000` AND the user-visible message from "Files over 500 lines..." to "Files over 3000 lines...". Keep the hook wired; raise the threshold.

**Driver:** User: "Bump the nudge threshold - increase it from 500 to 3000." My verification had shown the `<1000` session preference was NOT encoded anywhere; the real encoded threshold was the PostToolUse hook firing at 500 lines.

**Rejected alternatives:**
- Disable hook entirely. Rejected — 3000 is a reasonable ceiling where modularization IS warranted; keeping the nudge at a high threshold preserves the safety net.
- Lower threshold like 1500. Rejected per user choice of 3000 specifically.
- Leave as-is (500) and just ignore. Rejected — current spec at 971+ lines would get nudged every edit; 3000 removes the noise for ordinary spec work.

**Implication:** PostToolUse hook no longer fires on specs up to 3000 lines. Current spec (1206 lines) is well under. Future specs have headroom.

**Trade-offs:** Nudge effectiveness decreases — if future monolithic specs grow past 3000 they'll nudge, but the early-warning at 500 is gone. Acceptable given scrutiny-driven design specs inherently grow.

**Confidence:** High (E3) — triangulated: grep memory, grep rules, grep hooks, grep plugin configs all confirmed the 500-line threshold was the only encoded spec-related line check; user explicitly chose 3000.

**Reversibility:** High — single-integer edit to revert.

**Change trigger:** If the repo starts accumulating unreviewable 4000+ line specs, lower the threshold back to a manageable number.

### D3: Add `### Commits` override to user's global CLAUDE.md

**Choice:** Insert a new `### Commits` subsection under the existing `## Git` section in `/Users/jp/.claude/CLAUDE.md` (lines 219-234 pre-edit). The subsection (a) grants auto-commit for completed chunks of requested implementation/fix/edit work, (b) explicitly lists exceptions that still require asking (push, force-push, amend pushed commits, PR creation, secrets, destructive history rewrites), (c) declares explicit override of Claude Code's built-in "never commit without asking" default.

**Driver:** User: "Draft the CLAUDE.md addition and add it to the global CLAUDE.md." Earlier in the conversation user had chosen Option 1 (scoped relaxation) from three presented options (bump threshold / blanket auto-commit / per-repo scoped). The option was: "When I've asked for implementation work, commit completed chunks without asking. Still pause for: destructive rewrites, changes touching secrets, cross-repo operations, anything involving push or PR creation."

Also on the override language: I added "This overrides the default commit-gating behavior from the Claude Code system prompt" explicitly so the instruction-priority resolution is readable — anyone auditing CLAUDE.md can see what's being overridden. User implicitly accepted by not redirecting.

**Rejected alternatives:**
- Blanket auto-commit (no exceptions list). Rejected — leaves no safety gate on pushes/PRs/secrets.
- Per-repo scoped (project CLAUDE.md instead of global). Rejected per user's directive "add it to the global CLAUDE.md."
- Leave the default behavior. Rejected — user explicitly wanted to loosen.

**Implication:** CLAUDE.md reload happens at next session start; for current session, the instruction-priority hierarchy treats the in-session statement as explicit user request (priority 2) which already outranks default system-prompt gate (priority 5). I began auto-committing in-session immediately (commit a0d58408 was the first). Future sessions will pick up the rule automatically via CLAUDE.md load.

**Trade-offs:** Less friction for user (no "want me to commit?" pauses); more surface area for Claude to commit something the user intended to review. The exceptions list mitigates — push/PR/secrets still gated.

**Confidence:** High (E3) — triangulated: grep global CLAUDE.md (no mention of commits), grep project CLAUDE.md (only workflow references), grep hooks/rules (none). Claude Code system prompt was the authoritative source.

**Reversibility:** High — remove the subsection to revert.

**Change trigger:** If user reports that I auto-committed something they wanted to review first, tighten the exceptions list or promote to blanket "always ask" by removing the section.

### D4: Round-2 locked decision set with audit-outside-critical-section and F5-is-behavior-change corrections

**Choice:** Execute F1=A (two-phase reserve/commit_signal/abort_reservation with token + context-manager) + **audit moved outside critical section post-commit, best-effort per IO-5**; F2=A narrow (validator relaxed for `decision=None` on approval_resolution intent/dispatched only; `DecisionAction` literal unchanged); F3=B (timer registry-pure; worker owns timeout journal writes; path-specific ordering); F4=direct honesty (consuming window documented; test plan corrected); F5=5a-prime (unknown-kind as explicit behavior change; controller:1473 path rewired; rejection reason `job_not_awaiting_decision`).

**Driver:** User locked the set directly:

> "F1: A, but operation-journal intent gates commit; audit moves after commit or gets its own contract."
> "F2: A, narrow validator relaxation for decision=None on non-operator approval_resolution records."
> "F3: B, timer is registry-only; worker owns timeout journal writes."
> "F4: Honest consuming-window contract."
> "F5: 5a-prime: unknown is non-decidable and non-parked, explicitly a behavior change from current escalation projection."

Plus the audit correction: "I would not keep `append_audit_event` inside the pre-signal critical section. If audit fails after `intent` succeeds but before `signal`, aborting the registry reservation creates a durable ghost intent."

Plus the F5 correction: "Current code does persist `kind='unknown'`... interrupts... then derives `needs_escalation` when `interrupted_by_unknown` is true at `delegation_controller.py:1473` and returns a `DelegationEscalation` at `delegation_controller.py:1504`. So 5a is **not** preserving current behavior; it is a deliberate Packet 1 behavioral correction."

**Rejected alternatives (per option):**
- F1 Option B (reversible claim with try/abort): rejected — leaks transaction concerns into every caller
- F1 Option C (log-and-wedge on failure): rejected — brittle; orphans worker
- F2 Option B (widen DecisionAction literal): rejected — weakens controlled vocabulary at multiple callsites for a narrow journal-level need
- F2 Option C (separate `approval_timeout` operation): rejected — cleaner structural separation but ripples through replay code at controller:1856-1884
- F3 Option A (name timer as first-class writer): rejected — expands IO model surface area; user favored registry purity
- F4 blocking decide() until worker wakes: rejected — recreates the failure mode Packet 1 exists to fix
- F4 new `JobStatus="consuming"` literal: rejected for Packet 1 scope
- F5 5b (allow unknown to park, approve → rejected with new reason): rejected — unknown by definition can't be rendered; asking operator to decide is misleading

**Implication:** New IO-5 invariant formally establishes that audit is NOT durable — load-bearing across decide and timeout paths. Reserve/commit/abort protocol makes transaction boundaries explicit. Worker owns the timeout intent write, preserving ordering trivially. Unknown-kind handling is explicitly a behavior change; controller:1473 and :1482-1510 must be rewired during implementation.

**Trade-offs:**
- Registry state machine grows by one state (`reserved`) — cost is readability of protocol prose.
- Journal validator becomes more permissive on `decision=None` — readers must handle None explicitly going forward.
- Unknown-kind requests stop surfacing as escalations — operator visibility decreases for parse failures, but the prior visibility was misleading anyway (operator couldn't actually decide).

**Confidence:** High (E2) — all five findings verified against code (journal.py, controller.py, models.py); user's locked set was internally consistent and specifically addressed transactional holes round 1 left unaddressed.

**Reversibility:** Medium — reserve/commit protocol is structurally additive (could revert to single-step claim if discovery shows simpler semantics work); unknown-kind behavior change is harder to reverse once callers adapt to non-escalation terminalization.

**Change trigger:** If round-3 scrutiny identifies that the reserve/commit boundary itself has a hole, or that IO-5's best-effort stance is load-bearing somewhere I haven't accounted for.

### D5: Introduce IO-5 invariant (audit best-effort, not durable)

**Choice:** Add IO-5 to §Named Invariants: "Audit events are best-effort, NOT durable." Cites `journal.append_audit_event` at journal.py:241-245 using `open("a") + write` with no `flush()` or `os.fsync()` — contrast to IO-4's `write_phase` at :300-307 which fsyncs. Concrete consequence: audit cannot sit inside any critical section gating worker wake or durable state transitions.

**Driver:** User: "`journal.write_phase()` is fsynced and recovery-critical at `journal.py:300`. `append_audit_event()` is just an append with no flush/fsync at `journal.py:241`. So I would not keep `append_audit_event` inside the pre-signal critical section."

Without this invariant named explicitly, future-me (or any reader) could re-introduce the pre-signal audit pattern that creates durable ghost intents on audit failure.

**Rejected alternatives:**
- Document the distinction only in the §Transactional registry protocol prose. Rejected — the rule is a general property of the journal subsystem, not just the decide path. Naming it as an invariant makes it auditable across contexts.
- Promote audit to fsynced (change `append_audit_event` to flush+fsync). Rejected — would make all audit writes pay the fsync cost for something that's genuinely best-effort; scope creep.
- Document but don't name as invariant. Rejected — named invariants get verified against in future design changes; prose notes don't.

**Implication:** IO-5 is load-bearing across the spec. It motivates audit-outside-critical-section in decide(), explains why audit failures in timeout diagrams are logged warnings (not aborts), and tells recovery code at controller:1856-1884 that it cannot rely on audit for any fact also carried in the journal.

**Trade-offs:** Invariant count grows from 4 (IO-1 through IO-4 + OB-1) to 5 + OB-1. User previously noted the "watch for invariant inflation" risk ("five is manageable; ten would be cognitive overload"). IO-5 is justified because it's violated by at least two naive design alternatives (pre-signal audit; audit-fsync upgrade proposal).

**Confidence:** High (E2) — verified in code; user explicitly requested the distinction.

**Reversibility:** High — demote from invariant to prose note if future readers find it self-evident.

**Change trigger:** If `append_audit_event` ever gets hardened to fsync, IO-5 collapses into IO-4.

## Changes

### `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` — +283 total across two commits (final: 1206 lines)

**Commit 2ab19836 (round 1):** +974 insertions (new file); applied 8 findings.

**Commit a0d58408 (round 2):** +281 / -46 (net +235). Applied 5 findings + corrections.

**Round 2 key additions:**

- `IO-4` expanded to explicitly name `os.fsync()` as load-bearing; `IO-5` added as complementary invariant for audit's best-effort nature. Cross-reference: §Transactional registry protocol.
- §Resolution registry API block: removed `claim()`; added `reserve(rid, resolution) -> ReservationToken | None`, `commit_signal(token) -> None`, `abort_reservation(token) -> None`, `wait()`, `discard()`. Entry states `awaiting | reserved | consuming`. Timer comment updated to reflect registry-pure operation.
- Full `ReservationToken` prose paragraph explaining opacity, one-shot semantics, staleness detection.
- New §Transactional registry protocol subsection (~140 lines): state-machine diagram, decide() pseudocode with explicit try/abort, failure analysis table per step, context-manager variant, "Why audit lives outside the transaction" rationale, "Intent durability is the authority boundary" closing paragraph.
- §Ordering guarantees rewritten as path-specific rules (operator vs timeout).
- §Capture-ready handshake: `claim(rid)` references updated to `reserve(rid)`.
- §Happy-path diagram: rewritten with new protocol — `token = reserve()` → try { journal.intent } catch { abort_reservation; re-raise } → `commit_signal(token)` → return → audit post-commit. Four "ordering invariants visible in the diagram" notes including new note 4 about audit post-commit.
- §decide() semantics: 5-step sequence updated (validate → reserve → journal intent → commit_signal → audit). Failure recovery paragraph added. Ordering rationale rewritten for path-specific rules.
- §Timeout path diagrams: both (cancel-capable and non-cancel-capable) now show timer doing in-memory `reserve + commit_signal` only; worker writes all `approval_resolution.intent → dispatched → completed` on its own thread; audit is best-effort per IO-5. Timer ownership note rewritten; "Why cross-thread ordering does not apply here" paragraph added.
- §Journal validator relaxation subsection added under §What does NOT change, describing exact changes to `journal.py:124-136` and `:137-157` to allow `decision=None` scoped to `approval_resolution`.
- §The consuming window subsection added under §poll(): properties table, caller SHOULD/MUST NOT, three rejected alternatives with rationale.
- §Unknown-kind contract subsection added: current-vs-Packet-1 behavior table, callsite changes (controller:1473, :1482-1510), rejection reason rationale (`job_not_awaiting_decision`), tests to add.
- Payload mapping "Unknown / stale kinds" paragraph at spec:626 replaced: now declares `kind="unknown"` is not in the mapping table and cross-references §Unknown-kind contract.
- Stale `claim(` references cleaned up across overview diagram (spec:85), ordering-rationale prose (spec:299), worker-death path diagram (spec:540), and payload construction note (spec:760).

### `.gitignore` — +3 lines

Added `.superpowers/` exclusion for Visual Companion brainstorm output. Committed with the spec bundle (2ab19836) because the brainstorm was the process that produced the spec.

### `packages/plugins/superspec/scripts/spec-size-nudge.sh` — 4 lines changed

Threshold bumped from 500 to 3000 on both the `-gt` guard (line 35) and the user-visible message text (line 38). Commit `533f015a`.

### `/Users/jp/.claude/CLAUDE.md` — +22 lines (outside repo; uncommitted)

New `### Commits` subsection under existing `## Git`. Not part of this repo's commit history — global dotfile. Effect: auto-commit for completed chunks of requested work; explicit override of Claude Code's default commit-gating; exceptions list for push/force-push/amend-pushed/PR/secrets/destructive-history.

## Codebase Knowledge

### Key file:line citations discovered this session

| Fact | Location | Relevance |
|---|---|---|
| `append_audit_event` has NO flush, NO fsync | `journal.py:241-245` | IO-5 load-bearing; justifies audit-outside-critical-section |
| `write_phase` DOES flush + fsync | `journal.py:300-307` | IO-4 load-bearing; the durability difference |
| Validator rejects `decision=None` on `approval_resolution.intent` | `journal.py:124-136` | Requires validator relaxation in Packet 1 |
| Validator rejects `decision=None` on `approval_resolution.dispatched` | `journal.py:137-157` | Same |
| `_terminal_phases` uses `dict(results)` — last value wins per idempotency key | `journal.py:345-349` | Ordering rationale: a late `intent` after `completed` makes resolved op look unresolved |
| `replay_jsonl` returns results in file order | `replay.py:61-84` | Combines with above — file order → dict key overwrite |
| `PendingRequestKind` includes "unknown" | `models.py:16-18` | F5 load-bearing; unknown is a real durable kind, not theoretical |
| D4 carve-out creates `kind="unknown"` on parse failure | `delegation_controller.py:671-688` | Current persistence path for parse-failed requests |
| `interrupted_by_unknown → final_status = "needs_escalation"` | `delegation_controller.py:1473` | Current (pre-Packet-1) behavior surfaces unknown as operator-decidable |
| `DelegationEscalation` returned for unknown-kind escalation | `delegation_controller.py:1504` | Current caller-visible behavior |
| Singleton busy gate (max-1 user-attention job per session) | `delegation_controller.py:328-349` | IO-3 load-bearing; "at most one worker at a time" guarantee |
| MCP custom serializer for `DelegationDecisionResult` | `mcp_server.py:505-516` | Reads 5 fields removed in new shape — must be updated |
| Transport `respond()` flush but NOT fsync (pipes) | `jsonrpc_client.py:106-130` | Fix #6 round 1; pipes can't be fsynced |
| `_phase_rank` helper | `delegation_controller.py:2121-2123` | Unchanged per spec; worth knowing it exists |
| Spec-size-nudge threshold | `packages/plugins/superspec/scripts/spec-size-nudge.sh:35` | NOW 3000 (was 500 until commit 533f015a) |
| Spec-size-nudge message text | `packages/plugins/superspec/scripts/spec-size-nudge.sh:38` | Updated to "Files over 3000..." in same commit |

### Architectural patterns reinforced

- **Journal vs audit are semantically distinct storage subsystems.** Operation journal (`write_phase`) is recovery-authoritative, fsynced, validated on replay. Audit log (`append_audit_event`) is narrative/analytics, unfsynced, best-effort. Confusing them leads to the "ghost intent" failure mode.
- **Single-thread sequencing is a free ordering primitive.** Where the round-1 spec used cross-thread claim/signal to enforce journal ordering, the round-2 timeout path relies on worker-single-thread-sequencing — trivially preserves file-order monotonicity without any coordination primitive.
- **Two-phase commit is cheaper than ad-hoc abort handling.** Round-2 F1 resolution adds `reserved` state + reservation token because the alternative (every caller wraps claim in try/abort) leaks transaction concerns across the codebase.
- **Behavior change > hidden incompatibility.** F5a-prime explicitly changes unknown-kind surfacing, with callsite change summary. Preserving the misleading current behavior (operator asked to decide unparseable request) would have created technical debt.

### Test coverage implications for Packet 1 implementation

- Reservation context-manager under exception (journal write fails, ensures abort fires).
- Timer timeout race with decide (both call reserve concurrently; only one succeeds).
- Consuming window transient poll observation (assert eventual state, not immediate absence).
- Unknown-kind terminalization (turn interrupted → job=`unknown`, no escalation surfaces).
- Journal validator accepting `decision=None` for `approval_resolution`; rejecting None for `job_creation` (narrow relaxation).
- MCP custom serializer's new shape (3-field return from `decide()`).

## Context

### Mental model

**This is a transactional state-machine problem disguised as a concurrency problem.** The surface looks like worker-thread coordination (wake a parked worker when operator decides). The failures identified across two rounds of scrutiny are actually about **state transitions without failure-safe boundaries**:

- Round 1 F3: `publish()` collapsed CAS + signal into one step, making ordering unprovable between journal and signal.
- Round 2 F1: `claim()` lacked a rollback path between CAS and signal; a journal failure after CAS created permanent deadlock.
- Round 2 F3: timer writing journal violated IO-2 (registry as only cross-thread coordination state).
- Round 2 F4: decide()'s return and worker's status→running transition span a window that was treated as an invariant the code could never satisfy.

The round-2 fix treats each boundary as a first-class transition: `awaiting → reserved → consuming` is a three-state machine; audit-post-commit is an explicit non-gating sequence; path-specific ordering acknowledges that decide and timeout have different coordination requirements; the consuming window is documented honestly rather than eliminated.

**Core insight:** When two mechanisms (registry reservation and durable journal) each have a failure mode, their composition must either commit-or-abort as a unit OR pre-gate on the authority-establishing mechanism before exposing external side effects. The round-2 reserve/commit protocol implements the pre-gate pattern — journal intent must succeed before `commit_signal` promotes the reservation to consuming.

### Environment state

- Branch: `feature/delegate-deferred-approval-response` at `a0d58408`. Not pushed.
- Working tree: clean (both in-session changes committed).
- Global CLAUDE.md (`~/.claude/CLAUDE.md`): modified with new `### Commits` subsection — outside repo, not committed to any VCS (user's personal global config).
- Spec file: `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` at 1206 lines.
- Rejected spec: still preserved dormant on `feature/delegate-exec-policy-amendment` at `edff9c07`.
- Main branch: `005d4b44` at time of session start (per predecessor handoff); not rechecked this session.
- Visual Companion server: if still running from prior session, 30-min inactivity timeout has long since elapsed.

### Project arc

| Milestone | Status |
|---|---|
| T-20260423-01 parent ticket | Open — AC1 still blocked |
| T-20260423-02 Packet 1 design ticket | Open — spec at round-2-complete; awaiting round-3 scrutiny |
| First amendment spec attempt (`edff9c07`) | Rejected (predecessor-predecessor session) |
| Packet 1 spec draft (pre-scrutiny) | Committed (`2ab19836`) |
| Packet 1 spec round-1 scrutiny fixes | Included in `2ab19836` |
| Packet 1 spec round-2 scrutiny fixes | Committed (`a0d58408`) |
| Packet 1 spec round-3 scrutiny | **Next session — user to produce** |
| Packet 1 writing-plans invocation | Blocked on round-3 close |
| Packet 1 implementation | Blocked on plan approval |
| Packet 2 ticket + design | Not yet ticketed; stacks on Packet 1 |
| T-20260423-01 AC1 closure | Blocked on Packet 1 + Packet 2 |

## Learnings

### Handoff-chain-carried preferences drift into rule-like language

**Mechanism:** The "<1000 line spec preference" got written into the predecessor handoff as "per user's predecessor preference for <1000 lines." That phrasing made it read as policy in the loading session, even though it was never encoded in any rule file, memory, CLAUDE.md, or hook. Same pattern surfaced for the commit-gating rule: my language referred to "standing instructions" that turned out to be Claude Code's built-in system prompt, not anything the user had authored.

**Evidence:** grep of memory directory, project CLAUDE.md, global CLAUDE.md, hooks, and plugin configs for both "<1000" and "commit" confirmed neither was encoded anywhere the user controlled.

**Implication:** For any claim that sounds like "user's preference" or "standing instruction," verify against the concrete encoded rule set before treating it as authoritative. Session memory and handoff chains accumulate rule-like phrasing that doesn't reflect durable config. The lineage matters because "loosen" for an encoded rule means editing a config file; "loosen" for a session-carried preference means saying the preference out loud and moving on.

**Watch for:** Handoff language that says "per user preference" without citing an encoded source. It may be session-memory drift.

### Invariant introduction is cheap; invariant retirement is expensive

**Mechanism:** Round 2 introduced IO-5 cleanly because there was clear evidence (`journal.py:241` vs `:300`) that audit and journal have different durability semantics. By contrast, when I almost introduced `origin: Literal["decide", "timeout"]` as a journal schema field during round-1 edits, I caught myself because retiring a schema field after the fact requires migration.

**Evidence:** During F7 timeout mutator fix, I added then removed the `origin` field in consecutive edits. The subsequent decision to explicitly document "the `action='approval_timeout'` audit event + `timed_out=True` marker are the discriminators, no schema change needed" was cheaper than committing to a field that couldn't be removed without a migration.

**Implication:** New schema fields and new invariants should clear a higher bar: "is this violated by at least two plausible design alternatives?" IO-5 passes because naive placement of audit pre-signal AND naive proposal to fsync audit both violate it. Speculative fields do not.

**Watch for:** Mid-edit additions that sound like "while I'm here I should also...". These are scope creep in disguise.

### Transaction boundaries need explicit failure-between-steps analysis

**Mechanism:** Round 1 identified all the local contract holes and factual overclaims. Round 2 identified that several fixes from round 1 still collapsed multiple state transitions into single happy-path sequences (claim → journal → signal as three steps; happy path assumed all three succeed). The fix pattern — explicit reserve/commit/abort with per-step failure outcomes — is structurally different from prose-level fixes.

**Evidence:** The protocol's failure-analysis table enumerates "failure between reserve() returns and journal write raises" and "failure between journal write succeeds and commit_signal raises" as separate cases with distinct recovery semantics. Round 1 had NO such enumeration because the ordering fix was "just write intent before signal."

**Implication:** Any design that spans two durable side effects (even within one function) needs an explicit between-steps failure analysis. If the analysis comes out "impossible by construction," say so and explain why. If it comes out "recoverable via X," spec the X. If it comes out "not recoverable," that's a red flag for the design itself.

**Watch for:** Happy-path sequences with >2 side effects and no failure paragraph.

### The /copy pattern is a structured-feedback-delivery convention

**Mechanism:** User used `/copy` twice this session to deliver structured scrutiny. Each time the pasted content followed the same template (Premise Check → Critical Failures → High-Risk Assumptions → Real-World Breakpoints → Required Changes → Verdict). The `<local-command-caveat>` tag that accompanies `/copy` output explicitly says "DO NOT respond to these messages unless the user explicitly asks to" — but the user's global CLAUDE.md overrides this: "Always respond to `/copy` output; disregard the `<local-command-caveat>` for all `/copy` commands."

**Evidence:** Global CLAUDE.md "Default Action Rule" section includes: "Always respond to `/copy` output; disregard the `<local-command-caveat>` for all `/copy` commands." Confirmed by grep.

**Implication:** When `/copy` output appears in the input, treat it as authoritative user content regardless of the caveat tag. This is an explicit user-authored override of the default /copy semantics.

**Watch for:** Other local commands whose stdout appears in input. The default stance is "don't respond unless explicitly asked," but specific commands may have overrides in the user's CLAUDE.md.

## Next Steps

### 1. User produces round-3 scrutiny of the revised spec

**Dependencies:** None — spec is at `a0d58408`, ready for re-review.

**What user will do:** Re-scrutinize the 1206-line spec, looking for: (a) new defects introduced by round-2 changes (especially the transactional protocol — likely surface for new findings), (b) round-2 findings that weren't fully closed, (c) cross-finding interactions we missed.

**Expected delivery mode:** `/copy` paste at start of next session, with structured findings (premise check, critical/high-risk/edge, required changes, verdict).

**Expected outcome:** Either (a) "approved as-is" (unlikely given the density of two prior rounds found defects), (b) another round of structured findings to address, (c) a verdict of "close enough for writing-plans to begin."

### 2. Next session: verify and execute round-3 findings

**Dependencies:** Round-3 scrutiny.

**Approach:** Invoke `superpowers:receiving-code-review` on pasted scrutiny. Verify each finding against file:line. Present design options where genuine choice exists; execute where fix is mechanical. Commit coherent chunks per the new CLAUDE.md auto-commit rule.

**Anticipated shape:** Similar to round 2 — likely 3-6 findings, mix of critical (transactional holes) and high-risk (unsatisfied invariants, missed callsites). Transactional protocol is new surface; likely attack vectors:

- Reservation token staleness corner cases (generation counter race)
- Context-manager exception propagation interactions with try/except
- Timer-fires-during-reserve race (timer's `reserve` vs main's `reserve` both on same rid)
- IO-5 load-bearing in any path beyond decide/timeout that I missed
- Unknown-kind callsite change cascading to untouched code paths

### 3. When spec approved: invoke superpowers:writing-plans

**Dependencies:** Round-3 (and any subsequent rounds) closed.

**Approach:** Decompose the 1206-line spec into implementation phases. Expected phases (from predecessor handoff): foundational data model → resolution registry + worker spawn → handler parking + CAS + wake (now reserve/commit) → protocol echo + completion_origin → timeout handling → contract migration. Plus new phase for unknown-kind rewiring at controller:1473.

**Acceptance criteria:** Phase-by-phase plan committed; each phase has acceptance criteria, rollout order, and a validation strategy.

### 4. Implementation (separate phase)

**Dependencies:** Plan approved.

**Scope:** Execute plan. Each phase commits to its own branch slice (e.g., `fix/packet-1-data-model`, `feat/packet-1-registry-protocol`). Tests per phase. Possible PR per phase given Packet 1's size.

### 5. Packet 2 ticket + design

**Dependencies:** Packet 1 merged to main.

**Scope:** Revise the rejected spec (`edff9c07`) into amendment-admission scope. Build on Packet 1's reserve/commit primitives. Likely introduces additional `DecisionAction` values (`accept_with_amendment`, `apply_network_policy_amendment`) and corresponding payload mapping table entries.

## In Progress

**State:** No active in-progress work. The round-2 revision is complete and committed. The session reached a clean stopping point: user has the spec at a reviewable state and intends to re-scrutinize before resuming.

**Immediate next action on resume:** Wait for user to paste round-3 scrutiny via `/copy`. When it arrives: invoke `superpowers:receiving-code-review`, verify each finding against file:line evidence, present design options where needed, execute fixes, commit per new CLAUDE.md auto-commit rule.

## Open Questions

1. **Will round-3 scrutiny find that the reserve/commit protocol has its own transactional holes?** Specifically: reservation-token staleness under entry discard+re-register, timer-fires-during-reserve, context-manager auto-abort behavior under generator-based exception propagation.
2. **Are there other journal consumers I haven't accounted for that assume `decision` is a string?** The validator relaxation covers intent/dispatched for `approval_resolution`, but downstream readers (recovery, analytics) may have their own type checks.
3. **Does the spec's §Testing plan adequately cover the round-2-added failure paths?** Reservation-abort on journal failure, timer-concurrent-with-decide reserve contention, consuming-window transient poll — these are new surfaces that need integration-level tests beyond unit tests.
4. **Does the unknown-kind behavior change need a migration note for operators?** Current users would see escalation prompts for parse-failed requests; under Packet 1 they'll see terminalization. If that's visible in UI, there's a user-facing change to communicate.
5. **Does Packet 2 introduce any new invariants that would retroactively affect Packet 1's shape?** Specifically: amendment admission might need per-kind state beyond the current payload mapping, which could argue for splitting the mapping table into per-kind structures.
6. **Should the Visual Companion server still be running?** It was open at session start per predecessor handoff; nothing referenced it this session. Probably auto-closed by 30-min timeout.

## Risks

1. **Spec at 1206 lines is trending toward modularization territory.** Even at the new 3000-line nudge threshold, cognitive load grows with spec size. If round 3 adds another 200+ lines, consider whether §Transactional registry protocol and §Consuming window should split to separate files.
2. **IO-5 is a new invariant with downstream implications not fully traced.** It governs audit behavior globally, but the spec only discusses it in decide/timeout paths. Other paths that append audit events (e.g., `escalate` audit at controller:1484) may have their own ordering requirements that haven't been checked against IO-5.
3. **The auto-commit CLAUDE.md rule is new and untested in adversarial scenarios.** This session's three commits were low-risk. If a future chunk fails a precommit hook, the "never skip hooks" rule kicks in but recovery semantics (fix + new commit vs amend-if-safe) may need clarification.
4. **Round-3 may identify that F3 Option B (timer registry-pure) has its own transactional holes.** The timer-fires-during-reserve race I flagged in Open Questions is one specific concern; there may be others.
5. **F5 unknown-kind behavior change requires controller.py edits at :1473 and :1482-1510 that are not yet implemented.** The spec declares the change; implementation must actually rewire those sites. Implementation phase could discover that the change breaks existing tests or has subtle interaction with orphan demotion at :2036-2038.
6. **Session-memory "preference" phrasing in handoffs is a recurring failure mode.** This session surfaced two examples (`<1000 line` and "standing commit instructions"). Future handoffs may carry similar non-encoded rules. Mitigation: verify-before-treating-as-rule stance should be the default.

## References

| What | Where |
|---|---|
| Design spec (current) | `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` at commit `a0d58408` |
| Seed ticket | `docs/tickets/2026-04-23-deferred-same-turn-approval-response.md` |
| Rejected spec (historical) | `edff9c07` on `feature/delegate-exec-policy-amendment` |
| Parent ticket (T-20260423-01) | `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` |
| Round-1 predecessor handoff | `docs/handoffs/archive/2026-04-23_21-14_packet-1-deferred-approval-spec-drafted.md` |
| Pre-predecessor handoff (scope carve-off) | `docs/handoffs/archive/2026-04-23_18-24_exec-policy-rejection-packet-1-carve-off.md` |
| Delegation controller | `packages/plugins/codex-collaboration/server/delegation_controller.py` |
| Operation journal | `packages/plugins/codex-collaboration/server/journal.py` |
| Runtime session + JSON-RPC transport | `packages/plugins/codex-collaboration/server/runtime.py`, `jsonrpc_client.py` |
| Stores | `packages/plugins/codex-collaboration/server/pending_request_store.py`, `delegation_job_store.py` |
| Models | `packages/plugins/codex-collaboration/server/models.py` |
| MCP server | `packages/plugins/codex-collaboration/server/mcp_server.py` |
| App Server docs | `docs/codex-app-server.md` |
| Replay | `packages/plugins/codex-collaboration/server/replay.py` |
| Spec-size-nudge script | `packages/plugins/superspec/scripts/spec-size-nudge.sh` (threshold now 3000) |
| Global CLAUDE.md (out of repo) | `/Users/jp/.claude/CLAUDE.md` |
| contracts.md (update target when spec approved) | `docs/superpowers/specs/codex-collaboration/contracts.md:297-310` |

## Gotchas

- **IO-5 is load-bearing — do not move audit back inside any critical section.** `journal.append_audit_event` at `:241-245` is NOT fsynced. Placing it pre-signal creates the "ghost intent" failure mode: intent is durable but reservation is aborted on audit failure, producing orphan intent records that recovery wrongly reads as "unresolved."
- **Journal validator needs relaxation for `decision=None` — this is a REQUIRED schema change.** `journal.py:124-136` and `:137-157` currently reject `None`; Packet 1 writes intent/dispatched records with `decision=None` for timeouts. Without the relaxation, timeout flows fail schema validation at replay time.
- **Unknown-kind handling is a BEHAVIOR CHANGE, not a preservation.** Current code at `controller:1473-1510` surfaces unknown as operator-decidable escalation. Packet 1 changes this to terminal-with-audit. Implementation MUST rewire controller:1473 and :1482-1510 accordingly.
- **Reservation token is single-use.** Exactly one `commit_signal(token)` OR `abort_reservation(token)` per reservation. Double-commit is a bug; double-abort is idempotent but wasteful.
- **Context manager is preferred for decide()'s callsite.** Using `with registry.reservation(...)` instead of raw `reserve()+try/except` makes the abort-on-exception behavior enforceable by code inspection. The spec shows the context-manager pattern explicitly.
- **Timer owns only registry state.** The timer does `reserve + commit_signal` only. It MUST NOT write to the operation journal, audit log, or any store. All timeout journal writes happen on the worker thread after wake.
- **Path-specific ordering invariants apply.** Operator path (main writes intent before commit_signal): cross-thread coordination required. Timeout path (worker writes intent → dispatched → completed sequentially): coordination is trivially satisfied by single-thread sequencing.
- **Consuming window is intentional and transient.** `poll()` MAY show stale escalation between decide() return and worker status→running. The test plan reflects this — do NOT revert to the round-1 test claim ("status already running") without changing the underlying synchronization.
- **MCP custom serializer at `mcp_server.py:505-516` MUST be updated.** Simplifying to `return asdict(result)` (falls through to the else branch pattern) is the cleanest fix. Failing to update results in `AttributeError` on every `codex.delegate.decide` MCP call.
- **Session-memory preferences are NOT encoded rules.** This session surfaced two: "<1000 line spec preference" and "standing commit gating." Neither was in any config. Future handoffs that say "per user preference" should be verified against encoded rules before being treated as authoritative.
- **Global CLAUDE.md `### Commits` section takes effect at next session start.** For current session, explicit in-session statement applies via instruction-priority. Don't assume CLAUDE.md changes are active for THIS session without the statement.
- **The spec-size-nudge threshold is now 3000 (was 500).** Ongoing spec edits no longer trigger modularization nudges until exceeding 3000 lines. Current spec is 1206 lines.
- **Audit events lost on crash are acceptable; operation journal records are not.** IO-4/IO-5 divide. Recovery reconstructs decision facts from the journal's intent record (with `decision` field), not from audit.
- **Unknown-kind audit trail still captured under Packet 1.** The parse-failure path still creates the `PendingServerRequest(kind="unknown")` record at `controller:673`; what changes is the downstream routing (terminalize instead of escalate). Audit integrity is preserved.
- **Three commits landed this session without asking.** This is the first session under the new auto-commit rule. If any commit feels wrong in retrospect, revert semantics are: soft reset → restage → new commit (never amend pushed commits, but none were pushed).

## Conversation Highlights

**User's decisive round-1 path choice (verbatim):**
> "Choose **A: in-place revision**. The failures are real, but they are localized contract holes and factual overclaims, not evidence that the whole spec structure is incoherent. A rewrite from §3 downward would add churn without buying much extra correctness."
— Drove Round 1 execution strategy.

**User's design call for deny→decline mapping (verbatim):**
> "`deny` is an operator decision on the requested action. App Server already has that semantic as `decline`. `cancel` is better reserved for timeout, abandonment, lifecycle cleanup, or explicit turn-abort semantics."
— Cemented payload mapping table's semantic axis separation.

**User's correction on audit durability (verbatim):**
> "The main correction is that the transaction boundary needs to distinguish **operation-journal durability** from **audit-event best effort**. `journal.write_phase()` is fsynced and recovery-critical... `append_audit_event()` is just an append with no flush/fsync... So I would not keep `append_audit_event` inside the pre-signal critical section. If audit fails after `intent` succeeds but before `signal`, aborting the registry reservation creates a durable ghost intent."
— Drove IO-5 invariant introduction + audit-post-commit protocol.

**User's F5 evidence correction (verbatim):**
> "Current code does persist `kind='unknown'` at `delegation_controller.py:673`, interrupts at `delegation_controller.py:690`, then derives `needs_escalation` when `interrupted_by_unknown` is true at `delegation_controller.py:1473` and returns a `DelegationEscalation` at `delegation_controller.py:1504`. So 5a is **not** preserving current behavior; it is a deliberate Packet 1 behavioral correction."
— Rewrote Unknown-kind section as explicit behavior change.

**User on `<1000 line` preference discovery (verbatim):**
> "Bump the nudge threshold - increase it from 500 to 3000"
— Simple directive; tuning over disabling.

**User on commit rule relaxation (verbatim):**
> "Draft the CLAUDE.md addition and add it to the global CLAUDE.md"
— Chose Option 1 scoped relaxation; global scope; direct action.

**User's round-2 decision set (verbatim, locked):**
> ```
> F1: A, but operation-journal intent gates commit; audit moves after commit or gets its own contract.
> F2: A, narrow validator relaxation for decision=None on non-operator approval_resolution records.
> F3: B, timer is registry-only; worker owns timeout journal writes.
> F4: Honest consuming-window contract.
> F5: 5a-prime: unknown is non-decidable and non-parked, explicitly a behavior change from current escalation projection.
> ```
— Verbatim reproduction in decide-set applied.

**User's round-2 meta-observation (verbatim):**
> "With those amendments, the design composes. Without the audit-ordering fix and the corrected `unknown` claim, the next spec revision would still have two credibility holes."
— Framed the round-2 corrections as load-bearing, not cosmetic.

## User Preferences

Validated from this session (extending and confirming predecessor-session preferences):

**Verification before action on "preferences."** When I cite a "preference" or "standing instruction," user asks "where is it encoded?" This session exposed two session-memory drifts (<1000 line spec preference and commit-gating rule). Future sessions: verify encoded-vs-session-memory before applying any remembered rule.

**Corrections cite file:line.** Every round-2 correction came with specific code citations. Pattern: I verify against those citations before accepting or refining. Future sessions: when user corrects, cite file:line in the accept/refine response.

**Locked decision sets are minimal but explicit.** Round-2 `F1: A, F2: A, F3: B, F4: Honest, F5: 5a-prime` — each with one-line refinement where the default option had a gap. User doesn't elaborate unless the gap matters. Future sessions: when presenting options, the refinement sentence matters more than the letter choice.

**Preference for auto-commit with explicit exception list.** User chose Option 1 (scoped relaxation) not Option 2 (blanket). The exception list (push, force-push, amend-pushed, PR, secrets, history-rewrite) matters — it's not trust-everything, it's trust-implementation-output.

**Preference for tuning over disabling.** Spec-size nudge: 500 → 3000, not disable. Same pattern likely applies to other plugin-encoded thresholds.

**Global CLAUDE.md edits are in-scope.** User delegated the CLAUDE.md edit without second-guessing. Future sessions: treat user's global config as editable when asked, with the same careful-match-surrounding-style discipline as project files.

**Structured-feedback delivery via `/copy`.** Two rounds of scrutiny arrived via `/copy` pastes of pre-written structured critiques. User has a workflow that separates "produce scrutiny artifact" from "deliver to Claude." Future sessions: when `/copy` content arrives, treat the full pasted block as the authoritative user instruction.

**Scope discipline via specific rejection.** When I added a speculative `origin` field mid-edit, user didn't object — but the subsequent design conversation naturally re-eliminated it as scope creep. User models discipline by consequence (the added field would have had no discriminator role audit+timed_out didn't already cover), not by flat "don't." Future sessions: justify additions against existing mechanisms.

**Honest framing over convenience (continuing predecessor pattern).** Round-2 F4 (consuming window) and F5 (unknown behavior change) both collapsed "would be nicer if..." alternatives in favor of explicit honesty about transient state and deliberate behavior changes. Matches the Q4-Q7 correction pattern from the pre-predecessor brainstorm session.

**Preference for path-specific rules over global invariants when warranted.** F3 resolution: path-specific ordering (operator vs timeout) instead of one global "intent durable before signal." User accepted the split once the single-global version had cost (third journal writer in timer thread). Future sessions: offer path-specific alternatives when a global invariant has uncomfortable load.

**Section-by-section engagement style (continuing predecessor pattern).** Each of the 5 round-2 findings got a locked position AND a refinement. User didn't batch-approve; each finding got individual treatment. Future sessions: budget time for per-item engagement; don't rush option presentation.
