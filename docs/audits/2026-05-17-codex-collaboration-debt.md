# Tech Debt Audit — codex-collaboration

**Audit initiated:** 2026-05-16 · **Finalized:** 2026-05-17
**Scope:** `system` (whole repository) · **Stakes:** `high` (trust-boundary safety substrate + autonomous code execution)
**Archetypes:** Single-author project (high confidence) + Greenfield-on-legacy (med-high)
**Method:** Fresh independent re-audit. 6 category-scoped auditors, parallel, **blind to all prior audits**, lateral cross-lens messaging, lead synthesis. No auditor suppressed (high stakes).

**Backlog status:** This audit is an active backlog source. The canonical open/deferred routing lives in [`docs/status/reconciliation-register.md`](../status/reconciliation-register.md) under `DEBT-20260517-*` rows, with existing ticket-owned work left on its tickets. This report's routing claim is only true when this audit, [`docs/status/current-state.md`](../status/current-state.md), and the reconciliation-register update are published together; do not publish this audit alone with register-backed authority language. If this audit and the register disagree about current priority, ownership, or exit conditions, update the register and treat the register as the active-backlog index.

---

## 1. Audit Snapshot

| Severity | Count | | Bucket | Entries |
|----------|-------|---|--------|---------|
| P0 | **0** | | Quick Wins | 3 |
| P1 | 4 | | High-Leverage | 3 (+1 deferred watch-mapped item) |
| P2 | 14 | | Strategic | **0** |
| P3 | 7 | | Watch | 11 (+2 notes) |
| **Canonical** | **25** | | | |

**Headline:** A genuinely clean, disciplined, young codebase. The durable backlog signal is the tracked issue routing below plus the `DEBT-20260517-*` register rows. The audit found **zero P0** and only **four current P1s** — none in code-health, architecture, or dependency *correctness*. The strongest implementation signal is that the OpenAI Codex CLI is the system's primary external trust dependency and **no CI gate detects its drift** (`SY-1`, from `DP-1`+`AD-4`+`TD-2`). A cross-lens chain (test-debt -> architecture-drift Playbook #4) surfaced **`AD-9`**, a *named missing seam* upstream of two test-debt findings — the audit's clearest high-leverage lever. The largest module (`delegation_controller.py`, 3367 LOC) was investigated and **disconfirmed as a god-module** — cohesive, P2, watch — a deliberate non-inflation. The concurrent-session promotion race remains a real high-consequence issue, but current project policy maps it to deferred watch row `WL6-CONCURRENT-PROMOTION-LOCK` until broad marketplace distribution or routine multi-session use appears.

**Local synthesis snapshot, not durable proof:** raw 34 -> canonical 25 · 6 duplicate clusters merged · 6 corroborated · **1 contradiction surfaced and resolved** (Codex "fail-open" mischaracterization corrected by architecture-drift's call-graph trace -> reframed as `SY-2`) · ~26 schema normalizations · 0 auditors failed · 4 tradeoffs mapped. These numbers describe the local audit run; use the tracked findings, register rows, and source anchors for durable backlog truth.

**Reproducibility note:** The raw findings and synthesis ledger currently live under `.tech-debt-audit-workspace/`, which is explicitly transient and gitignored. Treat raw-count, duplicate-merge, corroboration, contradiction-resolution, timing, and per-auditor breakdown claims as on-machine synthesis metadata until a compact ledger/appendix is promoted into a durable tracked artifact or the report links tracked evidence for those claims.

**Coverage snapshot:** 6/6 categories deep. No `auditors_failed`. Severity distribution (0% P0, 16% current P1) is local synthesis metadata rather than fresh-clone proof; the durable claim is that no tracked P0 remains in the register-backed backlog and the current P1 work is routed through the rows/tickets named below.

> **Note on revision:** Auditors continued cross-lens refinement after the initial synthesis draft; findings files were re-read on team shutdown. `AD-9` and `TD-6b` were added; `TD-1`/`TD-4` were re-anchored to `AD-9`. This report reflects the final state.

---

## 2. Focus and Coverage

- **Scope:** `system`, single level. **Stakes:** `high` → +1 deep-lens cap on primary auditors, no suppression.
- **Archetypes:** Single-author (one author/email across 100% of commits → bus factor 1 *by construction*) + Greenfield-on-legacy (extracted from `claude-code-tool-dev` monorepo 2026-05-11, 5 days before audit).
- **Emphasis map:** primary = architecture-drift, test-debt, knowledge, **operational (lead-escalated)** — the runtime-safety surface IS the product's core risk; secondary = code-health, dependency.

| Category | Status | One-line |
|----------|--------|----------|
| Code Health | deep | Clean. One cohesive size outlier (not rot), two P3 duplications. Broad-except usage was reviewed as disciplined, not a smell. |
| Architecture Drift | deep | Extraction import-clean. Composition-root lacks Protocol seams (P2); Codex version window has no certified tolerance range (P2); no god-module; **named the AD-9 missing test seam (high leverage)**. |
| Dependency | deep | No active PyPI dependency finding was retained; scanner coverage remains absent (see QW3). All real risk is the out-of-band Codex CLI. |
| Test Debt | deep | Exceptional depth (~1.2k tests; current all-test collection is 1199, default marker-filtered collection is 1184/1199). Parked-worker drain overhead is structurally forced by a missing seam; exact timing remains local synthesis metadata until reproduced. Codex wire-contract gate frozen at 0.117.0; 8/15 secret families untested; partial-`git apply` crash path untested. |
| Operational | deep | No root log handler; crash/restart audit events unimplemented; concurrent-session promotion race. Containment boundary confirmed architecturally clean. |
| Knowledge | deep | Spec/ADR layer unusually rich. `delivery.md` omits 2 security-adjacent modules; `docs/superpowers/` is unrationalized extraction residue (load-bearing ref). |

**Local per-auditor summary:** code-health 3 · architecture-drift 9 · dependency 2 (+4 clean sentinels) · test-debt 7 · operational 8 · knowledge 5 (+3 clean coverage notes). This is audit-run metadata, not an independently reproducible fresh-clone ledger.

---

## 3. Quick Wins

Start here for audit-derived implementation work after confirming the matching `DEBT-20260517-*` row in the reconciliation register. These are sprint-startable and high ROI, but the register remains the current priority and ownership index.

### QW1 — Configure a logging root handler *(P1, leverage: high, effort: small)*
- **category:** operational · **anchor:** `scripts/codex_runtime_bootstrap.py` `main()`; all modules use `logging.getLogger(__name__)` · **source:** SY-3 / OP-1
- **Problem:** `codex_runtime_bootstrap.py` never calls `logging.basicConfig()`. Python's `lastResort` handler emits only WARNING+ to stderr, unformatted. Every DEBUG/INFO record (job IDs, session IDs, worktree paths, transition states) is silently dropped.
- **Impact:** When a delegation hangs, the operator has no structured diagnostic record. Compounds OP-2/OP-4/OP-5 — their evidence is invisible without this.
- **Recommendation:** Add a minimal `basicConfig` call at the top of `main()` writing to stderr with a structured format (timestamp, level, logger name, message); use a `CODEX_COLLAB_LOG_LEVEL` env var defaulting to `WARNING`. Document the env var in README's Configuration table.
- **Why #1:** P1 + one-line fix + highest leverage (unblocks the observability 3 other findings depend on).

### QW2 — Add the `drain_workers` seam and explicit parked-worker contract *(P1, leverage: high, effort: small)*
- **category:** architecture-drift / test-debt · **anchor:** `server/delegation_controller.py:812` (`spawn_worker(...)` — return value discarded) + `server/worker_runner.py:112-116` · **source:** SY-25 / AD-9(a) + TD-1
- **Problem:** `DelegationController.start()` discards the `threading.Thread` from `spawn_worker(...)`; there is no `_worker_threads` collection and no `drain_workers` method. Tests have *no alternative* but to enumerate by name (`threading.enumerate()` filtered by `"delegation-worker-job-1"`). The current test suite already demonstrates the important semantic boundary: parked workers must be resolved or explicitly signaled before they can be joined.
- **Impact:** Local audit timing attributed substantial CI overhead to process-wide worker-name enumeration and bounded joins, but the exact `~50s of an 84s CI suite` claim is transient synthesis evidence until reproduced in an implementation PR. The durable debt is the missing supported worker-handle seam and the brittle cross-test dependence on process-wide thread names.
- **Recommendation:** Add `_worker_threads: list[threading.Thread]` to `DelegationController.__init__`, capture `self._worker_threads.append(spawn_worker(...))`, and expose a `drain_workers(timeout: float = 5.0)` seam that joins tracked handles, prunes completed handles, and reports any still-alive/timed-out threads. The seam must not pretend to unblock parked workers: tests must first drive the protocol to an exit condition with `decide()`, terminal runtime completion, or an explicit worker-exit signal such as `signal_internal_abort()`. Teardown then calls `controller.drain_workers()` instead of process-wide name enumeration. **This is a 1-2h structural fix, not a test-quality patch.** *Short-term workaround before the seam lands:* add `controller.decide()` or an explicit worker-exit signal in `test_start_returns_escalation_on_parked` teardown.
- **Note:** This is AD-9(a). Its sibling AD-9(b) (supported delegation test seams) is HL4. Independent of the SY-7 module-split (the seam gap survives any split).

### QW3 — Documentation & config hygiene sweep *(cluster: P2/P3, leverage: low–medium, effort: small — bundle, ~½ day)*
Closure rule: keep the cluster itemized. Do not close QW3 as a single blob unless every subitem below is resolved, explicitly split to another owner, or deliberately declined with evidence.

Independently-trivial fixes worth shipping as one chunk:
- **SY-18 / KN-1:** README.md, AGENTS.md, `.claude/CLAUDE.md` contain stale exact test counts; live collection on 2026-05-17 is 1199 all tests / 1184 default marker-filtered tests → prefer "~1.2k tests" unless a specific doc truly needs an exact count.
- **SY-9 / KN-2+AD-6:** `docs/specs/delivery.md` component tree omits `server/tool_prefix.py` and `server/turn_extraction.py` (the `tool_prefix → consultation_safety → credential-scan gate` path is spec-invisible) → add both with a one-line role description each.
- **SY-10 / DP-2:** No vulnerability scanner in CI → add `uv run --with pip-audit pip-audit` as a CI step + a `dependabot.yml` (pip ecosystem), or add `pip-audit` to the dev dependency group before using plain `uv run pip-audit`. *(< 5 min; trust-boundary hardening.)*
- **SY-20 / CH-3:** Promote `_CANCEL_CAPABLE_KINDS` from duplicated method-locals (`delegation_controller.py:1068`, `:2559`) to a module-level constant beside `_ESCALATABLE_REQUEST_KINDS`.
- **SY-24 / OP-8:** Log the resolved `plugin_data_path` at INFO during startup; add a README note that `CLAUDE_PLUGIN_DATA` defaults to `/tmp/codex-collaboration` (ephemeral on macOS reboots).
- **AD-4(c):** Sync all public plugin version surfaces: `pyproject.toml` (`0.1.0`), `.claude-plugin/plugin.json` (`0.2.0`), and the App Server handshake `clientInfo.version` in `server/runtime.py` (`0.1.0`). If `T-20260516-01` owns the version-surface repair, record that handoff and do not claim QW3 independently closed; if the intended repair is package metadata only, state that explicitly so runtime identity is not accidentally treated as fixed. (Inherited extraction mismatch; 10 min for straight alignment.)
- **SY-11(opt 3) / OP-5:** Add a comment documenting the `jsonrpc_client.py` `deque(maxlen=200)` cap and that it may truncate long-running error context.

---

## 4. High-Leverage Fixes

Each removes downstream pain or protects the highest-blast-radius surface. Ordered by downstream unblock breadth, then severity. HL3 is retained here as risk provenance, but it is explicitly mapped to the existing deferred watch row and is not current implementation work unless that row's trigger fires.

### HL1 — Make Codex CLI contract/version drift visible to CI *(P1, leverage: high, effort: medium)*
- **category:** dependency + architecture-drift + test-debt (3-auditor independent convergence) · **source:** SY-1 / DP-1 + AD-4 + TD-2
- **anchor:** `server/codex_compat.py` (`TESTED_CODEX_VERSION = "0.117.0"`, `MINIMUM_CODEX_VERSION = "0.117.0"`); `server/jsonrpc_client.py` (`["codex", "app-server"]` from PATH); `tests/test_codex_wire_contract.py` fixture-presence gate; `tests/conftest.py` `schema_loader` / `vendored_schema_dir` `pytest.skip()` behavior; `tests/fixtures/codex-app-server/0.117.0/`; `.github/workflows/ci.yml` (no Codex binary)
- **Problem:** The Codex CLI is the primary runtime trust peer, **declared in no manifest and monitored by no CI gate**. `TESTED == MINIMUM == 0.117.0` means the source tree has no certified tolerance window beyond the currently vendored fixture version; `tests/test_codex_wire_contract.py::test_contract_fixtures_present` correctly fails if the required fixture directory or schema files are missing, but the shared schema fixtures in `tests/conftest.py` still skip missing schemas when consumed directly. CI does not install or probe the Codex binary. Runtime startup does run `check_live_runtime_compatibility()` and live method-surface probing, so the remaining problem is source-control/CI invisibility plus the unresolved contract-version boundary, not absence of startup method probing.
- **Impact:** Silent regression class on the system's core function (autonomous Codex execution). A push to `main` with a stale compat pin passes all checks.
- **Unblocks:** dependency (DP-1), architecture (AD-4 seam), test-debt (TD-2 gate); downstream-compounds OP-5/SY-2/SY-4 Codex-crash diagnosis.
- **Existing owners:** `T-20260516-01` owns the Codex App Server version-pin upgrade; `T-20260516-02` owns the explicit contract-version assertion decision. Route HL1 work through those tickets instead of creating a duplicate backlog lane.
- **Recommendation (one shared remediation + verbatim residuals in ledger):** Add a CI `version-check` job validating `TESTED_CODEX_VERSION` matches the vendored fixture directory name (DP-1 low-cost); add a scheduled (weekly) CI job installing the latest Codex CLI and running the compat check, **or at minimum alert when the installed version exceeds `TESTED_CODEX_VERSION`** (AD-4b); narrow the residual TD-2 remediation to `tests/conftest.py`'s skip behavior while preserving the explicit failing fixture-presence gate in `tests/test_codex_wire_contract.py`; widen `TESTED_CODEX_VERSION` ahead of `MINIMUM` for a tolerance range (AD-4a); document the 5-step manual upgrade as a PR-checklist item (DP-1).

### HL2 — Implement the reserved `crash`/`restart` audit events *(P1, leverage: high, effort: medium)*
- **category:** operational · **anchor:** `docs/specs/recovery-and-journal.md` §Reserved Audit Events; `server/journal.py` · **source:** SY-4 / OP-2
- **Problem:** The spec reserves `crash`/`restart` audit event types but no code emits them. On crash, in-flight journal entries have an incomplete final phase; `recover_startup()` marks jobs `unknown` with no correlating audit record — recovery is *reconstructed*, not *recorded*.
- **Impact:** Post-crash forensics require cross-referencing JSONL + host stderr + poll output. An operator cannot distinguish "crashed mid-promotion" from "crashed pre-dispatch" from audit alone. Compounds the Codex cluster (a version-mismatch crash leaves no structured trace). Complementary to SY-26 (OP-2 = missing record; SY-26 = unverified recovery behavior).
- **Implementation precondition:** Before coding, write the mini-design decision: event locus (process-level vs. controller/job-level), sentinel IDs vs. schema change for process-level events, duplicate-prevention/idempotency rules for repeated startup/recovery paths, and the exact lazy-recovery ordering around `McpServer.startup()` / `_ensure_*_controller()`.
- **Recommendation:** Best-effort `crash` write on unhandled exception + SIGTERM, and `restart` write after startup recovery has actually run, but implement against the live audit contract: construct an `AuditEvent` dataclass and call `journal.append_audit_event(event)`, with `action="crash"` or `action="restart"` (not a dict with `type`). Source `event_id` from the same UUID factory pattern used by controllers, `timestamp` from `journal.timestamp()`, and `actor="system"`. Controller/job-level events can use real `collaboration_id`, `runtime_id`, and `job_id`; process-level bootstrap events need the precondition's documented sentinel or schema decision because `AuditEvent` currently requires `collaboration_id` and `runtime_id`. Avoid false crash records on normal shutdown, prevent duplicate restart records across idempotent startup/recovery calls, and account for the actual lazy `McpServer` recovery call graph (`recover_startup()` runs when dialogue/delegation controllers are created).

### HL3 — Harden the concurrent-session promotion race *(deferred watch mapping: `WL6-CONCURRENT-PROMOTION-LOCK`; P1 only if trigger fires)*
- **category:** operational · **anchor:** `scripts/publish_session_id.py`; `server/delegation_controller.py` promotion prechecks; `README.md` Limitations · **source:** SY-5 / OP-3
- **Current policy:** The live status register already tracks this as deferred watch row `WL6-CONCURRENT-PROMOTION-LOCK`: the race remains real, but implementation is intentionally deferred at solo single-session scale until broad marketplace distribution is actively pursued or routine multi-session use begins. README's current rollout target is single-session only.
- **Problem:** The only guard against two sessions racing the `HEAD == base_commit` precheck is a 60s startup-time stderr warning in `publish_session_id.py` — it fires at SessionStart, not promotion, and blocks nothing. Two sessions can both pass the point-in-time check; the second applies its diff to the wrong base.
- **Impact:** Blast radius is the user's **primary workspace git state** (not a sandboxed worktree). A corrupted promotion is not automatically reversible — manual `git log` forensics + reset. Highest-consequence finding in the audit.
- **Recommendation if the trigger fires:** Promote `WL6-CONCURRENT-PROMOTION-LOCK` to an implementation ticket, then emit a pre-promotion audit event recording the lock attempt; add an atomic `O_CREAT | O_EXCL` advisory lockfile (`.promotion-in-progress` in `plugin_data_path`) checked/written before the HEAD precondition and removed on completion/rollback; move concurrent-session detection to promotion time, not just session start. Do not treat this as current sprint work without also updating `docs/status/reconciliation-register.md`.

### HL4 — Add supported delegation test seams *(P2, leverage: high, effort: medium)*
- **category:** architecture-drift / test-debt · **anchor:** `server/delegation_controller.py` (no inspection surface beyond `poll()`); `tests/test_delegation_controller.py` (5028 LOC, 107 tests, 40+ `object.__setattr__`/private-attr sites); `tests/test_delegate_start_async_integration.py` (projection and registry-abort spies); `tests/test_delegate_decide_async_integration.py` (direct registry reservation and `commit_signal` ordering spies) · **source:** SY-25 / AD-9(b) + TD-4
- **Problem:** `DelegationController` exposes no supported seams for tests to observe intermediate state or drive narrow behavior edges. The coupling is not just read-only state inspection: live tests also monkeypatch `_project_pending_escalation`, spy on `controller._registry.signal_internal_abort`, reserve registry entries directly to force contention, and replace `commit_signal` to assert ordering. A `_snapshot_for_test()` seam would cover only the state-observation subset.
- **Impact:** Private-state reads, behavior injection, and synchronization assertions are all coupled to `DelegationController` internals. A refactor can therefore break tests even when public behavior is preserved, and a future SY-7 lifecycle split would still need bespoke harness work unless these seams are named first.
- **Unblocks:** TD-4's state-inspection subset immediately; behavior-injection and registry/synchronization coupling require separate supported harness/protocol seams before the 40+ private sites can collapse cleanly.
- **Recommendation:** Split the repair into two explicit seams. First, add a narrow `_snapshot_for_test()` method (or `DelegationControllerState` dataclass) exposing only legitimate observable state. Second, add supported test harness/protocol seams for projection and registry behavior, such as injectable projection hooks or a registry Protocol/fake that can model `signal_internal_abort`, reservation contention, and commit ordering without direct private monkeypatching. Sequence after QW2 (AD-9(a)); do not count TD-4 as repaired by the snapshot alone.

---

## 5. Strategic Items

**None.** No P0/P1 finding requires large-effort planning. The single large-effort item — splitting `delegation_controller.py` (`SY-7`) — is **P2 and explicitly not bleeding** ("does not change the risk profile of the running system"), so it is a Watch item with a planning prerequisite, not a roadmap item. A zero strategic count is the honest reflection of an unusually clean 5-day-old codebase, not an omission.

---

## 6. Watch List

Real **latent** debt (named cost + revisit trigger), not observations. A clean codebase structurally yields latent-not-bleeding debt — that is what `watch` is for.

| ID | Title | Sev | Revisit trigger |
|----|-------|-----|-----------------|
| WL1 | **`secret_taxonomy`: 8/15 families lack pattern-level tests** (SY-16/TD-3) — safety-class; the credential gate that justified `high` stakes | P2 | Before any `secret_taxonomy.py` edit; or next security ADR. Priority family: `credential_assignment_strong`. |
| WL2 | **Crash-during-`git apply` promotion path untested** (SY-26/TD-6b) — safety-class; partial-apply mutates primary workspace, rollback asserted only by reasoning | P2 | Bundle with HL3 only if `WL6-CONCURRENT-PROMOTION-LOCK` is promoted; same blast-radius surface, but HL3 is currently deferred by policy. Both tests are unit-testable without the Codex binary. |
| WL3 | `has_capability()` never gates production dispatch (SY-2) — contract-breaking Codex upgrade fails mid-run, not at startup | P2 | If Codex CLI is upgraded past `TESTED` anywhere; pairs with HL1. May be an accepted design → see OQ3. |
| WL4 | MCP tool-prefix rename coupling has no drift guard or checklist (SY-8/AD-6+KN-5) | P2 | Before any plugin/MCP-server rename. (Doc-checklist half is a trivial opportunistic add.) |
| WL5 | `delegation_controller.py` 3367 LOC split — cohesive, not rot (SY-7/CH-1+AD-3) | P2 | If file exceeds ~4000 LOC, a second author joins, or before any major delegation refactor. Do SY-19/CH-2 dedup *as part of* this split (same fix). Prereq: helper→cluster attribution trace. HL4's supported test seams are a prerequisite that de-risk it. |
| WL6 | Worktree orphan accumulation; silent `remove_worktree()` error suppression (SY-12/OP-4) | P2 | Long-running sessions / disk pressure. Containment confirmed clean — disk/diagnosability only. |
| WL7 | Session journal files accumulate; no retention policy + spec gap (SY-13/OP-6) | P2 | Many sessions over months; pair with a `recovery-and-journal.md` retention-table addition. |
| WL8 | No oncall/recovery runbook for hung/failed delegation jobs (SY-14/OP-7) | P2 | Before any second operator / handoff (becomes P1 the first time someone else operates this). |
| WL9 | `docs/superpowers/` unrationalized extraction residue; reconciliation-register cites a load-bearing path inside it (KN-3 / `DEBT-20260517-WL9-DOCS-SUPERPOWERS-RESIDUE`) | P2 | Next docs-layout pass; resolve before more cross-refs accumulate. |
| WL10 | ADR practice sparse + partially retroactive (SY-15/KN-4) | P2 | Next significant architectural decision — produce the ADR in-flight. |
| WL11 | `slow` marker covers only live-binary tests; real slow tests unmarked (SY-22/TD-5); no MCP-level E2E with real Codex (SY-23/TD-6) | P3 | When a fast inner-loop dev run is needed; add `@pytest.mark.integration` distinct from `slow`. |

*Notes (demoted, not watch entries):* `SY-21/AD-5` (module-level approval-window env-var read frozen at import) — low confidence, test-ergonomics only; address opportunistically if touching `DelegationController.__init__`. `SY-19/CH-2` (3 copy-pasted `_group_by_latest_phase` blocks in `recover_startup`, lines 2996–3002 / 3041–3047 / 3070–3076) — not standalone; fold the `_group_by_latest_phase` extraction into the WL5 lifecycle split (architecture-drift: "deduplication and extraction become the same fix").

---

## 7. Tradeoff Map

Resource-allocation tensions with concrete anchors.

- **TR1 — Stop-the-Bleeding ↔ Build-the-Future:** HL1's cheap detection patch (CI version-consistency check + scheduled sentinel, ~2-4h) vs. WL3/SY-2's structural fix (per-call `has_capability()` dispatch guard). The sentinel stops drift-blindness but leaves the runtime gap. *Do HL1's sentinel now; schedule SY-2 only if a real Codex upgrade is anticipated (or accept it via OQ3).*
- **TR2 — Test Coverage ↔ Deploy Speed:** QW2 (the `drain_workers` seam) should reduce the local overhead currently caused by brittle parked-worker teardown; WL1/SY-16 + WL2/SY-26 *add* tests. Doing QW2 first is expected to create headroom for the safety-class test additions, but any exact wall-time improvement must be measured in the implementation PR. Anchors: `delegation_controller.py:812` seam vs. `test_credential_scan.py` / `test_journal.py` additions.
- **TR3 — Refactor ↔ Ship:** HL4 (supported delegation test seams) is a *prerequisite* that de-risks the large WL5/SY-7 split — but SY-7 itself is explicitly not-bleeding (P2). Spending large refactor capacity on SY-7 now delays the P1 quick-wins; doing HL4 captures most of the refactor-safety benefit at medium cost without the full split. *Do HL4; defer SY-7 until a real trigger fires.*
- **TR4 — Bus-Factor / Doc-as-Code ↔ Speed:** WL8 (runbook) + WL10 (forward ADR) + tracked bus-factor-1: invisible benefit until a second operator/handoff; the cost is the sole author's time now. The audit surfaces the tension; the spend decision is the user's.

---

## 8. Open Questions / Next Probes

1. **Is broad plugin distribution actively pursued?** Stakes were set `high` by conservatively assuming wide install. If this stays a single-author personal tool, WL4 (rename), WL8 (runbook), and WL1's urgency soften; if marketplace distribution is planned, several P2s escalate. Gates *escalation*, not *existence*, of those items.
2. **Is the Codex CLI version contract owned anywhere?** HL1 + WL3 both stem from the Codex CLI being out-of-band. `T-20260516-01` now owns the version-pin upgrade path; use that ticket to name the intended owner/cadence for tracking Codex releases, or to record an explicit "pin and wait for breakage" policy.
3. **Should `has_capability()`'s absence at dispatch be a guard or a documented decision?** SY-2 has no proposed fix from any single auditor — it may be an accepted design (startup-gated, not per-call). `T-20260516-02` owns the adjacent contract-version assertion decision; if that ticket records the runtime compatibility boundary, reference it here. If dispatch-time capability gating remains distinct after that decision, create a separate follow-up then rather than duplicating the current ticket lane now.
4. **What is the journal/worktree retention intent?** WL6 + WL7 both reveal the spec is silent on retention for the *operations journal* and on *mid-session* worktree cleanup. Is unbounded accumulation an accepted single-developer-machine tradeoff, or an unspecified gap? A one-paragraph spec decision closes both.

---

*Buckets derive from severity × leverage × effort per the audit rubric. Anchors and recommendations are carried from the local synthesis ledger (incl. the post-synthesis correction), with post-review precision repairs for current test counts, runnable vulnerability-scan command shape, Codex-version ticket ownership, schema-fixture skip scope, and the status-layer deferral of the concurrent-promotion lock. The local synthesis sanity checks reported severity inflation 16% current P1, quick-win inflation 12%, strategic 0%, and watch ratio ~48% after mapping HL3 to `WL6-CONCURRENT-PROMOTION-LOCK`; those ratios are not durable proof until a tracked ledger is promoted. The durable editorial decision is that every retained watch item has a named cost and revisit trigger, and the two weakest items were demoted to notes rather than padding the list. AD-9/TD-6b were incorporated after a post-shutdown re-read of revised findings files.*
