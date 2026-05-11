---
date: 2026-04-13
time: "19:45"
created_at: "2026-04-13T23:45:16Z"
session_id: fbbd0301-acf5-4058-9244-a0f9320acffb
resumed_from: docs/handoffs/archive/2026-04-13_18-50_t04-gap-analysis-and-turn-semantics-closure.md
project: claude-code-tool-dev
branch: feature/t04-v1-scoping-plan
commit: 72c66714
title: "T-04 v1 scoping plan drafted, pending user review"
type: handoff
files:
  - docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md
---

# T-04 v1 Scoping Plan Drafted, Pending User Review

## Goal

Convert the prior session's clean stopping point (T-04 gap analysis complete,
T-20260410-01 closed) into a forward-moving artifact: a scoping plan for the
v1 production `/dialogue` slice in codex-collaboration. The plan must
**assemble accepted T1–T6 contracts into a user-facing surface** rather than
literally port cross-model — that framing distinction was the central
architectural pivot of this session.

**Trigger:** Resumed from the prior handoff with my recommendation to "port
the production dialogue surface from cross-model." The user pushed back on
the "port" framing in their first turn with three independent evidence
citations, then escalated with a second pressure-point response after I
revised. The session converged on a third proposal (assembly + migration
sequencing) and I drafted the plan against six explicit pin-down asks.

**Stakes:** This is the first concrete plan artifact for the broader T-04
implementation packet — the sprint that takes codex-collaboration from
"shakedown-validated runtime" to "user-adoption-ready production surface."
The plan's framing decisions (port-vs-assemble, what to migrate now vs
later, what containment shape, what to reuse from T8) constrain every
implementation session that follows.

**Success criteria for this session:**

1. Reach alignment on framing (port vs assemble) — **achieved.**
2. Pin down v1 scope and non-goals — **achieved in plan §2.**
3. Make and document material judgment calls on synthesis format,
   containment, T8 reuse, and migration sequencing — **achieved.**
4. Produce a draftable plan grounded in evidence with file:line
   citations — **achieved at 517 lines.**
5. Hand off to user for review — **this handoff.**

**Connection to project arc:** The supersession chain is at packet 3 of 6.
T-02/T-03 closed last session as verification work. T-04 is the first
genuine implementation sprint in the chain. T8 shakedown validated the
per-turn loop on B4. This v1 scoping plan defines the production slice
that turns the validated loop into a user-facing surface — the gating
work for codex-collaboration to retire cross-model in practice.

## Session Narrative

**Phase 1 — Load and recommend (~5 min):**

Loaded the prior handoff. Summarized the three-phase shape of T-04
(shakedown done, broader packet next, scored benchmark parked).
Recommended starting the broader packet by "porting the production
dialogue surface from cross-model" with cross-model `/dialogue` skill
and `codex-dialogue` agent as semantic sources. Asked: formal plan or
direct execution?

**Phase 2 — User's first pushback (~10 min):**

User agreed on direction but rejected the "port" framing with three
specific citations:

1. The T-04 ticket itself labels cross-model surfaces as "Semantic
   source only" — not implementation templates.
2. Cross-model `/dialogue` is built around context-injection MCP tools
   and a `server_assisted` / `manual_legacy` model. T-04's intended
   mode is `agent_local`, structurally different.
3. The convergence-loop risk analysis explicitly argues cross-model
   complexity exists because it straddles a process boundary and
   should simplify in T-04, not be copied.

User proposed instead: contract first → thin orchestration → gatherers
in production-needed form → first E2E. On planning: small formal plan,
not a long T7-style cycle.

**Key pivot (~30 min):**

Read the three cited docs to ground my response:
`2026-04-01-t04-convergence-loop-risk-analysis.md` (347 lines, hadn't
seen before), the T-04 ticket, and `2026-04-02-t04-t5-mode-strategy.md`
(329 lines). Confirmed user's framing. Refined my position with a
specific claim: the contract isn't fully greenfield — T1–T6 are
accepted and assembled. The plan's job is **assembly + ownership +
migration sequencing**, not contract authoring. Offered to draft.

**Phase 3 — User's second pushback (~10 min):**

User agreed with revision but added four pressure points that the plan
must answer:

1. Don't assume cross-model `dialogue/SKILL.md` parser is in critical
   path — Risk H mitigation says it's only required if v1 still
   depends on it.
2. "Anchor to T8" must mean reuse verification scaffolding and
   containment mechanics, **not** reuse the shakedown user flow or
   shakedown agent.
3. Frame the open containment question as **production scope-envelope
   design**, with one model for both code and falsifier gatherers.
4. "Thin orchestration" must be thin in surface area, not thin in
   truthfulness — the first slice still needs all accepted T1–T6
   semantics or it becomes throwaway.

User listed six things they wanted the plan to pin down: invocation +
artifact guarantee, ownership table, minimum production loop,
containment model, migration table split (required vs deferred), and
verification path that reuses T8 without collapsing the boundary. Said
"Draft that plan. I'll review it against exactly those pressure points
once it has been drafted."

**Phase 4 — Evidence gathering (~15 min):**

Created branch `feature/t04-v1-scoping-plan`. Read in parallel:
`shakedown-dialogue.md` (17 lines — confirmed it's a thin wrapper
loading dialogue-codex), `mcp_server.py` (270 lines — confirmed the
3 `codex.dialogue.*` tool surface), `context-gatherer-code.md` and
`context-gatherer-falsifier.md` from cross-model (confirmed tag
grammar, COUNTER constraints, and the falsifier's repo-first
exploration of `docs/decisions/` etc), and the T4 `containment.md`
(152 lines — found T4-CT-04 benchmark scope requirement and T4-CT-05
declared safety dependency for secrets).

The containment.md read produced the v1 scope-envelope decision: T4
already has the structural answer (`allowed_roots`, post-execution
filter on canonical paths, anti-narrowing invariant); v1 just needs
to choose the granularity (coarse repo-root vs anchor-derived).

**Phase 5 — Plan drafting (~25 min):**

Wrote the plan to
`docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`.
13 sections, 7 tables, 517 lines. Made six material judgment calls
(see Decisions section below). Hook flagged length. Surfaced the
length issue to user transparently with three options (review as-is,
in-place trim pass, modularize via spec-writer) and a recommendation
to review as-is first.

**Phase 6 — Handoff (~5 min):**

User chose to review the draft as-is in next session and asked for a
handoff. Plan file is uncommitted on `feature/t04-v1-scoping-plan` —
the user will likely want to read the file directly during review.

## Decisions

### Decision 1: Frame v1 work as "assembly," not "port"

**Choice:** The v1 plan is positioned as assembling accepted T1–T6
contracts into surfaces that did not previously exist
(`/dialogue` skill, dialogue-orchestrator agent, two production
gatherer agents). Cross-model is consulted as **semantic source only**
for tag grammar, behavioral patterns, and convergence semantics — not
as an implementation template.

**Driver:** Three independent evidence sources from user's pushback:
the ticket's "Semantic source only" framing, T5's deliberate
non-migration of `codex-dialogue.md`, and the risk analysis's central
principle that "complexity in the source architecture doesn't mean
complexity in the port" (line 144). Risk E shows it concretely:
`unknown_claim_paths`, entity extraction, HMAC scout tokens — all
plumbing that exists only because cross-model straddles a process
boundary and "evaporates" with direct tool access.

**Alternatives considered:**

- **Literal port** — copy cross-model surfaces and adapt MCP routing.
  Rejected because it would re-import accidental complexity from the
  process-boundary plumbing (Risk E), and because cloning
  `codex-dialogue.md` would produce a contract violation: T5 §6
  explicitly bars that agent from emitting `agent_local`.
- **Greenfield redesign** — author new contracts from scratch.
  Rejected because T1–T6 are already accepted with explicit
  rationale, hostile-review verdicts, and 4-commit Codex-reviewed
  remediations. Re-authoring would discard sunk design work.

**Trade-offs accepted:** The plan must take a position on which T1–T6
behaviors live in the orchestrator vs the dialogue-codex skill vs the
gatherers. Some boundary calls may need refinement during
implementation. The risk is real but lower than the alternatives.

**Confidence:** High (E2) — three evidence sources from user, all
confirmed by direct doc reads.

**Reversibility:** Medium — re-framing as "port" would require
re-doing the ownership table and the migration table.

**Change trigger:** Implementation discovers that some T1–T6 contract
surface cannot live in codex-collaboration without re-importing
context-injection plumbing.

### Decision 2: codex-collaboration owns its own synthesis format

**Choice:** v1 emits a synthesis artifact owned by codex-collaboration
(plan §3.2). The artifact is **not bound** to cross-model's
`dialogue-synthesis-format.md`. The T5 migration set (event_schema.py
`VALID_MODES`, dialogue-synthesis-format.md prose, dialogue/SKILL.md
parser) is **deferred** behind a named trigger: "binding the first
time a cross-model consumer is expected to ingest a v1 artifact."

**Driver:** User pressure point: "I would not assume the cross-model
`dialogue/SKILL.md` parser is automatically in the critical path.
Risk H says that parser must be migrated only if the new path still
depends on it. If codex-collaboration owns its own /dialogue surface
and artifacts, that parser may be a follow-on consumer migration, not
a v1 blocker."

**Alternatives considered:**

- **Emit cross-model's format extended with `agent_local`** — would
  force the four-step T5 migration as a v1 blocker (event_schema +
  format doc + parser + tests + handbook updates). Invasive across
  cross-model tests and operator documentation.

**Trade-offs accepted:** If a future consumer (e.g., the benchmark
adjudicator) does want the cross-model format, the deferred migration
becomes binding. The trigger is named explicitly so the deferral is
not a silent dependency.

**Confidence:** High (E2) — the user's framing is consistent with the
ticket's "no analytics dashboard or cutover" out-of-scope clause.

**Reversibility:** High — reversing means picking up the deferred
migration table; it does not require redesigning v1.

**Change trigger:** A consumer demands the cross-model format. Most
likely candidates: scored benchmark adjudicator (likely needs
benchmark-specific fields anyway), or analytics dashboard
(out-of-scope per ticket).

### Decision 3: Coarse repo-root `allowed_roots` for v1 containment

**Choice:** v1 production `/dialogue` uses `scope_envelope` with
`allowed_roots = [<repo_root>]`. Same model applies uniformly to
pre-dialogue gatherer invocations and mid-dialogue orchestrator
scouting. Containment guard enforces at PreToolUse for Read/Grep/Glob
(T4-CT-02).

**Driver:** Three constraints converge on this:

1. T4-CT-04 requires a non-empty `scope_envelope` for any benchmark
   run — starting production at repo-root keeps the mechanism live in
   the v1 path so later benchmark runs don't introduce a new
   enforcement surface.
2. The falsifier's value comes from broad repo-first exploration of
   `docs/decisions/`, `docs/plans/`, `docs/learnings/`. Repo-root
   `allowed_roots` preserves that surface while still giving the
   containment guard a real fence.
3. One model for both gatherers is cleaner than bespoke rules per
   gatherer.

**Alternatives considered:**

- **Anchor-derived `allowed_roots`** (narrower, derived from briefing
  seeds) — rejected because T4-BR-07 prerequisite item 5 flags
  conceptual-query root selection as a benchmark-blocked prerequisite
  requiring a validator-enforceable rule. v1 is not the venue to
  resolve that.
- **Unrestricted (consultation-contract default)** — rejected because
  it contradicts T4-CT-04's presence requirement for future benchmark
  runs and offers no containment mechanism to extend.

**Trade-offs accepted:** Coarse containment doesn't address the
T4-CT-05 declared safety dependency (secrets in tracked files). v1
inherits this assumption explicitly with a release-note commitment.
A post-v1 packet owns resolving it (likely redaction at PreToolUse or
gatherer output capture).

**Confidence:** High (E2) — all three constraints have explicit doc
citations.

**Reversibility:** High — narrowing later (anchor-derived) is purely
additive on top of repo-root containment.

**Change trigger:** Production use against repos with credentials in
tracked files (general-purpose deployment beyond curated corpora).

### Decision 4: dialogue-orchestrator is a NEW agent, not extended from shakedown-dialogue

**Choice:** Author a new agent file at
`packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md`.
The shakedown-dialogue agent (17-line wrapper) and shakedown-b1 skill
remain untouched. Production orchestrator loads dialogue-codex skill
directly via `skills:` frontmatter, same pattern as shakedown-dialogue,
but is otherwise separate.

**Driver:** User pressure point: "'Anchor to the T8 shakedown harness'
is good only if it means reuse the verification scaffolding and
containment mechanics, not reuse the shakedown user flow or shakedown
agent as the production path. The repo has already worked hard to
separate internal shakedown from production dialogue."

**Alternatives considered:**

- **Extend shakedown-dialogue to handle production** — rejected
  because it collapses the shakedown/production boundary the project
  has deliberately maintained.
- **Reuse shakedown-b1 as the production user flow** — rejected for
  the same reason; shakedown-b1 is operator-facing harness for B1
  scope, not user-facing dialogue.

**Trade-offs accepted:** Two parallel agents that share the
dialogue-codex skill load pattern. Slight duplication, but the
separation prevents accidental coupling of production failure modes
to shakedown failure modes.

**Confidence:** High (E2) — user explicitly named the boundary as a
project-level invariant.

**Reversibility:** Low — once two agents are in production, merging
them later would be a design change with cross-cutting impact.

**Change trigger:** Discovery during implementation that the
production orchestrator's needs exactly match shakedown-dialogue's
needs (very unlikely — shakedown is bounded to a single benchmark
task; production handles arbitrary user objectives).

### Decision 5: T8 reuse is infrastructure + rubric, not user flow

**Choice:** v1 reuses T8's containment guard mechanics, transcript
capture scaffolding (JSONL shape), and 14-item inspection rubric. The
14-item rubric is reused **as a verification test tool**, not as a
production artifact. shakedown-b1 user flow and shakedown-dialogue
agent are NOT reused.

**Driver:** Same user pressure point as Decision 4. Plus my own
recognition that the 14 inspection items encode the T1–T6 per-turn
contract; using them as a v1 test rubric is the cheapest way to
verify that v1's first transcript actually conforms to the accepted
contracts.

**Alternatives considered:**

- **Reuse the entire shakedown harness** — collapses the boundary.
- **Author new verification tooling** — duplicates work; the 14-item
  rubric is already validated against B4.

**Trade-offs accepted:** The 14-item rubric is presented in
shakedown-b1's SKILL.md, so the production verification path
references a shakedown skill file for the rubric while not invoking
the shakedown flow. This is borderline — could be cleaned up later
by extracting the rubric to a standalone reference doc.

**Confidence:** High (E2).

**Reversibility:** High — extracting the rubric to its own file is
mechanical.

**Change trigger:** Future shakedown evolution makes the 14-item
contract specific to shakedown rather than universal to dialogue-codex.

### Decision 6: T1–T6 accepted semantics are all present in v1 loop

**Choice:** The v1 minimum production loop (plan §6.1) commits to
every accepted T1–T6 semantic from the first slice:
TerminationCode enum, fallback-claim provenance tagging, deterministic
referential continuity, structured per-scout evidence records,
agent_local mode emission, structured synthesis output, scope-breach
termination separate from convergence, ledger summary survival under
compression, cross-turn unresolved diff.

**Driver:** User pressure point: "'Thin orchestration' only works if
it is thin in surface area, not thin in truthfulness. The first slice
still needs the real accepted semantics… If it punts those, it
becomes a throwaway path."

**Alternatives considered:**

- **Punt some semantics to a later pass** — would require either
  (a) re-doing the loop later when the missing semantic blocks a use
  case, or (b) accepting the loop as throwaway. User explicitly
  rejected (b).

**Trade-offs accepted:** The orchestrator is correspondingly larger
than a pure transport layer. But each step in the loop maps to a
specific T-contract or risk-analysis mitigation, so the size is
truthful, not bloated.

**Confidence:** High (E2).

**Reversibility:** Medium — removing a semantic later would require
deciding whether the dropped behavior was actually unnecessary or
was a correctness gap.

**Change trigger:** Implementation discovers that a T1–T6 contract
cannot be satisfied with current runtime surface (very unlikely —
T8 shakedown already proved the per-turn contract works against the
runtime).

## Changes

### `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`

**What changed:** New file (517 lines). Frontmatter declares status:
Draft, supersession_ticket: T-20260330-04, prior_authority listing T1
through T8 + risk analysis. 13 sections: Purpose and Non-Purposes,
Scope, User-Facing `/dialogue` Contract, Ownership Table, Containment
Model for v1, Minimum Production Loop, Migration Table, Verification
Path, v1-Specific Risks, v1 Open Questions, Acceptance Criteria for
Plan Approval, Next Step, References. 7 tables: ownership (9 rows),
out-of-scope (9 rows), required migrations (6 rows), deferred
migrations (5 rows), T8 reuse (6 rows), verification checks (9 rows),
synthesis fields (10 rows).

**Why:** Pin down v1 scope and non-goals per user's six explicit
asks. Make the six material judgment calls (synthesis format,
containment, orchestrator separation, T8 reuse, T1–T6 semantics
inclusion, cross-model migration deferral) explicit and evidence-backed.

**Status:** Uncommitted on `feature/t04-v1-scoping-plan`. Pending
user review.

### Branch state

Created `feature/t04-v1-scoping-plan` from `main` at `72c66714`. No
commits on the branch yet — plan file is untracked. User may want to
read the file directly during review; commit happens after their
feedback.

## Codebase Knowledge

### codex-collaboration runtime surface (codex.dialogue.*)

The MCP server at
`packages/plugins/codex-collaboration/server/mcp_server.py:15-83`
exposes 5 tools, with 3 forming the dialogue surface:

| Tool | Required args | Purpose |
|---|---|---|
| `codex.dialogue.start` | `repo_root` | Create durable dialogue thread; profile resolved at start, persisted for all replies |
| `codex.dialogue.reply` | `collaboration_id`, `objective` | Continue a dialogue turn on existing handle |
| `codex.dialogue.read` | `collaboration_id` | Read dialogue state |

Dispatch is serialized through `_dispatch_tool` (line 216) — single
chokepoint, INVARIANT comment at line 219 warns that any concurrent
dispatch model must revisit advisory locking and turn sequencing.

The server uses a `dialogue_factory` lazy-init pattern (line 115) with
a one-way pin: factory called at most once, controller cached for
process lifetime. Recovery runs on first dialogue tool call when
deferred via factory.

### shakedown-dialogue agent (the boundary the production path must NOT cross)

`packages/plugins/codex-collaboration/agents/shakedown-dialogue.md` is
17 lines:

```yaml
name: shakedown-dialogue
description: Contained pre-benchmark shakedown agent for B1 dialogue.
  Invoked by the shakedown-b1 skill. Do not use directly.
model: opus
maxTurns: 30
tools: [Read, Grep, Glob, mcp__plugin_codex-collaboration_codex-collaboration__codex_dialogue_start, ..._reply, ..._read]
skills: [dialogue-codex]
```

Single-line body: "Execute the dialogue-codex skill procedure. Your
Read, Grep, and Glob calls are constrained to the B1 scope by the
containment guard — you can access any file within the scope
directories. You do not need to manage containment — the harness
handles it transparently."

This is the pattern the production orchestrator should mirror but not
extend: `skills: [dialogue-codex]` frontmatter loads the per-turn
contract, tools allowlist constrains MCP access, and the body
delegates to the skill. The production orchestrator's body will be
longer because it owns the user-objective routing and synthesis
emission, not just shakedown execution.

### Cross-model gatherer agents (semantic sources for adaptation)

**`context-gatherer-code.md`** (111 lines): single-purpose explorer.
Tools: Glob, Grep, Read. Model: sonnet. Emits `CLAIM` and `OPEN`
prefix-tagged lines with citations (`@ path:line`) and provenance
tags (`[SRC:code]`). 40-line cap. Explicit constraint: "Do not
explore docs/decisions/, docs/plans/, docs/learnings/, or git
history — those are the falsifier agent's domain."

**`context-gatherer-falsifier.md`** (157 lines): assumption tester
with broad repo-first exploration. Same tools and model. Emits
`COUNTER`, `CONFIRM`, `OPEN`, `CLAIM` (CLAIM only in no-assumptions
fallback). COUNTER constraints: max 3 per consultation; every COUNTER
requires citation, AID (assumption ID), and TYPE from a 5-value
whitelist (interface mismatch, control-flow mismatch, data-shape
mismatch, ownership/boundary mismatch, docs-vs-code drift).
No-assumptions fallback explores rationale surfaces only
(docs/decisions/, docs/plans/, docs/learnings/, CLAUDE.md, README.md).

Both agents reference §15 of the consultation contract (governance:
prompt/log retention debug-gated, redaction failures fail-closed,
egress sanitization). For codex-collaboration adaptation, rules 3-5
and 7 don't apply (those are Codex-calling rules — gatherers don't
call Codex).

### T4 containment model

`docs/plans/t04-t4-scouting-position-and-evidence-provenance/containment.md`
(152 lines, normative authority `containment`):

| Requirement | Mechanism |
|---|---|
| **T4-CT-01** | Per-call counting: N out-of-scope results = 1 breach. Mid-round `scope_breach_count >= 3` → pending-round marker → T1 termination |
| **T4-CT-02** | Pre-execution confinement at the harness, not the agent. Read target checked before execution; Grep/Glob `path` parameter set to `scope_root` within `allowed_roots` |
| **T4-CT-03** | Post-containment capture — transcript records output AFTER containment filter; "raw" means "unprocessed by the agent," not "unfiltered by the harness" |
| **T4-CT-04** | Benchmark runs require non-empty `scope_envelope` |
| **T4-CT-05** | Declared safety dependency: allowed-scope secrets are NOT redacted by T4 — explicit T7 external blocker |

Anti-narrowing invariant: agent MUST NOT select narrower `scope_root`
to exclude contradicting evidence.

### Risk analysis pre-design invariants (lines 296-303)

Four invariants the v1 plan must honor:

1. `converged` and termination fields computed from structured state,
   never prose. `compute_action` equivalent returns TerminationCode
   enum.
2. Synthetic minimum-claim fallbacks explicitly marked
   (`claim_source=fallback`); excluded from `new_claims` for
   `effective_delta`.
3. Candidate evidence retained as structured provenance per-scout
   `{turn, target_claim, path, line_range, snippet, disposition}`.
4. Any new mode value treated as cross-contract migration
   (event_schema, parser, format doc).

The plan's §6.1 loop steps each cite which T-contract or risk
mitigation they implement.

### T5 mode strategy deliberate non-migration

`docs/plans/2026-04-02-t04-t5-mode-strategy.md:217-222` lists
deliberate non-migrations: cross-model `codex-dialogue.md` continues
to define only `server_assisted` and `manual_legacy`, will NOT emit
`agent_local`. This is why "porting codex-dialogue.md" would produce
a contract violation, not parity.

T5 §6 also enumerates the migration set IF cross-model surfaces are
to consume `agent_local`: synthesis-format prose, JSON epilogue
contract, event_schema VALID_MODES, dialogue/SKILL.md parser, three
test files. The plan §7.2 lists exactly this set as deferred.

## Context

### Branch and Repository State

- **Branch:** `feature/t04-v1-scoping-plan` (created from `main` at
  `72c66714`)
- **Working tree:** One untracked file —
  `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`
- **Commits on branch:** None yet (plan uncommitted)
- **Remote:** Branch not pushed

### Mental Model

**v1 = assembly + ownership + migration sequencing, not contract
design.** This is the central frame. T1–T6 already settled the hard
behavioral semantics. T7 defined the executable slice for shakedown.
T8 implemented and validated it. The work that remains is composing
those into surfaces that did not previously exist: a user skill, an
orchestrator agent, two gatherer agents, and a synthesis artifact.

**The shakedown/production boundary is rigid.** This is not an
optimization — it's a project-level invariant the user has reinforced
multiple times. Any plan or implementation that blurs it is a defect.

**Migrations are deferred until proven necessary.** The plan's
deferral-trigger pattern keeps v1 honest without pre-committing to
cross-model surgery. The trigger is named explicitly so deferred work
isn't a silent dependency.

### Plan length context

The plan is 517 lines, which the PostToolUse hook flagged as exceeding
its 500-line threshold. Comparison points:

| Doc | Lines | Shape |
|---|---|---|
| T7 executable slice (`2026-04-07-t7-executable-slice-definition.md`) | 447 | Defines shakedown executable slice |
| This v1 scoping plan | 517 | Defines production assembly slice |
| T8 minimum runnable shakedown packet | TBD | Defines shakedown packet |

The plan's length is mostly table-driven (7 tables), not speculative
prose. Each table maps to a specific user pin-down ask. Trimming prose
is cheap; trimming tables would drop pin-down answers.

### What the user said about the draft

User has not yet read the plan as written. The session ended with
"save a handoff. I will review this draft as-is, then share my
feedback in the next session." This is a deliberate review pattern —
user wants a fresh pass on the artifact, not in-conversation iteration.

## Learnings

### "Port" framing collapses two distinct architectural relationships

**Mechanism:** When semantically-related code exists in another
plugin, "port" is a tempting verb because it implies low-risk
mechanical work. But it elides whether the source code is being used
as a **structural template** (copy + adapt the shape) or a
**semantic reference** (consult for behavioral patterns, write fresh
implementation). These are very different tasks with different risk
profiles.

**Evidence:** Three separate doc citations from the user's pushback
all said the same thing: the cross-model surfaces are "Semantic
source only" (ticket), the cross-model orchestrator deliberately
won't emit agent_local (T5 §6), and cross-model complexity
"evaporates" with direct tool access (risk analysis line 144). My
"port" framing was reading semantic-source language as
structural-template language.

**Implication:** When proposing reuse from another plugin, name the
relationship explicitly: "structural template" or "semantic source."
The verb choice matters for downstream scope estimation.

### Risk-analysis-style "what to keep, what to drop" patterns prevent re-importing accidental complexity

**Mechanism:** Risk E in the convergence-loop risk analysis
distinguishes the **mechanism** (`unknown_claim_paths` path-tracking,
template matching, HMAC scout tokens) from the **function**
(provenance debt tracking). It says: drop the mechanism, keep the
function. The same pattern applies across the cross-model →
codex-collaboration adaptation.

**Evidence:** Risk E's correction note: "Original recommendation said
'drop unknown_claim_paths' without distinguishing mechanism from
function. The provenance debt tracking function must survive — only
the helper-specific path machinery should go."

**Implication:** When adapting code across plugins with different
architectural shapes, frame the adaptation as a "mechanism vs
function" decomposition for each subsystem. The plan's gatherer
adaptation explicitly applies this rule.

### Deferral triggers prevent silent dependency growth

**Mechanism:** The plan's §7.2 lists deferred migrations with a
named trigger ("binding the first time a cross-model consumer is
expected to ingest a v1 artifact"). This makes the deferral a
**conditional commitment** rather than a **silent gap**. Reading the
plan, anyone can immediately see the conditions under which deferred
work becomes blocking.

**Evidence:** The user's pressure point that originally surfaced this:
"I would not assume the cross-model dialogue/SKILL.md parser is
automatically in the critical path… If codex-collaboration owns its
own /dialogue surface and artifacts, that parser may be a follow-on
consumer migration, not a v1 blocker."

**Implication:** Deferral tables in scoping plans should always carry
a trigger column. "Deferred to later compatibility work" without a
trigger is a recipe for forgotten dependencies.

### Plan-length verdict is best left to the user, not the model

**Mechanism:** I drafted at 517 lines knowing the hook would flag it.
The honest move was to surface the length transparently and offer
options (review as-is, in-place trim, modularize) rather than
silently compress. The user picked "review as-is" — confirming that
the right call was to surface, not pre-emptively reduce.

**Evidence:** Hook fired with the >500-line warning; I noted it,
explained what was driving the length, offered three options, and
recommended (1). User implicitly accepted by asking for a handoff
without comment on length.

**Implication:** When tooling flags a soft constraint (line count,
token budget, file count) and the work has substance, surface the
flag with options rather than silently reshaping. The user is the
right judge of whether substance vs constraint matters more.

## Next Steps

### 1. User review of v1 scoping plan (next session)

**Dependencies:** None — plan file is on disk, branch ready.

**What to read first:**

1. `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`
   — the artifact under review.

**Approach suggestion:** Review the plan against the six pressure
points the user named:

1. Cross-model parser — deferred to §7.2; check the deferral trigger
   is sharp enough.
2. T8 reuse — separated in §8.1 reuse table; check the
   shakedown/production boundary invariants in §8.4 are airtight.
3. Containment — §5 with one model for both gatherers; check whether
   coarse repo-root is the right call vs anchor-derived.
4. Thin-but-truthful orchestration — §6.1 loop steps each cite
   T-contracts or risk mitigations; check none are punted.
5. Ownership table (§4) — concrete paths, status (new/existing/
   untouched); check no entry contradicts T5 deliberate non-migration.
6. Migration table (§7) — required vs deferred with trigger; check
   the split is defensible.

User's words: "I will review this draft as-is, then share my feedback
in the next session."

### 2. Address review feedback

**Dependencies:** User feedback from step 1.

**Likely shapes of feedback:**

- **Trim request** — sections to compress. I offered an in-place trim
  pass with ~80–120 lines savings probable.
- **Modularization request** — split via `/superspec:spec-writer` into
  authority files. Worth it only if implementation sessions will pull
  different authorities separately.
- **Substance change** — re-decide one of the six judgment calls.
  Most likely candidates: containment granularity (§5) or the
  T8-rubric reuse coupling (§8.1 borderline call).

### 3. Commit and merge plan

**Dependencies:** Review feedback addressed.

**Note:** Branch `feature/t04-v1-scoping-plan` is ready to commit.
After commit, decide PR vs direct merge to main. Given this is a
plan doc (not code), direct merge is reasonable per the project's
established pattern for design plans.

### 4. Begin implementation per plan §12

**Dependencies:** Plan approved.

**Implementation order from §12:**

1. `dialogue-orchestrator` agent — contract-first, references
   `dialogue-codex` skill behaviors.
2. `context-gatherer-code` and `context-gatherer-falsifier` production
   agents — adapted from cross-model with containment invariants.
3. Containment-guard extension for production `scope_envelope`.
4. `/dialogue` user skill — thin routing layer over the orchestrator.
5. First end-to-end verification per §8.

## In Progress

**Plan drafted, pending review.** No work in flight beyond awaiting
user feedback.

- Plan file at
  `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`
  (517 lines, untracked on `feature/t04-v1-scoping-plan`)
- Six material judgment calls made and documented
- Six pin-down asks from user explicitly addressed
- T8 boundary preserved in the verification path

## Open Questions

### 1. Plan length — accept, trim, or modularize?

**Context:** Hook flagged 517 lines as exceeding 500-line threshold.
I offered three options with a recommendation to review as-is first.

**Impact:** Trim pass is straightforward (~80–120 line savings, no
substance loss). Modularization via `/superspec:spec-writer` is more
ceremony but produces authority-tagged files that different
implementation sessions could pull separately.

### 2. Containment granularity — coarse repo-root vs anchor-derived?

**Context:** §5.1 chose coarse repo-root with rationale tied to
T4-CT-04 and the falsifier's broad-exploration value. Anchor-derived
was rejected because T4-BR-07 item 5 defers conceptual-query root
selection to benchmark contract work.

**Impact:** If anchor-derived is preferred, the plan would need to
add the anchor-derivation rule (or defer it as an open T7-style
dependency) and would carry an unresolved gap until that rule is
defined.

### 3. T8 14-item rubric coupling — borderline call

**Context:** §8.1 reuses the 14-item rubric as a verification test
tool. The rubric currently lives in `shakedown-b1/SKILL.md`, so the
production verification path references a shakedown file for the
rubric. Decision 5 trade-offs note this is borderline.

**Impact:** If the user wants a cleaner separation, the rubric should
be extracted to a standalone reference doc that both shakedown-b1 and
the production verification path can reference.

### 4. Commit before review, or after?

**Context:** Plan is uncommitted. Committing makes the file easier
for the user to read in their normal workflow (renders better in some
git tools, has a stable commit hash). Not committing keeps the file
as a working draft.

**Impact:** Low. User said "review this draft as-is" — they may want
to read it directly from the working tree. I'll let them decide on
commit timing.

## Risks

### 1. Plan over-commits to v1 implementation specifics that should be authoring-time decisions

**Impact:** §3.1 names a `/dialogue <objective>` invocation shape and
§6.1 names the per-turn loop steps in detail. If implementation
discovers a better shape, the plan needs revision, which adds churn.

**Mitigation:** §10 lists three specifically-deferred authoring-time
decisions (flag vocabulary, briefing assembly field set, recovery
semantics). The plan tries to draw the line at "what the user sees"
+ "what contracts are honored," not "exact implementation paths."

### 2. T4-CT-05 secrets dependency could surprise users in v1 deployment

**Impact:** v1 inherits the benchmark-corpus-safe assumption. If
someone deploys against a repo with credentials, the falsifier could
read them and they could surface in the synthesis.

**Mitigation:** §5.3 names this explicitly as a release-note
commitment. Risk 9.5 in the plan calls out the leak path. This is a
documented limitation, not a hidden defect.

### 3. The "deferral trigger" pattern requires discipline to honor

**Impact:** If a future session sees a deferred migration and treats
it as "definitely needed" without checking the trigger condition, v1
scope creeps.

**Mitigation:** Trigger column is explicit in §7.2. The handoff
captures the deferral-trigger pattern as a Learning so future sessions
recognize it.

## References

**Plan artifact (under review):**

- `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`

**Prior authority cited by the plan:**

- T1: `docs/plans/2026-04-02-t04-t1-structured-termination-contract.md`
- T2: `docs/plans/2026-04-02-t04-t2-synthetic-claim-and-closure-contract.md`
- T3: `docs/plans/2026-04-02-t04-t3-deterministic-referential-continuity.md`
- T4 modular spec: `docs/plans/t04-t4-scouting-position-and-evidence-provenance/`
- T4 containment: `docs/plans/t04-t4-scouting-position-and-evidence-provenance/containment.md`
- T5 mode strategy: `docs/plans/2026-04-02-t04-t5-mode-strategy.md`
- T7 executable slice: `docs/plans/2026-04-07-t7-executable-slice-definition.md`
- T8 minimum runnable shakedown packet: `docs/plans/2026-04-07-t8-minimum-runnable-shakedown-packet.md`
- Risk analysis: `docs/reviews/2026-04-01-t04-convergence-loop-risk-analysis.md`

**Ticket:**

- `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md`

**Codex-collaboration runtime + shakedown surface (read this session):**

- `packages/plugins/codex-collaboration/server/dialogue.py` (988 lines, not deeply read; interface understood from mcp_server.py)
- `packages/plugins/codex-collaboration/server/mcp_server.py` (270 lines)
- `packages/plugins/codex-collaboration/agents/shakedown-dialogue.md` (17 lines)
- `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md` (455 lines, summarized in prior handoff)
- `packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md` (211 lines, summarized in prior handoff)

**Cross-model semantic sources (read this session):**

- `packages/plugins/cross-model/agents/context-gatherer-code.md` (111 lines)
- `packages/plugins/cross-model/agents/context-gatherer-falsifier.md` (157 lines)

**Prior handoffs (chain):**

- This session loaded:
  `docs/handoffs/archive/2026-04-13_18-50_t04-gap-analysis-and-turn-semantics-closure.md`

**Branch:**

- `feature/t04-v1-scoping-plan` from `main` at `72c66714`

## Gotchas

### Plan file is uncommitted on a feature branch

**Symptom:** User opens a new session and the plan file exists on
disk but isn't visible in `git log --oneline`.

**Root cause:** I created the branch and wrote the file but didn't
commit, since the user said they'd review the draft as-is and the
implicit pattern was to defer commit until after review.

**Prevention:** When reviewing in next session, check `git status`
first — the plan file will appear as untracked on
`feature/t04-v1-scoping-plan`. Decide commit timing based on review
outcome.

### Cross-model `codex-dialogue.md` is "deliberate non-migration"

**Symptom:** A future session might propose adding `agent_local`
emission to cross-model `codex-dialogue.md` to "complete the
migration."

**Root cause:** T5 §6 explicitly bars this. The cross-model
orchestrator continues to emit only `server_assisted` and
`manual_legacy`. `agent_local` is owned by the new
codex-collaboration orchestrator (per this plan).

**Prevention:** When touching cross-model dialogue surfaces, check
T5 §6 first. The deliberate non-migration is a deliberate boundary
maintenance call, not an oversight.

### The 14-item rubric currently lives in shakedown-b1/SKILL.md

**Symptom:** The production verification path references a shakedown
skill file for the rubric, which slightly blurs the
shakedown/production boundary.

**Root cause:** The rubric was authored as part of the shakedown
work in T-20260410-01's closure. It's universal to dialogue-codex but
hosted in shakedown-b1.

**Prevention:** If the user flags this in review, the cleanest fix is
to extract the rubric to a standalone reference doc (e.g.,
`packages/plugins/codex-collaboration/references/dialogue-codex-inspection-rubric.md`)
that both shakedown-b1 and the production verification path
reference. Mechanical refactor.

### Handoff loaded by ID 237ea8dc but this session's ID is fbbd0301

**Symptom:** Future debugging may notice the prior handoff's
`session_id` (237ea8dc) does not match this handoff's `session_id`
(fbbd0301).

**Root cause:** Each Claude Code session gets a fresh session ID.
Chains are tracked via `resumed_from`, not session ID matching.

**Prevention:** Trust the `resumed_from` chain. Session IDs are
per-session; chain continuity comes from the resumed_from + state
file pattern.

## Conversation Highlights

**User's first pushback was three-citation style:**

User opened with "I agree mostly on direction, but not fully on
ordering or on what 'port' should mean" and provided three citations
in a single response: ticket "Semantic source only" framing, T5
mode strategy contradicting cross-model architecture, and risk
analysis arguing cross-model complexity should simplify. This is the
established pattern from prior sessions — multi-citation pushback
with specific evidence.

**User explicitly acknowledged the revision quality:**

"Your revision is materially stronger. I agree with the core
framing." This is positive feedback that the assembly framing landed
correctly. Worth noting that the user does provide explicit positive
signals when the revision lands, not just corrections.

**User's pressure points were named in advance:**

User listed six pin-down items the plan must address: invocation +
artifact guarantee, ownership table, minimum production loop,
containment model, migration table split, verification path.
Drafting against an explicit checklist made the plan more
defensible than an open brief would have.

**User chose review-as-is over in-conversation iteration:**

"Draft that plan. I'll review it against exactly those pressure
points once it has been drafted." This signals a deliberate review
pattern: produce the artifact, hand off, fresh review pass.

## User Preferences

**Multi-citation evidence-based pushback (confirmed again):**

When correcting framing, user provides specific file:line evidence
and rejects assertions without grounding. Two correction rounds this
session, each with 3+ citations to specific docs and line numbers.
Continues the pattern from prior sessions.

**Verb-precision matters:**

User specifically corrected "port" framing because it elides the
distinction between structural template and semantic reference.
Future proposals should name the relationship explicitly.

**Pin-down asks before drafting:**

User listed exactly what they wanted the plan to pin down before
asking me to draft. This let me draft against a checklist rather
than an open brief. Pattern worth replicating: when a user has a
clear target shape in mind, ask them to enumerate before drafting.

**Review-as-is over in-conversation iteration:**

User explicitly chose "review the draft as-is" rather than
in-conversation iteration. This is the second time this session
pattern has appeared (first time was in the prior handoff's
"three rounds of correction" pattern, but those were after a draft,
not in lieu of one).

**Acknowledges revision quality, not just corrections:**

"Your revision is materially stronger" was an explicit positive
signal. User does provide acknowledgement when work meets the bar,
not just corrections when it falls short. Worth saving as feedback
memory: positive signals are real signal, not just politeness.

**"Thin in surface area, not thin in truthfulness":**

This phrase from the user captures a specific architectural
preference: minimum viable surface OK, but skipping accepted
contracts is not. Worth remembering when proposing first-cuts of
anything in this codebase.
