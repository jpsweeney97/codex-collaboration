# AGENTS.md

Instructions for AI coding agents working in this repository.

## Authority

This repository is the **sole authority** for `codex-collaboration` source, tests, specs, status, tickets, plans, and operational documentation. It was extracted from `claude-code-tool-dev` on 2026-05-11.

- Do **not** edit `codex-collaboration` files in `/Users/jp/Projects/active/claude-code-tool-dev/`. Those files are either demoted to historical snapshots or replaced with redirect stubs.
- Open tickets, current-state, and reconciliation register live only in this repo (`docs/status/`, `docs/tickets/`).
- For migration provenance, see [`docs/migration/monorepo-extraction-manifest.md`](docs/migration/monorepo-extraction-manifest.md).

## Authority Map

Behavioral claim ownership comes from [`docs/specs/spec.yaml`](docs/specs/spec.yaml).

| Authority owner | Owns | Primary artifact(s) |
|---|---|---|
| `foundation` | Architecture rules, domains, trust model, terminology | `foundations.md` |
| `contracts` | MCP surface, data models, typed responses, audit schema | `contracts.md` |
| `promotion-contract` | Promotion preconditions, state machine, rollback semantics | `promotion-protocol.md` |
| `advisory-policy` | Advisory lifecycle, widening/narrowing/rotation policy | `advisory-runtime-policy.md` |
| `recovery-contract` | Journal, audit-log behavior, crash recovery, concurrency | `recovery-and-journal.md` |
| `delivery` | Build sequence, deployment profile, compatibility, test strategy | `delivery.md` |
| `decisions` | Locked design decisions and open design questions | `decisions.md` |

`docs/status/` is a synthesis/routing layer. It can summarize current truth and reader guidance, but it does not outrank the owner documents above.

If a status document claim conflicts with the underlying owner documents or current code/tests, the underlying owner artifacts win.

## Repository Conventions

### Branches

Working branches are based on `main`:

| Pattern | Purpose |
|---|---|
| `feature/*` | New functionality |
| `fix/*` | Bug fixes |
| `chore/*` | Maintenance, cleanup |

Do not commit directly to `main` once initial setup is complete.

### Verification

Before claiming completion of a code change, run:

```bash
uv run pytest tests -q
uv run ruff check .
```

The pytest suite has 1099 tests and takes ~4 minutes. A standalone CI workflow runs the same set on every push.

### Filesystem Layout (for path-touching code)

The repository root is the plugin root. Source code is at the top level (no `packages/plugins/codex-collaboration/` prefix).

- `server/`, `scripts/`, `skills/`, `agents/`, `hooks/`, `references/` — all directly under repo root
- `docs/specs/` — spec tree (foundations, contracts, delivery, decisions, promotion-protocol, advisory-runtime-policy, recovery-and-journal, README, spec.yaml, evidence/, plus design-docs/)
- `tests/` — pytest suite + `tests/fixtures/` for JSON test data

If you find code that references monorepo paths (`packages/plugins/codex-collaboration/...` or `docs/superpowers/specs/codex-collaboration/...`), treat that as a migration regression and fix it. The smoke-setup script's `_repo_paths()` function and its tests are the canonical example of paths that already track the new layout.

### Tickets

- Active tickets live in `docs/tickets/`.
- Closed tickets move to `docs/tickets/closed-tickets/` with frontmatter updated to `status: closed` and a `closed_date`.
- Tickets that predate `codex-collaboration` (cross-model or context-injection era) are not tracked here — they remain in the source monorepo as predecessor history.

### Handoffs

Session handoffs live in `docs/handoffs/`. Older handoffs migrate to `docs/handoffs/archive/`.

**Policy (post-extraction `.gitignore` sealed at commit `3563bb3`; active-handoff reclassification in this revision):**

- **Sealed migration corpus (142 archived handoffs)** — the markdown files in `docs/handoffs/archive/` migrated from the monorepo are tracked in git as canonical historical record. See `docs/migration/monorepo-extraction-manifest.md` for the per-file inventory. Do not delete, rewrite, or rename these files; they are the immutable migration snapshot.
- **Migrated active handoffs are local-only working memory** — the 4 migrated handoffs at `docs/handoffs/` root (the ones outside `archive/`) were tracked at extraction time, then explicitly untracked via `git rm --cached` because they are legitimately active session handoffs eligible for future `/load`, not sealed historical record. They remain on disk locally under the same policy as new session handoffs.
- **New session handoffs are local-only** — `.gitignore` ignores `docs/handoffs/` going forward. The rule does not untrack the sealed archived corpus (already-tracked files survive a new gitignore rule); it only blocks new additions. Handoff plugin outputs from `/save`, `/load`, and the `.session-state/` directory are local working memory per the plugin contract. Do not `git add -f` them in routine sessions.
- **Promotion procedure (exceptional only)** — if a specific local-only handoff must become project record, promote it explicitly: (1) `git add -f docs/handoffs/<file>`, (2) commit with a `docs(handoffs):` message stating the promotion rationale, (3) add a row in `docs/migration/monorepo-extraction-manifest.md` (or a follow-on durable record) so the addition is auditable. Default: do not promote; distill durable learnings via `/distill` into `docs/learnings/` instead.

## Migration-Era Cautions

- The package's MCP tool prefix is `mcp__plugin_codex-collaboration_codex-collaboration__*`. Hook matchers, skill `allowed-tools`, and agent `tools` frontmatter must use this exact prefix.
- The original package shipped with `version = "0.1.0"` in `pyproject.toml` while plugin manifest declared `version = "0.2.0"`. The mismatch was inherited from the monorepo; if you bump the plugin, update both.
- Tests assume `pyproject.toml`'s `[tool.pytest.ini_options]` adds the repo root to `pythonpath`. Direct imports like `from server.runtime import ...` rely on this.

## Workflow Notes

- Prefer editing existing files to creating new ones.
- Don't add `__pycache__`, `.pytest_cache`, `.ruff_cache`, or `.mypy_cache` to git — they are gitignored.
- When a change touches MCP tool names, hook matchers, or skill frontmatter, verify all three locations stay in sync.
