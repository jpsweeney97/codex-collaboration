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
| `docs/handoffs/archive/` (142 codex-collaboration handoffs) | `docs/handoffs/archive/` | Historical handoff record |

In the monorepo, `docs/handoffs/` is gitignored (`.gitignore` entry: `docs/handoffs/`). Because the monorepo never tracked these files in git, "history preservation deferred" is moot for handoffs — they have no git history to preserve.

**Handoff tracking policy in this repo (three temporal frames):**

- **At extraction time** (commits `b3c1f2c`..`9f68e02`), the handoff directories were tracked so the migrated corpus could enter git history as canonical project record. 146 files: 4 at `docs/handoffs/` root + 142 in `docs/handoffs/archive/`.
- **Post-extraction `.gitignore` (commit `3563bb3`)** gitignored `docs/handoffs/` going forward. All 146 migrated files remained tracked (gitignore rules do not untrack already-tracked files); new session handoffs became local-only working memory per the handoff plugin contract.
- **Active-handoff reclassification (this revision)** explicitly untracked the 4 migrated active handoffs at `docs/handoffs/` root via `git rm --cached`. Rationale: they are legitimately active session handoffs eligible for future `/load`, not sealed historical record. The sealed migration corpus is now the 142 archived handoffs only; the 4 active migrated handoffs live under the same local-only policy as new session handoffs.
- See `AGENTS.md` Handoffs section for the operational policy and the explicit promotion procedure that lets an exceptional post-extraction handoff become project record.

Excluded from migration: 12 non-codex-collaboration archived handoffs (5 about the `handoff` plugin's `handoff-no-commit` refactor, 7 about the public claude-code-skills repo / public-skills-repo build) and 1 recent non-codex handoff (page-turner browser extension design). See the file-level handoff exclusions table below for the precise list.

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
| `.gitignore` | Standalone repo's gitignore. At extraction, handoffs were tracked (not gitignored). Post-extraction (commit `3563bb3`), `docs/handoffs/` is gitignored going forward. In this revision, the 4 migrated active handoffs were explicitly untracked (`git rm --cached`); the 142 archived migration handoffs remain as the sealed tracked corpus. See `AGENTS.md` Handoffs section for the operational policy. |
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

## File Counts and Aggregate Checksums (in new repo, post-migration)

Aggregate checksum method (deterministic, reproducible):

```bash
find <tree> -type f -exec shasum -a 256 {} + | sort | shasum -a 256
```

The `| sort` step is critical: `find` traverses inodes in filesystem-defined order, which differs across runs and machines. Sorting the per-file hash lines makes the aggregate content-deterministic.

| Tree | Files | SHA-256 (sorted-line aggregate) |
|---|---|---|
| `server/*.py` | 31 | `3e9c492ca8cd869805173cef7af6852f7b0fbe476c29f1975a6b5953b8a58309` |
| `tests/**.py` (excluding `__pycache__`) | 67 | `abd15ddb9f440678fdffcd432c93ae14bd246a935847492eb79d7b11536fecc3` |
| `tests/fixtures/**` | 197 | `fe80d8ae2aa3183adcaf1eacdbc3ecf254d2f0ca1f07f199c4fa92dfd6a56153` |
| `skills/**` (excluding bytecode caches) | 9 (8 `SKILL.md` + 1 `codex-analytics/scripts/analytics.py`) | `0da785c2f52796e8cec27e0f80524881c2a210f5f1cdad6f3b0bf8a1a43440ab` |
| `docs/specs/**` | 18 (12 top-level + 5 design-docs + 1 evidence JSON) | `035c777d5e4270585a61c55b6597dab506ec5e7b949ed8c235791c9e1d771b28` |
| `docs/handoffs/**.md` (sealed tracked corpus per `git ls-files`, post-active-untrack) | 142 (archived migration handoffs only; 4 active migrated handoffs explicitly untracked in this revision) | (see file-level inventory below) |
| `docs/tickets/**.md` | 19 (2 active + 17 closed) | (see file-level inventory below) |

**Note on prior checksums (commit `e71db48`):** The initial manifest used `find ... -exec shasum +` without sorting, which made the aggregate non-deterministic. Three of the five prior checksums (`tests/fixtures`, `skills`, `docs/specs`) did not reproduce when independently recomputed. The hashes above are recomputed with the deterministic method and after the post-initial-commit cleanup (commits `cfcb642`, `e71db48`, and the DoD-followup commit landing this manifest revision).

**Note on handoff count (post-`3563bb3`, post-active-untrack in this revision):** The `docs/handoffs/**.md` row reports the **tracked sealed corpus** of 142 archived handoffs as enumerated by `git ls-files docs/handoffs/`. Three temporal frames apply:

1. **At extraction:** 146 tracked (4 active + 142 archive). All migrated handoffs entered git history together.
2. **Post-`3563bb3`:** still 146 tracked. The new `.gitignore` rule did not retroactively untrack existing files; it only blocked new additions.
3. **Post-active-untrack (this revision):** 142 tracked. The 4 migrated active handoffs were explicitly untracked via `git rm --cached` to honor their working-memory semantics (eligible for `/load`). Their on-disk presence is machine-specific — they survive on the machine where the untrack ran (and the `.gitignore` rule catches them there ongoing); a fresh clone of `HEAD` reproduces only the 142 archived files. Recover from history when needed: `git restore --source=ed98d3b -- docs/handoffs/<name>`.

The 142 figure refers only to the sealed historical corpus and does not float with local session activity. `find docs/handoffs -name '*.md'` may show a higher count due to local-only files (the 4 migrated active handoffs at root when present on this machine + any new session handoffs + post-load archives). See `AGENTS.md` Handoffs section for the operational policy and promotion procedure.

## File-Level Inventory (DoD §Manifest, path-by-path)

The high-level path-mapping tables in the [Inventory](#inventory) section cover one row per logical group (whole `server/`, whole `tests/`, etc.). The sub-sections below expand the per-class manifest to the file-level granularity the DoD asked for, for the file classes where it most matters: closed tickets, active handoffs, and archived handoffs.

#### File-level inventory: closed tickets (17)

All rows: classification `migrated-historical`. Rationale: codex-collaboration-era closed ticket; project record. Old path `docs/tickets/closed-tickets/<name>` (monorepo), new path `docs/tickets/closed-tickets/<name>` (this repo) — no rename.

| File |
|---|
| `2026-03-27-r1-carry-forward-debt.md` |
| `2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` |
| `2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` |
| `2026-03-30-codex-collaboration-execution-domain-foundation.md` |
| `2026-03-30-codex-collaboration-plugin-shell-and-consult-parity.md` |
| `2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` |
| `2026-03-30-codex-collaboration-safety-substrate-and-benchmark-contract.md` |
| `2026-03-30-context-assembly-redaction-hardening.md` |
| `2026-04-03-t7-conceptual-query-corpus-design-constraint.md` |
| `2026-04-10-dialogue-codex-turn-semantics-clarification.md` |
| `2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md` |
| `2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md` |
| `2026-04-10-T-20260410-04-align-cleanstaleshakedownpy-with-script-convention.md` |
| `2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md` |
| `2026-04-23-codex-collaboration-delegate-execution-remediation.md` |
| `2026-04-23-deferred-same-turn-approval-response.md` |
| `2026-05-11-codex-collaboration-needs-escalation-discard-recovery.md` |

#### File-level inventory: active migrated handoffs (4, now untracked)

All rows: classification `migrated-active-untracked`. Rationale: legitimately active codex-collaboration session handoff, eligible for future `/load`. At extraction these were tracked (incidentally, along with the rest of the corpus); in this revision they were untracked via `git rm --cached` to honor their working-memory semantics. Their on-disk presence is machine-specific: they survive on the machine where the untrack ran (the `.gitignore` rule `docs/handoffs/` catches them ongoing there), but a fresh clone of `HEAD` does not include them. Recover from history when needed: `git restore --source=ed98d3b -- docs/handoffs/<name>`. If a session loads one (after restore if needed), the `mv` to `archive/` proceeds cleanly with no git regression.

Old path `docs/handoffs/<name>` (gitignored in monorepo), new path `docs/handoffs/<name>` (untracked in this repo; on disk locally only on the machine where the untrack ran; recoverable elsewhere from `ed98d3b` history).

| File |
|---|
| `2026-04-29_19-22_t16-protocol-revision-schema-delta-audit-reachability-ticket.md` |
| `2026-05-01_00-29_codex-0128-sandbox-migration-rca-and-plan.md` |
| `2026-05-10_00-34_summary-envelope-overclaim-plan-reapproval.md` |
| `2026-05-11_13-20_summary-t20260511-01-landed-and-quick-wins-pass.md` |

#### File-level inventory: archived handoffs (142)

All rows: classification `migrated-historical`. Rationale: codex-collaboration-era session handoff; project record. Old path `docs/handoffs/archive/<name>` (gitignored in monorepo), new path `docs/handoffs/archive/<name>` (tracked in this repo as part of the sealed migration corpus; the active-handoff reclassification in this revision does not affect these — they remain the canonical sealed historical corpus).

| File |
|---|
| `2026-04-09_01-37_t4-publication-and-security-review.md` |
| `2026-04-10_07-08_t-04-published-pr-102-cleaned-local-main-drift-remains.md` |
| `2026-04-11_00-46_t-03-plan-round-4-fail-open-policy-and-decoupled-tests.md` |
| `2026-04-11_02-45_t-03-plan-round-5-revision-symmetry-fallback-silent-wrapper.md` |
| `2026-04-11_17-00_t03-execution-complete-pr-104.md` |
| `2026-04-11_21-24_pr-104-review-option-b-commits-pending-push.md` |
| `2026-04-11_21-53_pr-104-race-fix-smoke-setup-parity-marked-ready.md` |
| `2026-04-12_00-52_s1-refactor-pr-merge-ticket-triage.md` |
| `2026-04-12_01-40_t-20260410-02-design-review-complete-spec-draft-next.md` |
| `2026-04-12_01-42_t02-fast-path-hardening-design-approved.md` |
| `2026-04-12_23-45_t02-spec-revised-plan-written.md` |
| `2026-04-13_00-36_t02-implementation-complete-pr-open.md` |
| `2026-04-13_01-16_t02-closed-t-20260330-02-ready-for-design.md` |
| `2026-04-13_17-30_t02-t03-closed-t04-t05-unblocked.md` |
| `2026-04-13_18-50_t04-gap-analysis-and-turn-semantics-closure.md` |
| `2026-04-13_19-45_t04-v1-scoping-plan-drafted-pending-review.md` |
| `2026-04-13_22-09_t04-v1-plan-rewritten-after-three-scrutiny-rounds.md` |
| `2026-04-13_23-12_t04-v1-plan-approved-merged-pushed-implementation-unblocked.md` |
| `2026-04-14_12-55_t04-v1-section-10-authoring-decisions-resolved-and-committed.md` |
| `2026-04-14_16-30_t04-v1-four-production-surfaces-authored-and-committed.md` |
| `2026-04-14_20-17_t04-v1-e2e-verified-pr-106-open.md` |
| `2026-04-14_22-45_t04-gatherer-plan-reviewed-and-committed.md` |
| `2026-04-14_23-30_t04-gatherer-implementation-merged-and-e2e-smoke-run.md` |
| `2026-04-15_15-00_t04-ac4-closed-benchmark-v1-contract-rewrite.md` |
| `2026-04-15_19-30_t04-benchmark-v1-scaffold-reviewed-and-committed.md` |
| `2026-04-15_21-11_t04-rc4-resolved-posture-and-turn-budget-wired-through-candidate.md` |
| `2026-04-15_21-45_t04-benchmark-v1-phase1-complete-ready-for-execution.md` |
| `2026-04-15_22-38_t04-execution-mode-gate-cleared-invocations-prepared.md` |
| `2026-04-16_00-18_t04-runtime-gate-cleared-b1-baseline-pending-rerun.md` |
| `2026-04-16_11-48_t04-b1-baseline-valid-after-evidence-count-reconciliation.md` |
| `2026-04-16_12-17_t04-b1-pair-complete-b3-adversarial-next.md` |
| `2026-04-16_19-27_t04-b3-pair-complete-extraction-bug-ticketed.md` |
| `2026-04-16_22-25_t04-b5-pair-captured-scope-governance-addendum-landed-mid-track-commit-lapse.md` |
| `2026-04-16_23-43_t04-b8-pair-captured-all-four-rows-complete-adjudication-next.md` |
| `2026-04-17_01-41_t04-closed-ac7-direct-and-t05-kickoff-note-merged.md` |
| `2026-04-17_11-59_t05-q0-decision-record-implicit-scope-landed.md` |
| `2026-04-17_17-09_t05-tmp-hardening-three-step-chain-landed.md` |
| `2026-04-17_18-01_plan-t05-execution-start-slice-drafted-awaiting-review.md` |
| `2026-04-17_19-23_t05-plan-second-round-recovery-consumer-added.md` |
| `2026-04-17_19-30_t05-plan-revised-after-three-p1-findings.md` |
| `2026-04-17_19-39_t05-plan-rounds-4-5-propagation-and-retry-safety.md` |
| `2026-04-17_20-14_t05-plan-third-round-recovery-wiring-and-register-first.md` |
| `2026-04-17_21-40_t05-plan-rounds-6-7-mcp-tool-error-contract-defensible-merged.md` |
| `2026-04-17_23-42_t05-primitives-tasks-1-5-landed-ready-for-task-6.md` |
| `2026-04-18_00-52_t05-tasks-6-7-landed-orchestrator-and-recovery-ready-for-task-8.md` |
| `2026-04-19_00-45_t05-execution-start-complete-p1-fixes-landed-pending-request-capture-next.md` |
| `2026-04-19_13-00_t05-pending-request-capture-plan-complete-ready-for-execution.md` |
| `2026-04-19_14-02_t05-pending-request-capture-plan-amended-through-scrutiny.md` |
| `2026-04-19_15-13_t05-pending-request-capture-implemented-and-reviewed.md` |
| `2026-04-19_16-26_t05-closed-t06-scoped-review-fixes-merged.md` |
| `2026-04-19_17-01_t06-decide-plan-scrutinized-and-defensible.md` |
| `2026-04-19_22-25_t06-decide-implemented-reviewed-pr-opened.md` |
| `2026-04-19_23-20_t06-decide-merged-poll-next.md` |
| `2026-04-19_23-55_t06-poll-spec-amendments-published.md` |
| `2026-04-20_11-44_t06-poll-plan-scrutinized-ready-for-implementation.md` |
| `2026-04-20_13-30_t06-delegate-poll-implemented-pr-open.md` |
| `2026-04-20_14-37_t06-poll-merged-sidecar-hardening-open-promote-next.md` |
| `2026-04-20_15-30_t06-promote-discard-spec-patched-plan-scrutinized.md` |
| `2026-04-20_21-39_t06-promote-discard-implemented-pr-open.md` |
| `2026-04-20_23-11_t06-promote-discard-merged-review-fixes-landed.md` |
| `2026-04-21_10-37_t06-pending-escalation-view-projection-merged.md` |
| `2026-04-21_12-47_t06-delegate-skill-design-and-plan-complete.md` |
| `2026-04-21_13-40_t06-delegate-skill-ux-implementation-complete.md` |
| `2026-04-21_14-56_t06-pr-review-merge-and-ticket-closure.md` |
| `2026-04-21_21-44_t07-scope-reconciliation-complete.md` |
| `2026-04-21_23-53_t07-7a-plan-scrutinized-and-committed.md` |
| `2026-04-22_00-56_t07-7a-implementation-complete.md` |
| `2026-04-22_01-32_t07-7a-reviewed-and-merged.md` |
| `2026-04-22_12-10_t07-7b-plan-reviewed-and-approved.md` |
| `2026-04-22_13-09_t07-7b-implemented-reviewed-and-pr-opened.md` |
| `2026-04-22_14-15_t07-7b-7c-landed-7d-next.md` |
| `2026-04-22_19-15_t07-7d-context-injection-removed-7e-next.md` |
| `2026-04-22_22-04_t07-7e-cross-model-removed-t07-closed.md` |
| `2026-04-23_00-15_t07-merged-delegate-ticket-opened.md` |
| `2026-04-23_00-33_delegate-remediation-plan-approved.md` |
| `2026-04-23_01-16_delegate-remediation-implementation-complete.md` |
| `2026-04-23_01-41_checkpoint-sandbox-support-roots-implemented.md` |
| `2026-04-23_02-09_delegate-sandbox-state-machine-fix.md` |
| `2026-04-23_15-54_delegate-state-machine-partial-hardening-pr.md` |
| `2026-04-23_16-23_delegate-boundary-tightening-shipped.md` |
| `2026-04-23_17-55_exec-policy-amendment-design-brainstorm.md` |
| `2026-04-23_18-24_exec-policy-rejection-packet-1-carve-off.md` |
| `2026-04-23_21-14_packet-1-deferred-approval-spec-drafted.md` |
| `2026-04-23_22-04_deferred-approval-spec-round-2-scrutiny-revised.md` |
| `2026-04-24_00-53_deferred-approval-spec-rounds-7-to-10-scrutiny.md` |
| `2026-04-24_13-11_deferred-approval-spec-r13-r14-one-snapshot-rule.md` |
| `2026-04-24_22-05_task-6-complete-carry-forward-tracker-seeded.md` |
| `2026-04-24_22-28_phase-b-task-7-complete-replace-pattern-locked.md` |
| `2026-04-24_23-24_phase-b-complete-replay-preservation-locked.md` |
| `2026-04-25_00-00_phase-a-complete-t-20260423-02.md` |
| `2026-04-25_00-28_phase-c-complete-completion-origin-validator-locked.md` |
| `2026-04-25_01-51_phase-d-complete-phase-e-next.md` |
| `2026-04-25_11-40_phase-e-task-13-complete-task-14-next.md` |
| `2026-04-25_12-40_phase-e-task-14-complete-phase-f-next.md` |
| `2026-04-25_13-19_phase-f-task-15-convergence-map-ready.md` |
| `2026-04-25_15-42_phase-f-task-15-complete-task-16-next.md` |
| `2026-04-25_16-43_phase-f-task-16-convergence-map-drafted.md` |
| `2026-04-25_17-50_phase-f-task-16-implementer-blocked-23-test-deadlock.md` |
| `2026-04-25_19-30_phase-f-task-16-complete-3-commit-chain-landed.md` |
| `2026-04-26_07-02_phase-g-task-17-dispatch-and-closure.md` |
| `2026-04-26_12-46_checkpoint-task-18-convergence-map-2nd-draft-pending-review.md` |
| `2026-04-26_13-26_task-18-convergence-map-dispatch-ready.md` |
| `2026-04-26_13-52_task-18-dispatch-packet-ready-after-round-5-correction.md` |
| `2026-04-26_15-45_task-18-opus-implementer-in-flight-after-sonnet-budget-failure.md` |
| `2026-04-26_18-30_phase-g-task-18-closes-1plus1plus1-chain-with-round-7.md` |
| `2026-04-26_23-36_task-19-convergence-map-round-4-and-context-metrics-fix.md` |
| `2026-04-27_00-10_task-19-dispatch-ready-after-8-review-rounds.md` |
| `2026-04-27_01-53_task-20-convergence-map-and-dispatch-packet-reviewed-dispatch-ready.md` |
| `2026-04-27_05-11_task-19-implementation-complete-5-commit-chain.md` |
| `2026-04-27_12-30_checkpoint-task-20-convergence-map-and-dispatch-packet-committed.md` |
| `2026-04-27_13-01_phase-h-tasks-20-22-complete-mypy-triage-done-two-packet-1-typing-fixes-remain.md` |
| `2026-04-27_15-55_packet-1-final-verification-mypy-fixes-pr-created.md` |
| `2026-04-27_22-53_pr-126-review-cycle-1-six-findings-addressed-locally-awaiting-push-approval.md` |
| `2026-04-27_22-55_pr-126-cycles-2-6-f8-f15-fixes-pushed-merge-ready.md` |
| `2026-04-28_01-30_t01-run-record-defensible-pre-live.md` |
| `2026-04-28_04-43_t01-assessment-and-run-record-defensible-copy-mechanics-patched.md` |
| `2026-04-28_06-16_t01-runtime-proof-investigated-fallback-to-operator-instrumentation.md` |
| `2026-04-28_06-58_t01-step-1-complete-file-write-instrumentation-patched-ready-for-restart.md` |
| `2026-04-28_12-10_baseline-attempt-1-complete-tz-bug-corrected-ready-for-candidate-a.md` |
| `2026-04-28_12-35_baseline-attempt-1-closed-and-tightened-ready-for-candidate-a.md` |
| `2026-04-28_15-13_candidate-a-attempt-1-canceled-by-15min-approval-ttl.md` |
| `2026-04-28_17-13_candidate-a-patch-staged-and-pre-variant-evidence-locked.md` |
| `2026-04-28_23-30_candidate-a-closure-complete-att3-smoke-success-and-3-security-probes-blocked.md` |
| `2026-04-28_23-56_candidate-a-attempt-1-cells-filled-and-context-metrics-1m-window-fix.md` |
| `2026-04-29_01-04_candidate-a-engineering-landed-7-commits-pushed-awaiting-plugin-restart-for-live-smoke.md` |
| `2026-04-29_03-01_smoke-completed-t-01-closed-friction-reduction-ticket-opened.md` |
| `2026-04-29_16-13_reconciliation-landed-t16-fix-spec-tightened-branch-merged.md` |
| `2026-04-29_18-12_codex-collaboration-status-verification-audit.md` |
| `2026-04-29_23-59_codex-collaboration-drift-cleanup-d01-resolution.md` |
| `2026-04-30_00-53_codex-collaboration-d02-unknown-request-terminalization.md` |
| `2026-04-30_06-01_codex-collaboration-d03-d07-drift-cleanup.md` |
| `2026-04-30_13-20_codex-collaboration-drift-cleanup-complete-and-roadmap.md` |
| `2026-04-30_14-47_step-0-1-roadmap-cleanup-and-reply-extraction-fallback.md` |
| `2026-04-30_21-04_t-20260416-01-closure-and-step-2-plan.md` |
| `2026-04-30_21-57_step-2-sandbox-carve-outs-implementation-and-review.md` |
| `2026-05-09_23-13_summary-codex-collab-orientation-and-overclaim-fix-plan.md` |
| `2026-05-10_00-34_summary-overclaim-fix-plan-review-cycle-1-revisions.md` |
| `2026-05-10_01-10_summary-overclaim-fix-cycles-2-3-committed.md` |
| `2026-05-10_01-47_summary-overclaim-fix-cycle-4-committed.md` |
| `2026-05-10_02-01_summary-overclaim-fix-cycle-5-committed.md` |
| `2026-05-10_20-37_summary-overclaim-fix-executed-and-pr-opened.md` |
| `2026-05-11_12-45_summary-pr128-merge-pr125-close-and-t20260511-01-filed.md` |

#### File-level handoff exclusions (13 handoffs left in monorepo as non-codex-collaboration)

All rows: classification `excluded`. Rationale: handoff describes work unrelated to codex-collaboration; not part of this project's record. Old path `docs/handoffs/<name>` or `docs/handoffs/archive/<name>` in monorepo, **not** copied to this repo. Composition: 1 page-turner + 5 handoff-plugin + 7 public-skills-repo.

| File | Subject |
|---|---|
| `docs/handoffs/2026-05-05_14-13_page-turner-browser-extension-design-and-plan.md` | page-turner browser extension |
| `docs/handoffs/archive/2026-04-10_17-45_handoff-no-commit-refactor-design-complete.md` | handoff plugin refactor |
| `docs/handoffs/archive/2026-04-10_18-16_implementation-plan-written-subagent-execution-queued.md` | handoff plugin implementation |
| `docs/handoffs/archive/2026-04-10_18-57_refactor-complete-and-e2e-smoke-tests-passed.md` | handoff plugin refactor |
| `docs/handoffs/archive/2026-04-10_19-00_subagent-execution-commit-1-landed-task-9-next.md` | handoff plugin commits |
| `docs/handoffs/archive/2026-04-10_19-45_commits-2-3-landed-paused-before-push.md` | handoff plugin commits |
| `docs/handoffs/archive/2026-05-06_23-59_checkpoint-claude-code-skills-spec-v2-review-pending.md` | public claude-code-skills repo |
| `docs/handoffs/archive/2026-05-07_00-18_checkpoint-claude-code-skills-spec-v3-review-pending.md` | public claude-code-skills repo |
| `docs/handoffs/archive/2026-05-07_01-00_claude-code-skills-spec-v4-committed-awaiting-re-review.md` | public claude-code-skills repo |
| `docs/handoffs/archive/2026-05-07_22-19_checkpoint-claude-code-skills-spec-v5-committed-awaiting-re-review.md` | public claude-code-skills repo |
| `docs/handoffs/archive/2026-05-07_22-35_build-plan-committed-execution-deferred.md` | public-skills-repo build plan |
| `docs/handoffs/archive/2026-05-07_23-08_spec-v6-and-plan-re-revision-execution-deferred.md` | public-skills-repo spec/plan |
| `docs/handoffs/archive/2026-05-08_00-28_public-skills-repo-build-complete-publish-deferred.md` | public-skills-repo build complete |


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

The exact reproducible command (run from `/Users/jp/Projects/active/claude-code-tool-dev/`):

```bash
rg -l "codex-collaboration|codex_collaboration|packages/plugins/codex-collaboration" \
   --type-add 'cfg:*.{toml,yaml,yml,json,cfg,ini,md}' \
   -t cfg -t py -t sh
```

Returns **143 files** at the current post-cleanup state (re-verified at manifest-revision time). The count is sensitive (±2) to the exact type filter:

- `rg -l "<pattern>"` with no type filter: 144
- The scoped form above: 143
- `rg -l "<pattern>" -tmd -tpy -ttoml -tyaml -tjson -tsh`: 143

The 2-file drift between the original 143 reading (commit `e71db48`) and a separate reviewer's 145 reading is within this filter-sensitivity tolerance and does not affect the substantive claim that no file in the monorepo claims current authority over codex-collaboration. The standard is zero stale live authority, not a single canonical count.

Classification (counts approximate, based on current grep):

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

Initial commit `b3c1f2c2bec593463853fc3142eba60bd23657dc` migrated docs
that still referenced monorepo paths internally
(`packages/plugins/codex-collaboration/server/*`,
`docs/superpowers/specs/codex-collaboration/*`).

Subsequent cleanup commits on `main`:

- `cfcb642` `chore: rewrite stale monorepo paths in active docs/skills/references` — Rewrote stale paths to standalone layout across active docs, `references/dialogue-turn-contract.md`, and `skills/shakedown-b1/SKILL.md`. Closed tickets, archived handoffs, design docs, and evidence JSON deliberately left snapshot-true.

- `e71db48` `docs(migration): finalize manifest with monorepo cleanup details` — Added redirected-paths list, residual-reference report, and links to monorepo cleanup commit `701952b8`.

- **This commit** (DoD follow-up batch addressing five reviewer findings):
  - **F1 — broken status doc links:** Status docs (`current-state.md`, `reconciliation-register.md`) referenced their own old names (`codex-collaboration-current-state.md`, `codex-collaboration-reconciliation-register.md`) and pointed at non-existent `../superpowers/specs/codex-collaboration/` paths. Bulk-sed rewrite applied across active docs (excluding closed tickets, archived handoffs, design-docs, and evidence). Also restored sed-introduced empty inline code spans on two surfaces.
  - **F2 — non-deterministic checksums:** Original aggregate-of-aggregate hashes used `find ... -exec shasum +` without sorting, so file order (and therefore the digest) varied across machines. Recomputed all aggregate hashes with `find ... | sort | shasum -a 256` (deterministic) and documented the method above.
  - **F3 — file-level inventory:** Added per-file rows for the 17 closed tickets, 4 active handoffs, 142 archived handoffs, and 13 excluded handoffs above.
  - **F4 — residual-reference count:** Re-ran the residual grep, documented the exact command and the type-filter sensitivity. Count still 143 with the documented scope; a reviewer's 145 is within ±2 filter-sensitivity tolerance.
  - **F5 — stale fixture paths in test data:** `tests/test_approval_router.py` carried `packages/plugins/codex-collaboration/tests/test_runtime.py` strings inside parsed-payload fixtures for `command_approval` parsing tests. The tests verify opaque preservation (so the path string is data, not a filesystem ref), but per `AGENTS.md` guidance to treat any code reference to old monorepo paths as a migration regression, the fixture strings were rewritten to `tests/test_runtime.py`. 7 affected tests still pass.

Also: 3 additional non-codex-collaboration handoffs were missed in the original copy-time filter (public-skills-repo `2026-05-07_22-35`, `2026-05-07_23-08`, `2026-05-08_00-28`) and trashed from this repo. The archived-handoff count therefore went from 145 (commit `b3c1f2c`) to 142 (this commit). The exclusion table above lists all 13 non-codex handoffs left in the monorepo.

## History Preservation

Git history preservation is **deferred**. The monorepo retains the commit history of the package; this repo starts fresh on `main` from the migration commit. If history preservation is later required:

1. Use `git filter-repo --path packages/plugins/codex-collaboration/ --path-rename packages/plugins/codex-collaboration/:` against a fresh monorepo clone.
2. Cherry-pick relevant docs commits (specs, status, tickets) into the rebased tree.
3. Replace this repo's initial-commit history with the filtered history (or merge into a new branch and rebase).

Until then, this manifest plus the source commit SHA in Provenance is the authoritative provenance bridge.
