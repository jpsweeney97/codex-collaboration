---
date: 2026-04-13
time: "22:09"
created_at: "2026-04-14T02:09:36Z"
session_id: 501301e6-9d1b-4594-a972-0af486ed0f74
resumed_from: docs/handoffs/archive/2026-04-13_19-45_t04-v1-scoping-plan-drafted-pending-review.md
project: claude-code-tool-dev
branch: feature/t04-v1-scoping-plan
commit: 72c66714
title: "T-04 v1 plan rewritten after three scrutiny rounds"
type: handoff
files:
  - docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md
---

# T-04 v1 Plan Rewritten After Three Scrutiny Rounds

## Goal

Convert the prior session's pending-review v1 scoping plan into a re-minimized
artifact that actually matches the containment transport the code provides.
The previous draft (518 lines, pending review) was structured around a
topology the runtime does not support — parallel gatherers under a single-
agent scope transport, read-only reuse of a shakedown-owned skill, and
production emission guarantees that conflated verification telemetry with
user-facing product surface.

**Trigger.** Resumed from a handoff that explicitly framed the next session
as "user review against six pressure points, review-as-is pattern." User
opened with four prefix-tagged findings (two P1, two P2), each grounded in
specific file:line citations. Every finding was verified in code; each one
indicated that the previous plan had asserted architecture the transport
did not support.

**Stakes.** This is the first concrete implementation-ready artifact for
the T-04 production surface. Every downstream implementation session pulls
its frame from this plan — ownership boundaries, run model, hook wiring,
emission contract, acceptance gates. Getting the plan wrong means the
first implementation session either builds something the transport can't
run, or silently defeats containment by missing a hook matcher.

**Success criteria for this session:**

1. Absorb initial findings and verify each against code — **achieved.**
2. Withstand adversarial scrutiny until the verdict moves from Reject
   through Major revision to Minor revision — **achieved across three
   rounds.**
3. Re-minimize the plan globally rather than patching locally —
   **achieved by dropping gatherers and the sibling skill, two material
   cuts.**
4. Rewrite the plan with every required change integrated — **achieved
   at 591 lines; user chose review-as-is per precedent.**
5. Hand off for final review — **this handoff.**

**Bigger picture.** The supersession chain is packet 3 of 6. Prior
session closed T-02 and T-20260410-01 (turn-semantics contract). This
session turns the pending v1 draft into a re-minimized plan that will
ship as the first production dialogue slice under T-04. Remaining T-04
closure (gatherers, briefing assembly, multi-agent scope transport,
shakedown-to-production unification) is now explicitly staged after v1
rather than bundled into it.

**Trigger (why now).** The previous session's plan was drafted in one
pass against the user's six pin-down asks but was not yet stress-tested
against the actual runtime. This session stress-tested it, discovered
three rounds of architectural drift, and converged on a plan that cites
file:line for every load-bearing claim.

## Session Narrative

**Phase 1 — Load and plan read (~10 min).**

Loaded the prior handoff. Per explicit user directive ("read the plan in
full before I share my thoughts"), read the 518-line plan in its
entirety. Noted the structural load-bearing sections: §4 (ownership)
and §7 (migration split). Flagged via insight that most downstream edits
land in those two tables.

**Phase 2 — User's initial findings: 4 P1/P2 items (~30 min).**

User presented scrutiny output with four prefix-tagged code-comments:

1. **P1 — Parallel gatherers exceed current containment transport.**
   Cited `containment.py` single-scope model and warned that parallel
   gatherer agents can't both be contained simultaneously.
2. **P1 — `codex.dialogue.start` is not the opening send.** Cited that
   `start` creates a handle only; first `reply` sends the objective.
   The plan's §6.1 step 1 was off by one on turn numbering.
3. **P2 — Read-only `dialogue-codex` reuse conflicts with the skill's
   own contract.** Cited the frontmatter language "Preloaded by
   shakedown-dialogue agent. Do NOT invoke this skill directly."
4. **P2 — §3.2 overclaims what read-only reuse provides.** Cited that
   `minimum_fallback` is excluded from emission, named the drift to
   `fallback`, flagged per-turn `ledger_summary` as not emitted.

I verified all four against code in parallel (`containment.py`,
`containment_guard.py`, `dialogue-codex/SKILL.md`, `mcp_server.py`).
Every finding confirmed. Flagged an additional drift in Finding 4 —
per-turn `ledger_summary` emission is nowhere in the current skill;
only terminal epilogue carries it.

Recommended: (1) sequential gatherers for v1, (2) production sibling
skill `dialogue-codex-production`. Mapped downstream plan edits in a
table. User did not respond to the recommendation — instead escalated
to full adversarial review.

**Phase 3 — User asked conceptual shakedown question (~15 min).**

Mid-flow, user asked "What is shakedown? What is its relationship to
the dialogue capability I want codex-collaboration to have?" I
explained in explanatory-mode depth: shakedown as internal verification
harness; three-ring architecture (per-turn contract inner, shakedown
middle, production outer); why the boundary invariant matters. This
was a conceptual grounding turn — no code changes.

**Phase 4 — Adversarial review #1: Reject (~30 min).**

User returned with formal adversarial review. Verdict: **Reject.** Five
critical/high findings:

1. Sequential gatherers solves `agent_id` race but not run-ownership.
   Current transport is run-centric, not agent-centric; transcripts and
   scope lifecycles are per-`run_id`.
2. Paired-diff test is not a real source-of-truth strategy for long
   prose contracts.
3. Still over-promoting verification telemetry into production
   contract.
4. Slice still too large for a believable v1.
5. Deferral of cross-model migrations rests on unnamed consumer path.

Root-cause diagnosis: "still blurs verification infrastructure and
production contract" + "still trying to preserve too much of the
original desired topology after the code disproved it."

Key quote: **"The plan is being repaired locally instead of being
re-minimized globally."**

I absorbed the reject honestly. Re-minimized around what the transport
supports: dropped gatherers entirely from v1 (one cut that cascades —
single agent, single run, no multi-agent transport question); shared
reference doc extracted now with explicit freeze during v1; two-artifact
split separating verification transcript (internal) from production
synthesis (user-facing). Named the consumer path explicitly.

**Phase 5 — Adversarial review #2: Major revision (~30 min).**

User returned. Verdict: **Major revision.** Four findings including one
Critical:

1. **Critical.** The new bootstrap is still impossible as written. I
   said `/dialogue` skill writes scope file with
   `agent_id = orchestrator`, but the parent cannot know `agent_id`
   before spawn. `SubagentStart` must remain the scope-file creator.
   User cited `containment_lifecycle.py:63` and T7 explicitly.
2. Ticket-scope honesty: v1 without gatherers ≠ T-04 closure. Need
   explicit acceptance split.
3. "Shared source-of-truth" is overstated if shakedown remains
   untouched. Either accept a minimal shakedown touch or call it
   production-local extraction.
4. Verification transcript overclaim: I said "exact current shape" but
   included `evidence_records[]` which the current skill does not emit.

This was the second time I wrote the desired architecture as if the
transport supported it. Verified against `containment_lifecycle.py`
in full: parent writes active-run + seed only; `SubagentStart` reads
`agent_id` from hook payload (`payload.get("agent_id")`, line 65) and
writes scope at line 108.

Corrected the run model to obey the seed-to-scope lifecycle literally.
Additional simplification: **dropped the production sibling skill.**
Once the shared reference doc owns turn semantics, the sibling was
redundant; orchestrator body can cite the reference directly and add
production-specific emission inline. One more component removed.

Accepted user's three judgments: gatherers out entirely (fold bounded
initial scouting into orchestrator body); shared reference extraction
now but production-local (do not touch shakedown); user-facing synthesis
in v1.

**Phase 6 — Adversarial review #3: Minor revision (~20 min).**

User returned. Verdict: **Minor revision.** One new High finding:

1. **Critical wiring gap.** `hooks.json:15, 26` matchers are
   `shakedown-dialogue` only. Without extending matchers to include
   `dialogue-orchestrator`, `SubagentStart` never fires for production,
   scope is never materialized, transcript is never captured. Silent
   containment defeat.

User decisions:
- **Namespace:** share the existing `shakedown/` namespace in v1.
- **Shakedown touch:** no touch in v1; reference stays production-local.

User verified both choices and said: "Proceed once those two decisions
and the hook-matcher dependency are written into the plan."

Verified the hook-matcher claim by reading `hooks.json` in full.
Confirmed `containment_guard.py:180` operator-message drift ("outside
the shakedown scope") — noted as naming drift for v1, post-v1 fix.

**Phase 7 — Rewrite (~20 min).**

Wrote the plan via `Write` tool — full replacement rather than
incremental edits, given the structural scope of the change. 591 lines,
13 sections. Every load-bearing claim carries a file:line or contract
citation. Integrated:

- v1 ≠ T-04 closure split (§1, §2.1, §2.2)
- Seed-to-scope lifecycle in §6.1 table (parent writes active-run +
  seed; SubagentStart writes scope)
- Hook matcher extension named critical in §7.1, with risk in §9.1,
  check in §8.3, and acceptance gate in §11
- Shared-namespace single-active-run constraint plainly in §5.2
- Two-artifact emission with verification transcript limited to current
  13-field shape in §3.3
- Production-local reference framing (not shared authority) in §4

**Phase 8 — Length surfacing (~5 min).**

Hook flagged 591 lines. Per memory rule ("Plan-length verdict is best
left to the user, not the model"), surfaced transparently with three
options and recommendation to review as-is. User replied with /save
request, implicitly accepting review-as-is (continues pattern from
prior session at 518 lines).

## Decisions

### Decision 1: Drop pre-dialogue gatherers from v1 entirely

**Choice:** v1 has no separate gatherer agents. No `context-gatherer-code`,
no `context-gatherer-falsifier`. Orchestrator performs a bounded inline
initial scouting phase before the first `codex.dialogue.reply`.

**Driver:** User's adversarial review #1 Finding 4: "The slice still
looks too large for a believable v1." User explicitly named the cut in
judgment: "keep them out of v1 as separate agents. If you want some
early-context value, fold a short initial scouting phase into the
orchestrator itself rather than reintroducing another contained
subagent."

**Alternatives considered:**

- **One gatherer (code only) in v1, falsifier deferred.** Rejected — still
  triggers multi-agent transport questions (two contained subagents per
  session) which the current transport does not support.
- **Both gatherers sequentially.** Rejected by the adversarial analysis
  — sequential gathering solves the `agent_id` race but not run
  ownership, transcript capture, or artifact grouping.

**Implication:** Cascades to five other simplifications:
- No multi-agent scope transport design needed (dropped from remaining
  scope).
- No briefing assembly layer in v1 (deferred to remaining T-04).
- No gatherer tag-grammar adaptation from cross-model.
- Finding 1 (run ownership) resolves because one contained agent only.
- Sibling skill becomes redundant (Decision 5).

**Trade-offs accepted:** A sparse user objective may produce a weaker
first Codex reply than it would with pre-gathered briefing. This is a
product-quality bet, not a correctness concern. T1–T6 semantics don't
require pre-briefing.

**Confidence:** High (E2) — user directly authored the judgment; the
cut cascades are evidenced in the corrected plan.

**Reversibility:** High — gatherers are additive post-v1 work. Adding
them requires multi-agent scope transport design (named deferral
trigger).

**Change trigger:** "First empirical finding that inline orchestrator
scouting demonstrably underperforms pre-briefed scouting on an
evaluation set of representative objectives, OR a consumer workflow
that requires the briefing-assembly surface."

### Decision 2: Drop the production sibling skill

**Choice:** No `dialogue-codex-production` skill. Orchestrator body
cites the shared reference doc directly for per-turn semantics and
adds production-only emission (final synthesis + inline scouting)
within its own agent body.

**Driver:** My own recognition during the scrutiny-review-2 response:
once the shared reference doc owns turn semantics, the sibling's only
job is a thin wrapper ("follow the reference + emit these production
fields"), which is three lines of orchestrator-body content. User's
missing item in review #1: "whether 'production sibling skill' is
actually necessary in v1, or whether the orchestrator plus a reference
doc already covers the need."

**Alternatives considered:**

- **Keep sibling skill as thin wrapper.** Rejected — redundant once
  the reference owns turn semantics; adds an authority surface reviewers
  must track; doesn't reduce code.
- **Merge sibling into shakedown skill (generalized).** Rejected in
  prior round — collapses shakedown/production boundary.

**Implication:** One fewer component in v1 (four new surfaces instead
of five). Orchestrator body is slightly longer but concentrates all
production-specific logic in one file.

**Trade-offs accepted:** If later we add a second production agent
(e.g., lightweight dialogue variant), the loop-behavior reuse pattern
via skill frontmatter is not available. That's a v1.x concern, not a
v1 blocker.

**Confidence:** High (E2) — the cut is a direct consequence of Decision
1 (gatherers dropped) and the shared-reference architecture.

**Reversibility:** High — extracting a sibling skill later is mechanical.

**Change trigger:** A second production agent needs the same turn-loop
behavior and skill-frontmatter reuse becomes the right vehicle.

### Decision 3: Shared namespace (`shakedown/` directory) for v1

**Choice:** v1 production artifacts live in `<data_dir>/shakedown/`
alongside shakedown artifacts. No parallel `dialogue/` directory, no
rename of the namespace.

**Driver:** User's adversarial review #3 judgment: "Namespace: share
the existing `shakedown/` namespace in v1." Rationale (user's own):
"share-vs-parallel is really a question of whether you want to
duplicate lifecycle plumbing. You should not."

**Alternatives considered:**

- **Parallel namespace** (`<data_dir>/dialogue/`). Rejected — doubles
  transport-adjacent code, increases maintenance surface, introduces
  per-namespace lifecycle events.
- **Rename `shakedown/` to neutral now.** Rejected — touches shakedown
  invariants and adds scope.

**Implication:** **One active contained run per session.** Because the
transport is keyed by a single `active-run-<session_id>` pointer
(`containment.py:36`), a session can have at most one active contained
run. Concurrent shakedown + production in same session is not
supported. Both entry points implement a live-run check with
operator-visible failure message.

**Trade-offs accepted:**
- Naming drift: `shakedown/` directory now hosts production artifacts.
- Naming drift in `containment_guard.py:180` operator message ("outside
  the shakedown scope"). v1 release note documents; post-v1 fixes.
- Dual-run deferred to post-v1.

**Confidence:** High (E2) — user-authored decision, rationale validated.

**Reversibility:** Medium — rename is a mechanical post-v1 cleanup,
but every script referencing `_SHAKEDOWN_DIRNAME` changes.

**Change trigger:** Dual-run becomes a product need, OR operator-naming
drift becomes a support issue.

### Decision 4: Shakedown stays byte-for-byte untouched in v1

**Choice:** `dialogue-codex/SKILL.md`, `shakedown-b1/SKILL.md`, and
`shakedown-dialogue.md` are not edited in v1. Not even a one-line
description edit to point at the extracted reference.

**Driver:** User's adversarial review #3 judgment: "Shakedown touch: no
touch in v1; keep the extracted reference production-local." Rationale
(user's own): "a one-line `dialogue-codex` touch buys little and
creates avoidable risk."

**Alternatives considered:**

- **One-line description edit** pointing at the extracted reference.
  Rejected — creates avoidable risk to the 566-test shakedown suite
  without material benefit during v1.

**Implication:** The extracted reference doc is **production-local
authority** in v1, not shared authority. Shakedown continues to rely on
its own full skill body. Shared-authority unification is remaining-T-04
work.

**Trade-offs accepted:** The extracted reference and `dialogue-codex`
body are redundant copies during v1. Divergence is possible in
principle if either is edited. Mitigation: v1 commits to zero
behavioral edits to per-turn semantics in either surface. Named
remediation: remaining-T-04 factors `dialogue-codex` to an adapter.

**Confidence:** High (E2) — user-authored decision.

**Reversibility:** High — the factoring is a mechanical post-v1 edit.

**Change trigger:** Behavioral edits to turn semantics become required
during v1 (very unlikely given the contract is accepted).

### Decision 5: Hook matcher extension named as critical v1 change

**Choice:** Plan §7.1 explicitly names the `hooks.json` SubagentStart /
SubagentStop matcher extension as a **critical** required v1 change.
§9.1 captures the silent-defeat failure mode as a named risk. §8.3
includes an explicit verification check that the hooks fire for
`dialogue-orchestrator`. §11 acceptance criteria gates on the matcher
being in place.

**Driver:** User's adversarial review #3 Finding 1: "If the plan does
not explicitly add `dialogue-orchestrator` to those lifecycle matchers,
the seed never becomes scope, containment never activates, and
transcript capture never happens." Verified at `hooks.json:15, 26`.

**Alternatives considered:**

- **Leave implicit** — "reuse existing lifecycle" framing was in the
  previous draft. Rejected — user explicitly flagged this as silent
  containment defeat risk.

**Implication:** Implementation session cannot miss this without
breaking everything. The plan has four separate mentions of the hook
matcher extension (§7.1, §8.3, §9.1, §11) to prevent oversight.

**Trade-offs accepted:** None material.

**Confidence:** High (E3) — user cited, I verified, plan gates on it.

**Reversibility:** Trivial — it's a hooks.json edit.

**Change trigger:** Not applicable.

### Decision 6: Two-artifact emission split

**Choice:** v1 emits two separate artifacts at termination:
- **Production synthesis** (user-facing, structured JSON) — carries
  only product-surface fields: objective, mode, termination_code,
  turn_count/budget, final_claims with final_status and citations,
  synthesis_citations, final_synthesis, ledger_summary.
- **Verification transcript** (internal, JSONL) — the exact 13-field
  state-block shape the current `dialogue-codex` skill emits, captured
  via the existing SubagentStop lifecycle. No new emission fields.

**Driver:** User's adversarial review #1 Finding 3: "over-promoting
internal verification telemetry into the production contract."
Reinforced by review #2 Finding 4: the verification transcript must
not claim emission of fields (e.g., `evidence_records[]`) that the
current skill does not emit.

**Alternatives considered:**

- **Single merged artifact** with per-turn telemetry surfaced to user.
  Rejected — freezes internal mechanism into external contract; makes
  later schema cleanup harder.
- **Add new emission fields for v1** (e.g., `evidence_records[]`).
  Rejected — touches shakedown-owned skill semantics; violates Decision
  4 invariant.

**Implication:**
- `minimum_fallback` accounting, per-turn `effective_delta`, raw
  per-scout evidence records, `scope_breach_count` live in the
  verification transcript only, not the user-facing artifact.
- Risk-J structured per-scout evidence is reconstructable from emitted
  fields (turn + target_claim + scope_root + queries + citations +
  disposition) during rubric inspection; not a separately emitted field.

**Trade-offs accepted:** Two artifact types to manage. Slightly more
complex than single artifact, but each has a single audience and
single purpose.

**Confidence:** High (E2).

**Reversibility:** High — merging later is additive.

**Change trigger:** A single consumer demands both product and
verification data in one artifact (very unlikely — their audiences
differ).

### Decision 7: v1 is first production slice, not T-04 closure

**Choice:** Plan §1 frames v1 as "first production slice under T-04"
not closure. §2.1 names v1 acceptance. §2.2 enumerates remaining T-04
acceptance (gatherers, briefing assembly, multi-agent transport,
shakedown unification).

**Driver:** User's adversarial review #2 Finding 2: "If v1 drops
gatherers and briefing assembly, it no longer matches the supersession
ticket's named scope or acceptance bar." The ticket at
`docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md`
names gatherers and deterministic briefing assembly in closure.

**Alternatives considered:**

- **Silently ship v1 as "closure"** with gatherers dropped. Rejected —
  scope retreat masquerading as thin-slicing; the pattern the user
  explicitly called out.

**Implication:** Plan structure carries two acceptance gates: v1
acceptance (this slice) and remaining T-04 acceptance (explicitly not
v1). Downstream implementation sessions can verify against v1
acceptance without inferring closure.

**Trade-offs accepted:** T-04 ticket stays open after v1 ships.
Documented expectation; not a silent scope gap.

**Confidence:** High (E2).

**Reversibility:** High — reframing is prose-level.

**Change trigger:** Ticket author revises closure bar to exclude
gatherers (not expected).

## Changes

### `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`

**What changed:** Full rewrite via `Write` (not incremental edits given
structural scope). 591 lines, 13 sections. Every load-bearing claim now
carries a file:line or contract citation.

**Structural changes from prior draft (518 → 591 lines):**

- **New §2 acceptance split** (~40 lines): v1 acceptance vs remaining
  T-04 acceptance enumerated separately.
- **New §6.1 run-model table** (~15 lines): explicit seed-to-scope
  lifecycle with each step keyed to code (parent / SubagentStart /
  orchestrator / SubagentStop / skill).
- **New §9.1 hook-matcher risk + §8.3 hook-firing check** (~15 lines):
  silent-defeat failure mode named with explicit mitigation and
  verification.
- **New §5.2 shared-namespace constraint + §9.4 risk + §9.6 naming-drift
  risk** (~30 lines): one-active-run-per-session constraint and
  operator-visible drift both named.
- **Expanded §11 acceptance criteria** (~10 lines): gates on every new
  required item.

**Structural removals from prior draft:**

- Gatherer agents (code + falsifier) — gone from ownership and
  migration tables.
- Briefing assembly — gone.
- Production sibling skill — gone (dropped in session phase 6).
- Multi-agent scope transport extension — gone (deferred to remaining
  T-04).
- Custom `evidence_records[]` emission — gone (transcript shape limited
  to current emission).
- `fallback` naming — corrected to `minimum_fallback` throughout.

**Status:** Uncommitted on `feature/t04-v1-scoping-plan`. Pending final
user review.

### Branch state

No new commits this session. The plan file remains untracked on
`feature/t04-v1-scoping-plan` (from `main@72c66714`). User will likely
review the rewrite directly from the working tree; commit timing
depends on review outcome.

## Codebase Knowledge

### Containment transport is run-centric, not agent-centric

The transport is a three-file lifecycle keyed by `run_id`:

| File | Path format | Written by | Read by | Removed by |
|---|---|---|---|---|
| Active-run pointer | `shakedown/active-run-<session_id>` | Parent (skill) | Guard + lifecycle hooks | Overwritten on next invocation or 24h age sweep |
| Seed | `shakedown/seed-<run_id>.json` | Parent (skill) | SubagentStart hook | SubagentStart (line 110) after consuming |
| Scope | `shakedown/scope-<run_id>.json` | SubagentStart hook (line 108) | Guard | SubagentStop (line 158) |
| Transcript | `shakedown/transcript-<run_id>.jsonl` | SubagentStop hook (line 143-145) | Verification rubric | Never (manual) |

Key code locations:

- `packages/plugins/codex-collaboration/server/containment.py:14` —
  `_SHAKEDOWN_DIRNAME = "shakedown"` hardcoded directory name.
- `packages/plugins/codex-collaboration/server/containment.py:36` —
  `active_run_path(data_dir, session_id)` keys pointer by session.
- `packages/plugins/codex-collaboration/server/containment.py:42-63` —
  seed, scope, transcript paths all keyed by `run_id`.
- `packages/plugins/codex-collaboration/server/containment.py:192` —
  `build_scope_from_seed(seed, agent_id)` — scope is per-agent by
  construction.
- `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py:63-112` —
  `_handle_subagent_start`: reads pointer → reads seed → builds scope
  from seed + hook-provided `agent_id` → writes scope → unlinks seed.
- `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py:115-160` —
  `_handle_subagent_stop`: reads pointer → reads scope → checks
  `scope.agent_id == payload.agent_id` → copies transcript → unlinks
  scope. Pointer is NOT cleared.
- `packages/plugins/codex-collaboration/scripts/containment_guard.py:71-114` —
  reads active run + scope; at line 113, passthroughs tool call if
  `scope.agent_id != agent_id` (the single-agent enforcement point).

**Implication for v1:** Single-agent-per-run is enforced at the guard
level, not just at the scope file. Multiple contained subagents within
one run would require either (a) rewriting the scope between phases,
which the current lifecycle doesn't do, or (b) multiple run_ids with
aggregation semantics the current lifecycle doesn't provide. v1 avoids
both by using one contained agent (orchestrator) per run.

### Hook matchers are the activation contract

`packages/plugins/codex-collaboration/hooks/hooks.json`:

- Line 15 — SubagentStart matcher: `"shakedown-dialogue"`.
- Line 26 — SubagentStop matcher: `"shakedown-dialogue"`.

These matchers control whether `containment_lifecycle.py` runs for a
given subagent spawn/stop. Without extending these matchers to include
`dialogue-orchestrator`, v1's production agent spawns without scope
materialization — tool calls pass through uncontained, transcript is
never captured.

The matcher extension is a single-file, two-line edit. The plan names
it as a critical v1 change in §7.1 and gates acceptance on it in §11.

### dialogue-codex emits exactly 13 state-block fields

`packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md:252-268`:

| Field | Type | Notes |
|---|---|---|
| `turn` | int | First emitted block is `turn: 2` |
| `scouted` | bool | — |
| `target_claim_id` | int or null | — |
| `target_claim` | string or null | — |
| `scope_root` | string or null | — |
| `queries` | list | `[{type, tool, target}, …]` |
| `disposition` | string or null | Enum |
| `citations` | list | `[{path, lines, snippet}, …]` |
| `claims` | list | Ledger entries — **excludes** `minimum_fallback` per line 116 |
| `counters` | object | 8 fields |
| `effective_delta` | object | 8 fields, per-turn |
| `terminal` | bool | — |
| `epilogue` | object or null | Required when `terminal: true`; contains `ledger_summary`, `converged`, `effective_delta_overall` |

**No `evidence_records[]` flat array.** The Risk-J-style per-scout
record is reconstructable from `turn + target_claim + scope_root +
queries + citations + disposition` during inspection but is not a
separately emitted field.

`minimum_fallback` rules at lines 111-117:
- Created only when turn extraction yields zero distinct raw claims.
- Name is literally `minimum_fallback`, not `fallback` (the prior draft
  had naming drift).
- Excluded from counter computation for `new_claims`, `revised`,
  `conceded`.
- Excluded from the emitted `claims` array.
- Produces `quality: SHALLOW, effective_delta: STATIC` on all-fallback
  turns.

`ledger_summary` appears only in the terminal epilogue (SKILL.md:336-353),
never in a per-turn state block.

### MCP server dialogue tool semantics

`packages/plugins/codex-collaboration/server/mcp_server.py:45-82`:

- `codex.dialogue.start` takes `repo_root` (required), `profile`
  (optional). Returns a collaboration handle. **Does not send an
  objective.** No turn emission.
- `codex.dialogue.reply` takes `collaboration_id` (required),
  `objective` (required), `explicit_paths` (optional). This is the
  objective-sending tool. First call to `reply` is turn 1.
- `codex.dialogue.read` takes `collaboration_id` (required). State
  inspection only.

**Implication:** The opening send to Codex is `reply`, not `start`.
Turn numbering in the per-turn state contract (`turn: 2` for first
emitted block) assumes `start` creates the handle and the first `reply`
is turn 1 (no emission), and the second `reply` (or equivalently the
first post-reply verification) is turn 2 (first emitted block).

### Operator-message naming drift

`packages/plugins/codex-collaboration/scripts/containment_guard.py:179-182`:

```
return _deny(
    "Requested Read path is outside the shakedown scope. "
    f"Reissue under one of: {_format_scope_directories(list(scope_directories))}"
)
```

For production denials this operator-visible message still references
"shakedown scope." Not a behavioral defect — the containment enforcement
is correct — but a real operator-facing naming drift that v1 inherits
under the shared-namespace decision. Plan names it in §7.2 as post-v1
cleanup and in §9.6 as a named v1 risk.

## Context

### Branch and repository state

- **Branch:** `feature/t04-v1-scoping-plan` (created from `main` at
  `72c66714` in prior session).
- **Working tree:** one untracked file —
  `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`.
- **Commits on branch:** none; plan is uncommitted.
- **Remote:** branch not pushed.

### Mental model for this session

**v1 = re-minimization around the transport, not around the desired
topology.** This is the central frame. Three scrutiny rounds repeatedly
called out the same failure mode: writing architecture the current code
disproves, then patching locally when called out. Each re-minimization
cut another axis until the slice matched the transport literally:

- Round 1 → dropped multi-agent parallelism.
- Round 2 → dropped gatherers entirely; dropped sibling skill; fixed
  run model to obey seed-to-scope.
- Round 3 → named hook matcher extension explicitly; named shared
  namespace + naming drift; split acceptance.

**The boundary invariants are rigid because the tests are rigid.** The
566-test shakedown suite is written against shakedown semantics.
Changing shakedown artifacts risks failing tests. v1 obeys this by
never touching shakedown files (Decision 4).

**Plan length is not a shape failure by itself.** The prior session's
plan at 518 lines was accepted review-as-is; this session's plan at 591
is also being reviewed as-is. The length maps to content density, which
maps to the number of invariants the plan pins down. Trimming would
lose substance.

### What the user said about the draft (this session)

User never directly commented on the rewritten plan body — the session
ended after the length surfacing. User committed to review-as-is via
the /save request pattern: "save a handoff. I will review the plan
as-is and then share my feedback with you in the next session." This
is the third appearance of this pattern in the broader work:

1. Prior session (518 lines, pending review).
2. This session's rewrite (591 lines, pending review).
3. The pattern itself is stable: produce the artifact, hand off, fresh
   review pass.

### Why three scrutiny rounds

Each round caught a distinct failure mode:

- **Round 1 (Reject):** blurred verification/product; preserved desired
  topology after transport disproved it.
- **Round 2 (Major revision):** impossible bootstrap (agent_id); ticket-
  scope honesty; shared-authority overclaim; transcript-shape overclaim.
- **Round 3 (Minor revision):** silent hook-matcher gap; namespace
  question needed naming; shakedown-touch question needed answering.

Each round's findings were sharper and smaller than the previous. The
escalation pattern (Reject → Major revision → Minor revision) is a
reliable indicator that the plan is converging.

## Learnings

### "Writing the desired architecture as if the transport already supports it"

**Mechanism.** I repeatedly asserted architecture (parallel gatherers,
read-only skill reuse, parent-written scope, merged verification/
product emission) that the code did not support. Each assertion was
seductive because it matched cross-model's pattern or the previous
session's proposed shape. Each was caught only because the user
demanded file:line evidence.

**Evidence.** Verbatim from user in review #2: "you are still
occasionally writing the desired architecture as if the current
transport already supports it." Verbatim from review #1: "The plan is
being repaired locally instead of being re-minimized globally."

**Implication.** Before any architectural claim about how a subsystem
works, verify against current code with file:line evidence. Pattern
match to the codebase is not enough — the pattern must be implemented
at the claimed location. When the user calls out a mismatch, don't
patch the claim; re-minimize.

### Authority inflation

**Mechanism.** Calling things "shared authority" or "exact current
shape" before the consumers/emitters actually honor that. The prior
draft called `dialogue-codex` "shared" when it was production-local;
called the verification transcript "exact current shape" while
proposing additional fields.

**Evidence.** User in review #2 Finding 3: "A doc is not truly shared
authority if one consumer cites it and the other remains a full copied
contract with no obligation to defer to it. That is not source-of-truth;
it is a hopeful parallel document."

**Implication.** When framing an artifact's authority, name the exact
consumers that obey it. If only one consumer cites it, call it
consumer-local. When claiming to match "current shape," enumerate the
fields literally and diff against source — don't rely on a mental
summary.

### Cascading cuts beat local mitigations

**Mechanism.** Dropping pre-dialogue gatherers from v1 was one cut that
resolved five issues at once: multi-agent transport question (no
longer relevant), run ownership (single agent only), briefing-format
question (no briefing), sibling skill necessity (redundant), and slice-
size concern (smaller by one major component).

**Evidence.** Adversarial review #1 Finding 4: "cut another axis now,
or explicitly admit this is more than one packet." Single cut made
multiple findings evaporate in the next round.

**Implication.** When adversarial review lists 4-5 findings, look for
a structural cut that collapses them simultaneously. Local mitigations
accumulate; cuts simplify.

### Hook matchers are a silent-failure risk

**Mechanism.** Claude Code's hook matchers activate extensions per
agent name. If a new agent is added without updating matchers, the
hooks don't fire. The agent appears to work; its tool calls succeed;
but enforcement (containment, telemetry, logging) silently doesn't
run.

**Evidence.** `hooks.json:15, 26` matchers were `shakedown-dialogue`
only; user's review #3 Finding 1 identified that without extending
these, "the seed never becomes scope, containment never activates,
and transcript capture never happens."

**Implication.** Any plan that adds a new subagent to a plugin with
lifecycle hooks must explicitly name hook-matcher extension as a
required change. Leaving it implied as "reuse existing lifecycle" is a
silent-defeat recipe. The plan now cites this explicitly in four
sections to prevent oversight.

### Plan-length verdict is best left to the user

**Mechanism.** The PostToolUse hook flags plans over 500 lines. The
temptation is to silently compress. But compression loses substance
that the scrutiny rounds just added.

**Evidence.** Prior session, plan at 518 lines: I surfaced options;
user chose review-as-is. This session, plan at 591 lines: I surfaced
options again; user responded with /save (implicit review-as-is).
Memory already captures this pattern.

**Implication.** When a soft constraint fires, surface options; let
the user pick. Don't pre-emptively compress substance that was
hard-won through scrutiny.

## Next Steps

### 1. User review of the rewritten plan (next session)

**Dependencies:** None — plan file is on disk at
`docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`;
branch `feature/t04-v1-scoping-plan` is ready.

**What to read:**

1. The rewritten plan itself (591 lines).
2. This handoff for session context.
3. Optional: the previous handoff
   (`archive/2026-04-13_19-45_t04-v1-scoping-plan-drafted-pending-review.md`)
   for the prior draft's context.

**Approach suggestion.** The plan absorbs three scrutiny rounds. The
user's review should verify:

1. Acceptance split (§2.1 vs §2.2) is defensible — v1 ≠ T-04 closure.
2. Ownership table (§4) names four new surfaces, no more (no sibling,
   no gatherers).
3. Run model (§6.1) obeys seed-to-scope lifecycle — parent writes
   active-run + seed only; SubagentStart writes scope.
4. Hook matcher extension (§7.1) is named critical and gated in §11.
5. Shared-namespace constraint (§5.2) is plain — one active run per
   session.
6. Verification transcript (§3.3) is exactly the current 13-field shape
   — no additions.
7. Deferral triggers (§7.2) name concrete consumers.

### 2. Address review feedback

**Dependencies:** User feedback from step 1.

**Likely shapes of feedback:**

- **Approval** — proceed to commit + implementation.
- **Trim request** — §2.3 out-of-scope table overlaps §2.2 (a few rows
  could collapse). Plus some prose compressibility in §6.2 and §11.
  Realistic savings: 30–60 lines.
- **Modularization request** — `/superspec:spec-writer` split into
  authority-tagged files (run-model.md, containment.md, verification.md,
  migration.md, etc.). More ceremony; useful only if implementation
  sessions will pull different authorities separately.
- **Substance change** — re-decide one of Decisions 1-7. Least likely
  candidates: Decisions 3 (namespace) and 4 (shakedown touch), both
  user-authored. Most likely candidates: Decision 1 (drop gatherers) if
  user decides one gatherer (code) should be retained.

### 3. Commit and merge plan

**Dependencies:** Review feedback addressed.

**Note:** Branch `feature/t04-v1-scoping-plan` is ready to commit.
After commit, decide PR vs direct merge to main. Given this is a plan
doc (not code), direct merge is reasonable per the project's
established pattern for design plans.

### 4. Begin implementation per §12

**Dependencies:** Plan approved.

**Implementation order from §12:**

1. Author the production-local turn-semantics reference doc by extracting
   per-turn contract content from the current `dialogue-codex` skill.
2. Author `dialogue-orchestrator` agent body citing the reference doc,
   with inline initial scouting phase and production synthesis emission.
3. Author `/dialogue` user skill: invocation parsing, parent-owned
   active-run + seed write, shared-namespace single-run check,
   orchestrator dispatch, synthesis surfacing.
4. Extend `hooks.json` `SubagentStart` and `SubagentStop` matchers to
   include `dialogue-orchestrator`. Run existing lifecycle tests to
   confirm they still pass.
5. First end-to-end verification per §8.2 on a representative objective.
6. 14-item rubric inspection against the resulting verification
   transcript.
7. Confirm 566-test shakedown suite still passes unchanged.

## In Progress

**Plan rewritten, pending final review.** No work in flight beyond
awaiting user feedback.

- **Approach:** review-as-is (user-chosen). Plan file at
  `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`
  (591 lines, untracked on `feature/t04-v1-scoping-plan`).
- **State:** complete; every scrutiny round's required changes are
  integrated; every load-bearing claim carries a citation.
- **Working:** plan is syntactically well-formed; passes PostToolUse
  hook except for the line-count warning.
- **Not working:** nothing broken; length exceeds 500-line soft
  threshold (user accepts review-as-is per precedent).
- **Open question:** final user verdict on the rewrite — approve,
  trim, modularize, or substance-change.
- **Next action:** user reads the plan in the next session and shares
  feedback.

## Open Questions

### 1. Final approval vs substance-change

**Context:** Seven material decisions were made this session, four
user-authored (Decisions 3, 4, 7, the inline-scouting judgment) and
three mine-then-validated (Decisions 1, 2, 5, 6). User reviews the
rewrite fresh; any of the decisions could be reopened.

**Impact:** If approved, proceed to commit + implementation. If
substance-change requested on a user-authored decision, likely a small
correction. If substance-change on a mine-then-validated decision,
likely a larger re-think.

### 2. Plan length verdict

**Context:** 591 lines, above the 500-line soft threshold. Three
options surfaced: review as-is, trim ~30-60 lines, modularize via
spec-writer.

**Impact:** User has implicitly chosen review-as-is via the /save
pattern; explicit confirmation in next session. If user chooses trim
after review, I've pre-identified target sections (§2.3 redundancy
with §2.2; §6.2 prose; §11 acceptance rehashing §4/§5). If user chooses
modularize, more ceremony but produces authority-tagged files.

### 3. Commit timing — before or after review?

**Context:** Plan is uncommitted. Previous session left it uncommitted
for the same reason. Committing would make the plan easier to
reference via git tools but requires a decision on direct-commit vs
PR.

**Impact:** Low — user said "review this draft as-is" both sessions.
Commit after review outcome is the established pattern.

## Risks

### 1. Plan still over-commits to implementation specifics

**Impact:** Plan names specific paths (`skills/dialogue/SKILL.md`),
specific field names (`final_claims`, `synthesis_citations`), and a
specific inline-scouting budget (target N=3). Implementation may
discover these need adjustment.

**Mitigation:** §10 open questions carries three authoring-time
decisions (flag vocabulary, scouting budget, serialization format).
Additional small adjustments during implementation are expected; the
plan's load-bearing claims (run model, hook matcher, acceptance split)
are intentionally less flexible.

### 2. T4-CT-05 secrets dependency remains inherited

**Impact:** v1 inherits the benchmark-corpus-safe assumption. If
deployed against a repo with credentials, falsifier-equivalent
exploration via orchestrator's inline scouting could surface secrets
into the synthesis.

**Mitigation:** §5.3 names this explicitly as a v1 release-note
commitment. Risk 9.5 in the plan names the leak path. Documented
limitation, not hidden defect.

### 3. Hook-matcher extension miss during implementation

**Impact:** If the implementation session forgets to extend the
matchers in `hooks.json`, containment silently doesn't activate for
production. Symptom: `/dialogue` appears to work but transcript file
is never created and `Read`/`Grep`/`Glob` calls aren't guarded.

**Mitigation:** Plan mentions the matcher extension in four separate
places (§7.1, §8.3, §9.1, §11). Acceptance gates on it. Handoff
captures it as Learning. The redundancy is intentional.

### 4. Reference doc and `dialogue-codex` silently diverge

**Impact:** If v1 discipline breaks and either surface is edited
without mirroring, shakedown and production run against different
semantics.

**Mitigation:** §9.3 names zero-behavioral-edits-during-v1 as the
discipline. Remaining-T-04 work factors `dialogue-codex` to adapter,
eliminating the risk structurally.

### 5. Naming drift across namespace sharing

**Impact:** `shakedown/` directory hosts production artifacts;
`containment_guard.py:180` says "shakedown scope" in production
denials. Could confuse operators debugging production failures.

**Mitigation:** §7.2 names both as post-v1 cleanup. §9.6 captures as
named risk. Release note documents.

## References

**Plan artifact (under final review):**

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

**Ticket (supersession):**

- `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md`

**Closed ticket (turn semantics):**

- `docs/tickets/2026-04-10-dialogue-codex-turn-semantics-clarification.md`

**Containment lifecycle surface (read this session):**

- `packages/plugins/codex-collaboration/server/containment.py` (540 lines;
  functions used: `active_run_path`, `seed_file_path`, `scope_file_path`,
  `transcript_path`, `read_active_run_id`, `build_scope_from_seed`,
  `is_path_within_scope`, `select_scope_root`)
- `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py` (211 lines)
- `packages/plugins/codex-collaboration/scripts/containment_guard.py` (read lines 1-200 — the payload evaluation and Read enforcement paths)
- `packages/plugins/codex-collaboration/hooks/hooks.json` (56 lines)

**Runtime surface (read this session):**

- `packages/plugins/codex-collaboration/server/mcp_server.py` (lines 1-120 read; tool definitions for `codex.dialogue.start/reply/read` at 45-82)

**Skill contracts (read this session):**

- `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md` (456 lines read in full — emission shape at 252-268, minimum_fallback rules at 111-117, terminal epilogue at 336-353)

**Prior handoffs (chain):**

- This session loaded:
  `docs/handoffs/archive/2026-04-13_19-45_t04-v1-scoping-plan-drafted-pending-review.md`
- Prior (pre-previous):
  `docs/handoffs/archive/2026-04-13_18-50_t04-gap-analysis-and-turn-semantics-closure.md`

**Branch:**

- `feature/t04-v1-scoping-plan` from `main@72c66714`

## Gotchas

### Plan file is uncommitted on a feature branch

**Symptom:** User opens the next session; `git log --oneline` shows no
commits on `feature/t04-v1-scoping-plan`.

**Root cause:** I rewrote the plan file but didn't commit, since the
user chose review-as-is and the implicit pattern is to defer commit
until after review outcome.

**Prevention:** Check `git status` first in the next session — the
plan appears as untracked on `feature/t04-v1-scoping-plan`. Decide
commit timing based on review outcome.

### Hook-matcher extension is easy to miss

**Symptom:** Implementation session adds the `/dialogue` skill and
`dialogue-orchestrator` agent, runs `/dialogue test` and sees the
skill respond. But no `transcript-<run_id>.jsonl` is created; guard
doesn't fire; production tool calls succeed regardless of scope.

**Root cause:** `hooks.json` matchers at lines 15 and 26 are
`"shakedown-dialogue"` only. Without extending to
`"shakedown-dialogue|dialogue-orchestrator"`, the lifecycle hooks
never fire for production.

**Prevention:** Plan §7.1 names this as critical. Acceptance §11
gates on it. §8.3 includes an explicit check. This handoff captures
it as a first-class risk (Risk 3). Implementation session must verify
hook firing before declaring success.

### Active-run pointer lingers after a run completes

**Symptom:** After a successful `/dialogue` run, a stale
`active-run-<session_id>` file remains in `shakedown/`. A future
session sees it but subsequent invocations work fine.

**Root cause:** `containment_lifecycle.py:115-160` unlinks only the
scope file on SubagentStop. The active-run pointer is not cleared;
it's overwritten atomically on the next invocation or pruned by the
24h age sweep.

**Prevention:** Not a bug. The plan documents this in §6.1 step 5. The
next invocation's atomic replace handles it. Operators confused by
stale pointers can manually prune; plan notes this in §7.2 post-v1
cleanup list (implicitly).

### Shared namespace means concurrent shakedown + production can't coexist

**Symptom:** User runs `/shakedown-b1` (or equivalent), then in the
same session tries `/dialogue <objective>`. Second invocation fails
with "active run in progress" message.

**Root cause:** Transport is keyed by single `active-run-<session_id>`
pointer. Single-agent constraint enforced at guard level. Shakedown
and production share the namespace in v1 (Decision 3).

**Prevention:** Plan §5.2 and §9.4 name this explicitly. Both entry
points (`/dialogue` skill and `shakedown-b1` skill) must implement a
live-run check with operator-visible message. §11 acceptance gates on
the check existing.

### `dialogue-codex` and the extracted reference doc will be redundant

**Symptom:** Two files with identical normative turn-semantics
content. Future editor sees the reference doc and doesn't realize
`dialogue-codex` has the same content.

**Root cause:** v1 deliberately extracts the reference without
factoring shakedown (Decision 4). The redundancy is intentional and
frozen during v1.

**Prevention:** Plan §9.3 names zero-behavioral-edits as v1 discipline.
Remaining-T-04 closure factors `dialogue-codex` to an adapter,
eliminating the redundancy. Until then, editors must mirror changes
across both files (not expected during v1).

### Handoff session ID 501301e6 differs from last session's fbbd0301

**Symptom:** Future debugging notices session ID differs from the
prior handoff's.

**Root cause:** Each Claude Code session gets a fresh session ID.
Chains are tracked via `resumed_from` frontmatter, not session ID
equality.

**Prevention:** Trust the `resumed_from` chain. This handoff points to
`docs/handoffs/archive/2026-04-13_19-45_*` which was consumed via the
/load skill at session start.

## Conversation Highlights

### User's adversarial-review style is formalized

All three rounds used the same structured output:
- Premise Check
- Critical Failures (numbered with severity tags)
- High-Risk Assumptions
- Real-World Breakpoints And Edge Cases
- Hidden Dependencies Or Bottlenecks
- Adversarial Perspectives Applied
- Patterns And Root Causes
- Required Changes Before This Is Credible
- Verdict

Verdicts escalated Reject → Major revision → Minor revision → (implicit
proceed). This is the reliable signal that a plan is converging.

### User's root-cause diagnoses were sharper than the individual findings

Review #1 root-cause: *"you are still occasionally writing the desired
architecture as if the current transport already supports it. The other
remaining pattern is authority inflation: calling extracted docs 'shared
truth' and transcript fields 'current shape' before the consumers or
emitters actually honor that."*

Review #2 root-cause: *"The main shape is now plausible; the remaining
problems are sharper and smaller, but one is still a hard impossibility
(`agent_id` bootstrap) and two are still contract-truthfulness issues."*

Review #3 root-cause: *"The earlier systemic problems are mostly
resolved. The remaining issues are packaging honesty and transport
wiring, not architectural incoherence. That is a major improvement."*

The diagnoses named patterns, not just bugs. Future sessions should
expect this format and read for patterns in the root-cause paragraph
first.

### "Re-minimize globally, not patched locally"

Verbatim from review #1: *"The plan is being repaired locally instead
of being re-minimized globally."*

This is the most actionable critique of the session. It captures the
temptation to keep a desired topology and patch around its failure
points, versus cutting the topology and re-drawing from the transport's
constraints. Every subsequent round asked whether the latest proposal
was a patch or a re-minimization.

### User provides explicit positive acknowledgement when work lands

Review #3: *"This is now credible enough to rewrite the plan."* Review
#2: *"This is much better than the previous version."* Review #1 was
the only round with purely corrective language.

This matches the prior session's "Your revision is materially stronger"
— user does provide explicit positive signals when work meets the bar.
Worth reading as signal, not politeness.

### User handed off review-as-is both sessions

First session: *"Save a handoff. I will review this draft as-is, then
share my feedback in the next session."*

This session: *"save a handoff. I will review the plan as-is and then
share my feedback with you in the next session."*

Near-identical phrasing. This is a stable working pattern: produce
artifact, hand off, fresh review pass. Worth preserving across sessions.

## User Preferences

**Adversarial-review format with numbered severity tags:**

User's scrutiny output uses a fixed structure with severity tags
(`Critical`, `High`, `Medium`) and a final verdict (`Reject`, `Major
revision`, `Minor revision`, `Minor edits`). This is a tool for rapid
convergence — the escalation pattern tells both parties where they
are in the cycle.

Pattern: when a session produces an artifact of meaningful size,
expect this review format.

**Pattern: "writing the desired architecture as if the transport already supports it":**

User named this explicitly in review #2. It's the single highest-
leverage critique pattern for this codebase — the failure mode is
pervasive because plugin transport is real code that constrains real
architecture, and plans often get written against desired shapes
instead of current shapes.

Practical rule: before any structural claim in a plan, verify the
claim against a specific file:line in the plugin's transport code.
If the claim can't be grounded, either verify it differently or
acknowledge the uncertainty explicitly.

**Pattern: "authority inflation":**

User named this explicitly in review #1. It's adjacent to the desired-
architecture pattern — it's what happens when prose in a plan asserts
a status (shared, current, authoritative) that the artifact doesn't
yet hold. Honesty demand: name what an artifact actually is, not what
it's aspiring to be.

**Cascading cuts over local mitigations:**

User explicitly endorsed the "drop gatherers entirely" cut in review
#2 judgment: "keep them out of v1 as separate agents." Cascading cuts
are a stronger response to multi-finding reviews than enumerating
local mitigations. When a reviewer lists 4-5 findings, search for the
structural cut that collapses them.

**User-authored decisions when offered options:**

Review #3 judgments on the two open calls: *"1. Namespace: share the
existing `shakedown/` namespace in v1. 2. Shakedown touch: no touch in
v1; keep the extracted reference production-local."*

When I surface genuine open calls, user decides directly rather than
asking me to recommend. This is the right mode — user's judgment on
repo-level invariants is load-bearing.

**Review-as-is over in-conversation iteration:**

Explicit pattern across two sessions. User prefers fresh review pass
over iterative refinement during the drafting session. Honor this by
surfacing options when hooks fire or constraints tighten, not by
silently reshaping.

**Explicit positive signals are real signal:**

Corrections come with evidence; acknowledgements come with verbatim
phrasing ("materially stronger", "this is now credible enough"). Both
are first-class data. Read the acknowledgement tone as a calibration
signal for the work's bar.

**Conceptual questions mid-flow:**

Mid-session, user asked a purely conceptual question ("What is
shakedown? What is its relationship to the dialogue capability?").
Answered in explanatory-mode depth (three-ring architecture, boundary
invariants rationale). This is a valid working pattern — user may
interrupt solution work with clarifying conceptual questions. Answer
at the requested depth and return to the task flow naturally.
