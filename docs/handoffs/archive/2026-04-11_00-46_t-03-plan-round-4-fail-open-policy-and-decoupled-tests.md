---
date: 2026-04-11
time: "00:46"
created_at: "2026-04-11T04:46:13Z"
session_id: 209c1033-50bf-4e4b-b441-f1378c64d03c
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-10_07-08_t-04-published-pr-102-cleaned-local-main-drift-remains.md
project: claude-code-tool-dev
branch: fix/t03-stale-cleanup-observability
commit: fd7c9365
title: T-03 plan Round 4 revision — fail-open policy endorsed, caller tests decoupled
type: handoff
files:
  - docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md
  - packages/plugins/codex-collaboration/server/containment.py
  - packages/plugins/codex-collaboration/scripts/containment_lifecycle.py
  - packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py
  - packages/plugins/codex-collaboration/tests/test_containment.py
  - packages/plugins/codex-collaboration/tests/test_containment_lifecycle.py
---

# Handoff: T-03 plan Round 4 revision — fail-open policy endorsed, caller tests decoupled

## Goal

Address the Round 4 adversarial review of the T-03 implementation plan (`docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md`) and produce a fifth draft that closes all four findings — one High, two Medium, one Low — without invalidating any prior Round 1-3 fix.

**Trigger:** User delivered a Round 4 review with verdict `Minor revision` (stronger than Round 3's `Reject`, meaning the core algorithm finally survived but boundary-policy issues remained). The review was titled "Scrutiny: [2026-04-10-t03-stale-cleanup-observability.md]" and was structured with sections for Premise Check, Critical Failures, High-Risk Assumptions, Real-World Breakpoints, Hidden Dependencies, Adversarial Perspectives Applied, Patterns And Root Causes, and Required Changes.

**Stakes:** T-03 is a correctness hardening ticket on the codex-collaboration shakedown cleanup lifecycle. `clean_stale_files()` currently uses `Path.exists()` and `Path.glob()` — both of which silently swallow `OSError` subclasses, making a broken shakedown root indistinguishable from "nothing to clean". Four review rounds have been required to surface every silent-success class; this round handles the last layer (caller boundaries). Without the Round 4 fixes, a `chmod 0o000` on the shakedown root would pass the plan's tests (per-file unlink wiring) while still breaking the observability contract at the hook-runner boundary.

**Bigger picture:** T-03 is the remaining correctness hardening ticket on the shakedown lifecycle arc. T-04 (wrapper script fix, PR #102) was merged in the prior session. T-03 hardens the function T-04's wrapper calls. Once T-03 ships, the shakedown cleanup path has explicit failure modes at every layer from per-file operations up through the hook entry point.

**Success criteria for this session:**
- Reviewer's High finding (`containment_lifecycle.py:main()` fail-open implicit) resolved with an explicit design decision
- Reviewer's Medium #1 (smoke-setup test overfitted to `scope_file_remove`) resolved by decoupling via a direct module-level stub
- Reviewer's Medium #2 (no automated test for root-level failure through an internal caller) resolved with a new subprocess test
- Reviewer's Low finding (eager `os.listdir()` tradeoff unstated) resolved with an inline note
- All Round 1-3 fixes still in place, verified via grep for stale references

**Connection to project arc:** This session extends the iterative-review pattern established across three prior rounds. Each round narrows the silent-failure surface by one layer. Round 4's contribution is to pin the caller-boundary observability contract explicitly rather than implicitly relying on "exceptions propagate". The plan is now at fifth draft; the user said "I will review the draft and share my feedback with you in the next session" — meaning a potential Round 5 is possible before execution.

## Session Narrative

**Phase 1 — Resume and empirical verification of the Round 4 High claim.**

The session began resuming from the T-04 handoff (state file at `docs/handoffs/.session-state/handoff-209c1033-50bf-4e4b-b441-f1378c64d03c` pointed to `docs/handoffs/archive/2026-04-10_07-08_t-04-published-pr-102-cleaned-local-main-drift-remains.md`). The context at resume included the fourth draft of the T-03 plan (1625 lines) and the Round 4 review message from the user.

First investigation target: verify the reviewer's High claim that `containment_lifecycle.py:184` catches and swallows exceptions. Read `scripts/containment_lifecycle.py` completely. Found:

```python
def main() -> int:
    data_dir = _plugin_data_from_env()
    if data_dir is None:
        _log_error("containment-lifecycle: CLAUDE_PLUGIN_DATA missing")
        return 0
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError, UnicodeDecodeError) as exc:
        _log_error(f"containment-lifecycle: invalid hook payload. Got: {exc!r:.100}")
        return 0
    if not isinstance(payload, dict):
        _log_error(...)
        return 0
    try:
        handle_payload(payload, data_dir=data_dir)
    except Exception as exc:
        _log_error(f"containment-lifecycle: internal error ({exc})")
    return 0
```

Lines 184-188 confirmed: outer `try: handle_payload(...); except Exception as exc: _log_error(f"containment-lifecycle: internal error ({exc})")`, then `return 0`. The earlier drafts' "naturally propagates" language was wrong at the `main()` layer — exceptions DO propagate through `clean_stale_files → _handle_subagent_start → handle_payload`, but they stop at `main()`'s catch-all and never reach the hook runner. The reviewer was correct. This is a deliberate hook-contract boundary.

**Phase 2 — Explored `containment_smoke_setup.py` for direct seams.**

Second investigation target: find a direct seam for decoupling the smoke-setup wiring test from `scope_file_remove requires --run-id` choreography. Read `scripts/containment_smoke_setup.py` completely. Confirmed:

- `prepare_scenario()` at line 107 has `clean_stale_files(...)` as its FIRST call (line 118), before `_read_session_id`, `_assert_no_live_conflict`, or `_scenario_definition`.
- `_scenario_definition` is a module-level function at line 364 that `prepare_scenario` calls via module globals lookup.
- The "unknown scenario_id" `RuntimeError` at lines 494-497 is a generic termination path — not scenario-specific.

Decided: `monkeypatch.setattr(smoke_setup, "_scenario_definition", raising_stub)` is the cleanest direct seam. Cleanup runs FIRST at line 118; by the time the stub raises, the `had_errors=True` cleanup report is already in stderr. Passing explicit `session_id` + `run_id` bypasses `_read_session_id` and `uuid.uuid4()` respectively; `_assert_no_live_conflict` passes because no active-run pointer exists.

Key pivot moment: decided NOT to use `scenario_id="__unknown_sentinel__"` + the real `_scenario_definition`'s "unknown scenario_id" error path. That would still depend on the error text format. A direct stub (ignoring `scenario_id` entirely) is more robust.

**Phase 3 — Explored `test_containment_lifecycle.py` for subprocess test infrastructure.**

Third investigation target: confirm the subprocess helper for the new root-level lifecycle test exists. Read `tests/test_containment_lifecycle.py` lines 1-60. Found:

- `_load_lifecycle_module()` at lines 30-38: in-process importlib loader (used by existing per-file wiring test).
- `_run_lifecycle()` at lines 41-54: subprocess invocation via `subprocess.run([sys.executable, SCRIPT], input=json.dumps(payload), capture_output=True, text=True, env=env+CLAUDE_PLUGIN_DATA=data_dir)`.

Key decision: the new `test_subagent_start_surfaces_cleanup_enumeration_failure` test MUST use `_run_lifecycle` (subprocess) rather than `_load_lifecycle_module` (in-process). An in-process call to `_handle_subagent_start` bypasses `main()`'s outer try/except and therefore cannot observe the exception-to-exit-code conversion — which is the entire contract under test.

**Phase 4 — Read the current plan draft completely to understand edit targets.**

Fourth investigation target: the full fourth-draft plan file. Read all 1625 lines. Mapped the sections that needed edits:

- Architecture paragraph (line 17) — needs acknowledgment that T-03 does NOT change any caller's exit-code contract.
- Design Decisions section — needs new "Fail-Open Hook Policy" subsection after Enumeration Primitive.
- Enumeration Primitive subsection — needs scale tradeoff note.
- Key correctness constraints list (lines 80-89) — needs new constraint #11.
- File Structure row for `test_containment_lifecycle.py` — needs "Add 1 new test" → "Add 2 new tests".
- Task 8 Step 3 — needs expansion to add the new subprocess test.
- Task 8 Step 4 — needs updated pytest invocation covering both tests.
- Task 8 Step 5 — needs the smoke-setup test body rewritten with direct seam.
- Task 8 Step 6 — needs updated diagnostic paths.
- Task 9 Step 1 test table — needs new row.
- Task 9 Step 1 baseline (534 → 535) and platform table re-derivation.
- Task 9 Step 5 PR body — needs baseline count update.
- Resolution Map — needs 4 new rows for Round 4.
- Self-Review → Explicit design decisions — needs bump from "Two" to "Three".
- Self-Review → Type consistency — needs monkeypatch note extension.
- Self-Review → Risk verification — needs bullets for subprocess test and chmod restore.
- Scope notes "three rounds" → "four rounds".

**Phase 5 — Applied the edits sequentially.**

Fourteen targeted edits over the plan file. Each edit was atomic and touched exactly the section it needed to change. Highlights:

1. **Architecture paragraph rewrite** (1 edit) — added explicit "T-03 does not change any caller's exit-code contract" plus specific contract shape for each caller's outer exception boundary.
2. **Scale tradeoff paragraph** (1 edit, ~5 lines) — inserted into Enumeration Primitive subsection between rationale bullets and test coverage.
3. **Fail-Open Hook Policy design decision** (1 edit, ~30 lines) — full subsection with rationale bullets, contract shape table (failure class → stderr strings + exit code), and test coverage pointer to both lifecycle tests.
4. **Constraint #11** (1 edit, 1 line added to the numbered list) — locks in fail-open so future maintainers cannot silently flip it.
5. **File Structure row** (1 edit) — "Add 1 new test" → "Add 2 new tests" with detailed description of both tests.
6. **Task 8 Step 3 title + prose** (1 edit) — "Add the two lifecycle caller-wiring tests" with in-process vs subprocess split explanation.
7. **Task 8 Step 3 new test body** (1 edit, ~75 lines) — the full `test_subagent_start_surfaces_cleanup_enumeration_failure` function with `@pytest.mark.skipif`, real `chmod 0o000`, `try/finally` restore, and dual assertions on returncode + stderr content.
8. **Task 8 Step 4 pytest invocation** (1 edit) — covers both tests with expanded diagnostic paths including the "Round 3 / Round 4 silent-success regression" diagnostic.
9. **Task 8 Step 5 smoke-setup test rewrite** (1 edit, ~50 lines) — replaced the `scope_file_remove` body with the monkeypatched `_scenario_definition` version, including generic sentinel RuntimeError and explicit `session_id`/`run_id` to bypass `_read_session_id` and `uuid.uuid4()`.
10. **Task 8 Step 6 diagnostic paths** (1 edit) — replaced stale reference to "scope_file_remove requires" with four new diagnostic branches including "monkeypatch target wrong", "_read_session_id called", and "Path equality surprise".
11. **Task 9 Step 1 test table + baseline + platform table** (1 edit) — added new row for the subprocess test, baseline `534 passed` → `535 passed`, re-derived all five platform-conditional rows because both chmod tests now skip under the same guard.
12. **Task 9 Step 5 PR body baseline** (1 edit) — `534 passed` → `535 passed` with new platform-conditional text.
13. **Resolution Map** (1 edit, ~4 rows) — added High (fail-open), Medium (smoke-setup coupling), Medium (no root-level caller test), Low (eager scan tradeoff) with full resolution detail.
14. **Self-Review section updates** (3 edits) — "Two forced design decisions" → "Three", monkeypatch note extension, two risk-verification bullets.

Plus cleanup of stale references: scope-notes "three rounds" → "four rounds", resolution-map heading "P1-P3 across three review rounds" → "four review rounds", in-scope descriptions of both test files updated.

**Phase 6 — Final sanity checks.**

Ran four grep sweeps over the final plan:

1. `grep "5\d\d passed"` — confirmed all baseline references consistent (535 default, 533/534/532 conditional).
2. `grep "naturally propagate|propagate naturally"` — only one remaining occurrence, inside the Fail-Open Hook Policy design decision where it's EXPLICITLY called out as the misleading prior language. Intentional.
3. `grep "534"` — only two remaining occurrences: the "no symlink support" row (535 - 1 = 534, correct) and the PR body re-iterating the same.
4. `grep "scope_file_remove"` — only remaining occurrences are inside the new smoke-setup test's docstring where it's documenting the prior fragility. Intentional, serves as anti-pattern documentation.

Final line count: 1793 lines (up from 1625). Commit count still 8, file count still 7 — the new lifecycle test goes into `test_containment_lifecycle.py` which was already part of Task 8's commit.

**Phase 7 — Produced the final summary message.**

Wrote a comprehensive summary of the fifth draft's changes for the user, with three educational insights threaded through (defense-in-depth at boundary layers, in-process vs subprocess test pattern tradeoffs, the importance of empirical verification before committing to a fix). Presented two execution options (Subagent-Driven recommended for Task 8's three-pattern test coverage, Inline Execution alternative). Ended with "Or: if you see another gap in the fifth draft, I'll iterate rather than start execution."

Session ended with the user invoking `/handoff:save` rather than approving execution or triggering Round 5 — meaning they want to review the draft asynchronously before giving direction.

## Decisions

### Decision 1: Endorse fail-open as deliberate for `containment_lifecycle.py:main()`

**Choice:** Document fail-open as intentional policy; T-03 does NOT change any caller's exit-code contract. Add a full design decision subsection, a correctness constraint, and a subprocess test that asserts the dual contract (exit code `0` AND stderr contains caller-attributed context).

**Driver:** Reviewer's Round 4 High finding: "The plan still treats root-level cleanup failures in `containment_lifecycle.py` as safely 'surfaced' without changing failure semantics, even though the real script catches the exception and returns success at `containment_lifecycle.py:184`." Forced choice: "either fail-open is intentional for hook policy, and the plan must say so and test the downstream observable consequence, or root-level cleanup failures in `containment_lifecycle.py` need different exception plumbing or exit semantics."

Empirically verified at `scripts/containment_lifecycle.py:184-188`: `try: handle_payload(payload, data_dir=data_dir); except Exception as exc: _log_error(f"containment-lifecycle: internal error ({exc})"); return 0`.

**Alternatives considered:**
- **Return non-zero on cleanup failures** — would propagate an infrastructure failure in T4 containment state into a hard block on unrelated agent spawns. `SubagentStart` treats non-zero as "block the spawn". Rejected because the blast radius is unacceptable: a `chmod 0o000` on the shakedown root would cause every subagent spawn to fail, even for completely unrelated work.
- **Leave the policy implicit** — rejected because Round 4 proved that "naturally propagates" language was misleading and future maintainers would be confused. The prior three review rounds established a pattern of "if it's not documented, it's a time bomb".
- **Add a second exception boundary just for cleanup failures** — would require categorizing exceptions into "cleanup-class" and "everything-else-class". Rejected because the complexity is not justified for a boundary that is already fail-open by design.

**Implications:**
- Operator observability is now contracted on stderr (not exit codes). An operator triaging a stderr line needs to be able to identify the specific failure class from the wrapped error message alone.
- Contract shape is documented as a table of (failure class → stderr strings + exit code) pairs in the design decision. Six rows: Stage 1 lstat failure, dangling symlink, not-a-directory, Stage 3 enumeration failure, per-file unlink failure, clean run.
- Constraint #11 in the Key correctness constraints list: "Any future change that makes `main()` return non-zero on cleanup failures must be paired with an explicit policy update in the Design Decisions section, not slipped in silently."
- Future maintainer wanting to flip the policy will need to update THREE mechanisms: design decision subsection, constraint #11, and the subprocess test. Deliberate friction.

**Trade-offs accepted:**
- Hook runner cannot react to containment-state failures automatically. Accepted because the runner cannot distinguish "cleanup failed due to infrastructure" from "your code is broken" and should not be making that call.
- Stderr-only observability depends on operators actually reading stderr. Mitigation: the caller prefix (`containment-lifecycle:`) makes the lines greppable and the wrapped error message is structured.

**Confidence:** High (E2) — empirically verified `main()` structure at lines 184-188 AND reviewer's concern was specific enough to independently verify by reading the file. The exception flow through `clean_stale_files → _handle_subagent_start → handle_payload → main()` was traced manually.

**Reversibility:** Medium — flipping the policy requires updating the design decision section, removing constraint #11, rewriting the subprocess test, and justifying the change. Deliberate friction — not impossible, but structurally discouraged.

**Change trigger:** If `SubagentStart` changes its exit-code semantics (e.g., Claude Code introduces a "soft block" vs "hard block" distinction), or if the hook runner gains the ability to distinguish infrastructure failures from code failures at the protocol level.

### Decision 2: Use subprocess pattern (not in-process) for the new root-level lifecycle test

**Choice:** Add `test_subagent_start_surfaces_cleanup_enumeration_failure` via `_run_lifecycle` (subprocess invocation at `test_containment_lifecycle.py:41-54`), not via `_load_lifecycle_module` (in-process at lines 30-38).

**Driver:** In-process calls to `_handle_subagent_start` bypass `main()`'s outer try/except entirely. The contract under test IS the subprocess boundary's conversion of internal exceptions to `return 0` + stderr log. An in-process test structurally cannot observe this conversion.

**Alternatives considered:**
- **In-process via `_load_lifecycle_module` calling `_handle_subagent_start` directly** — the existing per-file wiring test pattern. Rejected because `_handle_subagent_start` raises `OSError` to the caller, bypassing `main()`. The test would assert on an exception, not on stderr + exit code, and therefore would not pin the fail-open contract.
- **In-process calling `lifecycle_module.main()` directly** — would require patching `sys.stdin` with a fake JSON payload, patching `os.environ["CLAUDE_PLUGIN_DATA"]`, and capturing stderr via `capsys`. Technically possible but more complex than reusing `_run_lifecycle`. Rejected for simplicity.
- **Add a new in-process helper that exercises `main()` without subprocess overhead** — rejected because it duplicates infrastructure that `_run_lifecycle` already provides.

**Implications:**
- Test has ~subprocess-startup overhead (~100-200ms on macOS). Existing lifecycle tests already use this pattern, so the overhead is amortized across the test suite.
- No new subprocess plumbing introduced. `_run_lifecycle` is the same helper existing tests rely on, so a breakage in that helper would surface in older tests before reaching the new one.
- The test's skipif guard (`not hasattr(os, "geteuid") or os.geteuid() == 0`) is shared with `test_clean_stale_files_raises_when_root_directory_unreadable` in Task 4. Both tests skip under the same conditions.

**Trade-offs accepted:**
- Subprocess tests are slower than in-process tests. Accepted because the contract under test requires executing `main()`, which requires a real process.
- Subprocess tests are less hermetic — they depend on `sys.executable` being available and on the script's imports resolving correctly. Mitigated by reusing the existing pattern which is already exercised by passing tests.

**Confidence:** High (E2) — confirmed `_run_lifecycle` helper exists and works at `test_containment_lifecycle.py:41-54`, and manually traced the subprocess flow (`subprocess.run([sys.executable, SCRIPT], input=json.dumps(payload), capture_output=True, text=True, env={**os.environ, "CLAUDE_PLUGIN_DATA": str(data_dir)})`).

**Reversibility:** Low — this is a structural requirement, not a preference. You cannot test `main()`'s fail-open conversion without executing `main()`, and executing `main()` from pytest requires a subprocess.

**Change trigger:** None under current Python semantics. Would only change if the codebase added an async in-process test runner for the script (e.g., via `click.testing.CliRunner`-equivalent for non-click scripts).

### Decision 3: Decouple smoke-setup wiring test via `monkeypatch.setattr(smoke_setup, "_scenario_definition", raising_stub)`

**Choice:** Replace the brittle `scenario_id="scope_file_remove"` + `run_id=None` termination with a monkeypatched `_scenario_definition` that raises a generic sentinel `RuntimeError("smoke-setup wiring test termination sentinel")`. Pass explicit `session_id="wiring-test-session"` and `run_id="wiring-test-run"` to bypass `_read_session_id` and `uuid.uuid4()`. Construct a minimal `RepoPaths` directly.

**Driver:** Reviewer's Round 4 Medium finding: "The proposed test in the plan drives `prepare_scenario()` through `scenario_id='scope_file_remove'` with `run_id=None` and relies on a later `RuntimeError` to terminate after the cleanup log fires. That is a brittle dependency on current scenario ordering, not a stable assertion of caller behavior."

The correct test should measure the STABLE contract ("cleanup runs first, then logging happens, then any later failure terminates") not the CHOREOGRAPHY of any specific scenario's validation.

**Alternatives considered:**
- **Keep the `scope_file_remove` approach** — rejected per reviewer's finding. A harmless refactor to that scenario (renaming, moving validation earlier, adding a different error message) would break the test even if the cleanup wiring remained correct.
- **Use `scenario_id="__unknown_sentinel__"` to trigger `_scenario_definition`'s own "unknown scenario_id" `RuntimeError`** — works without monkeypatch but still depends on the "unknown scenario_id" error path's text format. Slightly less robust than a direct stub. Rejected because the direct stub makes the test's intent unambiguous.
- **Monkeypatch `_read_session_id` to raise** — terminates BEFORE `_assert_no_live_conflict` rather than after. Cleanup still runs (it's at line 118, before `_read_session_id`), but the test's intent is less clear because `_read_session_id` is not the "scenario logic" seam. Rejected in favor of `_scenario_definition`.
- **Add a test-only code path in `prepare_scenario`** — rejected because it would contaminate production code for test purposes. Violates the principle that tests should use the production API, not a test-carve-out.

**Implications:**
- Test's termination sentinel is deliberately generic. The assertion `pytest.raises(RuntimeError, match="smoke-setup wiring test termination sentinel")` cannot accidentally re-couple to any real scenario's error text.
- `RepoPaths` is constructed directly (bypassing `_repo_paths()` which validates file existence). Fields must be `Path` objects to satisfy dataclass type annotations, but the target paths do not need to exist because `_scenario_definition` is stubbed and never evaluates `repo_paths.file_anchors` or `repo_paths.scope_directories`.
- The test now measures: "does `prepare_scenario` call `clean_stale_files` → did `clean_stale_files` return a `had_errors=True` result → did `prepare_scenario` log that result with the correct prefix before continuing → does termination happen before any scenario-specific logic runs". Every element of this chain is a stable contract.
- Docstring explicitly documents the prior fragility so the anti-pattern isn't reintroduced by a future maintainer.

**Trade-offs accepted:**
- Test uses a deeper mock (stubbing a module-level function) which is slightly more complex than a simple filter-based monkeypatch like `Path.unlink`. Accepted because it makes the contract under test crystal clear.
- If `prepare_scenario` is refactored to NOT call `_scenario_definition` via module globals (e.g., imported directly as `from server.smoke_setup._scenario_definition import ...`), the monkeypatch target would become wrong. Mitigation: the diagnostic list in Task 8 Step 6 calls out this exact failure mode.

**Confidence:** High (E2) — confirmed `_scenario_definition` is a module-level function at `containment_smoke_setup.py:364` and that `prepare_scenario` at line 127 calls it as `_scenario_definition(scenario_id, repo_paths=repo_paths)` via normal module-global lookup. Python's LEGB rule guarantees the monkeypatch will redirect the call.

**Reversibility:** High — the test file is new in this plan (created in Task 8 Step 5), and the test body can be rewritten independently. No production code depends on this test pattern.

**Change trigger:** If `prepare_scenario` is refactored to call `_scenario_definition` via an indirect reference (e.g., a function-parameter), or if the cleanup call is moved to a later position in `prepare_scenario` that's after some other validation step.

### Decision 4: Document `os.listdir()` scale tradeoff inline rather than defer to future exploration

**Choice:** Add a "Scale tradeoff" paragraph to the Enumeration Primitive design decision documenting that `os.listdir()` materializes the full directory into a `list[str]` and that the candidate list is iterated in a second pass.

**Driver:** Reviewer's Round 4 Low finding: "The draft assumes `os.listdir()` materialization is operationally fine because the shakedown directory is small. That is probably true today, but it is still an unstated scale assumption." A future maintainer hitting an unusual operational envelope should know the swap path without having to re-derive the decision.

**Alternatives considered:**
- **Defer to a future review round** — rejected because the tradeoff is fresh in mind now and documenting it inline is nearly free (5 lines).
- **Add a separate design decision subsection just for the scale tradeoff** — rejected because it's not a forced design decision, just a note. Belongs within the Enumeration Primitive subsection it relates to.
- **Skip it entirely** — rejected because the reviewer specifically asked for "one sentence in the design or risk section" and the cost of including it is trivial.

**Implications:**
- Design doc now tells future maintainers that `os.scandir()` with a `with` block is a drop-in replacement if shakedown footprint ever grows into thousands of entries. Both helpers raise `PermissionError` on `chmod 0o000`, so Stage 3 remains correct under either primitive.
- The paragraph includes operational envelope context: "the shakedown directory holds state files for a single agent run (typically 5-15 files bounded by `_STALE_PATTERNS`) and is cleaned every 24 hours".

**Trade-offs accepted:** None — the paragraph is 5 lines and adds no complexity.

**Confidence:** High (E2) — both `os.listdir` and `os.scandir` were empirically verified to raise `PermissionError` on `chmod 0o000` during the Round 3 Python 3.14 verification. The "drop-in" claim is backed by that verification.

**Reversibility:** High — the paragraph can be removed or updated trivially.

**Change trigger:** If shakedown footprint ever grows into thousands of entries, in which case the swap to `os.scandir()` becomes actionable.

## Changes

### `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` — Fifth draft (1793 lines, up from 1625)

**Purpose:** Fifth draft of the T-03 implementation plan, addressing all four Round 4 findings (High, Medium, Medium, Low) without invalidating any prior Round 1-3 fix.

**Approach:** Fourteen targeted edits via the Edit tool. No sections were removed or rewritten from scratch — all additions were atomic and preserved the surrounding text verbatim. Each edit was paired with a mental check: does this invalidate any prior fix? No edit invalidated any prior fix.

**Key implementation details added:**

*Architecture paragraph (line 17)* — Rewrote to explicitly acknowledge "T-03 does not change any caller's exit-code contract" and describe each caller's outer boundary behavior: wrapper exits `1` with `clean_stale_shakedown failed`, lifecycle exits `0` with `containment-lifecycle: internal error (<exc>)`, smoke-setup propagates `RuntimeError` to its `__main__` wrapper.

*Scale tradeoff paragraph (inside Enumeration Primitive)* — 5 lines documenting `os.listdir()` eager scan acceptable at current scale, `os.scandir()` as drop-in swap if envelope grows.

*Fail-Open Hook Policy design decision (new subsection, ~30 lines)* — Full subsection with:
- Decision statement: lifecycle hook deliberately fail-open, T-03 does not change this
- Rationale bullets: `SubagentStart` treats non-zero as "block the spawn", blast radius concern, stderr as observability surface, Round 4 explicitly calling out the "naturally propagates" language as misleading
- Contract shape table: 6 rows mapping each failure class to its exact stderr strings + exit code
- Test coverage: references both lifecycle tests with the "subprocess pattern is mandatory" note

*Constraint #11 (new item in Key correctness constraints list)* — Locks in fail-open policy with forward-looking guard: "Any future change that makes `main()` return non-zero on cleanup failures must be paired with an explicit policy update in the Design Decisions section, not slipped in silently."

*File Structure row update* — `test_containment_lifecycle.py` row changed from "Add 1 new test" to "Add 2 new tests: in-process test forcing `had_errors=True`... plus a subprocess test exercising a real `chmod 0o000` through `main()` and asserting fail-open exit code plus caller-attributed stderr context".

*Task 8 Step 3 expansion* — Title changed to "Add the two lifecycle caller-wiring tests" with intro prose explaining the in-process vs subprocess split. The new `test_subagent_start_surfaces_cleanup_enumeration_failure` function is appended after the existing in-process test (~75 lines of test body) with `@pytest.mark.skipif` decorator, real `chmod 0o000` setup, `try/finally` restore of `0o755`, and dual assertions on `result.returncode == 0` AND `"containment-lifecycle: internal error" in result.stderr` AND `"cannot enumerate shakedown root" in result.stderr`.

*Task 8 Step 4 pytest invocation* — Updated to run both tests with expanded diagnostic paths including "If the subprocess test FAILS because stderr contains `containment-lifecycle: clean_stale_files: removed=0` instead of `containment-lifecycle: internal error`, the Stage 3 enumeration guard in Task 1 Step 5 is missing" — the Round 3/4 silent-success regression diagnostic.

*Task 8 Step 5 smoke-setup test body (replaced)* — The entire test body is rewritten. Old version used `scenario_id="scope_file_remove"` + `run_id=None` to trigger a scenario-specific error. New version monkeypatches `smoke_setup._scenario_definition` to raise a generic sentinel, passes explicit `session_id` and `run_id`, and constructs minimal `RepoPaths` that are never evaluated. Docstring documents the prior fragility so the anti-pattern isn't reintroduced.

*Task 8 Step 6 diagnostic paths (rewritten)* — Removed stale reference to "if RuntimeError doesn't match 'scope_file_remove requires'". New diagnostics cover: (a) missing `containment_smoke_setup:` prefix (Step 2 not applied), (b) monkeypatch target wrong (real `_scenario_definition` runs), (c) `_read_session_id` called before stub (explicit session_id ignored), (d) `failed_unlink=0` indicating Path equality surprise.

*Task 9 Step 1 test table + baseline + platform table* — New row `test_subagent_start_surfaces_cleanup_enumeration_failure` added. Baseline `534 passed` → `535 passed`. Platform table re-derived because both chmod tests now share the same skipif guard:
- macOS/Linux non-root: 535 passed
- Running as root: 533 passed, 2 skipped
- No symlink support: 534 passed, 1 skipped
- Root AND no symlink: 532 passed, 3 skipped
- Windows: 533 passed, 2 skipped

*Task 9 Step 5 PR body baseline* — Updated from "expected: 534 passed; 533 passed + 1 skipped if running as root..." to "expected: 535 passed on macOS/Linux non-root; 533 passed + 2 skipped if running as root or on Windows — both chmod tests skip; 534 passed + 1 skipped if no symlink support; 532 passed + 3 skipped in the root-or-Windows ∩ no-symlink intersection".

*Resolution Map (4 new rows)* — Round 4 High, Medium ×2, Low findings each mapped to specific resolution with file/step references.

*Self-Review section updates* — "Two forced design decisions" → "Three" with new entry for Fail-Open Hook Policy. Monkeypatch scoping note extended to cover `monkeypatch.setattr(smoke_setup, "_scenario_definition", …)` alongside existing `Path` and `os.listdir` patterns. Two new risk-verification bullets: (a) both chmod tests share the same skipif guard and both restore `0o755` in `finally` blocks, (b) lifecycle subprocess test reuses existing `_run_lifecycle` helper.

*Cleanup of stale references* — "three rounds of adversarial review" → "four rounds" (constraint list header), "(P1-P3 across three review rounds)" → "(four review rounds)" (resolution map header), in-scope descriptions of both test files updated to describe the new test content.

**Design choices:**

- Insertions over rewrites wherever possible, to preserve prior-round context that reviewers can re-check
- Generic sentinel text in tests (e.g., `"smoke-setup wiring test termination sentinel"`) to make coupling impossible
- Contract shape table rather than prose for the Fail-Open Hook Policy, so operators can grep-check their observability is intact
- Diagnostic paths in test-running steps that name specific failure modes (e.g., "the Round 3 / Round 4 silent-success regression") so a future implementer encountering a failure has an immediate hypothesis

**Future-Claude note:** The plan file is untracked (`??` in git status). Before starting Task 1, decide whether to commit the plan file first as a separate docs commit, or include it in Task 1's commit. The existing pattern across prior plans has been to commit the plan as part of the first implementation task — but the plan itself has gone through four review rounds, so a separate commit may be cleaner for commit-message history.

## Codebase Knowledge

### Files Read During Session

| File | Why Read | What Was Found |
|------|----------|----------------|
| `scripts/containment_lifecycle.py` | Verify Round 4 High claim about `main()`'s fail-open boundary | Lines 184-188 confirmed: `try: handle_payload(...); except Exception as exc: _log_error("containment-lifecycle: internal error (...)"); return 0`. Two other `try/except → return 0` boundaries at lines 175 (JSON parse) and 178 (non-dict payload). All three are fail-open. |
| `scripts/containment_smoke_setup.py` | Find direct seam for decoupling smoke-setup wiring test | `prepare_scenario` at line 107; `clean_stale_files` call at line 118 (FIRST operation); `_read_session_id` at 119; `_assert_no_live_conflict` at 121; `_scenario_definition` at 127. `_scenario_definition` function itself at line 364 with "unknown scenario_id" `RuntimeError` at 495-497. `RepoPaths` dataclass at lines 40-63 with `file_anchors` and `scope_directories` as `@property` (lazy, only evaluated if accessed). |
| `tests/test_containment_lifecycle.py` (lines 1-60) | Confirm `_run_lifecycle` subprocess helper exists | Lines 1-24: imports (missing `time`, `pytest`). Lines 25-38: `_load_lifecycle_module` (in-process importlib loader). **Lines 41-54: `_run_lifecycle` (subprocess invocation)** — exactly the helper the new Round 4 test needs. |
| `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` | Full plan re-read for edit planning | 1625 lines (fourth draft). All 9 tasks, all prior-round resolution map entries, architecture paragraph, scope notes, constraint list, file structure table. |

### Architecture: T-03 Affected Layers

| Layer | File | Current State | T-03 Target State |
|-------|------|---------------|-------------------|
| Core helper | `server/containment.py:290-310` | `clean_stale_files` returns `None`, uses `shakedown_path.glob(pattern)` loop, silently swallows OSError | Returns `CleanStaleResult` with 4 buckets, three-stage failure check (`lstat`/`stat`/`os.listdir`), raises on root failures, captures per-file failures |
| CLI wrapper | `scripts/clean_stale_shakedown.py` | Calls `clean_stale_files(...)` and returns 0 | Captures result, prints `result.report()` to stderr, returns 0 (outer `try/except Exception` at lines 44-52 handles any raise with "clean_stale_shakedown failed: unexpected error" and exit 1) |
| Hook handler | `scripts/containment_lifecycle.py:73` | Calls `clean_stale_files(...)` in `_handle_subagent_start` | Captures result, `_log_error(result.report(prefix="containment-lifecycle: "))` on `had_errors`. Outer boundary at `main():184-188` unchanged — still fail-open with `return 0`. |
| Smoke-setup | `scripts/containment_smoke_setup.py:118` | Calls `clean_stale_files(...)` at top of `prepare_scenario` | Captures result, `print(result.report(prefix="containment_smoke_setup: "), file=sys.stderr)` on `had_errors`. Outer `__main__` wrapper at lines 505-510 unchanged — still raises to exit 1 on any exception. |

### Key Locations Mapped

| Concept | Location |
|---------|----------|
| `clean_stale_files` current implementation | `server/containment.py:290-310` |
| `_STALE_PATTERNS` tuple (11 glob patterns) | `server/containment.py:12-24` |
| Stale pattern examples | `active-run-*`, `seed-*.json`, `scope-*.json`, `transcript-*.jsonl`, `transcript-*.done`, etc. |
| `shakedown_dir(data_dir)` helper | `server/containment.py:27-30` |
| `_log_error` helper (lifecycle) | `scripts/containment_lifecycle.py:43-44` |
| Fail-open `main()` boundary | `scripts/containment_lifecycle.py:184-188` |
| Cleanup call in smoke-setup | `scripts/containment_smoke_setup.py:118` |
| `_scenario_definition` function | `scripts/containment_smoke_setup.py:364-498` |
| Unknown scenario_id error | `scripts/containment_smoke_setup.py:494-497` |
| `_run_lifecycle` subprocess helper | `tests/test_containment_lifecycle.py:41-54` |
| `_load_lifecycle_module` in-process helper | `tests/test_containment_lifecycle.py:30-38` |
| Existing symlink skip pattern | `tests/test_containment.py:81` (in `test_is_path_within_scope_denies_symlink_resolving_outside`) |
| T-03 plan file | `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` |
| Prior handoff (resumed from) | `docs/handoffs/archive/2026-04-10_07-08_t-04-published-pr-102-cleaned-local-main-drift-remains.md` |

### Dependency Graph for T-03 Edit Area

```
clean_stale_files (server/containment.py)
  ├── called by: clean_stale_shakedown.py (CLI wrapper)
  │     └── outer try/except Exception → exit 1 with "clean_stale_shakedown failed"
  │
  ├── called by: containment_lifecycle.py:_handle_subagent_start (line 73)
  │     └── call chain: _handle_subagent_start → handle_payload → main()
  │           └── main()'s try/except Exception at lines 184-188
  │                 → catches and logs "containment-lifecycle: internal error (<exc>)"
  │                 → returns 0 (FAIL-OPEN BOUNDARY)
  │
  └── called by: containment_smoke_setup.py:prepare_scenario (line 118)
        └── if prepare_scenario raises, bubbles to __main__ wrapper at lines 505-510
              → "containment_smoke_setup failed: <exc>" + exit 1

Test infrastructure:
test_containment.py → tests clean_stale_files directly (13 new tests in T-03)
test_containment_lifecycle.py → tests lifecycle behavior
  ├── _load_lifecycle_module (in-process) → for per-file wiring test
  └── _run_lifecycle (subprocess) → for new root-level test (Round 4)
test_containment_smoke_setup.py (NEW FILE in T-03) → tests smoke-setup caller wiring
  └── _load_smoke_setup_module (in-process, same pattern as lifecycle)
```

### Patterns Identified

- **Importlib-based script loading for in-process tests.** Both `_load_lifecycle_module` and the new `_load_smoke_setup_module` (Task 8 Step 5) use `importlib.util.spec_from_file_location` + `spec.loader.exec_module(module)` to load `scripts/*.py` as pytest-accessible modules. This bypasses the need for the scripts to be on `sys.path`. Pattern established at `test_containment_lifecycle.py:30-38`.
- **Subprocess invocation via `[sys.executable, SCRIPT]`.** `_run_lifecycle` at `test_containment_lifecycle.py:41-54` uses `subprocess.run([sys.executable, SCRIPT], input=json.dumps(payload), capture_output=True, text=True, env={**os.environ, "CLAUDE_PLUGIN_DATA": str(data_dir)})`. This pattern works because pytest runs under uv-managed Python and `sys.executable` resolves to the same interpreter. The new Round 4 test reuses this exact pattern.
- **Script `__main__` pattern.** Both `containment_lifecycle.py` and `containment_smoke_setup.py` use the `if __name__ == "__main__": try: raise SystemExit(main()) except Exception as exc: print(...); raise SystemExit(1) from exc` pattern. The lifecycle one is fail-open at `main()`'s inner try/except; the smoke-setup one is fail-fast at the `__main__` wrapper.
- **Lazy `RepoPaths` property evaluation.** `RepoPaths.file_anchors` and `RepoPaths.scope_directories` are `@property`-decorated, so constructing `RepoPaths` does NOT evaluate them. This lets tests construct minimal `RepoPaths` with non-existent file paths without triggering validation.
- **Three-layer test seam in `prepare_scenario`.** Cleanup (line 118) → session resolution (line 119) → live-conflict check (line 121) → scenario definition (line 127) → scenario branches. Each layer is a potential monkeypatch seam for decoupling tests from downstream scenario choreography.

### Conventions Observed

- **Error format convention:** Every error message follows `"{operation} failed: {reason}. Got: {input!r:.100}"` pattern per global CLAUDE.md. The plan's new `clean_stale_files` errors match this: `"clean_stale_files failed: cannot lstat shakedown root. Got: {exc!r:.100}"`, `"clean_stale_files failed: shakedown root is unreadable (possible broken symlink). Got: {exc!r:.100}"`, etc.
- **Caller prefix convention:** Lifecycle logs use `"containment-lifecycle: "` prefix (note hyphen); smoke-setup logs use `"containment_smoke_setup: "` prefix (note underscore, matching the filename). Wrapper uses no prefix (single-source context).
- **Skip pattern for platform-conditional tests:** `@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() == 0, reason=...)` — skips on Windows (no `geteuid`) and when running as root (chmod 0o000 bypassed). Established pattern now used by two Round 3/4 tests sharing the same guard.
- **Symlink skip pattern:** `try: link.symlink_to(target); except OSError as exc: pytest.skip(f"symlink creation unavailable: {exc}")` — established at `test_containment.py:81` and reused for the dangling-symlink root test in Task 4.
- **Ruff file-scoped checking:** Plan uses file-scoped `uv run ruff check <files>` rather than package-wide `uv run ruff check` because the package has pre-existing failures in unrelated files (`codex_runtime_bootstrap.py`, `tests/conftest.py`, `tests/test_credential_scan.py`, `tests/test_dialogue_profiles.py`) documented in the resumed handoff.

### Surprising Findings

- **Stat on `chmod 0o000` directory succeeds.** Verified in Round 3 via a Python 3.14 one-liner. `stat()` on a directory only requires execute permission on the *parent*, not read permission on the directory itself. So `chmod 0o000 shakedown/` still returns `Path.stat()` mode `0o40000` with `S_ISDIR` true. The read-bit failure only surfaces at the *listing* step (`os.listdir` or `Path.glob`). This is why the enumeration guard is a *separate layer* from the two-stage root check.
- **`Path.glob` silently returns `[]` on the same input.** Verified in same Round 3 one-liner. `Path.glob()` internally uses `_scandir` which catches `OSError` in the walker. No exception, just an empty iterator. This was the Round 3 Critical finding — the algorithm could not distinguish "directory has no matching files" from "directory cannot be read".
- **Lifecycle `main()` has THREE fail-open exit points.** Not just the one at lines 184-188. Also line 175 (invalid JSON payload → `return 0`) and line 178 (non-dict payload → `return 0`). All three follow the same "log to stderr, return 0" pattern. The Round 4 design decision applies to all three, not just the innermost.
- **`handle_payload` dispatch is a public function, not a method.** `scripts/containment_lifecycle.py:47` defines `handle_payload(payload, *, data_dir)` at module level, dispatching to `_handle_subagent_start` or `_handle_subagent_stop`. This is relevant because tests that want to exercise the dispatch logic without going through `main()`'s JSON parsing can call `handle_payload` directly with a Python dict.

## Context

### Mental Model

**Framing:** This is a boundary-policy problem, not an algorithm-correctness problem.

The core algorithm (three-stage failure check: `lstat` → `stat` → `os.listdir`) was fully debugged by Round 3. Round 4's findings all live at the *boundaries* between the algorithm and its callers. The question evolved from "does the algorithm detect the failure?" to "does the caller's exit-code contract surface the detection, and do the tests assert on the surfacing mechanism rather than on happy-path propagation?"

The four-round review arc makes more sense through this lens:
- Round 1: algorithm surface (per-file operations)
- Round 2: algorithm root-level (dangling symlinks)
- Round 3: algorithm discovery layer (`Path.glob()` swallowing)
- Round 4: caller-boundary policy (fail-open explicit, tests measure stable contracts)

**Core insight:** An algorithm that correctly raises OSError inside a boundary that silently converts all exceptions to `return 0 + stderr log` is indistinguishable from an algorithm that does nothing — UNLESS the observability surface (stderr contents) is contracted and tested. The Round 4 subprocess test is the first test that asserts on BOTH sides of the conversion (`returncode == 0` AND `caller prefix + actionable context in stderr`).

**Mental model:** "Defense in depth" for observability: every layer must independently contract its failure surface, and tests must assert on each layer's contract separately. Algorithm-level tests can pin algorithm behavior; caller-wiring tests must pin caller behavior; subprocess-boundary tests must pin subprocess behavior. None of these substitute for each other.

### Review Round Progression

| Round | Verdict | Findings | Resolution Pattern |
|-------|---------|----------|-------------------|
| 1 | (first draft) | P1: root `exists()` swallows; P2: count-only reports; P2: `monkeypatch.setattr(Path, "stat")` breaks `.exists()`; P3: `rm -rf` violates CLAUDE.md | Two-stage lstat/stat check, `report()` with path+error_repr, scoped `monkeypatch.context()`, switch to `trash` |
| 2 | (second draft) | P2: dangling symlink root still collapses; P2: smoke-setup wiring not testable (file didn't exist); P3: multi-line reports lose caller attribution | Confirmed two-stage check catches dangling symlinks, created new `test_containment_smoke_setup.py`, `report(prefix=...)` applies to every line |
| 3 | Reject | **Critical:** `Path.glob()` silently returns `[]` on unreadable dirs; **High:** no enumeration-failure test; **Minor:** test count drift | Stage 3 (`os.listdir` + `fnmatch`), two enumeration-failure tests (portable mock + real chmod), test count bookkeeping |
| 4 | Minor revision | **High:** lifecycle fail-open implicit; **Medium:** smoke-setup test overfitted; **Medium:** no root-level caller test; **Low:** eager scan unstated | Explicit Fail-Open Hook Policy design decision + constraint #11, monkeypatch `_scenario_definition` direct seam, subprocess root-level test via `_run_lifecycle`, inline scale tradeoff note |

### Environment State

- **Working directory:** `/Users/jp/Projects/active/claude-code-tool-dev`
- **Branch:** `fix/t03-stale-cleanup-observability` (based on `origin/main` at `fd7c9365`)
- **Git state:** Clean working tree except for untracked plan file `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md`
- **Current commit:** `fd7c9365` — the merge commit from PR #102 (T-04 wrapper fix) — this is the base for the T-03 branch
- **Plan file state:** Fifth draft, 1793 lines, fully written, not yet committed
- **No code changes to `containment.py`, scripts, or tests yet** — the plan documents future changes but none have been applied

### Project State

T-03 is the next ticket in the correctness hardening arc for codex-collaboration. Prior work:
- **T-04 (PR #102, merged last session):** `scripts/clean_stale_shakedown.py` wrapper script fix — script path handling, `CLAUDE_PLUGIN_DATA` validation. This is the CLI wrapper that calls `clean_stale_files`.
- **T-03 (this session):** `server/containment.py:clean_stale_files` hardening — rewrites the function to return `CleanStaleResult` with explicit failure modes at every layer. Wires the result through all three callers with caller-attributed stderr logs.

After T-03 ships, the next expected ticket is T-02 or similar (the `read_active_run_id` / `read_json_file` lenient helpers migration) — but that's explicitly out of scope for this plan per the scope notes.

## Learnings

### Fail-open policy is a first-class architectural decision that must be documented explicitly

**Mechanism:** When a system has a hook-runner boundary that converts exceptions to exit codes (as `containment_lifecycle.py:main()` does at lines 184-188), "let exceptions propagate" is not a real option — the boundary is structurally upstream of wherever propagation would deliver them. The correct design choice is to either (a) remove the boundary or (b) make the boundary's contract explicit and test the observable surface downstream of it.

**Evidence:** Round 4 High finding forced the explicit choice. The prior drafts' "naturally propagates" language was misleading because it described the flow *up to* `main()` but not the conversion *at* `main()`. The reviewer caught this by reading the actual `main()` source and observing that the plan's test assertions (on `had_errors` logged via `_log_error`) only tested the in-process path, not the exit-code conversion.

**Implication:** Any plan that makes claims about "failure surfaces" through a script that has a `try/except Exception → return 0` boundary must explicitly say whether that boundary is intentional and must test the observable surface downstream of it (stderr, side effects, observable state changes), not the exception type that reached the boundary. Future plans touching hook scripts need to make this check part of their initial drafting, not wait for a review round.

**Watch for:** Other hook scripts in the codex-collaboration plugin that likely have similar `try/except → return 0` patterns at their entry points. Grep `scripts/*.py` for `except Exception` near `return 0` — any match is a potential future instance of this pattern.

### Tests that measure stable contracts survive refactors better than tests that measure implementation paths

**Mechanism:** The old smoke-setup wiring test was coupled to `scenario_id="scope_file_remove"` + `run_id=None` raising a specific RuntimeError. That RuntimeError is a scenario-specific validation path that could change if the scenario was refactored (renamed, moved validation earlier, changed error message). The test's *intent* was "verify that `prepare_scenario` logs cleanup errors before any downstream logic runs" but its *implementation* was "verify that this specific error path is reached". Any refactor to the validation changed the implementation without changing the intent — and broke the test.

**Evidence:** Reviewer's Round 4 Medium #1 finding: "A harmless refactor that validates `scope_file_remove` earlier, renames the scenario, or changes the post-cleanup branch point will break the test even if the cleanup logging is still correct. The test becomes a maintenance trap."

The fix (monkeypatching `_scenario_definition` to raise a generic sentinel) tests the stable contract directly: "cleanup runs first" (established by `prepare_scenario`'s structure, which puts `clean_stale_files` at line 118 before everything else), "had_errors triggers logging" (established by Step 2's `if cleanup_result.had_errors:` block), "termination happens after logging" (established by the sentinel raising from a function that runs after cleanup).

**Implication:** When designing wiring tests, ask "what's the STABLE thing under test?" and find a seam that tests exactly that. If the seam doesn't exist naturally, prefer monkeypatching a stable module-level function over relying on a specific error path that could shift with refactors. The monkeypatch approach is more invasive but more robust.

**Watch for:** Other tests in the codebase that rely on specific error message text or specific validation orderings. These are fragility hotspots. Grep for `pytest.raises(.*, match="` — the `match=` pattern is a coupling smell when the matched text is specific to one code path.

### Empirical verification before fixing is disproportionately valuable for boundary-condition bugs

**Mechanism:** Both Round 3 and Round 4 fixes required empirical verification of claims that could otherwise have been argued from documentation or intuition. In Round 3, a Python 3.14 one-liner verified that `Path.glob()` silently returns `[]` on `chmod 0o000` while `os.listdir` raises. In Round 4, reading `containment_lifecycle.py:184-188` verified that `main()` catches `Exception` and returns `0`. Without these verifications, the fixes would have been drafted on assumption and the plan would have been vulnerable to another review round.

**Evidence:** Round 3 verification output: `Path.glob("seed-*.json") returned: []`, `os.listdir raised: PermissionError(13, 'Permission denied')`, `Path.stat succeeded with mode=0o40000`. Round 4 verification: confirmed `try: handle_payload(...); except Exception as exc: _log_error(...); return 0` at lines 184-188 exactly as reviewer claimed.

**Implication:** For any plan revision responding to a specific code-location claim, the first step should be "read that exact location and confirm". This takes 30 seconds to 5 minutes and converts a drafting exercise into a defensible fix. For any plan revision responding to a stdlib behavior claim, the first step should be "run a one-liner that exercises the behavior". Python's stdlib has many "quiet failure" behaviors (`Path.exists`, `Path.is_file`, `Path.glob`, etc.) that are counterintuitive unless verified.

**Watch for:** Claims about Python stdlib behavior that rely on "documentation says X" or "in my experience Y". These are less reliable than one-liners. When a reviewer asserts a specific behavior at a specific code location, verify the location AND verify the behavior.

### Resolution maps are worth the overhead for iteratively-reviewed documents

**Mechanism:** The T-03 plan's Resolution Map now tracks 10+ findings across four review rounds with specific resolution references (which task step, which test, which design decision addresses each finding). A future reviewer can use it as a "what has already been considered" index rather than re-raising the same concerns. Without it, the plan's increasing length would make re-finding the resolution of any specific prior finding exponentially harder.

**Evidence:** The fifth draft's Resolution Map has rows for Round 1 P1/P2/P3, Round 2 P2/P3, Round 3 Critical/High/Minor, Round 4 High/Medium/Medium/Low — 10 findings each mapped to specific resolutions with line-level or task-level references. The overhead per row is ~200 characters; the savings is "did we already address X?" becoming a ctrl-F rather than a full re-read.

**Implication:** Any plan that goes through 3+ review rounds should start a Resolution Map proactively in the first revision, not retroactively add one later. Cost is low, benefit compounds with each round.

**Watch for:** Plans that grow beyond ~1000 lines without a structured resolution tracking mechanism. These are candidates for resolution map insertion.

## Next Steps

### 1. Wait for user feedback on fifth draft

**Dependencies:** None — the fifth draft is complete and waiting for review.

**What to read first:** `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` (the full plan). The user's message indicated "I will review the draft and share my feedback with you in the next session" — so they want to review asynchronously before giving execution direction.

**Approach suggestion:** Do NOT start execution without explicit user approval. The user's iterative-review pattern has been consistent: four rounds of explicit review before accepting a draft. Assume Round 5 is possible.

**Acceptance criteria:** User returns with either (a) approval + execution choice (Subagent-Driven vs. Inline), (b) a Round 5 review with more findings to address, or (c) a different direction entirely.

**Potential obstacles:** None at this stage. The plan is complete and self-contained.

### 2. Execute the plan (when approved)

**Dependencies:** User approval.

**What to read first:** The fifth draft of the plan. Each task is self-contained with exact file paths, line numbers, code snippets, test bodies, expected outputs, and diagnostic paths.

**Approach suggestion:** Subagent-Driven execution is recommended per the plan's "Execution Handoff" section. Reasons:
- Task 1's three-stage flow is dense enough that a fresh subagent walking only Task 1 (without carrying the four rounds of review context) is likely to follow the spec more literally.
- Task 4's six-scenario coverage benefits from a focused walker.
- Task 7's seven manual probes (via subprocess + bash) benefit from a focused walker.
- Task 8's three separate test patterns (in-process, subprocess, direct-module-patch) each have different semantics and benefit from explicit task-level focus.

Inline execution is an acceptable alternative if the user wants to observe execution in real time.

**Acceptance criteria:** All 9 tasks completed; all 16 new tests + 1 tightened test passing; all 3 callers updated with caller-attributed stderr logs; all manual verification steps in Task 7 executed with expected outputs matching; PR opened in draft state with the exact shape specified in Task 9.

**Potential obstacles:**
- Task 1's three-stage refactor must be applied ATOMICALLY (no partial commits). The Task 4 coverage tests assume the full Task 1 implementation is present; running them against a half-applied Task 1 would produce confusing failures.
- The `chmod 0o000` tests require non-root POSIX. If executing on a CI-like environment, two tests will skip, which is acceptable but should be verified via the expected baseline counts.
- The new plan file (untracked) needs to be committed. Decide whether to commit it as a separate docs commit before Task 1, or include it in Task 1's commit. The plan itself does not specify — the implementer should decide.

### 3. Handle a potential Round 5 review

**Dependencies:** User's feedback determines whether this is needed.

**What to read first:** If the user returns with more findings, re-read the specific sections the user references AND verify any code-location claims empirically (same pattern as Round 4).

**Approach suggestion:** Treat any Round 5 as another iteration of the same pattern — identify each finding, verify it, draft a fix, apply it, update the Resolution Map, and produce a summary. Do NOT prematurely optimize for "this is the last round" — the user's review discipline has been consistent and four rounds have been needed so far.

**Acceptance criteria:** Every Round 5 finding has a documented resolution in the Resolution Map with specific references; no prior-round fix is invalidated.

## In Progress

**What was being worked on:** Round 4 revision of the T-03 implementation plan.

**Approach:** Fourteen targeted edits to the plan file at `docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md`. Each edit is atomic and preserves surrounding context. Empirical verification of the reviewer's High claim (via reading `containment_lifecycle.py:184-188`) preceded the fixes.

**State:** Fifth draft complete (1793 lines). All four Round 4 findings resolved with evidence. File is untracked in git. Waiting for user review before execution or further iteration.

**Working:**
- All 14 plan edits applied cleanly
- Architecture paragraph acknowledges fail-open contract explicitly
- Fail-Open Hook Policy design decision is a complete subsection with rationale, contract shape table, and test coverage pointer
- Constraint #11 locks in the policy at the correctness-constraint level
- Task 8 Step 3 has both lifecycle tests (in-process + subprocess) with full bodies
- Task 8 Step 5 smoke-setup test body rewritten with direct seam (monkeypatching `_scenario_definition`)
- Task 8 Step 6 diagnostic paths updated for the new seam
- Task 9 Step 1 test table, baseline (534 → 535), and platform-conditional table re-derived
- Task 9 Step 5 PR body baseline updated
- Resolution Map has 4 new rows for Round 4 (High, Medium, Medium, Low)
- Self-Review "explicit design decisions" bumped to Three with new Fail-Open entry
- Self-Review monkeypatch scoping note extended to cover `_scenario_definition`
- Self-Review risk verification has two new bullets
- Scope notes "three rounds" → "four rounds"
- Resolution Map heading "P1-P3 across three review rounds" → "four review rounds"
- In-scope descriptions of both test files updated
- Final grep sweeps confirmed no stale "534", "15 new tests", "naturally propagate" (except intentional one), or "scope_file_remove" (except intentional one in new test docstring) references

**Not working / incomplete:**
- Plan has NOT been executed. No code changes to `containment.py`, scripts, or tests.
- Plan file is untracked in git. Needs commit decision.

**Open questions:**
- User feedback unknown. Potential Round 5.
- Execution strategy unknown (Subagent-Driven vs. Inline).
- Plan commit strategy (separate commit vs. include with Task 1).

**Immediate next action:** Wait for user feedback. If user approves with execution choice, begin executing per the chosen strategy. If user returns with Round 5 findings, apply the same empirical-verify-then-fix pattern that addressed Round 4. Do NOT start execution autonomously.

## Open Questions

1. **Will the user approve the fifth draft or issue a Round 5 review?** The `/save` invocation at the end of the session suggests they want to review asynchronously rather than give immediate direction.

2. **Which execution strategy will the user choose?** The plan offers Subagent-Driven (recommended) or Inline Execution. The choice affects whether the execution session will dispatch a subagent per task or batch through checkpoints.

3. **Should the plan file be committed separately before Task 1, or included in Task 1's commit?** The plan is untracked. Existing pattern across prior plans has been to include with the first implementation task, but the plan's review-round history is extensive enough that a separate "docs: add T-03 implementation plan" commit might be cleaner.

4. **Are there other hook scripts with similar fail-open boundaries that should be flagged for future review?** The Round 4 design decision is specific to `containment_lifecycle.py`, but the fail-open pattern likely exists elsewhere in the codex-collaboration plugin's hook scripts. Not in scope for T-03, but worth noting for future tickets.

5. **Is the operator observability contract (stderr + caller prefix) sufficient, or do we also need a telemetry emission path?** The plan pins the stderr surface but doesn't add any structured telemetry. If operators don't read stderr, the Round 4 fix doesn't help them. Out of scope for T-03 but a potential follow-up concern.

## Risks

- **Plan fatigue risk:** The plan is now 1793 lines across five drafts. A future implementer executing the plan verbatim will need to cross-reference the Resolution Map frequently to understand why specific choices were made. Mitigation: Resolution Map and Design Decisions sections are at the top of the plan and are stable anchors.

- **Subprocess test environmental dependency:** The new `test_subagent_start_surfaces_cleanup_enumeration_failure` depends on `_run_lifecycle`'s subprocess invocation succeeding. If the test environment has `sys.executable` path resolution issues (e.g., a weird virtualenv setup), the test fails with an unrelated error. Mitigation: uses the same helper that existing lifecycle tests already rely on.

- **Two chmod tests sharing skipif guard:** `test_clean_stale_files_raises_when_root_directory_unreadable` (Task 4) and `test_subagent_start_surfaces_cleanup_enumeration_failure` (Task 8) both skip under `not hasattr(os, "geteuid") or os.geteuid() == 0`. If CI migrates to a root-running container or adds Windows, BOTH tests silently skip and the enumeration failure code path has only mock-based coverage. Mitigation: the mock-based `test_clean_stale_files_raises_when_enumeration_fails` in Task 4 always runs and provides coverage of the raise path.

- **Fail-open policy lock-in via three mechanisms:** The policy is pinned by the design decision subsection, constraint #11, and the subprocess test. A future maintainer wanting to flip the policy will need to update all three. This is deliberate friction but could be frustrating if the policy is later proven wrong. Mitigation: the design decision explicitly names change triggers ("if `SubagentStart` changes its exit-code semantics") so the unlock path is documented.

- **Plan commit timing undefined:** The plan file is untracked. If executing Task 1 first without committing the plan, the implementation commits will reference a plan that's not in git. Small risk but worth deciding before execution starts.

- **Empirical verifications from Round 3 assumed to still hold:** The Python 3.14 `Path.glob` silent-return-[] behavior was verified once. Python could theoretically change this in a patch release, though unlikely for a behavior that's documented-but-subtle. No mitigation needed but worth noting.

## References

**Plan file (the primary artifact of this session):**
- `/Users/jp/Projects/active/claude-code-tool-dev/docs/superpowers/plans/2026-04-10-t03-stale-cleanup-observability.md` — fifth draft, 1793 lines, untracked

**Target files for T-03 execution:**
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/server/containment.py` — `clean_stale_files` at lines 290-310, `_STALE_PATTERNS` at 12-24
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py` — CLI wrapper
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/containment_lifecycle.py` — `_handle_subagent_start` at line 63, `main()` fail-open at 184-188
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/scripts/containment_smoke_setup.py` — `prepare_scenario` at 107, cleanup call at 118, `_scenario_definition` at 364
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/tests/test_containment.py` — existing test file (Task 1-6 add 13 tests)
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/tests/test_containment_lifecycle.py` — existing test file with `_load_lifecycle_module` at 30-38 and `_run_lifecycle` at 41-54 (Task 8 adds 2 tests)
- `/Users/jp/Projects/active/claude-code-tool-dev/packages/plugins/codex-collaboration/tests/test_containment_smoke_setup.py` — NEW FILE to be created in Task 8 Step 5

**Prior handoff (resumed from):**
- `/Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-10_07-08_t-04-published-pr-102-cleaned-local-main-drift-remains.md`

**Ticket:**
- `/Users/jp/Projects/active/claude-code-tool-dev/docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md`

**Base commit:**
- `fd7c9365` — merge commit from PR #102 (T-04), base for the `fix/t03-stale-cleanup-observability` branch

## Gotchas

1. **`containment_lifecycle.py:main()` is fail-open by construction, not by accident.** Lines 184-188 catch every exception from `handle_payload` and return `0`. This is deliberate: `SubagentStart` treats non-zero as "block the spawn", and a containment-state defect must not escalate into blocking unrelated agent spawns. Any drafting language that says exceptions "propagate naturally" through this function is wrong. Use the explicit Fail-Open Hook Policy design decision framing.

2. **In-process tests via `_load_lifecycle_module` CANNOT observe `main()` behavior.** They call `_handle_subagent_start` directly. To test `main()`'s fail-open conversion, MUST use subprocess via `_run_lifecycle` at lines 41-54 of `test_containment_lifecycle.py`. This is a structural requirement, not a preference.

3. **`stat()` on a `chmod 0o000` directory succeeds.** Because `stat()` on a directory only needs execute permission on the *parent*, not read permission on the directory itself. Returns mode `0o40000` with `S_ISDIR` true. The read-bit failure surfaces only at the listing step (`os.listdir` raises, `Path.glob` silently returns `[]`). The enumeration guard is a *separate layer* from the two-stage root check, not a consequence of it. Constraint #5 in the plan.

4. **`Path.glob()` silently returns `[]` on `chmod 0o000` directories.** `_scandir` wrapper catches `OSError` in the walker. No exception. This is the Round 3 Critical finding. Never use `Path.glob()` for observability-sensitive cleanup. Use `os.listdir()` + `fnmatch.fnmatch()`. Constraint #4 in the plan.

5. **Monkeypatching `smoke_setup._scenario_definition` works because `prepare_scenario` calls it via module globals.** When the module is loaded via `importlib.util.spec_from_file_location`, the function is in the loaded module's namespace. `prepare_scenario`'s internal reference to `_scenario_definition` resolves via normal Python LEGB rule to the module global. `monkeypatch.setattr(smoke_setup, "_scenario_definition", stub)` updates that module global, so subsequent `prepare_scenario` calls find the stub. If `prepare_scenario` were refactored to call `_scenario_definition` via a parameter or local binding, the monkeypatch would become wrong.

6. **`RepoPaths.file_anchors` and `.scope_directories` are `@property` (lazy).** Constructing `RepoPaths` does NOT evaluate them. This is why the new smoke-setup test can construct `RepoPaths` with non-existent file paths — `_scenario_definition` is stubbed and never accesses the properties, so validation doesn't trigger. If a future change makes the properties eager (e.g., computed in `__post_init__`), the test would need real paths.

7. **Chmod `0o000` tests require `try/finally` to restore `0o755`.** Without the restore, pytest's `tmp_path` fixture cannot walk into the directory to clean up, and teardown raises — masking the real test failure. Both Round 3's and Round 4's chmod tests include the restore. The subprocess test's restore MUST happen even if the assertions below fail, otherwise the test failure becomes a teardown error.

8. **Plan commit count (8) is independent of the number of tests added.** The new subprocess test goes into `test_containment_lifecycle.py` which is already being modified in Task 8 Step 3. No new task added, no new commit needed. Task 9's verification expectations (8 commits, 7 files) are unchanged by this session's work.

9. **`containment_smoke_setup.py` has its own `try/except Exception → exit 1` boundary at lines 505-510.** Different from `containment_lifecycle.py`'s fail-open. The smoke-setup is a standalone script (not a hook), so fail-fast at the `__main__` wrapper is correct. Don't confuse the two policies — lifecycle is fail-open, smoke-setup is fail-fast.

10. **User's review discipline is consistent across rounds.** Four review rounds have been needed so far. Each round uses the same structured format (Premise Check, Critical Failures, High-Risk Assumptions, etc.). Do NOT assume the next round will be "just approval" — assume it could be Round 5 with more findings, and verify all claims empirically before drafting responses.
