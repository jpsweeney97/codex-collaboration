---
date: 2026-04-26
time: "13:26"
created_at: "2026-04-26T17:26:08Z"
session_id: 3ed61089-0ecd-44d1-9245-a44e4e8fe7c4
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: c5829049
title: "Task 18 convergence map dispatch-ready after 4 review rounds + wording pass"
type: handoff
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-26_12-46_checkpoint-task-18-convergence-map-2nd-draft-pending-review.md
files:
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-convergence-map.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-17-convergence-map.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md
  - docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/resolution_registry.py
---

# Task 18 convergence map dispatch-ready after 4 review rounds + wording pass

## Goal

**Bigger picture:** Phase G Task 18 closes the deferred-approval-response Packet 1 mechanism layer. Task 18 rewrites `decide()` with a `reserve()` + `commit_signal()` two-phase reservation protocol, replacing the legacy synchronous `_execute_live_turn`-and-local-finalize approach. This is the second of two Phase G tasks (Task 17 already landed `start()` rewrite at commit `c5829049`).

**Stakes:** Task 18 closes 12 Bucket B retention tests inherited from Task 17 — split across 3 dispositions: 3 close (Mode A defer mechanism-only), 3 DELETE (obsolete CDFE tests under new architecture), 6 RECLASSIFY to new G18.1 carry-forward (finalizer-dependent — Task 19 owns spec §1738-1808 Captured-Request Terminal Guard). Mechanism-level Bucket B closes; finalizer-derived test surface defers to Phase H.

**Trigger:** User checkpointed mid-cycle (handoff `2026-04-26_12-46_checkpoint-task-18-convergence-map-2nd-draft-pending-review.md`) with the 2nd draft of `task-18-convergence-map.md` pending /copy review. User explicitly chose handoff/cycle over inline iteration.

**Project arc context:** This is T-20260423-02 Packet 1, in active development. Following Task 18: dispatch packet drafting → implementer dispatch (`task-18-implementer`, sonnet, `superpowers:subagent-driven-development`) → spec reviewer → code-quality reviewer → 1+1+1 anticipated commit chain (feat + fix + docs).

## Session Narrative

**Starting state:** Loaded checkpoint with branch `feature/delegate-deferred-approval-response` @ `c5829049`, 4 commits ahead of main, untracked working artifact `task-18-convergence-map.md` (512 lines, 2nd draft). Pre-existing carry-forward: G17.1 (9 F16.2 tests Bucket B), RT.1 (`runtime.py:270` Pyright issue), proposed TT.1 (`_FakeControlPlane` Pyright). 1st draft had been restructured per round-1 review (4 P1 dispatch blockers identified; "Option Y narrow scope" adjudication: Task 18 doesn't absorb Task 19's finalizer guard; reclassify 6 tests to G18.1).

**Step 1 — Prime on 2nd draft (per user request):** Read all 512 lines. Performed internal-consistency spot-checks: arithmetic (3+3+6=12 disposition; 999+3+10=1012 passing; 1013-3+10=1020 total), lock numbering (L1-L14, W1-W18), list cross-references (L11 deletes match per-test triage; L12 reclassifies match G18.1 record). All consistent. Flagged 5 spots I'd watch in user's review: L4 Path A feasibility, L5 ReservationToken style choice, L6 grep verification scope, L13 lock-numbering nesting confusion, Restructure Record annotation hygiene.

**Step 2 — Round-2 review (user paste):** User found 2 P1s + 1 P2:
- **P1 (line 222 L13 row):** "Do not assert the worker has not progressed after commit_signal." Inverse ordering claim ("decide() returns BEFORE worker dispatched/observed turn/completed") was an unenforceable race — `commit_signal` is `threading.Event.set()` with no scheduler guarantee.
- **P1 (line 137 test #4):** "abort_reservation does not free the parked worker." Cleanup sentence "Test cleanup calls `abort_reservation` to free the worker" was wrong — `abort_reservation` only restores `awaiting`; doesn't set wake event. Worker stays parked → tests hang on teardown.
- **P2 (line 210 L13):** "L13 still says nine acceptance tests" while L9 has 10.

User answered 4 open questions: keep L11/L12 split; G18.1 as top-level; Restructure Record kept; L9 count stays at 10 but transient-state language must be revised.

**Pivot moment:** I had assumed worker-progress ordering was knowable from outside; user showed me `threading.Event.set()` semantics break that assumption. Same applies to `abort_reservation` — I'd assumed it was a complete release operation, user showed me it's only a state-restore.

**Step 3 — Round-2 fixes applied:** 9 edits — top-of-doc revision marker bump, L9 row #3 reframe (drop transient state), L9 row #4 explicit drain, L9 row #6 explicit drain, L9 row #7 dropped "entry stays in consuming" assertion, L13 row rewrite (only enforceable orderings), L13 opening "9→10", acceptance criteria "9→10", Restructure Record round-2 addendum appended. Doc grew 512 → 524 lines.

**Step 4 — Round-3 review (user paste):** 1 P1 + 1 P2:
- **P1 (line 136-140 tests #3 & #7):** "Follow-up decide rejection is still scheduler-dependent." My round-2 fix introduced a new race: I'd used "follow-up `decide(rid)` returns `request_already_decided`" as proxy for slot-still-claimed in tests #3 and #7. But validation order is `job_not_awaiting_decision` BEFORE `reserve()` — worker post-wake job-status mutation OR `registry.discard(rid)` per `delegation_controller.py:1278` produces wrong rejection reason.
- **P2 (line 137 test #4):** Remove cleanup option (b) `commit_signal(competing_token)` direct — too much flexibility.

User signaled fix split by test purpose: test #3 contract IS the rejection reason → must use deliberate worker-blocking; test #7 contract is non-gating → drop follow-up decide entirely; assert durable side effects.

**Pivot moment:** Realized round-2's "fix" had introduced a deeper race (validation-order trap). Three rejection reasons available depending on worker timing means rejection-reason assertions are inherently flaky without worker-blocking. The fact that worker `discard()` in the steady-state success case produces `request_not_found` — the *opposite* of what the assertion checks — was the lethal detail.

**Step 5 — Round-3 fixes applied:** 5 edits — revision marker bump (round-3 noted), test #3 row mandate "deliberate worker-blocking" with two approved patterns (`_execute_live_turn` monkeypatch OR `session.respond` block), test #4 cleanup option (b) pruned, test #7 dropped follow-up-decide proxy + new durable assertions (success + warning + journal intent + worker dispatch), round-3 addendum appended, round-2 addendum stale clause flagged. Doc grew 524 → 534 lines.

**Step 6 — Round-4 review (user paste):** 1 P1 + 1 P2:
- **P1 (line 136 test #3):** "Approved worker-blocking hooks do not hold the worker early enough." Both round-3 patterns were wrong: monkeypatching `_execute_live_turn` AFTER start has no effect (existing thread already inside); BEFORE start blocks initial park (test never gets pending request); `session.respond` is too late (worker mutates `job.status` to `running` at `delegation_controller.py:1166` BEFORE calling `respond` at `:1187`).
- **P2 (line 547 round-4 addendum, awaiting_decision):** Live pre-decision status is `needs_escalation`, not `awaiting_decision`.

User provided correct mechanism: wrap `job_store.update_status_and_promotion`, gate ONLY the resume call where `status=="running"`, leaving job in `needs_escalation` while second decide reaches reserve().

**Pivot moment:** This was the deepest miss of the session. I'd been reasoning about Python mock-patching as if it bound dynamically, but `setattr` on running-thread method has no effect — the thread is executing the *original* function object. The user had to walk me through both Python semantics AND the live worker code path order (`:1166` → `:1187`) for me to land it.

**Step 7 — Round-4 fixes applied:** 5 edits — revision marker bump, test #3 row total rewrite with correct mechanism + step-by-step protocol + rejected-mechanisms enumeration, round-2 addendum updated to flag round-3 supersession, round-4 addendum appended, round-3 addendum's stale mechanism flagged with "superseded by round-4" cross-ref. Doc grew 534 → 551 lines.

**Step 8 — Wording pass review (user paste):** 2 P2s:
- **P2 (line 547):** `JobStatus.NEEDS_ESCALATION` is invalid — `JobStatus` is `typing.Literal`, not enum; assertion must be `job.status == "needs_escalation"` (string comparison).
- **P2 (line 137 + cascade):** `valid_answers` reads as "valid decision arguments including answers" — implementer might pass `answers` dict on `command_approval`/`file_change` which L3 `answers_not_allowed` rejects.

**Step 9 — Wording fixes applied:** 6 edits cascading the `valid_answers` correction across 5 sites (test #3 step 3, test #4 cleanup, test #6 cleanup, round-2 addendum, round-4 addendum) using canonical phrase "kind-appropriate decision arguments per L3 + L4"; plus `JobStatus.NEEDS_ESCALATION` → `"needs_escalation"` string comparison with `typing.Literal` correction note. Doc remained 551 lines (length-neutral).

**Step 10 — User declared dispatchable; requested /save.** No remaining findings. User noted one carry-forward: "keep L9 test #3's wrapper protocol concise and impossible to miss" in the dispatch packet drafting.

## Decisions

### Decision: Apply each review round via incremental Edits rather than full rewrite

- **Driver:** Multi-round review with chronological revision marker requires preserving prior text as historical record. User said: "keep it. It is useful, and it explains why the task narrowed. I would not trim it before dispatch."
- **Rejected:** Full rewrite per round — would lose Restructure Record + addendum chronology; harder to track which decisions came from which review round.
- **Implication:** Doc grew with addenda + supersession markers but provenance chain is intact. Future Task 19 dispatch can inherit the addendum pattern.
- **Trade-offs:** Doc is longer (551 lines vs ~450 if rewritten flat) and has cross-references between rounds; readers must understand chronology. Accepted because the chronology IS the value.
- **Confidence:** High (E2) — user explicitly approved approach in round-1 review feedback + reaffirmed in round-3 ("supersession language prevents implementers from treating old proxy mechanics as current authority").
- **Reversibility:** Medium — doc could be flattened pre-Task-19, but the chronology becomes irrecoverable once compressed.
- **Change trigger:** If doc becomes >700 lines or if implementers report addendum confusion, flatten before Task 19.

### Decision: Cascade wording fixes beyond explicitly cited lines

- **Driver:** User cited line 137 as canonical example for `valid_answers` issue, but said "Use `valid decision arguments` or say `answers` only when the parked request kind is `request_user_input`" — wording prescription, not single-line scope. Same construct existed in 5 places (test #3, #4, #6, round-2 addendum, round-4 addendum).
- **Rejected:** Strict line-only fix (137 + 547). Would leave 4 other sites with the same misleading wording; an implementer reading test #3 step 3 with `decide(approve, valid_answers)` on a non-RUI parked request would hit `answers_not_allowed` rejection at first decide, breaking the test setup before reaching the actual contract under test.
- **Implication:** Future updates to L3/L4 payload-mapping have a grep-anchor "kind-appropriate decision arguments" across 5 sites.
- **Trade-offs:** 4 extra edits beyond literal user request. User's "I would not require another full convergence-map review unless those edits touch more than the cited sentences" was about scope-creep into NEW problem categories, not about applying SAME fix everywhere it belongs.
- **Confidence:** Medium-High (E1) — scope-creep judgment without explicit user authorization for cascade. Acknowledged in handoff for review if user disagrees.
- **Reversibility:** High — trivial revert of 4 cascade edits if user objects.
- **Change trigger:** User signals "I meant strictly those two lines."

### Decision: Use canonical phrase "kind-appropriate decision arguments per L3 + L4"

- **Driver:** User offered two phrasings: (A) "valid decision arguments" generic, (B) "answers only when parked request kind is `request_user_input`". Generic phrasing works in all 5 contexts; kind-specific phrasing requires per-test kind disclosure (current convergence map doesn't fix kinds for tests #3/#4/#6).
- **Rejected:** Per-site bespoke phrasing — would lose the grep-anchor; harder to update if L3/L4 changes.
- **Implication:** Phrase becomes a maintenance contract — future packets that change `EscalatableRequestKind` literals or payload mapping have a single search term to find related sites.
- **Trade-offs:** Slightly verbose vs spot-replacement; canonical phrase repeats 5 times (intentional for searchability).
- **Confidence:** High (E2) — user offered both phrasings; chose A; verified it reads correctly in all 5 contexts.
- **Reversibility:** High — phrase can be updated globally with replace_all if a better wording emerges.
- **Change trigger:** L3 or L4 spec changes such that kind-specific guidance becomes simpler than the parenthetical.

### Decision: Add Round-N addenda with explicit supersession markers

- **Driver:** Each review round invalidated some prior text. User explicitly cited round-2 addendum's stale clause as needing supersession flag. Same principle applies to round-3 addendum's stale mechanism description.
- **Rejected:** Rewrite addenda in place to remove stale claims — would distort historical record. Or skip supersession flags — would mislead implementers reading top-to-bottom.
- **Implication:** Provenance trail is now templated. Future multi-round-reviewed convergence maps can adopt the same pattern.
- **Trade-offs:** More markers, slightly more reading. Accepted because the markers are surgical (one phrase per stale claim).
- **Confidence:** High (E2) — user's principle explicitly extended round-2 → round-3 supersession; I extended same principle round-3 → round-4 proactively.
- **Reversibility:** High — supersession markers can be stripped if doc is later flattened.
- **Change trigger:** N/A — this is a process precedent, not a doc-mutable choice.

### Decision: Add Round-4 addendum proactively (round-3 → round-4 supersession not explicitly authorized)

- **Driver:** User's principle for round-2 → round-3 addendum supersession applied identically: "Since implementers will read the addenda as process authority, update this sentence to say round 2 attempted that proxy and round 3 superseded it." When round-4 invalidated round-3's mechanism description, same principle applied.
- **Rejected:** Wait for user to explicitly authorize each addendum supersession marker. Would slow review cycles; user already established the pattern.
- **Implication:** Future review rounds (if any) can extend addendum chronology following the templated pattern.
- **Trade-offs:** Slight scope-creep risk if user disagrees with the proactive supersession marker. Offset by transparency in handoff for review.
- **Confidence:** High (E2) — user explicitly approved round-2→round-3 supersession; same principle by analogy.
- **Reversibility:** High — supersession marker can be removed if user objects.
- **Change trigger:** User signals "supersession markers should be explicitly authorized per round."

### Decision: Verify each edit batch via bash grep rather than re-read

- **Driver:** Context budget tight (started at 65k/200k, ended at 96%); re-reading 551-line doc for verification would burn ~5-10k tokens per round.
- **Rejected:** Full re-read after each edit batch. Too expensive for context.
- **Implication:** Verification covered only what grep can detect (string presence/absence, count). Did NOT verify visual layout or table alignment.
- **Trade-offs:** Faster iteration; some risk of layout regressions undetected. Mitigated by Edit's exact-string-match requirement (replacements preserve surrounding structure).
- **Confidence:** High (E2) — grep counts validated each round's edit landing.
- **Reversibility:** High — re-read can be added if visual issues surface.
- **Change trigger:** Implementer reports formatting/layout issues in convergence map.

### Decision: Keep test #4 as deterministic competing-reservation form (round-1 inherited; reaffirmed across all rounds)

- **Driver:** Round-1 user adjudication: "deterministic competing-reservation: test directly calls `controller._registry.reserve(rid, ...)` to force the entry out of `awaiting`". User explicitly rejected timer-race form because timer fires also commit per `resolution_registry.py:393` (non-deterministic).
- **Rejected:** Timer-race form (race against timer-fired commit). Rejected for non-determinism; rejected unregistered-rid form because L3 `request_not_found` validation precedes reserve.
- **Implication:** Test #4 directly probes the registry CAS at `:209-223` rather than going through the full validation chain.
- **Trade-offs:** Tests internal registry state directly, not pure black-box decide(). Accepted because the test's purpose IS the reservation CAS contract.
- **Confidence:** High (E3) — verified through round-1 adjudication; round-3 trimmed cleanup options to single approved pattern.
- **Reversibility:** Low — would require new test design.
- **Change trigger:** If `_registry` becomes private-private (not just private) or if reserve semantics change.

## Changes

### Single file modified

**`docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-convergence-map.md`** (UNTRACKED, 512 → 524 → 534 → 551 lines, length-neutral wording pass)

Specific surgery:
- Top-of-doc revision marker: extended 4 times (round-2, round-3, round-4, wording pass implicit in chronology)
- L9 table rows 3, 4, 6, 7: rewritten across 3 review rounds for race correctness
- L13 row about commit_signal ordering: rewritten round-2 to enforceable orderings only
- L13 opening + acceptance criteria: "9 acceptance tests" → "10 acceptance tests"
- Restructure Record: 3 addenda appended (round-2, round-3, round-4)
- Round-2 addendum line 520: stale clause flagged with "superseded by round-3"
- Round-3 addendum line 530: stale mechanism flagged with "superseded by round-4"
- Round-4 addendum line 547: `JobStatus.NEEDS_ESCALATION` corrected to `"needs_escalation"` string + `typing.Literal` clarification
- 5 occurrences of `valid_answers`: replaced with `controller.decide(approve, ...)` + "kind-appropriate decision arguments per L3 + L4" parenthetical

### Files NOT modified this session

- `delegation_controller.py` (read but not edited; W1, W2, W15-W17 forbid edits beyond Task 18 scope; convergence map is dispatch contract, implementer applies edits)
- `resolution_registry.py` (read but not edited)
- `carry-forward.md` (will be updated by Task 18 closeout-docs)
- `phase-g-public-api.md` (informative-only per L4; binding mappings live in convergence map)
- Spec at `2026-04-23-deferred-approval-response-design.md` (authority; not modified)

## Codebase Knowledge

### Live worker path (verified at HEAD `c5829049`)

| Site | What happens |
|------|--------------|
| `delegation_controller.py:1166` | Worker mutates `job.status` from `needs_escalation` to `running` (post-`commit_signal` wake; FIRST step after registry.wait returns) |
| `delegation_controller.py:1187` | Worker calls `session.respond(payload)` (App Server boundary) |
| `delegation_controller.py:1278` | Worker calls `registry.discard(rid)` on success path (post-respond, post-finalizer) |
| `resolution_registry.py:283` | `discard()` pops the registry entry entirely |

**Implication:** Test #3's deterministic worker-blocking MUST gate at `:1166`'s precondition (the `update_status_and_promotion` call) — `:1187` blocking is too late.

### Validation chain order in `decide()`

```
invalid_decision → job_not_found → job_not_awaiting_decision → request_not_found
  → request_job_mismatch → answers_required → answers_not_allowed → runtime_unavailable
  → THEN reserve() → CAS-on-state-machine-slot
```

**Gotcha:** `job_not_awaiting_decision` rejection-reason STRING is misleading — the actual `JobStatus` literal is `needs_escalation`. The reason name dates from a legacy semantic.

### Registry API surface (live at `resolution_registry.py:209-259`)

Methods: `reserve, commit_signal, abort_reservation, wait, signal_internal_abort, discard`. NO context-manager `reservation()` despite spec §328-339 mention.

| Method | What it does |
|--------|--------------|
| `reserve(rid, resolution)` | CAS-on-`awaiting` → `reserved`; returns token or None if entry not in `awaiting` |
| `commit_signal(token)` | Transitions `reserved` → `consuming`; fires `threading.Event.set()` to wake worker |
| `abort_reservation(token)` | Transitions `reserved` → `awaiting`; **does NOT fire wake event** (tests must drain explicitly) |
| `wait()` | Worker blocks here; releases on `commit_signal`'s event |
| `discard(rid)` | Pops entry entirely |

### `JobStatus` is `typing.Literal`, NOT enum

```python
JobStatus = Literal["needs_escalation", "running", "completed", ...]
```

Assertions: `job.status == "needs_escalation"` (string comparison). NOT `JobStatus.NEEDS_ESCALATION` (would AttributeError at runtime).

### Python mock-patching binding rules

`setattr(controller, '_execute_live_turn', mock_fn)` only affects future *symbol lookups* on the bound object. A thread already executing the original `_execute_live_turn` continues running the original function — patching has no effect. To interpose on a long-running worker, gate at a *per-step boundary the worker crosses* (e.g., `job_store.update_status_and_promotion`), not at the worker's top-level entry.

### Registry state machine (verified at `resolution_registry.py:209-259`)

States and transitions:

| From → To | Trigger | Wake event fired? |
|-----------|---------|-------------------|
| (init) → `awaiting` | `register_request(rid)` | N/A |
| `awaiting` → `reserved` | `reserve(rid, resolution)` returns token | No |
| `awaiting` → (gone) | `discard(rid)` | N/A (no waiter) |
| `reserved` → `awaiting` | `abort_reservation(token)` | **No — worker stays parked** |
| `reserved` → `consuming` | `commit_signal(token)` | **YES — `Event.set()`** |
| `consuming` → (gone) | `discard(rid)` (worker calls on success) | N/A |

**Critical implication for tests:** Only `commit_signal` wakes the worker. Tests that exit decide() through the abort path (journal-intent rollback per L7b, or competing-reservation rejection from a forced reserve) leave the worker parked. Drain via re-call to `decide()` normally OR test hangs on teardown until daemon-thread cleanup at process exit.

**Timer behavior:** Per `resolution_registry.py:393`, the per-request timer ALSO fires `commit_signal` on timeout (with timeout payload). This is why round-1 explicitly rejected timer-race form for test #4 — both decide() commit AND timer fire commit; result is non-deterministic.

### Test fixture conventions (per W4)

- Module-local helper: `_build_controller(tmp_path)` for controller construction
- Built-in pytest fixtures: `tmp_path`, `caplog`, `monkeypatch`
- Mock objects: `unittest.mock.MagicMock`, `unittest.mock.patch.object`
- Forbidden fictional fixtures (do NOT exist in `tests/conftest.py`): `delegation_controller_fixture`, `app_server_runtime_stub`, `journal_spy`, `audit_event_spy` — plan body's pseudocode references these but they're fictional

### Authority order for Task 18 (from convergence map)

1. Spec §Transactional registry protocol (`design.md:250-345`)
2. Spec §Response payload mapping (`design.md:1663-1702`)
3. Spec §decide() semantics (`design.md:1646-1662`)
4. Spec §Captured-Request Terminal Guard (`design.md:1738-1808`) — informational; Task 19 territory
5. Spec §Internal abort coordination (`design.md:347-440`)
6. Spec §Unknown-kind contract (`design.md:1703-1736`)
7. Phase G plan body (`phase-g-public-api.md:290-538`) — code skeleton informative-not-binding
8. Carry-forward state
9. Live code at HEAD `c5829049`

### Per-test triage (final state)

- 3 Bucket B unskip (Mode A defer mechanism-only): `test_delegation_controller.py:1781, :2410`; `test_delegate_start_integration.py:1063`
- 3 DELETE (obsolete CDFE under new architecture): `:2166, :2457, :2509`
- 6 RECLASSIFY to G18.1 (finalizer-dependent): `:1524, :1736, :1825, :1871`; `:856, :933`
- 10 NEW acceptance tests in `tests/test_delegate_decide_async_integration.py`
- 2 F16.1 untouched (Phase H Task 19 owns; per W8): `test_handler_branches_integration.py:161, :179`

Suite expectation: 999+3+10=1012 passing, 8 skipped (6 Bucket C + 2 F16.1), 1020 total.

## Context

**Mental model:** The convergence map is a binding dispatch contract — every line is read-as-authoritative by the implementer. The 4 review rounds + wording pass surfaced layered race conditions that compose: each "fix" introduced a new failure mode that only manifested when reasoning about the *next* layer down (Event.set() semantics → validation-order race → mock-patching binding → status-name vs reason-name confusion). The supersession-marker pattern preserves the chronology of these layered discoveries.

**Core insight:** Multi-round review on a complex spec is not "find all bugs" — it's "trace each layer of the operational contract until reasoning grounds out in code-mechanics." Each round had to address what the prior round had implicitly assumed. The earliest unsound assumption that took the longest to surface was "Python mock-patching binds dynamically" (round-4 finding), which was hidden until the user walked through the live worker thread's execution flow.

**Framing analogy:** Think of the convergence map as a multi-layer contract where each layer has its own fault-injection mode — registry mechanics layer, validation chain layer, threading/Event layer, Python binding layer, type-system layer (Literal vs enum). The dispatch is ready when each layer's failure modes are explicitly documented and the test contract avoids each one.

## Learnings

### Patterns

- **Supersession-marker pattern for multi-round review:** Add Round-N addenda chronologically; flag stale claims in earlier rounds with "superseded by round-N+1" cross-refs in-place. Future implementers reading top-to-bottom encounter chronological history with always-current pointers.
- **Canonical phrase as grep-anchor:** When the same wording fix applies to N sites, use a single canonical phrase across all N rather than bespoke variations. Future maintainers grep one phrase to find related sites.
- **Cascade boundary judgment:** User citing line X for a wording issue MAY mean "fix everywhere this wording occurs" (same problem class, different lines) or "fix only line X" (canonical example). Default to cascade if the prescribed fix has no per-site dependency, and flag in handoff for review.

### Gotchas

- **`abort_reservation` does NOT wake.** Worker stays parked in `registry.wait()` after abort. Tests that exit decide() through abort path need explicit drain (re-call `decide()` normally) or worker hangs on teardown until daemon-thread cleanup at process exit.
- **`commit_signal` is `threading.Event.set()` — no scheduler guarantee.** Worker may complete dispatch + observation before `decide()`'s post-commit audit returns. Tests cannot assert `decide()` returns BEFORE worker progresses.
- **Validation-order trap for follow-up `decide()` probes.** Three rejection reasons available depending on worker timing (`job_not_awaiting_decision`, `request_not_found`, `request_already_decided`). Probing post-decide state via second `decide()` is inherently flaky without worker-blocking.
- **`_execute_live_turn` patches don't reach running threads.** Patch the symbol AFTER start = no effect; BEFORE start = blocks initial park. Use `job_store.update_status_and_promotion` wrap (per-step boundary) instead.
- **`JobStatus.NEEDS_ESCALATION` does NOT exist as an attribute.** `JobStatus` is `typing.Literal`; assertions are string comparisons.
- **`valid_answers` is misleading wording.** L3 `answers_not_allowed` rejects any `answers` payload on `command_approval`/`file_change` kinds. Test fixtures must pass kind-appropriate decision arguments.

### Conventions

- Convergence maps in this project use Live anchors table at the top, then Locks (positive scope) → Watchpoints (negative scope) → Branch matrix → Per-test triage → Acceptance criteria → Pre-dispatch checklist → Commit shape → Carry-forward expectations → Restructure Record/addenda.
- Lock numbering crosses tasks: Task 18's L13 inherits from Task 17's L12; documented as "L13 — L12 (Task-17-inherited)".
- Cross-task carry-forward records (G18.1) are inherited verbatim by the receiving task's convergence map; this convergence map encodes Task 19's prep into Task 18's deliverables.

### Connections

- `decide()` → `_registry.reserve()` → journal intent → `_registry.commit_signal()` → audit (non-gating) → return success
- Worker (after wake): `update_status_and_promotion("running")` at `:1166` → `session.respond(payload)` at `:1187` → on success: `_finalize_turn` (kind-based escalation pre-Task-19) → `registry.discard(rid)` at `:1278`
- `abort_reservation(token)` is called ONLY from the journal-intent rollback path in `decide()`; NEVER from audit failure (per L7b)

## Next Steps

1. **Draft Task 18 dispatch packet** (~340 lines mirroring Task 16/17 precedent). Structure: dispatch-target frontmatter + scope summary + spec excerpts + plan body inline + convergence map inline + reporting contract + agent invocation block. **User-flagged emphasis:** keep L9 test #3's wrapper protocol (the `job_store.update_status_and_promotion` mandate with step-by-step protocol) concise and impossible-to-miss in the packet — it's the most implementation-sensitive test mechanic.
2. **Two-read review** the dispatch packet (anticipate multi-round per convergence-map precedent).
3. **Dispatch implementer:** `task-18-implementer` agent, sonnet model, `superpowers:subagent-driven-development` workflow.
4. **Sequential review chain:** spec reviewer → code-quality reviewer (per L13 process precedent feedback memory).
5. **Anticipated commit chain:** 1+1+1 (feat + fix + docs).
6. **Post-Task-18 closeout-docs:** carry-forward updates (G17.1 dispositioned; Mode A row CLOSED; F16.2 stays Open via G18.1 lineage; new G18.1 entry; TT.1 formal promotion; RT.1 unchanged).

## In Progress

**Status:** Convergence map LANDED at 551 lines, dispatchable per user. Dispatch packet drafting NOT YET STARTED.

- **Approach:** Two-read review per round (user /copy paste of code-comment blocks); my role is apply-and-verify Edit cycle. Pivots happen each round on layered race conditions. Restructure Record + addenda preserve chronology.
- **State:** Convergence map dispatchable. Branch unchanged at `c5829049`. Untracked working artifact pending commit alongside Task 18 closeout-docs (NOT a separate commit — bundled with closeout-docs per round-1 dispatch checklist).
- **Working:** All 4 review rounds + wording pass applied. Internal-consistency audit passed. No remaining findings.
- **Not working/incomplete:** Dispatch packet does not exist yet. Pre-Task-18 dispatch checklist items (16 items in convergence map's "Pre-dispatch checklist") are not yet validated against an actual packet draft.
- **Open question:** Should dispatch packet inline the convergence map verbatim (Task 17 precedent) or just cite + key-excerpts? Lean toward inline per precedent.
- **Next action:** Draft dispatch packet section-by-section; emphasize L9 test #3 wrapper protocol per user note; present for two-read review.

## Open Questions

- **Inline vs cite for convergence map in dispatch packet?** Task 17 precedent inlines. Doing so for Task 18 means 551 lines inside the packet — increases packet size to ~890 lines. Could compress to convergence-map-cite-with-excerpts for size, but loses the dispatch-self-contained property.
- **Test #3 wrapper protocol prominence in packet?** User said "keep it concise and impossible to miss." Options: dedicated callout box; bold-italic step list at top of L9 section; pre-dispatch checklist line item.
- **Should commit shape change?** Round-4 addendum complexity (worker-blocking mechanism specificity) might push closeout-docs review surface beyond 1+1+1. Could be 1+2+1 if implementer review surfaces 2 fix categories.
- **Path A verification artifact source?** L4 mandates implementer verifies non-empty RUI approve answers wire shape against App Server. Implementer may report BLOCKED if App Server source unavailable in-scope. Pre-flag this risk in dispatch packet.
- **Round-2 addendum's `valid_answers` mention** — I updated it to use the new canonical phrase, but this means round-2 addendum text doesn't match what round-2 ACTUALLY said (it said `valid_answers`). Tension: chronological preservation vs current accuracy. Currently leaning toward current-accuracy (wording fixes in addenda are NOT substantive claim changes). User may want this revisited.

## Risks

- **Multi-round review precedent applies to dispatch packet too.** 4 rounds + wording pass on convergence map suggests packet may take 2-3 rounds. Plan time accordingly.
- **L4 Path A BLOCKED is plausible.** App Server source may not be accessible to implementer in-scope. Pre-flag in dispatch packet preamble.
- **Test #3 mechanism complexity.** 5-step protocol with explicit gating; implementer may need careful walkthrough. Mitigate via packet emphasis per user note.
- **Implementer may surface BLOCKED for unforeseen blocking patterns.** The convergence map enumerates 3 rejected mechanisms; if implementer finds the wrap-`update_status_and_promotion` pattern doesn't work in their test environment (e.g., monkeypatch on the job_store doesn't propagate to the running worker thread), they'd hit a wall. Mitigate via packet noting the wrap can be applied at controller construction time before worker spawn.
- **Stale spec line citations.** Convergence map cites `delegation_controller.py:1166, :1187, :1278` and `resolution_registry.py:283` — these are HEAD-`c5829049` line numbers. If implementer-feat lands on a different commit base, citations shift. Standard for plan-body line citations across all locks.
- **Context budget on packet drafting session.** This save is happening at 96% context; next session starts fresh. Packet drafting is ~340 lines + multi-round review; should fit in fresh context but watch for compression near end of session.

## References

### Prior handoffs (chain)

- **Resumed from:** `docs/handoffs/archive/2026-04-26_12-46_checkpoint-task-18-convergence-map-2nd-draft-pending-review.md`
- Earlier in chain: `2026-04-26_07-02_phase-g-task-17-dispatch-and-closure.md` (Task 17 closeout)

### Active plan / spec

- **Convergence map (active):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-convergence-map.md`
- **Plan body:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md:290-538`
- **Carry-forward:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md`
- **Spec authority:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`
- **Task 17 convergence map (precedent):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-17-convergence-map.md`

### Live code

- `packages/plugins/codex-collaboration/server/delegation_controller.py` @ HEAD `c5829049`
- `packages/plugins/codex-collaboration/server/resolution_registry.py` @ HEAD `c5829049`
- Tests: `packages/plugins/codex-collaboration/tests/test_delegation_controller.py`, `tests/test_delegate_start_integration.py`, `tests/test_handler_branches_integration.py` (untouched per W8)
- New file (Task 18): `packages/plugins/codex-collaboration/tests/test_delegate_decide_async_integration.py`

### Memory entries

- `feedback_bucket_reclassification_requires_blocked.md` (L13 process precedent)
- `feedback_assertion_shape_implementer_discretion.md` (L12 precedent)
- `feedback_subagent_driven_development_meaning.md` (full review chain workflow)

## Gotchas

- **Test #3 wrapper protocol gates at `:1166` precondition (the `update_status_and_promotion` call), NOT at `:1187` (`session.respond`).** Round-3 had this wrong; round-4 corrected.
- **`abort_reservation(token)` does NOT wake the worker.** It only restores `awaiting`. Tests need explicit drain via re-call to `decide()` normally.
- **`JobStatus` is `typing.Literal`. Assertions use string comparison.** `JobStatus.NEEDS_ESCALATION` AttributeErrors at runtime.
- **`commit_signal(competing_token)` direct cleanup path is FORBIDDEN.** Routes test-held fake `DecisionResolution` payload through worker `respond` — artificial cleanup mechanism. Pruned in round-3.
- **Plan body's `phase-g-public-api.md:498-505` payload-helper code has 2 spec defects:** `"reject"` should be `"decline"`; unconditional `dict(answers or {})` should be `{"answers": {}}` empty-fallback for deny on RUI. L4 binds the spec table; plan body is informative-not-binding.
- **Pre-Task-18 carry-forward state must be intact at dispatch.** G17.1 (9 F16.2 Bucket B), RT.1, proposed TT.1. Closeout-docs disposition tracker must update these (G17.1 retires; F16.2 stays Open via G18.1 lineage; TT.1 formal promotion; RT.1 unchanged).
- **W3 invariant:** `grep -nF "_WorkerTerminalBranchSignal(reason=" delegation_controller.py | wc -l` returns `6` post-Task-18.
- **W17 invariant:** `grep -c "DelegationEscalation(" delegation_controller.py` returns `1` post-Task-18 (only `:837`).

## Conversation Highlights

User's framing across rounds was consistent and forensic:

- Round-2 P1: "After commit_signal fires the registry event, the worker is allowed to run immediately while decide() is still doing post-commit audit/logging. So Task 18 can assert intent-before-commit and can assert decide() does not wait for finalizer-derived terminal state, but it cannot assert decide() returns before worker dispatches or observes turn/completed unless the test deliberately blocks the worker."
- Round-2 P1: "The deterministic competing-reservation test shape is good, but the cleanup sentence is wrong: abort_reservation only moves reserved -> awaiting and does not set the event, so the worker remains parked in registry.wait()."
- Round-3 P1: "Tests #3 and #7 still rely on a follow-up decide(rid) returning request_already_decided, but after commit_signal the worker may set the job to running before the second decide reaches validation, producing job_not_awaiting_decision instead."
- Round-4 P1 (the deepest miss): "Monkeypatching _execute_live_turn after start has no effect because the existing worker thread is already inside that method; monkeypatching it before start blocks the initial park and the test never obtains the pending request. Blocking session.respond is also too late: the worker sets job.status='running' at delegation_controller.py:1166 before calling respond at :1187, so the second decide can still fail validation with job_not_awaiting_decision."
- Round-4 P2: "JobStatus is a Literal, not an enum. The substantive correction is right, but this sentence tells the implementer to write JobStatus.NEEDS_ESCALATION. Live JobStatus is a typing.Literal."
- Wording-pass P2: "The cleanup guidance says to call controller.decide(approve, valid_answers) after aborting a reservation. For command_approval/file_change requests, answers remain rejected by L3's preserved non-RUI answers_not_allowed branch."

User's verdict at end: "I would treat task-18-convergence-map.md as dispatch-ready now. The only thing I'd carry into the dispatch packet is to keep L9 test #3's wrapper protocol concise and impossible to miss, because that is still the most implementation-sensitive test mechanic."

## User Preferences

- **Multi-round review with /copy paste:** User prefers structured code-comment blocks with file:line citations, priority levels (P1/P2), and confidence scores. Pattern: paste review → I apply edits → next paste with new round's findings.
- **Verbatim mechanism specifications:** User pushes for code-grounded line citations rather than vague "block the worker somewhere appropriate". User said: "block the resume worker before that status mutation, for example by wrapping job_store.update_status_and_promotion after the initial park and gating only the post-commit status='running' call."
- **Chronology preservation in docs:** User explicitly wants Restructure Record kept; addenda chained rather than rewritten. User said: "keep it. It is useful, and it explains why the task narrowed. I would not trim it before dispatch."
- **Dispatch readiness gating:** User signals dispatchable explicitly with phrase variants like "dispatch-ready" or "dispatchable". Does not greenlight implicitly.
- **Scope discipline within rounds:** User said: "I would not require another full convergence-map review unless those edits touch more than the cited sentences." Wording-only cascade is OK; structural changes trigger re-review.
- **Architectural precision over speed:** User finds residual issues round-after-round; values getting it right over moving to dispatch quickly. 4 rounds + wording pass on a single convergence map is not unusual for this user.
- **Spec-vs-plan disambiguation:** User trusts spec authority over plan body where they conflict. Plan body informative-not-binding has been a recurring theme (round-1 P1.1 + L4 plan-body defects).

## Rejected Approaches

### Inverse worker-progress ordering claim (round-2 cut)

- **Tried:** L13 row asserting "main-thread `decide()` returns AFTER `commit_signal` but BEFORE worker has dispatched/observed `turn/completed`."
- **Failed because:** `commit_signal` is `threading.Event.set()` with no scheduler guarantee. Worker may run to completion before decide()'s audit returns. The race is unenforceable without deliberate worker-blocking.
- **Learned:** Tests cannot assert worker-progress ordering relative to decide() return without explicit gating. Forward-only orderings (intent-before-commit) and negative orderings (no waiting on finalizer) are the only enforceable shapes.

### Follow-up decide as proxy for slot-still-claimed (round-3 cut)

- **Tried:** Tests #3 and #7 used "second `decide(rid)` returns `request_already_decided`" to prove the reservation slot stayed claimed.
- **Failed because:** Validation chain runs `job_not_awaiting_decision` BEFORE `reserve()`. Worker post-wake mutates `job.status` to `running`, making second decide reject with the wrong reason. On success path, `discard()` produces `request_not_found` — the *opposite* of the intended assertion.
- **Learned:** Probing post-decide registry state via second `decide()` is inherently flaky without worker-blocking. Three rejection reasons are available depending on timing. Use direct `_registry.reserve()` if you must probe slot state, OR assert durable side effects (journal entries, mocked-boundary captures) instead.

### `_execute_live_turn` and `session.respond` blocking patterns (round-4 cut)

- **Tried:** Round-3 specified two approved blocking patterns for test #3: monkeypatch `_execute_live_turn` OR block `session.respond`.
- **Failed because:** Patches on `_execute_live_turn` after start don't reach the running thread (Python binding rules); before start blocks initial park. `session.respond` is too late — `:1166` `update_status_and_promotion` precedes `:1187` `respond`.
- **Learned:** Mock-patching binding is dynamic at lookup time, not instance time. To interpose on a long-running thread, gate at a per-step boundary the worker crosses (job_store-level operation), not at the worker's top-level entry.

### Direct `commit_signal(competing_token)` cleanup option for test #4 (round-3 cut)

- **Tried:** Round-2 listed two cleanup patterns for test #4: (a) abort + decide-normally, (b) commit_signal direct on competing token.
- **Failed because:** Option (b) routes test-held fake `DecisionResolution` payload through worker `session.respond` dispatch. Technically a wake, but tests an artificial cleanup path rather than production decide semantics.
- **Learned:** When test cleanup must drive production semantics, restrict to the production drain path; flexibility-options that bypass it test the wrong thing.

### Strict line-only fix interpretation (wording pass — considered, rejected)

- **Tried (considered):** Apply user's wording fixes only at literal cited lines (137 + 547).
- **Failed because:** Same `valid_answers` wording existed at 4 other sites (test #3, test #6, both addenda). Strict interpretation would leave implementers exposed to the same trap when reading those other rows.
- **Learned:** When user cites a line as canonical example for a wording-class issue, default to cascade (same fix everywhere it applies) and flag in handoff for review. Cascade is small wording-only change; not scope-creep into NEW problem categories.
