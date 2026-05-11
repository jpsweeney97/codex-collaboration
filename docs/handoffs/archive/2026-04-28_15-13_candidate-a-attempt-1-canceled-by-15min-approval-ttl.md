---
date: 2026-04-28
time: "15-13"
created_at: "2026-04-28T19:13:43Z"
session_id: 15267690-603e-4715-be76-9c90ba41007a
resumed_from: docs/handoffs/archive/2026-04-28_17-13_candidate-a-patch-staged-and-pre-variant-evidence-locked.md
project: claude-code-tool-dev
branch: feature/delegate-execution-diagnostic-record
commit: 5a1e937e
title: Candidate A attempt 1 canceled by 15-min approval TTL; mechanism revision (untrusted-mode parking is sandbox-policy-invariant)
type: handoff
files:
  - docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md
  - packages/plugins/codex-collaboration/server/runtime.py
  - .tmp/variant-candidate-a.patch
  - .tmp/variant-candidate-a.applied-at
---

# Handoff: Candidate A attempt 1 canceled by 15-min approval TTL; mechanism revision needed

## Goal

Continue T-20260423-01 live delegate-execution remediation. **This session executed Candidate A attempt 1** with the patched runtime built and verified post-restart, fired `codex_delegate_start` with the canonical smoke prompt, and observed: (a) plugin correctly built `includePlatformDefaults: True` policy (runtime-proof confirmed); (b) App Server still parked `/bin/zsh -lc` at `command_approval` despite the True flag; (c) the deny adjudication failed because the job was already canceled — `approval_timeout` fired at +15m10s after start by `actor=system`.

**Three load-bearing findings emerged:**
1. **Runtime-proofed `True` flag**: `'includePlatformDefaults': True` was the actual emitted policy; this disambiguates "plugin built wrong policy" from "App Server interprets True restrictively."
2. **Mechanism revision**: Baseline's analysis (run record line 639) claimed parking was sandbox-driven (`/bin/zsh` unreachable under `False` → park). Candidate A's parking under `True` refutes this: parking is **sandbox-policy-invariant** under `untrusted` approval mode. The actual primary blocker is approval-policy gating that runs BEFORE sandbox readability check.
3. **Approval TTL discovered**: ~15-minute window between `delegate_start` parking and auto-cancellation. This is a hard plugin/App Server lifecycle constraint that affects variant-cycle methodology going forward.

**Connection to project arc:** Branch S1 ("Sandbox still blocked") needs re-classification — the sandbox isn't the primary mechanism. Candidate B (per-binary `readableRoots` additions) is now likely a wrong-direction escalation since it changes sandbox grants, but parking happens upstream of sandbox check. Need a different intervention class (e.g., approval-policy override, pre-authorized approve, or trusted-mode test) for the next variant.

**Stakes:** Methodology-altering findings. The TTL constraint changes how every future variant cycle must be operated. The mechanism revision changes the variant-strategy roadmap.

## Session Narrative

Resumed from `2026-04-28_17-13_candidate-a-patch-staged-and-pre-variant-evidence-locked.md`. The prior session left a deliberate restart boundary with the Candidate A patch staged on disk; operator restart had to happen before this session's work would observe the patched code.

**Pre-flight verification (Next Steps #3) — 9 GREEN checks** in parallel: new plugin PIDs `64122/64184/64213` (≠ prior `7116/7163/7165`); runtime.py diff = 37 lines; patch applied at `2026-04-28T17:12:59Z`; patch sha256 `4df1df3999…` matches captured; plugin session_id flipped to `15267690-…` (= THIS session); plugin start UTC `2026-04-28T17:24:44Z` is +705s after patch; runtime-proof log absent; codex CLI version still `0.125.0` (schema bundle valid); working tree shape matches expected (1 M + 8 D + 8 ??).

Three small craft observations during pre-flight: (1) `ps -p PID -o lstart=` returns 4 trailing spaces from column-padding that `date -j` warns about but parses correctly (`%Y` consumes 4 digits then stops); (2) skipped `codex_status` per user's explicit path-forward, deferring to the start-call as primary health probe; (3) plugin's `session_id` file automatically tracked the new claude session UUID, providing independent restart corroboration.

**Variant block instantiation (Next Steps #4) — DONE.** Read run record at lines 540-700 (template + Cross-variant checks) and 620-820 (Baseline block for shape reference). Verified live HEAD `5a1e937eff04f4cfecf5ce7bc65fae1f94db0fca` matches handoff. Mirrored byte-for-byte equality check between live working-tree diff and `.tmp/variant-candidate-a.patch` (exit 0 — empty diff). Composed Candidate A variant block: 7 pre-execution cells filled (Pre-run HEAD, Pre-run dirty diff, Patch capture form, Patch applied at, Policy diff, PIDs+session_id, Plugin process start timestamp); 25+ post-execution cells marked `TBD (post-execution; expected source: X)` with explicit falsification criteria where applicable; inline patch diff in code block; Attempt history with attempt 1 row. Inserted between Baseline raw excerpts and `## Threshold Calibration` section. Run record grew 990 → 1087 lines (+97); new anchor at line 826.

**Step #5 — `codex_delegate_start` invocation.** User authorized via /copy-routed scrutiny. Fetched the deferred MCP tool schemas via `ToolSearch select:` syntax (codex_status, codex_delegate_start, codex_delegate_poll, codex_delegate_decide). Fired with `repo_root: /Users/jp/Projects/active/claude-code-tool-dev` and `objective: <canonical smoke prompt verbatim with 20260428T005625 baked in>`; `base_commit` omitted to default to HEAD.

**Critical observation: Candidate A also parked at `command_approval`.** start() returned `status: needs_escalation`, `parked_request_id: "0"`, `pending_escalation.kind: command_approval`, `requested_scope.command: /bin/zsh -lc "..."` (compressed `&&`-chain, 7 steps; same autopilot pattern as Baseline incl. `.codex-collaboration/test-results.json` over-action). `available_decisions: ["approve", "deny"]` at the wire surface. `proposedExecpolicyAmendment` present (S7a fired — informational under untrusted-mode per S7 split).

Captured runtime-proof immediately to disambiguate "plugin built wrong policy" from "App Server interprets True restrictively": `/tmp/codex-collab-candidate-a-runtime-proof.log` showed `2026-04-28T17:51:27.685062+00:00 [CANDIDATE_A] sandboxPolicy={... 'includePlatformDefaults': True ...}`. **Plugin correctly built True policy — App Server still parked.** Three independent UTC clocks consistent: patch `17:12:59Z` < plugin start `17:24:44Z` < runtime-proof emit `17:51:27Z`.

Surfaced findings + decision matrix (deny / approve / deny-then-separate-approve). User used `$making-recommendations` skill to evaluate; chose (c): deny now to mirror Baseline + plan separate approve attempt as Candidate A attempt 2.

**Decide rejected: `job_not_awaiting_decision`, status `canceled`.** The decide call returned `{"rejected": true, "reason": "job_not_awaiting_decision", "detail": "Delegation decide failed: job not awaiting decision. Got: status='canceled'"}`. Polled to confirm: `status: canceled`, `pending_escalation: null`, `inspection: null`. Job had transitioned out of awaiting-decision before my decide arrived.

**Cause investigation via JSONL stores.** Grepped audit/events.jsonl + jobs.jsonl + requests.jsonl + journal/operations for the job_id `4ebd24d6-…`. **Smoking gun in audit: `2026-04-28T18:06:37Z action=approval_timeout actor=system request_id=0`** — exactly +15m10s after `delegate_start` at `17:51:27Z`. The plugin (`actor=system`) auto-cancels parked jobs after a fixed approval TTL. jobs.jsonl showed lifecycle: create → running → parked(0) → needs_escalation → (timeout fires) → running → park-cleared → canceled. So timeout flow is graceful unblock-then-cancel rather than hard kill.

Surfaced to user with three options (save / fill-cells / fire-attempt-2). User again used `$making-recommendations`; chose (a) save handoff now. Reasons: cancellation evidence is durable on disk (audit, jobs, runtime-proof); attempt 2 needs a deliberate cycle with pre-authorized approve to land within TTL; mechanism revision is the load-bearing finding worth capturing cleanly. Invoked `handoff:save` skill, which is producing this handoff.

## Decisions

### D1: Pre-flight verified before any state-changing action

**Choice:** Run all 9 pre-flight checks (PIDs, diff, patch hash, applied-at, session_id, start-UTC, log-absence, codex-version, working-tree-shape) before any state change.

**Driver:** Handoff's explicit Next Steps #3 + carried strict-gate-before-action user preference. Pre-flight verifies operator restart cycle completed correctly + patch survived + plugin loaded patched code; these are foundational for variant-cycle validity.

**Rejected alternatives:**
- **Skip pre-flight, fire delegate_start directly** — would defer detection of restart anomaly until delegate behavior was confused; harder to debug.
- **Subset pre-flight (just PID + diff)** — under-tests methodology; lower confidence in variant validity.

**Implication:** Variant validity is anchored cleanly. If anomaly had surfaced, would have stopped before delegate_start; in this session, all 9 GREEN.

**Confidence:** High (E2) — methodology directly inherited from Baseline and prior session.

**Reversibility:** N/A — read-only checks.

**Change trigger:** If pre-flight ever produces a false-positive (passes but variant later reveals plugin loaded stale code), add additional checks (e.g., import-time fingerprint).

### D2: Pre-execution cells filled now (vs commit-now or defer-all)

**Choice:** Instantiate Candidate A variant block with 7 pre-execution cells filled + 25 TBD cells marked with expected sources. NOT committed.

**Driver:** Pre-execution evidence is fresh; transcription accuracy maximal now. Committing pre-only would be a "half-row" inconsistent with project's bundled-closure pattern (Baseline's commit covered pre+post in one).

**Rejected alternatives:**
- **Defer everything to post-execution** — risks losing pre-flight context if anything in delegate_start changes interpretation. Also denies future-Claude a structural anchor.
- **Commit pre-execution cells now** — creates phase boundary but defeats bundled-closure shape; multiple commits per variant is anti-pattern in this project.

**Implication:** Variant block has clear pre/post split. Future-Claude can fill TBDs from disk-resident evidence (audit, jobs, runtime-proof) without re-deriving pre-flight.

**Confidence:** High (E2).

**Reversibility:** High — markdown edits are trivial to revert.

**Change trigger:** If next session reveals the TBD framing introduces ambiguity (e.g., reader can't distinguish "TBD because not yet captured" from "TBD because variant didn't surface this"), adjust template guidance.

### D3: Canonical smoke prompt verbatim (no modification for ≥3 actions)

**Choice:** Use the canonical smoke prompt from spec line 237-240 verbatim with `20260428T005625` substituted. Did NOT add explicit "make this ≥3 distinct shell calls" prescription.

**Driver:** User: "Do not modify the prompt to force ≥3 shell-visible actions. That would weaken cross-variant comparability for a secondary metric. Candidate A's load-bearing question is simpler: does `includePlatformDefaults: True` allow shell execution to reach the point of creating [the artifact]?" Cross-variant comparability with Baseline is paramount.

**Rejected alternatives:**
- **Modified prompt forcing ≥3 actions** — would diverge from Baseline's prompt; ratio interpretation gain is secondary metric.
- **Custom prompt (e.g., simpler test command)** — would change variant semantics entirely.

**Implication:** Delegate compressed into single chained command (same as Baseline). Denominator < 3, ratio uninterpretable per Branch Precedence #1.d. But primary question (does parking happen?) is independent of action count. As predicted, parking happened — same shape as Baseline.

**Confidence:** High (E2) — directly user-validated; outcome consistent with prediction.

**Reversibility:** High — prompt choice is per-attempt.

**Change trigger:** If a future attempt needs to distinguish ratio-driven vs unconditional-parking findings, modify the prompt then.

### D4: Recommended deny over approve (not executed due to timeout)

**Choice:** Recommended (a) deny mirroring Baseline. User chose (c) deny-now-then-separate-approve.

**Driver (mine):** Methodology fit (characterization first, intervention second). Mechanism revision (untrusted-mode unconditional parking) was already established by parking-with-True-flag observation alone; approving doesn't add evidence to that question; it adds evidence to a different question (does execution work past the gate).

**User's refinement:** "Attempt 2 = approve" should be a **separate variant cycle** (new delegate_start, fresh job) per variant-isolation discipline. Attempts within one job lifecycle cannot mix decision strategies cleanly.

**My structural refinement:** Within the run record, this fits as **Candidate A attempt 2** (same variant block, second row in Attempt history table) — not a new variant block — since the policy patch is unchanged and only the decision strategy differs.

**Outcome:** Decide(deny) on req 0 was rejected because job had already canceled by timeout. Attempt 1 ended as `canceled-by-approval-timeout`, NOT `deny-completed`.

**Confidence:** Medium (E1 → revised) — hypothesis was sound; execution failed for orthogonal reason (TTL).

**Reversibility:** Attempt 1 is now sealed as canceled. Cannot retroactively make it "as if" deny had landed.

**Change trigger:** TTL discovery itself is the change trigger — future deny attempts must land within 15min window or be redesigned.

### D5: Save handoff over fill-cells-now or fire-attempt-2-now

**Choice:** Option (a) — save handoff with cancellation findings; defer cell filling and attempt 2 to next session.

**Driver:** Context budget at 88-94% across the deliberation. Cancellation evidence on disk (audit, jobs, runtime-proof, requests) is durable — next session can fill cells without re-deriving. Attempt 2 needs a deliberate cycle with pre-authorized approve; firing it under context pressure has wrong risk profile (live TTL race + potential mid-cycle OOM). Mechanism revision is the load-bearing insight worth a clean handoff capture.

**User's framing (via $making-recommendations):** "Attempt 2 would start another irreversible live cycle while the session is already context-constrained and while TTL timing has just proven operationally material… 'verifiably best' for this session boundary."

**Rejected alternatives:**
- **(b) Fill cancellation cells now** — tempting for artifact completeness, but at 88% context risks ending with partial run-record edit + handoff explaining a half-edit.
- **(c) Fire attempt 2 immediately** — highest evidence yield but worst risk profile; could OOM mid-cycle OR repeat the TTL timeout if approve adjudication is delayed.

**Implication:** This handoff is the durable artifact. Cell filling becomes next session's first task. Attempt 2 is its own cycle.

**Confidence:** High (E2) — both my analysis and user's $making-recommendations independently arrived at (a).

**Reversibility:** N/A — saving handoff is purely additive; nothing to undo.

**Change trigger:** Never; clean session boundaries are the project pattern.

## Changes

### `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — Candidate A variant block instantiated (NOT committed)

**Purpose:** Capture Candidate A attempt 1's pre-execution evidence in the canonical Per-Variant Evidence template format, before delegate execution.

**Approach:** Mirror Baseline's block structure exactly. Preamble identifies tightenings carried forward + this-variant additions (session_id cross-check, distinct log filename). Cells filled cell-by-cell with explicit "Source / fill guidance" + "Observation"; post-execution cells marked `TBD (post-execution; expected source: X)` with falsification criteria where applicable.

**Key implementation details:**
- Inserted at line 826 (between Baseline raw excerpts at 824 and `## Threshold Calibration` at 826-pre-edit)
- File grew 990 → 1087 lines (+97)
- 7 pre-execution cells filled: Pre-run HEAD (`5a1e937e`), Pre-run dirty diff (with byte-for-byte verification), Patch capture form (sha256 anchor), Patch applied at (`2026-04-28T17:12:59Z`), Policy diff/patch under test (combined behavioral + instrumentation), Plugin process PID (`64213` evidentiary + uv `64184` + claude `64122` + session_id corroboration), Plugin process start timestamp (raw + normalized + ordering check + cross-clock plan)
- 25+ post-execution cells with TBD framing
- Inline patch diff in fenced code block after table
- Attempt history table with attempt 1 in-progress row
- Raw excerpts placeholder

**Future-Claude note:** Cells need updates post-cancellation for attempt 1: Observed sandboxPolicy payload (filled from runtime-proof line, captured in this handoff), poll() transitions (start → canceled, no decide reached), audit row for `approval_timeout`, attempt history outcome ("canceled-by-approval-timeout"). The Variant restoration command + Restoration verification + Cleanup performed cells should NOT be filled until attempt 2 is also complete (per VIP step 7: restoration is once-per-variant, not once-per-attempt).

### Plugin data root — new artifacts from this session (gitignored, durable)

**Purpose:** Audit trail for Candidate A attempt 1.

| File | What it contains |
|------|------------------|
| `~/.claude/plugins/data/codex-collaboration-inline/audit/events.jsonl` | 2 new rows: L65 `delegate_start` at `17:51:27Z`; L66 `approval_timeout` at `18:06:37Z` (`actor=system`, `request_id=0`) |
| `~/.claude/plugins/data/codex-collaboration-inline/delegation_jobs/15267690-.../jobs.jsonl` | 7 lifecycle rows for job `4ebd24d6-…`: create(queued) → running → parked(0) → needs_escalation → running(unpark) → parked(cleared) → canceled |
| `~/.claude/plugins/data/codex-collaboration-inline/pending_requests/15267690-.../requests.jsonl` | 2 rows: op:create for request 0; op:mark_resolved (or similar) — needs inspection next session |
| `~/.claude/plugins/data/codex-collaboration-inline/journal/operations/15267690-...jsonl` | OperationJournal with job_creation + (likely) approval_timeout op |

### `/tmp/codex-collab-candidate-a-runtime-proof.log` — runtime-proof artifact (1 line, 533 bytes)

**Purpose:** Direct evidence the live runtime built the patched policy with `True` flag.

**Content (verbatim, preserved here):**
```
2026-04-28T17:51:27.685062+00:00 [CANDIDATE_A] sandboxPolicy={'type': 'workspaceWrite', 'writableRoots': ['/Users/jp/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/4ebd24d6-6f1f-45b8-99eb-0d890a9d5326/worktree'], 'readOnlyAccess': {'type': 'restricted', 'readableRoots': ['/Users/jp/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/4ebd24d6-6f1f-45b8-99eb-0d890a9d5326/worktree'], 'includePlatformDefaults': True}, 'networkAccess': False, 'excludeSlashTmp': True, 'excludeTmpdirEnvVar': True}
```

**Critical for next session:** TRASH this file before attempt 2's delegate_start, OR the next emit will append below this line and the read-back will conflate attempts. Per Baseline restoration recipe: `trash /tmp/codex-collab-candidate-a-runtime-proof.log`.

### No commits this session

All work is in-progress on the variant block + dirty runtime.py + .tmp/ artifacts. Closure commit deferred until attempt 2 + Branch decision adjudication update + restoration are also complete.

## Codebase Knowledge

### Files read this session

| File | Why read | Understanding gained |
|------|----------|----------------------|
| `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` lines 540-565 | Cross-variant checks + VIP step 7 reference | Restoration is once-per-variant; runtime-proof-only instrumentation is exempt from no-patch rule |
| `docs/diagnostics/...` lines 567-625 | Per-Variant Evidence template (`### Variant: TBD`) | 30+ cell template; post-execution structure; falsification cells |
| `docs/diagnostics/...` lines 626-820 | `### Variant: Baseline (attempt 1)` block | Cell-by-cell shape reference; preamble structure; raw excerpts pattern; cross-clock consistency table |
| `docs/diagnostics/...` lines 232-263 | Smoke Objective + Policy Variants | Canonical prompt; reuse-timestamp policy; expected ≥3 shell-visible actions; Candidate B matrix scope |
| `.tmp/variant-candidate-a.patch` | Inline diff for variant block | Combined flag flip + instrumentation overlay; 37 lines unified |
| `packages/plugins/codex-collaboration/server/runtime.py:23-50` | Verify on-disk state of patched policy builder | Lines 23-50 contain `policy = {...}` (renamed from `return {...}`); flag at line 33 = `True`; instrumentation block 38-49 with `[CANDIDATE_A]` label |

### Architecture: process chain + lifecycle

| Layer | Location | Role this session |
|-------|----------|-------------------|
| Sandbox policy builder | `runtime.py:23-50` | Builds `workspaceWrite` policy with True flag; emits to file for proof; returns dict |
| Plugin process chain | `64122 (claude)` → `64184 (uv)` → `64213 (python)` | Three-layer codex-collaboration plugin process tree; python child holds the imported runtime.py |
| App Server | Codex CLI 0.125.0 spawned per delegation | Receives sandbox policy from plugin; enforces approval gating BEFORE sandbox check (mechanism revision) |
| DelegationJobStore | `<plugin-data-root>/delegation_jobs/<session-uuid>/jobs.jsonl` | 7 rows trace canceled lifecycle |
| PendingRequestStore | `<plugin-data-root>/pending_requests/<session-uuid>/requests.jsonl` | 2 rows for canceled request 0 |
| Audit | `<plugin-data-root>/audit/events.jsonl` | Single shared file; new rows L65-L66 |
| OperationJournal | `<plugin-data-root>/journal/operations/<session-uuid>.jsonl` | Per-session ops log |
| Approval TTL | UNKNOWN config location | Hard ~15min window between start and timeout |

### Patterns identified (this session)

- **Approval TTL is graceful unblock-then-cancel:** jobs.jsonl shows park-cleared → running → canceled rather than direct cancel-from-parked. Suggests App Server returns the request unresolved, plugin clears park state, then transitions job to canceled. Implication: timeout doesn't dispose mid-flight state abruptly.
- **`actor=system` in audit events:** distinct from `actor=claude` (orchestrator-initiated decisions). System events include lifecycle automation like `approval_timeout`. Useful for filtering audit by "what the operator did" vs "what the system did automatically."
- **`available_decisions` wire vs store:** wire-surface `pending_escalation.available_decisions` shows `["approve", "deny"]` (2 options); PendingRequestStore L1 op:create likely shows full 6-option list (matching Baseline pattern). Don't use wire-surface as ground truth for S7 amendment classification.
- **Decide is one-shot:** if rejected with `job_not_awaiting_decision`, the job has terminated (canceled, completed, or failed). Always poll first if there's any latency between start and decide.

### Surprising findings (this session)

- **15-min TTL, not the 5-min I initially guessed.** Audit events.jsonl made the actual window discoverable (delta between `delegate_start` and `approval_timeout` rows).
- **Mechanism revision: untrusted-mode parking is sandbox-policy-invariant.** The Baseline run record's mechanism analysis (line 639) was based on a single-data-point inference. Candidate A directly refutes it.
- **`proposedExecpolicyAmendment` is not a sandbox-readability signal.** It fires for both Baseline (False flag) and Candidate A (True flag), confirming S7a's "informational under untrusted" classification. The amendment payload is purely about offering operators a future-permission shortcut, not about the current command's parking decision.
- **Plugin re-import semantics worked correctly.** Despite my prior worry about "patch on disk but in-memory might be stale," runtime-proof confirmed the post-restart import picked up the patched policy builder.

### Key locations

| Concept | Location |
|---------|----------|
| Sandbox policy builder (post-patch, live) | `packages/plugins/codex-collaboration/server/runtime.py:23-50` |
| Run record (live HEAD: `5a1e937e` + dirty Candidate A block at line 826) | `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` |
| Candidate A variant block | run record lines 826-922 |
| Candidate A attempt 1 audit rows | `audit/events.jsonl` L65-L66 |
| Candidate A attempt 1 jobs lifecycle | `delegation_jobs/15267690-…/jobs.jsonl` (7 rows) |
| Candidate A attempt 1 requests | `pending_requests/15267690-…/requests.jsonl` (2 rows) |
| Candidate A attempt 1 runtime-proof | `/tmp/codex-collab-candidate-a-runtime-proof.log` (1 line, 533 bytes) |
| Patch capture | `.tmp/variant-candidate-a.patch` (sha256 `4df1df3999…`) |

## Context

### Project State

| Item | State |
|------|-------|
| Branch | `feature/delegate-execution-diagnostic-record` at `5a1e937e` (in sync with origin) |
| Run record | Live HEAD includes Candidate A variant block (pre-execution cells filled, 25+ TBD post-execution cells) |
| Run Identity table | Frozen at `49d93001`; live drift to `5a1e937e` |
| Sandbox blocker (Candidate A att1) | **Confirmed: parking occurs even with `includePlatformDefaults: True`** — refutes Baseline's sandbox-driven mechanism |
| Plugin process | PIDs `64122/64184/64213`; in-memory code is PATCHED (Candidate A: True flag + `[CANDIDATE_A]` instrumentation) |
| Candidate A patch on disk | Still applied (NOT restored) — preserved for attempt 2 |
| Patch applied at | `2026-04-28T17:12:59Z` |
| Plugin start | `2026-04-28T17:24:44Z` (+705s after patch) |
| Approval TTL constraint | ~15 minutes (NEW finding; need investigation) |
| Working tree | Dirty: `M runtime.py` + `M docs/diagnostics/...` (run record edits) + 8 carry-forward `docs/tickets/closed-tickets/` moves |
| Runtime-proof log | 1 line on disk (attempt 1 emit); MUST trash before attempt 2 |
| Pushed to origin? | Last push at `5a1e937e`; NO new commits this session |

### Mental Model

**Mechanism revision (load-bearing):** Branch S1 ("Sandbox still blocked") was based on Baseline's analysis that `/bin/zsh` unreachable → park. Candidate A demonstrates parking under `True` flag (where `/bin/zsh` SHOULD be reachable via platform defaults). The two parking observations together support: under `untrusted` approval mode, App Server parks every shell command unconditionally at `command_approval` BEFORE sandbox readability check. Sandbox grants affect what would happen IF the command were approved (e.g., would it succeed at runtime), but approval gating is the upstream blocker.

**Implications for variant strategy:**
- Candidate B (per-binary `readableRoots` additions) is likely a **wrong-direction escalation** — it changes sandbox grants, but parking happens upstream of sandbox check. Won't help.
- Candidate A attempt 2 (approve-strategy) is the next clean experiment: does shell execute past the gate under True flag? Distinguishes "sandbox is blocking too" from "sandbox is fine, only approval was blocking."
- Trusted-mode test would be the orthogonal experiment: does the parking go away if approval policy is `trusted` rather than `untrusted`? Confirms the mechanism revision.

**Three independent UTC sources cross-checked successfully** for attempt 1:
- Patch applied: `2026-04-28T17:12:59Z`
- Plugin start: `2026-04-28T17:24:44Z` (+705s)
- Runtime-proof emit: `2026-04-28T17:51:27.685062Z` (+1603s after start)
- Audit `delegate_start`: `2026-04-28T17:51:27Z` (matches runtime-proof to sub-second)
- Audit `approval_timeout`: `2026-04-28T18:06:37Z` (+15m10s after start)

### Environment

- Working tree: `feature/delegate-execution-diagnostic-record` at `5a1e937e` (in sync with origin)
- Codex: `codex-cli 0.125.0` (unchanged from prior session)
- Local timezone: `EDT (-0400)`
- Plugin process: PIDs `64122/64184/64213`; started `2026-04-28T17:24:44Z` UTC; in-memory code is PATCHED (Candidate A)
- Plugin data root: `~/.claude/plugins/data/codex-collaboration-inline/`
- Plugin's current session_id: `15267690-603e-4715-be76-9c90ba41007a` (matches THIS session)
- macOS Darwin 25.4.0; shell zsh

## Learnings

### Approval TTL is ~15 minutes — variant-cycle methodology constraint

**Mechanism:** Plugin (or App Server) auto-cancels parked jobs at exactly `delegate_start_timestamp + ~15min` via `approval_timeout` event. `actor=system` confirms self-initiated. Job lifecycle: needs_escalation → (timeout fires) → running → park-cleared → canceled. The timeout flow is graceful, not abrupt.

**Evidence:** `audit/events.jsonl` rows for job `4ebd24d6-…`:
- L65: `2026-04-28T17:51:27Z action=delegate_start actor=claude request_id=None`
- L66: `2026-04-28T18:06:37Z action=approval_timeout actor=system request_id=0`
- Delta: exactly 15m10s.

**Implication:** Any operator-mediated decide must complete within ~15min of start. The /copy-routed scrutiny round-trip pattern can eat into this budget — between start and my deny call, the cycle was: read parked response → capture runtime-proof → compose recommendation → user reads /copy + uses $making-recommendations → user responds → I send decide. That sequence took ~15min and the timeout fired first.

**Watch for:** Future variant cycles where deny/approve adjudication needs operator review. Mitigation options: (1) pre-authorize the decision before firing start; (2) skip /copy round-trip for known-mirror cases (e.g., Candidate B's deny-mirror); (3) investigate where TTL is configured and whether tunable.

### Mechanism revision: untrusted-mode parking is sandbox-policy-invariant

**Mechanism:** App Server's `command_approval` parking is upstream of sandbox readability check. Under `untrusted` approval policy, parking happens for `/bin/zsh -lc <chain>` regardless of whether `/bin/zsh` is reachable under the current sandbox grant.

**Evidence:** Two data points across variants (with everything else equal):
- Baseline (`includePlatformDefaults: False`): parked at `command_approval` for `/bin/zsh -lc`
- Candidate A (`includePlatformDefaults: True`, runtime-proofed): parked at `command_approval` for `/bin/zsh -lc`

If parking were sandbox-driven, flipping the flag would eliminate parking. It didn't.

**Implication:** Branch S1 ("Sandbox still blocked") in current Branch Precedence may be misclassified for what it's actually catching. The actual primary blocker for delegate-execution is approval-policy gating, not sandbox grants. Candidate B (per-binary `readableRoots` additions) is likely wrong-direction since it intervenes on sandbox; the right next intervention class is approval-policy (e.g., approve-strategy attempt 2, or trusted-mode test).

**Watch for:** Updates to Symptom Attribution rows (S1 may need rewording) and Branch Precedence rules (re-rank approval-policy branches).

### Decide is one-shot; always poll first under any latency

**Mechanism:** `codex_delegate_decide` checks `job.status == 'awaiting_decision'` before applying the decision. If the job has transitioned out of that state (via timeout, completion, etc.), decide returns `{"rejected": true, "reason": "job_not_awaiting_decision", "detail": ...}`.

**Evidence:** This session's decide(deny) on req 0 was rejected because the job had canceled in between start and decide. Subsequent poll confirmed `status: canceled, pending_escalation: null`.

**Implication:** Whenever there's any latency between `start()` and `decide()` (including operator-mediated review), poll first to confirm the job is still awaiting. Otherwise the decide call is wasted and the agent flow can't continue.

**Watch for:** Any future automation that wraps decide — should poll first. Manual operator workflow should also default to poll-then-decide if more than ~30s elapsed since start.

### Plugin re-import correctly picks up disk patches across restart boundary

**Mechanism:** Python's import-once semantics are bypassed by full process restart. The new process imports `runtime.py` from disk → patched code is loaded. No need for `importlib.reload()` or other dynamic mechanisms.

**Evidence:** Runtime-proof emit at `17:51:27Z` showed `'includePlatformDefaults': True` — confirming the post-restart plugin imported the patched module. Patch was on disk before restart (applied `17:12:59Z`); restart at `17:24:44Z`; first import-time was during plugin bootstrap (immediately after restart); first emit was on first delegate call (`17:51:27Z`).

**Implication:** The full-restart variant-cycle pattern is durable. Don't need to worry about hot-reload semantics; the operator restart IS the reload mechanism.

**Watch for:** If anything ever bypasses the operator restart (e.g., long-running plugin process across multiple variants without restart), in-memory code can drift from disk. Pre-flight's PID + start-time check is the safety net.

## Next Steps

### 1. New session: `/handoff:load`

Picks up THIS handoff and archives it. Auto-resolves session continuity.

### 2. New session: pre-flight verification (lighter than full session)

Check (no full restart needed since plugin still has patched code in memory):
- `ps -ef | grep codex-collaboration | grep -v grep` — verify plugin PIDs are still `64122/64184/64213` (or new ones if user restarted between sessions; if new, derive plugin start UTC and verify > patch applied)
- `git diff packages/plugins/codex-collaboration/server/runtime.py | wc -l` — should still be ~37 (Candidate A patch present)
- `cat .tmp/variant-candidate-a.applied-at` — `Patch applied at: 2026-04-28T17:12:59Z`
- `shasum -a 256 .tmp/variant-candidate-a.patch` — `4df1df3999…`
- `cat /tmp/codex-collab-candidate-a-runtime-proof.log` — should still show 1 line from attempt 1 (DO NOT trash yet — capture timestamp into cells first, THEN trash before attempt 2)

### 3. New session: fill Candidate A attempt 1 post-execution cells

Source data is durable on disk. Cells to fill (in run record at lines 826-922):
- **Observed `sandboxPolicy` payload**: from runtime-proof line preserved in this handoff's Changes section
- **Approval policy value**: inferred `untrusted` (S7a payload-presence + 6-option list pattern from Baseline carries; though for canceled job, the wire only showed 2-option `[approve, deny]`)
- **Job id**: `4ebd24d6-6f1f-45b8-99eb-0d890a9d5326`
- **Runtime id**: `84fce58f-c860-4757-a852-6f30c3d21ddf`
- **Collaboration id**: `9a8a1a64-65b7-4884-b34e-85dad62b9b94`
- **Worktree path**: `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/4ebd24d6-…/worktree`
- **First parked request id**: `0`
- **JSON-RPC wire id type**: requires PendingRequestStore inspection (likely integer per Baseline pattern)
- **shell_action_count**: `0` actually executed; `1` attempted as compressed chained command (same compression as Baseline; denominator < 3)
- **approval_request_count**: `1` (request 0 only — no req 1 since job canceled before deny→adapt cycle could fire)
- **Approval request kinds**: `command_approval` (request 0, with full `&&`-chain in scope.command)
- **`approval_request_count / shell_action_count`**: `1/0` — undefined (denominator zero) → record `no signal` per Branch Precedence #1.d
- **Command stdout/stderr summary**: not applicable (attempted action denied/canceled at gate; no execution)
- **Exit statuses**: not applicable
- **`decide(approve)` response payload**: not applicable (no approve issued; deny attempt rejected post-cancel)
- **`poll()` transitions**: `t0 (start)`: `needs_escalation, parked_request_id 0`. `t1 (post-rejected-decide)`: `canceled, pending_escalation null`.
- **`full.diff`**: not applicable (no artifacts produced)
- **`changed_files`**: not applicable
- **Artifact hash**: not applicable
- **PendingRequestStore rows**: 2 lines in `pending_requests/15267690-…/requests.jsonl` — needs inspection
- **DelegationJobStore rows**: 7 lines as captured in this handoff's Session Narrative (jobs.jsonl)
- **OperationJournal rows**: needs inspection (`journal/operations/15267690-….jsonl`, 3287 bytes)
- **Audit rows**: 2 rows as captured in this handoff (`audit/events.jsonl` L65-L66)
- **Network probe**: deferred to attempt 2 (when execution might actually happen)
- **Sensitive-path probe**: deferred to attempt 2
- **Sibling-worktree probe**: deferred to attempt 2 cross-check
- **Post-run HEAD**: TBD at next pre-flight (expected `5a1e937e` unchanged)
- **Post-run dirty diff**: TBD at next pre-flight
- **Variant restoration**: deferred to AFTER attempt 2 completes (per VIP step 7)
- **Restoration verification**: deferred
- **Cleanup performed**: deferred

### 4. New session: update Attempt 1 row in Attempt history table + add Attempt 2 row

```
| Attempt | Reason started | Shell-visible actions | Outcome | Preserved evidence |
|---:|---|---:|---|---|
| 1 | Initial Candidate A run; tests `includePlatformDefaults: True` hypothesis. | 0 executed (1 attempted as compressed chained command, denied at approval gate before any shell ran) | **canceled-by-approval-timeout** at +15m10s after start; deny adjudication failed because job had already canceled. Mechanism revision finding: parking with True flag refutes Baseline's sandbox-driven analysis. | Per-variant block above (cells filled post-handoff); audit L65-L66; jobs.jsonl 7 rows; runtime-proof line preserved verbatim in handoff `2026-04-28_15-13_*.md` Changes section. |
| 2 | Approve-strategy attempt; tests whether shell execution succeeds past the gate under True policy. Pre-authorized by user to land within TTL window. | TBD | TBD | TBD |
```

### 5. New session: TRASH attempt 1's runtime-proof log before firing attempt 2

`trash /tmp/codex-collab-candidate-a-runtime-proof.log` — to prevent attempt 2's emit from appending and conflating reads.

### 6. New session: fire `codex_delegate_start` for attempt 2 (approve-strategy)

Same canonical prompt as attempt 1 (cross-attempt comparability). User pre-authorizes "approve on first request" before firing — no /copy round-trip during the cycle. Land approve within ~10min of start to leave TTL buffer.

**Hypothesis (attempt 2):** With approve, shell will either (i) execute successfully → confirms approval gating was the only blocker, sandbox grants under True flag are sufficient; OR (ii) fail with sandbox-level error (e.g., "permission denied" reading `/bin/zsh`) → both layers were blockers, sandbox is real but downstream of approval.

### 7. New session: capture attempt 2 evidence + update Branch decision adjudication

After attempt 2 completes (or canceled), fill cells; update Branch decision for Candidate A overall (likely "Branch S1 invalidated; mechanism is approval-policy-driven, not sandbox-driven"); update Symptom Attribution if rows need rewording.

### 8. New session: investigate where 15-min approval TTL is configured

Grep plugin codebase + check Codex CLI app-server config for `15` / `900` (seconds) / `timeout` / `approval` / `ttl`. Document finding in run record's Gotchas section + this handoff's open questions resolution.

### 9. New session: restoration + closure commit

After attempt 2:
- `git checkout -- packages/plugins/codex-collaboration/server/runtime.py`
- `trash /tmp/codex-collab-candidate-a-runtime-proof.log`
- Verify clean: `git status --short` should show only the 8 carry-forward ticket-file moves + run-record edits
- Closure commit: `docs(delegate): capture Candidate A attempts 1+2 evidence + restoration on T-01 run record`

### 10. Carry-forward Baseline hygiene items (still open from prior sessions)

| # | Item | Status |
|---|------|--------|
| 2 | Optional follow-up on delegate's autopilot toward `.codex-collaboration/test-results.json` | Open (recurred in Candidate A attempt 1 — autopilot is invariant across variants) |
| 3 | Audit prior sessions' handoffs for the macOS `date -u -j -f` pitfall | Open |
| 4 | Open question on `available_decisions: []` in null-scope `file_change` | Open (not seen this attempt — file_change request 1 didn't surface because job canceled) |

## In Progress

**Clean stopping point at TTL-discovery boundary.** No work in flight beyond what's preserved on disk and in this handoff.

- Disk holds Candidate A patch (`runtime.py` modified)
- Running plugin holds PATCHED code in memory (Candidate A: True flag + instrumentation)
- 0 docs commits this session
- Restoration of Candidate A patch is deferred to AFTER attempt 2 completes
- Working tree dirty on: runtime.py (Candidate A), run record (variant block instantiation), 8 carry-forward ticket-file moves
- Runtime-proof log on disk: 1 line from attempt 1 (must trash before attempt 2)

## Open Questions

- **Where is the 15-min approval TTL configured?** Plugin code or App Server config? Tunable? (Affects future variant-cycle methodology.)
- **What does `actor=system` `approval_timeout` write to OperationJournal?** Needs inspection of `journal/operations/15267690-….jsonl` next session.
- **Will attempt 2 (approve) execute the command successfully under True flag?** This is the load-bearing question for the mechanism revision.
- **Does the plugin re-park automatically post-timeout if a new approval surfaces, or is the canceled job terminal?** Polled this session showed `canceled` as final state.
- **Should the Candidate B matrix even be the next escalation given the mechanism revision?** Sandbox grants likely don't help if parking happens upstream of sandbox check. May need to skip Candidate B entirely or re-frame it as a downstream-execution test.
- **Does `proposedExecpolicyAmendment` ever differ between variants under untrusted mode?** Both Baseline and Candidate A had it populated; appears truly universal. If a variant ever produces it as `null`, that would be a meaningful signal.
- **Is the wire-surface `available_decisions: ["approve", "deny"]` always 2-option, or did Baseline see a fuller list at the wire?** Need to re-check Baseline raw excerpts. (PendingRequestStore L1 had full 6-option list per Baseline cells.)

## Risks

### Forgetting to trash runtime-proof log before attempt 2

**Concern:** Attempt 2's emit will append to `/tmp/codex-collab-candidate-a-runtime-proof.log` — currently has 1 line from attempt 1. If not trashed first, the log will have 2 lines and reads must distinguish by timestamp. Easy mistake to make.

**Mitigation:** Pre-flight in next session must include `ls /tmp/codex-collab-candidate-a-runtime-proof.log` (expect: 1 line from attempt 1) + `trash /tmp/codex-collab-candidate-a-runtime-proof.log` BEFORE delegate_start. Document this in attempt 2 cell-filling instructions.

### Attempt 2 also timing out

**Concern:** If user takes too long to authorize approve OR if my call sequence has latency, the same 15-min TTL could fire again.

**Mitigation:** User pre-authorizes "approve on first request" BEFORE firing start. Land approve within first 5 minutes of start to leave wide buffer. If user needs to review the parked-state evidence first, a separate mini-cycle: poll-only (no decide) → review → fire decide(approve) within remaining TTL.

### Branch S1 may need re-classification, affecting Symptom Attribution + Branch Precedence

**Concern:** Mechanism revision (untrusted-mode unconditional parking) suggests Branch S1's framing ("Sandbox still blocked") is misleading. The actual blocker is approval-policy. Updating these table rows + Branch Precedence rules is a methodology-level change that touches the diagnostic's central classification scheme.

**Mitigation:** Do NOT update Branch decision rows during attempt 1 cell filling — wait until attempt 2 provides confirming or refuting evidence. Then update with full attempt 1+2 context. Avoid premature re-classification based on single-variant data point.

### Variant block in run record has 25 TBD cells; risk of staleness across multiple sessions

**Concern:** If next session also runs out of context before filling cells (e.g., during attempt 2 deliberation), the variant block stays half-complete. Multi-session staleness erodes evidence freshness.

**Mitigation:** Next session should prioritize cell filling for attempt 1 BEFORE firing attempt 2. Cell filling is durable (just markdown edits); attempt 2 can be deferred to a third session if needed.

### Plugin re-restart could happen between sessions; PIDs would change

**Concern:** If user restarts Claude Code between this session and the next (e.g., for unrelated reasons), pre-flight needs to re-derive plugin start UTC. The patch on disk would still be picked up by the new plugin process, but the PID + start-time evidence in run record's Candidate A cells would be for THIS session's plugin instance, not the next session's.

**Mitigation:** Pre-flight in next session checks PIDs vs `64122/64184/64213`. If different, re-derive plugin start UTC via SAFE epoch round-trip. Document the PID+UTC change in run record's notes section if it happens. The variant remains valid as long as: (a) patch still on disk; (b) plugin started after patch applied UTC; (c) runtime-proof emit confirms `True` flag.

### Pyright RT.1 could surface again on cell-filling edits

**Concern:** Same carry-forward risk as last session. RT.1 is at runtime.py:282 (TurnStatus literal narrowing); pre-existing per MEMORY.md.

**Mitigation:** Ignore for cell-filling work (markdown edits); only relevant if I re-edit runtime.py.

## References

### Files

- `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — run record (live HEAD: `5a1e937e` + dirty Candidate A block at line 826)
- `packages/plugins/codex-collaboration/server/runtime.py` — patched on disk (Candidate A: True flag + `[CANDIDATE_A]` instrumentation; in plugin's in-memory imported module)
- `.tmp/variant-candidate-a.patch` — patch capture (sha256 `4df1df3999b4914978fb0cf7582418cfd65377f36e4e45942983191d75fa2bf8`)
- `.tmp/variant-candidate-a.applied-at` — `Patch applied at: 2026-04-28T17:12:59Z`
- `.tmp/app-server-schema-pre-candidate-a/` — schema bundle (gitignored; from prior session)
- `~/.claude/plugins/data/codex-collaboration-inline/audit/events.jsonl` — Candidate A att1 rows L65-L66
- `~/.claude/plugins/data/codex-collaboration-inline/delegation_jobs/15267690-603e-4715-be76-9c90ba41007a/jobs.jsonl` — 7 rows for canceled job
- `~/.claude/plugins/data/codex-collaboration-inline/pending_requests/15267690-603e-4715-be76-9c90ba41007a/requests.jsonl` — 2 rows
- `~/.claude/plugins/data/codex-collaboration-inline/journal/operations/15267690-603e-4715-be76-9c90ba41007a.jsonl` — needs inspection
- `/tmp/codex-collab-candidate-a-runtime-proof.log` — 1 line, 533 bytes (attempt 1 emit)

### Job IDs (Candidate A attempt 1)

| ID | Value |
|----|-------|
| job_id | `4ebd24d6-6f1f-45b8-99eb-0d890a9d5326` |
| runtime_id | `84fce58f-c860-4757-a852-6f30c3d21ddf` |
| collaboration_id | `9a8a1a64-65b7-4884-b34e-85dad62b9b94` |
| base_commit | `5a1e937eff04f4cfecf5ce7bc65fae1f94db0fca` |
| worktree_path | `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/4ebd24d6-…/worktree` |
| parked_request_id | `0` |

### MCP tool calls this session

| Tool | Purpose | Outcome |
|------|---------|---------|
| `Skill: handoff:load` | Resume from 17:13 handoff | Archived prior handoff; state file written |
| `ToolSearch select:` | Fetch deferred MCP schemas | Loaded codex_status, codex_delegate_start, codex_delegate_poll, codex_delegate_decide |
| `mcp__plugin_codex-collaboration_codex-collaboration__codex_delegate_start` | Fire Candidate A attempt 1 | Returned `needs_escalation, parked_request_id 0` |
| `mcp__plugin_codex-collaboration_codex-collaboration__codex_delegate_decide` | Deny req 0 | Rejected: `job_not_awaiting_decision`, status `canceled` |
| `mcp__plugin_codex-collaboration_codex-collaboration__codex_delegate_poll` | Confirm canceled state | `status: canceled, pending_escalation: null, inspection: null` |
| `Skill: handoff:save` | Save this handoff | In progress |

### Bash invocations of note

- `ps -ef | grep codex-collaboration | grep -v grep` → 3 PIDs (`64122/64184/64213`)
- `LSTART=$(ps -p 64213 -o lstart=); EPOCH=$(date -j -f "%a %b %d %H:%M:%S %Y" "$LSTART" +%s); date -u -r "$EPOCH" +"%Y-%m-%dT%H:%M:%SZ"` → `2026-04-28T17:24:44Z`
- `cat /tmp/codex-collab-candidate-a-runtime-proof.log` → 1 line with True flag confirmed
- Stores grep with python3 JSONL pretty-printing → audit trail for canceled job

### Branches

- `feature/delegate-execution-diagnostic-record` at `5a1e937e` (in sync with origin)

## Gotchas

### Approval TTL is ~15 minutes — operator-mediated decide must land within window (NEW)

Discovered this session via `audit/events.jsonl` row sequence: `delegate_start` at `17:51:27Z`, `approval_timeout` at `18:06:37Z` (delta = 15m10s, `actor=system`). Mitigation: pre-authorize decisions before firing start, OR poll-then-decide if any latency, OR investigate TTL configurability.

### Decide is one-shot — always poll first under any latency (NEW)

`codex_delegate_decide` rejects with `{"reason": "job_not_awaiting_decision"}` if job has transitioned out of awaiting-decision state. Poll-then-decide is the safe pattern for any operator-mediated cycle.

### Candidate A attempt 1 outcome is `canceled-by-approval-timeout`, NOT `deny-completed` (NEW)

Important for cell semantics: cells should reflect canceled state, not denied state. Some cells become `not applicable` (Exit statuses, Command stdout/stderr) where they would have been "denied at gate" if deny had landed.

### Runtime-proof log accumulates across attempts; must trash between attempts (NEW)

`/tmp/codex-collab-candidate-a-runtime-proof.log` is opened in append mode by the patched policy builder. Each delegate call appends one line. To prevent contamination of attempt 2 reads, trash before attempt 2 fires.

### `actor=system` audit events vs `actor=claude` (NEW)

Filter by actor when reading audit trail. `system` events include lifecycle automation (timeout, cancel-from-system); `claude` events are orchestrator-initiated (delegate_start, decide).

### Mechanism revision pending validation (NEW — important for next-session work)

Branch S1 ("Sandbox still blocked") may need re-classification based on Candidate A attempt 1 + 2 combined evidence. Do NOT update Branch decision tables prematurely on attempt 1 alone.

### Carried gotchas (still applicable)

- **`pgrep -fa <pattern>` matches its own argv** — use `ps -ef | grep ... | grep -v grep` instead.
- **macOS `date -u -j -f FMT INPUT +OUTFMT`** is the parsing trap; use epoch round-trip for parsing, `date -u +FORMAT` for emission.
- **`available_decisions` wire vs PendingRequestStore** — wire surface may be shorter (`[approve, deny]`) than store record (full 6-option list). Use store record for S7 amendment classification.
- **`ps -p ... -o lstart=` returns trailing whitespace** — `date -j` warns "Ignoring 4 extraneous characters" but parses correctly.
- **Pyright RT.1 (runtime.py:282)** — pre-existing carry-forward; surfaces on every runtime.py edit; not a regression signal.
- **Run Identity drift** — Run Identity records `49d93001` (frozen); live HEAD now `5a1e937e` (drift of 11 commits; expected).
- **Each variant cycle is ~10 minutes minimum** — apply patch → operator restart → execute → restore → commit. Now augmented with TTL constraint.
- **`available_decisions: []` for null-scope `file_change`** — open question carry-forward; not surfaced this attempt because job canceled before file_change request could fire.
- **Two-clock-domain cross-check** — patch < plugin start < runtime-proof emit < audit timestamps. All three sources cross-checked successfully this session.

## User Preferences

(Carried from prior sessions, applied this session — verbatim quotes where relevant.)

**Strict-gate before fallback investigation (carried, applied).** Pre-flight verification ran before any state change.

**Two-layer HEAD anchor preserved (carried, applied).** Run Identity frozen at `49d93001`; live HEAD drift to `5a1e937e` documented.

**Decision fence over decision wall (carried, applied).** Three /copy-routed alignments this session: deny vs approve fork, save vs continue fork (both via $making-recommendations), preceded by user's prior session's framings.

**Push at clean phase boundaries (carried, applied via prior sessions).** No new push this session because no new commits.

**Handle commits proactively (carried).** Would have committed at closure but session ended at restart-boundary-equivalent before closure was reached.

**Variant patches mirror Baseline shape exactly with label-only changes (carried, applied).** Candidate A's instrumentation diff matches Baseline structure with only `[CANDIDATE_A]` label + log filename differing.

**Capture cheap read-only artifacts pre-variant (carried, applied via prior session).** Pre-execution cells filled in this session leveraged prior session's schema bundle capture.

(New this session — verbatim user quotes:)

**$making-recommendations skill is the operator's preferred fork-handling tool.**
> "Using `$making-recommendations` for this fork."

User invoked it twice this session (deny vs approve, save vs continue). The skill's structured output (Decision / Stakes / Options / Information gaps / Evaluation / Sensitivity / Ranking / Recommendation / Readiness) is the framework I should read into and respond to.

**Cross-variant comparability over secondary metrics.**
> "Do not modify the prompt to force ≥3 shell-visible actions. That would weaken cross-variant comparability for a secondary metric. Candidate A's load-bearing question is simpler: does `includePlatformDefaults: True` allow shell execution to reach the point of creating [the artifact]?"

Apply to all future variants: comparability across variants is the primary methodology axis; secondary metrics (ratio, action count) are subordinate.

**Variant-isolation discipline maps "approve attempt" to a separate cycle, not a continuation of attempt 1.**
> "Open a separate Candidate A approve attempt to test the downstream question: whether shell execution succeeds after the approval gate under the True policy."

Within the run record, this is **Candidate A attempt 2** (same variant block, second row in Attempt history) since the policy patch is unchanged.

**Save when context constrained AND when a load-bearing finding emerges.**
> "Save the handoff now. The handoff should explicitly say Candidate A attempt 1 is `canceled-by-approval-timeout`, not deny-completed and not Candidate A execution failure."

User's framing: cancel the noun confusion early. Future cells must reflect canceled, not denied.

## Conversation Highlights

**User on deny vs approve fork (drove D4 + plan for attempt 2):**
> "1. **C: Deny now, then separate approve attempt** - best evidence quality across both questions. … **Recommendation:** choose **(c)**."

**User on save vs continue fork (drove D5):**
> "**A** is the strongest fit. It preserves the new `approval_timeout` finding, avoids another live TTL race, and gives the next session a clean entry point: record attempt 1 cancellation, then run attempt 2 with an operator decision inside the TTL window."

**User on attempt 1 outcome framing (cell semantics guidance):**
> "The handoff should explicitly say Candidate A attempt 1 is `canceled-by-approval-timeout`, not deny-completed and not Candidate A execution failure."

**Working style observed:** User uses $making-recommendations skill for non-trivial decision forks; reads + responds to explicit Recommendation lines; makes structural refinements (e.g., naming attempt 2 within same variant block) without overriding the recommendation; respects context budget at session boundaries.

**Communication pattern (carried):** Reports use "What changed / Why / Verification / Remaining risks" structure (per global CLAUDE.md Response Contracts) AND end with explicit decision points framed as multiple-choice + recommendation. User responds with skill invocation or direct selection; rarely overrides without explanation.

## Rejected Approaches

### Modifying the smoke prompt to force ≥3 distinct shell-visible actions

**Approach:** Add explicit prescription to the canonical prompt to force the delegate to issue mkdir / printf / cat as separate shell calls rather than one chained `&&`-command.

**Why it seemed promising:** Would produce ≥3 shell-visible actions, making the `approval_request_count / shell_action_count` ratio interpretable per Branch Precedence #1.d. Could resolve Baseline's "denominator < 3" gap.

**Specific failure:** User explicitly rejected: "Do not modify the prompt to force ≥3 shell-visible actions. That would weaken cross-variant comparability for a secondary metric." Cross-variant comparability is primary; ratio interpretation is secondary.

**What it taught:** Methodology axes have priority order. Don't optimize a secondary axis at cost of the primary. The canonical prompt is canonical for a reason — variants must use it verbatim.

### Capturing attempt 1 cancellation cells now (before saving handoff)

**Approach:** Use remaining context (~12k tokens) to fill the canceled-state cells in run record, then save handoff with completed cells.

**Why it seemed promising:** Better artifact completeness; future-Claude has less to do.

**Specific failure:** Cell filling for canceled state involves: reading store JSONL files, deriving lifecycle table, updating ~15 cells, possibly updating attempt history table. Would consume 8-15k of remaining ~12k. Risk of half-complete edit + handoff explaining a half-edit.

**What it taught:** Durable evidence (audit, jobs, runtime-proof, requests on disk) doesn't need same-session capture. Handoff continuity is a sufficient bridge. Defer cell filling when context is constrained.

### Firing attempt 2 immediately while plugin still has patched code in memory

**Approach:** Use remaining context to: trash runtime-proof log, fire delegate_start with same prompt, pre-authorize approve, capture both attempts in one session.

**Why it seemed promising:** Highest evidence yield per session; no restart cycle needed since plugin still has Candidate A patch in memory; would resolve the mechanism revision question (does shell execute past the gate under True flag) within this session.

**Specific failure:** Wrong risk profile under context constraint. Attempt 2 = irreversible live cycle; if context exhausts mid-cycle, evidence sits incomplete. TTL also a live constraint — even pre-authorized approve has latency from poll → decide that could eat into the window. User's $making-recommendations evaluation: "operationally material" risk, "verifiably best for this session boundary" to save instead.

**What it taught:** Live cycles need budget headroom. Methodology constraints (TTL, restart boundaries) compose; don't pile them in a single context-pressured session.
