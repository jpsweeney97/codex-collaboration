---
date: 2026-05-09
time: "23:13"
created_at: "2026-05-10T06:13:00Z"
session_id: 3ae82b62-32e2-43d2-b76b-a5f3b73df384
project: claude-code-tool-dev
branch: chore/codex-collab-envelope-diagnostic-overclaim-fix
commit: 04a7fb43
title: "Summary: codex-collab orientation correction and overclaim-fix plan committed"
type: summary
files:
  - docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md
  - docs/diagnostics/2026-05-01-codex-app-server-server-request-envelope-probes.md
  - docs/diagnostics/codex-app-server-server-request-envelope-probes.json
  - docs/plans/2026-05-01-codex-app-server-client-platform-rebaseline-implementation-plan.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/approval_router.py
  - packages/plugins/codex-collaboration/server/codex_compat.py
---

# Summary: codex-collab orientation correction and overclaim-fix plan committed

## Goal

Read-only orientation pass on codex-collaboration build progress, then — once the orientation surfaced a docs-only contradiction in the May-1 envelope-probe diagnostic — produce an approval-gated plan to fix it. The orientation came at the start of a session resuming codex-collab work after a multi-day public-skills-repo workstream. The plan is the deliverable.

## Session Narrative

Started with a memory-anchored orientation report. Memory said "NEXT: Roadmap Steps 2-6" with Step 2 (T-20260429-01 sandbox carve-outs) as the next active item. Produced a report claiming the codex-collab post-Packet-1 work was parked in worktrees and not yet on main.

User invoked `/superpowers:receiving-code-review` with a P0 finding: the central premise was inverted. `git branch --contains` showed `* main` for the disputed shas (current-branch marker AND the listing is filtered to branches that contain the commit — both signals say main contains them), and `git rev-list --left-right --count main...feature/...rebaseline` returned `28 0` (main 28 ahead, feature 0 unique). My report had inverted the conclusion. Verified each finding before responding: P0 confirmed, P1 register-staleness confirmed, P1 artifact-count imprecision confirmed, P1 missed doc-tension confirmed, P2 stale "shouldn't merge" framing confirmed, P3 line-citation fabrication confirmed.

Issued a corrected orientation. User pushed back again with five more findings: (1) "live `cancel` triggers fallback" was wrong — the trigger is the mixed list containing a structured object (`acceptWithExecpolicyAmendment`), not `cancel`; (2) Threads 1 and 2 were not fully independent because smoke and credential-probe execution can pass through command-approval responses; (3) "Thread 2 is short" was only true if docs-only; (4) Priority #2 scope was too narrow vs the register's broader exit condition; (5) Wording nit on `+ main` vs `* main`. Verified at `approval_router.py:103-111` — `all(isinstance(decision, str) ...)` is the gate. Acknowledged all five.

User authorized drafting a docs-only fix plan with six explicit structural requirements (raw facts to preserve, overclaims to patch, authority basis, files to inspect, JSON disposition stop condition, verification rg sweep). Invoked `superpowers:writing-plans`. Created a chore branch (`chore/codex-collab-envelope-diagnostic-overclaim-fix`), wrote the plan to `docs/plans/2026-05-09-...md`, presented for approval.

User reviewed: "Approve with edits" — five findings. (1) The .md has four overclaim sites, not two — added "observed supported methods" (≈line 178) and "This packet proves compatibility" (≈line 185). (2) The verification rg pattern needed `proves compatibility|compatibility for the observed|local_compatibility|supported_methods` added. (3) Task 4 wording said "only smoke and probe remain" but ticket AC #3 (regression assertion + suite pass) is also unchecked. (4) Don't bump global "Last reconciled" for a partial annotation. (5) JSON paths should be first-class targets. Verified each, then revised the plan: 4 sites enumerated, sweep extended in three places, AC #1-#3 wording, no global date bump, JSON paths called out by exact path with vocabulary caveat (the JSON's binary `supported_methods/unsupported_methods` schema can't express the corrected lossy state, pushing toward supersession-note).

User reviewed revision: "Approve with two small edits" — Task 5.3 still said "smoke + credential probe + close" without AC #3, and the commit message body had the same stale wording. Fixed both. Approved. Committed plan at `04a7fb43`. Offered execution choices (inline / subagent-driven / pause).

## Decisions

### Plan-branch strategy

**Choice:** Create `chore/codex-collab-envelope-diagnostic-overclaim-fix` off main; write plan uncommitted; commit plan only after explicit approval.

**Driver:** User explicitly said "approval-gated." Uncommitted plan preserves freedom to amend during review without rebase or amend churn.

**Alternatives:** Commit plan immediately as draft and amend (creates pushed commit history of half-baked plans); skip branch and write directly on main (blocked by branch-protection hook anyway).

**Trade-offs:** Adds one approval-gate ceremony but produces a clean single-commit plan deliverable. Worked smoothly across two revision rounds.

### JSON disposition framework — supersession-preferred

**Choice:** In Task 1.4, prefer supersession-note over patch-in-place when the JSON's consumer status is unclear.

**Driver:** The JSON's `compatibility_classification` block uses a binary vocabulary (`supported_methods`/`unsupported_methods`/`unknown_or_unparseable_methods`/`missing_required_fields`). The corrected classification — *parser-kind compatible but decision-shape lossy* — has no slot in this vocabulary. Patch-in-place either invents a new key (schema change, may break consumers) or zeroes `supported_methods` and adds a sibling array (mutates existing array semantics).

**Alternatives:** Force patch-in-place with a new key everywhere; force in-place with array clearing and risk silent consumer breakage; mix patch + supersession.

**Trade-offs:** Supersession-note is conservative; future readers see the original capture plus a "_superseded_by" pointer. Slight cognitive overhead vs in-place clarity, but no risk of silently breaking consumers we don't know about.

### AC #3 wording (option 2 from user's offer)

**Choice:** Change register wording to enumerate AC #1-#3 explicitly rather than verify-and-reconcile AC #3 within this plan.

**Driver:** Plan scope is intentionally docs-only. Verifying AC #3 (regression assertion update + full suite pass) would expand into runtime verification work and break the scope guardrail.

**Alternatives:** Run `pytest` ourselves to check AC #3 status; defer wording entirely until AC #3 is independently verified.

**Trade-offs:** Register stays slightly less specific about what closure evidence currently exists (we don't know if the suite would pass right now). Acceptable because the register annotation is honest about what's *missing*, and any reader who acts on the annotation will re-verify before claiming closure.

### No global "Last reconciled" date bump

**Choice:** Leave register's global "Last reconciled: 2026-04-30" date alone; capture row-local recency via "As of 2026-05-09" stamp inside the T-20260429-01 row annotation.

**Driver:** Patch is intentionally narrow — only one row + one priority line. Bumping the global date would imply full register reconciliation, which this plan does not perform.

**Alternatives:** Bump global date with a footnote; defer the date question entirely.

**Trade-offs:** Future register readers might wonder why the global date wasn't bumped, but the in-cell stamp provides the recency signal at exactly the right scope.

## Changes

### `docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md` (new)

Approval-gated, docs-only plan to reconcile the May-1 envelope-probe diagnostic with `approval_router.py:103-111` and the rebaseline plan. Six tasks: discovery → .md patch → JSON reconciliation → optional register annotation → final cross-doc sweep → commit. Four .md overclaim sites enumerated with verbatim replacement wording. Two known JSON paths (`observed_server_requests[0].local_compatibility`, `compatibility_classification.supported_methods`) called out as first-class targets with explicit vocabulary caveat. Task 4 references AC #1, #2, AND #3 (no "only smoke and probe" framing). Verification rg pattern combines bare-word, phrase, and JSON-key terms in three places. Committed at `04a7fb43`.

## Codebase Knowledge

- **`packages/plugins/codex-collaboration/server/approval_router.py:103-111`**: `_resolve_available_decisions` keeps the wire `availableDecisions` only when `isinstance(wire_value, list) and all(isinstance(decision, str) for decision in wire_value)`. Mixed lists with structured (dict) entries fall through to `_AVAILABLE_DECISIONS[kind]`. The fallback tuple for `command_approval` includes `decline`. The live envelope offered `cancel`, not `decline`.
- **`packages/plugins/codex-collaboration/server/runtime.py:107-118`**: `build_workspace_write_sandbox_policy` Phase 1 carve-outs landed: `~/.codex/memories`, `~/.codex/plugins/cache`, `~/.agents/skills`, `~/.agents/plugins`, plus dynamic gitdir resolution from worktree's `.git` pointer. Two-layer defense on gitdir (3-component minimum + back-pointer round-trip) merged at PR #127.
- **`packages/plugins/codex-collaboration/server/codex_compat.py:24,27`**: `TESTED_CODEX_VERSION` and `MINIMUM_CODEX_VERSION` both `"0.117.0"`. Rebaseline plan explicitly forbids raising these.
- **Worktree topology**: Three feature branches (`...-exploration`, `...-rebaseline`, `unrelated-change`) are all ancestor branches of main. `git rev-list --left-right --count main...feature` returns `28 0`/`29 0`/`28 0`. Branches are clean but stale — deletable. 17 delegation runtime worktrees under `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/<uuid>/worktree/` are runtime artifacts, not active development.
- **`docs/status/codex-collaboration-reconciliation-register.md:9,52,67`**: Last reconciled date, priority #1 line, T-20260429-01 row. All three are stale relative to current `main` — implementation has landed but the register still ranks "Implement Phase 1" as priority #1.
- **May-1 artifact set on main**: 6 plans + 4 .md diagnostics + 4 .json diagnostics + 2 architecture notes covering the App Server rebaseline. The rebaseline implementation plan calls for two more derived artifacts (capability matrix .md/.json + method-classification .md/.json) that have not yet been created.

## Learnings

- **Single-signal trap.** `git branch --contains` output's `* main` line both lists "branches containing the commit" AND marks current branch. I read it as the latter and missed the former. When a single signal is going to load-bear a major conclusion, run a second independent check (`git rev-list --left-right --count`). Cost an entire round of orientation work and burned credibility for the rest of the session.
- **Narrative vs invariant.** My errors collapsed plan/register narrative summaries into the underlying invariant. Code (`_resolve_available_decisions`) and structured cells (register's exit-condition column) hold the truth. Narrative summaries can drift from both. Read both, prefer code.
- **JSON vocabulary expansion is the gotcha for tri-state corrections.** Binary `supported/unsupported` schemas become brittle when introducing a third state. Future T-20260429-02 capability artifacts should start with a tri-state vocabulary (`fully_supported` / `parser_kind_compatible_lossy` / `unsupported`) — captured as a non-scope-expanding observation in the plan.
- **Renumbering churn produces stale cross-references.** Adding/removing steps invalidates references downstream. After renumbering Tasks 2.3-2.5 → 2.5-2.7 and removing Task 4.4, Task 6.1/6.3 still pointed at old numbers; user caught it on second review.

## Next Steps

1. **Choose execution mode for the plan** — inline / subagent-driven / pause. User has been deeply involved in plan review; inline likely better given Task 1's decisions feed Tasks 2-4 tightly.
2. **Execute Tasks 1-6** of the overclaim-fix plan. Six tasks; expected commit at end of Task 6.
3. **PR back to main** when Task 6 commit lands. Single commit on top of plan-add commit.
4. **Then T-20260429-01 closure** — comparable `/delegate` smoke (AC #1), credential-boundary probe (AC #2), regression assertion update + suite pass (AC #3). Needs live App Server access.
5. **Then T-20260429-02 method matrix** — capability artifact + method-by-method classification + lossless parser/response branch implementation. Larger scope.
6. **Memory update candidate**: replace "NEXT: Roadmap Steps 2-6" with the corrected post-orientation framing once the plan executes and lands.

## Project Arc

### Accomplishments (across sessions)

- T-20260423-02 Packet 1 (Deferred-Approval Response): MERGED 2026-04-28 (PR #126).
- Codex-collaboration drift cleanup (D-01 through D-09): COMPLETE 2026-04-30.
- Step 0 roadmap cleanup: MERGED 2026-04-30.
- Step 1 (T-20260416-01 reply extraction): CLOSED 2026-04-30.
- Step 2 (T-20260429-01 sandbox carve-outs Options B + E + ~/.agents/): IMPLEMENTATION LANDED on `main` via PR #127, including two-layer gitdir defense after security review. Closure evidence (smoke + probe + suite) outstanding.
- May-1 App Server rebaseline scope: 6 plans + 4 .md/4 .json diagnostics + 2 architecture notes committed on main. Capability matrix + method-classification artifacts NOT YET created.
- Public-skills-repo (separate workstream): PUBLISHED 2026-05-08 at https://github.com/jpsweeney97/claude-code-skills (22 skills, v0.1.0).
- This session: orientation correction + approval-gated overclaim-fix plan committed at `04a7fb43`.

### Current position

Branch: `chore/codex-collab-envelope-diagnostic-overclaim-fix` at `04a7fb43`. Plan committed, uncommitted execution. Still on `main` for the latest codex-collab post-implementation state at `1ed3f3fc`. Three feature worktrees clean but stale. Register at `docs/status/codex-collaboration-reconciliation-register.md` is stale (last reconciled 2026-04-30).

### Load-bearing decisions still governing the work

- **Don't raise version pins** until the v128 branch decision packet lands — `TESTED_CODEX_VERSION = MINIMUM_CODEX_VERSION = "0.117.0"`.
- **Plan-first, approval-gated, docs-only** for the contradiction fix. Implementation work (parser fix, response branch) deferred.
- **Supersession-note preferred** for JSON disposition when consumer status is unclear.
- **Sandbox `~/.codex/` carve-outs are subdirectory-scoped only** (`memories/`, `plugins/cache/`); credential paths (`auth.json`, `config.toml`, `history.jsonl`, `sessions/`) remain blocked.

### Drift risks

- The "Roadmap Steps 2-6" framing in memory pre-dates the May-1 rebaseline scope expansion. Memory probably needs an update once the overclaim-fix plan executes.
- Three stale feature branches (`...-exploration`, `...-rebaseline`, `unrelated-change`) still exist locally. Deletable but not yet cleaned up.
- Reconciliation register staleness: still ranks "Implement T-20260429-01 Phase 1" as priority #1 even though implementation has landed. The plan's optional Task 4 addresses this narrowly.
- AC #3 (test suite pass) is unchecked; the plan's Task 4 wording acknowledges this rather than verifying.
- The committed envelope-probe diagnostic remains contradictory with the rebaseline plan and code reality on `main` *until* the plan executes. This is exactly the bug the plan exists to fix; not a new risk, but a present-tense one.

### Downstream impacts of this session

- Memory-update candidate: NEXT focus phrasing. Defer until plan execution closes the contradiction.
- Reconciliation register update: deferred to plan execution (Task 4).
- Stale feature-branch cleanup: orthogonal; can happen any time.
