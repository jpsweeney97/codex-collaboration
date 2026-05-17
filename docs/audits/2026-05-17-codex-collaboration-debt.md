# Tech Debt Audit — codex-collaboration

**Audit initiated:** 2026-05-16 · **Finalized:** 2026-05-17
**Scope:** `system` (whole repository) · **Stakes:** `high` (trust-boundary safety substrate + autonomous code execution)
**Archetypes:** Single-author project (high confidence) + Greenfield-on-legacy (med-high)
**Method:** Fresh independent re-audit. 6 category-scoped auditors, parallel, **blind to all prior audits**, lateral cross-lens messaging, lead synthesis. No auditor suppressed (high stakes).

---

## 1. Audit Snapshot

| Severity | Count | | Bucket | Entries |
|----------|-------|---|--------|---------|
| P0 | **0** | | Quick Wins | 3 |
| P1 | 5 | | High-Leverage | 4 |
| P2 | 13 | | Strategic | **0** |
| P3 | 7 | | Watch | 11 (+2 notes) |
| **Canonical** | **25** | | | |

**Headline:** A genuinely clean, disciplined, young codebase. Six independent auditors found **zero P0** and only **five P1s** — none in code-health, architecture, or dependency *correctness*. The strongest signal is a **3-auditor independent convergence**: the OpenAI Codex CLI is the system's primary external trust dependency and **no CI gate detects its drift** (`SY-1`, from `DP-1`+`AD-4`+`TD-2`). A cross-lens chain (test-debt → architecture-drift Playbook #4) surfaced **`AD-9`**, a *named missing seam* upstream of two test-debt findings — the audit's clearest high-leverage lever. The largest module (`delegation_controller.py`, 3367 LOC) was investigated and **disconfirmed as a god-module** — cohesive, P2, watch — a deliberate non-inflation.

**Audit metrics:** raw 34 → canonical 25 · 6 duplicate clusters merged · 6 corroborated · **1 contradiction surfaced and resolved** (Codex "fail-open" mischaracterization corrected by architecture-drift's call-graph trace → reframed as `SY-2`) · ~26 schema normalizations · 0 auditors failed · 4 tradeoffs mapped.

**Coverage:** 6/6 categories deep. No `auditors_failed`. Severity distribution (0% P0, 20% P1) is conservative and honest — no inflation; the disconfirmation discipline visibly held (a 3.4× LOC outlier was talked *down* from a god-module hypothesis, not up).

> **Note on revision:** Auditors continued cross-lens refinement after the initial synthesis draft; findings files were re-read on team shutdown. `AD-9` and `TD-6b` were added; `TD-1`/`TD-4` were re-anchored to `AD-9`. This report reflects the final state.

---

## 2. Focus and Coverage

- **Scope:** `system`, single level. **Stakes:** `high` → +1 deep-lens cap on primary auditors, no suppression.
- **Archetypes:** Single-author (one author/email across 100% of commits → bus factor 1 *by construction*) + Greenfield-on-legacy (extracted from `claude-code-tool-dev` monorepo 2026-05-11, 5 days before audit).
- **Emphasis map:** primary = architecture-drift, test-debt, knowledge, **operational (lead-escalated** — the runtime-safety surface IS the product's core risk); secondary = code-health, dependency.

| Category | Status | One-line |
|----------|--------|----------|
| Code Health | deep | Clean. One cohesive size outlier (not rot), two P3 duplications. 64 broad-except verified disciplined, not a smell. |
| Architecture Drift | deep | Extraction import-clean. Composition-root lacks Protocol seams (P2); Codex version window zero-tolerance (P2); no god-module; **named the AD-9 missing test seam (high leverage)**. |
| Dependency | deep | PyPI surface clean *as of 2026-05-16* by **manual** point-in-time cross-ref (no scanner in CI). All real risk is the out-of-band Codex CLI. |
| Test Debt | deep | Exceptional depth (1178 tests). ~50s/run thread-leak (structurally forced); Codex wire-contract gate frozen at 0.117.0; 8/15 secret families untested; partial-`git apply` crash path untested. |
| Operational | deep | No root log handler; crash/restart audit events unimplemented; concurrent-session promotion race. Containment boundary confirmed architecturally clean. |
| Knowledge | deep | Spec/ADR layer unusually rich. `delivery.md` omits 2 security-adjacent modules; `docs/superpowers/` is unrationalized extraction residue (load-bearing ref). |

**Per-auditor summary:** code-health 3 · architecture-drift 9 · dependency 2 (+4 clean sentinels) · test-debt 7 · operational 8 · knowledge 5 (+3 clean coverage notes).

---

## 3. Quick Wins

Start here — sprint-startable, high ROI.

### QW1 — Configure a logging root handler *(P1, leverage: high, effort: small)*
- **category:** operational · **anchor:** `scripts/codex_runtime_bootstrap.py` `main()`; all modules use `logging.getLogger(__name__)` · **source:** SY-3 / OP-1
- **Problem:** `codex_runtime_bootstrap.py` never calls `logging.basicConfig()`. Python's `lastResort` handler emits only WARNING+ to stderr, unformatted. Every DEBUG/INFO record (job IDs, session IDs, worktree paths, transition states) is silently dropped.
- **Impact:** When a delegation hangs, the operator has no structured diagnostic record. Compounds OP-2/OP-4/OP-5 — their evidence is invisible without this.
- **Recommendation:** Add a minimal `basicConfig` call at the top of `main()` writing to stderr with a structured format (timestamp, level, logger name, message); use a `CODEX_COLLAB_LOG_LEVEL` env var defaulting to `WARNING`. Document the env var in README's Configuration table.
- **Why #1:** P1 + one-line fix + highest leverage (unblocks the observability 3 other findings depend on).

### QW2 — Add the `drain_workers` seam (the structural fix for the ~50s CI overhead) *(P1, leverage: high, effort: small)*
- **category:** architecture-drift / test-debt · **anchor:** `server/delegation_controller.py:812` (`spawn_worker(...)` — return value discarded) + `server/worker_runner.py:112-116` · **source:** SY-25 / AD-9(a) + TD-1
- **Problem:** `DelegationController.start()` discards the `threading.Thread` from `spawn_worker(...)`; there is no `_worker_threads` collection and no `drain_workers` method. Tests have *no alternative* but to enumerate by name (`threading.enumerate()` filtered by `"delegation-worker-job-1"`); two integration tests leak workers, and the process-wide name match blocks 5 bounded-poll teardowns at 5s each — **~50s of an 84s CI suite**.
- **Impact:** ~50s on every push (high-velocity single-author repo). The thread-name brittleness is structurally forced by the missing seam — not test sloppiness.
- **Recommendation:** Add `_worker_threads: list[threading.Thread]` to `DelegationController.__init__`, capture `self._worker_threads.append(spawn_worker(...))`, add `drain_workers(timeout: float = 5.0) -> None` that joins each tracked thread; tests call `controller.drain_workers()` in teardown — name enumeration goes away. **This is a 1–2h structural fix, not a test-quality patch.** *Short-term workaround before the seam lands:* add `controller.decide()` or an explicit worker-exit signal in `test_start_returns_escalation_on_parked` teardown.
- **Note:** This is AD-9(a). Its sibling AD-9(b) (`_snapshot_for_test`) is HL4. Independent of the SY-7 module-split (the seam gap survives any split).

### QW3 — Documentation & config hygiene sweep *(cluster: P2/P3, leverage: low–medium, effort: small — bundle, ~½ day)*
Independently-trivial fixes worth shipping as one chunk:
- **SY-18 / KN-1:** README.md, AGENTS.md, `.claude/CLAUDE.md` say "1172 tests"; actual is 1178 → update to 1178 (or "~1180" to stop drift).
- **SY-9 / KN-2+AD-6:** `docs/specs/delivery.md` component tree omits `server/tool_prefix.py` and `server/turn_extraction.py` (the `tool_prefix → consultation_safety → credential-scan gate` path is spec-invisible) → add both with a one-line role description each.
- **SY-10 / DP-2:** No vulnerability scanner in CI → add `uv run pip-audit` as a CI step + a `dependabot.yml` (pip ecosystem). *(< 5 min; trust-boundary hardening.)*
- **SY-20 / CH-3:** Promote `_CANCEL_CAPABLE_KINDS` from duplicated method-locals (`delegation_controller.py:1068`, `:2559`) to a module-level constant beside `_ESCALATABLE_REQUEST_KINDS`.
- **SY-24 / OP-8:** Log the resolved `plugin_data_path` at INFO during startup; add a README note that `CLAUDE_PLUGIN_DATA` defaults to `/tmp/codex-collaboration` (ephemeral on macOS reboots).
- **AD-4(c):** Sync `pyproject.toml` version (`0.1.0`) to `plugin.json`'s `0.2.0` (inherited extraction mismatch; 10 min).
- **SY-11(opt 3) / OP-5:** Add a comment documenting the `jsonrpc_client.py` `deque(maxlen=200)` cap and that it may truncate long-running error context.

---

## 4. High-Leverage Fixes

Each removes downstream pain or protects the highest-blast-radius surface. Ordered by downstream unblock breadth, then severity.

### HL1 — Make Codex CLI contract/version drift visible to CI *(P1, leverage: high, effort: medium)*
- **category:** dependency + architecture-drift + test-debt (3-auditor independent convergence) · **source:** SY-1 / DP-1 + AD-4 + TD-2
- **anchor:** `server/codex_compat.py` (`TESTED_CODEX_VERSION = "0.117.0"`, `MINIMUM_CODEX_VERSION = "0.117.0"`); `server/jsonrpc_client.py` (`["codex", "app-server"]` from PATH); `tests/test_codex_wire_contract.py` / `conftest.py` `schema_loader` `pytest.skip()`; `tests/fixtures/codex-app-server/0.117.0/`; `.github/workflows/ci.yml` (no Codex binary)
- **Problem:** The Codex CLI is the primary runtime trust peer, **declared in no manifest and monitored by no CI gate**. `TESTED == MINIMUM == 0.117.0` (zero tolerance); the wire-contract test fixture *skips* (not fails) when the schema is missing; live tests skip without the binary. Drift is invisible until a user hits a runtime failure.
- **Impact:** Silent regression class on the system's core function (autonomous Codex execution). A push to `main` with a stale compat pin passes all checks.
- **Unblocks:** dependency (DP-1), architecture (AD-4 seam), test-debt (TD-2 gate); downstream-compounds OP-5/SY-2/SY-4 Codex-crash diagnosis.
- **Recommendation (one shared remediation + verbatim residuals in ledger):** Add a CI `version-check` job validating `TESTED_CODEX_VERSION` matches the vendored fixture directory name (DP-1 low-cost); add a scheduled (weekly) CI job installing the latest Codex CLI and running the compat check, **or at minimum alert when the installed version exceeds `TESTED_CODEX_VERSION`** (AD-4b); short-term change `schema_loader`'s missing-file behavior from `skip` to `xfail`/`fail` (TD-2); widen `TESTED_CODEX_VERSION` ahead of `MINIMUM` for a tolerance range (AD-4a); document the 5-step manual upgrade as a PR-checklist item (DP-1).

### HL2 — Implement the reserved `crash`/`restart` audit events *(P1, leverage: high, effort: medium)*
- **category:** operational · **anchor:** `docs/specs/recovery-and-journal.md` §Reserved Audit Events; `server/journal.py` · **source:** SY-4 / OP-2
- **Problem:** The spec reserves `crash`/`restart` audit event types but no code emits them. On crash, in-flight journal entries have an incomplete final phase; `recover_startup()` marks jobs `unknown` with no correlating audit record — recovery is *reconstructed*, not *recorded*.
- **Impact:** Post-crash forensics require cross-referencing JSONL + host stderr + poll output. An operator cannot distinguish "crashed mid-promotion" from "crashed pre-dispatch" from audit alone. Compounds the Codex cluster (a version-mismatch crash leaves no structured trace). Complementary to SY-26 (OP-2 = missing record; SY-26 = unverified recovery behavior).
- **Recommendation:** Best-effort `crash` write on unhandled exception + SIGTERM (wrap `server.run()` in try/finally calling `journal.append_audit_event({"type": "crash", ...})`; register a SIGTERM handler); emit `restart` at the top of `main()` after the prune/recovery step. Best-effort (no fsync per spec).

### HL3 — Harden the concurrent-session promotion race *(P1, leverage: high, effort: medium)*
- **category:** operational · **anchor:** `scripts/publish_session_id.py`; `server/delegation_controller.py` promotion prechecks; `README.md` Limitations · **source:** SY-5 / OP-3
- **Problem:** The only guard against two sessions racing the `HEAD == base_commit` precheck is a 60s startup-time stderr warning in `publish_session_id.py` — it fires at SessionStart, not promotion, and blocks nothing. Two sessions can both pass the point-in-time check; the second applies its diff to the wrong base.
- **Impact:** Blast radius is the user's **primary workspace git state** (not a sandboxed worktree). A corrupted promotion is not automatically reversible — manual `git log` forensics + reset. Highest-consequence finding in the audit.
- **Recommendation:** Emit a pre-promotion audit event recording the lock attempt; add an atomic `O_CREAT | O_EXCL` advisory lockfile (`.promotion-in-progress` in `plugin_data_path`) checked/written before the HEAD precondition and removed on completion/rollback; move concurrent-session detection to promotion time, not just session start.

### HL4 — Add the `_snapshot_for_test` state-inspection seam *(P2, leverage: high, effort: medium)*
- **category:** architecture-drift / test-debt · **anchor:** `server/delegation_controller.py` (no inspection surface beyond `poll()`); `tests/test_delegation_controller.py` (5028 LOC, 107 tests, 40+ `object.__setattr__`/private-attr sites) · **source:** SY-25 / AD-9(b) + TD-4
- **Problem:** `DelegationController` exposes no narrow seam for tests to observe intermediate state (`_project_pending_escalation`, capture-channel invocation). Tests are *structurally forced* into 40+ private-attribute reads and `object.__setattr__` spy injection. Confirmed by architecture-drift as a distinct gap that **survives any module split** (independent of SY-7).
- **Impact:** Every one of the 40+ coupling sites forces a simultaneous test rewrite on any `delegation_controller` internals refactor. This is the structural reason the module is refactor-hostile — fixing it de-risks every future change to the system's core execution path.
- **Unblocks:** TD-4 (40+ sites collapse), and is the prerequisite that makes a future SY-7 lifecycle split safe rather than test-breaking.
- **Recommendation:** Add a narrow `_snapshot_for_test()` method (or a `DelegationControllerState` dataclass) exposing only the state fields tests legitimately need, replacing the `object.__setattr__` spy pattern with a supported inspection surface. Sequence after QW2 (AD-9(a)).

---

## 5. Strategic Items

**None.** No P0/P1 finding requires large-effort planning. The single large-effort item — splitting `delegation_controller.py` (`SY-7`) — is **P2 and explicitly not bleeding** ("does not change the risk profile of the running system"), so it is a Watch item with a planning prerequisite, not a roadmap item. A zero strategic count is the honest reflection of an unusually clean 5-day-old codebase, not an omission.

---

## 6. Watch List

Real **latent** debt (named cost + revisit trigger), not observations. A clean codebase structurally yields latent-not-bleeding debt — that is what `watch` is for.

| ID | Title | Sev | Revisit trigger |
|----|-------|-----|-----------------|
| WL1 | **`secret_taxonomy`: 8/15 families lack pattern-level tests** (SY-16/TD-3) — safety-class; the credential gate that justified `high` stakes | P2 | Before any `secret_taxonomy.py` edit; or next security ADR. Priority family: `credential_assignment_strong`. |
| WL2 | **Crash-during-`git apply` promotion path untested** (SY-26/TD-6b) — safety-class; partial-apply mutates primary workspace, rollback asserted only by reasoning | P2 | Bundle with HL3 (same blast-radius surface). Both tests are unit-testable without the Codex binary. |
| WL3 | `has_capability()` never gates production dispatch (SY-2) — contract-breaking Codex upgrade fails mid-run, not at startup | P2 | If Codex CLI is upgraded past `TESTED` anywhere; pairs with HL1. May be an accepted design → see OQ3. |
| WL4 | MCP tool-prefix rename coupling has no drift guard or checklist (SY-8/AD-6+KN-5) | P2 | Before any plugin/MCP-server rename. (Doc-checklist half is a trivial opportunistic add.) |
| WL5 | `delegation_controller.py` 3367 LOC split — cohesive, not rot (SY-7/CH-1+AD-3) | P2 | If file exceeds ~4000 LOC, a second author joins, or before any major delegation refactor. Do SY-19/CH-2 dedup *as part of* this split (same fix). Prereq: helper→cluster attribution trace. HL4 is a prerequisite that de-risks it. |
| WL6 | Worktree orphan accumulation; silent `remove_worktree()` error suppression (SY-12/OP-4) | P2 | Long-running sessions / disk pressure. Containment confirmed clean — disk/diagnosability only. |
| WL7 | Session journal files accumulate; no retention policy + spec gap (SY-13/OP-6) | P2 | Many sessions over months; pair with a `recovery-and-journal.md` retention-table addition. |
| WL8 | No oncall/recovery runbook for hung/failed delegation jobs (SY-14/OP-7) | P2 | Before any second operator / handoff (becomes P1 the first time someone else operates this). |
| WL9 | `docs/superpowers/` unrationalized extraction residue; reconciliation-register cites a load-bearing path inside it (SY-…/KN-3) | P2 | Next docs-layout pass; resolve before more cross-refs accumulate. |
| WL10 | ADR practice sparse + partially retroactive (SY-15/KN-4) | P2 | Next significant architectural decision — produce the ADR in-flight. |
| WL11 | `slow` marker covers only live-binary tests; real slow tests unmarked (SY-22/TD-5); no MCP-level E2E with real Codex (SY-23/TD-6) | P3 | When a fast inner-loop dev run is needed; add `@pytest.mark.integration` distinct from `slow`. |

*Notes (demoted, not watch entries):* `SY-21/AD-5` (module-level approval-window env-var read frozen at import) — low confidence, test-ergonomics only; address opportunistically if touching `DelegationController.__init__`. `SY-19/CH-2` (3 copy-pasted `_group_by_latest_phase` blocks in `recover_startup`, lines 2996–3002 / 3041–3047 / 3070–3076) — not standalone; fold the `_group_by_latest_phase` extraction into the WL5 lifecycle split (architecture-drift: "deduplication and extraction become the same fix").

---

## 7. Tradeoff Map

Resource-allocation tensions with concrete anchors.

- **TR1 — Stop-the-Bleeding ↔ Build-the-Future:** HL1's cheap detection patch (CI version-consistency check + scheduled sentinel, ~2-4h) vs. WL3/SY-2's structural fix (per-call `has_capability()` dispatch guard). The sentinel stops drift-blindness but leaves the runtime gap. *Do HL1's sentinel now; schedule SY-2 only if a real Codex upgrade is anticipated (or accept it via OQ3).*
- **TR2 — Test Coverage ↔ Deploy Speed:** QW2 (the `drain_workers` seam) *reduces* CI time (~50s); WL1/SY-16 + WL2/SY-26 *add* tests. Doing QW2 first creates the headroom to absorb the safety-class test additions without slowing the loop. Anchors: `delegation_controller.py:812` seam vs. `test_credential_scan.py` / `test_journal.py` additions.
- **TR3 — Refactor ↔ Ship:** HL4 (state-inspection seam) is a *prerequisite* that de-risks the large WL5/SY-7 split — but SY-7 itself is explicitly not-bleeding (P2). Spending large refactor capacity on SY-7 now delays the P1 quick-wins; doing HL4 captures most of the refactor-safety benefit at medium cost without the full split. *Do HL4; defer SY-7 until a real trigger fires.*
- **TR4 — Bus-Factor / Doc-as-Code ↔ Speed:** WL8 (runbook) + WL10 (forward ADR) + tracked bus-factor-1: invisible benefit until a second operator/handoff; the cost is the sole author's time now. The audit surfaces the tension; the spend decision is the user's.

---

## 8. Open Questions / Next Probes

1. **Is broad plugin distribution actively pursued?** Stakes were set `high` by conservatively assuming wide install. If this stays a single-author personal tool, WL4 (rename), WL8 (runbook), and WL1's urgency soften; if marketplace distribution is planned, several P2s escalate. Gates *escalation*, not *existence*, of those items.
2. **Is the Codex CLI version contract owned anywhere?** HL1 + WL3 both stem from the Codex CLI being out-of-band. Is there an intended owner/cadence for tracking Codex releases, or is the implicit policy "pin and wait for breakage"? Naming the policy is half the fix.
3. **Should `has_capability()`'s absence at dispatch be a guard or a documented decision?** SY-2 has no proposed fix from any single auditor — it may be an accepted design (startup-gated, not per-call). If accepted, it deserves an ADR naming the runtime failure mode (ties to WL10); if not, it's a real seam to add.
4. **What is the journal/worktree retention intent?** WL6 + WL7 both reveal the spec is silent on retention for the *operations journal* and on *mid-session* worktree cleanup. Is unbounded accumulation an accepted single-developer-machine tradeoff, or an unspecified gap? A one-paragraph spec decision closes both.

---

*Buckets derived from severity × leverage × effort per the audit rubric. Anchors and recommendations carried verbatim from the synthesis ledger (incl. the post-synthesis correction). Sanity checks: severity inflation 20% (pass), quick-win inflation 12% (pass), strategic 0% (pass, honest — no P0/P1 large item exists), watch ratio ~44% — marginally exceeds the 40% guard; retained deliberately because every watch item is real latent debt with a named cost and revisit trigger (a clean codebase structurally yields latent-not-bleeding debt), and the two weakest items were demoted to notes rather than padding the list. AD-9/TD-6b were incorporated after a post-shutdown re-read of revised findings files.*
