---
date: 2026-04-16
time: "19:27"
created_at: "2026-04-16T19:27:34Z"
session_id: 361ed4cc-bf1c-4a70-a957-fba1dfb6b146
resumed_from: "docs/handoffs/archive/2026-04-16_12-17_t04-b1-pair-complete-b3-adversarial-next.md"
project: claude-code-tool-dev
branch: docs/ticket-dialogue-reply-extraction-mismatch
commit: 84d79fa6
title: "T-04 B3 pair complete; candidate hit extraction bug; ticket committed; B5 prep next"
type: handoff
files:
  - /private/tmp/benchmark-v1-staging-20260415/B3-baseline-metadata.json
  - /private/tmp/benchmark-v1-staging-20260415/B3-baseline-synthesis.md
  - /private/tmp/benchmark-v1-staging-20260415/B3-baseline-transcript.md
  - /private/tmp/benchmark-v1-staging-20260415/B3-candidate-metadata.json
  - /private/tmp/benchmark-v1-staging-20260415/B3-candidate-synthesis.md
  - /private/tmp/benchmark-v1-staging-20260415/B3-candidate-transcript.md
  - docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md
  - packages/plugins/codex-collaboration/server/dialogue.py
  - packages/plugins/codex-collaboration/server/prompt_builder.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/runtime.py
  - /Users/jp/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_benchmark_pathology_preservation.md
---

# T-04 B3 Pair Complete; Candidate Hit Extraction Bug; Ticket Committed; B5 Prep Next

## Goal

Run the B3 pair (adversarial code review), review both artifacts against the contract, triage an error-terminated candidate run without contaminating the benchmark, and set up B5 as the next row. The session was scoped at load time to "begin with B3 prep" per the predecessor handoff's explicit directive.

**Trigger.** The 12:17 handoff left B1 pair complete and explicitly named B3 prep as the next session's opening action. This session loaded that handoff and executed the B3 pair: baseline → review → candidate (in a fresh session out-of-conversation, artifacts returned for review) → review → RCA on candidate's non-convergence → ticket draft and revision → commit.

**Stakes.** Benchmark AC-5 (T-04 acceptance criteria) requires all four pairs (B1, B3, B5, B8) to execute on the fixed corpus. B3 is the first adversarial-posture pair and the first direct test of whether the candidate's architectural advantages from B1 (scope discipline, scouting-tier behavior, machine-adjudicable output) hold under a different cognitive mode. A contested B3 candidate would introduce ambiguity into supersession signal. The session produced decisive evidence: B3 baseline cleanly converged; B3 candidate terminated on a specific, fixable bug in the candidate's MCP dispatch layer.

**Success criteria (all met):**
1. B3 baseline validated against contract; review produced
2. B3 candidate validated-as-recorded per pathology-preservation rule; error termination documented not patched-around
3. Bug root cause identified via 15-min code spike; hypothesis triangulated against code + transcript evidence
4. Benchmark-status vs product-defect split preserved cleanly — no midstream rerun, no scored-validity preemption
5. Ticket drafted, reviewed (two review passes), committed on working branch
6. B5 prep deferred to next session opening action (same tempo as B3's load-session → fresh-session pattern)

**Connection to project arc.** T-04 (dialogue parity & scouting retirement) is the empirical gate for cross-model dialogue+context-injection retirement. B3 is the second of four pairs. The B3 signal is mixed in an interesting way: candidate still leads on scope discipline (0 out-of-scope Codex reads vs baseline's 4) and scouting (2 scouts vs 0), but baseline leads on convergence/completion (baseline converged at T4; candidate errored at T3). This is the confirmation-bias test the 12:17 handoff explicitly called for — and the data passed, in the sense that contradictory signal actually appeared and was preserved rather than rationalized away.

## Session Narrative

**Phase 1 — Load and B3 baseline prep (~4 min).**

Load skill resolved the 12:17 handoff, archived it, and wrote the state file. Pre-flight for B3 baseline: HEAD at `fa75111b` (unchanged since load handoff), staging intact at `/private/tmp/benchmark-v1-staging-20260415/`, session_id file present. Surfaced the paste-ready B3 baseline invocation from `invocations.md:72-89` with `{run_type}` → "This is a scored benchmark run." The fresh-session rule (operator-procedure.md:174) means the actual run happens in a separate Claude session; this session's role was prep + review.

User confirmed the pathology-preservation rule before running: *"if the baseline shows another obvious tooling pathology mid-run like the B1 scout timeout pattern, stop and preserve the artifacts rather than improvising around it. That kind of failure is benchmark signal."* Saved to memory as `feedback_benchmark_pathology_preservation.md` so it applies across all remaining pairs (B5, B8), not just B3.

**Phase 2 — B3 baseline review (~8 min).**

User returned with baseline artifacts exported (transcript 3178 lines, synthesis 15 KB, metadata 405 B). Initial metadata snapshot:

```json
{"id": "B3-baseline", "evidence_count": 0, "max_evidence": 5,
 "effective_posture": "adversarial", "actual_turns": 4,
 "converged_within_budget": true, "valid": true,
 "session_id": "361ed4cc-bf1c-4a70-a957-fba1dfb6b146",
 "session_id_canonical": true, "timestamp": "2026-04-16T14:08:42Z"}
```

Notable: `session_id` matches this session's ID, not a fresh-session ID. User clarified: baseline ran in a fresh session and they cat'd the file from that fresh session — but the fresh session didn't update the file because `/cross-model:dialogue` (baseline) doesn't fire the codex-collaboration plugin's SessionStart hook that writes to `~/.claude/plugins/data/codex-collaboration-inline/session_id`. So the baseline's `session_id` field reads whatever was last written by a codex-collaboration session — which for this session chain was this loader session's ID. Architectural observation worth Phase 3 notes: baseline `session_id` is weaker identity than candidate's. The actual run thread ID is `019d977b-23a3-7942-977d-21641446cae0` (captured separately in synthesis/transcript).

Scope-discipline audit: 0 agent scouts (matches `evidence_count: 0`), 0 agent Grep/Read tool calls, 73 in-scope file refs, 4 out-of-scope Codex server-side reads (`secret_taxonomy.py`, `control_plane.py`, `dialogue.py`, `prompt_builder.py`) — explicitly self-flagged at synthesis:111. Turn accounting: 6 USER TURNs in transcript (1 setup + 4 dialogue turns + 1 synthesis request) = `actual_turns: 4`. No invalidation triggers met. **Verdict: valid, proceed to candidate.**

Comparison to B1 baseline: evidence_count parity (0 both), out-of-scope Codex reads narrower (4 vs 8+), converged earlier (4 vs 5 turns) despite adversarial posture, structurally richer claims (5 RESOLVED + 4 UNRESOLVED + 2 EMERGED with confidence + basis tags + explicit T1→T4 trajectory annotation). Baseline's adversarial dialogue produced real challenge-and-concession exchange — Codex revised its initial "exfiltration primitive" framing on placeholder bypass after agent challenged threat model. The baseline *can* do adversarial dialogue despite its 0-scout architecture.

**Phase 3 — B3 candidate run + artifact exports (~30 min out-of-session).**

User ran B3 candidate in a fresh session and returned with exports. Key metadata snapshot:

```json
{"id": "B3-candidate", "evidence_count": 2, "max_evidence": 15,
 "effective_posture": "adversarial", "effective_turn_budget": 6,
 "actual_turns": 3, "converged_within_budget": false,
 "termination_code": "error", "mode": "agent_local",
 "session_id": "ea58817b-e193-4018-988f-d45e0c3cd94c",
 "session_id_canonical": true, "valid": true,
 "thread_id": "019d979c-f50c-7213-9729-be04ad765642",
 "notes": "Terminated on turn 3 due to codex.dialogue.reply parse failure (empty response). All 7 final claims supported by in-scope evidence..."}
```

User's insight flags:
1. `_extract_transcript.py` has `"# B1 Candidate"` hardcoded on line 54 — latent bug; someone already hand-corrected B1-baseline export. Worth a post-benchmark tidy, not inline.
2. `evidence_count=2` per fa75111b rule means "two agent-side scouts" — NOT "two file reads" (Codex server-side reads explicitly excluded). The fa75111b clarification is doing its job.

User explicitly invoked the pathology-preservation rule: marked `valid: true` with `converged_within_budget: false` and `termination_code: error`, preserved artifacts rather than improvising.

**Phase 4 — Candidate review and first validity call (~10 min).**

Read the three artifacts. Key structural observations:

- Synthesis explicitly flagged all 7 final claims as "supported by in-scope evidence." No out-of-scope Codex reads (0 vs baseline's 4). Scouted 12 `exec_command` calls, all within `allowed_roots`.
- `scope_breach_count: 0` in pipeline-data epilogue.
- The trajectory: `T1:advancing(evidence_gather, framing) → T2:advancing(evidence_gather, consolidation) → T3:error(tool_parse_failure)` — completed two substantive evidence-gathering rounds before termination.
- Synthesis surfaced 5 distinct findings (NEAR-window bypass, raw metadata sinks, construction-time-only invariant by convention not structure, JWT ticket-vs-code drift, inline dict/JSON assignment gap) before termination. 3 of 5 are DIFFERENT from baseline's findings.
- Cross-system corroboration: both systems independently surfaced JWT ticket-vs-code drift. That finding strengthens Phase 3 confidence.

Contract-validity analysis against operator-procedure.md:660-666 invalidation triggers:
1. Scope violation — NO (0 out-of-scope)
2. Evidence-budget overflow — NO (2 ≤ 15)
3. Run condition breach — NO (fresh session, clean tree, canonical session ID)
4. Missing artifacts — NO (all three present)

**Tool-layer parse failure is NOT in the invalidation trigger list.** Non-convergence is treated as a diagnostic metric (:519), not a validity condition. **Verdict: `valid: true` is contract-correct.** The current B3 candidate is valid scored evidence of a candidate fragility.

**Phase 5 — Fork framing error and user correction (~15 min).**

Initially framed the operator decision as a two-way fork: (A) accept as-is and move to B5, (B) patch + rerun B3 candidate as `B3-candidate-rerun-1` marked `superseded_by`. Recommended (B) with triage first.

**User pushed back on contract grounds:** "The invalidation triggers in the procedure are explicit at operator-procedure.md:660, and this run does not meet them. So I would not relabel it invalid just for scoring hygiene." And the critical insight: "The procedure says 'All runs must use the same commit' at operator-procedure.md:64. That means a mid-benchmark patch is not 'fix + rerun B3 candidate' in the scored packet. It is either: (a) a diagnostic post-fix rerun outside the current scored benchmark, or (b) a decision to restart the scored benchmark from B1 on the new commit."

Verified :66 directly: "All runs must use the same commit." The user's reading is correct. My step 5 (mark invalid + supersede + rerun on new commit) was a category confusion — treating a fragility finding as a run-level disqualifier.

Also: the 12:17 handoff's §Risks #1 explicitly named confirmation-bias as the failure mode I was exhibiting. Proposing to rerun B3 candidate on a patched commit would have replaced the contradictory signal with a converged run — the exact sanding-away the handoff warned against. Conceded the framing fully.

**Phase 6 — RCA spike on extraction bug (~18 min).**

User authorized a bounded 15-min RCA spike. Three hypotheses going in:
1. Systematic empty-reply handling bug in `codex.dialogue.reply`
2. Transient Codex App Server flake
3. Adversarial-posture interaction triggering output shape edge case

Steps executed:
1. Grepped `codex.dialogue.reply` references across plugin — found handler at `mcp_server.py:263-272`, parse error text source at `prompt_builder.py:58-63`.
2. Tailed B3 candidate transcript — found a **FULLY SUBSTANTIVE Codex reply** at line 1442 responding to USER TURN 4's adversarial pressure-test (~4000-char JSON with `position`, `evidence[5]`, `uncertainties[3]`, `follow_up_branches[3]`). This contradicts "empty completion" hypothesis — Codex produced substantive content.
3. Read `dialogue.py` reply path around line 470-520. Found: `parse_consult_response(turn_result.agent_message)` at line 502. Direct field read, no fallback.
4. Read `dialogue.py` around line 960-990. Found: `_read_turn_agent_message` static method at line 974 with TWO-shape extraction: first `raw_turn["agentMessage"]`, then iterate `raw_turn["items"][type="agentMessage"].text`. Returns `""` if neither found.
5. **Root cause identified.** Codex runtime can deliver agent messages in two shapes (top-level `agentMessage` field OR `items` array). `_read_turn_agent_message` handles both; `reply()` only handles shape 1. When Codex delivered T3's ~4000-char adversarial reply via shape 2, `turn_result.agent_message` came through empty → `parse_consult_response("")` → `json.JSONDecodeError` → `CommittedTurnParseError` → dialogue terminated.
6. Hypotheses re-ranked: H2 REJECTED (reply was substantive, not empty). H1 SUPPORTED with refinement (it's an *extraction mismatch*, not empty-response handling). H3 PARTIAL (adversarial posture correlates — longer replies more likely delivered via items-array shape — but doesn't cause the bug).

**Phase 7 — Decision dialogue on patch boundary (~8 min).**

Proposed Option A (canonicalize `agent_message` at dispatch in `runtime.py:173-177`) vs Option B (enrich `TurnExecutionResult`) vs Option C (post-commit journal read). Recommended Option A with rationale: narrowest long-term surface, fixes root cause, consult path benefits incidentally.

User accepted the technical framing entirely but pushed back HARD on the benchmark integrity angle — see Phase 5 above. The fork is not "patch + rerun B3 candidate" but "patch + abort and restart benchmark from B1 on new commit" OR "finish current scored track, patch post-benchmark."

User's clean split: (1) keep current B3 candidate as valid benchmark evidence for the pre-patch track, (2) if we patch, start new benchmark track on new commit. Conceded the framing fully. **Revised recommendation: Option A (complete benchmark on current pre-patch track, patch post-benchmark).**

**Phase 8 — Ticket drafting and review cycles (~30 min).**

User directed: draft ticket capturing the bug with benchmark-status vs product-defect split explicit, pause for review. Drafted `docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md` on branch `docs/ticket-dialogue-reply-extraction-mismatch` with sections: Dual record (benchmark-status + product-defect), Symptom, Reproduction context, Root cause, Why the B3 run stays valid, Proposed fix, Post-benchmark follow-up, B5/B8 reproduction expectations, References.

**First review pass (user, via code-comment format):**
- [P1] "Commit mismatch undermines the ticket's validity argument" (confidence 0.98): Ticket said "correct `run_commit: 693551cc` (current)" AND "`fa75111b` recorded in transcript" — self-contradictory. Under operator procedure, commit mismatch is a run-condition breach. Unless benchmark intentionally moved to `fa75111b` for all rows, ticket can't both preserve run as valid AND cite different transcript head without explaining.
- [P2] "Minimal fix description assumes data `reply()` does not currently have" (confidence 0.95): Proposed patch said `reply()` can "obtain the raw_turn dict from the dispatch layer" but `TurnExecutionResult` only carries `turn_id`, `agent_message`, `notifications`. As written, understates surface area and effort.

Verified P2 via grep — confirmed `TurnExecutionResult` at `models.py:106-111` has exactly 3 fields, and `runtime.py:173-177` constructs it without preserving raw response. Both reviewer points correct.

**Revisions applied:**
- §Why the B3 run stays valid: Added dedicated §Commit reconciliation subsection. Acknowledged B3 candidate ran on `fa75111b`, manifest records `693551cc`, two intervening commits are doc-only. Noted same mismatch applies uniformly to B1 candidate + B3 baseline + B3 candidate (not B3-specific). Deferred reconciliation to parent track `T-20260330` with three options named (update manifest, rerun B1 baseline, document as benchmark-procedural exception). Separated the "mid-track patching violates run_commit invariant" argument into its own subsection.
- §Proposed fix: Added "Correction to the initial draft" paragraph. Rewrote to present three fix options (Option A = canonicalize at dispatch, B = enrich TurnExecutionResult, C = post-commit journal read) with scope trade-offs. Recommended Option A. Bumped effort from `small` to `medium`. Expanded test matrix to 5 tests.

**Second review pass (user, code-comment format):**
- [P2] Benchmark-status paragraph still resolves commit dispute too early (0.94): Opening paragraph stated B3 "is valid scored evidence" as settled conclusion. If parent track later decides commit drift is invalidation, ticket would have encoded opposite decision.
- [P2] Follow-up section hardcodes one reconciliation outcome (0.97): "commit `693551cc`" hardcoded in section that explicitly routed the decision to parent track.

**Revisions applied:**
- §Benchmark status rewritten to "is preserved as captured — transcript, synthesis, and metadata exported to staging. The extraction-path failure this ticket tracks does not on its own meet any invalidation trigger... Final scored-validity classification for this row belongs to the parent benchmark track `T-20260330`." Explicit: "This bug ticket does not assert a scored-validity verdict; it preserves the artifact and its finding."
- §Post-benchmark follow-up: changed "commit `693551cc`" → "current pre-patch benchmark track"; added "The specific commit that defines that track is a reconciliation question owned by `T-20260330`."

**Third pass — user approved:** "Findings: No findings." Committed ticket at `84d79fa6` on branch `docs/ticket-dialogue-reply-extraction-mismatch`.

## Decisions

### Decision 1: Accept B3 baseline metadata as-is, valid: true

**Choice:** Treat `evidence_count: 0, valid: true` as contract-correct without edits. Mark B3 baseline complete.

**Driver:** Same pattern as B1 baseline. Agent scouted 0 times (consistent architectural signature across postures). Converged naturally at T4. `converged_within_budget: true`. No invalidation triggers met.

**Alternatives considered:**
- Mark `valid: false` due to 4 out-of-scope Codex server-side reads — rejected because contract §51-52 "prompt-only" enforcement binds agent scope, not Codex exec. Codex's autonomous scouting on `secret_taxonomy.py`, `control_plane.py`, `dialogue.py`, `prompt_builder.py` was self-flagged in synthesis:111 and is edge-case noted for Phase 3, not invalidation.
- Rerun for audit cleanliness — rejected because no contract-defined invalidation condition met.

**Trade-offs accepted:** Baseline `session_id` field has weaker identity semantics than candidate's (see Gotchas #2). Recorded this session's ID rather than a fresh-session ID because `/cross-model:dialogue` doesn't fire the codex-collaboration SessionStart hook that writes to the canonical session-id file. Accepted because thread_id provides real run identity; Phase 3 can use thread_id for cross-run audit.

**Confidence:** High (E3). Field-by-field validation, synthesis self-declaration, transcript audit, contract text all triangulate.

**Reversibility:** High — if Phase 3 adjudication surfaces unseen invalidation, reclassify.

**Change trigger:** Adjudication evidence of session reuse, wrong commit, missing artifact, or contract amendment redefining invalidation.

### Decision 2: Accept B3 candidate as `valid: true` despite error termination

**Choice:** Treat `converged_within_budget: false`, `termination_code: error`, `valid: true` as contract-correct. Preserve as captured. Do not rerun, do not reclassify.

**Driver:** Operator-procedure.md:660-666 invalidation triggers are explicit and exhaustive. Tool-layer parse failure is not one of them. Non-convergence is a diagnostic metric (:519), not a validity condition. The pathology-preservation rule (saved to memory early this session) says: "stop and preserve the artifacts... do not improvise around them — the failure is signal."

**Alternatives considered:**
- Mark `valid: false`, `superseded_by: B3-candidate-rerun-1` and rerun on patched commit — REJECTED after user correction. This would have been a category confusion (treating system fragility as run-level disqualifier) AND violated `run_commit` invariant (:66 "all runs must use the same commit") AND triggered exactly the confirmation-bias pattern the 12:17 handoff explicitly warned against.
- Mark `valid: false` without rerun, record the bug as sole finding — rejected because no contract invalidation trigger met, and marking invalid would erase the 7 supported findings the run produced.
- Accept `valid: true` for benchmark purposes but quietly reclassify later — rejected because it conflates two separate facts (benchmark-valid run + separate product defect). The ticket cleanly splits them.

**Trade-offs accepted:** B3 candidate will appear in Phase 4 aggregate scoring as non-converged. This correctly records that the candidate AS SHIPPED has an adversarial-posture fragility. Some readers may interpret non-convergence as "candidate lost"; the ticket makes clear this is an honest data point about current system behavior.

**Confidence:** High (E3). User directly challenged the original framing and the revised decision is their framing. Contract-integrity argument verified against :66.

**Reversibility:** High — if the parent benchmark track T-20260330 decides to reclassify based on commit reconciliation, that decision is structurally owned there. This ticket explicitly disclaims scored-validity verdict.

**Change trigger:** Parent track's commit-reconciliation decision; or Phase 3 adjudication revealing a previously-invisible invalidation signal.

### Decision 3: Continue scored benchmark on current pre-patch track; patch post-benchmark

**Choice:** Complete B5 + B8 pairs on current HEAD (`fa75111b`, whatever its reconciled run_commit is). Treat the `dialogue.reply` extraction bug as a post-benchmark work item tracked in `T-20260416-01`.

**Driver:** Contract integrity. The `run_commit` rule at operator-procedure.md:66 is structural, not procedural — it's what makes aggregate scoring (:510-519) interpretable. Patching mid-benchmark would produce per-row metrics against different system versions. That's not "less clean" — it's unscorable. Plus: patching + rerunning would erase the B3 contradictory signal, which is the confirmation-bias pattern explicitly flagged.

**Alternatives considered:**
- Patch now, restart scored benchmark from B1 on new commit — rejected because the 2-hour benchmark completion cost is meaningfully smaller than the ~4-pair rerun cost, AND the current track's data is valuable even with the fragility finding. If patching is justified, it's justified AFTER completion to preserve maximum signal.
- Patch now, treat as diagnostic-only post-fix rerun outside scored benchmark — rejected as less useful than simply documenting the bug with a ticket. The rerun wouldn't add to the scored benchmark; the ticket captures what's needed.
- Don't patch at all, let the bug ship — rejected because the bug affects `/codex-collaboration:dialogue` for any user hitting long Codex replies, and the fix is small-to-medium.

**Trade-offs accepted:** B5 candidate and B8 candidate may reproduce the same bug. User's framing: that's MORE benchmark data, not a blocker. The ticket explicitly says log additional occurrences as benchmark evidence, don't patch mid-track.

**Confidence:** High (E3). User's framing, verified against :66.

**Reversibility:** High — if B5 OR B8 reveals a NEW class of bug (not the same extraction bug), the calculus might shift. Not anticipated.

**Change trigger:** New class of candidate fragility surfacing in B5/B8; urgent user-facing bug report requiring hotfix before benchmark completes; or discovery that :66 has a doc-only-drift exception that changes the mid-track patch calculus.

### Decision 4: Fix boundary preference — Option A (canonicalize at dispatch)

**Choice:** When patching, prefer canonicalizing `agent_message` extraction at `runtime.py:173-177` (Option A) over enriching `TurnExecutionResult` (Option B) or post-commit journal read (Option C).

**Driver:** The robust two-shape extractor `_read_turn_agent_message` is already written and tested. Moving it to a shared module (e.g., `codex_compat.py`) and calling it from runtime's `agent_message` extraction fixes the root cause at its source. All downstream consumers (`reply`, `consult`, future tools) benefit. `TurnExecutionResult` stays unchanged.

**Alternatives considered:**
- Option B (enrich TurnExecutionResult with items projection) — rejected as broader surface than necessary. Exposes dispatch-layer data shape to all consumers whether they need it or not.
- Option C (post-commit journal read) — rejected as controller-only but couples `reply()` to persistence-layer retrieval, adds storage round-trip per reply.
- Wait-and-see (don't fix, accept the fragility) — rejected per Decision 3 rationale (user-facing impact is real).

**Trade-offs accepted:** Moving `_read_turn_agent_message` out of the controller touches more files than adding a fallback in-place. Accepted because the static extractor's tests move with it (no test rewriting), and the long-term surface is narrower.

**Confidence:** Medium-High (E2). User accepted technical framing. Actual implementation may surface edge cases (e.g., `runtime.py` needs access to `_read_turn_agent_message` without creating a circular import — may need new `turn_extraction.py` module).

**Reversibility:** High — if Option A turns out to have unexpected blockers, Option B is 1-2 hours of extra work.

**Change trigger:** Implementation revealing circular imports, unexpected test failures, or other consumers (e.g., consult) having divergent extraction requirements.

### Decision 5: Route commit-reconciliation question inline to T-20260330

**Choice:** When the benchmark track resumes, add the commit-reconciliation question as an explicit open decision in `T-20260330` (dialogue parity & scouting retirement), not as a separate standalone ticket.

**Driver:** User's framing: "benchmark-governance work, not a distinct product defect. Put it inline in `T-20260330` as an explicit open decision or benchmark exception note. That keeps the ownership in the track that can actually decide it, and avoids scattering one benchmark-integrity question across multiple tickets."

**Alternatives considered:**
- Open a separate ticket for reconciliation (e.g., `T-20260416-02`) — rejected per user's framing; splits ownership and dilutes context.
- Add to this ticket (`T-20260416-01`) — rejected because this ticket is scoped to the product defect, not governance. The existing §Commit reconciliation subsection here routes the decision to T-20260330 without claiming to resolve it.

**Trade-offs accepted:** Risks the reconciliation question being overlooked if T-20260330 gets tidied up before benchmark track resumes. Mitigation: flag in this handoff's §Next Steps so next-session Claude picks it up when loading.

**Confidence:** High (E3). User directive.

**Reversibility:** High — if the question grows beyond what T-20260330 can absorb, can spin out a separate ticket at that point.

**Change trigger:** T-20260330 being closed or repurposed before benchmark completes (then reconciliation needs a new home).

## Changes

### Files created

**`docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md` (198 lines)**

T-20260416-01 ticket documenting the `codex.dialogue.reply` extraction mismatch bug surfaced by B3 candidate. Includes:
- Frontmatter: `id: T-20260416-01`, `status: open`, `priority: medium`, `effort: medium`, `tags: [codex-collaboration, dialogue, bug, post-benchmark, mcp-dispatch]`
- §Dual record (benchmark-status preserving artifact; product-defect tracking bug)
- §Symptom with error text verbatim
- §Reproduction context (table: thread/run/commit/posture/budget)
- §Root cause (extraction-mismatch table with file:line refs)
- §Why the B3 run stays valid (all four invalidation triggers evaluated + commit reconciliation subsection + contract-integrity-constraint subsection)
- §Proposed fix (three options with scope trade-offs, Option A recommended)
- §Post-benchmark follow-up (sequence, closure criteria)
- §B5/B8 reproduction expectations (log don't patch mid-track)
- §References (11 rows)

Commit: `84d79fa6` on branch `docs/ticket-dialogue-reply-extraction-mismatch`. Branch NOT merged to main yet.

### Memory files created

**`~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_benchmark_pathology_preservation.md`**

Feedback memory saved at Phase 1 of session: mid-run tooling pathologies in scored benchmark runs → stop, preserve artifacts, patch out-of-run, rerun. Do not improvise around them. Applied uniformly to B5 and B8 going forward.

MEMORY.md updated with pointer under §Feedback.

### Benchmark staging artifacts

**B3 baseline pair (out-of-session exports):**
- `/private/tmp/benchmark-v1-staging-20260415/B3-baseline-transcript.md` (149 KB, 3178 lines)
- `/private/tmp/benchmark-v1-staging-20260415/B3-baseline-synthesis.md` (15 KB, 146 lines)
- `/private/tmp/benchmark-v1-staging-20260415/B3-baseline-metadata.json` (405 B)

**B3 candidate pair (out-of-session exports):**
- `/private/tmp/benchmark-v1-staging-20260415/B3-candidate-transcript.md` (103 KB, 1444 lines)
- `/private/tmp/benchmark-v1-staging-20260415/B3-candidate-synthesis.md` (8.6 KB)
- `/private/tmp/benchmark-v1-staging-20260415/B3-candidate-metadata.json` (1 KB)

No in-session edits to staging files. Review-only.

### Working tree state

Branch: `docs/ticket-dialogue-reply-extraction-mismatch`. HEAD: `84d79fa6`. Working tree clean. No changes to main.

## Codebase Knowledge

### `codex.dialogue.reply` parse path (bug site)

| File | Role | Key lines |
|---|---|---|
| `packages/plugins/codex-collaboration/server/mcp_server.py` | MCP tool handler dispatch | `:77` (tool registration), `:263-272` (handler: calls `controller.reply(collaboration_id, objective, explicit_paths)`) |
| `packages/plugins/codex-collaboration/server/dialogue.py` | Dialogue controller | `:341-520` (reply() method), `:498-509` (parse step with commit-before-parse design), `:502` (**bug site**: `parse_consult_response(turn_result.agent_message)`), `:973-990` (`_read_turn_agent_message` with two-shape fallback — **fix reuse target**) |
| `packages/plugins/codex-collaboration/server/prompt_builder.py` | Parse function | `:53-115` (`parse_consult_response`), `:58-63` (empty-string error source: `json.loads("")` → `JSONDecodeError` → `"Consult result parse failed: expected JSON object. Got: ''"`) |
| `packages/plugins/codex-collaboration/server/models.py` | Dataclass definitions | `:106-111` (**`TurnExecutionResult`** has exactly 3 fields: `turn_id: str`, `agent_message: str`, `notifications: tuple[dict[str, Any], ...]`). No raw_turn or items-array projection.) |
| `packages/plugins/codex-collaboration/server/runtime.py` | Codex App Server dispatch layer | `:173-177` (**`agent_message` extraction site** — where canonical extraction should live per Option A fix); the construction of `TurnExecutionResult` here determines what reply() sees. |

### Two Codex response shapes (root cause)

The Codex Rust runtime (`codex`) can deliver an agent message in two shapes. Both are valid per the runtime's API. Client-side code must handle both:

**Shape 1 — Top-level `agentMessage` field:**
```json
{"agentMessage": "...", "turn_id": "...", ...}
```
Used for short/simple replies. Handled by `reply()` directly (works fine).

**Shape 2 — `items` array with typed entries:**
```json
{"items": [{"type": "agentMessage", "text": "..."}, ...], "turn_id": "..."}
```
Used for streamed or complex replies. Handled by `_read_turn_agent_message` fallback (works fine). NOT handled by `reply()` (bug).

The B3 candidate's T3 reply (~4000 chars, 6-field JSON schema) was delivered via shape 2. `turn_result.agent_message` arrived empty. Parse failed.

### Commit-before-parse design (preserved invariant)

At `dialogue.py:498-499`, the comment reads:

> Parse projection — all durable state is committed above.
> If parsing fails, the turn is committed and readable via dialogue.read.

This is an architectural strength: the turn IS persisted (journal + turn_store + lineage_store) BEFORE the parse step. A parse failure raises `CommittedTurnParseError` but does NOT lose data. The failed turn is retrievable via `codex.dialogue.read` from a fresh session using the same collaboration_id.

**Implication for Option A fix:** whatever changes runtime-layer extraction must preserve commit-before-parse. Option A does — it only changes what `agent_message` gets populated with, not when persistence happens.

### Operator-procedure.md key provisions (canonical references)

| Provision | Line | Content |
|---|---|---|
| Fix the benchmark commit | :64-74 | "All runs must use the same commit." — the `run_commit` invariant |
| Evidence-budget overflow | :340-345 | Evidence-budget overflow is invalidating (not advisory) |
| Invalidation triggers (exhaustive) | :660-666 | 4 conditions: scope violation, evidence-budget overflow, run condition breach, missing artifacts |
| Rerun procedure | :669-676 | Mark `valid: false`, `invalid_reason`, `superseded_by`. Rerun from same commit in fresh session. Only valid runs contribute to aggregate metrics. |
| Diagnostic metrics | :519 | `converged_within_budget` is counted (not gated on) |
| Aggregate scoring | :510-530 | Computed across all valid runs per system |
| Known limitation: prompt-only scope | :687-698 | Neither system mechanically enforces `allowed_roots`; review is post-hoc |

### Transcript-format differences (B3 baseline vs B3 candidate)

Baseline (`/cross-model:dialogue`, mode `server_assisted`): 3178 lines. Structure: `## USER TURN N (agent → Codex)` headers alternating with `## ASSISTANT REPLY (Codex → agent)` headers. Codex `cmd:` markers for exec_command calls may appear as embedded blocks or may use a different format (grep for `^cmd:` returned 0 matches in B3 baseline transcript; synthesized from context).

Candidate (`/codex-collaboration:dialogue`, mode `agent_local`): 1444 lines extracted via `_extract_transcript.py` from Codex session rollout JSONL. Structure: USER TURN 1-4 + 3 ASSISTANT REPLY blocks = 1 setup + 3 dialogue turns. The 12 `exec_command` scouts are EMBEDDED within the ASSISTANT REPLY blocks (not separate items). This is why grep patterns that worked on baseline may not work on candidate.

### Staging directory structure (intact at 19:27)

```
/private/tmp/benchmark-v1-staging-20260415/
├── _extract_transcript.py   (5733 B, user-authored helper)
├── invocations.md           (11138 B, all 8 invocations pre-built)
├── B1-baseline-{transcript,synthesis,metadata}  (complete)
├── B1-candidate-{transcript,synthesis,metadata} (complete)
├── B3-baseline-{transcript,synthesis,metadata}  (complete, this session)
└── B3-candidate-{transcript,synthesis,metadata} (complete, this session)
```

B5 and B8 staging will follow same naming convention.

## Context

### Current T-04 acceptance criteria status

| AC | Description | Status |
|---|---|---|
| 1 | `/dialogue` skill exists | Done (PR #106) |
| 2 | `dialogue-orchestrator` agent exists | Done (PR #106) |
| 3 | Gatherer agents exist | Done (PR #107) |
| 4 | Synthesis with bounded citations | Done |
| 5 | Benchmark contract executed on fixed corpus | **2 of 4 pairs complete (B1, B3); 2 remaining (B5, B8)** |
| 6 | Benchmark result recorded with per-task metrics | Open; depends on AC-5 |
| 7 | Context-injection retirement decision | Open; depends on AC-6. **Directional signal: B1 positive for supersession; B3 mixed (candidate wins scope+scouting, baseline wins convergence).** |

### Mental model for this session

This was a **run + review + triage** session. The B3 pair produced structurally richer comparative data than B1 because:
1. Posture differs (adversarial vs B1's evaluative), so same dimensions were tested under a different cognitive mode
2. Candidate exercised its scouting budget (2 of 15) for the first time in scored runs — first real test of whether scope_envelope holds under scouting pressure
3. Candidate failed to converge — first contradictory signal to B1's "positive for supersession" direction

All three of those were expected possibilities. The third happening is valuable because it forces the retirement decision (AC-7) to be more nuanced than "candidate wins cleanly" — the candidate has real architectural advantages AND real shipped fragilities. That's closer to the truth than a clean win would have been.

### Environment snapshot

- Branch: `docs/ticket-dialogue-reply-extraction-mismatch` (not merged to main)
- HEAD: `84d79fa6` (this session's ticket commit)
- Working tree: clean
- Main branch: `fa75111b` (unchanged since the load handoff's predecessor saved)
- Staging directory: intact with 12 files (3 B1 baseline + 3 B1 candidate + 3 B3 baseline + 3 B3 candidate) + `invocations.md` + `_extract_transcript.py`
- `~/.claude/plugins/data/codex-collaboration-inline/session_id` contains `361ed4cc-bf1c-4a70-a957-fba1dfb6b146` (this session's ID)

### Open tickets

| Ticket | Status | Next |
|---|---|---|
| T-20260330 (Dialogue parity & scouting retirement — parent benchmark) | Open; AC 1-4 done, AC-5 at 2/4 pairs valid | Run B5 pair |
| T-20260416-01 (dialogue.reply extraction mismatch) | Open; deferred to post-benchmark | Pick up after benchmark track completes |
| T-05 Execution-domain foundation | Open (unstarted) | Separate workstream |
| T-06 Promotion flow & delegate UX | Open (blocked by T-05) | — |
| T-07 Analytics reviewer & cutover | Open | Separate workstream |

## Learnings

### Benchmark-surfaced bugs require evidence-preserving tickets, not invalidation

**Mechanism.** When a benchmark run surfaces a product defect in the system under test, the natural instinct is to fix the defect and rerun. But the contract's invalidation triggers (operator-procedure.md:660-666) are EXHAUSTIVE — they list run-condition issues, not system-behavior findings. A product defect that doesn't match any of the four triggers is valid scored evidence of that defect; marking it invalid to "clean up the scoring" is category confusion.

**Evidence.** B3 candidate hit a real bug (`dialogue.reply` items-array extraction). My first instinct was Option B (mark invalid + supersede + patch + rerun). User pushed back on two grounds: (a) no invalidation trigger met, so marking invalid violates :660-666 by operator fiat; (b) `run_commit` rule at :66 means patch-and-rerun-in-track is structurally impossible — all runs must share a commit. The correct move was accept-as-is + ticket-the-bug-separately + complete-track.

**Implication.** Future bug tickets surfaced DURING benchmark runs should: (1) preserve the artifact without scored-validity verdict (defer to parent track), (2) document the bug independently as product-defect lifecycle, (3) explicitly disclaim mid-track patch reclassification. The T-20260416-01 template captures this pattern — reuse it for any B5/B8 findings.

**Watch for.** Language like "this run should be rerun" or "clean up the benchmark" in my own reasoning. Both are red flags. If a run produces substantive findings + doesn't meet invalidation triggers, the findings stay. Signal is more valuable than hygiene.

### Tickets can preempt decisions that aren't theirs to make

**Mechanism.** A ticket documenting a bug in system X during benchmark Y can inadvertently encode decisions that belong to benchmark Y's parent governance. Stating "is valid scored evidence" in a bug ticket preempts whatever scored-validity decision the parent track might later make based on its own reconciliation rules.

**Evidence.** First draft said B3 candidate "is **valid scored evidence** and remains part of the scored benchmark track." Reviewer flagged [P2, 0.94 confidence]: "If T-20260330 later decides the commit drift is a run-condition breach, this ticket will already have encoded the opposite decision." Second revision: "is preserved as captured... Final scored-validity classification for this row belongs to the parent benchmark track T-20260330."

**Implication.** When writing cross-cutting tickets, the rule is: state artifact preservation, quote contract provisions, hand final classification to parent track with explicit wording. Do not conflate "I preserved the artifact" with "I verified it's scored-valid" — scored validity is a decision, not a fact the ticket records.

**Watch for.** Any claim about benchmark run status in a product-defect ticket. Rephrase to be about the artifact's captured state, not about its scored status.

### The commit-before-parse design is a preservation pattern worth emulating

**Mechanism.** `dialogue.py:498-499` commits durable state BEFORE the parse projection runs. A parse failure raises an error but doesn't lose data — the turn is retrievable from persistent stores. This is why the B3 candidate's T3 reply wasn't lost despite the MCP tool aborting; it lives in the journal, turn_store, and lineage_store.

**Evidence.** Comment at `dialogue.py:498-499`: "Parse projection — all durable state is committed above. If parsing fails, the turn is committed and readable via dialogue.read." Verified by code structure: `finalize_confirmed_turn` runs at line 484 before the `parse_consult_response` call at line 502.

**Implication.** When designing parse/projection steps over externally-produced data, commit the raw data FIRST, project SECOND. Data loss from projection bugs becomes impossible; at worst, projection can be retried from persisted state. This pattern is worth applying to other data-ingestion surfaces (e.g., future learnings ingestion, ticket imports, handoff parsing).

**Watch for.** Any code path where external data flows into a parse/validate step before persistence. That's a data-loss risk; flip the order.

### Short open-ended questions from user signal imprecise prior output (recurring)

**Mechanism.** User's corrections this session took the form of short code-review-style comments with surgical precision:
- P1 commit mismatch (0.98 confidence): a sharply-worded paragraph that exposed ticket self-contradiction
- P2 TurnExecutionResult (0.95 confidence): a terse statement that exposed a wrong implementation claim
- P2 scored-validity preemption (0.94 confidence): a single-issue correction showing the opening paragraph resolved too early

**Evidence.** Same pattern as the 12:17 handoff's "Why B3 and not B2?" and the 11:48 handoff's "it may actually be a more recent commit than 8243693b." Short, surgical, pointing at something subtly wrong.

**Implication.** When user returns with a code-comment-style correction, treat it as EVIDENCE of under-specification or over-assertion in prior output. Do NOT treat it as a request for explanation — treat it as a pointer to something to verify and fix. Verify the claim (I did `Grep TurnExecutionResult`), then rewrite honestly.

**Watch for.** Any user message that looks like a review finding (structured title + body + confidence). Always verify the finding against current code before dismissing or agreeing.

### Pathology preservation rule is memory-persistent, not just session-scoped

**Mechanism.** Saved to memory early this session as `feedback_benchmark_pathology_preservation.md`. Applied implicitly when B3 candidate's error termination arrived — no debate about whether to rerun; the rule was already in force.

**Evidence.** Memory file saved in Phase 1 in direct response to user's explicit directive. Then when Phase 4's candidate artifacts showed error termination, the first-instinct framing was "pathology preservation applies" without re-reading the rule. The memory did its job.

**Implication.** Operational rules that should govern multiple sessions (B5, B8 still upcoming) belong in memory, not in the handoff alone. Handoffs are session-resumption; memories are cross-session governance. For any rule like "always do X in situation Y," save to memory AND reference it in the handoff.

**Watch for.** Rules that apply beyond the current session but only mentioned in chat. Always save them to memory with structured frontmatter + pointer in MEMORY.md.

## Next Steps

### 1. B5 baseline prep and run (critical path, next session opener)

**Dependencies:** None. B3 pair complete and captured. Staging intact. `T-20260416-01` ticket exists as persistent record of the bug. Branch `docs/ticket-dialogue-reply-extraction-mismatch` can sit on the side or be merged at operator's discretion.

**What to do in the next session's opening turn:**
1. Paste the B5 baseline invocation from `/private/tmp/benchmark-v1-staging-20260415/invocations.md:114-131` (or wherever B5 sits in the file — verify line range on load) with `{run_type}` → `This is a scored benchmark run.`
2. **Same exception as B3:** B5 requires a fresh Claude session per operator-procedure.md:174. Resume session surfaces invocation; operator runs it in a different fresh session.

**Pre-built invocation (substitute `{run_type}` → `This is a scored benchmark run.`):**

Note: exact B5 text needs to be read from `invocations.md` at load time. The B5 row per the 12:17 handoff's §Codebase Knowledge:
- **Category:** Policy audit
- **Posture:** evaluative
- **Turn budget:** 6
- **allowed_roots:**
  - `packages/plugins/codex-collaboration/docs/advisory-runtime-policy.md`
  - `packages/plugins/codex-collaboration/server/control_plane.py`
  - `packages/plugins/codex-collaboration/server/runtime.py`
- **Baseline max_evidence:** 5
- **Candidate max_evidence:** 15

**What to read first (in the resume session before handing off to fresh session):**
- This handoff's §Codebase Knowledge → "Two Codex response shapes" and "Operator-procedure.md key provisions" tables
- The T-20260416-01 ticket (especially §B5/B8 reproduction expectations) — sets expectations for how to handle a repeat bug occurrence
- `/private/tmp/benchmark-v1-staging-20260415/invocations.md:<B5 row>` (baseline + candidate invocations pre-built)

**Per-session checklist (operator executes in the fresh session):**
1. Fresh `claude` session
2. `cat ~/.claude/plugins/data/codex-collaboration-inline/session_id` → record
3. Paste invocation (substituted)
4. Wait (~5-10 min expected for evaluative; baseline 693551cc stdin fix applies)
5. Export transcript → `B5-baseline-transcript.md`, synthesis → `B5-baseline-synthesis.md`
6. Write metadata with `evidence_count` = pipeline-data `scout_count` (fa75111b amendment)

**Comparison targets (cross-posture):**
- Does baseline stay at 0 scouts? (Architectural signature check — B1 and B3 both 0; B5 is evaluative again)
- Does baseline's Codex stay in scope? (B1: 8+ out-of-scope, B3: 4 out-of-scope — is the narrowing trend posture-driven?)
- Does evaluative posture produce different structural claim output than adversarial? (Cross-posture calibration)

**Potential obstacles:**
- **Latent baseline-system issues:** Each row's first-run is a gate for latent baseline-system bugs. Time-box 15 min per incident. The pathology-preservation rule applies equally here.
- **B5 scope is safety-adjacent:** Policy audit + control_plane.py + runtime.py. Any findings about advisory-runtime policy enforcement must be reviewed carefully in Phase 3.

### 2. B5 candidate prep and run (after B5 baseline valid)

**Dependencies:** B5 baseline complete.

**What to do:** Paste B5 candidate invocation from `invocations.md`. Fresh session. Same 6-turn budget, `max_evidence: 15`.

**Specific watch:** This is the HIGHEST-INTEREST run after B3 candidate. The question: does the candidate's extraction-bug reproduce on evaluative posture (lower probability per ticket §B5/B8 expectations)? If it DOES reproduce, log inline in T-20260416-01. If it doesn't, we have one fragility data point, not a reproducible rate — unchanged fix plan.

**Comparison targets:** Same three dimensions from B1 + B3 (scope, scouting, structure) plus cross-posture (does candidate maintain scope discipline across adversarial + evaluative?).

### 3. B8 pair (supersession analysis, comparative, 8-turn budget)

**Dependencies:** B5 pair complete. Anchored decomposition rule applies — three path groups, scouting stays within a group at a time.

**What to do:** Same pattern as B1/B3/B5. Longest dialogue of the four. Per ticket §B5/B8: highest probability of hitting the items-array extraction bug. If it reproduces, log inline in T-20260416-01 as additional benchmark evidence.

**Special note for B8:** Transcript review in Phase 3 must verify no cross-group target expansion (invocations.md rule).

### 4. Phase 3-5 adjudication after all 8 runs valid

**Dependencies:** All 4 pairs valid.

**What to do:** operator-procedure.md §3 (claim inventory, labeling, safety, completeness, scope compliance review) → §4 (aggregate scoring) → §5 (import to repo).

**Special Phase 3 note for B3 candidate:** The error termination is recorded; the 7 supported claims are substantive and should be adjudicated on their merits. Do NOT exclude from adjudication because of non-convergence — that would be another form of sanding away contradictory signal. The partial-dialogue data is real data.

### 5. Commit reconciliation in T-20260330 (inline, when benchmark track resumes)

**Dependencies:** Benchmark track resuming (= after B5 or B8 start).

**What to do:** Add the commit-reconciliation question as an explicit open decision in `T-20260330`:
- Manifest records `run_commit: 693551cc`
- B1 baseline ran on `693551cc` era
- B1 candidate, B3 baseline, B3 candidate ran on `fa75111b` (2 doc-only commits ahead)
- Three resolution options: update manifest to `fa75111b`, rerun B1 baseline on `fa75111b`, document as procedural doc-only-drift exception
- Route decision to benchmark parent track owner (user)

Do NOT open a separate ticket. Per Decision 5 — ownership belongs to T-20260330.

### 6. Retirement decision (AC-7) after Phase 4

**Dependencies:** Phase 4 aggregate metrics recorded.

**What to do:** Render retirement decision per T-04 ticket's AC-7. Current directional signal after 2 pairs:
- B1: positive for supersession (candidate dominates scope + scouting + structure)
- B3: mixed (candidate wins scope + scouting; baseline wins convergence due to specific fragility documented in T-20260416-01)
- If B5 + B8 confirm scope/scouting advantage without new fragilities, supersession decision is defensible (with documented caveat for the extraction bug)
- If B5/B8 reveal additional candidate fragilities, reassess

### 7. T-20260416-01 fix (post-benchmark)

**Dependencies:** Benchmark track complete (all 4 pairs valid + adjudicated).

**What to do:** Implement Option A per ticket §Proposed fix. Estimated ~15-25 production lines + ~30-50 test lines. Specifically:
1. Move `_read_turn_agent_message` from `dialogue.py:973-990` to a shared helper (e.g., add to `codex_compat.py` or create `turn_extraction.py`)
2. Call it from `runtime.py:173-177` when populating `agent_message`
3. Preserve commit-before-parse invariant (Option A doesn't touch persistence)
4. Add 5 tests per ticket's implementation-tests list
5. Update T-20260416-01 with final commit SHA, mark `status: closed`

## In Progress

**Clean stopping point — B3 pair captured, extraction bug ticketed, B5 ready for next session.**

- **Approach:** Review-and-triage-and-ticket pattern: consume out-of-session artifacts, validate against contract, produce signal, document bugs without contaminating benchmark, prep next row.
- **State:** B3 baseline valid + converged. B3 candidate valid-as-recorded + non-converged with bug documented. Staging intact. Ticket committed on branch `docs/ticket-dialogue-reply-extraction-mismatch`.
- **Working:** Pathology-preservation rule applied cleanly. Contract-integrity pushback from user corrected initial framing error. Ticket passed two review passes + commit approval.
- **Not working:** Nothing broken. Two pairs remaining (B5, B8), but that's expected progress. The extraction bug is logged, not fixed — by design.
- **Next action:** Operator opens fresh `claude` session, pastes B5 baseline invocation from this handoff's §Next Steps #1, runs to completion, exports artifacts, returns to a review session.

## Open Questions

### 1. Will B5 or B8 candidate reproduce the extraction bug?

**Context:** T-20260416-01 §B5/B8 predicts: B5 lower probability (evaluative replies tend shorter); B8 higher probability (8-turn budget, complex context, most turns).

**Impact:** HIGH for the fragility signal. Single reproduction in B3 is one data point. If B5 AND B8 reproduce, the bug has a clear incidence rate under benchmark conditions. If neither reproduces, B3 was an unusually-long-reply edge case.

**Decision pending until:** B5 and B8 complete.

### 2. Is the commit-reconciliation question going to force a B1 baseline rerun?

**Context:** B1 baseline ran on `693551cc` era; B1 candidate + B3 pair ran on `fa75111b`. Strict :66 reading says either update the manifest or rerun B1 baseline.

**Impact:** Moderate. If rerun required, 2 hours of operator time + introduces a new B1 baseline transcript. Fresh transcript may show different behavior (though unlikely given doc-only drift).

**Decision pending until:** T-20260330 resumes (when benchmark track starts B5).

### 3. Should T-20260416-01 fix happen before OR after the B5 + B8 runs if they also error-terminate?

**Context:** If B5 + B8 both error-terminate on the same bug, that's a pattern. The natural temptation: patch before B8 to let the candidate actually complete B8. But that violates :66 same-commit rule.

**Impact:** HIGH if B8 errors — B8 is the only comparative (supersession analysis) row; its data is valuable.

**Decision pending until:** If B5 errors AND B8 is still upcoming. At that point, decide: (a) accept potential B8 error (log as more signal), (b) abort scored benchmark, patch, restart from B1 on new commit.

### 4. Does the `session_id` field semantic gap for baseline runs matter for Phase 3?

**Context:** B1 baseline and B3 baseline both recorded `session_id` = this loader session's ID, not fresh-session ID, because `/cross-model:dialogue` doesn't fire codex-collaboration's SessionStart hook. Thread_id is separate and correct.

**Impact:** Low for scoring; potential confusion for Phase 3 adjudicators who expect `session_id` to uniquely identify runs.

**Decision pending until:** Phase 3 starts. Mitigation: document the semantic in Phase 3 notes, use `thread_id` for cross-run auditing on baseline side.

### 5. Should `scope_envelope` be wired through the candidate skill? (Carried forward from 12:17)

**Context:** Both gatherer agents support `scope_envelope` but the candidate skill doesn't pass it. v1-compliant (prompt-only) but a known fragility.

**Impact:** Low for v1. Could become higher if B5/B8 show scope discipline breaking down.

**Decision pending until:** After benchmark execution.

### 6. Does the "positive for supersession" directional signal persist across postures? (Sharpened from 12:17)

**Context:** B1 (evaluative): strongly positive. B3 (adversarial): mixed — candidate wins scope+scouting, loses convergence due to bug. B5 (evaluative-policy) and B8 (comparative) upcoming.

**Impact:** HIGH. This is THE retirement question.

**Decision pending until:** All 4 pairs complete and adjudicated.

## Risks

### 1. Confirmation-bias risk, now with active mitigation

**Impact:** Having recorded B1 as positive and B3 as mixed, I may unconsciously weight B5/B8 toward confirming either direction. This session's experience (initial fork error → user correction) shows I'm susceptible to the pattern even when warned.

**Mitigation:** This handoff captures the lesson explicitly in §Learnings #1. Next-session opening action should re-read the 12:17 handoff's §Risks #1 + this handoff's §Learnings #1 before reviewing any B5/B8 artifact.

### 2. Branch `docs/ticket-dialogue-reply-extraction-mismatch` sits unmerged

**Impact:** Ticket exists only on the branch, not on main. If the branch is deleted accidentally or the worktree cleaned up, the ticket could be lost.

**Mitigation:** Merge the branch before B5 pair run. Or leave it standing and merge after benchmark completes with whatever other tickets accumulate. Either is fine but don't delete without merging.

### 3. `/tmp/` staging reboot vulnerability (carried forward)

**Impact:** Machine reboot clears `/private/tmp/`, losing B1 + B3 artifacts. Phase 5 import relies on staging intactness.

**Mitigation:** Before extended breaks, `cp -r /private/tmp/benchmark-v1-staging-20260415 ~/benchmark-v1-staging-backup`. Worth doing NOW that there are 4 runs staged.

### 4. Extraction bug may reproduce in B5/B8 without clear resolution path

**Impact:** If both reproduce the same bug, the benchmark produces multiple non-converged candidate runs. Aggregate metrics will show "candidate converged in 0/4 adversarial-style cases" or similar — which is ACCURATE but requires careful framing for AC-7 to avoid over-reading.

**Mitigation:** T-20260416-01 §B5/B8 pre-commits the framing: "repeated occurrences logged as benchmark evidence, not patched mid-track." Phase 4 aggregate scoring should distinguish "fragility due to known bug X" from "fragility due to unknown system-level issue" — different implications for retirement decision.

### 5. Manual adjudication dominant cost (carried forward)

**Impact:** 4 rows × 2 systems = 8 syntheses, 80-160 claim adjudications, 2-4 hours.

**Mitigation:** Row-by-row, high-signal rows first. B3 candidate's non-convergence changes B3 adjudication scope — only 7 claims to adjudicate (not 11+ from converged runs).

### 6. `run_commit` drift compounding

**Impact:** Each new main-branch commit that lands during benchmark track (even doc-only) adds to the drift unless manifest is updated. Any non-doc commit (system behavior change) would force a restart or careful triage.

**Mitigation:** Opening check of next session: `git log --oneline -10` vs `manifest.json:7`. Halt benchmark if any non-doc commits land. Review via `git diff <manifest_commit>..HEAD` before every B5/B8 run.

## References

### Commits this session

- `84d79fa6 docs(codex-collaboration): add T-20260416-01 for dialogue.reply extraction mismatch` (this session) — on branch `docs/ticket-dialogue-reply-extraction-mismatch`, NOT merged to main

### Authority documents

| Document | Location | Role |
|---|---|---|
| Benchmark contract v1 | `docs/superpowers/specs/codex-collaboration/dialogue-supersession-benchmark.md` | Corpus structure, scope rules, prompt-only enforcement |
| Operator procedure | `docs/benchmarks/dialogue-supersession/v1/operator-procedure.md` | Execution procedure, invalidation triggers (:660-666), `run_commit` rule (:66), diagnostic metrics (:519), rerun procedure (:669-676) |
| Manifest | `docs/benchmarks/dialogue-supersession/v1/manifest.json` | `run_commit: 693551cc` (drift-pending reconciliation), 4-row corpus structure |
| T-04 supersession ticket | `docs/tickets/2026-03-30-codex-collaboration-dialogue-parity-and-scouting-retirement.md` | T-04 acceptance authority; parent for T-20260416-01 |
| T-20260416-01 | `docs/tickets/2026-04-16-codex-collaboration-dialogue-reply-extraction-mismatch.md` | Post-benchmark bug fix ticket (this session) |

### Staging artifacts (B1 + B3 pairs complete, B5 + B8 pending)

| Artifact | Path | Status |
|---|---|---|
| Invocations packet | `/private/tmp/benchmark-v1-staging-20260415/invocations.md` | Unchanged; contains all 8 invocations |
| Transcript extractor | `/private/tmp/benchmark-v1-staging-20260415/_extract_transcript.py` | User-authored; has `"# B1 Candidate"` hardcoded on :54 — post-benchmark tidy |
| B1 baseline artifacts | `B1-baseline-{transcript,synthesis,metadata}` | Complete, valid |
| B1 candidate artifacts | `B1-candidate-{transcript,synthesis,metadata}` | Complete, valid |
| B3 baseline artifacts | `B3-baseline-{transcript,synthesis,metadata}` | Complete, valid (this session) |
| B3 candidate artifacts | `B3-candidate-{transcript,synthesis,metadata}` | Complete, valid-as-recorded (non-converged error; this session) |

### Codex session rollouts

- B3 baseline: thread `019d977b-23a3-7942-977d-21641446cae0`
- B3 candidate: `/Users/jp/.codex/sessions/2026/04/16/rollout-2026-04-16T14-45-39-019d979c-f50c-7213-9729-be04ad765642.jsonl` (thread `019d979c-f50c-7213-9729-be04ad765642`, run `a39c2738-1af9-4e45-931e-833d6828c6d6`)

### Code files explored (for T-20260416-01 RCA)

| File | Lines read | Key findings |
|---|---|---|
| `packages/plugins/codex-collaboration/server/dialogue.py` | 470-520, 960-990 | `reply()` parse path, `_read_turn_agent_message` helper with two-shape fallback |
| `packages/plugins/codex-collaboration/server/prompt_builder.py` | 40-115 | `parse_consult_response` function, empty-string error message source |
| `packages/plugins/codex-collaboration/server/mcp_server.py` | 250-290 | Tool handler dispatch for `codex.dialogue.reply` |
| `packages/plugins/codex-collaboration/server/models.py` | 106-115 | `TurnExecutionResult` dataclass (3 fields only) |
| `packages/plugins/codex-collaboration/server/runtime.py` | 170-185 | `agent_message` extraction at dispatch (Option A fix site) |

### Memory files

- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/feedback_benchmark_pathology_preservation.md` (created this session)
- `~/.claude/projects/-Users-jp-Projects-active-claude-code-tool-dev/memory/MEMORY.md` (updated with feedback pointer)

### Prior handoffs (chain)

- Immediate predecessor (resumed from): `docs/handoffs/archive/2026-04-16_12-17_t04-b1-pair-complete-b3-adversarial-next.md`
- Prior (same-day chain): `docs/handoffs/archive/2026-04-16_11-48_t04-b1-baseline-valid-after-evidence-count-reconciliation.md`
- Earlier arc: `docs/handoffs/archive/2026-04-16_00-18_*`, `2026-04-15_*`, `2026-04-14_*` for T-04 scaffold / runtime gate / Phase 1 prep

## Gotchas

### Extraction mismatch between `dialogue.reply` and `dialogue.read` paths

**Symptom:** `codex.dialogue.reply` terminates with `"Consult result parse failed: expected JSON object. Got: ''"` when Codex delivers a long or complex agent message.

**Root cause:** `reply()` reads `turn_result.agent_message` directly (handles shape 1 only). `read()` uses `_read_turn_agent_message` with fallback to `items[type=agentMessage].text` (handles both shapes). Candidate's dispatch layer populates `agent_message` only for shape 1.

**Prevention:** Per T-20260416-01, Option A canonicalizes at dispatch. Until patch lands: B5/B8 candidate runs may reproduce. Follow pathology-preservation rule (preserve artifacts, don't mid-track-patch).

### `TurnExecutionResult` has no raw-turn projection

**Symptom:** Any proposed fix that says "reply() can grab the raw_turn dict from the dispatch layer" is wrong.

**Root cause:** `models.py:106-111` — `TurnExecutionResult` has exactly three fields: `turn_id`, `agent_message`, `notifications`. No items-array, no raw response. Fix requires either runtime-layer change (Option A) or model enrichment (Option B) or persistence-layer read (Option C).

**Prevention:** For any future proposed fix involving `TurnExecutionResult`, verify its fields first. Trust but verify.

### Baseline `session_id` field is weaker identity than candidate's

**Symptom:** B1 baseline and B3 baseline metadata recorded `session_id` values that don't match their actual fresh-session IDs.

**Root cause:** `/cross-model:dialogue` (baseline skill) doesn't fire codex-collaboration's SessionStart hook that writes to `~/.claude/plugins/data/codex-collaboration-inline/session_id`. In a fresh baseline session, `cat`'ing that file returns whatever was last written — typically the loader session's ID.

**Prevention:** For baseline runs, rely on `thread_id` (captured in synthesis/transcript) as the canonical run identifier. Note the semantic in Phase 3 adjudication.

### Commit drift between manifest and run transcript

**Symptom:** Manifest records `run_commit: 693551cc` but B1 candidate + B3 baseline + B3 candidate all ran on `fa75111b`.

**Root cause:** Two doc-only commits (`f0fde082` manifest update, `fa75111b` operator-procedure amendment) landed between B1 baseline and B1 candidate. The manifest wasn't bumped to `fa75111b`. Strict reading of :66 says this is a run-condition breach; lenient reading (doc-only drift doesn't count) lets runs proceed.

**Prevention:** Reconciliation routed to T-20260330 (parent benchmark track) per Decision 5. Three options: update manifest, rerun B1 baseline, document as procedural exception. Decision owned by parent track, not this handoff.

### Candidate transcript format differs from baseline format

**Symptom:** Regex patterns that work on B1 + B3 baseline transcripts may return 0 matches on candidate transcripts.

**Root cause:** Candidate transcript is extracted from Codex session rollout JSONL via `_extract_transcript.py`. Structure has 12 `exec_command` scouts EMBEDDED within ASSISTANT REPLY blocks (not as separate items). Baseline is dialogue-format with different structure.

**Prevention:** Use permissive grep patterns (no strict anchors). Or read transcript sections directly. Or parameterize `_extract_transcript.py` to emit a consistent format (post-benchmark tidy item).

### `_extract_transcript.py` has hardcoded `"# B1 Candidate"` header

**Symptom:** Transcripts extracted via `_extract_transcript.py` all say "# B1 Candidate" regardless of which run they represent.

**Root cause:** Line 54 of the helper has the header string hardcoded. Someone already hand-corrected the B1-baseline export.

**Prevention:** Check extracted transcript headers after each extraction. Post-benchmark: parameterize the script to accept a `--title` argument or derive from filename.

### `resumed_from` chain breaks when state file is missing

**Symptom:** Handoff has no `resumed_from` field even though a predecessor exists.

**Root cause:** `resumed_from` is populated only when `/load` writes a state file that `/save` subsequently reads. The state file was cleaned up in `load.md`'s step 2 mechanism, but if a previous save's cleanup removed it, next save has no state file to read.

**Prevention:** Filename timestamps + same-day chain references in §References → Prior handoffs provide implicit ordering. For reconstructing cross-save chains, use the `files:` frontmatter field.

## Conversation Highlights

### User's pathology-preservation directive (session-defining)

User: "One operating rule for B3: if the baseline shows another obvious tooling pathology mid-run like the B1 scout timeout pattern, stop and preserve the artifacts rather than improvising around it. That kind of failure is benchmark signal."

Saved to memory immediately. Applied silently when B3 candidate's error termination arrived. This rule shaped the entire session's posture toward the candidate's bug: preserve, don't patch-and-rerun.

### User's contract-integrity pushback (framing-correcting)

User: "The invalidation triggers in the procedure are explicit at operator-procedure.md:660, and this run does not meet them. So I would not relabel it invalid just for scoring hygiene. ... The procedure says 'All runs must use the same commit' at operator-procedure.md:64. That means a mid-benchmark patch is not 'fix + rerun B3 candidate' in the scored packet. It is either: (a) a diagnostic post-fix rerun outside the current scored benchmark, or (b) a decision to restart the scored benchmark from B1 on the new commit."

Most structurally important correction of the session. Exposed category confusion in my initial fork framing. Led to the benchmark-status-vs-product-defect split that the ticket encodes. The 12:17 handoff's §Risks #1 flagged this exact failure mode; user's correction was the mechanism that prevented it.

### User's first code-review pass (two findings)

User: "[P1] Commit mismatch undermines the ticket's validity argument" (0.98) and "[P2] Minimal fix description assumes data `reply()` does not currently have" (0.95).

Both findings verified (commit mismatch was internally contradictory; `TurnExecutionResult` grep confirmed 3 fields only). Revision produced the §Commit reconciliation subsection and the three-options fix framing. Code-comment format was precisely actionable.

### User's second code-review pass (two more findings)

User: "[P2] Benchmark-status paragraph still resolves the commit dispute too early" (0.94) and "[P2] Follow-up section hardcodes one unresolved commit-reconciliation outcome" (0.97).

Both findings about preempting decisions that belong to the parent track. Led to the final wording: "is preserved as captured... Final scored-validity classification... belongs to the parent benchmark track T-20260330." This is the cleanest statement of the split and will reuse well for future benchmark-surfaced bug tickets.

### User's commit-reconciliation ownership directive

User: "It is benchmark-governance work, not a distinct product defect. Put it inline in `T-20260330` as an explicit open decision or benchmark exception note. That keeps the ownership in the track that can actually decide it, and avoids scattering one benchmark-integrity question across multiple tickets."

Prevents ticket proliferation. The reconciliation question is logged in this handoff's §Next Steps #5 as an inline action for next-session Claude when the benchmark track resumes.

### User's approval to commit

User: "**Findings** No findings. ... Commit it now. No further review pass is needed from me before commit."

Closing the review loop. Three-round revision completed. Ticket committed at `84d79fa6`.

## User Preferences

### Contract-first reasoning over intuition-first triage

When a benchmark run surfaces a potential invalidation question, the user's default is to read the contract provisions directly (quote lines, cite numbers) rather than reason from procedural analogies. This session's "operator-procedure.md:660-666 invalidation triggers are explicit and exhaustive" was a direct contract read that corrected an intuition-led framing. Pattern: when in doubt, quote the contract.

### Reviewer-style corrections with confidence scores

Both review passes used code-comment format with explicit confidence scores (0.94, 0.95, 0.97, 0.98). This is a signal that the review is structured and grounded, not intuition. Response pattern: treat every code-comment finding as a verified claim to be addressed, rewrite the affected text, report back with a structured summary of changes.

### Preserve distinctions even when language is tempting

Two separate facts (benchmark-valid run + product defect) must stay separate in the ticket, even though collapsing them would read more smoothly. User's instruction: "capture the distinction explicitly so nobody later 'cleans up' the benchmark by reclassifying the run." This is the root pattern for any document that touches multiple ticket scopes.

### Ownership routing over ticket proliferation

When a discovered issue crosses ticket boundaries, user prefers routing to the ticket that OWNS the decision rather than opening a new one. Commit-reconciliation → T-20260330, not a new ticket. Keeps ownership clear; keeps the decision surface narrow.

### Narrow fix boundaries over broad refactors

Option A (canonicalize at dispatch) preferred over Option B (enrich TurnExecutionResult) — narrower surface even though B is controller-local. User explicitly approved A: "The fix-framing revision is materially better. The `TurnExecutionResult` limitation is now described honestly, `effort: medium` fits, and Option A is a coherent recommendation." Pattern: when multiple fix paths exist, prefer the narrowest one that addresses root cause.

### Explicit acknowledgement of drafting errors

When my initial draft contained an error (raw_turn claim), user pointed it out and I rewrote WITH an explicit "Correction to the initial draft" paragraph. User didn't ask for this, but the pattern of marking revisions that came from review findings is valuable — it shows the revision is responsive to specific feedback, not silent rewording. Preserved in final ticket text.

### Pace preference: thorough review over fast iteration

Three-round ticket review (initial draft → P1/P2 revisions → P2/P2 revisions → approval) before commit. User didn't rush past findings; took time to catch the scored-validity preemption in the second pass despite first pass not flagging it. Response pattern: don't push for commit until user signals readiness.

## Rejected Approaches

### Option B (mark B3 candidate invalid + supersede + rerun on patched commit)

**Why rejected:** Violates `run_commit` invariant at :66. Violates exhaustiveness of invalidation triggers at :660-666. Triggers confirmation-bias pattern explicitly flagged in 12:17 handoff §Risks #1.

**Trade-off:** Would have produced a cleanly-converged B3 candidate row for aggregate scoring. Scoring cleanliness is not worth the loss of contradictory signal and the contract violation.

### Option B (fix: enrich TurnExecutionResult with items projection)

**Why rejected:** Broader surface than needed. Exposes dispatch-layer shape to all consumers. Option A fixes root cause at source with same long-term surface.

**Trade-off:** B is controller-local in terms of where the fallback call happens. But the model change is a bigger churn than moving one helper function.

### Option C (fix: post-commit journal read in reply())

**Why rejected:** Couples `reply()` to persistence-layer retrieval. Adds storage round-trip per reply. Fixes symptom not cause.

**Trade-off:** C is the only option that would work if the dispatch layer cannot be modified for some reason. Not the case here.

### Opening a separate ticket for commit-reconciliation

**Why rejected:** User's framing — benchmark-governance work, not product defect. Scatters ownership across tickets. Parent track already owns the decision.

**Trade-off:** Standalone ticket would have a persistent URL and clearer lifecycle. Inline approach risks being overlooked if T-20260330 gets tidied up. Mitigated by flagging in this handoff's §Next Steps.

### Not saving pathology-preservation rule to memory (keeping it session-scoped)

**Why rejected:** Rule applies across multiple sessions (B5, B8 upcoming). A chat-only mention wouldn't survive a context compaction or session restart. Saving to memory makes it operational across the whole benchmark track.

**Trade-off:** Memory clutter risk. Mitigated by structured frontmatter and MEMORY.md index hygiene.
