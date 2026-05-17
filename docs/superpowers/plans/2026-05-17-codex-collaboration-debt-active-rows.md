# May 17 Debt Active Rows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute only the active `DEBT-20260517-*` backlog rows from the May 17 debt audit, leaving watch rows trigger-backed unless their register trigger fires.

**Architecture:** The reconciliation register owns routing; the audit owns problem statements and evidence. This plan converts the five open active rows into four reviewable phases with explicit branch boundaries, verification gates, and stop conditions. Ticket-owned HL1 work remains on `T-20260516-01` / `T-20260516-02`; deferred HL3 and watch rows remain out of scope.

**Tech Stack:** Python 3.11+, pytest, ruff, GitHub Actions, JSONL audit/journal files, Markdown specs/status docs.

---

## Current Anchors

- Repo: `/Users/jp/Projects/active/codex-collaboration`
- Audit source: `docs/audits/2026-05-17-codex-collaboration-debt.md`
- Active routing source: `docs/status/reconciliation-register.md` rows `DEBT-20260517-QW1-LOGGING`, `DEBT-20260517-QW2-DRAIN-WORKERS`, `DEBT-20260517-HL2-CRASH-RESTART-AUDIT`, `DEBT-20260517-QW3-HYGIENE`, `DEBT-20260517-HL4-DELEGATION-TEST-SEAMS`
- Status source: `docs/status/current-state.md` watchpoint for the May 17 active backlog
- Existing broad plan pattern: `docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md`; use its phase-gate discipline, not its size

## Out Of Scope

- Do not implement audit watch rows `DEBT-20260517-WL*` unless the matching trigger has fired and the register is updated first.
- Do not execute HL1 under this plan. Route Codex App Server version-pin and contract-version work through `T-20260516-01` and `T-20260516-02`.
- Do not implement the concurrent-promotion lock. It remains deferred under `WL6-CONCURRENT-PROMOTION-LOCK`.
- Do not use transient `.tech-debt-audit-workspace/` artifacts as proof unless a phase explicitly regenerates or promotes a durable appendix.

## File Structure

Expected touch points by phase:

- Phase 1, QW1 logging:
  - Modify `scripts/codex_runtime_bootstrap.py`
  - Modify `README.md`
  - Test `tests/test_bootstrap.py`
- Phase 1, QW2 worker drain:
  - Modify `server/delegation_controller.py`
  - Test `tests/test_delegation_controller.py`
  - Test `tests/test_delegate_start_integration.py`
  - Test `tests/test_delegate_start_async_integration.py`
- Phase 2, HL2 crash/restart audit:
  - Create `docs/specs/design-docs/2026-05-17-crash-restart-audit-events.md`
  - Modify `docs/specs/contracts.md`
  - Modify `docs/specs/recovery-and-journal.md`
  - Modify `server/journal.py`, `server/mcp_server.py`, and the controller recovery methods the design names
  - Test `tests/test_journal.py`, `tests/test_mcp_server.py`, plus controller-specific recovery tests
- Phase 3, QW3 hygiene:
  - Modify `README.md`, `AGENTS.md`, `.claude/CLAUDE.md`
  - Modify `docs/specs/delivery.md`
  - Modify `.github/workflows/ci.yml`
  - Create `.github/dependabot.yml`
  - Modify `server/delegation_controller.py`
  - Modify `server/jsonrpc_client.py`
  - Potentially modify `pyproject.toml`, `.claude-plugin/plugin.json`, and `server/runtime.py`, or explicitly hand that subitem to `T-20260516-01`
- Phase 4, HL4 delegation test seams:
  - Modify `server/delegation_controller.py`
  - Potentially modify `server/resolution_registry.py` only if the registry injection seam requires a protocol extraction
  - Test `tests/test_delegation_controller.py`
  - Test `tests/test_delegate_start_async_integration.py`
  - Test `tests/test_delegate_decide_async_integration.py`
  - Test `tests/test_projection_helpers.py`
  - Optionally add `tests/test_delegation_controller_test_seams.py`
- Status closeout for every phase:
  - Modify `docs/status/reconciliation-register.md` when a row is closed or re-routed
  - Modify `docs/status/current-state.md` when current-state watchpoints change
  - If a phase branch deliberately does not change status docs, state the reason in the PR body

## Phase Boundaries

Use one branch per phase, created from current `main` after this plan lands:

1. `chore/debt-20260517-observability-drain` for QW1 + QW2.
2. `chore/debt-20260517-crash-restart-audit` for HL2.
3. `chore/debt-20260517-hygiene` for QW3.
4. `chore/debt-20260517-delegation-test-seams` for HL4.

Phase 1 may split after QW1 if QW2 requires broader worker lifecycle changes than `server/delegation_controller.py` plus the named tests. Phases 2 and 4 must stay isolated because they touch recovery semantics and test harness seams respectively.

## Global Verification Gates

Run these before claiming any phase PR ready and again before claiming the whole
plan complete. Targeted phase commands are fast preflight only; they do not
replace the repo-wide completion bar.

```bash
uv run pytest tests -q -m ""
uv run ruff check .
git diff --check
```

Expected final state: full marker-inclusive pytest passes, ruff passes, no whitespace errors, the five active register rows are closed or explicitly re-routed with evidence, and no watch row is silently promoted. No phase branch is ready for review until these same full gates pass on that branch.

## Hard Stop Conditions

- Stop if Phase 1 QW2 needs changes to `server/worker_runner.py`, `server/resolution_registry.py`, or control-plane runtime ownership semantics. Split QW2 into its own branch and update this plan before continuing.
- Stop if Phase 2's mini-design requires changing the `AuditEvent` schema instead of using contract-valid existing fields. Patch the design/spec first and review before implementation.
- Stop if Phase 2 cannot name a concrete `crash` emission path with tests. Either patch the design to include a real crash locus or split crash emission into a named residual row and keep `DEBT-20260517-HL2-CRASH-RESTART-AUDIT` open.
- Stop if Phase 2 cannot name the duplicate-prevention owner and recovery idempotency key before source work starts.
- Stop if Phase 2 cannot prevent duplicate `restart` events across eager `startup()` and lazy `_ensure_*_controller()` recovery paths.
- Stop if QW3's version-surface item changes the intended public plugin version rather than only aligning stale surfaces. Route the version decision through `T-20260516-01`.
- Stop if Phase 4's proposed seam is read-only only. HL4 requires both observation and behavior/protocol seams; a snapshot alone is not closure.

---

## Phase 1: QW1 Logging + QW2 Drain Workers

**Rows:** `DEBT-20260517-QW1-LOGGING`, `DEBT-20260517-QW2-DRAIN-WORKERS`

**Branch:** `chore/debt-20260517-observability-drain`

**Purpose:** Make startup diagnostics visible, then add a supported worker-drain seam so tests stop depending on process-wide thread-name enumeration.

### Task 1.1: Configure Bootstrap Logging

**Files:**
- Modify `scripts/codex_runtime_bootstrap.py`
- Modify `README.md`
- Test `tests/test_bootstrap.py`

- [ ] **Step 1: Add failing bootstrap logging tests**

  Add tests in `tests/test_bootstrap.py` that prove:
  - `main()` calls a bootstrap logging configuration helper before startup work emits INFO/WARNING records.
  - `CODEX_COLLAB_LOG_LEVEL=INFO` makes an INFO record for the resolved `plugin_data_path` visible.
  - an invalid `CODEX_COLLAB_LOG_LEVEL` falls back to `WARNING` and does not crash startup.

  Run:

  ```bash
  uv run pytest tests/test_bootstrap.py -q
  ```

  Expected before implementation: the new logging tests fail because no helper configures root logging and no startup INFO record names `plugin_data_path`.

- [ ] **Step 2: Implement the minimal logging helper**

  In `scripts/codex_runtime_bootstrap.py`, add `import os`, define `CODEX_COLLAB_LOG_LEVEL`, and call the helper at the top of `main()` before `default_plugin_data_path()`:

  ```python
  _LOG_LEVEL_ENV = "CODEX_COLLAB_LOG_LEVEL"


  def _configure_logging() -> None:
      raw_level = os.environ.get(_LOG_LEVEL_ENV, "WARNING").upper()
      level = logging.getLevelNamesMapping().get(raw_level, logging.WARNING)
      logging.basicConfig(
          level=level,
          format="%(asctime)s %(levelname)s %(name)s: %(message)s",
      )
      if level == logging.WARNING and raw_level not in logging.getLevelNamesMapping():
          logger.warning(
              "invalid CODEX_COLLAB_LOG_LEVEL; falling back to WARNING. Got: %r",
              raw_level,
          )
  ```

  Then make `main()` start with:

  ```python
  def main() -> None:
      _configure_logging()
      plugin_data_path = default_plugin_data_path()
      logger.info("plugin data path resolved: %s", plugin_data_path)
      journal = OperationJournal(plugin_data_path)
  ```

- [ ] **Step 3: Document the env var**

  Add this row to the README Configuration table:

  ```markdown
  | `CODEX_COLLAB_LOG_LEVEL` | `WARNING` | Root logging level for the bootstrap process. Use `INFO` for startup diagnostics such as the resolved plugin data path; invalid values fall back to `WARNING`. |
  ```

- [ ] **Step 4: Verify QW1**

  Run:

  ```bash
  uv run pytest tests/test_bootstrap.py -q
  uv run ruff check scripts/codex_runtime_bootstrap.py tests/test_bootstrap.py
  ```

  Expected: all selected tests pass and ruff reports no findings.

### Task 1.2: Add Supported Worker Drain Seam

**Files:**
- Modify `server/delegation_controller.py`
- Test `tests/test_delegation_controller.py`
- Test `tests/test_delegate_start_integration.py`
- Test `tests/test_delegate_start_async_integration.py`

- [ ] **Step 1: Lock current worker-thread dependence**

  Run:

  ```bash
  rg -n "threading\\.enumerate\\(\\).*delegation-worker|delegation-worker-job-1|signal_internal_abort\\(\"99\"" tests/test_delegation_controller.py tests/test_delegate_start_integration.py tests/test_delegate_start_async_integration.py
  ```

  Expected at plan time: hits remain in `tests/test_delegation_controller.py` and `tests/test_delegate_start_integration.py`; use this output as the migration checklist.

- [ ] **Step 2: Add failing tests for the seam**

  Add targeted tests proving:
  - `DelegationController.start()` records the `threading.Thread` returned by `spawn_worker(...)`.
  - `controller.drain_workers(timeout=...)` joins tracked finished workers and prunes them from the controller-owned list.
  - `drain_workers()` returns still-alive worker names instead of pretending to unblock parked workers.

  Run:

  ```bash
  uv run pytest tests/test_delegation_controller.py -q
  ```

  Expected before implementation: the new tests fail because `DelegationController` has no `_worker_threads` collection and no `drain_workers()` method.

- [ ] **Step 3: Implement the seam without changing parked-worker semantics**

  In `server/delegation_controller.py`, add the result type near other small dataclasses:

  ```python
  @dataclass(frozen=True)
  class WorkerDrainResult:
      joined_thread_names: tuple[str, ...]
      alive_thread_names: tuple[str, ...]
  ```

  In `DelegationController.__init__`, add:

  ```python
  self._worker_threads: list[threading.Thread] = []
  ```

  Import `threading` at module scope if it is not already present.

  Replace the current fire-and-forget spawn call:

  ```python
  spawn_worker(...)
  ```

  with:

  ```python
  worker_thread = spawn_worker(...)
  self._worker_threads.append(worker_thread)
  ```

  Add:

  ```python
  def drain_workers(self, timeout: float = 5.0) -> WorkerDrainResult:
      joined: list[str] = []
      alive: list[str] = []
      remaining: list[threading.Thread] = []
      for thread in list(self._worker_threads):
          thread.join(timeout=timeout)
          if thread.is_alive():
              alive.append(thread.name)
              remaining.append(thread)
          else:
              joined.append(thread.name)
      self._worker_threads = remaining
      return WorkerDrainResult(
          joined_thread_names=tuple(joined),
          alive_thread_names=tuple(alive),
      )
  ```

  The method must not call `signal_internal_abort()`, `decide()`, or registry internals. Tests that park a worker must first resolve or abort the protocol, then drain.

- [ ] **Step 4: Migrate process-wide thread cleanup sites**

  Replace direct `threading.enumerate()` cleanup for delegation workers with:

  ```python
  controller._registry.signal_internal_abort("99", reason="test_teardown_drain")
  drain = controller.drain_workers(timeout=5.0)
  assert drain.alive_thread_names == ()
  ```

  Use a real `decide()` instead of `signal_internal_abort()` where the test is already asserting the operator-resolution path.

- [ ] **Step 5: Verify Phase 1**

  Run:

  ```bash
  uv run pytest tests/test_bootstrap.py tests/test_delegation_controller.py tests/test_delegate_start_integration.py tests/test_delegate_start_async_integration.py -q
  uv run ruff check scripts/codex_runtime_bootstrap.py server/delegation_controller.py tests/test_bootstrap.py tests/test_delegation_controller.py tests/test_delegate_start_integration.py tests/test_delegate_start_async_integration.py
  uv run pytest tests -q -m ""
  uv run ruff check .
  git diff --check
  ```

  Expected: selected tests pass, full marker-inclusive pytest passes, full ruff passes, and QW1 and QW2 are ready for a focused PR. If QW2 changed files outside the listed set, stop and split before opening the PR.

---

## Phase 2: HL2 Crash/Restart Audit Events

**Row:** `DEBT-20260517-HL2-CRASH-RESTART-AUDIT`

**Branch:** `chore/debt-20260517-crash-restart-audit`

**Purpose:** Turn reserved `crash` / `restart` audit actions into contract-valid emitted events without inventing an ad hoc dict shape or double-emitting during lazy recovery.

### Task 2.1: Write The Mini-Design Decision

**Files:**
- Create `docs/specs/design-docs/2026-05-17-crash-restart-audit-events.md`
- Modify `docs/specs/contracts.md`
- Modify `docs/specs/recovery-and-journal.md`

- [ ] **Step 1: Document the exact event locus**

  The design doc must decide, in prose and a small table:
  - whether `crash` is process-level, controller-level, runtime-level, or job/turn-level
  - whether `restart` means process startup, controller recovery execution, or actual reconciliation of unresolved records
  - which code path owns each event
  - which concrete `crash` trigger is implemented in this phase and which test proves normal shutdown does not emit a false `crash`

  Required default unless the design rejects it with evidence:

  ```text
  restart is emitted only after a recovery path actually reconciles unresolved state.
  No restart event is emitted for a clean startup with no recovered work.
  crash is emitted only where a real runtime/job/turn identity is available, or the schema/sentinel decision explicitly supports process-level records.
  Recovery-time crash detection is valid only when the event records detected_during="startup_recovery"; it must not pretend to know the original crash timestamp.
  ```

  If the design leaves all crash emission out of scope, immediately create or name a residual row for crash emission and do not close `DEBT-20260517-HL2-CRASH-RESTART-AUDIT` in this phase.

- [ ] **Step 2: Decide identity shape**

  The design must choose exactly one:
  - use existing `AuditEvent` fields with documented sentinel `collaboration_id` / `runtime_id` values for process-level events
  - extend `AuditEvent` and the contract to support process-level audit events without sentinel IDs
  - limit this phase to controller/job-level crash/restart events with real IDs and explicitly leave process-level best-effort crash emission out of scope

  Stop for review if the design chooses an `AuditEvent` schema change.

- [ ] **Step 3: Decide idempotency and duplicate-prevention**

  The design must name the idempotency key for restart emission across:
  - eager `McpServer.startup()`
  - lazy `_ensure_dialogue_controller()`
  - lazy `_ensure_delegation_controller()`
  - retry after failed lazy recovery

  Required invariant: the same unresolved recovery item cannot produce duplicate `restart` events in one process.

  Required default unless the design rejects it with evidence:

  ```text
  Recovery owners emit audit events only after the local reconciliation writes for
  one recovery item succeed. The audit idempotency key is:

      f"{entry.operation}:{entry.idempotency_key}:{action}"

  where action is "crash" or "restart".
  ```

  Implement duplicate prevention in `OperationJournal` with a narrow helper such as:

  ```python
  def append_recovery_audit_event_once(
      self,
      event: AuditEvent,
      *,
      recovery_key: str,
  ) -> bool:
      """Append a recovery audit event unless action + recovery_key already exists."""
  ```

  The helper must dedupe against both in-memory state and existing `audit/events.jsonl` records by `event.action` plus `event.extra["recovery_key"]`. It returns `True` when it appends and `False` when it suppresses a duplicate. Controllers must not implement their own independent duplicate sets.

- [ ] **Step 4: Patch specs before source**

  Update `docs/specs/contracts.md` and `docs/specs/recovery-and-journal.md` so the emitted event shape is normative before implementation starts. If recovery events use `extra`, document the exact keys:

  ```text
  recovery_key: action-specific idempotency key for duplicate suppression
  recovery_operation: operation journal operation that was reconciled
  recovery_phase: latest unresolved phase seen before reconciliation
  detected_during: "startup_recovery" for crash records inferred during recovery
  ```

### Task 2.2: Implement Contract-Valid Emission

**Files:**
- Modify `server/journal.py`
- Modify `server/mcp_server.py`
- Modify controller recovery files named by the design
- Test `tests/test_journal.py`
- Test `tests/test_mcp_server.py`
- Test controller-specific recovery tests

- [ ] **Step 1: Add failing tests**

  Add tests proving:
  - emitted events are `AuditEvent(action="crash")` or `AuditEvent(action="restart")`, not dicts with `type`
  - the chosen concrete crash trigger emits `action="crash"` with a real `collaboration_id` and `runtime_id`, or the phase explicitly creates a residual row and keeps HL2 open
  - normal shutdown / clean startup does not emit a false `crash`
  - normal startup with no unresolved recovery does not emit `restart`
  - recovery that runs through eager and lazy call paths does not duplicate `restart`
  - recovery failure does not mark the controller pinned and does not emit a false successful `restart`
  - `OperationJournal.append_recovery_audit_event_once(...)` suppresses duplicate action + recovery-key pairs but allows distinct recovery keys

  Run:

  ```bash
  uv run pytest tests/test_journal.py tests/test_mcp_server.py -q
  ```

  Expected before implementation: new tests fail because no crash/restart events are emitted.

- [ ] **Step 2: Implement event helpers**

  Prefer small helpers near the recovery owner rather than broad framework code. Any helper that appends an audit event must construct:

  ```python
  recovery_key = f"{entry.operation}:{entry.idempotency_key}:restart"
  AuditEvent(
      event_id=self._uuid_factory(),
      timestamp=self._journal.timestamp(),
      actor="system",
      action="restart",
      collaboration_id=collaboration_id,
      runtime_id=runtime_id,
      job_id=job_id,
      extra={
          "recovery_key": recovery_key,
          "recovery_operation": entry.operation,
          "recovery_phase": entry.phase,
      },
  )
  ```

  Use `journal.append_recovery_audit_event_once(event, recovery_key=recovery_key)`. Do not append raw dictionaries. Do not use `journal.append_audit_event(event)` directly for recovery crash/restart events unless the design proves another dedupe owner.

- [ ] **Step 3: Wire lazy recovery carefully**

  Preserve the existing `McpServer` ordering:
  - eager controllers recover in `startup()`
  - factory-created controllers recover in `_ensure_*_controller()`
  - controllers pin only after recovery succeeds

  If the design needs process-level coordination state, keep it on `McpServer`; do not scatter duplicate-prevention flags across unrelated controllers. The default is journal-owned duplicate suppression via `append_recovery_audit_event_once(...)`; if the design chooses a different owner, update this task before implementation.

- [ ] **Step 4: Verify Phase 2**

  Run:

  ```bash
  uv run pytest tests/test_journal.py tests/test_mcp_server.py tests/test_dialogue.py tests/test_delegation_controller.py -q
  uv run ruff check server/journal.py server/mcp_server.py server/dialogue.py server/delegation_controller.py tests/test_journal.py tests/test_mcp_server.py tests/test_dialogue.py tests/test_delegation_controller.py
  uv run pytest tests -q -m ""
  uv run ruff check .
  git diff --check
  ```

  Expected: selected tests pass, full marker-inclusive pytest passes, full ruff passes, specs and source agree on the event shape, a concrete crash path and a concrete restart path are both covered or explicitly split, and the register row is not closed unless both implemented surfaces match the design.

---

## Phase 3: QW3 Hygiene Sweep

**Row:** `DEBT-20260517-QW3-HYGIENE`

**Branch:** `chore/debt-20260517-hygiene`

**Purpose:** Resolve the QW3 cluster item-by-item. Do not close QW3 as one blob unless every subitem below is closed, split, or declined with evidence.

### Task 3.1: Resolve Each QW3 Subitem

**Files:**
- Modify `README.md`, `AGENTS.md`, `.claude/CLAUDE.md`
- Modify `docs/specs/delivery.md`
- Modify `.github/workflows/ci.yml`
- Create `.github/dependabot.yml`
- Modify `server/delegation_controller.py`
- Modify `server/jsonrpc_client.py`
- Potentially modify `pyproject.toml`, `.claude-plugin/plugin.json`, `server/runtime.py`

- [ ] **Step 1: Replace exact live-doc test counts with approximate wording**

  Replace stale exact claims such as `1172 tests` in current-facing docs with `~1.2k tests`. Do not rewrite frozen audit snapshots or archived handoffs.

  Verify:

  ```bash
  rg -n "1172 tests|1199 tests|1184" README.md AGENTS.md .claude/CLAUDE.md docs/status docs/specs
  ```

  Expected after edit: no current-facing doc uses stale exact counts unless the line is intentionally a point-in-time evidence record.

- [ ] **Step 2: Add missing delivery component entries**

  In `docs/specs/delivery.md` component tree, add:

  ```text
  │   ├── tool_prefix.py
  │   ├── turn_extraction.py
  ```

  Place them under `server/` in alphabetical position. If the nearby prose names component roles, add one-line roles:
  - `tool_prefix.py`: canonical MCP tool-prefix constant used by hooks, skills, and credential-scan safety checks
  - `turn_extraction.py`: shared agent-message extraction helper used by dialogue and runtime paths

- [ ] **Step 3: Add vulnerability scanning to CI**

  Add a CI step after dependency sync and before tests:

  ```yaml
      - name: Audit Python dependencies
        run: uv run --with pip-audit pip-audit
  ```

  Create `.github/dependabot.yml`:

  ```yaml
  version: 2
  updates:
    - package-ecosystem: "uv"
      directory: "/"
      schedule:
        interval: "weekly"
  ```

  This repo is uv-managed and CI consumes `uv.lock` through `uv sync`; use the
  `uv` ecosystem so dependency update coverage follows the lockfile-backed
  graph. If GitHub Actions updates are desired, add a separate
  `package-ecosystem: "github-actions"` entry rather than treating it as part
  of the Python dependency row.

- [ ] **Step 4: Promote `_CANCEL_CAPABLE_KINDS` to module scope**

  In `server/delegation_controller.py`, add beside `_ESCALATABLE_REQUEST_KINDS`:

  ```python
  _CANCEL_CAPABLE_KINDS: frozenset[str] = frozenset({"command_approval", "file_change"})
  ```

  Delete the duplicated method-local constants and keep existing references pointed to the module-level constant.

- [ ] **Step 5: Keep plugin-data-path logging/docs aligned with Phase 1**

  If Phase 1 landed, confirm README has both:
  - `CODEX_COLLAB_LOG_LEVEL`
  - a note that `CLAUDE_PLUGIN_DATA` defaults to `/tmp/codex-collaboration` when unset

  If Phase 1 did not land, add only the `CLAUDE_PLUGIN_DATA` default note here and leave logging to QW1.

- [ ] **Step 6: Disposition version-surface alignment**

  Choose one path and record it in the PR body:
  - Align `pyproject.toml`, `.claude-plugin/plugin.json`, and `server/runtime.py` to the same public version if the intended version is already decided.
  - Split the version-surface item to `T-20260516-01` if the target version is part of the Codex App Server upgrade decision.

  Do not update only package metadata while leaving `server/runtime.py` stale.

- [ ] **Step 7: Document stderr backlog truncation**

  Add a succinct comment near `server/jsonrpc_client.py`'s `deque(maxlen=200)`:

  ```python
  # Keep only recent stderr lines for failure context; long-running sessions may
  # truncate earlier diagnostics before an eventual request failure is reported.
  self._stderr_lines: deque[str] = deque(maxlen=200)
  ```

- [ ] **Step 8: Verify Phase 3**

  Run:

  ```bash
  uv run pytest tests/test_projection_helpers.py tests/test_codex_guard.py -q
  uv run ruff check .
  uv run python -c 'import pathlib, yaml; yaml.safe_load(pathlib.Path(".github/dependabot.yml").read_text())'
  uv run pytest tests -q -m ""
  git diff --check
  ```

  Expected: selected tests pass, full marker-inclusive pytest passes, full ruff passes, Dependabot YAML parses, and the PR body itemizes every QW3 subitem as closed, split, or declined.

---

## Phase 4: HL4 Delegation Test Seams

**Row:** `DEBT-20260517-HL4-DELEGATION-TEST-SEAMS`

**Branch:** `chore/debt-20260517-delegation-test-seams`

**Prerequisite:** Phase 1 QW2 worker-drain seam has landed on `main`.

**Purpose:** Add supported observation and behavior/protocol seams so representative delegation tests stop monkeypatching private controller and registry internals.

### Task 4.1: Add Observation And Behavior Seams

**Files:**
- Modify `server/delegation_controller.py`
- Test `tests/test_delegation_controller.py`
- Test `tests/test_delegate_start_async_integration.py`
- Test `tests/test_delegate_decide_async_integration.py`
- Test `tests/test_projection_helpers.py`
- Optionally add `tests/test_delegation_controller_test_seams.py`

- [ ] **Step 1: Inventory private coupling**

  Run:

  ```bash
  rg -n "object\\.__setattr__|controller\\._registry|controller\\._project_pending_escalation|commit_signal|threading\\.enumerate" tests/test_delegation_controller.py tests/test_delegate_start_async_integration.py tests/test_delegate_decide_async_integration.py tests/test_projection_helpers.py
  ```

  Expected: the output defines the migration checklist. Do not claim HL4 closure by reducing only one class of hits.

- [ ] **Step 2: Add an observation seam**

  Add a frozen test snapshot dataclass in `server/delegation_controller.py`:

  ```python
  @dataclass(frozen=True)
  class DelegationControllerTestSnapshot:
      session_id: str
      tracked_worker_names: tuple[str, ...]
      alive_worker_names: tuple[str, ...]
  ```

  Add:

  ```python
  def _snapshot_for_test(self) -> DelegationControllerTestSnapshot:
      return DelegationControllerTestSnapshot(
          session_id=self._session_id,
          tracked_worker_names=tuple(thread.name for thread in self._worker_threads),
          alive_worker_names=tuple(
              thread.name for thread in self._worker_threads if thread.is_alive()
          ),
      )
  ```

  Keep this seam read-only. It must not expose stores, mutable registries, or worktree managers.

- [ ] **Step 3: Add behavior/protocol injection seams**

  Add constructor parameters with production defaults:

  ```python
  resolution_registry: ResolutionRegistry | None = None,
  pending_escalation_projector: Callable[[DelegationJob], PendingEscalationView | None] | None = None,
  ```

  In `__init__`:

  ```python
  self._registry = resolution_registry or ResolutionRegistry()
  self._pending_escalation_projector = pending_escalation_projector
  ```

  At the top of `_project_pending_escalation`, delegate when a projector is provided:

  ```python
  if self._pending_escalation_projector is not None:
      return self._pending_escalation_projector(job)
  ```

  This supports projection-null, projection-raises, registry abort, reservation contention, and commit-ordering tests without mutating private attributes after construction.

- [ ] **Step 4: Migrate representative tests**

  Migrate at least these tests:
  - one observation-coupled worker/state test in `tests/test_delegation_controller.py` to call `_snapshot_for_test()` instead of reading `controller._worker_threads` or process-wide `threading.enumerate()`
  - `tests/test_delegate_start_async_integration.py` projection-null path
  - `tests/test_delegate_start_async_integration.py` projection-raises path
  - `tests/test_delegate_decide_async_integration.py::test_decide_writes_intent_before_commit_signal_ordering`

  New test construction should pass fakes through constructor parameters instead of using `object.__setattr__` or assigning to `controller._registry.commit_signal`.

  If Phase 1 left no existing observation-coupled test suitable for migration, add `tests/test_delegation_controller_test_seams.py::test_snapshot_for_test_reports_tracked_and_alive_worker_names`. That fallback is acceptable only if the PR body states that it adds observation coverage rather than migrating an existing observation assertion.

- [ ] **Step 5: Verify Phase 4**

  Run:

  ```bash
  uv run pytest tests/test_delegation_controller.py tests/test_delegate_start_async_integration.py tests/test_delegate_decide_async_integration.py tests/test_projection_helpers.py -q
  uv run ruff check server/delegation_controller.py tests/test_delegation_controller.py tests/test_delegate_start_async_integration.py tests/test_delegate_decide_async_integration.py tests/test_projection_helpers.py
  uv run pytest tests -q -m ""
  uv run ruff check .
  git diff --check
  ```

  Expected: selected tests pass, full marker-inclusive pytest passes, full ruff passes, at least one observation-coupled test and one behavior/protocol-coupled test now use supported seams.

---

## Register Closeout

Before each phase PR is ready for review, update `docs/status/reconciliation-register.md` in the same branch when a row is closed, split, or re-routed. Also update `docs/status/current-state.md` when the current-state watchpoint text changes. If a phase intentionally leaves status docs unchanged, state the reason in the PR body.

- Close `DEBT-20260517-QW1-LOGGING` only after README documents the env var and bootstrap tests prove logging configuration.
- Close `DEBT-20260517-QW2-DRAIN-WORKERS` only after tests use `drain_workers()` instead of process-wide worker enumeration for migrated teardown paths.
- Close `DEBT-20260517-HL2-CRASH-RESTART-AUDIT` only after the mini-design, specs, source, and tests agree on emitted event shape, duplicate-prevention behavior, a concrete crash path, and a concrete restart path. If crash emission is split out, keep this row open or re-route it by name.
- Close `DEBT-20260517-QW3-HYGIENE` only after every QW3 bullet is closed, split, or declined by name.
- Close `DEBT-20260517-HL4-DELEGATION-TEST-SEAMS` only after both observation and behavior/protocol seams exist and representative tests migrate to them. At least one observation-coupled test and one behavior/protocol-coupled test must use supported seams.

## Self-Review Notes

- Spec coverage: every active May 17 register row has exactly one phase. HL1 and HL3 are deliberately excluded because the register routes them to tickets/deferred watch.
- Placeholder scan: no task uses deferred filler; unresolved Phase 2 design choices are explicit stop-gated decisions, not implementation blanks.
- Type consistency: `WorkerDrainResult`, `DelegationControllerTestSnapshot`, and constructor seam names are defined before use in later steps.
