---
date: 2026-05-07
time: "23-08"
created_at: "2026-05-08T03:08:48Z"
session_id: 6f00ca31-a5a5-405d-b43c-5e6a8a9142ce
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-05-07_22-35_build-plan-committed-execution-deferred.md
project: claude-code-tool-dev
branch: feature/public-skills-repo-design
commit: 16366af9
title: "Public-skills-repo: scrutiny pass on plan + audit-miss discovery → spec v6 + plan re-revision; execution still deferred"
type: handoff
files:
  - docs/superpowers/plans/2026-05-07-public-skills-repo-build.md
  - docs/superpowers/specs/2026-05-06-public-skills-repo-design.md
---

# Handoff: Spec v6 and plan re-revision; execution still deferred

## Goal

Resume from prior session's "build plan committed at `7d748bb6`, execution deferred" handoff and execute the build plan in a fresh session — i.e., produce the verified-ready local artifact at `/Users/jp/Projects/active/claude-code-skills/`.

**What actually happened:** Execution was deferred a second time. Two finding chains pushed the work back into spec/plan revision before a single Task 1 step ran:

1. **User's own scrutiny pass on the build plan** — produced a "Minor revision" verdict with 7 required changes (clerical drift + robustness holes + precision improvements). I verified each finding against the file, then applied 8 surgical edits.
2. **Pre-execution `trash` audit query from user** — turned into a real audit miss: 8 `trash` references in 2 of the 22 publishable skills (`git-hygiene` ×7, `writing-principles/writing-principles.md` ×1). `trash` is a user-machine convention from the author's CLAUDE.md, not part of macOS or universal Claude Code surface. Spec v5's audit framework didn't catch this category. Same shape as the v4→v5 progression (each adding a new structural scan category).

**Stakes:** Without addressing both finding chains, the build would have produced an artifact that (a) had clerical issues making the verification protocol incoherent and (b) shipped 7 directives prescribing a non-portable tool to external adopters. The first is recoverable; the second is hard to recover (artifact is published before the bug surfaces in user reports).

**Success criteria for this session (achieved):**
- Plan revisions for the 7 scrutiny findings, committed
- Spec revised to v6 covering the audit-miss class, with the new category formally added to Step 4b, committed
- Plan re-revised against spec v6, committed
- Handoff written so a fresh session can pick up execution

**Connection to project arc:** Third-to-last session in the public-skills-repo design track, with the publish phase deferred to a future plan. Prior arc:
1. Initial design (v1) — `30c68a8e`
2. Re-audit and rewrite (v2) — `095e2c70`
3. Minor revision after scrutiny v2 (v3) — `66b19a5b`
4. Major revision after scrutiny v3 (v4) — `7cd09882`
5. Minor revision after scrutiny v4 (v5) — `9ab5a4ad`
6. Build plan written (`7d748bb6`)
7. Plan minor revision per scrutiny — **`6c341b9c` (this session)**
8. Spec v6 (personal-tool category) — **`1b9ed8c9` (this session)**
9. Plan re-revision for v6 — **`16366af9` (this session)**
10. Execution (next session) — pending
11. Publish plan + execution (further deferred)

A separate publish plan will cover spec Steps 9-11 (`gh repo create`, push, tag, marketplace verify).

## Session Narrative

Session opened by `/load`-ing the prior handoff (`2026-05-07_22-35_build-plan-committed-execution-deferred.md`). That handoff concluded with "Continue with the integrity check, then run Task 1?" expecting the next session to verify spec/plan binding (`9ab5a4ad`/`7d748bb6`) and start executing.

The user did not proceed to execution. Instead they posted a fully-formed scrutiny verdict on the plan: "Minor revision" with 7 required changes plus an execution-model contract mismatch. The verdict named specific lines and specific defect types — it was clearly a real adversarial pass, not a casual question.

**First decision point: verify findings before acting.** The scrutiny made specific claims (e.g., "lines 1051-1065 have 15 pre-marked `[x]` checkboxes"; "line 924 trap second `mv` is unprotected"). These are falsifiable. I ran a sequence of `rg`/`Read` commands to verify each:
- `[x]` checkboxes: confirmed 15 occurrences on lines 1051-1065, all on acceptance criteria.
- "Tasks 11" / "Tasks 2-11" / "11 (Step 8)": confirmed at lines 1053 + 1095. Plan has 10 tasks, not 11 — clerical drift from the prior session's `replace_all`-substring renumbering bug (captured as a Learning in the prior handoff but never swept downstream).
- Trap second `mv`: confirmed at line 924 — `mv "$TMPSKILLS/skills.bak" ~/.claude/skills` with no existence guard. The user's worked example slightly overstated one branch (the `trash` of the tmp dir is conditional on `set -e` and trap completion), but the underlying hole is real regardless of which exact path.
- PCRE check: confirmed at line 117 (`/etc/hostname`) — fragile.
- Variable scope: confirmed by smoking-gun comment at line 196 (`# or: trash <path-from-Step-1> if SCRATCH var was lost`) — the plan already knows it's fragile.

**Second decision point: scope of revision.** Asked the user via `AskUserQuestion` between three options: clerical only (#3+#4) / substantive only (4 fixes) / all 7 + reconcile execution model. User chose **"All 7 + reconcile execution model"** — the recommended option. The execution-model reconciliation could go two ways: (a) tighten Tasks 5/8 to literal text so `subagent-driven-development` is viable, or (b) drop the sub-skill recommendation, keep judgment caveats, recommend `executing-plans` only. I went with (b) per the inline recommendation.

Applied 8 surgical edits to the plan in sequence:
1. Preface — drop subagent-driven-development from REQUIRED SUB-SKILL, mark "not recommended" with reason
2. Task 1 Step 5 PCRE check — stdin pipe instead of `/etc/hostname`
3. Task 9 Step 4 trap — multi-line, `skills.bak` existence check, three `TRAP:` recovery lines on stderr
4. `[x]` → `[ ]` (used `replace_all`; safe per verification — only 15 occurrences, all in acceptance section)
5. "Tasks 2-11" → "Tasks 2-10" (combined with the [x] flip on line 1053)
6. Self-review numbering — `+ 9 (Step 6) + 10 (Step 7) + 11 (Step 8)` → `+ 8 (Step 6) + 9 (Step 7) + 10 (Step 8)`
7. Task 6 Step 5 — added expected hit-count baseline (30-80 typical), reframed as manual scan
8. Conventions — added Shell variable scope bullet; Task 5 codex-delta `trash` got `|| true` for re-run safety

Verified post-edits with `rg -c '\[x\]'` (returns 0), `rg -c '^## Task'` (returns 10), no stale "Tasks 11" references. Committed at `6c341b9c` with structured commit message naming the binding ("address all 7 required changes from scrutiny pass").

Reported back with the standard `What changed / Why / Verification / Remaining risks` contract. Asked: "Awaiting your decision: proceed to integrity check + Task 1 now, or hold for separate session?"

**The pivot:** User did not answer the proceed question. Instead asked: "When we use `trash`, is that a macOS native tool or is that a tool that is specific to my machine?"

This is the kind of suspicion-trigger that should not be answered casually. I gave the factual answer (no, not native; Homebrew install via `brew install trash`) but flagged the implication immediately — there are two distinct concerns, with very different stakes. The build plan using `trash` is fine (your workflow on your machine). The shipped skills referencing `trash` is potentially a problem because external adopters don't have it. The spec's existing lexical residue regex doesn't include `trash` (would be too broad). Step 4b structural scan also wasn't designed to catch this. So whether the shipped skills reference `trash` is an open question. Asked: "Want me to run that scan now, before Task 1?"

User said: "run that scan now."

**The scan defect.** First scan attempt used `for s in $SKILLS_22; do ...; done` with the 22-skill names in a space-separated string. All three passes (case-sensitive `trash`, case-sensitive `Trash`, install hints) returned empty. I had ALSO included a counter-test (`rg "skill"` over the same scope, expecting hundreds of hits). Counter-test returned **0 hits**. That's impossible for a directory of SKILL.md files. The bug surfaced: zsh (which Claude Code's Bash tool uses on macOS) does NOT word-split unquoted variables by default — the `for s in $SKILLS_22` iterated ONCE with `$s` set to the entire 22-name string. `rg` got a nonexistent path argument and silently failed via `2>/dev/null`. Without the counter-test, I would have reported "No `trash` references found in shipped skills" and proceeded to execution with the bug in place.

**Re-running with array iteration** (`SKILLS_22=(adversarial-review claude-md ...)` then `"${SKILLS_22[@]}"`) produced 49 .md files scanned and 8 hits in 2 skills:
- `git-hygiene/SKILL.md` — 7 references at lines 21, 33, 151, 241, 291, 335, 379. The skill is architecturally about deletion safety; `trash` is foundational, not incidental.
- `writing-principles/writing-principles.md:753` — 1 reference, in a meta-example table about prohibition phrasing. Read context (lines 745-755) to triage: it's a META example illustrating "negative-instruction-is-clearer", using `rm -rf`/`trash` as the example pair. Not a directive; the example just leaks the local-tool convention.

**Two decisions to make.** Asked via `AskUserQuestion`:
1. How to handle the git-hygiene `trash` prescription (Generalize / Hybrid / Ship-as-is / Defer). User chose **"Generalize to portable language."**
2. Where the fix lives (Spec v6 + plan re-revision / Plan-only patch / Plan-only no-spec). User chose **"Spec v6 + plan re-revision."** Most principled path.

Began spec v6 edits. Applied surgical edits in sequence:
1. Status: `Draft v5 — minor revision per scrutiny v4` → `Draft v6 — minor revision after pre-execution audit-miss finding`
2. SANITIZE git-hygiene row extended with 7 line-specific replacements + Requirements paragraph
3. SANITIZE writing-principles row extended with `writing-principles.md:753` example swap
4. Step 4b — added category (f) personal-tool prescriptions with enumerated targets and "why this isn't in lexical" rationale
5. Acceptance criteria — `(a)-(e)` → `(a)-(f)`
6. Decisions item 1 — reframed "two-layer machinery" to "multi-category machinery, asymptotic completeness" (v4→v5→v6 each added a category)
7. History — appended v6 entry

**Bug encountered.** The v6 history entry was inserted using `Edit` with `old_string = "- **v5 (this revision):** minor revision per scrutiny v4."` and `new_string = "- **v6 (this revision):** ...\n\n- **v5 (committed `9ab5a4ad`):** minor revision per scrutiny v4."`. This put v6 BEFORE v5 in the file (chronologically inverted). Verification grep `rg -n '^- \*\*v[0-9]'` showed v1, v2, v3, v4, v6, blank, v5 — wrong order.

**Mitigation.** Decided not to do a giant `Edit` swap (~6KB of v5+v6 text per side). Instead used a small Python script via `Bash`: read file, find both entries via regex anchors, swap their positions, write back. Verified the swap produced v1→v2→v3→v4→v5→v6 in correct order. This is the pattern for in-place reorderings where Edit-tool gymnastics are awkward.

Committed spec v6 at `1b9ed8c9` with structured commit message naming the audit-miss class and the v4/v5/v6 progression.

Then re-revised the plan for spec v6:
1. Spec binding header (line 7): `(v5, commit 9ab5a4ad)` → `(v6, commit 1b9ed8c9)`
2. Task 5 Step 2 (git-hygiene) restructured into Part A (codex/cleanup, v5 carryover) + Part B (7 trash portability edits + Requirements paragraph, v6)
3. Task 5 Step 6 (writing-principles) restructured into Part A (SKILL.md Composability removal, v5 carryover) + Part B (writing-principles.md:753 meta-example swap, v6). Updated the v5 "do NOT touch writing-principles.md" note to reflect the targeted v6 edit.
4. Task 6 heading: `(5 categories)` → `(6 categories)`. Added new Step 6 for category (f) with the targeted rg scan and acceptable-vs-defect form distinctions. Renumbered the USER GATE step from 6 to 7.
5. Acceptance criteria — sanitization-changes bullet names v6 additions; structural-scan bullet says `(a)-(f)`.

Verified post-edits: spec binding `1b9ed8c9` ✓, no stale `9ab5a4ad` ✓, no stale `5 categories` ✓, Task 6 has both Part A and Part B markers ✓. Plan grew from 1122 to 1220 lines (+98 net), consistent with substantive additions.

Committed plan re-revision at `16366af9`.

User then said: "After you finish both the spec revision and the plan revision, save a handoff so that we can proceed with execution in a fresh session." Initiated `/save`.

## Decisions

### Apply all 7 scrutiny findings + reconcile execution model

**Choice:** Apply all seven required changes from the user's scrutiny pass, AND reconcile the contract mismatch by dropping `subagent-driven-development` from the plan's REQUIRED SUB-SKILL preface (option (b)), keeping `executing-plans` only.

**Driver:** User selected "All 7 + reconcile execution model" from `AskUserQuestion`. The scrutiny verdict was "Minor revision" — fix-list, not open question. The execution-model resolution preserves the implementer-judgment caveats in Tasks 5 and 8 (which subagent-driven would strip via per-task isolation).

**Alternatives considered:**
- **Substantive only (4 fixes):** trap robustness, `[x]` precheck, Tasks 11+ references, sub-skill preface. Skip the regex-baseline (#5), PCRE-fragility (#6), variable-scope (#7) findings as known-fragile-but-tolerable. Lighter touch. Rejected — user chose the more thorough option.
- **Clerical only (#3 + #4):** flip `[x]` to `[ ]` and fix Tasks 11+ references. Minimum to make the verification protocol coherent. Rejected — leaves real robustness holes (trap, PCRE, variable-scope) for execution-time discovery.
- **Execution-model option (a):** tighten Tasks 5/8 to literal diffs and literal README/LICENSE text, drop "implementer judgment" caveats, make `subagent-driven-development` viable. Rejected because it would have inflated the plan substantially (literal README ~500-1000 lines of prose) and removed reasonable judgment calls.

**Implication:** Plan now reads as a single-Claude execution document. Tasks 5 and 8 retain prose-spec form. Future workflow plans should declare execution model up front and align spec density to it.

**Trade-offs accepted:** The plan grew from 1100 to 1122 lines (then to 1220 after v6 re-revision). Some optional improvements deferred (e.g., sample `claude --debug` output for Task 9; dedicated acceptance-criteria audit step before Task 10's commit) — low-impact, accepted.

**Confidence:** High (E1 — explicit user choice with verified findings).

**Reversibility:** High — could revert any specific edit. Trap rewrite is the only structural change; remainder are surgical.

**Change trigger:** If execution surfaces new robustness gaps that the seven fixes didn't cover, capture as a learning and fold into next plan iteration.

### Generalize `trash` references in git-hygiene to portable language

**Choice:** Replace 7 `trash` prescriptions in `git-hygiene/SKILL.md` with portable language ("a reversible deletion mechanism") and add a one-paragraph Requirements explanation listing concrete tools by OS (macOS `trash`, Linux `trash-put`, GNOME `gio trash`, fallback inspect-before-`rm`).

**Driver:** User selected "Generalize to portable language" from `AskUserQuestion`. The question explicitly framed `trash` as a user-machine convention (per the hook context: `trash already in ~/dotfiles/homebrew/Brewfile`) and `git-hygiene` as architecturally about deletion safety.

**Alternatives considered:**
- **Hybrid (Recommended in question):** keep `trash` as primary recommendation with install instructions in skill body and README. Adopters install or skip. Less disruptive to skill content but ties safety to a specific tool. Rejected.
- **Ship-as-is + README mitigation:** no skill content changes; document in README. Lightest touch, least defensive. Adopters who skip the README hit `command not found` mid-execution. Rejected.
- **Defer to v0.2.x:** ship v0.1.0 as-is, address based on adopter feedback. Inconsistent with prior 5 scrutiny rounds' diligence. Rejected.

**Implication:** The skill is now OS-portable. The safety property (recoverable deletion) is preserved as an abstract requirement; tool selection delegates to the adopter's installed toolchain. This is the canonical pattern for any future "personal-tool prescription" findings.

**Trade-offs accepted:** Slightly more prose per directive ("a reversible deletion mechanism (e.g., \`trash\` on macOS, \`trash-put\` on Linux, \`gio trash\` on GNOME)" is heavier than just `\`trash\``). Adopters need to know what "reversible deletion" means. Mitigated by the Requirements paragraph at first occurrence.

**Confidence:** High (E1 — explicit user choice).

**Reversibility:** High — could revert to `trash`-only if adopter feedback shows the abstraction confused users.

**Change trigger:** If adopters consistently misinterpret "reversible deletion mechanism" as `rm -i` or `mv to ~/.Trash/`, tighten the language.

### Spec v6 + plan re-revision (vs plan-only)

**Choice:** Address the `trash` audit miss at the spec layer (v6) with a new Step 4b category (f) and SANITIZE table extensions, then re-revise the plan against v6.

**Driver:** User selected "Spec v6 + plan re-revision" from `AskUserQuestion`. The framing in the question: this is the most principled path; matches the v4 (added Step 4b) and v5 (added category (e)) pattern of formalizing the audit-miss in the spec.

**Alternatives considered:**
- **Plan-only patch + spec note (Recommended in question):** add Task 5 substeps for the specific edits in the plan, add a small note in the spec's residual-risks. Faster; spec stays at v5. Rejected — user chose the heavier option.
- **Plan-only patch, no spec touch:** pure execution-layer fix. Rejected — loses the audit-gap learning.

**Implication:** Spec is now at v6 with formal acknowledgment that audit-completeness is asymptotic (v4→v5→v6 each added a category). This sets a precedent: future scrutiny rounds that surface new categories should follow the same pattern (define category → add Step 4b sub-scan → update SANITIZE table). Plan binding now points to spec v6 commit `1b9ed8c9`.

**Trade-offs accepted:** Two extra commits this session. One additional integrity check coordinate for the next session (now both spec and plan must verify, two commit hashes to validate). Heavier than plan-only would have been.

**Confidence:** High (E1 — explicit user choice).

**Reversibility:** Medium — could revert spec to v5 and retro-fold the v6 SANITIZE entries into a plan-only patch, but that would lose the formalized category (f) framework.

**Change trigger:** None expected — the spec-revision path is the canonical answer for audit-miss findings.

### Use Python via Bash for in-place v5/v6 history swap

**Choice:** When the v6 history entry ended up chronologically inverted (between v4 and v5 instead of after v5), used a small inline Python script via `Bash` to swap the two entries in-place, rather than constructing a giant `Edit` with both entries' full text on each side.

**Driver:** Pragmatism. The two history entries are ~3KB each; an Edit swap would require ~6KB of text in old_string and ~6KB in new_string. Edit tool handles this but it's noisy. Python read+modify+write is mechanical, idempotent, and verifiable.

**Alternatives considered:**
- **Giant Edit with both entries duplicated:** old_string = v6 + blank + v5_start; new_string = v5_full + v6_full. Verbose; risk of typo or whitespace drift between the two copies of long blocks. Rejected.
- **Two-step Edit (delete v6 then re-insert after v5):** clean conceptually but requires copying v6's full content into the second Edit's new_string anyway. Rejected — same cost, more steps.
- **Sed-based in-place swap:** would work but `sed` regex for matching multi-line bullet points is fragile. Rejected.

**Implication:** Pattern for similar in-place reorderings of large text blocks: prefer Python `re.search`/`replace` over Edit-tool gymnastics. Cleaner audit trail (the script's match anchors and replace logic are explicit).

**Trade-offs accepted:** A small-script-via-Bash sidesteps the Edit tool's atomicity guarantee. Mitigated by reading the result back via `rg -n '^- \*\*v[0-9]'` to verify ordering.

**Confidence:** High (E2 — script ran cleanly, verification grep confirmed correct order).

**Reversibility:** High — could re-swap with the same script.

**Change trigger:** Nothing.

### Did not include `trash` in Step 5 lexical regex (v6)

**Choice:** Spec v6's Step 5 lexical regex remains unchanged — `trash` is NOT added to the token list. Category (f) handles personal-tool prescriptions via Step 4b structural-checklist instead.

**Driver:** Lexical regex's value depends on bounded false positives. Adding `trash` would create high FP rate ("trash this idea", "in the trash bin", "macOS Trash" capitalized) while the actual targets (command-style usage in code blocks) are better caught by the structural checklist anyway. Same logic excludes `mise`, `stow`, `brew`, `uv`, `ruff` — all generic-enough words that lexical inclusion would dilute the gate.

**Alternatives considered:**
- **Add `trash` (case-sensitive) to lexical:** would catch lowercase `trash` references. FP rate moderate. Rejected — sets precedent for adding generic English to lexical, which dilutes its precision over time.
- **Both lexical AND structural:** belt-and-suspenders. Rejected — duplicates work without adding signal.

**Implication:** The structural-vs-lexical division is preserved: lexical = unique internal-vocab tokens (low FP rate); structural = manually-adjudicated checklist for categories with real-word overlap. Spec v6 documents this rationale explicitly so future scrutiny rounds don't try to add personal-tool tokens to lexical.

**Trade-offs accepted:** Category (f) requires manual scan instead of automated regex gate. Acceptable for v0.1.0 given enumerated target list.

**Confidence:** High (E2 — verified by spec text + acceptance criteria framing).

**Reversibility:** High — could add specific tokens to lexical in a future iteration if FP rate proves manageable.

**Change trigger:** If `mise`/`stow`/`uv`/`ruff` references multiply in future skill additions and the manual scan becomes burdensome.

## Changes

### Plan minor revision per scrutiny (commit `6c341b9c`, +45/-23, 1 file)

**File:** `docs/superpowers/plans/2026-05-07-public-skills-repo-build.md`

**Purpose:** Address user's scrutiny verdict ("Minor revision", 7 required changes + execution-model contract mismatch) before Task 1 of execution starts.

**Approach:** 8 surgical edits in sequence, each targeting a specific finding. Verified post-edits with grep counters. Single coherent commit.

**Key implementation details:**
- **Preface (line 3):** dropped `subagent-driven-development` from REQUIRED SUB-SKILL, marked "not recommended" with reason ("per-task isolation strips spec context that Tasks 5/8 implementer-judgment caveats rely on"). `executing-plans` is now the only sub-skill recommendation.
- **Task 1 Step 5 PCRE check (line 117-118):** stdin pipe `echo "test" | rg --pcre2 -n 'test' >/dev/null && echo "PCRE2 OK"` instead of `rg --pcre2 -n 'test' /etc/hostname || true`. Cleaner test, doesn't depend on `/etc/hostname` existence.
- **Task 9 Step 4 trap (lines 919-948):** rewrote as multi-line block. Added `[ -d "$TMPSKILLS/skills.bak" ]` existence check before the second `mv`. On failure (skills.bak missing), emits three `TRAP:` lines on stderr explaining recovery via `tar xzf "$BACKUP" -C ~/.claude` and explicitly NOT trash-ing the tmp dir (to preserve any live skills stranded in `skills.test`).
- **Acceptance criteria (lines 1051-1065):** flipped 15 `[x]` to `[ ]`. Used `replace_all` after verifying these were the only `[x]` in the file.
- **Tasks 2-11 → Tasks 2-10 (line 1053):** combined with the `[x]` flip on the same line into a single Edit.
- **Self-review numbering (line 1095):** `+ 9 (Step 6) + 10 (Step 7) + 11 (Step 8)` → `+ 8 (Step 6) + 9 (Step 7) + 10 (Step 8)`. Three sequential off-by-ones from the renumbering bug carried over from prior session.
- **Task 6 Step 5 regex (line 583-590):** added "Expected hit count: typically 30-80 matches" baseline + reframed as manual scan with bounded count signal. Compares to Step 1 (~40 hits / 4-FP list) for analogy.
- **Conventions section (line 65):** added Shell variable scope bullet — names `SCRATCH` (Task 2), `BACKUP` and `TMPSKILLS` (Task 9) and the cross-step references; mandates either single-Bash-invocation execution or literal-value passing.
- **Task 5 codex-delta (line 408-410):** wrapped `trash skills/making-recommendations/references/codex-delta.md` with `2>/dev/null || true` and follow-up existence check + `GONE`/`TRASH FAILED` echo, so re-runs don't error if the file's already trashed.

**Pattern followed:** Same bite-sized + verification-gate model the plan already used. Each edit is targeted; no rewrites.

**Future-Claude note:** This commit was a precursor to spec v6. It addressed the scrutiny findings independently of the audit-miss discovery. The plan was committed clean before the `trash` discussion started.

### Spec v6 — add personal-tool category (commit `1b9ed8c9`, +23/-6, 1 file)

**File:** `docs/superpowers/specs/2026-05-06-public-skills-repo-design.md`

**Purpose:** Formalize the audit-miss class (personal-tool prescriptions presented as universal directives) at the spec layer. Adds a sixth category to Step 4b structural scan; documents the asymptotic-completeness pattern in Decisions item 1.

**Approach:** 7 surgical edits + one Python-via-Bash chronological reordering of v5/v6 history entries (which my initial Edit had inverted).

**Key implementation details:**
- **Status (line 5):** `Draft v5 — minor revision per scrutiny v4` → `Draft v6 — minor revision after pre-execution audit-miss finding (personal-tool prescription class)`.
- **History v6 entry:** ~1.5KB paragraph naming the finding (8 trash references in 2 skills), the 5 specific changes, and the audit-completeness pattern note. Inserted at line 15 after chronological reordering.
- **SANITIZE git-hygiene row (line 63):** extended from "codex/cleanup branch convention" only to include 7 line-specific `trash` replacements + the Requirements paragraph spec. Severity marked "High — portability" (new severity tag).
- **SANITIZE writing-principles row (line 67):** extended to include the `writing-principles.md:753` meta-example swap (`rm -rf`/`trash` pair → `commit secrets`/`exclude .env` pair).
- **Step 4b category (f) (after line 400):** ~25-line block defining personal-tool prescriptions, enumerated targets (`trash`, `trash-cli`, `brew`, `mise`, `stow`, `uv`, `ruff`), acceptable forms (install instructions, portable examples, documented Requirements), and explicit "why this isn't in lexical Step 5" rationale.
- **Acceptance criteria (line 542):** structural-scan bullet updated from `(a)-(e)` to `(a)-(f)`.
- **Decisions item 1 (line 521):** "two-layer machinery (v4)" reframed to "multi-category machinery, asymptotic completeness (v4 → v6)". Documents the v4/v5/v6 progression. Notes the response pattern when new categories surface in future scrutiny: define category → add Step 4b sub-scan → update SANITIZE table.

**Pattern followed:** Spec History/SANITIZE/Step 4b/Acceptance/Decisions — each section is updated as part of a coherent revision. Same shape as v5's revision pattern.

**Bug encountered:** v6 history entry inserted in wrong chronological position (between v4 and v5 instead of after v5). My initial `Edit` matched on `- **v5 (this revision):**` and substituted `- **v6 (this revision):** ...\n\n- **v5 (committed `9ab5a4ad`):**`. That put v6 first, then a blank line, then v5. Detected via `rg -n '^- \*\*v[0-9]' "$SPEC"` showing inverted order.

**Mitigation:** Inline Python script via Bash:
```python
import re
text = open(path).read()
v6_match = re.search(r'^- \*\*v6 \(this revision\):\*\* .*$', text, re.MULTILINE)
v5_match = re.search(r'^- \*\*v5 \(committed `9ab5a4ad`\):\*\* .*$', text, re.MULTILINE)
old_block = v6_match.group(0) + "\n\n" + v5_match.group(0)
new_block = v5_match.group(0) + "\n" + v6_match.group(0)
text = text.replace(old_block, new_block, 1)
open(path, 'w').write(text)
```
Verified post-swap with `rg -n '^- \*\*v[0-9]'` showing v1→v2→v3→v4→v5→v6 order.

### Plan re-revision for spec v6 (commit `16366af9`, +108/-10, 1 file)

**File:** `docs/superpowers/plans/2026-05-07-public-skills-repo-build.md`

**Purpose:** Re-bind plan to spec v6 (commit `1b9ed8c9`) and apply the v6-mandated edits.

**Approach:** 5 targeted edits — spec binding, two SANITIZE entries split into Part A/Part B, Task 6 expanded with category (f), acceptance criteria.

**Key implementation details:**
- **Spec binding (line 7):** `(v5, commit 9ab5a4ad)` → `(v6, commit 1b9ed8c9)`.
- **Task 5 Step 2 git-hygiene:** restructured into Part A (codex/cleanup, 2 lines, v5 carryover) + Part B (7 trash portability edits + Requirements paragraph, v6). Part B has 8 numbered substeps (7 line replacements + 1 inline insertion) plus a verify block expecting CLEAN-A and 4-6 acceptable-form `trash` hits in install/example contexts only.
- **Task 5 Step 6 writing-principles:** restructured into Part A (SKILL.md Composability removal, v5 carryover) + Part B (writing-principles.md:753 meta-example swap, v6). Part B has the literal old/new table-row text. Updated the v5-era "do NOT touch writing-principles.md" warning to specifically allow the v6 line-753 edit.
- **Task 6 heading (line 608):** `(5 categories)` → `(6 categories)`. Goal text updated to mention "personal-tool prescriptions".
- **Task 6 new Step 6 (line 680):** inserted before the existing USER GATE (which became Step 7). Has the `rg -nw 'trash|trash-cli|brew|mise|stow|uv|ruff' skills/` scan with expected 4-12 hit baseline. Documents acceptable forms (install, portable example, documented Requirements paragraph) vs. defects (bare imperatives).
- **Acceptance criteria:** sanitization-changes bullet names v6 additions explicitly; structural-scan bullet says `(a)-(f)`.

**Pattern followed:** Plan revision mirrors spec revision. Each Part A/Part B split makes the v5-vs-v6 origin of edits transparent for execution-time understanding.

**Future-Claude note:** When executing Task 5 Step 2, run Part A first (verify codex/cleanup CLEAN), then Part B (7 trash edits + Requirements insertion). The verify block at the end checks both. Don't conflate the two — they're independent edits with different rationales.

### Archived: prior session's handoff

**File:** `docs/handoffs/archive/2026-05-07_22-35_build-plan-committed-execution-deferred.md`

Moved by `/load` skill at session start. State file written to `.session-state/handoff-6f00ca31-...` for `resumed_from` tracking; this handoff's frontmatter `resumed_from` field points back to the archive path.

## Codebase Knowledge

### Spec / plan / handoff layout in this monorepo

| Path | Type | Authority |
|------|------|-----------|
| `docs/superpowers/specs/` | Spec documents | Approved spec v6 (`1b9ed8c9`) |
| `docs/superpowers/plans/` | Implementation plans | Re-revised plan (`16366af9`) |
| `docs/handoffs/` | Active handoffs | This handoff |
| `docs/handoffs/archive/` | Resumed handoffs | Prior handoff (resumed at session start) |
| `docs/handoffs/.session-state/` | Chain state files | 24-hour TTL |
| `extensions/skills/` | Dev-staged skills (~29) | Source for the public-repo build |
| `~/.claude/skills/` | Production skills (deployed via `scripts/promote`) | Affected by Task 9's stash |

### Public-skills-repo audit framework (now 6 categories at Step 4b)

| Category | What it catches | Mechanism |
|----------|-----------------|-----------|
| Step 5 lexical | Internal-vocab leakage in prose (codex, engram, superspec, jpsweeney97, etc.) | `rg -i` over 18+ unique tokens |
| Step 4b (a) | Plugin-relative slash commands | PCRE `\B/[a-z]…(?::[a-z0-9-]+)?` |
| Step 4b (b) | Named-skill refs in tables/prose | "X skill" / "the X skill" / "Distinct from X" |
| Step 4b (c) | Environmental flag deps | `CLAUDE_CODE_EXPERIMENTAL_*` |
| Step 4b (d) | Sibling-skill cross-refs | "Distinct from X, Y, Z" |
| Step 4b (e) | Named protocols / procedures / workflows (added v5) | PCRE `\b[\w-]+(?:[\s-][\w-]+)*\s+(workflow\|protocol\|procedure)\b` |
| Step 4b (f) | Personal-tool prescriptions (added v6) | `rg -nw 'trash\|trash-cli\|brew\|mise\|stow\|uv\|ruff'` |

The v4→v5→v6 progression each added a new category. Spec v6 Decisions item 1 names this as "asymptotic completeness" — future scrutiny may surface more categories; the response pattern is define → add Step 4b sub-scan → update SANITIZE table.

### Public-skills-repo target structure

Unchanged from prior handoff. Plan creates `/Users/jp/Projects/active/claude-code-skills/` (new repo, **outside** this monorepo) with 22 skills under `skills/`, manifests under `.claude-plugin/`, and repo-level docs (README, LICENSE, CHANGELOG, CONTRIBUTING, .gitignore).

**12 PUBLISH AS-IS:** `adversarial-review`, `exiting-worktrees`, `format-export`, `implementation-review`, `llm-reference`, `prompt-generator`, `review-code`, `review-plan`, `review-strategy`, `review-writing`, `scrutinize`, `system-design-review`.

**10 SANITIZE:** `claude-md`, `git-hygiene`, `next-steps`, `merge-branch`, `making-recommendations`, `writing-principles`, `handbook`, `readme`, `design-review-team`, `explore-repo`. Of these, `git-hygiene` and `writing-principles` got expanded SANITIZE entries in v6.

### `git-hygiene` skill architecture

The skill is **architecturally about deletion safety**. The 7 `trash` references are not incidental:
- `SKILL.md:21` — top-level rule defining the skill's deletion convention
- `SKILL.md:33` — table cell defining the `apply-destructive` action
- `SKILL.md:151` — output template for "Files to delete"
- `SKILL.md:241` — procedure step in the destructive-action workflow
- `SKILL.md:291` — anti-pattern table mandate
- `SKILL.md:335` — output template counter ("files deleted with trash: 0")
- `SKILL.md:379` — anti-pattern recovery prescription

Generalizing all 7 to "a reversible deletion mechanism" preserves the safety property (recoverable deletion) while delegating tool selection to the adopter's installed toolchain. The Requirements paragraph at line 21 names concrete tools by OS so adopters know what satisfies the abstraction.

### `writing-principles/writing-principles.md` is a 71KB supplementary file

Most of it is illustrative content (failure-mode catalog, prohibition-phrasing examples, common violations). Spec v5 designated it as "do not touch except for documented FPs at lines 54+1025". Spec v6 adds line 753 (the meta-example swap) to the touched-set. The rest of the file remains off-limits for this curation.

### Key locations

| Concept | Location |
|---------|----------|
| Spec v6 | `docs/superpowers/specs/2026-05-06-public-skills-repo-design.md` (commit `1b9ed8c9`) |
| Build plan (re-revised) | `docs/superpowers/plans/2026-05-07-public-skills-repo-build.md` (commit `16366af9`) |
| Source skills | `extensions/skills/<name>/...` |
| 22-skill name list | Embedded in scan scripts and Plan Task 4 allowlist |
| Production skills (target of Task 9 stash) | `~/.claude/skills/` |
| Target repo (created by Task 3) | `/Users/jp/Projects/active/claude-code-skills/` |
| Writing-plans skill | `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-plans/SKILL.md` |
| Executing-plans skill | `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/executing-plans/SKILL.md` |

## Context

### Prior project arc (compressed)

- **2026-05-06 (`30c68a8e`):** v1 spec drafted (premature "Approved").
- **(`095e2c70`):** v2 — rewrite after agent-summary audit found unsound; new counts 13+9.
- **(`66b19a5b`):** v3 — minor precision fixes; 14+8.
- **(`7cd09882`):** v4 — major revision per scrutiny v3. Added Step 4b structural scan, Step 0 preflight, README Requirements, `trash`-based deletion rule (ironic given v6's findings), `claude-md` PUBLISH→SANITIZE.
- **(`9ab5a4ad`):** v5 — minor revision per scrutiny v4. Added category (e), success criteria section, README v2.1.32+ floor, subshell-scoped trap, `set -euo pipefail`, CHANGELOG.md spec. Counts 12+10=22.
- **(`7d748bb6`):** Build plan written (10 tasks, halt before publish).
- **`6c341b9c` (this session):** Plan minor revision per user's scrutiny pass.
- **`1b9ed8c9` (this session):** Spec v6 — added category (f) personal-tool prescriptions.
- **`16366af9` (this session):** Plan re-revision for spec v6.
- **Pending:** Build execution (next session). Publish plan + execution (further deferred).

### Mental model

This is **iterative-formalization-of-an-audit-framework**, not a system-build problem.

The spec defines a curation procedure for transforming dev-staged skills into a public-shippable set. The procedure has audit gates that must be sound to produce a safe artifact. Each scrutiny round has surfaced a category of audit miss that the prior framework didn't anticipate:
- **v4 added Step 4b** because lexical-only audit missed structural references.
- **v5 added category (e)** because Step 4b's slash-command/named-skill categories missed bare-name workflow references.
- **v6 added category (f)** because Step 4b's existing categories framed the missing class as "real-tool reference" rather than "personal-prescription leak".

The **asymptotic completeness** framing (now formal in spec v6 Decisions item 1) accepts that new categories may continue to surface. The response pattern is established: define category → add Step 4b sub-scan → update SANITIZE table → re-revise plan. v0.1.0 doesn't need perfect audit-completeness; bug reports against the public repo are the catch-all.

A useful analogy: the audit framework is like a defensive perimeter. Each scrutiny round identifies a hole in the perimeter and adds a new section of fence. The perimeter is always partial; the question is whether it's complete enough for v0.1.0 release.

### Environment

- **Working directory:** `/Users/jp/Projects/active/claude-code-tool-dev` (this monorepo)
- **Branch:** `feature/public-skills-repo-design`
- **Working tree:** clean as of session end
- **HEAD:** `16366af9` (plan re-revision commit)
- **Tools needed for execution:** `bash`, `git` ≥ 2.28, `gh` (authenticated), `trash-cli`, `ripgrep` with PCRE2, `tar`, `claude` CLI ≥ 2.1.32, `python3` (used this session for one in-place edit; not needed for execution)

### Spec ↔ plan task mapping (compressed; unchanged from prior session except v6 additions)

| Spec Step | Plan Task | What it does |
|-----------|-----------|--------------|
| Preconditions | Task 1 | Verify gh auth, trash, git, claude, rg PCRE |
| Step 0 (preflight) | Task 2 | Pre-validate `source: "./"` in scratch repo (USER GATE) |
| Step 1 (init) | Task 3 | `mkdir + git init -b main` |
| Step 2 (structure) + Step 3 (copy) | Task 4 | `.claude-plugin/`, `skills/`, allowlist copy of 22 skills, `.DS_Store` strip |
| Step 4 (sanitize) | Task 5 | 10 substeps; **Steps 2 + 6 each have Part A + Part B for v6 additions** |
| Step 4b (structural scan) | Task 6 | **6 substeps now** (added Step 6 for category (f)); USER GATE is Step 7 |
| Step 5 (lexical grep) | Task 7 | Single grep run (regex unchanged from v5), expect only 2 documented FPs |
| Step 6 (manifests + docs) | Task 8 | plugin.json, marketplace.json, README, LICENSE, CHANGELOG, CONTRIBUTING, .gitignore |
| Step 7 (validation) | Task 9 | Tarball + subshell-stash + claude --plugin-dir (USER GATE) — trap hardened in `6c341b9c` |
| Step 8 (commit) | Task 10 | Single "Initial release" commit; HALT |
| Steps 9-11 | **Deferred** | gh repo create, push, tag, marketplace verify |

## Conversation Highlights

**Opening — user posts scrutiny verdict:**
User posted a fully-formed scrutiny output ending with `**Minor revision.**` verdict and 7 required changes. Notable: the message mirrored the explanatory-style "★ Insight" framing the assistant uses, suggesting the user ran scrutiny themselves and presented the findings.

The implicit ask was "address these," but the scope was ambiguous (clerical only? all 7? all 7 + execution-model resolution?). My response: verify findings against the file, ask user to choose scope.

**Scope answer:**
> "Which revision scope to apply to the build plan before executing Task 1?" → User chose: "All 7 + reconcile execution model"

The Recommended option. Notable that the user accepted the inline recommendation that option (b) (drop subagent-driven from preface) was the right execution-model resolution.

**The pivot question:**
> User: "I have a question first. When we use `trash`, is that a macOS native tool or is that a tool that is specific to my machine?"

The phrasing "I have a question first" is the trigger — user is signaling that execution shouldn't proceed until this is answered. Suspicion-mode question; deserved a careful answer with implication-flagging, not just a factual reply.

**Scan trigger:**
> User: "run that scan now"

Two-word answer to my offered scan. Confirms the option-letter style preference noted in prior handoff — minimal commentary, action-only response when the choice is clear.

**Trash-finding decisions:**
> "How to handle the git-hygiene `trash` prescription?" → "Generalize to portable language" (NOT the recommended Hybrid option)
> "Where should the fix live — spec or plan?" → "Spec v6 + plan re-revision" (NOT the recommended plan-only option)

User chose the **most thorough** option in both cases, against my Recommended-marker hints. This continues the pattern from prior session ("user uses Recommended as starting point, not endpoint"). They have higher quality bar than my recommendations were calibrated for.

**End-of-session prompt:**
> User: "After you finish both the spec revision and the plan revision, save a handoff so that we can proceed with execution in a fresh session."

Sent mid-execution as a `<system-reminder>` rather than a separate turn — user wanted to make sure the handoff happened without interrupting the spec/plan work in flight. Clear instruction; no ambiguity.

**Working pattern observed:** User did NOT proceed straight to plan execution despite the prior handoff's "Continue with Task 1?" pose. They ran their own quality gate (scrutiny pass) BEFORE letting execution start, and asked the `trash` question that triggered another quality gate. The pattern: **two independent quality checks before execution**, even when the prior session "completed" the planning phase.

## User Preferences

**Quality bar over recommended ease:**
On both AskUserQuestion calls about scope (revision scope; spec-vs-plan layer), user chose the heavier option — NOT the one labeled Recommended. Prior session showed the same pattern with execution mode. Future-Claude should treat Recommended labels as *defaults to consider*, not *defaults to push*. When the user's likely answer would be "what's most thorough?", lead with the thorough option even if it's heavier.

**Execution-pause questions are quality gates, not casual asides:**
> "When we use `trash`, is that a macOS native tool or is that a tool that is specific to my machine?"

Phrased as a question, but it's the user gate-checking before execution starts. Future-Claude: when the user asks an apparently-simple factual question right before "proceed?" was asked, treat it as a suspicion-trigger. Answer thoroughly with implications flagged.

**Plain-language explanations, structured artifacts (per saved memory):**
The session followed this — reasoning was conveyed in prose with `★ Insight` blocks, while the spec/plan files use formal headings, tables, and structured changes. The verbose multi-section commit messages used heading-style bullet structure for navigation. Direct application of `feedback_plain_language.md`.

**Handle commits proactively (per saved memory):**
Three commits this session, none asked-about: plan revision (`6c341b9c`), spec v6 (`1b9ed8c9`), plan re-revision (`16366af9`). All used HEREDOC commit messages, no `--no-verify`, no force, no amend. Direct application of `feedback_handle_commits.md`.

**No `git add -A` or `git add .`:**
Each commit staged the specific file path: `git add docs/superpowers/plans/...` and `git add docs/superpowers/specs/...`. Honored even when the staged set was unambiguous (only one file modified).

**No `rm` ever:**
Used `trash` for the codex-delta deletion in plan-edits. The plan itself prescribes `trash` for build steps but generalizes prescriptions in shipped skills. Build-vs-ship distinction maintained.

**Multiple-choice efficiency:**
User responded to AskUserQuestion in seconds with a single-option pick. No commentary, no commentary-needed. The pattern: questions calibrated, options enumerated, user picks. Don't ask follow-up clarifications when the answer is decisive.

## Learnings

### Counter-test patterns prevent silent-failure-induced false negatives

**Mechanism:** Empty output from a shell pipeline is suspicious unless paired with an independent counter-test that should have produced output. Without a counter-test, an empty result can mean "no matches found" OR "the pipeline is broken." `2>/dev/null` (used here for "skill directory not found" errors) makes the second case invisible.

**Evidence:** Initial scan with `for s in $SKILLS_22; do rg -nw 'trash' "$s/" 2>/dev/null; done` returned empty across all three passes. Counter-test (`rg "skill"` over the same scope, expecting hundreds of hits) returned 0. That's impossible — the directories contain SKILL.md files. The `for` loop was iterating ONCE with `$s` as the entire 22-name string (zsh doesn't word-split unquoted variables), so `rg` got a nonexistent path and silently failed via the error suppression.

**Implication:** For any scan where the "no findings" answer would be load-bearing, include a counter-test that proves the scan ran. Patterns:
- Counter-grep with a token expected to be everywhere (e.g., `skill` for SKILL.md files; `function` for code).
- File count via `find ... | wc -l` to confirm the iteration saw files.
- Explicitly checking the iteration variable count: `for s in ...; do echo "$s"; done | wc -l` to confirm N=22, not N=1.

**Watch for:** Bash-vs-zsh word-splitting differences. zsh does NOT word-split unquoted variables by default. Array form (`SKILLS=(a b c)`, then `"${SKILLS[@]}"`) works in both shells. `setopt SH_WORD_SPLIT` enables bash-style splitting in zsh but is per-shell setting. Default to arrays for any iteration over multi-element variables.

### Audit-framework completeness is asymptotic, not absolute

**Mechanism:** Each scrutiny round of the public-skills audit has surfaced a new category that the prior framework didn't anticipate. v4 added Step 4b structural scan (caught dangling references invisible to lexical). v5 added category (e) named-protocols (caught bare-name workflow refs). v6 added category (f) personal-tool prescriptions (caught `trash` references). The pattern suggests the audit-completeness premise is ongoing.

**Evidence:** Spec v6 Decisions item 1 now formalizes this: "v4 added Step 4b (structural-vs-lexical), v5 added category (e) (named protocols), v6 adds category (f) (personal tools) — each scrutiny round has surfaced a category the prior framework missed. Audit-completeness premise is asymptotic, not absolute."

**Implication:** Future scrutiny rounds may surface more categories. The response pattern is established: define category → add Step 4b sub-scan with regex/checklist → update SANITIZE table for known instances → re-revise plan to bind to new spec version → document in the spec's Decisions item 1 progression. Don't treat the discovery of a new category as a failure of prior diligence; treat it as iteration of an asymptotic process.

**Watch for:** When refreshing audit frameworks for similar curation work in the future, build in the expectation of incremental category-discovery. Initial framework can be (and should be) less than complete; the formalization process is iterative.

### Personal-tool prescriptions are a distinct audit class

**Mechanism:** A skill prescribes a specific external tool (e.g., `trash`) without acknowledging it's user-installed. The tool name is a real word (high lexical FP rate) AND the reference points to a real tool (so structural-checklist for "dangling references" doesn't catch it — the tool exists, just not universally). This is its own category, separate from internal-vocab leakage and dangling-references.

**Evidence:** Spec v6 category (f) names the targets: `trash`, `trash-cli`, `brew`, `mise`, `stow`, `uv`, `ruff`. These are user-machine tools (per `~/dotfiles/homebrew/Brewfile`) that the author's CLAUDE.md prescribes as universal directives. The fix: portable language with concrete-tool examples in a Requirements paragraph.

**Implication:** When publishing skills extracted from a personal/project codebase, audit for tool-name references separately. Don't just rely on lexical/structural categories — those are designed for vocab-leakage and reference-integrity, not tool-portability. Personal-tool category requires its own scan with bounded targets (the toolchain you know is non-universal).

**Watch for:** The author's own CLAUDE.md is the canonical source of personal-tool prescriptions. Future scrutiny: enumerate tools mentioned in CLAUDE.md as required, then grep shipped content for those.

### Python-via-Bash for in-place file edits when Edit gymnastics get awkward

**Mechanism:** The `Edit` tool requires `old_string` to match exactly. For some operations (in-place reordering of large blocks, multi-section coordinated changes), the natural `old_string` and `new_string` would each be ~5-10KB of mostly-identical content. A small inline Python script (read → modify → write) is cleaner.

**Evidence:** v5/v6 history swap this session. The two entries are ~3KB each. An Edit-based swap would have required ~6KB on each side of the operation. Python's `re.search` + `text.replace(old_block, new_block)` is mechanical and idempotent, with explicit match anchors that document what's being moved.

**Implication:** Consider Python-via-Bash for: reorderings of large blocks, multi-occurrence coordinated edits (where each occurrence has subtle differences), text manipulations that depend on regex semantics that Edit doesn't support. Don't use it for simple substitutions or single-line changes — Edit is cleaner for those.

**Watch for:** The script must be self-contained (no external deps) and verify success (e.g., check `old_block in text` before replacing). Always verify the result with a follow-up `rg` or `Read`.

### `replace_all` is safe when verified single-purpose

**Mechanism:** `replace_all=true` substitutes every occurrence. Risky when the pattern is a substring of unintended targets (prior session's lesson: `# Task 9` matches inside `## Task 9:`). Safe when verified that ALL occurrences are the intended targets.

**Evidence:** Used `replace_all` to flip 15 `[x]` → `[ ]` on the plan's acceptance criteria. Pre-verified with `rg '\[x\]'` showing all 15 occurrences were on lines 1051-1065 (acceptance section only). Post-verified with `rg -c '\[x\]'` returning 0. Worked cleanly.

**Implication:** `replace_all` requires a verification grep BEFORE the edit. If the grep output is bounded and exclusively the intended targets, `replace_all` is safe and efficient. If the grep shows unintended targets, fall back to specific-context Edits.

**Watch for:** Patterns that are real substrings of common structures (e.g., `# Task` is a substring of `## Task`). Markdown structures with header-prefix relationships are particularly hazardous.

## Next Steps

### 1. Resume in a new session and execute the plan

**Dependencies:** None — both spec and plan are committed.

**What to do first:** Run `/load` to resume from this handoff. Verify spec/plan integrity (now TWO hashes to check):

```bash
git log --oneline -1 -- docs/superpowers/specs/2026-05-06-public-skills-repo-design.md
# Expected: 1b9ed8c9

git log --oneline -1 -- docs/superpowers/plans/2026-05-07-public-skills-repo-build.md
# Expected: 16366af9
```

If either has shifted, reconcile drift before executing.

**Approach suggestion:** Use `superpowers:executing-plans` (inline mode). Subagent mode is **not recommended** per spec v6 — Tasks 5/8 contain implementer-judgment caveats that the per-task isolation would strip.

**Acceptance criteria:** Plan's Task 10 commits a single "Initial release" commit on `main` in `/Users/jp/Projects/active/claude-code-skills/`. The plan's acceptance-criteria checklist (in-scope subset) is fully checked.

**Potential obstacles:**
- **Step 0 preflight may fail** (`source: "./"` rejected) — would require restructuring spec to nested layout BEFORE re-running.
- **Task 5 Step 2 Part B** has 8 substeps with line numbers from the source file; line numbers may shift slightly in the just-copied file. Use `rg` to find current locations rather than trusting source line numbers.
- **Task 9 validation may fail** if a sanitize edit corrupted SKILL.md frontmatter or YAML — return to Task 5 substep, fix, re-verify.
- **Tarball backup may run out of disk space** — `set -euo pipefail` aborts before destructive mv (this is the WHOLE POINT of v5's `set -e` addition).
- **`trash` references in shipped artifact** — if Task 6 Step 6 finds defects (bare imperatives), return to Task 5 and add the missing edit.

### 2. Write the publish plan (post-build)

**Dependencies:** Build plan must execute successfully first.

**What to read first:** This handoff (for build-state context), the spec's Steps 9-11 (lines 469-489, may have shifted slightly with v6), the spec's Acceptance criteria (deferred items at line 553-554), the build plan's Acceptance criteria section (deferred items).

**Approach suggestion:** A separate plan covering: gh repo create, remote add, push -u origin main, git tag v0.1.0, push tag, gh repo edit --add-topic (×5), marketplace install verification in a separate clean-machine session, post-publish CHANGELOG date replacement.

**Acceptance criteria:** Repo public on GitHub, tagged `v0.1.0`, five discoverability topics applied, marketplace install verified end-to-end, post-publish success-criteria tracking initiated.

### 3. Track Success criteria for v0.1.0 (post-publish)

**Dependencies:** Publish plan must execute successfully.

**What to do:** Track the four post-publish criteria from spec lines 22-31 over the first month after release: discoverable via gh search, installable without contacting author, no "missing flag" support traffic, skill triggering works as described. Use observations to inform v1.x triage.

**Acceptance criteria:** Observations recorded somewhere durable (issue comment, separate notes file, or `docs/learnings/`).

### 4. (Optional) Audit other personal-tool references

**Dependencies:** Build execution should expose any remaining instances via Task 6 Step 6.

**What to do:** If build execution reveals references to `mise`, `stow`, `brew`, `uv`, or `ruff` in shipped skills (none found in this session's quick `trash` scan, but the v6 enumerated list includes them defensively), add SANITIZE edits and either re-revise spec to v7 or patch in the plan only.

**Acceptance criteria:** Task 6 Step 6 returns CLEAN or only acceptable forms (install instructions, portable examples, documented Requirements paragraph).

## In Progress

Clean stopping point. No work in flight.

The session ended at a natural boundary: spec v6 committed (`1b9ed8c9`), plan re-revised and committed (`16366af9`), working tree clean, handoff initiated.

## Open Questions

- **Will Step 0 preflight succeed?** Spec docs verification confirmed `source: "./"` should accept, but the running CLI may differ from docs. Plan halts the entire workflow if preflight fails — restructuring to nested layout is the contingency.
- **Will Task 9 clean-machine validation reveal any registration errors?** All 22 skills should register cleanly given the audit + sanitize work, but any frontmatter corruption in any sanitize step (especially the new v6 Part B git-hygiene Requirements paragraph insertion) could cause a skill to fail load. Recovery is to fix the substep and re-validate.
- **Should the spec v6 Decisions-item-1 asymptotic-completeness framing be added to the published artifact?** Currently it's only in the dev-monorepo spec. Could be useful as a CONTRIBUTING.md or design-rationale doc in the public repo. Decide if/when.
- **Whether to keep the tarball after Task 9 PASS.** Plan defaults to `trash`-ing it. Defense-in-depth argument for keeping it through Task 10. Low-stakes choice; defer to user at execution time. (Carried over from prior handoff — still open.)
- **Are there other personal-tool prescriptions in skills the v6 scan didn't enumerate?** Spec v6's category (f) regex covers `trash|trash-cli|brew|mise|stow|uv|ruff`. The author's CLAUDE.md mentions all of these; any in shipped skills will be caught by Task 6 Step 6. But there may be tools NOT in CLAUDE.md (e.g., `pyenv`, `nvm`, `rbenv`) that could leak. Risk-vs-effort suggests deferring to bug reports per spec v6's "asymptotic completeness, residual risk → bug reports" stance.

## Risks

- **Spec/plan integrity check now requires TWO hashes** — `1b9ed8c9` for spec, `16366af9` for plan. If either is edited between sessions, binding breaks. Mitigated by the integrity-check requirement in Next Steps #1.
- **Concurrent claude session during Task 9** — exposes the user's main shell to an empty `~/.claude/skills/`. Mitigated by subshell-scoped trap (v5) + tarball backup (v5) + hardened trap-second-mv (`6c341b9c` — added existence check + recovery instruction on stderr).
- **CHANGELOG `2026-MM-DD` placeholder accidentally "fixed" before publish** — plan's Task 8 Step 5 and Self-review section both flag this. Acceptance criteria preserve the placeholder.
- **Auth-teams flag dependency at install time** — 5 of 22 skills hard-stop without `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. README Requirements section is the primary mitigation; spec Risk #7 documents the venue interrogation and "fail visibly, fix on bug report" stance. (Carried over from prior handoffs.)
- **Audit-framework asymptotic-completeness assumption** — formal in spec v6 but means more categories may surface. Low-probability for v0.1.0 since the spec has been through 6 revisions and the personal-tool category was the only miss this session, but non-zero. Mitigated by acceptance-criteria → bug-reports flow.
- **`replace_all` regression** — same risk pattern as prior session (renumbering bug). This session's edits did not hit it because verification grep preceded each `replace_all` use. Future plan edits should keep this pattern.
- **Python-via-Bash side-effect** — the v5/v6 swap script wrote to the spec file directly via `open(path, 'w')`. If the read+modify+write encountered an error mid-stream, the file could end up partially written. Did not occur this session (script was simple and verified post-write), but the pattern is sharper-edged than Edit tool's atomicity. Future use should include error handling and post-write verification.

## References

| What | Where |
|------|-------|
| Approved spec v6 | `docs/superpowers/specs/2026-05-06-public-skills-repo-design.md` (commit `1b9ed8c9`) |
| Build plan (re-revised) | `docs/superpowers/plans/2026-05-07-public-skills-repo-build.md` (commit `16366af9`) |
| Resumed handoff (prior session) | `docs/handoffs/archive/2026-05-07_22-35_build-plan-committed-execution-deferred.md` |
| Spec v5 → v6 diff | `git diff 9ab5a4ad 1b9ed8c9 -- docs/superpowers/specs/...` |
| Plan revision diffs | `git diff 7d748bb6 6c341b9c -- docs/superpowers/plans/...` (scrutiny revision); `git diff 6c341b9c 16366af9 -- docs/superpowers/plans/...` (v6 re-revision) |
| Writing-plans skill | `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-plans/SKILL.md` |
| Executing-plans skill | `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/executing-plans/SKILL.md` |
| Handoff format reference | `packages/plugins/handoff/references/format-reference.md` |
| Handoff contract | `packages/plugins/handoff/references/handoff-contract.md` |
| Project arc commit chain | `30c68a8e → 095e2c70 → 66b19a5b → 7cd09882 → 9ab5a4ad → 7d748bb6 → 6c341b9c → 1b9ed8c9 → 16366af9` |

## Gotchas

- **Two integrity hashes now required** — spec `1b9ed8c9`, plan `16366af9`. If the next session checks only one, drift in the other can be missed.
- **CHANGELOG `2026-MM-DD` is intentional** — do NOT replace until publish time. Plan's Task 8 Step 5 and Self-review section both flag this.
- **`docs/superpowers/plans/` vs `docs/plans/`** — both exist with similar content in this repo. The plan went to the former for proximity to the spec, but either is valid local convention. Don't be confused if a future browse finds plans split across both.
- **zsh word-splitting bug** — caught this session via counter-test. `for s in $SPACE_SEPARATED_VAR; do ...` does NOT word-split in zsh by default; iterates once with the entire string as `$s`. Use array form (`var=(a b c)`, then `"${var[@]}"`) for portable iteration.
- **`# Task N` vs `## Task N:` substring relationship** — carry-forward gotcha from prior session. `replace_all` on `# Task 9` matches inside `## Task 9:`. Verified-before-replace is the mitigation.
- **History entry insertion order** — when adding a new History bullet, ensure chronological ordering. This session, `Edit` matching on the prior most-recent entry's preface inserted the new entry BEFORE the matched line. Correct pattern: match the prior entry's full body so the new entry appears AFTER it, OR explicitly verify post-Edit ordering and reorder if needed.
- **`trash` is non-portable but the Brewfile-tracked status is the reliable signal** — the hook injection ("trash already in `~/dotfiles/homebrew/Brewfile`") confirmed the tool's user-installed status. Future scans for personal-tool prescriptions should consult `~/dotfiles/homebrew/Brewfile` and `~/.config/mise/config.toml` for the canonical user-toolchain inventory.
- **Spec v6 history entry was initially inverted in chronological order** — sessions doing similar revisions should pre-check the desired insertion point and verify post-Edit with `rg -n '^- \*\*v[0-9]'`.
- **Auto-memory `MEMORY.md` does not yet reflect this session** — the spec v6 + plan re-revision aren't recorded. If user runs `/promote` or other memory-curation, this session's facts may need to be added.
- **Handoff archive chain is now 3 deep** — this handoff resumes the build-plan handoff, which resumed the v5-checkpoint, which itself resumed the v4-checkpoint. The `resumed_from` field only points to the immediate predecessor.

## Rejected Approaches

### Plan-only patch (no spec touch)

**Approach:** Add Task 5 substeps for the git-hygiene + writing-principles `trash` edits in the plan. Don't touch the spec at all.

**Why it seemed promising:** Lightest touch — fixes the artifact-bound issue without spec/plan binding churn. Single commit instead of three.

**Specific failure (rejected by user choice):** User explicitly chose "Spec v6 + plan re-revision" from the AskUserQuestion. Reasoning implicit in their choice: the audit-miss is a framework gap, not a one-off bug. Patching at the plan layer would fix THIS instance but leave the framework unable to catch the next instance (e.g., `mise`, `stow`).

**What it taught:** When a finding represents a class (audit-framework gap, not a single-instance bug), the principled fix is at the framework layer (spec) even if it costs more. Plan-only patches are appropriate for one-off implementation choices, not framework gaps.

### Hybrid: keep `trash`, document as requirement

**Approach:** Keep `trash` as the primary recommendation in `git-hygiene` body. Add a Requirements note at the top: install via `brew install trash` (macOS) or `pip install trash-cli` (Linux). Repo README mentions it in the per-skill requirements section.

**Why it seemed promising:** Keeps the skill opinionated (single recommended tool) while documenting the dependency. Less skill-content churn than full generalization.

**Specific failure (rejected by user choice):** User chose "Generalize to portable language" over the Recommended Hybrid option. Implicit reasoning: the safety property (recoverable deletion) shouldn't depend on a specific tool name; abstracting to "reversible deletion mechanism" makes the skill OS-portable AND tool-agnostic.

**What it taught:** When a skill is architecturally about a property (deletion safety), the prescription should name the property, not a specific tool. Tool examples can ride along as concrete-tools paragraphs without being mandated.

### Substantive-only revision (4 fixes, skip #5/#6/#7)

**Approach:** Apply only the trap-robustness, `[x]` precheck, Tasks 11+ references, and sub-skill preface fixes. Skip the regex baseline (#5), PCRE-fragility (#6), and variable-scope (#7) findings.

**Why it seemed promising:** Lighter touch — about half the edits. The skipped findings are precision improvements rather than robustness holes; could be tolerated as known-fragile-but-acceptable.

**Specific failure (rejected by user choice):** User chose the full all-7 option. Implicit reasoning: precision improvements pay off at execution time (#5 baseline tells the executor what to expect; #6 PCRE check is cleaner; #7 variable-scope avoids resume-time surprises). Skipping them would push fragility-handling to execution time.

**What it taught:** When the user has already done a thorough scrutiny and produced a fix-list, scope-down options that ignore the lower-severity findings are usually wrong. The user's quality bar matches the scope of the verdict, not a subset.

### Inline execution after plan revision (this session)

**Approach:** Commit the plan revision (`6c341b9c`), then immediately proceed to integrity check + Task 1 execution in this session.

**Why it seemed promising:** No session boundary risk; revision-fresh context for execution; "two birds, one session."

**Specific failure (rejected by user pivot):** User did not answer the "proceed?" question. Instead asked the `trash` question, which surfaced the audit miss and pulled the work back into spec/plan revision. By the time the v6 + plan re-revision was complete, the session had grown substantially and a fresh-context boundary became preferable.

**What it taught:** "Proceed?" prompts at the end of a coherent revision are an opportunity for the user to surface concerns BEFORE execution starts, not just an execution-trigger. Don't anchor on the prior plan ("we'll execute next") if the user signals new questions or concerns; treat those as legitimate gates.
