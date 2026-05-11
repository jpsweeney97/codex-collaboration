---
date: 2026-04-27
time: "01:53"
created_at: "2026-04-27T05:53:18Z"
session_id: 9eabea45-1b4e-473d-9b32-b1574a9f6086
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-27_12-30_checkpoint-task-20-convergence-map-and-dispatch-packet-committed.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: c3b310cd
title: "Task 20 convergence map + dispatch packet reviewed through 3 rounds — dispatch-ready"
type: handoff
files:
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-20-convergence-map.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-20-dispatch-packet.md
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_poll_projection_guard_integration.py
---

# Handoff: Task 20 convergence map + dispatch packet reviewed through 3 rounds — dispatch-ready

## Goal

Complete the review and correction cycle for Task 20's binding convergence map and dispatch packet, bringing them from draft quality to dispatch-credible status. Task 20 adds a `try/except UnknownKindInEscalationProjection` around the `_project_pending_escalation` call in `poll()` at `delegation_controller.py:1826-1828`. On catch: signal `signal_internal_abort` (capturing the CAS return as `abort_signaled`), log critical with `abort_signaled` in extra, set `pending_escalation = None`.

**Trigger:** Task 19 (`_finalize_turn` one-snapshot terminal guard) completed in a prior session chain. Task 20 is the next Phase H task — the poll-side complement to the `start()` catch at `:788-813`.

**Stakes:** Without the `poll()` callsite guard, an `UnknownKindInEscalationProjection` from `_project_request_to_view` propagates as an unhandled exception through `poll()`, breaking the controller boundary invariant that this exception "MUST NOT escape the controller boundary" (exception class docstring at `delegation_controller.py:200-206`).

**Success criteria:** Convergence map and dispatch packet survive user scrutiny and are authoritative enough to dispatch an implementer subagent (opus, worktree isolation) that can complete the task without adjudication.

**Connection to project arc:** T-20260423-02 Packet 1 (Deferred-Approval Response), Phase H (Finalizer + Consumers + Contracts). Task 20 is 1 of 4 remaining Phase H tasks (20-22, where 21 is discard gate expansion and 22 is contracts update).

## Session Narrative

This session resumed from a checkpoint where the Task 20 convergence map (9 locks, 5 watchpoints) and dispatch packet had been drafted and committed at `d86c01cc`, pending user review. The prior session had done fresh-read orientation from HEAD `c53a5199`, identified 3 stale plan anchors, and produced both documents.

The user performed three rounds of increasingly focused scrutiny, each with a formal verdict:

**Round 1 — "Major revision":** The user identified 5 defects in the original documents. The most severe was a false claim that the spec section "§Projection helper rewrites — poll() callsite" was fictional. In reality, that section exists at `design.md:1888-1988` and contains the most precise authority for Task 20's callsite mechanics (poll callsite at `:1936-1964`). The convergence map had overcorrected from the Phase H plan's stale line numbers by declaring the entire section fictional, which would have demoted the implementer's primary authority source. Other findings: test filename lacked `_integration.py` suffix (breaking the plan-wide `-k integration` smoke gate), an impossible grep in the DONE verification template, ambiguous test setup instructions, and a live anchor citing a commit hash instead of a line number.

All 5 corrections were verified against live code before applying. The spec section was confirmed at `design.md:1888` with poll callsite requirements at `:1936-1964`. The Phase H plan at `phase-h-finalizer-consumers-contracts.md:351` names `test_poll_projection_guard_integration.py`, and the manifest's final smoke at `2026-04-24-packet-1-deferred-approval-response.md:174` uses `-k integration` to select by filename substring. The `self._registry` init was confirmed at `delegation_controller.py:392`. Committed at `2c065da0`.

**Round 2 — "Minor revision":** The user found a spec compliance gap: the production snippet discarded `signal_internal_abort`'s return value, but the spec at `:436` says "they log the return value" and at `:1978` (Branch B) says "the abort attempt's only artifact is a log line recording the `False` return from `signal_internal_abort`." This is the diagnostic evidence distinguishing abort-won (Branch A) from abort-lost (Branch B) when both produce `pending_escalation=None`. The user also found that L3 required critical logging but no test asserted it, and that L1 and L8 cited wrong spec line numbers (`:347` and `:354` instead of the helper docstring at `:1749-1756` and spec `:1892`).

Key design decision: restructured the production snippet from log-before-signal to signal-before-log. The `start()` precedent at `:788-813` logs before signaling because it raises unconditionally afterward (the log is a last-chance diagnostic). `poll()` continues after the catch, so it can afford the cleaner order: signal first (capturing `abort_signaled`), then log once with the full picture. The log message changed from "signaling" (pre-signal, potentially a lie if the guard skips the signal) to "signaled" (post-signal, always truthful). Added `caplog` assertions to Tests 1 and 2 for `abort_signaled=True` and `abort_signaled=False` respectively. Committed at `22d210da`.

**Round 3 — "Defensible":** The user found only two low-severity issues: the mission sentence still said "log critical, call signal_internal_abort" (pre-correction ordering) and the acceptance criteria table lacked a row for the critical log assertion. Both corrected. Committed at `c3b310cd`.

The user's final verdict: "Defensible. I would not block dispatch on anything substantive now."

## Decisions

### Signal-before-log ordering in poll() catch

**Choice:** `poll()` calls `signal_internal_abort()` first, captures the boolean return as `abort_signaled`, then calls `logger.critical()` with `abort_signaled` in extra.

**Driver:** Spec §436: "Callers therefore MUST NOT assume `signal_internal_abort` always takes effect; they log the return value and react accordingly." Spec §1978 (Branch B): "The abort attempt's only artifact is a log line recording the `False` return from `signal_internal_abort`." Without capturing the return value, there is no evidence in the log distinguishing whether the abort won or lost the CAS race.

**Alternatives considered:**
- **Log-before-signal (original draft, matching `start()` precedent)** — rejected because: (1) `start()` raises unconditionally after signaling, so the log is a last-chance diagnostic before the exception; `poll()` continues, so the log can and should include the signal outcome; (2) saying "signaling" in the log message is a lie if the `parked_request_id is None` guard skips the signal call; (3) the spec explicitly requires logging the return value, not just the intent.
- **Two log lines (one before, one after)** — rejected as redundant; a single post-signal log entry with `abort_signaled` in extra captures both the intent and the outcome.

**Trade-offs accepted:** Diverges from `start()` precedent at `:788-813`, which logs before signaling. Acceptable because the asymmetry is justified by the different control flow (raise vs. continue) and the spec's explicit return-value logging requirement for `poll()`.

**Confidence:** High (E2) — spec text at `:436` and `:1978` is unambiguous. Both sections independently require logging the return value. Cross-verified with the `start()` precedent to confirm the divergence is intentional, not accidental.

**Reversibility:** High — local to the catch block. Reordering log and signal or adding/removing `abort_signaled` from extra is a single-hunk change.

**Change trigger:** If spec is revised to say `poll()` should NOT log the CAS outcome, or if a future audit shows the `abort_signaled` field creates noise in log aggregation without diagnostic value.

### Test filename preserves `-k integration` smoke gate

**Choice:** New test file is `test_poll_projection_guard_integration.py` (not `test_poll_projection_guard.py`).

**Driver:** The packet-level manifest at `2026-04-24-packet-1-deferred-approval-response.md:174` defines a final integration smoke: `pytest ... -k integration`. This uses pytest's substring matching on collected test IDs, which include the filename. Without the `_integration.py` suffix, the 3 new tests would pass in full-suite runs but silently disappear from the named integration gate.

**Alternatives considered:**
- **`test_poll_projection_guard.py` (original draft)** — rejected because it breaks the acceptance chain. The tests are substantively integration tests (they exercise `controller.poll()` through the full production path with store-seeded state), so the `_integration` suffix is semantically correct, not just a naming convention.
- **Update the manifest to remove `-k integration`** — rejected because it would weaken the gate for all other integration tests.

**Trade-offs accepted:** The tests are synchronous and don't require async timing, so calling them "integration" might seem like a misnomer. But they test the controller's public API with real store state (not mocked internals), which aligns with the codebase's existing integration test pattern.

**Confidence:** High (E2) — verified by reading the manifest at `:174` and confirming pytest's `-k` substring matching behavior against filenames.

**Reversibility:** High — rename the file.

**Change trigger:** If the project abandons the `-k integration` gate convention.

### Dual spec authority sources (§Projection helper rewrites + §Internal abort coordination)

**Choice:** The convergence map and dispatch packet cite both `§Projection helper rewrites` at `design.md:1888-1988` and `§Internal abort coordination` at `design.md:347-440` as companion authorities.

**Driver:** The original draft falsely declared §Projection helper rewrites "fictional" and cited only §Internal abort coordination. User review exposed that §Projection helper rewrites is not only real but contains the most precise poll() callsite guidance (`:1936-1964`), while §Internal abort coordination covers CAS/coordination semantics (`:436`). The two sections govern different aspects of the same change.

**Alternatives considered:**
- **§Internal abort coordination only (original draft)** — rejected because it omits the poll callsite mechanics, helper purity contract (`:1892`), and Branch A/B observation sequence (`:1967-1981`).
- **§Projection helper rewrites only** — rejected because it doesn't cover CAS race semantics or worker abort sequence in sufficient detail.

**Trade-offs accepted:** The implementer must read two spec sections (~140 lines total) instead of one. Acceptable because both are genuinely authoritative for different aspects.

**Confidence:** High (E2) — verified both sections exist and contain non-overlapping authoritative content for Task 20.

**Reversibility:** N/A — this is a documentation/authority decision, not a code decision.

**Change trigger:** If the spec is restructured to merge these sections.

## Changes

### `task-20-convergence-map.md` — 3 rounds of corrections

**Purpose:** Binding convergence map for Task 20 implementer. Contains 9 locks (L1-L9), 5 watchpoints (W1-W5), stale anchor corrections, live anchors, test strategy, and acceptance criteria.

**Round 1 corrections (at `2c065da0`):**
- Stale anchor row: "Plan anchor is fictional" → "Plan anchor is valid; section exists at `:1888`, poll callsite at `:1936`. Also read §Internal abort coordination."
- `self._registry` init live anchor: "Task 16 `667ed20e`" → "`:392`" (live line reference)

**Round 2 corrections (at `22d210da`):**
- L1 rationale: "spec §347" → "helper docstring at `delegation_controller.py:1749-1756` and spec §Projection helper rewrites at `design.md:1892`"
- L3: rewritten to specify signal-before-log order with `abort_signaled` capture and spec citations (`:436`, `:1978`)
- L4: "observational only" → "MUST be logged but MUST NOT branch the response shape"
- L8 rationale: "spec §Internal abort coordination `:354`" → "helper docstring at `delegation_controller.py:1754-1756` and spec §Projection helper rewrites at `design.md:1892`"
- Test strategy table: added `caplog` assertions for `abort_signaled=True/False`

**Round 3 corrections (at `c3b310cd`):**
- Acceptance criteria: added "CRITICAL log records `abort_signaled=True/False`" row

**Key implementation detail for future-Claude:** The convergence map is the binding authority. If the dispatch packet's code snippet contradicts a lock, the lock governs.

### `task-20-dispatch-packet.md` — 3 rounds of corrections

**Purpose:** Self-contained implementer prompt for opus subagent in worktree isolation. Contains mission, authority sources, production change code, test obligations, reporting contract, and 11 boundary prohibitions.

**Round 1 corrections (at `2c065da0`):**
- Authority sources: added source 2a (§Projection helper rewrites `:1888-1988`) alongside existing 2b (§Internal abort coordination `:347-440`)
- Test filename: `test_poll_projection_guard.py` → `test_poll_projection_guard_integration.py` (all references)
- DONE verification: impossible `grep "_project_pending_escalation"` → visual diff instruction (verify no hunks inside helper defs)
- Test 1 setup: ambiguous "Create a job via `controller.start()` or direct store seeding" → explicit "direct-seed" with pattern reference to `test_handler_branches_integration.py:759-817`

**Round 2 corrections (at `22d210da`):**
- Production snippet restructured: signal-before-log, captures `abort_signaled`, log message uses "signaled" (past tense)
- Test 1 assertions: added `caplog` CRITICAL with `abort_signaled=True`
- Test 2 assertions: added `caplog` CRITICAL with `abort_signaled=False`
- Begin section: added step 2 (read both spec sections), renumbered subsequent steps

**Round 3 corrections (at `c3b310cd`):**
- Mission sentence: "log critical, call signal_internal_abort" → "call signal_internal_abort (capture return as abort_signaled), log critical with abort_signaled in extra"

**Key implementation detail for future-Claude:** The dispatch packet's production code snippet at the "Replacement" section is the exact code shape the implementer should produce. The 11 boundary prohibitions are hard constraints, not suggestions.

## Codebase Knowledge

### poll() method — the change site

| Component | Location | Purpose |
|-----------|----------|---------|
| `poll()` method def | `delegation_controller.py:1804` | `def poll(self, *, job_id: str) -> DelegationPollResult \| PollRejectedResponse:` |
| Unguarded projection call | `:1826-1828` | `pending_escalation = None` / `if refreshed.status == "needs_escalation":` / `pending_escalation = self._project_pending_escalation(refreshed)` |
| `refreshed` job fetch | `:1825` | Post-artifact-materialization re-fetch — authority for projection path (W1) |
| `detail` field assembly | `:1830-1839` | Downstream of projection — must remain downstream after catch insertion (W4) |
| `DelegationPollResult` construction | `:1841-1846` | `pending_escalation=None` is the default |

### Projection helper chain (DO NOT MODIFY — L8)

| Component | Location | Purpose |
|-----------|----------|---------|
| `_project_pending_escalation` | `:1746-1766` | Pure helper. Returns `None` for 4 legitimate guard states (terminal `:1759`, unparked `:1761`, tombstone via `get()`, non-pending). Re-raises `UnknownKindInEscalationProjection`. |
| `_project_request_to_view` | `:1720-1744` | Constructor. Raises `UnknownKindInEscalationProjection` at `:1732-1738` when `request.kind not in _ESCALATABLE_REQUEST_KINDS`. |
| `UnknownKindInEscalationProjection` | `:200-210` | Module-scope exception. Docstring: "MUST NOT escape the controller boundary." |
| `_ESCALATABLE_REQUEST_KINDS` | `:1718` | `frozenset({"command_approval", "file_change", "request_user_input"})` |

### poll() method full flow (for understanding the change site in context)

The `poll()` method at `:1804-1846` has this structure:

1. **Job lookup** (`:1805-1812`): Fetches job from store by `job_id`. Returns `PollRejectedResponse(reason="job_not_found")` if missing.
2. **Artifact materialization** (`:1814-1824`): Materializes any pending artifacts (inspection snapshots). This is an idempotent side-effect.
3. **Re-fetch** (`:1825`): `refreshed = self._job_store.get(job_id)` — the post-materialization snapshot. This is the authority for all subsequent logic. W1 requires using `refreshed`, not the pre-materialization `job`.
4. **Projection** (`:1826-1828`): **THE CHANGE SITE.** Currently unguarded: `pending_escalation = self._project_pending_escalation(refreshed)` if status is `needs_escalation`. Task 20 wraps this in try/except.
5. **Detail assembly** (`:1830-1839`): Builds `detail` string from job fields. W4 requires this stays downstream of the projection block — the try/except must NOT swallow this logic.
6. **Result construction** (`:1841-1846`): Returns `DelegationPollResult(job=refreshed, pending_escalation=pending_escalation, inspection=..., detail=detail)`.

### Exception propagation chain (the path that Task 20 guards)

```
poll() calls _project_pending_escalation(refreshed)          # :1828
  _project_pending_escalation checks 4 guard states          # :1759-1765
    if all pass → calls _project_request_to_view(request)    # :1766
      _project_request_to_view checks kind ∈ _ESCALATABLE_REQUEST_KINDS  # :1732
        if NOT in set → raises UnknownKindInEscalationProjection         # :1733-1738
          propagates through _project_pending_escalation (re-raises)      # docstring :1752
            WITHOUT Task 20: escapes poll() as unhandled exception
            WITH Task 20: caught at poll() callsite → signal + log + null escalation
```

The 4 guard states in `_project_pending_escalation` that return `None` WITHOUT raising (L2 — these are legitimate, not abort triggers):
- Terminal status (`completed`, `failed`, `canceled`, `unknown`) at `:1759`
- `parked_request_id is None` at `:1761`
- Request not found in store (tombstone) at `:1763-1764`
- Request status is not `"pending"` at `:1764`

### start() catch precedent (pattern reference)

The `start()` catch at `:788-813` is the existing callsite catch. Key structural differences from the `poll()` catch:

| Aspect | `start()` catch (`:788-813`) | `poll()` catch (Task 20) |
|--------|------------------------------|--------------------------|
| Log timing | Before signal (last-chance before raise) | After signal (captures CAS outcome) |
| CAS return | Discarded | Captured as `abort_signaled`, logged |
| Post-catch | Raises `DelegationStartError` | Returns `DelegationPollResult(pending_escalation=None)` |
| Reason string | `"parked_projection_invariant_violation"` | `"unknown_kind_in_escalation_projection"` |
| Log message | `"delegation.start: unknown-kind in parked projection"` | `"delegation.poll: unknown-kind in escalation projection; signaled worker-coordinated internal abort"` |
| Defense-in-depth guard | Not needed (request_id always non-None in start) | `if refreshed.parked_request_id is not None:` (W5 — structurally redundant but acceptable) |

### signal_internal_abort

Located at `resolution_registry.py:311-327`. CAS: `awaiting → aborted`. Wakes worker with `InternalAbort`. Returns `True` if transition took effect, `False` if entry was already in another state (operator `decide()` won the race). Idempotent no-op for non-`awaiting` entries.

The two CAS branches (spec `:1967-1981`):
- **Branch A — abort wins** (`True`): Worker wakes on `InternalAbort`, executes abort sequence, terminalizes job as `unknown`. Subsequent polls see `status="unknown"`.
- **Branch B — decide wins** (`False`): Operator's reservation already committed. Worker wakes on operator's `DecisionResolution`, completes dispatch normally. The abort attempt's only artifact is the log line with `abort_signaled=False`.

Both branches produce `pending_escalation=None` in the immediate poll result. The diagnostic distinction is ONLY in the log record.

### self._registry availability

`self._registry: ResolutionRegistry = ResolutionRegistry()` initialized at `delegation_controller.py:392` in `__init__`. Available to all controller methods. The registry is controller-scoped (one per `DelegationController` instance), not global.

### Test infrastructure

| Component | Location | Purpose |
|-----------|----------|---------|
| `_build_controller` | `test_delegation_controller.py:206` | Returns 8-tuple. Cross-imported by sibling test files. |
| `_FakeSession` | `test_delegation_controller.py` | Imported at `test_handler_branches_integration.py:44-47`. Established cross-import pattern. |
| Worker-side abort test | `test_handler_branches_integration.py:759-817` | Supporting coverage for `InternalAbort(reason="unknown_kind_in_escalation_projection")`. DO NOT modify (L7). |
| Normal-kind poll regression | `test_delegation_controller.py:2665-2681` | `test_poll_needs_escalation_projects_pending_request_without_raw_ids`. Must not regress (L5). |
| Direct-seeding pattern | `test_handler_branches_integration.py:759-817` | Uses `_make_running_job_with_lineage` + `job_store.update_status` + `pending_request_store.create`. Reference for unknown-kind test setup. |

### Spec authority sources for Task 20

| Source | Location | Governs |
|--------|----------|---------|
| §Projection helper rewrites | `design.md:1888-1988` | Poll callsite mechanics (`:1936-1964`), helper purity (`:1892`), Branch A/B observation sequence (`:1967-1981`) |
| §Internal abort coordination | `design.md:347-440` | CAS race semantics (`:436`), worker abort sequence (`:395-422`), poll triggers (`:352`) |

### Suite baseline

1040 passed / 0 skipped / 0 failed (from Task 19 — no Task 20 production changes yet). Task 20 should add 3 new tests → expected 1043+.

## Conversation Highlights

**Round 1 — false authority demotion caught:**
User's scrutiny verdict: "Major revision." The user identified that the convergence map falsely declared §Projection helper rewrites "fictional" — "That is wrong. The spec has exactly that section at `design.md:1888`." This was the highest-severity finding because it would have demoted the implementer's most precise authority source.

**Round 1 — acceptance chain caught:**
User: "The Phase H plan and manifest name `test_poll_projection_guard_integration.py`, and the final integration smoke explicitly expects that file under `-k integration`." Exposed a substrate-level acceptance chain where full-suite passes but the named gate silently drops the new tests.

**Round 2 — CAS-return observability:**
User: "The spec goes further: callers 'log the return value' when discussing CAS failure semantics, and Branch B says the abort attempt's only artifact is a log line recording the `False` return." This drove the signal-before-log restructuring and the `abort_signaled` capture.

**Round 2 — citation hygiene after false demotion:**
User: "After the previous false-demotion bug, citation hygiene matters. These do not misstate the lock, but they weaken trust in the map as a precise authority artifact." Set the standard that citations must point to the actual source, not a nearby section header.

**Round 3 — clean pass with one wording fix:**
User: "Defensible. I would not block dispatch on anything substantive now. The only required cleanup is a one-line wording fix so the mission summary matches the corrected signal-before-log implementation contract."

**User instruction on next step:**
User: "Proceed with that cleanup, and then save a handoff."

**Adversarial review methodology:**
The user's scrutiny applies named adversarial perspectives explicitly:
- **Spec-authority adversary:** checks that every spec citation is accurate and that no valid authority is demoted or falsely declared fictional.
- **CI/acceptance adversary:** checks that test filenames, gate commands, and smoke filters actually select the intended tests.
- **Implementer-following-literally adversary:** checks that an implementer following the dispatch packet word-for-word would produce correct code (catches impossible grep commands, ambiguous setup instructions, stale ordering in mission statements).
- **Concurrency adversary:** checks that CAS-race semantics are correctly handled (return value logged but not branched on).

Each round's "Required Changes Before This Is Credible" section lists findings by severity (Critical/High/Medium/Low) with specific line references and required changes. This is not a pass/fail gate — it's a graduated credibility assessment with a named verdict scale: "Major revision" → "Minor revision" → "Defensible" → (presumably) "Clean pass".

**Review escalation pattern observed:**
Round 1 found 5 issues across authority-chain, acceptance-chain, and proof-chain categories. Round 2 found 4 issues, all narrower (observability semantics, citation hygiene). Round 3 found 2 issues, both low-severity wording. The pattern is convergent: each round's findings are at a finer grain than the previous round, and the severity ceiling drops. This suggests the review methodology is exhaustive at each level before proceeding to the next.

**Working style note:**
The user does not perform incremental reviews during drafting. They wait for a committed artifact, then scrutinize it holistically. The user explicitly said "I am going to review both of those documents and share my feedback with you" before the first round — setting the expectation that review happens on a complete artifact, not on work-in-progress.

## Context

### Mental model

Task 20 is an **assertion-boundary completion** problem. The `UnknownKindInEscalationProjection` exception was designed to never escape the controller boundary (docstring at `:200-206`). Task 17 already caught it in `start()` at `:788-813`. Task 20 catches it in the remaining unguarded callsite: `poll()`. The exception class, the helper chain, and the CAS-based cleanup primitive (`signal_internal_abort`) are all already built and tested. Task 20 is wiring — connecting the existing catch/signal/log pattern to the last callsite.

The key insight from this session: the `poll()` catch is NOT a clone of the `start()` catch. The differences are:
1. **Response shape:** `start()` raises `DelegationStartError`; `poll()` returns `DelegationPollResult(pending_escalation=None)` (poll is observational, not transactional).
2. **Signal order:** `start()` logs before signaling (last-chance diagnostic before raise); `poll()` signals before logging (captures CAS outcome for the log).
3. **Return value:** `start()` discards `signal_internal_abort`'s return; `poll()` captures it as `abort_signaled` and logs it (spec §436 requires this).
4. **Reason string:** `start()` uses `"parked_projection_invariant_violation"`; `poll()` uses `"unknown_kind_in_escalation_projection"`.

### Phase H task map

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| 19 | `_finalize_turn` one-snapshot terminal guard | **Complete** (5-commit chain ending `c53a5199`) | None |
| 20 | `poll()` `UnknownKindInEscalationProjection` catch + `signal_internal_abort` | **Dispatch-ready** (convergence map + dispatch packet reviewed) | None — independent of Task 19 changes |
| 21 | `discard()` gate expansion for `"canceled"` status | Not started | Independent of Task 20 (L9) |
| 22 | `contracts.md` 5-section update | Not started | Independent of Task 20 (L9) |

Tasks 20, 21, and 22 are explicitly independent per L9: "`discard()` at `:2290` and `contracts.md` are independent of `poll()`'s projection path." Task 21 modifies `discard()` at `:2290-2338` (specifically the `_discardable` gate at `:2305-2306`). Task 22 modifies `contracts.md` (6 literals → 7 for status, kind narrowing, decide result shape update, active_delegation.status, discard admissibility).

### Dispatch process (subagent-driven development)

The established process for Tasks 15-19 (and now 20):
1. **Fresh-read orientation** from live HEAD — verify plan anchors, identify stale references.
2. **Draft convergence map** — locks (hard constraints), watchpoints (verification checks), live anchors, test strategy, acceptance criteria.
3. **Draft dispatch packet** — self-contained implementer prompt with authority sources, exact code shape, test obligations, reporting contract (DONE/BLOCKED templates), boundary prohibitions.
4. **User review** — graduated scrutiny with adversarial perspectives. Iterate until "Defensible" or better.
5. **Dispatch implementer** — opus subagent in worktree isolation, using the dispatch packet as the prompt.
6. **Review chain** — spec reviewer + code-quality reviewer sequentially (per `subagent-driven-development` feedback memory).
7. **Closeout** — fix any review findings directly (per `closeout-work-directly` feedback memory), commit, verify suite.

This session completed steps 1-4 (steps 1-3 were done in the prior session chain; step 4 was this session). Next session begins at step 5.

### Project state

Branch `feature/delegate-deferred-approval-response` is 8 commits ahead of `main` (Tasks 15-19 + Task 20 docs). No production code changes for Task 20 yet — all changes this session are to the convergence map and dispatch packet documents.

### Commit chain this session

| SHA | Type | Content |
|-----|------|---------|
| `d86c01cc` | docs | Task 20 convergence map + dispatch packet (pre-session, inherited) |
| `2c065da0` | fix | Round 1: 5 corrections (false demotion, filename, grep, seeding, live anchor) |
| `22d210da` | fix | Round 2: CAS-return logging, caplog assertions, citation fixes |
| `c3b310cd` | fix | Round 3: mission ordering, acceptance criteria row |

## Learnings

### Overcorrection from stale anchors is a real hazard in convergence maps

**Mechanism:** When a convergence map corrects stale plan references, the correction can go too far — declaring a valid anchor "fictional" when only the line numbers shifted. This functionally demotes an authority source for every downstream consumer (the implementer reads the map as binding truth).

**Evidence:** The Phase H plan referenced "§Projection helper rewrites — poll() callsite (spec lines ~1936-1964)". The convergence map declared it fictional. In reality, the section exists at `design.md:1888` with poll callsite requirements at `:1936`. The line numbers in the plan were approximately correct; only the section header location had shifted.

**Implication:** When correcting stale references, distinguish between "anchor name is wrong" and "anchor exists but line numbers shifted." Verify by searching for the section title, not just the line range.

**Watch for:** Any future convergence map that says "fictional" or "does not exist" about a plan or spec anchor. Verify the claim before accepting it.

### Acceptance chains can be substrate-level and invisible

**Mechanism:** The `-k integration` smoke gate uses pytest's substring matching on collected test IDs (which include filenames). A file without `_integration` in its name is silently excluded from the gate, even if the full suite passes.

**Evidence:** The dispatch packet named `test_poll_projection_guard.py`. The manifest at `2026-04-24-packet-1-deferred-approval-response.md:174` runs `-k integration`. The tests would pass in full-suite runs but disappear from the acceptance gate.

**Implication:** Test filenames are not just organizational — they carry acceptance-chain semantics. Future convergence maps should verify test filenames against all named gates, not just assume they'll be collected.

### Signal-before-log vs log-before-signal depends on control flow after the catch

**Mechanism:** If the catch block raises (like `start()`), logging before the signal is a last-chance diagnostic. If the catch block continues (like `poll()`), logging after the signal can include the signal's outcome. The spec at `:436` requires logging the CAS return value for poll().

**Evidence:** `start()` at `:788-813` logs before signaling because it raises `DelegationStartError` unconditionally. `poll()` continues to construct `DelegationPollResult`, so it can signal first, capture the boolean, and log once with the full picture.

**Implication:** Don't blindly clone catch patterns across callsites. Each callsite's post-catch control flow determines the optimal log/signal ordering.

## Next Steps

### 1. Dispatch Task 20 implementer (opus, worktree isolation)

**Dependencies:** None — convergence map and dispatch packet are dispatch-credible at `c3b310cd`.

**What to do:** Dispatch an opus subagent in worktree isolation using the dispatch packet at `task-20-dispatch-packet.md` as the implementer prompt. The packet is self-contained: it includes authority sources, exact production code, test obligations, DONE/BLOCKED reporting templates, and 11 boundary prohibitions.

**Expected outcome:** ~15 lines of production code change at `delegation_controller.py:1826-1828`, 3 new tests in `test_poll_projection_guard_integration.py`, suite count ≥ 1043.

**Potential obstacles:** The direct-seeding approach for unknown-kind test setup requires consulting `test_handler_branches_integration.py:759-817` for the pattern. If the implementer can't find `_make_running_job_with_lineage` or if the store-seeding API has shifted, it should report BLOCKED.

### 2. After implementer DONE: run review chain

**Dependencies:** Implementer DONE report.

**What to do:** Per the subagent-driven-development feedback memory: dispatch implementer + spec reviewer + code-quality reviewer sequentially. Do NOT stop at implementer DONE.

### 3. After Task 20 lands: Tasks 21 and 22

**Dependencies:** Task 20 merged to branch.

**What to do:** Task 21 is discard gate expansion for "canceled" status. Task 22 is contracts.md 5-section update. Both are independent of Task 20's production changes (L9 confirms no coupling).

### 4. Carry-forward open items (end of Packet 1)

| Item | Description | When |
|------|-------------|------|
| TT.1 | `_FakeControlPlane` Pyright issues at `test_delegation_controller.py:257, 2547, 2621, 2686, 2867, 2888, 3064, 3194, 3418` | End-of-Packet-1 typing polish |
| RT.1 | `runtime.py:270` Pyright TurnStatus literal narrowing | End-of-Packet-1 typing polish |

## In Progress

**In Progress:** Task 20 convergence map and dispatch packet are reviewed and dispatch-credible.

- **Approach:** Subagent-driven development: dispatch opus implementer in worktree isolation → sequential spec/quality reviews → closeout.
- **State:** Dispatch-ready. No production code changes yet. All 3 rounds of review corrections committed.
- **Working:** Convergence map (9 locks, 5 watchpoints, acceptance criteria) and dispatch packet (authority sources, exact code, 3 test obligations, 11 prohibitions) at `c3b310cd`.
- **Not working:** Nothing broken — this is a clean stopping point before dispatch.
- **Open question:** None blocking dispatch.
- **Next action:** Dispatch the implementer using the dispatch packet as the prompt.

## Open Questions

No open questions blocking dispatch. The 3 review rounds resolved all identified defects.

The user's final verdict: "Defensible. I would not block dispatch on anything substantive now."

## Risks

### Implementer direct-seeding complexity

The unknown-kind test requires direct store seeding because `controller.start()` won't produce a `needs_escalation` job with `kind="unknown"` parked request under Task 17's L11 carve-out. The dispatch packet provides a pattern reference (`test_handler_branches_integration.py:759-817`) but the implementer must adapt it. If the store API has shifted since that test was written, the implementer should BLOCKED rather than improvise.

### caplog assertion fragility

The `caplog` assertions for `abort_signaled=True/False` depend on the exact `logger.critical()` call structure. If the implementer changes the log message or extra fields, the assertions break. The dispatch packet's production snippet is the authority for both the log call and the test assertions — they must be consistent.

## References

| Resource | Location | Purpose |
|----------|----------|---------|
| Task 20 convergence map (binding) | `docs/plans/.../task-20-convergence-map.md` | 9 locks, 5 watchpoints, acceptance criteria |
| Task 20 dispatch packet | `docs/plans/.../task-20-dispatch-packet.md` | Self-contained implementer prompt |
| Spec §Projection helper rewrites | `design.md:1888-1988` | Poll callsite mechanics, helper purity, Branch A/B |
| Spec §Internal abort coordination | `design.md:347-440` | CAS race, worker abort, poll triggers |
| Phase H plan | `phase-h-finalizer-consumers-contracts.md` | Tasks 19-22 plan body |
| Packet-level manifest | `2026-04-24-packet-1-deferred-approval-response.md` | Final integration smoke at `:174` |
| Carry-forward register | `carry-forward.md` | TT.1, RT.1 open items |

## Gotchas

### pytest `-k integration` is filename-sensitive

The plan-wide final smoke at `2026-04-24-packet-1-deferred-approval-response.md:174` uses `pytest ... -k integration`. This does substring matching on the collected test ID, which includes the filename. A test file without `_integration` in its name is silently excluded. This was caught during Round 1 review — the original dispatch packet named `test_poll_projection_guard.py`, which would have passed full-suite but disappeared from the gate.

### signal_internal_abort return value is diagnostic, not decisional

The `poll()` catch must capture `abort_signaled = self._registry.signal_internal_abort(...)` and include it in `logger.critical` extra. But `abort_signaled` MUST NOT branch the response shape — `pending_escalation = None` regardless. The spec at `:436` makes this a MUST-level requirement. The `start()` precedent discards the return value entirely, which is justified there (unconditional raise), but NOT justified for `poll()` (continues to return, needs the diagnostic trail).

### Convergence map is binding, dispatch packet is implementation guidance

If the dispatch packet's code snippet contradicts a lock in the convergence map, the lock governs. The implementer should report BLOCKED if a contradiction is found, not silently follow the snippet.

## User Preferences

**Review methodology:** The user performs formal scrutiny with structured verdicts ("Major revision", "Minor revision", "Defensible"). Each round has: Premise Check, Critical Failures, High-Risk Assumptions (with severity and required changes), Real-World Breakpoints, Hidden Dependencies, Adversarial Perspectives Applied, Patterns And Root Causes, Required Changes, and Verdict.

**Citation standard:** After the Round 1 false-demotion incident, the user elevated citation hygiene to a review criterion. User: "After the previous false-demotion bug, citation hygiene matters. These do not misstate the lock, but they weaken trust in the map as a precise authority artifact."

**Authority-chain integrity:** The user treats authority demotion (declaring a valid source fictional or irrelevant) as a high-severity defect, even if the lock's substantive content is correct. The authority chain itself must be accurate.

**Dispatch credibility bar:** The user will not authorize implementer dispatch until the convergence map and dispatch packet survive scrutiny without high-severity findings. "Defensible" is the minimum dispatch-credible verdict.
