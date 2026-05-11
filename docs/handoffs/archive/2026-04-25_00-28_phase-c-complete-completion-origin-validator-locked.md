---
date: 2026-04-25
time: "00:28"
created_at: "2026-04-25T04:28:42Z"
session_id: a3c9effe-44a0-4fcb-bd34-ca19465e2ac1
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-24_23-24_phase-b-complete-replay-preservation-locked.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: ee143b25
title: Phase C complete (T-20260423-02) — completion_origin validator locked across operation/phase/completion_origin Literal triad; Task 10 + F1 closeout + docs landed
type: handoff
files:
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/journal.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_journal_completion_origin.py
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md
---

# Handoff: Phase C complete (T-20260423-02) — completion_origin validator locked

## Goal

**Immediate objective:** Land Phase C of Packet 1 (T-20260423-02 deferred-approval response design) in this session. Phase C contains a single task (Task 10) that relaxes the `OperationJournal` validator to admit `decision=None` on `approval_resolution.intent/dispatched` records and adds an `OperationJournalEntry.completion_origin` provenance annotation field. Phase C closes when Task 10 lands cleanly, with any review-discovered fixes applied per the disposition heuristic.

**Trigger:** This session resumed from `2026-04-24_23-24_phase-b-complete-replay-preservation-locked.md`. The prior handoff explicitly directed: "Phase C entry — read Phase C plan + Task 10 dispatch." User opened the session with: "Continue with **reading `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-c-journal.md` and locating the Task 10 section**".

**Stakes:** Phase C is the journal-layer counterpart to Phase B's store-layer durability work. Without Phase C closure, Phase D (`ResolutionRegistry` cross-thread coordination primitive) cannot dispatch — the consumer-wiring tasks in Phases D-H all depend on the journal correctly admitting `decision=None` records (the timeout-wake / internal-abort-wake origin case) and on a stable `completion_origin` provenance signal. This session also tested whether the principle-coherence axis of the Phase B 3-axis severity heuristic generalizes from "fix latent bug breaking the durability theme" (Phase B's tuple-loss) to "complete new field's validator coverage matching the existing pattern" (Phase C's `completion_origin` Literal validation gap).

**Bigger picture:** Packet 1 converts `_finalize_turn`'s captured-request branch from synchronous-decide kind-based escalation to async-decide worker-owned resolution. Phase A (foundation) ✅. Phase B (PendingRequestStore + DelegationJobStore mutators + replay-preservation principle) ✅. Phase C (journal validator relaxation + provenance annotation) ✅ this session. Phases D-H remain (ResolutionRegistry, journal projection, consumer wiring, escalation rewiring, worker terminal-branch signal, restart sequence).

**Why now:** Plan-execute discipline + the 1M context window calibration from prior session. User explicitly indicated "we have plenty of room to proceed" at Phase B end; Phase C entry was the natural next step in a fresh session.

**Success criteria (all achieved):**
- Task 10 committed with spec ✅ + quality ✅ reviewer approval (achieved at `e8786626`; +8 tests = 942)
- F1 (`completion_origin` Literal lacked validator coverage) escalated via 3-axis principle-coherence reasoning to **Path A1** (closeout fix this session) — achieved at `9061d268`; +2 tests = 944
- Phase C closeout docs commit landed updating `carry-forward.md` (achieved at `ee143b25`)
- Full-package regression clean (944 tests pass, up 10 from 934 at session start)
- Branch state ready for Phase D dispatch in a fresh session (achieved)

**Connection to project arc:** Phase C closes here. Tasks 6, 7, 8, 9, 10 ✅ landed across three sessions (Tasks 6/7 prior session; Tasks 8/9 + Phase B closeout last session; Task 10 + Phase C closeout this session). Phases D-H remain. The `_VALID_*` frozenset pattern for membership-validating Literal-typed journal fields is now locked as a third validation primitive (alongside `_JOURNAL_REQUIRED_STR` and `_JOURNAL_OPTIONAL_STR` type checks). Phase D will likely extend this pattern as it introduces new typed fields.

## Session Narrative

**Starting state (session open):** Loaded the Phase B closeout handoff. Branch was `feature/delegate-deferred-approval-response` at `23e427c6` (Phase B closeout docs). Working tree clean. 934 tests passing. Phase C ready for dispatch. Patterns locked from Phase B: (1) `dataclasses.replace(existing, **changes)` for replay branches; (2) `record.get(key) or default` for null-safe coercion of tuple/list-typed fields; (3) `assert type(field) is expected_type` regression tests; (4) 3-axis severity heuristic (precondition × symptom × principle-coherence-at-phase-boundary); (5) pre-authorize plan deviations in implementer briefings when ≥2 deviations exist; (6) 3-commit closeout shape (feat + fix + docs).

**Read-first discipline (per user's opening directive):** Read in parallel:
- `phase-c-journal.md` (424 lines, single Task 10 section)
- `journal.py` (full, 407 lines) — locate `_journal_callback`, the `approval_resolution` schema blocks at `:124-157`, and `_terminal_phases`/`replay_jsonl` interaction
- `models.py:330-399` — `OperationJournalEntry` 14-field dataclass
- `delegation_controller.py:1850-2000` — to verify the plan's `:1856-1884` recovery reference (the plan's reference was stale — see Pivot 1)
- `tests/test_delegation_controller.py:2115-2255` — the sibling test `test_recover_startup_marks_intent_only_approval_resolution_unknown` at `:2129` which Step 10.7a's new test must mirror
- `tests/test_journal.py` — for any existing "decision required" assertions

**Pre-dispatch analysis (more involved than Phase B Tasks 7/8/9 due to Phase C plan staleness):** Six categories of findings crystallized:

1. **Plan-text staleness in line numbers and "common fix shape" guidance.** Phase C plan's Step 10.7a refers to `delegation_controller.py:1856-1884` for the recovery audit target. That range is currently inside `_decide_approve_path`'s post-execution journaling, NOT recovery. The actual `approval_resolution` recovery loop is at `:1965-1994` (located by the structural landmark `# --- approval_resolution reconciliation ---` at line 1966). Plan's "Common fix shape" — `assert isinstance(decision, str)` followed by removal — is also stale: no such assertion exists in the current recovery code. The current code already does `decision=entry.decision` without checks, so `decision=None` would pass through cleanly without modification.

2. **Plan tests test the wrong code paths.** The plan's `Step 10.1` test stubs at `phase-c-journal.md:23-167` had three structural problems:
   - Tests `test_completion_origin_worker_completed_round_trip` and `test_completion_origin_recovered_unresolved_round_trip` call `journal.replay_jsonl(session_id="s1")`. **`OperationJournal` does NOT expose `replay_jsonl` as a method** — it's a module-level helper from `replay.py` invoked via `_terminal_phases`. The class exposes `check_idempotency`, `list_unresolved`, `check_health`, `compact`, and `_terminal_phases` (private). Calls would `AttributeError`.
   - Test `test_decision_non_string_non_none_still_rejected` does `with pytest.raises(SchemaViolation): journal.write_phase(bad, session_id="s1")`. **`write_phase` does not validate** — `journal.py:300-307` is a pure append (`json.dumps(asdict(entry))`). Validator runs only on replay via `_terminal_phases` → `replay_jsonl(path, _journal_callback)`. Test would silently pass.
   - Legacy-record test path uses `tmp_path / "journal" / "s1" / "journal.jsonl"`. Actual `_operations_path()` (line 357-358) is `plugin_data_path / "journal" / "operations" / "{session_id}.jsonl"`.

3. **Step 10.7a is missing a code-modification instruction.** The new test `test_recover_startup_closes_orphaned_none_decision_intent` asserts `completion_origin == "recovered_unresolved"` on the recovered record. But the current recovery loop at `:1980-1994` does NOT set this field. **The implementer must modify the recovery loop to add `completion_origin="recovered_unresolved"` to the `OperationJournalEntry(...)` call.** Step 10.7a's plan-text only says "audit for any `assert decision is not None`" — incomplete instruction.

4. **Phase B patterns: which apply, which don't.** `dataclasses.replace()` lock is structurally inapplicable — journal has no per-op replay branches; `_journal_callback` is single linear `OperationJournalEntry(...)` construction. `or ()` defensive coercion inapplicable — no tuple/list-typed fields touched. Type-identity assertions only marginally apply (`Literal` strings; equality suffices). Pre-authorize-deviations pattern fully applies given 6 deviations.

5. **Existing "decision required" test surface clean.** `grep "decision\|approval_resolution" tests/test_journal.py` returned only two tests touching `decision`, both using `decision="approve"`. No "decision is required" assertions to update per Step 10.7's permission grant.

6. **Open question for user (G):** Should recovery loop ALWAYS set `completion_origin="recovered_unresolved"` (regardless of decision) or only for `decision=None` records? My recommendation: always (cleaner; the field describes WHO wrote the marker, not the original record's decision value).

**Pivot 1 (user dispatch-watch-outs message):** While I was assembling the consolidated pre-dispatch findings, user sent their own "Important Dispatch Watch-Outs" message that **independently surfaced 4 of the same findings** (with refinements). Critical refinements vs my analysis:

- User correction on B2: my proposed fix `pytest.raises(SchemaViolation): journal.list_unresolved(...)` ALSO doesn't work. **`replay_jsonl()` catches `SchemaViolation` at lines 109-117 and converts it to a `ReplayDiagnostic(label="schema_violation")` — it does NOT propagate.** Correct test pattern: `journal.write_phase(bad, session_id="s1")` then `journal.check_health(session_id="s1")` and assert `len(diagnostics.schema_violations) == 1`.
- User correction on B4: Don't ask for a "`decision=None` on non-approval op is rejected" test. The narrowness proof should be: `approval_resolution.intent/dispatched` accept None; `decision=42` still rejected (via global `_JOURNAL_OPTIONAL_STR` type check); required fields (`job_id`, `request_id`, `runtime_id`, `codex_thread_id`) remain enforced.
- User confirmed Path A on G: "always set `completion_origin='recovered_unresolved'` in the recovery loop. Rationale: the field describes WHO wrote the terminal `completed` journal marker, not whether the original unresolved record had an operator decision."

**Pivot 2 (verifying user's correction):** Read `replay.py` (full, 154 lines) directly to verify the SchemaViolation-catching behavior. Confirmed at `replay.py:109-117`: the `SchemaViolation` exception is caught and converted to a `ReplayDiagnostic(label="schema_violation", line_number=..., detail=...)` accumulated in `immediate_diagnostics`. `ReplayDiagnostics.schema_violations` property at `:55-58` filters to schema-violation labels. The test pattern is now lockable: `write_phase(bad)` → `check_health()` → `diagnostics.schema_violations` → assert.

**Task 10 implementer dispatch (haiku, background):** Briefing included full plan text + 6 pre-authorized deviations (DEV-1 through DEV-6) + 10 hard rules (locked from Phase B) + verification gate (pytest + ruff + pyright). Background dispatch.

**Task 10 implementer report (DONE at `e8786626`):** 942 tests pass (was 934, +8: 7 in `test_journal_completion_origin.py` + 1 in `test_delegation_controller.py`). All 6 pre-authorized deviations applied correctly. Implementer-side pyright reported `server/models.py` and `server/journal.py` as "0 errors, 0 warnings, 0 informations." Pre-existing pyright errors in unrelated test files acknowledged as outside scope.

**Self-verification (controller, not subagent):** Per Phase B precedent for tightly-scoped work:
- `git show e8786626 --stat` — confirmed 5 files (3 src + 2 tests, +230/-4 lines)
- `git diff` of `journal.py`, `models.py`, `delegation_controller.py` — verified surgical edits match spec verbatim
- `uv run --package codex-collaboration pytest packages/plugins/codex-collaboration/ -q` → **942 passed in 20.26s** ✓
- Cross-referenced new harness pyright diagnostics against prior commit (`23e427c6`): `delegation_controller.py:965` (`PendingRequestKind` vs `EscalatableRequestKind` mismatch), `:116` (`_sanitize_error_string` unused), `:197` (`_WorkerTerminalBranchSignal` unused), and 9 test-file errors — **all confirmed pre-existing at `23e427c6` via `git show 23e427c6:...`**. Pyright cache staleness pattern from Phase B applies.

**Reviewers dispatched (parallel, both sonnet, background):** Spec-compliance reviewer + code-quality reviewer. Each given the 6 pre-authorized deviations as locked context (NOT to classify as defects).

**Spec reviewer report:** ✅ SPEC-COMPLIANT. All 6 deviations confirmed. Step-by-step PASS for 10.1, 10.3, 10.4, 10.5, 10.7a, 10.8. 4 out-of-scope observations (none defects):
1. `SchemaViolation` import omitted from new test file (clean DEV-2 consequence)
2. `write_phase` doesn't validate at write time (interface documentation gap)
3. New recovery test omits `list_unresolved == []` assertion (sibling-parity gap)
4. Plan's Step 10.8 `git add` line omits `delegation_controller.py` (editorial plan-doc gap)

**Quality reviewer report:** ✅ Ship-ready, **zero Critical, zero Important**. 4 Minor findings, all carry-forward candidates:
- **F1:** `completion_origin` absent from `_JOURNAL_OPTIONAL_STR` validation loop — a hand-crafted JSONL record with `completion_origin=42` or `completion_origin=[]` would silently pass. Pattern asymmetry vs other optional string fields. **Severity: Minor (low precondition × moderate-if-triggered symptom × pattern-asymmetry not Phase-C-defining).**
- **F2:** New recovery test omits `list_unresolved == []` post-recovery assertion (same as spec Obs #3 partial)
- **F3:** Same test omits `job.status == "unknown"` and `handle.status == "unknown"` assertions
- **F4:** `worker_completed` Literal value not wired to any production writer (intentional, future-task scope)

Plus a tautological-but-safe analysis: per-op `decision` check redundancy with global `_JOURNAL_OPTIONAL_STR` loop. NOT classified as defect.

**Disposition decision moment (Phase B parallel):** Surfaced F1 to user with 3-axis severity classification + Phase B parallel framing. My recommendation was **Path B (carry-forward)** with reasoning:
1. Phase C is "narrow relaxation," not "preservation theme" (lower principle-coherence weight)
2. Adding to `_JOURNAL_OPTIONAL_STR` is partial — wouldn't catch invalid Literal values like `"garbage"` (still a string)
3. Phase D's `ResolutionRegistry` introduction is natural venue for Literal-membership validation patterns

**User chose Path A1 with structured 9-section disposition analysis.** Quote: "I recommend **Path A1: separate closeout fix for F1 only**, and make it a complete validation fix, not just adding `completion_origin` to `_JOURNAL_OPTIONAL_STR`. Concretely: add `completion_origin` validation in `_journal_callback` so `None`, `'worker_completed'`, and `'recovered_unresolved'` are accepted, while non-string values and unknown strings are reported as schema violations through `check_health()`."

User's reasoning (load-bearing for the decision): "F1 is not just test polish. It is a new schema field on a validator-owned object, and the implementation apparently accepts arbitrary typed garbage at replay. Carrying it forward means Phase C closes while knowingly leaving the new journal provenance field less validated than the operation and phase Literals around it." User's readiness condition: `verifiably best` after confirming no existing `_VALID_COMPLETION_ORIGINS`-style check (verified by grep on `journal.py`).

**Closeout fix dispatch (haiku, background):** User-spec'd 4 explicit edits: (EDIT-1) add `"completion_origin"` to `_JOURNAL_OPTIONAL_STR`; (EDIT-2) add `_VALID_COMPLETION_ORIGINS = frozenset(("worker_completed", "recovered_unresolved"))` constant; (EDIT-3) membership-check block in `_journal_callback` after optional-int loop; (EDIT-4) two new tests `test_completion_origin_unknown_string_value_rejected` + `test_completion_origin_non_string_rejected`. Verification gate + exact commit message pre-spec'd.

**Closeout fix implementer report (DONE at `9061d268`):** 944 tests pass, ruff clean, pyright on `journal.py` 0/0/0. All 4 edits applied. No deviations encountered.

**Self-verification of closeout fix:** Per Phase B precedent for tightly-scoped user-directed fixes:
- `git show 9061d268 --stat` — 2 files, +53 lines
- `git show 9061d268 -- journal.py` — surgical changes match spec verbatim, `_VALID_COMPLETION_ORIGINS` IS referenced at line 86 inside the membership-check block
- `uv run pytest` → **944 passed in 19.50s** ✓
- `uv run pyright packages/plugins/codex-collaboration/server/journal.py` → **0 errors, 0 warnings, 0 informations** ✓
- Harness reported `★ "_VALID_COMPLETION_ORIGINS" is not accessed` hint — investigated and confirmed cache staleness; direct pyright on the file is clean.

**Closeout docs commit:** Edited `carry-forward.md` to add 3 new C10.2/C10.3/C10.4 open items + 1 closed C10.1 entry under appropriate Phase C subsections. Committed at `ee143b25` with message `docs(delegate): record Phase C closeout (T-20260423-02)`.

**Final state verification:** `git rev-list --count b6dbaa3c..HEAD` = **14 commits** (Phase B = 11, Phase C = 3). Branch tip `ee143b25`. 944 tests pass. Working tree clean. Phase C closes in canonical 3-commit shape (feat `e8786626` + closeout fix `9061d268` + closeout docs `ee143b25`) mirroring Phase B exactly (`16aca095` + `c6bf834c` + `23e427c6`).

## Decisions

### Pre-dispatch deep code audit before Task 10 implementer dispatch

**Decision:** Read all touched code in parallel before dispatching the haiku implementer — `phase-c-journal.md`, `journal.py`, `models.py`, `delegation_controller.py:1850-2000`, `test_delegation_controller.py:2115-2255`, `test_journal.py` for stale assertions.

**Driver:** Phase B Task 9 pattern caught the `asdict_for_replay` phantom helper escalation BEFORE dispatch and saved the cost of a wrong-implementation review cycle. Per prior handoff: "Pre-Task-9 analysis (more involved): Three CRITICAL pre-dispatch findings... Plan tells the implementer to DEFINE `asdict_for_replay` as a new helper... Plan-text fiction we already knew about; Task 9 escalates because the plan is asking the implementer to *create* it." Phase C plan was suspected to have similar staleness given its age.

**Rejected:** Dispatch immediately with plan text only. Rejected because plan text was authored against an older codebase shape and would have produced a haiku implementation with at least 4 broken tests (per the dispatch-watch-outs that user independently surfaced).

**Implication:** The pre-dispatch audit is now established as a phase-entry pattern, not a Task-9-specific pattern. Future phase entries (Phase D, E, F, G, H) should default to coordinator pre-reads before haiku dispatch.

**Trade-offs:** Higher coordinator context cost (~30k tokens for Phase C pre-audit) but bypassed the "wrong implementation → review cycle → fix dispatch" loop that would have cost ~80k+ tokens. Net positive at the 1M context window the user emphasized.

**Confidence:** High (E3) — three data points (Phase B Task 9 audit + Phase C Task 10 audit + user's independent dispatch-watch-outs converging on same findings).

**Reversibility:** High — could skip pre-audit on a future task if plan staleness is verified absent.

**Change trigger:** First case where pre-audit produces zero findings. Would suggest the plan is current and audit is unnecessary overhead.

### Pre-authorize 6 deviations in Task 10 implementer briefing (vs surface-as-decision-point)

**Decision:** Use the "PRE-AUTHORIZED DEVIATIONS" briefing structure (Phase B Task 9 pattern, scaled up). Six pre-authorized deviations explicitly named (DEV-1 through DEV-6), each with rationale, replacement code, and disclosure-protocol obligation.

**Driver:** Phase B Task 9 used 3 pre-authorized deviations and shipped clean. The cognitive load on a haiku implementer scales with deviation count — surface-as-decision-point (Task 7's 1 deviation pattern) doesn't transfer to 6 deviations. Each DEV-N item names: (a) what the plan says, (b) why it's wrong, (c) the correct replacement, (d) a code template if non-obvious.

**Rejected:** Surface-as-decision-point (one or two deviations as "you may need to adapt..."). Rejected because the implementer must navigate 6 stale references in 1 dispatch — the cognitive load ceiling for haiku tier is exceeded.

**Implication:** Establishes the deviation-count threshold heuristic: **≤1 deviation → surface-as-decision; ≥2 → pre-authorize**. The deviation-disclosure protocol (implementer must explicitly name each DEV-N applied) functions as the verification handshake — spec reviewer cross-checks the disclosed list against the diff.

**Trade-offs:** Briefing is longer (~3,500 tokens vs Task 7's ~1,800). Implementer can't surface novel deviations easily — they must hit a "DEVIATION-DISCOVERED" stop. But this is exactly the right behavior: novel deviations need coordinator triage, not implementer judgment.

**Confidence:** High (E2) — pattern locked across Tasks 9 and 10 (4 out of 4 implementations clean ship at this scale).

**Reversibility:** High — switch back to surface-as-decision for tasks with 1 or fewer deviations.

**Change trigger:** First case where a pre-authorized implementer mis-applies a DEV-N (would invalidate the pattern). Track via spec reviewer cross-reference.

### Always set `completion_origin="recovered_unresolved"` in recovery loop (regardless of `entry.decision`)

**Decision:** Modify `delegation_controller.py:1992` to add `completion_origin="recovered_unresolved",` unconditionally inside the `approval_resolution` recovery reconciliation loop. No branching on `entry.decision`.

**Driver:** User-confirmed coordinator decision via Pivot 1 message. Quote: "Proceed with **(a): always set `completion_origin='recovered_unresolved'` in the recovery loop**. Rationale: the field describes **who wrote the terminal `completed` journal marker**, not whether the original unresolved record had an operator decision. A recovered `decision='approve'` orphan and a recovered `decision=None` orphan are both cold-start recovery completions."

**Rejected:** Conditional set (only for `decision=None` records). Rejected because: (a) semantic mismatch — `recovered_unresolved` means "recovery wrote it" not "decision was none"; (b) two-class behavior would be harder to reason about for downstream consumers; (c) the existing sibling test at `:2129` doesn't assert against `completion_origin`, so unconditional set doesn't break sibling.

**Implication:** Establishes the coordinator pattern: when a new field has provenance semantics (who wrote it), the corresponding writer site sets it unconditionally. Phase E worker-side wiring will mirror — `decide()` callsites set `completion_origin="worker_completed"` regardless of decision.

**Trade-offs:** Existing recovered-completed records (decision="approve" path) now also carry `completion_origin="recovered_unresolved"`. No backward-compat issue (the field defaults to `None` for legacy records).

**Confidence:** High (E2) — user-provided rationale aligns with field semantics; sibling test confirms no breakage.

**Reversibility:** Trivial — could change to conditional set in a future task if a downstream consumer requires it.

**Change trigger:** A future consumer that needs to distinguish "recovered with decision" vs "recovered without decision." Currently no such consumer exists.

### F1 disposition: Path A1 — closeout fix this session with COMPLETE validation (type + membership)

**Decision:** Accept user's Path A1 over my recommended Path B. Apply COMPLETE validation: add `"completion_origin"` to `_JOURNAL_OPTIONAL_STR` (type half) AND add `_VALID_COMPLETION_ORIGINS = frozenset(("worker_completed", "recovered_unresolved"))` + dedicated membership-check block (membership half).

**Driver:** User stated: "F1 is not just test polish. It is a new schema field on a validator-owned object, and the implementation apparently accepts arbitrary typed garbage at replay. Carrying it forward means Phase C closes while knowingly leaving the new journal provenance field less validated than the operation and phase Literals around it." Path A1 specifically calls out that the partial fix (just `_JOURNAL_OPTIONAL_STR`) is insufficient — the Literal type implies membership, and only complete validation matches the type signature.

**Rejected — Path A2 (fix F1 + F2/F3):** User reasoning: "F2/F3 are not Phase C acceptance-critical. They assert existing behavior already covered by sibling tests and can dilute the closeout fix commit with lower-value parity work."

**Rejected — Path B (carry-forward all):** User reasoning: leaves Phase C's new field under-validated; convention check fails (operation/phase have membership validation, so "Literal annotations are documentation-only" doesn't hold for journal schema).

**Rejected — Null (close with no action):** User reasoning: "Even if you choose not to fix, F1 should at least be tracked."

**Rejected — Coordinator's Path B recommendation:** Overruled by user's principle-coherence framing. Coordinator's reasoning had two flaws: (1) treated principle-coherence as "Phase C is narrow relaxation theme" — but user's framing was "the new field's validator coverage breaks pattern symmetry"; (2) treated partial fix (`_JOURNAL_OPTIONAL_STR` only) as the comparison set — but user demanded complete fix.

**Implication:** Establishes the "complete validation" disposition shape for new Literal-typed fields. The pattern is: every new optional Literal-typed journal field MUST have both type-check (via `_JOURNAL_OPTIONAL_STR` or equivalent) AND membership-check (via `_VALID_*` frozenset). Phase D fields will be evaluated against this lock.

**Trade-offs:** Adds a closeout fix commit (3-commit phase shape vs 2-commit clean ship). +2 tests, +7 source lines. Net cost ~30k coordinator tokens for dispatch + verify; well within 1M context budget.

**Confidence:** High (E3) — user's structured 9-section analysis (multi-axis evaluation, sensitivity check, ranking) + my own 3-axis classification + spec/quality reviewer agreement on F1 as a real finding.

**Reversibility:** Trivial — fix already landed; reverting would be a separate decision with its own justification.

**Change trigger:** A future Literal-typed field that's intentionally NOT validated (e.g., for performance reasons on a high-throughput path). Currently no such case exists in the journal layer.

### Self-verify closeout fix instead of re-dispatching reviewers

**Decision:** Controller (this seat) verified the closeout fix via direct `git show` + `git diff` + independent `pytest` + direct `pyright`, rather than dispatching another spec/quality reviewer subagent.

**Driver:** Same precedent as Phase B closeout fix at `c6bf834c`. User's spec was extremely explicit (4 named edits, exact code templates, exact verification gate, exact commit message). Implementer reported "no deviations encountered." Re-dispatching would cost ~30-50k tokens for a fix scope where the spec was user-provided rather than reviewer-directed.

**Rejected:** Re-dispatch a spec-compliance reviewer for the closeout fix. Would provide stronger rigor but at meaningful context cost for a fix where the spec was user-authored and tightly scoped (3 source edits + 2 tests, single source file + single test file).

**Implication:** Self-verification pattern is now used **5 times** (Tasks 6/7/8 in-scope fixes + Phase B closeout fix + this Phase C closeout fix). Pattern is durable. For tightly-scoped user-directed or reviewer-directed fixes (≤ ~100 lines, single-file or 2-file scope, no ambiguity), self-verify via diff inspection + verification gate. For ambiguous fix scope, always re-dispatch.

**Trade-offs:** Less rigor than strict subagent-driven-development. Risk: implementer silently deviated. Mitigated by: (a) user's spec explicit (every edit named), (b) implementer's deviation-disclosure protocol reporting "None" on EDITs and "no unanticipated deviations", (c) my direct diff inspection, (d) verification gate (pytest + ruff + pyright) that the implementer ran.

**Confidence:** High (E3) — pattern works, 5 data points across two phases now.

**Reversibility:** Trivial — could dispatch a re-review now if any future regression surfaces.

**Change trigger:** First failed self-verification (would invalidate the pattern). Track via post-merge findings.

### 3-commit Phase C closeout shape (feat + fix + docs)

**Decision:** Phase C closes as 3 commits: Task 10 feat (`e8786626`) + closeout fix (`9061d268`) + closeout docs (`ee143b25`). Mirrors Phase B's 3-commit closeout shape exactly.

**Driver:** User's preference established at Phase B end: "**Three-commit closeout shape preferred:** 'Task 9 stayed as its own feature commit, the tuple-loss replay defect landed as a separate visible fix commit, and the docs commit records the review-discovered closeout rather than hiding it in an amend.' Audit-trail clarity > commit-count minimization."

**Rejected:** 2-commit shape (feat + docs, no closeout fix). Rejected per the F1 disposition decision.

**Rejected:** Squashed-into-amend shape (single commit with all changes). Rejected because amending would hide the review-loop's discovery work and the principle-coherence escalation.

**Implication:** The 3-commit shape is now the canonical phase-closeout pattern. Phases D-H will follow the same shape unless a phase ships completely clean (no in-scope or closeout fix), in which case 2 commits suffice.

**Trade-offs:** More commits in branch history. But each commit is independently meaningful: feat = "what landed," fix = "what was discovered + escalated," docs = "what was decided." Audit trail is clearer than a squashed commit.

**Confidence:** High (E3) — pattern locked across Phase B + Phase C now.

**Reversibility:** N/A — commits already landed.

**Change trigger:** N/A.

## Changes

### `packages/plugins/codex-collaboration/server/models.py` (MODIFIED — Task 10 commit `e8786626`, +6 lines)

**Purpose:** Add `completion_origin` field to `OperationJournalEntry` dataclass.

**Approach:**
- Added at END of field list (line 396-401), after `decision: str | None = None`. Position-of-default rule: all new optional fields go at the end.
- Type signature: `Literal["worker_completed", "recovered_unresolved"] | None = None`. The `None` default preserves back-compat — legacy records replay with `None` via dataclass default.
- 4-line docstring comment block matches plan's `:204-209` verbatim: explains `worker_completed`, `recovered_unresolved`, and `None` (legacy) semantics.

**Future-Claude note:** `Literal["worker_completed", "recovered_unresolved"] | None` is a type-system hint, not a runtime guard. Python's `@dataclass(frozen=True)` does NOT enforce field types at construction. `OperationJournalEntry(... completion_origin=42 ...)` constructs cleanly. The runtime guard is the journal validator (closeout fix at `9061d268`).

### `packages/plugins/codex-collaboration/server/journal.py` (MODIFIED — TWO commits)

**Commit 1, `e8786626` (Task 10):** Three changes:
- Lines 130-136 (intent block): relax `decision` schema check from `if not isinstance(record.get("decision"), str): raise` to `decision = record.get("decision"); if decision is not None and not isinstance(decision, str): raise`. Error message updated to "string or None".
- Lines 144-150 (dispatched block): identical relaxation pattern.
- Line 182: add `completion_origin=record.get("completion_origin"),` as the last kwarg in the `entry = OperationJournalEntry(...)` construction inside `_journal_callback`.

**Commit 2, `9061d268` (Phase C closeout fix):** Four changes:
- Line 60: add `"completion_origin",` to `_JOURNAL_OPTIONAL_STR` tuple (type half — triggers the existing optional-string-type-check loop at `:80-83` to validate `completion_origin` is `str | None`).
- Line 62: add `_VALID_COMPLETION_ORIGINS = frozenset(("worker_completed", "recovered_unresolved"))` constant after `_JOURNAL_OPTIONAL_INT`.
- Lines 84-88: add membership-check block inside `_journal_callback` after the optional-int loop and before the per-operation+phase comment. Reads: `completion_origin = record.get("completion_origin"); if completion_origin is not None and completion_origin not in _VALID_COMPLETION_ORIGINS: raise SchemaViolation(f"unknown completion_origin value: {completion_origin!r}")`.

**Combined post-commit state:**
- `_journal_callback` now validates `completion_origin` symmetrically with `operation` and `phase`: type-checked via `_JOURNAL_OPTIONAL_STR` loop, membership-checked via `_VALID_COMPLETION_ORIGINS` frozenset.
- Validator pattern matrix:

| Field | Required? | Type check | Membership check |
|---|---|---|---|
| `operation` | Yes | `_JOURNAL_REQUIRED_STR` | `_VALID_OPERATIONS` |
| `phase` | Yes | `_JOURNAL_REQUIRED_STR` | `_VALID_PHASES` |
| `decision` (now post-Phase-C) | Optional | `_JOURNAL_OPTIONAL_STR` | (per-op-phase narrow check) |
| `completion_origin` | Optional | `_JOURNAL_OPTIONAL_STR` | `_VALID_COMPLETION_ORIGINS` |

### `packages/plugins/codex-collaboration/server/delegation_controller.py` (MODIFIED — Task 10 commit `e8786626`, +1 line)

**Purpose:** Tag every recovered-completed `approval_resolution` record with provenance annotation.

**Approach:** Single line addition at `:1992`: `completion_origin="recovered_unresolved",` inside the `OperationJournalEntry(...)` call within the `approval_resolution` recovery reconciliation loop (lines 1980-1994 in pre-edit state, located by structural landmark `# --- approval_resolution reconciliation ---` at `:1966`).

**Why unconditional:** Per "Always set" decision above. The field describes who wrote the marker, not the original record's decision value.

**Plan-text staleness note:** Phase C plan referenced `:1856-1884` for this audit target. Stale — that range is `_decide_approve_path`'s post-execution journaling. Located by structural landmark instead. Future plan updates should specify the comment landmark, not absolute line numbers.

### `packages/plugins/codex-collaboration/tests/test_delegation_controller.py` (MODIFIED — Task 10 commit `e8786626`, +72 lines, 1 new test)

**Purpose:** Verify recovery handles orphaned `approval_resolution.intent` with `decision=None` (the timeout-wake / internal-abort-wake origin case) and tags the recovered-completed record with `completion_origin="recovered_unresolved"`.

**Approach:**
- Test name: `test_recover_startup_closes_orphaned_none_decision_intent`
- Placement: line 2186 (immediately after the sibling test `test_recover_startup_marks_intent_only_approval_resolution_unknown` at `:2129`)
- Mirrors sibling pattern: uses `_build_controller(tmp_path)` 8-tuple unpack helper; creates `DelegationJob(status="needs_escalation")` + `CollaborationHandle(status="active")` + writes orphaned `approval_resolution.intent` via `journal.write_phase`
- Differs from sibling: uses `decision=None` instead of `decision="approve"` in the intent record; uses `idempotency_key="42:recovered"` instead of `"42:approve"`
- Assertions (3): recovery succeeds without raising; `journal.check_idempotency("42:recovered", session_id="sess-1")` returns a record with `phase == "completed"`; that record has `completion_origin == "recovered_unresolved"`

**Coverage gaps (carry-forward C10.2 + C10.3):** test does NOT assert `journal.list_unresolved == []` or `job.status == "unknown"` / `handle.status == "unknown"` (sibling does both). These are sibling-parity gaps, not Phase C invariant violations.

### `packages/plugins/codex-collaboration/tests/test_journal_completion_origin.py` (NEW — Task 10 commit `e8786626` + closeout fix `9061d268`, 9 tests total)

**Purpose:** Verify Task 10's `completion_origin` field round-trips correctly + Phase C closeout's complete validation coverage.

**Test breakdown (9 tests):**

| Test | Commit | Purpose |
|---|---|---|
| `test_completion_origin_field_exists_with_default_none` | `e8786626` | Construction with no `completion_origin` arg defaults to `None` |
| `test_intent_accepts_decision_none` | `e8786626` | `approval_resolution.intent` validator accepts `decision=None` |
| `test_dispatched_accepts_decision_none` | `e8786626` | `approval_resolution.dispatched` validator accepts `decision=None` |
| `test_decision_non_string_non_none_still_rejected` | `e8786626` | `decision=42` produces `schema_violations` via `check_health` (DEV-2 pattern) |
| `test_completion_origin_worker_completed_round_trip` | `e8786626` | `completion_origin="worker_completed"` round-trips through `check_idempotency` |
| `test_completion_origin_recovered_unresolved_round_trip` | `e8786626` | `completion_origin="recovered_unresolved"` round-trips |
| `test_legacy_records_without_field_replay_as_none` | `e8786626` | Legacy JSONL (no `completion_origin` key) replays with `None` (back-compat) |
| `test_completion_origin_unknown_string_value_rejected` | `9061d268` | `completion_origin="garbage"` produces `schema_violations` via membership check |
| `test_completion_origin_non_string_rejected` | `9061d268` | `completion_origin=42` produces `schema_violations` via type check |

**Pattern note:** All schema-violation tests use the DEV-2 pattern (`write_phase(bad)` then `check_health(session_id="s1")` then assert `len(diagnostics.schema_violations) == 1`). Equality-only assertions on `violations[0].detail` use `"completion_origin" in violations[0].detail` substring check — robust against minor message wording changes.

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (MODIFIED — closeout docs commit `ee143b25`, +12 lines)

**Purpose:** Record Phase C closeout state — 3 new open items + 1 closed item.

**Open items added:**
- C10.2: New recovery test omits `list_unresolved == []` post-recovery assertion (sibling-parity gap)
- C10.3: Same test omits `job.status == "unknown"` and `handle.status == "unknown"` assertions (sibling-parity gap)
- C10.4: `worker_completed` Literal not wired to decide path (intentional, future-task scope)

**Closed items added:**
- F1 / C10.1 closure entry referencing `9061d268`. Records the 3-axis severity reasoning + Path A1 escalation + complete-validation fix shape.

**Tracker state at Phase C end:**
- 12 open items: A1-A5 (5), B6.1-B6.2 (2), B7.1-B7.2 (2), B8.1-B8.2 (2), C10.2-C10.4 (3)
- 4 closed items: Task 6 update_status fix, Task 7 record_protocol_echo null-guard fix, Task 9+closeout tuple-loss fix, Phase C completion_origin Literal validator fix
- Linear projection: ~22-30 items by end of Task 22. Still below the 30-item migration threshold from the original Risk.

## Codebase Knowledge

### Architecture: Phase C end state — journal validator covers all Literal-typed fields symmetrically

| Validator concern | Mechanism | Constants | File:line |
|---|---|---|---|
| Required-string fields | `_JOURNAL_REQUIRED_STR` loop | `_JOURNAL_REQUIRED_STR` (6 fields) | `journal.py:46-53`, check at `:68-70` |
| Optional-string fields | `_JOURNAL_OPTIONAL_STR` loop | `_JOURNAL_OPTIONAL_STR` (6 fields incl. `completion_origin`) | `journal.py:54-61`, check at `:80-83` |
| Optional-int fields | `_JOURNAL_OPTIONAL_INT` loop | `_JOURNAL_OPTIONAL_INT` (2 fields) | `journal.py:62`, check at `:84-87` |
| `operation` membership | `_VALID_OPERATIONS` frozenset | 5 op values | `journal.py:36-44`, check at `:73-74` |
| `phase` membership | `_VALID_PHASES` frozenset | 3 phase values | `journal.py:45`, check at `:75-76` |
| `completion_origin` membership | `_VALID_COMPLETION_ORIGINS` frozenset | 2 values | `journal.py:62`, check at `:88-92` |
| Per-operation+phase narrow checks | inline `elif op == "..."` blocks | (none — bespoke) | `journal.py:96-160` |

**`OperationJournalEntry` 14-field dataclass shape (post-Phase-C):**

```
required:  idempotency_key, operation, phase, collaboration_id, created_at, repo_root
optional:  codex_thread_id, turn_sequence, runtime_id, context_size, job_id, request_id, decision, completion_origin
```

### Pattern: `OperationJournal` validation seam is REPLAY, not WRITE

**Discovered (Pivot 1, user dispatch-watch-outs).** The `_journal_callback` validator runs only via `replay_jsonl(path, _journal_callback)` invoked from `_terminal_phases` (`journal.py:345-349`), NOT from `write_phase` (`:300-307`).

**Implication:** Bad records can be written to disk; they only fail at next replay. This is deliberate — replay must survive partial corruption to produce a usable terminal-state map.

**`replay_jsonl` corruption-tolerance behavior:** Catches `SchemaViolation` (`replay.py:109-117`) and `UnknownOperation` (`:118-126`), converts to `ReplayDiagnostic`, skips the bad record, and continues. Only programmer-bug exceptions propagate.

**Test surface:** Use `journal.check_health(session_id="s1")` to inspect `ReplayDiagnostics.schema_violations`. NOT `pytest.raises(SchemaViolation): journal.list_unresolved(...)` — the SchemaViolation is swallowed.

### Pattern: `_VALID_*` frozenset for Literal-typed journal field membership

**Locked across:** `_VALID_OPERATIONS` (existing), `_VALID_PHASES` (existing), `_VALID_COMPLETION_ORIGINS` (Phase C closeout, `9061d268`).

**Why frozenset over alternatives:**
- `frozenset` is hashable, immutable, O(1) `in` lookup
- Module-level constant — no runtime construction cost per `_journal_callback` invocation
- Matches existing pattern (`_VALID_OPERATIONS`, `_VALID_PHASES`)

**When to add a new `_VALID_*`:** Whenever a new Literal-typed journal field is introduced. Phase D's `ResolutionRegistry` introduction will likely add new typed fields with their own membership constraints — apply this pattern.

### Pattern: Plan-line-number drift is structural, not incidental

**Discovered across:** Phase B Task 7/8/9 + Phase C Task 10 (4 data points).

**Pattern:** Phase plans were authored against earlier codebase shapes. Line numbers in plan text drift as tasks land. Examples:
- Phase B plan referenced `pending_request_store.py` lines that drifted across Tasks 6/7/8/9
- Phase C plan referenced `delegation_controller.py:1856-1884` for recovery audit; actual is `:1965-1994`
- Phase C plan referenced `journal.py:166-179` for entry construction; actual is `:166-180` (close, but drift)

**Robust localization:** Always locate by structural landmark — `def _journal_callback`, `op == "approval_resolution"`, `# --- approval_resolution reconciliation ---`, `entry = OperationJournalEntry(`. NEVER by absolute line number alone.

**Briefing implication:** Implementer briefings should explicitly direct "locate by structural landmark, not absolute line number" as a hard rule.

### Convention: `write_phase` uses `asdict(entry)` for serialization

`journal.py:305` and `:340` (compact) both serialize via `json.dumps(asdict(entry), sort_keys=True)`. Auto-handles new dataclass fields without explicit serialization changes.

**Implication for Phase C:** Adding `completion_origin` to `OperationJournalEntry` required NO change to `write_phase` or `compact()` — the new field is auto-included in `asdict(entry)` output. This is why Step 10.5 of the plan said "If the current serialization uses `asdict(entry)`, no change is needed."

### Convention: `_JOURNAL_OPTIONAL_STR` lists ALL optional string-typed journal fields

Every optional field where `field_value is None or isinstance(field_value, str)` should be listed. Phase C closeout added `"completion_origin"` to maintain pattern symmetry. Future fields must follow.

### Surprising Findings

- **`OperationJournal.replay_jsonl(...)` is NOT a class method.** Only the module-level `replay_jsonl` from `replay.py` exists. Tests hand-rolled by Phase C plan called `journal.replay_jsonl(...)` — would `AttributeError`. Caught by both my pre-dispatch audit and user's independent dispatch-watch-outs.
- **`replay_jsonl` swallows `SchemaViolation` into diagnostics.** Surprising because the function is named "replay" and the exception is named "violation" — sounds like it should propagate. But the design is deliberate: replay must survive corrupted records. Test surface is `check_health()` for diagnostic inspection.
- **Per-op `decision` check redundancy.** The `approval_resolution.intent/dispatched` blocks (`:130-136`, `:144-150`) check `decision is None or isinstance(decision, str)` AFTER the global `_JOURNAL_OPTIONAL_STR` loop already enforced this. Tautological-but-safe — the per-op check is structurally redundant. Quality reviewer flagged in tautological-but-safe analysis (NOT classified as defect).
- **`Literal["worker_completed", "recovered_unresolved"] | None`'s membership constraint is type-system documentation, not a runtime guard.** Python doesn't validate `Literal` at construction. The closeout fix's membership-check block is what enforces it at runtime (replay).
- **Pyright cache staleness extends to harness re-runs vs direct CLI.** Direct `uv run pyright <file>` reports 0/0/0 on `journal.py`; harness pyright reports `★ "_VALID_COMPLETION_ORIGINS" is not accessed` (false positive). Match Phase B's "Cannot access attribute" pattern on test files.

### Key Locations

| Concept | Location |
|---|---|
| `OperationJournalEntry` dataclass | `models.py:367-401` (14 fields, including `completion_origin` from Task 10) |
| `OperationJournal` class | `journal.py:184-400` |
| `_journal_callback` validator | `journal.py:64-181` |
| `_VALID_OPERATIONS` frozenset | `journal.py:36-44` |
| `_VALID_PHASES` frozenset | `journal.py:45` |
| `_VALID_COMPLETION_ORIGINS` frozenset | `journal.py:62` (Phase C closeout) |
| `_JOURNAL_REQUIRED_STR` tuple | `journal.py:46-53` |
| `_JOURNAL_OPTIONAL_STR` tuple | `journal.py:54-61` (6 fields incl. `completion_origin`) |
| `_JOURNAL_OPTIONAL_INT` tuple | `journal.py:62` |
| `write_phase` (pure append) | `journal.py:300-307` |
| `_terminal_phases` (replay surface) | `journal.py:345-349` |
| `check_health` (diagnostic surface) | `journal.py:351-355` |
| `replay_jsonl` (module-level) | `replay.py:61-154` |
| `SchemaViolation`, `UnknownOperation` | `replay.py:18-27` |
| `ReplayDiagnostics.schema_violations` | `replay.py:55-58` |
| `recover_startup` (delegation) | `delegation_controller.py:1899-2030` |
| `approval_resolution` recovery loop | `delegation_controller.py:1965-1994` (post-Phase-C, with `completion_origin="recovered_unresolved"`) |
| Sibling test (operator-origin recovery) | `tests/test_delegation_controller.py:2129-2183` |
| New recovery test (None-decision) | `tests/test_delegation_controller.py:2186-2257` |
| `test_journal_completion_origin.py` | `tests/test_journal_completion_origin.py` (9 tests) |
| Packet 1 manifest | `docs/plans/2026-04-24-packet-1-deferred-approval-response.md` |
| Phase C plan | `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-c-journal.md` (424 lines) |
| Phase D plan (next) | `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-d-*.md` (NOT read this session) |
| Carry-forward tracker | `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (~83 lines post-Phase-C) |

### Dependency Graph (Packet 1 Phase C end state)

```
OperationJournalEntry (models.py:367-401, 14 fields incl. Phase C's completion_origin)
  └── used by: OperationJournal (journal.py)
        ├── write_phase()                      [pure append; asdict(entry); no validation]
        ├── _journal_callback                  [validator; runs on replay only]
        │     ├── _JOURNAL_REQUIRED_STR loop  (6 fields)
        │     ├── _VALID_OPERATIONS check     (5 op values)
        │     ├── _VALID_PHASES check         (3 phase values)
        │     ├── _JOURNAL_OPTIONAL_STR loop  (6 fields incl. Phase C's completion_origin)
        │     ├── _JOURNAL_OPTIONAL_INT loop  (2 fields)
        │     ├── _VALID_COMPLETION_ORIGINS check  [Phase C closeout — 9061d268]
        │     └── per-op-phase narrow checks  (turn_dispatch, thread_creation, job_creation,
        │                                       approval_resolution, promotion)
        ├── _terminal_phases() ────────► replay_jsonl(path, _journal_callback)
        ├── check_idempotency() ──────► _terminal_phases()
        ├── list_unresolved() ────────► _terminal_phases()
        ├── check_health() ───────────► replay_jsonl + return diagnostics
        └── compact() ────────────────► _terminal_phases() + temp-file rename

DelegationController.recover_startup (delegation_controller.py:1899-2030)
  └── reads: journal.list_unresolved(session_id) (replay surface)
  └── writes: journal.write_phase(...) for each unresolved entry
        ├── job_creation reconciliation       (lines 1924-1964)
        └── approval_resolution reconciliation (lines 1966-1994)
              └── writes phase="completed", completion_origin="recovered_unresolved"  [Task 10]

External writers of approval_resolution.completed records (Phase E future):
  └── _decide_approve_path / _decide_deny_path (delegation_controller.py:1828-1878 region)
        └── currently emits completion_origin=None (dataclass default) — C10.4 future-task
```

### Conventions Observed (Phase C end state)

- Tests use `tmp_path` pytest fixture for isolation
- Tests use `journal.write_phase(...)` to write valid records and raw `(operations_dir / "s1.jsonl").write_text(...)` for legacy/hand-crafted record injection
- JSONL records use `sort_keys=True` — deterministic serialization (`journal.py:305`, `:340`)
- `os.fsync()` after every write — durability convention (`:307`)
- `from server.X import Y` import style (NOT `codex_collaboration.server.*`)
- Commit messages use lowercase `feat`/`fix`/`docs(delegate):` prefix + task identifier `(T-20260423-02 Task X)` or `(T-20260423-02)` for cross-task fixes
- 3-commit phase-closeout shape (feat + closeout fix + closeout docs) is the canonical pattern

## Context

### Project State

- Branch: `feature/delegate-deferred-approval-response`
- Branch tip: `ee143b25`
- 14 commits on branch from Phase A baseline (`b6dbaa3c`):
  - `5120413b` feat — Task 6 (Packet 1 fields)
  - `3fbba140` fix — Task 6 (Critical-in-scope `update_status` replay fix; `replace()` origin)
  - `4a35e636` docs — Task 6 (carry-forward tracker)
  - `941e7efd` feat — Task 7 (success-path mutators)
  - `b623548b` fix — Task 7 (Important I-1 null-guard)
  - `038525ba` docs — Task 7 (B7.1 + B7.2)
  - `21b2eb7e` feat — Task 8 (atomic failure-path mutators)
  - `be46ecd6` docs — Task 8 (B8.1 + B8.2; first clean ship)
  - `16aca095` feat — Task 9 (`parked_request_id` + `update_parked_request`)
  - `c6bf834c` fix — **Phase B closeout** (tuple-loss bug; 4 branches → `replace()` + Task 9 cleanup bundled)
  - `23e427c6` docs — **Phase B closeout** (P1 closed entry + bundled M1/M2/M3)
  - `e8786626` feat — Task 10 (journal validator relaxation + `completion_origin` field)
  - `9061d268` fix — **Phase C closeout** (validate `completion_origin` Literal at journal replay)
  - `ee143b25` docs — **Phase C closeout** (C10.2/C10.3/C10.4 open + C10.1 closed)
- Working tree clean
- 944 tests in codex-collaboration package (was 934 at start of session; 942 after Task 10 feat; 944 after closeout fix)
- Phase C ✅ closed; Phase D ready for dispatch
- Carry-forward tracker: 12 open + 4 closed items

### Environment

- Python 3.12 (pytest runs under uv workspace selection)
- macOS (BSD sed/find)
- `uv run --package codex-collaboration pytest ...` from repo root
- `uv run --package codex-collaboration ruff check ...` for lint
- `uv run --package codex-collaboration pyright ...` for type checking (impl files only; test files use a different config)
- Direct `uv run --package codex-collaboration pyright <file>` is the ground-truth pyright surface (harness pyright re-runs may have cache staleness)

### Mental Model

**Framing:** Phase C is "narrow validator relaxation + new provenance annotation," distinct from Phase B's "store-layer durability preservation." This shifts the principle-coherence calibration: Phase B's tuple-loss escalation was about preserving an existing invariant retroactively; Phase C's `completion_origin` validator gap is about completing a new invariant introduced this phase.

**Core insight (refined this session):** The 3-axis severity heuristic produces principled disposition decisions across DIFFERENT phase themes:
1. **Phase B (preservation theme):** Tuple-loss bug → Path A (in-scope fix) because retroactive principle imposition + concrete symptom + phase-defining-invariant violation.
2. **Phase C (relaxation/extension theme):** `completion_origin` validator gap → Path A1 (closeout fix with COMPLETE validation) because new-feature completeness gap + dormant symptom + phase-defining-invariant violation (the "Literal field has membership validator" pattern).

The shared element across both is "phase-defining invariant violation." The differentiator is the precondition + symptom shape AND the fix scope (Phase B = multi-branch migration; Phase C = surgical 3-edit add). Same heuristic, different outcomes, both principled.

**Mental model — Phase shape:** Phase C has the shape "single task that touches the journal validator + 1 dataclass field + 1 recovery callsite." Phases D-H will have different shapes (consumer-wiring, ResolutionRegistry coordination), but the principle-coherence audit at phase boundaries is durable.

**Mental model — Reviewer hierarchy (post-Phase-C):**
1. Implementer (haiku) — mechanical transcription with deviation disclosure
2. Spec reviewer (sonnet) — plan literality + observation collection
3. Quality reviewer (sonnet) — severity classification on observations + independent audit
4. Coordinator (this seat) — disposition decision: in-scope fix vs separate-commit fix vs carry-forward
5. User (final) — phase-boundary principle coherence + escalation + structured 9-section disposition analysis when Path A vs B emerges

The user's structured 9-section disposition analysis is now a **recurring pattern at phase boundaries** — they explicitly produce one when the coordinator surfaces a Path A vs B moment. Format: (1) Decision To Make + type; (2) Stakes; (3) Options enumerated; (4) Information Gaps; (5) Per-option Evaluation; (6) Sensitivity; (7) Ranking; (8) Recommendation; (9) Readiness.

### Phase C → Phase D transition state

Phase D introduces the cross-thread `ResolutionRegistry` coordination primitive. Plan section: `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-d-*.md` (NOT read this session — likely named after the registry).

**Patterns locked at Phase C end (apply to Phase D):**
- Use `dataclasses.replace(existing, **changes)` for replay branches if Phase D introduces new replay code (Phase B lock)
- Apply `or ()` defensive coercion if any new field is a tuple/list read via `dict.get(...)` (Phase B lock)
- Add `_VALID_*` frozenset for any new Literal-typed field; check membership at validator (Phase C lock)
- Add new optional string-typed fields to `_JOURNAL_OPTIONAL_STR` if they're journal-bound (Phase C lock)
- `assert type(...) is expected_type` regression tests for any new dataclass replay path (Phase B lock)
- Match the per-task feat + (any in-scope fix) + closeout-docs cadence (Phase B + C lock)
- Two-stage review (spec + quality reviewers) with independent audit asks (Phase B + C lock)
- Phase-boundary principle audit before closeout (Phase B + C lock)
- Pre-dispatch coordinator audit before haiku dispatch (Phase B + C lock)
- Pre-authorize ≥2 deviations in implementer briefing (Phase B + C lock)

**Caller-wiring constraints surfaced from Phase B Task 8 review (still in force for Phase D+):**
- **Lifecycle ordering is a CALLER invariant**, not a store invariant. Don't try to add ordering validation in stores. The stale-timer / registry-reserve contract is the actual prevention mechanism for timeout-after-resolution.
- **`dispatch_error` vs `interrupt_error` mutual exclusion is a CALLER convention** — not enforced by `record_timeout`'s signature or replay. Caller wiring in Phase D+ must preserve orthogonality deliberately — pass exactly one (or neither), not both.

## Conversation Highlights

**User opening (entire user-side initial message):**
> "Continue with **reading `docs/plans/2026-04-24-packet-1-deferred-approval-response/[phase-c-journal.md](http://phase-c-journal.md)` and locating the Task 10 section**"
— Single-message authorization for Phase C entry sequence (read-first, then dispatch).

**User dispatch-watch-outs (full message preserved — load-bearing for Pivot 1):**
> "**Important Dispatch Watch-Outs**
> The Phase C plan's sample test code has a few executable-shape problems Claude should fix rather than copy blindly:
> 1. `OperationJournal` has no public `replay_jsonl(...)` method. The round-trip tests should use `check_idempotency(...)`, `list_unresolved(...)`, `check_health(...)`, or the module-level replay helper through the real operations path.
> 2. `write_phase(...)` does not validate records before appending. A test like `with pytest.raises(SchemaViolation): journal.write_phase(...)` will not test the validator. To hit validation, write/read through `check_health(...)`, `list_unresolved(...)`, or `check_idempotency(...)`.
> 3. The legacy-record sample path in the plan uses `tmp_path / "journal" / "s1" / "journal.jsonl"`, but the actual operations path is `plugin_data_path / "journal" / "operations" / "{session_id}.jsonl"` via `_operations_path(...)`.
> 4. The narrowness tests need to prove both sides: `decision=None` is accepted only for `approval_resolution.intent` and `.dispatched`, while non-string non-None values remain schema violations."

**User confirmation on (a) + corrections to my analysis (Pivot 1, full message preserved):**
> "Proceed with **(a): always set `completion_origin='recovered_unresolved'` in the recovery loop**.
> Rationale: the field describes **who wrote the terminal `completed` journal marker**, not whether the original unresolved record had an operator decision. A recovered `decision='approve'` orphan and a recovered `decision=None` orphan are both cold-start recovery completions.
> Two corrections to fold into the implementer briefing:
> - Your B2 proposed `pytest.raises(SchemaViolation): journal.list_unresolved(...)` still won't work. `replay_jsonl()` catches `SchemaViolation` and records diagnostics; it does not raise. The test should call `journal.check_health(session_id='s1')` and assert one `schema_violation`, or call `list_unresolved()` and assert the bad record is skipped plus `check_health()` reports the violation.
> - For B4, don't ask for a '`decision=None` on non-approval op is rejected' test. In the current schema, `decision` is globally optional-string metadata, so `None` on another operation is not meaningful evidence of narrowness. The important narrowness proof is: `approval_resolution.intent/dispatched` accept `None`, but `decision=42` still produces a schema violation; required fields like `job_id`, `request_id`, `runtime_id`, and `codex_thread_id` remain enforced.
> No need to read the future worker-side Phase E write site before dispatching Task 10. The spec already makes the symmetric meaning clear: worker-written completed records later get `worker_completed`; recovery-written completed records now get `recovered_unresolved`."

**User Path A1 disposition decision (full structured 9-section message preserved — load-bearing for the F1 escalation):**
> "**1. Decision To Make** [...]
> **2. Stakes** Medium. [...]
> **3. Options** Path A1, Path A2, Path B, Null. [...]
> **5. Evaluation** Path A1: 'It closes the only structurally meaningful issue in the set: the new `completion_origin` field is a validator-facing journal field, and leaving it unvalidated makes the Phase C validator story incomplete. I would not do the partial `_JOURNAL_OPTIONAL_STR`-only fix; I'd make it complete with type + membership validation against `{"worker_completed", "recovered_unresolved"}` while still allowing `None`.' [...]
> **8. Recommendation** I recommend **Path A1: separate closeout fix for F1 only**, and make it a complete validation fix, not just adding `completion_origin` to `_JOURNAL_OPTIONAL_STR`. Concretely: add `completion_origin` validation in `_journal_callback` so `None`, `'worker_completed'`, and `'recovered_unresolved'` are accepted, while non-string values and unknown strings are reported as schema violations through `check_health()`. Carry F2/F3 as Minor test-parity polish, and treat F4 as note-only future wiring.
> **9. Readiness** `best available`. This becomes `verifiably best` after confirming the implemented Task 10 commit has no existing `_VALID_COMPLETION_ORIGINS`-style check."

**Implicit signals:**
- User authored an independent dispatch-watch-outs message in PARALLEL with my pre-dispatch analysis. This is a strong alignment signal — they're applying the same audit lens at the same time.
- User's structured 9-section disposition analysis is a recurring template at phase boundaries. Future-Claude should expect this format for any Path A vs B decision.
- User noted "No need to read the future worker-side Phase E write site before dispatching Task 10" — explicitly de-scoping coordinator pre-reads when not load-bearing for the current task. Useful calibration.
- User's `verifiably best` readiness check ("after confirming no existing `_VALID_COMPLETION_ORIGINS`-style check") demonstrates they want me to verify before acting on a recommendation, not just accept it. I did the grep.

## User Preferences

**Stated priorities (this session):**
- "Continue with **reading `docs/plans/.../phase-c-journal.md`...**" — affirms read-first-then-dispatch sequencing for phase entries.
- "Proceed with (a): always set `completion_origin='recovered_unresolved'`" — confirms the "field describes who wrote the marker" semantic interpretation.
- "I would not do the partial `_JOURNAL_OPTIONAL_STR`-only fix; I'd make it complete with type + membership validation" — confirms "complete validation matches Literal type signature" principle.

**Carried forward from prior sessions (still in force):**
- **Recommendation-first decision style:** User accepts recommendations with refinements (or rejects with explicit reasoning). Confirmed by Path A1 explicit override of my Path B recommendation with structured 9-section reasoning.
- **Plan-first discipline / fix-immediately:** Important findings get fixed in scope; principle-coherence-elevated Minor findings (Phase B tuple-loss, Phase C F1) get fixed in closeout commit.
- **Trust-but-verify:** User's `verifiably best` readiness check is the first explicit codification of this — they want a specific verification before acting on a recommendation.
- **Plan-literal execution discipline:** Implementer briefing's "preserve literal plan execution" rule continues to hold. Where deviations exist, they are explicitly authorized (DEV-N) and disclosed in implementer report.
- **Carry-forward tracking durability:** From Phase A — items go in `carry-forward.md`, not just handoff narrative.
- **3-commit closeout shape:** From Phase B — feat + closeout fix + closeout docs. Audit-trail clarity > commit-count minimization.
- **1M context window calibration:** From Phase B Task 8 close — "we have plenty of room to proceed." Don't be context-budget-cautious within a session.

**New preferences observed this session:**
- **Structured 9-section disposition analysis at phase-boundary Path A vs B moments.** Format: (1) Decision To Make + type; (2) Stakes; (3) Options enumerated; (4) Information Gaps; (5) Per-option Evaluation with strength/weakness/best-when; (6) Sensitivity; (7) Ranking; (8) Recommendation; (9) Readiness with verification condition. This is now the recurring template at phase boundaries.
- **Proactive dispatch-watch-outs.** User authored independent audit findings in parallel with my pre-dispatch analysis. They're applying the same audit lens — coordinator can rely on this as a check rather than the sole authoritative pre-audit.
- **Explicit de-scoping when coordinator pre-reads aren't load-bearing.** User said: "No need to read the future worker-side Phase E write site before dispatching Task 10. The spec already makes the symmetric meaning clear." This calibrates how much pre-reading is "enough" — read what affects the current task, defer the rest.
- **`verifiably best` readiness as a recurring concept.** User's MCDM-style readiness signal: `best available` until a specific verification confirms; then `verifiably best`. Future-Claude should expect this signal and perform the verification before acting.
- **Preference for "complete" rather than "partial" fixes when the type signature implies coverage.** User explicitly rejected partial `_JOURNAL_OPTIONAL_STR` fix because Literal type implies membership validation. Generalize: when adding type-system coverage, match the semantic constraint, not just the structural constraint.

**Communication:** Concise, evidence-backed, file-linked. Single-line directives where possible BUT extensively structured (9-section MCDM templates) when disposition decisions are load-bearing. Expects coordinator to maintain context without re-statement. Provides corrections with explicit refinements (the B2/B4 corrections came with replacement test patterns inline).

## Learnings

### Pre-dispatch audit pattern is durable across phase entries

**Refined heuristic:** Default to coordinator pre-reads of all touched code before haiku dispatch. The audit catches plan-text staleness (line numbers, function references, helper-existence claims) BEFORE the implementer encounters them.

**Mechanism:** Phase B Task 9 introduced this pattern when the `asdict_for_replay` phantom helper escalation was caught. Phase C Task 10 confirmed it when 6 plan-text issues were caught (4 of which user independently surfaced, validating the audit's findings).

**Evidence:** Five tasks now (Phase B 7, 8, 9 + Phase C 10 + Phase B closeout fix) confirm pre-dispatch audits produce findings worth pre-authorizing.

**Implication:** Phase D entry should default to coordinator pre-reads. The audit cost (~30k tokens) is far less than the wrong-implementation cycle cost (~80k+).

**Watch for:** First case where pre-audit produces zero findings. Would suggest the plan is current and audit is unnecessary overhead.

### Pre-authorize-deviations pattern scales beyond 3 deviations

**Mechanism:** Phase B Task 9 pre-authorized 3 deviations and shipped clean. Phase C Task 10 pre-authorized 6 deviations and shipped clean. The deviation-disclosure protocol (implementer must explicitly name each DEV-N) functions as the verification handshake — spec reviewer cross-checks against the diff.

**Evidence:** Both tasks shipped with all deviations confirmed-applied at spec review.

**Implication:** The deviation-count threshold is at least 6 for haiku tier. This is far higher than I would have expected — the explicit code templates per DEV-N do most of the cognitive work; the implementer just transcribes.

**Watch for:** First case where ≥7 deviations are needed. May reach a complexity ceiling. Mitigation: split task into multiple commits (each with its own deviations) or escalate to sonnet implementer.

### `replay_jsonl` corruption-tolerance is non-obvious from the function name

**Mechanism:** `replay_jsonl(path, callback)` catches `SchemaViolation` + `UnknownOperation` from the callback (`replay.py:109-126`), converts to `ReplayDiagnostic`, skips the bad record, continues. Only programmer-bug exceptions propagate.

**Evidence:** Verified directly by reading `replay.py:14-126`.

**Implication:** Tests of validator behavior must use `check_health(session_id="s1")` to inspect `ReplayDiagnostics.schema_violations`. NOT `pytest.raises(SchemaViolation): journal.list_unresolved(...)` — the SchemaViolation is swallowed before reaching the caller.

**Watch for:** Any future code that wraps `replay_jsonl` with `pytest.raises(SchemaViolation)` — false-positive test that silently passes.

### Pyright cache staleness extends to harness vs CLI divergence

**Mechanism:** Direct `uv run pyright <file>` reports 0 errors on `journal.py`; harness pyright re-runs report `★ "_VALID_COMPLETION_ORIGINS" is not accessed` (false positive). Cache + config drift between the two pyright invocations.

**Evidence:** Confirmed this session — harness reported 11 new diagnostics; direct pyright on `journal.py` reported 0/0/0; all harness "errors" outside Task 10's diff confirmed pre-existing at `23e427c6`.

**Implication:** When triaging new harness pyright diagnostics, ALWAYS cross-reference against the prior commit (`git show <prev>:<file>` for the affected lines). Direct CLI pyright is the ground-truth source-file pyright surface.

**Watch for:** Future commits that introduce real pyright errors. The pattern of "all new harness diagnostics are pre-existing" is the load-bearing claim that must hold — verify each time.

### The 3-axis severity heuristic generalizes across phase themes

**Mechanism:** Phase B's tuple-loss escalation was about preserving an existing invariant retroactively (preservation theme); Phase C's `completion_origin` validator gap is about completing a new invariant introduced this phase (relaxation/extension theme). Both meet the principle-coherence axis bar via "phase-defining invariant violation" but with different precondition + symptom shapes.

**Evidence:** Two phase closeouts now (Phase B + Phase C) where principle-coherence elevation was the deciding factor for fix-this-session vs carry-forward.

**Implication:** The heuristic is theme-agnostic. Future phases can apply it regardless of whether they're "preservation," "relaxation," "introduction," or "wiring" themed.

**Watch for:** A phase where the principle-coherence axis seems to apply but elevation feels wrong. Would suggest the heuristic needs refinement (perhaps a "scope creep" guard).

### User's structured 9-section disposition analysis is a recurring phase-boundary template

**Mechanism:** User authored a 9-section MCDM-style analysis when asked to choose between Path A vs B for F1. Format includes: Decision To Make + type, Stakes, Options enumerated, Information Gaps, Per-option Evaluation with strength/weakness/best-when, Sensitivity, Ranking, Recommendation, Readiness with verification condition. This format is itself a learnable template.

**Evidence:** This is the first session where the user explicitly produced this format. But the prior session's Path A escalation message had similar structure (less explicit). Pattern is emerging across phase boundaries.

**Implication:** Future-Claude should EXPECT this format when surfacing a Path A vs B moment to the user. Format the surface-up to align: name the options, name the stakes, name the information gaps, recommend with reasoning. The user will respond in 9-section structure.

**Watch for:** Phase D Task 11+ disposition decisions. Expect the same 9-section response format from the user.

### Self-verification pattern is now used 5+ times durably

**Mechanism:** Tightly-scoped + user-specified or reviewer-directed fixes (≤ ~100 lines, single or 2-file scope, no ambiguity) → controller self-verifies via `git show` + `pytest` + `pyright` + diff inspection. Skip re-dispatch.

**Evidence:** Used at: Task 6 fix, Task 7 fix, Task 8 close, Phase B closeout fix, Phase C closeout fix = 5 data points across two phases. All clean.

**Implication:** Pattern is durable. For Phase D+, default to self-verify when the scope criteria match.

**Watch for:** First failed self-verification (would invalidate the pattern). Would flag implementer report unreliability and force re-review on all subsequent self-verify candidates.

## Next Steps

### 1. Phase D entry — read Phase D plan + Task 11 dispatch (or whichever is the first Phase D task)

**Plan section:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-d-*.md` (NOT read this session). Per Phase B + Phase C epilogues: "Phase D introduces the cross-thread `ResolutionRegistry` coordination primitive."

**What it adds (anticipated, NOT verified by reading the plan):** A new `ResolutionRegistry` class for cross-thread coordination. Likely new dataclass(es), likely new typed fields, likely new replay surface or new validator coverage.

**Dependencies:** Phase C complete at `ee143b25`. No blockers.

**What to read first:**
- The Phase D plan section (entire file, plus any sub-files)
- Existing `ResolutionRegistry` references in the codebase (likely none; this is the introduction)
- The caller-wiring constraint surfaces from Phase B Task 8 review (lifecycle ordering, dispatch_error/interrupt_error orthogonality)
- `carry-forward.md` (post-Phase-C-close state, may have items relevant to Phase D — especially C10.4 which is "wire `worker_completed`" likely Phase D-adjacent)

**Approach suggestion:** Same subagent-driven-development pattern. Model tier: haiku for implementer, sonnet for reviewers. Briefing notes for the implementer:

1. **"Preserve literal plan execution: if adapting any sample, report the deviation explicitly."**
2. **"Phase A/B/C carry-forward items are NOT Phase D scope unless encountered directly; do not opportunistically fix them."**
3. **"For any new replay code: use `dataclasses.replace(existing, **changes)` directly. Phase B locked this; skip any plan reference to `asdict_for_replay`."**
4. **"For any new tuple/list-typed field read via `dict.get(...)`: apply `record.get(key) or default` defensive coercion. Phase B Task 7 established."**
5. **"For any new Literal-typed field on a journal-validator-touched dataclass: add to `_JOURNAL_OPTIONAL_STR` (type half) AND add `_VALID_*` frozenset + membership check (membership half). Phase C closeout established."**
6. **"Add `assert type(...) is expected_type` regression tests for any dataclass replay path. Equality alone doesn't catch silent type-contract violations."**
7. **"Locate code by structural landmark, not absolute line number. Plan line numbers may have drifted."**

**Special review focus:**
- Caller-wiring orthogonality (`dispatch_error` vs `interrupt_error`) per Phase B Task 8 review
- New Literal-typed field validator coverage (Phase C lock)
- ResolutionRegistry race condition exposure (this is a coordination primitive — verify timing semantics)

**Acceptance criteria:** Phase D first-task commit lands cleanly; spec ✅; quality ✅; full-package regression clean (≥948 tests, up from 944 — assuming task adds ≥4 tests).

### 2. C10.4 — wire `completion_origin="worker_completed"` in worker decide path

Per Phase C carry-forward C10.4: the `decide()` path `write_phase` calls in `delegation_controller.py` (deny + approve, both writing `phase="completed"` records) currently emit `completion_origin=None` via the dataclass default. This is the worker-side counterpart to Phase C's recovery-side `completion_origin="recovered_unresolved"` annotation.

**Likely scope:** 2 line additions in `delegation_controller.py` (one for `_decide_approve_path`, one for `_decide_deny_path` write_phase calls). Test additions to verify worker-written records carry the field correctly.

**When:** Either as part of Phase D scope (if naturally adjacent) OR as a standalone commit during Phase D execution. Not a separate task per the plan; carry-forward note only.

### 3. Phase B + C carry-forward sweep at end of Phase D or Phase F

12 open items at end of Phase C:
- A1, A2, A3 (3 items waiting for Tasks 14/15/16)
- A4, A5 (2 items, end-of-phase polish)
- B6.1, B6.2 (2 items, end-of-phase polish)
- B7.1, B7.2 (2 items, end-of-phase polish — B7.1 is the only concrete lint-cleanliness issue per user's Phase B note)
- B8.1, B8.2 (2 items, end-of-phase polish)
- C10.2, C10.3 (2 items, sibling-parity test gaps)
- C10.4 (1 item, worker-side wiring — likely closes during Phase D)

**Recommendation:** Sweep at end of Phase D or end of Phase F. Most are cosmetic; C10.4 will likely close during Phase D execution naturally; B7.1 is the most concrete (lint cleanliness) but user explicitly deferred it.

### 4. Optional: Audit other typed-field validators in the codebase for `_VALID_*` pattern coverage

The Phase C closeout established `_VALID_COMPLETION_ORIGINS` for journal Literal-typed fields. Other stores in the package (`pending_request_store.py`, `delegation_job_store.py`, `lineage_store.py`) may have similar Literal fields lacking dedicated validation. Could be:
- Surface in Phase D if it touches stores directly
- Or schedule as a separate audit task at end of Phase H
- Or carry-forward and address in Phase H sweep

**Pattern to grep for:** `Literal\[.*\] \| None = None` in `models.py` — locates new Literal-typed fields. Cross-reference against the corresponding store's validator coverage.

## In Progress

Clean stopping point. Phase C (Task 10) fully landed across this session. Carry-forward tracker updated with all closed entries. Working tree clean. Phase D ready for dispatch in a fresh session.

**No work in flight.**

## Open Questions

### Does Phase D's plan introduce new Literal-typed fields requiring `_VALID_*` frozensets?

`phase-d-*.md` not read this session. Phase D is "ResolutionRegistry coordination primitive" per Phase C epilogue. Coordinator pre-read should locate any new Literal fields and apply the Phase C `_VALID_*` lock-in language in implementer briefings.

### Should `worker_completed` wiring (C10.4) happen in Phase D or as a standalone task?

Phase D scope unclear without reading the plan. If Phase D touches `delegation_controller.py:1828-1878` region naturally, fold in. If not, schedule as a separate small commit during Phase D execution.

### Are there other Literal-typed fields in `OperationJournalEntry` (or other journal-bound dataclasses) lacking `_VALID_*` coverage?

Quick check: `OperationJournalEntry.operation` (covered by `_VALID_OPERATIONS`), `.phase` (covered by `_VALID_PHASES`), `.completion_origin` (covered by `_VALID_COMPLETION_ORIGINS` post-closeout). All Literal fields in `OperationJournalEntry` are now covered. But future fields will need explicit attention.

### When does the carry-forward tracker hit the 30-item migration threshold?

Currently 12 open items at end of Phase C. Phase D-H have ~12 more tasks (11-22). Average ~1-2 carry-forward items per task. Linear projection: ~24-36 items by end of Task 22.

**Recommendation:** Monitor at end of Phase D and end of Phase F. If approaching 25, sweep early. If below 20 at end of Phase F, defer to end of Phase H.

## Risks

### Phase D plan may have similar plan-text staleness

Plans were authored in batch; staleness affects all of them. Phase D plan may have stale line numbers, stale helper references (`asdict_for_replay`), stale function-method references (`replay_jsonl` as method).

**Mitigation:** Coordinator pre-reads Phase D plan section AND reads all touched code before dispatch. Surface stale references in implementer briefing as pre-authorized deviations. Reference Phase B + C commits as locked precedent.

### `_VALID_*` pattern doesn't have generic Literal-validation infrastructure

Each new Literal field requires its own bespoke frozenset + check block. As Phase D-H introduce more Literal fields, the validator function will grow. Could become a maintenance burden.

**Mitigation:** Monitor at end of Phase F. If 5+ Literal fields with bespoke validation, consider introducing a `_JOURNAL_OPTIONAL_LITERAL` generic pattern. NOT scoped for this phase.

### Harness pyright noise will continue surfacing pre-existing diagnostics on every commit

Each new harness pyright re-run reports the full pre-existing error set, plus any cache-stale "not accessed" hints. Cross-reference cost grows.

**Mitigation:** Always cross-reference against prior commit (`git show <prev>:<file>` for affected lines) before triaging. Document the pre-existing pyright surface in a stable location if it grows.

### Pre-dispatch audit cost grows with phase complexity

Phase C's audit cost ~30k tokens. Phase D's `ResolutionRegistry` introduction may be larger (new class, new coordination primitive, new lifecycle).

**Mitigation:** Reading `phase-d-*.md` first and prioritizing high-risk surfaces (replay code, validator code, recovery code) keeps audit scope tractable.

### User offline during Phase D closeout means principle-coherence axis must be coordinator-applied

User functioned as 5th reviewer for principle coherence on F1 escalation via the structured 9-section disposition. If user is offline during a future phase closeout, coordinator must apply the third-axis lens independently.

**Mitigation:** Coordinator pre-checks at every phase boundary: "Does this finding contradict a phase-defining invariant? If yes, treat as Important regardless of symptom." Default-toward-Path-A when in doubt at phase boundaries. User can correct on next interaction.

### Self-verification pattern could mask deviations if implementer report quality degrades

Pattern works because implementer reports are reliable (5/5 data points). If a future implementer report inaccurately claims "no deviations encountered," self-verification might miss the gap.

**Mitigation:** Continue verifying via `git show` (independent of implementer report). Track first failed self-verification — if it occurs, switch back to mandatory re-review.

### Three-axis severity heuristic could elevate false positives during Phase D-H

Each phase introduces new "phase-defining invariants." A coordinator overly eager to apply the principle-coherence axis could escalate every cosmetic finding. The heuristic requires discipline.

**Mitigation:** Apply third axis only when (a) the finding is in code Phase X locked in patterns for, AND (b) leaving the finding visibly contradicts the lock-in. Phase C's F1 met both: locked the `_VALID_*` pattern for journal Literal fields; F1 contradicted it.

## References

- **Plan manifest:** `docs/plans/2026-04-24-packet-1-deferred-approval-response.md`
- **Phase C plan:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-c-journal.md` (424 lines, single Task 10)
- **Phase D plan (next):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-d-*.md` (NOT read this session)
- **Carry-forward tracker:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (~83 lines post-Phase-C)
- **Spec source:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`
- **Prior handoff (resumed from):** `docs/handoffs/archive/2026-04-24_23-24_phase-b-complete-replay-preservation-locked.md`
- **Phase A-C commits (chronological, 14 total):**
  - Phase A: `5120413b`, `3fbba140`, `4a35e636`
  - Phase B Task 7: `941e7efd`, `b623548b`, `038525ba`
  - Phase B Task 8: `21b2eb7e`, `be46ecd6`
  - Phase B Task 9 + closeout: `16aca095`, `c6bf834c`, `23e427c6`
  - Phase C Task 10 + closeout: `e8786626`, `9061d268`, `ee143b25`
- **Subagent-driven-development skill:** `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/subagent-driven-development/`

## Gotchas

### `OperationJournal.replay_jsonl(...)` is NOT a class method

Plan-text fiction in Phase C plan. Only the module-level `replay_jsonl` from `replay.py` exists. The class exposes `check_idempotency`, `list_unresolved`, `check_health`, `compact`. Tests calling `journal.replay_jsonl(...)` will `AttributeError`.

**Test surface for completed-record round-trips:** `journal.check_idempotency(key, session_id="s1")` returns the terminal-phase entry by key.

### `OperationJournal.write_phase(...)` does NOT validate

`journal.py:300-307` is a pure append (`json.dumps(asdict(entry))`). Validator runs only on replay via `_terminal_phases` → `replay_jsonl(path, _journal_callback)`. Tests using `with pytest.raises(SchemaViolation): journal.write_phase(...)` silently pass.

**Test surface for validation:** `journal.write_phase(bad)` then `journal.check_health(session_id="s1")` and inspect `diagnostics.schema_violations`.

### `replay_jsonl()` swallows `SchemaViolation` into diagnostics

`replay.py:109-117`: `SchemaViolation` is caught, converted to `ReplayDiagnostic(label="schema_violation")`, accumulated in `immediate_diagnostics`. Bad record is skipped. The exception does NOT propagate.

**Implication:** Tests using `with pytest.raises(SchemaViolation): journal.list_unresolved(...)` silently pass for the same reason.

### Plan line numbers drift across phases

Phase C plan was written when codebase was smaller. Line numbers drift as tasks land:
- `delegation_controller.py:1856-1884` (plan claim, recovery audit) → actual `:1965-1994`
- `journal.py:166-179` (plan claim, entry construction) → actual `:166-180`

Locate by structural landmark (`def _journal_callback`, `op == "approval_resolution"`, `# --- approval_resolution reconciliation ---`, `entry = OperationJournalEntry(`), not by absolute line number.

### `OperationJournalEntry` doesn't enforce field types at construction

Python's `@dataclass(frozen=True)` doesn't validate field types at construction. `OperationJournalEntry(decision=42, completion_origin="garbage")` constructs cleanly. Validation only fires on replay via `_journal_callback`. This is what makes the bad-record write tests possible at all.

### `Literal["worker_completed", "recovered_unresolved"] | None` is a documentation-only type at runtime

The Literal annotation is a static-type hint. Runtime guard is the validator (`_VALID_COMPLETION_ORIGINS` membership check, post-closeout). NEVER assume Literal field values are constrained at the dataclass level.

### `_JOURNAL_OPTIONAL_STR` and `_VALID_COMPLETION_ORIGINS` are PARALLEL pattern, not sequential

Type half (`_JOURNAL_OPTIONAL_STR` loop, `journal.py:80-83`) catches non-string values like `completion_origin=42`. Membership half (`_VALID_COMPLETION_ORIGINS` check, `journal.py:88-92`) catches invalid Literal strings like `completion_origin="garbage"`. BOTH are needed for complete coverage. Don't conflate them.

### Pyright cache staleness extends to harness re-runs

Direct `uv run pyright <file>` reports 0 errors on `journal.py`. Harness pyright re-runs may report `★ "_VALID_COMPLETION_ORIGINS" is not accessed` (false positive). Generalizes Phase B's "test files reference new methods that pyright thinks don't exist" pattern.

**Disambiguation:** Direct CLI pyright is ground truth for source files. Test-file pyright is allowed to lag (different config).

### Self-verification skips re-review under context pressure or for tightly-scoped fixes

Pattern locked across 5 fixes now (Tasks 6/7/8 in-scope + Phase B closeout + Phase C closeout). Skip the spec/quality reviewer cycle when: (a) user-spec'd or reviewer-directed, (b) ≤100 lines, (c) ≤2 files, (d) no ambiguity. Verify directly via `git show` + `pytest` + `pyright` + diff inspection.

### Branch has 3 commits for Phase C closeout — do NOT squash

Task 10 feat (`e8786626`) + closeout fix (`9061d268`) + closeout docs (`ee143b25`) is the audit trail. Squashing would hide the principle-coherence escalation work.

### Recovery loop sets `completion_origin="recovered_unresolved"` UNCONDITIONALLY

`delegation_controller.py:1992` writes the field on every recovered-completed `approval_resolution` record, regardless of `entry.decision` value. The field semantics are "who wrote the marker" not "what was the original decision." Don't add conditional logic here in future tasks.

### Phase C carry-forward C10.4 is intentional, not a missed wiring

`Literal["worker_completed", "recovered_unresolved"]` includes `"worker_completed"` but no production callsite sets it. This is by-design — Phase C scope was deliberately narrow (recovery-side provenance only). Worker-side wiring is future-task scope (likely Phase D-adjacent).

### The 3-axis severity heuristic can ELEVATE quality-reviewer-Minor findings to Important

F1 was quality-reviewer-classified Minor. User's principle-coherence framing elevated it to Important. The heuristic is principled but produces non-obvious dispositions. Always surface Path A vs B at phase boundaries when a Minor finding might violate a phase-defining invariant.
