# Adversarial Review - F4 audit retention design round-8

**Date:** 2026-05-12
**Target:** `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md`
**Reviewed commits:** `67cf17f` (round-7 audit), `82081f6` (round-7 amendments)
**Scope level:** `subsystem`
**Input type:** fifth adversarial pass over the post-round-7 design
**Methodology:** adversarial (same lens as rounds 4-7, applied to the quadruply-amended doc, with code-citation discipline, project-memory cross-check, and consumer-surface propagation check)
**Archetypes:** Data pipeline / ETL + internal tool / back-office
**Stakes:** high

## 1. Review Snapshot

| Signal | Count |
| ------ | ----- |
| Blocking-class findings | 1 (F1) |
| High-class findings | 1 (F2) |
| Moderate-class findings | 2 (F3, F4) |
| Low-class findings | 1 (F5) |
| Algorithm-level changes | 0 |
| Findings confirmed against design+code | 5 |

**Label set:**

| Finding | Label | Class | Algorithm-level? |
| --- | --- | --- | --- |
| F1 | `blocking-correctness` | Pseudocode contradicts contract (partial seen-set survives quarantine) | No — reset statement only |
| F2 | `high-completeness` | Consumer-doc propagation gap (30-day horizon not reflected in readers) | No — doc update only |
| F3 | `moderate-verification` | LF-only contract under-tested for append writers | No — §9 gate addition |
| F4 | `moderate-envelope` | No-lock startup rewrite is sharp (already handled in design) | No — plan carry-forward |
| F5 | `low-future-scope` | Quarantine/malformed retention lacks operator disposition path | No — §10 note |

## 2. Methodology Note

A fifth adversarial pass on the round-7 amended doc. This round introduced **consumer-surface propagation check** as a new verification axis: after the design makes a data-class decision (outcomes = 30-day operational diagnostics), the pass verified whether live consumer surfaces (`decisions.md`, `codex-analytics/SKILL.md`) had been updated to reflect the new horizon. They had not. Rounds 4-7 focused inward on the design's internal coherence; round 8 expanded outward to the design's downstream propagation.

The round also surfaced a **pseudocode/contract contradiction** (F1) that prior rounds missed because existing tests assert the correct behavior — the contradiction is between the contract (which says "seen-set becomes empty") and the pseudocode (which doesn't clear partial builders on quarantine), not between contract and test.

Code-citation discipline and project-memory cross-check carry forward from rounds 6-7.

## 3. Adversarial Findings

### F1. Partial seen-sets survive invalid-UTF-8 quarantine

- **Lens:** Contract↔Algorithm Coherence (pseudocode contradicts stated invariant)
- **Severity:** BLOCKING (correctness-class)
- **Decision state:** pseudocode fix in §5.2 and §5.7
- **Anchor:** §2 line 34 (contract: "relevant in-memory seen-set(s) become empty") vs §5.2 lines 290-317 (startup prune) vs §5.7 lines 538-557 (runtime ensure-loaded)
- **Problem:** The contract says the in-memory seen-set becomes empty after quarantine. But the `populate` callback mutates the local builder sets during the file scan. If the invalid UTF-8 byte appears after some valid JSONL lines, the callback has already added keys to the local sets. The `except UnicodeDecodeError` block quarantines the file and sets stats to zero but never clears the partially-populated local sets. The subsequent assignment (e.g., `self._audit_seen = new_audit_seen`) commits partial state.
- **Impact:** A record whose dedup key survived in the partial set but whose bytes exist only in the quarantined file gets silently skipped on the next `append_*_once`. The contract says it should re-append (quarantine trade-off). The test plan (§8.2) correctly asserts `_audit_seen` is empty post-quarantine — but the pseudocode as written would fail that test when the bad byte follows valid records.
- **Verification:** confirmed at `82081f6`. Both startup path (§5.2 lines 296-317) and runtime path (§5.7 lines 544-557) share the same structural flaw.
- **Resolution:** In every `except UnicodeDecodeError` block, explicitly reassign the relevant local builder set(s) to fresh empty sets before the assignment to `self._*_seen`. This is a 1-line fix per except block (4 total: audit+outcomes in §5.2, audit in §5.7 audit-ensure, outcomes in §5.7 outcomes-ensure).

### F2. Outcome 30-day horizon not propagated to existing analytics consumers

- **Lens:** Consumer-Surface Propagation
- **Severity:** HIGH (completeness gap in live reader contracts)
- **Decision state:** doc updates to `decisions.md` and `codex-analytics/SKILL.md`
- **Anchor:** §2 line 25 (data-class decision: outcomes = 30-day operational diagnostics) vs `docs/specs/decisions.md` line 94 (analytics source, no horizon language) vs `skills/codex-analytics/SKILL.md` line 3 (description: "consultation history, usage data") and line 19 ("Both are append-only JSONL" — no retention caveat)
- **Problem:** The design makes an explicit, irreversible data-class decision at §2 line 25: outcomes are 30-day operational diagnostics, not long-term analytics history. But two live consumer surfaces still describe outcomes as unbounded: `decisions.md` names outcomes as an analytics source with no horizon, and `codex-analytics/SKILL.md` frames its purpose as "consultation history" and "usage data" from "append-only JSONL" with no mention that records older than 30 days are pruned.
- **Impact:** A user invoking `/codex-analytics` for "consultation history" gets only the retained 30-day window with no warning. The loss is surprising because the consuming surface was not updated with the new retention class.
- **Verification:** confirmed at `82081f6` against `decisions.md:94` and `SKILL.md:3,19`.
- **Resolution:** Add `decisions.md` and `skills/codex-analytics/SKILL.md` to the F4 implementation plan's consumer-doc update scope, with explicit "30-day retained operational window" language. The design's §3 (Scope / In) should name these as in-scope doc updates.

### F3. LF-only contract is under-tested for append writers

- **Lens:** Verification Completeness
- **Severity:** MODERATE (test gap; invisible on POSIX)
- **Decision state:** §9 gate addition
- **Anchor:** §2 line 26 (contract: "every `append_*` writer and the prune temp-file write open with `newline="\n"`") vs §8.3 lines 832-835 (test plan pins LF only for prune rewrite)
- **Problem:** The contract covers all writers (append + prune). The test plan only pins the prune rewrite in §8.3. No test or verification gate covers `append_audit_event`, `append_outcome`, or `append_delegation_outcome` for `newline="\n"` usage.
- **Impact:** On POSIX this gap is invisible (default text mode also writes `\n`). But the contract explicitly covers Windows behavior for all writers. An implementation could fix prune output but leave direct append writers platform-dependent, and the test suite would pass on POSIX.
- **Verification:** confirmed at `82081f6`. §8.3 names only prune behavior; no append-writer LF test exists.
- **Resolution:** Add a §9 structural verification gate: `rg 'newline="\\n"' server/journal.py` returning the expected hit count (1 prune temp-file + N append writers). The grep gate catches future append writers too. Name the expected count as a spot-check target.

### F4. No-lock startup rewrite is an acknowledged but sharp envelope

- **Lens:** Operational Envelope
- **Severity:** MODERATE (already handled in design; plan carry-forward only)
- **Anchor:** §2 line 37 (single-writer operating envelope paragraph)
- **Problem:** The design honestly names the single-writer assumption, keys it on `${CLAUDE_PLUGIN_DATA}` root (round-7 F2), and defers a startup lock. F4 changes global files from append-only to rewritten-at-startup, making the unsupported multi-session case more damaging than before.
- **Verification:** confirmed at `82081f6`. §2 line 37 is adequate as a design-level defense.
- **Resolution:** No design amendment. Carry forward to `writing-plans`: the implementation plan must explicitly treat concurrent sessions as unsupported and keep the single-writer envelope visible as a hard assumption.

### F5. Quarantine/malformed retention lacks an operator disposition path

- **Lens:** Operational Completeness
- **Severity:** LOW (future-scope clarification)
- **Anchor:** §2 line 36 (malformed trade-off: "only long-term bound ... is operator intervention") and §2 line 39 (reader classification: forensic quarantined files)
- **Problem:** The design describes the observability signal (WARNING logs) but not what an operator does when warned. No stated cleanup, inspection, or archival path for `*.corrupt-*` files or indefinitely-retained malformed lines.
- **Verification:** confirmed at `82081f6`. §10 (future scope) does not mention operator disposition.
- **Resolution:** Add a §10 future-scope note for operator disposition of forensic files and TTL-exempt malformed records.

## 4. Severity Summary and Resolution Table

| ID | Class | Finding | Resolution | Sections Touched |
| --- | --- | --- | --- | --- |
| F1 | blocking-correctness | Partial seen-sets survive quarantine | Reset local builders in every `except UnicodeDecodeError` | §5.2, §5.7 |
| F2 | high-completeness | 30-day horizon not propagated to consumers | Name consumer-doc updates in §3 scope | §3 |
| F3 | moderate-verification | LF-only under-tested for append writers | Add §9 `newline="\n"` grep gate | §9 |
| F4 | moderate-envelope | No-lock rewrite is sharp | Plan carry-forward (no design change) | — |
| F5 | low-future-scope | No operator disposition path | Add §10 note | §10 |

**Round-8 amendment scope:** F1 + F2 + F3 + F5 (4 findings amended). F4 is a `writing-plans` carry-forward. Test wording sharpened for §8.2 and §8.7 to cover partial-population scenarios.

## 5. Convergence Trajectory (Updated)

| Round | Methodology | Findings | Class breakdown |
| --- | --- | --- | --- |
| 1 | system-design-review on `a94c05f` | 7 | 4 HIGH / 3 MED / 0 LOW |
| 2 | system-design-review on `5117792` | 3 | 2 HIGH / 1 MED / 0 LOW |
| 3 | system-design-review on `10e32ce` | 1 | 0 HIGH / 1 MED / 0 LOW |
| 4 | adversarial on `539f55a` | 5 | 1 HIGH / 2 MED / 2 LOW |
| 5 | adversarial on `92a52fb` | 3 | 0 HIGH / 1 MED / 2 LOW |
| 6 | adversarial on `c3adce6` | 3 | 1 HIGH (algorithm) / 1 MED / 1 LOW |
| 7 | adversarial on `b9cb9fb` | 5 | 1 blocking-coherence / 2 structural / 2 framing — 0 algorithm-level |
| 8 | **adversarial on `82081f6`** | 5 | 1 blocking-correctness / 1 high-completeness / 2 moderate / 1 low — **0 algorithm-level** |

**Two consecutive rounds with zero algorithm-level changes.** Round 8's blocking finding is a pseudocode omission (missing reset), not a design-level algorithm change. The consumer-propagation lens (F2) is new and produced a real completeness gap, confirming that extended-lens passes continue to find material. The stopping rule remains applicable: writing-plans or a genuinely new extended lens could trigger a ninth round.

## 6. Confidence

**Going in:** 4 (round-7 amendments clean; 0-algorithm-level streak).
**Going out:** 4 (post-amendment). F1 is a 1-line-per-block fix that aligns pseudocode with the contract and tests. F2/F3/F5 are documentation-scoped. Recommend invoking `superpowers:writing-plans` after round-8 amendments commit.

## 7. Stopping Rule (unchanged)

*No further design-review cycles unless (a) writing-plans surfaces algorithm-level changes OR (b) an extended-lens pass surfaces a structural finding.*

Round 8 invoked clause (b) via the consumer-propagation lens (F2). The 0-algorithm-level streak across rounds 7-8 strengthens confidence that the algorithm is stable.

## 8. Deferred Probes

- **F4 plan carry-forward:** `writing-plans` must keep the single-writer/no-lock envelope visible as a hard implementation-plan assumption.
- F12 sibling-slice questions stand from prior rounds.

## 9. Implementation Cost Estimate

- F1 §5.2 + §5.7 reset lines: ~4 lines (1 per except block).
- F1 §8.2/§8.7 test wording sharpening: ~6 lines (cover "bad byte after valid records").
- F2 §3 scope addition: ~2 lines.
- F3 §9 gate: ~2 lines.
- F5 §10 note: ~2 lines.
- Estimated diff: ~+20/-5 across §3, §5.2, §5.7, §8.2, §8.7, §9, §10. Smallest amendment round in the F4 chain.
