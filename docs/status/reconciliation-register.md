# Codex-Collaboration Reconciliation Register

Use this file for open or unreconciled work.

Start at [Current State](./current-state.md) for project orientation,
implemented-now surface, authority ownership, and reader routing.

Last reconciled: 2026-05-17

## Authority

This register is the working index of still-open, still-deferred, or
still-unreconciled `codex-collaboration` work in this repo.

Authority boundary:

- This file summarizes current-state classification, priority, and next-action
  labeling for work that already has source evidence elsewhere in the repo.
- This file is **not** the canonical long-form current-state synthesis. It is the
  bounded index of open, deferred, or still-unreconciled work.
- Linked tickets, plans, diagnostics, and specs remain authoritative for
  acceptance criteria, evidence, and behavioral design.
- If a linked artifact's status language drifts from newer repo evidence, this
  register may record that drift only when the row makes the newer source of
  truth explicit. If the register and source artifacts disagree without that
  evidence trail, treat the row as needing reconciliation rather than as a
  tie-breaker.

Scope included here:

- Open ticket-owned work
- Residual carry-forward debt
- Benchmark closeout follow-on work that remains intentionally unresolved
- Spec and documentation reconciliation debt
- Intentional future-scope deferrals that are still active design surfaces
- Recent closeout rows when they explain why a formerly active blocker left
  the active list
- Active supporting artifacts whose open/closed design state no longer matches
  current decisions

## State Vocabulary

| State | Meaning |
|---|---|
| `blocking` | Blocks the next important operational gate |
| `open` | Real work item remains unresolved |
| `drift` | The underlying implementation or closure state changed, but the owning artifact still says the old thing |
| `missing-artifact` | Work exists conceptually, but the durable tracker is missing |
| `deferred` | Intentionally out of the current slice, but still a live future-scope surface |
| `closed` | Resolved; retained briefly as closeout evidence because it was recently a priority item |

## Current Priority Order

1. Close `T-20260429-01` by recording closure evidence for the three
   unchecked acceptance criteria: comparable `/delegate` smoke with
   avoidable sandbox-friction escalations <=2 (AC #1); credential-boundary
   probe (AC #2); `test_runtime.py` regression assertion updated and full
   codex-collaboration test suite passing (AC #3). Phase 1 implementation
   has landed on `main` (`runtime.py:111-114`). Count legitimate
   operator-gated approvals separately.
2. Execute or explicitly defer `T-20260516-01`, the Codex App Server
   version-pin upgrade. HL1 payload-shape contract tests are now landed, so
   the next decision is target version plus live-smoke evidence.
3. Decide `T-20260516-02`, the Codex App Server contract-version assertion
   boundary. QW4 remains a startup preflight stopgap, not ST3 closure.
4. Continue the active 2026-05-17 debt-audit backlog rows in this order unless
   a narrower PR explicitly reorders with evidence:
   `DEBT-20260517-QW3-HYGIENE` and
   `DEBT-20260517-HL4-DELEGATION-TEST-SEAMS`. Phase 1 closed
   `DEBT-20260517-QW1-LOGGING` and `DEBT-20260517-QW2-DRAIN-WORKERS`; HL2
   crash/restart audit emission closed with HL2 Task 2.2; HL1 remains
   ticket-owned by `T-20260516-01` / `T-20260516-02`; HL3 remains mapped to
   deferred `WL6-CONCURRENT-PROMOTION-LOCK`.
5. Classify or intentionally safe-terminalize the currently unsupported App
   Server request kinds tracked by `T-20260429-02`.
6. Sweep residual typing and minor Packet 1 carry-forward debt (`TT.1`,
   `RT.1`, `P1-MINOR-SWEEP`).
7. Convert `BMARK-L1-L3` into explicit follow-up tickets or deliberately
   decline those L1/L2/L3 items as non-goals.
8. Specify or explicitly defer `AUDIT-CONSUMER-INTERFACE`.

## Audit-Owned Active Work

The 2026-05-17 debt audit is an active backlog source. Rows below are the
canonical active routing for audit-owned work that is not already ticket-owned.
For ticket-owned findings, keep the ticket row canonical and reference the audit
there instead of creating a duplicate active owner.

Publication boundary: these rows, the corresponding
`docs/audits/2026-05-17-codex-collaboration-debt.md` update, and the
`docs/status/current-state.md` watchpoint must publish as one change. Without
that atomic publication, the audit's register-backed routing claim is not yet
project truth.

| ID | State | Owning artifact | Current truth | Exit condition |
|---|---|---|---|---|
| `DEBT-20260517-QW3-HYGIENE` | `open` | `docs/audits/2026-05-17-codex-collaboration-debt.md` QW3 | The audit bundles small doc/config hygiene items: stale exact test counts, missing `delivery.md` component entries, vulnerability-scanner CI shape, `_CANCEL_CAPABLE_KINDS` duplication, plugin-data-path logging/doc note, version-surface alignment across `pyproject.toml`, `.claude-plugin/plugin.json`, and `server/runtime.py`, and `deque(maxlen=200)` truncation documentation. | Resolve, split, or deliberately decline each subitem individually. If the version-surface item is handled with `T-20260516-01`, record that handoff instead of claiming QW3 closure independently. |
| `DEBT-20260517-HL4-DELEGATION-TEST-SEAMS` | `open` | `docs/audits/2026-05-17-codex-collaboration-debt.md` HL4 | Delegation tests still couple to private state, behavior injection, registry calls, and commit ordering. A snapshot-only seam is insufficient; observation and behavior/protocol seams must be handled separately. | Add supported observation and behavior/protocol seams, then migrate representative tests away from private monkeypatching/registry spies without counting a read-only snapshot alone as closure. |

## Recently Closed Audit Work

| ID | State | Owning artifact | Closeout evidence | Residual owner |
|---|---|---|---|---|
| `DEBT-20260517-HL2-CRASH-RESTART-AUDIT` | `closed` | `docs/audits/2026-05-17-codex-collaboration-debt.md` HL2, `docs/specs/design-docs/2026-05-17-crash-restart-audit-events.md`, and `docs/superpowers/plans/2026-05-17-phase2-task-2.2-crash-restart-audit-emission.md` | HL2 Task 2.2 landed recovery audit emission for all three subjects: `lineage_handle` (crash+restart on genuine reattach, crash-only on quarantine, including `turn_dispatch` two-phase and between-turn cases), `orphaned_active_job` (crash only), and `operation_journal` (residual-proof `job_creation`/`approval_resolution:dispatched` plus recovery-mutation `promotion`, with no-op intent/guard paths emitting nothing). Persisted `(action, recovery_key)` dedup is journal-owned and keys `lineage_handle` on stable `collaboration_id`, preventing eager/lazy retry double-emission without an `McpServer` flag. Close gates: `uv run pytest tests -q -m ""` -> 1241 passed; `uv run ruff check .` passed; `git diff --check` passed. | None. |
| `DEBT-20260515` | `closed` | `docs/audits/2026-05-15-codex-collaboration-debt.md` and `docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md` | PR #4 published the audit (`cd205e5`); PR #5 published the plan (`d9a76ed`); PRs #6-#9 landed the four execution phases (`32792af`, `b823386`, `a649b9d`, `b34a39b`). Main CI passed after every merge. Phase 4 close gates included `uv run pytest tests -q -m ""` -> 1199 passed, `uv run pytest tests/test_codex_wire_contract.py -q -rA` -> 6 passed with no skips, and `uv run ruff check .` passing. | Active residuals are `T-20260516-01` (ST2 upgrade) and `T-20260516-02` (ST3 contract-version decision). Intentional deferrals are `HL2-XDIST-PARALLELIZATION`, `HL4a-LINEAGE-CACHE`, `ST1-KNOWLEDGE-TRANSFER`, `WL1-MODELS-MEGAHUB`, `WL2-ANY-TYPED-CONTROLLERS`, `WL3-LAYERING-CI-ASSERT`, `WL4-UNBOUNDED-AUDIT-LOG`, `WL5-MODELS-HOLDS-SESSION`, and `WL6-CONCURRENT-PROMOTION-LOCK`. |
| `DEBT-20260517-QW1-LOGGING` | `closed` | `docs/audits/2026-05-17-codex-collaboration-debt.md` QW1 and `docs/superpowers/plans/2026-05-17-codex-collaboration-debt-active-rows.md` Phase 1 | Phase 1 added bootstrap root logging configuration, `CODEX_COLLAB_LOG_LEVEL`, startup INFO logging for the resolved plugin data path, and README configuration documentation. Close gates: `uv run pytest tests/test_bootstrap.py tests/test_delegation_controller.py tests/test_delegate_start_integration.py tests/test_delegate_start_async_integration.py -q` -> 170 passed; `uv run pytest tests -q -m ""` -> 1204 passed; `uv run ruff check .` passed; `git diff --check` passed. | None. |
| `DEBT-20260517-QW2-DRAIN-WORKERS` | `closed` | `docs/audits/2026-05-17-codex-collaboration-debt.md` QW2 and `docs/superpowers/plans/2026-05-17-codex-collaboration-debt-active-rows.md` Phase 1 | Phase 1 added controller-owned worker thread tracking plus `drain_workers()`, migrated delegation worker cleanup off process-wide thread enumeration, and drove re-escalation cleanup through protocol-level `decide()` before drain. Close gates: `uv run pytest tests/test_bootstrap.py tests/test_delegation_controller.py tests/test_delegate_start_integration.py tests/test_delegate_start_async_integration.py -q` -> 170 passed; `uv run pytest tests -q -m ""` -> 1204 passed; `uv run ruff check .` passed; `git diff --check` passed. | None. |

## Audit-Owned Deferred Watch Rows

| ID | State | Owning artifact | Current truth | Watch trigger |
|---|---|---|---|---|
| `WL3-LAYERING-CI-ASSERT` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | The scripts->server layering invariant is now documented in `foundations.md` (QW8/Task 2). The optional CI guard (`rg "from scripts\." server/` -> fail on match) is not yet wired. | At next contributor onboarding, or when a reverse import is first attempted, add the CI assertion. |
| `HL2-XDIST-PARALLELIZATION` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | HL2's fast/slow split + approval-window injection landed (Task 7); the suite's whole-wall-time parallelization via pytest-xdist is not yet done. The HL2-first premise (cheap to add HL1/HL5) still holds because the timeout-path injection is the load-bearing part. | If full-suite wall time after the slow/fast split is still a friction point in routine work, add `pytest-xdist` and a `-n auto` CI/local profile. |
| `HL4a-LINEAGE-CACHE` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | TurnStore replay cache landed (Task 12, single-instance-per-session, safe). The LineageStore replay cache is deferred because LineageStore is constructed twice per session over one shared JSONL — a per-instance cache returns stale handles. | If lineage replay is shown to dominate a real dispatch path, implement Option A (mtime/size invalidation) or Option B (one shared per-session LineageStore instance). |
| `WL6-CONCURRENT-PROMOTION-LOCK` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md`; reaffirmed by `docs/audits/2026-05-17-codex-collaboration-debt.md` HL3 | The startup-overlap warning is only an operator-awareness patch. The actual cross-process promotion race remains open by design at solo single-session scale. | Promote to an implementation ticket if broad marketplace distribution is actively pursued or routine multi-session use begins. |
| `ST1-KNOWLEDGE-TRANSFER` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | Bus factor remains one by construction. No handoff trigger is currently active. | If onboarding, transition, or more than one-quarter unavailability becomes real, create module notes for `delegation_controller.py`, `journal.py`, and `control_plane.py`, preferably after HL3 has landed. |
| `WL1-MODELS-MEGAHUB` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | `models.py` is a flat-domain hub (15/28 importers). Clean today; compounds as capabilities are added. | When `models.py` > ~800 LOC **or** a 2nd capability domain is added → split into advisory/execution/infrastructure modules with a re-export shim. |
| `WL2-ANY-TYPED-CONTROLLERS` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | Controllers are `Any`-typed at the MCP boundary (no protocol seam); mitigated only because integration tests use the real controller types. | If integration tests shift to test doubles for speed/isolation → promote to P2 and add `_interfaces.py` protocols. |
| `WL4-UNBOUNDED-AUDIT-LOG` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | Intra-session audit/outcomes log is pruned only at startup. Documented v1 limitation; theoretical at solo scale. | If session duration regularly > 4h **or** `audit/events.jsonl` > 10 MB → implement periodic pruning. |
| `WL5-MODELS-HOLDS-SESSION` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | `models.py` holds a live `AppServerRuntimeSession` via `TYPE_CHECKING`. No runtime cost; conceptual layer oddity. | If `AdvisoryRuntimeState` ever needs JSON serialization or independent mocking → move the session field to a `control_plane.py` wrapper. |
| `DEBT-20260517-WL1-SECRET-TAXONOMY-TESTS` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL1 | Eight of fifteen secret-taxonomy families lack pattern-level tests. This is safety-class coverage debt but not current breakage. | Before editing `server/secret_taxonomy.py` or the next security ADR, add pattern-level tests for the missing families, starting with `credential_assignment_strong`. |
| `DEBT-20260517-WL2-GIT-APPLY-CRASH-TEST` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL2 | Crash-during-`git apply` promotion recovery is asserted by reasoning more than direct test coverage. | When `WL6-CONCURRENT-PROMOTION-LOCK` is promoted, or when promotion recovery is otherwise touched, add unit coverage for partial apply failure and journal recovery handling. |
| `DEBT-20260517-WL3-DISPATCH-CAPABILITY-GUARD` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL3 | Startup compatibility probing exists, but production dispatch does not gate each call through `has_capability()`. This may be an accepted v1 boundary rather than a bug. | If Codex CLI is upgraded past `TESTED_CODEX_VERSION`, decide whether dispatch-time capability gating is required or record the startup-only boundary in `T-20260516-02`. |
| `DEBT-20260517-WL4-TOOL-PREFIX-DRIFT-GUARD` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL4 | MCP tool-prefix rename coupling has no drift guard or checklist. | Before any plugin/MCP-server rename, add a guard/checklist covering hooks, skills, agents, and server tool names. |
| `DEBT-20260517-WL5-DELEGATION-CONTROLLER-SPLIT` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL5 | `delegation_controller.py` is large but cohesive; no current god-module finding is active. HL4 seams are a prerequisite for a lower-risk split. | If the file exceeds roughly 4000 LOC, a second author joins, or a major delegation refactor starts, plan the split after HL4 seams and fold the duplicated grouping helper cleanup into that work. |
| `DEBT-20260517-WL6-WORKTREE-ORPHANS` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL6 | Worktree orphan accumulation and suppressed `remove_worktree()` errors are disk/diagnosability debt, not a current containment breach. | If long-running sessions or disk pressure appear, add visible cleanup diagnostics and/or retention behavior for orphaned worktrees. |
| `DEBT-20260517-WL7-JOURNAL-RETENTION` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL7 | Session journal accumulation has no explicit retention policy/spec decision. | If many sessions accumulate over months, add a `recovery-and-journal.md` retention decision and matching implementation. |
| `DEBT-20260517-WL8-RECOVERY-RUNBOOK` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL8 | No operator runbook exists for hung or failed delegation jobs. | Before a second operator/handoff, publish a concise recovery runbook for stuck jobs, failed promotion, discard, and cleanup paths. |
| `DEBT-20260517-WL9-DOCS-SUPERPOWERS-RESIDUE` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL9 | `docs/superpowers/` remains extraction-era residue, but at least one register reference has been load-bearing historically. | On the next docs-layout pass, classify each remaining `docs/superpowers/` reference as durable project record, redirect, or removable residue before adding new cross-references. |
| `DEBT-20260517-WL10-ADR-PRACTICE` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL10 | ADR practice is sparse and partly retroactive. | Produce an ADR in-flight for the next significant architecture decision rather than backfilling after implementation. |
| `DEBT-20260517-WL11-INTEGRATION-MARKERS` | `deferred` | `docs/audits/2026-05-17-codex-collaboration-debt.md` WL11 | `slow` currently means live-binary tests more than general slow/integration behavior; there is no MCP-level E2E with real Codex. | When a faster inner-loop profile is needed, introduce an integration marker distinct from `slow` and consider a real-Codex MCP-level E2E. |

## Ticket-Owned Active Work

| ID | State | Owning artifact | Current truth | Exit condition |
|---|---|---|---|---|
| `T-20260516-02` | `open` | `docs/tickets/2026-05-16-codex-app-server-contract-versioning.md`; `docs/audits/2026-05-17-codex-collaboration-debt.md` HL1/WL3 | Codex App Server JSON-RPC currently has no explicit contract-version assertion. QW4's startup compatibility preflight is a stopgap, not ST3 closure. The May 17 audit routes the contract-version portion of HL1 and the dispatch-capability boundary question here. | Land a startup contract-version assertion design, or record why vendored schema plus live method probing is the v1 compatibility boundary. |
| `T-20260516-01` | `open` | `docs/tickets/2026-05-16-codex-app-server-version-upgrade.md`; `docs/audits/2026-05-17-codex-collaboration-debt.md` HL1 | Codex App Server version-pin upgrade is explicitly tracked. The May 17 audit confirms the CI/source-control invisibility problem: CI does not install or probe Codex, while runtime startup already performs live compatibility probing. Execution remains gated by payload-shape contract tests and live smoke evidence. | Target Codex version fixtures, diff, contract tests, live smoke, docs, version constants, and CI/source-control visibility are updated or the upgrade is explicitly deferred with evidence. |
| `T-20260429-01` | `open` | `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md` | T-01's closing live `/delegate` smoke required 24 operator escalations to produce a 1-line edit, surfacing three plugin friction sources: `~/.codex/` reads (Codex consulting its own memory + skill cache), worktree `.git` cross-pointer reads (in-worktree `rg`/`git` traversing the gitdir target outside the worktree), and opaque `file_change` escalation payloads. Phase 1 (Options B + E) is mechanical sandbox-policy carve-outs in `runtime.py`; Phase 2 Option F investigation is complete — `file_change` payload opacity is confirmed as an upstream schema limitation (`FileChangeRequestApprovalParams` carries only `grantRoot` and `reason`), `/delegate` SKILL.md rendering narrowed accordingly (D-06). `file_change` opacity is counted separately from avoidable sandbox friction. As of 2026-05-09, Phase 1 sandbox carve-outs (Options B + E + ~/.agents/ + dynamic gitdir) have landed on `main` (`server/runtime.py` — readable-roots append at lines 111-114, dynamic gitdir resolver at lines 27-72). Closure evidence remains missing for ticket acceptance criteria #1 (comparable `/delegate` smoke with avoidable sandbox-friction escalations ≤2), #2 (credential-boundary probe), and #3 (`test_runtime.py` regression assertion updated and full codex-collaboration test suite passing). Acceptance criterion #4 (Option F upstream limitation) is already checked. The ticket therefore remains open; the work shape changes from "implement" to "record closure evidence and close." | Record closure evidence for the three unchecked acceptance criteria: AC #1 — comparable `/delegate` smoke with avoidable sandbox-friction escalations <=2 (count legitimate operator-gated approvals separately); AC #2 — credential-boundary probe; AC #3 — `test_runtime.py` regression assertion updated and full codex-collaboration test suite passing. Phase 1 implementation has landed on `main` (`runtime.py:111-114`); AC #4 (Option F upstream limitation) is already checked. |
| `T-20260429-02` | `open` | `docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md` | The current delegation runtime parks only three server-request kinds (`command_approval`, `file_change`, `request_user_input`). Other App Server request methods that the current parser cannot fully support can still create minimal `unknown` records and terminalize jobs as `unknown`. The open work is to classify each unsupported method by reachability and then provide one of: supported handling, a regression test proving intentional safe terminal behavior, or a documented non-reachability proof. | Classify each unsupported `ServerRequest` method and land either support, regression coverage for intentional safe terminal behavior, or a recorded non-reachability proof for current advisory/delegation flows. |

## Residual Carry-Forward Debt

| ID | State | Owning artifact | Current truth | Exit condition |
|---|---|---|---|---|
| `TT.1` | `open` | `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` | Pre-existing Pyright issues around `_FakeControlPlane` typing remain open after Packet 1 closeout. | Resolve the test-fake typing mismatches or explicitly accept them in a narrower typing policy. |
| `RT.1` | `open` | `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` | Pre-existing Pyright `TurnStatus` literal narrowing issue in `runtime.py` remains open after Packet 1 closeout. | Fix the narrowing issue or explicitly document a durable rationale for leaving it unresolved. |
| `P1-MINOR-SWEEP` | `open` | `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` | Fourteen non-blocking carry-forward items remain open: `A4`, `A5`, `B6.1`, `B6.2`, `B7.1`, `B7.2`, `B8.1`, `B8.2`, `C10.2`, `C10.3`, `E13.1`, `E13.2`, `E13.3`, `E14.1`. These are test-parity, style, docstring, and declarative-cleanup items rather than correctness blockers. | Sweep or disposition the items individually in the carry-forward tracker. |

## Benchmark-Carried Follow-On Work

| ID | State | Owning artifact | Current truth | Exit condition |
|---|---|---|---|---|
| `BMARK-L1-L3` | `open` | `docs/tickets/closed-tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | The benchmark closeout preserved three candidate mechanism losses as future work rather than closure blockers: `L1` scout integrity, `L2` plateau / budget control, and `L3` per-scout redaction of raw host-tool output. These are not yet decomposed into standalone backlog artifacts. | Convert the three caveats into explicit follow-up tickets / packets, or explicitly decline them as non-goals. |

## Open Spec Questions

| ID | State | Owning artifact | Current truth | Exit condition |
|---|---|---|---|---|
| `AUDIT-CONSUMER-INTERFACE` | `open` | `docs/specs/decisions.md` | The audit record shape and write behavior are specified, but the query / aggregation / export interface for consuming audit records is still not specified. | Specify the consumer interface or deliberately defer it behind a narrower rollout boundary. |

## Intentional Future-Scope Deferrals

| ID | State | Owning artifact | Current truth | Exit condition |
|---|---|---|---|---|
| `DIALOGUE-FORK` | `deferred` | `docs/specs/decisions.md` and `docs/specs/contracts.md` | Dialogue branchability is preserved as an architectural property, but the intended surface is `seed_from` on `codex.dialogue.start` (copy-and-diverge via current-head `thread/fork`), not a standalone `codex.dialogue.fork` tool. Tree-structured dialogue and prefix seeding are explicitly deferred. See [decisions.md §Dialogue Fork Scope](../specs/decisions.md#dialogue-fork-scope). | A concrete seeded-dialogue use case justifies implementation. Constraints: admissibility, fresh control resolution, dialogue-thread `thread/fork` verification, and D-07 ordering dependency. |
| `MCP-STRUCTURED-ERROR-REASON` | `deferred` | `docs/specs/contracts.md` | MCP clients still rely on text-prefix recoverability for certain delegation errors because a structured wire-level `reason` field is explicitly deferred to a future packet. | Define and land the structured wire field in a follow-up packet. |
| `ADVISORY-WIDENING-ROTATION` | `deferred` | `docs/specs/advisory-runtime-policy.md` plus `server/control_plane.py` and `server/profiles.py` | Advisory widening, narrowing, freeze-and-rotate, and reap behavior are specified as future-scope design, clearly separated from current Packet 1 fixed-posture behavior. The spec text (`advisory-runtime-policy.md`) has been restructured into current behavior and future-scope sections (D-03). The current implementation rejects widened advisory requests and rejects widened profile settings until rotate support exists. | Implement advisory widening/rotation with matching recovery and profile behavior. |
| `PHASED-CONSULTATION-PROFILES` | `deferred` | `references/consultation-profiles.yaml` plus `server/profiles.py` | The profile catalog includes phased profiles such as `debugging`, but the resolver currently rejects any profile with `phases` until phase-progression support exists. This is an intentional future-scope surface, not an accidental runtime bug. | Implement phase-progression support for phased profiles, or narrow the shipped profile catalog/documentation so only currently resolvable profiles are advertised. |

## Maintenance Rule

When a new unresolved item appears, add it here immediately if it crosses any
authority boundary:

- a closed ticket leaves real follow-on work behind
- a carry-forward tracker becomes the real home of still-open debt
- a linked ticket/spec/plan no longer matches the implemented state
- a newer diagnostic or closeout explicitly disproves an older planned
  follow-up or blocker model
- a future-scope surface is intentionally deferred but still matters to roadmap
  truth

This register should stay short enough to scan in one sitting. If a row grows
too detailed, move the detail into the owning artifact and keep only the
current-truth summary here.
