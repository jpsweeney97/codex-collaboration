---
date: 2026-04-21
time: "21:44"
created_at: "2026-04-22T01:44:06Z"
session_id: aa4b5c44-8521-44b5-8916-f3840782dc0b
resumed_from: "docs/handoffs/archive/2026-04-21_14-56_t06-pr-review-merge-and-ticket-closure.md"
project: claude-code-tool-dev
branch: main
commit: 57d89874
title: "T-07 scope reconciliation complete"
type: handoff
files:
  - docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md
  - docs/superpowers/specs/codex-collaboration/decisions.md
  - docs/superpowers/specs/codex-collaboration/delivery.md
  - docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md
  - packages/plugins/codex-collaboration/server/journal.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/control_plane.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/dialogue.py
---

# T-07 Scope Reconciliation Complete

## Goal

Reconcile T-07 (analytics, reviewer, and cross-model cutover) scope against
the actual evidence from closed predecessors T-04 and T-06, make design
decisions for the analytics and review replacement surfaces, adjudicate the
context-injection removal gate, and close stale T-05 ticket metadata.

**Trigger:** Prior session closed T-06 and prescribed "T-07 design
reconciliation, not coding. First step should be a scope reconciliation pass
over the closed T-04/T-06 evidence and the T-07 ACs, especially the conditional
context-injection removal rule."

**Stakes:** T-07 is the final cutover packet. Its original ACs assumed
outcomes from T-04 and T-06 that resolved differently than expected — T-04
closed as "demonstrated-not-scored" rather than a formal aggregate benchmark
pass, and the cross-model reviewer was an agent compensating for the older
plugin shape rather than a natural architecture component for codex-collaboration.
Without reconciliation, the next implementor would work from stale assumptions.

**Success criteria (all met):**
1. Every T-07 AC mapped against predecessor evidence.
2. Analytics and review replacement architecture decided with code verification.
3. Context-injection removal adjudicated with honest evidence labeling.
4. T-05 retroactively closed with verifiable AC evidence.
5. All changes recorded in three layers (ticket, decisions.md, delivery.md).
6. PR opened and merged.

**Connection to project arc:** Sixth session in the codex-collaboration build
sequence. T-06 delivered the last implementation work. T-07 reconciliation
bridges from "all code is built" to "the cutover plan is specified." Next:
slice 7a implementation.

## Session Narrative

**Phase 0 — Handoff load (~2 min).** Loaded the T-06 handoff
(`2026-04-21_14-56`). Clean state: main at `541bb45f`, 845 tests, T-06 closed,
prescribed next step was T-07 design reconciliation.

**Phase 1 — Evidence gathering (~10 min).** Read all authority documents in
parallel: T-07 ticket, T-04 ticket (dialogue parity/benchmark), T-06 ticket
(promotion/delegate), T-05 ticket (execution domain), T-02 ticket (plugin
shell), T-03 ticket (safety substrate), delivery.md, dialogue-supersession-
benchmark.md, cross-model capability analysis, and the decisions.md spec. Also
inventoried cross-model vs codex-collaboration skills and agents to build the
parity matrix.

Key discovery: T-05 still showed `status: open` despite T-06 being closed and
depending on T-05's work. This was a ticket hygiene issue, not an engineering
gap — the execution domain was fully consumed.

**Phase 2 — Initial reconciliation draft (~5 min).** Produced an AC-by-AC
mapping: AC-1 (analytics) and AC-2 (reviewer) needed net-new work; AC-3
(migration docs) and AC-4 (parity matrix) needed net-new docs with clear
inputs; AC-5 (cross-model removal) depended on AC-1 through AC-4; AC-6
(context-injection) required adjudication given T-04's non-standard resolution.
Proposed five slice boundaries and identified the context-injection wording gap.

**Phase 3 — Analytics design discussion (~20 min).** User proposed treating both
replacements as new codex-collaboration surfaces with cross-model as semantic
source only, not as ports. Extended collaborative discussion covering:

1. Analytics source: user recommended reading the server-owned observability
   projection (`analytics/outcomes.jsonl` + `audit/events.jsonl`), not raw
   recovery stores or a new cross-model-style flat emitter. User cited the
   two-log split in `recovery-and-journal.md:12` and the existing `OutcomeRecord`
   at `models.py:202`.

2. Outcome shape: user proposed keeping `OutcomeRecord` as advisory-only and
   adding a separate `DelegationOutcomeRecord` for terminal execution outcomes.
   Rationale: advisory outcomes require `turn_id`; delegation outcomes require
   `job_id`; a single optional-field record would make invalid combinations easy
   to write.

3. I verified the code: `OutcomeRecord.outcome_type` is
   `Literal["consult", "dialogue_turn"]` — no delegation types exist. Audit
   events have 6 distinct action values (`consult`, `dialogue_turn`,
   `delegate_start`, `promote`, `discard`, `escalate`, `approve`). The schema
   gap was exactly where the user predicted.

**Phase 4 — Tension analysis (~15 min).** I raised four observations, two
substantive:

1. *Emission timing*: advisory outcomes emit synchronously; delegation terminal
   outcomes are discovered asynchronously on poll. User adopted option (c):
   emit at first authoritative terminal observation + startup recovery catch-up,
   keyed on `(outcome_type, job_id)` for idempotency.

2. *`promotion_state` lifecycle mismatch*: append-only stream vs. two-point
   lifecycle. I recommended dropping `promotion_state` from
   `DelegationOutcomeRecord` because execution terminal state and user
   disposition have different authorities and timing. User agreed and also
   dropped `artifact_hash` (not reliably available at terminal-observation time).

**Phase 5 — Review skill design (~5 min).** User proposed replacing the
cross-model `codex-reviewer` agent with a `codex-review` skill over
`codex.consult`. Rationale: the reviewer agent was compensating for the older
plugin shape; codex-collaboration already has the structured advisory runtime.
I confirmed: `codex.consult` in `control_plane.py:230` already does full
context assembly, audit emission, and outcome recording. A skill that gathers
a diff and calls `codex.consult` gets all of that for free.

**Phase 6 — Workflow discriminator gap (~10 min).** I identified that
`codex-review` calling `codex.consult` would produce an `OutcomeRecord`
indistinguishable from regular consultations. User resolved: add a first-class
`workflow: ConsultWorkflow` field to `codex.consult` input and `OutcomeRecord`.
`ConsultWorkflow = Literal["consult", "review"]`. The control plane threads it
through without branching; analytics interprets.

**Phase 7 — Recording layers discussion (~5 min).** User specified three-layer
recording: T-07 ticket owns scope/ACs, decisions.md owns the durable
architecture decision, contracts.md/recovery-and-journal.md own eventual
normative schema (deferred to implementation time).

**Phase 8 — Remaining decisions (~5 min).** User adjudicated:
- AC-6: context-injection removal permitted by T-04's explicit retirement
  decision. Rewrite AC to reference "demonstrated-not-scored" honestly.
- T-05: close retroactively with evidence from the 51-commit sequence.

I stress-tested both: verified PR #108 exists (`271f23aa`, merged 2026-04-19),
confirmed sandbox exclusions are implemented at `runtime.py:23-38` (both
`excludeSlashTmp: true` and `excludeTmpdirEnvVar: true`), and found the
`resolution_ref` should be broader than PR #108 alone.

**Phase 9 — Drafting (~10 min).** Created feature branch
`chore/t07-scope-reconciliation`, drafted all four file changes.

**Phase 10 — Review and fixes (~5 min).** User reviewed and found four findings:
- P2: Shared `workflow` dependency between slices 7a and 7b (hidden).
  Fixed: made 7b depend on 7a explicitly.
- P2: Removal AC omits live delegate smoke gate. Fixed: folded into AC-5.
- P3: T-05 resolution used `541bb45f` (docs closeout) instead of `85afab6b`
  (tested code). Fixed: accurate wording.
- P3: Decision nested under wrong section. Fixed: promoted to `##` level.

Committed at `a443d336`, pushed, PR #115 opened and merged at `57d89874`.

## Decisions

### Analytics computed from existing audit/outcome streams, not cross-model event log

**Choice:** Analytics reads `analytics/outcomes.jsonl` (advisory + delegation
terminal outcomes) and `audit/events.jsonl` (lifecycle/security). No new
cross-model-style flat emitter. No raw-store walking as the primary contract.

**Driver:** User cited the two-log architecture in `recovery-and-journal.md:12`:
"The operation journal is the wrong long-term analytics source" because it is
session-bounded, fsync-before-dispatch, trimmed recovery state. The audit log
is cross-session, best-effort, human reconstruction state. The live code
already writes both streams (`journal.py:191-196`).

**Alternatives considered:**
- **Port cross-model's flat event emitter.** Rejected: would duplicate the
  already-existing audit/outcome split and add another emit path to keep
  correct. User: "I would not create a separate `~/.claude/.codex-events.jsonl`
  equivalent."
- **Walk lineage/session directories for aggregation.** Rejected: lineage store
  is session-bounded and cleanup-eligible per `contracts.md:96`. User: "I'd
  also avoid making analytics walk `lineage/<session_id>/` as the main
  aggregation mechanism."
- **Widen `OutcomeRecord` into a nullable catch-all.** Rejected: advisory
  outcomes require `turn_id`; delegation outcomes require `job_id`;
  `artifact_hash` is meaningful for delegation and meaningless for consult.
  User: "A single optional-field record would make invalid combinations easy to
  write and hard to test."

**Trade-offs accepted:** Delegation analytics requires cross-stream join
(outcomes for terminal status, audit for disposition). Advisory analytics is
outcome-only. This asymmetry reflects the actual architecture.

**Confidence:** High (E2) �� verified against live code: `OutcomeRecord` at
`models.py:202-219`, audit event emission at 7 call sites across
`delegation_controller.py`, `dialogue.py`, and `control_plane.py`.

**Reversibility:** High — the schema additions are additive. If a different
analytics source is needed later, the existing streams remain.

**Change trigger:** Revisit if the `Audit Consumer Interface` open question in
decisions.md specifies requirements that the outcome/audit split cannot serve.

### Separate `DelegationOutcomeRecord` instead of widening `OutcomeRecord`

**Choice:** Add `DelegationOutcomeRecord` with `outcome_type="delegation_terminal"`,
`job_id`, `collaboration_id`, `runtime_id`, `repo_root`, `terminal_status`,
`base_commit`. No `promotion_state`. No `artifact_hash`. Both shapes in
`analytics/outcomes.jsonl`, reader dispatches on `outcome_type`.

**Driver:** Execution terminal state and user disposition have different
authorities and timing. The Codex runtime owns "the job completed / failed /
became unknown." The user, through Claude, owns "promote / discard / leave
pending." User: "Keeping those separate maps directly onto the audit/outcome
split in recovery-and-journal.md."

**Alternatives considered:**
- **Include `promotion_state` on `DelegationOutcomeRecord`.** Rejected:
  terminal outcome emits when the job reaches terminal status; promotion
  happens later. Append-only stream cannot update. Would require either a
  second record per job or accepting stale data. User agreed: "Drop
  `promotion_state` from `DelegationOutcomeRecord`."
- **Include `artifact_hash`.** Rejected: review snapshot materialization is a
  later poll/review concern, not reliably available at terminal-observation
  time. User: "I'd also be cautious about `artifact_hash`."

**Trade-offs accepted:** The analytics skill must join audit events for
disposition metrics (promoted/discarded). Terminal outcome captures execution
result only; user disposition is audit-derived.

**Confidence:** High (E2) — verified emission timing against code flow and
existing idempotency pattern (`append_dialogue_outcome_once` at
`journal.py:266`).

**Reversibility:** High — adding fields later is additive; the reader already
dispatches on `outcome_type`.

**Change trigger:** If analytics consumers need a single denormalized record
per delegation job, consider a materialized view rather than changing the
source shapes.

### `codex-review` skill instead of `codex-reviewer` agent

**Choice:** Replace the cross-model `codex-reviewer` agent with a
`codex-review` skill that reviews diffs through `codex.consult` with
`workflow="review"`.

**Driver:** User: "Review is not fundamentally a new runtime primitive. It is
a Claude-facing workflow that gathers a diff, reads enough surrounding context,
assembles a review briefing, calls Codex for a second opinion, and then applies
Claude's own review judgment." The cross-model agent was compensating for the
older plugin shape.

**Alternatives considered:**
- **Port the reviewer agent.** Rejected: a separate agent would bypass the
  control plane and need its own emit path. The cross-model reviewer "emits no
  events — invisible to stats" per the capability analysis.
- **Dedicated reviewer using `codex.dialogue`.** Deferred as future `--deep`
  mode. User: "should not be the T-07 default."

**Trade-offs accepted:** Single-turn review via `codex.consult` may miss
nuances that a multi-turn dialogue would catch. Accepted because the review
skill synthesizes Codex findings with Claude-side judgment.

**Confidence:** High (E2) — verified that `codex.consult` at
`control_plane.py:230` already does full context assembly, audit emission, and
outcome recording. A skill consuming it gets all infrastructure for free.

**Reversibility:** High — the skill can add a `--deep`/`--dialogue` mode later
without changing the default path.

**Change trigger:** If single-turn review proves insufficient for complex diffs,
add dialogue mode. This is additive.

### First-class `workflow` discriminator on `codex.consult` and `OutcomeRecord`

**Choice:** Add `workflow: ConsultWorkflow` (default `"consult"`) to
`codex.consult` tool input and `OutcomeRecord`. `ConsultWorkflow =
Literal["consult", "review"]` for T-07. MCP validates and threads through;
control plane persists without branching; analytics interprets.

**Driver:** Without a discriminator, `codex-review` calling `codex.consult`
produces an `OutcomeRecord` indistinguishable from regular consultations.
User: "I would not use the generic `metadata` bag for the primary
discriminator." The field must be first-class.

**Alternatives considered:**
- **Use `AuditEvent.extra` for the discriminator.** Rejected: user stated
  "analytics section selection should not depend on untyped nested metadata."
- **Open `str` type.** Rejected: user preferred narrow enum to prevent
  analytics cardinality drift. "Use something like
  `Literal["consult", "review"]` only if the model layer already tolerates
  that style."

**Trade-offs accepted:** MCP tool input schema changes (minor contract
expansion). Existing rows without `workflow` default to `"consult"` during
reads.

**Confidence:** High (E2) — traced the plumbing path: skill → MCP input →
`control_plane.codex_consult()` → `OutcomeRecord`. All layers exist and accept
optional fields.

**Reversibility:** High — additive field with default. New workflow values are
future enum extensions.

**Change trigger:** If non-review workflows need discrimination (e.g.,
`"analysis"`, `"audit"`), extend the literal.

### Context-injection removal permitted by T-04 demonstrated-not-scored retirement

**Choice:** Context-injection is removed as part of the cross-model cutover.
The removal gate is satisfied by T-04's explicit retirement decision, not by a
formal aggregate benchmark pass.

**Driver:** T-04 resolution: "Context-injection remains retired by default for
codex-collaboration dialogue flows; no rollback is warranted on the evidence
captured in this benchmark track." The benchmark closed as
demonstrated-not-scored with AC-7 resolved.

**Alternatives considered:**
- **Require a formal scored benchmark pass before removal.** Rejected: T-04
  deliberately chose not to pursue aggregate scoring. The scope-rule governance
  question (Options A/B/C) resolved as moot. Requiring a scored pass would
  reopen a closed decision.
- **Keep context-injection until the three caveats are resolved.** Rejected:
  T-04's resolution explicitly says "no rollback is warranted." The caveats
  (T-20260416-01 extraction mismatch, L1/L2/L3 mechanism losses, multi-commit
  capture sequence) are acknowledged future evolution work, not blockers.

**Trade-offs accepted:** Three caveats travel with the removal. Git history
preserves all context-injection code if a future rollback is warranted after
cross-model removal.

**Confidence:** High (E2) — verified against T-04 resolution language and the
benchmark artifact set at
`docs/benchmarks/dialogue-supersession/v1/summary.md`.

**Reversibility:** Medium — context-injection code is recoverable from git
history, but restoring it after cross-model removal would require re-creating
the packaging and integration.

**Change trigger:** If a production dialogue workflow demonstrates a quality
regression that traces back to L1/L2/L3 mechanism losses.

### T-05 retroactive hygiene closeout

**Choice:** Close T-05 with `closed_date: 2026-04-19`, `resolution: completed`,
`resolution_ref: "T-05 commit sequence (6ed5f731..271f23aa), PR #108 final"`.

**Driver:** T-05 was consumed by T-06, which is itself closed. T-06's
resolution explicitly treats T-05 as complete. Stale ticket metadata, not
unresolved engineering work.

**Alternatives considered:**
- **Create a new ticket for the T-05 closeout.** Rejected: a new ticket would
  imply unresolved engineering work. User: "I would not create a new ticket for
  this."
- **Leave T-05 open until manually verified.** Rejected: all 7 ACs are
  verifiably met. Sandbox exclusions confirmed at `runtime.py:23-38`. 51
  commits, 9 merge boundaries, PR #108 final.

**Trade-offs accepted:** Retroactive closeout uses a date that matches the
last PR merge (2026-04-19), not the date of the documentation update
(2026-04-21). This is accurate to when the work completed, not when the ticket
was updated.

**Confidence:** High (E2) — verified PR #108 exists (`271f23aa`, merged
`2026-04-19T20:14:07Z`), sandbox exclusions at `runtime.py:36-37`
(`excludeSlashTmp: True`, `excludeTmpdirEnvVar: True`), all 7 test files exist.

**Reversibility:** High — if an AC is found to be unmet, reopen the ticket.

**Change trigger:** If any T-05 AC evidence is found to be incorrect.

## Changes

### T-07 ticket: full scope reconciliation

| File | What changed |
|------|-------------|
| `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` | Title updated ("reviewer" → "review"). Added Design Reconciliation section with: predecessor status table, parity matrix, analytics design (sources, schema changes, emission timing, workflow plumbing, documented limitation, analytics views), review design (skill shape, delegate integration, architecture reference), context-injection adjudication (AC-6 with caveats), slice boundaries (7a→7b→7c→7d→7e with explicit dependency on shared workflow contract). Rewrote Scope section for reconciled design. Rewrote all 6 ACs: AC-1 references specific analytics views and data sources; AC-2 specifies `codex-review` skill with `workflow="review"`; AC-5 folds live delegate smoke gate; AC-6 uses T-04 demonstrated-not-scored language. Updated Verification section. Updated References table with 4 new entries. |

### decisions.md: analytics/review architecture decision

| File | What changed |
|------|-------------|
| `docs/superpowers/specs/codex-collaboration/decisions.md` | Added `## Analytics and Review Cutover Model` as a peer section between Architecture Option Analysis and Open Questions. Records: analytics source (audit/outcome streams), outcome shape split (advisory vs delegation terminal), review discrimination (first-class `workflow` on `OutcomeRecord` and `codex.consult`), delegate review advisory-only. Cites T-07 reconciliation as driver. Links to Audit Consumer Interface open question for change trigger. |

### T-05 ticket: retroactive hygiene closeout

| File | What changed |
|------|-------------|
| `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | Frontmatter: `status: closed`, `closed_date: 2026-04-19`, `resolution: completed`, `resolution_ref: "T-05 commit sequence (6ed5f731..271f23aa), PR #108 final"`. Checked all 7 AC boxes. Added Resolution section with AC Evidence table mapping all 7 ACs to specific commits/merges. Added Successor Concerns note. Fixed T-06 commit reference to distinguish `85afab6b` (merge/tested) from `541bb45f` (docs closeout). |

### delivery.md: terminology update

| File | What changed |
|------|-------------|
| `docs/superpowers/specs/codex-collaboration/delivery.md` | Packet 6/7 description: "Analytics dashboard, reviewer, migration, and cutover" → "Analytics skill, review skill, migration, and cutover". |

## Codebase Knowledge

### Analytics/Outcome Emission Architecture

```
codex.consult request
  → control_plane.codex_consult()
       → append_audit_event(action="consult")           # audit/events.jsonl
       → append_outcome(OutcomeRecord(type="consult"))   # analytics/outcomes.jsonl

codex.dialogue.reply request
  → dialogue.dispatch_turn()
       → append_dialogue_audit_event_once(action="dialogue_turn")
       → append_dialogue_outcome_once(OutcomeRecord(type="dialogue_turn"))

codex.delegate.start request
  → delegation_controller.start()
       → append_audit_event(action="delegate_start")
       [no OutcomeRecord — terminal outcome emitted later on poll]

delegation terminal discovery (poll or recovery)
  → [T-07 7a: append DelegationOutcomeRecord(type="delegation_terminal")]

codex.delegate.promote / discard
  → delegation_controller.promote() / discard()
       → append_audit_event(action="promote" / "discard")
       [disposition is audit-only, not outcome]
```

### Three Data Paths for Analytics

| Path | File | Consumers | Retention |
|------|------|-----------|-----------|
| `analytics/outcomes.jsonl` | Advisory + delegation terminal outcomes | Analytics skill | Cross-session |
| `audit/events.jsonl` | Trust boundary, lifecycle, security | Analytics skill (join for delegation disposition) | 30-day TTL |
| `journal/<session_id>/` | Operation journal (recovery) | Control plane only | Trimmed on completion |

Analytics reads paths 1 and 2. Path 3 is NOT an analytics source.

### `OperationJournal` Path Setup

`journal.py:186-196` — the journal constructor creates three directories:
- `self._journal_dir = plugin_data_path / "journal"` (recovery)
- `self._audit_dir = plugin_data_path / "audit"` (trust boundary)
- `self._analytics_dir = plugin_data_path / "analytics"` (outcomes)

### Audit Event Actions (7 distinct)

| Action | Emitter | File:line |
|--------|---------|-----------|
| `consult` | `control_plane.py:218` | Advisory turn |
| `dialogue_turn` | `dialogue.py:268` | Dialogue turn |
| `delegate_start` | `delegation_controller.py:540` | Job creation |
| `escalate` | `delegation_controller.py:1448` | Execution needs escalation |
| `approve` | `delegation_controller.py:1642` | User resolved escalation |
| `promote` | `delegation_controller.py:1248` | User promoted delegate work |
| `discard` | `delegation_controller.py:1388` | User discarded delegate work |

### `OutcomeRecord` Current Shape

`models.py:202-219`:
```python
outcome_id: str
timestamp: str
outcome_type: Literal["consult", "dialogue_turn"]
collaboration_id: str
runtime_id: str
context_size: int | None
turn_id: str
turn_sequence: int | None = None
policy_fingerprint: str | None = None
repo_root: str | None = None
```

T-07 7a adds: `workflow: ConsultWorkflow = "consult"`.

### Sandbox Policy Implementation

`runtime.py:23-38` — `build_workspace_write_sandbox_policy()`:
- `type: "workspaceWrite"`
- `writableRoots: [worktree_path]`
- `readOnlyAccess: {type: "restricted", readableRoots: [worktree_path], includePlatformDefaults: false}`
- `networkAccess: false`
- `excludeSlashTmp: true`
- `excludeTmpdirEnvVar: true`

All 6 fields present. Overrides 4 App Server defaults. Verified at commit
`cced8727`.

### Cross-Model vs Codex-Collaboration Parity State

| Cross-model | Codex-collaboration | Parity |
|---|---|---|
| 4 skills (`codex`, `consultation-stats`, `delegate`, `dialogue`) | 6 skills (`codex-status`, `consult-codex`, `delegate`, `dialogue-codex`, `dialogue`, `shakedown-b1`) | 4/4 functional, analytics/review remain |
| 2 agents (`codex-dialogue`, `codex-reviewer`) | 4 agents (`context-gatherer-code`, `context-gatherer-falsifier`, `dialogue-orchestrator`, `shakedown-dialogue`) | dialogue complete, reviewer → skill |
| context-injection package | Claude-side scouting | Retired by T-04 decision |

### Key Locations Updated

| Concept | Location |
|---------|----------|
| T-07 ticket (reconciled) | `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` |
| Analytics/review decision | `docs/superpowers/specs/codex-collaboration/decisions.md` §Analytics and Review Cutover Model |
| T-05 ticket (closed) | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` |
| Delivery packet table | `docs/superpowers/specs/codex-collaboration/delivery.md:259` |
| `OutcomeRecord` | `models.py:202-219` |
| `AuditEvent` | `models.py:186-199` |
| Audit emission sites | `control_plane.py:214`, `dialogue.py:264`, `delegation_controller.py:536,1244,1384,1444,1638` |
| Outcome emission sites | `control_plane.py:230`, `dialogue.py:275` |
| Sandbox policy builder | `runtime.py:23-38` |
| Journal path setup | `journal.py:186-196` |
| Two-log architecture | `recovery-and-journal.md:12-27` |

## Context

### Mental Model

This was a **design reconciliation session**, not an implementation session.
The mental model was: T-07's original ACs assumed outcomes from T-04/T-06 that
resolved differently than planned. The reconciliation maps "what was assumed"
to "what actually happened" and rewrites scope accordingly.

The core insight: the cross-model analytics and reviewer were shaped by the
older plugin's architecture. Codex-collaboration has a fundamentally different
data topology (session-partitioned journals, typed audit/outcome split,
structured advisory runtime), so the replacements must be new surfaces, not
ports. User framed this precisely: "treat both replacements as new
codex-collaboration surfaces with cross-model as semantic source only."

### Project State

| Ticket | Status | Tests | Key commit |
|--------|--------|-------|------------|
| T-02 | Closed | 566 | `d4b4a988` |
| T-03 | Closed | 566 | `d4b4a988` |
| T-04 | Closed | 566 | demonstrated-not-scored |
| T-05 | **Closed (retroactive)** | 698 | `271f23aa` |
| T-06 | Closed | 845 | `85afab6b` |
| T-07 | **Open (reconciled)** | — | `57d89874` |

T-07 is the only open ticket in the codex-collaboration build sequence. All
predecessors are closed.

### Slice Sequence for T-07 Implementation

| Slice | Work | Dependencies |
|---|---|---|
| 7a | Analytics skill + `DelegationOutcomeRecord` + `ConsultWorkflow` type + `workflow` on `codex.consult` and `OutcomeRecord` | None |
| 7b | `codex-review` skill consuming `workflow="review"` | 7a (shared workflow contract) |
| 7c | Migration docs + parity matrix document | 7a + 7b |
| 7d | Context-injection removal | 7c |
| 7e | Cross-model removal + verification + live delegate smoke | 7c + 7d |

7a owns the shared `workflow` contract. 7b depends on 7a. 7c through 7e are
sequential.

## Learnings

### Design reconciliation surfaces scope drift that code review cannot

**Mechanism:** The original T-07 ACs assumed T-04 would produce a scored
benchmark pass/fail and that the reviewer would be an agent. Neither happened.
Code review catches implementation issues; reconciliation catches scope
assumptions that became stale across a multi-ticket build sequence.

**Evidence:** AC-6 said "only if the benchmark decision in T-04 passed." T-04
closed with "demonstrated-not-scored" and "AC-6 reclassified, not passed."
AC-2 said "codex-reviewer agent" but the codex-collaboration architecture
makes a skill the natural shape, not an agent.

**Implication:** For multi-ticket build sequences, reconcile scope against
predecessor evidence before starting implementation. The cost of one
reconciliation session is much lower than discovering stale assumptions during
implementation.

### The analytics source question is settled by the two-log architecture

**Mechanism:** The operation journal is session-bounded, fsync-before-dispatch,
trimmed recovery state. The audit log is cross-session, best-effort. Once you
understand the two-log split, the analytics source becomes obvious: audit and
outcome streams, not the recovery journal, not a new flat emitter.

**Evidence:** `recovery-and-journal.md:12-27` defines the split.
`journal.py:186-196` implements three separate paths. `OutcomeRecord` at
`models.py:202` already exists.

**Implication:** Future analytics extensions should read from audit/outcome
streams. If a new metric requires data not in those streams, the right fix is
to add an emission point, not to walk recovery stores.

### Execution outcomes and user disposition should be recorded separately

**Mechanism:** The Codex runtime owns "job completed/failed/unknown." The
user, through Claude, owns "promote/discard." These have different authorities,
different timing, and different failure modes. Mixing them in one record creates
lifecycle mismatches in an append-only stream.

**Evidence:** `DelegationOutcomeRecord` emits at terminal observation;
promotion/discard happens later via `delegation_controller.py:1248,1388`.
Append-only JSONL cannot update a previously written record.

**Implication:** When designing analytics schemas for multi-phase workflows,
separate the phases by authority. Join them at read time, not write time.

## Next Steps

### 1. Implement slice 7a: analytics skill + schema changes

**Dependencies:** None — can start immediately.

**What to read first:** The T-07 ticket's Design Reconciliation §Analytics
Design section. Then `models.py:202-219` (OutcomeRecord), `journal.py:186-196`
(emission paths), `control_plane.py:208-240` (consult outcome emission),
`delegation_controller.py` (audit event sites).

**What to do:**
1. Add `ConsultWorkflow = Literal["consult", "review"]` to `models.py`.
2. Add `workflow: ConsultWorkflow = "consult"` to `OutcomeRecord`.
3. Add `DelegationOutcomeRecord` to `models.py`.
4. Add `workflow` parameter to `codex.consult` MCP tool input.
5. Thread `workflow` through `control_plane.codex_consult()` to
   `OutcomeRecord`.
6. Add `DelegationOutcomeRecord` emission on terminal job observation in
   `delegation_controller.py` with `append_once` keyed on
   `(outcome_type, job_id)`.
7. Add startup recovery catch-up in `_ensure_delegation_controller()`.
8. Create analytics skill at
   `packages/plugins/codex-collaboration/skills/codex-analytics/SKILL.md`.
9. Add analytics computation reading `analytics/outcomes.jsonl` and
   `audit/events.jsonl`.

**Approach:** Start with schema changes (steps 1-5), add tests, then emission
(steps 6-7), then the skill (steps 8-9).

### 2. Implement slice 7b: codex-review skill

**Dependencies:** 7a (shared `workflow` contract must exist).

**What to do:** Create `codex-review` skill that gathers diff, calls
`codex.consult` with `workflow="review"`, synthesizes findings. Test with a
real diff.

### 3. Implement slices 7c-7e: migration docs, removal, verification

**Dependencies:** 7a + 7b complete.

**What to do:** Write migration docs, formalize parity matrix, remove
context-injection, remove cross-model, run live delegate smoke (or document
deferral).

## In Progress

**Clean stopping point.** All reconciliation work completed, committed, and
merged to main at `57d89874`. PR #115 merged. No code changes in flight. T-07
ticket is reconciled and ready for implementation starting at slice 7a.

## Open Questions

### 1. Abandoned cross-session delegation terminal outcomes

**Context:** If a delegation job reaches terminal status in a session that
crashes before poll, and the next session has a different session ID, the
terminal outcome may be missing from `analytics/outcomes.jsonl`. The job store
retains the data.

**Decision pending until:** T-07 7a implementation — document as a known
limitation. A broader stale-session analytics sweep would be a separate design
choice.

### 2. Codex P2: Non-store busy sources in active delegation summary (inherited)

**Context:** `get_active_delegation_summary()` only checks the job store while
`start()`'s busy gate checks three sources. Source (b) (runtime registry) is
genuinely reachable in a narrow window.

**Decision pending until:** Production evidence or T-07 implementation
determines it should be addressed.

### 3. `git diff --binary` output stability (inherited)

**Context:** Post-apply verification relies on byte-for-byte comparison of
regenerated `full.diff`.

**Decision pending until:** Production testing.

### 4. `request_user_input` answer construction in live skill (inherited)

**Context:** Design specifies Claude constructs the `answers` parameter from
conversation context. Untestable without live skill invocation.

**Decision pending until:** First live `request_user_input` escalation through
the delegate skill.

## Risks

### 1. Implementation may surface schema gaps not visible in reconciliation

The reconciliation identified the `DelegationOutcomeRecord` shape and
`workflow` discriminator at a design level. Implementation may reveal additional
fields needed or emission timing edge cases not considered. The shapes are
directional — expect refinement during 7a.

### 2. Live delegate smoke may be deferred again

The live delegate smoke requires Codex App Server. If it's unavailable during
7e, the removal AC allows explicit deferral (matching T-06's pattern), but this
means cross-model removal happens without end-to-end product verification.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-07 ticket (reconciled) | `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` | Scope and ACs |
| Analytics/review decision | `docs/superpowers/specs/codex-collaboration/decisions.md` | Architecture decision |
| Delivery spec | `docs/superpowers/specs/codex-collaboration/delivery.md` | Build sequence |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Tool surface, response shapes |
| Recovery and journal | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Two-log architecture |
| T-04 ticket (closed) | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | Context-injection evidence |
| T-05 ticket (closed) | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | Execution domain evidence |
| T-06 ticket (closed) | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Delegate evidence |
| Capability analysis | `docs/reviews/2026-03-17-cross-model-capability-analysis.md` | Cross-model inventory |
| Benchmark contract | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Context-injection retirement |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-21_14-56_t06-pr-review-merge-and-ticket-closure.md`
- T-07 arc: T-06 closure → **T-07 scope reconciliation (this handoff)** → 7a implementation

### Commits this session

| Commit | Title |
|--------|-------|
| `a443d336` | docs(t20260330-07): reconcile analytics review cutover scope |
| `57d89874` | Merge pull request #115 (merge commit) |

### PR

- PR #115: `docs(t20260330-07): reconcile analytics review cutover scope` — MERGED at `57d89874`

## Gotchas

### 1. `rg` misses dict-literal field names

`rg "excludeSlashTmp"` returns no results when searching Python server code
because the field names are string keys inside a dict literal
(`"excludeSlashTmp": True`), not Python identifiers. The `rg` patterns
`excludeSlashTmp` and `exclude_slash_tmp` both miss the camelCase string key.
Use exact string search: `rg '"excludeSlashTmp"'`.

**Discovered when:** Verifying T-05 sandbox AC. Initial search returned empty;
direct file read at `runtime.py:23-38` confirmed the fields exist.

### 2. T-05 had 9 merge boundaries but only 1 GitHub PR

Most T-05 work landed via direct branch merges to main, not GitHub PRs. Only
the final slice (pending-request capture, AC 6) went through PR #108. Using
only PR #108 as `resolution_ref` would be inaccurate. The commit range
`6ed5f731..271f23aa` captures the full sequence.

### 3. Pyright stale diagnostics after subagent writes (inherited)

Pyright reports methods as unknown even though they exist and tests pass. LSP
server doesn't get real-time file-change notifications from subprocess edits.
Verify with test execution, not Pyright diagnostics.

## User Preferences

### Design reconciliation before coding

User explicitly prescribed: "T-07 design reconciliation, not coding. First step
should be a scope reconciliation pass over the closed T-04/T-06 evidence and
the T-07 ACs." This was the first instruction in the handoff's Next Steps and
was followed exactly.

### New surfaces, not ports

User: "I'd treat both replacements as new codex-collaboration surfaces with
cross-model as semantic source only, not as ports." This framing drove every
design decision — analytics source, outcome shapes, review skill vs agent.

### Contract precision over convenience

User: "A single optional-field record would make invalid combinations easy to
write and hard to test." Chose separate typed records over a nullable catch-all.
This repo has been strict about contract precision throughout.

### Honest evidence labeling

User: "Context-injection removal is permitted because T-04 explicitly resolved
the retirement decision. This is a demonstrated-not-scored adjudication, not a
formal aggregate benchmark pass." Refused to call it a "pass" when the
benchmark deliberately chose not to score.

### Explicit deferral over silent omission (inherited)

User previously instructed: "do not silently imply it did." Applied again in
this session: the live delegate smoke is folded into AC-5 with an explicit
App Server deferral escape hatch.

### Structured review before merge

User reviewed the draft and provided four structured findings (2× P2, 2× P3)
with file locations, confidence scores, and specific fix instructions. All
four addressed before merge. Pattern: user does a thorough review pass before
declaring work reviewable.
