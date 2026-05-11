---
date: 2026-04-23
time: "18:24"
created_at: "2026-04-23T18:24:17Z"
session_id: c038943e-d784-4775-aeab-5940fbad5252
resumed_from: "docs/handoffs/archive/2026-04-23_17-55_exec-policy-amendment-design-brainstorm.md"
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: 41b4c1aa
title: "Exec-policy spec rejected, Packet 1 (deferred approval response) carved off"
type: handoff
files:
  - docs/tickets/2026-04-23-deferred-same-turn-approval-response.md
  - docs/superpowers/specs/2026-04-23-exec-policy-amendment-design.md
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/pending_request_store.py
  - packages/plugins/codex-collaboration/server/jsonrpc_client.py
  - packages/plugins/codex-collaboration/server/runtime.py
---

# Handoff: Exec-policy spec rejected, Packet 1 (deferred approval response) carved off

## Goal

Process the user's scrutiny of the exec-policy amendment design spec
(`edff9c07` on `feature/delegate-exec-policy-amendment`) and reach a
clean stopping point for the next session's brainstorm. This is a
scope-reconciliation turn, not a design turn. The predecessor session
produced an 805-line single-file spec; the user reviewed it, rejected
it with a structured `/scrutinize` output citing 4 Critical/High
findings plus a Required Changes list, and chose the split path
(B-prime) to carve the packet into two.

**Trigger:** User invoked `/load` to resume, then delivered the
scrutiny as a structured review message with verdict `Reject`. The
session's work was: verify the scrutiny's claims against repo state,
acknowledge the verdict honestly, present options, execute the chosen
split, and hand off.

**Stakes:** High — T-20260423-01 AC1 (end-to-end delegation with
platform-tool verification) is blocked. The rejected spec is the
second attempt to design the closure path; the first was the
predecessor session. Getting Packet 1's scope right now prevents a
third attempt from repeating the "transport prerequisite as
afterthought" pattern.

**Success criteria:**
- User's scrutiny verified against repo (trust-but-verify, not
  performative agreement).
- Path forward decided with user's explicit input, not assumed.
- Packet 1 ticket created with enough seed material that the fresh
  session's brainstorm has immediate grounding.
- Rejected spec preserved as record, not patched forward.
- Handoff chain continuity — next session's `/load` picks up cleanly.

**Connection to project arc:** This session's work does not close any
acceptance criterion directly. It carves off `T-20260423-02` (Packet
1) from `T-20260423-01` (parent acceptance-gap ticket) and lays the
groundwork for a fresh-session brainstorm. T-20260423-01's AC1 closes
when Packet 1's spec + implementation land AND the amendment admission
follow-up (Packet 2, not yet ticketed) also lands.

## Session Narrative

### 1. Resume and handoff archive

Session began with `/load`. Predecessor handoff was
`2026-04-23_17-55_exec-policy-amendment-design-brainstorm.md` —
archived at load time to `docs/handoffs/archive/`, state file written
to `.session-state/handoff-c038943e-d784-4775-aeab-5940fbad5252`.

Summarized predecessor for the user: 12 design decisions (D1–D12),
spec at `edff9c07`, branch `feature/delegate-exec-policy-amendment`,
immediate next action on resume = user's feedback on the spec.

Verified repo state matched handoff's Environment section:
- Branch `feature/delegate-exec-policy-amendment` — confirmed
- HEAD `edff9c07` — confirmed
- Working tree clean — confirmed

### 2. User delivered `/scrutinize` output against the spec

Not incremental feedback — a structured adversarial review. Key
sections:

- **Premise Check:** Directionally right seam identified (transport),
  but too much of the required rewrite treated as implementation
  detail.
- **4 Critical/High findings** with exact file:line citations:
  - Critical: `start()` return path unresolved
  - Critical: single captured_request model breaks on amended-turn
    resume with second approval
  - High: audit design depends on observability channel that doesn't
    exist (`applied` vs `error`)
  - High: timeout inconsistency + non-atomic status transition
- **3 Missing assumptions:** background-turn concurrency treated as
  "implementation-plan choice" when stores are lockless appenders;
  public contract changes claimed as "no changes" while introducing
  new verbs; `PendingRequestStore.update(...)` pseudocode against a
  store API that has no generic `update`.
- **Required Changes list** of seven items, each actionable.
- **Verdict:** `Reject`.

### 3. Invoked `superpowers:receiving-code-review` before responding

Critical discipline point. The scrutiny was structured and detailed;
performative agreement would have been the wrong response. The skill's
pattern: read → understand → verify → evaluate → respond → implement.

### 4. Trust-but-verify against the codebase

Read six targeted ranges in parallel to check the load-bearing claims.
All cited line numbers matched:

| Finding | Claim | Verified at |
|---|---|---|
| Critical 1 | `start()` returns `_execute_live_turn()` synchronously | `delegation_controller.py:618-624` |
| Critical 1 | `DelegationEscalation` constructed post-turn in `_finalize_turn` | `delegation_controller.py:1504-1510` |
| Critical 2 | `captured_request` singular, three `is None` guards | `delegation_controller.py:639, 685-687, 702-704, 714-716` |
| High 3 | `respond()` fire-and-forget stdin write | `jsonrpc_client.py:106-130` |
| High 3 | Loop continues consuming notifications with no ack | `runtime.py:243-249` |
| High 4 | Transport request_timeout 1200s; notification timeout 1200s | `runtime.py:49, 233`; `jsonrpc_client.py:163-170` |
| Missing | `PendingRequestStore` has only `create`/`get`/`list_*`/`update_status` | `pending_request_store.py:29-69` |

All claims confirmed. No grounds for pushback on any of the load-bearing
findings.

### 5. Presented options A / B / C

Three paths for the next iteration:

- **A. Patch in place** — add missing sections (start lifecycle,
  capture cardinality, concurrency, contracts) to the existing
  805-line file. Risk: structurally dishonest document blending
  validated and rejected content.
- **B. Split into two packets** — Packet 1 as control-plane rewrite;
  Packet 2 as amendment admission stacked on Packet 1. Cleaner
  separation.
- **C. Full rewrite** — scrap and restart. Throws away validated D1–D6,
  D9, D11, D12 from the rejected spec.

Recommended **Option B** with rationale: diagnosis at face value,
preserves validated work, each packet single-purpose.

### 6. User refined to B-prime

User's response: **B-prime**. The refinement: "keep Packet 1 narrowly
about deferred same-turn approval responses, not a generic 'new
control-plane framework.'" Also specified:

- Packet 1 scope (8 items listed in user's message)
- Packet 2 scope (6 items listed)
- Keep T-20260423-01 as parent; child ticket for Packet 1 is the
  user's preference
- Start Packet 1 on fresh branch from main, not on existing branch
- Treat current spec as **rejected input**, not fix-forward target

This matched the user's established "narrower > broader" scope
discipline pattern (e.g., the Narrower-B scope decision from the
predecessor session).

### 7. Session-split decision

Asked the user where to run the brainstorm: here (~90k context
headroom) or fresh session. Recommended fresh session (Path A).

User's response: **A.** Reasoning: "The setup is cheap and
deterministic; the brainstorm is the expensive, failure-prone part.
Splitting them keeps the next session focused on Packet 1's real work
instead of spending half the budget re-establishing boundaries."

### 8. Setup execution

Executed the setup operations:

- `git checkout main && git pull --ff-only` — already up-to-date at
  `005d4b44`
- `git checkout -b feature/delegate-deferred-approval-response` —
  fresh branch off main HEAD
- Wrote `docs/tickets/2026-04-23-deferred-same-turn-approval-response.md`
  (191 lines) following T-20260423-01 format exactly
- Committed as `41b4c1aa` with message citing the B-prime split

Ticket content includes:
- Parent/child relationship (`blocks: [T-20260423-01]`)
- 8 in-scope items (matching user's B-prime packet-1 scope)
- 3 out-of-scope items (explicit non-goals)
- 7 brainstorm questions, each with file:line evidence from the
  verification pass
- 8 acceptance criteria for the design phase
- Provenance pointing to `edff9c07` rejected spec + scrutiny record
- Non-goals that carve out implementation + amendment-specific logic
  + D1–D6, D9, D11, D12 (those survive to the follow-up ticket)

Rejected spec `edff9c07` remains on `feature/delegate-exec-policy-amendment`
— dormant, not deleted, not merged.

## Decisions

### D1: Accept scrutiny verdict (Reject) — do not fix forward

**Choice:** Treat `edff9c07` as rejected input; do not patch the
single-file spec. Preserve it on its branch as historical record.

**Driver:** Verified 4/7 load-bearing claims against codebase with
exact line-matches. Scrutiny's core diagnosis — "the spec is trying to
preserve the existing public/control-plane shape while quietly
introducing a fundamentally different lifecycle" — matches repo
evidence (e.g., `_execute_live_turn` synchronous return at
`delegation_controller.py:618-624` incompatible with spec's
turn-stays-live claim at spec line 347-427).

**Rejected alternatives:**
- **Patch the spec in place (Option A):** Rejected because the
  resulting 1,200+ line document would blend validated decisions with
  post-rejection revisions. Future readers would have to archeology
  which parts were approved vs corrected. Structurally dishonest.
- **Full rewrite (Option C):** Rejected because D1–D6, D9, D11, D12
  from the rejected spec are still validated design work — scope
  (D1), contract revision + gate (D2), allowlist eligibility (D3),
  distinct verb (D4), persistence (D5), dedicated record (D6),
  diagnostic gate shape (D9), branch discipline (D11), single-file
  format (D12) all survive. Throwing them away would waste validated
  work.

**Implication:** 805-line spec stays on dormant branch. Two new specs
will be written: Packet 1 (this session's ticket, next session's
brainstorm) and Packet 2 (follow-up, reuses D1–D6, D9, D11, D12).

**Trade-offs accepted:** Two specs instead of one. Packet 1's ticket
creates tracking overhead. Accepted because a single-file with
patched-in transport design would be structurally dishonest and would
set a bad precedent for future scope-rot.

**Confidence:** High (E2) — verified 4/7 claims directly; scrutiny's
specificity (exact line numbers for all claims) argues for trusting
the remaining 3.

**Reversibility:** High — rejected spec is preserved on its branch;
can be re-adopted or patched if Packet 1 brainstorm exposes that the
split was premature.

**Change trigger:** If Packet 1 brainstorm reveals that deferred
same-turn approval is materially simpler than the scrutiny implied,
could revisit whether a single spec would have worked. Evidence so
far is unambiguous though.

### D2: B-prime — Packet 1 narrow to deferred same-turn approval response, not generic framework

**Choice:** Packet 1 scope = the specific lifecycle required to send
an amendment/approval response back through an in-flight App Server
request. NOT a "generic deferred-decision framework."

**Driver:** User: "Keep Packet 1 narrowly about deferred same-turn
approval responses, not a generic 'new control-plane framework.'"
Matches the Narrower-B pattern from the predecessor session (user
pushed back on the original A-option for being too broad; similar
scope discipline here).

**Rejected alternatives:**
- **Generic deferred-decision framework:** Rejected because amendments
  are the only consumer for v1. Generality would blow up the design
  surface (capability negotiation, decision-kind parameterization,
  extensibility hooks). Reusability for future deferred-decision
  patterns is incidental, not a scope driver.
- **Wider control-plane rewrite:** Rejected for the same reason. Scope
  discipline protects the packet from becoming a re-architect.

**Implication:** Packet 1 has 8 concrete in-scope items, 3 explicit
non-goals. Future deferred-decision patterns copy the shape if they
want it; Packet 1 is not designed for them. If extension is ever
needed, it's additive work with its own ticket.

**Trade-offs accepted:** If Packet 1's primitives get reused later,
some aspects may need widening (e.g., decision-kind parameterization).
Accepted because premature generalization is worse than targeted
extension.

**Confidence:** High (E2) — user's framing was direct and matches
their established scope-discipline pattern. Two independent
reinforcing signals.

**Reversibility:** High — widening Packet 1 scope later is additive.

**Change trigger:** None anticipated. If Packet 2's brainstorm reveals
that other decision kinds need the same lifecycle, widen via a
follow-up sub-packet rather than retrofitting Packet 1.

### D3: Child ticket T-20260423-02; parent T-20260423-01 stays open and unrenamed

**Choice:** Create T-20260423-02 with `blocks: [T-20260423-01]`.
Parent stays open, not renamed.

**Driver:** User: "Keep T-20260423-01 as the parent acceptance-gap
ticket unless you want a child blocker ticket for Packet 1. I would
not rename the parent yet." Parent's role as the acceptance-gap anchor
is preserved; child tracks the blocker independently.

**Rejected alternatives:**
- **No child ticket, track Packet 1 implicitly under parent's "Scope
  Limitations":** Rejected because the two packets' progress should
  be visible independently — parent's AC1 has multiple blockers
  (Packet 1 + Packet 2 follow-up), and implicit tracking conflates
  them.
- **Rename parent:** User explicitly said no.

**Implication:** Parent AC1 closure depends on Packet 1's spec
landing + implementation + admission-layer follow-up. Three gates, not
one. Makes dependency chain explicit.

**Trade-offs accepted:** One more ticket to track. Accepted.

**Confidence:** High (E1) — direct user guidance.

**Reversibility:** High.

**Change trigger:** None.

### D4: Branch `feature/delegate-deferred-approval-response` from main

**Choice:** Fresh branch off main at `005d4b44`. New branch name
matches `feature/*` convention.

**Driver:** User: "Start Packet 1 on a fresh branch from main, not on
feature/delegate-exec-policy-amendment." Scope discipline: the
rejected branch is preserved untouched as record.

**Rejected alternatives:**
- **Continue on `feature/delegate-exec-policy-amendment`:** Rejected
  per user direction. The rejected spec on that branch is the
  historical artifact.

**Implication:** Rejected spec stays dormant. Never pushed, never
merged, never modified. If future sessions need to reference D1–D6,
D9, D11, D12, cite the commit `edff9c07`, not a live file.

**Confidence:** High (E1).

**Reversibility:** High.

**Change trigger:** None.

### D5: Session split — setup in current session, brainstorm in fresh session

**Choice:** Path A — execute ticket creation + branch setup in current
session, then save handoff. Fresh session runs the Packet 1
brainstorm.

**Driver:** User: "A. The setup is cheap and deterministic; the
brainstorm is the expensive, failure-prone part. Splitting them keeps
the next session focused on Packet 1's real work instead of spending
half the budget re-establishing boundaries."

**Rejected alternatives:**
- **Path B (brainstorm in current session):** Current context at
  ~117k/200k (59%). A rigorous 7-question brainstorm with section-by-
  section review + spec write typically burns 40–80k. Feasible but
  risks hitting ~180k before the spec is complete. Fresh session
  eliminates this risk.

**Implication:** Next session opens with full context budget, picks
up via `/load`, and starts `superpowers:brainstorming` directly.
Handoff carries B-prime plan + 7 questions + verification work
forward.

**Confidence:** High (E1).

**Reversibility:** N/A — session boundary.

**Change trigger:** None.

## Changes

### `docs/tickets/2026-04-23-deferred-same-turn-approval-response.md` — new file, 191 lines

**Purpose:** Seeds Packet 1's scope + 7 brainstorm questions + 8
acceptance criteria. Establishes parent/child relationship with
T-20260423-01.

**Approach:** Matches T-20260423-01's format exactly — YAML
frontmatter code block (id, date, status, priority, tags, blocked_by,
blocks, effort), numbered sections with narrative prose, tables for
evidence. Line-number evidence included for every brainstorm question
(grounds the fresh session in verified repo state).

**Key implementation details:**
- `blocks: [T-20260423-01]` — explicit dependency marker for future
  ticket-triage operations.
- 8 in-scope items match user's B-prime Packet 1 list exactly.
- 3 out-of-scope items carve out amendment admission + eligibility +
  generic framework.
- 7 brainstorm questions map 1-to-1 with the user's recommendation.
- Provenance section cites `edff9c07`, the scrutiny date, and the
  B-prime split decision.
- Non-goals section explicitly excludes implementation, amendment-
  specific logic, and revisiting surviving decisions from rejected
  spec.

**Future-Claude note:** The ticket's "Design-phase brainstorm
questions" section is the authoritative source for the fresh session's
brainstorm. Each question has a repo-grounded evidence line — those
line numbers may drift if the codebase changes before the brainstorm
runs. Worth spot-checking in the fresh session's Task 1 (context
exploration) before Task 2 (question-driven design).

### Branch `feature/delegate-deferred-approval-response` created from main

**Purpose:** Isolate Packet 1's design work from the rejected spec's
branch. Keep the rejected artifact preserved untouched.

**Approach:** `git checkout main && git pull --ff-only && git checkout
-b feature/delegate-deferred-approval-response`. Standard
feature-branch creation off main HEAD.

**Key detail:** Branch matches the repo's `feature/*` convention from
`.claude/rules/workflow/git.md`. Origin has no push yet — branch is
local-only until spec is written and user decides to push.

### Commit `41b4c1aa` on `feature/delegate-deferred-approval-response`

**Purpose:** Durable record of ticket creation + split rationale.

**Approach:** Single-file commit, message body documents the
carve-off, references `edff9c07` as the rejected antecedent, cites
the B-prime split.

**Key detail:** Commit message matches repo conventions
(`chore: add ...` prefix for ticket additions, matching the parent
ticket's creation commit `82121adf`).

## Codebase Knowledge

### Files read this session (verification pass)

| File | Lines read | Why | Key finding |
|------|-----------|-----|-------------|
| `delegation_controller.py` | 600-735 | Verify `start()` sync return + capture model | `_execute_live_turn` returns inline at 618-624; `captured_request: PendingServerRequest \| None = None` at 639; three set-sites guarded by `is None` at 685-687, 702-704, 714-716 |
| `delegation_controller.py` | 1440-1515 | Verify `DelegationEscalation` construction site | Single construction at 1504-1510 inside `_finalize_turn` post-turn block; runtime kept live for decide's reuse; view projected via `_project_request_to_view` |
| `pending_request_store.py` | 1-140 | Verify store API surface | API: `create(PendingServerRequest)`, `get(request_id)`, `list_pending()`, `list_by_collaboration_id(cid)`, `update_status(id, status)`. No generic `update`. JSONL append + replay pattern. `_VALID_STATUSES` enforced on both write paths. |
| `jsonrpc_client.py` | 90-175 | Verify respond is fire-and-forget | `respond(request_id, result)` at 106-130 writes to `process.stdin` + flushes; no response channel; only failure mode is `BrokenPipeError`. `_get_message` timeout at 163-170 uses `self._request_timeout` default. |
| `runtime.py` | 40-270 | Verify timeouts + handler loop | `AppServerRuntimeSession.__init__` default `request_timeout: float = 1200.0` at 49; `_run_turn` notification loop `next_notification(timeout=1200.0)` at 233; handler response dispatched inline at 245-248 via `self._client.respond(notification["id"], response_payload)`; loop continues to next notification after respond. |
| `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` | full | Format reference for new ticket | YAML frontmatter code block; numbered sections (Context, Defect N, Acceptance criteria, Implementation sequence, Evidence, Source-verified defect locations); line-number evidence tables pervasive |

### Architecture confirmed

The amendment lifecycle (turn resumes after operator delay) does not
compose with the current call path. Concrete incompatibilities:

| Current behavior | Amendment-path need |
|---|---|
| `start()` returns only after turn ends (`delegation_controller.py:618`) | `start()` must return while turn stays live |
| `DelegationEscalation` built post-turn inside `_finalize_turn` | Escalation must be surfaced mid-turn |
| `captured_request` singular, set-once | Amended turn resumes → second request could arrive → second capture needs a home |
| `JsonRpcClient.respond()` fire-and-forget stdin write | Audit requires observable response outcome (applied / error) |
| `PendingRequestStore` has `create/get/list_*/update_status` only | New fields (handler_disposition, resolution_result) need mutation path |
| Transport/notification-loop timeouts both 1200s | Operator window 1800s (spec) exceeds transport budget |
| `McpServer` synchronous/serialized (`mcp_server.py:191`); stores lockless appenders | Background turn execution + live decide = multi-threaded writes to unlocked logs |

### Architecture NOT in scope for verification (trusted from scrutiny citations)

| File | Claim | Source |
|------|-------|--------|
| `models.py:34-47, 420-437` | Current `DecisionAction` enum + rejection reason shapes | Scrutiny |
| `contracts.md:297-310` | Current decide contract | Scrutiny |
| `mcp_server.py:191` | Synchronous dispatch | Scrutiny |
| `delegation_controller.py:1789-2057` | Cold-start recovery behavior | Scrutiny |
| `delegation_job_store.py:133-140` | Lockless appender pattern | Scrutiny |
| `journal.py:301-307` | Lockless append | Scrutiny |

These were not re-verified but the citations are specific and the
pattern fits the verified portions. Treat as accurate unless a
specific claim is contradicted during Packet 1 brainstorm.

### Key locations future-Claude needs

| Concept | Location |
|---------|----------|
| Start lifecycle | `delegation_controller.py:577-624` (entry to `_execute_live_turn`) |
| Server request handler | `delegation_controller.py:650-720` |
| Post-turn finalization | `delegation_controller.py:1440-1515` (`_finalize_turn`) |
| Projection to operator view | `delegation_controller.py:~864` (`_project_request_to_view`) |
| Decide entry | `delegation_controller.py:~1731` (approve) / `~1802` (deny) |
| Cold-start reconciliation | `delegation_controller.py:~2117` |
| JSON-RPC respond | `jsonrpc_client.py:106-130` |
| JSON-RPC receive loop | `jsonrpc_client.py:163-175` |
| Turn notification loop | `runtime.py:194-275` (`_run_turn`) |
| Pending request store | `pending_request_store.py:21-140` |
| Runtime registry | `runtime_registry.py` |
| MCP tool surface | `mcp_server.py:160` (decide schema) |

## Context

### Mental model

**This session is scope-reconciliation, not design.** It converts a
too-broad spec into two properly-scoped packets. The design work moves
to the next session.

**The B-prime pattern** — split packets on architecture/feature lines
when a single spec is trying to do both — is reusable. Any future
design spec that names infrastructure as a prerequisite without
designing it is a candidate for the same carve-off.

**Why the carve-off works:** Packet 1 is about mechanism (call paths,
data models, contracts); Packet 2 is about policy (what to admit, what
to reject). These are separable concerns with a clean interface (Packet
1's primitives are a library; Packet 2 is a consumer).

### Environment state

- Branch `feature/delegate-deferred-approval-response` at commit
  `41b4c1aa`. Not pushed to origin.
- Working tree clean.
- `feature/delegate-exec-policy-amendment` branch at `edff9c07`,
  dormant with rejected spec. Not pushed, not deleted.
- `main` at `005d4b44` — matches origin.
- Handoff state file at
  `docs/handoffs/.session-state/handoff-c038943e-d784-4775-aeab-5940fbad5252`
  will be cleaned by the save procedure.

### Project arc

| Milestone | Status |
|-----------|--------|
| T-07 delegate smoke (predecessor) | Complete — identified AC1 blockers |
| PR #125: state-machine + boundary tightening | Merged 2026-04-23 |
| T-20260423-01 parent ticket | Open — AC1 still blocked |
| First amendment spec attempt (`edff9c07`) | **Rejected** 2026-04-23 |
| T-20260423-02 Packet 1 ticket | **Created** 2026-04-23 (this session) |
| Packet 1 brainstorm | Queued for fresh session |
| Packet 1 spec + implementation | Not started |
| Packet 2 (amendment admission) ticket | Not yet ticketed; stacks on Packet 1 |
| T-20260423-01 AC1 closure | Blocked on Packet 1 + Packet 2 |

## Learnings

### Named prerequisites without owned designs are a red flag

**Mechanism:** When a design spec names infrastructure as a
"prerequisite" and moves on, that infrastructure often dominates the
actual cost. The document gives the appearance of a bounded feature
spec when the underlying work is a larger rewrite.

**Evidence:** The rejected spec named "transport prerequisite"
(`docs/superpowers/specs/2026-04-23-exec-policy-amendment-design.md`)
but didn't design it. Scrutiny's core diagnosis: "it still
underestimates how much architecture has to move with it." The
architecture was the packet, not a precondition.

**Implication:** Future design spec reviews should ask: "Does this
spec name any infrastructure that isn't actually designed here?" If
yes, decide whether to own it in this packet or split it off cleanly.
Don't ship a spec that names a primitive it doesn't design.

**Watch for:** Phrases like "assumes X exists," "builds on Y,"
"requires Z at runtime." Each is a potential red flag.

### Line-number-grounded scrutiny is dispositive

**Mechanism:** When a reviewer cites specific repo lines for every
claim, verification of 2-3 spot-checks can be extrapolated to the
rest. Non-cited claims are lower signal; every-line-cited reviews are
higher signal.

**Evidence:** User's scrutiny cited exact file:line for every claim
(e.g., `delegation_controller.py:614`, `jsonrpc_client.py:97-130`).
Verified 4/7; all matched. Trusted remaining 3 on pattern match.
Decision to accept verdict was high-confidence without re-verifying
every claim.

**Implication:** For future reviews — both giving and receiving —
invest in line-number citations. It compresses the verification loop
from "check everything" to "spot-check enough to validate the
pattern."

**Watch for:** Reviews with vague citations (entire files, no lines)
— these require more verification work per claim.

### Spec-as-rejected-input preserves cleaner history than spec-as-patched-forward

**Mechanism:** A rejected spec on a dormant branch is a citable,
unambiguous artifact. A patched-forward spec blends approved and
corrected content in a single file — future readers have to diff
against prior commits to see what was approved vs corrected.

**Evidence:** The rejected `edff9c07` is now preserved on
`feature/delegate-exec-policy-amendment` — any future session can
cite "the rejected design spec at `edff9c07`" unambiguously. If we'd
patched forward, D1–D6, D9, D11, D12 would be mixed with revisions
to D7, D8, D10, and the transport-design additions.

**Implication:** For designs that get substantive rejection, prefer
dormant-branch preservation over in-place patching. The cost of
carrying an extra ticket is lower than the cost of archeology.

**Watch for:** "Just add a section" suggestions after a design
rejection — often the wrong move if the rejection is structural.

### Reusability as incidental benefit, not scope driver

**Mechanism:** When designing infrastructure primitives, it's tempting
to pre-parameterize for future consumers. The user's B-prime
refinement rejects this: Packet 1 is designed for amendments;
reusability is incidental.

**Evidence:** User: "Keep Packet 1 narrowly about deferred same-turn
approval responses, not a generic 'new control-plane framework.'"
Also: the Narrower-B pattern from the predecessor session (reject
`acceptForSession`-style widening).

**Implication:** When Packet 1's primitives get reused (if they do),
extension is additive. Future consumers can drive their own scope
tickets. The primitive doesn't need to pre-support them.

**Watch for:** Design proposals that parameterize for speculative
future consumers. Push back: what consumer exists today? If zero,
don't parameterize.

## Next Steps

### 1. Start Packet 1 brainstorm in a fresh session

**Dependencies:** None — ticket seeds the work.

**What to read first:**
- This handoff (via `/load`).
- Ticket T-20260423-02 at
  `docs/tickets/2026-04-23-deferred-same-turn-approval-response.md`.
- Spot-check line numbers in the ticket's question evidence (verify
  no drift since this session's verification pass).

**Approach:** Invoke `superpowers:brainstorming` as the first
significant action. Drive the 7 questions in order; user's
predecessor-session pattern was section-by-section-approval with
substantive corrections per section. Expect 3-5 rounds of refinement
per question.

**Acceptance criteria:** Packet 1 spec produced on
`feature/delegate-deferred-approval-response` covering all 8 in-scope
items + all 8 acceptance criteria from T-20260423-02.

**Potential obstacles:**
- Background-task execution model is genuinely novel — Python
  threading vs asyncio vs subprocess choice is a real design question
  with cascading implications.
- Capture cardinality (Q2) may require live App Server evidence to
  adjudicate (does an amended turn emit a second approval?). If so,
  note as a deferred observation rather than blocking the spec.

### 2. Implementation plan via `superpowers:writing-plans`

**Dependencies:** Packet 1 spec approved.

**Approach:** Phase-by-phase implementation plan grounded in Packet
1's spec. Initial phase likely covers the transport primitive
(blocking resolution registry + background-turn execution); later
phases layer on mutations to stores and public contracts.

### 3. Packet 1 implementation

**Dependencies:** Plan approved.

**Scope:** Execute the plan phase-by-phase. Each phase its own
commit-group; land Packet 1 to main when AC1 checks pass.

### 4. Packet 2 (amendment admission) ticket + design

**Dependencies:** Packet 1 merged to main.

**Scope:** Revise the rejected spec into an admission-only document.
Reuse D1 (scope), D2 (contract revision + gate), D3 (allowlist
eligibility), D4 (distinct verb), D5 (persistence), D6 (dedicated
record), D9 (diagnostic gate shape), D11 (branch), D12 (single file).
Drop "transport prerequisite" entirely — Packet 1's merged primitives
are the substrate.

### 5. T-20260423-01 AC1 verification

**Dependencies:** Packet 1 + Packet 2 merged.

**Approach:** Live `/delegate` smoke with a real file-edit objective.
Confirm end-to-end delegation produces artifacts.

## In Progress

**State:** Clean stopping point. Setup is complete:
- Child ticket `T-20260423-02` written and committed (`41b4c1aa`).
- New branch `feature/delegate-deferred-approval-response` created
  from main.
- Rejected spec preserved dormant on
  `feature/delegate-exec-policy-amendment`.

**Immediate next action on resume:** `/load` will surface this
handoff. Fresh session should invoke `superpowers:brainstorming`
targeting the 7 questions in T-20260423-02. Do not open the rejected
spec file for editing — it's preserved as historical record only.

## Open Questions

The seven brainstorm questions from T-20260423-02 are the open
questions. Each is design work, not factual lookup:

1. How does `start()` return an operator-visible escalation while the
   original App Server turn stays live?
2. What replaces the single `captured_request` model?
3. What persisted state records blocked-request disposition, and how
   is that state mutated after capture?
4. How do `poll()` and `decide()` synchronize with background turn
   execution?
5. What exact MCP tool schema / contracts.md / model enum changes are
   required?
6. What outcome can the runtime honestly observe after sending a
   deferred response?
7. What timeout budget matches the real transport limits?

Questions 5 and 6 also have factual sub-components (current contract
state; current observability surface) that can be answered from repo
state directly; the design choices remain open.

## Risks

1. **Packet 1's brainstorm may expose that the 8 in-scope items are
   mis-scoped.** Either too broad (can drop items) or too narrow
   (needs additions). Mitigation: ticket treats the items as starting
   scope, not binding scope; fresh session can refine via the
   brainstorm's clarifying-question phase.

2. **Concurrency model change requires test rework.** Lockless
   appenders in stores (`pending_request_store.py:71-75`,
   `delegation_job_store.py:133-140`, `journal.py:301-307`) aren't
   designed for multi-threaded writes. If background-turn execution
   lands, either add locking or re-architect. Either way, existing
   tests that assume serial dispatch will need updates. Implementation
   plan should scope this.

3. **T-20260423-01 AC1 remains blocked until Packet 1 + Packet 2 both
   land.** No partial unblock available. This constrains downstream
   promotion work that depends on working delegation.

4. **Spec-write pattern inconsistency across sessions.** Predecessor
   session produced a single-file spec (user chose Option 1 over
   modularized). Packet 1 default is similarly single-file. If
   Packet 1 exceeds 1000 lines, reconsider `superspec:spec-writer`
   modularization.

5. **Background-task execution model may require deeper runtime
   changes than estimated.** Current runtime is synchronous; the
   design choice (threading / asyncio / subprocess) has cascading
   implications for error handling, signal safety, lifecycle, and
   crash recovery. Spec should name the choice explicitly; brainstorm
   should not defer it.

6. **The 7 brainstorm questions' line-number evidence may drift.**
   Codebase changes between this session and the next session could
   invalidate the cited line numbers. Mitigation: fresh session's
   first action should spot-check 2-3 lines to confirm currency.

## References

| What | Where |
|------|-------|
| Packet 1 ticket (this session's artifact) | `docs/tickets/2026-04-23-deferred-same-turn-approval-response.md` |
| Parent acceptance-gap ticket | `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` |
| Rejected design spec | `docs/superpowers/specs/2026-04-23-exec-policy-amendment-design.md` at commit `edff9c07` on `feature/delegate-exec-policy-amendment` |
| Predecessor handoff (archived) | `docs/handoffs/archive/2026-04-23_17-55_exec-policy-amendment-design-brainstorm.md` |
| This session's commit | `41b4c1aa` |
| Current branch | `feature/delegate-deferred-approval-response` |
| Rejected-spec branch | `feature/delegate-exec-policy-amendment` (dormant) |
| PR #125 (state-machine + boundary tightening) | https://github.com/jpsweeney97/claude-code-tool-dev/pull/125 |
| Server request handler | `packages/plugins/codex-collaboration/server/delegation_controller.py:650-720` |
| Post-turn finalization | `packages/plugins/codex-collaboration/server/delegation_controller.py:1440-1515` |
| JSON-RPC respond | `packages/plugins/codex-collaboration/server/jsonrpc_client.py:106-130` |
| Pending request store | `packages/plugins/codex-collaboration/server/pending_request_store.py:21-140` |
| Turn notification loop | `packages/plugins/codex-collaboration/server/runtime.py:194-275` |

## Gotchas

- **Rejected spec is on `feature/delegate-exec-policy-amendment`, not
  merged and not pushed.** Future sessions may confuse this with
  "available at main" — it's branch-only until (if ever) resurrected.
- **Handoff chain protocol is filesystem-based, gitignored.** The
  `docs/handoffs/archive/` and `.session-state/` directories are
  gitignored; handoffs don't travel across machines. Chain continuity
  relies on the local filesystem.
- **`resolution-class classifier` from D7 of rejected spec is NOT
  Packet 1's concept.** The classifier is an admission-layer
  abstraction (Packet 2). Packet 1 is about mechanism, not
  classification. Do not import classifier language into Packet 1's
  brainstorm.
- **Single-file spec vs modularized is a deferred choice.** Packet 1
  defaults to single-file per predecessor-session preference, but if
  it grows past 1000 lines the user may revisit. Size is the trigger.
- **Line-number evidence in the ticket may drift.** If codebase
  changes between this session and the brainstorm session, spot-check
  2-3 cited lines before trusting the rest.
- **Background-turn execution model is the biggest design surface.**
  Spec's rollout must own this choice (threading / asyncio /
  subprocess) rather than defer it. Deferring caused the previous
  rejection.
- **`AMENDMENT_DECIDE_TIMEOUT` is not Packet 1's concept directly —
  but the timeout-alignment question (Q7) is.** Packet 1 needs to
  define operator-window, transport-budget, and runtime-notification
  timeouts coherently. Specific values are implementation detail; the
  coordination rule is spec-level.
- **The scrutiny's Required Changes #7 (`PendingRequestStore`
  mutation API) is item 3 in the brainstorm questions.** Two
  independent forces converge on the same need: add mutation methods
  or inline fields at create-time.

## User Preferences

Validated from this session (consistent with predecessor):

**Codebase-authority-first scrutiny.** Every claim in the scrutiny
had file:line evidence. Future sessions should expect and match this
rigor — cite lines when making factual claims, don't hand-wave.
User's scrutiny: "Severity: Critical. To make it defensible, the spec
needs an explicit replacement start lifecycle, not just 'background
turn execution exists.'"

**Scope discipline: narrower > broader.** User's B-prime refinement:
"Keep Packet 1 narrowly about deferred same-turn approval responses,
not a generic 'new control-plane framework.'" Consistent with
predecessor-session's Narrower-B scope choice.

**Spec-as-rejected-input over spec-as-patched-forward.** User: "Treat
the current amendment spec as rejected input, not something to 'fix
forward' in place." Preserves history cleanly; avoids archeology.

**Session-budget awareness.** User chose Path A (setup now, brainstorm
fresh): "The setup is cheap and deterministic; the brainstorm is the
expensive, failure-prone part." Protects high-value work from context
pressure.

**Reusability is incidental, not scope driver.** From B-prime: Packet
1's primitives aren't designed for hypothetical future consumers.
Extension is additive.

**Structured multi-choice delivery with reasoning.** User's
recommendations cited alternatives, rejected them with reasoning, and
named the next concrete step. Matches predecessor pattern. Future
sessions should offer this shape when presenting choices back to the
user.

**Design-language epistemic honesty.** User sharpens phrasing to
preserve tension rather than resolve it falsely. E.g., scrutiny's
"The spec found the right seam, but it still is not executable as
written" — acknowledges directional correctness while rejecting the
artifact.

## Conversation Highlights

**User's scrutiny verdict:**
> "The design found the right seam, but it still is not executable as
> written. The transport change is real; the spec just has not yet
> carried its consequences through the controller lifecycle, capture
> model, public contract, and observability story."
— The core diagnosis. Directional correctness + rejection on
executability.

**User's Critical-1 framing:**
> "That is not an implementation detail; it is the public
> start-contract."
— Sharpened the distinction between "named but not designed" vs
"implementation detail." Named-but-not-designed is not OK for
public-surface concerns.

**User's pattern-level diagnosis:**
> "The findings are mostly systemic, not isolated. The spec is trying
> to preserve the existing public/control-plane shape while quietly
> introducing a fundamentally different lifecycle: 'same-turn approval
> response after operator delay.'"
— The root-cause framing that justified the rejection and informed
the split.

**User's B-prime scope refinement:**
> "B-prime = split the packets, but keep Packet 1 narrowly about
> deferred same-turn approval responses, not a generic 'new
> control-plane framework.'"
— Scope discipline. Prevented the reusability-first trap.

**User's path-A rationale:**
> "A. The setup is cheap and deterministic; the brainstorm is the
> expensive, failure-prone part. Splitting them keeps the next
> session focused on Packet 1's real work instead of spending half
> the budget re-establishing boundaries."
— Session-budget discipline. Protects the brainstorm from context
pressure.

**User's artifact-preservation directive:**
> "Treat the current amendment spec as rejected input, not something
> to 'fix forward' in place."
— Cleaner history protocol. The rejected spec is a citable artifact,
not a working document.

**User's branch discipline:**
> "Start Packet 1 on a fresh branch from main, not on
> feature/delegate-exec-policy-amendment."
— Fresh branch off main signals Packet 1 is a distinct packet, not
continuation.

**User's ticket-shape framing:**
> "Keep T-20260423-01 as the parent acceptance-gap ticket unless you
> want a child blocker ticket for Packet 1. I would not rename the
> parent yet."
— Separates acceptance-gap tracking (parent) from blocker execution
(child). Parent preserved.
