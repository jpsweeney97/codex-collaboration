# Adversarial Review - F4 audit retention design round-5

**Date:** 2026-05-12
**Target:** `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md`
**Reviewed commits:** `fbb17da` (round-4 audit), `92a52fb` (round-4 amendments)
**Scope level:** `subsystem`
**Input type:** second adversarial pass over amended design
**Methodology:** adversarial (same lens as round-4, applied to the amended doc)
**Archetypes:** Data pipeline / ETL + internal tool / back-office
**Stakes:** high

## 1. Review Snapshot

| Signal | Count |
| ------ | ----- |
| High-severity findings | 0 |
| Moderate-severity findings | 1 |
| Low-severity findings | 2 |
| Editorial notes | 0 |
| Findings confirmed against design+code | 3 |
| Findings carrying structural concerns | 0 |

## 2. Methodology Note

A second adversarial pass on the round-4 amended doc. Round-4 resolved F1's structural blocker (cross-file append coupling) plus four precision findings (F2-F5 + editorial). This round verifies the amendments landed cleanly **and** stress-tests the remaining contract surface for gaps.

Convergence-by-methodology continues to hold: this round found 3 issues (1 moderate + 2 low), all spec-propagation or contract-precision, none structural. The reviewer's pre-emptive verdict ("I would not run another full design-review cycle after that unless the patch changes the algorithm") fits the finding shape — no algorithm changes are required.

## 3. Adversarial Findings

### F1. Invalid-UTF-8 stance is missing from the owner-spec patch

- **Lens:** Source of Truth / Carry-over Discipline
- **Severity:** MODERATE
- **Decision state:** spec-propagation gap
- **Anchor:** §2 Contract and §5.2 explicitly name invalid UTF-8 as file-level corruption with bootstrap-caught `UnicodeDecodeError`. §7.2's proposed `recovery-and-journal.md` bullets cover TTL, storage, cleanup, timestamp parsing, per-file atomicity, ownership, and blank lines — but **not** the UTF-8 invariant.
- **Problem:** The round-4 D4 discipline ("§2-to-§7 mirroring") caught most amendments but missed F5 because F5 is a file-format invariant rather than a record-level retention rule, so it didn't match the implicit checklist that drove §7.2's other bullets.
- **Impact:** Implementation follows §7 exactly, updates `recovery-and-journal.md`, and accidentally omits the invalid-UTF-8 fatal-to-pass rule. The design remains precise, but the owner spec under-specifies one of the round-4 decisions, and future readers of the owner spec encounter the rule only in commit archaeology.
- **Verification:** confirmed by reading §7.2 against §2 Contract. The UTF-8 invariant lives at the contract level (file-format), not retention level, so it belongs as its own §7.2 bullet (or folded into a new "Encoding" bullet).
- **Resolution chosen:** Add a combined **"Encoding and line endings"** bullet to §7.2 that covers UTF-8-by-construction *and* LF-only-by-construction (resolving this finding plus F2 below) plus the fatal-to-pass corruption behavior plus the bootstrap-catch policy.

### F2. "Record bytes preserved" still overclaims under default text-mode newline translation

- **Lens:** Contract Specification / Correctness Precision
- **Severity:** LOW
- **Decision state:** contract precision gap
- **Anchor:** §5.2 algorithm uses `path.open(encoding="utf-8")` (read, line 208) and `tmp_path.open("w", encoding="utf-8")` (write, line 249). Both are default text mode, which on POSIX does universal-newlines translation: CRLF input → LF in Python string; `\n` write → `\n` on disk (LF only). A hypothetical CRLF input file is silently rewritten as LF.
- **Problem:** §2 Contract says "retained record bytes are preserved" with no qualification for line endings. The body of each record is byte-for-byte preserved, but line-ending bytes are translated.
- **Verification:** confirmed by reading `path.open(encoding="utf-8")` Python defaults — `newline=None` means universal-newlines translation on both read and write. The journal itself only writes LF (`append_*` writers use text-mode write with `+ "\n"`), so CRLF input is purely hypothetical — but the contract should name the format invariant rather than overclaim byte preservation.
- **Resolution chosen:** **LF-only-by-construction**, not `newline=""`. Justification: the journal's own writers always produce LF; the "CRLF input never happens" scenario is rooted in a documented file-format invariant; `newline=""` would add algorithmic complexity for a scenario that doesn't exist in production. §2 Contract gains the user's tightened wording naming the format boundary. §5.2 gains a brief consequence note. §8.3 adds one format-boundary-pin test that asserts the rewritten file uses LF regardless of input — preventing a future implementer from "fixing" text-mode behavior to preserve CRLF without realizing they've changed the documented stance.

### F3. Partial-failure warning text is inaccurate

- **Lens:** Operational Honesty / Messaging Accuracy
- **Severity:** LOW
- **Decision state:** stale wording from before the per-file decoupling landed
- **Anchor:** §6.1 bootstrap call site logs `"audit prune failed; continuing without startup retention cleanup"` when prune raises. After round-4's per-file flag lifecycle, a successful audit pass followed by a failed outcomes pass yields the same warning text — but `events.jsonl` *was* cleaned up.
- **Problem:** The log message says no cleanup happened. The reader cannot distinguish "both files untouched" from "audit cleaned, outcomes failed."
- **Verification:** confirmed by reading §6.1 against §5.2 per-file commit semantics.
- **Resolution chosen:** Reword to `"startup retention cleanup failed or incomplete; continuing"`. Accurate across both failure modes: full failure (both files untouched) and partial failure (one file rewritten, the other untouched). `exc_info=True` continues to surface the specific exception type and traceback for diagnostics.

## 4. Severity Summary and Resolution Table

| ID | Severity | Finding | Resolution | Sections Touched |
| --- | --- | --- | --- | --- |
| F1 | MODERATE | F5 stance missing from owner-spec | New §7.2 "Encoding and line endings" bullet (combined with F2) | §7.2 |
| F2 | LOW | Byte-preservation overclaims under text-mode IO | LF-only-by-construction contract; format-boundary pin test | §2, §5.2, §7.2, §8.3 |
| F3 | LOW | Warning text inaccurate on partial success | Reword to "failed or incomplete; continuing" | §6.1 |

## 5. Convergence Trajectory (Updated)

| Round | Methodology | Findings | High | Medium | Low |
| --- | --- | --- | --- | --- | --- |
| 1 | system-design-review on `a94c05f` | 7 | 4 | 3 | 0 |
| 2 | system-design-review on `5117792` | 3 | 2 | 1 | 0 |
| 3 | system-design-review on `10e32ce` | 1 | 0 | 1 | 0 |
| 4 | adversarial on `539f55a` | 5 | 1 | 2 | 2 |
| 5 | **adversarial on `92a52fb`** | 3 | 0 | 1 | 2 |

Round-5 findings are smaller in count, smaller in severity, and entirely free of structural concerns. The HIGH-severity issue surfaced by round-4's lens change is closed; the residual findings are exactly the kind of "spec propagation + precision" work that a second adversarial pass typically yields once the structural blockers are gone.

**Adversarial-pass convergence is observable.** Round-5 added a 5th round to the trajectory and confidence stayed at 4 (not regressed). The reviewer's own ex-ante verdict — "I would not run another full design-review cycle after that unless the patch changes the algorithm" — calibrates the stopping point.

## 6. Confidence

**Going in:** 4 (round-4 structural fix landed cleanly).
**Going out:** 4 (the three small fixes tighten the contract surface without changing it). Design will be ready for `superpowers:writing-plans` after round-5 amendments are committed.

## 7. Stopping Rule

No further design-review cycles after round-5 amendments unless writing-plans surfaces algorithm-level changes. The diminishing-returns curve has bottomed for this design slice; further marginal precision gains belong to the implementation pass's verification surface, not another design read-through.
