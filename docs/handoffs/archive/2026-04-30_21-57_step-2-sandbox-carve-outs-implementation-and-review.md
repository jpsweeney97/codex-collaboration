---
date: 2026-04-30
time: "21:57"
created_at: "2026-05-01T01:57:28Z"
session_id: 92cc828a-2fd4-4268-9344-8c253b47567e
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-30_21-04_t-20260416-01-closure-and-step-2-plan.md
project: claude-code-tool-dev
branch: feature/step-2-sandbox-carve-outs
commit: d1f9ed06
title: Step 2 sandbox carve-outs — implementation, review, and security hardening
type: handoff
files:
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/tests/test_runtime.py
  - docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md
  - docs/plans/2026-04-30-step-2-sandbox-carve-outs-options-b-e-agents.md
---

# Handoff: Step 2 sandbox carve-outs — implementation, review, and security hardening

## Goal

Implement T-20260429-01 Phase 1 sandbox carve-outs (Options B + E + `~/.agents/`) to reduce avoidable delegation escalations from ~11 to near-zero, then iterate through code review cycles to close security gaps before merging.

**Trigger:** Continuation of the 7-step roadmap. Steps 0-1 completed in prior sessions. The Ultraplan-refined plan was ready for implementation at `docs/plans/2026-04-30-step-2-sandbox-carve-outs-options-b-e-agents.md`.

**Stakes:** The prior T-01 smoke required 24 operator escalations for a 1-line edit, ~11 of which were avoidable sandbox friction. This implementation directly reduces the operator burden for `/delegate` runs by widening `readableRoots` to include benign data paths Codex reads during execution.

**Success criteria:**
- `build_workspace_write_sandbox_policy()` extended with Option B, `~/.agents/`, and Option E
- Credential boundary preserved (`~/.codex/auth.json`, `~/.codex/config.toml` NOT in `readableRoots`)
- Full test suite passes with updated regression assertion
- Security review clean (no trust-boundary bypass vectors)

**Connection to project arc:** Seventh session in the codex-collaboration reconciliation and implementation sequence. Steps 0-1 complete + closed, drift cleanup complete (D-01 through D-09). Step 2 is the first implementation step in the post-closure roadmap.

## Session Narrative

Loaded the prior handoff (T-20260416-01 closure and Step 2 plan). The handoff's first next step was to check if Ultraplan had refined the plan and then implement. Read the plan at `docs/plans/2026-04-30-step-2-sandbox-carve-outs-options-b-e-agents.md` — it was complete and ready for implementation.

One notable refinement from Ultraplan: the original session decision was full-directory `~/.agents/` as a single `readableRoots` entry, but the refined plan narrowed to subdirectory carve-outs (`~/.agents/skills` + `~/.agents/plugins`) to match the `~/.codex/` carve-out model. This is more conservative — if `~/.agents/` later gains credential files, the subdirectory-level carve-out prevents silent read-access expansion.

Verified the plan against current source: `runtime.py:27-61` matched the plan's description of `build_workspace_write_sandbox_policy()`, and `test_runtime.py:171-187` matched the regression assertion shape. Created a feature branch (`feature/step-2-sandbox-carve-outs`) and proceeded.

Implementation was straightforward — five tasks executed sequentially:

1. Updated T-20260429-01 ticket with `~/.agents/` scope amendment (Friction surface 1b section)
2. Implemented `_resolve_worktree_gitdir()` helper and updated `build_workspace_write_sandbox_policy()` with all three categories (Option B static paths, `~/.agents/` static paths, Option E dynamic gitdir)
3. Updated regression test to expect 5-entry `readableRoots` (worktree + 4 carve-outs)
4. Added 6 Option E tests: absolute pointer, relative pointer, `.git` is directory, malformed, unreadable, missing
5. Full test suite: 1089 passed, 1 skipped

Committed, pushed, and created PR #127. Then used the finishing-a-development-branch skill — user chose option 2 (push and create PR).

The user then submitted a code review with 4 findings:

**P1 (Security — sandbox bypass):** `_resolve_worktree_gitdir` trusted whatever path was written in the worktree's `.git` file. Since the worktree has `writableRoots` access, a compromised execution turn could rewrite `.git` to point at an arbitrary host path (e.g., `~/.codex/`), and the next decide turn would rebuild the policy and grant read access there. This was a genuine sandbox boundary bypass introduced by Option E.

**P2 (PR scope):** PR #127 was targeting `origin/main` which was 6 commits behind local `main`, so the PR included those 6 prior-session commits alongside the Step 2 work. Fixed by fast-forward pushing `main` to `origin/main` (user verified the graph was clean: `main..origin/main` was empty).

**P3 body (overstated result):** PR body said "Reduces avoidable sandbox-friction escalations from ~11 to near-zero" but no live smoke had run. Changed to "Expected to reduce...pending smoke."

**P3 code comment (skip condition bug):** The unreadable `.git` test used `Path("/").stat().st_uid == 0` as the skip condition, which checks if root owns `/` (always true on POSIX), not whether the current process is root. Changed to `os.geteuid() == 0`.

Applied all four fixes in review cycle 1 commit. Verified: 29 tests passed, PR narrowed to 2 commits / 3 files after the `main` push.

The user then submitted a second review finding a residual issue in the P1 fix:

**Residual P2 (sibling worktree gitdir access):** The `.git/worktrees/` structural check alone accepted any sibling worktree gitdir. A compromised worker could rewrite `.git` to point at a sibling's gitdir, gaining read access to that sibling's metadata on the next decide turn. The reviewer suggested three mitigations — minimum component after `worktrees`, round-trip back-pointer validation, or immutable gitdir capture at worktree creation time.

Verified the attack vector: confirmed that `_execute_live_turn` is called for both `start` and `decide` flows, and the policy is rebuilt per-turn at `delegation_controller.py:1370`. Also verified the git worktree bidirectional pointer structure on live delegation worktrees — the gitdir's `gitdir` file contains an absolute path back to the worktree's `.git` file.

Implemented two-layer defense:
1. Structural: require at least 3 components (`.git/worktrees/<name>`, not just `.git/worktrees/`)
2. Round-trip: read the gitdir's `gitdir` back-pointer file and verify it resolves to this worktree's `.git` file

Created `_make_worktree_gitdir` test helper to build realistic bidirectional pointer pairs. Added tests for the attack scenario (sibling worktree rewrite rejected), `.git/worktrees` directory itself rejected, and missing back-pointer rejected. Integration test: policy excludes gitdir when sibling pointer detected.

Review cycle 2 passed clean — 33 tests passing, no new findings. PR #127 is 3 commits / 3 files, review-clean.

## Decisions

### Subdirectory carve-outs for `~/.agents/` instead of full directory

**Choice:** Grant `~/.agents/skills` and `~/.agents/plugins` as separate `readableRoots` entries, not `~/.agents/` as a whole.

**Driver:** Ultraplan refinement — narrowing to subdirectories matches the `~/.codex/` carve-out model and prevents silent read-access expansion if `~/.agents/` later gains credential files.

**Rejected alternatives:**
- **Full `~/.agents/` directory** — the original session decision. Rejected by the Ultraplan refinement because it doesn't match the narrow carve-out model used for `~/.codex/`. The prior session verified `~/.agents/` has no credential files today, but a blanket grant has no future-proofing.

**Implication:** If Codex adds new data under `~/.agents/` (e.g., `~/.agents/sessions/`), a new explicit carve-out is needed. This is safer than silent inclusion.

**Trade-offs accepted:** Slightly more code (two entries instead of one). Negligible maintenance cost.

**Confidence:** High (E2) — verified directory contents directly in the prior session. Plan refinement is a defensible tightening.

**Reversibility:** High — add or remove `readableRoots` entries.

**Change trigger:** If `~/.agents/` gains credential-class files, the subdirectory carve-out is already correct. If it gains many benign subdirectories, reconsider full-directory grant.

### Two-layer gitdir validation (structural + round-trip)

**Choice:** Validate the gitdir target with both structural path checking (`.git/worktrees/<name>` components) and round-trip back-pointer verification (read `gitdir` file in the resolved directory, confirm it points back to this worktree's `.git`).

**Driver:** Code review P1/residual P2 findings. The structural check alone accepted sibling worktree gitdirs. The round-trip check uses git's own bidirectional pointer mechanism — the same mechanism `git worktree prune` uses to validate worktree integrity.

**Rejected alternatives:**
- **Structural check only** — the initial P1 fix. Rejected because it accepted sibling worktree gitdirs (residual P2 finding, confidence 0.86).
- **Immutable gitdir capture at worktree creation time** — architecturally cleanest (resolve gitdir once before worker execution, pass immutably into policy builder). Rejected because it requires changing `build_workspace_write_sandbox_policy`'s signature and the `delegation_controller.py:1370` call site. The round-trip validation achieves the same security goal without API changes.
- **No validation (original implementation)** — rejected because of the sandbox boundary bypass: writable worktree + trusted `.git` content = arbitrary read access on next turn.

**Implication:** The gitdir resolution now requires the target directory to exist on disk and contain a `gitdir` back-pointer file. Graceful degradation: if either check fails, the carve-out is omitted (same as current behavior without Option E).

**Trade-offs accepted:** One additional filesystem read per turn (reading the back-pointer file). Negligible — the policy builder already reads the `.git` file. The round-trip also fails if the gitdir directory doesn't exist yet (unlikely since the policy builder runs after worktree creation at `delegation_controller.py:1370`).

**Confidence:** High (E2) — verified round-trip structure on live delegation worktrees (`worktree3`'s gitdir contains a `gitdir` file pointing back to the worktree's `.git`). Attack scenario tested and confirmed rejected.

**Reversibility:** High — remove the round-trip check if it causes issues. The structural check remains as first-layer defense.

**Change trigger:** If git changes the worktree bidirectional pointer format (extremely unlikely — it's a core git mechanism). If the round-trip read causes latency issues at scale (measure before worrying).

### Push 6 prior-session commits to origin/main

**Choice:** Fast-forward push local `main` (6 commits ahead) to `origin/main` to fix PR #127's scope.

**Driver:** Code review P2 finding — PR included 6 prior-session commits because `origin/main` was behind local `main`. User verified the graph: `main..origin/main` was empty, so a clean fast-forward was safe.

**Rejected alternatives:**
- **Rebase the feature branch** — would achieve the same PR narrowing but leaves `origin/main` stale. The 6 commits are all reviewed and committed work from prior sessions.
- **Leave PR scope as-is** — rejected because reviewers would see unrelated historical work under a sandbox-carve-outs title.

**Implication:** `origin/main` is now at `7cf29f78`. PR #127 correctly shows only the Step 2 delta (3 commits / 3 files).

**Trade-offs accepted:** None — clean fast-forward with no divergence.

**Confidence:** High (E2) — user verified graph topology before approving.

**Reversibility:** Low (pushed commits are now on remote), but there's no reason to reverse.

**Change trigger:** None.

## Changes

### `runtime.py` — `_resolve_worktree_gitdir()` helper and policy builder update

**Purpose:** Add gitdir resolution helper and extend `build_workspace_write_sandbox_policy()` with three new `readableRoots` categories.

**Changes made:**
- New `_resolve_worktree_gitdir(worktree_path: Path) -> str | None` helper at `runtime.py:27-62`
  - Reads `.git` pointer file, validates `gitdir:` prefix, resolves absolute/relative paths
  - Structural check: resolved path must contain `.git/worktrees/<name>` components
  - Round-trip check: reads back-pointer from `<gitdir>/gitdir`, verifies it resolves to this worktree's `.git`
  - Returns `None` on any failure (graceful degradation)
- `build_workspace_write_sandbox_policy()` updated at `runtime.py:65-109`:
  - `readableRoots` expanded from `[str(resolved)]` to a 5-entry list + optional gitdir
  - Static entries: worktree, `~/.codex/memories`, `~/.codex/plugins/cache`, `~/.agents/skills`, `~/.agents/plugins`
  - Dynamic entry: gitdir from `_resolve_worktree_gitdir()` (appended if not None)
  - Docstring updated with Phase 1 grant categories

### `test_runtime.py` — regression assertion update and Option E tests

**Purpose:** Update regression assertion for new `readableRoots` shape and add comprehensive Option E coverage.

**Changes made:**
- Added `import os` and `_resolve_worktree_gitdir` import
- Regression test expects 5 static `readableRoots` entries (no gitdir since test worktree has no `.git` file)
- `_make_worktree_gitdir()` helper creates realistic bidirectional pointer pairs
- 10 helper-level tests: absolute pointer, relative pointer, outside `.git/worktrees/`, inside `.git/` but not `worktrees/`, `.git/worktrees` directory itself, sibling worktree attack, missing back-pointer, `.git` is directory, malformed, unreadable, missing
- 3 integration tests: policy includes gitdir when valid, excludes when outside worktrees, excludes when sibling pointer
- Skip condition fixed: `Path("/").stat().st_uid == 0` → `not hasattr(os, "geteuid") or os.geteuid() == 0`

### T-20260429-01 ticket — `~/.agents/` scope amendment

**Purpose:** Document the `~/.agents/` addition as Friction surface 1b before the implementation commit.

**Changes made:**
- Added "Friction surface 1b: `~/.agents/` reads" section between surfaces 1 and 2
- Includes scope amendment date, security boundary assessment, implementation reference, and metric treatment

## Codebase Knowledge

### Sandbox policy architecture (updated after implementation)

| Component | Location | Role |
|-----------|----------|------|
| Gitdir resolver | `runtime.py:27-62` | `_resolve_worktree_gitdir(worktree_path)` — two-layer validation (structural + round-trip) |
| Policy builder | `runtime.py:65-109` | `build_workspace_write_sandbox_policy(worktree_path)` — constructs sandbox dict with 5 static + 1 dynamic readableRoot |
| Policy consumer | `delegation_controller.py:1370` | Passes policy to `run_execution_turn()` at turn-dispatch time |
| Turn dispatch | `delegation_controller.py:946` | `_execute_live_turn()` — called for both start and decide flows |
| Worker runner | `worker_runner.py:63` | Calls `_execute_live_turn()` in a thread |
| Regression test | `test_runtime.py:175-195` | Exact dict equality with 5 static readableRoots |
| Test helper | `test_runtime.py:623-632` | `_make_worktree_gitdir()` — creates bidirectional pointer pairs |

### Updated sandbox policy shape

```python
{
    "type": "workspaceWrite",
    "writableRoots": [str(resolved)],
    "readOnlyAccess": {
        "type": "restricted",
        "readableRoots": [
            str(resolved),                          # worktree itself
            str(home / ".codex" / "memories"),       # Option B
            str(home / ".codex" / "plugins" / "cache"),  # Option B
            str(home / ".agents" / "skills"),        # scope amendment
            str(home / ".agents" / "plugins"),       # scope amendment
            # + optional gitdir from _resolve_worktree_gitdir()  # Option E
        ],
        "includePlatformDefaults": True,
    },
    "networkAccess": False,
    "excludeSlashTmp": True,
    "excludeTmpdirEnvVar": True,
}
```

### Git worktree bidirectional pointer structure

Verified on live delegation worktrees (`worktree3`):

```
Forward: worktree/.git → "gitdir: /repo/.git/worktrees/worktree3"
Back:    /repo/.git/worktrees/worktree3/gitdir → "/path/to/worktree/.git"
```

The round-trip validation exploits this standard git mechanism. `git worktree prune` uses the same back-pointer to detect orphaned worktrees.

### Policy rebuild timing

`build_workspace_write_sandbox_policy(worktree_path)` is called at `delegation_controller.py:1370` inside `_execute_live_turn()`. Per line 2445 comment: "Called by _execute_live_turn (used by both start and decide)." This means the policy is rebuilt for every turn, including decide turns — confirming the P1 attack vector where a rewritten `.git` file would affect the next decide turn's policy.

### Trust model for readableRoots

| Path | Source | Validation |
|------|--------|------------|
| Worktree | Plugin-controlled (created by delegation controller) | None needed — we created it |
| `~/.codex/memories` | Static, known-safe | None — narrowed from `~/.codex/` to avoid credentials |
| `~/.codex/plugins/cache` | Static, known-safe | None — narrowed from `~/.codex/` to avoid credentials |
| `~/.agents/skills` | Static, known-safe | None — verified no credentials in prior session |
| `~/.agents/plugins` | Static, known-safe | None — verified no credentials in prior session |
| Gitdir | **Untrusted** — read from writable worktree's `.git` file | Structural + round-trip validation |

### Test coverage map

| Test | Validates | Branch |
|------|-----------|--------|
| `test_resolve_worktree_gitdir_absolute_pointer` | Valid absolute .git pointer resolves | Happy path |
| `test_resolve_worktree_gitdir_relative_pointer` | Relative path resolved against worktree root | Happy path |
| `test_resolve_worktree_gitdir_none_when_outside_git_worktrees` | Arbitrary host path rejected | Security |
| `test_resolve_worktree_gitdir_none_when_git_but_not_worktrees` | .git/refs/heads rejected | Security |
| `test_resolve_worktree_gitdir_none_when_worktrees_dir_itself` | .git/worktrees/ (no name) rejected | Security |
| `test_resolve_worktree_gitdir_none_when_sibling_worktree` | Sibling worktree gitdir rejected | Security |
| `test_resolve_worktree_gitdir_none_when_back_pointer_missing` | Missing gitdir back-pointer rejected | Security |
| `test_resolve_worktree_gitdir_none_when_git_is_directory` | Real repo root (.git dir) rejected | Edge case |
| `test_resolve_worktree_gitdir_none_when_malformed` | Non-gitdir content rejected | Edge case |
| `test_resolve_worktree_gitdir_none_when_unreadable` | Permission error handled | Edge case |
| `test_resolve_worktree_gitdir_none_when_missing` | No .git file handled | Edge case |
| `test_policy_includes_gitdir_when_valid_git_pointer_present` | Policy adds gitdir to readableRoots | Integration |
| `test_policy_excludes_gitdir_when_pointer_outside_git_worktrees` | Policy omits invalid gitdir | Integration |
| `test_policy_excludes_gitdir_when_sibling_worktree_pointer` | Policy omits sibling gitdir | Integration |
| `test_policy_excludes_gitdir_when_no_git_pointer` | Policy has 5 static entries only | Integration |

## Context

### Roadmap position

| Step | Status | Description |
|------|--------|-------------|
| 0 | Complete | Roadmap cleanup — docs-only reconciliation |
| 1 | Complete + closed | Reply extraction fallback (implementation + ticket closure) |
| 2 | **PR #127 open, review-clean** | T-20260429-01 Phase 1 sandbox carve-outs |
| 3 | Not started | T-20260429-02 unsupported request classification |
| 4 | Not started | Carry-forward debt sweep (TT.1, RT.1, P1-MINOR-SWEEP) |
| 5 | Not started | BMARK-L1-L3 disposition |
| 6 | Not started | AUDIT-CONSUMER-INTERFACE specification or deferral |

### Commit topology

| Commit | Content | Location |
|--------|---------|----------|
| `d1f9ed06` | Review cycle 2: round-trip gitdir validation | `feature/step-2-sandbox-carve-outs` (pushed) |
| `39d6c109` | Review cycle 1: structural check + skip condition fix | `feature/step-2-sandbox-carve-outs` (pushed) |
| `4ed10fc9` | Initial implementation: Options B + E + `~/.agents/` | `feature/step-2-sandbox-carve-outs` (pushed) |
| `7cf29f78` | Prior session: T-20260416-01 closure | `main` (pushed to origin) |

### PR #127 state

- **URL:** https://github.com/jpsweeney97/claude-code-tool-dev/pull/127
- **Scope:** 3 commits / 3 files against `main`
- **Status:** Review-clean after 2 review cycles (4 original findings + 1 residual, all addressed)
- **Remaining:** Live smoke + credential-boundary security probes (follow-up, not blocking PR)

## Learnings

### Writable worktrees require validation of any data read from them for trust decisions

**Mechanism:** The sandbox policy grants `writableRoots` access to the worktree, meaning the sandboxed process can modify files inside it — including `.git`. If the policy builder reads a file from the worktree and uses it to expand `readableRoots`, that's an untrusted input widening a trust boundary. The `.git` file is the specific vector, but the principle applies to any worktree content used for policy decisions.

**Evidence:** P1 code review finding: "an execution turn can rewrite `.git` to point at an arbitrary host path and the next turn will receive read access there." Confirmed by tracing `_execute_live_turn` at `delegation_controller.py:946` — policy rebuilt per-turn for both start and decide.

**Implication:** Any future sandbox policy expansion that reads from the worktree must validate the read content against a trusted source or structural constraint. The round-trip pattern (verify bidirectional pointer) is one approach; the immutable-capture pattern (resolve once before worker gets write access) is another.

**Watch for:** Future `readableRoots` entries derived from worktree content.

### Git worktree bidirectional pointers provide a built-in trust anchor

**Mechanism:** Every git worktree has a bidirectional link: worktree's `.git` file points to the gitdir, and the gitdir's `gitdir` file points back to the worktree's `.git`. This is how `git worktree prune` detects orphaned worktrees. The round-trip can be used as a trust check — a rewritten `.git` file will point to a gitdir whose back-pointer doesn't match.

**Evidence:** Verified on live delegation worktree `worktree3`: `cat .git` shows `gitdir: .../.git/worktrees/worktree3`, and `cat .../.git/worktrees/worktree3/gitdir` shows the path back to the worktree's `.git`.

**Implication:** This is a reusable validation pattern for any code that trusts worktree `.git` content. The back-pointer is maintained by git itself and is reliable.

**Watch for:** Non-standard git configurations where the back-pointer format differs (not observed in practice).

### `Path("/").stat().st_uid` is not a root-user check

**Mechanism:** `Path("/").stat().st_uid` returns the owner UID of the root filesystem directory (always 0 on POSIX). This is unrelated to whether the current process is running as root. `os.geteuid()` returns the effective user ID of the current process.

**Evidence:** `python3 -c "from pathlib import Path; print(Path('/').stat().st_uid)"` returns `0` regardless of who runs it. The test was always skipping because the condition was always true.

**Implication:** Use `os.geteuid() == 0` for "am I root?" checks. `not hasattr(os, "geteuid") or os.geteuid() == 0` handles non-POSIX platforms.

**Watch for:** Similar patterns in other test skip conditions.

## Next Steps

### 1. Merge PR #127

**Dependencies:** None — review-clean after 2 cycles.

**What to do:** Merge PR #127 via GitHub. The feature branch `feature/step-2-sandbox-carve-outs` can be deleted after merge.

**Approach:** `gh pr merge 127 --merge --delete-branch` or merge via GitHub UI.

### 2. Live smoke and security probes (post-merge)

**Dependencies:** PR #127 merged to `main`. App Server access available.

**What to read first:** T-01 security probe pattern at `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md:1168-1260`. `/delegate` SKILL.md for operator flow.

**Approach:** Three-commit pattern: (1) implementation already landed (PR #127), (2) live smoke + credential-boundary probes as evidence artifact, (3) ticket/register closeout if smoke passes.

**Acceptance criteria:**
- Avoidable sandbox-friction escalations <=2 in a comparable small-edit smoke
- Credential boundary preserved: `~/.codex/auth.json` and `~/.codex/config.toml` remain BLOCKED
- `~/.agents/plugins` content audit at probe time (verify no credential drift)
- `file_change` opacity counted separately (upstream limitation, not avoidable friction)

### 3. Ticket/register closeout (post-smoke)

**Dependencies:** Smoke passes acceptance criteria.

**What to do:** Update T-20260429-01 AC checkboxes, update reconciliation register, update current-state watchpoints. Ticket closure is a 3-surface operation (learning from T-20260416-01 closure).

### 4. Continue to Step 3 (T-20260429-02)

**Dependencies:** Step 2 fully closed.

**What to read first:** The reconciliation register for Step 3 priority and scope.

## In Progress

Clean stopping point. PR #127 is pushed, review-clean, and ready to merge. No work in flight. The feature branch `feature/step-2-sandbox-carve-outs` is at `d1f9ed06` on both local and remote.

## Open Questions

### Should the 5 non-codex closed tickets in `docs/tickets/` root be moved?

Carried from three prior handoffs. After D-05, `docs/tickets/` root still has 5 non-codex closed tickets (T-010, T-20260319-01, T-20260403-01, T-20260410-03, T-20260410-04). Separate general hygiene, not codex-collaboration work.

### When should the older handoff be addressed?

There is still an older handoff in `docs/handoffs/` (`2026-04-29_19-22_t16-protocol-revision-schema-delta-audit-reachability-ticket.md`) from a separate topic. It was not loaded this session.

## Risks

### Live smoke may reveal additional friction sources

The implementation covers Option B, `~/.agents/`, and Option E based on the T-01 smoke analysis. If Codex's execution patterns have changed between `0.117.0` and `0.128.0`, new read paths may trigger escalations not predicted by the T-01 evidence. The acceptance criterion (<=2 avoidable) provides tolerance.

### Round-trip validation adds a filesystem read per turn

The `_resolve_worktree_gitdir` helper now reads two files per invocation: the worktree's `.git` file and the gitdir's `gitdir` back-pointer file. At delegation scale (single worktree, single-digit turns per job), this is negligible. At higher scale, measure before worrying.

## References

- **PR #127:** https://github.com/jpsweeney97/claude-code-tool-dev/pull/127
- **T-20260429-01 (friction ticket):** `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md`
- **Step 2 plan:** `docs/plans/2026-04-30-step-2-sandbox-carve-outs-options-b-e-agents.md`
- **Sandbox policy builder:** `packages/plugins/codex-collaboration/server/runtime.py:27-109`
- **Gitdir resolver:** `packages/plugins/codex-collaboration/server/runtime.py:27-62`
- **Policy call site:** `packages/plugins/codex-collaboration/server/delegation_controller.py:1370`
- **Turn dispatch:** `packages/plugins/codex-collaboration/server/delegation_controller.py:946`
- **Regression test:** `packages/plugins/codex-collaboration/tests/test_runtime.py:175-195`
- **Option E tests:** `packages/plugins/codex-collaboration/tests/test_runtime.py:616-755`
- **Test helper:** `packages/plugins/codex-collaboration/tests/test_runtime.py:623-632`
- **T-01 diagnostic (probe pattern):** `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md`
- **Prior handoff:** `docs/handoffs/archive/2026-04-30_21-04_t-20260416-01-closure-and-step-2-plan.md`
- **Reconciliation register:** `docs/status/codex-collaboration-reconciliation-register.md`
- **Current-state document:** `docs/status/codex-collaboration-current-state.md`

## Gotchas

### The `.git` file in a worktree is writable and must not be trusted blindly

The worktree has `writableRoots` access, so the sandboxed Codex process can rewrite `.git`. Any policy decision based on `.git` content is using untrusted input. The two-layer validation (structural `.git/worktrees/<name>` check + round-trip back-pointer verification) is the current defense. If a future feature reads other files from the worktree for policy decisions, the same trust principle applies.

### Ticket closure is a 3-surface operation

Reinforced from prior session: closing a codex-collaboration ticket requires updating (1) the ticket itself, (2) the reconciliation register, (3) the current-state watchpoints. Missing any one creates drift visible to the next executor.

### `origin/main` was 6 commits behind local `main`

The 6 prior-session commits (Steps 0-1, T-20260416-01 closure) had not been pushed to `origin/main`. This caused PR #127 to include those commits in its diff. Fixed by fast-forward push of `main` to `origin/main` before finalizing the PR.

### Skip conditions for permission-based tests

`Path("/").stat().st_uid == 0` does NOT check if the process is root — it checks if root owns `/` (always true). Use `os.geteuid() == 0` instead. This caused the unreadable `.git` test to silently skip on every run.

## Conversation Highlights

**On Ultraplan refinement of `~/.agents/` scope:**
User did not explicitly comment on the subdirectory narrowing — it was accepted as part of the refined plan. The prior session decision was full-directory; Ultraplan narrowed to subdirectories to match the carve-out model.

**On PR scope (P2 finding):**
User: "Since `origin/main` is a strict ancestor of local `main` and there is no divergence, pushing local `main` is the right fix for P2." Provided the verified graph topology and the exact command (`git push origin main:main`).

**On the residual sibling worktree finding:**
User: "The four original findings are verified as addressed, but I would not merge yet until this residual trust-boundary hole is tightened."

**On review completion:**
User: "I'd consider PR #127 review-clean from the code-review findings we've been tracking. Remaining Step 2 work is the already-declared follow-up: live `/delegate` smoke, credential-boundary/security probes, and ticket/register closeout evidence."

## User Preferences

**Code review thoroughness (reinforced):** The user reviews at max effort with follow-up cycles. The first review found 4 findings (P1 security, P2 scope, P3 body, P3 code). The second review found a residual issue in the P1 fix. Each review included verification evidence (targeted tests, `git diff --check`, PR metadata inspection).

**Trust-boundary rigor:** The user will not merge until security findings are fully resolved. The residual sibling-worktree access concern (confidence 0.86) was treated as blocking despite being lower severity than the original P1.

**PR hygiene:** The user expects PRs to be cleanly scoped — a "Step 2" PR should contain only Step 2 work. Including unrelated prior commits is a finding even if the commits are themselves clean.

**Evidence-based review process:** The user provides structured findings with file references, line numbers, confidence ratings, and explicit "What Looks Solid" / "Verification Performed" sections. Corrections include specific remediation suggestions (e.g., "at minimum require a component after `worktrees`; stronger is to read the target gitdir's `gitdir` back-pointer").

**Graph verification before push:** The user verifies the git graph topology before approving push operations: "Current verified graph: origin/main: `11207241`, local main: `7cf29f78`, `origin/main..main`: exactly the six prior-session commits, `main..origin/main`: empty."
