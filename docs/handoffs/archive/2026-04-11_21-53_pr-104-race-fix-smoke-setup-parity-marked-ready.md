---
date: 2026-04-11
time: "21:53"
created_at: "2026-04-12T01:53:20Z"
session_id: 1c79c649-1539-4c6d-a20b-ac397b9de6c8
project: claude-code-tool-dev
branch: fix/t03-stale-cleanup-observability
commit: 62765e81
title: PR #104 — Race fix from inspection feedback + smoke-setup parity, pushed and marked ready
type: handoff
resumed_from: docs/handoffs/archive/2026-04-11_21-24_pr-104-review-option-b-commits-pending-push.md
files:
  - packages/plugins/codex-collaboration/server/containment.py
  - packages/plugins/codex-collaboration/tests/test_containment.py
  - packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py
  - packages/plugins/codex-collaboration/tests/test_containment_smoke_setup.py
  - docs/handoffs/archive/2026-04-11_21-24_pr-104-review-option-b-commits-pending-push.md
---

# PR #104 — Race Fix from Inspection Feedback + Smoke-Setup Parity, Pushed and Marked Ready

## Goal

Inspect the 2 commits from the previous session per the user's approval gate, integrate the user's already-applied race-condition fix into the local commit chain, complete the smoke-setup parity gap deferred from last session, then execute the publish flow (`git push` + `gh pr ready 104`). The session's "done" bar was **PR #104 transitioned from draft → ready for review with all 4 commits visible on GitHub, headRefOid converged to local HEAD, all tests still passing locally**.

**Trigger:** The prior session (2026-04-11 21:24) closed with an explicit approval gate, verbatim user message: *"Save a handoff. I will inspect this work and share my feedback with you in the next session."* This session opened with that feedback in hand — a P3 finding about FileNotFoundError races, with the fix already applied to the working tree before they loaded the session. The user's pattern was clear: review first, fix in place, then ask Claude to verify and commit.

**Stakes:** PR #104 was the culmination of the T-03 observability hardening work — 8 implementation commits + 2 polish commits already on the branch (10 + 2 prior plan-revision commits = 12 commits since main as of session start). The branch was in pre-review limbo: code was good locally but invisible to reviewers because nothing had been pushed. This session needed to (a) close the inspection loop without missing the user's feedback, (b) complete the smoke-setup parity gap so the PR doesn't ship with an internal inconsistency that a reviewer would catch, and (c) execute the shared-state transitions (push, mark ready) only with explicit approval per global CLAUDE.md "actions visible to others" policy.

**Success criteria (all met):**
- User's race-fix diff reviewed line-by-line and verified empirically (ruff + 546 tests)
- Race fix committed as a discrete `fix(containment)` commit (not amended into prior work)
- smoke_setup:525 consistency gap closed with matching format-template parity to the lifecycle pattern from `82d8cada`
- Format change validated as non-breaking — substring assertions tolerate it without test edits
- 4 local commits pushed to origin in one fast-forward push (no force-push, no rewrites)
- PR #104 transitioned draft → ready via `gh pr ready 104`
- GitHub state read back via `gh pr view` to verify (caught + resolved a real API consistency lag)
- All actions taken only after explicit user authorization at each shared-state boundary

**Connection to project arc:** T-03 (ticket `T-20260410-03`) is now in mark-ready state. Downstream: CI run (if configured for ready PRs), human review, possible feedback iterations, merge, then ticket status `deferred → done`. No further T-03 implementation work pending until reviewer feedback arrives. The cross-model plugin's containment hardening initiative is essentially complete pending merge.

## Session Narrative

Session opened by loading the prior handoff at `docs/handoffs/2026-04-11_21-24_pr-104-review-option-b-commits-pending-push.md` via `/handoff:load`. The load surfaced a comprehensive ~970-line handoff describing 9 decisions, the 5-reviewer parallel agent dispatch from the prior session, and the explicit approval gate the user had installed at the end of the prior session. I displayed the resumption marker ("Resuming from **handoff**"), summarized the 4 outstanding next-action options, and offered to either show the 2 prior commits, fix the smoke_setup gap, push, or take a different direction.

Before my offer landed, the user provided their feedback inline as the first user message of this session. They opened with a meta-statement (*"Here is my feedback for the 2 commits from last session:"*) followed by a P3 finding:

> "The patch largely does what it intends, but the new per-file error reporting misclassifies benign concurrent deletions as cleanup failures. That can produce misleading stderr from all three callers during overlapping sweeps."

They then quoted the specific finding with file:line refs (`containment.py:468-471`) and an explanation of the TOCTOU window — *"Once `os.listdir()` has built candidates, another cleanup invocation can legitimately remove one of those files before this code reaches `stat()` or the `unlink()` a few lines below."* — and a recommendation: *"Treating `FileNotFoundError` as a benign lost race here would avoid false-positive cleanup failures under overlapping sweeps."*

Crucially, they then described what they had **already done**: updated containment.py:358 area, added 2 regression tests at test_containment.py:302 and :320, and gave a "Why It Changed" rationale. The diff was sitting in the working tree at session start (visible in the SessionStart git status). This was the key reframe of the session: **I needed to verify their work, not propose a fix**.

**Phase 1 — Verifying the user's race fix (~5 min):**

I checked `git status` to confirm exactly 2 modified files in the codex-collaboration package, then ran `git diff` on each. The production change in containment.py was minimal — +7/-1 lines:

```python
# At path.stat() site:
        try:
            stat_result = path.stat()
        except FileNotFoundError:        # NEW
            continue                      # NEW
        except OSError as exc:
            failed_stat.append(...)
            continue

# At path.unlink() site (parallel structure):
        try:
            path.unlink()
        except FileNotFoundError:        # NEW
            continue                      # NEW
        except OSError as exc:
            failed_unlink.append(...)
            continue
```

Plus a 2-line docstring update at line 363 stating: *"Concurrent-deletion races after `os.listdir()` are ignored because the stale file is already gone."*

The exception-ordering placement is **load-bearing**: `FileNotFoundError` is a subclass of `OSError`. Python's `try/except` matches top-down, so if you wrote `except OSError` first, it would catch `FileNotFoundError` and record it in the failure bucket — exactly the bug being fixed. The specific subclass MUST come first.

The 2 new tests (lines 302, 320 of test_containment.py) covered both race windows:

- **Test 1** (`test_clean_stale_files_ignores_candidates_removed_before_stat`): monkeypatches `os.listdir` to return a never-created filename `seed-run-1.json`. The production `path.stat()` then hits the actual filesystem and gets a real `FileNotFoundError` from the kernel — no fake exception needed; the OS provides ground truth. Asserts all 4 result buckets empty (`removed`, `skipped_fresh`, `failed_stat`, `failed_unlink`) AND `had_errors=False`.

- **Test 2** (`test_clean_stale_files_ignores_candidates_removed_before_unlink`): more creative simulation. Creates a real stale file (26 hours old via `os.utime`), then monkeypatches `Path.stat` with a wrapper that:
  1. Calls the original `stat()` to get the result
  2. Calls `original_unlink(self)` to actually remove the file
  3. Returns the stat result

  When the production code subsequently calls `path.unlink()`, the file is already gone → `FileNotFoundError`. Faithfully simulates the TOCTOU window between stat() succeeding and unlink() executing. Includes an explicit `assert not stale.exists(), "simulated concurrent deletion should remove the file"` guard so the test fails loudly if the mock ever stops firing (rather than passing trivially because the simulation didn't run).

I ran ruff + the full pytest suite in parallel via two simultaneous bash calls: ruff clean on both files; **546 tests passed in 3.78s** (was 544 baseline → +2 new tests, zero regressions). The fix was tight, correct, and well-tested. I told the user "Nothing I'd change" and presented 4 commit-strategy options.

**Phase 2 — Committing the race fix (~3 min):**

The user picked **Option (a) — new 3rd local commit** (matched my recommendation). Rationale: a `fix(containment)` commit with both file changes bundled, distinct from the prior `fix(containment-lifecycle)` commit `82d8cada` because the file surface (`server/containment.py` vs `scripts/containment_lifecycle.py`) and concern (race fix vs format polish) are different. Separating them keeps `git bisect` useful if any future regression localizes to one or the other.

I drafted a ~30-line commit body explaining:
- The TOCTOU window (concurrent invocations from lifecycle/smoke_setup/clean_stale_shakedown)
- Why all 3 callers were affected via `had_errors`
- The load-bearing exception ordering
- Both regression tests' simulation strategies
- Verification results (ruff + 546 tests)

Committed as `31ac66e8`. Branch state: 3 commits ahead of origin.

**Phase 3 — Smoke-setup parity (~10 min):**

The user said: *"We should fix containment_smoke_setup.py"* — closing the I-2' gap I had explicitly flagged in the prior session. The defect: `containment_smoke_setup.py:525` had the **identical** `{exc}` vs `{exc!r:.100}` pattern as the lifecycle defect from `82d8cada`, but the silent-failure-hunter reviewer in the prior session had only flagged the lifecycle site (and incorrectly claimed "every other error site uses `{exc!r:.100}`"). The prior session had deferred the fix per scope control; the user's "we should fix" message was the explicit approval to close it now.

Before editing, I read the actual code at `containment_smoke_setup.py:490-540` to confirm the current state and structure. The defect is inside `_run_with_wrapper()` (the Round 6 testability extraction), which has its own docstring at lines 511-521 that quoted the old format as a "behavior-preserving" claim from Round 6. Then I read `test_containment_smoke_setup.py:200-300` to find the test docstrings and assertions.

Then I grep'd the entire codex-collaboration package for `containment_smoke_setup failed` to map every single touchpoint:

| Line | Type | Action needed |
|---|---|---|
| `scripts/containment_smoke_setup.py:516` | Production docstring (factual format claim) | Update format reference + drop "Behavior-preserving" framing |
| `scripts/containment_smoke_setup.py:525` | Production code (the I-2' defect) | Fix `{exc}` → `unexpected error. Got: {exc!r:.100}` |
| `tests/test_containment_smoke_setup.py:214` | Test docstring (factual format claim) | Update format reference |
| `tests/test_containment_smoke_setup.py:221` | Test docstring (prefix-only reference) | No change — describes prefix only |
| `tests/test_containment_smoke_setup.py:283` | Test assertion (substring `"containment_smoke_setup failed"`) | No change — substring still matches |
| `tests/test_containment_smoke_setup.py:317` | Test docstring (prefix-only reference) | No change |
| `tests/test_containment_smoke_setup.py:397` | Test assertion (substring) | No change |

The mapping was a small but important step — it prevented both incomplete fixes (missing a docstring update) AND unnecessary churn (editing test files that didn't actually need it). I traced the substring assertions through `repr(OSError(...))` truncation: the substring `"cannot enumerate shakedown root"` lands at character positions ~36–66 of the OSError repr, well within the `:.100` cap, so the existing assertions (`tests/test_containment_smoke_setup.py:289, 403`) survive the format change without modification.

I made 3 sequential `Edit` calls in one batch:
1. Production code at line 525: changed inline `{exc}` print to a 4-line parenthesized form mirroring `containment_lifecycle.py:188` style
2. Production docstring at lines 511-521: dropped the "**Behavior-preserving**" framing (it was relative to Round 6's extraction baseline, no longer accurate after this format change), added current-state contract description with the new format and reasoning about lifecycle parity
3. Test docstring at line 214: minimal 2-line change to quote the new format

Then ran ruff + the full pytest suite in parallel again. Ruff clean on both modified files; **546 tests passed in 3.88s**. Critically, both format-dependent tests passed unchanged: `test_prepare_scenario_surfaces_cleanup_enumeration_failure` (the subprocess chmod test) and `test_prepare_scenario_main_wrapper_fail_fast_via_monkeypatched_listdir` (the in-process Round 6 test). This confirmed the substring-assertion design from the original tests had been the right call — it decoupled the format from the contract, making the format polish trivial.

Committed as `62765e81` with a thorough body explaining the parity rationale, the I-2' history, and which test assertions were robust to the change. Branch state: 4 commits ahead of origin.

**Phase 4 — Push + mark ready as a chained shared-state action (~3 min):**

The user said *"Push + mark ready"*. This was the explicit authorization for two distinct shared-state actions: the push (visible to anyone with repo access) and the draft → ready transition (notifies any configured reviewers, may trigger CI). Per global CLAUDE.md, both required prior authorization, which the user had now provided.

I chained the operations in a single bash call with `&&`: 
```bash
git push origin fix/t03-stale-cleanup-observability \
  && gh pr ready 104 \
  && gh pr view 104 --json state,isDraft,url,headRefOid
```

The `&&` short-circuits at each step — if push fails, ready doesn't run; if ready fails, the verify-read doesn't run. This makes the dependency explicit in the command itself. (Two separate bash calls would have the same behavior in practice, but chaining communicates intent.)

The push fast-forwarded origin from `95232d52..62765e81` (4 commits — the 2 from last session that had been local-only PLUS this session's 2 race-fix and parity commits all landed in one push). `gh pr ready 104` returned `"✓ Pull request jpsweeney97/claude-code-tool-dev#104 is marked as ready for review"`. So far so good.

**Phase 5 — Catching the headRefOid consistency lag (~1 min):**

But the verification read showed `headRefOid: 95232d52d975...` — the **pre-push** HEAD! Not `62765e81`. This was either (a) a real failure (PR didn't update its head ref despite push and ready both succeeding), or (b) GitHub API consistency lag — the API hit a stale cached representation immediately after the push event.

I noted the discrepancy explicitly to the user as an insight ("Spot the inconsistency in the verification output...") and re-queried with more fields:

```bash
gh pr view 104 --json state,isDraft,url,headRefOid,commits \
  --jq '{state, isDraft, headRefOid, lastCommit: .commits[-1].oid, commitCount: (.commits | length)}'
```

The re-query came back: `headRefOid: 62765e81...`, `lastCommit: 62765e81...`, `commitCount: 16`, `isDraft: false`, `state: OPEN`. All fields converged to the local HEAD. Confirmed — the first stale read was indeed GitHub API consistency lag (the cached representation took a few seconds to invalidate after the push event).

This is what the project's verification framework calls "evidence before assertions": `gh pr ready 104` returning exit 0 only proves the API call was accepted, not that the PR is in the state I expect. Reading back the new state is the actual proof. **The verification leg correctly flagged the discrepancy as worth re-checking instead of trusting the first response** — and prevented me from telling the user "all good" while the API was actually still showing the wrong state.

**Phase 6 — Handoff request:**

User said *"Save a handoff for the next session /save"*. The session ends in a cleanly-closed state — no work in flight, the PR is now in human-review territory, and the next-session work depends on external feedback (CI results, reviewer comments, possible request for changes). This handoff captures the full session arc so future-Claude can pick up wherever the next signal arrives.

## Decisions

### Decision 1: Endorse the user's race fix as-is without proposing additional changes

**Choice:** After reviewing the user's already-applied diff (production code + 2 tests), tell the user "Nothing I'd change" and proceed directly to commit strategy. Did NOT propose additional tests, additional refactors, or alternative implementations.

**Driver:** The user had already done the analysis, written the fix, and added tests before the session began. The diff was sitting in the working tree at session start. Their task framing was *"Here is my feedback for the 2 commits from last session"* followed by the rationale and a "What Changed" / "Why It Changed" structure. This was a **review request, not a propose request**. Proposing additional changes when the user had already committed to a tight scope would be scope creep.

Verified in actual file content:
- Exception ordering correct (`FileNotFoundError` before `OSError`)
- Both race sites covered (stat + unlink)
- Both tests use evidence-based simulation rather than over-mocking
- Ruff clean, 546/546 tests pass, +2 new tests, zero regressions

**Alternatives considered:**
- **(a) Propose additional tests** — e.g., a 3rd test for the case where listdir itself raises FileNotFoundError. Rejected because that error doesn't reach the per-file loop (it raises during enumeration, caught at the function boundary).
- **(b) Propose `errno` discrimination** — only ignore `FileNotFoundError` if `exc.errno == errno.ENOENT`. Rejected because `FileNotFoundError`'s definition guarantees `errno == ENOENT`; the discrimination is redundant.
- **(c) Refactor the duplication** — extract a helper for the stat-and-unlink-with-race-handling. Rejected because the duplication is small (4 lines × 2 sites), the parallel structure is more readable than a helper, and refactoring into a helper would expand scope.
- **(d) Endorse as-is** (chosen)

**Rejection reasons:**
- (a) Out of scope; the function boundary handles enumeration errors elsewhere
- (b) `FileNotFoundError` is precisely defined; the check would be defensive without value
- (c) Premature abstraction; the local CLAUDE.md tenets explicitly call this out

**Trade-offs:** None — the user's fix is tight and the verification confirms it. Endorsing-as-is is the lowest-friction path that respects the user's work.

**Confidence:** Very high (E3) — verified by direct read of the diff, manual reasoning about the exception ordering invariant, and empirical test results (546 pass).

**Reversibility:** N/A — endorsement is informational; the user's fix had already been written.

**Change trigger:** If the empirical verification had failed (test failure, ruff failure, semantic regression in another caller), I would have surfaced the issue and proposed a fix. None of those happened.

### Decision 2: New 3rd local commit for the race fix (not amend to prior commits)

**Choice:** Commit the race fix as a new discrete `fix(containment)` commit `31ac66e8` rather than amending it into either of the 2 prior session's commits (`82d8cada` polish or `3568becd` test).

**Driver:** The race fix touches `server/containment.py` (production logic) and `tests/test_containment.py` (regression tests). Both prior session commits touched different file surfaces:
- `82d8cada` touched `scripts/containment_lifecycle.py` + 2 test docstrings (lifecycle polish)
- `3568becd` touched `tests/test_clean_stale_shakedown.py` only (new test file)

Different file surface = different concern = separate commit. Prior session's Decision 8 explicitly captured this rationale: *"Different types of changes warrant different commit types per conventional commit style... cleaner git history, easier to revert either independently"*. This session's race fix follows the same logic.

**Alternatives considered:**
- **(a) New commit** (chosen) — keeps git history clean, distinct commit type/scope, bisect-friendly
- **(b) Amend `82d8cada`** — bundles race fix with lifecycle polish; mixes concerns, harder to revert
- **(c) Amend `3568becd`** — wrong category; that commit is `test()` and the race fix is `fix()`
- **(d) Squash all 3 local commits** — minimizes commit count but loses bisect surface

**Rejection reasons:**
- (b) Mixes the lifecycle polish concern with the production race fix concern; bisect can't isolate either
- (c) Type/scope mismatch (test vs fix)
- (d) Premature optimization; the user's prior-session Decision 8 already endorsed separating commits

**Trade-offs:** One more commit message to write vs three. Minor overhead well worth the bisect surface.

**Implication:** Branch now has 3 distinct commits (and after this session's smoke_setup parity fix, 4) since `95232d52`. Each is a single-concern, well-tested change. Reviewer can request individual revert/squash if desired without losing information.

**Confidence:** High (E2) — matches existing branch style; verified by `git log` showing good structure.

**Reversibility:** Could squash later if reviewer requests it.

**Change trigger:** If reviewer says "please squash" — trivial.

### Decision 3: Drop "**Behavior-preserving**" framing from the smoke_setup production docstring

**Choice:** When updating `containment_smoke_setup.py:511-521`'s docstring as part of the I-2' format-parity fix, remove the **Behavior-preserving** prefix from the description of `_run_with_wrapper()`. Replace with current-state contract description.

**Driver:** The phrase "Behavior-preserving" was Round 6's commitment — *the extraction from the `__main__` block preserved what was there before*. After the format polish in this commit, the stderr text is no longer identical to the pre-Round-6 baseline. Keeping the phrase would mean the docstring describes a property the function no longer has. The cleanest fix: state the *current* contract directly and let `git log` carry the historical "behavior-preserving" framing where it belongs.

**Alternatives considered:**
- **(a) Drop "Behavior-preserving"** (chosen) — cleanest, factual, current-state
- **(b) Keep "Behavior-preserving" with caveat** — e.g., "Behavior-preserving relative to the Round 6 extraction baseline; the format was later polished to mirror lifecycle." Verbose and historical.
- **(c) Leave the phrase intact** — would make the docstring factually wrong about current behavior
- **(d) Just update the format reference and leave the framing** — partial fix; the framing is the real load-bearing word

**Rejection reasons:**
- (b) Historical caveats in docstrings rot; future readers shouldn't have to reason about commit history to understand current state
- (c) Factually wrong — docstrings should describe current state, not historical commitments
- (d) Half-fix; the framing word is the one that misleads

**Trade-offs:** The docstring becomes slightly longer (~12 lines vs 10) because the current-state description is more thorough than the original parenthetical. Worth it for accuracy.

**Implication:** The smoke_setup `_run_with_wrapper()` docstring now reads as a self-contained contract specification (format, exit code, happy path) with a brief note about the Round 6 extraction reason. Future readers don't need to know what "behavior-preserving" referred to.

**Confidence:** High (E2) — the framing was clearly tied to a specific historical context (Round 6) and that context no longer applies.

**Reversibility:** Trivial — could restore the framing if a future review prefers the historical anchoring.

**Change trigger:** Reviewer pushback that the historical anchor is more valuable than current-state clarity. Unlikely.

### Decision 4: Chain `push && ready && verify` in one bash call (not three separate calls)

**Choice:** Single bash call: `git push origin fix/t03-stale-cleanup-observability && gh pr ready 104 && gh pr view 104 --json state,isDraft,url,headRefOid`. Three operations chained with `&&`.

**Driver:** The three operations have a strict sequential dependency: push must succeed before mark-ready makes sense (otherwise the PR is in inconsistent state with the branch); mark-ready must succeed before verify-read makes sense (otherwise we're verifying the wrong state). The `&&` short-circuit makes that dependency explicit at the command level — if any step fails, subsequent steps don't run, and the failed step's output is the last thing visible.

**Alternatives considered:**
- **(a) Single chained call** (chosen) — atomic at the user-perception level; explicit dependency
- **(b) Three separate bash calls** — clearer per-step output but more roundtrips and slightly looser failure attribution
- **(c) Push first, wait for confirmation, then ready in a separate message** — over-cautious; the user explicitly authorized both actions in one message

**Rejection reasons:**
- (b) Same actual behavior in practice (I'd check each result), but the chained version makes the dependency structural rather than procedural
- (c) Redundant gating; the user said "Push + mark ready" together

**Trade-offs:** Output from all three commands lands in one tool-result block, slightly harder to scan than separate blocks. Mitigated by the fact that each command's output is short.

**Implication:** Both shared-state transitions completed in one observable atomic-ish step. If the push had failed (e.g., remote ahead, hook rejection), ready would never have fired and the PR would not have been left in a half-transitioned state.

**Confidence:** High (E2) — `&&` short-circuit is a well-understood shell idiom; verified by the actual successful execution.

**Reversibility:** N/A — both actions completed successfully.

**Change trigger:** If push had failed, I would have inspected the failure and reported to the user before any further action. The chained command is structurally safe even on failure.

### Decision 5: Re-query GitHub state after seeing stale `headRefOid` (vs trusting the first response)

**Choice:** When the first `gh pr view` response after push showed `headRefOid: 95232d52d975...` (the pre-push HEAD), I did NOT report success to the user. Instead I flagged the discrepancy as an insight and re-queried with more fields (`commits[-1].oid`, `commitCount`).

**Driver:** The verification-leg principle from the project's verification framework: `gh pr ready 104` returning exit 0 only proves the API call was accepted, not that the PR is in the state I expect. A discrepancy between local HEAD (`62765e81`) and remote `headRefOid` (`95232d52`) is either a real failure or an API consistency lag. Either way, "trust the first response" is wrong — the discrepancy needs explanation.

**Alternatives considered:**
- **(a) Report success and ignore the stale headRefOid** — fast but wrong if it's a real failure
- **(b) Re-query with more fields** (chosen) — surfaces additional convergent or divergent evidence
- **(c) Sleep N seconds and re-query** — works but blocks unnecessarily; the lag is typically <5 seconds and the immediate re-query typically catches the converged state
- **(d) Roll back the push** — overreaction; we don't yet know if it's a real failure

**Rejection reasons:**
- (a) Violates the verification-leg principle; would have left the user with false confidence
- (c) Unnecessary blocking; the immediate re-query worked
- (d) Premature; no evidence of failure yet

**Trade-offs:** Adds one extra API roundtrip (~200ms). Negligible.

**Implication:** The re-query confirmed convergence (`headRefOid: 62765e81`, `lastCommit: 62765e81`, `commitCount: 16`, `isDraft: false`). The first response was indeed GitHub API consistency lag, not a real failure. The user has correct, verified state instead of false success.

**Confidence:** Very high (E3) — verified by the converged re-query, and the post-hoc explanation (API lag vs real failure) was disambiguated by the second result.

**Reversibility:** N/A — read-only verification.

**Change trigger:** If the re-query had ALSO shown stale state, I would have escalated to the user with the discrepancy and waited before proceeding.

### Decision 6: Update the test docstring at line 214 but NOT the second test docstring at lines 322-333

**Choice:** When updating test_containment_smoke_setup.py to reflect the new smoke_setup format, edit only the first test's docstring (line 214 — `test_prepare_scenario_surfaces_cleanup_enumeration_failure`). Leave the second test's docstring (lines 322-333 — `test_prepare_scenario_main_wrapper_fail_fast_via_monkeypatched_listdir`) untouched, even though it contains the phrase "same stderr text" in describing the Round 6 extraction.

**Driver:** The two docstrings reference the format differently:
- **Line 214 docstring**: explicitly quotes the format as `"containment_smoke_setup failed: <exc>"` — a factual present-tense claim about what the wrapper writes. Becomes false after the format change. **Must update.**
- **Lines 322-333 docstring**: says "Round 6 extracted... as a behavior-preserving refactor (same stderr text, same SystemExit(1) on exception, same happy-path SystemExit(main(argv)))". This is describing **Round 6's historical commitment** — at the time of the extraction, the stderr text was preserved. The historical claim is still accurate even after the format change. **Leave intact.**

**Alternatives considered:**
- **(a) Update both for consistency** — would require rewriting the historical anchoring in the second docstring
- **(b) Update only the first** (chosen) — preserves the historical context that explains *why* the Round 6 refactor happened
- **(c) Leave both** — would leave the line 214 docstring factually wrong

**Rejection reasons:**
- (a) Loses the historical context; the second docstring is teaching future readers about why Round 6 was needed, not specifying current behavior
- (c) Factually wrong on the line 214 quote

**Trade-offs:** Slight asymmetry — the two test docstrings now describe the format differently. Mitigated by the fact that they describe it from different angles (factual quote vs historical commitment).

**Implication:** Future readers see (a) the current format in the line 214 docstring (factual specification) and (b) the Round 6 historical context in the lines 322-333 docstring (motivation for the refactor). Both are accurate; together they tell a complete story.

**Confidence:** High (E2) — the distinction between "factual current quote" and "historical commitment" is explicit in the docstring text itself.

**Reversibility:** Trivial — could update the second docstring if reviewer prefers full uniformity.

**Change trigger:** Reviewer feedback that the asymmetry is confusing. Unlikely given the docstring framing.

## Changes

**Session produced 2 new commits on `fix/t03-stale-cleanup-observability` and pushed all 4 local commits to origin.** Branch is now on parity with origin at `62765e81`. PR #104 transitioned from draft to ready for review.

### Commit log (this session)

| Commit | Type | Files | Insertions/Deletions | Description |
|---|---|---|---|---|
| `31ac66e8` | fix | 2 | +55/-1 | `fix(containment): ignore FileNotFoundError races in per-file sweep loop` |
| `62765e81` | fix | 2 | +16/-10 | `fix(containment-smoke-setup): preserve exc class in fail-FAST log` |

Total this session: ~71 insertions, ~11 deletions across 4 files.

### File-by-file changes

**`packages/plugins/codex-collaboration/server/containment.py`** (commit `31ac66e8`, +7/-1 lines, written by user, committed by Claude):

- Added `except FileNotFoundError: continue` ahead of `except OSError as exc:` at the `path.stat()` site (around line 468). The specific-subclass-first ordering is load-bearing because `FileNotFoundError` is a subclass of `OSError` — Python matches top-down, so the wrong order would silently swallow the FileNotFoundError into the generic handler.
- Added the same pattern at the `path.unlink()` site (around line 481), parallel structure.
- Updated the docstring at line 363 to add: *"Concurrent-deletion races after `os.listdir()` are ignored because the stale file is already gone."*
- Root-level failures (the three-stage shakedown-dir check earlier in the function) remain untouched. Only per-file races are reclassified as benign.

**`packages/plugins/codex-collaboration/tests/test_containment.py`** (commit `31ac66e8`, +49/-0 lines, NEW tests by user, committed by Claude):

- New test `test_clean_stale_files_ignores_candidates_removed_before_stat` (~25 lines): monkeypatches `os.listdir` via `monkeypatch.context()` to return a never-created filename (`seed-run-1.json`). When production code calls `path.stat()`, the kernel returns a real `FileNotFoundError` because the file was never created. Asserts all 4 result buckets empty AND `had_errors=False`.

- New test `test_clean_stale_files_ignores_candidates_removed_before_unlink` (~30 lines): more elaborate simulation. Creates a real stale file (mtime 26 hours old via `os.utime`), captures `original_stat = Path.stat` and `original_unlink = Path.unlink`, then defines a wrapper `stat_then_remove(self, ...)` that:
  1. Calls `original_stat(self, ...)` to get the stat result
  2. If `self == stale`, calls `original_unlink(self)` to remove the file
  3. Returns the stat result
  
  Monkeypatches `Path.stat` with this wrapper inside `monkeypatch.context()`. When production code subsequently calls `path.unlink()`, the file is already gone. Includes an explicit `assert not stale.exists(), "simulated concurrent deletion should remove the file"` guard so the test fails loudly if the mock ever stops firing. Asserts all 4 result buckets empty AND `had_errors=False`.

**`packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py`** (commit `62765e81`, +14/-8 lines):

- Production code at line 525: changed `print(f"containment_smoke_setup failed: {exc}", file=sys.stderr)` to a 4-line parenthesized form:
  ```python
  print(
      f"containment_smoke_setup failed: unexpected error. Got: {exc!r:.100}",
      file=sys.stderr,
  )
  ```
- The new format mirrors `containment_lifecycle.py:188`'s pattern from commit `82d8cada`: `<prefix>: <description>. Got: {exc!r:.100}`. Both fail-* outer boundaries now produce a parseable, class-preserving exception trail.
- Production docstring at lines 511-521: rewrote the `_run_with_wrapper()` description. Dropped the "**Behavior-preserving**" prefix (which referenced the Round 6 extraction baseline, no longer accurate after the format change) and replaced with a current-state contract description that includes the new format, the truncation rationale, and a brief note about parity with the lifecycle convention.

**`packages/plugins/codex-collaboration/tests/test_containment_smoke_setup.py`** (commit `62765e81`, +2/-2 lines):

- Updated the docstring of `test_prepare_scenario_surfaces_cleanup_enumeration_failure` (around line 214): changed the quoted format from `"containment_smoke_setup failed: <exc>"` to `"containment_smoke_setup failed: unexpected error. Got: <repr(exc)>"`. Minimal 2-line edit; no test logic changes.
- Did NOT update the second test's docstring at lines 322-333 (Decision 6 above).

## Codebase Knowledge

### Architecture: Two distinct error surfaces, three callers, ONE format template (now)

The T-03 PR's core architectural insight is that `clean_stale_files` exposes TWO error surfaces to its 3 callers. As of this session's commits, all 3 callers now use the SAME `Got: {exc!r:.100}` format template at the outer boundary.

| Caller | Path | Wrapper | Exit | Stderr template | Policy |
|---|---|---|---|---|---|
| **CLI wrapper** | `scripts/clean_stale_shakedown.py` | inline `__main__` block | 1 | `clean_stale_shakedown failed: unexpected error. Got: {exc!r:.100}` | fail-FAST |
| **Smoke setup** | `scripts/containment_smoke_setup.py` | `_run_with_wrapper()` function | 1 | `containment_smoke_setup failed: unexpected error. Got: {exc!r:.100}` | fail-FAST |
| **Lifecycle hook** | `scripts/containment_lifecycle.py` | `main()` outer `except Exception` | **0** | `containment-lifecycle: internal error. Got: {exc!r:.100}` | **fail-OPEN** |

The fail-OPEN vs fail-FAST distinction is unchanged — lifecycle cannot raise or return non-zero because SubagentStart treats that as "block the agent spawn", a containment-state defect must surface via stderr observability never via the hook's exit code. But the **format template is now uniform across all 3**: operators learn one parse pattern and apply it everywhere.

Per-file error surface (sweep loop in `clean_stale_files`):
- `clean_stale_files()` returns `CleanStaleResult` with `removed` + `skipped_fresh` + `failed_stat` + `failed_unlink` buckets
- `had_errors` property is True iff `failed_stat` or `failed_unlink` is non-empty
- **NEW (this session, commit `31ac66e8`)**: `FileNotFoundError` at `path.stat()` or `path.unlink()` is no longer recorded — it's a benign concurrent-deletion race; the caller's goal (file gone) is already achieved
- Other `OSError` subclasses still recorded in `failed_stat`/`failed_unlink` as before
- Each caller does `if result.had_errors: print(result.report(prefix=...), file=sys.stderr)` with its own caller prefix

Root-level error surface (three-stage check at the start of `clean_stale_files`):
- `clean_stale_files()` raises `OSError` with stage-specific messages (Stage 1 lstat, Stage 2 type check, Stage 3 enumeration)
- Caller's outer exception boundary wraps it with caller-specific context and exit code via the now-uniform `Got: {exc!r:.100}` template
- `CleanStaleResult.report()` is NOT called for root-level failures because the function raises before returning a result

### Files read this session

| File | Why | Key findings |
|---|---|---|
| `docs/handoffs/2026-04-11_21-24_*.md` | Handoff load via `/handoff:load` | 9 decisions, 5-reviewer review, 4 outstanding next-action options, explicit user approval gate |
| `packages/plugins/codex-collaboration/server/containment.py` (diff only via `git diff`) | Verify user's race fix | +7/-1 lines, exception ordering correct, docstring updated |
| `packages/plugins/codex-collaboration/tests/test_containment.py` (diff only via `git diff`) | Verify user's regression tests | +49 lines, 2 new tests at lines 302 and 320, both use evidence-based simulation |
| `packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py` (lines 490-540) | Locate I-2' defect at line 525 + read `_run_with_wrapper` docstring | Confirmed `{exc}` defect on line 525, `_run_with_wrapper` extracted in Round 6, docstring claims "behavior-preserving" |
| `packages/plugins/codex-collaboration/tests/test_containment_smoke_setup.py` (lines 200-410) | Map all docstring/assertion touchpoints for the format change | Found 7 grep hits; 3 need editing, 4 are robust to format change |
| `packages/plugins/handoff/skills/save/synthesis-guide.md` | Handoff writing | 13 required sections, evidence requirements, depth targets per section |
| `packages/plugins/handoff/references/format-reference.md` | Handoff writing | Frontmatter schema, section checklist, quality calibration table |
| `packages/plugins/handoff/references/handoff-contract.md` | Handoff writing | Chain protocol, state file conventions, git tracking policy |

### Test patterns confirmed/extended this session

- **Race condition simulation via filesystem ground truth**: Test 1 of the race fix (`ignores_candidates_removed_before_stat`) simulates FileNotFoundError by monkeypatching `os.listdir` to return a non-existent filename. The kernel then provides the real exception when production calls `path.stat()`. **Pattern**: when testing error handling, prefer tests that elicit real OS errors over tests that throw fake ones.
- **TOCTOU window simulation via stat-then-remove**: Test 2 (`ignores_candidates_removed_before_unlink`) wraps `Path.stat` with a callable that *also* removes the file after returning the stat result, then re-binds it via `monkeypatch.setattr(Path, "stat", ...)`. The class-level rebinding means the wrapper receives `self` automatically. The `assert not stale.exists()` post-condition guards against the mock silently failing.
- **Substring-vs-exact-match for evolving formats**: Existing test assertions in `test_containment_smoke_setup.py` at lines 283, 397, 289, 403 use substring matching (`"containment_smoke_setup failed" in result.stderr`, `"cannot enumerate shakedown root" in captured.err`). This decoupled the format from the contract, making this session's format polish trivial — no test edits needed beyond the docstring quotes.
- **Truncation arithmetic for substring assertions**: When changing a format from `{exc}` to `{exc!r:.100}`, verify that any substring assertions on the wrapped exception's content still land within the 100-char window. For an `OSError("clean_stale_files failed: cannot enumerate shakedown root. ...")`, the substring "cannot enumerate shakedown root" appears at character positions 36-66 of the repr — well within the cap.

### Key locations (updated this session)

| Concept | Location |
|---|---|
| FileNotFoundError race handling at stat() site | `containment.py:468-471` (NEW per `31ac66e8`) |
| FileNotFoundError race handling at unlink() site | `containment.py:481-484` (NEW per `31ac66e8`) |
| Race-fix policy docstring | `containment.py:363-366` |
| Race regression tests | `test_containment.py:302-348` (NEW per `31ac66e8`) |
| Smoke-setup outer boundary (now uniform format) | `containment_smoke_setup.py:522-530` (UPDATED per `62765e81`) |
| `_run_with_wrapper` docstring (current contract) | `containment_smoke_setup.py:511-521` (UPDATED per `62765e81`) |
| Smoke-setup test docstring (factual quote) | `test_containment_smoke_setup.py:214-215` (UPDATED per `62765e81`) |
| Smoke-setup test docstring (Round 6 historical) | `test_containment_smoke_setup.py:322-333` (UNCHANGED — historical context) |

## Context

### Branch and PR state

- **Branch:** `fix/t03-stale-cleanup-observability`
- **HEAD commit:** `62765e81` (local + remote in sync)
- **Origin commit:** `62765e81` (just pushed)
- **Commits ahead of origin:** 0 (now in sync)
- **Commits ahead of main:** 16 total (12 prior + 2 last session + 2 this session)
- **PR #104 state:** OPEN, **ready for review** (no longer draft), URL https://github.com/jpsweeney97/claude-code-tool-dev/pull/104
- **PR `headRefOid` (verified):** `62765e810e0f53cec4c45c710d375648ac107498`
- **PR `commitCount`:** 16

### Test baseline

- **Pre-session baseline:** 544 tests passing (from prior session's commit `3568becd`)
- **This session added:** 2 new tests (the race regression tests in commit `31ac66e8`)
- **Post-session baseline:** **546 tests passing** (macOS non-root)
- **Verification frequency:** ran twice this session (after race fix commit, after smoke_setup commit). Both runs: 546 passed.
- **Alternative baselines (not re-verified this session):** Root/Windows: 543 passed + 3 skipped (the 3 chmod tests skip)

### Ruff quality gate

All 4 edited files pass `uv run ruff check <file>` (file-scoped, not package-wide). Verified twice this session (once per commit). Package-wide ruff NOT run — pre-existing failures in unrelated files per project policy.

### Mental model for this session

**Framing:** This is a chained-action session with 3 distinct phases (review user's work, fix consistency gap, execute publish). Each phase has its own approval gate and verification checkpoint. The user is the priority-setter; I'm the executor and the verifier.

**Core insight:** The user's pattern of "fix in place, then ask for review" is structurally different from "describe the fix, then ask for proposal". When they bring a diff, my job is verification, not creation. When they say "we should fix X", my job is execution of an already-identified problem, not re-investigation.

**Mental model:** "Approval-gated execution" — the session is composed of discrete actions with explicit user authorization between them. The boundaries are: (1) inspection of prior work, (2) commit of new work, (3) shared-state transitions. Each boundary requires explicit user assent. Verification (read-back) is a first-class step, not an afterthought.

### Environment state

- macOS Darwin 25.3.0
- Python 3.14.2
- pytest 9.0.2 with anyio-4.12.1, asyncio-1.3.0 plugins
- `uv` for all Python tool invocations (no direct `pip`, `pytest`, `ruff` calls)
- Working directory throughout session: `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration` (already inside the package)
- Test runs and ruff invocations executed from package directory

## Conversation Highlights

### User's race-condition feedback (the opening exchange)

The user opened the session with a structured, evidence-based finding. Verbatim:

> "Here is my feedback for the 2 commits from last session: The patch largely does what it intends, but the new per-file error reporting misclassifies benign concurrent deletions as cleanup failures. That can produce misleading stderr from all three callers during overlapping sweeps."

Followed by the P3 finding with file:line evidence:

> "[P3] Ignore FileNotFound races when sweeping listed candidates — `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/server/containment.py:468-471` Once `os.listdir()` has built candidates, another cleanup invocation can legitimately remove one of those files before this code reaches `stat()` or the `unlink()` a few lines below. Right now those FileNotFoundErrors are recorded in `failed_stat`/`failed_unlink`, which flips `had_errors` and makes `clean_stale_shakedown`, `containment_lifecycle`, and `containment_smoke_setup` emit an operator-visible error report even though the stale file is already gone. Treating FileNotFoundError as a benign lost race here would avoid false-positive cleanup failures under overlapping sweeps."

Then a "What Changed" / "Why It Changed" structure describing the fix they had **already applied**:

> "I updated `packages/plugins/codex-collaboration/server/containment.py:358` so the per-file sweep loop treats FileNotFoundError as a benign lost race at both `stat()` and `unlink()` time instead of recording it in `failed_stat` / `failed_unlink`. I also tightened the docstring at `packages/plugins/codex-collaboration/server/containment.py:363` to say concurrent deletions after `os.listdir()` are ignored.
> 
> I added two regression tests in `packages/plugins/codex-collaboration/tests/test_containment.py:302` and `packages/plugins/codex-collaboration/tests/test_containment.py:320` covering: candidate listed, then missing before stat(); stale file observed by stat(), then removed before unlink()."

The structure of this message — finding with evidence, action taken, rationale — established the session's working pattern: **review-first, then commit**.

### User's smoke_setup directive (terse, decisive)

After the race fix landed in commit `31ac66e8`, I asked the user about next steps. They said:

> "We should fix `containment_smoke_setup.py`"

That's the entire message. No preamble, no debate. The smoke_setup defect had been on the open-questions list from the prior handoff (Q1: "Should `containment_smoke_setup.py:525` be fixed in the same PR?"), so this was an answer to a pre-existing question, not new investigation. The terseness reflects the user's decisive style on previously-discussed items.

### User's authorization for shared-state actions

After the smoke_setup parity commit landed, I presented 4 options (push, push+mark-ready, hold, other). User said:

> "Push + mark ready"

Three words. Maximum information density. Both shared-state actions authorized in one message. This is the user's pattern for explicit approval — direct, unambiguous, no qualifications.

### User's structured feedback message style

The user's race-fix message used a notable convention: **P-rated severity** (P3 in this case). This is software-engineering shorthand for issue priority (P0 = blocker, P1 = critical, P2 = important, P3 = polish-class problem worth fixing but not blocking, P4 = nice-to-have). P3 here meant "real defect, but the PR is functional without the fix; worth addressing before review". The label calibrated my sense of urgency without me having to ask.

### Mid-session insight observation about consistency lag

When the first `gh pr view` returned a stale `headRefOid`, I called it out explicitly to the user as an insight:

> "Spot the inconsistency in the verification output: The `git push` command clearly shows `95232d52..62765e81` (origin advanced from `95232d52` to `62765e81`), and `gh pr ready 104` reported success. But the `gh pr view` `headRefOid` field still shows `95232d52d975...` — the *pre-push* HEAD. That's almost certainly GitHub's API consistency lag... but I shouldn't assume — the verification leg is doing its job by surfacing the discrepancy. Let me re-query to confirm convergence."

The user did not need to prompt for the re-query. The verification framework was load-bearing — without the read-back, I would have reported success based on a stale state.

## User Preferences

**Bring-the-diff workflow (this session, observed):**
The user wrote production code AND test code AND a "What Changed / Why It Changed" rationale BEFORE invoking Claude. They didn't ask Claude to design the fix; they asked Claude to verify and commit it. This suggests:
- **Implication**: When the user provides a diff with rationale, treat it as a review request, not a design request
- **Anti-pattern**: Proposing additional changes, alternative implementations, or "improvements" to a user-provided diff unless verification surfaces a real defect

**P-rated severity language (observed):**
> "[P3] Ignore FileNotFound races when sweeping listed candidates"
- The user uses standard P0–P4 severity rating in feedback
- P3 = real defect, polish-class urgency, worth fixing before invitation to review
- **Implication**: When reading user feedback, treat the P-rating as ground truth for urgency calibration; don't second-guess the priority

**Decisiveness on previously-identified items (observed):**
> "We should fix containment_smoke_setup.py" (3 words)
- When the user has already discussed an issue in a prior session and decides to act on it, the directive is short and unconditional
- **Implication**: Don't re-litigate the decision — they've already weighed it; just execute

**Authorization compactness (observed):**
> "Push + mark ready" (3 words)
- Multiple shared-state actions can be authorized in one terse message when they belong together
- **Implication**: Treat compact authorizations as fully-loaded — execute all named actions in sequence, with appropriate verification between them

**Verification expectation (inferred from prior handoff + this session):**
The user appreciates when I run ruff + pytest before reporting "looks good", and when I read back state from external systems before claiming success. They didn't ask me to do this — they expect it. The prior handoff captured this as a pattern; this session confirmed it.

**Approval gates (carried forward from prior handoff):**
The user uses the handoff/load cycle as an explicit approval gate for irreversible actions. *"I will inspect this work and share my feedback with you in the next session"* is the canonical phrase. **Implication**: Don't push, mark ready, or take other shared-state actions when the user has installed an approval gate, even if subsequent context implies enthusiasm.

**Communication style observations (consistent with prior handoff):**
- Terse messages with high information density
- Explicit priority weighting when correcting
- Treats handoffs as first-class working memory
- Uses numbered/bulleted lists for structured options
- Doesn't waste words on social niceties

## Learnings

### When the user brings a diff, verify don't propose

**Mechanism:** The user's "Here is my feedback" message included a complete diff already applied to the working tree, with rationale and tests. The session's optimal response was to verify the diff (ruff + pytest + manual code reading) and commit it, not to propose alternatives or additional changes.

**Evidence:** This session's verification (ruff clean + 546 tests pass + manual exception-ordering check) confirmed the user's diff was correct without modification. Proposing alternatives would have been scope creep and a poor read of the user's intent.

**Implication:** Develop a "review mode" for sessions where the user brings work in. The mode is: (1) read the diff, (2) verify empirically, (3) check exception ordering / similar load-bearing patterns, (4) report verification results, (5) ask about commit strategy. NOT: (1) read the diff, (2) imagine alternatives, (3) propose them.

**Watch for:** Misreading verification mode as design mode. The signal is the user providing both code AND rationale, especially with structured "What Changed / Why It Changed" framing — that's a finished product asking for sign-off.

### Substring assertions decouple format from contract

**Mechanism:** The smoke_setup tests asserted `"containment_smoke_setup failed" in stderr` (a prefix substring) and `"cannot enumerate shakedown root" in stderr` (the wrapped exception's content). When I changed the format from `{exc}` to `unexpected error. Got: {exc!r:.100}`, both substrings still appeared in the new format. **Zero test edits required for the format change** — only docstring updates.

**Evidence:** Commit `62765e81` modified `tests/test_containment_smoke_setup.py` by only +2/-2 lines, all in a docstring. The actual test logic (the assertions at lines 283, 289, 397, 403) was unchanged, and all 3 smoke_setup tests passed unchanged.

**Implication:** When writing assertions on error messages or log output, prefer substring matching for the load-bearing parts (caller prefix that routes operator attention; wrapped exception context that proves causation) over exact-match. The format then becomes a polish surface that can evolve without breaking tests. Apply this pattern to new tests in the same area.

**Watch for:** The temptation to assert on exact format strings for "test specificity". The cost is brittleness whenever the format polishes; the benefit is dubious because the test is testing the framework (does Python's f-string format correctly?) rather than the contract (does the wrapper route the right context?).

### GitHub API has eventual consistency on PR head refs after push

**Mechanism:** Immediately after `git push` succeeds, `gh pr view 104 --json headRefOid` may return the *pre-push* HEAD for a few seconds. The PR's HTTP API representation is cached and takes a moment to invalidate after the push event reaches the GitHub backend. The branch ref itself is updated immediately (visible via `git ls-remote`); the PR association lags slightly.

**Evidence:** This session's first `gh pr view` after push returned `headRefOid: 95232d52d975...` (the pre-push HEAD). A re-query ~3 seconds later returned `headRefOid: 62765e81...` (the post-push HEAD). The push had clearly succeeded — `git push` output showed `95232d52..62765e81 fix/t03-stale-cleanup-observability -> fix/t03-stale-cleanup-observability`.

**Implication:** When verifying a PR state after push, do NOT trust the first `gh pr view` response. Either (a) re-query after a brief delay, (b) compare against `git ls-remote` for the branch ref directly, or (c) include both `headRefOid` and `commits[-1].oid` in the query — they should converge once the lag clears.

**Watch for:** Concluding "the push didn't take" based on a stale `headRefOid`. The branch ref is the authoritative state; the PR HTTP representation is a denormalization that converges. If you're really worried, check `git ls-remote origin <branch>` which is the live ref state.

### `FileNotFoundError` MUST come before `OSError` in except chains

**Mechanism:** Python's `try/except` matches clauses top-down. `FileNotFoundError` is a subclass of `OSError`, so `except OSError` will catch `FileNotFoundError` instances. If you put `except OSError` first, the `except FileNotFoundError` clause is unreachable — the more general handler eats the more specific case.

**Evidence:** This session's race fix at `containment.py:468-471, 481-484` places `except FileNotFoundError: continue` before `except OSError as exc:`. If reversed, the FileNotFoundError would be appended to `failed_stat`/`failed_unlink` (the bug being fixed) and the new clause would never run. Verified by code reading and by the regression tests passing (which would fail if the order were wrong).

**Implication:** Whenever distinguishing exception subclasses in an `except` chain, the **specific subclass MUST come first**. This is a general Python rule, not specific to this codebase. Apply when:
- Catching `PermissionError` separately from `OSError`
- Catching `IsADirectoryError` separately from `OSError`
- Catching `KeyError` separately from `LookupError`
- Catching `UnicodeDecodeError` separately from `ValueError`

**Watch for:** Code reviewers (human or AI) who reorder except clauses "for readability" — the alphabetical order is not the correct order; the subclass hierarchy is.

### Verification leg catches consistency lag

**Mechanism:** The principle "evidence before assertions" means after every state-changing action, you read back the state from the authoritative source before claiming success. When the read-back diverges from expectation, that's evidence — either a real failure or eventual consistency, both worth investigating before reporting.

**Evidence:** This session's `gh pr view` returned stale `headRefOid` after a successful push. Without the read-back, I would have reported "Push and ready complete" with the user believing the new commits were associated with the PR. The re-query revealed the truth (lag, not failure), and the user got verified state instead of plausible-but-unverified state.

**Implication:** Always include a read-back verification step after shared-state actions. The cost is one extra API call (~200ms); the benefit is correctness. Apply to: PR creation, PR ready/draft transitions, push operations to remote branches, branch protection rule changes, anything that interacts with a remote service that can have eventual consistency or webhook lag.

**Watch for:** Treating "the command returned exit 0" as proof of success. Exit 0 means "the API call was accepted", not "the state I expected is now true". The two are often the same but not always.

## Next Steps

### 1. Watch CI on PR #104 (next-session action if CI runs)

**Dependencies:** None — CI runs are async, may already be in progress or may not run depending on repo config for ready PRs.

**What to read first:** `gh pr checks 104` to see what's running. `gh pr view 104` to see overall status.

**Approach suggestion:** If CI is configured to run on PR ready transitions, the push + ready combination should trigger checks. Watch for completion via `gh pr checks 104 --watch` (blocking) or one-shot polling. If failures are unrelated pre-existing issues (per the prior handoff's known package-wide ruff failures), document and move on. If failures are caused by this PR's changes, investigate immediately.

**Acceptance criteria:** All required CI checks green, OR documented failures that are confirmed pre-existing and unrelated.

**Potential obstacles:** The repo may not have CI configured for draft → ready transitions, in which case nothing runs and there's nothing to watch. Test environment may differ from local (e.g., Linux vs macOS, root vs non-root) — the 3 chmod tests skip on root, so CI test counts may differ.

### 2. Address reviewer feedback when it arrives (next-session action)

**Dependencies:** Human review, which is now possible since the PR is ready.

**What to read first:** `gh pr view 104 --comments` for in-thread comments; `gh api repos/jpsweeney97/claude-code-tool-dev/pulls/104/reviews` for review-level comments.

**Approach suggestion:** Reviewer feedback typically falls into 4 categories: (a) requested changes (must address before merge), (b) suggestions (consider but optional), (c) questions (clarify in thread), (d) approval. For (a), make the changes in new commits on the same branch. For (b), discuss with user before implementing. For (c), respond directly with explanation.

**Acceptance criteria:** All requested changes addressed, all questions answered, review approved or merged.

**Potential obstacles:** Reviewer may request commit history changes (squash, reorder, split) — handle via interactive rebase OR new commits on top, depending on user preference. Reviewer may surface architectural concerns the prior 7-round adversarial review missed — escalate to user before making structural changes.

### 3. (Optional) Address the 7 deferred Suggestions from the prior session's review

**Dependencies:** Decision from user on whether to address in this PR (additional commits) or a follow-up PR.

**What to read first:** Prior handoff's "Suggestions (7 found)" subsection in the Session Narrative. Most leveraged: S-1 (`NamedTuple FileFailure`).

**Approach suggestion:** S-1 is the highest-leverage — replacing the positional tuple `(path, error_repr)` in `failed_stat`/`failed_unlink` with a `NamedTuple` removes positional-unpack fragility and improves readability. ~15 lines of refactor + minor test updates. The other 6 suggestions are lower-leverage and can be deferred indefinitely.

**Acceptance criteria:** Per-suggestion decision made (include in this PR / follow-up PR / skip), and any chosen suggestions implemented and verified.

**Potential obstacles:** User pushed back on similar scope-expansion suggestions in the prior session ("Option B if you want the strongest pre-review state... not Option A"). For this PR, scope discipline argues for deferring — but if reviewer requests S-1 specifically, address it directly.

### 4. Update ticket `T-20260410-03` status at merge time

**Dependencies:** PR merged.

**What to read first:** `docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md`

**Approach suggestion:** Edit frontmatter `status: deferred` → `status: done`. Optionally fix the pre-existing wrong `branch:` field if it's still wrong. Single-file edit, no other dependencies.

**Acceptance criteria:** Ticket reflects completed status; branch field accurate.

**Potential obstacles:** None — bookkeeping operation.

### 5. (Carried forward) Address open questions about `superpowers:finishing-a-development-branch`

**Dependencies:** Curiosity-driven; not blocking.

**What to read first:** `~/.claude/plugins/cache/claude-plugins-official/superpowers/*/skills/finishing-a-development-branch/SKILL.md` (or similar).

**Approach:** Read-only lookup. Question: "Does invoking this skill auto-mark-ready, or does it pause for approval?" The prior handoff's Q3.

**Acceptance criteria:** Question answered. May lead to future use of the skill once its behavior is understood.

## In Progress

**Clean stopping point — PR #104 transitioned to ready, all 4 commits pushed, no work in flight.**

The session executed all 3 phases (review user's race fix → close smoke_setup parity → push + mark ready) to completion. The only "in progress" artifact is the PR's transition to **human review state** — that's not a technical in-progress state (nothing is half-written or broken locally), it's an external dependency on either CI or human reviewer feedback.

Local state at session end:
- `git status`: clean (working tree, no uncommitted changes)
- `git log origin/fix/t03-stale-cleanup-observability..HEAD`: empty (local matches remote)
- 4 commits ahead of `origin/main` for this branch (16 total since main)
- 546/546 tests passing
- ruff clean on all 4 modified files
- PR #104: OPEN, ready for review, headRefOid converged to local HEAD

## Open Questions

### 1. Will CI run on the now-ready PR?

**Context:** The repo's CI configuration determines whether the draft → ready transition triggers checks. Some repos run CI on every push regardless of draft state; others gate on ready-for-review.

**How to find out:** Check for `.github/workflows/*.yml` in the repo root, look for `pull_request:` triggers and `types: [ready_for_review]` filters. Or just observe via `gh pr checks 104` after a few minutes.

### 2. How will reviewers feel about the 4-commit structure?

**Context:** This PR has 16 total commits (12 pre-session + 4 from sessions 2 and 3). Some reviewers prefer squashed-to-one for clean main history; others appreciate the granularity for bisect.

**Options if requested:** Interactive rebase to squash, OR `gh pr merge --squash` at merge time. The user's prior session Decision 8 favored separate commits, so the current structure is the user's preference.

### 3. Should we proactively address Suggestion S-1 (`NamedTuple FileFailure`) before reviewer asks?

**Context:** S-1 is the highest-leverage of the 7 deferred suggestions from the prior session's parallel reviews. It removes positional-tuple fragility in `CleanStaleResult.failed_stat`/`failed_unlink`.

**Options:**
- (a) Address now as commit 5 before any reviewer comments — proactive polish
- (b) Wait to see if reviewer asks — scope-faithful
- (c) Defer to a follow-up PR after merge — minimum churn for this PR

**Bias:** (b) — scope discipline argues for not expanding scope post-mark-ready unless requested.

### 4. (Carried forward) Does `superpowers:finishing-a-development-branch` auto-mark-ready?

**Context:** Same as prior handoff Q3. Now somewhat moot since this session manually marked ready, but useful to know for future PRs.

**How to find out:** Read the skill's SKILL.md.

### 5. Will the smoke_setup format change ripple to any external log parsers?

**Context:** The format change in `62765e81` changed `containment_smoke_setup failed: <exc-msg>` to `containment_smoke_setup failed: unexpected error. Got: <repr(exc)>`. Any external log parser that splits on `"failed: "` and reads the next token as the exception message will now see the literal string "unexpected error. Got:".

**How to find out:** Grep the codebase + monitoring configs for parsers of this prefix. If found, decide whether to update the parser or revert to a more conservative format. The change was modeled on the lifecycle pattern from `82d8cada`, which presumably went through the same consideration in the prior 7-round plan review.

## Risks

### 1. Race fix's Test 2 couples to internal Path.stat behavior

**Impact:** `test_clean_stale_files_ignores_candidates_removed_before_unlink` monkeypatches `Path.stat` at the class level. If a future Python version refactors how `pathlib.Path.stat` is implemented (e.g., wraps it in a `functools.cached_property` or moves it to a C extension), the monkeypatch target may stop working. The test would fail loudly (no SystemExit raised, or wrong assertion behavior), not silently — that's the correct failure mode.

**Mitigation:** Test 1 (`test_clean_stale_files_ignores_candidates_removed_before_stat`) covers the same race window via a different path (filesystem-level FileNotFoundError). If Test 2 ever breaks, Test 1 still pins the contract. The redundancy is intentional.

### 2. CI may surface failures unrelated to this PR

**Impact:** The package has known pre-existing ruff failures in other files (per prior handoff's "Pre-existing package-wide ruff failures" gotcha). If CI runs `ruff check` package-wide, it will fail on those files even though this PR's changes are clean.

**Mitigation:** The plan doc explicitly noted this as known. If CI fails on unrelated files, document and move on. If CI fails on this PR's changes specifically, investigate.

### 3. Smoke_setup format change ripples to anything that parsed the old format

**Impact:** Already covered in Open Questions #5. External log parsers, dashboards, or alerts that split on the old format will see different content. If any exist and aren't updated, they may surface false alerts or miss real ones.

**Mitigation:** Grep the codebase + monitoring configs for parsers. The lifecycle pattern from `82d8cada` was already changed in the prior session, so any parser of THAT format would have already broken — if it didn't, the format change is safe for both.

### 4. Reviewer may want different commit structure

**Impact:** A reviewer who prefers single-commit PRs may request squash. The 4 commits in this PR (plus the 12 prior) total 16 — squashing loses bisect surface but produces a clean main history.

**Mitigation:** Either approach is fine. User's prior Decision 8 favored separate commits; if reviewer overrides, defer to user for the final call. Squash can be done at merge time via `gh pr merge --squash`.

### 5. (Carried forward) Pyright continues to be advisory; no permanent fix

**Impact:** Same as prior handoff. Pyright fires false positives (pytest import not resolved, "not accessed" warnings on intentional unused params). Developer ergonomics slightly degraded.

**Mitigation:** Documented. Project policy: trust ruff + pytest as authoritative. Could add project-level Pyright config, but out of scope.

### 6. `gh pr view` may show stale state immediately after push

**Impact:** This session encountered this exact issue. Future sessions querying PR state immediately after push may see stale `headRefOid` and conclude push failed. Wasted investigation time, possible false escalation.

**Mitigation:** New gotcha (below). Always re-query if `headRefOid` doesn't match local HEAD; the lag is typically <5 seconds.

## References

**PR, branch, commits:**
- PR #104: https://github.com/jpsweeney97/claude-code-tool-dev/pull/104 (now **ready for review**)
- Branch: `fix/t03-stale-cleanup-observability` (local + origin in sync at `62765e81`)
- This session's commits (now pushed):
  - `31ac66e8` — fix(containment): ignore FileNotFoundError races in per-file sweep loop
  - `62765e81` — fix(containment-smoke-setup): preserve exc class in fail-FAST log
- Prior session's commits (also now pushed via this session's push):
  - `82d8cada` — fix(containment-lifecycle): preserve exc class in fail-OPEN log; document policy
  - `3568becd` — test(shakedown): cover CLI wrapper silent-on-clean and fail-FAST contracts

**Handoffs:**
- Prior handoff: `docs/handoffs/archive/2026-04-11_21-24_pr-104-review-option-b-commits-pending-push.md`
- This handoff: `docs/handoffs/2026-04-11_21-53_pr-104-race-fix-smoke-setup-parity-marked-ready.md`

**Plan and tickets:**
- Implementation plan: `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md`
- Ticket: `docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md` (status: deferred → will become done at merge)

**Skill resources consulted:**
- `packages/plugins/handoff/skills/save/synthesis-guide.md`
- `packages/plugins/handoff/references/format-reference.md`
- `packages/plugins/handoff/references/handoff-contract.md`
- `packages/plugins/handoff/skills/load/SKILL.md` (load skill, used at session start)

**Project standards:**
- `~/.claude/CLAUDE.md` — global rules (no `rm`, scope control, shared-state approval, root-cause analysis)
- `.claude/CLAUDE.md` — project rules (ruff authoritative, error format convention, tenets, frameworks)
- `.claude/rules/methodology/tenets.md` — design philosophy (Explicit over Silent, Deterministic over Heuristic)
- `.claude/rules/workflow/git.md` — branch protection policy (allowed `fix/*` branch this session)

## Gotchas

### `gh pr view` returns stale `headRefOid` immediately after `git push`

**Symptom:** After a successful `git push origin <branch>` followed immediately by `gh pr view <num> --json headRefOid`, the returned `headRefOid` may be the **pre-push** HEAD, not the just-pushed HEAD. The `gh pr ready` and other commands also work but the read-back is stale.

**Root cause:** GitHub's API representation of a PR is cached/denormalized at the HTTP layer. After a push event, the underlying branch ref is updated immediately (visible via `git ls-remote origin <branch>`), but the PR's `headRefOid` field — which is associated through a denormalized join — takes a few seconds to invalidate and re-populate.

**Mitigation:** Always re-query after seeing a stale `headRefOid`. The lag is typically <5 seconds. Alternatively:
- Compare against `git ls-remote origin <branch>` (authoritative branch ref state)
- Include `commits[-1].oid` in the query — it tends to converge slightly faster than the top-level `headRefOid` field
- Trust the local `git push` output as the authoritative source of "did the push land"

**Discovered when:** This session's chained `git push && gh pr ready 104 && gh pr view ...` returned the old `headRefOid` despite successful push and ready. Re-query ~3 seconds later showed the converged state.

### `monkeypatch.setattr(Path, "stat", wrapper)` rebinds the descriptor at class level; the wrapper gets `self` automatically

**Symptom:** A test that wraps `Path.stat` via `monkeypatch.setattr(Path, "stat", stat_then_remove)` works without explicit binding — the wrapper function with signature `def stat_then_remove(self: Path, *args, **kwargs):` receives `self` correctly when called as `path.stat()` in production code.

**Root cause:** `pathlib.Path.stat` is defined as a regular method (not a property or staticmethod). `monkeypatch.setattr(Path, "stat", ...)` replaces the method at the class level, and Python's descriptor protocol re-binds it on attribute lookup, so `path.stat()` calls `stat_then_remove(path, ...)` automatically.

**Mitigation:** Just use the natural `def func(self, *args, **kwargs):` signature. Don't try to manually bind or wrap with `functools.partial`.

**Discovered when:** Reading the user's race-fix Test 2 (`test_clean_stale_files_ignores_candidates_removed_before_unlink`) — the test uses exactly this pattern and works correctly with the natural signature.

### `FileNotFoundError` MUST come before `OSError` in `except` chains (load-bearing in this codebase)

**Symptom:** If you catch `OSError` first and `FileNotFoundError` second, the FileNotFoundError clause is unreachable — the more general handler eats the more specific case. In this codebase, that would route concurrent-deletion races into `failed_stat`/`failed_unlink`, exactly the bug commit `31ac66e8` fixes.

**Root cause:** Python's `try/except` matches clauses top-down using `isinstance`-style subclass matching. `FileNotFoundError` is a subclass of `OSError`, so `except OSError` catches both.

**Mitigation:** Always put the more specific subclass first. This applies to:
- `FileNotFoundError` before `OSError`
- `PermissionError` before `OSError`
- `IsADirectoryError` before `OSError`
- `KeyError` before `LookupError`
- `UnicodeDecodeError` before `ValueError`

**Discovered when:** Reading the user's race-fix at `containment.py:468-471, 481-484`. The ordering is the load-bearing detail of the fix.

### Substring assertions on error formats are robust to format polishes

**Symptom:** Tests that assert `"prefix" in stderr` (substring) survive format changes that preserve the prefix. Tests that assert `stderr == "exact format"` (exact match) break on every format change.

**Root cause:** Prefix preservation is the load-bearing contract (caller routing); the surrounding format is a polish surface. Substring matching tests the contract; exact matching tests the format.

**Mitigation:** Prefer substring assertions for error message tests. Reserve exact match for cases where the exact string IS the contract (e.g., parser-facing JSON output, machine-readable status codes).

**Discovered when:** This session's smoke_setup parity fix (commit `62765e81`) changed the format from `{exc}` to `unexpected error. Got: {exc!r:.100}`. All 3 existing smoke_setup tests passed without modification because they used substring assertions on the prefix and the wrapped exception's content.

### `:.100` truncation arithmetic for substring assertions

**Symptom:** When using `{exc!r:.100}` to bound log volume, you must verify that any substring assertion on the exception's content lands within the first 100 characters of the repr.

**Root cause:** `repr(OSError("..."))` produces `OSError("...")` — adding ~10 characters of overhead. The `:.100` slice cuts at character 100, potentially cutting through important content.

**Mitigation:** Calculate the substring's position in the repr. For `OSError("clean_stale_files failed: cannot enumerate shakedown root. Got: ...")`:
- `OSError("` = 9 chars
- `clean_stale_files failed: ` = 26 chars (running total: 35)
- `cannot enumerate shakedown root` = 31 chars (running total: 66)
- This substring lands at chars 35-66, well within the 100-char cap. ✓

**Discovered when:** Verifying that this session's smoke_setup format change wouldn't break existing substring assertions. Did the calculation manually before editing.

### When the user brings a diff, "Nothing I'd change" is a valid response

**Symptom:** A new pattern observed this session: the user provides a complete diff (production + tests + rationale) before invoking Claude. The natural Claude impulse is to propose alternatives, additional tests, or "improvements". This is the wrong impulse for this mode.

**Root cause:** The user's bring-the-diff pattern is a **review request**, not a **design request**. Proposing changes is appropriate when the user asks "how should I do X?" — not when they say "here is what I did, please verify and commit it."

**Mitigation:** When the user provides a diff with rationale and you've verified empirically that it's correct, the right response is:
1. State that verification passed (with concrete evidence)
2. Note any specific things that look right (exception ordering, test design, etc.)
3. Move directly to commit strategy
4. Do NOT propose alternative implementations, additional tests, or refactors unless verification surfaced a real defect

**Discovered when:** The race-fix opening exchange. The user's structured "What Changed / Why It Changed" message made the review-mode framing explicit; recognizing it early let me skip the propose-alternatives step entirely.
