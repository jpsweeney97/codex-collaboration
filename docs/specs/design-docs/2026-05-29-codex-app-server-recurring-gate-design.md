# Codex App Server Recurring Drift Gate — Design

**Date:** 2026-05-29
**Status:** Draft (design) — non-normative until accepted
**Owner docs (on acceptance):** [`delivery.md`](../delivery.md) §Compatibility Policy (normative edits: version policy, scheduled-gate cadence, test strategy); a follow-on Decision Record under [`docs/decisions/`](../../decisions/) for the `MINIMUM_CODEX_VERSION`-vs-`TESTED_CODEX_VERSION` floor policy.
**Prerequisite (landed):** Tier 1b installed-runtime guard — PR #15, merge commit `6d4a481`.
**Related tickets:** [T-20260516-01](../../tickets/2026-05-16-codex-app-server-version-upgrade.md) (version upgrade), [T-20260516-02](../../tickets/2026-05-16-codex-app-server-contract-versioning.md) (contract-version assertion boundary), [T-20260429-02](../../tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md) (unsupported ServerRequest reachability).

This document is **non-normative**. It defines the recurring drift gate's architecture and the decisions it locks. On acceptance, the normative claims graft into the owner docs above; this doc explains *why* and records the design boundaries. It **defines the gate; it does not rebaseline Codex** (see [Out of scope](#out-of-scope)).

## Problem

`codex-collaboration` talks to OpenAI Codex App Server over JSON-RPC. Codex releases independently and frequently, and the repo's tested baseline lags it. The repo already has compatibility machinery — vendored schema fixtures, contract tests, a live method-surface probe, manual rebaseline tickets — but every one of those checks is **pull-based and human-triggered**, not **push-based and recurring**. Nothing notices, on its own, when Codex moves.

The concrete failure mode this gate closes:

- The wire-contract suite validates runtime payloads against the **vendored** schema keyed by `TESTED_CODEX_VERSION` in [`server/codex_compat.py`](../../../server/codex_compat.py). When the installed binary outruns the tested baseline, those tests keep passing against the *stale* fixture — drift goes silent.
- This is not hypothetical. As of this design: tested baseline `0.117.0`, npm `latest` `0.135.0`, the operator's installed binary `0.135.0` — an 18-minor gap. The repo's own audit recorded installed as `0.130.0` on 2026-05-16; twelve days later it was `0.135.0` and no record updated. The tracking decayed the moment no human re-ran it.

A correct gate must respect the three distinct levels of proof, which the existing machinery already embodies:

| Proof | "Question" | Mechanism | What it does **not** prove |
|---|---|---|---|
| Doors exist | Are the method names still there? | live probe (`codex app-server generate-json-schema`) / schema surface | that the payloads still fit, or that workflows run |
| Keys fit | Do our runtime payloads still validate? | contract tests vs **vendored** fixture | anything about a version newer than the fixture |
| Workflow works | Does delegation/dialogue actually run, and is containment intact? | authenticated live smokes | — |

A newer Codex passing a method probe is **not** the same as this repo being rebaselined to it. Method probing proves the doors. Fixtures + contract tests prove our keys fit *those* doors. Live smokes prove the workflow. The gate exists to keep those distinct and make the gap between them visible before it becomes operational confusion.

## Goal

A recurring gate that detects when Codex App Server has advanced beyond the version this repo has intentionally tested, and produces enough information to **route** the work (regenerate fixtures, compare schemas, run contract tests, run live smokes, decide version policy, update docs/tickets/status). It answers: what is the tested baseline; what is current; what changed; is the change harmless/relevant/blocking; and has the repo recorded a rebaseline decision or is it silently stale.

## Two axes (why the gate has tiers)

"Local vs CI" conflates two independent checks with different homes:

1. **Internal consistency** — does the repo agree with itself? (fixture dir ↔ `TESTED_CODEX_VERSION`, manifest ↔ constants, prose ↔ constants). Needs **no** Codex binary — pure source inspection. → Tier 1a, every push.
2. **World-moved** — has Codex advanced past the tested baseline? Needs an external reference. Two sub-signals, both real and both kept:
   - **installed-vs-tested** — per-machine, what an *operator* actually runs (today `0.135` vs `0.117`). → Tier 1b (landed), fires where a binary is present.
   - **latest-release-vs-tested** — machine-independent, authoritative "the protocol moved." → Tier 2, scheduled.

The recurring gate proper is **push-based**, so its home is a **scheduler** (GitHub Actions `schedule:`), the only place a single shared observation produces a single shared, dated artifact. A session-start nudge would still be pull-based. Tier 1a/1b are the synchronous consistency mirror and the operator-local signal; Tier 2 is the recurring sentinel; Tier 3 is the human rebaseline tier.

## Tier 1a — Repo consistency

Source-only, deterministic, **no Codex install**. Runs on push/PR (extend the existing [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml)) and locally via `scripts/check`. Checks:

- **Fixture-dir ↔ constant**: `tests/fixtures/codex-app-server/<TESTED_CODEX_VERSION>/` exists and carries the required schema files.
- **Manifest ↔ constants**: the generated `required-methods.json` for the active fixture matches `REQUIRED_METHODS` / `OPTIONAL_METHODS`.
- **Prose ↔ constants** (closes the "rule-d is prose-only" gap): `delivery.md` §Compatibility Policy currently states `Baseline version: codex-cli 0.117.0` as prose with no machine link to the constant. Make this checkable — either a regex extraction compared to `TESTED_CODEX_VERSION`, or move the version into machine-readable frontmatter — so docs can't claim a baseline the code doesn't hold.
- **Extra fixture dirs — warn-first**: a fixture directory newer than `TESTED_CODEX_VERSION` (today `0.130.0` exists, unreferenced, from in-progress work) is **not** a hard failure. There is no marker mechanism today; inventing one and enforcing it would red-flag legitimate work. Introduce a per-dir `.status.json` (`{"status": "in_progress" | "ready" | "blocked", ...}`), ship the check as a **warning/report first**, and only escalate "unmarked extra dir → error" once markers exist and are populated.

Not a new check: `MINIMUM_CODEX_VERSION <= TESTED_CODEX_VERSION` is **already** enforced by `test_minimum_not_above_tested` in [`tests/test_codex_compat.py`](../../../tests/test_codex_compat.py). Tier 1a documents this coverage; it does not duplicate it.

## Tier 1b — Installed-runtime guard

**Landed** (PR #15, merge commit `6d4a481`). `TestGetCodexVersion.test_installed_matches_tested_baseline` in [`tests/test_codex_compat_live.py`](../../../tests/test_codex_compat_live.py), inheriting that module's `skipif(no binary)` + `slow` gating:

- **No binary** (binary-less CI) → **skips**. Adds no Codex-install prerequisite to ordinary CI.
- **Binary present and version ≠ `TESTED_CODEX_VERSION`** → **fails loudly**, naming the rebaseline path.

This is the **installed-vs-tested** axis — the operator's immediate local mismatch. It is distinct from Tier 2's latest-vs-tested: a containment-affecting version that an operator already runs but that is not yet npm `latest` is invisible to Tier 2 and caught only here. Also de-hardcoded the `CapturingClient` `initialize` `userAgent` to `f"codex-cli {TESTED_CODEX_VERSION}"` so the mock tracks the constant.

## Tier 2 — Scheduled CI drift analyzer

A new GitHub Actions workflow on `schedule:` (**daily**) plus `workflow_dispatch:`.

**Cadence — daily.** Observed Codex release velocity is ~0.4 stable releases/day (`0.130`→`0.135` in 12 days), with an `alpha` (`0.136.0-alpha.1`) already staged. Weekly would queue 5–14 versions per run; daily keeps the rolling issue close to reality at negligible CI cost. (Confirm at review.)

Sequence (all steps verified to run **unauthenticated, no network beyond npm/registry**):

1. Read `TESTED_CODEX_VERSION` from [`server/codex_compat.py`](../../../server/codex_compat.py); read current release from **npm `dist-tags.latest`** (`npm view @openai/codex dist-tags.latest`) — the authoritative source, matching the `codex --version` string exactly. **Ignore `alpha`** unless a `workflow_dispatch` input requests it.
2. If `latest <= TESTED` → no drift; ensure the rolling issue is closed (see [Issue lifecycle](#issue-lifecycle)); exit GREEN.
3. Install: `npm install -g @openai/codex@<latest>`. The package uses per-platform `optionalDependencies`, which npm auto-resolves on `ubuntu-latest` (linux-x64). **Post-install, verify `codex --version` == `codex-cli <latest>`** before proceeding.
4. Generate the schema **bare, without `--experimental`** (matching `scripts/regenerate_schema.sh`, which generates fixtures this way), and apply the same canonical JSON key ordering the script uses, so the diff is apples-to-apples and deterministic.
5. Diff via [`scripts/compare_app_server_schemas.py`](../../../scripts/compare_app_server_schemas.py) `--old-root tests/fixtures/codex-app-server/<TESTED> --new-root <generated>`.
6. **Classify** the diff (see [Classifier ceiling](#classifier-ceiling)).
7. Publish the generated schema bundle + diff JSON + classification as workflow artifacts; create/update one rolling issue; write a job summary.

**Prerequisites the analyzer needs that CI lacks today:**

- **Node/npm setup** — current CI only sets up Python (`setup-uv`); the scheduled job needs a Node toolchain step.
- **`permissions: { issues: write }`** — current `ci.yml` declares no permissions block; the default `GITHUB_TOKEN` is read-only on issues, so `gh issue` would 403 and turn the "success" outcome RED.
- **Comparator hardening** — `compare_app_server_schemas.py` hardcodes its file inventory and raises `SystemExit` on a missing file. A release that adds/removes bundle files would crash with a traceback instead of a diff. The analyzer requires the comparator to **emit a `diagnostics` section** (`unexpected_files`, `missing_files`, `parse_errors`) instead of crashing. This is the first build step (see [Build sequence](#build-sequence)).

## Classifier ceiling

The classifier is `classify_drift(report: dict) -> {label, action, confidence}`, a pure function over the comparator output. Its labels are bounded:

> CI may emit `harmless`, `relevant`, `needs-live-review`, or `unclassified`. **It must never emit `safe-to-upgrade` from schema alone.**

Schema diffing proves protocol *surface* change; it cannot prove runtime **containment**. The `0.130` `readOnlyAccess`/`workspaceWrite` permission regression was offline-clean yet live-broken — schema-invisible. Only Tier 3b can support upgrade confidence.

Rules:

- **ClientRequest additions** (plugin *sends*): `harmless`/`relevant` — additive, the plugin opts in.
- **ClientRequest removals or shape changes** to runtime-consumed methods: `relevant` → `needs-live-review`.
- **ServerRequest additions** (plugin must *receive/handle*): default `needs-live-review` or `unclassified`. Reachability cannot be answered from schema; it is owned by [T-20260429-02](../../tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md). Until that produces a reachability registry, new ServerRequest methods surface explicitly as `unclassified`, never silently passed.
- **Permission / sandbox / approval shape deltas**: `needs-live-review` — the schema-invisible containment class.
- **Unknown bundle files / parse failures**: `unclassified`, carried from the comparator `diagnostics` section.

`unclassified` is an explicit, non-silent state — it routes to human review, it does not mean "fine."

## Issue lifecycle

- **Permissions**: the workflow declares `permissions: { issues: write }`.
- **One rolling issue**, found idempotently by a fixed **label** (e.g. `codex-drift`) and deterministic title — not a new issue per run. The problem is singular ("baseline is stale"), not per-release.
- **Per-run update**: append a timestamped comment with the version delta and classification; keep the issue **severity label/title mutable**, reflecting the highest current classification.
- **Auto-close on resolution**: when `TESTED_CODEX_VERSION >= npm latest` (the rebaseline caught up), post a "drift resolved" comment and close the issue. No zombie issue, no duplicates.
- **Job exit policy**: ordinary drift detection is a **successful routed outcome** → job GREEN. The job goes RED **only** for analyzer failure (latest unresolved, install/generate/diff failed, publication failed) or an explicit *blocking-escalation policy* (open question — should e.g. a `needs-live-review` removal of a runtime-consumed method fail the job?). Drift itself never reds the loop.
- **Notification**: write `$GITHUB_STEP_SUMMARY` with the classification and a link to the issue, so a GREEN run is still visible — a green job with a silent issue is an operator blind spot.

## Tier 3a — Offline rebaseline feasibility

No auth, runnable in CI or locally. The early feasibility gate before any live turns are spent:

- Generate target fixtures: `scripts/regenerate_schema.sh <target>`.
- Run the comparator + classifier against the target.
- Run contract tests against the **target** fixture (point `TESTED_CODEX_VERSION` at the candidate and run the wire-contract suite).
- Verify the `required-methods.json` manifest, `.status.json` markers, and prose/version docs.

This maps onto [`delivery.md`](../delivery.md) §Version Upgrade Workflow steps 2–4.

## Tier 3b — Live proof

Authenticated; **local/manual**, not unattended CI (auth lives in `CODEX_HOME`, which CI does not have):

- Authenticated advisory / dialogue / delegation smokes.
- Permission / sandbox / containment probes — the schema-invisible class the classifier defers here.

This is the **only** tier allowed to support "runtime-safe enough to promote" / to justify moving the floor. Maps onto `delivery.md` §Version Upgrade Workflow step 5 plus containment verification.

## Decision record

**Open decision, not resolved here:** does `MINIMUM_CODEX_VERSION` move in lockstep with `TESTED_CODEX_VERSION`, or stay a lower compatibility floor (a tolerance window)? This is load-bearing — Tier 1a's prose↔constant consistency and any future widening of the floor depend on the intended relationship being recorded, and today no durable record states it.

Route it to a follow-on **Decision Record** at `docs/decisions/<date>-codex-version-floor-policy.md` (ADR format per [`2026-05-16-security-hook-guard-extension.md`](../../decisions/2026-05-16-security-hook-guard-extension.md)), produced as an exit condition of the rebaseline workflow ([T-20260516-01](../../tickets/2026-05-16-codex-app-server-version-upgrade.md)). This spec records the **need and the home**; it does not pick the policy.

## Test strategy and seams

Follow the repo's existing seam convention: **module-level `@patch` of `subprocess` at the test boundary** (as `tests/test_codex_compat.py` does for `get_codex_version`), **not** callable injection threaded through call sites. Concretely:

- `classify_drift` is a pure function over the comparator dict → unit-test with synthetic diff fixtures (additive ClientRequest, ServerRequest addition, permission-shape delta, unknown file → `unclassified`).
- Comparator hardening → unit-test a synthetic bundle missing/adding a file and assert a `diagnostics` section is emitted, not a crash.
- The npm-latest lookup and codex install are patched at the subprocess boundary so the analyzer logic is testable offline.

## Build sequence

For the follow-on implementation plan, **not** this spec's scope, and **no Tier 2 code until this spec is accepted**:

1. Comparator hardening (diagnostics instead of crash) — prerequisite for everything downstream.
2. `classify_drift` + ceiling, with synthetic-diff unit tests.
3. Tier 1a consistency checks + `.status.json` marker format (warn-first).
4. Scheduled workflow (Node setup, `issues: write`) + rolling-issue routing + job summary.
5. Docs/ADR/status updates: graft normative claims into `delivery.md`, create the floor-policy ADR, update `docs/status/`.

Tier 1b is already done.

## Out of scope

This spec **defines the gate**; it does **not** rebaseline Codex. The stale `chore/t-20260516-01-version-rebaseline` branch and the actual `0.117`→`0.135` rebaseline are noted as relevant context only — the rebaseline itself is [T-20260516-01](../../tickets/2026-05-16-codex-app-server-version-upgrade.md) work, separate from this design branch.

## Open questions for review

- **Cadence**: daily confirmed? (recommended given release velocity)
- **Blocking-escalation policy**: should any classification ever fail the scheduled job, or is GREEN-with-issue always the right outcome for detected drift?
- **Floor policy**: the `MINIMUM`-vs-`TESTED` ADR (deferred to its own decision record).
- **Marker format**: the `.status.json` schema for extra fixture dirs.
