# Tech Debt Audit — codex-collaboration

**Date:** 2026-05-15
**Scope:** system (whole repository)
**Method:** parallel 6-auditor team (code-health, architecture-drift, dependency, test-debt, operational, knowledge), category-scoped lenses, lateral cross-lens coordination, lead synthesis.
**Archetypes:** Single-author project (high confidence) + Greenfield-on-legacy (med-high). **Stakes:** high (trust-boundary safety substrate + autonomous code execution + distributable plugin; user-confirmed).

---

## 1. Audit Snapshot

| Severity | Count | | Bucket | Count |
|----------|-------|---|--------|-------|
| P0 | **0** | | Quick Wins | 9 |
| P1 | 4 | | High-Leverage | 5 |
| P2 | 14 | | Strategic | 3 |
| P3 | 3 | | Watch | 5 |
| **Total canonical** | **21** | | | |

**Headline:** This is a **clean, disciplined, young codebase** (4 days post-extraction, 1172 tests, ~2.5:1 test:code ratio, zero TODO/FIXME, extensive specs/ADRs). Five auditors found **zero P0 and zero P1** in their lenses; the only P1s came from `test-debt` (suite performance, mock-vs-reality) and `knowledge` (ADR gap, bus factor). The debt that exists is overwhelmingly **small, well-bounded doc/test/observability fixes**, not structural rot. The single strongest signal is a 4-auditor convergence on one root cause: **the Codex CLI is an unmanaged external dependency whose contract/version drift is invisible to CI.**

**Audit metrics:** raw 24 → canonical 21 (5 merges); 9 corroborated; 0 contradictions; 16 schema normalizations; 4 tradeoffs. `test-debt` delivered ~18 min late (3× the timeout threshold) after two lead escalations but **recovered fully** — no category lost; its findings include the audit's highest-severity items.

**Coverage:** 6/6 categories deep. No `auditors_failed`. Severity distribution (0% P0, 19% P1) is conservative and honest — no inflation.

---

## 2. Focus and Coverage

- **Scope:** `system`, single level. **Stakes:** `high` → +1 lens depth on primary auditors, no auditor suppressed.
- **Archetypes:** Single-author (61/61 commits one author → bus factor 1 by construction; calibrated per handoff-readiness note) + Greenfield-on-legacy (extracted from `claude-code-tool-dev` monorepo 2026-05-11 → extraction-seam focus).
- **Emphasis map:** primary = architecture-drift, test-debt, operational, knowledge; secondary = code-health, dependency.

| Category | Status | One-line |
|----------|--------|----------|
| Code Health | deep | Clean; one method-level complexity hotspot. Duplication/dead-code/naming/smells confirmed clean. |
| Architecture Drift | deep | Extraction seam 99% clean (1 test regression); models hub + MCP-boundary seams are the structural watch-items. |
| Dependency | deep | PyPI surface clean *as of 2026-05-15* (3 pkgs; no CVEs at locked versions per **manual** advisory cross-ref — no automated scanner, e.g. `pip-audit`/`osv-scanner`, in CI, so this claim decays). All real risk is the out-of-band Codex CLI. |
| Test Debt | deep | Safety substrate well-tested; gaps are suite *performance* and wire-contract validation, not critical-path coverage. |
| Operational | deep | Solo dev-tool (no SLA). Real items: telemetry gaps on highest-risk ops, concurrent-session hazard, external-dep bring-up. |
| Knowledge | deep | Well-documented for age; gaps are doc *drift* (status docs, README) and missing ADR on a security change. |

**Per-auditor:** code-health 1 finding + 5 clean lenses. architecture-drift 4 P2 + 3 P3 + 1 verified-clean boundary. dependency 2 findings + 6 thorough clean coverage notes (genuinely clean PyPI surface). test-debt 4 findings (2× P1) + safety-substrate confirmed clean. operational 6 findings, properly calibrated to solo-tool scale. knowledge 5 findings + 3 suppressed-by-archetype lenses.

---

## 3. Quick Wins

*Ship-in-a-sprint items. Ordered severity → leverage → corroboration. Calibration note: this audit found 0 P0/0 P1 in five lenses; per the rubric's sanity-check guidance, well-justified P2 items with small effort, a clear fix, and a concrete cost are admitted to quick-wins (severity ≠ priority).*

**QW1 — Add an ADR for the security hook-guard extension (commit d4f38f7)** · knowledge · `docs/decisions/` · **P1**
The May-12 commit extended the fail-closed credential guard from advisory tools to delegation tools — a trust-boundary change — with no decision record anywhere (only the commit message + `hooks.json`). *Impact:* security-boundary changes without ADRs make intentional-vs-accidental impossible to verify in any future audit; sets a precedent for the next solo-author security change. *Fix:* write one dated ADR (context/decision/status/rationale); adopt "ADR in the same commit" for future security-boundary changes. *Effort:* small (~1h) · *Leverage:* high (security traceability) · cross-links QW6.

**QW2 — Correct the README safety-substrate tool list** · knowledge · `README.md:115` · **P2**
README states the guard covers 3 advisory tools; the matcher actually covers 5 (adds `delegate.start`, `delegate.decide`). *Impact:* the primary reader/security-reviewer entry point *understates* the trust boundary — wrong direction (looks more permissive than reality). *Fix:* one sentence. *Effort:* XS (~15 min) · *Leverage:* high.

**QW3 — Emit terminal-path audit events (rollback + unknown-terminal)** · operational · `delegation_controller.py` rollback branch (~2209-2255) · **P2**
Promotion `rollback_needed→rolled_back` and `terminal_status="unknown"` emit no `append_audit_event`. *Impact:* the forensic surface most likely consulted first (`audit/events.jsonl`) is silent on the highest-risk operation — a rolled-back promotion looks identical to a clean one. *Fix:* the `AuditEvent` *record* schema exists, but **no `action` enum value covers rollback or unknown-terminal** (`contracts.md` §Audit Event Actions enumerates "currently emitted" + "reserved"; neither list contains them). So this is a contract+spec change, not a drive-by call-site add: (a) select action name(s); (b) update `contracts.md` §Audit Event Actions; (c) update `recovery-and-journal.md` §Unknown Request Handling, which currently states *no* audit event is emitted for unknown terminalization and that terminal evidence is the `DelegationOutcomeRecord` — a deliberate "trust-boundary crossings → AuditEvent, provenance → OutcomeRecord" split (`contracts.md`); (d) tests. The **rollback half** is a clean forensic gap (a state-changing trust-boundary event with no record). The **unknown-terminal half reverses a documented design decision** — it needs an ADR-style rationale (or should be split out to Strategic), not a silent contract widening. *Effort:* small for the rollback half; the unknown-terminal half is a spec+contract change requiring a decision record · *Leverage:* high (rollback) / medium (unknown-terminal).

**QW4 — Add startup Codex-version pre-flight check** · operational · `scripts/codex_runtime_bootstrap.py` `main()` · **P2**
Codex CLI version is enforced only at first delegation call, not at bring-up. *Impact:* `uv sync` + plugin load succeed; a version mismatch surfaces as a mid-session runtime error, not an install-time failure — worse as a distributable plugin. *Fix:* call a version check before `server.run()`, fail fast with a clear message. *Effort:* small (~1-3h) · *Leverage:* high (part of the Codex-CLI cluster — see HL1/ST2).

**QW5 — Document the concurrent-session promotion hazard + add race detection** · operational+knowledge · `README.md:126`, `scripts/publish_session_id.py` · **P2** · *independent_convergence (OP-4 ⋂ KN-5)*
README calls it a "race on the session identity file"; the real worst case is two sessions passing the `HEAD==base_commit` promotion gate and the second `git apply --binary` landing on an already-mutated tree (workspace corruption). *Impact:* operator underestimates severity by ~an order of magnitude; no recovery step documented. *Fix:* expand the Limitations section (what collides, promotion is highest-risk, recovery = stop all/`git status`/single restart) + a cheap mtime-based "session_id written by someone else <60s ago" stderr warning at startup. *Effort:* small (doc XS + detection ~1-2h) · *Leverage:* medium.

**QW6 — Extract the duplicated trust-boundary tool-name prefix + add a consistency test** · architecture-drift · `scripts/codex_guard.py:24`, `server/consultation_safety.py:76-83` · **P2** · *cross_lens_followup_confirmation (AD-3 ⋂ TD)*
The full MCP prefix string is hardcoded independently in the guard and the policy map; no test asserts they match. *Impact:* a plugin rename updating one but not the other silently bypasses credential scanning on affected tools — a silent failure in the security layer. *Fix:* shared constant + `assert all(k.startswith(_TOOL_PREFIX) for k in _TOOL_POLICY_MAP)`. *Effort:* small · *Leverage:* medium.

**QW7 — Fix the `parents[4]` extraction-seam regression in the live test** · architecture-drift+test-debt · `tests/test_control_plane_live.py:21` · **P2** · *cross_lens_followup_confirmation (AD-1 ⋂ TD)*
`parents[4]` resolves to `~` post-extraction (was correct in the monorepo). Masked by the `codex`-absent skip gate in CI; on a dev machine with `codex` present it silently validates `codex.status` against an arbitrary git repo (false green). *Fix:* `parents[4]` → `parents[1]`. *Effort:* XS (one line) · *Leverage:* medium (removes a silent false-green).

**QW8 — Reconcile the stale status synthesis docs** · knowledge · `docs/status/current-state.md`, `reconciliation-register.md` · **P2**
Both are ~15 days / ~29 commits stale (pre-extraction), yet the README names them the "reader entry point for current project state" and the register is the open-work tracker. *Impact:* orientation friction; the register cannot do its one job. *Fix:* reconcile post-extraction commits; add a per-commit touch to the existing AGENTS.md checklist. *Effort:* small (1-2h) · *Leverage:* medium.

**QW9 — Make bounded-poll test failures diagnosable** · test-debt · `tests/test_delegation_controller.py` (~15 sites), `test_resolution_registry.py` · **P2**
5s bounded-poll deadlines + a `time.sleep(0.7)` vs 0.5s-timer margin are latent flakes on loaded CI; failures look like real regressions. *Impact:* phantom CI failures erode the single-author project's primary quality signal. *Fix:* widen the thin sleep margin; add `f"...final_job={final_job!r}"` to poll assertions. *Effort:* low · *Leverage:* medium.

---

## 4. High-Leverage Fixes

*Investing here removes other backlog items. Ordered by downstream count → severity → effort.*

**HL1 — Validate the Codex wire contract in CI (payload shape, not just method names)** · test-debt+dependency · `tests/fixtures/codex-app-server/0.117.0/`, `server/runtime.py` · **P1** · *independent_convergence (TD-2 ⋂ DP-2)*
Vendored schemas are used only to assert client method-name *presence* (`codex_compat.REQUIRED_METHODS ⊆ extracted methods`); no test validates *payload shape*, and the surface splits across **two distinct schema boundaries** that must be tested separately. (1) **Client-request params** — `turn/start` (incl. the security-adjacent `approvalPolicy` / `sandboxPolicy` / `effort` fields) and `account/read`, sent via `JsonRpcClient.request()` — validated against the client-request param schemas. (2) **Server-request responses** — the approval / file-change / user-input results the controller builds in `_server_request_handler` and sends via `JsonRpcClient.respond()` as JSON-RPC *responses* (`{id, result}`, no `method` — these do **not** travel as a client request method, so there is no `command-respond` surface to validate) — validated against the vendored `*ApprovalResponse` / `ToolRequestUserInputResponse` schemas. A field rename (`approval_policy`→`approvalPolicy`) passes all 1172 tests; the only catch is `test_codex_compat_live.py`, skipped in CI. *Unblocks:* the entire Codex-CLI cluster — DP-1 pin upgrades (ST2), DP-2 CI gap, OP-3 contract drift, and the security-adjacent approval/sandbox payload risk. *Fix:* add `jsonschema` dev dep; **two** contract-test families — one building client-request params through the `runtime.py` request paths, one building server-request responses through the `_server_request_handler` / `respond()` path — each `jsonschema.validate()`d against the matching already-vendored schema. *Effort:* medium · *Leverage:* high (unblocks dependency + operational + closes a security-adjacent gap).

**HL2 — Make the test suite fast (inject the approval window; fast/slow split)** · test-debt · `tests/test_delegation_controller.py`, `pyproject.toml` · **P1**
~245s of the 250s suite is ~6 timeout-path tests parking on the real 900s-default approval window (never injected; `_build_controller` has no override). No `fast`/`slow` markers, no `addopts`, no `pytest-xdist`. *Unblocks:* every other test-coverage recommendation (HL1, SY-17) can be added without worsening an already-discouraging 4-min loop; reduces "push and wait for CI" behavior. *Fix:* injectable `approval_window_seconds` (0.5s in timeout tests); `slow` marker + `addopts="-m 'not slow'"` as the **local default only**. A global `addopts` applies to *every* invocation including CI's `uv run pytest tests -q`, so the CI workflow must **explicitly override it to run the full suite** (e.g., `-m ''` / `--override-ini` / an explicit marker) — otherwise the ~6 timeout-path tests (the highest-risk coverage this very item is about) are silently dropped from CI. Consider `-n auto` in CI. *Effort:* medium · *Leverage:* high (prerequisite to safely growing coverage).

**HL3 — Extract `_server_request_handler` from `_execute_live_turn`** · code-health · `server/delegation_controller.py:946-1429` · **P2** · *cross_lens_followup_confirmation (CH-1 ⋂ AD-5)*
A 459-LOC nested closure (~37 branches, 3 nonlocal write-back side-channels) is the sole router for all approval-request kinds. architecture-drift confirmed the *module* is correctly partitioned (no split needed) — the debt is purely this method. *Unblocks:* individual approval-kind handlers become unit-testable in isolation (a test-debt enabler); collapses 2-3 indentation levels. *Fix:* extract to a named `_ServerRequestRouter`/method with explicit params/returns — pure in-module refactor. *Effort:* medium · *Leverage:* medium (test isolation of the approval path).

**HL4 — Add a read-through cache to LineageStore/TurnStore + close the orphaned-dir gap** · operational · `server/lineage_store.py`, `server/turn_store.py` · **P2**
Both replay the full JSONL on every `get()`/`list()` — O(n) per call, growing with dialogue length; session dirs orphan on abnormal exit. *Unblocks:* the dialogue/delegation scaling surface (each dispatch reads lineage to resolve handles) and slow disk accumulation. *Fix:* cache replay result, invalidate on append (safe — single-writer per session); add/verify `cleanup()` on the abnormal-exit path. *Effort:* medium · *Leverage:* medium-high.

**HL5 — Add a real-subprocess test layer for `JsonRpcClient`** · test-debt · `server/jsonrpc_client.py` · **P2**
`request()` / `next_notification()` and the malformed-line silent-drop (`except json.JSONDecodeError: continue`) are untested in the non-live suite; a dropped notification the controller awaits → hang/timeout, unexercised. *Unblocks:* safe evolution of the transport layer (all higher tests use fakes). *Fix:* `tests/test_jsonrpc_client.py` driving a trivial echo subprocess (not the Codex binary; <1s, CI-safe) for round-trip / notification-buffer / malformed-drop / ID-mismatch. *Effort:* medium · *Leverage:* medium.

---

## 5. Strategic Items

*Real pain, not sprint-sized. Roadmap planning, not next sprint.*

**ST1 — Knowledge transfer for the three load-bearing modules** · knowledge · `delegation_controller.py` (3,296 LOC), `journal.py` (762), `control_plane.py` (566) · **P1**
Bus factor 1 by construction (solo project); the *finding* is the combination of BF-1 + operational criticality + high complexity + fast change on exactly these three modules — the gap between "only JP can debug this" and "the plugin is blocked" is narrowest here. Correctly calibrated **P1, not P0**: no handoff evidence (no announced transition/successor/deadline) was found.
*Planning notes:* no action required absent a handoff. **Trigger:** any announced transition, onboarding, or >1-quarter unavailability. **Pre-work when triggered:** module-level architecture comments documenting the state machines/invariants/non-obvious decisions (~2-4h each) — these also accelerate future-self recall. True knowledge transfer (paired work, design walkthroughs) is the large, unschedulable part — name it now so it isn't discovered at the worst time. Sequences naturally *after* HL3 (extracting the closure makes `delegation_controller.py` materially easier to hand off).

**ST2 — Track and execute the Codex version-pin upgrade** · dependency · `server/codex_compat.py:24-27`, `docs/specs/2026-04-29-codex-app-server-0.125.0-schema-delta.md` · **P2** · *Codex-CLI cluster*
`TESTED_CODEX_VERSION=0.117.0` lags the installed binary (≥0.128.0) by ≥2 minor; the 0.117→0.125 delta alone is 63 changed schema files + a `permissionProfile`/`sandboxPolicy` mutual-exclusion. No tracked upgrade artifact exists; the gap widens every Codex release.
*Planning notes:* the schema-delta doc already enumerates the exact pre-upgrade gates (fixture regen → schema diff → contract tests → live probe → advisory+execution smoke → thread regression → sandboxPolicy/permissionProfile behavior → operator-notification tests → doc sweep). Open one reconciliation-register-tracked ticket that satisfies or explicitly defers each gate. **Strongly sequence after HL1** — payload-shape contract tests are the cheapest gate and de-risk every subsequent one.

**ST3 — Version the Codex App Server JSON-RPC contract** · operational · `server/jsonrpc_client.py`, `docs/specs/` · **P2** · *Codex-CLI cluster*
There is no protocol-version handshake (the `"2.0"` is the JSON-RPC spec version, not a Codex contract version). A Codex-side schema change produces silent data corruption / silent tool-call failure rather than a clean version error.
*Planning notes:* larger and less well-defined than ST2 — needs a contract-version field design, a negotiation/assertion point at server init, and a documented contract-version doc in `docs/specs/`. Depends on HL1 (you need payload-shape validation before a version assertion is meaningful). Roadmap item; revisit after HL1 + ST2 land.

---

## 6. Watch List

| ID | Item | Rationale | Revisit trigger |
|----|------|-----------|-----------------|
| WL1 | `models.py` mega-hub (15/28 importers, flat domains) | Clean today; compounds as capabilities are added | When `models.py` > ~800 LOC **or** a 2nd capability domain is added → split into advisory/execution/infrastructure + re-export shim |
| WL2 | `Any`-typed controllers at MCP boundary (no protocol seam) | Mitigated *only* by integration tests using real controller types (operational watch-point) | If integration tests shift to test doubles for speed/isolation → promote to P2, add `_interfaces.py` protocols |
| WL3 | scripts/server layering invariant undocumented in `foundations.md` | Holds in practice (0 reverse imports); risk is onboarding a 2nd contributor | At next contributor onboarding, or bundle into QW8 doc refresh (one sentence + optional `rg "from scripts\." server/` CI assert) |
| WL4 | Unbounded intra-session audit/outcomes log (startup-only prune) | Documented v1 limitation; theoretical at solo scale | If session duration regularly > 4h **or** `audit/events.jsonl` > 10 MB → implement periodic pruning |
| WL5 | `models.py` holds live `AppServerRuntimeSession` via TYPE_CHECKING | No runtime cost; conceptual layer oddity | If `AdvisoryRuntimeState` ever needs JSON serialization or independent mocking → move session field to a `control_plane.py` wrapper |

---

## 7. Tradeoff Map

*Resource-allocation tensions with concrete anchors — for capacity planning, not design debate.*

**TR1 — Refactor ↔ Ship** (anchor: `delegation_controller.py:946`)
HL3 (extract the 459-LOC closure) competes directly with feature work for the **only** contributor's time. The closure isn't touched every PR, so the compounding cost is real but slow — but it also gates ST1 (knowledge transfer is far cheaper after extraction). Spending on HL3 buys down ST1; deferring both compounds approval-routing change-friction *and* handoff risk together.

**TR2 — Test Coverage ↔ Deploy Speed** (anchor: `.github/workflows/ci.yml`, `pyproject.toml`)
The audit *recommends adding* contract coverage (HL1) and a transport test layer (HL5) onto a suite that is already a discouraging 4 minutes (HL2). Adding coverage first makes the loop worse; HL2 (fast/slow split, window injection, xdist) is the **prerequisite** that makes HL1/HL5 free to land. Sequence HL2 → HL1 → HL5. Doing HL1 before HL2 is the trap.

**TR3 — Stop-the-Bleeding ↔ Build-the-Future** (anchor: `server/codex_compat.py`, `server/runtime.py`)
The Codex-CLI cluster has a cheap local patch (QW4 startup pre-flight — converts silent mid-session failure to a clean startup error) and a structural fix (ST3 contract versioning). QW4 buys time cheaply but does **not** protect against silent wire-format drift; only HL1+ST3 do. Risk: QW4 feels like "done" and ST3 never gets scheduled. Name QW4 explicitly as a stopgap on the ST3 roadmap line.

**TR4 — Bus-Factor-Fix ↔ Speed** (anchor: `delegation_controller.py`, `journal.py`, `control_plane.py`)
The cure for ST1 (architecture docs, paired walkthroughs) slows the one person who already knows the code, for a benefit invisible until a handoff. Classic under-investment trap. The audit's stance: do **not** pay this now (correctly P1-not-P0, no handoff evidence) — but pre-commit the trigger and the ~2-4h/module doc pre-work so it's a scheduled response, not a scramble.

---

## 8. Open Questions / Next Probes

1. **Is a Codex-CLI pin-upgrade actually scheduled?** ST2's severity rests on the gap being *untracked*. If a reconciliation-register item or ticket already owns it, ST2 drops toward watch. (Probe: `docs/status/reconciliation-register.md` after QW8 refresh.)
2. **`_TOOL_POLICY_MAP` over-declaration** — policies for `delegate.poll/promote/discard` exist but those tools aren't in the hook matcher (harmless: `content_fields` empty). Forward-compat by intent, or stale? One sentence of intent-documentation resolves it; not backlogged.
3. **Is the marketplace-distribution path real?** Several findings (QW2, QW4, ST3) escalate in importance if this plugin will be installed by users with arbitrary Codex versions. If distribution is not planned, the Codex-CLI cluster stays medium, not high.
4. **Does `LineageStore.cleanup()` actually run on session end?** HL4's orphaned-dir half is `confidence: medium` — the call site wasn't traced to the abnormal-termination path. Confirm before sizing HL4.

---

*Workspace artifacts (findings, ledger) at `.tech-debt-audit-workspace/` — gitignored, transient. This report is the durable deliverable.*

---

**Revision 2026-05-16 (post-commit cross-model review).** Remediation shapes corrected after external review of the `e7b551b` deliverable; findings and severities unchanged. (1) **HL1** rewritten — the original named a non-existent `command-respond` wire surface and conflated client-request params with server-request responses; now split into the two real schema boundaries. (2) **QW3** *Fix* corrected — emitting these events is a `contracts.md` + `recovery-and-journal.md` contract/spec change (no `action` enum value exists), and the unknown-terminal half reverses a documented AuditEvent-vs-OutcomeRecord decision. (3) **HL2** *Fix* corrected — a global `addopts="-m 'not slow'"` would silently drop the timeout-path tests from CI unless the CI workflow explicitly overrides it. (4) **Dependency** snapshot caveated — the no-CVE/current claim is a manual, unscanned, point-in-time check.
