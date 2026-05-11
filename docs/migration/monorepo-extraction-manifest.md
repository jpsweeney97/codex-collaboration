# Monorepo Extraction Manifest

`codex-collaboration` source-authority migration from `claude-code-tool-dev` monorepo.

## Migration Type

This is a **source-authority migration**, not a history-preserving split. The canonical location of authoritative source moves to this repository. Git history preservation is **deferred**; commits from the monorepo do not cross the boundary. Provenance is recorded below.

A separate history-preserving archival migration (using `git filter-repo` or `git subtree split`) may occur later if needed. This manifest is the bridge.

## Provenance

| Field | Value |
|---|---|
| Source repo | `/Users/jp/Projects/active/claude-code-tool-dev` |
| Source branch | `main` |
| Source commit SHA | `dd112da644de8851c9bba591a50a592cfcdeffde` |
| Source worktree cleanliness | clean at copy time (`git status` reported `nothing to commit, working tree clean`) |
| Destination repo | `/Users/jp/Projects/active/codex-collaboration` |
| Migration date | 2026-05-11 |
| Migration agent | Claude Opus 4.7 (1M context) |
| Migrator | jpsweeney97@gmail.com |

## Scope Summary

Move all active `codex-collaboration` authority into the new repo: source, tests, specs, status, tickets, evidence, handoffs, packaging, and local development. Snapshot-only historical artifacts (reviews, benchmark transcripts, older plans, incidental references) remain in the source monorepo as `left-historical`. Current-facing monorepo surfaces are replaced with redirects pointing here.

## Classification Vocabulary

| Class | Meaning |
|---|---|
| `migrated-active` | Live source, tests, docs, tickets, status, evidence, packaging, or operational handoff |
| `migrated-historical` | Historical material moved because it belongs with this project's record |
| `left-historical` | Historical monorepo artifact left snapshot-true in source |
| `redirected` | Current-facing monorepo surface replaced with a pointer to this repo |
| `excluded` | Generated residue, incidental mention, or unrelated file |

A file is **active** if it governs current behavior, current status, current unresolved work, local development, packaging, verification, or operator handoff.

## Inventory

### Migrated-Active

#### Source code & packaging (mapped to repo root)

| Old path (in monorepo) | New path (in this repo) | Rationale |
|---|---|---|
| `packages/plugins/codex-collaboration/server/` | `server/` | MCP server, runtime, delegation controller, dialogue — live source authority |
| `packages/plugins/codex-collaboration/skills/` | `skills/` | 8 plugin skills — live operator surface |
| `packages/plugins/codex-collaboration/agents/` | `agents/` | shakedown-dialogue, dialogue-orchestrator subagents — live |
| `packages/plugins/codex-collaboration/scripts/` | `scripts/` | Bootstrap, guards, smoke setup — live operational scripts |
| `packages/plugins/codex-collaboration/hooks/` | `hooks/` | hooks.json hook configuration — live |
| `packages/plugins/codex-collaboration/references/` | `references/` | tag-grammar.md, dialogue-turn-contract.md — referenced from skills/specs |
| `packages/plugins/codex-collaboration/tests/` | `tests/` | 67 test files + 197 fixture files — live verification |
| `packages/plugins/codex-collaboration/.mcp.json` | `.mcp.json` | MCP server registration (uses `${CLAUDE_PLUGIN_ROOT}` — auto-rebases to new root) |
| `packages/plugins/codex-collaboration/.claude-plugin/plugin.json` | `.claude-plugin/plugin.json` | Plugin manifest |
| `packages/plugins/codex-collaboration/pyproject.toml` | `pyproject.toml` | Already standalone-shaped; no workspace dependency |
| `packages/plugins/codex-collaboration/README.md` | `README.md` (rewritten) | Standalone-repo README with authority declaration |

**Source change applied during migration:** `scripts/containment_smoke_setup.py:_repo_paths()` and `tests/test_containment_smoke_setup.py` hardcoded monorepo paths (`docs/superpowers/specs/codex-collaboration/…` and `packages/plugins/codex-collaboration/…`) and computed repo root via `Path(__file__).resolve().parents[4]`. Both were rewritten to the standalone layout (`docs/specs/…`, `server/…`, `scripts/…`, `parents[1]`). Pre-existing ruff debt (3 unused `pytest` imports, 1 E402 mid-file `import json`) was cleaned up so the standalone gate passes; these were already present in the monorepo.

#### Authoritative specs (mapped to `docs/specs/`)

| Old path | New path | Rationale |
|---|---|---|
| `docs/superpowers/specs/codex-collaboration/foundations.md` | `docs/specs/foundations.md` | Authority owner |
| `docs/superpowers/specs/codex-collaboration/contracts.md` | `docs/specs/contracts.md` | Authority owner |
| `docs/superpowers/specs/codex-collaboration/delivery.md` | `docs/specs/delivery.md` | Authority owner |
| `docs/superpowers/specs/codex-collaboration/decisions.md` | `docs/specs/decisions.md` | Authority owner |
| `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | `docs/specs/promotion-protocol.md` | Authority owner |
| `docs/superpowers/specs/codex-collaboration/advisory-runtime-policy.md` | `docs/specs/advisory-runtime-policy.md` | Authority owner |
| `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | `docs/specs/recovery-and-journal.md` | Authority owner |
| `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | `docs/specs/dialogue-supersession-benchmark.md` | Supporting authority |
| `docs/superpowers/specs/codex-collaboration/official-plugin-rewrite-map.md` | `docs/specs/official-plugin-rewrite-map.md` | Supporting authority |
| `docs/superpowers/specs/codex-collaboration/README.md` | `docs/specs/README.md` | Spec entry point |
| `docs/superpowers/specs/codex-collaboration/spec.yaml` | `docs/specs/spec.yaml` | Authority map |
| `docs/superpowers/specs/codex-collaboration/2026-04-29-codex-app-server-0.125.0-schema-delta.md` | `docs/specs/2026-04-29-codex-app-server-0.125.0-schema-delta.md` | Active schema-delta record |
| `docs/superpowers/specs/codex-collaboration/evidence/2026-04-29-codex-app-server-schema-0.117.0-to-0.125.0-comparison.json` | `docs/specs/evidence/2026-04-29-codex-app-server-schema-0.117.0-to-0.125.0-comparison.json` | Active evidence artifact |

#### Active design docs (mapped to `docs/specs/design-docs/`)

| Old path | New path | Rationale |
|---|---|---|
| `docs/superpowers/specs/2026-03-27-codex-collaboration-plugin-design.md` | `docs/specs/design-docs/...` | Foundational design doc |
| `docs/superpowers/specs/2026-03-31-persistence-hardening-and-type-narrowing-design.md` | `docs/specs/design-docs/...` | Hardening design |
| `docs/superpowers/specs/2026-04-12-dialogue-first-turn-fast-path-hardening-design.md` | `docs/specs/design-docs/...` | Dialogue hardening |
| `docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md` | `docs/specs/design-docs/...` | Delegate UX |
| `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` | `docs/specs/design-docs/...` | Deferred approval response |

#### Status (mapped to `docs/status/`, redundant `codex-collaboration-` prefix dropped)

| Old path | New path | Rationale |
|---|---|---|
| `docs/status/codex-collaboration-current-state.md` | `docs/status/current-state.md` | Project state reader entry point |
| `docs/status/codex-collaboration-reconciliation-register.md` | `docs/status/reconciliation-register.md` | Open / unreconciled work |

#### Architecture

| Old path | New path | Rationale |
|---|---|---|
| `docs/architecture/2026-05-01-codex-app-server-current-client-platform-rebaseline.md` | `docs/architecture/...` | Current rebaseline |
| `docs/architecture/2026-05-01-codex-app-server-v128-permission-architecture-implications.md` | `docs/architecture/...` | Active arch note |

#### Audits, assessments, decisions

| Old path | New path | Rationale |
|---|---|---|
| `docs/audits/2026-04-29-codex-collaboration-status-verification.md` | `docs/audits/...` | Latest status audit |
| `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md` | `docs/assessments/...` | Drift report (final verdict: all 9 findings addressed) |
| `docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md` | `docs/decisions/...` | Drift recovery decision record |

#### Tickets

| Old path | New path | Rationale |
|---|---|---|
| `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md` | `docs/tickets/...` | Active ticket (T-20260429-01) |
| `docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md` | `docs/tickets/...` | Active ticket (T-20260429-02) |
| `docs/tickets/closed-tickets/` (17 codex-collaboration closed tickets) | `docs/tickets/closed-tickets/...` | Closed project record |

17 closed tickets migrated (codex-collaboration era only). 8 pre-codex-collaboration closed tickets (context-injection / cross-model predecessor era) were intentionally **not** moved — see `excluded` section below.

#### Handoffs

| Old path | New path | Rationale |
|---|---|---|
| `docs/handoffs/` (4 codex-collaboration handoffs, excluding page-turner) | `docs/handoffs/` | Recent operational handoffs |
| `docs/handoffs/archive/` (145 codex-collaboration handoffs) | `docs/handoffs/archive/` | Historical handoff record |

In the monorepo, `docs/handoffs/` is gitignored (`.gitignore` entry: `docs/handoffs/`). Because the monorepo never tracked these files in git, "history preservation deferred" is moot for handoffs — they have no git history to preserve. In this repo, the handoff directories are tracked (not gitignored) because they are the canonical project record.

Excluded from migration: 9 non-codex-collaboration archived handoffs (5 about the `handoff` plugin's `handoff-no-commit` refactor, 4 about the public claude-code-skills repo spec) and 1 recent non-codex handoff (page-turner browser extension design).

#### Plans (operational, recent)

| Old path | New path | Rationale |
|---|---|---|
| `docs/plans/2026-04-30-step-2-sandbox-carve-outs-options-b-e-agents.md` | `docs/plans/...` | Phase 1 sandbox carve-outs (landed, retained for closure evidence) |
| `docs/plans/2026-05-01-codex-app-server-*` (6 files) | `docs/plans/...` | Current platform rebaseline plans |
| `docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md` | `docs/plans/...` | Envelope-overclaim fix (PR #128, just landed) |
| `docs/superpowers/plans/2026-04-21-t07-analytics-7a.md` | `docs/plans/...` | T-07 analytics plan |

#### Standalone-repo metadata (created during migration)

| New artifact | Purpose |
|---|---|
| `README.md` | Standalone-repo README, declares sole authority |
| `AGENTS.md` | Instructions for AI coding agents |
| `.gitignore` | Standalone repo's gitignore (handoffs are NOT gitignored in this repo) |
| `.github/workflows/ci.yml` | CI workflow (uv + ruff + pytest + JSON validation) |
| `scripts/check` | Local convenience script mirroring CI gates |
| `docs/migration/monorepo-extraction-manifest.md` | This file |

### Left-Historical (snapshot-true in monorepo, not moved)

These artifacts record past work that is not used to determine current behavior or open work. Snapshots stay where they are.

- `docs/reviews/2026-03-*-*.md` and earlier — historical reviews (R1, R2, delegation review rounds 4-7, T04 evidence review, etc.).
- `docs/superpowers/plans/2026-02-*` through `2026-04-21-*` and earlier — completed snapshot plans for T02/T03/T04/T05/T06/T07/T08/Packet-1 work. Memory and closed tickets contain the outcomes.
- `docs/plans/2026-03-*-*` through `2026-04-24-packet-1-*` and earlier — older completed plans, including the `2026-04-24-packet-1-deferred-approval-response/` directory of task-level plans.
- `docs/plans/t04-t4-scouting-position-and-evidence-provenance/`, `t8-t4-live-smoke-log.md`, `t8-t4-poll-telemetry.jsonl` — snapshot evidence from T8 shakedown.
- `docs/superpowers/specs/2026-02-*` through `2026-03-*` codex-tagged design docs (codex-plugin-design, cross-model-plugin-migration, codex-shim, codex-consult-adapter) — predecessor cross-model plugin lineage, not codex-collaboration project record.
- `docs/tickets/closed-tickets/2026-02-*`, `2026-03-19-*` — context-injection / cross-model predecessor tickets (T-001, T-002, T-003, T-004, T-005, T-006, T-010, T-20260319-01).
- Benchmark transcripts and discontinued-tier-A/B artifacts under `docs/benchmarks/`.

### Redirected (current-facing monorepo surfaces replaced with pointers)

Applied in monorepo on branch `chore/extract-codex-collaboration`, commit
`701952b822a7cb5594d2fde648cec428f5c6d1ae`. Full list of redirected paths
in monorepo:

**Configuration / discovery surfaces (modified in place):**
- `pyproject.toml` — `[tool.uv.workspace] members` no longer includes `packages/plugins/codex-collaboration`; explanatory comment added
- `.claude-plugin/marketplace.json` — `codex-collaboration` plugin entry removed
- `.claude/CLAUDE.md` — `codex-collaboration` row removed from Packages table; migration redirect note added
- `docs/references/README.md` — canonical-source pointer updated from `packages/plugins/codex-collaboration/references/` to new repo

**Package + spec directories demoted to MIGRATED stub:**
- `packages/plugins/codex-collaboration/` — entire dir contents replaced with `MIGRATED.md`
- `docs/superpowers/specs/codex-collaboration/` — entire dir contents replaced with `MIGRATED.md`

**Current-facing single docs replaced with redirect content:**
- `docs/status/codex-collaboration-current-state.md`
- `docs/status/codex-collaboration-reconciliation-register.md`
- `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md`
- `docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md`
- `docs/architecture/2026-05-01-codex-app-server-current-client-platform-rebaseline.md`
- `docs/architecture/2026-05-01-codex-app-server-v128-permission-architecture-implications.md`
- `docs/audits/2026-04-29-codex-collaboration-status-verification.md`
- `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`
- `docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md`
- `docs/plans/2026-04-30-step-2-sandbox-carve-outs-options-b-e-agents.md`
- `docs/plans/2026-05-01-codex-app-server-client-platform-exploration-plan.md`
- `docs/plans/2026-05-01-codex-app-server-client-platform-rebaseline-implementation-plan.md`
- `docs/plans/2026-05-01-codex-app-server-materialized-thread-and-server-request-probe-plan.md`
- `docs/plans/2026-05-01-codex-app-server-scratch-home-runtime-probe-plan.md`
- `docs/plans/2026-05-01-codex-app-server-server-request-envelope-probe-plan.md`
- `docs/plans/2026-05-01-codex-app-server-v128-execution-sandbox-migration-plan.md`
- `docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md`
- `docs/superpowers/plans/2026-04-21-t07-analytics-7a.md`

### Excluded (generated residue, unrelated files)

- `.DS_Store` — macOS metadata
- `__pycache__/` — Python bytecode cache
- `.pytest_cache/` — pytest cache
- `.ruff_cache/` — ruff cache
- `.mypy_cache/` — mypy cache
- `*.pyc` — Python bytecode
- Runtime artifacts under `analytics/` (none observed in source tree)

Caches re-appear in this repo after running tests locally; they remain `.gitignore`d.

## File Counts (in new repo, post-migration)

| Tree | Files | SHA-256 (aggregate of file checksums) |
|---|---|---|
| `server/*.py` | 31 | `1132ff258e95d999f869cdd9956ef7beaadb1110efda4d68556adc41de0d44b1` |
| `tests/**.py` | 67 | `39625fb5bb24b4ac5e1ca633303a9a78a1f9dd5590a346a1262f5f362245dc51` |
| `tests/fixtures/**` | 197 | `0da559a3c514c38904c97cf1f9920325c5ac408bad4c925f2ab9b7d95008efd6` |
| `skills/**` | (8 SKILL.md + supporting files) | `84693c18705f40ec78af3f1010be2fd38e10954ef63b7799ce352367baa14539` |
| `docs/specs/**` | 16 (markdown) | `fd9772c7bdd729181cb89780fe87d02a307640da730d9442131fd605f3ea1b9d` |
| `docs/handoffs/**.md` | 149 | (not aggregated; project-record only) |
| `docs/tickets/**.md` | 19 (2 active + 17 closed) | (not aggregated) |

Aggregate checksum method: `find <tree> -type f -exec shasum -a 256 {} + \| shasum -a 256`. This produces a deterministic digest of the digest list; any single-byte change to any file under the tree changes the aggregate.

## Verification Results

All gates run from `/Users/jp/Projects/active/codex-collaboration/` with `PYTHONPATH` unset and `cwd` set to this repo (no monorepo dependency).

| Gate | Command | Result |
|---|---|---|
| Dependency resolution | `uv sync` | OK — 7 packages installed (`iniconfig`, `packaging`, `pluggy`, `pygments`, `pytest 9.0.3`, `pyyaml 6.0.3`, `ruff 0.15.12`) |
| Lint | `uv run ruff check .` | `All checks passed!` |
| Full test suite | `uv run pytest tests -q` | `1099 passed in 254.07s` |
| MCP config | `python -m json.tool .mcp.json` | OK |
| Plugin manifest | `python -m json.tool .claude-plugin/plugin.json` | OK |
| Hooks config | `python -m json.tool hooks/hooks.json` | OK |
| Import smoke | `import server.mcp_server` etc. | All modules resolve from `/Users/jp/Projects/active/codex-collaboration` |
| Convenience runner | `./scripts/check` | All checks passed |

A live Codex App Server / delegation smoke is **not** required for this migration per the goal statement.

### Residual-Reference Report (monorepo, post-cleanup)

A repo-wide grep for `codex-collaboration|codex_collaboration|packages/plugins/codex-collaboration` in the monorepo (limited to `.md/.toml/.yaml/.yml/.json/.cfg/.ini/.py/.sh`) returns **143 files** post-cleanup. Classification:

| Class | Count | Notes |
|---|---|---|
| Migration redirects (stubs I authored) | 22 | The MIGRATED.md stubs, single-file redirects, and updated discovery surfaces — these explicitly point at the new repo |
| Historical reviews / design docs | ~12 | `docs/reviews/2026-*`, design docs `docs/superpowers/specs/2026-03-*` and `2026-04-*-*-design.md` — snapshot-true, never claimed current authority |
| Historical plans (snapshot evidence) | ~50 | `docs/plans/2026-03-*` through `2026-04-24-packet-1-*` and earlier; `docs/superpowers/plans/2026-02-*` through `2026-04-20-*` — completed snapshots; memory + closed tickets carry the outcomes |
| Closed tickets (project history) | 17 | `docs/tickets/closed-tickets/2026-*codex-collaboration*` and related — closed work record; the new repo has its own copy as `migrated-historical`, the monorepo retains them as snapshot ancestry |
| Benchmark transcripts | ~15 | `docs/benchmarks/dialogue-supersession/v1/*` — frozen benchmark artifacts that reference codex-collaboration paths as they were at run time |
| Diagnostics | ~7 | `docs/diagnostics/*codex-app-server*` — frozen diagnostic data |
| Active runtime contract references | 3 | `extensions/skills/next-steps/SKILL.md`, `extensions/skills/making-recommendations/SKILL.md`, `extensions/skills/making-recommendations/references/codex-delta.md` — reference the plugin's runtime tool names (`mcp__plugin_codex-collaboration_codex-collaboration__codex.consult`, etc.). The runtime contract is unchanged by the source migration; the plugin is still installed under the same name, so these references work without modification |
| Historical handoffs (gitignored in monorepo) | many | Local-only session-state files |
| **Disallowed live authority** | **0** | — |
| **Unresolved exceptions** | **0** | — |

Standard met: **zero stale live authority** in the monorepo. No file in the monorepo claims to be the current source of truth for codex-collaboration behavior, status, or open work; all such claims have either been moved or replaced with a redirect.

The repo-wide string count is non-zero by design (historical artifacts mention codex-collaboration); the standard is not zero string matches but zero stale live authority.

### Post-Initial-Commit Cleanup in the New Repo

Initial commit `b3c1f2c2bec593463853fc3142eba60bd23657dc` migrated docs that
still referenced monorepo paths internally
(`packages/plugins/codex-collaboration/server/*`,
`docs/superpowers/specs/codex-collaboration/*`). Commit
`cfcb642` (`chore: rewrite stale monorepo paths in active
docs/skills/references`) rewrote those paths to the standalone layout
across active docs, `references/dialogue-turn-contract.md`, and
`skills/shakedown-b1/SKILL.md`. Closed tickets, archived handoffs,
design docs, and evidence JSON were deliberately left snapshot-true.

## History Preservation

Git history preservation is **deferred**. The monorepo retains the commit history of the package; this repo starts fresh on `main` from the migration commit. If history preservation is later required:

1. Use `git filter-repo --path packages/plugins/codex-collaboration/ --path-rename packages/plugins/codex-collaboration/:` against a fresh monorepo clone.
2. Cherry-pick relevant docs commits (specs, status, tickets) into the rebased tree.
3. Replace this repo's initial-commit history with the filtered history (or merge into a new branch and rebase).

Until then, this manifest plus the source commit SHA in Provenance is the authoritative provenance bridge.
