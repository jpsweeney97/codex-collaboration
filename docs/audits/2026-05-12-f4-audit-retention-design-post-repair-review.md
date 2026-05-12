# System Design Review - F4 audit retention design post-repair review

**Date:** 2026-05-12
**Target:** `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md`
**Reviewed commits:** `20a7689` (post-amendment review), `10e32ce` (repair)
**Scope level:** `subsystem`
**Input type:** updated design doc + repair diff
**Archetypes:** Data pipeline / ETL (medium-high confidence) + internal tool / back-office (medium confidence)
**Stakes:** high

## 1. Review Snapshot

| Signal | Count |
| ------ | ----- |
| High-priority findings | 1 |
| Total findings | 1 |
| Tensions identified | 0 |
| Categories screened only | 5 |
| Insufficient evidence | 0 |

## 2. Focus and Coverage

This fresh pass verifies the repair commit before re-reviewing the current design. The change summary is accurate: `20a7689` adds the previous post-amendment review artifact, and `10e32ce` changes only `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md` by repairing the mixed-prune flag invariant, correcting warning-vs-info logging visibility, and expanding the owner-spec update plan.

The prior post-amendment findings are substantially closed:

- PA-F1 is repaired by invalidating `_seen_sets_initialized` before any disk mutation and restoring it only after the successful set reassignment block.
- PA-F2 is repaired by distinguishing warning-level `lastResort` stderr visibility from discarded info-level success summaries.
- PA-F3 is repaired by expanding the proposed `recovery-and-journal.md` retention text with outcome data class, TTL-exempt malformed records, per-file atomicity, and single-writer ownership.

Deep lenses: Correctness, Consistency Model, Failure Containment, Legibility.

| Category | Status | Sentinel, anchor, disposition |
| --- | --- | --- |
| Structural | screened | Components and boundaries remain stable: `OperationJournal`, JSONL files, prune helpers, bootstrap, owner spec, and tests are explicit. |
| Behavioral | deep | Runtime path and failure behavior are mostly clear, but §6.3 still contains one stale success-only rewrite statement. |
| Data | screened | Data lifecycle is traceable from raw line to retention decision, rewrite, dedup population, and owner-spec propagation. |
| Reliability | deep | Per-file atomicity and mixed-prune fallback are explicit; one lifecycle summary still blurs failure behavior. |
| Change | screened | F12/F18/F19 remain deferred cleanly; the operating envelope and refactor triggers are named. |
| Cognitive | deep | The design is legible overall, with one local contradiction likely to mislead implementers. |
| Trust and Safety | screened | Retain-on-uncertainty, TTL exemption, and warning visibility are explicit enough at this scope. |
| Operational | screened | Bootstrap warning visibility and info-summary limitations are now accurately described. |

## 3. Findings

### F1. §6.3 still says rewritten files are written only on success

- **Lens:** Correctness + Legibility
- **Decision state:** explicit decision with stale contradictory wording
- **Anchor:** §2 and §5.2 now define per-file atomicity and pair-level partial success: `events.jsonl` may be rewritten even if `outcomes.jsonl` later fails. §5.6 explains that the flag-clear-at-entry discipline preserves append correctness after that partial failure. §6.3 still summarizes each prune invocation as writing rewritten files only on success.
- **Problem:** The §6.3 lifecycle summary has not been updated to match the repaired contract. In the accepted model, the set reassignment is all-or-nothing, but file rewrites are not all-or-nothing at the `prune_audit_logs()` call level.
- **Impact:** An implementation plan could inherit the stale §6.3 sentence and write tests or prose assuming no file is rewritten on overall prune failure. That would conflict with the named per-file atomicity model.
- **Recommendation or question:** Patch §6.3 to separate the two guarantees. For example: "Rebuilds local seen-sets from scratch; reassigns seen-sets only after both files complete; each file rewrite is atomic per file, so a failed later file can leave an earlier file already rewritten."

## 4. Tension Map

No material cross-cutting tensions remain at this review depth. The prior tensions have been converted into explicit tradeoffs or owner-spec text; the remaining issue is local stale wording, not a new architectural tension.

## 5. Questions / Next Probes

1. Should §6.3 be patched before writing the implementation plan, so the plan does not inherit the stale all-or-nothing wording?
2. After that wording fix, is the design ready to move to `writing-plans`, with implementation readiness handled by the planning workflow rather than another architecture review?
