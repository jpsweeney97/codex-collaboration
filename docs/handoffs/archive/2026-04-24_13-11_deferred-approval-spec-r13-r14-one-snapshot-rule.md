---
date: 2026-04-24
time: 13-11
created_at: 2026-04-24T17:11:26Z
session_id: 61300fe6-8c58-45d2-ac76-637700a68566
project: claude-code-tool-dev
title: Deferred-approval spec R13-R14 — success-path terminal guard + one-snapshot rule
type: handoff
branch: feature/delegate-deferred-approval-response
commit: 64608b01
resumed_from: docs/handoffs/archive/2026-04-24_00-53_deferred-approval-spec-rounds-7-to-10-scrutiny.md
files:
  - docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md
---

# Deferred-approval spec R13-R14 — success-path terminal guard + one-snapshot rule

## Goal

**Immediate objective:** Execute Round 13 (R13) and Round 14 (R14) of the structured /copy-style scrutiny cycle on the deferred-approval response design spec (`docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`, ticket T-20260423-02), landing both rounds as commits and maintaining the user's gate on `superpowers:writing-plans` invocation until the spec is clean.

**Bigger picture:** Packet 1 of the deferred-approval work is the foundational deliverable — it converts `_finalize_turn`'s captured-request branch from a synchronous-decide kind-based escalation model to an async-decide worker-owned resolution model. The spec is under rigorous scrutiny because any ambiguity will propagate into build packets when `writing-plans` decomposes it. The user's gate policy: "writing-plans stays blocked until R14 lands and the one-snapshot rule is explicit."

**Context (not visible in code):** This session continued from the prior handoff. By entry, rounds 7-12 had landed; R13 /copy scrutiny was delivered and locked-in mid-session, then R14 /copy arrived at session end after R13's commit. Each round follows a stable pattern: user delivers /copy with findings → I propose A/B fix options → user locks in specific sub-options with constraints → I execute + run user-stated gates → commit.

**Trigger:** User's R14 /copy scrutiny arrived after R13's commit (`050e309b`) landed, asserting the verdict "Minor revision" with two P2 findings (ordering bug + vocabulary drift). User's lock-in added a stronger invariant than I had originally proposed.

---

## Session Narrative

**Starting state (0):** Session resumed mid-cycle. Prior summary established that R7-R12 commits were on branch `feature/delegate-deferred-approval-response`, R12 had landed as `26bb727b`, spec was at 2382 lines. User had delivered R13 /copy scrutiny and explicitly locked in P1a-A + P1b-A + P2a-A + P2b-A with constraints: name new subsection "`_finalize_turn` Captured-Request Terminal Guard"; writing-plans stays blocked until R13 lands and three gates pass (no old timeout-success test text, no remaining job-status `resolved` drift, no captured resolved/canceled request can re-enter escalation).

**Phase 1 — R13 execution (partly pre-handoff):** Per the prior context, 15 tasks executed covering (a) new §`_finalize_turn` Captured-Request Terminal Guard subsection at :1731 with rule, request-to-job terminal mapping table, D4 blind-write suppression, path table, 5 test bullets; (b) vocabulary normalization at :1722, :1864, :2054 to include `canceled` in terminal lists; (c) new discard-gate row + decision log entry expanding `discard()` to admit `canceled` jobs; (d) diagram annotations at :990 and :1077 documenting the terminal guard; (e) rewritten stale timeout-success test at :2206 asserting sentinel-raise design; (f) §contracts.md updates bumped from "four sections" to "five sections" with new §discard sub-section. All landed as commit `050e309b` (+86/-6). Spec reached 2396 lines.

**Phase 2 — R14 /copy scrutiny arrival:** User delivered new artifact with two P2 findings and "Minor revision" verdict:

> **R14-01:** D4 pending fallback contradicts the terminal-guard algorithm. The spec says `pending` or missing request records fall through to the existing kind-based escalation logic, but the D4 suppression section says the legacy `update_status(request_id, "resolved")` still runs for the pending case. The callsite summary then re-reads the request for status derivation, so an anomalous pending request becomes `resolved` before the guard evaluates it and maps to `completed`/`unknown`, not the promised fallback.

> **R14-02:** Canceled origin text is now stale. Line 1336 and 1809 still describe single-origin for `canceled`, but R13 added a second origin.

**Phase 3 — R14 analysis:** Read spec sections :1320-1370, :1720-1819, :1800-1880 to verify the ordering problem. Traced the literal pseudocode path for "pending + not parse-failed":
1. Line :1782 instructs: "before D4 write, re-read. If terminal, skip D4."
2. Line :1783 instructs: "add terminal guard as FIRST status-derivation check at :1473-1478 — re-read, if terminal use mapping."
3. **Bug:** In pending case, step 1 sees `pending` → D4 writes `"resolved"` → step 2 sees `"resolved"` (promoted by D4, not worker) → maps to `completed`/`unknown` → fall-through never fires → test at :1791 can't pass.

The root cause was structural: two `pending_request_store.get(...)` calls with a mutating `update_status` call between them. The scrutiny gave me two fix options verbatim: "Pin one authoritative snapshot for final-status derivation, or explicitly move the D4 write after the fallback decision."

**Phase 4 — A/B proposal:** Presented to user:

- **Option A** (single authoritative snapshot): read request once at top of captured-request branch; derive both D4 decision and terminal-guard decision from that one snapshot. No second re-read. Test at :1791 works because snapshot genuinely says `pending`.
- **Option B** (defer D4): re-read only at terminal guard; if terminal use mapping; if pending fall through to kind-based logic, D4 runs inside that fall-through branch.

Recommended A — smaller textual delta, collapses to single read (easier invariant to prove), preserves existing D4 location in code.

**Phase 5 — User lock-in (critical moment):** User confirmed A but added a stronger constraint than I had stated:

> "The key constraint I'd add is: **only one request-status read may participate in final-status derivation**. Later reads can still exist for return-shape hydration if needed, but they must not feed the terminal-guard decision."

Also confirmed R14-02 as proposed with specific phrasing requirement ("two origins" + both call-sites name `_WorkerTerminalBranchSignal(reason="timeout_interrupt_succeeded")` and `_finalize_turn` Captured-Request Terminal Guard). Added gate grep:

> "`rg \"only via the non-cancel|single-origin|timeout_interrupt_succeeded branch\"` over the spec after the edit, because this is precisely the kind of stale explanatory sentence that has been recurring."

User's lock-in reframed R14: it wasn't just "fix two P2 findings" — it was "install a named invariant with machinery around it."

**Phase 6 — R14 execution:** Applied six primary edits + supporting consistency fixes:

1. **§The rule** at :1740 — rewrote from "FIRST status-derivation step" language to "The rule — one authoritative snapshot" with inline Python pseudocode showing `request_snapshot = pending_request_store.get(...)` as the single read. Added an explicit paragraph stating the one-snapshot invariant and naming the R14 ordering bug as the specific anti-pattern it prevents.

2. **§D4 blind-write suppression** at :1760 — restructured into three-row table keyed on `request_snapshot.status` (`resolved`/`canceled` → skip D4; `pending` → D4 may write but snapshot authority unchanged; `None` → skip D4, log anomaly). Added closing paragraph "the invariant is 'one snapshot governs,' not 'two reads agree.'"

3. **§Callsite change summary** at :1782 — collapsed the previous two bullets (one for D4 pre-check, one for terminal guard) into a single `:1467-1478` bullet describing the three decisions that consume the same snapshot in order: D4 write, terminal-guard mapping, fall-through. Added explicit prohibition: "future maintainers must not introduce a second `pending_request_store.get(captured_request.request_id)` whose `.status` re-enters the derivation."

4. **§Tests to add** at :1826 — rewrote 5 existing bullets with snapshot vocabulary ("reads the request once into `request_snapshot`, observes `request_snapshot.status="resolved"`, derives..."), and added a new 6th bullet "One-snapshot invariant enforcement" that instruments `PendingRequestStore.get(request_id=<rid>)` with a call counter and asserts exactly-one increment per captured-request path. Rewrote the anomalous+pending test to be explicit about the one-snapshot semantics: snapshot reads once → observes `pending` → D4 writes `resolved` → **still** falls through based on pre-D4 snapshot value.

5. **§Origin** at :1336 (R14-02) — rewrote from single-origin prose to two-origin enumeration listing (1) non-cancel timeout interrupt-succeeded via `_WorkerTerminalBranchSignal(reason="timeout_interrupt_succeeded")` and (2) cancel-capable timeout cancel-dispatch-succeeded mapped by `_finalize_turn` Captured-Request Terminal Guard. Both explicitly verified-cancel.

6. **§poll() `job.status` transitions** at :1851 (R14-02) — rewrote from "reached only via the non-cancel timeout interrupt-succeeded branch" to "reached via either (a) ... or (b) ..." with same two-origin enumeration.

**Phase 7 — Supporting consistency fixes** (discovered during gate sweep):
- Happy-path diagram annotation at :991 — updated from "Captured-Request Terminal Guard re-reads the request" to "reads the request once into request_snapshot, sees snapshot.status=..."
- Timeout cancel-capable diagram annotation at :1085 — same update
- Request-to-job terminal mapping table header at :1760 — updated from `| Re-read \`request.status\` |` to `| \`request_snapshot.status\` |`
- §Why re-read from store subsection at :1774 — renamed to "Why `request_snapshot` reads the store, not `captured_request`" and rewrote body to explicitly invoke the one-snapshot invariant as the upstream authority.

**Phase 8 — Gate verification:** Ran all four primary gates:
- `rg "only via the non-cancel|single-origin|timeout_interrupt_succeeded branch"` → empty (R14-02 gate PASS)
- `rg "re-reads the request|re-read at 1473|second re-read|FIRST status-derivation"` → empty (R14-01 two-reads vocabulary PASS)
- `rg request_snapshot | head -30` → 14+ references established across rule, D4, callsite, tests, diagrams, table header (one-snapshot penetration PASS)
- `rg "two origins|canceled.*origin"` → both :1336 and :1851 show two-origin prose (two-origin prose PASS)

**Phase 9 — Structural invariant preservation check:**
- Sentinel raise-sites table at :476 — 6 rows (unchanged)
- Request-to-job terminal mapping table — 4 rows (unchanged; header vocabulary aligned)
- "Which paths hit the finalizer" path table at :1790 — header preserved
- §contracts.md updates "five sections" at :2023 — preserved
- Test bullets in §_finalize_turn Captured-Request Terminal Guard — 6 (R13 had 5; R14 added one-snapshot invariant enforcement)
- Remaining "re-read" mentions (16) triaged — all are justified (describing `start()`'s distinct flow, or explicit anti-pattern references like "NOT a post-D4 re-read")

**Phase 10 — R14 commit:** Landed as `64608b01` (+63 / -19). Spec reached 2438 lines.

**Phase 11 — Post-commit summary:** Provided user with per-finding resolution table, pre-commit gate results, R12/R13 invariants preserved table, and closing line "Ready for R15 review, or — if this cycle closes — a go-ahead to invoke `superpowers:writing-plans` on the 2438-line spec."

**Set aside for later:** Writing-plans invocation remains blocked per user's lock-in policy.

---

## Decisions

### Decision 1: R14-01 fix strategy = Option A (single authoritative snapshot)

> **Decision:** Pin one authoritative `request_snapshot = pending_request_store.get(...)` read at the top of `_finalize_turn`'s captured-request branch; use that snapshot for both D4 suppression and terminal-guard mapping. Reject Option B (defer D4 into fall-through branch).
> - **Driver:** User quote: "Lock in R14-01 = A, single authoritative snapshot. The key constraint I'd add is: only one request-status read may participate in final-status derivation. Later reads can still exist for return-shape hydration if needed, but they must not feed the terminal-guard decision."
> - **Rejected:** Option B (defer D4 into fall-through branch). User quote: "I would not pick B. Moving D4 into the fall-through branch is semantically cleaner in isolation, but it expands the finalizer rewrite surface and changes the existing line-order contract more than this drift fix needs. A is the smaller and easier-to-prove correction."
> - **Implication:** Future implementer reads the request once, not twice. The one-snapshot invariant is explicit and testable. D4 stays at `delegation_controller.py:1467-1470` in the actual code; its behavior becomes conditional on the snapshot's pre-existing status. The spec's §Callsite change summary now describes a single `:1467-1478` block that restructures around one snapshot rather than two separate surgical insertions.
> - **Trade-offs:** The D4 gate becomes a three-branch conditional (`resolved`/`canceled` → skip; `pending` → write; `None` → skip+log) rather than an unconditional block OR a fully relocated block. Slightly more complex conditional at the same line, vs. a cleaner branch split that would move D4 out of its original line range.
> - **Confidence:** High (E2 — user lock-in + my independent A/B analysis + concrete literal-pseudocode trace showing the R14 ordering bug).
> - **Reversibility:** Medium — a future packet could relocate D4 if profiling or implementation complexity argues for it. The one-snapshot invariant would survive that relocation (the invariant is about how many reads, not where D4 lives).
> - **Change trigger:** If the implementation reveals that the conditional D4 gate is awkward to express in actual Python code (e.g., if `PendingRequestStore.get()` has side effects that the conditional can't elegantly handle), or if a new captured-request path emerges where the single-snapshot model doesn't naturally apply.

### Decision 2: Add "One-snapshot invariant enforcement" as a new dedicated test bullet

> **Decision:** Add a 6th test bullet to §Tests to add in §_finalize_turn Captured-Request Terminal Guard that instruments `PendingRequestStore.get(request_id=<rid>)` with a call counter during `_finalize_turn` and asserts the counter for the captured `rid` increments exactly once per captured-request path.
> - **Driver:** User's lock-in language established the one-snapshot rule as a *named invariant*, not just a convention. A named invariant needs test machinery to survive future regressions — otherwise a maintainer could accidentally add a second `.status` read during refactoring and break the invariant silently.
> - **Rejected alternative:** Strengthen the existing "D4 blind-write suppression" test to cover both the D4 atomicity check AND the one-snapshot rule. Rejected because these are two distinct invariants that should fail independently: D4 suppression is about "don't overwrite worker's write"; one-snapshot is about "don't re-derive from a post-D4 state." Bundling them obscures which invariant failed.
> - **Implication:** §_finalize_turn Captured-Request Terminal Guard Tests block grew from 5 bullets (R13) to 6 bullets (R14). The one-snapshot invariant has explicit dedicated test coverage. Future maintainers who read the spec will see machinery enforcing the invariant, not just prose asserting it.
> - **Trade-offs:** Slightly larger test matrix. Test infrastructure requires instrumenting the store's `get()` with a call counter — more setup than a pure behavioral test.
> - **Confidence:** High (E2 — user explicit lock-in language + structural alignment with how the spec treats other invariants).
> - **Reversibility:** High — if the test proves too brittle (e.g., if legitimate hydration reads trigger false positives), it can be relaxed to a looser assertion or split into multiple narrower tests.
> - **Change trigger:** If the implementation needs more than one `.status` read for legitimate reasons (which would mean the one-snapshot invariant needs revisiting).

### Decision 3: Rewrite §Origin and §poll() status prose in two-origin form

> **Decision:** For R14-02, rewrite both single-origin prose lines (at :1336 and :1809) to explicitly enumerate the two `canceled` origins: (1) non-cancel timeout interrupt-succeeded via `_WorkerTerminalBranchSignal(reason="timeout_interrupt_succeeded")`, and (2) cancel-capable timeout cancel-dispatch-succeeded mapped by §`_finalize_turn` Captured-Request Terminal Guard.
> - **Driver:** User confirmed "R14-02 exactly as proposed. The important phrase is 'two origins,' and both references should name: 1. non-cancel timeout interrupt succeeded via `_WorkerTerminalBranchSignal(reason="timeout_interrupt_succeeded")`, 2. cancel-capable timeout cancel-dispatch succeeded via `_finalize_turn` Captured-Request Terminal Guard."
> - **Rejected alternative:** Leave the single-origin prose and let the newer §`_finalize_turn` Captured-Request Terminal Guard subsection at :1731 (R13) implicitly override the stale prose. Rejected because this creates drift — a reader starting at :1336 or :1809 would form an incorrect single-origin mental model before reaching the subsection that contradicts it.
> - **Implication:** The `canceled` vocabulary is now consistent across three surfaces: §JobStatus='canceled' propagation (origin), §poll() (observability), and §`_finalize_turn` Captured-Request Terminal Guard (mapping). All three name both origins.
> - **Trade-offs:** Slightly longer prose in both sections. Redundancy of two-origin enumeration across the spec (but this redundancy is defense against drift).
> - **Confidence:** High (E2 — user explicit phrasing requirement + structural alignment check against lines :1755, :1788, :2004 which already acknowledge both origins).
> - **Reversibility:** High — prose can be edited freely.
> - **Change trigger:** If a third origin emerges (e.g., a new Packet adds another path that writes `canceled` on the worker path without sentinel-bypass), the enumeration would need to grow.

### Decision 4: Update Request-to-job terminal mapping table header from "Re-read `request.status`" to `request_snapshot.status`

> **Decision:** During the gate sweep, align the R13 terminal mapping table header's column label with the R14 one-snapshot vocabulary.
> - **Driver:** Internal consistency — the R14 rule names the authoritative read `request_snapshot`; the table takes that read as input; using two different labels for the same value is vocabulary drift.
> - **Rejected alternative:** Leave the header as "Re-read `request.status`" since the table's semantics are unchanged. Rejected because "re-read" implies a prior read existed in the finalizer's captured-request branch, which under the one-snapshot rule is false.
> - **Implication:** Small alignment edit; the table's semantics are identical but its vocabulary now consistently points to `request_snapshot`.
> - **Trade-offs:** None meaningful.
> - **Confidence:** High (E1 — internal consistency check).
> - **Reversibility:** Trivial.
> - **Change trigger:** None foreseeable.

---

## Changes

| File | Change | Commit |
|---|---|---|
| `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` | R13: Full §`_finalize_turn` Captured-Request Terminal Guard subsection at :1731 added; vocabulary fixes at :1722, :1864, :2054; new discard-gate admissibility row + decision log entry; diagram annotations at :990 and :1077; rewritten timeout-success test at :2206; §contracts.md updates section count bumped to "five sections" with new §discard sub-section. +86/-6. | `050e309b` |
| `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` | R14: §The rule at :1740 rewritten with one-snapshot invariant language + pseudocode; §D4 blind-write suppression at :1760 restructured as snapshot-keyed table; §Callsite change summary at :1782 collapsed into single-snapshot flow with prohibition clause; §Tests to add at :1826 rewrote 5 bullets with snapshot vocabulary + added "One-snapshot invariant enforcement" as 6th test; §Origin at :1336 rewritten as two-origin enumeration; §poll() at :1851 rewritten as two-origin enumeration; diagram annotations at :991 and :1085 updated; table header at :1760 aligned to `request_snapshot.status`; §Why re-read subsection at :1774 renamed and rewritten. +63/-19. | `64608b01` |

Spec line count progression: R12 closure 2382 → R13 closure 2396 → R14 closure 2438.

---

## Codebase Knowledge

### Spec structure (load-bearing sections for R13/R14 work)

| Section | Location | Role in R13/R14 |
|---|---|---|
| §JobStatus='canceled' propagation | :1332 (header) | Defines the `canceled` literal and its origins. R14-02 edit target at :1336 (origin prose). |
| §JobStatus='canceled' propagation table | :1359 onward (14-row table) | Enumerates every touch point for canceled literal. R13 added `discard()` gate row (R13-05). |
| §Unknown-kind contract | :1720 onward | Defines pre-R13 routing for unparseable requests. R13 terminal guard sits strictly above this. |
| §`_finalize_turn` Captured-Request Terminal Guard | :1731 onward (R13-created) | The central arena. R14 tightened the rule inside this subsection. |
| Request-to-job terminal mapping table | :1758-1765 (4 rows) | Input = `request_snapshot.status` (post R14 rename) × `turn_result.status`. Output = `final_status`. |
| §Why `request_snapshot` reads the store | :1774 (R14 rename) | Explains why the finalizer reads the store, not the `captured_request` arg. |
| §D4 blind-write suppression | :1776 onward | Post-R14: snapshot-keyed three-branch gate. |
| §Callsite change summary | :1801 onward | Post-R14: single-snapshot three-decision flow. |
| §Which paths hit the finalizer (path table) | :1790 (9 rows) | 2 Yes load-bearing (decide-success, timeout-cancel-dispatch-succeeded), 5 No sentinel-bypass, 2 edge. |
| §Tests to add (guard) | :1826 onward | 6 test bullets (post-R14). |
| §poll() — unchanged shape | :1842 (header) | R14-02 edit target at :1851. |
| §contracts.md updates | :2023 (header, "five sections") | R13 bumped from four to five; §discard sub-section added. |

### Key implementation references (from delegation_controller.py)

Not actively read this session, but referenced consistently across the spec. From prior summary context:

- `_finalize_turn` at `delegation_controller.py:1473` — central arena
- `_finalize_turn` D4 carve-out at `delegation_controller.py:1467-1470` — unconditional pre-R14 `update_status(rid, "resolved")` write; R14 converts this to snapshot-gated conditional
- `_finalize_turn` kind-based escalation at `delegation_controller.py:1473-1478` — existing `if captured_request.kind in _CANCEL_CAPABLE_KINDS` branch that R13 terminal guard sits above
- `discard()` gate at `delegation_controller.py:1404-1406` — admits `failed`/`unknown` only, R13 expanded to admit `canceled` with null promotion_state
- `_TERMINAL_STATUS_MAP` at `delegation_controller.py:104-108` — maps `JobStatus` terminal literals to `DelegationTerminalStatus`; R13 added `"canceled": "canceled"` entry requirement
- `_load_or_materialize_inspection` guard at `delegation_controller.py:873` — R13 requires tuple expansion to 4 literals

### `AppServerRuntimeSession` (runtime.py)

Not actively read this turn, but shown via system-reminder as a reference. At `packages/plugins/codex-collaboration/server/runtime.py` (294 lines):

- `build_workspace_write_sandbox_policy(worktree_path)` at `runtime.py:23` — execution sandbox for delegate-worktree turns
- `run_advisory_turn(...)` at `runtime.py:140` — read-only advisory with `allowed_terminal_statuses=("completed",)`
- `run_execution_turn(...)` at `runtime.py:160` — execution with `allowed_terminal_statuses=("completed", "interrupted", "failed")` and optional `server_request_handler`
- `_run_turn(...)` at `runtime.py:194` — shared notification loop; the `server_request_handler` callback fires for messages with both `id` and `method` (server-initiated requests)
- `interrupt_turn(...)` at `runtime.py:185` — calls `turn/interrupt` with `{threadId, turnId?}`

Relevant for R13/R14 because the server_request_handler mechanism at `runtime.py:245-248` is where `command_approval`/`file_change` server requests surface to the plugin layer, which is what the captured-request branch is ultimately handling.

### Spec conventions observed

- **Subsection intros:** `**Bold intro.** Prose follows...` pattern.
- **Tables:** Pipe-delimited Markdown; 3-column for mapping, 4+ for complex relationships.
- **Sentinel raise-sites:** notation `_WorkerTerminalBranchSignal(reason="...")` used consistently across path tables and prose.
- **Callsite references:** File-line format `delegation_controller.py:NNNN-NNNN` or `:NNNN` for single lines.
- **Vocabulary rigor:** `request.status` = underlying field on `PendingServerRequest`; `request_snapshot.status` = value observed by finalizer's single read. The spec distinguishes these — R14 reinforced the distinction.

### Structural invariants of the spec (surviving R14)

| Invariant | Location | Count |
|---|---|---|
| Sentinel raise-sites table rows | :476 | 6 |
| Request-to-job terminal mapping rows | :1760 | 4 |
| "Which paths hit the finalizer" rows | :1790 | 9 |
| §JobStatus='canceled' propagation touch-point table rows | :1359 | 14-15 (R13 expanded) |
| §contracts.md updates sub-sections | :2023 | 5 (R13 expanded from 4) |
| §_finalize_turn Captured-Request Terminal Guard test bullets | :1826 | 6 (R14 expanded from 5) |

---

## Context

**Framing:** R14 is a *tightening* round, not an *expansion* round. R7 through R13 were predominantly *additive* — they added new subsections, new table rows, new raise-sites, new scenarios to cover cases that prior rounds missed. R14 took existing prose (the R13 terminal guard's two-read structure) and compressed it into a stronger invariant (one snapshot governs all derivation).

**Core insight:** The one-snapshot rule is the kind of invariant that only becomes necessary AFTER the design is complete enough that a careful implementer could *almost* introduce the bug during implementation. R13 added the terminal guard subsection with two sequential `pending_request_store.get(...)` reads (one at the D4 pre-check, one at the mapping derivation). The spec literal was internally contradictory — the anomalous+pending test at :1791 couldn't pass if the implementation followed the two-read spec literally. R14 didn't discover new behavior; it made the intended behavior enforceable.

**Mental model used:** `_finalize_turn`'s captured-request branch as a "time-crystallized view." The snapshot freezes world state; all decisions derive from that frozen state. Mutations after the snapshot (like D4) are visible in future store reads but invisible to the frozen snapshot. Same mental model as a database SERIALIZABLE isolation snapshot, or a functional immutable snapshot in a pure-language data model. The one-snapshot rule says: "the frozen view is the authority; live re-reads don't participate in derivation."

**Round framing arc observed:** R7-R9 were scope-expansion rounds (new scenarios, new raise-sites). R10-R12 were vocabulary-normalization rounds (propagating new literals through all touch points). R13 was a critical-fix round (fixing the success-path re-escalation hole). R14 is an invariant-tightening round. The user appears to be gradually narrowing the spec from "complete" (all cases handled) to "rigid" (no implementation path can accidentally break the design).

---

## Learnings

### Spec-review cycle rhythm

- **Round pattern:** user delivers /copy with findings → I propose A/B fixes with tables → user locks in with constraints (often adding invariants my proposal missed) → I execute + run user-stated gates → commit with `docs: round-N ...` title → summarize closure → wait for next round.
- **Gate discipline:** Each round's commit must pass user-stated grep gates AND preserve prior rounds' structural invariants. Invariant tables (sentinel raise-sites, terminal mapping, path table, propagation rows) must be preserved or explicitly expanded — never silently changed.
- **Round commit title format:** `docs: round-N <theme> on deferred-approval spec (T-20260423-02)`. Theme examples: "success-path propagation" (R13), "one-snapshot rule" (R14), "vocabulary/control-flow propagation" (R12).

### Spec patterns observed

- **Two sources of `canceled`:** R13 created a second origin for `DelegationJob.status="canceled"` (cancel-capable timeout cancel-dispatch-succeeded via finalizer guard, in addition to the existing non-cancel timeout interrupt-succeeded via sentinel bypass). R14-02 was the corresponding vocabulary normalization across the spec.
- **Layer separation:** `request.status` (request layer, lifecycle: pending/resolved/canceled) vs `DelegationJob.status` (job layer, lifecycle includes queued/running/needs_escalation + terminal set). The spec is explicit that `resolved` never appears on the job layer — R13 corrected drift at :1864.
- **Snapshot vs. struct distinction:** `captured_request` = struct passed into `_finalize_turn` by `_execute_live_turn` at parking time (frozen, still shows `pending`). `request_snapshot` = fresh store read from inside `_finalize_turn` (reflects worker's post-parking writes). The R14 one-snapshot rule names `request_snapshot` as the sole authority.
- **Path table rule:** Every captured-request worker path is classified as "Reaches `_finalize_turn`? Yes/No." The 9-row path table at :1790 is the authoritative enumeration — a new path must appear there or it's silently undocumented.

### Gate grep patterns

User-stated grep gates are specific and runnable:

- `rg "only via the non-cancel|single-origin|timeout_interrupt_succeeded branch"` — R14-02 single-origin recurrence guard
- `rg "re-reads the request|re-read at 1473|second re-read|FIRST status-derivation"` — R14-01 two-reads vocabulary guard (self-imposed)
- Structural invariant checks via `awk` range + `rg -c` count (e.g., test bullets in §_finalize_turn Captured-Request Terminal Guard tests block)

---

## Next Steps

1. **Wait for user input.** Next expected interaction is either (a) R15 /copy scrutiny or (b) explicit "proceed to writing-plans" direction. Per user's established policy, writing-plans stays blocked until the spec cycle closes.

2. **If R15 arrives:** Apply same round-structure: read relevant sections → propose A/B (or single-direction) fixes → wait for lock-in → execute → gate-check → commit with `docs: round-N ...` title. Expect the scrutiny to target either residue from R14 (e.g., consistency holes the one-snapshot rule might have missed) or new surfaces (e.g., implementation-time concerns not yet addressed).

3. **If writing-plans go-ahead:** Invoke `superpowers:writing-plans` on the 2438-line spec `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`. This will decompose into build packets. Expected output is an implementation plan artifact — likely in `docs/plans/` or similar.

4. **For either branch, preserve invariants:** If new edits are made, verify all R13/R14 structural invariants remain: sentinel raise-sites (6), terminal mapping (4), path table (9), `canceled` propagation touch points (14-15), §contracts.md updates (5 sections), tests in §Captured-Request Terminal Guard (6).

---

## In Progress

Clean stopping point — no work in flight.

R14 committed as `64608b01`. All user-stated gates passed. Prior-round invariants verified preserved. Spec at 2438 lines.

Session ended after providing the R14 closure summary and waiting for user direction.

---

## Open Questions

1. **Whether the R14 cycle closes the spec:** User's policy blocks writing-plans until the cycle closes. It's unclear whether the user will deliver an R15 /copy (extending the cycle) or issue a go-ahead. Pattern across R7-R14 suggests at least one more round is likely — residual drift from the R14 one-snapshot rule may surface in post-R14 review (e.g., downstream prose that used "re-read" vocabulary for legitimate but now-confusable reasons).

2. **Implementation-time translation of single-snapshot rule:** The spec describes the rule in terms of `pending_request_store.get(request_id)` semantics. The actual Python implementation may need to grapple with (a) hydration reads that need to happen anyway and (b) test harness design that can distinguish "derivation reads" from "hydration reads." The R14 test bullet says "hydration reads for non-status fields are permitted only if they use a distinct access pattern that the test harness recognizes as non-derivation" — this punts the actual mechanism to implementation time.

3. **Whether the D4 conditional gate is the cleanest expression:** Option A preserves D4's location at `:1467-1470` but makes its behavior conditional on `request_snapshot.status`. An implementer might find this awkward and prefer Option B-like relocation. The spec doesn't prohibit implementation-time relocation as long as the one-snapshot invariant is preserved — but the spec's §Callsite change summary describes the D4 write inline with the three-decision flow, which may need updating if relocation happens during build.

---

## Risks

1. **Round proliferation risk:** Each round adds surface to the spec. Spec is now 2438 lines (started cycle at ~2300). Further rounds risk making the spec harder to read holistically. Mitigation: treat closure as a positive goal; err toward "accept" verdicts when findings are cosmetic.

2. **Implementation-spec divergence risk:** Each round references `delegation_controller.py` line numbers (e.g., `:1467-1470` for D4). As Packet 1 implementation proceeds, those line numbers will shift and the spec's callsite references will decay. Mitigation: post-implementation, run a review pass to update or remove brittle line references.

3. **Snapshot invariant leak risk (low but real):** The one-snapshot rule relies on the spec-level prohibition + a test with an instrumented call counter. If the implementation accidentally bypasses `PendingRequestStore.get()` (e.g., reads the underlying JSONL or uses a different accessor), the call counter test could pass while the invariant is violated. Mitigation: the spec prose explicitly names `pending_request_store.get(captured_request.request_id)` as the sole authority — an alternative access pattern would be a spec violation.

4. **Scrutiny cycle fatigue risk:** R14's findings were P2 (vs. P1 in R13). If R15 also surfaces P2/P3-only findings, the marginal value of continuing vs. declaring closure becomes a judgment call. User appears to be the gate-keeper here.

---

## References

### Prior-round handoffs (archived)

- `docs/handoffs/archive/2026-04-24_00-53_deferred-approval-spec-rounds-7-to-10-scrutiny.md` (this session's `resumed_from`)

### Spec and supporting files

- Primary spec: `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md` (2438 lines post-R14)
- Implementation (not modified this session): `packages/plugins/codex-collaboration/server/delegation_controller.py`
- Runtime wrapper (referenced, not modified): `packages/plugins/codex-collaboration/server/runtime.py`
- Models (referenced in spec as `models.py:NN`): `packages/plugins/codex-collaboration/server/models.py`

### Commits this session

- `050e309b` — `docs: round-13 success-path propagation on deferred-approval spec (T-20260423-02)` (+86/-6, executed early in session per prior-handoff continuation)
- `64608b01` — `docs: round-14 one-snapshot rule on deferred-approval spec (T-20260423-02)` (+63/-19, this session's landed commit)

### Prior-round commits (for cycle context)

- `26bb727b` — R12 vocabulary/control-flow propagation
- `e8d0cbd0` — R11 scrutiny
- `fa4955b4` — R10 normalize
- `4211c408` — R9 scrutiny
- `5e041f90` — R8 normalize
- `873d8470` — R7 normalize
- `1f2f1f72` — R6 scrutiny

### User lock-in text for R13 (from prior handoff continuation)

User required: name the new subsection "`_finalize_turn` Captured-Request Terminal Guard"; take the contract expansion (P2b-A) rather than remove "dismiss" claim; agree P1a-A key correction is `_finalize_turn` must re-read authoritative `PendingServerRequest`.

### User lock-in text for R14 (this session)

> "Lock in R14-01 = A, single authoritative snapshot.
>
> The key constraint I'd add is: only one request-status read may participate in final-status derivation. Later reads can still exist for return-shape hydration if needed, but they must not feed the terminal-guard decision.
>
> Recommended wording for the implementation rule:
>
> ```python
> request_snapshot = pending_request_store.get(captured_request.request_id)
>
> # D4 decision uses request_snapshot.status.
> # final_status derivation uses request_snapshot.status.
> # No second status-derivation re-read after D4.
> ```
>
> Then:
> - `snapshot.status in ("resolved", "canceled")` → skip D4 and map via terminal guard.
> - `snapshot.status == "pending"` → D4 may write `"resolved"` for legacy/fall-through behavior, but final-status derivation still treats the authoritative status as the pre-D4 `"pending"` snapshot and falls through to kind-based logic.
> - `snapshot is None` → skip D4, fall through to kind-based logic, log the anomaly.
>
> I would not pick B. Moving D4 into the fall-through branch is semantically cleaner in isolation, but it expands the finalizer rewrite surface and changes the existing line-order contract more than this drift fix needs. A is the smaller and easier-to-prove correction.
>
> Confirm R14-02 exactly as proposed. The important phrase is 'two origins,' and both references should name:
> 1. non-cancel timeout interrupt succeeded via `_WorkerTerminalBranchSignal(reason="timeout_interrupt_succeeded")`
> 2. cancel-capable timeout cancel-dispatch succeeded via `_finalize_turn` Captured-Request Terminal Guard
>
> One extra gate I'd add to yours: `rg \"only via the non-cancel|single-origin|timeout_interrupt_succeeded branch\"` over the spec after the edit, because this is precisely the kind of stale explanatory sentence that has been recurring.
>
> Writing-plans remains blocked until R14 lands and the one-snapshot rule is explicit."

---

## Gotchas

1. **Two re-reads in R13's terminal guard were the literal spec — not a bug in a different file.** The R14 finding was a self-consistency defect within the R13 commit. The fix wasn't "change the code" but "tighten the spec so the code can't be written wrong." This is characteristic of late-cycle scrutiny rounds.

2. **`canceled` has two origins but only one reaches `_finalize_turn`.** Origin 1 (non-cancel timeout interrupt-succeeded) sentinel-bypasses the finalizer. Origin 2 (cancel-capable timeout cancel-dispatch-succeeded) reaches the finalizer with `request_snapshot.status="canceled"` and gets mapped by the terminal guard. Both produce `DelegationJob.status="canceled"`, but via structurally different paths. Any prose that describes canceled must be explicit about which origin it refers to.

3. **D4 pre-existed Packet 1.** The D4 carve-out at `delegation_controller.py:1467-1470` is legacy — it unconditionally calls `update_status(request_id, "resolved")` before status derivation. Under synchronous-decide (pre-Packet-1), this was harmless: the decide had just been called, so writing "resolved" was idempotent with what was already true. Under async-decide (Packet 1), D4 becomes dangerous because it can overwrite the worker's earlier `canceled` write. R14's D4 gate makes the legacy write conditional without fully relocating it.

4. **The phrase "re-read" is ambiguous in context.** Pre-R14, the spec used "re-read" to mean "read the store (as opposed to the passed-in `captured_request` struct)." R14's one-snapshot rule uses "re-read" to mean "second read after the snapshot." Post-R14, uses of "re-read" that remain are either (a) describing `start()`'s distinct flow (not the finalizer) or (b) explicit anti-pattern references ("NOT a post-D4 re-read"). Any new prose that uses "re-read" without qualification risks confusion.

5. **Test bullet count can drift silently.** The spec has five `Tests to add:` blocks across sections (at :560, :905, :1278, :1730, :1826). Only the one at :1826 is for §_finalize_turn Captured-Request Terminal Guard. Counting test bullets requires scoping the range explicitly (e.g., between the guard's header and §Rejection reasons).

6. **`git status` was clean before I started this session's edits** — the only modified file after R14 edits was the spec itself, so the commit hash of the R14 edits is reliable. If the branch had accumulated other stray edits, the commit message would need to be careful about scope.

7. **The `rg "re-read"` sweep showed 16 matches after R14 edits.** Triage confirmed all were legitimate (describing `start()`'s flow or explicit anti-patterns). A naive "zero matches" gate would be wrong — the right gate is "no two-reads-in-finalizer vocabulary remains," which is narrower.

---

## Conversation Highlights

### User's R14 /copy scrutiny (artifact delivered mid-session)

Two findings, verdict "Minor revision":

> **R14-01 (P2):** "D4 pending fallback contradicts the terminal-guard algorithm. The spec says `pending` or missing request records fall through to the existing kind-based escalation logic, but the D4 suppression section says the legacy `update_status(request_id, \"resolved\")` still runs for the pending case. The callsite summary then re-reads the request for status derivation, so an anomalous pending request becomes `resolved` before the guard evaluates it and maps to `completed`/`unknown`, not the promised fallback."

> **R14-02 (P2):** "Canceled origin text is now stale. This still says `canceled` comes only from the non-cancel timeout interrupt-success branch, but R13 added a second `DelegationJob.status=\"canceled\"` origin: cancel-capable timeout with successful cancel dispatch via the finalizer guard."

> "Required Changes Before This Is Credible: Clarify `_finalize_turn` with one authoritative status snapshot: terminal guard and pending fallback must be based on the same pre-D4 read, or D4 must move after final-status derivation. Then update the `canceled` origin prose at lines 1336 and 1809 to include cancel-capable timeout cancel-dispatch-success."

### My A/B proposal back

Laid out Option A (single snapshot) vs Option B (defer D4) in a table, recommended A for three reasons: smaller textual delta, collapses to one read (easier invariant to prove), preserves existing D4 location in code.

### User's lock-in (with invariant strengthening)

Key addition beyond my proposal: "only one request-status read may participate in final-status derivation. Later reads can still exist for return-shape hydration if needed, but they must not feed the terminal-guard decision."

This converted the rule from a procedural "read it once" to a structural invariant: "the snapshot is the authority." The shift was load-bearing — it required the 6th test bullet (one-snapshot invariant enforcement) that my initial proposal didn't include.

### User's gate prescription

> "One extra gate I'd add to yours: `rg \"only via the non-cancel|single-origin|timeout_interrupt_succeeded branch\"` over the spec after the edit, because this is precisely the kind of stale explanatory sentence that has been recurring."

The word "recurring" is informative — it signals this pattern has shown up in prior rounds.

### My closing summary line

> "Writing-plans remains blocked per your lock-in. Ready for R15 review, or — if this cycle closes — a go-ahead to invoke `superpowers:writing-plans` on the 2438-line spec."

Mirrored the prior rounds' closing-line pattern and deferred forward progress to user direction.

---

## User Preferences

**Invariants over procedural rules:** User consistently strengthens my "do X at step N" proposals into "X is the authority." R14's "only one request-status read may participate in final-status derivation" is this pattern in action — my A proposal was procedurally correct; the user's lock-in added the structural invariant.

**Smaller-delta corrections over bigger rewrites:** User quote: "A is the smaller and easier-to-prove correction." Explicit preference for minimizing change surface when both options achieve correctness.

**Grep-enforceable gates:** User provides concrete `rg` patterns for post-edit verification. These are runnable in a commit-hook or CI context. User quote about R14-02 gate: "this is precisely the kind of stale explanatory sentence that has been recurring."

**Writing-plans blocking as durable policy:** Across multiple rounds, user has blocked writing-plans invocation behind specific gate conditions. This is a standing policy, not a one-off. Gates so far: "R13 lands + three gates pass" (success-path hole closed), "R14 lands + one-snapshot rule explicit."

**Named subsection conventions:** User supplied the exact name "`_finalize_turn` Captured-Request Terminal Guard" for R13's new subsection. Explicit naming preference.

**Precision of phrasing:** For R14-02, user required "two origins" as the exact phrase and specified both origin names must appear. Not paraphrasable.

**"Minor revision" verdict means targeted fixes, not skip:** R14's verdict was "Minor revision" but the user still required concrete edits and a commit before considering the cycle unblocked. "Minor" describes severity, not bypassability.

**Round cycle rhythm:** User delivers /copy → expects A/B-framed proposal back → locks in with constraints → expects edits + gate sweep + commit + summary. Breaking this rhythm (e.g., executing without lock-in, or skipping summary) would be a divergence from observed pattern.

---

## Rejected Approaches

### Option B for R14-01 (defer D4 into fall-through branch)

> **Tried (considered, not executed):** Re-read request only at terminal guard; if terminal use mapping; if pending fall through to kind-based logic, D4 runs inside that fall-through branch body.
> - **Failed because:** User quote: "Moving D4 into the fall-through branch is semantically cleaner in isolation, but it expands the finalizer rewrite surface and changes the existing line-order contract more than this drift fix needs." D4's line-location contract at `delegation_controller.py:1467-1470` is referenced in multiple spec touch points; relocating it would cascade edits across those references.
> - **Learned:** When two options achieve correctness, the one that preserves prior structural references wins. "Line-order contract" is a first-class concern in a spec that's heavily cross-referenced.

### Strengthening D4 suppression test to cover one-snapshot invariant

> **Tried (considered, not executed):** Fold the new "One-snapshot invariant enforcement" test into the existing "D4 blind-write suppression" test.
> - **Failed because:** These are two distinct invariants that should fail independently. D4 suppression is about "don't overwrite worker's write"; one-snapshot is about "don't re-derive from a post-D4 state." Bundling would obscure which invariant failed when a future regression broke one.
> - **Learned:** Invariant tests should be orthogonal where possible. A failing test that pinpoints the broken invariant saves debugging time.

### Leaving R13 diagram annotations at :991 and :1085 with "re-reads the request" vocabulary

> **Tried (considered, briefly left):** Argue that "re-reads" in the diagram annotations was semantically accurate enough to leave.
> - **Failed because:** Post-R14, "re-read" in finalizer context implies a second read that violates the one-snapshot rule. Leaving the vocabulary would create drift between the rule (single snapshot) and the diagrams (which still suggest a re-read mental model).
> - **Learned:** When a load-bearing invariant is added, downstream documentation that uses the old vocabulary needs to align — even if the old vocabulary was technically correct in isolation.

---

End of handoff.
