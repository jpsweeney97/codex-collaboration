---
date: 2026-04-21
time: "10:37"
created_at: "2026-04-21T14:37:47Z"
session_id: accb8a97-8a86-43b8-b071-550d08a97363
resumed_from: "docs/handoffs/archive/2026-04-20_23-11_t06-promote-discard-merged-review-fixes-landed.md"
project: claude-code-tool-dev
branch: main
commit: 57c6466a
title: "T-06 PendingEscalationView projection merged — git housekeeping, 818 tests"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_models_r2.py
  - docs/superpowers/specs/codex-collaboration/contracts.md
---

# T-06 PendingEscalationView Projection Merged — Git Housekeeping, 818 Tests

## Goal

Project `codex.delegate.start` and `codex.delegate.decide` escalation payloads through `PendingEscalationView`, eliminating the internal Codex ID leak to callers. This was a contract-hardening prerequisite before the delegate skill/UX work.

**Trigger:** The prior handoff identified PendingEscalationView projection change as the first next step. User provided detailed guidance at session start: the delegate skill will consume these response shapes, so if it's written against today's leaked payloads, it will need rewriting.

**Stakes:** Without this projection, the delegate skill would bake in `codex_thread_id`, `codex_turn_id`, `item_id`, `runtime_id`, `collaboration_id`, and `status` — fields the contracts spec explicitly says must remain internal to the control plane (contracts.md §Logical Data Model). The skill would then require a breaking change when projection is eventually enforced.

**Success criteria (all met):**
1. `start`, `poll`, and re-escalating `decide` all use `pending_escalation: PendingEscalationView` — done
2. Internal IDs absent from all caller-visible payloads — done (pinned by MCP boundary tests)
3. Contracts updated — done (Start Escalation section added, Decide Result updated, sidecar note removed)
4. Full suite green — done (818 tests)

**Connection to project arc:** T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md`. Remaining T-06 ACs: delegate skill UX.

## Session Narrative

**Phase 0 — Git housekeeping (~5 min).** Session started by loading the prior handoff (`2026-04-20_23-11`). Before starting the projection work, the user wanted to address the git status. Four items were on the working tree:

1. `test_execution_prompt_builder.py` — a stale import reorder (moved `PendingServerRequest` from top-of-file to mid-file) carried across 6+ handoffs with unknown origin. No behavioral change. User chose to discard.
2. Three untracked plan docs for already-merged work (T-05 capture, T-06 decide, T-06 poll). User chose to commit.

Discarded the test file via `git restore`. Created `chore/archive-completed-plan-docs` branch, committed the 3 plan docs, fast-forward merged to main, pushed (`012fce44`). Working tree clean.

**Phase 1 — Reading current shapes (~10 min).** User provided detailed analysis of the current state with specific file:line references. Read all cited locations to confirm:

- `PendingServerRequest` (models.py:246) carries 6 internal fields: `runtime_id`, `collaboration_id`, `codex_thread_id`, `codex_turn_id`, `item_id`, `status`
- `PendingEscalationView` (models.py:418) is the clean 4-field projection: `request_id`, `kind`, `requested_scope`, `available_decisions`
- `poll()` already projects via `_project_pending_escalation()` (delegation_controller.py:801)
- `start` handler (mcp_server.py:397) serializes raw `asdict(result.pending_request)` with `"pending_request"` key
- `decide` handler (mcp_server.py:465) does the same for re-escalation
- contracts.md:318 has a sidecar note acknowledging the leak

Traced the dependency chain: `DelegationEscalation` is constructed in one place (delegation_controller.py:1440, inside `_dispatch_execution_turn`). `DelegationDecisionResult` copies from the `DelegationEscalation` at line 1702. The execution prompt builder (`build_execution_resume_turn_text`) takes `PendingServerRequest` as a direct parameter — not via the response model — so it's unaffected by model changes.

**Phase 2 — TDD: RED tests (~5 min).** Created `feature/pending-escalation-view-projection` branch. Wrote 2 new MCP-boundary integration tests:

1. `test_start_escalation_uses_pending_escalation_key` — asserts `pending_escalation` key present, `pending_request` absent, all 6 internal IDs absent from serialized payload
2. `test_decide_reescalation_uses_pending_escalation_key` — same contract for decide approve→re-escalation path

Both failed as expected: `AssertionError: start must use 'pending_escalation' key` — payload had `pending_request` with full leaked internal IDs visible in the error output.

**Phase 3 — TDD: GREEN implementation (~10 min).** Three production files changed:

1. **models.py**: Renamed `DelegationEscalation.pending_request: PendingServerRequest` → `.pending_escalation: PendingEscalationView`. Same for `DelegationDecisionResult`.
2. **delegation_controller.py**: Extracted `_project_request_to_view()` helper from `_project_pending_escalation()`. Used it at both construction sites — `DelegationEscalation` in `_dispatch_execution_turn` and `DelegationDecisionResult` in `decide()`.
3. **mcp_server.py**: Renamed serialization keys `"pending_request"` → `"pending_escalation"` in both start and decide handlers.

New tests passed. Full suite had 1 failure from existing tests referencing old key name.

**Phase 4 — Test fixup (~5 min).** Updated all existing test references:
- Integration tests: `payload["pending_request"]` → `payload["pending_escalation"]`, removed `status` assertion (not in view)
- Controller tests: `result.pending_request` → `result.pending_escalation` across 10+ assertions
- Model tests: Updated `DelegationDecisionResult` construction with `PendingEscalationView`

818 tests passing, ruff clean.

**Phase 5 — Contracts update (~3 min).** Three changes to contracts.md:
1. Added `Start Escalation` response shape section (was undocumented)
2. Updated `Decide Result` table: `pending_request: PendingServerRequest?` → `pending_escalation: PendingEscalationView?`
3. Replaced sidecar note with updated Pending Escalation View description stating all three tools now project through the view

**Phase 6 — Review and merge (~5 min).** User reviewed independently, found no blocking findings. Confirmed the internal `build_execution_resume_turn_text(pending_request=...)` path was correctly left unchanged. Committed at `57c6466a`, merged to main via fast-forward, deleted branch. User declined PR — direct merge.

## Decisions

### Decision 1: Project at the controller boundary, not the MCP serialization layer

**Choice:** Changed the model types (`DelegationEscalation.pending_escalation: PendingEscalationView`) so projection happens inside the controller before constructing the response. The MCP layer just does `asdict()` on an already-clean model.

**Driver:** `poll()` established this pattern — `DelegationPollResult` carries `PendingEscalationView`, projected by the controller. Aligning start and decide to match keeps the boundary consistent. User's guidance: "Add a single projection helper from PendingServerRequest to PendingEscalationView, then use it for poll, start, and re-escalating decide."

**Alternatives considered:**
- **Project at MCP boundary only** — keep models carrying `PendingServerRequest`, project during serialization. Rejected because it leaves the internal models leaky and requires the MCP layer to be a transformer rather than a simple serializer. Also inconsistent with poll's established pattern.

**Trade-offs accepted:** Internal consumers of `DelegationEscalation` (controller tests, the `decide()` re-escalation path) now see the projected view. This means controller-level tests can no longer assert `status` on the escalation result — they must verify status via the store directly. Acceptable because the store is the authoritative source anyway.

**Confidence:** High (E2) — follows the established poll pattern. User confirmed approach.

**Reversibility:** High — single-site projection. Could move back to MCP-boundary projection by reverting models and adding serialization logic.

**Change trigger:** If a future internal consumer needs the full `PendingServerRequest` from the response model (no current consumer does — the prompt builder gets it directly).

### Decision 2: Align all three tools on `pending_escalation` key (not keep `pending_request` with projected value)

**Choice:** Renamed the wire-format key from `"pending_request"` to `"pending_escalation"` across start, poll, and decide.

**Driver:** User presented this as option 1 (cleanest) vs option 2 (more conservative — keep key, change value). User's analysis: "The more conservative option is keeping `pending_request` as the outer key but changing its value to the projected view; that is less clean because it preserves a misleading name."

**Alternatives considered:**
- **Keep `"pending_request"` key with `PendingEscalationView` value** — less breaking for any tooling parsing response keys. Rejected because the key name is misleading (it's an escalation view, not a server request) and no external consumer exists yet (the delegate skill hasn't been written).

**Trade-offs accepted:** Any code referencing `["pending_request"]` in MCP response payloads breaks. This is by design — we're fixing this before the delegate skill bakes in the wrong key.

**Confidence:** High (E2) — no external consumers. The delegate skill (the first consumer) hasn't been written yet. This is the cheapest time to break the contract.

**Reversibility:** High — single key rename in the serialization layer.

**Change trigger:** None foreseen. The name `pending_escalation` accurately describes the projected view.

### Decision 3: Keep `build_execution_resume_turn_text` on full `PendingServerRequest`

**Choice:** The execution prompt builder's function signature stays `pending_request: PendingServerRequest`. Not touched by this change.

**Driver:** The prompt builder is internal (builds the Codex agent's resume prompt). It needs `kind`, `request_id`, and `requested_scope` — all available in `PendingEscalationView` — but it's called from the controller's `decide()` path where the full `PendingServerRequest` is already in hand. Changing it would add complexity without benefit.

**Alternatives considered:**
- **Change to accept `PendingEscalationView`** — would work since it only uses fields present in the view. Rejected because it's an internal interface, the `PendingServerRequest` is already available at the call site, and expanding the view's usage surface beyond caller-visible boundaries would muddy the boundary semantics.

**Trade-offs accepted:** Internal code still uses the unprojected type. This is intentional — the projection boundary is at the controller's response construction, not at internal helper calls.

**Confidence:** High (E2) — user explicitly confirmed: "The only thing I'd avoid changing in this slice is the internal `build_execution_resume_turn_text(... pending_request=...)` path; keeping that on full PendingServerRequest is correct because it is not caller-facing and still needs the authoritative request payload."

**Reversibility:** High — could narrow to `PendingEscalationView` later if needed.

**Change trigger:** If the prompt builder starts being used as a caller-facing API (unlikely — it's deeply internal).

## Changes

### Production files (3 modified)

| File | What changed |
|------|-------------|
| `server/models.py` | `DelegationEscalation.pending_request: PendingServerRequest` → `.pending_escalation: PendingEscalationView`. Same rename on `DelegationDecisionResult`. Docstring updated to describe the projected view. |
| `server/delegation_controller.py` | Extracted `_project_request_to_view(request: PendingServerRequest) -> PendingEscalationView` helper. `_project_pending_escalation()` delegates to it. `DelegationEscalation` construction at line ~1445 and `DelegationDecisionResult` construction at line ~1709 now call the projection helper. |
| `server/mcp_server.py` | `"pending_request"` → `"pending_escalation"` in start handler (line ~400) and decide handler (line ~466). Both use `result.pending_escalation` instead of `result.pending_request`. |

### Spec files (1 modified)

| File | What changed |
|------|-------------|
| `docs/superpowers/specs/codex-collaboration/contracts.md` | Added `Start Escalation` response shape section after Job Busy. Updated `Decide Result` table: `pending_request: PendingServerRequest?` → `pending_escalation: PendingEscalationView?`. Removed sidecar note. Updated Pending Escalation View description to state all three tools project through it. |

### Test files (3 modified)

| File | Tests Added | Tests Updated | Coverage |
|------|------------|---------------|----------|
| `tests/test_delegate_start_integration.py` | +2 | ~6 | MCP boundary: start uses `pending_escalation` key + internal IDs absent; decide re-escalation uses `pending_escalation` key + internal IDs absent |
| `tests/test_delegation_controller.py` | 0 | ~10 | Controller-level `.pending_request` → `.pending_escalation` attribute renames |
| `tests/test_models_r2.py` | 0 | 1 | Model construction updated to use `PendingEscalationView` |

### Housekeeping (1 commit, pushed separately)

| File | What |
|------|------|
| `docs/plans/2026-04-19-t05-pending-request-capture-slice.md` | Committed untracked plan doc (T-05, already merged) |
| `docs/plans/2026-04-19-t06-decide-opening-slice.md` | Committed untracked plan doc (T-06 decide, already merged) |
| `docs/superpowers/plans/2026-04-20-codex-delegate-poll-implementation.md` | Committed untracked plan doc (T-06 poll, already merged) |

## Codebase Knowledge

### Architecture: Projection Boundary

The projection from internal `PendingServerRequest` to caller-visible `PendingEscalationView` happens at the controller's response construction boundary. This is the same layer where `poll()` already projected.

```
Internal (controller + stores):
  PendingServerRequest
    ├── request_id         ←─ kept in view
    ├── runtime_id         ←─ STRIPPED
    ├── collaboration_id   ←─ STRIPPED
    ├── codex_thread_id    ←─ STRIPPED
    ├── codex_turn_id      ←─ STRIPPED
    ├── item_id            ←─ STRIPPED
    ├── kind               ←─ kept in view
    ├── requested_scope    ←─ kept in view
    ├── available_decisions ←─ kept in view (overridden with _PLUGIN_DECISIONS)
    └── status             ←─ STRIPPED

Controller response construction:
  _project_request_to_view(request) → PendingEscalationView
    Used by:
    ├── _project_pending_escalation() → for poll
    ├── _dispatch_execution_turn()   → for start (DelegationEscalation construction)
    └── decide()                     → for re-escalation (DelegationDecisionResult construction)

MCP layer (pure serializer):
  asdict(result.pending_escalation)   ← already clean
```

### Key Implementation Locations

| Concept | Location |
|---------|----------|
| `PendingServerRequest` model | `server/models.py:246` |
| `PendingEscalationView` model | `server/models.py:418` |
| `DelegationEscalation` model | `server/models.py:379` |
| `DelegationDecisionResult` model | `server/models.py:396` |
| `_project_request_to_view()` helper | `server/delegation_controller.py:~801` |
| `_project_pending_escalation()` (poll) | `server/delegation_controller.py:~812` |
| `DelegationEscalation` construction | `server/delegation_controller.py:~1445` |
| `DelegationDecisionResult` re-escalation | `server/delegation_controller.py:~1709` |
| Start handler serialization | `server/mcp_server.py:~397` |
| Decide handler serialization | `server/mcp_server.py:~459` |
| `build_execution_resume_turn_text` (unchanged, internal) | `server/execution_prompt_builder.py:41` |

### Dependency Graph (Projection Slice)

```
delegation_controller.py
  → models.py (DelegationEscalation, DelegationDecisionResult, PendingEscalationView)
  → pending_request_store.py (PendingServerRequest — internal reads)
  → _project_request_to_view() (new helper)

mcp_server.py
  → models.py (DelegationEscalation, DelegationDecisionResult — type checks)
  → asdict() (serialization of already-projected models)

execution_prompt_builder.py
  → models.py (PendingServerRequest — unchanged, direct parameter)
```

### Execution Prompt Builder Interface (Investigated, Unchanged)

`build_execution_resume_turn_text()` at `server/execution_prompt_builder.py:41` takes `pending_request: PendingServerRequest` directly as a keyword argument. It accesses only three fields:

- `pending_request.requested_scope` — JSON-serialized into the prompt (line ~48)
- `pending_request.kind` — rendered as "Escalation kind: {kind}" (line ~59)
- `pending_request.request_id` — rendered as "Request id: {request_id}" (line ~60)

All three fields exist on `PendingEscalationView`, but the function is called from `delegation_controller.py:1682` in the `decide()` approve path, where the full `PendingServerRequest` is already loaded from the store. The prompt builder is never called from MCP-facing code — it's purely internal to the controller's resume-turn dispatch.

### `available_decisions` Override in Projection

The `_project_request_to_view()` helper always sets `available_decisions=self._PLUGIN_DECISIONS` (which is `("approve", "deny")`), regardless of what the raw `PendingServerRequest.available_decisions` contains. The raw request carries the App Server's decision set (e.g., `["accept", "acceptForSession", "acceptWithExecpolicyAmendment", ...]`), but the plugin exposes only the two plugin-level decisions. This override was already present in `_project_pending_escalation()` for poll — the new helper preserves this behavior.

### MCP Boundary Test Pattern

The new tests (`test_start_escalation_uses_pending_escalation_key`, `test_decide_reescalation_uses_pending_escalation_key`) establish a pattern for MCP-boundary contract testing:

1. Define internal IDs as a frozen set
2. Assert the correct key is present AND the old key is absent
3. JSON-serialize the payload value and assert no internal ID field names appear anywhere in the serialized string

This catches both direct field leaks and nested object leaks. The helper `_assert_no_internal_ids(payload, key)` is reusable for future MCP boundary tests.

## Context

### Mental Model

This is a boundary-hardening problem. The internal `PendingServerRequest` carries correlation IDs needed for the control plane's internal routing (matching requests to threads, turns, and items). The caller (the delegate skill) doesn't need these — it only needs enough to render a prompt and route a decision back. The `PendingEscalationView` is the minimal information set for that.

The projection pattern is analogous to a DTO/view model in traditional web frameworks: the internal model is rich, the external contract is minimal. The key architectural choice is WHERE the projection happens — in this codebase, it happens at the controller's response construction, not at the serialization boundary.

### Project State

- **T-05:** COMPLETE. Both slices merged to main at `271f23aa`. 698 tests.
- **T-06 decide:** COMPLETE AND MERGED at `e041c896`. 734 tests.
- **T-06 spec amendments:** COMPLETE AND MERGED at `db7fd1da` (PR #110).
- **T-06 poll:** COMPLETE AND MERGED at `8bae4dde` (PR #111). 765 tests.
- **T-06 sidecar hardening:** COMPLETE AND MERGED at `f9a40366` (PR #112). 771 tests.
- **T-06 promote/discard:** COMPLETE AND MERGED at `27505cc0` (PR #113). 816 tests.
- **T-06 PendingEscalationView projection:** COMPLETE AND MERGED at `57c6466a`. 818 tests.
- **Next T-06 slice:** Delegate skill UX.

## Learnings

### Projection should happen at the controller response construction, not the serialization layer

**Mechanism:** When the controller constructs `DelegationEscalation` or `DelegationDecisionResult`, it calls `_project_request_to_view()` to produce the `PendingEscalationView`. The MCP layer just does `asdict()` — it's a pure serializer with no transformation logic. This matches the pattern `poll()` established with `DelegationPollResult`.

**Evidence:** The alternative (projecting at the MCP layer) would require the MCP server to know about `PendingServerRequest` internals and which fields to strip. This couples the serialization layer to the internal model, defeating the purpose of the projection.

**Implication:** Future response types that need projection should follow this same pattern: project in the controller, use the projected type in the response model.

### Contract hardening before consumer implementation prevents baked-in leaks

**Mechanism:** The user identified this as a prerequisite for the delegate skill, not a simultaneous change. By fixing the contract first, the skill will be written against the correct shapes from the start.

**Evidence:** User's analysis: "If the skill is written against today's start()/decide() payloads, it will bake in the current leak and then need to be rewritten."

**Implication:** When adding a new consumer for an existing API surface, check whether the current surface is the intended one. If there's a known gap (like the sidecar note in contracts.md), fix it before the consumer exists.

### MCP boundary tests should assert absence, not just presence

**Mechanism:** The new tests don't just check that `pending_escalation` has the right fields — they JSON-serialize the entire value and grep for internal field names. This catches nested leaks that field-level assertions would miss.

**Evidence:** The `_assert_no_internal_ids()` helper serializes to JSON and checks for all 6 internal field names in the serialized string. A naive test checking only `"request_id" in esc` would miss a case where, e.g., `requested_scope` contained a nested object with `codex_thread_id`.

**Implication:** For any projection boundary, test both the presence of expected fields AND the absence of internal fields via serialization-level assertions.

## Next Steps

### 1. Delegate skill UX

**Dependencies:** PendingEscalationView projection merged (done).

**What to do:** Build the delegate skill — the Claude-facing UX for the full delegation lifecycle: start → poll → decide → promote/discard. This is the remaining T-06 AC.

**Where to start:** Read the T-06 ticket at `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` for the acceptance criteria. The skill will consume the MCP tool responses, so reference contracts.md for the response shapes (now fully documented including Start Escalation).

## In Progress

**Clean stopping point.** PendingEscalationView projection merged, git housekeeping done, on `main` at `57c6466a` with 818 tests. No work in flight.

## Open Questions

### 1. `git diff --binary` output stability across invocations (inherited)

**Context:** Post-apply verification relies on byte-for-byte comparison of regenerated `full.diff`. The spec noted this may not be stable across git versions. Precheck 6 (hash-based from execution worktree) is the strong guarantee; diff comparison is defense-in-depth.

**Decision pending until:** Production testing reveals whether byte comparison is reliable.

### 2. `turn/interrupt` transport re-entrancy (inherited from T-05)

**Context:** Handler calls `entry.session.interrupt_turn()` from inside `_server_request_handler`. Sends `turn/interrupt` via same transport reading notifications.

**Decision pending until:** Live testing against real App Server.

### 3. `on-request` operational semantics (inherited from T-05)

**Context:** Vendored schema proves `on-request` is a valid `approvalPolicy` value but operational semantics undocumented. Controller defaults to `untrusted`.

**Decision pending until:** Live probe against real App Server.

### 4. Test-results persistence in execution runtime (inherited from poll)

**Context:** The execution prompt instructs the agent to persist at `.codex-collaboration/test-results.json`. If the agent ignores this, all jobs degrade to `"not_recorded"` stubs.

**Decision pending until:** Live execution testing with the amended prompt.

## Risks

### 1. Byte-for-byte diff comparison may be fragile (inherited)

The post-apply verification compares `full.diff` bytes between the execution worktree and primary workspace. If `git diff` output isn't stable across invocations (line endings, hunk headers, binary encoding), verification could produce false failures.

### 2. `DelegationJobStore.update_status` still public (inherited from poll session)

No remaining callers for status-only transitions — all sites use `_persist_job_transition` → `update_status_and_promotion`. Direct `update_status("completed")` would strand `promotion_state=None`.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Tool surface, response shapes (updated this session) |
| Promotion protocol | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | State machine, preconditions, verification |
| Recovery and journal | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Journal phases, WAL ordering, replay rules |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-20_23-11_t06-promote-discard-merged-review-fixes-landed.md`
- T-05/T-06 arc: ... → T-06 promote/discard implementation → T-06 promote/discard review fixes + merge → **T-06 PendingEscalationView projection (this handoff)**

### Commits this session

| Commit | Title |
|--------|-------|
| `012fce44` | chore: add completed plan docs for T-05 capture, T-06 decide, and T-06 poll |
| `57c6466a` | feat(t20260330-06): project start/decide escalation payloads through PendingEscalationView |

## Gotchas

### 1. `build_execution_resume_turn_text` still takes `PendingServerRequest`

**Symptom:** Future developer sees `pending_request=request` in `delegation_controller.py:1682` and thinks it's a missed rename.

**Root cause:** Intentional — the prompt builder is internal and needs the authoritative request payload. The projection boundary is at response construction, not at internal helper calls.

**Prevention:** Don't rename this parameter. It's correct. The prompt builder is not caller-facing.

### 2. MCP boundary tests use JSON serialization for absence checks

**Symptom:** A test might seem redundant — why check JSON serialization when you could check individual fields?

**Root cause:** Individual field checks would miss nested leaks. If `requested_scope` contained a dict that happened to include `codex_thread_id`, a field-level assertion wouldn't catch it. The JSON serialization check catches all leaks regardless of nesting depth.

**Prevention:** Use the `_assert_no_internal_ids()` helper pattern for any future MCP boundary tests. It's defined at the bottom of `test_delegate_start_integration.py`.

### 3. `status` is stripped by projection (inherited behavior)

**Symptom:** Caller can't check escalation resolution status from the MCP response.

**Root cause:** `PendingEscalationView` intentionally omits `status` — the caller doesn't need to know the internal resolution state. The store tracks this. The prior integration test that asserted `status == "resolved"` was removed (it tested an internal field that no longer leaks).

**Prevention:** If caller needs to know whether an escalation was resolved, check job status (`needs_escalation` vs `running`), not the request's internal status.

## User Preferences

### Contract hardening as a prerequisite, not a simultaneous change

User explicitly framed this as: "address this first if the next real work is delegate skill/UX." The projection change was treated as a standalone slice, not part of the skill implementation. This keeps the skill PR clean — it consumes a stable, correct contract rather than simultaneously defining and consuming it.

### Direct merge for small, reviewed slices

User declined a PR for this change: "No need for a PR here." The change was independently reviewed during the session (user ran ruff, pytest, git diff --check, and the full suite before approving). For slices that are reviewed in-session and don't need async/remote review, direct merge to main is preferred.

### Detailed upfront analysis before implementation

User provided 4 specific steps, 6 file:line references, and two ranked options for the key naming decision — all before any code was written. Key verbatim guidance:

- On sequencing: "It's important to do the PendingEscalationView projection change before starting the delegate skill/UX packet. The reason is concrete: this is the response shape the skill will consume."
- On naming: "Cleanest is to align all caller-visible escalation payloads on `pending_escalation: PendingEscalationView` for start, poll, and re-escalating decide."
- On test strategy: "Pin tests at the MCP boundary, not only the controller boundary: start escalation and decide re-escalation should assert that `codex_thread_id`, `codex_turn_id`, `item_id`, `runtime_id`, `collaboration_id`, and `status` are absent."
- On the prompt builder: "The only thing I'd avoid changing in this slice is the internal `build_execution_resume_turn_text(... pending_request=...)` path."

This is the preferred working style: user provides a detailed problem statement and recommended approach, Claude implements with TDD discipline. Not a "figure it out" handoff — a "here's what to do and why" handoff.
