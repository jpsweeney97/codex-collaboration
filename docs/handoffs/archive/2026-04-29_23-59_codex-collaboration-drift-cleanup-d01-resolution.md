---
date: 2026-04-29
time: "23:59"
created_at: "2026-04-30T03:59:34Z"
session_id: 1d33b9bd-a6a5-4067-aff4-9c94b87a5d48
resumed_from: /Users/jp/Projects/active/claude-code-tool-dev/docs/handoffs/archive/2026-04-29_18-12_codex-collaboration-status-verification-audit.md
project: claude-code-tool-dev
branch: main
commit: b86e5be2
title: codex-collaboration drift cleanup — D-01 fork resolution and drift report corrections
type: handoff
files:
  - docs/superpowers/specs/codex-collaboration/decisions.md
  - docs/superpowers/specs/codex-collaboration/foundations.md
  - docs/superpowers/specs/codex-collaboration/contracts.md
  - docs/superpowers/specs/codex-collaboration/delivery.md
  - docs/superpowers/specs/codex-collaboration/recovery-and-journal.md
  - docs/status/codex-collaboration-current-state.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md
  - docs/audits/2026-04-29-codex-collaboration-status-verification.md
---

# Handoff: codex-collaboration drift cleanup — D-01 fork resolution and drift report corrections

## Goal

Execute the cleanup work identified by the status verification audit (`docs/audits/2026-04-29-codex-collaboration-status-verification.md`), starting with the audit's required drift report corrections and then the prioritized drift findings.

**Trigger:** The previous session produced a verification audit of three `codex-collaboration` status documents and outlined a six-step cleanup sequence. This session is the execution of that sequence, starting from step 1.

**Stakes:** The audit is being used as the basis for cleanup work that aligns code, specs, and operator-facing docs. If the cleanup introduces new drift while fixing old drift, the audit's value is undermined.

**Success criteria:**
- Drift report's required corrections applied (D-04 annotation, skill enumeration, Section 8 split)
- D-01 (fork drift) resolved with a behavior-decision, not just a doc cleanup
- All spec owner docs internally consistent on the resolved finding
- Drift report summary surfaces updated to reflect resolved status

**Connection to project arc:** This continues the status-topology work from the drift-synthesis-recovery decision (`docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md`). That decision established the three-document topology (current-state synthesis, reconciliation register, drift report). This session verifies and repairs the documents operating under that topology.

## Session Narrative

Loaded the handoff from the previous verification audit session. The handoff outlined six next steps in priority order: (1) apply required corrections to drift report, (2) land D-01 fork drift, (3) decide D-02, (4) decide D-03, (5) land D-07, (6) batch remaining findings.

Started with step 1 — the three required corrections to the drift report. These were mechanical: add a D-04 addressed-status annotation (the register row was added in the same commit that saved the drift report), split Section 8 step 4 into addressed and still-actionable halves, and correct the skill enumeration from 5+1 to 7+1. Verified the skill directories and their `user-invocable` frontmatter before making the change. Created branch `docs/drift-report-required-corrections`, committed at `e1c90770`, fast-forward merged to main. Clean and quick.

Moved to step 2 — D-01 (fork drift). The audit had classified this as "docs-only" because code intentionally excludes fork and `decisions.md` records a deferral. User pushed back: "I want to discuss D-01 as a behavior-decision. We were too hasty to classify D-01 as a docs-only item."

This was the key pivot of the session. The user's instinct was right. The spec describes dialogue as architecturally "branchable" — not just mentioning a tool name, but embedding branching into the scope/goals (`foundations.md:17, 23`), the dialogue flow (`foundations.md:169`), the handle schema via `parent_collaboration_id` / `fork_reason` (`contracts.md:40`), and the contracts tool surface (`contracts.md:18`). Meanwhile `decisions.md:142` says fork is "deferred, additive, and not blocked." Editing the docs to remove fork references would implicitly decide that dialogue is linear-only — smuggling a cancellation decision into a docs cleanup.

The discussion explored three options: (1) linear-only — remove branchability entirely, (2) copy-and-diverge — preserve branchable architecture but implement as independent seeded dialogues, (3) true branching — full tree semantics. User asked "What would dialogue being branchable actually look like in real-world use?" which drove a concrete analysis of the value proposition at different dialogue depths.

User then pushed to explore copy-and-diverge in depth. Key discovery: `TurnStore` only stores `context_size` metadata, not turn content, and `dialogue.read` reconstructs turns from App Server `thread/read`. So the actual seed mechanism needs to account for Codex thread state, not just local lineage. This gave two realistic variants: fork-head-and-linearize (use existing `runtime.fork_thread()`) and synthetic seed packet (replay/summarize for prefix selection).

User proposed the decision wording with two additions I hadn't considered: (1) admissibility criteria for `seed_from` — reject if source handle has integrity issues rather than creating partial provenance, and (2) fresh control resolution — seeded dialogues resolve their own profile/posture/turn budget, no implicit inheritance.

I verified the additions against code: `control_plane.py:181-186` already separates profile resolution from thread creation, so the implementation naturally honors the inheritance boundary. I also checked for gaps: `fork_thread` is live but only for consultations (not dialogue), `parent_collaboration_id`/`fork_reason` exist in `CollaborationHandle` (`models.py:278-279`) but nobody writes them, the journal has a provenance gap for seeded dialogues that interacts with D-07.

Committed the decision and spec edits across 7 files at `7429e470`. Then the critique rounds began.

First critique (verdict: Major revision) found that `contracts.md` tool table described `seed_from` as currently accepted (same drift class as D-01 itself), and `recovery-and-journal.md` was skipped despite `spec.yaml:89` requiring cross-review with `contracts`. Applied four fixes at `8a316262`.

Second critique (verdict: Minor revision) found that `recovery-and-journal.md:138` crash recovery path still said "fork from the interrupted snapshot" in current tense, and the drift report annotation pointed at the wrong commit set. Applied two fixes at `c55aeff9` + `65f63ef9` (annotation backfill).

Third critique (verdict: Minor revision) found that the D-01 subsection had a correct addressed-status annotation, but the drift report's summary surfaces (executive verdict, findings table, Section 7, repair order) still presented D-01 as active unresolved drift — the same stale-summary pattern previously fixed for D-04. Applied five summary surface updates at `b86e5be2`.

## Decisions

### Decision: Reclassify D-01 from docs-only to behavior-decision

**Choice:** Treat D-01 (fork drift) as a behavior-decision requiring an architectural choice, not a docs-only cleanup.

**Driver:** User said: "I want to discuss D-01 as a behavior-decision. We were too hasty to classify D-01 as a docs-only item." The repo evidence supported this — branchability appears in foundations scope/goals, dialogue flow, handle schema, and contracts tool surface. `decisions.md:142` says "deferred, additive, and not blocked," not "cancelled."

**Rejected alternative:** Treat as docs-only — edit spec text to remove fork references, aligning docs with code. Rejected because it would smuggle a cancellation decision into a docs cleanup. The deferral in `decisions.md` says fork is deferred, not cancelled — different claims with different spec edit implications.

**Implication:** The cleanup cost for D-01 increased from one spec edit pass to a multi-file decision record plus three critique rounds, but the result is an architecturally sound decision rather than an implicit cancellation.

**Trade-offs accepted:** More work now, but the decision is explicit and reversible rather than implicit and hard to undo.

**Confidence:** High (E2) — verified against multiple spec files that branchability is an architectural property, not just a stale tool name.

**Reversibility:** High — the decision record exists at `decisions.md §Dialogue Fork Scope` and can be revisited if the architectural direction changes.

**Change trigger:** If the team decides dialogue should be strictly linear-only, the decision can be updated and the reserved handle fields (`parent_collaboration_id`, `fork_reason`) removed.

### Decision: Dialogue remains architecturally branchable via copy-and-diverge

**Choice:** Preserve branchability as an architectural property. The implementation target is copy-and-diverge via current-head forking (`seed_from` on `codex.dialogue.start`), not a standalone `codex.dialogue.fork` tool or true tree-structured dialogue.

**Driver:** User's three-way framing: "1. Linear-only: remove branchability. 2. Copy-and-diverge: preserve branchable architecture, implement as independent seeded dialogues. 3. True branching: preserve tree semantics." Combined with analysis that copy-and-diverge captures the primary use case (explore alternatives from a decision point) without tree state complexity.

**Rejected alternatives:**
- **Linear-only:** Rejected because it would remove an architectural property woven into foundations, contracts, and the handle schema. User: "So 'remove fork from the docs' would indeed smuggle in a cancellation decision."
- **True branching:** Rejected as heavier than needed. Requires tree-structured lineage store, tree-read in `dialogue.read`, tree-aware crash recovery, and tree-aware prompt building — all for a feature whose value depends on dialogue depth that may not materialize.
- **`codex.dialogue.fork` as a standalone tool:** Replaced by `seed_from` parameter on `dialogue.start`. More natural API shape — "start a new dialogue seeded from an existing one" vs "fork this dialogue into a tree."

**Implication:** `CollaborationHandle.parent_collaboration_id` and `fork_reason` remain as reserved nullable fields. The planned surface is `seed_from` on `codex.dialogue.start` with current-head semantics only. Arbitrary prefix seeding (`up_to_turn`) is separately deferred.

**Trade-offs accepted:** Copy-and-diverge doesn't support reconvergence, structural "show all branches from X" queries, or prefix selection. These are explicitly deferred as separate design questions with different implementation surfaces.

**Confidence:** High (E2) — verified `fork_thread` exists in `runtime.py:145` (consultation path), `CollaborationHandle` has the reserved fields at `models.py:278-279`, and the lineage store requires no new operations under copy-and-diverge.

**Reversibility:** High — the decision record specifies the architectural direction; if true branching is needed later, copy-and-diverge is forward-compatible (it becomes one way to create a branch).

**Change trigger:** Implementation enters scope when a concrete seeded-dialogue use case justifies the work. Prefix seeding requires separate design if the use case demands it.

### Decision: Record D-01 decision in spec-local `decisions.md`, not monorepo-wide `docs/decisions/`

**Choice:** Replace the existing "Dialogue Fork Scope" section in `docs/superpowers/specs/codex-collaboration/decisions.md` with the full decision record.

**Driver:** User identified the routing: "The current codex-collaboration routing already points readers to the spec-local decisions file, not the monorepo-wide `docs/decisions/` directory." Cited `current-state.md:16` routing behavioral truth to the spec, `current-state.md:44` mapping `decisions` authority to the spec-local file, and `README.md:41` including `decisions.md` in the spec reading order.

**Rejected alternative:** Create a standalone `docs/decisions/` record. Rejected because it would be orphaned for codex-collaboration readers whose discovery path goes through the spec.

**Implication:** Future codex-collaboration decisions should be recorded in the spec-local `decisions.md`, with `docs/decisions/` used only for cross-project decisions or with explicit cross-links.

**Trade-offs accepted:** Monorepo-wide decision search misses this record unless someone reads the spec. Acceptable because the decision is codex-collaboration-specific.

**Confidence:** High (E1) — directly driven by user's routing analysis.

**Reversibility:** High — could move to `docs/decisions/` with a cross-link if needed.

**Change trigger:** If a monorepo-wide decision index is created that needs to include codex-collaboration decisions.

### Decision: Use Constraints subsection for implementation-level detail

**Choice:** The `decisions.md` section contains the architectural direction in the main body and a `#### Constraints` subsection for admissibility, fresh control resolution, dialogue-thread verification, and D-07 ordering dependency.

**Driver:** The full decision has 7 specific points. Fitting all into the existing `decisions.md` format (which is concise per-section) would make D-01 3-4x the size of its neighbors. The Constraints subsection keeps the architectural direction readable at the top while preserving implementation constraints in the same file.

**Rejected alternative:** Split into separate design note. Rejected because the constraints are decision-level (they constrain any implementation), not implementation-level (they don't prescribe how).

**Implication:** The Constraints subsection is part of the decision record and governs implementation.

**Trade-offs accepted:** Slightly longer section in `decisions.md`.

**Confidence:** High (E1) — fits the file's structure while accommodating more detail.

**Reversibility:** High — could restructure within the same file.

**Change trigger:** None — this is a formatting choice.

## Changes

### `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md` — Required corrections + D-01 annotation + summary surfaces

**Purpose:** Apply the verification audit's three required corrections, add D-01 addressed-status annotation, and update summary surfaces for D-01 resolution.

**Approach:** Five separate commits touching this file: (1) D-04 annotation + skill enumeration + Section 8 split at `e1c90770`, (2) D-01 addressed-status annotation at `7429e470`, (3) traceability fix at `65f63ef9`, (4) commit hash backfill at `c55aeff9`→`65f63ef9`, (5) summary surface updates (executive verdict, findings table, Section 7, repair order) at `b86e5be2`.

**Key details:**
- D-04 addressed-status note explains the snapshot-true / stale-as-saved pattern with the specific commit (`a5fd568d`) where the register row was added
- D-01 addressed-status note cites three commits: `7429e470` (decision + spec edits), `8a316262` (tense corrections), `c55aeff9` (recovery crash-path fix)
- Findings table D-01 row now shows `addressed` status with `resolved` category
- Executive verdict second bullet changed from "No" to "Partially" (D-01 resolved, D-02/D-03 remain)
- Repair order step 1 struck for fork, remaining contradictions explicitly named

### `docs/superpowers/specs/codex-collaboration/decisions.md` — Dialogue Fork Scope replacement

**Purpose:** Replace the original 9-line deferral with the full decision record including Constraints subsection.

**Approach:** The section now has: Resolved statement, Rationale (why copy-and-diverge not tree or linear), Planned surface (`seed_from` on `dialogue.start`), Forward compatibility, and a Constraints subsection with four implementation constraints.

**Key details:**
- Rationale explicitly says "removing [branchability] would smuggle a cancellation decision into a docs cleanup"
- Planned surface specifies current-head semantics only; prefix seeding deferred as separate design question
- Constraints: admissibility criteria, fresh control resolution, dialogue-thread verification, D-07 ordering dependency

### `docs/superpowers/specs/codex-collaboration/foundations.md` — Dialogue flow update

**Purpose:** Preserve "branchable" in scope/goals while replacing the live fork/tree-read flow with deferred copy-and-diverge.

**Approach:** Removed steps 4-6 (fork, lineage recording, tree reconstruction). Added step 4 (linear read) and a paragraph describing branchability as a deferred architectural property with future-tense language ("will be seedable when the deferred copy-and-diverge surface lands").

### `docs/superpowers/specs/codex-collaboration/contracts.md` — Tool table, lineage store, crash recovery, audit action

**Purpose:** Remove `codex.dialogue.fork` from current MCP tool surface, update lineage store deferral language, fix crash recovery sentence, and annotate `fork` audit action as reserved.

**Approach:** Four edits:
- Tool table: removed `codex.dialogue.fork` row, updated `dialogue.start` description to "Future copy-and-diverge support is planned via `seed_from`" (not "accepts `seed_from`" — that would claim current behavior)
- Lineage store operations: fork-specific ops not needed under copy-and-diverge; provenance via existing `parent_collaboration_id` field
- Crash recovery step 7: "Forking from the interrupted snapshot requires `codex.dialogue.fork`" → seeding requires `seed_from` to be in scope
- Audit event `fork` action: annotated as reserved, not currently emitted, will be produced by `seed_from` when implemented

### `docs/superpowers/specs/codex-collaboration/recovery-and-journal.md` — Fork write trigger + crash recovery path

**Purpose:** Align the recovery contract with `contracts.md` on fork's reserved status.

**Approach:** Two edits:
- Moved `fork` row from the current write trigger table to a **Reserved trigger** note below the table, with deferred-`seed_from` annotation and link to decisions.md
- Crash recovery step 6: "Allow Claude to continue from the last completed turn or fork from the interrupted snapshot" → seeding deferred until `seed_from` enters scope

**Key detail:** This file was missed in the initial edit set (`7429e470`). `spec.yaml:89` says changes to `contracts` authority should review `recovery-contract`. The miss was caught in the first critique round and fixed at `8a316262` (write trigger) and `c55aeff9` (crash recovery path).

### `docs/superpowers/specs/codex-collaboration/delivery.md` — R2 deferral + integration test plan

**Purpose:** Update R2 deferred language and integration test plan to reference `seed_from` instead of `codex.dialogue.fork`.

**Approach:** Two edits:
- R2 Deferred bullet: `codex.dialogue.fork` and tree reconstruction → dialogue branching via `seed_from` on `codex.dialogue.start` (copy-and-diverge, not tree-structured)
- Integration test plan: "Dialogue with fork and read" → "Dialogue with seeded start and read"

### `docs/status/codex-collaboration-current-state.md` — Deferred item update

**Purpose:** Update the deferred item to name copy-and-diverge / seeded start rather than only `codex.dialogue.fork`.

**Approach:** Single edit replacing the deferred item text with explicit statement that `codex.dialogue.fork` as a standalone tool is permanently replaced, linking to the decision.

### `docs/status/codex-collaboration-reconciliation-register.md` — DIALOGUE-FORK row update

**Purpose:** Update the `DIALOGUE-FORK` row to reflect the resolved direction.

**Approach:** Updated current truth and exit condition. Current truth now says the intended surface is `seed_from` on `codex.dialogue.start` (copy-and-diverge), not a standalone fork tool. Exit condition now lists the four implementation constraints.

## Codebase Knowledge

### Spec authority structure — how changes propagate

The codex-collaboration spec has 8 authority owners defined in `spec.yaml`. Changes to one owner may require cross-review of linked authorities:

| Authority | File | Cross-review dependencies |
|-----------|------|--------------------------|
| `foundation` | `foundations.md` | `contracts` (tool surface), `delivery` (build sequence) |
| `contracts` | `contracts.md` | `recovery-contract` (audit schema, crash recovery) |
| `decisions` | `decisions.md` | All owners (decisions affect all layers) |
| `delivery` | `delivery.md` | `contracts` (acceptance gates reference contract shapes) |
| `recovery-contract` | `recovery-and-journal.md` | `contracts` (audit schema shared) |
| `advisory-policy` | `advisory-runtime-policy.md` | `contracts` (advisory widening), `decisions` (policy decisions) |

The D-01 resolution required touching 5 of 8 authority owners. The miss on `recovery-and-journal.md` in the first commit was because the `spec.yaml:89` cross-review dependency was not followed.

### Fork-related surfaces in the codebase

| Surface | Location | Status | Notes |
|---------|----------|--------|-------|
| `fork_thread()` | `runtime.py:145` | Live, consultation only | Calls App Server `thread/fork`; used by `control_plane.py:189` |
| `parent_thread_id` on `ConsultRequest` | `models.py:107` | Live, not exposed via MCP | Triggers `fork_thread` in control plane but not wired in `mcp_server.py` |
| `parent_collaboration_id` on `CollaborationHandle` | `models.py:278` | Reserved nullable | In contract and code; never populated |
| `fork_reason` on `CollaborationHandle` | `models.py:279` | Reserved nullable | In contract and code; never populated |
| `test_no_fork_tool_in_r2` | `test_mcp_server.py:21-23` | Live | Enforces `codex.dialogue.fork` absence from MCP surface |
| `fork` audit action | `contracts.md:213`, `recovery-and-journal.md` | Reserved | Annotated as not currently emitted |
| `DIALOGUE-FORK` register row | `reconciliation-register.md:102` | Deferred | Updated with copy-and-diverge direction |
| `consultation_safety.py:38` | `DIALOGUE_START_POLICY` | Live | Does not include `seed_from` — correct because `seed_from` is deferred |

### TurnStore architecture — relevant for future `seed_from` implementation

`TurnStore` (`turn_store.py`) is a session-partitioned append-only JSONL store that records only `context_size` per `(collaboration_id, turn_sequence)`. It does NOT store turn content. `dialogue.read` reconstructs actual turn content from App Server `thread/read` and left-joins local metadata.

This means "copy turns from lineage" is insufficient for `seed_from` — the seed mechanism must account for Codex thread state via `thread/fork`, not just local turn metadata.

### Critique-round verification pattern

The session established a multi-round critique pattern for spec-level changes:

1. Apply edits → commit
2. User applies scrutinize-style critique (Major/Minor/Defensible verdict)
3. Address all named issues → commit
4. User re-critiques
5. Repeat until verdict is Defensible or Minor with no critical findings

The D-01 resolution went through 3 critique rounds: Major → Minor → Minor (summary surfaces). Key learning: the critique consistently caught the same drift class the fix was addressing — future-tense architecture leaking into current-tense contract language.

### Drift report summary surface pattern

When marking a finding as addressed in the drift report, five summary surfaces need updating:

1. **Executive Verdict** (Section 2) — overall consistency assessment
2. **Highest-risk drifts** (Section 2) — bullet naming the finding
3. **Findings table** (Section 6) — row with severity/status/action
4. **Section 7 stale docs list** — bullet listing the finding
5. **Repair order** (Section 8) — step referencing the finding

A subsection-level addressed-status annotation does NOT automatically neutralize these summary surfaces. This is the D-04 stale-summary pattern — previously caught for D-04, re-caught for D-01.

## Context

### Drift-synthesis-recovery status topology

The three current-facing `codex-collaboration` status documents operate under a topology defined in `docs/decisions/2026-04-29-codex-collaboration-drift-synthesis-recovery.md`:

- **Current-state synthesis** (`docs/status/codex-collaboration-current-state.md`): reader entry point, routes to spec for behavioral truth
- **Reconciliation register** (`docs/status/codex-collaboration-reconciliation-register.md`): bounded index of unresolved work across authority boundaries
- **Drift report** (`docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`): supporting evidence, not authoritative

Changes to spec owner docs should flow through to the status surfaces (current-state deferred items, register rows, drift report annotations) to maintain topology consistency.

### D-01 findings that informed the decision

| Evidence | Location | What it showed |
|----------|----------|----------------|
| "branchable" in scope | `foundations.md:17, 23` | Branchability is an architectural property, not a tool name |
| Handle schema | `contracts.md:40, models.py:278-279` | `parent_collaboration_id` / `fork_reason` are live reserved fields |
| Deferral wording | `decisions.md:142` | "deferred, additive, and not blocked" — not cancelled |
| `fork_thread()` | `runtime.py:145` | Working for consultations, not tested for dialogue |
| No fork tool | `mcp_server.py`, `test_mcp_server.py:21-23` | Deliberately absent with test enforcement |
| TurnStore limitation | `turn_store.py` | Only stores `context_size`, not turn content |
| `dialogue.read` reconstruction | `dialogue.py:915` | Turns come from App Server `thread/read`, not local storage |

### Mental model: doc-only vs behavior-decision

The audit's cleanup-sequencing insight distinguishes two categories of drift findings:

- **Doc-only:** code is intentional, docs are stale → single-source spec edit. Test: would I confidently edit the docs to match the code right now without confirmation?
- **Behavior-decision:** disagreement is unresolved → requires a decision before cleanup; if decision goes against code, becomes code + tests + docs work

D-01 looked like doc-only on the surface (code excludes fork, decision says deferred) but was actually a behavior-decision (the decision changes the intended future surface, not just the current docs). The cost difference was real: one spec edit pass vs a multi-file decision record with three critique rounds.

## Learnings

### The same drift class repeats across fix iterations

**Mechanism:** When fixing drift between current behavior and spec text, the replacement text can introduce the same drift class — describing a future/planned surface as if it's current. The D-01 fix described `seed_from` as currently accepted on `contracts.md` tool table, which is the exact same error as describing `codex.dialogue.fork` as a current tool.

**Evidence:** Three critique rounds all caught current-vs-deferred tense leaks: `contracts.md` tool table, `recovery-and-journal.md` write trigger, `foundations.md` dialogue flow, and `recovery-and-journal.md` crash recovery path.

**Implication:** After editing spec text to address drift, specifically check: does the replacement text describe only current behavior? Or does it leak future-planned behavior into current-tense contract language?

**Watch for:** Any spec edit that introduces a new identifier or parameter. Ask: does this parameter/tool exist in the MCP schema today? If not, use future tense.

### Addressed-status annotations don't neutralize summary surfaces

**Mechanism:** A drift report has multiple reader-facing entry points: executive verdict, findings table, section 7 stale docs list, and repair order. Adding an addressed-status note to the finding's subsection leaves the summary surfaces stale. A reader starting at the executive verdict will still treat the finding as active.

**Evidence:** D-04 taught this lesson first (previous session's learnings). D-01 re-taught it — three summary surfaces still presented D-01 as active unresolved drift after the subsection annotation was added.

**Implication:** When addressing a drift finding, update 5 surfaces: the subsection (annotation), executive verdict, findings table, section 7, and repair order. This is a checklist, not a judgment call.

**Watch for:** Future D-02, D-03, D-07 resolutions. Each will need the same five-surface update pattern.

### `spec.yaml` cross-review dependencies are real enforcement rules

**Mechanism:** `spec.yaml:89` says changes to `contracts` authority should review `recovery-contract`. The D-01 resolution edited `contracts.md` (audit action) without initially checking `recovery-and-journal.md` (write triggers). The write trigger table still listed `fork` as a current event after `contracts.md` marked it as reserved.

**Evidence:** First critique round caught the miss. `recovery-and-journal.md:110` still said `fork` was a current write trigger while `contracts.md:213` said it was reserved.

**Implication:** Before committing spec edits, check `spec.yaml` for cross-review dependencies. For each authority owner edited, read the linked authorities to verify consistency.

**Watch for:** D-02 and D-03 resolutions. Both affect `contracts.md` and will require `recovery-and-journal.md` cross-review.

### Behavior-decisions hiding in docs-only classifications

**Mechanism:** A drift finding that says "docs say X, code does Y" can look like a docs-only fix (edit docs to match code). But if the docs describe an architectural property (not just a tool name), removing the docs text is a de facto architecture decision, not a cleanup.

**Evidence:** D-01 described dialogue as "branchable" across scope/goals, flow, handle schema, and tool surface. The deferral said "not blocked — deferred for scope reasons, not design reasons." Editing docs to remove fork would have implicitly decided dialogue is linear-only.

**Implication:** For drift findings classified as "docs-only," verify: does the docs text describe a tool name (docs-only) or an architectural property (behavior-decision)?

**Watch for:** D-02 and D-03. The audit classifies D-03's fix type as "source doc edit or code follow-up," but the advisory-widening text describes active policy behavior — the same pattern as D-01 where the docs describe more than a tool name.

## Next Steps

### 1. Decide D-02 (unknown request handling) — behavior-decision

**Dependencies:** None — independent of D-01 resolution.

**What to read first:** T-20260429-02 ticket (`docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md`) — this may be where the decision happens. Then the audit's D-02 entry and: `decisions.md:122-124`, `contracts.md:354-360`, `delegation_controller.py:984-1069`, `recovery-and-journal.md:159-166`.

**Approach:** The core question: is terminalization (current code) the intended contract, or is escalation (`decisions.md` / `recovery-and-journal.md`) the intended contract? If terminalize is canonical → doc-only fix. If escalate is canonical → code + tests + docs work spanning `delegation_controller.py`, contracts spec, and operator-facing skill text.

**Acceptance criteria:** D-02 addressed-status annotation, decision record in `decisions.md`, spec edits across affected authority owners (check `spec.yaml` cross-review deps), five drift-report summary surfaces updated.

**Potential obstacles:** This may require stakeholder input on intended behavior. The D-01 resolution was internally resolvable (architecture vs implementation); D-02 may need an external judgment on what "correct" handling of unknown requests means.

### 2. Decide D-03 (advisory widening) — behavior-decision

**Dependencies:** None — independent of D-01 and D-02.

**What to read first:** Audit's D-03 entry; `advisory-runtime-policy.md:32-118`; `control_plane.py:154-158`; `profiles.py:148-158`. The register's `ADVISORY-WIDENING-ROTATION` row already characterizes it as deferred.

**Approach:** Same pattern as D-01 — the advisory-widening text describes active policy behavior but code rejects it. Is this deferred-future-scope (edit docs to mark as future, keep the spec text for when it lands) or cancelled (remove the spec text)?

**Acceptance criteria:** Same five-surface pattern as D-01.

**Potential obstacles:** D-03 spans `advisory-runtime-policy.md` extensively (lines 32-118). If the decision is "mark as future-scope," the edit scope is large — 86 lines of active-behavior prose that needs to be annotated or restructured.

### 3. Land D-07 (audit schema alignment) — most expensive

**Dependencies:** Should account for D-01's `fork` audit action reservation. Should also account for D-02 and D-03 if they've been decided (their resolutions may affect audit actions).

**What to read first:** Audit's D-07 entry. `contracts.md:188-223` (audit schema), `recovery-and-journal.md:104-120` (write triggers), `models.py:202-217` (AuditEvent dataclass), `delegation_controller.py` (emission sites), `skills/codex-analytics/SKILL.md` (consumer docs).

**Approach:** Reconcile audit-event field set across spec and dataclass. Reconcile action enumeration (13 in contracts vs 7 in analytics skill). Decide which is canonical and align all artifacts.

**Acceptance criteria:** AuditEvent dataclass, contract spec, recovery write triggers, and analytics skill all agree on field set and action enumeration.

**Potential obstacles:** D-07 is multi-artifact and touches code (`models.py`, `delegation_controller.py`). May require tests. Most expensive cleanup item by far.

### 4. Batch remaining findings (D-05, D-06, D-08, D-09)

**Dependencies:** D-05 (closed-in-root tickets) is independent. D-06 (delegate skill file_change visibility) is independent. D-08 (package README skill list) is independent. D-09 (diagnostic TTL prose) is independent.

**Approach:** These are lower-risk and can be batched. D-05 requires ticket moves or supersession notes. D-06 and D-08 are doc edits. D-09 is a supersession note or doc edit.

## In Progress

Clean stopping point — all session work completed. D-01 fully resolved across 6 commits and 9 files. No work in flight.

## Open Questions

### Should D-02 and D-03 be resolved before D-07?

D-07 (audit schema alignment) touches `contracts.md` audit actions and `recovery-and-journal.md` write triggers — the same surfaces that D-02 and D-03 may affect. If D-02 or D-03 change the intended behavior for unknown-request escalation or advisory widening, that could add or modify audit actions. Resolving D-02 and D-03 first gives D-07 a stable target.

The handoff's ordering already puts D-02 and D-03 before D-07. This question is about whether that ordering is a hard dependency or a preference.

### Is the five-surface update pattern worth codifying?

The pattern of updating 5 surfaces when addressing a drift finding (subsection annotation, executive verdict, findings table, Section 7, repair order) was learned by failure twice (D-04, D-01). Should this be captured in a checklist or process note? The drift report is a one-time artifact, so the pattern only applies while it's being used as cleanup basis.

## Risks

### Critique-round debt accumulation

Each D-01 critique round added a commit. The resolution is now 6 commits for a single finding. If D-02 and D-03 follow the same pattern, the commit history becomes noisy. **Mitigation:** Consider squashing or using a single branch for each finding's full resolution, only merging when the critique rounds converge.

### D-07 scope growth from D-01's audit action reservation

The `fork` audit action is now annotated as reserved in both `contracts.md` and `recovery-and-journal.md`. D-07 must reconcile this reservation with the rest of the audit schema. If D-07 is landed by someone who doesn't know about the reservation, they might remove it. **Mitigation:** The decision record at `decisions.md §Dialogue Fork Scope` Constraints subsection explicitly names the D-07 ordering dependency.

### Stale-summary pattern may recur for D-02 and D-03

D-01 resolution required updating 5 drift-report summary surfaces. D-02 and D-03 will need the same treatment. If the pattern is forgotten, the drift report's summaries will again present resolved findings as active. **Mitigation:** The learning is captured here and in MEMORY.md; the five-surface checklist should be applied for each finding resolution.

## References

- **Verification audit:** `docs/audits/2026-04-29-codex-collaboration-status-verification.md`
- **Drift report:** `docs/assessments/2026-04-29-codex-collaboration-verified-drift-report.md`
- **Decision record:** `docs/superpowers/specs/codex-collaboration/decisions.md §Dialogue Fork Scope`
- **Spec authority model:** `docs/superpowers/specs/codex-collaboration/spec.yaml`
- **Previous handoff:** `docs/handoffs/archive/2026-04-29_18-12_codex-collaboration-status-verification-audit.md`
- **Commit chain:** `e1c90770` (required corrections), `7429e470` (D-01 decision + spec edits), `8a316262` (tense corrections), `c55aeff9` (recovery crash-path), `65f63ef9` (annotation backfill), `b86e5be2` (summary surfaces)

## Gotchas

### `spec.yaml` cross-review dependencies are enforced by critique, not tooling

The `spec.yaml` file lists cross-review dependencies between authority owners, but there is no automated enforcement. The D-01 resolution missed `recovery-and-journal.md` despite `spec.yaml:89` requiring cross-review with `contracts`. The miss was caught by the user's critique, not by any hook or check.

**For future-Claude:** After editing any spec owner doc, read `spec.yaml` and check every linked authority. Don't rely on grep for the changed identifier — the linked authority may use different terminology for the same concept (e.g., `contracts.md` says "audit action"; `recovery-and-journal.md` says "write trigger").

### Current-tense replacement text is the highest-risk edit in drift fixes

When replacing stale spec text that describes a non-existent tool/feature, the replacement text tends to describe the planned replacement in current tense. This produces the same drift class the fix is addressing. The D-01 fix went through three rounds of tense corrections.

**For future-Claude:** After writing replacement text for a drift fix, apply the tense test: does this text describe only what exists today? If it names a parameter, tool, or behavior that isn't in the MCP schema or code, use future tense ("when implemented," "is planned," "will be produced").

### Addressed-status annotations need five-surface treatment

A drift report finding annotation at the subsection level does not propagate to summary surfaces. Five surfaces need updating: (1) executive verdict, (2) highest-risk drifts bullet, (3) findings table row, (4) Section 7 stale docs list, (5) repair order step. Missing any of these leaves a reader-facing summary that contradicts the subsection.

**For future-Claude:** When adding an addressed-status annotation to a drift finding, update all five summary surfaces in the same commit. This is a checklist, not a judgment call.

## Conversation Highlights

**On reclassifying D-01:**
User: "I want to discuss D-01 as a behavior-decision. We were too hasty to classify D-01 as a docs-only item."
— Triggered the reclassification that shaped the entire session.

**On the three-way decision surface:**
User: "Your three-way framing is the right decision surface: 1. Linear-only, 2. Copy-and-diverge, 3. True branching."
— Validated the decision structure before implementation.

**On TurnStore limitations:**
User: "The shape I'd pressure-test is the proposed implementation detail. 'Copy turns from source partition into new partition' is probably not enough in the current implementation."
— Caught a naive implementation assumption by grounding in actual code. TurnStore only stores context_size; `dialogue.read` reconstructs from `thread/read`.

**On admissibility:**
User: "Define admissibility for `seed_from`. Current-head fork should probably be allowed only when the source dialogue is readable and active/known-good."
— Added a constraint I hadn't considered, grounded in the existing recovery model's treatment of missing turn metadata.

**On inheritance semantics:**
User: "Decide inheritance semantics. A seeded dialogue needs clear behavior for posture/profile/turn budget. My default would be: `seed_from` copies context lineage only, not execution controls."
— Prevented a subtle future bug where inherited profiles could surprise operators.

**On recording location:**
User: "I recommend: record the D-01 decision in decisions.md, probably replacing or extending the existing Dialogue Fork Scope section. Do not create a standalone docs/decisions/ record."
— Established that codex-collaboration decisions route through the spec-local file, not the monorepo-wide directory.

**On critique methodology:**
User applied three rounds of scrutinize-style critiques via `/copy` paste-back, with verdicts: Major revision → Minor revision → Minor revision. Each round named specific line numbers, severity levels, and required changes. The critique consistently caught the same drift class the fix was addressing.

## User Preferences

**Reject-first, evidence-first stance:** User applies structured critiques with severity labels (P1, P2), confidence scores, and specific file:line citations. The critique format follows the scrutinize skill's structure even when applied manually.

**Behavior-decision over docs-only when architecture is at stake:** User: "We were too hasty to classify D-01 as a docs-only item." — Prefers explicit architectural decisions over implicit decisions hidden in doc edits.

**Decision wording precision:** User crafted the final decision wording themselves, adding admissibility and inheritance constraints. Prefers decisions precise enough that "a future implementer won't re-open the decision."

**Spec-local authority routing:** User routes codex-collaboration decisions through the spec-local `decisions.md`, not the monorepo-wide `docs/decisions/`. Cited specific routing evidence from status docs.

**Direct action after alignment:** User said "Yes. I'd record it now" and "proceed with the full edit set" after alignment was reached — no hedging or re-confirmation needed.

**Critique-driven iteration:** Same pattern as previous session — produce → critique → tighten → re-critique. Verdict labels set response scope: Major = restructure, Minor = targeted fixes, Defensible = ship.

**Probe before acting:** User: "Probe this plan for gaps — where is it weak?" — Wants gap analysis before execution, especially for spec-level changes.

## Rejected Approaches

### Treating D-01 as a docs-only fix

**Approach:** Edit `foundations.md`, `contracts.md`, and `delivery.md` to remove fork references, aligning spec text with code's deliberate exclusion of fork.

**Why it seemed promising:** Code intentionally excludes fork. `decisions.md` records a deferral. Tests enforce fork's absence. The surface evidence says "docs are stale, code is right, update the docs."

**Specific failure:** The docs describe dialogue as architecturally "branchable" — not just mentioning a tool name. `foundations.md:17, 23` embed branching into scope/goals. `contracts.md:40` includes `parent_collaboration_id` / `fork_reason` in the handle schema. `decisions.md:142` says "deferred, additive, and not blocked." Removing these references would implicitly decide dialogue is linear-only, which is an architecture change, not a cleanup.

**What it taught:** The test for docs-only vs behavior-decision: does the docs text describe a tool name (docs-only) or an architectural property (behavior-decision)?

### Including `seed_from` in the contracts.md tool table as current behavior

**Approach:** Describe `codex.dialogue.start` as "accepts optional `seed_from` for copy-and-diverge."

**Why it seemed promising:** The decision establishes `seed_from` as the planned surface. Including it in the tool table makes the spec forward-looking and complete.

**Specific failure:** The MCP schema in `mcp_server.py:53` has no `seed_from` property. Describing it as currently accepted creates the same drift class D-01 was meant to eliminate — spec says a parameter exists that code doesn't implement.

**What it taught:** Replacement text in drift fixes must describe only current behavior. Future-planned behavior goes in future tense with "planned" or "when implemented" qualifiers.

### Creating a `mode` enum for `seed_from` supporting both current-head and prefix seeding

**Approach:** Ship `seed_from` with a `mode` parameter: `"thread_head"` for current-head fork, `"prefix"` for arbitrary `up_to_turn` seeding.

**Why it seemed promising:** A single parameter supporting both modes provides a clean, extensible API.

**Specific failure:** Current-head fork is a thin wrapper around `thread/fork`. Prefix seeding requires either replaying Codex turn content across threads (App Server may not support arbitrary turn injection) or constructing synthetic seed context (generation task with quality risks). These aren't modes of the same feature — they're different features sharing a parameter. Shipping under one enum couples their design decisions.

**What it taught:** Ship `seed_from: {collaboration_id}` with implicit current-head semantics. If prefix seeding later proves valuable, it should come through a separately designed schema.
