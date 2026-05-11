---
date: 2026-04-23
time: "15:54"
created_at: "2026-04-23T15:54:31Z"
session_id: ca490f66-ea66-4599-992d-9c14806af5f7
resumed_from: "docs/handoffs/archive/2026-04-23_02-09_delegate-sandbox-state-machine-fix.md"
project: claude-code-tool-dev
branch: feature/delegate-remediation-sandbox-approval
commit: fb73f10d
title: "Delegate state-machine remediation — partial hardening PR #125"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/execution_prompt_builder.py
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/skills/delegate/SKILL.md
  - docs/superpowers/specs/codex-collaboration/promotion-protocol.md
  - docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md
  - docs/plans/2026-04-23-delegate-remediation-implementation.md
---

# Handoff: Delegate state-machine remediation — partial hardening PR #125

## Goal

Close out the delegate execution remediation (T-20260423-01) by completing the handoff's deferred steps: run live smoke to validate the state-machine fix end-to-end, then commit and publish the branch. The predecessor session had written and unit-tested the code (913 tests passing) but was blocked by a stale MCP server holding old code in memory.

**Trigger:** Predecessor handoff read: "live smoke cannot be verified this session — MCP server has old code. Stuck job c382b5dc blocks new delegations via busy gate." The restart-MCP requirement is structural — every plugin code change requires a fresh session to take effect.

**Stakes:** High — delegate is a foundational capability for the codex-collaboration plugin and cannot ship without state-machine correctness. The remediation had landed in code but was unproven in live operation.

**Success criteria:**
- Verify busy gate is clear in the new session
- Run live smoke and observe Option B firing correctly (empty `available_decisions` → `failed`, not stuck `needs_escalation`)
- Verify discard clears busy gate after failure
- Commit and publish a PR with honest framing of what's delivered vs deferred

**Connection to project arc:** This session closes the acute remediation work for delegate. End-to-end happy-path delegation remains blocked by exec-policy gaps (deferred). The exec-policy design is the next packet of work and intentionally deferred to a fresh session to avoid scope blur.

## Session Narrative

### 1. Resume and state discovery

Session began with `/load`, pulling the predecessor handoff `2026-04-23_02-09_delegate-sandbox-state-machine-fix.md`. Confirmed expectations: 913 tests passing, Options A+B implemented in `delegation_controller.py`, execution prompt tuned, live smoke blocked by stale MCP code.

First action was the handoff's step 1: run `/delegate` (bare) to see current state. `codex.status` returned `active_delegation: null` — a surprise, because the predecessor's stuck job `c382b5dc` was expected to still be holding the busy gate. Investigation revealed:

- Job store is on disk at `~/.claude/plugins/data/codex-collaboration-inline/delegation_jobs/<session_id>/jobs.jsonl`.
- The stuck job was in session `40271cdd-...` (the predecessor's session). Current session is `ca490f66-...`.
- Session-scoped job store means the current controller cannot see the old session's jobs (`poll` returned `job_not_found`).
- MCP restart cleared the in-memory runtime registry and `_decided_request_ids` set, resolving the "busy gate" concern entirely for the current session.

This invalidated the handoff's step 1 (discard stuck job) as unnecessary — the fresh session was self-isolating.

### 2. Pre-smoke doc review from user

Before proceeding to smoke, user returned with two P2 findings from independent code review of the branch:

1. `SKILL.md:296` and `promotion-protocol.md:140-144` still described the old discard predicate, missing the new `needs_escalation + null` entry that `delegation_controller.py:1409` now admits.
2. Ticket acceptance criteria still read like generic "simple repo edit" support, not recording that `execution_prompt_builder.py:40-43` now restricts delegated workers to `/bin` and `/usr/bin` tools.

User's framing: "contract drift" — operator-facing documentation out of sync with the new runtime contract. Fixed all three by explicit edits:

- **SKILL.md:** extended the "allowed states" sentence to include `status == "needs_escalation"` with null `promotion_state` and an inline note about the cleanup semantics.
- **promotion-protocol.md:** restructured Discard Semantics as bulleted allowed states + "Simple path" vs "Cleanup path" sub-sections that match the implementation's two code paths.
- **Ticket:** scoped AC1 to platform-default tools; added a new **Scope limitations** section explicitly naming the exec-policy deferral with its design questions.

### 3. Live smoke #3

With docs aligned, ran the handoff-specified smoke: `/delegate Create docs/scratch/T-20260423-01-smoke.md with heading "Delegate Smoke Test" and one sentence with today's date.`

Job `191ec8d6-31c3-4265-b8d2-70b3adb5b82d` was created and returned immediately with `status: "failed", promotion_state: null`, `artifact_paths` populated. This matched Option B's expected behavior: the job didn't get stuck in `needs_escalation`.

Inspected artifacts: `full.diff` showed the agent had created the file correctly with exact content:
```
# Delegate Smoke Test

This smoke test was created on 2026-04-23.
```

So the agent successfully wrote the requested file in the worktree — but the job still finalized as `failed`. To trace why, read `delegation_jobs/<session_id>/jobs.jsonl` and `pending_requests/<session_id>/requests.jsonl`.

### 4. Discovery: shell wrapper is the real exec-policy blocker

Raw pending-request payload showed:

```json
{
  "available_decisions": [],
  "kind": "command_approval",
  "request_id": "1",
  "requested_scope": {
    "command": "/bin/zsh -lc '/bin/test -f docs/scratch/T-20260423-01-smoke.md'",
    "proposedExecpolicyAmendment": ["/bin/test", "-f", "docs/scratch/T-20260423-01-smoke.md"]
  }
}
```

The agent's final self-verification was `test -f <file>` — wrapped in `/bin/zsh -lc '...'`. Codex invokes every command through a login shell wrapper. The sandbox flags the wrapper, not the target binary. Even though `/bin/test` is in platform defaults, wrapping it in `/bin/zsh -lc` triggers `command_approval`.

This reframed the exec-policy gap: not "certain tools aren't available" but "every command goes through a login shell wrapper, and the wrapper itself is exec-policy-suspect."

Key understanding shift: the handoff's D1 decision (prompt tuning for platform tools) was necessary but insufficient. Even with perfect tool constraints, delegated work cannot complete because the execution vehicle (`/bin/zsh -lc`) is blocked. Exec-policy widening is load-bearing for any successful delegation, not just objectives that structurally need developer tools.

### 5. Validating simple discard + busy gate clearance

With the job `failed + null`, status became `attention-active` (failed + null is in the widened busy gate by spec). Called `codex.delegate.discard` on job `191ec8d6`. Result: transitioned cleanly to `failed + discarded` via the simple flag-flip path. Follow-up status check: `active_delegation: null`. Busy gate cleared immediately.

### 6. Publication planning

Reported findings and proposed three commit strategies (A bundle / B split / C stop-for-review). User chose C: stop for review. Reviewed the diff themselves, then returned with clear final recommendation:

- Publish as partial hardening, not ticket closure
- Keep ticket open (AC1 not actually met — shell wrapper is the real obstacle)
- Either amend AC5 or call out in PR that `failed + null` is a new legitimate terminal state
- For the scratch diagnostic: distill to real decision record OR put raw payload in PR description
- Start exec-policy design in fresh session

### 7. Distillation attempt, discovery, pivot

Wrote a full decision record at `docs/decisions/2026-04-23-delegate-stuck-escalation-state-machine.md` following the existing repo format (Decision, Stakes, Options, Evaluation, Validation, Follow-ups). After writing, git status didn't show the file. `git check-ignore -v` revealed `.gitignore:20: docs/decisions/` — the entire directory is gitignored.

Further investigation: 8 tracked files in the directory are pre-gitignore historical records; 4 untracked. The "established Decision Record pattern" is actually a local-only scratch convention. The canonical tracked decisions file for codex-collaboration is `docs/superpowers/specs/codex-collaboration/decisions.md` (frontmattered `authority: decisions`, normative spec).

Pivoted: user's "otherwise put in PR description" branch of their option tree became the right move. Trashed the untracked decision record. Embedded the full decision record content in the PR body instead — durable at merge time, doesn't need a new tracked file location invented.

### 8. AC amendments + commit + publish

Final ticket edits:
- **AC1:** explicit note that as of 2026-04-23 this criterion is not met; root cause stated (`/bin/zsh -lc` wrapper triggers amendment even for `/bin`/`/usr/bin` binaries).
- **AC5:** expanded from two-option dichotomy (successful promotion / promotion rejection) to three options: adds "(c) typed pre-promotion job failure (`status="failed"` with `promotion_state=null`)" with full cleanup as a valid terminal state for deferred-scope operations.

Re-ran tests: 913 passing. Staged 15 files explicitly (no `git add -A` per CLAUDE.md safety). Committed `fb73f10d` with detailed message framing scope and deferral. Pushed to remote, opened PR #125 with comprehensive body including the distilled decision record, raw wire evidence, live validation narrative, follow-up list.

## Decisions

### D1: Fix contract drift inline (SKILL.md + promotion-protocol.md + ticket) before proceeding to smoke

**Choice:** Resolve all three P2 doc-drift findings before running live smoke. Treat them as blockers on PR publication, not as post-smoke cleanup.

**Driver:** User framed them as "contract drift" — documentation out of sync with implementation in a merge-relevant way. Quote: "That leaves the written operator contract out of sync with the exact recovery path this patch adds."

**Rejected:** Defer docs to a follow-up PR — rejected because the PR would then advertise a contract that the docs don't describe, creating a merge-time readability hazard for reviewers.

**Implication:** Documentation and implementation land in the same commit. Future readers of `SKILL.md:296` or `promotion-protocol.md:140-150` see the same contract that `delegation_controller.py:1409-1456` implements.

**Trade-offs:** Slightly larger diff in the PR. Accepted — the doc changes are ~30 lines across 3 files, small relative to the code delta.

**Confidence:** High (E2) — user explicitly flagged them as P2 with specific line references and priority metadata.

**Reversibility:** High — doc-only changes.

**Change trigger:** Would only matter if a reviewer disagrees with the new contract shape itself (not just the doc wording), forcing a re-design.

### D2: Distill scratch diagnostic into PR body, not a tracked decision record

**Choice:** Remove the untracked scratch file and the (also-untracked) decision record I wrote. Put the distilled decision record content in the PR description.

**Driver:** Discovery that `docs/decisions/` is gitignored in this repo (`.gitignore:20`). The user's guidance assumed a tracked decision-record pattern; the pattern is actually local-only. User quote: "If you want it durable in-tree, distill it into a real decision record; otherwise put the raw payload evidence in the PR description."

**Rejected:**
- **Move to `docs/plans/`** — plans and decision records have different semantics; forcing a mismatch.
- **Add to `decisions.md` (normative spec)** — too heavy for a post-hoc implementation record; would mutate a normative spec doc for content that's really a changelog-level artifact.
- **Commit to `docs/decisions/` with forced add** — would violate the gitignore intent; the directory is deliberately local-only.

**Implication:** The decision record content is durable at merge time (PR body is preserved by GitHub), discoverable via PR search and commit metadata. If future-Claude wants to find the reasoning behind Options A+B, the commit message + PR body is authoritative.

**Trade-offs:** Less grep-able than an in-tree file. Accepted because the PR is linked from the ticket (T-20260423-01), which is in-tree, so discovery path remains intact.

**Confidence:** High (E2) — verified gitignore behavior directly with `git check-ignore -v`.

**Reversibility:** Low-medium — once the PR is merged, promoting the content back into the tree requires a new commit. But the content itself is preserved in the PR body verbatim.

**Change trigger:** If the repo adopts a tracked decision-record convention (e.g., remove `docs/decisions/` from `.gitignore`), re-promote the PR body content to a tracked file.

### D3: Single bundled commit vs split commits — chose single

**Choice:** One commit (`fb73f10d`) containing all 15 file changes (code, tests, docs, plan, contract).

**Driver:** The changes are a coherent remediation: state-machine fixes + sandbox support + prompt tuning + doc alignment. They share context (T-20260423-01) and rationale. Splitting would create commits that only make sense together.

**Rejected:** Split into logical slices (sandbox-roots / state-machine / doc-alignment) — viable but adds complexity without bisect value; bisecting through the middle of this remediation wouldn't yield a runnable intermediate state.

**Implication:** PR #125 is reviewed as a single coherent unit. If reverted, reverts as a unit.

**Trade-offs:** Larger single diff to review (+2070/-145). Accepted because the tests carry most of the line count (1000+ in test_delegation_controller.py) and the source changes are narrow.

**Confidence:** High (E1) — user didn't push back on the single-commit choice when offered A/B/C.

**Reversibility:** Medium — could split on a follow-up branch before merge if reviewer requests.

**Change trigger:** Reviewer requests splitting for bisect clarity or separate-author attribution.

### D4: Amend AC5 to admit `failed + null promotion_state` as a valid terminal state

**Choice:** Replace AC5's two-option dichotomy with three options, explicitly naming `(c) typed pre-promotion job failure` with runtime released, session closed, lineage completed, and artifacts materialized.

**Driver:** User stated: "live validation now includes a legitimate pre-promotion terminal state, `failed + null promotion_state`, for no-decision exec-policy failures. As written, AC5 is too narrow for the state machine you now intentionally support."

**Rejected:** Leave AC5 as-is and only call out in PR body — rejected because the ticket is a persistent contract; relying on PR body alone lets the criterion rot into an inaccurate reference.

**Implication:** The ticket now accurately describes the post-fix contract. A future closeout reviewer reading AC5 sees that `failed + null` is an expected terminal state, not a regression.

**Trade-offs:** Slightly longer AC5. Accepted — 6 lines to avoid the contract misstatement is cheap.

**Confidence:** High (E2) — user explicitly proposed this amendment.

**Reversibility:** High — doc-only.

**Change trigger:** If the state machine evolves to eliminate the `failed + null` path entirely, re-tighten AC5.

## Changes

### `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` — AC1 + AC5 amendments

**Purpose:** Align acceptance criteria with post-fix contract; name the real obstacle for AC1.

**Approach:** Two `Edit` operations. AC1 gets an explicit "as of 2026-04-23 this criterion is not met" note naming `/bin/zsh -lc` wrapper as the blocker. AC5 expands from `(a) successful promotion | (b) typed promotion rejection` to add `(c) typed pre-promotion job failure (status="failed" with promotion_state=null)`.

**Future-Claude note:** Do NOT remove the AC1 note until exec-policy support lands. The note is the honest signal that ticket closure is not imminent.

### `packages/plugins/codex-collaboration/skills/delegate/SKILL.md:296` — Discard rejection guidance

**Purpose:** Align operator-facing documentation with the new discard gate.

**Approach:** Single-line edit appending `, or status == "needs_escalation" with null promotion_state (stuck-escalation cleanup — atomically transitions the job to failed + discarded, releases the runtime, closes the session, and completes lineage)` to the existing allowed-states sentence.

**Future-Claude note:** The inline cleanup semantics note is there to prevent operators from expecting a simple flag-flip when this path fires — audit events look different.

### `docs/superpowers/specs/codex-collaboration/promotion-protocol.md:140-150` — Discard Semantics section

**Purpose:** Normative spec update to describe the two discard code paths.

**Approach:** Restructured "Allowed states" as a bulleted list including the new `needs_escalation` entry. Added a rationale sentence for why `needs_escalation + null` is admitted ("still owns a live runtime, so the cleanup path is required to release resources that deny-based finalization would otherwise handle"). Split the post-"Discard emits" paragraph into two sub-bullets: "Simple path" and "Cleanup path" — each naming the exact state-machine mutations and resource operations.

**Future-Claude note:** This is the authoritative protocol contract. If the discard logic changes further, update this file first.

### (From predecessor session — unchanged in this session but now published)

- `server/delegation_controller.py` — Options A + B logic, ~132 line delta.
- `server/execution_prompt_builder.py` — worktree-boundary + platform-tool constraints added to execution-turn prompt.
- `server/runtime.py` — sandbox support roots (`_resolve_codex_support_roots`, `_CODEX_SUPPORT_READ_SUBROOTS`).
- `server/approval_router.py` — wire decision normalization (`_resolve_available_decisions`).
- `server/models.py` — supporting shape change.
- `tests/test_delegation_controller.py` — 7 new scenario tests + 1 update, ~1023 line delta.
- `tests/test_runtime.py`, `tests/test_approval_router.py`, `tests/test_delegate_start_integration.py` — test support.
- `docs/plans/2026-04-23-delegate-remediation-implementation.md` — implementation plan artifact (new, committed).
- `docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md`, `docs/superpowers/specs/codex-collaboration/contracts.md` — minor spec touchups.

## Codebase Knowledge

### Session-scoped data stores

| Store | Path | Scope | Observations |
|-------|------|-------|--------------|
| Job store | `plugins/data/codex-collaboration-inline/delegation_jobs/<session_id>/jobs.jsonl` | Per MCP session | Jobs from dead sessions are structurally unreachable to new sessions via `poll` (returns `job_not_found`). |
| Pending request store | `plugins/data/codex-collaboration-inline/pending_requests/<session_id>/requests.jsonl` | Per MCP session | Raw wire payloads. **The only source of truth for `available_decisions`** — the operator view is projected. |
| Runtime registry | In-memory | Per MCP process | Cleared on MCP restart. This is why the predecessor's stuck job didn't block the new session. |
| Worktrees | `plugins/data/codex-collaboration-inline/runtimes/delegation/<job_id>/worktree` | Git-managed | Persist across MCP restarts. Orphan cleanup requires separate tooling. |

### Projection layer — operator view vs wire truth

`_project_request_to_view` at `delegation_controller.py:864-878` forces `_DENY_ONLY_DECISIONS = ("deny",)` for all `_CANCEL_CAPABLE_KINDS = {"command_approval", "file_change"}`. This means:

- Operator sees `available_decisions: ["deny"]`.
- Wire may actually be `[]` (empty), `["decline", "cancel"]`, or anything else.
- **Diagnostic rule:** For any cancel-capable escalation, always inspect `pending_requests/<session_id>/requests.jsonl` for the raw payload. The operator view is lossy.

### State machine post-fix (authoritative)

| Wire signal | `_finalize_turn` status | User-facing |
|-------------|------------------------|-------------|
| `command_approval`, `available_decisions: ["decline", "cancel"]` | `needs_escalation` | Projected `("deny",)` |
| `command_approval`, `available_decisions: []` | **`failed` (NEW)** | Plain `DelegationJob`, `promotion_state=null` |
| `file_change`, `available_decisions: []` | **`failed` (NEW)** | Plain `DelegationJob`, `promotion_state=null` |
| `interrupted_by_unknown` | `needs_escalation` | Projected `("approve", "deny")` |

### Discard gate post-fix

| State | Path | Effect |
|-------|------|--------|
| `promotion_state in {pending, prechecks_failed}` | Simple flag-flip | `promotion_state → discarded` |
| `status in {failed, unknown}` + `promotion_state is None` | Simple flag-flip | `promotion_state → discarded` |
| `status == needs_escalation` + `promotion_state is None` | **Cleanup path (NEW)** | Atomic `status → failed, promotion_state → discarded`, runtime release, session close, lineage complete, terminal outcome emit |
| `prechecks_passed`, `applied`, `verified`, `rollback_needed`, `rolled_back`, `discarded` | Rejected | `job_not_discardable` |

### `docs/decisions/` is gitignored — local-only convention

Discovered via `git check-ignore -v`. `.gitignore:20` is `docs/decisions/`. 8 tracked files are pre-rule historical; 12 total on disk (4 untracked). The "decision record" pattern in this repo has two distinct meanings:

- `docs/decisions/` — local-only scratch decision artifacts, not committed.
- `docs/superpowers/specs/codex-collaboration/decisions.md` — normative, tracked, frontmattered `authority: decisions`. This is the canonical tracked decisions file for codex-collaboration.

### Key code locations (updated this session)

| Concept | Location |
|---------|----------|
| Finalize turn status derivation (Option B) | `delegation_controller.py:~1527-1539` |
| Discard gate (Option A) | `delegation_controller.py:~1409-1456` |
| `_project_request_to_view` | `delegation_controller.py:864-878` |
| `_CANCEL_CAPABLE_KINDS` | `delegation_controller.py:110` |
| `_DENY_ONLY_DECISIONS` | `delegation_controller.py:862` |
| `_resolve_available_decisions` | `approval_router.py:102-112` |
| Execution prompt constraints | `execution_prompt_builder.py:36-43` |
| Sandbox support roots | `runtime.py:31-46` |

## Context

### Mental model

This session operated under two reframing moves that matter for future work:

**Reframing 1 — "Option A's role has shifted."** In the predecessor session, Options A and B were both justified as "root cause + escape hatch for the currently-observed bug." Post live-validation in this session, Option B now prevents jobs from entering the stuck state. Option A could not be exercised live because the state is no longer reachable through normal operation. Option A is now specifically a *forward-compatibility safety valve* for future state-machine regressions, not an active remediation for any known failure mode. This changes its maintenance contract — if future regressions don't produce `needs_escalation + null` specifically, Option A won't catch them.

**Reframing 2 — "The exec-policy blocker is the shell wrapper, not the tool inventory."** Codex invokes every command via `/bin/zsh -lc '...'`. The sandbox treats the wrapper itself as exec-policy-suspect, regardless of what the wrapped command targets. This means:
- Prompt-level "use only `/bin` and `/usr/bin` tools" doesn't actually clear the blocker — the shell wrapper is the obstacle.
- Exec-policy widening is load-bearing for *any* successful delegation, not just objectives that structurally need developer tools.
- The minimum viable exec-policy design must establish a trust-bounded contract for shell-wrapper execution, not just individual binary allowlisting.

### Environment state

- Branch `feature/delegate-remediation-sandbox-approval` is at commit `fb73f10d`, pushed to origin.
- PR #125 open: https://github.com/jpsweeney97/claude-code-tool-dev/pull/125.
- 913 tests passing, ruff clean.
- Ticket T-20260423-01 remains **open** (AC1 not met; AC5 amended to admit the new terminal state).
- 6 orphaned delegation worktrees visible in `git worktree list` (not blocking, tracked as follow-up).

### Architecture: request handler flow (from predecessor handoff, unchanged)

```
_execute_live_turn
  → _server_request_handler (closure, called per server request)
      → parse_pending_server_request (approval_router.py)
      → kind in _CANCEL_CAPABLE_KINDS?
          YES → "accept" in decisions AND in_boundary?
              YES → {"decision": "accept"} (inline_accepted)
              NO  → store request, {"decision": "cancel"} (captured)
          NO  → known denial kind?
              YES → store, {"answers": {}}
              NO  → store, interrupt_turn, None
  → _finalize_turn
      → captured_request?
          D6 diagnostic (wire signals)
          D4 mark request "resolved"
          Status derivation:
              cancel-capable + empty available_decisions → "failed" (NEW)
              cancel-capable + non-empty → "needs_escalation"
              interrupted_by_unknown → "needs_escalation"
          if needs_escalation: keep runtime live → DelegationEscalation
          else: release runtime, close session → DelegationJob
```

## Learnings

### `docs/decisions/` is local-only scratch; decision records that need to ship must go elsewhere

**Mechanism:** `.gitignore:20` matches the entire `docs/decisions/` directory. 8 tracked files predate the rule and remain tracked; new files are untracked by default. The tracked-convention location for codex-collaboration decisions is the normative spec file `docs/superpowers/specs/codex-collaboration/decisions.md`.

**Evidence:** `git check-ignore -v docs/decisions/...` → `.gitignore:20:docs/decisions/`. `git ls-files docs/decisions/` returns 8 files; `ls docs/decisions/` shows 12.

**Implications:** Any post-hoc decision record intended to travel with a PR must either (a) live in the PR body, (b) go into a tracked location like `docs/plans/` with plan framing, or (c) be promoted into the normative `decisions.md` as a new entry. Do not assume `docs/decisions/` commits will travel with the branch.

**Watch for:** Future sessions may make the same incorrect assumption — the directory's name is misleading.

### Session-scoped job stores are self-isolating across MCP restarts

**Mechanism:** `delegation_jobs/<session_id>/jobs.jsonl` layout scopes job state to the owning MCP session. When a session dies (MCP restart), its jobs become unreachable to new sessions. The `poll` tool rejects cross-session lookups with `job_not_found`.

**Evidence:** Attempted `codex.delegate.poll` on stuck job `c382b5dc` from predecessor session. Result: `job_not_found`. Verified on-disk: the job record exists at `delegation_jobs/40271cdd-.../jobs.jsonl` with terminal-adjacent state `needs_escalation + null`.

**Implications:** The "busy gate" from the predecessor's diagnosis was a *runtime* concern (in-memory `_decided_request_ids`, runtime_registry), not a persistent one. MCP restart is sufficient recovery for orphaned runtime state. Persistent stuck jobs require active session-level cleanup (discard) while the owning session is alive.

**Watch for:** Orphan worktrees under `runtimes/delegation/<job_id>/worktree` persist across restarts (git-managed, not plugin JSONL). Cleanup is a separate concern.

### Shell-wrapper execution (`/bin/zsh -lc`) is the actual exec-policy boundary, not binary inventory

**Mechanism:** Codex wraps every command in `/bin/zsh -lc '<cmd>'`. The sandbox's exec policy evaluates the wrapper itself. Even when `<cmd>` targets a platform-default binary (`/bin/test`, `/bin/find`), the wrapper produces `command_approval` with empty `available_decisions` and `proposedExecpolicyAmendment` populated.

**Evidence:** Live smoke #3, job `191ec8d6`. Agent's self-verification command:
```json
"command": "/bin/zsh -lc '/bin/test -f docs/scratch/T-20260423-01-smoke.md'",
"proposedExecpolicyAmendment": ["/bin/test", "-f", "docs/scratch/T-20260423-01-smoke.md"]
```
The `proposedExecpolicyAmendment` names `/bin/test` — a `/bin` binary — because the sandbox blocked it under the shell wrapper.

**Implications:**
- The handoff's prompt-tuning decision (D1: "prefer platform-default tools") was necessary but insufficient.
- Exec-policy widening is load-bearing for any delegation, regardless of objective complexity.
- The exec-policy design packet must cover the shell-wrapper case as a primary concern, not as an edge case.

**Watch for:** Any proposed exec-policy design that only allowlists binaries will not unblock delegation. The contract must reason about command invocation vehicles.

### Agents verify their work even when not asked — structural, not prompt-fixable

**Mechanism:** Codex agents have strong priors for self-verification. Even an objective as narrow as "create this file with this content" triggers a follow-up `test -f <file>` (or similar). This is part of the agent's training, not prompt-inducible.

**Evidence:** Smoke #3 objective was purely write-one-file. Agent did the write, then ran `test -f` to verify. The verification is what hit the exec-policy boundary.

**Implications:** Objectives cannot be crafted to avoid verification-class commands. Exec-policy widening must support verification commands as a baseline, not as a luxury.

**Watch for:** If the exec-policy design tries to scope approval to "only commands in the objective," it will fail because the agent's verification commands aren't in the objective.

## Conversation Highlights

**User's framing of contract drift:**
> "[P2] Discard contract drift: SKILL.md and promotion-protocol.md still describe the old discard predicate, but delegation_controller.py now also allows needs_escalation + promotion_state=None and terminalizes it as failed + discarded. That is the exact recovery path added for the stuck-escalation bug, so the written operator contract is now stale in a merge-relevant way."
— Drove D1 (fix docs before smoke).

**User's framing of ticket scope drift:**
> "Because exec-policy widening was intentionally deferred, that limitation needs to be recorded in the ticket or closeout instead of being left implicit."
— Drove the Scope Limitations section addition to the ticket.

**User's final publication recommendation:**
> "My direct choice is: publish this as partial hardening, keep the ticket open, and start exec-policy design in a fresh session."
— Set the closeout sequence: commit + push + PR with honest framing; defer exec-policy design.

**User's AC5 amendment guidance:**
> "Either amend AC5 or at least call out in the PR that live validation now includes a legitimate pre-promotion terminal state, failed + null promotion_state, for no-decision exec-policy failures. As written, AC5 is too narrow for the state machine you now intentionally support."
— Drove D4 (amend AC5 in-tree, not just PR body).

**User's framing of the deferred scope boundary:**
> "The next move I recommend is... This is no longer a prompt-tuning problem; it is an exec-policy / trust-boundary problem."
— Drew the clean scope line between this branch's deliverable and the next packet.

**Working style observed:** User prefers recommendations-first with honest scoping. Rewards accurate scope diagnosis; pushes back hard on scope creep or glossing. Expects structured reasoning with cited lines/files. Corrects fast and precisely when synthesis drifts.

## User Preferences

**Contract accuracy over convenience.** User insisted on fixing doc drift before any smoke iteration. Quote: "the written operator contract is now stale in a merge-relevant way." Implication: fix drift immediately; don't defer it to a "post-review cleanup" PR.

**Scope discipline between remediation and design.** User drew clean line between "state machine completeness" (in scope) and "exec-policy amendment handling" (separate design packet). Quote: "That needs its own contract: Which binaries are eligible? Absolute path allowlist or command-pattern amendment? Does it persist for the session, the job, or only the current turn?"

**Publish partial wins rather than hold for full completion.** User's direct choice was to publish as partial hardening rather than keep the branch open waiting for exec-policy fix. Quote: "That is mergeable value if you want it now."

**Convention discovery before assumption.** When I assumed `docs/decisions/` was a committed convention, user reinforced checking the actual repo state. This trained toward verifying conventions via git state, not inferring from directory name.

**Honest acceptance-criteria state over green-washing.** User explicitly wanted AC1 marked not met even though the branch has significant value. Quote: "AC1 is still not actually met." The criterion stays unchecked because the actual operational blocker hasn't been resolved.

**Explicit test requirements + evidence-first.** User's review process verified tests pass (913) and ran `ruff check` independently before offering findings. They didn't rely on claims; they checked the evidence themselves.

## Next Steps

### 1. Exec-policy design packet (fresh session)

**Dependencies:** None — design work can start immediately.

**What to read first:**
- PR #125 body (distilled decision record)
- `packages/plugins/codex-collaboration/server/approval_router.py` (current approval handling)
- `packages/plugins/codex-collaboration/server/delegation_controller.py:~650-731` (request handler in start)
- Raw wire evidence in PR #125 body and this handoff's Session Narrative §4

**Approach suggestion:** Lead with the shell-wrapper framing — exec-policy must reason about command invocation vehicles, not just binary inventory. Surface the design questions from the ticket's Scope Limitations:
- Which binaries are eligible? Absolute path allowlist or command-pattern amendment?
- Does amendment persist for the session, the job, or the current turn?
- How is amendment represented in `available_decisions`?
- Can `/delegate approve` become valid for command approvals?
- How to prevent precedent for arbitrary Homebrew tools?

Add the session's own finding: shell-wrapper trust-boundary. The minimum viable design must support `test`, `find`, and similar verification commands — agents self-verify structurally.

**Acceptance criteria:** Happy-path delegation completes end-to-end. Smoke file appears in primary workspace after promotion. No escalations for platform-tool verification commands. Exec-policy widening has explicit audit trail.

**Potential obstacles:**
- Shell-wrapper trust model is genuinely novel — no precedent in codebase.
- `proposedExecpolicyAmendment` field semantics may require upstream (App Server) clarification.
- `/delegate approve` for command approvals reopens trust-model questions the current design deliberately sidestepped.

### 2. PR #125 review + merge

**Dependencies:** Reviewer availability.

**What to read first:** PR #125 body — framing is "partial hardening, not closure."

**Watch for:**
- Reviewer may push back on AC1 being marked not met — the answer is in the body.
- Reviewer may ask why Option A can't be exercised live — the answer is "Option B prevents reachability."

### 3. Orphan delegation worktree cleanup

**Dependencies:** None.

**Scope:** 6 worktrees under `plugins/data/codex-collaboration-inline/runtimes/delegation/<job_id>/worktree` from prior sessions. Not blocking; git `prunable` flag set on at least one.

**Approach suggestion:** `git worktree prune` first (conservative — only removes prunable ones). Manual inspection + `git worktree remove` for the rest.

### 4. `_decided_request_ids` namespace collision fix (latent bug)

**Dependencies:** Exec-policy design may inform the fix (if request IDs become more meaningful).

**Scope:** `delegation_controller.py:268` — in-memory set, session-scoped. Wire `request_id: "0"` is reused across jobs (observed historically). Current mitigation: widened discard gate. Longer-term: scope to `collaboration_id` or job ID.

**Acceptance criteria:** Two concurrent jobs in the same session can deny different requests even if wire IDs collide.

## In Progress

**State:** Clean stopping point. PR #125 open. All work for T-20260423-01's state-machine remediation is published.

**Immediate next action on resume:** Start the exec-policy design packet in a fresh session. Do NOT continue exec-policy work in the current context — user explicitly wanted a fresh session to avoid scope blur from this branch's deliverable.

## Open Questions

1. **What's the minimum viable exec-policy design?** Must cover shell-wrapper trust-boundary and verification-class commands at minimum. Does it extend to `uv`, `python`, `pytest` as well? What's the scope gate?

2. **Should `_decided_request_ids` be scoped to `collaboration_id` or job ID?** The session-scoped collision is latent; current discard gate mitigates but doesn't fix.

3. **What is the `proposedExecpolicyAmendment` field for?** Wire-level suggests App Server has an amendment mechanism. But `available_decisions: []` means it's not offering amendment as a decision option. Understanding this field's semantics is prerequisite to the exec-policy design.

4. **Is shell-wrapper avoidable, or must it always be trust-bounded?** Can Codex be configured to invoke bare commands? Or is `/bin/zsh -lc` hard-coded in the App Server?

5. **Can `/delegate approve` become valid for command approvals?** The current design says `decide(approve)` is rejected for `command_approval`/`file_change` with a typed reason. Exec-policy widening might reopen this.

## Risks

1. **PR may be challenged on AC1 framing.** A reviewer might want AC1 reworded differently. The PR body and ticket Scope Limitations should make the framing defensible. Mitigated by explicit "as of 2026-04-23 this criterion is not met" note in AC1 itself.

2. **Future state-machine regressions may produce stuck states Option A doesn't cover.** Option A catches `needs_escalation + null` specifically. Other stuck states would need new discard-gate entries or new cleanup paths.

3. **Exec-policy design may turn out to be bigger than anticipated.** The shell-wrapper finding reframed the problem from "binary allowlist" to "trust-bounded command invocation." The design packet may need to be split further.

4. **Orphan worktrees accumulating.** Every aborted/failed delegation leaves a worktree. 6 already present. If cleanup is not automated, this grows monotonically.

## References

| What | Where |
|------|-------|
| PR #125 (partial hardening) | https://github.com/jpsweeney97/claude-code-tool-dev/pull/125 |
| Commit fb73f10d | `git show fb73f10d` |
| Predecessor handoff | `docs/handoffs/archive/2026-04-23_02-09_delegate-sandbox-state-machine-fix.md` |
| Implementation plan | `docs/plans/2026-04-23-delegate-remediation-implementation.md` |
| Delegate ticket (open) | `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` |
| Discard protocol (normative) | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md:136-150` |
| Normative decisions | `docs/superpowers/specs/codex-collaboration/decisions.md` |
| Raw wire evidence (this session smoke) | PR #125 body |
| Codex App Server version used | `codex_collaboration/0.123.0 (Mac OS 26.3.1; arm64) kitty (codex_collaboration; 0.1.0)` |

## Gotchas

- **`docs/decisions/` is gitignored.** Any decision record written there will not travel with a PR. Use PR body, `docs/plans/`, or normative `decisions.md` instead.
- **Shell-wrapper is the real exec-policy boundary.** Prompt-tuning for platform-default tools doesn't clear it. Every command goes through `/bin/zsh -lc '...'`.
- **Option A cannot be exercised live anymore.** Option B prevents jobs from reaching `needs_escalation + null`. Option A is now a forward-compatibility safety valve only.
- **Job stores are session-scoped.** Cross-session `poll` fails with `job_not_found`. Dead-session jobs are unreachable — use MCP restart as the recovery mechanism if a session dies with jobs in flight.
- **Pending-request-store is the only authoritative source for `available_decisions`.** The operator view is projected (`_project_request_to_view` forces `_DENY_ONLY_DECISIONS` for cancel-capable kinds). Always inspect raw JSONL for diagnostic work.
- **Agent self-verification is structural.** Even objectives that seem not to need verification will trigger it. Exec-policy design must account for this.
- **MCP server loads code at session start.** Plugin Python edits require a fresh session to take effect. Live smoke testing always needs a new session after code changes.

## Verification Snapshot

```
uv run pytest packages/plugins/codex-collaboration/tests → 913 passed in 18.42s
git log -1 --format="%h %s" → fb73f10d fix(delegate): harden escalation state machine and sandbox support roots
git status → clean
gh pr view 125 → open, draft=false, mergeable pending review
```
