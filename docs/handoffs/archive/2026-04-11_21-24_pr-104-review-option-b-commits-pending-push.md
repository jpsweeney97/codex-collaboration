---
date: 2026-04-11
time: "21:24"
created_at: "2026-04-12T01:24:48Z"
session_id: 44b0a9d1-8e2a-476d-8162-f8d45acb3645
project: claude-code-tool-dev
branch: fix/t03-stale-cleanup-observability
commit: 3568becd
title: PR #104 reviewed via 5 specialized agents; Option B polish + missing tests landed locally
type: handoff
resumed_from: docs/handoffs/archive/2026-04-11_17-00_t03-execution-complete-pr-104.md
files:
  - packages/plugins/codex-collaboration/scripts/containment_lifecycle.py
  - packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py
  - packages/plugins/codex-collaboration/tests/test_containment_lifecycle.py
  - packages/plugins/codex-collaboration/tests/test_containment_smoke_setup.py
  - packages/plugins/codex-collaboration/tests/test_clean_stale_shakedown.py
  - docs/handoffs/archive/2026-04-11_17-00_t03-execution-complete-pr-104.md
---

# PR #104 Reviewed via 5 Specialized Agents; Option B Polish + Missing Tests Landed Locally

## Goal

Review draft PR #104 ("[codex] Harden stale cleanup observability and failure reporting") via the `pr-review-toolkit` plugin's multi-agent review flow, aggregate findings, present an action plan, then implement whichever option the user chose. The session's "done" bar was **code committed locally, verified via ruff + full pytest suite, awaiting user inspection before push**.

**Trigger:** The prior session (2026-04-11_17-00) closed with draft PR #104 created and the subagent-driven-development skill's `finishing-a-development-branch` handoff deferred pending user approval for shared-state actions. The user's explicit next-session goal was "Review the draft PR at https://github.com/jpsweeney97/claude-code-tool-dev/pull/104". This session executed that review and went one step further — actually implementing the findings into local commits.

**Stakes:** The PR is the culmination of 8 sequential implementation commits through the T-03 observability work, built on top of 7 rounds of adversarial plan review. A clean pre-mark-ready state (robust, consistent, well-tested) minimizes churn when human reviewers get involved. The user explicitly said (verbatim): "The branch is still in **draft PR** state, so this is the right moment to add the small test file before inviting human review. After the PR is ready, adding a new caller test file is more churn for less benefit."

**Success criteria (all met):**
- 5 specialized reviewers dispatched in parallel with explicit scope boundaries
- Findings aggregated into a structured action plan (Critical / Important / Suggestions / Strengths)
- User picks an option; session implements it end-to-end
- All edits verified with `uv run ruff check` + `uv run pytest`
- Test count ≥ 538 baseline
- Commits created with descriptive conventional messages
- Session handoff captures the full decision chain so next-session user feedback can be integrated cleanly

**Connection to project arc:** T-03 is part of the codex-collaboration plugin's containment hardening initiative. This PR (draft) plus the two pending local commits completes the observability work. Downstream: (1) user inspection, (2) push to origin, (3) mark PR ready with `gh pr ready 104`, (4) CI run, (5) human review, (6) merge. The ticket `T-20260410-03` will transition from `deferred` to `done` at merge time.

## Session Narrative

Session opened by loading the prior handoff (`2026-04-11_17-00_t03-execution-complete-pr-104.md`) via the `/handoff:load` skill. The prior handoff was dense and comprehensive (~580 lines of body content) and described in detail the 9-task execution, the 3 session pivots (Task 1 reviewer false positives → pre-load fix, Pyright stale diagnostics, Task 8 Python 3.14 dataclass fix), and 6 reasoned decisions with rejection rationale. The load archived the handoff and created a state file at `.session-state/handoff-44b0a9d1-8e2a-476d-8162-f8d45acb3645` so this handoff's `resumed_from` field would be populated automatically.

I presented a summary of where we left off and offered 4 options for the next action: **(a)** fetch and walk through PR #104, **(b)** run the Task 7 manual probes locally, **(c)** read `finishing-a-development-branch` to answer the open question about auto-mark-ready, **(d)** something else.

The user invoked `/pr-review-toolkit:review-pr` with the argument `Let's review PR #104.`, triggering the comprehensive multi-agent PR review flow.

**Phase 1 — Review scope determination (~3 min):**
I fetched PR metadata via `gh pr view 104 --json` and `gh pr diff 104 --name-only`, plus `git log --oneline origin/main..fix/t03-stale-cleanup-observability` to confirm the branch state matched the handoff. Key facts:
- Draft, 8 commits, **3505 additions / 24 deletions** across 8 files
- Production code (`server/containment.py` + 3 scripts): ~228 additions
- Test additions across 3 files: ~996 additions (1 new file)
- Plan doc (`docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md`): 2281 additions (documentation, not code — would be noise to reviewers)

I made an early decision to **exclude the plan doc from every reviewer's scope** and to include **explicit notes about deliberate design choices** (fail-OPEN lifecycle policy, Round 5 Choice 3B silent-on-clean-runs, Round 6 `_run_with_wrapper` testability refactor) in each dispatch prompt. This was a direct application of the prior session's "spec-verbatim pre-load" learning — telling reviewers what's intentional up front prevents false-positive churn on spec-prescribed patterns. I also decided NOT to brief reviewers about the prior session's specific Task 1 false positives; a fresh review should be genuinely fresh, and aggregation would dedupe if necessary.

**Phase 2 — 5 parallel agent dispatches (~5 min wall, ~90 min subagent time):**
I dispatched 5 agents simultaneously via single-message multiple Agent tool calls with `run_in_background=true`:
1. **`pr-review-toolkit:code-reviewer`** — general quality, CLAUDE.md compliance
2. **`pr-review-toolkit:pr-test-analyzer`** — test coverage gaps and quality
3. **`pr-review-toolkit:silent-failure-hunter`** — silent failures (the PR is literally about this)
4. **`pr-review-toolkit:type-design-analyzer`** — `CleanStaleResult` encapsulation and invariants
5. **`pr-review-toolkit:comment-analyzer`** — comment accuracy and rationale coverage

I deliberately skipped `code-simplifier` because the command template says "After passing review" — it's a polish pass, not a find-issues pass.

Each agent received:
- Full file list (7 files, excluding plan doc)
- Specific focus lens with examples
- Explicit deliberate-design notes (fail-OPEN, silent-on-clean, Round 6 refactor)
- Ruff as authoritative quality gate
- "Do not re-litigate plan-prescribed decisions"
- Report format (Critical / Important / Suggestions / Strengths with file:line refs)

Agents streamed back completion notifications over ~8 minutes wall time. The code-reviewer completed first and reported "Ready to merge" with zero critical/important findings — a potentially worrying signal if taken alone, since it might mean the reviewer was superficial. But the pr-test-analyzer and silent-failure-hunter came back next with substantive findings, confirming that the code-reviewer had legitimately found nothing new (the specialists were carrying different lenses, not catching code-reviewer misses per se).

**Phase 3 — Findings aggregation (~5 min):**
After all 5 agents completed, I aggregated findings into the structured command-template format:

- **Critical (0 found).** No correctness bugs, no silent failures, no security issues.
- **Important (4 found):**
  - **I-1**: Missing inline comment explaining fail-OPEN policy at `containment_lifecycle.py:186-190` (flagged by comment-analyzer C2 and silent-failure-hunter independently)
  - **I-2**: `{exc}` vs `{exc!r:.100}` in lifecycle fail-OPEN log — drops exception class (flagged by silent-failure-hunter Suspicious #2)
  - **I-3**: `scripts/clean_stale_shakedown.py` has **zero tests** — most material coverage gap; silent-on-clean-run Choice 3B has no regression guard (flagged by pr-test-analyzer at criticality 9)
  - **I-4**: Stale line-number refs in test docstrings (flagged by comment-analyzer C1)
- **Suggestions (7 found)** — ranging from `NamedTuple FileFailure` refactor to `skipped_non_regular` observability bucket to Python 3.14 version note reframing.
- **Strengths** — 3-stage failure check, `CleanStaleResult` immutability, per-line prefix regression guard, dual in-process + subprocess tests, SystemExit propagation correctness, etc.

I presented **4 action options** (A: minimum polish, B: polish + missing test file, C: defer all and mark ready, D: polish + mark ready) with my own recommendation of **Option A** as the "sweet spot" because I-1 is a maintainability landmine and I-2 + I-4 are trivial. I noted that I-3 (missing test file) was real but could be a follow-up PR since Round 5 Choice 3B is at least pinned in the plan doc.

**Phase 4 — User counter-recommendation and alignment on Option B (~2 min):**
The user pushed back on my Option A recommendation with a clear, reasoned argument:

> "I recommend (b) Option B. I-3 is the only remaining finding that materially affects confidence, not just maintainability. clean_stale_shakedown.py is still untested, and it is the most user-facing caller boundary in the PR. The wrapper is small and cheap to lock down. I-1, I-2, and I-4 are real, but they are polish-class compared with I-3. The branch is still in draft PR state, so this is the right moment to add the small test file before inviting human review."

And explicitly:

> "Option A only if you want minimum churn and are deliberately optimizing for speed (which we aren't, we are aiming for robustness)"

This was a **correction**, not just a preference. My Option A recommendation had traded confidence for churn-minimization in a context where the user wanted robustness. The correction changed the decision from "fix 3 things" to "fix 3 things + write 6 new tests" — roughly 3x the work. I aligned immediately and committed to Option B.

**Phase 5 — Scope clarification on `containment_smoke_setup.py:525` (~2 min):**
While reading `containment_lifecycle.py` to execute I-2, I noticed that `containment_smoke_setup.py:525` (inside `_run_with_wrapper`) has the **exact same `{exc}` pattern** as the lifecycle defect:
```python
print(f"containment_smoke_setup failed: {exc}", file=sys.stderr)
```
The silent-failure-hunter had claimed "every other error site uses `{exc!r:.100}`" — but this claim was factually wrong; smoke_setup also uses `{exc}`. This was a meaningful discovery because:
1. If I fix only lifecycle (per the reviewer's explicit flag), smoke_setup stays inconsistent
2. If I fix both, I'm exceeding the reviewer's scope

I surfaced this to the user proactively, flagged my scope-control reasoning ("fix what's explicitly flagged; mention what's adjacent"), and explicitly decided NOT to touch smoke_setup in this session. The decision followed the user's global CLAUDE.md: **"Solve the task that was asked for. Do not expand scope without a concrete reason... If you notice unrelated issues, mention them briefly instead of silently fixing them."**

This was a judgment call I'm uncertain about. If the user reviews the commits and says "go ahead and fix smoke_setup too", the fix is a 5-character Edit. I flagged it in my final summary so the decision is theirs.

**Phase 6 — Task tracking and execution (~20 min):**
I loaded `TaskCreate`/`TaskUpdate` via `ToolSearch` and created **8 tasks** for the work: edit containment_lifecycle.py (I-1+I-2), update test_containment_lifecycle.py docstrings (I-4), update test_containment_smoke_setup.py docstring (I-4), verify polish edits, commit polish, create test_clean_stale_shakedown.py, verify new test file, commit new test file. Marked each in_progress when starting and completed when done.

Execution order:
1. **Polish commit (`82d8cada`)**: 3 files, +18/-8 lines
   - Added a 7-line fail-OPEN policy comment above `containment_lifecycle.py:188`'s `except Exception`, cross-referencing both pinning tests by name
   - Changed `_log_error(f"containment-lifecycle: internal error ({exc})")` to `_log_error(f"containment-lifecycle: internal error. Got: {exc!r:.100}")` — now preserves the exception class in the repr
   - Updated 2 stale docstrings in `test_containment_lifecycle.py` (lines 381-382 and 464) and 1 in `test_containment_smoke_setup.py` (line 212) — all swapped numeric line refs for symbol names (`main()`'s outer except Exception block, `_run_with_wrapper()`, etc.)
   - Also updated the docstring `<exc>` format descriptions to match the new `<repr(exc)>` format
   - Verified: `uv run ruff check` clean on all 3 files, `uv run pytest tests/test_containment_lifecycle.py tests/test_containment_smoke_setup.py` → **15 passed in 0.50s**
   - Committed with conventional message `fix(containment-lifecycle): preserve exc class in fail-OPEN log; document policy` + body describing I-1/I-2/I-4

2. **New test file commit (`3568becd`)**: 1 new file, +387 lines, 6 tests
   - Created `tests/test_clean_stale_shakedown.py` following the patterns of `test_containment_lifecycle.py` (loader, subprocess runner, in-process tests, subprocess chmod tests)
   - **6 tests total:**
     - `test_clean_stale_shakedown_is_silent_on_clean_run` — Round 5 Choice 3B regression guard (in-process main() call on empty shakedown dir, assert empty stderr)
     - `test_clean_stale_shakedown_emits_report_on_had_errors` — monkeypatches `containment.clean_stale_files` to return `CleanStaleResult(failed_unlink=(...))`, calls main() in-process, asserts stderr contains report with `failed_unlink=1` + path + error repr
     - `test_clean_stale_shakedown_exits_1_when_env_var_missing` — monkeypatch.delenv + in-process main() → exit 1 + canonical prefix
     - `test_clean_stale_shakedown_exits_1_when_env_var_is_regular_file` — env var points at a file → exit 1 + canonical "is not a directory" message
     - `test_clean_stale_shakedown_subprocess_fails_fast_on_unreadable_shakedown` — subprocess end-to-end with real `chmod 0o000` on shakedown dir, skipif root/Windows, `finally: chmod 0o755`, asserts exit 1 + "unexpected error" + "cannot enumerate shakedown root" (matches lifecycle subprocess chmod test pattern)
     - `test_clean_stale_shakedown_wrapper_converts_exception_to_exit_1_via_runpy` — platform-agnostic in-process fallback using `runpy.run_path(SCRIPT, run_name="__main__")` with monkeypatched `os.listdir`; asserts `SystemExit.code == 1` via `pytest.raises`
   - Verified: `uv run ruff check` clean, `uv run pytest tests/test_clean_stale_shakedown.py -v` → **6 passed in 0.07s**, full suite → **544 passed in 3.96s** (538 baseline + 6 new)
   - Pyright fired false positive on `_shakedown_path` "not accessed" (the stub parameter is intentionally unused); renamed from `shakedown_path` → `_shakedown_path` for underscore convention, Pyright STILL complained (ruff respects the convention, Pyright didn't in this context) — confirmed ruff is authoritative per project policy, ignored
   - Committed with conventional message `test(shakedown): cover CLI wrapper silent-on-clean and fail-FAST contracts` + 20-line body

**Phase 7 — Final verification and handoff prep:**
Showed `git log --oneline origin/fix/t03-stale-cleanup-observability..HEAD` to confirm the branch is **2 commits ahead of remote** (both commits local-only). Presented the final summary with:
- What was done per finding ID
- Verification results (ruff clean, 544 pass)
- The `containment_smoke_setup.py:525` inconsistency I deliberately did NOT fix (scope control)
- 4 next-action options (push, push+fix smoke_setup, hold, push+mark-ready)

User responded with `/handoff:save` instruction: "Save a handoff. I will inspect this work and share my feedback with you in the next session". This is an **approval-gated checkpoint** — the user wants to review the commits themselves (via git diff, code reading, etc.) before any push or mark-ready transition. The next session will start from user feedback on these two commits.

## Decisions

### Decision 1: Dispatch 5 specialized review agents in parallel vs sequential/single-reviewer

**Choice:** Single-message multiple Agent tool calls with `run_in_background=true` for all 5 agents (code-reviewer, pr-test-analyzer, silent-failure-hunter, type-design-analyzer, comment-analyzer).

**Driver:** The user's prompt was broad ("Let's review PR #104"), the command template's default is "all applicable reviews", and the PR touches 7 files spanning production code, tests, types, and comments — no single specialist fully covers the surface. The command template explicitly lists parallel as a valid mode.

**Alternatives considered:**
- **(a) Sequential reviews** — dispatch one agent, read report, aggregate, dispatch next. Simpler to aggregate incrementally.
- **(b) Single general reviewer** — just code-reviewer. Lowest token cost.
- **(c) User-selected subset** — ask the user which lenses they want first.
- **(d) Parallel all 5** (chosen)

**Rejection reasons:**
- (a) Sequential: slower wall-clock; aggregation at the end is the same complexity; also loses the "independent lenses" property (later reviewers might be primed by earlier findings if I shared context)
- (b) Single reviewer: code-reviewer came back with zero findings — would have been a falsely reassuring "ready to merge" signal. The specialists found 4 important + 7 suggestions that a general review missed.
- (c) User subset: over-consults for a broad request; the user said "Let's review PR #104" not "which lenses should I use?"

**Trade-offs:** Parallel means 5 reports arrive over ~8 minutes with different completion times, requiring an aggregation step at the end. Higher token budget than single-reviewer. Risk of context-window pressure (mitigated by `run_in_background` which keeps transcripts out of the main context and returns only the final result).

**Confidence:** High (E2) — verified by results. code-reviewer found zero issues; silent-failure-hunter and pr-test-analyzer each found distinct critical/important findings that code-reviewer missed. Specialization paid off empirically.

**Reversibility:** N/A — reviews are informational, not state-changing.

**Change triggers:** If the main conversation context were already tight (not the case — at 81k/1M tokens when dispatched), I'd consider sequential with summarization between dispatches. If the PR were trivial (single-file, <100 lines), a single reviewer would suffice.

### Decision 2: Do NOT brief reviewers about the prior session's Task 1 false positives

**Choice:** Fresh review with no knowledge of the earlier session's specific decision to skip 3 code-quality reviewer "Important" findings that were all spec-prescribed patterns.

**Driver:** A fresh review should be genuinely fresh. If fresh reviewers re-surface the same patterns, aggregation can dedupe and compare against the authoritative quality gate (ruff). Briefing reviewers on prior decisions risks (a) biasing them toward confirming the earlier call, (b) priming them to miss the REAL issues (like the `{exc}` vs `{exc!r:.100}` defect that the prior session did NOT catch).

**Alternatives considered:**
- **(a) Brief reviewers with the full context of prior Task 1 decisions** — would make the review more aligned with prior session's judgment
- **(b) Selectively brief on some decisions** — arbitrary choice of which to include
- **(c) No prior-session context at all** (chosen)

**Rejection reasons:**
- (a) Biases reviewers, risks missing real defects they might catch without prior framing
- (b) No principled rule for which context to include

**Trade-offs:** Small risk fresh reviewers re-surface known false positives (e.g., the `str(path)!r` pattern that was flagged in Task 1). Mitigated by the aggregation step + the authoritative ruff gate. In practice, NO fresh reviewer re-surfaced any of the 3 prior false positives — they found NEW, real issues instead.

**Implication:** The silent-failure-hunter caught I-2 (lifecycle `{exc}` → `{exc!r:.100}`) which the prior session's code-quality reviewer did not. Freshness paid off.

**Confidence:** Very high (E2) — validated by results. Not a single prior false positive was re-surfaced, and NEW real findings were captured.

**Reversibility:** Trivial — future reviews can include or exclude prior context as needed.

**Change triggers:** If a specific prior decision was load-bearing for correctness (e.g., a workaround for a bug) and the fresh reviewer might undo it unknowingly.

### Decision 3: Exclude the 2281-line plan doc from every reviewer's scope

**Choice:** Explicit "SKIP `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` — it's documentation, not code" in every dispatch prompt.

**Driver:** The plan doc dominates the PR's line count (2281 of 3505 additions = 65%) but contributes zero executable code. Reviewers parsing plan prose would waste cycles and might flag stylistic concerns in narrative English as if they were code issues.

**Alternatives considered:**
- **(a) Include the plan doc** — reviewers could check it for outdated information after execution
- **(b) Exclude** (chosen)

**Rejection reasons:** Plan docs are already reviewed in the 7 rounds of adversarial plan review. Re-reviewing prose via code-review lenses is a category error.

**Trade-offs:** If the plan doc contains post-execution inaccuracies (e.g., the Python 3.14 dataclass workaround is not mentioned), this review wouldn't catch them. Known residual risk from prior handoff ("Risks" section, item 4).

**Confidence:** High (E2) — reviewers respected the exclusion; no false-positive flags on the plan doc.

**Reversibility:** Trivial — future reviews can include or exclude as needed.

### Decision 4: Choose Option B (polish + missing test file) over Option A (minimum polish)

**Choice:** Implement all 3 Important findings I had colocated (I-1+I-2+I-4 in one commit) AND create the missing `test_clean_stale_shakedown.py` test file (6 new tests, ~387 lines) in a separate commit.

**Driver:** The user pushed back on my Option A recommendation with a reasoned counter-argument. Verbatim quotes:
> "I-3 is the only remaining finding that materially affects confidence, not just maintainability. clean_stale_shakedown.py is still untested, and it is the most user-facing caller boundary in the PR."
> "The wrapper is small and cheap to lock down."
> "Option A only if you want minimum churn and are deliberately optimizing for speed (which we aren't, we are aiming for robustness)"

**Alternatives considered:**
- **(a) Option A (minimum polish)** — my original recommendation. Fix I-1+I-2+I-4, skip I-3. 15-minute work.
- **(b) Option B (chosen)** — polish + missing test file. ~45-minute work.
- **(c) Option C (defer all)** — mark ready as-is, fix on human reviewer feedback. Minimum churn.
- **(d) Option D (polish + mark ready)** — same as A then mark ready now.

**Rejection reasons:**
- (a) Misreads the user's priorities. The user values robustness over speed in this context. My recommendation traded confidence for churn-minimization — wrong optimization target.
- (c) Leaves Round 5 Choice 3B (silent-on-clean-runs) pinned only in the plan doc and code-review memory — vulnerable to a future refactor silently reversing the gate.
- (d) Mark-ready is a shared-state action requiring user approval; can't auto-bundle with polish.

**Trade-offs:** 
- Option B requires writing 6 new tests (~387 lines) and is ~3x the work of Option A
- The runpy.run_path fallback test adds a new stdlib dependency to the test suite (runpy is core, but the pattern is new for this project)
- Longer commit chain (2 commits instead of 1)

**Implication:** Branch now has commits `82d8cada` and `3568becd` local-only, representing the strongest pre-review state. Round 5 Choice 3B is now protected by an automated regression test. clean_stale_shakedown.py coverage went from 0 tests → 6 tests.

**Confidence:** High (E3) — user's reasoning is sound (coverage gap > polish), verified by empirical test pass (6/6 new tests on first run), and aligned with the global CLAUDE.md "fail fast + explicit over silent" tenets.

**Reversibility:** High — could amend the commits, drop tests, or switch back to Option A. No external state changed yet (nothing pushed).

**Change trigger:** If time pressure emerged mid-execution, could have committed just the polish and deferred tests. Not applicable here.

### Decision 5: Do NOT fix `containment_smoke_setup.py:525` in this session

**Choice:** Leave `print(f"containment_smoke_setup failed: {exc}", file=sys.stderr)` at line 525 of `scripts/containment_smoke_setup.py` unchanged, despite it having the **identical** `{exc}` vs `{exc!r:.100}` pattern as I-2.

**Driver:** Scope control per user's global CLAUDE.md:
> "Solve the task that was asked for. Do not expand scope without a concrete reason tied to correctness, safety, or clear adjacent breakage."
> "If you notice unrelated issues, mention them briefly instead of silently fixing them unless they block the requested work."

The silent-failure-hunter agent explicitly flagged `containment_lifecycle.py:188` only. It did NOT flag `containment_smoke_setup.py:525`, even though the pattern is identical. The agent's claim that "every other error site uses `{exc!r:.100}`" was actually factually wrong — it missed the smoke_setup instance. But the user asked for Option B, which was I-1+I-2+I-3+I-4. Fixing smoke_setup:525 is I-2' (a new finding surfaced during implementation), not what was approved.

**Alternatives considered:**
- **(a) Fix both lifecycle and smoke_setup for consistency** — exceeds reviewer scope + user's Option B; minor adjacent fix
- **(b) Fix only lifecycle (reviewer's explicit flag)** (chosen) — stays within scope; flags the inconsistency for user decision
- **(c) Skip both** — would ignore a real issue the reviewer did flag

**Rejection reasons:**
- (a) Violates scope control; the user's global rule is specific about "do not expand scope"
- (c) Ignores a legitimate reviewer finding

**Trade-offs:** The PR now has an INTERNAL inconsistency — `containment_lifecycle.py:188` uses `{exc!r:.100}` while `containment_smoke_setup.py:525` still uses `{exc}`. A future code reviewer will likely catch this. The fix is trivial (5-character edit). I surfaced this explicitly in my final summary so the user can decide whether to:
1. Have me fix it next session as a 3rd local commit before push
2. Leave it and fix on human review feedback
3. Skip it entirely (accept the minor inconsistency)

**Confidence:** Medium (E1) — the scope-control rule is clear, but this is an edge case where the rule's letter (don't fix unflagged issues) slightly conflicts with its spirit (maintain consistency). I'm moderately confident in following the letter here because the user's explicit Option B scope was clear and the inconsistency is surfaced transparently.

**Reversibility:** Trivial — 5-character Edit + re-run ruff + amend/new-commit.

**Change trigger:** If the user says "yes, fix smoke_setup too" OR if they want to optimize for PR-wide consistency over commit-boundary discipline.

### Decision 6: Use `runpy.run_path` for the in-process `__main__` wrapper fallback test

**Choice:** Test the `__main__` wrapper of `clean_stale_shakedown.py` in-process via `runpy.run_path(SCRIPT, run_name="__main__")`, rather than refactoring the production code to extract a `_run_with_wrapper()` function like `containment_smoke_setup.py` did in Round 6.

**Driver:** The fallback test is needed so root/Windows CI runs still have automated coverage of the `exception → SystemExit(1)` conversion when the subprocess chmod test skips. But `clean_stale_shakedown.py` has its wrapper inlined at the `if __name__ == "__main__":` block (no extracted function to call directly). So I had three options.

**Alternatives considered:**
- **(a) Refactor `clean_stale_shakedown.py` to extract a `_run_with_wrapper()`** — mirrors smoke_setup's Round 6 pattern exactly, cleanest testing surface
- **(b) Subprocess-only coverage** — accept weaker coverage on root/Windows
- **(c) `runpy.run_path(..., run_name="__main__")`** (chosen) — stdlib-blessed in-process script execution

**Rejection reasons:**
- (a) **Scope creep** — user asked for "add missing tests", not "refactor production + add tests". The Round 6 refactor was a targeted 15-line change to smoke_setup justified by spec-prescribed testability. clean_stale_shakedown.py's wrapper works fine as-is; there's no need to add a function just to make it testable in one specific way.
- (b) Leaves root/Windows CI with weaker coverage than lifecycle and smoke_setup callers, which DO have in-process fallbacks. Would create an asymmetric coverage story.

**Trade-offs:** 
- `runpy.run_path` is slightly more complex than a direct function call — requires `run_name="__main__"` parameter and `pytest.raises(SystemExit)` wrapping
- Test brittleness: if the `__main__` block's structure changes, the test might need updating. But a direct function call has the same property in a different way.
- New stdlib dependency pattern for this project (first use of `runpy` in the test suite). Documented with a long docstring explaining why.

**Implication:** clean_stale_shakedown.py now has the same in-process + subprocess coverage parity as lifecycle and smoke_setup callers. Production code is unchanged. Tests pass on every platform (6/6).

**Confidence:** High (E2) — verified empirically with 6/6 tests passing including the runpy fallback on macOS. The `runpy.run_path` semantics (executes file with `__name__ == "__main__"`, propagates SystemExit) are stdlib-documented and stable.

**Reversibility:** Easy — could later extract `_run_with_wrapper()` in production and swap the test to direct call.

**Change trigger:** If a future production change creates a compelling independent reason to extract `_run_with_wrapper()` (e.g., adding custom signal handling, or needing the wrapper callable from tests of OTHER behaviors).

### Decision 7: Follow lifecycle loader pattern (no sys.modules registration) for `_load_shakedown_module`

**Choice:** `_load_shakedown_module()` in the new test file does NOT register the module in `sys.modules` before calling `exec_module` — matching `_load_lifecycle_module`'s pattern, not `_load_smoke_setup_module`'s pattern.

**Driver:** The Python 3.14 `sys.modules` registration workaround exists specifically because `containment_smoke_setup.py` contains a dataclass definition with `from __future__ import annotations` — Python 3.14's annotation resolver calls `sys.modules[cls.__module__].__dict__` to resolve string-form annotations, and the synthetic module name created by `spec_from_file_location` is absent from `sys.modules` by default. The workaround only triggers when the LOADED MODULE itself contains a dataclass definition. `clean_stale_shakedown.py` has NO dataclass definition (it only imports `clean_stale_files` from `server.containment`, which is already fully resolved in `sys.modules`). Therefore the registration is not needed.

**Alternatives considered:**
- **(a) Defensive registration** — add the sys.modules dance anyway for future-proofing if someone adds a dataclass to clean_stale_shakedown.py later
- **(b) Match lifecycle's minimal pattern** (chosen) — only add the workaround where it's actually needed

**Rejection reasons:**
- (a) Would create 3 different loader patterns in the test suite (none, register+cleanup, and a hypothetical hybrid) — the final holistic reviewer in the prior session already called out the asymmetry between lifecycle and smoke_setup loaders as a hygiene issue. Adding a third pattern would compound the problem.

**Trade-offs:** If someone adds a dataclass to `clean_stale_shakedown.py` in the future, they'll need to add the sys.modules registration at that time. The `_load_smoke_setup_module` helper has a detailed inline comment explaining the Python 3.14 workaround that can serve as a reference.

**Implication:** Test suite now has 3 loader patterns: `_load_lifecycle_module` (minimal, 5 lines), `_load_shakedown_module` (minimal, 5 lines + docstring pointer to the workaround explanation), `_load_smoke_setup_module` (with registration + cleanup, 12 lines). Each is correct for its target module.

**Confidence:** Very high (E3) — validated by (1) 6/6 new tests passing, (2) prior-session holistic reviewer's analysis of the same issue in lifecycle, (3) direct verification that clean_stale_shakedown.py has no dataclass.

**Reversibility:** Trivial — add 3 lines if needed.

**Change trigger:** Adding a dataclass definition to `clean_stale_shakedown.py`.

### Decision 8: Separate the polish and test commits (not bundled)

**Choice:** Two distinct commits (`82d8cada` polish, `3568becd` tests) rather than one combined commit.

**Driver:** Different types of changes warrant different commit types per conventional commit style — `fix()` for the polish (bug-class fix + documentation) and `test()` for the new test file. Matches the prior session's commit style (8 commits, each a single task).

**Alternatives considered:**
- **(a) Single combined commit** — smaller commit count, single atomic change
- **(b) Two commits** (chosen) — cleaner git history, easier to revert either independently
- **(c) More granular** (e.g., 4 commits: I-1, I-2, I-4, I-3) — too fragmented

**Rejection reasons:**
- (a) Mixes `fix()` and `test()` concerns; harder to revert just the test file or just the polish; bisect-unfriendly
- (c) I-1+I-2+I-4 are all touching the same 3 files and could each be trivially reverted; fragmenting into 3 polish commits adds git noise without benefit

**Trade-offs:** Two commit messages to write vs one. Minor overhead.

**Implication:** Branch now has 10 commits ahead of main (8 pre-session + 2 this-session), with clean commit-type separation.

**Confidence:** High (E2) — matches existing branch style; verified by `git log` showing good structure.

**Reversibility:** Could squash later if desired.

**Change trigger:** If the reviewer prefers a single commit, could squash before push.

### Decision 9: Ask user before pushing (shared-state action)

**Choice:** Do NOT `git push origin fix/t03-stale-cleanup-observability` automatically. Present 4 options (push, push+fix smoke_setup, hold, push+mark-ready) and wait for user direction.

**Driver:** User's global CLAUDE.md:
> "Actions visible to others or that affect shared state: pushing code, creating/closing/commenting on PRs or issues, sending messages... Uploading content to third-party web tools..."
> "User approving an action (like a git push) once does NOT mean that they approve it in all contexts, so unless actions are authorized in advance in durable instructions like CLAUDE.md files, always confirm first."

Pushing updates the draft PR view on GitHub, which is visible to anyone with repo access. Even though the PR is draft and reviewers haven't been notified, the state change is irreversible (can't unpush without force-push, which is further shared-state churn).

**Alternatives considered:**
- **(a) Auto-push after verification** — assumes continuity with Option B implementation
- **(b) Push + mark ready** — even more shared-state
- **(c) Present options and wait** (chosen)

**Rejection reasons:**
- (a) Violates the explicit policy. The policy says to confirm even when the earlier context seems to imply approval.
- (b) Compounds the violation with a second shared-state action.

**Trade-offs:** User must take one more action (approve push or instruct alternative) before the work becomes visible. Minor friction.

**Implication:** Session ends with the 2 commits local-only. Next session must either (1) user approves push, (2) user wants more changes before push, (3) user rejects commits and we revert.

**Confidence:** Very high (E3) — explicit policy, clear application, user's `/handoff:save` message confirmed the intent ("I will inspect this work and share my feedback with you in the next session" — literally asks for review-before-action).

**Reversibility:** N/A — deferring push costs nothing; pushing prematurely costs force-push churn to undo.

**Change trigger:** User says "push it" or provides durable instructions like "auto-push after local verification" in CLAUDE.md.

## Changes

**Session produced 2 new commits on `fix/t03-stale-cleanup-observability`** (on top of the 8 commits from the prior session + 4 pre-session plan revision commits = 14 commits total ahead of main). All 2 new commits are local-only, NOT yet pushed to origin.

### Commit log (this session)

| Commit | Type | Files | Insertions/Deletions | Description |
|---|---|---|---|---|
| `82d8cada` | fix | 3 | +18/-8 | `fix(containment-lifecycle): preserve exc class in fail-OPEN log; document policy` |
| `3568becd` | test | 1 (NEW) | +387/0 | `test(shakedown): cover CLI wrapper silent-on-clean and fail-FAST contracts` |

Total: ~405 insertions, ~8 deletions across 4 files.

### File-by-file changes

**`packages/plugins/codex-collaboration/scripts/containment_lifecycle.py`** (commit `82d8cada`, +11/-1 lines):
- Added an 8-line inline comment above `main()`'s outer `except Exception as exc:` at line 188 explaining that fail-OPEN is deliberate `SubagentStart` hook policy. The comment cross-references BOTH pinning tests by name (`test_main_fail_open_conversion_via_monkeypatched_listdir` and `test_subagent_start_surfaces_cleanup_enumeration_failure`) so a future maintainer who opens only this file can immediately find the tests that assert this contract.
- Changed the log call from `_log_error(f"containment-lifecycle: internal error ({exc})")` to a 3-line parenthesized form:
  ```python
  _log_error(
      f"containment-lifecycle: internal error. Got: {exc!r:.100}"
  )
  ```
- The new format preserves the exception class name via `repr(exc)`. Previously, `OSError("clean_stale_files failed: cannot enumerate shakedown root. Got: ...")` would log as `containment-lifecycle: internal error (clean_stale_files failed: ...)` — losing the `OSError` class marker. The new format logs as `containment-lifecycle: internal error. Got: OSError('clean_stale_files failed: ...')` — preserving it. The `:.100` truncation caps length at 100 chars.
- All existing assertions (`"containment-lifecycle: internal error" in result.stderr`) still match because the prefix is preserved.

**`packages/plugins/codex-collaboration/tests/test_containment_lifecycle.py`** (commit `82d8cada`, +4/-4 lines):
- Updated the docstring of `test_subagent_start_surfaces_cleanup_enumeration_failure` (lines 381-383):
  - Removed stale ref `at lines 184-188 of`
  - Changed `(lines 184-188 of containment_lifecycle.py)` to `in containment_lifecycle.py`
  - Changed `containment-lifecycle: internal error (<exc>)` to `containment-lifecycle: internal error. Got: <repr(exc)>` (reflects new format)
- Updated the docstring of `test_main_fail_open_conversion_via_monkeypatched_listdir` (line 464):
  - Changed `at main() lines 184-188` to `in main()'s outer except Exception block`

**`packages/plugins/codex-collaboration/tests/test_containment_smoke_setup.py`** (commit `82d8cada`, +3/-4 lines):
- Updated the docstring of `test_prepare_scenario_surfaces_cleanup_enumeration_failure` (around line 212):
  - Removed stale ref `at containment_smoke_setup.py:505-510`
  - Changed the sentence to reference `_run_with_wrapper()` by symbol name and describe it as "the Round 6 testability refactor extracted from the __main__ block"

**`packages/plugins/codex-collaboration/tests/test_clean_stale_shakedown.py`** (commit `3568becd`, NEW FILE, +387 lines):
- Module docstring (10 lines) explaining what coverage gap this file closes and what 4 contracts it pins
- Module-level `SCRIPT` constant pointing at `scripts/clean_stale_shakedown.py`
- `_load_shakedown_module()` helper (~20 lines) — importlib loader matching the lifecycle pattern (no sys.modules registration needed)
- `_run_shakedown(*, data_dir)` helper (~20 lines) — subprocess runner with env-var injection, parallels `_run_lifecycle`
- **6 tests:**
  1. `test_clean_stale_shakedown_is_silent_on_clean_run` (~25 lines) — Round 5 Choice 3B regression guard. In-process, empty shakedown dir, assert `captured.err == ""`.
  2. `test_clean_stale_shakedown_emits_report_on_had_errors` (~40 lines) — monkeypatches `containment.clean_stale_files` to return a stub `CleanStaleResult` with `failed_unlink=(failure_path, error_repr)`, calls main() in-process, asserts stderr contains `"clean_stale_files:"`, `"failed_unlink=1"`, the failure path name, and the error repr substring.
  3. `test_clean_stale_shakedown_exits_1_when_env_var_missing` (~15 lines) — `monkeypatch.delenv("CLAUDE_PLUGIN_DATA", raising=False)`, in-process main() → exit 1, asserts canonical `"clean_stale_shakedown failed: CLAUDE_PLUGIN_DATA not set"` prefix.
  4. `test_clean_stale_shakedown_exits_1_when_env_var_is_regular_file` (~20 lines) — creates a regular file, points env var at it, asserts canonical `"clean_stale_shakedown failed: CLAUDE_PLUGIN_DATA is not a directory"` prefix.
  5. `test_clean_stale_shakedown_subprocess_fails_fast_on_unreadable_shakedown` (~60 lines including long docstring) — subprocess end-to-end with real `chmod 0o000` on shakedown dir, `skipif` root/Windows, `finally: chmod 0o755` teardown to unblock pytest cleanup. Asserts exit 1 + 3 substring checks (caller prefix, Stage 3 enumeration context).
  6. `test_clean_stale_shakedown_wrapper_converts_exception_to_exit_1_via_runpy` (~55 lines including long docstring) — platform-agnostic in-process fallback. Uses `runpy.run_path(SCRIPT, run_name="__main__")` with monkeypatched `os.listdir`, asserts `SystemExit.code == 1` via `pytest.raises`, plus the same 3 stderr substring checks.

## Codebase Knowledge

### Architecture: Two distinct error surfaces across 3 callers

The T-03 PR's core architectural insight is that `clean_stale_files` exposes TWO error surfaces to its 3 callers. Each caller has its own outer-boundary contract shape.

| Caller | Path | Wrapper | Exit | Stderr prefix | Policy |
|---|---|---|---|---|---|
| **CLI wrapper** | `scripts/clean_stale_shakedown.py` | inline `__main__` block (lines 47-54) | 1 | `clean_stale_shakedown failed:` | fail-FAST (operator tool) |
| **Smoke setup** | `scripts/containment_smoke_setup.py` | `_run_with_wrapper()` function (lines 510-526) | 1 | `containment_smoke_setup failed:` | fail-FAST (developer tool) |
| **Lifecycle hook** | `scripts/containment_lifecycle.py` | `main()` outer `except Exception` (lines 186-190) | 0 | `containment-lifecycle: internal error` | **fail-OPEN** (SubagentStart hook policy — non-zero blocks spawn) |

The fail-OPEN vs fail-FAST distinction is the key architectural decision. Lifecycle cannot raise or return non-zero because SubagentStart treats that as "block the agent spawn" — a containment-state defect must surface via stderr observability, never via the hook's exit code.

**Per-file error surface (all 3 callers):**
- `clean_stale_files()` returns `CleanStaleResult` with `removed` + `skipped_fresh` + `failed_stat` + `failed_unlink` buckets
- `had_errors` property is True iff `failed_stat` or `failed_unlink` is non-empty
- Each caller does `if result.had_errors: print(result.report(prefix=...), file=sys.stderr)` with its own caller prefix
- Clean runs produce silent stderr (Round 5 Choice 3B) so operators only see output when something went wrong

**Root-level error surface (all 3 callers):**
- `clean_stale_files()` raises `OSError` with specific messages for each failure stage
- Caller's outer exception boundary wraps it with caller-specific context and exit code
- `CleanStaleResult.report()` is NOT called for root-level failures because the function raises before returning a result

### Files read this session

| File | Why | Key findings |
|---|---|---|
| `docs/handoffs/2026-04-11_17-00_*.md` | Handoff load | Branch state, prior decisions, 6 gotchas list |
| `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py` (full, 202 lines) | I-1/I-2 edits | Lines 186-190 contain the fail-OPEN block; `_log_error` at line 43; `_handle_subagent_start` at 63 with cleanup at 73-75 |
| `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py` (full, 55 lines) | Test authoring | Short file: env validation, delayed import, `clean_stale_files` call, `__main__` wrapper at 47-54 |
| `tests/test_containment_lifecycle.py` (lines 1-100 + 370-480 via grep) | Find stale refs + helper patterns | `_load_lifecycle_module` at 35-43 (no sys.modules registration), `_run_lifecycle` at 46-59, stale line refs at 381 and 464 |
| `tests/test_containment_smoke_setup.py` (lines 1-60 + 200-280) | Find stale refs + Python 3.14 workaround pattern | `_load_smoke_setup_module` at 23-41 (WITH sys.modules registration + cleanup), stale ref at line 212 referring to `containment_smoke_setup.py:505-510` |
| `scripts/containment_smoke_setup.py` (lines 500-540) | Verify `_run_with_wrapper` actual location | Function at 510-526, `__main__` block at 529-530, confirmed smoke_setup:525 uses `{exc}` (not flagged by reviewer) |
| `packages/plugins/handoff/skills/save/synthesis-guide.md` | Handoff writing | 13 required sections, 8 decision elements, evidence requirements |
| `packages/plugins/handoff/references/format-reference.md` | Handoff writing | Frontmatter schema, depth targets, quality calibration |

### Test patterns confirmed this session

- **Loader helper** (`_load_*_module`): `importlib.util.spec_from_file_location(name, SCRIPT)` + `exec_module`. Optional sys.modules registration when the target module has dataclasses with `from __future__ import annotations`.
- **Subprocess runner** (`_run_*`): `subprocess.run([sys.executable, SCRIPT], input=json..., capture_output=True, text=True, env=env)`. Env-var injection for `CLAUDE_PLUGIN_DATA`.
- **Subprocess chmod test pattern**: Create shakedown dir + test fixture, `try: chmod 0o000, call subprocess, finally: chmod 0o755`. `@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() == 0, reason=...)` guard. The `finally` chmod reset is mandatory because pytest's `tmp_path` teardown would fail on unwalkable directories, masking real test failures.
- **In-process fallback pattern**: Mock `os.listdir` via `monkeypatch.setattr("os.listdir", _raising_listdir)` — works because `containment.py` uses module-scope `import os` with attribute lookup at call time. Would break if refactored to `from os import listdir`.
- **Delayed import monkeypatching**: `main()` does `from server.containment import clean_stale_files` inside the function body. Monkeypatching `containment.clean_stale_files` BEFORE calling `main()` works because the `from ... import` line resolves the attribute at call time from the already-cached `server.containment` module.
- **runpy as `__main__` entry point**: `runpy.run_path(SCRIPT, run_name="__main__")` executes a script with `__name__ == "__main__"`, causing the `if __name__ == "__main__":` block to run. `SystemExit` propagates to the caller; catch with `pytest.raises(SystemExit)` and inspect `exc_info.value.code`. `capsys` captures stderr because `print(..., file=sys.stderr)` uses pytest's replaced `sys.stderr` object.

### Available review agents in pr-review-toolkit plugin

Surfaced during the ToolSearch for subagent types:
- `pr-review-toolkit:silent-failure-hunter` — error-handling audit, catches silent failures and inadequate fallbacks
- `pr-review-toolkit:code-reviewer` — general quality, CLAUDE.md compliance
- `pr-review-toolkit:code-simplifier` — post-review polish pass (not used this session)
- `pr-review-toolkit:comment-analyzer` — comment accuracy, maintainability, rot
- `pr-review-toolkit:type-design-analyzer` — type encapsulation, invariant expression
- `pr-review-toolkit:pr-test-analyzer` — test coverage quality and gaps

All 5 used (minus code-simplifier) for a comprehensive review. Each has a distinct specialty that catches different issue classes. Empirically: code-reviewer missed findings that specialists caught.

### Key locations

| Concept | Location |
|---|---|
| Fail-OPEN hook block (needs-rationale-comment-now-has-one) | `containment_lifecycle.py:186-197` (was 186-190) |
| Lifecycle `_handle_subagent_start` cleanup gate | `containment_lifecycle.py:73-75` |
| Smoke-setup Round 6 `_run_with_wrapper` | `containment_smoke_setup.py:510-526` |
| Smoke-setup `__main__` dispatch | `containment_smoke_setup.py:529-530` |
| Shakedown CLI `__main__` wrapper (inline, no extraction) | `clean_stale_shakedown.py:47-54` |
| `CleanStaleResult` dataclass | `server/containment.py:293-355` (approximate) |
| Three-stage failure check | `server/containment.py:412-457` (approximate) |
| Test loader pattern (no registration) | `test_containment_lifecycle.py:35-43` |
| Test loader pattern (WITH registration) | `test_containment_smoke_setup.py:23-41` |
| Monkeypatch.context scoping guard comments | `test_containment.py:291, 546` |

## Context

### Branch and PR state

- **Branch:** `fix/t03-stale-cleanup-observability`
- **HEAD commit:** `3568becd` (local)
- **Origin commit:** `95232d52` (unchanged from prior session)
- **Commits ahead of origin:** 2 (`82d8cada`, `3568becd`)
- **Commits ahead of main:** 14 total (4 plan revisions + 8 prior session tasks + 2 this session)
- **PR #104 state:** Draft, URL https://github.com/jpsweeney97/claude-code-tool-dev/pull/104
- **PR current state on GitHub:** Reflects `95232d52` (doesn't include this session's 2 commits)
- **Push status:** Not yet pushed. Awaiting user inspection per user's explicit `/handoff:save` message.

### Test baseline

- **Pre-session baseline:** 538 tests passing (macOS non-root)
- **This session added:** 6 new tests in `test_clean_stale_shakedown.py`
- **Post-session baseline:** 544 tests passing (macOS non-root)
- **Alternative baselines (not re-verified this session):**
  - Root/Windows: 541 passed + 3 skipped (the 3 chmod tests skip)
  - No symlink: 543 passed + 1 skipped
  - Root AND no symlink: 540 passed + 4 skipped

### Ruff quality gate

All 4 edited/created files pass `uv run ruff check <file>`. Verified twice this session:
- After polish edits: 3 files clean
- After new test file: 1 file clean

Package-wide `uv run ruff check` NOT run this session — per plan guidance, file-scoped check only (package-wide has pre-existing failures in unrelated files).

### Mental model for this session

**Framing:** This is an evidence-gathering problem with a decision-making layer. Each reviewer is a narrow sensor; aggregation is the classifier; the user is the priority-setter. My job is to run the sensors, aggregate honestly, make an initial recommendation, and accept corrections that change the priority weights.

**Core insight:** Specialized reviewers dramatically outperform a single general review when the target has multiple dimensions (correctness + tests + types + comments + error handling). The code-reviewer found zero issues; specialists found 11 findings across 4 categories. Parallelism is the speed multiplier; specialization is the thoroughness multiplier.

**Mental model:** "Review as evidence gathering" — don't skip the review even if you think you know the answer. Don't bias reviewers by pre-briefing them. Aggregate and prioritize AFTER evidence is collected. Be willing to accept user corrections to the priority weighting.

### Environment state

- macOS Darwin 25.3.0
- Python 3.14.2
- pytest 9.0.2 with anyio-4.12.1, asyncio-1.3.0 plugins
- `uv` for all Python tool invocations (no direct `pip`, `pytest`, `ruff` calls)
- Working directory: `/Users/jp/Projects/active/claude-code-tool-dev`
- Test run from: `packages/plugins/codex-collaboration/` (via `cd` in Bash command)

## Conversation Highlights

### User's Option B counter-recommendation (the key exchange)

I recommended Option A (minimum polish, skip the missing test file) as "the sweet spot" — my reasoning was that I-1 was a maintainability landmine, I-2+I-4 were trivial, and I-3 was "real but deferrable". The user pushed back with a reasoned argument:

**User, verbatim:**
> "I recommend **(b) Option B**.
>
> Reasoning from the live tree:
> - **I-3 is the only remaining finding that materially affects confidence, not just maintainability.** `clean_stale_shakedown.py` is still untested, and it is the most user-facing caller boundary in the PR.
> - The wrapper is **small and cheap to lock down**. Its behaviors are clear and finite: clean run stays silent, `had_errors=True` reports to `stderr`, bad `CLAUDE_PLUGIN_DATA` exits `1`, and the outer wrapper converts unexpected exceptions to the prefixed `exit 1` path.
> - **I-1, I-2, and I-4 are real, but they are polish-class compared with I-3.** I would still fix them, but I would not stop at Option A and leave the one real coverage hole open.
> - The branch is still in **draft PR** state, so this is the right moment to add the small test file before inviting human review. After the PR is ready, adding a new caller test file is more churn for less benefit.
>
> So my ordering is:
> 1. **Option B** if you want the strongest pre-review state.
> 2. **Option A** only if you want minimum churn and are deliberately optimizing for speed (which we aren't, we are aiming for robustness)
> 3. **Option D** is defensible, but not my recommendation while the wrapper caller still has zero tests."

The correction is rich: it explicitly separates "confidence" from "maintainability" as distinct axes, names the exact window ("draft PR state, this is the right moment"), and calibrates the user's priority weighting ("we are aiming for robustness, not speed"). This is what a **correction that reveals priorities** looks like.

### User's handoff request

**User, verbatim:**
> "Save a handoff. I will inspect this work and share my feedback with you in the next session"

This is an explicit approval-gated checkpoint. The user wants to review my work (the 2 commits) before any push or mark-ready action. The next-session feedback will shape whether we push as-is, make changes, fix smoke_setup:525, or do something else entirely.

### User's task tool reminder response

The task tools had a system reminder asking about task tracking. I took this as a signal to use TaskCreate, loaded it via ToolSearch, and created 8 tasks. User did not push back on the task tracking overhead — accepted as appropriate for 8-step work.

## User Preferences

**Robustness over speed (this session, explicit):**
> "Option A only if you want minimum churn and are deliberately optimizing for speed (which we aren't, we are aiming for robustness)"
— Changes the priority weighting from "minimize churn" to "maximize confidence".

**Confidence vs maintainability distinction:**
> "I-3 is the only remaining finding that materially affects **confidence**, not just **maintainability**."
— User separates "will this work correctly" (confidence, driven by tests) from "will future-me understand this" (maintainability, driven by comments and structure). Confidence is weighted higher here.

**Draft PR state discipline:**
> "The branch is still in draft PR state, so this is the right moment to add the small test file before inviting human review. After the PR is ready, adding a new caller test file is more churn for less benefit."
— User has a mental model of PR lifecycle with distinct "pre-review" and "post-review" phases and allocates work accordingly. Pre-review is the cheap-change window.

**Structured option evaluation:**
When the user made the Option B recommendation, they explicitly ordered all 4 options by preference ("my ordering is: 1. Option B... 2. Option A... 3. Option D..."). This style — total-ordering the alternatives rather than picking one — reveals they think about decisions as preference orderings, not binary yes/no choices.

**Scope-control expectation (inferred from corrections):**
When I proactively flagged the `containment_smoke_setup.py:525` inconsistency as "NOT fixed due to scope control", the user acknowledged the flag without pushing back on the decision. This suggests the scope-control policy is understood and expected. The `/handoff:save` message asking for inspection also implicitly endorses NOT auto-fixing things they might review.

**Communication style (from prior handoff observation, confirmed this session):**
- Terse corrections with clear reasoning chains
- Explicit about priority weighting ("robustness" vs "speed", "confidence" vs "maintainability")
- Prefers recommendations-first presentation but will push back with full reasoning when the recommendation is wrong
- Uses numbered lists and bold for structure
- Treats the handoff/load cycle as a first-class tool

## Learnings

### Parallel specialized reviewers outperform single general review

**Mechanism:** Each reviewer specialty has a different "lens" — code-reviewer looks for general quality, silent-failure-hunter looks for error-handling gaps, pr-test-analyzer looks for coverage holes, type-design-analyzer looks for invariant violations, comment-analyzer looks for inaccurate/missing rationale. Each finds things the others miss.

**Evidence:** This session's concrete numbers:
- code-reviewer: 0 critical, 0 important, 2 minor suggestions (recommended "Ready to merge")
- pr-test-analyzer: 1 critical gap (missing test file, criticality 9)
- silent-failure-hunter: 1 important defect (`{exc}` → `{exc!r:.100}`)
- type-design-analyzer: 1 important suggestion (`NamedTuple FileFailure`)
- comment-analyzer: 1 critical gap (missing fail-OPEN comment), 3 improvements

Had I used only code-reviewer, we'd have marked the PR ready with I-2 (exception class dropped in fail-OPEN path), I-3 (missing test file for Round 5 Choice 3B), and I-1 (missing policy comment) still unflagged. The specialized parallel dispatch caught all three.

**Implication:** For any non-trivial PR review, dispatch multiple specialized reviewers. The token cost is outweighed by the findings uplift. For trivial PRs (single-file, small diff), a single general reviewer is sufficient.

**Watch for:** Reviewer claims can be factually wrong — silent-failure-hunter asserted "every other error site uses `{exc!r:.100}`" but missed that `containment_smoke_setup.py:525` has the same defect as lifecycle. Never take a reviewer claim as ground truth without spot-checking.

### "Spec-verbatim pre-load" doesn't forbid real findings

**Mechanism:** The prior session's learning was that telling reviewers "these patterns are spec-prescribed, don't flag them as style issues" prevents false positives on Task 1's code-quality review. This session extended that: include explicit "deliberate design choices" in the dispatch prompt (fail-OPEN, silent-on-clean, Round 6 refactor). Reviewers still found NEW issues in the non-spec areas.

**Evidence:** Every reviewer this session respected the deliberate-design notes (none flagged the fail-OPEN policy as "swallowing exceptions"). But they still caught real defects — I-2 (`{exc}` vs `{exc!r:.100}`) is not a spec-prescribed choice; it's an implementation inconsistency that got missed during the 8 prior commits.

**Implication:** The pre-load is an "exclusion zone" not a "suppression zone". It tells reviewers "don't flag these", not "accept all of this code". Real implementation drift in the non-spec areas is still in-scope.

**Watch for:** Over-applying the pre-load would create false negatives (missing real issues in code adjacent to spec-prescribed patterns). Keep the exclusion list narrow.

### Delayed imports can be monkeypatched via the target module

**Mechanism:** When a function does `from X import Y` inside its body, the `from ... import` line resolves the attribute `Y` on the cached module `X` at call time. Monkeypatching `X.Y` BEFORE calling the function causes the import to pick up the patched value — as long as `X` is already loaded in `sys.modules`.

**Evidence:** `clean_stale_shakedown.py:main()` does `from server.containment import clean_stale_files, shakedown_dir`. Test monkeypatches `containment.clean_stale_files` before calling `main()`. Test works:
```python
monkeypatch.setattr(containment, "clean_stale_files", _stub_clean_stale_files)
module = _load_shakedown_module()
exit_code = module.main()
# assertions pass — main() picked up the stub
```

**Implication:** Delayed imports aren't a testing obstacle if you know this trick. They can even be BETTER for testing than top-level imports because you can patch without affecting unrelated tests (as long as monkeypatch is properly scoped).

**Watch for:** If the delayed import happens before sys.modules has cached `server.containment` (e.g., module was loaded fresh via importlib with a synthetic name), the import might load the real module at call time. This is not the case for clean_stale_shakedown.py because `server.containment` is imported at the test file's top level.

### runpy.run_path is the stdlib's answer to "test my __main__ block"

**Mechanism:** `runpy.run_path(script_path, run_name="__main__")` executes a Python file with `__name__ == "__main__"`, triggering the `if __name__ == "__main__":` block. All top-level code runs, including the file's imports. Exceptions propagate to the caller (including SystemExit). `capsys` captures stderr because Python-level `print(..., file=sys.stderr)` resolves to the replaced `sys.stderr` at call time.

**Evidence:** This session's `test_clean_stale_shakedown_wrapper_converts_exception_to_exit_1_via_runpy` uses:
```python
monkeypatch.setattr("os.listdir", _raising_listdir)
with pytest.raises(SystemExit) as exc_info:
    runpy.run_path(SCRIPT, run_name="__main__")
assert exc_info.value.code == 1
assert "clean_stale_shakedown failed: unexpected error" in captured.err
```
Works on macOS Python 3.14.2 with zero setup beyond the imports.

**Implication:** When a script's `__main__` wrapper is inlined and can't be refactored (or shouldn't be), runpy is the cleanest in-process testing path. Matches the Round 6 testability goal (in-process fallback for root/Windows) without requiring a production code refactor.

**Watch for:** 
- `runpy.run_path` re-executes the file in a fresh namespace every call — not the same as importing and calling a function. Don't use if you need to test multiple invocations sharing state.
- Monkeypatching via `monkeypatch.setattr("os.listdir", ...)` works with runpy because the patch applies to the `os` module in `sys.modules`, which runpy re-uses. If you patch a module-level function reference (`from X import Y`), runpy's fresh exec might get the unpatched version.

### Pyright continues to be advisory, not authoritative

**Mechanism:** Pyright's static analysis captures file state at intermediate moments (Edit tool events) and doesn't always re-analyze after the final state lands. This produces "stale" warnings that don't reflect the current code.

**Evidence (this session):**
1. After editing `containment_lifecycle.py`: Pyright fired "Import pytest could not be resolved" — pre-existing environment config issue, still firing
2. After editing `test_containment_smoke_setup.py`: Pyright fired "scenario_id is not accessed" at line 125 — the line didn't even match the current file state; I was editing a docstring
3. After writing `test_clean_stale_shakedown.py`: Pyright fired "_shakedown_path is not accessed" despite the underscore-prefix convention for intentionally unused parameters; renamed from `shakedown_path` to `_shakedown_path` and Pyright STILL complained

**Implication:** NEVER trust Pyright advisory warnings without verifying via `uv run pytest` and `uv run ruff check`. Those are the authoritative quality gates. Pyright is for IDE-level feedback only.

**Watch for:** Pyright tempts you to "fix" false positives (e.g., add type annotations, rename variables) that add noise without improving real quality. Ignore them unless ruff or tests fail.

## Next Steps

### 1. User inspection of the 2 local commits (next-session action)

**Dependencies:** None — commits are local-only, ready to inspect.

**What to read first:** `git log --oneline origin/fix/t03-stale-cleanup-observability..HEAD` to see the 2 commits, then `git show 82d8cada` and `git show 3568becd` to review each diff.

**Approach suggestion:** The user explicitly said they'll inspect this work and share feedback. The next session should start with the user's feedback on the commits. Be prepared for any of:
- "Looks good, push and mark ready" → execute `git push origin fix/t03-stale-cleanup-observability` + `gh pr ready 104`
- "Also fix smoke_setup:525" → make the 5-char edit, amend or new commit, re-verify, push
- "Change X in the test file" → edit, re-verify, amend or new commit
- "Revert the test file, it's too much" → unlikely given the Option B alignment, but possible
- "I want to see the aggregated review again" → summarize from this handoff

**Acceptance criteria:** User's feedback is understood and acted on; next session ends with either the commits modified per feedback OR pushed to origin.

**Potential obstacles:** User may want to amend the polish commit to also fix smoke_setup:525, which requires `git commit --amend` rather than new commit (minor complication but standard).

### 2. Push to origin (awaits user approval)

**Dependencies:** User approval per global CLAUDE.md shared-state action policy.

**What to read first:** None — just execute.

**Approach:** `git push origin fix/t03-stale-cleanup-observability` — updates draft PR #104 on GitHub. Branch is 2 commits ahead so push is a straight fast-forward.

**Acceptance criteria:** PR #104 page on GitHub shows the 2 new commits; `gh pr view 104` shows them in the commit list.

**Potential obstacles:** CI may run even on draft PRs depending on repo config. Any CI failure would need investigation (most likely pre-existing unrelated failures, not these commits).

### 3. (Optional) Fix `containment_smoke_setup.py:525` consistency

**Dependencies:** User decision on whether to do this now, next PR, or skip entirely.

**What to read first:** `packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py:522-526`

**Approach:** 5-character edit:
```python
# Before (line 525):
print(f"containment_smoke_setup failed: {exc}", file=sys.stderr)
# After:
print(f"containment_smoke_setup failed: unexpected error. Got: {exc!r:.100}", file=sys.stderr)
```
Then re-verify with `uv run ruff check` + `uv run pytest tests/test_containment_smoke_setup.py` (need to check if any tests assert on the exact format).

**Acceptance criteria:** Both fail-wrapper outer contracts (lifecycle + smoke_setup) use `{exc!r:.100}` consistently. clean_stale_shakedown's wrapper already uses the pattern.

**Potential obstacles:** Test assertions at `test_containment_smoke_setup.py:282, 396` use substring `"containment_smoke_setup failed"` which is prefix-only — those will still match. But the docstring descriptions at lines 213-220 reference the old `<exc>` format and would need parallel updates.

### 4. (Optional) Mark PR ready for review

**Dependencies:** All commits pushed. User approval (shared-state action — notifies reviewers).

**What to read first:** The PR body; the 14 commits on the branch.

**Approach:** `gh pr ready 104` — transitions draft → ready, may trigger CI, notifies any configured reviewers.

**Acceptance criteria:** PR is marked ready; CI runs and passes; reviewers can comment.

**Potential obstacles:** Notifies GitHub reviewers; irreversible via `gh` (though `gh pr ready --undo` exists for un-ready). Consider whether all in-progress cleanup is done first.

### 5. (Optional, deferred) Address the 7 Suggestions from the review

**Dependencies:** Merge of PR #104 (or a follow-up PR for these).

**What to read first:** This handoff's "Suggestions (7 found)" list in the earlier session narrative + the prior handoff's similar list.

**Approach:** Evaluate each suggestion's leverage vs cost:
- **S-1 `NamedTuple FileFailure`** (highest leverage) — positional tuple unpacks are fragile; a named tuple refactor is low-cost and removes the fragility
- **S-3 `skipped_non_regular` bucket** — observability improvement; low priority today
- **S-6 `_load_smoke_setup_module` sys.modules cleanup on happy path** — hygiene; minor
- **S-1 through S-7** — can bundle into a follow-up "T-03 follow-ups" PR

**Acceptance criteria:** Decided per suggestion whether to include in this PR, a follow-up PR, or skip.

**Potential obstacles:** Each suggestion adds churn; scope discipline argues for a separate PR.

### 6. Ticket status update at merge time

**Dependencies:** PR merged.

**What to read first:** `docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md`

**Approach:** Update frontmatter `status: deferred` → `status: done`; optionally fix pre-existing wrong `branch:` field.

**Acceptance criteria:** Ticket reflects completed status.

(Carried forward from prior handoff — not this-session work.)

## In Progress

**Clean stopping point — 2 local commits landed and verified, no work in flight.** The session's Option B execution completed fully. The branch is in a consistent state: all 8 tasks from the internal TaskCreate list are marked `completed`, ruff is clean, 544 tests pass.

The only "in progress" artifact is the **pending user inspection** of the 2 commits before push. This is not a technical in-progress state (nothing is half-written or broken); it's an **approval gate** explicitly requested by the user via `/handoff:save`.

## Open Questions

### 1. Should `containment_smoke_setup.py:525` be fixed in the same PR?

**Context:** Same `{exc}` vs `{exc!r:.100}` pattern as I-2 in lifecycle. Not flagged by the silent-failure-hunter reviewer; I flagged it during implementation but did NOT fix it per scope control.

**Options:**
- (a) Fix in a 3rd local commit before push (bundled with the current 2 commits) — cleanest PR state
- (b) Fix as a follow-up commit after push (separate commit, shows up in PR diff) — scope-faithful
- (c) Fix in a follow-up PR after this one merges — scope-faithful, but creates PR proliferation
- (d) Skip entirely (accept the inconsistency) — minimum churn

**My bias:** (a) or (b). The fix is trivial and fixing consistency before human review is the right time. But deferring to user.

### 2. Should any of the 7 Suggestions be addressed in this PR?

**Context:** The most leveraged is S-1 (`NamedTuple FileFailure` for the failure tuple structure). Others are deferrable hygiene items.

**Options:**
- (a) Include S-1 in this PR as another commit (adds ~15 lines of refactor)
- (b) Defer all to a follow-up PR
- (c) Defer all indefinitely

**My bias:** (b). S-1 is real but exceeds Option B scope.

### 3. Does `superpowers:finishing-a-development-branch` auto-mark-ready, or wait for approval?

**Context:** Carried forward from prior handoff. If we want to use the skill's flow, need to know whether invoking it triggers the mark-ready shared-state action automatically or pauses for approval.

**How to find out:** Read the skill file at `~/.claude/plugins/cache/claude-plugins-official/superpowers/*/skills/finishing-a-development-branch/SKILL.md` (or similar). Won't touch anything; read-only lookup.

### 4. Does the ticket system have intermediate statuses?

**Context:** Also carried forward from prior handoff. `deferred` is the current status; `done` is the end target. Is there a `ready_for_review` or `in_review` for the draft-PR interval? Pre-existing tickets would need survey.

**How to find out:** `grep -h "^status:" docs/tickets/*.md | sort -u` to see all in-use statuses.

## Risks

### 1. smoke_setup:525 inconsistency remains unresolved

**Impact:** Human reviewers will likely catch the `{exc}` vs `{exc!r:.100}` inconsistency and request it be fixed. Minor delay in review cycle.

**Mitigation:** Flagged in my final summary to the user. User can decide to fix before push.

### 2. CI may surface failures not visible in local ruff/pytest

**Impact:** Push would trigger CI; unexpected CI failure delays mark-ready. The PR is draft, so CI may or may not run depending on repo config.

**Mitigation:** Test plan in PR body lists expected baselines (538 → 544 with 6 new tests). If CI fails, investigate immediately.

### 3. runpy test brittleness

**Impact:** `test_clean_stale_shakedown_wrapper_converts_exception_to_exit_1_via_runpy` depends on `runpy.run_path` semantics and monkeypatched `os.listdir`. If `containment.py` ever refactors to `from os import listdir`, the monkeypatch target becomes wrong and the test silently stops covering the wrapper (SystemExit never raised).

**Mitigation:** Docstring explicitly documents this coupling. If `containment.py` is ever refactored, the test will fail loudly (no SystemExit) which is the correct failure mode.

### 4. sys.modules asymmetry across test loaders (still present, now 3 patterns)

**Impact:** Minor hygiene debt. The prior session's holistic reviewer flagged the 2-pattern asymmetry; this session adds a 3rd pattern (no registration for shakedown). Each is correct for its target, but the divergence is slightly surprising.

**Mitigation:** Each loader has a docstring explaining why it does or doesn't register in sys.modules. Future developers adding a new loader should check their module's dataclass usage.

### 5. Pyright continues to complain; no permanent fix

**Impact:** Every session with test file edits produces Pyright false positives (pytest import not resolved, unused params, stale line numbers). Developer ergonomics slightly degraded; real issues could hide in the noise.

**Mitigation:** Documented pattern in prior handoff + this handoff. Project policy: trust `uv run pytest` and `uv run ruff check` as authoritative. Could add project-level Pyright config to silence the known false positives, but that's out of scope for this PR.

### 6. Draft PR merge-time risks (carried forward)

**Impact:** Ticket status update, branch field cleanup, `finishing-a-development-branch` skill invocation. All documented in prior handoff.

**Mitigation:** Captured in Next Steps.

## References

**PR, branch, commits:**
- PR #104: https://github.com/jpsweeney97/claude-code-tool-dev/pull/104
- Branch: `fix/t03-stale-cleanup-observability`
- This session's commits (local-only):
  - `82d8cada` — fix(containment-lifecycle): preserve exc class in fail-OPEN log; document policy
  - `3568becd` — test(shakedown): cover CLI wrapper silent-on-clean and fail-FAST contracts
- Prior session's 8 task commits (already pushed): `6c841ed3`, `0119d97f`, `723cf471`, `d550a683`, `418017c4`, `9df5ae06`, `7226a299`, `95232d52`
- Pre-session plan revision commits: `d30ee249`, `f038aaff`, `c3a3c7a0`, `6e0f6820`

**Handoffs:**
- Prior handoff: `docs/handoffs/archive/2026-04-11_17-00_t03-execution-complete-pr-104.md`
- This handoff: `docs/handoffs/2026-04-11_21-24_pr-104-review-option-b-commits-pending-push.md`

**Plan and tickets:**
- Implementation plan: `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` (2281 lines)
- Ticket: `docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md` (status: deferred, needs update to done at merge time)

**Review agents used:**
- `pr-review-toolkit:code-reviewer`
- `pr-review-toolkit:pr-test-analyzer`
- `pr-review-toolkit:silent-failure-hunter`
- `pr-review-toolkit:type-design-analyzer`
- `pr-review-toolkit:comment-analyzer`

**Skill resources consulted:**
- `packages/plugins/handoff/skills/save/synthesis-guide.md`
- `packages/plugins/handoff/references/format-reference.md`
- `packages/plugins/handoff/references/handoff-contract.md` (referenced, not re-read)

**Project standards:**
- `~/.claude/CLAUDE.md` — global rules (no `rm`, use `trash`, scope control, shared-state approval)
- `.claude/CLAUDE.md` — project rules (ruff authoritative, error format convention, tenets, frameworks)
- `.claude/rules/methodology/tenets.md` — design philosophy (Explicit over Silent, Deterministic over Heuristic)
- `.claude/rules/workflow/git.md` — branch protection policy

## Gotchas

### Silent-failure-hunter can claim consistency that isn't true

**Symptom:** The silent-failure-hunter agent confidently asserted "every other error site in this PR uses `{exc!r:.100}`" when flagging I-2. But `containment_smoke_setup.py:525` has the identical `{exc}` pattern that was not flagged.

**Root cause:** Specialized reviewers can confuse their narrow lens with a global audit. The silent-failure-hunter focused on the lifecycle module and didn't systematically check every outer-wrapper in the PR.

**Mitigation:** Always spot-check reviewer claims that generalize across the codebase ("every other", "always", "nowhere else"). A quick grep is cheap insurance.

### `runpy.run_path` re-executes the file in a fresh namespace

**Symptom:** A test that imports the module AND also uses `runpy.run_path` on the same file will see different state (the imported module's attributes vs the runpy-loaded namespace's attributes).

**Root cause:** `runpy.run_path` creates a new globals dict and `exec`s the file into it. `sys.modules` entries from earlier imports are still used for the file's OWN imports (e.g., `import os`), but the file's top-level assignments (`main = def ...`) don't touch the earlier imported module.

**Mitigation:** Don't mix `_load_shakedown_module()` and `runpy.run_path` in the same test. This session's test file does mix them but in separate tests, so each test starts with a clean state.

### `capsys` captures `print(..., file=sys.stderr)` from runpy-executed code

**Symptom:** Writing to `sys.stderr` from inside runpy-executed code IS captured by `capsys` (not `capfd`).

**Root cause:** capsys replaces `sys.stdout` and `sys.stderr` at the Python module level. `print(..., file=sys.stderr)` resolves `sys.stderr` at call time, picking up the replaced object. runpy doesn't override these.

**Mitigation:** Use `capsys` fixture (not `capfd`) for runpy-executed code. Verified in this session's test.

### Delayed imports must have the target module ALREADY CACHED in sys.modules for monkeypatch to work

**Symptom:** If you load a script via `importlib` with a fresh name and monkeypatch `some_module.func`, the script's `from some_module import func` might get a DIFFERENT copy of `some_module` if `some_module` isn't cached.

**Root cause:** `from X import Y` looks up `sys.modules['X']` to find `X`, then reads `X.Y`. If the test file's top-level `from server import containment` has already happened, `sys.modules['server.containment']` exists and `containment.clean_stale_files` is patchable. If not, the delayed `from server.containment import` could load a separate copy.

**Mitigation:** Import the target module at the top of the test file (`from server import containment`) BEFORE defining tests. This session's test does this at line 32.

### Pyright doesn't always respect underscore-prefix for unused parameters

**Symptom:** Renamed `shakedown_path` → `_shakedown_path` to silence Pyright's "not accessed" warning. Pyright continued to complain.

**Root cause:** Pyright's "unused parameter" check apparently doesn't always apply the `_` prefix convention that ruff does. May be a Pyright version or config issue.

**Mitigation:** Ignore Pyright on this — ruff is authoritative and accepts the underscore convention. If the warning is persistent, could add `# type: ignore` comment, but that's yet more noise.

### The project has pre-existing package-wide ruff failures

**Symptom:** `cd packages/plugins/codex-collaboration && uv run ruff check` (no file arguments) surfaces failures in `codex_runtime_bootstrap.py`, `tests/conftest.py`, `tests/test_credential_scan.py`, `tests/test_dialogue_profiles.py` — unrelated to T-03.

**Root cause:** Pre-existing code quality debt in files outside T-03's scope.

**Mitigation:** Always use file-scoped `uv run ruff check <file> <file> ...` when verifying this PR. Per plan guidance, package-wide ruff is NOT the Task 9 quality gate.

### Test assertion style: substring checks tolerate format changes

**Symptom:** When I changed `f"... internal error ({exc})"` to `f"... internal error. Got: {exc!r:.100}"`, I worried existing tests would break.

**Root cause:** Test assertions use `"containment-lifecycle: internal error" in result.stderr` (substring check on prefix) not `result.stderr == "..."` (exact match). Prefix-preserving format changes don't break substring assertions.

**Mitigation:** When changing error message formats, check test assertions for exact-match vs substring. Prefer substring checks for format flexibility, but be aware that exact matches elsewhere could break. This session's lifecycle tests all use substring — safe to change format.

### The `finally: os.chmod(shakedown, 0o755)` teardown is mandatory

**Symptom:** Without it, `chmod 0o000` test fixtures leave the tmp_path directory unwalkable, and pytest's tmp_path cleanup fails — masking the actual test failure with an opaque teardown error.

**Root cause:** pytest's tmp_path teardown walks the directory tree to delete it. A 0o000 directory can't be walked into.

**Mitigation:** Every chmod 0o000 test MUST have a `finally: os.chmod(..., 0o755)` block. This session's new subprocess test includes it at lines ~265-270 of the test file. The comment explicitly says "This MUST happen even if the assertions below fail, otherwise tmp_path cleanup raises and masks the real failure."
