---
date: 2026-05-01
time: "00:29"
created_at: "2026-05-01T04:29:08Z"
session_id: 00a0ce9a-2ede-4217-a6db-404ebef2cc09
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-30_21-57_step-2-sandbox-carve-outs-implementation-and-review.md
project: claude-code-tool-dev
branch: fix/delegation-turn-start-probe
commit: 394868b5
title: Codex 0.128.0 sandbox migration — RCA, probe, plan, and scrutiny
type: handoff
files:
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/jsonrpc_client.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/server/worker_runner.py
  - packages/plugins/codex-collaboration/server/control_plane.py
  - packages/plugins/codex-collaboration/server/resolution_registry.py
  - packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/v2/TurnStartParams.json
  - .tmp/app-server-schema-pre-candidate-a/v2/TurnStartParams.json
  - docs/superpowers/specs/codex-collaboration/evidence/2026-04-29-codex-app-server-schema-0.117.0-to-0.125.0-comparison.json
  - .tmp/probe_turn_start.py
  - docs/plans/2026-05-01-codex-app-server-v128-execution-sandbox-migration-plan.md
---

# Handoff: Codex 0.128.0 sandbox migration — RCA, probe, plan, and scrutiny

## Goal

Merge PR #127 (Step 2 sandbox carve-outs), run the T-20260429-01 Phase 4 live `/delegate` smoke, and close the friction-reduction ticket. PR #127 was already review-clean after 2 review cycles in the prior session.

**Trigger:** PR #127 merged by the user between sessions. The first next step from the prior handoff was to merge, then run the live smoke and close out.

**Stakes:** The T-20260429-01 ticket targets reducing avoidable sandbox-friction escalations from ~11 to <=2 per delegation run. Without the smoke, the acceptance criteria remain unverified and the ticket can't close.

**What actually happened:** The live smoke was blocked by a Codex App Server protocol break. The session pivoted to root-cause analysis, produced a direct diagnostic probe confirming the break, and developed a scrutinized migration plan. The smoke itself never ran.

**Connection to project arc:** Eighth session in the codex-collaboration reconciliation sequence. Steps 0-1 complete + closed, Step 2 implementation complete (PR #127 merged), but Step 2 cannot close until the live smoke passes. The smoke is now blocked on a sandbox protocol migration.

## Session Narrative

Loaded the prior handoff (Step 2 sandbox carve-outs — implementation and review). PR #127 had been merged by the user. Confirmed the merge: `cd586e60` merge commit on `origin/main`, local `main` synced, feature branch deleted locally (remote branch `origin/feature/step-2-sandbox-carve-outs` still existed).

Checked Codex runtime health via `codex_status`: version `0.128.0`, authenticated, all methods available. The pre-smoke checks passed — `~/.agents/plugins` contained only `marketplace.json` (metadata, no credentials), and the plugin source confirmed PR #127 code was present (`_resolve_worktree_gitdir`, `~/.agents/skills`, `~/.agents/plugins` entries).

The user provided detailed operator guidance for the smoke: use a scratch diagnostic artifact instead of touching `runtime.py`, expand credential probes to four paths (the prior plan had only two), audit `~/.agents/plugins` before the smoke, confirm plugin host is running post-merge code, and use a structured classification table for escalation tracking.

First delegation attempt: `worker_failed_before_capture`. Discarded. Second attempt: same failure. Both jobs followed `queued` → `running` → `unknown` instantly with no turns registered, no escalations, and empty artifacts.

**Key pivot:** Shifted from "run the smoke" to "diagnose why delegation fails." Traced the failure through `worker_runner.py:70` → `delegation_controller.py:1401` → `runtime.py:317` (`turn/start` JSON-RPC call). The exception was logged to MCP server stderr via `logger.exception` at `worker_runner.py:71` but was invisible from the conversation context.

Investigated systematically:
- Sandbox policy: built it directly via Python — well-formed, 6 readableRoots, correct shape
- All readableRoots paths existed on disk
- Job store and lineage records showed no intermediate states between `running` and `unknown`
- Turn records directory had no entries from this session
- 18 accumulated git worktrees from prior delegations (noted but not causal)

**Key insight:** The user suggested looking at the App Server stderr. Without direct access, I built a diagnostic probe script at `.tmp/probe_turn_start.py` that reproduced the exact `turn/start` call sequence: `initialize` → `account/read` → `thread/start` → `turn/start`. Steps 1-3 succeeded; step 4 returned:

```
JSON-RPC error: {'code': -32600, 'message': 'Invalid request: workspaceWrite.readOnlyAccess is no longer supported; '}
```

**Root cause confirmed:** Codex App Server `0.128.0` rejects the `readOnlyAccess` field on `workspaceWrite` sandbox policies. This is a protocol break between `0.117.0` (where prior delegations worked) and `0.128.0`. PR #127 changed the contents of `readableRoots` but the rejection is of the containing field itself — the break predates PR #127.

After confirmation, the session shifted to planning the migration. The user and I iterated through three rounds of plan refinement:

1. **Initial migration direction:** User proposed a `build_execution_permission_profile` builder emitting a `managed` profile with `fileSystem.entries`. I identified that `FileSystemPath` is an object (`{"type": "path", "path": "/abs/path"}`), not a bare string — the user's pseudocode would have hit the next `-32600`.

2. **Probe-matrix-first approach:** User tightened the plan to require empirical probes before writing the builder. Seven probes covering: legacy advisory acceptance, managed profile shape, filesystem behavior, read/write semantics, CWD leakage, tmp boundaries, and credential/session boundaries.

3. **Scrutiny:** User wrote a plan document and I scrutinized it. Verdict: Minor revision. One critical finding (no contingency for advisory probe failure), one high finding (observability patch underspecified), and three high-risk assumptions. The plan survives with targeted fixes.

## Decisions

### Migrate to `permissionProfile` rather than patching `sandboxPolicy`

**Choice:** Build a new `build_execution_permission_profile()` function emitting a `managed` permission profile, rather than removing `readOnlyAccess` and staying on legacy `sandboxPolicy`.

**Driver:** The error message says `readOnlyAccess` "is no longer supported" — not deprecated, not warned, rejected. The App Server is enforcing the removal. Additionally, the pre-candidate-a schema shows `permissionProfile` was added as the replacement with the note "Cannot be combined with `sandboxPolicy`."

**Rejected alternatives:**
- **Remove `readOnlyAccess` and stay on `sandboxPolicy`** — Would remove the readable root grants entirely, silently widening reads to the default (likely full access). User: "The fix should not be 'remove readOnlyAccess and hope'; that would likely widen reads back toward the old default."
- **Use `sandboxPolicy` with a different field name** — No evidence of an alternative field on the `workspaceWrite` variant.

**Implication:** The `_run_turn` method needs to support sending either `sandboxPolicy` or `permissionProfile` (never both). Execution turns use `permissionProfile`; advisory turns stay on `sandboxPolicy` unless the advisory probe also fails.

**Trade-offs accepted:** The migration introduces a new payload shape that needs probe verification before it can be trusted. The builder design depends on empirical answers from the probe matrix (does `special:minimal` work, does `write` imply `read`, etc.).

**Confidence:** High (E2) — root cause confirmed by direct probe reproduction. Migration target confirmed by schema analysis showing `permissionProfile` as the replacement.

**Reversibility:** Medium — once migrated, reverting requires re-adding the old `sandboxPolicy` shape, which only works on `<0.128.0` servers.

**Change trigger:** If `0.128.0` also rejects `permissionProfile` (extremely unlikely given the schema), or if a `0.128.x` release re-accepts `readOnlyAccess`.

### Probe matrix before implementation

**Choice:** Run 7 empirical probes against the live `0.128.0` App Server before writing the profile builder.

**Driver:** The pre-candidate-a schema is from an unknown intermediate version, not necessarily `0.128.0`. Schema acceptance doesn't guarantee runtime acceptance. Several critical unknowns (platform defaults, write-implies-read, deny precedence) can only be resolved empirically.

**Rejected alternatives:**
- **Implement from schema and iterate** — Rejected because each failed attempt requires spawning a fresh App Server and the error messages may be truncated (the initial error was cut at a semicolon).
- **Single combined smoke** — User: "The biggest weakness is trying to answer too much with one combined smoke. If the first payload is malformed, or the first tool call fails for unrelated reasons, you lose resolution."

**Implication:** Implementation cannot start until probes 1-2 (acceptance) pass. The builder design for `excludeSlashTmp`/`excludeTmpdirEnvVar` and `includePlatformDefaults` equivalents depends on probe results.

**Trade-offs accepted:** Probes take time and each spawns an App Server process. But the alternative (iterating blind) cost us two full delegation failures before we had any diagnostic signal.

**Confidence:** High (E2) — the probe script already reproduced the root cause successfully. Extending it for the matrix is mechanical.

**Reversibility:** N/A — probes are diagnostic, not implementation.

**Change trigger:** If the live App Server becomes unavailable or changes version mid-investigation.

### Capability-specific floor, not global version bump

**Choice:** Gate only execution turns on `permissionProfile`-capable runtime. Advisory turns stay on `sandboxPolicy` unless the advisory probe fails.

**Driver:** User: "Treat 'raise execution runtime floor' as an execution capability decision first, not automatically a global `MINIMUM_CODEX_VERSION` bump. If advisory still works on older versions, a global floor would block more than the confirmed failure requires."

**Rejected alternatives:**
- **Global `MINIMUM_CODEX_VERSION = 0.128.0`** — Would block advisory features (consult, dialogue, review) on older servers even if they still work.

**Implication:** The codebase needs to express execution-specific compatibility separately from advisory compatibility. If this isn't architecturally clean, a global floor is the pragmatic fallback with the understanding that it's a product/support decision.

**Trade-offs accepted:** Two codepaths (execution uses `permissionProfile`, advisory uses `sandboxPolicy`) adds complexity to `_run_turn`. Acceptable because it's bounded to one method.

**Confidence:** Medium (E1) — depends on advisory probe (probe 1). If advisory is also broken, this decision is moot and the scope doubles.

**Reversibility:** High — merging into a global floor is always possible.

**Change trigger:** Advisory probe fails (scope expands to full migration) or advisory `sandboxPolicy` is deprecated in a future version.

## Changes

### `.tmp/probe_turn_start.py` — diagnostic probe script

**Purpose:** Direct reproduction of the `turn/start` JSON-RPC call sequence, bypassing the delegation controller, worker runner, and MCP tool layers. Captures full error objects without the `{!r:.100}` truncation in `jsonrpc_client.py:96`.

**Approach:** Uses the plugin's `JsonRpcClient` class directly. Spawns `codex app-server`, runs `initialize` → `account/read` → `thread/start` → `turn/start` with the exact sandbox policy from `build_workspace_write_sandbox_policy()`.

**Key result:** `turn/start` returns `{'code': -32600, 'message': 'Invalid request: workspaceWrite.readOnlyAccess is no longer supported; '}`. Steps 1-3 succeed.

**Note:** Uses hardcoded worktree path from the discarded `83d1a7cd` job. Future probes should use a fresh worktree or verify the path exists.

### `docs/plans/2026-05-01-codex-app-server-v128-execution-sandbox-migration-plan.md` — migration plan

**Purpose:** Scoped plan for migrating execution turns to `permissionProfile`.

**Status:** Written by user, scrutinized. Verdict: Minor revision. See Scrutiny Results below for the five required changes.

## Codebase Knowledge

### Execution turn call chain (confirmed during RCA)

| Step | Location | Role |
|------|----------|------|
| Call site | `delegation_controller.py:1370` | Calls `run_execution_turn` with sandbox policy from `build_workspace_write_sandbox_policy(worktree_path)` |
| Public method | `runtime.py:253` (`run_execution_turn`) | Takes `sandbox_policy: dict`, passes to `_run_turn` |
| Shared method | `runtime.py:287` (`_run_turn`) | Constructs `turn/start` params; always sets `params["sandboxPolicy"]` at line 308 |
| Param construction | `runtime.py:303-315` | Builds the full `turn/start` JSON-RPC params dict |
| JSON-RPC transport | `jsonrpc_client.py:61` (`request`) | Sends JSON-RPC, raises `JsonRpcError` on error response |
| Error truncation | `jsonrpc_client.py:95-97` | `{error!r:.100}` truncates error dict repr to 100 chars |
| Worker exception path | `delegation_controller.py:1401` → `_mark_execution_unknown_and_cleanup:1430` | Catches exception, marks job unknown, re-raises |
| Worker runner catch | `worker_runner.py:70-74` | Catches re-raised exception, logs via `logger.exception`, calls `announce_worker_failed` |
| Start outcome | `delegation_controller.py:911-922` | Matches `WorkerFailed`, raises `DelegationStartError(reason="worker_failed_before_capture")` |

### Advisory vs. execution sandbox paths

| Path | Builder | Sandbox type | `_run_turn` param |
|------|---------|-------------|-------------------|
| Advisory (consult, dialogue) | `_build_read_only_sandbox_policy()` at `runtime.py:21` | `{"type": "readOnly"}` | `sandboxPolicy` |
| Execution (delegation) | `build_workspace_write_sandbox_policy()` at `runtime.py:65` | `{"type": "workspaceWrite", "readOnlyAccess": {...}, ...}` | `sandboxPolicy` |

Both paths go through `_run_turn` which always sets `params["sandboxPolicy"]`. After migration, execution will use `params["permissionProfile"]` instead. Advisory stays on `sandboxPolicy` unless probe 1 shows it's also broken.

### `_mark_execution_unknown_and_cleanup` — observability gap

At `delegation_controller.py:1430`. Receives `job_id`, `collaboration_id`, `runtime_id`, `entry` — but NOT the exception. Called from the `except Exception` at line 1401 before the re-raise. The exception is available at the catch site but not passed to the cleanup method. This is why the job record contains no diagnostic information when `unknown` is reached.

Three possible persistence paths for the observability patch:
1. Add `failure_reason: str | None` parameter to `_mark_execution_unknown_and_cleanup` (signature change, affects 3+ call sites)
2. Capture at line 1401 before calling cleanup (minimal change, one call site)
3. Persist in worker runner after the catch at `worker_runner.py:70` (separate journal write)

The `DelegationStartError` at line 921 already carries `cause=exc`, but `cause` is only surfaced as `reason` to the MCP tool handler. The full exception string is lost.

### Schema comparison evidence

| Document | Location | Versions compared |
|----------|----------|-------------------|
| 0.117.0 `TurnStartParams` | `tests/fixtures/codex-app-server/0.117.0/v2/TurnStartParams.json` | Baseline (working) |
| Pre-candidate-a `TurnStartParams` | `.tmp/app-server-schema-pre-candidate-a/v2/TurnStartParams.json` | Intermediate (≥0.125.0) |
| Comparison | `docs/superpowers/specs/codex-collaboration/evidence/2026-04-29-codex-app-server-schema-0.117.0-to-0.125.0-comparison.json` | Diff between 0.117.0 and 0.125.0 |

Key finding from comparison: `TurnStartParams` gained `permissionProfile` (line 1224-1239 of comparison doc). Description: "Override the full permissions profile for this turn and subsequent turns. Cannot be combined with `sandboxPolicy`." The `sandboxPolicy` field was still present in the pre-candidate-a schema, but the `0.128.0` runtime rejects `workspaceWrite.readOnlyAccess` at runtime.

### `PermissionProfile` schema (from pre-candidate-a)

Three variants: `managed` (App Server constructs sandbox), `disabled` (no sandbox), `external` (caller-enforced). For delegation, `managed` is correct — we want the App Server to enforce our filesystem entries.

`managed` requires:
- `fileSystem`: `restricted` (with `entries` array of `FileSystemSandboxEntry`) or `unrestricted`
- `network`: `{"enabled": boolean}`

`FileSystemSandboxEntry` requires:
- `access`: `"read"` | `"write"` | `"none"`
- `path`: a `FileSystemPath` object (NOT a bare string)

`FileSystemPath` variants:
- `{"type": "path", "path": "/absolute/path"}` — concrete path
- `{"type": "glob_pattern", "pattern": "..."}` — glob
- `{"type": "special", "value": {"kind": "root"|"minimal"|"current_working_directory"|"project_roots"|"tmpdir"|"slash_tmp"|"unknown"}}` — special paths

`special:minimal` is the likely replacement for `includePlatformDefaults: true`, but this is unverified against the live `0.128.0` runtime.

### Accumulated worktrees

18 git worktrees from prior delegation runtimes (1 primary + 17 delegation). Not causal to this failure but notable for future cleanup.

## Context

### Roadmap position

| Step | Status | Description |
|------|--------|-------------|
| 0 | Complete | Roadmap cleanup — docs-only reconciliation |
| 1 | Complete + closed | Reply extraction fallback |
| 2 | **Blocked** — PR merged, smoke blocked on sandbox migration | T-20260429-01 Phase 1 sandbox carve-outs |
| 3 | Not started | T-20260429-02 unsupported request classification |
| 4 | Not started | Carry-forward debt sweep |
| 5 | Not started | BMARK-L1-L3 disposition |
| 6 | Not started | AUDIT-CONSUMER-INTERFACE specification or deferral |

### PR #127 state

Merged to `main` via merge commit `cd586e60`. The Step 2 implementation (Options B + E + `~/.agents/` carve-outs) is on `main` but cannot be verified via live smoke until the sandbox protocol migration is complete. The carve-out paths themselves are correct — the rejection is of the `readOnlyAccess` container field, not the paths inside it.

### Scrutiny results summary

Plan at `docs/plans/2026-05-01-codex-app-server-v128-execution-sandbox-migration-plan.md`. Verdict: **Minor revision**. Five required changes before credible:

1. **F1 (Critical):** Add contingency for advisory probe failure — if probe 1 fails, the scope doubles to include advisory migration. The plan has no designed response.
2. **F2 (High):** Specify observability persistence mechanism — which store, which method signature changes, where the exception is captured.
3. Add contingency for `special:minimal` not being available — what is the fallback if managed profiles can't express platform defaults?
4. Trace the full call chain in the implementation section: `delegation_controller:1370` → `run_execution_turn:253` → `_run_turn:287` → params at line 303.
5. Add follow-up tracking for advisory `sandboxPolicy` deprecation — even if it works today, it's on a deprecation path.

## Learnings

### `workspaceWrite.readOnlyAccess` removed in Codex App Server 0.128.0

**Mechanism:** The `turn/start` JSON-RPC method in Codex App Server `0.128.0` rejects `workspaceWrite` sandbox policies that include the `readOnlyAccess` field with error code `-32600` (Invalid Request). The replacement is `permissionProfile` with a `managed` profile type containing explicit `fileSystem.entries`.

**Evidence:** Direct probe at `.tmp/probe_turn_start.py` — `initialize`, `account/read`, `thread/start` all succeed; `turn/start` returns `{'code': -32600, 'message': 'Invalid request: workspaceWrite.readOnlyAccess is no longer supported; '}`.

**Implication:** All execution delegation is broken on `0.128.0`. Advisory turns may still work (use `readOnly` type which doesn't have `readOnlyAccess`). Migration to `permissionProfile` is required before any `/delegate` runs succeed.

**Watch for:** Future Codex App Server versions may also deprecate `sandboxPolicy` entirely. The advisory path should have a follow-up ticket.

### `worker_failed_before_capture` has no persisted diagnostic

**Mechanism:** When `run_execution_turn` raises an exception, `_mark_execution_unknown_and_cleanup` runs but the exception is not passed to it. The job record transitions to `unknown` with no failure reason. The exception is only logged via `logger.exception` at `worker_runner.py:71`, which goes to MCP server stderr — invisible from the conversation context.

**Evidence:** Two consecutive `unknown` jobs with empty artifacts, no turns, no escalations. Root cause required building a separate diagnostic probe to reproduce the error outside the delegation stack.

**Implication:** Every `unknown` job from a pre-capture failure requires external log access for diagnosis. The observability patch (persist exception string into job/journal) is independently valuable.

**Watch for:** Other `_mark_execution_unknown_and_cleanup` call sites (line 1402 and line 1422) have the same gap.

### The pre-candidate-a schema lags behind the 0.128.0 runtime

**Mechanism:** The vendored pre-candidate-a schema still defines `readOnlyAccess` on `WorkspaceWriteSandboxPolicy`, but the `0.128.0` runtime rejects it. Schema acceptance does not guarantee runtime acceptance for security-sensitive fields.

**Evidence:** Schema shows `readOnlyAccess` as a valid optional field with default. Runtime rejects it with `-32600`.

**Implication:** Do not rely on schema alone for migration. Every payload shape must be probed against the live runtime. The probe matrix approach is the correct methodology.

**Watch for:** Other schema-defined fields that may be deprecated at the runtime level.

### Error message truncation obscures diagnostic guidance

**Mechanism:** `jsonrpc_client.py:96` truncates error dicts to 100 chars via `{error!r:.100}`. The actual error message from `0.128.0` ends with a semicolon and space (`"is no longer supported; "`), strongly suggesting continuation text was truncated.

**Evidence:** Full error dict is ~96 chars repr, at the truncation boundary. The trailing `; ` is consistent with "is no longer supported; use permissionProfile instead" or similar guidance.

**Implication:** The probe script should capture full error objects without truncation. The observability patch should also use full error text.

**Watch for:** Other JSON-RPC errors that may contain migration guidance after the truncation point.

## Next Steps

### 1. Address scrutiny findings in the migration plan

**Dependencies:** None.

**What to do:** Apply the 5 required changes from the scrutiny (see Scrutiny Results Summary above). The critical one is the advisory probe failure contingency.

### 2. Run the probe matrix

**Dependencies:** Plan revisions complete (step 1). Existing `.tmp/probe_turn_start.py` provides the scaffold.

**What to read first:** The migration plan at `docs/plans/2026-05-01-codex-app-server-v128-execution-sandbox-migration-plan.md` for the 7-probe specification.

**Approach:** Extend `.tmp/probe_turn_start.py` with separate functions for each probe. Capture full JSON-RPC error objects. Run probes in order: advisory acceptance → managed profile shape → filesystem behavior → read/write semantics → CWD leakage → tmp boundaries → credential boundaries. Record all results in a diagnostic artifact.

**Acceptance criteria:** All 7 probes executed with clear pass/fail results. The five unknowns resolved: `FileSystemPath` shapes, `special:minimal` acceptance and safety, write-implies-read, deny precedence, CWD/minimal widening.

### 3. Implement the migration

**Dependencies:** Probe matrix complete with passing results for probes 1-2.

**What to read first:** Probe results (for builder design decisions), then `runtime.py:65-131` (current builder), `runtime.py:253-315` (`run_execution_turn` and `_run_turn`), `delegation_controller.py:1370` (call site), `delegation_controller.py:1430` (`_mark_execution_unknown_and_cleanup` for observability patch).

**Approach:** Three units: (1) profile builder, (2) turn payload selector, (3) observability patch. The builder uses probe-verified entry shapes. The payload selector modifies `_run_turn` to accept either `sandbox_policy` or `permission_profile`. The observability patch adds a `failure_reason` parameter to the cleanup method.

### 4. Run the deferred T-20260429-01 live smoke

**Dependencies:** Migration implemented, tests passing.

**What to read first:** The smoke specification from this session's conversation (scratch diagnostic artifact, classification table, credential probes).

**Acceptance criteria:** Avoidable sandbox-friction escalations <=2; credential/session paths blocked; network blocked; tmp behavior matches explicit policy.

### 5. Ticket/register closeout

**Dependencies:** Smoke passes acceptance criteria.

**What to do:** 3-surface operation: ticket AC checkboxes, reconciliation register, current-state watchpoints.

## In Progress

Clean stopping point. The probe script exists and confirmed the root cause. The migration plan exists and has been scrutinized. No implementation work has started. The current branch `fix/delegation-turn-start-probe` has only the probe script in `.tmp/`.

Two discarded delegation jobs (`1261a5f3` and `83d1a7cd`) are cleaned up. No active delegation.

## Open Questions

### Does advisory `sandboxPolicy: {"type": "readOnly"}` still work on 0.128.0?

Probe 1 will answer this. If it fails, the migration scope doubles to include advisory turns (consult, dialogue, review). The plan has no contingency for this outcome yet (scrutiny finding F1).

### Does `special:minimal` exist and is it safe?

The pre-candidate-a schema shows `{"kind": "minimal"}` in `FileSystemSpecialPath`. If it works and doesn't grant credential/session access, it replaces `includePlatformDefaults: true`. If it doesn't exist or is unsafe, the builder needs an alternative way to express platform defaults — and that alternative is unknown.

### Does `access: "write"` imply read?

The old policy listed the worktree in both `writableRoots` and `readableRoots`. If `write` doesn't imply `read` in the new model, the builder needs two entries per writable path. If duplicate entries are rejected, the builder shape changes again.

### What is the full text of the truncated error message?

The error ends with `; ` suggesting continuation. The full message might contain migration guidance. The probe script should capture the full error without truncation.

### Should the 5 non-codex closed tickets in `docs/tickets/` root be moved?

Carried from four prior handoffs. Separate general hygiene, not codex-collaboration work.

### When should the older handoff be addressed?

There is still an older handoff in `docs/handoffs/` from a separate topic. It was not loaded this session or the prior session.

## Risks

### Advisory turns may also be broken

If `0.128.0` rejects `sandboxPolicy` entirely (not just `readOnlyAccess`), advisory features (consult, dialogue, review) are all broken. This would be discovered in probe 1 but the migration plan has no designed response for this outcome.

### `special:minimal` might not exist or might be too broad

If `minimal` grants access to credential paths, it can't be used. If it doesn't exist, there's no known way to express platform defaults in the `managed` profile. Either outcome blocks the migration until an alternative is found.

### Probe matrix results may invalidate the builder design

If multiple probes fail (e.g., `minimal` is rejected AND deny entries don't override AND `write` doesn't imply read), the builder design becomes significantly more complex. The plan assumes most probes will pass.

### 18 accumulated worktrees from prior delegations

Not causal to this failure but could cause resource issues in future delegation runs. No automated cleanup exists.

## References

- **Probe script:** `.tmp/probe_turn_start.py`
- **Migration plan:** `docs/plans/2026-05-01-codex-app-server-v128-execution-sandbox-migration-plan.md`
- **0.117.0 TurnStartParams fixture:** `packages/plugins/codex-collaboration/tests/fixtures/codex-app-server/0.117.0/v2/TurnStartParams.json`
- **Pre-candidate-a TurnStartParams:** `.tmp/app-server-schema-pre-candidate-a/v2/TurnStartParams.json`
- **Schema comparison:** `docs/superpowers/specs/codex-collaboration/evidence/2026-04-29-codex-app-server-schema-0.117.0-to-0.125.0-comparison.json`
- **Sandbox policy builder:** `packages/plugins/codex-collaboration/server/runtime.py:65-131`
- **Turn payload construction:** `packages/plugins/codex-collaboration/server/runtime.py:287-315`
- **Execution call site:** `packages/plugins/codex-collaboration/server/delegation_controller.py:1370`
- **Cleanup method:** `packages/plugins/codex-collaboration/server/delegation_controller.py:1430`
- **Worker runner catch:** `packages/plugins/codex-collaboration/server/worker_runner.py:70-74`
- **T-20260429-01 friction ticket:** `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md`
- **Prior handoff:** `docs/handoffs/archive/2026-04-30_21-57_step-2-sandbox-carve-outs-implementation-and-review.md`
- **Reconciliation register:** `docs/status/codex-collaboration-reconciliation-register.md`
- **PR #127:** https://github.com/jpsweeney97/claude-code-tool-dev/pull/127 (merged)

## Gotchas

### `FileSystemPath` is an object, not a bare string

The `permissionProfile` schema's `FileSystemSandboxEntry.path` is a discriminated union: `{"type": "path", "path": "/abs/path"}`, NOT just `"/abs/path"`. Bare strings will produce another `-32600`. This is the most likely second rejection if the builder is coded from the pseudocode in the plan.

### The pre-candidate-a schema is NOT the 0.128.0 schema

The schema snapshot is from an unknown intermediate version (≥0.125.0). Field names, enum values, and special path kinds may have changed. Do not trust the schema without empirical verification against the live runtime.

### Error message truncation hides diagnostic guidance

`jsonrpc_client.py:96` truncates to 100 chars. The `0.128.0` error message was likely truncated after a semicolon, possibly hiding "use permissionProfile instead" or similar guidance. Always capture full error objects in probes.

### `_run_turn` always sends `sandboxPolicy` — no conditional path exists yet

Line 308 unconditionally sets `params["sandboxPolicy"] = sandbox_policy`. The migration needs to make this conditional: send `permissionProfile` for execution, `sandboxPolicy` for advisory.

### `_mark_execution_unknown_and_cleanup` doesn't receive the exception

The cleanup method at line 1430 receives job/runtime metadata but not the exception that triggered it. The exception is available at the catch site (line 1401) but not passed through. Any observability patch needs to bridge this gap.

### Ticket closure is a 3-surface operation

Reinforced from two prior sessions: closing a codex-collaboration ticket requires updating (1) the ticket itself, (2) the reconciliation register, (3) the current-state watchpoints.

## Conversation Highlights

**On the initial delegation failures:**
After two `worker_failed_before_capture` errors, I presented hypotheses. User: "The failure is real, but I would not classify PR #127 as suspect from the evidence so far." This correctly separated the carve-out content (PR #127) from the container field rejection (protocol break).

**On the probe approach:**
User: "The biggest weakness is trying to answer too much with one combined smoke. If the first payload is malformed, or the first tool call fails for unrelated reasons, you lose resolution." This drove the 7-probe matrix design.

**On version floor framing:**
User: "Treat 'raise execution runtime floor' as an execution capability decision first, not automatically a global `MINIMUM_CODEX_VERSION` bump. If advisory still works on older versions, a global floor would block more than the confirmed failure requires."

**On the `FileSystemPath` correction:**
User: "Your read is right, and the `FileSystemPath` wrapper is the most important correction. My pseudocode would very likely hit the next `-32600`."

**On the plan scrutiny:**
User invoked `/scrutinize` on their own plan. The scrutiny found 1 critical, 1 high, and 3 medium findings. The user accepted the verdict without pushback.

## User Preferences

**Thorough scoping before implementation (reinforced):** User explicitly blocked implementation multiple times: "Also, don't proceed to implementation until I explicitly say to. We need to continue scoping and planning right now." Three rounds of plan iteration before any code would be written.

**Structured RCA format:** User's investigation feedback used the exact `Hypotheses / Evidence needed / Tests to run / Recommended next step` format from the project's CLAUDE.md root-cause-analysis protocol.

**Expects challenge and gap-finding:** User asked "What subtle nuances did I miss? Where is this weak? Where could things go wrong? Where could we be surprised?" — wanted adversarial review of their own plan, not agreement.

**Invokes `/scrutinize` on own work:** Used formal scrutiny on their own plan draft, not just on Claude's work. Treats the scrutiny process as a quality gate regardless of authorship.

**Probe-empirical over schema-theoretical:** User: "Do not rely on schema alone where runtime behavior is security-sensitive." Strong preference for empirical verification over inference from documentation.

**Clean separation of diagnostic from production code:** The probe script lives in `.tmp/`, not in the test suite. Diagnostic tools are separate from the product.
