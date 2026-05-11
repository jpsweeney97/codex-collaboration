---
date: 2026-04-27
time: "22:53"
created_at: "2026-04-27T22:53:35Z"
session_id: 5f34fc5c-3eef-437c-8333-04f02b64cb7c
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-27_15-55_packet-1-final-verification-mypy-fixes-pr-created.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: d97eb8e8
title: "PR #126 review cycle 1 — six findings addressed locally, awaiting push approval"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/approval_router.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/pending_request_store.py
  - packages/plugins/codex-collaboration/skills/delegate/SKILL.md
  - packages/plugins/codex-collaboration/tests/test_approval_router.py
  - packages/plugins/codex-collaboration/tests/test_delegate_decide_async_integration.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-{a-h}.md
---

# Handoff: PR #126 review cycle 1 — six findings addressed locally, awaiting push approval

## Goal

Address all six review findings on PR #126 (the Packet 1 closeout PR for T-20260423-02 Deferred-Approval Response) and re-verify the 5-gate suite locally. Land each fix as its own commit. Stop short of pushing — user requested local review before publication.

**Trigger:** User responded to the prior session's "PR #126 created" with a structured `/scrutinize`-style review containing six code comments (1 P1, 4 P2, 1 P3), a Verdict of `Reject`, and the assessment "PR #126 still requires real work. These are genuine contract and runtime holes, not polish nits." User stated explicitly: "PR #126 is far from being ready to merge."

**Stakes:** The Packet 1 closeout from the prior session was at risk. PR #126 had real bugs that the prior gate set didn't catch. Most importantly:
- F1 (P1) was a transport-layer correctness violation — a numeric JSON-RPC request id from the App Server gets responded to as a string, leaving real numeric requests unresolved.
- F2 (P2) had an explicit local reproduction — the user ran a happy approve and observed `[('42:approve', 'approval_resolution', 'intent', '42', 'approve')]` left in `list_unresolved` after the worker completed.
- F3-F6 expose stale consumer contracts (the `/delegate` skill, contracts.md producer list, recovery sweep, discard text) that would silently mislead operators after merge.

**Success criteria:**
- Each finding addressed with a separate commit using `fix(delegate): ...` style messages matching the existing branch convention.
- Wire-id preservation surfaced as both a parser-level test and an end-to-end int-id round-trip test.
- F2 leaves no unresolved approval_resolution after happy decide (the user's reproduction inverted as a regression test).
- Skill text consistent with the new async decide contract from contracts.md §Decide / §DelegationDecisionResult.
- All 5 final verification gates pass locally with merge-base mypy attribution showing zero HEAD-only errors.
- Stop before push (user explicitly wants to review locally before publishing to the PR).

**Connection to project arc:** This is the cycle-1 response on PR #126, which is the closeout PR for Packet 1 of T-20260423-02 (Deferred-Approval Response). Once user re-reviews and approves push, the PR becomes mergeable.

## Session Narrative

Resumed from the prior handoff at HEAD `68a290fb`. The starting state was: Packet 1 implementation complete (22 tasks, 8 phases), suite at 1047/0/0, mypy delta verified zero against merge-base, PR #126 created and pushed. Working tree clean, no work in flight. The prior session's verdict was "defensible" per the user.

The session pivoted immediately on user input. They returned with a `/scrutinize`-style review:

- 6 code comments rendered as `::code-comment{title="[P1] ..." body="..." file="..." start=... end=... priority=... confidence=...}`
- A scrutiny narrative under "## Scrutiny: PR #126" with sections: Premise Check, Critical Failures, High-Risk Assumptions, Real-World Breakpoints And Edge Cases, Hidden Dependencies Or Bottlenecks, Adversarial Perspectives Applied, Patterns And Root Causes, Required Changes Before This Is Credible, Verdict.
- Verdict: `Reject`
- Closing line: "These are genuine contract and runtime holes, not polish nits."

Confidence ratings on the findings ranged 0.87 to 0.96. F2 had an explicit reproduction. F1 had a docstring-vs-implementation contract violation cited.

I invoked the `superpowers:receiving-code-review` skill rather than charging into fixes. The skill's core rule — "verify before implementing, no performative agreement, technical rigor over social comfort" — matched the user's preference for evidence-grounded work. Loaded TaskCreate (deferred), then read all six cited code locations in parallel:

- `delegation_controller.py:1180-1260` (F1 worker dispatch site)
- `delegation_controller.py:2630-2710` (F2 decide journal site)
- `delegation_controller.py:3020-3100` (F5 recovery catch-up)
- `SKILL.md:120-220` (F3 escalation continuation, F4 Tier 4 status table)
- `contracts.md:330-370` (F6 PendingEscalationView producer list)
- `git diff --check origin/main...HEAD` (whitespace finding)

All six findings reproduced. Two needed deeper trace before designing fixes: F1 (PendingServerRequest schema implications for JSONL persistence) and F5 (`_TERMINAL_STATUS_MAP` membership check). Confirmed both:
- `models.py:51` defines `DelegationTerminalStatus = Literal["completed","failed","canceled","unknown"]` — `canceled` IS terminal.
- `delegation_controller.py:119-124` `_TERMINAL_STATUS_MAP` includes `canceled`.
- `approval_router.py:84-91` docstring on `_require_request_id` explicitly states "The respond() transport layer preserves the original wire type for the response" — the implementation does not honor this.
- `runtime.py:248` legacy auto-response path: `self._client.respond(notification["id"], ...)` — passes raw wire id directly, confirming the pre-Packet-1 transport behavior.
- `test_jsonrpc_respond.py:36` already tests int-id preservation at the transport layer — proving the bug is upstream of `JsonRpcClient.respond`.

Built an 8-task plan covering F1-F7 plus a final verification task. Started F1 first because it had the largest blast radius (PendingServerRequest schema change touches JSONL persistence, replay, and 25+ test fixtures).

F1 implementation went smoothly with one mid-stream design choice: rather than passing the raw id alongside `request_id` at every callsite, added a `wire_request_id` property on `PendingServerRequest` that returns `raw_request_id` if set, else `request_id` (the str-form fallback for legacy records). This kept the change to two callsites in `delegation_controller.py` (worker dispatch + timeout cancel) plus the parser, store replay, and minimal-fallback construction. Back-compat was free because Packet 1 had already established the `record.get(field, default)` pattern in the JSONL replay branch.

F1 testing path: extended `test_parse_integer_request_id_normalized_to_string` in `test_approval_router.py` to assert `raw_request_id == 42` and `wire_request_id == 42`; added a string-id parallel; added a legacy-fallback test; added a new end-to-end test `test_worker_respond_preserves_integer_wire_id` in `test_delegate_decide_async_integration.py` that asserts int-typed wire id arrives at the spy.

Hit one editing mistake: my `Edit` for the new end-to-end test matched on `payload = controller._build_response_payload(...)` which was the last line of Test 10 — but Test 10 had a trailing `assert payload == expected_payload` that I orphaned out of scope. pytest caught it (`NameError: name 'payload' is not defined`). Fixed with a small follow-up Edit. Lesson: when appending tests to a file with parametrized prior tests, prefer appending after the entire prior test (look for `\n\n#` boundary markers), not in the middle of a method.

F1 commit at `60bceda4` — 6 files, +175/-18 lines, full back-compat with legacy JSONL.

F2 was a 1-line production fix (`f"{request_id}:{decision}"` → `f"approval_resolution:{job_id}:{request_id}"`) plus updating 3 recovery test sites that used the old key shape. Wrote `test_happy_decide_leaves_no_unresolved_approval_resolution` — the inverse of the user's reproduction. Initially used `entry[1] == "approval_resolution"` (subscript), but Pyright caught it: `list_unresolved` returns `OperationJournalEntry` dataclass objects, not tuples. The user's reproduction format `[('42:approve', ...)]` was their own format, not the API's actual shape. Switched to `entry.operation == "approval_resolution"`. Test passes. F2 commit at `7e4ffd67`.

F3 was a SKILL.md rewrite. The dead "Escalation continuation" paragraph at lines 218-220 was replaced with the new contract: decide is accepted-for-dispatch, decision_accepted is authoritative, poll is the sole observation surface for post-decide state. Updated Approve/Deny verb procedures to render "Decision accepted -- worker is dispatching. Run `/delegate` to check..." and stop, rather than auto-polling inside the skill. Removed the misleading "Handle escalation continuation (step 6f)" references. Commit at `9b05cdce`.

F4 added a `canceled` row to the Tier 4 status table at SKILL.md:134-136 ("Decision dispatch was canceled (typically a timeout or transport failure). `/delegate discard` to clear, then start a new delegation if you still need the work, or `/delegate poll {job_id}` to inspect artifacts.") and updated the discard rejection text to include `canceled` in the allowed-states list. Verified the server-side `_discardable` check at `delegation_controller.py:2340-2343` actually accepts canceled. Commit at `f4c971db`.

F5 added `"canceled"` to the catch-up sweep filter at `delegation_controller.py:3050` and a recovery test `test_recover_startup_emits_for_canceled_jobs_missing_outcome` modeled on the existing `test_recover_startup_emits_for_completed_jobs_missing_outcome`. Commit at `d221efff`.

F6 was a single contracts.md edit: removed `, and codex.delegate.decide` from the PendingEscalationView producer list and added an explicit note that decide returns DelegationDecisionResult and the next escalation is observed via poll(). Combined with F7 (whitespace) into one docs commit. F7 stripped trailing blank lines from 8 phase plan docs to satisfy `git diff --check`. Commit at `d97eb8e8`.

Final 5-gate verification ran into two operational gotchas:
1. The structural invariant grep `rg "raise _WorkerTerminalBranchSignal"` returned 7 (was 6 in the prior baseline). Investigation showed the count includes 1 comment line that mentions the raise; tightening to `^\s*raise` returns 6 actual statements. Verified the prior HEAD (`68a290fb`) ALSO had 7 with the loose pattern — so the count is unchanged. The loose grep was always brittle.
2. The merge-base mypy comparison ran the HEAD mypy command in `/tmp/baseline-mypy` because the cwd from `cd /tmp/baseline-mypy` in the prior command persisted. Both error files were identical from the baseline. Re-ran with explicit cwd from repo root.

After fixing both: gates 1-5 all pass. mypy merge-base attribution confirms zero HEAD-only errors (21 unique error lines on HEAD vs 23 on merge-base; net delta -2, unchanged from prior closeout).

User then requested a handoff (this document) before reviewing the changes.

## Decisions

### Add `raw_request_id` field to `PendingServerRequest` rather than passing alongside or via wrapper

**Choice:** Add a new field `raw_request_id: int | str | None = None` to the `PendingServerRequest` frozen dataclass plus a derived `wire_request_id` property that surfaces the raw id (or falls back to the str-form `request_id` on legacy records).

**Driver:** The two `session.respond` callsites (worker dispatch at `:1204`, timeout cancel at `:1523`) both consume `PendingServerRequest` instances retrieved via the store. Adding the field to the request itself means every callsite that needs the wire id gets the right answer with no plumbing change, and the JSONL replay layer carries the wire type across restarts. The docstring at `approval_router._require_request_id` (`:84-91`) already promised this contract: "The `respond()` transport layer preserves the original wire type for the response." — the field+property design honors that promise.

**Alternatives considered:**
- **Pass raw id as a separate parameter through worker channels** — rejected because it doesn't survive store persistence (timeout cancel can fire after a process restart and replay).
- **Add to `ApprovalEntry` (runtime-side wrapper)** — rejected because it solves only the worker dispatch path, not the timeout cancel path.
- **Inline `req.raw_request_id if req.raw_request_id is not None else req.request_id` at each callsite** — rejected for "self-contained over dependent" tenet — every callsite would need to know about the None semantics, and a future callsite could trivially miss it.

**Implications:**
- `PendingServerRequest` now has 12 nullable Packet-1-introduced fields (was 11). Backward-compat is preserved via the `record.get("raw_request_id")` pattern in `pending_request_store._replay`.
- The `wire_request_id` property is the canonical way for any future code to get the transport id. Reading `req.request_id` directly will give the str-form correlation key, which is correct for storage but wrong for transport.
- Future cross-process state involving wire ids must use this property, not `request_id`.

**Trade-offs accepted:**
- One additional persisted field per pending request — negligible JSONL size impact (a few bytes per record).
- A property on a frozen dataclass adds minor lookup overhead — irrelevant in the worker hot path.
- Tests now have an int-typed assertion (`captured_rid == 42` and `isinstance(captured_rid, int)`) which means a future regression to str-coercion will fail with a type-strict error message rather than just a value mismatch.

**Confidence:** High (E2) — design verified by full test suite (1054 passed, including the new int-id end-to-end test) and by reading the legacy `runtime.py:248` auto-response path which used the raw notification id.

**Reversibility:** High — `wire_request_id` is a property, so removing the field requires only updating the property to return `request_id`. The two production callsites would silently revert to str-form behavior (the original bug).

**Change trigger:** If the App Server JSON-RPC schema ever drops integer ids (currently `anyOf [string, integer]` per `ServerRequest.json:1475`), the field becomes redundant — at that point `wire_request_id` could be removed and `respond` could take `request_id` directly.

### Use `wire_request_id` property over inline fallback at callsites

**Choice:** Encapsulate the "raw_request_id or fallback to str-form request_id" logic as a `@property` on `PendingServerRequest`.

**Driver:** Two production callsites today, but every future code path that needs the wire id must get the right answer. The fallback is a one-liner but it has subtle semantics (None means "legacy record, use str-form") that could be missed by a reader who saw the str fallback and didn't realize int values are valid.

**Alternatives considered:**
- **Inline at each callsite** — rejected (above).
- **Make `raw_request_id` non-Optional and require all callers to pass it** — rejected because legacy JSONL records (pre-fix) genuinely don't have it; forcing non-None would break replay back-compat.
- **Module-level helper function `wire_id(request: PendingServerRequest) -> int | str`** — viable, but a method/property is more discoverable in IDE auto-complete and keeps the abstraction tight to the type.

**Implications:** Future callsites can write `req.wire_request_id` and don't need to know the field exists. The `request_id` field semantics ("str-normalized correlation key for store/MCP/journal") become explicit by contrast.

**Trade-offs accepted:** One extra method on the dataclass. Frozen-dataclass `asdict()` doesn't serialize properties — so JSONL records still only persist `raw_request_id`, not a duplicate field.

**Confidence:** High (E2) — pattern confirmed by reading existing `@property` use at the codebase (model has no other properties in this file, but the pattern is standard Python).

**Reversibility:** High.

**Change trigger:** N/A.

### Use canonical journal key shape `f"approval_resolution:{job_id}:{request_id}"` across decide and worker

**Choice:** Change `decide()` to write its `approval_resolution.intent` record under the same key shape the worker uses for `dispatched` and `completed` records.

**Driver:** F2 finding — the user reproduced the symptom and provided the cause. `OperationJournal` groups by `idempotency_key`. Diverging keys mean the intent stays unresolved on the happy path, leaking into recovery as `recovered_unresolved` (forensically misleading). Every other approval_resolution write site (`:1077, :1091, :1111, :1198, :1238, :1296, :1500, :1517, :1704`) uses the canonical shape; only `decide()` at `:2685` was different.

**Alternatives considered:**
- **Change worker to use `f"{request_id}:{decision}"` shape** — rejected because the worker writes BOTH `dispatched` and `completed`, often with different decisions across re-escalations on the same request_id; the worker's key needs `job_id` for uniqueness across jobs reusing rid "42".
- **Make journal grouping insensitive to key prefix** — rejected as scope creep — would change the journal contract for all callers, not just this one.

**Implications:**
- Recovery's `recovered_unresolved` close path now ONLY fires for genuine orphaned intents (decide wrote intent, then the worker crashed or the process died before completing). Before the fix, EVERY successful decide left a fake "unresolved" entry that recovery would close as `recovered_unresolved`, which had been masking the bug.
- Three recovery tests (`test_recover_startup_marks_intent_only_approval_resolution_unknown`, `test_recover_startup_marks_dispatched_approval_resolution_unknown`, the closes-orphaned-none-decision test) updated to use the new canonical key. Functionally equivalent — recovery doesn't depend on key shape — but consistent with what production now writes.

**Trade-offs accepted:** None — this is a bug fix, not a preference.

**Confidence:** High (E2) — verified by user's reproduction, by my regression test (`test_happy_decide_leaves_no_unresolved_approval_resolution`), and by the full suite passing including all 3 updated recovery tests.

**Reversibility:** Trivial — revert the one-liner.

**Change trigger:** N/A.

### Update existing test wire-id assertions to value-comparison; add dedicated wire-type test

**Choice:** Two existing assertions in `test_delegate_decide_async_integration.py:535` (Test 7) and `:647` (Test 7b) that compared `rid == "42"` are updated to `str(rid) == "42"` (value-focused). A new dedicated test (`test_worker_respond_preserves_integer_wire_id`) asserts type-strict int preservation.

**Driver:** The existing tests' purpose is "the worker dispatched something" and "the L4 wire-shape contract holds for the payload." Their `rid` comparisons were incidental, not the test's contract. Making them tolerant of wire-type variation keeps them focused on their actual purpose. The new dedicated test makes the type contract explicit and gives a clear failure message ("wire id preservation regression: expected int 42, got '42' (type=str)") if the bug ever returns.

**Alternatives considered:**
- **Update the existing tests to assert int** — would work, but couples the test to the wire type for a contract it wasn't supposed to be about. Less informative failure message.
- **Make the comparison `int(call_rid) == 42`** — rejected because rid could legitimately be a non-numeric string ("req-7"), and int() would raise ValueError.

**Implications:** A future change that re-introduces str-coercion would fail the new dedicated test loudly while leaving Test 7/7b passing — making the diagnostic crisp.

**Trade-offs accepted:** Slightly more assertion code in the new test (`isinstance(captured_rid, int) and not isinstance(captured_rid, bool)` to handle Python's bool ⊂ int subclass). Justified for the diagnostic value.

**Confidence:** High (E2) — full suite passes.

**Reversibility:** High.

### Commit each fix individually with `fix(delegate): ...` style messages

**Choice:** 6 commits, one per finding (F6 + F7 combined as docs-only). Each commit message includes the finding number, the priority tag, the reviewer's quoted concern, and the fix approach.

**Driver:** Matches the existing branch commit-history style observed via `git log --oneline` — every prior Packet 1 commit uses `fix(delegate): ...` or `test(delegate): ...` with detailed multi-paragraph bodies. The user's prior reviews referenced commits by hash; per-finding commits make those references precise.

**Alternatives considered:**
- **One mega-commit** — rejected; loses per-finding review trail and makes selective revert impossible.
- **Squash on push** — rejected; user has previously expressed preference for preserving per-task audit trails (per the prior handoff: "consider whether to squash-merge (loses per-task audit trail) or merge-commit (preserves history)").

**Implications:** PR #126 grows from 91 commits to 97 commits. Reviewers can review each fix independently.

**Trade-offs accepted:** Six commit-message overheads instead of one. Worth it for traceability.

**Confidence:** High (E1) — matches the explicit pattern in branch history.

**Reversibility:** High — could squash later before merge if the user prefers.

### Stop before push; do not publish until user reviews locally

**Choice:** Held push and PR-comment actions pending explicit user approval, even though the user's reject implicitly authorized fix work.

**Driver:** Global `~/.claude/CLAUDE.md` rule: "Still ask before: git push, force-push, or anything that publishes commits beyond the local clone." The "Handle commits proactively" memory authorizes commits without asking, but explicitly excludes push.

**Alternatives considered:**
- **Push now, ask forgiveness later** — rejected; violates the durable rule and the user's preference for measure-twice-cut-once on publishing actions.
- **Push and revert if user disagrees** — rejected; force-push would be needed since PR is auto-tracking, even worse outcome.

**Implications:** User saw the full fix surface in this session's text output and can review the 6 commits at their pace. The handoff captures everything they'd need to decide whether to push, request changes, or rerun verification themselves.

**Trade-offs accepted:** One extra round-trip before the PR updates. Minimal cost.

**Confidence:** High (E2) — user explicitly confirmed: "I will review these changes. Save a handoff. I will share my feedback in the next session."

**Reversibility:** N/A.

## Changes

### `packages/plugins/codex-collaboration/server/models.py` — PendingServerRequest gains `raw_request_id` + `wire_request_id` property

**Purpose:** Persist the original JSON-RPC wire id (int or str) alongside the str-form correlation key, with a derived property surfacing the right value for transport.

**Approach:** Frozen dataclass field `raw_request_id: int | str | None = None` added after the existing 11 Packet 1 fields. Property `wire_request_id` returns `raw_request_id` if not None, else `request_id`. Kept defaults safe for legacy records.

**Key implementation details:**
- The None default is intentional — legacy JSONL records don't have this field; replay needs to materialize them without crashing.
- Property docstring documents the fallback behavior.
- `@dataclass(frozen=True)` + property is standard Python; `asdict()` serializes only declared fields, so JSONL records persist `raw_request_id` (the field) but not `wire_request_id` (the property) — correct.

**Future-Claude:** Any new callsite that needs the JSON-RPC wire id MUST use `req.wire_request_id`, not `req.request_id`. The latter is the str-form correlation key (for store/MCP/journal indexing).

### `packages/plugins/codex-collaboration/server/approval_router.py` — extract raw wire id at parse boundary

**Purpose:** Capture the int|str wire id from the App Server message before str-coercion.

**Approach:** Renamed `_require_request_id` to `_extract_wire_request_id` with new return type `int | str` (was `str`). The caller (`parse_pending_server_request`) now does its own `str()` for `request_id` and passes the raw value to `raw_request_id`.

**Key implementation details:**
- Helper docstring updated to note the contract that `respond()` preserves wire type.
- No bool exclusion (kept original permissive behavior — JSON-RPC schema doesn't list bool, but the original code didn't reject it either; out of scope).

### `packages/plugins/codex-collaboration/server/delegation_controller.py` — three production fixes

**Purpose:**
1. Worker dispatch path uses `parsed.wire_request_id` instead of `parsed.request_id` (F1).
2. Timeout cancel path uses `request.wire_request_id` instead of `request.request_id` (F1).
3. Minimal/parse-failure construction at `:948` populates `raw_request_id` when present (F1).
4. `decide()` writes `approval_resolution.intent` under canonical `f"approval_resolution:{job_id}:{request_id}"` (F2).
5. Recovery catch-up sweep at `:3055` includes `"canceled"` in the terminal status filter (F5).

**Approach:** Surgical edits at each site. Comments inline at the change sites explaining the contract (wire-type preservation, key-shape canonicality, terminal status mirroring).

**Key implementation details:**
- The minimal-fallback construction handles the case where the App Server omits `id` entirely (out-of-spec but defensive). In that case `wire_id is None`, `raw_wire_id` stays None, and `wire_request_id` falls back to the synthetic-uuid str-form `request_id`.
- The decide key change is one line; the comment block above it is six lines explaining why the keys must match.
- The catch-up sweep filter expansion is one element added to a tuple; the comment explains the invariant (filter must mirror `DelegationTerminalStatus`).

### `packages/plugins/codex-collaboration/server/pending_request_store.py` — JSONL replay reads `raw_request_id`

**Purpose:** Materialize the new field on replay with defensive type check; legacy records without the field replay with `raw_request_id=None`.

**Approach:** Added `raw_wire = record.get("raw_request_id")` then `raw_request_id = raw_wire if isinstance(raw_wire, (int, str)) else None`. The defensive isinstance check rejects malformed values.

### `packages/plugins/codex-collaboration/skills/delegate/SKILL.md` — F3 + F4 skill migration

**Purpose:** Bring the `/delegate` skill in line with the new async decide contract (F3) and the `canceled` terminal status (F4).

**Approach:**
- F3: Replaced the dead "Escalation continuation" paragraph (lines 218-220 pre-fix) with the new three-paragraph contract: decide returns `DelegationDecisionResult` with `decision_accepted: true` for acceptance, or `DecisionRejectedResponse` for typed rejection; `poll` is the sole observation surface for post-decide state; user-driven re-invocation re-runs Gate 2.
- F3: Updated Approve/Deny verb procedures (lines 259-271) to render "Decision accepted -- worker is dispatching..." on success and stop, rather than auto-polling inside the skill.
- F4: Added a `canceled` row to the Tier 4 status table (between `needs_escalation` and `failed`/`unknown`) with the routing text.
- F4: Updated discard rejection text to include `canceled` in allowed-states list (matching the server's `_discardable` check at `delegation_controller.py:2340-2343`).

**Future-Claude:** The skill is now a reflection of the contracts.md async model. If contracts.md changes the decide contract again, this skill needs to be updated in lockstep — the dead-contract-following bug F3 caught is the canonical example of what happens when they drift.

### `packages/plugins/codex-collaboration/tests/test_approval_router.py` — wire-type preservation parser tests

**Purpose:** Parser-level unit tests for `raw_request_id` and `wire_request_id`.

**Approach:** Three tests: extended int-id test asserts `raw_request_id == 42` and `wire_request_id == 42`; new str-id test asserts string ids round-trip on `raw_request_id`; new legacy-fallback test constructs a `PendingServerRequest` without `raw_request_id` and asserts `wire_request_id` falls back to `request_id`.

### `packages/plugins/codex-collaboration/tests/test_delegate_decide_async_integration.py` — three new integration tests + two assertion updates

**Purpose:**
1. New `test_happy_decide_leaves_no_unresolved_approval_resolution` (F2): asserts `list_unresolved` returns no `approval_resolution` entries after a happy approve completes.
2. New `test_worker_respond_preserves_integer_wire_id` (F1): end-to-end int-id round-trip.
3. Update Test 7 assertion at `:535`: `rid == "42"` → `str(rid) == "42"`.
4. Update Test 7b assertion at `:647`: `call_rid == rid` → `str(call_rid) == rid`.

**Approach:** New tests follow the established `_seed_parked_command_approval` + `respond_spy` pattern from sibling tests. Worker-drain via `threading.enumerate()` + `join(timeout=10.0)`.

**Key detail (F2 test):** `list_unresolved` returns `list[OperationJournalEntry]`, not tuples. Filter by `entry.operation == "approval_resolution"`, then assert empty list. The user's reproduction format `[('42:approve', ...)]` was their own format, not the API shape.

### `packages/plugins/codex-collaboration/tests/test_delegation_controller.py` — recovery key updates + canceled recovery test

**Purpose:**
1. Three recovery-test sites updated from `"42:approve"` to `"approval_resolution:job-1:42"` (F2 consistency — functionally equivalent but matches what production now writes).
2. New `test_recover_startup_emits_for_canceled_jobs_missing_outcome` (F5) modeled on the existing completed/promoted variants.

### `docs/superpowers/specs/codex-collaboration/contracts.md` — F6 stale producer cleanup

**Purpose:** Remove `, and codex.delegate.decide` from the PendingEscalationView producer list at line 352. Add explicit note that decide returns DelegationDecisionResult and the next escalation is observed via poll().

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-{a-h}.md` — F7 EOF blank stripping

**Purpose:** Satisfy `git diff --check origin/main...HEAD` whitespace check across all 8 phase plan docs.

**Approach:** Python `data.rstrip() + b"\n"` to enforce single trailing newline.

## Codebase Knowledge

### Files read this session

| File | Why | What was found |
|------|-----|----------------|
| `delegation_controller.py:1180-1260` | F1 worker dispatch site | `parsed.request_id` (str-coerced) at `:1204` is the F1 bug; same pattern at `:1523` |
| `delegation_controller.py:2630-2710` | F2 decide journal site | `idempotency_key = f"{request_id}:{decision}"` at `:2685` (now `:2685` after fix); doesn't match worker's key shape at `:1188` etc. |
| `delegation_controller.py:3020-3100` | F5 recovery catch-up | `for job in self._job_store.list(): if job.status in ("completed", "failed", "unknown"):` — missing canceled |
| `delegation_controller.py:119-124` | _TERMINAL_STATUS_MAP definition | Maps all 4 statuses including canceled; confirms F5 invariant |
| `delegation_controller.py:2330-2374` | discard server-side _discardable check | Accepts `status in ("failed", "unknown", "canceled")` with null promotion_state |
| `models.py:285-320` | PendingServerRequest dataclass | 11 Packet 1 fields; pattern for adding the 12th cleanly |
| `models.py:51` | DelegationTerminalStatus type | `Literal["completed","failed","canceled","unknown"]` — confirms canceled is terminal |
| `approval_router.py` (whole file) | F1 parse boundary | `_require_request_id` docstring promises wire-type preservation but implementation doesn't honor it |
| `pending_request_store.py:1-80, 200-280` | JSONL replay branch | `record.get(field, default)` pattern is established for new-field back-compat |
| `runtime.py:240-300` | Legacy auto-response path + JsonRpcSession.respond signature | `self._client.respond(notification["id"], ...)` at `:248` confirms pre-Packet-1 transport behavior; `respond(request_id: str | int, ...)` at `:292` accepts both |
| `jsonrpc_client.py:100-130` | JsonRpcClient.respond | Accepts str|int, writes `payload["id"] = request_id` directly to subprocess stdin — preserves wire type at the bottom transport layer |
| `journal.py:319` | list_unresolved signature | Returns `list[OperationJournalEntry]`, not tuples |
| `SKILL.md:120-220, 250-285` | F3/F4 skill sites | Dead decide contract at `:218-220`; missing canceled in Tier 4 at `:134-136`; missing canceled in discard text at `:283` |
| `contracts.md:330-370` | F6 producer list contradiction | Line 352 says decide returns PendingEscalationView; lines 325-335 say decide returns DelegationDecisionResult only |
| `test_jsonrpc_respond.py:36-37` | Existing int-id transport test | Proves the bottom transport layer DOES preserve int — bug is upstream of JsonRpcClient |
| `test_approval_router.py` | F1 test surface | Existing int-id parser test at line 6 normalized to str; perfect site to extend with wire-type assertion |
| `test_delegate_decide_async_integration.py:478, 535, 621-657` | F1 spy pattern + F2 reproduction site | `respond_spy` captures (rid, payload) — assertion `rid == "42"` codified the bug; updated to value-comparison + new dedicated wire-type test |
| `test_delegation_controller.py:2300-2500, 4060-4270` | F2 recovery tests + F5 catch-up tests | 3 sites used `"42:approve"` key shape; canceled variant of catch-up test slotted cleanly into TestRecoveryCatchup class |
| `test_delegation_controller.py:1267-1325` | _command_approval_request fixture | Defaults to int 42 — every existing decide test exercises the int path through the parser; bug was masked by str-only spy assertions |

### Architecture: Wire-id flow (post-fix)

| Stage | What happens | Type |
|-------|--------------|------|
| App Server sends | `{"id": 42, "method": "..."}` | int (or str) per JSON-RPC |
| `_server_request_handler` calls `parse_pending_server_request` | `_extract_wire_request_id` returns raw value | int (or str) |
| `parse_pending_server_request` constructs `PendingServerRequest` | `request_id=str(raw_request_id)`, `raw_request_id=raw_request_id` | request_id: str; raw_request_id: int|str |
| Stored in `PendingRequestStore` | JSONL record persists both fields | as-is |
| `decide()` looks up by request_id | uses str-form correlation key | str |
| Worker reads parsed request from store | replay materializes both fields | as-is |
| Worker calls `entry.session.respond(parsed.wire_request_id, ...)` | property returns int (or str) | int (or str) |
| `JsonRpcClient.respond` writes payload | `payload["id"] = request_id` (no coercion) | int (or str) |
| App Server receives response | matches request id type-exactly | int (or str) |

### Architecture: Journal key grouping (post-fix)

| Operation | Phase | Key shape |
|-----------|-------|-----------|
| approval_resolution | intent | `f"approval_resolution:{job_id}:{request_id}"` (was `f"{request_id}:{decision}"` — F2 bug) |
| approval_resolution | dispatched | `f"approval_resolution:{job_id}:{request_id}"` |
| approval_resolution | completed | `f"approval_resolution:{job_id}:{request_id}"` |
| job_creation | intent/completed | `f"job_creation:{job_id}"` |
| promotion | intent/completed | `f"promotion:{job_id}:{attempt}"` |

All approval_resolution writes use `f"approval_resolution:{job_id}:{request_id}"`. OperationJournal groups by exact key match. After F2, decide's intent groups with worker's dispatched + completed under one key.

### Architecture: Terminal-status invariants

| Type | File:line | Members |
|------|-----------|---------|
| `DelegationTerminalStatus` | `models.py:51` | `completed, failed, canceled, unknown` |
| `_TERMINAL_STATUS_MAP` | `delegation_controller.py:119-124` | Same 4 |
| Recovery catch-up filter | `delegation_controller.py:3055` (after F5) | Same 4 (was 3 before F5 — missing canceled) |
| Discard `_discardable` (status branch) | `delegation_controller.py:2341` | `failed, unknown, canceled` (completed handled by promotion_state branch) |
| Skill Tier 4 routing | `SKILL.md:134-137` (after F4) | `queued/running, needs_escalation, canceled, failed/unknown` |
| Skill discard text | `SKILL.md:283` (after F4) | `failed, unknown, canceled` |

These six locations must stay in sync. Any future addition to `DelegationTerminalStatus` requires touching all six — there's no enforcement, only convention. A future improvement could derive the recovery filter from `_TERMINAL_STATUS_MAP.keys()` to reduce drift risk.

### Pattern: per-finding fix commit style

Branch convention from `git log --oneline`: `fix(delegate): <one-line summary>` with a multi-paragraph body explaining (a) what the reviewer flagged, (b) why it was a bug, (c) the change, (d) tests added, (e) `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` trailer. Each commit independently buildable and reviewable.

### Conventions observed

- New JSONL fields: always nullable/default-safe, replay reads `record.get(field, default)`, fall back is the legacy behavior
- Frozen dataclass + derived property: legitimate pattern (used here for the first time in this codebase, but standard Python)
- Test fixture defaults: `_command_approval_request` uses int 42 by default — every Packet 1 decide test exercised the int path through the parser, and the bug was masked only by str-only spy assertions
- Recovery tests: seed lineage handle + job, optionally write journal records, call `controller.recover_startup()`, assert outcome record presence/content via `outcomes.jsonl` read

### Surprising / counter-intuitive

- The bottom transport layer (`JsonRpcClient.respond`) was already correct — it accepts int|str and writes the payload verbatim. The bug was only in the layers that lost the type before reaching it. This is a "loss at the seams" pattern: when each layer is independently correct but the boundary between layers loses information, no single layer's tests catch the bug.
- The parser docstring at `_require_request_id:84-91` PROMISED the contract that the implementation broke. Bug-by-divergence-from-promise. A future static check could validate that promises like "respond preserves wire type" are tested.
- `time.monotonic()` semantics aren't relevant here, but the analogous lesson is: type-loss at boundaries is silent and pernicious.

## Context

### Mental model

This session's bug class is **boundary fidelity loss**: each layer is internally correct, but information (here, JSON-RPC id type) gets dropped between layers. Packet 1's tests focused on producer-side correctness — what `decide` returns, what the worker dispatches — without enough consumer-side and grouping assertions:

- F1: producer (App Server) sends int; consumer (App Server) needs int back. Plugin lost the type at the parse boundary.
- F2: producer (decide) writes intent; consumer (recovery / forensic readers) reads grouped intent → completed. Plugin used different keys at the producer-vs-consumer boundary inside its own journal.
- F3-F4: producer (server) reshapes contracts; consumer (skill) follows the old contract. Plugin's contract spec and skill text drifted.
- F5: producer (recovery sweep) wants to repair missing outcomes; consumer (analytics) needs canceled outcomes too. Plugin's filter omitted one status.
- F6: producer-list documentation drifted from actual producers. Plugin's contracts.md and code drifted.

The fix pattern is the same in all six: identify the boundary, identify what's lost or contradicted, restore fidelity. Future Packet work should structure verification gates around boundary-fidelity (consumer-side reads, cross-process round-trips, contract-spec parity checks) in addition to producer-side tests.

### Branch state

`feature/delegate-deferred-approval-response` is now 6 commits ahead of where it was at session start (`68a290fb` → `d97eb8e8`). All 6 commits are unpushed. Working tree clean. PR #126 still tracks the old commits (the prior session's `73bf9a3d` and `68a290fb` are the latest visible on the remote).

### Final 5-gate verification results (HEAD `d97eb8e8`)

| Gate | Command | Exit | Result | Detail |
|------|---------|------|--------|--------|
| Final 1: Full pytest | `uv run --package codex-collaboration pytest packages/plugins/codex-collaboration/tests/` | 0 | **PASS** | 1054 passed in 251.16s (was 1047 — net +7: F1 added 4, F2 added 1, F5 added 1, plus parametrize variants) |
| Final 2: mypy merge-base attribution | `comm -23` of line-stripped error sets between HEAD and merge-base `005d4b44` | — | **PASS** | 21 unique HEAD lines vs 23 base lines; 0 HEAD-only errors; net delta -2 (unchanged from prior closeout) |
| Final 3: Structural invariants | `rg` counts | 0 | **PASS** | 6 actual sentinel raises (7 grep-matches with loose pattern; 1 is a comment, same as prior baseline); 4 request_snapshot.status refs; 24 canceled touch points (was 21 — F5 expansion adds 3, correct direction) |
| Final 4: Dialogue regression | `pytest test_dialogue*.py` | 0 | **PASS** | 102 passed in 0.31s (unchanged) |
| Final 5: Integration smoke | `pytest -k integration` | 0 | **PASS** | 78 passed, 976 deselected in 4.26s (was 74 — +4 from new integration tests) |

The closeout statement is unchanged: Packet 1 runtime + structural verification passes; mypy gate exits nonzero due to pre-existing baseline; merge-base attribution shows zero Packet-1+fixes-introduced errors.

### Six commits unpushed

| Hash | Subject |
|------|---------|
| `60bceda4` | fix(delegate): preserve raw JSON-RPC wire id through worker session.respond |
| `7e4ffd67` | fix(delegate): align decide() journal key with worker dispatched/completed key |
| `9b05cdce` | fix(delegate): migrate skill to async decide accepted-for-dispatch contract |
| `f4c971db` | fix(delegate): add canceled to skill Tier 4 routing + discard allowed states |
| `d221efff` | fix(delegate): include canceled in terminal-outcome catch-up sweep |
| `d97eb8e8` | docs(delegate): clean stale decide producer + strip phase-doc EOF blanks |

## Conversation Highlights

**User's review framing was structured `/scrutinize`:**

The user opened with six `::code-comment` blocks (frontmatter-tagged with title, body, file, start, end, priority, confidence), then a free-form scrutiny narrative covering Premise Check, Critical Failures, High-Risk Assumptions, Real-World Breakpoints And Edge Cases, Hidden Dependencies Or Bottlenecks, Adversarial Perspectives Applied, Patterns And Root Causes, Required Changes Before This Is Credible, and Verdict.

Confidence scores: 0.87 (F1), 0.96 (F2), 0.94 (F3), 0.9 (F4), 0.88 (F5), 0.95 (F6).

**The Verdict:** "Reject."

**The closing line:** "PR #126 still requires real work. These are genuine contract and runtime holes, not polish nits."

**F2 reproduction explicitly cited:**

User: "I reproduced this locally after a happy approve: the job reached completed while list_unresolved still returned [('42:approve', 'approval_resolution', 'intent', '42', 'approve')]."

The reproduction shape was the user's own format — `list_unresolved` actually returns `list[OperationJournalEntry]` dataclass objects. The information conveyed was the key shape (`'42:approve'`) and the operation/phase (`'approval_resolution'`/`'intent'`), which is enough to identify the bug. My initial test code subscripted the entry as a tuple before Pyright caught it.

**F1 docstring-vs-implementation citation:**

User: "approval_router.parse_pending_server_request coerces JSON-RPC ids to str for plugin storage. The App Server schema allows integer request ids, and the old runtime auto-response path responded with notification['id'] directly."

This pointed me directly at `runtime.py:248` (the legacy path) and at `_require_request_id` (where the docstring promised the contract that was being violated). Without this hint, I would have spent more time tracing the wire flow.

**User's verdict scale and standard:**

The user used "Reject" as the formal verdict. From the prior handoff: their graduated scale is "Major revision → Minor revision → Defensible → Clean pass." "Reject" sits below "Major revision" — a stronger statement that the work isn't ready to proceed in its current form.

**User's request style on closeout:**

"I will review these changes. Save a handoff. I will share my feedback in the next session"

Unambiguous: stop work, document state, hand control back. No room for "should I push first?" — the answer is no.

## User Preferences

**Verification rigor for closeout claims (durable from prior sessions):** Closeout-grade claims require merge-base evidence. Same-branch deltas don't count. I used the established merge-base methodology this session and it caught zero new errors.

**Distinguish observable facts from attribution claims:** "mypy exits nonzero" ≠ "Packet 1 introduced errors." The fix re-verification preserves this distinction in the gate-results table.

**Recommendation precision over performative agreement:** When the user provides reject-grade feedback, the response is verification + fix + re-verification — not "you're absolutely right" or "let me implement that now." The receiving-code-review skill encodes this and matched user expectations cleanly.

**Per-task commit history matters:** From the prior handoff: "consider whether to squash-merge (loses per-task audit trail) or merge-commit (preserves history)." Same logic applied here — 6 separate commits, one per finding.

**Authority of contracts.md:** The user treated `contracts.md:333-335` (the new async decide contract) as authoritative when calling out F3 and F6 — both findings flag drift between contracts.md and other surfaces (skill, contracts.md producer list). Future Packet work should treat contracts.md as authority and verify other surfaces against it.

**Stop-before-push discipline:** Even with reject-grade feedback that implicitly authorizes fixes, the global rule "ask before push" applied. User confirmed by requesting handoff before reviewing.

**Reproduction provided when feasible:** The user spent time reproducing F2 locally before flagging it. This is signal: when the user does the reproduction work, they want the fix to land precisely, not be re-debated. My response was to write the inverse-as-regression-test (`test_happy_decide_leaves_no_unresolved_approval_resolution`) — which honors the reproduction by ensuring it stays fixed.

## Learnings

### Boundary fidelity loss is a recurring bug pattern in Packet 1's surface area

**Mechanism:** Each plugin layer (parser, store, journal, recovery, skill) is internally tested for correctness, but the interfaces between layers can lose information silently. F1 lost wire type at the parse boundary; F2 lost grouping fidelity at the decide-to-worker journal boundary; F3 lost contract fidelity at the server-to-skill boundary; F5 lost completeness at the recovery-to-analytics boundary; F6 lost documentation fidelity at the spec-to-implementation boundary.

**Evidence:** Six independent findings across one PR all fit the same pattern. Each had layer-internal tests that passed. None had cross-layer fidelity assertions (no test asserted "the int sent to the App Server == the int received back," "intent and completed share a key," "skill behavior matches contracts.md").

**Implication:** Future Packet work should add boundary-fidelity gates to the verification suite: cross-process round-trip tests, contract-vs-implementation diff checks, recovery-vs-status-set parity checks. The current 5-gate suite focuses on producer-side correctness; consumer-side tests would have caught most of these in the prior session.

### Type-strict assertions catch silent type-coercion regressions

**Mechanism:** Python's `==` is value-comparing; `42 == "42"` is False but easy to miss in tests written with str-only fixtures. `isinstance(x, int)` plus the bool-exclusion (`not isinstance(x, bool)` because `bool ⊂ int`) gives a type-strict assertion that fails loudly on coercion.

**Evidence:** The pre-fix Test 7 assertion `rid == "42"` would have failed if the bug were ever fixed naively — masking the fix. The new dedicated test `test_worker_respond_preserves_integer_wire_id` asserts both value AND type, with a failure message that includes the wrong type.

**Implication:** When the contract is type-sensitive, the test should be type-strict. When the test's purpose is "the worker dispatched something" (Test 7's actual purpose), value-tolerant comparison (`str(rid) == "42"`) decouples it from the type contract. Use both kinds of tests at the right sites.

### Existing fixtures using int defaults masked the F1 bug for the entire prior session

**Mechanism:** `_command_approval_request(request_id: int | str = 42)` defaulted to int. Every Packet 1 decide test sent int through the parser. The parser str-coerced. The spy compared with str. Nothing failed — but the bug was present everywhere.

**Evidence:** I found 25+ test sites using the default fixture; not one would have caught F1.

**Implication:** When a fixture has type flexibility (like `int | str`), tests should explicitly cover both paths AND assert the wire-type that actually transits to the consumer. A type-flexible fixture without type-strict assertions creates a false-confidence floor.

### Sentinel-pattern grep counts can be inflated by comments

**Mechanism:** `rg "raise _WorkerTerminalBranchSignal"` counts every match including comments that quote the pattern. Tightening to `^\s*raise _WorkerTerminalBranchSignal` (line starts with optional whitespace then `raise`) excludes comments.

**Evidence:** Loose grep returned 7; tight grep returned 6. Prior baseline at `68a290fb` also returned 7 with loose grep — same comment, unchanged. Manifest expected 6 actual raise sites.

**Implication:** Structural invariant counts in manifests should specify the regex precisely or pre-commit a script that counts AST nodes, not text matches. Loose counts are brittle to documentation additions.

### Shell cwd persists across Bash tool calls within one conversation

**Mechanism:** The Bash tool documentation says working directory persists between commands. A `cd /tmp/baseline-mypy` in one tool call bleeds into subsequent tool calls until explicit `cd` back.

**Evidence:** My merge-base mypy comparison ran the HEAD command from the baseline directory because cwd persisted from the prior `cd /tmp/baseline-mypy`. Both error sets were identical. Symptom: HEAD-only and BASE-only diffs both empty — too-good-to-be-true.

**Implication:** For multi-step shell sequences that involve `cd`, use absolute paths or explicit `cd /Users/jp/Projects/active/claude-code-tool-dev` at the start of each independent command. The Bash tool's persistence is a footgun for diff-style verification flows.

### `git diff --check origin/main...HEAD` reads committed state, not working tree

**Mechanism:** The `origin/main...HEAD` notation means "commits in HEAD but not in origin/main." `git diff` shows changes between commits, not working-tree changes. So whitespace fixes only show as resolved AFTER commit.

**Evidence:** I edited the 8 phase docs to strip blank lines, ran `git diff --check origin/main...HEAD`, and saw the same 8 errors. Confused for a moment until I realized the working-tree edits weren't in any commit yet.

**Implication:** For whitespace-fix verification, run `git diff --check` (working-tree) or `git diff --cached --check` (staged), or commit first then re-run. The `origin/main...HEAD` form is for verifying resolution AFTER committing.

## Next Steps

### 1. User reviews the 6 commits locally

**Dependencies:** None — all commits are local.

**What to read first:** The commit log: `git log --oneline -6 feature/delegate-deferred-approval-response`. Then per-commit diffs in priority order — `60bceda4` (F1, biggest blast radius) first, then `7e4ffd67` (F2), then the others.

**Approach suggestion:** Review the production code changes first (`models.py`, `approval_router.py`, `delegation_controller.py`, `pending_request_store.py`), then the test changes, then the doc changes (`SKILL.md`, `contracts.md`). The handoff captures rationale per commit so the diffs should map cleanly.

**Acceptance criteria:** User decides whether each fix is sufficient, requires additional work, or should be unwound.

**Potential obstacles:** The wire-type field addition is a JSONL schema change. User may want to sanity-check back-compat scenarios beyond the test (e.g., a fresh checkout reading a JSONL file written by the pre-fix branch).

### 2. On user approval: push and add PR comment

**Dependencies:** User approval to push.

**What to do:**
1. `git push origin feature/delegate-deferred-approval-response` — no force-push needed (commits append cleanly).
2. Add a PR #126 comment summarizing the response: per-finding table mapping commit hash → finding ID → fix approach → tests added; final 5-gate re-verification table; explicit note that mypy attribution is unchanged at zero HEAD-only errors.

**Approach suggestion for PR comment:** Match the format of the prior PR body (layered sections of increasing detail). Include the "where the bug was masked" insight for F1 (existing fixtures used int defaults but assertions were str-only) — useful context for any reviewer evaluating whether the fix is structurally complete vs. cosmetic.

**Acceptance criteria:** PR shows the 6 new commits; PR comment is visible; no force-push warnings.

### 3. Post-merge cleanup (carry-forward, deferred)

**Dependencies:** PR merged.

| Item | Description | Status |
|------|-------------|--------|
| RT.1 | `runtime.py:270` Pyright TurnStatus literal narrowing | Pre-existing, not Packet 1-introduced; defer to chore branch |
| TT.1 | `_FakeControlPlane` Pyright issues at multiple `test_delegation_controller.py` instantiation sites | Pre-existing; defer |
| Boundary-fidelity gate suite | Add cross-layer fidelity assertions to verification gates (consumer-side reads, contract-vs-implementation parity) | New deferred work surfaced this session |
| Centralize terminal-status filter derivation | Replace literal tuple at `delegation_controller.py:3055` with `tuple(_TERMINAL_STATUS_MAP.keys())` to prevent F5-style drift | New deferred work surfaced this session |

## In Progress

**Clean stopping point.** All six findings addressed in 6 separate commits on `feature/delegate-deferred-approval-response`. Working tree clean. Final 5-gate verification re-run locally. User explicitly directed: "Save a handoff. I will share my feedback in the next session." No work in flight.

## Open Questions

1. **Does the user want a 7th commit consolidating any of the documentation updates?** F3 (skill) + F6 (contracts.md) are conceptually paired (both bring consumer surfaces in line with the new async decide contract), but they're committed separately. User may prefer that or may want them squashed.
2. **Is the wire-type fix sufficient at the schema layer, or does the user want a contract test that runs the actual App Server subprocess to verify int round-trip?** My new test uses a spy at `session.respond`. A subprocess-level test would prove the integration end-to-end but is more fragile and slower.
3. **Should F5's recovery test exercise the actual crash-mid-emission scenario?** My test seeds a canceled job with no outcome; it doesn't simulate the crash. A more realistic test would use a recorded JSONL with the canceled-but-no-outcome state. Possibly out of scope.
4. **Does "Boundary-fidelity gate suite" deserve its own ticket, or fold into the carry-forward register?** It's a new surface emerging from this session's bug class.

## Risks

### JSONL schema change requires users with pre-fix JSONL to replay correctly

**Risk:** Adding `raw_request_id` to `PendingServerRequest` is a JSONL schema change. Users with checkouts that wrote JSONL records BEFORE this fix would have records without `raw_request_id`. Replay should handle this (the `record.get("raw_request_id")` defaults to None and the `wire_request_id` property falls back to `request_id`), but I haven't tested with an actual pre-fix JSONL file.

**Mitigation:** The test `test_existing_records_replay_cleanly_with_none_defaults` (existing) covers the legacy-record case structurally. Manual smoke test: create a JSONL record without `raw_request_id`, call store replay, confirm `wire_request_id` returns the str-form. Could be added as a regression test.

### F2 fix changes the journal key shape — recovery code adapts but behavior could differ

**Risk:** Recovery code reads orphaned intents and writes the close record under the SAME key the orphaned intent used. So after F2, recovery writes under `"approval_resolution:job-1:42"` (canonical). Any external tooling that parsed journal records and assumed the old key shape would break.

**Mitigation:** No external tooling is known to depend on the journal key shape. The audit/forensic surfaces read by phase, not by key prefix. Risk is low.

### The "boundary fidelity" pattern may have additional unfound instances

**Risk:** This session found 6 boundary-fidelity bugs. The pattern likely repeats elsewhere in the plugin's surface area. A future code review should look specifically for: parse-vs-respond type mismatches, producer-vs-consumer key shape mismatches, contract docs vs implementation drift, status enum vs filter mismatches.

**Mitigation:** Add a dedicated boundary-fidelity audit pass to the next major Packet's verification gate. Defer until then.

## References

| Resource | Location | Purpose |
|----------|----------|---------|
| PR #126 | https://github.com/jpsweeney97/claude-code-tool-dev/pull/126 | Packet 1 PR (current head still at `68a290fb`; new commits unpushed) |
| Packet manifest | `docs/plans/2026-04-24-packet-1-deferred-approval-response.md` | Parent plan with the 5-gate verification checklist |
| Carry-forward register | `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` | Open polish items + new boundary-fidelity gate items |
| Spec design | `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` | Authority for all Packet 1 changes |
| Authoritative contract | `docs/superpowers/specs/codex-collaboration/contracts.md` (after F6) | New async decide contract — skill text now mirrors this |
| receiving-code-review skill | (loaded this session) `superpowers:receiving-code-review` | Methodology used to process the user's review without performative agreement |
| Prior handoff (archived) | `docs/handoffs/archive/2026-04-27_15-55_packet-1-final-verification-mypy-fixes-pr-created.md` | Predecessor session; closeout state at PR #126 creation |

## Gotchas

### `list_unresolved` returns dataclass objects, not tuples

The user's reproduction format `[('42:approve', 'approval_resolution', 'intent', '42', 'approve')]` looks like a tuple, but `OperationJournal.list_unresolved` actually returns `list[OperationJournalEntry]`. Filter and assert via `entry.operation`, `entry.idempotency_key`, etc. — not subscript indices. Pyright catches this immediately if you use the type-checker but pytest will fail with a non-obvious "TypeError: 'OperationJournalEntry' object is not subscriptable" if not.

### Bash tool cwd persists across calls

`cd /tmp/baseline-mypy && uv run mypy ...` in one Bash call leaves cwd at `/tmp/baseline-mypy` for the NEXT Bash call. For diff-style flows that involve running the same command in two locations, use absolute paths or explicit `cd <repo-root>` at the start of each independent command. The "shell cwd was reset" notification appears after a tool call, but the resetting happens only on certain conditions (not every call).

### Adding tests inside parametrized test blocks orphans assertions

When a parametrized test ends with a one-liner assertion (e.g., `assert payload == expected_payload` inside Test 10), inserting a new test before that assertion via `Edit` matching the second-to-last line will orphan the assertion. Defensive approach: match on `\n\n#` (two newlines + comment marker for next test section) rather than the last code line of the prior test.

### `git diff --check origin/main...HEAD` reads committed state

Working-tree edits don't affect the output. To verify whitespace fixes in the working tree, use `git diff --check` (no commit range) or stage and use `git diff --cached --check`. The `origin/main...HEAD` form is for AFTER committing.

### Sentinel raise count includes comment mentions

`rg "raise _WorkerTerminalBranchSignal"` counts comments. Use `^\s*raise _WorkerTerminalBranchSignal` for actual statements only. The discrepancy (7 vs 6) was a false alarm in this session — same as the prior verified baseline.

### The `int|str` type union doesn't catch bool

`isinstance(value, (int, str))` returns True for bools (because `bool ⊂ int`). Wire id is documented as int|str per JSON-RPC, but if a bool somehow arrives, the existing parser code accepts it and `str(True)` becomes "True". Not changed in this session — out of scope — but worth noting.

### `_command_approval_request` fixture defaults to int 42

Every test that calls this without args sends `{"id": 42, ...}` to the parser. Pre-fix, str-only spy assertions hid the wire-type bug. Post-fix, the new dedicated test asserts int round-trip. If you add a new test using this fixture and care about wire type, use the type-strict assertion pattern from `test_worker_respond_preserves_integer_wire_id`.
