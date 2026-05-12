# Adversarial Review - F4 audit retention design round-6

**Date:** 2026-05-12
**Target:** `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md`
**Reviewed commits:** `5bd1e0d` (round-5 audit), `c3adce6` (round-5 amendments)
**Scope level:** `subsystem`
**Input type:** third adversarial pass over the post-round-5 design
**Methodology:** adversarial (same lens as rounds 4-5, applied to the doubly-amended doc, with active code-path tracing)
**Archetypes:** Data pipeline / ETL + internal tool / back-office
**Stakes:** high

## 1. Review Snapshot

| Signal | Count |
| ------ | ----- |
| High-severity findings | 1 |
| Moderate-severity findings | 1 |
| Low-severity findings | 1 |
| Editorial notes | 0 |
| Findings confirmed against design+code | 3 |
| Findings carrying structural concerns | 1 (F1) |

## 2. Methodology Note

A third adversarial pass on the round-5 amended doc, after round-5 set an explicit stopping rule: *no further design-review cycles unless writing-plans surfaces algorithm-level changes*. The pass was nevertheless run because the reviewer extended the substrate-vs-surface lens (originating in round-4 F1) to a new boundary — the **failure-class boundary** between startup-warn and runtime-propagate behaviors for the same file. That extension surfaced 1 HIGH structural finding.

**Stopping-rule exception triggered.** F1 is algorithm-level: it forces a degraded-mode decision that changes how the runtime append-once path behaves on invalid UTF-8. Writing-plans would not surface this — it isn't a sequencing or fixture question. The stopping rule's exception clause applies.

This pass also added a code-citation discipline absent from rounds 4-5: every finding includes specific `file.py:line` anchors in `server/` to confirm the claim against actual runtime code, not only design prose. F1's verification depended on this discipline.

## 3. Adversarial Findings

### F1. Invalid-UTF-8 warn-and-continue is incoherent across startup vs runtime

- **Lens:** Substrate-vs-Surface / Failure-Class Coherence
- **Severity:** HIGH (structural)
- **Decision state:** algorithm-level — requires explicit degraded-mode policy
- **Anchor:** §2 Contract "invalid UTF-8 byte sequence ... is fatal to that file's prune pass"; §6.1 bootstrap catches `(OSError, UnicodeDecodeError)` and continues; §5.7 `_ensure_*_seen_loaded` makes no provision for `UnicodeDecodeError` and lets it propagate.
- **Problem:** The design treats the same corruption class with two different policies: at startup, warn-and-continue; at runtime, propagate-to-caller. Both code paths read the same corrupt file. After a startup that warned-and-continued, the first `append_dialogue_audit_event_once` or `append_dialogue_outcome_once` call triggers `_ensure_*_seen_loaded()`, which opens the same byte-corrupt file with `encoding="utf-8"`, raises `UnicodeDecodeError`, and propagates the exception up through `append_*_once`.
- **Runtime propagation chain (verified against code):**
  - `server/dialogue.py:264-289` — `_finalize_confirmed_turn` calls `self._journal.append_dialogue_audit_event_once(...)` then `self._journal.append_dialogue_outcome_once(...)` for confirmed turns with a `runtime_id` and `turn_id`.
  - `server/dialogue.py:484-497` — the entire `_finalize_confirmed_turn` call site is wrapped in `try/except Exception as exc: raise CommittedTurnFinalizationError(...) from exc`. Any `UnicodeDecodeError` from either append-once method becomes a user-visible committed-turn finalization failure for the next dialogue turn after a poisoned startup.
- **Impact:** The corruption class — local audit/diagnostic file with invalid UTF-8 — escalates from "operator-visible startup warning" to "next dialogue turn is committed-but-finalization-failed." A class of failures the design intends to be local-only diagnostic leaks into user-facing workflow state. The design's defense — §5.7's "in practice, an invalid UTF-8 file is a corruption signal that surfaces at startup prune and warns there before any append-once site is reached" — relies entirely on operator vigilance: operator sees the startup `WARNING` via `logging.lastResort` and removes/repairs the file before the next append-once call. If the operator doesn't see or act on the warning (host suppresses stderr, attended terminal closed, race between startup and first dialogue turn), the failure path is undefended.
- **Verification:** confirmed against `server/dialogue.py` at HEAD `c3adce6`. The propagation path is real and is not gated on any opt-in flag.
- **Pattern signature:** same substrate-vs-surface shape as round-4 F1 (shared `_ensure_seen_sets_loaded` coupled audit and outcomes availability), one layer deeper — this time the mismatch is between *failure classes* (startup-warn vs runtime-propagate) rather than between API surfaces. The lens generalizes: any time two entry points to the same resource handle the same failure class with different policies, future contributors inherit the mismatch implicitly.
- **Resolution chosen — Path A (Quarantine + empty-set):** Both startup prune and runtime `_ensure_*_seen_loaded` catch `UnicodeDecodeError` per file, rename the affected file to a sibling `<name>.corrupt-<utc-ts>.jsonl` via a shared `_quarantine_corrupt_jsonl` helper (with deterministic `.1`/`.2`/... suffix on existing-target collision), log at `WARNING`, assign the relevant seen-set(s) to empty, and mark that file's initialized flag `True`. The next `append_*` writes a fresh JSONL record into a newly-created file. Quarantine itself does not catch broad `Exception`; quarantine-rename `OSError` propagates normally as a pass failure.
  - **Alternatives considered and rejected:** (B) fatal startup — escalates a local diagnostic-file corruption to MCP-won't-start; worse outcome than today's status quo. (C) empty-set fallback without quarantine — minimum change but corrupt file persists indefinitely; every startup re-warns. (D) tolerate journal failures in `dialogue._finalize_confirmed_turn` — localizes the symptom but undermines `_once` semantics in committed-turn paths.
  - **Explicit trade-off documented in §2 Contract:** records that existed *only* in the quarantined file (no longer in the in-memory seen-set after quarantine) can be re-appended as duplicates on subsequent `append_*_once` calls. This is the accepted trade-off: corrupt diagnostic data does not block live workflow finalization; records in the quarantined file remain available for forensic inspection.

### F2. §7.3 Retention Defaults preamble contradicts the event-timestamp TTL change

- **Lens:** Source of Truth / Carry-over Discipline
- **Severity:** MODERATE
- **Decision state:** spec-propagation gap
- **Anchor:** Owner-spec preamble at `docs/specs/recovery-and-journal.md`, "Retention Defaults" section: *"Canonical retention values. All TTLs are measured from `last_touched_at`, not creation time."* The design's §7.3 patch updates two rows of that table to "From event timestamp" but says "All other rows unchanged" — leaving the preamble contradicting two of its own rows.
- **Problem:** The same carry-over discipline that round-4 D4 introduced ("§2-to-§7 mirroring") and round-5 F1 refined ("after amending §2, check every contract-level invariant has owner-spec representation") still missed this: the preamble is a section-level invariant, not a record-level or file-format invariant. Implementation faithfully applies the §7.3 row patch, leaves the preamble alone, and ships an owner spec that asserts contradictory rules in adjacent sentences.
- **Impact:** Future readers of `recovery-and-journal.md` encounter "All TTLs are measured from `last_touched_at`" immediately above two rows that explicitly say "From event timestamp." Retention semantics become locally undecidable from the spec alone; readers either guess or re-derive from implementation.
- **Verification:** confirmed by reading `recovery-and-journal.md` against design §7.3. The preamble is not in the §7.3 patch envelope.
- **Resolution chosen:** Extend the §7.3 patch envelope to also amend the preamble. Replace *"All TTLs are measured from `last_touched_at`, not creation time."* with *"TTL triggers vary by resource: see the Trigger column. Most TTLs are measured from `last_touched_at`; audit log and outcome records use their event timestamp."* This is a minimal, scoped fix that names both classes explicitly.

### F3. LF-only-by-construction is platform-implicit; writers do not pin `newline="\n"`

- **Lens:** Contract Specification / Cross-Platform Precision
- **Severity:** LOW
- **Decision state:** contract precision gap
- **Anchor:** §2 Contract: *"File format is LF-only by construction: every `append_*` writer emits `\n`."* §5.2 prune uses `path.open(encoding="utf-8")` (read) and `tmp_path.open("w", encoding="utf-8")` (write). Neither passes `newline=` explicitly.
- **Problem:** Python's default text mode (`newline=None`) translates `\n` → `\r\n` on write when running on Windows. The journal's `append_*` writers also use default text mode. So the "by construction" claim is platform-conditional on POSIX, not file-format-by-construction across the platforms Python supports. Round-5's adopted LF-only stance and the §8.3 format-boundary pin test both targeted *input* CRLF normalization on read — neither addressed the writer side or platform portability.
- **Impact:** If the plugin were ever run on Windows, `events.jsonl` and `outcomes.jsonl` would contain CRLF line endings on disk while every spec sentence and test asserts LF-only. The §8.3 pin test would still pass on POSIX CI but fail on Windows.
- **Verification:** confirmed by reading Python text-mode defaults — `newline=None` means platform-dependent newline-on-write. The journal's existing writers in `server/journal.py` use `encoding="utf-8"` with no `newline=` argument.
- **Resolution chosen:** Pin `newline="\n"` in every `open()` call for both writers (`append_*` writers and prune temp-file write). Update §2 Contract to name this construction discipline explicitly. Add one test to §8.3 that asserts the rewritten file's raw bytes contain `\n` and no `\r` regardless of platform. The codex-collaboration plugin has no explicit "POSIX only" stance documented anywhere; pinning the writer is the smaller-blast-radius option versus scoping the contract to POSIX.

## 4. Severity Summary and Resolution Table

| ID | Severity | Finding | Resolution | Sections Touched |
| --- | --- | --- | --- | --- |
| F1 | HIGH | Warn-at-startup + propagate-at-runtime makes UTF-8 corruption surface as committed-turn failure | Quarantine + empty-set, shared helper, both entry points; explicit duplicate-record trade-off documented | §2, §4, §5.2, §5.7, §5.X (new helper section), §6.1, §7.2, §8.2, §8.X (new tests) |
| F2 | MODERATE | §7.3 patch leaves the §Retention Defaults preamble contradicting two of its rows | Extend §7.3 patch envelope to amend preamble | §7.3 |
| F3 | LOW | LF-only-by-construction is platform-implicit; writers do not pin `newline="\n"` | Pin `newline="\n"` in writers + prune temp-file; document; add one platform-portable §8.3 test | §2, §5.2, §7.2, §8.3 |

## 5. Convergence Trajectory (Updated)

| Round | Methodology | Findings | High | Medium | Low |
| --- | --- | --- | --- | --- | --- |
| 1 | system-design-review on `a94c05f` | 7 | 4 | 3 | 0 |
| 2 | system-design-review on `5117792` | 3 | 2 | 1 | 0 |
| 3 | system-design-review on `10e32ce` | 1 | 0 | 1 | 0 |
| 4 | adversarial on `539f55a` | 5 | 1 | 2 | 2 |
| 5 | adversarial on `92a52fb` | 3 | 0 | 1 | 2 |
| 6 | **adversarial on `c3adce6`** | 3 | 1 | 1 | 1 |

**Adversarial-pass convergence is non-monotonic.** Round-5 looked converged (0 HIGH, all spec-propagation). Round-6 re-extended the substrate-vs-surface lens to the *failure-class boundary* and surfaced a HIGH structural finding the prior passes did not see. The lesson: within-methodology convergence (round 4 → 5 dropping to 0 HIGH) is a noisier signal than the round-5 audit treated it as. The pattern is robust enough to name: **structural lenses can re-fire when extended to a new boundary type, even after the same methodology converged on the prior boundaries.**

## 6. Confidence

**Going in:** 4 (round-5 amendments clean; design declared ready for writing-plans).
**Going out:** 4 (post-amendment). The quarantine path closes the F1 incoherence without expanding scope; F2 and F3 are scoped precision fixes. Recommend invoking `superpowers:writing-plans` after round-6 amendments commit.

## 7. Stopping Rule (revised)

Round-5's stopping rule said *no further design-review cycles unless writing-plans surfaces algorithm-level changes*. Round-6 triggered the exception via an extended-lens adversarial pass, not via writing-plans. **Refine the stopping rule:** *no further design-review cycles unless (a) writing-plans surfaces algorithm-level changes OR (b) an extended-lens pass surfaces a structural finding.* This pass demonstrates that (b) is a non-trivial exception class and should be named.

## 8. Deferred Probes

- None new this round. F12 sibling-slice deferred questions stand. F1's quarantine mechanism may need a future "what does ops do with quarantined files" runbook entry — handbook scope, not design scope.

## 9. Implementation Cost Estimate

- One new private helper (`_quarantine_corrupt_jsonl`) plus two call-site catches in `_ensure_*_seen_loaded` plus per-file catches in `prune_audit_logs`.
- `PruneSummary` gains two optional `*_quarantined_to: Path | None` fields.
- ~3–4 new tests in §8.2 / new §8.X; one §8.3 platform-portable LF test.
- One owner-spec preamble line amendment in `recovery-and-journal.md`.
- `newline="\n"` added to existing writer `open()` calls — one-line edits, no logic change.
- Estimated diff size: similar to round-4 (+150/-50 lines) — the quarantine logic is small but documentation around the duplicate-record trade-off and the new helper occupies most of the line count.
