---
date: 2026-04-29
time: "01-04"
created_at: "2026-04-29T05:04:38Z"
session_id: fbb6621e-8e9d-4c02-8a3c-17776668a178
resumed_from: docs/handoffs/archive/2026-04-28_23-30_candidate-a-closure-complete-att3-smoke-success-and-3-security-probes-blocked.md
project: claude-code-tool-dev
branch: feature/delegate-execution-diagnostic-record
commit: 6a2bb5ae
title: Candidate A engineering action landed in production — 7 commits pushed (closure + sandbox patch + env-tune + mechanism docs + carry-forward closeouts); awaiting plugin restart for live smoke validation
type: handoff
files:
  - docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md
  - docs/plans/2026-04-23-t07-cross-model-removal-7e.md
  - docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md
  - packages/plugins/codex-collaboration/server/runtime.py
  - packages/plugins/codex-collaboration/server/delegation_controller.py
  - packages/plugins/codex-collaboration/tests/test_runtime.py
  - packages/plugins/codex-collaboration/tests/test_delegation_env_config.py
  - packages/plugins/codex-collaboration/README.md
  - packages/plugins/context-metrics/scripts/config.py
  - packages/plugins/context-metrics/tests/test_config.py
  - packages/plugins/context-metrics/README.md
  - packages/plugins/context-metrics/CHANGELOG.md
---

# Handoff: Candidate A engineering action landed — 7 commits pushed; awaiting plugin restart for live smoke

## Goal

Continue T-20260423-01 delegate-execution remediation from prior session's Candidate A diagnostic closure. **This session converted the diagnostic conclusion into shipped production code**: Candidate A's policy patch (`includePlatformDefaults: True`) is now committed + pushed at `ce0579f6`, three carry-forward engineering improvements followed (T-07 plan reconciliation, env-tunable approval TTL, App Server interruption-mechanism source comments), and two unrelated hygiene items (context-metrics 1M-window fix, 8 ticket archives) cleared the working tree alongside.

**Bigger picture:** The 5-commit arc landing on this branch (`091d6120` → `6a2bb5ae`) implements the full lifecycle from diagnostic findings to engineering action to follow-up improvements. The branch is now in a "ready for live smoke validation" state — every code change the diagnostic recommended is on disk and pushed; what remains is the operator-side validation step (plugin restart + live `/delegate` against a real repo-edit objective) to satisfy the T-01 ticket's acceptance criteria.

**Trigger:** Prior handoff (`2026-04-28_23-30_candidate-a-closure-complete...`) explicitly enumerated "Defer commits, plugin restart, and ticket creation" as session-end phasing — this session executed all of those plus the engineering action. User's instructions arrived structured: prior session's review queries via `/copy`, this session's incremental scope expansions ("proceed with the commit", "Move to the third commit first and push them together", "Address the T-07 plan annotation now. Then, I want to address two other items: ..."). Each scope expansion was paired with explicit "commit and push" authorization.

**Stakes:**
1. **T-01 ticket nearly closeable** — only live smoke validation remains. The diagnostic closure's "engineering next action" (promote Candidate A) is shipped.
2. **Operator workflow tunability** — env-tunable approval TTL eliminates the empirical 900s race condition for diagnostic-style operator loops without further code edits.
3. **Source-discoverability of mechanism finding** — the "App Server kills shell mid-execution at boundary-violating ops" insight is now in `runtime.py`'s docstring, not just in the run-record handoff prose. Future maintainers reading the policy builder learn the enforcement mechanism without crawling diagnostic records.
4. **Plan/ticket reconciliation** — T-07's plan doc (closed initiative) was still describing pre-fix policy as "root cause" without acknowledgment that both root causes are now closed in production.

**Success criteria (all met):**
- ✓ Closure commit pushed (`091d6120`) — diagnostic record durable on origin
- ✓ Context-metrics 1M-window fix committed and pushed (`d21c6284`) — separate concern, separate commit
- ✓ 8 carry-forward ticket archives committed and pushed (`f66f8b7c`) — `R100` rename detection clean
- ✓ Candidate A sandbox policy patch committed and pushed (`ce0579f6`) — full implementation review verdict READY before commit
- ✓ T-07 plan annotation committed and pushed (`736fcf95`) — historical text preserved, status callout added
- ✓ Env-tunable approval TTL implemented + tested + committed and pushed (`cd0f2142`) — 7/7 new tests pass; full suite 1070/1070
- ✓ App Server interruption mechanism docstring committed and pushed (`6a2bb5ae`) — multi-paragraph doc captures sufficiency + safety + empirical anchor
- ✓ Working tree fully clean across session boundary
- ✓ Plugin restart guidance provided (operator action — not Claude-executable)

## Session Narrative

Resumed from `2026-04-28_23-30_candidate-a-closure-complete...` via `/handoff:load`. Prior session left the working tree dirty with three unrelated concerns (run record closure, context-metrics fix, ticket carry-forward) and an unpushed local state — closure was complete diagnostically but not committed.

**Phase 1 — Reviewer scrutiny + closure commit (091d6120).** Before any commits, user routed a `/copy` adversarial-review pass through Codex. Findings (P1, P1, P2):
- P1: top-level run-record status said "Candidate A pending operator-mediated Claude Code restart" — contradicted the closure body
- P1: Candidate B framing keyed to "att2 outcome" but att2 canceled (att3 was the success — attempt-numbering drift)
- P2: "Implication for Branch decision (still pending update at section below)" — self-contradictory after closure was filled in

I applied 5 doc-only edits (3 explicit + 2 scope-note consistency), ran `git diff --check` clean, and committed as `091d6120` — `docs(delegate): close Candidate A att1+att2+att3 + security probes 1+2+3` (484/-16, run-record only). Body cited diagnostic basis (att3 succeeded, 3 probes BLOCKED), enumerated per-section changes, noted ticket open pending live smoke. Pushed via fast-forward after user's "/copy"-routed verification recommended push.

**Phase 2 — Two follow-up commits (d21c6284, f66f8b7c).** User instructed "Move to the third commit (chore(tickets): for the 8 carry-forward moves) first and push them together" — so I committed context-metrics 1M-window fix as `d21c6284` (4 files, +14/-1, all 11 model-detection tests pass), then verified the 8 ticket files were pure renames via `diff <(git show HEAD:...) <(...new path...)` (all identical), staged with explicit `git rm` + `git add` pairs, and committed as `f66f8b7c` — `chore(tickets): archive 8 closed tickets to closed-tickets/`. Git's rename detection caught all 8 as `R100` (100% similarity, zero content insertions/deletions). Pushed both commits in one fast-forward.

**Phase 3 — User's Candidate A implementation review (ce0579f6 build-up).** User implemented the Candidate A sandbox policy patch directly (without delegating to me) — flipped `includePlatformDefaults: False` → `True` in `runtime.py:33`, updated the `test_runtime.py` regression assertion at line 178, added an "Implementation update (2026-04-29)" section to the T-01 ticket with header rename "Current policy shape" → "Original policy shape (pre-fix)" — and asked: "Please review my work."

This was an explicit invocation of the `implementation-review` skill. I built a Requirements Ledger (R1-R6 derived from `091d6120`'s closure record + ticket spec), ran falsification pass (each requirement: does it hold under scrutiny?) + failure-modes pass (call sites, Pydantic pins, plugin in-memory consistency, RT.1 carry-forward, doc drift, acceptance-criteria coherence, wrong-False/True location, security-boundary test scope, broader test runs). All 6 requirements held; 0 P1/P2 findings; 1 P3 (T-07 plan still describing pre-fix as root cause — non-blocking). Targeted test passed 11/11; broader suite passed 1063/1063 in 250s. Verdict: **READY**.

**Phase 4 — Candidate A commit (ce0579f6).** User said "proceed with the commit (suggested message above)". I committed as `ce0579f6` — `feat(codex-collaboration): promote Candidate A sandbox policy (includePlatformDefaults: True)`. Body anchored the change in `091d6120`'s diagnostic record, cited empirical sufficiency (att3 byte-perfect smoke at ~1m33s) and safety (3 probes BLOCKED, App Server interrupts uniformly), enumerated per-file changes, and explicitly stated the ticket remains open pending live smoke. 3 files, +29/-8.

**Phase 5 — User scope expansion to 3 carry-forward items.** User: "Address the T-07 plan annotation now. Then, I want to address two other items: 1. env-tunable `_APPROVAL_OPERATOR_WINDOW_SECONDS` 2. capture App Server interruption-mechanism finding in plugin source comments. Once all 3 of these are completed, they can be committed and pushed together"

I gathered context in parallel:
- T-07 plan structure: defects at L33-45, "What was proved/not proved/Transparency" at L47-57. Annotation point: callout after defect 2.
- Env-var conventions: only `CLAUDE_PLUGIN_DATA` (Claude Code platform var) exists; no `CODEX_COLLAB_*` prefix. Establishing convention.
- TTL constant location: `delegation_controller.py:116`. `os` not yet imported.
- Logger location: line 114 — set up before constant, available to helper.
- Confirmed PR #126 / commit `36ef13e8` was deferred-approval-response (defect 2 fix) → T-07 annotation can correctly close both root causes.

**Phase 6 — Implement all 3 in parallel where possible.**
- T-07 plan: inserted callout block after defect 2 (15 lines) referencing `ce0579f6` (defect 1) + `36ef13e8` (defect 2)
- runtime.py: extended `build_workspace_write_sandbox_policy` docstring from 1 line → 17-line block covering enforcement mechanism + `includePlatformDefaults: True` rationale + empirical anchor
- delegation_controller.py: added `os` import, introduced `_APPROVAL_OPERATOR_WINDOW_SECONDS_ENV` and `_APPROVAL_OPERATOR_WINDOW_SECONDS_DEFAULT` constants, added `_read_approval_operator_window_seconds()` helper with non-numeric/zero/negative validation + fall-back-with-warning, replaced hardcoded constant with helper call
- Created `test_delegation_env_config.py`: 7 tests (default-when-unset, custom integer, custom float, non-numeric, zero, negative, empty-string) — initially with wrong import path

**Phase 7 — Test file import error correction (ImportError → fix).** First pytest run failed: `ModuleNotFoundError: No module named 'codex_collaboration'`. I'd assumed Python-package-style imports (`from codex_collaboration.server.X`) but pyproject.toml has `pythonpath = ["."]` and existing tests use `from server.X` directly. Fixed import to `from server.delegation_controller import ...` — 7/7 tests passed in 0.02s.

**Phase 8 — README Configuration section + broader test pass.** Added Configuration section between Limitations and Tests in `packages/plugins/codex-collaboration/README.md` documenting `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS`. Broader test suite ran in background while I drafted the commit messages: **1070/1070 passed in 254.66s** (1063 baseline + 7 new = 1070 expected).

**Phase 9 — Three concern-isolated commits (736fcf95, cd0f2142, 6a2bb5ae) + push.** User's "they can be committed and pushed together" had ambiguous parsing — could mean 1 commit or 3 + 1 push. I chose 3 separate commits per the branch's per-concern discipline (offered to combine if user wanted, but executed as 3):
- `736fcf95` — `docs(plans): annotate T-07 plan with post-Candidate-A-closure status` (1 file, +15)
- `cd0f2142` — `feat(codex-collaboration): env-tune approval-operator window via CODEX_COLLAB_*` (3 files, +133/-1)
- `6a2bb5ae` — `docs(codex-collaboration): document App Server interruption mechanism in policy builder` (1 file, +20/-1)

All 4 commits (including `ce0579f6`) pushed in one operation: `f66f8b7c..6a2bb5ae` fast-forward. HEAD verified == upstream.

**Phase 10 — Plugin restart guidance.** User asked: "How do I restart the codex-collaboration plugin?" I searched claude-code-docs (`/reload-plugins`, "plugin lifecycle reload changes") and inspected running processes via `ps -ef | grep codex-collaboration`: PID 21408 (Claude Code) → PID 21455 (uv wrapper) → PID 21509 (long-lived Python MCP server holding stale module table). Provided answer: full Claude Code restart is deterministic (Python `import` is cached in `sys.modules`); cheaper alternatives exist (`/reload-plugins`, `/plugin disable/enable`) but their behavior on `--plugin-dir` dev-loaded plugins is doc-ambiguous; verify by checking PID changed.

**Phase 11 — Save handoff (this).** User invoked `/handoff:save`. Read synthesis-guide.md, gathered frontmatter inputs, constructed comprehensive handoff.

Set aside for next session: plugin restart (operator action), live `/delegate` smoke against real repo-edit objective, T-01 ticket close (after smoke validates).

## Decisions

### D1: Three concern-isolated commits for the 3 carry-forward items, not one combined

**Choice:** Land the carry-forward items as three separate commits (`736fcf95` docs(plans), `cd0f2142` feat(codex-collaboration), `6a2bb5ae` docs(codex-collaboration)) pushed together, rather than as a single combined commit.

**Driver:** User's phrasing "Once all 3 of these are completed, they can be committed and pushed together" was ambiguous between "1 combined commit" and "3 commits, 1 push". Branch's prior discipline (4 single-concern commits in this session: `091d6120`, `d21c6284`, `f66f8b7c`, `ce0579f6`) signals per-concern grouping is the project pattern. Memory feedback `feedback_handle_commits.md` says "default to action when work reaches a coherent buildable chunk" — choose the cleaner path proactively.

**Rejected alternatives:**
- **One combined commit titled `chore(codex-collaboration): post-closure engineering improvements`**. Rejected: commit type would have to be the most-significant (`feat` for env-tuning), polluting `git log --grep="^feat"` queries with bundled docs. Different commit types (docs / feat / docs) signal genuinely different concerns.
- **Two commits (bundle T-07 with one of the docs commits)**. Rejected: T-07 plan annotation is unrelated to plugin code; bundling would make scope-grep harder.
- **Defer to next session and ask user explicitly**. Rejected: latency without benefit; user said "proactively handle commits" via memory.

**Implication:** Each commit individually revertable. `git log --oneline` reads as a single coherent narrative across the branch's 7 commits. Future readers scanning by `<type>(<scope>):` get accurate filtering.

**Trade-offs accepted:** Three commit messages to write instead of one. Slightly more git operations.

**Confidence:** Medium-High (E2) — pattern-matching on 4 prior single-concern commits in same branch + project pattern from memory + explicit branch discipline. User can override if disagreed (none of the commits push to main; reversion is local).

**Reversibility:** High — `git reset --soft HEAD~3` would re-stage all 3 commits' content if user wanted to combine. Not destructive.

**Change trigger:** If user explicitly says "I prefer one combined commit when items are conceptually related", switch to bundled grouping.

### D2: Env-var name `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS`

**Choice:** Name the env var `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS` (mirrors the constant `_APPROVAL_OPERATOR_WINDOW_SECONDS` with `CODEX_COLLAB_` prefix).

**Driver:** No existing `CODEX_COLLAB_*` env vars in the package — only `CLAUDE_PLUGIN_DATA` (Claude Code platform var). This implementation establishes the convention, so picking a scalable name matters.

**Rejected alternatives:**
- **`CODEX_COLLABORATION_APPROVAL_OPERATOR_WINDOW_SECONDS`** (full plugin name). Rejected: too long; future env vars would each be ~50 characters.
- **`CODEX_COLLAB_APPROVAL_TTL_SECONDS`** (semantic abbreviation). Rejected: "TTL" loses the semantic specificity that the constant carries ("operator window" vs "request TTL" or "session TTL"). Mirroring the constant name keeps the env-var → constant relationship discoverable.
- **`CODEX_DELEGATE_APPROVAL_WINDOW_SECONDS`** (focus-scoped). Rejected: this var lives in delegation flow, but the prefix `CODEX_DELEGATE_` would force a separate namespace from the broader plugin (consultation, dialogue, review) — fragmenting future env-var space.

**Implication:** All future plugin runtime tunables get `CODEX_COLLAB_` prefix (matches the `codex-collaboration` plugin name with conventional `_` separator). Future env-var documentation table extends naturally.

**Trade-offs accepted:** Long name (49 characters). Mitigated by: README documents it; only operators tuning it need to type it; matches the constant name exactly so future-self recognizes the relationship.

**Confidence:** Medium (E1) — convention pick based on first-mover principle; no existing project pattern to match. Easy to rename if future env vars suggest a better convention.

**Reversibility:** Medium — renaming requires touching `delegation_controller.py`, test file, and README. Could be done in a single migration commit.

**Change trigger:** If a future env var requires a different prefix (e.g., shared tooling that already uses `CC_*`), reconsider.

### D3: Helper function pattern for env-tuning vs inline read

**Choice:** Implement `_read_approval_operator_window_seconds()` as a private helper function called once at module load, rather than inlining the env read into the constant assignment.

**Driver:** Testability. Inline reads (`_APPROVAL_OPERATOR_WINDOW_SECONDS = float(os.environ.get(...) or 900)`) are not directly testable without `importlib.reload` machinery. Helper functions can be tested by `patch.dict(os.environ, ...)` then calling the helper — clean and idiomatic.

**Rejected alternatives:**
- **Inline at constant assignment**. Rejected: untestable without module reload; validation logic (numeric parse, positive check, fall-back-with-warning) would inflate the line and obscure intent.
- **Eager singleton class** (`class ApprovalConfig: ...; CONFIG = ApprovalConfig()`). Rejected: over-engineered for a single value; introduces a new abstraction that doesn't generalize until the second tunable arrives.
- **Lazy property** (read at every call site). Rejected: behavior change — current code reads the constant once; changing to per-call read would bypass the "restart required" semantic that matches Python module-load conventions.

**Implication:** Future tunables can follow the same pattern (helper function → constant). Tests land in dedicated `test_delegation_env_config.py` module; pattern scales.

**Trade-offs accepted:** Slightly more code (helper + 2 helper-pinning constants `_ENV` and `_DEFAULT`) vs a one-line read. ~30 extra lines in `delegation_controller.py`. Mitigated by full test coverage of all branches.

**Confidence:** High (E2) — testability is empirically validated (7 tests cover all branches in 0.02s); helper pattern is the standard Python convention.

**Reversibility:** High — could collapse to inline at any time if the helper proves unnecessary.

**Change trigger:** If future tunables need runtime-mutation (vs module-load-only), would need a different pattern (lazy property with cache, or a Settings class).

### D4: Validation pattern: fall-back-with-warning, not raise

**Choice:** Invalid env values (non-numeric, zero, negative, empty string) fall back to the default with a `logger.warning(...)` rather than raising an exception.

**Driver:** Operator UX. Plugin loads at session start; raising on a malformed env var would prevent the entire plugin from loading. Fall-back-with-warning preserves plugin functionality with predictable default behavior, leaving a discoverable trace in the log for the operator to fix.

**Rejected alternatives:**
- **Raise `ValueError`**. Rejected: breaks plugin load on invalid config — plugin disable equivalent. Bad UX for typo-level errors (e.g., `1800s` instead of `1800`).
- **Silently fall back without warning**. Rejected: violates the project's "fail fast" / "explicit over silent" tenets. Operator might not realize their tuning was ignored.
- **Use `logger.error`**. Rejected: error level implies action-required; a typo-corrected default is just informational. Warning is the right severity.

**Implication:** Operators set the env var, see expected behavior with default if typoed, find warning in the log when troubleshooting. Plugin always loads.

**Trade-offs accepted:** Operators might miss the warning if they don't check logs. Mitigated by: README documents validation rules; the tunable's purpose (extending TTL for diagnostic workflows) is itself a debugging context where logs are scrutinized.

**Confidence:** High (E2) — matches Python ecosystem conventions for env-var-driven config (e.g., `LOGLEVEL` defaults to `WARNING` if invalid, doesn't crash).

**Reversibility:** High — toggle to raise via single-line change in helper.

**Change trigger:** If operators consistently miss warnings and ship misconfigured plugin, escalate to error or refuse-to-load.

### D5: T-07 plan annotation form: callout block, not full rewrite

**Choice:** Insert a blockquote callout (`> **Status update (post-2026-04-29):** ...`) after the defect 2 description, preserving the historical defect text verbatim.

**Driver:** The T-07 plan is a closed-initiative document. Rewriting historical text would lose the point-in-time T-07-closure context (what was true when T-07 closed vs what's true now). Future readers reconstructing the T-07 → T-01 handoff need both states.

**Rejected alternatives:**
- **Rewrite the defect descriptions to past tense**. Rejected: erases historical context; T-07 closed when both defects were live, that's diagnostic data.
- **Add a top-of-file banner only**. Rejected: too distant from the specific defect descriptions; a reader scrolling to a section would miss it.
- **Inline the annotation into each defect description as parentheticals**. Rejected: clutters the defect descriptions; harder to scan.

**Implication:** Historical text preserved; current state cross-referenced via callout. Reader gets both views in one place.

**Trade-offs accepted:** Slightly more vertical space than an inline parenthetical.

**Confidence:** High (E2) — pattern matches the doc-rot-prevention practice from the prior session's run-record updates ("Original policy shape (pre-fix)" header pattern).

**Reversibility:** High — callout is a single block, easy to edit/remove.

**Change trigger:** None — historical preservation is a permanent value.

### D6: Commit type `feat` for Candidate A (vs `fix`)

**Choice:** Commit type `feat(codex-collaboration): promote Candidate A sandbox policy (includePlatformDefaults: True)`.

**Driver:** The closure record framed it as "Engineering action: promote Candidate A's policy configuration as the sandbox-policy patch" (engineering-action language). The commit's user-impact framing is "delegated shell execution is now structurally enabled" — that's a capability landing, not just a bug fix.

**Rejected alternatives:**
- **`fix(codex-collaboration): unblock delegated shell execution under untrusted sandbox`**. Rejected: technically defensible (the previous policy was a defect that blocked execution), but loses the diagnostic-validated framing. "Promote" implies a deliberate forward step from a proven-safe diagnostic conclusion, not just removing a block.
- **`refactor(codex-collaboration): ...`**. Rejected: behavior change, not refactor.

**Implication:** `git log --grep="^feat"` correctly identifies the moment of capability landing.

**Trade-offs accepted:** Slightly less obvious to readers searching `git log --grep="^fix"` for the fix to T-01.

**Confidence:** Medium (E1) — convention pick; either `feat` or `fix` defends in review. User explicitly accepted the suggested message (silence == endorsement).

**Reversibility:** Low — commit message is durable. Could be amended pre-merge but generally not worth it.

**Change trigger:** If team adopts a different `feat` vs `fix` convention.

### D7: Plugin restart guidance — full Claude Code restart, not /reload-plugins

**Choice:** Recommend full Claude Code restart as the deterministic answer; mention `/reload-plugins` and `/plugin disable/enable` as cheaper alternatives with documented caveats.

**Driver:** Python `import` is cached in `sys.modules`. The MCP server process (PID 21509) has `delegation_controller.py` and `runtime.py` baked into its module table. There's no `importlib.reload` in the codex-collaboration server's hot path. Process restart is the only deterministic way to load a new module image. Memory `2026-04-28_23-30_...` confirms: prior session also concluded "restart plugin (Claude Code restart)".

**Rejected alternatives:**
- **Recommend `/reload-plugins` first**. Rejected: docs ambiguous on whether it respawns MCP server processes for source-only edits. The doc body specifically calls out enable/disable/install lifecycle — not source code edits. Recommending it as the primary answer would risk false success (operator runs `/reload-plugins`, sees component-count summary, assumes it worked, runs live smoke against stale code).
- **Recommend killing PID 21509 directly**. Rejected: Claude Code may not handle child-process death gracefully; clean shutdown via session exit is safer.

**Implication:** User has clear deterministic path + verification step (check PID 21509 is gone). Operator-side action; not Claude-executable.

**Trade-offs accepted:** Loses session state (mitigated by `/handoff:save`). Heaviest restart option.

**Confidence:** High (E3) — triangulated by: docs (positions `/reload-plugins` as alternative-to-restart, suggesting restart is the canonical path); Python language semantics (sys.modules caching); prior session memory (operationally validated).

**Reversibility:** N/A — guidance only, not a code change.

**Change trigger:** If Claude Code adds a documented "reload Python source" feature for `--plugin-dir` plugins.

## Changes

### `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — closure additions + 5 reviewer-found consistency fixes

**Purpose:** Land prior session's closure work durably + apply Codex `/copy` review fixes.

**Approach:** Single bundled commit (`091d6120`). Prior session's closure additions (~287 lines) + this session's 5 reviewer fixes (~50 net) committed together per prior handoff's D4 phasing.

**Key implementation details:**
- L5 top-level status: "pending operator-mediated Claude Code restart" → "att1+att2+att3 + security probes 1+2+3 executed and adjudicated (Branch — Sandbox patch candidate fires; S1 refuted for canonical workload). Engineering action pending: promote Candidate A's policy configuration..."
- L269 Policy Variants Candidate B cell: "Post-att2 conditional. Role depends on Candidate A att2 outcome..." → "Post-Candidate-A-success conditional. Role determined by Candidate A's first successful approved-execution attempt (att3 — renamed from "att2 attempt 2" after att2 attempt 1 canceled by approval timeout): att3 succeeded → optional minimum-grant minimization..."
- L276-280 Candidate B Matrix scope note: forward-conditional language → retrospective ("Resolved (post-att3, 2026-04-29): att3 succeeded — shell executed past the gate, smoke artifact produced byte-perfect, security probes 1+2+3 all BLOCKED. Per the success branch below, Candidate B is now optional minimum-grant minimization (security hygiene only).")
- L1254 "still pending update at section below" → "recorded in the Candidate A Branch decision section below"
- L1365 "att2 succeeded → B becomes hygiene-only" → "att3 succeeded → B becomes hygiene-only"

**Commit:** `091d6120` — `docs(delegate): close Candidate A att1+att2+att3 + security probes 1+2+3` (484 insertions, 16 deletions).

### `packages/plugins/context-metrics/{config.py, test_config.py, README.md, CHANGELOG.md}` — 1M-window detection for Opus 4.7

**Purpose:** Fix dashboard misreading sessions on `claude-opus-4-7` as 200k window (default).

**Approach:** Add `claude-opus-4-7` to `MODEL_WINDOWS` registry in `scripts/config.py`. Cover both the bare model ID and the `[1m]` suffix variant in tests.

**Key implementation details:**
- `scripts/config.py:18` (one line): added `"claude-opus-4-7": 1_000_000,` between `claude-opus-4-6` and `claude-sonnet-4-6`
- `tests/test_config.py:55-65` (10 lines): added `test_opus_4_7_detects_1m` and `test_opus_4_7_with_1m_suffix_detects_1m` (the latter covers `claude-opus-4-7[1m]` — the actual wire model ID this session ran on per the system prompt)
- `README.md:148`: added Opus 4.7 row to the model detection table
- `CHANGELOG.md`: documented under both "Added" (new model entry) and "Fixed" (user-facing bug — sessions saw `Nk/200k` until reactive `maybe_upgrade_window` fallback fired at >200k)

**Commit:** `d21c6284` — `fix(context-metrics): detect claude-opus-4-7 1M context window` (4 files, 14 insertions, 1 deletion). 11/11 `TestModelDetection` tests pass.

### 8 ticket files: `docs/tickets/2026-03-30-*.md` and `docs/tickets/2026-04-10-*.md` → `docs/tickets/closed-tickets/`

**Purpose:** Archive 8 closed tickets carry-forward from prior session's closeout activity.

**Approach:** Pure renames (R100). Verified via `diff <(git show HEAD:...) <(...new path...)` on 3 spot-checked files (all identical). Staged with explicit `git rm` + `git add` pairs (no `git add -A`).

**Key implementation details:**
- 6 codex-collaboration tickets from 2026-03-30: analytics-reviewer-and-cutover, dialogue-parity-and-scouting-retirement, execution-domain-foundation, plugin-shell-and-consult-parity, safety-substrate-and-benchmark-contract, context-assembly-redaction-hardening
- 2 dialogue tickets from 2026-04-10: T-20260410-02-harden-dialogue-first-turn-fast-path-and-test-cove, dialogue-codex-turn-semantics-clarification
- All 8 detected as `R100` by git's rename detection (100% similarity, zero content insertions/deletions)
- Established convention: `docs/tickets/closed-tickets/` already had 7 prior closures; this commit continues the pattern

**Commit:** `f66f8b7c` — `chore(tickets): archive 8 closed tickets to closed-tickets/` (8 R100 renames, 0 insertions, 0 deletions).

### `packages/plugins/codex-collaboration/server/runtime.py` (Phase 4 commit) — Candidate A sandbox policy promotion

**Purpose:** Convert diagnostic conclusion into shipped production code. Set `includePlatformDefaults: True` in `build_workspace_write_sandbox_policy`.

**Approach:** Single-line bool flip (`False` → `True`). Preserve all other 6 fields verbatim.

**Key implementation details:**
- `runtime.py:33`: `"includePlatformDefaults": False` → `True`. No other lines changed.
- All 7 policy fields preserved: `type: workspaceWrite`, `writableRoots: [worktree-only]`, `readOnlyAccess.{type, readableRoots, includePlatformDefaults}`, `networkAccess: False`, `excludeSlashTmp: True`, `excludeTmpdirEnvVar: True`
- `tests/test_runtime.py:178`: corresponding regression-test assertion updated to expect `True`
- `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md`: header rename "Current policy shape" → "Original policy shape (pre-fix)"; added "Implementation update (2026-04-29)" section pointing to diagnostic record; updated Verified column to reflect both pre-fix state and post-Candidate-A promotion.

**Commit:** `ce0579f6` — `feat(codex-collaboration): promote Candidate A sandbox policy (includePlatformDefaults: True)` (3 files, 29 insertions, 8 deletions). User implemented; I reviewed (verdict READY) and committed.

### `docs/plans/2026-04-23-t07-cross-model-removal-7e.md` — T-07 plan post-Candidate-A-closure annotation

**Purpose:** Reconcile T-07's plan doc (closed initiative) with the current state of its identified root causes (both now closed in production).

**Approach:** Insert a callout block after the defect 2 description; preserve historical text verbatim.

**Key implementation details:**
- Added 15-line blockquote callout (`> **Status update (post-2026-04-29):** ...`) after L45 (end of defect 2 description), before L47 ("What was proved")
- References commit `ce0579f6` (defect 1: Candidate A sandbox patch) and PR #126 / commit `36ef13e8` (defect 2: deferred-approval response)
- Provides forward pointers: `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` (Candidate A closure) + `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` (T-01 ticket)

**Commit:** `736fcf95` — `docs(plans): annotate T-07 plan with post-Candidate-A-closure status` (1 file, 15 insertions).

### `packages/plugins/codex-collaboration/server/delegation_controller.py` + `tests/test_delegation_env_config.py` (new) + `README.md` — env-tunable approval window

**Purpose:** Implement the deferred env-tuning support that the existing `# configurable via env later` comment in `delegation_controller.py:116` flagged. Diagnostic-style operator workflows (`/copy + adversarial scrutiny per cycle`) empirically exceed the 900s default TTL — three independent timeouts in prior diagnostic runs.

**Approach:**
- Read at module load via helper function (`_read_approval_operator_window_seconds`)
- Validate (must be positive number); fall back to default with `logger.warning(...)` on invalid
- Establish `CODEX_COLLAB_*` env-var prefix convention

**Key implementation details:**
- `delegation_controller.py:62`: added `import os` (between `logging` and `subprocess`, alphabetical)
- `delegation_controller.py:116-156`: introduced `_APPROVAL_OPERATOR_WINDOW_SECONDS_ENV = "CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS"` and `_APPROVAL_OPERATOR_WINDOW_SECONDS_DEFAULT: float = 900.0` constants; added `_read_approval_operator_window_seconds()` helper with non-numeric/zero/negative validation; replaced `_APPROVAL_OPERATOR_WINDOW_SECONDS: float = 900` with `_APPROVAL_OPERATOR_WINDOW_SECONDS: float = _read_approval_operator_window_seconds()`
- Removed comment `# 15 minutes; configurable via env later` (now obsolete); replaced with `# Env-tunable via CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS at module load.`
- `tests/test_delegation_env_config.py` (new, 90 lines): 7 tests — `test_default_when_env_unset`, `test_custom_integer`, `test_custom_float`, `test_invalid_string_falls_back_with_warning`, `test_zero_falls_back_with_warning`, `test_negative_falls_back_with_warning`, `test_empty_string_falls_back_with_warning`. Initially had wrong import path (`from codex_collaboration.server.X`) — corrected to `from server.X` after first pytest run failed with `ModuleNotFoundError`.
- `README.md:81`: inserted "## Configuration" section between "## Limitations" and "## Tests" with 1-row table documenting `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS`

**Commit:** `cd0f2142` — `feat(codex-collaboration): env-tune approval-operator window via CODEX_COLLAB_*` (3 files modified + 1 new, 133 insertions, 1 deletion). 7/7 new tests pass; full codex-collaboration suite 1070/1070 in 254.66s.

### `packages/plugins/codex-collaboration/server/runtime.py` (Phase 6 commit) — App Server interruption mechanism docstring

**Purpose:** Capture the empirical "App Server kills shell mid-execution at boundary-violating ops, uniform across operation classes" finding in plugin source — currently only in run-record handoff prose.

**Approach:** Extend `build_workspace_write_sandbox_policy` docstring from 1 line to multi-paragraph block.

**Key implementation details:**
- Original docstring: `"""Return the v1 execution sandbox policy for an isolated worktree."""`
- New docstring (17 lines): 4-paragraph block covering:
  1. Title line (preserved from original)
  2. Enforcement note: shell process interrupted mid-execution at first boundary-violating operation, uniform across operation classes (network, sensitive-host-path read, sibling-worktree read), NOT permission-error-returned-to-userspace, chain patterns like `cmd || handler` cannot catch sandbox denials
  3. `includePlatformDefaults: True` rationale: grants curated platform-default reads (e.g., `/bin/zsh`, `/usr/bin/env`) needed for command execution
  4. Empirical anchor: T-01 Candidate A diagnostic; sufficiency (smoke artifact succeeded) + safety (3 probes BLOCKED); pointer to `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md`

**Commit:** `6a2bb5ae` — `docs(codex-collaboration): document App Server interruption mechanism in policy builder` (1 file, 20 insertions, 1 deletion). Docs-only; no behavior change.

## Codebase Knowledge

### Files read this session

| File | Why read | Understanding gained |
|------|----------|----------------------|
| `packages/plugins/codex-collaboration/server/runtime.py:23-50` | Verify Candidate A patch shape; locate docstring extension point | Function is pure; single source of truth for policy shape; line 33 is the lone False→True target; docstring was 1 line before extension |
| `packages/plugins/codex-collaboration/tests/test_runtime.py:1-25, 167-200` | Verify test convention (imports + assertion shape) | Tests use `from server.runtime import ...` (NOT `codex_collaboration.server.runtime`); pyproject pythonpath = ["."]; assertion uses `assert policy == {...}` exact-equality dict literal pinning every field |
| `packages/plugins/codex-collaboration/server/delegation_controller.py:1-70, 100-130` | Find TTL constant location; verify imports + logger setup | TTL constant `_APPROVAL_OPERATOR_WINDOW_SECONDS: float = 900` at L116 with comment "configurable via env later"; `os` NOT yet imported (need to add); `logger = logging.getLogger(__name__)` at L114 (available before L116 helper); imports stdlib alphabetical |
| `packages/plugins/codex-collaboration/server/delegation_controller.py:935-955` | Investigate Pyright "unreachable" warning at L942 | `case _: assert_never(outcome)` pattern at L942 — defensive exhaustiveness guard; Pyright marks unreachable because all union members handled by explicit `case` arms; pre-existing (L902 at HEAD before my +40-line shift) |
| `packages/plugins/codex-collaboration/tests/test_delegation_controller.py:1-25` | Verify test imports convention (since test_runtime.py is small) | Same convention: `from server.X import Y`; pyproject `pythonpath = ["."]` makes `server` the import root |
| `packages/plugins/codex-collaboration/README.md:1-90` | Find Configuration section insertion point | No existing Configuration section; structure ends `Limitations → Tests`; insert "## Configuration" between them |
| `docs/plans/2026-04-23-t07-cross-model-removal-7e.md:1-60` | Locate annotation point for T-07 plan | Defects at L33-45; "What was proved/not proved/Transparency" at L47-57; cleanest annotation point is callout after defect 2 (L45) before L47 |
| `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md:1, 263-300, 1245-1255, 1350-1374` | Apply 5 reviewer-found consistency fixes | L5 top-level status, L269 Policy Variants cell, L273-279 scope note, L1254 implication line, L1365 downstream att2/att3 reference — all needed updates for internal consistency |
| `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md:228-275` | Verify acceptance criteria post-implementation | 6 criteria still well-formed for live smoke validation; criteria are observable post-restart; 4 already proven empirically (decide-approve grants, artifact materialization, hash stability, no approval-loop recurrence); 2 require fresh repo-edit objective |

### Architecture: codex-collaboration plugin process structure (mapped this session)

| Layer | PID | Role | Lifecycle |
|---|---|---|---|
| Claude Code | 21408 | Plugin host; spawns plugin processes | Long-lived per Claude Code session |
| `uv run` wrapper | 21455 | Resolves plugin venv; executes bootstrap script | Long-lived child of 21408 |
| Plugin Python MCP server | 21509 | Holds module table for `delegation_controller.py`, `runtime.py`, etc.; exposes JSON-RPC over stdio | Long-lived child of 21455 |
| Plugin data root | (filesystem) | `~/.claude/plugins/data/codex-collaboration-inline/` — JSONL stores (audit, jobs, requests, journal, runtimes) | Persistent across plugin restarts |
| Codex App Server | (per-delegation) | Spawned by plugin per-delegation; enforces sandbox policy by interrupting shell mid-execution | Per-delegation, terminates with job |

**Key insight:** PID 21509 holds Python's `sys.modules` cache. Module imports (`from .runtime import build_workspace_write_sandbox_policy`) bind the function object at first import. On-disk source changes do NOT propagate to the running process. Process restart is the only deterministic way to load new module images.

### Test conventions (codex-collaboration)

| Convention | Example | Source |
|---|---|---|
| Import path: `from server.<module>` | `from server.runtime import build_workspace_write_sandbox_policy` | `tests/test_runtime.py:7-10`; `pyproject.toml` has `pythonpath = ["."]` and `testpaths = ["tests"]` |
| Test file naming: `test_<area>_<focus>.py` for focused tests | `test_delegation_decision_result_shape.py`, `test_delegation_exceptions.py`, `test_delegation_job_parked_request_id.py`, `test_delegation_sanitization.py`, `test_delegation_env_config.py` (this session) | Existing tests directory structure |
| Test class pattern: `TestXxx` for grouping related tests | `TestModelDetection`, `TestRunTurnEffort`, `TestReadApprovalOperatorWindowSeconds` (this session) | `tests/test_runtime.py`, `tests/test_delegation_env_config.py` |
| `pytest.LogCaptureFixture` for log assertions | `caplog: pytest.LogCaptureFixture` parameter; `with caplog.at_level(logging.WARNING):` | `tests/test_delegation_env_config.py` (this session, established) |
| `unittest.mock.patch.dict(os.environ, ...)` for env-var tests | `with patch.dict(os.environ, {"VAR": "value"}):` | `tests/test_delegation_env_config.py` (this session) |

### Env-var conventions (codex-collaboration plugin) — established this session

| Variable | Default | Validation |
|---|---|---|
| `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS` | `900.0` (15 min) | Must be positive number; non-numeric / zero / negative / empty fall back to default with WARNING log |

**Convention rules (for future env vars):**
- Prefix: `CODEX_COLLAB_*` (matches plugin name with underscore separator)
- Read at module load via helper function (testable; mirrors Python module-load conventions)
- Validation: fall back to default with `logger.warning` on invalid (preserves plugin load; explicit-over-silent)
- Plugin restart required for changes (matches Python `sys.modules` caching semantics)
- Document in `README.md` "## Configuration" section table

### Key locations (post-this-session)

| Concept | Location |
|---|---|
| Sandbox policy builder + enforcement docstring | `packages/plugins/codex-collaboration/server/runtime.py:23-58` |
| TTL helper + constant | `packages/plugins/codex-collaboration/server/delegation_controller.py:116-156` |
| TTL helper tests | `packages/plugins/codex-collaboration/tests/test_delegation_env_config.py` |
| Plugin Configuration docs | `packages/plugins/codex-collaboration/README.md` (## Configuration section) |
| TTL → registry call site | `packages/plugins/codex-collaboration/server/delegation_controller.py:1071` |
| Per-request timer | `packages/plugins/codex-collaboration/server/resolution_registry.py:238-242` |
| `assert_never` exhaustiveness guard (defensive idiom; Pyright marks "unreachable") | `packages/plugins/codex-collaboration/server/delegation_controller.py:942` |
| 6-row binding contract | `packages/plugins/codex-collaboration/server/delegation_controller.py:2779-2784` |
| T-07 plan with post-Candidate-A annotation | `docs/plans/2026-04-23-t07-cross-model-removal-7e.md` (callout block after defect 2) |
| T-01 ticket with Implementation update section | `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` |
| Diagnostic closure record | `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` |

### Patterns identified (refined this session)

- **Pure builder functions are policy-change-safe**: `build_workspace_write_sandbox_policy` has no Pydantic models, no serializers, no other tests pinning its output beyond the single `tests/test_runtime.py` regression. A one-line policy-flag flip propagates fully through a single edit. This pattern is worth recognizing as a quality marker — many policy-code surfaces have flags duplicated across types/schemas/validators/tests, requiring coordinated edits.
- **Python module-load env-var pattern**: read at import time via helper function; validate with fall-back-with-warning; document expectation that plugin restart is required for changes. Future env vars should follow this template.
- **Concern-isolated commits within a logical batch**: even when items are conceptually related (post-closure improvements), if they have different commit types (`docs` vs `feat` vs `docs`), separate commits preserve revertability and keep `git log --grep="^feat"` honest. Three commits + one push beats one bundled commit when types differ.
- **`R100` rename detection for archival moves**: `git rm <old> + git add <new>` for identical content yields `R100` in `--stat`, producing zero `+`/`-` diff lines. Right pattern for ticket-archive flows.
- **App Server enforcement is uniform across operation classes**: refutes the prior hypothesis that filesystem and network enforcement differed. Mid-shell-execution interruption at boundary-violating operations, NOT permission-error-returned-to-userspace. `cmd || handler` chain patterns can't catch sandbox denials.

### Surprising findings (this session)

- **Test imports use `from server.X` not `from codex_collaboration.server.X`**: I assumed Python-package-path imports based on the `codex-collaboration` plugin name; pyproject's `pythonpath = ["."]` makes `server` (the directory) the import root. Caught by first pytest run with `ModuleNotFoundError: No module named 'codex_collaboration'`. Fixed in 1 edit.
- **Pyright reports `case _: assert_never(...)` as "unreachable code"**: this is a defensive exhaustiveness idiom — Pyright correctly identifies it as type-system-unreachable, but the runtime guard exists for the case where a future contributor adds a union member without a `case` arm. Hint (★) not error (✘); pre-existing; not a quality issue.
- **The 1070-test count after env-tuning addition** (was 1063): suggests the test surface grows linearly with new helpers + edge-case coverage; targeted runs are fast (< 0.1s per file) but full suite is 250+ seconds — keep this in mind for CI feedback loops.
- **Plugin process structure has 3 levels** (Claude Code → uv wrapper → venv Python): the actual long-lived MCP server (PID 21509 in this session) is grandchild of Claude Code. Restarting just kills the chain via session exit.

## Context

### Project state (post-7-commit-arc)

| Item | State |
|---|---|
| Branch | `feature/delegate-execution-diagnostic-record` at `6a2bb5ae` (in sync with origin) |
| Closure record | `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` durable on origin (1458 lines, 58 fence pairs) |
| Candidate A patch | Live on disk + origin; `runtime.py:33` has `includePlatformDefaults: True` |
| Plugin in-memory state | PID 21509 still has the patched True flag loaded (from prior session-time edit); on-disk now matches in-memory; **divergence resolved** by this commit, not by restart |
| Env-tuning | `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS` available; default 900s; documented in plugin README |
| App Server interruption mechanism | Documented in `runtime.py` docstring (build_workspace_write_sandbox_policy) |
| T-07 plan reconciliation | Status callout added, defect descriptions preserved as historical |
| T-01 ticket | Open pending live `/delegate` smoke validation post-restart |
| Working tree | **Clean** (zero uncommitted changes) |
| Pushed to origin | All 7 commits pushed; HEAD == upstream |
| Recent commits (this session, oldest first) | `091d6120`, `d21c6284`, `f66f8b7c`, `ce0579f6`, `736fcf95`, `cd0f2142`, `6a2bb5ae` |
| Test suite | 1070/1070 codex-collaboration tests pass (was 1063 + 7 new env-config tests) |
| Pyright diagnostics | RT.1 (`runtime.py:289`, was `:282`) and `delegation_controller.py:942` "unreachable" — both pre-existing carry-forwards, line numbers shifted by edits |

### Mental model

**The branch's narrative arc is now fully shaped:**

1. **Diagnostic schema phase** (pre-session): Run record scaffolding, App Server schema bundle captured (`5a1e937e`).
2. **Diagnostic findings phase** (prior session): att1+att2+att3 + 3 security probes; closure record drafted.
3. **Closure landing + hygiene phase** (this session, commits 1-3): Reviewer fixes applied; closure committed; context-metrics fix and ticket archives also landed.
4. **Engineering action phase** (this session, commit 4): Candidate A sandbox policy promoted in production code.
5. **Carry-forward improvements phase** (this session, commits 5-7): T-07 plan reconciled, env-tuning landed, App Server enforcement mechanism documented in source.

**What remains (next-session operator action, not Claude-executable):**

6. **Live validation phase**: Plugin restart → live `/delegate` smoke against real repo-edit objective → T-01 ticket close (move to `closed-tickets/`).

**Why the divergence between code-changes-this-session and operator-action-next-session:**

- Code changes are repeatable, scriptable, deterministic
- Plugin restart loses session state (mitigated by handoff)
- Live smoke requires picking a real objective (operator-judgment-call)
- Ticket close requires verifying acceptance criteria pass empirically (operator-side review)

**Key insight that shaped this session's tempo:** Memory feedback `feedback_handle_commits.md` ("Handle commits proactively") + branch's per-concern commit discipline + user's consistent commit-and-push authorization patterns combined into a "land-as-you-go" working style. This session shipped 7 commits in ~7 user turns — each turn corresponding to a coherent, buildable chunk. The user's `/copy` adversarial review pattern provided quality gating between phases without adding turn overhead.

### Environment

- Working tree: `feature/delegate-execution-diagnostic-record` at `6a2bb5ae` (in sync with origin)
- Codex CLI: 0.125.0
- Local timezone: EDT (-0400)
- Plugin process structure: Claude Code (PID 21408) → uv wrapper (PID 21455) → venv Python MCP server (PID 21509) — long-lived, holding stale module table; **restart required before live smoke**
- Plugin data root: `~/.claude/plugins/data/codex-collaboration-inline/`
- Plugin's Claude session UUID: `fbb6621e-8e9d-4c02-8a3c-17776668a178` (this session)
- Model: `claude-opus-4-7[1m]` (1M context window — context-metrics fix this session covers this exact ID)
- macOS Darwin 25.4.0; shell zsh
- Test suite runtime: ~250s for full codex-collaboration package (1070 tests); ~0.02-0.10s for targeted single-file runs

## Learnings

### Single-line policy flips are propagation-safe when the policy builder is a pure function

**Mechanism:** `build_workspace_write_sandbox_policy` has no fan-out — no Pydantic models pinning the policy fields, no serializers re-asserting shape, no other tests beyond the single regression. Flipping one bool propagates through one edit.

**Evidence:** `grep -rn "includePlatformDefaults\b" packages/plugins/codex-collaboration/server/` returns only `runtime.py:33`. Production call sites (`delegation_controller.py:111, 1327`) pass-through; no flag-specific logic. Test sites (`test_runtime.py:9, 167, 171, 192`) — only the regression at L167 pins the flag value.

**Implication:** Future policy changes in this codebase can be small. Don't add abstraction layers (Pydantic models, schema validators) unless there's a concrete need — the pure-builder pattern keeps changes localized.

**Watch for:** Future code that introduces a Pydantic model wrapping the policy dict — that would multiply the change surface. Prefer extending the builder function over adding a typed wrapper unless the type system would prevent a real bug.

### Concern-isolated commits scale well; bundle only when commit types match

**Mechanism:** Each commit's diff is reviewable in isolation; `git log --oneline` reads as a coherent narrative; `git log --grep="^<type>"` queries return accurate filtered sets.

**Evidence:** This session's 7 commits each cover one concern (closure additions, model registry fix, ticket archive, sandbox patch, plan annotation, env-tuning, mechanism docs). The `git log --oneline` output is self-documenting:
```
6a2bb5ae docs(codex-collaboration): document App Server interruption mechanism in policy builder
cd0f2142 feat(codex-collaboration): env-tune approval-operator window via CODEX_COLLAB_*
736fcf95 docs(plans): annotate T-07 plan with post-Candidate-A-closure status
ce0579f6 feat(codex-collaboration): promote Candidate A sandbox policy (includePlatformDefaults: True)
f66f8b7c chore(tickets): archive 8 closed tickets to closed-tickets/
d21c6284 fix(context-metrics): detect claude-opus-4-7 1M context window
091d6120 docs(delegate): close Candidate A att1+att2+att3 + security probes 1+2+3
```

**Implication:** When a logical batch contains items with different commit types (`docs` / `feat` / `fix` / `chore`), separate commits. When items share a type AND scope (e.g., 3 doc edits to the same file area), bundling is fine. The commit-type-mismatch rule is the simplest heuristic.

**Watch for:** Tempting bundles where commit types differ. The "ship it together" instinct often misreads as "commit it together" — they're different.

### `R100` rename detection requires identical content + correct staging order

**Mechanism:** Git's rename detection runs at `--stat` / `--name-status` time, comparing source file content (recorded as deletion via `git rm`) against destination file content (recorded as addition via `git add`). 100% similarity = `R100` = single-line `--stat` output, zero diff lines.

**Evidence:** This session's `f66f8b7c` ticket archive: 8 files moved from `docs/tickets/` → `docs/tickets/closed-tickets/`. Verified content identity via `diff <(git show HEAD:...) <(...new path...)` on 3 spot-checked files. After staging (`git rm` + `git add` pairs), `git diff --cached --name-status -M` showed `R100` for all 8 entries.

**Implication:** For pure file relocations (no content edits), the rename-staged form gives a much cleaner diff than `git add -A` would. Use this pattern for archival flows, restructuring, and similar moves.

**Watch for:** Renames with even 1-line content edits drop below 100% similarity (e.g., R96, R85). If the operator wants `R100`, content edits must come in a separate commit.

### Python module-load env-var pattern: helper function + fall-back-with-warning

**Mechanism:** Read at module-load via helper function; validate (numeric parse, positive check); fall back to default with `logger.warning` on invalid. Plugin restart is the canonical path for tuning changes (matches Python `sys.modules` caching).

**Evidence:** `_read_approval_operator_window_seconds()` in `delegation_controller.py:120-156` (this session). 7 tests in `test_delegation_env_config.py` cover all branches in 0.02s.

**Implication:** Future plugin runtime tunables follow this template. Convention is now established for `CODEX_COLLAB_*` env vars.

**Watch for:** Tunables that need runtime mutation (vs module-load-only) need a different pattern (lazy property, Settings class). The current pattern matches the most common case (per-deployment tuning).

### Plugin restart for source code changes = full Claude Code restart

**Mechanism:** Python's `import` statement caches modules in `sys.modules`. Once `from .runtime import build_workspace_write_sandbox_policy` has run in the MCP server process, the function object is bound regardless of on-disk changes. There's no `importlib.reload` in the codex-collaboration server hot path. Process restart is the only deterministic way to load new module images.

**Evidence:** Memory `2026-04-28_23-30_...` says verbatim "restart plugin (Claude Code restart)". Docs (claude-code-docs MCP search): `/reload-plugins` is positioned as alternative to restarting Claude Code, but doc body specifically calls out enable/disable/install lifecycle (not source-code edits) — ambiguous on whether MCP server processes are respawned for source changes. Verifiable via PID check: `ps -ef | grep codex_runtime_bootstrap`.

**Implication:** Operator workflow for plugin changes: (1) edit source in repo, (2) save handoff if state matters, (3) `/exit`, (4) re-launch with same flags, (5) verify PID changed.

**Watch for:** Future Claude Code versions might add documented "reload Python source" support for `--plugin-dir` plugins. Re-check docs periodically.

## Next Steps

### 1. New session: `/handoff:load`

Picks up THIS handoff and archives it. Auto-resolves session continuity.

### 2. Plugin restart (operator action — not Claude-executable)

Required before live smoke validation. Path:
1. (Optional) `/handoff:save` first if there's session state worth preserving
2. `/exit`
3. Re-launch: `claude --plugin-dir packages/plugins/codex-collaboration --dangerously-skip-permissions`
4. Verify PID changed: `ps -ef | grep codex_runtime_bootstrap | grep -v grep` — expect different PID than 21509
5. (Optional) Verify on-disk policy is what's expected: `grep "includePlatformDefaults" packages/plugins/codex-collaboration/server/runtime.py` — expect `True`

### 3. Live `/delegate` smoke validation against a real repo-edit objective

The T-01 ticket's acceptance criteria require validation on a real (non-canonical) objective:
- [ ] Live `/delegate` runs at least one shell command needed for a simple repo edit
- [ ] `decide(approve)` grants the original App Server request via schema-valid `accept`
- [ ] Real objective produces non-empty `full.diff` and non-empty `changed_files`
- [ ] `poll` materializes reviewable artifacts with stable `artifact_hash`
- [ ] Final disposition: successful promotion OR typed/documented promotion rejection (not sandbox-execution-related)
- [ ] Regression tests cover sandbox policy serialization + approval decision response shape

The diagnostic empirically proved 4 of these (decide-approve grants, artifact materialization, hash stability, no approval-loop recurrence). Two remain TBD post-restart: live-shell-on-repo-edit, non-empty diff/changed_files.

**Optional: extend approval TTL for the live smoke** (per env-tuning landed `cd0f2142`):
```bash
export CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS=1800   # 30 min
claude --plugin-dir packages/plugins/codex-collaboration --dangerously-skip-permissions
```
Useful if anticipating adversarial-scrutiny review cycles on the smoke.

### 4. Close T-01 ticket once smoke passes

Move `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` → `docs/tickets/closed-tickets/`. Same `R100` rename pattern as `f66f8b7c`. Update ticket body with closing notes (acceptance criteria checked off, smoke evidence captured).

### 5. (Optional) Branch merge to main

After T-01 closes, the branch represents the full T-01 remediation arc + post-closure improvements. Either:
- Merge to main directly (single fast-forward, 7 linear commits)
- Open PR for review
- Squash if a flat single-commit landing is preferred

Branch's linear no-merge history makes the eventual `main` integration the cheapest possible operation.

### 6. (Optional) Carry-forward unchanged from prior session

| # | Item | Status |
|---|------|--------|
| 1 | Pre-existing Pyright RT.1 (`runtime.py:289`, was `:282`) | Surfaces on every runtime.py edit; not a regression signal |
| 2 | Pre-existing Pyright "unreachable" at `delegation_controller.py:942` (was `:902`) | Defensive `assert_never` exhaustiveness idiom; informational hint |
| 3 | Pre-existing flaky `test_delegate_decide_async_integration.py` worker-drain assertions | Did NOT trigger this session's 1070-test run |
| 4 | Optional follow-up on delegate's autopilot toward `.codex-collaboration/test-results.json` | Structural agent behavior; not a bug |

### 7. (Optional) Persist ELI5 codex-collaboration glossary

From an even earlier session: ~25 terms organized by Cast / Delegate flow / Decisions / TTL / Audit / Runtime-proof / Other. Could be distilled into `docs/references/codex-collaboration-glossary.md` for cross-session preservation.

## In Progress

**Clean stopping point at session boundary.** All session work is committed and pushed; working tree fully clean.

- Disk: 7 commits pushed to origin; HEAD `6a2bb5ae` matches upstream
- Plugin: in-memory PID 21509 still has the patched True flag loaded (from prior session-time edit) AND the on-disk source now permanently has it (this session's `ce0579f6`); divergence is consistent (both have `True`); restart will pick up the now-canonical source
- Working tree dirty across 0 concerns; nothing carried forward at the disk level
- T-01 ticket: open pending live smoke (operator-side action)

## Open Questions

- **Should `START_OUTCOME_WAIT_SECONDS` (delegation_controller.py:117) also be env-tunable?** Currently 30s; comment is "synchronous start-wait budget; not a wedge detector". User didn't request this. Decision: defer until empirical signal that 30s is too short/long for a real workflow.
- **Is `CODEX_COLLAB_*` the right env-var prefix?** No prior project pattern existed; this session established the convention. If a different prefix becomes preferred (e.g., shared tooling uses `CC_*`), renaming touches `delegation_controller.py`, test file, and README — minor migration.
- **Should the `_APPROVAL_OPERATOR_WINDOW_SECONDS_ENV` and `_APPROVAL_OPERATOR_WINDOW_SECONDS_DEFAULT` constants live in a separate `config.py` module?** Currently in `delegation_controller.py` near the constant they back. If future tunables proliferate, a `server/env_config.py` module might be cleaner. Defer until 2-3 tunables exist.
- **Does `/reload-plugins` actually respawn MCP server processes for `--plugin-dir` dev-loaded plugins?** Docs ambiguous. Could be tested empirically (run `/reload-plugins`, check if PID 21509 changed). Operator can verify when they do the live smoke restart.
- **Should the Pyright "unreachable" hint at `delegation_controller.py:942` be silenced?** Currently surfaces on every file edit. Could be silenced via `# type: ignore[unreachable]` comment at L943 (the `assert_never(outcome)` line). Trade-off: silences the hint but masks any future real unreachable-code introduction. Defer; pre-existing carry-forward.

## Risks

### Plugin restart loses Claude Code session state

**Concern:** The deterministic plugin-restart path (`/exit` + re-launch) terminates the entire Claude Code session, losing conversation context and any unsaved work.

**Mitigation:** Save handoff first via `/handoff:save`. Resume next session via `/handoff:load`. This handoff itself is the mitigation — future-Claude can pick up exactly where this session ended.

### Live smoke might surface unexpected sandbox-policy edge case

**Concern:** The diagnostic validated Candidate A on canonical workloads (smoke artifact byte-perfect) and 3 well-defined security probes (Network, Sensitive-path, Sibling-worktree). Real repo-edit objectives may exercise paths not covered by either — e.g., reading a project-internal config file outside the worktree, or invoking a tool with platform-default-but-unusual binary location.

**Mitigation:** If smoke fails at a specific path, follow the diagnostic flow: characterize the missing-path error → check Candidate B Matrix in run record → consider narrower `readableRoots` extension. The diagnostic infrastructure is already in place; another variant is feasible if needed.

### Pre-existing Pyright issues re-surface on every runtime.py / delegation_controller.py edit

**Concern:** RT.1 (`runtime.py:289`) and "unreachable" at `delegation_controller.py:942` are pre-existing carry-forwards. Every edit to those files re-runs Pyright and surfaces these as new diagnostics in the IDE, potentially misleading future-Claude into investigating non-issues.

**Mitigation:** This handoff documents both as carry-forwards with current line numbers. Memory `feedback_carry_forwards` (implicit pattern) preserves them across sessions. Optional: silence with `# type: ignore[...]` comments — tradeoff documented in Open Questions.

### Env-tuning could be misused if operator sets value too low

**Concern:** Setting `CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS=1` (or any tiny positive number) would pass validation but cause every approval to time out before the operator can decide.

**Mitigation:** Validation rejects ≤0 with warning; very small values are technically valid and would produce predictable failure (timeout cancels job — not destructive, just non-functional). README documents intended use case (extending TTL for diagnostic workflows). No real risk beyond operator-self-foot-shooting.

### T-07 plan annotation could become outdated if Candidate A is later replaced

**Concern:** The callout cites `ce0579f6` as the defect-1 fix. If Candidate A is ever superseded (e.g., by Candidate B or a different policy), the citation would point to a still-existent commit but no longer the canonical fix.

**Mitigation:** Annotation is a callout pointing to the diagnostic record, which would be updated alongside any policy change. Future cleanup would update the callout to cite the new commit. Low-frequency event; not blocking.

## References

### Files (this session's modifications)

- `docs/diagnostics/2026-04-28-delegate-execution-diagnostic.md` — closure additions + 5 reviewer fixes (`091d6120`)
- `packages/plugins/context-metrics/{config.py, test_config.py, README.md, CHANGELOG.md}` — Opus 4.7 1M-window detection (`d21c6284`)
- 8 ticket files: `docs/tickets/{2026-03-30-*, 2026-04-10-*}.md` → `docs/tickets/closed-tickets/` (`f66f8b7c`)
- `packages/plugins/codex-collaboration/server/runtime.py` — Candidate A patch + interruption-mechanism docstring (`ce0579f6` + `6a2bb5ae`)
- `packages/plugins/codex-collaboration/tests/test_runtime.py` — regression assertion update (`ce0579f6`)
- `docs/tickets/2026-04-23-codex-collaboration-delegate-execution-remediation.md` — Implementation update section (`ce0579f6`)
- `docs/plans/2026-04-23-t07-cross-model-removal-7e.md` — post-closure callout (`736fcf95`)
- `packages/plugins/codex-collaboration/server/delegation_controller.py` — env-tuning helper + import (`cd0f2142`)
- `packages/plugins/codex-collaboration/tests/test_delegation_env_config.py` (new) — 7 env-tuning tests (`cd0f2142`)
- `packages/plugins/codex-collaboration/README.md` — Configuration section (`cd0f2142`)

### Commits (this session, oldest to newest)

| Commit | Type/Scope | Description | Files | Lines |
|--------|---|---|---|---|
| `091d6120` | docs(delegate) | close Candidate A att1+att2+att3 + security probes 1+2+3 | 1 | +484/-16 |
| `d21c6284` | fix(context-metrics) | detect claude-opus-4-7 1M context window | 4 | +14/-1 |
| `f66f8b7c` | chore(tickets) | archive 8 closed tickets to closed-tickets/ | 8 (R100) | 0/0 |
| `ce0579f6` | feat(codex-collaboration) | promote Candidate A sandbox policy (includePlatformDefaults: True) | 3 | +29/-8 |
| `736fcf95` | docs(plans) | annotate T-07 plan with post-Candidate-A-closure status | 1 | +15 |
| `cd0f2142` | feat(codex-collaboration) | env-tune approval-operator window via CODEX_COLLAB_* | 4 (1 new) | +133/-1 |
| `6a2bb5ae` | docs(codex-collaboration) | document App Server interruption mechanism in policy builder | 1 | +20/-1 |

### Branches

- `feature/delegate-execution-diagnostic-record` at `6a2bb5ae` (in sync with origin)

### Test runs (this session)

| Run | Tests | Result | Time |
|---|---|---|---|
| `tests/test_runtime.py` (after Candidate A patch) | 11 | 11/11 pass | 0.01s |
| `tests/test_delegation_env_config.py` (new) | 7 | 7/7 pass | 0.02s |
| Targeted: env_config + delegation_controller + runtime | 119 | 119/119 pass | 208s |
| Full codex-collaboration suite (post-env-tuning) | 1070 | 1070/1070 pass | 254.66s |

### MCP tool calls this session

| Tool | Count | Purpose |
|------|-------|---------|
| `Skill: handoff:load` | 1 | Resume from prior handoff |
| `Skill: implementation-review` | 1 | Adversarial review of user's Candidate A patch |
| `Skill: handoff:save` | 1 | Save this handoff |
| `mcp__claude-code-docs__search_docs` | 2 | Plugin restart semantics + lifecycle |
| Bash | ~30 | Test runs, git operations, evidence gathering |
| Edit/Write | ~15 | Doc edits + new test file + commit message HEREDOCs |
| Read | ~10 | File context for edits + verification |

## Gotchas

### Test imports use `from server.X` not `from codex_collaboration.server.X`

`pyproject.toml` has `pythonpath = ["."]` and `testpaths = ["tests"]` — `server` (the directory) is the import root. Existing tests use `from server.runtime import ...` etc. New test files must follow this convention.

**Detection:** First pytest run with wrong import fails with `ModuleNotFoundError: No module named 'codex_collaboration'`.

**Fix:** Single import-line edit.

### Pyright reports `case _: assert_never(...)` as "unreachable code" — informational hint

This is the project's exhaustiveness idiom. Pyright correctly identifies it as type-system-unreachable; the runtime guard exists for the case where a future contributor adds a union member without an explicit `case` arm. Hint (★) not error (✘); pre-existing; not a quality issue. Do NOT investigate or attempt to fix.

### Plugin restart for source code changes = full Claude Code restart, not /reload-plugins

Python's `sys.modules` caches imports. `/reload-plugins` is documented for enable/disable/install lifecycle, not source-code edits. For source changes to take effect, the long-lived MCP server Python process must die and respawn — only deterministic via Claude Code session restart.

**Verification:** `ps -ef | grep codex_runtime_bootstrap | grep -v grep` — PID changed = restart succeeded.

### `/reload-plugins` may or may not respawn MCP server processes for source-only changes

Docs ambiguous. The `/reload-plugins` doc says "applies pending changes without restarting" but the body specifically calls out enable/disable/install lifecycle. Worth trying as cheaper alternative (it's free), but verify by checking PID changed before assuming success.

### Plugin in-memory state vs disk state can drift in dev mode

If you edit `runtime.py` mid-session (without committing), the disk has the new code but the running Python process at PID 21509 has the old. This session resolved a divergence: prior session edited `runtime.py` mid-run for the diagnostic patch (in-memory had `True`), then `git checkout`-ed to clean (on-disk had `False`); this session committed `True` to disk (on-disk now has `True`, matching in-memory). Plugin restart will pick up the canonical disk state.

### Carried gotchas (from prior sessions, still applicable)

- **`pgrep -fa <pattern>` matches its own argv** — use `ps -ef | grep ... | grep -v grep` instead.
- **macOS `date -u -j -f FMT INPUT +OUTFMT`** is the parsing trap; use epoch round-trip for parsing, `date -u +FORMAT` for emission.
- **`available_decisions` wire vs PendingRequestStore** — wire surface may be shorter (`[approve, deny]`) than store record (full 6-option list).
- **Pyright RT.1 (`runtime.py:289`, was `:282` before this session)** — pre-existing carry-forward; surfaces on every runtime.py edit; not a regression signal.
- **Approval TTL is graceful unblock-then-cancel** — jobs.jsonl shows park-cleared → running → canceled rather than direct cancel-from-parked.
- **`actor=system` audit events vs `actor=claude`** — filter by actor when reading audit trail.
- **`R100` rename detection requires identical content + correct staging order** — `git rm <old>` + `git add <new>` for byte-identical files.

## User Preferences

(Carried from prior sessions, applied this session — verbatim quotes where relevant.)

**Handle commits proactively (carried, applied 7 times this session).** Memory `feedback_handle_commits.md`: "User wants Claude to author + execute commits without asking; default to action when work reaches a coherent buildable chunk." Applied throughout — every commit landed without re-asking permission once the chunk was buildable.

**Adversarial review is the preferred quality gate before proceeding to next phase (carried, applied via /copy patterns and implementation-review skill invocation).** User routed reviewer findings via `/copy` for the run-record fixes; explicitly invoked review for the Candidate A implementation. The "review my work" + structured response pattern is the project pattern.

**Probe my recommendation for weaknesses before blindly accepting it (carried, applied this session).** Memory `feedback_handle_commits` and prior session captured this. Applied: when user described their Candidate A implementation, I ran adversarial passes (falsification + failure-modes) before declaring READY.

**Push at clean phase boundaries (carried, applied 2 times this session).** No push without authorization, but explicit `/copy` recommendations to push (Codex's verification reports) provide that authorization. Two pushes this session: after `091d6120` + `d21c6284` + `f66f8b7c`, and after `ce0579f6` + 3 carry-forward commits.

**"Awaiting your next X" closing line is the trigger (carried, applied this session).** Memory `feedback_copy_awaiting_means_act.md`. User pasted structured /copy reports ending with "My recommendation: push X next." — interpreted as authorization to push. Applied for the first push of `091d6120`.

**Per-concern commit isolation (project pattern, applied 7 times).** Each commit covers exactly one concern; types span `docs`, `fix`, `chore`, `feat` across the 7 commits — never bundled across types. Branch's linear history reflects this discipline.

**Concise commit messages mirroring the repo style (project pattern, applied).** Recent commits use `<type>(<scope>): <description>` with body explaining why before what. Matched throughout this session.

(New this session — verbatim user quotes:)

**Sequential scope expansion via "address X, then Y, then Z, then commit/push together":**
> "Address the T-07 plan annotation now. Then, I want to address two other items: 1. env-tunable `_APPROVAL_OPERATOR_WINDOW_SECONDS` 2. capture App Server interruption-mechanism finding in plugin source comments. Once all 3 of these are completed, they can be committed and pushed together"

User specifies a complete batch upfront with sequencing + commit-grouping intent. Apply: implement all items first, then surface for commit decision; group items by commit type discipline (3 separate commits when types differ).

**Implementation handoff with explicit review request:**
> "I promoted Candidate A's sandbox policy in [runtime.py]: ... Please review my work."

User implements the change directly and asks for review. Apply: invoke `implementation-review` skill; build Requirements Ledger; run falsification + failure-modes; verdict before commit. Don't bundle review with implementation when user has already implemented.

**"Move to the third commit (chore(tickets):) first and push them together":**

User's wording when wanting separate commits with one push. Distinguishes "third commit" (separate commit) from "push them together" (one push operation). The pattern: explicit-separate-then-one-push when items are unrelated.

**Sequential authorization "proceed with the commit (suggested message above)":**

User's pattern when consenting to a previously-suggested action. Apply: use the suggested commit message verbatim (or near-verbatim); don't deviate without flagging.

**Plugin operations (operator-side, not Claude-executable) are recognized as such:**
> "How do I restart the codex-collaboration plugin?"

User asks operational questions when an action is operator-side. Apply: provide step-by-step instructions, verification steps, and tradeoffs between options. Don't attempt to execute.

## Conversation Highlights

**User on commit grouping for the carry-forward batch:**
> "Once all 3 of these are completed, they can be committed and pushed together"

Ambiguous between 1 combined commit and 3 separate commits with 1 push. I chose 3 separate per branch's per-concern discipline; user did not push back.

**User on plugin restart procedure:**
> "How do I restart the codex-collaboration plugin?"

Asked at end of session, after all engineering work landed. Signals readiness to do the operator-side validation step.

**User on Candidate A implementation:**
> "I promoted Candidate A's sandbox policy in [runtime.py:23]: `build_workspace_write_sandbox_policy()` now emits `includePlatformDefaults: True` while preserving worktree-only roots, `networkAccess: False`, `excludeSlashTmp: True`, and `excludeTmpdirEnvVar: True`. Updated the policy regression in [test_runtime.py:167] to assert the promoted policy shape. Added a narrow implementation note to [2026-04-23-codex-collaboration-delegate-execution-remediation.md:93], keeping the ticket open pending post-restart live `/delegate` smoke. ... Please review my work."

User's structured "What changed / Where" + closing "Please review my work" mirrors my own reporting pattern. The "review my work" closing was the explicit review trigger.

**Codex /copy reviewer's pre-push verification:**
> "Verified. The three review findings are addressed in commit `091d6120`. ... My recommendation: push `091d6120` next."

Structured verification + recommendation. The "push X next" closing is the action trigger per memory `feedback_copy_awaiting_means_act.md`.

**Working style observed:** User progressively expands scope via clear instruction batches; uses /copy for adversarial scrutiny at quality gates; implements directly when changes are small/familiar (Candidate A patch); asks operational questions for operator-side actions (plugin restart). Communication is structured but compact — declarative "do X" rather than open-ended exploration.

**Communication pattern (carried + reinforced this session):** Reports use "What changed / Why / Verification / Remaining risks" structure (per global CLAUDE.md Response Contracts). User responds with structured analysis or directive instruction. The mutual structured-evidence pattern is durable across sessions.

## Rejected Approaches

### Recommending `/reload-plugins` as the primary plugin-restart path

**Approach:** When the user asked "How do I restart the codex-collaboration plugin?", consider recommending `/reload-plugins` as the cheap-first answer (with full restart as fallback).

**Why it seemed promising:** Docs say `/reload-plugins` "applies pending changes without restarting" — positions it as a lightweight alternative. User would prefer cheap.

**Specific failure (caught before applying):** Doc body specifically calls out enable/disable/install lifecycle, NOT source-code edits. If `/reload-plugins` doesn't actually respawn the long-lived MCP server process, operator runs it, sees the component-count summary, assumes success, runs live smoke against stale code — false-positive failure mode that's worse than the heavy-restart approach. Memory `2026-04-28_23-30_...` also explicitly says full Claude Code restart for prior validation.

**What it taught:** When recommending operations with ambiguous semantics, prefer the deterministic answer with verification path (PID check) over the cheaper alternative without one. Cheaper + verifiable = mention as alternative; cheaper + ambiguous = deprioritize.

### Bundling the 3 carry-forward items into a single combined commit

**Approach:** When user said "they can be committed and pushed together", consider one combined commit covering all 3 items.

**Why it seemed promising:** Literal reading of "committed... together" suggests singular commit. Simpler git operation.

**Specific failure (caught before applying):** The 3 items had different commit types (`docs(plans)`, `feat(codex-collaboration)`, `docs(codex-collaboration)`). A combined commit would have to use the most-significant type (`feat`), polluting `git log --grep="^feat"` queries with bundled docs. Branch's per-concern discipline established by 4 prior commits in this session.

**What it taught:** When commit types differ within a batch, separate. When commit types match AND scope matches, bundling is fine. The commit-type-mismatch heuristic is simpler than re-litigating "are these conceptually one concern or three?" each time.

### Using the existing test_delegation_controller.py for env-tuning tests

**Approach:** Add the 7 env-tuning tests to the existing 169KB `test_delegation_controller.py`.

**Why it seemed promising:** Tests for `_read_approval_operator_window_seconds` are tests for a private helper of `delegation_controller.py`; same module, same test file is conventional.

**Specific failure (caught by project pattern matching):** Other focused tests for delegation-related concerns each have their own file: `test_delegation_decision_result_shape.py`, `test_delegation_exceptions.py`, `test_delegation_job_parked_request_id.py`, `test_delegation_sanitization.py`. Pattern: `test_<area>_<focus>.py` for focused tests. Adding to the 169KB main file would dilute that pattern.

**What it taught:** Match the project's modularization granularity when introducing new test files. Focused-concern → focused file.

### Annotating the T-07 plan via top-of-file banner instead of section callout

**Approach:** Add a "Last updated" banner at the top of the T-07 plan file noting both root causes are now closed.

**Why it seemed promising:** First-line visibility for any reader.

**Specific failure (caught by reader-flow analysis):** A reader scrolling to a specific defect description would miss a top-of-file banner. The annotation needs to be near the historical content it's annotating. Section-level callout is the right granularity.

**What it taught:** For doc-rot prevention, place annotations as close to the rotting content as possible. Top-of-file is for status (e.g., "DRAFT", "DEPRECATED"); inline-callouts are for content-specific updates.

### Inlining the env-var read into the constant assignment

**Approach:** `_APPROVAL_OPERATOR_WINDOW_SECONDS: float = float(os.environ.get("CODEX_COLLAB_APPROVAL_OPERATOR_WINDOW_SECONDS") or 900)`.

**Why it seemed promising:** Single line; no helper function; minimal new abstraction.

**Specific failure (caught by testability requirement):** Validation logic (numeric parse, positive check, fall-back-with-warning) doesn't fit on one line. Even if it did, testing requires `importlib.reload` machinery — fragile and slow. Helper function is the standard Python pattern for testable env-var reads.

**What it taught:** Testability often dominates compactness for config-loading code. The 30-line helper + tests is structurally better than the 1-line inline read with no tests.
