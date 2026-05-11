---
date: 2026-04-23
time: "00:15"
created_at: "2026-04-23T04:15:00Z"
session_id: 02770601-b011-46a0-97f6-d03ba7745c33
resumed_from: "docs/handoffs/archive/2026-04-22_22-04_t07-7e-cross-model-removed-t07-closed.md"
project: claude-code-tool-dev
branch: chore/delegate-remediation-ticket
commit: 82121adf
title: "T-07 merged, delegate remediation ticket opened"
type: handoff
files:
  - .claude/CLAUDE.md
  - .claude/skills/making-recommendations/references/codex-delta.md
  - docs/plans/2026-04-23-t07-cross-model-removal-7e.md
  - docs/references/README.md
  - docs/references/consultation-contract.md (deleted)
  - docs/references/consultation-profiles.yaml (repointed)
  - docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md
  - docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md (new)
  - packages/plugins/codex-collaboration/agents/context-gatherer-code.md
  - packages/plugins/codex-collaboration/agents/context-gatherer-falsifier.md
  - packages/plugins/codex-collaboration/references/consultation-profiles.yaml
  - packages/plugins/codex-collaboration/references/tag-grammar.md
  - packages/plugins/codex-collaboration/server/profiles.py
---

# T-07 Merged, Delegate Remediation Ticket Opened

## Goal

Two objectives this session: (1) land PR #123 (T-07 slice 7e — cross-model
package removal and marketplace cutover), and (2) write a remediation ticket
for the delegate execution defects discovered during the 7e live smoke.

**Trigger:** Predecessor handoff left PR #123 open with all verification
passed. The delegate defects were recorded as an execution-domain deferral
in T-07 but needed a formal ticket before remediation work could begin.

**Stakes:** PR #123 was the final cutover slice in the T-02 through T-07
arc that built codex-collaboration as the successor to cross-model. The
delegate defects are the gap between "cutover complete" and "live delegate
actually works end-to-end."

**Success criteria:** PR #123 merged to main, delegate remediation ticket
written and reviewed, both defensible.

**Connection to project arc:** Fifteenth session in the codex-collaboration
build sequence. This session closes the T-02–T-07 arc (PR #123 merge) and
opens the post-T-07 remediation arc (T-20260423-01).

## Session Narrative

**Phase 0 — Handoff load (~2 min).** Loaded predecessor handoff from the 7e
session. Clean state: PR #123 open at `2255b066`, all verification passed,
T-07 ticket closed in the commit.

**Phase 1 — User's PR review feedback (~10 min).** User provided two P3
findings from their own review of PR #123:
1. `PR #TBD` placeholder in ticket closeout at line 263 — straightforward
   fix to `PR #123`.
2. codex-collaboration missing from CLAUDE.md package table — the
   marketplace successor wasn't listed in the repo-local package inventory.

Additionally, one reviewer comment from Codex on GitHub: broken symlinks for
`consultation-contract.md` and `consultation-profiles.yaml` in
`docs/references/`. Investigated: `consultation-contract.md` was a symlink
to the deleted cross-model package with no codex-collaboration equivalent
(contract was Claude-cognitive, superseded by server-enforced contracts).
`consultation-profiles.yaml` had a copy in codex-collaboration. Fix:
deleted contract symlink, repointed profiles symlink, updated README index.

All three fixes committed at `efe2d70c`, pushed, tests verified (47 root +
881 codex-collaboration).

**Phase 2 — Parallel 4-agent PR review (~6 min active, agents ran
in background).** Launched four review agents in parallel: code-reviewer,
comment-analyzer, silent-failure-hunter, code-simplifier. Results:

- **Code reviewer** (93s, 16 tool uses): Clean pass, no issues.
- **Code simplifier** (133s, 21 tool uses): 7 findings, all low/cosmetic.
  Only F1 (README description style) had a concrete improvement.
- **Silent failure hunter** (203s, 56 tool uses): 6 findings (2 medium,
  4 low). Key: stale MCP tool name in codex-review skill (F1), 44 stale
  `.planning/` references (F3).
- **Comment analyzer** (386s, 93 tool uses): 2 labeled "critical" + 4
  improvements. Key: plan text contradicts implementation (Group 7 says
  consultation-contract.md "exists" but fix-up commit deleted it), stale
  `consultation-contract.md §14/§15/§7` references in live plugin docs.

After deduplication: 15 unique findings across agents, triaged to 4
categories.

**Phase 3 — User triage of review findings (~5 min).** User triaged all
findings with accept/reject/defer verdicts:

- **Accept (I1 + I2 + S5 + S1):** Plan text correction, consultation-
  profiles.yaml dangling reference, gatherer agent §15 citations, README
  description style. User expanded S5 to include `tag-grammar.md:57`
  citing §7. User also suggested changing "contract defaults" to
  "built-in defaults" in `profiles.yaml` and `profiles.py`.
- **Reject (I3/S3, S6):** codex-review legacy guard and lowercase heading
  — intentional and cosmetic respectively.
- **Defer (I4):** `.planning/` stale references — allowlisted in 7e plan,
  not a PR blocker.

All accepted items implemented in one commit at `23c0b6f9`. Key changes:
consolidated gatherer governance rules (removed inapplicable Codex-calling-
agent rule stubs), replaced §14/§15/§7 citations with inlined wording,
updated "contract defaults" to "built-in defaults." Pushed. User verified
PR #123 at final head `23c0b6f9`.

**Phase 4 — PR merge (~2 min).** User confirmed merge-readiness. Merged
PR #123 via `gh pr merge --merge --delete-branch`. Merge commit `89e2b802`.
Pulled to main, deleted local T-07 branches (7d and 7e).

**Phase 5 — Delegate remediation ticket (~25 min).** User proposed the
next work packet: delegate execution remediation. Recommended diagnostic-
first structure with two phases (sandbox investigation, approval API
investigation) before implementation.

Read source code to ground the ticket:
- `runtime.py:23-38` — `build_workspace_write_sandbox_policy`, confirmed
  `includePlatformDefaults: False`
- `delegation_controller.py:642-720` — `_server_request_handler`, confirmed
  `{"decision": "cancel"}` for `_CANCEL_CAPABLE_KINDS`
- `delegation_controller.py:1743-1754` — `decide(approve)` path, confirmed
  cancel-then-new-turn pattern via `build_execution_resume_turn_text`
- `execution_prompt_builder.py:41-77` — resume prompt, confirmed
  natural-language-only grant
- `delegation_controller.py:246` — `approval_policy` defaults to
  `"untrusted"`
- Vendored schemas at `tests/fixtures/codex-app-server/0.117.0/` —
  discovered valid response shapes

Wrote ticket, went through 3 scrutiny rounds with user:

**Round 1 (P2 + P3):** User found (1) ticket used `{"decision": "approve"}`
but vendored schemas show `accept`/`acceptForSession`/etc., and (2) sandbox-
only interaction claim was unqualified — `approval_policy="untrusted"` is
a separate mechanism from sandbox readability. Fixed by adding static
contract evidence section citing vendored schemas and qualifying the
interaction claim as a hypothesis to verify.

**Round 2 (P2 + P3):** User found (1) stale "no grant path" escape hatch
in acceptance criteria and implementation plan — the vendored schema proves
a grant path exists, so the unknown is live behavior not existence, and
(2) live grant verification only mentioned `command_approval` but not
`file_change`. Fixed both: AC now says "grants using `accept`" with
mismatch as integration failure, diagnostic gate covers both kinds.

**Round 3 (clean).** User approved: "defensible as the execution-boundary
ticket."

Committed at `82121adf`, PR #124 created.

## Decisions

### D1: Three-commit structure for PR #123 review fixes

**Choice:** Address review findings in two additional commits on the PR
branch rather than squashing into the original commit.

**Driver:** Each commit has a distinct scope: `efe2d70c` (symlinks,
placeholder, package table from initial review), `23c0b6f9` (stale
consultation-contract references from 4-agent review). Squashing would
obscure the review-driven provenance.

**Alternatives considered:**
- **Squash all into original commit** — rejected because amendments
  risk overwriting the original `2255b066` commit that passed the 6-round
  scrutiny in the predecessor session.
- **Interactive rebase** — rejected per CLAUDE.md instruction: "always
  create NEW commits rather than amending."

**Trade-offs accepted:** Three commits instead of one for a removal PR.
PR history is slightly noisier but each commit has clear provenance.

**Confidence:** High (E2) — follows repo conventions and CLAUDE.md
instructions.

**Reversibility:** N/A — commits are merged.

**Change trigger:** N/A.

### D2: Delete consultation-contract symlink, don't replace

**Choice:** Remove the `docs/references/consultation-contract.md` symlink
entirely rather than pointing it to a codex-collaboration equivalent.

**Driver:** The consultation contract was a Claude-cognitive document
specific to cross-model. codex-collaboration uses server-enforced contracts
instead. No equivalent document exists or should exist.

**Alternatives considered:**
- **Create a codex-collaboration consultation contract** — rejected because
  the consultation contract pattern (Claude-cognitive document governing
  consultation behavior) is superseded by server-enforced contracts in
  codex-collaboration.
- **Leave broken symlink** — rejected because the Codex reviewer (GitHub)
  flagged it as broken, and broken symlinks cause read failures.

**Trade-offs accepted:** `consultation-profiles.yaml` still has a
comment referencing `consultation-contract.md §14` (fixed in `23c0b6f9`),
and gatherer agents had `§15`/`§7` citations (also fixed). The contract's
rules were inlined locally rather than creating a replacement document.

**Confidence:** High (E2) — verified no codex-collaboration equivalent
exists in `references/` directory, confirmed contract is cross-model-
specific by reading its content (16-section Claude-cognitive document).

**Reversibility:** High — git history preserves the symlink and contract.

**Change trigger:** If codex-collaboration develops a Claude-cognitive
contract, a new document would be created from scratch (not restored from
cross-model).

### D3: Diagnostic-first ticket structure for delegate remediation

**Choice:** Structure T-20260423-01 with diagnostic gates before
implementation, separating what we know (vendored schemas) from what we
need to verify (live runtime behavior).

**Driver:** User's guidance: "I'd make the first implementation gate
explicitly diagnostic, not 'fix sandbox'" and "frame it as an API-contract
discovery problem before choosing the implementation path."

**Alternatives considered:**
- **Direct fix ticket** — rejected because the sandbox policy was set to
  `False` deliberately (T-05 hardening intent). Changing it without
  investigating what `True` grants risks opening the security boundary.
- **Investigation-only ticket** — rejected because the acceptance criteria
  need to include artifact production (the product gap), not just
  diagnostic findings.

**Trade-offs accepted:** Two-phase diagnostic adds an investigation step
before implementation. The ticket may take longer to close than a direct
fix, but the diagnostic evidence ensures the fix doesn't trade one defect
for a security regression.

**Confidence:** High (E2) — user performed the root-cause analysis
independently and defined the diagnostic structure.

**Reversibility:** High — ticket is documentation, not code.

**Change trigger:** N/A.

### D4: Inline governance rules rather than create replacement contract

**Choice:** Replace `consultation contract §15` citations in gatherer
agents with inlined local rules, rather than creating a new authority
document.

**Driver:** The three applicable rules (prompt/log retention, redaction
fail-closed, egress sanitization) are simple enough to inline. The
inapplicable rule stubs ("Rules 3-5 apply to Codex-calling agents only")
were noise in read-only agents that have no outbound dispatch.

**Alternatives considered:**
- **Create a codex-collaboration governance reference** — rejected because
  the rules are simple, the agents are the only consumers, and a reference
  document would be a single-consumer indirection.
- **Keep §15 citations as historical** — rejected by user's triage:
  "these live plugin docs should stop citing [the deleted contract]."

**Trade-offs accepted:** Rules are now duplicated across two agent files
rather than centralized. Accepted because both agents need the same three
rules and cross-file consistency is easy to verify.

**Confidence:** High (E2) — rules verified against the original contract
§15 content before inlining.

**Reversibility:** High — if a governance reference is created later, the
agents can cite it instead of inlining.

**Change trigger:** If more consumers need these rules, centralize into a
governance reference document.

## Changes

### `docs/references/consultation-contract.md` — Deleted (symlink)

Broken symlink pointing to `../../packages/plugins/cross-model/references/
consultation-contract.md` (deleted with cross-model package). No
codex-collaboration equivalent — contract was Claude-cognitive, superseded
by server-enforced contracts.

### `docs/references/consultation-profiles.yaml` — Repointed symlink

Changed from `../../packages/plugins/cross-model/references/` to
`../../packages/plugins/codex-collaboration/references/`. Target verified
to exist (4190 bytes).

### `docs/references/README.md` — Updated index

Removed `consultation-contract.md` entry. Updated `consultation-profiles.yaml`
description from "Symlink to..." to purpose-oriented text: "Canonical source
in `packages/plugins/codex-collaboration/references/`."

### `.claude/CLAUDE.md` — Package table updated

Added codex-collaboration row: `packages/plugins/codex-collaboration/` |
Python | Codex advisory runtime (consult, delegate, dialogue, review).

### `docs/tickets/...cutover.md` — PR citation fixed

Line 263: `PR #TBD` → `PR #123`.

### `docs/plans/...7e.md` — Group 7 corrected

Updated Group 7 item 14 to reflect actual implementation: deleted
`consultation-contract.md` symlink, repointed `consultation-profiles.yaml`,
updated README index. Replaced stale "Retain entries 1-2" text that
contradicted the fix-up commit.

### `packages/plugins/codex-collaboration/references/consultation-profiles.yaml` — Contract reference removed

Removed `# Reference: consultation-contract.md §14` header comment.
Changed "contract defaults" to "built-in defaults" in resolution order.

### `packages/plugins/codex-collaboration/server/profiles.py` — Docstring updated

Changed "contract defaults" to "built-in defaults" in resolution order
docstring, matching the YAML change.

### `packages/plugins/codex-collaboration/agents/context-gatherer-code.md` — Governance inlined

Replaced 7-line governance section (3 rules + 4 inapplicable stubs citing
`consultation contract §15`) with 3-line section inlining the applicable
rules. Removed all §15 citations.

### `packages/plugins/codex-collaboration/agents/context-gatherer-falsifier.md` — Governance inlined

Same change as `context-gatherer-code.md` — identical governance section.

### `packages/plugins/codex-collaboration/references/tag-grammar.md` — §7 citation removed

Line 57: "credential patterns (consultation contract §7)" → "credential
sanitizer patterns". Removed citation to deleted document.

### `docs/tickets/2026-04-23-...delegate-execution-remediation.md` — New ticket

T-20260423-01: scopes sandbox policy and approval path defects. 279 lines.
Diagnostic-first structure with vendored schema evidence, live verification
gates, hard acceptance criteria requiring non-empty artifact production.

## Codebase Knowledge

### Files Read This Session

| File | Why | Key Finding |
|------|-----|-------------|
| `runtime.py:23-38` | Ground sandbox defect | `build_workspace_write_sandbox_policy`: `includePlatformDefaults: False`, `readableRoots: [worktree]`, `networkAccess: False` |
| `delegation_controller.py:642-720` | Ground approval defect | `_CANCEL_CAPABLE_KINDS = {"command_approval", "file_change"}`, handler returns `{"decision": "cancel"}` |
| `delegation_controller.py:1743-1754` | Understand approve path | `decide(approve)` calls `build_execution_resume_turn_text` then `_execute_live_turn` — new turn with same sandbox |
| `execution_prompt_builder.py:41-77` | Understand resume prompt | Natural-language-only: "treat the caller decision below as authoritative" |
| `delegation_controller.py:246` | Check approval policy | `approval_policy` defaults to `"untrusted"` — separate mechanism from sandbox |
| `CommandExecutionRequestApprovalResponse.json` | Discover grant shapes | `accept`, `acceptForSession`, `acceptWithExecpolicyAmendment`, `applyNetworkPolicyAmendment`, `decline`, `cancel` |
| `FileChangeRequestApprovalResponse.json` | Discover grant shapes | `accept`, `acceptForSession`, `decline`, `cancel` |
| `runtime.py:160-183` | Check turn API | `run_execution_turn` accepts `sandbox_policy`, `approval_policy`, `server_request_handler` |
| `docs/references/README.md` | Review stale entries | Had `consultation-contract.md` and `consultation-profiles.yaml` entries |
| `consultation-profiles.yaml:1-16` | Check header comment | `# Reference: consultation-contract.md §14` — stale |
| `profiles.py:1-6` | Check docstring | "contract defaults" — stale terminology |
| `context-gatherer-code.md:89-99` | Check §15 citations | 3 citations to `consultation contract §15` in governance section |
| `context-gatherer-falsifier.md:135-143` | Check §15 citations | Identical governance section with §15 citations |
| `tag-grammar.md:50-63` | Check §7 citation | Line 57: "credential patterns (consultation contract §7)" |

### Delegation Architecture (Key Locations)

| Component | File | Line | Purpose |
|-----------|------|------|---------|
| Sandbox policy builder | `runtime.py` | 23-38 | Constructs `workspaceWrite` policy for delegation |
| Advisory policy builder | `runtime.py` | 17-20 | Constructs `readOnly` policy for consultations |
| Server request handler | `delegation_controller.py` | 636-720 | Handles App Server escalation requests during turns |
| Cancel-capable kinds | `delegation_controller.py` | 642 | `{"command_approval", "file_change"}` |
| Decide approve path | `delegation_controller.py` | 1743-1754 | Builds resume prompt, starts new turn |
| Resume prompt builder | `execution_prompt_builder.py` | 41-77 | Natural-language-only grant prompt |
| Turn finalization | `delegation_controller.py` | 1440-1479 | Post-turn status derivation and audit |
| Approval policy default | `delegation_controller.py` | 246 | `"untrusted"` |
| Vendored schemas | `tests/fixtures/codex-app-server/0.117.0/` | — | `CommandExecution*` and `FileChange*` response schemas |

### Approval Flow (Current — Defective)

```
Agent requests command_approval/file_change
  → _server_request_handler returns {"decision": "cancel"}
  → App Server interrupts the turn
  → Request captured in _pending_request_store
  → Job transitions to needs_escalation
  → Caller runs codex.delegate.decide(approve)
    → build_execution_resume_turn_text constructs NL prompt
    → _execute_live_turn starts NEW turn with SAME sandbox
    → Agent retries action → sandbox blocks → re-escalates
    → Loop repeats
```

### Approval Flow (Expected — After Fix)

```
Agent requests command_approval/file_change
  → _server_request_handler returns {"decision": "accept"}
  → App Server resumes the original action inline
  → Turn completes with artifacts
```

## Context

### Project State

T-02 through T-07 arc is complete. codex-collaboration is the sole Codex
integration in the repo and marketplace.

| Ticket | Status | Key Commit |
|--------|--------|------------|
| T-02 | Closed | `d4b4a988` |
| T-03 | Closed | `d4b4a988` |
| T-04 | Closed | demonstrated-not-scored |
| T-05 | Closed | `271f23aa` |
| T-06 | Closed | `85afab6b` |
| T-07 | Closed | `89e2b802` (merge commit) |
| **T-20260423-01** | **Open** | PR #124 (ticket only) |

### Mental Model

This session had two distinct phases with different shapes: (1) PR landing
was a review-response-merge cycle with iterative refinement, (2) ticket
writing was a diagnostic-first design exercise with scrutiny convergence.

The key insight from the ticket work: the delegate defects compound but the
sandbox fix has higher standalone value because it unblocks shell execution
(a prerequisite for any artifact production). The approval fix is trickier
because it depends on App Server's actual runtime behavior of schema-valid
`accept` responses — the vendored schemas prove the grant path exists, but
live behavior needs verification.

## Learnings

### Parallel 4-agent review deduplicates and cross-validates findings

**Mechanism:** Four specialized agents (code-reviewer, comment-analyzer,
silent-failure-hunter, code-simplifier) ran in parallel against the same
diff. Total runtime ~6 min wall clock (386s longest agent). Produced 15
unique findings after deduplication (some found by multiple agents from
different angles — e.g., `consultation-profiles.yaml` dangling reference
found by both comment-analyzer and silent-failure-hunter).

**Evidence:** Silent failure hunter's F6 and comment analyzer's Critical 2
were the same finding. Code simplifier's F1 and comment analyzer's
Improvement 4 were related (README description style).

**Implication:** Running agents in parallel maximizes coverage while
deduplication prevents double-counting. The triage step is essential —
15 raw findings triaged to 4 accepted fixes. Without triage, the noise
would overwhelm the signal.

### Vendored schemas are contract evidence, not just test fixtures

**Mechanism:** The `tests/fixtures/codex-app-server/0.117.0/` directory
contains JSON Schema definitions for App Server request/response types.
These schemas define the valid response shapes for `command_approval` and
`file_change` — including `accept`, `acceptForSession`,
`acceptWithExecpolicyAmendment`, `decline`, and `cancel`.

**Evidence:** The initial ticket draft used `{"decision": "approve"}` as
a hypothetical grant response. User's P2 finding: the vendored schemas
already prove `accept` is the valid grant value, not `approve`. Framing
the approval diagnostic as "unknown API discovery" was wrong when contract
evidence exists in the repo.

**Implication:** Before treating any App Server behavior as unknown, check
the vendored schemas first. They are authoritative for the wire contract
shape even if live behavior needs separate verification.

### `cancel` in App Server approval is denial + interruption, not deferral

**Mechanism:** The vendored `CommandExecutionRequestApprovalResponse` schema
defines `cancel` as "User denied the command. The turn will also be
immediately interrupted." This is semantically equivalent to deny +
interrupt, not to "defer for later approval." The current code returns
`cancel` for approved requests and then tries to resume via a new turn —
using a denial response for an approval flow.

**Evidence:** Schema description at
`CommandExecutionRequestApprovalResponse.json:75-79`: `"description":
"User denied the command. The turn will also be immediately interrupted."`

**Implication:** The fix is to return `{"decision": "accept"}` for
approved requests. `cancel` should only be used when the caller intends
to deny and interrupt.

## Next Steps

### 1. Merge PR #124 (delegate remediation ticket)

**Dependencies:** None — ticket-only PR, no code changes.

**What to review:** 1 file, 279 lines. Ticket structure and acceptance
criteria.

### 2. Start delegate remediation (T-20260423-01)

**Dependencies:** PR #124 merged (or can work from the ticket directly).

**Recommended sequence:**
1. Phase 1 diagnostic (sandbox): investigate `includePlatformDefaults`
   behavior, confirm security boundary with `True`, find minimum viable
   grant.
2. Phase 2 diagnostic (approval): verify live behavior of `accept`
   response from `_server_request_handler` for both `command_approval`
   and `file_change`.
3. Phase 3: implementation plan from diagnostic evidence.
4. Phase 4: implement + regression tests.
5. Phase 5: live `/delegate` smoke with artifact production.

**What to read first:**
- T-20260423-01 ticket (the execution boundary document)
- `runtime.py:23-38` (sandbox policy)
- `delegation_controller.py:636-720` (server request handler)
- Vendored schemas at `tests/fixtures/codex-app-server/0.117.0/`

### 3. Fix T-20260416-01 (dialogue reply extraction mismatch)

**Dependencies:** Independent of delegate remediation.

**Context:** `codex.dialogue.reply` items-array extraction mismatch. Only
true open ticket with high confidence. Narrower and less strategically
blocking than delegate remediation.

## In Progress

**Clean stopping point.** PR #123 merged to main at `89e2b802`. PR #124
(delegate ticket) open on `chore/delegate-remediation-ticket` at
`82121adf`. No uncommitted changes. Currently on the ticket branch.

## Open Questions

### 1. What does `includePlatformDefaults: True` actually grant?

**Context:** The sandbox policy investigation in T-20260423-01 Phase 1.
Need to determine whether `True` grants a curated set of system directories
or broad filesystem read access. This determines whether it's safe to
enable.

**Decision pending until:** Phase 1 diagnostic of T-20260423-01.

### 2. Does `accept` actually resume the original turn inline?

**Context:** Vendored schemas prove `accept` is valid, but live behavior
needs verification. Does App Server execute the original command when
the handler returns `{"decision": "accept"}`?

**Decision pending until:** Phase 2 diagnostic of T-20260423-01.

### 3. Does `approval_policy="untrusted"` still escalate after sandbox fix?

**Context:** Sandbox readability and approval prompting are separate
mechanisms. Even with `includePlatformDefaults: True`, the `untrusted`
approval policy may still emit escalation requests. This is a hypothesis
to verify after the sandbox fix.

**Decision pending until:** Post-sandbox-fix live smoke.

### 4. Abandoned cross-session delegation terminal outcomes (inherited)

**Context:** If a delegation job reaches terminal status in a session that
crashes before poll, and the next session has a different session ID, the
terminal outcome may be missing from `analytics/outcomes.jsonl`.

**Decision pending until:** Beyond current scope.

## Risks

### 1. `includePlatformDefaults: True` may open the security boundary

The T-05 hardening deliberately set this to `False`. Changing it without
investigation could expose host secrets to the delegated agent. The ticket's
diagnostic gate (Phase 1) explicitly requires verifying that the worktree-
only write restriction is sufficient when platform defaults are included.

### 2. `accept` may not resume turns as the schema implies

The vendored schema defines the wire contract, but runtime behavior could
differ. If `accept` doesn't resume the original action inline, the approval
fix needs a different approach (sandbox policy adjustment on resume turns,
or a documented limitation).

### 3. `.planning/` files are stale (deferred from review)

44 cross-model references across 6 `.planning/codebase/*.md` files. Tracked
in git. The 7e plan explicitly allowlisted these as generated/stale. Any
session using these for orientation gets outdated information.

## References

### PRs this session

| PR | Title | Status | Commit |
|----|-------|--------|--------|
| #123 | chore(7e): remove cross-model package and cut marketplace to codex-collaboration | Merged | `89e2b802` |
| #124 | chore: add delegate execution remediation ticket (T-20260423-01) | Open | `82121adf` |

### Authority documents

| Document | Location | Role |
|----------|----------|------|
| T-07 ticket (closed) | `docs/tickets/2026-03-30-codex-collaboration-analytics-reviewer-and-cutover.md` | T-07 AC definitions |
| T-20260423-01 ticket | `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` | Delegate remediation scope |
| 7e plan | `docs/plans/2026-04-23-t07-cross-model-removal-7e.md` | Implementation plan (merged) |
| Vendored command approval schema | `tests/fixtures/codex-app-server/0.117.0/CommandExecutionRequestApprovalResponse.json` | App Server wire contract |
| Vendored file change schema | `tests/fixtures/codex-app-server/0.117.0/FileChangeRequestApprovalResponse.json` | App Server wire contract |

### Prior handoffs (chain)

- Immediate predecessor: `docs/handoffs/archive/2026-04-22_22-04_t07-7e-cross-model-removed-t07-closed.md`
- Arc: ... → 7e smoke + plan + scrutiny + implementation + PR → **7e review +
  merge + delegate ticket (this handoff)**

## Gotchas

### 1. Vendored schemas are test fixtures, not generated

The `tests/fixtures/codex-app-server/0.117.0/` schemas are manually vendored,
not auto-generated from the App Server. If App Server updates its wire
contract, these schemas may lag. Always verify live behavior in addition to
schema evidence.

### 2. `cancel` means deny + interrupt in App Server

The `cancel` decision is not a neutral "defer for later" — it actively denies
the request and interrupts the turn. Using it for approved requests creates
the cancel-retry loop. Use `accept` or `acceptForSession` for approvals.

### 3. `approval_policy` and sandbox are independent mechanisms

`approval_policy="untrusted"` controls whether App Server prompts for
approval. Sandbox policy controls what the agent can read/write/execute.
Fixing sandbox readability doesn't necessarily eliminate approval prompts.
Both may need attention for full delegation.

### 4. Gatherer agents share identical governance sections

`context-gatherer-code.md` and `context-gatherer-falsifier.md` have
identical governance rules (now inlined). Changes to one should be mirrored
to the other. No shared reference document exists — the rules are
duplicated.

## User Preferences

### Systematic review triage with explicit verdicts

User triaged all 15 review findings with accept/reject/defer verdicts,
citing specific reasons for each. Rejections had justification ("this is
an intentional guard"), deferrals had scope reasoning ("allowlisted in 7e
plan, not a PR blocker").

### Diagnostic-first over fix-first for unknown API contracts

User's guidance for the ticket: "I'd make the first implementation gate
explicitly diagnostic, not 'fix sandbox'" and "frame it as an API-contract
discovery problem before choosing the implementation path." Values
separating what's known from what needs verification.

### Vendored schema evidence as static contract baseline

User caught the ticket using `{"decision": "approve"}` when the vendored
schemas prove `accept` is the correct value. Expects repo-local evidence
to be cited before treating behavior as unknown: "Keeping `approve` in
the ticket risks a false negative in Phase 2."

### Qualify claims about mechanism interaction

User caught the sandbox-only interaction claim being stated as fact when
`approval_policy="untrusted"` is a separate mechanism. Prefers hypotheses
labeled as hypotheses: "sandbox-first sequencing [is right], but phrase
this as a hypothesis to verify."

### Tight scope on review fix commits

User's triage was decisive: 4 items accepted, 3 rejected or deferred.
No scope creep — the accepted items were "the minimum patch I'd want
before merge." Rejected items were explicitly not blockers, even when
they had non-zero improvement value.
