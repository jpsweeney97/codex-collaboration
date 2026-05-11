---
date: 2026-04-28
time: "12-35"
created_at: "2026-04-28T16:35:00Z"
session_id: 7337aa50-e517-44f7-8793-eebb3f0fe3db
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-28_06-58_t01-step-1-complete-file-write-instrumentation-patched-ready-for-restart.md
project: claude-code-tool-dev
branch: feature/delegate-execution-diagnostic-record
commit: 19ed53b7
title: T-01 Baseline attempt 1 fully closed and tightened (8 review findings addressed); ready for Candidate A restart
type: handoff
files:
  - docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md
  - packages/plugins/codex-collaboration/server/runtime.py
  - .tmp/variant-baseline.patch
  - .tmp/variant-baseline.applied-at
supersedes: docs/handoffs/2026-04-28_12-10_baseline-attempt-1-complete-tz-bug-corrected-ready-for-candidate-a.md
---

# Handoff: T-01 Baseline attempt 1 fully closed and tightened; ready for Candidate A

## Goal

Continue T-20260423-01 live delegate-execution remediation. **This handoff supersedes the 12:10 version** (which captured the mid-stage state before two adversarial-review-driven closure batches). Baseline attempt 1 is now fully closed: per-variant evidence + adjudication tables (Branch decision, Threshold Calibration) + store-row JSONL inspection + top-level status + reusable-template fixes are all in place.

**Why we stopped:** Baseline closure is complete. Candidate A requires another Claude Code restart so the running plugin process (PID `11696`) re-imports the un-patched `runtime.py` from disk.

## Session Narrative

Resumed from `2026-04-28_06-58_t01-step-1-complete-...md`. Pre-flight verified post-restart state (PIDs differ from prior session; plugin start > patch applied; dirty diff matches `.tmp/variant-baseline.patch`). User `/copy`-routed a Codex docs read corroborating the file-sink choice on three new grounds; answered the two checkpoints with two Pre-run-evidence tightenings.

Locked Pre-run evidence into a new `### Variant: Baseline (attempt 1)` block instantiated from the Per-Variant Evidence template. Quoted concrete smoke objective (timestamp pinned to `20260428T005625`) and invoked `codex_delegate_start` — returned `needs_escalation` immediately with `command_approval` parked at `request_id=0` for a chained `/bin/zsh -lc` command. Read `/tmp/codex-collab-baseline-runtime-proof.log`: production `sandboxPolicy` reproduced byte-for-byte, T-01 mechanism confirmed.

User `/copy`-routed a structured 9-section Codex consultation: deny + record S1 + restore + advance to Candidate A. Aligned with my recommendation; followed verbatim. Denied `request_id=0`. Polled. **Surprise:** state went `running` → back to `needs_escalation` with a new `request_id=1`, `kind: file_change`, **scope null**. Stored memory `feedback_deny_finalizes_job.md` says deny prevents agent adaptation — empirically false here. Denied `request_id=1`. Job reached `completed` with `changed_files: []`, `artifact_hash d604766e...`.

Locked terminal evidence into the run record. Restored: `git checkout -- runtime.py` + `trash /tmp/codex-collab-baseline-runtime-proof.log`. Verified clean. Committed as `2cb223d4`.

Then ran a sanity check on the recorded plugin start UTC value out of paranoia — caught a 4-hour error from `date -u -j -f` silently treating local-tz input as UTC (local tz here is EDT/-0400). Re-derived via epoch round-trip; corrected to `2026-04-28T15:41:29Z`. Cross-checked against runtime-proof artifact's independent timestamp (Python `datetime.now(timezone.utc)` → `2026-04-28T15:53:37Z`): now ~12min gap (plausible). Updated run record (two cells); committed correction as `c704eafa`.

Wrote a 12:10 handoff. User `/copy`-routed a first adversarial review (5 closure findings — store evidence still TBD; Branch decision unassigned; Threshold Calibration contradicting captured counts; top-level status stale; Raw excerpts placeholder). All real. Per "No pending-fill execution under partial validity," closed before Candidate A. Inspected the per-session JSONL stores at `~/.claude/plugins/data/codex-collaboration-inline/`, locked all store-row evidence (jobs.jsonl L1-12, requests.jsonl L1-6, journal L1-9, audit L62-64), filled Threshold Calibration and Branch decision tables, populated Raw excerpts with full transition transcript and cross-store timestamp consistency table, updated top-level status. Committed as `68c993fc` (+129/-21 lines).

User `/copy`-routed a second adversarial review (3 follow-up findings: broken `date -u -j -f` recipe still in the per-variant template — copy source for Candidate A and B; S7 fired loosely from `proposedExecpolicyAmendment` in PendingRequestStore L1 but not recorded; cleanup-row contradiction with filled store rows). Fixed all three: replaced template recipe with epoch round-trip + pitfall warning; added S7 as secondary fired branch with caveat; rewrote cleanup cell. Added Hygiene action #5 to narrow S7 definition for future variants. Committed as `19ed53b7` (+4/-4 lines).

This handoff (12:35) supersedes the 12:10 version with the full closure context.

## What changed since the 12:10 handoff

Two closure batches landed after the 12:10 handoff was written, prompted by Codex's adversarial review of the run record's contractual completeness:

### Closure batch 1 — `68c993fc`: "close Baseline attempt 1 adjudication on T-01 run record" (+129 / -21 lines)

Addressed 5 closure gaps:

1. **Top-level status** (line 5): "draft first-run record, not yet executed" → "Baseline attempt 1 executed and adjudicated (Branch S1 — Sandbox still blocked); Candidate A pending operator-mediated Claude Code restart."
2. **Per-variant TBDs filled from JSONL inspection** of `~/.claude/plugins/data/codex-collaboration-inline/`:
   - `Approval policy value`: inferred `untrusted` from PendingRequestStore L1's `available_decisions` list (full 6-option incl. `acceptWithExecpolicyAmendment`).
   - `JSON-RPC wire id type`: integer (`raw_request_id 0` and `1` are unquoted JSON ints in `requests.jsonl` L1+L4; plugin's surface `request_id` is the stringified form).
   - `PendingRequestStore rows`: 6 lines (3 per request × 2 requests). Internal `deny` → wire `decline`. Both requests share `codex_thread_id` and `codex_turn_id` — single-turn adaptation.
   - `DelegationJobStore rows`: 12 lines covering full lifecycle (queued → running → escalated×2 with running interludes between denies → completed/promotion_state pending).
   - `OperationJournal rows`: 9 lines (3 ops × 3 phases; all clean).
   - `Audit rows`: events.jsonl L62-64 (delegate_start + 2 denies). **Independent timestamp cross-check**: `delegate_start` audit at `2026-04-28T15:53:37Z` matches runtime-proof artifact emit `2026-04-28T15:53:37.116985+00:00` to sub-second precision.
3. **Threshold Calibration** populated: shell_action_count `2`, approval_request_count `2`, ratio `no signal for threshold comparison`, calibration deferred to Candidate A's first successful baseline-equivalent run per Recalibration rule sub-bullet 3.
4. **Branch decision** adjudicated: Primary S1 (Sandbox still blocked) by precedence; 7 secondary observations to carry forward; Engineering next action: proceed to Candidate A; 4-item Hygiene next action.
5. **Attempt history + Raw excerpts** populated: full transition transcript, JSONL line refs, runtime-proof line preserved verbatim, inspection artifact summaries, cross-store timestamp consistency table.

### Closure batch 2 — `19ed53b7`: "tighten Baseline closure (template recipe, S7 fire, cleanup)" (+4 / -4 lines)

Addressed 3 follow-up findings from a second adversarial review of `68c993fc`:

1. **Per-Variant Evidence template (line ~582)** — replaced the broken macOS `date -u -j -f FMT INPUT +OUTFMT` recipe (which silently relabels local-tz input as UTC) with the epoch round-trip recipe. Highest leverage of the three: this template is the copy source for Candidate A and Candidate B, so the bad recipe would have propagated without this fix.
2. **Branch decision "Branches fired"** — added S7 (Amendment required) as a secondary fired branch under loose interpretation. PendingRequestStore L1's `requested_scope.proposedExecpolicyAmendment` is populated, triggering S7's first clause literally. Caveat: under `untrusted` mode this field appears in every `command_approval` request as Codex's standard amendment-offer mechanism, so the loose fire is informational only. S1 remains primary by precedence.
3. **Cleanup performed cell** — removed the contradiction with the now-filled store-evidence rows. Cell now states store inspection completed this session; underlying JSONL files + job worktree + inspection artifacts intentionally preserved.
4. **Hygiene next action #5** — added action: narrow Symptom Attribution row S7's "or" so future variants don't auto-fire S7 on every `untrusted`-mode escalation. Suggested split into S7a (payload-presence; informational) and S7b (response-required; classification-driving).

## Decisions

### Treat closure as a contract — not an option

**Choice:** Iterate two closure batches in this same session rather than deferring adjudication to next session.

**Driver:** User preference memory: "No pending-fill execution under partial validity." Branch Precedence #1.b explicitly classifies "missing storage evidence" as "always invalidates" the run. Deferring would have meant Candidate A starts against an evidence-incomplete Baseline.

**Confidence:** High — Codex's two adversarial reviews independently surfaced complementary gap sets.

### Fix the template, not just the cell

**Choice:** When correcting the macOS `date` pitfall, edit the *Per-Variant Evidence template* (line ~582), not just the Baseline cell. The template is the copy source for Candidate A and Candidate B blocks.

**Driver:** Single-fix-vs-template-fix tradeoff. Single-fix is faster but propagates the error to future variants. Template-fix is the durable one.

### Record S7 as fired (loose interpretation) and queue narrowing

**Choice:** Add S7 (Amendment required) as a secondary fired branch with explicit caveat about the loose interpretation; queue Hygiene action to narrow S7's definition for future variants.

**Driver:** Both completeness and clarity. The Symptom Attribution row literally fires under our evidence (presence of `proposedExecpolicyAmendment` in request payload). Hiding that fact violates "record all fired branches." But the literal fire is informational only — under `untrusted` mode, `proposedExecpolicyAmendment` appears in *every* `command_approval` request as the standard amendment-offer surface. Narrowing the definition fixes future-variant interpretation without changing this attempt's classification.

## Changes

### Commits (this session, local — NOT pushed)

| Commit | Subject | Diff stat |
|---|---|---|
| `2cb223d4` | docs(delegate): capture Baseline attempt 1 evidence + restoration on T-01 run record | +92 / -0 |
| `c704eafa` | docs(delegate): correct Plugin start UTC on Baseline block (macOS date pitfall) | +2 / -2 |
| `68c993fc` | docs(delegate): close Baseline attempt 1 adjudication on T-01 run record | +129 / -21 |
| `19ed53b7` | docs(delegate): tighten Baseline closure (template recipe, S7 fire, cleanup) | +4 / -4 |

Branch is **4 ahead** of `origin/feature/delegate-execution-diagnostic-record`.

### `packages/plugins/codex-collaboration/server/runtime.py` — restored (no diff vs HEAD)

Disk state matches `7650366d`. **Running plugin process still holds patched code in memory** — restart required before Candidate A.

### `/tmp/codex-collab-baseline-runtime-proof.log` — captured then trashed

Preserved verbatim in run record's "Observed sandboxPolicy payload" cell + Raw excerpts block.

## Codebase Knowledge

### Plugin data root structure (verified this session)

`~/.claude/plugins/data/codex-collaboration-inline/`:

| Subdir | Purpose | Per-session? |
|---|---|---|
| `delegation_jobs/<session-id>/jobs.jsonl` | DelegationJobStore — job lifecycle | yes |
| `pending_requests/<session-id>/requests.jsonl` | PendingRequestStore — escalation events | yes |
| `journal/operations/<session-id>.jsonl` | OperationJournal — three-phase op records (intent / dispatched / completed) | yes |
| `audit/events.jsonl` | Audit log | NO — single file across sessions |
| `analytics/outcomes.jsonl` | Analytics outcomes | NO — shared |
| `lineage/<session-id>/handles.jsonl` | Cross-job lineage | yes |
| `runtimes/delegation/<job-id>/worktree` | Delegate's working tree | per-job |
| `runtimes/delegation/<job-id>/inspection/` | Framework-generated artifacts (full.diff, changed-files.json, test-results.json) | per-job |
| `session_id` | Marker file with current session UUID | top-level |

Session id for this session: `7337aa50-e517-44f7-8793-eebb3f0fe3db` (matches `session_id` file content).

### Delegate state machine (corrected mental model)

Empirically observed transitions for this Baseline attempt (12 jobs.jsonl rows):

```
queued                                                     [L1, op:create]
  → running                                                [L2]
    → parked at request 0 (command_approval)               [L3, parked_request_id=0]
    → needs_escalation                                     [L4]
    [orchestrator: deny request 0]
  → running                                                [L5]
  → cleared parked                                         [L6, parked_request_id=null]
    [agent adapts, proposes file_change]
  → parked at request 1 (file_change, null scope)          [L7]
  → needs_escalation                                       [L8]
  [orchestrator: deny request 1]
  → running                                                [L9]
  → cleared parked                                         [L10]
[agent finalizes after second deny]
  → completed (promotion_state: pending)                   [L11]
  → artifacts updated (artifact_hash, 3 paths)             [L12]
```

Key insight: deny doesn't unilaterally terminate. It rejects ONE proposed action; the agent then either (a) adapts to a different action class within the same Codex turn, or (b) finalizes. We saw (a) once, (b) on the second deny.

### `proposedExecpolicyAmendment` is universal, not signal

Under `untrusted` approval policy, *every* `command_approval` request payload includes `requested_scope.proposedExecpolicyAmendment`. It's Codex's standard offer of an amendment path, not a signal that progress is blocked on a missing response shape. The S7 row's first clause currently fires informationally on every `untrusted` escalation; the second clause (App Server *requires* the amendment) is the load-bearing one.

### macOS `date -u -j -f` is a parsing trap (now also captured in template)

With `-u` set, both input and output are treated as UTC. `ps -o lstart` returns local-tz with no zone marker. The recipe `date -u -j -f FMT INPUT +OUTFMT` thus relabels local-tz value as UTC instead of converting. Correct macOS recipe is two-step epoch round-trip:
```bash
EPOCH=$(date -j -f "%a %b %d %H:%M:%S %Y" "$LSTART" +%s)
date -u -r "$EPOCH" +"%Y-%m-%dT%H:%M:%SZ"
```
The Per-Variant Evidence template now documents this pitfall explicitly so future variants don't repeat the error.

### Runtime-proof artifact emit + audit row + corrected plugin start agree

Three independent UTC sources cross-check:
- Plugin start (corrected via epoch round-trip): `2026-04-28T15:41:29Z`
- `delegate_start` audit row (events.jsonl L62): `2026-04-28T15:53:37Z` (+12m08s)
- Runtime-proof emit (Python `datetime.now(timezone.utc)`): `2026-04-28T15:53:37.116985+00:00` (matches audit row sub-second)

Disagreement implies parsing/conversion error in one recipe. Build cross-checks into evidence templates.

### Surprising findings carried forward

- **Memory `feedback_deny_finalizes_job.md` is empirically wrong** — deny does NOT finalize; agent adapts.
- **`available_decisions: []` for null-scope `file_change`** — anomalous; protocol shape question worth investigating.
- **Internal `deny` → wire `decline`** — naming differs across orchestrator and PendingRequestStore `response_payload`.
- **Both escalations from same Codex turn** (`019dd4cb-c461-7dc0-b3f8-2329e816fd81`) — adaptation stays within one turn.
- **Delegate over-action toward `test-results.json`** — recurs across attempts; may push `shell_action_count >= 3` in Candidate A.

### Key Locations

| Concept | Location |
|---|---|
| Run record (now closed for Baseline) | `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` |
| Baseline variant block | run record §"Per-Variant Evidence" → "Variant: Baseline (attempt 1)" |
| Branch decision adjudication | run record §"Branch Precedence" → Branch decision table |
| Threshold Calibration (deferred to Candidate A) | run record §"Threshold Calibration" |
| Patched-and-restored build site | `packages/plugins/codex-collaboration/server/runtime.py:23-38` |
| Patch capture file | `.tmp/variant-baseline.patch` (gitignored) |
| Patch applied at | `.tmp/variant-baseline.applied-at` (gitignored) |
| Plugin data root | `~/.claude/plugins/data/codex-collaboration-inline/` |
| Plugin's session id file | `<plugin-data-root>/session_id` |

## Context

### Project State

| Item | State |
|---|---|
| Run record | **Baseline attempt 1 fully closed**; 4 unpushed commits |
| Run Identity table | Frozen at `49d93001` per two-layer pattern; live drift to `19ed53b7` |
| Sandbox blocker | Confirmed live (S1) |
| Baseline outcome | Branch S1 primary; S7 secondary (loose, informational); ratio `no signal for threshold comparison` |
| Plugin process (this session) | PIDs `11645`/`11696`; in-memory code is patched (post-disk-restoration) |
| Runtime-proof artifact | Trashed |
| Patch on disk | RESTORED |
| Working tree | Clean except 8 carry-forward ticket-file moves |
| Pushed to origin? | NO — 4 commits local |

### Mental Model

- **Memory is patched; disk is restored.** Restart re-imports restored code → safe to start Candidate A.
- **The diagnostic's evidence contract has been validated end-to-end** for Baseline. Candidate A and Candidate B can now use the same template (with corrected recipe) and trust their own closure cycles will reach the same depth.
- **S1 is structurally proven**, not just observed: runtime-proof shows `readableRoots: [worktree]` + `includePlatformDefaults: False` at the build site; parked `command_approval` for `/bin/zsh -lc` is the predictable consequence. Candidate A (`includePlatformDefaults: True`) directly tests the contrapositive.

### Environment

- Working tree: `feature/delegate-execution-diagnostic-record` at `19ed53b7` (4 ahead of origin); 8 ticket-file moves carry-forward.
- Codex: `codex-cli 0.125.0`.
- Local timezone: `EDT (-0400)`. Pitfall: macOS `date -u -j -f` (now documented in template).
- Plugin process: PID `11696` (python child), PID `11645` (uv wrapper); started `2026-04-28T15:41:29Z` UTC (corrected). In-memory code is patched.
- Plugin data root: `~/.claude/plugins/data/codex-collaboration-inline/`.

## Learnings

### Closure vs richness are different evidence states

A variant block can be evidence-rich (every TBD filled) while the run record's adjudication is incomplete (top-level status stale, Branch decision unassigned, Calibration table contradicting captured counts). Closure means the document's contract is satisfied, not just that row-by-row evidence is collected. Adversarial review surfaces this gap precisely.

### Fix templates, not just instances

When you find a bug in a copy-source (template, codegen seed, scaffold), fix the source. Fixing only the current instance leaves the bug to propagate to future copies. The macOS `date` recipe was the case-in-point: per-variant template at line 582 was the copy source for Candidate A and B; fixing only the Baseline cell would have left the bad recipe to be copied verbatim.

### Loose vs strict definitions create silent classification ambiguity

Symptom Attribution row S7's "or" structure ("payload contains X *or* requires Y") collapses two distinct symptoms into one row. The first clause (payload-presence) is universal under `untrusted` mode; the second (response-required) is the load-bearing classification driver. Future variants will benefit from explicit S7a/S7b split or stricter "or" wording.

### Cross-store timestamp triangulation catches silent recipe errors

Three UTC sources agreeing on relative spacing validates a recipe; disagreement (4h12m gap vs ~12min gap) is the symptom. Build cross-checks into evidence templates — they're silent on correct values, loud on broken recipes.

## Next Steps

### 1. Push decision

User to decide whether to push the 4 commits to `origin/feature/delegate-execution-diagnostic-record`. Recommendation: push now (Baseline is complete; downstream Candidate A interpretation reads against Baseline's S1 outcome; future-session continuity benefits).

### 2. Operator: restart Claude Code

**Acceptance criteria post-restart:**
- New plugin process PIDs differ from `11645`/`11696`.
- `git diff packages/plugins/codex-collaboration/server/runtime.py` → EMPTY (disk restored).
- `git status --short` → only the 8 carry-forward ticket-file moves.
- `git log --oneline -5` shows the 4-commit chain ending at `19ed53b7`.

### 3. New session: `/handoff:load`

Picks up THIS handoff (12-35) and archives it. The 12-10 handoff stays in `docs/handoffs/` (not loaded; superseded by this one).

### 4. New session: optional schema-dump artifact (deferred from this session)

Capture `codex --version` + `codex app-server generate-json-schema` for the run record's Cross-variant block. Validates Candidate A's narrower-shape policy is schema-accepted by the installed Codex version. Schema proof complements (not replaces) runtime-payload proof.

### 5. New session: Candidate A patch + Pre-run evidence + execution

**Candidate A patch:** flip `"includePlatformDefaults": False` → `True` at `runtime.py:23`. Optionally also add the runtime-proof file-write instrumentation with `[CANDIDATE_A]` label.

Capture: `.tmp/variant-candidate-a.patch` + `.tmp/variant-candidate-a.applied-at`. Then restart again so the new plugin process re-imports Candidate A code.

Pre-flight uses the **corrected template recipe** (epoch round-trip, NOT `date -u -j -f`). Per the template's new explicit guidance, also cross-check plugin start UTC against the runtime-proof artifact's `datetime.now(timezone.utc)` timestamp.

Expected outcome: shell unblocked (delegate can `mkdir`, `printf`, `cat`); smoke artifact created.

### 6. New session: memory correction

Update `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_deny_finalizes_job.md` with corrected mechanism: deny rejects ONE action; agent may iterate once before terminal.

### 7. Hygiene: narrow S7 definition

Edit Symptom Attribution row S7 to split S7a (payload-presence; informational) and S7b (response-required; classification-driving), or strengthen the "or" wording. Action item #5 in Branch decision Hygiene next action.

## In Progress

Clean stopping point. No work in flight.

- 4 commits this session (`2cb223d4`, `c704eafa`, `68c993fc`, `19ed53b7`). All local.
- Restoration complete on disk; memory restoration pending Candidate-A restart.
- Working tree dirty only on 8 carry-forward ticket-file moves.
- Job `6753a537-...` left at `promotion_state: pending` (preserved for cross-variant correlation).

## Open Questions

- **Did the prior session's handoff use the same broken `date -u -j -f` recipe?** Same machine, same recipe template. Likely yes. Audit recommended in next session.
- **Why did `file_change` come back with `available_decisions: []`?** Protocol quirk vs. agent-internal placeholder vs. specific Codex behavior under "denial-after-shell-rejection." Worth a deeper look before Candidate A in case it recurs.
- **Why is `proposedExecpolicyAmendment` always populated under `untrusted` mode?** Confirms Codex's amendment-offer mechanism but exact triggering conditions unclear. Affects S7 narrowing.
- **Will Candidate A's `includePlatformDefaults: True` actually unblock `/bin/zsh`?** Pending empirical confirmation.

## Risks

### Operator forgets to restart Claude Code before Candidate A

**Concern:** Same as before — running plugin holds PATCHED code; new Candidate A patch on disk wouldn't be observed.

**Mitigation:** Pre-flight in next session: verify plugin PID differs from `11696`. Verify `git diff runtime.py` is EMPTY at session start.

### Memory drift if `feedback_deny_finalizes_job.md` is not corrected

**Mitigation:** Memory correction is in Next Steps #6. Low risk if next session reads the handoff.

### Candidate A's variant block must use the corrected template recipe

**Concern:** If next-session operator copies the OLD pre-19ed53b7 template by reflex, the broken `date -u -j -f` recipe could resurface.

**Mitigation:** The template at `runtime-proof:582` now contains explicit "do NOT use" warnings + the c704eafa incident reference. Next-session pre-flight should also cross-check the corrected timestamp against the runtime-proof artifact's `datetime.now(timezone.utc)` source.

### S7 definition narrowing could change Candidate A's classification

**Concern:** If Candidate A succeeds in producing artifacts but `proposedExecpolicyAmendment` still surfaces (likely under `untrusted`), the loose S7 fire would record again. Without narrowing, this could conflate "S7 informational" with "S7 amendment-required" classifications.

**Mitigation:** Hygiene action #5 to narrow S7 definition. Could be done before or alongside Candidate A; not blocking.

## References

### Files

- `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — run record (now at `19ed53b7`)
- `packages/plugins/codex-collaboration/server/runtime.py` — restored
- `.tmp/variant-baseline.patch`, `.tmp/variant-baseline.applied-at` — gitignored

### Code references (verified this session)

- Sandbox policy builder (restored): `packages/plugins/codex-collaboration/server/runtime.py:23-38`
- Plugin data root: `~/.claude/plugins/data/codex-collaboration-inline/`
- Per-Variant Evidence template (with corrected macOS recipe): run record line ~582

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
| `68c993fc` | docs(delegate): close Baseline attempt 1 adjudication on T-01 run record | Local |
| `19ed53b7` | docs(delegate): tighten Baseline closure (template recipe, S7 fire, cleanup) | Local |

### Branches

- `feature/delegate-execution-diagnostic-record` at `19ed53b7` (4 commits ahead of origin)

### Job artifacts (delegate-framework managed)

- Worktree: `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/6753a537-99d8-456f-a1c0-1c79f13a2fc9/worktree`
- Inspection: `<worktree-parent>/inspection/{full.diff,changed-files.json,test-results.json}`
- Artifact hash: `d604766ea0e6f7d82c1f37f5b66d10d985cfd0271b01f3a7491ceb8f167d7b8d`

### JSONL refs (Baseline attempt 1)

- `delegation_jobs/7337aa50-.../jobs.jsonl` L1-12 (full lifecycle)
- `pending_requests/7337aa50-.../requests.jsonl` L1-6 (req 0 + req 1)
- `journal/operations/7337aa50-....jsonl` L1-9 (3 ops × 3 phases)
- `audit/events.jsonl` L62-64 (delegate_start + 2 denies)

### Superseded handoff

- `docs/handoffs/2026-04-28_12-10_baseline-attempt-1-complete-tz-bug-corrected-ready-for-candidate-a.md` — captures the mid-stage state before closure batches 1 + 2. Preserved in `docs/handoffs/` (not archived) for historical reference; will not be loaded by `/handoff:load` (this 12-35 version is more recent).

## Gotchas

### Plugin process holds patched code in memory after disk restoration

(Carried.) Restart required before Candidate A. New PIDs after restart should differ from `11645`/`11696`.

### macOS `date -u -j -f` silently mis-converts local-tz inputs

**Wrong recipe:** `date -u -j -f FMT "<lstart>" +"%Y-%m-%dT%H:%M:%SZ"` — relabels local as UTC.

**Correct recipe:** `EPOCH=$(date -j -f FMT "<lstart>" +%s); date -u -r "$EPOCH" +"%Y-%m-%dT%H:%M:%SZ"`.

Now also captured in the run record's Per-Variant Evidence template (line ~582) with explicit "do NOT use" warning.

### `proposedExecpolicyAmendment` triggers S7's first clause on every `untrusted` escalation

(New this session.) Until S7 is narrowed, every Candidate variant's `command_approval` request will fire S7 informationally. Don't conflate with S7 response-required classification. Narrowing is Hygiene action #5.

### `available_decisions: []` for null-scope `file_change`

(Open question.) If Candidate A surfaces a similar request, deny by default unless protocol shape is clarified.

### Smoke artifact + test-results.json + worktree state — all empty for Baseline

EXPECTED outcome — symptom of S1, not a failure of the diagnostic.

### 4 ahead of origin; push deferred

User decision pending. Fast-forward push expected.

### Run Identity drift

Run Identity table records `49d93001` (frozen). Live HEAD now `19ed53b7`. Drift of 9 commits expected by design.

## User Preferences

**Strict-gate before fallback investigation (carried).**

**Two-layer HEAD anchor preserved (carried, applied).**

**Decision fence over decision wall (carried, applied).**

**Push at clean phase boundaries (carried, applied with deferral).**

**Handle commits proactively (carried, applied).** Four commits this session, all without asking.

**Record operational findings in durable artifacts before handoff (carried, applied).** TZ-bug pitfall, S7 caveat, and store-row line refs all in the run record before this handoff.

**Tightening guidance via /copy-routed scrutiny (carried, applied).** User routed three review cycles through Codex; closure batches 1 + 2 directly responsive to the structured findings.

**No pending-fill execution under partial validity (carried, applied).** Two closure batches landed before the handoff because partial validity meant Candidate A couldn't safely start.

**Two-clock-domain cross-check (new this session, codified in template).** Independent UTC sources cross-check captures parsing errors silently; correct values fly through, broken recipes raise an obvious anomaly.

**Fix templates, not just instances (new this session).** When you find a bug in a copy-source, fix the source. The macOS `date` recipe was the case-in-point.

**Closure vs richness as distinct evidence states (new this session).** A variant block can be evidence-rich while the run record's adjudication is incomplete. Closure means the document's contract is satisfied — not just row-by-row evidence collected.
