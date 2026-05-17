# codex-collaboration

Codex advisory consultation, durable dialogue, and isolated delegation via direct JSON-RPC to the Codex App Server.

> **Authority:** This repository is the **sole authority** for `codex-collaboration` source, tests, specs, status, tickets, and operational documentation. The repository was extracted from `claude-code-tool-dev` on 2026-05-11; see [docs/migration/monorepo-extraction-manifest.md](docs/migration/monorepo-extraction-manifest.md) for provenance and verification evidence.

## Repository Layout

```
.
├── server/                  # MCP server, runtime, delegation controller, dialogue
├── skills/                  # Plugin skills (consult-codex, delegate, dialogue, etc.)
├── agents/                  # Subagents (shakedown-dialogue, dialogue-orchestrator)
├── scripts/                 # Plugin scripts (bootstrap, guards, smoke setup)
├── hooks/                   # Hook configuration (hooks.json)
├── references/              # Reference material (tag grammar, dialogue contract)
├── tests/                   # pytest suite (1172 tests) + JSON fixtures
├── .mcp.json                # MCP server registration
├── .claude-plugin/          # Plugin manifest (plugin.json)
├── pyproject.toml           # Standalone Python project
├── docs/
│   ├── specs/               # Authoritative specs (foundations, contracts, delivery, ...)
│   ├── status/              # current-state.md + reconciliation-register.md
│   ├── tickets/             # Active + closed tickets
│   ├── architecture/        # Architecture notes (App Server rebaseline, etc.)
│   ├── audits/              # Audit reports
│   ├── assessments/         # Drift reports, verified state assessments
│   ├── decisions/           # Architecture Decision Records
│   ├── plans/               # Operational plans
│   ├── handoffs/            # Session handoffs (+ archive/)
│   ├── evidence/            # Evidence artifacts (separate from spec evidence/)
│   └── migration/           # Migration manifest (provenance)
└── .github/workflows/       # CI
```

## Prerequisites

| Requirement | Purpose | Check |
|-------------|---------|-------|
| Claude Code | Plugin host | `claude --version` |
| Codex CLI 0.117.0+ | Advisory runtime | `codex --version` |
| Python 3.11+ | MCP server and hooks | `uv run python --version` |
| uv | Package management | `uv --version` |

**Authentication:** Run `codex login` or set `OPENAI_API_KEY`.

## Local Development

This repository is now standalone — clone it and develop from its root.

```bash
git clone <this-repo> /Users/jp/Projects/active/codex-collaboration
cd /Users/jp/Projects/active/codex-collaboration
uv sync
uv run pytest tests -q              # fast inner loop; excludes slow live-runtime tests
uv run pytest tests -q -m ""        # full marker-inclusive suite
uv run ruff check .
```

The plugin root is the repository root. `.mcp.json` and `hooks/hooks.json` use `${CLAUDE_PLUGIN_ROOT}` which Claude Code resolves to the directory containing `.claude-plugin/plugin.json` — i.e., this repo's root.

## Install as a Claude Code Plugin

### From this repo (plugin-dir, for local development)

```bash
claude --plugin-dir /Users/jp/Projects/active/codex-collaboration
```

### From a marketplace

```bash
/plugin install codex-collaboration@<marketplace>
```

## Smoke Test (after install)

1. **Check plugin loaded:**
   ```
   /mcp
   ```
   Look for `codex-collaboration` in the MCP server list.

2. **Run status check:**
   ```
   /codex-status
   ```
   Should return Codex version, auth status, and method availability.

3. **Run a consultation:**
   ```
   /consult-codex What is the purpose of this repository?
   ```
   Should perform a `codex.status` preflight, then dispatch a consultation and relay the result.

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| `codex-status` | `/codex-status` | Runtime health, auth, version diagnostics |
| `consult-codex` | `/consult-codex <question>` | One-shot advisory consultation with status preflight |
| `delegate` | `/delegate` | Isolated delegation with worktree execution, escalation handling, and promotion |
| `codex-review` | `/codex-review` | Code review via the advisory runtime |
| `codex-analytics` | `/codex-analytics` | Analytics views from audit and outcome streams |
| `dialogue` | `/dialogue` | Multi-turn durable dialogue with Codex |
| `shakedown-b1` | `/shakedown-b1` | Pre-benchmark integration shakedown |

## Architecture

The plugin runs a stdio MCP server (`scripts/codex_runtime_bootstrap.py`) that exposes tools for advisory consultation, durable dialogue, and isolated delegation. The server communicates with the Codex App Server via JSON-RPC (`server/runtime.py`). Delegation runs in isolated git worktrees with per-request approval routing and artifact-verified promotion (`server/delegation_controller.py`).

Dialogue state (lineage, journal, turn metadata) is session-scoped. The session identity is published by a `SessionStart` hook and read lazily on the first dialogue tool call.

## Safety Substrate

The plugin enforces a fail-closed credential scanning chain on all content-bearing Codex collaboration tool calls (`codex.consult`, `codex.dialogue.start`, `codex.dialogue.reply`, `codex.delegate.start`, `codex.delegate.decide`):

- **Hook guard** (`scripts/codex_guard.py`): `PreToolUse` hook validates raw tool input before the MCP server processes it. Exits 2 (block) on parse failure, malformed input, or internal error.
- **Tool-input safety policy** (`server/consultation_safety.py`): Per-tool scan policies with field-aware traversal and tiered credential scanning.
- **Secret taxonomy** (`server/secret_taxonomy.py`): Tiered pattern definitions — strict (hard-block), contextual (block unless placeholder bypass), broad (shadow/telemetry).
- **Consultation profiles** (`server/profiles.py`): Named profiles resolving posture, turn budget, reasoning effort, sandbox, and approval policy.
- **Learning retrieval** (`server/retrieve_learnings.py`): Tag/keyword-matched learnings injected into advisory briefings via the context assembly pipeline.
- **Analytics emission**: `OutcomeRecord` persisted to `analytics/outcomes.jsonl` for consult and dialogue outcomes.

## Limitations

- **Concurrent sessions unsupported:** Two simultaneous Claude sessions sharing this plugin can collide on the session identity file and, in the promotion path, can both pass a pre-apply `HEAD == base_commit` check before one applies changes. Single-session use only for the current rollout target. If overlap is suspected, stop all sessions, inspect `git status`, keep only one session running, and re-run the relevant status or promotion command. The SessionStart hook emits a weak warning when it sees a recent different `session_id`, but this is only startup-overlap detection, not a cross-process promotion lock.
- **No phased profiles:** Profiles with `phases` (e.g., `debugging`) are rejected until phase-progression support is implemented.

## Configuration

The plugin reads the following environment variables at module load. Plugin restart is required for changes to take effect.

| Variable | Default | Description |
|---|---|---|
| `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS` | `900` (15 min) | TTL for parked approval requests in `command_approval` and `file_change` flows. Operator decides arriving after this window are rejected as `job_not_awaiting_decision`. Must be a positive number; non-numeric or non-positive values fall back to the default with a warning logged. Useful for diagnostic-style operator workflows that exceed the default budget under per-cycle review tempo. |
| `CODEX_COLLAB_LOG_LEVEL` | `WARNING` | Root logging level for the bootstrap process. Use `INFO` for startup diagnostics such as the resolved plugin data path; invalid values fall back to `WARNING`. |

## Tests

```bash
uv run pytest tests -q              # fast inner loop; excludes slow live-runtime tests
uv run pytest tests -q -m ""        # full marker-inclusive suite (CI uses this)
uv run pytest tests/test_runtime.py # single file
uv run ruff check .                 # lint
```

A local convenience script is also provided:

```bash
./scripts/check
```

## Authoritative Documents

| Document | Purpose |
|----------|---------|
| [`docs/status/current-state.md`](docs/status/current-state.md) | Reader entry point for current project state |
| [`docs/status/reconciliation-register.md`](docs/status/reconciliation-register.md) | Open / unreconciled work |
| [`docs/specs/spec.yaml`](docs/specs/spec.yaml) | Authority map for behavioral claims |
| [`docs/specs/foundations.md`](docs/specs/foundations.md) | Architecture rules, domains, trust model |
| [`docs/specs/contracts.md`](docs/specs/contracts.md) | MCP surface, data models, typed responses |
| [`docs/specs/delivery.md`](docs/specs/delivery.md) | Build sequence, deployment profile, compatibility |
| [`docs/specs/decisions.md`](docs/specs/decisions.md) | Locked design decisions and open design questions |
| [`docs/specs/promotion-protocol.md`](docs/specs/promotion-protocol.md) | Promotion preconditions, state machine, rollback |
| [`docs/specs/advisory-runtime-policy.md`](docs/specs/advisory-runtime-policy.md) | Advisory lifecycle policy |
| [`docs/specs/recovery-and-journal.md`](docs/specs/recovery-and-journal.md) | Journal, audit log, crash recovery, concurrency |
| [`docs/migration/monorepo-extraction-manifest.md`](docs/migration/monorepo-extraction-manifest.md) | Provenance and migration evidence |

## License

MIT
