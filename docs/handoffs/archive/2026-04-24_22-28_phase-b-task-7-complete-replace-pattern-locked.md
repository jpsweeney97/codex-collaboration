---
date: 2026-04-24
time: "22:28"
created_at: "2026-04-25T02:28:18Z"
session_id: fcc6a39e-532e-4308-9150-6326a5cd5985
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-24_22-05_task-6-complete-carry-forward-tracker-seeded.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: 038525ba
title: Phase B Task 7 complete (T-20260423-02) — replace() pattern locked; null-corruption guard added; B7.1+B7.2 tracked
type: handoff
files:
  - packages/plugins/codex-collaboration/server/pending_request_store.py
  - packages/plugins/codex-collaboration/tests/test_pending_request_store_mutators.py
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md
---

# Handoff: Phase B Task 7 complete (T-20260423-02) — replace() pattern locked; null-corruption guard added; B7.1+B7.2 tracked

## Goal

**Immediate objective:** Land Phase B Task 7 of Packet 1 (T-20260423-02 deferred-approval response design) — adding three success-path mutators (`mark_resolved`, `record_response_dispatch`, `record_protocol_echo`) plus three new `_replay` op branches plus a `Literal` import to `PendingRequestStore`. Ship through two-stage review (spec + code quality), apply any in-scope review findings, and seed the carry-forward tracker with new Minor items.

**Trigger:** This session resumed from `2026-04-24_22-05_task-6-complete-carry-forward-tracker-seeded.md` after Task 6 landed three commits (feat + fix + tracker doc). The prior handoff explicitly directed: "Dispatch Phase B Task 7: PendingRequestStore success-path mutators... Approach suggestion: Same subagent-driven-development pattern. Model tier: haiku for implementer, sonnet for reviewers." User opened the session with: "Yes, start by reading the Task 7 plan section and then dispatching."

**Stakes:** Task 7 is the success-path half of Phase B's mutator set (Task 8 is the failure-path half). Without Task 7 landing cleanly, Task 8 cannot dispatch. Task 7 also tested whether the `dataclasses.replace()` precedent established by Task 6's fix at `3fbba140` could be carried forward as a Phase B-wide pattern, replacing the plan's sampled `asdict_for_replay` helper. The pattern decision affects Tasks 8 + 9 (both currently sample the helper).

**Bigger picture:** Packet 1 converts `_finalize_turn`'s captured-request branch from synchronous-decide kind-based escalation to async-decide worker-owned resolution. The 11 new fields on `PendingServerRequest` (Task 6) capture the deferred-resolution lifecycle. Tasks 7-9 add the store-layer mutators that write those fields. Tasks 10+ wire consumers, projection, journal, and ResolutionRegistry.

**Why now:** Plan-execute discipline. Prior session set the stage; this session executed Task 7 in a fresh session.

**Success criteria:**
- Task 7 committed with spec ✅ and quality ✅ reviewer approval ✅ (achieved)
- Any reviewer-flagged Important+ issues fixed before Task 7 closes ✅ (I-1 fixed in scope)
- Branch state ready for Task 8 dispatch in a fresh session ✅
- Carry-forward tracker updated with new Minor findings ✅ (B7.1 + B7.2)
- Full-package regression clean ✅ (917 tests pass, up 6 from 911)

**Connection to project arc:** Phase B has 4 tasks (6-9). Task 6 ✅ landed. Task 7 ✅ landed this session. Tasks 8 (failure-path mutators) + 9 (DelegationJob.parked_request_id) remain. Phases C-H follow.

## Session Narrative

**Starting state (session open):** Loaded the Task-6-complete handoff. Branch was `feature/delegate-deferred-approval-response` at `4a35e636` (the carry-forward tracker docs commit). Working tree clean. 911 tests passing in the codex-collaboration package. Phase B Task 7 ready for dispatch. Three open questions from the prior handoff — most importantly whether to use `replace()` (Task 6 precedent) or `asdict_for_replay` (plan sample) for Task 7's three new replay branches.

**Read-first discipline:** Per user's opening message ("start by reading the Task 7 plan section and then dispatching"), I read in parallel:
- `phase-b-stores.md:239-524` (Task 7 section, 286 lines including step 7.1-7.6)
- `pending_request_store.py` post-Task-6 state (137 lines)
- `carry-forward.md` (50 lines)
- Located plan section boundaries via `grep -n "^## Task " phase-b-stores.md`

**Pre-dispatch analysis (the interesting work):** Three observations crystallized:

1. **The `asdict_for_replay` helper exists in the plan to work around a problem `replace()` doesn't have.** The helper's docstring justifies its existence with: "since `dataclasses.asdict` would conflict with the custom tuple/dict types if we use it naively". This is true for `asdict()` (which recursively converts tuples → lists, dataclasses → dicts), but **`replace()` doesn't go near those internals** — it just constructs a new instance with named overrides. The helper is a workaround for a tool we don't need to use.

2. **The plan's replay branches contain redundant explicit overrides.** For example, `phase-b-stores.md:443-446` includes `"available_decisions": existing.available_decisions, "protocol_echo_signals": existing.protocol_echo_signals, "requested_scope": existing.requested_scope` even though those fields are already in the `**asdict_for_replay(existing)` spread. With `replace()`, no defensive overrides needed: unmentioned fields auto-preserve.

3. **Task 7 is bigger than Task 6 (3 mutators + 3 replay branches vs 11 fields + 1 branch), but each unit is mechanical.** Haiku is still appropriate for the implementer; the interesting decision is the pattern choice, which goes in the briefing.

**Implementer dispatch (haiku, subagent):** Briefing included full Task 7 plan text + scene-setting (commits `b6dbaa3c` → `5120413b` → `3fbba140` → `4a35e636`) + 9 hard rules + 3 special-attention areas + an explicit "Option A vs Option B" critical decision section. Option A: use `replace()` directly (matches Task 6 precedent, ~5 lines per branch). Option B: implement the plan's `asdict_for_replay` helper verbatim. The briefing required the implementer to choose and justify.

**Implementer report (DONE at commit `941e7efd`):** Implementer chose **Option A** with this justification: "`replace()` is already imported, established as precedent in Task 6's `update_status` branch, and functionally equivalent to the plan's pattern while avoiding unnecessary helper abstraction." Five new tests + 7 existing store tests = 12 PASS. Two files changed (store.py + new test file). No deviations from plan beyond the authorized Option A choice.

**First pivot — Pyright diagnostic stream post-implementation:** Post-commit, 8 "unknown attribute" Pyright errors appeared on the new test file's mutator calls (`mark_resolved`, `record_response_dispatch`, `record_protocol_echo`), plus the recurring "import pytest could not be resolved / not accessed" pair. Triaged per Task 6's "Pyright cache vs runtime" learning: cache staleness on new attributes, runtime tests are ground truth. The unused `import pytest` matches Phase A carry-forward A4 pattern. Decision: do not block dispatch on these.

**Spec compliance review (sonnet, subagent):** BASE_SHA=`4a35e636`, HEAD_SHA=`941e7efd`. Reviewer verified independently via `git show 941e7efd`, ran `pytest`, compared signatures + bodies + commit message + file count line-by-line against `phase-b-stores.md:239-523`.

**Spec reviewer verdict (✅ Compliant — 8/8 checklist):** All three mutator signatures match plan verbatim, bodies match (including the "succeeded" hardcode and `list(signals)` write-time conversion), Literal import added, test file matches plan verbatim, 12 tests pass, commit message verbatim, exactly 2 files in commit. **Reviewer's notable validation of Option A:** "the deviation is not just equivalent; it is strictly better. `replace()` is type-safe, requires no intermediate dict allocation, and preserves field types without manual reconstruction. The plan's pattern included explicit redundant overrides... precisely because `asdict()` loses tuple identity and dict identity — `replace()` sidesteps this entirely."

**Out-of-scope observations from spec reviewer (3):**
- Guard asymmetry: `update_status` branch has 3 guards (type check, validity check, existence check); the 3 new branches have only 1 (existence check via `if rid in requests:`).
- Unused `import pytest` (matches A4).
- Pyright cache staleness on new test file.

**Code quality review dispatch (sonnet, subagent):** Included full diff context + the spec reviewer's three out-of-scope observations as input + Task 6's precedent framing for severity classification. Reviewer verified each finding with file:line evidence, ran tests, and produced a structured verdict.

**Second pivot — Important finding from quality reviewer:** Reviewer found I-1: `tuple(None)` in `record_protocol_echo` replay branch crashes all store reads on JSONL corruption. Reasoning (evidence-backed):

The `_replay` branch calls `tuple(record.get("protocol_echo_signals", ()))`. `dict.get(key, default)` only returns `default` when the key is *absent* — if the JSONL record has `"protocol_echo_signals": null` (realistic corruption: partial flush, hand-edit, external writer), `record.get("protocol_echo_signals", ())` returns `None`. Then `tuple(None)` raises `TypeError`. This exception is uncaught in the new branch (vs the `op == "create"` branch which has `try/except (KeyError, TypeError): continue` protection). The exception propagates through `_replay()` and crashes every read API — `get`, `list_pending`, `list_by_collaboration_id`. Worse than Task 6's "silent drop" pattern: this is total store unavailability, not field zeroing.

**Reviewer's recommended fix (verbatim):** Use `or ()` rather than broader `try/except`. Narrow fix, specific to the realistic corruption case, doesn't paper over other defect classes:

```python
raw_signals = record.get("protocol_echo_signals") or ()
requests[rid] = replace(
    requests[rid],
    protocol_echo_signals=tuple(raw_signals),
    ...
)
```

**Reviewer's classification:** Important (not Critical). Reasoning: precondition requires JSONL corruption (not normal-path), failure mode is loud (crash) not silent (corruption), plan-sanctioned pattern that the implementer faithfully followed.

**Severity classification decision:** Reviewer's call. I accepted Important rather than upgrading to Critical because:
- Task 6 precedent: Critical was for normal-path data flow defects (Tasks 7-8 mutators would have hit the `update_status` defect on every call). Task 7's I-1 requires data corruption to manifest.
- Phase A protocol: Important findings get fixed immediately but don't block. This matches the discipline.

**Decision to dispatch fix without pausing for user alignment:** Per Phase A protocol "Important findings get fixed immediately" + user's prior alignment with fix-immediately approach for Task 6's `update_status`. Surfaced classification + dispatch decision in chat for transparency. Did not pause for explicit user OK because momentum + context cost outweighed alignment risk for a 1-line fix with reviewer-directed verbatim recommendation.

**Fix dispatch (haiku, subagent):** Tight scope. Briefing included reviewer's `before → after` diff verbatim + a regression test (null-injection JSONL corruption case) + scope lock on two files + the standard 6 hard rules.

**Fix implementer report (DONE at commit `b623548b`):** Diff matched directive verbatim. Three-line code change in `pending_request_store.py:213-217` (extract `raw_signals = record.get(...) or ()`, pass to `tuple(raw_signals)`). New test `test_record_protocol_echo_replay_handles_null_signals` injects a corrupted JSONL record with `"protocol_echo_signals": null`, reopens the store, asserts the request is preserved with `protocol_echo_signals == ()` and no crash. Six mutator + 7 existing store = 13 PASS. No deviations.

**Self-verification of fix (controller, not subagent):** Per Task 6 precedent under context pressure, I verified directly:
- `git show b623548b` — confirmed diff matches reviewer directive verbatim.
- `git show b623548b --stat` — confirmed exactly 2 files (5 line changes in store + 27 line additions in test).
- `git log --oneline -3` — confirmed branch has feat → fix progression, no amend or squash.
- Full-package regression: `uv run --package codex-collaboration pytest packages/plugins/codex-collaboration/ -q` → **917 passed in 19.89s** (up 6 from Task 6's 911).

**Carry-forward update + closeout commit:** Edited `carry-forward.md` to add B7.1 (unused `import pytest`) and B7.2 (`req_id` vs `rid` variable naming) under "From Phase B Task 7" subsection, plus a new closed-items entry for the resolved I-1 with commit SHA `b623548b`. Committed at `038525ba` with message `docs(delegate): record Task 7 carry-forward items B7.1 + B7.2 (T-20260423-02)`.

**Decision to handoff:** Task 7 fully landed in 3 commits (matching Task 6's pattern: feat + fix + docs). Context ~70-75%, sufficient headroom but Task 8 dispatch would consume meaningfully. Pattern alignment with Task 6's session-per-task cadence. User signaled `/save`.

## Decisions

### Surface the `replace()` vs `asdict_for_replay` choice to the implementer rather than pre-deciding

**Decision:** The Task 7 implementer briefing included an explicit "CRITICAL DECISION POINT" section requiring the implementer to choose between Option A (`replace()` direct) and Option B (`asdict_for_replay` helper) and justify the choice in the final report.

**Driver:** Prior handoff (`2026-04-24_22-05_task-6-complete-carry-forward-tracker-seeded.md` Section "Next Steps", item 1) explicitly recommended: "**New — surface this to implementer:** 'The plan samples `asdict_for_replay(existing)` helper. Task 6's `update_status` fix used `dataclasses.replace()` instead. Before adding `asdict_for_replay`, evaluate whether `replace(existing, **changes)` is cleaner. Report your evaluation.'"

**Rejected:** Pre-decide for the implementer (direct briefing toward Option A). Would have been faster but bypasses the implementer's evaluation step. The prior handoff explicitly chose the surface-don't-pre-decide path.

**Implication:** Establishes a coordinator pattern: when a non-obvious pattern decision exists between a plan sample and an established precedent, surface as decision point in the implementer briefing with both options spelled out. The implementer's choice + justification becomes a first-class artifact reviewers can validate.

**Trade-offs:** Briefing was longer (~50 extra lines). Implementer had to evaluate before implementing (~marginal time cost). Risk that haiku-tier implementer would default to "follow plan literally" — mitigated by explicit framing that BOTH options are authorized.

**Confidence:** High (E2) — prior handoff recommended it explicitly, and the project tenets ("Explicit over Silent") align.

**Reversibility:** High — could pre-decide for future tasks if surfacing pattern fails.

**Change trigger:** If a future implementer fails to evaluate and just defaults to plan-literal, switch to direct-decide for similar pattern decisions.

### Classify I-1 (`tuple(None)` crash) as Important rather than Critical

**Decision:** Accept the code-quality reviewer's classification of Important and fix in-scope per Phase A protocol, rather than upgrading to Critical-in-scope per Task 6 precedent.

**Driver:** Reviewer's evidence-backed argument: "this is worse than the Task 6 'silent drop' defect pattern — it is a complete loss of store access. However: requires JSONL corruption (partial flush, hand-edit, external writer) — not normal-path data. Plan-sanctioned pattern."

**Rejected:** Upgrade to Critical-in-scope. Rejected because the precondition (corrupted JSONL) is not normal-path data flow. Task 6's `update_status` defect was Critical because it would activate on every `update_status` call after Tasks 7-8 mutators wrote new-field values — guaranteed to manifest. Task 7's I-1 only manifests when the JSONL log is corrupted.

**Implication:** Establishes a calibration heuristic: severity = precondition-likelihood × symptom-impact, not symptom-impact alone. Critical = normal-path manifestation. Important = corruption-required manifestation. Minor = unlikely or low-impact.

**Trade-offs:** Risk of leaving a known crash vector if the user disagreed with classification. Mitigated by surfacing the finding + classification + dispatch decision in the same response, allowing intervention.

**Confidence:** Medium (E2) — reviewer's classification + my analysis. Could be argued either direction; reasonable people might disagree on whether JSONL corruption is "realistic enough" to warrant Critical.

**Reversibility:** High — could re-classify any time. The fix landed regardless, so reversibility is academic.

**Change trigger:** If JSONL corruption events occur in production or in similar future findings, upgrade similar patterns to Critical-equivalent severity.

### Self-verify the I-1 fix instead of re-dispatching the code-quality reviewer

**Decision:** I (controller) verified the fix via direct `git show` + `git log` + full-package pytest, rather than dispatching another code-quality reviewer subagent.

**Driver:** Same precedent as Task 6's reviewer-directed `update_status` fix. Reviewer's directive was mechanical (3-line code change + 1 specific test). Implementer reported "no deviations". Re-dispatching would cost ~30-50k tokens for a verification scope of "did the implementer apply the exact 3-line change?"

**Rejected:** Re-dispatch code-quality reviewer subagent. Would provide stronger rigor but at meaningful context cost for a tightly-scoped fix.

**Implication:** Self-verification is now an established pattern (used twice — Task 6 + Task 7). For tightly-scoped reviewer-directed fixes (≤ ~5 lines code change), self-verify via diff inspection + test run. For ambiguous fix scope, always re-dispatch.

**Trade-offs:** Less rigor than strict subagent-driven-development. If implementer silently deviated, would miss it. Mitigated by: (a) reviewer's directive being verbatim, (b) implementer's deviation-disclosure protocol reporting "None", (c) my direct diff inspection.

**Confidence:** Medium (E2) — pattern works, but two data points isn't enough to call it durable.

**Reversibility:** Trivial — could dispatch a re-review now if needed.

**Change trigger:** If a self-verified fix later turns out to have a defect, switch back to mandatory re-review.

### Dispatch I-1 fix without pausing for explicit user alignment

**Decision:** Surface I-1 finding + classification rationale + dispatch decision in same response, then dispatch immediately. Did not pause for user "yes" before dispatching.

**Driver:** Phase A protocol: "Important findings get fixed immediately; Minor findings defer." User's prior alignment in Task 6 ("I agree that the `update_status` finding is Critical-in-Task-6-scope") confirmed the fix-immediately approach for non-Minor severities. Prior handoff: "user accepts recommendations with refinements rather than rejecting outright." Momentum preservation under context pressure.

**Rejected:** Pause for explicit per-finding user OK. Would slow momentum, cost context, and the protocol is established. Would also fragment the conversation into "review summary → wait → user OK → dispatch → wait → next step."

**Implication:** Coordinator now has authority to dispatch Important fixes without explicit user OK, provided the dispatch decision is announced in chat for transparency. User can intervene if they disagree with classification.

**Trade-offs:** If user disagreed with Important classification, the fix dispatch would have been wasted. Mitigated by surfacing classification + dispatch in the same response (interruption window).

**Confidence:** Medium (E2) — Phase A pattern strong but no direct user statement this session affirming the autonomous dispatch.

**Reversibility:** High — fix can be reverted or carry-forwarded if user objects.

**Change trigger:** If user pushes back on dispatching without alignment, switch to ask-first.

## Changes

### `packages/plugins/codex-collaboration/server/pending_request_store.py` (MODIFIED — two commits)

**Purpose:** (Commit 1, `941e7efd`) Added 3 success-path mutator methods + 3 new `_replay` op branches + `Literal` import. (Commit 2, `b623548b`) Fixed null-corruption crash in `record_protocol_echo` replay branch via defensive `or ()` coercion.

**Approach:**
- **Mutators:** Three new methods on `PendingRequestStore`, placed after `update_status` (line 70-126 post-Task-7-feat). Each is a thin wrapper around `_append({...op: ..., ...record fields})`. `mark_resolved` writes `op="mark_resolved"` + `request_id` + `resolved_at`. `record_response_dispatch` writes 6 keys including hardcoded `"dispatch_result": "succeeded"` and converts caller's `payload` dict pass-through. `record_protocol_echo` writes `op="record_protocol_echo"` + `request_id` + `list(signals)` (tuple → list at write time) + `protocol_echo_observed_at`.
- **Replay branches:** Three new `elif op == "..."` branches added after the existing `op == "update_status"` branch (lines 193-223 post-Task-7-feat). Used **`dataclasses.replace(existing, **changes)`** consistently (Option A — matches Task 6's `update_status` precedent), NOT the plan's sampled `asdict_for_replay` helper. Each branch does `if rid in requests:` existence check then `requests[rid] = replace(requests[rid], ...named overrides)`.
- **Null-corruption guard (commit 2):** Single point change in `op == "record_protocol_echo"` branch: extract `raw_signals = record.get("protocol_echo_signals") or ()` before passing to `tuple()`. Handles both absent keys AND null values.

**Key implementation details:**
- Import update: `from typing import Any, get_args` → `from typing import Any, Literal, get_args` (line 14)
- `mark_resolved`'s replay branch sets `status="resolved"` + `resolved_at` from record. All other fields auto-preserved.
- `record_response_dispatch`'s replay branch sets `resolution_action`, `response_payload`, `response_dispatch_at`, `dispatch_result`. **Status unchanged** (verified by `test_record_response_dispatch_does_not_change_status`).
- `record_protocol_echo`'s replay branch sets `protocol_echo_signals` (with `or ()` null guard) and `protocol_echo_observed_at`. All other fields auto-preserved.
- `replace()` import was already present from Task 6's fix (`from dataclasses import asdict, replace`); no import change needed for Option A.

**Future-Claude note:** The `update_status` branch's defensive guards (3 of them: type check, validity check, existence check) were not replicated in the new branches because (a) the plan sample showed only `if rid in requests:`, and (b) the new ops encode their semantics in the op name itself (no domain validation needed for `mark_resolved` etc.). The reviewer accepted this asymmetry as plan-sanctioned. The narrower I-1 finding (null-tuple crash) was the only concrete consequence of the lighter guard set.

### `packages/plugins/codex-collaboration/tests/test_pending_request_store_mutators.py` (NEW — 6 tests after I-1 fix)

**Purpose:** Verify the 3 new mutators correctly write JSONL records and that replay correctly hydrates state. Plus regression test for the I-1 null-corruption fix.

**Approach:** 6 tests total (5 from plan-verbatim + 1 added with the I-1 fix). Uses project-standard flat tests layout. Imports follow project convention (`from server.X import Y`).

| Test | Purpose |
|---|---|
| `test_mark_resolved_sets_status_and_timestamp` | Verifies status flip + resolved_at population on a fresh store |
| `test_record_response_dispatch_sets_four_fields` | Verifies all 4 fields including hardcoded `dispatch_result="succeeded"` |
| `test_record_response_dispatch_does_not_change_status` | **Critical invariant**: status stays `"pending"` after `record_response_dispatch` (separation of concerns from `mark_resolved`) |
| `test_record_protocol_echo_sets_signals_and_timestamp` | Tuple preservation through write→replay |
| `test_mutators_round_trip_across_replay` | End-to-end: `create → record_response_dispatch → mark_resolved → record_protocol_echo` then **fresh store instance** to force replay, verify all state persisted |
| `test_record_protocol_echo_replay_handles_null_signals` (added in fix) | **Regression for I-1**: inject a raw JSONL record with `"protocol_echo_signals": null`, reopen store, verify replay completes cleanly with `protocol_echo_signals == ()` |

**Pattern note:** The regression test uses `store._store_path.write_text(...)` / direct `.open("a")` to inject raw JSONL (matches B6.2 carry-forward — inline `import json` is the same style divergence already noted).

### `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (MODIFIED, +11 lines)

**Purpose:** Track Task 7's two Minor findings (B7.1, B7.2) and document the resolved Important finding (I-1).

**Approach:** Appended a new "From Phase B Task 7" subsection under "Open items" with two rows. Appended a new "From Phase B Task 7" subsection under "Closed items" with the I-1 resolution entry.

**Seeded content:**
- B7.1: Unused `import pytest` in `test_pending_request_store_mutators.py` (matches A4 pattern; end-of-phase polish)
- B7.2: `req_id` vs `rid` variable naming inconsistency in `_replay` (`update_status` uses `req_id`; the 3 new branches use `rid`)
- Closed: `b623548b` — I-1 `record_protocol_echo` null-signals corruption guard

**Future-Claude note:** Tracker now has 7 open items (5 Phase A + 2 Task 6 + 0 Task 7 net Critical; 2 Task 7 Minor) and 2 closed items. Watch the line count — handoff Risk flagged 30+ items by Task 22 as the migration threshold.

## Codebase Knowledge

### Architecture: Phase B success-path lifecycle (post-Task-7)

| Component | File:line | Role |
|---|---|---|
| `PendingServerRequest` | `models.py:285-319` | 21-field `@dataclass(frozen=True)` (10 base + 11 Packet 1) |
| Persistence | `pending_request_store.py` (222 lines post-Task-7) | Append-only JSONL; replay-on-read; last-record-wins |
| `create` | `pending_request_store.py:29-38` | Initial write API. Validates status, calls `asdict()`, list-converts `available_decisions` |
| `update_status` | `pending_request_store.py:58-69` | Status transition. Validates against `_VALID_STATUSES` |
| **`mark_resolved` (NEW)** | `pending_request_store.py:71-83` | Atomic transition to `status="resolved"` + `resolved_at` timestamp |
| **`record_response_dispatch` (NEW)** | `pending_request_store.py:85-108` | Records successful operator-decision dispatch; sets 4 fields including hardcoded `dispatch_result="succeeded"`; **does NOT change status** |
| **`record_protocol_echo` (NEW)** | `pending_request_store.py:110-126` | Records post-turn protocol echo signals; tuple → list at write time |
| `_replay` | `pending_request_store.py:138-223` | Re-creates dict of `request_id → PendingServerRequest` from JSONL. Now handles 5 ops: `create`, `update_status`, `mark_resolved`, `record_response_dispatch`, `record_protocol_echo` |
| Read API | `pending_request_store.py:40-56` | `get`, `list_pending`, `list_by_collaboration_id` — unchanged |

### Pattern: `dataclasses.replace()` over `asdict_for_replay()` for replay branches

**Discovered (Task 6 fix `3fbba140`, locked in Task 7 `941e7efd`):** All replay branches that perform state transitions use `replace(existing, **changes)` rather than the plan's sampled `asdict_for_replay(existing)` helper.

**Why `replace()` is strictly better:**
- `replace()` is stdlib (`from dataclasses import replace`).
- Auto-preserves all unmentioned fields. No defensive explicit overrides needed.
- Type-safe: returns the same dataclass type.
- Doesn't traverse into tuples/dicts (avoids `asdict()`'s recursive corruption issue).
- ~5 lines per branch vs ~9-13 lines for the plan's pattern.

**The plan's helper was a workaround for a problem `replace()` doesn't have.** The helper docstring justifies its existence with: "since `dataclasses.asdict` would conflict with the custom tuple/dict types if we use it naively". `replace()` doesn't go near those internals.

**Generalization for Tasks 8, 9, and beyond:** Use `replace(existing, **changes)` for all replay branches that transform state. Reject the `asdict_for_replay` helper unless there's a use case `replace()` genuinely can't handle (none observed yet).

### Pattern: `record.get(key) or default` for null-safe coercion

**Discovered (Task 7 I-1 fix `b623548b`):** `dict.get(key, default)` returns `default` only when the key is *absent*. If the key is present with value `None`, `get` returns `None`. Wrapping `None` in `tuple()`, `list()`, `int()`, or any other type constructor raises `TypeError`.

**The fix pattern:** Use `or` fallback when extracting tuple/list values from JSONL records:
```python
raw_signals = record.get("protocol_echo_signals") or ()
result = tuple(raw_signals)
```

This handles both absent keys AND null values:
- Key absent: `record.get(...)` returns `None`. `None or ()` → `()`. `tuple(())` → `()`. ✅
- Key present with `null`: same as above. ✅
- Key present with `[]`: `[] or ()` → `()`. `tuple(())` → `()`. ✅
- Key present with `["a", "b"]`: `["a", "b"] or ()` → `["a", "b"]`. `tuple(["a", "b"])` → `("a", "b")`. ✅

**Generalization for Tasks 8, 9, and beyond:** Apply this pattern whenever wrapping `record.get(...)` in any constructor. Especially relevant for tuple-typed fields. Verify Task 8's plan for any new tuple fields and pre-emptively apply the pattern.

### Convention: Replay-branch defensive coercion strategies (3 patterns)

Three patterns coexist in `pending_request_store.py:_replay` for handling potentially-malformed records:

1. **`try/except (KeyError, TypeError): continue`** — used by the `op == "create"` branch (line 121-122). Catches missing keys AND tuple-of-None failures. Defense-in-depth.
2. **Explicit type checks before mutation** — used by the `op == "update_status"` branch (lines 184-191): `isinstance(req_id, str)`, `isinstance(status, str)`, `status not in _VALID_STATUSES`, `req_id not in requests`. Loud rejection of bad data.
3. **Existence check + `or default` coercion** — used by Task 7's new branches (post-fix). Single guard `if rid in requests:` plus `or ()` for tuple-coerced values. Narrow, plan-sanctioned.

**No single pattern is universal.** Task 6's `update_status` branch uses pattern 2, Task 7's new branches use pattern 3, the existing `op == "create"` uses pattern 1. The reviewer accepted the asymmetry as plan-sanctioned but flagged it as observation.

### Surprising Findings

- **The plan's redundant explicit overrides in `_replay` branches** (e.g., `"available_decisions": existing.available_decisions` in `mark_resolved`) are unnecessary even within the plan's own pattern — they're already in the `**asdict_for_replay(existing)` spread. This was defensive copy-paste in the plan author's draft.
- **The `op == "update_status"` Pyright `str→PendingRequestStatus` narrowing error** that Task 6 inherited and Task 6's fix resolved (via `replace()` handling typing internally) is now firmly resolved. Task 7 verified post-fix Pyright is clean on that line.
- **Pyright cache staleness on dataclass-method new methods** (not just new fields) repeats the Task 6 pattern. After Task 7's commit, Pyright reported "Cannot access attribute" on the new test file's `mark_resolved`/`record_response_dispatch`/`record_protocol_echo` calls. Runtime tests are ground truth. Confirms the gotcha generalizes from new fields to new methods.

### Key Locations

| Concept | Location |
|---|---|
| `PendingServerRequest` dataclass | `models.py:285-319` (21 fields) |
| `PendingRequestStore` | `pending_request_store.py` (222 lines post-Task-7) |
| `_replay` | `pending_request_store.py:138-223` |
| `op == "create"` replay branch | `pending_request_store.py:154-183` |
| `op == "update_status"` replay branch | `pending_request_store.py:184-192` (uses `replace`) |
| `op == "mark_resolved"` replay branch | `pending_request_store.py:193-200` (uses `replace`) |
| `op == "record_response_dispatch"` replay branch | `pending_request_store.py:201-210` (uses `replace`) |
| `op == "record_protocol_echo"` replay branch | `pending_request_store.py:211-223` (uses `replace` + `or ()` null guard) |
| `_VALID_STATUSES` | `pending_request_store.py:18` (derives from `get_args(PendingRequestStatus)`) |
| Packet 1 manifest | `docs/plans/2026-04-24-packet-1-deferred-approval-response.md` |
| Phase B plan | `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-b-stores.md` (1151 lines) |
| Carry-forward tracker | `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (61 lines) |

### Dependency Graph (Packet 1 Phase B post-Task-7)

```
PendingServerRequest (models.py:285-319, 21 fields)
  └── used by: PendingRequestStore (persistence)
        ├── create()                          [pre-Packet-1]
        ├── update_status()                   [pre-Packet-1; Task 6 fixed replay]
        ├── mark_resolved()                   [Task 7 NEW]
        ├── record_response_dispatch()        [Task 7 NEW]
        ├── record_protocol_echo()            [Task 7 NEW]
        ├── record_timeout()                  [Task 8 — pending]
        ├── record_dispatch_failure()         [Task 8 — pending]
        └── record_internal_abort()           [Task 8 — pending]
        └── _replay (5 ops post-Task-7, 8 ops post-Task-8)
              ├── op=="create"                [Task 6 extended]
              ├── op=="update_status"         [Task 6 fix: replace()]
              ├── op=="mark_resolved"         [Task 7 NEW: replace()]
              ├── op=="record_response_dispatch"  [Task 7 NEW: replace()]
              ├── op=="record_protocol_echo"  [Task 7 NEW: replace() + or () null guard]
              └── (Task 8 adds 3 more replay branches)
```

### Conventions Observed (Phase B)

- Tests use `tmp_path` pytest fixture for isolation
- Tests use `store._store_path.write_text(...)` / `.open("a")` for raw JSONL injection (precedent + B6.2 + B7's regression test)
- JSONL records use `sort_keys=True` (line 132) — deterministic serialization
- `os.fsync()` after every write (line 134) — durability convention
- `from server.X import Y` import style (not `codex_collaboration.server.*`)
- `import pytest` is included by convention even when unused (carry-forward A4, B7.1)
- Variable naming: `req_id` in pre-existing branches, `rid` in new branches (carry-forward B7.2)

## Context

### Project State

- Branch: `feature/delegate-deferred-approval-response`
- Commits on branch (most recent first):
  - `038525ba` docs(delegate): record Task 7 carry-forward items B7.1 + B7.2
  - `b623548b` fix(delegate): guard record_protocol_echo replay against null signals
  - `941e7efd` feat(delegate): add PendingRequestStore success-path mutators
  - `4a35e636` docs(delegate): add Packet 1 carry-forward tracker
  - `3fbba140` fix(delegate): preserve Packet 1 fields across update_status replay
  - `5120413b` feat(delegate): extend PendingServerRequest with 11 new deferred-approval fields
  - `b6dbaa3c` ← Phase A end state
- Working tree clean
- 917 tests in codex-collaboration package (was 911 at Task 6 end; +5 from Task 7 mutator tests + 1 from I-1 regression)
- Phase B Task 7 complete; Tasks 8-9 remain

### Environment

- Python 3.12 (pytest runs under uv workspace selection)
- macOS (BSD sed/find)
- `uv run --package codex-collaboration pytest ...` from repo root
- `PYTHONPATH=packages/plugins/codex-collaboration uv run --package codex-collaboration python -c "..."` for direct imports

### Mental Model

**Framing:** Phase B is a chain of mechanical tasks where the *interesting work* is finding-elevation across the spec→quality review boundary. The implementation itself is plan-verbatim copy-paste with one structural pattern decision per task.

**Core insight:** Two-stage review's value is in the spec→quality boundary. Spec compliance asks "did they build what was specified?" Quality asks "is it well-built?" A finding about robustness lands at the boundary, and the quality reviewer's lens converts spec-irrelevant observations into Important findings. Task 6 demonstrated this with the `update_status` Critical upgrade. Task 7 demonstrated it with the I-1 Important.

**Mental model — task shape:** Each Phase B task has the same shape:
1. Implementer (haiku, mechanical) writes plan-verbatim code + tests.
2. Spec reviewer (sonnet) verifies plan compliance + identifies out-of-scope observations.
3. Quality reviewer (sonnet) converts observations into severity-classified findings.
4. Coordinator dispatches Critical/Important fixes in scope, defers Minor to carry-forward.
5. Self-verify fixes under context pressure (per Task 6+7 precedent).

**For Tasks 8-9:** Expect the same shape. Apply the locked-in patterns (`replace()`, `or ()` defensive coercion). Watch for new tuple fields that need the null guard. Reject the plan's `asdict_for_replay` references.

### Phase B Task 7 → Task 8 transition state

Task 8 adds atomic failure-path mutators:
- `record_timeout(request_id, timed_out_at)` — should set `status="canceled"` + `timed_out=True` + `resolved_at=timed_out_at`
- `record_dispatch_failure(request_id, error)` — should set `status="canceled"` + `dispatch_result="failed"` + `dispatch_error=error`
- `record_internal_abort(request_id, reason, aborted_at)` — should set `status="canceled"` + `internal_abort_reason=reason` + `resolved_at=aborted_at`

Plus 3 new `_replay` op branches.

Plan section: `phase-b-stores.md:525-895` (per `grep` output earlier this session).

The pattern decisions are now locked in by Task 7:
- Use `replace(existing, **changes)` directly. NOT `asdict_for_replay`.
- Apply `or ()` defensive coercion if any new field is a tuple/list read via `dict.get(...)`. Look for `dispatch_error`, `internal_abort_reason` — if they're typed as something coerced via constructor, may need the pattern.
- Match Task 7's 3-commit shape: feat + (any in-scope fix) + carry-forward update.

## Conversation Highlights

**User opening (the entire user-side this session):**
> User: "Yes, start by reading the Task 7 plan section and then dispatching"
— Single-message authorization for the full Task 7 sequence. Trust signal that prior-session handoff alignment was sufficient.

(No mid-execution user interjections.)

**Implicit signals:**
- User trusted the coordinator to dispatch the I-1 fix without explicit per-finding approval.
- User did not interject when reviewers came back, suggesting they read the reports but only intervene on disagreement.

## User Preferences

**Stated priorities (this session):**
- "start by reading the Task 7 plan section and then dispatching" — affirms read-first-then-dispatch sequencing as the working pattern.

**Carried forward from prior session (still in force):**
- **Recommendation-first decision style:** User accepts recommendations with refinements rather than rejecting outright. Confirmed by zero pushback this session.
- **Plan-first discipline / fix-immediately:** Important findings get fixed in scope; Minor findings carry-forward. Phase A pattern. Confirmed by zero pushback on the I-1 dispatch.
- **Trust-but-verify:** User likely runs `/copy` on coordinator output. Communication style assumes they're reading reports independently.
- **Plan-literal execution discipline:** The implementer briefing's "preserve literal plan execution" rule continues to hold. Where deviations exist (Option A choice this session), they are explicitly authorized and disclosed.
- **Carry-forward tracking durability:** From Task 6 — items go in `carry-forward.md`, not just handoff narrative. Confirmed by tracker still being the right home for B7.1 + B7.2.

**Communication:** Concise, evidence-backed, file-linked. Single-line directives. Expects coordinator to maintain context without re-statement.

## Learnings

### `dict.get(key, default)` does NOT handle JSON null values

This is a Python language detail that becomes a JSONL persistence gotcha: `dict.get(key, default)` returns `default` only when the key is *absent*. If the key is present with value `None`, `get` returns `None`, not `default`. When the loaded JSONL has `"foo": null`, downstream `tuple(record.get("foo", ()))` will raise `TypeError`.

**Mechanism:** `dict.get` checks key existence, not value falsy-ness. None is returned as-is.

**Evidence:** Task 7 I-1 finding. Reviewer's analysis at the code-quality review confirmed this is the cause of the `tuple(None)` crash.

**Implication:** Any defensive coercion that wraps `record.get(...)` in `tuple()`, `list()`, `int()`, etc. is vulnerable to JSON null values. Pattern audit needed for all replay branches across all stores.

**Fix pattern:** `record.get(key) or default` — handles both absent and null cases.

**Watch for:** Tasks 8, 9, and any future replay branch that calls `tuple(...)`, `list(...)`, etc. on the result of `record.get(...)`. Apply `or default` proactively.

### Severity classification: Important vs Critical based on precondition

**Heuristic:** Classify by precondition-likelihood × symptom-impact, not symptom-impact alone:
- **Critical:** precondition exists in normal-path data flow (e.g., Task 6's `update_status` defect — every call would activate it).
- **Important:** precondition requires data corruption (partial flush, hand-edit, external writer; e.g., Task 7's I-1 — only manifests on JSONL with `null` values).
- **Minor:** precondition unlikely or low-impact (e.g., unused imports, naming inconsistencies).

**Mechanism:** Importance is severity × likelihood. A symptomatically-loud crash (store unavailability) can be Important if the precondition is rare; a symptomatically-silent corruption (field zeroing) can be Critical if the precondition is normal-path.

**Evidence:** Task 6 vs Task 7 contrast. Reviewer correctly applied this lens to I-1 ("plan-sanctioned pattern, JSONL corruption required").

**Implication:** When dispatching review subagents, give them the precondition lens explicitly so they don't over- or under-classify.

**Watch for:** Findings labeled "loud crash" with rare preconditions — likely Important not Critical. Findings labeled "silent corruption" with normal-path preconditions — likely Critical not Important.

### Self-verification of reviewer-directed fixes is now an established pattern

Used twice (Task 6 + Task 7). Both worked. Pattern: when reviewer's directive is mechanical (≤ ~5 lines code change), implementer reports verbatim match + no deviations, and context budget is constrained, controller verifies via `git show` + test run rather than re-dispatching code-quality reviewer.

**Mechanism:** Reviewer's directive is the spec for the fix. Implementer's adherence + diff inspection + test pass = sufficient verification for tightly-scoped fixes.

**Evidence:** Both Task 6 (`3fbba140`) and Task 7 (`b623548b`) self-verified fixes shipped clean with no subsequent issues found.

**Threshold:** Self-verify when directive is mechanical (≤ ~5 lines, single-file or 2-file scope, no ambiguity). Re-dispatch when ambiguity exists or scope is larger.

**Trade-off:** ~30-50k token savings per skipped re-review. Cost: less rigor, theoretical risk of missed deviation.

**Watch for:** First failed self-verification (would invalidate the pattern). Track via post-merge findings.

### Coordinator can dispatch Important fixes without explicit per-finding user OK

**Mechanism:** Phase A protocol "Important findings get fixed immediately" + user's prior alignment in Task 6 establishes coordinator authority to dispatch fixes for findings classified Important by reviewers, provided the dispatch decision is announced in chat.

**Evidence:** Task 7 I-1 fix dispatched without pause. User did not push back.

**Implication:** Reduces fragmentation of conversation flow. Coordinator surfaces classification + dispatch decision in same response, allowing user intervention if disagreement.

**Trade-off:** Wasted dispatch if user disagreed with classification. Mitigated by reviewer's evidence-backed classification + transparent surfacing.

**Watch for:** User pushback ("ask me first") — would invalidate the pattern. Switch back to alignment-first if signaled.

### Pattern decisions can be locked in across multiple tasks via the first-implementation-choice

The `replace()` over `asdict_for_replay()` choice locked the pattern for the entire Phase B store layer (Tasks 7, 8, 9 plus any future replay code). One implementer's evaluation, validated by both reviewers, becomes durable convention.

**Mechanism:** First implementation establishes precedent. Reviewers validate. Coordinator codifies in handoff + carry-forward + future briefings. Future implementers see the precedent (commit history + handoff references) and follow it.

**Evidence:** Task 6 fix established `replace()` for `update_status`. Task 7 implementer evaluated + chose Option A. Spec reviewer validated as "strictly better." Task 8/9 briefings will reference this precedent.

**Implication:** Coordinator should explicitly identify pattern-decision moments and surface them as decision points. Once decided, lock in by referencing the precedent in subsequent briefings.

**Watch for:** Plan samples that conflict with locked patterns. Always reference the precedent in implementer briefings to prevent regression.

## Next Steps

### 1. Dispatch Phase B Task 8: PendingRequestStore atomic failure-path mutators

**Plan section:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-b-stores.md:525-895` (~370 lines).

**What it adds:**
- `record_timeout(request_id, timed_out_at)` — atomic transition to `status="canceled"` + `timed_out=True` + `resolved_at=timed_out_at`
- `record_dispatch_failure(request_id, error)` — atomic transition to `status="canceled"` + `dispatch_result="failed"` + `dispatch_error=error`
- `record_internal_abort(request_id, reason, aborted_at)` — atomic transition to `status="canceled"` + `internal_abort_reason=reason` + `resolved_at=aborted_at`
- 3 new `_replay` op branches

**Dependencies:** Task 7 complete at `038525ba`. No blockers.

**What to read first:**
- `phase-b-stores.md:525-895` (Task 8 section)
- `pending_request_store.py` (post-Task-7 state, 222 lines) — note the `replace()` precedent in 4 branches now
- `models.py:285-319` (21 fields)
- `carry-forward.md` (may have items relevant to Task 8)

**Approach suggestion:** Same subagent-driven-development pattern. Model tier: haiku for implementer (mechanical), sonnet for reviewers. Briefing notes for the implementer:

1. **"Preserve literal plan execution: if adapting any sample, report the deviation explicitly."**
2. **"Phase A + Phase B Task 6/7 carry-forward items are NOT Task 8 scope unless encountered directly; do not opportunistically fix them."**
3. **"Use `dataclasses.replace(existing, **changes)` directly for all replay branches. Task 7's commit `941e7efd` locks this pattern. Skip the plan's sampled `asdict_for_replay` helper. If the plan still references it for Task 8, treat as a known-stale plan reference."**
4. **"Apply the `or ()` defensive coercion pattern if any new field is a tuple/list read via `dict.get(...)`. Task 7 commit `b623548b` establishes this — `record.get(key) or default` handles both absent and null values, while `record.get(key, default)` does NOT handle null."**

**Special review focus:**
- Each failure-path mutator must atomically set status to `"canceled"` AND the failure-specific fields. Verify no partial-state risk.
- Watch for double-resolve scenarios: what happens if `record_timeout` is called after `mark_resolved`? Plan should specify; reviewer should verify.
- Audit each new replay branch for `tuple()`/`list()` traps with `dict.get(...)` (the I-1 pattern).

**Acceptance criteria:** Task 8 commit lands cleanly; spec ✅; quality ✅; full-package regression clean (≥920 tests, up from 917).

### 2. Continue Phase B sequentially: Task 9

Task 9: `DelegationJob.parked_request_id` + `DelegationJobStore.update_parked_request`. This touches a different store (`delegation_job_store.py`). Plan section: `phase-b-stores.md:897-1151`.

**Carry-forward Task 7's pattern decisions:**
- `delegation_job_store.py` plan likely samples an `asdict_for_replay(job)` helper. Reject in favor of `replace()` per Task 7 precedent.
- Apply `or ()` defensive coercion for any tuple/list field.
- Audit `delegation_job_store.py`'s existing replay code for tuple-coercion vulnerabilities (post-Phase-B polish if not in Task 9 scope).

### 3. End-of-Phase-B polish pass

Sweep `carry-forward.md` items that can land without Task 8/9 context:
- A4 (unused `import pytest` in Task 3, Task 4 test files)
- B6.1 (redundant test in `test_pending_server_request_fields.py`)
- B6.2 (inline `import json` style)
- B7.1 (unused `import pytest` in `test_pending_request_store_mutators.py`)
- B7.2 (`req_id` vs `rid` naming consistency in `_replay`)

Coordinator decides whether to batch with end-of-Phase-B closeout or defer to end-of-Phase-H. Consider whether B7.2 can be done as part of Task 8/9 since they touch the same `_replay` method.

### 4. Optional: Audit other stores for `tuple(None)` vulnerabilities

Other stores in the codex-collaboration package (`delegation_job_store.py`, `operation_journal.py`, etc.) may have similar `tuple()`/`list()` calls on `dict.get(...)` results. Could be a separate audit task or rolled into Task 9 (which touches `delegation_job_store.py` directly).

## In Progress

Clean stopping point. Task 7 fully landed (3 commits: `941e7efd` feat + `b623548b` fix + `038525ba` docs). Carry-forward tracker updated with B7.1 + B7.2 + I-1 closed. Working tree clean. Phase B Task 8 ready for dispatch in a fresh session.

## Open Questions

### Does Task 8 add any new tuple/list fields that need the `or ()` defensive pattern?

`dispatch_error` and `internal_abort_reason` are typed as `str | None` per `models.py:285-319` (Task 6 additions). Strings don't need the pattern. But Task 8 may introduce new fields not yet on the dataclass — verify by reading Task 8 plan section before dispatching.

**Recommendation:** Coordinator should pre-read Task 8 plan and pre-emptively apply the pattern in the implementer briefing if any tuple/list field appears.

### Should Task 8/9 audit `delegation_job_store.py` for similar `tuple(None)` vulnerabilities?

Task 9 touches `delegation_job_store.py` directly (`update_parked_request`). Natural opportunity to audit. Could be in-scope or carry-forward.

**Recommendation:** Surface in Task 9 implementer briefing as "while touching `_replay`, audit existing tuple-coercion calls for `or ()` resilience."

### Will the plan's stale `asdict_for_replay` references in Task 8/9 confuse implementers?

The plan was written before Task 6's fix established `replace()`. Task 8 + Task 9 sections still sample `asdict_for_replay`. A future implementer reading the plan literally might introduce the helper despite the locked-in precedent.

**Mitigation:** Implementer briefings must reference Task 7's commits and explicitly direct toward `replace()`. Consider opening a meta-issue to update the plan text post-Phase-B.

## Risks

### Pattern divergence between Task 7 (replace) and Tasks 8-9 (asdict_for_replay)

The plan still samples `asdict_for_replay` for Task 8 + Task 9 sections. If a future implementer follows the plan literally without seeing Task 7's precedent, two patterns will coexist and future readers will have to reason about both.

**Mitigation:** Surface in Task 8 + Task 9 implementer briefings. Reference Task 7 commits `941e7efd` and `b623548b` as precedent. Add briefing rule: "If the plan references `asdict_for_replay`, treat as stale plan text — use `replace()`."

### Tuple-field replay branches in other stores may have similar null-corruption traps

Beyond `pending_request_store.py`, other stores (`delegation_job_store.py`, `operation_journal.py`, etc.) may have `tuple(record.get(...))` patterns vulnerable to JSON null. This is latent tech debt across the package.

**Mitigation:** Audit during Task 9 (which touches `delegation_job_store.py`) or end-of-Phase-B polish. Could grep for the pattern: `tuple\(record\.get\(`.

### Carry-forward tracker growth

Tracker now has 7 open items (5 Phase A + 2 Task 6 + 0 Task 7 net Critical; 2 Task 7 Minor). Phase B has 2 tasks left. Could add 4-6 more by end of Phase B. Handoff Risk flagged 30+ items as the migration threshold.

**Mitigation:** End-of-Phase-B polish sweeps before Phase C. If tracker grows past ~30 items, migrate to per-item tickets via `handoff:defer` skill.

### Self-verification pattern could mask deviations if implementer report quality degrades

Pattern works because implementer reports are reliable ("no deviations"). If a future implementer report inaccurately claims no deviations, self-verification might miss the gap.

**Mitigation:** Continue verifying via `git show` (independent of implementer report). Track first failed self-verification — if it occurs, switch back to mandatory re-review.

### Coordinator-dispatched Important fixes could surprise user if classification is wrong

Pattern works because reviewer classifications are evidence-backed. If a future reviewer misclassifies a Critical as Important, coordinator-dispatched fix might be too narrow.

**Mitigation:** Coordinator second-checks reviewer classification before dispatching. Surface classification rationale in chat for user intervention window.

## References

- **Plan manifest:** `docs/plans/2026-04-24-packet-1-deferred-approval-response.md`
- **Phase B plan:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-b-stores.md`
- **Carry-forward tracker:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md`
- **Spec source:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` (commit `64608b01`)
- **Prior handoff (resumed from):** `docs/handoffs/archive/2026-04-24_22-05_task-6-complete-carry-forward-tracker-seeded.md`
- **Task 6 commits:** `5120413b` feat + `3fbba140` fix + `4a35e636` docs
- **Task 7 commits:** `941e7efd` feat + `b623548b` fix + `038525ba` docs
- **Subagent-driven-development skill:** `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/subagent-driven-development/`

## Gotchas

### `dict.get(key, default)` does NOT handle JSON null

The Python `dict.get` API returns `default` only when the key is absent. JSON null values come through as `None`. Wrap with `or default` whenever passing the result to a constructor: `record.get(key) or () → tuple(...)`. Affects all replay branches that coerce record values into tuple/list/int/etc.

### Plan's `asdict_for_replay` helper references in Task 8/9 are stale

Task 7's precedent locks `dataclasses.replace()` as the pattern. If the plan still samples `asdict_for_replay`, treat as stale plan text and use `replace()`. Reference Task 7 commits `941e7efd` and `b623548b` in Task 8/9 implementer briefings.

### Plan line numbers continue to drift

Phase B plan was written when `pending_request_store.py` was 137 lines. Post-Task-7 it's 222 lines. Locate by structural landmark (`def update_status`, `def _replay`, `op == "create"` branch, etc.), not by absolute line number. Phase B will continue accumulating drift.

### Pyright cache staleness applies to new methods (not just new fields)

After Task 7's commit, Pyright reported "Cannot access attribute" on the new test file's mutator method calls (`mark_resolved`, etc.), generalizing the Task 6 pattern from new fields to new methods. Runtime tests are ground truth.

### Branch has 3 commits for Task 7 — do NOT squash

feat (`941e7efd`) + fix (`b623548b`) + docs (`038525ba`) is the audit trail. Squashing would hide the I-1 review-loop's correction work and the carry-forward documentation update. Phase A precedent: each commit is a first-class artifact.

### `dataclasses.replace()` vs `dataclasses.asdict()` semantics

`replace()` constructs a new instance with named overrides — does NOT recurse into tuples/dicts. `asdict()` is a deep conversion — recurses into nested dataclasses, converts tuples to lists. For replay-branch state transitions, `replace()` is the correct primitive. `asdict()` would corrupt tuple fields.

### Self-verified fixes break strict subagent-driven-development protocol

The skill specifies "Code quality reviewer subagent approves? → yes → Mark task complete." Self-verifying skips this step. Used twice (Task 6, Task 7) under context pressure. Document the deviation explicitly in handoffs so future coordinators know to re-check if needed.

### `record_response_dispatch` does NOT change status

Status flips to `"resolved"` only via `mark_resolved`. `record_response_dispatch` is the transport-write stamp only. Verified by `test_record_response_dispatch_does_not_change_status`. Do NOT accidentally add `"status": "resolved"` to the `record_response_dispatch` replay branch.

### `dispatch_result` is hardcoded inside `record_response_dispatch`

The mutator hardcodes `"dispatch_result": "succeeded"` — no caller kwarg. The failure path is structurally separate (`record_dispatch_failure` in Task 8). Don't expose `dispatch_result` as a caller parameter in Task 7's mutator.
