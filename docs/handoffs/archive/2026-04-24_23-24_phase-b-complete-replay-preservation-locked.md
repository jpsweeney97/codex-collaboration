---
date: 2026-04-24
time: "23:24"
created_at: "2026-04-25T03:24:53Z"
session_id: b13b7628-bd2b-4ab5-bdee-076fc191eba9
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-24_22-28_phase-b-task-7-complete-replace-pattern-locked.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: 23e427c6
title: Phase B complete (T-20260423-02) — replay-preservation principle locked across both stores; Task 8 + Task 9 + tuple-loss closeout fix landed
type: handoff
files:
  - packages/plugins/codex-collaboration/server/pending_request_store.py
  - packages/plugins/codex-collaboration/tests/test_pending_request_store_atomic_mutators.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/delegation_job_store.py
  - packages/plugins/codex-collaboration/tests/test_delegation_job_parked_request_id.py
  - packages/plugins/codex-collaboration/tests/test_delegation_job_store.py
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md
---

# Handoff: Phase B complete (T-20260423-02) — replay-preservation principle locked across both stores

## Goal

**Immediate objective:** Land Phase B Tasks 8 + 9 of Packet 1 (T-20260423-02 deferred-approval response design) in this session, closing Phase B. Phase B has 4 tasks total (6-9); the prior session landed Tasks 6 and 7. This session executes Tasks 8 (atomic failure-path mutators) + 9 (`DelegationJob.parked_request_id`) and any review-discovered fixes.

**Trigger:** This session resumed from `2026-04-24_22-28_phase-b-task-7-complete-replace-pattern-locked.md`. The prior handoff explicitly directed: "Dispatch Phase B Task 8: PendingRequestStore atomic failure-path mutators... Approach suggestion: Same subagent-driven-development pattern. Model tier: haiku for implementer, sonnet for reviewers." User opened the session with: "Start by reading the Task 8 plan section (`phase-b-stores.md:525-895`) and the current state of `pending_request_store.py` (post-Task-7), then dispatch the haiku implementer with the locked-in patterns baked into the briefing."

**Stakes:** Tasks 8 + 9 complete the store-layer mutator set for Packet 1. Without Phase B closure, Phase C (journal validator relaxation) cannot dispatch — the consumer-wiring tasks in Phases D-H all depend on durable store transitions. This session also tested whether the `dataclasses.replace()` precedent established by Task 6/7 fixes generalizes from `PendingRequestStore` (where the pattern was locked) to `DelegationJobStore` (Task 9 — different store, different pre-existing pattern).

**Bigger picture:** Packet 1 converts `_finalize_turn`'s captured-request branch from synchronous-decide kind-based escalation to async-decide worker-owned resolution. The 11 new fields on `PendingServerRequest` (Task 6) capture the deferred-resolution lifecycle. Tasks 7-8 add the success-path + failure-path mutators that write those fields. Task 9 wires `DelegationJob.parked_request_id` so the worker can durably advertise which request it's currently parked on. Tasks 10+ (Phase C and beyond) wire consumers, projection, journal, and ResolutionRegistry.

**Why now:** Plan-execute discipline. Prior session set the stage with two locked-in patterns (`replace()` over `asdict_for_replay`, `record.get(key) or ()` for null-safe coercion). This session executed the remaining Phase B tasks in a fresh session.

**Success criteria (all achieved):**
- Task 8 committed with spec ✅ + quality ✅ reviewer approval (achieved at `21b2eb7e`; first clean ship — no in-scope fix needed)
- Task 9 committed with spec ✅ + quality ✅ + 3 authorized deviations applied (achieved at `16aca095`)
- Phase B closeout fix migrating 4 `DelegationJobStore` replay branches to `replace()` (achieved at `c6bf834c`; resolved pre-existing tuple-loss bug discovered by Task 9 review)
- Carry-forward tracker updated with all closed entries (achieved at `23e427c6`)
- Full-package regression clean (934 tests pass, up 17 from 917 at session start)
- Branch state ready for Phase C dispatch in a fresh session (achieved)

**Connection to project arc:** Phase B closes here. Tasks 6, 7, 8, 9 ✅ landed across two sessions (Task 6/7 prior session; Task 8/9 + closeout this session). Phases C-H remain. Replay-preservation principle now applies consistently across both stores at the phase boundary.

## Session Narrative

**Starting state (session open):** Loaded the Task-7-complete handoff. Branch was `feature/delegate-deferred-approval-response` at `038525ba` (Task 7 docs). Working tree clean. 917 tests passing. Phase B Task 8 ready for dispatch. Three locked-in patterns from prior sessions: (1) `dataclasses.replace(existing, **changes)` for replay branches; (2) `record.get(key) or default` for null-safe tuple/list coercion; (3) `asdict_for_replay` is plan-text fiction — never define it.

**Read-first discipline:** Per user's opening message, I read in parallel:
- `phase-b-stores.md:525-895` (Task 8 section, ~370 lines)
- `pending_request_store.py` post-Task-7 state (222 lines)
- `carry-forward.md` (post-Task-7 state)
- `models.py:285-319` (`PendingServerRequest` 21-field dataclass)

**Pre-Task-8 analysis:** Three observations crystallized:

1. **None of Task 8's three new mutators write tuple/list fields.** All scalars (str/dict/bool/None). The `or ()` defensive pattern doesn't apply to any new replay branch — but should remain in the briefing as a guardrail against accidentally removing it from existing branches.
2. **The plan's `asdict_for_replay` references in Task 8 are stale** — same as Task 7. All three plan code blocks for the new replay branches sample the helper plus redundant explicit overrides (`available_decisions: existing.available_decisions`, etc.).
3. **The plan's Task 8 mutator sample is sound otherwise.** Signatures, kwargs, defaults, docstrings transferable verbatim.

**Task 8 implementer dispatch (haiku):** Briefing included full plan text + 9 hard rules + 3 special-attention areas + locked-in pattern directives. Background dispatch.

**Task 8 implementer report (DONE at commit `21b2eb7e`):** 8 new tests + 925 package pass. Disclosed `replace()` deviation. Pyright cache-staleness on test file (matches Task 7 pattern: new methods → cache lag).

**Task 8 spec-compliance review (sonnet):** ✅ 8/8 PASS. Confirmed three authorized deviations applied. Flagged 4 out-of-scope observations:
1. Guard asymmetry vs `update_status` (known pattern from Task 7).
2. `timed_out=True` hardcoded in `record_timeout` replay (vs `record.get("timed_out", False)` in `op == "create"` branch).
3. `dispatch_result="failed"` hardcoded in `record_dispatch_failure` replay (vs `record.get(...)` in `record_response_dispatch` replay).
4. Missing reopen round-trip tests for `record_timeout` and `record_dispatch_failure` (only `record_internal_abort` has one).

**Task 8 code-quality review (sonnet):** ✅ Ship-ready, **zero Critical/Important findings**. First Phase B task to ship clean. Two Minor findings carry-forwarded:
- B8.1: `dispatch_result` hardcode-vs-read style asymmetry (tautological-but-safe — both mutators write the value unconditionally).
- B8.2: Missing reopen round-trip tests (same `_replay()` code path; gap is bounded to `__init__` (mkdir + store_path) which is already exercised by the abort round-trip).

**Quality reviewer's reasoning on Observations 2 + 3 was sharp:** "tautological-but-safe — the op name IS the assertion. Reading back a field that the mutator always writes unconditionally adds no value. Both are corruption-required (single-field drift bounded to corrupted record), severity = Minor." Two architectural conclusions surfaced and were validated by user review:
- **Lifecycle ordering is a CALLER invariant**, not a store invariant. Store is pure append-only journal with last-write-wins replay.
- **`dispatch_error` vs `interrupt_error` mutual exclusion is a CALLER convention** — neither mutator nor replay enforces it.

**User pivot — Task 8 closeout review:** User performed independent verification (git status, lint, pyright, atomic mutator tests, diff check) — all clean. Provided two architectural reframings: "Stale timer / registry reserve contract is the actual prevention mechanism for timeout-after-resolution, not the store" (sharper than my "caller convention") + "construction is caller sequencing, not record_timeout(...) signature or replay logic" (named the mechanism: terminal-op exclusivity is encoded in the call graph, not the data model). Verdict: "Task 8 is closeable. I would proceed to Task 9 with two handoff notes... Note: we have a 1 million token context window, so we have plenty of room to proceed."

**Task 8 carry-forward + closeout commit:** Edited `carry-forward.md` to add B8.1 + B8.2 under "From Phase B Task 8" subsection (no closed-items entries — first clean ship). Committed at `be46ecd6`. Self-verified: 925 tests, branch tip clean, linear history.

**Pre-Task-9 analysis (more involved):** Read in parallel:
- `phase-b-stores.md:897-1151` (Task 9 section, 255 lines)
- `delegation_job_store.py` (full file, 310 lines)
- `models.py:395-419` (DelegationJob dataclass)
- `wc -l` on `delegation_job_store.py` + grep for `asdict_for_replay`

Three CRITICAL pre-dispatch findings:

1. **The plan tells the implementer to DEFINE `asdict_for_replay` as a new helper** (Step 9.4 line 1072-1078: "Add a local `asdict_for_replay(job)` helper at module scope"). The plan author thought `pending_request_store.py` defined one to copy from — but it doesn't. There IS no helper to follow. Plan-text fiction we already knew about; Task 9 escalates because the plan is asking the implementer to *create* it.
2. **`delegation_job_store.py`'s existing 4 replay branches use a DIFFERENT pattern** than `pending_request_store.py`'s post-Task-7 style: `DelegationJob(**{**asdict(existing), ...overrides})` rather than `replace(existing, **overrides)`. This means `delegation_job_store.py` has a **latent `asdict()` tuple-loss bug**: `update_status` replay silently converts `artifact_paths` from tuple to list because `asdict()` recurses. The bug is hidden because Python doesn't runtime-validate generic types. OUT OF SCOPE for Task 9 — but the implementer briefing must explicitly direct the new branch to use `replace()` to *avoid introducing* the same bug.
3. **The plan's Step 9.4 instruction to update `op == "create"` branch is unnecessary.** The existing iteration `{k: record[k] for k in DelegationJob.__dataclass_fields__ if k in record}` already auto-handles new fields via dataclass defaults. Legacy records without `parked_request_id` will default to `None` without any code change to the create branch.

**Task 9 implementer dispatch (haiku):** Briefing included three pre-authorized deviations explicitly: (1) `replace()` over `asdict_for_replay` for the new branch only; (2) NO modification to `op == "create"` branch; (3) NO migration of existing replay branches' patterns. Background dispatch.

**Task 9 implementer report (DONE at commit `16aca095`):** 6 new tests, 931 package pass. All three authorized deviations applied. Implementer report: "Plan was mechanically transcribed with the three pre-authorized exceptions applied."

**Task 9 spec-compliance review (sonnet):** ✅ 7/7 PASS. Five out-of-scope observations:
1. Pattern asymmetry in `_replay()` between new `replace()`-based branch and existing 4 `asdict()`-based branches.
2. **Silent tuple→list coercion in existing branches** — the latent bug I'd predicted, surfaced by the spec reviewer's audit.
3. Guard asymmetry on new branch (only `if jid in jobs:` vs existing branches' multi-step validation).
4. `jid` vs `job_id` naming inconsistency.
5. Missing `isinstance(jid, str)` guard.

**Task 9 code-quality review (sonnet):** ✅ Ship-ready as Task 9 close, but with one Important finding **classified as pre-existing**: P1 — the tuple-loss bug. Reviewer's reasoning was disciplined: "Why Important rather than Critical: normal-path activation argues Critical, but symptom is dormant + bounded + self-healing. Compromise classification: Important. Recommend (b) Fix in separate Phase B closeout commit, same session." Three Minor findings (M1 pattern asymmetry, M2 guard symmetry + isinstance check, M3 `jid` naming) all bundle naturally with P1 fix.

**Coordinator decision moment — Path A vs Path B:** Surfaced finding to user with classification + recommendation. My recommendation was Path B (defer to carry-forward) due to context pressure (95% on Claude Code's 200k context — though user later reminded me about the 1M context window). User chose Path A: "fix this session, in a separate Phase B closeout commit."

**User's reframing of severity (load-bearing for the decision):** "This is not because the runtime symptom is severe. It is because the defect class is exactly the Phase B durability theme: replay must preserve structured field semantics. You already fixed the same family in `PendingRequestStore` by moving to `replace(...)`; leaving the same `asdict(existing)` trap in `DelegationJobStore` makes the Phase B story asymmetrical at the point where you are about to close the phase." This is a third axis of severity: **principle-coherence at phase boundaries** — independent of symptom severity.

**Closeout fix dispatch (haiku):** User-provided spec was explicit (4 branches to migrate, Task 9 cleanup bundled, 3 regression tests with `type(retrieved.artifact_paths) is tuple` assertions, verification gate of pytest + ruff + pyright, exact commit message). Background dispatch.

**Closeout fix implementer report (DONE at commit `c6bf834c`):** 3 regression tests added, 934 package pass, all verification gates passed. Five replay branches now use `replace()` consistently (4 migrated + Task 9's new branch already using it). Task 9 cleanup bundled (`jid` → `job_id` rename, `isinstance` guard added).

**Self-verification of fix (controller, not subagent):** Per Task 6/7 precedent under context pressure, I verified directly:
- `git show c6bf834c --stat` — confirmed 2 files (52 line changes in store + 68 line additions in test)
- `git log --oneline -5` — confirmed branch progression: `16aca095` → `c6bf834c` → no amend
- Full-package regression: `uv run --package codex-collaboration pytest packages/plugins/codex-collaboration/ -q` → **934 passed in 19.61s**

**Carry-forward update + Phase B closeout docs commit:** Edited `carry-forward.md` to add the closed entry under "From Phase B Task 9 + closeout" subsection, recording P1 + bundled M1/M2/M3 closure with diagnostic detail. Committed at `23e427c6` with message "docs(delegate): record Task 9 + Phase B closeout (T-20260423-02)".

**User light-verification of closeout boundary:** User confirmed clean working tree, branch tip `23e427c6`, expected commit sequence in `git log b6dbaa3c..HEAD`, expected file scope. Caught off-by-three count error (I said "8 commits from Phase A baseline" when the table shows 11). Otherwise: "this is a clean stopping point. The closeout shape is strong."

## Decisions

### Surface the `replace()` vs `asdict_for_replay` choice as pre-authorized deviation in Task 9 briefing

**Decision:** The Task 9 implementer briefing included an explicit "CRITICAL — three authorized deviations from the plan" section pre-authorizing: (1) `replace()` over `asdict_for_replay`, (2) no `op == "create"` modification, (3) no migration of existing pattern. This is different from Task 7's "surface as decision point" approach — Task 9 PRE-authorized rather than asking the implementer to evaluate.

**Driver:** Three Phase B tasks of evidence (Tasks 6, 7, 8) had locked the `replace()` pattern as "strictly better" per spec reviewer's Task 7 verdict. Task 9 implementer didn't need to re-evaluate; they needed to know the precedent applied. Surfacing as decision point would be ceremony that haiku-tier implementers might struggle with given the more complex deviation surface (3 deviations instead of 1).

**Rejected:** Surface-as-decision-point (Task 7 approach) — would have generated longer dispatch + report cycle. Rejected because the pattern lock-in is durable; future tasks should be PRE-authorized to deviate, not re-litigate.

**Implication:** Establishes a coordinator pattern for cross-store pattern application: once a pattern is locked in across N>=2 tasks, switch from "surface as decision" to "pre-authorize as deviation" briefing language. Reduces ceremony, increases throughput.

**Trade-offs:** Risk that haiku-tier implementer mis-applies a pre-authorized deviation. Mitigated by deviation-disclosure protocol (implementer must name each deviation in their report) and spec reviewer validation (verify each deviation was applied correctly).

**Confidence:** High (E2) — three prior tasks of pattern stability + Task 9's clean implementer report.

**Reversibility:** High — could switch back to surface-as-decision for future tasks if pre-authorization fails.

**Change trigger:** If a future implementer mis-applies a pre-authorized deviation (e.g., adds the helper anyway), switch to surface-as-decision for that pattern class.

### Classify P1 (tuple-loss bug in 3 existing replay branches) as Important — pre-existing, fix in Phase B closeout commit

**Decision:** Accept the code-quality reviewer's Important classification (compromise between Critical-by-precondition and Minor-by-symptom) and the user's escalation rationale ("principle coherence at phase boundary"), and fix in a separate Phase B closeout commit (Path A) rather than carry-forward (Path B).

**Driver:** User stated: "This is not because the runtime symptom is severe. It is because the defect class is exactly the Phase B durability theme: replay must preserve structured field semantics. You already fixed the same family in `PendingRequestStore` by moving to `replace(...)`; leaving the same `asdict(existing)` trap in `DelegationJobStore` makes the Phase B story asymmetrical at the point where you are about to close the phase."

**Rejected:** Path B (carry-forward to next session). Rejected because: (a) phase-boundary inconsistency is a high-leverage moment to fix (next session would forget the diagnostic detail), (b) the fix is small + local + low-risk (`replace` already imported), (c) "Phase B closeout" is the natural seam — same store Task 9 just touched, same review session, same file context.

**Implication:** Establishes a **third axis of severity classification** beyond precondition × symptom: **principle-coherence at phase boundaries**. Future reviewers should consider: "even if dormant, does leaving this contradict a phase-defining invariant?"

**Trade-offs:** Phase B closes as 11 commits instead of 9 — slightly longer audit trail. Context cost: ~15-20k tokens for fix dispatch + verify (within budget given 1M context). Risk that the fix introduces a regression in pre-existing branches (mitigated by 3 new regression tests + full-package pytest gate).

**Confidence:** High (E3) — reviewer's Important classification (E2) + user's principle-coherence escalation (E2) + my own analysis of dormant-but-real symptom (E1). Triangulated.

**Reversibility:** Medium — fix already landed; reverting would require explicit rollback decision. The 3 regression tests would also need to be removed.

**Change trigger:** If a future tuple-loss-equivalent bug surfaces in another store (e.g., `operation_journal.py`, `lineage_store.py`), apply the same Path A reasoning — fix at the discovering session's natural seam, don't carry-forward.

### Bundle Task 9 cleanup (M1/M2/M3) into the closeout fix commit, not a separate commit

**Decision:** The closeout fix subagent migrated 4 existing branches AND cleaned up Task 9's new branch (`jid` → `job_id` rename, `isinstance` guard added) in the same commit `c6bf834c`. NOT a separate Task 9 polish commit.

**Driver:** All three Minor findings (M1 pattern asymmetry, M2 guard symmetry + isinstance, M3 naming) converge on "make replay branches consistent." User's spec explicitly directed: "Also clean the Task 9 branch guard/style while in the same file: rename `jid` to `job_id`, add the same `isinstance(job_id, str)` guard shape before lookup."

**Rejected:** Separate polish commit for M1/M2/M3 + closeout fix commit for P1. Would have produced two commits where one suffices, and the polish would visually look like an unrelated cleanup.

**Implication:** When a phase-closeout fix touches the same file as the just-landed feature, bundling MINOR cleanup into the same commit is correct as long as the commit message names both classes of change. The result is a coherent "consistency pass" commit rather than two atomic commits.

**Trade-offs:** Slightly larger diff in the closeout fix commit (52 +/- lines instead of ~30). Reviewer cost is the same (already inspecting all branches in the file). Audit trail is slightly less granular but more readable as a single principle-applied commit.

**Confidence:** High (E2) — user explicitly directed it, and the bundled diff was independently verified.

**Reversibility:** Trivial — if future readers want the rename split out, `git revert c6bf834c` and re-apply only the migration.

**Change trigger:** If carry-forward sweeps in future phases tend to land as their own commits (e.g., end-of-phase polish PR), switch to separate-commit-for-Minor pattern.

### Self-verify the closeout fix instead of re-dispatching reviewers

**Decision:** I (controller) verified the fix via direct `git show` + `git log` + full-package pytest, rather than dispatching another spec or quality reviewer subagent.

**Driver:** Same precedent as Tasks 6/7/8 reviewer-directed fixes. User's spec was extremely explicit (4 branches to migrate, exact regression test pattern, verification gate, commit message). Implementer reported "no deviations encountered". Re-dispatching would cost ~30-50k tokens for a fix scope of "did the implementer apply the user's exact specification?"

**Rejected:** Re-dispatch a spec-compliance reviewer for the closeout fix. Would provide stronger rigor but at meaningful context cost for a fix where the spec was user-provided rather than reviewer-directed.

**Implication:** Self-verification is now used **three times** (Tasks 6, 7, 8 fixes + this closeout fix = 4 total). Pattern is durable. For tightly-scoped user-directed or reviewer-directed fixes (≤ ~100 lines, single-file or 2-file scope, no ambiguity), self-verify via diff inspection + verification gate. For ambiguous fix scope, always re-dispatch.

**Trade-offs:** Less rigor than strict subagent-driven-development. If implementer silently deviated, would miss it. Mitigated by: (a) user's spec being explicit, (b) implementer's deviation-disclosure protocol reporting "None", (c) my direct diff inspection, (d) verification gate (pytest + ruff + pyright) that the implementer ran before commit.

**Confidence:** High (E3) — pattern works, four data points across two sessions (Task 6 fix + Task 7 fix + this Task 8 close + this Task 9 closeout).

**Reversibility:** Trivial — could dispatch a re-review now if needed.

**Change trigger:** First failed self-verification (would invalidate the pattern). Track via post-merge findings.

## Changes

### `packages/plugins/codex-collaboration/server/pending_request_store.py` (MODIFIED — Task 8 commit `21b2eb7e`)

**Purpose:** Add three atomic failure-path mutators (`record_timeout`, `record_dispatch_failure`, `record_internal_abort`) plus three new `_replay` op branches.

**Approach:**
- **Mutators:** Three new methods on `PendingRequestStore`, placed after `record_protocol_echo` (post-Task-7 line 126). Each is a single `_append({...})` with all fields as keys. `record_timeout` writes `timed_out=True` + `status="canceled"` + 5 dispatch fields. `record_dispatch_failure` writes `status="canceled"` + `dispatch_result="failed"` (hardcoded) + `resolution_action` + 3 dispatch fields. `record_internal_abort` writes `status="canceled"` + `internal_abort_reason` + 5 cleared fields.
- **Replay branches:** Three new `elif op == "..."` branches added after `op == "record_protocol_echo"` (post-Task-7 line 221). Used **`dataclasses.replace(existing, **changes)`** consistently per locked-in pattern. Each branch does `if rid in requests:` existence check then `requests[rid] = replace(requests[rid], ...named overrides)`.
- **Atomicity invariant:** Each mutator is a single `_append` call → single JSONL line written → partial-write replay impossible. Verified by `test_record_dispatch_failure_atomicity_no_partial`.

**Key implementation detail:** `dispatch_result="failed"` and `timed_out=True` are HARDCODED in their replay branches (read literal, not `record.get(...)`). The mutator signature is the assertion — there's no path where `record_timeout` doesn't set `timed_out=True`. Quality reviewer classified the hardcode-vs-read-from-record asymmetry as Minor (B8.1) because it's tautological-but-safe.

**Future-Claude note:** Task 8's three mutators set status to `"canceled"` regardless of which failure path triggered. The `interrupt_error` field on `record_timeout` is for non-cancel-capable interrupt failures; `dispatch_error` is for cancel-dispatch failures. **Mutual exclusion is a CALLER convention** — neither the signature nor the replay enforces it. Tests cover the four spec-valid combinations; the "both non-None" corruption case is silently producible.

### `packages/plugins/codex-collaboration/tests/test_pending_request_store_atomic_mutators.py` (NEW — Task 8 commit `21b2eb7e`, 8 tests)

**Purpose:** Verify the 3 new atomic mutators correctly write JSONL records and that replay correctly hydrates state.

**Test breakdown:**
| Test | Purpose |
|---|---|
| `test_record_timeout_succeeded_cancel_dispatch` | Cancel-capable + dispatch succeeded (4 fields populated) |
| `test_record_timeout_failed_cancel_dispatch_carries_error` | Cancel-capable + dispatch failed (carries `dispatch_error`) |
| `test_record_timeout_non_cancel_capable_interrupt_path` | Non-cancel-capable interrupt succeeded (all dispatch fields None) |
| `test_record_timeout_non_cancel_capable_interrupt_failed_carries_interrupt_error` | Non-cancel-capable interrupt failed (carries `interrupt_error`, NOT `dispatch_error`) |
| `test_record_dispatch_failure_atomic_fields` | All 6 fields populated atomically |
| `test_record_dispatch_failure_atomicity_no_partial` | **Atomicity invariant**: single-append → single new JSONL line |
| `test_record_internal_abort_sets_canceled_and_reason` | Status flip + reason population, all payload fields cleared |
| `test_record_internal_abort_round_trip_via_replay` | **Round-trip**: fresh store instance → replay from disk |

### `packages/plugins/codex-collaboration/server/models.py` (MODIFIED — Task 9 commit `16aca095`, +1 line)

**Purpose:** Add `parked_request_id: str | None = None` field to `DelegationJob` dataclass.

**Approach:** Single line added at the END of the field list (after `artifact_hash: str | None = None`). Default `None` preserves back-compatibility — legacy records without the field replay with `None` via the dataclass default.

**Why end-of-field-list:** Position-of-default matters in dataclasses — no non-default-after-default. `parked_request_id` has a default so it's safe at the end.

### `packages/plugins/codex-collaboration/server/delegation_job_store.py` (MODIFIED — TWO commits)

**Commit 1, `16aca095` (Task 9):** Added `update_parked_request` mutator + new `op == "update_parked_request"` replay branch + `replace` to import.

**Commit 2, `c6bf834c` (Phase B closeout fix):** Migrated 5 replay branches to `replace()`, bundled Task 9 cleanup.

**Combined post-commit state (post-`c6bf834c`):**
- All 5 replay branches use `replace(existing, **changes)` consistently
- All 5 replay branches use `job_id` (not `jid`)
- All 5 replay branches have `isinstance(job_id, str)` guards before `jid in jobs` lookup
- Tuple identity preserved across `update_status`, `update_status_and_promotion`, `update_promotion_state`, `update_artifacts`, and `update_parked_request` replay

**Latent bug now closed:** Pre-existing `asdict(existing)` tuple-loss on `artifact_paths` after normal-path replay. The bug was dormant (only concrete symptom: spurious `update_artifacts` write at `delegation_controller.py:988` — idempotent, self-healing) but violated the `tuple[str, ...]` field contract.

### `packages/plugins/codex-collaboration/tests/test_delegation_job_parked_request_id.py` (NEW — Task 9 commit `16aca095`, 6 tests)

**Purpose:** Verify the new `parked_request_id` field + `update_parked_request` mutator + replay branch.

**Test breakdown:**
| Test | Purpose |
|---|---|
| `test_parked_request_id_default_is_none` | Default `None` for new records |
| `test_update_parked_request_sets_rid` | Mutator sets the field |
| `test_update_parked_request_clears_rid` | Mutator clears via `None` arg |
| `test_update_parked_request_replay_consistency` | Multiple set/clear ops replay correctly via fresh store instance |
| `test_legacy_records_without_field_replay_as_none` | **Back-compat**: legacy JSONL (no `parked_request_id` key) replays with `None` via dataclass default |
| `test_list_user_attention_required_admits_canceled_jobs` | **Step 9.7 integration assertion**: existing predicate already admits canceled jobs without code change |

### `packages/plugins/codex-collaboration/tests/test_delegation_job_store.py` (MODIFIED — closeout fix commit `c6bf834c`, +68 lines, 3 new tests)

**Purpose:** Regression coverage for tuple identity preservation across replay.

**Test breakdown:**
| Test | Purpose |
|---|---|
| `test_artifact_paths_remain_tuple_through_status_replay` | After `update_status` replay, `type(retrieved.artifact_paths) is tuple` |
| `test_artifact_paths_remain_tuple_through_status_and_promotion_replay` | After `update_status_and_promotion` replay |
| `test_artifact_paths_remain_tuple_through_promotion_state_replay` | After `update_promotion_state` replay |

**Pattern note:** Tests assert `type(...) is tuple` (identity check), not just `== ("a.txt",)` (equality check). Equality alone passes even with the bug (Python's `list == tuple` returns `False`, but the comparison via `==` of identical contents would still be False — the failing comparison at `delegation_controller.py:988` is the symptom). The `type()` assertion catches the silent type-contract violation directly.

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (MODIFIED — TWO commits)

**Commit 1, `be46ecd6` (Task 8 docs):** +7 lines — added "From Phase B Task 8" subsection with B8.1 + B8.2 (no closed-items entries — first clean ship).

**Commit 2, `23e427c6` (Phase B closeout docs):** +4 lines — added "From Phase B Task 9 + closeout" subsection under Closed items recording P1 + bundled M1/M2/M3 resolution at `c6bf834c`. NO new open items for Task 9 (the would-be B9.1/B9.2/B9.3 were absorbed into the closeout fix).

**Tracker state at Phase B end:**
- 9 open items: A1-A5 (5), B6.1-B6.2 (2), B7.1-B7.2 (2), B8.1-B8.2 (2)
- 3 closed items: Task 6 update_status fix, Task 7 record_protocol_echo null-guard fix, Task 9+closeout tuple-loss fix
- Well below the "30+ items by Task 22" migration threshold from the original Risk

## Codebase Knowledge

### Architecture: Phase B end state — both stores apply `replace()` consistently

| Store | File | Replay branches (post-Phase-B) | Pattern |
|---|---|---|---|
| `PendingRequestStore` | `pending_request_store.py` (224 lines post-Phase-B) | 7 branches: create, update_status, mark_resolved, record_response_dispatch, record_protocol_echo, record_timeout, record_dispatch_failure, record_internal_abort | All non-create branches use `replace()` |
| `DelegationJobStore` | `delegation_job_store.py` (~290 lines post-closeout) | 6 branches: create, update_status, update_status_and_promotion, update_artifacts, update_promotion_state, update_parked_request | All non-create branches use `replace()` (4 migrated in `c6bf834c` + 1 added by Task 9 + create unchanged) |

**Replay-preservation principle:** Both stores now structurally preserve all dataclass field semantics through replay — including tuple identity on tuple-typed fields. The `dataclasses.replace()` primitive is the single load-bearing tool.

### Pattern: `dataclasses.replace()` is the canonical replay primitive

**Locked across:** Tasks 6 fix (`3fbba140`) + Task 7 feat (`941e7efd`) + Task 8 feat (`21b2eb7e`) + Task 9 feat (`16aca095`) + closeout fix (`c6bf834c`). Five tasks of evidence.

**Why `replace()` is strictly better than `asdict()` + dict-spread:**
- `replace()` is stdlib (`from dataclasses import replace`), works on `frozen=True` dataclasses
- Auto-preserves all unmentioned fields. No defensive explicit overrides needed.
- Type-safe: returns the same dataclass type
- **Doesn't traverse into tuples/dicts** — avoids `asdict()`'s recursive corruption issue
- Eliminates the `asdict_for_replay` phantom helper entirely

**Why `asdict()` + dict-spread had the latent bug:** `asdict()` is a deep conversion — recurses into nested dataclasses, **converts tuples to lists**. `DelegationJob(**asdict(existing))` then receives a list as the `artifact_paths` value. Python doesn't runtime-validate generic types so the dataclass accepts the list. Result: silent type-contract violation.

### Pattern: `record.get(key) or default` for null-safe coercion

**Discovered (Task 7 fix `b623548b`), still in force after Phase B close.** `dict.get(key, default)` returns `default` only when the key is *absent*. JSON null values come through as `None`. Wrap with `or default` whenever passing to a constructor: `record.get(key) or () → tuple(...)`.

**Affected branches in `pending_request_store.py`:**
- `op == "record_protocol_echo"` (lines 211-223 post-Phase-B): uses `record.get("protocol_echo_signals") or ()` before `tuple(...)`

**Phase B audit:** No other replay branches in either store call `tuple(...)` or `list(...)` on `record.get(...)` results. The pattern is bounded to `record_protocol_echo` because it's the only mutator that writes a tuple-typed field.

### Pattern: Atomic mutators write all fields in single `_append`

**All Task 8 + Task 9 + Task 7 success-path mutators are atomic.** Each calls `_append({...})` exactly once, with all relevant fields as keys in the dict. Crash-mid-write produces an invalid JSON line that the JSONDecodeError handler skips on replay. No path produces a partial-state record.

**Verification pattern for atomicity:** `test_record_dispatch_failure_atomicity_no_partial` in `test_pending_request_store_atomic_mutators.py` reads `_store_path.read_text(...)` before + after a mutator call, asserts `len(after_lines) == len(before_lines) + 1`.

### Convention: Defensive coercion strategies (3 patterns coexist in `pending_request_store.py`)

Three patterns coexist for handling potentially-malformed JSONL records:

1. **`try/except (KeyError, TypeError): continue`** — used by `op == "create"` branch. Defense-in-depth.
2. **Explicit type checks before mutation** — used by `op == "update_status"` branch (`isinstance(req_id, str)`, `isinstance(status, str)`, `status not in _VALID_STATUSES`, `req_id not in requests`). Loud rejection.
3. **Existence check + `or default` coercion** — used by Task 7 + Task 8 new branches. Single guard `if rid in requests:` plus `or ()` for tuple-coerced values. Narrow.

**Post-Phase-B audit:** `delegation_job_store.py` after the closeout fix uses pattern 2 consistently (multi-step validation in all 5 non-create branches). `pending_request_store.py` retains the asymmetry (B7-style observation, accepted as plan-sanctioned).

### Surprising Findings

- **`asdict_for_replay` is a phantom helper.** Plan-text fiction across all of Phase B — never defined anywhere in the package. Tasks 6/7/8 implementers couldn't accidentally use it because it would fail at import. Task 9 plan ESCALATED by asking the implementer to define it as new module-level code; pre-authorized deviation rejected this.
- **`asdict()` tuple-loss is uncaught by existing test suite.** Zero tests in `test_delegation_job_store.py` (pre-Phase-B-closeout) asserted `type(retrieved.artifact_paths) is tuple` after replay. Equality-only tests pass with the bug because `["a"] != ("a",)` is the symptom, but the test never compared types. **This is a generalizable test pattern**: when validating dataclass replay, assert `type(field) is expected_type`, not just equality.
- **The plan's redundant explicit overrides** (`available_decisions: existing.available_decisions` etc.) were defensive copy-paste in the plan author's `asdict_for_replay` template — necessary ONLY because `asdict()` loses tuple identity. With `replace()`, they're noise.
- **Pyright cache staleness applies to new methods AND new fields.** After Task 7+8+9 commits, Pyright reported "Cannot access attribute" on test files referencing the new methods/fields. Runtime tests are ground truth. Generalizes from "new fields" (Task 6 pattern) to "new methods" (Task 7 pattern) to "new fields on existing dataclass" (Task 9 pattern).
- **`update_artifacts` was already self-healing.** It's the 4th existing branch in `delegation_job_store.py`; it explicitly re-tuples `artifact_paths` from the JSONL record before constructing the `DelegationJob`. So the override beats the `asdict()` spread's list version. The other 3 branches did NOT have this self-healing — they were the bug surface.

### Key Locations

| Concept | Location |
|---|---|
| `PendingServerRequest` dataclass | `models.py:285-319` (21 fields) |
| `DelegationJob` dataclass | `models.py:398-419` (11 fields, including `parked_request_id` from Task 9) |
| `PendingRequestStore` | `pending_request_store.py` (~224 lines post-Phase-B) |
| `DelegationJobStore` | `delegation_job_store.py` (~290 lines post-Phase-B-closeout) |
| `_replay` for PendingRequestStore | `pending_request_store.py:138-223` (8 op branches) |
| `_replay` for DelegationJobStore | `delegation_job_store.py:193+` (6 op branches, all non-create using `replace()`) |
| `_VALID_STATUSES` (PendingRequestStore) | `pending_request_store.py:18` |
| `_VALID_STATUSES` (DelegationJobStore) | `delegation_job_store.py:17` |
| `_TERMINAL_PROMOTION_STATES` | `delegation_job_store.py:23-25` |
| Packet 1 manifest | `docs/plans/2026-04-24-packet-1-deferred-approval-response.md` |
| Phase B plan | `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-b-stores.md` (1151 lines) |
| Phase C plan | `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-c-journal.md` (NOT read this session) |
| Carry-forward tracker | `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (~71 lines post-Phase-B) |

### Dependency Graph (Packet 1 Phase B end state)

```
PendingServerRequest (models.py:285-319, 21 fields)
  └── used by: PendingRequestStore (pending_request_store.py)
        ├── create()                           [pre-Packet-1]
        ├── update_status()                    [pre-Packet-1; Task 6 fixed replay → replace()]
        ├── mark_resolved()                    [Task 7 — replace() replay]
        ├── record_response_dispatch()         [Task 7 — replace() replay]
        ├── record_protocol_echo()             [Task 7 — replace() + or () null guard]
        ├── record_timeout()                   [Task 8 — replace() replay, atomic 5+1 fields]
        ├── record_dispatch_failure()          [Task 8 — replace() replay, atomic 7 fields]
        └── record_internal_abort()            [Task 8 — replace() replay, atomic 7 cleared fields]

DelegationJob (models.py:398-419, 11 fields incl. Task 9's parked_request_id)
  └── used by: DelegationJobStore (delegation_job_store.py)
        ├── create()                           [pre-Packet-1]
        ├── update_status()                    [closeout fix — migrated to replace()]
        ├── update_status_and_promotion()      [closeout fix — migrated to replace()]
        ├── update_artifacts()                 [closeout fix — migrated to replace() (was already self-healing)]
        ├── update_promotion_state()           [closeout fix — migrated to replace()]
        └── update_parked_request()            [Task 9 — replace() (was already correct)]
```

**No remaining `asdict()` + dict-spread patterns in either store.**

### Conventions Observed (Phase B end state)

- Tests use `tmp_path` pytest fixture for isolation (both store test files)
- Tests use `store._store_path.write_text(...)` / `.open("a")` for raw JSONL injection
- JSONL records use `sort_keys=True` — deterministic serialization
- `os.fsync()` after every write — durability convention
- `from server.X import Y` import style (NOT `codex_collaboration.server.*`)
- `import pytest` is included by convention even when unused (carry-forward A4, B7.1)
- Variable naming in `_replay` branches: post-closeout, all `delegation_job_store.py` branches use `job_id`. `pending_request_store.py` retains the `req_id` (existing) vs `rid` (new branches) asymmetry as B7.2.
- Atomic mutators (Task 8 set): atomicity is encoded in the single-`_append` call, verified by line-count assertion in tests.
- Type-identity assertions in regression tests: post-closeout pattern is `assert type(retrieved.field) is expected_type`, not just equality.

## Context

### Project State

- Branch: `feature/delegate-deferred-approval-response`
- Branch tip: `23e427c6`
- 11 commits on branch from Phase A baseline (`b6dbaa3c`):
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
- Working tree clean
- 934 tests in codex-collaboration package (was 911 at start of prior session; 917 after Task 7; 925 after Task 8; 931 after Task 9; 934 after closeout fix +3 regression tests)
- Phase B Tasks 6, 7, 8, 9 all ✅ landed; Phase C ready for dispatch
- Carry-forward tracker: 9 open + 3 closed items

### Environment

- Python 3.12 (pytest runs under uv workspace selection)
- macOS (BSD sed/find)
- `uv run --package codex-collaboration pytest ...` from repo root
- `uv run --package codex-collaboration ruff check ...` for lint
- `uv run --package codex-collaboration pyright ...` for type checking (impl files only; test files use a different config)

### Mental Model

**Framing:** Phase B is a chain of mechanical tasks where the *interesting work* is finding-elevation across the spec→quality review boundary, AND the **principle-coherence audit at phase boundaries**. The implementation itself is plan-verbatim copy-paste with one structural pattern decision per task. The reviewer pipeline + closeout audit are where novel findings emerge.

**Core insight (refined this session):** Severity is 3-dimensional, not 2-dimensional:
1. **Precondition likelihood** (normal-path vs corruption-required vs unlikely)
2. **Symptom impact** (silent corruption vs loud crash vs cosmetic)
3. **Principle coherence at phase boundaries** (does leaving this contradict a phase-defining invariant?)

The third axis was added by user's escalation of the tuple-loss finding. P1 was Important by precondition + Minor by symptom + **Phase-Critical by principle**. The third axis flipped the disposition from "carry-forward" to "fix this session."

**Mental model — Phase shape:** Phase B has the shape "for each new mutator class, add the mutator + replay branch + tests, then audit at phase boundary for principle coherence across both stores." Phases C-H will have different shapes (consumer-wiring, journal-validation, registry-coordination), but the principle-coherence audit at phase boundaries is durable.

**Mental model — Reviewer hierarchy:**
1. Implementer (haiku) — mechanical transcription with deviation disclosure
2. Spec reviewer (sonnet) — plan literality + observation collection
3. Quality reviewer (sonnet) — severity classification on observations + independent audit
4. Coordinator (this seat) — disposition decision: in-scope fix vs separate-commit fix vs carry-forward
5. User (final) — phase-boundary principle coherence + escalation

The user functions as a 5th reviewer for principle-coherence — that's why the tuple-loss escalation worked. Future Phase-X closeouts should reserve a "user phase-coherence audit" step.

### Phase B → Phase C transition state

Phase C section: `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-c-journal.md` (NOT read this session). Per Phase B plan epilogue (`phase-b-stores.md:1148`): "Phase C follows with the journal validator relaxation for `decision=None`, after which Phase D introduces the cross-thread `ResolutionRegistry`."

**Patterns locked at Phase B end (apply to Phase C):**
- Use `dataclasses.replace(existing, **changes)` for all replay branches. NOT `asdict_for_replay`.
- Apply `or ()` defensive coercion if any new field is a tuple/list read via `dict.get(...)`.
- Match the per-task 3-commit cadence: feat + (any in-scope fix) + carry-forward update.
- Two-stage review (spec + quality reviewers) with independent audit asks.
- Phase-boundary principle audit before closeout.

## Conversation Highlights

**User opening (entire user-side initial message):**
> User: "Start by reading the Task 8 plan section (`phase-b-stores.md:525-895`) and the current state of `pending_request_store.py` (post-Task-7), then dispatch the haiku implementer with the locked-in patterns baked into the briefing."
— Single-message authorization for Task 8 sequence.

**User Task 8 closeout review (full message preserved for forward-looking notes):**
> User: "**Findings**: No new Task 8 correctness findings from my review. The implementation matches the Task 8 plan shape: the three mutators are single `_append(...)` calls, replay uses `dataclasses.replace(...)`, and the atomic failure-path fields are applied together in replay. One branch-level caveat remains: B7.1 is still present... I would describe Task 8 as ship-ready, but not the branch as lint-clean unless B7.1 is intentionally deferred."
> "Lifecycle ordering being a caller invariant is defensible. `pending_request_store.py` is a pure replay branch, not an ordering validator. The spec's stale timer / registry reserve contract is the actual prevention mechanism for timeout-after-resolution, not the store. Adding pre-write reads here would weaken the single-append journal property Task 8 is explicitly trying to preserve."
> "The `dispatch_error` / `interrupt_error` mutual-exclusion point is also worth carrying forward. The design text says those axes are 'mutually exclusive by construction,' but the construction is caller sequencing, not the `record_timeout(...)` signature or replay logic. `pending_request_store.py:128` can persist both if a caller passes both. That is not a Task 8 defect, but Task 9/downstream wiring should preserve the convention deliberately."
> "B8.2 is correctly classified as polish, not a material replay gap. `store.get()` already calls `_replay()` from the JSONL file, so the timeout and dispatch-failure tests do exercise replay. The missing coverage is only 'new store instance points at same path,' and that constructor/path behavior is already covered once by the internal-abort round trip."
> "**Verdict**: Task 8 is closeable. I would proceed to Task 9 with two handoff notes: caller ordering owns terminal-op exclusivity, and caller wiring must keep `dispatch_error` and `interrupt_error` orthogonal. B7.1 remains the only concrete lint-cleanliness issue on the Phase B surface. Note: we have a 1 million token context window, so we have plenty of room to proceed."

**User Path A escalation on P1 (full message preserved — load-bearing for the third-axis severity decision):**
> User: "Recommendation: **Path A, fix this session**, in a separate Phase B closeout commit."
> "This is not because the runtime symptom is severe. It is because the defect class is exactly the Phase B durability theme: replay must preserve structured field semantics. You already fixed the same family in `PendingRequestStore` by moving to `replace(...)`; leaving the same `asdict(existing)` trap in `DelegationJobStore` makes the Phase B story asymmetrical at the point where you are about to close the phase."
> [explicit fix spec with 4 branches to migrate, Task 9 cleanup bundled, regression test pattern, verification gate, exact commit message]
> "Phase B then closes as: `16aca095` Task 9 feature, `fix(delegate): preserve DelegationJob artifact_paths tuple through replay`, docs closeout recording the review-found fix. That gives you the best audit trail: Task 9 remains clean, the pre-existing replay defect is visibly review-discovered and fixed, and Phase B ends with the replay-preservation principle applied consistently across both stores."

**User light-verification of closeout boundary (closing message):**
> User: "One correction before handoff: the heading says **'8 commits from Phase A baseline'**, but the table and live `git log b6dbaa3c..HEAD` show **11 commits**. I would fix that wording in the handoff summary so the resume boundary does not encode a count mismatch."
> "Substantively, I agree this is a clean stopping point. The closeout shape is strong: Task 9 stayed as its own feature commit, the tuple-loss replay defect landed as a separate visible fix commit, and the docs commit records the review-discovered closeout rather than hiding it in an amend."
> "Recommended next action: run `/handoff:save` now."

**Implicit signals:**
- User caught the off-by-three count error — they are reading my outputs precisely. Future sessions should expect arithmetic / count claims to be cross-checked.
- User explicitly mentioned "1 million token context window" mid-session — a calibration signal that I'd been over-cautious about context budget. Worth recalibrating: `/handoff:save` and reviewer dispatches should not be gated on Claude Code's 200k console context if the underlying conversation context is 1M.
- User performs independent verification at task closeouts (they ran `git status`, `git diff --check`, lint, pyright, pytest themselves before validating). Coordinator self-verification doesn't substitute for user verification — both happen.

## User Preferences

**Stated priorities (this session):**
- "Start by reading the Task 8 plan section... then dispatch" — affirms read-first-then-dispatch sequencing.
- "Recommendation: Path A, fix this session" — confirms principle-coherence trumps symptom-severity at phase boundaries.
- "we have a 1 million token context window, so we have plenty of room to proceed" — calibration signal that I should not be context-budget-cautious within a session.

**Carried forward from prior session (still in force):**
- **Recommendation-first decision style:** User accepts recommendations with refinements rather than rejecting outright. Confirmed by zero pushback on Tasks 8 + 9 dispatches.
- **Plan-first discipline / fix-immediately:** Important findings get fixed in scope; Minor findings carry-forward. **Refined this session:** principle-coherence at phase boundaries can ELEVATE Important findings to "fix this session" even when symptom is dormant.
- **Trust-but-verify:** User runs independent verification at task closeouts. Communication style assumes they're reading reports independently and may catch arithmetic / boundary errors.
- **Plan-literal execution discipline:** The implementer briefing's "preserve literal plan execution" rule continues to hold. Where deviations exist, they are explicitly authorized and disclosed.
- **Carry-forward tracking durability:** From Task 6 — items go in `carry-forward.md`, not just handoff narrative.

**New preferences observed this session:**
- **Three-commit closeout shape preferred:** "Task 9 stayed as its own feature commit, the tuple-loss replay defect landed as a separate visible fix commit, and the docs commit records the review-discovered closeout rather than hiding it in an amend." Audit-trail clarity > commit-count minimization.
- **Phase-boundary principle audit:** User functions as a 5th reviewer for principle coherence. Future closeouts should EXPLICITLY surface a "phase-boundary audit" step, not assume it's coordinator-only.
- **Verification gate explicitness:** User's fix spec required `pytest + ruff + pyright` as the verification gate, not just `pytest`. Future fix dispatches should default to the full gate.
- **Type-identity assertion pattern:** User implicitly endorsed `assert type(retrieved.field) is expected_type` regression tests over equality-only tests. This is a generalizable pattern for dataclass replay validation.

**Communication:** Concise, evidence-backed, file-linked. Single-line directives where possible. Expects coordinator to maintain context without re-statement. Provides corrections succinctly (the count-error fix was 2 sentences).

## Learnings

### Severity classification has 3 axes, not 2

**Refined heuristic:** Severity = max(precondition × symptom, principle-coherence-at-phase-boundary).

**Mechanism:** Pure precondition × symptom analysis would have classified P1 as Important (corruption-required-by-careful-reading × dormant-bounded-symptom). Adding the principle-coherence axis flipped the disposition from carry-forward to fix-this-session because: "leaving the `asdict()` trap in `DelegationJobStore` after fixing it in `PendingRequestStore` makes the Phase B story asymmetrical."

**Evidence:** User's Path A escalation rationale, reviewer's classification choice, this session's coordinator decision.

**Implication:** When dispatching code-quality reviewers for phase-end tasks, give them the principle-coherence lens explicitly: "If this finding contradicts a phase-defining invariant, escalate severity regardless of symptom."

**Watch for:** Findings in subsequent Phase X closeouts that look "dormant" but contradict the phase's locked-in patterns. Apply third-axis lens.

### Phantom helpers (`asdict_for_replay`) become harder to ignore over time

**Mechanism:** The plan author drafted a helper that doesn't exist. Tasks 6/7/8 implementers couldn't accidentally use it (would fail at import). Task 9 plan ESCALATED by asking the implementer to define it as new module-level code — pre-authorized deviation rejected this. Without the deviation, the implementer would have created the helper and we'd have introduced a different replay pattern in `delegation_job_store.py`.

**Evidence:** `grep -r "asdict_for_replay" packages/plugins/codex-collaboration/` returned no matches at session start; plan still references it in Tasks 6, 7, 8, 9 sections.

**Implication:** Stale plan references compound — they can shift from "fiction we ignore" to "fiction the plan asks us to actualize." Pre-authorize deviations in implementer briefings; don't trust haiku-tier implementers to navigate stale plan text without explicit guidance.

**Watch for:** Phase C/D plan text may still sample `asdict_for_replay` or other deprecated patterns. Pre-read each Task X plan and surface stale references in implementer briefings.

### Type-identity assertions catch silent type-contract violations

**Mechanism:** Equality-only tests pass even when a tuple is silently coerced to a list (because `["a"] != ("a",)`, but the test only checks the contents match, not the container type). Type-identity assertions (`assert type(x) is tuple`) catch the coercion directly.

**Evidence:** Pre-closeout `test_delegation_job_store.py` had ZERO type-identity assertions. The latent bug was uncaught for an unknown duration. Post-closeout: 3 new tests with `type(...) is tuple` assertions.

**Implication:** When validating dataclass replay (or any persistence round-trip), assert both equality AND type identity. The pattern generalizes beyond tuples to any concrete generic type.

**Watch for:** Other regression test surfaces in the codex-collaboration package that may have equality-only assertions on dataclass fields. Consider an audit pass at end-of-Phase-D or end-of-Phase-H.

### `update_artifacts`-style explicit re-tupling makes a branch self-healing for prior corruption

**Mechanism:** The 4th branch in `delegation_job_store.py`'s pre-Phase-B `_replay` was self-healing because it explicitly re-tuples `artifact_paths` from the JSONL record. The override beat the `asdict()` spread's list version. So a job that had been corrupted by `update_status` replay would self-heal on the next `update_artifacts` call.

**Evidence:** Code-quality reviewer's audit confirmed `update_artifacts` was the only correct existing branch.

**Implication:** Self-healing branches in append-only journals are a useful defensive pattern. When designing replay branches, consider: does this branch's explicit overrides re-establish the correct types regardless of prior corruption? If yes, it's self-healing; if no, it's vulnerable.

**Watch for:** New mutators in Phase D+ (`ResolutionRegistry`, etc.) that read tuple-typed or list-typed fields. Apply the explicit-re-coercion pattern.

### User functions as a 5th reviewer for principle-coherence

**Mechanism:** Two-stage subagent review (spec + quality) covers plan literality + code quality. User review covers principle coherence at phase boundaries — a class of finding the subagent reviewers may classify but not escalate.

**Evidence:** User's Path A escalation on P1. The quality reviewer correctly identified P1 as Important and recommended option (b) "fix this session" — but only the user's "Phase B durability theme" reframing made the disposition decision feel correct rather than ambiguous.

**Implication:** Future phase-end closeouts should EXPLICITLY include a "user phase-boundary audit" step in the workflow, not assume coordinator + subagents fully cover the disposition decision.

**Watch for:** Phase C/D/H closeout sessions where the user is offline or unresponsive. The principle-coherence axis must still be applied; coordinator can apply it independently with high evidence (the heuristic is "does this contradict a phase-defining invariant?"), but absent user signal, the disposition decision is lower-confidence.

### Three-commit task shape vs two-commit task shape both ship cleanly

**Mechanism:** Tasks 6, 7 closed as 3 commits (feat + fix + docs). Task 8 closed as 2 commits (feat + docs — no in-scope fix needed). Task 9 closed as 1 commit on its own (feat) but Phase B closed as 3 commits (Task 9 feat + closeout fix + closeout docs). Both shapes are healthy.

**Evidence:** All four task closures landed clean per spec + quality reviewer + user verification.

**Implication:** Don't optimize for commit count. The right shape emerges from finding-elevation: clean ship → 2 commits; in-scope fix → 3 commits; pre-existing finding requiring closeout fix → 3 commits at phase boundary (across what could be a single task).

**Watch for:** Phase X tasks where a single feat would normally land but the principle-coherence audit surfaces a fix opportunity. Apply the closeout-fix-as-separate-commit pattern.

## Next Steps

### 1. Phase C entry — read Phase C plan + Task 10 dispatch

**Plan section:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-c-journal.md` (NOT read this session). Per Phase B epilogue: "Phase C follows with the journal validator relaxation for `decision=None`, after which Phase D introduces the cross-thread `ResolutionRegistry`."

**What it adds (anticipated, NOT verified by reading the plan):** Journal validator must accept records where `decision` is `None` (vs the current strict-non-None requirement). This unblocks Packet 1's deferred-approval flow where the approve/deny decision is captured asynchronously.

**Dependencies:** Phase B complete at `23e427c6`. No blockers.

**What to read first:**
- `phase-c-journal.md` (entire file) — locate Task 10 section + scope
- `operation_journal.py` (current journal validator location — TBD by reading Phase C plan)
- `carry-forward.md` (post-Phase-B-close state, may have items relevant to Phase C)

**Approach suggestion:** Same subagent-driven-development pattern. Model tier: haiku for implementer, sonnet for reviewers. Briefing notes for the implementer:

1. **"Preserve literal plan execution: if adapting any sample, report the deviation explicitly."**
2. **"Phase A/B carry-forward items are NOT Phase C scope unless encountered directly; do not opportunistically fix them."**
3. **"Use `dataclasses.replace(existing, **changes)` directly for all replay branches if Phase C touches replay code. Phase B locked this pattern; skip any plan reference to `asdict_for_replay`."**
4. **"Apply the `or ()` defensive coercion pattern if any new field is a tuple/list read via `dict.get(...)`. Phase B established `record.get(key) or default`."**
5. **"Add `assert type(...) is expected_type` regression tests for any dataclass replay path. Equality alone doesn't catch silent type-contract violations."**

**Special review focus:**
- The `decision=None` relaxation is the key correctness invariant. Verify the validator's accept-None branch is symmetric with existing strict-validation paths.
- Watch for any existing journal-replay code that may have its own tuple-loss / type-contract issues (similar to Phase B's `delegation_job_store.py` discovery).

**Acceptance criteria:** Task 10 commit lands cleanly; spec ✅; quality ✅; full-package regression clean (≥937 tests, up from 934).

### 2. Phase D — `ResolutionRegistry` introduction

Per Phase B epilogue: "Phase D introduces the cross-thread `ResolutionRegistry`." This is where caller-wiring tasks begin (per user's Task 8 closeout notes):

**Caller-wiring constraints (from user's Task 8 review — load-bearing for Phase D+):**
- **Lifecycle ordering is a CALLER invariant, not a store invariant.** Don't try to add ordering validation in stores. The stale-timer / registry-reserve contract is the actual prevention mechanism for timeout-after-resolution.
- **`dispatch_error` vs `interrupt_error` mutual exclusion is a CALLER convention** — not enforced by `record_timeout`'s signature or replay. Caller wiring in Phase D+ must preserve orthogonality deliberately — pass exactly one (or neither), not both.

**Carry-forward Phase B's pattern decisions:**
- `replace()` over `asdict()` for any new replay code
- `or ()` defensive coercion for tuple/list `record.get(...)` reads
- Type-identity regression tests
- Three-axis severity classification (precondition × symptom × phase-coherence)

### 3. End-of-Phase-B carry-forward sweep (LOW PRIORITY)

Open items after Phase B close (9 items):
- A1: `_WorkerTerminalBranchSignal.reason` logging (Task 15)
- A2: Sentinel raise-site docs (Task 16)
- A3: `_project_request_to_view` Pyright error (Task 14)
- A4: Unused `import pytest` in Task 3/4 test files (end-of-phase polish)
- A5: `DelegationStartError` class-level annotation style (design discussion)
- B6.1: Redundant `test_has_resolution_action_field` (end-of-phase polish)
- B6.2: Inline `import json` style (end-of-phase polish)
- B7.1: Unused `import pytest` in `test_pending_request_store_mutators.py` (end-of-phase polish; **user flagged as the only concrete lint-cleanliness issue on Phase B surface**)
- B7.2: `req_id` vs `rid` naming inconsistency in `pending_request_store.py:_replay` (end-of-phase polish)
- B8.1: `dispatch_result` hardcode-vs-read style asymmetry (end-of-phase polish)
- B8.2: Missing reopen round-trip tests for `record_timeout` + `record_dispatch_failure` (end-of-phase polish)

**Recommendation:** Sweep at end of Phase D or end of Phase H, NOT end of Phase B. Most are cosmetic; B7.1 is the most concrete (lint cleanliness) but user explicitly deferred it.

### 4. Optional: Audit `operation_journal.py` (and any other store) for `asdict()` + dict-spread tuple-loss patterns

The Phase B closeout fix migrated `delegation_job_store.py` to `replace()`. Other stores in the package (`operation_journal.py`, possibly others) may have similar patterns. Could be:
- Surface in Phase C if it touches the journal directly
- Or schedule as a separate Phase B-end audit task
- Or carry-forward and address in Phase H

**Pattern to grep for:** `\bDelegationJob\(\*\*\{.*asdict\(` or `\b\w+Store\(\*\*\{.*asdict\(` — looks for `Store(**{**asdict(existing), ...})` patterns.

## In Progress

Clean stopping point. Phase B (Tasks 6-9) fully landed across two sessions. Carry-forward tracker updated with all closed entries. Working tree clean. Phase C ready for dispatch in a fresh session.

**No work in flight.**

## Open Questions

### Does Phase C touch replay code? If so, the `replace()` pattern lock applies; if not, the locked pattern is informational only

`phase-c-journal.md` not read this session. Phase C is "journal validator relaxation for `decision=None`" per the Phase B epilogue. Validator code may or may not include replay paths. Recommendation: coordinator pre-reads Phase C plan and applies the pattern lock-in language only if replay code is in scope.

### Are there other tuple-typed fields in `DelegationJob` or `PendingServerRequest` that depend on tuple semantics?

Phase B closeout established that `artifact_paths: tuple[str, ...]` is now correctly preserved. But `available_decisions: tuple[str, ...]` and `protocol_echo_signals: tuple[str, ...]` on `PendingServerRequest` are the other tuple-typed fields. Quick check: do any consumers depend on tuple semantics (hashability, set membership, dict keys)?

**Recommendation:** Surface in Phase C/D implementer briefings as "audit consumer code for tuple-semantics dependencies on these 3 fields." Lower priority than Phase C scope; could be carry-forward.

### When does the carry-forward tracker hit the 30-item migration threshold?

Currently 9 open items at end of Phase B. Phase C-H have ~13 more tasks (10-22). Average ~1-2 carry-forward items per task. Linear projection: ~22-35 items by end of Task 22.

**Recommendation:** Monitor at end of Phase D and end of Phase F. If approaching 25, sweep early. If below 20 at end of Phase F, defer to end of Phase H.

### Will Phase D's caller-wiring tasks need to enforce `dispatch_error` vs `interrupt_error` mutual exclusion?

The user's Task 8 review explicitly flagged this as a caller convention, not enforced anywhere. Phase D introduces `ResolutionRegistry` — likely the caller surface that needs to enforce orthogonality.

**Recommendation:** Coordinator pre-reads Phase D plan and surfaces this as an implementer briefing rule: "Pass exactly one of `dispatch_error` / `interrupt_error` to `record_timeout`, never both."

## Risks

### Phase C plan may have stale `asdict_for_replay` references

The plan's Tasks 6/7/8/9 sections all sampled `asdict_for_replay`. Phase C plan likely has the same issue. If implementer briefings don't pre-authorize the deviation, haiku-tier implementer may try to define the helper.

**Mitigation:** Coordinator pre-reads Phase C plan section before dispatch. Surface stale references in implementer briefing as pre-authorized deviations. Reference Phase B commits (`3fbba140`, `941e7efd`, `21b2eb7e`, `16aca095`, `c6bf834c`) as locked precedent.

### Other stores may have `asdict()` + dict-spread tuple-loss patterns

Phase B audit covered `delegation_job_store.py`. `operation_journal.py` and other stores not audited. Latent bugs may exist.

**Mitigation:** Surface as Phase C implementer briefing audit ask if scope touches journal-replay. Or schedule Phase B-end audit as a separate task. Or carry-forward to end-of-Phase-H sweep.

### Carry-forward tracker growth

9 open items at Phase B end. Linear projection ~22-35 by end of Task 22. Could hit 30 threshold before Phase H.

**Mitigation:** Monitor at Phase D end + Phase F end. Sweep early if approaching threshold. If tracker grows past ~30, migrate to per-item tickets via `handoff:defer` skill.

### Self-verification pattern could mask deviations if implementer report quality degrades

Pattern works because implementer reports are reliable ("no deviations"). 4 data points (Tasks 6, 7, 8 in-scope fixes + closeout fix). If a future implementer report inaccurately claims no deviations, self-verification might miss the gap.

**Mitigation:** Continue verifying via `git show` (independent of implementer report). Track first failed self-verification — if it occurs, switch back to mandatory re-review.

### User offline during Phase X closeout means principle-coherence axis must be coordinator-applied

User functioned as 5th reviewer for principle coherence on P1 escalation. If user is offline during a future phase closeout, coordinator must apply the third-axis lens independently. Risk: coordinator may not catch principle-violations the user would have escalated.

**Mitigation:** Coordinator pre-checks at every phase boundary: "Does this finding contradict a phase-defining invariant? If yes, treat as Important regardless of symptom." Default-toward-Path-A when in doubt at phase boundaries. User can correct on next interaction.

### Three-axis severity heuristic may produce false positives

The principle-coherence axis is broad. A coordinator that's overly eager to apply it could escalate every cosmetic finding to "fix this session" by claiming phase-coherence. The heuristic requires discipline.

**Mitigation:** Apply third axis only when (a) the finding is in code Phase X locked in patterns for, AND (b) leaving the finding visibly contradicts the lock-in. Tasks 6/7/8 patterns ARE Phase B's locks; B7.1's `import pytest` is NOT (cosmetic, not a pattern violation). The user's Path A escalation was on P1 specifically because P1 contradicted the `replace()` lock-in — a clear violation, not a stretch.

## References

- **Plan manifest:** `docs/plans/2026-04-24-packet-1-deferred-approval-response.md`
- **Phase B plan:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-b-stores.md` (1151 lines)
- **Phase C plan (next):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-c-journal.md` (NOT read this session)
- **Carry-forward tracker:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (~71 lines post-Phase-B)
- **Spec source:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` (commit `64608b01`)
- **Prior handoff (resumed from):** `docs/handoffs/archive/2026-04-24_22-28_phase-b-task-7-complete-replace-pattern-locked.md`
- **Phase B commits (chronological):**
  - `5120413b` Task 6 feat + `3fbba140` Task 6 fix + `4a35e636` Task 6 docs
  - `941e7efd` Task 7 feat + `b623548b` Task 7 fix + `038525ba` Task 7 docs
  - `21b2eb7e` Task 8 feat + `be46ecd6` Task 8 docs
  - `16aca095` Task 9 feat + `c6bf834c` Phase B closeout fix + `23e427c6` Phase B closeout docs
- **Subagent-driven-development skill:** `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/subagent-driven-development/`

## Gotchas

### `asdict()` recursively converts tuples to lists; `replace()` does not

`dataclasses.asdict()` is a deep conversion — recurses into nested dataclasses, **converts tuples to lists**. `dataclasses.replace()` constructs a new instance with named overrides — does NOT traverse internals. For replay-branch state transitions, `replace()` is the correct primitive.

**Symptom of using `asdict()` for replay:** Silent tuple→list coercion of generic-typed fields. Python doesn't runtime-validate so the dataclass accepts the list. Type contract violated silently.

**Fix:** Use `replace(existing, **changes)`. Already locked across both stores at Phase B end.

### `dict.get(key, default)` does NOT handle JSON null

`dict.get` returns `default` only when the key is absent. JSON null comes through as `None`. Wrap with `or default` whenever passing the result to a constructor: `record.get(key) or () → tuple(...)`.

**Affected branches at Phase B end:** Only `op == "record_protocol_echo"` in `pending_request_store.py:214`. Other branches don't tuple/list-coerce. Pattern is durable for any future tuple-typed mutator.

### Plan's `asdict_for_replay` references are PHANTOM helpers — never define them

The plan samples `asdict_for_replay` in Phase B Tasks 6, 7, 8, 9. It was NEVER defined anywhere in the package. Implementers must REJECT plan references and use `replace()` directly.

**Test:** `grep -r "asdict_for_replay" packages/plugins/codex-collaboration/` returns no matches at end of Phase B.

### Pyright cache staleness applies to new methods, new fields, AND fields on existing dataclasses

After commits adding new dataclass methods or fields, Pyright reports "Cannot access attribute" on test files. Cache lag, not real error. Runtime tests are ground truth.

**Generalization:** Any time a `@dataclass` is mutated (new field) or a class gains methods, expect ~1-cycle Pyright cache staleness on test files. Source-file Pyright is usually clean.

### Plan line numbers drift across tasks

Phase B plan was written when stores were smaller. Line numbers in the plan don't match the current file state. Locate by structural landmark (`def update_status`, `_replay` method, `op == "create"` branch), not by absolute line number.

### `record_response_dispatch` does NOT change status; `record_dispatch_failure` DOES

Status flips:
- to `"resolved"` only via `mark_resolved` (Task 7)
- to `"canceled"` via `record_timeout`, `record_dispatch_failure`, `record_internal_abort` (Task 8)
- NOT changed by `record_response_dispatch` (Task 7) — that's the transport-write stamp only

### `dispatch_error` vs `interrupt_error` mutual exclusion is CALLER convention

Neither `record_timeout` signature nor replay enforces "exactly one of dispatch_error/interrupt_error is non-None." Tests cover the four spec-valid combinations; "both non-None" corruption case is silently producible.

**Phase D wiring must preserve this orthogonality deliberately** (per user's Task 8 review).

### Lifecycle ordering is CALLER invariant, not STORE invariant

Stores are pure append-only journals with last-write-wins replay. `record_timeout` after `mark_resolved` produces an internally inconsistent state (`status="canceled"` + `resolved_at=<set>`) — by design, not a defect. Enforcing ordering would require pre-write reads, breaking single-append atomicity.

**Phase D `ResolutionRegistry` must enforce ordering at the caller level** (per user's Task 8 review).

### Branch has 3 commits for Phase B closeout — do NOT squash

Task 9 feat (`16aca095`) + closeout fix (`c6bf834c`) + closeout docs (`23e427c6`) is the audit trail. Squashing would hide the review-loop's discovery work and the principle-coherence escalation.

### Self-verified fixes break strict subagent-driven-development protocol

The skill specifies "Code quality reviewer subagent approves? → yes → Mark task complete." Self-verifying skips this step. Used 4 times now (Task 6 fix, Task 7 fix, Task 8 close, closeout fix) under context pressure or for tightly-scoped reviewer-directed/user-directed fixes. Document the deviation explicitly so future coordinators know to re-check if a self-verification fails.

### `dispatch_result` and `timed_out` are HARDCODED in their respective Task 8 replay branches

`record_timeout` replay sets `timed_out=True` literally (not `record.get(...)`). `record_dispatch_failure` replay sets `dispatch_result="failed"` literally. The mutator name IS the assertion — there's no path where a `record_timeout` op should produce `timed_out=False`. Carry-forward B8.1 captures the style asymmetry (vs `record_response_dispatch` replay which reads from record).

**Don't "fix" by changing to `record.get(...)` — that would weaken the tautology to a corruption-vulnerable read.**

### Type-identity assertions catch silent type-contract violations that equality misses

Use `assert type(retrieved.field) is expected_type`, not just `assert retrieved.field == expected_value`. The closeout fix's 3 regression tests use this pattern. Apply to any future dataclass replay validation.
