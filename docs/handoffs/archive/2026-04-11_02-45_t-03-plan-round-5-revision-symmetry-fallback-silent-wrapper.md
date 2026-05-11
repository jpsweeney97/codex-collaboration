---
date: 2026-04-11
time: "02:45"
created_at: "2026-04-11T06:45:00Z"
session_id: be296122-8956-4559-98e9-dd67b77a416f
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-11_00-46_t-03-plan-round-4-fail-open-policy-and-decoupled-tests.md
project: claude-code-tool-dev
branch: fix/t03-stale-cleanup-observability
commit: 6e0f6820
title: T-03 plan Round 5 revision — smoke-setup symmetry, in-process fallback, silent wrapper
type: handoff
files:
  - docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md
  - packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py
  - docs/tickets/closed-tickets/2026-02-15-plan-review-errata.md
---

# Handoff: T-03 plan Round 5 revision — smoke-setup symmetry, in-process fallback, silent wrapper

## Goal

Address the Round 5 adversarial review of the T-03 implementation plan (`docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md`) and produce a sixth draft that closes the High finding (smoke-setup root-failure proof gap) plus four Medium findings (two doc-drift, one platform-gating, one wrapper noise) plus one assumption note (stderr monitoring path), without invalidating any prior Round 1-4 fix.

**Trigger:** User delivered a Round 5 review titled "Scrutiny: [2026-04-10-t03-stale-cleanup-observability.md]" with verdict `Minor revision` (same as Round 4, meaning the core helper algorithm still survives but boundary-policy and coverage-symmetry issues remained). Five sections: Premise Check, Critical Failures, High-Risk Assumptions, Real-World Breakpoints, Hidden Dependencies, Adversarial Perspectives, Patterns And Root Causes, Required Changes.

**Stakes:** T-03 is now five rounds deep into adversarial review. The helper algorithm is settled; the remaining risk is **coverage asymmetry** (lifecycle has subprocess root-failure proof, smoke-setup does not — and they have structurally different outer-boundary contracts) and **summary drift** (Round 4's design decision corrected the framing in one place, but sibling sections — Task 8 lead-in at line 1136, self-review row 2 at line 1742 — still used the prior misleading "propagates naturally" / "all three callers print report() on error" wording). Without Round 5 fixes, a smoke-setup root-failure regression could ship with every other T-03 test passing.

**Bigger picture:** T-03 is the last correctness-hardening ticket on the codex-collaboration shakedown cleanup arc. T-04 (PR #102, merged in the second-prior session) shipped the wrapper script convention fixes. T-03 hardens `clean_stale_files()` itself — the function T-04's wrapper calls. Once T-03 ships, the cleanup path has explicit, tested failure modes at every layer from per-file operations up through each of the three callers' outer exception boundaries.

**Success criteria for this session:**
- Reviewer's High finding (smoke-setup root-failure gap) resolved with either a new test or an explicit scope narrow
- Reviewer's two Medium documentation-drift findings (Task 8 lead-in at line 1136, self-review row 2 at line 1742) resolved with rewrites that distinguish per-file from root-level surfaces
- Reviewer's Medium platform-gating finding (lifecycle subprocess test skip-gated → only proof on root/Windows disappears) resolved with a documented gap or a platform-agnostic fallback
- Reviewer's Medium wrapper noise finding (clean-path stderr trains operators to discount cleanup output) resolved with documentation or a code change
- Stderr-monitoring-path assumption (cross-referenced from MCP-server errata) addressed with at least an explicit assumption note
- All Round 1-4 fixes still intact, verified via grep sweeps
- Plan committed to the working branch as a discrete `docs:` commit (the plan file was untracked at session start)

**Connection to project arc:** This session is the fifth iteration in the iterative-review pattern established across rounds 1-4. Each round narrows the silent-failure surface by one layer:
- Round 1: per-file operations
- Round 2: root-level (dangling symlinks)
- Round 3: enumeration discovery layer (`Path.glob()` swallowing)
- Round 4: caller-boundary policy (fail-open made explicit)
- Round 5: caller-boundary coverage symmetry + summary drift cleanup

The user said: *"I will review the latest draft of the plan and then share my feedback with you in the next session"* — so this is a wait-for-feedback handoff, not a proceed-with-execution handoff. A potential Round 6 is possible.

## Session Narrative

**Phase 1 — Resume and frame Round 5.**

Session began by resuming from the Round 4 handoff (state file at `docs/handoffs/.session-state/handoff-be296122-8956-4559-98e9-dd67b77a416f` pointed to `docs/handoffs/archive/2026-04-11_00-46_t-03-plan-round-4-fail-open-policy-and-decoupled-tests.md`). The Round 4 handoff predicted that a Round 5 was possible and instructed: "If user returns with Round 5 findings, apply the same empirical-verify-then-fix pattern that addressed Round 4." The user delivered exactly that — a structured Round 5 review with the same format as prior rounds.

Initial framing observation: Round 5 is qualitatively different from Rounds 1-4 because the reviewer opened with *"this draft is finally attacking the right problem"* and every finding targets caller-contract asymmetry or summary drift, not helper correctness. The pattern shifted from "fix the algorithm" to "match the summary language to what the tests actually pin."

**Phase 2 — Empirical verification of every Round 5 claim.**

Following the Round 4 pattern (verify before fixing), I read every line the reviewer cited:

- **Plan line 1136** (Task 8 lead-in): Confirmed it still says "Both callers already have outer `except Exception` boundaries, so root-level `OSError` propagates naturally. ... each caller uses `report(prefix=…)`". This is exactly the wording Round 4 explicitly flagged as misleading at line 72. The Fail-Open Hook Policy design decision corrected the framing in one place, but the sibling Task 8 lead-in was never updated.
- **Plan line 1742** (self-review row 2): Confirmed it says "Tasks 7-8 (all three callers print `report()` on error)". This is **false at the root-level path** because `clean_stale_files` raises before returning a `CleanStaleResult`, so `report()` is never produced. At the root-level path, each caller's outer boundary prints its own wrapper-specific message (`"clean_stale_shakedown failed: …"`, `"containment-lifecycle: internal error (…)"`, `"containment_smoke_setup failed: …"`).
- **Plan line 1273-1279** (skipif on lifecycle subprocess test): Confirmed `@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() == 0, …)`. On root or Windows, the only automated proof of `main()`'s fail-open conversion through the caller boundary disappears.
- **Plan line 1001** (Task 7 Step 2 wrapper code): Confirmed `print(result.report(), file=sys.stderr)` is unconditional. Plan line 1030 confirms expected happy-path stderr is `clean_stale_files: removed=0, fresh=0`.
- **`containment_smoke_setup.py:505-510`**: Confirmed the `__main__` wrapper is fail-fast: `try: raise SystemExit(main()) except Exception as exc: print(f"containment_smoke_setup failed: {exc}", file=sys.stderr); raise SystemExit(1) from exc`. Genuinely different outer contract from lifecycle's fail-open.
- **`containment_smoke_setup.py:65` (`main()` signature)**: Confirmed `main(argv: list[str] | None = None) -> int` parses CLI args via argparse. The `prepare` subcommand requires `scenario_id` positional arg + optional `--session-id`, `--run-id`, `--delay-ms`. The parent parser requires `--data-dir` (or `CLAUDE_PLUGIN_DATA` env var) and `--repo-root`.
- **`containment_smoke_setup.py:244-261` (`_repo_paths()`)**: Confirmed it validates that B1 fixture files exist on disk: `contracts.md`, `delivery.md`, `foundations.md`, `mcp_server.py`, `dialogue.py`, `codex_guard.py`. Raises `RuntimeError("resolve repo paths failed: required B1 fixture paths missing. ...")` if any are absent. **This is what makes the smoke-setup subprocess test more involved than the lifecycle subprocess test** — it needs a valid `--repo-root` that points at the actual repo (with all B1 fixtures present).
- **`docs/tickets/closed-tickets/2026-02-15-plan-review-errata.md:439`**: Confirmed it says "MCP servers run as subprocesses with no stderr monitoring path. Fail-fast or nothing." The reviewer cross-referenced this as evidence that "repo history already treats stderr-only subprocess diagnostics as risky in adjacent contexts."

Also did a grep sweep for additional drift beyond the two lines the reviewer named:
- `propagates naturally` → 3 matches: line 72 (Round 4 callout, intentional), line 1136 (Task 8 lead-in, stale).
- `all three callers print` → 1 match at line 1742 (false claim).
- `unconditional` → 2 matches at line 1685 (self-review summary bullet) and line 1741 (self-review row 1) — both context-sensitive (technically accurate for current code, but change if Choice 3B picked).
- Architecture paragraph at line 17 → CORRECT, distinguishes per-file from root-level explicitly. This is the model the rewrites should match.

**Phase 3 — Drafted decision brief with three forced choices.**

Round 5 has design decisions baked into the resolution path, unlike Round 4 (where the fixes were unambiguous once the claims were verified). Three forced choices identified:

- **Choice 1 (smoke-setup root-failure gap, High):** Add a smoke-setup subprocess test (symmetric coverage) OR explicitly narrow the claim (faster but leaves the gap).
- **Choice 2 (platform gating, Medium):** Document the verification environment and accept the gap on root/Windows OR add a platform-agnostic in-process fallback OR both.
- **Choice 3 (wrapper noise, Medium):** Document the intentional unconditional stderr OR switch to error-only stderr (silent on success).

Plus a fourth decision point on the stderr monitoring path: accept the assumption with a note (Option 1) OR validate empirically before finalizing (Option 2) OR treat as unproven and add to risks (Option 3).

Drafted a comprehensive decision brief with verification evidence, proposed unambiguous fixes (with `[CONTINGENT]` placeholders for the choice-dependent wording), and recommendations: Choice 1A (add the test), Choice 2C (in-process fallback + subprocess, both kept), Choice 3B (silent wrapper), Stderr Option 1 (accept + note).

**Phase 4 — User approved package with one correction.**

User responded: *"I don't see a flaw in your reasoning. The package is directionally right."* and confirmed every choice as recommended.

But user pushed back on one specific implementation detail: *"For Choice 1A, I would avoid making the test depend on git when the repo-root relationship is already knowable from the test file location. That keeps the new coverage focused on the real coupling instead of adding another one."*

**Key pivot moment:** I had originally proposed deriving repo root via `subprocess.check_output(["git", "rev-parse", "--show-toplevel"])` in the smoke-setup subprocess test. User correctly pointed out this introduces a NEW coupling class (subprocess + git availability + git PATH + git repo state) when an existing coupling class (filesystem layout) was already in use via the existing `SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / ...` constant. The cleaner approach: extend the existing coupling one level deeper via `Path(__file__).resolve().parents[4]`.

Accepted the correction and noted the underlying principle in the response: **"prefer to deepen an existing dependency over to broaden the dependency surface."** Saved this as a methodology insight for future test design work.

**Phase 5 — Created task list and applied 26+ atomic edits top-down.**

Created 15 tracked tasks (one per logical edit group) and applied edits sequentially from line 64 to line 2056 of the plan, using the Edit tool for each atomic change:

1. **Line ~73:** Added stderr monitoring assumption paragraph to Fail-Open Hook Policy distinguishing hook-script stderr from MCP-server stderr precedent.
2. **Lines 110, 1748:** "four rounds" → "five rounds" in constraints header and resolution map header.
3. **Lines 132-133:** File structure rows updated for new test counts (lifecycle "2 → 3 tests", smoke-setup "1 → 2 tests").
4. **Lines 101-102:** In-scope descriptions updated to match.
5. **Line 1001:** Task 7 Step 2 wrapper code gated on `if result.had_errors:`. Prose updated to explain Unix-convention rationale.
6. **Line 1030, 1045:** Task 7 Step 4 + 5 expected stderr changed to *(empty)*.
7. **Line 1065, 1090:** Task 7 Step 6 + 7 diagnostic notes updated: regression-detection signal is now "stderr empty + exit=0" (with parenthetical note explaining the change).
8. **Line 1136:** **Task 8 lead-in fully rewritten** with two-error-surfaces framing + contract shape table (lifecycle fail-OPEN vs smoke-setup fail-FAST) + explicit "root-level raises don't go through `report()`" note + wiring tests paragraph mapping both surfaces.
9. **Line 1196 area:** Imports list updated: `import io`, `import json` added (with explanatory comment that `subprocess` and `sys` should already be present from `_run_lifecycle`).
10. **After line 1345:** **Appended `test_main_fail_open_conversion_via_monkeypatched_listdir`** (~120 lines) — platform-agnostic in-process fallback that calls `lifecycle.main()` directly with monkeypatched `os.listdir`, `sys.stdin`, and `CLAUDE_PLUGIN_DATA`. Wrapped in `with monkeypatch.context() as patched:` per constraint #6 (had to refactor after initial draft used direct `monkeypatch.setattr`).
11. **Line ~1351:** Task 8 Step 4 pytest invocation updated to run all 3 lifecycle tests; Expected text re-derived for the in-process fallback's no-skipif behavior.
12. **After line ~1362:** Task 8 Step 4 diagnostic paths extended with 5 new branches for the in-process fallback's failure modes (exit_code != 0, empty stderr from monkeypatch not taking effect, JSONDecodeError from stdin rigging not applied, `Path.glob()` bypass).
13. **Line ~1377:** Task 8 Step 5 imports updated: `import subprocess`, `import sys` added.
14. **After line ~1397:** **`_run_smoke_setup` subprocess helper added** — modeled on `_run_lifecycle`, deliberately omits `env=` since smoke-setup uses `--data-dir` for data directory override.
15. **After line ~1519:** **Appended `test_prepare_scenario_surfaces_cleanup_enumeration_failure`** (~120 lines) — subprocess test with real `chmod 0o000`, derives `repo_root` via `Path(__file__).resolve().parents[4]` (NOT git rev-parse per user correction), invokes via `_run_smoke_setup` with `--data-dir`, `--repo-root`, `prepare`, `scope_file_remove`, `--session-id`, `--run-id`. Asserts `returncode == 1`, stderr contains both `"containment_smoke_setup failed"` and `"cannot enumerate shakedown root"`.
16. **Line ~1530:** Task 8 Step 6 expected text updated to mention both tests and the chmod skipif behavior. Diagnostic paths extended with 6 new branches for the smoke-setup subprocess test (returncode 0 vs 1, missing wrapper prefix, missing Stage 3 context, B1 fixture missing, parents[N] index off, chmod restore failure).
17. **Lines 1577-1608:** Task 9 Step 1 test table +2 rows, baseline `535 → 537`, prose changed from "second test" to "**three** chmod tests share skipif", platform matrix re-derived: `537 / 534 / 536 / 533 / 534`.
18. **Line ~1700:** Task 9 Step 5 PR body baseline updated to match new platform matrix (`537 passed on macOS/Linux non-root; 534 + 3 skipped if root or Windows; 536 + 1 skipped if no symlink; 533 + 4 skipped in the intersection`).
19. **Line 1685:** Self-review summary bullet — "prints `report()` to stderr unconditionally (single-source context)" → "prints `report()` to stderr **only when `had_errors`** (Round 5 Choice 3B: silent on clean runs to preserve operator signal; loud on failure)".
20. **Line 1741:** Self-review row 1 — "Task 7 (wrapper logs unconditionally)" → "Task 7 (wrapper logs `report()` on `had_errors`, silent on clean runs per Round 5 Choice 3B)".
21. **Line 1742:** **Self-review row 2 fully rewritten** with explicit per-file vs root-level surface distinction, listing each caller's outer-boundary wrapper message verbatim, and pointing at the three Round 5 root-level tests.
22. **After Round 4 Low row:** **Six new Resolution Map rows added** — Round 5 High (smoke-setup gap), Round 5 Medium ×4 (Task 8 lead-in drift, self-review drift, stderr monitoring assumption, platform gating, wrapper noise). Note: I drafted "5 rows" but ended up adding 6 (the documentation drift was split into two separate rows since they're at different line locations).
23. **Line ~2035:** Three forced design decisions entry #3 (Fail-Open Hook Policy) updated to reference both lifecycle tests (subprocess + in-process fallback) AND the new smoke-setup subprocess test, plus the stderr monitoring note cross-reference.
24. **Line ~2046:** Type consistency rule extended to acknowledge the dotted-string monkeypatch form and the new `setattr("os.listdir", …)` + `setenv` + `setattr("sys.stdin", …)` triple.
25. **Line ~2055:** Risk verification — "Both chmod tests" → "All **three** chmod tests" with Round 5 additions.
26. **After existing risk verification bullets:** Added 3 new bullets for `_run_smoke_setup` helper (parallel pattern, deliberately no `env=`), in-process fallback platform-agnostic guarantee, and wrapper signal-to-noise change.

**Phase 6 — Final grep sweeps and verification.**

Ran six grep sweeps over the final plan to confirm no stale references survived:

1. `propagates naturally` — 3 hits, all intentional: line 72 (Round 4 callout), lines 2025 + 2030 (Resolution Map rows describing the prior problem).
2. `all three callers print` — 2 hits, both intentional: line 1150 (Round 5 fix sentence in Task 8 lead-in saying the prior wording is wrong), line 2031 (Resolution Map row quoting the prior false claim).
3. `four rounds | four review rounds` — 0 hits ✓
4. `unconditional | unconditionally` — 2 hits, both intentional: line 1093 (Step 7 diagnostic note providing context), line 2034 (Resolution Map row describing the prior wording).
5. `5\d\d passed` — All matches consistent: 519 (pre-T-03 baseline), 537 (new baseline), 534/536/533 (platform-conditional). No stale 535 anywhere.
6. `533 passed | 534 passed | 535 passed | 532 passed` — Only 533/534 matches in the NEW platform matrix and PR body; no stale 535 or 532.

Final line count: 2066 (up from 1793, +273 lines).

**Phase 7 — Committed the plan as a discrete `docs:` commit.**

User explicitly requested: "commit the plan file". Followed the standard commit protocol:
1. Ran `git status`, `git diff`, `git log --oneline -10` in parallel.
2. Confirmed plan was the only untracked file; tree was otherwise clean.
3. Drafted commit message matching the recent `docs(spec): add handoff no-commit refactor design` style: `docs(t-03): add stale-cleanup observability implementation plan`.
4. Staged the plan file by name (NOT `git add -A`) and committed via HEREDOC with the Co-Authored-By footer.
5. Verified post-commit with `git status`: working tree clean, branch 1 commit ahead of `origin/main`, commit hash `6e0f6820`.

Pre-commit hooks fired during the plan edit phase (allowing edits because we're on a `fix/*` branch per `.claude/rules/workflow/git.md`) rather than at commit time. The clean exit confirms `fix/t03-stale-cleanup-observability` is a recognized working branch pattern.

**Phase 8 — Produced final summary and waited for next-step direction.**

Summarized the Round 5 revision (table of all 26 edits, grep sweep results, line count delta) with three educational insights threaded through:
- The "find sibling sections" pattern (Round 5 surfaced that adding a design decision doesn't auto-update sibling sections — should grep for old framing across the whole document).
- The "deepen existing coupling vs broaden surface" principle (user's git rev-parse correction is a generalizable test design heuristic).
- The "in-process fallback for skip-gated tests" pattern (subprocess test is authoritative when supported; in-process fallback guarantees minimum coverage everywhere — neither replaces the other).

User then invoked `/handoff:save` with the message: "save a handoff. I will review the latest draft of the plan and then share my feedback with you in the next session." — confirming this is a wait-for-feedback handoff.

## Decisions

### Decision 1: User chose Choice 1A — add smoke-setup subprocess test (symmetric coverage)

**Choice:** Add `test_prepare_scenario_surfaces_cleanup_enumeration_failure` in `test_containment_smoke_setup.py` as a subprocess test with real `chmod 0o000`. Pin smoke-setup's fail-FAST `__main__` wrapper contract (exit 1, outer wrapper stderr prefix).

**Driver:** User: *"Choice 1: A, with one tweak. Add the smoke-setup subprocess test. I would not shell out to git rev-parse inside the test unless you need a fallback; prefer deriving the repo root from the test file path and documenting the B1-fixture coupling explicitly in the diagnostic notes. The asymmetry is real, and narrowing the claim would leave the strongest Round 5 finding unresolved."*

**Alternatives considered:**
- **Option B: Narrow the claim** (document scope, no new test) — would leave the High finding unresolved; reviewer's exact concern (a smoke-setup root-error regression can ship with every test green) would persist. Rejected because it accepts the gap rather than closing it.
- **Variant of Option A using `git rev-parse` for repo root** — initially proposed by me. Rejected per user correction: introduces a new dependency class (subprocess + git availability + git PATH + git repo state) when an existing coupling class (filesystem layout via `SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / ...`) was already in use. Cleaner to extend existing coupling via `parents[4]`.

**Implications:**
- Test framework is symmetric: lifecycle has subprocess test pinning fail-OPEN; smoke-setup has subprocess test pinning fail-FAST. Adjacent contracts, adjacent proofs.
- Three chmod tests now share the same skipif guard (was two): `test_clean_stale_files_raises_when_root_directory_unreadable` (Task 4), `test_subagent_start_surfaces_cleanup_enumeration_failure` (Task 8 lifecycle), `test_prepare_scenario_surfaces_cleanup_enumeration_failure` (Task 8 smoke-setup). All skip together on root or Windows.
- Baseline grew by 1 (537 instead of 536): +2 new tests total (smoke-setup subprocess + in-process fallback per Choice 2C), but the smoke-setup subprocess shares the skipif so platform-conditional counts re-derived.
- New `_run_smoke_setup` subprocess helper added in `test_containment_smoke_setup.py` — modeled on `_run_lifecycle` but deliberately omits `env=` because smoke-setup uses `--data-dir` for data directory override. Inherits parent environment unmodified.
- Test now couples to B1 fixture file existence (`contracts.md`, `delivery.md`, `foundations.md`, `mcp_server.py`, `dialogue.py`, `codex_guard.py`). Documented inline in test docstring and in Task 8 Step 6 diagnostic paths with recovery options.

**Trade-offs accepted:**
- Test depends on the B1 fixture files. If any is moved or renamed, the test breaks even if the cleanup wiring is still correct. Mitigated by an explicit diagnostic path and the principle that this coupling is the same class as the existing `SCRIPT` constant — a single coupling class, not two.
- Test setup is more involved than the lifecycle subprocess test (needs `--data-dir`, `--repo-root`, scenario id, session id, run id) because smoke-setup's CLI is more complex. Accepted because the symmetry is worth the boilerplate.

**Confidence:** High (E2) — empirically verified `containment_smoke_setup.py:65-104` (`main()` argv shape), `:244-261` (`_repo_paths()` validation), and `:505-510` (`__main__` fail-fast wrapper). Test design follows the existing `_run_lifecycle` + chmod + try/finally pattern from the lifecycle subprocess test.

**Reversibility:** High — test is in a new file (`test_containment_smoke_setup.py`) created by Task 8 Step 5; can be removed without affecting any production code.

**Change trigger:** If the smoke-setup script's `__main__` wrapper is intentionally redesigned (e.g., to fail-open), the test will fail with `returncode == 0` and should be updated to match the new contract — NOT bypassed.

### Decision 2: User chose Choice 2C — keep both subprocess test and add in-process fallback

**Choice:** Add `test_main_fail_open_conversion_via_monkeypatched_listdir` to `test_containment_lifecycle.py` as a platform-agnostic in-process fallback for the lifecycle fail-open conversion contract. Keep the existing subprocess chmod test as the authoritative end-to-end proof on supported platforms.

**Driver:** User: *"Choice 2: C. Keep the real subprocess lifecycle test for the true OS boundary on supported platforms, and add the in-process fallback so root/Windows still pin main()'s fail-open conversion. That closes the current 'all proof disappears under skip' weakness cleanly."*

**Alternatives considered:**
- **Option A: Document the verification environment** (accept the gap on root/Windows) — would leave the gap. Rejected because the in-process fallback is ~50 lines and closes the gap cleanly.
- **Option B: Replace the subprocess test with the in-process fallback** — would lose the real OS-level subprocess boundary proof. Rejected because the two tests prove different things (subprocess proves the OS boundary; in-process proves the language-level `main()` fail-open conversion).

**Implications:**
- Two complementary lifecycle tests. The subprocess test is the authoritative end-to-end proof when the platform supports it; the in-process test is the platform-agnostic minimum coverage. Neither replaces the other.
- The in-process fallback uses `monkeypatch.setattr("os.listdir", _raising_listdir)` + `monkeypatch.setenv("CLAUDE_PLUGIN_DATA", str(data_dir))` + `monkeypatch.setattr("sys.stdin", io.StringIO(payload_json))` to simulate the chmod failure without requiring real OS permissions. Wrapped in `with monkeypatch.context() as patched:` per constraint #6.
- Calls `lifecycle.main()` in-process via `_load_lifecycle_module()`, captures stderr via `capsys`, asserts on the return value (NOT `SystemExit`).
- Adds 1 to the baseline (537 instead of 536). No new skipif (always runs), so all platform-conditional counts include this test.

**Trade-offs accepted:**
- The in-process test cannot prove the REAL OS-level subprocess boundary including `argv` parsing, `sys.executable` resolution, and `SystemExit` handling. Accepted because the subprocess test still does that on supported platforms, and the in-process test only needs to prove the language-level conversion.
- The `os.listdir` monkeypatch depends on `containment.py` using `import os; os.listdir(...)` (attribute lookup at call time), not `from os import listdir` (reference captured at import time). If a future refactor changes the import style, the monkeypatch becomes a no-op. Mitigated by an explicit diagnostic path in Task 8 Step 4.
- Setting up `sys.stdin` via `io.StringIO` + `json.dumps` requires `import io` and `import json` in the test file. Both added to the verify-imports comment in Task 8 Step 3.

**Confidence:** High (E2) — verified the in-process pattern works because the existing `test_subagent_start_logs_cleanup_errors_with_lifecycle_prefix` already uses `_load_lifecycle_module()` + `capsys`. Adding `main()` instead of `_handle_subagent_start()` is the only structural change.

**Reversibility:** High — test is appended to `test_containment_lifecycle.py` after the existing subprocess test; can be removed without affecting any other test.

**Change trigger:** If `containment.py` adopts `from os import listdir` style imports (the monkeypatch becomes wrong), or if `lifecycle.main()` is refactored to read `sys.stdin` differently, or if pytest's `monkeypatch.context()` is removed in a future version.

### Decision 3: User chose Choice 3B — silent wrapper on success

**Choice:** Gate Task 7 Step 2's wrapper `print` call on `if result.had_errors:` so the wrapper is silent on clean runs and only prints on actual errors. Update Task 7 Step 4 + Step 5 expected stderr to *(empty)*. Update self-review bullets at lines 1685 and 1741 to reflect the gated behavior.

**Driver:** User: *"Choice 3: B. Make the wrapper silent on success and noisy on error. The current unconditional stderr path weakens the signal you are trying to strengthen."*

**Alternatives considered:**
- **Option A: Document the intentional unconditional stderr** — would keep the current behavior with a rationale. Rejected because the reviewer's exact concern (operators learn to discount cleanup stderr) is real.

**Implications:**
- Wrapper now matches Unix convention: silent on success, noisy on failure. Same as `rm`, `cp`, `trash`, etc.
- Wrapper now matches the internal callers' pattern: lifecycle and smoke-setup were already gated on `had_errors` via `_log_error` and `print` respectively.
- Task 7 Step 4 (happy path manual probe) and Step 5 (first-run path manual probe) expected stderr changed from `clean_stale_files: removed=0, fresh=0` to *(empty)*.
- Task 7 Step 6 (dangling symlink probe) and Step 7 (chmod 0o000 probe) diagnostic notes updated: regression-detection signal is now "stderr empty + exit=0" rather than "stderr contains `clean_stale_files: removed=0, fresh=0` + exit=0". Each diagnostic includes a parenthetical note explaining the change to give future-Claude context.
- Self-review bullet at line 1685 ("prints `report()` to stderr unconditionally (single-source context)") rewritten to mention `had_errors` gating + Round 5 Choice 3B reference.
- Self-review row 1 at line 1741 ("Task 7 (wrapper logs unconditionally)") rewritten to "Task 7 (wrapper logs `report()` on `had_errors`, silent on clean runs per Round 5 Choice 3B)".

**Trade-offs accepted:**
- Operators who rely on the wrapper's clean-run output to confirm the cleanup ran will now see nothing on success. Accepted because (a) operators can verify cleanup ran by checking the shakedown directory directly, (b) the wiring tests in Task 8 already prove the cleanup executed, (c) preserving the stderr signal is more valuable than the transparency.
- The change is small but ripples through 4 diagnostic notes and 2 self-review entries. All updates applied atomically.

**Confidence:** High (E2) — confirmed the change is a 2-line code modification (gate the print on `if result.had_errors:`) with cascading documentation updates. The Unix-convention argument is well-established.

**Reversibility:** High — flipping back to unconditional is a 1-line change. The cascading documentation updates would also need to revert.

**Change trigger:** If operational experience shows that operators rely on the clean-path stderr to confirm cleanup ran, OR if a CI/script integration breaks because it parsed the clean-path stderr.

### Decision 4: User chose Stderr Option 1 — accept the assumption with an explicit note

**Choice:** Add an assumption paragraph to the Fail-Open Hook Policy design decision distinguishing hook-script stderr from MCP-server stderr (per the errata at `docs/tickets/closed-tickets/2026-02-15-plan-review-errata.md:439`). Mark as accepted assumption for T-03; empirical validation is a potential follow-up outside scope.

**Driver:** User: *"Additional concern: include the note as Option 1 in the plan now. Distinguish hook-script stderr from MCP-server stderr explicitly and mark it as an accepted assumption for T-03. If you want extra confidence later, validate empirically, but I would not block this revision on that experiment."*

**Alternatives considered:**
- **Option 2: Validate empirically** (10-minute experiment) — would strengthen the design decision significantly. Rejected for this round because user said *"would not block this revision on that experiment"*. Possible follow-up.
- **Option 3: Treat as unproven and add to Open Questions/Risks** — would weaken the design decision. Rejected because the assumption is structurally sound (hook scripts run per-event, MCP servers are long-lived background processes — different observability models).

**Implications:**
- Added a new paragraph between the rationale bullets and the contract shape table in the Fail-Open Hook Policy design decision (~lines 73-75 of the new plan). The paragraph explicitly says: hook-script stderr is captured by Claude Code's hook runner (surfaced in session UI, logs, or aggregation pipelines depending on operator setup), while MCP servers are long-lived background subprocesses with no real monitoring path.
- The paragraph commits T-03 to this assumption being load-bearing AND commits that "if operational experience later shows hook stderr is being swallowed in practice, the correct fix is NOT to flip fail-open — it is to add a structured telemetry emission path orthogonal to stderr."
- Empirical validation is named as a potential follow-up "outside T-03's scope".
- The Fail-Open Hook Policy design decision entry in the self-review section was also updated to reference this note (entry #3 of "Three forced design decisions").

**Trade-offs accepted:**
- The assumption is unproven this session. If the user later discovers hook stderr is actually being swallowed, the entire fail-open policy needs to be revisited. Mitigated by the explicit "not by flipping fail-open, but by adding a telemetry path" guidance — future-Claude won't reach for the wrong fix.
- The note itself is ~10 lines of prose, adding mass to the design decision. Accepted because the distinction from the MCP errata precedent is non-obvious and worth documenting.

**Confidence:** Medium (E1) — the structural difference between hook scripts and MCP servers is clear, but I have not empirically tested whether hook stderr actually surfaces to operators in this codebase. The assumption is the user's call, not mine.

**Reversibility:** High — note is a single paragraph and can be removed or replaced.

**Change trigger:** If empirical testing shows hook stderr is being swallowed (operator runs into the failure mode and the stderr never surfaces), the design decision needs to be revisited.

### Decision 5: Used `Path(__file__).resolve().parents[4]` instead of `git rev-parse` for smoke-setup test repo root

**Choice:** Derive `repo_root` for the smoke-setup subprocess test from `Path(__file__).resolve().parents[4]` (the test file's location), NOT via `subprocess.check_output(["git", "rev-parse", "--show-toplevel"])`.

**Driver:** User correction: *"For Choice 1A, I would avoid making the test depend on git when the repo-root relationship is already knowable from the test file location. That keeps the new coverage focused on the real coupling instead of adding another one."*

**Alternatives considered:**
- **`git rev-parse --show-toplevel`** — initially proposed by me. Rejected because it introduces a new coupling class (subprocess + git availability + git PATH + git repo state) when an existing coupling class (filesystem layout) was already in use via the existing `SCRIPT` constant.
- **Hardcoded absolute path** — would couple to a specific developer's machine. Rejected.
- **Environment variable like `REPO_ROOT`** — would require test setup to set the variable. Rejected for unnecessary indirection.

**Implications:**
- Test now derives `repo_root = Path(__file__).resolve().parents[4]`. The path walks: `tests/test_containment_smoke_setup.py → tests → codex-collaboration → plugins → packages → repo_root`. Five `parent` traversals, indexed as `parents[4]`.
- The same coupling class as the existing `SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "containment_smoke_setup.py"` constant. Both rely on the test file being at a known location relative to the script and the repo root.
- If the test file is moved within the repo, BOTH the `SCRIPT` constant and the `parents[4]` derivation break together — they fail in the same way at the same time. This is "fail loudly together" coupling, which is easier to debug than "two independent failure modes that both need to be fixed."
- Documented inline in the test docstring with the explicit reasoning (deepen existing coupling vs broaden surface), plus a diagnostic path in Task 8 Step 6 explaining how to recompute the `parents[N]` index if the test file moves.

**Trade-offs accepted:**
- The test breaks if the test file is moved within the repo. Accepted because (a) moving test files is rare, (b) the failure mode is loud and clear (`Path(__file__).resolve().parents[4]` returns the wrong path, `_repo_paths()` raises `RuntimeError("resolve repo paths failed: ...")`), (c) the diagnostic path explains the recovery procedure.

**Confidence:** High (E2) — verified the directory depth by counting from the test file location. The principle (deepen existing coupling) is generalizable beyond this test.

**Reversibility:** High — switching to `git rev-parse` would require changing one line in the test plus removing the `Path(__file__).resolve().parents[4]` documentation.

**Change trigger:** If the test file is moved within the repo, OR if the test framework changes such that `__file__` becomes unreliable (e.g., in-memory test loading without filesystem paths).

### Decision 6: Committed the plan as a standalone `docs(t-03):` commit, not folded into Task 1

**Choice:** Created commit `6e0f6820` with subject `docs(t-03): add stale-cleanup observability implementation plan` containing only the plan file. The plan file was untracked in git at session start (`??` status) and was committed as a discrete commit before any code changes.

**Driver:** Plan went through five adversarial review rounds across three working sessions before any implementation. The Round 4 handoff explicitly flagged this as an open question for Round 5: *"Plan commit timing undefined — separate commit vs. fold into Task 1."* User did not resolve the question this session, but explicitly requested *"commit the plan file"* — and a standalone commit was the cleaner default.

**Alternatives considered:**
- **Fold the plan into Task 1's commit** — established convention for prior plans in this repo. Rejected because (a) this plan's review history is unusually deep, (b) folding conflates "this is the plan" with "this is the first implementation slice", (c) a separate commit creates a clean ancestor that implementation commits can reference.
- **Wait until execution starts** — would leave the plan untracked indefinitely. Rejected because user explicitly said "commit the plan file".

**Implications:**
- The plan is now discoverable via `git log` and `git blame` as its own commit. Reviewers can `git log -p docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` to see the full history.
- The branch is now 1 commit ahead of `origin/main`. Pushing requires `git push -u origin fix/t03-stale-cleanup-observability`.
- Implementation commits (Tasks 1-8) will reference the plan via commit-message body or PR description, not via co-located commit. This is the same pattern as `f953e253 docs(spec): add handoff no-commit refactor design` from the recent commit log.
- Pre-commit hooks ran silently — no output means they passed. The branch-protection hook in this repo fires on `Edit`/`Write` events, not on `git commit` itself, so it had already run during the plan edits and approved them (because `fix/t03-stale-cleanup-observability` is a recognized working branch pattern per `.claude/rules/workflow/git.md`).

**Trade-offs accepted:**
- One extra commit in the branch history (8 implementation commits + 1 plan commit = 9 total) instead of 8. Negligible cost.
- The plan commit is local-only until pushed. If pushed, GitHub PR will show 9 commits. The PR body in Task 9 Step 5 doesn't currently mention the plan commit explicitly — may want to add a note in the PR body that one of the commits is the plan itself.

**Confidence:** High (E2) — followed the standard commit protocol from CLAUDE.md, used HEREDOC for the message, included Co-Authored-By footer, verified post-commit with `git status`. All hooks passed.

**Reversibility:** Low — squashing the plan commit into Task 1 later would require an interactive rebase, which the user rules forbid (`-i` flag explicitly disallowed). The commit is durable.

**Change trigger:** If the user later decides the plan commit should be squashed into Task 1, they would need to do it manually. The commit is in the local branch only — has not been pushed yet.

## Changes

### `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` — Sixth draft (2066 lines, up from 1793)

**Purpose:** Sixth draft of the T-03 implementation plan, addressing all six Round 5 findings (1 High + 4 Medium + 1 Assumption Note) without invalidating any prior Round 1-4 fix.

**Approach:** 26+ targeted edits via the Edit tool, applied top-down through the plan from line 64 (Fail-Open Hook Policy stderr note) through line 2056 (final risk verification bullet). Each edit was atomic and preserved surrounding text verbatim. No section was rewritten from scratch — additions were additive, replacements were minimal.

**Key implementation details added (categorized by which Round 5 finding they address):**

*High finding (smoke-setup root-failure gap):*
- `_run_smoke_setup` subprocess helper added to `test_containment_smoke_setup.py` template (modeled on `_run_lifecycle`, deliberately omits `env=`)
- `test_prepare_scenario_surfaces_cleanup_enumeration_failure` (~120 lines) appended to Task 8 Step 5 — subprocess test with real `chmod 0o000`, derives repo_root via `Path(__file__).resolve().parents[4]`, asserts `returncode == 1` + `"containment_smoke_setup failed"` + `"cannot enumerate shakedown root"` in stderr
- 6 new diagnostic paths in Task 8 Step 6 covering the new test's failure modes (returncode 0, missing wrapper prefix, missing Stage 3 context, B1 fixture missing, `parents[N]` index off, chmod restore failure)
- Resolution Map row documenting the gap and the resolution

*Medium findings (documentation drift, lines 1136 + 1742):*
- Task 8 lead-in fully rewritten to distinguish two error surfaces (per-file `had_errors` → `report(prefix=…)` vs root-level raise → caller's outer exception boundary). Added contract shape table showing the two different boundary contracts (lifecycle fail-OPEN at `main()` lines 184-188 vs smoke-setup fail-FAST at `__main__` lines 505-510). Added explicit "Root-level raises do not go through `report(prefix=…)`" sentence.
- Self-review row 2 fully rewritten with the same per-file vs root-level surface distinction, listing each caller's outer-boundary wrapper message verbatim, and pointing at the three Round 5 root-level tests.
- Two Resolution Map rows (one per drift instance) documenting both findings.

*Medium finding (platform gating):*
- `test_main_fail_open_conversion_via_monkeypatched_listdir` (~120 lines) appended to Task 8 Step 3 — platform-agnostic in-process fallback that calls `lifecycle.main()` directly with monkeypatched `os.listdir`, `sys.stdin`, and `CLAUDE_PLUGIN_DATA`. Wrapped in `with monkeypatch.context() as patched:` per constraint #6.
- `import io`, `import json` added to Task 8 Step 3 imports verify-list (with explanatory comment about which were already present from `_run_lifecycle`).
- 5 new diagnostic paths in Task 8 Step 4 covering the in-process fallback's failure modes (exit_code != 0, empty stderr from monkeypatch not taking effect, JSONDecodeError from stdin rigging, `Path.glob()` bypass).
- Task 8 Step 4 pytest invocation updated to run all 3 lifecycle tests; Expected text re-derived for the in-process fallback's no-skipif behavior.
- Resolution Map row documenting the gap and the resolution.

*Medium finding (wrapper signal-to-noise):*
- Task 7 Step 2 wrapper code: `print(result.report(), file=sys.stderr)` → `if result.had_errors: print(result.report(), file=sys.stderr)`
- Task 7 Step 2 prose updated with rationale (Unix convention, preserves operator signal)
- Task 7 Step 4 + Step 5 expected stderr changed from `clean_stale_files: removed=0, fresh=0` to *(empty — wrapper is silent on clean runs per Choice 3B, Round 5)*
- Task 7 Step 6 + Step 7 diagnostic notes updated: regression signal is now "stderr empty + exit=0" with parenthetical context about the change
- Self-review summary bullet at line 1685 updated to remove "unconditionally" and add the gating + Round 5 Choice 3B reference
- Self-review row 1 at line 1741 updated similarly
- Resolution Map row documenting the change

*Assumption note (stderr monitoring path):*
- New paragraph added between rationale bullets and contract shape table in Fail-Open Hook Policy design decision (~line 73-75): explicit assumption note distinguishing hook-script stderr from MCP-server stderr precedent at `docs/tickets/closed-tickets/2026-02-15-plan-review-errata.md:439`. Commits T-03 to "if operational experience later shows hook stderr is being swallowed in practice, the correct fix is NOT to flip fail-open — it is to add a structured telemetry emission path orthogonal to stderr."
- Three forced design decisions entry #3 updated to reference the note + the cross-reference URL
- Resolution Map row documenting the assumption

*Bookkeeping:*
- "four rounds" → "five rounds" in constraints header (line 110) and resolution map header (line 1748)
- File structure rows updated for new test counts: lifecycle "2 → 3 tests", smoke-setup "1 → 2 tests"
- In-scope descriptions in Scope Notes updated to match
- Task 9 Step 1 baseline: 535 → 537. Platform matrix re-derived (537/534/536/533/534) with 3 chmod tests sharing the skipif. Expected new test count: 18 (was 16).
- Task 9 Step 5 PR body baseline updated to match
- Risk verification "Both chmod tests" → "All **three** chmod tests"; 3 new bullets added for the Round 5 changes
- Type consistency rule extended to acknowledge the dotted-string monkeypatch form

**Design choices:**
- Insertions over rewrites wherever possible to preserve prior-round context that reviewers can re-check
- Explicit Round 5 references in many of the updated paragraphs (e.g., "per Round 5 Choice 3B", "Round 5 resolution") so future readers can trace which round introduced each change
- The Resolution Map now has 17+ findings spanning five rounds, making it the canonical "what has been considered" index
- All Python test code uses `with monkeypatch.context() as patched:` per constraint #6 — refactored the in-process fallback test after initial draft to comply

**Future-Claude note:** The plan is now committed (`6e0f6820`). The branch is 1 commit ahead of `origin/main`. Pushing is optional and depends on whether the user wants the plan visible on GitHub before execution starts. The plan commit does NOT contain any code changes — implementation commits will follow during execution.

## Codebase Knowledge

### Files Read During Session

| File | Why Read | What Was Found |
|------|----------|----------------|
| `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` | Verify Round 5 line citations + plan all 26 edits | 1793 lines (fifth draft). Architecture paragraph (line 17) is correct and serves as the model for downstream rewrites. Task 8 lead-in (line 1136) and self-review row 2 (line 1742) are the two stale drift points. Three forced design decisions in self-review at line 1768. Resolution Map at lines 1746+. Risk verification bullets at lines 1788+. |
| `packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py` (lines 65-110) | Verify `main()` argv shape for the new subprocess test | `def main(argv: list[str] | None = None) -> int` at line 65. Uses argparse with subparsers `prepare` and `cleanup`. `prepare` requires `scenario_id` positional + optional `--session-id`, `--run-id`, `--delay-ms`. Parent parser requires `--data-dir` (or `CLAUDE_PLUGIN_DATA` env var) and `--repo-root`. `prepare` calls `_repo_paths(args.repo_root)` which validates B1 fixture file existence — BEFORE `prepare_scenario` runs. |
| `packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py` (lines 234-270) | Verify `_resolve_data_dir` and `_repo_paths` validation | `_resolve_data_dir` at line 234 raises `RuntimeError("resolve data dir failed: set --data-dir or CLAUDE_PLUGIN_DATA. ...")` if neither is set. `_repo_paths` at line 244 builds a `RepoPaths` dataclass with six file paths (contracts, delivery, foundations, mcp_server, dialogue, out_of_scope) all derived from `repo_root`. Then validates: `missing = [str(path) for path in paths.__dict__.values() if isinstance(path, Path) and not path.exists()]`. If any are missing, raises `RuntimeError("resolve repo paths failed: required B1 fixture paths missing. ...")`. |
| `packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py` (lines 490-510) | Verify the `__main__` wrapper outer boundary | `_scenario_definition` at line 364, "unknown scenario_id" RuntimeError at lines 494-497. `__main__` block at lines 505-510: `try: raise SystemExit(main()) except Exception as exc: print(f"containment_smoke_setup failed: {exc}", file=sys.stderr); raise SystemExit(1) from exc`. **Confirmed fail-FAST contract, structurally different from lifecycle's fail-OPEN.** |
| `docs/tickets/closed-tickets/2026-02-15-plan-review-errata.md` (lines 425-455) | Verify the stderr-monitoring-path errata cross-reference | Section discusses `MAX_CONVERSATIONS` cap for MCP server. "Resolved: Hybrid — Option B (defer eviction) + fail-fast guard." Line 439: "Warning-only logging rejected: MCP servers run as subprocesses with no stderr monitoring path. Fail-fast or nothing." This is the precedent the reviewer cross-referenced — explicit prior decision against stderr-only logging in MCP server context. |
| `packages/plugins/handoff/skills/save/synthesis-guide.md` | Required reading per `/handoff:save` skill before drafting handoff | Synthesis prompts for all 13 sections with depth targets and templates. Evidence requirements (file:line, quote, output). Output Mapping table linking synthesis prompts to handoff sections. Completeness Self-Check at the end. |
| `packages/plugins/handoff/references/format-reference.md` | Required reading per skill | Frontmatter schema, section checklist (13 required), depth targets, two example handoffs (new session ~300 lines, resumed session ~150 lines), checkpoint format. |
| `packages/plugins/handoff/references/handoff-contract.md` | Required reading for chain protocol | Frontmatter schema, chain protocol (load writes state, save reads + cleans), storage locations, git tracking model (local-only working memory), known limitations. |
| `docs/handoffs/.session-state/handoff-be296122-8956-4559-98e9-dd67b77a416f` | Get `resumed_from` path for chain protocol | Single line: path to the Round 4 archived handoff at `docs/handoffs/archive/2026-04-11_00-46_t-03-plan-round-4-fail-open-policy-and-decoupled-tests.md`. |

### Architecture: T-03 Affected Layers (post-Round 5)

| Layer | File | Round 5 Status |
|-------|------|----------------|
| Core helper | `server/containment.py:290-310` | Unchanged from Round 4. `clean_stale_files` returns `CleanStaleResult` with three-stage failure check. |
| CLI wrapper | `scripts/clean_stale_shakedown.py` | **Round 5 change:** Task 7 Step 2 wrapper code now gates `print(result.report(), file=sys.stderr)` on `if result.had_errors:` (Choice 3B). Outer `try/except Exception` at lines 44-52 unchanged — still catches root-level raises and exits 1 with `"clean_stale_shakedown failed: unexpected error. ..."`. |
| Hook handler | `scripts/containment_lifecycle.py:73` | Unchanged from Round 4. Calls `clean_stale_files`, captures result, `_log_error(result.report(prefix="containment-lifecycle: "))` on `had_errors`. Outer `main()` boundary at lines 184-188 unchanged — still fail-OPEN with `return 0`. |
| Smoke-setup | `scripts/containment_smoke_setup.py:118` | Unchanged from Round 4. Calls `clean_stale_files`, captures result, `print(result.report(prefix="containment_smoke_setup: "), file=sys.stderr)` on `had_errors`. Outer `__main__` wrapper at lines 505-510 unchanged — still fail-FAST with exit 1. |

### Key Locations Mapped

| Concept | Location |
|---------|----------|
| Plan file | `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` (now 2066 lines) |
| Plan commit | `6e0f6820` on `fix/t03-stale-cleanup-observability` |
| Architecture paragraph (the "model" for rewrites) | Plan line 17 |
| Fail-Open Hook Policy design decision | Plan lines 64-89 (now ~lines 64-95 with stderr note) |
| Stderr monitoring assumption note (NEW) | Plan ~line 73-75 |
| Constraint #11 (locks fail-open) | Plan line ~119 |
| Task 7 Step 2 wrapper code (now gated) | Plan line 1001 |
| Task 8 lead-in (NEW two-surface framing + contract shape table) | Plan line 1136+ |
| Task 8 Step 3 lifecycle test code block | Plan line ~1208-1345 (3 tests now: per-file in-process, subprocess chmod, in-process fallback) |
| Task 8 Step 5 smoke-setup test code block | Plan line ~1364-1525 (2 tests now: per-file direct seam, subprocess chmod) |
| `_run_smoke_setup` subprocess helper (NEW) | Plan line ~1397-1415 in Task 8 Step 5 template |
| Resolution Map | Plan line 1748+ (now 17+ rows across 5 rounds) |
| Three forced design decisions self-review entry | Plan line 2031+ |
| Risk verification bullets | Plan line 2048+ |
| `containment_smoke_setup.py:_repo_paths` | `scripts/containment_smoke_setup.py:244-261` |
| `containment_smoke_setup.py:__main__` fail-FAST wrapper | `scripts/containment_smoke_setup.py:505-510` |
| Errata cross-reference | `docs/tickets/closed-tickets/2026-02-15-plan-review-errata.md:439` |
| Prior handoff (resumed from) | `docs/handoffs/archive/2026-04-11_00-46_t-03-plan-round-4-fail-open-policy-and-decoupled-tests.md` |

### Patterns Identified This Session

- **The "find sibling sections" pattern:** When a design decision is added (Round 4's Fail-Open Hook Policy), the corrected framing lives in the decision subsection, but pre-existing prose in sibling sections doesn't auto-update. Round 5's two doc-drift findings (Task 8 lead-in + self-review row 2) are both instances of this pattern. Mitigation: after adding a design decision, do `rg <old-framing>` across the whole document and update every match.
- **The "deepen existing coupling" principle:** When a test already has a filesystem-layout assumption (the existing `SCRIPT` constant), extending that same assumption one level deeper (to repo root) stays within the same coupling class. Adding `git rev-parse` would have introduced a new coupling class. Generalizable test design heuristic.
- **The "in-process fallback for skip-gated tests" pattern:** When a subprocess test depends on platform behavior that only some platforms support (chmod 0o000 requires non-root POSIX), add a parallel in-process test that simulates the same failure via monkeypatching. The two tests prove different things (subprocess proves the OS-level boundary, in-process proves the language-level boundary), so neither replaces the other. They're complementary belt-and-suspenders.
- **Two error surfaces, two contract shapes:** Helper raises (root-level) vs helper returns with `had_errors=True` (per-file) are two distinct surfaces. Each caller has an outer exception boundary that catches root-level raises. The boundaries have two contract shapes: lifecycle = fail-OPEN (exit 0 + log to stderr), wrapper + smoke-setup = fail-FAST (exit 1 + print to stderr). Three callers, two contract shapes — not three.
- **Contract shape table format:** The Round 5 Task 8 lead-in rewrite uses a markdown table with columns Caller, Outer boundary, stderr wrapper, Exit code, Intent. This format works well for documenting boundary contracts at a glance — adopted from the existing Fail-Open Hook Policy contract shape table at line 76-83.

### Conventions Observed This Session

- **Plan line-anchored references:** Edits use line numbers for navigation (e.g., "line 1136", "line 1742") but the actual line numbers shift as edits accumulate. The original line numbers in this session's notes refer to the pre-Round-5 state (1793 lines). After all edits, the same content is at different line numbers (~1136 → ~1150, ~1742 → ~1932 etc.) Use `Grep` for the canonical text rather than line numbers when verifying.
- **Edit-tool atomicity:** Each Edit call has unique `old_string` content; using `replace_all=true` only when the same text appears in multiple places (e.g., "Expected stderr: `clean_stale_files: removed=0, fresh=0`" was identical in Step 4 and Step 5).
- **Commit message style:** `<type>(<scope>): <subject>` per recent commit log. Used `docs(t-03):` matching the precedent of `docs(spec):` from `f953e253`.
- **Plan review feedback format:** User uses structured headers (Premise Check, Critical Failures, High-Risk Assumptions, Real-World Breakpoints, Hidden Dependencies, Adversarial Perspectives, Patterns And Root Causes, Required Changes, Verdict). Verdict has been Reject (Round 3), Minor revision (Rounds 4-5).

### Surprising Findings

- **Smoke-setup `prepare` command has more validation than I expected.** `_repo_paths()` validates that 6 specific B1 fixture files exist on disk. This is what makes the smoke-setup subprocess test more involved than the lifecycle test — you can't just run `containment_smoke_setup.py prepare scope_file_remove`; you need a valid `--repo-root` that points at a directory with all six fixture files present.
- **`_repo_paths()` runs BEFORE `prepare_scenario` runs.** So the chmod test must have a valid repo root even though the test never actually uses any of the fixture files (it raises in Stage 3 of `clean_stale_files` before reaching the scenario logic). The repo-root requirement is upstream of the failure, not coupled to it.
- **`time.monotonic()` is not the issue here, unlike in the previous session.** The Round 4 handoff mentioned that monotonic timestamps are process-local, but that's relevant for the rate-limiting example in the format-reference.md, not for this codebase.
- **Pre-commit hooks fired during Edit operations, not at commit time.** Per `.claude/rules/workflow/git.md`, the branch-protection PreToolUse hook checks the current branch on `Edit`/`Write` events. Since `fix/t03-stale-cleanup-observability` is a recognized working branch pattern (`fix/*`), the hook approved the edits silently. By the time `git commit` ran, no further hook checks were needed.

## Context

### Mental Model

**Framing:** This is a coverage-symmetry and summary-drift problem, not an algorithm problem.

The core algorithm has been settled since Round 3. The boundary policy was settled in Round 4. Round 5 found that the FIVE places where the plan describes the boundaries do not all describe them correctly:
- The architecture paragraph at line 17: CORRECT (distinguishes per-file from root-level explicitly)
- The Fail-Open Hook Policy design decision at lines 64-89: CORRECT
- Task 8 lead-in at line 1136: STALE (still says "propagates naturally")
- Self-review row 2 at line 1742: STALE (still says "all three callers print report() on error")
- Resolution Map: CORRECT (describes the Round 4 fix)

Two of five descriptions were stale. The Round 5 fixes propagated the correct framing to those two locations. The "find sibling sections" pattern (a fix in one place doesn't auto-update sibling places that discuss the same concept) is itself a learning worth flagging.

**Core insight:** The remaining risk after Round 4 was not algorithm correctness — it was symmetry of test coverage and accuracy of summary language. Round 5 closes both: adds the missing smoke-setup root-failure test (symmetry), and rewrites the two stale paragraphs (accuracy).

**Mental model:** "Three callers, two contract shapes." Lifecycle is fail-OPEN. Wrapper and smoke-setup are both fail-FAST. The plan needs to consistently distinguish these throughout — both the per-file vs root-level error surfaces AND the fail-open vs fail-fast outer boundary contracts.

### Review Round Progression (now 5 rounds)

| Round | Verdict | Key Finding | Resolution Pattern |
|-------|---------|-------------|---------------------|
| 1 | (first draft) | P1: root `exists()` swallows; P2: count-only reports; P2: monkeypatch breaks `.exists()`; P3: `rm -rf` violates CLAUDE.md | Two-stage lstat/stat check, `report()` with path+error_repr, scoped `monkeypatch.context()`, switch to `trash` |
| 2 | (second draft) | P2: dangling symlink root collapses; P2: smoke-setup wiring not testable; P3: multi-line reports lose attribution | Two-stage check catches dangling symlinks, created `test_containment_smoke_setup.py`, `report(prefix=...)` applies to every line |
| 3 | Reject | **Critical:** `Path.glob()` silently returns `[]`; **High:** no enumeration-failure test | Stage 3 (`os.listdir` + `fnmatch`), two enumeration-failure tests, test count bookkeeping |
| 4 | Minor revision | **High:** lifecycle fail-open implicit; **Medium:** smoke-setup test overfitted; **Medium:** no root-level caller test; **Low:** eager scan unstated | Explicit Fail-Open Hook Policy + constraint #11, monkeypatch `_scenario_definition` direct seam, subprocess root-level test, inline scale tradeoff note |
| 5 | Minor revision | **High:** smoke-setup root-failure gap; **Medium ×2:** doc drift (Task 8 lead-in + self-review row 2); **Medium:** platform gating; **Medium:** wrapper noise; **Assumption:** stderr monitoring path | Smoke-setup subprocess test (Choice 1A), in-process fallback (Choice 2C), wrapper silent on success (Choice 3B), stderr monitoring assumption note (Option 1), 6 Resolution Map rows |

### Environment State

- **Working directory:** `/Users/jp/Projects/active/claude-code-tool-dev`
- **Branch:** `fix/t03-stale-cleanup-observability` (based on `origin/main` at `fd7c9365` originally; now 1 commit ahead with `6e0f6820`)
- **Git state:** Clean working tree. Plan is now committed (was untracked at session start).
- **Current commit:** `6e0f6820` — `docs(t-03): add stale-cleanup observability implementation plan` (the new commit from this session)
- **Previous commit:** `fd7c9365` — merge commit from PR #102 (T-04 wrapper fix)
- **Plan file state:** Sixth draft, 2066 lines, committed locally, NOT pushed to remote
- **No code changes** to `containment.py`, scripts, or tests yet — the plan documents future changes but none have been applied

### Project State

T-03 is the next ticket in the correctness hardening arc for codex-collaboration. Status:
- **T-04 (PR #102, merged in second-prior session):** `scripts/clean_stale_shakedown.py` wrapper script convention fixes — script path handling, `CLAUDE_PLUGIN_DATA` validation. This is the CLI wrapper that calls `clean_stale_files`.
- **T-03 (this session, fifth review round complete):** `server/containment.py:clean_stale_files` hardening plan ready for execution. Sixth draft committed as `6e0f6820`. Waiting for user feedback (potential Round 6) or execution approval.

After T-03 ships, the next expected ticket is T-02 or similar (the `read_active_run_id` / `read_json_file` lenient helpers migration) — but that's explicitly out of scope for this plan per the scope notes.

## Conversation Highlights

**User's verdict on the package proposal:**
*"I don't see a flaw in your reasoning. The package is directionally right."*
— Green light for the recommended choices.

**User's Choice 1 direction with the key correction:**
*"Choice 1: A, with one tweak. Add the smoke-setup subprocess test. I would not shell out to git rev-parse inside the test unless you need a fallback; prefer deriving the repo root from the test file path and documenting the B1-fixture coupling explicitly in the diagnostic notes. The asymmetry is real, and narrowing the claim would leave the strongest Round 5 finding unresolved."*
— Drove the `Path(__file__).resolve().parents[4]` decision.

**User's Choice 2 direction:**
*"Choice 2: C. Keep the real subprocess lifecycle test for the true OS boundary on supported platforms, and add the in-process fallback so root/Windows still pin main()'s fail-open conversion. That closes the current 'all proof disappears under skip' weakness cleanly."*
— Drove keeping both tests rather than replacing one with the other.

**User's Choice 3 direction:**
*"Choice 3: B. Make the wrapper silent on success and noisy on error. The current unconditional stderr path weakens the signal you are trying to strengthen."*
— Drove the wrapper gating decision.

**User's stderr monitoring direction:**
*"Additional concern: include the note as Option 1 in the plan now. Distinguish hook-script stderr from MCP-server stderr explicitly and mark it as an accepted assumption for T-03. If you want extra confidence later, validate empirically, but I would not block this revision on that experiment."*
— Drove adding the assumption note without empirical validation.

**User's green light for the package:**
*"Green light: yes. Apply the two pure drift fixes, then update the context-sensitive rows to match Choice 3, add the new Round 5 resolution rows, and re-derive the test-count/platform matrix after the new tests are in."*
— Approval to apply all edits.

**User's correction on git rev-parse (this is the key methodological insight):**
*"One correction to your preferred package: for Choice 1A, I would avoid making the test depend on git when the repo-root relationship is already knowable from the test file location. That keeps the new coverage focused on the real coupling instead of adding another one. Thoughts on this?"*
— This is the "deepen existing coupling vs broaden surface" principle stated explicitly. I responded by accepting the correction and noting the underlying principle.

**User's wait-for-feedback direction:**
*"save a handoff. I will review the latest draft of the plan and then share my feedback with you in the next session."*
— Confirms this is a pause-for-review handoff. A potential Round 6 is possible.

**User's commit direction:**
*"commit the plan file"*
— Brief, direct. I followed the standard commit protocol and committed as a discrete `docs(t-03):` commit.

## Learnings

### The "find sibling sections" pattern is now load-bearing for iteratively-reviewed documents

**Mechanism:** When a design decision is added (e.g., Round 4's Fail-Open Hook Policy), the corrected framing lives in the decision subsection but pre-existing prose in sibling sections that discuss the same concept doesn't automatically update. The fix corrects the description in one place; the description elsewhere still uses the old (now-misleading) wording. Future reviewers can find both the corrected version and the stale version, and the reviewer's quality assessment depends on which one they read first.

**Evidence:** Round 5's two Medium documentation-drift findings are both instances of this pattern. Plan line 72 (Round 4 callout) explicitly says the "naturally propagates" language was misleading, but line 1136 (Task 8 lead-in) still uses it. Plan line 17 (architecture paragraph) correctly distinguishes per-file from root-level, but line 1742 (self-review row 2) still says "all three callers print `report()` on error". Two cheap greps (`rg "propagates naturally"`, `rg "all three callers print"`) would have caught both before submission.

**Implication:** Any plan that goes through 3+ review rounds should adopt the "after a fix, grep for the old framing across the whole document" rule. Cost: 5 seconds. Benefit: prevents an entire review round devoted to drift cleanup.

**Watch for:** Other instruction documents (skill SKILL.md files, agent definitions, contracts) where a fix in one section may not propagate to sibling sections. The same pattern applies anywhere a concept is described in multiple places.

### Deepening an existing coupling is preferable to broadening the dependency surface

**Mechanism:** Tests often have implicit couplings (filesystem layout, environment variables, available binaries). When extending a test, the natural temptation is to add new dependencies (e.g., `git rev-parse` for repo root). But each new dependency adds a new failure class — the test can now fail in additional ways unrelated to the contract under test. The cleaner approach is to extend an existing coupling: if the test already couples to filesystem layout via one path, derive the new path from the same starting point.

**Evidence:** User correction on Choice 1A. I proposed `subprocess.check_output(["git", "rev-parse", "--show-toplevel"])` for repo root. User: *"I would avoid making the test depend on git when the repo-root relationship is already knowable from the test file location. That keeps the new coverage focused on the real coupling instead of adding another one."* The existing `SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / ...` constant already coupled to filesystem layout. Extending via `Path(__file__).resolve().parents[4]` stays within the same coupling class.

**Implication:** When designing test infrastructure, prefer to derive new path/state from existing coupling points. Adding new dependencies (subprocess, env var, network, git, etc.) should be a deliberate choice with explicit justification, not the default. The test's failure modes are easier to reason about when they're concentrated in one coupling class.

**Watch for:** Tests that introduce `subprocess.run([...])` calls for setup tasks where a Python-native equivalent exists. Tests that use environment variables when test arguments would do. Tests that assume git availability when the path information is already in `__file__`.

### Two complementary tests can prove different things — neither replaces the other

**Mechanism:** Skip-gated subprocess tests (e.g., chmod 0o000 + non-root POSIX) lose coverage on excluded platforms. The conventional response is to skip and accept the gap. The alternative — adding a parallel in-process test that simulates the same failure via monkeypatching — gives "best when available, minimum guaranteed coverage everywhere". The subprocess test proves the OS-level boundary (real chmod, real subprocess, real `SystemExit`); the in-process test proves the language-level boundary (`main()`'s exception-to-return-code conversion). They prove different things.

**Evidence:** Round 5 Choice 2C: kept the existing `test_subagent_start_surfaces_cleanup_enumeration_failure` (subprocess + chmod, skips on root/Windows) AND added `test_main_fail_open_conversion_via_monkeypatched_listdir` (in-process + monkeypatched os.listdir, runs on every platform). The subprocess test is the authoritative end-to-end proof when supported; the in-process test guarantees that the language-level conversion contract is pinned even when the subprocess test skips.

**Implication:** For any test that uses real OS-level features but pins a language-level contract, consider whether a complementary in-process test can pin the same contract via monkeypatching. The two tests together provide belt-and-suspenders coverage. This is especially valuable for Windows CI where many POSIX-isms unconditionally skip.

**Watch for:** Other tests in the codebase that skip-gate on platform features. Each is a candidate for an in-process complementary test if the contract under test can be expressed at the language level.

### Resolution maps are the canonical "what has been considered" index for iteratively-reviewed documents

**Mechanism:** As a plan grows through multiple review rounds, the same concerns can be re-raised by future reviewers who haven't read the full history. A Resolution Map indexed by finding (Round + Severity + Description) and Resolution (specific task/step/test) lets reviewers ctrl-F for prior consideration before raising a concern. Without it, the plan's increasing length makes "did we already address X?" a full re-read.

**Evidence:** The T-03 plan's Resolution Map now has 17+ rows across five rounds. Each row maps a finding to a specific resolution with line/step references. The Round 5 review didn't raise any concerns that were already in the map — the reviewer's findings were all NEW (not re-raised). This is evidence the map is working as a "what has been considered" index.

**Implication:** Any plan that goes through 3+ review rounds should adopt a Resolution Map proactively in the first revision. Cost is low (~200 chars per row). Benefit compounds with each round because the map prevents re-raising prior concerns AND serves as a navigation aid for the plan itself.

**Watch for:** Plans that grow beyond 1500 lines without a Resolution Map. These are candidates for retroactive map insertion — but the cost of retroactive insertion is much higher than proactive insertion.

## Next Steps

### 1. Wait for user feedback on the sixth draft

**Dependencies:** None — the sixth draft is complete and committed.

**What to read first:** `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` (the full plan, now 2066 lines, committed as `6e0f6820`). Pay special attention to:
- The new stderr monitoring assumption note in the Fail-Open Hook Policy design decision (~line 73-75)
- The rewritten Task 8 lead-in (~line 1136+)
- The new in-process fallback test in Task 8 Step 3 code block
- The new smoke-setup subprocess test in Task 8 Step 5 code block
- The rewritten self-review row 2 (~line 1932+)
- The 6 new Resolution Map rows (Round 5 entries)

**Approach suggestion:** Do NOT start execution without explicit user approval. The user's iterative-review pattern has been consistent: five rounds of explicit review before accepting a draft. Assume Round 6 is possible. The user said: *"I will review the latest draft of the plan and then share my feedback with you in the next session."*

**Acceptance criteria:** User returns with either (a) approval + execution choice (Subagent-Driven vs. Inline), (b) a Round 6 review with more findings to address, or (c) a different direction entirely.

**Potential obstacles:** None at this stage. The plan is complete, self-contained, and committed.

### 2. Execute the plan (when approved)

**Dependencies:** User approval of the sixth draft.

**What to read first:** The sixth draft of the plan. Each task is self-contained with exact file paths, line numbers, code snippets, test bodies, expected outputs, and diagnostic paths.

**Approach suggestion:** Subagent-Driven execution is recommended per the plan's "Execution Handoff" section. Reasons (carried over from Round 4 handoff):
- Task 1's three-stage flow is dense enough that a fresh subagent walking only Task 1 (without carrying the four-rounds-of-review context) is likely to follow the spec more literally.
- Task 4's six-scenario coverage benefits from a focused walker.
- Task 7's seven manual probes (via subprocess + bash) benefit from a focused walker.
- Task 8's now FOUR test patterns (in-process per-file, subprocess chmod, in-process fallback, smoke-setup subprocess) each have different semantics and benefit from explicit task-level focus.

Inline execution is an acceptable alternative if the user wants to observe execution in real time.

**Acceptance criteria:** All 9 tasks completed; all 18 new tests + 1 tightened test passing; all 3 callers updated with caller-attributed stderr logs; all manual verification steps in Task 7 executed with expected outputs matching; PR opened in draft state with the exact shape specified in Task 9.

**Potential obstacles:**
- Task 1's three-stage refactor must be applied ATOMICALLY (no partial commits). The Task 4 coverage tests assume the full Task 1 implementation is present.
- The `chmod 0o000` tests (now THREE of them) require non-root POSIX. If executing on a CI-like environment, three tests will skip. The in-process fallback covers the lifecycle path but not the smoke-setup subprocess path or the helper-level path on those platforms.
- The plan commit (`6e0f6820`) is local-only. Before opening a PR (Task 9 Step 5), the branch must be pushed to remote.

### 3. Push the plan commit to remote (optional, before execution)

**Dependencies:** User approval (push is durable and visible).

**What to read first:** `git status` to confirm clean tree. `git log --oneline origin/main..HEAD` to confirm only the plan commit is ahead.

**Approach suggestion:** `git push -u origin fix/t03-stale-cleanup-observability`. This makes the plan visible on GitHub, creates the upstream tracking branch, and prepares for the future PR. The push is optional — the plan can stay local if the user wants to start execution before publishing.

**Acceptance criteria:** Branch published, upstream tracking set, plan commit visible at `https://github.com/jpsweeney97/claude-code-tool-dev/blob/fix/t03-stale-cleanup-observability/docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md`.

**Potential obstacles:** None expected. Branch protection allows pushes to feature branches.

### 4. Handle a potential Round 6 review

**Dependencies:** User's feedback determines whether this is needed.

**What to read first:** If the user returns with more findings, re-read the specific sections the user references AND verify any code-location claims empirically (same pattern as Rounds 4-5).

**Approach suggestion:** Treat any Round 6 as another iteration of the same pattern — identify each finding, verify it, draft a fix, present forced choices to the user (if any), apply approved edits, update the Resolution Map, produce a summary. Do NOT prematurely optimize for "this is the last round" — the user's review discipline has been consistent and five rounds have been needed so far.

**Acceptance criteria:** Every Round 6 finding has a documented resolution in the Resolution Map with specific references; no prior-round fix is invalidated.

## In Progress

**What was being worked on:** Round 5 revision of the T-03 implementation plan and committing the resulting plan file.

**Approach:** 26+ targeted edits to the plan file applied top-down (line ~73 through line ~2056), each via the Edit tool with unique `old_string` content. Empirical verification of every reviewer claim preceded the fixes. Three forced choices presented to the user as a decision brief; user approved with one correction (use `parents[4]` not `git rev-parse`). All edits applied; final grep sweeps confirmed no stale references; plan committed as `6e0f6820`.

**State:** Sixth draft complete (2066 lines, +273 from 1793). Plan committed. Branch is 1 commit ahead of origin/main. Working tree clean. Waiting for user review before execution or further iteration.

**Working:**
- All 26+ plan edits applied cleanly via the Edit tool
- Stderr monitoring assumption paragraph added to Fail-Open Hook Policy (Option 1)
- Task 8 lead-in fully rewritten with two-error-surfaces framing + contract shape table (lifecycle fail-OPEN vs smoke-setup fail-FAST) + explicit "root-level raises don't go through `report()`" sentence
- `test_main_fail_open_conversion_via_monkeypatched_listdir` (Choice 2C in-process fallback) appended to Task 8 Step 3, wrapped in `with monkeypatch.context() as patched:` per constraint #6
- `_run_smoke_setup` subprocess helper added to Task 8 Step 5 template (modeled on `_run_lifecycle`, omits `env=`)
- `test_prepare_scenario_surfaces_cleanup_enumeration_failure` (Choice 1A smoke-setup subprocess test) appended to Task 8 Step 5, derives repo root via `Path(__file__).resolve().parents[4]` per user correction
- Task 7 wrapper gated on `if result.had_errors:` (Choice 3B); all 4 ripple updates (Step 4 expected, Step 5 expected, Step 6 diagnostic, Step 7 diagnostic) applied
- Task 8 Step 4 + Step 6 diagnostic paths extended for all new tests (5 + 6 new branches respectively)
- Task 9 Step 1 baseline `535 → 537`, platform matrix re-derived (`537/534/536/533/534`)
- Task 9 Step 5 PR body baseline updated to match
- Self-review row 2 (Fix 2b) fully rewritten with per-file vs root-level surface distinction
- Self-review summary bullet (line 1685) and row 1 (line 1741) updated for Choice 3B
- 6 new Round 5 Resolution Map rows added (High + 5 Medium)
- Three forced design decisions entry #3 updated to reference both lifecycle tests + smoke-setup subprocess test + stderr monitoring note
- Type consistency rule extended for new monkeypatch forms
- Risk verification "Both" → "All three" + 3 new bullets for Round 5 changes
- Final grep sweeps (6 sweeps) confirmed no stale "534/535", "propagates naturally" (except intentional), "all three callers print" (except intentional Round 5 fix sentence), "four rounds", "16 new tests", or "unconditional" (except intentional Resolution Map quotes) references
- Plan committed as `6e0f6820` via standard commit protocol (HEREDOC + Co-Authored-By + verified post-commit)

**Not working / incomplete:**
- Plan has NOT been executed. No code changes to `containment.py`, scripts, or tests yet.
- Plan commit is local-only — not pushed to `origin`.

**Open questions:**
- User feedback on the sixth draft is unknown. Round 6 is possible.
- Execution strategy still unknown (Subagent-Driven vs. Inline).
- Whether to push the plan commit to remote before execution starts.
- Whether the stderr monitoring path assumption should be empirically validated as a follow-up.

**Immediate next action:** Wait for user feedback. If user approves with execution choice, begin executing per the chosen strategy. If user returns with Round 6 findings, apply the same empirical-verify-then-fix pattern that addressed Rounds 4 and 5. Do NOT start execution autonomously.

## Open Questions

1. **Will the user approve the sixth draft or issue a Round 6 review?** The `/handoff:save` invocation at the end of the session, with the explicit message "I will review the latest draft of the plan and then share my feedback with you in the next session", suggests the user wants to review asynchronously rather than give immediate direction.

2. **Which execution strategy will the user choose?** The plan offers Subagent-Driven (recommended) or Inline Execution. The choice affects whether the execution session will dispatch a subagent per task or batch through checkpoints.

3. **Should the plan commit be pushed to remote before execution starts, or stay local until the PR is opened?** The plan is now committed locally as `6e0f6820`. Pushing makes it visible on GitHub but is optional. The user did not specify.

4. **Should the stderr monitoring path assumption be empirically validated as a follow-up?** The Round 5 resolution accepted the assumption with a note rather than validating empirically. If the user wants extra confidence, a 10-minute experiment (run a real `chmod 0o000` scenario and confirm stderr surfaces somewhere operators see) could strengthen the design decision. Out of scope for T-03 but a potential follow-up.

5. **Are there other hook scripts in the codex-collaboration plugin with similar fail-open boundaries?** The Round 4 design decision is specific to `containment_lifecycle.py`. The Round 5 stderr monitoring note acknowledges hook stderr is an observability surface. If other hook scripts in the plugin have the same fail-open pattern, they may need similar policy documentation. Not in scope for T-03 but worth noting for future tickets.

6. **Should the new smoke-setup subprocess test's B1 fixture coupling be relaxed?** The current implementation depends on the existence of 6 specific fixture files (`contracts.md`, `delivery.md`, etc.). If those files are reorganized, the test breaks. A future refactor could make `_repo_paths()` lazy (only validate fixtures that are actually accessed) — that would decouple the test from B1 fixture paths. Out of scope for T-03.

## Risks

- **Plan fatigue risk:** The plan is now 2066 lines across six drafts. A future implementer executing the plan verbatim will need to cross-reference the Resolution Map (now 17+ entries) frequently to understand why specific choices were made. Mitigation: Resolution Map and Design Decisions sections are at the top of the plan and are stable anchors.

- **Three chmod tests sharing skipif risk:** All three chmod tests (`test_clean_stale_files_raises_when_root_directory_unreadable` in Task 4, `test_subagent_start_surfaces_cleanup_enumeration_failure` in Task 8, `test_prepare_scenario_surfaces_cleanup_enumeration_failure` in Task 8) skip together on root or Windows. If CI migrates to a root container or adds Windows runners, all three skip silently and the only caller-boundary coverage of root-level failures is the in-process fallback (which only covers lifecycle, not smoke-setup or wrapper). Mitigation: in-process fallback exists; helper-level mock-based test (`test_clean_stale_files_raises_when_enumeration_fails`) always runs.

- **Smoke-setup B1 fixture coupling risk:** The new smoke-setup subprocess test depends on 6 specific fixture files existing in the repo. If any are moved or renamed, the test fails with `RuntimeError("resolve repo paths failed: ...")` even though the cleanup wiring is still correct. Mitigation: explicit diagnostic path in Task 8 Step 6 with recovery options.

- **`Path(__file__).resolve().parents[4]` brittleness risk:** If the test file is moved within the repo (e.g., to a different package directory), `parents[4]` will return the wrong path and the test will fail. Mitigation: explicit diagnostic path in Task 8 Step 6 explaining how to recompute the index.

- **`os.listdir` monkeypatch import-style dependency risk:** The in-process fallback test depends on `containment.py` using `import os; os.listdir(...)` (attribute lookup). If a future refactor changes to `from os import listdir` (reference captured at import time), the monkeypatch becomes a no-op. Mitigation: explicit diagnostic path in Task 8 Step 4 with the recovery hint.

- **Stderr monitoring path assumption is unvalidated:** The Round 5 resolution accepted the assumption that hook-script stderr surfaces to operators. If this turns out to be wrong, the entire Fail-Open Hook Policy needs to be revisited. Mitigation: explicit assumption note in the design decision, plus the commitment "if operational experience later shows hook stderr is being swallowed in practice, the correct fix is NOT to flip fail-open — it is to add a structured telemetry emission path orthogonal to stderr." Future-Claude won't reach for the wrong fix.

- **Plan commit timing risk:** The plan commit (`6e0f6820`) is local-only. If the user wants to squash it into Task 1 later, it would require an interactive rebase, which the user rules forbid (`-i` flag explicitly disallowed). The commit is durable and cannot be folded post-hoc without violating the rule. Mitigation: this was a deliberate decision documented in Decision 6.

- **Sixth draft could trigger Round 6:** Five rounds have been needed so far. The user's review discipline has been consistent. There is no structural reason to assume Round 6 is impossible. Plan accordingly: do not start execution autonomously.

## References

**Plan file (the primary artifact of this session):**
- `/Users/jp/Projects/active/claude-code-tool-dev/docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` — sixth draft, 2066 lines, committed as `6e0f6820`

**Plan commit:**
- `6e0f6820` — `docs(t-03): add stale-cleanup observability implementation plan`

**Target files for T-03 execution (unchanged from Round 4):**
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/server/containment.py` — `clean_stale_files` at lines 290-310, `_STALE_PATTERNS` at 12-24
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py` — CLI wrapper, will be gated on `had_errors` per Round 5 Choice 3B
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/containment_lifecycle.py` — `_handle_subagent_start` at line 63, `main()` fail-open at 184-188
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py` — `prepare_scenario` at 107, cleanup call at 118, `_scenario_definition` at 364, `__main__` fail-fast wrapper at 505-510
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/tests/test_containment.py` — existing test file (Task 1-6 add 13 tests)
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/tests/test_containment_lifecycle.py` — existing test file with `_load_lifecycle_module` and `_run_lifecycle` (Task 8 adds 3 tests including the Round 5 in-process fallback)
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/tests/test_containment_smoke_setup.py` — NEW FILE created in Task 8 Step 5 (now 2 tests including the Round 5 subprocess test)

**Errata cross-reference (Round 5 stderr monitoring note):**
- `/Users/jp/Projects/active/claude-code-tool-dev/docs/tickets/closed-tickets/2026-02-15-plan-review-errata.md:439` — "MCP servers run as subprocesses with no stderr monitoring path. Fail-fast or nothing." (the precedent the Round 5 assumption note explicitly distinguishes from)

**Prior handoff (resumed from):**
- `/Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-11_00-46_t-03-plan-round-4-fail-open-policy-and-decoupled-tests.md`

**Ticket:**
- `/Users/jp/Projects/active/claude-code-tool-dev/docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md`

**Base commit:**
- `fd7c9365` — merge commit from PR #102 (T-04), original base for the `fix/t03-stale-cleanup-observability` branch

**Current commit:**
- `6e0f6820` — `docs(t-03): add stale-cleanup observability implementation plan` (this session's commit)

## Gotchas

1. **The Task 8 lead-in line number shifted significantly during edits.** The original "line 1136" reference from the Round 5 review applied to the fifth draft (1793 lines). After all Round 5 edits, the equivalent content is at a different line number in the sixth draft (2066 lines). Use Grep for the canonical text rather than line numbers when verifying.

2. **`monkeypatch.context()` is required for the in-process fallback test per constraint #6.** I initially drafted the test without it (using direct `monkeypatch.setattr`), then refactored to wrap the patches in `with monkeypatch.context() as patched:` to match the existing pattern. Future tests in this plan that use monkeypatch must also follow this pattern, or constraint #6 needs to be amended to allow direct setattr (which is functionally equivalent for function-scoped tests but inconsistent with the pattern).

3. **`_run_smoke_setup` deliberately omits `env=`.** Unlike `_run_lifecycle` which passes `env={**os.environ, "CLAUDE_PLUGIN_DATA": str(data_dir)}`, `_run_smoke_setup` inherits the parent environment unmodified. This is because smoke-setup uses `--data-dir` (a CLI argument) for data directory override, not the env var. If a future test needs to test the env-var fallback, it would need to extend `_run_smoke_setup` with an optional `env` parameter.

4. **`Path(__file__).resolve().parents[4]` requires the test file to be at exactly 4 directories deep from the repo root.** The current location is `packages/plugins/codex-collaboration/tests/test_containment_smoke_setup.py`, which is `packages → plugins → codex-collaboration → tests → file = 4 levels`. So `parents[0] = tests`, `parents[4] = repo_root`. If the test file is moved (e.g., to `packages/plugins/codex-collaboration/tests/integration/test_*.py`), the index needs to be `parents[5]`. Documented in Task 8 Step 6 diagnostic paths.

5. **The smoke-setup `prepare` command requires a valid `--repo-root` even when the test fails before reaching `prepare_scenario`.** `_repo_paths()` validation runs in `main()` BEFORE `prepare_scenario` is called (which is where the `chmod 0o000` would cause the failure). So the test must provide a valid `--repo-root` even though it never actually uses any of the fixture files. This is an upstream coupling, not a coupling to the failure mode itself.

6. **Pre-commit hooks fired during `Edit` operations, not at `git commit` time.** The branch-protection hook is configured as a `PreToolUse` hook on `Edit`/`Write` events (per `.claude/rules/workflow/git.md`), not as a Git pre-commit hook. So it had already evaluated the branch when the plan was edited and approved (because `fix/t03-stale-cleanup-observability` is a recognized `fix/*` working branch pattern). By the time `git commit` ran, no further hook checks were needed. This means a `git commit` from a script or detached process (without going through Claude Code's edit pipeline) would NOT be blocked by the branch-protection rule — the rule lives in Claude Code's hook layer, not in git's pre-commit layer.

7. **The plan commit cannot be squashed into Task 1 later via `git rebase -i`.** The user's global CLAUDE.md forbids the `-i` flag for git rebase. So the plan commit (`6e0f6820`) is permanent — it will appear as its own commit in the final PR. Decision 6 in this handoff documents this as a deliberate choice.

8. **The Resolution Map now has rows for "Round 4 High" and "Round 5 High" — same severity, different rounds, different findings.** When grepping for findings, distinguish by round number, not just severity. The Round 4 High was fail-open implicit; the Round 5 High is smoke-setup gap. Different concepts, different resolutions, different tests.

9. **User's review discipline is consistent across rounds.** Five review rounds have been needed so far. Each round uses the same structured format (Premise Check, Critical Failures, High-Risk Assumptions, Real-World Breakpoints, Hidden Dependencies, Adversarial Perspectives, Patterns And Root Causes, Required Changes, Verdict). Do NOT assume the next round will be "just approval" — assume it could be Round 6 with more findings, and verify all claims empirically before drafting responses.

10. **`Path(__file__).resolve().parents[4]` is the kind of code that looks like a magic number but isn't.** The `4` is determined by the repo's directory structure, not by an arbitrary choice. A future maintainer reading the test should know that the index counts directories from the test file up to the repo root. Documented in the test docstring with the explicit path walk: `tests → codex-collaboration → plugins → packages → repo_root`.
