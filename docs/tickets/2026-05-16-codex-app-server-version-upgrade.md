---
id: T-20260516-01
title: Track and execute Codex App Server version-pin upgrade
status: open
created: 2026-05-16
---

# Track and execute Codex App Server version-pin upgrade

## Current state

`server/codex_compat.py` pins `TESTED_CODEX_VERSION` and `MINIMUM_CODEX_VERSION` to `0.117.0`. The debt audit records local `codex-cli 0.130.0` on 2026-05-16, with a known 0.117 -> 0.125 schema delta already documented in `docs/specs/2026-04-29-codex-app-server-0.125.0-schema-delta.md`.

## Dependent observed failures (2026-05-18)

Live delegation under local `codex-cli 0.130.0` reproduces a
probe-independent worker failure that gates downstream acceptance work:

- Two delegations — `2b5e8c9c-81d6-43b3-90b4-49653e998f31` (a credential
  probe) and `7a5478c9-02c2-48f4-9210-2d291de38f59` (a no-op control: write
  one file, no out-of-worktree reads) — both failed identically with
  `worker_failed_before_capture`. The sandbox policy was built, then the
  worker died before the execution agent ran any command (`changed_files:
  []`; detail "Delegation outcome could not be confirmed after recovery").
- The no-op control with zero out-of-worktree access reproduces it, so the
  failure is **probe-independent** — not a sandbox/credential-boundary
  signal.
- This `0.117.0`-pin-vs-live-`0.130.0` lane is the best existing owner and
  the likely confound; root cause is **not proven**. Confirm or repair during
  the rebaseline (or a focused worker-startup RCA), capturing evidence under
  the "Run live advisory and execution smoke checks" gate below.

Gates downstream: **T-20260429-01** AC#1 (comparable live `/delegate` smoke,
avoidable-friction ≤2) and AC#2's behavioral half (runtime credential-boundary
enforcement probe) are both blocked on a usable live delegation lane under the
target Codex version. See that ticket's "AC#2 verification evidence
(2026-05-18)" block. Both jobs were discarded; session instrumentation
reverted.

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
