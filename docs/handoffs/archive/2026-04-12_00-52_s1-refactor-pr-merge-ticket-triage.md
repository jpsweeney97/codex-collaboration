---
date: 2026-04-12
time: "00:52"
created_at: "2026-04-12T04:52:29Z"
session_id: f75f6bd1-685a-4bce-a0d1-f0c2fbaf18ea
resumed_from: docs/handoffs/archive/2026-04-11_21-53_pr-104-race-fix-smoke-setup-parity-marked-ready.md
project: claude-code-tool-dev
branch: main
commit: 7f7cbfc6
title: S-1 FileFailure refactor, PR #104 merged, ticket triage clears 3
type: handoff
files:
  - packages/plugins/codex-collaboration/server/containment.py
  - packages/plugins/codex-collaboration/tests/test_containment.py
  - packages/plugins/codex-collaboration/tests/test_clean_stale_shakedown.py
  - docs/tickets/2026-04-03-t7-conceptual-query-corpus-design-constraint.md
  - docs/tickets/2026-03-27-r1-carry-forward-debt.md
  - docs/tickets/2026-04-10-T-20260410-04-align-cleanstaleshakedownpy-with-script-convention.md
  - docs/tickets/2026-04-10-T-20260410-03-harden-stale-cleanup-observability-and-failure-rep.md
---

# S-1 FileFailure Refactor, PR #104 Merged, Ticket Triage Clears 3

## Goal

Three-part session: (1) implement the highest-leverage deferred review suggestion from PR #104 (S-1 `NamedTuple FileFailure`), (2) merge PR #104 and close T-03, (3) triage the full ticket backlog to identify what to work on next.

**Trigger:** Session resumed from a handoff where PR #104 had been pushed and marked ready for review. CI was green, no reviewer feedback. The user wanted to revisit the deferred suggestions from the prior session's parallel review, specifically the S-1 `FileFailure` refactor.

**Stakes:** PR #104 represented the culmination of the T-03 observability hardening work — 17 commits across 5 sessions. Merging it and closing the ticket was the primary milestone. The ticket triage addressed backlog hygiene: 11 active tickets, some 13+ days old, with unclear staleness.

**Success criteria (all met):**
- S-1 `FileFailure` NamedTuple implemented and pushed to PR #104
- PR #104 merged via GitHub UI (user action)
- Ticket T-20260410-03 closed as `done`
- Local branch `fix/t03-stale-cleanup-observability` deleted, remote pruned
- 3 stale/obsolete tickets closed during triage
- Clear next-work recommendation produced

**Connection to project arc:** T-03 is now fully closed. The ticket triage surfaced T-20260410-02 (dialogue first-turn hardening) and T-20260330-02 (codex-collaboration plugin shell) as the top next-work candidates. The user confirmed during triage that codex-collaboration is still the intended successor to the current cross-model plugin — a strategic clarification that was saved to memory.

## Session Narrative

Session opened by loading the prior handoff via `/load`. The handoff described PR #104 in ready-for-review state with all commits pushed and CI pending. The user confirmed CI was green and no reviewer feedback needed addressing, then asked about the deferred suggestions from the prior session's parallel review.

**Phase 1 — Identifying the deferred suggestions (~5 min):**

The handoff referenced "7 deferred Suggestions" from the parallel review but only explicitly named 3: S-1 (`NamedTuple FileFailure`), S-3 (`skipped_non_regular` bucket), and S-6 (`sys.modules` cleanup). The remaining 4 (S-2, S-4, S-5, S-7) were described only as "deferrable hygiene items." I searched the prior archived handoff at `docs/handoffs/archive/2026-04-11_21-24_pr-104-review-option-b-commits-pending-push.md` for the full list but the individual S-2/S-4/S-5/S-7 descriptions weren't preserved — the review agent outputs were transient. I presented the known items and asked whether to reconstruct the full list from the code or focus on S-1. The user chose: *"I would rather just focus on S-1 as the highest-leverage item."*

**Phase 2 — Implementing S-1 FileFailure refactor (~15 min):**

I used `Grep` to map every touchpoint of `failed_stat`, `failed_unlink`, and `CleanStaleResult` across the codex-collaboration package. Found ~50 grep hits across 5 files. Then read the production code (`containment.py:290-360` for `CleanStaleResult`, `:410-496` for `clean_stale_files`) and the key test sites to understand the full scope:

- **Production code:** 2 type annotations on `CleanStaleResult` fields (`:314-315`), 2 local list type annotations (`:410-411`), 2 append sites in the sweep loop (`:474, :487`), 2 unpack sites in `report()` (`:351-354`)
- **Test code:** 3 `CleanStaleResult` constructors with inline tuple literals (`test_containment.py:510-511, 534-535`, `test_clean_stale_shakedown.py:150`), 2 positional unpacks (`test_containment.py:266, 296`), 2 positional index accesses (`test_containment.py:599, 601`)

The key design choice was using `NamedTuple` rather than `@dataclass(frozen=True)`. NamedTuple is tuple-compatible, so existing `for path, error in self.failed_stat` unpacking in `report()` and `== ()` emptiness checks in tests continue to work unchanged. A frozen dataclass would break both patterns. I explained this reasoning to the user before editing.

Made 10 sequential edits across 3 files:
1. Added `NamedTuple` to the `typing` import in `containment.py`
2. Defined `FileFailure(NamedTuple)` with `path: Path` and `error: str` fields, with a docstring
3. Updated `CleanStaleResult` docstring from `(path, error_repr) pairs` to `:class:FileFailure entries`
4. Changed field type annotations from `tuple[tuple[Path, str], ...]` to `tuple[FileFailure, ...]`
5. Changed local list annotations from `list[tuple[Path, str]]` to `list[FileFailure]`
6. Changed both append sites to use `FileFailure(path, ...)`
7. Updated 2 `CleanStaleResult` constructors in `test_containment.py` to use `containment.FileFailure(...)`
8. Updated 1 stub constructor in `test_clean_stale_shakedown.py` to use `FileFailure(...)`
9. Replaced positional unpacks (`failed_path, failed_repr = result.failed_unlink[0]`) with named access (`.path`, `.error`)
10. Replaced positional index access (`result.failed_stat[0][0]`) with `.path`

Ran ruff + full pytest in parallel: ruff clean on all 3 files, **546/546 tests pass** in 3.98s. Zero regressions — the NamedTuple's tuple compatibility made this a purely mechanical refactor.

Committed as `3d81c719` with conventional message `refactor(containment): replace failure tuples with FileFailure NamedTuple`. Pushed to update PR #104 (fast-forward `62765e81..3d81c719`).

**Phase 3 — User review and PR merge (~5 min):**

The user reviewed PR #104 one final time after the S-1 push. Report: *"No findings!"* They merged via GitHub's UI. I then:
1. Updated ticket T-20260410-03: `status: deferred → done`, corrected `branch:` from the source PR's branch to the actual implementation branch
2. Switched local repo to `main`, pulled merged changes (hit a divergent-branch situation because the ticket update commit was on local `main` but not on `origin/main` before the merge), resolved via `git stash && git rebase origin/main && git stash pop`
3. Committed and pushed the ticket status update as `ce720ada`
4. Deleted local branch `fix/t03-stale-cleanup-observability` and pruned the remote tracking ref

A notable issue during cleanup: the `git stash && rebase && stash pop` flow left the ticket edits as unstaged working-tree changes rather than in the committed state. The first push sent the rebased commit without the ticket update, requiring a second commit (`ce720ada`). The lesson: when stashing across a rebase that changes the base, verify the stash-pop result is reflected in the committed state.

**Phase 4 — Ticket triage (~20 min):**

The user asked what to do next. I ran the `making-recommendations` skill and produced a structured recommendation. The top recommendation was to triage the ticket backlog first — 9 open tickets, some from March 30 with unclear staleness. The user approved.

Attempted to run the ticket plugin's triage scripts (`ticket_triage.py dashboard` and `audit`), but the plugin's `ticket_engine_guard.py` PreToolUse hook blocked the invocations because `CLAUDE_PLUGIN_ROOT` was not set in this session. Fell back to manual triage by reading each ticket's frontmatter directly.

Walked through each stale/questionable ticket one at a time with the user, presenting the context, staleness signal, and recommendation for each:

| Ticket | Decision | User's reasoning |
|--------|----------|------------------|
| **T-20260403-01** (T7 corpus design) | **wontfix** | Benchmark tiers discontinued March 17; ticket filed April 3 with no live consumer; ADR retained as historical context |
| **T-20260327-01** (R1 debt triage) | **closed** | Umbrella triage complete; items 6-7 resolved; items 1-5 parked with explicit trigger conditions; keeping open makes backlog noisy; re-enter via new tickets when triggers fire |
| **T-20260330-02 through -07** (6 tickets) | **kept open** | User confirmed codex-collaboration is still the intended successor to the current cross-model plugin; supersession plan is active |
| **T-20260410-01** (dialogue turn semantics) | **kept open** | Fresh (2 days), concrete, small, unblocked |
| **T-20260410-02** (dialogue hardening) | **kept open** | Fresh, high-priority, adjacent to same package, strong next-work candidate |
| **T-20260410-04** (script conventions) | **done** | All 4 acceptance criteria already fulfilled by PR #104 work; verified by reading current code |

The user provided detailed reasoning for each decision, often 100+ words. Key pattern: the user evaluates tickets against *actionability* — "An open ticket should represent work someone could pick up now." Umbrella tickets that function as parking lots are closed; the parking-lot items re-enter scope via new targeted tickets.

Committed and pushed all 3 ticket closures as `7f7cbfc6`.

## Decisions

### Decision 1: Use NamedTuple for FileFailure (not dataclass)

**Choice:** Define `FileFailure` as a `NamedTuple` subclass with `path: Path` and `error: str` fields.

**Driver:** The existing code uses positional tuple patterns everywhere — `for path, error in self.failed_stat` in `report()`, `== ()` emptiness checks in tests, `result.failed_stat[0][0]` index access. A dataclass would break all of these patterns, requiring changes to `report()` and dozens of test assertions.

**Alternatives considered:**
- **(a) NamedTuple** (chosen) — tuple-compatible, supports iteration/unpacking, immutable, lightweight
- **(b) @dataclass(frozen=True)** — immutable but not tuple-compatible; would break `for path, error in ...` unpacking and `== ()` comparisons
- **(c) TypedDict** — dict-based, not tuple-compatible, no field access syntax
- **(d) Keep bare tuples** — status quo; retains fragility

**Rejection reasons:**
- (b) Would require rewriting `report()` method's iteration and many test assertions — scope creep for what should be a mechanical refactor
- (c) TypedDict is for dict-shaped data, not sequence-shaped; poor fit
- (d) The whole point of S-1 is removing the fragility

**Trade-offs:** NamedTuple's iteration order is implicitly part of the contract. If someone adds a field between `path` and `error`, existing `for path, error in ...` unpacking breaks. Mitigated by the fact that adding fields to a NamedTuple would naturally go at the end (append-only), and the `report()` method would need updating regardless.

**Confidence:** Very high (E3) — verified empirically (546/546 tests pass), verified by code reading (all existing patterns preserved), verified by Python language spec (NamedTuple is a tuple subclass).

**Reversibility:** High — revert the commit; the old tuple pattern still works.

**Change trigger:** If `FileFailure` needs to carry non-tuple-compatible data (e.g., an `OSError` object rather than its repr), a dataclass would be more appropriate. But the current design deliberately stores the repr as a string for serialization/log-safety.

### Decision 2: Close T-20260327-01 (R1 debt) rather than keep as backlog

**Choice:** Close the umbrella triage ticket with a note that parked items re-enter scope via new targeted tickets.

**Driver:** User stated: *"this is no longer an actionable ticket. An open ticket should represent work someone could pick up now."* The ticket had 2 resolved items and 5 parked items with explicit trigger conditions (R2, delegation, advisory-widening) that haven't fired.

**Alternatives considered:**
- **(a) Keep open** — backlog reminder for parked items
- **(b) Close with note** (chosen) — re-enter via new tickets when triggers fire
- **(c) Close items 6-7, keep open for 1-5** — split resolved vs parked state

**Rejection reasons:**
- (a) User: keeping it open "makes backlog health noisier" and "turns the backlog into a historical note instead of an execution queue"
- (c) User: "splitting resolved vs parked state inside one still-open umbrella ticket preserves the same problem: it remains non-actionable"

**Trade-offs:** Parked items are no longer tracked in any ticket. Risk of forgetting them when their triggers fire. Mitigated by the trigger conditions being explicit in the closed ticket's body and closure note.

**Confidence:** High (E2) — user's reasoning is sound and the ticket body preserves all context.

**Reversibility:** High — reopen the ticket or file new targeted tickets.

**Change trigger:** If R2/delegation/advisory-widening work begins and the parked items aren't independently filed, this closure was premature.

### Decision 3: Close T-20260403-01 (T7 corpus design) as wontfix

**Choice:** Close the benchmark-related ticket as `wontfix` and clear its `blocks: [T6-composition-check]` field.

**Driver:** MEMORY.md records benchmark tiers A and B discontinued on March 17. This ticket was filed April 3 but targets benchmark-only machinery (corpus constraints, validator rules, scored runs). User's reasoning: *"the deciding fact is that the benchmark program was discontinued on March 17, 2026, and this ticket, filed on April 3, 2026, still appears scoped entirely to benchmark-only machinery"*.

**Alternatives considered:**
- **(a) Keep open** — in case benchmark work resumes
- **(b) Close as wontfix** (chosen) — benchmark discontinued, no live consumer
- **(c) Repurpose** — adapt the corpus design constraint for a non-benchmark use case

**Rejection reasons:**
- (a) No signal that benchmark work will resume; keeping it open adds noise
- (c) User: *"If some future non-benchmark workflow needs the same constraint, that should come back as a new ticket with a non-benchmark consumer instead of keeping this one open"*

**Trade-offs:** ADR at `docs/decisions/2026-04-03-conceptual-query-scope-constraint-for-benchmark-v1.md` is retained as historical context, but the implementation ticket is closed. If benchmark work ever resumes, this constraint would need a new ticket.

**Confidence:** High (E2) — benchmark discontinuation is documented in MEMORY.md and confirmed by project history.

**Reversibility:** High — reopen or file new ticket.

**Change trigger:** Benchmark program reinstated.

### Decision 4: Close T-20260410-04 (script conventions) as done

**Choice:** Close the deferred ticket because all 4 acceptance criteria were already fulfilled by PR #104 work.

**Driver:** Verified each criterion against the current code:
- Import shim pattern: identical `sys.path.insert(0, str(_PACKAGE_ROOT))` across all 3 sibling scripts
- `main()` entry point: present at `clean_stale_shakedown.py:19`
- `__main__` guard: present at `:46`
- Canonical error format: `Got: {exc!r:.100}` at lines 24, 33, 51

User confirmed: *"this ticket no longer represents future work. Its acceptance criteria were absorbed by the merged T-03 work"*

**Alternatives considered:**
- **(a) Keep open** for any remaining convention gaps
- **(b) Close as done** (chosen)

**Rejection reasons:**
- (a) User: *"keeping it open would just duplicate already-landed scope. If a future script-convention delta appears, that should be a new ticket"*

**Trade-offs:** None — the work is done.

**Confidence:** Very high (E3) — verified all 4 criteria by reading the current file and comparing with sibling scripts.

**Reversibility:** N/A — the work is already merged.

**Change trigger:** None — acceptance criteria met.

### Decision 5: Confirm codex-collaboration as intended successor (strategic)

**Choice:** Keep T-20260330-02 through -07 open. codex-collaboration is still the intended successor to the current cross-model plugin despite D-prime's completion and the shim being kept.

**Driver:** User confirmed directly when asked: *"codex-collaboration is still the intended successor to the current cross-model plugin."* This was a key strategic clarification — MEMORY.md's note about D-prime being complete and the shim being retained could lead future sessions to incorrectly conclude the supersession plan was abandoned.

**Alternatives considered:**
- **(a) Keep the chain open** (chosen) — supersession confirmed active
- **(b) Close the chain** — if D-prime's success had changed the strategy
- **(c) Partial close** — keep some tickets, close others

**Rejection reasons:**
- (b) User explicitly confirmed the plan is active
- (c) The tickets form a strict dependency chain; partial closure would leave orphaned blockers

**Trade-offs:** 6 high-priority tickets remain in the backlog. T-20260330-02 (plugin shell) is the root blocker — 5 tickets are transitively blocked on it. This is the highest-leverage work in the queue but also the largest (medium-to-large effort across the chain).

**Confidence:** Very high (E3) — direct user confirmation.

**Reversibility:** High — close tickets if strategy changes.

**Change trigger:** User decides the current cross-model plugin is sufficient long-term.

## Changes

### Commit `3d81c719` — `refactor(containment): replace failure tuples with FileFailure NamedTuple`

**`packages/plugins/codex-collaboration/server/containment.py`** (+21/-11 lines):
- Added `NamedTuple` to `typing` import at line 10
- Defined `class FileFailure(NamedTuple)` with `path: Path` and `error: str` fields and docstring (12 lines) at line 293
- Updated `CleanStaleResult` docstring: `(path, error_repr) pairs` → `:class:FileFailure entries`
- Changed field type annotations: `tuple[tuple[Path, str], ...]` → `tuple[FileFailure, ...]`
- Changed local list annotations: `list[tuple[Path, str]]` → `list[FileFailure]`
- Changed append sites: `(path, f"{exc!r:.100}")` → `FileFailure(path, f"{exc!r:.100}")`

**`packages/plugins/codex-collaboration/tests/test_containment.py`** (+10/-12 lines):
- Replaced positional unpacks at lines 266, 296 with named access (`.path`, `.error`)
- Replaced positional index access at lines 599, 601 with `.path`
- Updated 2 `CleanStaleResult` constructors to use `containment.FileFailure(...)`

**`packages/plugins/codex-collaboration/tests/test_clean_stale_shakedown.py`** (+2/-2 lines):
- Added `FileFailure` to import from `server.containment`
- Updated 1 stub constructor to use `FileFailure(...)`

### Commit `ce720ada` — `chore(ticket): close T-20260410-03 after PR #104 merge`

- Updated `docs/tickets/2026-04-10-T-20260410-03-*.md`: `status: deferred → done`, corrected `branch:` field

### Commit `7f7cbfc6` — `chore(tickets): triage — close 3 resolved/obsolete tickets`

- Updated `docs/tickets/2026-04-03-t7-*.md`: `status: open → wontfix`, cleared `blocks`, added closure note
- Updated `docs/tickets/2026-03-27-r1-*.md`: `status: open → closed`, added closure note with item-by-item status
- Updated `docs/tickets/2026-04-10-T-20260410-04-*.md`: `status: deferred → done`, corrected `branch:`, added closure note

## Codebase Knowledge

### FileFailure NamedTuple — placement and usage pattern

`FileFailure` is defined at `containment.py:293` immediately above `CleanStaleResult` (which uses it). It's a `NamedTuple` subclass, meaning it supports both named access (`.path`, `.error`) and positional access (iteration, unpacking, indexing). This dual-access property is load-bearing — `CleanStaleResult.report()` at `:351-354` iterates with `for path, error in self.failed_stat`, which works because NamedTuple supports `__iter__`.

| Access pattern | Where used | Still works? |
|---|---|---|
| `for path, error in ...` | `containment.py:351-354` (report method) | Yes — NamedTuple iterates |
| `== ()` | Multiple test assertions | Yes — comparing outer tuple |
| `.path` / `.error` | `test_containment.py:265-268, 293-298, 597-601` (NEW) | Yes — named access |
| `[0][0]` | Removed in this session | Replaced with `.path` |
| `FileFailure(path, repr)` | `containment.py:486, 499` | Yes — positional construction |

### Ticket dependency chain (post-triage)

```
T-20260330-02 (plugin shell — ROOT BLOCKER, unblocked)
  └→ T-20260330-03 (safety substrate)
       ├→ T-20260330-04 (dialogue parity)
       │    └→ T-20260330-07 (analytics reviewer)
       └→ T-20260330-05 (execution domain)
            └→ T-20260330-06 (promotion flow)
                 └→ T-20260330-07 (also blocked by -06)
```

All 6 tickets are codex-collaboration supersession work. T-20260330-02 is the critical path — nothing else in the chain can start until it ships the plugin shell.

### Post-triage backlog state

| Status | Count | Tickets |
|--------|-------|---------|
| open | 7 | T-20260330-02 through -07, T-20260410-01 |
| deferred | 1 | T-20260410-02 |
| done | 2 | T-20260410-03, T-20260410-04 |
| closed | 2 | T-20260327-01, T-20260330-01 |
| complete | 1 | T-010 |
| resolved | 1 | T-20260319-01 |
| wontfix | 1 | T-20260403-01 |

### Files read this session

| File | Why | Key findings |
|---|---|---|
| Prior handoff (archived) | Session load | 4 next-action items; S-1 identified as highest-leverage deferred suggestion |
| `containment.py:290-360, 400-500` | Map S-1 refactor scope | `CleanStaleResult` fields, `clean_stale_files` append sites, `report()` iteration pattern |
| `test_containment.py:260-300, 488-560, 590-610` | Map test touchpoints | 3 constructor sites, 2 positional unpacks, 2 index accesses |
| `test_clean_stale_shakedown.py:140-170` | Map stub constructor | 1 inline tuple literal in `_stub_clean_stale_files` |
| All 15 ticket files (frontmatter only) | Triage | Status distribution, dependency chains, staleness signals |
| `2026-03-30-codex-collaboration-plugin-shell-*.md` (full) | Assess staleness | Plugin shell scope, supersession context |
| `2026-03-27-r1-carry-forward-debt.md` (full) | Assess staleness | 7 items, 5 parked, 2 resolved, trigger conditions |
| `2026-04-03-t7-*.md` (full) | Assess staleness | Benchmark-only scope, ADR reference |
| `2026-04-10-T-20260410-02-*.md` (full) | Assess actionability | Concrete acceptance criteria, fresh, high-priority |
| `2026-04-10-T-20260410-04-*.md` (full) | Assess completion | All 4 acceptance criteria already met by PR #104 |
| `clean_stale_shakedown.py` (grep only) | Verify T-04 criteria | Import shim, main(), error format all present |
| `containment_lifecycle.py`, `containment_smoke_setup.py` (grep only) | Verify sibling patterns | Same import shim confirmed |

## Context

### Branch and repository state

- **Branch:** `main` (returned from feature branch after merge)
- **HEAD commit:** `7f7cbfc6` (triage ticket closures)
- **Origin:** in sync at `7f7cbfc6`
- **Working tree:** clean
- **No feature branches:** `fix/t03-stale-cleanup-observability` deleted locally and remotely

### Test baseline

- **546 tests passing** (verified before S-1 commit push)
- Ruff clean on all 3 modified files
- Full suite not re-run after merge to `main` (code is identical; merge was fast-forward equivalent via GitHub)

### Mental model

**Session framing:** "Closing loops and clearing the board." Three distinct activities — finishing deferred work (S-1), landing merged work (PR/ticket), and surveying what's next (triage) — each with its own completion criteria but all serving the same purpose: leaving the project in a clean, well-understood state for the next implementation session.

**Triage framing:** Tickets evaluated against *actionability*, not importance. An open ticket should represent work someone could pick up now. Umbrella tickets, fulfilled tickets, and tickets for discontinued programs fail this test regardless of their original priority.

### Environment state

- macOS Darwin 25.3.0
- Python 3.14.2
- `uv` for all Python tool invocations
- Working directory: `/Users/jp/Projects/active/claude-code-tool-dev`

## Learnings

### NamedTuple is the right choice when refactoring positional tuples in typed code

**Mechanism:** `NamedTuple` is a tuple subclass, so it supports iteration, unpacking, indexing, and comparison — all the patterns that existing code uses on bare tuples. A `@dataclass(frozen=True)` would break iteration and comparison patterns. This makes NamedTuple the zero-breaking-change path for upgrading bare tuples to named fields.

**Evidence:** S-1 refactor changed types and construction sites but required zero changes to `report()` iteration or `== ()` emptiness checks. All 546 tests passed unchanged on the first run.

**Implication:** When encountering `tuple[tuple[X, Y], ...]` patterns in this codebase (or similar), prefer `NamedTuple` for the upgrade path. Reserve `@dataclass` for cases where tuple compatibility is not needed.

**Watch for:** NamedTuple's iteration order is implicit contract. Adding fields requires appending (not inserting) to preserve existing unpacking patterns.

### Ticket triage ROI: stale tickets are noise multipliers

**Mechanism:** 3 of 11 active tickets were closable without any code changes — one from a discontinued program, one umbrella that had served its purpose, one already fulfilled by adjacent work. Each open ticket adds cognitive load when scanning the backlog, and stale tickets make the real priorities harder to see.

**Evidence:** Post-triage backlog went from 11 active to 8 active. The 3 closures were unambiguous once examined — the question was not "should we close these?" but "why haven't we closed these already?"

**Implication:** Run ticket triage periodically, especially after major work completes. The best time is when the last task closes and before the next task opens — exactly what this session did.

**Watch for:** The temptation to keep umbrella/parking-lot tickets open "just in case." The user's principle is clear: if it's not actionable, close it and file new tickets when the parked items' triggers fire.

### `git stash && rebase && stash pop` can leave edits as unstaged changes

**Mechanism:** When stashing before a rebase that changes the base commit, `git stash pop` re-applies the stashed changes as working-tree modifications. But the rebased commit itself doesn't include the stashed edits — they're applied on top of the new base as unstaged changes, not incorporated into the rebased commit.

**Evidence:** This session's ticket status update was committed on local `main`, then stashed before rebase onto `origin/main` (which now included the merge commit). After rebase + stash pop, the ticket edits were unstaged working-tree changes. The first push sent the rebased commit without the ticket update, requiring a second commit.

**Implication:** After `stash pop` following a rebase, always check `git status` to verify whether stashed changes need a new commit. Don't assume the rebase incorporated them.

**Watch for:** This is most likely to bite when local `main` has commits that `origin/main` doesn't (e.g., ticket updates made while a PR merge is pending on GitHub).

### `CLAUDE_PLUGIN_ROOT` may not be set in all sessions

**Mechanism:** The ticket plugin's `ticket_engine_guard.py` hook blocks direct invocation of ticket scripts when `CLAUDE_PLUGIN_ROOT` is not set. The guard checks whether the command matches a recognized pattern; without the env var, the invocation pattern doesn't match.

**Evidence:** `echo $CLAUDE_PLUGIN_ROOT` returned empty in this session. The `python3 .../ticket_triage.py dashboard` command was blocked by the hook with "Command invokes unrecognized ticket script."

**Implication:** When the triage scripts are blocked, fall back to manual triage by reading ticket frontmatter directly. The plugin scripts provide aggregate data (counts, staleness, audit trails) that manual triage can approximate but not replicate.

**Watch for:** This may affect other plugin scripts that rely on `CLAUDE_PLUGIN_ROOT`. If the env var is consistently unset, investigate the plugin's session-start hook or registration.

## Next Steps

### 1. Pick up T-20260410-02: Harden dialogue first-turn fast path

**Dependencies:** None — unblocked, no prerequisite work.

**What to read first:**
- `docs/tickets/2026-04-10-T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove.md` — full ticket with acceptance criteria
- `packages/plugins/codex-collaboration/server/dialogue.py` — the `DialogueController._next_turn_sequence` method
- `packages/plugins/codex-collaboration/tests/test_dialogue.py` — existing test coverage

**Approach suggestion:** This is a hardening ticket, not a feature. The pattern matches T-03: read the current code, identify the fragility (first-turn fast path trusts empty TurnStore as proof of no completed turns), write regression tests that expose the gap, then harden the predicate. Medium effort — likely 1-2 sessions.

**Acceptance criteria (from ticket):**
- Empty TurnStore no longer treated as sufficient proof of zero completed turns under corruption/ambiguity
- Regression test: turn 1 succeeds without calling read_thread on healthy path
- Regression test: turn 1 read_thread failure not masked by fast path
- Regression test: partial/gapped turn metadata handled
- Error messages include enough context to distinguish local vs remote failures

**Potential obstacles:** The ticket's `branch:` field is stale (`feature/b4-agent-skill-harness-assembly`). Create a new branch like `fix/t02-dialogue-first-turn-hardening` from `main`.

### 2. (Alternative) Pick up T-20260330-02: Plugin shell and consult parity

**Dependencies:** None — unblocked, root of the supersession chain.

**What to read first:**
- `docs/tickets/2026-03-30-codex-collaboration-plugin-shell-and-consult-parity.md` — full ticket
- `packages/plugins/codex-collaboration/` — current package structure
- Any supersession delivery spec referenced in the ticket

**Approach suggestion:** This is the critical path for the codex-collaboration supersession. Larger scope than T-02 — involves creating plugin.json, .mcp.json, bootstrap entry point, and user-facing skills. Likely 3+ sessions. Consider starting with a planning session to scope the work before implementation.

**Acceptance criteria:** Not specified in ticket detail — need to read the ticket body and referenced delivery spec.

**Potential obstacles:** The supersession plan may need updating given D-prime's completion and the shim being kept. The strategic context has evolved since these tickets were filed.

### 3. (Deferred) Investigate CLAUDE_PLUGIN_ROOT not being set

**Dependencies:** None — independent investigation.

**What to read first:** Ticket plugin's session-start hook, plugin registration in `.mcp.json` or similar.

**Approach suggestion:** Read-only investigation. Check whether `CLAUDE_PLUGIN_ROOT` is expected to be set by the plugin framework or by a session-start hook. If it's a configuration issue, fix it; if it's a known limitation, document it.

**Acceptance criteria:** Either the env var is reliably set in future sessions, or the limitation is documented and the triage scripts have a fallback.

## In Progress

**Clean stopping point — all work complete, no work in flight.**

- S-1 refactor committed, pushed, merged (via PR #104)
- PR #104 merged by user via GitHub UI
- Ticket T-20260410-03 closed as `done`
- 3 stale tickets closed during triage
- Ticket triage results committed and pushed
- Local repo on `main`, clean working tree, synced with origin
- Next-work recommendation produced (T-20260410-02 or T-20260330-02)

## Open Questions

### 1. Should T-20260410-02 or T-20260330-02 be the next work item?

**Context:** Both are unblocked, both are high-priority. T-02 is smaller (medium effort, hardening work, 1-2 sessions). T-20260330-02 is the critical path for the supersession (medium-to-large effort, 3+ sessions, unblocks 5 other tickets).

**Trade-off:** T-02 is a quick win with clear acceptance criteria and familiar patterns (same hardening arc as T-03). T-20260330-02 has higher strategic leverage (unblocks the entire supersession chain) but higher risk (larger scope, older ticket, may need planning update).

**Bias:** T-02 first — it's self-contained, builds momentum, and the user may want to batch the supersession work into a dedicated planning+execution arc rather than starting it ad hoc.

### 2. Are the remaining 4 deferred suggestions (S-2, S-4, S-5, S-7) worth pursuing?

**Context:** The handoff only named S-1, S-3, and S-6. S-1 is done. S-3 and S-6 are low-leverage. S-2/S-4/S-5/S-7 were described only as "deferrable hygiene items" and their specific content was lost with the review agent outputs.

**Options:** (a) Reconstruct by re-running review agents, (b) ignore — the highest-leverage item is done, (c) scan the code for obvious remaining improvements.

**Bias:** (b) — the highest-leverage item is done, and the PR is merged. Any remaining improvements can come from future reviews, not by re-running old ones.

## Risks

### 1. Parked R1 debt items may be forgotten

**Impact:** Closing T-20260327-01 removed the only tracking artifact for items 1-5 (bootstrap assertions, process orphan cleanup, concurrent safety, AuditEvent schema, policy fingerprint). If their trigger conditions fire and nobody files new tickets, the debt persists untracked.

**Mitigation:** The closed ticket body preserves all 7 items with their classifications and trigger conditions. The closure note explicitly says "re-enter scope via new targeted tickets when triggers fire." The risk is someone starting R2/delegation work without checking the closed ticket.

### 2. March 30 supersession tickets may need plan updates

**Impact:** The 6 codex-collaboration tickets were filed 13 days ago, before D-prime completed. The strategic landscape has shifted (shim kept, D-prime stable). The tickets' acceptance criteria and proposed approaches may need updating to reflect current reality.

**Mitigation:** The first session on T-20260330-02 should include a plan review/update step before implementation. The user confirmed the direction is correct; only the specifics may need adjustment.

## References

**Commits this session:**
- `3d81c719` — refactor(containment): replace failure tuples with FileFailure NamedTuple
- `ce720ada` — chore(ticket): close T-20260410-03 after PR #104 merge
- `7f7cbfc6` — chore(tickets): triage — close 3 resolved/obsolete tickets

**PR:**
- PR #104: https://github.com/jpsweeney97/claude-code-tool-dev/pull/104 (merged)

**Handoffs:**
- Prior: `docs/handoffs/archive/2026-04-11_21-53_pr-104-race-fix-smoke-setup-parity-marked-ready.md`
- This: `docs/handoffs/2026-04-12_00-52_s1-refactor-pr-merge-ticket-triage.md`

**Tickets closed:**
- T-20260410-03: done (PR #104 merged)
- T-20260410-04: done (acceptance criteria met by PR #104)
- T-20260403-01: wontfix (benchmark discontinued)
- T-20260327-01: closed (umbrella triage complete)

**Tickets confirmed active:**
- T-20260330-02 through -07 (codex-collaboration supersession chain)
- T-20260410-01 (dialogue turn semantics)
- T-20260410-02 (dialogue first-turn hardening)

**Memory updated:**
- `project_codex_collaboration_successor.md` — codex-collaboration confirmed as intended successor

## Conversation Highlights

### User's terse approval style (consistent with prior sessions)

The user's responses during the triage walk-through were substantive but decisive. Each keep/close decision came with detailed reasoning, often 100+ words, but always ending with an unambiguous directive:

> "Close it." (T-20260403-01)
> "Close it, with **option (b)**." (T-20260327-01)
> "Keep it open." (T-20260410-01, T-20260410-02)
> "Close it as `done`." (T-20260410-04)

The reasoning was thorough but the directive was never hedged.

### User's actionability principle for tickets

The user's reasoning for closing T-20260327-01 captured a clear principle:

> "this is no longer an actionable ticket. An open ticket should represent work someone could pick up now. T-20260327-01 does not: two items are already resolved, and the remaining five are explicitly parked behind future trigger conditions."

This principle was applied consistently across all triage decisions. Umbrella tickets, parking-lot tickets, and tickets for discontinued programs all fail the actionability test regardless of priority.

### User's post-merge cleanup

After merging PR #104 via GitHub UI, the user followed up with specific cleanup instructions:

> "Please **push `main`** so the ticket-status update lands on `origin/main`."

Then after verification:

> "After that, re-check with: `git status --short --branch` and `git log --oneline --decorate -n 5`"

The user specifies both the action and the verification step. This pattern — action + explicit read-back — is consistent with the verification-leg principle from the T-03 sessions.

### Strategic confirmation on codex-collaboration

When asked whether codex-collaboration is still the intended successor, the user's response was a single sentence:

> "codex-collaboration is still the intended successor to the current cross-model plugin"

No qualification, no conditions. This is the same decisiveness pattern seen in prior sessions — when the user has already decided, the directive is direct.

## User Preferences

**Ticket actionability principle (new this session):**
> "An open ticket should represent work someone could pick up now."
- Umbrella/parking-lot tickets should be closed when all items are resolved or parked
- Parked items re-enter scope via new targeted tickets, not by keeping the umbrella open
- **Implication:** Don't keep tickets open "just in case" — close them and trust the trigger conditions

**Verification after shared-state actions (confirmed):**
User specified explicit verification commands after requesting push: `git status --short --branch` and `git log --oneline --decorate -n 5`. This is the same read-back pattern from prior T-03 sessions — the user expects empirical verification, not just "it worked."

**Structured triage walk-through (new this session):**
When asked to triage tickets, the user said *"One at a time"* — each ticket gets its own presentation, assessment, and decision before moving to the next. The user provided detailed reasoning for each decision (100+ words), suggesting they value the deliberation process even when the decision is clear-cut.

**Decisiveness on previously-discussed items (confirmed):**
When confirming codex-collaboration as successor: one sentence, no hedging. Same pattern as prior sessions' *"Push + mark ready"* and *"We should fix containment_smoke_setup.py"*.

## Gotchas

### `git stash && rebase && stash pop` splits committed and working-tree state

**Symptom:** After `git stash && git rebase origin/main && git stash pop`, committed changes from before the stash are in the rebased commit, but the stashed working-tree edits are re-applied as unstaged modifications. If the stashed edits were the *only* changes being tracked, the rebased commit may be empty or stale.

**Root cause:** `git stash pop` applies changes to the working tree, not to the latest commit. The rebase replays the original commit (before stashing); the stash pop adds the edits on top. These are two separate states — committed (rebased) and uncommitted (stash-popped).

**Mitigation:** After `stash pop` following a rebase, always run `git status` and `git diff` to verify. If stashed edits need to be committed, create a new commit — don't assume the rebase incorporated them.

**Discovered when:** This session's ticket status update was stashed across a rebase and re-appeared as unstaged changes, requiring a second commit.

### `CLAUDE_PLUGIN_ROOT` may be unset, blocking plugin scripts

**Symptom:** Direct invocation of ticket plugin scripts via `python3 <path>/scripts/ticket_triage.py` is blocked by the `ticket_engine_guard.py` PreToolUse hook with "Command invokes unrecognized ticket script."

**Root cause:** `CLAUDE_PLUGIN_ROOT` is not set in all sessions. The guard hook checks whether the command matches a recognized pattern; without the env var, the pattern match fails.

**Mitigation:** Fall back to manual triage by reading ticket files directly. The plugin scripts provide aggregate data that manual triage approximates but cannot fully replicate.

**Discovered when:** Attempted to run `ticket_triage.py dashboard` and `audit` during the triage phase of this session.
