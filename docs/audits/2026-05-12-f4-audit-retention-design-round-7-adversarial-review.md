# Adversarial Review - F4 audit retention design round-7

**Date:** 2026-05-12
**Target:** `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md`
**Reviewed commits:** `fb4a36d` (round-6 audit), `b9cb9fb` (round-6 amendments)
**Scope level:** `subsystem`
**Input type:** fourth adversarial pass over the post-round-6 design
**Methodology:** adversarial (same lens as rounds 4-6, applied to the triply-amended doc, with active code-path verification and project-memory cross-check)
**Archetypes:** Data pipeline / ETL + internal tool / back-office
**Stakes:** high

## 1. Review Snapshot

| Signal | Count |
| ------ | ----- |
| Blocking-class findings | 1 (F1) |
| Structural-class findings | 2 (F2, F3) |
| Framing-class findings | 2 (F4, F5) |
| Algorithm-level changes | 0 |
| Findings confirmed against design+code | 5 |

**Label set (refined this round):**

| Finding | Label | Class | Algorithm-level? |
| --- | --- | --- | --- |
| F1 | `blocking-coherence` | Contract↔test contradiction | No — test text only |
| F2 | `structural-defense` | Declared but undefended assumption | No — paragraph addition |
| F3 | `structural-seam` | Duplicate seam at wrong level | No — parameter removal |
| F4 | `residual-risk framing` | Substance present, framing buried | No — paragraph promotion |
| F5 | `future-reader drift pin` | Naming choice load-bearing for future readers | No — §9 gate addition |

## 2. Methodology Note

A fourth adversarial pass on the round-6 amended doc. Round-6 set the refined stopping rule: *no further design-review cycles unless (a) writing-plans surfaces algorithm-level changes OR (b) an extended-lens pass surfaces a structural finding.* This pass triggered clause (b) via two structural findings (F2 structural-defense, F3 structural-seam) plus one blocking-class coherence finding (F1 contract↔test). The round produced **no algorithm changes** — every finding resolves through documentation or signature edits.

This pass also exercised **project-memory cross-check** as a verification axis absent from rounds 4-6: F3 was tagged as a real seam issue specifically because `feedback_seam_leaf_consumption.md` ("Test seams consume their default at the leaf — don't pass concrete clocks/sources at production call sites") names exactly this anti-pattern. The memory predates the F4 design; the design re-introduced the pattern the memory was written to prevent. Project-memory consultation during adversarial review is now a named verification axis alongside code-citation discipline (round-6).

Code-citation discipline carries forward: every finding includes design-section or `file.py:line` anchors. F1 verification reads §2 line 35, §5.7 line 604-605, §8.7 line 863 in cross-reference. F3 verification reads 7 distinct anchors (enumerated in §3 below).

## 3. Adversarial Findings

### F1. Post-quarantine duplicate test contradicts append-once semantics

- **Lens:** Contract↔Test Coherence (multiple specifications of one behavior)
- **Severity:** BLOCKING (coherence-class, not algorithm-class)
- **Decision state:** test-text-only amendment
- **Anchor:** §2 line 35 (contract) vs §5.7 line 604-605 (algorithm) vs §8.7 line 863 (test).
- **Problem:** §2 line 35 says *"A subsequent `append_*_once` call carrying a logical record that matched a quarantined-file record will succeed (not deduped)"* — singular "a subsequent call." §5.7 line 604-605 confirms the algorithm: `append_*` first, then `self._audit_seen.add(key)` on success — so after a successful first post-quarantine write, the key IS added to the seen set. §8.7 line 863 says *"call `append_dialogue_audit_event_once(R)` twice; assert both calls add records to disk."* The test contradicts both the contract and the algorithm. If both calls wrote, the algorithm would have to skip `self._audit_seen.add(key)` after quarantine — which it does not.
- **Impact:** Implementation reaches this test, finds the algorithm correctly populates the seen set after the first post-quarantine write, and the second call hits dedup. The test as specified would fail. Implementer either reverse-engineers the test text to match algorithm (correct outcome, but the test description was a false anchor) or invents a special-case to satisfy the test (wrong outcome — undermines `_once` semantics permanently post-quarantine).
- **Verification:** confirmed against design at `b9cb9fb`. The contract paragraph is correct; the algorithm is correct; the test description is wrong.
- **Pattern signature:** same "multiple specifications of one behavior" anti-pattern as round-4 F1 (substrate-vs-surface), at a different layer — this time the mismatch is between *contract* and *test catalog* (both specifying the same observable). The pattern: any time two artifacts both state how a behavior must observe, drift is the default.
- **Resolution chosen:** Rewrite the §8.7 line 863 test to assert the correct behavior. Rename it from `test_append_after_quarantine_can_re_append_quarantined_record_as_duplicate` to `test_append_after_quarantine_reappends_once_then_resumes_dedup`. The renamed test asserts: first post-quarantine `append_*_once(R)` writes (single accepted duplicate vs quarantined ghost); second call with the same logical record hits the now-populated seen set and is skipped. Pins the single-accepted-duplicate trade-off explicitly.

### F2. Single-writer assumption is declared but undefended

- **Lens:** Failure-Class Boundary / Assumption-Defense Discipline
- **Severity:** STRUCTURAL (defense gap, not algorithm gap)
- **Decision state:** §2 paragraph extension
- **Anchor:** §2 line 36 (single-writer assumption) vs `docs/specs/contracts.md` line 118 (`${CLAUDE_PLUGIN_DATA}` is "durable plugin state ... not inherently session-scoped").
- **Problem:** §2 line 36 declares "Exactly one MCP process owns a given `plugin_data_path` at a time" and appeals to the `compact()` / `_write_markers` precedent. But: (a) `${CLAUDE_PLUGIN_DATA}` is documented as durable, cross-session plugin state — not session-scoped; (b) the journal files `events.jsonl` and `outcomes.jsonl` sit at the plugin data root, not under a session subdirectory; (c) the precedent appeal is a pattern observation, not a safety proof. The assumption is named and unsupported.
- **Impact:** Two MCP server processes whose `plugin_data_path` resolves to the same `${CLAUDE_PLUGIN_DATA}` root (two concurrent Claude Code sessions on the same plugin install, bind-mount aliasing, manual symlink, shared host directory) collide on `<path>.tmp` during concurrent prune. Outcome is undefined: silent corruption, lost retention state, partial rewrites with no operator signal.
- **Verification:** confirmed against `contracts.md` line 118 and the §2 line 36 paragraph at `b9cb9fb`. The defense-by-precedent is real; the defense-by-architecture is missing.
- **Pattern signature:** same failure-class-boundary lens as round-6 F1 — two entry points (concurrent processes) to the same resource (the plugin data root) with no coordination policy. Round-6 closed the startup-vs-runtime boundary; this finding names the process-vs-process boundary.
- **Resolution chosen:** Replace §2 line 36 paragraph with a **narrowed operating-envelope defense**: (a) scope the claim to the prune writer only (`audit/events.jsonl` and `analytics/outcomes.jsonl`), acknowledging that plugin hooks run as separate processes but are not prune writers; (b) key the unsupported case on the shared `${CLAUDE_PLUGIN_DATA}` root (the actual invariant), naming plugin-install-sharing, bind mounts, symlinks, and shared host directories as path-aliasing routes that produce the condition; (c) name a startup file lock as the obvious mitigation that is out of scope for this slice; (d) frame the `compact()` / `_write_markers` precedent as "this matches the repo's current no-lock rewrite pattern," not as a safety argument. The narrowed envelope keeps the no-lock decision honest without overclaiming runtime exclusivity.

### F3. Explicit `now=` is a duplicate seam at the wrong level

- **Lens:** Test-Seam Architecture / Leaf-Consumption Discipline
- **Severity:** STRUCTURAL (seam at wrong layer)
- **Decision state:** parameter removal across 7 anchors
- **Anchor (cross-reference within the design):**
  - §2 line 31 — contract bullet mentions `now=`
  - §4 line 147 — public method signature has `now: datetime | None = None`
  - §5.1 line 195 — clock seam paragraph references `now=` flow
  - §5.2 lines 275-281 — `prune_audit_logs(now)` normalize branch
  - §5.2c line 446 — `_quarantine_corrupt_jsonl` uses `self._now()` (the INCONSISTENCY)
  - §6.3 line 712 — "(or explicit `now=`)" parenthetical
  - §6.4 line 726 — test fixture pattern table row for "Explicit cutoff override"
  - §8.5 line 844 — `test_prune_audit_logs_rejects_naive_explicit_now`
- **Problem:** The journal has TWO seams covering the same axis — `OperationJournal(clock=...)` at the constructor (leaf seam) and `prune_audit_logs(now=...)` at the method (wrong-level seam). `_quarantine_corrupt_jsonl` consumes only the leaf seam (`self._now()`). When tests use the constructor seam, both cutoff AND quarantine ts come from the fake clock — consistent. When tests use `prune_audit_logs(now=T)`, cutoff uses T but quarantine ts uses `self._clock()` — inconsistent. Tests that want to assert on the quarantine filename must coordinate two seams.
- **Impact:** Quarantine-filename test determinism is fragile. Implementer either (a) discovers the inconsistency during test authoring and works around it by also setting the constructor clock, doubling fixture surface, or (b) misses it and writes a flaky test that depends on real-time `datetime.now()` for the quarantine ts. Both outcomes are worse than removing the redundant seam.
- **Verification:** confirmed across the 7 anchors at `b9cb9fb`. Project-memory `feedback_seam_leaf_consumption.md` names exactly this anti-pattern: *"Test seams consume their default at the leaf — don't pass concrete clocks/sources at production call sites."*
- **Pattern signature:** wrong-level seam advertises itself wherever it touches. The 7-anchor blast radius is the structural signature of a leaf-seam violation: removing the `now=` parameter requires edits across §2 contract, §4 signature, §5.1 narrative, §5.2 algorithm, §6.3 lifecycle, §6.4 fixture table, §8.5 test catalog. A leaf-seam at the right level (constructor `clock=`) does not propagate this way.
- **Resolution chosen:** Remove `now=` entirely. Tests fake the clock at the constructor seam. Quarantine and cutoff both flow from `self._clock()` automatically. The design must pass a `rg "now=" docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md` zero-hit gate after the amendment. The audit precursor describes the removed seam; the design does not preserve any historical `now=` mention.

### F4. Malformed TTL-exempt records lack a dedicated trade-off paragraph

- **Lens:** Contract Style / Trade-off Visibility
- **Severity:** RESIDUAL-RISK FRAMING (substance present, framing buried)
- **Decision state:** §2 paragraph promotion
- **Anchor:** §2 line 27 sub-clause: *"a sufficiently corrupt audit or outcome line can survive past the 30-day window indefinitely. `PruneSummary.audit_retained_malformed` and `PruneSummary.outcomes_retained_malformed` count these records each pass."*
- **Problem:** The substance of the residual risk is present, but it's buried inside the larger retain-on-uncertainty bullet. §2 already practices the explicit-trade-off paragraph pattern — see §2 line 35 *"Quarantine duplicate-record trade-off."* Without a parallel paragraph, the malformed-record residual risk is stylistically inconsistent and easy to miss when calibrating "what does F4 actually bound."
- **Impact:** Future readers parsing §2 to understand F4's scope find the quarantine trade-off as a labeled paragraph but the TTL-exempt trade-off as a sub-clause. A future maintainer may believe F4 fully bounds growth, miss the carve-out, and design a downstream system (alerting, capacity, retention policy) that assumes the wrong bound.
- **Verification:** confirmed at `b9cb9fb` §2 line 27. The WARNING-escalation conditional in §6.1 covers observability; only the contract-side framing is buried.
- **Resolution chosen:** Add a parallel §2 paragraph titled "Malformed-record TTL-exempt accumulation trade-off," explicitly naming F4's bound as *valid timestamped records only* and identifying operator intervention via the WARNING summary signal as the sole long-term bound on malformed-record accumulation. Matches house style with no algorithm or test change.

### F5. Quarantined `.jsonl` files are vulnerable to future glob-based readers

- **Lens:** Forward-Compatibility / Reader-Classification Discipline
- **Severity:** FUTURE-READER DRIFT PIN (speculative future concern, deliberate pre-pin)
- **Decision state:** §2 reader-classification paragraph + §9 manual structural gate
- **Anchor:** §5.2c line 468 (deliberate `.jsonl` suffix preservation); production has unrelated `glob`/`rglob` usage in `server/containment.py:400`, `scripts/compare_app_server_schemas.py:119,128` (verified). F4's own readers target `events.jsonl` / `outcomes.jsonl` by exact name — F4 itself is not exposed.
- **Problem:** §5.2c deliberately preserves the `.jsonl` suffix on quarantined files so that "existing log-analysis tooling that filters on `.jsonl` still matches." That choice is correct for inspection tooling — but it makes the quarantined files indistinguishable from live logs to any future production code that enumerates the directory by extension. F18 (metrics summarization) and F19 (config-inventory) are likely candidates to add such enumeration. Without a pin, a future implementer who adds glob-based reading will accidentally include quarantined files in live-record processing.
- **Impact:** Speculative — F4 does not itself add such a reader. Materializes only if/when a future slice adds directory enumeration without filtering. The cost of pre-pinning is one paragraph in §2 plus one clause in §9; the cost of not pinning is rediscovering the carve-out during a future failure investigation.
- **Verification:** confirmed against `server/containment.py:400` (Path.glob in docstring/comment), `scripts/compare_app_server_schemas.py` (rglob production usage). A broad `rg "glob|rglob"` detector would be noisy enough to lose signal.
- **Pattern signature:** same "drift detector for a structural decision" pattern that round-6 added (the `_quarantine_corrupt_jsonl` 4-call-site verification). Pre-pinning load-bearing naming/classification choices is cheap; rediscovery is expensive.
- **Resolution chosen:** (a) Add a §2 paragraph titled "Reader classification" naming three classes of artifact after F4 lands — *live valid records* (TTL-scoped), *live malformed retained records* (TTL-exempt, observed via PruneSummary), *forensic quarantined files* (`*.corrupt-*`, inspection only, not active read sources). Future readers (F18/F19/etc.) must target classes (a)+(b) by exact-name reads and explicitly exclude (c). (b) Add a §9 manual structural review-gate clause (NOT a regex check, because production already has unrelated glob usage that would make a grep-based detector noisy): any future production reader enumerating files under `${CLAUDE_PLUGIN_DATA}/audit/` or `${CLAUDE_PLUGIN_DATA}/analytics/` (via `glob`, `rglob`, `os.scandir`, `os.listdir`, or equivalent) must explicitly exclude or separately classify `*.corrupt-*` siblings.

## 4. Severity Summary and Resolution Table

| ID | Class | Finding | Resolution | Sections Touched |
| --- | --- | --- | --- | --- |
| F1 | blocking-coherence | Test text contradicts contract + algorithm post-quarantine | Rewrite + rename test in §8.7 | §8.7 |
| F2 | structural-defense | Single-writer declared, not defended | Replace §2 line 36 with narrowed operating-envelope paragraph | §2 |
| F3 | structural-seam | `now=` is a duplicate seam at wrong level | Remove parameter across 7 anchors; design must satisfy `rg "now="` zero-hit gate | §2, §4, §5.1, §5.2, §6.3, §6.4, §8.5 |
| F4 | residual-risk framing | TTL-exempt accumulation buried in sub-clause | Promote to parallel §2 trade-off paragraph | §2 |
| F5 | future-reader drift pin | `.jsonl`-preserving quarantine names exposed to future glob readers | §2 reader-classification paragraph + §9 manual structural review-gate clause | §2, §9 |

**Round-7 amendment scope discipline:** §6.4 picks up a fixture-pattern note for the fake-clock surface created by F3's removal of the secondary seam — mutable clock state for time-advance tests (covers the existing §8.6 second-prune test without modifying §8.6 itself) and a warning against using `journal.timestamp()` for time-independent fixtures (since `AuditEvent.timestamp` and `OutcomeRecord.timestamp` are `str`, the example uses a literal `"2026-04-01T00:00:00Z"` or `datetime(...).isoformat().replace("+00:00", "Z")`).

## 5. Convergence Trajectory (Updated)

| Round | Methodology | Findings | Class breakdown |
| --- | --- | --- | --- |
| 1 | system-design-review on `a94c05f` | 7 | 4 HIGH / 3 MED / 0 LOW |
| 2 | system-design-review on `5117792` | 3 | 2 HIGH / 1 MED / 0 LOW |
| 3 | system-design-review on `10e32ce` | 1 | 0 HIGH / 1 MED / 0 LOW |
| 4 | adversarial on `539f55a` | 5 | 1 HIGH / 2 MED / 2 LOW |
| 5 | adversarial on `92a52fb` | 3 | 0 HIGH / 1 MED / 2 LOW |
| 6 | adversarial on `c3adce6` | 3 | 1 HIGH (algorithm) / 1 MED / 1 LOW |
| 7 | **adversarial on `b9cb9fb`** | 5 | 1 blocking-coherence / 2 structural / 2 framing — **0 algorithm-level** |

**Round-7 distinguishes itself from rounds 1-6** by surfacing zero algorithm-level changes — every finding resolves through documentation, signature, or test-text edits. Within-methodology convergence has stabilized on the algorithm; remaining drift is in coherence, defense, and forward-compatibility framing. **Refined stopping rule maintained, no further refinement this round.** The next adversarial pass should look for: (a) algorithm-level changes from writing-plans, (b) further-extended-lens structural findings, (c) coherence drift introduced during implementation.

## 6. Confidence

**Going in:** 4 (round-6 amendments clean; F4 chain dense but coherent).
**Going out:** 4 (post-amendment). The round-7 amendment is documentation-scoped; no algorithm change means no new failure-mode surface introduced. Recommend invoking `superpowers:writing-plans` after round-7 amendments commit.

## 7. Stopping Rule (unchanged from round-6)

*No further design-review cycles unless (a) writing-plans surfaces algorithm-level changes OR (b) an extended-lens pass surfaces a structural finding.*

Round 7 invoked clause (b) via F2 and F3. The 0-algorithm-level outcome suggests within-methodology convergence is now load-bearing on the algorithm; future adversarial cycles should escalate to clause (b) only when the lens has genuinely shifted (e.g., reader-classification lens, project-memory cross-check lens — both new this round).

## 8. Deferred Probes

- None new this round. F12 sibling-slice deferred questions stand. F2's "future startup file lock" is a F4-adjacent slice candidate if multi-Claude-Code-session-per-plugin-install becomes a supported deployment.

## 9. Implementation Cost Estimate

- Test text + rename for F1: ~3 lines in §8.7.
- F2 §2 paragraph replacement: ~6 lines net (4 lines of existing paragraph replaced by ~10 lines of narrowed defense).
- F3 seven-anchor edit: ~15 lines net (mostly deletions — drop signature param, drop normalize branch, drop table row, drop one test entry).
- F3-derivative §6.4 fixture note: ~5 lines.
- F4 §2 paragraph promotion: ~3 lines.
- F5 §2 reader-classification + §9 review-gate: ~6 lines.
- Estimated diff: ~+50/-25 across §2, §4, §5.1, §5.2, §6.3, §6.4, §8.5, §8.7, §9. Substantially smaller than rounds 4-6.
