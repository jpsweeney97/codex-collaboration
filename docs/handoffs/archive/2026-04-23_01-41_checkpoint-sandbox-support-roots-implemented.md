---
date: 2026-04-23
time: "01:41"
created_at: "2026-04-23T05:41:27Z"
session_id: 0507e8d9-bd4b-433c-9c7a-8c4e20337c1e
resumed_from: "docs/handoffs/archive/2026-04-23_01-16_delegate-remediation-implementation-complete.md"
project: claude-code-tool-dev
branch: feature/delegate-remediation-sandbox-approval
commit: 005d4b44
title: "Checkpoint: sandbox support roots implemented, live smoke needs MCP restart"
type: checkpoint
files:
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_runtime.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
---

# Checkpoint: Sandbox Support Roots Implemented, Live Smoke Needs MCP Restart

## Current Task

Fixing the delegate execution sandbox policy gap discovered during live smoke testing.
The first smoke (from predecessor session) proved all 3 handler fixes work, but revealed
that `readableRoots` was too narrow — the Codex agent needs read access to its skill/plugin
files under `~/.codex/`. Implemented a narrow allowlist of Codex support subroots.

## In Progress

**Sandbox support roots — code complete, tests passing.**

Added `_CODEX_SUPPORT_READ_SUBROOTS` allowlist to `runtime.py`: `skills/`, `plugins/cache/`,
`memories/`, `references/`. Helper `_resolve_codex_support_roots()` validates existence,
rejects symlink escapes, deduplicates. `build_workspace_write_sandbox_policy()` now accepts
optional `codex_home` kwarg. Session stores handshake after `initialize()`, exposes
`codex_home` property. Controller passes `entry.session.codex_home` to sandbox builder.

906 tests passing (901 + 5 new). Ruff clean. Git diff clean.

Live smoke attempted twice — both showed stale MCP server code (expected). User will close
this session and start fresh to restart MCP server with updated code.

## Active Files

- `server/runtime.py` — sandbox policy builder + support root resolver + handshake storage
- `server/delegation_controller.py` — one-line change: passes `codex_home` to sandbox builder
- `tests/test_runtime.py` — 5 new tests (support roots, missing roots, symlink escape, init retention, compat)
- `tests/test_delegation_controller.py` — 1 new test + `_FakeSession`/`_FakeControlPlane` gain `codex_home`
- `tests/test_delegate_start_integration.py` — `_StubSession` gains `codex_home` property

## Next Action

1. Start new Claude Code session (restarts MCP server with updated code)
2. Run live smoke: `/delegate` with objective "Create docs/scratch/T-20260423-01-smoke.md"
3. Verify: no `command_approval`/`file_change` escalation for Codex support file reads
4. If smoke passes: commit all changes and create PR
5. If smoke still escalates: check escalation kind/path — may be a different out-of-boundary reason

## Verification Snapshot

```
uv run pytest packages/plugins/codex-collaboration/ → 906 passed in 18.42s
ruff check → All checks passed!
git diff --check → clean
```

## Key Finding

Smoke #2 showed the agent trying `find .. -name AGENTS.md` from the worktree — navigating
above the worktree boundary. Even with support roots, this would sandbox-fail because `..`
resolves outside all allowed paths. The agent should search WITHIN the worktree (which IS a
repo copy). This is a separate issue from the support-root gap — likely an agent
working-directory confusion. Not blocking the current fix.

## Decisions

**D1: Narrow allowlist, not full codex_home.** Only `skills/`, `plugins/cache/`, `memories/`,
`references/` under `codex_home` are readable. Session state, config, logs, and auth material
stay outside. Driver: least-privilege principle for a sandboxed execution agent.

**D2: Symlink-escape check on support roots.** `_resolve_codex_support_roots` rejects any
subroot whose resolved path falls outside resolved `codex_home`. Driver: without this, a
crafted `~/.codex/memories` symlink could grant read access to arbitrary filesystem paths.
