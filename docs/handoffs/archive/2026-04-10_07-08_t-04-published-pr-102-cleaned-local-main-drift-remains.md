---
date: 2026-04-10
time: "07:08"
created_at: "2026-04-10T07:08:26Z"
session_id: bde86ee0-a9f4-4eaf-962e-19195c61e59f
resumed_from: /Users/jp/.codex/handoffs/claude-code-tool-dev/.archive/2026-04-10_01-02_b4-complete-pr-101-merged-follow-up-tickets-filed.md
project: claude-code-tool-dev
branch: fix/clean-stale-shakedown-script-conventions
commit: 8649ef04
title: T-04 published cleanly after PR #102 rebuild; local main drift remains
type: handoff
files:
  - /Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py
  - /Users/jp/Projects/active/claude-code-tool-dev/docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md
  - /Users/jp/Projects/active/claude-code-tool-dev/docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md
  - /Users/jp/Projects/active/claude-code-tool-dev/docs/tickets/2026-04-10-T-20260410-04-align-cleanstaleshakedownpy-with-script-convention.md
  - /Users/jp/Projects/active/claude-code-tool-dev/.claude/rules/workflow/git.md
---

# Handoff: T-04 published cleanly after PR #102 rebuild; local main drift remains

## Goal

This session began by explicitly resuming the archived handoff at:

- `/Users/jp/.codex/handoffs/claude-code-tool-dev/.archive/2026-04-10_01-02_b4-complete-pr-101-merged-follow-up-tickets-filed.md`

That handoff said B4 was complete and that the remaining work was operational and
follow-up oriented rather than delivery oriented:

- clean up the B4 worktree and any leftover MCP process state
- decide how to restore the canonical repo after the worktree was removed
- choose the next ticket instead of reopening B4 broadly
- if doing ticket work, start from one of the deferred follow-ups rather than
  from vague “clean up B4”

The session objective evolved in two stages.

Stage 1 was operational cleanup:

- remove the B4 worktree safely
- verify whether the work had actually been lost or only removed from the local
  checkout
- fix the canonical repo state so the merged B4 files were present on disk again

Stage 2 was ticket execution and publication hygiene:

- take the smallest deferred hardening ticket, T-20260410-04
- scrutinize the actual wrapper script against the ticket, not just the
  self-reported completion note
- get the fix onto a dedicated branch and into a PR
- repair the PR if publication scope turned out to be polluted

The stakes were not feature-delivery stakes anymore.

They were provenance and workflow stakes.

If the repo remained in a split-brain state, future sessions would keep reading
the wrong checkout from the canonical path.

If the T-04 branch stayed polluted with handoff commits, a reviewable one-file fix
would instead look like a noisy multi-file docs branch.

If those two state problems were not solved before starting T-02 or T-03, the
next session would inherit broken footing and would spend time rediscovering
branch state rather than doing the next hardening task.

Success criteria for this session became:

- local canonical repo regains the merged B4 files on disk
- runtime-verified commit `7f4eed41` becomes reachable from local `main`
- T-04 lands as a single coherent commit on a dedicated `fix/*` branch
- PR #102 is reduced to one commit and one changed file
- no new T-02 or T-03 work is started before the publication surface is clean
- the session ends at a clean stopping point with a save-ready handoff

Connection to the broader project arc:

- B4 remains complete and merged via PR #101 at `b964be63`
- this session is the first post-B4 cleanup/hardening session
- T-04 is now isolated and reviewable
- T-02 and T-03 remain deferred and untouched

## Session Narrative

1. The session opened from an explicit `handoff:load`, not from an empty state.
   I loaded the archived “B4 complete via PR #101; follow-up tickets and cleanup
   notes filed” handoff and wrote the resume-state pointer as required by the
   handoff chain protocol.

2. The user’s first direction after load was direct and narrow:
   “Continue with operational cleanup”.
   That immediately constrained the work away from new implementation and toward
   repo/process cleanup.

3. I verified the operational targets before touching anything.
   `git worktree list --porcelain` still showed the B4 worktree at
   `/Users/jp/Projects/active/claude-code-tool-dev-t8-impl`.
   `git -C ... status --short --branch` showed the worktree branch
   `feature/b4-agent-skill-harness-assembly` was clean.
   `git -C /Users/jp/Projects/active/claude-code-tool-dev status --short --branch`
   showed local `main` was already divergent from `origin/main` and had the
   untracked archive file
   `docs/handoffs/archive/2026-04-09_01-37_t4-publication-and-security-review.md`.

4. I also checked the reported MCP process cleanup target.
   The earlier handoff referenced PID `22692`.
   The process scan did not show that PID or any live command still referencing
   the removed worktree path.
   That mattered because it reduced the cleanup sequence to worktree cleanup
   rather than process-first triage.

5. I verified that the feature tip was safe to remove as a worktree.
   `git merge-base --is-ancestor ad27127a... origin/main` succeeded.
   `git branch -r --contains ad27127a` showed both
   `origin/feature/b4-agent-skill-harness-assembly` and `origin/main`.
   This was enough to conclude that removing the worktree would not orphan the
   actual B4 code.

6. `git worktree remove` failed in the sandbox because `.git/worktrees/...`
   required unrestricted write access.
   I escalated that one operation, removed the worktree, and verified the path
   was gone and that `git worktree list --porcelain` now showed only the main
   repo.

7. I then attempted the non-force local branch delete.
   Git’s own warning said the branch was merged to
   `origin/feature/b4-agent-skill-harness-assembly` but not to local `HEAD`.
   The real blocker was sandboxed `.git/refs/...lock` creation.
   I requested escalation for `git branch -d`, and the user rejected it.
   I stopped there and left the local branch intact.

8. That led directly to the user’s most important correctness challenge of the
   session:
   “Wait. We just removed the worktree, but some of the files like the dialogue
   skill were on that worktree and they aren't at
   `/Users/jp/Projects/active/claude-code-tool-dev`. Did we just lose work?”

9. I checked the actual object graph instead of answering from intuition.
   The result was clear:
   `git ls-tree origin/main packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md`
   returned the file, and the same was true for the preserved feature branch.
   The file was missing only from the current filesystem checkout because local
   `HEAD` was still old `main`.
   So the work was not lost in Git; only the checkout had not yet moved to a ref
   containing it.

10. The user then invoked the recommendation workflow and asked for the
    objectively best next step.
    My first answer recommended creating a fresh worktree from `origin/main`.
    That answer was materially wrong in framing and in verification depth.

11. The user’s scrutiny of that recommendation was one of the most important
    turning points in the session.
    They explicitly said:
    “The analysis is solving a misframed problem.”
    They also called out what they saw as “verifiability theater”.
    Those were not rhetorical complaints.
    They were backed by concrete checks showing that local-only handoff commits
    on `main` were path-disjoint from PR #101’s merged B4 files and that
    branch-protection semantics made a fresh `main` worktree a scaffolding step,
    not a real solution.

12. I reran the missing checks instead of defending the earlier answer.
    `git diff --name-only origin/main...main -- ':!docs/handoffs/' ':!docs/handoffs/archive/'`
    returned nothing.
    `git merge-base --is-ancestor 7f4eed41 main; echo $?` returned `1`,
    confirming that local `main` still did not reach the runtime-verified SHA.
    Reading `.claude/rules/workflow/git.md` confirmed that `main` is protected in
    every worktree and that feature branches are the expected place for edits.

13. Once those facts were in hand, the right recommendation became clear:
    rebase local `main` onto `origin/main`, then branch later for actual code
    work.
    The user scrutinized that revised answer too and improved it:
    mandatory safety tag, explicit `git pull --rebase origin main`, explicit
    post-rebase verification, and explicit acknowledgment that the untracked
    archive file was separate cleanup rather than a blocker.

14. I then executed the corrected sequence.
    First attempt to create the safety tag hit the expected sandbox ref-lock
    restriction.
    After escalation, `git tag backup-main-pre-b4-rebase` succeeded.
    Then `git pull --rebase origin main` also needed escalation because it writes
    `.git/FETCH_HEAD`.
    The rebase replayed all 14 local handoff commits cleanly and updated local
    `main` without any conflict.

15. Post-rebase verification was the strongest execution checkpoint in the
    session:
    `git merge-base --is-ancestor 7f4eed41 main` returned success,
    `git rev-list --left-right --count origin/main...main` returned `0	14`,
    `git status --short --branch` showed local `main` ahead only,
    and the file-presence check for
    `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md`
    returned `present`.

16. After the canonical repo was repaired, the user asked for the next direction.
    I compared T-02, T-03, and T-04.
    I recommended T-04 because it was the smallest scoped hardening ticket with
    the clearest acceptance criteria and the lowest risk-to-progress ratio after a
    session dominated by branch-state cleanup.

17. The user then supplied a response contract claiming T-04 was already
    implemented.
    The important move here was not to trust the write-up.
    I read the actual file
    `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py`,
    its sibling scripts, and the T-04 ticket itself.
    That revealed two real gaps:
    the outer error boundary did not catch import-time failures because the
    `server.containment` import still lived at module scope, and the wrapper did
    not yet mirror the sibling scripts’ `expanduser().resolve()` path
    normalization behavior.

18. The user then supplied a second response contract for “post-scrutiny fixes”.
    When I reopened the actual file, it already contained the corrected shape:
    import moved inside `main()`, env normalization via
    `Path(plugin_data).expanduser().resolve()`, distinct error messages, and use
    of normalized `data_dir`.
    That is important attribution:
    by the time I verified the final T-04 code, the file was already edited in the
    workspace; my contribution there was validation and publication, not the final
    code edit itself.

19. Verification itself had its own pivot.
    `uv run pytest` in `packages/plugins/codex-collaboration` passed with
    `519 passed in 3.94s`.
    But `uv run ruff check` at the package root failed because of unrelated,
    pre-existing lint errors in `codex_runtime_bootstrap.py`, `tests/conftest.py`,
    `tests/test_credential_scan.py`, and `tests/test_dialogue_profiles.py`.
    That meant package-wide Ruff was not a valid signal for T-04 correctness.
    I switched to the file-scoped check
    `uv run ruff check scripts/clean_stale_shakedown.py`, which passed.

20. The subprocess smoke checks also surfaced one procedural trap.
    I ran the happy-path temp-dir check in parallel with the import-failure
    simulation that temporarily moved `server/containment.py`.
    The happy-path result then failed with the same `ModuleNotFoundError` as the
    import test, not because the wrapper was broken, but because the two commands
    overlapped.
    I recognized that as invalid evidence, verified that `server/containment.py`
    had been restored, and reran the happy-path check in isolation.

21. The final T-04 verification matrix was therefore sound:
    unset env, empty env, nonexistent path, valid temp dir, literal tilde path,
    and simulated `ModuleNotFoundError` all behaved as expected.
    That closed both scrutiny findings.

22. I staged only the wrapper file and committed it as a single coherent fix
    commit:
    `b39d8d90 fix(shakedown): align clean_stale_shakedown conventions`.
    The unrelated untracked archive file remained untouched.

23. The user then surfaced a stale review finding that repeated the earlier
    env-normalization complaint.
    I checked the actual committed file with numbered lines and confirmed that
    lines 29-30 already used `expanduser().resolve()` and then validated the
    normalized `data_dir`.
    That meant the finding was outdated, not actionable.

24. I recommended publishing T-04, and the user agreed.
    I pushed the branch and opened draft PR #102:
    `https://github.com/jpsweeney97/claude-code-tool-dev/pull/102`.

25. A deeper publication bug then surfaced.
    I checked the actual PR diff and discovered that PR #102 was polluted.
    `git log origin/main..fix/clean-stale-shakedown-script-conventions` showed
    the T-04 commit on top of 14 handoff commits.
    `git diff --name-only origin/main...fix/clean-stale-shakedown-script-conventions`
    showed seven archived handoff files plus
    `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py`.
    The branch had been cut from local `main`, and local `main` was still ahead of
    `origin/main` by the handoff archive commits even after the rebase.

26. That publication-scope bug became the new highest-priority issue.
    I explicitly advised against starting T-02 or T-03 while PR #102 was polluted.
    The user drafted a rebuild plan using safety tags, reset, cherry-pick, and
    `--force-with-lease`.
    I reviewed that plan, tightened it with `git fetch origin`, stronger
    verification, and removal of the invalid “push local main” future option, and
    then the user executed the rebuild outside my tool calls.

27. The user returned with the rebuilt result:
    branch tip rewritten from `b39d8d90` to `8649ef04`,
    PR reduced from 15 commits / 8 files to 1 commit / 1 file,
    and backup tags created.
    I verified with GitHub and local Git that the cleaned branch state was real.

28. There was one last subtle trap.
    `gh pr diff --name-only 102` initially returned stale data after the
    force-push.
    The user reran it and got the correct single-file result.
    Cross-checking with GitHub PR metadata (`commits: 1`, `changed_files: 1`) and
    local `git diff --name-only origin/main...HEAD` confirmed the PR was actually
    clean.
    The first `gh pr diff` result was stale cache, not real branch state.

29. With PR #102 clean and no further blocking work in flight, I recommended
    stopping and saving instead of immediately taking T-02 or T-03.
    I checked the PR body for stale `b39d8d90` references before making that
    recommendation.
    The body contained no hard-coded old SHA references, so there was no need for
    an extra PR-body polish pass before saving.

30. The user then invoked `handoff:save`.
    This handoff is the save artifact for the session.

## Decisions

### Decision 1: Repair canonical local `main` via rebase, not by creating a new worktree

**Decision:** Rebase local `main` onto `origin/main` using a mandatory safety tag
and explicit verification, rather than creating a fresh `origin/main` worktree.

- **Driver:** The user’s scrutiny correctly reframed the problem away from
  “get the files back on disk” and toward “recover a workable canonical
  environment”. The user’s wording was explicit:
  “The analysis is solving a misframed problem.”
  They also backed the critique with the disjointness check that I had failed to
  run in the first recommendation.
- **Rejected:** Create a fresh worktree from `origin/main`.
  Rejected because `.claude/rules/workflow/git.md` says `main` is protected in all
  worktrees, so a fresh `main` worktree would still require an immediate feature
  branch before edits, while leaving the canonical repo stale.
  The user also correctly identified the split-brain risk for handoff paths,
  `.claude` config, and MCP-server path assumptions.
- **Rejected:** Do nothing and accept that the merged B4 files exist only in Git
  history or a secondary path.
  Rejected because `git merge-base --is-ancestor 7f4eed41 main` returned exit `1`
  before the rebase, meaning the canonical local repo did not even reach the
  runtime-verified SHA.
- **Implication:** After the rebase, the canonical repo path again matches merged
  B4 state, and future file references from the main checkout no longer require a
  secondary worktree.
- **Trade-offs:** Rebase rewrote the SHAs of the 14 local handoff commits sitting
  on `main`. That cost was accepted because the tree changes were preserved and
  the safety tag `backup-main-pre-b4-rebase` made reversal straightforward.
- **Confidence:** High (E3) — based on the user’s independent disjointness check,
  my rerun of the disjointness and reachability commands, and the successful
  clean rebase + post-rebase verification.
- **Reversibility:** High — `backup-main-pre-b4-rebase` points to `51028978`, so
  the pre-rebase local `main` tip can be reconstructed if needed.
- **Change trigger:** This decision would become wrong if the local handoff commits
  were not path-disjoint from `origin/main`, or if any external system depended on
  those local handoff SHAs remaining stable.

### Decision 2: Take T-04 next, not T-02 or T-03

**Decision:** Work T-04 first once the canonical repo was repaired.

- **Driver:** After the rebase and repo-state cleanup, the user asked for the next
  direction.
  I read the ticket files for T-02, T-03, and T-04 and recommended T-04 because
  it had the narrowest surface area and the clearest acceptance criteria.
  The user accepted that direction and proceeded to present the implementation
  state for T-04.
- **Rejected:** T-02 first.
  Rejected because it is the highest-priority deferred ticket but also the deepest
  runtime hardening ticket. It lives in `server/dialogue.py` and
  `tests/test_dialogue.py` and reopens the first-turn fast-path semantics.
  That was the wrong complexity jump immediately after a session already dominated
  by repo-state repair.
- **Rejected:** T-03 first.
  Rejected because it is still medium-effort and lives in the broader
  `server/containment.py` cleanup/observability path. T-04 offered the fastest
  way to get a scoped fix reviewed and published before taking on a broader
  containment cleanup refactor.
- **Implication:** T-04 is now isolated and reviewable, while T-02 and T-03
  remain untouched and can be approached from a clean repo state in the next
  session.
- **Trade-offs:** T-04 was not the highest-impact ticket. The cost of doing it
  first was deferring the higher-priority T-02 hardening work.
- **Confidence:** Medium-high (E1) — the recommendation rested on the ticket
  texts, the current repo-state context, and the goal of achieving a quick clean
  win after repair work.
- **Reversibility:** High — no irreversible architecture commitment was made by
  choosing T-04 first.
- **Change trigger:** If the user had explicitly prioritized highest-risk runtime
  hardening over workflow momentum, T-02 would have been the better next ticket.

### Decision 3: Treat the actual T-04 file as the source of truth, not the response contract

**Decision:** Scrutinize and verify the real `clean_stale_shakedown.py` artifact,
not the user-supplied completion note alone.

- **Driver:** The user invoked the scrutiny skill explicitly and the T-04 ticket
  had already been through one round of “looks done” but still failed on real
  review findings.
  That made the actual file the only defensible source of truth.
- **Rejected:** Trust the response contract’s “all checks green” claims and move
  straight to commit/publish.
  Rejected because the ticket’s cited failure case, uncaught import-time failure,
  had already survived one earlier completion claim.
- **Rejected:** Use package-wide Ruff as the decisive validation signal.
  Rejected once `uv run ruff check` surfaced unrelated pre-existing failures in
  other files not touched by T-04.
- **Implication:** The real T-04 acceptance bar is now known:
  import-time failure is routed through the wrapper’s canonical error boundary,
  env-path normalization matches sibling behavior,
  and the wrapper passes the targeted smoke checks.
- **Trade-offs:** This made the session slower and more adversarial than a normal
  one-file cleanup task.
  The cost was worth it because the earlier self-reported completion had in fact
  missed two defects.
- **Confidence:** High (E2) — based on reading the file and ticket directly plus
  running the targeted smoke checks and tests.
- **Reversibility:** High — verification-first workflow changes no product state
  by itself; it only decides whether to proceed.
- **Change trigger:** If the wrapper had already been covered by a committed
  CLI-level regression test suite, the hand-run subprocess checks could have been
  reduced.

### Decision 4: Rebuild PR #102 before starting any new ticket or ending casually

**Decision:** Treat the polluted PR #102 as the highest-priority problem once it
was discovered, and repair it before considering T-02, T-03, or session stop.

- **Driver:** The evidence was concrete:
  `git log origin/main..fix/clean-stale-shakedown-script-conventions` showed 15
  commits, and `git diff --name-only origin/main...branch` showed the seven
  archived handoff files plus the wrapper script.
  That was not an acceptable review surface for a one-file T-04 fix.
- **Rejected:** Start T-02 or T-03 immediately and leave PR #102 polluted.
  Rejected because publication correctness outranked new implementation work once
  the review branch itself was wrong.
- **Rejected:** End the session with the polluted PR still open.
  Rejected because it would preserve a broken branch state for future reviewers
  and for future Codex.
- **Implication:** The rebuilt PR branch is now a one-commit, one-file review
  surface with head SHA `8649ef04` and draft PR #102 points at the corrected
  branch state.
- **Trade-offs:** Fixing the PR shape delayed any progress on T-02 or T-03 and
  required a force-push workflow plus backup tags.
- **Confidence:** High (E2) — based on local branch/diff verification and the
  final GitHub PR metadata (`commits: 1`, `changed_files: 1`, `head_sha:
  8649ef044ca460fa5034e96ce176a2be1a972b42`).
- **Reversibility:** High — the user created backup tags
  `backup-pr102-polluted` and `backup-t04-b39d8d90`, so the pre-rebuild state is
  still reconstructable.
- **Change trigger:** This decision would only change if the branch-repair
  evidence turned out to be false, or if PR #102 were deliberately intended to
  carry the archived handoff commits (it was not).

### Decision 5: Stop after PR #102 was clean instead of starting T-02 or T-03

**Decision:** End at a clean milestone boundary once PR #102 was verified clean.

- **Driver:** Earlier in the session I had explicitly recommended “repair PR #102
  first, then stop” rather than pile on new ticket work.
  After the rebuild, the user proposed session-end options and I recommended save
  rather than more work.
- **Rejected:** Start T-02 immediately after PR cleanup.
  Rejected because T-02 is higher-risk runtime work and deserved a fresh branch
  and a new session with that scope as the primary focus.
- **Rejected:** Start T-03 immediately after PR cleanup.
  Rejected for the same reason, though T-03 remains the most natural next ticket
  if the next session wants to stay in the containment/cleanup area.
- **Implication:** The session ends with a clean published T-04 draft PR and no
  partial follow-up ticket state.
- **Trade-offs:** Momentum on the remaining tickets is paused.
  The benefit is that the next session starts from a clean publication boundary
  instead of mid-fix or mid-triage.
- **Confidence:** High (E1) — milestone judgment, reinforced by the user’s own
  session-end framing.
- **Reversibility:** High — future sessions can immediately open T-03 or T-02.
- **Change trigger:** If CI or review on PR #102 surfaced a new blocking issue
  immediately, continuing in the same session could have been justified.

## Changes

### `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py`

**Purpose:** T-04 wrapper cleanup and hardening for the pre-seed stale-state
cleanup script used by `shakedown-b1`.

**Current shape:** See lines 14-52 at
`packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py:14-52`.

**Approach actually present in the file:**

- package-root shim with guarded `sys.path.insert(0, str(_PACKAGE_ROOT))`
- `main() -> int` entry point
- explicit raw-string env check (`if not plugin_data`)
- normalized `data_dir = Path(plugin_data).expanduser().resolve()`
- explicit normalized directory check (`if not data_dir.is_dir()`)
- delayed `from server.containment import clean_stale_files, shakedown_dir`
  inside `main()`
- outer `try/except` in `__main__` converting unexpected failures into canonical
  stderr

**Key lines:**

- env raw-string check and canonical stderr:
  `clean_stale_shakedown.py:20-27`
- path normalization:
  `clean_stale_shakedown.py:29`
- normalized-directory validation:
  `clean_stale_shakedown.py:30-36`
- delayed import:
  `clean_stale_shakedown.py:38`
- cleanup call:
  `clean_stale_shakedown.py:40`
- outer exception boundary:
  `clean_stale_shakedown.py:44-52`

**Important attribution note:** By the time I verified and committed the final
state, the file already contained the post-scrutiny fixes in the working tree.
I did not apply the final code delta myself in this session.
My contribution at that stage was:

- detecting the earlier missing behaviors during scrutiny
- verifying that the real file now addressed both findings
- committing the result
- publishing and later repairing the PR branch

### Git history and branch-state changes

**Operational cleanup / repo-state repair:**

- removed worktree:
  `/Users/jp/Projects/active/claude-code-tool-dev-t8-impl`
- created safety tag:
  `backup-main-pre-b4-rebase`
- rebased local `main` onto `origin/main`
- verified post-rebase state:
  `git rev-list --left-right --count origin/main...main` -> `0	14`
- local `main` still remains ahead 14 because it still carries the handoff archive
  commits

**T-04 branch / PR publication:**

- created and committed T-04 as `b39d8d90`
- pushed `fix/clean-stale-shakedown-script-conventions`
- opened draft PR #102
- discovered pollution from 14 docs(handoff) commits inherited from local `main`
- user rebuilt the branch with safety tags and a reset/cherry-pick flow
- current clean branch tip is `8649ef04`
- PR #102 now points at `8649ef04` and shows `1` commit / `1` changed file

**Backup tags now present:**

- `backup-main-pre-b4-rebase`
- `backup-pr102-polluted`
- `backup-t04-b39d8d90`

### Validation changes relative to earlier T-04 claims

**Originally claimed but invalid as stated:**

- package-wide `uv run ruff check` as proof of T-04 cleanliness
- smoke checks that did not exercise the ticket’s cited import-failure class

**Corrected validation standard used in this session:**

- package tests:
  `uv run pytest` in `packages/plugins/codex-collaboration`
- file-scoped Ruff:
  `uv run ruff check scripts/clean_stale_shakedown.py`
- subprocess checks for:
  unset env,
  empty env,
  nonexistent path,
  valid temp dir,
  literal tilde path,
  and simulated `ModuleNotFoundError`

### PR #102 state after rebuild

As of the save point, PR #102 is:

- URL:
  `https://github.com/jpsweeney97/claude-code-tool-dev/pull/102`
- title:
  `[codex] Align clean_stale_shakedown script conventions`
- state:
  open
- draft:
  true
- mergeable:
  true
- base:
  `main` at `b964be630b663c5e7618153d07b03d68d813874f`
- head:
  `fix/clean-stale-shakedown-script-conventions` at
  `8649ef044ca460fa5034e96ce176a2be1a972b42`
- commits:
  `1`
- changed files:
  `1`
- additions/deletions:
  `36` / `7`

## Codebase Knowledge

### Files read directly this session and why they mattered

| File | Why it was read | What it established |
|------|-----------------|---------------------|
| `.claude/rules/workflow/git.md` | To validate branch-protection and worktree behavior before recommending repo recovery | `main` is protected for Edit/Write workflows; valid work happens on `feature/*`, `fix/*`, etc.; worktrees are supported but inherit the same branch rules |
| `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py` | To scrutinize the actual T-04 artifact and later to verify stale findings against real code | Final wrapper structure, canonical error messages, delayed import, normalized path handling |
| `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py` | To compare T-04 against sibling script conventions | Package-root sys.path shim at `:15-17`; `_plugin_data_from_env()` uses `Path(...).expanduser().resolve()` at `:36-40` |
| `packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py` | To compare env-path semantics and script structure | `_resolve_data_dir()` uses `Path(value).expanduser().resolve()` at `:234-241`; script uses `main(argv) -> int` |
| `packages/plugins/codex-collaboration/scripts/codex_runtime_bootstrap.py` | To understand why package-wide Ruff was noisy and unrelated to T-04 | Contains pre-existing E402 Ruff failures due post-shim imports without `# noqa: E402` |
| `docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md` | To evaluate next-ticket choice | T-02 is high-priority, medium effort, touches `server/dialogue.py` and `tests/test_dialogue.py`, and reopens fast-path ambiguity handling |
| `docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md` | To evaluate next-ticket choice | T-03 is medium-priority containment cleanup observability work touching `server/containment.py` |
| `docs/tickets/2026-04-10-T-20260410-04-align-cleanstaleshakedownpy-with-script-convention.md` | To verify actual T-04 acceptance against the code | Ticket evidence explicitly names import-time failure and canonical error-format drift |

### Script conventions mapped from the containment area

**Pattern 1: package-root import shim**

- `containment_lifecycle.py:15-17`
- `containment_smoke_setup.py:16-18`
- final `clean_stale_shakedown.py:15-17`

This repo’s containment-adjacent scripts do not import from a separately mounted
installed package.
They insert the plugin package root into `sys.path`, then import `server.*`.
That is the normative shim shape for this cluster of scripts.

**Pattern 2: env-path normalization uses `expanduser().resolve()`**

- `containment_lifecycle.py:36-40`
- `containment_smoke_setup.py:234-241`
- final `clean_stale_shakedown.py:29`

This matters because literal tilde-style values are treated as valid inputs.
A raw `Path(plugin_data).is_dir()` check is not equivalent.
The scrutiny finding on T-04 was correct until this normalization existed in the
actual file.

**Pattern 3: wrappers often use `main() -> int` or `main(argv) -> int`**

- `containment_smoke_setup.py:57`
- final `clean_stale_shakedown.py:19`

This is more important than the earlier ticket prose suggesting `main() -> None`.
The script neighborhood’s actual pattern is return-code style main functions.

**Pattern 4: import-time failures remain a repo-wide sharp edge**

- `containment_lifecycle.py:19-33`
- `codex_runtime_bootstrap.py:26-31`
- final `clean_stale_shakedown.py:38`

T-04’s final state improves this one wrapper by moving the containment import
inside `main()`.
Sibling scripts still keep their imports at module scope.
That is now a concrete codebase asymmetry future Codex should remember.

### Branch / PR hygiene patterns learned the hard way

**Pattern 5: “ahead-only local main” is still dangerous for new branches**

- local `main` after rebase:
  `git branch -vv --list main` -> `[origin/main: ahead 14]`
- polluted branch before rebuild:
  `git log --oneline origin/main..fix/clean-stale-shakedown-script-conventions`
  showed the T-04 commit on top of the 14 docs(handoff) commits

The important lesson is not just “branch from origin/main”.
It is:

- local `main` can be perfectly fine for local reading and still be a bad branch
  base for publication
- rebase removed the “behind” side of divergence but not the “ahead” side
- future branches cut from local `main` will inherit those ahead-only commits
  unless local `main` is reset or branches are cut explicitly from `origin/main`

**Pattern 6: PR diff views can lag after force-push**

The rebuild of PR #102 revealed a real GitHub-side caching delay.
The first `gh pr diff --name-only 102` after the force-push returned stale data.
The rerun returned the correct one-file diff.

So the reliable post-force-push verification stack is:

- local `git log origin/main..HEAD`
- local `git diff --name-only origin/main...HEAD`
- GitHub PR metadata (`commits`, `changed_files`, `head_sha`)
- optionally raw `/pulls/<n>/files`
- treat a single stale `gh pr diff` result as suspicious, not authoritative

### Ticket map for next session

| Ticket | Scope | Files | Why it matters |
|--------|-------|-------|----------------|
| T-02 | dialogue fast-path hardening | `server/dialogue.py`, `tests/test_dialogue.py` | protects against corruption/ambiguity around the first-turn fast path |
| T-03 | stale cleanup observability | `server/containment.py` | turns silent cleanup failures into surfaced operator-visible results |
| T-04 | wrapper convention alignment | `scripts/clean_stale_shakedown.py` | now isolated, fixed, and in draft PR #102 |

### Key locations future Codex should know

- branch-protection policy:
  `.claude/rules/workflow/git.md`
- current T-04 wrapper:
  `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py:14-52`
- sibling env normalization reference:
  `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py:36-40`
- sibling env normalization reference:
  `packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py:234-241`
- clean draft PR:
  `https://github.com/jpsweeney97/claude-code-tool-dev/pull/102`
- backup tags:
  `backup-main-pre-b4-rebase`,
  `backup-pr102-polluted`,
  `backup-t04-b39d8d90`

## Context

**Framing:** This session was not primarily a coding session.
It was a state-restoration and publication-hygiene session with one small wrapper
fix nested inside it.

The core technical work was straightforward.
The real difficulty was distinguishing four different kinds of “wrong”:

- work removed from the checkout but still safe in Git
- local repo state that was readable but not a safe branch base
- a ticket write-up that sounded complete but still failed real scrutiny
- a PR that looked published but carried hidden docs(handoff) cargo

**Core insight:** In this repo, correctness after B4 was not just about file
contents.
It was about reachable SHAs, canonical path state, branch base provenance, and
review-surface cleanliness.

The most important mental model for future Codex is:

> treat the repo as having two independent truths:
> 1. what Git objects safely contain
> 2. what the current checkout and current branch actually expose to the next
>    session and to reviewers

The worktree-removal scare only made sense once that model was applied.
The code was still safe in Git, but the canonical checkout no longer exposed it.

The polluted PR only made sense once that same model was applied to publication.
The branch tip contained the right T-04 commit, but the branch ancestry exposed
too much to reviewers because it was cut from ahead-only local `main`.

**Bigger picture:** This session’s cleanup and publication work protects the next
hardening sessions from inheriting state confusion.

- If the canonical repo had remained stale, T-02 or T-03 would begin from the
  wrong checkout.
- If PR #102 had remained polluted, review would focus on the wrong files and the
  actual T-04 fix would be harder to reason about.
- If the stale review finding had been accepted at face value, Codex would have
  tried to “fix” a file that was already correct.

**Context future Codex will not get from the code alone:**

- the user is willing to challenge recommendation quality aggressively when the
  recommendation claims more verification than it actually contains
- local `main` intentionally carries handoff archive commits and therefore is not
  the same thing as “branch I should always base work from”
- the untracked handoff archive file
  `docs/handoffs/archive/2026-04-09_01-37_t4-publication-and-security-review.md`
  has survived across multiple sessions and is unrelated to T-04

**Why now:** The loaded B4-complete handoff explicitly said the remaining work was
cleanup and future-ticket selection, not more B4 design.
The user immediately confirmed that by saying:
“Continue with operational cleanup”.

## Learnings

### 1. Worktree removal can make merged code disappear from disk without losing it

- **Mechanism:** Removing a worktree deletes the working directory, not the Git
  objects reachable from refs.
- **Evidence:** After the worktree was removed, the user noticed files like
  `dialogue-codex/SKILL.md` were missing from
  `/Users/jp/Projects/active/claude-code-tool-dev`, but
  `git ls-tree origin/main ...` and `git show origin/main:...` still succeeded.
- **Implication:** When a user asks “did we lose work?”, the first check is ref
  reachability, not filesystem presence.
- **Watch for:** Future cleanup sessions that remove worktrees before aligning the
  canonical checkout.

### 2. Recommendation quality must be earned with the checks it claims

- **Mechanism:** The user’s critique of the first recovery recommendation was
  correct because it attacked missing verification rather than just preference.
- **Evidence:** User wording:
  “The analysis is solving a misframed problem.”
  and
  “This is ‘verifiability theater’ — using the language of verification to add
  confidence without the work of verification.”
- **Implication:** In this repo, recommendations about Git state need concrete
  disjointness, reachability, and policy checks before ranking options.
- **Watch for:** Any future “best option” answer that relies on branch semantics,
  path state, or PR shape.

### 3. File-scoped lint can be the only valid signal in a noisy package

- **Mechanism:** `uv run ruff check` at package scope reported unrelated,
  pre-existing failures in files outside T-04.
- **Evidence:** Ruff failures came from
  `scripts/codex_runtime_bootstrap.py`,
  `tests/conftest.py`,
  `tests/test_credential_scan.py`,
  and `tests/test_dialogue_profiles.py`,
  not from `scripts/clean_stale_shakedown.py`.
- **Implication:** For surgical tickets in a package with existing lint debt, the
  correct validation move is file-scoped lint plus broader tests, not broad lint
  treated as a pass/fail gate.
- **Watch for:** Overclaiming “ruff passes” when only the touched file passes.

### 4. Import-failure testing has to isolate the import mutation from happy-path tests

- **Mechanism:** I ran a temp-dir happy-path script invocation in parallel with the
  import-failure simulation that temporarily moved `server/containment.py`.
- **Evidence:** The happy-path run failed with the same
  `ModuleNotFoundError("No module named 'server.containment'")` as the simulated
  import-failure path.
- **Implication:** That result was invalid evidence, not a product failure.
  The proper fix was to confirm the restore trap ran, then rerun the happy-path
  check in isolation.
- **Watch for:** Any future “parallel smoke tests” that mutate shared files.

### 5. Rebased local `main` can still be a dangerous branch base

- **Mechanism:** Rebase fixed local `main`’s “behind” side but preserved its 14
  ahead-only docs(handoff) commits.
- **Evidence:** `git branch -vv --list main` now shows
  `[origin/main: ahead 14]`.
  PR #102 pollution proved that those ahead-only commits still ride along when
  branching from local `main`.
- **Implication:** Future feature branches should be cut explicitly from
  `origin/main` or local `main` should be reset to `origin/main`.
- **Watch for:** Repeating exactly this PR-pollution bug on T-02 or T-03.

### 6. GitHub PR diff views can briefly lag behind force-pushed reality

- **Mechanism:** `gh pr diff --name-only 102` returned stale data immediately after
  the force-push, then returned the correct one-file result on rerun.
- **Evidence:** The user explicitly reported the first result as stale cache, and
  that claim matched the cleaner GitHub PR metadata (`commits: 1`,
  `changed_files: 1`) and the local branch diff.
- **Implication:** After a force-push, treat single-source PR diff output as
  provisional until it agrees with branch head SHA and file list checks.
- **Watch for:** Mistaking cached GitHub CLI output for real PR scope.

### 7. T-04 is now stronger than its sibling scripts in one narrow respect

- **Mechanism:** The final wrapper moves the containment import into `main()`.
- **Evidence:** `clean_stale_shakedown.py:38` imports inside the guarded runtime
  path, while sibling scripts still import `server.containment` at module scope.
- **Implication:** The T-04 wrapper no longer fails the exact import-time boundary
  case that created the ticket, but the same vulnerability class still exists in
  `containment_lifecycle.py` and `containment_smoke_setup.py`.
- **Watch for:** Assuming T-04 generalized to the rest of the script cluster.

## Next Steps

### 1. Drive PR #102 to closure

- **Why next:** T-04 is now isolated, published, and draft-open. The smallest
  real unit of unfinished work is PR review/merge, not more local implementation.
- **What to read first:** PR #102 on GitHub, plus
  `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py:14-52`.
- **Approach suggestion:** Keep the current branch and PR state. Monitor CI on
  `8649ef04`, answer any real review findings, and only reply to the stale
  env-normalization finding if it actually appears in a review thread.
- **Acceptance criteria:** PR remains one commit / one file, CI is green or
  reviewed, and the PR is either merged or ready for merge.
- **Potential obstacle:** Cached PR diff views may lag immediately after force-push.
  Use head SHA + changed_files if the diff looks suspicious again.

### 2. Decide how to handle local `main` drift before cutting another feature branch

- **Why next:** local `main` still being `ahead 14` is a known recurrence risk.
- **What to read first:** `git branch -vv --list main`,
  `git log --oneline origin/main..main`,
  and the backup tag list.
- **Approach suggestion:** Either:
  1. keep local `main` as-is but branch explicitly from `origin/main`, or
  2. reset local `main` to `origin/main` once the handoff archive strategy is
     no longer needed there.
- **Acceptance criteria:** Future branches for T-02 or T-03 no longer inherit the
  docs(handoff) archive commits.
- **Potential obstacle:** If anyone still wants those handoff commits reachable
  from local `main`, a reset will surprise them unless it is deliberate.

### 3. If opening the next ticket, prefer T-03 before T-02

- **Why next:** T-03 stays in the same containment/cleanup area as T-04 but
  broadens from wrapper hygiene to real cleanup observability.
- **What to read first:** `docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md`,
  `packages/plugins/codex-collaboration/server/containment.py`,
  and `tests/test_containment.py`.
- **Approach suggestion:** Add explicit cleanup-result reporting, surface
  `OSError`/`PermissionError` information, and add a table-driven pattern-coverage
  test tied to the documented cleanup surface.
- **Acceptance criteria:** T-03 ticket criteria, plus tests that prove mixed
  success/failure cleanup batches are visible to callers.
- **Potential obstacle:** Callers currently ignore cleanup return values, so the
  shape of a new return object or logging behavior needs to be chosen carefully.

### 4. Keep T-02 as the highest-risk deferred ticket

- **Why next:** T-02 is still the highest-priority runtime hardening item even if
  it is not the most natural immediate next step after T-04.
- **What to read first:** `docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md`,
  `packages/plugins/codex-collaboration/server/dialogue.py`,
  and `packages/plugins/codex-collaboration/tests/test_dialogue.py`.
- **Approach suggestion:** Decide between additive health-check hardening and a
  more structural last-turn-sequence representation before editing.
- **Acceptance criteria:** All five ticket acceptance items land together.
- **Potential obstacle:** This ticket reopens the first-turn fast-path semantics,
  so it is better suited to a fresh session where that is the primary focus.

### 5. Clean up backup tags and the stray untracked archive file later, not now

- **Why next:** These are now true housekeeping items, not blockers.
- **What to read first:** `git tag --list 'backup-*' | sort` and
  `git status --short --branch`.
- **Approach suggestion:** Keep tags until PR #102 is merged and confidence is
  high that no reconstruction is needed.
  Handle the untracked archive file in a separate cleanup decision rather than
  mixing it into ticket work.
- **Acceptance criteria:** No lingering ambiguity about why each backup tag exists,
  and the untracked archive file is either intentionally preserved or deliberately
  removed/committed on its own merits.
- **Potential obstacle:** Cleaning these up too early removes easy rollback anchors
  for branch-state reconstruction.

## In Progress

Clean stopping point.

- **Approach:** The session reached a deliberate publication boundary, not a
  partial implementation boundary.
- **State:** PR #102 is clean, draft-open, and mergeable.
- **Working:** Current branch
  `fix/clean-stale-shakedown-script-conventions` points at `8649ef04`,
  tracks `origin/fix/clean-stale-shakedown-script-conventions`,
  and is one commit above `origin/main`.
- **Not working:** No T-02 or T-03 work has started.
- **Open question:** Whether to reset local `main` to `origin/main` before the next
  feature branch, or keep explicit `origin/main` branching discipline.
- **Next action:** Save handoff and end the session.

## Open Questions

### 1. Should local `main` be reset to `origin/main` before starting T-02 or T-03?

- Current status:
  `git branch -vv --list main` shows
  `main e1b7ef69 [origin/main: ahead 14]`.
- This is not a correctness bug for local reading, but it is a branch-base bug for
  publication unless future branches are cut from `origin/main` explicitly.
- No decision was made this session.

### 2. Should PR #102 remain draft until CI and any review findings land?

- Current PR state from GitHub:
  `draft: true`, `mergeable: true`, `commits: 1`, `changed_files: 1`.
- No explicit “ready for review” transition was performed this session.

### 3. Should the sibling containment scripts receive the same delayed-import fix?

- T-04 fixed the wrapper that was in scope.
- `containment_lifecycle.py` and `containment_smoke_setup.py` still import
  `server.containment` at module scope.
- This is adjacent work, not part of T-04 as filed.

### 4. Should the stale review-finding dismissal be posted proactively or only if the
finding appears in a real review thread?

- My recommendation in this session was to keep the dismissal text ready but only
  post it where a real review surface needs it.
- No actual stale-thread response was posted by me in this session.

### 5. What should happen to the untracked file
`docs/handoffs/archive/2026-04-09_01-37_t4-publication-and-security-review.md`?

- It survived multiple sessions.
- It was intentionally ignored during T-04 and publication work.
- It still appears in `git status`.

## Risks

### 1. Future branches can still repeat PR #102’s pollution bug

- **Mechanism:** local `main` remains ahead 14 with docs(handoff) archive commits.
- **Evidence:** `git branch -vv --list main` -> `[origin/main: ahead 14]`.
- **Impact:** Any future branch cut from local `main` instead of `origin/main`
  can silently include the handoff archive commits in its review surface.
- **Mitigation:** Reset local `main` later, or branch explicitly from
  `origin/main`.

### 2. Backup tags can become forgotten, stale clutter

- **Mechanism:** Three backup tags now exist.
- **Evidence:** `git tag --list 'backup-*' | sort` shows
  `backup-main-pre-b4-rebase`,
  `backup-pr102-polluted`,
  `backup-t04-b39d8d90`.
- **Impact:** They are useful now, but if forgotten they become cleanup debt and
  ambiguity about which state each one preserves.
- **Mitigation:** Delete them once PR #102 is merged and no reconstruction path is
  needed.

### 3. Cached PR diff output can mislead future verification

- **Mechanism:** GitHub diff views lagged after the force-push to PR #102.
- **Evidence:** User explicitly reported that the first `gh pr diff --name-only`
  result was stale and the rerun was correct, while GitHub PR metadata already
  reflected the rebuilt branch state.
- **Impact:** A future session could misdiagnose a clean PR as still polluted.
- **Mitigation:** Cross-check with local branch diff and PR metadata.

### 4. Sibling containment scripts still have module-scope import-time vulnerability

- **Mechanism:** T-04 fixed the wrapper in scope, not the whole script family.
- **Evidence:** `containment_lifecycle.py:19-33` and
  `codex_runtime_bootstrap.py:26-31` still import at module scope after the shim.
- **Impact:** Similar import-time failure behavior can still occur in related
  wrappers.
- **Mitigation:** File a future ticket or fold into T-03 if that scope expands
  naturally.

### 5. Package-wide lint remains noisy and can confuse verification claims

- **Mechanism:** Ruff at package scope currently fails for unrelated pre-existing
  files.
- **Evidence:** The package-wide `uv run ruff check` output this session included
  failures outside the T-04 file.
- **Impact:** Future response contracts can accidentally overclaim “ruff passes”
  unless the scope is stated precisely.
- **Mitigation:** Specify file-scoped Ruff when validating narrow tickets.

## References

### Git and branch-state commands used

- `git worktree list --porcelain`
- `git -C /Users/jp/Projects/active/claude-code-tool-dev-t8-impl status --short --branch`
- `git -C /Users/jp/Projects/active/claude-code-tool-dev status --short --branch`
- `git merge-base --is-ancestor ad27127add749ef1a7d6b5a8a30ae407472784d6 origin/main`
- `git diff --name-only origin/main...main -- ':!docs/handoffs/' ':!docs/handoffs/archive/'`
- `git merge-base --is-ancestor 7f4eed41 main`
- `git rev-list --left-right --count origin/main...main`
- `git log --oneline origin/main..HEAD`
- `git diff --name-only origin/main...HEAD`
- `git branch -vv --list main fix/clean-stale-shakedown-script-conventions`
- `git tag --list 'backup-*' | sort`

### Files read directly

- `/Users/jp/Projects/active/claude-code-tool-dev/.claude/rules/workflow/git.md`
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py`
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/containment_lifecycle.py`
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py`
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/codex_runtime_bootstrap.py`
- `/Users/jp/Projects/active/claude-code-tool-dev/docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md`
- `/Users/jp/Projects/active/claude-code-tool-dev/docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md`
- `/Users/jp/Projects/active/claude-code-tool-dev/docs/tickets/2026-04-10-T-20260410-04-align-cleanstaleshakedownpy-with-script-convention.md`

### GitHub / remote references

- PR #102:
  `https://github.com/jpsweeney97/claude-code-tool-dev/pull/102`
- current PR #102 head SHA:
  `8649ef044ca460fa5034e96ce176a2be1a972b42`
- current PR #102 base SHA:
  `b964be630b663c5e7618153d07b03d68d813874f`

### Local-state references

- resumed-from archive handoff:
  `/Users/jp/.codex/handoffs/claude-code-tool-dev/.archive/2026-04-10_01-02_b4-complete-pr-101-merged-follow-up-tickets-filed.md`
- state-file path that should be cleaned after this save:
  `/Users/jp/.codex/.session-state/handoff-claude-code-tool-dev`
- current branch:
  `fix/clean-stale-shakedown-script-conventions`
- current clean branch tip:
  `8649ef04`
- current local `main` tip:
  `e1b7ef69`
- original T-04 commit before rebuild:
  `b39d8d90`

## Gotchas

### 1. Removing a worktree can look like data loss even when Git state is safe

Once the B4 worktree was removed, the canonical repo no longer had the merged B4
files on disk.
That looked like work loss to the user, but it was actually a checkout-state
problem, not a Git-object problem.
Always distinguish “not present in this checkout” from “not reachable from a ref”.

### 2. Fresh-worktree recommendations can be wrong even when they sound conservative

My first recommendation after the worktree removal was to create a fresh
`origin/main` worktree.
The user’s scrutiny showed why that was wrong:

- it did not solve the canonical-path problem
- `main` would still be protected there
- it deferred rather than fixed the real repo-state mismatch

Future Codex should remember this specific failure mode in reasoning, not just in
Git commands.

### 3. Package-wide Ruff was a trap here

Package-wide `uv run ruff check` was not a valid acceptance signal for T-04
because the package already had unrelated lint failures elsewhere.
The correct statement is:

- package-wide Ruff fails for unrelated pre-existing reasons
- file-scoped Ruff for `clean_stale_shakedown.py` passes

### 4. Parallel smoke tests that mutate shared files can invalidate each other

The first happy-path temp-dir smoke check failed only because it ran concurrently
with the temporary rename of `server/containment.py` for the import-failure test.
This is a methodology gotcha, not a product gotcha.

### 5. zsh reserves `status` as a read-only variable

One early happy-path shell snippet used:

- `status=$?`

in zsh.

That failed with:

- `zsh:1: read-only variable: status`

Use a different variable name such as `rc`.

### 6. PR diff caching after force-push is real

The first `gh pr diff --name-only 102` after the PR rebuild returned stale data.
The rerun was correct.
Do not trust a single immediate diff read after force-pushing a branch.

### 7. Local `main` being “ahead only” still matters operationally

The rebase fixed local `main` enough for reading and for regaining B4 files on
disk.
It did not make local `main` a safe default branch base.
That subtle distinction is exactly what polluted PR #102 the first time.

## Conversation Highlights

### The worktree-removal scare mattered

The user’s most important correctness check early in the session was:

> “Wait. We just removed the worktree, but some of the files like the dialogue
> skill were on that worktree and they aren't at
> `/Users/jp/Projects/active/claude-code-tool-dev`. Did we just lose work?”

That question prevented a lazy “cleanup complete” conclusion.
It forced the distinction between Git reachability and checkout state.

### The user’s scrutiny materially improved the Git recommendation

The user did not just disagree with the fresh-worktree recommendation.
They demonstrated why it was wrong:

> “The analysis is solving a misframed problem.”

and later:

> “This is ‘verifiability theater’ — using the language of verification to add
> confidence without the work of verification.”

Those comments were correct and changed the actual path taken.

### The user preferred defended execution, not generic confidence

When the rebase plan was revised, the user’s review focus was execution rigor:

- mandatory safety tag
- explicit `git pull --rebase origin main`
- explicit post-rebase verification
- explicit checkpoint if anything unexpected appeared during rebase

That was not stylistic nitpicking.
It was the user telling Codex what level of rigor they expect before a
“verifiably best” recommendation is allowed to stand.

### The user kept the session scoped

Once PR #102 was known to be polluted, the user accepted the advice to fix
publication scope before resuming ticket work.
Later, after the rebuild, the user proposed save/end options rather than trying to
piggyback T-02 or T-03 onto the end of the session.

That reinforced the session’s pattern:
finish one milestone boundary completely before moving on.

## User Preferences

### Evidence before confidence

- User scrutiny quote:
  “This is ‘verifiability theater’ — using the language of verification to add
  confidence without the work of verification.”

Interpretation:
They do not want polished recommendation language unless the underlying checks have
actually been run.

### Correct framing matters as much as correct commands

- User scrutiny quote:
  “The analysis is solving a misframed problem.”

Interpretation:
They care about whether Codex is solving the right decision, not just whether the
suggested commands are plausible.

### Prefer fixing the review surface before starting new work

- User-approved guidance in this session:
  repair PR #102 first, then stop, and only then consider T-02 or T-03 later

Interpretation:
They prefer a clean review/publication boundary over squeezing more implementation
into the same session.

### Strong preference for exact, checkable verification language

The user repeatedly reformulated recommendations into explicit command sequences
and explicit expected outputs.
That includes:

- mandatory tag before rebase
- explicit `git pull --rebase origin main`
- concrete post-rebase checks and expected values
- multiple independent PR-cleanliness checks after force-push

Interpretation:
Future Codex should continue to present operational recommendations as executable
and falsifiable verification sequences, not as informal prose.

### User is comfortable correcting Codex sharply when the evidence is good

This is not a personality note.
It is a workflow note.
When the user has stronger evidence, they will use it and expect the model to
update quickly.
Future Codex should treat that as collaboration, not friction.

## Rejected Approaches

### 1. Fresh `origin/main` worktree as the repo-recovery fix

- **Tried:** Recommended creating a fresh worktree from `origin/main`.
- **Failed because:** It solved the wrong problem.
  It would leave the canonical repo stale, still require a feature branch before
  edits because `main` is protected, and create path split-brain for future
  handoffs and repo-local config.
- **Learned:** The real goal was canonical-path correctness, not merely “somewhere
  on disk” correctness.

### 2. Treat package-wide Ruff as proof that T-04 is clean

- **Tried:** Used `uv run ruff check` at package scope while validating T-04.
- **Failed because:** The package already has unrelated Ruff failures outside the
  touched file.
- **Learned:** For narrow tickets in a noisy package, file-scoped lint is the
  correct signal.

### 3. Accept PR #102 publication at first push without diff-shape review

- **Tried:** Publish branch and open PR #102 after T-04 commit.
- **Failed because:** The branch ancestry still contained 14 docs(handoff)
  commits from local `main`, so the PR diff was polluted.
- **Learned:** Local branch cleanliness is not enough; base ancestry must also be
  reviewed when local `main` is ahead-only of `origin/main`.
