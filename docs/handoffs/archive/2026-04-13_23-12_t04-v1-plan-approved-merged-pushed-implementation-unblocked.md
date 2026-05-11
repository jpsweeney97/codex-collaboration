---
date: 2026-04-13
time: "23:12"
created_at: "2026-04-14T03:12:09Z"
session_id: 72e0c2e6-5365-45da-88d9-d10dc55c9c8e
resumed_from: docs/handoffs/archive/2026-04-13_22-09_t04-v1-plan-rewritten-after-three-scrutiny-rounds.md
project: claude-code-tool-dev
branch: main
commit: 73f8c9c1
title: "T-04 v1 plan approved, merged, pushed — implementation unblocked"
type: handoff
files:
  - docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md
---

# T-04 v1 Plan Approved, Merged, Pushed — Implementation Unblocked

## Goal

Resume from the 22:09 handoff where the rewritten v1 scoping plan was
handed off for review-as-is. Absorb the user's review pass, apply
warranted corrections, then commit/merge/push as the approved
implementation baseline for T-04 v1.

**Trigger.** User's handoff request from the prior session explicitly
framed this session as "I will review the plan as-is and then share my
feedback" — the third appearance of the review-as-is pattern in the
T-04 program. The plan was uncommitted at 591 lines on
`feature/t04-v1-scoping-plan` from `main@72c66714`.

**Stakes.** This is the last remaining gate before T-04 v1
implementation can begin. Every downstream implementation session pulls
its frame from this plan. Getting the plan into a merged, approved
state on `main` converts the three-round scrutiny work into a durable
baseline — which was the entire purpose of the prior session's
re-minimization arc.

**Success criteria for this session:**

1. User review returns with either clean-pass or tractable
   corrections — **achieved on the first pass** (four findings, all
   tractable doc-level corrections, no architectural reopens).
2. Corrections verified against code with file:line evidence, accepted
   or pushed back with reasoning — **achieved** (3 full-accepts, 1
   partial pushback that user validated).
3. Plan edits applied without reopening any of the seven settled
   decisions — **achieved** (11 parallel edits, +40 lines net).
4. Second review pass clean — **achieved.**
5. Status flipped to Approved; plan committed, merged to main, pushed
   to origin — **achieved.**

**Bigger picture.** This closes the scoping packet of the T-04
supersession chain. Packet sequence across three sessions: draft → rewrite
after three adversarial rounds → approve + land. v1 implementation
(§12 of the merged plan) is now unblocked and sequenced in order from
reference-doc extraction through the 14-item rubric inspection.

## Session Narrative

**Phase 1 — Load and plan read (~10 min).**

Loaded the prior handoff via `/handoff:load`. Per explicit directive in
the handoff (and precedent from the prior two sessions), read the plan
in full before the user shared feedback. 592 lines, 13 sections. Noted
the load-bearing concentration in §4 (ownership) and §6.1 (run-model
table) — those sections encode transport reality and every other
section cites down to them. Explicit acknowledgement that plan had been
read end-to-end before feedback was shared.

**Phase 2 — User feedback absorbed (~5 min).**

User returned with structured feedback:
- Two P1 prefix-tagged code-comments.
- One P2 prefix-tagged code-comment.
- Three findings (1 High, 1 High, 1 Medium) with file:line citations.
- One Open Question on the `plugin.json` manifest row.
- Positive acknowledgement that the rewrite was "materially better than
  the prior draft on the major architectural points."
- Explicit ask: "Let me know if you would push back on any of it."

**Phase 3 — Evidence verification (~10 min).**

Verified each finding against code in parallel:

1. `clean_stale_shakedown.py` exists; `shakedown-b1/SKILL.md:35-45`
   runs it explicitly before the single-active-run check at step 5;
   `containment_lifecycle.py:73` runs cleanup INSIDE
   `_handle_subagent_start` (post-spawn, unreachable from parent fail-
   fast). Finding 1 confirmed.
2. `test_bootstrap.py:256` asserts no user-invocable skill's
   `allowed-tools` includes dialogue MCP tools. The plan's `/dialogue`
   skill architecturally doesn't need those tools (orchestrator owns
   the `codex.dialogue.*` calls; skill only dispatches via `Agent`).
   Mechanically, the test passes. But the test's class docstring ties
   the boundary to T-20260330-02 — intent needs explicit reconsideration
   for v1.
3. `dialogue-codex/SKILL.md:111-120` excludes `minimum_fallback` from
   emitted `claims` and from `counters`; line 120 states
   "transcript-indistinguishable from an omitted fallback ... verified
   by source review, not transcript inspection." Lines 272 and 336-353
   confirm: no `scope_breach_count` counter, no scope-breach field in
   the epilogue schema. Grep: `scope_breach` has zero matches in the
   skill. Finding 3 confirmed.
4. `.claude-plugin/plugin.json` is pure metadata (name, version,
   description, author, license, keywords). No skill/agent
   declarations. Confirms the open question — skills auto-discover.

Additional discovery during verification: T1 contract at
`2026-04-02-t04-t1-structured-termination-contract.md:59` defines
`termination_code` as lowercase string literals
(`"convergence" | "budget_exhausted" | "scope_breach" | "error"`). The
plan's §6.3 used `SCOPE_BREACH` (uppercase enum-constant style) — a
naming drift that my edits would need to correct in passing. Also:
`termination_code` is NOT in the current `dialogue-codex` transcript
emission (grep returned zero hits); the transcript carries only
`converged: bool` in the epilogue, projected from termination_code.

**Phase 4 — Response with partial pushback (~10 min).**

Delivered a finding-by-finding response:
- Finding 1 (stale cleanup): full accept. Evidence cited.
- Finding 2 (bootstrap gate): partial pushback. Showed that the test
  mechanically passes because the `/dialogue` skill's `allowed-tools`
  doesn't need dialogue MCP tools per §4 ownership. But agreed the
  higher-level point (plan should explicitly name the boundary) holds —
  because the test's class-level intent is scope-bound to T-20260330-02.
  Proposed fix: add a boundary-invariant bullet in §8.4 naming the
  constraint precisely.
- Finding 3 (transcript overclaim): full accept. Named the internal
  contradiction explicitly (§3.3 freezes shape; §3.2 and §8.3 claim
  fields that aren't in the frozen shape). Proposed downgrade to
  prose-evidence framing + naming-drift correction to lowercase enum.
- Open Question (plugin.json): full accept. Proposed drop the row and
  replace with the bootstrap-boundary invariant.

Also surfaced an insight: Findings 2 and 4 were linked — the plan's
"plugin wiring" row was a placeholder covering the wrong thing. The
real repo-level gate for this surface was the bootstrap test, not a
manifest declaration. Presented as combined fix.

**Phase 5 — User pinpoint guidance (~2 min).**

User returned precise direction, distinguishing "doc corrections" from
"architectural debates":

> "I would not reopen Findings 1, 3, or the manifest row. Those are
> straight doc corrections, not architectural debates. I would only
> surface the Finding 2 nuance, and even that does not need a separate
> discussion thread unless you want to change the bootstrap test itself."

Explicit instructions:
- Apply stale-cleanup fix directly.
- Apply transcript/prose-evidence fix directly.
- Drop the bogus `plugin.json` row directly.
- Rewrite Finding 2 in the plan as a boundary invariant, not a repo-gate
  blocker.
- User's stronger earlier claim ("`/dialogue` will fail the existing
  repo gate") withdrawn in favor of my narrower mechanical framing.
- Optional later ticket: rename/reword the bootstrap test to match
  its actual assertion.

**Phase 6 — Parallel edits applied (~5 min).**

Applied 11 Edit tool calls in parallel against the plan:

1. §4 ownership row for `/dialogue` — added "preflight stale-state
   cleanup" and `scripts/clean_stale_shakedown.py` dependency; reordered
   to match execution order (cleanup → live-run check → seed write).
2. §6.1 step 1 — added the preflight sweep invocation with rationale
   explaining why parent-side cleanup is load-bearing (post-spawn
   `_handle_subagent_start` is unreachable from parent fail-fast).
3. §3.2 telemetry paragraph — rewrote to distinguish transcript-present
   fields (per-turn `effective_delta`, reconstructable Risk-J evidence)
   from orchestrator-internal state (`minimum_fallback` accounting,
   scope-breach counts) that appears in neither artifact.
4. §3.3 — appended "Explicitly NOT in the transcript" paragraph
   capturing the no-new-fields commitment with file:line citation.
5. §6.3 scope-breach bullet — corrected `SCOPE_BREACH` →
   `"scope_breach"` (T1 enum), clarified count is orchestrator-internal.
6. §8.3 scope-breach check row — rewrote evidence path from
   structured-counter to orchestrator-logs + termination_code +
   ledger_summary prose.
7. §7.1 — dropped the bogus `plugin.json` manifest row.
8. §8.4 — added bootstrap-boundary invariant bullet naming the
   `allowed-tools` constraint and the test's mechanical compatibility.
9. §9.4 mitigation — updated to reference the preflight sweep.
10. §11 — added a checkbox for preflight cleanup.
11. §11 — added a checkbox for bootstrap-boundary invariant.

Verified via grep: zero `SCOPE_BREACH` uppercase matches remain; one
`scope_breach_count` remains (inside the explicit "NOT in the
transcript" clarification — correct context); zero `plugin manifest` /
`Declare the new skill` matches. Line count 592 → 632 (+40,
proportional to added substance).

**Phase 7 — Clean-pass review (~3 min).**

User returned: "No findings on the revised plan. This pass came back
clean." Validated three substantive points:
- Stale-cleanup gap covered in the run model.
- Transcript contract no longer overclaims fields the frozen
  `dialogue-codex` emission cannot carry.
- `/dialogue` bootstrap boundary stated mechanically correctly: skill
  stays free of `codex.dialogue.*`; orchestrator owns the calls.

Residual-risk framing from user was implementation-level (not plan-
level): keep future `/dialogue` `allowed-tools` aligned with the
bootstrap test, keep scope-breach evidence prose-only, keep
`dialogue-codex` byte-for-byte untouched. User suggested commit as the
approved baseline.

**Phase 8 — Commit ceremony (~3 min).**

Surfaced the frontmatter `status: Draft` field (was overlooked during
edits) — user chose "flip status to Approved and commit." Applied:

1. Edited frontmatter: `status: Draft` → `status: Approved`.
2. Pre-commit inspection: `git status` showed single untracked file;
   `git branch --show-current` confirmed `feature/t04-v1-scoping-plan`;
   recent log showed conventional-commits style (`type(scope): desc`).
3. Committed with HEREDOC message following repo convention:
   `docs(plan): add approved T-04 v1 production dialogue scoping plan`.
   Body captured re-minimization rationale. Co-Authored-By trailer.
4. Commit landed as `73f8c9c1`; one file changed, 632 insertions.

**Phase 9 — Merge and push (~2 min).**

User invoked `/merge-branch` with `feature/t04-v1-scoping-plan` →
`main`. Fast-forward merge (no merge commit, no divergence). Feature
branch deleted with safe `-d`. Local `main` now at `73f8c9c1`; origin
still at `72c66714`.

User then said "push main to origin." Pushed:
`72c66714..73f8c9c1  main -> main` — remote accepted the fast-forward
without branch-protection pushback (per `.claude/rules/workflow/git.md`,
protection blocks local edits on `main` via a PreToolUse hook on
`Edit`/`Write`, not pushes to the remote).

Implementation is now unblocked end-to-end.

## Decisions

### Decision 1: Partial pushback on Finding 2, not full accept

**Choice:** Accept the substance of Finding 2 (plan should name the
bootstrap boundary) but push back on the stronger framing ("`/dialogue`
will fail the existing repo gate"). Proposed concrete fix as a boundary
invariant in §8.4, not a repo-gate blocker in §7.1.

**Driver:** Mechanical verification at `test_bootstrap.py:263-283`
showed the test body iterates `user-invocable` skills and asserts
`allowed & _DIALOGUE_MCP_TOOLS == ∅`. It fails only if `allowed-tools`
includes dialogue MCP tools. The plan's §4 ownership row for `/dialogue`
lists only "Invocation parsing ... orchestrator dispatch ...
production synthesis surfacing" — none of which require
`codex.dialogue.*` tools (dispatch uses `Agent`; orchestrator agent
owns the Codex calls). Mechanically, the test passes unchanged.

**Alternatives considered:**

- **Full accept.** Would have conceded a mechanically incorrect claim.
  Rejected — the handoff's memory rule ("verify architectural claims
  against current code with file:line evidence") applies in both
  directions: pushback requires evidence, but so does acceptance.
- **Full pushback.** Would have missed the higher-level correct point.
  Rejected — the test's class docstring ties the boundary to
  T-20260330-02 (consult parity), and the test name
  `test_no_user_invocable_dialogue_skill_exists` reads broader than
  its body asserts. The plan should name this boundary regardless of
  mechanical pass/fail.

**Implication:** Set precedent for how to handle reviewer claims that
are partially correct: surface the mechanical situation, retain the
valid substance, drop the inaccurate framing. User validated the
approach directly ("Replace it with the invariant you identified").

**Trade-offs accepted:** Slightly longer response. Risked being read as
nitpicking. Validated when user said "Drop my earlier stronger claim
that `/dialogue` necessarily breaks the existing test" — user rewrote
their own framing based on the evidence.

**Confidence:** High (E2) — verified the test body AND the test's class
docstring AND the `/dialogue` skill's ownership row. Triangulated.

**Reversibility:** High — a later implementation session can add
`codex.dialogue.*` to `allowed-tools` if truly needed, but then the
test breaks and the boundary must be explicitly reconsidered.

**Change trigger:** If `/dialogue` skill architecture changes such that
the skill needs direct dialogue-tool access (e.g., if we decide the
skill rather than the orchestrator owns the Codex calls — unlikely
per §4 invariants), this pushback would need revisiting.

### Decision 2: Apply all edits directly rather than draft first

**Choice:** Apply the 11 plan edits as parallel `Edit` tool calls,
without first producing a side-by-side diff or marked-up draft for
user pre-approval.

**Driver:** User said "Apply the stale-cleanup fix directly. Apply the
transcript/prose-evidence fix directly. Drop the bogus plugin.json row
directly. Rewrite Finding 2 in the plan as a boundary invariant."
Four consecutive "directly"s. Explicit license.

**Alternatives considered:**

- **Draft first, review, then apply.** Would have been the default
  when uncertain, but user's phrasing foreclosed that option.
- **Single sequential edits.** Slower; no benefit over parallel for
  non-overlapping edits.

**Implication:** Session shape shifted from drafting-plus-review to
verification-plus-application. Enabled a clean-pass review in the
next turn rather than an extended back-and-forth.

**Trade-offs accepted:** Small risk of misinterpreting an edit
direction. Mitigated by grep verification post-edit.

**Confidence:** High (E2) — user's direction was unambiguous;
verification grep confirmed all edits landed.

**Reversibility:** Trivial — each Edit is a doc change; any
misinterpretation gets caught in review.

**Change trigger:** N/A for this decision (session-specific).

### Decision 3: Flip status Draft → Approved before committing

**Choice:** Edit frontmatter `status: Draft` → `status: Approved`
before the commit, making the "approved baseline" claim explicit in
the machine-readable metadata rather than only in git history.

**Driver:** I surfaced this as a small thing worth handling before
commit. User chose "flip status to Approved and commit." Explicit.

**Alternatives considered:**

- **Commit as Draft, flip status in a follow-up commit.** Would have
  produced a two-commit sequence where the first commit's metadata
  didn't match its landing context. Rejected.
- **Leave status: Draft.** Would have left downstream tooling or
  future-scanners keying on `status:` with stale information.
  Rejected.

**Implication:** The machine-readable metadata now matches the git
history — anyone scanning for approved plans via frontmatter will find
this one.

**Trade-offs accepted:** None material — one extra Edit before commit.

**Confidence:** High (E3) — user validated directly.

**Reversibility:** Trivial.

### Decision 4: Direct merge to main, no PR

**Choice:** Merge `feature/t04-v1-scoping-plan` → `main` directly via
`/merge-branch` skill (local fast-forward), rather than opening a PR
on GitHub.

**Driver:** The prior handoff noted direct-merge is the established
project pattern for design plans ("Given this is a plan doc (not code),
direct merge is reasonable per the project's established pattern for
design plans"). User invoked `/merge-branch` directly.

**Alternatives considered:**

- **PR to main.** Standard for code changes, but the repo treats design
  plans differently. User didn't request a PR; direct merge was
  invoked explicitly.
- **Push feature branch and merge later.** Would have delayed the
  "approved baseline" claim. Rejected — implementation is intended to
  begin next session.

**Implication:** No external review gate on the plan. All review
happened in-session via three adversarial rounds plus a clean-pass.

**Trade-offs accepted:** No asynchronous review opportunity. Fine
given the intensive in-session review.

**Confidence:** High (E2) — user explicitly invoked merge-branch.

**Reversibility:** Medium — the merge can be reverted, but the commit
is on `main` now and has been pushed.

## Changes

### `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`

**What changed:** 11 parallel edits + 1 frontmatter edit. Line count
592 → 632 (+40 net, after dropping one row from §7.1).

**Edits by section:**

| § | Before | After |
|---|---|---|
| Frontmatter | `status: Draft` | `status: Approved` |
| §3.2 last paragraph | Claimed `minimum_fallback` and `scope_breach_count` live in verification transcript | Distinguishes transcript-present fields from orchestrator-internal state; scope-breach surfaces via `termination_code = "scope_breach"` + `ledger_summary` prose |
| §3.3 | Only Risk-J reconstructability paragraph | Added "Explicitly NOT in the transcript" paragraph citing `dialogue-codex/SKILL.md:111-120` |
| §4 `/dialogue` ownership row | 5 owned activities | 6 owned activities (adds preflight stale-state cleanup); adds `scripts/clean_stale_shakedown.py` to dependencies; reordered to match execution order |
| §6.1 step 1 | Generate run_id + write seed | Preflight sweep FIRST, then live-run check, then seed write; rationale explains why parent-side cleanup is load-bearing |
| §6.3 scope-breach bullet | `SCOPE_BREACH` uppercase; implied counter emission | `"scope_breach"` (T1 enum); count is orchestrator-internal only |
| §7.1 | Had bogus `plugin manifest` row | Row removed |
| §8.3 scope-breach check | Gated on `scope_breach_count` in epilogue | Gated on orchestrator logs + `termination_code = "scope_breach"` + `ledger_summary` prose |
| §8.4 | Five invariant bullets | Six invariant bullets (adds bootstrap-boundary invariant) |
| §9.4 mitigation | Generic live-run check | Preflight sweep named explicitly with 24h threshold and shakedown-b1 parallel |
| §11 acceptance | 11 checkboxes | 13 checkboxes (adds preflight cleanup + bootstrap boundary) |

**Status:** Landed. Committed as `73f8c9c1`. Merged fast-forward to
`main`. Pushed to `origin/main`.

### Branch state

| Before | After |
|---|---|
| On `feature/t04-v1-scoping-plan` from `main@72c66714` | On `main` at `73f8c9c1` |
| Plan uncommitted (untracked) | Plan tracked, committed, merged, pushed |
| Feature branch exists | Feature branch deleted (safe `-d`) |
| Origin at `72c66714` | Origin at `73f8c9c1` |

## Codebase Knowledge

### Files read this session

| File | Range | Purpose | Key finding |
|---|---|---|---|
| `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py` | existence only | Verify Finding 1 | Exists — available for `/dialogue` to invoke the same way `shakedown-b1` does |
| `packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md` | 1-120 | Verify preflight cleanup precedent | Step 4 (line 35-45) runs cleanup BEFORE step 5 (live-run check); explicit rationale: "Runs before seed creation to prevent stale containment state from a crashed prior run." |
| `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py` | 50-170 | Verify post-spawn cleanup path | `clean_stale_files(shakedown_dir(data_dir))` at line 73 is inside `_handle_subagent_start` — post-spawn only. Unreachable if parent fails fast pre-spawn. |
| `packages/plugins/codex-collaboration/tests/test_bootstrap.py` | 1-50, 230-283 | Verify Finding 2 | Test asserts `allowed & _DIALOGUE_MCP_TOOLS == ∅` for all user-invocable skills (body); docstrings tie boundary to T-20260330-02 (intent); mechanical pass possible for a dispatch-only skill |
| `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md` | 100-130, 330-360 | Verify Finding 3 | Line 111-117: `minimum_fallback` exclusion rules; line 120: "verified by source review, not transcript inspection"; lines 336-353: epilogue schema has `ledger_summary, converged, effective_delta_overall` — no `scope_breach_count` |
| `packages/plugins/codex-collaboration/.claude-plugin/plugin.json` | full file | Verify Open Question | 11 lines total. Pure metadata. No skills/agents declarations. Auto-discovery is the model. |
| `docs/plans/2026-04-02-t04-t1-structured-termination-contract.md` | grep only | Resolve `termination_code` enum drift | Line 59: values are lowercase string literals `"convergence" | "budget_exhausted" | "scope_breach" | "error"` — NOT uppercase enum constants. The plan's `SCOPE_BREACH` was drift. |

### Plugin wiring model

`.claude-plugin/plugin.json` is metadata-only (name, version, description,
author, license, keywords — 11 lines). There is no manifest-level
declaration of skills, agents, commands, or hooks. Discovery is
directory-based:

- Skills auto-discover from `skills/<name>/SKILL.md`
- Agents auto-discover from `agents/<name>.md`
- Commands auto-discover from `commands/<name>.md`
- Hook matchers are EXPLICIT in `hooks/hooks.json` (not auto-discovered)

**Implication:** The plan's original `plugin manifest` row was always
a placeholder. For v1, the only wiring-level change the repo actually
requires is `hooks.json` matcher extension (already captured in §7.1).

### Test name vs test body asymmetry

`test_bootstrap.py::test_no_user_invocable_dialogue_skill_exists`
(line 256) reads as a broad existence assertion. The body iterates
`user-invocable: true` skills and asserts:

```python
assert not allowed & _DIALOGUE_MCP_TOOLS, ...
```

— which only fails if the skill's `allowed-tools` intersects with
`codex.dialogue.*` tools. A user-invocable `/dialogue` skill whose
`allowed-tools` list is `Bash, Read, Write, Agent` (no dialogue MCP
tools) mechanically passes.

The class docstring at lines 234-240 frames the boundary as
"T-20260330-02 skill layer must not expose [dialogue tools]" — that
ticket predates v1 and the scope needs explicit reconsideration with
v1's introduction of a production dialogue surface. The plan captures
this in §8.4.

### T1 enum is lowercase string literals

`docs/plans/2026-04-02-t04-t1-structured-termination-contract.md:59`:

```
termination_code: null | "convergence" | "budget_exhausted" | "scope_breach" | "error"
```

These are **string literal values**, not enum constant names. The plan
previously wrote `SCOPE_BREACH` (uppercase) — a drift likely seeded by
the `TerminationCode` enum label in §3.2's field table, which suggests
Python-style enum constants. My §6.3 and §8.3 edits corrected this to
`"scope_breach"`.

### `termination_code` is production-synthesis-only, not in transcript

Grep for `termination_code` in `dialogue-codex/SKILL.md` returned zero
matches. The transcript emission shape (13 fields per line 252-268)
has `converged: bool` in the epilogue, which the T1 contract describes
as "projected mechanically from `termination_code`" (line 22).

**Implication:** Scope-breach evidence differs across the two
artifacts:
- Production synthesis: `termination_code = "scope_breach"` (explicit).
- Transcript: `converged: false` + `ledger_summary` prose (projected).

Plan edits to §3.2, §6.3, §8.3 made this distinction explicit.

### Preflight cleanup asymmetry (pre-spawn vs post-spawn)

The containment transport has TWO cleanup paths on the same
`shakedown/` directory:

1. **Pre-spawn, parent-side:** `clean_stale_shakedown.py` invoked by
   the user-invocable skill before its live-run check. 24h age
   threshold. `shakedown-b1/SKILL.md:35-45` is the precedent.
2. **Post-spawn, hook-side:** `clean_stale_files(shakedown_dir(...))`
   called at `containment_lifecycle.py:73` inside
   `_handle_subagent_start`. Runs AFTER `SubagentStart` fires.

If the parent fails fast (e.g., live-run check trips on a crashed prior
run), the post-spawn path is unreachable. The pre-spawn path is the
only safety net for this case. v1 plan now names this explicitly in
§6.1 step 1 and in §9.4 mitigation.

## Context

### Branch and repository state

- **Branch:** `main` at `73f8c9c1` (local and `origin` synced).
- **Feature branch:** `feature/t04-v1-scoping-plan` deleted
  (was merged fast-forward).
- **Working tree:** clean.
- **Recent commits on main:**
  - `73f8c9c1` — docs(plan): add approved T-04 v1 production dialogue scoping plan
  - `72c66714` — fix(contract): align turn semantics to model 2 and close T-20260410-01
  - `16cab95f` — chore(ticket): close T-20260410-02 dialogue first-turn hardening

### Mental model for this session

**Review pass after re-minimization.** The prior session did the hard
re-minimization work under three adversarial rounds. This session
exercised the "converged plan, exit and land" phase of the pattern:
surface feedback → verify → apply doc-level corrections → commit
baseline. The expected review-pass shape was "tractable corrections,
no architectural reopens" — which is exactly what the first pass
returned.

The partial pushback on Finding 2 was the only session moment that
could have reopened a decision. Mechanical evidence carried the day:
the correct response was surface-and-refine, not blanket-accept. User
validated by withdrawing the stronger claim and keeping the substance.

### Review-as-is pattern, third appearance

The user's review-as-is pattern is now load-bearing across the T-04
scoping program:

1. Prior-prior session (518 lines, pending review).
2. Prior session (591 lines rewrite, pending review).
3. This session (632 lines approved, now merged).

Each review pass converged more sharply than the previous (Reject →
Major → Minor → clean-pass). Worth preserving as the standard pattern
for design-doc work in this repo.

### Memory status

MEMORY.md's "Current Focus" section names Engram as the active design
work. T-04 v1 wasn't previously listed as active focus. This session
closes the T-04 scoping packet — the next live-work packet is either
T-04 v1 implementation or Engram implementation, depending on what the
user prioritizes next.

## Learnings

### "Apply directly" is a license, not a default

**Mechanism.** When a user gives specific, itemized "apply X directly"
instructions after a round of analysis, it signals they've absorbed
the evidence and want execution rather than another review cycle.
Producing a marked-up draft for re-approval at that point is friction,
not care.

**Evidence.** User said: "Apply the stale-cleanup fix directly. Apply
the transcript/prose-evidence fix directly. Drop the bogus
`plugin.json` row directly. Rewrite Finding 2 in the plan as a
boundary invariant, not as a repo-gate blocker." Four consecutive
"directly"s. I applied 11 parallel edits in one turn.

**Implication.** The session converged faster than a draft-review
cycle would have. The post-edit grep verification served the same
safety function as a pre-edit draft, with lower latency.

**Watch for:** "apply directly" applies in the specific context it was
given. Don't generalize to unrelated edits or architectural changes —
that reopens decisions without license.

### Partial pushback with evidence beats blanket accept

**Mechanism.** When a reviewer's high-level point is correct but their
specific mechanical claim is wrong, blanket-acceptance propagates the
inaccurate mechanical claim into the plan. Partial pushback preserves
the correct substance while correcting the inaccurate framing.

**Evidence.** Finding 2 claimed "`/dialogue` will fail the existing
repo gate." Mechanical verification at `test_bootstrap.py:263-283`
showed the test body only fails if `allowed-tools` intersects dialogue
MCP tools — which the plan's `/dialogue` skill architecturally doesn't
need. Substance ("plan should name the boundary") was correct;
mechanical framing ("will fail the gate") was incorrect. User
responded: "Drop my earlier stronger claim ... Replace it with the
invariant you identified."

**Implication.** Reviewers rewriting their own framing based on
evidence is a validation signal. Trust the pattern; deliver partial
pushback with evidence when warranted.

**Watch for:** Partial pushback must be evidence-backed. If the
mechanical claim is merely "I don't think so," that's not pushback —
that's resistance. File:line + quoted test body + counter-example is
the minimum bar.

### Plugin manifest is metadata-only; boundaries live in tests

**Mechanism.** `.claude-plugin/plugin.json` carries no wiring for
skills, agents, or commands — all discovery is directory-based. Any
"add skill X to manifest" language is a misconception. The real
boundary enforcement lives in hooks (`hooks.json` matchers) and tests
(`test_bootstrap.py::test_no_user_invocable_dialogue_skill_exists`).

**Evidence.** `plugin.json` full content (11 lines) contains only
name, version, description, author, license, keywords. Zero skill or
agent references. Conversely, `test_bootstrap.py:256` is the only
repo-level gate that could meaningfully block or validate the
`/dialogue` surface's boundary.

**Implication.** For v1 and any future plugin work in this repo,
"wiring" means (a) hooks.json matchers, (b) tests that encode
boundaries. It does NOT mean `plugin.json` edits.

**Watch for:** If a plan has a "plugin manifest" entry, check whether
it's actually specifying a hook matcher or a boundary test — or
whether it's a placeholder that doesn't map to any real surface.

### Enum naming drift propagates via type labels

**Mechanism.** The plan's §3.2 field table says
`"One of the `TerminationCode` enum values"`. That label reads as
Python-style enum constants (uppercase). But T1 defines the values as
lowercase string literals. The mismatch let `SCOPE_BREACH` (wrong) drift
into §6.3.

**Evidence.** T1 line 59: `termination_code: null | "convergence" |
"budget_exhausted" | "scope_breach" | "error"`. My §6.3 edit corrected
the drift in passing.

**Implication.** When a type label and the literal values disagree in
surface form, the literal values are canonical. Future plans using T1
should quote the lowercase literal, not mimic the `TerminationCode`
label.

**Watch for:** This specific drift is likely fixed in the current
plan, but future additions citing T1 should use lowercase.
Consider: a post-v1 cleanup that renames the `TerminationCode` type
label itself to match (e.g., `termination_code_value: Literal[...]`)
would eliminate the drift vector entirely.

### Test name rot: assertion-narrowing without renaming

**Mechanism.** `test_no_user_invocable_dialogue_skill_exists` reads as
a broad existence assertion but the body only checks `allowed-tools`
intersection. If the test was renamed/narrowed at some point (or if
the original intent was narrower than the name), future readers can
easily misread the test's scope and block legitimate changes that
mechanically satisfy the assertion.

**Evidence.** Finding 2 initially claimed "`/dialogue` will fail the
existing repo gate." Reading only the test name made this sound
correct. Reading the body made it incorrect. Class docstring ties the
boundary to T-20260330-02, which pre-dates v1.

**Implication.** Optional post-v1 cleanup: rename the test (or its
class) to match its actual assertion — e.g.,
`test_user_invocable_skills_do_not_allow_dialogue_tools`. Not blocking
for v1 per the plan's §8.4 note.

**Watch for:** This pattern probably exists elsewhere in the repo.
Worth a sweep when there's bandwidth: any test whose name describes a
broader assertion than its body asserts.

## Next Steps

### 1. Begin T-04 v1 implementation per plan §12

**Dependencies:** None — plan approved, merged, pushed. Baseline is
`main@73f8c9c1`.

**What to read first:**
1. `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`
   (the merged plan, §12 implementation order).
2. `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md`
   (source for the reference-doc extraction, step 1 of §12).
3. This handoff for session context.

**Implementation order from §12:**

1. Author the production-local turn-semantics reference doc by
   extracting per-turn contract content from the current
   `dialogue-codex` skill. Target:
   `packages/plugins/codex-collaboration/references/dialogue-turn-contract.md`.
2. Author `dialogue-orchestrator` agent body citing the reference doc,
   with inline initial scouting phase and production synthesis
   emission. Target:
   `packages/plugins/codex-collaboration/agents/dialogue-orchestrator.md`.
3. Author `/dialogue` user skill with invocation parsing, preflight
   stale-state cleanup (via `clean_stale_shakedown.py`), shared-
   namespace single-run check, parent-owned active-run + seed write,
   orchestrator dispatch, production synthesis surfacing. Target:
   `packages/plugins/codex-collaboration/skills/dialogue/SKILL.md`.
   **Do NOT include `codex.dialogue.*` tools in `allowed-tools`.**
4. Extend `hooks.json` `SubagentStart` and `SubagentStop` matchers to
   match `dialogue-orchestrator` in addition to `shakedown-dialogue`.
5. First end-to-end verification per plan §8.2 on a representative
   objective.
6. 14-item rubric inspection against the resulting verification
   transcript.
7. Confirm 566-test shakedown suite still passes unchanged.

**Acceptance gates from plan §11** — verify all 13 checkboxes.

**Potential obstacles:**
- Hook matcher extension is a silent-defeat risk if missed. Plan
  mentions it in four places specifically to prevent oversight.
- Preflight cleanup must be invoked from the skill before the live-
  run check — mirrors `shakedown-b1:35-45` pattern.
- `/dialogue` skill `allowed-tools` must NOT include dialogue MCP
  tools or the bootstrap test trips.

### 2. Optional post-v1 cleanup items

These are explicitly deferred in the plan but worth tracking:

- Rename `<data_dir>/shakedown/` directory to neutral or add a
  parallel `dialogue/` namespace (plan §7.2, triggered by dual-run
  support or operator confusion).
- Rework `containment_guard.py:180` operator message ("outside the
  shakedown scope") to neutral phrasing (plan §7.2).
- Secrets redaction for allowed-scope content (plan §5.3, T4-CT-05).
- Rename `test_bootstrap.py::test_no_user_invocable_dialogue_skill_exists`
  to match its actual assertion body (user's optional suggestion from
  this session).
- Factor `dialogue-codex` skill body to a thin adapter over the
  production-local reference doc (plan §2.2, remaining-T-04 closure).

### 3. Remaining T-04 closure (not v1)

Per plan §2.2: production gatherer agents + briefing assembly +
multi-agent scope transport + shared-authority reference unification.
These are the remaining closure items for T-04 after v1 ships. Not
blocked on v1 implementation landing; not scheduled here.

## In Progress

**Clean stopping point — plan approved, merged to main, pushed to
origin. No work in flight.**

- **Approach:** v1 scoping packet closed as approved implementation
  baseline.
- **State:** complete. Plan is `main@73f8c9c1`; working tree clean;
  `origin/main` synced.
- **Working:** plan is syntactically well-formed; status is `Approved`
  in frontmatter; all 13 acceptance checkboxes in §11 are written into
  the plan (not checked — they're implementation gates, not plan-quality
  gates).
- **Not working:** nothing broken.
- **Open question:** whether the next session begins T-04 v1
  implementation, Engram implementation, or something else — depends
  on user prioritization.
- **Next action:** user decides next packet; if v1 implementation,
  start with plan §12 step 1 (extract reference doc).

## Open Questions

### 1. Which packet does next session start?

**Context:** Three active-work packets are viable:
- T-04 v1 implementation (now unblocked by this session).
- Engram implementation (spec merged at `d615439`, build sequence in
  `docs/superpowers/specs/engram/delivery.md`).
- Something the user surfaces fresh.

**Impact:** High — sets the frame for the next session. Both active
packets are substantial.

### 2. Plan §10 authoring-time decisions (deferred to implementation)

Plan §10 explicitly defers four decisions to the implementation
session:
- Exact inline-scouting tool budget (§6.2 initial target N=3).
- `/dialogue` flag vocabulary (profile, explicit paths, budget override).
- Production synthesis serialization (Markdown wrapper vs raw JSON).
- Recovery semantics on orchestrator crash.

These are implementation decisions, not plan blockers. Implementation
session resolves them at authoring time.

### 3. Optional post-v1 cleanup timing

Plan §7.2 lists post-v1 cleanup items (namespace rename, operator-
message rewording, bootstrap-test rename). None are blocking.
Question: when is the right moment to batch them? Natural trigger is
either (a) remaining-T-04 closure or (b) a separate cleanup ticket.

## Risks

### 1. Hook-matcher extension oversight during implementation

**Impact:** Plan §7.1 names this as critical. If implementation session
adds `/dialogue` skill and `dialogue-orchestrator` agent without
extending `SubagentStart` / `SubagentStop` matchers in `hooks.json`,
containment lifecycle never activates for production — silent
containment defeat.

**Mitigation:** Plan references this in four sections (§7.1, §8.3,
§9.1, §11). Prior handoff captures it as Learning. This handoff
captures it in Next Steps. Implementation session must verify hook
firing before declaring success per plan §8.3.

### 2. Preflight cleanup script call-site compatibility

**Impact:** Plan §6.1 step 1 says `/dialogue` invokes
`scripts/clean_stale_shakedown.py` "the same sweep `shakedown-b1`
runs at its step 4." Assumes the script's command-line interface works
the same from `/dialogue` as from `shakedown-b1`. If the script has a
caller-specific assumption (e.g., environment vars unique to
shakedown-b1's invocation context), `/dialogue` invocation could
silently fail to sweep.

**Mitigation:** Implementation session should test the preflight
invocation in isolation (simulate a stale `active-run-*` + `scope-*`,
invoke the script, verify cleanup fires) before integrating into
`/dialogue` skill. Low-probability risk but easy to verify.

### 3. `/dialogue` skill `allowed-tools` drift (bootstrap test)

**Impact:** If any future edit adds `codex.dialogue.*` to the skill's
`allowed-tools`, `test_bootstrap.py::test_no_user_invocable_dialogue_skill_exists`
fails. The test name reads broad; edit-authors might add the tools
thinking "the skill needs them" without realizing the orchestrator
owns them instead.

**Mitigation:** Plan §8.4 names this as a boundary invariant explicitly.
Implementation session documents this in the skill's own SKILL.md body
as an "architectural boundary" note. Could also add a comment in
`allowed-tools` frontmatter.

### 4. `dialogue-codex` and extracted reference drift (v1 discipline)

**Impact:** Plan §9.3 names zero-behavioral-edits-during-v1 as the
discipline. Any hotfix or clarification to per-turn semantics must
land in both `dialogue-codex` and the extracted reference in the same
commit.

**Mitigation:** v1 is expected to be a short packet — discipline is
tractable. Remaining-T-04 closure (§2.2) factors `dialogue-codex` to
an adapter, eliminating the risk structurally.

### 5. Stale run younger than 24h blocks live-run check

**Impact:** `clean_stale_shakedown.py` uses a 24h age threshold. A
crashed run younger than 24h won't be swept, and the subsequent live-
run check will fail fast with the "run in progress" message. Same
failure mode shakedown-b1 has. Operator remediation is manual state-
file removal.

**Mitigation:** Plan §5.2 documents this. Not a new v1 risk — it's
inherited infrastructure behavior.

## References

### This session's landed commit

- `73f8c9c1` on `main` — docs(plan): add approved T-04 v1 production dialogue scoping plan

### Plan artifact (approved baseline)

- `docs/plans/2026-04-13-t04-v1-production-dialogue-scoping-plan.md`
  (632 lines, status: Approved, committed as `73f8c9c1`)

### Prior handoffs (chain)

- Loaded this session:
  `docs/handoffs/archive/2026-04-13_22-09_t04-v1-plan-rewritten-after-three-scrutiny-rounds.md`
- Prior:
  `docs/handoffs/archive/2026-04-13_19-45_t04-v1-scoping-plan-drafted-pending-review.md`
- Pre-prior:
  `docs/handoffs/archive/2026-04-13_18-50_t04-gap-analysis-and-turn-semantics-closure.md`

### Code surfaces read this session

- `packages/plugins/codex-collaboration/scripts/clean_stale_shakedown.py`
- `packages/plugins/codex-collaboration/skills/shakedown-b1/SKILL.md:1-120`
- `packages/plugins/codex-collaboration/scripts/containment_lifecycle.py:50-170`
- `packages/plugins/codex-collaboration/tests/test_bootstrap.py:1-50, 230-283`
- `packages/plugins/codex-collaboration/skills/dialogue-codex/SKILL.md:100-130, 330-360`
- `packages/plugins/codex-collaboration/.claude-plugin/plugin.json`

### T-04 prior authority cited by the plan

- T1 (termination): `docs/plans/2026-04-02-t04-t1-structured-termination-contract.md:59` (enum values)
- T2/T3/T4/T5/T6/T7/T8 — full list in plan §13.

### Ticket (supersession)

- `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md`
  (stays open — v1 ≠ T-04 closure per plan §2)

## Gotchas

### Plan is now on main; feature branch is gone

**Symptom:** User or future-Claude opens a session; `git branch` does
NOT show `feature/t04-v1-scoping-plan`.

**Root cause:** Branch was merged fast-forward to `main` and deleted
with safe `-d` this session.

**Prevention:** Not a gotcha in the strict sense — this is the
expected state. But prior handoffs in the chain reference the branch
as if it still exists. Future sessions should note that the plan is
now on `main` directly; no branch to check out.

### `plugin.json` is metadata-only — do NOT add skill/agent declarations

**Symptom:** Implementation session looks at `plugin.json` and assumes
new skills/agents need to be declared there, or tries to add them.

**Root cause:** `plugin.json` at `.claude-plugin/plugin.json` is pure
metadata. Skills/agents auto-discover from their directory structure.
Only hooks (`hooks.json`) require explicit matcher entries.

**Prevention:** Plan §7.1 no longer has a `plugin manifest` row — it
was dropped precisely to prevent this misconception.

### T1 enum values are lowercase strings, not uppercase constants

**Symptom:** Implementation session writes `termination_code = SCOPE_BREACH`
or similar uppercase naming, following what the `TerminationCode` type
label suggests.

**Root cause:** T1 line 59 defines values as lowercase string literals
(`"convergence" | "budget_exhausted" | "scope_breach" | "error"`). The
`TerminationCode` label reads as enum constants but the literal values
don't match.

**Prevention:** Plan §6.3 and §8.3 now use lowercase
`"scope_breach"`. Implementation session should mirror literal values
exactly.

### `termination_code` is NOT in the current transcript emission

**Symptom:** Implementation session tries to inspect transcript for
`termination_code` field and finds nothing.

**Root cause:** Current `dialogue-codex/SKILL.md` emission shape has
`converged: bool` in the epilogue, projected from `termination_code`.
The code itself is production-synthesis-only (§3.2 field table row 4).

**Prevention:** Plan §3.2, §3.3, §6.3, §8.3 all reflect this
distinction now. Scope-breach evidence:
- Production synthesis: `termination_code = "scope_breach"`.
- Transcript: `converged: false` + `ledger_summary` prose.

### `test_no_user_invocable_dialogue_skill_exists` name is broader than body

**Symptom:** Future-Claude reads the test name and assumes any user-
invocable skill named something like `/dialogue` will fail the test.

**Root cause:** The test body (`test_bootstrap.py:263-283`) only
asserts `allowed-tools` doesn't intersect dialogue MCP tools. A user-
invocable skill whose `allowed-tools` doesn't include
`codex.dialogue.*` mechanically passes.

**Prevention:** Plan §8.4 captures this as an invariant with the
rationale. `/dialogue` skill's `allowed-tools` must NOT include
dialogue MCP tools — orchestrator owns those.

### Session ID 72e0c2e6 differs from prior handoff's 501301e6

**Symptom:** Future debugging notices session ID differs from prior
handoff in the chain.

**Root cause:** Each Claude Code session gets a fresh session ID.
Chains track via `resumed_from` frontmatter, not session ID equality.

**Prevention:** Trust `resumed_from`. This handoff points at
`docs/handoffs/archive/2026-04-13_22-09_*` which was consumed via
`/handoff:load` at session start.

## Conversation Highlights

### User's pinpoint guidance, distinguishing doc corrections from architectural debates

Verbatim:

> "I would not reopen Findings 1, 3, or the manifest row. Those are
> straight doc corrections, not architectural debates. I would only
> surface the Finding 2 nuance, and even that does not need a separate
> discussion thread unless you want to change the bootstrap test itself."

This is the sharpest framing the user has delivered for scope control.
"Doc corrections" = apply directly, no reopen. "Architectural
debates" = requires discussion. The distinction is actionable.

### User rewrote their own earlier claim based on evidence

Verbatim:

> "Keep the substance: the plan should name the bootstrap boundary
> explicitly. Drop my earlier stronger claim that `/dialogue`
> necessarily breaks the existing test. Replace it with the invariant
> you identified."

User absorbed the mechanical evidence I'd surfaced and rewrote their
own framing. Intellectual honesty on display. This is the second
session in the program where the user has done this (prior session
also saw several user-authored reframings mid-review).

### User commit-sequence pattern

Three consecutive authorized steps, each explicit:

1. "flip status to Approved and commit"
2. "merge feature/t04-v1-scoping-plan into main now" (via `/merge-branch`)
3. "push main to origin"

Each step separately authorized. User does not bundle. This is the
second session where the commit-merge-push sequence has followed this
cadence. Worth preserving as the standard: confirm each step, don't
chain without authorization.

### User's clean-pass acknowledgement

Verbatim:

> "No findings on the revised plan. This pass came back clean. The
> stale-cleanup gap is now covered in the run model, the transcript
> contract no longer overclaims fields the frozen `dialogue-codex`
> emission shape cannot carry, and the `/dialogue` bootstrap boundary
> is now stated in the mechanically correct way: the user-invocable
> skill stays free of `codex.dialogue.*`, while the orchestrator owns
> those calls."

User cited three specific improvements by name. Explicit positive
acknowledgement matches the pattern from prior sessions ("materially
stronger", "this is now credible enough to rewrite the plan"). Read
as calibration signal: work met the bar.

### Residual-risk framing

Verbatim:

> "Residual risk is implementation drift rather than plan drift: keep
> the eventual `/dialogue` `allowed-tools` aligned with
> `test_bootstrap.py`, keep scope-breach evidence prose-only on the
> transcript side, and keep `dialogue-codex` byte-for-byte untouched
> in the v1 packet."

User separated plan-risk from implementation-risk. This is a useful
discipline: implementation risks belong in the handoff's Risks
section (they're runtime concerns), plan risks belong in the plan's
risk section (they're baseline concerns). My handoff Risks section
reflects this split.

## User Preferences

**Scope control via "doc corrections vs architectural debates":**

User's explicit framing from this session:
> "Those are straight doc corrections, not architectural debates."

Pattern: review findings that require only doc-level edits get
"apply directly." Findings that would reopen a settled decision
get explicit discussion. Future sessions should pre-classify their
response into this taxonomy.

**Apply directly — four-fold "directly" as explicit license:**

User said: "Apply ... directly. Apply ... directly. Drop ...
directly. Rewrite ... [directly]."

The repetition was deliberate and operative. When the user lays out an
itemized apply-directly instruction, the right response is execution,
not another review cycle. Produced 11 parallel edits in one turn; user
validated on first review.

**Evidence-first pushback when warranted:**

User accepted the partial pushback on Finding 2 without friction, then
rewrote their own claim:
> "Drop my earlier stronger claim that `/dialogue` necessarily breaks
> the existing test."

Pattern: evidence-backed partial pushback is welcome. Vague pushback
("I don't think so") is not.

**Commit-merge-push as three separate authorizations:**

User chained `/save → commit → merge → push` via four explicit
requests. Never bundled. Future sessions: confirm each step;
don't assume authorization for the next.

**Frontmatter hygiene matters:**

User chose "flip status to Approved and commit" when I surfaced the
`status: Draft` frontmatter before committing. Small-but-real hygiene
point — machine-readable metadata should match the landing context.

**Review-as-is over in-conversation iteration:**

Third appearance of this pattern. Standing preference for this repo.
Produce the artifact, hand off, fresh review pass.

**Positive acknowledgement as calibration data:**

Verbatim quotes from this session:
- "No findings on the revised plan. This pass came back clean."
- (Implicit approval via commit-merge-push sequence.)

Explicit positive signals are real signal in this repo (user has said
this several times across the program). Read the acknowledgement tone
as calibration for the work's bar, not politeness.

**Direct-merge over PR for design plans:**

User invoked `/merge-branch` directly, no PR. This matches the prior
handoff's noted pattern for design plans in this repo. For code
changes the default may differ; for plan docs, direct-merge is
standard.
