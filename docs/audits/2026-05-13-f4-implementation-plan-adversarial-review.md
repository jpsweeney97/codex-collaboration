# Adversarial Review - F4 implementation plan

**Date:** 2026-05-13
**Target:** `docs/superpowers/plans/2026-05-13-f4-audit-retention-implementation.md` (untracked, 2053 lines)
**Reviewed against:** F4 design at `HEAD=977b962` (929 lines)
**Scope level:** `slice`
**Input type:** first adversarial pass over the integrated F4 implementation plan
**Methodology:** plan-vs-design conformance + carry-forward conformance + code-shape snippet correctness + test-coverage diff + plan-craft (stop conditions, branch flow, intermediate states) + code-state verification against the live repo
**Archetypes:** Implementation plan for data-pipeline retention slice / internal MCP tool
**Stakes:** high (last gate before `superpowers:subagent-driven-development` touches `server/journal.py`)

## 1. Review Snapshot

| Signal | Count |
| ------ | ----- |
| Blocking-class findings | 2 (F1, F2) |
| High-class findings | 0 |
| Moderate-class findings | 2 (F3, F4) |
| Low-class findings | 1 (F5) |
| Design-level changes triggered | 0 |
| Findings confirmed against plan + design + live repo | 5 |
| False alarms dropped during verification | 2 (asdict-unused, bootstrap-logger-duplicate) |

**Label set:**

| Finding | Label | Class | Plan-level fix? |
| --- | --- | --- | --- |
| F1 | `blocking-completeness` | Plan implements thin subset of design §8 test plan; key invariants unpinned | Yes — add missing tests across Tasks 2-5 |
| F2 | `blocking-correctness` | Analytics `_timestamp_range` includes malformed timestamps; round-10 F4 carry-forward (f) ignored | Yes — filter via `_parse_aware_iso8601`, add fixture and test |
| F3 | `moderate-visibility` | Single-writer envelope (round-8 F4 carry-forward (d)) buried in Completion Report only | Yes — add to Stop Conditions + top-of-plan Assumptions |
| F4 | `moderate-mechanical` | Task 4 Step 5 "return the quarantine paths" instruction without inlined return statement | Yes — inline the updated `return PruneSummary(...)` |
| F5 | `low-flow` | Task 0 Step 2 `git switch -c` fails if branch exists, despite fallback text | Yes — split into existence check + conditional create |

## 2. Methodology Note

This pass is the first adversarial review of a *plan* (not a *design*) in the F4 chain. Rounds 4-10 reviewed the design at successive amendment commits; this round changes target type. The plan inherits the design's stability (algorithm reviewed 10 times) but introduces **new surfaces**: test enumeration, task ordering, intermediate states, code-shape snippets, commit checkpoints, stop conditions. Those surfaces are unreviewed.

Three checks drove the pass:

1. **Design conformance.** Every design §2 contract bullet and §5.x algorithm must map to a plan task. Pass A confirmed all 17 contract bullets are addressed in code-shape.
2. **Carry-forward conformance.** Six items from rounds 7-10 (handoff (a)-(f)) must be addressed. Pass B confirmed (b), (c), (e), and partially (d) and (f). Items (a) and (f) — both `superpowers:writing-plans` deliverables — are the source of F1 and F2.
3. **Test-coverage diff.** Tallied the design §8 named tests against the plan's added tests. ~33/48 (69%) coverage with the worst gaps in §8.6 (re-runnable prune) and §8.8 (dedup-skip).

Code-citation discipline carried forward: every claim was verified against either the design at `977b962`, the plan as untracked, the round-8 audit precursor as style exemplar, OR the live `server/journal.py`, `scripts/codex_runtime_bootstrap.py`, and `skills/codex-analytics/scripts/analytics.py`. Two findings I expected to keep were dropped after verification: (a) `asdict` is already imported and used 5 times in `journal.py` — the plan's import line is additive, no unused-import; (b) bootstrap has no current logging, so the plan's `import logging` + `logger = ...` adds rather than duplicates.

Project-memory cross-check applied: `feedback_seam_leaf_consumption.md`, `feedback_retention_retain_on_uncertainty.md`, `feedback_drift_detector_manual_gate.md`, `feedback_design_zero_hit_gate.md`. F1 is partially anchored to `feedback_seam_leaf_consumption.md` because the missing §8.6 second-prune eviction test is the test that exercises the mutable-clock fixture pattern (carry-forward (a)) that round-7 surfaced.

## 3. Plan Strengths (calibration)

Before the findings, what the plan gets right — this is not throat-clearing; it bounds the criticism.

- **Code-shape snippets match the design verbatim.** `_prune_jsonl_pass`, `_quarantine_corrupt_jsonl`, `_populate_from_*_record`, `_parse_aware_iso8601`, the orchestrator try/except blocks, and `_ensure_*_seen_loaded` are near-character-identical to design §5.x.
- **TDD-first sequencing.** Every task writes failing tests before implementation, with explicit `FAIL because ...` expected output.
- **Commit checkpoints are granular.** 9 tasks, one commit per task, each commit message conforms to the F4-chain `fix(component): ...` style.
- **Carry-forward (b) implemented exactly.** Test helpers use string-typed timestamps (`timestamp: str = "2026-04-21T00:00:00Z"`), avoiding `journal.timestamp()` for fixtures.
- **Carry-forward (c) implemented exactly.** Task 9 Step 5 runs the `rg "glob|rglob|iterdir|scandir|listdir"` review-gate as a manual process step, matching the round-7 F5 resolution that named it as "not a CI step."
- **Carry-forward (e) implemented exactly.** Task 6 covers `recovery-and-journal.md` + `decisions.md`; Task 7 covers `SKILL.md` + `analytics.py`. All four consumer surfaces are scheduled.
- **`newline="\n"` accounting matches design §9.** Three appender pins (Task 2 Step 6) + one prune temp-file pin (Task 2 Step 5) = 4 hits; Task 9 Step 4 expects 4. Exact.
- **Stop conditions explicitly include the dialogue-exception-broadening trap** (round-6 F1 carry-forward). This is the prior incident the design closed.
- **Self-Review Checklist at end is a real backstop.** Maps design behaviors to tasks; cheap to verify; reads as if the author re-read §8 of the design.

That said.

## 4. Adversarial Findings

### F1. Plan implements thin subset of design §8 test plan

- **Lens:** Test-coverage conformance (plan vs design)
- **Severity:** BLOCKING (completeness-class; carry-forward (a) ignored)
- **Decision state:** New tests must be added across Tasks 2, 3, and 4 (and a new orchestration task for mutable-clock fixture)
- **Anchor:** Plan Task 2 Step 1-3 vs design §8.1-§8.8
- **Problem:** Design §8 names ~48 distinct tests across §8.1-§8.9. Plan adds ~33 — 69% coverage. The gaps are not symmetric: §8.6 (re-runnable prune) and §8.8 (dedup-skip) are at 25%. Specifically missing:

  **Design §8.1 — Pruning correctness happy-path (4 missing):**
  - `test_prune_audit_logs_retains_records_within_ttl` — positive case of TTL retention
  - `test_prune_audit_logs_retains_record_exactly_at_ttl_boundary` — pins against accidental `<=` inversion of the `if ts < cutoff` check
  - `test_prune_audit_logs_empty_file_is_noop` — file exists, zero records
  - `test_prune_audit_logs_returns_correct_summary_counts` — multi-record summary accuracy

  **Design §8.2 — Retain-on-uncertainty (3 missing):**
  - `test_prune_audit_logs_retains_malformed_json_line` — invalid JSON line retained as raw bytes
  - `test_prune_audit_logs_retains_non_dict_record` — array or scalar JSON line retained
  - `test_prune_audit_logs_drops_blank_lines` — blank-line drop confirmed (the only design-named drop besides expired records)

  **Design §8.5 — Clock seam (1 missing):**
  - `test_prune_audit_logs_normalizes_non_utc_aware_timestamps` — record at `+09:00`, cutoff in UTC; the cross-timezone correctness test

  **Design §8.6 — Re-runnable prune (3 of 4 missing):**
  - `test_prune_audit_logs_evicts_newly_expired_keys_on_second_run` — **this is the round-7 carry-forward (a) test that exercises the mutable-clock fixture pattern**. Without it, the entire mutable-clock helper rationale is unpinned and the §6.4 fixture pattern is unused.
  - `test_prune_audit_logs_restores_per_file_flag_after_each_pass` — pins independent per-file restoration (load-bearing for §5.6 contract)
  - `test_prune_audit_logs_partial_failure_keeps_outcomes_flag_cleared` — pins round-4 PA F1 (per-file flag invalidation enables partial-failure isolation)

  **Design §8.7 — Dedup-set construction (4 missing):**
  - `test_ensure_audit_seen_loaded_tolerates_corrupt_jsonl_line` — JSONL-line malformed tolerance on runtime path
  - `test_ensure_outcomes_seen_loaded_tolerates_corrupt_jsonl_line` — mirror
  - `test_ensure_audit_seen_loaded_does_not_mark_initialized_on_failure` — pins non-UTF-8 exception keeps flag `False`; second call retries (load-bearing for §5.7 contract)
  - `test_ensure_outcomes_seen_loaded_does_not_mark_initialized_on_failure` — mirror

  **Design §8.8 — Dedup-set update invariant (3 of 4 missing):**
  - `test_append_dialogue_audit_event_once_skips_when_key_in_seen_set` — the basic dedup-skip behavior is not directly tested. Plan covers update-after-success but not skip-when-present.
  - Mirror tests for `append_dialogue_outcome_once` and `append_delegation_outcome_once` (basic skip)

  Plus the design-implicit "Mirror the invalid-UTF-8 startup test for `outcomes.jsonl`" prose in Task 4 Step 1, which leaves `summary.outcomes_quarantined_to` and the symmetric quarantine path unwritten.

- **Impact:** Three concrete regression vectors slip past the suite:
  1. **`<` → `<=` boundary inversion**: a refactor that flips the comparison would drop boundary records silently. The boundary-pin test was named in design §8.1 specifically against this.
  2. **Mutable-clock fixture pattern (carry-forward (a)) is never exercised.** Plan defines `_fixed_clock` (single-call) but no `clock_state = [t0]` mutable container. Design §6.4 fixture-pattern table line "Time-advance between prune calls" is unused. A future test author writing time-sensitive prune tests would have no idiom in the suite to copy.
  3. **Basic dedup-skip behavior is not pinned.** Test coverage is "we add to the seen-set after success" and "we don't add on failure" — but the consumer-visible contract is "we skip the IO when the key is present." A refactor that breaks `if key in self._audit_seen: return` (e.g., a typo to `if key not in ...`) would not surface in any plan-listed test.

- **Verification:** Confirmed by line-by-line walk of plan Tasks 2-5 against design §8.1-§8.9. Tally by section:

  | Design §8 section | Tests named | Tests planned | Coverage |
  | --- | --- | --- | --- |
  | §8.1 Pruning happy-path | 6 | 2 | 33% |
  | §8.2 Retain-on-uncertainty | 9 | 5 | 56% |
  | §8.3 Raw-line retention | 3 | 3 | 100% |
  | §8.4 Atomic replacement | 2 | 2 | 100% |
  | §8.5 Clock seam | 3 | 2 | 67% |
  | §8.6 Re-runnable prune | 4 | 1 | 25% |
  | §8.7 Dedup-set construction | 9 | 5 | 56% |
  | §8.8 Dedup-set update invariant | 4 | 1 | 25% |
  | §8.9 Bootstrap integration | 8 | 8 | 100% |
  | **Total** | **48** | **29** | **60%** |

  Note: this tally is stricter than the 69% in §2 because it counts "Mirror the invalid-UTF-8 startup test for `outcomes.jsonl`" as a missing test rather than a planned one. Either way, §8.6 and §8.8 are <50% and contain load-bearing invariants.

- **Resolution:** Amend Tasks 2, 3, and 4 to enumerate the missing tests. Specifically:
  - Add to Task 2 Step 2: `test_prune_audit_logs_retains_record_exactly_at_ttl_boundary`, `test_prune_audit_logs_retains_records_within_ttl`, `test_prune_audit_logs_retains_malformed_json_line`, `test_prune_audit_logs_retains_non_dict_record`, `test_prune_audit_logs_drops_blank_lines`, `test_prune_audit_logs_empty_file_is_noop`, `test_prune_audit_logs_normalizes_non_utc_aware_timestamps`.
  - Add a new task (or new step in Task 2) for the mutable-clock fixture: define `_mutable_clock(at: list[datetime])` helper, add `test_prune_audit_logs_evicts_newly_expired_keys_on_second_run`, `test_prune_audit_logs_restores_per_file_flag_after_each_pass`, `test_prune_audit_logs_partial_failure_keeps_outcomes_flag_cleared`.
  - Add to Task 3 Step 1-2: `test_append_dialogue_audit_event_once_skips_when_key_in_seen_set` and mirror tests for both outcomes append-once methods.
  - Add to Task 3 Step 2: the four `_ensure_*_seen_loaded` resilience tests (tolerates_corrupt_jsonl_line, does_not_mark_initialized_on_failure for audit and outcomes).
  - Add to Task 4 Step 1: an explicit `test_prune_audit_logs_quarantines_outcomes_on_invalid_utf8` (mirror of the audit version) rather than a prose "Mirror the invalid-UTF-8 startup test" instruction.

### F2. Analytics `_timestamp_range` does not filter malformed timestamps

- **Lens:** Carry-forward conformance (round-10 F4 carry-forward (f))
- **Severity:** BLOCKING (correctness-class — produces user-visible wrong output)
- **Decision state:** Helper logic + a fixture-extended analytics test
- **Anchor:** Plan Task 7 Step 3 `_timestamp_range`; round-10 F4 carry-forward (f) per handoff; design §3 In-Scope analytics requirement; live `skills/codex-analytics/scripts/analytics.py` lines 83-89 (which currently print `records` count without any range)
- **Problem:** The plan's `_timestamp_range` helper picks all string-typed `timestamp` values and sorts them lexically:

  ```python
  def _timestamp_range(records: list[dict[str, object]]) -> str:
      timestamps = sorted(
          value for record in records
          if isinstance((value := record.get("timestamp")), str)
      )
      if not timestamps:
          return "n/a"
      return f"{timestamps[0]} to {timestamps[-1]}"
  ```

  Lexical sort of ISO 8601 Z-form strings is **chronologically correct** — that part is fine. But the `isinstance(value, str)` filter accepts any string, including malformed ones. Two production scenarios produce wrong output:

  1. A record with `"timestamp": "not-a-date"` (string but unparseable). `"not-a-date"` sorts after any `"2026-..."` (digit-comes-before-lowercase), so it becomes `timestamps[-1]`. The displayed range becomes `"2026-04-01T00:00:00Z to not-a-date"` — a string the user reads as "the data extends until not-a-date."
  2. A record with `"timestamp": "2026-04-01T00:00:00"` (string, no timezone). This sorts lexically with the well-formed strings but is design-§5.3 *retained-on-uncertainty* — it should not represent the operational range. Lexical sort would place it between the well-formed strings, possibly contracting the displayed range to a misleading point.

  Round-10 F4 carry-forward (f) explicitly named "parseable-range rules, missing-timestamp counts, per-file vs combined ranges." The plan picks the easy approach (string-typed, lexical sort), defers all three semantics decisions silently. None of "parseable-range rules" / "missing-timestamp counts" appears in the plan.

- **Impact:**
  - **User-visible wrong output**: analytics consumer sees malformed timestamps in their operational range. The plan's whole point per design §3 is so users "do not mistake post-prune records for total historical analytics" — but the range becomes meaningless once a malformed record is in the file. Malformed records are explicitly retained per §5.3.
  - **Carry-forward (f) is unaddressed.** Round-10 F4 was a deferred-probe item, the plan was the place to address it.
  - **Test as written would pass** because the implied fixture for `test_data_header_reports_observed_timestamp_ranges` includes only well-formed timestamps (the test asserts specific timestamps appear in output). The bug doesn't surface in the suite.

- **Verification:** Confirmed by reading plan Task 7 Step 3 helper + plan Task 7 Step 1 test. Current `analytics.py:83-89` (live repo) prints `records` count only — there is no existing timestamp-range code to regress, so this is net-new analytics code that ships with a defect. Live `analytics.py` line 87: `f"- Outcomes: \`{outcomes_path}\` ({total_outcome_records} records{outcomes_note})"`.

- **Resolution:** Two changes.

  1. Filter via `_parse_aware_iso8601` (importing from journal or re-implementing) so only parseable timezone-aware timestamps define the range. Also report a "missing/malformed timestamps" count for transparency:

     ```python
     def _timestamp_range(records: list[dict[str, object]]) -> tuple[str, int]:
         parseable: list[datetime] = []
         missing_or_malformed = 0
         for record in records:
             ts = _parse_aware_iso8601(record.get("timestamp"))
             if ts is None:
                 missing_or_malformed += 1
             else:
                 parseable.append(ts)
         if not parseable:
             return "n/a", missing_or_malformed
         parseable.sort()
         return f"{parseable[0].isoformat()} to {parseable[-1].isoformat()}", missing_or_malformed
     ```

     Print format: `Outcomes observed timestamp range: 2026-04-01T00:00:00+00:00 to 2026-04-21T00:00:00+00:00 (3 records with missing or malformed timestamps)`.

  2. Add a test that pins the parseable-only behavior:

     ```python
     def test_data_header_excludes_malformed_timestamps_from_range(self, tmp_path: Path) -> None:
         # fixture includes one record with timestamp "not-a-date"
         output = _run_analytics(tmp_path)
         assert "not-a-date" not in output
         assert "1 records with missing or malformed timestamps" in output  # or similar
     ```

### F3. Single-writer envelope buried in Completion Report only

- **Lens:** Carry-forward conformance (round-8 F4 carry-forward (d))
- **Severity:** MODERATE (visibility-class — design-level invariant present but not load-bearing in the plan flow)
- **Decision state:** Promote to Stop Conditions + top-of-plan Assumptions
- **Anchor:** Plan Stop Conditions block (5 items, no concurrency mention); Plan Completion Report Template Remaining Risks ("Concurrent MCP processes sharing one plugin data root remain unsupported."); design §2 single-writer envelope paragraph
- **Problem:** Round-8 F4 carry-forward (d) per handoff: "Single-writer/no-lock envelope must remain visible as a hard assumption (round-8 F4)." The plan mentions the assumption exactly once: in the Completion Report Template's Remaining Risks section. By the time an implementer or reviewer reads that line, the work is done and the report is being written. The visibility intent was to keep the assumption load-bearing during implementation — specifically so a well-meaning implementer doesn't add a `multiprocessing.Lock` or file-lock during this slice (which would expand scope) AND doesn't accidentally relax the assumption with a "this seems racy, let me defend it" pattern.

- **Impact:** Implementer skimming the plan's top sections (Goal, Architecture, Files And Responsibilities, Stop Conditions) does not see the assumption. Stop conditions catch behaviors that should stop work; assumptions catch claims the plan does *not* defend. Both are appropriate places. Neither is used.

- **Verification:** Confirmed by grep of plan Goal/Architecture/Stop Conditions: the only mention of concurrency or single-writer is in the Completion Report Remaining Risks tail.

- **Resolution:** Two changes.
  1. Add a "Hard Assumptions" block near the top (between Architecture and Files And Responsibilities) with two assumptions: (a) single-writer per `${CLAUDE_PLUGIN_DATA}` root — multi-session is unsupported; (b) host runs Python 3.11+ for `datetime.fromisoformat` Z-form support.
  2. Add a Stop Condition: "Stop if implementation pressure introduces a file lock, advisory lock, or `multiprocessing` primitive to defend the prune writer. The single-writer envelope is the design-level assumption; defending it inside F4 is out of scope."

### F4. Task 4 Step 5 instructs "Return the quarantine paths" without showing the updated return statement

- **Lens:** Plan mechanical completeness
- **Severity:** MODERATE (mechanical — silent miss-vector for an implementer)
- **Decision state:** Inline the updated `return PruneSummary(...)` block
- **Anchor:** Plan Task 4 Step 5 (lines 1311+, post-snippets)
- **Problem:** Task 4 Step 5 shows the audit and outcomes try/except blocks in full, then ends with the prose instruction "Return the quarantine paths in `PruneSummary`." The Task 2 Step 5 `return PruneSummary(...)` shown earlier has **six** kwargs; the updated return should have **eight** (adding `audit_quarantined_to=audit_quarantined_to` and `outcomes_quarantined_to=outcomes_quarantined_to`). The plan does not show the updated block.

  Two failure modes:
  - Implementer copies the Task 2 Step 5 return and never updates it → `summary.audit_quarantined_to is None` always. Task 4 quarantine tests catch this (one of them asserts `summary.audit_quarantined_to == quarantine_path`), so the loop closes. But the test failure happens at run time, not at plan-read time.
  - Implementer adds only one of the two new kwargs → asymmetric coverage; outcomes quarantine appears `None` even when set. Task 4 Step 1 prose "Mirror the invalid-UTF-8 startup test for `outcomes.jsonl`" leaves the mirror test undefined, so the asymmetric bug could slip past the suite.

- **Impact:** Time loss for the implementer to re-run the test cycle. Worse if F1 amendment is not applied first and the outcomes-quarantine mirror test is also missing (compound miss).

- **Verification:** Confirmed by re-reading Task 4 Step 5 — the snippet block ends at `new_dialogue_outcomes_seen = set(); new_delegation_outcomes_seen = set()` and the prose follows immediately.

- **Resolution:** Add the explicit return:

  ```python
  return PruneSummary(
      audit_retained=audit_stats.retained,
      audit_dropped=audit_stats.dropped,
      audit_retained_malformed=audit_stats.retained_malformed,
      outcomes_retained=outcomes_stats.retained,
      outcomes_dropped=outcomes_stats.dropped,
      outcomes_retained_malformed=outcomes_stats.retained_malformed,
      audit_quarantined_to=audit_quarantined_to,
      outcomes_quarantined_to=outcomes_quarantined_to,
  )
  ```

### F5. Task 0 Step 2 `git switch -c` fails if branch exists

- **Lens:** Plan flow correctness
- **Severity:** LOW (mechanical — known fallback documented in prose, but bash is unconditional)
- **Decision state:** Split into existence check + conditional create
- **Anchor:** Plan Task 0 Step 2
- **Problem:** Task 0 Step 2 instructs:

  > Run only if currently on `main`:
  >
  > ```bash
  > git switch -c fix/f4-audit-retention
  > ```
  >
  > Expected: `Switched to a new branch 'fix/f4-audit-retention'`
  >
  > If the branch already exists, use a timestamped suffix such as `fix/f4-audit-retention-2`. Do not commit directly to `main`.

  The bash command unconditionally runs `git switch -c`, which fails with a non-zero exit if the branch exists. The fallback prose says "use a timestamped suffix" but the bash doesn't execute it. An implementer running the literal command would get a fatal error on the second use of this plan (any retry after a prior partial attempt).

- **Impact:** A second-attempt implementer hits a confusing error mid-Task-0 and has to back out to read the fallback prose. Minor friction; not load-bearing for correctness.

- **Verification:** Plan Task 0 Step 2 — confirmed unconditional `git switch -c`.

- **Resolution:** Replace with a check-then-act bash:

  ```bash
  branch="fix/f4-audit-retention"
  if git show-ref --verify --quiet "refs/heads/$branch"; then
      n=2
      while git show-ref --verify --quiet "refs/heads/$branch-$n"; do
          n=$((n+1))
      done
      branch="$branch-$n"
  fi
  git switch -c "$branch"
  ```

  Or simply: "If `git switch -c fix/f4-audit-retention` fails because the branch exists, run `git switch -c fix/f4-audit-retention-2` instead, and continue."

## 5. Severity Summary and Resolution Table

| ID | Class | Finding | Resolution | Sections Touched |
| --- | --- | --- | --- | --- |
| F1 | blocking-completeness | Plan implements 60% of design §8 tests; key invariants unpinned (boundary, mutable-clock eviction, per-file restoration, partial-failure isolation, basic dedup-skip, non-dict/malformed-JSON retention, UTC normalization) | Add ~17 tests across Tasks 2-4; introduce mutable-clock fixture helper | Tasks 2, 3, 4 |
| F2 | blocking-correctness | Analytics `_timestamp_range` includes malformed string timestamps in range output | Filter via `_parse_aware_iso8601`; report missing/malformed count; add fixture and test pinning parseable-only behavior | Task 7 Step 3, Task 7 test step |
| F3 | moderate-visibility | Single-writer envelope (carry-forward (d)) only in Completion Report | Add Hard Assumptions block + Stop Condition near top of plan | Top-of-plan, Stop Conditions |
| F4 | moderate-mechanical | Task 4 Step 5 lacks the updated `return PruneSummary(...)` block | Inline the 8-kwarg return statement | Task 4 Step 5 |
| F5 | low-flow | Task 0 Step 2 `git switch -c` is unconditional | Replace with check-then-act bash or "if X fails, run Y" pattern | Task 0 Step 2 |

**Amendment scope:** F1 + F2 + F3 + F4 + F5 = all 5. Skip nothing — F5 is one-line and F4 is a single insert.

## 6. Convergence Note (cross-artifact)

The F4 design chain produced 10 review rounds with the convergence trajectory:

| Round | Target | Findings | Algorithm-level |
| --- | --- | --- | --- |
| 4-7 | design | 5 / 3 / 3 / 5 | 1 / 0 / 1 / 0 |
| 8-10 | design | 5 / 5 / 5 | 0 / 0 / 0 |
| **plan-r1** | **plan** | **5** | **0 design-level** |

Plan round 1 produces 5 findings, of which 0 require design-level changes. The plan-vs-design conformance lens caught two carry-forwards that should have been addressed during `writing-plans` invocation but weren't: (a) mutable-clock fixture → F1 sub-issue, (f) parseable timestamp range → F2.

**Pattern observation:** carry-forward items survive across reviewer hand-offs unless the receiving step explicitly checks them. Round-7 → round-8 carry-forward survived. Rounds 8-10 → plan carry-forward survived two items. A simple plan-Section-0 "Carry-Forward Checklist" with one line per handoff item, checkbox per item, would have caught both F1 and F2 before this review.

## 7. Confidence

**Going in:** 4 (10-round-reviewed design; plan is detailed at 2053 lines; user verification reports clean placeholder/ASCII/git state).

**Going out:** 3.

The drop from 4 → 3 is driven by F1 and F2. Both are unambiguously plan-level gaps (not design-level), both have concrete one-amendment fixes, but both block invoking `superpowers:subagent-driven-development` against the plan as-written: an executor following the plan literally would produce code that (a) lacks regression coverage for the boundary, mutable-clock eviction, and dedup-skip invariants, AND (b) ships an analytics range function that produces visibly wrong output for malformed records.

Recommend the standard audit-precursor + amendment-commit pattern (which the F4 chain has used across 10 rounds, 19 commits). Estimated amendment diff: +~80/-~10 across the plan; mostly new test stubs in Tasks 2-4 and one new helper in Task 7.

## 8. Stopping Rule (proposed for plan reviews)

The design's stopping rule was: "*No further design-review cycles unless (a) writing-plans surfaces algorithm-level changes OR (b) an extended-lens pass surfaces a structural finding.*" Round 8 invoked clause (b) via the consumer-propagation lens.

For plan reviews, a parallel rule:

> *No further plan-review cycles unless (a) execution surfaces a missing task / commit boundary OR (b) an extended-lens pass surfaces a plan-flow finding.*

If the proposed amendments above are applied, the next gate is `superpowers:subagent-driven-development` execution itself. Execution naturally surfaces a different class of finding (intermediate-state correctness, commit-checkpoint ordering, real test failures) that is appropriate for plan round 2 if needed.

## 9. Deferred Probes

- **Plan round 2 (post-execution):** if execution reveals intermediate-state issues (e.g., Task 2 leaves the journal in a state where a UnicodeDecodeError from `_prune_jsonl_pass` propagates unhandled because Task 4 hasn't landed), capture as plan-flow findings.
- **`_jsonl_contains` removal pre-grep:** plan Task 3 Step 6 removes after tests pass; a pre-grep `rg "_jsonl_contains" server/` confirming 3 call sites + 1 def would be marginally tighter but adds little. Verification at the live repo shows exactly 3 call sites + 1 def: `server/journal.py:297,317,337` + def at `408`. The plan's post-removal grep gate (Task 9 Step 4) is sufficient.
- **F12 sibling-slice questions** stand from prior rounds; out of scope for this plan review.

## 10. Implementation Cost Estimate

| Finding | Plan changes | Est. lines |
| --- | --- | --- |
| F1 | ~17 new test stubs across Tasks 2-4; one new mutable-clock helper | +~60 |
| F2 | `_timestamp_range` filter + one test stub + one fixture extension | +~25 / -8 |
| F3 | Hard Assumptions block + Stop Condition | +~10 |
| F4 | Inlined `return PruneSummary(...)` | +~12 |
| F5 | Replace one bash line | +~6 / -2 |
| **Total** | | **+~113 / -~10** |

Smaller-than-round-1 amendment surface on the design chain. Mechanical and well-bounded.

## 11. What This Review Did Not Cover

- **Plan executor behavior under partial completion.** If `subagent-driven-development` stops mid-task, what does recovery look like? Outside this pass's scope; would belong to a plan round 2.
- **Cross-file test-import correctness.** Plan adds `from typing import Any, Callable` to `test_journal.py` (Task 1 Step 1) without verifying current imports. If `typing.Any` is already imported, this is a duplicate; ruff catches it; not material.
- **Existing test breakage on `_jsonl_contains` removal.** Plan Task 8 Step 1 inventories but doesn't proactively migrate. If existing tests directly call `_jsonl_contains` (unlikely — it's `_`-prefixed private), removal would break them. Discovery happens at Task 8 Step 2. Acceptable but not zero-risk.
- **Live behavior of `caplog.at_level` across pytest versions.** Plan tests use `with caplog.at_level("INFO"):`. Standard pytest, should work; not verified against the local pytest version.
- **`importlib`-based bootstrap loader.** Plan defers to "that module's established importlib-based loader pattern" without re-deriving it; assumes `_import_bootstrap()` exists in `tests/test_bootstrap.py`. Verifiable by reading the test file; not done in this pass.
