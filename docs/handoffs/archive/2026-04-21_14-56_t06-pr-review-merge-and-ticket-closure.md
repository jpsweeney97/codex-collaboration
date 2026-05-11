---
date: 2026-04-21
time: "14:56"
created_at: "2026-04-21T18:56:57Z"
session_id: 5a1106fc-f44e-4723-8dd6-85d5df6d06f3
resumed_from: "docs/handoffs/archive/2026-04-21_13-40_t06-delegate-skill-ux-implementation-complete.md"
project: claude-code-tool-dev
branch: main
commit: 541bb45f
title: "T-06 PR review, merge, and ticket closure"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/skills/delegate/SKILL.md
  - docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - packages/plugins/codex-collaboration/tests/test_delegation_job_store.py
  - packages/plugins/codex-collaboration/tests/test_delegate_start_integration.py
  - docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md
---

# T-06 PR Review, Merge, and Ticket Closure

## Goal

Complete the T-06 ticket lifecycle: review PR #114 (delegate skill UX), address findings, merge, and close the ticket with precise AC evidence.

**Trigger:** Prior session completed all 7 implementation tasks and opened PR #114. This session was the review-and-land pass.

**Stakes:** T-06 is the final implementation ticket before T-07 (analytics, reviewer, migration docs, cross-model removal). Closing it cleanly with AC evidence unblocks T-07 design reconciliation.

**Success criteria (all met):**
1. PR #114 review findings addressed.
2. PR #114 merged to main.
3. T-06 ticket closed with AC mapping table and explicit verification status.
4. Live `/delegate` smoke explicitly deferred with rationale.

**Connection to project arc:** T-06 is the sixth ticket in the codex-collaboration build sequence. T-05 (execution domain) was the prerequisite. T-07 (analytics + cutover) is now unblocked.

## Session Narrative

**Phase 0 -- Handoff load (~2 min).** Loaded the prior session's handoff (`2026-04-21_13-40`). Clean state: `chore/delegate-skill-design` at `4304eb0b`, 842 tests, PR #114 open with all implementation work complete.

**Phase 1 -- PR review comments (~5 min).** User asked to address the review comment on PR #114 before merging. Fetched PR review state via `gh pr view` and `gh api .../pulls/114/comments`. Found one automated Codex review (P2: "Surface non-store busy states in active delegation summary") and the user brought a separate P3 finding about a router rule contradiction in the SKILL.md.

The Codex P2 finding identified a consistency gap between `get_active_delegation_summary()` (checks only job store) and `start()`'s busy gate (checks job store + registry + unresolved journal entries). Analyzed the three busy sources:
- Source (a) job store: durable, primary source -- checked by both paths.
- Source (b) runtime registry: in-process only, catches same-session retry after committed-start failure. Genuinely reachable from the status path but extremely narrow window.
- Source (c) unresolved journal entries: NOT reachable from status path because `_ensure_delegation_controller()` calls `recover_startup()` which reconciles these before the summary runs.

Presented two options (surface non-store busy sources in summary vs. add a diagnostic field). User did NOT address the Codex P2 in this session -- deferred.

**Phase 2 -- Router rule contradiction fix (~5 min).** The user's P3 finding was a doc consistency issue: the SKILL.md state router general rule (line 103) said "evaluate promotion_state first when non-null" but the Tier 3 pending row overrides this for non-completed jobs. Updated both SKILL.md and design spec to name the exception explicitly in the general rule. Committed at `80756b9a`.

**Phase 3 -- Full PR review (~15 min).** User requested `/pr-review-toolkit:review-pr`. Launched 4 specialized review agents in parallel:
- **code-reviewer**: No issues at confidence >= 80%. 842 tests pass. Server code follows patterns, SKILL.md internally consistent, assertion usage appropriate.
- **test-analyzer**: No critical gaps. Important suggestions: missing `queued/null` (6/10), `applied`/`prechecks_passed` (5/10) inclusion tests, `get_active_delegation_summary()` not directly unit-tested (4/10).
- **error-reviewer**: One actionable finding (MEDIUM): `except Exception` in MCP status enrichment missing server-side logging. Assertion usage appropriate. Error propagation from `get_active_delegation_summary()` correct (delegated to caller's catch).
- **comment-reviewer**: SKILL.md Tier 4 has an unreachable paragraph about `failed/unknown` with post-mutation states (I2). `promote()` docstring omits promotion_state gate and handle-exists check (I3). `active_delegation` in contracts.md has no field enumeration (I4).

**Phase 4 -- User adjudication (~5 min).** User adjudicated all findings with severity calibration:
- I1 (logging): Keep. P2/P3 hardening. "Every other broad catch logs" claim overstated but logging is warranted.
- I2 (dead-code paragraph): Keep and broaden. Same issue in design spec. Also noted Tier 4 headings say "promotion_state is null" which is now inaccurate with the pending fallthrough.
- I3 (promote docstring): Keep. P3 code-comment accuracy.
- I4 (contract fields): Keep. P3/P2 contract completeness.
- S1/S2 (queued/null, applied, prechecks_passed tests): Accept if touching tests.
- S3 (qualify attention_job_count): Accept.
- S4 (completed+null exclusion note): Accept.
- S5 (pre-migration anomaly phrasing): Optional.
- S6 (direct unit test for summary method): Defer/drop.

**Phase 5 -- Implementing review findings (~15 min).** Applied all accepted findings in one commit:
- I1: Added `logging`, `logger`, and `logger.warning(exc_info=True)` to mcp_server.py. Added `caplog` assertion to the existing factory-failure test.
- I2: Removed dead-code paragraph from SKILL.md. Updated Tier 4 headings in both SKILL.md and design spec. Cleaned up design spec's Tier 4 `failed/unknown` row to remove dead sub-cases.
- I3: Expanded `promote()` docstring with separate entry gates section.
- I4: Added `active_delegation` field table (7 fields) to contracts.md.
- S1/S2: Added 3 inclusion tests (queued/null, applied, prechecks_passed).
- S3: Qualified `attention_job_count` as `active_delegation.attention_job_count`.
- S4: Added exclusion note for completed+null.

845 tests passing, ruff clean. Committed at `e290bd69`.

**Phase 6 -- User's final precision fix (~3 min).** User found one more P3: the new `active_delegation` field table in contracts.md described `artifact_paths` generically ("diff, patch, summary") instead of naming the actual files (`full.diff`, `changed-files.json`, `test-results.json`), and `promotion_state` said "null for pre-completion jobs" without noting the legacy pending/non-completed shape. Fixed both rows. Committed at `062f4afb`.

**Phase 7 -- Merge and cleanup (~5 min).** Merged PR #114 via `gh pr merge 114 --merge --delete-branch`. Merge commit `85afab6b`. Synced local main.

**Phase 8 -- T-06 ticket closure (~10 min).** Updated the T-06 ticket with:
- `status: closed`, `closed_date: 2026-04-21`, `resolution: completed`, `resolution_ref: "PR #114 (85afab6b)"`
- All 7 AC checkboxes checked with evidence mapping table citing PRs #109-#114 and commit `57c6466a`.
- All 4 automated verification items checked with test names.
- Live `/delegate` smoke explicitly deferred: "Requires running Codex App Server. Automated package-level verification passed (845 tests). Live product smoke deferred to T-07 cutover or standalone App Server testing session."
- Resolution section with test count progression: 698 -> 734 -> 765 -> 771 -> 816 -> 818 -> 845.

Committed at `541bb45f`, pushed to main.

## Decisions

### Defer the Codex P2 finding (non-store busy sources in summary)

**Choice:** Did not address the Codex review finding about `get_active_delegation_summary()` only checking the job store while `start()` checks three busy sources.

**Driver:** User brought a separate P3 finding (router rule contradiction) and the Codex P2 was not revisited. The P2 describes a real consistency gap but with extremely narrow reachability: requires a committed-start finalization failure that leaves a registered runtime without a persisted job, in the same session, and the user must invoke bare `/delegate` (not `/delegate <objective>`) after the failure.

**Alternatives considered:**
- **Surface non-store busy sources in summary** -- adds complexity for an edge case that self-resolves on session restart.
- **Add a `delegation_busy_orphan` diagnostic field** -- lighter touch, preserves the clean job-store-only method.

**Trade-offs accepted:** A narrow window exists where `codex.status` reports `active_delegation: null` while `codex.delegate.start` returns `busy`. Self-resolves on restart.

**Confidence:** Medium (E1) -- analysis of the three busy sources shows (b) is genuinely reachable but (c) is not (reconciled by `_ensure_delegation_controller`).

**Reversibility:** High -- can be addressed in a future PR without changing any public interface.

**Change trigger:** If a user hits this in practice (status says "no active delegation" but start returns busy), address it. Otherwise, the edge case is self-resolving.

### Explicit deferral of live `/delegate` smoke

**Choice:** Closed T-06 with the live smoke test explicitly deferred rather than silently omitted.

**Driver:** User instruction: "do not silently imply it did. Either run that smoke now with App Server, or close T-06 with a clear note that automated/package verification passed and live product smoke is deferred."

**Alternatives considered:**
- **Run the live smoke now** -- requires Codex App Server, which is not available in this session. Not feasible.
- **Silently close without mentioning it** -- user explicitly prohibited this.

**Trade-offs accepted:** One verification item remains unchecked. All server-side behavior is verified by 845 automated tests; the deferred item covers only skill rendering UX (diff display, escalation formatting, ceremony gate enforcement as experienced by Claude in a live session).

**Confidence:** High (E2) -- automated tests verify server behavior; only the skill-as-instruction-document aspect is untested.

**Reversibility:** N/A -- the deferral is documented in the ticket. Can be addressed in any future session with App Server access.

**Change trigger:** When Codex App Server is available, run the live smoke. Or fold into T-07 cutover verification.

## Changes

### Server: `mcp_server.py` -- added logging for delegation status enrichment

| File | What changed |
|------|-------------|
| `server/mcp_server.py` | Added `import logging` and `logger = logging.getLogger(__name__)`. Added `logger.warning("Delegation status enrichment failed: %s", exc, exc_info=True)` inside the `except Exception` block at the delegation status enrichment path. Full traceback now preserved server-side; truncated repr still goes to consumer via `delegation_status_error`. |

### Server: `delegation_controller.py` -- expanded promote() docstring

| File | What changed |
|------|-------------|
| `server/delegation_controller.py` | `promote()` docstring at line 907 expanded from 5 prechecks to separate "Entry gates" section (job exists, status completed, promotion_state promotable, artifact_hash present, collaboration handle exists) followed by 4 workspace prechecks (HEAD match, clean status, clean index, artifact hash verification). No behavior change. |

### Skill: `skills/delegate/SKILL.md` -- 4 doc fixes

| Change | Location | What |
|--------|----------|------|
| Router rule exception | Line 103 | Named the `pending` with `status != "completed"` exception in the general rule |
| Tier 4 heading | Line 130 | Removed "(promotion_state is null)" from heading |
| Dead-code paragraph removed | Line 139 (was) | Removed unreachable paragraph about `failed/unknown` with post-mutation states |
| `attention_job_count` qualified | Line 97 | Changed to `active_delegation.attention_job_count` |
| `completed + null` note | Line 137 | Added "Excluded from `active_delegation` and the busy gate -- reachable only via explicit `/delegate poll {job_id}`" |

### Design spec: `2026-04-21-delegate-skill-ux-design.md` -- 3 doc fixes

| Change | Location | What |
|--------|----------|------|
| Router precedence exception | Line 135 | Named the `pending` exception in the general rule |
| Tier 4 heading + sub-note | Line 162 | Removed "(promotion_state is null)", added explanatory line about fallthrough |
| `failed/unknown` row cleaned | Line 168 | Removed dead sub-cases for post-mutation states; added parenthetical noting Tier 2 handles those |
| `completed + null` note | Line 169 | Added exclusion from `active_delegation`/busy gate |

### Contracts: `contracts.md` -- field table for `active_delegation`

| File | What changed |
|------|-------------|
| `contracts.md` | Added `#### active_delegation Fields` subsection with 7-field table: `job_id`, `status`, `promotion_state`, `base_commit`, `artifact_hash`, `artifact_paths`, `attention_job_count`. Descriptions reference actual artifact names (`full.diff`, `changed-files.json`, `test-results.json`) and note the legacy pending/non-completed shape. |

### Tests: 3 new inclusion tests + caplog assertion

| File | Tests added |
|------|------------|
| `test_delegation_job_store.py` | `test_list_user_attention_required_returns_queued_null_promotion`, `test_list_user_attention_required_returns_applied`, `test_list_user_attention_required_returns_prechecks_passed` |
| `test_delegate_start_integration.py` | Updated `test_status_delegation_status_error_when_factory_fails` with `caplog` fixture and 2 new assertions: log message present + `exc_info` attached |

### Ticket: T-06 closure

| File | What changed |
|------|-------------|
| `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Status changed to `closed`, `closed_date: 2026-04-21`, `resolution: completed`. All 7 AC checkboxes checked with evidence mapping table. 4/5 verification items checked. Live smoke explicitly deferred. Resolution section with test progression. Added design spec and plan to References table. |

## Codebase Knowledge

### Architecture: Delegation Status Enrichment Path (post-review)

```
codex.status request arrives at MCP server
  -> _dispatch_tool (mcp_server.py:350)
       -> control_plane.codex_status(repo_root)  # base advisory status
       -> try:
            _ensure_delegation_controller()       # init/recover
            controller.get_active_delegation_summary()
            if job: populate active_delegation (7 fields)
          except Exception:
            logger.warning(..., exc_info=True)    # NEW: full traceback
            set delegation_status_error
       -> return enriched result
```

### Three Busy Sources in start() vs. Summary

| Source | `start()` busy gate | `get_active_delegation_summary()` | Notes |
|--------|--------------------|------------------------------------|-------|
| (a) Job store: `list_user_attention_required()` | Yes (line 335) | Yes (line 2008) | Primary, durable |
| (b) Runtime registry: `active_runtime_ids()` | Yes (line 352) | **No** | In-process only, same-session. Codex P2. |
| (c) Unresolved journal: `job_creation` entries | Yes (line 376) | **No** (reconciled by `_ensure_delegation_controller`) | Durable but resolved before summary runs |

This is the Codex P2 finding. Source (b) is the only genuinely reachable gap. Source (c) is a non-issue because `_ensure_delegation_controller()` at mcp_server.py:357 calls `recover_startup()` during initialization.

### Key Implementation Locations (updated)

| Concept | Location |
|---------|----------|
| MCP status enrichment | `mcp_server.py:350-381` |
| Delegation status logging | `mcp_server.py:374` (new) |
| `get_active_delegation_summary()` | `delegation_controller.py:1996-2012` |
| `promote()` entry gates | `delegation_controller.py:920-978` |
| `_TERMINAL_PROMOTION_STATES` | `delegation_job_store.py:23-25` |
| Delegate skill SKILL.md | `skills/delegate/SKILL.md` |
| `active_delegation` field table | `contracts.md:376-384` (new) |
| T-06 ticket | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` |

### Review Agent Patterns

| Agent | Model | Duration | Tool calls | Finding quality |
|-------|-------|----------|------------|-----------------|
| code-reviewer | sonnet | ~161s | 28 | No high-confidence issues. Good pattern conformance check. |
| test-analyzer | sonnet | ~102s | 19 | Precise matrix gap analysis. Correctly identified queued/null as conspicuous. |
| error-reviewer | sonnet | ~162s | 29 | Distinguished new vs pre-existing issues. Correctly flagged logging gap. |
| comment-reviewer | sonnet | ~159s | 29 | Caught unreachable Tier 4 paragraph (cross-section consistency). |

## Context

### Mental Model

This was a **review-and-land session**, not a design or implementation session. The work was: verify correctness of prior implementation, address findings, merge, and close the ticket with evidence. The mental model was quality assurance with documentation discipline -- every finding needed precise classification (P2/P3, keep/defer, code vs doc), and every ticket AC needed traceable evidence.

### Project State

| Ticket | Status | Tests | Key commit |
|--------|--------|-------|------------|
| T-04 | Closed | -- | -- |
| T-05 | Closed | 698 | -- |
| T-06 | **Closed** | **845** | **541bb45f** |
| T-07 | **Unblocked** | -- | -- |

**T-07 scope** (from ticket): Analytics dashboard, reviewer agent, migration docs, parity matrix, cross-model removal. First step should be a scope reconciliation pass over T-04/T-06 evidence and T-07 ACs.

### Codex P2 Status

The Codex automated review found one P2 finding on `delegation_controller.py:2012` about `get_active_delegation_summary()` not surfacing non-store busy states. Analysis showed source (c) is a non-issue but source (b) is genuinely reachable in a narrow window. Not addressed this session. The finding remains open on the PR (now merged). Can be addressed in a future PR if it surfaces in practice.

## Learnings

### 4-agent parallel review catches cross-section issues that per-section review misses

**Mechanism:** The comment-analyzer found the unreachable Tier 4 paragraph (I2) that survived 6 rounds of adversarial review in the prior session. Each prior review looked at sections individually; the comment-analyzer cross-referenced the state router general rule against the specific tier contents.

**Evidence:** The paragraph about `failed/unknown` with post-mutation `promotion_state` was placed after Tier 4 but described states handled in Tier 2. The state router preamble guarantees those states never reach Tier 4.

**Implication:** For multi-section instruction documents, a dedicated cross-section consistency pass is more valuable than deeper per-section review. The 4-agent review structure (code + tests + errors + comments) naturally produces this cross-referencing.

### Contract precision matters when the contract is the resume source

**Mechanism:** The `active_delegation` field table is what the delegate skill reads on every invocation. Generic descriptions ("diff, patch, summary") would have caused confusion when matching artifact names against actual files on disk.

**Evidence:** ArtifactStore materializes `full.diff`, `changed-files.json`, `test-results.json` (verified at `artifact_store.py:68-70`). The initial field table used generic placeholders.

**Implication:** When a contract field is the primary data source for a downstream consumer, the contract should enumerate the exact values, not describe them generically. This applies to any future contract additions.

### User adjudication adds calibration that raw review findings lack

**Mechanism:** The 4 review agents produced findings with severity labels (MEDIUM, LOW). The user recalibrated: I1's "every other broad catch logs" claim was "overstated" but the fix was still warranted. I2 was "keep and broaden" (same issue in design spec, plus stale Tier 4 headings). This calibration step prevented both over-reaction and under-reaction.

**Evidence:** User's adjudication table included severity calibration and explicit notes fields for each finding. S5 was downgraded to "optional" and S6 to "defer/drop unless reviewer insists."

**Implication:** Review findings should be presented as input to user adjudication, not as final directives. The user's domain knowledge adds calibration that automated review cannot provide.

## Next Steps

### 1. T-07 design reconciliation

**Dependencies:** T-06 closed (done).

**What to do:** Scope reconciliation pass over T-07 ACs against T-04/T-06 evidence. The user specified: "First step should be a scope reconciliation pass over the closed T-04/T-06 evidence and the T-07 ACs, especially the conditional context-injection removal rule."

**What to read first:** T-07 ticket at `docs/tickets/` (find the exact file). T-04 and T-06 closed tickets for evidence. Cross-model capability analysis at `docs/reviews/2026-03-17-cross-model-capability-analysis.md`.

**Approach:** Read T-07 ACs, map each against what T-04/T-06 already delivered, identify what's net-new, reconcile any ACs that may be satisfied or changed by the T-06 work.

### 2. Live `/delegate` smoke (when App Server available)

**Dependencies:** Running Codex App Server.

**What to test:** Full delegation lifecycle through the skill: start -> poll (check progress) -> poll (completed, review rendering) -> promote or discard. Specifically watch for: grammar parsing, status preflight catching `delegation_status_error`, review rendering reading artifact files, ceremony gates enforcing review-before-promote, escalation rendering per-kind.

### 3. Codex P2 (non-store busy sources) -- optional

**Dependencies:** None. Can be addressed independently.

**What to do:** If the narrow window (registered runtime without persisted job, same session, bare `/delegate` invocation) is deemed worth closing, either widen `get_active_delegation_summary()` to check the registry and journal, or add a `delegation_busy_orphan` diagnostic field.

## In Progress

**Clean stopping point.** All work completed, committed, and pushed. T-06 closed. PR #114 merged. No code changes in flight.

## Open Questions

### 1. Codex P2: Non-store busy sources in active delegation summary (inherited + analyzed)

**Context:** `get_active_delegation_summary()` only checks the job store, but `start()`'s busy gate checks three sources. Source (b) (runtime registry) is genuinely reachable in a narrow window in the same session. Source (c) (unresolved journal entries) is reconciled by `_ensure_delegation_controller()` before the summary runs.

**Decision pending until:** Either production evidence that someone hits the gap, or T-07 design reconciliation determines it should be addressed.

### 2. `git diff --binary` output stability (inherited from prior sessions)

**Context:** Post-apply verification relies on byte-for-byte comparison of regenerated `full.diff`.

**Decision pending until:** Production testing reveals whether byte comparison is reliable.

### 3. `request_user_input` answer construction in live skill (inherited)

**Context:** Design specifies Claude constructs the `answers` parameter from conversation context. Untestable without live skill invocation.

**Decision pending until:** First live `request_user_input` escalation through the delegate skill.

## Risks

### 1. Skill rendering behavior untestable without live session

All server-side behavior is verified by 845 automated tests. The deferred live smoke covers only skill UX rendering -- diff display, escalation formatting, ceremony gate enforcement as experienced by Claude. This is the one gap between "tests pass" and "product works."

### 2. Codex P2 gap (narrow but real)

A committed-start finalization failure that leaves a registered runtime without a persisted job creates a state where status reports `active_delegation: null` while start returns `busy`. Self-resolves on restart. Narrow window but the inconsistency could confuse users who see "no active delegation" and try to start a new one.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-06 ticket (closed) | `docs/tickets/2026-03-30-codex-collaboration-promotion-flow-and-delegate-ux.md` | Ticket scope and AC evidence |
| Design spec | `docs/superpowers/specs/2026-04-21-delegate-skill-ux-design.md` | Normative design |
| Contracts | `docs/superpowers/specs/codex-collaboration/contracts.md` | Tool surface, response shapes, `active_delegation` field table |
| Promotion protocol | `docs/superpowers/specs/codex-collaboration/promotion-protocol.md` | State machine, preconditions |
| Recovery and journal | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Journal phases, concurrency |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-21_13-40_t06-delegate-skill-ux-implementation-complete.md`
- T-06 arc: ... -> delegate skill design + plan -> delegate skill implementation -> **PR review, merge, ticket closure (this handoff)**

### Commits this session

| Commit | Title |
|--------|-------|
| `80756b9a` | fix(t20260330-06): resolve router rule contradiction for pending fallthrough |
| `e290bd69` | fix(t20260330-06): address PR review findings -- logging, dead-code routing, docs, tests |
| `062f4afb` | fix(t20260330-06): correct active_delegation contract field descriptions |
| `85afab6b` | Merge pull request #114 (merge commit) |
| `541bb45f` | docs(t20260330-06): close ticket -- all ACs met, 845 tests |

### PR

- PR #114: `feat(t20260330-06): delegate skill UX -- server enrichment + SKILL.md` -- MERGED at `85afab6b`

## Gotchas

### 1. `_replay()` silent corruption now on hot path

**Symptom:** `_replay()` silently skips corrupted JSONL lines. With status enrichment, this runs on every `codex.status` call.

**Root cause:** Pre-existing design -- `_replay()` uses skip-and-continue for forward compatibility. Before this PR, it was only called during active delegation operations. Now it's called on every status request.

**Impact:** If the JSONL file has a corrupted record for the only active job, status reports `active_delegation: null` without setting `delegation_status_error`. No exception is raised because `_replay()` succeeded -- it just returned fewer results.

**Prevention:** Pre-existing pattern debt. Out of scope for this PR. Noted by the error-reviewer as MEDIUM severity.

### 2. Pyright stale diagnostics after subagent writes (inherited)

**Symptom:** Pyright reports methods as unknown even though they exist and tests pass.

**Root cause:** LSP server doesn't get real-time file-change notifications from subprocess edits. Stale diagnostics in the notification bar (`"logging" is not accessed`, `"pytest" is not accessed`) appear immediately after adding imports but resolve once Pyright catches up.

**Prevention:** Verify with test execution, not Pyright diagnostics.

### 3. Ruff format pre-existing divergence

**Symptom:** `ruff format --check` on the full package reports 19 files needing reformatting.

**Root cause:** Pre-existing formatting differences across the package. Not introduced by this PR.

**Prevention:** Only check formatting on changed files: `ruff format --check <specific files>`.

## User Preferences

### Adjudication before action

User reviewed all 4 review agents' findings and provided a structured adjudication table with severity calibration and notes for each finding before any changes were made. Pattern: "My adjudication: keep all four Important findings, but calibrate them as 'small follow-up patch before merge,' not evidence that the implementation is structurally unsafe."

### Verification before claims

User ran independent verification after the review findings commit: `git diff --check`, pytest on affected files, ruff check, and `gh pr view` for merge state. Explicitly stated the results before declaring merge-readiness.

### Explicit deferral over silent omission

User instructed: "do not silently imply it did. Either run that smoke now with App Server, or close T-06 with a clear note that automated/package verification passed and live product smoke is deferred." Clear pattern: prefer honest documentation of what wasn't done over implying completeness.

### Structured ticket closure

User specified the exact closure procedure: "Update T-20260330-06 with `status: closed`, `closed_date`, `resolution`, `resolution_ref`, and an AC mapping table. This should cite the poll/decide/promote/discard/delegate-skill PRs or commits."

### Design reconciliation before coding for T-07

User explicitly stated: "Then start T-07 design reconciliation, not coding. First step should be a scope reconciliation pass over the closed T-04/T-06 evidence and the T-07 ACs."
