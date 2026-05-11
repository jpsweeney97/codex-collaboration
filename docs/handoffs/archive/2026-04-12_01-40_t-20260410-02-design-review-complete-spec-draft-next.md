---
date: 2026-04-12
time: "01:40"
created_at: "2026-04-12T05:40:51Z"
session_id: 03831bb2-c146-4dab-98d1-97c8df957b6b
resumed_from: docs/handoffs/archive/2026-04-12_00-52_s1-refactor-pr-merge-ticket-triage.md
project: claude-code-tool-dev
branch: main
commit: 7f7cbfc6
title: T-20260410-02 design review complete; spec draft next
type: handoff
files:
  - docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md
  - docs/tickets/2026-03-30-codex-collaboration-plugin-shell-and-consult-parity.md
  - docs/tickets/2026-04-10-dialogue-codex-turn-semantics-clarification.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/specs/codex-collaboration/delivery.md
  - packages/plugins/codex-collaboration/README.md
  - packages/plugins/codex-collaboration/.claude-plugin/plugin.json
  - packages/plugins/codex-collaboration/.mcp.json
  - packages/plugins/codex-collaboration/server/dialogue.py
  - packages/plugins/codex-collaboration/server/turn_store.py
  - packages/plugins/codex-collaboration/server/replay.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_dialogue.py
  - packages/plugins/codex-collaboration/tests/test_turn_store.py
  - packages/plugins/codex-collaboration/tests/test_control_plane.py
  - packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md
  - packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md
  - packages/plugins/codex-collaboration/agents/shakedown-dialogue.md
---

# T-20260410-02 design review complete; spec draft next

## Goal

Orient on `T-20260410-02` deeply enough to evaluate the design space before any
implementation work begins.

The user explicitly asked for a read-oriented session first:
"Read each of the relevant files for `T-20260410-02` to orient yourself and
understand this work and its context within the larger codex-collaboration
Claude Code plugin build."

The session then shifted from orientation into design scrutiny.

The user presented three implementation directions for the fast-path hardening
work and asked for a critical read:
"What's your read?"

After the first critique, the user refined the proposal into a second-pass
design and raised the bar again:
"Probe this for gaps. Really scrutinize this - I want to catch problems early."

The practical goal became:
produce a design-level review strong enough that the user can write a spec in a
separate session without accidentally preserving a subtle hole in the
turn-sequence derivation logic.

Stakes were moderate but real.

`T-20260410-02` is not a cosmetic cleanup ticket.
It hardens `DialogueController._next_turn_sequence()` in the live
codex-collaboration dialogue path.
That path is exercised by the existing `codex.dialogue.*` MCP surface and by
downstream dialogue/shakedown tooling.

Success criteria for this session were:
- understand the current implementation and test surface
- place the ticket correctly within the codex-collaboration build arc
- evaluate approaches A/B/C without coding
- converge on a design shape future implementation can safely follow
- identify any remaining bug or ambiguity before the user writes the spec

All of those criteria were met.

No repository implementation work was attempted or requested.
This session ended intentionally at the design-review boundary.

## Session Narrative

The session began from the prior handoff rather than from a blank slate.

The immediately preceding archived handoff established the current project
baseline:
PR `#104` is merged, the repository is on `main`, the working tree is clean,
and the suggested next work item is `T-20260410-02`.

I loaded that handoff, verified the repo state, and confirmed that `main` was
still aligned with `origin/main` at `7f7cbfc6`.

That mattered because it meant this session did not need to spend any time on
branch cleanup, merge fallout, or unfinished implementation work.
The design discussion could start from a clean repository and a closed prior
task.

After the handoff load, the user did not ask for code changes.
They asked for orientation.
That changed the mode from "default implementation" to "read, map, and analyze."

I first identified the files directly named by the ticket:
`docs/tickets/2026-04-10-T-20260410-02-...`,
`packages/plugins/codex-collaboration/server/dialogue.py`, and
`packages/plugins/codex-collaboration/tests/test_dialogue.py`.

I also checked whether there were any nested `AGENTS.md` files inside the
codex-collaboration package.
There were not.
That meant the repo-level instructions governed the area.

The first reading pass was intentionally broad.

I read the ticket body to anchor the problem statement and acceptance criteria.
The ticket says the fast path currently treats `TurnStore.get_all()` returning
an empty mapping as definitive proof that no turns have completed, and calls out
corruption, path mismatch, and partial metadata as the failure modes to harden
against.
That framing comes from
`docs/tickets/2026-04-10-T-20260410-02-...:18-32`.

I then read the codex-collaboration package README.
That shifted the framing in an important way.
The README shows that the package is already presenting itself as a plugin with
consultation and dialogue support, installation instructions, and a smoke test;
see `packages/plugins/codex-collaboration/README.md:16-63`.

At that point, the first understanding shift happened:
`T-20260410-02` is not a speculative future-architecture ticket.
It is a hardening ticket inside an already-real dialogue surface.

The next pass focused on the actual dialogue control flow.

I read `DialogueController.reply()` around
`packages/plugins/codex-collaboration/server/dialogue.py:351-389`.
That established the ordering:
the controller loads the runtime and repo identity, derives `turn_sequence`
through `_next_turn_sequence()`, and only then builds the request packet and
writes the intent journal entry.

That ordering matters.
If `_next_turn_sequence()` is wrong, the failure happens before journaling,
before dispatch, and before any durable write.

I then read `_next_turn_sequence()` itself at
`packages/plugins/codex-collaboration/server/dialogue.py:725-753`.
The current implementation is extremely small:
`get_all()` is called,
empty local metadata immediately returns `1`,
otherwise `read_thread()` is called and completed turns are counted remotely.

That small size was clarifying.
The ticket is not asking for a large refactor.
It is asking for a more defensible trust predicate around one tight branch.

The next read targeted the persistence side of the same boundary.

`TurnStore.get_all()` at
`packages/plugins/codex-collaboration/server/turn_store.py:63-69`
replays the JSONL file and filters records for the current collaboration.
It does not surface replay diagnostics.

`TurnStore.check_health()` at
`packages/plugins/codex-collaboration/server/turn_store.py:73-75`
does surface replay diagnostics, but as a separate call.

`replay_jsonl()` at
`packages/plugins/codex-collaboration/server/replay.py:26-51`
classifies corruption into `trailing_truncation`, `mid_file_corruption`,
`schema_violation`, and `unknown_operation`, and computes `has_warnings` as
"anything other than trailing truncation."

That triggered the second key understanding shift:
the current problem is not "the replay layer cannot detect corruption."
It can.
The problem is that `_next_turn_sequence()` is using the replayed results
without any visibility into that diagnostic layer.

I then read `DialogueController.read()` at
`packages/plugins/codex-collaboration/server/dialogue.py:812-875`.
This was the first strong asymmetry signal.

`read()` already treats missing metadata for any completed remote turn as an
integrity failure.
Specifically,
`packages/plugins/codex-collaboration/server/dialogue.py:853-862`
raises if `metadata.get(seq)` is `None`.

That means the codebase already has a strict position on remote/local metadata
consistency in the read path.
The fast path in `_next_turn_sequence()` is the looser exception.

I then read `recover_startup()` around
`packages/plugins/codex-collaboration/server/dialogue.py:510-548`.
That introduced the third understanding shift.

Startup recovery already checks metadata completeness before reattaching
handles, but only with a coarse predicate:
`len(metadata) < completed_count`.

That means:
- missing tail metadata is rejected
- but gapped metadata with the same cardinality is not rejected
- and extra local metadata is also not rejected

That asymmetry became central to the later design review.

At that point I widened from implementation to surrounding architecture.

I read `mcp_server.py` to confirm the deployment and concurrency assumptions.
`packages/plugins/codex-collaboration/server/mcp_server.py:1-16` and
`:204-233` make the serialized-dispatch invariant explicit.

I read the codex-collaboration delivery spec and contracts to place the code in
the larger build arc.
`docs/superpowers/specs/codex-collaboration/delivery.md:205-245`
describes R2 as the dialogue foundation and explicitly lists the implemented
surface as `codex.status`, `codex.consult`, and `codex.dialogue.*`.
`docs/superpowers/specs/codex-collaboration/contracts.md:152-165`
defines crash-recovery eligibility in terms of zero completed turns or complete
TurnStore metadata.

This clarified that the ticket lives inside R2 hardening, not the later
supersession packaging packets.

I then looked at `T-20260330-02` anyway, because the user had asked for the
larger codex-collaboration build context.
The ticket still describes the plugin shell and consult parity work as open, but
the current package tree already contains `.claude-plugin/plugin.json`,
`.mcp.json`, README install docs, and consult/status skills.

That mismatch did not become the focus of the session, but it was worth noting
as context drift.
The current tree is ahead of parts of the old packet framing.

The next pass shifted into tests.

I read `test_dialogue.py` broadly, then narrowed to three clusters:
- first-turn fast-path tests
- read/recovery integrity tests
- repair/outcome tests

`test_first_reply_skips_read_thread()` at
`packages/plugins/codex-collaboration/tests/test_dialogue.py:1842-1871`
proves the happy-path optimization:
empty TurnStore on the first reply should not call `read_thread()`.

`test_second_reply_uses_read_thread()` at
`packages/plugins/codex-collaboration/tests/test_dialogue.py:1873-1909`
proves that once local metadata exists, the controller falls back to remote
counting.

`test_read_raises_on_pre_fix_turn_without_metadata()` at
`packages/plugins/codex-collaboration/tests/test_dialogue.py:1066-1086`
and the adjacent partial-metadata read test at `:1048-1065`
show the strict integrity behavior already present in `read()`.

That test coverage confirmed the exact boundary the ticket wants to strengthen:
protect the first-turn fast path without regressing the existing verified
optimization.

I also read `test_control_plane.py` to understand how the fake runtime models
the thread-materialization race.
`FakeRuntimeSession.read_thread()` at
`packages/plugins/codex-collaboration/tests/test_control_plane.py:125-137`
returns turns derived from `completed_turn_count` unless an override response is
provided.
That makes the first-turn tests very direct:
if you can stay on the empty fast path, you avoid remote thread reads
entirely.

Only after this orientation phase did the session move into design critique.

The user presented three candidate approaches:
secondary `check_health()`,
a new `get_all_checked()` method,
or changing `_replay()` and propagating diagnostics everywhere.

My initial read favored approach B:
an additive `TurnStore.get_all_checked()` API,
combined with controller-side structural validation.

The rationale was:
A duplicates replay work and splits one logical read into two calls;
C creates broad return-type churn for callers that do not need diagnostics;
B keeps the new behavior narrow and additive while preserving existing callers.

The user then presented an initial design built around that B-shaped API.

That first design had the right direction:
`get_all_checked()`,
four trust branches,
diagnostic-aware fallback,
and explicit error-context wrapping.

But while checking it against the existing code, one important weakness
remained:
the design still allowed a remote-success case where local metadata was empty
and diagnostics were present, yet the controller would accept a positive
`completed_count` and continue with `completed_count + 1`.

That was the fourth key understanding shift of the session.

The real invariant is not just:
"don’t trust empty local results when diagnostics exist."

The deeper invariant is:
once you leave the clean empty fast path and ask the remote thread for truth,
all local metadata states must be validated against the remote completed-turn
count, including the empty state.

That led to the recommendation to reuse a single consistency helper between
`_next_turn_sequence()` and `recover_startup()`,
and to treat non-matching local state as an integrity failure before dispatch,
not just a reason to keep counting remotely.

The user then posted `v2`, which adopted most of that feedback:
file-global diagnostics documented explicitly,
a shared `_local_metadata_consistent()` helper,
and updating `recover_startup()` to use the same invariant.

`v2` was close, but still preserved one bug:
its Phase 3 table treated empty local metadata after remote success as "n/a"
instead of validating it against the returned `completed_count`.

I responded by narrowing the remaining correction:
after remote success,
the invariant should apply to all local states,
not only to non-empty ones.
If diagnostics forced the controller off the fast path and the remote says one
or more turns have completed, empty local metadata should fail consistency just
like `{1}` against `completed_count=2` would.

The session ended after that design correction.

No code edits were made.
No tests were run.
The repository remained clean.

The user's explicit plan is to write the spec themselves and share it in the
next session for review.

That means future work starts from a design-review checkpoint, not from an
implementation checkpoint.

## Decisions

### Decision 1: Treat `T-20260410-02` as R2 dialogue hardening, not as plugin-shell work

**Decision:** Frame the ticket as a hardening pass inside the already-live R2
dialogue surface.

- **Driver:** The ticket itself targets only
  `server/dialogue.py` and `tests/test_dialogue.py`; see
  `docs/tickets/2026-04-10-T-20260410-02-...:12-15`.
  The delivery spec also lists the dialogue surface as already implemented in
  R2 at `docs/superpowers/specs/codex-collaboration/delivery.md:205-245`.
- **Rejected:** Treat it as part of packet `2a` packaging work.
  Rejected because the package already exposes `.claude-plugin/plugin.json`,
  `.mcp.json`, install docs, and skills in the current tree; see
  `packages/plugins/codex-collaboration/.claude-plugin/plugin.json:1-10`,
  `packages/plugins/codex-collaboration/.mcp.json:1-17`, and
  `packages/plugins/codex-collaboration/README.md:16-63`.
- **Implication:** Design and implementation should stay narrowly focused on
  turn-sequence derivation and test coverage, not reopen packaging scope.
- **Trade-offs:** This framing intentionally ignores the interesting drift
  between older ticket/spec language and the current package shape.
  That drift is real, but it is not necessary to solve `T-20260410-02`.
- **Confidence:** High (E2) — based on the ticket body plus independent
  confirmation from the current package tree and delivery spec.
- **Reversibility:** High — if the user later wants to reframe the work as part
  of a broader packet cleanup, the implementation can still remain the same.
- **Change trigger:** Reconsider only if the user explicitly expands scope to
  reconcile packet/ticket/spec drift during the same work item.

### Decision 2: Prefer additive `TurnStore.get_all_checked()` over approaches A or C

**Decision:** The right implementation shape is a new additive method on
`TurnStore` that returns both per-collaboration results and replay diagnostics
in a single pass.

- **Driver:** The user’s A/B/C design prompt asked for a comparative read, and
  the need is narrowly scoped to one controller decision point.
- **Rejected:** Approach A, a secondary `check_health()` call after `get_all()`.
  Rejected because it replays the same JSONL file twice and pushes replay-health
  stitching into `DialogueController`, even though the store is the natural
  owner of "results plus diagnostics" in one pass.
- **Rejected:** Approach C, changing `_replay()` return types and propagating
  diagnostics through `get_all()`, `get()`, and related callers.
  Rejected because it broadens churn far beyond the ticket and forces callers
  that do not care about diagnostics to absorb a new return contract.
- **Implication:** Future implementation should keep existing store APIs stable
  and add a new method for the new need.
- **Trade-offs:** The additive API still leaves one subtle policy burden in the
  controller: diagnostics are file-global, not collaboration-scoped.
  The controller must document and interpret that explicitly.
- **Confidence:** High (E2) — based on the existing store surface in
  `packages/plugins/codex-collaboration/server/turn_store.py:32-80`
  and the user’s candidate approaches.
- **Reversibility:** High — the additive method can be removed or inlined later
  if a broader replay API redesign ever becomes warranted.
- **Change trigger:** Reconsider only if multiple other stores or controllers
  begin needing the same "results plus diagnostics" contract and a shared
  replay-return convention becomes worth the churn.

### Decision 3: Any replay diagnostic is enough to distrust an otherwise-empty first-turn fast path

**Decision:** Do not gate this hardening on `ReplayDiagnostics.has_warnings`.
Treat any replay diagnostic as sufficient reason to distrust an empty local
result for fast-path purposes.

- **Driver:** The replay layer distinguishes benign crash-tail truncation from
  stronger warnings, but `_next_turn_sequence()` is not answering a generic
  replay-health question.
  It is answering:
  "Can I safely conclude that this collaboration has zero completed turns?"
- **Rejected:** Use `has_warnings` and ignore pure `trailing_truncation`.
  Rejected because a truncated final line may be the exact missing metadata
  entry for this collaboration’s first completed turn.
- **Rejected:** Ignore diagnostics unless they appear to belong to this
  collaboration.
  Rejected because `TurnStore` diagnostics are file-global and the file format
  does not give the controller a safe way to attribute parse failures to a
  collaboration-specific record.
- **Implication:** Any diagnostic forces `_next_turn_sequence()` off the empty
  fast path and into remote validation.
- **Trade-offs:** This is deliberately fail-closed.
  Corruption in another collaboration’s record can slow or block first-turn
  progression for a clean collaboration in the same session-partitioned file.
- **Confidence:** High (E2) — based on `replay_jsonl()` classification behavior
  at `packages/plugins/codex-collaboration/server/replay.py:26-51`
  plus the semantics of the ticket’s acceptance criteria.
- **Reversibility:** Medium — changing later to a more selective diagnostic
  policy would require confidence that per-collaboration attribution is safe.
- **Change trigger:** Reconsider only if the store format changes so that
  corruption attribution can be safely tied to a specific collaboration.

### Decision 4: Remote/local consistency must be enforced with one shared invariant across reply and recovery

**Decision:** The correct integrity rule is:
local metadata keys must equal exactly `{1, 2, ..., completed_count}` once the
controller has a remotely authoritative `completed_count`.

- **Driver:** `read()` already enforces strict metadata completeness for every
  completed remote turn at
  `packages/plugins/codex-collaboration/server/dialogue.py:853-862`,
  while `recover_startup()` currently uses only `len(metadata) < completed_count`
  at `:533-539`.
- **Rejected:** Contiguity-only local checks such as
  `sorted(keys) == range(1, max(keys)+1)`.
  Rejected because `{1}` is contiguous but still inconsistent if the remote says
  `completed_count == 2`.
- **Rejected:** Continue dispatching when local metadata is non-empty but gapped,
  partial, or extra, as long as `read_thread()` succeeds.
  Rejected because that would allow `reply()` to proceed on state that `read()`
  would later reject as an integrity failure.
- **Implication:** `_next_turn_sequence()` and `recover_startup()` should share
  the same helper and the same underlying invariant, even if their consequences
  differ.
- **Trade-offs:** This tightens behavior and may quarantine or reject dialogues
  that older logic would have allowed to limp forward.
  That is intentional.
- **Confidence:** High (E2) — based on the existing strictness in `read()`,
  the recovery eligibility contract in
  `docs/superpowers/specs/codex-collaboration/contracts.md:154-165`,
  and the observed weakness of the current cardinality-only check.
- **Reversibility:** Medium — loosening later would require a principled reason
  to tolerate states the read path currently defines as inconsistent.
- **Change trigger:** Reconsider only if the project explicitly decides to add
  a repair-or-heal path for gapped metadata rather than a fail-fast boundary.

### Decision 5: The current `v2` design still needs one correction before spec freeze

**Decision:** After a remote `read_thread()` succeeds, empty local metadata must
still be validated against `completed_count` if diagnostics forced the controller
off the clean fast path.

- **Driver:** The user’s `v2` table left empty local metadata as "n/a" in the
  post-remote consistency phase.
  That leaves an incorrect branch:
  diagnostics present,
  local metadata empty,
  remote reports completed turns,
  controller returns `completed_count + 1`.
- **Rejected:** Accept empty local metadata after remote success as long as the
  controller only reached remote validation because diagnostics existed.
  Rejected because this is the same inconsistency class as partial-tail state,
  just with zero local keys instead of a short prefix.
- **Implication:** The final spec should define the logic as:
  clean empty store with no diagnostics fast-paths to `1`;
  every other state goes remote and then must satisfy the exact shared
  consistency invariant.
- **Trade-offs:** This makes the logic slightly less intuitive than a
  three-table design, because the empty case is split between pre-remote and
  post-remote handling.
- **Confidence:** High (E2) — based on adversarial reasoning against the `v2`
  table and consistency with the existing `read()` semantics.
- **Reversibility:** High — this is a spec-level correction before code exists.
- **Change trigger:** Reconsider only if the project explicitly wants a
  recovery-like repair flow inside `_next_turn_sequence()`, which was not part
  of the ticket as discussed here.

## Changes

No production code, tests, docs, or tickets were edited during the substantive
design-review part of this session.

The repository stayed on `main` and remained clean throughout the analysis.

No branch was created.
No implementation was started.
No tests were run.

The only artifact created at session end is this handoff file:
`docs/handoffs/2026-04-12_01-40_t-20260410-02-design-review-complete-spec-draft-next.md`.

That means future work starts from a pure design checkpoint, not a partially
implemented branch.

This is useful because the next session can evaluate the user’s spec draft on
its own terms, without disentangling incomplete code from incomplete design.

## Codebase Knowledge

### Files read and why

| File | Why it was read | What it established |
|---|---|---|
| `docs/tickets/2026-04-10-T-20260410-02-...` | Anchor the problem statement and acceptance criteria | The ticket is about hardening the empty fast path, corruption/gap handling, and error-context surfacing; see `:18-32` |
| `packages/plugins/codex-collaboration/server/dialogue.py` | Understand the actual turn-sequence logic and adjacent invariants | `reply()` derives `turn_sequence` before journaling at `:351-389`; `_next_turn_sequence()` is minimal at `:725-753`; `read()` is strict at `:853-862`; `recover_startup()` is looser at `:526-539` |
| `packages/plugins/codex-collaboration/server/turn_store.py` | See what persistence APIs already exist | `get_all()` hides diagnostics at `:63-69`; `check_health()` exposes them separately at `:73-75` |
| `packages/plugins/codex-collaboration/server/replay.py` | Understand corruption classification semantics | Diagnostics are structured and file-global at `:26-51`; `has_warnings` excludes pure trailing truncation |
| `packages/plugins/codex-collaboration/server/mcp_server.py` | Verify dialogue is part of the live MCP surface | Serialized dispatch is explicit; dialogue tools are already exposed; see `:1-16` and `:204-233` |
| `packages/plugins/codex-collaboration/tests/test_dialogue.py` | Map current coverage and missing cases | First-turn happy path is locked in at `:1842-1871`; second-turn remote fallback at `:1873-1909`; read-integrity failures around `:1048-1086` |
| `packages/plugins/codex-collaboration/tests/test_turn_store.py` | Check existing store-test style and available seams | Store tests already cover malformed records and `check_health()` diagnostics |
| `packages/plugins/codex-collaboration/tests/test_control_plane.py` | Understand fake runtime behavior used by dialogue tests | `read_thread()` reflects `completed_turn_count` by default at `:125-137`, which encodes the thread-materialization model |
| `packages/plugins/codex-collaboration/README.md` | Place the ticket in the broader plugin surface | The package already presents consultation and dialogue as a plugin capability at `:16-63` |
| `docs/superpowers/specs/codex-collaboration/contracts.md` | Check the normative recovery predicate | Eligible unknown handles require zero completed turns or complete TurnStore metadata at `:154-165` |
| `docs/superpowers/specs/codex-collaboration/delivery.md` | Place the work inside the project arc | R2 dialogue foundation is already in scope and implemented at `:205-245` |
| `docs/tickets/2026-03-30-codex-collaboration-plugin-shell-and-consult-parity.md` | Compare the old packet framing to the current tree | Ticket still describes packaging as future work even though the current package now contains those artifacts |
| `docs/tickets/2026-04-10-dialogue-codex-turn-semantics-clarification.md` | Understand adjacent dialogue hardening work | Confirms there is still active contract-shaping work around the dialogue tooling |
| `packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md` | See who depends on the dialogue path | The B1 harness spawns a dialogue workflow that depends on the dialogue surface remaining stable |
| `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md` | Understand the dialogue consumer contract | Downstream workflow assumes `codex.dialogue.start`, `.reply`, and `.read` are operational and trustworthy |
| `packages/plugins/codex-collaboration/agents/shakedown-dialogue.md` | Confirm the agent-level dependency on dialogue tools | The shakedown agent is built directly on the codex-collaboration dialogue tools |

### Architecture mapped for this area

| Component | Responsibility | Evidence |
|---|---|---|
| `McpServer` | Synchronous tool dispatch, serialization chokepoint | `packages/plugins/codex-collaboration/server/mcp_server.py:204-233` |
| `DialogueController.reply()` | Main turn-dispatch orchestration | `packages/plugins/codex-collaboration/server/dialogue.py:351-389` |
| `_next_turn_sequence()` | Local fast path plus remote fallback for determining next turn number | `packages/plugins/codex-collaboration/server/dialogue.py:725-753` |
| `TurnStore` | Session-scoped append-only metadata store for `context_size` by turn | `packages/plugins/codex-collaboration/server/turn_store.py:32-80` |
| `replay_jsonl()` | Shared corruption-tolerant replay and diagnostics engine | `packages/plugins/codex-collaboration/server/replay.py:26-51` |
| `read()` | Remote-authoritative read path with strict metadata join | `packages/plugins/codex-collaboration/server/dialogue.py:812-875` |
| `recover_startup()` | Startup reattach and integrity screening for active/unknown handles | `packages/plugins/codex-collaboration/server/dialogue.py:507-548` |
| `FakeRuntimeSession` | Test double modeling start/run/read/resume behavior | `packages/plugins/codex-collaboration/tests/test_control_plane.py:26-141` |

### Dependency graph for the hardening work

| Entry point | Depends on | Why it matters to `T-20260410-02` |
|---|---|---|
| `codex.dialogue.reply` | `McpServer` → `DialogueController.reply()` → `_next_turn_sequence()` | The ticket changes this path directly |
| `_next_turn_sequence()` | `TurnStore.get_all()` today; `TurnStore.get_all_checked()` in the proposed design | The API seam for diagnostics lives here |
| Remote fallback | `runtime.session.read_thread()` | Needed once the local fast path is distrusted |
| Read integrity | `DialogueController.read()` + `TurnStore.get_all()` | Existing strictness here defines the consistency bar future logic should match |
| Recovery integrity | `recover_startup()` + `TurnStore.get_all()` + remote completed count | Needs the same consistency invariant if the design is to be internally coherent |

### Conventions observed

- Error messages in this area use the repo’s standard
  `"... failed: ... Got: ..."` pattern in several places, including
  `reply()` validation errors at
  `packages/plugins/codex-collaboration/server/dialogue.py:339-345`
  and recovery logging via `_log_recovery_failure()` at `:57-61`.
- The dialogue controller prefers fail-fast integrity boundaries over silent
  healing in read paths; see `read()` throwing on missing metadata at
  `packages/plugins/codex-collaboration/server/dialogue.py:853-862`.
- Tests in `test_dialogue.py` are organized around behavior clusters rather than
  helper-private unit tests only:
  `TestDialogueReply`,
  `TestRecoverPendingOperations`,
  `TestBestEffortRepairTurn`,
  `TestFirstTurnFastPath`,
  and others.
- The package treats dialogue state as session-scoped.
  README states that lineage, journal, and turn metadata are session-scoped at
  `packages/plugins/codex-collaboration/README.md:61-63`.
- Serialized dispatch remains a load-bearing assumption.
  The delivery spec calls it out at
  `docs/superpowers/specs/codex-collaboration/delivery.md:211-218`,
  and the MCP server repeats it in code comments and structure.

### Surprises and counter-intuitive findings

- The package is more mature than some older ticket/spec text suggests.
  The current tree already contains `.claude-plugin/plugin.json` and `.mcp.json`
  even though older packet language still talks about plugin shell work as open.
- The replay layer is not the missing piece.
  Diagnostics already exist; the controller just does not consume them.
- `recover_startup()` is currently weaker than `read()` in a very specific way:
  it checks cardinality, not exact sequence-set consistency.
- The first-turn optimization is not just a micro-optimization.
  It is coupled to avoiding premature `read_thread()` on a thread that may not
  yet be materialized.
  That is why the existing happy-path test is important and should not be
  casually replaced.

### Key locations future Codex should know immediately

- `_next_turn_sequence()`: `packages/plugins/codex-collaboration/server/dialogue.py:725-753`
- `reply()` call site: `packages/plugins/codex-collaboration/server/dialogue.py:351-389`
- `read()` integrity enforcement: `packages/plugins/codex-collaboration/server/dialogue.py:853-862`
- `recover_startup()` metadata eligibility check:
  `packages/plugins/codex-collaboration/server/dialogue.py:526-539`
- `TurnStore` store APIs: `packages/plugins/codex-collaboration/server/turn_store.py:32-80`
- Replay diagnostics semantics: `packages/plugins/codex-collaboration/server/replay.py:26-51`
- Happy-path fast-path test:
  `packages/plugins/codex-collaboration/tests/test_dialogue.py:1842-1871`
- Fake runtime `read_thread()` semantics:
  `packages/plugins/codex-collaboration/tests/test_control_plane.py:125-137`

## Conversation Highlights

Several user messages materially shaped the session.

The orientation request was explicit and scoped:

> "Read each of the relevant files for `T-20260410-02` to orient yourself and
> understand this work and its context within the larger codex-collaboration
> Claude Code plugin build."

That prevented any premature implementation.

The first design-evaluation prompt forced a comparative read rather than a
single-path endorsement:

> "What's your read?"

The tone then sharpened around review quality rather than speed:

> "Excellent analysis. You've refined the design significantly — B with
> controller-side structural checks is clearly the right shape."

And then:

> "Probe this for gaps. Really scrutinize this - I want to catch problems early."

This is not generic encouragement.
It is a direct quality bar:
the user wants adversarial review before spec writing.

The final session boundary was also explicit:

> "Save a handoff. I will write the spec and then share it with you in the next
> session to review"

That establishes the next-session contract clearly:
review the user’s spec draft,
do not assume implementation work begins immediately.

## User Preferences

The user showed several stable preferences in this session.

- They want read-first orientation when a ticket needs context before design:
  "Read each of the relevant files..."
- They value comparative design analysis over one-shot recommendations when the
  implementation shape is still open:
  "What's your read?"
- They explicitly reward scrutiny and want weak points identified before spec
  freeze:
  "Probe this for gaps. Really scrutinize this - I want to catch problems early."
- They are comfortable separating design/spec work from implementation work.
  This session ended at the handoff/spec boundary by design.
- They want the next session to begin by reviewing their written spec, not by
  rediscovering the design discussion:
  "I will write the spec and then share it with you in the next session to review"

Future Codex should match that preference by:
- reading the user’s spec carefully first
- checking it against the specific design corrections captured here
- only proposing implementation after the spec is internally coherent

## Context

### Repository state at session end

- Branch: `main`
- Commit: `7f7cbfc6`
- Working tree: clean
- Upstream relation: `main...origin/main` with no local modifications shown by
  `git status --short --branch`
- No feature branch in flight

### Current task context

This session did not advance `T-20260410-02` in code.
It advanced it in design certainty.

The ticket remains deferred in its frontmatter at
`docs/tickets/2026-04-10-T-20260410-02-...:4-12`.

The current branch field inside that ticket,
`feature/b4-agent-skill-harness-assembly`,
is stale and should not be reused automatically for future implementation.

### Mental model

The right framing for the bug is:
this is a trust-boundary problem around turn-sequence derivation,
not a replay-library bug and not a broad crash-recovery redesign.

`_next_turn_sequence()` currently collapses two different states into one:
- legitimately empty first-turn metadata
- unreadable or structurally suspect local metadata that happens to replay to
  empty

The hardening work is about separating those states without regressing the
verified healthy fast path.

The deeper model is:
once the controller has asked the remote thread for authoritative completed-turn
count, local metadata is no longer just a hint.
It becomes an integrity subject that must agree with the remote count.

### Placement within the larger codex-collaboration build

The codex-collaboration package already advertises dialogue as part of its
plugin surface in the README at `packages/plugins/codex-collaboration/README.md:52-63`.

The plugin artifacts also exist in-tree:
- plugin metadata at `.claude-plugin/plugin.json:1-10`
- MCP launch config at `.mcp.json:1-17`

That means this ticket affects a live subsystem that already has:
- a packaged shape
- exposed MCP dialogue tools
- downstream shakedown workflows depending on those tools

### Environment assumptions relevant to this ticket

- serialized MCP dispatch is still assumed
- advisory runtime is read-only
- session identity is session-scoped
- dialogue state stores are session-partitioned append-only JSONL

None of those assumptions were challenged in this session.

## Learnings

### Learning 1: The real seam is "results plus diagnostics," not "diagnostics only"

The replay engine is already capable of classifying corruption.
The missing capability is a single-pass store API that lets the controller see
both the filtered local state and the replay diagnostics together.

Evidence:
`TurnStore.get_all()` returns only filtered results at
`packages/plugins/codex-collaboration/server/turn_store.py:63-69`,
while `check_health()` returns diagnostics separately at `:73-75`.

Implication:
the best implementation seam is additive, not architectural.

### Learning 2: `read()` already defines the stricter integrity bar future logic should honor

The design question is not being answered in a vacuum.
`DialogueController.read()` already throws if a completed remote turn has no
local metadata entry at
`packages/plugins/codex-collaboration/server/dialogue.py:853-862`.

Implication:
new turn-sequence logic should avoid creating or tolerating states that the read
path already defines as invalid.

### Learning 3: Cardinality-only recovery checks are too weak

`recover_startup()` currently checks only `len(metadata) < completed_count` at
`packages/plugins/codex-collaboration/server/dialogue.py:533-539`.

That misses:
- gapped metadata with equal cardinality
- extra local metadata

Implication:
if the implementation only hardens `_next_turn_sequence()` and does not update
`recover_startup()`, the subsystem keeps two incompatible notions of
"metadata is complete enough."

### Learning 4: The subtle remaining bug in `v2` is the empty-plus-diagnostics-plus-remote-success case

The user’s `v2` already fixed most of the earlier issues.

The remaining bug is not obvious because it lives at the intersection of:
- diagnostics present
- local metadata empty
- remote read succeeds
- remote reports completed turns

That case must fail consistency, not return `completed_count + 1`.

Implication:
the final spec needs one more tightening pass before implementation.

## Next Steps

### 1. User writes the formal spec for `T-20260410-02`

This is the immediate next action the user already committed to.

Future Codex should expect to receive a draft spec, not a request to start
coding blindly.

When reviewing the spec, check first for these exact points:
- does it use an additive `get_all_checked()`-style API rather than A or C?
- does it define diagnostics as file-global and fail-closed?
- does it use one shared consistency invariant across `_next_turn_sequence()`
  and `recover_startup()`?
- does it reject non-empty inconsistent local metadata before dispatch?
- does it close the empty-plus-diagnostics-plus-remote-success hole?

### 2. Review whether confirmed inconsistency should also quarantine the handle

This was recommended but not fully locked as a final design decision.

Current recommendation:
if remote read succeeds and local metadata is inconsistent with the returned
`completed_count`,
consider moving the handle to `unknown` before raising.

What to read first:
`packages/plugins/codex-collaboration/server/dialogue.py:510-548`
and the existing quarantine behavior in other reply/recovery failure paths.

### 3. After spec approval, implement in a new fix branch from `main`

The ticket’s stored branch name is stale.

Suggested branch shape:
`fix/t02-dialogue-first-turn-hardening`

Implementation files are expected to be:
- `packages/plugins/codex-collaboration/server/turn_store.py`
- `packages/plugins/codex-collaboration/server/dialogue.py`
- `packages/plugins/codex-collaboration/tests/test_turn_store.py`
- `packages/plugins/codex-collaboration/tests/test_dialogue.py`

Verification should include:
- targeted test coverage for corrupt-empty and remote-failure cases
- targeted recovery coverage for gapped metadata
- likely the full `test_dialogue.py` and `test_turn_store.py` slices

## In Progress

Clean stopping point.

- No implementation is in flight.
- No files are partially edited.
- No branch exists for this work yet.
- The active artifact is the design discussion summarized in this handoff.

Immediate next action for the next session:
read the user’s spec draft and review it against the decisions and gaps
captured here.

## Open Questions

### 1. Should a confirmed local/remote inconsistency set the handle to `unknown` before raising?

There is a good case for doing so.

Reason:
the system already uses `unknown` to quarantine ambiguous or unrecoverable
dialogue state in other paths.

But this was not finalized in-session as a required part of the design.

### 2. How explicit should the error wording be about file-global vs collaboration-local ambiguity?

Current recommendation is to avoid wording that overclaims collaboration-local
certainty.

Better wording:
`session turn metadata file has replay diagnostics (...)`

Weaker wording to avoid:
`local turn metadata for this collaboration is ambiguous`

### 3. Should the final spec treat "remote says zero completed turns" after diagnostics-forced fallback as fully acceptable?

Current recommendation: yes.

That case is consistent with the shared invariant because empty local metadata
matches `completed_count == 0`.

But the spec should say that explicitly so future reviewers do not confuse it
with the rejected positive-completed-count case.

## Risks

### 1. The user’s spec could preserve the old `v2` Phase 3 table and leave the subtle hole intact

This is the highest immediate risk.

If the spec says empty local metadata is "n/a" after remote success,
the controller could still advance past a corrupted-empty local state when the
remote shows completed turns.

### 2. File-global diagnostics create a deliberate blast radius

A corrupt record from another collaboration in the same session file can disable
the otherwise-empty fast path for this collaboration.

This is probably the correct trade-off today,
but it should be called out plainly in the spec and tests.

### 3. Recovery and reply can drift again if only one path gets the stronger invariant

If implementation hardens `_next_turn_sequence()` but leaves
`recover_startup()` on cardinality-only checks,
future behavior will remain internally inconsistent.

## References

### Primary ticket

- `docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md:18-32`

### Core implementation

- `packages/plugins/codex-collaboration/server/dialogue.py:351-389`
- `packages/plugins/codex-collaboration/server/dialogue.py:725-753`
- `packages/plugins/codex-collaboration/server/dialogue.py:812-875`
- `packages/plugins/codex-collaboration/server/dialogue.py:853-862`
- `packages/plugins/codex-collaboration/server/dialogue.py:526-539`
- `packages/plugins/codex-collaboration/server/turn_store.py:32-80`
- `packages/plugins/codex-collaboration/server/replay.py:26-51`
- `packages/plugins/codex-collaboration/server/mcp_server.py:204-233`

### Test surface

- `packages/plugins/codex-collaboration/tests/test_dialogue.py:1048-1086`
- `packages/plugins/codex-collaboration/tests/test_dialogue.py:1842-1909`
- `packages/plugins/codex-collaboration/tests/test_turn_store.py:1-166`
- `packages/plugins/codex-collaboration/tests/test_control_plane.py:26-141`

### Broader package/spec context

- `packages/plugins/codex-collaboration/README.md:16-63`
- `packages/plugins/codex-collaboration/.claude-plugin/plugin.json:1-10`
- `packages/plugins/codex-collaboration/.mcp.json:1-17`
- `docs/superpowers/specs/codex-collaboration/contracts.md:154-165`
- `docs/superpowers/specs/codex-collaboration/delivery.md:205-245`
- `docs/tickets/2026-03-30-codex-collaboration-plugin-shell-and-consult-parity.md`
- `docs/tickets/2026-04-10-dialogue-codex-turn-semantics-clarification.md`

## Gotchas

- The handoff plugin’s generic storage contract talks about `~/.codex/handoffs`,
  but this repository uses `docs/handoffs/` and `docs/handoffs/archive/` as
  durable project artifacts.
  Follow the repo pattern here.
- The current package tree contains packaged-plugin artifacts even though some
  older tickets/spec text still talk as if packaging is future work.
  Do not assume older packet language exactly matches the live tree.
- `ReplayDiagnostics.has_warnings` is the wrong threshold for this ticket.
  A pure `trailing_truncation` can still invalidate the proof that a
  collaboration has zero completed turns.
- Contiguity by itself is not enough.
  `{1}` is contiguous but still inconsistent if the remote says two completed
  turns exist.
- The next session should begin with spec review, not code changes.
  That sequencing was explicitly set by the user at the end of this session.
