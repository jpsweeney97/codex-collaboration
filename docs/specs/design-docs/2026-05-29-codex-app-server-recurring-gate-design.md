# Codex App Server Recurring Drift Gate — Design

**Date:** 2026-05-29
**Status:** Draft (design) — non-normative until accepted
**Revision:** Revised after round-1 adversarial-review adjudication (2026-05-29). Adds an [Acceptance Blockers](#acceptance-blockers-and-phase-0-prerequisites) gate and tightens the classifier contract, comparator hardening, issue lifecycle, and CI mechanics.
**Owner docs (on acceptance):** [`delivery.md`](../delivery.md) §Compatibility Policy (normative edits: version policy, scheduled-gate cadence, test strategy; also the normative home for the `MINIMUM_CODEX_VERSION`-vs-`TESTED_CODEX_VERSION` floor relationship). A follow-on Decision Record under [`docs/decisions/`](../../decisions/) carries the floor-policy *rationale* only — reachable by a one-line pointer from `delivery.md` and a cross-reference in [`decisions.md`](../decisions.md) §Open Questions — and is rationale-of-record, not the authority (see [Decision record](#decision-record)).
**Prerequisite (landed):** Tier 1b installed-runtime guard — PR #15, merge commit `6d4a481`.
**Related tickets:** [T-20260516-01](../../tickets/2026-05-16-codex-app-server-version-upgrade.md) (version upgrade), [T-20260516-02](../../tickets/2026-05-16-codex-app-server-contract-versioning.md) (contract-version assertion boundary), [T-20260429-02](../../tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md) (unsupported ServerRequest reachability).

This document is **non-normative**. It defines the recurring drift gate's architecture and the decisions it locks. On acceptance, the normative claims graft into the owner docs above; this doc explains *why* and records the design boundaries. It **defines the gate; it does not rebaseline Codex** (see [Out of scope](#out-of-scope)).

## Acceptance Blockers and phase-0 prerequisites

This draft is **not yet ready to hand to implementation planning**. Two distinct gates apply — conflating them is the error this section fixes:

- **Spec-acceptance gate** — the design must *commit to* the B1–B5 approaches below. That is a decision, recorded here; it is what acceptance means.
- **Phase-0 implementation gate** — B1–B3 (comparator nested-permission visibility, the `diagnostics` taxonomy, the closed-`Literal` classifier) must be *implemented and tested before* any scheduled-workflow or issue-routing code (B4/B5) is written — see [Build sequence](#build-sequence).

Items are ordered by severity and supersede the looser [Open questions for review](#open-questions-for-review). Each is elaborated in the referenced section.

- **B1 (critical) — The comparator cannot see the regression class the gate exists to catch.** The classifier rule "permission/sandbox/approval shape deltas → `needs-live-review`" has *no input to fire on*: `compare_app_server_schemas.py`'s `shape_summary` reads only top-level `properties`, and `SandboxPolicy` is not among its tracked nested definitions, so the `0.130` `readOnlyAccess`/`workspaceWrite` regression yields only `equal: false` — indistinguishable from a description-string edit. The gate would classify the exact break it was built to catch as harmless. **Resolution:** the comparator must descend into nested permission/sandbox/approval definitions (`/definitions/SandboxPolicy` variants, `readOnlyAccess`, `workspaceWrite`, permission-profile surfaces) and emit explicit permission-delta fields; the classifier must key off those fields, never infer containment risk from `equal: false`. → [Tier 2 comparator hardening](#tier-2--scheduled-ci-drift-analyzer), [Classifier contract](#classifier-contract).
- **B2 (high) — A removed runtime-consumed file must escalate, not downgrade.** Today a missing consumed schema file is a `read_json` `SystemExit` → RED. Folding missing files blindly into `diagnostics → unclassified → GREEN-with-issue` would *invert* a safety signal. **Resolution:** the diagnostics taxonomy must distinguish `missing_consumed_file` / `missing_tracked_file` / `unexpected_file` / `parse_error`; a missing **consumed or permission-sensitive** file routes to `needs-live-review`, not generic `unclassified`. → [Tier 2 comparator hardening](#tier-2--scheduled-ci-drift-analyzer), [Classifier contract](#classifier-contract).
- **B3 (high) — The `safe-to-upgrade` ceiling must be structural, not prose.** The "never emit `safe-to-upgrade` from schema alone" invariant is the gate's one load-bearing safety property and is currently a sentence. **Resolution:** `classify_drift`'s label must be a closed enum (Python `Literal`) lacking `safe-to-upgrade`, with a test that exhaustively asserts the forbidden label is unreachable and that permission deltas route to `needs-live-review`. → [Classifier contract](#classifier-contract).
- **B4 (high) — The scheduled sentinel decays exactly when it is needed.** GitHub disables `schedule:` workflows after ~60 days without repository activity — i.e. during the quiet periods this gate exists to cover, reproducing the very "tracking decayed when no human re-ran it" failure one layer up. **Resolution (v1):** a **Tier 1a push/PR check** — which runs regardless of schedule state — warns/fails when no successful drift-analyzer run has been recorded within `N` days, with manual `workflow_dispatch` as the recovery path. The rolling issue may *display* stale state but **cannot be the detector**: a disabled workflow can't update its own issue. → [Tier 2](#tier-2--scheduled-ci-drift-analyzer), [Issue lifecycle](#issue-lifecycle).
- **B5 (medium) — CI mechanics.** `permissions` must be `{ contents: read, issues: write }` (any `permissions:` block drops unlisted scopes to `none`); the `codex-drift` label must be **create-or-fallback**, never a post-analysis RED on a missing label; the rolling-issue workflow needs a `concurrency:` group so overlapping cron/`workflow_dispatch` runs don't race the single issue; and per-run comments must be **delta-gated** (comment only when the version delta or classification changes) so an unchanged `latest` doesn't spam the issue daily. → [Tier 2](#tier-2--scheduled-ci-drift-analyzer), [Issue lifecycle](#issue-lifecycle).

**Recalibrated out of the blocker set (from round-1 review):** the floor-policy ADR routing is a one-line pointer cleanup, not an authority violation (see [Decision record](#decision-record)); the `regenerate_schema.sh` `rm -rf` objection is **withdrawn** — both targets are self-created `mktemp -d` dirs, and the global "never run `rm -rf`" rule governs direct shell actions, not invoking an already-safe maintenance script; and **blocking-escalation is not open for v1** — drift stays GREEN-with-issue unless the analyzer itself fails (see [Issue lifecycle](#issue-lifecycle)).

**Deferred — recorded, not addressed in this revision** (tracked for the next scrutiny pass, deliberately out of the current patch scope): a future **prerelease investigation mode** (a separate workflow that would preserve raw npm versions and avoid `SemVer` suffix stripping — alpha is out of v1 scope, see [Out of scope](#out-of-scope)); routing the `foundation` (compatibility invariant) and `contracts` (classifier label enum / ServerRequest rule) claims to their owner docs alongside `delivery.md`; the `delivery.md` multi-surface version-prose problem (the baseline appears in three places / two formats, with `MINIMUM`/`TESTED` conflated) that complicates the Tier 1a prose↔constant check; npm-install pinning / supply-chain exposure; `required`-array sort stability for deterministic classifier input; the moving-target auto-close condition and the Tier 1b-RED vs Tier 2-GREEN disagreement for the same drift; and cron UTC time-of-day selection.

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

A new GitHub Actions workflow on `schedule:` (**daily**) plus `workflow_dispatch:` (a manual rerun of the same stable-`latest` analyzer — no alpha/prerelease input in v1).

**Cadence — daily.** Observed Codex release velocity is ~0.4 stable releases/day (`0.130`→`0.135` in 12 days), with an `alpha` (`0.136.0-alpha.1`) already staged. Weekly would queue 5–14 versions per run; daily keeps the rolling issue close to reality at negligible CI cost. (Confirm at review.)

Sequence (steps 1–6 run **unauthenticated, with no network beyond the npm registry**; step 7 publishes via the GitHub Actions/REST API authenticated with `GITHUB_TOKEN` — see **Prerequisites** below and [Issue lifecycle](#issue-lifecycle)):

1. Read `TESTED_CODEX_VERSION` from [`server/codex_compat.py`](../../../server/codex_compat.py); read current release from **npm `dist-tags.latest`** (`npm view @openai/codex dist-tags.latest`) — the authoritative source, matching the `codex --version` string exactly. **Use `dist-tags.latest`; ignore prerelease tags such as `alpha` in v1** (prerelease investigation is out of scope — see [Out of scope](#out-of-scope)).
2. If `latest <= TESTED` → no drift; ensure the rolling issue is closed (see [Issue lifecycle](#issue-lifecycle)); exit GREEN.
3. Install: `npm install -g @openai/codex@<latest>`. The package uses per-platform `optionalDependencies`, which npm auto-resolves on `ubuntu-latest` (linux-x64). **Post-install, verify `codex --version` == `codex-cli <latest>`** before proceeding.
4. Generate the schema **bare, without `--experimental`** (matching `scripts/regenerate_schema.sh`, which generates fixtures this way), and apply the same canonical JSON key ordering the script uses, so the diff is apples-to-apples and deterministic.
5. Diff via [`scripts/compare_app_server_schemas.py`](../../../scripts/compare_app_server_schemas.py) `--old-root tests/fixtures/codex-app-server/<TESTED> --new-root <generated>`.
6. **Classify** the diff (see [Classifier contract](#classifier-contract)).
7. Publish the generated schema bundle + diff JSON + classification as workflow artifacts; create/update one rolling issue; write a job summary.

**Prerequisites the analyzer needs that CI lacks today:**

- **Node/npm setup** — current CI only sets up Python (`setup-uv`); the scheduled job needs a Node toolchain step.
- **`permissions: { contents: read, issues: write }`** — current `ci.yml` declares no permissions block. Setting *any* `permissions:` block drops every unlisted scope to `none`, so `contents: read` must be named explicitly or `actions/checkout` loses its token (it survives on a public repo via anonymous clone, but that is fragile and breaks if the repo ever goes private). `issues: write` is required because the default `GITHUB_TOKEN` is read-only on issues, so `gh issue` would 403 and turn the "success" outcome RED. (`GH_TOKEN` wiring and `gh` ergonomics are implementation-plan detail.)
- **Comparator hardening (B1 + B2)** — `compare_app_server_schemas.py` hardcodes its file inventory, raises `SystemExit` on a missing file, and its `shape_summary` reads only top-level `properties`. Two requirements: **(a) nested permission visibility** — descend into permission/sandbox/approval definitions (`/definitions/SandboxPolicy` variants, `readOnlyAccess`, `workspaceWrite`, permission-profile surfaces) and emit explicit permission-delta fields, so the classifier's containment rule has a signal to fire on (B1); **(b) a typed `diagnostics` section** distinguishing `missing_consumed_file` / `missing_tracked_file` / `unexpected_file` / `parse_error` instead of crashing — where a missing **consumed or permission-sensitive** file routes to `needs-live-review`, never a downgrade to generic `unclassified`/GREEN (B2). This is the first build step (see [Build sequence](#build-sequence)).
- **Schedule durability (B4)** — GitHub auto-disables `schedule:` workflows after ~60 days without repository activity, so the sentinel goes dark precisely during the quiet periods it exists to cover. **v1 mitigation:** a **Tier 1a push/PR check** — which fires on every push regardless of schedule state — warns or fails when no successful drift-analyzer run has been recorded within `N` days (consulting the scheduled workflow's last successful run, e.g. via the Actions API or a recorded marker), with manual `workflow_dispatch` as the recovery path. The detector **must** live on the push/PR trigger; the rolling issue may *display* stale state but cannot be the detector, since a disabled scheduled workflow cannot update its own issue.

## Classifier contract

`classify_drift(report: dict) -> ClassifyResult`, a **pure** function over the comparator output. Its result is a typed, closed shape — not an open dict — so the safety ceiling is enforced structurally, not by prose.

**Output shape:** `{label, action, confidence, reasons, evidence_paths}`. `reasons` is a human-readable list of what drove the label; `evidence_paths` is the list of schema paths (e.g. `/definitions/SandboxPolicy/...`) the classification keyed off, so a reader of a >90-day-old issue can see *what* changed without the expired artifacts.

**Label is a closed enum (Python `Literal`), with no `safe-to-upgrade` member (B3):**

> `label ∈ { harmless, relevant, needs-live-review, unclassified }`. **`safe-to-upgrade` is not in the enum and must be unreachable from schema input.** Schema diffing proves protocol *surface* change; it cannot prove runtime **containment**. The `0.130` `readOnlyAccess`/`workspaceWrite` regression was offline-clean yet live-broken. Only Tier 3b can support upgrade confidence.

**Risk and unknownness are separate axes (resolves the severity-precedence gap).** The three *risk* labels carry a total order — `harmless < relevant < needs-live-review` — used to compute the rolling issue's "highest current classification." `unclassified` is **not** a point on that scale; it is an orthogonal "could not be assessed" flag that always routes to human review and pins the issue open regardless of risk rank. So "highest current classification" = the max over the risk axis, with `unclassified` independently forcing human-triage state.

**Comparator output the classifier consumes (minimal contract, B1 + B2 — facts only; risk is the classifier's job):**

- `permission_deltas: [{ schema_file, json_pointer, change, old, new }]` — one entry per added / removed / changed permission/sandbox/approval field, e.g. `{schema_file: "v2/TurnStartParams.json", json_pointer: "/definitions/SandboxPolicy/.../readOnlyAccess", change: "removed", old: {…}, new: null}`. The comparator reports the change and emits **no** `risk_hint` — `classify_drift` assigns the label, preserving the facts-vs-risk separation B1 exists to create.
- `diagnostics: { missing_consumed_files, missing_permission_sensitive_files, unexpected_files, parse_errors }` — typed string lists, populated instead of raising `SystemExit`.

(This is the comparator↔classifier interface; on normative grafting it is a `contracts.md`-owned interface contract, sketched here for buildability.)

**Rules (each keyed off explicit comparator fields, never `equal: false` inference):**

- **ClientRequest additions** (plugin *sends*): `harmless`/`relevant` — additive, the plugin opts in.
- **ClientRequest removals or shape changes** to runtime-consumed methods: `relevant` → `needs-live-review`.
- **A removed/missing consumed or permission-sensitive schema file** (from the `diagnostics` taxonomy, B2): `needs-live-review` — never `unclassified`/GREEN.
- **ServerRequest additions** (plugin must *receive/handle*): default `needs-live-review` or `unclassified`. Reachability cannot be answered from schema; it is owned by [T-20260429-02](../../tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md). Until that produces a reachability registry, new ServerRequest methods surface explicitly as `unclassified`, never silently passed. *(The label enum and this rule intersect `contracts.md`'s `kind: unknown` contract; routing them to that owner doc is a [deferred](#acceptance-blockers-and-phase-0-prerequisites) item.)*
- **Permission / sandbox / approval shape deltas** (from the nested permission-delta fields the hardened comparator now emits, B1): `needs-live-review` — the schema-invisible containment class. This rule is only implementable once B1 lands; without the explicit fields it has no input.
- **Unknown bundle files / parse failures**: `unclassified`, carried from the comparator `diagnostics` section.

**Source of truth for "runtime-consumed methods":** the comparator's existing constants (`DIRECT_RUNTIME_CONSUMED`, `THREAD_TURN_REQUESTS`, `THREAD_PERMISSION_RESPONSES`, `SERVER_METHOD_FILES`, command-approval surfaces) are the single registry the classifier reads; the term is not redefined in prose here, and the per-file lists stay code-owned to avoid doc drift.

`unclassified` is an explicit, non-silent state — it routes to human review, it does not mean "fine."

## Issue lifecycle

- **Permissions**: the workflow declares `permissions: { contents: read, issues: write }` (see Prerequisites — `contents: read` is not optional once a `permissions:` block exists).
- **Label bootstrap (B5)**: before any `gh issue create`/`gh issue edit --add-label`, run an idempotent `gh label create codex-drift --force` (create-or-fallback). A missing or deleted label must **never** turn a successful analysis RED via the "publication failed" path — that would discard a completed diff+classification over a cosmetic label gap. (The find step, `gh issue list --label`, returns empty on a missing label rather than failing; the failure is in the subsequent create/edit-with-label.)
- **One rolling issue**, found idempotently by a fixed **label** (`codex-drift`) and deterministic title — not a new issue per run. The problem is singular ("baseline is stale"), not per-release.
- **Concurrency (B5)**: the workflow declares a `concurrency:` group (single in-flight run; queue or cancel-superseded). Without it, an overlapping cron tick and `workflow_dispatch` run race the find→comment→mutate-label sequence — both can find no open issue and each create one, or clobber each other's severity title. Label idempotency dedups *identity* but not *concurrent execution*.
- **Cross-epoch reopen (H3)**: the label+title lookup searches **all** issues including closed (`--state all`). A recurring drift after a prior resolution **reopens the existing closed issue** rather than opening a new one, preserving the "one rolling issue / no duplicates" invariant across close→reopen cycles.
- **Per-run update — delta-gated (B5)**: comment **only when the version delta or classification changes** (an unchanged `latest` must not append a near-identical comment every day). When it does comment, embed a **durable summary** in the comment body — version delta, classification (`label`/`action`/`confidence`/`reasons`), the method add/remove list, and the `diagnostics` section — not just links to the (90-day-expiring) artifacts. Keep the issue **severity label/title mutable**, reflecting the highest current risk-axis classification. Detail beyond the comment lives in artifacts and is regenerable offline via Tier 3a from the recorded version delta.
- **Auto-close on resolution**: when `TESTED_CODEX_VERSION >= npm latest` (the rebaseline caught up), post a "drift resolved" comment and close the issue. No zombie issue, no duplicates.
- **Job exit policy — locked for v1**: ordinary drift detection is a **successful routed outcome** → job GREEN. The job goes RED **only** for analyzer/infrastructure failure (latest unresolved, install/generate/diff/publication failed). **Drift itself never reds the loop** — this is the v1 default and is *not* an open question. A later opt-in escalation exception (e.g. flip RED on a `needs-live-review` removal of a runtime-consumed method) may be layered additively on top of this default; it does not block the v1 analyzer.
- **Notification**: write `$GITHUB_STEP_SUMMARY` with the classification and a link to the issue so a GREEN run is visible on its run page. Note the step summary is run-scoped and retention-bound — the **open issue itself** is the durable, operator-facing signal; the step summary is a convenience, not the primary visibility mechanism.

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

**Routing (recalibrated):** the floor relationship's **normative home is `delivery.md` §Compatibility Policy**, which already owns the `MINIMUM`/`TESTED` constants and the version-upgrade workflow. A follow-on **Decision Record** at `docs/decisions/<date>-codex-version-floor-policy.md` (ADR format per [`2026-05-16-security-hook-guard-extension.md`](../../decisions/2026-05-16-security-hook-guard-extension.md)) carries the **rationale**, produced as an exit condition of the rebaseline workflow ([T-20260516-01](../../tickets/2026-05-16-codex-app-server-version-upgrade.md)). Because `docs/decisions/` sits outside the spec authority tree, the ADR must be reachable from the authority path: a one-line normative pointer in `delivery.md` §Compatibility Policy plus a cross-reference in [`decisions.md`](../decisions.md) §Open Questions. This matches the repo's established "ADR-as-rationale, normative-claim-in-owner-doc" pattern. This spec records the **need and the home**; it does not pick the policy.

## Test strategy and seams

Follow the repo's existing seam convention: **module-level `@patch` of `subprocess` at the test boundary** (as `tests/test_codex_compat.py` does for `get_codex_version`), **not** callable injection threaded through call sites. Concretely:

- `classify_drift` is a pure function over the comparator dict → unit-test with synthetic diff fixtures (additive ClientRequest, ServerRequest addition, permission-shape delta, removed consumed file, unknown file → `unclassified`). **Negative tests (B3):** assert that *no* input produces `safe-to-upgrade` (the closed `Literal` makes it a type error, and a test enumerates/fuzzes report shapes to confirm unreachability) and that a permission/sandbox delta and a removed consumed file both route to `needs-live-review`.
- Comparator hardening → unit-test (a) a synthetic bundle missing/adding a file emits the typed `diagnostics` section (not a crash) **and routes a missing *consumed* file to `needs-live-review`, not `unclassified`** (B2); (b) a `SandboxPolicy` nested-variant change (the `0.130` `readOnlyAccess` removal) produces an explicit permission-delta field, not a bare `equal: false` (B1). The test must witness the removed-consumed-file path specifically — an inventory-churn-only test passes while the real crash/downgrade path stays live.
- The npm-latest lookup and codex install are patched at the subprocess boundary so the analyzer logic is testable offline — **which requires that logic to live in an importable Python module, not only in workflow YAML**; factoring it out is an implementation-plan requirement, else there is no `subprocess` boundary to `@patch`.

## Build sequence

For the follow-on implementation plan, **not** this spec's scope. Spec acceptance commits to B1–B5 (above); this sequence is the phase-0-first ordering — **B1–B3 (steps 1–2) land and are tested before any scheduled-workflow or issue-routing code (step 4)**:

1. Comparator hardening — nested permission-delta extraction (B1) + typed `diagnostics` taxonomy with consumed/permission-file escalation (B2). Prerequisite for everything downstream.
2. `classify_drift` as a closed-`Literal` contract + ceiling, with synthetic-diff unit tests and the `safe-to-upgrade`-unreachable negative test (B3).
3. Tier 1a consistency checks + `.status.json` marker format (warn-first).
4. Scheduled workflow (Node setup, `permissions: { contents: read, issues: write }`, `concurrency:` group, `workflow_dispatch` + staleness/dormancy mitigation B4) + label-bootstrap and cross-epoch-reopen rolling-issue routing + delta-gated durable comments + job summary.
5. Docs/ADR/status updates: graft normative claims into `delivery.md` (with the floor-policy pointer), create the floor-policy rationale ADR, update `docs/status/`.

Tier 1b is already done.

## Out of scope

This spec **defines the gate**; it does **not** rebaseline Codex. The stale `chore/t-20260516-01-version-rebaseline` branch and the actual `0.117`→`0.135` rebaseline are noted as relevant context only — the rebaseline itself is [T-20260516-01](../../tickets/2026-05-16-codex-app-server-version-upgrade.md) work, separate from this design branch.

**Prerelease (`alpha`) investigation is also out of v1 scope.** The recurring sentinel tracks stable `dist-tags.latest` only; `workflow_dispatch` is a manual rerun of that same stable analyzer. A future prerelease investigation mode — raw-version identity, no `SemVer` suffix stripping — is deferred (see [Acceptance Blockers and phase-0 prerequisites](#acceptance-blockers-and-phase-0-prerequisites)).

## Open questions for review

- **Cadence**: daily confirmed? (recommended given release velocity)
- **Floor policy**: the `MINIMUM`-vs-`TESTED` relationship (rationale deferred to its own ADR; normative home is `delivery.md` — see [Decision record](#decision-record)).
- **Marker format**: the `.status.json` schema for extra fixture dirs.

*(Resolved since round-1 review: **blocking-escalation** is no longer open — v1 locks GREEN-with-issue unless the analyzer fails, see [Issue lifecycle](#issue-lifecycle). The substantive items now live under [Acceptance Blockers](#acceptance-blockers-and-phase-0-prerequisites).)*
