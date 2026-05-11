---
date: 2026-04-22
time: "12:10"
created_at: "2026-04-22T16:10:10Z"
session_id: 6dd78ed5-3575-4b10-90ab-ea84093887a5
resumed_from: "docs/handoffs/archive/2026-04-22_01-32_t07-7a-reviewed-and-merged.md"
project: claude-code-tool-dev
branch: feature/t07-review-7b
commit: 61eaa590
title: "T-07 7b plan reviewed and approved — codex-review skill ready for implementation"
type: handoff
files:
  - docs/plans/2026-04-22-t07-codex-review-7b.md
  - packages/plugins/codex-collaboration/server/context_assembly.py
  - packages/plugins/codex-collaboration/server/mcp_server.py
  - packages/plugins/codex-collaboration/server/models.py
  - packages/plugins/codex-collaboration/server/control_plane.py
  - packages/plugins/codex-collaboration/server/profiles.py
  - packages/plugins/codex-collaboration/skills/consult-codex/SKILL.md
  - packages/plugins/codex-collaboration/skills/codex-analytics/SKILL.md
  - packages/plugins/cross-model/agents/codex-reviewer.md
  - packages/plugins/cross-model/skills/consultation-stats/SKILL.md
  - packages/plugins/codex-collaboration/references/consultation-profiles.yaml
---

# T-07 7b Plan Reviewed and Approved

## Goal

Draft and review an implementation plan for slice 7b: the `codex-review` skill in the
codex-collaboration plugin. This skill replaces the cross-model `codex-reviewer` agent
with a review-orchestration skill over `codex.consult` with `workflow="review"`.

**Trigger:** Slice 7a merged to main at `61eaa590` (PR #116). The `workflow` contract,
`ConsultWorkflow` type, `DelegationOutcomeRecord`, and analytics skill are all in place.
7b is the next slice in the T-07 sequence.

**Stakes:** 7b owns the review workflow that downstream slices 7c-7e depend on for
parity matrix completeness. The review design decision (skill over advisory runtime,
not a separate runtime primitive) was made during the T-07 reconciliation and must be
respected — any drift toward a native `review/start` API path would violate the
architecture.

**Success criteria (for this session):** A plan that survives scrutiny and is credible
for implementation. Not the implementation itself.

**Connection to project arc:** Tenth session in the codex-collaboration build sequence.
The preceding session (9th) reviewed and merged PR #116 (slice 7a). This session
produces the implementation plan for 7b. T-07 is the final ticket with 5 slices
(7a-7e). 7a is merged; 7b is the plan stage; 7c-7e are not started.

## Session Narrative

**Phase 0 — Handoff load and orientation (~10 min).** Loaded the 7a handoff
(`2026-04-22_01-32_t07-7a-reviewed-and-merged.md`). The user directed a thorough
orientation read before starting any work. Read 11 files in parallel across 3 rounds:
the T-07 ticket, the analytics skill and script (reference pattern), all 4 server files
(MCP server, models, control plane, delegation controller), the cross-model reviewer
agent (semantic source), the consult-codex skill (closest pattern), the plugin manifest,
the cross-model consultation-stats skill (analytics predecessor), and the consultation
profiles YAML.

Key orientation findings: (1) the MCP schema only exposes 5 fields (`repo_root`,
`objective`, `explicit_paths`, `profile`, `workflow`) — the richer `ConsultRequest`
fields are not reachable through MCP dispatch; (2) two relevant profiles exist:
`code-review` (effort=high, posture=evaluative, turn_budget=4) and `deep-review`
(effort=xhigh, posture=evaluative, turn_budget=8); (3) the `workflow="review"` runtime
path is already tested end-to-end by 7 tests across 4 files; (4) no server changes are
needed — the skill is a pure instruction document.

**Phase 1 — User analysis of orientation (~5 min).** The user reviewed the orientation
summary and identified 8 gaps:
1. `objective` is more constrained than "assembled briefing" sounds — MCP only exposes 5 fields
2. The skill needs its own review-scope grammar for all entry conditions
3. `profile="deep-review"` should be considered, not omitted
4. Secret handling is needed even though server-side safety exists
5. Allowed tools must match the context-gathering behavior (not just the consult dispatch)
6. Analytics verification needs a real acceptance story
7. Must prohibit native `review/start` API usage
8. Output contract should be stricter than "present findings"

The user reframed the target: "build a review-orchestration skill, not just a consult
wrapper." This reframing shaped the entire plan — the skill is semantically closer to
the cross-model reviewer agent than to the thin consult-codex wrapper.

**Phase 2 — Plan drafting (~15 min).** Created `feature/t07-review-7b` branch from
main. Wrote a 9-section plan at `docs/plans/2026-04-22-t07-codex-review-7b.md` covering
all 8 gaps: skill identity/frontmatter, scope/non-goals, preconditions, review scope
selection, context gathering, layer-0 secret safety, consult dispatch, synthesis contract,
and verification/acceptance. Key design decisions: `code-review` as default profile
(verified from `consultation-profiles.yaml`), `explicit_paths` for changed file metadata
separate from `objective` as briefing container.

**Phase 3 — First scrutiny round (~10 min).** The user performed a structured scrutiny
(major revision verdict) and identified 7 required changes:
1. PR review advertised but not specified → remove from trigger language
2. `explicit_paths` breaks on deleted files → filter to extant paths only
3. Smoke deferral undermines 7b AC → make smoke failure block closure
4. Default-branch staged/unstaged logic is contradictory → use deterministic `git diff HEAD`
5. Untracked files can explode on generated dirs → add caps and filters
6. Smoke evidence is underdefined → add before/after analytics row verification
7. Broad Bash without read-only guidance → constrain to git read commands

I verified the `explicit_paths` failure mode by reading `context_assembly.py:362-390`:
`_read_file_excerpt` raises `ContextAssemblyError("file reference missing")` at line
376-379 if the path doesn't exist. Applied all 7 changes to the plan.

**Phase 4 — Second scrutiny round (~10 min).** The user performed a second scrutiny
(minor revision verdict) and identified 4 remaining issues:
1. Objective payload can exceed the server's 48KB hard cap → add byte budget
2. `explicit_paths` extraction not tied to selected diff scope → use `--name-status` variant
3. Smoke evidence assumes existing quiet analytics stream → handle missing file and concurrent appends
4. AC line reference is stale → replace with search string

I verified the objective-size issue by reading `context_assembly.py:12-19` (caps: 24KB
soft/48KB hard for advisory) and lines 200-227 (trimming loop removes context entries
only, not objective). Confirmed: a large objective can cause all `explicit_paths` entries
to be trimmed, then crash with `ContextAssemblyError` if it exceeds the hard cap. Added
a 20KB hard limit / 16KB soft target for the objective, with a truncation cascade
(surrounding code → diff sections → convention text). Applied all 4 changes.

**Phase 5 — Final scrutiny (defensible verdict).** The user's third scrutiny found no
critical failures, no high-risk assumptions, and no required changes. One recommended
cleanup: replace the overview search string to match the actual ticket text. Applied
the fix. Plan approved.

## Decisions

### `code-review` profile as default, not `deep-review`

**Choice:** Default to `profile="code-review"` (effort=high, turn_budget=4) with
`deep-review` (effort=xhigh, turn_budget=8) as explicit user-requested override.

**Driver:** `code-review` profile description is "focused code or document review"
with evaluative posture — matches the skill's intent exactly. `deep-review` is
"thorough multi-turn review with high reasoning effort" — heavier than needed for
most diff reviews. Verified from `consultation-profiles.yaml:62-71`.

**Alternatives considered:**
- **`deep-review` as default** — user's initial suggestion. Revised after I found the
  `code-review` profile exists with a tighter budget. User agreed: the profile is "the
  right default."
- **No profile (omit parameter)** — would use contract defaults
  (posture=collaborative, turn_budget=6, no effort). Rejected because review requires
  evaluative posture, not collaborative.

**Trade-offs accepted:** `code-review` has turn_budget=4 which limits back-and-forth.
For large architecture reviews, users must explicitly request `deep-review`.

**Confidence:** High (E2) — verified both profiles against the YAML source and
confirmed `code-review` semantics match the use case.

**Reversibility:** High — single parameter change in skill instructions.

**Change trigger:** If users consistently request `deep-review` overrides, the default
should be revisited.

### Review as skill over `codex.consult`, not a separate runtime primitive

**Choice:** Implement `codex-review` as a SKILL.md instruction document that calls
`codex.consult` with `workflow="review"`, not as a new MCP tool, agent, or App Server
API.

**Driver:** Architecture decision from the T-07 reconciliation (ticket lines 111-121):
"The `codex-reviewer` agent in cross-model is replaced by a `codex-review` skill in
codex-collaboration. Review is a workflow over the advisory runtime, not a separate
runtime primitive."

**Alternatives considered:**
- **New MCP tool `codex.review`** — separate dispatch path and server handler. Rejected
  because the ticket design explicitly models review as a consultation workflow, not a
  primitive.
- **Agent (subagent)** — the cross-model predecessor is an agent. Rejected because the
  codex-collaboration architecture decision moved from agent to skill.

**Trade-offs accepted:** Review material must fit into the 5-field MCP schema
(`repo_root`, `objective`, `explicit_paths`, `profile`, `workflow`). This forces the
skill to pack the entire review briefing into `objective`, subject to the 20KB
objective budget constraint.

**Confidence:** High (E1) — directly follows the documented architecture decision.

**Reversibility:** Medium — creating a new MCP tool later would require server changes,
but the skill could coexist.

**Change trigger:** If the `objective` size constraint proves too limiting for real
reviews, a dedicated `codex.review` tool with richer input fields might be needed.

### Objective byte budget: 20KB hard / 16KB soft

**Choice:** Cap the assembled briefing (review material embedded in `objective`) at
20KB hard limit and 16KB soft target before dispatch.

**Driver:** Server's `context_assembly.py` renders `objective` directly into the
advisory packet (line 238). Objective is NOT trimmed — only context entries
(`explicit_references`, etc.) are trimmed. Advisory caps: 24KB soft target, 48KB hard
cap (lines 12-18). If objective alone exceeds 24KB, all `explicit_paths` entries are
trimmed away (defeating their purpose). If it exceeds 48KB, `ContextAssemblyError`
crashes the consultation.

**Alternatives considered:**
- **No budget (trust line-count thresholds)** — inherited from cross-model reviewer.
  Rejected because line-count thresholds don't account for byte size, and the cross-model
  reviewer used a different MCP tool without the same packet caps.
- **Match 24KB soft target exactly** — rejected because the packet includes framing,
  repo identity, safety envelope, and output schema beyond the objective. 20KB leaves
  ~4KB headroom.

**Trade-offs accepted:** 20KB constrains the review material more than the 1500-line
diff limit suggests. A 500-line diff with surrounding code can approach 20KB. The
truncation cascade (surrounding code → diff sections → convention text) prioritizes
review material over context.

**Confidence:** High (E2) — verified the packet rendering at `context_assembly.py:238`,
the trimming behavior at lines 200-227, and the cap constants at lines 12-18.

**Reversibility:** High — change the number in the SKILL.md.

**Change trigger:** If the server's packet cap changes, or if a dedicated review MCP
tool with separate caps is created.

### `explicit_paths` filtering: extant files only, scope-matched extraction

**Choice:** Filter `explicit_paths` to only include files that exist on disk, extracted
from the selected diff scope's `--name-status` variant. Deleted files (`D` status)
excluded; renamed files (`R` status) use only the destination path.

**Driver:** `context_assembly._read_file_excerpt` raises `ContextAssemblyError` if a
path doesn't exist (verified at `context_assembly.py:376-379`). A diff that deletes
`foo.py` would crash the entire consultation if `foo.py` were included in
`explicit_paths`.

**Alternatives considered:**
- **Pass all changed paths unfiltered** — original plan. Would crash on deleted files.
- **Don't use `explicit_paths` at all** — would lose the server-side file metadata
  that survives even if `objective` is trimmed.

**Trade-offs accepted:** Deleted files are represented only through the diff content
in `objective`, not through `explicit_paths`. This means the server's context assembly
cannot read deleted file content (because it's gone), but the diff captures the
deletion.

**Confidence:** High (E2) — verified the failure mode in the source code and the
`--name-status` output format for all status codes.

**Reversibility:** High — change filtering logic in SKILL.md.

**Change trigger:** If the server adds graceful handling for missing `explicit_paths`.

### Smoke failure blocks 7b closure

**Choice:** Manual smoke test is a hard requirement for 7b AC closure. If the App
Server is unavailable and the smoke cannot run, 7b remains open and the PR cannot
claim the AC.

**Driver:** The 7b AC requires the skill "can review a real diff through `codex.consult`
with `workflow="review"`" — a functional requirement that cannot be satisfied by
static analysis of a Markdown file. The user explicitly stated: "if smoke cannot run,
that should block 7b closure."

**Alternatives considered:**
- **Smoke deferral allowed** — original plan said "manual smoke on a real diff (or
  document deferral)." User rejected: "It can be a PR-known gap only if the PR is
  explicitly not claiming the 7b AC."
- **Static test (grep SKILL.md for workflow="review")** — user and I agreed this is
  fragile and tests a string, not behavior.

**Trade-offs accepted:** App Server availability is now a hard dependency for 7b
closure. If unavailable, 7b stays open even though the SKILL.md is complete.

**Confidence:** High (E1) — directly follows the user's directive.

**Reversibility:** N/A — acceptance policy, not a code decision.

**Change trigger:** If the AC is reworded to not require live demonstration.

## Changes

### `docs/plans/2026-04-22-t07-codex-review-7b.md` — New file

| Aspect | Detail |
|--------|--------|
| **What** | Implementation plan for the `codex-review` skill |
| **Type** | Instruction-document implementation plan (not runtime implementation) |
| **Status** | Reviewed through 2 scrutiny rounds (7 major + 4 minor fixes), approved with "defensible" verdict |
| **Sections** | 9 sections covering all operational boundaries |
| **Key constraints** | 20KB objective budget, scope-matched `explicit_paths` extraction, smoke-blocks-closure acceptance |

No other files were modified this session. All file reads were for orientation only.

## Codebase Knowledge

### MCP `codex.consult` Input Surface (verified this session)

The MCP schema exposes only 5 input fields for `codex.consult`:

| Field | Type | Required | Source |
|-------|------|----------|--------|
| `repo_root` | string | yes | `mcp_server.py:36` |
| `objective` | string | yes | `mcp_server.py:37` |
| `explicit_paths` | array[string] | no | `mcp_server.py:38` |
| `profile` | string | no | `mcp_server.py:39-42` |
| `workflow` | string enum `["consult", "review"]` | no | `mcp_server.py:43-47` |

The richer `ConsultRequest` fields (`explicit_snippets`, `supplementary_context`,
`task_local_paths`, `broad_repository_summaries`, etc.) exist in `models.py:77-96`
but are NOT reachable through MCP dispatch — they are only used when the control
plane is called directly (e.g., from the dialogue controller).

### Context Assembly Packet Lifecycle (verified this session)

```
ConsultRequest.objective
  → context_assembly._render_packet() (line 238)
    → rendered directly into JSON payload["objective"]
    → NOT a trimmable context entry

ConsultRequest.explicit_paths
  → _build_explicit_entries() (line 321-333)
    → _read_file_excerpt() per path (line 330)
      → raises ContextAssemblyError if path missing (line 376-379)
      → raises ContextAssemblyError if path escapes repo root (line 372-375)
      → binary sniff → return placeholder (line 380-382)
      → truncate at _MAX_FILE_EXCERPT_BYTES (line 387-389)
      → _redact_text() (line 390)
    → stored in entries["explicit_references"]

Trimming loop (_trim_entries, lines 200-227):
  → renders packet, checks size against soft target
  → if over: pops last entry from REVERSED _TRIM_ORDER categories
  → categories: explicit_references, task_local_context, delegation_summaries,
    promoted_summaries, broad_repository_summaries, supplementary_context,
    external_research_material
  → explicit_references is FIRST in trim order → trimmed LAST
  → objective is NOT in trim order → NEVER trimmed

Hard cap check (line 187-191):
  → if packet still > 48KB after all entries trimmed → ContextAssemblyError
```

**Key implication:** A large `objective` will cause all context entries to be trimmed
(explicit_paths included), then potentially crash the consultation. The skill must
budget its objective size.

### Advisory Packet Size Constants (verified this session)

| Profile | Soft target | Hard cap | Source |
|---------|------------|----------|--------|
| advisory | 24KB (24576) | 48KB (49152) | `context_assembly.py:12-18` |
| execution | 12KB (12288) | 24KB (24576) | `context_assembly.py:12-18` |

### Consultation Profiles (verified this session)

Two profiles relevant to review:

| Profile | Posture | Effort | Turn budget | Source |
|---------|---------|--------|-------------|--------|
| `code-review` | evaluative | high | 4 | `consultation-profiles.yaml:62-71` |
| `deep-review` | evaluative | xhigh | 8 | `consultation-profiles.yaml:51-60` |

Profile resolution happens server-side in `control_plane.py:182-186`. The MCP
`profile` parameter is a string name resolved via `profiles.resolve_profile()`.

### Cross-Model Reviewer Agent Architecture (read for reference)

The `codex-reviewer.md` agent (210 lines) has a 5-step process:
1. Gather changes from git (scope table with 6 entries)
2. Assemble briefing (structured template with context, material, conventions)
3. Consult Codex via `mcp__plugin_cross-model_codex__codex` (1-2 turns)
4. Synthesize findings (severity ratings, source attribution, disagreements)
5. Emit analytics via `emit_analytics.py`

The codex-collaboration replacement reuses the semantic behavior but:
- Routes through `codex.consult` with `workflow="review"` instead of cross-model MCP
- Does not need step 5 (server-side `OutcomeRecord` handles analytics)
- Must respect the 20KB objective budget (cross-model had no such constraint)
- Must filter `explicit_paths` for deleted files (server raises on missing paths)

### Existing `workflow="review"` Test Coverage (verified this session)

| Test | File | Lines |
|------|------|-------|
| `test_codex_consult_schema_includes_workflow` | `test_mcp_server.py` | 1500 |
| `test_codex_consult_dispatch_passes_workflow_to_control_plane` | `test_mcp_server.py` | 1510 |
| `test_codex_consult_rejects_invalid_workflow` | `test_mcp_server.py` | 1552 |
| `test_codex_consult_threads_workflow_to_outcome_record` | `test_control_plane.py` | 1082 |
| `test_codex_consult_default_workflow_in_outcome` | `test_control_plane.py` | 1111 |
| `test_outcome_record_explicit_review_workflow` | `test_outcome_record.py` | 161 |
| `test_outcome_record_workflow_in_asdict` | `test_outcome_record.py` | 174 |
| `test_consult_request_default_workflow` | `test_outcome_record.py` | 187 |
| `test_consult_request_explicit_workflow` | `test_outcome_record.py` | 193 |
| Analytics review view tests | `test_analytics_skill.py` | multiple |

### Key File Shapes (verified this session)

| Concept | Location | Shape |
|---------|----------|-------|
| MCP `codex.consult` schema | `mcp_server.py:30-50` | 5 input fields, workflow enum |
| Workflow validation | `mcp_server.py:394-399` | `raw_workflow not in ("consult", "review")` → ValueError |
| ConsultRequest.workflow | `models.py:95` | `ConsultWorkflow = "consult"` default |
| OutcomeRecord.workflow | `models.py:223` | `ConsultWorkflow = "consult"` default |
| ConsultWorkflow type | `models.py:35` | `Literal["consult", "review"]` |
| Profile resolution | `control_plane.py:182-186` | Server-side, from `ConsultRequest.profile` |
| Objective rendering | `context_assembly.py:238` | Direct into JSON, NOT trimmable |
| Path existence check | `context_assembly.py:376-379` | Raises `ContextAssemblyError` |
| Soft/hard caps | `context_assembly.py:12-18` | 24KB/48KB advisory |
| Trim order | `context_assembly.py:20-29` | explicit_references first (trimmed last) |

## Context

### Mental Model

This was a **plan-and-review session** — no code was written, only an instruction
document was planned. The mental model: the skill is a review-orchestration protocol
encoded as prose that Claude follows at invocation time. The hardest part isn't the
consult dispatch (thin and well-tested) — it's making the Markdown instructions precise
enough that Claude reliably (1) selects the right diff scope, (2) doesn't leak secrets,
(3) respects the 20KB objective budget, (4) filters `explicit_paths` correctly, and
(5) always uses `workflow="review"`.

The scrutiny rounds proved the value of this framing: every major revision finding was
about operational precision at procedure boundaries, not about the architecture.

### Project State

| Ticket | Status | Tests | Key commit |
|--------|--------|-------|------------|
| T-02 | Closed | 566 | `d4b4a988` |
| T-03 | Closed | 566 | `d4b4a988` |
| T-04 | Closed | 566 | demonstrated-not-scored |
| T-05 | Closed (retroactive) | 698 | `271f23aa` |
| T-06 | Closed | 845 | `85afab6b` |
| T-07 | **Open (7a merged, 7b plan approved, 7c-7e not started)** | 881 | `61eaa590` |

### Slice Sequence for T-07

| Slice | Work | Status |
|---|---|---|
| **7a** | Analytics + DelegationOutcomeRecord + ConsultWorkflow + plumbing | **MERGED — PR #116** |
| **7b** | `codex-review` skill consuming `workflow="review"` | **Plan approved, ready for implementation** |
| 7c | Migration docs + parity matrix | Not started |
| 7d | Context-injection removal | Not started |
| 7e | Cross-model removal + verification + live delegate smoke | Not started |

## Learnings

### Objective field is never trimmed by context assembly

**Mechanism:** The server's context assembly renders `ConsultRequest.objective`
directly into the packet JSON at `context_assembly.py:238`. The trimming loop
(`_trim_entries`, lines 200-227) only removes context entries from the `_TRIM_ORDER`
categories. `objective` is not a category — it's a fixed payload field.

**Evidence:** Read `_render_packet` (line 230-278) — objective goes directly into
`payload["objective"]`. Read `_trim_entries` (line 200-227) — loops over
`_TRIM_ORDER[profile]` categories only.

**Implication:** Any skill that packs large material into `objective` must budget for
size independently. The server provides no safety net for oversized objectives — it
either trims away everything else trying to fit, or crashes.

### `explicit_paths` crash on deleted files

**Mechanism:** `_read_file_excerpt` at `context_assembly.py:376-379` raises
`ContextAssemblyError` with message "file reference missing" if the resolved path
doesn't exist on disk. Every path in `explicit_paths` goes through this function
(line 330).

**Evidence:** Read `_build_explicit_entries` (lines 321-333) → calls
`_read_file_excerpt` for each path → existence check at line 376.

**Implication:** Any skill passing `explicit_paths` through `codex.consult` must
filter for extant files. Diffs that include deletions or renames must exclude the
old/deleted paths. This affects `codex-review` directly — the filtering rules are
now in the plan (§5a).

### Instruction documents need the same scrutiny rigor as code

**Mechanism:** A SKILL.md is executed by Claude at invocation time. Ambiguous or
contradictory instructions produce unpredictable behavior — similar to ambiguous code
producing bugs. The scrutiny rounds found 11 issues across 2 passes (7 major, 4
minor), all in the instruction-level specification, none in the architecture.

**Evidence:** Every major-revision finding (PR trigger mismatch, `explicit_paths`
crash, smoke deferral, staged/unstaged ambiguity, untracked explosion, underdefined
evidence, unrestricted Bash) was a procedure-boundary ambiguity — the kind that would
cause silent misbehavior at runtime without producing an error.

**Implication:** SKILL.md files for complex orchestration skills should go through
the same plan-review-scrutinize cycle as code implementations. The plan is the
specification; the SKILL.md is the "code."

## Next Steps

### 1. Implement the codex-review SKILL.md

**Dependencies:** Plan approved (this session).

**What to read first:**
- The plan at `docs/plans/2026-04-22-t07-codex-review-7b.md` (authority document)
- The `consult-codex` SKILL.md (dispatch pattern reference)
- The cross-model `codex-reviewer.md` (semantic reference for scope table and output
  format, NOT to be copied verbatim)

**What to do:**
1. Stay on `feature/t07-review-7b` (already created)
2. Create `packages/plugins/codex-collaboration/skills/codex-review/SKILL.md`
3. Write the skill following the plan's 9 sections
4. Verify existing tests still pass (881+)
5. Attempt manual smoke on a real diff

**Approach:** The plan is the specification — follow its 9 sections directly. The SKILL.md
should map 1:1 to the plan sections. The writing style should follow the
`consult-codex` pattern (imperative, step-by-step, decision-table format) adapted for
the review orchestration's greater complexity.

**Potential obstacles:**
- SKILL.md length — the plan has significant detail that needs to be encoded in the
  skill. The cross-model reviewer is 210 lines; the codex-review skill will likely be
  longer given the additional constraints (objective budget, explicit_paths filtering,
  scope grammar).
- Objective budget encoding — the skill needs to instruct Claude to estimate byte size
  before dispatch. This is awkward in prose but essential for correctness.

### 2. Manual smoke test

**Dependencies:** SKILL.md written (step 1).

**What to do:** Follow the smoke procedure in plan §9:
1. Record before line count of `analytics/outcomes.jsonl`
2. Invoke `/codex-review` on the 7b branch against merge-base
3. Verify `workflow: "review"` and `profile: "code-review"` in the tool call
4. Verify synthesis follows §8 output contract
5. Verify analytics row with `"workflow": "review"` and `"outcome_type": "consult"`

**Blocker if App Server unavailable:** 7b stays open; PR ships for structural review
only.

### 3. PR and slice closure

**Dependencies:** Smoke test passed (step 2).

**What to do:** Create PR with:
- Smoke evidence (before/after analytics counts, new row, review output summary)
- 7a test coverage citation (7 tests listed in plan §9)
- PR description noting this is a single-file instruction document change

## In Progress

**Clean stopping point.** The plan file is written and approved. Branch
`feature/t07-review-7b` exists with the plan as the only change. No code changes in
flight. 881 tests passing on main.

## Open Questions

### 1. Abandoned cross-session delegation terminal outcomes (inherited)

**Context:** If a delegation job reaches terminal status in a session that crashes
before poll, and the next session has a different session ID, the terminal outcome may
be missing from `analytics/outcomes.jsonl`. The job store retains the data.

**Decision pending until:** Beyond T-07 scope.

### 2-4. Inherited from predecessor handoff chain

Open questions #2-4 from the predecessor handoff (non-store busy sources in active
delegation summary, `git diff --binary` output stability, `request_user_input` answer
construction) remain unchanged.

## Risks

### 1. SKILL.md complexity may reduce reliability

The plan encodes significant operational detail (objective budget, explicit_paths
filtering, scope resolution, secret scanning). Complex instructions have more failure
modes than simple ones. The cross-model reviewer agent is 210 lines; the
codex-collaboration replacement will likely be longer.

**Mitigation:** The plan already addresses this through explicit prohibitions, decision
tables, and deterministic scope resolution. The scrutiny rounds specifically targeted
instruction ambiguity.

### 2. App Server availability for smoke test

If the App Server is unavailable when the implementation session runs, the smoke
cannot execute and 7b remains open. The PR can ship for structural review but cannot
claim the AC.

**Mitigation:** The plan explicitly handles this as "7b remains open" rather than
silently deferring.

### 3. Package-wide ruff format pre-existing violations (inherited)

25 files need reformatting in codex-collaboration. Only PR-scoped files should be
formatted to keep diffs scoped.

## References

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| 7b implementation plan (approved) | `docs/plans/2026-04-22-t07-codex-review-7b.md` | Implementation specification |
| T-07 ticket (reconciled) | `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` | Scope and ACs |
| Consultation profiles | `packages/plugins/codex-collaboration/references/consultation-profiles.yaml` | Profile definitions |

### Semantic sources (read, not ported)

| Document | Location | Role |
|----------|----------|------|
| Cross-model reviewer agent | `packages/plugins/cross-model/agents/codex-reviewer.md` | Behavioral reference |
| Cross-model consultation-stats | `packages/plugins/cross-model/skills/consultation-stats/SKILL.md` | Analytics predecessor |
| Consult-codex skill | `packages/plugins/codex-collaboration/skills/consult-codex/SKILL.md` | Dispatch pattern |
| Analytics skill | `packages/plugins/codex-collaboration/skills/codex-analytics/SKILL.md` | Skill structure pattern |

### Prior handoffs (chain)

- Immediate predecessor: `docs/handoffs/archive/2026-04-22_01-32_t07-7a-reviewed-and-merged.md`
- T-07 arc: T-06 closure → T-07 scope reconciliation → 7a plan scrutiny → 7a
  implementation → 7a review + merge → **7b plan + review (this handoff)** → 7b
  implementation

## Gotchas

### 1. Pyright stale diagnostics after subagent writes (persistent, inherited)

Pyright reports methods as unknown even though they exist and tests pass. LSP server
doesn't get real-time file-change notifications from subprocess edits. Verify with
test execution, not Pyright diagnostics.

### 2. Package-wide ruff format has pre-existing violations (inherited)

`ruff format --check packages/plugins/codex-collaboration` reports 25 files needing
reformatting. Only PR-scoped files should be formatted.

### 3. `uv run --package` pytest path resolution (inherited)

Running `uv run --package codex-collaboration pytest tests/test_outcome_record.py`
from repo root fails. Only full paths work:
`packages/plugins/codex-collaboration/tests/test_outcome_record.py`.

### 4. `${CLAUDE_SKILL_DIR}` substitution (inherited)

When referencing bundled scripts from SKILL.md, use `${CLAUDE_SKILL_DIR}/path`. Do
not use relative paths or instruct Claude to resolve from the plugin root.

### 5. MCP `explicit_paths` crash on deleted files (NEW)

`context_assembly._read_file_excerpt` raises `ContextAssemblyError` if a path doesn't
exist (`context_assembly.py:376-379`). Any skill passing `explicit_paths` must filter
for extant files. Diffs with deletions or renames require filtering before dispatch.

### 6. Objective field is never trimmed (NEW)

The server's context assembly renders `objective` directly into the packet. It is not
a trimmable context entry. Large objectives can (a) cause all context entries to be
trimmed away, and (b) crash with `ContextAssemblyError` if exceeding 48KB.

## User Preferences

### Review rigor confirmed

The user performed 3 scrutiny rounds on the plan, escalating from "major revision" to
"minor revision" to "defensible." This mirrors the 7a review pattern: multi-layered
review with increasing specificity. The user values thorough operational specification
over quick shipping.

### Autonomous execution within directive

The user provided the 8-gap analysis, the 9-section outline, and the scrutiny verdicts.
Implementation of fixes was delegated without micromanagement. Pattern: user sets
constraints and acceptance criteria, then evaluates results. Matches predecessor
handoff's observation: "provide findings → direct implementation → review final result."

### Smoke test as hard gate

The user explicitly rejected the smoke deferral option: "if smoke cannot run, that
should block 7b closure. It can be a PR-known gap only if the PR is explicitly not
claiming the 7b AC." This is a stronger acceptance stance than 7a (which allowed
deferred verification for some metrics).
