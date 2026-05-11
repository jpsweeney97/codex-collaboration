---
date: 2026-04-29
time: "19-22"
created_at: "2026-04-29T19:22:27Z"
session_id: 47bb4483-617c-4472-9bf3-56447bdc315b
resumed_from: docs/handoffs/archive/2026-04-29_16-13_reconciliation-landed-t16-fix-spec-tightened-branch-merged.md
project: claude-code-tool-dev
branch: main
commit: 72d92b22
title: T-16 protocol revision through 4 review rounds, schema delta audit with nested definition tracking, reachability ticket failure-path fix
type: handoff
files:
  - docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/superpowers/specs/codex-collaboration/2026-04-29-codex-app-server-0.125.0-schema-delta.md
  - docs/superpowers/specs/codex-collaboration/evidence/2026-04-29-codex-app-server-schema-0.117.0-to-0.125.0-comparison.json
  - docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md
  - packages/plugins/codex-collaboration/scripts/compare_app_server_schemas.py
  - docs/superpowers/specs/codex-collaboration/README.md
---

# Handoff: T-16 protocol revision through 4 review rounds, schema delta audit with nested definition tracking, reachability ticket failure-path fix

## Goal

Continue from the prior session's stopping point (reconciliation landed, T-16 fix spec tightened, branch merged to main). This session had three phases:

1. Revise the T-16 ticket from "final `turn/completed.turn.items[]` fallback" to an evidence-backed fix spec grounded in the vendored Codex App Server schema — the prior fix spec targeted a field that's always empty per schema.
2. Audit the user's new schema delta analysis document (0.117.0 → 0.125.0) and the new reachability ticket (T-20260429-02).
3. Fix findings from both audits.

**Trigger:** User pasted code-comment findings showing the proposed `turn/completed.turn.items[]` fallback was invalid — the vendored schema says Turn.items is always empty for notifications. This invalidated the previous session's fix spec.

**Stakes:** The T-16 ticket is the tracking artifact for the only known product defect in codex-collaboration. An incorrect fix spec would lead an implementer to write a patch that silently does nothing. The schema delta analysis is the evidence base for a future 0.125.0 pin upgrade — inaccurate claims there propagate to downstream planning.

**Success criteria (all met):**
- T-16 ticket revised with protocol analysis grounded in vendored schema evidence
- Schema delta analysis audited, findings fixed, comparison script enhanced
- Reachability ticket audited and failure-path classification corrected

## Session Narrative

Resumed from the prior handoff via `/load`. The prior session left all work committed and clean on `main` at `553fa58f`.

**Phase 1 — T-16 protocol revision (4 review rounds).** User pasted detailed code-comment findings showing the proposed `turn/completed.turn.items[]` fallback was invalid. Read the vendored schemas directly: `TurnCompletedNotification.json:1285` says Turn.items is "Only populated on a `thread/resume` or `thread/fork` response. For all other responses and notifications returning a Turn, the items field will be an empty list." Also discovered `AgentMessageDeltaNotification.json` — a streaming delta notification the runtime doesn't handle. Confirmed that `item/completed` is already captured at `runtime.py:268-273`, and that the runtime has zero handling for `item/agentMessage/delta`.

Created branch `fix/t16-protocol-evidence-revision` and rewrote the ticket through 4 iterative review rounds with the user:

**Round 1 (commits `be67c1e0`, `1ea8ebb2`):** Replaced the withdrawn turn.items fallback with protocol analysis documenting three notification sources. Presented three candidate mechanisms (thread/read fallback, delta assembly, item/completed investigation). Fixed stale line references. Strengthened closure criteria. Then user caught: symptom section still used old response-shape theory, fallback scope was undefined for execution turns, and B3 notification stream was incorrectly claimed as preserved.

**Round 2 (commit `d2447526`):** Rewrote symptom to current claim. Added advisory-only scope constraint (run_advisory_turn uses `allowed_terminal_statuses=("completed",)` while run_execution_turn allows `("completed", "interrupted", "failed")` — empty agent_message is legitimate for interrupted/failed). Clarified B3 rollout is Codex Desktop session JSONL, not App Server notification stream. Downgraded mechanism C from prerequisite to optional diagnostic. Expanded implementation tests from 5 to 9 (added fallback failure cases #6-#8 and execution-turn isolation #9). User then caught: thread/read still overclaimed as "guaranteed," fallback used position-based turn selection instead of ID-based, and read_thread failure semantics were undefined.

**Round 3 (commit `09012b91`):** Required exact turn_id lookup (position-based selection is unsafe under ordering divergence or overlapping turns). Defined best-effort failure semantics (fallback must not raise — falls through to existing CommittedTurnParseError path). Downgraded thread/read from "guaranteed" to "plausible" with post-patch reproduction as proof point. Replaced ephemeral `/private/tmp` references with durable repo paths.

**Round 4 (commit `aed4ab05`):** Replaced remaining "committed turn history" phrase with "Codex session log" for consistent evidence boundary language throughout. User verdict: "functionally ready — remaining issue is narrow wording precision, not a blocker."

Merged to main via fast-forward (5 commits plus 1 user commit). Deleted branch.

**Phase 2 — Schema delta audit.** User had created a schema delta analysis (`2026-04-29-codex-app-server-0.125.0-schema-delta.md`, 875 lines) and a new ticket (T-20260429-02) while this session was working on T-16. Read the full delta document. Cross-verified claims against vendored 0.117.0 and scratch 0.125.0 schemas.

Key verification: `Turn.items` description is identical in both schema versions — the T-16 fix spec's constraint holds even after upgrading. Also found the Turn definition gained 3 new properties (`completedAt`, `durationMs`, `startedAt`) and Thread gained `forkedFromId`, but the document only said "nested schema changed" without calling these out. The comparison script only checked top-level schema-file properties, not nested definition properties.

**Phase 3 — Schema delta fixes and reachability ticket audit.** Created branch `fix/schema-delta-nested-turn-properties`. Enhanced the comparison script with `nested_definition_delta()` tracking `Turn`, `ThreadItem`, and `Thread` properties across direct-runtime-consumed schemas. Regenerated the comparison report — it now mechanically captures the Turn timing fields and Thread.forkedFromId across 5 schema files. Updated the document with explicit Turn property additions, comparison-report limitation note, and fixed the markdown table separator bug.

Then audited the reachability ticket (T-20260429-02, 86 lines). Verified all 9 ServerRequest methods against the vendored schema and the actual parser code in `approval_router.py`. Found `item/permissions/requestApproval` was misclassified — it has all required context fields per schema, so it routes through the known-parsed non-parkable path, not the parse-failure path. Added failure-path classification column to the method table distinguishing the two runtime code paths. Committed, merged to main, deleted branch.

**Side task — plain language preference.** User asked for plain-language explanations after an ELI5-style audit summary. Saved as a global CLAUDE.md instruction and a memory record.

## Decisions

### D1: Advisory-only scope for thread/read fallback

**Choice:** The T-16 fallback fires only in `run_advisory_turn()`, not in `run_execution_turn()`.

**Driver:** `_run_turn()` is shared between advisory and execution paths. Execution turns legitimately complete with empty `agent_message` on `interrupted` or `failed` status. User feedback round 2: "scoping the runtime fallback so it does not accidentally perturb execution/delegation turns while fixing advisory `reply()` and `consult()`."

**Rejected alternatives:**
- **Unconditional fallback in `_run_turn()`** — would add `thread/read` calls to delegation paths where empty is correct, and could introduce new failure modes. Rejected because it changes behavior for paths that work correctly today.
- **Status-only check (`completed` status)** — narrows the blast radius but still fires in execution turns that complete successfully. Rejected because execution turns with `completed` status and empty `agent_message` may also be legitimate.

**Implication:** Implementation options are (a) `fallback_on_empty_message: bool` parameter on `_run_turn()`, or (b) post-processing in `run_advisory_turn()`.

**Trade-offs accepted:** If execution turns also suffer from the same bug (empty agent_message on successful completion), they won't be fixed by this patch. Accepted because the bug has only been observed in advisory dialogue turns.

**Confidence:** High (E2) — verified both callers' `allowed_terminal_statuses` directly in `runtime.py:169-200`.

**Reversibility:** High — the scope constraint is a single parameter or call-site check.

**Change trigger:** If the same empty-message bug appears in execution turns.

### D2: Best-effort failure semantics for thread/read fallback

**Choice:** If `read_thread()` raises, returns no matching turn, or the matching turn has no extractable message, the fallback does not raise — it falls through and returns the original `TurnExecutionResult` with `agent_message == ""`.

**Driver:** User feedback round 3: "an unguarded exception from the fallback would escalate to dispatch-failure semantics, potentially invalidating the runtime and quarantining the handle — a worse outcome than the parse error it was trying to prevent."

**Rejected alternatives:**
- **Raise on fallback failure** — would change the existing `CommittedTurnParseError` semantics (recoverable) into dispatch-failure semantics (runtime invalidation). Rejected because the fallback must not have a worse failure mode than the bug it's fixing.
- **Log-and-retry** — adds complexity without clear value. The failure is already captured in the parse error downstream.

**Implication:** Three failure-case tests (#6-#8) verify the best-effort behavior. The existing `CommittedTurnParseError` path is preserved as the safety net.

**Trade-offs accepted:** If thread/read consistently fails for this failure class, the fallback is a no-op and the bug remains. Accepted because the post-patch live reproduction will reveal this.

**Confidence:** High (E2) — traced both failure paths through `delegation_controller.py:984-1070` to confirm the different cleanup obligations.

**Reversibility:** High — changing from best-effort to raise-on-failure is a one-line change.

**Change trigger:** If the thread/read fallback is confirmed working and we want to promote it from best-effort to mandatory.

### D3: Add nested definition tracking to comparison script

**Choice:** Track property changes in `Turn`, `ThreadItem`, and `Thread` definitions across direct-runtime-consumed schema files.

**Driver:** The Turn definition gained 3 timing properties (`completedAt`, `durationMs`, `startedAt`) in 0.125.0, but the comparison report showed `added_props: []` because it only checked top-level schema-file properties. User: "otherwise we will keep relying on prose for one of the highest-signal runtime-consumed deltas."

**Rejected alternatives:**
- **Full recursive definition comparison** — would compare every definition in every file. Rejected because it would be extremely verbose and most definitions are ThreadItem variants that don't affect runtime code directly.
- **Prose-only callout** — just add text to the document without enhancing the script. Rejected because the point is mechanical capture, not manual tracking.

**Implication:** The report now has a `nested_definition_deltas` section. Future schema comparisons will automatically capture property additions in Turn, ThreadItem, and Thread.

**Trade-offs accepted:** Tracked definitions are hardcoded in `TRACKED_NESTED_DEFINITIONS`. If a new definition becomes runtime-relevant, it must be added to the list manually.

**Confidence:** High (E3) — verified the report output against direct schema inspection, confirmed it caught all additions including Thread.forkedFromId which I hadn't spotted manually.

**Reversibility:** High — the tracked list is a simple constant.

**Change trigger:** If the tracked list needs expansion, or if full recursive comparison becomes needed.

## Changes

### `docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md` — Major revision across 5 commits

**Purpose:** Revise the T-16 fix spec from the invalid `turn/completed.turn.items[]` fallback to an evidence-backed advisory-only `thread/read` fallback with turn-ID lookup and best-effort failure semantics.

**Approach:** Four iterative review rounds with the user, each addressing specific findings. The ticket went from a single-mechanism spec to a three-mechanism analysis with explicit protocol evidence, scope constraints, failure semantics, and 9 implementation tests.

**Key changes:**
- Title: "items-array response shape" → "empty agent_message despite Codex session log containing reply"
- Root cause: separated live notification sources (item/completed, item/agentMessage/delta, turn/completed) from thread/read projection shapes
- Protocol analysis: documented Turn.items schema constraint with citation to TurnCompletedNotification.json:1285
- Mechanism A: post-completion thread/read fallback with turn-ID lookup, advisory-only scope, best-effort failure semantics
- Mechanism B: delta assembly (future enhancement, not primary)
- Mechanism C: item/completed failure-mode investigation (optional diagnostic, not a gate)
- Tests: expanded from 5 to 9 (added fallback failure cases #6-#8, execution-turn isolation #9)
- Closure criteria: require runtime integration test, downstream regression, failure tests, execution-turn isolation
- Evidence language: "committed turn history" → "Codex session log" throughout
- References: ephemeral `/private/tmp` paths → durable repo paths

### `docs/status/codex-collaboration-reconciliation-register.md` — T-16 row updated (3 commits)

**Purpose:** Keep the register's T-16 row coherent with the ticket revisions.

**Key changes:** Updated "Current truth" from "Option A (canonicalize at dispatch)" to "advisory-only thread/read fallback with turn-ID lookup, best-effort failure semantics, 9 implementation tests. Mechanism C is optional." Updated exit condition to reference tests #1-#9.

### `packages/plugins/codex-collaboration/scripts/compare_app_server_schemas.py` — Nested definition tracking

**Purpose:** Mechanically capture property changes in shared definitions (Turn, ThreadItem, Thread) that the top-level comparison misses.

**Approach:** Added `TRACKED_NESTED_DEFINITIONS` constant and `nested_definition_delta()` function. For each direct-runtime-consumed schema file, compares properties of tracked definitions between old and new schema trees. Results appear in the report under `nested_definition_deltas` (only includes definitions with actual property changes).

### `docs/superpowers/specs/codex-collaboration/evidence/2026-04-29-codex-app-server-schema-0.117.0-to-0.125.0-comparison.json` — Regenerated

**Purpose:** Report now includes `nested_definition_deltas` section.

**Key content:** Turn gained `completedAt`, `durationMs`, `startedAt` across 5 files. Thread gained `forkedFromId` in ThreadReadResponse and ThreadStartedNotification.

### `docs/superpowers/specs/codex-collaboration/2026-04-29-codex-app-server-0.125.0-schema-delta.md` — Audit fixes

**Purpose:** Fix three findings from audit: missing Turn property callout, comparison-report limitation note, table separator bug.

**Key changes:**
- Added "Nested Turn definition property additions" section after the direct-runtime-consumed table, documenting completedAt/durationMs/startedAt
- Added note clarifying that `added_props: []` in the report is top-level only, with pointer to `nested_definition_deltas`
- Confirmed Turn.items description unchanged between 0.117.0 and 0.125.0
- Added Thread.forkedFromId callout
- Fixed markdown table separator (3 → 4 columns)

### `docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md` — Failure-path classification

**Purpose:** Distinguish the two runtime failure paths for unsupported server requests.

**Approach:** Added a path-comparison table documenting the parse-failure path (delegation_controller.py:984, minimal unknown record) vs. known-parsed non-parkable path (delegation_controller.py:1072, full-context unknown record). Added failure-path column to the method classification table. Fixed `item/permissions/requestApproval`: it has all required context fields per schema, so it routes through known-parsed non-parkable, not parse-failure. Added `availableDecisions` note.

## Codebase Knowledge

### Files read this session

| File | Why read | Understanding gained |
|------|----------|----------------------|
| `TurnCompletedNotification.json` (0.117.0) | Verify Turn.items constraint | Line 1285: "Only populated on thread/resume or thread/fork." Turn has 4 properties: error, id, items, status |
| `TurnCompletedNotification.json` (0.125.0 scratch) | Cross-version comparison | Turn.items description identical. Turn gained completedAt, durationMs, startedAt (7 properties total) |
| `AgentMessageDeltaNotification.json` | Check undiscussed notification | Shape: {delta, itemId, threadId, turnId}. Runtime has zero handling for this method |
| `ItemCompletedNotification.json` | Verify item/completed shape | Shape: {item: ThreadItem, threadId, turnId}. Runtime captures agentMessage items from this correctly |
| `ItemStartedNotification.json` | Item lifecycle context | Same ThreadItem shape as ItemCompleted, same required fields |
| `ThreadReadResponse.json` | Check Turn definition in thread/read | Turn.items description same ("empty for non-resume/fork"). Turn properties differ from 0.125.0 (gained timing fields) |
| `runtime.py:165-292` | Verify advisory vs execution turn paths | run_advisory_turn: completed-only. run_execution_turn: completed/interrupted/failed. _run_turn: shared with configurable allowed_terminal_statuses |
| `dialogue.py:925-1001` | Check read path and extractor | read() calls read_thread() → processes raw_turns → _read_turn_agent_message handles top-level agentMessage and items[] |
| `approval_router.py:1-112` | Verify parser behavior for reachability ticket | _require_string hard-requires itemId/threadId/turnId. _METHOD_TO_KIND maps 3 methods. Others get kind="unknown" |
| `delegation_controller.py:971-1078` | Trace failure paths for unsupported requests | Two paths: parse-failure (line 984 catch → minimal unknown) and known-parsed non-parkable (line 1072 → full-context unknown) |
| `compare_app_server_schemas.py` (462 lines) | Understand comparison tool capabilities | shape_summary only checks top-level properties. No recursive definition comparison. Added nested_definition_delta to fix this |
| Schema delta analysis (875 lines) | Full audit of user's evidence document | Thorough evidence map with validation matrix, coverage boundary, tracking disposition, pre-pin-upgrade gates, and capability surface map |
| Reachability ticket (86 lines) | Audit of T-20260429-02 | 9 ServerRequest methods classified. Missing failure-path distinction between parse-failure and known-parsed non-parkable |

### Architecture: Codex App Server notification delivery

```
turn/start response
  └─ notification loop (runtime.py:252-292)
       ├─ item/agentMessage/delta: streaming text chunks
       │    ⚠️ UNHANDLED — runtime ignores this method entirely
       ├─ item/completed (268-273): full item capture
       │    └─ if item.type == "agentMessage": agent_message = item.text
       │    ✓ This is the primary path. Works when it fires.
       ├─ server-request handling (264-267): delegate to handler
       └─ turn/completed (274-291): terminal
            └─ Turn.items is ALWAYS [] (per TurnCompletedNotification.json:1285)
            └─ return TurnExecutionResult(agent_message=agent_message)
                 ⚠️ If item/completed never fired, agent_message is ""
```

### Architecture: server request failure paths (delegation)

```
server-request received during _run_turn()
  └─ has "id" and handler is installed? (runtime.py:264)
       └─ _server_request_handler (delegation_controller.py:971)
            ├─ parse_pending_server_request (approval_router.py:36)
            │    ├─ SUCCESS: has itemId/threadId/turnId
            │    │    ├─ method in _METHOD_TO_KIND → kind = command_approval/file_change/request_user_input
            │    │    │    └─ PARKED for operator decision
            │    │    └─ method NOT in _METHOD_TO_KIND → kind = "unknown"
            │    │         └─ KNOWN-PARSED NON-PARKABLE (line 1072)
            │    │              └─ interrupt → terminalize as unknown (full context preserved)
            │    └─ FAILURE: missing required context field
            │         └─ PARSE-FAILURE (line 984 catch)
            │              └─ minimal unknown record → interrupt → terminalize (empty context)
```

### Key locations (post-session)

| Concept | Location |
|---------|----------|
| Turn.items schema constraint | `tests/fixtures/codex-app-server/0.117.0/v2/TurnCompletedNotification.json:1284-1290` |
| item/completed capture (runtime) | `runtime.py:268-273` |
| turn/completed handler (runtime) | `runtime.py:274-291` |
| Advisory turn caller | `runtime.py:162-177` (allowed_terminal_statuses=("completed",)) |
| Execution turn caller | `runtime.py:179-202` (allowed_terminal_statuses=("completed","interrupted","failed")) |
| thread/read projection extractor | `dialogue.py:984-1001` (_read_turn_agent_message) |
| Server request parser | `approval_router.py:36-72` |
| Parse-failure path | `delegation_controller.py:984-1070` |
| Known-parsed non-parkable path | `delegation_controller.py:1072-1078` |
| Comparison script | `packages/plugins/codex-collaboration/scripts/compare_app_server_schemas.py` |
| Tracked nested definitions | `compare_app_server_schemas.py:83` (TRACKED_NESTED_DEFINITIONS) |
| Schema delta analysis | `docs/superpowers/specs/codex-collaboration/2026-04-29-codex-app-server-0.125.0-schema-delta.md` |
| Comparison report | `docs/superpowers/specs/codex-collaboration/evidence/2026-04-29-codex-app-server-schema-0.117.0-to-0.125.0-comparison.json` |

## Context

### Project state (post-session)

| Item | State |
|---|---|
| Branch | `main` at `72d92b22` |
| Working tree | Clean |
| T-20260416-01 (T-16) | **OPEN** — implementation-ready after 4-round protocol revision |
| T-20260429-01 | **OPEN** — Phase 1 sandbox carve-outs next after T-16 |
| T-20260429-02 | **OPEN** — server request reachability classification (new this session) |
| Schema delta analysis | Audited and fixed — nested definition tracking added |
| Reachability ticket | Audited and fixed — failure-path classification added |

### Mental model

This session was about evidence discipline. The T-16 ticket had a plausible-sounding fix spec that targeted a field (`Turn.items`) that's always empty by schema. The only way to catch that was to read the actual schema files rather than trusting the ticket's claim. The same discipline applied to the schema delta audit — the comparison script showed "no changes" at the top level while the nested Turn definition gained 3 useful timing properties.

The pattern: any claim about protocol behavior must be traceable to a specific schema definition or code path, not derived from analogies to how similar systems work. The Codex App Server uses shared type definitions (Turn, ThreadItem) across multiple schema files, but those types behave differently depending on which method returns them. Top-level property equality does not mean semantic equality.

### Environment

- Working tree: `main` at `72d92b22`
- Model: `claude-opus-4-6[1m]`
- macOS Darwin 25.4.0; shell zsh
- Codex CLI: 0.125.0 (schema delta evidence generated against this binary)

## Learnings

### Turn.items is empty for notifications — but the constraint is in the description, not the schema validation

**Mechanism:** The Turn.items field is typed as `array` in the JSON Schema, with no `maxItems: 0` or conditional constraint. The "always empty" rule exists only in the `description` string at TurnCompletedNotification.json:1285. An implementer looking only at the type system would see a normal array field and assume it could contain items.

**Evidence:** Direct schema reads — 0.117.0 and 0.125.0 both have the same description text. No machine-enforced constraint.

**Implication:** Schema descriptions are normative for Codex protocol behavior even when the JSON Schema validation layer doesn't enforce them. Read descriptions, not just types.

**Watch for:** If the description changes in a future schema version (e.g., "populated for turn/completed starting in version X"), the T-16 fix approach would need revisiting.

### The comparison script must recurse into definitions to catch high-signal changes

**Mechanism:** Shared type definitions (Turn, ThreadItem, Thread) appear inside multiple schema files. When a shared type gains properties, every referencing file is marked "changed" but the top-level property comparison shows "no additions." The real change is invisible unless the comparison recurses into definitions.

**Evidence:** TurnCompletedNotification.json showed `added_props: []` in the report while its nested Turn definition gained completedAt, durationMs, startedAt. Fixed by adding `nested_definition_delta()` to the comparison script.

**Implication:** The `TRACKED_NESTED_DEFINITIONS` list must be maintained when new shared types become runtime-relevant.

**Watch for:** Thread gained `forkedFromId` — this could become relevant if fork operations are implemented.

### Two distinct failure paths exist for unsupported server requests

**Mechanism:** `approval_router.py` hard-requires `itemId`, `threadId`, `turnId`. Methods lacking these fields hit the parse-failure path (delegation_controller.py:984) — minimal unknown record with empty context. Methods with all fields but outside `_METHOD_TO_KIND` hit the known-parsed non-parkable path (delegation_controller.py:1072) — full-context unknown record. Both terminalize as `unknown`, but diagnostic quality differs significantly.

**Evidence:** `item/permissions/requestApproval` has all three context fields per schema, so it routes through known-parsed non-parkable, not parse-failure. Other unsupported methods genuinely lack context fields.

**Implication:** When classifying server request behavior, the failure path matters for diagnostic quality and any future support work.

**Watch for:** If new parkable methods are added, they need entries in `_METHOD_TO_KIND` and regression tests.

## Next Steps

### 1. Implement T-20260416-01 extraction fix

**Dependencies:** None — ticket is implementation-ready with 9 tests specified.

**What to read first:** T-16 ticket (fully revised), especially: Mechanism A (thread/read fallback), Turn selection (turn_id lookup), Scope constraint (advisory-only), Failure semantics (best-effort), Implementation tests (#1-#9).

**Approach:**
1. Create `turn_extraction.py` with `extract_agent_message(raw_turn: Mapping[str, object]) -> str`
2. Wire into `dialogue.py:947` (replace `self._read_turn_agent_message`)
3. Add thread/read fallback in `run_advisory_turn()` (or via parameter on `_run_turn()`) — when agent_message is empty and status is completed, call read_thread, find turn by turn_id, extract
4. Best-effort: wrap fallback in try/except, fall through on any failure
5. Write 9 tests per ticket spec

**Acceptance criteria:** Per ticket closure criteria — patch with tests #1-#9, one-run verification (B3 adversarial prompt, confirm convergence or natural termination without parse error).

**Potential obstacles:** `thread/read` projection shape for this failure class is unproven — the post-patch live reproduction is the proof point.

### 2. Implement T-20260429-01 Phase 1 (sandbox carve-outs)

**Dependencies:** Ideally after T-16 (priority #1 in register), but independent.

**What to read first:** `runtime.py:23-58` (sandbox policy builder), `tests/test_runtime.py:178` (regression assertion).

### 3. Classify T-20260429-02 server request reachability

**Dependencies:** None — independent investigation work.

**What to read first:** T-20260429-02 ticket (updated with failure-path classification), schema delta analysis (server request delta section).

### 4. Housekeeping: move T-02 to `closed-tickets/`, fix `CONTRACTS-T02-TEMPORAL-MARKER`

**Dependencies:** None. Both tracked as drift rows in register.

## In Progress

Clean stopping point — all work completed and committed. Working tree is clean on `main`.

## Open Questions

- **Does `thread/read` actually return the agent message for the T-16 failure class?** The Codex session log proves the text existed, but no one has captured a `thread/read(includeTurns=true)` response for a turn where `item/completed` didn't fire. The post-patch live reproduction is the proof point.
- **What causes `item/completed` to not fire?** The B3 notification stream was not persisted. Mechanism C (fresh reproduction with notification-stream logging) would answer this but is optional — the thread/read fallback works regardless of the root cause.
- **Should the comparison script's TRACKED_NESTED_DEFINITIONS list expand?** Currently tracks Turn, ThreadItem, Thread. Other definitions may become runtime-relevant as new capabilities are adopted.

## Risks

### thread/read fallback may be a no-op for the T-16 failure class

**Concern:** The fallback is based on the hypothesis that `thread/read` returns the agent message even when `item/completed` didn't fire during the turn. This is plausible (the session log has the text) but not proven.

**Mitigation:** The fallback has best-effort semantics — if it doesn't work, the existing CommittedTurnParseError path is preserved. The post-patch live reproduction will either confirm or falsify the hypothesis. If falsified, mechanism B (delta assembly) or mechanism C (root cause investigation) become the next candidates.

### Schema scratch evidence is ephemeral

**Concern:** The 0.125.0 schema comparison was generated from scratch trees under `/private/tmp/`. These will be lost on system restart.

**Mitigation:** The comparison report is committed to the repo. The reproduction commands are documented in the schema delta analysis. The comparison script can regenerate against any schema tree.

## References

### Commits (this session, oldest to newest)

| Commit | Type/Scope | Description |
|--------|---|---|
| `be67c1e0` | docs(codex-collaboration) | revise T-20260416-01 fix spec with protocol evidence |
| `1ea8ebb2` | docs(codex-collaboration) | fix symptom conflation, scope fallback, clarify B3 artifact |
| `d2447526` | docs(codex-collaboration) | turn-ID lookup, failure semantics, label cleanup |
| `09012b91` | docs(codex-collaboration) | align evidence claims and reference paths |
| `aed4ab05` | docs(codex-collaboration) | replace ambiguous 'committed turn history' with 'Codex session log' |
| `88f098a1` | docs | capture codex app server schema delta evidence (user commit) |
| `6d0713fa` | docs(codex-collaboration) | add nested definition tracking to schema delta |
| `72d92b22` | docs(codex-collaboration) | distinguish failure paths in T-20260429-02 method table |

### Branch operations

- `fix/t16-protocol-evidence-revision` merged to `main` via fast-forward (6 commits). Branch deleted.
- `fix/schema-delta-nested-turn-properties` merged to `main` via fast-forward (2 commits). Branch deleted.

## Gotchas

### Carried gotchas (from prior sessions, still applicable)

- **`git mv` doesn't restage modified content** — after edit + `git mv`, run `git add <new-path>` to re-stage.
- **`worktree_dirty` blocks promote on untracked files** — stash + promote + pop workaround.
- **`file_change` escalation has empty `requested_scope` payload** — tracked as T-20260429-01 Phase 2-3.
- **Pre-existing Pyright RT.1 (`runtime.py:289`)** — surfaces on every runtime.py edit; not a regression.
- **Test imports use `from server.X`** — `pyproject.toml` has `pythonpath = ["."]`.

### New this session

- **Turn.items constraint is description-only, not schema-enforced** — the "always empty" rule is in a description string, not a validation constraint. Easy to miss if you only read the type system.
- **Top-level schema comparison misses nested definition changes** — comparison script's `shape_summary` checks schema-file properties, not definition properties. Fixed by adding `nested_definition_delta()`, but only for tracked definitions.
- **`item/permissions/requestApproval` has all context fields** — unlike other unsupported methods, it passes the parser and routes through the known-parsed non-parkable path. The method table must distinguish this.

## User Preferences

**Carried from prior sessions (applied this session):**

**Handle commits proactively.** Applied — committed completed chunks without asking. 8 commits across 2 branches.

**Detailed feedback with code citations.** User's review rounds included file:line references, code analysis, and specific improvement recommendations across 4 review iterations.

**New this session:**

**Plain language in conversation.** User responded positively to an ELI5-style audit summary and asked for this to be the default. Saved as global CLAUDE.md instruction and memory record. Key distinction: talk plainly, write precisely — code and documents stay formal, conversational explanations use accessible language with concrete analogies.

## Conversation Highlights

**User on the invalid fallback (round 1, kicking off the whole revision):**
> "The protocol also exposes `item/agentMessage/delta`, which the current ticket does not discuss."
> "Recommended next step: revise the ticket from 'final turn/completed.turn.items[] fallback' to 'dispatch-layer canonicalization, source TBD by protocol evidence.'"

This reframed the entire fix spec from a specific mechanism to an evidence-first analysis.

**User on failure semantics (round 3):**
> "The ticket still does not say what happens if the post-completion thread/read fallback fails [...] An unguarded exception from the fallback would escalate to dispatch-failure semantics, potentially invalidating the runtime and quarantining the handle."

This identified the most important implementation boundary: the fallback must not be worse than the bug.

**User on comparison script enhancement:**
> "Update the generated comparison script/report only if we want the artifact to mechanically capture nested definition property changes. I think we should, because otherwise we will keep relying on prose for one of the highest-signal runtime-consumed deltas."

This drove the script enhancement rather than just adding prose to the document.

**User on plain language:**
> "Is there a way to have you always use plain language in our conversations, like that last explanation?"

Led to the CLAUDE.md instruction and memory record.
