---
date: 2026-04-25
time: "13:19"
created_at: "2026-04-25T17:19:00Z"
session_id: dfaa1fd6-020d-4795-8537-69a00984b0f6
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-25_12-40_phase-e-task-14-complete-phase-f-next.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: d8f1911b
title: Phase F Task 15 convergence map saved — fresh-session dispatch next
type: handoff
files:
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md
---

# Handoff: Phase F Task 15 convergence map saved — fresh-session dispatch next

## Goal

Execute a read-only Phase F Task 15 orientation pass and produce a binding convergence map for the upcoming implementer dispatch. Do NOT dispatch the implementer this session — defer to a fresh session because the orientation pass plus two-stage review would overrun the available context.

**Trigger:** Resumed from prior handoff `2026-04-25_12-40_phase-e-task-14-complete-phase-f-next.md` at commit `d8f1911b` on branch `feature/delegate-deferred-approval-response`. Prior handoff named Phase F Task 15 as the next work item with the user's standing cadence preference: orientation pass + convergence map first, then dispatch in a fresh session.

**Stakes:** Task 15 is Phase F's first task and opens the worker-thread model. The convergence map drafted here is **binding** for the upcoming dispatch — locks/watchpoints become the implementer's positive/negative scope contracts. Mistakes captured during orientation (line-number drift, plan-fixture-name traps, sentinel-table-vs-plan-header discrepancy, lint-hygiene adjustments to plan templates) save dispatch-iteration cycles. Phase F is the largest phase per the plan structure; Tasks 15 → 16 → 17 form the tightest coupling cluster.

**Success criteria (achieved):**
- Convergence map drafted with L1-L8 + W1-W11 + per-test triage table + out-of-scope + acceptance + pre-dispatch checklist
- Saved to working doc at `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md`
- Three required edits applied per user feedback (lint-hygiene, structural-not-line-numbered acceptance, ruff command instead of "ruff + pyright clean")
- Carry-forward A1 confirmed closed by L4
- Dispatch deferred to fresh session per user's context-management directive

**Connection to project arc:** T-20260423-02 Packet 1 progress is now Phase E complete (Tasks 13 + 14) → Phase F next (Tasks 15 + 16) → Phase G (Tasks 17 + 18) → Phase H (Tasks 19+). Phase F = worker-side machinery (worker_runner skeleton, handler rewrite with 6 sentinel raise sites, `update_parked_request` wiring, `completion_origin="worker_completed"` writes). Task 15 specifically is the **scaffold** — purely additive (new file + new catch + tuple expansion); the catch is structurally dead code under Task 15 scope until Task 16 lands the raise sites and Task 17 spawns the worker thread.

## Session Narrative

Started by `/handoff:load` at the beginning of the session (state file written at `docs/handoffs/.session-state/handoff-dfaa1fd6-...`). Prior handoff resumed cleanly with full Phase E Task 14 closeout context.

**Stage 1 — Task list setup + initial reads.** Created 8 todos covering: (a) read phase-f-worker.md, (b) read carry-forward.md, (c) read controller surface, (d) read resolution_registry.py, (e) read delegation_job_store.update_parked_request, (f) read design spec worker section, (g) audit caller graph for any Phase F-touching helper, (h) draft convergence map.

Sized files first via `wc -l`: phase-f-worker.md (1189 lines), phase-g-public-api.md (543), phase-h-finalizer-consumers-contracts.md (718), carry-forward.md (152), design spec (2440), delegation_controller.py (2256), resolution_registry.py (416). The plan and design files are large; I read them in chunks rather than monolithic.

**Stage 2 — Read pass.** Read phase-f-worker.md lines 1-400 (Task 15 body) + 400-800 (Task 16 step 16.1-16.3) + 800-1189 (Task 16 step 16.4-16.7 + closure). Read full carry-forward.md (152 lines). Read controller `_execute_live_turn` body at `:741-872` + `_load_or_materialize_inspection` at `:1012-1041`. Read `_WorkerTerminalBranchSignal` definition at `:201-223` + `DelegationStartError` definition at `:153-185`.

Critical discoveries from this pass:
- **Plan-line drift confirmed**: `_load_or_materialize_inspection` is at `:1012` (plan says `:873`); `_execute_live_turn` is at `:741` (plan says `:730`); `_server_request_handler` body is at `:765` (plan says `:650-720`).
- **Spec sentinel table** at `design.md:474-484` lists 6 reasons that DO NOT match the plan header's loose wording at `phase-f-worker.md:5`. Plan header says "park, completion, unknown, timeout-interrupt-succeeded, internal-abort, worker-failure" — but `Parked` is a `ParkedCaptureResult` variant signaled via `announce_parked`, not a sentinel reason; "worker-failure" is the OUTER `except Exception` path (`WorkerFailed` capture outcome), not a sentinel reason. Spec table is authority.
- **`_execute_live_turn` body has TWO try/except Exception blocks**: around `run_execution_turn` (`:837-852`) and around `_finalize_turn` (`:854-872`). Task 15 modifies only the first; the second stays untouched.

**Stage 3 — User-paste independent read.** User pasted their own /copy-output Task 15/16 read at message 3, mid-stage-2. Same workflow as Tasks 13 + 14 (independent read first, share findings, refine, then dispatch). User's read was structurally complementary to mine:
- User's read hit higher-level structural traps: `registry.register(..., kind=...)` requires `EscalatableRequestKind` (Task 16 trap); spec table > plan header text; phase boundaries strict.
- My read hit lower-level mechanical traps: line-number drift; dead-code aspects of Task 15's catch; lint-hygiene issues in plan template (unused `Callable`, dead `result =`).

User's recommended dispatch posture: "Dispatch Task 15 first, but with two explicit corrections in the dispatch packet: (1) Use local test helper patterns from `test_delegation_controller.py`; do not use nonexistent fixture names from the plan examples. (2) Treat `ResolutionRegistry.register(..., kind=...)` as a required live-code adjustment, not optional pseudocode cleanup."

**Stage 4 — Convergence map drafting (round 1).** Verified spec sentinel table (`design.md:474-484`), registry.register signature (`resolution_registry.py:173-180`), conftest.py contents (only schema fixtures + `make_test_handle` helper — NO `delegation_controller`/`simple_job_factory`/`artifact_store_spy`/`worker_runner_fixture`). Confirmed Pre-Execution Notes' affected-task list (`docs/plans/2026-04-24-packet-1-deferred-approval-response.md:104-111`) does NOT include Task 15 even though the Task 15 plan template DOES include placeholder tests with fictional fixtures.

Shared findings + alignment table + 8 extensions (E1-E8). E1 was the placeholder-test disposition; my lean was (a) "omit entirely — only the 2 concrete tests are sufficient." E2 noted the canceled-inspection tests are contract guards, not red/green. E3+E7 noted the dead-code aspects of Task 15's catch + worker-runner skeleton. E5 noted A1 logging is required at the catch site (plan omits it).

**Stage 5 — User refinement.** User confirmed with refinements:
- E1 tightened: omit fictional-fixture placeholder tests, BUT add at least one concrete sentinel-catch test using local fakes/monkeypatching, because Task 15 actually changes `_execute_live_turn` behavior. "Do not leave the sentinel catch entirely untested if Task 15 lands that catch."
- A1 logging at `logger.info` (NOT warning/error — "post-branch sentinel handling is expected control flow; warning/error would be too noisy because post-branch sentinel handling is expected control flow").
- Commit shape: 1 `feat` only; closeout-docs commit only if review surfaces real updates. "Task 15 is thin enough that a closeout-docs commit would be ceremony unless something changes."
- Workflow: single fresh implementer + spec review + code-quality review (sequential, NOT parallel). One implementer per task.
- Task 16 fresh session boundary.

User then provided a recommended convergence-map shape: L1-L8 + W1-W8 + test triage rows. I adopted the structure verbatim and integrated my E2/E5 specifics.

**Stage 6 — Convergence map drafting (round 2).** Drafted the full map with: live anchors table (verified line numbers), L1-L8 locks, W1-W8 watchpoints + W9-W11 (additional traps I identified — `cast`/`EscalatableRequestKind` already imported, `_WorkerTerminalBranchSignal`'s empty `args`, plan-placeholder-fictional-fixtures), per-test triage table (5 net new tests + 5 omitted/subsumed), out-of-scope table with plan-line citations, acceptance criteria, pre-dispatch checklist, commit shape, carry-forward expectations (A1 closed by L4).

**Stage 7 — User refinement (round 2).** User confirmed with three required edits:
1. **Do not say worker_runner.py skeleton matches Step 15.3 verbatim.** Plan skeleton has at least two likely lint issues: unused `Callable` import + unused `result =` binding. Change to "follows the Step 15.3 behavior, with lint-clean adjustments."
2. **Avoid fixed post-edit line numbers in acceptance.** "Inserted at `:845`" works as orientation anchor but shifts after edit. Acceptance should describe structural location: "inserted in the first `run_execution_turn` try block, before the generic `except Exception`."
3. **Ruff command exact, no pyright in acceptance** (since dispatch doesn't provide a type-check command). Replace "passes ruff + pyright clean" with concrete `ruff check` command and "no lint/type regressions in modified files."

Bonus: `caplog` added to per-test triage as an allowed real pytest fixture; substring assertions on `signal.reason` (e.g., `"dispatch_failed"` substring), not exact message equality.

User also gave the context-management directive: "Given 94% context, I would not dispatch the implementer from this session. Task 15 is small, but the proper workflow is implementer + spec review + quality review, and that can easily overrun the remaining context. Best next move: save this convergence map into a working doc or handoff, then dispatch Task 15 fresh."

**Stage 8 — Apply edits + write working doc.** Applied the three edits to L2 + acceptance criterion 1 + acceptance criterion 2 + per-test triage. Wrote the full convergence map to `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md` (working doc, not handoff body). Closed all 8 todos.

**Set aside for later:** Phase F Task 15 implementer dispatch deferred to fresh session per the user's context-management directive. Three E13.x carry-forward items still deferred (E13.1 to end-of-Packet-1; E13.2-E13.3 to Phase H). E14.1 deferred to end-of-Packet-1.

## Decisions

### D1: Defer Task 15 implementer dispatch to fresh session

**Choice:** Save the convergence map to a working doc + create a handoff. Do NOT spawn implementer in this session.

**Driver:** User explicit directive at message 5 (round 2 refinements): "Given 94% context, I would not dispatch the implementer from this session. Task 15 is small, but the proper workflow is implementer + spec review + quality review, and that can easily overrun the remaining context. Best next move: save this convergence map into a working doc or handoff, then dispatch Task 15 fresh."

**Alternatives considered:**
- **Dispatch in this session.** Rejected — context was at 98% when user confirmed; two-stage review (implementer + spec reviewer + code-quality reviewer) plus closeout cycles would overrun. Note: context budget reset to 1M after the directive was given (system showed 21% of 1M post-save), but the directive was correct at the time it was made.
- **Carry the convergence map in the handoff body.** Rejected — handoff would be massively long and the working doc is a more durable, citable artifact for the fresh-session dispatch.

**Implications:** Fresh session loads handoff via `/handoff:load`, then reads `task-15-convergence-map.md` directly into the dispatch packet. Implementer + reviewers fire from the fresh session with a clean context. Slight overhead of session-warm-up but preserved context safety.

**Trade-offs accepted:** Slight DRY-violation (handoff Next Steps refers to working doc; working doc embeds the binding scope contracts). Mitigated by: handoff is the entry point; working doc is the binding artifact.

**Confidence:** High (E2) — user explicitly directed this; convergence map structure validated end-to-end via two refinement rounds.

**Reversibility:** N/A — context safety is the priority.

**Change trigger:** None.

### D2: Concrete sentinel-catch tests using local fakes (E1 tightening per user)

**Choice:** Per-test triage includes 2 sentinel-catch tests using `monkeypatch` + `caplog` (built-in pytest fixtures), in addition to the smoke test + 2 contract guards.

**Driver:** User correction to my E1: "do not leave the sentinel catch entirely untested if Task 15 lands that catch." Pure scaffold-only with no sentinel-catch test would mean Task 15 ships an unverified behavior change.

**Alternatives considered:**
- **Only contract guards + smoke (3 tests).** My original E1 lean. Rejected per user direction — would leave the sentinel catch unverified.
- **End-to-end worker harness tests.** Rejected — Task 16/17 territory; plan placeholders use fictional fixtures.
- **Skip the sentinel catch tests with substantive Task 17 unblock citations.** Rejected — Task 15 IS the catch's landing point, so deferring tests defeats the test-with-feature principle.

**Implications:** 5 net new tests for Task 15 (or 6 if combining cleanup-counter assertion). Tests use `monkeypatch.setattr(entry.session, "run_execution_turn", ...)` to inject sentinel raises; `caplog` to assert `signal.reason` substring presence in log output.

**Trade-offs accepted:** Slightly larger test surface; preserves coverage of actual Task 15 behavior change.

**Confidence:** High (E2).

**Reversibility:** High.

**Change trigger:** N/A — triage table is binding for dispatch.

### D3: Convergence-map structure follows user's recommended L1-L8 + W1-W8 shape (extended with W9-W11)

**Choice:** Adopt user's L1-L8 + W1-W8 verbatim. Extend with W9 (`cast`/`EscalatableRequestKind` already imported), W10 (`_WorkerTerminalBranchSignal` empty `args`), W11 (plan placeholder fictional-fixtures).

**Driver:** User provided detailed lock/watchpoint shape that already integrated my findings. Re-deriving would waste session time; user's structure matches Task 13/14 dispatch packet shape.

**Alternatives considered:**
- **Re-derive from scratch.** Rejected — wasteful given user's structure was already calibrated to my E1-E8.
- **Compress to fewer locks.** Rejected — loses specificity; Task 13/14 used 7 locks each, Task 15 uses 8 of similar size.

**Implications:** Map is binding for dispatch. Implementer reads it as scaffold; reviewers map locks/watchpoints during their passes.

**Trade-offs accepted:** Slight verbosity; matches Task 13/14 dispatch packet shape (which produced clean implementations).

**Confidence:** High (E3).

### D4: A1 sentinel logging at `logger.info` severity

**Choice:** `logger.info("worker terminal-branch signal caught. job_id=%r reason=%s", job_id, signal.reason)` placed at the top of the new `except _WorkerTerminalBranchSignal as signal:` clause.

**Driver:** User direct guidance: "I'd prefer `logger.info` or `logger.debug` for normal post-branch sentinel consumption, but warning/error would be too noisy because post-branch sentinel handling is expected control flow."

**Alternatives considered:**
- **`logger.warning`.** Rejected — too noisy; sentinel catch is expected control flow under Task 16+.
- **`logger.error`.** Rejected — same reason; sentinel handling is not an error.
- **`logger.debug`.** Acceptable but less observable. `logger.info` matches "expected event of operational interest" semantic.
- **No logging.** Rejected — A1 carry-forward explicitly requires `signal.reason` logging.

**Implications:** Carry-forward A1 closes at Task 15. Future readers see post-branch sentinel transitions in info-level streams.

**Trade-offs accepted:** info level may be filtered by some log levels; expected control flow shouldn't pollute warning streams.

**Confidence:** High (E2).

### D5: Save convergence map to working doc instead of carrying in handoff body

**Choice:** Write `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md` as a durable artifact. Reference it from handoff Next Steps.

**Driver:** Persistence — fresh session can read directly without re-deriving. Carrying the full convergence map in the handoff body would be token-heavy and DRY-violating (handoff is ephemeral; working doc is binding).

**Alternatives considered:**
- **Carry full text in handoff.** Rejected — token-heavy; handoff body's purpose is session synthesis, not specification capture.
- **Rely on chat history.** Rejected — chat history is lost on session boundary.
- **Append to phase-f-worker.md.** Rejected — would mix authoritative plan with task-specific convergence map; cleaner to keep them separate.

**Implications:** Working doc is the binding artifact for dispatch. Handoff Next Steps is the entry point.

**Trade-offs accepted:** Slight DRY-violation (carry-forward expectations table appears in both); mitigated by working doc having more detail.

**Confidence:** High (E2).

## Changes

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md` (new)

**Purpose:** Binding convergence map for Phase F Task 15 implementer dispatch. Acts as the dispatch packet's primary scope contract.

**Approach:**
- Live anchors table (verified line numbers): 14 rows covering all symbols Task 15 references
- Locks L1-L8: scaffold-only scope, worker_runner shape with lint-clean adjustments, sentinel catch placement (BEFORE generic except Exception), A1 logging via `logger.info`, pre-capture maps to `DelegationStartError`, post-branch returns stored job, `_load_or_materialize_inspection` tuple+early-return, module-local helper test pattern
- Watchpoints W1-W11: no raise sites (Task 16); no `_registry` attr; no `spawn_worker` wiring; no `update_parked_request`; no `_finalize_turn` edits; canceled-inspection-tests-are-contract-guards (W6); use live line numbers (W7); sentinel raise count remains 0 (W8); imports already exist (W9); empty `args` trap (W10); fictional-fixture omission (W11)
- Per-test triage (10 rows): 5 written + 5 omitted/subsumed
- Out-of-scope table: 11 items with plan-line citations
- Acceptance criteria (8 checkboxes, structural-not-line-numbered)
- Pre-dispatch checklist
- Commit shape (1 feat only)
- Carry-forward expectations table (A1 closed at L4; A2 + C10.4 + Mode B → Task 16; Mode A → Task 17)

**Key locations within the file:**
- "Live anchors" table near top — orientation
- "Locks" section — positive scope
- "Watchpoints" section — negative scope
- "Per-test triage table" — binding test surface
- "Acceptance criteria" — exit gate

**Future-Claude:** This file is the binding dispatch packet for Task 15 only. Task 16 will need its own convergence map (likely 2-3x larger per user's recommended posture); save it as `task-16-convergence-map.md` in the same directory. The file pattern is intentional — convergence maps live alongside the plan files for the same packet.

## Codebase Knowledge

### Task 15 modification surface (live anchors verified 2026-04-25)

| Symbol | File:line | What changes in Task 15 |
|--------|-----------|-------------------------|
| `_WorkerTerminalBranchSignal` | `delegation_controller.py:201-223` | No change (defined Phase A) |
| `DelegationStartError` | `delegation_controller.py:153-185` | No change (defined Phase A) |
| `_execute_live_turn` first try/except | `:837-852` | **Insert `except _WorkerTerminalBranchSignal as signal:` before existing `except Exception:`** |
| `_execute_live_turn` second try/except | `:854-872` | **No change — leave untouched** |
| `_load_or_materialize_inspection` guard | `:1015` | **Add `"canceled"` to tuple + add `if job.status == "canceled": return None` before `load_snapshot`** |
| Construction sites of `_WorkerTerminalBranchSignal(reason=...)` | None yet (Task 16 adds 6) | Sentinel raise-site count remains 0 |
| `_load_or_materialize_inspection` callsite | `:1055` (in `poll`) | No change — observable behavior preserved (canceled → `inspection=None`) |
| `_execute_live_turn` callsite | `:733` (in `start`) | No change — Task 17 will eventually rewrite to spawn worker |
| `_execute_live_turn` callsite | `:1888` (decide-resume) | No change |
| `cast` import | `:64` | Already present (Task 14 closeout-1) — do NOT re-add |
| `EscalatableRequestKind` import | `:90` | Already present (Task 14) — do NOT re-add |
| `worker_runner.py` | NEW | Create with `_WorkerRunner` class + `spawn_worker` helper |

### Sentinel reason mapping (spec authority)

```
Pre-capture (1):
  unknown_kind_interrupt_transport_failure → DelegationStartError(reason=same, cause=None)

Post-decide / post-Parked (5 — return stored DelegationJob, bypass _finalize_turn):
  internal_abort                    → status="unknown"
  dispatch_failed                   → status="unknown"
  timeout_interrupt_failed          → status="unknown"
  timeout_cancel_dispatch_failed    → status="unknown"
  timeout_interrupt_succeeded       → status="canceled"  ← only one with canceled, not unknown
```

Source: `design.md:474-484` (sentinel table) + `design.md:489-538` (catch site code).

The plan's loose header wording at `phase-f-worker.md:5` ("park, completion, unknown, timeout-interrupt-succeeded, internal-abort, worker-failure") is NOT authoritative — it conflates `Parked`/`WorkerFailed` (`ParkedCaptureResult` variants signaled via `announce_*`) with sentinel reasons.

### `_WorkerTerminalBranchSignal` empty-args mechanic (G9 source)

```python
@dataclass(frozen=True)
class _WorkerTerminalBranchSignal(Exception):
    reason: str
```

Frozen dataclass exceptions don't pass args to `Exception.__init__`. So:
- `signal.args == ()`
- `str(signal) == ""`
- `repr(signal)` shows the dataclass repr (includes reason)

**Implications for Task 15:**
- Logging `signal.reason` — works (carries the actual reason literal)
- Logging `str(signal)` — empty string (silent observability loss)
- Test assertions targeting `signal.reason` — works
- Test assertions targeting `str(signal)` — won't catch reason

This is the carry-forward A1 mechanic.

### `worker_runner.py` skeleton intent (lint-clean shape)

```python
"""Worker thread runner for Packet 1's deferred-approval model."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import TYPE_CHECKING

from .resolution_registry import ResolutionRegistry

if TYPE_CHECKING:
    from .delegation_controller import DelegationController

logger = logging.getLogger(__name__)


class _WorkerRunner:
    def __init__(
        self,
        *,
        controller: "DelegationController",
        registry: ResolutionRegistry,
        job_id: str,
        collaboration_id: str,
        runtime_id: str,
        worktree_path: Path,
        prompt_text: str,
    ) -> None:
        self._controller = controller
        self._registry = registry
        self._job_id = job_id
        # ... etc.

    def run(self) -> None:
        try:
            self._controller._execute_live_turn(
                job_id=self._job_id,
                collaboration_id=self._collaboration_id,
                runtime_id=self._runtime_id,
                worktree_path=self._worktree_path,
                prompt_text=self._prompt_text,
            )
        except Exception as exc:
            logger.exception("Worker runner: unhandled exception in _execute_live_turn")
            self._registry.announce_worker_failed(self._job_id, error=exc)
            return
        self._registry.announce_turn_completed_empty(self._job_id)


def spawn_worker(...) -> threading.Thread:
    runner = _WorkerRunner(...)
    thread = threading.Thread(target=runner.run, name=f"delegation-worker-{job_id}", daemon=True)
    thread.start()
    return thread
```

Differences from plan Step 15.3 verbatim:
- Drop unused `Callable` import (was in plan template)
- Drop dead `result = self._controller._execute_live_turn(...)` binding — call without assignment (plan template assigned to `result` but never used it for anything that mattered in Task 15 scope)

### conftest.py inventory (W11 source)

```python
# packages/plugins/codex-collaboration/tests/conftest.py
@pytest.fixture
def vendored_schema_dir() -> Path: ...   # line 14

@pytest.fixture
def client_request_schema(vendored_schema_dir: Path) -> Path: ...  # line 22

def make_test_handle(...) -> CollaborationHandle: ...  # line 34 — REGULAR FUNCTION, not a fixture
```

NO factory fixtures. NO `delegation_controller`/`simple_job_factory`/`artifact_store_spy`/`worker_runner_fixture`. The plan placeholder tests reference these names — they would fail collection with "fixture not found" errors.

Available alternatives:
- Built-in pytest fixtures: `monkeypatch`, `tmp_path`, `caplog`
- Module-local `_build_controller(tmp_path)` from `tests.test_delegation_controller` (used 30+ times across the package)
- `make_test_handle()` as a regular function call (callable inline)
- `unittest.mock.MagicMock(spec=_ArtifactStoreLike)` for protocol-based mocks

### Caller graph for the two helpers Task 15 modifies

| Helper | Callsite | File:line | Task 15 transitive effect |
|--------|----------|-----------|---------------------------|
| `_load_or_materialize_inspection` | `poll()` | `delegation_controller.py:1055` | None (`inspection=None` for canceled job — same observable behavior) |
| `_execute_live_turn` | `start()` | `delegation_controller.py:733` | Sentinel catch is dead code under Task 15 scope (handler body unchanged) |
| `_execute_live_turn` | decide-resume path | `delegation_controller.py:1888` | Same — sentinel catch is dead code |

**Zero transitive-effects gap candidates anticipated for Task 15.** Unlike Task 14's L4 transitive-effects gap (which expanded the breaking-test set from 3 to 8), Task 15's additions are scope-bounded.

## Context

### Project state

T-20260423-02 Packet 1 progress (post-Task-14, pre-Task-15):

| Phase | Tasks | Status |
|-------|-------|--------|
| A (types) | 1-5 | Complete |
| B (stores) | 6-9 | Complete (with closeout) |
| C (journal) | 10 | Complete (with closeout) |
| D (registry) | 11-12 | Complete (with closeouts) |
| E (serialization/projection) | 13-14 | Complete (with closeouts) |
| **F (worker)** | **15-16** | **Not started — Task 15 next (convergence map ready)** |
| G (public API) | 17-18 | Not started |
| H (finalizer/consumers/contracts) | 19+ | Not started |

13 open carry-forward items at start of Task 15 (will become 12 when L4 closes A1).

### Branch state

Branch: `feature/delegate-deferred-approval-response`. Clean working tree at `d8f1911b`. **One new uncommitted file at end of session:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md`. This is a working doc not a code change; can be committed alongside Task 15's feat commit OR separately as a docs-only commit (user discretion). The convergence map is itself binding for Task 15 dispatch, so committing it with Task 15 makes sense for traceability.

### Mental model

**Phase F = worker-side machinery.** Three orthogonal axes:
- Worker thread mechanics (Task 15 scaffold + Task 16 handler rewrite)
- Sentinel raise-site contract (Task 16 — 6 distinct reason literals)
- `update_parked_request` / `completion_origin` durable writes (Task 16)

Task 15 is the SCAFFOLD — purely additive, dead code under its own scope, activated by Task 16's raise sites + Task 17's worker spawn from `start()`.

**Phase G = public API rewrite.** `start()` waits for `wait_for_parked` (Task 17); `decide()` reservation context manager (Task 18). Phase G is where the worker actually runs in production.

**Phase H = finalizer + consumer surfaces.** `_finalize_turn` Captured-Request Terminal Guard (Task 19); `poll()` `UnknownKindInEscalationProjection` catch + `signal_internal_abort` (Task 20); `discard()` admits canceled (Task 21); contracts.md updates (Task 22).

Task 15 must not pre-wire any of these — the W1-W5 + W11 watchpoints are explicit fences.

### Environment

- Python 3.12, uv workspace, pytest test runner
- Run package suite: `uv run --package codex-collaboration pytest`
- Run lint: `uv run --package codex-collaboration ruff check packages/plugins/codex-collaboration/server/ packages/plugins/codex-collaboration/tests/`
- Branch protection hook: edits allowed on `feature/*`; blocked on `main`/`master`
- Branch is `feature/delegate-deferred-approval-response` — edits allowed throughout

### Task 15 commit shape (anticipated)

| Step | Type | Subject | Conditional? |
|------|------|---------|--------------|
| 1 | feat | `feat(delegate): add _WorkerRunner + sentinel catch scaffold + canceled-inspection tuple (T-20260423-02 Task 15)` | Always |
| 2 | fix | `fix(delegate): <whatever review surfaces>` | Only if review surfaces issues |
| 3 | docs | `docs(delegate): record Phase F Task 15 closeout` | Only if real new carry-forward items |

Task 15 is anticipated to be a 1-commit task (no closeout-fix expected; convergence map's W coverage is dense enough to catch most issues pre-dispatch).

## Conversation Highlights

**Workflow choice (definitive):**
User invoked `/handoff:load` to start, then "Continue with Phase F Task 15 read-only orientation pass" — explicit read-only mode, no implementer dispatch this session.

**Independent-read-first protocol (definitive):**
User pasted `/copy`-output independent read at message 3, paralleling Tasks 13 + 14: "I mostly agree with your extensions. The one place I'd tighten your recommendation is E1: omit the fictional-fixture placeholder tests, yes, but do not leave the sentinel catch entirely untested if Task 15 lands that catch."

**E1 tightening (binding):**
User: "Add only real, concrete tests using module-local helpers. I would include: `_WorkerRunner is not None`, two `_load_or_materialize_inspection` canceled contract tests, at least one concrete sentinel-catch test, using local fakes/monkeypatching, because Task 15 actually changes `_execute_live_turn` behavior."

**A1 logging severity (binding):**
User: "I'd prefer `logger.info` or `logger.debug` for normal post-branch sentinel consumption, but warning/error would be too noisy because post-branch sentinel handling is expected control flow."

**Convergence-map shape (binding for Task 15):**
User provided complete L1-L8 + W1-W8 + test triage. I extended with W9-W11 for traps I had identified during my read.

**Required edits round 2 (binding):**
User: "Confirm with two required edits before dispatch. (1) Do not say the worker_runner.py skeleton matches Step 15.3 verbatim. The plan skeleton has at least two likely lint issues: Callable is imported but unused; result = self._controller._execute_live_turn(...) is assigned but unused. (2) Avoid fixed post-edit line numbers in acceptance."

User added a third soft edit: "Acceptance criterion 1: replace 'passes ruff + pyright clean' with the exact checks you want the implementer to run. If the dispatch does not provide a type-check command, say 'no lint/type regressions in modified files' rather than 'pyright clean.'"

**caplog allowance (binding):**
User: "Sentinel logging test: add `caplog` as an allowed real pytest fixture. It is built-in, not a fictional project fixture. The assertion should be substring-based on `dispatch_failed` or `unknown_kind_interrupt_transport_failure`, not exact message equality."

**Context-management directive (binding):**
User: "Given 94% context, I would not dispatch the implementer from this session. Task 15 is small, but the proper workflow is implementer + spec review + quality review, and that can easily overrun the remaining context. Best next move: save this convergence map into a working doc or handoff, then dispatch Task 15 fresh."

**Working style observed:** User produces tight, evidence-first refinements with explicit corrections. Pre-locks structural decisions in convergence maps. Uses `/copy` heavily for external verification. Treats locks as non-negotiable. Distinguishes structural traps (line numbers, fixture names) from mechanical traps (lint issues) — the recommended dispatch posture explicitly addresses both classes.

## User Preferences

(All carry-over items from Tasks 13/14 still apply; new this session noted below.)

**Workflow:** `superpowers:subagent-driven-development` — controller does not implement; review subagents critique. **Single fresh implementer + spec reviewer + code-quality reviewer per task, sequential not parallel.** One implementer per task.

**Convergence-map structure:** Live-anchors table + Locks (L1-Lₙ) + Watchpoints (W1-Wₙ) + Per-test triage table + Out-of-scope table with plan-line citations + Acceptance criteria + Pre-dispatch checklist + Commit shape + Carry-forward expectations table. Binding — dispatch only after the full map is in the prompt.

**Acceptance criteria style (NEW):** Structural location, NOT post-edit line numbers. "Inserted in the first `run_execution_turn` try block, before the generic `except Exception`" — NOT "inserted at `:845`." Pre-edit anchors are fine for orientation/locks but not for post-edit acceptance.

**Plan-template literalism (NEW):** "Verbatim" should be qualified for lint-hygiene adjustments. Plan templates pre-date lint passes; unused imports + dead bindings are common. Convergence map should explicitly say "follows the intended Step 15.X behavior, with lint-clean adjustments."

**Logging severity (NEW):** `logger.info` for expected control flow events (e.g., post-branch sentinel handling). NOT `warning` or `error` — those are reserved for genuine anomalies.

**Test fixture taxonomy (NEW):** Built-in pytest fixtures (`monkeypatch`, `tmp_path`, `caplog`) are acceptable. Module-local helpers (e.g., `_build_controller`) are preferred. Module-level helper functions in conftest.py (`make_test_handle`) are acceptable as regular function calls. **Fictional fixture names from plan templates** (project-defined-but-nonexistent) are W-locked.

**Test assertion style (NEW):** Substring assertions on log content (`"dispatch_failed" in caplog.text`), NOT exact message equality. Robust against logging-format drift.

**Closeout cadence:** `feat → optional fix(es) → optional closeout-docs`. Task 13 was 5+1; Task 14 was 3+1. Task 15 anticipated as 1+0 (no closeout) unless review surfaces real items.

**Commit discipline:** New commits, never amend. CLAUDE.md (global): "Always create NEW commits rather than amending."

**Scope discipline:** Locked decisions and watchpoints are hard constraints. Out-of-scope items have explicit plan-line landing points. No silent scope expansion.

**Per-test triage style:** No blanket migrations. Every old test gets per-case judgment. Triage table in dispatch packets is binding.

**Skip-reason rubric:** Each `@pytest.mark.skip(reason=...)` must (a) cite specific Phase/Task as unblock owner, (b) explain structural mechanic, (c) point to real sibling for partial coverage OR honestly explain why no real sibling exists. Fabricated sibling citations are the failure mode the rubric exists to prevent (Task 14 closeout-2 caught two instances).

**Evidence density:** File:line citations expected throughout; tables preferred over prose.

**External verification:** User uses `/copy` heavily for out-of-session verification.

**Process gap signaling:** BLOCKED + question preferred over DONE_WITH_CONCERNS + unilateral decision. Controller adjudicates scope; implementer faithfully executes.

**Context management (NEW for this session):** Don't dispatch implementer + reviewers + closeout cycles when context is approaching saturation. Save convergence map to working doc; dispatch fresh.

## Next Steps

### 1. Phase F Task 15 dispatch (FRESH session)

**Dependencies:** Phase E complete ✅. Convergence map saved ✅.

**Procedure for fresh-session dispatch:**

1. `/handoff:load` — resumes from this handoff
2. Read `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md` — binding scope contract
3. (Optional) Skim `phase-f-worker.md:1-374` (Task 15 body) for plan literal — convergence map already extracts the binding parts
4. Invoke `superpowers:subagent-driven-development`
5. Construct dispatch packet with:
   - Convergence map content (full file)
   - Spec sentinel table (`design.md:474-484`)
   - Spec catch site code (`design.md:489-538`)
   - Plan Step 15.3 (worker_runner skeleton — note lint-clean adjustments per L2)
   - Plan Step 15.4 (tuple expansion)
   - Per-test triage table (already in convergence map)
   - Reporting contract: `DONE` with commit SHA + suite output line + W8 grep result + per-lock conformance summary; `BLOCKED` with question if any lock turns out unreachable (NOT `DONE_WITH_CONCERNS`)
6. Dispatch implementer (sonnet, general-purpose subagent)
7. After feat commit: spec-compliance reviewer (sonnet, general-purpose)
8. After spec review: code-quality reviewer (`superpowers:code-reviewer`)
9. If review surfaces issues: round-trip via SendMessage to same implementer for closeout-fix
10. If real new carry-forward items emerge: closeout-docs commit per Task 13/14 cadence

**Acceptance criteria:** see convergence map's Acceptance section.

### 2. Phase F Task 16 dispatch (subsequent fresh session)

**Dependencies:** Task 15 complete + closeouts (if any).

**Approach:** Construct a fresh convergence map for Task 16 specifically. User's recommended posture: "rows for: all direct `run_execution_turn`/handler exit paths, all six sentinel reasons, `registry.register` argument conformance, `update_parked_request` set/clear points, `completion_origin="worker_completed"` writes, and the eight Task 14 skip owners."

Task 16 is the LARGEST task in the plan per `phase-f-worker.md:385`. Anticipated convergence map: 2-3x larger than Task 15. Save as `task-16-convergence-map.md` in the same directory.

Sweep candidates at Task 16:
- Carry-forward A2 (raise-site comments absorb sentinel caller-contract docs)
- Carry-forward C10.4 (`completion_origin="worker_completed"` writes)
- 2 Mode B unblock tests (`test_delegation_controller.py:2588`, `test_delegate_start_integration.py:793`)

Critical Task 16 watchpoints (carried over from this session):
- `ResolutionRegistry.register(..., kind=...)` is a REQUIRED keyword arg — plan pseudocode shows it without `kind`. Implementer must pass `parsed.kind` (already narrowed via `_CANCEL_CAPABLE_KINDS` + `_KNOWN_DENIAL_KINDS` filter at handler-rewrite time).
- Sentinel raise-site count must reach exactly 6 at Task 16 commit time — `rg "_WorkerTerminalBranchSignal\(reason=" packages/plugins/codex-collaboration/server/delegation_controller.py | wc -l` must return `6`.
- The 5 omitted plan placeholder tests from Task 15 (`test_worker_runner_translates_return_to_announce_parked`, etc.) may be appropriate to author at Task 16 if real fixtures exist by then; defer to Task 17 (start-async) per the plan's Pre-Execution Notes.

### 3. Carry-forward sweep candidates (later)

Open items at start of Task 15 (13 total; will become 12 when A1 closes):

| Item | Landing point | Trigger |
|------|---------------|---------|
| **A1** | **Task 15 (THIS upcoming task)** | **L4 logger.info catch — closes at Task 15** |
| A2 | Task 16 raise sites | Caller-contract docs absorbed at raise-site comments |
| C10.4 | Task 16 worker-runner work | `completion_origin="worker_completed"` writes |
| 2 Mode B tests (`:2588`, `:793`) | Task 16 | `update_parked_request` callsite wiring |
| 6 Mode A tests (`:1360`, `:1418`, `:1737`, `:2372`, `:617`, `:1062`) | Task 17 | Unknown-kind handling at L6 callsite |
| E13.2, E13.3 | Phase H | Phase H owns contracts.md + docstring trim |
| E14.1 | End-of-Packet-1 polish | `get_args` derivation refactor |
| A4, B6.x, B7.x, B8.x, C10.2-C10.3, A5, E13.1 | End-of-Packet-1 polish | Per landing-point rows |

No immediate action — these are deferred by design.

## In Progress

Clean stopping point — convergence map drafted, refined twice, edits applied, working doc written. No work in flight in this session.

The pending work (Phase F Task 15 implementer dispatch) is fully prepared for fresh-session execution. The convergence map is the binding contract; this handoff is the entry point.

## Open Questions

None pending action. Three questions surfaced and were resolved in-session:

1. **Disposition for plan placeholder tests?** Resolved: omit entirely (W11). Task 15 ships 5 net new tests using module-local helpers + built-in fixtures only.

2. **A1 logging severity?** Resolved: `logger.info`. Post-branch sentinel handling is expected control flow; warning/error too noisy.

3. **Dispatch this session or fresh?** Resolved: fresh. Two-stage review + closeout cycles risk context overrun. Working doc preserves binding contract.

## Risks

### R1: Dead-code sentinel catch invites premature wiring at Task 15

**Concern:** The catch is structurally unreachable under Task 15 scope (handler body has no raise sites yet). An implementer reading the plan literal might "fix" the dead-code observation by adding raise sites in Task 15 (Task 16 territory) or wiring `start()` to spawn the worker (Task 17 territory).

**Mitigation:** W1, W3, W8 explicit. W8 includes a commit-time grep check (`_WorkerTerminalBranchSignal\(reason=` count must return 0). Convergence map's "Out of scope" table has plan-line citations for each potential scope-creep direction.

**Severity:** Low — convergence map is dense enough to catch this; reviewers map locks/watchpoints during their passes.

### R2: Test surface mismatch with plan placeholders

**Concern:** Plan template includes 5 placeholder tests with fictional fixtures. If implementer takes plan-literal-verbatim, will paste them in and pytest fails on collection ("fixture not found") OR adds skip decorators with potentially-fabricated unblock citations (Task 14 closeout-2 pattern).

**Mitigation:** Per-test triage table explicitly lists each placeholder test as Omit (with reason). W11 explicit. Convergence map binds Task 15 test surface to 5 net new tests + 5 explicitly-omitted.

**Severity:** Low — triage table is binding; reviewers will catch deviations.

### R3: Convergence map file may diverge from working code

**Concern:** Convergence map's live anchors are verified at 2026-04-25. If Task 15 dispatch doesn't happen for several days, intervening commits could shift line numbers further, making the live anchors stale.

**Mitigation:** Working doc includes a "Drafted: 2026-04-25" date stamp. Fresh-session dispatch should re-verify live anchors before sending implementer (one `grep -n` pass per symbol). The convergence map's structural locks (L1-L8) are content-based, not line-based, so stay valid.

**Severity:** Low — fresh session re-verification is cheap; locks are structural.

### R4: Task 16 may surface convergence-map gaps that retroactively touch Task 15's surface

**Concern:** Task 16's handler rewrite activates Task 15's sentinel catch. If Task 16's convergence map drafting reveals that Task 15's catch shape was wrong (e.g., needs to log differently or raise a different exception type), Task 15's commit might need revision.

**Mitigation:** Spec sentinel table at `design.md:474-484` is authoritative for catch shape; Task 15's L3-L6 are derived directly from spec. The catch shape is structurally pinned by the spec, so Task 16 should not invalidate it. If spec evolves, both tasks would need revision regardless.

**Severity:** Low — spec is stable; convergence map binds to spec.

## References

- **Branch:** `feature/delegate-deferred-approval-response` @ `d8f1911b`
- **Convergence map (this session's deliverable):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-15-convergence-map.md`
- **Phase F plan (Task 15 + 16):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-f-worker.md` (1189 lines)
- **Manifest (Pre-Execution Notes for placeholder tests):** `docs/plans/2026-04-24-packet-1-deferred-approval-response.md` (198 lines, see lines 91-119)
- **Carry-forward tracker:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (152 lines, 13 open items)
- **Phase G plan (Task 17 owns Mode A unblock):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md`
- **Phase H plan:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-h-finalizer-consumers-contracts.md`
- **Design spec sentinel reason table:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md:474-484`
- **Design spec sentinel catch site code:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md:489-538`
- **Prior session handoff (resumed_from):** `docs/handoffs/archive/2026-04-25_12-40_phase-e-task-14-complete-phase-f-next.md`
- **Phase E Task 14 closeout-docs (style reference):** commit `d8f1911b`
- **Plan symbols at live line numbers:**
  - `_WorkerTerminalBranchSignal` at `delegation_controller.py:201-223`
  - `DelegationStartError` at `delegation_controller.py:153-185`
  - `_execute_live_turn` first try/except at `delegation_controller.py:837-852`
  - `_load_or_materialize_inspection` at `delegation_controller.py:1012-1041`
  - `ResolutionRegistry.register` at `resolution_registry.py:173-180`
  - conftest.py inventory at `tests/conftest.py:14-52`

## Learnings

### L1: Plan-line drift is per-task, not session-once

**Mechanism:** Plan templates are written before the codebase reaches stability for a given task. Phase E Task 14 had stale line numbers (helper at `:963`, plan said `:965`). Phase F Task 15 has the same pattern (helper at `:1012`, plan says `:873`). Pattern: convergence map MUST verify live line numbers each task.

**Evidence:** Task 14's plan template referenced `_project_pending_escalation` at `:967`; current code is `:990`. Task 15's plan references `_load_or_materialize_inspection` at `:873`; current code is `:1012`. Same offset class — early-Phase-A drafted plans haven't been kept in sync as Tasks 6-14 added intermediate lines.

**Implications:** Don't trust plan-line numbers as anchors. Always run a quick `grep -n` pass before drafting the convergence map. Use a "Live anchors" table at the top of every convergence map.

**Watch for:** Plans drafted before the implementing codebase exists, OR plans that span enough commits that line numbers shift. The earlier the plan was written relative to the current state, the more drift.

### L2: Plan placeholder fixtures are an anti-pattern across phases

**Mechanism:** Plan templates often include placeholder tests with concrete docstrings + `pass` bodies + fixture references like `delegation_controller`, `simple_job_factory`, `artifact_store_spy`. These fixtures may not exist in conftest.py. The Pre-Execution Notes section of the manifest formally acknowledges this for SOME tasks (Tasks 10, 16, 17, 18, 19, 20) but not all (Task 15 not listed even though its plan template includes such placeholders).

**Evidence:** Phase F Task 15 plan template at `phase-f-worker.md:46-97` includes 5 placeholder tests referencing `worker_runner_fixture`/`delegation_controller`/`simple_job_factory`/`artifact_store_spy`. conftest.py at `tests/conftest.py:14-52` has only 2 schema fixtures + `make_test_handle` regular function. Pasting the placeholders in would cause pytest collection errors.

**Implications:** Convergence map MUST W-lock against pasting fictional-fixture placeholder tests. Skip-decoration is risky (Task 14 closeout-2 fabrication risk). Omit entirely.

**Watch for:** Plan templates that include placeholder test bodies with fixture parameters. Cross-check against actual conftest.py before drafting test triage.

### L3: Spec table > plan header text

**Mechanism:** Plan headers can have loose summary wording that doesn't match the authoritative spec table. Phase F's plan header at `phase-f-worker.md:5` lists 6 "branches" but conflates `Parked`/`WorkerFailed` (`ParkedCaptureResult` variants) with sentinel reasons. The spec sentinel table at `design.md:474-484` is the canonical 6-reason set.

**Evidence:** Plan header: "park, completion, unknown, timeout-interrupt-succeeded, internal-abort, worker-failure". Spec table: `internal_abort`, `dispatch_failed`, `timeout_interrupt_failed`, `timeout_interrupt_succeeded`, `timeout_cancel_dispatch_failed`, `unknown_kind_interrupt_transport_failure`. The "park" / "completion" / "worker-failure" labels in the plan header refer to `announce_*` capture-ready signals, NOT sentinel reasons.

**Implications:** In plan-vs-spec discrepancies, prefer spec authority. The spec is denser and was reviewed adversarially during the design phase; plan headers are summary scaffolding written for navigation.

**Watch for:** Plan headers that paraphrase spec tables. Verify all enumerations match the spec literal.

### L4: Independent-read-first-pass workflow is highly compressive

**Mechanism:** User pastes a `/copy`-output independent read at the start of orientation, before I've finished my own. The two reads converge on a tighter map than either alone. Calibration: user's read tends to hit higher-level structural traps (API drift, phase boundaries); my read tends to hit lower-level mechanical traps (line-number drift, lint hygiene, dead-code aspects).

**Evidence:** Task 13: user identified the wire-shape vs timing-semantics separation; I identified the orphan `updated_job` binding. Task 14: user identified the tombstone-guard-on-resolved-after-D4 watchpoint; I identified the convergence-map L4 transitive-effects gap. Task 15: user identified `registry.register(..., kind=...)` API drift; I identified the lint-hygiene issues + line-number drift.

**Implications:** Two-read convergence map is structurally more robust than one-read. The patterns are complementary, not redundant.

**Watch for:** Single-read maps risk under-coverage in whichever class (structural vs mechanical) the drafter is weaker at. Always solicit user's own read before dispatch.

### L5: Acceptance criteria should describe structural location, not post-edit line numbers

**Mechanism:** Line numbers shift mid-commit. An acceptance criterion saying "inserted at `:845`" becomes false the moment the new clause is inserted (because `:845` is now where the OLD next line went). Acceptance must be content-based: "inserted in the first `run_execution_turn` try block, before the generic `except Exception:`."

**Evidence:** User's required edit 2: "Avoid fixed post-edit line numbers in acceptance. 'Inserted at `:845`' is fine as an orientation anchor, but after the edit the line number will shift."

**Implications:** Pre-edit anchors (live anchors table) are fine for orientation/locks (WHERE TO EDIT). Post-edit acceptance must be structural (WHAT THE STRUCTURE LOOKS LIKE).

**Watch for:** Convergence maps that pin acceptance to specific line numbers. Convert to structural location descriptions.

### L6: Plan-template-verbatim is an anti-pattern in lint-strict codebases

**Mechanism:** Plan templates pre-date lint passes. Common artifacts: unused imports (`Callable`, `cast`), dead bindings (`result = self._controller.foo()` unused), inline `import` statements that violate module-level convention. Implementers who paste verbatim ship lint regressions.

**Evidence:** Plan Step 15.3's `worker_runner.py` skeleton imports `Callable` (unused) and assigns `result = self._controller._execute_live_turn(...)` (unused). User's required edit 1: "Do not say the worker_runner.py skeleton matches Step 15.3 verbatim."

**Implications:** Convergence map should explicitly say "follows the intended Step 15.X behavior, with lint-clean adjustments." Implementer adapts to lint-clean equivalents. Reviewers catch lint regressions during code-quality pass.

**Watch for:** Plan templates with concrete code blocks. Verify lint hygiene before locking the implementer to verbatim copying.

### L7: Working-doc convergence maps decouple session boundaries from binding artifacts

**Mechanism:** Carrying a binding scope contract in a handoff body forces the next session to re-derive it from chat history (lossy) or copy-paste from an old handoff (token-heavy). Saving to a working doc (`task-N-convergence-map.md`) preserves it as a durable, citable artifact.

**Evidence:** User's context-management directive: "Best next move: save this convergence map into a working doc or handoff, then dispatch Task 15 fresh." The "or handoff" alternative is acceptable but worse — handoffs are ephemeral working memory; working docs are durable plan artifacts that fit the existing `docs/plans/.../` directory structure.

**Implications:** For thin tasks, carry the convergence map in the handoff body. For substantive tasks where dispatch may take a separate session, save as a working doc. Reference from handoff Next Steps.

**Watch for:** Convergence maps that span session boundaries. Default to working-doc placement.

## Gotchas

(Carry-over from prior session: G1-G8 still apply. New this session: G9-G13.)

### G1-G8 (carry-forward from prior handoff)

Apply identically. See `docs/handoffs/archive/2026-04-25_12-40_phase-e-task-14-complete-phase-f-next.md` for full text.

### G9: `_WorkerTerminalBranchSignal` is `@dataclass(frozen=True) Exception` with empty `args`

`str(signal) == ""`. `signal.args == ()`. Catch sites must use `signal.reason` (the dataclass field) for any logging or error message construction. Carry-forward A1 captures this; Task 15 L4 closes A1 by logging `signal.reason` via `logger.info` at the catch site.

**Do NOT log `str(signal)`** — silent observability loss.

### G10: Plan placeholder tests use fictional fixture names

`worker_runner_fixture`, `delegation_controller`, `simple_job_factory`, `artifact_store_spy` do NOT exist in conftest.py. conftest.py only has `vendored_schema_dir`, `client_request_schema` fixtures + `make_test_handle` helper function. Use module-local `_build_controller` from `test_delegation_controller.py` (per Task 14 W4 precedent).

**Do NOT paste plan placeholder tests with fictional fixtures into Task 15's `test_worker_runner.py`** — pytest collection fails with "fixture not found." Convergence map W11 + per-test triage table explicitly omits each.

### G11: Plan-line numbers throughout phase-f-worker.md are stale

Helper at `:873` is actually at `:1012`. `_execute_live_turn` at `:722-757` is actually at `:741-872`. `_server_request_handler` body at `:650-720` is actually at `:765-835`. The plan was drafted before Tasks 6-14 added intermediate lines.

**Do NOT use plan-cited line numbers as anchors** — verify via `grep -n` against current code. Convergence map's "Live anchors" table has the verified numbers (as of 2026-04-25).

### G12: Plan header sentinel labels differ from spec sentinel reasons

Plan header at `phase-f-worker.md:5` says "park, completion, unknown, timeout-interrupt-succeeded, internal-abort, worker-failure". `Parked` is a `ParkedCaptureResult` variant (signaled via `announce_parked`); `WorkerFailed` is the OUTER `except Exception` path (`announce_worker_failed`). Neither is a sentinel reason.

**Spec table at `design.md:474-484` is authority:** `internal_abort`, `dispatch_failed`, `timeout_interrupt_failed`, `timeout_interrupt_succeeded`, `timeout_cancel_dispatch_failed`, `unknown_kind_interrupt_transport_failure`.

### G13: `ResolutionRegistry.register(..., kind=...)` requires `kind: EscalatableRequestKind` kw arg (Task 16 trap)

Plan pseudocode at `phase-f-worker.md:663-667` shows `registry.register(parsed.request_id, job_id=job_id, timeout_seconds=...)` — missing `kind`. Live API at `resolution_registry.py:173-180` requires `kind: EscalatableRequestKind` as a kw-only arg.

**Task 15 does NOT call `registry.register`** (handler body unchanged), so this is NOT a Task 15 trap — captured here for the upcoming Task 16 dispatch packet. Implementer must pass `parsed.kind` (already narrowed via `_CANCEL_CAPABLE_KINDS` filter at handler rewrite time).

### G14: Worker-runner skeleton's `announce_turn_completed_empty` fallthrough is dead under Task 15

`_WorkerRunner.run` ends with `self._registry.announce_turn_completed_empty(self._job_id)` if no exception. But Task 15 does NOT spawn a worker thread anywhere, AND `DelegationController.__init__` does NOT have `_registry` (Task 16 step 16.4 adds it). So `_WorkerRunner` cannot be instantiated end-to-end under Task 15 scope.

**Do NOT "fix" this dead-code observation by:**
- Adding `_registry` to `__init__` (W2 — Task 16 territory)
- Spawning workers in `start()` (W3 — Task 17 territory)
- Adding handler raise sites (W1 — Task 16 territory)

Task 15's worker-runner skeleton is intentionally testable only in isolation (e.g., construct a `_WorkerRunner` with a real `ResolutionRegistry()` directly + a mock `DelegationController` for `_execute_live_turn` injection).
