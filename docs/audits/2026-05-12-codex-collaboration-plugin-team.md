# Design Review Report — codex-collaboration plugin

**Date:** 2026-05-12
**Scope:** `system` (the whole plugin as one unit)
**Archetypes:** Internal tool + Event-driven + Trust & Safety (lead-escalated)
**Stakes:** high
**Reviewers:** structural-cognitive, behavioral, data, reliability-operational, change, trust-safety
**Lead synthesis:** SY prefix

---

## 1. Review Snapshot

| Priority | Count |
|---|---|
| P0 | 1 |
| P1 | 11 |
| P2 | 9 (+ 3 appendix) |
| **Total findings (primary)** | **21** |
| **Total with appendix** | **24** |

**Headline:** One P0 — the fail-closed credential scanning chain has a hook matcher coverage gap that lets `codex.delegate.start` reach Codex without the outer-boundary scan. Two independent reviewers converged on it from different lenses (Trust Boundary Integrity and Boundary Definition), and structural-cognitive flagged it as a **spec/implementation contradiction**: `foundations.md` claims the hook is "the authoritative enforcement point" for "delegation policy checks before job creation," but the matcher and execution prompt builder make this materially false for delegation tools. The mechanical fix is small (extend a regex + add `_redact_text` to the execution prompt builder), but the systemic shape (custom tension T-3) is broader: every component of the safety chain works in isolation; what fails is the **coverage discipline** that ensures the chain actually runs for every content-bearing tool.

A second P1 emerged post-synthesis from a data ↔ trust-safety cross-pollination: when `CLAUDE_PLUGIN_DATA` is unset, all plugin state lands in `/tmp/codex-collaboration` — world-readable on default Unix umask, with no documentation warning.

**Audit metrics:**

| Metric | Value |
|---|---|
| raw_finding_count | 36 (SC-7 + DA-4 update from shutdown-window cross-pollination) |
| canonical_finding_count | 24 |
| duplicate_clusters_merged | 6 |
| corroborated_findings | 7 (5 independent_convergence + 4 cross_lens_followup_confirmation; 2 findings have both) |
| contradictions_surfaced | 0 |
| normalization_rewrites | 2 |
| reviewers_failed | 0 |
| tensions_mapped | 3 (2 canonical, 1 custom) |

Two unrelated findings have **3-reviewer independent convergence**: SY-4 (audit retention) and SY-5 (stale marker fsync). Three findings are **cross_lens_followup_confirmation** (SY-8, SY-9, SY-13). Convergence is unusually high for a review of this size — both safety findings and durability findings showed up from multiple lenses.

**Coverage assessment:** Full — all 6 reviewers delivered findings + coverage notes. Every category has at least one finding. No `reduced-depth` label.

---

## 2. Focus and Coverage

### Scope, archetypes, stakes

The plugin is a single MCP server + control plane + storage substrate + skills/hooks/agents bundled in one repo (~14K LOC Python, 1101 tests). It bridges Claude Code (host) and Codex App Server (external untrusted runtime) via JSON-RPC, with 3 capabilities across 2 capability classes (advisory + execution). The trust model is explicit: 3-layer boundary (Claude hook guard outside the plugin, control plane policy engine in the middle, Codex sandbox inside). Crash recovery is contractually specified (fsync'd journal, audit log with TTL, idempotency keys, pending-request ordering).

Despite being a personal tool, stakes are high because of (1) credential-leakage threat on every advisory tool call, (2) code-execution surface via delegation worktree + promotion, and (3) concentrated complexity (`server/delegation_controller.py` is 3,218 lines in one class).

### Emphasis map (recap)

| Reviewer | Categories | Emphasis |
|----------|-----------|----------|
| structural-cognitive | Structural, Cognitive | background, primary |
| behavioral | Behavioral | primary |
| data | Data | secondary (lead-bumped from background) |
| reliability-operational | Reliability, Operational | secondary, primary |
| change | Change | primary |
| trust-safety | Trust & Safety | primary (lead-escalated) |

### Category status (one-liner each)

| Category | Status | Note |
|---|---|---|
| Structural | screened | Strong dependency direction, Protocol injection where it matters. Concentration in 1 file (SY-10). |
| Cognitive | deep | Spec authority resolution (SY-11), discoverability of monolith (SY-10), invariant invisibility (SY-13). |
| Behavioral | deep | 4 of 7 findings — concurrency safety, failure containment, consistency. Backpressure (SY-4) overlaps with retention. |
| Data | deep | Retention surfaces (SY-4, SY-5, SY-15), sensitivity classification (SY-16), schema governance (appendix). Datum trace clean. |
| Reliability | screened | Durability gaps real but small in scope; no SLO surface needed at this archetype. |
| Operational | deep | 4 of 6 findings. Logging config (SY-18) and worktree cleanup (SY-17) are the most concrete. |
| Change | deep | Concentration (SY-10) + extensibility blockers (SY-20) + version mismatch (SY-19). |
| Trust & Safety | deep | All 5 lenses surfaced findings. The P0 is here. Approval invariant verified clean. |

### Per-reviewer summary

- **structural-cognitive (6 findings, 1 followup):** Found the discoverability harm of the delegation controller monolith (SY-10), the spec authority↔filename gap (SY-11), and the credential-pipeline self-documentation gap (SY-21). Confirmed BH-4 from the legibility angle (SY-13).
- **behavioral (7 findings, 1 followup):** Surfaced the single-session race detection gap (SY-7), the crash-during-approval frozen state (SY-8), the stale marker fsync gap (SY-5), and the unknown-kind handler re-entry bug (SY-9). All P1.
- **data (5 findings, 2 followups):** Traced delegation job end-to-end. Confirmed SY-4 (audit retention) and SY-5 (marker fsync) from data lenses. Surfaced the asymmetric session cleanup (SY-15) and `requested_scope` sensitivity gap (SY-16).
- **reliability-operational (6 findings):** Confirmed SY-4 (durability angle) and SY-5 (durability angle). Surfaced the no-logging-config gap (SY-18), the worktree accumulation (SY-17), and the multi-axis config clarity gap (SY-19).
- **change (6 findings):** Surfaced the delegation controller monolith (SY-10) independently from structural-cognitive. Found the profile extensibility blocker (SY-20), the 3-way version split (SY-19), and the MCP tool deprecation gap (appendix SY-A1).
- **trust-safety (5 findings):** Surfaced the P0 (SY-1), the related decide-tool gap (SY-2), the broad-tier shadow-without-telemetry gap (SY-3), and the unverified sandbox carve-out (SY-6). Verified the approval invariant (advisory/execution separation) is correctly implemented.

---

## 3. Findings

Findings ordered by priority. Each finding cites the lens, decision state, anchor, problem, impact, recommendation, and corroboration evidence (where applicable).

### F1 — Hook guard matcher covers only 3 of 10 MCP tools; spec's "outer boundary" claim contradicts the actual enforcement topology

- **Priority:** P0
- **Lens:** Trust Boundary Integrity (trust-safety) / Boundary Definition (structural-cognitive)
- **Decision state:** underspecified
- **Anchor:** `hooks/hooks.json:37`, `docs/specs/foundations.md` §Outer Boundary, `server/consultation_safety.py:75-84` (`DELEGATE_START_POLICY` defined but unreachable from the hook layer), `server/execution_prompt_builder.py`
- **Problem:** `foundations.md` declares the `PreToolUse` hook guard as "the authoritative enforcement point" with explicit responsibility for "delegation policy checks before job creation" — and notes the hook "sits outside the plugin so a plugin bug cannot silently bypass it." The hook matcher in `hooks/hooks.json:37` covers only `codex.consult`, `codex.dialogue.start`, and `codex.dialogue.reply`. All 5 delegation tools (`codex.delegate.start`, `.poll`, `.promote`, `.discard`, `.decide`) plus `codex.status` and `codex.dialogue.read` are absent. `consultation_safety.py` defines scan policies for all 8 content-bearing tools including `DELEGATE_START_POLICY` and `DELEGATE_DECIDE_POLICY` — but those policies are unreachable at the outer boundary because `codex_guard.py` is never invoked for those tools. `execution_prompt_builder.build_execution_turn_text` inserts the user-supplied `objective` verbatim with no `_redact_text` call.
- **Impact:** The outer boundary as implemented is advisory-only. A credential embedded in a `codex.delegate.start` objective bypasses the outer boundary entirely and reaches Codex unscanned. The spec's claim that the hook guard "sits outside the plugin so a plugin bug cannot silently bypass it" is materially false for the higher-risk execution tools. This is a spec/implementation topology mismatch on the highest-stakes trust surface in the system, not merely a missing matcher entry.
- **Recommendation:** Extend the matcher to cover all content-bearing delegation tools (`codex\.delegate\.start`, `codex\.delegate\.decide`). Add `_redact_text` to `build_execution_turn_text` as defense-in-depth. Add an end-to-end test that asserts each content-bearing MCP tool invokes the credential scan chain. If any delegation tool exclusion is intentional, scope the spec's outer-boundary description to advisory-only and either remove or annotate the dead `DELEGATE_*_POLICY` entries.
- **Corroboration:** **independent_convergence** — trust-safety (TS-1, Trust Boundary Integrity) and structural-cognitive (SC-7, Boundary Definition, filed during shutdown-window cross-pollination after trust-safety DM). Two reviewers, two lenses, same mechanical defect with two complementary framings (security bypass + spec/implementation contradiction). Strengthens the case for P0.

---

### F2 — Hook guard matcher misses `codex.delegate.decide` answers field

- **Priority:** P1
- **Lens:** Trust Boundary Integrity
- **Decision state:** underspecified
- **Anchor:** `hooks/hooks.json:36-44`, `server/consultation_safety.py:50-53` (`DELEGATE_DECIDE_POLICY`)
- **Problem:** `codex.delegate.decide` carries an `answers` field with user-authored text replying to Codex escalations. The hook matcher does not include it, so the credential scan chain never runs. The `DELEGATE_DECIDE_POLICY` exists in `consultation_safety.py` but is dormant.
- **Impact:** Same threat class as F1, different path. A user pasting a credential into an escalation reply (e.g., responding to `request_user_input`) bypasses the outer boundary.
- **Recommendation:** Same fix bundle as F1 — extend the matcher. Revisit all delegate-tool matchers as a set to ensure coverage parity with advisory tools.
- **Corroboration:** Singleton.

---

### F3 — Broad-tier credential pattern shadows without blocking and without telemetry

- **Priority:** P1
- **Lens:** Data Sensitivity Classification
- **Decision state:** explicit tradeoff (broad tier is intentionally "shadow") but **the tradeoff itself is mis-stated as fail-closed in spec language**
- **Anchor:** `server/secret_taxonomy.py:218-229` (broad tier), `server/credential_scan.py:67-73`, `scripts/codex_guard.py:59-65` (only `block` triggers exit 2)
- **Problem:** The `credential_assignment` family (`password=`, `passwd=`, `secret=`, `credential=` followed by 6+ chars) is `broad`-tier, producing a `shadow` verdict. `codex_guard.py` exits 0 on shadow, letting the call proceed. The module comment says "telemetry not yet wired" — the call passes through with no audit event, no warning, no user-visible signal.
- **Impact:** The broad tier covers the most human-readable credential format, common in config snippets and shell commands. The fail-closed contract is materially false for this class. A `password=actual_password` in an advisory objective is silently exfiltrated.
- **Recommendation:** Either promote `credential_assignment` to `contextual` tier (block unless placeholder words present), accepting false-positive risk, OR wire shadow telemetry to emit an audit event + user-visible warning before allowing. Update spec to reflect the actual policy.
- **Corroboration:** Singleton. Linked to tension T-1 (fail-closed declaration ↔ telemetry maturity) and T-3 (fail-closed declaration ↔ coverage discipline).

---

### F4 — Audit log retention specified but not implemented; O(n) dedup compounds with growth

- **Priority:** P1
- **Lens:** Retention & Lifecycle (data) / Durability (reliability-operational) / Backpressure & Load Shedding (behavioral)
- **Decision state:** underspecified — spec contractually states the TTL and trigger, but no code enforces it
- **Anchor:** `server/journal.py:251-256`, `docs/specs/recovery-and-journal.md` (retention section)
- **Problem:** `recovery-and-journal.md` specifies "Old records are pruned on plugin startup and periodically during session" with a 30-day TTL. No pruning code exists anywhere. `events.jsonl` and `analytics/outcomes.jsonl` grow unbounded. Compounding: `append_dialogue_audit_event_once` and `append_dialogue_outcome_once` linear-scan the full file before each append to deduplicate.
- **Impact:** Long-lived installs accumulate audit/outcome records indefinitely. Per-write dedup cost grows proportionally with total history. The spec's retention contract is contradicted in code. The `AUDIT-CONSUMER-INTERFACE` open item in the reconciliation register overlaps this surface.
- **Recommendation:** Implement startup-triggered pruning in `OperationJournal.__init__` (atomic temp-rename pattern already used by `compact()`). Add a test that writes records with >30-day timestamps and asserts they are removed. Separately address the dedup scan — bound the search window to the current session, or replace with an in-memory seen-set keyed on `(action, collaboration_id, turn_id)`.
- **Corroboration:** **independent_convergence** — data (DA-1), reliability-operational (RO-1), behavioral (BH-6) all surfaced this from distinct lenses. Strongest convergence in the review.

---

### F5 — Stale advisory context marker write is not crash-safe

- **Priority:** P1
- **Lens:** Consistency Model (behavioral) / Retention & Source of Truth (data) / Durability (reliability-operational)
- **Decision state:** default likely inherited — the journal's `compact()` and `write_phase` both fsync; `_write_markers` does not, with no comment explaining the omission
- **Anchor:** `server/journal.py:408-411` (`_write_markers`), `docs/specs/recovery-and-journal.md` §Stale Advisory Context Marker (classifies as "crash-recovery state")
- **Problem:** `_write_markers` opens the file for write (truncating), calls `json.dump`, and closes — no `flush()`, no `os.fsync()`, no temp-rename. Two crash modes: (1) crash before OS flushes → marker silently lost; (2) crash mid-write → file truncated, `json.load` raises `JSONDecodeError` on next read, hard-failing every subsequent advisory path that calls `load_stale_marker`.
- **Impact:** Failure mode 1 silently breaks the post-promotion coherence injection (Codex answers questions on stale workspace state with no signal). Failure mode 2 is a hard-stop on advisory calls until manual cleanup. Spec contract is "crash-recovery state" — the write path doesn't honor that classification.
- **Recommendation:** Apply the atomic temp-rename + fsync pattern from `compact()` to `_write_markers`. Add try/except around `_read_markers` that treats `JSONDecodeError` as "absent marker" and clears the corrupt file. Add a test that simulates crash mid-write.
- **Corroboration:** **independent_convergence** — behavioral (BH-3), data (DA-2), reliability-operational (RO-2) all surfaced this from distinct lenses. BH-3 was upgraded P2→P1 via DM from data noting spec classifies the marker as recovery state.

---

### F6 — Credential-boundary sandbox carve-out (`~/.codex/memories`) not yet verified

- **Priority:** P1
- **Lens:** Least Privilege
- **Decision state:** explicit decision (carve-out is intentional) with **acceptance criterion open**
- **Anchor:** `server/runtime.py:107-130`, `docs/status/reconciliation-register.md` T-20260429-01 AC #2
- **Problem:** Execution sandbox `readableRoots` includes `~/.codex/memories` and `~/.codex/plugins/cache` but excludes `~/.codex/auth.json`, `~/.codex/config.toml`, `~/.codex/history.jsonl`. The exclusion relies entirely on the Codex App Server `restricted` sandbox correctly enforcing sub-directory boundaries — that granting read on `~/.codex/memories` doesn't grant read on `~/.codex/`. Reconciliation register lists this as unverified (T-20260429-01 AC #2).
- **Impact:** If the App Server sandbox does not enforce sub-directory boundaries (parent traversal, symlinks, directory listing), Codex running inside execution can read `auth.json` and exfiltrate OpenAI credentials. The plugin has no in-process enforcement of this — it is a declaration passed downstream.
- **Recommendation:** Close T-20260429-01 AC #2. Run a credential-boundary probe verifying Codex inside execution cannot read `auth.json` or `config.toml`. Until closure evidence exists, this is an unverified trust claim on the inner sandbox layer.
- **Corroboration:** Singleton. Reconciliation register itself corroborates the gap.

---

### F7 — Single-session race has no detection or fast-fail path

- **Priority:** P1
- **Lens:** Concurrency Safety
- **Decision state:** explicit tradeoff (README line 126 names the limitation; no remediation planned for v1)
- **Anchor:** `scripts/publish_session_id.py:37-43`, `README.md:126`
- **Problem:** Two simultaneous Claude sessions both fire `SessionStart`, both write to the shared session-id file. Last writer wins via `os.replace`. The losing session reads the post-race file and silently uses the winner's session_id for store partitioning (LineageStore, PendingRequestStore, OperationJournal, DelegationJobStore).
- **Impact:** The losing session's data is silently co-mingled under the winner's session_id. On next startup, `recover_startup` reads the wrong bucket, missing cross-session in-flight jobs. The README documents the limitation; it does not document the failure mode.
- **Recommendation:** Either (a) flock-based advisory lock in `publish_session_id.py` so the second writer blocks + logs a warning, or (b) per-session-id directory layout that doesn't share a singleton file. At minimum, document the failure mode in README and surface a `/codex-status` signal when multiple session-id files are present.
- **Corroboration:** Singleton. Linked to tension T-2 (consistency invariants ↔ recovery-time availability).

---

### F8 — Crash during active approval window leaves job permanently frozen at `needs_escalation` with no runbook

- **Priority:** P1
- **Lens:** Failure Containment (behavioral) / Recoverability (reliability-operational)
- **Decision state:** underspecified — recovery code closes journal entries without examining job liveness
- **Anchor:** `server/delegation_controller.py:1114-1119`, `:2929-2955`, `:3096-3116`
- **Problem:** When an approval is parked (`needs_escalation`), the worker thread blocks at `registry.wait(request_id)`. If the MCP server crashes after the `approval_resolution:intent` journal entry is written but before the operator decides or the timer fires, `recover_startup` finds the unresolved entry and writes `completed` — but does NOT re-examine job status. The job stays at `needs_escalation` with no live worker, no timer, and no path to resolve. `poll()` sees the job in escalation, `_project_pending_escalation` reads a `pending` request that can never resolve. There's no runbook entry and no `/codex-status` indicator distinguishing this stuck state from normal escalations.
- **Impact:** After crash + open approval + restart, the user has a job permanently stuck at `needs_escalation` that requires manual `discard`. The reconciliation loop keeps closing the journal entry as completed on each restart without fixing the job. Silent and confusing.
- **Recommendation:** In `recover_startup`'s `approval_resolution` reconciliation block, check whether the associated job is still `needs_escalation` and the pending request is still `pending`. Force-cancel via `record_internal_abort` and transition the job to `unknown`, OR document the recovery path in `poll()` output when the frozen state is detected. Add a runbook entry and a `/codex-status` indicator.
- **Corroboration:** **cross_lens_followup_confirmation** — behavioral (BH-2) surfaced the frozen-state mechanism; reliability-operational (RO-6) extended via DM with the runbook/observability angle.

---

### F9 — `_server_request_handler` lacks re-entry guard after unknown-kind interrupt

- **Priority:** P1
- **Lens:** Failure Containment
- **Decision state:** underspecified
- **Anchor:** `server/delegation_controller.py:971-1070`, `server/runtime.py:339-342`
- **Problem:** When an unknown-kind parse failure sets `interrupted_by_unknown = True` and the handler returns `None`, the notification loop continues. If a second server-request notification arrives before `turn/completed`, the handler is re-entered with no early-return guard and proceeds into the full parkable-capture branch — registering a new request in `ResolutionRegistry`, blocking at `registry.wait()`. The job is simultaneously `unknown` (persisted from first invocation, terminal status) and `needs_escalation` (from second).
- **Impact:** Incoherent state: terminal status persisted and outcome record emitted, while a live park registration exists. `poll()` projects pending escalation on an already-terminated job. `decide()` proceeds against an already-terminated job. `_finalize_turn` re-terminates to `unknown` a second time, producing duplicate outcome records.
- **Recommendation:** One-line fix: `if interrupted_by_unknown: return None` at the top of `_server_request_handler`. Same guard for `captured_request_parse_failed`.
- **Corroboration:** **cross_lens_followup_confirmation** — behavioral filed this as a followup after structural-cognitive's SC-2 cross-message about the monolith. The complexity flagged by SY-10 enabled this specific bug.

---

### F10 — `DelegationController` is a 3,218-line monolith with no internal structural boundaries

- **Priority:** P1
- **Lens:** Discoverability (structural-cognitive) / Changeability (change)
- **Decision state:** default likely inherited — no ADR explains the single-class boundary; size grew organically
- **Anchor:** `server/delegation_controller.py:399-3173`
- **Problem:** `DelegationController` contains all 5 top-level operations (`start`, `poll`, `decide`, `promote`, `discard`), the live-turn state machine (`_execute_live_turn` ~400 lines), 5 separate recovery reconciliation passes, plus utility methods. 40 methods in one class, no section markers beyond ad-hoc `# ---` inside individual methods. Cross-operation coupling is thread-mediated (`decide` → `registry.commit_signal` → unblocks `_execute_live_turn`) and invisible in the call graph.
- **Impact:** Every change in the delegation path carries the cognitive cost and regression risk of 3,218 lines. The 5 recovery passes are buried inside a single method, only navigable by grep. F9 is a concrete example: a one-line bug was enabled by the complexity. The matching test file (`tests/test_delegation_controller.py`) is 4,644 lines and mirrors the same organization problem (appendix-eligible).
- **Recommendation:** Partition along existing internal boundaries: (1) `DelegationLifecycleController` (start, poll, promote, discard, decide), (2) `DelegationRecoveryController` (startup reconciliation, orphan detection, terminal catch-up), (3) extract `_execute_live_turn` state machine into a named collaborator. The Protocol-based injection at lines 280-320 means the injected surface is already clean — work is splitting the class, not redesigning interfaces.
- **Corroboration:** **independent_convergence** — structural-cognitive (SC-2, Discoverability) and change (CH-1, Changeability) surfaced independently. DM exchange confirmed thread-mediated coupling nuance.

---

### F11 — Spec authority names decoupled from filenames with no documented resolution rule

- **Priority:** P1
- **Lens:** Legibility
- **Decision state:** default likely inherited
- **Anchor:** `docs/specs/spec.yaml:4-61`, `docs/specs/README.md:43-52`
- **Problem:** `spec.yaml` defines 7 authority names (`promotion-contract`, `advisory-policy`, `recovery-contract`, etc.) as logical identifiers. The implementing files have different names (`promotion-protocol.md`, `advisory-runtime-policy.md`, `recovery-and-journal.md`). The only way to map authority → file is to scan all `.md` files for matching `authority:` frontmatter. This resolution rule is nowhere documented. The README's reading-order table shows both columns but is non-normative (`supporting` authority).
- **Impact:** A reader following a `boundary_rules` cross-reference in `spec.yaml` cannot find the file without prior knowledge. There's no machine-verifiable link between `spec.yaml` and the files it governs. A future editor adding a new authority document may set the wrong `authority:` value.
- **Recommendation:** Add a `files:` key to each authority in `spec.yaml` naming the canonical file. Alternatively, add a short "how to find authority files" note to `spec.yaml`'s comments. Machine-checkable resolution rule.
- **Corroboration:** Singleton.

---

### F12 — Audit log lacks fsync and tamper-evidence; reserved `crash`/`restart` events not emitted

- **Priority:** P2
- **Lens:** Auditability
- **Decision state:** default likely inherited
- **Anchor:** `server/journal.py:251-255`, `docs/specs/recovery-and-journal.md:18-23`
- **Problem:** Audit log (`audit/events.jsonl`) is plain append-only JSONL — no fsync, no hash chain, no HMAC, no write-order protection. Spec describes it as "best-effort" but stated purpose is "human incident reconstruction" requiring trust. Separately, the spec reserves `crash` and `restart` audit event types but the codebase doesn't emit them.
- **Impact:** For personal-tool threat model, full cryptographic tamper-evidence is overkill. The integrity gap matters most for promotion forensics — Codex-generated code entering the workspace is a high-stakes operation where the audit trail must be trustworthy. The missing crash/restart events leave coverage incomplete for the most significant runtime moments.
- **Recommendation:** Add fsync to `append_audit_event` for trust-boundary events at minimum. Emit `crash`/`restart` events when crash recovery wiring is implemented. Explicitly acknowledge in spec that audit log is not tamper-evident.
- **Corroboration:** Singleton. Linked to tension T-1 (security ↔ operability).

---

### F13 — `turn_sequence` derivation relies on an unstructural serialization invariant

- **Priority:** P2
- **Lens:** Concurrency Safety (behavioral) / Minimal Surprise (structural-cognitive)
- **Decision state:** explicit decision (comment names the assumption; no enforcement)
- **Anchor:** `server/dialogue.py:395-398`, `:782-857`
- **Problem:** `_next_turn_sequence` derives the next 1-based sequence by reading the remote thread's completed turn count and adding 1. The comment at line 397 notes safety depends on "the MCP server keeping serialized dispatch for the accepted R1/R2 rollout posture." No lock, queue, or enforced call path makes this visible at the method boundary. The MCP server's single-call dispatch provides de-facto serialization, but the invariant lives only in a comment at the call site.
- **Impact:** A future refactor introducing concurrent advisory calls (e.g., background context refresh, multi-turn prefetch) creates idempotency-key collisions in the journal (`runtime_id:thread_id:N` reused), silently dropping turns during recovery. The coupling between MCP-layer serialization and dialogue-layer correctness is invisible from `dialogue.py`.
- **Recommendation:** Either add an in-process advisory-turn lock in the dialogue controller and enforce on `reply`, OR document the invariant in `_next_turn_sequence`'s docstring with reference to the MCP dispatch constraint. Make the dependency visible to any future caller.
- **Corroboration:** **cross_lens_followup_confirmation** — behavioral (BH-4) flagged the race assumption; structural-cognitive (SC-6) reframed it from the cognitive angle as a followup.

---

### F14 — Promotion recovery silently rolls back user manual edits

- **Priority:** P2
- **Lens:** Idempotency & Safety
- **Decision state:** default likely inherited
- **Anchor:** `server/delegation_controller.py:2999-3076` (recover_startup promotion dispatched branch), `:2310-2377` (`_verify_promotion`)
- **Problem:** When `recover_startup` encounters a `promotion:dispatched` entry (apply may have already run), `_verify_promotion` re-runs `git status --porcelain` and compares regenerated diff against reviewed diff. The check assumes the workspace is in one of two clean states. If the user manually edited the workspace between crash and restart (a realistic scenario when recovery takes a session restart), the check fails, triggering rollback that discards both Codex output AND the user's manual edits.
- **Impact:** Hard-to-detect data loss. The `rolled_back` status gives no indication user edits were present at recovery time. Spec doesn't cover the case where workspace was manually modified between crash and recovery.
- **Recommendation:** At start of the `dispatched` branch, run `git status --porcelain`; if files beyond `reviewed_changed_files` are present, skip auto-rollback and set `promotion_state="rollback_needed"` with a warning, requiring manual resolution. Document in spec promotion replay section.
- **Corroboration:** Singleton.

---

### F15 — Session-scoped store cleanup is asymmetric across 4 stores

- **Priority:** P2
- **Lens:** Retention & Lifecycle
- **Decision state:** explicit decision for `LineageStore`; underspecified for the other three
- **Anchor:** `server/lineage_store.py:185-188` (has cleanup), `server/delegation_job_store.py:36-39`, `server/pending_request_store.py:24-27`, `server/turn_store.py:35-38` (no cleanup)
- **Problem:** `LineageStore` has `cleanup()` and the spec documents session-end cleanup. The three parallel stores partition identically by `session_id` but have no cleanup method. Old session directories remain indefinitely. No orphan-scan covers them.
- **Impact:** Each session accrues 3 permanent directory trees. For daily-Claude users, linear growth across sessions. Stale-session data is dark (not exposed to current session) but occupies disk silently.
- **Recommendation:** Add `cleanup()` to `DelegationJobStore`, `PendingRequestStore`, `TurnStore` mirroring `LineageStore.cleanup()`. Wire all 4 at session-end. Add startup scan that removes session dirs older than configurable TTL (7-30 days).
- **Corroboration:** Singleton.

---

### F16 — All JSONL stores default to world-readable `/tmp/codex-collaboration` when `CLAUDE_PLUGIN_DATA` unset; `requested_scope` stores raw command payloads with no sensitivity classification

- **Priority:** P1 (upgraded from P2 after data + trust-safety cross-pollination identified the /tmp fallback affecting all stores)
- **Lens:** Data Locality / Schema Governance (data) / Data Sensitivity Classification (trust-safety)
- **Decision state:** default likely inherited — `/tmp` fallback in `journal.py:33`; explicit decision to store opaquely in `requested_scope` (`models.py:290`), but sensitivity implications + locality interaction unaddressed
- **Anchor:** `server/journal.py:33` (`/tmp/codex-collaboration` fallback), `server/approval_router.py:58-70`, `server/models.py:286-306`, `server/pending_request_store.py:253`
- **Problem:** `CLAUDE_PLUGIN_DATA` falls back to `/tmp/codex-collaboration` when the env var is unset. `/tmp` is world-readable on default Unix umask. This means **every** plugin JSONL store — pending requests, audit log, job store, lineage store, turn store — lands in a world-readable directory when the env var is absent. Documentation does not warn. Compounding this, `parse_pending_server_request` strips 4 context keys but stores the rest of App Server params into `requested_scope` as raw `dict[str, Any]` including full `commandActions` arrays (actual command lines, file paths). The `requested_scope` content is not run through `_redact_text` or the secret taxonomy before persistence, so a command argument carrying a token value (e.g., `curl -H "Authorization: Bearer sk-..."`) lands on disk unredacted. `contracts.md §Lineage Store` classifies that store as "opaque identifiers, not secrets or conversation content"; no equivalent classification exists for `PendingRequestStore`.
- **Impact:** A multi-user system with the env var unset exposes all plugin state — including command lines Codex attempted to execute, audit events, and job history — to other users via `/tmp`. Even on single-user systems, `/tmp` is typically world-readable by service accounts. A command argument carrying a token reaches disk unredacted. The /tmp default makes this a wide-surface exposure, not a single-store classification issue.
- **Recommendation:** Make `CLAUDE_PLUGIN_DATA` mandatory: fail to start (or emit loud stderr warning) when the env var is absent rather than fall back to `/tmp`. If a fallback must remain, locate it under `${HOME}/.local/share/codex-collaboration` or similar user-private directory. Add a `contracts.md §PendingRequestStore` section classifying `requested_scope` as execution-context data. Consider whether `requested_scope` should be size-bounded or run through `_redact_text` before persistence.
- **Corroboration:** **cross_lens_followup_confirmation** — data (DA-4) surfaced the `requested_scope` sensitivity gap; trust-safety extended via DM with the `/tmp` world-readable angle, broadening the surface from one store to all stores. Discovered during shutdown-window cross-pollination after the initial synthesis.

---

### F17 — Worktree disk consumption unbounded between discard and TTL expiry

- **Priority:** P2
- **Lens:** Resource Proportionality
- **Decision state:** explicit tradeoff (discard-time cleanup deferred to TTL); TTL enforcement unimplemented
- **Anchor:** `server/delegation_controller.py:2412-2431` (`discard`), `server/worktree_manager.py:61-99`, `docs/specs/recovery-and-journal.md` §Retention Defaults
- **Problem:** `discard()` marks job `discarded` and emits audit event but does not call `remove_worktree`. Spec documents 1h TTL for completed worktrees, 24h for failed/crashed. Cleanup deferred to TTL-based scan at startup — but no startup worktree scan exists. The spec's "Abandoned sessions → Next startup → Scan for orphaned runtimes/worktrees" row is unimplemented.
- **Impact:** Worktrees from discarded and crashed jobs accumulate in `${CLAUDE_PLUGIN_DATA}/runtimes/delegation/`. Each worktree is a full git checkout. Over many delegations, significant disk consumption with no automatic recovery short of manual deletion.
- **Recommendation:** Add startup scan to `recover_startup()` (or separate `_cleanup_stale_worktrees()` called from MCP server init) that removes worktrees for terminal-state jobs older than TTL. Closes the gap between spec and implementation.
- **Corroboration:** Singleton.

---

### F18 — No logging configuration — structured diagnostics silently discarded

- **Priority:** P2
- **Lens:** Observability
- **Decision state:** default likely inherited
- **Anchor:** `server/delegation_controller.py:115`, `server/mcp_server.py:16`, `server/worker_runner.py:29`, `server/runtime.py:18`, `scripts/codex_runtime_bootstrap.py`
- **Problem:** Five server modules call `logging.getLogger(__name__)` and emit structured messages at DEBUG/WARNING/ERROR. No `basicConfig`, `StreamHandler`, or log-level config anywhere in bootstrap or server code. Python's default logging silently discards `logger.warning/error` calls. Separately, `control_plane.py` and `dialogue.py` use `print(..., file=sys.stderr)` as fallback — two inconsistent observability channels.
- **Impact:** A user debugging "why did delegation mark the job unknown" cannot see the structured error from `_mark_execution_unknown_and_cleanup` because it was silently discarded. The only observable signal is the job state itself. Diagnostic path is significantly harder than necessary.
- **Recommendation:** Add `logging.basicConfig(level=logging.WARNING, stream=sys.stderr)` to `codex_runtime_bootstrap.py`. Routes all existing structured logs to stderr — consistent with MCP stdio transport — zero behavior change for callers. Add `CODEX_COLLAB_LOG_LEVEL` env var.
- **Corroboration:** Singleton.

---

### F19 — Configuration clarity gaps + 3-way plugin version mismatch

- **Priority:** P2
- **Lens:** Configuration Clarity (reliability-operational) / Versioning & Migration (change)
- **Decision state:** explicit decision (acknowledged in AGENTS.md as migration debt) with **no enforcement** of sync
- **Anchor:** `server/delegation_controller.py:117-156`, `README.md:135`, `.claude-plugin/plugin.json:3`, `pyproject.toml:3`, `server/runtime.py:159`
- **Problem:** Three distinct gaps converged: (1) `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS` read at module load; restart requirement only documented in README, not at code site; (2) no config inventory enumerating `CODEX_COLLAB_*` env knobs; (3) plugin version split 3 ways — `plugin.json` declares `0.2.0`, `pyproject.toml` declares `0.1.0`, `runtime.py:159` hardcodes `"0.1.0"` in the `clientInfo` handshake. The App Server always sees `0.1.0` regardless of `plugin.json` value, so `/codex-status` surfaces a different identity than the Claude Code plugin registry.
- **Impact:** User who sets the env var and restarts Claude (not the plugin) sees no effect with no warning. Plugin reports a different version to the Codex App Server than to the Claude Code plugin registry — diagnostics that cross-reference both see inconsistent identity. Diagnostic confusion under migration-provenance framing.
- **Recommendation:** Add `# Plugin restart required — read at module load` comment at config site. Add config inventory to README. Resolve the 3-way version split — drive `runtime.py:159` from `pyproject.toml` dynamically via `importlib.metadata.version("codex-collaboration")`, or pin all three to same value with sync comment. A pre-commit version-sync check would eliminate the class of error.
- **Corroboration:** **independent_convergence** — reliability-operational (RO-5) and change (CH-3) both surfaced this; change added the `runtime.py:159` detail; reliability-operational incorporated it.

---

### F20 — Profile extensibility blocked by single-value `Literal` types + hard validation gate

- **Priority:** P2
- **Lens:** Extensibility
- **Decision state:** explicit tradeoff — `profiles.py:4` and `advisory-runtime-policy.md` §Current Packet 1 Behavior intentionally restrict pending freeze-and-rotate implementation
- **Anchor:** `server/profiles.py:25-26`, `:149-157`, `docs/specs/advisory-runtime-policy.md:73`
- **Problem:** `SandboxPolicy = Literal["read-only"]` and `ApprovalPolicy = Literal["never"]` are single-value Literal types. The resolver hard-rejects any other value with "not yet implemented". Adding a new sandbox mode or approval policy requires (1) widening Literals, (2) removing the validation gate, (3) implementing freeze-and-rotate, (4) updating callers. Steps 3-4 are significant; steps 1-2 are entangled with step 3 — no incremental path.
- **Impact:** Freeze-and-rotate is documented in `advisory-runtime-policy.md §Future-Scope` but not ticketed and has no `delivery.md` milestone. If a new posture (e.g., `network_access=True`) becomes necessary before freeze-and-rotate is built, there is no partial rollout path. Phased profiles are rejected at runtime with no defined implementation timeline.
- **Recommendation:** Add a ticket tracking freeze-and-rotate with profile extensibility as acceptance criterion. As a lower-cost interim measure, add `SandboxPolicy` and `ApprovalPolicy` extension points to `delivery.md` so the dependency is visible in the delivery plan.
- **Corroboration:** Singleton.

---

### F21 — Credential scanning pipeline (4 modules) is well-structured but not self-documenting

- **Priority:** P2
- **Lens:** Layering & Abstraction
- **Decision state:** explicit tradeoff
- **Anchor:** `scripts/codex_guard.py:49`, `server/consultation_safety.py:1-7`, `server/credential_scan.py:1-7`, `server/secret_taxonomy.py:1-10`
- **Problem:** The 4 modules form a clean vertical pipeline: `secret_taxonomy` (patterns) → `credential_scan` (tiered logic) → `consultation_safety` (per-tool policy + traversal) → `codex_guard` (hook entry point). Each module has a docstring for its own role; none describes the chain.
- **Impact:** A developer adding a new pattern can find `secret_taxonomy.py`. A developer asked "explain the credential scanning chain" has no single document or code location to start from. For a fail-closed safety subsystem — especially given F1, F2, F3 reveal callers do not always know what is or isn't enforced — the chain should be self-documenting.
- **Recommendation:** Add 1-2 lines to `consultation_safety.py`'s module docstring describing the pipeline (`secret_taxonomy → credential_scan → consultation_safety → codex_guard`) with each layer's responsibility boundary. Cheap and removes oral-tradition dependency.
- **Corroboration:** Singleton. Adjacent to T-3 (fail-closed declaration ↔ coverage discipline).

---

## Appendix Findings

### F-A1 — No MCP tool deprecation policy

- **Priority:** P2 (appendix)
- **Source:** CH-4
- **Problem:** All 10 MCP tools referenced by full name in skill `allowed-tools`. No deprecation policy in `contracts.md`/`delivery.md`/`decisions.md`. `codex.dialogue.fork` removal in `decisions.md:146` was treated as permanent replacement with no consumer-impact mention.
- **Recommendation:** Add deprecation policy to `contracts.md` covering coexistence period, caller notification mechanism, atomic-update process across skills. Document that plugin/package rename is a breaking change.

### F-A2 — Codex CLI upgrade procedure does not reference schema diff tool

- **Priority:** P2 (appendix)
- **Source:** CH-5
- **Problem:** `delivery.md` defines 6-step upgrade procedure but does not mention `scripts/compare_app_server_schemas.py` (509 lines, structured schema-diff tool). Unclear whether required, ad hoc, or retrospective.
- **Recommendation:** Add step: "Run `compare_app_server_schemas.py` and review output for breaking changes before proceeding." Alternatively, document as optional-but-recommended.

### F-A3 — No plugin-internal schema versioning on any storage format

- **Priority:** P2 (appendix)
- **Source:** DA-5
- **Problem:** All 5 JSONL stores use "extra fields ignored / missing optional fields default" policy. No `schema_version` field. Inconsistent application — `lineage_store.py` raises `SchemaViolation` for unknown literals; `delegation_job_store.py` silently skips records with `TypeError` without logging.
- **Recommendation:** Add `schema_version: int = 1` to records. Centralize forward-compat policy as shared module comment. Lower-urgency at current scale but the schema is actively evolving.

---

## 4. Tension Map

### T1 — Fail-closed credential contract ↔ Operational telemetry maturity (CT-4)

- **Sides:** Security (fail-closed contract declared in spec + policy map) ↔ Operability (telemetry consumer surface, audit retention, observable shadow events)
- **What's being traded:** The plugin declares a fail-closed credential scanning chain. The operational machinery that would make the chain trustworthy at runtime — telemetry consumers wired up, bounded audit retention, observable shadow events — is unbuilt. Each side considers their work done; the seam between them is unmonitored.
- **Why it hid:** Security wrote the scanning policies, verdict tiers, and guard script — and that side is internally consistent. Operational treated audit retention as deferred per spec language calling the audit log "best-effort." The shadow tier (F3) needs telemetry to be more than fail-open. Telemetry needs bounded retention (F4) to be sustainable. Neither reviewer's lens by itself surfaces this dependency.
- **Likely failure story:** A credential matches a `broad`-tier pattern (`password=...`), `codex_guard` exits 0 (shadow verdict), the call proceeds, no event is emitted because the telemetry consumer is unwired, and the audit log either doesn't capture it or captures it in an unbounded file no one reads. The fail-closed contract is materially false for this credential class.
- **Linked findings:** F3, F4, F12

---

### T2 — Consistency invariants ↔ Recovery-time availability (CT-6)

- **Sides:** Consistency (single-session, concurrency=1 invariants documented in spec) ↔ Availability (no automated path to restore service when invariants are silently violated or crashes occur)
- **What's being traded:** The system protects consistency by limiting itself to single-session and concurrency=1. When those invariants are silently violated (F7 session race) or when crashes strand state inside the invariant (F8 frozen approval), there is no automated availability restoration and no documented manual recovery either.
- **Why it hid:** The consistency invariants are explicit and central (foundations.md §Approval Invariant, recovery-and-journal.md §Concurrency Limits). The availability cost only manifests during specific edge cases (two simultaneous sessions; crash mid-approval) and the recovery code closes journal entries without reasoning about job-state liveness.
- **Likely failure story:** User runs delegation, gets an escalation, machine crashes before deciding. After restart, the job sits at `needs_escalation` with no live worker, no timer, no `/codex-status` signal, and the user has no documented action other than `discard`. Or: user has two Claude sessions, session B's delegation jobs write under session A's session_id partition, session B's recovery cannot find its own jobs.
- **Linked findings:** F7, F8

---

### T3 — Fail-closed declaration ↔ End-to-end coverage discipline (CT-8, custom)

- **Sides:** Stated fail-closed contract (spec + policy map + verdict tiers + guard script) ↔ Hook matcher coverage (which content-bearing tools actually invoke the guard)
- **What's being traded:** Every component of the safety chain is internally consistent. The hook matcher in `hooks/hooks.json` covers 3 of 10 tools, so for the 7 uncovered tools the chain is unreachable. The fail-closed contract — and the spec's explicit claim that the hook handles "delegation policy checks before job creation" — is materially false without any single component being wrong in isolation. The dead `DELEGATE_START_POLICY` and `DELEGATE_DECIDE_POLICY` definitions in `consultation_safety.py` make this contradiction visible from inside the source tree.
- **Why it hid:** Each component was correct in its own scope. The matcher was authored when the advisory tools shipped; delegate tools were added later without extending the matcher; the policy map was extended without anyone checking that the matcher caught up. No end-to-end test verifies the chain runs for every content-bearing tool. The framing notes correctly observed that the 4 scanning modules sit at different boundary layers — but did not check that each layer covers the same tool surface. Two reviewers independently surfaced this from different lenses (trust-safety: bypass mechanism; structural-cognitive: spec/implementation topology contradiction), confirming the gap is visible from multiple architectural angles.
- **Likely failure story:** A user calls `codex.delegate.start` with an objective containing `export AWS_SECRET_ACCESS_KEY=...`. The matcher doesn't fire. `execution_prompt_builder` inserts the objective verbatim. The credential reaches Codex unscanned. The plugin's own `DELEGATE_START_POLICY` was written and ready, sitting in `consultation_safety.py` dormant. Even if telemetry were wired (per T-1), there would be no signal because the hook never ran.
- **Linked findings:** F1, F2, F3
- **Reviewers involved:** trust-safety, structural-cognitive

---

## 5. Questions / Next Probes

1. **Was the hook matcher coverage gap (F1, F2) introduced by a specific change?** Reviewing the git history of `hooks/hooks.json` would confirm whether the matcher was written for advisory tools and never extended when delegate tools shipped, or whether the omission was intentional (e.g., earlier design where delegate.start had a different content-bearing surface). The answer changes whether the fix should be "extend matcher" or "rethink delegate content path."

2. **What is the planned closure date for T-20260429-01 AC #2 (credential-boundary sandbox probe)?** F6 depends entirely on this probe. Closing it would either retire F6 or surface a concrete sandbox enforcement gap that warrants higher priority. The reconciliation register tracks it but does not name a target.

3. **Does the "best-effort" classification for the audit log (recovery-and-journal.md) actually match the system's needs?** F4, F5, and F12 all reveal that "best-effort" in spec language has become "no durability machinery" in code. The spec uses one word; the implementation chose 4-5 specific defaults that may not all be intended. A spec-level decision about which audit/marker stores need fsync vs which truly are best-effort would clarify the boundary instead of leaving each module to inherit a default.

4. **Is the freeze-and-rotate protocol on the roadmap, or has it been quietly deferred?** F20 names this as the blocker for profile extensibility. `advisory-runtime-policy.md §Future-Scope` documents the design; `delivery.md` does not list a milestone. If freeze-and-rotate is deferred indefinitely, the validation gate's "not yet implemented" message will become misleading over time.

5. **What is the intended life of the migration provenance debt?** AGENTS.md names the version mismatch (F19) as inherited from extraction. CH-3 / RO-5 found a third version site (`runtime.py:159`) the original note didn't anticipate. A planned "migration-debt sweep" would scope this — otherwise each new place that touches version identity will be discovered ad hoc.

---

## Closing note

The plugin has unusually mature spec discipline for a single-user tool — 7 authority documents, an explicit precedence graph, boundary rules for cross-spec review, and a documented migration manifest. The findings cluster in two patterns: **(a) declared-vs-implemented gaps** where the spec promises something the code doesn't deliver (F4 retention, F5 fsync, F6 sandbox probe, F8 recovery completeness, F17 worktree TTL), and **(b) coverage-discipline gaps** where each component is correct in isolation but the chain is unreachable for some surface (F1, F2, F3 — captured as tension T-3). The first pattern is straightforward to remediate: implement what the spec already promises. The second pattern requires a new kind of test — end-to-end coverage assertions that pin every content-bearing MCP tool to the credential scan chain — and is the highest-leverage architectural commitment the review surfaces.
