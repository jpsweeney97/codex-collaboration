---
date: 2026-04-28
time: "17-13"
created_at: "2026-04-28T17:13:56Z"
session_id: 801b6646-171e-4a80-a647-c9de35041d4c
resumed_from: docs/handoffs/archive/2026-04-28_12-35_baseline-attempt-1-closed-and-tightened-ready-for-candidate-a.md
project: claude-code-tool-dev
branch: feature/delegate-execution-diagnostic-record
commit: 5a1e937e
title: Candidate A patch staged and pre-variant evidence locked; restart-boundary handoff
type: handoff
files:
  - packages/plugins/codex-collaboration/server/runtime.py
  - docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md
  - .tmp/variant-candidate-a.patch
  - .tmp/variant-candidate-a.applied-at
  - .tmp/app-server-schema-pre-candidate-a/
---

# Handoff: Candidate A patch staged and pre-variant evidence locked; restart-boundary handoff

## Goal

Continue T-20260423-01 live delegate-execution remediation. **This session closed three items from the 12-35 handoff's Next Steps register** (memory correction, S7 narrowing, schema-dump artifact) and **staged Candidate A on disk in instrumented form**. The session ends at a deliberate restart boundary so the next session can re-import patched code and execute the variant.

**Bigger picture:** Baseline attempt 1 proved S1 (Sandbox still blocked) is structural under `includePlatformDefaults: False` — runtime-proof confirmed `readableRoots: [worktree]` only. Candidate A directly tests the contrapositive: with `includePlatformDefaults: True`, does platform-defaults grant unblock `/bin/zsh -lc`? If yes, the smoke artifact (`mkdir`/`printf`/`cat` sequence) succeeds and Branch S1 stops firing. If no, narrower per-binary grants (Candidate B matrix) are needed.

**Trigger:** Prior handoff's Next Steps #4 (schema dump), #5 (Candidate A patch), #6 (memory correction), #7 (S7 narrowing) were all queued. User authorized closure batches across this session in three /copy-routed alignments.

**Stakes:** Each variant requires an operator-mediated Claude Code restart cycle (because the running plugin holds in-memory imported code), so each cycle is ~10 minutes minimum. Pre-variant evidence completeness directly determines whether the variant outcome is interpretable on first attempt vs requiring a re-run.

**Connection to project arc:** Baseline closed (Branch S1 primary). Candidate A is the first attempted *resolution* variant (vs Baseline's *characterization* role). Outcome shapes whether T-01 remediation lands at `includePlatformDefaults: True` or escalates to Candidate B's matrix exploration.

## Session Narrative

Resumed from `2026-04-28_12-35_baseline-attempt-1-closed-and-tightened-ready-for-candidate-a.md`. Started with a parallel-fanout pre-flight to validate the restart boundary the prior session left for the operator. Ran 4 checks simultaneously: plugin process PIDs, `runtime.py` diff vs HEAD, git status + log + ahead/behind, .tmp/ carry-forward artifacts + plugin session marker + branch state.

**Two anomalies surfaced.** First, `pgrep -fa "uv run.*codex-collaboration"` returned a transient PID (`10668`) not in the `ps -ef | grep` output. Investigation: pgrep matches its own argv when the pattern appears in cmdline — phantom matches from pgrep itself or its parent shell on each call. Real plugin chain is just `7116` (claude) → `7163` (uv) → `7165` (python child); all distinct from prior session's `11645`/`11696`. Restart confirmed.

Second, `git rev-list --left-right --count origin/<branch>...HEAD` returned `0\t0`, but the handoff said "4 ahead." Reflog inspection: `19ed53b7 update by push @{0}, 7650366d update by push @{1}` — the user pushed those 4 commits between the prior session's handoff write and this session's load. Next Step #1 (push decision) was already done.

Pre-flight verdict: clean to proceed. Reported the two-anomaly resolutions back to user with explanations and a remaining-work table. User responded `Yes proceed with pre-flight verification` (this had already happened — I'd already shown results, so the response confirmed acceptance).

**First closure batch: memory + S7 as a single commit.** User said "Proceed with the memory correction (#6) and S7 narrowing (#7) as a single closure commit." I read the targets in parallel: memory file `feedback_deny_finalizes_job.md` (12 lines, claimed "deny finalizes the job"), MEMORY.md index line 88 with matching wording, and the run record's S7 references (lines 877, 893, 915, 919, 933 — five touchpoints). Realized the memory file lives outside the repo (`~/.claude/projects/.../memory/`), so the "single commit" would only contain run-record edits; the memory edits would be a separate side-effect with audit trail in the commit message body.

Made all edits in two batches. Memory rewrite: frontmatter `name`/`description` flipped from "deny finalizes" to "deny rejects ONE action; agent may adapt within same Codex turn"; body rewritten with empirical evidence from Baseline attempt 1's `jobs.jsonl` (12-row lifecycle showing within-turn adaptation between two denies); MEMORY.md hook updated. Then 5 run-record edits: split row S7 into S7a (payload-presence; informational under `untrusted` mode) + S7b (response-required; classification-driving), updated Branch Precedence rule 1.d to reference S7b only, rewrote rule 4 ("Amendment required") to require S7b not S7a with explicit "S7a alone does NOT trigger" caveat, rewrote Branch decision narrative to record S7a-fired-informationally + S7b-did-NOT-fire (with `available_decisions` 6-option-list as the evidence S7b doesn't fire), marked Hygiene actions #1 and #5 as **DONE this session** preserving the original action descriptions. Verified all 7 post-edit S7 references resolved consistently. Committed `dd897c5e`.

**Second user prompt: "Capture it first."** User chose to capture the App Server schema dump *before* applying the Candidate A patch, with a structured rationale: cheap, non-contaminating if treated as read-only, gives "a stable 'tool/schema environment at Candidate A entry' record before any local patch or restart changes the runtime story," and "cleanly separates **App Server contract surface** from **plugin runtime policy behavior**." User explicitly framed it as "supporting environment evidence, not as proof that Candidate A works."

First attempt: `codex app-server generate-json-schema > .tmp/app-server-schema-pre-candidate-a.txt`. Errored — the command requires `--out <DIR>`, not stdout. Trashed the bad file (using `trash`, not `rm`, per global CLAUDE.md), checked the help, ran with `--out .tmp/app-server-schema-pre-candidate-a/` (default mode, no `--experimental` — single capture aligned to user's "schema/contract truth" framing). Generated 35 top-level Params/Response files + `v1/` (8 KB) + `v2/` (1.6 MB, 192 files); ~2.5 MB total.

Sanity-checked the bundle: `ExecCommandApprovalParams.json` parses with expected JSON Schema top-level keys; grepped for S7-relevant fields. Found `proposedExecpolicyAmendment` in `CommandExecutionRequestApprovalParams.json` + `ServerRequest.json` + umbrella; `acceptWithExecpolicyAmendment` in BOTH Params AND Response (decision branch). The schema's own field descriptions directly corroborated the S7 split: `proposedExecpolicyAmendment` is "Optional proposed execpolicy amendment to allow similar commands without prompting" (forward-looking offer = S7a definition) and `acceptWithExecpolicyAmendment` is one branch of `CommandExecutionApprovalDecision` enum, documented "User approved the command, and wants to apply the proposed execpolicy amendment so future matching commands can run without prompting" (S7b only fires when `available_decisions` is restricted to amendment-class).

Found one structural insight worth recording: plugin's snake_case `kind: command_approval` ↔ schema's CamelCase `CommandExecutionRequestApproval`; plugin `kind: file_change` ↔ schema `FileChangeRequestApproval`. Implicit name mapping at the protocol layer.

Added a single new row to Run Identity table (between `codex --version` and Raw App Server identity rows) with: capture command, mode (default), file count + size, `.tmp/`-gitignored location, 4 SHA-256 forensic anchors (umbrella + v2 umbrella + 2 S7-relevant files), explicit "Cross-variant supporting evidence only — NOT a Candidate-A gate" framing, schema-quoted S7-split corroboration, plugin↔schema name mapping. Committed `5a1e937e`.

**Third user prompt: push then apply Candidate A.** User authorized push of the 2 unpushed commits (clean phase boundary before variant patch) AND chose option (b) instrumented Candidate A patch with the explicit instruction: "Keep the instrumentation semantics-preserving: emit the policy dict, return the same policy, no extra control-flow or policy logic."

Pushed `19ed53b7..5a1e937e` to origin in parallel with reading the patch site (runtime.py:23-38) and the Baseline patch reference (.tmp/variant-baseline.patch). Mirrored Baseline's exact shape for Candidate A: rename `return {…}` → `policy = {…}`; insert 12-line file-write instrumentation block before `return policy`. Two intentional changes from Baseline pattern: (1) `False` → `True` on the `includePlatformDefaults` line (the actual Candidate A semantic flip), (2) label `[BASELINE]` → `[CANDIDATE_A]` AND log filename from `baseline-runtime-proof.log` → `candidate-a-runtime-proof.log` (distinct file prevents stale-Baseline-content contamination AND makes "did we read the right variant's evidence" trivially verifiable).

Captured `.tmp/variant-candidate-a.patch` via `git diff` (37 lines, sha256 `4df1df3999…`) and `.tmp/variant-candidate-a.applied-at` via `printf "Patch applied at: $(date -u +'%Y-%m-%dT%H:%M:%SZ')\n"` (recorded `2026-04-28T17:12:59Z`, sha256 `bf897498bb…`). Note: `date -u +FORMAT` is the SAFE recipe — only `date -u -j -f FMT INPUT +OUTFMT` is the trap (input gets relabeled as UTC). For emitting "now" there's no input parsing, so no relabel risk.

Sanity checks: AST-parsed runtime.py via `python3 -c "import ast; ast.parse(open(...).read())"` (OK; 314 total lines); `git status --short packages/plugins/codex-collaboration/` showed only runtime.py dirty; `sed -n '33p'` confirmed `"includePlatformDefaults": True,`; cross-checked patch timestamp (`2026-04-28T17:12:59Z`) against current plugin start (`2026-04-28T15:41:29Z`) — patch is 1h31m AFTER plugin start, confirming running plugin still holds clean code in memory and restart is required before execution.

A new-diagnostics reminder fired about a Pyright issue at runtime.py:282 (TurnStatus literal narrowing). Verified via memory's carry-forward register that this is RT.1 — pre-existing, not introduced by my patch (line 282 is far from edits at 23-50). Documented as a Risk in this handoff but not actionable for Candidate A.

User authorized stop: "Stop there for restart boundary and save a handoff." Invoked the `handoff:save` skill, which is producing this handoff.

## Decisions

### D1: Memory + S7 work as a single docs commit

**Choice:** `dd897c5e` covers run-record S7 narrowing only; memory file rewrite + MEMORY.md index update happen separately (outside repo, no git commit).

**Driver:** User said "Proceed with the memory correction (#6) and S7 narrowing (#7) as a single closure commit." Memory location is `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/` — outside the repo, so it can't physically be in any git commit.

**Rejected alternatives:**
- **Two separate commits (one per item)** — no atomic relationship to capture; would proliferate small commits inconsistent with project's bundled-closure pattern.
- **Defer memory edit to next session** — would leave the wrong "deny finalizes" memory active during Candidate A planning, polluting interpretation.

**Implication:** Future readers of the run record see one closure commit with the memory-side audit trail in the commit message body (Hygiene #1 cell explicitly summarizes the memory change with field-by-field detail).

**Trade-offs accepted:** Cannot `git revert` the memory side; mitigated because auto-memory has no git relationship anyway, and the commit message preserves the intent.

**Confidence:** High (E2) — verified all 7 S7 references resolve consistently post-edit; commit landed cleanly with pre-commit hook passing; AST/JSON sanity checks all green.

**Reversibility:** High — Edit reverses are trivial; commit revert is one git operation; memory file is plain markdown editable in place.

**Change trigger:** If a future audit revealed the memory file lives at a different path, OR if memory store gained git-tracked persistence semantics, the approach changes.

### D2: Capture schema bundle BEFORE Candidate A patch

**Choice:** Run `codex app-server generate-json-schema --out .tmp/app-server-schema-pre-candidate-a/` and record in run record's Run Identity table BEFORE staging the Candidate A patch.

**Driver:** User: "it is cheap, non-contaminating if you treat it as a read-only pre-variant artifact, and it gives you a stable 'tool/schema environment at Candidate A entry' record before any local patch or restart changes the runtime story. It also cleanly separates **App Server contract surface** from **plugin runtime policy behavior**, which has been a recurring distinction in this diagnostic."

**Rejected alternatives:**
- **Skip the schema dump** — minimizes pre-variant actions; user explicitly weighed and rejected this with "the only reason to skip it is if you are trying to minimize all nonessential actions before the patch. But given how much this run depends on separating schema/contract truth from runtime/process truth, I'd take the artifact now."
- **Capture AFTER Candidate A executes** — couples schema state to variant outcome, defeating the "pre-variant baseline" purpose.

**Implication:** Clean separation of contract-surface vs runtime-policy concerns. Drift in either is independently detectable (e.g., if Candidate B uses a different `codex --version` and the schema umbrella hash changes, that's a finding). Schema-level corroboration of S7 split was a serendipitous bonus.

**Trade-offs accepted:** Extra ~2-3 minute pre-variant action; user explicitly framed this as worth the cost.

**Confidence:** High (E2) — user articulated rationale + I observed the schema directly corroborates S7 split via field descriptions.

**Reversibility:** N/A — purely additive; bundle is gitignored so doesn't pollute the tree.

**Change trigger:** Never; this artifact has independent reference value across all subsequent variants.

### D3: Default-mode schema dump (no `--experimental`)

**Choice:** Capture schema bundle without `--experimental` flag.

**Driver:** User instruction was simply "Run `codex app-server generate-json-schema`" — no flag specified. Their framing "schema/contract truth" → stable surface (default) is what we want for cross-variant reference.

**Rejected alternatives:**
- **`--experimental` capture** — would conflate stable contract with experimental drift in one snapshot; harder to interpret deltas.
- **Both captures (default + experimental)** — adds capture surface area; user didn't ask for two; "less is more" applied.

**Implication:** If a future variant emits a field absent from this default-mode bundle, re-capture with `--experimental` and diff. Recorded as caveat in commit message body.

**Trade-offs accepted:** Less complete capture; `acceptWithExecpolicyAmendment` and `proposedExecpolicyAmendment` were both present in default mode anyway, so no immediate cost for the S7 corroboration use case.

**Confidence:** Medium (E1) — based on the `[experimental]` tagging in `codex app-server --help` output and the assumption that production-stable fields are in default; not directly tested by capturing both.

**Reversibility:** High — re-run with `--experimental` is one command.

**Change trigger:** Variant emits unknown field, OR user asks for the broader surface.

### D4: Candidate A patch in instrumented form (mirror Baseline shape)

**Choice:** Apply Candidate A patch with both (a) `includePlatformDefaults: False → True` flip AND (b) file-write runtime-proof emit with `[CANDIDATE_A]` label.

**Driver:** User: "Candidate A needs the same evidence layer Baseline had: not just 'disk says includePlatformDefaults: True,' but 'the running plugin process emitted a [CANDIDATE_A] policy payload from the code path under test.' Keep the instrumentation semantics-preserving: emit the policy dict, return the same policy, no extra control-flow or policy logic."

**Rejected alternatives:**
- **Minimal patch (flag flip only)** — would force interpretation of Candidate A outcome via inference rather than direct runtime-proof evidence. Like-with-like comparison vs Baseline becomes harder.
- **Different instrumentation structure** — would introduce a new variable in cross-variant comparison.

**Implication:** Parallel evidence layer to Baseline; like-with-like comparison enabled. Runtime-proof artifact will tell us *exactly* what the running process emitted, independent of disk state or schema inferences.

**Trade-offs accepted:** Instrumentation is a "patch" for capture/restore purposes (per Cross-variant checks rule's Runtime-proof-only instrumentation exception at run record line 556-562) — must be recorded in `Patch capture form` field and `Patch applied at` row, but it's NOT a behavioral patch for variant interpretation purposes (semantics-preserving file write before unchanged return).

**Confidence:** High (E2) — user explicitly authorized; mirroring Baseline pattern (which already worked end-to-end in attempt 1's evidence chain).

**Reversibility:** High — `git checkout -- packages/plugins/codex-collaboration/server/runtime.py` restores cleanly. Verified by Baseline's clean restoration at the end of prior session.

**Change trigger:** If instrumentation introduced measurable delay (very unlikely — file write is fast and bounded; first delegate call adds one syscall), revisit.

### D5: Distinct log filename for Candidate A vs Baseline

**Choice:** Write to `/tmp/codex-collab-candidate-a-runtime-proof.log` instead of reusing `baseline-runtime-proof.log`.

**Driver:** Explicit isolation principle — variant-named log files prevent any chance of stale-Baseline-content contaminating Candidate A reads, and make "did we read the right variant's evidence" trivially verifiable.

**Rejected alternatives:**
- **Reuse Baseline's filename** — Baseline's log was trashed at prior session's restoration step, but if any restoration step ever fails or partially completes, residual content could appear in a future variant's read. High contamination risk for tiny convenience gain.
- **Single shared log with all variants** — requires per-line label parsing; harder to grep.

**Implication:** Each variant has its own proof file; restoration trash list is variant-specific. Restore protocol for Candidate A: `trash /tmp/codex-collab-candidate-a-runtime-proof.log` (parallel to Baseline's `trash /tmp/codex-collab-baseline-runtime-proof.log`).

**Trade-offs accepted:** More files to track; trivial cost.

**Confidence:** High (E0+) — pure isolation principle; no empirical risk to verify against.

**Reversibility:** N/A — purely additive (each variant's log is independent).

**Change trigger:** Never; per-variant isolation is the durable pattern.

### D6: Push pre-Candidate-A docs commits before applying patch

**Choice:** Push `dd897c5e` and `5a1e937e` to origin before staging the Candidate A patch on disk.

**Driver:** User: "push now... they're complete, pre-Candidate-A evidence/cleanup commits. Pushing them now creates a clean boundary before the variant patch and avoids coupling docs/schema/S7 corrections to whatever Candidate A discovers."

**Rejected alternatives:**
- **Defer push until Candidate A complete** — couples unrelated commits to variant outcome; if Candidate A reveals new findings requiring revision of either commit, the bundled push gets messier.
- **Push only S7 commit, defer schema bundle commit** — splits artifacts that share a "pre-Candidate-A evidence" framing; user's framing pushed for atomic phase boundary.

**Implication:** Clean phase boundary established. If Candidate A fails or pivots, both docs commits remain valid independent record. Branch is now in sync with origin at `5a1e937e` — next push will start fresh from runtime.py restoration + run-record updates.

**Trade-offs accepted:** More push events; trivial cost.

**Confidence:** High (E2) — user's "Push at clean phase boundaries" preference (carried from prior sessions) + repository's branch-protection model favors small clean pushes.

**Reversibility:** Standard revert-via-revert-commit; pushed history doesn't get rewritten.

**Change trigger:** Never; phase-boundary push is the durable pattern.

## Changes

### Commits this session (both pushed)

| Commit | Subject | Diff stat | Pushed |
|---|---|---|---|
| `dd897c5e` | docs(delegate): split S7 attribution into S7a/S7b; close hygiene #1 + #5 | +12 / -9 lines on run record | YES (this session) |
| `5a1e937e` | docs(delegate): capture pre-Candidate-A App Server schema bundle | +1 line on run record (Run Identity row) | YES (this session) |

Branch is **in sync with origin** at `5a1e937e`. Push event: `19ed53b7..5a1e937e  feature/delegate-execution-diagnostic-record -> feature/delegate-execution-diagnostic-record`.

### `packages/plugins/codex-collaboration/server/runtime.py` — Candidate A patch staged on disk (NOT committed)

**Purpose:** Apply Candidate A semantic change (`includePlatformDefaults: True`) with parallel-to-Baseline runtime-proof instrumentation.

**Approach:** Mirror Baseline's exact patch shape — rename `return {…}` to `policy = {…}` so the dict can be referenced both for emit and for return. Insert 12-line file-write block between dict construction and return: imports `datetime`/`Path` inline (semantics-preserving — no module-level dependency added), opens `/tmp/codex-collab-candidate-a-runtime-proof.log` in append mode, writes `<iso-utc> [CANDIDATE_A] sandboxPolicy=<repr>\n`. Returns the same `policy` dict that was emitted (zero behavioral divergence between emit and return).

**Key implementation details:**
- Line 33: `"includePlatformDefaults": True,` (the semantic flip — was `False` in HEAD)
- Lines 38-49: instrumentation block (parallel structure to Baseline's lines 38-49; only label and filename differ)
- Comment marker: `# variant instrumentation (remove after diagnostic)` — preserved verbatim from Baseline pattern; serves as cleanup marker
- Restoration recipe: `git checkout -- packages/plugins/codex-collaboration/server/runtime.py` (verified to work cleanly via Baseline's restoration in prior session)

**Future-Claude note:** This is the ONLY runtime.py change. AST parses (`python3 -c "import ast; ast.parse(open(...).read())"` returns OK). Total file is 314 lines post-patch. The Pyright finding at line 282 (TurnStatus literal narrowing) is pre-existing carry-forward RT.1, NOT introduced by this patch — see Risks.

### `.tmp/variant-candidate-a.patch` — patch capture (gitignored)

**Purpose:** Forensic record of the exact Candidate A patch applied this session.

**Approach:** `git diff packages/plugins/codex-collaboration/server/runtime.py > .tmp/variant-candidate-a.patch`.

**Key details:**
- 37 lines unified-diff format
- SHA-256: `4df1df3999b4914978fb0cf7582418cfd65377f36e4e45942983191d75fa2bf8`
- Contains the flag flip (`-False` → `+True`) and the 12-line instrumentation insertion
- Preserves blob hashes (`9f28e0b0..95a98ab9`) so future re-apply is verifiable

### `.tmp/variant-candidate-a.applied-at` — patch timestamp (gitignored)

**Purpose:** Record exact UTC instant when patch hit disk, for cross-checking against post-restart plugin start UTC.

**Approach:** `printf "Patch applied at: %s\n" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" > .tmp/variant-candidate-a.applied-at`.

**Key details:**
- Value: `Patch applied at: 2026-04-28T17:12:59Z`
- SHA-256: `bf897498bb2fa7159fcb1b33e7d75e79a2817f786acbc2ae77eb8d2be1baf9cb`
- Recipe note: `date -u +FORMAT` is SAFE for emitting "now" in UTC. The trap recipe `date -u -j -f FMT INPUT +OUTFMT` (which silently relabels local-tz input as UTC) only applies when parsing input. No input parsing here → no relabel risk.

### `.tmp/app-server-schema-pre-candidate-a/` — schema bundle (gitignored)

**Purpose:** Read-only pre-variant snapshot of the App Server contract surface. Independent reference for cross-variant interpretation.

**Approach:** `codex app-server generate-json-schema --out .tmp/app-server-schema-pre-candidate-a/`. Default mode (no `--experimental`).

**Key details:**
- 35 top-level Params/Response files + `v1/` (8 KB, 2 files) + `v2/` (1.6 MB, 192 files)
- Total: ~2.5 MB
- SHA-256 forensic anchors recorded in run record's Run Identity row:
  - umbrella `codex_app_server_protocol.schemas.json`: `d12aeef8eb…`
  - v2 umbrella `codex_app_server_protocol.v2.schemas.json`: `0e72877f63…`
  - S7 request `CommandExecutionRequestApprovalParams.json`: `dc3251a5dc…`
  - S7 response `CommandExecutionRequestApprovalResponse.json`: `42010a48dd…`
- Reproducibility: same `codex --version` (`codex-cli 0.125.0`) + same command should yield matching hashes; divergence is itself a finding

## Codebase Knowledge

### Files read this session and what they yielded

| File | Why read | Understanding gained |
|---|---|---|
| `packages/plugins/codex-collaboration/server/runtime.py` (lines 1-60) | Identify the Candidate A patch site | `build_workspace_write_sandbox_policy` at lines 23-38; returns the v1 execution policy dict; `readOnlyAccess.includePlatformDefaults` at line 33 is the Candidate A flip target |
| `.tmp/variant-baseline.patch` (32 lines) | Reference for Candidate A's instrumentation shape | Pattern: rename `return {…}` → `policy = {…}`; insert 12-line file-write block; return `policy` |
| `.tmp/variant-baseline.applied-at` | Cross-check Baseline's timestamp pattern | Format: `Patch applied at: <iso-utc>`; Baseline's was `2026-04-28T06:56:55Z` |
| `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` (multiple sections) | Locate every S7 reference for the split | 5 touchpoints: lines 877, 893+897, 915, 919, 933; plus structure of Run Identity (52-65), Per-Variant Evidence template (566+), Cross-variant checks (552-564) |
| `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_deny_finalizes_job.md` | Source for memory rewrite | 12-line file with frontmatter + Why + How-to-apply structure; pre-correction text |
| `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/MEMORY.md` (line 88) | Source for index entry update | Single-line index hook |
| `.tmp/app-server-schema-pre-candidate-a/ExecCommandApprovalParams.json` | Validate JSON parses; sanity-check structure | Top-level keys `['$schema','title','type','required','properties','definitions']` — standard JSON Schema |
| `.tmp/app-server-schema-pre-candidate-a/CommandExecutionRequestApprovalParams.json` | Confirm `proposedExecpolicyAmendment` shape | "Optional proposed execpolicy amendment to allow similar commands without prompting." Type: `array \| null`. **S7a definition in schema's own vocabulary.** |
| `.tmp/app-server-schema-pre-candidate-a/CommandExecutionRequestApprovalResponse.json` | Confirm `acceptWithExecpolicyAmendment` shape | One branch of `CommandExecutionApprovalDecision` enum (definition list). **S7b definition in schema's own vocabulary.** |
| `packages/plugins/handoff/skills/save/synthesis-guide.md` | Required reading per save skill | Synthesis prompts and depth targets |
| `packages/plugins/handoff/references/format-reference.md` | Section checklist + frontmatter schema | All 13 required sections; depth targets |
| `packages/plugins/handoff/references/handoff-contract.md` | Chain protocol + state file mechanics | resumed_from path lookup; trash state file after save |

### Architecture: process chain + data layout

| Layer | Location | Purpose |
|---|---|---|
| Sandbox policy builder (post-patch) | `packages/plugins/codex-collaboration/server/runtime.py:23-50` | Builds `workspaceWrite` policy dict; emits to file for proof; returns dict |
| Plugin process chain (this session) | `claude (PID 7116)` → `uv (PID 7163)` → `python (PID 7165)` | Three-layer codex-collaboration plugin process tree |
| Plugin data root | `~/.claude/plugins/data/codex-collaboration-inline/` | Per-session JSONL stores; per-job worktrees; cross-session audit |
| Plugin session marker | `<plugin-data-root>/session_id` | Currently `801b6646-…` matching THIS session |
| App Server contract source | `codex CLI 0.125.0` invoked via `codex app-server generate-json-schema --out` | Emits 35 top-level + 192 v2 schema files |

### Patterns identified

- **Variant patch shape:** `policy = {…}; <file-write emit>; return policy` (semantics-preserving — emit captures exactly what gets returned, no mutation between emit and return). See `runtime.py:23-50` post-patch and `.tmp/variant-baseline.patch` for the template.
- **Patch capture pattern:** `git diff <path> > .tmp/variant-<name>.patch` + `printf "Patch applied at: %s\n" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" > .tmp/variant-<name>.applied-at`. Both gitignored under `.tmp/`.
- **Restoration recipe:** `git checkout -- <file>` + `trash /tmp/codex-collab-<variant>-runtime-proof.log` after variant complete. Verified clean by Baseline's prior session.
- **Self-documenting cleanup marker:** `# variant instrumentation (remove after diagnostic)` — preserved across variants; survives as a grep target for future audit.
- **Plugin↔schema name mapping:** Plugin uses snake_case `kind: command_approval` / `file_change`; App Server schema uses CamelCase `CommandExecutionRequestApproval` / `FileChangeRequestApproval`. Implicit at protocol layer; documented in run record's Run Identity row.
- **Closure batches via /copy-routed scrutiny:** User routes Codex consultations through structured /copy reasoning, then Claude implements verbatim. Three rounds this session: pre-flight resumption, schema-dump capture choice, push+patch sequencing.

### Conventions observed

- Patch files live at `.tmp/variant-<name>.patch` (gitignored). Per-variant naming with explicit name-in-file (e.g., `[CANDIDATE_A]` label) ensures cross-variant attribution is unambiguous.
- Runtime-proof log files at `/tmp/codex-collab-<variant>-runtime-proof.log` (per-variant; isolated).
- Run record commits use `docs(delegate): <subject>` Conventional Commits prefix; subject line ≤ ~75 chars; verbose body with numbered items + diff stat at end.
- Hygiene action items get marked `**DONE this session**` rather than deleted, preserving the original action description for audit trail.
- Forensic SHA-256 anchors recorded for any artifact that's gitignored but referentially important (schema bundle umbrella, patch files, applied-at files).

### Surprising findings

- **`pgrep -fa <pattern>` matches its own argv.** PIDs `10668`/`11657` looked like phantom plugin processes from prior session. They were pgrep itself or its parent shell on each call (the pattern string appears in the cmdline at runtime). Real plugin chain is parent-PID-rooted: `7116→7163→7165`.
- **`codex app-server generate-json-schema` requires `--out <DIR>`, not stdout.** First attempt without flag errored with exit code 2. Output is a directory tree, not a single file.
- **Schema's own field descriptions corroborate the S7 split semantically.** Not just "the field exists" — the schema literally documents `proposedExecpolicyAmendment` as "Optional proposed... allow similar commands without prompting" (forward-looking offer = S7a) and `acceptWithExecpolicyAmendment` as a decision branch among multiple (S7b only when restricted). Schema-level corroboration validates runtime classification independently.
- **macOS `date -u +FORMAT` is SAFE** (no `-j -f`, so no input parsing, so no relabel risk). The Per-Variant Evidence template's corrected recipe is for *parsing* `lstart` strings, where `date -u -j -f FMT INPUT +OUTFMT` is the trap. Worth distinguishing in template guidance: parsing recipes have the trap; emission recipes don't.

### Key locations

| Concept | Location |
|---|---|
| Sandbox policy build site (post-patch) | `packages/plugins/codex-collaboration/server/runtime.py:23-50` |
| Run record (live HEAD: `5a1e937e` includes schema row + S7 split) | `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` |
| Symptom Attribution rows S7a/S7b | run record lines 935-936 |
| Branch Precedence rule 1.d (S7b reference) | run record line 877 |
| Branch Precedence rule 4 (Amendment required → S7b) | run record lines 893-897 |
| Branch decision narrative (S7a/S7b for Baseline) | run record line 917 |
| Hygiene next action (#1 + #5 marked DONE) | run record line 921 |
| Run Identity (schema bundle row) | run record lines 52-65; new row at 62 |
| Per-Variant Evidence template (with corrected macOS recipe) | run record line 566+ |
| Cross-variant checks (Runtime-proof-only instrumentation exception) | run record lines 552-564 |
| Schema bundle | `.tmp/app-server-schema-pre-candidate-a/` (gitignored) |
| Candidate A patch capture | `.tmp/variant-candidate-a.patch` |
| Candidate A applied-at | `.tmp/variant-candidate-a.applied-at` |
| Memory file (corrected) | `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_deny_finalizes_job.md` |
| MEMORY.md index entry | `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/MEMORY.md:88` |

## Context

### Project State

| Item | State |
|---|---|
| Branch | `feature/delegate-execution-diagnostic-record` at `5a1e937e` (in sync with origin — pushed this session) |
| Run record | Live HEAD includes S7 split + schema bundle row |
| Run Identity table | Frozen at `49d93001` per two-layer pattern; live drift to `5a1e937e` |
| Sandbox blocker (Baseline) | Confirmed live S1 primary; S7a fired informationally; S7b did NOT fire |
| Plugin process (this session) | PIDs `7116`/`7163`/`7165`; in-memory code is CLEAN (Baseline-restored state); started `2026-04-28T15:41:29Z` UTC |
| Candidate A patch on disk | STAGED (runtime.py modified; AST parses; git status shows ` M packages/plugins/codex-collaboration/server/runtime.py`) |
| Patch applied at | `2026-04-28T17:12:59Z` (1h31m AFTER plugin start → restart REQUIRED) |
| Working tree | Dirty: runtime.py (Candidate A) + 8 carry-forward `docs/tickets/closed-tickets/` moves (unrelated) |
| Schema bundle | Captured at `.tmp/app-server-schema-pre-candidate-a/` (gitignored) |
| Pushed to origin? | YES — `19ed53b7..5a1e937e` pushed this session |

### Mental Model

**Variant comparison via instrumented evidence.** Baseline established the pattern: file-write the actual policy dict from the build site, restore after, interpret the runtime-proof artifact alongside the JSONL store inspections. Candidate A mirrors with `[CANDIDATE_A]` label and distinct log file. The flag flip (`includePlatformDefaults: False → True`) is the *only* policy-behavior change between Baseline and Candidate A; instrumentation is identical structure with different label/filename to ensure semantics-preserving comparison.

**Three independent UTC sources** will cross-check Candidate A (per Baseline's pattern):
1. Patch applied at: `2026-04-28T17:12:59Z` (this session)
2. Plugin start (post-restart): TBD next session — must be > patch applied
3. Runtime-proof emit (Python `datetime.now(timezone.utc)`): TBD on first delegate call

If any of these three disagree on relative ordering, that's a signal of either a recipe error or a lifecycle anomaly worth investigating.

**Schema bundle is environmental, not variant-coupled.** Same `codex --version` produces same hashes — bundle characterizes "what App Server contract is in scope at Candidate A entry," not "what Candidate A does." If Candidate B uses the same Codex version, bundle is reusable; if Codex is upgraded, re-capture and diff.

### Environment

- Working tree: `feature/delegate-execution-diagnostic-record` at `5a1e937e` (in sync with origin)
- Codex: `codex-cli 0.125.0`
- Local timezone: `EDT (-0400)`. Pitfall: macOS `date -u -j -f FMT INPUT +OUTFMT` (parsing-only). Safe: `date -u +FORMAT` (emission-only).
- Plugin process: PIDs `7116/7163/7165`; started `2026-04-28T15:41:29Z` UTC. In-memory code is CLEAN (Baseline-restored state).
- Plugin data root: `~/.claude/plugins/data/codex-collaboration-inline/`
- Plugin's current session_id: `801b6646-171e-4a80-a647-c9de35041d4c` (matches THIS session)
- macOS Darwin 25.4.0; shell zsh

## Learnings

### Schema-level corroboration is the strongest evidence form for protocol-derived classifications

**Mechanism:** The S7 split (S7a payload-presence informational; S7b response-required classification-driving) was originally derived from runtime payload analysis (PendingRequestStore inspection of Baseline attempt 1). The schema dump showed the schema's own field descriptions use the same semantic distinction independently:
- `proposedExecpolicyAmendment` description: "Optional proposed execpolicy amendment to allow similar commands without prompting" — forward-looking *offer* (S7a)
- `acceptWithExecpolicyAmendment` description: "User approved the command, and wants to apply the proposed execpolicy amendment so future matching commands can run without prompting" — one branch of `CommandExecutionApprovalDecision` enum (S7b only when restricted)

**Evidence:** Verified by direct `python3 json.load` + regex extraction across the schema bundle. Both descriptions align with the S7a/S7b semantics derived runtime-only.

**Implication:** When a runtime-derived classification can be cross-validated against the schema/contract surface, prefer two-source evidence over one-source. Future variants can use the same schema-bundle approach to validate their interpretations.

**Watch for:** Schema descriptions are authored by humans (potentially out of sync with implementation behavior). Schema-level corroboration is a strong signal but not absolute proof; runtime-level evidence is still load-bearing.

### Patch-capture timestamps must use the SAFE date recipe

**Mechanism:** macOS `date -u -j -f FMT INPUT +OUTFMT` silently relabels local-tz input as UTC (the trap that produced the 4-hour error fixed in commit `c704eafa`). But `date -u +FORMAT` (no `-j -f`, no input parsing) is safe — it's emitting "now" in UTC with no input to misinterpret.

**Evidence:** Used `date -u +'%Y-%m-%dT%H:%M:%SZ'` for Candidate A's applied-at; cross-checked against shell `$(date -u +'%Y-%m-%dT%H:%M:%SZ')` invocation showing same value `2026-04-28T17:12:59Z`. No anomaly.

**Implication:** Worth distinguishing in the Per-Variant Evidence template: parsing recipes have the trap (need epoch round-trip); emission recipes don't (single `date -u +FORMAT` is correct). Currently the template documents the parsing trap; could add a "Safe emission" note for completeness.

**Watch for:** Any future need to *parse* a timestamp — that's where the trap returns. Always use epoch round-trip when input parsing is involved.

### Pyright diagnostics surfacing far from edited code are usually pre-existing

**Mechanism:** Pyright runs full-file analysis on edits. A finding at line 282 when you edited lines 23-50 is likely a pre-existing issue Pyright surfaces every time the file is touched.

**Evidence:** New-diagnostics reminder fired about `runtime.py:282 TurnStatus literal narrowing` after the Candidate A patch at lines 23-50. Verified via memory's carry-forward register: this is RT.1, pre-existing, not Packet 1-introduced (and certainly not Candidate-A-introduced). Line 282 is 230+ lines from my edit site.

**Implication:** Before assuming new Pyright findings are caused by current edits, check carry-forward registers and compare line numbers to your edit. Distance > 50 lines is a strong signal it's pre-existing.

**Watch for:** If a future variant patch DID introduce a typing issue (e.g., changed a return type), distance heuristic alone isn't enough — also check whether the finding's specific failure mode could be caused by your change.

### `pgrep -fa <pattern>` matches its own argv

**Mechanism:** With `-f`, pgrep matches against full command line. The pattern itself appears in pgrep's own argv at runtime, so pgrep can match itself unless it explicitly excludes its own PID.

**Evidence:** Two `pgrep -fa "uv run.*codex-collaboration"` calls returned different transient PIDs (`10668` then `11657`) alongside the persistent `7163`. PID `10668` was not present in subsequent `ps -p` lookup, confirming transient.

**Implication:** Robust process discovery uses parent-PID lineage (`pgrep -P <ppid>`) or filename-based matching (`pgrep -x <name>`) rather than pattern matching against full cmdline. If you must use `-f`, filter via `| grep -v $$` or `| awk '$1 != PROCINFO["pid"]'`.

**Watch for:** Any process-discovery automation that uses pattern matching — phantom matches will pollute the result.

## Next Steps

### 1. Operator: restart Claude Code

**Acceptance criteria post-restart:**
- New plugin PIDs differ from `7116`/`7163`/`7165`
- Plugin process start UTC > `2026-04-28T17:12:59Z` (Candidate A patch applied at)
- `git diff packages/plugins/codex-collaboration/server/runtime.py` shows Candidate A patch on disk (NOT empty — patch must still be there)
- `git status --short` shows `M packages/plugins/codex-collaboration/server/runtime.py` + 8 carry-forward ticket-file moves

### 2. New session: `/handoff:load`

Picks up THIS handoff and archives it. Auto-resolves session continuity.

### 3. New session: pre-flight verification

Run in parallel:
- `ps -ef | grep codex-collaboration | grep -v grep` — verify new PIDs
- `git diff packages/plugins/codex-collaboration/server/runtime.py | wc -l` — should be ~37 (Candidate A patch present)
- `cat .tmp/variant-candidate-a.applied-at` — verify timestamp `2026-04-28T17:12:59Z`
- `shasum -a 256 .tmp/variant-candidate-a.patch` — verify hash `4df1df3999b4914978fb0cf7582418cfd65377f36e4e45942983191d75fa2bf8`
- `cat ~/.claude/plugins/data/codex-collaboration-inline/session_id` — verify session id flipped to new UUID
- Plugin start UTC: derive from `ps -o lstart` via the SAFE epoch round-trip recipe (Per-Variant Evidence template line ~582). Cross-check that start UTC > patch applied UTC.
- `ls /tmp/codex-collab-candidate-a-runtime-proof.log` — should NOT exist yet (first execution will create it)

### 4. New session: instantiate `### Variant: Candidate A (attempt 1)` block

Copy from Per-Variant Evidence template (run record line 566+). Use the corrected macOS date recipe (epoch round-trip — for `lstart` parsing). Cross-check plugin start UTC against runtime-proof emit's `datetime.now(timezone.utc)` source after first delegate call. Cell-by-cell: Operator/Date/Branch/Patch capture form/Patch applied at/Plugin process start timestamp/Restart performed/Pre-restart sandbox snapshot/Pre-run HEAD/Smoke objective/Approval policy value/etc.

### 5. New session: invoke `codex_delegate_start` with smoke

Reuse Baseline smoke timestamp `20260428T005625` for cross-variant correlation (or generate a new one — both choices work; Baseline reuse maximizes correlation, new timestamp maximizes independence). Capture transitions via `codex_delegate_poll`.

**Hypothesis (expected outcome):** shell unblocked. Delegate executes the chained `mkdir`/`printf`/`cat` sequence without parking on `command_approval`. Smoke artifact created. S1 stops firing.

**Falsification (alternative outcome):** shell still blocked. Smoke artifact NOT created. S1 still primary. Indicates platform-defaults grant insufficient — escalates to Candidate B matrix exploration.

### 6. New session: capture runtime-proof + interpret outcome

Read `/tmp/codex-collab-candidate-a-runtime-proof.log`. Verify `[CANDIDATE_A] sandboxPolicy={…}` payload shows `includePlatformDefaults: True`. Cross-check audit row timestamp (`audit/events.jsonl`) against runtime-proof emit's UTC for sub-second alignment (per Baseline's cross-check pattern).

### 7. New session: restoration + commit

- `git checkout -- packages/plugins/codex-collaboration/server/runtime.py`
- `trash /tmp/codex-collab-candidate-a-runtime-proof.log`
- Verify clean: `git status --short` should show only the 8 carry-forward ticket-file moves
- Commit run-record updates: `docs(delegate): capture Candidate A attempt 1 evidence + restoration on T-01 run record`

### 8. Carry-forward Baseline hygiene items (non-blocking, deferred)

| # | Item | Status |
|---|---|---|
| 2 | Optional follow-up issue on delegate's autopilot toward `.codex-collaboration/test-results.json` | Open |
| 3 | Audit prior session's handoff for the macOS `date -u -j -f` pitfall | Open |
| 4 | Open question on `available_decisions: []` in null-scope `file_change` | Open |

## In Progress

**Clean stopping point at restart boundary.** No work in flight.

- Disk holds Candidate A patch (`runtime.py` modified)
- Running plugin holds CLEAN code in memory (Baseline-restored state from prior session)
- 2 docs commits this session, both pushed (`dd897c5e`, `5a1e937e`)
- Restoration of Candidate A patch is deferred to AFTER variant execution per Baseline pattern
- Working tree dirty only on runtime.py (Candidate A) + 8 carry-forward ticket-file moves

## Open Questions

- **Will `includePlatformDefaults: True` actually unblock `/bin/zsh`?** Pending Candidate A execution next session.
- **If S1 still fires under Candidate A, does the policy patch reach the App Server with the True flag, or does the App Server interpret `includePlatformDefaults: True` differently than expected?** Runtime-proof artifact will resolve — if log shows `True` but parked `command_approval` still appears, App Server is interpreting the flag as not-grant rather than grant.
- **Will delegate's `test-results.json` autopilot recur in Candidate A?** If it does and `shell_action_count >= 3`, ratio interpretation comes back into play (per Branch Precedence #1.d). Carry-forward.
- **Will any new Symptom row fire that wasn't seen in Baseline?** Particularly: S2 (slow worker), S3 (capture-ready regression), S4-S6 (registry/dispatch), S7b (true response-required amendment). Candidate A will produce its own Branch decision adjudication.
- **Is the `acceptWithExecpolicyAmendment` field still offered (S7a) but not required (S7b not fired) under Candidate A's narrower-grant?** Likely yes (S7a is universal under `untrusted` mode), but worth verifying in Candidate A's PendingRequestStore inspection.

## Risks

### Operator forgets to restart Claude Code

**Concern:** Same as Baseline's risk. Running plugin holds CLEAN code; new Candidate A patch on disk wouldn't be observed by execution. Variant attempt 1 would actually re-run Baseline behavior, polluting cross-variant interpretation.

**Mitigation:** Pre-flight in next session checks PID difference + plugin start UTC > patch applied UTC. Both checks would catch a missed restart.

### Patch on disk gets accidentally restored before execution

**Concern:** If someone runs `git checkout -- runtime.py`, `git stash apply`, or similar by reflex before next session executes the variant, Candidate A is lost on disk. Running plugin would still hold clean code (post-restart-with-stale-disk would be back to Baseline).

**Mitigation:** `.tmp/variant-candidate-a.patch` is gitignored but preserved (sha256 `4df1df3999…`). Re-apply via `git apply .tmp/variant-candidate-a.patch` if needed. Pre-flight in next session also verifies patch is still on disk.

### Runtime-proof file has stale content from a prior Candidate A run

**Concern:** First execution will append to `/tmp/codex-collab-candidate-a-runtime-proof.log`. Future re-runs accumulate without overwriting. Could conflate attempts.

**Mitigation:** For attempt 1, the file shouldn't exist yet (this is the first Candidate A patch ever). Pre-execution check: `ls /tmp/codex-collab-candidate-a-runtime-proof.log 2>/dev/null` should return nothing. If present (defensive), `trash` before execution.

### Pyright RT.1 (line 282 TurnStatus literal narrowing) might be re-triggered by future variant patches

**Concern:** Pre-existing per MEMORY.md carry-forward register; surfaces on every runtime.py edit because Pyright runs full-file analysis. Could be mistaken for a Candidate-A-introduced regression.

**Mitigation:** Check carry-forward register before assuming new Pyright findings are caused by current edits. RT.1 is documented as pre-existing; ignore for variant work.

### Schema bundle becomes stale if codex CLI is upgraded mid-variant-cycle

**Concern:** Bundle was captured at `codex-cli 0.125.0`. If user updates codex between sessions, the contract surface this bundle characterizes no longer matches the runtime.

**Mitigation:** Run record's Run Identity row records `codex --version` at capture time. Pre-flight in next session re-runs `codex --version` and confirms match. If mismatch, re-capture bundle and update Run Identity row.

### S7a "informational" status could erode if `untrusted`-mode behavior changes

**Concern:** S7a's "always fires under `untrusted`" classification depends on `proposedExecpolicyAmendment` being universally populated in `command_approval` requests. If a future Codex version changes this (e.g., omits the field when no amendment is plausible), S7a becomes more meaningful and should be re-classified.

**Mitigation:** Per-variant inspection of `proposedExecpolicyAmendment` presence vs context will surface drift. Run record's Hygiene action #5 marks S7 split as DONE for this version — re-evaluate per major Codex version.

## References

### Files

- `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — run record (HEAD: `5a1e937e`)
- `packages/plugins/codex-collaboration/server/runtime.py` — patched on disk (Candidate A staged, NOT committed)
- `.tmp/variant-candidate-a.patch` — patch capture (sha256 `4df1df3999b4914978fb0cf7582418cfd65377f36e4e45942983191d75fa2bf8`)
- `.tmp/variant-candidate-a.applied-at` — `2026-04-28T17:12:59Z` (sha256 `bf897498bb2fa7159fcb1b33e7d75e79a2817f786acbc2ae77eb8d2be1baf9cb`)
- `.tmp/app-server-schema-pre-candidate-a/` — schema bundle (gitignored; umbrella sha256 `d12aeef8eb…`)
- `.tmp/variant-baseline.patch` — Baseline reference (preserved)
- `.tmp/variant-baseline.applied-at` — Baseline timestamp `2026-04-28T06:56:55Z` (preserved)
- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_deny_finalizes_job.md` — corrected memory
- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/MEMORY.md` — index updated at line 88

### Code references (verified this session)

- Sandbox policy builder (post-patch): `packages/plugins/codex-collaboration/server/runtime.py:23-50` (was 23-38 pre-patch)
- Plugin data root: `~/.claude/plugins/data/codex-collaboration-inline/`
- Plugin's session id file: `<plugin-data-root>/session_id` (now `801b6646-…`)

### MCP tool calls this session

| Tool | Purpose | Outcome |
|---|---|---|
| `Skill: handoff:load` | Resume from 12-35 handoff | Archived prior handoff; state file written |
| `Skill: handoff:save` | Save this handoff | In progress (this is the output) |

### Bash invocations of note

- `codex --version` → `codex-cli 0.125.0`
- `codex app-server generate-json-schema --out .tmp/app-server-schema-pre-candidate-a/` → 35 top-level + v1/ + v2/ files
- `codex app-server generate-json-schema` (without --out) → exit code 2; required `--out <DIR>`
- `git push origin feature/delegate-execution-diagnostic-record` → `19ed53b7..5a1e937e` pushed
- `git diff packages/plugins/codex-collaboration/server/runtime.py > .tmp/variant-candidate-a.patch` → 37-line patch
- `python3 -c "import ast; ast.parse(open('runtime.py').read())"` → OK; 314 lines

### Commits this session

| Commit | Subject | Pushed |
|---|---|---|
| `dd897c5e` | docs(delegate): split S7 attribution into S7a/S7b; close hygiene #1 + #5 | YES |
| `5a1e937e` | docs(delegate): capture pre-Candidate-A App Server schema bundle | YES |

### Branches

- `feature/delegate-execution-diagnostic-record` at `5a1e937e` (in sync with origin)

### Forensic anchors (SHA-256)

| Artifact | Hash |
|---|---|
| `.tmp/variant-candidate-a.patch` | `4df1df3999b4914978fb0cf7582418cfd65377f36e4e45942983191d75fa2bf8` |
| `.tmp/variant-candidate-a.applied-at` | `bf897498bb2fa7159fcb1b33e7d75e79a2817f786acbc2ae77eb8d2be1baf9cb` |
| Schema umbrella `codex_app_server_protocol.schemas.json` | `d12aeef8eb…` (full hash in run record Run Identity row) |
| Schema v2 umbrella | `0e72877f63…` |
| Schema S7 request file | `dc3251a5dc…` |
| Schema S7 response file | `42010a48dd…` |

## Gotchas

### Plugin process holds CLEAN code in memory; disk holds Candidate A patch

(Inverse of Baseline mid-state.) After restart, plugin re-imports patched code (Candidate A semantics + instrumentation). Pre-flight verification post-restart is mandatory.

### `pgrep -fa <pattern>` matches its own argv

(Discovered this session.) PIDs that appear in `pgrep -fa` but not in `ps -ef | grep` are usually pgrep itself or its parent shell (the pattern string appears in cmdline at runtime). Don't confuse for stale plugin processes.

### `codex app-server generate-json-schema` writes to a directory, not stdout

(Discovered this session.) Required flag: `--out <DIR>`. First attempt without `--out` errors with exit code 2.

### macOS `date` has TWO recipes — use the right one

- **EMISSION** (now → UTC string): `date -u +'%Y-%m-%dT%H:%M:%SZ'` — SAFE, no input parsing.
- **PARSING** (lstart string → UTC string): `EPOCH=$(date -j -f FMT INPUT +%s); date -u -r "$EPOCH" +"%Y-%m-%dT%H:%M:%SZ"` — SAFE, two-step round-trip.
- **TRAP**: `date -u -j -f FMT INPUT +"%Y-%m-%dT%H:%M:%SZ"` — silently relabels local-tz input as UTC; produced the 4-hour error fixed in commit `c704eafa`.

### `available_decisions: []` for null-scope `file_change` (carried)

Open question. If Candidate A surfaces a similar request, deny by default unless protocol shape is clarified.

### Each variant cycle is ~10 minutes minimum

Apply patch → operator restarts Claude Code → new session executes → restore → commit run-record. Plan accordingly. Consider scheduling variant cycles in dedicated sessions rather than back-to-back within one.

### Carry-forward Pyright RT.1 (runtime.py:282 TurnStatus literal narrowing)

Pre-existing; surfaces on every runtime.py edit. Not caused by Candidate A patch. Don't mistake for Candidate-A-introduced regression.

### Run Identity drift

Run Identity table records `49d93001` (frozen). Live HEAD now `5a1e937e`. Drift of 11 commits expected by design.

### Two-clock-domain cross-check (carried, applied this session)

For Candidate A, three independent UTC sources will be cross-checked:
- Patch applied at: `2026-04-28T17:12:59Z`
- Plugin start (post-restart): TBD next session
- Runtime-proof emit (`datetime.now(timezone.utc)`): TBD on first delegate call

If any disagree on relative ordering, that's a signal of recipe error or lifecycle anomaly.

## User Preferences

(Carried from prior sessions, applied this session — verbatim quotes from earlier sessions where relevant.)

**Strict-gate before fallback investigation (carried, applied).** Pre-flight verification ran before any closure work this session.

**Two-layer HEAD anchor preserved (carried, applied).** Run Identity records `49d93001`; live HEAD drift to `5a1e937e` documented in this handoff.

**Decision fence over decision wall (carried, applied).** Three /copy-routed alignments this session: pre-flight resumption, schema-dump capture choice, push+patch sequencing.

**Push at clean phase boundaries (carried, applied).** Pushed `19ed53b7..5a1e937e` after schema bundle capture, before Candidate A patch on disk.

**Handle commits proactively (carried, applied).** Committed `dd897c5e` and `5a1e937e` without re-asking; both were complete buildable docs chunks.

**Record operational findings in durable artifacts before handoff (carried, applied).** S7 split + memory correction + schema bundle row + Candidate A patch capture + applied-at — all in durable artifacts before this handoff.

**Tightening guidance via /copy-routed scrutiny (carried, applied).** User routed three rounds of structured reasoning through /copy this session; closure batches and decisions all responsive to those structured findings.

**No pending-fill execution under partial validity (carried, applied).** All pre-Candidate-A items closed (memory, S7 split, schema bundle, push, patch capture) before the patch hit disk and the restart boundary.

**Two-clock-domain cross-check (carried, codified in template).** Will be applied for Candidate A's three independent UTC sources next session.

**Fix templates, not just instances (carried, applied).** S7 split applies to all variants going forward (template-level fix, not per-cell).

**Closure vs richness as distinct evidence states (carried, applied).** Schema bundle alone wasn't closure — the Run Identity row + corroboration narrative IS closure for the schema-dump artifact.

(New this session — verbatim user quotes:)

**Capture cheap read-only artifacts pre-variant.**
> "it is cheap, non-contaminating if you treat it as a read-only pre-variant artifact, and it gives you a stable 'tool/schema environment at Candidate A entry' record before any local patch or restart changes the runtime story."

The schema bundle is the exemplar. Future variants may have similar pre-variant supporting captures (e.g., codex config dump, plugin JSONL pre-state snapshot).

**Variant patches mirror Baseline shape exactly with label-only changes.**
> "Candidate A needs the same evidence layer Baseline had: not just 'disk says includePlatformDefaults: True,' but 'the running plugin process emitted a [CANDIDATE_A] policy payload from the code path under test.' Keep the instrumentation semantics-preserving: emit the policy dict, return the same policy, no extra control-flow or policy logic."

Apply to Candidate B and beyond: preserve the `policy = {…}; <emit>; return policy` shape; only the policy-flag change and the variant label/filename should differ.

**Push timing at phase boundaries (reaffirmed this session).**
> "push now... they're complete, pre-Candidate-A evidence/cleanup commits. Pushing them now creates a clean boundary before the variant patch and avoids coupling docs/schema/S7 corrections to whatever Candidate A discovers."

## Conversation Highlights

**User on schema-dump rationale (full structured reasoning):**
> "Capture it first. Rationale: it is cheap, non-contaminating if you treat it as a read-only pre-variant artifact, and it gives you a stable 'tool/schema environment at Candidate A entry' record before any local patch or restart changes the runtime story. It also cleanly separates **App Server contract surface** from **plugin runtime policy behavior**, which has been a recurring distinction in this diagnostic. … The only reason to skip it is if you are trying to minimize all nonessential actions before the patch. But given how much this run depends on separating schema/contract truth from runtime/process truth, I'd take the artifact now."

This drove D2 and D3.

**User on Candidate A patch shape (drove D4):**
> "For patch shape, choose **(b) instrumented**. Candidate A needs the same evidence layer Baseline had: not just 'disk says `includePlatformDefaults: True`,' but 'the running plugin process emitted a `[CANDIDATE_A]` policy payload from the code path under test.' Keep the instrumentation semantics-preserving: emit the policy dict, return the same policy, no extra control-flow or policy logic."

**User on push timing (drove D6):**
> "For push timing, also yes: **push now**. `dd897c5e` and `5a1e937e` are complete, pre-Candidate-A evidence/cleanup commits. Pushing them now creates a clean boundary before the variant patch and avoids coupling docs/schema/S7 corrections to whatever Candidate A discovers."

**User on stop point (triggered handoff save):**
> "Stop there for restart boundary and save a handoff."

**User on closure approach (carried):**
The 12-35 handoff codified "Treat closure as a contract — not an option" — applied this session: all queued items (memory, S7, schema, patch capture) closed before the restart boundary rather than deferred.

**Working style observed:** User prefers /copy-routed structured reasoning for non-trivial decisions (three rounds this session). Each /copy comes with explicit rationale, alternatives evaluated, and a recommendation. Implementation should follow verbatim. When a /copy includes "I would" or "Recommended," that IS the directive — no further confirmation needed.

**Communication pattern:** Reports use the "What changed / Why / Verification / Remaining risks" structure (per global CLAUDE.md Response Contracts) AND end with explicit decision points framed as multiple-choice + recommendation. User responds with "Yes, proceed with X" or modifies the recommendation; rarely overrides without explanation.

## Rejected Approaches

### Single combined memory + S7 + schema + Candidate A commit

**Approach:** Defer all closures to a single mega-commit covering memory correction, S7 split, schema bundle row, and Candidate A patch artifacts.

**Why it seemed promising:** Bundles all "pre-Candidate-A pre-execution" work atomically; one commit message covers everything; minimum push events.

**Specific failure:** Memory edits live outside the repo (no git relationship). Schema bundle is gitignored (only the row is committable). Candidate A patch is intentionally NOT committed (per Baseline's pattern). So the "single mega-commit" would actually be impossible for memory + bundle, and inappropriate for the patch. The actual structure is what we ended with: 2 separate docs commits + 2 side-effect filesystem changes (memory edit + patch staging) + 1 gitignored capture (schema bundle + .tmp/ files).

**What it taught:** "Atomic" means atomic *within* the repo. Cross-boundary "atomicity" (memory + repo + filesystem) doesn't compose; force-fitting it produces commits that lie about scope or scope that lies about commits.

### Capture schema bundle WITH `--experimental` flag

**Approach:** Include experimental fields in the pre-Candidate-A schema dump.

**Why it seemed promising:** More complete capture; would surface any experimental field a future variant might emit.

**Specific failure:** User's framing was "schema/contract truth" — the *stable* surface is the contract. `--experimental` would conflate stable contract with experimental drift in one snapshot, defeating the cross-variant-reference purpose. Also, user instruction was simply "Run `codex app-server generate-json-schema`" without flag specification — adding flags is scope creep.

**What it taught:** When the user gives a precise tool invocation, treat it as the directive. If broader capture is later useful (e.g., if a variant emits an unknown field), re-capture is one command. Defer surface expansion until evidence demands it.

### Reuse Baseline's runtime-proof log filename for Candidate A

**Approach:** Have Candidate A append to `/tmp/codex-collab-baseline-runtime-proof.log` (or rename to `runtime-proof.log` without variant prefix).

**Why it seemed promising:** Single file to read across all variants; less file management; "everything's in one log."

**Specific failure:** Risks contamination — if a future restoration step partially fails or if `trash` ever leaves residual content, a variant could read stale data from a prior variant. Per-variant isolation is cheap and eliminates the risk class entirely.

**What it taught:** When isolation is cheap and contamination is expensive, prefer isolation by default. Variant-named log files cost nothing; debugging "did we read the right variant" if reuse fails costs hours.
