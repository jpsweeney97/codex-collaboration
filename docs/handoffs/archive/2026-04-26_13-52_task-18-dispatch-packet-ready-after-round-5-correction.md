---
date: 2026-04-26
time: "13:52"
created_at: "2026-04-26T17:52:33Z"
session_id: 2a2721e6-509e-4e97-bc84-1448b094b8c3
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-26_13-26_task-18-convergence-map-dispatch-ready.md
project: claude-code-tool-dev
branch: feature/delegate-deferred-approval-response
commit: c5829049
title: "Task 18 dispatch packet ready after Round-5 W17/:2400 correction"
type: handoff
files:
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-dispatch-packet.md
  - docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-convergence-map.md
  - packages/plugins/codex-collaboration/server/delegation_controller.py
---

# Task 18 dispatch packet ready after Round-5 W17/:2400 correction

## Goal

**Bigger picture:** Phase G Task 18 closes the deferred-approval-response Packet 1 mechanism layer. Task 18 rewrites `decide()` post-validation block at `delegation_controller.py:2560-2675` for the `reserve()` + journal-intent + `commit_signal()` two-phase reservation protocol per spec §Transactional registry protocol (`design.md:250-345`). This is the second and final task of Phase G; Task 17's `start()` rewrite already landed at commit `c5829049`.

**Stakes:** Task 18 closes 12 Bucket B retention tests inherited from Task 17, dispositioned as 3 close (Mode A defer mechanism-only) + 3 DELETE (obsolete CDFE per L11) + 6 RECLASSIFY to new G18.1 carry-forward (finalizer-dependent — Task 19 owns spec §1738-1808 Captured-Request Terminal Guard). Mechanism-level Bucket B closes; finalizer-derived test surface defers to Phase H.

**Trigger:** User loaded prior handoff (`task-18-convergence-map-dispatch-ready.md`) with convergence map at 551 lines after 4 review rounds + wording pass. This session drafted the dispatch packet (`task-18-dispatch-packet.md`), surfaced and corrected one P1 W17/`:2400` mechanical-impossibility via Round-5, applied a P3 metadata fix, and reached dispatch-ready state.

**Project arc context:** T-20260423-02 Packet 1 active development. Following Task 18: implementer dispatch in fresh session via `task-18-implementer` agent (sonnet, `superpowers:subagent-driven-development`) → spec reviewer → code-quality reviewer → 1+1+1 anticipated commit chain (feat + fix + docs) → Phase G CLOSES → Phase H Task 19 begins (`_finalize_turn` Captured-Request Terminal Guard rewrite, with G18.1 pre-authorizations to inherit verbatim).

## Session Narrative

**Starting state:** Loaded checkpoint with branch `feature/delegate-deferred-approval-response` @ `c5829049`, 4 commits ahead of main. Untracked working artifacts: `task-18-convergence-map.md` (551 lines, dispatch-ready per prior handoff). Pre-existing carry-forward: G17.1 (9 F16.2 Bucket B), RT.1 (`runtime.py:270` Pyright issue), proposed TT.1 (`_FakeControlPlane` Pyright issues at multiple lines).

**Step 1 — Load + offer continuation:** Read prior handoff and presented summary. User offered "Continue with drafting the Task 18 dispatch packet?" User confirmed.

**Step 2 — Read sources for packet drafting:** Parallel read of Task 17 dispatch packet (364 lines, structural precedent), Task 18 convergence map (551 lines, content to inline), plus file size check on plan body and carry-forward. Took the cite-vs-inline tradeoff position: Task 17 precedent cites the convergence map as binding authority and only inlines the highest-leverage CRITICAL sections — chose this pattern over verbatim 551-line inline. Verbatim would have pushed packet to ~890 lines with no functional benefit since the implementer reads convergence map first as Authority source #1.

The cite-vs-inline framing required reinterpreting the user's prior open question ("Inline vs cite for convergence map in dispatch packet? Task 17 precedent inlines."). On closer reading of Task 17 packet, "inline" in the user's context meant inline-the-criticals-not-inline-everything. Task 17 packet's Authority source #1 cites the convergence map as a separate file with a list of what it contains (live anchors, locks, watchpoints, branch matrix, per-test triage, out-of-scope, acceptance criteria), then has 5 inline CRITICAL sections (L4 exhaustive match w/ skeleton, L8 signal-then-raise, L6 constant rename, W4 fictional fixtures, W5 hang verification). I extended this for Task 18 to 8 CRITICAL sections reflecting the larger scope.

**Step 3 — Draft packet (469 lines, 8 CRITICAL sections):** Wrote the packet end-to-end in one Write call. Structure: frontmatter + agent dispatch block + Implementer Prompt (Mission, 7 Authority sources with pre-read guard, 8 CRITICAL sections, Plan-pseudocode known issues, Code/Tests/Closeout-docs acceptance summaries, Commit shape, Reporting contract, Boundaries, Mid-task questions, Begin) + Post-implementer review chain.

CRITICAL sections in deliberate order (most error-prone first per user's "concise and impossible to miss" emphasis on L9 test #3):
1. L9 test #3 wrapper protocol (line 57 — first; user-flagged)
2. L4 Path A mandatory + 6-row payload mapping
3. L7 rollback boundary (highest confusion risk)
4. L10 constant rename (mechanical surgery)
5. L11 + L12 + W18 process precedent
6. L14 commit_signal bare
7. W4 no fictional fixtures
8. W14 no signal_internal_abort in decide()

**Step 4 — Self-audit against pre-dispatch checklist (16 items):** Walked through each item. All covered. Three deliberate cite-not-inline choices flagged for user review: (a) L13 not a CRITICAL section (discretionary by design); (b) per-test triage table not inlined verbatim (Task 17 precedent); (c) G18.1 record not inlined verbatim (closeout-docs deliverable). Presented to user with offer for review.

**Step 5 — User /copy review round 1 (P1):** User found one P1 dispatch blocker via /copy review: "W17 invariant is impossible without violating W2." Live grep showed `:2400` is inside `_finalize_turn` body (`:2324-2430`), not inside the deleted `decide()` approve block (`:2606-2675`). Convergence map's live-anchors row had wrongly classified `:2400` as "Legacy `DelegationEscalation` construction site (DELETE with approve block)." Deleting `:2400` would violate W2 (which forbids `_finalize_turn` body edits); preserving it would leave the grep at `2`, violating the convergence map's W17 invariant claim of `1`. Internally contradictory dispatch contract.

**Pivot moment:** I had assumed `:2400` was inside the approve block based on the convergence map's row classification. User showed that grep-style verification confirms a symbol exists at a line but does NOT confirm which enclosing function owns it. The convergence map's L2 said "post-validation block at `:2560-2675`" — `:2400` is OUTSIDE that range, which by itself was a structural inconsistency the row should have flagged. 4 prior review rounds missed this because reviewers (including me) trusted the row's classification.

User's recommended fix: convergence-map correction PLUS packet correction (because the packet names the convergence map as binding authority — leaving the convergence map uncorrected would let the implementer inherit the impossible contract from Authority source #1).

**Step 6 — Verify live code:** Ran `rg -n "DelegationEscalation\(" delegation_controller.py` and `rg -n "^    def [a-zA-Z_]+" delegation_controller.py | head -40`. Confirmed `:837` (Task 17 Parked-arm) and `:2400` (inside `_finalize_turn`) are the only two construction sites. Confirmed function order: `_finalize_turn` def at `:2324`, `_reject_decision` at `:2431`, `decide()` at `:2447` — places `:2400` squarely inside `_finalize_turn`.

**Step 7 — Apply Round-5 corrections (convergence map + packet):**
- Convergence map: 5 substantive edits + new Round-5 addendum (~15 lines). Top revision marker extended; live-anchors row reclassified; W17 watchpoint rewritten; Acceptance criteria W17 invariant grep changed from `1` to `2`; "No edits to" line made `:2400` mention explicit; Round-5 addendum appended after Round-4 with P1 description + corrections list + why-the-gap-survived + future-prevention pattern. Convergence map grew 551 → 566 lines.
- Packet: 5 edits. Mission paragraph removed `:2400` from "legacy synchronous flow" list and added explicit PRESERVED note; Code acceptance "No edits to" bullet made `:2400` explicit; "Legacy DelegationEscalation DELETED" bullet REMOVED; W17 invariant grep changed from `1` to `2`; Reporting contract W17 grep expected value updated; Boundaries "NO touches to `:837`" rewritten to enumerate both sites. Packet shrunk 469 → 468 lines (1-line net change).

**Step 8 — User /copy review round 2 (P3):** User found one P3 cosmetic finding: packet's authority-source description at line 33 still said "551 lines after 4 review rounds + wording pass" — stale relative to the post-Round-5 566-line state. Not a dispatch blocker (substantive corrected wording is present later in packet) but worth fixing because line 33 is inside the implementer's pre-read authority block.

**Step 9 — Apply P3 fix:** Two updates. Packet line 3 (frontmatter): added "then a Round-5 packet-review correction landed the W17/`:2400` mechanical-impossibility fix — both artifacts updated together." Packet line 33: "551 lines after 4 review rounds + wording pass" → "566 lines after 5 review rounds + wording pass; Round-5 added the W17/`:2400` mechanical-impossibility correction." Verified packet line 59's "4 review rounds" reference is intentionally retained (it's about the L9 worker-blocking pattern stabilizing in round-4; round-5 was a different correction).

**Step 10 — User declared dispatch-ready:** User's final review found "Final targeted check passes" with metadata coherent across packet line 3 / line 33 / line 59, file counts matching (468 / 566), W17 consistently `2`. Decision: "proceed with implementer dispatch in a fresh session. I do not recommend further pre-dispatch review unless you want a separate non-blocking copyedit pass." User then invoked /save.

## Decisions

### Decision: Cite convergence map (Task 17 precedent) instead of verbatim 551-line inline

- **Driver:** User's open question from prior handoff: "Inline vs cite for convergence map in dispatch packet? Task 17 precedent inlines. Lean toward inline per precedent." Closer reading of Task 17 packet showed it CITES the convergence map as Authority source #1 and only INLINES the highest-leverage CRITICAL sections — not verbatim 551-line inline. So "inline" in the user's note meant inline-the-criticals, not inline-everything.
- **Rejected:** Verbatim 551-line inline. Would have pushed packet to ~890 lines with no functional benefit since implementer reads convergence map first.
- **Rejected:** Cite-only with NO inline (just file references). Would have left the highest-leverage locks invisible at packet read time; implementer would have to context-switch to convergence map for each lock.
- **Implication:** Packet is 468 lines instead of ~890. Implementer reads convergence map first (Authority source #1), then encounters 8 CRITICAL sections in the packet that surface the most error-prone locks inline.
- **Trade-offs:** If convergence map and packet diverge (as happened in Round-5), both must be corrected in lock-step. Mitigated by treating convergence map as binding and packet as derivative.
- **Confidence:** High (E2) — Task 17 precedent is concrete, user's "lean toward inline" guidance was directional.
- **Reversibility:** High — could fold convergence map content inline if review surfaces issues.
- **Change trigger:** If implementer reports having to flip back-and-forth to the convergence map mid-implementation, future packets should inline more material.

### Decision: Order CRITICAL sections by error-proneness (L9 test #3 first), not file order

- **Driver:** User's prior-session note: "keep L9 test #3's wrapper protocol concise and impossible to miss in the packet — it's the most implementation-sensitive test mechanic." 4 review rounds were needed to get the L9 test #3 worker-blocking mechanism right; other locks (L4, L7) are mechanically straightforward once spec authority is consulted.
- **Rejected:** File-order arrangement (L1 → L4 → L7 → L9 → L10 → L11 → L12 → L13 → L14). Would have put L9 in mid-pack, easy to skim.
- **Implication:** Implementer reading top-to-bottom encounters the most error-prone mechanism first while attention is fresh.
- **Trade-offs:** Departs from Task 17 packet's order (which was approximately file-order). User accepted in dispatch-ready review.
- **Confidence:** High (E2) — explicit user guidance + 4-round history demonstrating L9 sensitivity.
- **Reversibility:** Trivial — re-order CRITICAL sections.
- **Change trigger:** None; order is robust to packet revisions.

### Decision: Apply P1 corrections to BOTH convergence map and packet (not just packet)

- **Driver:** User's open question in /copy review: "Do you want to treat this as a dispatch-packet-only correction, or as a convergence-map correction plus packet correction? My recommendation is convergence-map correction plus packet correction, because the dispatch packet names the convergence map as binding authority."
- **Rejected:** Packet-only correction. Would leave the convergence map's live-anchors row + W17 watchpoint internally contradictory; implementer reads convergence map FIRST as Authority source #1, before encountering the packet's corrected wording.
- **Implication:** Convergence map gets a Round-5 revision marker + addendum; chronology preserved per supersession-marker pattern (extends 4-round precedent).
- **Trade-offs:** More edits (5 substantive + addendum vs ~3 packet edits). Convergence map grew 551 → 566 lines. Provenance chain stays intact.
- **Confidence:** High (E2) — user explicitly recommended this approach with reasoning.
- **Reversibility:** High — could revert if user disagrees with addendum scope.
- **Change trigger:** None expected.

### Decision: Round-5 addendum follows supersession-marker pattern (4-round precedent extended)

- **Driver:** Convergence map already had 4 review-round addenda chained chronologically. User's prior preference: "keep it. It is useful, and it explains why the task narrowed. I would not trim it before dispatch." Same principle applies to round-5 — preserve chronology with explicit supersession.
- **Rejected:** Rewrite original live-anchors row in place to remove "DELETE with approve block" claim. Would lose chronological history; reviewers could not see what was changed and why.
- **Rejected:** Skip the addendum; just fix the row. Would leave no record of the structural-defect class for future-task referencing.
- **Implication:** Round-5 addendum includes "Pattern for future convergence maps" — every "DELETE" row's line number must fall inside an explicit deletion range named by some lock. Future-task referencing benefit.
- **Trade-offs:** ~15 more lines in convergence map. Negligible vs the value of the chronological record.
- **Confidence:** High (E2) — pattern is established; user explicitly approved chronology preservation in round-1 of the convergence map review.
- **Reversibility:** High — addendum can be removed if doc is later flattened.
- **Change trigger:** N/A — process precedent.

### Decision: P3 metadata fix updates packet line 3 + line 33; line 59 stays unchanged

- **Driver:** User flagged stale "551 lines after 4 review rounds" reference in packet line 33 (Authority source #1 description). Line 3 (frontmatter) had similar issue. Line 59 (L9 test #3 CRITICAL) mentions "4 review rounds" in context of worker-blocking pattern stabilization — that's historically accurate, not stale.
- **Rejected:** Update line 59 to "5 review rounds." Would be misleading because round-5 was about W17/`:2400`, not L9 worker-blocking. The L9 worker-blocking mechanism stabilized in round-4 and is unchanged by round-5.
- **Implication:** Both contextually accurate "4 review rounds" mentions (line 3 historical narrative; line 59 worker-blocking history) preserved; only the stale Authority-source-description count updated.
- **Trade-offs:** None — surgical edit.
- **Confidence:** High (E2) — user explicitly limited scope to line 33 + suggested line 3.
- **Reversibility:** Trivial.
- **Change trigger:** None.

## Changes

### Files modified this session

**`docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-dispatch-packet.md`** (CREATED, 469 → 468 lines after Round-5 fix; UNTRACKED)

Initial draft — 469 lines. Round-5 corrections — 5 edits, net −1 line. P3 metadata fix — 2 edits, length-neutral.

Specific surgery:
- Frontmatter line 3 + Authority source #1 description line 33: updated to reflect Round-5 correction
- Mission paragraph (line 27): removed `:2400` from "legacy synchronous flow" list; added explicit BOTH-sites-PRESERVED note
- Code acceptance summary "No edits to" bullet: made `:2400` mention explicit (W2-protected; inside `_finalize_turn` body `:2324-2430`)
- Code acceptance summary "Legacy DelegationEscalation DELETED" bullet: REMOVED
- Code acceptance summary "W17 invariant" line: expected grep count `1` → `2`; both protected sites enumerated
- Reporting contract W17 grep expected value: `1` → `2` with both protections cited
- Boundaries — "NO touches to `:837`" → "NO touches to either site" — both `:837` and `:2400` enumerated

**`docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-convergence-map.md`** (UPDATED, 551 → 566 lines; UNTRACKED)

5 substantive edits + new Round-5 addendum (~15 lines):
- Top revision marker (line 3): extended with round-5 mention
- Live anchors table row at `:2400` (line 27): "Legacy `DelegationEscalation` construction site (DELETE with approve block)" → "`_finalize_turn` `DelegationEscalation` needs-escalation return site (DO NOT MODIFY per W2 — Task 19 territory)"
- W17 watchpoint description (line 278): rewritten to enumerate both sites; legacy-approve-block-no-DelegationEscalation note; grep returns `2` post-Task-18
- Acceptance criteria → Code "W17 invariant" line (line 400): expected `1` → `2` with both protections enumerated
- Acceptance criteria → Code "No edits to" line (line 398): `:2400` mention made explicit (W2 protection)
- Round-5 addendum appended after Round-4 addendum (lines 553-566): P1 description + corrections list + why-the-gap-survived + future-prevention pattern

### Files NOT modified this session

- `delegation_controller.py` (read-only verification of `:2400` location and function boundaries)
- `phase-g-public-api.md` (cited as Authority source #6 in packet; not modified)
- `carry-forward.md` (closeout-docs commit will update; not in scope this session)
- Spec at `2026-04-23-deferred-approval-response-design.md` (cited as Authority sources #2-#5 in packet; not modified)

## Codebase Knowledge

### Live `DelegationEscalation(` construction sites at HEAD `c5829049`

Two sites total. Both PRESERVED by Task 18:

| File:line | Enclosing function | Protection |
|---|---|---|
| `delegation_controller.py:837` | `_dispatch_parked_capture_outcome` (Task 17 helper) | W17 (explicit watchpoint) |
| `delegation_controller.py:2400` | `_finalize_turn` body (def at `:2324`, ends before `_reject_decision` at `:2431`) | W2 (forbids `_finalize_turn` body edits) |

**Critical implication for Task 18:** post-Task-18 `grep -c "DelegationEscalation("` returns `2` (UNCHANGED from pre-Task-18). The legacy `decide()` approve block being deleted (`:2606-2675`) contains NO direct `DelegationEscalation(` construction — the legacy approve path returned via `_execute_live_turn`'s indirect dispatch.

### Function order in `delegation_controller.py` near the Task 18 surface

Verified via `rg -n "^    def [a-zA-Z_]+"`:

| Function | Line |
|---|---|
| `_finalize_turn` def | `:2324` |
| `_reject_decision` def | `:2431` |
| `decide` def | `:2447` |
| `recover_startup` def | `:2677` |

So `_finalize_turn` body spans `:2324-2430`. `:2400` falls squarely inside it.

### Round-5 future-prevention pattern (recorded in convergence map addendum)

When a row in a live-anchors table claims a line should be DELETED and falls outside an explicit "deletion range," verify two things:
1. The line is INSIDE the deletion range (not just numerically close).
2. No other lock or watchpoint protects the line.

The Round-5 defect surfaced because L2 said "post-validation block at `:2560-2675`" but the live-anchors row claimed `:2400` was DELETED — `:2400` is OUTSIDE that range, a structural inconsistency the row should have flagged at first construction.

### Convergence map structural anatomy (post-Round-5)

The Task 18 convergence map (566 lines) is organized as:

| Section | Approximate lines | Purpose |
|---|---|---|
| Top revision marker (frontmatter prose) | 1-3 | Round chronology with supersession trail |
| Scope (Option Y narrow) | 5 | Task 18 vs Task 19 boundary |
| Authority order (9 layers) | 7-17 | Spec > plan > carry-forward > live code |
| Live anchors table (~30 rows) | 19-54 | File:line citations, verified at HEAD |
| Locks L1-L14 | 56-230 | Binding positive scope |
| Watchpoints W1-W18 | 232-281 | Binding negative scope |
| Branch matrix (10 rows) | 283-296 | Decision × kind × outcome |
| Per-test triage (4 sub-tables) | 298-338 | Bucket B / G18.1 / DELETE / new acceptance / F16.1 |
| G18.1 carry-forward record | 340-367 | Pre-authorizations Task 19 inherits |
| Out-of-scope table | 369-383 | Plan/spec citations |
| Acceptance criteria (Code/Tests/Closeout-docs) | 385-429 | Mandatory checkboxes |
| Pre-dispatch checklist | 431-456 | 16 items the packet must cover |
| Commit shape | 458-466 | 1+1+1 anticipated |
| Carry-forward expectations | 468-485 | Net change matrix |
| Pre-dispatch warnings | 489-498 | High-risk loci callouts |
| Restructure Record + Round 2-5 addenda | 500-566 | Chronological review history |

This anatomy is reusable for Task 19's convergence map.

### Task 17 dispatch packet structure (the precedent followed)

Task 17 packet (364 lines) demonstrated the cite-and-call-out pattern:
- Frontmatter + agent dispatch block (Python invocation)
- Implementer Prompt: Mission, Authority sources (READ IN THIS ORDER) with pre-read guard, CRITICAL sections (L4 exhaustive match w/ skeleton, L8 signal-then-raise, L6 constant rename, W4 fictional fixtures, W5 hang verification), Plan-pseudocode known issues, Code/Tests/Closeout-docs acceptance summaries, Commit shape, Reporting contract, Boundaries, Mid-task questions, Begin
- Post-implementer review chain (sequential: spec reviewer → code-quality reviewer → closeout-fix → closeout-docs)

Task 18 packet (468 lines) extends this with: 8 CRITICAL sections (vs Task 17's 5); L9 test #3 first per user emphasis; explicit BLOCKED protocol for non-pre-authorized renames/deletions/reclassifications.

## Context

**Mental model:** A dispatch packet is a layered instruction document where the convergence map is binding authority and the packet is dispatch-time briefing. The packet's job is to (a) brief the implementer at dispatch time, (b) call out the highest-leverage / most-error-prone locks inline so they can't be missed, (c) provide the reporting contract and BLOCKED protocol. The packet does NOT duplicate binding authority — when packet and convergence map disagree, convergence map wins and the packet must be corrected to match.

**Core insight:** Round-5 surfaced a class of defect that grep-style verification cannot catch: a symbol's enclosing function ownership. `rg -n "DelegationEscalation\("` confirms the symbol exists at a line, but doesn't confirm which `def ...` owns it. Reviewers (across 4 prior rounds and my own self-audit) trusted the live-anchors row's classification "Legacy ... DELETE with approve block" because grep verified the symbol exists at `:2400`. The actual enclosing function order — `_finalize_turn` def at `:2324`, `_reject_decision` at `:2431`, `decide()` at `:2447` — places `:2400` inside `_finalize_turn`. The next review pass (the user's) caught it by running both queries and reading surrounding context.

**Framing analogy:** Multi-round review on a complex spec is layered fault-injection — each layer has its own structural defect modes. Round-1 caught spec-vs-plan scope conflicts. Round-2 caught threading/Event semantics. Round-3 caught validation-order races. Round-4 caught Python mock-patching binding rules. Round-5 caught grep-vs-enclosing-function ownership. Each round addressed an implicit assumption from the prior round. The dispatch is ready when each layer's failure modes are explicitly documented and the test contract avoids each one.

## Learnings

### Patterns

- **Cite-and-call-out for binding authority docs:** When a binding authority doc is large (>400 lines) and an instruction doc derives from it, cite the authority and inline only the highest-leverage / most-error-prone material as CRITICAL sections. Avoid verbatim inline of binding authority — keeps derivative docs lean and prevents subtle drift between authority and derivative.
- **Order CRITICAL sections by error-proneness, not file order:** When a doc has multiple inline-promoted "CRITICAL" sections, order them by historical error-rate (how many review rounds were needed to land each correctly), not by source file order. Most error-prone first while reader attention is fresh.
- **Supersession-marker pattern extends N rounds:** Each new review round's addendum chronologically chains; stale claims in earlier rounds get in-place "superseded by round-N+1" cross-refs. Round-5 extending Round-4 extending Round-3 etc. is robust as long as each addendum cites what it's correcting.
- **Apply P1 corrections to BOTH binding authority + derivative when defect is in authority:** When a P1 surfaces in a derivative doc but the root cause is in the binding authority, correct BOTH. Otherwise the implementer reading authority FIRST inherits the impossible contract before reaching the derivative's correction.

### Gotchas

- **`_finalize_turn` body extends from `:2324` to `:2430` at HEAD `c5829049`.** `:2400` (the second `DelegationEscalation(` site) falls inside it, NOT inside `decide()`. Anyone touching this surface should verify enclosing function before classifying a line for deletion.
- **Grep-style verification cannot catch enclosing-function ownership.** `rg -n "<symbol>"` confirms a line exists; it does NOT confirm which function/class owns it. For deletion/protection decisions, ALSO check the surrounding `def ...` / `class ...` boundaries.
- **A "DELETE" row falling outside an explicit deletion range is a structural defect.** The convergence map's L2 said "post-validation block at `:2560-2675`" — `:2400` was outside, which by itself was a smoking gun the row's classification was wrong.

### Conventions

- Convergence-map review rounds preserve chronology via Restructure Record + addenda chain. Each addendum has explicit supersession markers for stale earlier claims.
- Dispatch-packet revision markers (frontmatter line 3 + Authority-source line 33) cite the binding-authority's revision state to keep implementer pre-read context coherent.
- "Round-N" terminology in convergence-map addenda is sequential and non-skipping. Round-5 is the FIFTH review round, regardless of which doc surfaced the defect (in this case, the packet review surfaced a convergence-map defect; addendum still numbered Round-5).

### Connections

- Packet Authority source #1 (BINDING) → convergence map → Round-5 addendum chain → Restructure Record
- Packet CRITICAL sections (L9 #3, L4, L7, L10, L11+L12+W18, L14, W4, W14) → convergence map locks/watchpoints → spec sections at `design.md:250-345, 1646-1702, 1738-1808`
- Packet Reporting contract → convergence map Acceptance criteria → live-code grep audits

## Next Steps

1. **Dispatch implementer in fresh session.** Use the agent dispatch block at the top of the packet:
   ```python
   Agent({
     name: "task-18-implementer",
     subagent_type: "general-purpose",
     model: "sonnet",
     description: "Phase G Task 18 decide() rewrite",
     prompt: <<everything in §"Implementer Prompt" of the dispatch packet>>
   })
   ```
   Per user instruction: "proceed with implementer dispatch in a fresh session."

2. **Anticipated implementer DONE/BLOCKED outcomes:**
   - DONE: feat commit + suite output + 5 grep audits + L4 Path A verification artifact + L7a regression evidence + lock conformance summary + W5 hang verification.
   - BLOCKED: most likely on L4 Path A if codex-app-server source is unavailable (proposed scope expansion: "Task 18a: codex-app-server source verification + ground-truth artifact"). Also possible: any test outside L11/L12/the 3 explicit Bucket B unskips appearing to need rename/deletion/reclassification (per W18 BLOCKED protocol).

3. **Sequential review chain after DONE:**
   - Spec compliance reviewer (`general-purpose`, sonnet) — focus on L4/L7/L9 #3/L11/L12/W18.
   - Code-quality reviewer (`pr-review-toolkit:code-reviewer` if available, else `general-purpose` sonnet) — focus on `_build_response_payload` helper + L7 try/except boundary + L9 #3 wrapper mechanism + L7a regression + L10 constant rename text fidelity.
   - User adjudicates between rounds (per `feedback_subagent_driven_development_meaning.md`).

4. **Closeout-fix dispatch (if needed):** Continue the `task-18-implementer` agent via `SendMessage`, NOT a new agent.

5. **Closeout-docs commit (mandatory third commit):** Continue same implementer to write `carry-forward.md` updates (G17.1 closure + Mode A row closure + F16.2 lineage annotation + NEW G18.1 entry verbatim from convergence map + TT.1 formal promotion + RT.1 unchanged) + Phase G Task 18 closeout entry + Verification artifacts section appended to convergence map.

6. **Anticipated commit chain:** 1+1+1 (feat + fix + docs).

7. **Post-Task-18 state:** Phase G CLOSES. Phase H Task 19 begins. F16.1 + RT.1 + TT.1 + G18.1 + F16.2-via-G18.1 are the cross-Phase carry-forward set entering Phase H.

## In Progress

**Status:** Both artifacts dispatch-ready; no implementation begun. Branch unchanged at `c5829049`. Untracked working artifacts pending commit alongside Task 18 closeout-docs (NOT separate commits — bundled with closeout-docs per L1 + closeout-docs acceptance summary).

- **Approach:** Two-read review per round (user /copy paste of code-comment blocks); my role is apply-and-verify Edit cycle. 2 review rounds completed this session (P1 + P3); final user verdict was dispatch-ready.
- **State:** Convergence map at 566 lines (Round-5 addendum complete); packet at 468 lines (Round-5 corrections applied + P3 metadata fix applied). Both internally consistent; W17 grep returns `2`; both `DelegationEscalation(` sites preserved.
- **Working:** All checklist items in convergence map's pre-dispatch checklist covered or addressed. Self-audit complete with 3 cite-not-inline choices flagged and accepted.
- **Not working/incomplete:** Implementer dispatch not yet executed (deferred to fresh session per user instruction). Task 18 acceptance criteria NOT YET VALIDATED against actual implementer output.
- **Open question:** None — user declared dispatch-ready.
- **Next action:** In fresh session, invoke `Agent({name: "task-18-implementer", ...})` with the packet's Implementer Prompt as the prompt body.

## Open Questions

- **L4 Path A verification artifact source.** L4 mandates implementer verifies non-empty RUI approve answers wire shape against App Server. Implementer may report BLOCKED if App Server source unavailable in-scope. Pre-flagged in packet preamble; user may want to pre-empt this by providing the artifact source upfront if known.
- **Test #3 wrapper protocol robustness in implementer's test environment.** The convergence map enumerates 3 rejected blocking patterns; if implementer finds the wrap-`update_status_and_promotion` pattern doesn't propagate to the running worker thread in their test environment, they'd hit a wall. Mitigation in packet: noting the wrap can be applied at controller construction time before worker spawn.
- **Implementer review surface size.** L4 Path A + L7 rollback boundary + L9 #3 wrapper protocol + L10 constant rename + L11 deletions + L12 reclassifications create 6+ precision-sensitive surfaces. Code-quality review may surface 2-4 cleanups. Commit shape may need to flex to 1+2+1 if review surfaces 2 fix categories.

## Risks

- **Dispatch packet revision precedent applies to Task 19 dispatch.** 4 rounds + wording pass + Round-5 on Task 18 convergence map suggests Task 19's convergence map may take 2-4 rounds. Plan time accordingly.
- **L4 Path A BLOCKED is plausible.** App Server source may not be accessible to implementer in-scope.
- **Stale spec line citations.** Convergence map cites `delegation_controller.py:1166, :1187, :1278, :2324, :2400, :2447, :2560-2675` and `resolution_registry.py:209-259` — all HEAD-`c5829049` line numbers. If implementer-feat lands on a different commit base, citations shift. Standard for plan-body line citations across all locks.
- **Round-5 supersession pattern propagation.** Future convergence maps inheriting the Round-5 addendum's "Pattern for future convergence maps" should add the integrity check on first construction, not rediscover it post-review.

## References

### Prior handoffs (chain)

- **Resumed from:** `docs/handoffs/archive/2026-04-26_13-26_task-18-convergence-map-dispatch-ready.md`
- Earlier in chain: `docs/handoffs/archive/2026-04-26_12-46_checkpoint-task-18-convergence-map-2nd-draft-pending-review.md`
- Earlier still: `docs/handoffs/archive/2026-04-26_07-02_phase-g-task-17-dispatch-and-closure.md`

### Active artifacts

- **Dispatch packet (active, untracked):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-dispatch-packet.md` (468 lines)
- **Convergence map (active, untracked):** `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-18-convergence-map.md` (566 lines, post-Round-5)
- **Plan body:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/phase-g-public-api.md:290-538`
- **Carry-forward:** `docs/plans/2026-04-24-packet-1-deferred-approval-response/carry-forward.md` (242 lines pre-Task-18)
- **Spec authority:** `docs/superpowers/specs/2026-04-23-deferred-approval-response-design.md`

### Live code

- `packages/plugins/codex-collaboration/server/delegation_controller.py` @ HEAD `c5829049`
- `packages/plugins/codex-collaboration/server/resolution_registry.py` @ HEAD `c5829049`
- Tests: `packages/plugins/codex-collaboration/tests/test_delegation_controller.py`, `tests/test_delegate_start_integration.py`, `tests/test_handler_branches_integration.py` (untouched per W8)
- New file (Task 18): `packages/plugins/codex-collaboration/tests/test_delegate_decide_async_integration.py`

### Memory entries

- `feedback_bucket_reclassification_requires_blocked.md` (L13 process precedent)
- `feedback_assertion_shape_implementer_discretion.md` (L12 precedent)
- `feedback_subagent_driven_development_meaning.md` (full review chain workflow)

### Task 17 precedent

- `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-17-dispatch-packet.md` (364 lines)
- `docs/plans/2026-04-24-packet-1-deferred-approval-response/task-17-convergence-map.md` (399 lines)

## Gotchas

- **`:2400` is INSIDE `_finalize_turn` body, NOT inside the deleted `decide()` approve block.** W2 protects it. `_finalize_turn` body spans `:2324-2430`.
- **`grep -c "DelegationEscalation(" delegation_controller.py` returns `2` post-Task-18 (UNCHANGED from pre-Task-18).** Both sites preserved: `:837` (Task 17 Parked-arm; W17) and `:2400` (`_finalize_turn` needs-escalation; W2).
- **The legacy `decide()` approve block being deleted (`:2606-2675`) contains NO direct `DelegationEscalation(` construction.** Legacy approve path returned via `_execute_live_turn`'s indirect dispatch, not by directly constructing one inside `decide()`.
- **Packet line 59 ("4 review rounds") intentionally NOT updated to "5 review rounds."** That mention is about the L9 worker-blocking pattern stabilizing in round-4, which is unchanged by round-5 (round-5 was about W17/`:2400`). Updating would be misleading.
- **W3 invariant:** `grep -nF "_WorkerTerminalBranchSignal(reason=" delegation_controller.py | wc -l` returns `6` post-Task-18.
- **L6 invariant:** `grep -n "_decided_request_ids" delegation_controller.py` returns 0 post-Task-18 (4 callsites retired: `:395, :2505, :2627, :2665`).
- **Plan body's `phase-g-public-api.md:498-505` payload-helper code has 2 spec defects:** `"reject"` should be `"decline"`; unconditional `dict(answers or {})` should be `{"answers": {}}` empty-fallback for deny on RUI. L4 binds the spec table; plan body is informative-not-binding.
- **Pre-Task-18 carry-forward state must be intact at dispatch.** G17.1 (9 F16.2 Bucket B), RT.1, proposed TT.1. Closeout-docs disposition tracker must update these (G17.1 retires; F16.2 stays Open via G18.1 lineage; TT.1 formal promotion; RT.1 unchanged).

## Conversation Highlights

User's framing across the 2 review rounds was forensic and precise:

**Round-1 P1 (W17/`:2400` mechanical-impossibility):**
- Comment header: "[P1] W17 invariant is impossible without violating W2"
- Body: "The packet tells the implementer to delete the `DelegationEscalation(` site at `:2400` and expects `grep -c \"DelegationEscalation(\"` to return `1`, but live `delegation_controller.py:2400` is inside `_finalize_turn`, not inside the deleted `decide()` approve block. W2 forbids `_finalize_turn` edits, so this dispatch instruction creates an impossible contract: either the implementer violates W2 to satisfy W17, or preserves W2 and fails the packet's grep. Current live grep returns two sites: `:837` and `:2400`."
- Recommendation: "Minimum repair: In the dispatch packet, remove claims that `:2400` is inside the deleted approve block. Change W17 verification from expected `1` to expected `2`. State explicitly that both remaining construction sites are allowed after Task 18."
- Open question (with recommendation): "Do you want to treat this as a dispatch-packet-only correction, or as a convergence-map correction plus packet correction? My recommendation is convergence-map correction plus packet correction, because the dispatch packet names the convergence map as binding authority."

**Round-2 P3 (stale Authority-source description):**
- Comment header: "[P3] Packet still advertises the old convergence-map revision"
- Body: "The packet now points to a Round-5-corrected convergence map, but this authority-source summary still says the map is 551 lines after 4 review rounds plus wording pass. The live map is now 566 lines and includes the Round-5 addendum that fixes the W17/:2400 impossibility. This is not a dispatch blocker because the substantive corrected W17 wording is present later in the packet, but the first authority-source description should be updated so the implementer knows they are reading the Round-5-corrected authority."
- Final verdict: "Final targeted check passes. ... Decision: proceed with implementer dispatch in a fresh session. I do not recommend further pre-dispatch review unless you want a separate non-blocking copyedit pass. Save a handoff."

## User Preferences

- **Multi-round review with /copy paste:** User prefers structured code-comment blocks with file:line citations, priority levels (P1/P2/P3), and confidence scores. Pattern: paste review → I apply edits → next paste with new round's findings.
- **Convergence-map + packet corrections in lock-step:** User explicitly says "the dispatch packet names the convergence map as binding authority" — when a defect is in the convergence map, correct both. Don't paper over in the derivative.
- **Chronology preservation in docs:** User explicitly wants Restructure Record + addendum chronology. User's prior session quote: "keep it. It is useful, and it explains why the task narrowed. I would not trim it before dispatch." Round-5 addendum extends this principle.
- **Dispatch readiness gating:** User signals dispatchable explicitly with phrase variants like "dispatch-ready" or "proceed with implementer dispatch." Does not greenlight implicitly.
- **Scope discipline within rounds:** User said in prior session: "I would not require another full convergence-map review unless those edits touch more than the cited sentences." Confirmed in this session — the Round-5 substantive correction was treated as a structural change requiring a re-review pass; the P3 metadata fix was treated as wording-only.
- **Architectural precision over speed:** User found a 5th-round residual issue after I (and 4 prior rounds + my own self-audit) had passed the convergence map. Values getting it right over moving to dispatch quickly.
- **Verbatim mechanism specifications:** User pushes for code-grounded line citations rather than vague descriptions. Round-1 P1 cited "live `delegation_controller.py:2400`" + "Current live grep returns two sites: `:837` and `:2400`" — concrete evidence drove the diagnosis.
- **Save-on-dispatch-ready cadence:** User invokes `/save` immediately after declaring dispatch-ready. Pattern observed across both this session and the prior session it resumed from.
- **Priority labeling discipline:** User uses P1/P2/P3 with calibrated meanings. P1 = dispatch blocker (Round-5 W17/`:2400` was P1 because it created an impossible contract). P3 = cosmetic / metadata-only (the stale "551 lines" was P3 because substantive corrected wording was already present in the packet). User explicitly notes when something "is not a dispatch blocker" — that signals the implementer can proceed even if the fix is not yet applied, but the user still wants it fixed for cleanliness.
- **Confidence scoring in /copy reviews:** User attaches confidence values (e.g., `confidence=0.97` on the W17 P1, `confidence=0.92` on the metadata P3). Higher confidence on P1 reflects mechanical certainty (live grep + function boundaries verifiable); lower confidence on P3 acknowledges judgment call about whether metadata staleness rises to "must-fix."

### Patterns observed across multi-round packet review

- **Round count is non-monotonic across artifacts.** The Task 18 convergence map went through 4 review rounds + wording pass before reaching dispatch-ready, then a 5th round triggered by packet review. Task 18 packet went through 2 review rounds (P1 + P3). The "rounds" terminology is sequential but per-artifact; round-N on the convergence map need not correspond to round-N on the packet.
- **Defects can surface across artifact boundaries.** Round-5 on the convergence map was triggered by a defect surfaced during packet review, not by re-reading the convergence map. This argues for treating the dispatch packet review as a final-validation pass on the convergence map, not just a packet-quality pass.

## Rejected Approaches

### Verbatim 551-line inline of convergence map in packet (round-0 — considered, rejected)

- **Tried (considered):** Inline the full 551-line convergence map into the packet for self-contained dispatch.
- **Failed because:** Would push packet to ~890 lines without functional benefit. Implementer reads convergence map first as Authority source #1; verbatim inline duplicates without adding clarity. Task 17 precedent showed cite-and-call-out works.
- **Learned:** "Inline the convergence map" in user guidance meant "inline the highest-leverage CRITICAL sections" not "verbatim full-doc inline."

### Packet-only correction for Round-5 P1 (considered, rejected)

- **Tried (considered):** Fix only the packet; leave convergence map as-is.
- **Failed because:** Convergence map is Authority source #1 — implementer reads it FIRST. Leaving it uncorrected means the implementer inherits the impossible contract before reaching the packet's correction. User explicitly recommended both-artifacts correction.
- **Learned:** When defect is in binding authority, derivative-only correction is insufficient. Apply to both.

### Update packet line 59 to "5 review rounds" (P3 fix scope — considered, rejected)

- **Tried (considered):** Update all "4 review rounds" mentions in packet to "5 review rounds."
- **Failed because:** Line 59 is in the L9 test #3 CRITICAL section and refers to "the convergence map went through 4 review rounds before the worker-blocking pattern was correct." That's historically accurate — the L9 worker-blocking mechanism stabilized in round-4; round-5 was about W17/`:2400`. Changing to "5 review rounds" would misleadingly imply round-5 affected L9.
- **Learned:** "N review rounds" mentions in instruction docs need to be checked for context. Some refer to overall doc state; others refer to specific lock/decision history. Don't blanket-replace.

### Skip the Round-5 addendum; just fix the rows (considered, rejected)

- **Tried (considered):** Edit the convergence map rows in place; skip the addendum to keep doc length down.
- **Failed because:** Loses chronological history; future-task referencing benefit gone; user explicitly approved chronology preservation in earlier rounds.
- **Learned:** Supersession-marker pattern is robust to N rounds. Cost (~15 lines per addendum) is negligible vs the value of the chronological record.
