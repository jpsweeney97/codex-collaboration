# Codex Collaboration Debt Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `docs/audits/2026-05-15-codex-collaboration-debt.md` into a sequenced repair lane that removes the sprint-sized debt first, then adds the contract and transport gates needed before Codex CLI upgrade work.

**Architecture:** Execute in small, independently reviewable slices. Quick wins land first only where they do not mask the larger Codex App Server contract risk; test-loop speed work precedes new contract coverage; strategic items become tracked decisions, tickets, or watch triggers rather than drive-by implementation.

**Tech Stack:** Python 3.11+, pytest, ruff, JSON Schema fixtures under `tests/fixtures/codex-app-server/0.117.0/`, Claude Code plugin hooks, Codex App Server JSON-RPC, Markdown specs/status docs.

---

## Current Anchors

- Repo: `/Users/jp/Projects/active/codex-collaboration`
- Audit source: `docs/audits/2026-05-15-codex-collaboration-debt.md`
- Audit revision this plan was built against: commit `46e8750` "docs(audit): eighth cross-model review — QW4 enforcement-path correction". **Provenance caveat:** the on-disk audit body's last revision footer is the *seventh* cross-model review; the eighth-review QW4 enforcement-path correction is in the commit but may not have its own footer line. Before Task 5 (QW4), the executor must re-read the audit's QW4 section and confirm it matches commit `46e8750` content, not an earlier shape. This re-confirmation is only executable because the Audit Publication Gate puts the audit *and commit `46e8750` itself* on `main` via a non-squash PR merge commit, so `git show 46e8750:docs/audits/...` resolves on the Phase 2 branch; without that gate the caveat is unverifiable.
- Current branch at plan creation: `chore/tech-debt-audit`
- Current HEAD at plan creation: `46e8750`
- **Audit publication state (verified at plan revision):** the audit and its nine `docs(audit)` cross-model-review commits (`e7b551b`..`46e8750`) live **only on `chore/tech-debt-audit`**. `origin/main` is at `536a529`; `46e8750` is **not** an ancestor of `main`; `docs/audits/2026-05-15-codex-collaboration-debt.md` is **absent from `main`**. The only delta `chore/tech-debt-audit` carries over `main` is that audit file (+180) plus `.gitignore` (+3, the `.tech-debt-audit-workspace/` ignore). The audit is a durable owning artifact — every reconciliation-register/spec row this plan adds names it as the owning artifact — so it MUST reach `main` with its revision provenance intact **before** any phase branch (created from `main`) references it. See the new "Audit Publication Gate".
- Existing plan pattern: `docs/superpowers/plans/2026-05-13-f4-audit-retention-implementation.md`
- Test baseline advertised by repo docs: `uv run pytest tests -q` and `uv run ruff check .`
- Suite-mode caveat: after Phase 3 lands HL2 (Task 7), a bare `uv run pytest tests -q` is a *fast-only* run, not a full-suite run. See "Suite Mode After HL2" below.

## Execution Shape

Structure: **risk-tiered (decision D)**. Branch protection on `main` is *not* platform-enforced (private repo, no GitHub Pro — verified via `gh api …/branches/main/protection` → 403), so PR count is pure self-imposed discipline; this plan right-sizes it to the regression risk of each slice rather than to task count. Per-task commits remain the review/revert unit; PRs are the CI-integration unit. Every work branch uses a repo-approved prefix (`chore/*`) and is created from current `main` after the plan file is on `main`.

**Audit landing (PR with merge commit):** the audit branch lands on `main` via a **pull request merged with a merge commit, squash disabled** (Audit Publication Gate). `allow_merge_commit: true` is confirmed on the remote, so the PR preserves the nine-commit provenance identically to a local `--no-ff` while giving the audit the same real CI gate as every work phase — conforming to AGENTS.md's "no direct commits to `main`" and to this plan's own rule that "PRs are the CI-integration unit", with zero convention-exception debt. Squash and rebase are forbidden for this PR (they flatten/rewrite the nine-revision provenance).

0. `chore/debt-plan-publication` — publish this plan file to `main` (one small PR; plan file only, no source/status work). The audit must be on `main` first (every register row names it as owning artifact).
1. `chore/debt-low-risk-batch` — **Tasks 1–6**: QW1, QW2, QW5, QW6, QW7, QW8, QW9 (Tasks 1–4) **plus** QW3 rollback-audit and QW4 startup-preflight (Tasks 5–6). All small, well-bounded docs/test/additive-operational changes; each task is its own commit. One PR.
2. `chore/debt-fast-suite` — **Task 7**: HL2. Isolated on its own PR because it changes the repo-wide default test invocation (`addopts`), CI, and the verification docs — a genuinely revert-worthy boundary.
3. `chore/debt-wire-contract` — **Tasks 8–9**: HL5 then HL1. Isolated: this is the audit's strongest systemic-risk cluster (Codex wire contract) and HL1 is the contract gate every later Codex item depends on.
4. `chore/debt-codex-cluster` — **Tasks 10–13**: ST2 tracking (Task 10), HL3 handler extraction (Task 11), HL4 store hygiene (Task 12), ST1/ST3/WL strategic+watch rows (Task 13). HL3/HL4 are behavior-preserving and lower-regression-risk than HL1. If Phase 3 closes fully green, HL1 is fully locked on `main`; if it closes degraded under Task 9 Step 6a, Phase 4 proceeds only on the narrower `_build_response_payload` mapper-invariant basis and ST2 execution remains blocked. The rest is tracking docs. One PR, per-task commits.

So: 1 audit-publication PR + 1 plan-publication PR + 4 work PRs, down from the earlier ten PR-equivalents. **Phase boundaries (branch + PR + close gate) occur only after Task 6, Task 7, and Task 9**; every other task-to-task transition is linear on the same branch within a phase.

Do not split Phase 1, 3, or 4 into more branches, and do not merge Phase 2 (HL2) into another phase: HL2's repo-wide default change must stay independently revertable.

**HL ordering — precise constraint.** The audit (debt audit, §"Sequence HL2 → HL1 → HL5", TR2) establishes exactly one **safety** ordering: **HL2 must precede both HL1 and HL5**, because HL2's fast/slow split is what stops new contract/transport coverage from making the already-slow loop worse. The audit's "→ HL1 → HL5" tail is a **leverage/severity** ordering (HL1 is P1 and unblocks the whole Codex-CLI cluster; HL5 is P2), explicitly *not* a safety or functional dependency — the audit states HL1 and HL5 are independent test-only additions. HL2 is Phase 2; HL1 and HL5 are both Phase 3, *after* HL2, and share an identical relationship to it (each is coverage added once the fast/slow split exists). Within Phase 3 this plan runs Task 8 (HL5) before Task 9 (HL1) purely as a **risk ordering**: HL5 is a small, self-contained transport-test addition; HL1 is the larger contract gate that also constrains the Phase 4 HL3 refactor — landing the cheap, low-risk slice first keeps the contract gate on its own clean commit. This is risk sequencing, not a dependency, and it violates neither the audit's HL2-first safety rationale nor its HL1-over-HL5 leverage ordering. Do not reorder HL2 relative to HL1/HL5.

**Scope honesty.** The audit's HL2 remediation names three components: fast/slow split, approval-window injection, and `pytest-xdist` parallelization. Task 7 implements the first two only; xdist is explicitly **deferred** and tracked as a Watch List row (Task 13), not silently dropped. HL2 is therefore reported as *partially closed* (loop ergonomics improved; whole-suite wall-time parallelization deferred), not closed. The audit's HL2-first premise still holds because the timeout-path injection is the part that makes HL1/HL5 cheap to add.

**Split-vs-injection — they target different tiers (read before Task 7).** Injection and the `slow` marker are *antagonistic*, not additive: `approval_window_seconds=0.5` makes a timeout test run in ~0.5s, so an injected test is *fast* and must stay in the default loop — marking it `slow` would wrongly exclude a fast test. The two tiers Task 7 produces are therefore disjoint: (1) **timeout-path tests** → made fast by the injection seam, **left unmarked**, run in the default loop; (2) the **inherently-slow live-runtime tier** (`tests/test_control_plane_live.py`, `tests/test_codex_compat_live.py` — currently `pytest.mark.skipif`-gated on `codex` presence, slow when `codex` *is* present and the skip does not fire) → carries `@pytest.mark.slow`, excluded from the default loop, run in CI via `-m ""`. The `slow` marker is the audit's "fast/slow split"; the injection is the audit's "approval-window injection." A `slow` marker that selects **zero** tests makes `addopts = "-m 'not slow'"` deselect the empty set (default loop ≡ full suite) and renders every `-m ""` distinction in this plan ceremony — Task 7 Step 5 hard-fails on that, and it is a Stop Condition.

## Mandatory Phase Gates

Every phase starts from `main`, ends before the next phase starts, and carries only the tasks listed in "Execution Shape". Within a phase, tasks proceed linearly on the same branch (Phase 1 runs Tasks 1→6 on `chore/debt-low-risk-batch`; Phase 4 runs Tasks 10→13 on `chore/debt-codex-cluster`). Do not continue across a *phase boundary* (after Task 6, Task 7, or Task 9) on the same branch — close the phase and start the next from `main`.

### Merge Model And Solo-Review Reality

This is a bus-factor-1 project (audit: "every commit on every ref is single-author") and `main` has **no platform-enforced branch protection** (private repo, no GitHub Pro — verified via `gh api …/branches/main/protection` → 403). The "protected-branch flow" is therefore a *self-imposed* convention, not an external control. This plan uses one audit-publication PR, one plan-publication PR, plus four work-phase PRs. There is no second human reviewer; the PR boundary's value is **not** second-party review but (a) a diff-sized self-review checkpoint against this plan's per-task acceptance text and (b) a clean-branch CI run. Treat each PR as a self-review + CI gate, not external sign-off. The audit PR gets the same treatment — it is no longer an exception.

Merge path: the maintainer self-merges each PR (no enforced gate exists to block this). Still do **not** bypass the self-imposed discipline — no `--no-verify`, no force-push, and do not merge a PR whose CI is red. The earlier "blocked if non-author review is hard-required" contingency no longer applies (verified: no such requirement exists); if branch protection is *later* enabled with a hard non-author-reviewer rule, re-surface it as a decision needed rather than working around it.

**Single-commit revert from a merged batch PR (the claimed revert unit, made executable).** Phase 1 merges 6 task commits and Phase 4 merges 4 in one `--no-ff` PR each. "Per-task commits are the revert unit" is only true if reverting one is actually specified, so: after a batch PR merges, each task is one commit on `main` reachable by its `git commit -m` subject. To back out exactly one task without unwinding the others, branch from `main` and `git revert <that-commit-sha>` (a new inverse commit — never history rewrite on the shared ref), then PR the revert. This is clean **only when the target commit does not have later commits in the same PR depending on it**; that is why Task 6 (the only Phase 1 trust-path/contract change) is pinned as the **last** commit in the Phase 1 sequence (Task 6 header) — reverting it touches nothing downstream. If a *non-last* batched commit ever needs reverting and later commits touched the same files, the revert is no longer isolated: treat that as a decision-needed, not a mechanical `git revert`. Do not use `--no-ff` PR squash for batch phases — squashing collapses the per-task commits and destroys this revert unit entirely (it is also why the audit merge forbids squash for a different reason: provenance).

Phase ordering: Phase 2 (HL2) must precede Phase 3 (HL1/HL5) — the audit's one hard safety ordering. Phase 4 depends on Phase 3. ST2 execution needs HL1 fully green; Task 10's tracking artifact may still land after a degraded Phase 3 close. HL3 must not share a diff with HL1's mapper, which is on `main` from Phase 3 either as a full HL1 close or as the explicitly narrower mapper-invariant guarantee described in Task 9 Step 6a. Phases 2→3→4 are strictly serialized.

**Phase 1 parallelism is bounded by the register dependency, not "independent".** Phase 1 is *code-independent* of Phases 2–4, but it is **not** file-independent: Task 2 (Phase 1) *restructures* `docs/status/reconciliation-register.md` — it renumbers the priority list and creates **two distinct anchors** (Task 2 Step 4): `## Audit-Owned Active Work` (open work, Exit-condition column) and `## Audit-Owned Deferred Watch Rows` (deferred rows, Watch-trigger column). The second is the watch-section anchor that Task 2 Step 5b, Task 7 Step 4b, Task 12, and Task 13 later append rows to — never the first. `reconciliation-register.md` is the single highest-traffic file in this plan (6 tasks edit it). Therefore: **Task 2 must be merged to `main` before any later register-touching task runs** (Task 7 Step 4b, Task 10 Step 2, Task 12 Step 4, Task 13). Phase 1 may run on a parallel branch at the maintainer's discretion **only** if it passes its own Phase Close Gate *and* lands on `main` before Phase 2's register-touching Task 7 Step 4b — otherwise the "add a watch row" steps have no anchor section and the lanes collide on merge. Register-append convention for every later task: every row this plan adds after Task 2 is a `deferred` watch row, so locate the `## Audit-Owned Deferred Watch Rows` header and append the row as the last line of **that** section's table (the only audit-active row, `DEBT-20260515`, is written once by Task 2 Step 4 and never appended to thereafter); never reflow, renumber, restructure, or append to `## Audit-Owned Active Work`. If the `## Audit-Owned Deferred Watch Rows` section is absent when a later task tries to append, **stop** — Task 2 has not landed; the parallelism bound was violated.

**Phase-count rationale (decision D — risk-tiered).** PR count tracks regression risk, not task count, because no enforced protection makes many PRs pure self-imposed latency on a solo project. Phase 1 batches six small, well-bounded changes (QW docs/test fixes + the two small additive fixes QW3/QW4) into one PR with per-task commits — commit-level revert is preserved without six PR round-trips. Phase 2 isolates HL2 alone because it changes the repo-wide default test invocation and must stay independently revertable. Phase 3 isolates the HL1/HL5 contract+transport cluster — the audit's strongest systemic risk and the gate every later Codex item depends on. Phase 4 batches the behavior-preserving HL3 refactor, the well-tested HL4 store hygiene, and the ST2/ST1/ST3/WL tracking rows; none is the top systemic risk (that is HL1, isolated in Phase 3) and HL3's mapper-coupling Stop Condition is satisfied only because the Phase 3 close semantics explicitly require either a fully green HL1 close or the narrower `_build_response_payload` mapper-invariant guarantee before Phase 4 proceeds. Collapsing Phase 1, 3, or 4 further, or merging Phase 2 into any other phase, is not authorized — the four boundaries are the risk-isolation mechanism.

### Suite Mode After HL2

Task 7 (HL2, **Phase 2**) adds `addopts = "-m 'not slow'"` to `pyproject.toml` **and** applies `@pytest.mark.slow` to the live-runtime tier (Step 3b) so the marker selects a **non-empty** set — see "Split-vs-injection" above. Consequence: **after Task 7, a bare `uv run pytest tests -q` excludes the `slow` live-runtime tests** — including within Phase 2 itself. (The marker-only variant is rejected as the *sole* mechanism because it does not speed the timeout loop; injection does that. The marker's job is the separate live-runtime split, not the timeout speedup.)

Binding rule for every gate and task that runs after Task 7:

- Any verification that claims a *full-suite* pass MUST invoke `uv run pytest tests -q -m ""`. This includes the Phase 2, 3, and 4 Close Gates, the Final Verification Gate, and any per-task verification whose Expected text says or implies "full suite".
- A bare `uv run pytest tests -q` after Task 7 is a fast-only run. It MUST NOT be reported as a full-suite pass in any phase commit message or PR body.
- **File-scoped per-task runs after Task 7 also inherit `addopts`.** The per-task `uv run pytest tests/<file> -q` invocations in Tasks 8–13 silently exclude `slow` tests in that file. This is *acceptable only because the `slow` tier is the two live-runtime modules* (`test_control_plane_live.py`, `test_codex_compat_live.py`), which no task in Phases 3–4 modifies or relies on for behavior-drift verification, and the Phase Close Gate's `-m ""` re-includes them. If any future task marks a non-live test `slow`, that task's per-file verification MUST add `-m ""` or the drift check is blind by construction.
- CI (`.github/workflows/ci.yml`) runs `uv run pytest tests -q -m ""` so CI's collection is **marker-inclusive** — the fast timeout-path tests are no longer deselected by `addopts`. Precision: `-m ""` defeats the `not slow` deselection so the `slow` live-runtime modules (`test_control_plane_live.py`, `test_codex_compat_live.py`) are *collected*, but they remain `pytest.mark.skipif(shutil.which("codex") is None)` and CI does not install `codex` — so CI **collects but skips** the live Codex contract; it does not execute it. The load-bearing effect of the CI change is keeping the unmarked fast timeout-path tests (the highest-risk coverage HL2 is about) in the run, not exercising the live tier. Verify this in Task 7 Step 4; if CI is not changed in the same commit that adds `addopts`, that is a Stop Condition.

### Audit Publication Gate

Run this **before** the Publication Gate. The audit (`docs/audits/2026-05-15-codex-collaboration-debt.md`) and its nine `docs(audit)` cross-model-review commits live only on `chore/tech-debt-audit` and are not on `main` (see "Current Anchors"). The audit is the owning artifact for every reconciliation-register and spec row this plan adds; it must reach `main` with its revision provenance intact before any phase branch references it. Land it via a **pull request merged with a merge commit (squash disabled)**. The merge-commit method is confirmed available on this remote (`allow_merge_commit: true`), so the PR preserves the nine-commit `e7b551b..46e8750` provenance identically to a local `--no-ff` merge **and** gives the audit the same real CI run every work phase gets — honoring this plan's own rule that "PRs are the CI-integration unit" instead of exempting the one write that most needs it. First verify the branch is exactly the audit delta:

```bash
git switch chore/tech-debt-audit
git rev-parse --short HEAD                       # expect 46e8750
git fetch origin
git log --oneline origin/main..chore/tech-debt-audit   # expect 9 docs(audit) commits, e7b551b..46e8750
git diff --stat origin/main...chore/tech-debt-audit    # expect ONLY the audit (+180) and .gitignore (+3)
```

If `git diff --stat` shows anything beyond the audit and the `.gitignore` line, **stop** — `chore/tech-debt-audit` is carrying unrelated work and is not a clean audit-PR candidate. The publication proof must compare against `origin/main` (the PR base), not a potentially stale local `main`.

Pushing the branch and opening the PR are themselves on the user's standing ask-before list (push / create PR / modify shared state). An agentic executor MUST present the intended sequence below and obtain explicit confirmation **before starting it**:

```bash
git switch chore/tech-debt-audit
git push -u origin chore/tech-debt-audit
gh pr create --base main --head chore/tech-debt-audit \
  --title "Land tech-debt audit (e7b551b..46e8750)" \
  --body "Publishes docs/audits/2026-05-15-codex-collaboration-debt.md with its nine docs(audit) cross-model-review commits — the owning artifact for every reconciliation-register/spec row in the debt-repair plan. MERGE WITH A MERGE COMMIT; do NOT squash or rebase (either flattens or rewrites the nine-revision provenance the plan's QW4/Task 13 Stop Conditions and the audit footer depend on)."
```

The `pull_request: branches: [main]` workflow in `.github/workflows/ci.yml` runs on the PR (`uv run pytest tests -q` — `addopts` is not on `main` yet, so this is a full-suite run — plus `ruff` and the JSON-config validation). Wait for it to be green. Then, **only after explicit maintainer confirmation that CI is green and the PR is approved to land** (Stop Condition):

```bash
gh pr checks chore/tech-debt-audit --watch        # CI must be green before merge
gh pr merge chore/tech-debt-audit --merge         # --merge = merge commit; NEVER --squash / --rebase
git fetch origin
git merge-base --is-ancestor 46e8750 origin/main && echo "audit provenance on origin/main"
```

Expected:

```text
PR CI green: full suite + ruff + JSON validation on the exact e7b551b..46e8750 commits.
PR merged with a MERGE COMMIT: 46e8750 is an ancestor of origin/main and the nine-commit e7b551b..46e8750 history is intact (no squash, no rebase).
```

`--merge` is mandatory; `--squash` and `--rebase` are forbidden — squash collapses the nine revisions into one and rebase rewrites their SHAs, and either breaks the `git show 46e8750:docs/audits/...` re-reads that the QW4 (Task 5) and Task 13 re-derivation Stop Conditions depend on. If the GitHub UI is used instead of `gh`, the maintainer MUST select "Create a merge commit", not "Squash and merge". If approval is not given, **stop** — do not merge and do not proceed to the plan-publication branch; the audit stays on its open PR until the maintainer decides.

**Post-merge red-`main` protocol (Stop Condition).** The PR's pre-merge CI is the real gate, so a red `main` is unlikely — but the merge also triggers the ungated `push: [main]` run of `ci.yml`. If that post-merge run is red:

- Known-flaky failure → re-run the job; a green re-run clears it.
- Otherwise do **not** leave `main` red and do **not** force-push or rewrite `main`. Open an immediate revert PR (`git revert -m 1 <merge-commit-sha>`; `-m 1` keeps `main`'s first-parent line) and land it the same merge-commit way; reattempt the audit landing only after the cause is fixed on a branch.
- Fix-forward instead of reverting **only** if the fix is small, obvious, and verified locally green within a few minutes; otherwise revert first and diagnose on a branch.
- Do not create the plan-publication branch or start any phase while `main` CI is red.

### Publication Gate

Use this gate **only after the Audit Publication Gate has merged the audit (with its `e7b551b..46e8750` history) to `main`**, before any implementation phase. The plan file is currently untracked on `chore/tech-debt-audit`; the publication branch is created from the post-audit-merge `main` (which now contains the audit):

```bash
git switch main
git pull --ff-only
git switch -c chore/debt-plan-publication
git add docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md
git commit -m "docs: plan codex collaboration debt repair"
```

Expected:

```text
The only staged path in the commit is docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md.
Local plan-publication commit created on branch `chore/debt-plan-publication`.
```

Pushing the branch, opening the PR, and merging it are themselves on the user's standing ask-before list (push / create PR / modify shared state). An agentic executor MUST present the intended sequence below and obtain explicit confirmation **before starting it**:

```bash
git push -u origin chore/debt-plan-publication
gh pr create --base main --head chore/debt-plan-publication \
  --title "docs: plan codex collaboration debt repair" \
  --body "Publishes docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md after the audit is already on main. Plan artifact only; no source or status mutations."
```

Then, **only after explicit maintainer confirmation that CI is green and the PR is approved to land**:

```bash
gh pr checks chore/debt-plan-publication --watch
gh pr merge chore/debt-plan-publication --merge
```

If approval is withheld at either stop, **stop** — do not push, do not merge, and do not begin implementation. After merge, run:

```bash
git switch main
git pull --ff-only
git ls-files --error-unmatch docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md
```

Expected:

```text
docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md
```

### Phase Start Gate

Before each phase branch, run the `main` verification and the exact branch creation command for that phase:

```bash
git switch main
git pull --ff-only
git ls-files --error-unmatch docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md
```

Then run exactly one branch creation command:

| Phase | Branch creation command |
|---|---|
| Phase 1 (Tasks 1–6) | `git switch -c chore/debt-low-risk-batch` |
| Phase 2 (Task 7) | `git switch -c chore/debt-fast-suite` |
| Phase 3 (Tasks 8–9) | `git switch -c chore/debt-wire-contract` |
| Phase 4 (Tasks 10–13) | `git switch -c chore/debt-codex-cluster` |

After the branch is created, run:

```bash
git merge-base --is-ancestor main HEAD
```

Expected:

```text
main fast-forwards cleanly.
The plan file path is printed.
The new phase branch is created from main.
git merge-base exits 0.
```

After the branch is created and before the phase's first TDD step, run the matching **API Pre-Flight** row below.

### API Pre-Flight (per phase, before any TDD loop)

This plan pastes literal "paste-this" test/impl code against private internal APIs. Those APIs were verified at plan-revision time (baselines below), but a later commit could move them. Before the first TDD step of any phase that touches code, run the phase's symbol pre-flight and confirm the baseline still holds. A mismatch is a **Stop Condition**: the pasted code is built on a stale assumption — reconcile the affected task's code against the live signature *before* writing the failing test, do not improvise mid-loop. Verifying an assumption inside the task that depends on it is circular; this gate exists so verification precedes the dependent code.

| Phase / Task | Pre-flight command | Baseline that must still hold |
|---|---|---|
| Phase 1 / Task 1 | `python -c "from pathlib import Path; import server.consultation_safety as m; print(Path('server/tool_prefix.py').exists(), '_TOOL_POLICY_MAP' in dir(m))"`; `rg -n "_TOOL_PREFIX" scripts/codex_guard.py` | `False True` — there is **no** dependency-light shared prefix module yet, `_TOOL_POLICY_MAP` already exists in `consultation_safety`, and `codex_guard.py:24` still defines the `_TOOL_PREFIX` literal. Task 1 must create the shared module without widening `codex_guard.py`'s startup dependency beyond that tiny module. |
| Phase 1 / Task 5 | `python -c "import inspect,server.control_plane as m; print('compat_checker' in inspect.signature(m.ControlPlane.__init__).parameters)"`; `rg -n "test_codex_status_invalidates_cached_runtime_on_compat_drift|module_from_spec|spec_from_file_location|def _patch_bootstrap_run" tests/test_control_plane.py tests/test_bootstrap.py` | `True` — `ControlPlane.__init__` accepts `compat_checker`, and `tests/test_control_plane.py::test_codex_status_invalidates_cached_runtime_on_compat_drift` proves the live checker is intentionally re-evaluated across status calls. Task 5 may add a startup preflight, but it must preserve that ongoing diagnostic behavior — do **not** freeze a startup result into `ControlPlane`. **And** `tests/test_bootstrap.py` still shows `_import_bootstrap()` building a fresh module via `module_from_spec()` on every call. Therefore Task 5's default-pass fixture must patch the same module instance each test later executes (for example by caching `_import_bootstrap()` per test); patching one throwaway module object is invalid. |
| Phase 2 / Task 7 | `rg -n "def _build_controller\|_APPROVAL_OPERATOR_WINDOW_SECONDS\|CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS" tests/test_delegation_controller.py server/delegation_controller.py` | `_build_controller` exists in the test module; `_APPROVAL_OPERATOR_WINDOW_SECONDS` is a module-level constant (`server/delegation_controller.py`) resolved **at import** by `_read_approval_operator_window_seconds()` from env var `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS` (default `900.0`). Task 7 Step 2 uses the resolved constant `_APPROVAL_OPERATOR_WINDOW_SECONDS` as the seam default — it does **not** reference the env-var name, so the env name is not load-bearing for the paste code. **Baseline corrected 2026-05-16: the prior text named a non-existent `CODEX_APPROVAL_WINDOW_SECONDS`. Every other Pre-Flight row in this table was re-verified against the live tree at the same time and holds as written; this row was the sole authoring miss.** |
| Phase 3 / Task 9 | `rg -n "def _build_response_payload" server/delegation_controller.py`; then `awk '/def _build_response_payload/,/^    def [a-z]/' server/delegation_controller.py \| rg -n "self\."` (expect **no output**); `rg -n "self\._repo_root\|self\._client\|def __init__\|JsonRpcClient" server/runtime.py` | `_build_response_payload` exists and reads **no `self.*`** (pure mapper — the HL1 `object.__new__` bypass and the Task 11/HL3 invariant both depend on this); `AppServerRuntimeSession.__init__` assigns exactly `_repo_root` and `_client` and eagerly constructs `JsonRpcClient(["codex","app-server"])`. |
| Phase 4 / Task 12 | `rg -n "_ensure_dialogue_controller\|_ensure_delegation_controller" server/mcp_server.py`; `rg -n "def cleanup" server/lineage_store.py server/turn_store.py`; `rg -n "_build_dialogue_factory\(|_build_delegation_factory\(" tests/test_bootstrap.py tests/test_delegate_start_integration.py tests/test_delegation_controller.py` | `McpServer._ensure_dialogue_controller` / `_ensure_delegation_controller` exist; `LineageStore.cleanup()` exists; `TurnStore` has **no** `cleanup()` yet (Task 12 adds it). Direct no-`store_cleanup` callers still exist in `tests/test_bootstrap.py`, `tests/test_delegate_start_integration.py`, and `tests/test_delegation_controller.py`; Task 12 must therefore preserve a no-`store_cleanup` call path (optional kwarg or explicit caller migration), not introduce a blind `TypeError`. |

If a baseline no longer holds (e.g., a later commit gave `_build_response_payload` a `self.*` dependency), stop and reconcile that task's pasted code against the live signature before writing the failing test. Phase 0 (plan publication) has no code and skips this gate; within Phase 4, Tasks 10 and 13 are tracking docs with no pre-flight row.

### Phase Close Gate

After the last task assigned to the phase, run the full-suite verification. **Phase 1 only** (Tasks 1–6, before Task 7 adds the marker split):

```bash
uv run pytest tests -q
uv run ruff check .
git status --short
```

**Phase 2 onward** (Task 7 adds `addopts = "-m 'not slow'"` *within* Phase 2, so even Phase 2's own close is marker-inclusive — a bare `pytest tests -q` here is fast-only and is not a valid full-suite gate, see "Suite Mode After HL2"):

```bash
uv run pytest tests -q -m ""
uv run ruff check .
git status --short
```

Pushing the current phase branch, opening the phase PR, and merging it are shared-state writes on the same standing ask-before list as the audit/publication PRs. An agentic executor MUST stop twice for **every** phase close: first before `git push` + PR creation, then again before the PR merge after CI is green.

Then, and only after explicit maintainer approval to start the remote-write sequence, push exactly the current phase branch:

| Phase | Push command |
|---|---|
| Phase 1 | `git push -u origin chore/debt-low-risk-batch` |
| Phase 2 | `git push -u origin chore/debt-fast-suite` |
| Phase 3 | `git push -u origin chore/debt-wire-contract` |
| Phase 4 | `git push -u origin chore/debt-codex-cluster` |

Expected:

```text
The full test suite passes (Phase 1: `pytest tests -q`; Phases 2–4: `pytest tests -q -m ""`).
Ruff passes.
git status shows only intentional branch-local changes before commit and is clean after the phase commit.
The phase branch is pushed and its PR is opened only after recorded maintainer approval.
```

Open the phase PR for that same branch (`gh pr create --base main --head <phase-branch>` or equivalent UI flow), let CI run, then stop again. Merge only after CI is green **and** the maintainer has explicitly approved landing that phase PR (see "Merge Model And Solo-Review Reality"), then re-enter the Phase Start Gate for the next phase. Phase 1's PR carries six task commits and Phase 4's carries four; that is intended — per-task commits are the review/revert unit. From Phase 2 onward, a phase that reports "full suite passes" while having run only a bare `pytest tests -q` (fast-only) is a defective close — re-run with `-m ""` before merging.

## Files And Responsibilities

- Modify `README.md`
  - Correct safety-substrate scope from three advisory tools to the actual content-bearing guarded set.
  - Expand concurrent-session limitation wording and recovery guidance.
- Create `docs/decisions/2026-05-16-security-hook-guard-extension.md`
  - ADR for commit `d4f38f7` extending the fail-closed guard to delegation surfaces.
- Modify `AGENTS.md`
  - Add a Workflow Notes maintenance rule requiring status doc updates when post-extraction project state changes.
- Modify `docs/status/current-state.md`
  - Refresh stale post-extraction current-state framing and header date.
- Modify `docs/status/reconciliation-register.md`
  - Refresh stale post-extraction register framing and add rows/tracking for debt items that become active backlog.
- Publish (land on `main`, before the plan) `docs/audits/2026-05-15-codex-collaboration-debt.md`
  - Land the audit via a **PR merged with a merge commit, squash disabled** (Audit Publication Gate), preserving the `e7b551b..46e8750` revision provenance and getting a real CI run, before any register/spec row names it as owning artifact.
- Track `docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md`
  - Publish via one small plan-publication PR *after* the audit is on `main`, before any register row references it.
- Modify `scripts/codex_guard.py`
  - Import or share the canonical MCP tool prefix instead of owning a duplicate literal.
- Modify `server/consultation_safety.py`
  - Export the canonical MCP tool prefix and build policy-map keys from it.
  - Document whether non-content-bearing delegate policies are forward-compatible by intent.
- Modify `tests/test_codex_guard.py`
  - Assert guard and policy-map prefix consistency directly.
- Modify `tests/test_hooks_coverage.py`
  - Keep matcher-to-policy coverage; add a direct prefix invariant if it belongs better here.
- Modify `tests/test_control_plane_live.py`
  - Change live repo root discovery from `parents[4]` to `parents[1]`.
- Modify `tests/test_delegation_controller.py`
  - Make bounded-poll failures show final job/request state.
  - Add `approval_window_seconds` test seam only in the HL2 phase.
- Modify `tests/test_resolution_registry_capture_ready.py`
  - Widen the late-timer sleep margin and add final state details to thread assertions.
- Modify `tests/test_resolution_registry_per_request.py`
  - Widen the late-timer sleep margin and add final state details to thread assertions.
- Modify `scripts/publish_session_id.py`
  - Emit a weak startup-overlap warning when a recent different `session_id` exists.
- Modify `tests/test_bootstrap.py`
  - Add SessionStart hook warning tests and bootstrap startup-compatibility tests.
- Modify `scripts/codex_runtime_bootstrap.py`
  - Invoke the existing shared Codex compatibility checker before `server.run()`.
- Modify `docs/specs/contracts.md`
  - Add a rollback audit-event action value.
- Modify `docs/specs/promotion-protocol.md`
  - Change rollback semantics from "no event emitted" to the emitted rollback event contract.
- Modify `server/delegation_controller.py`
  - Emit rollback audit events in live promotion and recovery rollback paths.
  - Later extract `_server_request_handler` after contract tests are in place.
- Modify `tests/test_jsonrpc_client.py`
  - Add real-subprocess transport tests for request/response, notification buffering, malformed stdout, and response-ID mismatch.
- Modify `tests/test_codex_wire_contract.py`
  - Add JSON Schema payload-shape tests for client requests and server-request responses.
- Modify `pyproject.toml`
  - Add `jsonschema` to the dev dependency group when HL1 lands.
  - Add pytest marker configuration and local default marker behavior when HL2 lands.
- Modify `.github/workflows/ci.yml`
  - Ensure CI still runs the full suite after any local default `addopts` marker split.
- Modify `.claude/CLAUDE.md` and `AGENTS.md`
  - When HL2 lands (Task 7), reconcile the documented verification command: a bare `uv run pytest tests -q` becomes the fast inner-loop run; `uv run pytest tests -q -m ""` is the full-suite completion gate. Both files currently hardcode the bare command and "1172 tests … ~4-5 minutes" as the completion gate.
- Modify `server/jsonrpc_client.py`
  - Only if HL5 tests expose a real behavioral bug.
- Modify `server/turn_store.py`
  - Add replay caching and `cleanup()`.
- Modify `server/lineage_store.py`
  - Either add cross-instance-safe invalidation or explicitly defer lineage caching while still handling cleanup ownership.
- Modify `scripts/codex_runtime_bootstrap.py`
  - Own session-store normal-exit cleanup when HL4b is closed; if this owner is not implemented, HL4b remains deferred.
- Modify `docs/specs/contracts.md`
  - Align the Lineage Store cleanup contract with the actual normal-exit and abnormal-exit retention owner.
- Modify `docs/specs/recovery-and-journal.md`
  - Document store cleanup/retention behavior and the current stance on unknown-terminal audit events.
- Modify `server/codex_compat.py`
  - Only during ST2 execution after HL1 passes: update version constants and fixtures as the tracked upgrade artifact requires.
- Modify `scripts/compare_app_server_schemas.py` and `scripts/regenerate_schema.sh`
  - Only during ST2 execution if the upgrade artifact requires fixture regeneration or report refresh.

## Stop Conditions

- Stop if `git status --short --branch` shows unrelated user changes in files this plan will touch. Re-read those files and adapt rather than overwrite.
- Stop if execution is still on `main`; create the phase branch first.
- Stop if an implementation phase starts before the publication PR for `chore/debt-plan-publication` has merged to `main`.
- Stop if a phase branch was not created from current `main`. Switch to `main`, fast-forward it, and create a new repo-conforming phase branch before implementation.
- Stop if `docs/status/reconciliation-register.md` references `docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md` while the plan file is untracked or absent from the branch. Publish the plan artifact first.
- Stop if a later register-touching task (Task 7 Step 4b, Task 10, Task 12, Task 13) is about to append a row while the `## Audit-Owned Deferred Watch Rows` section created by Task 2 Step 4 (or `## Audit-Owned Active Work`) is absent from the branch. Task 2 (Phase 1) has not landed on `main`; appending now dangles or collides. Land Task 2 first (see "Phase 1 parallelism is bounded by the register dependency").
- Stop if any reconciliation-register, spec, or status row this plan adds references `docs/audits/2026-05-15-codex-collaboration-debt.md` while the audit is absent from the branch or `46e8750` is not an ancestor of `main`. The Audit Publication Gate must merge the audit to `main` first; a register row whose owning artifact is not in the tree is a dangling-authority defect under this repo's authority model (`.claude/CLAUDE.md` "Authority").
- Stop if the plan-publication branch is created, or any implementation phase starts, before the Audit Publication Gate has merged `chore/tech-debt-audit` to `main`. The audit must precede the plan on `main`.
- Stop before any remote write in this plan (`git push`, `gh pr create`, or PR merge) until the maintainer has explicitly approved that exact remote-write sequence; then stop again before the merge until (a) the PR's CI is green and (b) the maintainer has explicitly approved landing it. This applies to the audit PR, the plan-publication PR, and every phase PR. An agentic executor that pushes, opens, or merges without recorded maintainer approval has violated this plan and the user's standing instruction.
- For the audit PR specifically, `--squash`/`--rebase` is itself a Stop Condition (destroys the nine-revision provenance). Use `gh pr merge chore/tech-debt-audit --merge` or the UI's "Create a merge commit" path only.
- Stop if the local audit source changes after this plan is created. Re-read `docs/audits/2026-05-15-codex-collaboration-debt.md` and reconcile deltas before continuing. (After the Audit Publication Gate, the audit is present on every phase branch because it is on `main`; if it is *not* present on a phase branch, the Audit Publication Gate was skipped — that is itself a Stop Condition, not a reason to proceed without the source.)
- Stop if `.tech-debt-audit-workspace/synthesis/report.md` is used as an authority source. The audit says that local file is superseded and contains rejected remediation shapes.
- Stop if a QW item starts pulling in the structural remainder that the audit explicitly split out: unknown-terminal audit events for QW3, or a cross-process promotion lock for QW5.
- Stop if HL1 starts validating only `turn/start` or invents a `command-respond` request method. HL1 has two real schema boundaries: client-request params and JSON-RPC response result payloads.
- Stop if HL2 changes `pyproject.toml` in a way that makes CI skip slow timeout-path tests.
- Stop if, after Task 7, `uv run pytest -m slow --co -q` collects **zero** tests, or the default `pytest tests --co` count equals the `pytest tests -q -m "" --co` count. Either means Step 3b was skipped and the `slow` marker is unpopulated: `addopts = "-m 'not slow'"` deselects the empty set, the default loop equals the full suite, and every `-m ""` gate, the "Suite Mode After HL2" rule, the `.claude/CLAUDE.md`/`AGENTS.md` reconciliation, and the HL2 partial-close claim become inert ceremony. Populate the marker (Step 3b) or, if no test is genuinely slow, remove the marker/`addopts`/CI/Suite-Mode apparatus entirely and deliver HL2 by injection alone with the Step 5 duration assertion as the sole speed evidence — do not ship the apparatus around an empty set.
- Stop if HL4a adds a per-instance `LineageStore` replay cache without mtime/size invalidation or a single shared instance. That is a correctness regression because dialogue and delegation use separate instances over the same file.
- Stop if ST2 changes Codex version pins before HL1 payload-shape tests exist and pass.
- Stop if any HL1 helper constructs `AppServerRuntimeSession(...)` via its real `__init__`. `__init__` eagerly spawns `JsonRpcClient(["codex","app-server"])`; constructing it in a test launches (or fails to launch) a real Codex subprocess before the stub is injected. HL1 session fixtures must bypass `__init__` with `object.__new__` and set `_repo_root` + `_client` directly (mirrors the `object.__new__(DelegationController)` pattern already used for the response-mapper test).
- Stop if the HL1 contract suite reports green while any schema test is `skipped` rather than executed. `vendored_schema_dir`/`schema_loader` skip on a missing fixture dir or file; a skipped contract test proves nothing. The HL1 commit must include the fixtures-present hard assertion and the negative-payload rejection test (Task 9 Steps 3a/4a); a phase close that shows the contract module skipped is a defective close.
- Stop if an HL1 payload fails validation against a vendored schema and the schema is correct. That is a real wire-contract bug, not a test problem. Do not weaken the schema or the assertion to go green; follow the Task 9 "real contract violation" contingency.
- Stop if the Task 11 (HL3) extraction gives `_build_response_payload` a `self.*` dependency, moves it onto the handler-state object, or changes its signature without updating `tests/test_codex_wire_contract.py`'s `object.__new__` construction in the same commit. The HL1 mapper bypass depends on that method staying a pure self-free mapper.
- Stop if any audit-derived content this plan transcribes into a paste block (the `DEBT-20260515` row, WL1–WL6 triggers, HL/QW disposition text, the ST2/ST3 ticket bodies) has not been confirmed against `git show 46e8750:docs/audits/2026-05-15-codex-collaboration-debt.md` before its commit. The QW4 footer-vs-body desync this plan documents proves the audit's content can drift from a transcription; the repo Authority model (`.claude/CLAUDE.md`) makes the audit the owning artifact, so the plan must not become the de facto source for these values. Re-derive each row's load-bearing figures (e.g. WL1's "15/28 importers" / "~800 LOC", WL4's "10 MB", the HL2/HL4a partial-close wording) from the pinned commit at transcription time; if the audit text differs from this plan's paste block, the audit wins — reconcile the paste block, do not ship the stale plan value.
- Stop before Task 5 (QW4) if the audit's QW4 section on disk cannot be confirmed to match commit `46e8750`'s eighth-review enforcement-path correction. Reconcile against the pinned commit, not an earlier audit shape. This re-read is only possible because the Audit Publication Gate landed the audit (and commit `46e8750` itself) on `main`, hence on the Phase 1 branch (Task 5 = QW4 is in Phase 1 under decision D) — `git show 46e8750:docs/audits/2026-05-15-codex-collaboration-debt.md` resolves. If `docs/audits/2026-05-15-codex-collaboration-debt.md` is absent on the Phase 1 branch, stop: the Audit Publication Gate was skipped; do not proceed against an unverifiable QW4 shape.
- Stop if branch protection is *later* enabled on `main` with a hard non-author-reviewer requirement and no admin self-merge path. Verified at plan revision: `main` has **no** platform-enforced protection (private repo, no GitHub Pro), so the four work PRs self-merge without a blocker; this condition only fires if that changes. If it does, surface it as a decision needed rather than bypassing protection.

---

### Task 0: Publish The Audit And Plan, Establish Branch Boundaries

**Files:**
- Read: `docs/audits/2026-05-15-codex-collaboration-debt.md`
- Read: `docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md`
- Read: `git status`
- Publish before the plan (Audit Publication Gate): `docs/audits/2026-05-15-codex-collaboration-debt.md` (PR `chore/tech-debt-audit` → `main`, merge commit, no squash/rebase)
- Track after the audit is on `main`: `docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md`

- [ ] **Step 1: Re-anchor on live state**

Run:

```bash
git status --short --branch
git rev-parse --short HEAD
git log --oneline -8
```

Expected:

```text
Current branch can be the planning branch; no implementation task starts from it.
No unexpected worktree edits exist in files named by the phase.
HEAD is `46e8750` on `chore/tech-debt-audit`; the audit and its `e7b551b..46e8750` history are NOT yet on `main`.
```

- [ ] **Step 1b: Run the Audit Publication Gate (land the audit on `main` first)**

The audit and its nine `docs(audit)` commits exist only on `chore/tech-debt-audit` (see "Current Anchors"). Run the **Audit Publication Gate exactly as written in that section** — do not inline an unattended push or merge here. That gate: (1) verifies the branch is exactly the audit delta, (2) **stops for explicit maintainer confirmation before** pushing the branch and opening the PR (both on the standing ask-before list), (3) lets the PR's CI run (the same full-suite + ruff + JSON-validation gate every work phase gets), (4) **stops again for explicit maintainer confirmation before `gh pr merge --merge`**, gated on green CI, and (5) merges with a merge commit (never squash/rebase) so the `e7b551b..46e8750` provenance survives, then runs the post-merge red-`main` protocol.

Do not duplicate or shortcut the gate's commands here; run the gate, including both mandatory confirmation Stops. Do not create the plan-publication branch until the audit is on `origin/main` via the merged PR *with maintainer approval recorded* and `main` CI is green. If approval is withheld or the audit is not on `main`, stop — every register row this plan adds would otherwise dangle.

- [ ] **Step 2: Create the plan-publication branch from `main` (audit already on `main`)**

Run:

```bash
git switch main
git pull --ff-only
git ls-files --error-unmatch docs/audits/2026-05-15-codex-collaboration-debt.md
git switch -c chore/debt-plan-publication
```

Expected:

```text
main fast-forwards cleanly.
The audit file path is printed (Step 1b landed it on `main` via the merged audit PR). If it is not printed, stop — the Audit Publication Gate was skipped.
Switched to a new branch 'chore/debt-plan-publication'
```

- [ ] **Step 3: Commit only the plan artifact**

```bash
git status --short
git add docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md
git commit -m "docs: plan codex collaboration debt repair"
```

Expected:

```text
git status shows the untracked plan file before git add.
Commit created with only docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md staged.
```

- [ ] **Step 4: Publish and merge the plan-publication branch before implementation**

Complete the Publication Gate's remote-write sequence exactly as written above. In particular, stop for explicit maintainer approval before `git push` + `gh pr create`, let CI run on the PR, then stop again for explicit maintainer approval before `gh pr merge --merge`. Do not begin Task 1 until the publication PR is merged.

- [ ] **Step 5: Verify `main` contains the plan**

Run:

```bash
git switch main
git pull --ff-only
git ls-files --error-unmatch docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md
```

Expected:

```text
The plan file path is printed.
```

- [ ] **Step 6: Create the Phase 1 branch**

Run:

```bash
git switch -c chore/debt-low-risk-batch
git merge-base --is-ancestor main HEAD
```

Expected:

```text
Switched to a new branch 'chore/debt-low-risk-batch'
git merge-base exits 0.
```

- [ ] **Step 7: Establish the relevant baseline**

For Phase 1:

```bash
uv run pytest tests/test_codex_guard.py tests/test_hooks_coverage.py tests/test_control_plane_live.py tests/test_resolution_registry_capture_ready.py tests/test_resolution_registry_per_request.py tests/test_bootstrap.py -q
uv run ruff check scripts/codex_guard.py scripts/publish_session_id.py server/consultation_safety.py tests/test_codex_guard.py tests/test_hooks_coverage.py tests/test_control_plane_live.py tests/test_resolution_registry_capture_ready.py tests/test_resolution_registry_per_request.py tests/test_bootstrap.py
```

Expected:

```text
Selected tests either pass or skip only live Codex checks because codex is absent.
Ruff passes for Python paths.
```

If a selected test fails before edits, stop and record it as a baseline failure in the phase notes.

---

### Task 1: Make The Tool-Prefix Safety Invariant Explicit

**Audit items:** QW6, Open Question 2.

Preserve the existing failure-containment boundary: non-plugin tools must still pass through **before** `codex_guard.py` imports scanner/policy code. The shared prefix constant therefore moves into a tiny dependency-light module, not into `consultation_safety.py`.

**Files:**
- Create: `server/tool_prefix.py`
- Modify: `server/consultation_safety.py`
- Modify: `scripts/codex_guard.py`
- Modify: `tests/test_codex_guard.py`
- Modify: `tests/test_hooks_coverage.py`

- [ ] **Step 1: Write the invariant tests and pass-through guard**

Add to `tests/test_codex_guard.py`:

```python
def test_guard_prefix_matches_policy_map_prefix() -> None:
    module = _load_guard_module()
    from server.consultation_safety import _TOOL_POLICY_MAP
    from server.tool_prefix import TOOL_PREFIX

    assert module._TOOL_PREFIX == TOOL_PREFIX
    assert all(tool_name.startswith(TOOL_PREFIX) for tool_name in _TOOL_POLICY_MAP)
```

Add this regression guard to `tests/test_codex_guard.py` in the same step. It is expected to stay GREEN before and after the implementation — its job is to prevent Task 1 from widening the hook's startup dependency:

```python
def test_non_plugin_tool_passes_through_without_policy_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_guard_module()
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/example.txt"},
            "session_id": "test-session",
        }
    )

    original_import = __import__

    def guarded_import(
        name: str,
        globals: object | None = None,
        locals: object | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        if name == "server.consultation_safety":
            raise ImportError("policy import should not run for non-plugin tools")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(module.sys, "stdin", io.StringIO(payload))
    monkeypatch.setattr("builtins.__import__", guarded_import)

    assert module.main() == 0
```

Add to `tests/test_hooks_coverage.py` (the snippet imports `_TOOL_POLICY_MAP` explicitly; the Phase 1 API Pre-Flight confirmed `_TOOL_POLICY_MAP` lives in `server.consultation_safety`. If `tests/test_hooks_coverage.py` already imports `_TOOL_POLICY_MAP` at module scope, use that existing binding and drop the local re-import rather than shadowing it):

```python
def test_policy_map_keys_share_one_mcp_prefix() -> None:
    from server.consultation_safety import _TOOL_POLICY_MAP
    from server.tool_prefix import TOOL_PREFIX

    unexpected = sorted(
        tool_name
        for tool_name in _TOOL_POLICY_MAP
        if not tool_name.startswith(TOOL_PREFIX)
    )
    assert unexpected == []
```

- [ ] **Step 2: Run the tests and confirm the failure**

Run:

```bash
uv run pytest tests/test_codex_guard.py::test_guard_prefix_matches_policy_map_prefix tests/test_codex_guard.py::test_non_plugin_tool_passes_through_without_policy_import tests/test_hooks_coverage.py::test_policy_map_keys_share_one_mcp_prefix -q
```

Expected:

```text
The two prefix-invariant tests are RED. The precise signal is an ImportError
(`ModuleNotFoundError: No module named 'server.tool_prefix'`) raised when the
test calls the import — pytest reports this as an ERROR, not an assertion
failure. That error IS the expected red for this TDD step; do not look for a
failed assertion here.
The non-plugin pass-through regression test stays GREEN pre-implementation:
current `codex_guard.py` already returns before importing policy code for
unrelated tools. If that test goes red, stop — Task 1 has already widened the
hook's blast radius before the shared-prefix refactor even starts.
```

- [ ] **Step 3: Create a dependency-light shared prefix module and use it**

Create `server/tool_prefix.py`:

```python
"""Dependency-light shared MCP tool prefix for guard fast-path checks."""

TOOL_PREFIX = "mcp__plugin_codex-collaboration_codex-collaboration__"
```

Keep this module free of `consultation_safety`, credential-scan, or other policy imports. `codex_guard.py` is allowed to import **only** this tiny module before the non-plugin pass-through branch.

In `server/consultation_safety.py`, import the constant and replace `_TOOL_POLICY_MAP` keys with f-strings:

```python
from .tool_prefix import TOOL_PREFIX
```

Then:

```python
_TOOL_POLICY_MAP: dict[str, ToolScanPolicy] = {
    f"{TOOL_PREFIX}codex.consult": CONSULT_POLICY,
    f"{TOOL_PREFIX}codex.dialogue.start": DIALOGUE_START_POLICY,
    f"{TOOL_PREFIX}codex.dialogue.reply": DIALOGUE_REPLY_POLICY,
    f"{TOOL_PREFIX}codex.delegate.start": DELEGATE_START_POLICY,
    f"{TOOL_PREFIX}codex.delegate.decide": DELEGATE_DECIDE_POLICY,
    f"{TOOL_PREFIX}codex.delegate.poll": DELEGATE_POLL_POLICY,
    f"{TOOL_PREFIX}codex.delegate.promote": DELEGATE_PROMOTE_POLICY,
    f"{TOOL_PREFIX}codex.delegate.discard": DELEGATE_DISCARD_POLICY,
}
```

In `scripts/codex_guard.py`, replace the literal `_TOOL_PREFIX` assignment with:

```python
from server.tool_prefix import TOOL_PREFIX as _TOOL_PREFIX
```

Place the import after the package-root `sys.path` insertion. Do **not** import `server.consultation_safety` at module import time — that would make unrelated tools depend on the scanner module importing cleanly and would violate the existing pass-through-before-policy-import contract.

- [ ] **Step 4: Document the over-declared non-content policies**

Add this comment immediately above `_TOOL_POLICY_MAP` in `server/consultation_safety.py`:

```python
# Non-content-bearing delegate policies are intentionally present even when the
# hook matcher does not invoke the guard for those tools. They keep policy lookup
# total for all plugin tool names and preserve fail-closed behavior if the matcher
# is widened later.
```

- [ ] **Step 5: Verify and commit**

Run:

```bash
uv run pytest tests/test_codex_guard.py tests/test_hooks_coverage.py -q
uv run ruff check scripts/codex_guard.py server/tool_prefix.py server/consultation_safety.py tests/test_codex_guard.py tests/test_hooks_coverage.py
git add scripts/codex_guard.py server/tool_prefix.py server/consultation_safety.py tests/test_codex_guard.py tests/test_hooks_coverage.py
git commit -m "test: make codex tool prefix invariant explicit"
```

Expected:

```text
All selected tests pass.
Ruff passes.
Commit created.
```

---

### Task 2: Repair Reader-Facing Safety And Status Documentation

**Audit items:** QW1, QW2, QW8, WL3 (the audit routes WL3 into the QW8 doc refresh — one sentence + an optional CI assert).

**Files:**
- Create: `docs/decisions/2026-05-16-security-hook-guard-extension.md`
- Modify: `README.md`
- Modify: `docs/status/current-state.md`
- Modify: `docs/status/reconciliation-register.md`
- Modify: `AGENTS.md`
- Modify: `docs/specs/foundations.md` (Step 5b: document the scripts→server layering invariant — WL3)

- [ ] **Step 1: Patch README safety-substrate wording**

Replace the Safety Substrate opening sentence with:

```markdown
The plugin enforces a fail-closed credential scanning chain on all content-bearing Codex collaboration tool calls (`codex.consult`, `codex.dialogue.start`, `codex.dialogue.reply`, `codex.delegate.start`, `codex.delegate.decide`):
```

- [ ] **Step 2: Add the ADR**

Create `docs/decisions/2026-05-16-security-hook-guard-extension.md`:

```markdown
# Decision Record: Extend Fail-Closed Hook Guard To Delegation Inputs

**Date:** 2026-05-16
**Status:** Decided
**Stakes:** High
**Decision:** The PreToolUse credential guard covers content-bearing delegation inputs in addition to advisory inputs.

## 1. Decision

The credential guard applies to every Codex collaboration tool that accepts user-authored prose capable of carrying secrets:

- `codex.consult`
- `codex.dialogue.start`
- `codex.dialogue.reply`
- `codex.delegate.start`
- `codex.delegate.decide`

The guard remains fail-closed. Malformed hook payloads, malformed plugin tool input, unknown guarded plugin tools, and internal policy errors block execution.

## 2. Context

Delegation introduced execution-domain content fields: `objective` on `codex.delegate.start` and `answers` on `codex.delegate.decide`. These fields cross the same outbound trust boundary as advisory prompts. Treating them as outside the guard would create an inconsistent credential-egress model.

Commit `d4f38f7` extended the guard coverage but did not leave a durable decision record. This ADR records the boundary and the reason so future hook, policy-map, and skill-frontmatter changes can be reviewed against one source of intent.

## 3. Rationale

The plugin has a three-layer safety model: host hook guard, plugin policy traversal, and Codex runtime sandboxing. The hook layer is the earliest fail-closed boundary and should not vary by capability class when the input is user-authored prose.

Non-content-bearing delegation tools may still have scan policies for forward compatibility and fail-closed lookup behavior, but the required hook matcher coverage is the content-bearing set above.

## 4. Consequences

- Any new content-bearing Codex collaboration tool must be added to `server/consultation_safety.py`, `hooks/hooks.json`, and the hook coverage tests in the same change.
- If the MCP tool prefix changes, the shared prefix invariant test must fail until the guard and policy-map move together.
- Future security-boundary changes require an ADR in the same change set.
```

- [ ] **Step 3: Refresh current-state header and debt watchpoints**

In `docs/status/current-state.md`, change:

```markdown
Last updated: 2026-04-29
```

to:

```markdown
Last updated: 2026-05-16
```

Add a bullet under "Active Current-State Watchpoints":

```markdown
- tech-debt audit remediation (`docs/audits/2026-05-15-codex-collaboration-debt.md`), with the Codex CLI wire-contract cluster sequenced behind test-loop speed and payload-shape contract coverage
```

- [ ] **Step 4: Refresh reconciliation register header and add the debt row**

In `docs/status/reconciliation-register.md`, change:

```markdown
Last reconciled: 2026-04-30
```

to:

```markdown
Last reconciled: 2026-05-16
```

Add this as priority item 1 and renumber the existing list:

```markdown
1. Execute or explicitly disposition the tech-debt audit remediation plan from `docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md`, preserving the HL2 -> HL1 -> HL5 ordering for Codex App Server contract work.
```

Create **two** new sections, in this order, before `## Ticket-Owned Active Work`. This step is the **sole** creator of both anchors; every later watch row in this plan (Task 2 Step 5b, Task 7 Step 4b, Task 12 HL4a-lineage, Task 13 Steps 3/4/4b) appends to `## Audit-Owned Deferred Watch Rows` and **never** to `## Audit-Owned Active Work`. The two sections are not interchangeable: active work is `open` and has an **Exit condition**; watch rows are `deferred` and carry a **Watch trigger** (the condition that promotes them back to active work), so they get distinct column semantics.

```markdown
## Audit-Owned Active Work

| ID | State | Owning artifact | Current truth | Exit condition |
|---|---|---|---|---|
| `DEBT-20260515` | `open` | `docs/audits/2026-05-15-codex-collaboration-debt.md` and `docs/superpowers/plans/2026-05-16-codex-collaboration-debt-repair.md` | The 2026-05-15 debt audit found no P0s and four P1s, with the strongest systemic cluster around unmanaged Codex CLI contract/version drift. Quick wins are bounded, but Codex wire-contract work must follow the sequence HL2 -> HL1 -> HL5 before version-pin upgrade execution. | Each quick win is either landed or explicitly declined; HL2, HL1, and HL5 have passing verification; ST2 has a tracked upgrade artifact or is deliberately downgraded with evidence. |

## Audit-Owned Deferred Watch Rows

| ID | State | Owning artifact | Current truth | Watch trigger |
|---|---|---|---|---|
```

Leave the `## Audit-Owned Deferred Watch Rows` table body empty here (header rows only); Task 2 Step 5b appends the first row (`WL3-LAYERING-CI-ASSERT`) to it, and later tasks append the rest. The empty table with its header is the durable anchor every later "append a watch row" step targets; if a later task finds this section absent, that is the Stop Condition in "Phase 1 parallelism is bounded by the register dependency".

- [ ] **Step 5: Add the AGENTS maintenance rule**

Under `## Workflow Notes` in `AGENTS.md`, add:

```markdown
- When a commit changes post-extraction project state, update `docs/status/current-state.md` and `docs/status/reconciliation-register.md` in the same branch or explicitly state why no status-layer change is needed.
```

- [ ] **Step 5b: Document the scripts→server layering invariant (WL3)**

The audit routes WL3 into this QW8 refresh: the invariant "`server/` must not import from `scripts/`" holds in practice (0 reverse imports) but is undocumented in `docs/specs/foundations.md`. Add one sentence to the architecture-rules section of `docs/specs/foundations.md`, matching that file's existing heading and phrasing conventions (read the surrounding rules first; do not invent a new section style):

```markdown
`scripts/` may import from `server/`, but `server/` must never import from `scripts/`. `scripts/` is the host/bootstrap edge; `server/` is the importable core. This one-directional layering currently holds with zero reverse imports.
```

The audit's optional `rg "from scripts\." server/` CI assertion is **deferred, not implemented here** (CI-surface change, not a doc fix). Append this as the first row of the `## Audit-Owned Deferred Watch Rows` section created in Step 4 (its last cell is the watch trigger, matching that section's `Watch trigger` column — do not put it in `## Audit-Owned Active Work`):

```markdown
| `WL3-LAYERING-CI-ASSERT` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | The scripts→server layering invariant is now documented in `foundations.md` (QW8/Task 2). The optional CI guard (`rg "from scripts\." server/` → fail on match) is not yet wired. | At next contributor onboarding, or when a reverse import is first attempted, add the CI assertion. |
```

- [ ] **Step 6: Verify and commit**

The plan file is already tracked on `main` from the Publication Gate; do not re-`git add` it here (no-op that misleads the executor into thinking this commit publishes the plan). Run:

```bash
uv run pytest tests/test_codex_guard.py tests/test_hooks_coverage.py -q
uv run ruff check .
git add README.md AGENTS.md docs/decisions/2026-05-16-security-hook-guard-extension.md docs/status/current-state.md docs/status/reconciliation-register.md docs/specs/foundations.md
git commit -m "docs: record debt and guard coverage decisions"
```

Expected:

```text
Selected tests pass.
Ruff passes.
Commit created.
```

---

### Task 3: Fix Live-Test Rooting And Bounded-Poll Diagnostics

**Audit items:** QW7, QW9.

**Files:**
- Modify: `tests/test_control_plane_live.py`
- Modify: `tests/test_delegation_controller.py`
- Modify: `tests/test_resolution_registry_capture_ready.py`
- Modify: `tests/test_resolution_registry_per_request.py`

- [ ] **Step 1: Fix the live test repo root**

In `tests/test_control_plane_live.py`, replace:

```python
repo_root = Path(__file__).resolve().parents[4]
```

with:

```python
repo_root = Path(__file__).resolve().parents[1]
```

- [ ] **Step 2: Add assertion detail to delegation bounded polls**

For each `while time.monotonic() < deadline:` bounded poll in `tests/test_delegation_controller.py`, keep the polling structure but make the final assertion include the last observed persisted job.

Use this pattern:

```python
final_job = job_store.get(job.job_id)
assert final_job is not None, f"job missing after bounded poll; job_id={job.job_id!r}"
assert final_job.status == "expected_status", f"final_job={final_job!r}"
```

Where a test already has a local job id rather than `job.job_id`, use that exact local variable in the message.

- [ ] **Step 3: Widen the late-timer margin**

In `tests/test_resolution_registry_per_request.py`, replace the late timer wait:

```python
time.sleep(0.7)
```

with:

```python
time.sleep(1.0)
```

Do not widen the 0.05 scheduling sleeps unless a local run proves they are the source of flake.

- [ ] **Step 4: Add final-state details to thread joins**

In `tests/test_resolution_registry_capture_ready.py` and `tests/test_resolution_registry_per_request.py`, replace bare assertions like:

```python
assert not t.is_alive()
```

with stateful messages:

```python
assert not t.is_alive(), f"worker thread still alive; result={result!r}"
```

For two-thread cases, include both result dictionaries:

```python
assert not t1.is_alive(), f"first worker still alive; results={results!r}"
assert not t2.is_alive(), f"second worker still alive; results={results!r}"
```

- [ ] **Step 5: Verify and commit**

Run:

```bash
uv run pytest tests/test_control_plane_live.py tests/test_delegation_controller.py tests/test_resolution_registry_capture_ready.py tests/test_resolution_registry_per_request.py -q
uv run ruff check tests/test_control_plane_live.py tests/test_delegation_controller.py tests/test_resolution_registry_capture_ready.py tests/test_resolution_registry_per_request.py
git add tests/test_control_plane_live.py tests/test_delegation_controller.py tests/test_resolution_registry_capture_ready.py tests/test_resolution_registry_per_request.py
git commit -m "test: improve live-root and bounded-poll diagnostics"
```

Expected:

```text
Selected tests pass; live control-plane test may skip if codex is absent.
Ruff passes.
Commit created.
```

---

### Task 4: Add Startup-Overlap Warning For Session Identity Writes

**Audit item:** QW5 only. Do not implement WL6 in this task.

**Files:**
- Modify: `README.md`
- Modify: `scripts/publish_session_id.py`
- Modify: `tests/test_bootstrap.py`

- [ ] **Step 1: Add failing hook warning tests**

Add tests to `TestPublishSessionIdHook` in `tests/test_bootstrap.py`:

```python
def test_warns_when_recent_different_session_id_exists(self, tmp_path: Path) -> None:
    (tmp_path / "session_id").write_text("old-session", encoding="utf-8")
    payload = json.dumps({"session_id": "new-session"})
    result = subprocess.run(
        [sys.executable, str(_hook_path)],
        input=payload,
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PLUGIN_DATA": str(tmp_path)},
        timeout=5,
    )
    assert result.returncode == 0
    assert "concurrent session warning" in result.stderr
    assert (tmp_path / "session_id").read_text(encoding="utf-8") == "new-session"


def test_no_warning_when_recent_session_id_is_same(self, tmp_path: Path) -> None:
    (tmp_path / "session_id").write_text("same-session", encoding="utf-8")
    payload = json.dumps({"session_id": "same-session"})
    result = subprocess.run(
        [sys.executable, str(_hook_path)],
        input=payload,
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PLUGIN_DATA": str(tmp_path)},
        timeout=5,
    )
    assert result.returncode == 0
    assert "concurrent session warning" not in result.stderr
```

- [ ] **Step 2: Run and confirm the failure**

Run:

```bash
uv run pytest tests/test_bootstrap.py::TestPublishSessionIdHook::test_warns_when_recent_different_session_id_exists tests/test_bootstrap.py::TestPublishSessionIdHook::test_no_warning_when_recent_session_id_is_same -q
```

Expected:

```text
FAIL because scripts/publish_session_id.py does not warn yet.
```

- [ ] **Step 3: Implement the weak overlap warning**

In `scripts/publish_session_id.py`, import `time`:

```python
import time
```

Add constants below imports:

```python
_RECENT_SESSION_WINDOW_SECONDS = 60.0
```

Before writing the temp file, add:

```python
    if os.path.exists(target):
        try:
            existing_session_id = open(target, encoding="utf-8").read().strip()
            age_seconds = time.time() - os.path.getmtime(target)
        except OSError:
            existing_session_id = ""
            age_seconds = _RECENT_SESSION_WINDOW_SECONDS + 1.0
        if (
            existing_session_id
            and existing_session_id != session_id
            and age_seconds <= _RECENT_SESSION_WINDOW_SECONDS
        ):
            print(
                "codex-collaboration: concurrent session warning: "
                "recent different session_id exists; single-session use only",
                file=sys.stderr,
            )
```

This is only a startup-overlap warning. It does not claim to detect the promotion race.

- [ ] **Step 4: Patch README Limitations**

Replace the concurrent sessions limitation with:

```markdown
- **Concurrent sessions unsupported:** Two simultaneous Claude sessions sharing this plugin can collide on the session identity file and, in the promotion path, can both pass a pre-apply `HEAD == base_commit` check before one applies changes. Single-session use only for the current rollout target. If overlap is suspected, stop all sessions, inspect `git status`, keep only one session running, and re-run the relevant status or promotion command. The SessionStart hook emits a weak warning when it sees a recent different `session_id`, but this is only startup-overlap detection, not a cross-process promotion lock.
```

- [ ] **Step 5: Verify and commit**

Run:

```bash
uv run pytest tests/test_bootstrap.py::TestPublishSessionIdHook -q
uv run ruff check scripts/publish_session_id.py tests/test_bootstrap.py
git add README.md scripts/publish_session_id.py tests/test_bootstrap.py
git commit -m "chore: warn on likely concurrent session startup"
```

Expected:

```text
Selected tests pass.
Ruff passes.
Commit created.
```

---

### Phase 1 Continues: Task 4 → Task 5 (same branch)

- [ ] No phase boundary here. Under decision D, Tasks 1–6 are one phase. Tasks 5–6 (QW3 rollback audit, QW4 startup preflight) continue on `chore/debt-low-risk-batch`; do **not** close, push, or PR the phase yet.
- [ ] Each task stays its own commit; the Phase 1 Close Gate runs once, after Task 6.

### Task 5: Add Startup Codex Compatibility Preflight

**Audit item:** QW4. This is a stopgap, not the Codex wire-contract solution.

Chosen semantics for QW4: **startup preflight plus ongoing runtime diagnostics**. The bootstrap must fail fast before `McpServer.run()` when the live Codex surface is already incompatible, but the process must continue using `ControlPlane`'s live checker for later `codex.status()` drift detection and execution-runtime bootstrap. Do **not** turn the startup result into a process-lifetime cache.

**Files:**
- Modify: `scripts/codex_runtime_bootstrap.py`
- Modify: `tests/test_bootstrap.py`

- [ ] **Step 1: Add bootstrap preflight tests and the live-checker guard (do not modify the shared helper)**

Do **not** modify `_patch_bootstrap_run()`. It is shared with the existing bootstrap tests and is reused by Task 12's Phase 4 store-cleanup tests; rewriting its body to patch compat couples three phases through one helper, and a `raising=False` patch permanently masks a mis-wired compat symbol (a fail-fast violation). The default-pass behavior other `main()`-calling tests need once `main()` calls compat is added as an explicit, greppable autouse fixture in Step 3 — not by mutating this helper.

Add to `tests/test_bootstrap.py`:

```python
class TestBootstrapCodexCompatPreflight:
    def test_bootstrap_runs_compat_check_before_server_run(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mod = _import_bootstrap()
        runs = _patch_bootstrap_run(monkeypatch, mod, tmp_path)
        calls: list[str] = []

        def compat_pass() -> object:
            calls.append("compat")
            return type(
                "R",
                (),
                {
                    "passed": True,
                    "codex_version": None,
                    "errors": (),
                    "available_methods": frozenset(),
                },
            )()

        # raising=True is intentional. Pre-implementation the bootstrap module
        # does not import check_live_runtime_compatibility, so this raises
        # AttributeError — that IS the expected Step 2 red. Once Step 3 adds the
        # import the patch binds; thereafter a typo in the symbol name fails
        # loudly instead of silently no-op'ing (the raising=False trap).
        monkeypatch.setattr(mod, "check_live_runtime_compatibility", compat_pass)

        mod.main()

        assert calls == ["compat"]
        assert len(runs) == 1

    def test_bootstrap_exits_before_server_run_when_compat_fails(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mod = _import_bootstrap()
        runs = _patch_bootstrap_run(monkeypatch, mod, tmp_path)

        def compat_fail() -> object:
            return type(
                "R",
                (),
                {
                    "passed": False,
                    "codex_version": None,
                    "errors": ("Codex binary not found on PATH",),
                    "available_methods": frozenset(),
                },
            )()

        monkeypatch.setattr(mod, "check_live_runtime_compatibility", compat_fail)

        with pytest.raises(RuntimeError, match="Codex startup compatibility failed"):
            mod.main()

        assert runs == []

    def test_bootstrap_preserves_live_control_plane_compat_checker(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mod = _import_bootstrap()
        created_kwargs: list[dict[str, object]] = []

        mod.check_live_runtime_compatibility = lambda: type(
            "R",
            (),
            {
                "passed": True,
                "codex_version": None,
                "errors": (),
                "available_methods": frozenset(),
            },
        )()

        class _FakeControlPlane:
            def __init__(self, **kwargs: object) -> None:
                created_kwargs.append(kwargs)

        monkeypatch.setattr(mod, "default_plugin_data_path", lambda: tmp_path)
        monkeypatch.setattr(mod, "ControlPlane", _FakeControlPlane)
        monkeypatch.setattr(mod.McpServer, "run", lambda self: None)

        mod.main()

        assert len(created_kwargs) == 1
        assert created_kwargs[0]["plugin_data_path"] == tmp_path
        assert "journal" in created_kwargs[0]
        assert "compat_checker" not in created_kwargs[0]
```

- [ ] **Step 2: Run and confirm the failure (precise outcome)**

Run:

```bash
uv run pytest tests/test_bootstrap.py::TestBootstrapCodexCompatPreflight -q
uv run pytest tests/test_bootstrap.py -q
```

Expected:

```text
The two startup-preflight tests are RED. Pre-implementation the precise signal
is an ERROR, not an assertion failure: monkeypatch.setattr(mod,
"check_live_runtime_compatibility", ...) raises AttributeError because
scripts/codex_runtime_bootstrap.py does not import that symbol yet. That
AttributeError is the expected red.
The "preserves live control-plane checker" regression test stays GREEN
pre-implementation: bootstrap does not currently pass any `compat_checker`
override into `ControlPlane`, and that must remain true after the preflight
lands.
The second invocation confirms the rest of tests/test_bootstrap.py still passes —
the shared _patch_bootstrap_run was not modified, so only the two new tests are red.
If any other bootstrap test is red here, stop: the helper was modified or something
else regressed.
```

- [ ] **Step 3: Implement preflight before `McpServer` construction**

In `scripts/codex_runtime_bootstrap.py`, add:

```python
from server.codex_compat import check_live_runtime_compatibility  # noqa: E402
```

In `main()`, after retention cleanup and before constructing `ControlPlane`, add:

```python
    compat_result = check_live_runtime_compatibility()
    if not compat_result.passed:
        raise RuntimeError(
            "Codex startup compatibility failed: "
            f"{'; '.join(compat_result.errors)}. Got: {compat_result.codex_version!r:.100}"
        )
```

Then construct `ControlPlane` exactly as before:

```python
    control_plane = ControlPlane(
        plugin_data_path=plugin_data_path,
        journal=journal,
    )
```

Do **not** pass `compat_checker=lambda: compat_result`. That would freeze the startup result for the process lifetime and silently regress the live-drift semantics that `tests/test_control_plane.py::test_codex_status_invalidates_cached_runtime_on_compat_drift` currently proves. The startup preflight is intentionally additive: it blocks obviously bad launches, but later `codex.status()` and execution-runtime startup still call the live checker.

In the **same commit**, add an explicit autouse fixture to `tests/test_bootstrap.py` so every other `main()`-calling test (and Task 12's Phase 4 store-cleanup tests, which reuse this module's bootstrap harness) keeps passing now that `main()` calls compat. Add it to the test module, not to `_patch_bootstrap_run`, so the cross-test coupling is greppable. **Do not** patch a throwaway module instance: `_import_bootstrap()` creates a fresh module via `module_from_spec()` on every call, so the fixture must patch the same `mod` object the test later executes by replacing the local `_import_bootstrap()` helper for the duration of that test:

```python
@pytest.fixture(autouse=True)
def _bootstrap_compat_passes_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default the startup compat check to pass for every bootstrap test.

    Explicit + autouse (not buried in _patch_bootstrap_run) so the coupling is
    visible. `_import_bootstrap()` returns a fresh module on every call, so this
    fixture patches the module instance it creates and then monkeypatches the
    test-local helper to return that same module for the rest of the test.
    raising=True is safe here: this runs at test-setup time, after Step 3's
    `from server.codex_compat import check_live_runtime_compatibility` has made
    the symbol an attribute of the bootstrap module. Tests that exercise the
    compat path (TestBootstrapCodexCompatPreflight) re-monkeypatch the same
    symbol in the test body, which runs after fixture setup and wins.
    """
    mod = _import_bootstrap()

    def _pass() -> object:
        return type(
            "R",
            (),
            {
                "passed": True,
                "codex_version": None,
                "errors": (),
                "available_methods": frozenset(),
            },
        )()

    monkeypatch.setattr(mod, "check_live_runtime_compatibility", _pass)
    monkeypatch.setattr(sys.modules[__name__], "_import_bootstrap", lambda: mod)
```

This fixture is added only in Step 3 (with the implementation), never in Step 1 — at Step 2 the symbol does not exist yet, so an autouse patch would error out the whole module instead of just the two new tests. Task 12's Phase 4 bootstrap tests inherit this fixture automatically because they also call `_import_bootstrap()` from the same test module; Task 12 must not re-add compat patching (cross-referenced there).

- [ ] **Step 4: Verify and commit**

Run:

```bash
uv run pytest tests/test_bootstrap.py tests/test_control_plane.py -q
uv run ruff check scripts/codex_runtime_bootstrap.py tests/test_bootstrap.py
git add scripts/codex_runtime_bootstrap.py tests/test_bootstrap.py
git commit -m "fix: fail fast on Codex startup incompatibility"
```

Expected:

```text
Selected tests pass.
`test_codex_status_invalidates_cached_runtime_on_compat_drift` remains green, so
Task 5 added startup fail-fast behavior without freezing the live checker.
Ruff passes.
Commit created.
```

---

### Task 6: Emit Rollback Audit Events

**Audit item:** QW3 only. Do not add unknown-terminal audit events in this task.

**Risk classification — NOT a docs/test fix (read before batching).** Despite riding in the Phase 1 "low-risk batch", Task 6 is the *only* Phase 1 task that changes production behavior on the **promotion/recovery trust-boundary mutation path** (`server/delegation_controller.py` live-promotion *and* recovery-rollback paths — the path the audit names as the system's sharpest risk) **and** changes two authority-owned specs: `contracts.md` (owner: `contracts`) and `promotion-protocol.md` (owner: `promotion-contract`). Per `.claude/CLAUDE.md` Authority Map these owner docs outrank status docs; this is an ADR-adjacent contract change, not a QW doc tweak. It therefore carries the dedicated trust-path verification in Step 6 (full promotion + recovery suite, not a scoped selection) and is the canonical example for the single-commit-revert procedure in "Merge Model And Solo-Review Reality". It stays in the Phase 1 PR (per decision D) but is the highest-blast-radius commit in that PR and must be the last commit in the Phase 1 sequence so a revert of it does not require unwinding later commits.

**Files:**
- Modify: `docs/specs/contracts.md`
- Modify: `docs/specs/recovery-and-journal.md`
- Modify: `docs/specs/promotion-protocol.md`
- Modify: `server/delegation_controller.py`
- Modify: `tests/test_delegation_controller.py`

- [ ] **Step 1: Add rollback audit-event and replay coverage**

In `tests/test_delegation_controller.py`, add this helper near the promotion tests:

```python
def _rollback_audit_events(plugin_data: Path) -> list[dict[str, Any]]:
    audit_path = plugin_data / "audit" / "events.jsonl"
    if not audit_path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("action") == "rollback":
            events.append(payload)
    return events
```

Invalid UTF-8 is a different corruption class and is **not** handled in this helper. Preserve the existing authority boundary: in the real startup path, `OperationJournal.prune_audit_logs()` runs before `DelegationController.recover_startup()` and quarantines UTF-8-corrupt `audit/events.jsonl`. This task's direct `controller.recover_startup()` tests therefore cover record-local malformed JSON here; UTF-8-corrupt audit input remains owned by the existing `tests/test_journal.py` and `tests/test_bootstrap.py` coverage. If any new direct `controller.recover_startup()` test writes invalid UTF-8 to `audit/events.jsonl`, call `journal.prune_audit_logs()` first so the test preserves the real startup precondition instead of inventing a second controller-local quarantine path.

Extend `test_promote_rolls_back_when_primary_workspace_verification_fails` after the persisted state assertion:

```python
    rollback_events = _rollback_audit_events(plugin_data)
    assert len(rollback_events) == 1
    assert rollback_events[0]["actor"] == "system"
    assert rollback_events[0]["job_id"] == job_id
    assert rollback_events[0]["collaboration_id"] == job.collaboration_id
    assert rollback_events[0]["runtime_id"] == job.runtime_id
```

If `json` is not already imported in the file, add:

```python
import json
```

Add recovery-success coverage as a separate test. This test simulates a crash after `promotion:dispatched`, tampers with a reviewed file so verification fails, lets recovery rollback succeed, and asserts exactly one rollback audit event:

```python
def test_recover_startup_emits_rollback_audit_event_after_successful_recovery_rollback(
    tmp_path: Path,
) -> None:
    controller, job_store, journal, primary_repo, job_id, _hash, _cb = (
        _build_promote_scenario(tmp_path)
    )
    plugin_data = tmp_path / "data"
    session_id = "sess-promote"
    idempotency_key = f"promotion:{job_id}:1"
    created_at = journal.timestamp()
    repo_root_str = str(primary_repo)

    journal.write_phase(
        OperationJournalEntry(
            idempotency_key=idempotency_key,
            operation="promotion",
            phase="intent",
            collaboration_id="collab-promote-1",
            created_at=created_at,
            repo_root=repo_root_str,
            job_id=job_id,
        ),
        session_id=session_id,
    )
    journal.write_phase(
        OperationJournalEntry(
            idempotency_key=idempotency_key,
            operation="promotion",
            phase="dispatched",
            collaboration_id="collab-promote-1",
            created_at=created_at,
            repo_root=repo_root_str,
            job_id=job_id,
        ),
        session_id=session_id,
    )

    persisted = job_store.get(job_id)
    assert persisted is not None
    diff_path = persisted.artifact_paths[0]
    subprocess.run(
        ["git", "-C", str(primary_repo), "apply", "--binary", diff_path],
        check=True,
        capture_output=True,
    )
    (primary_repo / "README.md").write_text("# Tampered\n", encoding="utf-8")

    controller.recover_startup()

    recovered = job_store.get(job_id)
    assert recovered is not None
    assert recovered.promotion_state == "rolled_back"
    rollback_events = _rollback_audit_events(plugin_data)
    assert len(rollback_events) == 1
    assert rollback_events[0]["actor"] == "system"
    assert rollback_events[0]["job_id"] == job_id
    assert rollback_events[0]["collaboration_id"] == "collab-promote-1"
    assert rollback_events[0]["runtime_id"] == "rt-promote-1"
```

Add the crash-window test that closes the real forensic gap. This simulates the exact state the scrutiny called out: `promotion_state="rolled_back"` already persisted, the `promotion:dispatched` journal entry is still unresolved, and no rollback audit event exists yet. Recovery must backfill the missing event before writing `promotion:completed`:

```python
def test_recover_startup_backfills_missing_rollback_audit_event_for_rolled_back_job(
    tmp_path: Path,
) -> None:
    controller, job_store, journal, primary_repo, job_id, _hash, _cb = (
        _build_promote_scenario(tmp_path)
    )
    plugin_data = tmp_path / "data"
    session_id = "sess-promote"
    idempotency_key = f"promotion:{job_id}:1"
    created_at = journal.timestamp()
    repo_root_str = str(primary_repo)

    journal.write_phase(
        OperationJournalEntry(
            idempotency_key=idempotency_key,
            operation="promotion",
            phase="intent",
            collaboration_id="collab-promote-1",
            created_at=created_at,
            repo_root=repo_root_str,
            job_id=job_id,
        ),
        session_id=session_id,
    )
    journal.write_phase(
        OperationJournalEntry(
            idempotency_key=idempotency_key,
            operation="promotion",
            phase="dispatched",
            collaboration_id="collab-promote-1",
            created_at=created_at,
            repo_root=repo_root_str,
            job_id=job_id,
        ),
        session_id=session_id,
    )
    job_store.update_promotion_state(
        job_id,
        promotion_state="rolled_back",
        promotion_attempt=1,
    )

    controller.recover_startup()

    rollback_events = _rollback_audit_events(plugin_data)
    assert len(rollback_events) == 1
    assert rollback_events[0]["job_id"] == job_id
    unresolved = [
        entry
        for entry in journal.list_unresolved(session_id=session_id)
        if entry.operation == "promotion"
    ]
    assert unresolved == []
```

Add the corrupted-audit-line recovery test. This proves both the test helper above and the controller-side replay helper follow the recovery contract's record-local corruption rule instead of letting one malformed audit line abort startup recovery:

```python
def test_recover_startup_ignores_malformed_audit_line_when_backfilling_rollback_event(
    tmp_path: Path,
) -> None:
    controller, job_store, journal, primary_repo, job_id, _hash, _cb = (
        _build_promote_scenario(tmp_path)
    )
    plugin_data = tmp_path / "data"
    session_id = "sess-promote"
    idempotency_key = f"promotion:{job_id}:1"
    created_at = journal.timestamp()
    repo_root_str = str(primary_repo)

    journal.write_phase(
        OperationJournalEntry(
            idempotency_key=idempotency_key,
            operation="promotion",
            phase="intent",
            collaboration_id="collab-promote-1",
            created_at=created_at,
            repo_root=repo_root_str,
            job_id=job_id,
        ),
        session_id=session_id,
    )
    journal.write_phase(
        OperationJournalEntry(
            idempotency_key=idempotency_key,
            operation="promotion",
            phase="dispatched",
            collaboration_id="collab-promote-1",
            created_at=created_at,
            repo_root=repo_root_str,
            job_id=job_id,
        ),
        session_id=session_id,
    )
    job_store.update_promotion_state(
        job_id,
        promotion_state="rolled_back",
        promotion_attempt=1,
    )
    audit_path = plugin_data / "audit" / "events.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text("{not valid json}\n", encoding="utf-8")

    controller.recover_startup()

    rollback_events = _rollback_audit_events(plugin_data)
    assert len(rollback_events) == 1
    assert rollback_events[0]["job_id"] == job_id
    unresolved = [
        entry
        for entry in journal.list_unresolved(session_id=session_id)
        if entry.operation == "promotion"
    ]
    assert unresolved == []
```

Add the idempotency guard for the same replay state. If the rollback event already exists but `promotion:completed` does not, recovery must not emit a duplicate:

```python
def test_recover_startup_does_not_duplicate_existing_rollback_audit_event(
    tmp_path: Path,
) -> None:
    controller, job_store, journal, primary_repo, job_id, _hash, _cb = (
        _build_promote_scenario(tmp_path)
    )
    plugin_data = tmp_path / "data"
    session_id = "sess-promote"
    idempotency_key = f"promotion:{job_id}:1"
    created_at = journal.timestamp()
    repo_root_str = str(primary_repo)

    journal.write_phase(
        OperationJournalEntry(
            idempotency_key=idempotency_key,
            operation="promotion",
            phase="intent",
            collaboration_id="collab-promote-1",
            created_at=created_at,
            repo_root=repo_root_str,
            job_id=job_id,
        ),
        session_id=session_id,
    )
    journal.write_phase(
        OperationJournalEntry(
            idempotency_key=idempotency_key,
            operation="promotion",
            phase="dispatched",
            collaboration_id="collab-promote-1",
            created_at=created_at,
            repo_root=repo_root_str,
            job_id=job_id,
        ),
        session_id=session_id,
    )
    job_store.update_promotion_state(
        job_id,
        promotion_state="rolled_back",
        promotion_attempt=1,
    )
    journal.append_audit_event(
        AuditEvent(
            event_id="evt-existing-rollback",
            timestamp=journal.timestamp(),
            actor="system",
            action="rollback",
            collaboration_id="collab-promote-1",
            runtime_id="rt-promote-1",
            job_id=job_id,
        )
    )

    controller.recover_startup()

    rollback_events = _rollback_audit_events(plugin_data)
    assert len(rollback_events) == 1
```

Extend `test_recover_startup_leaves_unresolved_when_rollback_fails` after the `rollback_needed` assertion:

```python
    assert _rollback_audit_events(tmp_path / "data") == []
```

- [ ] **Step 2: Run and confirm the failure**

Run:

```bash
uv run pytest tests/test_delegation_controller.py::test_promote_rolls_back_when_primary_workspace_verification_fails tests/test_delegation_controller.py::test_recover_startup_emits_rollback_audit_event_after_successful_recovery_rollback tests/test_delegation_controller.py::test_recover_startup_backfills_missing_rollback_audit_event_for_rolled_back_job tests/test_delegation_controller.py::test_recover_startup_ignores_malformed_audit_line_when_backfilling_rollback_event tests/test_delegation_controller.py::test_recover_startup_does_not_duplicate_existing_rollback_audit_event tests/test_delegation_controller.py::test_recover_startup_leaves_unresolved_when_rollback_fails -q
```

Expected:

```text
Live, recovery-success, crash-window backfill, and malformed-audit-line recovery tests FAIL or error because no action="rollback" audit event is emitted and the record-local malformed-line tolerance is not implemented yet.
The duplicate-guard test stays GREEN pre-implementation: current recovery already
avoids double-emitting only because it silently skips the already-rolled-back job.
Rollback-failure test still passes with zero rollback events.
```

- [ ] **Step 3: Update the audit contract**

In `docs/specs/contracts.md` under currently emitted Audit Event Actions, add:

```markdown
| `rollback` | execution | `system` | Promotion rollback completed after post-apply verification failed. Carries `job_id`. |
```

In `docs/specs/recovery-and-journal.md` under **Currently emitted**, add:

```markdown
| Promotion rolled back after post-apply verification failed | `rollback` | `collaboration_id`, `job_id`, `runtime_id` |
```

In `docs/specs/promotion-protocol.md`, the "no rollback audit event" claim appears in **two** places that must change together (Step 6's consistency grep checks for both — replacing only one leaves the spec self-contradictory):

1. The **Rollback Semantics** numbered list — replace item 3 ("No rollback-specific audit event is currently emitted. The promotion state machine records the rollback in job state… A future rollback audit event may be added…") with:

```markdown
3. A rollback audit event is emitted after the workspace is restored and the job reaches `promotion_state: rolled_back`.
```

2. The **state-transition table** row for `rollback_needed → rolled_back` — its "Effect" cell currently reads "Job state updated; worktree retained for inspection. No rollback-specific audit event is currently emitted." Replace the trailing sentence so it reads:

```markdown
| `rollback_needed` | `rolled_back` | Workspace restored | Job state updated; worktree retained for inspection. A rollback audit event is emitted (see [contracts.md §Audit Event Actions](contracts.md#audit-event-actions)). |
```

If the live wording has drifted from the quotes above, reconcile against the live spec — this is a contract-truth fix, not a blind find-replace. Match the table's existing column structure exactly.

- [ ] **Step 4: Add shared rollback audit helpers**

In `server/delegation_controller.py`, add one helper that writes the rollback audit event and one helper that detects whether a matching rollback event already exists for `job_id`. Keep both helpers controller-local; do not guess from `promotion:completed` alone:

```python
    def _append_rollback_audit_event(self, *, job: DelegationJob, job_id: str) -> None:
        self._journal.append_audit_event(
            AuditEvent(
                event_id=self._uuid_factory(),
                timestamp=self._journal.timestamp(),
                actor="system",
                action="rollback",
                collaboration_id=job.collaboration_id,
                runtime_id=job.runtime_id,
                job_id=job_id,
            )
        )

    def _has_rollback_audit_event(self, *, job_id: str) -> bool:
        audit_path = self._plugin_data_path / "audit" / "events.jsonl"
        if not audit_path.exists():
            return False
        # Invalid UTF-8 is owned by startup prune/quarantine before recovery
        # runs. This helper only needs record-local malformed JSON tolerance
        # once that precondition holds.
        for line in audit_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if payload.get("action") == "rollback" and payload.get("job_id") == job_id:
                return True
        return False
```

- [ ] **Step 5: Use the helpers in live, recovery-success, and replay-backfill paths**

Wire the helpers into all three relevant paths:

```python
            self._job_store.update_promotion_state(
                job_id,
                promotion_state="rolled_back",
                promotion_attempt=new_attempt,
            )
            self._append_rollback_audit_event(job=job, job_id=job_id)
```

```python
                                self._job_store.update_promotion_state(
                                    entry.job_id,
                                    promotion_state="rolled_back",
                                )
                                self._append_rollback_audit_event(
                                    job=job,
                                    job_id=entry.job_id,
                                )
```

And handle the crash-window replay case **before** the current pre-terminal branch short-circuits on `promotion_state in ("verified", "discarded", "rolled_back")`:

```python
                    if job is not None and job.promotion_state == "rolled_back":
                        if not self._has_rollback_audit_event(job_id=entry.job_id):
                            self._append_rollback_audit_event(
                                job=job,
                                job_id=entry.job_id,
                            )
                    elif job is not None and job.promotion_state not in (
                        "verified",
                        "discarded",
                        "rolled_back",
                    ):
                        ...
```

This makes the replay rule explicit and idempotent:

- If recovery itself performs the rollback and succeeds, emit the rollback event before the common `promotion:completed` write.
- If recovery starts with the job already at `rolled_back` and the rollback event is missing, backfill it, then let the existing common `promotion:completed` write resolve the journal.
- If the event already exists, do not append another one.
- If unrelated malformed JSON audit lines exist, ignore them record-locally while searching for the rollback event; do not let one bad audit line abort startup recovery.
- Invalid UTF-8 stays owned by startup prune/quarantine: do not add controller-local quarantine logic here, and preserve the real `journal.prune_audit_logs()` precondition in any direct tests that touch UTF-8-corrupt audit input.
- If rollback fails and the job remains `rollback_needed`, emit nothing and leave the journal unresolved.

UUID determinism is already covered — do not add a new seam. `_build_promote_scenario(tmp_path)` constructs the `DelegationController` with `uuid_factory=lambda: next(uuid_counter)` and returns that controller, so the recovery rollback event's `event_id` is deterministic for free in the recovery tests. The assertions check `actor`, `job_id`, `collaboration_id`, and `runtime_id` — never `event_id` — so even the determinism is not load-bearing here. Do not assert on `event_id` and do not rewire `uuid_factory`; the requirement is exactly-one `action="rollback"` event for the missing-event states and zero duplicates for the already-present state.

- [ ] **Step 6: Verify and commit**

Because this is a trust-path + contract change (see Task 6 header), the verification is the **full** promotion/recovery surface, not a scoped selection — a subtle double-emit or emit-before-durable-persist bug here corrupts the audit log on the system's sharpest path. Run:

```bash
# Full delegation/promotion/recovery surface, not -k-scoped.
uv run pytest tests/test_delegation_controller.py tests/test_delegate_decide_async_integration.py tests/test_handler_branches_integration.py -q
# Whole suite (Phase 1 is still pre-Task-7, so a bare run is full-suite here).
uv run pytest tests -q
# Spec/code consistency: check the contract row, recovery trigger row, and code emitter separately.
rg -n '^\| `rollback` \|' docs/specs/contracts.md
rg -n '^\| Promotion rolled back after post-apply verification failed \| `rollback` \|' docs/specs/recovery-and-journal.md
rg -n 'action="rollback"' server/delegation_controller.py
# Must each print nothing and exit 1: only the exact obsolete rollback wording is gone.
# Do not widen this grep to generic "no .*event.*emitted" text — unrelated rows
# legitimately mention other audit events and would make the gate unsatisfiable.
rg -n 'No rollback-specific audit event is currently emitted' docs/specs/promotion-protocol.md
rg -n 'A future rollback audit event may be added' docs/specs/promotion-protocol.md
uv run ruff check server/delegation_controller.py tests/test_delegation_controller.py
git add docs/specs/contracts.md docs/specs/recovery-and-journal.md docs/specs/promotion-protocol.md server/delegation_controller.py tests/test_delegation_controller.py
git commit -m "feat: audit promotion rollback events"
```

Expected:

```text
Full delegation/promotion/recovery suite passes (live + recovery-success + crash-window backfill + malformed-audit-line tolerance asserted; existing-event replay stays single-emission; rollback-FAILURE path still emits zero events).
Whole suite passes (Phase 1 pre-Task-7 full run).
The contract-row grep prints the `docs/specs/contracts.md` table row, the recovery-trigger grep prints the `docs/specs/recovery-and-journal.md` row, and the code grep prints the `server/delegation_controller.py` rollback emitter/helper.
Both exact obsolete-rollback greps print nothing and exit 1 (the old item 3 and
its "future audit event may be added" tail were replaced, not appended to).
Ruff passes. Commit created (last commit in the Phase 1 sequence).
```

---

### Phase Boundary: Close Phase 1, Start Phase 2

- [ ] Run the Phase 1 Close Gate for `chore/debt-low-risk-batch` after Task 6 (Tasks 1–6 complete). Phase 1 uses the **plain** `uv run pytest tests -q` full-suite gate — Task 7 has not yet added the marker split.
- [ ] Complete the Phase 1 Close Gate's remote-write sequence (push/create/merge with the two approval stops) once CI is green.
- [ ] Run the Phase Start Gate for `chore/debt-fast-suite` (Phase 2), then its Phase 2 / Task 7 API Pre-Flight row.
- [ ] Stop if the current branch is still `chore/debt-low-risk-batch`.

### Task 7: Make Timeout-Path Tests Cheap Without Dropping CI Coverage

**Audit item:** HL2 (partial — fast/slow split + approval-window injection; xdist deferred to a watch row, Step 4b).

**Files:**
- Modify: `server/delegation_controller.py`
- Modify: `tests/test_delegation_controller.py`
- Modify: `tests/test_control_plane_live.py` and `tests/test_codex_compat_live.py` (Step 3b: add `pytest.mark.slow` to the live-runtime tier so the marker is non-empty — confirm the exact set via the Step 3b `rg` command)
- Modify: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/status/reconciliation-register.md` (Step 4b: the HL2-xdist deferral watch row)
- Modify: `README.md`, `.claude/CLAUDE.md`, and `AGENTS.md` (Step 4c: reconcile the documented verification command after `addopts` makes a bare `pytest tests -q` fast-only)

- [ ] **Step 1: Identify timeout-path tests before editing**

Run:

```bash
rg -n "_APPROVAL_OPERATOR_WINDOW_SECONDS|timeout|wait_for_parked|approval_window" tests/test_delegation_controller.py server/delegation_controller.py
```

Expected:

```text
The slow tests are the ones waiting on the production approval window or bounded waits derived from it.
```

- [ ] **Step 2: Add a controller constructor seam**

In `DelegationController.__init__`, add a nullable keyword:

```python
        approval_window_seconds: float | None = None,
```

Store it:

```python
        self._approval_window_seconds = (
            _APPROVAL_OPERATOR_WINDOW_SECONDS
            if approval_window_seconds is None
            else approval_window_seconds
        )
```

Replace registry registration timeout usage:

```python
                timeout_seconds=self._approval_window_seconds,
```

- [ ] **Step 3: Thread the seam through test helper**

In `_build_controller`, add:

```python
    approval_window_seconds: float | None = None,
```

Pass it into `DelegationController(...)`:

```python
        approval_window_seconds=approval_window_seconds,
```

In timeout-path tests, call:

```python
_build_controller(tmp_path, approval_window_seconds=0.5)
```

These injected tests are now fast (~0.5s). **Do not mark them `slow`** — they belong in the default loop. The `slow` marker is for the inherently-slow live-runtime tier only (Step 3b).

- [ ] **Step 3b: Populate the `slow` marker (the audit's fast/slow split)**

Without this step the `slow` marker added in Step 4 selects **zero** tests and `addopts = "-m 'not slow'"` deselects the empty set — the default loop equals the full suite and every `-m ""` distinction in this plan is inert ceremony. The split is real only if the marker selects a non-empty set.

Identify the genuinely-slow tier (tests that injection cannot speed because they exercise a real live `codex` subprocess):

```bash
rg -ln "^pytestmark = pytest\.mark\.skipif" tests/
```

Expected: exactly `tests/test_control_plane_live.py` and `tests/test_codex_compat_live.py` (baseline at plan revision). If the set differs, mark the live set the command reports — do not hardcode the two names if the tree has drifted.

For each reported live module, change the module-level guard from a single mark to a list that adds `slow` alongside the existing `skipif` (preserve the existing `skipif` exactly):

```python
pytestmark = [
    pytest.mark.skipif(
        shutil.which("codex") is None,
        reason="codex binary not found on PATH",
    ),
    pytest.mark.slow,
]
```

Rationale: these modules run a real `codex` subprocess when `codex` is present (slow, and not injectable). When `codex` is absent they already `skipif`; adding `slow` additionally excludes them from the default loop *when `codex` is present*, which is exactly the loop the split exists to keep fast. The injected timeout tests stay unmarked and fast in the default loop.

- [ ] **Step 4: Add the marker and the decided local-default split**

**Decision (not an option):** add the marker *and* `addopts = "-m 'not slow'"`, and change CI to force the full suite, in this one commit — and the marker is populated by Step 3b (the live-runtime tier), so it is *not* dead configuration. Rationale: injection (Steps 2–3) delivers the fast timeout loop; the `slow` marker + `addopts` delivers the audit's separate fast/slow split for the inherently-slow live-runtime tier. Both are needed for HL2's two implemented components; a marker that selects zero tests would be the dead configuration this decision explicitly rejects (Step 3b prevents that; Step 5 hard-verifies it).

In the existing `[tool.pytest.ini_options]` table in `pyproject.toml` (do not add a second table), preserve `pythonpath = ["."]` and `testpaths = ["tests"]` and append:

```toml
markers = [
    "slow: tests that intentionally exercise timeout or live-runtime behavior",
]
addopts = "-m 'not slow'"
```

In the **same commit**, change the CI test command in `.github/workflows/ci.yml` so the protected-branch flow runs the **marker-inclusive** suite (the fast timeout-path tests are no longer deselected by `addopts`; the `slow` live-runtime modules are collected but still `skipif`-skip without `codex` on PATH — CI does not install `codex`):

```yaml
run: uv run pytest tests -q -m ""
```

Changing `pyproject.toml`'s `addopts` without changing `.github/workflows/ci.yml` in the same commit is a Stop Condition (CI would silently stop running timeout-path tests). After this lands, every full-suite gate in this plan uses `-m ""` — see "Suite Mode After HL2".

- [ ] **Step 4b: Record the xdist component as explicitly deferred**

The audit's HL2 names three parts: fast/slow split, approval-window injection, and `pytest-xdist`. This task delivers the first two. xdist (whole-suite parallelization) is **deferred, not dropped**. Append this row to the `## Audit-Owned Deferred Watch Rows` section in `docs/status/reconciliation-register.md` (created by Task 2 Step 4 — the same section Task 13 appends to; not `## Audit-Owned Active Work`):

```markdown
| `HL2-XDIST-PARALLELIZATION` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | HL2's fast/slow split + approval-window injection landed (Task 7); the suite's whole-wall-time parallelization via pytest-xdist is not yet done. The HL2-first premise (cheap to add HL1/HL5) still holds because the timeout-path injection is the load-bearing part. | If full-suite wall time after the slow/fast split is still a friction point in routine work, add `pytest-xdist` and a `-n auto` CI/local profile. |
```

HL2 is therefore reported in the completion report as **partially closed** (split + injection done; xdist deferred), never as fully closed.

- [ ] **Step 4c: Reconcile the documented verification command (close the doc-staleness this step creates)**

`addopts = "-m 'not slow'"` makes a bare `uv run pytest tests -q` fast-only. Three checked-in docs state that bare command as the completion gate and/or default local verification surface: `README.md` (`## Local Development` and `## Tests`), `.claude/CLAUDE.md` (project instructions, the `### Verification` content, ~lines 50-56), and `AGENTS.md` (`### Verification`, ~lines 49-58). Leaving any of them unchanged manufactures exactly the status-doc staleness QW8 (Task 2) exists to remove — in the same plan. In the **same commit** as the `addopts` change, update all three files so the documented gate reads: the full-suite completion gate is `uv run pytest tests -q -m ""`; a bare `uv run pytest tests -q` is the fast inner-loop run and excludes `slow` timeout/live-runtime tests; CI runs `-m ""`. Match each file's existing phrasing and section structure; do not restructure surrounding content. If the live wording has drifted from what is quoted here, reconcile against the live file — this is a documentation-truth fix, not a blind find-replace. README is a user-facing verification surface here, not ancillary prose, so it belongs in the same truth-maintenance commit.

This is the only place the plan edits `.claude/CLAUDE.md`. State in the phase commit body that the documented verification command moved to the marker-aware form *because Task 7 changed the default*, so a future reader does not treat it as accidental drift.

- [ ] **Step 5: Verify the split is real (non-inert) and the loop is fast**

The split is the deliverable; prove it selects a non-empty set and actually changes the default collection. Run:

```bash
# 1. The slow marker must select a NON-EMPTY set (else the apparatus is inert).
#    Exactly ONE -m. pytest's -m is argparse store (last-wins), and addopts
#    prepends "-m 'not slow'", so this single `-m slow` overrides the addopts
#    deselection and collects exactly the slow tier. Do NOT append a second
#    `-m ""` as "proof" — last-wins makes `-m ""` the effective expression and
#    collects the whole suite, proving nothing about the slow marker.
uv run pytest -m slow --co -q | tail -1
# 2. The default loop must collect strictly FEWER tests than -m "".
uv run pytest tests --co -q | tail -1
uv run pytest tests -q -m "" --co | tail -1
# 3. The injected timeout tests must be fast (seconds, not minutes).
uv run pytest tests/test_delegation_controller.py -q --durations=5
# 4. Full marker-inclusive suite still green.
uv run pytest tests -q -m ""
uv run ruff check server/delegation_controller.py tests/test_delegation_controller.py
```

Expected:

```text
`pytest -m slow --co` reports a NON-EMPTY collection (the live-runtime tier from Step 3b). If it reports "0 tests collected", STOP — the marker is unpopulated and the entire Suite Mode apparatus is inert; Step 3b was skipped or the live set drifted.
The default `pytest tests --co` count is strictly LESS than the `-m ""` count (by exactly the Step 3b live-runtime test count). Equal counts == inert split == defective Task 7.
test_delegation_controller.py's slowest durations are seconds, not the production approval window — injection works.
The full marker-inclusive suite passes; ruff passes.
```

If the default and `-m ""` collection counts are equal, the split is inert regardless of green tests — treat as a defective Task 7 and do not close Phase 2.

- [ ] **Step 6: Commit**

Run:

```bash
git add server/delegation_controller.py tests/test_delegation_controller.py tests/test_control_plane_live.py tests/test_codex_compat_live.py pyproject.toml .github/workflows/ci.yml docs/status/reconciliation-register.md README.md .claude/CLAUDE.md AGENTS.md
git commit -m "test: shorten approval timeout paths and split slow live tier without dropping CI coverage"
```

Expected:

```text
Commit created.
```

---

### Phase Boundary: Close Phase 2, Start Phase 3

- [ ] Run the Phase 2 Close Gate for `chore/debt-fast-suite` after Task 7. Task 7 added `addopts`, so this close MUST use `uv run pytest tests -q -m ""` — a bare run is fast-only (see "Suite Mode After HL2").
- [ ] Complete the Phase 2 Close Gate's remote-write sequence (push/create/merge with the two approval stops) once CI is green.
- [ ] Run the Phase Start Gate for `chore/debt-wire-contract` (Phase 3), then its Phase 3 / Task 9 API Pre-Flight row.
- [ ] Stop if the current branch is still `chore/debt-fast-suite`.

### Task 8: Add Real-Subprocess JsonRpcClient Tests

**Audit item:** HL5.

**Files:**
- Create: `tests/test_jsonrpc_client.py`
- Read: `server/jsonrpc_client.py`
- Modify: `server/jsonrpc_client.py` only when the subprocess tests expose a real transport bug.

- [ ] **Step 1: Add the echo subprocess script inside the test file**

Create `tests/test_jsonrpc_client.py`:

```python
"""Subprocess-backed tests for JsonRpcClient transport behavior."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from server.jsonrpc_client import JsonRpcClient


def _write_echo_server(tmp_path: Path, *, mode: str = "echo") -> Path:
    script = tmp_path / "echo_jsonrpc.py"
    script.write_text(
        f"""
import json
import sys

mode = {mode!r}
if mode == "malformed-first":
    print("not json", flush=True)
elif mode == "notify-first":
    print(json.dumps({{"jsonrpc": "2.0", "method": "note", "params": {{"value": 1}}}}), flush=True)

for line in sys.stdin:
    message = json.loads(line)
    if message.get("method") == "mismatch":
        print(json.dumps({{"jsonrpc": "2.0", "id": 999, "result": {{}}}}), flush=True)
        continue
    print(json.dumps({{"jsonrpc": "2.0", "id": message["id"], "result": {{"method": message["method"], "params": message.get("params", {{}})}}}}), flush=True)
    sys.stdout.flush()
""".lstrip(),
        encoding="utf-8",
    )
    return script
```

- [ ] **Step 2: Add transport tests**

Add:

```python
def test_request_round_trip(tmp_path: Path) -> None:
    script = _write_echo_server(tmp_path)
    client = JsonRpcClient([sys.executable, str(script)], request_timeout=2.0)
    try:
        result = client.request("ping", {"x": 1})
    finally:
        client.close()
    assert result == {"method": "ping", "params": {"x": 1}}


def test_request_buffers_notification_before_response(tmp_path: Path) -> None:
    script = _write_echo_server(tmp_path, mode="notify-first")
    client = JsonRpcClient([sys.executable, str(script)], request_timeout=2.0)
    try:
        result = client.request("ping", {})
        notification = client.next_notification(timeout=0.1)
    finally:
        client.close()
    assert result == {"method": "ping", "params": {}}
    assert notification["method"] == "note"


def test_malformed_stdout_line_is_dropped(tmp_path: Path) -> None:
    script = _write_echo_server(tmp_path, mode="malformed-first")
    client = JsonRpcClient([sys.executable, str(script)], request_timeout=2.0)
    try:
        result = client.request("ping", {})
    finally:
        client.close()
    assert result["method"] == "ping"


def test_unexpected_response_id_raises(tmp_path: Path) -> None:
    script = _write_echo_server(tmp_path)
    client = JsonRpcClient([sys.executable, str(script)], request_timeout=2.0)
    try:
        with pytest.raises(RuntimeError, match="unexpected response id"):
            client.request("mismatch", {})
    finally:
        client.close()
```

- [ ] **Step 3: Verify and commit**

Run:

```bash
uv run pytest tests/test_jsonrpc_client.py -q
uv run ruff check tests/test_jsonrpc_client.py server/jsonrpc_client.py
git add tests/test_jsonrpc_client.py server/jsonrpc_client.py
git commit -m "test: cover json-rpc subprocess transport"
```

Expected:

```text
Tests pass.
Ruff passes.
Commit created.
```

If a test exposes a real `JsonRpcClient` bug, patch the smallest transport behavior needed and keep it in this commit.

---

### Task 9: Validate Codex Wire Payload Shapes Against Vendored Schemas

**Audit item:** HL1. Sequenced after Task 7 (HL2). This is an *ergonomic* ordering, not a functional dependency: HL1 uses nothing from the `approval_window_seconds` seam; HL2 just goes first so adding contract coverage does not worsen the slow loop (audit rationale). Do not treat HL1 as code-dependent on HL2.

**Files:**
- Modify: `pyproject.toml`
- Modify: `tests/conftest.py`
- Create: `tests/test_codex_wire_contract.py`
- Modify: `tests/test_delegate_decide_async_integration.py`
- Read: `server/runtime.py`
- Read: `server/delegation_controller.py`
- Modify: `server/runtime.py` only if the public methods cannot exercise a request payload that must be validated, **or** if Step 6a finds a real request-payload contract violation.
- Modify: `server/delegation_controller.py` only if the response payload builders must be made callable without running a live worker, **or** if Step 6a finds a real response-payload contract violation.

- [ ] **Step 1: Add dev dependency**

In `pyproject.toml`, add:

```toml
    "jsonschema>=4.0",
```

to the `dev` dependency group.

Run:

```bash
uv sync
```

Expected:

```text
uv.lock updates to include jsonschema and its transitive dependencies.
```

- [ ] **Step 2: Add schema fixtures**

In `tests/conftest.py`, add:

```python
@pytest.fixture
def schema_loader(vendored_schema_dir: Path):
    def load(name: str) -> dict:
        path = vendored_schema_dir / name
        if not path.exists():
            pytest.skip(f"{name} not found in vendored schema")
        import json

        return json.loads(path.read_text(encoding="utf-8"))

    return load
```

- [ ] **Step 3: Add request-capture helper**

Create `tests/test_codex_wire_contract.py` with:

```python
"""Payload-shape contract tests against vendored Codex App Server schemas."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema.validators import validator_for

from server.runtime import (
    AppServerRuntimeSession,
    _build_read_only_sandbox_policy,
    build_workspace_write_sandbox_policy,
)

# Schemas this contract gate must validate against. If a bump (ST2) changes
# TESTED_CODEX_VERSION without regenerating fixtures, vendored_schema_dir would
# skip and this gate would pass vacuously — test_contract_fixtures_present
# turns that into a hard failure instead.
_REQUIRED_SCHEMAS = (
    "ClientRequest.json",
    "CommandExecutionRequestApprovalResponse.json",
    "FileChangeRequestApprovalResponse.json",
    "ToolRequestUserInputResponse.json",
)


def _validator_for(schema: dict[str, Any]):
    """Build the jsonschema validator the fixture's own ``$schema`` declares.

    The vendored Codex schemas are TypeScript-generated; do not assume Draft 7.
    Deriving the validator from the schema keeps the gate honest across a
    vendored-draft change on a version bump.
    """
    cls = validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


class CapturingClient:
    def __init__(self) -> None:
        self.requests: list[tuple[str, dict[str, Any]]] = []
        self.responses: list[tuple[str | int, dict[str, Any]]] = []
        self.notifications: list[dict[str, Any]] = []

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self.requests.append((method, params))
        if method == "initialize":
            return {
                "codexHome": "/tmp/codex",
                "platformFamily": "unix",
                "platformOs": "macos",
                "userAgent": "codex-cli 0.117.0",
            }
        if method == "account/read":
            return {"account": {"type": "openai"}, "requiresOpenaiAuth": False}
        if method in {"thread/start", "thread/fork", "thread/resume"}:
            return {"thread": {"id": "thread-1"}}
        if method == "thread/read":
            return {"thread": {"turns": []}}
        if method == "turn/start":
            self.notifications.append(
                {
                    "method": "turn/completed",
                    "params": {"turn": {"id": "turn-1", "status": "completed"}},
                }
            )
            return {"turn": {"id": "turn-1"}}
        if method == "turn/interrupt":
            return {}
        raise AssertionError(f"unexpected method {method!r}")

    def next_notification(self, timeout: float | None = None) -> dict[str, Any]:
        # Today _run_turn pops exactly once per turn (the queued turn/completed
        # terminates the loop). If a future runtime.py change drains this
        # (e.g. it starts requiring an explicit turnId on every notification,
        # making the stubbed turn/completed get skipped), fail with a clear
        # message instead of a bare IndexError from pop(0).
        assert self.notifications, (
            "CapturingClient notification queue drained: _run_turn requested "
            "more notifications than the stub queued. The turn loop contract "
            "changed — queue the notifications the new flow expects."
        )
        return self.notifications.pop(0)

    def respond(self, request_id: str | int, result: dict[str, Any]) -> None:
        self.responses.append((request_id, result))

    def close(self) -> None:
        return None


def _session_with_client(tmp_path: Path, client: CapturingClient) -> AppServerRuntimeSession:
    # AppServerRuntimeSession.__init__ eagerly constructs
    # JsonRpcClient(["codex", "app-server"]) — calling it here would spawn (or
    # fail to spawn, when codex is absent per the Task 0 baseline) a real Codex
    # subprocess before the stub is injected. Bypass __init__ and set exactly
    # the two attributes __init__ assigns (server/runtime.py: _repo_root,
    # _client). Same pattern as object.__new__(DelegationController) below.
    session = object.__new__(AppServerRuntimeSession)
    session._repo_root = tmp_path  # type: ignore[attr-defined]
    session._client = client  # type: ignore[attr-defined]
    return session
```

If `server/runtime.py` later adds another instance attribute to `__init__`, this helper must set it too; the contract-test commit must re-read `AppServerRuntimeSession.__init__` and assign every attribute it sets, never call the real `__init__`.

- [ ] **Step 4: Validate every runtime client-request payload**

Add tests that exercise and validate:

```python
def test_runtime_client_request_payloads_validate(schema_loader, tmp_path: Path) -> None:
    client = CapturingClient()
    session = _session_with_client(tmp_path, client)

    session.initialize()
    session.read_account()
    thread_id = session.start_thread()
    session.fork_thread(thread_id)
    session.resume_thread(thread_id)
    session.read_thread(thread_id)
    session.run_advisory_turn(
        thread_id=thread_id,
        prompt_text="hello",
        output_schema={"type": "object"},
    )
    session.run_execution_turn(
        thread_id=thread_id,
        prompt_text="do work",
        sandbox_policy=_build_read_only_sandbox_policy(),
    )
    # The real delegation execution path sends turn/start with the
    # workspace-write sandbox policy (server/delegation_controller.py
    # run_execution_turn(sandbox_policy=build_workspace_write_sandbox_policy(
    # worktree_path))). Validating only the read-only shape leaves the
    # security-adjacent workspace-write sandboxPolicy payload — the exact
    # surface the audit's HL1 calls out (`turn/start` carries
    # `sandboxPolicy`) — unvalidated. Exercise it so the gate covers the
    # payload shape that actually crosses the wire during delegation.
    session.run_execution_turn(
        thread_id=thread_id,
        prompt_text="do work",
        sandbox_policy=build_workspace_write_sandbox_policy(tmp_path),
    )
    session.interrupt_turn(thread_id=thread_id, turn_id="turn-1")

    client_request_schema = schema_loader("ClientRequest.json")
    validator = _validator_for(client_request_schema)
    for method, params in client.requests:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        errors = sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
        assert errors == [], f"{method} payload invalid: {errors}"

    # Prove the workspace-write turn/start was actually exercised and
    # validated above — not silently absent. If a future executor deletes
    # `build_workspace_write_sandbox_policy` to silence an unused-import
    # lint (or the execution-turn coverage regresses), this fails loudly
    # instead of the gate passing with read-only-only coverage and the
    # security-adjacent sandbox payload uncovered.
    turn_start_sandboxes = [
        params.get("sandboxPolicy")
        for method, params in client.requests
        if method == "turn/start"
    ]
    assert any(
        isinstance(sp, dict) and sp.get("type") == "workspaceWrite"
        for sp in turn_start_sandboxes
    ), (
        "no workspace-write turn/start payload captured: HL1 must validate "
        "the sandboxPolicy shape the real delegation path sends "
        "(build_workspace_write_sandbox_policy), not only the read-only shape"
    )
```

This test must cover `initialize`, `account/read`, `thread/start`, `thread/fork`, `thread/resume`, `thread/read`, `turn/start` (**both** the read-only and the workspace-write `sandboxPolicy` variants — the workspace-write shape is the one the real delegation execution path sends and the audit's HL1 flags as security-adjacent), and `turn/interrupt`.

- [ ] **Step 4a: Make missing fixtures and a toothless validator hard failures**

The contract gate is worthless if it skips (missing fixture) or passes everything (permissive schema). Add both guards to `tests/test_codex_wire_contract.py`:

```python
def test_contract_fixtures_present() -> None:
    """A missing fixture dir or file must FAIL here, never skip the gate.

    Deliberately does NOT depend on the `vendored_schema_dir` fixture: that
    fixture skips when the version dir is absent, which is exactly the
    ST2-version-bump failure mode that must fail loudly. Reconstruct the path
    the same way conftest does (server.codex_compat.TESTED_CODEX_VERSION) so
    this assertion is skip-proof.
    """
    from server.codex_compat import TESTED_CODEX_VERSION

    fixtures_dir = (
        Path(__file__).parent
        / "fixtures"
        / "codex-app-server"
        / TESTED_CODEX_VERSION
    )
    assert fixtures_dir.is_dir(), (
        f"vendored schema dir missing for TESTED_CODEX_VERSION="
        f"{TESTED_CODEX_VERSION!r}: {fixtures_dir} — an ST2 version bump must "
        f"regenerate fixtures before the contract gate can run."
    )
    missing = [
        name for name in _REQUIRED_SCHEMAS if not (fixtures_dir / name).exists()
    ]
    assert missing == [], f"required vendored schemas missing: {missing}"


def test_client_request_validator_rejects_known_bad_payload(schema_loader) -> None:
    """Negative control: prove the validator has teeth.

    If the vendored ClientRequest schema is too permissive to reject this
    obviously malformed payload, every positive assertion above is vacuous.
    """
    validator = _validator_for(schema_loader("ClientRequest.json"))
    bad = {"jsonrpc": 2.0, "method": 12345}  # wrong types, no id/params
    errors = list(validator.iter_errors(bad))
    assert errors, "ClientRequest schema accepted a malformed payload; the contract gate is toothless"
```

If `test_client_request_validator_rejects_known_bad_payload` does not produce errors, do not delete or weaken it. A permissive vendored schema is itself a finding: record it in the phase notes and the HL1 PR body, and add a per-method `oneOf`/`$ref` selection so the test validates the specific request schema rather than a permissive envelope. The HL1 commit is not complete while the negative control passes (i.e., while the schema is toothless).

- [ ] **Step 5: Validate server-request response payloads**

Add explicit schema tests for the response result objects the controller sends back through `JsonRpcClient.respond()`:

```python
from typing import Any, cast

from server.delegation_controller import DelegationController
from server.models import PendingServerRequest


def _assert_valid(schema: dict[str, Any], payload: dict[str, Any]) -> None:
    errors = sorted(_validator_for(schema).iter_errors(payload), key=lambda err: list(err.path))
    assert errors == [], f"payload invalid: {errors}"


def _pending_request(kind: str) -> PendingServerRequest:
    return PendingServerRequest(
        request_id=f"req-{kind}",
        runtime_id="runtime-1",
        collaboration_id="collab-1",
        codex_thread_id="thread-1",
        codex_turn_id="turn-1",
        item_id="item-1",
        kind=cast(Any, kind),
        requested_scope={},
    )


def _controller_response_payload(
    *,
    decision: str,
    kind: str,
    answers: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, Any]:
    controller = object.__new__(DelegationController)
    return controller._build_response_payload(
        decision=decision,
        answers=answers,
        request=_pending_request(kind),
    )


def test_command_approval_response_payloads_validate(schema_loader) -> None:
    schema = schema_loader("CommandExecutionRequestApprovalResponse.json")
    approved = _controller_response_payload(
        decision="approve",
        kind="command_approval",
    )
    denied = _controller_response_payload(
        decision="deny",
        kind="command_approval",
    )

    assert approved == {"decision": "accept"}
    assert denied == {"decision": "decline"}
    _assert_valid(schema, approved)
    _assert_valid(schema, denied)


def test_file_change_response_payloads_validate(schema_loader) -> None:
    schema = schema_loader("FileChangeRequestApprovalResponse.json")
    approved = _controller_response_payload(
        decision="approve",
        kind="file_change",
    )
    denied = _controller_response_payload(
        decision="deny",
        kind="file_change",
    )

    assert approved == {"decision": "accept"}
    assert denied == {"decision": "decline"}
    _assert_valid(schema, approved)
    _assert_valid(schema, denied)


def test_user_input_response_payloads_validate(schema_loader) -> None:
    schema = schema_loader("ToolRequestUserInputResponse.json")
    approved = _controller_response_payload(
        decision="approve",
        kind="request_user_input",
        answers={"question-1": ("yes",)},
    )
    denied = _controller_response_payload(
        decision="deny",
        kind="request_user_input",
    )

    assert approved == {"answers": {"question-1": {"answers": ["yes"]}}}
    assert denied == {"answers": {}}
    _assert_valid(schema, approved)
    _assert_valid(schema, denied)
```

Do not validate hand-written plugin-level decisions such as `{"decision": "approve"}` or `{"decision": "deny"}` against the App Server schemas. The contract test must call the production `_build_response_payload()` mapper and validate the mapper's returned App Server payloads against the vendored response schemas.

- [ ] **Step 6: Validate the real decide-to-dispatch path**

In `tests/test_delegate_decide_async_integration.py`, import the validator factory (not a pinned draft — same rationale as `tests/test_codex_wire_contract.py`):

```python
from jsonschema.validators import validator_for
```

Add a local helper near `test_decide_worker_dispatches_l4_payload_end_to_end`:

```python
def _assert_schema_valid(schema: dict[str, Any], payload: dict[str, Any]) -> None:
    cls = validator_for(schema)
    cls.check_schema(schema)
    errors = sorted(cls(schema).iter_errors(payload), key=lambda err: list(err.path))
    assert errors == [], f"payload invalid: {errors}"
```

Add `schema_loader` to `test_decide_worker_dispatches_l4_payload_end_to_end(...)` and validate the captured `session.respond(...)` payload after the existing exact-payload assertion:

```python
    schema_name = {
        "command_approval": "CommandExecutionRequestApprovalResponse.json",
        "request_user_input": "ToolRequestUserInputResponse.json",
    }[kind]
    _assert_schema_valid(schema_loader(schema_name), matching[0][1])
```

This is the consumer-side complement to `tests/test_codex_wire_contract.py`: the mapper schema tests prove the private payload builder returns valid App Server payloads, and this integration assertion proves the real `decide()` -> worker -> `session.respond(...)` path dispatches a schema-valid payload without a wrapper or mutation.

- [ ] **Step 6a: Disposition a real contract violation (expected, not exceptional)**

This is the first time these wire payloads are validated against the vendored schemas. A genuine failure — a builder that emits a shape the schema rejects, where the schema is correct (negative control from Step 4a passes-as-rejection, draft derived from the fixture) — is a likely and *intended* outcome of adding a contract gate, not a test defect.

When a payload fails and the schema is right:

1. Do not weaken the schema, relax the assertion, or `xfail` it to make the phase green.
2. Identify the smallest production builder at fault (`server/runtime.py` request builder or `server/delegation_controller.py` response builder).
3. If the fix is small and self-contained, make it in this HL1 commit and state the corrected wire shape in the commit body and PR.
4. If the fix is non-trivial (changes a live request/response contract, touches the promotion/turn path, or needs its own tests), stop: do not stretch HL1. Land HL1 with the failing case marked `xfail(strict=True, reason="<finding>")` so the gate stays red-honest, open a `fix/codex-wire-<shape>` ticket and register row, and record that ST2 execution (not Task 10's tracking artifact) is blocked until that fix lands. In this branch the phase is **degraded, not closed**: do not claim "HL1 closed" in the commit, PR, or completion report. Phase 4 may proceed only on the narrower `_build_response_payload` mapper-invariant basis, and only if the xfailed case is outside that mapper and the mapper-focused assertions still pass; otherwise stop before Phase 4. `xfail(strict=True)` is mandatory so the suite fails loudly if the shape is silently "fixed" elsewhere.
5. Either way, this is a finding: add it to the phase notes and the HL1 PR body. HL1 closing with zero findings and zero `xfail`s is acceptable only if the negative control genuinely rejects and every builder validates.

- [ ] **Step 7: Verify and commit**

Run:

```bash
uv run pytest tests/test_codex_compat.py tests/test_codex_wire_contract.py tests/test_runtime.py tests/test_delegate_decide_async_integration.py::test_decide_worker_dispatches_l4_payload_end_to_end -q
uv run ruff check tests/conftest.py tests/test_codex_wire_contract.py tests/test_delegate_decide_async_integration.py server/runtime.py server/delegation_controller.py
git add pyproject.toml uv.lock tests/conftest.py tests/test_codex_wire_contract.py tests/test_delegate_decide_async_integration.py server/runtime.py server/delegation_controller.py
git commit -m "test: validate Codex app-server wire payloads"
```

Expected:

```text
test_contract_fixtures_present PASSES (required schemas present, not skipped).
test_client_request_validator_rejects_known_bad_payload PASSES (the validator rejects a malformed payload — the gate has teeth).
All contract assertions are executed, not skipped. `pytest -q` shows 0 skipped in test_codex_wire_contract.py.
Every builder payload validates, OR each failure is dispositioned per Step 6a (small fix in-commit, or `xfail(strict=True)` + fix ticket + ST2-blocked + explicit degraded-HL1 note).
Ruff passes.
Commit created.
```

If `pytest -q` reports any skip in `tests/test_codex_wire_contract.py`, the contract gate did not run — treat as a defective phase close and resolve the fixture/version mismatch before merging.

---

### Phase Boundary: Close Phase 3, Start Phase 4

- [ ] Run the Phase 3 Close Gate for `chore/debt-wire-contract` after Task 9 (marker-inclusive `-m ""`; 0 unexpected skips in `tests/test_codex_wire_contract.py` — a skipped HL1 contract gate is a defective close).
- [ ] If Task 9 is fully green (no HL1 `xfail`s), complete the Phase 3 Close Gate's remote-write sequence and merge the Phase 3 PR. In that branch HL1 is closed and fully locked on `main`.
- [ ] If Task 9 lands via the degraded Step 6a branch, the Phase 3 PR/body must say so explicitly: HL1 is partial/degraded, ST2 execution remains blocked, and Phase 4 is proceeding only on the narrower `_build_response_payload` mapper-invariant basis. Do not claim "HL1 closed" anywhere in that PR, merge note, or completion report.
- [ ] Run the Phase Start Gate for `chore/debt-codex-cluster` (Phase 4), then its Phase 4 / Task 12 API Pre-Flight row (Task 11 carries its own HL1-contract lock baseline in Task 11 Step 1 and, in the degraded branch, must stay within the narrower mapper-only guarantee).
- [ ] Stop if the current branch is still `chore/debt-wire-contract`.

### Task 10: Track The Codex Version-Pin Upgrade

**Audit item:** ST2. Depends on Task 9.

This task is tracking-only. It may still land after a degraded Task 9 close, but its ticket/register text must preserve that ST2 execution remains blocked until the HL1 follow-up fix clears the `xfail`.

**Files:**
- Create: `docs/tickets/2026-05-16-codex-app-server-version-upgrade.md`
- Modify: `docs/status/reconciliation-register.md`
- Modify only during execution, not tracking: `server/codex_compat.py`

- [ ] **Step 1: Create the upgrade ticket**

Create `docs/tickets/2026-05-16-codex-app-server-version-upgrade.md`:

```markdown
---
id: T-20260516-01
title: Track and execute Codex App Server version-pin upgrade
status: open
created: 2026-05-16
---

# Track and execute Codex App Server version-pin upgrade

## Current state

`server/codex_compat.py` pins `TESTED_CODEX_VERSION` and `MINIMUM_CODEX_VERSION` to `0.117.0`. The debt audit records local `codex-cli 0.130.0` on 2026-05-16, with a known 0.117 -> 0.125 schema delta already documented in `docs/specs/2026-04-29-codex-app-server-0.125.0-schema-delta.md`.

## Required gates

- Regenerate fixtures for the target Codex version.
- Produce a schema diff against `0.117.0`.
- Keep `tests/test_codex_wire_contract.py` passing against the target fixtures.
- Run live advisory and execution smoke checks.
- Verify `sandboxPolicy` / `permissionProfile` behavior explicitly.
- Update operator-facing docs and status/register rows.
- Decide whether `MINIMUM_CODEX_VERSION` moves with `TESTED_CODEX_VERSION` or stays lower with compatibility gates.

## Exit condition

The target version is either landed with passing contract/live evidence, or explicitly deferred with a recorded reason and a next review date.
```

- [ ] **Step 2: Add register row**

In `docs/status/reconciliation-register.md`, add under Ticket-Owned Active Work:

```markdown
| `T-20260516-01` | `open` | `docs/tickets/2026-05-16-codex-app-server-version-upgrade.md` | Codex App Server version-pin upgrade is now explicitly tracked. Execution remains gated by payload-shape contract tests and live smoke evidence. | Target Codex version fixtures, diff, contract tests, live smoke, docs, and version constants are updated or the upgrade is explicitly deferred with evidence. |
```

- [ ] **Step 3: Verify and commit**

Run:

```bash
uv run ruff check .
git add docs/tickets/2026-05-16-codex-app-server-version-upgrade.md docs/status/reconciliation-register.md
git commit -m "docs: track Codex app-server version upgrade"
```

Expected:

```text
Ruff passes.
Commit created.
```

Do not change `server/codex_compat.py` in this task.

---

### Phase 4 Continues: Task 10 → Task 11 (same branch)

- [ ] No phase boundary here. Tasks 11–13 continue on `chore/debt-codex-cluster`; do **not** close, push, or PR the phase yet. Each task is its own commit; the Phase 4 Close Gate runs once, after Task 13.
- [ ] Task 11 (HL3) edits `delegation_controller.py` where HL1's `_build_response_payload` lives. If Phase 3 closed fully green, HL1 is fully on `main`; if Phase 3 closed degraded under Task 9 Step 6a, only the `_build_response_payload` mapper invariant is treated as locked and the refactor must stay within that narrower guarantee. Task 11 Step 1 still locks the HL1 contract test as its refactor baseline.

### Task 11: Extract The Server-Request Handler

**Audit item:** HL3. Sequence after Tasks 8 and 9.

**HL1 coupling (read before refactoring).** This refactor edits `server/delegation_controller.py`, which is exactly where HL1's `_build_response_payload` lives and where `tests/test_codex_wire_contract.py` constructs the controller via `object.__new__(DelegationController)` to call that mapper without `__init__`. That HL1 test is not in this task's default lock/verify set, so a mapper regression would otherwise stay invisible until the Phase 4 close gate. The contract test is therefore added to Step 1 and Step 3 below, and the mapper invariant is pinned in Step 2.

**Files:**
- Modify: `server/delegation_controller.py`
- Modify or create: `tests/test_handler_branches_integration.py`
- Modify: `tests/test_delegation_controller.py` when direct-call coverage needs to follow the extracted handler signature.
- Verify (do not modify unless the `object.__new__` mapper bypass must move): `tests/test_codex_wire_contract.py`.

- [ ] **Step 1: Lock current behavior before refactor**

Run (the contract test is included so the HL1 mapper invariant is part of the locked baseline, not just the handler-branch tests):

```bash
uv run pytest tests/test_handler_branches_integration.py tests/test_delegation_controller.py tests/test_codex_wire_contract.py -q
```

Expected:

```text
All selected tests pass before refactor, including the HL1 response-mapper contract tests.
0 skipped in tests/test_codex_wire_contract.py (the contract gate actually ran — a skip here means the lock baseline is fictitious).
```

- [ ] **Step 2: Extract without changing branch behavior**

Keep the code in `server/delegation_controller.py`. Do not create a new module in this pass.

Introduce a private helper class or private method that receives every state dependency explicitly:

```python
@dataclass
class _ServerRequestHandlerState:
    captured_request: PendingServerRequest | None = None
    interrupted_by_unknown: bool = False
    captured_request_parse_failed: bool = False
```

Then move the nested handler body into a named method:

```python
    def _handle_server_request(
        self,
        message: dict[str, Any],
        *,
        job_id: str,
        collaboration_id: str,
        runtime_id: str,
        entry: ExecutionRuntimeEntry,
        registry: ResolutionRegistry,
        state: _ServerRequestHandlerState,
    ) -> dict[str, Any] | None:
        ...
```

The closure inside `_execute_live_turn` becomes:

```python
        state = _ServerRequestHandlerState()

        def _server_request_handler(message: dict[str, Any]) -> dict[str, Any] | None:
            return self._handle_server_request(
                message,
                job_id=job_id,
                collaboration_id=collaboration_id,
                runtime_id=runtime_id,
                entry=entry,
                registry=registry,
                state=state,
            )
```

Pass `state.captured_request`, `state.interrupted_by_unknown`, and `state.captured_request_parse_failed` into `_finalize_turn`.

**HL1 mapper invariant — do not break this in the extraction.** `_build_response_payload` must remain a pure, instance-state-free mapper of `(decision, kind, answers)` (it currently reads no `self.*` — verified at the HL1 task). The HL1 contract test calls it via `object.__new__(DelegationController)` without `__init__`. This extraction must not move `_build_response_payload` onto the new handler state object, give it a `self.*` dependency, or change its signature. If a future requirement genuinely forces the mapper to take instance state, that is a contract change, not a drive-by refactor: stop, and update `tests/test_codex_wire_contract.py`'s construction (`_controller_response_payload`) in the same commit so the bypass still exercises the real mapper.

- [ ] **Step 3: Verify no behavior drift**

Run (the contract test is re-run so a mapper regression fails here, in Task 11, not silently at the Phase 4 close gate):

```bash
uv run pytest tests/test_handler_branches_integration.py tests/test_delegation_controller.py tests/test_delegate_decide_async_integration.py tests/test_codex_wire_contract.py -q
uv run ruff check server/delegation_controller.py tests/test_handler_branches_integration.py tests/test_delegation_controller.py
```

Expected:

```text
All selected tests pass, including the unchanged HL1 response-mapper contract tests.
0 skipped in tests/test_codex_wire_contract.py.
Ruff passes.
```

- [ ] **Step 4: Commit**

Run (include `tests/test_codex_wire_contract.py` only if the mapper bypass had to move per the Step 2 invariant note; otherwise it is unchanged and must not appear in the diff):

```bash
git add server/delegation_controller.py tests/test_handler_branches_integration.py tests/test_delegation_controller.py
git commit -m "refactor: extract delegation server-request handler"
```

Expected:

```text
Commit created.
```

---

### Phase 4 Continues: Task 11 → Task 12 (same branch)

- [ ] No phase boundary here. Task 12 (HL4 store hygiene) continues on `chore/debt-codex-cluster`; do **not** close, push, or PR the phase yet.
- [ ] Run the Phase 4 / Task 12 API Pre-Flight row before Task 12's first TDD step.

### Task 12: Repair Store Hygiene

**Audit items:** HL4a (TurnStore portion; LineageStore portion deferred under default Option C — see Step 4), HL4b (only if the Step 5 owner is implemented), Open Question 4 resolved.

**Files:**
- Modify: `server/turn_store.py`
- Modify: `tests/test_turn_store.py`
- Modify: `server/lineage_store.py`
- Modify: `tests/test_lineage_store.py`
- Modify: `scripts/codex_runtime_bootstrap.py`
- Modify: `tests/test_bootstrap.py`
- Modify: `docs/specs/contracts.md`
- Modify: `docs/specs/recovery-and-journal.md`
- Modify: `docs/status/reconciliation-register.md` (Step 4 HL4a-lineage defer row under Option C; Step 5 HL4b defer row if owner not implemented)

- [ ] **Step 1: Add TurnStore cache tests**

In `tests/test_turn_store.py`, add coverage that writes a turn, reads it twice, writes a newer value, and verifies the second value is returned after write invalidation:

```python
def test_turn_store_replay_cache_invalidates_on_write(tmp_path: Path) -> None:
    store = TurnStore(tmp_path, "sess-1")
    store.write("collab-1", turn_sequence=1, context_size=10)
    assert store.get("collab-1", turn_sequence=1) == 10
    assert store.get("collab-1", turn_sequence=1) == 10
    store.write("collab-1", turn_sequence=1, context_size=20)
    assert store.get("collab-1", turn_sequence=1) == 20
```

- [ ] **Step 2: Implement TurnStore cache**

In `server/turn_store.py`, add an instance cache:

```python
        self._cache: dict[str, int] | None = None
```

In `write()`, invalidate after the fsync succeeds:

```python
        self._cache = None
```

In `_replay()`:

```python
        if self._cache is not None:
            return dict(self._cache)
        results, _ = replay_jsonl(self._store_path, _turn_callback)
        self._cache = dict(results)
        return dict(self._cache)
```

- [ ] **Step 3: Add cleanup method and tests**

In `server/turn_store.py`, import `shutil` and add:

```python
    def cleanup(self) -> None:
        """Remove the session directory. Called on session end."""
        if self._store_dir.exists():
            shutil.rmtree(self._store_dir)
        self._cache = None
```

Test both `LineageStore.cleanup()` and `TurnStore.cleanup()` remove their session directories.

- [ ] **Step 4: Decide LineageStore cache scope before coding**

Choose exactly one option and record it in the commit body:

```text
Option A: mtime/size invalidation in LineageStore.
Option B: one shared LineageStore instance across dialogue and delegation factories.
Option C: no LineageStore cache in this phase; TurnStore-only cache plus cleanup.
```

Default to Option C unless an execution-time benchmark shows LineageStore replay dominates. Option C is acceptable because it avoids the cross-instance stale-handle bug.

**Disposition tracking (Option C defers part of HL4a).** Option C delivers the `TurnStore` half of HL4a and *defers the `LineageStore` replay cache*. If Option C is chosen, HL4a is **partially closed**, not closed: in this commit append this row to the `## Audit-Owned Deferred Watch Rows` section of `docs/status/reconciliation-register.md` (created by Task 2 Step 4; not `## Audit-Owned Active Work`), exactly as HL4b carries its own defer note in Step 5:

```markdown
| `HL4a-LINEAGE-CACHE` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | TurnStore replay cache landed (Task 12, single-instance-per-session, safe). The LineageStore replay cache is deferred because LineageStore is constructed twice per session over one shared JSONL — a per-instance cache returns stale handles. | If lineage replay is shown to dominate a real dispatch path, implement Option A (mtime/size invalidation) or Option B (one shared per-session LineageStore instance). |
```

Only Option A or Option B closes HL4a fully. Under Option C the completion report must list HL4a as partially closed (TurnStore done; LineageStore deferred), never as closed.

- [ ] **Step 5: Wire normal-shutdown cleanup and document exception retention**

This task closes HL4b only if it adds an explicit production owner and call site. Implement cleanup for normal `server.run()` return only. Do not clean session stores when `server.run()` raises; in-process server exceptions are forensic boundaries until a separate retention decision proves that deleting those stores is safe.

In `scripts/codex_runtime_bootstrap.py`, add a bootstrap-owned registry that deduplicates lazy-created stores by session directory:

```python
class _SessionStoreCleanupRegistry:
    def __init__(self) -> None:
        self._cleanup_by_dir: dict[Path, Callable[[], None]] = {}

    def register(self, store: object) -> None:
        store_dir = getattr(store, "_store_dir")
        cleanup = getattr(store, "cleanup")
        self._cleanup_by_dir[store_dir] = cleanup

    def cleanup_all(self) -> None:
        for cleanup in self._cleanup_by_dir.values():
            cleanup()
```

Thread `store_cleanup: _SessionStoreCleanupRegistry | None = None` into `_build_dialogue_factory(...)` and `_build_delegation_factory(...)`. **Do not** make it required: direct no-registry callers already exist in `tests/test_bootstrap.py`, `tests/test_delegate_start_integration.py`, and `tests/test_delegation_controller.py`, and this task should preserve that call shape rather than forcing a blind test migration. In the dialogue factory, guard the registrations:

```python
def _build_dialogue_factory(
    *,
    plugin_data_path: Path,
    control_plane: ControlPlane,
    journal: OperationJournal,
    store_cleanup: _SessionStoreCleanupRegistry | None = None,
) -> Callable[[], DialogueController]:
    ...
        lineage_store = LineageStore(plugin_data_path, session_id)
        turn_store = TurnStore(plugin_data_path, session_id)
        if store_cleanup is not None:
            store_cleanup.register(lineage_store)
            store_cleanup.register(turn_store)
```

In the delegation factory, keep the same optional shape and guard its `LineageStore` registration the same way:

```python
def _build_delegation_factory(
    *,
    plugin_data_path: Path,
    control_plane: ControlPlane,
    runtime_registry: ExecutionRuntimeRegistry,
    journal: OperationJournal,
    store_cleanup: _SessionStoreCleanupRegistry | None = None,
) -> Callable[[], DelegationController]:
    ...
        lineage_store = LineageStore(plugin_data_path, session_id)
        if store_cleanup is not None:
            store_cleanup.register(lineage_store)
```

The registry's path-keyed map is load-bearing because dialogue and delegation currently create separate `LineageStore` instances for the same `lineage/<session_id>/` directory.

In `main()`, create the registry before `McpServer(...)`, pass it into both factories, and clean only after `server.run()` returns:

```python
    store_cleanup = _SessionStoreCleanupRegistry()

    server = McpServer(
        control_plane=control_plane,
        dialogue_factory=_build_dialogue_factory(
            plugin_data_path=plugin_data_path,
            control_plane=control_plane,
            journal=journal,
            store_cleanup=store_cleanup,
        ),
        delegation_factory=_build_delegation_factory(
            plugin_data_path=plugin_data_path,
            control_plane=control_plane,
            runtime_registry=runtime_registry,
            journal=journal,
            store_cleanup=store_cleanup,
        ),
    )
    server.run()
    store_cleanup.cleanup_all()
```

These tests reuse the bootstrap harness and run inside `tests/test_bootstrap.py`, so they inherit Task 5's autouse `_bootstrap_compat_passes_by_default` fixture: that fixture rewires the test-local `_import_bootstrap()` helper to return one compat-patched module per test, so `main()`'s startup compat preflight passes without per-test patching here. Do **not** re-add compat monkeypatching in these tests, and do **not** modify `_patch_bootstrap_run` — same reasoning as Task 5 Step 1.

Leave the existing direct-call tests for `_build_dialogue_factory(...)` / `_build_delegation_factory(...)` unchanged. Their current no-`store_cleanup` call sites are the regression proof that the optional path still works; the new cleanup behavior is proven by the new `main()` tests above, not by changing every caller.

Add tests in `tests/test_bootstrap.py` that prove:

```python
def test_bootstrap_cleans_session_stores_after_server_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _import_bootstrap()
    _patch_bootstrap_run(monkeypatch, mod, tmp_path)
    (tmp_path / "session_id").write_text("sess-cleanup", encoding="utf-8")

    def run_with_controllers(self: object) -> None:
        self._ensure_dialogue_controller()
        self._ensure_delegation_controller()

    monkeypatch.setattr(mod.McpServer, "run", run_with_controllers)

    mod.main()

    assert not (tmp_path / "lineage" / "sess-cleanup").exists()
    assert not (tmp_path / "turns" / "sess-cleanup").exists()
```

```python
def test_bootstrap_preserves_session_stores_when_server_run_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _import_bootstrap()
    _patch_bootstrap_run(monkeypatch, mod, tmp_path)
    (tmp_path / "session_id").write_text("sess-cleanup-error", encoding="utf-8")

    def fail_run(self: object) -> None:
        self._ensure_dialogue_controller()
        self._ensure_delegation_controller()
        raise RuntimeError("server stopped")

    monkeypatch.setattr(mod.McpServer, "run", fail_run)

    with pytest.raises(RuntimeError, match="server stopped"):
        mod.main()

    assert (tmp_path / "lineage" / "sess-cleanup-error").exists()
    assert (tmp_path / "turns" / "sess-cleanup-error").exists()
```

Update `docs/specs/contracts.md` and `docs/specs/recovery-and-journal.md` in the same commit to state the exact retention policy: normal `server.run()` return cleans registered session-store directories; in-process server exceptions, hard crash, process kill, or machine shutdown preserve them for recovery/forensics until a separate startup-prune owner is implemented. If execution chooses not to add the bootstrap cleanup owner, mark HL4b deferred in `docs/status/reconciliation-register.md` and do not count HL4b as closed.

- [ ] **Step 6: Verify and commit**

Run:

```bash
uv run pytest tests/test_turn_store.py tests/test_lineage_store.py tests/test_bootstrap.py tests/test_delegate_start_integration.py tests/test_delegation_controller.py::test_bootstrap_factory_wires_promotion_callback -q
uv run ruff check server/turn_store.py server/lineage_store.py scripts/codex_runtime_bootstrap.py tests/test_turn_store.py tests/test_lineage_store.py tests/test_bootstrap.py
git add server/turn_store.py server/lineage_store.py scripts/codex_runtime_bootstrap.py tests/test_turn_store.py tests/test_lineage_store.py tests/test_bootstrap.py docs/specs/contracts.md docs/specs/recovery-and-journal.md docs/status/reconciliation-register.md
git commit -m "perf: cache turn replay and clarify store cleanup"
```

Expected:

```text
Selected tests pass, including the unchanged no-`store_cleanup` factory callers.
Ruff passes.
Commit created.
```

---

### Phase 4 Continues: Task 12 → Task 13 (same branch)

- [ ] No phase boundary here. Task 13 (ST1/ST3/WL strategic+watch rows) continues on `chore/debt-codex-cluster` and is the last task in Phase 4 (and the plan).
- [ ] After Task 13, run the Phase 4 Close Gate for `chore/debt-codex-cluster` (marker-inclusive `-m ""`), complete its remote-write sequence with the two approval stops, then run the Final Verification Gate.

### Task 13: Record Strategic And Watch Decisions Without Over-Implementing

**Audit items:** ST1, ST3, WL1–WL6, Open Questions 3 and 5. WL6 = Step 3; WL1/WL2/WL4/WL5 = Step 4b; WL3 is dispositioned in Task 2 (Step 5b). HL2-xdist and HL4a-lineage carry their own defer rows in Tasks 7 and 12 — Task 13 does not re-own them.

**Files:**
- Modify: `docs/status/reconciliation-register.md`
- Modify: `docs/specs/recovery-and-journal.md`
- Create: `docs/tickets/2026-05-16-codex-app-server-contract-versioning.md`

- [ ] **Step 1: Record ST3 as a roadmap item, not a code task**

Create `docs/tickets/2026-05-16-codex-app-server-contract-versioning.md` only after HL1 is merged:

```markdown
---
id: T-20260516-02
title: Decide Codex App Server contract-version assertion
status: open
created: 2026-05-16
---

# Decide Codex App Server contract-version assertion

## Current state

The JSON-RPC `"2.0"` field is the JSON-RPC protocol version, not a Codex App Server contract version. Payload-shape tests now cover the vendored schema boundary, but runtime negotiation still has no explicit contract-version assertion.

## Relationship to QW4 (stopgap)

QW4 (the Task 5 startup compatibility preflight) is an explicit **stopgap on this roadmap line, not a substitute for ST3**. QW4 converts a silent mid-session version mismatch into a clean startup failure; it does **not** protect against silent wire-format drift within a "compatible" version. Only HL1 (payload-shape contract tests) plus this ST3 contract-version decision close that gap. Risk the audit calls out explicitly: QW4 feels like "done" and ST3 never gets scheduled — this ticket exists so it does.

## Exit condition

Land a design that either adds a clear contract-version assertion point at startup or records why vendored schema plus live method probing is the v1 compatibility boundary.
```

- [ ] **Step 2: Resolve unknown-terminal audit-event question deliberately**

In `docs/specs/recovery-and-journal.md`, add a short note under Unknown Request Handling:

```markdown
Unknown terminalization continues to use the persisted `PendingServerRequest(kind="unknown")` plus `DelegationOutcomeRecord(terminal_status="unknown")` as its provenance record. It does not emit an `AuditEvent` unless a later ADR changes the AuditEvent-vs-OutcomeRecord split.
```

Do not add an unknown-terminal audit event in this plan.

- [ ] **Step 3: Preserve WL6 as a trigger, not a quick win**

Append this row to the `## Audit-Owned Deferred Watch Rows` section of `docs/status/reconciliation-register.md` (created by Task 2 Step 4; its last cell is the watch trigger — not `## Audit-Owned Active Work`):

```markdown
| `WL6-CONCURRENT-PROMOTION-LOCK` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | The startup-overlap warning is only an operator-awareness patch. The actual cross-process promotion race remains open by design at solo single-session scale. | Promote to an implementation ticket if broad marketplace distribution is actively pursued or routine multi-session use begins. |
```

- [ ] **Step 4: Record ST1 trigger**

Append this row to the `## Audit-Owned Deferred Watch Rows` section of `docs/status/reconciliation-register.md` (created by Task 2 Step 4; its last cell is the watch trigger — not `## Audit-Owned Active Work`):

```markdown
| `ST1-KNOWLEDGE-TRANSFER` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | Bus factor remains one by construction. No handoff trigger is currently active. | If onboarding, transition, or more than one-quarter unavailability becomes real, create module notes for `delegation_controller.py`, `journal.py`, and `control_plane.py`, preferably after HL3 has landed. |
```

- [ ] **Step 4b: Record the remaining Watch List items (WL1, WL2, WL4, WL5) with the audit's exact triggers**

The audit's Watch List has six rows. WL6 is Step 3; WL3 is dispositioned in Task 2 (foundations.md sentence + the `WL3-LAYERING-CI-ASSERT` defer row); HL2-xdist and HL4a-lineage carry their own defer rows in Tasks 7 and 12. The remaining four (WL1, WL2, WL4, WL5) must each get a watch row so the plan's coverage claim is true rather than aspirational.

**Re-derive from the audit before pasting (authority Stop Condition).** The figures below were transcribed from the audit at plan-authoring time; the audit is the owning artifact and its content can drift from a transcription (the QW4 footer desync proves this). Before committing, run `git show 46e8750:docs/audits/2026-05-15-codex-collaboration-debt.md` and confirm the audit's Watch List section still states exactly six rows and that WL1/WL2/WL4/WL5's load-bearing triggers match the values below (WL1 `15/28 importers` / `~800 LOC`; WL4 `4h` / `10 MB`; WL2 test-double trigger; WL5 `TYPE_CHECKING` session-hold). If any differ, the audit wins — paste the audit's current values, not the stale block below, and note the reconciliation in the phase commit body. Then append these rows to the `## Audit-Owned Deferred Watch Rows` section of `docs/status/reconciliation-register.md` (created by Task 2 Step 4; not `## Audit-Owned Active Work`):

```markdown
| `WL1-MODELS-MEGAHUB` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | `models.py` is a flat-domain hub (15/28 importers). Clean today; compounds as capabilities are added. | When `models.py` > ~800 LOC **or** a 2nd capability domain is added → split into advisory/execution/infrastructure modules with a re-export shim. |
| `WL2-ANY-TYPED-CONTROLLERS` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | Controllers are `Any`-typed at the MCP boundary (no protocol seam); mitigated only because integration tests use the real controller types. | If integration tests shift to test doubles for speed/isolation → promote to P2 and add `_interfaces.py` protocols. |
| `WL4-UNBOUNDED-AUDIT-LOG` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | Intra-session audit/outcomes log is pruned only at startup. Documented v1 limitation; theoretical at solo scale. | If session duration regularly > 4h **or** `audit/events.jsonl` > 10 MB → implement periodic pruning. |
| `WL5-MODELS-HOLDS-SESSION` | `deferred` | `docs/audits/2026-05-15-codex-collaboration-debt.md` | `models.py` holds a live `AppServerRuntimeSession` via `TYPE_CHECKING`. No runtime cost; conceptual layer oddity. | If `AdvisoryRuntimeState` ever needs JSON serialization or independent mocking → move the session field to a `control_plane.py` wrapper. |
```

After this step, every audit Watch List row (WL1–WL6) has an explicit disposition somewhere in this plan, and HL2-xdist / HL4a-lineage carry parallel defer rows. The Self-Review Notes coverage claim is now literally true.

- [ ] **Step 5: Verify and commit**

Run:

```bash
uv run ruff check .
git add docs/status/reconciliation-register.md docs/specs/recovery-and-journal.md docs/tickets/2026-05-16-codex-app-server-contract-versioning.md
git commit -m "docs: record strategic debt triggers"
```

Expected:

```text
Ruff passes.
Commit created.
```

---

## Final Verification Gate

Run after the last phase being claimed complete. Task 7 *always* installs the local-fast/full split (it is a decision, not an option — see "Suite Mode After HL2"), so a bare `pytest tests -q` here is fast-only and is NOT the full-suite gate. The marker-inclusive run is mandatory:

```bash
uv run pytest tests -q -m ""
uv run ruff check .
git status --short --branch
```

Expected:

```text
Full marker-inclusive suite passes (slow timeout-path and live-runtime tests included).
0 unexpected skips in tests/test_codex_wire_contract.py (the HL1 contract gate actually ran).
Ruff passes.
Git status shows only intentional branch divergence and no unstaged edits.
```

A "full suite passes" claim here based on a bare `pytest tests -q` (no `-m ""`) is invalid and must be re-run.

## Completion Report Checklist

The final completion report must list:

- Commit hashes per phase.
- Confirmation that the Audit Publication Gate landed `docs/audits/2026-05-15-codex-collaboration-debt.md` on `main` via a **PR merged with a merge commit (squash/rebase disabled)** with its `e7b551b..46e8750` revision history intact and the PR's CI green **before** the plan-publication PR and any phase branch, and that no reconciliation-register or spec row references the audit while it is absent from the tree.
- Confirmation that each code phase's API Pre-Flight baselines held (or, if one drifted, how the affected task's pasted code was reconciled before the TDD loop).
- Which audit IDs are closed vs. partially closed vs. deferred. State precisely:
  - QW1–QW9: closed or declined (with owning artifact).
  - HL1: **closed only if every builder validates with zero `xfail`s**. Otherwise report HL1 as **partial/degraded**, name the xfailed case, the fix ticket, the ST2 block, and whether Phase 4 proceeded only on the `_build_response_payload` mapper-invariant basis.
  - HL2: **partially closed** — fast/slow split + window injection done; xdist deferred (`HL2-XDIST-PARALLELIZATION` row).
  - HL3, HL5: closed or deferred.
  - HL4a: **closed only if Option A/B**; under default Option C it is **partially closed** (TurnStore done; `HL4a-LINEAGE-CACHE` deferred). HL4b: closed only if the Step 5 owner was implemented, else deferred.
  - ST2 tracking, ST3 tracking; WL1–WL6 each mapped to their disposition row.
- Any declined/deferred item and the exact owning artifact/register row that records the decision. A deferred component reported as "closed" is a defective completion report.
- Whether `server/codex_compat.py` version pins changed.
- Whether CI still runs slow timeout-path tests (`ci.yml` uses `-m ""`), and confirmation that every full-suite gate from Phase 2 onward (after Task 7 added `addopts`) was run with `-m ""`, not a bare invocation.
- Whether the HL1 contract suite executed (0 unexpected skips) or skipped — a skipped contract gate is not a closed HL1.
- Whether live Codex verification was run or skipped, with the concrete reason.

## Self-Review Notes

- Spec coverage: every audit item has a task, an explicit partial-close defer row, or a watch/trigger row. WL1–WL6 each have a register row (WL6 Task 13 Step 3; WL1/2/4/5 Step 4b; WL3 Task 2 Step 5b). HL2-xdist and HL4a-lineage carry explicit defer rows in Tasks 7 and 12, so HL2 and (under Option C) HL4a are reported partially closed, never closed. QW3 and QW5 preserve the audit's split boundaries. **Ordering constraint:** HL2 (Phase 2) precedes both HL1 and HL5 (Phase 3); HL1 and HL5 are mutually independent, so Task 8 (HL5) running before Task 9 (HL1) inside Phase 3 does not violate the audit's HL2-first rationale (see "HL ordering — precise constraint"). ST2 execution (not Task 10 tracking) waits for HL1 fully green; a degraded HL1 close may carry Phase 4 only on the narrower mapper-invariant basis. **Structure:** decision D (risk-tiered) — 4 work PRs + 1 plan-publication PR + 1 audit-publication PR (merge commit, no squash/rebase), justified in "Phase-count rationale (decision D)".
- Placeholder scan: no task uses open-ended filler or unspecified test coverage as an acceptance criterion.
- Type consistency: new names are consistent across tasks: `TOOL_PREFIX`, `_ServerRequestHandlerState`, `approval_window_seconds`, and `T-20260516-*`.
- Prerequisite integrity: the audit (owning artifact for every register row) reaches `main` via the Audit Publication Gate before any phase branch is created; an API Pre-Flight gate verifies the private-symbol baselines this plan's pasted code assumes (`_build_response_payload` self-freeness, `ControlPlane.compat_checker`, `McpServer._ensure_*`, `_build_controller`, `AppServerRuntimeSession.__init__` attrs) before each TDD loop, so verification precedes the dependent code rather than being asserted circularly inside it. **Caveat (post-scrutiny):** the Phase 2/Task 7 Pre-Flight row originally named a non-existent env var, proving the Pre-Flight table was not fully executed against the live tree at authoring time. That row is corrected and every other row was re-verified live (see the API Pre-Flight table note); the anti-circularity property holds only because the rows are now confirmed accurate, not by construction.
- Shared-helper integrity: `_patch_bootstrap_run` is never mutated; Task 5's startup-compat default is an explicit autouse fixture (`raising=True`, fail-fast) that patches one bootstrap module per test and rewires the local `_import_bootstrap()` helper to return that same module. Task 12 inherits that fixture by reference rather than re-patching — no hidden cross-phase coupling through a rewritten helper or a throwaway module patch.
- **Scrutiny revision (2026-05-16, post-adversarial-review).** Six defects found by a reject-until-credible review were patched in place: (1) **Critical** — Task 7's `slow` marker was never applied to any test, making `addopts = "-m 'not slow'"` deselect the empty set and the entire "Suite Mode After HL2" apparatus inert; fixed by adding Step 3b (populate the marker on the live-runtime tier), a hard non-empty collection-count gate in Step 5, and a Stop Condition with an explicit "remove the apparatus instead" alternative. (2) the Audit Publication Gate's unattended `git push origin main` now stops for a local full-suite run + explicit maintainer confirmation (honors the standing ask-before-push rule; the only un-PR'd/un-CI'd publish gets the strongest human gate, not the weakest). (3) Task 6 (QW3) is reclassified as a trust-path + authority-owned-spec change with a dedicated full promotion/recovery verification and a pinned last-in-Phase-1 position. (4) the "Phase 1 is independent" license is bounded by the register dependency (Task 2 must land before any later register-append task) with an append-anchor convention. (5) the wrong Pre-Flight baseline is corrected and all rows re-verified. (6) a generalized authority Stop Condition + Task 13 re-derivation step prevent the plan from becoming the de facto source for audit-owned figures. Findings 1/5/6 shared a root cause (governance accreted faster than it was executed against the tree); 2/3/4 shared another (PR-count optimization without re-deriving revert boundaries).
- **Scrutiny revision (2026-05-16, second post-adversarial-review pass).** A later reject-until-credible review found five more defects, all verified against the live repo before patching: (1) **[high]** Task 9/HL1's contract test imported `build_workspace_write_sandbox_policy` but exercised only `_build_read_only_sandbox_policy()` — a real `ruff F401` in the pasted code and, worse, the workspace-write `turn/start` `sandboxPolicy` (the shape the real delegation path sends, `delegation_controller.py` `run_execution_turn`; flagged security-adjacent in audit §HL1) went unvalidated; fixed by adding a workspace-write execution turn plus a self-protecting assertion that a `workspaceWrite` `turn/start` was captured (so deleting the import to silence lint now fails loudly). (2) **[high]** the Audit Publication Gate's no-PR `git push origin main` (prior pass's finding 2) is **superseded**: confirmed `allow_merge_commit: true`, so the audit now lands via a PR merged with a merge commit (squash/rebase forbidden) — same provenance, real CI, conforms to AGENTS.md, no convention-exception debt — plus a post-merge red-`main` protocol that the no-PR model lacked. (3) **[moderate]** the "watch section" anchor was referenced at ~9 sites but no task created it; Task 2 Step 4 now creates a distinct `## Audit-Owned Deferred Watch Rows` section (Watch-trigger column) and every watch-row site names it explicitly. (4) **[moderate]** "CI always exercises slow tests" overclaimed (CI does not install `codex`; the live tier `skipif`-skips) — reworded to "marker-inclusive collection; live tier collected but skipped". (5) **[low]** Task 7 Step 5's `pytest -m slow --co -q -m ""` is argparse last-wins and proves nothing; replaced with one unambiguous command. Prior-pass finding 2's text above is retained as history but no longer describes the gate.
- **Scrutiny revision (2026-05-16, third post-adversarial-review pass).** A later live-tree review found four more executable defects and this revision patches each one in the plan itself: (1) **[critical]** Task 5's default-pass compat fixture originally patched a throwaway bootstrap module even though `_import_bootstrap()` returns a fresh `module_from_spec()` object on every call; fixed by requiring the autouse fixture to rebind the test-local `_import_bootstrap()` helper to the same patched module instance for the duration of each test, with the Task 5 API Pre-Flight row calling out that import semantic explicitly. (2) **[high]** Task 6's rollback event plan was not crash-safe for the state `unresolved promotion journal + job already rolled_back + no rollback audit event`; fixed by adding a crash-window backfill test, an explicit replay-idempotency guard test, and a recovery rule that backfills the missing rollback event before `promotion:completed` while avoiding duplicates when the event already exists. (3) **[medium]** Task 12 previously made `store_cleanup` a silent required factory-signature expansion even though live no-registry callers remain in `tests/test_bootstrap.py`, `tests/test_delegate_start_integration.py`, and `tests/test_delegation_controller.py`; fixed by making `store_cleanup` optional by design, preserving unchanged caller coverage, and expanding Task 12's verification command to include those direct-call tests. (4) **[medium]** Task 6's proof grep could pass from code alone while the contracts row was absent; fixed by splitting the verification into file-specific checks for the Markdown table row and the controller emitter/helper. The common root cause was the same one the scrutiny named directly: governance and sequencing were stronger than the pasted execution snippets, so the repair here was to bind the snippets back to the live harness and replay semantics.
- **Scrutiny revision (2026-05-16, fourth post-adversarial-review pass).** A later reject-until-credible review found five more control-document defects, all patched here before execution begins: (1) **[critical]** Task 6's rollback-event existence checks and test helper were crash-intolerant on malformed audit lines even though `recovery-and-journal.md` makes JSON parse failures record-local; fixed by making both helpers tolerate `JSONDecodeError` and by adding an explicit malformed-audit-line recovery test. (2) **[high]** the standing ask-before rule was enforced only for the audit PR; fixed by applying the same two-stop approval model to the plan-publication PR and every phase PR/push/merge path. (3) **[high]** Task 6's rollback-event spec fan-out omitted `docs/specs/recovery-and-journal.md`; fixed by adding the emitted-trigger row and verifying all three authority surfaces together. (4) **[high]** HL1's degraded `xfail(strict=True)` branch was underspecified; fixed by marking that branch as partial/degraded rather than "closed", blocking ST2 execution, and defining the only allowed Phase 4 continuation as the narrower `_build_response_payload` mapper-invariant basis. (5) **[medium]** HL2's verification-command doc sync omitted `README.md`; fixed by bringing README into the same truth-maintenance commit as `.claude/CLAUDE.md` and `AGENTS.md`. The common pattern was invariant propagation failure: one strengthened surface still left its adjacent execution or authority surface stale.
- **Scrutiny revision (2026-05-16, fifth post-adversarial-review pass).** A later live-tree scrutiny found three remaining control-surface defects and this revision patches each one explicitly: (1) **[high]** Task 6's "old wording is gone" grep was unsatisfiable because the broad `no .*event.*emitted` pattern already matched an unrelated valid transition row in `promotion-protocol.md`; fixed by narrowing the verification to the two exact obsolete rollback phrases only. (2) **[high]** Task 1's shared-constant refactor previously widened `codex_guard.py`'s startup dependency by importing `consultation_safety` at module import time; fixed by moving `TOOL_PREFIX` into a tiny new `server/tool_prefix.py` module and by adding a regression test that non-plugin tools still pass through even when policy import would fail. (3) **[medium-high]** Task 5 previously froze the startup compatibility result into `ControlPlane` via `compat_checker=lambda: compat_result`, silently regressing the live drift semantics that `test_codex_status_invalidates_cached_runtime_on_compat_drift` proves; fixed by explicitly choosing "startup preflight + ongoing diagnostics", leaving `ControlPlane` on the live checker, and adding a bootstrap-level regression test that no frozen checker override is injected. The common root cause was the one the scrutiny named directly: control-document invariants were specified, but the adjacent execution surfaces had not been re-derived tightly enough.
- **Scrutiny revision (2026-05-16, sixth post-adversarial-review pass).** A later live-tree validation found four remaining executable defects in the plan text itself, all patched here before execution begins: (1) **[high]** Task 6 still referenced the stale node id `test_promote_rolls_back_when_post_apply_verification_fails` even though the live test is `test_promote_rolls_back_when_primary_workspace_verification_fails`; fixed in both the prose and the runnable pytest command so the task no longer dead-ends on collection. (2) **[high]** Task 7's commit command omitted `README.md` even though Step 4c made README part of the same verification-truth update; fixed by staging `README.md` in the Task 7 commit snippet so the commit shape matches the declared file set. (3) **[moderate]** the Audit Publication Gate previously compared `chore/tech-debt-audit` against local `main`, which is only safe while local `main == origin/main`; fixed by anchoring the proof to `origin/main`, the actual PR base. (4) **[moderate]** Task 6's malformed-JSON tolerance wording did not state the invalid-UTF-8 boundary even though the repo contract gives UTF-8 corruption to startup prune/quarantine; fixed by making that precondition explicit in the helper notes and replay rules so the controller task does not accidentally claim journal-owned quarantine behavior. The common root cause was again execution-surface drift: the control logic was mostly right, but a few pasted command and ownership details had not been re-validated tightly enough against the live tree.
