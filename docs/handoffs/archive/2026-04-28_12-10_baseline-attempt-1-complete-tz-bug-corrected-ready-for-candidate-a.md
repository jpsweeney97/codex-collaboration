---
date: 2026-04-28
time: "12-10"
created_at: "2026-04-28T16:14:00Z"
session_id: 7337aa50-e517-44f7-8793-eebb3f0fe3db
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-28_06-58_t01-step-1-complete-file-write-instrumentation-patched-ready-for-restart.md
project: claude-code-tool-dev
branch: feature/delegate-execution-diagnostic-record
commit: c704eafa
title: T-01 Baseline attempt 1 complete; TZ-bug caught + corrected; ready for Candidate A restart
type: handoff
files:
  - docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md
  - packages/plugins/codex-collaboration/server/runtime.py
  - .tmp/variant-baseline.patch
  - .tmp/variant-baseline.applied-at
---

# Handoff: T-01 Baseline attempt 1 complete; restoration done; TZ-bug corrected; ready for Candidate A

## Goal

**Bigger picture:** Continue T-20260423-01 live delegate-execution remediation. Prior session pre-staged the runtime-proof instrumentation patch on `runtime.py:23` and pushed `7650366d` with the FD 2 routing finding. This session executed Baseline (Variant 1 of 3): captured runtime-proof, observed live delegate behavior under the production sandbox policy, denied both surfaced escalations, restored disk state.

**Why we stopped:** Baseline complete on disk. Candidate A requires another Claude Code restart so the running plugin process (PID `11696`, started `2026-04-28T15:41:29Z` UTC corrected) re-imports the un-patched `runtime.py` from disk. Continuing in-session would run any subsequent work against the still-patched in-memory code (would emit phantom `[BASELINE]` lines if any code path hit `build_workspace_write_sandbox_policy`).

**Stakes:** This session produced the load-bearing Baseline evidence: runtime-proof of the production `sandboxPolicy` at `runtime.py:23` build site confirms the parent T-01 mechanism (`readableRoots: [worktree]` + `includePlatformDefaults: False` → `/bin/zsh` unreachable → every shell command parks as `command_approval` before execution). Branch S1 (Sandbox still blocked) is conclusively the Baseline classification. Two commits this session — `2cb223d4` (Baseline evidence + restoration) and `c704eafa` (macOS-`date` pitfall correction) — are local and unpushed.

**Success criteria for this session (all met):**
- Pre-flight verified post-restart (PIDs differ from prior session; plugin start > patch applied; dirty diff matches `.tmp/variant-baseline.patch`).
- Pre-run evidence locked into run record's `### Variant: Baseline (attempt 1)` block with the two user-specified tightenings (Patch applied at exception form; PID labels with raw lstart + normalized UTC).
- Runtime-proof emit captured at `2026-04-28T15:53:37Z` to `/tmp/codex-collab-baseline-runtime-proof.log` — production policy reproduced byte-for-byte.
- Delegate state walked: start → `command_approval` (req 0) → deny → `file_change` (req 1, null scope) → deny → `completed`.
- Inspection artifacts captured (full.diff empty, changed_files [], framework's test-results.json `not_recorded`, artifact_hash `d604766e...`).
- Restoration verified: `runtime.py` reverted via `git checkout`; runtime-proof artifact trashed; running plugin still holds patched code (memory restoration pending Candidate-A restart).
- Run record committed at `2cb223d4` (+92 lines).
- macOS `date -u -j -f` pitfall caught + documented + corrected in `c704eafa`.

## Session Narrative

Resumed from `2026-04-28_06-58_t01-...md`. Pre-flight: HEAD `7650366d` ✓; `git diff runtime.py` byte-identical to `.tmp/variant-baseline.patch` ✓; new plugin PIDs `11645`/`11696` (different from prior session's `22152`/`22154`) ✓; plugin start `Tue Apr 28 11:41:29 2026` (initially mis-normalized to UTC — see TZ-bug below).

User `/copy`-routed a Codex docs read corroborating the file-sink choice on three new grounds: stdio = protocol; `sandboxPolicy` is protocol-first-class; `command/exec` stdout/stderr is App-Server-runs-the-command, not host-surfaces-plugin-stderr. Schema-dump refinement (`codex app-server generate-json-schema`) discussed; deferred to Candidate prep.

User answered the two checkpoints with two tightenings: (1) `Patch applied at` exception form spelled out; (2) PID labels both PIDs with python child as evidentiary, and record raw `lstart` alongside normalized UTC. Locked Pre-run evidence into the run record. Quoted concrete smoke objective with timestamp pinned to `20260428T005625`.

Invoked `codex_delegate_start`. Returned `needs_escalation` immediately — `request_id="0"`, `kind: command_approval`, scope = chained `/bin/zsh -lc "..."` containing the smoke commands plus an unsolicited `.codex-collaboration/test-results.json` write. Read `/tmp/codex-collab-baseline-runtime-proof.log`: production `sandboxPolicy` dict reproduced byte-for-byte at `runtime.py:23` build site; T-01 mechanism confirmed.

User `/copy`-routed a structured Codex consultation: deny request 0; classify Baseline attempt 1 valid for non-ratio Branch S1; no rerun; restore; advance to Candidate A. Aligned with my recommendation; followed verbatim.

Denied `request_id="0"`. Polled. **Surprise:** status went `running` → then back to `needs_escalation` with a new parked `request_id="1"`, `kind: file_change`, **scope null** (`grantRoot: null`, `reason: null`). Stored memory `feedback_deny_finalizes_job.md` says deny prevents agent adaptation — empirically false here. Denied request 1. Job reached `completed` with `changed_files: []`, `artifact_hash d604766ea0e6f7d82c1f37f5b66d10d985cfd0271b01f3a7491ceb8f167d7b8d`, `reviewed_at 2026-04-28T16:02:51Z`.

Locked terminal evidence into run record (poll transitions, escalation kinds + null-scope flag, full.diff/changed_files/artifact_hash). Restored: `git checkout -- packages/plugins/codex-collaboration/server/runtime.py` + `trash /tmp/codex-collab-baseline-runtime-proof.log`. Verified clean. Committed as `2cb223d4`.

Then ran a sanity check on plugin start UTC — caught a 4-hour error from `date -u -j -f` silently treating local-tz input as UTC (local tz here is EDT/-0400). Re-derived via epoch round-trip; corrected to `2026-04-28T15:41:29Z`. Cross-checked against runtime-proof artifact's independent timestamp (`2026-04-28T15:53:37Z` from Python `datetime.now(timezone.utc)`): now ~12min gap (plausible for first delegate call), where the broken recipe would have implied 4h12m gap. Updated run record (two cells); committed correction as `c704eafa`.

## Decisions

### Deny both escalations to finalize Baseline at S1

**Choice:** Denied request 0 (`command_approval`) and request 1 (`file_change`).

**Driver:** Baseline's claim is "production policy blocks shell" — already proven by runtime-proof + parked first command. Approve has no diagnostic upside (would either fail at execution with no new evidence, or succeed with an out-of-scope chained command that contaminates the variant).

**Alternatives considered:** Approve (rejected); discard the job (would erase audit trail); rerun with separate-commands prompt (would almost certainly hit the same parked-state outcome).

**Confidence:** High. Codex consultation independently aligned.

**Reversibility:** Medium. Baseline could be rerun in a future session; signal cost is low (parked outcome reproducible).

### Commit run record at clean phase boundaries (no push)

**Choice:** Two run-record-only commits this session: `2cb223d4` (Baseline evidence + restoration) and `c704eafa` (TZ correction). Did NOT push.

**Driver:** Mirrors prior `7650366d` pattern; "Handle commits proactively" preference; coherent buildable chunks. Push deferred per global CLAUDE.md "Still ask before: git push."

**Confidence:** High.

**Reversibility:** High (revert + push if needed; both unpushed so amend would also be safe but new commits is the chosen pattern).

### Correct the macOS `date -u -j -f` UTC error and document the pitfall on the run record

**Choice:** Re-derived plugin start UTC via epoch round-trip; updated the run record's "Plugin process start timestamp" cell with the corrected value `2026-04-28T15:41:29Z`, the pitfall description, the correct recipe, and a cross-check against the runtime-proof artifact's independent timestamp.

**Driver:** Self-audit caught a 4-hour error from `date -u -j -f` silently treating local-tz input as UTC. Variant validity conclusion held (plugin still started after patch — by 8h44m, not 4h44m), but absolute timestamp was wrong. Future variants would propagate the same bug if not flagged.

**Alternatives considered:** Amend prior commit (rejected per system-prompt CRITICAL rule); leave the error in place because conclusion is unchanged (rejected — load-bearing evidence; future sessions running the same recipe would produce broken records).

**Confidence:** High — three independent recipes converge on `15:41:29Z`; runtime-proof artifact's own UTC timestamp (`datetime.now(timezone.utc)`) cross-checks at ~12min gap (plausible).

## Changes

### Commits (this session, local only — NOT pushed)

| Commit | Subject | Diff stat |
|---|---|---|
| `2cb223d4` | docs(delegate): capture Baseline attempt 1 evidence + restoration on T-01 run record | +92 lines (1 file) |
| `c704eafa` | docs(delegate): correct Plugin start UTC on Baseline block (macOS date pitfall) | +2 / -2 lines (1 file) |

Branch is 2 ahead of `origin/feature/delegate-execution-diagnostic-record`.

### `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md`

New section `### Variant: Baseline (attempt 1)` after the Per-Variant Evidence template at line ~624. Contains: full Pre-run evidence; inline reproduction of the runtime-proof-only instrumentation patch; Job + escalation evidence; Branch S1 classification; full poll() transition timeline; inspection artifact references; post-run state; restoration + cleanup evidence. ~92 lines added across both commits combined.

### `packages/plugins/codex-collaboration/server/runtime.py` — restored

`git checkout` reverted the runtime-proof instrumentation patch. Disk state matches `7650366d`. **Running plugin process still holds patched code in memory** — restart required before Candidate A.

### `/tmp/codex-collab-baseline-runtime-proof.log` — captured then trashed

Single line emitted at `2026-04-28T15:53:37.116985+00:00`:
```
[BASELINE] sandboxPolicy={'type': 'workspaceWrite', 'writableRoots': [worktree], 'readOnlyAccess': {'type': 'restricted', 'readableRoots': [worktree], 'includePlatformDefaults': False}, 'networkAccess': False, 'excludeSlashTmp': True, 'excludeTmpdirEnvVar': True}
```

Trashed via `trash` per project rule (no `rm`).

## Codebase Knowledge

### Delegate's escalation pattern is a state machine, not single request-and-finalize

Empirically observed this session: `start()` → `needs_escalation` → orchestrator decides → either advance via approve+execute or advance to the agent's next intent via deny → either terminal `completed` or another `needs_escalation` for a different action class.

This contradicts memory entry `feedback_deny_finalizes_job.md`. Update needed: deny rejects ONE action; the agent may then propose a different action class (typically once); ONE more deny terminates. We saw: req 0 deny → req 1 (file_change) → deny → completed.

### `file_change` escalation can have null scope

Both `requested_scope.grantRoot` and `requested_scope.reason` returned `null` on the wire in our second escalation. Deny is the only safe response when scope is unbounded.

### Inspection artifact triplet from `codex_delegate_poll` terminal state

`<plugin_data_root>/runtimes/delegation/<job-id>/inspection/`:
- `full.diff` — git diff of delegate's worktree changes (empty for fully-denied runs).
- `changed-files.json` — `{"changed_files": [...]}` (empty list = no writes).
- `test-results.json` — framework's structured result; records `not_recorded` with `commands: []` if delegate never wrote `.codex-collaboration/test-results.json`.

`artifact_hash` is sha256 over the triplet.

### Plugin data root resolves to `~/.claude/plugins/data/codex-collaboration-inline/`

Not the `/tmp/codex-collaboration` default. The `CLAUDE_PLUGIN_DATA` env var is unset on this host but the plugin's bootstrap code resolves a different default. Confirmed via inspection-artifact paths in poll responses.

### macOS `date -u -j -f` is a parsing trap

With `-u` set, both input and output are treated as UTC, so a local-tz input is silently relabeled rather than converted. Correct macOS recipe is two-step: `date -j -f FMT INPUT +%s` to parse local-tz to epoch, then `date -u -r EPOCH +"%Y-%m-%dT%H:%M:%SZ"` to format epoch as UTC.

### Patterns Identified

- **Two-clock-domain consistency check** — independent timestamp sources (Python `datetime.now(timezone.utc)` from runtime-proof emit; OS-level `ps -o lstart` + epoch round-trip from process start) should agree on relative spacing. ~12min gap was plausible; 4h12m would have been the symptom of a parsing error.
- **Decision fence over decision wall (carried)** — denied parked requests as the conservative path; left "approve under specific scope" as a documented future option without committing to it.

### Conventions Observed

- Commit message style (carried): `docs(delegate): <subject>` with HEREDOC body, no Co-Authored-By, conventional commit scope.
- Per-Variant block instantiation: copy template, replace TBDs with values; place new variant blocks after the template (between Raw excerpts placeholder and `## Threshold Calibration`).
- Runtime-proof-only instrumentation exception: semantics-preserving instrumentation IS a patch for capture/restore (record under "Patch capture form", mark `Patch applied at`) but NOT a behavioral patch for variant interpretation.

### Surprising Findings

- **Memory contradiction on deny semantics** — stored `feedback_deny_finalizes_job.md` is empirically wrong. Memory correction queued for next session.
- **Null-scope `file_change`** — second escalation surfaced with both `grantRoot` and `reason` null. Future sessions should deny these by default unless protocol semantics are clarified.
- **macOS `date -u -j -f`** — caught the pitfall before evidence propagated, but the prior session's handoff probably used the same recipe (same machine, same recipe template). Audit recommended.

### Key Locations

| Concept | Location |
|---|---|
| Run record | `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` |
| Baseline variant block | run record §"Per-Variant Evidence" → "Variant: Baseline (attempt 1)" |
| Patched-and-restored build site | `packages/plugins/codex-collaboration/server/runtime.py:23-38` |
| Patch capture file | `.tmp/variant-baseline.patch` (still on disk; gitignored) |
| Patch applied at | `.tmp/variant-baseline.applied-at` (still on disk; gitignored) |
| Delegate worktree (this attempt) | `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/6753a537-99d8-456f-a1c0-1c79f13a2fc9/worktree` |
| Inspection artifacts | same parent dir, `inspection/` subdir |
| Plugin data root (resolved) | `~/.claude/plugins/data/codex-collaboration-inline/` |

## Conversation Highlights

**User shared Codex docs read** — corroborated file-sink choice on three new grounds (stdio = protocol; `sandboxPolicy` first-class; `command/exec` stdout/stderr is App-Server-runs-the-command, not host-surfaces-plugin-stderr). Schema-dump refinement noted but deferred.

**User's two-checkpoint answers:** quote smoke objective verbatim from run record (pin timestamp to `20260428T005625`); two tightenings on Pre-run evidence (Patch applied at exception form; PID labels with raw + normalized UTC).

**User's Codex consultation on the escalation:** structured 9-section adversarial review confirming deny + record S1 + restore + advance to Candidate A as the strongest option. Ranked alternatives with explicit tradeoffs.

## Context

### Project State

| Item | State | Where |
|---|---|---|
| Run record | Two new commits this session (`2cb223d4`, `c704eafa`) | `feature/delegate-execution-diagnostic-record` HEAD |
| Run Identity table | Frozen at `49d93001` per two-layer pattern; live drift to `c704eafa` documented | run record lines 56-66 |
| Sandbox blocker | Confirmed live | `runtime.py:23-38` (restored to pre-patch) |
| Baseline outcome | Branch S1 (Sandbox still blocked); ratio uninterpretable per #1.d | run record §"Variant: Baseline (attempt 1)" |
| Plugin process (this session) | python child PID `11696`, uv wrapper PID `11645`; in-memory code is patched (post-restore disk-only restoration) | `ps aux \| grep codex_runtime_bootstrap` |
| Runtime-proof artifact | Trashed; does not exist | `/tmp/codex-collab-baseline-runtime-proof.log` |
| Patch on disk | RESTORED (matches `7650366d`) | `git diff packages/plugins/codex-collaboration/server/runtime.py` empty |
| Working tree | Clean except 8 ticket-file moves (carry-forward) | `git status --short` |
| Pushed to origin? | NO — both commits local | `git rev-list origin/feature/delegate-execution-diagnostic-record..HEAD` returns 2 |

### Mental Model

**Memory is patched; disk is restored.** Inverse polarity of pre-Baseline. Next restart re-imports the restored code from disk → memory and disk align on un-patched form → safe to start Candidate A.

**Two layers of timestamps for variant validity.** `Patch applied at` from `date -u +"%Y-%m-%dT%H:%M:%SZ"` is correct UTC directly. Plugin start from `ps -o lstart` is local-tz needing explicit conversion. Mixing the two requires the conversion to be correct — the macOS `date -u -j -f` pitfall is the trap.

**Inspection artifacts are framework state, not delegate state.** The triplet reflects what the framework saw, not what the delegate intended. Delegate's PROPOSED (and denied) actions live in PendingRequestStore JSONL rows (deferred inspection).

### Environment

- Working tree: `feature/delegate-execution-diagnostic-record` at `c704eafa` (2 ahead of origin); 8 ticket-file moves carry-forward.
- Codex: `codex-cli 0.125.0`.
- **Local timezone: `EDT (-0400)`** — source of the `date -u -j -f` pitfall.
- Plugin process: PIDs `11645`/`11696`; started `2026-04-28T15:41:29Z` UTC (corrected). In-memory code is patched.
- Plugin data root: `~/.claude/plugins/data/codex-collaboration-inline/` (resolved; NOT `/tmp/codex-collaboration`).

## Learnings

### macOS `date -u -j -f` silently mis-converts local-tz inputs

**Mechanism:** `-u` sets UTC mode globally for both input and output. `ps -o lstart` returns local-tz with no zone marker. The recipe `date -u -j -f "%a %b %d %H:%M:%S %Y" "<lstart>" +"%Y-%m-%dT%H:%M:%SZ"` thus relabels the local-tz value as UTC instead of converting.

**Evidence:** This session, raw lstart `Tue Apr 28 11:41:29 2026` (EDT). Wrong recipe → `2026-04-28T11:41:29Z`. Correct recipe (epoch round-trip) → `2026-04-28T15:41:29Z`. Cross-check via runtime-proof artifact's `datetime.now(timezone.utc)` confirmed the corrected value.

**Implication:** When recording UTC timestamps from `ps -o lstart` on macOS, always use the two-step epoch round-trip. Better: include a cross-check pair (independent UTC source) so silent recipe errors trigger an obvious anomaly.

### Delegate adapts after deny — does not finalize on first deny

**Mechanism:** `codex_delegate_decide(deny)` does not unilaterally terminate. The agent receives the rejection and chooses to (a) propose a different action class, or (b) finalize. Empirically (a) was chosen for the first deny; (b) for the second.

**Evidence:** Polling sequence after first deny showed `status: running` → `status: needs_escalation, parked_request_id: "1", kind: file_change`. After second deny: `status: completed`.

**Implication:** Memory entry `feedback_deny_finalizes_job.md` overstates the case. Update: deny rejects ONE action; the agent may iterate (typically once); a second deny is what terminates in the observed pattern.

### Two-clock-domain cross-check is a useful evidence audit

**Mechanism:** Independent timestamp sources should agree on relative spacing. Disagreement is a red flag for a parsing/conversion error in one of the recipes.

**Evidence:** Corrected plugin start `15:41:29Z` + runtime-proof emit `15:53:37Z` = 12min gap (plausible). Wrong recipe (`11:41:29Z`) would have implied 4h12m gap (implausible).

**Implication:** Build cross-checks into evidence templates. The check is silent on correct values, loud on broken recipes.

## Next Steps

### 1. Operator: restart Claude Code

**Dependencies:** None. Quit-relaunch from same project directory.

**Acceptance criteria:** New plugin process PIDs (different from `11645`/`11696`); new in-memory code is the restored (pre-patch) form.

**Sanity checks (post-restart):**
- `git diff packages/plugins/codex-collaboration/server/runtime.py` → EMPTY (disk restored).
- `git status --short` → only 8 carry-forward ticket-file moves for variant-relevant paths.
- `git log --oneline -3` → `c704eafa` then `2cb223d4` then `7650366d`.

### 2. New session: `/handoff:load`

Pick up THIS handoff; archive automatically. State file path becomes the next handoff's `resumed_from`.

### 3. New session: optional schema-dump artifact (deferred from this session)

**Dependencies:** Step 2 complete.

**Approach suggestion:** Capture `codex --version` + `codex app-server generate-json-schema` as a one-shot artifact for the run record's Cross-variant block. Validates that Candidate A's narrower-shape policy is schema-accepted by the installed Codex version BEFORE runtime — separates schema proof from runtime-payload proof.

### 4. New session: Candidate A patch + Pre-run evidence

**Dependencies:** Step 3 complete (or skipped).

**What to read first:** Run record §"Policy Variants" table + Candidate B Matrix Pre-Matrix Discovery section (relevant for which paths Candidate A unblocks).

**Approach suggestion:**
1. Edit `runtime.py:23` — flip `"includePlatformDefaults": False` → `True`. Optionally also re-add the runtime-proof instrumentation block with `[CANDIDATE_A]` label (preserves the durable file-sink evidence pattern).
2. Capture `.tmp/variant-candidate-a.patch` via `git diff > .tmp/variant-candidate-a.patch`; `.tmp/variant-candidate-a.applied-at` via `date -u +"%Y-%m-%dT%H:%M:%SZ"`.
3. Restart Claude Code AGAIN (so new plugin process re-imports Candidate A code).
4. Pre-flight per the same template as Baseline (HEAD, dirty diff, Plugin process PID + start using **correct epoch-round-trip recipe**, ordering check, runtime-proof method).

### 5. New session: Candidate A live execution

**Dependencies:** Step 4 complete.

**Approach suggestion:** Same smoke objective with same `<timestamp>` token (`20260428T005625`). Expected outcome: shell unblocked (delegate can `mkdir`, `printf`, `cat`); smoke artifact created. Network/sensitive-path probes per Candidate-only fields.

**Potential obstacles:** If smoke still doesn't produce — escalate to Candidate B Matrix.

### 6. New session: memory correction

**Dependencies:** None (parallel to other steps).

**Approach suggestion:**
- Update `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_deny_finalizes_job.md` with corrected mechanism: deny rejects ONE action; the agent may iterate once before terminal state.
- Update the corresponding MEMORY.md index entry's one-line hook.

### 7. Push decision

**Dependencies:** None.

User to decide whether to push `c704eafa` + `2cb223d4` to `origin/feature/delegate-execution-diagnostic-record` at session start, or keep local until more variants land.

## In Progress

Clean stopping point. No work in flight.

- 2 commits this session (`2cb223d4` Baseline evidence; `c704eafa` TZ-bug correction). Both local.
- Restoration complete on disk; memory restoration pending Candidate-A restart.
- Working tree dirty only on the 8 carry-forward ticket-file moves (untouched all session).
- Job `6753a537-...` left in `promotion_state: pending` (not promoted, not discarded; worktree persists for audit).

## Open Questions

- **Did the prior session's handoff use the same broken `date -u -j -f` recipe?** Same machine, same recipe template. Likely yes. Audit recommended in next session.
- **Why did `file_change` come back with null scope?** Protocol quirk vs. agent-internal placeholder vs. specific Codex behavior under "denial-after-shell-rejection." Worth a deeper look.
- **Will Candidate A's `includePlatformDefaults: True` actually unblock `/bin/zsh`?** Documentation says yes; empirical confirmation pending.
- **Should the test-results.json over-action be patched out of the delegate?** It's a delegate-framework property, not part of the smoke objective. Currently it's denied at the approval gate but the proposal still appears in escalation scope. Out of scope for this diagnostic but worth a follow-up issue.
- **Is the running plugin process actually held since the operator's earlier restart, or is it a fresh process started post-restart this session?** PID `11696` was already running when this session loaded (per pre-flight check). Cross-reference `etime` in next session.

## Risks

### Operator forgets to restart Claude Code before Candidate A

**Concern:** Inverse polarity of last time — running plugin holds PATCHED code; new Candidate A patch on disk wouldn't be observed. Phantom `[BASELINE]` lines could appear if any code path fires `build_workspace_write_sandbox_policy`.

**Likelihood:** Low if operator reads handoff fully.

**Impact:** Medium. New variant evidence would be invalid (Plugin process start timestamp would still be `2026-04-28T15:41:29Z`, BEFORE Candidate A's applied time).

**Mitigation:** Pre-flight at next session: verify plugin PID differs from `11696`. Verify `git diff runtime.py` is EMPTY (Candidate A patch is NOT yet applied at session start; would be applied IN-session).

### Memory drift if `feedback_deny_finalizes_job.md` is not corrected

**Concern:** Future sessions reading the wrong memory might (a) avoid sending denies when they should, or (b) plan single-deny finalization when two-deny is the actual pattern.

**Mitigation:** Memory correction is in Next Steps #6.

### Pyright pre-existing issues (carried; line numbers reset)

Now that `runtime.py` is restored, line numbers in pre-existing Pyright issues revert to pre-patch values (RT.1 was at `:270` pre-patch, was `:282` mid-patch, now back to `:270`). Carry-forward register references should reset to pre-patch line numbers.

### Pre-existing flaky `test_delegate_decide_async_integration.py` (carried)

Unchanged from prior handoffs.

### Push delay across multiple variants

**Concern:** Keeping commits local across 2 more variants means a larger push at the end. Marginal risk of branch divergence.

**Mitigation:** Periodic push at variant boundaries. User can decide.

## References

### Files

- `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — run record (now at `c704eafa`)
- `packages/plugins/codex-collaboration/server/runtime.py` — restored
- `.tmp/variant-baseline.patch` — captured patch (still on disk; gitignored)
- `.tmp/variant-baseline.applied-at` — patch application timestamp (still on disk)

### Code references (verified this session)

- Sandbox policy builder (restored): `packages/plugins/codex-collaboration/server/runtime.py:23-38`
- Sandbox policy call site (unchanged): `packages/plugins/codex-collaboration/server/delegation_controller.py:1327`
- Plugin data root (resolved this session via inspection-artifact paths): `~/.claude/plugins/data/codex-collaboration-inline/`

### MCP tool calls this session

| Tool | Outcome |
|---|---|
| `codex_delegate_start` | Returned `needs_escalation` immediately; parked at request 0 (`command_approval`) |
| `codex_delegate_decide(deny, request 0)` | `decision_accepted: true` |
| `codex_delegate_poll` ×3 | Captured transitions: running → needs_escalation (req 1, file_change null scope) → completed |
| `codex_delegate_decide(deny, request 1)` | `decision_accepted: true` |

### Commits this session

| Commit | Subject | State |
|---|---|---|
| `2cb223d4` | docs(delegate): capture Baseline attempt 1 evidence + restoration on T-01 run record | Local |
| `c704eafa` | docs(delegate): correct Plugin start UTC on Baseline block (macOS date pitfall) | Local |

### Branches

- `feature/delegate-execution-diagnostic-record` at `c704eafa` (2 commits ahead of origin)

### Job artifacts (delegate-framework managed)

- Worktree: `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/6753a537-99d8-456f-a1c0-1c79f13a2fc9/worktree`
- Inspection: `<worktree-parent>/inspection/{full.diff,changed-files.json,test-results.json}`
- Artifact hash: `d604766ea0e6f7d82c1f37f5b66d10d985cfd0271b01f3a7491ceb8f167d7b8d`

## Gotchas

### Plugin process holds patched code in memory after disk restoration

(Carried.) Restart required before Candidate A. New PIDs after restart should differ from `11645`/`11696`.

### macOS `date -u -j -f` silently mis-converts local-tz inputs

**Wrong recipe:** `date -u -j -f FMT "<lstart>" +"%Y-%m-%dT%H:%M:%SZ"`
**Correct recipe:** `EPOCH=$(date -j -f FMT "<lstart>" +%s); date -u -r "$EPOCH" +"%Y-%m-%dT%H:%M:%SZ"`

### Smoke artifact + test-results.json + worktree state — all empty for Baseline

This is the EXPECTED Baseline outcome — symptom of S1, not a failure of the diagnostic.

### Two ahead of origin (this session's 2 commits not pushed)

User decision pending. If pushing at session start: `git push` should be straightforward (fast-forward).

### `codex_delegate_promote` / `codex_delegate_discard` not invoked

Job is in `promotion_state: pending` per terminal poll. Worktree persists at `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/6753a537-...`. If disk is tight, `codex_delegate_discard` would clean it up. Default: leave for audit-trail purposes; clean up after Candidate B (full diagnostic complete).

### Run Identity drift continues

Run Identity table records `49d93001` (frozen). Live HEAD now `c704eafa`. Drift of 7 commits is expected by design (two-layer HEAD anchor pattern).

### `test-results.json` over-action recurs across variants?

Possible. The delegate's autopilot toward `.codex-collaboration/test-results.json` is a framework property, not specific to Baseline. Candidate A's first proposal may include the same write. If so, it'll add a 4th shell-visible action — potentially making `shell_action_count >= 3` and bringing ratio interpretation back into play.

### `_Path` aliased import in instrumentation block

If re-applying instrumentation for Candidate A (with `[CANDIDATE_A]` label), preserve the `from pathlib import Path as _Path` aliased re-import inside the function. The aliased re-import is intentional — visual hint for restoration. Don't simplify to module-top `Path`.

## User Preferences

**Strict-gate before fallback investigation (carried).**

**Two-layer HEAD anchor preserved (carried, applied).** Run Identity stays at `49d93001`; live commits drift independently.

**Decision fence over decision wall (carried, applied).** Denied parked requests as conservative path; `--debug mcp` (stderr) and Candidate-prep schema-dump remain documented future options without commitment.

**Push at clean phase boundaries (carried, applied with deferral).** Both commits at clean boundaries; push deferred to user.

**Handle commits proactively (carried, applied).** Both commits this session done without asking.

**No mid-track doc commits during benchmark — N/A here** (this is a diagnostic, not a benchmark).

**Record operational findings in durable artifacts before handoff (carried, applied).** TZ-bug pitfall is now documented in the run record's "Plugin process start timestamp" cell, not just in this handoff.

**Tightening guidance via /copy-routed scrutiny (carried, applied).** User routed the deny adjudication through Codex; structured 9-section recommendation aligned with my read.

**No pending-fill execution under partial validity (carried, applied).** Waited for full evidence + decisive recommendation before adjudicating each escalation.

**Two-clock-domain cross-check (new this session).** When recording multi-source timestamps, build in at least one cross-check pair so silent recipe errors trigger an obvious anomaly. Adopted for evidence-template practice.
