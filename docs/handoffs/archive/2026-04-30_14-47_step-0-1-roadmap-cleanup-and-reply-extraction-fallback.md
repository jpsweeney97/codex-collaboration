---
date: 2026-04-30
time: "14:47"
created_at: "2026-04-30T18:47:51Z"
session_id: e2a1c6bb-93c0-46ab-9fdc-683cd33bf737
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-30_13-20_codex-collaboration-drift-cleanup-complete-and-roadmap.md
project: claude-code-tool-dev
branch: main
commit: 55a0fdc9
title: Steps 0-1 complete — roadmap closure gates and reply extraction fallback
type: handoff
files:
  - packages/plugins/codex-collaboration/server/turn_extraction.py
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/dialogue.py
  - packages/plugins/codex-collaboration/tests/test_turn_extraction.py
  - packages/plugins/codex-collaboration/tests/test_runtime.py
  - docs/diagnostics/2026-04-30-dialogue-reply-extraction-post-patch.md
  - docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md
  - docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
---

# Handoff: Steps 0-1 complete — roadmap closure gates and reply extraction fallback

## Goal

Execute Steps 0 and 1 of the codex-collaboration short-term roadmap produced and scrutinized in the prior session.

**Trigger:** Continuation of the roadmap sequence from the drift-cleanup-complete handoff. Step 0 (docs-only reconciliation) was a prerequisite for Step 1 (runtime implementation).

**Stakes:** Step 0 prevents future sessions from re-landing already-completed work (AC #4 was satisfied by D-06 but the ticket still listed it as open). Step 1 fixes a live product defect — the `codex.dialogue.reply` empty-agent-message parse failure that terminated B3/B5 benchmark runs.

**Success criteria:**
- Step 0: friction ticket AC #4 marked satisfied, Phase 2/3 headings rewritten, escalation metric reframed, register timestamp updated, temporal marker rewritten
- Step 1: `thread/read` fallback implementation with 9+ tests, live post-patch verification, ticket/register reconciled to current truth

**Connection to project arc:** Fifth session in the codex-collaboration reconciliation and implementation sequence. Drift cleanup (D-01 through D-09) completed in the prior four sessions. This session transitions from reconciliation to runtime implementation work.

## Session Narrative

Loaded the drift-cleanup-complete handoff, which outlined a 7-step roadmap (Steps 0-6) with operating rules. The roadmap had been scrutinized through two rounds in the prior session and accepted with 4 adjustments.

Started with Step 0 on `chore/codex-collaboration-roadmap-cleanup`. The user had already created the branch and committed the changes at `5bfeeada` before presenting it for review. The review verified all five Step 0 acceptance criteria: AC #4 marked satisfied in the friction ticket, Phase 2/3 headings rewritten from conditional investigation language to definitive limitation language, escalation metric reframed from absolute `<=2` to "avoidable sandbox-friction escalations <=2", register timestamp updated to `2026-04-30`, and `CONTRACTS-T02-TEMPORAL-MARKER` replaced with "Post-Packet 1 deferred-approval-response baseline."

Review also swept for stale markers — verified that remaining `CONTRACTS-T02-TEMPORAL-MARKER` mentions (3 in plans, 1 in superseded audit) and `Post-Packet 1 (T-20260423-02)` mentions (6 across plans and audit) were all in snapshot-bounded documents. No current-facing surface contradicted the closure state. User merged to `main` with fast-forward, branch deleted.

Transitioned to Step 1 (T-20260416-01 reply extraction fix). Created an 11-item task list with dependency tracking before starting implementation. Read the full ticket (~380 lines), the runtime notification loop (`runtime.py:249-292`), the `_read_turn_agent_message` helper (`dialogue.py:984-1001`), the reply parse path (`dialogue.py:498-509`), and the existing test infrastructure (`test_runtime.py`, 332 lines with `FakeServerProcess` and `_StubClientForTurnStart` stubs).

Implementation proceeded in three stages: (1) extracted the shared `turn_extraction.py` helper and rewired `dialogue.py`, (2) added the `_fallback_extract_agent_message` method and `fallback_on_empty_message` parameter to `runtime.py`, (3) wrote all tests.

First test run failed with 3 failures. Two were caused by the existing `_StubClientForTurnStart` — it didn't handle `thread/read` requests, so when the fallback fired (advisory turn, completed status, empty message), it crashed. The third was a test data error — used `source_file`/`source_lines` evidence fields instead of the actual `claim`/`citation` schema. Fixed both issues: made `_StubClientForTurnStart` only record `turn/start` params and return empty turns for `thread/read`; corrected the test evidence payload. Second run: 1082/1082 passed.

User reviewed the implementation commit at `00ec0054`. Verdict: "No blocking findings." Two non-blocking notes: (1) the fallback docstring's "must never raise" contract is adequately enforced by the `try/except Exception` and upstream `JsonRpcClient.request()` dict-result enforcement, (2) test #5 is narrower than the ticket wording (tests `parse_consult_response` directly, not the full `DialogueController.reply()` flow) but acceptable given that `dialogue.py:501` directly parses `turn_result.agent_message`.

Proceeded to live verification. Confirmed App Server access (Codex `0.125.0`, compatibility check passing). Wrote a verification script that instruments `_fallback_extract_agent_message` to detect whether the fallback fires. Ran 5 adversarial advisory turns across 3 sessions:

| Run | Thread ID | Message length | Fallback fired |
|-----|-----------|---------------|----------------|
| 1 | `019ddfa5-639b-7471-a8fd-9db608bc8c19` | 15,726 | No |
| 2 | `019ddfa7-9031-7ad0-a09d-4a9808b73511` | 14,679 | No |
| 3-5 | `019ddfa9-9986-7ea2-8591-c5881066daa3` | 17K-26K | No |

All completed normally. `item/completed` delivered agent messages on the normal path every time. The B3/B5 failure mode (missing `item/completed`) did not reproduce. Evidence artifact written to `docs/diagnostics/2026-04-30-dialogue-reply-extraction-post-patch.md` and committed at `c5807d84`.

User's assessment: "Your read is correct, and the evidence artifact is honest." But noted that leaving the ticket and register unchanged would create drift — they'd still say "Land the fix" when the fix was already landed. Directed a narrow status-reconciliation commit to update both surfaces to current truth without claiming closure.

Applied the reconciliation at `a8b1f04e`. User's scrutiny found one P3: the register priority item started with "Close T-20260416-01" which steers toward closure. Reworded to "Resolve T-20260416-01 closure standard" at `55a0fdc9`. Merged to `main`, branch deleted.

## Decisions

### Step 0 verification approach: sweep both positive and negative markers

**Choice:** Run the roadmap's own 5 verification `rg` commands plus additional sweeps for stale markers across all of `docs/`.

**Driver:** The drift-cleanup handoff documented "incomplete sweep before first commit is the recurring root cause" — applying that lesson from D-09/D-08.

**Rejected alternatives:**
- **Trust the commit diff only** — rejected because the prior session showed closure-propagation failures in 100% of findings (D-05, D-06, D-08 all required scrutiny to catch status surfaces left behind).

**Implication:** Verification includes both "did the new markers land?" and "did any old markers survive in current-facing docs?"

**Trade-offs accepted:** Longer verification cycle. Minimal cost given the pattern of closure-propagation failures.

**Confidence:** High (E2) — both positive and negative checks passed. All remaining old-marker hits were in snapshot-bounded documents.

**Reversibility:** N/A — verification, not a code decision.

**Change trigger:** None — verification is complete.

### Test #5 narrower than ticket wording is acceptable

**Choice:** Test #5 verifies `parse_consult_response` directly on fallback-produced text, not the full `DialogueController.reply()` flow.

**Driver:** User review: "Given the controller already directly parses `turn_result.agent_message` at dialogue.py:501, and runtime tests prove the fallback populates that field, this is acceptable rather than a required rework."

**Rejected alternatives:**
- **Full `DialogueController.reply()` integration test** — would require mocking the entire lineage store, journal, and control plane. High complexity for minimal additional coverage given the two halves (runtime produces the text, controller parses it) are independently tested.

**Implication:** If `dialogue.py` ever changes how it reads `turn_result.agent_message`, test #5 won't catch the regression. The existing dialogue test suite covers that path.

**Trade-offs accepted:** Narrower coverage boundary. Acceptable because the contract between runtime and dialogue is a single field (`agent_message`) on a dataclass.

**Confidence:** High (E2) — both the runtime test (proving the field is populated) and the parse test (proving the text is valid) independently verify the contract.

**Reversibility:** High — add a full integration test later if needed.

**Change trigger:** `dialogue.py` changes how it accesses `turn_result.agent_message`.

### T-20260416-01 stays open despite implementation landing

**Choice:** Do not close T-20260416-01. Keep it open pending closure adjudication.

**Driver:** User: "I would not close T-20260416-01 on this evidence." The live verification establishes non-regression but does not prove the fallback recovery path for the original missing-`item/completed` failure class.

**Rejected alternatives:**
- **Close immediately** — rejected because the closure criteria include "One-run verification: confirm convergence or natural termination without parse error" and the ticket's evidence hierarchy distinguishes non-regression from recovery proof.
- **Leave ticket/register unchanged** — rejected by user: "That would create a smaller version of the same drift pattern Step 0 just cleaned up."

**Implication:** The ticket and register were updated to reflect current truth (implementation landed, non-regression established, fallback unproven). The closure fork is explicit: accept test coverage + version drift, or wait for natural live fallback proof.

**Trade-offs accepted:** Ticket stays open potentially indefinitely if the failure mode never reproduces on Codex `0.125.0+`. The implementation is test-covered and merged regardless.

**Confidence:** High (E2) — the evidence artifact clearly distinguishes what was proven from what wasn't.

**Reversibility:** High — close the ticket anytime by accepting test coverage as sufficient.

**Change trigger:** A live run where the fallback fires and recovers text, or an explicit decision to accept the current evidence.

### Register priority wording: neutral framing over directional framing

**Choice:** Reword "Close T-20260416-01" to "Resolve T-20260416-01 closure standard" in the register priority list.

**Driver:** User scrutiny finding (P3, confidence 0.82): "The priority item starts with 'Close T-20260416-01' which can steer the next executor toward closure even when the chosen outcome may be to keep waiting."

**Rejected alternatives:**
- **Keep "Close" wording** — rejected because "this repo has repeatedly treated closure wording drift as a real operational risk."

**Implication:** The priority list now matches the open-ticket boundary.

**Trade-offs accepted:** None significant.

**Confidence:** High (E2) — direct user feedback with explicit reasoning.

**Reversibility:** High — wording change only.

**Change trigger:** If the closure decision is made, the row gets removed (per the register lifecycle: open → work → remove).

## Changes

### `server/turn_extraction.py` — New shared helper

**Purpose:** Extract agent message text from `thread/read` turn projections. Shared by both the dialogue read path and the runtime fallback path.

**Approach:** Single function `extract_agent_message(raw_turn: Mapping[str, object]) -> str`. Handles two App Server projection shapes: top-level `agentMessage` field (current) and nested `items[]` with `type: "agentMessage"` (legacy). Returns `""` on unrecognized shapes.

**Key detail:** Uses `Mapping[str, object]` (not `dict`) for the parameter type to accept any dict-like input. Top-level `agentMessage` takes precedence over `items[]` if both exist.

### `server/runtime.py` — Fallback mechanism

**Purpose:** Recover agent message text via `thread/read` when `item/completed` notification fails to deliver it during advisory turns.

**Key changes:**
- Added `_fallback_extract_agent_message(thread_id, turn_id)` method — best-effort recovery, catches all exceptions, falls through to `""` on any failure
- Added `fallback_on_empty_message: bool = False` parameter to `_run_turn()`
- `run_advisory_turn()` passes `True`; `run_execution_turn()` uses default `False`
- Fallback fires only when `agent_message == ""` AND `status == "completed"`
- Turn selection by exact `turn_id`, not position

**Design choice:** Fallback is advisory-only because execution turns legitimately complete with empty `agent_message` on `interrupted`/`failed` status. An unconditional fallback would add unnecessary `thread/read` calls to delegation paths.

### `server/dialogue.py` — Rewired to shared helper

**Purpose:** Replace private `_read_turn_agent_message` static method with shared `extract_agent_message` from `turn_extraction.py`.

**Changes:** Import added, call site at line 948 rewired, old static method deleted.

### `tests/test_turn_extraction.py` — 5 unit tests

Tests #1-#3 from the ticket plus two supplementary: top-level extraction, items extraction, empty return on missing shapes, malformed item handling, precedence when both shapes exist.

### `tests/test_runtime.py` — 7 integration tests + stub updates

**Stub changes:** `FakeServerProcess` extended with `queue_error()` for simulating request failures. `_StubClientForTurnStart` updated to handle `thread/read` requests (returns empty turns) and only record `turn/start` params.

**New tests:** Fallback populates agent_message (#4), turn-ID lookup (#4 supplement), downstream parse parity (#5), read raises (#6), no matching turn (#7), empty extraction (#8), execution-turn isolation (#9).

### `docs/diagnostics/2026-04-30-dialogue-reply-extraction-post-patch.md` — Evidence artifact

Live verification record: 5 adversarial turns across 3 sessions on Codex `0.125.0`. All completed normally, fallback did not fire. Non-regression established, fallback recovery unproven.

### Ticket and register reconciliation

Friction ticket (`T-20260416-01`): closure criteria checkboxes updated (6 of 7 checked), current status paragraph added, next step updated from "Land the fix" to closure adjudication.

Register: priority #1 reworded to "Resolve T-20260416-01 closure standard", T-20260416-01 row current truth and exit condition updated to reflect implementation landed and live evidence.

### Step 0 changes (user-authored)

Friction ticket (`T-20260429-01`): AC #4 marked satisfied, Phase 2/3 headings rewritten, escalation metric reframed. Register: timestamp updated, `CONTRACTS-T02-TEMPORAL-MARKER` row removed. `contracts.md`: temporal marker rewritten.

## Codebase Knowledge

### Runtime notification loop and fallback architecture

| Component | Location | Role |
|-----------|----------|------|
| Notification loop | `runtime.py:258-306` | Collects notifications until `turn/completed`; captures agent message from `item/completed` |
| Agent message capture | `runtime.py:275-280` | Checks `item.type == "agentMessage"` on `item/completed` notifications |
| Fallback trigger | `runtime.py:294-301` | After `turn/completed`, if `agent_message == ""` and `status == "completed"` and `fallback_on_empty_message`, calls `_fallback_extract_agent_message` |
| Fallback method | `runtime.py:309-341` | `read_thread()` → turn-ID lookup → `extract_agent_message()`. All failures fall through to `""` |
| Advisory entry point | `runtime.py:164-183` | `run_advisory_turn()` — passes `fallback_on_empty_message=True` |
| Execution entry point | `runtime.py:185-208` | `run_execution_turn()` — uses default `False` |
| Shared extractor | `turn_extraction.py:8-30` | `extract_agent_message()` handles both projection shapes |
| Dialogue read path | `dialogue.py:948` | Uses same `extract_agent_message()` for `thread/read` results |
| Parse pipeline | `dialogue.py:500-509` | `parse_consult_response(turn_result.agent_message)` — where `CommittedTurnParseError` originates |

### Test stub architecture

| Stub | Location | Purpose | Supports fallback? |
|------|----------|---------|-------------------|
| `_StubClient` | `test_runtime.py:13-21` | Account read only | No |
| `_StubClientForThreadOps` | `test_runtime.py:35-50` | Thread read/resume | No |
| `_StubClientForTurnStart` | `test_runtime.py:111-137` | Turn start + completion; handles `thread/read` with empty turns | Yes (returns empty) |
| `FakeServerProcess` | `test_runtime.py:224-243` | Full-featured fake with queued responses, notifications, and errors | Yes (via `queue_response`/`queue_error`) |

### `FakeServerProcess.queue_error()` — new capability

Added to support test #6 (read_thread raises). `_FakeJsonRpcClient.request()` checks `self._server._errors` before `self._server._responses` — if a method has a queued error, it raises instead of returning. This allows simulating transport failures for specific methods.

### Evidence schema for `parse_consult_response`

`parse_consult_response` expects evidence items with `claim: str` and `citation: str` fields — not `source_file`/`source_lines`/`how_found`/`reasoning`. The initial test data used the wrong schema, causing test #5 to fail with "evidence entry missing claim/citation strings." Corrected to `{"claim": "test claim", "citation": "test.py:1-5"}`.

### `_StubClientForTurnStart` interaction with fallback

The `_StubClientForTurnStart` stub's `next_notification` returns `turn/completed` with `agentMessage` in params, but the runtime code only reads agent message from `item/completed` notifications (line 275-280). The `agentMessage` field in `turn/completed` params is ignored. This means `_StubClientForTurnStart` tests always produce `agent_message == ""`, which triggers the fallback for advisory turns. The stub needed to handle `thread/read` requests to avoid crashing. Also needed to only record `turn/start` params (not overwrite with `thread/read` params) to preserve the existing param-capture tests.

## Context

### Roadmap position

Steps 0-1 of a 7-step roadmap (0-6) are complete. The roadmap was produced and scrutinized in the prior session (v2 with 4 adjustments).

| Step | Status | Description |
|------|--------|-------------|
| 0 | Complete | Roadmap cleanup — docs-only reconciliation |
| 1 | Implementation complete, ticket open | Reply extraction fallback |
| 2 | Not started | T-20260429-01 Phase 1 sandbox carve-outs (Options B + E) |
| 3 | Not started | T-20260429-02 unsupported request classification |
| 4 | Not started | Carry-forward debt sweep (TT.1, RT.1, P1-MINOR-SWEEP) |
| 5 | Not started | BMARK-L1-L3 disposition |
| 6 | Not started | AUDIT-CONSUMER-INTERFACE specification or deferral |

Steps 2-3 share the live App Server access bottleneck. Steps 4-6 can proceed independently.

### Pre-existing Pyright issues (carry-forward, not introduced)

All Pyright diagnostics observed during this session are pre-existing:
- `runtime.py` `TurnStatus` literal narrowing (RT.1)
- `dialogue.py` Posture literal narrowing, `runtime` possibly unbound, `session` attribute access, `thread_id` nullability
- `test_runtime.py` `_client` assignment, `pytest` import resolution

None were introduced by the implementation changes.

### Commit topology on `main` (post-merge)

| Commit | Step | Content |
|--------|------|---------|
| `5bfeeada` | 0 | Roadmap closure gates (docs-only: friction ticket, register, contracts.md) |
| `00ec0054` | 1 | Implementation + 12 tests (turn_extraction.py, runtime.py, dialogue.py) |
| `c5807d84` | 1 | Evidence artifact (5 adversarial runs, non-regression established) |
| `a8b1f04e` | 1 | Status reconciliation (ticket/register updated to current truth) |
| `55a0fdc9` | 1 | Wording fix (register priority neutral framing) |

All 5 commits are ahead of `origin/main`. No push has been requested.

### App Server version context

The original B3/B5 failure mode was on Codex `0.117.0`. This verification used `0.125.0`. The `item/completed` delivery behavior may have changed between versions. The vendored schema fixtures are `0.117.0`. The schema delta at `docs/tickets/` covers `0.125.0` but `ThreadReadResponse` was not explicitly compared.

### Dialogue reply path — how the bug manifests

The `CommittedTurnParseError` originates at `dialogue.py:504-509`. The call chain is:

1. `DialogueController.reply()` calls `runtime.run_advisory_turn()` → gets `TurnExecutionResult`
2. `reply()` commits the turn to durable state (`dialogue.py:484-496`) — this succeeds regardless of agent message content
3. `reply()` calls `parse_consult_response(turn_result.agent_message)` at `dialogue.py:501`
4. If `agent_message == ""`, `json.loads("")` raises `json.JSONDecodeError` → wrapped as `CommittedTurnParseError`

The fix canonicalizes `agent_message` at the runtime layer (step 1), so by the time `reply()` receives the `TurnExecutionResult`, the field is already populated from the fallback. This means `dialogue.py` doesn't need any changes beyond the import rewiring — the fix is transparent to all downstream consumers.

## Learnings

### Existing test stubs interact with new fallback behavior

**Mechanism:** When `run_advisory_turn()` gained `fallback_on_empty_message=True`, every existing advisory-turn test that used `_StubClientForTurnStart` suddenly triggered the fallback — because the stub's `next_notification` produces `turn/completed` without a preceding `item/completed`, leaving `agent_message == ""` and `status == "completed"`.

**Evidence:** First test run: 3 failures including `test_effort_included_when_provided` and `test_run_advisory_turn_uses_read_only_policy`. Both used `_StubClientForTurnStart` which didn't handle `thread/read` requests, and whose `request()` method overwrote `last_params` with the `thread/read` call.

**Implication:** When adding fallback behavior to a shared code path, sweep all test stubs that exercise that path for compatibility. Stubs that were fine with the old behavior may break with the new behavior not because the implementation is wrong but because the stubs are incomplete.

**Watch for:** Future changes to `_run_turn()` that add conditional behavior based on parameters — each existing stub must handle the new conditional's side effects.

### Evidence field schemas must be verified against the parser, not assumed

**Mechanism:** Test #5's evidence payload used `source_file`/`source_lines`/`how_found`/`reasoning` fields (which look like a reasonable evidence schema) instead of the actual `claim`/`citation` fields that `parse_consult_response` expects.

**Evidence:** Test failure: "evidence entry missing claim/citation strings. Got: {'claim': 'test claim', 'source_file': 'test.py', ...}" — `claim` was present but `citation` was missing.

**Implication:** When writing test data that will be fed through a real parser, read the parser's validation logic first. Don't rely on what the schema "probably" looks like.

### Closure wording in status surfaces has operational consequences

**Mechanism:** Register priority #1 initially said "Close T-20260416-01" — directional wording that steers the next executor toward closure even when the open decision might be to keep waiting.

**Evidence:** User scrutiny: "this repo has repeatedly treated closure wording drift as a real operational risk."

**Implication:** Status surfaces that describe open work should use neutral verb framing ("Resolve", "Adjudicate", "Determine") not directional framing ("Close", "Land", "Fix") when the outcome is genuinely undecided.

## Next Steps

### 1. Resolve T-20260416-01 closure standard

**Dependencies:** None — this is a decision, not implementation.

**What to read first:** Evidence artifact at `docs/diagnostics/2026-04-30-dialogue-reply-extraction-post-patch.md`. Ticket closure criteria at `docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md:341-358`.

**Approach:** Binary choice: (a) accept test coverage plus App Server version drift (`0.117.0` → `0.125.0`) as sufficient closure evidence, or (b) keep the ticket open and wait for a natural live fallback recovery proof.

**Acceptance criteria:** If closing: update ticket `status: closed`, remove register row, record closure commit. If keeping open: no action needed — current state is correct.

### 2. Execute Step 2: T-20260429-01 Phase 1 sandbox carve-outs

**Dependencies:** Step 0 is landed. Step 1 closure is independent.

**What to read first:** Friction ticket at `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md` — Friction surface 1 (Option B, `~/.codex/` reads) and Friction surface 2 (Option E, worktree `.git` cross-pointer reads). Implementation sections at lines 68-111.

**Approach:** Three-commit pattern per the roadmap. Single implementation commit for both Options B and E in `runtime.py:46-57` (`build_workspace_write_sandbox_policy`). Extend `readableRoots` with `~/.codex/memories` and `~/.codex/plugins/cache` (Option B) and the dynamically-resolved gitdir target (Option E). Update `test_runtime.py:167-183` regression assertion.

**Acceptance criteria:** Avoidable sandbox-friction escalations <=2 in a comparable `/delegate` smoke. Legitimate operator-gated approvals counted separately. Credential boundary preserved (`~/.codex/auth.json`, `~/.codex/config.toml`, `~/.codex/history.jsonl` remain blocked).

### 3. Execute Steps 3-6 per roadmap

Steps 3-6 follow the roadmap sequence. Steps 2-3 share the live-access bottleneck. Steps 4-6 can proceed independently.

## In Progress

Clean stopping point — Steps 0 and 1 committed and merged to `main`, T-20260416-01 intentionally open pending closure adjudication. No work in flight. `main` is 5 commits ahead of `origin/main`.

## Open Questions

### Should the 5 non-codex closed tickets in `docs/tickets/` root be moved?

Carried from prior handoff. After D-05, `docs/tickets/` root still has 5 non-codex closed tickets (T-010, T-20260319-01, T-20260403-01, T-20260410-03, T-20260410-04). Separate general hygiene, not codex-collaboration drift.

### Is `thread/read` response shape stable across App Server versions?

Carried from prior handoff. The vendored schema is `0.117.0`. Verification ran on `0.125.0`. `ThreadReadResponse` was not explicitly compared between versions. Relevant if a future run triggers the fallback on a newer App Server version.

### When should `origin/main` be updated?

`main` is now 5 commits ahead of `origin/main`. No push has been requested. The commits are all local.

## Risks

### Fallback recovery path unproven by live evidence

The `thread/read` fallback is test-covered (7 runtime tests including the load-bearing regression test #4) but has never been exercised against the real App Server. If the App Server's `thread/read` response shape differs from what the tests assume for the specific failure class (missing `item/completed`), the fallback could fail silently and return `""`. The implementation's best-effort semantics mean this would manifest as the original `CommittedTurnParseError` — no worse than the unfixed state, but also no better.

### `origin/main` divergence

5 local commits not pushed. If another machine pushes to `origin/main`, a merge or rebase will be needed.

## References

- **Friction ticket (T-20260429-01):** `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md`
- **Reply extraction ticket (T-20260416-01):** `docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md`
- **Reconciliation register:** `docs/status/codex-collaboration-reconciliation-register.md`
- **Live verification evidence:** `docs/diagnostics/2026-04-30-dialogue-reply-extraction-post-patch.md`
- **Prior handoff:** `docs/handoffs/archive/2026-04-30_13-20_codex-collaboration-drift-cleanup-complete-and-roadmap.md`
- **Roadmap (scrutinized v2):** Captured in prior handoff's Context section
- **Step 0 commit:** `5bfeeada` — reconcile roadmap closure gates
- **Step 1 commits:** `00ec0054` (implementation), `c5807d84` (evidence), `a8b1f04e` (reconciliation), `55a0fdc9` (wording fix)

## Gotchas

### `_StubClientForTurnStart` silently produces empty `agent_message`

The stub's `next_notification` puts `agentMessage` in the `turn/completed` params, but the runtime only reads agent message from `item/completed` notifications. This means all advisory-turn tests using this stub produce `agent_message == ""`. After the fallback was added, this triggers `thread/read` on every advisory-turn stub test. The stub handles it by returning empty turns, but any future test that asserts `agent_message != ""` using this stub will fail unless it also queues an `item/completed` notification or a `thread/read` response with matching turn data.

### `parse_consult_response` evidence fields are `claim`/`citation`, not `source_file`/`source_lines`

Test data for the parse pipeline must use `{"claim": "...", "citation": "..."}`. The schema looks like it might use more descriptive field names but the parser at `prompt_builder.py:102-109` validates exactly `claim` and `citation`.

### Register rows are removed on completion, not marked resolved

Carried from prior handoff. The register defines 5 states (`blocking`, `open`, `drift`, `missing-artifact`, `deferred`). "Resolved" is not one of them. When work is done, remove the row. The drift report's addressed annotations serve as the historical record.

## Conversation Highlights

**On test #5 scope:**
User review: "Test #5 is slightly narrower than the ticket wording: it verifies fallback-produced text passes parse_consult_response, not a full DialogueController.reply() flow. Given the controller already directly parses turn_result.agent_message at dialogue.py:501, and runtime tests prove the fallback populates that field, this is acceptable."

**On closure standard:**
User: "I would not close T-20260416-01 on this evidence. The artifact says the right thing: do not close based solely on this run."

**On drift prevention:**
User: "I would not leave the current-facing ticket/register exactly as-is after merging Commit 1 and Commit 2. That would create a smaller version of the same drift pattern Step 0 just cleaned up."

**On register wording:**
User: "I would reword this to 'Adjudicate T-20260416-01 closure' or 'Resolve T-20260416-01 closure standard' so the priority list matches the open-ticket boundary."

## User Preferences

**Closure standard rigor:** The user distinguishes between non-regression evidence and recovery-path evidence. Non-regression (the patched code doesn't break normal operation) is necessary but not sufficient for closure. Recovery-path evidence (the fallback actually fires and works) is the higher bar. User: "The evidence artifact is honest. It proves live non-regression on Codex 0.125.0; it does not prove the fallback recovery path for the original missing-item/completed failure class."

**Drift prevention as a principle:** Status surfaces must reflect current truth at all times. The user treats any contradiction between implementation state and status-surface claims as actionable — not "we'll fix it later" but "fix it now before merging." User: "this repo has repeatedly treated closure wording drift as a real operational risk."

**Scrutiny depth and specificity:** User scrutiny findings include file paths, line numbers, confidence scores, and priority levels. Expects the same specificity in responses. The P3 wording finding (confidence 0.82) was a single word change but treated as worth a separate commit.

**Three-commit pattern for runtime work:** Implementation/tests → evidence artifact → ticket/register closeout. The pattern can be abbreviated (no Commit 3 if evidence doesn't support closure) but the separation between implementation and evidence is structural.
