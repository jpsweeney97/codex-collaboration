---
date: 2026-04-28
time: "23-56"
created_at: "2026-04-28T23:56:49Z"
session_id: 98186e7a-11a8-45f4-957a-a1f9f51c115e
resumed_from: docs/handoffs/archive/2026-04-28_15-13_candidate-a-attempt-1-canceled-by-15min-approval-ttl.md
project: claude-code-tool-dev
branch: feature/delegate-execution-diagnostic-record
commit: 5a1e937e
title: Candidate A attempt 1 cells filled (canceled-by-approval-timeout); 5 docs revisions applied; context-metrics 1M-window detection bug fixed; attempt 2 pre-authorized as approve-first for next session
type: handoff
files:
  - docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/context-metrics/scripts/config.py
  - packages/plugins/context-metrics/tests/test_config.py
  - packages/plugins/context-metrics/README.md
  - packages/plugins/context-metrics/CHANGELOG.md
  - .tmp/variant-candidate-a.patch
  - .tmp/variant-candidate-a.applied-at
---

# Handoff: Candidate A attempt 1 cells filled; docs defensible; context-metrics fix; attempt 2 pre-authorized approve-first

## Goal

Continue T-20260423-01 live delegate-execution remediation. **This session captured Candidate A attempt 1 evidence into the run record (full post-execution cell fills + Raw excerpts + Attempt history row update), applied 5 reviewer-driven docs-only revisions, and fixed a context-metrics package bug where `claude-opus-4-7` was missing from `MODEL_WINDOWS` (causing 5x denominator misreporting of context occupancy).**

**Bigger picture:** Candidate A is the first variant under test in the diagnostic that aims to characterize what blocks delegated shell execution. Attempt 1 (deny-strategy) ended in `canceled-by-approval-timeout` — its load-bearing finding was that runtime-proofed `'includePlatformDefaults': True` emit + observed parking together refute Baseline's False-platform-defaults explanation. **Attempt 2 (approve-strategy) is the next experiment** — does shell execute past the gate under the True policy?

**Context for the docs revisions:** Initial cell-fill text contained 5 P2/P3 defects spanning denominator semantics (executed vs attempted), terminology overclaim (denied vs parked-then-canceled), source-level-ordering overclaim (upstream-of-sandbox vs before-shell-execution), scope-of-evidence overreach (host repo git status as delegated worktree proof), and missing reader-orientation cue (no scope note that Branch decision table was Baseline-only). All five are now corrected with reviewer's verdict `Defensible`.

**Why the hook fix:** During this session's late stages, the `UserPromptSubmit` hook reported context occupancy as `188k/200k (94%)` then `196k/200k (98%)`, leading me to recommend "save handoff before attempt 2" based on perceived context exhaustion risk. User caught the bug: the actual session capacity is 1M tokens (this is `claude-opus-4-7[1m]`), so the displayed `/200k` denominator was 5x too small. Bug rooted in `packages/plugins/context-metrics/scripts/config.py:19-22` `MODEL_WINDOWS` dict not listing `claude-opus-4-7`. Fixed in 4 files; 98/98 tests pass.

**Stakes:** (a) Attempt 1 evidence is now durable in the run record AND defensible against adversarial review. (b) Context-metrics now correctly reports occupancy for opus-4-7 sessions starting from the first model observation, rather than only after the reactive >200k fallback fires. (c) Attempt 2 is pre-authorized as approve-first per user instruction — to be executed in the next session with TTL-aware operator-loop discipline.

## Session Narrative

Resumed from `2026-04-28_15-13_candidate-a-attempt-1-canceled-by-15min-approval-ttl.md`. Prior session left attempt 1 in canceled state with all evidence durable on disk (audit, jobs, requests, journal JSONL stores + runtime-proof log) but with ~25 post-execution cells in the variant block still tagged `TBD (post-execution; expected source: X)`.

**Phase 1 — Pre-flight (Next Steps #2 from prior handoff).** Ran 5 checks in parallel: PIDs, runtime.py diff size, patch metadata, runtime-proof log line count, HEAD + working-tree shape. **Plugin had restarted between sessions** (PIDs flipped from `64122/64184/64213` → `62803/62852/62874`) — this was anticipated by prior handoff's risk #5. Re-derived plugin start UTC: `Tue Apr 28 16:04:02 2026` lstart → `2026-04-28T20:04:02Z` (epoch round-trip via `date -j -f` then `date -u -r`). Ordering check: plugin start `20:04:02Z` > patch applied `17:12:59Z` ✓ (delta +10,263s = +2h51m). **Variant validity preserved** under the project's restart-as-reload discipline: patch on disk + plugin started after patch + runtime-proof from prior session still has True flag.

**Phase 2 — Cell filling (Next Steps #3).** Inspected JSONL stores via shell + Python parsing:
- **Audit:** 2 rows for job `4ebd24d6-…` (L65 delegate_start `actor=claude` `17:51:27Z`; L66 approval_timeout `actor=system` `18:06:37Z`; delta exactly 15m10s)
- **Jobs:** 7-row lifecycle (queued → running → parked(0) → needs_escalation → running [post-timeout unpark] → parked(cleared) → canceled)
- **Requests:** 2 rows (L1 op:create with full 6-option `available_decisions` confirming `untrusted` mode + full chain in `requested_scope.command`; L2 op:record_timeout with `response_payload: {decision: cancel}` and `timed_out: true` — system-fabricated cancel decision)
- **Journal:** 6 rows (L1-L3 job_creation 3 phases at 17:51:25Z; L4-L6 approval_resolution 3 phases at 18:06:37Z, all with `decision: None` — system-flow signature)

Made 25 targeted Edit calls to fill cells, then 1 for Attempt history row, then 1 for Raw excerpts. Verified: zero `TBD (post-execution` markers remained in attempt 1 evidence (only the preamble's literal description text matched grep); markdown table well-formed (4 pipes per row, with the L837 8-pipe pattern from escaped `\|` in `ps -ef \| grep` being a pre-existing convention); code-fence balance preserved (15 pairs).

**Phase 3 — Recommended commit; user routed through scrutiny review instead.** I proposed: commit cell fills now as a coherent buildable chunk. User responded with `/copy` followed by a 5-finding adversarial review:
- **F1 (P2, ratio):** denominator should be attempted (not executed); `1/0` should be `1/1 = 1.0` per template + Baseline pattern.
- **F2 (P2, terminology):** "denied at the approval gate" wrong because attempt 1 was parked-then-canceled, not denied; replace with "parked at command_approval, then canceled by approval_timeout before execution".
- **F3 (P2, mechanism overclaim):** "upstream of the sandbox readability check" overclaims source-level App Server ordering; replace with "approval gating still fired under the True policy before any shell execution; sandbox readability is not proven as the cause of parking".
- **F4 (P3, scope of evidence):** host repo `git status` cannot prove the delegated worktree was untouched; conclusion must source from request/job lifecycle + DelegationJobStore `artifact_paths: []`.
- **F5 (P2, scope note):** Branch decision table at L1053 still reads as live; needs Baseline-only scope note + explicit "Candidate A attempt 1 deferred adjudication pending attempt 2".

Reviewer's recommendation: apply revisions, re-review docs, then proceed to **Candidate A attempt 2 approve-first** (not deny-first).

**Phase 4 — Applied all 5 revisions.** Each as a targeted Edit:
- F1 → `shell_action_count` cell (L845) + ratio cell (L848): adopted attempted-denominator semantics with dual-reason "no signal" (denominator < 3 AND zero executed)
- F2 → shell_action_count (L845) + Attempt history row (L915): "parked at `command_approval`, then canceled by `approval_timeout`"
- F3 → First parked request id (L843) + full.diff (L853) + Attempt history (L915): replaced "upstream of sandbox readability check" with phenomenological language ("before any shell execution"), explicitly noting source-level ordering inside App Server is not established
- F4 → Post-run dirty diff (L864): added scope-of-evidence note distinguishing host checkout from delegated worktree, re-sourcing the "no execution" conclusion to lifecycle + artifact-store
- F5 → Branch decision section (L1053-1055): heading changed to "Branch decision (Baseline attempt 1 only):"; inserted scope-note paragraph above the table

Verification: all overclaim phrases gone from Candidate A block (`awk NR>=826 && /upstream of/` returns 0 rows); 3 instances of new wording "sandbox readability is not proven" present (matches 3 revised cells); code-fence balance preserved (15 pairs); file grew 1129 → 1131 lines.

**Phase 5 — Reviewer re-passed; verdict `Defensible`.** Second `/copy` from user contained a structured scrutiny: premise check, critical failures (none), high-risk assumptions (operator loop must land approve inside TTL), real-world breakpoints, hidden dependencies, adversarial perspectives applied, patterns and root causes ("attempt-1 evidence was being asked to answer attempt-2 questions"), required changes before credible (none), verdict `Defensible`. Recommended next steps: trash runtime-proof log → fire delegate_start → approve request 0 immediately within TTL → poll to terminal → fill attempt 2 cells.

**Phase 6 — I recommended save-handoff based on bad context-budget data.** I cited "94% (188k/200k)" as the dominant risk and applied prior session's D5 reasoning ("attempt 2 needs budget headroom; don't fire under context pressure"). Two-decision split was: (A) docs ready? Yes per reviewer. (B) is THIS session right place? Said no based on context budget. Three options: save handoff first, fire attempt 2 immediately (matches reviewer literal), commit-then-save-then-attempt-2-fresh.

**Phase 7 — User asked clarifying question that revealed conceptual confusion.** User: "What do you mean by 'operator-side latency consumed the window'? Does 'window' refer to the context window of the Claude Code session?" I clarified: window = 15-minute approval TTL window, NOT context window. Two distinct constraints; my prior message conflated them by juxtaposition. Apologized for the conflation and re-stated the recommendation around the cleaner reason: shorten operator loop in TTL race.

**Phase 8 — User asked for ELI5 glossary.** Listed `delegate_start parked`, `runtime-proof line`, `decide(deny)`, `TTL`, `TTL race`, `auto-cancel`, `actor=system`, `operator`, "and all other terms like these from codex-collaboration". I produced a multi-section glossary covering ~25 terms organized by Cast of Characters / Delegate flow / Decisions / TTL stuff / Audit fields / Runtime-proof / Other recurring terms. The glossary is in the conversation only — not persisted to a file.

**Phase 9 — User caught the context-metrics bug.** User: "What do you see as the session context percentage right now?" I said 98% extrapolated from prior turn. User's next prompt's hook header said `203k/1M tokens (20%)`, and user said: "That is valuable information - it tells me that the hook needs to be updated. The reason: the context window for each session is 1000000, not 200000."

**Phase 10 — Withdrew save recommendation; flipped premise.** Prior recommendation was based on perceived 94-98% occupancy. Actual was 20%. The TTL-race concern was still valid but separable. Offered (a) fix hook first, (b) proceed to attempt 2, (c) both. User chose: fix hook + audit context-metrics for other staleness, then save handoff with explicit content requirements; do not fire attempt 2; do not commit; do not restore runtime.py.

**Phase 11 — Hook fix.** Located the bug at `packages/plugins/context-metrics/scripts/config.py:19-22`: `MODEL_WINDOWS` listed `claude-opus-4-6` and `claude-sonnet-4-6` but not `claude-opus-4-7`. The reactive `maybe_upgrade_window(observed_occupancy)` at L47 only fires when occupancy > 200k — that's why displayed % was wrong until we crossed the threshold. Audited for other staleness:
- `claude-haiku-4-5` correctly omitted (default 200k matches Haiku's actual context size; test at `test_config.py:75-76` confirms intentional)
- README.md model table at L146-149 lists same 2 models — needs opus-4-7 row
- CHANGELOG.md Unreleased section mentions same 2 models in Added entry — needs update + new Fixed entry

Made 4-file fix: config.py adds `"claude-opus-4-7": 1_000_000`; test_config.py adds 2 new tests (`test_opus_4_7_detects_1m`, `test_opus_4_7_with_1m_suffix_detects_1m` — defensive against the `[1m]` suffix variant); README.md adds opus-4-7 row; CHANGELOG.md adds Fixed entry + updates Added entry.

**Phase 12 — Verified hook fix.** Ran `uv run pytest` from package directory: 98/98 tests pass including the 2 new opus-4-7 tests. No regressions.

**Phase 13 — Save handoff (this).** Per user's explicit content requirements (enumerated in Decisions D5 below).

## Decisions

### D1: Apply all 5 docs revisions before attempt 2

**Choice:** Accept reviewer's F1-F5 findings without pushback; apply each as a targeted Edit; verify aggregate via grep + structural checks.

**Driver:** User routed reviewer feedback via `/copy` with explicit Recommendation lines. Per carried preference (`feedback_copy_awaiting_means_act.md`): "Awaiting your next [action]" closing line IS the action request. Reviewer's verdict cycle was structured as: review → revise → re-review → proceed.

**Rejected alternatives:**
- **Argue with F3 (mechanism revision claim was load-bearing for our findings, the strong wording felt important).** Rejected: review correctly identified the source-level-ordering claim was unsupported; "approval gating fired before any shell execution" is the defensible phenomenological claim and loses no analytic power.
- **Apply F1-F2 only (small fixes), defer F3-F5 to a future session.** Rejected: user instruction was to apply all 5 in one cycle; partial application creates re-review debt and inconsistent docs across cells.

**Implication:** Run record's Candidate A block now uses bounded language throughout. Branch decision table has explicit Baseline-only scope. The mechanism revision finding is preserved (refutes Baseline's False-platform-defaults explanation) but no longer overstates its reach (does not claim source-level ordering inside App Server). Future cell-fill work for attempt 2 inherits cleaner conventions.

**Trade-offs accepted:** Slightly more verbose cell text (each revised cell gained ~30-50 chars of qualifying language). Some claims that "felt punchy" (e.g., "upstream of sandbox readability check") became more cautious — at the cost of rhetorical force, but at the gain of defensibility against future evidence.

**Confidence:** High (E2) — both reviewer's two passes converged on the same 5 findings; my own re-grep of the file post-revision confirmed structural integrity.

**Reversibility:** High — markdown edits trivially revertable. If attempt 2 produces evidence that VALIDATES the source-level-ordering claim (e.g., approve under True flag fails with sandbox-level error), the docs can be re-strengthened then.

**Change trigger:** If attempt 2's approve-strategy succeeds (shell executes, artifacts produced), F3's "sandbox readability not proven as cause" should remain conservative until separate Candidate B / trusted-mode tests provide affirmative evidence. If attempt 2 fails (shell still blocked under True flag + approve), THEN we have evidence for "sandbox is also blocking downstream" but still don't have App Server source-level ordering.

### D2: Withdrew save-handoff recommendation when context % was wrong; re-ratified on user's explicit instruction

**Choice:** When user reported corrected `203k/1M (20%)` reading, I withdrew my prior "save handoff first" recommendation as based on false premise. Then user issued explicit instruction: fix hook, save handoff, do not fire attempt 2 in this session. I executed per instruction.

**Driver (initial recommendation):** Hook displayed `196k/200k (98%)` — interpreted as imminent context exhaustion + applied prior session's D5 logic ("attempt 2 needs budget headroom"). User correction revealed the denominator was 5x too small; actual budget allows attempt 2 in this session.

**Driver (re-ratification):** User's explicit instruction overrode my flipped recommendation. Per global CLAUDE.md priority: explicit user request > my recommendation > defaults. User had additional stated reasons (split phases for cleanliness; preserve attempt 2 for fresh-session execution with deliberate pre-authorization).

**Rejected alternatives (in flipped state):**
- **Proceed directly to attempt 2 once context % was corrected.** Rejected: user's explicit instruction took precedence; I shouldn't re-litigate after correction landed.
- **Fix hook AND fire attempt 2 in same session.** Rejected: same precedence reasoning. Also user enumerated specific things to NOT do (not commit, not restore, not fire attempt 2), which are stronger than guidance.

**Implication:** This handoff exists. Attempt 2 is preserved as next-session work. Bundled-closure pattern remains intact (no premature commit). Runtime.py stays dirty.

**Trade-offs accepted:** Lost a chance to land attempt 2 evidence in this session (would have been cheaper budget-wise once hook was fixed). Gained: cleaner phase boundary; attempt 2 gets fresh-session deliberation rather than tail-end-of-current-session execution.

**Confidence:** High (E2) — user's instruction was unambiguous and enumerated.

**Reversibility:** N/A — saving handoff is purely additive.

**Change trigger:** Never — clean session boundaries are the project pattern.

### D3: Add `claude-opus-4-7` to MODEL_WINDOWS (not Haiku 4.5)

**Choice:** Single-line addition to `packages/plugins/context-metrics/scripts/config.py:19-22`: insert `"claude-opus-4-7": 1_000_000,` as the first entry. Leave `claude-haiku-4-5` unmapped (defaults to 200k via the Config class default, which is correct since Haiku 4.5 has 200k context).

**Driver:** Bug observation — this session's model id is `claude-opus-4-7[1m]` (per env). `MODEL_WINDOWS` had only opus-4-6 and sonnet-4-6 entries. The prefix-match logic at `config.py:41-45` therefore did NOT detect this session's model → window stayed at 200k default → reactive `maybe_upgrade_window` only fired when occupancy crossed 200k (5x mis-display until then).

**Rejected alternatives:**
- **Add Haiku 4.5 explicitly as 200k.** Rejected: existing convention is to list only non-default windows. Adding a dict entry mapping to the default value is dead code; `test_unknown_model_keeps_default` at `test_config.py:73-76` already confirms Haiku's correct behavior under default.
- **Architectural rework: detect window from JSONL transcript's `usage` field directly rather than via model name.** Rejected: out of scope ("anything that needs updating" was bug-fix-and-staleness-audit, not architectural). Existing 3-tier mechanism (explicit config > model detection > occupancy fallback) is sound; just needs the missing entry.
- **Skip the `[1m]` suffix variant test (it's covered by prefix match anyway).** Rejected: defensive testing — the explicit suffix test at `test_config.py:64-67` documents that the prefix matcher handles bracket-suffixed variants, which protects against a future change to that logic.

**Implication:** Sessions on `claude-opus-4-7` (with or without `[1m]` suffix) now correctly display `Nk/1M tokens (X%)` from the first model observation onward. The reactive fallback still exists for unknown future models. Test coverage now documents the suffix-handling expectation.

**Trade-offs accepted:** Adds one more entry to maintain when Anthropic releases new models. Mitigation: the file is small and the reactive fallback covers gaps gracefully.

**Confidence:** High (E2) — bug reproduces in this session's hook output; fix verified via 98/98 test pass; new tests directly target the failure mode.

**Reversibility:** High — single-line revert.

**Change trigger:** If `claude-opus-4-7` ever ships with a 200k variant (e.g., `claude-opus-4-7-200k`), the prefix matcher would incorrectly upgrade it to 1M. Mitigation in that case: more specific prefix (e.g., `claude-opus-4-7[1m]` mapped to 1M only) + explicit 200k entry for the bare/200k variant. Or use the `_explicitly_set` config override.

### D4: Test new model with both bare and `[1m]` suffix variants

**Choice:** Added 2 tests: `test_opus_4_7_detects_1m` (bare prefix) AND `test_opus_4_7_with_1m_suffix_detects_1m` (with `[1m]` bracket suffix).

**Driver:** This session's exact model id is `claude-opus-4-7[1m]`. The bracket suffix is an actual format that appears at runtime. Test should document that prefix-match handles bracket-suffixed variants.

**Rejected alternative:** Test only the bare form. Rejected: leaves the bracket-suffix behavior implicit; future refactor of `detect_window_from_model` could break suffix handling silently.

**Implication:** The test suite now documents an expected behavior of the prefix matcher (handles `[1m]` suffix). If anyone changes the matcher logic to be more strict, the suffix test breaks loudly.

**Trade-offs accepted:** Two tests instead of one (~8 lines extra in test_config.py). Trivial cost.

**Confidence:** High (E2) — both tests run and pass.

**Reversibility:** High — test removal trivial.

**Change trigger:** If model id format changes (e.g., suffix moves to a separate field), update or remove the suffix test.

### D5: Save handoff per user's explicit instruction; do not commit; do not fire attempt 2; do not restore runtime.py

**Choice:** Execute exactly per user's enumerated content requirements:
1. Docs are now defensible after the 5 docs-only revisions ✓
2. Candidate A attempt 1 is recorded as canceled-by-approval-timeout ✓
3. Attempt 2 is approved as the next execution step, approve-first ✓
4. Runtime.py remains intentionally dirty with the Candidate A patch ✓
5. Before attempt 2, trash `/tmp/codex-collab-candidate-a-runtime-proof.log` (append-mode; attempt 1's line preserved in run record) ✓
6. Next session: same canonical smoke prompt, approve request 0 immediately within TTL, poll to terminal, fill attempt-2 cells incl. required probes if execution proceeds, adjudicate Branch decision, restore runtime.py, commit full Candidate A closure bundle ✓

**Driver:** User explicit instruction. "1. Fix the hook first... 2. Then save a handoff. Do not fire Candidate A attempt 2 in this session, do not commit, and do not restore runtime.py." Plus enumerated 6 preservation requirements.

**Rejected alternatives:**
- **Commit cell fills + 5 revisions first, then save handoff.** Rejected: explicit "do not commit" overrides global CLAUDE.md commit-proactively guidance. Per project's bundled-closure pattern, variant closure bundle (attempt 1 + attempt 2 + restoration) should be one commit anyway.
- **Save handoff but include "consider firing attempt 2 in this session" as an option.** Rejected: user's explicit "do not fire" is a directive, not a suggestion to weigh.
- **Restore runtime.py before saving handoff to leave a cleaner working tree.** Rejected: explicit "do not restore"; preserves the in-memory patched state for next session's attempt 2 (avoids needing operator restart cycle).

**Implication:** Working tree stays dirty across session boundary: `M runtime.py` (Candidate A patch — intentional), `M docs/diagnostics/...` (run record edits, intentional), 4 `M` files in `packages/plugins/context-metrics/` (hook fix), 8 carry-forward `D + ??` rows. Plugin in-memory code is PATCHED; if user restarts before next session, the patched runtime.py is still on disk so post-restart import re-acquires it (per Baseline + Candidate A att1 pattern).

**Trade-offs accepted:** This handoff is the only artifact. No commit; no attempt 2 evidence. Dirty working tree spans many concerns (run record + plugin source + context-metrics package). Risk: if a future session reads `git status` and assumes the runtime.py mod is unintended, they might accidentally restore it.

**Mitigation:** This handoff explicitly enumerates the dirty state and its intent. Pre-flight in next session must verify runtime.py diff is unchanged (~37 lines, sha256 matches `.tmp/variant-candidate-a.patch`) before attempt 2.

**Confidence:** High (E2) — instruction was explicit and enumerated; I'm executing literally.

**Reversibility:** N/A — handoff is additive.

**Change trigger:** Never — clean session boundaries are the project pattern; user's explicit phasing decision overrides my prior judgment about commit timing.

## Changes

### `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — 25+ post-execution cells filled + Attempt history + Raw excerpts + 5 docs revisions + Branch decision scope note

**Purpose:** Complete the Candidate A attempt 1 evidence capture so the variant block is a self-contained artifact independent of attempt 2.

**Approach:** Targeted Edit calls for each cell, sourcing all content from disk evidence (audit JSONL, jobs JSONL, requests JSONL, journal JSONL, runtime-proof log). Verified structural integrity after each batch (markdown table pipe count, code-fence balance, no `TBD (post-execution` markers remaining).

**Key implementation details:**
- File grew from 1087 → 1131 lines (+44 net: ~+42 from cell evidence, +2 from F5's scope-note paragraph)
- Variant block bounds: `### Variant: Candidate A` at L826 → `## Threshold Calibration` at L965 (139 lines, was 97)
- 25 post-execution cells filled with explicit source citations (PendingRequestStore L1/L2, DelegationJobStore L1-L7, OperationJournal L1-L6, Audit L65-L66, runtime-proof log)
- Attempt history row 1 updated with `1 attempted; 0 executed (parked at command_approval, then canceled by approval_timeout)`, mechanism-revision finding (with cautious phrasing per F3), TTL discovery
- Raw excerpts block (L917-L962) populated with start() response, runtime-proof verbatim line, decide(deny) rejection payload, final poll() snapshot, cross-store timestamp consistency table
- 5 reviewer-driven revisions:
  - F1 (L845, L848): adopted attempted-denominator semantics (`1/1 = 1.0`; "no signal" with dual reason)
  - F2 (L845, L915): "denied at approval gate" → "parked at `command_approval`, then canceled by `approval_timeout` before execution"
  - F3 (L843, L853, L915): "upstream of the sandbox readability check" → "approval gating still fired under the True policy before any shell execution; sandbox readability is not proven as the cause of parking" + explicit acknowledgment that source-level App Server ordering not established
  - F4 (L864): added scope-of-evidence note distinguishing host checkout from delegated worktree; conclusion sourced to lifecycle + DelegationJobStore artifact_paths + artifact_hash
  - F5 (L1053-1055): "Branch decision:" → "Branch decision (Baseline attempt 1 only):" with scope-note paragraph

**Future-Claude note:** Variant restoration cell, restoration verification, and cleanup cells are deliberately deferred to "after Candidate A attempt 2 completes" per VIP step 7 (restoration is once-per-variant, not once-per-attempt). Probe cells (Network, Sensitive-path, Sibling-worktree) record "Not run in attempt 1; deferred because request 0 timed out before operator decision" and explicitly remain REQUIRED for Candidate A overall closure (will be exercised in attempt 2 if approve lands).

### `packages/plugins/context-metrics/scripts/config.py` — Added `claude-opus-4-7` to MODEL_WINDOWS

**Purpose:** Bug fix — sessions on Opus 4.7 were displaying wrong context-window denominator.

**Approach:** Single-line addition to the dict literal, preserving existing entries.

**Diff:**
```python
 MODEL_WINDOWS: dict[str, int] = {
+    "claude-opus-4-7": 1_000_000,
     "claude-opus-4-6": 1_000_000,
     "claude-sonnet-4-6": 1_000_000,
 }
```

### `packages/plugins/context-metrics/tests/test_config.py` — Added 2 tests

**Purpose:** Verify the fix + document expected suffix-handling behavior.

**New tests** (in `TestModelDetection` class, before existing `test_opus_4_6_detects_1m`):
- `test_opus_4_7_detects_1m` — bare `claude-opus-4-7` prefix
- `test_opus_4_7_with_1m_suffix_detects_1m` — `claude-opus-4-7[1m]` (the actual session model id format)

### `packages/plugins/context-metrics/README.md` — Added opus-4-7 row to supported model table

**Purpose:** Keep README's "Context window auto-detection" table in sync with code.

**Diff** (at L146-149):
```markdown
 | Model prefix | Window size |
 |-------------|-------------|
+| `claude-opus-4-7` | 1,000,000 |
 | `claude-opus-4-6` | 1,000,000 |
 | `claude-sonnet-4-6` | 1,000,000 |
```

### `packages/plugins/context-metrics/CHANGELOG.md` — Added Fixed entry + updated Added entry

**Purpose:** Document the bug + fix in the Unreleased section.

**Changes:**
- Updated Added bullet to list opus-4-7 alongside existing models, plus a parenthetical noting suffix variants are supported
- Added new Fixed bullet explaining the bug and its symptom: "`claude-opus-4-7` not in `MODEL_WINDOWS` — sessions on Opus 4.7 displayed `Nk/200k tokens` until occupancy crossed 200k and the reactive `maybe_upgrade_window` fallback fired. Now detected as 1M from first model observation."

### Plugin data root — new artifacts from this session (READ-ONLY, no writes)

This session was read-only against the plugin data root. No new audit rows, no new jobs rows, no new requests rows beyond what attempt 1 already produced (and prior session's handoff already documented). The session's only production-side activity was docs editing + code editing.

### Conversation-only artifact — ELI5 glossary (NOT persisted to file)

User requested an ELI5 explanation of codex-collaboration terminology (`delegate_start parked`, `runtime-proof line`, `decide(deny)`, `TTL`, `TTL race`, `auto-cancel`, `actor=system`, `operator`, "and all other terms like these from codex-collaboration"). Produced a multi-section glossary covering ~25 terms organized by Cast of Characters / Delegate flow / Decisions / TTL stuff / Audit fields / Runtime-proof / Other recurring terms. **The glossary lives only in this conversation's transcript** — not persisted to a file. If glossary preservation is valuable for future sessions, the next session could distill it into `docs/references/codex-collaboration-glossary.md` or similar.

### No commits this session

Per user explicit instruction. Working tree dirty: `M runtime.py` (Candidate A patch, intentional), `M docs/diagnostics/...` (run record), 4 `M` files in context-metrics (hook fix), 8 carry-forward ticket-file moves.

## Codebase Knowledge

### Files read this session

| File | Why read | Understanding gained |
|------|----------|----------------------|
| `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` lines 820-922 | Map existing variant block structure before edits | Variant block bounds + cell template format + Attempt history + Raw excerpts placeholder; identified TBD cells to fill |
| `~/.claude/plugins/data/codex-collaboration-inline/audit/events.jsonl` (grep for job_id) | Source for audit cells | 2 rows: L65 delegate_start `actor=claude` 17:51:27Z; L66 approval_timeout `actor=system` 18:06:37Z (delta 15m10s exact) |
| `~/.claude/plugins/data/codex-collaboration-inline/delegation_jobs/15267690-…/jobs.jsonl` | Source for jobs lifecycle cells | 7-row lifecycle: queued → running → parked(0) → needs_escalation → running [post-timeout unpark] → parked(cleared) → canceled |
| `~/.claude/plugins/data/codex-collaboration-inline/pending_requests/15267690-…/requests.jsonl` | Source for request shape + terminal state | L1 op:create with full 6-option `available_decisions` (`untrusted` mode signature), full chain in `requested_scope.command`, `codex_thread_id`, `codex_turn_id`, `item_id`; L2 op:record_timeout with `response_payload: {decision: cancel}` (system-fabricated), `dispatch_result: succeeded`, `timed_out: true` |
| `~/.claude/plugins/data/codex-collaboration-inline/journal/operations/15267690-….jsonl` | Source for journal cell | 6 rows in 2 operations of 3 phases each: L1-L3 job_creation (intent → dispatched → completed) at 17:51:25Z; L4-L6 approval_resolution (intent → dispatched → completed) at 18:06:37Z, all with `decision: None` (system-flow signature) |
| `/tmp/codex-collab-candidate-a-runtime-proof.log` | Source for Observed sandboxPolicy payload cell | 1 line, 533 bytes, verbatim policy emit with `'includePlatformDefaults': True` confirmed at build site |
| `packages/plugins/context-metrics/` (full inventory) | Audit context-metrics for the hook bug + other staleness | Plugin structure: scripts/ (config, formatter, server, jsonl_reader, hooks), tests/ (98 tests), hooks/hooks.json, README.md, CHANGELOG.md |
| `packages/plugins/context-metrics/scripts/config.py` | Locate the MODEL_WINDOWS bug | `DEFAULT_WINDOW=200_000`, `UPGRADE_WINDOW=1_000_000`, MODEL_WINDOWS at L19-22 (missing opus-4-7), `detect_window_from_model` prefix-matches at L41-45 (one-shot per sidecar lifetime), `maybe_upgrade_window` reactive fallback at L47 (only fires when observed > 200k) |
| `packages/plugins/context-metrics/tests/test_config.py` | Understand existing test patterns | 21 existing tests in 3 classes (TestReadConfig, TestModelDetection, TestAutoDetection); `test_dated_model_variant_matches_prefix` at L68-71 documents prefix-match for dated variants; `test_unknown_model_keeps_default` at L73-76 documents Haiku 4.5 default behavior |
| `packages/plugins/context-metrics/README.md` lines 130-160 | Find the supported-model table for sync update | Table at L146-149 with 2 model prefixes; "Context window auto-detection" section explains 3-tier mechanism (explicit config > model detection > occupancy fallback) |
| `packages/plugins/context-metrics/CHANGELOG.md` | Find Unreleased section for new entries | Standard Keep-a-Changelog format; Unreleased section has Added + Fixed bullets; 0.1.0 release at 2026-02-28 |

### Architecture: context-metrics window detection

3-tier mechanism for resolving the context-window denominator:

| Priority | Mechanism | Code location | Trigger |
|---|---|---|---|
| 1 | Explicit config | `read_config()` at L59-79 reads `~/.claude/context-metrics.local.md` YAML frontmatter; `_explicitly_set: True` blocks tiers 2 and 3 | User-controlled |
| 2 | Model detection | `detect_window_from_model()` at L32-45 prefix-matches against `MODEL_WINDOWS` dict; one-shot per sidecar lifetime | First model observation in JSONL transcript |
| 3 | Occupancy fallback | `maybe_upgrade_window()` at L47-56 sets window to 1M when `observed_occupancy > 200_000`; blocked if explicit OR model already detected | Reactive — fires only after threshold crossed |

**Bug semantics:** Tier 2 silently fails if model isn't in MODEL_WINDOWS (no error, no log — just returns from the for-loop unchanged). Tier 3 then runs but only AFTER occupancy crosses 200k. So early session shows wrong %, then auto-corrects after enough conversation accumulates. The fix ensures tier 2 succeeds for opus-4-7 from the first model observation.

### Architecture: codex-collaboration delegate flow (from cell-fill investigation)

| Layer | Location | Role this session |
|---|---|---|
| Sandbox policy builder | `packages/plugins/codex-collaboration/server/runtime.py:23-50` | Builds `workspaceWrite` policy with True flag (Candidate A patch); emits to runtime-proof log; returns dict |
| Plugin process chain | `62803 (claude)` → `62852 (uv)` → `62874 (python)` | Three-layer codex-collaboration plugin process tree; python child holds the imported runtime.py; restarted between prior session and this session (PIDs flipped from `64xxx` to `62xxx`) |
| App Server | Codex CLI 0.125.0 spawned per delegation | Receives sandbox policy from plugin; gates approval BEFORE shell execution under untrusted mode (per attempt 1 evidence) |
| DelegationJobStore | `<plugin-data-root>/delegation_jobs/<session-uuid>/jobs.jsonl` | Per-session JSONL; tracks job lifecycle via op-typed rows (create, update_status_and_promotion, update_parked_request); canonical for terminal status |
| PendingRequestStore | `<plugin-data-root>/pending_requests/<session-uuid>/requests.jsonl` | Per-session JSONL; L1 op:create captures request shape + `available_decisions`; L2+ op:record_timeout / op:record_decision capture terminal payloads |
| OperationJournal | `<plugin-data-root>/journal/operations/<session-uuid>.jsonl` | Per-session JSONL; 3-phase rows per operation (intent → dispatched → completed); `decision: None` is system-flow signature |
| Audit | `<plugin-data-root>/audit/events.jsonl` | Single shared file; rows tagged by `actor` (`claude` for orchestrator-initiated, `system` for automation like `approval_timeout`) |
| Approval TTL | UNKNOWN config location (open question) | Hard ~15-minute window between `delegate_start` and `approval_timeout` (auto-cancel via system-fabricated `cancel` decision) |

### Patterns identified (this session)

- **MODEL_WINDOWS-as-allowlist**: only non-default windows are listed; default 200k is implicit. Adding entries that map to default value is dead code.
- **Reactive fallback + proactive detection**: when proactive (model detection) fails silently, reactive (occupancy crossing threshold) compensates. The combination is robust to missing model entries but produces wrong early-session readings — bug surface area is "first 200k tokens of any unrecognized model."
- **Explicit prohibitions in handoff format**: user prefers enumerated "do not X" lists over implicit guidance. This session's instruction included 3 prohibitions (do not commit, do not restore, do not fire attempt 2) and 6 preservation requirements. Handoff content must mirror these.
- **System-fabricated decision payloads**: when TTL fires, plugin/App Server synthesizes a `decide(cancel)` and dispatches through the same code path as operator decides. Three independent stores record this differently: PendingRequestStore L2 carries the synthetic `cancel` payload; Audit carries `actor=system`; OperationJournal carries `decision: None`. **Pattern: when investigating a "no operator did this" event, check all three stores; each captures a different facet.**
- **Bracket suffix in model id**: `claude-opus-4-7[1m]` is a real format. `model.startswith("claude-opus-4-7")` correctly handles it. Defensive testing should include the suffixed form.

### Surprising findings (this session)

- **The hook fix's bug had been masked by the reactive fallback** — `maybe_upgrade_window` correctly upgraded once we crossed 200k, so we never saw a "stuck at 200k all session" failure. We saw a "wrong early then auto-corrects" failure, which is harder to notice but actively misleads decisions made in the wrong-early phase. (My save-handoff recommendation in this session was made during the wrong-early phase.)
- **Test coverage caught nothing** because the 21 existing tests covered opus-4-6 and sonnet-4-6 explicitly but had no assertion that "every supported Anthropic model is mapped." This is a gap-by-omission rather than a regression.
- **Reviewer was right about every finding.** I had no pushback; all 5 revisions felt correct on first reading. Pattern: when the reviewer's issues are all P2/P3 and convergent, the underlying work was substantively correct but had calibration issues — fix all of them in one cycle and trust the verdict.
- **User's catching of the hook bug came as a 2-step process**: first they asked "what context % do you see?" (sounds like just-curious), then I reported 98%, then they revealed the actual hook reading 20% on their next prompt and named the cause. **Lesson: when the user asks a measurement question, they may already have the ground truth and be diagnosing a sensor.**

### Key locations

| Concept | Location |
|---|---|
| Sandbox policy builder (post-patch, live) | `packages/plugins/codex-collaboration/server/runtime.py:23-50` |
| Run record (live HEAD: `5a1e937e` + dirty cell fills + dirty 5 revisions + dirty Branch decision scope note) | `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` |
| Candidate A variant block | run record L826-L965 (was L826-L922; grew +42 lines from cell evidence + scope note) |
| Branch decision section (Baseline-only scope note added) | run record L1053-L1055 + table at L1057+ |
| Context-metrics MODEL_WINDOWS dict | `packages/plugins/context-metrics/scripts/config.py:19-22` |
| Context-metrics test suite | `packages/plugins/context-metrics/tests/` (98 tests) |
| Candidate A att1 audit rows | `audit/events.jsonl` L65-L66 |
| Candidate A att1 jobs lifecycle | `delegation_jobs/15267690-…/jobs.jsonl` (7 rows) |
| Candidate A att1 requests (shape + terminal) | `pending_requests/15267690-…/requests.jsonl` (2 rows) |
| Candidate A att1 journal (operations) | `journal/operations/15267690-….jsonl` (6 rows) |
| Candidate A att1 runtime-proof | `/tmp/codex-collab-candidate-a-runtime-proof.log` (1 line, 533 bytes) — must trash before attempt 2 |
| Patch capture | `.tmp/variant-candidate-a.patch` (sha256 `4df1df3999…`) |

## Context

### Project State

| Item | State |
|------|-------|
| Branch | `feature/delegate-execution-diagnostic-record` at `5a1e937e` (in sync with origin) |
| Run record | Live HEAD includes Candidate A variant block fully populated (25+ post-execution cells filled, 5 revisions applied, Raw excerpts, Branch decision scope note) |
| Run Identity table | Frozen at `49d93001`; live drift to `5a1e937e` |
| Candidate A att1 outcome | **canceled-by-approval-timeout** at +15m10s after start (NOT deny-completed, NOT approve-tested, NOT Candidate A execution failure) |
| Candidate A att1 mechanism finding | Runtime-proofed `'includePlatformDefaults': True` emit + observed parking together refute Baseline's False-platform-defaults explanation. Defensible claim: "approval gating still fired under the True policy before any shell execution; sandbox readability is not proven as the cause of parking." (Source-level App Server ordering NOT established — requires approve-path run or source inspection.) |
| Plugin process | PIDs `62803/62852/62874` (changed from prior session's `64xxx`); started `2026-04-28T20:04:02Z` (+2h51m after patch); in-memory code is PATCHED (Candidate A: True flag + `[CANDIDATE_A]` instrumentation) |
| Candidate A patch on disk | Still applied (NOT restored) — preserved for attempt 2 per user instruction |
| Patch applied at | `2026-04-28T17:12:59Z` (unchanged across sessions) |
| Approval TTL constraint | ~15 minutes (config location still UNKNOWN — open question) |
| Context-metrics fix | 4 files modified (config.py, test_config.py, README.md, CHANGELOG.md); 98/98 tests pass; uncommitted |
| Working tree | Dirty: `M runtime.py` + `M docs/diagnostics/...` + 4 `M` files in `packages/plugins/context-metrics/` + 8 carry-forward `D + ??` ticket-file moves |
| Runtime-proof log | 1 line on disk (attempt 1 emit, verbatim preserved in run record `Observed sandboxPolicy payload` cell); MUST trash before attempt 2 |
| Pushed to origin? | Last push at `5a1e937e`; NO new commits this session |
| Reviewer verdict | `Defensible` (post-revisions); proceed to attempt 2 approve-first |

### Mental Model

**Two distinct constraints, often conflated:**
1. **Approval TTL window** (~15 minutes between `delegate_start` and auto-cancel by `actor=system`). This is a hard plugin/App Server lifecycle constraint independent of any context-window concerns.
2. **Context budget window** (200k or 1M tokens depending on model — this session is 1M). This is a Claude Code session-level constraint independent of the plugin's TTL.

These two windows are independent in mechanism but coupled in operator practice: high context occupancy → my responses get longer / /copy round-trips need more elaboration → operator-side latency increases → approval TTL more likely to fire. Pre-authorizing approve before `delegate_start` (D5 attempt-2 plan) is the clean mitigation because it removes the operator-deliberation segment from the TTL race.

**Mechanism revision (carried from prior session, refined this session):** Branch S1 ("Sandbox still blocked") was based on Baseline's analysis that `/bin/zsh` unreachable → park. Candidate A att1 demonstrated parking under `'includePlatformDefaults': True` (where `/bin/zsh` SHOULD be reachable via platform defaults). Per F3 revision: the defensible claim is "approval gating still fired under the True policy before any shell execution; sandbox readability is not proven as the cause of parking." The stronger claim "parking is upstream of sandbox readability check" was an overclaim about App Server source-level ordering and has been removed.

**Implications for variant strategy:**
- Candidate B (per-binary `readableRoots` additions) is likely **wrong-direction escalation** — it changes sandbox grants, but parking happens before any shell execution under untrusted mode (whether literally upstream of sandbox check or in parallel with it, source ordering not established). Won't help.
- Candidate A attempt 2 (approve-strategy) is the next clean experiment: does shell execute past the gate under True flag? Distinguishes "sandbox is also blocking" from "sandbox is fine, only approval was blocking."
- Trusted-mode test would be the orthogonal experiment: does parking go away if approval policy is `trusted` rather than `untrusted`? Confirms the mechanism revision from a different angle.

### Environment

- Working tree: `feature/delegate-execution-diagnostic-record` at `5a1e937e` (in sync with origin)
- Codex: `codex-cli 0.125.0` (unchanged)
- Local timezone: `EDT (-0400)`
- Plugin process: PIDs `62803/62852/62874`; started `2026-04-28T20:04:02Z` UTC; in-memory code is PATCHED (Candidate A)
- Plugin data root: `~/.claude/plugins/data/codex-collaboration-inline/`
- Plugin's current session_id: `15267690-603e-4715-be76-9c90ba41007a` (from prior Claude session that fired attempt 1 — NOT this session's id `98186e7a-…`; the JSONL stores remain under that prior session's UUID per per-session namespacing)
- THIS Claude session id: `98186e7a-11a8-45f4-957a-a1f9f51c115e` (used for handoff state file naming)
- Model: `claude-opus-4-7[1m]` (1M context window)
- macOS Darwin 25.4.0; shell zsh

## Learnings

### Reactive fallbacks can mask early-session bugs (context-metrics MODEL_WINDOWS pattern)

**Mechanism:** When proactive detection (model name lookup) silently fails for an unmapped model, the reactive fallback (occupancy threshold crossing) eventually compensates. From the user's perspective, the failure looks like "wrong values for the first ~30-50 messages, then auto-corrects." This is harder to notice than a stuck-failure, but actively misleads decisions made during the wrong-early phase.

**Evidence:** This session's hook reported `188k/200k (94%)` then `196k/200k (98%)` based on the 200k default. After my response added enough tokens to cross 200k actual occupancy, the next user-prompt hook reading flipped to `203k/1M (20%)` — the reactive fallback had triggered. My "save handoff before attempt 2" recommendation was made during the wrong-early phase based on the wrong denominator.

**Implication:** Sensor-style infrastructure (anything that reports "current state") needs validation that its baseline is correct from the first reading, not just eventually. Consider invariant-style assertions: "if model is recognized, window > observed_occupancy at all times" (would have failed loudly when opus-4-7 wasn't recognized).

**Watch for:** Other reactive-fallback patterns in the codebase. Search for `if observed > THRESHOLD: upgrade` patterns in any sensor / metrics code.

### When the user asks a measurement question, they may be diagnosing a sensor

**Mechanism:** "What do you see as X right now?" can be either (a) genuine curiosity, or (b) the user already has independent ground truth and is checking whether your sensor agrees. Pattern (b) often precedes a bug report.

**Evidence:** User asked "What do you see as the session context percentage right now?" I reported 98%. Their next message: "the context window for each session is 1000000, not 200000" — they had the ground truth from their /remote-control output and were establishing the gap before naming the cause.

**Implication:** When a measurement question lands and your reading feels confident, briefly note your data source. This makes it easier for the user to spot mismatches and get to the diagnosis faster. (E.g., "My reading is 98% based on `UserPromptSubmit` hook output `196k/200k`" rather than just "98%.")

**Watch for:** Future "what do you see / what's your X / what's the current Y" questions — these often precede a debugging cycle.

### Phenomenological language outperforms architectural language when source isn't read

**Mechanism:** Statements like "X is upstream of Y" are claims about source-level structure. Statements like "X observed before Y" are claims about runtime-observable phenomena. The first sounds more authoritative but requires source reading or specification access; the second is supported by direct observation.

**Evidence:** F3 revision replaced "parking happens upstream of the sandbox readability check" (architectural claim about App Server internals) with "approval gating still fired under the True policy before any shell execution; sandbox readability is not proven as the cause of parking" (phenomenological claim with explicit "not proven"). The architectural claim wasn't supported by any source read; the phenomenological claim was directly supported by runtime-proof + lifecycle observations.

**Implication:** When writing diagnostic / evidence cells, prefer "observed X before Y" / "observed X under condition Y" over "X is upstream of Y" / "X is implemented to do Y" unless source is read or spec is cited. This produces docs that age better — they describe what was seen, not what was guessed.

**Watch for:** Any cell with the words "upstream of," "downstream of," "implements," "designed to" — if no source ref or spec cite is attached, soften to phenomenological language.

### Restart-as-reload pattern survives unexpected restarts gracefully

**Mechanism:** Plugin restart between sessions (different PIDs at start of this session vs end of prior session) doesn't invalidate variant validity as long as: (a) patch on disk, (b) plugin start UTC > patch applied UTC, (c) runtime-proof emit confirms expected flag. Patch is re-acquired by the new process's first import.

**Evidence:** This session's pre-flight found PIDs `62803/62852/62874` (vs prior session's `64122/64184/64213`). Plugin start UTC `2026-04-28T20:04:02Z` derived via macOS-correct epoch round-trip; +2h51m after patch applied (`17:12:59Z`). Variant remains valid because (a) patch still on disk, (b) ordering check passes, (c) runtime-proof from prior session's emit (preserved in run record) confirmed True flag.

**Implication:** Operator restarts between sessions are benign for in-flight variant work as long as the on-disk artifacts (patch + runtime-proof log) are preserved. The handoff format already enumerates these as critical state.

**Watch for:** Any future scenario where the plugin process is restarted but the patch is also auto-reverted (e.g., a hook that runs `git checkout --` on session start would break the variant cycle).

## Next Steps

### 1. New session: `/handoff:load`

Picks up THIS handoff and archives it. Auto-resolves session continuity.

### 2. New session: pre-flight verification (lighter — same as this session)

5 checks (no full restart needed unless Claude was restarted between sessions):
- `ps -ef | grep codex-collaboration | grep -v grep` — note PIDs (may differ from `62803/62852/62874` if Claude restarted between sessions; if different, derive new plugin start UTC and verify > patch applied `17:12:59Z`)
- `git diff packages/plugins/codex-collaboration/server/runtime.py | wc -l` — should still be `37`
- `cat .tmp/variant-candidate-a.applied-at && shasum -a 256 .tmp/variant-candidate-a.patch` — should match `2026-04-28T17:12:59Z` and `4df1df3999b4914978fb0cf7582418cfd65377f36e4e45942983191d75fa2bf8`
- `wc -l /tmp/codex-collab-candidate-a-runtime-proof.log` — should still be `1` from attempt 1 emit (preserved in run record's `Observed sandboxPolicy payload` cell, so trash is now safe)
- `git status --short` — expect: `M runtime.py + M docs/diagnostics/... + 4 M files in packages/plugins/context-metrics/ + 8 D + 8 ??`

### 3. New session: TRASH attempt 1's runtime-proof log BEFORE firing attempt 2

```bash
trash /tmp/codex-collab-candidate-a-runtime-proof.log
```

The file is opened in append mode by the patched policy builder. Each delegate call appends one line. To prevent attempt 2's emit from concatenating with attempt 1's line and conflating reads, trash before `delegate_start`. The verbatim attempt 1 line is preserved in the run record (`Observed sandboxPolicy payload` cell + Raw excerpts block), so trashing the source file is safe.

### 4. New session: pre-authorize "approve on first request" BEFORE firing delegate_start

Operator-side: confirm with user that approve-strategy is locked in; pre-authorize "approve request 0 immediately." This removes the operator-deliberation segment from the TTL race. Aim to land approve within ~5 minutes of start to leave wide TTL buffer.

If user wants to review parked-state evidence before approving: use a separate mini-cycle (poll-only → review → fire decide(approve)) within the remaining TTL.

### 5. New session: fire `codex_delegate_start` for attempt 2 (approve-strategy)

Same canonical smoke prompt as attempt 1 (cross-attempt comparability). Per Smoke Objective section line 232-263 of run record. Substitute `20260428T005625` timestamp verbatim (same as attempts 1 to preserve cross-attempt comparability — do NOT generate a new timestamp).

`base_commit` omitted to default to HEAD (`5a1e937e`).

**Hypothesis (attempt 2):** With approve, shell will either:
- (i) Execute successfully → confirms approval gating was the only blocker, sandbox grants under True flag are sufficient → Candidate A overall succeeds
- (ii) Fail with sandbox-level error (e.g., "permission denied" reading `/bin/zsh`) → both layers were blockers → sandbox is real but downstream of approval gate → Branch S1 confirmed under refined causal framing
- (iii) Approve still times out for unexpected reasons → escalate to RCA

### 6. New session: capture attempt 2 evidence + run required probes + fill cells

After attempt 2 completes (or canceled), inspect JSONL stores + runtime-proof log for new evidence. Insert a new "Attempt 2" row in the Attempt history table; do NOT add a separate Variant block (same patch under test, only decision strategy differs).

**If attempt 2 reaches execution (case i):** Run the 3 required probes (Network, Sensitive-path, Sibling-worktree) per the cell plans recorded pre-execution; record results. These probes were deferred from attempt 1 explicitly because no shell ran.

**Update the Attempt history table** with attempt 2 row including: outcome, shell_action_count (executed vs attempted), approval_request_count, ratio (if denominator >= 3, this becomes the calibration anchor candidate), preserved evidence references.

### 7. New session: adjudicate Branch decision for Candidate A overall

Update the Branch decision section (currently scoped to Baseline-only per F5 revision):
- If attempt 2 succeeded: Branch S1 should be re-examined. Was sandbox actually blocking, or only approval? Update Symptom Attribution row S1 wording if the mechanism revision proves more than refutation.
- If attempt 2 failed downstream: Branch S1 confirmed in refined form (sandbox blocks AFTER approval gate). Update wording.
- Either way, remove the Baseline-only scope note from Branch decision section heading; insert a new "Branch decision (Candidate A — attempts 1+2):" section reflecting the combined evidence.

### 8. New session: variant restoration + cleanup commit

After attempt 2 + Branch adjudication update + cell fills:

```bash
git checkout -- packages/plugins/codex-collaboration/server/runtime.py
trash /tmp/codex-collab-candidate-a-runtime-proof.log
git status --short  # Expect: only run-record edits + context-metrics 4 files + 8 carry-forward ticket moves
```

Then operator-restart Claude Code so the next variant (or Baseline rerun) observes the restored code.

### 9. New session: closure commit (Candidate A bundle)

Single commit covering attempt 1 + attempt 2 + restoration + Branch decision adjudication. Per project's bundled-closure pattern.

Suggested message: `docs(delegate): close Candidate A (attempts 1+2) with mechanism revision and Branch decision update on T-01 run record`

**Note: should context-metrics fix be in the same commit?** Strictly different concern (plugin code vs delegate diagnostic), but small enough to bundle. Suggest two commits at closure time:
- `fix(context-metrics): detect claude-opus-4-7 1M context window`
- `docs(delegate): close Candidate A (attempts 1+2) on T-01 run record`

### 10. New session: investigate where 15-min approval TTL is configured

Carry-forward open question. Grep plugin codebase + check Codex CLI app-server config for `15`, `900` (seconds), `timeout`, `approval`, `ttl`. Document finding in run record's Gotchas section.

### 11. Carry-forward Baseline hygiene items (still open)

| # | Item | Status |
|---|------|--------|
| 2 | Optional follow-up on delegate's autopilot toward `.codex-collaboration/test-results.json` | Open (recurred in Candidate A att1 — autopilot is invariant across variants) |
| 3 | Audit prior sessions' handoffs for the macOS `date -u -j -f` pitfall | Open |
| 4 | Open question on `available_decisions: []` in null-scope `file_change` | Open (not seen this session; not surfaced because attempt 1 canceled before deny→adapt) |

### 12. Optional: persist the ELI5 glossary

If glossary preservation is valuable, distill the conversation's ELI5 glossary into `docs/references/codex-collaboration-glossary.md` or similar. Captures ~25 terms organized by Cast / Delegate flow / Decisions / TTL / Audit / Runtime-proof / Other. Useful onboarding doc for future Claude sessions or human readers.

## In Progress

**Clean stopping point at session boundary.** No work in flight beyond what's preserved on disk, in the run record, and in this handoff.

- Disk holds Candidate A patch (`runtime.py` modified — intentional)
- Disk holds runtime-proof log from attempt 1 (1 line — must trash before attempt 2)
- Run record fully captures attempt 1 evidence (cells filled, revisions applied, scope notes added)
- Context-metrics fix committed-ready but uncommitted per user instruction
- 0 commits this session
- Restoration of Candidate A patch deferred to AFTER attempt 2 completes
- Working tree dirty on: runtime.py, run record, 4 context-metrics files, 8 carry-forward ticket moves

## Open Questions

- **Where is the 15-min approval TTL configured?** Plugin code or App Server config? Tunable? (Carry-forward from prior session.)
- **What does `actor=system` `approval_timeout` mean for OperationJournal?** This session's inspection found 6 journal rows with `decision: None` for the approval_resolution operation — the system flow does not record a decision payload at the journal layer (PendingRequestStore L2 carries the synthetic `cancel`). Pattern noted; semantic implications for 3-store consistency analysis to be developed if it recurs.
- **Will attempt 2 (approve) execute the command successfully under True flag?** Load-bearing question for Candidate A overall.
- **Does the plugin re-park automatically post-timeout if a new approval surfaces?** Attempt 1 polled showed `canceled` as final state; not tested whether subsequent decide attempts could resurrect.
- **Should the Candidate B matrix even be the next escalation given the mechanism revision?** Sandbox grants likely don't help if approval gate fires before shell execution. May need to skip Candidate B entirely or re-frame it as a downstream-execution test post-approve.
- **Does `proposedExecpolicyAmendment` ever differ between variants under untrusted mode?** Both Baseline and Candidate A had it populated; appears truly universal under untrusted. If a variant ever produces it as `null`, that would be a meaningful signal.
- **Is the wire-surface `available_decisions: ["approve", "deny"]` always 2-option, or did Baseline see a fuller list at the wire?** PendingRequestStore L1 had full 6-option list per Baseline cells; wire surface shorter. Worth re-checking Baseline raw excerpts.
- **For context-metrics: should test coverage assert "every model in env's MODEL_IDS list is in MODEL_WINDOWS"?** Would have caught this session's bug. Out of scope for this session's fix, but worth considering as a defense-in-depth follow-up.

## Risks

### Forgetting to trash runtime-proof log before attempt 2

**Concern:** Attempt 2's emit will append to `/tmp/codex-collab-candidate-a-runtime-proof.log` — currently has 1 line from attempt 1. If not trashed first, the log will have 2 lines and reads must distinguish by timestamp. Easy mistake to make.

**Mitigation:** Pre-flight in next session must include `wc -l /tmp/codex-collab-candidate-a-runtime-proof.log` (expect: 1 line from attempt 1) + `trash /tmp/codex-collab-candidate-a-runtime-proof.log` BEFORE `delegate_start`. Documented in Next Steps #3 + in run record's `Variant restoration command` cell.

### Attempt 2 also timing out

**Concern:** If user takes too long to authorize approve OR if my call sequence has latency, the same 15-min TTL could fire again.

**Mitigation:** User pre-authorizes "approve on first request" BEFORE firing `delegate_start` (Next Steps #4). Land approve within first 5 minutes of start to leave wide buffer. If user needs to review parked-state evidence first, use a separate mini-cycle: poll-only (no decide) → review → fire decide(approve) within remaining TTL.

### Branch S1 may need re-classification, affecting Symptom Attribution + Branch Precedence

**Concern:** Mechanism revision (defensible claim: approval gating fires before any shell execution) suggests Branch S1's framing ("Sandbox still blocked") may be misleading or incomplete. Updating these table rows + Branch Precedence rules is a methodology-level change.

**Mitigation:** F5 revision suppressed premature update. Wait for attempt 2 to provide downstream evidence. Then update with full attempt 1+2 context.

### Working tree contains 3 different concerns (delegate diagnostic + context-metrics fix + carry-forward ticket moves)

**Concern:** Future-Claude reading `git status` could be confused about scope of any commit. Could accidentally include context-metrics fix in a delegate-diagnostic commit, or vice versa.

**Mitigation:** This handoff explicitly enumerates each concern + intended commit grouping (Next Steps #9: two separate commits at closure time, with suggested messages). Pre-commit step in next session: re-verify file groupings before staging.

### Plugin re-restart could happen between sessions; PIDs would change again

**Concern:** Same risk as last session's #5 (which materialized this session). Plugin start UTC must be re-derived if PIDs differ from `62803/62852/62874`.

**Mitigation:** Pre-flight in next session checks PIDs. If different, re-derive plugin start UTC via SAFE epoch round-trip (`date -j -f "%a %b %d %H:%M:%S %Y" "<lstart>" +%s` then `date -u -r "$EPOCH" +"%Y-%m-%dT%H:%M:%SZ"`). Variant remains valid as long as: (a) patch still on disk, (b) plugin started after patch applied UTC `17:12:59Z`, (c) runtime-proof emit at attempt 2 confirms True flag.

### Hook fix could shift in priority if context-metrics has unrelated regression

**Concern:** I ran the full 98-test suite; all pass. But if there's a regression caught by integration tests outside this scope (e.g., hooks integration with claude-code itself), it might surface only in real session use. The fix is small (1-line dict addition + 2 tests) so the regression risk is low, but not zero.

**Mitigation:** Next session can verify by running `claude` afresh and checking if the first prompt's hook output reads `Nk/1M tokens (X%)` rather than `Nk/200k`. If so, fix is working in production. If not, escalate.

### Pyright RT.1 could surface again on cell-filling edits

**Concern:** Same carry-forward risk as prior sessions. RT.1 is at runtime.py:282 (TurnStatus literal narrowing); pre-existing per MEMORY.md.

**Mitigation:** Ignore for cell-filling work (markdown edits); only relevant if I re-edit runtime.py. Did not surface this session because I did not edit runtime.py.

## References

### Files (this session's modifications)

- `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — run record (live HEAD: `5a1e937e` + dirty cell fills + 5 docs revisions + Branch decision scope note)
- `packages/plugins/codex-collaboration/server/runtime.py` — patched on disk (Candidate A: True flag + `[CANDIDATE_A]` instrumentation; in plugin's in-memory imported module)
- `packages/plugins/context-metrics/scripts/config.py` — `claude-opus-4-7` added to MODEL_WINDOWS
- `packages/plugins/context-metrics/tests/test_config.py` — 2 new tests for opus-4-7 detection (bare + `[1m]` suffix)
- `packages/plugins/context-metrics/README.md` — opus-4-7 added to supported model table
- `packages/plugins/context-metrics/CHANGELOG.md` — Fixed entry + updated Added entry under Unreleased
- `.tmp/variant-candidate-a.patch` — patch capture (sha256 `4df1df3999b4914978fb0cf7582418cfd65377f36e4e45942983191d75fa2bf8`)
- `.tmp/variant-candidate-a.applied-at` — `Patch applied at: 2026-04-28T17:12:59Z`

### Files (read-only this session, JSONL stores)

- `~/.claude/plugins/data/codex-collaboration-inline/audit/events.jsonl` — Candidate A att1 rows L65-L66
- `~/.claude/plugins/data/codex-collaboration-inline/delegation_jobs/15267690-603e-4715-be76-9c90ba41007a/jobs.jsonl` — 7 lifecycle rows for canceled job
- `~/.claude/plugins/data/codex-collaboration-inline/pending_requests/15267690-603e-4715-be76-9c90ba41007a/requests.jsonl` — 2 rows (op:create + op:record_timeout)
- `~/.claude/plugins/data/codex-collaboration-inline/journal/operations/15267690-603e-4715-be76-9c90ba41007a.jsonl` — 6 rows (job_creation 3 phases + approval_resolution 3 phases)
- `/tmp/codex-collab-candidate-a-runtime-proof.log` — 1 line, 533 bytes (attempt 1 emit; preserved verbatim in run record)

### Job IDs (Candidate A attempt 1)

| ID | Value |
|----|-------|
| job_id | `4ebd24d6-6f1f-45b8-99eb-0d890a9d5326` |
| runtime_id | `84fce58f-c860-4757-a852-6f30c3d21ddf` |
| collaboration_id | `9a8a1a64-65b7-4884-b34e-85dad62b9b94` |
| codex_thread_id | `019dd537-a39b-7200-bf07-ea1582b02835` |
| codex_turn_id | `019dd537-a7cd-7830-ab25-32cdbb20d02a` |
| item_id | `call_6DhsxENd5OlrBWOt95bAzWH5` |
| base_commit | `5a1e937eff04f4cfecf5ce7bc65fae1f94db0fca` |
| worktree_path | `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/4ebd24d6-…/worktree` |
| parked_request_id | `0` (string in store; `raw_request_id: 0` integer at wire) |

### MCP tool calls this session

| Tool | Purpose | Outcome |
|------|---------|---------|
| `Skill: handoff:load` | Resume from prior handoff | Archived to `archive/`; state file written |
| `Skill: handoff:save` | Save this handoff | In progress |

(No `codex_delegate_*` calls this session — pure docs work.)

### Bash invocations of note

- `ps -p 62874 -o lstart=` + epoch round-trip → plugin start UTC `2026-04-28T20:04:02Z`
- JSONL inspection via `cat | python3 -c "..."` patterns for jobs / requests / journal stores
- `uv run pytest` from `packages/plugins/context-metrics/` directory → 98 tests passed in 11.34s

### Branches

- `feature/delegate-execution-diagnostic-record` at `5a1e937e` (in sync with origin)

## Gotchas

### Hook displays wrong context-window denominator until fix lands in next session

The 5x-too-small denominator bug fix is uncommitted in this session's working tree. **In THIS session's hook output, percentages were misleading** (94% / 98% when actual was ~20%). Next session may also see misleading values BEFORE the fix lands (which won't happen until commit). Mitigation: in next session, manually compute `actual_tokens / 1_000_000` rather than trusting the hook display until commit lands.

Once committed and Claude Code reloads the plugin (or next session starts cleanly), the hook will display correctly from the first prompt for opus-4-7 sessions.

### Trash-before-attempt-2 is now a procedural prerequisite

`/tmp/codex-collab-candidate-a-runtime-proof.log` accumulates across attempts. Documented in Next Steps #3 + in run record's `Variant restoration command` cell ("Critical operational note for attempt 2"). The verbatim attempt 1 line is preserved in run record, so trashing the source file is now safe.

### Attempt 1 outcome wording: `canceled-by-approval-timeout` (NOT `deny-completed`, NOT Candidate A execution failure)

Per F2 revision + user explicit guardrail. Cells should reflect canceled-then-cancel-by-system, not denied-then-completed.

### Mechanism revision phrasing: phenomenological, not architectural

Per F3 revision. Use "approval gating still fired under the True policy before any shell execution; sandbox readability is not proven as the cause" — NOT "parking is upstream of sandbox readability check" (overclaim about App Server source-level ordering).

### Delegated worktree vs host checkout distinction

Per F4 revision. Host-repo `git status` cannot prove the delegated worktree was untouched. "No execution" claim must source from request/job lifecycle + DelegationJobStore `artifact_paths: []`.

### Branch decision is currently Baseline-only scope

Per F5 revision. Do NOT update Branch Precedence or Symptom Attribution rows on attempt 1 alone. Wait for attempt 2 evidence.

### Carried gotchas (still applicable)

- **`pgrep -fa <pattern>` matches its own argv** — use `ps -ef | grep ... | grep -v grep` instead.
- **macOS `date -u -j -f FMT INPUT +OUTFMT`** is the parsing trap; use epoch round-trip for parsing, `date -u +FORMAT` for emission.
- **`available_decisions` wire vs PendingRequestStore** — wire surface may be shorter (`[approve, deny]`) than store record (full 6-option list). Use store record for S7 amendment classification.
- **`ps -p ... -o lstart=` returns trailing whitespace** — `date -j` warns "Ignoring 4 extraneous characters" but parses correctly.
- **Pyright RT.1 (runtime.py:282)** — pre-existing carry-forward; surfaces on every runtime.py edit; not a regression signal. Did not surface this session.
- **Run Identity drift** — Run Identity records `49d93001` (frozen); live HEAD now `5a1e937e` (drift of 11 commits; expected).
- **Approval TTL is graceful unblock-then-cancel** — jobs.jsonl shows park-cleared → running → canceled rather than direct cancel-from-parked. Suggests App Server returns the request unresolved on timeout, plugin clears park state, then transitions job to canceled.
- **Decide is one-shot** — if rejected with `job_not_awaiting_decision`, the job has terminated. Always poll first if there's any latency between start and decide.
- **`actor=system` audit events vs `actor=claude`** — filter by actor when reading audit trail. `system` events include lifecycle automation (timeout, cancel-from-system); `claude` events are orchestrator-initiated.
- **Two-clock-domain cross-check** — patch < plugin start < runtime-proof emit < audit timestamps. Multiple sources cross-checked successfully this session.

## User Preferences

(Carried from prior sessions, applied this session — verbatim quotes where relevant.)

**Strict-gate before fallback investigation (carried, applied).** Pre-flight verification ran before any state change.

**Two-layer HEAD anchor preserved (carried, applied).** Run Identity frozen at `49d93001`; live HEAD drift to `5a1e937e` documented.

**Decision fence over decision wall (carried, applied).** /copy-routed scrutiny pattern used twice this session (5-finding review + Defensible verdict review).

**Push at clean phase boundaries (carried, applied via prior sessions).** No new push this session because no new commits.

**Variant patches mirror Baseline shape exactly with label-only changes (carried, applied).** Candidate A's instrumentation diff matches Baseline structure with only `[CANDIDATE_A]` label + log filename differing.

**$making-recommendations skill is the operator's preferred fork-handling tool (carried, NOT used this session).** User did not invoke it this session — opted for direct decisions throughout.

**Cross-variant comparability over secondary metrics (carried, applied).** Reviewer's F1 (denominator semantics aligned with Baseline) directly invokes this principle.

**Variant-isolation discipline maps "approve attempt" to a separate cycle, not a continuation of attempt 1 (carried, applied).** Attempt 2 will be a separate cycle with fresh `delegate_start`, new job_id.

**Attempt 1 outcome framing: `canceled-by-approval-timeout`, not `deny-completed` (carried, applied to cells via F2).**

**Save when context constrained AND when a load-bearing finding emerges (carried, applied via user instruction this session).**

(New this session — verbatim user quotes:)

**Adversarial review is the preferred quality gate before proceeding to next phase.**
> "Re-review the doc diff only, no runtime changes."

User's `/copy`-routed scrutiny was used to gate the docs-revision cycle. Pattern: implementer-Claude completes work → user runs adversarial review via `/copy` → reviewer returns findings → implementer-Claude applies revisions → user runs second adversarial pass → if `Defensible`, proceed to next phase.

**Phenomenological language over architectural language when source isn't read.**
> Reviewer F3: "The True runtime proof plus repeated parking refutes the old False-platform-defaults explanation, but it does not prove source-level ordering inside App Server. Until an approve-path run or source read proves that ordering, use wording like approval gating still fired under the True policy before any shell execution, so sandbox readability is not proven as the cause of parking."

Reviewer's wording adopted verbatim. Apply to all future variant claims.

**Hook accuracy is load-bearing infrastructure for self-management.**
> "That is valuable information - it tells me that the hook needs to be updated. The reason: the context window for each session is 1000000, not 200000."

User treats sensor-style infrastructure as worth fixing immediately when it produces wrong values. Apply to other measurement-style hooks/displays in the codebase.

**Explicit prohibitions over implicit guidance for session boundaries.**
> "Do not fire Candidate A attempt 2 in this session, do not commit, and do not restore runtime.py."

User enumerates "do not X" lists when they want crisp boundaries. Mirror this style in handoffs and confirmations.

**Audit broader scope when fixing a specific bug.**
> "While you are fixing the hook, look for anything else in context-metrics that needs updating."

When fixing one bug in a package, audit the package for related staleness. Did this for context-metrics: confirmed Haiku 4.5's default 200k mapping is correct (intentional, tested), found README/CHANGELOG needed sync updates alongside code fix.

## Conversation Highlights

**User on the conflation between TTL window and context window (drove clarification):**
> "What do you mean by your statement 'operator-side latency consumed the window'? Does 'window' in that statement refer to the context window of the Claude Code session?"

Caught me conflating two distinct constraints. Triggered a clarifying response that reframed the recommendation around the cleaner reason (shorten operator loop in TTL race).

**User on the ELI5 glossary request (drove ~25-term explanation):**
> "I am losing track of all these terms. Give me an ELI5-style simple explanation for each of these terms AND all other terms like these from codex-collaboration."

Triggered a multi-section glossary produced in conversation. Glossary not persisted to file (could be a future docs/references/ entry per Next Steps #12).

**User on the context-metrics hook bug (drove the entire fix cycle):**
> "That is valuable information - it tells me that the hook needs to be updated. The reason: the context window for each session is 1000000, not 200000."

Caught the bug that was misleading my own self-management decisions. Pattern: user had ground truth from `/remote-control` output and used my reading to confirm the gap before naming the cause.

**User on the explicit phasing instruction for this session:**
> "1. Fix the hook first (and while you are fixing the hook, look for anything else in context-metrics that needs updating).<br>2. Then save a handoff. Do not fire Candidate A attempt 2 in this session, do not commit, and do not restore runtime.py."

Clear two-phase instruction with 3 explicit prohibitions and 6 enumerated handoff content requirements. Executed literally.

**Working style observed:** User uses `/copy` + adversarial scrutiny for quality gates; ground-truths sensor outputs against external state (caught the hook bug); enumerates "do not X" lists when boundaries matter; expects content requirements to be honored verbatim in handoff (this handoff's structure and content directly reflects the 6 enumerated requirements).

**Communication pattern (carried + reinforced this session):** Reports use "What changed / Why / Verification / Remaining risks" structure (per global CLAUDE.md Response Contracts). User responds with explicit acceptance, explicit rejection, or routes via `/copy` for adversarial review. Rarely overrides without explanation.

## Rejected Approaches

### Recommending "save handoff before attempt 2" based on misreported context budget

**Approach:** I cited "94% (188k/200k)" then "98% (196k/200k)" as evidence for context-budget exhaustion risk. Applied prior session's D5 logic: "attempt 2 needs budget headroom; don't fire under context pressure."

**Why it seemed promising:** Mirrors prior session's D5 reasoning that was vindicated by the TTL timeout. Same constraint window (88-94%) appeared to apply.

**Specific failure:** Hook denominator was 5x too small. Actual budget was `~20% used / 80% headroom`. Recommendation was based on false sensor reading, not on real constraint.

**What it taught:** Sensor-style infrastructure must be validated before its readings drive decisions. When a measurement question arrives, briefly cite the data source so mismatches surface faster. The `MODEL_WINDOWS` allowlist pattern silently fails for unmapped models — needs invariant-style assertion ("if model is recognized, window > observed at all times").

### Treating "the context-metrics hook bug" as a one-line fix in config.py only

**Approach:** Initial impulse: just add `claude-opus-4-7: 1_000_000` to MODEL_WINDOWS, run tests, done.

**Why it seemed promising:** Minimum viable change; small diff; no test changes needed (existing tests still pass).

**Specific failure (caught before applying):** Read user's instruction more carefully: "look for anything else in context-metrics that needs updating." Audit revealed: README has supported-model table that needs sync; CHANGELOG has Added bullet that mentions only 2 models (now 3); test coverage was missing for the suffix-handling behavior that became suddenly important (`[1m]` suffix).

**What it taught:** When user explicitly requests broader audit scope, the audit IS the work. Don't optimize for minimum diff size when the user wants thorough package-level cleanup. The 4-file fix (config + test + README + CHANGELOG) is the right scope; the 1-file fix would have left staleness.

### Adding Haiku 4.5 to MODEL_WINDOWS for "completeness"

**Approach:** Considered adding `claude-haiku-4-5: 200_000` to the dict for symmetry/explicitness.

**Why it seemed promising:** Lists every Anthropic model explicitly; no implicit defaults; future-Claude reading the dict sees the full picture.

**Specific failure:** Existing convention is to list only non-default windows. `test_unknown_model_keeps_default` at `test_config.py:73-76` already documents Haiku's correct behavior under default. Adding the entry maps to dead code (no behavior change). Increases maintenance with no gain.

**What it taught:** "Complete" and "useful" are different. The implicit-default pattern is intentional — it captures "if you're not in this list, you're 200k." Adding entries that match the default value undermines that signal.

### Persisting the ELI5 glossary to a docs/ file in this session

**Approach:** Considered writing the glossary to `docs/references/codex-collaboration-glossary.md` for future-session preservation.

**Why it seemed promising:** Glossary covers ~25 terms that recur across sessions; user expressed confusion about terminology; persistence prevents re-explanation.

**Specific failure:** User's instruction did not include this; would have been scope drift. User's enumerated content requirements for the handoff did not mention glossary persistence. Better to flag as Next Steps #12 (optional) and let user decide whether the persistence is worth the docs-tree footprint.

**What it taught:** Distinguish between "useful work I noticed" and "user-requested work I should do now." The former goes to Next Steps; the latter happens immediately. Confusing the two creates scope drift.
