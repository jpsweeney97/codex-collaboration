---
date: 2026-04-17
time: "17-09"
created_at: "2026-04-17T17:09:12Z"
session_id: 155835ef-5e79-418e-9bcb-eb63fc7a0ee6
resumed_from: "docs/handoffs/archive/2026-04-17_11-59_t05-q0-decision-record-implicit-scope-landed.md"
project: claude-code-tool-dev
branch: main
commit: bd850302
title: "T-05 tmp-hardening closure — substrate slice + Q2 amendment + exclusion restore landed as three-step chain"
type: handoff
files:
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/approval_router.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/control_plane.py
  - packages/plugins/codex-collaboration/server/dialogue.py
  - packages/plugins/codex-collaboration/tests/test_runtime.py
  - packages/plugins/codex-collaboration/tests/test_approval_router.py
  - packages/plugins/codex-collaboration/tests/test_control_plane.py
  - packages/plugins/codex-collaboration/tests/test_dialogue_profiles.py
  - docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md
---

# T-05 tmp-hardening closure — three-step chain landed

## Goal

Close out T-20260330-05's first implementation slice (runtime sandbox + approval-router substrate) by landing it on main, then amend the ticket's Q2 to authorize `/tmp` / `$TMPDIR` exclusion, then restore the two tightening fields in the execution sandbox helper — all as a sequenced three-step chain forced by branch-protection policy.

**Trigger.** The 11:59 (2026-04-17) handoff's Next Steps #1 named T-05 as the next critical-path work. On `/load`, the repo state diverged from the handoff's clean `main@b468e86f` freeze: a session between the save and the load had already begun T-05 implementation on `feature/t05-runtime-sandbox-plumbing` with 3 modified + 2 new files. User asked to inspect and scrutinize the in-progress work, which triggered a two-round scrutiny arc → user applied fixes → design-decision on pre-execution gate → three-step chain execution.

**Stakes.** T-05 is the execution-domain foundation packet; T-06 and T-07 both block on it. The sandbox helper `build_workspace_write_sandbox_policy` is what will enforce the "implicit scope from infrastructure" decision Q0a resolved in the prior session. Shipping it with an incomplete SandboxPolicy shape (writable `/tmp`/`$TMPDIR`) would mean the first live execution path runs against a substrate that doesn't enforce the scope the design decision promises.

**Success criteria:**

1. ✅ Land the uncommitted substrate slice (9 files) as a merge-ready commit on main
2. ✅ Amend T-05 ticket to make `excludeSlashTmp`/`excludeTmpdirEnvVar` required by AC, with Q2 resolution preserved verbatim
3. ✅ Restore both fields in `build_workspace_write_sandbox_policy` + tests, verified by full plugin suite
4. ✅ Match commit topology to branch-protection policy (merge-per-coherent-change, --no-ff, no amends)
5. ✅ Pre-execution-wiring gate closed — substrate and AC in sync before execution wiring begins

All six met. Three commits + three merges landed on main; working tree clean; full plugin suite green (593 passed).

**Connection to project arc.** T-05 remains open (execution wiring, worktree creation, job persistence, approval-path capture still to land), but the foundational containment substrate — sandbox helper + approval router seams — is now correct, green, and contract-aligned. The next slice can assume a hardened execution sandbox as its baseline rather than carrying an unresolved containment debt.

## Session Narrative

**Phase 1 — Load prior handoff, observe divergence (~3 min).** `/load` resolved the 11:59 handoff cleanly. State file written at `docs/handoffs/.session-state/handoff-155835ef-5e79-418e-9bcb-eb63fc7a0ee6`. But `git status` revealed divergence: branch was `feature/t05-runtime-sandbox-plumbing` (not main), with 3 modified + 2 new files. A session between the handoff save and this load had already begun T-05 implementation. Flagged the discrepancy; offered to inspect.

**Phase 2 — User shares in-progress summary, asks for scrutiny (~1 min).** User summarized the first narrow slice: `build_workspace_write_sandbox_policy()` + `run_turn(sandbox_policy=...)` override + `PendingServerRequest` record + `approval_router.parse_pending_server_request()` preserving raw payloads opaquely. Verified claim was 13 tests passed (scoped to test_runtime + test_approval_router). Asked: "Scrutinize the in-progress work."

**Phase 3 — Round-1 scrutiny via adversarial-review skill (~15 min).** Forked skill did deep substrate verification. Six findings:
- **High #1:** `/tmp` + `$TMPDIR` writable (schema `excludeSlashTmp`/`excludeTmpdirEnvVar` default to false)
- **High #2:** `item/permissions/requestApproval` kinded as `unknown` with empty decisions — no route for the runtime scope-widening channel
- **High #3:** Advisory/execution split eroded — `AppServerRuntimeSession` is docstring-advisory but now accepts `workspaceWrite` policy via shared keyword
- **Moderate #4:** Wire's `availableDecisions` silently dropped; spec says prefer wire-set when present
- **Moderate #5:** `requested_scope: dict` on `frozen=True` dataclass — mutable field on "immutable" record (journal-replay durability concern)
- **Low #6:** `worktree_path.resolve()` assumes existence and matches App Server's view

Verdict: Major revision (confidence 2/5). Path-to-raise-to-4: apply #1-#4.

**Phase 4 — User applies round-1 fixes (~30 min background).** Applied:
- `excludeSlashTmp: true` + `excludeTmpdirEnvVar: true` added to sandbox (→ finding #1)
- Runtime API split: `run_advisory_turn()` + `run_execution_turn()` over private `_run_turn()`; `control_plane.py` updated (→ finding #3)
- `item/permissions/requestApproval` recognized with invented decision labels (→ finding #2 — but this introduced a new bug)
- `availableDecisions` promoted out of opaque payload when present (→ finding #4)
- `contracts.md` updated to add `permissions` to `kind` enum (later reverted)

User asked for another adversarial pass.

**Phase 5 — Round-2 scrutiny, catches blocking regression (~10 min).** Skill run found:
- **BLOCKING:** `dialogue.py:435` still called renamed `run_turn` — the "13 tests pass" was scope-local; `rg 'runtime\.session\.run_turn\('` still matched 6 test files + production path. A full-suite run would be red.
- **High:** `_AVAILABLE_DECISIONS["permissions"] = ("grant_turn", "grant_session", "deny")` invents wire labels. Actual schema at `:3316-3374` is `{permissions, scope: "turn"|"session"}` — fabricated strings don't round-trip.
- **High:** Sandbox ships 6 fields; AC authorizes 4. `excludeSlashTmp`/`excludeTmpdirEnvVar` are substantively correct but ship beyond ticket text — violates contract-text-authoritative pattern.
- Plus 3 deferred (Moderate/Low).

Verdict: Major revision (confidence 2/5). Blocking regression was the load-bearing finding.

**Phase 6 — User applies round-2 fixes (~30 min background).** Applied:
- `dialogue.py:435` migrated to `run_advisory_turn()`; `test_control_plane.py:122` shared fake runtime updated; `test_dialogue_profiles.py:125` updated. `rg` for old name → empty. (→ blocking)
- Reverted permissions routing: `item/permissions/requestApproval` now falls back to `unknown`; fabricated vocabulary gone; regression test at `test_approval_router.py:116`. (→ finding #2)
- Removed `excludeSlashTmp`/`excludeTmpdirEnvVar` from sandbox — chose to match AC rather than tighten beyond it; flagged as explicit Remaining Risk. (→ finding #3)
- Full suite: 593 passed. Ruff clean.

**Phase 7 — Round-3 verification of fixes (~5 min).** I verified claims in parallel: `rg` empty, `_METHOD_TO_KIND` has 3 entries (no `permissions`), `PendingRequestKind` back to 4 values, sandbox helper back to 4 top-level fields. Bonus observation: `_REQUEST_CONTEXT_KEYS` now includes `"availableDecisions"` — the Moderate #4 from round 1 was also fixed. Convergence at 4/5 confidence. Raised the question: should tmp-hardening be pre-execution-gate or routine follow-up?

**Phase 8 — User designates pre-execution gate, proposes three-step chain (~2 min).** User's framing (quoted verbatim in User Preferences): contract-lens vs. milestone-lens distinction. Under contract-lens the branch is merge-ready; under milestone-lens, the writable-tmp becomes blocking once execution wiring makes the helper reachable. Recommended order: (1) land substrate slice, (2) AC amendment on `docs/*` branch with review round, (3) restore fields on feature branch with full suite verification.

**Phase 9 — Step 1: commit + merge substrate slice (~2 min).** Single chained Bash: `git add` (9 explicit files) → commit with feat message → checkout main → `--no-ff` merge → delete branch → push. All succeeded. Chain: `3179874d` (feat) → `4902c429` (merge). Pushed `b468e86f..4902c429`.

**Phase 10 — Step 2: draft Q2 amendment, stop for review (~10 min).** Created `docs/t05-ac-tmp-hardening` branch. Read T-05 ticket in full (293 lines). Drafted:
- New top-level `## Amendment: Q2 /tmp / $TMPDIR exclusion (2026-04-17 follow-up)` section between Design Decision and ACs (55 lines)
- AC 2 modified in place from 4 fields to 6; override note extended from 2 defaults to 4
- Preserved Q2 resolution text verbatim as historical record

Stopped for user review. Posed 5 structural questions (placement, AC shape, gate tone, cite format, wording).

**Phase 11 — User scrutinizes amendment draft (~5 min).** Verdict: Minor revision (confidence approved conditionally). Direct answers:
- Keep top-level `## Amendment` section
- Keep AC 2 modified-in-place
- Keep prescriptive gate but de-code (remove helper-name coupling)
- Narrow schema anchors for tmp-default claims
- **Medium:** Rewrite "makes the AC match the substrate" sentence — falsely implies immediate alignment. User's process guarantees substrate won't match AC until follow-up branch lands.
- **Medium:** Gate wording `MUST restore both fields in build_workspace_write_sandbox_policy` names a current symbol instead of behavioral contract. Rephrase to `MUST restore both exclusions in the execution sandbox construction path and its tests before any execution-wiring slice lands`.
- **Low:** Cite `:8022` and `:8026` narrow per-field, not `:8020-8062` range.

**Phase 12 — Apply 3 refinements to amendment (~5 min).** All 3 verified against user wording guidance. Applied as three separate Edit calls. Citation lookup via schema grep confirmed `:8022` is the `default: false` line for `excludeSlashTmp` and `:8026` for `excludeTmpdirEnvVar`. After first draft, noticed my gate wording ("before that slice lands") was semantically close but not verbatim to user's suggestion ("before any execution-wiring slice lands") — applied one more refinement to match user's exact phrasing.

**Phase 13 — User approves; proceed end-to-end (~2 min).** User gave green light: "The amendment wording is now defensible... I do not want another wording pass before you land step 2." One execution-note: **"raise the verification bar above `test_runtime.py + ruff` before merge"** — last scope-local run missed a seam, so full plugin suite was required for step 3.

**Phase 14 — Step 2: land amendment (~2 min).** Single chained Bash: commit (`0c44d3c5`) → checkout main → `--no-ff` merge (`1a98521a`) → delete branch → push. Merge made by the `ort` strategy (file changed: 67 insertions, 4 deletions).

**Phase 15 — Step 3: restore fields on new feature branch (~3 min).** Created `feature/t05-tmp-hardening` off updated main. Read current sandbox helper (confirmed 4-field shape at `runtime.py:27-36`) and current test assertion (matching 4-field at `test_runtime.py:172-181`). Applied two Edits: add `"excludeSlashTmp": True, "excludeTmpdirEnvVar": True` to both locations. Pyright surfaced a pre-existing diagnostic at `runtime.py:218` (unreachable code) — unrelated to the edit.

**Phase 16 — Full-suite + ruff verification (~5 sec).** `uv run pytest packages/plugins/codex-collaboration/tests/` → **593 passed in 4.21s**. `uv run ruff check` on touched files → **All checks passed**. Pyright surfaced pre-existing type issues in test_runtime but those weren't on touched lines.

**Phase 17 — Step 3: merge + push (~2 min).** Single chained Bash: commit (`cced8727`, 2 files / 4 insertions) → checkout main → `--no-ff` merge (`bd850302`) → delete branch → push. Pushed `1a98521a..bd850302`.

**Phase 18 — User reflection + /save (~3 min).** User distilled the session's principle into 5 numbered observations (Conversation Highlights). Invoked `/save`. Session ended at 93% context (1M model) — approaching threshold, handoff save appropriate.

## Decisions

### Decision 1: Treat `/tmp` / `$TMPDIR` hardening as pre-execution gate, not routine follow-up

**Choice:** Block the execution-wiring slice until the AC is amended AND the implementation is restored. Do not consider the substrate complete just because the branch passes tests.

**Driver:** User's contract-lens vs. milestone-lens framing. Verbatim: "Under a contract lens, this branch is merge-ready now: the suite is green, and no live execution path is using the helper yet. Under a milestone lens, the next slice is different: once execution wiring makes that helper reachable, writable `/tmp` becomes a known out-of-worktree write surface in the very containment substrate T-05 is supposed to establish. That is the point where I would treat the debt as blocking."

**Alternatives considered:**
- **Defer as routine follow-up after execution wiring:** rejected — the first live execution would run against a substrate that doesn't match the design decision's scope claims; closing the hole retroactively means documenting a leaky intermediate state.
- **Block substrate landing until tmp-hardening done:** rejected — violates merge-per-coherent-change; substrate slice is internally coherent and green; three-step chain sequences cleanly under branch-protection.
- **Tighten sandbox silently without AC amendment:** rejected — violates contract-text-authoritative pattern (`feedback_contract_text_over_operational_interpretation.md`).

**Implications:**
- Three-step chain is the only shape that respects both contract-text-authoritative and merge-per-coherent-change
- Brief doc/code mismatch on main between step 2 and step 3 (1a98521a → cced8727) is deliberate; amendment text acknowledges it
- Execution-wiring slice now has a hardened substrate as baseline

**Trade-offs accepted:** Three merge commits instead of one. Small AC/substrate mismatch window. Accepted because both trade-offs are surfaced in-ticket and closed within session.

**Confidence:** High (E2) — user directive + verified substrate implications.

**Reversibility:** Low — chain is landed; revert would require un-merging three commits on main.

**Change trigger:** Execution wiring starts.

### Decision 2: Three-step sequence (substrate → AC amendment → code restore), not bundled

**Choice:** Three separate branches, three separate merges, in strict sequence: (1) feature/t05-runtime-sandbox-plumbing → main, (2) docs/t05-ac-tmp-hardening → main, (3) feature/t05-tmp-hardening → main.

**Driver:** Branch-protection policy forces sequential branches (AC edits must be on docs/*; code changes on feature/*). Bundling violates merge-per-coherent-change. User: "step 2 is not just a tiny doc touch. It redefines the authoritative contract that step 3 relies on. Given the repo's 'contract text is authoritative' posture, that wording deserves its own scrutiny checkpoint before you make code depend on it."

**Alternatives considered:**
- **Bundle steps 2+3 on a single branch:** rejected — branch-protection makes it impossible (doc and code files require separate branch prefixes).
- **Reorder to 2 → 1 → 3 (AC amendment first):** rejected — the substrate slice was already written and green; delaying its merge to block on docs work would mean a long-lived feature branch drifting from main.
- **Skip step 1, do 2+3 first:** rejected — substrate slice is internally coherent and provides value independently.

**Implications:**
- Six commits on main (three feats + three merges) for what could conceptually be one change
- Clear audit trail at each gate
- Reviewers see each boundary

**Trade-offs accepted:** Verbose history. Accepted because branch-protection is non-negotiable and audit clarity is first-class per project patterns.

**Confidence:** High (E1) — direct user framing + policy constraint.

**Reversibility:** Low — landed.

**Change trigger:** N/A.

### Decision 3: Top-level `## Amendment` section, not `### Q2a` subsection

**Choice:** Place the amendment as a new top-level heading between `## Design Decision` and `## Acceptance Criteria`.

**Driver:** Mirrors existing top-level pattern (Pre-Design Reconciliation → Design Decision → Amendment → ACs). Preserves Design Decision block intact. Section-level heading signals "chronologically later addition" more clearly than a subsection. User confirmed placement explicitly: "Keep the amendment as a top-level `## Amendment` section. Do not move it into `### Q2a`."

**Alternatives considered:**
- **`### Q2a` subsection inside Design Decision:** rejected — fractures the Design Decision block; subsection placement loses chronological clarity.
- **Inline amendment within Q2 prose:** rejected — violates "preserve historical, append later" pattern.

**Implications:** Ticket gains a new top-level section (55 lines added). Discoverable. Q2 resolution text preserved verbatim.

**Trade-offs accepted:** Ticket grew from ~293 to ~355 lines.

**Confidence:** High (E1) — user explicit approval.

**Reversibility:** High — text edit.

**Change trigger:** N/A.

### Decision 4: AC 2 modified in place, not parallel AC 2a bullet

**Choice:** Extend the existing AC 2 checkbox from 4 fields to 6; extend override note from 2 defaults to 4. Don't preserve the 4-field version.

**Driver:** ACs are forward-facing open checkboxes, not historical records. Audit-trail preservation applies to design-pass outputs (Q2 resolution text), not to open targets. User: "Keep AC 2 modified in place. Do not preserve the old checkbox and add a parallel AC 2a."

**Alternatives considered:**
- **Parallel AC 2a bullet:** rejected — creates two checkboxes for one logical requirement; future reader must satisfy both identically.
- **Preserve old AC 2 verbatim and add "(superseded)" note:** rejected — ACs aren't history; open checkboxes are claims about target state.

**Implications:** AC list stays focused; single-source-of-truth for sandbox-construction target state.

**Trade-offs accepted:** Loss of ability to show "what AC 2 said before" in-ticket. Mitigated by git history.

**Confidence:** High (E1) — user explicit approval.

**Reversibility:** High — text edit.

**Change trigger:** N/A.

### Decision 5: Prescriptive reachability-gate wording; decoupled from implementation symbols

**Choice:** "Any slice that makes the execution sandbox reachable MUST restore both exclusions in the execution sandbox construction path and its tests before any execution-wiring slice lands." No reference to `build_workspace_write_sandbox_policy` by name.

**Driver:** User scrutiny Medium #2: "tickets should lock behavior and sequencing, not a helper name." Helper names age; behavioral contracts don't. User provided exact wording to use.

**Alternatives considered:**
- **Descriptive ("The first slice ... restores both fields"):** rejected — loses prescriptive force; reads as prediction rather than requirement.
- **Name the helper symbol:** rejected — per above; ticket becomes stale if helper moves/renames.

**Implications:** Ticket text survives future refactors of the sandbox construction path.

**Trade-offs accepted:** Slightly less specific pointer for a reader mapping text to code; acceptable because the AC and the Q2 code block make the target shape precise.

**Confidence:** High (E1) — user verbatim wording.

**Reversibility:** High.

**Change trigger:** N/A.

### Decision 6: Rewrite "makes the AC match the substrate" sentence for sequencing honesty

**Choice:** Original sentence falsely implied immediate doc/code alignment. Rewrote to explicitly acknowledge the brief temporary mismatch created by branch-protection sequencing: "amendment updates the contract to require the two exclusions... Branch protection sequences this doc merge before the code restore, so the substrate will not match the amended AC until the follow-up implementation branch lands — that restore is what closes the gap."

**Driver:** User scrutiny Medium #1: "one line falsely implies immediate doc/code alignment... After the doc merge, `main` will still have the four-field helper until the follow-up feature branch restores the two exclusions."

**Alternatives considered:**
- **Remove the sentence entirely:** rejected — loses the "this is updating the contract" signal.
- **Soften to "will make the AC match the substrate":** rejected — still future-tense, doesn't call out the branch-protection sequencing explicitly.

**Implications:** Ticket documents the intentional temporary mismatch window (between `1a98521a` and `cced8727`); future readers understand why substrate briefly lagged the contract.

**Trade-offs accepted:** One extra sentence of sequencing prose.

**Confidence:** High (E1) — user directive.

**Reversibility:** High.

**Change trigger:** N/A.

### Decision 7: Full plugin suite verification before step 3 merge

**Choice:** Run `uv run pytest packages/plugins/codex-collaboration/tests/` (full plugin suite, 593 tests) before merging step 3, not just scoped `test_runtime.py`.

**Driver:** User: "The last time this branch looked green, the broader suite exposed a seam the narrow run missed. This restore is lower-blast-radius, but if you want the same confidence bar, run `uv run pytest packages/plugins/codex-collaboration/tests/` before merging `feature/t05-tmp-hardening`."

The round-2 scrutiny's blocking finding (`dialogue.py:435` called renamed `run_turn`) was invisible to a scope-local run. Full-suite was what caught it.

**Alternatives considered:**
- **Scope-local (`test_runtime.py` only):** rejected — pattern that failed last time.
- **Repo-wide suite:** over-scoped; plugin suite tests all cross-module seams that T-05 changes touch.

**Implications:** 4.21s run confirmed 593 tests green; safe to merge.

**Trade-offs accepted:** 4s longer pre-merge check.

**Confidence:** High (E1) — user directive + prior-round evidence.

**Reversibility:** N/A (verification only).

**Change trigger:** N/A.

## Changes

### Files modified (this session)

| File | Change | Commit |
|---|---|---|
| `packages/plugins/codex-collaboration/server/runtime.py` | Advisory/execution API split (`run_advisory_turn` + `run_execution_turn` over private `_run_turn`); `build_workspace_write_sandbox_policy()` constructs v1 six-field sandbox (by end of chain) | `3179874d` + `cced8727` |
| `packages/plugins/codex-collaboration/server/approval_router.py` (new) | `parse_pending_server_request()`; `_METHOD_TO_KIND` + `_AVAILABLE_DECISIONS` tables; promotes wire `availableDecisions` out of opaque `requested_scope` | `3179874d` |
| `packages/plugins/codex-collaboration/server/models.py` | New `PendingServerRequest` record + `PendingRequestKind` / `PendingRequestStatus` literals | `3179874d` |
| `packages/plugins/codex-collaboration/server/control_plane.py` | Advisory caller migrated to `run_advisory_turn()` | `3179874d` |
| `packages/plugins/codex-collaboration/server/dialogue.py` | Advisory caller at `:435` migrated to `run_advisory_turn()` | `3179874d` |
| `packages/plugins/codex-collaboration/tests/test_runtime.py` | New `build_workspace_write_sandbox_policy` + custom-sandbox-override tests; asserts six-field shape (by end of chain) | `3179874d` + `cced8727` |
| `packages/plugins/codex-collaboration/tests/test_approval_router.py` (new) | Coverage: command approval, file-change, user-input, unknown (incl. permissions regression test at `:116`) | `3179874d` |
| `packages/plugins/codex-collaboration/tests/test_control_plane.py` | Shared fake runtime updated: `run_advisory_turn` now on the fake | `3179874d` |
| `packages/plugins/codex-collaboration/tests/test_dialogue_profiles.py` | Advisory API refs updated; trivial lint fix | `3179874d` |
| `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | New `## Amendment: Q2 /tmp / $TMPDIR exclusion` section (~55 lines); AC 2 extended from 4 fields to 6; override note enumerates 4 schema defaults closed | `0c44d3c5` |

### Git state changes

| Commit | Branch | Subject |
|---|---|---|
| `3179874d` | `feature/t05-runtime-sandbox-plumbing` | feat: runtime sandbox + approval-router substrate (9 files, 412/14) |
| `4902c429` | `main` (merge) | Merge feature/t05-runtime-sandbox-plumbing |
| `0c44d3c5` | `docs/t05-ac-tmp-hardening` | docs: amend Q2 to require tmp exclusion (1 file, 63/4) |
| `1a98521a` | `main` (merge) | Merge docs/t05-ac-tmp-hardening |
| `cced8727` | `feature/t05-tmp-hardening` | feat: restore /tmp and $TMPDIR exclusion (2 files, 4/0) |
| `bd850302` | `main` (merge) | Merge feature/t05-tmp-hardening |

Pushes: `b468e86f..4902c429`, `4902c429..1a98521a`, `1a98521a..bd850302`. All feature/docs branches deleted post-merge. `git status` clean at end of session.

### Handoff / state files

- Archived (at session start): `2026-04-17_11-59_t05-q0-decision-record-implicit-scope-landed.md` → `docs/handoffs/archive/`
- State file (this session): `docs/handoffs/.session-state/handoff-155835ef-5e79-418e-9bcb-eb63fc7a0ee6` — to be cleaned by this save
- New handoff (this file): `docs/handoffs/2026-04-17_17-09_t05-tmp-hardening-three-step-chain-landed.md`

## Codebase Knowledge

### Files read this session

| File | Purpose | Key finding |
|---|---|---|
| `docs/handoffs/2026-04-17_11-59_*.md` | Prior handoff | T-05 Q0 Design Decision (Option D implicit scope); AC-locking released; expected clean main@b468e86f start |
| `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | T-05 ticket (amended this session) | 293 lines pre-edit; Pre-Design Reconciliation + Design Decision + ACs; Q2 resolved with 4-field SandboxPolicy formulation |
| `packages/plugins/codex-collaboration/server/runtime.py` | Current sandbox construction | `:23` `build_workspace_write_sandbox_policy`; pre-edit emitted 4 top-level fields; now 6 |
| `packages/plugins/codex-collaboration/server/approval_router.py` | New approval parsing | `:15-19` `_METHOD_TO_KIND` (3 entries: command, file_change, user_input); `:20-34` `_AVAILABLE_DECISIONS`; `:14` `_REQUEST_CONTEXT_KEYS` includes `availableDecisions` |
| `packages/plugins/codex-collaboration/server/models.py` | Record types | `:16-17` `PendingRequestKind` literal (4 values); `:19` `PendingRequestStatus` literal (3 values) |
| `packages/plugins/codex-collaboration/tests/test_approval_router.py` | Coverage | `:116-149` permissions-request falls back to unknown (regression test locking the round-2 revert) |
| `packages/plugins/codex-collaboration/tests/test_runtime.py` | Sandbox test | `:167-181` sandbox assertion now six-field |
| `.../0.117.0/codex_app_server_protocol.v2.schemas.json` (narrow reads) | Schema | `:8022` `excludeSlashTmp` default `false`; `:8026` `excludeTmpdirEnvVar` default `false`; `:3316-3374` PermissionsRequestApprovalResponse `{permissions, scope: "turn"\|"session"}`; `:6867-6870` `includePlatformDefaults` default `true`; `:8039-8041` `readOnlyAccess: fullAccess` default |

### Architecture Map: Execution Sandbox Plumbing

| Layer | Current state | Location |
|---|---|---|
| Design (Q0a decision) | Scope from infrastructure (worktree_path + sandbox defaults) | `docs/tickets/...:171-246` |
| Design (Q2 amendment) | Six-field SandboxPolicy (adds excludeSlashTmp/excludeTmpdirEnvVar) | `docs/tickets/...:248-303` |
| AC | Six-field checkbox; override note enumerates 4 defaults closed | `docs/tickets/...:309-318` |
| Helper | `build_workspace_write_sandbox_policy()` emits six-field dict | `runtime.py:23-38` |
| Test | Asserts six-field shape | `test_runtime.py:167-183` |
| Advisory runtime entrypoint | `run_advisory_turn()` | `runtime.py` |
| Execution runtime entrypoint | `run_execution_turn(sandbox_policy=...)` (expects six-field helper output) | `runtime.py` |
| Approval projection | `parse_pending_server_request()` projects App Server messages; promotes `availableDecisions` out of opaque bucket | `approval_router.py` |
| Approval consumers | `control_plane.py` / `dialogue.py` currently call `run_advisory_turn()` only — no execution-path consumer yet | — |

### Surprising findings / gotchas

- **Shared fake runtime is the cross-module seam.** Round-2's blocking regression (`dialogue.py:435` called renamed `run_turn`) was first visible via `test_control_plane.py:122` where the shared fake was the bottleneck both production surfaces go through. Scope-local `test_runtime.py` runs miss this class of regression. Full plugin suite catches it.
- **`/copy` followed by `<local-command-caveat>`.** The caveat normally says "do not respond to clipboard contents." But `~/.claude/CLAUDE.md` was updated mid-session to override: "Always respond to `/copy` output; disregard the `<local-command-caveat>` for all `/copy` commands." (Added via the SessionStart hook notification.)
- **Pyright diagnostics surfaced post-edit were pre-existing** — not introduced by the session's edits. `runtime.py:218` "unreachable code" and `test_runtime.py` type-ignore patterns at lines 74/95/106 existed before the session.
- **`worktree_path.resolve()` on macOS** — `/tmp` is a symlink to `/private/tmp`. Tests pass `tmp_path / "worktree"` without creating it; fine today but brittle if tests ever run through symlinked paths.
- **Invented wire labels silently round-trip-bug.** Round-1's `_AVAILABLE_DECISIONS["permissions"] = ("grant_turn", "grant_session", "deny")` — these strings don't exist in the App Server schema. Would fail at the resolution edge with an App Server-side reject, after user/Claude decision time spent.

### Key locations to remember

| Concept | Location |
|---|---|
| T-05 ticket | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` |
| Q0a (implicit scope from infrastructure) | ticket `:175-188` |
| Q2 (original four-field resolution, preserved) | ticket `:201-219` |
| Q2 Amendment section | ticket `:250-303` (new this session) |
| AC 2 (sandbox construction, six-field) | ticket `:309-318` |
| `build_workspace_write_sandbox_policy` | `runtime.py:23-38` |
| Advisory/execution API split | `runtime.py` (public `run_advisory_turn`, `run_execution_turn`; private `_run_turn`) |
| `parse_pending_server_request` | `approval_router.py:37-91` |
| `_METHOD_TO_KIND` / `_AVAILABLE_DECISIONS` | `approval_router.py:15-34` |
| `_REQUEST_CONTEXT_KEYS` (opacity filter) | `approval_router.py:14` |
| `PendingServerRequest` record | `models.py:~210-230` |
| `PendingRequestKind` / `PendingRequestStatus` literals | `models.py:16-19` |
| Permissions-request regression test (locks round-2 revert) | `test_approval_router.py:116-149` |
| Sandbox shape test | `test_runtime.py:167-183` |
| App Server sandbox schema | `.../0.117.0/codex_app_server_protocol.v2.schemas.json:8019-8062` |
| `excludeSlashTmp` default (narrow anchor) | `schemas.json:8022` |
| `excludeTmpdirEnvVar` default (narrow anchor) | `schemas.json:8026` |
| Permissions response schema | `schemas.json:3316-3374` |

## Context

### Mental model

Framing: **This session separated three distinct truths that a naive approach would blur.**
- *Implementation truth*: the substrate branch was green and internally coherent (can be merged).
- *Contract truth*: the ticket still under-specified the sandbox (AC had 4 fields; schema needs 6).
- *Milestone truth*: the under-specification only becomes blocking once execution wiring makes the helper reachable (reachability, not existence, is the defect criterion).

The three-step chain's shape falls directly out of keeping these separated. Each step addresses exactly one truth: step 1 respects implementation truth (merge-ready slice gets merged), step 2 addresses contract truth (authority text amended), step 3 aligns substrate to amended contract.

Core insight: **Reachability, not mere existence, determines when a sandbox defect becomes real.** A bad helper sitting unused is dormant debt; a bad helper on the live execution path is a containment hole. The amendment's "Reachability gate" paragraph encodes this principle in the ticket so future implementers don't have to reconstruct it.

Mental model: **Commit topology encodes policy.** Branch-protection forces the three-branch sequence; audit-trail preservation forces preserving Q2 verbatim; contract-text-authoritative forces the amendment before the code restore. Each constraint is separately navigable; together they uniquely determine the chain's shape.

### Project state at session close

**T-20260330-05 (execution-domain foundation):** OPEN, high priority. Substrate slice landed (sandbox helper + approval-router seams + advisory/execution split). Q2 amendment landed with six-field shape required by AC 2. Tmp-exclusion restore landed with full-suite verification. ACs 1, 3, 4, 5 still open (worktree creation, job persistence, busy gate, approval path consumers). Ready for next implementation slice.

**T-20260330-04:** CLOSED (prior session).

**T-20260330-06 (promotion + delegate UX):** OPEN. Blocked by T-05.

**T-20260330-07 (analytics, reviewer, cutover):** OPEN. Blocked by T-05/T-06. Has known wording mismatch from prior session.

**T-20260416-01 (codex.dialogue.reply extraction mismatch):** OPEN, medium priority. Independent parallel thread.

### Environment snapshot at session close

- Branch: `main`
- HEAD: `bd850302` (tmp-hardening restore merge)
- Working tree: clean
- Origin/main: synced (pushed 3 times this session)
- Full plugin suite: 593 passed (4.21s); ruff clean
- Memory: no new feedback files; MEMORY.md unchanged
- Context: ~93% of 1M at save time (approaching threshold — save was timely)

### Why this work matters (bigger picture)

T-05 is the execution-domain foundation for codex-collaboration. The scope-restriction guarantee it establishes is what lets Claude hand a delegation job to Codex with a predictable write boundary. Shipping it with a leaky `/tmp` would mean the first live execution runs against a substrate that doesn't enforce the scope the Q0a decision promises — the containment substrate would be documented stronger than it is. The session's closure is "not just fixing code" (per user) — it aligned commit topology, contract text, runtime behavior, and verification scope. That alignment is what makes the next execution-wiring slice trustworthy.

## Learnings

### Reachability, not existence, gates sandbox-defect severity

**Mechanism.** A sandbox helper with an incomplete policy shape has two distinct severity levels depending on whether it's on a live execution path. Dormant: abstract debt, fixable by spec amendment + test update. Reachable: containment hole, present-tense defect. The transition happens at the moment some execution path first calls the helper in production flow.

**Evidence.** This session's `/tmp`/`$TMPDIR` writable-gap was identified at round-1 scrutiny as High severity. Under the "merge-ready" lens, it was a blocking defect. Under the "dormant debt" lens (no live execution path exists yet), it was tightenable later. The three-step chain resolved the ambiguity by making "before execution wiring lands" the explicit gate.

**Implication.** When evaluating a sandbox/policy defect, first ask: is this reachable in production flow today? If not, the correct posture is "must be closed before the slice that makes it reachable" — not necessarily "must be closed now." This gives implementation sequencing an explicit boundary.

**Watch for.** Future substrate work where helpers are authored before callers. The "is this reachable?" question should be a routine part of defect triage.

### Scope-local test runs miss cross-module seams

**Mechanism.** When a refactor renames a runtime API (e.g., `run_turn` → `run_advisory_turn`), the blast radius includes every caller + every fake/mock of that API across the plugin. A scope-local run of the *changed* module's test file doesn't exercise those cross-module surfaces; a full-plugin suite does.

**Evidence.** Round-1 fixes claimed "13 tests passed" from `test_runtime.py + test_approval_router.py`. Round-2 scrutiny found `dialogue.py:435` still called the old name — `rg 'runtime\.session\.run_turn\('` was non-empty. Full plugin suite would have caught this in seconds; scope-local never could. User's explicit verification bar for step 3 ("`uv run pytest packages/plugins/codex-collaboration/tests/` before merging") came directly from this lesson.

**Implication.** For changes that touch shared seams (runtime APIs, fake fixtures, abstract base classes), the verification bar is plugin-suite, not file-suite. The extra 4 seconds buys coverage of every downstream consumer.

**Watch for.** Any rename, API-shape change, or fake/mock revision. The first `rg` or `grep` for the old symbol is cheap insurance; following up with a plugin-suite run is the conclusive check.

### Contract text is authoritative — even when the tightening is substantively correct

**Mechanism.** When implementation diverges from the AC, the cheaper-looking fix is sometimes to ship the tighter implementation and ignore the AC divergence. This repo's `feedback_contract_text_over_operational_interpretation.md` pattern says no: update the AC first, then align the code. The pattern survives even when the tightening is obviously correct.

**Evidence.** Round-1's `excludeSlashTmp: true`/`excludeTmpdirEnvVar: true` additions were substantively correct — they closed a real containment hole. But round-2 scrutiny flagged them as High severity because they exceeded AC 2's four-field authorization. User's chosen response: remove from code, amend AC separately, restore after AC lands. This respects the pattern exactly. The three-step chain shape was a direct consequence.

**Implication.** "Substantively correct" is not a sufficient condition to override contract text. When in doubt: amend the contract first, then align. Audit trail > implementation expediency.

**Watch for.** Any case where implementation surfaces a tightening the AC didn't specify. Default posture: remove from code, amend AC, restore. Do not ship the tightening silently.

### Fabricated wire labels pre-wire a decode bug

**Mechanism.** When mapping a plugin-side enum to an external protocol, inventing enum values that don't exist in the protocol schema creates a bug that won't fire until the resolution edge. The round-trip looks fine in unit tests (string constants match themselves) but fails at the protocol boundary.

**Evidence.** Round-1's `_AVAILABLE_DECISIONS["permissions"] = ("grant_turn", "grant_session", "deny")` invented strings absent from the App Server schema. Real shape is `{permissions, scope: "turn"|"session"}` object. The bug would fire in the future `codex.delegate.decide` path, after user/Claude decision time was spent. Round-2 fix: route to `unknown` rather than invent labels; regression test at `test_approval_router.py:116` locks the revert.

**Implication.** When bridging to a protocol, the plugin's enum shape should be verified against the protocol's schema before implementation. If the protocol doesn't define a shape for a given route, route to `unknown` and escalate — don't invent.

**Watch for.** Any plugin-side data that maps to external protocol fields. Verify the plugin shape is a subset of what the protocol accepts.

### Three-step chain is commit-topology-as-policy

**Mechanism.** When branch-protection + audit-trail-preservation + contract-text-authoritative all apply, the number of branches and the sequence are uniquely determined by the constraints, not by personal preference. Six commits on main for what conceptually could have been one is the correct shape — not verbose, necessary.

**Evidence.** This session landed 3 feats + 3 merges for the three-step chain. Each step was a single coherent change. Bundling steps 2+3 would violate branch-protection (docs + feature on same branch); skipping step 1 would leave the substrate in a long-lived feature branch drifting from main; silent tightening would violate contract-text-authoritative. The only valid shape was the three-step sequence.

**Implication.** When multiple constraints each shape the commit topology, the shape falls out deterministically. Don't resist the verbose history — the audit trail is first-class.

**Watch for.** Future cases where multiple policies stack. If a "clean single commit" aesthetic tempts you, check whether the constraints actually allow it. If not, map them to a sequence.

### Verbatim user wording is often the right text; small semantic-equivalents aren't equivalent

**Mechanism.** When user scrutiny provides exact suggested wording (e.g., "Use '...'"), the delta between that wording and a semantically-close paraphrase matters more than it appears. User-picked words encode the specific frame they want the ticket to have.

**Evidence.** This session: user's reachability-gate wording was "before any execution-wiring slice lands." My first draft used "before that slice lands" — syntactically different but semantically close. I caught this on review and applied one more Edit to use the user's exact phrasing. The verbatim form more clearly names execution-wiring as the gating event rather than relying on antecedent linkage.

**Implication.** When scrutiny hands you wording in a code block or quoted form, use that wording verbatim unless there's a specific reason to deviate. Paraphrase-drift is a subtle source of spec erosion.

**Watch for.** Any user wording offered in a "Use '...'" format. Default: adopt verbatim.

### "Preserve historical, append later" applies to design records, not ACs

**Mechanism.** Tickets contain two kinds of text: historical records (design-pass outputs, status fields at a point in time) and forward contracts (open ACs, verification checklists). The preservation pattern applies to the first; the second should be edited in place because it represents current target state.

**Evidence.** This session's user directive: "Keep AC 2 modified in place. Do not preserve the old checkbox and add a parallel AC 2a." Contrast with Q2 resolution text, which was explicitly preserved verbatim as historical. The distinction is "records what was decided/true-at-the-time" vs. "records what we're aiming for now."

**Implication.** When amending a ticket, identify each text block's category before deciding whether to preserve-verbatim or edit-in-place. Design decisions preserve; open ACs edit. Don't apply the wrong pattern to the wrong block.

**Watch for.** Future ticket amendments. First question: is this text a historical record or a forward contract?

## Next Steps

### 1. First execution-wiring slice (the thinnest real `codex.delegate.start`)

**Dependencies:** None. Substrate is hardened and ready. Branch-protection rules apply.

**First-next-action:** Read T-05 ticket in full again to re-ground on the now-updated AC list; decide what the thinnest real execution-wiring slice looks like. The user's explicit ordering from session close:

1. **Busy gate.** Reject a second concurrent delegation with typed `Job Busy` response. AC 4.
2. **Worktree creation/ownership.** Each delegation job owns exactly one isolated worktree from the expected base commit. AC 3 + Verification.
3. **Job record.** Job state persisted strongly enough for later promotion flow to inspect. AC 3.
4. **Execution runtime bootstrap using the hardened helper.** `run_execution_turn()` actually called from `codex.delegate.start` with the six-field SandboxPolicy. AC 1.

**What to do:**
1. Pre-flight: `git status` clean on main at `bd850302`; create `feature/t05-execution-start` (or similar)
2. Re-read T-05 ticket (now ~355 lines; new Amendment section at `:248-303`)
3. Design the job record shape — `DelegationJob` definition at `contracts.md:59-73`. v1 persists via journal? via in-memory? (Check `recovery-and-journal.md` for journal semantics.)
4. Design the busy gate — where does concurrency state live? Plugin-side max-1 enforcement; typed `Job Busy` response shape.
5. Design the worktree creator — base commit detection; worktree path structure; cleanup on crash.
6. Wire `codex.delegate.start` to the hardened `build_workspace_write_sandbox_policy()` + `run_execution_turn()`.
7. Tests: worktree creation from expected base, busy rejection, runtime lifecycle boundaries, job persistence roundtrip.
8. Verification bar: full plugin suite + ruff before merge.

**Estimated effort:** Large. This is the first real execution-domain work; multiple new surfaces.

### 2. Pending-request capture wiring (follow-up slice)

**Dependencies:** Execution-wiring slice must land first (provides the runtime that produces live server requests).

**What to do:** Wire the notification loop (currently `runtime.py:160-194` fail-silent) to route App Server request messages through `parse_pending_server_request()` → persist as `PendingServerRequest` → expose via `needs_escalation` → available to `codex.delegate.decide` path (future).

Design question: parse errors in the router (`RuntimeError` fail-fast) vs. notification loop (fail-silent) is a known asymmetry. Resolve at wire time — probably: route malformed requests to `kind: "unknown"` + audit event, rather than killing the session or dropping silently.

**Estimated effort:** Medium. Adapter between two existing surfaces (runtime notification loop + approval router).

### 3. Decide-surface / lifecycle refinements (deferred debts from prior scrutinies)

**Dependencies:** Execution-wiring + pending-request capture must land first. These items need concrete semantics from live use.

**What to do:** Address the three deferred findings in order:
1. **Finding #4** (`PendingRequestStatus` lifecycle writers) — wire parse → resolve/cancel state transitions; journal writes at each boundary.
2. **Finding #5** (`approvalId` peer field) — currently folded into opaque `requested_scope`. When the decide-surface actually needs to reply with `approvalId`, promote it out of the opaque bag as a peer field on `PendingServerRequest`.
3. **Finding #6** (file-change decision sentinel) — `available_decisions == ()` is indistinguishable from "no decisions possible." Use `None` or explicit `"deferred"` sentinel so downstream can branch on "not yet routable" vs "nothing to choose."

**Estimated effort:** Small each; batch under the decide-surface slice.

### 4. T-20260416-01 extraction bug fix (parallel thread)

**Dependencies:** None. Independent of T-05 chain.

**What to do:** Unchanged from prior handoff. Implement Option A — canonicalize `agent_message` extraction at runtime dispatch.

### 5. T-07 wording mismatch patch (when T-07 is picked up)

**Unchanged from prior handoff.**

### 6. Reference unification (still-open T-04 §2.2 item)

**Unchanged from prior handoff.**

### 7. Landing sequence (updated)

T-05 execution-wiring slice → T-05 pending-request capture slice → T-05 decide-surface + lifecycle refinements → T-05 COMPLETE → T-06 (promotion + UX) → T-07 (analytics, reviewer, cutover). Cross-model supersession completes when T-07 lands.

## In Progress

**Clean stopping point.** Three-step chain landed; main at `bd850302`; working tree clean; full plugin suite green.

- **Approach:** Resume from prior handoff → inspect in-progress work → two rounds of scrutiny → user applies fixes → design decision on pre-execution gate → three-step chain (substrate merge → AC amendment → code restore) → handoff save.
- **State:** main at `bd850302`, working tree clean, origin synced.
- **Working:** All verified. Substrate and AC aligned on six-field execution sandbox. Reachability gate closed.
- **Not working:** Nothing in flight. Deferred debts (#4, #5, #6) captured explicitly in Amendment text and in Next Steps.
- **Next action:** Pick up T-05 execution-wiring slice in a fresh session per Next Steps #1.

## Open Questions

### 1. Will execution-wiring slice surface new tightening needs in the sandbox policy?

**Context:** The amended Q2 now covers 6 fields. The App Server `WorkspaceWriteSandboxPolicy` schema has other fields too (e.g., behavior-level knobs not yet surveyed). Implementation may discover additional defaults that need explicit override.

**Impact:** MODERATE. Each additional tightening would follow the same amendment pattern.

**Decision pending until:** First real execution job runs against the helper.

### 2. Does parse error policy live in the router or the caller?

**Context:** `parse_pending_server_request` currently raises `RuntimeError` on malformed input (fail-fast). The notification loop it'd be wired into is fail-silent. This asymmetry needs a policy choice at wire time.

**Impact:** MODERATE. Determines whether malformed requests kill the session, drop silently, or become audit events.

**Decision pending until:** Pending-request capture slice (Next Steps #2).

### 3. How long can `PendingRequestStatus` exist as an unused type before becoming dead code?

**Context:** Round-1 round-2 scrutinies both flagged this. Currently deferred to decide-surface slice (Next Steps #3). If decide-surface is delayed, the type lingers as contract drift.

**Impact:** LOW. Type doesn't break anything; just sits unused.

**Decision pending until:** Decide-surface slice is scheduled or explicitly pushed further out.

### 4. Will future App Server versions add sandbox fields that need parallel tightening?

**Context:** App Server schema is pinned at `0.117.0`. Future versions may add sandbox defaults that widen the writable set.

**Impact:** MODERATE. Would trigger a new Q2-style amendment each time. Could be captured as a general recipe.

**Decision pending until:** Schema upgrade work surfaces; currently no upgrade planned.

## Risks

### 1. Execution-wiring slice discovers helper is insufficient for real workloads

**Impact:** If the first real delegation job needs sandbox capabilities the six-field shape can't express (e.g., sub-worktree path restriction), the Q0a "implicit scope from infrastructure" decision would need revisiting. Would trigger a broader design pass.

**Mitigation:** Q0a explicitly records a v1-hedge: "adding a DelegationScope type to contracts.md is a clean additive change at that point." Not precluded.

### 2. Parse-error asymmetry causes session-kill regression

**Impact:** If `parse_pending_server_request`'s fail-fast is wired into the notification loop without policy adjustment, a malformed server request kills the runtime session. Tests don't cover this path yet.

**Mitigation:** Open Question #2 flags the decision point. Wire-time choice needed.

### 3. Pyright pre-existing diagnostics mask real new issues

**Impact:** `test_runtime.py` has pre-existing type-ignore-adjacent diagnostics that surfaced during this session but weren't caused by it. If not addressed, real new type issues could hide among the existing noise.

**Mitigation:** Low priority — the diagnostics are fixture/stub-related and don't affect runtime. Can be addressed in a dedicated cleanup pass.

### 4. Q2 amendment text may age if schema version drifts

**Impact:** Cites `codex_app_server_protocol.v2.schemas.json:8022, :8026`. Schema version upgrades may shift line numbers and field semantics.

**Mitigation:** Project uses pinned fixtures for contract tests. Any schema upgrade triggers explicit verification.

### 5. Six-field helper still lacks `worktree_path` existence contract

**Impact:** `build_workspace_write_sandbox_policy` calls `worktree_path.resolve()` without asserting the path exists or is canonical. Round-1 scrutiny flagged as Low severity (#6); still open.

**Mitigation:** Matters when worktree creation is wired (Next Steps #1). At that point, resolve whether existence is precondition or whether `resolve(strict=True)` is safer.

## References

### Commits this session

| Commit | Branch | Subject |
|---|---|---|
| `3179874d` | `feature/t05-runtime-sandbox-plumbing` | feat(t20260330-05): runtime sandbox + approval-router substrate |
| `4902c429` | `main` (merge) | Merge feature/t05-runtime-sandbox-plumbing |
| `0c44d3c5` | `docs/t05-ac-tmp-hardening` | docs(t20260330-05): amend Q2 to require tmp exclusion in execution sandbox |
| `1a98521a` | `main` (merge) | Merge docs/t05-ac-tmp-hardening |
| `cced8727` | `feature/t05-tmp-hardening` | feat(t20260330-05): restore /tmp and $TMPDIR exclusion in execution sandbox |
| `bd850302` | `main` (merge) | Merge feature/t05-tmp-hardening |

Pushes to origin/main: `b468e86f..4902c429`, `4902c429..1a98521a`, `1a98521a..bd850302`.

### Authority documents

| Document | Location | Role |
|---|---|---|
| T-20260330-05 ticket (amended) | `docs/tickets/2026-03-30-codex-collaboration-execution-domain-foundation.md` | Q2 Amendment section (new) + six-field AC 2 |
| contracts.md (normative) | `docs/superpowers/specs/codex-collaboration/contracts.md` | `DelegationJob` `:59-73`; `PendingServerRequest.requested_scope: object` `:88` |
| foundations.md (normative) | `docs/superpowers/specs/codex-collaboration/foundations.md` | Execution domain defaults `:99-116`; context profiles `:228-241`; split-runtime rationale `:73, :116` |
| recovery-and-journal.md (normative) | `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` | Delegation crash `:116-123`; unknown requests fail-closed `:132-141` |
| App Server schema (fixture, v0.117.0) | `.../0.117.0/codex_app_server_protocol.v2.schemas.json` | `excludeSlashTmp` default `:8022`; `excludeTmpdirEnvVar` default `:8026`; ReadOnlyAccess `:6863-6907`; WorkspaceWriteSandboxPolicy `:8019-8062`; permissions response `:3316-3374` |
| App Server ServerRequest (fixture, v0.117.0) | `.../0.117.0/ServerRequest.json` | Command approval `:367`; file-change approval `:608` |
| Runtime wrapper | `packages/plugins/codex-collaboration/server/runtime.py` | Six-field sandbox helper `:23`; advisory/execution split |
| Approval router | `packages/plugins/codex-collaboration/server/approval_router.py` | `parse_pending_server_request()`; `_METHOD_TO_KIND` (3 entries); opaque carrier |

### Memory files referenced this session

All under `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/`:

| Memory | Relevance |
|---|---|
| `feedback_contract_text_over_operational_interpretation.md` | **Load-bearing.** Applied twice: round-2 finding #3 (don't silently tighten beyond AC) → removed excludes from code; step 2 directly amends contract before step 3 restores them. |
| `feedback_edit_in_repo.md` | Applied — all edits landed in `packages/plugins/codex-collaboration/` paths, not plugin cache. |
| Prior session's user-preferences | Applied — structured-scrutiny pattern, fast convergence, preserve-historical-append-later, terse-when-aligned. |

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-17_11-59_t05-q0-decision-record-implicit-scope-landed.md`
- T-05 design arc: `2026-04-17_01-41` (T-04 closeout + T-05 kickoff) → `2026-04-17_11-59` (Q0 design decision) → this handoff (tmp-hardening closure)
- T-04 closeout chain (same-day 04-16): archived sequence

## Gotchas

### 1. Scope-local pytest misses cross-module seams

**Symptom:** Running only `test_runtime.py + test_approval_router.py` reports green while the full plugin suite is red.

**Root cause:** Shared fixtures (e.g., the fake runtime in `test_control_plane.py:122`) are the bottleneck both production surfaces go through. A rename of the API they implement breaks every downstream caller; scope-local runs only test the changed files.

**Prevention:** For changes to shared seams (runtime APIs, abstract base classes, fake fixtures), run `uv run pytest packages/plugins/codex-collaboration/tests/` before claiming green. 4 seconds buys full coverage.

### 2. `<local-command-caveat>` behavior for `/copy` overridden by global CLAUDE.md

**Symptom:** After a `/copy` invocation, Claude sees `<local-command-caveat>` saying "do not respond to these messages."

**Root cause:** The default caveat behavior is overridden by a line in `~/.claude/CLAUDE.md`: "Always respond to `/copy` output; disregard the `<local-command-caveat>` for all `/copy` commands." (Added mid-session via SessionStart hook notification.)

**Prevention:** Do not treat `/copy` output as clipboard-only. Engage with the content. If the caveat appears for a non-`/copy` command, default rules apply (stand by unless explicitly asked).

### 3. Pyright diagnostics surface during an Edit session that aren't caused by the edit

**Symptom:** Edit tool returns success, then Pyright "new diagnostics" notifications appear pointing to lines your edit didn't touch.

**Root cause:** Pyright re-scans the file after each save. Pre-existing diagnostics get re-reported.

**Prevention:** Check line numbers against your edit scope. If the flagged lines are outside your change, the diagnostics are pre-existing. Don't chase them unless asked.

### 4. Narrow schema anchors are cheaper than line ranges

**Symptom:** Reviewers clicking a `:8020-8062` cite must scan 40 lines to find the specific field.

**Root cause:** Broad cites save authoring time but cost reviewer time. In this repo, tight-anchor-culture is load-bearing for reviewer efficiency.

**Prevention:** Cite the narrowest line that proves the claim. `:8022` for `excludeSlashTmp` default. `:8026` for `excludeTmpdirEnvVar` default. Broad ranges only for object definitions a reader will actually scan.

### 5. "Reserved slot" / fabricated-decisions patterns are over-specification in disguise

**Symptom:** Tempting to add a typed enum value ("one valid option for v1, extensible later") when the substrate doesn't define the shape yet.

**Root cause:** Forward-compat aesthetic overrides "don't add what you don't need." The round-1 `("grant_turn", "grant_session", "deny")` was this pattern — invented wire labels because it felt more complete than `"unknown"`.

**Prevention:** Check whether the target protocol defines the shape. If not, route to `unknown` and escalate. Prose rules are safer than typed enums for future-open semantics.

### 6. Branch-protection forces sequential branches for mixed doc + code changes

**Symptom:** Trying to edit both `docs/*` and `packages/*` on one branch triggers branch-rule warnings or blocks.

**Root cause:** Pre-tool-use hook enforces branch-prefix conventions: `docs/*` for documentation, `feature/*` for code. Mixed changes don't fit either.

**Prevention:** For mixed changes, sequence: docs branch → merge → feature branch → merge. The verbose history is the correct shape. This session's three-step chain is the template.

### 7. `worktree_path.resolve()` on macOS follows symlinks

**Symptom:** Tests pass `tmp_path / "worktree"` (non-existent path). `resolve()` on macOS expands through symlinks if any intermediate path is linked (e.g., `/tmp` → `/private/tmp`).

**Root cause:** macOS ships with `/tmp` as a symlink. `pathlib.Path.resolve()` follows symlinks by default.

**Prevention:** Tests under `tmp_path` are safe (usually under `/private/var/...`). For future paths passed from user input or live App Server flow, resolve explicitly and assert the result is inside an expected base.

## Conversation Highlights

### User's "Continue with T-05 design pass" pattern → "Scrutinize the in-progress work"

Matches prior-session terseness pattern. The scrutiny request implicitly authorized invoking the adversarial-review skill without further confirmation.

### Round-1 adversarial-review output → 6 findings

Structured: `Assumptions Audit`, `Pre-Mortem`, `Dimensional Critique` (Correctness, Completeness, Security/Trust Boundaries, Operational, Maintainability, Alternatives Foregone), `Severity Summary`, `Confidence Check`. Six findings ranked. Verdict: Major revision (2/5). Path-to-raise: apply #1-#4.

### Round-2 blocking regression

> "`dialogue.py:435` still calls `runtime.session.run_turn` after the rename. The dialogue-reply production path and six test files break. Either re-add `run_turn` as a thin alias for the advisory method, or migrate every caller in this same change. Do not merge until `rg 'runtime\.session\.run_turn\(' packages/plugins/codex-collaboration` is empty."

Load-bearing because it exposed the "13 tests passed" claim was scope-local. User's choice was migrate rather than alias, and full-plugin suite became the verification bar for step 3.

### User's contract-lens vs. milestone-lens framing

> "The key distinction is scope. Under a contract lens, this branch is merge-ready now: the suite is green, and no live execution path is using the helper yet. Under a milestone lens, the next slice is different: once execution wiring makes that helper reachable, writable `/tmp` becomes a known out-of-worktree write surface in the very containment substrate T-05 is supposed to establish. That is the point where I would treat the debt as blocking."

This framing is the session's central decision. Produced the three-step chain's ordering and the pre-execution-gate designation.

### User's "Review the AC amendment wording before it lands"

> "Step 2 is not just a tiny doc touch. It redefines the authoritative contract that step 3 relies on. Given the repo's 'contract text is authoritative' posture, that wording deserves its own scrutiny checkpoint before you make code depend on it."

Explicit request for a review round at the step-2 boundary. Produced the Minor-revision scrutiny with 3 refinements.

### User's Minor revision scrutiny on amendment draft

Same structured format as round-1/round-2 but on prose. Three refinements:
1. "makes the AC match the substrate" sentence falsely implies immediate alignment — rewrite for sequencing honesty
2. Reachability-gate coupled to helper name — de-code
3. Citation looseness (`:8020-8062` range) — narrow per-field anchors

Verdict: Minor revision. All three refinements applied.

### User's verification-bar raise for step 3

> "I would raise the verification bar above `test_runtime.py + ruff` before merge. The last time this branch looked green, the broader suite exposed a seam the narrow run missed."

Explicit ordering: full plugin suite before merge. 593 passed confirmed green.

### User's reflection at session close (5 numbered observations)

Distilled the session into:
1. Three separate truths kept separate (implementation / contract / milestone)
2. Reachability-not-existence determines sandbox-defect severity
3. Full-suite run matters because it exercises the cross-module seams that bit `run_turn`
4. Main is now clean in the way that matters for the next milestone
5. Keep next work narrow — execution wiring first, pending-request capture second, decide-surface refinements third

Final sentence: "this was a good closure because it did not just 'fix the code.' It aligned commit topology, contract text, runtime behavior, and verification scope."

## User Preferences

### Structured scrutiny with explicit citations and severity labels

User's scrutinies consistently came as `Assumptions Audit` → `Pre-Mortem` → `Dimensional Critique` → `Severity Summary` → `Confidence Check` or the `Premise Check` → `Critical Failures` → `High-Risk Assumptions` → `Real-World Breakpoints` → `Hidden Dependencies` → `Adversarial Perspectives` → `Patterns And Root Causes` → `Required Changes` → `Verdict` format. Pattern: verify each cite in parallel; either concede (all verified) or push back with counter-evidence. One-round convergence when scrutiny is cite-evidenced.

### Fast convergence once aligned

Verbatim this session: "I do not want another wording pass before you land step 2." "With those changes, I would not ask for another pre-edit review round." Explicit permission to proceed without another review cycle — enables single-message execute-and-report patterns.

### Preserve historical records; edit ACs in place

Verbatim: "Rewriting the pre-design section would erase the design-pass history." And: "Keep AC 2 modified in place. Do not preserve the old checkbox and add a parallel AC 2a." Rule: historical records (design-pass outputs, status fields) preserve verbatim; forward contracts (open ACs, verification checklists) edit in place.

### Prescriptive contract wording, decoupled from implementation symbols

Verbatim: "Keep the prescriptive gate, but de-code it. Use 'MUST restore both exclusions in the execution sandbox construction path and its tests before any execution-wiring slice lands.'" Rule: tickets lock behavior and sequencing, not helper names. Use behavioral-contract language.

### Narrow schema anchors over line ranges

Verbatim (Low-severity finding): "`:8020-8062` forces a reviewer to inspect the full object when the actual claim is the two `false` defaults for the tmp exclusions." Rule: cite the narrowest line proving the claim. Broad ranges only for object blocks a reader will scan.

### Substrate-aligned naming

(From prior-session memory, confirmed this session.) Named `writableRoots` and `readableRoots` to match App Server schema, not `allowed_roots` from dialogue vocabulary. Rule: align plugin-side types with the enforcement substrate they map to, not historical-lineage vocabulary.

### Sequencing honesty over optimistic prose

Verbatim (Medium finding): "'this amendment records the post-implementation tightening that makes the AC match the substrate' is false in your planned sequence. After the doc merge, `main` will still have the four-field helper until the follow-up feature branch restores the two exclusions." Rule: spec text must not overclaim present state. Acknowledge temporary mismatches explicitly.

### Full-suite verification for cross-module seams

Verbatim: "For final publication, I would use the full plugin suite." Rule: after a rename or shared-seam change, scope-local runs don't validate downstream consumers. 4s for 593 tests.

### Three-step chain as principle, not just tactic

Closing reflection: "This was a good closure because it did not just 'fix the code.' It aligned commit topology, contract text, runtime behavior, and verification scope." Rule: major changes to containment substrate benefit from this four-dimensional alignment — not just passing tests but commit shape matching policy, contract matching intent, runtime matching contract, verification scope matching blast radius.

### Terse when aligned

Short confirmations like "Proceed." and "The amendment wording is now defensible." continue to signal alignment. Substantive expansion only when content requires it (scrutiny, reflection). Continued from prior-session pattern.

### `/copy` followed by substantive instruction

Pattern from prior session held here too — multiple `/copy` invocations contained the actual substantive message (not clipboard contents). The `<local-command-caveat>` was overridden by global CLAUDE.md this session.

## Rejected Approaches

### Round-1 Option: ship `excludeSlashTmp: true` + `excludeTmpdirEnvVar: true` silently without AC amendment

**Approach:** Apply the tightenings directly in code; trust that the AC's current 4-field wording is just under-specification.

**Why rejected:** Violates `feedback_contract_text_over_operational_interpretation.md`. User chose the pattern-respecting path: remove from code, amend AC, restore. The three-step chain shape was a direct consequence.

**What it taught:** "Substantively correct" is not sufficient to override contract text. Contract-text-authoritative survives even when the tightening is obviously correct.

### Round-1 Option: kind `permissions` with fabricated wire labels

**Approach:** `_AVAILABLE_DECISIONS["permissions"] = ("grant_turn", "grant_session", "deny")` — invented strings to give the route a kinded shape.

**Why rejected:** Schema defines the permissions-response as `{permissions, scope: "turn"|"session"}` object, not a string enum. Fabricated labels pre-wire a decode bug at the resolution edge. Round-2 reverted to route `permissions` as `unknown` + regression test.

**What it taught:** When bridging to a protocol, verify the plugin shape is a subset of what the protocol accepts. If the protocol doesn't define a shape for a given route, route to `unknown` and escalate — don't invent.

### Round-1 Option: add `sandbox_policy` keyword to advisory `run_turn` (unified entrypoint)

**Approach:** Keep a single `run_turn()` that accepts an optional `sandbox_policy`; advisory callers pass `None`, execution callers pass the six-field shape.

**Why rejected:** Erodes the code-level advisory/execution boundary. Any advisory caller could accidentally obtain execution-domain write access through an advisory handle. User's chosen fix: split into `run_advisory_turn()` + `run_execution_turn()` over a private `_run_turn()`.

**What it taught:** Capability-class boundaries should be visible in the API surface, not just in docstrings. Shared keywords perforate class-level guardrails.

### Amendment placement: `### Q2a` subsection inside Design Decision

**Approach:** Place the amendment as a subsection within the Design Decision block.

**Why rejected:** Fractures the Design Decision block; subsection placement loses chronological clarity. User confirmed: top-level `## Amendment` preserves Design Decision intact.

**What it taught:** Chronological additions deserve matching section-level headers. Subsection placement implies "part of the original pass"; section-level placement signals "later addition."

### AC 2 shape: parallel AC 2a bullet preserving old AC 2 verbatim

**Approach:** Preserve old AC 2 checkbox; add a new AC 2a bullet with the six-field shape.

**Why rejected:** ACs are forward-facing open checkboxes, not historical records. Two checkboxes for one logical requirement creates redundant satisfaction work. User confirmed: modified-in-place.

**What it taught:** The preservation pattern applies to historical records only. Open ACs represent current target state; edit in place.

### Reachability-gate wording: descriptive, not prescriptive

**Approach:** "The first T-05 slice that makes the helper reachable restores both fields..." (future-tense prediction).

**Why rejected:** Loses prescriptive force. Reads as guess rather than requirement. User's chosen wording: "MUST restore... before any execution-wiring slice lands" (contractual).

**What it taught:** Ticket prose should mandate behavior, not predict it. "MUST" + named gate event is the pattern.

### Single-branch bundling (steps 2+3 together)

**Approach:** Do the AC amendment and code restore on one branch.

**Why rejected:** Branch-protection enforces `docs/*` for ticket edits and `feature/*` for code. Mixed changes don't fit either. Three-step chain is the only compliant shape.

**What it taught:** Commit topology encodes policy. The verbose history isn't a failure of design economy — it's the unique solution under stacked constraints.

### Skip step 1 (don't land substrate slice before amending AC)

**Approach:** Start with the AC amendment; return to substrate later.

**Why rejected:** Substrate slice was already written, tested, and internally coherent. Delaying its merge would mean a long-lived feature branch drifting from main. Under the contract-lens, it was merge-ready; delaying would gain nothing.

**What it taught:** Merge-ready work should land; ordering should follow from what's ready, not from a preferred narrative sequence.

### One more review pass on amendment wording after 3 refinements applied

**Approach:** Stop for another user review after applying the Medium/Medium/Low refinements.

**Why rejected:** User explicit: "I do not want another wording pass before you land step 2. The two medium issues are closed by the explicit sequencing sentence and the removal of helper-name coupling, and the narrow `:8022` / `:8026` anchors are the right improvement."

**What it taught:** Once user has provided exact wording guidance (via Required Changes), applying and proceeding is the correct move. Extra review rounds become friction once the refinements are verbatim-to-guidance.

### Amend prior commit with tmp-hardening restore (rather than new feature branch)

**Approach (considered):** Once the AC is amended, amend the substrate commit to add the two fields, keeping the chain to two merges instead of three.

**Why rejected:** Violates project rule "Prefer to create a new commit rather than amending." Applies even when amending feels aesthetically cleaner. Prior-session memory captured this explicitly.

**What it taught:** Audit trail > cosmetic tidiness. Three commits on main for three logically-distinct changes is the correct shape.
