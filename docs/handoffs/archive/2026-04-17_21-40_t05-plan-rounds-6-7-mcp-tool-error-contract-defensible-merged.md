---
date: 2026-04-17
time: "21:40"
created_at: "2026-04-18T01:40:53Z"
session_id: 2535a7e5-2f0e-4a3f-a944-9dca5ff618b0
resumed_from: "docs/handoffs/archive/2026-04-17_19-39_t05-plan-rounds-4-5-propagation-and-retry-safety.md"
project: claude-code-tool-dev
branch: main
commit: f154c682
title: "T-05 execution-start plan — rounds 6-7 (MCP tool-error contract → Defensible) → merged + pushed"
type: handoff
files:
  - docs/plans/2026-04-17-t05-execution-start-slice.md
---

# T-05 Execution-Start Plan — Rounds 6-7 + Landing (MCP Tool-Error Contract → Defensible → Merged)

## Goal

Close the multi-round scrutiny → revision arc on the T-05 execution-start plan by absorbing rounds 6 and 7 of review, landing the plan to `main`, and publishing to remote. This session was the terminal session of the T-05 planning arc — the first non-revision verdict ("Defensible") arrived in round 7, and the user directed the full landing sequence (A1 polish → B commit+merge → B.1 push → C2 save handoff).

**Trigger.** User sent round-6 scrutiny via `/copy` immediately after session load, citing one finding: the new negative-path test at plan `:3394` asserted `"error" in response1` but the live `McpServer._handle_tools_call` at `mcp_server.py:207-230` wraps tool-call exceptions as `{"result": {"content": [...], "isError": True}}` — no top-level `error` key. The test's load-bearing retry-safety proof would fail on transport-shape mismatch before reaching any actual ordering assertion. Verdict: "Minor revision."

After the fix (3 assertion substitutions + 1 adjacent fold-in at Task 10 E2E), round 7 arrived with verdict "**Defensible**" — no required changes, optional polish flagged (3 `json.loads` sites lacking `isError` guards). User directed full landing: **A1** (apply polish) → **B** (commit + `--no-ff` merge to main + delete merged docs branch) → **B.1** (push to origin) → **C2** (save handoff, start fresh session for execution).

**Bigger picture.** T-05 is the execution-domain foundation for codex-collaboration. The plan is a **4191-line** contract across 11 tasks that a subagent-driven execution pipeline will consume task-by-task. Across 7 review rounds it absorbed defects in descending abstraction order: data shapes (R1) → reader/failure semantics (R2) → integration wiring (R3) → propagation (R4) → proof shape (R5) → protocol-contract alignment (R6) → polish (R7). The multi-round pattern produced textbook convergence — line-count delta decelerated 500 → 499 → 339 → 116 → 125 → 0 → +3 (polish-only), defects-per-round 3 → 2 → 2 → 4+fold → 1 → 1 → 0-required. User established the pattern of per-round verdict + structured scrutiny via `/copy`; this session terminated the pattern on the "Defensible" verdict.

**Success criteria for this session:**

1. ✅ Verify each cited line in round 6 literally against plan + `mcp_server.py` + test precedent before responding.
2. ✅ Confirm user's finding structurally correct AND discover the adjacent Task 10 E2E occurrence (`:3988`) proactively via grep sweep.
3. ✅ Apply 3 mechanical substitutions matching local precedent (`response["result"]["isError"]`), not `.get()` form user tentatively suggested.
4. ✅ Deliver round-6 summary with zero net line change — the strongest convergence signal observed so far.
5. ✅ Absorb round-7 "Defensible" verdict without over-reading it as approval-to-land (verdict ≠ merge directive).
6. ✅ Present A1/A2/A3 × B × C sub-decisions as discrete; recommend sequencing without forcing a choice.
7. ✅ Execute A1 (3 polish guards) after user direction; line count 4188 → 4191 exactly.
8. ✅ Execute B: commit on docs branch (`7f0329ca`) → `--no-ff` merge to main (`f154c682`) → safe branch-delete (`-d`).
9. ✅ Execute B.1: push main to origin — cleanly applied (`bd850302..f154c682`).
10. ✅ Invoke `handoff:save` skill per C2 directive with full synthesis.

All ten met.

## Session Narrative

**Phase 1 — Load prior handoff (~immediate).** `/handoff:load` resolved the 19:39 handoff for the T-05 plan from the active directory; archived to `docs/handoffs/archive/`; state file written at `.session-state/handoff-2535a7e5-2f0e-4a3f-a944-9dca5ff618b0`. Read 973 lines of prior-session context (rounds 4+5 synthesis, 4 anticipated round-6 vectors, Goal/Decisions/Learnings/etc.). Positioning: wait for user feedback per handoff's explicit "next action"; do NOT pre-emptively edit.

**Phase 2 — Receive round-6 scrutiny via `/copy` (~immediate).** User posted a structured scrutiny with **one** finding at High severity:

> "The new Task 8 failure-path test asserts the wrong error envelope."

Cited lines:
- plan `:3382-3394` — `assert "error" in response1`
- `mcp_server.py:207-230` — live tool-error surface is `result.content[0].text = str(exc)` + `result.isError = True`, NOT a top-level `error` object
- plan `:3412` — paired success check also uses wrong envelope

User's argument: the negative-path assertion "does not match the live McpServer tool-error surface" + "violates the stated intent to avoid transport-detail coupling: it still couples to one specific transport shape, just the wrong one." Suggested fix: `response1["result"].get("isError") is True`.

Verdict: "Minor revision."

**Phase 3 — Invoke `superpowers:receiving-code-review` (~30s).** Skill engaged before responding. Core rule: "Verify. Question. Then implement."

**Phase 4 — Verify round-6 finding literally (~3 min, parallel reads).** Three parallel reads:
- plan `:3340-3440` to ground the test (confirmed assertion `assert "error" in response1  # error surface detail intentionally not asserted` at `:3394`)
- `mcp_server.py:195-254` to verify the live error shape (confirmed `_handle_tools_call` at `:207-231` returns `{"result": {"content": [...], "isError": True}}` on exception; no top-level `error` key)
- plan `:3260-3340` for fixture + neighboring test context

Plus verified `handle_request` itself at `:153-167` — top-level `error` is ONLY produced by `_error_response` for method-not-found (JSON-RPC protocol errors). For `tools/call` with a handler exception, the flow is `handle_request → _handle_tools_call → except → result.isError wrapper`.

Plus grepped `isError` across the package: **9 existing test occurrences** in `test_mcp_server.py` established `response["result"]["isError"] is True` (strict subscript) as the canonical local precedent. Five occurrences of the symmetric success check: `"isError" not in response["result"]`.

**Phase 5 — Adjacent-occurrence grep sweep (~1 min).** Ran `"error" in response|"error" not in response` grep across the full plan. **Found 3 matches**, not 2:
- `:3394` (negative-path gate — user-flagged)
- `:3412` (paired success check — user-flagged)
- `:3988` (Task 10 E2E success check — **not** user-flagged)

The `:3988` occurrence is Task 10's E2E busy-path proof. Same defect class. Noteworthy asymmetric failure mode: if a tool error leaked here, the assertion `assert "error" not in response` would PASS (no top-level `error` key on isError responses either), then crash loudly on the next line `content = response["result"]["content"][0]["text"]` → `json.loads(str(exc))` → `JSONDecodeError`. Wrong-place failure, not silent success.

**Phase 6 — Respond with verification + revision-shape options (~2 min).** Structured response:
1. Insight block (3 educational points: MCP's two-layer error protocol, local precedent as authoritative, asymmetric false-gate failure modes)
2. Verification table — 5 rows with literal citations
3. Adjacent occurrence discovery — flagged `:3988`, offered 3 fold-in options (fold / defer / leave)
4. Single revision shape (mechanical substitution — no alternatives)
5. Two decisions needed:
   - Assertion style: `.get("isError")` (user's wording) vs strict `response["result"]["isError"]` (local precedent). Recommended strict.
   - Fold `:3988`? Recommended yes.
6. Scope cap + hold-until-decision.

**Phase 7 — User decisions via `/copy` (~2 min).** User confirmed both recommendations via structured scrutiny:
- Strict subscript: "Use strict subscript, not `.get()`. Reason: that matches both repo precedent and the actual contract in mcp_server.py:221. A missing key should fail loudly."
- Fold `:3988` now: "Same defect class, same fix shape, near-zero scope cost. Deferring it just invites another round on an already-understood propagation bug."

Verdict: "Minor revision."

**Phase 8 — Execute round-6 revision (~3 min, 3 parallel Edits + verification).** Three Edit calls in parallel (each `old_string` unique):
- `:3394`: `assert "error" in response1  # error surface detail intentionally not asserted` → `assert response1["result"]["isError"] is True`
- `:3412`: `assert "error" not in response2` → `assert "isError" not in response2["result"]`
- `:3988`: `assert "error" not in response` → `assert "isError" not in response["result"]`

Verification:
- Stale pattern grep: **0 matches** ✓
- New `isError` count: **3** at exact target lines ✓
- Line count: **4188 → 4188 (unchanged)** ✓ — pure single-line substitution, zero structural shift

**Phase 9 — Deliver round-6 summary (~2 min).** Insight block highlighted zero net line change as strongest convergence signal across the review arc. Coherence table, what-did-NOT-change list, anticipated round-7 vectors (narrow list: other transport-layer assertions, fixture sprawl, approval signal).

**Phase 10 — Receive round-7 scrutiny via `/copy` (~immediate).** User returned with zero critical failures. Verdict: "**Defensible**."

> "The remaining round-6 issue is closed. The plan now says what the tests actually prove, the protocol assertions match live repo authority, and I did not find another substantive flaw in the reviewed surface that justifies another revision round."

**First non-revision verdict across 7 rounds.** User explicitly noted the convergence: "The zero-net-line round is consistent with actual convergence here, not with a missed structural issue."

Optional polish flagged (not a blocker): 3 `json.loads(response["result"]["content"][0]["text"])` sites without explicit `isError` guards — `:3176` (Task 8 dispatch test), `:3235` (Task 8 busy-response test), `:4067` (Task 10 E2E busy proof). User framing: "If you want stricter explicitness later, you could add `"isError" not in response["result"]` guards before the success-path `json.loads(...)` sites. I would treat that as polish, not a blocker."

**Phase 11 — Verify polish sites (~1 min, 3 parallel reads).** Read `:3170-3182`, `:3230-3242`, `:4060-4074` to ground the 3 polish sites literally. Confirmed:
- All 3 sites parse `response["result"]["content"][0]["text"]` as JSON immediately
- None have a prior `isError` guard
- All 3 would crash loudly on tool-error payload via `JSONDecodeError`, but the assertion would be a false gate before the loud crash

**Phase 12 — Present 3-step landing sequence with discrete decisions (~3 min).** Structured response:
1. Insight block ("Defensible" ≠ approved-to-land, convergence curve across 7 rounds, polish vs blocker distinction)
2. Polish sites verification table
3. Three discrete decisions:
   - **A** (polish): A1 apply / A2 defer to implementer / A3 leave — no clear recommendation
   - **B** (commit+merge): propose commit subject + merge sequence + branch delete — require explicit green light per global CLAUDE.md
   - **C** (execution mode): subagent-driven-development vs inline (still pending from prior session)
4. Two sequencing options: "land today" (A3→B→C) vs "absolute closure" (A1→B→C)

**Phase 13 — User direction via `/copy` (~immediate).** User chose: **A1 (apply polish) → B (commit+merge) → C (subagent-driven-development)**.

**Phase 14 — Execute A1 (~2 min, 3 parallel Edits + verification).** Three guard insertions:
- `:3176` inserted `assert "isError" not in response["result"]` before `content = response["result"]["content"][0]["text"]`
- `:3235` inserted `assert "isError" not in response["result"]` before `payload = json.loads(response["result"]["content"][0]["text"])`
- `:4067` inserted `assert "isError" not in busy_response["result"]` before `busy_payload = json.loads(busy_response["result"]["content"][0]["text"])`

Verification: line count **4188 → 4191** (+3 exactly, one per polish edit). `isError` total: **6** occurrences (3 from round 6 at `:3394/:3412/:3988`, plus 3 new guards).

**Phase 15 — Pre-commit checks (~1 min, parallel Bash).** Verified:
- Working tree: plan still untracked; no other changes
- Branch: `docs/t05-execution-start-plan` (unchanged from prior session)
- HEAD: `bd850302` (unchanged from prior session)
- `origin/docs/t05-execution-start-plan` does NOT exist — branch was NEVER pushed, landing is purely local

Also checked recent commit message style for 5 prior docs-scoped commits to match local convention (`docs(t20260330-05): <subject>` pattern with structured body + Co-Authored-By trailer).

**Phase 16 — Execute B1 (commit on docs branch, ~1 min, single Bash chain).** Composed subject from my Decision-B proposal in phase 12 (implicitly approved by user's "B"). Body: single paragraph describing 7-round hardening + quantitative line ("11 tasks, 62 new tests (chain 593 → 655), 4191 lines"). HEREDOC for correct formatting. Commit `7f0329ca` created on `docs/t05-execution-start-plan`.

**Phase 17 — Execute B2 (merge to main + branch delete, ~1 min, single Bash chain).** `git checkout main` → `git merge --no-ff docs/t05-execution-start-plan -m "Merge branch 'docs/t05-execution-start-plan': T-05 execution-start plan (seven-round hardened)"` → `git branch -d docs/t05-execution-start-plan`. Merge commit `f154c682`. Safe delete (`-d`) succeeded because the branch was merged. Main now ahead of origin by 2 commits (plan commit + merge commit).

**Phase 18 — Ask user about B.1 (push) and C (execution session) (~2 min).** Push explicitly separated as sub-decision per global CLAUDE.md's shared-state-mutation rule. C presented with two paths: C1 (start subagent execution in this session) vs C2 (save handoff, fresh session). Recommended C2 for context-budget reasons (current ~64%).

**Phase 19 — User direction (~immediate).** "B.1: Push now. C2 - /save handoff, start fresh session."

**Phase 20 — Execute B.1 (push main, ~immediate, single Bash).** `git push origin main` → `bd850302..f154c682 main -> main`. Post-push status clean: local = remote. Git log verified: merge commit + plan commit both present on `origin/main`.

**Phase 21 — Invoke `handoff:save` (C2, this handoff being written now).**

## Decisions

### Decision 1: Accept round-6 finding without pushback

**Choice:** Confirm all 3 protocol-shape assertions (`:3394`, `:3412`, `:3988`) are structurally wrong and should be replaced with local-precedent-matching `response["result"]["isError"]` pattern.

**Driver.** User's citation held literally when verified:
- plan `:3394`: `assert "error" in response1`
- `mcp_server.py:221-231`: tool-call exception path returns `{"result": {"content": [...], "isError": True}}` — no top-level `error`
- `handle_request` at `:153-167`: top-level `error` is ONLY for protocol errors (method-not-found), never for tool-handler exceptions
- 9 existing test sites in `test_mcp_server.py` use `response["result"]["isError"] is True` as canonical pattern

**Alternatives considered:**
- **Push back on transport-coupling characterization:** Argue that my original wording (`assert "error" in response1`) is "transport-shape agnostic" because it only checks key presence. Rejected because `"error"` is itself a transport-shape choice — it's coupling to the wrong transport. User's critique ("couples to one specific transport shape, just the wrong one") held.
- **Claim the test works in practice:** It doesn't — `"error" in response1` evaluates False on the actual isError-shaped response, so the assertion would fail on dispatch 1 BEFORE reaching any ordering assertion. The test would fail-but-for-wrong-reason.

**Implications.** The fix is mechanical (3 substitutions). Preserves the "no message-surface assertion" intent (matches `isError is True`, not the message text). Aligns with 9 existing test-site occurrences — visually consistent when a reader scans the file.

**Trade-offs accepted.** None. Correct change on all axes.

**Confidence:** High (E3) — triangulated across live server code + 9 existing test occurrences + verified the one path (`handle_request`) that COULD produce top-level `error` is orthogonal (method-not-found only, not tool failures).

**Reversibility:** High at plan level; zero implementation cost.

**Change trigger:** If MCP protocol evolves to put tool-call failures back on top-level `error`. Unlikely — the current model aligns with MCP TypeScript SDK conventions.

### Decision 2: Strict subscript over `.get()` form

**Choice:** Use `response1["result"]["isError"] is True` (strict subscript) instead of user's tentatively-suggested `response1["result"].get("isError") is True` (defensive `.get()`).

**Driver.** Two confirmatory signals:
- Local precedent: 9 existing test occurrences use strict subscript; 0 use `.get()`.
- User's round-6 direction after my recommendation: "Use strict subscript, not `.get()`. Reason: that matches both repo precedent and the actual contract in `mcp_server.py:221`. A missing key should fail loudly."

**Alternatives considered:**
- **`.get("isError") is True`** — more defensive, tolerates missing key. Rejected because the key MUST be present on error responses (server-side contract at `mcp_server.py:229`); a missing key would be a server bug worth crashing on, not silently masking.
- **`response1["result"].get("isError", False) is True`** — same problem, adds default value complexity. Rejected.

**Implications.** Tests crash loudly on protocol-contract violations (missing `isError` key on an error response). Matches the "assert invariants, don't widen contracts" pattern established in round 4 (F4, `active_job_id: str` preserved over widening).

**Trade-offs accepted.** Test is coupled to the specific MCP error-surface shape. If the shape ever changes (top-level `error` return, for example), this test needs updating. Accepted because the shape is stable per MCP conventions.

**Confidence:** High (E2) — user directive + local precedent verified.

**Reversibility:** High — purely text-level change.

**Change trigger:** Repo adopts `.get()` pattern elsewhere, or MCP protocol changes.

### Decision 3: Fold `:3988` (Task 10 E2E adjacent occurrence) into round 6

**Choice:** Apply the protocol-shape fix to `:3988` in the same round as the user-flagged `:3394`/`:3412`, not deferred to round 7.

**Driver.** User's directive (after I flagged the adjacent occurrence): "Fold it in now. Same defect class, same fix shape, near-zero scope cost. Deferring it just invites another round on an already-understood propagation bug."

This is the second time the user has directed a fold-in across the arc (round 4's journal-branch fold-in). Establishes a pattern: when an adjacent occurrence is same-class, fold now.

**Alternatives considered:**
- **Fold silently without asking:** Rejected per global CLAUDE.md "ask before scope expansion" norm. The round-4 precedent was a user-directed fold, not a silent expansion.
- **Defer to round 7:** Rejected by user as "invites another round."
- **Leave unfixed:** Rejected by user — a false gate is still a defect even if downstream assertions would catch the problem loudly.

**Implications.** Task 10's E2E test is now internally consistent with the Task 8 assertions. Round 7 did NOT re-raise this class of finding, confirming the fold-in prevented the predicted round-7 cost.

**Trade-offs accepted.** Round 6 scope slightly wider than user's initial scrutiny. Accepted per user's explicit directive.

**Confidence:** High (E1) — direct user directive.

**Reversibility:** High.

**Change trigger:** N/A.

### Decision 4: Apply A1 polish (3 `isError` guards before `json.loads`)

**Choice:** Add `assert "isError" not in response["result"]` (or `busy_response["result"]` for the E2E site) before each of 3 `json.loads` sites at `:3176` (Task 8 dispatch test), `:3235` (Task 8 busy-response test), `:4067` (Task 10 E2E busy proof).

**Driver.** User directive: "A1 (apply polish) → B (commit+merge) → C (subagent-driven-development)."

Round-7 framing: "polish, not a blocker." I recommended no-call in the response; user explicitly chose apply. Rationale: absolute closure before landing to main.

**Alternatives considered:**
- **A2 (defer to implementer during Task 8/10 execution):** User rejected implicitly. Would have left the plan at 4188 lines.
- **A3 (leave as-is, rely on loud-but-wrong-place failure via `JSONDecodeError`):** User rejected implicitly. Matches "polish not blocker" framing literally but sacrifices absolute closure.

**Implications.** Plan at 4191 lines (4188 + 3 guards). Full defensive coverage across 6 assertion sites (3 from round 6 + 3 new guards). Future-readers see consistent guard-then-parse pattern.

**Trade-offs accepted.** +3 lines, 0 new test logic. Effectively free.

**Confidence:** High (E1) — direct user directive.

**Reversibility:** High — pure text edits.

**Change trigger:** N/A.

### Decision 5: Commit message — single structured body paragraph over multi-section body

**Choice:** Commit `7f0329ca` uses subject `docs(t20260330-05): plan first execution-wiring slice` + single-paragraph body describing 7-round hardening attributes + quantitative summary line ("11 tasks, 62 new tests (chain 593 → 655), 4191 lines") + Co-Authored-By trailer.

**Driver.** Two signals:
- User implicitly approved the subject I proposed in Decision-B presentation (no override given when saying "B").
- Recent docs-scoped commit style in the repo: 5 out of 5 recent `docs(t20260330-05): *` commits use structured body paragraphs. My single-paragraph form is within the range but less structured than the median.

**Alternatives considered:**
- **Multi-section body with bullet lists:** More structured, matches `0c44d3c5` precedent exactly. Rejected as slightly over-engineered for a plan-landing commit — the plan file itself contains all structure.
- **Terse one-line body:** Rejected because 7 rounds of hardening warrants documentation in the commit message for future archaeology.

**Implications.** Commit is readable, concise, matches repo style approximately, mentions all key proof mechanisms (register-FIRST, seed-and-assert, negative-path retry, 3-source busy gate, committed-start failure semantics, MCP tool-error contract alignment).

**Trade-offs accepted.** Slightly less-structured body than repo median; loss is cosmetic.

**Confidence:** Medium (E1) — judgment call based on repo style inspection.

**Reversibility:** Medium — commit message is immutable post-push, but the commit itself is mergeable/reverable via standard git flow.

**Change trigger:** N/A.

### Decision 6: `--no-ff` merge + safe `-d` branch delete

**Choice:** `git merge --no-ff docs/t05-execution-start-plan` creates an explicit merge commit (`f154c682`) preserving the branch-point structure. `git branch -d` uses safe delete (refuses unmerged).

**Driver.** Repo convention per recent merges on main (`bd850302`, `1a98521a`, `4902c429` all use merge commits, not fast-forward). Preserves review-round arc as a visible boundary in git history.

**Alternatives considered:**
- **Fast-forward merge (`--ff-only`):** Collapses to a single commit, loses visible branch-point. Rejected per repo convention.
- **Squash merge:** Loses the individual commit structure. Rejected — only 1 commit on the docs branch anyway, would be equivalent to ff in outcome.
- **Force delete (`-D`):** Skips merge-state check. Rejected per global CLAUDE.md destructive-actions rule; safe `-d` self-verifies.

**Implications.** `git log --first-parent main` shows "Merge branch 'docs/t05-execution-start-plan'" as a discrete unit. Future archaeology can distinguish "planning arc" from "execution arc."

**Trade-offs accepted.** Main is ahead by 2 commits post-merge instead of 1 (both the plan commit and the merge commit). Accepted as normal for `--no-ff` merges.

**Confidence:** High (E2) — repo convention verified via recent merge commit history + global CLAUDE.md safe-delete rule.

**Reversibility:** Low — merge is in main, branch is deleted. Revert path: `git revert -m 1 f154c682`. But this should not be needed.

**Change trigger:** N/A.

### Decision 7: Push main to origin via explicit B.1 step (not implicit in B)

**Choice:** Present push as a separate sub-decision (B.1) requiring explicit user authorization, even though handoff's original "Next Steps #3" listed "Push main" as part of the landing sequence.

**Driver.** Global CLAUDE.md: "Actions visible to others or that affect shared state: pushing code... A user approving an action (like a git push) once does NOT mean that they approve it in all contexts."

**Alternatives considered:**
- **Push immediately after merge:** The handoff listed push as part of the landing sequence. Rejected because user's "B" directive was explicit about commit+merge+branch-delete but silent on push. Safer posture: confirm.
- **Ask before every sub-step:** Over-confirmation. Rejected — user had already approved commit+merge+branch-delete in bulk.

**Implications.** Added one confirmation loop before push. Minimal friction. User confirmed immediately.

**Trade-offs accepted.** +1 round-trip. Zero cost.

**Confidence:** High (E2) — global rule verified; user's explicit B wording verified as silent on push.

**Reversibility:** Low — push is durable. Revert path: another push with a revert commit.

**Change trigger:** N/A.

### Decision 8: C2 (save+fresh session) over C1 (execute in this session)

**Choice:** Invoke `handoff:save` and recommend next session starts fresh for subagent-driven execution.

**Driver.** Two signals:
- Current context at ~64% (128k/200k) post-landing. 11-task execution even in delegation mode will accumulate parent-side coordination state.
- User directive: "C2 - /save handoff, start fresh session."

**Alternatives considered:**
- **C1 (execute in this session):** Subagent-driven-development pattern keeps parent context clean (parent holds summaries, not full task transcripts). Viable but riskier — if context pressure forces mid-execution handoff, the execution state is more complex to capture than planning state.

**Implications.** This handoff captures planning-arc terminus + landing + positions next-session Claude to load with full 1M budget free for execution. Next session can invoke `superpowers:subagent-driven-development` from clean state.

**Trade-offs accepted.** One additional session-boundary crossing. Handoff + load overhead ~5 min. Accepted as cheap insurance against mid-execution context pressure.

**Confidence:** High (E1) — direct user directive.

**Reversibility:** High — if next session decides inline execution is preferable, pivot is trivial.

**Change trigger:** N/A.

## Changes

### Files modified (this session)

| File | Change | Commit |
|---|---|---|
| `docs/plans/2026-04-17-t05-execution-start-slice.md` | **Round 6 (3 edits):** `:3394` asserted `response1["result"]["isError"] is True` replacing `"error" in response1`. `:3412` asserted `"isError" not in response2["result"]` replacing `"error" not in response2`. `:3988` asserted `"isError" not in response["result"]` replacing `"error" not in response` in Task 10 E2E busy-path check. Line count unchanged at 4188. **A1 polish (3 edits):** `:3176` inserted `assert "isError" not in response["result"]` guard before `json.loads` in Task 8 dispatch test. `:3235` inserted same guard before `json.loads` in Task 8 busy-response test. `:4067` inserted `assert "isError" not in busy_response["result"]` guard before `json.loads` in Task 10 E2E busy-path proof. Line count: **4188 → 4191 (+3)**. `isError` total across plan: **6** (3 from round 6 + 3 from A1). | `7f0329ca` + merged as `f154c682` |

### Git state changes

| Commit | Branch/Pointer | Subject |
|---|---|---|
| `7f0329ca` | `docs/t05-execution-start-plan` (since deleted) | `docs(t20260330-05): plan first execution-wiring slice` |
| `f154c682` | `main` | `Merge branch 'docs/t05-execution-start-plan': T-05 execution-start plan (seven-round hardened)` |
| pushed | `origin/main` | `bd850302..f154c682` |

Branch `docs/t05-execution-start-plan` deleted locally via safe `-d` (it was never pushed). `main` now at `f154c682` both locally and at `origin/main` — in sync.

### Handoff / state files

- Archived (at session start): `2026-04-17_19-39_t05-plan-rounds-4-5-propagation-and-retry-safety.md` → `docs/handoffs/archive/`
- State file: `docs/handoffs/.session-state/handoff-2535a7e5-2f0e-4a3f-a944-9dca5ff618b0` — to be cleaned by this save
- New handoff (this file): `docs/handoffs/2026-04-17_21-40_t05-plan-rounds-6-7-mcp-tool-error-contract-defensible-merged.md`

## Codebase Knowledge

### Files read this session

| File | Range | Purpose | Key finding |
|---|---|---|---|
| `docs/handoffs/2026-04-17_19-39_t05-plan-rounds-4-5-propagation-and-retry-safety.md` | full (973 lines) | Prior handoff (resumed) | Plan at 4188 lines, test-chain 593→655, awaiting round-6 review |
| `docs/plans/2026-04-17-t05-execution-start-slice.md` | `:3340-3440`, `:3260-3340` | Ground round-6 test citations | `:3394` assertion held literally; fixture `_FailOnceDelegationController` sound |
| `packages/plugins/codex-collaboration/server/mcp_server.py` | `:100-254` | Verify live tool-error surface | `_handle_tools_call` at `:207-231` wraps exceptions as `result.isError=True`. Top-level `error` ONLY at `:167` via `_error_response` for method-not-found. |
| `docs/plans/2026-04-17-t05-execution-start-slice.md` | `:3170-3182`, `:3230-3242`, `:4060-4074` | Ground round-7 polish sites | 3 sites parse `response["result"]["content"][0]["text"]` immediately without `isError` guard |

### Grep sweeps this session

| Pattern | Scope | Result | Purpose |
|---|---|---|---|
| `isError` | `packages/plugins/codex-collaboration/**` | 9 test sites + 1 server site | Confirm local precedent for assertion style |
| `"error" in response\|"error" not in response\|response\[.error.\]` | plan (full) | 3 matches (`:3394`, `:3412`, `:3988`) | Adjacent-occurrence sweep (found `:3988`) |
| `isError` | plan (full) | 0 pre-round-6; 3 post-round-6; 6 post-A1 | Verify substitution applied at exact target lines |
| `"error" in response\|"error" not in response\|response\[.error.\]` | plan (full, post-round-6) | 0 matches | Confirm no stale patterns remain |

### Architecture: MCP tool-error vs protocol-error surface

```
JSON-RPC 2.0 request: tools/call
  │
  ▼
handle_request() (mcp_server.py:153-167)
  │
  ├─ method == "tools/call" → _handle_tools_call (line 166)
  │     │
  │     ├─ try: _dispatch_tool() → success
  │     │     return {"jsonrpc":"2.0", "id": req_id, "result": {"content":[...]}}  (line 212-220)
  │     │     NOTE: success response has NO "isError" key at all
  │     │
  │     └─ except Exception:
  │           return {"jsonrpc":"2.0", "id": req_id, "result": {"content":[...], "isError": True}}  (line 222-231)
  │
  └─ method not found → _error_response(req_id, -32601, ...)
        return {"jsonrpc":"2.0", "id": req_id, "error": {...}}  (line 167, :284)
        NOTE: this is where top-level "error" key appears
```

Key takeaway: top-level `error` = protocol-layer failure. `result.isError = True` = tool-handler failure wrapped as a successful-protocol-level response. **Different layer, different surface.** The plan test initially conflated the two.

### Architecture: convergent-review defect-class ladder (7 rounds)

| Round | Defect class closed | Lines delta | Findings | Key mechanism |
|---|---|---|---|---|
| 1 | Data shapes | +~500 | 3 | Structural: types, invariants |
| 2 | Reader/failure semantics | +~499 | 2 | Failure-mode matrix |
| 3 | Integration wiring | +339 | 2 | Factory/consumer/persistence |
| 4 | Propagation | +116 | 4 + fold | Docstring/AC/summary alignment |
| 5 | Proof shape | +125 | 1 | Negative-path test for ordering |
| 6 | Protocol-contract alignment | **0** | 1 | `response["result"]["isError"]` |
| 7 | (approval: Defensible) | **+3** (polish only) | 0 required / 3 optional | Grep-sweep guards |

Total: +1,582 lines across 7 rounds. **Defect-class ordering is monotonically narrowing** from the global (data shapes) to the local (protocol assertions) — the pattern that emerged in round 5 (propagation vs design) continued cleanly.

### Surprising findings / gotchas this session

- **MCP's two-layer error model is easy to miss.** My original `assert "error" in response1` was superficially correct-sounding to anyone who remembers JSON-RPC 2.0 as "either result or error at top level." But MCP-as-a-protocol wraps tool-handler failures inside `result.isError`, preserving top-level `error` for protocol failures only. This layering is documented in the MCP TypeScript SDK conventions but easy to forget when writing tests in isolation.
- **Zero net line change is a powerful convergence signal.** Round 6 produced 3 substitutions on existing lines — no new structure, no cascading updates. The strongest pre-approval signal observed. Rounds with +100+ lines (1-5) were still hunting defects; round 6 was adjusting text in place; round 7 confirmed defensibility.
- **Safe branch delete (`-d`) self-verifies merge state.** `git branch -d` refuses to delete unmerged branches. After a `--no-ff` merge, the docs branch WAS merged into main, so `-d` accepted. If the merge had failed silently or been incomplete, `-d` would have refused — saving me from the `-D` forced delete that could have orphaned work.
- **Branch never pushed means no remote-delete step.** I verified `origin/docs/t05-execution-start-plan` → "Needed a single revision" (git's way of saying the ref doesn't exist). Simplified the landing sequence to a fully local operation + a single push of main.

### Key locations to remember

| Concept | Location |
|---|---|
| T-05 plan (7x revised, MERGED) | `docs/plans/2026-04-17-t05-execution-start-slice.md` (4191 lines, on main@f154c682) |
| MCP tool-error wrapper | `packages/plugins/codex-collaboration/server/mcp_server.py:221-231` |
| MCP protocol-error wrapper | `packages/plugins/codex-collaboration/server/mcp_server.py:167` (via `_error_response` at `:284`) |
| Local precedent for `isError is True` | `packages/plugins/codex-collaboration/tests/test_mcp_server.py:377,550,555,565,586,609,647,683` |
| Landing commit (plan on docs branch) | `7f0329ca` |
| Merge commit on main | `f154c682` |

## Context

### Mental model

**Framing:** Rounds 6-7 were the **protocol-contract-alignment** (R6) and **polish-and-approval** (R7) rounds — the terminal narrowing of the review arc.

- **Design rounds** (1-2): "Is this the right architecture?"
- **Integration rounds** (3): "Does the design actually connect?"
- **Propagation rounds** (4): "Do prose, docstrings, AC summaries match?"
- **Proof-shape rounds** (5): "Do tests actually falsify claims?"
- **Protocol-contract rounds** (6): "Do test assertions match live contracts?"
- **Polish-and-approval rounds** (7): "Defensible, with optional polish."

**Core insight:** *Each round closes a different defect class; defect classes are ordered by abstraction from global (data shapes) to local (protocol assertions). The ladder is monotonically narrowing — you can't skip a rung because a propagation bug looks like a proof-shape bug when you're actually at the propagation layer.* The fact that round 6 found exactly 1 defect (down from 4+fold in round 4, 1 in round 5) and that defect was at an even narrower abstraction layer (single assertion text) signals that the plan has hit the floor of its own defect space.

**Mental model:** *Converging review series with monotonically narrowing defect classes.* Each round's verdict tells you where on the ladder you are. A "Minor revision" with a single finding at a narrow layer (R6) predicts convergence; the next round is likely to either approve or find at the same-narrow-or-narrower layer. That pattern held: R6 → R7 = "Defensible" with polish-only.

### Project state at session close

**T-20260330-05 (execution-domain foundation):** Plan MERGED on main. Ready for execution. Handoff chain: plan kickoff → Q0 decision → tmp-hardening → plan draft → R1 → R2 → R3 → R4 → R5 → **R6 → R7 (Defensible) → merged to main + pushed** → [execution phase begins next session].

**T-20260330-06 / T-07:** OPEN, blocked by T-05 execution. T-05 plan is now merged, so execution can start.

**T-20260416-01 (codex.dialogue.reply extraction mismatch):** OPEN, medium priority. Independent parallel thread — unchanged this session.

### Environment snapshot at session close

- Branch: `main` (docs branch deleted; never pushed)
- HEAD: `f154c682`
- `origin/main`: `f154c682` (in sync post-push)
- Working tree: clean
- Plugin suite: not run this session (no code changes — only plan edits)
- Memory: MEMORY.md unchanged this session (should be updated post-merge — see Next Steps)
- Context usage at session close: ~72% of 200k (planning arc terminus — appropriate closure point)

### Why this work matters (bigger picture)

T-05 is the execution-domain foundation for codex-collaboration. The plan has now sustained 7 rounds of scrutiny and landed with a "Defensible" verdict. Shipping round-3 text would have produced 2 bugs (F1 + F4); round-4 text would have produced 1 bug (round-5 finding); round-5 text would have produced a test that fails on transport-shape mismatch (round-6 finding); round-6 text would have produced 3 tests with silent false gates (round-7 polish). Each round's cost (~20-60 min) prevented 1-3 hours of execution-time rework.

The arc also establishes a reusable review methodology: structured scrutiny via `/copy` + verbatim-citation verification + option presentation + per-round verdict. This pattern has now produced 7 rounds with 14 defects closed (3+2+2+5+1+1+0) and a clean approval. Applicable to future plans.

## Learnings

### MCP protocol has two error surfaces — test assertions must target the right one

**Mechanism.** MCP wraps tool-handler failures as successful JSON-RPC responses with `result.isError: True`, reserving top-level `error` for protocol-layer failures (method-not-found, parse errors). This is a protocol-level design choice (separates "protocol broken" from "tool ran but failed"). A test asserting `"error" in response` against a tool-handler failure would false-negative — the assertion targets the wrong layer.

**Evidence.** Verified at `mcp_server.py:221-231` (isError wrapper for tool-handler exceptions) vs `:167, :284` (`_error_response` for method-not-found). 9 existing test-site occurrences in `test_mcp_server.py` use `response["result"]["isError"] is True`.

**Implication.** Any test claiming to prove tool-handler behavior must assert against `result.isError`, not top-level `error`. This applies to all future Task-8-style tests in codex-collaboration and any new MCP server tests in the project.

**Watch for.** Tests where the variable name is `response` and the assertion pattern is `"error" in response` or `response["error"]` — these likely target the wrong surface unless the test is specifically exercising a protocol-layer failure (unknown method, malformed request).

### Zero net line change + single narrow finding = approval-imminent signal

**Mechanism.** Across a converging review series, line-count delta and findings-per-round both serve as convergence signals. When BOTH hit floor simultaneously — delta near zero, findings ≤1 at the narrowest abstraction layer — the next round typically either approves or finds at the same-or-narrower layer.

**Evidence.** T-05 arc: R1 (+500, 3 findings) → R2 (+499, 2) → R3 (+339, 2) → R4 (+116, 4+fold) → R5 (+125, 1) → **R6 (0, 1)** → R7 (+3 polish only, "Defensible"). R6's zero-delta + single-narrow finding predicted R7 approval precisely.

**Implication.** When running a multi-round review arc, use line-count delta as a trend indicator. A zero-delta round signals "done hunting structural defects, now polishing text." If the next round finds anything at a deeper layer (design/integration/propagation), it's signal of an undetected structural issue — worth investigating before assuming convergence.

**Watch for.** Rounds that suddenly grow significantly after a zero-delta round — red flag for undetected defects re-surfacing from deeper layers.

### Adjacent-occurrence grep sweep pre-empts next-round cost

**Mechanism.** When the user flags one occurrence of a defect class, grepping for the defect-class pattern across the entire artifact often surfaces 1-2 additional same-class occurrences. Folding those in immediately (not silently — ASK the user) pre-empts the next round's cost of re-raising the same pattern one line later.

**Evidence.** Round 4 established the pattern (journal-branch fold-in after F4 registry fix). Round 6 repeated it: grepping `"error" in response|"error" not in response` after user flagged `:3394`/`:3412` found `:3988` in Task 10 E2E. User confirmed fold-in with: "Deferring it just invites another round on an already-understood propagation bug."

**Implication.** After each round's revision, run a defect-class grep before returning. Pattern: identify the user's finding's structural pattern (e.g., "top-level `error` assertion"), grep for it, flag additional matches with fold-in/defer/leave options.

**Watch for.** Defects that show up in both "user-flagged" and "silent-adjacent" occurrences — suggests the pattern spans the codebase and a systematic sweep is warranted.

### Safe git operations (`-d`, `--no-ff`) are self-verifying

**Mechanism.** Safe git operations encode correctness preconditions. `git branch -d` refuses unmerged branches; `git merge --no-ff` preserves branch structure in history; `git push` (without `--force`) refuses non-fast-forward updates. Each refusal is signal that something unexpected is happening.

**Evidence.** This session used `git branch -d docs/t05-execution-start-plan` after the `--no-ff` merge; git accepted because the branch was fully merged. If it had refused, I would have investigated before forcing. Repo convention for merges (verified via `bd850302`, `1a98521a`, `4902c429`) uses `--no-ff` to preserve review-round arcs as visible merge boundaries.

**Implication.** Prefer safe variants (`-d`, `--no-ff`, `push` without `--force`) as first resort. Use destructive variants (`-D`, `--ff-only`, `--force`) only when the safe variant refuses AND the investigation confirms forcing is correct.

**Watch for.** Any script or hook that defaults to destructive flags — a signal of deferred investigation cost.

### `--no-ff` merges preserve planning-arc boundaries for archaeology

**Mechanism.** A `--no-ff` merge creates an explicit merge commit that shows up in `git log --first-parent main` as a discrete unit even after the feature branch is deleted. The merge commit message ("Merge branch 'docs/...'") serves as a self-documenting boundary.

**Evidence.** `f154c682` on main shows "Merge branch 'docs/t05-execution-start-plan': T-05 execution-start plan (seven-round hardened)". Future `git log --first-parent --oneline main` will show this as a single entry, hiding the 1 commit on the branch but preserving the boundary.

**Implication.** For multi-commit branches or single-commit branches with significant context, prefer `--no-ff` to preserve the boundary. For trivial branches (typo fixes, trivial refactors), fast-forward is acceptable.

**Watch for.** Repos where `--ff-only` is the default — commit history loses planning/review arcs.

## Next Steps

### 1. Execute the T-05 plan via subagent-driven development

**Dependencies:** None (plan is merged on main; execution can begin immediately).

**What to read first (next-session Claude):**
1. `docs/plans/2026-04-17-t05-execution-start-slice.md` — the 11-task plan. Read sequentially. Task 1 is the starting point.
2. `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` — the recovery + journal spec (referenced throughout the plan).
3. `packages/plugins/codex-collaboration/server/mcp_server.py` — for dialogue-controller precedent (lazy factory pattern, line 132-151).
4. This handoff's "Codebase Knowledge" section — for the MCP tool-error surface map.

**Approach (per user's C choice):** Invoke `superpowers:subagent-driven-development` skill. Dispatch Task 1 to a subagent. Parent session holds coordination state. Subagent returns with task summary; parent reviews; next task dispatched. Pattern iterates for all 11 tasks.

**Estimated effort:** 5-7 hours across 11 tasks. 62 new tests, chain 593 → 655.

**Key proof mechanisms (subagent must preserve):**
- Register-FIRST ordering in controller `start()` flow (Task 6)
- Pin-only-after-successful-recovery in `_ensure_delegation_controller` (Task 7)
- Seed-and-assert proof in Task 10 E2E (factory path, unresolved journal entry reconciliation)
- Negative-path retry-safety test in Task 8 (`_FailOnceDelegationController`, 3-dispatch shape)
- Three-source busy gate with invariant asserts (Task 2-3)
- MCP tool-error contract assertions (`response["result"]["isError"]`) at 6 sites

**Acceptance criteria:** 11 tasks complete, ~655 tests passing, coverage unchanged or improved, no regressions in existing 593-test baseline.

**Potential obstacles:**
- **Error-response surface flag from round 5 anticipation:** The new negative-path test at plan `:3349-3437` assumes `handle_request` catches `RuntimeError` from `_ensure_delegation_controller` and returns an `isError`-wrapped response. This is **partially verified** post-round-6 — `_handle_tools_call` at `:207-231` DOES catch `Exception`. But the control flow for lazy-factory `_ensure_delegation_controller` raising inside `_handle_tools_call` is not fully traced; implementer should verify during Task 8 execution.
- **Fixture sprawl in test_mcp_server.py:** 6 fake/recording classes with overlapping purposes (`FakeControlPlane`, `FakeDialogueController`, `FakeDelegationController`, `_RecordingDelegationController`, `_FailOnceDelegationController`, `_BusyController`). Deferred per round-5 disposition; revisit after Task 8 if readability becomes a concern.
- **Test count divergence:** Task 11's chain (593 → 655) may diverge ±3 during execution per plan's explicit tolerance. Investigate if divergence >3.

### 2. Update MEMORY.md post-merge (pre-execution or during-execution)

**Dependencies:** None.

**What to do:** The "Current Focus" section in `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/MEMORY.md` still lists Engram as the only active work. Add T-05 execution as the new primary focus now that the plan is merged.

**Suggested addition:**
```
## Current Focus

Active work:
1. **T-05 execution-start slice** — Plan merged to main (f154c682) after 7 review rounds. Execution via subagent-driven-development next session. Plan at `docs/plans/2026-04-17-t05-execution-start-slice.md` (4191 lines, 11 tasks, 62 new tests).
2. **Engram** — Still in design phase. Spec at `docs/superpowers/specs/engram/`.
```

### 3. Pending-request capture slice (follow-up)

**Dependencies:** T-05 execution complete.

**What to do:** Unchanged from prior handoffs. Wire the notification loop → route App Server request messages through `parse_pending_server_request` → persist as `PendingServerRequest` → expose via `needs_escalation`. Closes AC 6. Also triggers `ExecutionRuntimeRegistry.lookup` for turn-dispatch paths.

### 4. Decide-surface refinements (deferred)

Unchanged from prior handoffs.

### 5. T-20260416-01 extraction bug fix (parallel thread)

Unchanged from prior handoffs.

### 6. Landing sequence (updated — planning arc COMPLETE)

~~T-05 plan review~~ ✓ COMPLETE → ~~T-05 plan merge~~ ✓ COMPLETE → **T-05 execution-start slice (11-task plan executes)** → T-05 pending-request capture slice → T-05 decide-surface + lifecycle refinements → T-05 COMPLETE → T-06 → T-07.

## In Progress

**Clean stopping point.** T-05 planning arc terminated cleanly with "Defensible" verdict, merged to main, pushed to origin. No work in flight.

- **What was completed:** Rounds 6 and 7 of review absorbed; polish applied (A1); commit + merge + branch-delete executed; push to origin executed; this handoff being written.
- **What is NOT in flight:** Plan execution (deferred to next session per C2 directive). Memory file update (step 2 in Next Steps). No code changes pending.
- **Next action (for next-session Claude):** Load this handoff via `/handoff:load`. Invoke `superpowers:subagent-driven-development` skill. Dispatch Task 1.

## Open Questions

### 1. Does `_handle_tools_call` fully wrap errors from `_ensure_delegation_controller`?

**Context:** The new negative-path Task 8 test at plan `:3349-3437` calls `server.handle_request(...)` with a factory whose first-call controller raises from `recover_startup`. The test asserts `response1["result"]["isError"] is True`. This assumes:
- `_ensure_delegation_controller` is invoked inside `_handle_tools_call` (not before)
- The `try: _dispatch_tool(...) except Exception:` block at `mcp_server.py:210-230` catches `RuntimeError` from controller instantiation

Post-round-6 verification confirmed `_handle_tools_call` does catch `Exception` broadly. But the control-flow path `_handle_tools_call → _dispatch_tool → <some controller access> → _ensure_delegation_controller` was not fully traced.

**Impact:** If `_ensure_delegation_controller` is called BEFORE `_dispatch_tool` (e.g., during request-routing setup), the exception would escape the try/except and crash the server. Test would fail with uncaught `RuntimeError`, not the expected `isError` assertion.

**Decision pending until:** Implementer verifies during Task 8 execution (probably Task 8.1 test-first phase).

### 2. Should the `_FailOnceDelegationController` fixture mirror `_RecordingDelegationController` more closely?

**Context:** Unchanged from prior session. User did NOT address this in rounds 6-7.

**Impact:** LOW — style consistency only.

**Decision pending until:** Execution phase if readability becomes a concern.

### 3. Fixture sprawl consolidation

**Context:** 6 fake/recording classes in `test_mcp_server.py`. Flagged in prior handoffs; not addressed in rounds 6-7.

**Impact:** LOW — post-execution cleanup opportunity.

**Decision pending until:** Post-execution review or T-06.

### 4. MEMORY.md update timing

**Context:** "Current Focus" section should reflect T-05 execution as active work. I deferred the update to next session rather than making it this session.

**Impact:** LOW — next session will see the handoff and know the state; MEMORY.md update is a convenience, not a correctness issue.

**Decision pending until:** Next session (or this session if user directs pre-save).

## Risks

### 1. Next-session error-response surface verification

**Impact:** If `_ensure_delegation_controller`'s exception is NOT caught by `_handle_tools_call`'s try/except (control-flow depends on invocation point), Task 8's negative-path test would fail with uncaught `RuntimeError`. The test would need adjustment: either `pytest.raises(RuntimeError)` wrapping the first `handle_request` OR a code change to ensure the exception IS caught.

**Mitigation:** Flagged explicitly in Open Questions #1. Implementer will catch during Task 8 execution. The fix is localized.

**Action:** Spot-check `mcp_server.py` error-handling path during Task 8 implementation.

### 2. Test count estimates diverge from reality during execution

**Impact:** Unchanged from prior handoffs. Baseline (593) + per-task estimates (11+8+3+3+6+15+5+8+2+1 = 62) = 655. Actual execution may produce slightly different counts.

**Mitigation:** Explicit tolerance language in Task 11 ("divergence >3 tests = investigation signal").

### 3. Fixture sprawl friction during execution

**Impact:** 6 fake/recording classes in `test_mcp_server.py` may slow Task 8 implementation if the fixtures need extension. Deferred consolidation is rational but creates a small compounding cost.

**Mitigation:** Watch for fixture-related friction during Task 8; consolidate opportunistically if the cost exceeds ~10 min.

### 4. Push made without code review

**Impact:** LOW. The merged change is a plan document, not code. No CI pipeline effects. No runtime behavior change. But the pattern of "review → merge → push without PR" sets a precedent for this project; watch for this becoming normalized for non-trivial code changes.

**Mitigation:** Next session should use a PR workflow if/when code changes land, per standard practice.

### 5. Context pressure if plan execution runs longer than 5-7 hours

**Impact:** 11 tasks × ~30 min each = 5.5 hours in steady state. Subagent-driven pattern keeps parent context clean, but coordination state accumulates. A single session may not complete all 11 tasks.

**Mitigation:** C2 (save+fresh session) chosen precisely for this reason. If needed, subagent-driven execution can span multiple sessions with handoff at natural task boundaries.

### 6. Memory file drift

**Impact:** MEMORY.md not updated this session. Next session's auto-loaded memory will still say Engram is the only active work.

**Mitigation:** Step 2 in Next Steps. Low priority; handoff itself provides the state.

## References

### Session's deliverable

| Artifact | Location | Status |
|---|---|---|
| Seven-times-revised, landed implementation plan | `docs/plans/2026-04-17-t05-execution-start-slice.md` | **Merged to main** (4,191 lines); pushed to origin |
| Docs branch | ~~`docs/t05-execution-start-plan`~~ | **Deleted** (safe `-d` after `--no-ff` merge) |
| Merge commit | `f154c682` on `main` | Pushed to `origin/main` |

### Authority documents (verified this session)

| Document | Location | Role |
|---|---|---|
| T-20260330-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | AC source of truth (unchanged) |
| recovery-and-journal.md | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Recovery spec (unchanged — referenced by plan) |
| mcp_server.py | `packages/plugins/codex-collaboration/server/mcp_server.py` | **Round 6 authority**: `:221-231` (isError wrapper), `:167` (top-level error for method-not-found), `:284` (`_error_response`), `:135` (dialogue pin precedent) |
| test_mcp_server.py | `packages/plugins/codex-collaboration/tests/test_mcp_server.py` | **Round 6 precedent**: 9 test occurrences of `response["result"]["isError"] is True` (lines 377, 550, 555, 565, 586, 609, 647, 683) |

### Memory files referenced this session

All under `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/`:

| Memory | Relevance |
|---|---|
| `feedback_contract_text_over_operational_interpretation.md` | Applied — verified round-6 finding literally against live `mcp_server.py` before responding |
| `feedback_edit_in_repo.md` | Applied — revised plan in `docs/plans/` under the repo; did not touch plugin cache |
| Prior-session user-preferences memories | Applied — structured response shape, verbatim wording, per-round verdict awareness, `/copy` as substantive channel |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-17_19-39_t05-plan-rounds-4-5-propagation-and-retry-safety.md`
- T-05 arc: kickoff (04-17 01:41) → Q0 decision (04-17 11:59) → tmp-hardening closure (04-17 17:09) → plan drafted (04-17 18:01) → plan round 1 (04-17 19:30) → plan round 2 (04-17 19:23) → plan round 3 (04-17 20:14) → plan rounds 4+5 (04-17 19:39) → **plan rounds 6+7 + landing (this handoff, 04-17 21:40 local)** → plan execution → pending-request capture → decide-surface → T-05 complete

## Gotchas

### 1. Branch never pushed means no remote cleanup needed

**Symptom:** `git rev-parse --verify origin/docs/t05-execution-start-plan` returns `fatal: Needed a single revision`.

**Root cause:** The docs branch was created locally but never pushed (the handoff's landing sequence said "push main, delete branch local+remote if pushed" — the "if pushed" clause applied).

**Prevention:** Always check `git rev-parse --verify origin/<branch>` before attempting `git push origin :<branch>` or similar remote-delete operations. Non-existent remote refs cause `git push` to produce confusing errors.

### 2. `--no-ff` merge creates 2 commits on main, not 1

**Symptom:** `git status` says "Your branch is ahead of 'origin/main' by 2 commits" immediately after a `--no-ff` merge of a single-commit branch.

**Root cause:** `--no-ff` adds:
- The branch's own commit (e.g., `7f0329ca`)
- The merge commit (e.g., `f154c682`)

Total: 2 commits ahead. Fast-forward would have been 1.

**Prevention:** When counting commits-to-push post-merge, remember `--no-ff` doubles the count for single-commit branches. This is expected, not a bug.

### 3. MCP error surface is NOT JSON-RPC's top-level error

**Symptom:** Test asserting `"error" in response` against a tool-handler failure always False. If used with `assert ... is True`, crashes immediately.

**Root cause:** MCP wraps tool-handler failures as successful JSON-RPC responses with `result.isError: True`. Top-level `error` is reserved for protocol-layer failures (method-not-found, parse errors).

**Prevention:** When writing MCP server tests, default to `response["result"]["isError"] is True` for tool-call failure assertions. Use top-level `error` assertions ONLY for tests specifically exercising protocol-layer failures (unknown method name, malformed JSON).

### 4. Safe branch delete (`-d`) after `--no-ff` merge works because branch IS merged

**Symptom:** `git branch -d docs/t05-execution-start-plan` accepts the delete without complaint, even though the branch had non-trivial commits.

**Root cause:** `--no-ff` merge creates an explicit merge commit on main that descends from the branch's tip. Safe delete verifies: "is this branch's tip reachable from HEAD?" After the merge, yes. Before the merge, no — `-d` would have refused.

**Prevention:** Always merge before deleting a branch. Never use `-D` unless you've verified the work is preserved elsewhere.

### 5. Invariant-assert style now spans 6 sites (3 round-6 + 3 polish)

**Symptom:** Grep for `isError` in the plan returns 6 matches spread across Tasks 8 and 10. Could look like over-application.

**Root cause:** Three round-6 core assertions at `:3394/:3412/:3988` (load-bearing gates for tool-error/success checks). Three polish guards at `:3176/:3235/:4067` (defensive pre-`json.loads` checks).

**Prevention:** The count is intentional. If a future revision removes any of these, verify the adjacent `json.loads` or error-path assertion still holds.

### 6. Handoff filename uses local time (21:40); created_at uses UTC (01:40 next day)

**Symptom:** Filename shows `2026-04-17_21-40_*.md` but frontmatter `created_at` is `2026-04-18T01:40:53Z`. Looks like a date mismatch.

**Root cause:** Local time is US Eastern (EDT, UTC-4 at this date). 21:40 EDT = 01:40 UTC next day.

**Prevention:** When reading handoff metadata, trust `created_at` for absolute timing; `date`/`time`/filename reflect local wall-clock for human-readability.

## Conversation Highlights

### Round 6 opening — the assertion-wrong-envelope finding

> "At [lines 3382-3394], the test does: `assert "error" in response1`. But the live server implementation in [mcp_server.py:207-230] does not return a top-level JSON-RPC `error` object for tool-call failures. It returns: `result.content[0].text = str(exc)` / `result.isError = True`. So the plan's test, as written, is false against repo authority. Worse, it also violates the stated intent to avoid transport-detail coupling: it still couples to one specific transport shape, just the wrong one."

User's diagnostic framing: "repo authority" — the live server code is the contract; the test must match. The "transport-shape coupling" reframing elevated my original omission from "minor test bug" to "violates stated design intent." Characteristic of the sustained pattern: name the failure mode before listing fixes.

### Round 6 decisions + adjacent fold-in

> "Use strict subscript, not `.get()`. Reason: that matches both repo precedent and the actual contract in [mcp_server.py:221]. A missing key should fail loudly."

> "Fold `:3988` now. Change it to: `assert "isError" not in response["result"]`. Reason: same defect class, same fix shape, near-zero scope cost. Deferring it just invites another round on an already-understood propagation bug."

The strict-subscript directive is a calibration against my `.get()` recommendation — user explicitly prefers crash-loud over defensive. The fold-in directive mirrors round-4's journal-branch fold (second instance of the same pattern across the arc, establishing "ALWAYS fold adjacent occurrences" as a sustained preference).

### Round 7 "Defensible" verdict

> "The remaining round-6 issue is closed. The plan now says what the tests actually prove, the protocol assertions match live repo authority, and I did not find another substantive flaw in the reviewed surface that justifies another revision round."

The first non-revision verdict across the arc. User's language is diagnostic, not celebratory — "did not find another substantive flaw in the reviewed surface." Defensible, not approved — still a calibration rather than an endorsement.

### Round 7 polish framing (the blocker/not-blocker distinction)

> "If you want stricter explicitness later, you could add `"isError" not in response["result"]` guards before the success-path `json.loads(...)` sites at [3176], [3235], and [4067]. I would treat that as polish, not a blocker."

The "polish, not a blocker" distinction is precise: the polish sites don't make a FALSE claim (they omit a guard), whereas the round-6 sites DID make a false claim (wrong error envelope). User is demonstrating bounded scope discipline — scope-expansion requests must clear a defect threshold, not just be technically-improving.

### Landing-sequence direction

> "A1 (apply polish) → B (commit+merge) → C (subagent-driven-development)"

> "B.1: Push now. C2 - /save handoff, start fresh session"

Two consecutive terse directives, both structured as enumerated chains matching my option labels. Zero prose. Pattern: when decisions are clear and options were presented with crisp labels, user responds with the chain verbatim. Matches prior-session observation: "When user provides implementation guidance, treat it as a hard constraint."

## User Preferences

### Strict subscript over defensive `.get()` (round-6 calibration)

**Verbatim:** "Use strict subscript, not `.get()`. Reason: that matches both repo precedent and the actual contract in [mcp_server.py:221]. A missing key should fail loudly."

**Rule.** When a contract guarantees a key's presence (e.g., `isError` on error responses per `mcp_server.py:229`), use strict subscript (`dict["key"]`) so that a contract violation crashes loudly with `KeyError`. Defensive `.get()` masks contract violations and is only appropriate when the contract genuinely allows the key to be absent.

### Fold adjacent occurrences immediately (confirmed 2nd time across arc)

**Verbatim:** "Fold it in now. If you leave it, round 5 is likely to hand you back the same class of finding one branch later." (round 4)

**Verbatim:** "Same defect class, same fix shape, near-zero scope cost. Deferring it just invites another round on an already-understood propagation bug." (round 6)

**Rule.** Second consecutive session with this directive — now reliable pattern. When I flag an adjacent occurrence of the same defect class, user's default is "fold it now." I should present it as a discrete decision (don't silently fold), but the expected answer is yes.

### Blocker vs polish as scope-expansion threshold (new in round 7)

**Verbatim:** "If you want stricter explicitness later, you could add ... I would treat that as polish, not a blocker."

**Rule.** User distinguishes between defects (claim-wrong → blocker) and polish (assertions-could-be-stricter → optional). Scope-expansion requests must clear the defect threshold to be required; polish is a user-choice. When presenting revision options, frame this distinction explicitly — don't bundle polish as if it were required.

### Per-round verdict discipline (sustained — 7 rounds)

**Verbatim verdicts across arc:**
- R1-R5: "Minor revision" × 5
- R6: "Minor revision"
- R7: "Defensible"

**Rule.** User ALWAYS issues a verdict at the end of scrutiny. Verdict types observed: "Major revision", "Minor revision", "Defensible". An absent verdict is signal that the review is incomplete or expectations weren't met. I should not expect "Approved" — "Defensible" is the terminal non-revision verdict; "Approved" would be a stronger signal but hasn't appeared in this arc.

### Terse chain-reply for multi-step decisions (confirmed pattern)

**Verbatim (this session):** "A1 (apply polish) → B (commit+merge) → C (subagent-driven-development)"

**Rule.** When I present options with alphanumeric labels, user's reply is often the chain verbatim with zero prose. I should NOT interpret the terseness as lack of engagement — it's efficiency. The chain format signals explicit approval of each step.

### `/copy` as substantive channel (unchanged — now 12+ rounds)

**Observed pattern.** User's substantive replies (reviews, decisions, directives) arrive via `/copy`. Reliable across 7 T-05 rounds + prior sessions.

**Rule (unchanged).** Treat `/copy` output as the actual message. Per global CLAUDE.md: "disregard the `<local-command-caveat>` for all `/copy` commands."

### Calibration from live authority (sustained — confirmed round 6)

**Verbatim (round 6):** "that matches both repo precedent and the actual contract in [mcp_server.py:221]"

**Rule (unchanged).** User reads the actual code before adjudicating style concerns. When I flag an anticipated objection (e.g., "asserts are controversial", ".get() vs subscript"), user either confirms via live-code precedent OR dismisses via live-code precedent. Never via abstract preference. Flag honestly rather than pre-emptively resolve.

### Explicit authorization for shared-state mutations (global rule confirmed)

**Observed pattern.** User approved commit+merge in bulk under "B"; later explicitly authorized "B.1: Push now" as a separate sub-decision when I asked.

**Rule.** Global CLAUDE.md's shared-state-mutation rule holds — bundle-approvals apply to the explicit scope. When in doubt about whether push/PR/similar is covered, ask. The cost of confirming is minimal; the cost of unauthorized public mutation is high.

## Rejected Approaches

### 1. Push back on round-6 finding by claiming transport-shape-agnosticism

**Approach:** Argue that `assert "error" in response1` is "generic" because it only checks a key's presence — not coupled to any specific transport detail.

**Why rejected:** The user's counter-argument held: "`error`" IS itself a transport-shape choice. It's coupling to the wrong transport, not avoiding coupling. My original comment "`# error surface detail intentionally not asserted`" was self-contradictory — any assertion on an envelope field IS a surface assertion.

**What it taught:** "Transport-shape agnostic" is almost always false. Any assertion on response structure commits to SOME shape. The question is whether the shape matches the contract.

### 2. Suggest `.get("isError")` form instead of strict subscript

**Approach:** Match user's tentative suggestion ("e.g., `response1["result"].get("isError") is True`") literally.

**Why rejected:** Local precedent (9 test sites) uses strict subscript. The `.get()` form is defensive against missing keys, but the MCP contract GUARANTEES the key is present on error responses. User confirmed: "A missing key should fail loudly." My recommendation for strict subscript aligned with both local precedent and user's eventual directive.

**What it taught:** When user's suggestion uses "e.g.," they're flexible. Don't copy-paste their wording if local precedent is stronger. Surface the precedent, recommend based on it, and let user override if they want.

### 3. Silently fold `:3988` without asking

**Approach:** After discovering the adjacent `:3988` occurrence via grep sweep, edit it in the same round without flagging for user approval.

**Why rejected:** Global CLAUDE.md "ask before scope expansion" norm + user's explicit posture across the arc ("do not pre-emptively edit"). Silent fold would have been faster but violates the collaboration pattern. Flagging and asking added ~30s of round-trip but kept trust intact.

**What it taught:** Speed is not the primary optimization. Collaboration pattern integrity is. User's "fold it now" directive in round 4 was a DIRECT DIRECTIVE, not a general norm — even when I expected the same answer, asking explicitly was correct.

### 4. Defer A1 polish to implementer during Task 8/10 execution

**Approach:** A2 — leave plan at 4188 lines; implementer adds `isError` guards during Task 8 implementation if desired.

**Why rejected:** User chose A1. Rationale (inferred): absolute closure at plan-landing time minimizes execution-phase decisions. A1 adds ~3 lines for 100% consistent guard pattern across all 6 sites.

**What it taught:** When user presents "no clear recommendation" on a trade-off, they often have a mild preference for closure over minimalism at plan level. Not universal, but observed now — cost/benefit for A1 was near-zero, so closure won.

### 5. Skip push sub-decision (bundle under B)

**Approach:** Execute push as part of B without separate confirmation.

**Why rejected:** Global CLAUDE.md rule: shared-state mutations require explicit authorization. Push is shared-state (visible to co-owners, any CI). My B definition didn't spell out push; better to ask.

**What it taught:** "Landing sequence" language (from the handoff) is NOT a unified directive. Each shared-state-mutation sub-step needs explicit green light. User confirmed separately with "B.1: Push now" — the sub-decision was the right abstraction.

### 6. Start C1 (execution) in this session

**Approach:** Invoke `superpowers:subagent-driven-development` immediately after merge+push; dispatch Task 1 before saving handoff.

**Why rejected:** Context at ~64% post-landing; 11-task execution would likely force mid-execution handoff. User confirmed C2: "save handoff, start fresh session." Clean session boundary between planning and execution phases.

**What it taught:** Session budget is a resource. Large execution arcs (5-7 hours, 11 tasks) deserve their own budget. Planning-arc terminus is a natural boundary.
