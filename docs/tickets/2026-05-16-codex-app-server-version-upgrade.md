---
id: T-20260516-01
title: Track and execute Codex App Server version-pin upgrade
status: open
created: 2026-05-16
---

# Track and execute Codex App Server version-pin upgrade

## Current state

`server/codex_compat.py` pins `TESTED_CODEX_VERSION` and `MINIMUM_CODEX_VERSION` to `0.117.0`. The debt audit records local `codex-cli 0.130.0` on 2026-05-16, with a known 0.117 -> 0.125 schema delta already documented in `docs/specs/2026-04-29-codex-app-server-0.125.0-schema-delta.md`.

## Required gates

- Regenerate fixtures for the target Codex version.
- Produce a schema diff against `0.117.0`.
- Keep `tests/test_codex_wire_contract.py` passing against the target fixtures.
- Run live advisory and execution smoke checks.
- Verify `sandboxPolicy` / `permissionProfile` behavior explicitly.
- Update operator-facing docs and status/register rows.
- Decide whether `MINIMUM_CODEX_VERSION` moves with `TESTED_CODEX_VERSION` or stays lower with compatibility gates.

## Exit condition

The target version is either landed with passing contract/live evidence, or explicitly deferred with a recorded reason and a next review date.
