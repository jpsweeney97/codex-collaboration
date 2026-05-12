# Adversarial Review - F4 audit retention design round-4

**Date:** 2026-05-12
**Target:** `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md`
**Reviewed commit:** `539f55a` (round-3 repair — the converged state)
**Scope level:** `subsystem`
**Input type:** adversarial review of converged design
**Methodology:** adversarial pass (distinct from prior rounds' `system-design-review`)
**Archetypes:** Data pipeline / ETL + internal tool / back-office
**Stakes:** high

## 1. Review Snapshot

| Signal | Count |
| ------ | ----- |
| High-severity findings | 1 |
| Moderate-severity findings | 2 |
| Low-severity findings | 2 |
| Editorial notes | 1 |
| Findings confirmed against design+code | 5 |
| Findings carrying novel content beyond §2 / §6.5 | 4 |

## 2. Methodology Note

The prior session's D5 — "three-pass review depth, not four" — bet on diminishing returns within the `system-design-review` category set. This pass falsifies that bet by applying an **adversarial** lens (assumptions audit + pre-mortem + dimensional critique) instead. The substrate-vs-surface question — *does the API's per-domain shape match the implementation's coupling?* — wasn't asked in rounds 1–3 and surfaced a HIGH-severity contract issue.

Diminishing returns is **category-specific, not absolute**. Switching review lenses re-surfaces signal. Future Bucket 2b/2c slices should plan for at least one adversarial pass in addition to the category-driven `system-design-review` rounds.

## 3. Adversarial Findings

### F1. Shared `_ensure_seen_sets_loaded()` creates cross-file append failure coupling

- **Lens:** Substrate-vs-surface (API shape vs. internal coupling) + Failure Containment
- **Severity:** HIGH
- **Decision state:** explicit but mis-specified intent
- **Anchor:** §5.7 `_ensure_seen_sets_loaded` populates both files unconditionally; the inline comment on the `_populate_seen_from_file` block states "If either population raises, exception propagates and the seen-set state stays as it was. `append_*_once` will then surface the IO error rather than silently appending a possibly-duplicate record."
- **Problem:** The current `append_dialogue_audit_event_once` ([`server/journal.py` line 297](../../server/journal.py)) consults only `_audit_path`. The design changes this to a journal-wide load: any unreadable file blocks every append-once method. The API surface is per-domain (audit / dialogue-outcomes / delegation-outcomes), but the substrate is journal-wide. The §5.7 rationale ("rather than silently appending a possibly-duplicate record") only applies to *that domain's* file — appending an audit event has no logical dependency on outcomes' seen-set freshness.
- **Impact:** Behavioral regression vs. current code. A file-specific permission error, inode corruption, or transient IO failure in `outcomes.jsonl` now also blocks audit appends. More importantly, the substrate-vs-surface mismatch is a maintenance hazard regardless of failure frequency: future contributors adding new append-once methods would inherit cross-file coupling implicitly.
- **Verification against code:** confirmed. Current `_jsonl_contains` is called with one `path` per append-once site (`server/journal.py` 297/317/337). Design §5.7 lines 423–432 call `_populate_seen_from_file` for both files.
- **Resolution chosen:** **Path A — split seen-set initialization by source file.** Replace the single `_seen_sets_initialized` flag with two: `_audit_seen_initialized` (covers `events.jsonl` → `_audit_seen`) and `_outcomes_seen_initialized` (covers `outcomes.jsonl` → both `_dialogue_outcomes_seen` and `_delegation_outcomes_seen`). Each `append_*_once` triggers only its own file's load. `prune_audit_logs` clears both flags at entry and restores each only after the relevant file's seen-set is reassigned.
- **Granularity note:** the user's instruction said "split by domain: audit, dialogue outcomes, delegation outcomes" — three domains. The design adopts **two flags per source file** rather than three flags per domain because dialogue and delegation outcomes share `outcomes.jsonl`'s fate by construction (same file, same single-writer). Three flags would force two reads of the same file in steady state for no isolation benefit. The substantive isolation property the user demanded — *audit must not share fate with outcomes* — holds at two flags. The adversarial reviewer's own "stronger alternative" in §3 of their report described two-flag per-file decoupling.

### F2. Byte-for-byte retention contract contradicts the algorithm

- **Lens:** Correctness + Contract Specification
- **Severity:** MODERATE
- **Decision state:** contract claim contradicts algorithm
- **Anchor:** §2 Contract says "retained records are written back as their original raw lines, byte-for-byte, never re-serialized." §5.2 algorithm assigns `line_to_keep = raw_line if raw_line.endswith("\n") else raw_line + "\n"` — appending `\n` to a final line lacking one.
- **Problem:** A retained final JSONL record with no trailing newline is rewritten with one. The contract says "byte-for-byte"; the algorithm normalizes EOF newlines.
- **Verification against design:** confirmed. §5.2 line containing `raw_line + "\n"` is explicit; §2 wording is unqualified.
- **Resolution chosen:** **Loosen the contract, not the algorithm.** Truly byte-for-byte rewrite of a missing-EOF-newline file would leave the next `append_*` call concatenating onto the last record, breaking JSONL parseability. The algorithm's normalization is load-bearing for JSONL append-safety. Reword §2 to: *"Pruning is a pure filter: retained record bytes are preserved, with a single `\n` appended to the final retained line if absent, to keep the file JSONL-append-safe. Records are never re-serialized through `json.dumps`."* §8.3 test name should follow suit.

### F3. Malformed TTL-exempt records can grow without operator-visible signal

- **Lens:** Operational Honesty + Observability
- **Severity:** MODERATE
- **Decision state:** named in §2 / §6.5, but mitigation deferred to F18 by default
- **Anchor:** §2 line 27 ("can survive past the 30-day window indefinitely") + §6.5 ("operator visibility into envelope adherence rides F18").
- **Problem:** The blind spot is already documented, but the design's default behavior leaves nonzero `retained_malformed` counts entirely silent before F18. A 30-day-TTL claim becomes conditional on records being well-formed; corrupt records accumulate forever without any operator signal.
- **Verification against design:** confirmed. The summary `logger.info(...)` call in §6.1 is below `logging.lastResort`'s WARNING threshold and discarded by default Python logging.
- **Resolution chosen:** **Promote the summary log to `WARNING` when any malformed counts are nonzero.** Change §6.1's bootstrap call site to split: if `summary.audit_retained_malformed > 0 or summary.outcomes_retained_malformed > 0`, log at `WARNING` level (visible via `lastResort` to stderr); else log at `INFO` (discarded by default, surfaced via F18 later). This delivers a default-visible operator signal before F18 lands at zero substrate cost. §2 Contract needs a one-sentence update acknowledging the visibility split.

### F4. Bootstrap test placement contradicts repo structure

- **Lens:** Procedural / Conformance
- **Severity:** LOW
- **Decision state:** §8 wording inconsistent with existing test module layout
- **Anchor:** §8 line 589 says "All tests in `tests/test_journal.py`." §8.9 lists `test_bootstrap_logs_prune_summary_when_prune_succeeds` and `test_bootstrap_warns_when_prune_raises_oserror`.
- **Problem:** `tests/test_bootstrap.py` already exists (312 lines, importlib-based loader for the bootstrap script as a non-package module). Bootstrap-integration tests semantically belong there. Following §8 as written would steer implementation into the wrong file.
- **Verification against repo:** confirmed. `tests/test_bootstrap.py` present with established conventions for importing `scripts/codex_runtime_bootstrap.py`.
- **Resolution chosen:** §8 preamble qualified: "All tests in `tests/test_journal.py` **except §8.9 bootstrap integration tests, which live in `tests/test_bootstrap.py` and use its existing importlib-based loader pattern.**"

### F5. Invalid UTF-8 behavior is unspecified

- **Lens:** Completeness + Failure Containment
- **Severity:** LOW
- **Decision state:** missing decision
- **Anchor:** §5.2 uses `path.open(encoding="utf-8")` — default `errors="strict"`. Invalid UTF-8 raises `UnicodeDecodeError` mid-pass.
- **Problem:** `UnicodeDecodeError` is not an `OSError`, so the bootstrap's `try/except OSError` does **not** catch it. Today, an invalid-UTF-8 byte sequence in either file would surface as a bootstrap-failing exception. The design says nothing about this.
- **Verification against design:** confirmed.
- **Resolution chosen:** **Treat invalid UTF-8 as file-level corruption; fatal-to-this-pass; caught at bootstrap.**
  - File format is UTF-8 by construction (`append_audit_event` always writes `encoding="utf-8"`). Invalid UTF-8 = corruption of an invariant the file format owns.
  - §5.2 adds an explicit stance: invalid UTF-8 aborts the pass (no retain-on-uncertainty for byte-level corruption — the granularity of "retain-on-uncertainty" is one JSONL record, not one byte).
  - §6.1's bootstrap catch broadens to `except (OSError, UnicodeDecodeError)` — and **only** these two. `json.JSONDecodeError` remains line-local retained data (§5.2 retain-on-uncertainty table). Programming errors (`ValueError` from naive clocks, `AttributeError`, etc.) still fail fast. The catch list is precise, not "anything parse-like."

## 4. Editorial: Owner-spec patch doesn't position outcomes at architecture level

- **Lens:** Source of Truth / Spec Architecture
- **Severity:** EDITORIAL (not elevated to a numbered finding)
- **Anchor:** `docs/specs/recovery-and-journal.md` §Two-Log Architecture (line 12) describes Operation Journal vs. Audit Log. Design §7 patches the Audit Log column's Retention row and adds outcomes-aware text under §Audit Log → Retention. Outcomes (`analytics/outcomes.jsonl`) appears in the spec only as a child of Audit Log retention text — structurally awkward because outcomes is a peer file, not a subordinate of Audit Log.
- **Problem:** A later reader of the owner spec encounters outcomes only via the retention subsection's bullet; the architecture overview at the top names only two logs.
- **Resolution chosen:** Design §7 adds a small new subsection ("Operational Outcomes") after "Why Two Logs" describing `analytics/outcomes.jsonl` as a peer file sharing the Audit Log's retention class but with a distinct format (`OutcomeRecord` / `DelegationOutcomeRecord`) and purpose (terminal-state diagnostics). The "Two-Log Architecture" title and table are unchanged — outcomes is a sibling of Audit Log in retention behavior, not a third equally-distinct log.

## 5. Severity Summary and Resolution Table

| ID | Severity | Finding | Resolution | Sections Touched |
| --- | --- | --- | --- | --- |
| F1 | HIGH | Cross-file append failure coupling | Path A: two-flag per-source-file decouple | §2, §4, §5.2, §5.6, §5.7, §5.8, §6.3, §8.6 |
| F2 | MODERATE | Byte-for-byte vs. JSONL append-safety | Loosen contract; algorithm unchanged | §2, §8.3 |
| F3 | MODERATE | Silent malformed accumulation | `WARNING` when nonzero retained_malformed | §2, §6.1 |
| F4 | LOW | Bootstrap test placement | §8 wording qualification | §8 preamble, §8.9 |
| F5 | LOW | Invalid UTF-8 unspecified | Fatal-to-pass; bootstrap catches `UnicodeDecodeError` | §5.2, §6.1 |
| E1 | editorial | Outcomes not at architecture level in owner spec | Add "Operational Outcomes" subsection in §7 patch | §7 |

## 6. Convergence Trajectory

| Round | Methodology | Findings | High-severity | Medium-severity | Low-severity |
| --- | --- | --- | --- | --- | --- |
| 1 | system-design-review on `a94c05f` | 7 | 4 | 3 | 0 |
| 2 | system-design-review on `5117792` | 3 | 2 | 1 | 0 |
| 3 | system-design-review on `10e32ce` | 1 | 0 | 1 | 0 |
| 4 | **adversarial review on `539f55a`** | 5 | 1 | 2 | 2 |

The round-4 finding count is higher than round 3 because the lens changed. Within the `system-design-review` category set, convergence at round 3 was real. Round 4 applies a different review surface (adversarial / substrate-vs-surface / pre-mortem) and re-surfaces signal that no `system-design-review` pass would have produced. **Convergence is per-methodology, not absolute.**

## 7. Confidence

**Going in:** 3 (the prior session's converged claim was structurally credible but lens-limited).
**Going out:** 4 after the chosen amendments land. F1's two-flag decoupling resolves the structural concern that prevented confidence-4 from the adversarial reviewer; F2/F3/F4/F5 are tightening and explicit-decision work.

The design will be ready for `superpowers:writing-plans` after the round-4 amendments are committed.

## 8. Next Probes (Deferred to Implementation Plan)

1. The two-flag per-file decoupling needs a test pinning that an unreadable `outcomes.jsonl` blocks outcomes-append-once but NOT audit-append-once. This is a new §8.6 entry: `test_unreadable_outcomes_does_not_block_audit_append_once`.
2. F5's invalid-UTF-8 stance needs a regression test (synthetic invalid-byte file). This is a new §8.2 entry or §8.4 entry depending on how the test is shaped — leave to writing-plans.
3. The §7 architecture-level subsection for outcomes is a spec patch, not a design-doc change. Implementation must apply it as a substep of the spec update.
