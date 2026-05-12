# System Design Review - F4 audit retention design post-amendment review

**Date:** 2026-05-12
**Target:** `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md`
**Reviewed commits:** `47533f3` (review), `5117792` (amendments)
**Scope level:** `subsystem`
**Input type:** updated design doc + amendment diff
**Archetypes:** Data pipeline / ETL (medium-high confidence) + internal tool / back-office (medium confidence)
**Stakes:** high

## 1. Review Snapshot

| Signal | Count |
| ------ | ----- |
| High-priority findings | 2 |
| Total findings | 3 |
| Tensions identified | 1 |
| Categories screened only | 3 |
| Insufficient evidence | 0 |

## 2. Focus and Coverage

This fresh pass verifies the landed amendment commit before re-reviewing the current design. The change summary is accurate: `47533f3` adds the previous review artifact, and `5117792` changes only `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md` by tightening §2 Contract, adding one §5.2 mixed-prune paragraph, and adding §6.5 Operating envelope.

The first-order closure matrix is materially correct: prior findings F1-F7 are addressed as conscious decisions. This post-amendment review therefore focuses on second-order architecture issues introduced or exposed by the tightened contract.

Deep lenses: Correctness, Consistency Model, Failure Containment, Source of Truth, Observability, Boundary Definition, Legibility.

| Category | Status | Sentinel, anchor, disposition |
| --- | --- | --- |
| Structural | screened | Components and boundaries remain nameable: `OperationJournal`, bootstrap, JSONL files, prune helpers, seen-sets, and owner spec updates are explicit. |
| Behavioral | deep | The runtime path is traceable, but the mixed-prune fallback now overclaims append correctness for already-initialized journals. |
| Data | deep | Data lifecycle is much clearer after the amendments, but owner-spec propagation is incomplete. |
| Reliability | deep | Per-file atomicity is now a conscious decision; initialized-state failure containment is still underspecified. |
| Change | screened | Deferred F12/F18/F19 boundaries are still explicit, and §6.5 names refactor triggers for out-of-envelope deployments. |
| Cognitive | deep | The amended design is mostly legible; the remaining risk is divergence between the design contract and owner-doc update plan. |
| Trust and Safety | screened | Retain-on-uncertainty now owns the evidence-vs-minimization tradeoff; no new trust-boundary finding at this depth. |
| Operational | deep | Observability language now depends on a Python logging premise that is not correct for `WARNING` records under the default runtime. |

## 3. Findings

### F1. Mixed-prune fallback is only correct when the journal was not already initialized

- **Lens:** Correctness + Failure Containment
- **Decision state:** underspecified
- **Anchor:** §2 says append correctness is preserved in a mixed-prune state because `_ensure_seen_sets_loaded()` reads disk as source of truth. §5.2 repeats that after an `outcomes.jsonl` failure, the next `append_*_once` consults `_ensure_seen_sets_loaded()`. §5.6 says failed prune leaves seen-set state exactly as it was, and §5.7 shows `_ensure_seen_sets_loaded()` returns immediately when `_seen_sets_initialized` is already true.
- **Problem:** The amended mixed-prune story is valid for the bootstrap-first path where `_seen_sets_initialized` starts false. It is not valid for a journal whose seen-sets were already initialized before a re-runnable prune. In that case, a partial prune can rewrite `events.jsonl`, fail before assignment, leave `_seen_sets_initialized == True`, and cause later append-once calls to use stale pre-prune sets rather than reloading from disk.
- **Impact:** The design can over-dedup after partial failure: a key for a record just pruned from disk may remain in memory and cause a later append to be skipped. That contradicts the amended claim that append correctness is preserved across mixed state.
- **Recommendation or question:** Either constrain `prune_audit_logs()` architecturally to bootstrap-before-initialization and remove the general re-runnable safety claim, or specify an invalidation rule: once any canonical file may have been replaced during prune, any later failure marks seen-sets uninitialized before propagating. The latter keeps the current re-runnable contract.

### F2. The default logging claim is wrong for warnings

- **Lens:** Observability + Boundary Definition
- **Decision state:** explicit decision with incorrect premise
- **Anchor:** §2 and §6.1 state that `logger.warning(..., exc_info=True)` is discarded by Python's default logging configuration until F18 lands `logging.basicConfig`.
- **Problem:** Under default Python logging, a named logger's `warning` record propagates to the default `logging.lastResort` stderr handler when no root handlers are configured. A quick runtime check confirms `logger.warning("warn-message")` emits, while `logger.info("info-message")` does not. The current design is correct for `info`, but not for `warning`.
- **Impact:** The contract now encodes an observability model that is stricter than the runtime. That can lead the implementation plan or tests to assert the wrong behavior, and it makes F18 appear necessary for any warning visibility when it is really needed for consistent configuration/formatting and info-level summary visibility.
- **Recommendation or question:** Amend the language to distinguish levels: by Python default, warnings may reach stderr via `lastResort`; info summaries are discarded without configured logging. If the MCP host suppresses stderr, name that host-level behavior rather than attributing suppression to Python logging.

### F3. The owner-spec update plan does not carry the amended contract

- **Lens:** Source of Truth + Legibility
- **Decision state:** underspecified
- **Anchor:** §2 now owns important contract decisions: outcomes are operational diagnostics, malformed/timestamp-uncertain records are TTL-exempt, atomicity is per file, `plugin_data_path` is single-writer, and prune warning visibility is conditional. §7's proposed `recovery-and-journal.md` changes still update only the short retention row, the retention subsection, and the defaults table.
- **Problem:** The design document is clearer than the proposed owner-spec patch. In this repo, `docs/specs/recovery-and-journal.md` owns journal/audit behavior. If implementation follows §7 as written, future readers of the owner spec will miss several contract constraints that exist only in the design artifact.
- **Impact:** The repo can drift immediately after implementation: the design says one thing, while the owner doc that later readers trust says less. The highest-risk omissions are TTL-exempt malformed records, per-file-not-pairwise atomicity, and single-writer ownership.
- **Recommendation or question:** Expand §7 so the owner spec receives the same durable contract shape, or explicitly add a follow-up owner-doc amendment before implementation closeout. Prefer updating §7 now; otherwise the design is asking the implementation plan to preserve facts that the authority layer will not.

## 4. Tension Map

### T1. Contract tightening vs authority propagation

- **Tension:** The amendment deliberately kept scope to contract-tightening, but the tightened contract now exceeds the planned owner-spec edits.
- **What is being traded:** Fast design-doc amendment closure versus preserving the repo's authority model after implementation.
- **Why it hid:** §2 reads complete in isolation, and §7 looks like routine spec-edit plumbing; the gap only appears when the design is read against the repo's authority map.
- **Likely failure story:** F4 lands correctly in code, but `recovery-and-journal.md` only says "30-day TTL at startup"; a later maintainer changes retention or concurrency assumptions without seeing the TTL-exempt and single-writer constraints.
- **Linked findings:** F3

## 5. Questions / Next Probes

1. Should `prune_audit_logs()` remain generally re-runnable after seen-sets are initialized, or is it only a bootstrap-before-use operation?
2. Is warning visibility meant to be governed by Python defaults, MCP host stderr capture, or a future F18 logging policy?
3. Should §7 be patched now so `recovery-and-journal.md` receives the amended contract, including TTL exemptions, per-file atomicity, and single-writer ownership?
