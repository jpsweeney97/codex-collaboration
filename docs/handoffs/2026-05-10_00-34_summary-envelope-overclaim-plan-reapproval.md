---
date: 2026-05-10
time: "00:34"
created_at: "2026-05-10T04:34:43Z"
session_id: b243f43a-b970-4e46-bcce-88452b46de71
project: claude-code-tool-dev
branch: chore/codex-collab-envelope-diagnostic-overclaim-fix
commit: acda226a
title: "Summary: envelope overclaim plan reapproval after scrutiny"
type: summary
files:
  - docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md
  - docs/diagnostics/2026-05-01-codex-app-server-server-request-envelope-probes.md
  - docs/diagnostics/codex-app-server-server-request-envelope-probes.json
  - docs/plans/2026-05-01-codex-app-server-client-platform-rebaseline-implementation-plan.md
  - docs/plans/2026-05-01-codex-app-server-server-request-envelope-probe-plan.md
  - docs/status/codex-collaboration-reconciliation-register.md
  - docs/tickets/2026-04-29-codex-collaboration-delegation-friction-reduction.md
  - docs/tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md
  - packages/plugins/codex-collaboration/server/approval_router.py
  - packages/plugins/codex-collaboration/server/runtime.py
---

# Summary: envelope overclaim plan reapproval after scrutiny

## Goal

Complete a hard review cycle for the committed docs-only plan that fixes the May-1 App Server server-request envelope diagnostic overclaim.
The immediate target was `docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md`.
The larger purpose is to keep the current-client-platform rebaseline evidence honest before anyone executes parser or response-shape work.
The plan must reconcile diagnostic Markdown, sibling JSON, and the reconciliation register without changing raw envelope evidence.
The session stayed advisory/read-only until the user revised the plan and asked for reapproval.
End state: revised plan commit `acda226a` is approved for execution; the actual diagnostic/JSON/register edits have not run yet.

## Session Narrative

The session began with `[$scrutinize]` on the plan file at commit `04a7fb43`.
I used the scrutinize skill and reviewed the actual file, not the prior chat summary.
I also checked the live authority files: `approval_router.py`, the May-1 envelope diagnostic, the rebaseline plan, the T-01/T-02 tickets, and the reconciliation register.
The first scrutiny verdict was `Reject`.
The plan was solving the right problem, but three execution-level defects made it unsafe to run as written.

The first defect was a sweep collision with `T-20260429-02`.
The plan swept `docs/tickets/2026-04-29-codex-collaboration-*.md` while declaring T-20260429-02 method-by-method work out of scope.
The unsupported-server-request ticket still contained legacy "Supported as `<kind>`" / "Supported (parked)" route vocabulary.
Because the original sweep was also case-sensitive, it could miss capital-S matches while still catching lowercase acceptance-criterion wording.
The result was an unstable stop condition: a literal worker could stop before the plan reached its intended patch tasks.

The second defect was the register patch.
The plan appended landed-implementation language to the T-20260429-01 `Current truth` cell and updated the priority list.
It did not replace the same row's `Exit condition` cell.
That would leave the row saying Phase 1 had landed while still saying the exit condition was to land Phase 1.

The third defect was the JSON disposition.
The preferred supersession-note path left `local_compatibility: "supported"` and `supported_methods` untouched.
That was not real reconciliation for any `jq` consumer or future agent that reads the classification fields directly.
I also flagged three high-risk assumptions: the need to frame this as vocabulary succession, the imprecise fallback-tuple wording, and the missing git proof for "landed on `main`".

The user independently verified every claim against code and docs.
They agreed all six findings were valid.
They proposed the next step as revising the plan on the branch, then presenting the diff for reapproval.
I pre-decided the open dispositions so the repair would not be vague.
Those dispositions were: treat T-02 `Supported as <kind>` as legacy parser-route vocabulary, make sweeps case-insensitive, require git proof for `runtime.py` on `main`, enumerate the fallback tuple precisely, default JSON to patch-in-place unless a consumer honors `_superseded_by`, and replace the register exit-condition cell.

The user then landed follow-up commit `acda226a` on top of `04a7fb43`.
They reported a 217-insertion/66-deletion single-file diff to the plan.
I re-verified the actual commit, branch, working tree, and plan contents.
The revised plan now has a `Vocabulary Succession` section, `Sweep Classification Rules`, case-insensitive `rg` commands, JSON consumer discovery, git proof for `main`, precise fallback tuple wording, and a Task 4 step to replace the exit-condition cell.
I also ran the revised read-only smoke checks from the plan.
Consumer discovery surfaced only the JSON artifact itself, so patch-in-place is the expected JSON path.
`git diff main..HEAD -- runtime.py` was empty, and `git show main:runtime.py | sed -n '107,118p'` showed the carve-outs and dynamic gitdir logic.
Final verdict: approved to execute Tasks 1-6 from `acda226a`.

## Decisions

### Treat T-02 supported wording as legacy parser-route vocabulary

**Choice:** Keep T-20260429-02 out of scope and classify its `Supported as <kind>` / `Supported (parked)` wording as `legacy-parser-route-vocabulary`.
**Driver:** The ticket is using the May-1 probe-plan vocabulary where `supported` means route plus required fields, not response-shape compatibility.
**Alternatives:** Patch the T-02 ticket in this plan, or exclude the ticket from the sweep.
**Trade-off:** The sweep remains broad enough to catch real drift, but future workers must classify matches by context instead of string alone.

### Make overclaim sweeps case-insensitive

**Choice:** All overclaim-detection `rg` commands now use `-i`.
**Driver:** The live tickets contain capital-S `Supported` while the diagnostic uses lowercase `supported`.
**Alternatives:** Keep case-sensitive searches and rely on separate patterns.
**Trade-off:** More matches require classification, but the plan's new classification rules make that manageable.

### Default JSON reconciliation to patch-in-place

**Choice:** Patch JSON classification fields in place unless consumer discovery proves a production consumer honors `_superseded_by`.
**Driver:** Unknown consumers are exactly where stale machine-readable fields are dangerous.
**Alternatives:** Prefer supersession notes for unclear consumer status.
**Trade-off:** Patch-in-place expands the JSON vocabulary, but it prevents stale `supported_methods` from remaining the apparent truth.

### Require git proof before writing "landed on main"

**Choice:** Task 1.5b must prove the current branch has not changed `runtime.py` and that `main` contains the expected carve-outs.
**Driver:** Prior orientation failed by inverting branch-containment evidence; claims about `main` must be corroborated.
**Alternatives:** Trust the current branch file read because this branch only changes the plan.
**Trade-off:** Two cheap commands add friction but prevent a register assertion from becoming ungrounded.

### Own the register exit-condition cell

**Choice:** Task 4 now replaces the T-20260429-01 row's `Exit condition` cell, not just the `Current truth` cell and priority list.
**Driver:** The exit condition is what readers use to know what remains to close the item.
**Alternatives:** Append a note to `Current truth` only.
**Trade-off:** The table-row edit is more invasive, but it removes a direct contradiction.

## Changes

### `docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md`

The user revised this plan in commit `acda226a`.
The diff added the `Vocabulary Succession` section at line 44, grounding the old May-1 `supported` vocabulary against the stricter rebaseline vocabulary.
It added `Sweep Classification Rules` at line 140, including `legacy-parser-route-vocabulary` and a rule to prefer `interpretive-overclaim` for borderline matches.
It added consumer discovery in Step 1.4 and flipped the JSON default to patch-in-place.
It added Step 1.5b git proof for the `main` claim.
It rewrote the Task 2 fallback wording to enumerate `_AVAILABLE_DECISIONS[command_approval]`.
It updated Task 3 JSON patch instructions to mirror the precise fallback semantics.
It added Task 4.4 to replace the T-20260429-01 register row's exit-condition cell.
No diagnostic, JSON, register, or code files were edited in this session.

## Codebase Knowledge

`approval_router.py:103-111` is the authority for the lossy parser behavior.
`_resolve_available_decisions` preserves the wire list only when every entry is a string.
The observed May-1 command-approval envelope has a mixed list because `acceptWithExecpolicyAmendment` is structured.
The default command-approval tuple is `("accept", "acceptForSession", "acceptWithExecpolicyAmendment", "applyNetworkPolicyAmendment", "decline", "cancel")`.
Lossiness is bidirectional: the structured payload is collapsed to a bare string, and fallback adds decisions not offered by the wire.

The May-1 diagnostic still has the overclaims until the repaired plan executes.
Known Markdown sites are `local compatibility classification: supported`, "`availableDecisions` is also present and preserved", "observed supported methods", and "This packet proves compatibility".
Known JSON sites are `observed_server_requests[0].local_compatibility: "supported"` and `compatibility_classification.supported_methods`.
The plan's raw-evidence boundary still protects method string, params keys, redacted summary, trigger command, and "No approval response was sent."

The May-1 probe-plan vocabulary matters.
In `2026-05-01-codex-app-server-server-request-envelope-probe-plan.md:666-672`, `supported` meant route plus required correlation fields.
The rebaseline plan later split that into parser-kind compatibility and response-shape compatibility.
Future agents should not treat every old `supported` word as retroactively wrong; classify the context.

The T-20260429-01 register row is still stale until Task 4 runs.
The row currently says Phase 1 implementation is pending in the priority and exit-condition framing.
The repaired plan will narrowly update the priority line, `Current truth`, and `Exit condition` without bumping the register's global `Last reconciled` date.

`runtime.py` on `main` already contains the Phase 1 carve-outs.
The read roots at lines 107-118 include the worktree, `~/.codex/memories`, `~/.codex/plugins/cache`, `~/.agents/skills`, `~/.agents/plugins`, plus optional dynamic gitdir.
The branch `chore/codex-collab-envelope-diagnostic-overclaim-fix` does not modify `runtime.py`.

## Learnings

String sweeps need a classification contract when old and new vocabularies coexist.
The right fix was not "exclude T-02" or "patch everything with supported in it"; it was to define the legacy parser-route boundary.

Supersession markers are not consumer behavior.
If a JSON consumer reads stale fields directly, a top-level note does not protect it.
Unknown consumer status should bias toward changing the stale fields, not preserving them.

Register rows have multiple truth-bearing cells.
Updating a narrative `Current truth` cell while leaving an old `Exit condition` can make the table more contradictory than before.

The fallback tuple detail matters.
The old shorthand "live offered cancel, fallback includes decline" was incomplete because `cancel` is still preserved.
The precise issue is structured payload loss plus added decisions.

## Next Steps

Execute Tasks 1-6 from `docs/plans/2026-05-09-codex-collaboration-envelope-diagnostic-overclaim-fix.md` at commit `acda226a`.
Do not re-open the plan-review loop unless a task stop condition fires.
Expected JSON path is patch-in-place because consumer discovery currently finds no production consumer outside the JSON artifact.
Expected register path is to update priority, current-truth, and exit-condition cells for T-20260429-01.
After execution, commit the diagnostic/JSON/register changes with the plan's Task 6 commit message, adjusted only if actual conditional paths differ.
Do not treat the repaired plan approval as proof that T-20260429-01 is closed; AC #1-#3 evidence remains missing.
Do not use this docs-only plan to implement parser/response semantics or T-20260429-02 method classification.

## Project Arc

The codex-collaboration project is in a post-Packet-1, post-drift-cleanup state.
Packet 1 deferred-approval response work landed earlier, and D-01 through D-09 cleanup completed.
Roadmap Step 0 and Step 1 completed before the Step 2 sandbox-carve-out work.
Step 2 implementation landed on `main` via PR #127, including subdirectory carve-outs and hardened dynamic gitdir validation.
What remains for T-20260429-01 is closure evidence: comparable `/delegate` smoke, credential-boundary probe, regression assertion update, and suite pass.

The May-1 current-client-platform rebaseline widened the project beyond the original 0.128 permission branch.
It produced exploration, scratch-home, materialized-thread, server-request-envelope, architecture, and implementation-plan artifacts.
The live envelope evidence is valuable but narrow: one `item/commandExecution/requestApproval` envelope was captured.
That envelope proves parser-kind compatibility only.
Response-shape compatibility remains unproven because the mixed `availableDecisions` list is not preserved losslessly.

The current branch contains only plan commits.
`04a7fb43` added the first overclaim-fix plan.
`acda226a` repaired that plan after scrutiny and is now approved for execution.
The working tree was clean at reapproval time.

The main drift risk is status flattening.
Do not say "Step 2 green" when implementation has landed but closure evidence is missing.
Do not say command approval is fully supported when only parser-kind compatibility is established.
Do not treat T-20260429-02 parser-route vocabulary as a response-shape overclaim unless the surrounding text claims lossless preservation, closability, or full response compatibility.

Once the repaired plan executes, the next active work should return to evidence collection and runtime proof.
That likely means T-20260429-01 closure first, then T-20260429-02 method matrix and any lossless parser/response branch.
The public-skills-repo workstream is separate and should not distort codex-collaboration status.
