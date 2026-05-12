# System Design Review - F4 audit retention design

**Date:** 2026-05-12
**Target:** `docs/superpowers/specs/2026-05-12-f4-audit-retention-design.md`
**Scope level:** `subsystem`
**Input type:** design doc
**Archetypes:** Data pipeline / ETL (medium-high confidence) + internal tool / back-office (medium confidence)
**Stakes:** high

## 1. Review Snapshot

| Signal | Count |
| ------ | ----- |
| High-priority findings | 4 |
| Total findings | 7 |
| Tensions identified | 3 |
| Categories screened only | 1 |
| Insufficient evidence | 0 |

## 2. Focus and Coverage

This review treats F4 as the audit/outcome retention and dedup subsystem, not the whole plugin and not an implementation-readiness audit. The stakes are high because the design performs irreversible data deletion, touches auditability, and relies on startup behavior at a trust/recovery boundary.

Deep lenses: Retention & Lifecycle, Source of Truth, Auditability, Durability, Failure Containment, Reversibility, Performance Envelope, Concurrency Safety, Observability, Configuration Clarity.

| Category | Status | Sentinel, anchor, disposition |
| --- | --- | --- |
| Structural | screened | Components and boundaries are nameable: `OperationJournal`, bootstrap, JSONL files, prune helpers, and seen-sets are specified in sections 4-6. Boundary shape is generally legible. |
| Behavioral | deep | Runtime path and failure behavior are described in the contract, pruning pass, append-once invariant, and bootstrap catch path, but several failure boundaries need sharper decisions. |
| Data | deep | The critical datum is traceable from JSONL raw line to timestamp parse, retention decision, rewrite, and dedup population; lifecycle policy has unresolved data-class implications. |
| Reliability | deep | Atomic replacement and non-fatal bootstrap degradation are stated, but cross-file transaction boundaries and operator visibility remain underspecified. |
| Change | deep | Deferred F12/F18/F19 boundaries are explicit, but the same-TTL choice for outcomes makes future analytics separation partly irreversible. |
| Cognitive | deep | The design is unusually legible, but one public exception contract contradicts its own helper/test wording. |
| Trust and Safety | deep | Audit evidence preservation is explicit; the privacy/data-minimization side of malformed-record indefinite retention is not. |
| Operational | deep | Bootstrap integration, logging calls, and verification commands are present, but default logging makes failures practically unobservable. |

## 3. Findings

### F1. Cross-file prune atomicity is underspecified

- **Lens:** Reversibility + Durability
- **Decision state:** underspecified
- **Anchor:** The design gives per-file atomic replacement guarantees, then prunes audit and outcomes sequentially before assigning seen-sets only after both passes succeed.
- **Problem:** The design is clear that a file is never partially replaced, and clear that in-memory sets are swapped only after both passes. It does not say that the filesystem side can partially commit across files: `events.jsonl` can be pruned successfully, then `outcomes.jsonl` can fail, leaving the journal sets uninitialized but one canonical file already rewritten.
- **Impact:** Operators and tests may infer all-or-nothing prune semantics that the design does not provide. The statement that a failed prune can leave old records in place is only sometimes true; a failed prune can also leave one file already pruned.
- **Recommendation or question:** Add an explicit transaction boundary: pruning is atomic per file, not across the audit/outcome pair. State whether partial cross-file prune is accepted, how it should be logged, and that later seen-set loading treats disk as the source of truth after any failure.

### F2. Failure observability is weaker than the contract implies

- **Lens:** Observability + Degradation Strategy
- **Decision state:** explicit decision with hidden cost
- **Anchor:** The contract says prune failure is logged as a warning and startup continues; the bootstrap section later says warning/info output is discarded by Python's default logging configuration until F18.
- **Problem:** "Logged as a warning" reads like an operational signal, but the same design says the signal is not actually emitted anywhere by default. That makes retention failure effectively silent in the deployed shape.
- **Impact:** Old records, malformed retained records, and prune failures can persist without a human-visible cue. This weakens both retention and auditability while preserving the appearance that operations are notified.
- **Recommendation or question:** Decide the v1 minimum signal. Either configure an observable sink, write a maintenance/audit event, emit to stderr, or explicitly downgrade the contract to "a logging call is made but not guaranteed observable until F18."

### F3. Audit and outcome records are coupled to one TTL without a data-class tradeoff

- **Lens:** Retention & Lifecycle + Source of Truth
- **Decision state:** explicit decision
- **Anchor:** The design applies the 30-day audit TTL to both `audit/events.jsonl` and `analytics/outcomes.jsonl`, then leaves long-term analytics as future scope.
- **Problem:** Audit evidence and outcome analytics have related storage mechanics but different lifecycle value. Applying the same TTL may be right, but the design frames it mainly as an unbounded-growth fix, not as a conscious data-class decision.
- **Impact:** If outcome history later becomes useful for long-term analytics, the deployed slice will already have irreversibly deleted older data. A future separate retention class cannot recover history that this slice pruned.
- **Recommendation or question:** Add the explicit tradeoff: are outcomes intentionally operational-only with a 30-day horizon, or should outcomes have a separate retention class before deletion ships?

### F4. Retain-on-uncertainty creates indefinite malformed-record retention

- **Lens:** Auditability + Data Sensitivity Classification
- **Decision state:** explicit decision with hidden cost
- **Anchor:** Missing, non-string, unparseable, and timezone-naive timestamps are retained; the malformed-retention tests cover those cases.
- **Problem:** The retain-on-uncertainty rule protects audit evidence, but it also means timestampless or malformed records are outside the 30-day deletion contract indefinitely. The design does not state that exception as a privacy/minimization tradeoff.
- **Impact:** A malformed line containing sensitive content can survive forever while the surrounding spec says records have a 30-day TTL. If the only signal is a discarded logger call, the exception is easy to miss.
- **Recommendation or question:** State that malformed/timestamp-uncertain records are exempt from TTL deletion by design. Pair that with an observable count or follow-up path so indefinite retention is intentional and visible.

### F5. The single-writer assumption is not named

- **Lens:** Concurrency Safety + Boundary Definition
- **Decision state:** underspecified
- **Anchor:** Startup calls `journal.prune_audit_logs()`, the prune is re-runnable, and the rewrite uses a fixed sibling temp path before `os.replace`.
- **Problem:** The design does not define whether two plugin processes, two startups, or direct callers may prune the same `plugin_data_path` concurrently. The fixed temp path makes that assumption more important because concurrent writers can collide even if each individual replace is atomic.
- **Impact:** If the runtime is implicitly single-process, that is a valid architecture choice, but it should be part of the contract. If concurrent processes are possible, the current design lacks a lock/ownership model.
- **Recommendation or question:** Either state "one process owns a plugin data directory; concurrent prune is unsupported" and test/guard that assumption, or add a cross-process coordination mechanism such as a lock plus unique temp file.

### F6. The performance fix lacks a retained-volume envelope

- **Lens:** Performance Envelope + Resource Proportionality
- **Decision state:** underspecified
- **Anchor:** The design replaces per-write linear scans with startup population of in-memory sets from retained audit/outcome records.
- **Problem:** The design removes per-write O(n) behavior, but it shifts cost to startup scanning and resident memory for all retained dedup keys. The 30-day TTL bounds the window, but there is no expected cardinality, startup latency, or memory envelope.
- **Impact:** If outcomes are high volume, the system may trade one cliff for another: faster appends after startup, but slow process start or large memory growth.
- **Recommendation or question:** Add an expected 30-day volume assumption and an acceptable startup/memory budget. If the answer is "small personal/internal plugin volumes," state that so future reviewers know the intended operating envelope.

### F7. The naive-clock exception contract contradicts itself

- **Lens:** Boundary Definition + Legibility
- **Decision state:** explicit decision with internal contradiction
- **Anchor:** The contract says naive clock outputs fail fast with `RuntimeError`, while the helper, public method docstring, and tests specify `ValueError`.
- **Problem:** The design exposes a clock seam as part of the journal contract, but the failure class is inconsistent inside the design.
- **Impact:** Implementation and tests can satisfy different readings of the same document. Callers also lose a clear distinction between bad injected data and runtime system failure.
- **Recommendation or question:** Pick one exception class and align the contract, helper, and tests. `ValueError` appears to match the helper and test intent.

## 4. Tension Map

### T1. Audit evidence preservation vs data minimization

- **Tension:** Retain-on-uncertainty preserves evidence, but also creates indefinite retention for malformed/timestampless records.
- **What is being traded:** Avoiding silent audit evidence loss versus enforcing a truthful 30-day deletion policy for all records.
- **Why it hid:** The rule sounds conservative and safety-aligned until viewed through the retention/privacy lens.
- **Likely failure story:** A malformed audit line with sensitive content is retained forever, prune summaries are not visible, and the operator believes the 30-day TTL is fully enforced.
- **Linked findings:** F2, F4

### T2. Per-write scalability vs startup/resource concentration

- **Tension:** Replacing linear scans improves append behavior but concentrates work at startup and in resident memory.
- **What is being traded:** Fast dedup checks after initialization versus one full retained-history scan and one full retained-key set in memory.
- **Why it hid:** Both sides are described as one linear pass, but only the old per-write O(n) cost is framed as a performance problem.
- **Likely failure story:** A large `outcomes.jsonl` no longer slows every append, but the MCP server starts slowly or consumes unexpected memory after a long high-volume month.
- **Linked findings:** F5, F6

### T3. Startup availability vs retention accountability

- **Tension:** Continuing startup after prune failure preserves availability but can hide failed maintenance.
- **What is being traded:** Non-fatal cleanup failures versus confidence that retention actually ran.
- **Why it hid:** The design correctly avoids making retention cleanup a startup gate, but "logged warning" makes the availability choice appear operationally visible when it is not.
- **Likely failure story:** Startup succeeds for weeks with prune failures, old records accumulate, and the first visible signal is storage growth or manual inspection.
- **Linked findings:** F1, F2

## 5. Questions / Next Probes

1. Is the cross-file prune contract intentionally "per-file atomic, pair-level partial success allowed," or should F4 require all-or-nothing behavior across audit and outcomes?
2. Are `outcomes.jsonl` records operational logs with a deliberate 30-day horizon, or is this slice making an irreversible analytics retention decision too early?
3. What is the intended ownership model for a `plugin_data_path`: exactly one live MCP process, or multiple possible readers/writers?
4. What signal must an operator actually see when malformed records are retained or prune fails before F18 exists?
