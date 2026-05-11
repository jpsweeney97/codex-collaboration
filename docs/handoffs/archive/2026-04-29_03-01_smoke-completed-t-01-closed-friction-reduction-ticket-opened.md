---
date: 2026-04-29
time: "03-01"
created_at: "2026-04-29T07:01:31Z"
session_id: 3afda249-a634-416b-b954-40d5a49a90fe
resumed_from: docs/handoffs/archive/2026-04-29_01-04_candidate-a-engineering-landed-7-commits-pushed-awaiting-plugin-restart-for-live-smoke.md
project: claude-code-tool-dev
branch: feature/delegate-execution-diagnostic-record
commit: aa3daed2
title: T-01 live `/delegate` smoke completed end-to-end (24 escalations, promotion verified); T-01 closed; T-20260429-01 friction-reduction ticket opened with Options B/E/F as Phase 1-3
type: handoff
files:
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - docs/tickets/closed-tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md
  - docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - ~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_codex_memory_reads_always_approve.md
  - ~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/MEMORY.md
---

# Handoff: T-01 smoke completed; T-01 closed; T-20260429-01 friction-reduction ticket opened

## Goal

Continue the T-20260423-01 (delegate execution remediation) story from the prior session's "Candidate A engineering landed; awaiting plugin restart for live smoke" stopping point. **This session ran the live `/delegate` smoke end-to-end, validated all 6 T-01 acceptance criteria via successful promotion, closed T-01, and opened a successor ticket (T-20260429-01) tracking the three plugin-level friction sources the smoke surfaced.**

**Bigger picture:** The branch `feature/delegate-execution-diagnostic-record` now represents the complete Candidate A diagnostic → engineering action → live validation → ticket closure → follow-up tracking arc. The smoke ran on the freshly-restarted plugin (post-`6a2bb5ae`), exercised the full delegation lifecycle (start → 24 escalations → completion → promotion), and produced a real artifact (`a7a4e9c9`: 1-line `# pyright: ignore[reportUnreachable]` suppression with justification comment on `delegation_controller.py:944`). Successful promotion satisfied AC #5 (the disposition criterion) via the strongest evidence path rather than a typed-rejection proxy.

**Trigger:** Prior handoff explicitly enumerated "Plugin restart (operator action)" and "Live `/delegate` smoke validation" as the next steps, with all engineering work committed and pushed. This session executed both, plus the closure and follow-up tracking that the smoke's outcomes required.

**Stakes:**
1. **T-01 ticket closeable** — only live smoke validation remained; this session produced and verified the closing evidence.
2. **Operational signal on delegation friction** — 24 escalations for a 1-line edit is far above expected; the smoke functioned as both a validation and a cost benchmark for the current plugin policy. The follow-up ticket captures three specific reductions (Options B/E/F) with measurable acceptance (≤2 escalations on a comparable smoke).
3. **Tracking discipline** — closing T-01 without recording the friction findings as separate tracked work would have created immediate drift in the reconciliation register (Maintenance Rule violation: "a closed ticket leaves real follow-on work behind").
4. **Memory persistence** — durable user policy on `~/.codex/` reads developed mid-session and saved to memory file `feedback_codex_memory_reads_always_approve.md` (later broadened to entire `~/.codex/` data root).

**Success criteria (all met):**
- ✓ Plugin restart confirmed via PID change verification (3-layer process chain all respawned)
- ✓ Live `/delegate` smoke ran end-to-end on real objective (silence Pyright `reportUnreachable` on `delegation_controller.py:942` `assert_never` arm)
- ✓ All 6 T-01 acceptance criteria satisfied with successful-promotion evidence (job `4586c6c3...`, artifact_hash `d26a0b22...`)
- ✓ Smoke artifact committed (`a7a4e9c9`) and primary-workspace verification re-ran clean (pyright 0 issues, focused pytest 2/2)
- ✓ T-01 ticket moved to `closed-tickets/` with full closure section; reconciliation register T-01 row removed
- ✓ T-20260429-01 ticket opened tracking Options B/E/F with measurable acceptance criterion (≤2 escalations target)
- ✓ Reconciliation register updated with new T-20260429-01 row in Ticket-Owned Active Work
- ✓ Memory updated with durable "always approve `~/.codex/` reads" policy
- ✓ All 3 commits pushed cleanly to origin

## Session Narrative

Resumed from `2026-04-29_01-04_candidate-a-engineering-landed-7-commits-pushed-awaiting-plugin-restart-for-live-smoke.md` via `/handoff:load`. Prior session left the working tree clean at branch HEAD `6a2bb5ae` with all engineering work pushed; the next operator action was plugin restart followed by live smoke.

**Phase 1 — Plugin restart verification.** User reported they restarted the plugin. I checked process state via `ps -ef | grep -E "codex|claude"` and confirmed all three layers of the plugin process chain had new PIDs:
- Claude Code: 21408 → 46669
- uv wrapper: 21455 → 46757
- Plugin Python MCP server: 21509 → **46796** (the load-bearing one — holds Python `sys.modules` cache for `runtime.py` and `delegation_controller.py`)

Verified on-disk `runtime.py:52` had `includePlatformDefaults: True` (Candidate A patch) — confirming the freshly-spawned MCP server imported the canonical state.

**Phase 2 — Smoke kickoff (objective debate).** I invoked `codex-collaboration:delegate` skill with vague args "smoke validation"; the skill loaded the protocol but I held before calling start because "smoke validation" wasn't a concrete objective. Surfaced this with the user via a recommendation to silence the Pyright "unreachable" hint at `delegation_controller.py:942` — a real carry-forward from the prior handoff's Open Questions. User responded with a `/copy`-routed Codex review confirming Option A (Pyright suppression) and providing a TIGHTENED objective verbatim:

> "Silence the expected Pyright 'unreachable' diagnostic on the exhaustive `assert_never(outcome)` arm in `packages/plugins/codex-collaboration/server/delegation_controller.py` near line 942 by adding the narrowest justified suppression/comment, without changing runtime behavior. Keep the change tightly scoped. Verify with a targeted Pyright check and any focused test(s) needed."

Sent that exact objective to `codex.delegate.start`. Got `job_id: 4586c6c3-39cb-49ff-815b-620d7f3212c9`, base_commit `6a2bb5aeb`, status `running`.

**Phase 3 — First escalation cycle (validate approval flow).** First poll surfaced `request_id: "0"` — a `command_approval` for `sed` reading a `verification-before-completion/SKILL.md` from `~/.codex/plugins/cache/`. Read-only, low risk, but the path is outside the worktree (sandbox blocks per `readableRoots`). User authorized approve via `/copy` with explicit reasoning ("first approval already exercised the live approve path you needed for T-01"). Sent decide(approve, "0") → `decision_accepted: true`. Bounded poll loop: request_id advanced 0 → 1 (worker dispatched).

**Phase 4 — Deny experiment (validate deny path).** Request_id "1" was another skill-doc read (`using-superpowers/SKILL.md`). User policy: "If the next escalation is still meta-tooling instead of the actual repo edit, tighten the leash and consider denying that one." Sent deny → `decision_accepted: true`. Bounded poll: 1 → 2.

**Phase 5 — Memory carve-out policy emerges.** Request_id "2" was `rg` searching `~/.codex/memories/MEMORY.md` for terms relevant to the objective (`delegation_controller`, `assert_never`, `Pyright`, `unreachable`). I recommended deny (still `~/.codex/` reads). User OVERRODE with explicit policy directive:

> "approve — authorize; let Codex consult its memory before proceeding. Codex should always be allowed to consult its memory"

I noted the disambiguation rule violation (trailing text on `approve`) but proceeded per clear intent. **Saved durable user policy to memory** (`feedback_codex_memory_reads_always_approve.md`) carving out `~/.codex/memories/` from deny-pressure. Approved request 2.

**Phase 6 — Policy broadening to all `~/.codex/`.** Request_id "3" was back to skill-doc reads (`test-driven-development/SKILL.md`). I recommended deny per the not-yet-broadened policy. User OVERRODE again:

> "I actually changed my mind about Codex reading skills - I want to always-approve Codex to read skills"

Updated memory file: replaced narrow "memories only" with broader "all `~/.codex/` reads" policy. Approved request 3. Note: the security boundary distinction between `~/.codex/memories/`/`plugins/cache/` (safe) and `~/.codex/auth.json`/`config.toml`/`history.jsonl` (mode 0600 credential paths) became important here — the user's policy is about WHAT THEY APPROVE, not what the plugin should bypass altogether.

**Phase 7 — In-worktree git-pointer friction discovered.** Request_id "4" was `rg` over `packages/plugins/codex-collaboration` and `tests` — IN-WORKTREE paths. The `command failed; retry without sandbox?` reason was puzzling because the worktree IS in `writableRoots`. Realized the cause: ripgrep respects `.gitignore`, which requires reading the worktree's `.git` pointer file pointing to `<source-repo>/.git/worktrees/<name>/` — a path OUTSIDE the worktree. This is the "Option E" pattern that would later become a ticket entry. Approved.

**Phase 8 — Long preparation cycle.** Escalations 5-13 were Codex's preparation phase: project config discovery (`pyrightconfig*.json`, `package.json`, `pyproject.toml`), targeted searches for the suppression site, convention checks across `~/.codex/` skill catalog, focused single-file searches for union member definitions, broad `pyright` mentions in docs/CI, narrower `pyright: ignore` syntax checks. Many of these would be eliminated by Options B+E. User commented during this phase: "By the way, this is a lot of friction" — noted, reinforced the post-smoke plugin-change plan.

**Phase 9 — Verification cycle starts.** Escalation 12 was the actual `pyright` baseline run on `delegation_controller.py` — first non-`rg` direct-objective command. Then file_change escalations 14-15 (denied first, then approved). Then post-edit pyright re-run (16), focused pytest (17), another file_change (18), git diff for artifacts (19), `trash` availability probe (20).

**Phase 10 — `file_change` opacity diagnostic.** Escalations 14 and 15 were `file_change` kind with **empty `requested_scope` payload** (`grantRoot: null, reason: null`). I flagged this as Option F: opacity defeats operator visibility. Tested deny (14) — Codex retried with same opaque payload (15), confirming the opacity is STRUCTURAL, not strategic. Approved 15 to push smoke through to terminal state, relying on Gate 1 (review-before-promote) for visibility instead.

**Phase 11 — Plugin policy investigation (mid-smoke).** User asked: "is there anywhere in the codex-collaboration plugin that should be updated?" I read `runtime.py:23-58`, then inspected `~/.codex/` directory contents to assess security implications. Found `auth.json`, `config.toml`, `history.jsonl` all at mode 0600 (credential paths). Recommended NARROWER carve-out (memories + plugins/cache only, NOT all of `~/.codex/`) to preserve credential boundary. User accepted: "wait for the smoke to finish before doing anything" — deferred plugin change to post-smoke.

**Phase 12 — Smoke completion.** After escalations 21-23 (more `~/.codex/memories/` reads with awk, post-test git diff prep, etc.), poll showed:
- `status: completed`
- `promotion_state: pending`
- `artifact_hash: d26a0b223c0d7c1fd3b96e309b1bbb11c348c8f26027de892c27421617769b9b`
- `changed_files: ["packages/plugins/codex-collaboration/server/delegation_controller.py"]`

Read `full.diff` (1 file, +3/-1 — exact suppression we asked for with 2-line justification comment), `test-results.json` (pyright 0 issues, pytest 2 passed 7 deselected), `changed-files.json`. Rendered full review per skill step 6e.

**Phase 13 — Promotion attempt 1 (typed rejection).** User authorized `/delegate promote` with a correction: T-01 isn't fully closed until promotion succeeds (criterion 5 = final disposition). Ran Gate 1: status preflight saw artifact_hash non-null (already materialized), so step 5 routed to confirm + promote. Promote returned typed rejection: `reason: "worktree_dirty"`. Investigated: 2 untracked items present (`docs/plans/04-29-2026-...md` and `docs/status/`). User confirmed both were intentional WIP from earlier today (separate concern from smoke).

**Phase 14 — Stash, retry, success.** Recommended `git stash push -u -m "pre-promote: docs reconciliation WIP"` to preserve WIP atomically. User authorized. Stashed cleanly (worktree clean), re-polled (`promotion_state: prechecks_failed` from prior failed attempt — informative state transition), re-promoted. Success: `promotion_state: verified`, `promotion_attempt: 2`, file applied to primary workspace.

**Phase 15 — Primary-workspace verification.** Per user's stated sequence ("Verify the promoted file in the primary workspace and rerun the same narrow checks there"), ran:
- `git status --short` → 1 modified file (the suppression diff)
- `sed -n '938,946p' delegation_controller.py` → confirmed the diff landed exactly at the right location
- `pyright delegation_controller.py` → 0 errors, 0 warnings, 0 informations (matches smoke artifact byte-perfect)
- `uv run pytest ... -k 'worker_failed_before_capture or start_wait_elapsed'` → 2 passed, 7 deselected (matches smoke artifact byte-perfect)

**Phase 16 — Smoke commit (`a7a4e9c9`).** Authored detailed commit message with verification evidence and T-01 acceptance reference. Single-file commit (1 file, +3/-1). Popped stash to restore WIP atomically (no merge issues; "Already up to date").

**Phase 17 — T-01 closure planning.** Surfaced closure plan with two sub-paths (proactive close vs. hold for review). User authorized closure 1-3 with two adjustments via `/copy`:
1. Don't optimize for R100 rename (single-purpose closure commit > preserving rename detection)
2. Update reconciliation register at `docs/status/codex-collaboration-reconciliation-register.md` in same commit (it still listed T-01 as `blocking`)

Tight scope: T-01 + register only, NO bundling diagnostic-doc findings (separate concern), NO staging WIP plans file.

**Phase 18 — `git mv` gotcha discovered.** Edited T-01 ticket body in place (added closure section, updated frontmatter status). Then `git mv` to move to closed-tickets/. First diff stat showed `0` net changes for the ticket, but working file had 356 lines (vs 300 staged). **Realized:** `git mv` only updates the index entry's PATH, not the staged blob — my edits were on disk but the staged version was the pre-edit content. Fixed by `git add` on the new path → re-stages content matching working tree. Status flag transitioned `RM` → `R` correctly.

**Phase 19 — Closure commit (`6580d86e`).** 2 files changed, +165/-1: register (added 108 lines for new entry — wait, this is the register's first commit since it was untracked) + ticket renamed-with-modifications (77% similarity per git's detection). Commit message detailed all 6 ACs satisfied + smoke evidence + Options B/E/F follow-up reference.

**Phase 20 — Push of `a7a4e9c9` + `6580d86e`.** User authorized: "Yes. Push `feature/delegate-execution-diagnostic-record` as-is. `a7a4e9c9` and `6580d86e` are a coherent pair: the live smoke artifact landed, T-01 is closed, and the reconciliation register was updated in the same closure commit." Pushed `6a2bb5ae..6580d86e` (fast-forward).

**Phase 21 — Friction-reduction ticket question.** User asked about Options B + E priorities to make sure they don't get forgotten. Recognized this as the register's Maintenance Rule firing ("a closed ticket leaves real follow-on work behind"). Proposed Path A (create ticket + register row + commit + push) vs Path B (memory-only backstop). User authorized Path A.

**Phase 22 — T-20260429-01 ticket creation.** Drafted comprehensive ticket: Context (24-escalation problem), Friction surface 1 (Option B with security boundary analysis), Friction surface 2 (Option E with dynamic gitdir resolution), Friction surface 3 (Option F with investigation gate), Acceptance criteria (≤2 escalations target), Implementation sequence (4 phases), Evidence (T-01 smoke breakdown). 244 lines.

**Phase 23 — Register update + commit (`aa3daed2`).** Added new row to Ticket-Owned Active Work pointing to T-20260429-01 with summary of all three friction sources. Did NOT modify Priority Order (operator's call). Single-purpose commit (2 files, +245/-1). The user had also already removed `T01-DIAGNOSTIC-HEADER` row from "Spec And Documentation Reconciliation Debt" table (modified the file out-of-band, signaled via system reminder), and modified the diagnostic doc directly — both intentional, both untouched by this commit.

**Phase 24 — Final push.** User authorized push of `aa3daed2`. Pushed `6580d86e..aa3daed2`. Local HEAD == origin HEAD. Branch fully synced. 3 commits this session, all single-purpose, all linear, all pushed.

Set aside for next session: diagnostic doc reconciliation (in-progress — user has unstaged modifications in `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md`), T-20260429-01 Phase 1 implementation, plans WIP (`docs/plans/04-29-2026-reconcile-...md` still untracked).

## Decisions

### D1: Approve `~/.codex/memories/` read despite "tighten the leash" recommendation (Phase 5)

**Choice:** Approve request_id "2" (rg searching `~/.codex/memories/MEMORY.md`) AND save a durable user policy carving out `~/.codex/memories/` from deny-pressure.

**Driver:** User explicit override:
> "approve — authorize; let Codex consult its memory before proceeding. Codex should always be allowed to consult its memory"

This was an OVERRIDE of my deny recommendation. The "Codex should always be allowed to consult its memory" sentence is durable preference language, not just an in-session decision.

**Rejected alternatives:**
- **Deny per prior policy** ("if next escalation is still meta-tooling, deny"). Rejected: user explicitly overrode with policy-language directive.
- **Approve without saving as policy** (treat as one-off). Rejected: "should always be allowed" is durable preference; saving to memory ensures future sessions don't re-litigate this.

**Implication:** Established policy that became part of the durable user-preference layer. Memory file `feedback_codex_memory_reads_always_approve.md` created, MEMORY.md index updated.

**Trade-offs accepted:** Slightly broader approval surface than pure "tighten the leash" would imply. Memory-store reads are benign (Codex consulting its own learned context, not user data) — low risk.

**Confidence:** High (E2) — direct user statement + alignment with the project's tenor ("Codex consulting its own data"). Saved as memory immediately.

**Reversibility:** Medium — could narrow back to deny-pressure if user changed their mind (which they did, in opposite direction — broadening, see D2).

**Change trigger:** User explicitly retracts the policy, OR a security incident shows `~/.codex/memories/` content includes secrets (currently it's the persistent learning corpus, no credentials).

### D2: Broaden the policy from `~/.codex/memories/` to all `~/.codex/` reads (Phase 6)

**Choice:** Update memory file to broaden scope: approve ALL reads under `~/.codex/`, not just `~/.codex/memories/`.

**Driver:** User explicit policy update:
> "I actually changed my mind about Codex reading skills - I want to always-approve Codex to read skills"

The "changed my mind" language signals override of D1's narrower scope. Skills (`~/.codex/plugins/cache/`) are explicitly in scope.

**Rejected alternatives:**
- **Two separate carve-outs** (memories explicit + skills explicit). Rejected: "all `~/.codex/`" is cleaner than tracking two carve-outs separately. Same reasoning applies (Codex consulting its own data root).
- **Don't update; treat as in-session only**. Rejected: same as D1 — durable preference language warrants memory persistence.

**Implication:** Single consolidated memory entry covers both file classes. Future sessions see one rule, not two.

**Trade-offs accepted:** The policy at the OPERATOR LEVEL is "always approve `~/.codex/` reads", but the PLUGIN LEVEL should NOT bypass `~/.codex/` wholesale (auth.json, config.toml, history.jsonl are credential paths at mode 0600 — separate analysis in T-20260429-01). So the operator policy and the plugin policy diverge intentionally.

**Confidence:** High (E2) — explicit user statement; saved to memory atomically (Edit failed on string mismatch, recovered with full Write).

**Reversibility:** High — can re-narrow with a single Edit on the memory file.

**Change trigger:** User narrows the policy back, OR the plugin lands the Option B carve-outs (which would make the policy moot for `~/.codex/memories/` and `~/.codex/plugins/cache/` — only other `~/.codex/` reads would remain operator-approval-driven).

### D3: Promote despite opaque `file_change` payload (Phase 10 → 12)

**Choice:** Approve the opaque `file_change` escalations (15, 18) to push the smoke through to terminal state, relying on Gate 1 (review-before-promote) for visibility.

**Driver:** Diagnostic exhaustion. After deny on request 14, Codex retried with the same opaque payload (15) — proving the opacity is STRUCTURAL, not strategic. Continuing to deny would just produce more identical escalations without new information. The smoke needs the file_change → completion → review path validated, not just the deny path.

**Rejected alternatives:**
- **Keep denying until Codex gives up.** Rejected: would produce zero useful information after the first deny; would fail the smoke without validating end-to-end pipeline.
- **Discard the job and re-issue with different objective.** Rejected: starting over costs another full preparation cycle (~24 escalations) and doesn't change the file_change opacity question.
- **Investigate the App Server schema mid-smoke.** Rejected: would pause the smoke for unbounded investigation; better to complete the smoke and investigate Option F as a separate ticket phase.

**Implication:** The smoke completed end-to-end and produced verifiable artifacts. The opacity is documented as Friction surface 3 in T-20260429-01.

**Trade-offs accepted:** Approved escalations without per-escalation visibility. Mitigation: worktree isolation (writes go to delegation worktree, not active branch) + Gate 1 (review-before-promote) — both held safety.

**Confidence:** High (E2) — empirical evidence that deny doesn't surface more detail (request 14 deny → request 15 same payload).

**Reversibility:** N/A — past action. Going forward, the same situation should be approached the same way until Option F is resolved (then per-escalation visibility returns).

**Change trigger:** Option F lands and `file_change` escalations carry meaningful `requested_scope` — at that point per-escalation review is meaningful again.

### D4: Stash WIP rather than commit-as-WIP (Phase 13-14)

**Choice:** `git stash push -u -m "pre-promote: docs reconciliation WIP"` to clear the worktree for promote, then `git stash pop` after promote-and-commit.

**Driver:** User explicit confirmation of intent:
> "I created those files intentionally" + "Yes, proceed with that" (re: stash recommendation)

**Rejected alternatives:**
- **Commit-as-WIP** (option C from my menu). Rejected: pollutes git history with "wip:" commits that need amending later — promise that often goes unfulfilled.
- **Move to /tmp** (option B). Rejected: more invasive than stash; harder to recover if the operator forgets to move back.
- **Add to `.gitignore` temporarily** (option D). Rejected: `.gitignore` is itself tracked; same dirty-tree problem.

**Implication:** Clean separation between the smoke's commit (`a7a4e9c9`) and the operator's WIP. Stash popped cleanly after commit; "Already up to date" — no merge complications. WIP files restored exactly as before.

**Trade-offs accepted:** Two extra git operations (stash + pop) vs. zero git operations for commit-as-WIP. Mitigation: standard git pattern, low cognitive overhead.

**Confidence:** High (E3) — triangulated by: standard git pattern, user explicit authorization, clean execution (no merge issues, files restored byte-perfect).

**Reversibility:** N/A — completed cleanly. Future similar situations: same approach recommended.

**Change trigger:** WIP files are actually ready to commit (then commit them properly instead of stashing). Or workspace's promote check changes to ignore untracked files (then no clearance needed — but that's a plugin design discussion).

### D5: Don't optimize for R100 rename on T-01 closure commit (Phase 17)

**Choice:** `git mv` the ticket file naturally, with body modifications in the same commit. Accept that git's similarity detection will classify it as <100% rename (final result: R 77%).

**Driver:** User explicit guidance:
> "Update the ticket and move it to `closed-tickets/`, but don't optimize for an `R100` rename. Once you edit the body, it is no longer a pure rename, and that is fine. A clean single-purpose closure commit matters more than preserving `R100`."

**Rejected alternatives:**
- **Two-commit closure** (move-only commit at R100, then body-edit commit). Rejected: user explicitly said single-purpose closure commit is preferred.
- **Edit body BEFORE the move via separate commit** (keep ticket at active path with closing notes, then move-only commit). Rejected: same as above — splits the closure into two commits unnecessarily.

**Implication:** The git history shows one coherent closure commit (`6580d86e`) with both the rename and the closing-notes addition. Future readers see `R 77%` in stat — clear signal that this is "rename + significant modification", not pure rename.

**Trade-offs accepted:** Lose the R100 cleanliness. Mitigated by: clean commit message + the rename detection still works (77% > 50% threshold).

**Confidence:** High (E2) — direct user instruction + clean execution.

**Reversibility:** N/A — past commit. Future similar closures should follow the same pattern (closing notes + move in single commit).

**Change trigger:** None — this is established preference now.

### D6: Path A (create ticket) for friction-reduction tracking, not Path B (memory-only) (Phase 21-22)

**Choice:** Create a new ticket T-20260429-01 + register row pointing to it, rather than just saving a memory entry as a backstop.

**Driver:** Multiple factors:
1. The register's Maintenance Rule explicitly says "a closed ticket leaves real follow-on work behind" → immediate-add condition.
2. Project pattern: everything goes in tickets / register (not in floating memory entries).
3. The closure body's mention is acknowledgment, not tracking — it's read once when reviewing closure, then forgotten.
4. User asked: "I want to make sure we don't forget those" — implies wants durable visible tracking.

**Rejected alternatives:**
- **Path B: Memory-only backstop**. Rejected: weaker tracking; wouldn't appear in register or ticket listings; future-Claude wouldn't see it as active work without explicitly checking memory.
- **Add only to register without separate ticket file**. Rejected: register entries point to owning artifacts; without a ticket file, the register entry has nothing to point to.
- **Add to T-01 closure body as "outstanding work" section** (no separate ticket). Rejected: closing T-01 with outstanding work in its body contradicts closure semantics; that work belongs in a successor ticket.

**Implication:** T-20260429-01 is now first-class active work. Future smoke runs measure against its acceptance criterion (≤2 escalations).

**Trade-offs accepted:** More upfront work (ticket draft, register edit, separate commit) vs. minimal-touch memory entry. Mitigated by: T-20260429-01 is now durable across all future sessions; memory entries can be missed or expire.

**Confidence:** High (E3) — register's Maintenance Rule + user's "don't forget those" directive + project pattern of formal ticket tracking.

**Reversibility:** Medium — could close the ticket if the user decides not to pursue B/E/F. But the cost of having a tracked-but-unaddressed ticket is low; the cost of forgotten-because-untracked work is high.

**Change trigger:** User decides Options B/E/F aren't worth pursuing → close the ticket as `won't-fix` with rationale.

### D7: Narrow `~/.codex/` carve-out for the plugin (memories + plugins/cache/ only, NOT all `~/.codex/`) — design recommendation in T-20260429-01

**Choice:** Recommend Option B as a narrow carve-out: extend `readableRoots` with `~/.codex/memories/` and `~/.codex/plugins/cache/` only, NOT all of `~/.codex/`.

**Driver:** Security investigation in Phase 11. `~/.codex/` contains:
- `auth.json` (mode 0600 — OAuth/API credentials)
- `config.toml` (mode 0600 — possibly contains API keys)
- `history.jsonl` (mode 0600 — 433 KB of prior conversations)
- `state_5.sqlite`, `logs_2.sqlite` — session DB and logs

The OS-level 0600 mode is a deliberate restriction; the plugin must preserve it.

**Rejected alternatives:**
- **Add all of `~/.codex/` to `readableRoots`**. Rejected: would expose credentials and conversation history; defeats the OS-level 0600 protection at the plugin layer.
- **No plugin change; rely only on operator policy**. Rejected: 24-escalation friction is real; per-escalation approval for a durable policy is friction without security value.
- **Env-tunable carve-out** (operator opt-in via env var). Rejected: over-engineered for current need; defer until a second carve-out request comes (mirrors the env-tuning pattern from `cd0f2142` but premature here).

**Implication:** T-20260429-01's Phase 1 implementation must include the security-boundary preservation as an explicit acceptance criterion (which it does — AC #2 requires probe verification that auth.json etc. remain blocked).

**Trade-offs accepted:** Two specific carve-outs to maintain (memories + plugins/cache) instead of single broader entry. Mitigated by: matches the access patterns observed in T-01's smoke (no other `~/.codex/` reads were attempted).

**Confidence:** High (E2) — investigated `~/.codex/` directory contents directly, identified credential paths via `stat -f "%Sp"` mode check.

**Reversibility:** Medium — broadening or narrowing the carve-out is a single-line policy change; would touch `runtime.py:46-57` + `test_runtime.py:178`.

**Change trigger:** A future Codex version stores credentials elsewhere (then `~/.codex/auth.json` etc. become safe to read), OR a different access pattern emerges that the narrow carve-out doesn't cover.

## Changes

### `packages/plugins/codex-collaboration/server/delegation_controller.py` — Pyright unreachable suppression (smoke artifact, commit `a7a4e9c9`)

**Purpose:** Silence the Pyright "unreachable code" hint at the `case _: assert_never(outcome)` arm in `DelegationController._wait_for_park_capture`, while preserving the `assert_never` runtime guard.

**Approach:** Add `# pyright: ignore[reportUnreachable]` to the `assert_never` line + 2-line comment justifying why the suppression is intentional.

**Key implementation details:**
- Line 942 area: original `assert_never(outcome)` becomes `assert_never(outcome)  # pyright: ignore[reportUnreachable]`
- Comment added (2 lines): "Pyright proves ParkedCaptureResult exhaustive here, but keep / assert_never as a runtime tripwire for future union extension."
- Net diff: +3/-1 (3 added lines, 1 removed)
- New assertion location: `delegation_controller.py:944` (was `:942` before the comment insertion shifted it)

**Commit:** `a7a4e9c9` — `chore(codex-collaboration): silence pyright unreachable hint on assert_never arm` (1 file, +3/-1). Verification: pyright clean (0 issues), focused pytest 2/2 passed. **PRODUCED VIA LIVE `/delegate` SMOKE** (job `4586c6c3-39cb-49ff-815b-620d7f3212c9`, artifact_hash `d26a0b22...`, promoted via `verified` state).

### `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` → `docs/tickets/closed-tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` — T-01 closure (commit `6580d86e`)

**Purpose:** Close T-20260423-01 with full closure section recording job/artifact/criteria evidence and operational findings.

**Approach:** Update frontmatter `status: open` → `status: closed` with `closed_at` and `closed_via` fields. Append "## Closure (2026-04-29)" section with smoke evidence table, all 6 acceptance criteria checked off with substantiation, operational findings (24-escalation breakdown, Options B/E/F follow-up), and references. `git mv` to closed-tickets/.

**Key implementation details:**
- Frontmatter: added `closed_at: 2026-04-29` and `closed_via: a7a4e9c9` fields
- Closure section: ~57 added lines covering smoke evidence (job ID, base commit, artifact hash, promotion attempts, closing commit, changed file), all 6 ACs with substantiation, operational findings (3 friction sources with escalation count attribution), references
- Move + edit handled via `git mv` then re-`git add` (gotcha: `git mv` doesn't restage content — see Gotchas section)
- Final stat: 77% similarity (rename + significant modification)

**Commit:** `6580d86e` — `chore(codex-collaboration): close T-01 delegate execution remediation` (2 files: this rename + register update; +165/-1 total).

### `docs/status/codex-collaboration-reconciliation-register.md` — register update for T-01 closure (commit `6580d86e`) AND for T-20260429-01 opening (commit `aa3daed2`)

**Purpose:** Keep the active-work view of the register in sync with both T-01's closure and T-20260429-01's opening.

**Approach:** Two separate edits in two separate commits.

**Key implementation details (commit `6580d86e` edit):**
- Removed `T-20260423-01` row from "Ticket-Owned Active Work" table (it was the first row)
- Removed item 1 from "Current Priority Order" ("Complete the post-restart live `/delegate` smoke for `T-20260423-01`") and renumbered remaining 1-3
- File was untracked at the start (the user created it earlier this morning during separate work) — this commit is its first git tracking; 108 added lines

**Key implementation details (commit `aa3daed2` edit):**
- Added new `T-20260429-01` row to "Ticket-Owned Active Work" table (after `T-20260416-01`) with summary of all three friction sources and exit condition
- Did NOT modify Priority Order (operator's call)
- Net change: 1 line added (new row appended), 1 line modified (the prior row's text was preserved as part of the Edit's old_string match)

**Commits:** `6580d86e` (initial creation + T-01 row removal) and `aa3daed2` (new T-20260429-01 row). Note: between these two commits, the user modified the register out-of-band (removed `T01-DIAGNOSTIC-HEADER` row from "Spec And Documentation Reconciliation Debt" table — visible in the Read I did before the second edit). My second commit preserved that user edit.

### `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md` (new) — T-20260429-01 ticket (commit `aa3daed2`)

**Purpose:** Track the three plugin-level friction sources surfaced by T-01's smoke as a successor ticket with measurable acceptance criteria.

**Approach:** New ticket file following T-01's structure (frontmatter + Context + Defect-style "Friction surface" sections + Acceptance criteria + Implementation sequence + Evidence). 244 lines.

**Key implementation details:**
- Frontmatter: `id: T-20260429-01`, `status: open`, `priority: medium`, `effort: small`
- Context: 24-escalation problem framing
- Friction surface 1 (Option B): `~/.codex/` reads — observed behavior (4 escalations), security boundary analysis (auth.json/config.toml/history.jsonl exclusion rationale), implementation (narrow carve-outs only)
- Friction surface 2 (Option E): worktree `.git` cross-pointer reads — ripgrep/git friction (~7 escalations), implementation (dynamic gitdir resolution at delegation-start time)
- Friction surface 3 (Option F): file_change escalation payload opacity — observed empty `requested_scope`, deny-doesn't-help diagnostic, investigation gate (App Server response shape, plugin handler trace, vendored schemas), implementation (conditional on findings)
- Acceptance criteria: 4 items, anchored on "comparable smoke run with ≤2 operator escalations" measurement
- Implementation sequence: 4 phases (B+E together, then F investigation, then F implementation, then acceptance smoke)
- Evidence: T-01 smoke breakdown (job ID, escalation count, approximate per-class breakdown), source locations table

**Commit:** `aa3daed2` — `chore(tickets): track T-20260429-01 codex-collaboration delegation friction reduction` (2 files: this + register update; +245/-1).

### `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_codex_memory_reads_always_approve.md` — durable user policy on `~/.codex/` reads (NOT committed; user-private memory)

**Purpose:** Persist the user's policy "always approve Codex reads under `~/.codex/`" across all future sessions.

**Approach:** Two-step evolution within this session:
1. **Initial save (Phase 5):** Narrow scope — only `~/.codex/memories/` carve-out; deny-pressure still applies to `~/.codex/plugins/cache/`. Filename: `feedback_codex_memory_reads_always_approve.md`.
2. **Broadening (Phase 6):** Replaced with broader policy — all `~/.codex/` reads (memories + plugins/cache + any other subpaths). Filename unchanged for simplicity (description and content updated).

**Key implementation details:**
- Frontmatter `name`/`description` updated to reflect broadened scope
- Body explains why (Codex consulting its own data root) AND security boundary distinction (operator-policy vs plugin-policy: operator approves all `~/.codex/`, but plugin shouldn't bypass `auth.json` etc.)
- "How to apply" section gives concrete guidance for future Claude
- Notes that this supersedes an earlier narrower version
- MEMORY.md index updated with one-line entry

### `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/MEMORY.md` — index entry update

**Purpose:** Surface the new feedback memory in the always-loaded memory index.

**Approach:** Edit the Feedback section to add a new bullet pointing to `feedback_codex_memory_reads_always_approve.md` with one-line summary.

**Key implementation details:** Single bullet under "Feedback" section: `- [Always allow Codex to read from its own data root](feedback_codex_memory_reads_always_approve.md) — Approve all delegation escalations reading under \`~/.codex/\` ...`

## Codebase Knowledge

### Files read this session

| File | Why read | Understanding gained |
|------|----------|----------------------|
| `packages/plugins/codex-collaboration/server/runtime.py:1-80` | Investigate plugin policy structure for Option B/E feasibility analysis | `build_workspace_write_sandbox_policy` at line 23-58 builds the v1 sandbox policy; `readableRoots` at line 51 is the relevant field; `includePlatformDefaults: True` (line 52) is the Candidate A patch; `excludeSlashTmp: True` and `excludeTmpdirEnvVar: True` block `/tmp` access (relevant to escalation #19 where Codex used `TMPDIR=$PWD/.tmp` workaround) |
| `~/.codex/` directory listing | Security investigation for Option B carve-out scope | Found credential-class files at mode 0600: `auth.json` (4249 bytes, OAuth/API credentials), `config.toml` (6856 bytes, possibly API keys), `history.jsonl` (433296 bytes, conversation history). Also non-credential subdirs: `memories/` (Codex learning corpus), `plugins/cache/` (skill catalog with namespaces local/local-personal/openai-bundled/openai-curated/openai-primary-runtime), `cache/` (uv + codex_apps_tools — build/install caches) |
| `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` | Reference for closure section structure + AC list | T-01 ticket structure: title + frontmatter + Context + Defect 1/2 sections + Interaction + ACs + Implementation sequence + Evidence. 6 acceptance criteria. Used as template for T-20260429-01. |
| `docs/status/codex-collaboration-reconciliation-register.md` | Plan T-01 row removal + T-20260429-01 row addition | Register structure: Authority + State Vocabulary + Current Priority Order + Ticket-Owned Active Work table + Residual Carry-Forward Debt + Benchmark-Carried Follow-On Work + Spec And Documentation Reconciliation Debt + Open Spec Questions + Intentional Future-Scope Deferrals + Maintenance Rule. Each row has columns: ID / State / Owning artifact / Current truth / Exit condition. State vocabulary: blocking/open/drift/missing-artifact/deferred (no "closed" — closed work is removed from active tables). |
| `~/.claude/projects/.../memory/MEMORY.md` | Update index entry for new feedback policy memory | Memory index uses one-line bullets per entry under sectioned headings (Project / Feedback / Key References). Format: `- [Title](filename.md) — one-line summary` |
| `~/.claude/projects/.../memory/feedback_codex_memory_reads_always_approve.md` (re-read after Edit failure) | Recover from string-mismatch on broadening Edit | Memory file frontmatter has `originSessionId` field added by harness automatically; my initial Write didn't include it but the harness added it; subsequent Edit needed to handle that |
| Smoke artifacts: `inspection/full.diff`, `inspection/test-results.json`, `inspection/changed-files.json` | Render smoke review per skill step 6e | Artifact format: full.diff is unified diff format (single-file +3/-1); test-results.json has fields `commands`, `schema_version`, `status`, `summary`; changed-files.json has `changed_files` array with file paths |

### Architecture: codex-collaboration plugin escalation lifecycle (mapped this session)

| Phase | Status | pending_escalation | Operator action |
|---|---|---|---|
| Job started | `running` | null | Wait or poll |
| Codex needs unsanboxed action | `needs_escalation` | populated | `/delegate approve|deny` |
| Decision dispatched | `running` (transient consuming window) | suppression sentinel | Bounded poll, suppress sentinel |
| Worker advances to next state | `running` OR `needs_escalation` (next request_id) | null OR populated | Continue cycle |
| Codex completes objective | `completed` | null | Trigger materialization via poll |
| Artifacts materialized | `completed` + `promotion_state: pending` | null, `artifact_hash` populated | Render review (Gate 1), then `/delegate promote` |
| Promote attempted, prechecks fail | `completed` + `promotion_state: prechecks_failed` | null | Resolve blocking condition, retry promote |
| Promote succeeds | `completed` + `promotion_state: verified` | null | Verify in primary workspace |

### Codex App Server escalation kinds (observed this session)

| Kind | `requested_scope` shape | Operator visibility |
|---|---|---|
| `command_approval` | Has `command`, `commandActions`, `cwd`, `proposedExecpolicyAmendment`, `reason` | Full — operator sees the exact command |
| `file_change` | **EMPTY** (`grantRoot: null`, `reason: null`) — no `file_path`, `change_type`, or `diff` | **OPAQUE** — operator cannot see what file/change before approving |
| `request_user_input` | (Not encountered this session) | Per skill: `answers` field with question identifiers |

### Codex preparation cycle pattern (observed in T-01 smoke)

Codex appears to load context aggressively before attempting the actual edit. The 24 escalations broke down approximately as:
- **Skill stack load** (~3-4 escalations): reads `verification-before-completion`, `using-superpowers`, `test-driven-development` SKILL.md from `~/.codex/plugins/cache/`
- **Memory consult** (~3-4 escalations): reads `~/.codex/memories/MEMORY.md` for prior context relevant to objective
- **In-worktree discovery** (~5-6 escalations): rg-based searches for source location, conventions, project config (`pyrightconfig*.json`, `package.json`, `pyproject.toml`)
- **Tool availability probes** (~2 escalations): Python `shutil.which()` for `pyright`/`basedpyright`/`uv`/`trash`
- **Verification** (~2 escalations): pyright runs (pre-edit baseline + post-edit verify), focused pytest selection
- **File writes** (~2 escalations): opaque `file_change` for the actual edit + a second related write
- **Artifact prep** (~2 escalations): `git diff` with TMPDIR workaround for the policy-blocked /tmp access

### Test conventions (codex-collaboration) — confirmed pattern from prior sessions

| Convention | Example | Source |
|---|---|---|
| Import path: `from server.<module>` | `from server.runtime import build_workspace_write_sandbox_policy` | `tests/test_runtime.py`; pyproject `pythonpath = ["."]` |
| Test class pattern: `TestXxx` for grouping | `TestModelDetection`, `TestRunTurnEffort` | Existing tests directory structure |
| Focused tests: `test_<area>_<focus>.py` | `test_delegation_decision_result_shape.py`, `test_delegate_start_async_integration.py` | Existing tests directory structure |

### Plugin process structure (re-confirmed this session)

| Layer | PID (this session) | Role | Lifecycle |
|---|---|---|---|
| Claude Code | 46669 | Plugin host; spawns plugin processes | Long-lived per Claude Code session |
| `uv run` wrapper | 46757 | Resolves plugin venv; executes bootstrap script | Long-lived child of Claude Code |
| Plugin Python MCP server | **46796** | Holds module table for `delegation_controller.py`, `runtime.py`, etc.; exposes JSON-RPC over stdio | Long-lived child of uv wrapper |
| Plugin data root | (filesystem) | `~/.claude/plugins/data/codex-collaboration-inline/` — JSONL stores | Persistent across plugin restarts |
| Codex App Server | (per-delegation) | Spawned by plugin per-delegation; enforces sandbox policy | Per-delegation, terminates with job |

### Key locations (post-this-session)

| Concept | Location |
|---|---|
| Pyright suppression (smoke artifact) | `packages/plugins/codex-collaboration/server/delegation_controller.py:944` |
| Sandbox policy builder | `packages/plugins/codex-collaboration/server/runtime.py:23-58` |
| Sandbox policy regression test | `packages/plugins/codex-collaboration/tests/test_runtime.py:178` |
| T-01 closed ticket | `docs/tickets/closed-tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` |
| T-20260429-01 active ticket | `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md` |
| Reconciliation register | `docs/status/codex-collaboration-reconciliation-register.md` |
| User memory: `~/.codex/` policy | `~/.claude/projects/.../memory/feedback_codex_memory_reads_always_approve.md` |

### Patterns identified (refined this session)

- **`git mv` doesn't restage content** — see Gotchas. The standard `git mv` workflow when files are also being modified: edit → `git mv` → `git add new-path` (re-stages content).
- **Pre-promote stash pattern for intentional WIP** — `git stash push -u -m "<reason>"` → promote → commit → `git stash pop`. Cleaner than commit-as-WIP for files not ready for commit.
- **Codex's preparation depth scales with skill-stack reach** — the smoke loaded 3+ skill SKILL.md files before attempting the edit. Each skill load = 1 escalation under current policy. Option B carve-out reduces this to 0.
- **Bounded poll loop with suppression sentinel** — post-decide poll suppresses results matching the just-decided request_id (consuming window) and routes the first different-state observation through the state router. Critical for not re-rendering already-decided escalations as new prompts.
- **`promotion_state` persistence** — `prechecks_failed` persists on the job model after a failed promote attempt; subsequent successful promote transitions through this state but increments `promotion_attempt`. Useful for recovery diagnostics.

### Surprising findings (this session)

- **`file_change` escalation has empty `requested_scope` payload** — operator can't see file path, change type, or diff before deciding. Confirmed structural via deny experiment (request 14 deny → request 15 same payload). Logged as Option F investigation in T-20260429-01.
- **`worktree_dirty` includes untracked files** — the plugin's promotion precheck blocks even on untracked files unrelated to the diff being applied. Conservative-but-correct safety; resolved here via stash.
- **`git mv` followed by Edit-tool-equivalent doesn't restage content** — caught by diff-stat showing 0 net change despite obvious content additions. Required explicit `git add` after `git mv` to refresh the staged blob.
- **Stale `advisory_runtime` flag on promote response** — `stale_advisory_context: true` returned by `codex.delegate.promote` indicates Codex's advisory-runtime view of repo state is now out of date because the file was just modified. Informational, not an error.
- **Codex's `TMPDIR=$PWD/.tmp` workaround for the `excludeSlashTmp: True` policy** — Codex actively adapts to sandbox boundaries by routing tmp access to in-worktree subpaths. Pattern to remember for future plugin design.

## Context

### Project state (post-session)

| Item | State |
|---|---|
| Branch | `feature/delegate-execution-diagnostic-record` at `aa3daed2` (in sync with origin) |
| Commits this session | `a7a4e9c9`, `6580d86e`, `aa3daed2` (3 commits, all pushed) |
| Total commits on branch | 10 (7 from prior session + 3 from this) |
| T-20260423-01 (T-01) | **CLOSED** at `closed-tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` |
| T-20260429-01 | **OPEN** at `tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md` (Phase 1: Options B+E sandbox carve-outs; Phase 2: Option F investigation; Phase 3: Option F implementation; Phase 4: acceptance smoke) |
| Reconciliation register | Reflects current state: T-01 row removed, T-20260429-01 row added; user separately removed `T01-DIAGNOSTIC-HEADER` row out-of-band |
| Working tree | 1 modified file (`docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — user's in-progress doc-rot reconciliation), 1 untracked (`docs/plans/04-29-2026-reconcile-...md` — earlier WIP) |
| Memory | New file `feedback_codex_memory_reads_always_approve.md`; MEMORY.md index updated |

### Mental model

**The branch's narrative arc has graduated from "engineering complete + awaiting validation" to "validation complete + follow-up tracked":**

1. **Diagnostic schema phase** (pre-prior-session): Run record scaffolding, App Server schema bundle captured.
2. **Diagnostic findings phase** (prior-prior session): att1+att2+att3 + 3 security probes; closure record drafted.
3. **Closure landing + hygiene phase** (prior session, commits 1-3): Reviewer fixes applied; closure committed; context-metrics fix and ticket archives also landed.
4. **Engineering action phase** (prior session, commit 4): Candidate A sandbox policy promoted in production code.
5. **Carry-forward improvements phase** (prior session, commits 5-7): T-07 plan reconciled, env-tuning landed, App Server enforcement mechanism documented in source.
6. **Live validation phase** (THIS session, commit 8 = `a7a4e9c9`): Live `/delegate` smoke produced and promoted the Pyright suppression artifact, validating Candidate A end-to-end.
7. **Closure phase** (THIS session, commit 9 = `6580d86e`): T-01 closed with full acceptance evidence; reconciliation register synced.
8. **Successor tracking phase** (THIS session, commit 10 = `aa3daed2`): T-20260429-01 opened with Options B/E/F as Phase 1-3.

**What remains (next-session work):**

9. **Diagnostic doc reconciliation phase** (in progress per user's working-tree state): Reconcile contradictions in `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — was the next target user explicitly flagged.
10. **T-20260429-01 implementation** (open ticket): Phase 1 (Options B+E) → Phase 2 (Option F investigation) → Phase 3 (Option F implementation) → Phase 4 (acceptance smoke).

**Key insight:** The smoke functioned as both validation AND a cost benchmark. The 24-escalation count (vs expected ~3-5 for a 1-line edit) is itself a measurable signal — T-20260429-01's acceptance criterion ("comparable smoke run with ≤2 escalations") makes the friction reduction quantifiable.

### Environment

- Working tree: `feature/delegate-execution-diagnostic-record` at `aa3daed2` (in sync with origin)
- Codex CLI: 0.125.0
- App Server version: `codex_collaboration/0.125.0 (Mac OS 26.4.1; arm64) kitty (codex_collaboration; 0.1.0)`
- Local timezone: EDT (-0400)
- Plugin process structure: Claude Code (PID 46669) → uv wrapper (PID 46757) → venv Python MCP server (PID 46796) — all freshly restarted at session start
- Plugin data root: `~/.claude/plugins/data/codex-collaboration-inline/`
- Smoke job's plugin data: `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/4586c6c3-39cb-49ff-815b-620d7f3212c9/`
- Model: `claude-opus-4-7[1m]`
- macOS Darwin 25.4.0; shell zsh
- Authoritative state: `auth_status: authenticated`, no `delegation_status_error`, no errors

## Learnings

### `git mv` only restages the path, not the content

**Mechanism:** `git mv old new` is essentially `mv old new && git add new && git rm old`. But the `git add new` step re-targets the existing index entry to the new path — it does NOT rehash the working tree's current content. If the file was modified before the `git mv`, the staged blob remains the pre-modification version.

**Evidence:** This session, after editing T-01 ticket body and running `git mv`, `git diff --cached --numstat` showed `0  0` for the moved file despite ~60 added lines visible in the working tree. `git show :<new-path> | wc -l` showed 300 (pre-edit) vs working file 356. Fixed by `git add <new-path>` to re-hash and re-stage.

**Implication:** When editing-and-moving a file in the same logical change, the workflow MUST be: edit → `git mv` → `git add <new-path>` (the third step is the load-bearing one). Or: `git mv` first → edit → `git add <new-path>` (which avoids the gotcha entirely but is less natural for in-place edits).

**Watch for:** `git status` shows `RM` (renamed + modified) when working tree differs from staged content at the new path — that's the signal. If it shows just `R`, content matches.

### `worktree_dirty` blocks promote even on untracked files unrelated to the diff

**Mechanism:** The codex-collaboration plugin's promote precheck calls `git status --porcelain` (or equivalent) and treats any non-empty output as `worktree_dirty`. This includes untracked files that have no relationship to the diff being applied.

**Evidence:** This session, `/delegate promote` rejected with `reason: "worktree_dirty"` when only `docs/plans/04-29-2026-...md` and `docs/status/` were untracked — neither related to the `delegation_controller.py` diff being applied.

**Implication:** Operators may need to stash or stage unrelated files before promote. Standard workaround: `git stash push -u -m "..."` → promote → `git stash pop`.

**Watch for:** This is conservative-but-correct safety (prevents mixing operator's in-progress work with delegated changes during review). T-20260429-01 doesn't propose changing this — the workaround is fine.

### `prechecks_failed` is a recoverable promotion state

**Mechanism:** When `/delegate promote` fails a precheck (like `worktree_dirty`), the job's `promotion_state` transitions from `pending` → `prechecks_failed`. The job remains promotable from this state — resolving the blocking condition and re-promoting transitions to `verified`. The `promotion_attempt` counter increments per attempt.

**Evidence:** This session: attempt 1 (worktree dirty) → `prechecks_failed`; cleared via stash; attempt 2 → `verified`. `promotion_attempt: 2` in the verified response.

**Implication:** Operators don't need to discard-and-restart on prechecks_failed. Just resolve the issue and retry. Skill Tier 3 router correctly handles this state ("Resolve the blocking condition, then retry").

**Watch for:** Other prechecks (besides worktree_dirty) likely surface here too. The skill renders prechecks_failed without a specific reason because the rejection reason is returned at failure time and not persisted on the job model — operators must remember the failure reason between attempts.

### Codex's preparation depth is comprehensive but addressable via plugin policy

**Mechanism:** Codex loads its skill stack and consults its memory store before attempting work. Each load is a separate escalation under current policy because `~/.codex/` is outside `readableRoots`. The result: 24-escalation count for a 1-line edit.

**Evidence:** This session's smoke breakdown (~7 escalations from `~/.codex/` reads + ~7 from in-worktree git friction + ~3 opaque file_change + ~7 legitimate verification operations).

**Implication:** Plugin policy changes (Options B+E in T-20260429-01) eliminate the friction sources without changing Codex's behavior. Acceptance criterion measures this directly: ≤2 escalations on a comparable run.

**Watch for:** Codex's preparation is a feature, not a bug. The plugin's job is to make benign preparation cheap (no operator approval needed for `~/.codex/` reads or worktree git metadata) while keeping risky operations (writes outside the worktree, network access, sensitive-host-path reads) operator-gated.

### File-class distinction within `~/.codex/` (memories/skills vs credentials)

**Mechanism:** `~/.codex/` contains a mix of file classes:
- **Codex's own data** (memories, skill cache): benign, Codex consulting its own learned context
- **Credentials and conversation history** (auth.json, config.toml, history.jsonl): mode 0600, OS-level restricted

**Evidence:** Direct inspection via `ls -la ~/.codex/` and `stat -f "%Sp"` mode check. `auth.json` is 4249 bytes mode 0600 (OAuth tokens). `history.jsonl` is 433KB mode 0600 (conversation history).

**Implication:** Operator policy ("always approve `~/.codex/` reads") and plugin policy (carve-out only specific subpaths) MUST diverge. Operator-policy is about workflow trust; plugin-policy must preserve the OS-level credential boundary.

**Watch for:** When implementing T-20260429-01 Phase 1, the carve-out MUST be `~/.codex/memories/` + `~/.codex/plugins/cache/` only — NOT all of `~/.codex/`. The acceptance criterion includes a security probe to verify auth.json/config.toml/history.jsonl/sessions/ remain blocked.

### `disambiguation rule` for `/delegate approve` with trailing text

**Mechanism:** The skill's grammar disambiguation rule says any trailing text after `approve` should reject with escape guidance. But user routinely sends `/delegate approve — authorize` style commands with brief comments.

**Evidence:** Multiple instances this session (escalations 5, 6, 7, 12, 13, 16, 17, etc.) — user pasted `/delegate approve` plus narrative reasoning via `/copy`. Strict skill interpretation would reject; pragmatic interpretation processes as approve.

**Implication:** Treat trailing narrative text as commentary, not as part of an objective. Note the rule once per session for awareness, then proceed with clear-intent interpretation. Do NOT silently re-interpret if intent is genuinely ambiguous (e.g., user might have meant to start a new delegation).

**Watch for:** If the user ever sends something like `/delegate approve the deletion of X` mid-delegation, that IS ambiguous (could be approve + comment, or could be a stray new-delegation start). In ambiguous cases, ask for clarification rather than guessing.

## Next Steps

### 1. New session: `/handoff:load`

Picks up THIS handoff and archives it.

### 2. Diagnostic doc reconciliation (in-progress, user's flagged next target)

User has unstaged modifications in `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md`. Per the register's prior `T01-DIAGNOSTIC-HEADER` row (now removed by user, suggesting they're addressing it directly): "the run record header still says the engineering action is pending even though Candidate A policy promotion has already landed." The exit condition was: "Reconcile the header language to the landed state or explicitly mark the line as historical context."

User flagged this as the next target after T-01 push. Continue from their unstaged work.

### 3. T-20260429-01 Phase 1: Sandbox carve-outs (Options B + E)

Per the new ticket's Implementation sequence:
- Modify `packages/plugins/codex-collaboration/server/runtime.py:46-57` to extend `readableRoots` with:
    - `Path.home() / ".codex" / "memories"` (Option B)
    - `Path.home() / ".codex" / "plugins" / "cache"` (Option B)
    - Dynamic resolution of worktree's gitdir target (Option E) — read the worktree's `.git` file content at delegation-start, parse for `gitdir: <path>` line, add target to `readableRoots`
- Update `packages/plugins/codex-collaboration/tests/test_runtime.py:178` regression assertion to match the new shape (will need parameterization for the dynamic gitdir path)
- Verify with security probe: confirm `~/.codex/auth.json`, `~/.codex/config.toml`, `~/.codex/history.jsonl`, `~/.codex/sessions/` remain blocked
- Land in single commit (same surface, same test surface)

### 4. T-20260429-01 Phase 2: file_change opacity investigation (Option F gate)

Per the ticket's investigation gate:
1. Inspect App Server's actual JSON-RPC response for `applyPatchApprovalRequest` (or equivalent file-change-class request method)
2. Trace `_server_request_handler` (or equivalent in `delegation_controller.py`) for file-change-class requests
3. Check vendored schemas at `tests/fixtures/codex-app-server/0.117.0/`

Determine: is the data in the App Server response (plugin gap) or not (App Server limitation)?

### 5. T-20260429-01 Phase 3: file_change opacity implementation (conditional)

Based on Phase 2 findings:
- If data available: extend escalation rendering to surface `file_path`, `change_type`, diff preview
- If data not available: document as upstream limitation; possibly add opt-in operator-side preflight (e.g., `git diff HEAD` against worktree)

### 6. T-20260429-01 Phase 4: Acceptance smoke

Run a comparable small-edit `/delegate` smoke. Record escalation count. If ≤2, AC #1 satisfied. If higher, decompose remaining friction sources.

### 7. (Optional) Other open tracking items in register

- **T-20260423-02** (`drift`): Rewrite to current truth; Packet 1 is landed; amendment-admission follow-up premise no longer valid
- **T-20260416-01** (`open`): Land the dialogue reply-path extraction fix; benchmark closeout no longer blocks
- **DELIVERY-ROLLOUT-PROFILE** (`drift`): Rewrite spec's R1/R2 Deployment Profile block to reflect implemented surfaces
- **T16-BLOCKER-MODEL** (`drift`): Update T-20260416-01 ticket body to remove benchmark-defer language
- **REWRITE-MAP-CONSULT-QUESTION** (`drift`): Update spec to reference resolved decision

### 8. (Optional) Stash plans WIP commit/disposition

`docs/plans/04-29-2026-reconcile-active-stale-codex-collaboration-artifacts-to-current-repo-truth.md` is still untracked from earlier today. Per its content, it's a docs reconciliation plan covering 8 artifacts. Could be committed as separate concern when ready, or refined further before commit.

### 9. (Optional) Schedule background agent for T-20260429-01 progress check

Mentioned this in the session — could `/schedule` an agent in 1-2 weeks to check whether Phase 1 has landed yet and surface a status report. User didn't authorize; held off.

## In Progress

**Clean stopping point at session boundary** — but the user has separate in-progress work in the working tree that's preserved untouched.

- Disk: 3 commits pushed to origin; HEAD `aa3daed2` matches upstream
- Working tree:
    - 1 modified file: `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` (user's diagnostic doc reconciliation work in progress)
    - 1 untracked file: `docs/plans/04-29-2026-reconcile-active-stale-codex-collaboration-artifacts-to-current-repo-truth.md` (user's earlier WIP from this morning)
- T-01: closed and committed; ticket at `closed-tickets/`
- T-20260429-01: opened and committed; ticket at active path; ready for Phase 1 implementation
- Memory: feedback policy file saved and indexed
- All session work completed; handoff in flight

## Open Questions

- **What's the exact gitdir resolution mechanism for Option E?** Need to read the worktree's `.git` file at delegation-start; the file has format `gitdir: <absolute path>`. Need to handle the case where the file doesn't exist yet at policy-build time (early failure path).
- **Will `~/.codex/cache/` be needed in the carve-out?** Currently has `codex_apps_tools/` and `uv/` (build/install caches). T-01's smoke didn't access these. Holding for now; add to carve-out only if a future smoke shows access.
- **Does the Codex App Server's `applyPatchApprovalRequest` response include file path/change type/diff?** Phase 2 investigation gate for Option F.
- **Should `~/.codex/scripts/` or other top-level subdirs be carved out?** Inspection showed `~/.codex/` has many subdirs (rules, references, scripts, dist, vendor_imports, etc.). Codex didn't access these in T-01 smoke; holding for now.
- **Is the `worktree_dirty` precheck too conservative?** It blocks on untracked files unrelated to the diff. The workaround (stash) is acceptable but could be relaxed to "block only if the diff would touch a tracked-modified or untracked file at the same path". Out of scope for T-20260429-01; would be a separate enhancement.
- **What's the right way to handle the diagnostic doc reconciliation?** User has unstaged work; depending on scope, may be one commit or multiple. User flagged it as the next target — they'll likely drive scope decisions.

## Risks

### T-20260429-01 Phase 1 might hit `test_runtime.py` parameterization complexity

**Concern:** The current regression test (`test_runtime.py:178`) pins the EXACT policy shape via dict equality. Adding dynamic gitdir resolution (Option E) means the test needs to either parameterize over a fake gitdir path or mock the resolution function. This is more complex than the simple bool flip from Candidate A.

**Mitigation:** Use pytest parameterization with a fixture that provides a known fake gitdir path. The policy builder can take an optional `gitdir_resolver: Callable[[Path], Path | None]` parameter for testability, defaulting to the production resolver.

### Option B carve-out could expand if Codex's data layout changes

**Concern:** If a future Codex CLI version adds more subdirectories under `~/.codex/` that delegation needs to read, the carve-out won't cover them, and we'll see escalations again. The narrow-carve-out approach trades less-future-proof for tighter security boundary.

**Mitigation:** When this happens, the operator's "always approve `~/.codex/` reads" policy still applies at the per-escalation level — work continues, just with more friction. Add the new subpath to the carve-out reactively. The plugin code change is one line per addition.

### Diagnostic doc reconciliation could expose more drift than expected

**Concern:** The `T01-DIAGNOSTIC-HEADER` row in the register suggested header language drift; but the diagnostic doc is large (~1458 lines per prior handoff) and may have other internal contradictions beyond the header. User's in-progress work might surface these.

**Mitigation:** Start with the header (the explicit drift item) and let user steer scope from there. Don't pre-emptively rewrite the whole doc.

### `git mv` re-stage gotcha could trip up future Claude

**Concern:** This session caught the issue via diff-stat sanity check. But future Claude editing a file then `git mv`-ing might miss the gap between staged and working content if the diff stat isn't checked.

**Mitigation:** This handoff documents the pattern in Learnings. Consider also: a safer pattern is `git mv` first (filesystem move, clean staged state), then edit, then `git add` — avoids the gotcha entirely. Will adopt this pattern going forward.

### Memory file contradiction risk if user changes policy again

**Concern:** The "always approve `~/.codex/` reads" policy was broadened from narrower scope mid-session. If the user changes their mind again (e.g., re-narrows after seeing security implications more clearly), the memory file would need re-update. Stale memory could mislead future Claude.

**Mitigation:** The memory file body explicitly notes "This supersedes an earlier narrower version" — sets a precedent that the file is the canonical current state. If user updates policy, update the memory file in the same conversation (don't defer).

## References

### Files (this session's modifications)

- `packages/plugins/codex-collaboration/server/delegation_controller.py` — Pyright suppression at line 944 (commit `a7a4e9c9`)
- `docs/tickets/closed-tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` — T-01 closed with closure section (commit `6580d86e`)
- `docs/status/codex-collaboration-reconciliation-register.md` — T-01 row removed in `6580d86e`; T-20260429-01 row added in `aa3daed2`
- `docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md` — T-20260429-01 opened (commit `aa3daed2`)
- `~/.claude/projects/.../memory/feedback_codex_memory_reads_always_approve.md` — durable user policy on `~/.codex/` reads (NOT committed; user-private memory)
- `~/.claude/projects/.../memory/MEMORY.md` — index entry for new feedback policy

### Commits (this session, oldest to newest)

| Commit | Type/Scope | Description | Files | Lines |
|--------|---|---|---|---|
| `a7a4e9c9` | chore(codex-collaboration) | silence pyright unreachable hint on assert_never arm | 1 | +3/-1 |
| `6580d86e` | chore(codex-collaboration) | close T-01 delegate execution remediation | 2 (1 R 77%, 1 new) | +165/-1 |
| `aa3daed2` | chore(tickets) | track T-20260429-01 codex-collaboration delegation friction reduction | 2 (1 modified, 1 new) | +245/-1 |

### Branches

- `feature/delegate-execution-diagnostic-record` at `aa3daed2` (in sync with origin; 3 commits added this session)

### Smoke job artifacts (preserved on disk in plugin data root)

| Artifact | Path |
|---|---|
| Job worktree | `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/4586c6c3-39cb-49ff-815b-620d7f3212c9/worktree/` |
| full.diff | `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/4586c6c3-39cb-49ff-815b-620d7f3212c9/inspection/full.diff` |
| changed-files.json | `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/4586c6c3-39cb-49ff-815b-620d7f3212c9/inspection/changed-files.json` |
| test-results.json | `~/.claude/plugins/data/codex-collaboration-inline/runtimes/delegation/4586c6c3-39cb-49ff-815b-620d7f3212c9/inspection/test-results.json` |

### MCP tool calls this session

| Tool | Approximate count | Purpose |
|------|-------|---------|
| `Skill: handoff:load` | 1 | Resume from prior handoff |
| `Skill: codex-collaboration:delegate` | ~25 | Skill protocol load on each /delegate invocation |
| `Skill: handoff:save` | 1 | Save this handoff |
| `mcp__plugin_codex-collaboration_codex-collaboration__codex_status` | ~25 | Gate 2 status preflight per skill |
| `mcp__plugin_codex-collaboration_codex-collaboration__codex_delegate_poll` | ~30 | Gate 2 + post-acceptance + final renderings |
| `mcp__plugin_codex-collaboration_codex-collaboration__codex_delegate_decide` | ~24 | Per-escalation approve/deny decisions |
| `mcp__plugin_codex-collaboration_codex-collaboration__codex_delegate_start` | 1 | Smoke job start |
| `mcp__plugin_codex-collaboration_codex-collaboration__codex_delegate_promote` | 2 | Promotion attempts (1 worktree_dirty rejection, 1 verified) |
| Bash | ~30 | Process inspection, git operations, verification commands |
| Edit/Write | ~10 | Memory updates, ticket edits, register edits |
| Read | ~15 | Files for context (runtime.py, ticket, register, smoke artifacts) |

## Gotchas

### `git mv` doesn't restage modified content (NEW this session)

When you edit a file at its OLD path then `git mv` it to the NEW path, git stages the rename but keeps the PRE-EDIT blob as the staged content. Your edits are on disk but NOT staged.

**Detection:** `git status` shows `RM` (renamed + modified), or `git diff --cached --numstat` shows `0 0` for the moved file despite obvious content additions.

**Fix:** `git add <new-path>` after the `git mv` — re-hashes the working tree content and re-stages.

**Avoidance:** Pattern preference is `git mv` first → edit → `git add <new-path>`. Or even simpler: `mv` (regular shell), then edit, then stage both old-deletion and new-addition explicitly.

### `worktree_dirty` blocks promote on untracked files (NEW this session)

The plugin's promote precheck rejects with `reason: "worktree_dirty"` if `git status` shows ANY non-empty output, including untracked files unrelated to the diff being applied.

**Detection:** `/delegate promote` returns `{"rejected": true, "reason": "worktree_dirty", "detail": "Promotion failed: primary workspace has uncommitted changes."}`.

**Fix:** `git stash push -u -m "..."` to clear, then promote, then `git stash pop` to restore.

### `file_change` escalation has empty `requested_scope` payload (NEW this session)

App Server `file_change` escalations carry only `{grantRoot: null, reason: null}` in `requested_scope`. No file path, no change type, no diff preview. Operator approves blind.

**Detection:** `/delegate poll` shows `pending_escalation.kind == "file_change"` with empty scope fields.

**Workaround:** Approve and rely on Gate 1 (review-before-promote) for visibility on the eventual diff. Worktree isolation preserves safety.

**Long-term fix:** T-20260429-01 Phase 2-3 (Option F).

### `/delegate approve|deny` disambiguation rule conflicts with operator narration

The skill's strict grammar says trailing text after `approve` or `deny` should reject with escape guidance. But operators routinely send `/delegate approve — authorize` style commands with brief commentary.

**Detection:** Skill loads, parses args with trailing text, would reject per strict rule.

**Workaround:** Interpret intent based on context. If user is clearly responding to an escalation prompt with `approve` + commentary, proceed with approve. If genuinely ambiguous, ask.

### `stale_advisory_context: true` on promote response is informational, not an error

The promote response includes `stale_advisory_context: true` when the file modification has invalidated Codex's advisory-runtime view of the repo state. This is metadata, not a problem.

**Detection:** Response includes `"stale_advisory_context": true`.

**Action:** None required for the promote itself. Subsequent advisory operations in the same session would re-fetch.

### Carried gotchas (from prior sessions, still applicable)

- **`git mv` restage gotcha** — see above (NEW this session).
- **Test imports use `from server.X` not `from codex_collaboration.server.X`** — `pyproject.toml` has `pythonpath = ["."]`; `server` (the directory) is the import root.
- **Pyright reports `case _: assert_never(...)` as "unreachable"** — defensive exhaustiveness idiom; pre-existing carry-forward AT line 944 NOW (was 942 before this session's suppression). RESOLVED by the smoke artifact (`a7a4e9c9`).
- **Plugin restart for source code changes = full Claude Code restart** — Python's `sys.modules` caches imports.
- **`pgrep -fa <pattern>` matches its own argv** — use `ps -ef | grep ... | grep -v grep` instead.
- **macOS `date -u -j -f FMT INPUT +OUTFMT`** is the parsing trap; use epoch round-trip.
- **`actor=system` audit events vs `actor=claude`** — filter by actor when reading audit trail.
- **Approval TTL is graceful unblock-then-cancel** — jobs.jsonl shows park-cleared → running → canceled rather than direct cancel-from-parked.
- **Pre-existing Pyright RT.1 (`runtime.py:289`)** — pre-existing carry-forward; surfaces on every runtime.py edit; not a regression signal.

## User Preferences

(Carried from prior sessions, applied this session — verbatim quotes where relevant.)

**Handle commits proactively (carried, applied 3 times this session).** Memory `feedback_handle_commits.md`: "User wants Claude to author + execute commits without asking; default to action when work reaches a coherent buildable chunk." Applied throughout — every commit landed without re-asking permission once the chunk was buildable.

**Adversarial review is the preferred quality gate before proceeding to next phase (carried, applied multiple times via /copy patterns).** User routed multiple decisions through Codex via `/copy` for second opinions: smoke objective wording, first approve, deny experiment, plugin change scope, stash strategy, closure scope. The /copy reviewer's "My recommendation: X" closing line was the action trigger.

**"Awaiting your next X" closing line is the trigger (carried, applied multiple times).** Memory `feedback_copy_awaiting_means_act.md`. User pasted structured /copy reports throughout; their closing recommendations served as authorization for the next action.

**Push at clean phase boundaries with explicit authorization (carried, applied 3 times this session).** No push without authorization, but explicit recommendations to push (Codex's verification reports + user's "Yes, push") provide that authorization. Three pushes this session: `6a2bb5ae..6580d86e` (smoke artifact + T-01 closure), then `6580d86e..aa3daed2` (T-20260429-01 ticket).

**Per-concern commit isolation (carried, applied 3 times).** Each commit covers exactly one concern; types span `chore(codex-collaboration)`, `chore(codex-collaboration)`, `chore(tickets)`. The smoke artifact and T-01 closure are RELATED but not bundled — different concerns (code change vs ticket lifecycle), different scopes.

**Concise commit messages mirroring the repo style (carried, applied).** Format: `<type>(<scope>): <description>` with body explaining why before what.

(New this session — verbatim user quotes:)

**Tightened objective for live smoke:**
> "Silence the expected Pyright 'unreachable' diagnostic on the exhaustive `assert_never(outcome)` arm in `packages/plugins/codex-collaboration/server/delegation_controller.py` near line 942 by adding the narrowest justified suppression/comment, without changing runtime behavior. Keep the change tightly scoped. Verify with a targeted Pyright check and any focused test(s) needed."

User specifies a precise objective with constraints (narrowest, justified, no behavioral churn, scope tight, verification target). Apply: forward verbatim to `codex.delegate.start` without re-paraphrasing.

**Memory carve-out policy (initial):**
> "approve — authorize; let Codex consult its memory before proceeding. Codex should always be allowed to consult its memory"

The "should always be allowed" language is durable preference. Apply: save to memory immediately as feedback policy, don't treat as in-session-only.

**Memory carve-out policy (broadened):**
> "I actually changed my mind about Codex reading skills - I want to always-approve Codex to read skills"

The "changed my mind" language signals override of prior policy. Apply: update the memory file with broader scope, note the supersession.

**Friction observation:**
> "By the way, this is a lot of friction"

Casual but signals real pain. Apply: don't dismiss; reinforce the post-smoke plugin-change plan; consider quantifying (24 escalations) for the eventual ticket.

**Plugin change deferral:**
> "wait for the smoke to finish before doing anything"

Apply: don't bundle plugin-change work with smoke validation; let smoke complete first to provide measurement baseline for the change.

**Closure correction:**
> "T-01 is not fully closed yet. Criteria 1-4 and 6 are satisfied from the smoke evidence you showed, but criterion 5 in T-01 is about the final disposition. Right now the job is still `promotion: pending`, so T-01 closes only after: 1. `/delegate promote` succeeds, or 2. promotion is rejected with a typed, documented reason unrelated to the old sandbox/approval loop."

User precisely interpreted the AC criterion. Apply: don't conflate "evidence available" with "criterion satisfied" — read AC text literally and check disposition state.

**Closure scope discipline:**
> "Update the ticket and move it to `closed-tickets/`, but don't optimize for an `R100` rename. Once you edit the body, it is no longer a pure rename, and that is fine. A clean single-purpose closure commit matters more than preserving `R100`."

Apply: don't engineer for git's similarity detection; prioritize commit purity.

> "Update the reconciliation register at codex-collaboration-reconciliation-register.md in the same commit. Right now it still lists `T-20260423-01` as `blocking`; if you close the ticket without updating the register, you create fresh drift immediately."

Apply: closing a ticket WITHOUT updating the register creates immediate drift; bundle them in the same commit.

> "include only T-01 and the register / do not bundle the three diagnostic-doc findings into this closure commit / do not stage the restored untracked WIP files"

Apply: tight scope discipline; stage only the in-scope files explicitly.

**Tracking-not-forgotten directive:**
> "What about the Option B + E as priorities that we discussed earlier in this session for reducing unnecessary friction? I want to make sure we don't forget those"

Apply: the closure body's mention isn't tracking; create a real ticket + register entry.

**WIP creation intentionality:**
> "I created those files intentionally"

Apply: untracked files in the working tree may be deliberate WIP; don't propose deletion or treat as stray artifacts; preserve via stash for promote-clearing.

## Conversation Highlights

**User on smoke objective discipline:**
> "I would not close T-01 before step 2 completes."

Refers to the verification-in-primary-workspace step. Apply: complete each step in sequence; don't claim closure prematurely.

**User on stash strategy authorization:**
> "Yes, proceed with that"

Brief authorization for the multi-step stash → promote → commit → pop sequence. Apply: trust user's brief authorizations when context is clear.

**User on push timing:**
> "Yes. Push `feature/delegate-execution-diagnostic-record` as-is. `a7a4e9c9` and `6580d86e` are a coherent pair: the live smoke artifact landed, T-01 is closed, and the reconciliation register was updated in the same closure commit. The outstanding diagnostic-doc findings are separate follow-up work, not a reason to hold these two commits locally."

Refines my push proposal with specific reasoning. Apply: user values understanding the WHY of each push; provide it proactively in proposals.

**User on follow-up tracking creation:**
> "proceed with Path A (draft ticket + register update + commit + push confirmation)"

Direct authorization; minimal verbiage. Apply: when authorized, execute without re-litigating the design.

**User on the 24-escalation pain (passive observation):**
> "By the way, this is a lot of friction"

Drove the formalization of T-20260429-01. Without this comment, the friction findings might have stayed as closure-body mentions only. Apply: passive observations are first-class data — they signal what's annoying enough to formally fix.

**User mid-deny strategy override:**
> "I actually changed my mind about Codex reading skills - I want to always-approve Codex to read skills"

Mid-policy reversal. Apply: don't anchor on initial policy; user can update preferences mid-stream. Note the supersession explicitly.

**Working style observed:** User progressively expands scope via clear instruction batches; uses /copy for adversarial scrutiny at quality gates; intervenes with policy updates when prior policy proves wrong; trusts brief authorizations once context is clear; maintains tight commit-scope discipline. Communication is structured but compact.

**Communication pattern (carried + reinforced this session):** Reports use "What changed / Why / Verification / Remaining risks" structure (per global CLAUDE.md Response Contracts). User responds with structured analysis or directive instruction. The mutual structured-evidence pattern is durable across sessions.

## Rejected Approaches

### Recommending deny on `~/.codex/` reads (Phase 5-6, overridden mid-stream)

**Approach:** Apply "tighten the leash" recommendation to all `~/.codex/` reads to push Codex toward in-worktree work.

**Why it seemed promising:** Memory `feedback_deny_finalizes_job.md`: deny rejects ONE proposed action; agent adapts. Initial 4 escalations on skill-doc reads suggested Codex was in a meta-tooling loop.

**Specific failure (caught by user override):** User explicitly prefers Codex to consult its own data (memory + skills) without per-escalation friction. The "tighten the leash" pattern is appropriate for genuinely meta operations, but `~/.codex/` reads are Codex orienting itself — not meta-overhead.

**What it taught:** File-class distinction matters within `~/.codex/` (memories/skills are safe to always-approve; auth/config/history must remain operator-gated). The user's policy is about WORKFLOW TRUST, not about the security boundary — those are two separate questions answered by two separate mechanisms (operator policy + plugin policy).

### Premature T-01 closure declaration (Phase 12)

**Approach:** After the smoke completed and the diff materialized, declared "All 6 T-01 acceptance criteria are now satisfied" before promote had been attempted.

**Why it seemed promising:** All ACs had supporting evidence; criterion 5 (final disposition) seemed implicitly satisfied by reaching `promotion_state: pending`.

**Specific failure (caught by user correction):** Criterion 5 is about "successful promotion or typed/documented promotion rejection unrelated to sandbox/approval loop". `promotion_state: pending` is NEITHER — it's the awaiting-decision state. The criterion requires actual disposition (verified or typed-rejected). User caught this and corrected me before I closed prematurely.

**What it taught:** Read AC text literally. "Disposition" means final state, not "evidence available for final state". Don't conflate "criteria observable" with "criteria satisfied".

### Bundling diagnostic-doc reconciliation with T-01 closure commit (Phase 17)

**Approach:** Consider including the user's in-progress diagnostic doc edits (and the `T01-DIAGNOSTIC-HEADER` row update) in the T-01 closure commit since they're related concerns.

**Why it seemed promising:** Same area (codex-collaboration), same closure cycle (T-01 ending), one commit covering all related cleanup.

**Specific failure (caught before applying, by user directive):** User explicitly said tight scope: "include only T-01 and the register / do not bundle the three diagnostic-doc findings into this closure commit". Bundling would have polluted the commit with unrelated diagnostic-doc churn.

**What it taught:** Per-concern commit discipline trumps "related cleanup" instinct. Even when concerns are adjacent, separate commits keep history clean and revert-safe.

### Memory-only backstop for T-20260429-01 tracking (Phase 21, rejected as Path B)

**Approach:** Save Options B/E/F as a memory entry instead of creating a formal ticket.

**Why it seemed promising:** Lower-touch; no ticket draft needed; covered the "don't forget" concern at minimum cost.

**Specific failure (caught by Path A vs B comparison):** Memory entries are weaker tracking — don't appear in active work tables, don't show up in operational triage, depend on Claude proactively recalling them. The register's Maintenance Rule explicitly fires here: "a closed ticket leaves real follow-on work behind" → ticket required.

**What it taught:** When the project pattern is formal ticket tracking, follow it. Memory is for Claude-side preferences and policies; tickets are for operational work that needs to land.

### Optimizing for R100 rename on T-01 closure (Phase 17, rejected by user)

**Approach:** Consider doing the move as R100 (no body modifications) and adding closing notes in a separate commit or via the register update.

**Why it seemed promising:** Pure rename is the cleanest git diff; matches the prior session's `f66f8b7c` ticket-archive pattern (8 R100 renames).

**Specific failure (caught by user directive):** User explicitly said don't optimize for R100 — single-purpose closure commit matters more than preserving rename detection. The T-01 closure body needs the closing notes; splitting that into a separate commit bifurcates the closure into two adjacent commits unnecessarily.

**What it taught:** Pattern matching to a recent commit's shape (R100 archives) is a starting point, not a default. The actual constraint here ("clean single-purpose closure commit") differs from the archive case ("pure relocation") — different commits, different rules.
