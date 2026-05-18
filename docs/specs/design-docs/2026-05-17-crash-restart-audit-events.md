# Crash/Restart Audit Events — Phase 2 Mini-Design

**Date:** 2026-05-17
**Register row:** `DEBT-20260517-HL2-CRASH-RESTART-AUDIT`
**Status:** Accepted (design); implemented in HL2 Task 2.2 (DEBT-20260517-HL2-CRASH-RESTART-AUDIT)
**Owner docs touched:** [`contracts.md`](../contracts.md) (audit schema), [`recovery-and-journal.md`](../recovery-and-journal.md) (recovery + audit-log behavior)

This document is the decision record. The **normative** model lives in the owner docs above; this doc explains *why*, records the justified deviation from the live plan's prescribed defaults, and defines the verification oracle.

## Problem

`crash` and `restart` are declared in the audit-event action vocabulary but were carried as **reserved, never emitted** — the owner docs said they "will be emitted when crash-recovery audit wiring is implemented." The reserved trigger rows further specified them as **runtime-level events keyed by `runtime_id`**, with a forward note that "the `restart` event should link to the `crash` event for forensic correlation."

Two facts from the live code make the reserved framing unimplementable as written:

1. **There is no concrete process-level crash signal.** No pid file, lock file, or crash sentinel exists. A crash is only *inferable at startup-recovery time* from residual state: unresolved `OperationJournalEntry` records, orphaned active delegation jobs, or lineage handles whose runtime is gone. The audit record's timestamp is recovery time, not crash time.
2. **`runtime_id` is not universally available.** `AuditEvent.runtime_id` is a required non-empty string, but `OperationJournalEntry.runtime_id` is optional (`thread_creation` entries never carry it; `turn_dispatch`/`job_creation` carry it only when knowable). The reserved "runtime-level, `runtime_id` required" framing cannot hold for journal-only recovery.

## Decision

Adopt a **recovery-event audit model**, not a process-crash model:

- `crash` means *startup recovery detected residual state implying a prior runtime interruption*. It carries `detected_during="startup_recovery"` and makes no claim about the original crash timestamp.
- `restart` means *a runtime was actually reattached/resumed for a specific subject*. It is **not** "recovery touched this item." Detect-and-quarantine outcomes (job marked `unknown`, handle quarantined, journal entry reconciled-to-completed without reattach) emit `crash` only.
- No `AuditEvent` schema change. `action` is an unconstrained `str`; the vocabulary is doc-defined. `extra` already exists and carries the recovery sub-contract.

### Three recovery subjects

The honest identity available to recovery is whatever the *subject* itself records. There are exactly three subjects, each keyed on its own stable identity:

| `recovery_subject` | stem | events | `runtime_id` source | `recovery_result` |
|---|---|---|---|---|
| `lineage_handle` | `lineage_handle:{collaboration_id}` | `crash`+`restart` co-emitted at reattach success | `crash`: pre-existing handle's `runtime_id`, or the sentinel below when the handle was *created during recovery* from a runtime-less `thread_creation` entry; `restart`: new resumed `runtime_id` (always real) | `handle_reattached` |
| `lineage_handle` | `lineage_handle:{collaboration_id}` | `crash` only (reattach failed → `unknown`) | pre-existing handle's `runtime_id` (real, required) | `handle_quarantined_unknown` |
| `orphaned_active_job` | `orphaned_active_job:{job_id}` | `crash` only | `DelegationJob.runtime_id` (real, required, now dead) | `job_marked_unknown` |
| `operation_journal` | `operation_journal:{operation}:{idempotency_key}` | `crash` only — delegation `job_creation`/`approval_resolution`/`promotion` reconciles whose own recovery path is crashworthy — `job_creation`/`approval_resolution` `dispatched` via residual-proof (the unresolved `dispatched` entry is itself the interruption evidence), `promotion` via the recovery-mutation predicate (Oracle 4) — no reattached handle (pure no-ops / no-op sub-paths emit nothing) | `entry.runtime_id` if recorded, else the sentinel below | `journal_reconciled` |

`recovery_key = "{stem}:{action}"`. A `restart` always carries `extra["crash_recovery_key"]` pointing at the **same subject's** crash recovery key — so the forensic link the owner doc wanted is true by construction, never dangling. `crash` may stand alone (quarantine paths have no restart).

**Precedence rule (no double-crash for one incident):** if recovery reattaches a handle, the incident is recorded on the `lineage_handle` subject; we do **not** also emit a separate `operation_journal` crash for that same handle's driving entry. The entry's `operation`/`phase` ride along in `extra` (`recovery_operation`, `recovery_phase`). `operation_journal` crash covers only reconciled operations with **no** reattached handle — in practice the delegation `job_creation`/`approval_resolution`/`promotion` reconciles, which never reattach (delegation crash recovery quarantines to `unknown` by policy).

**Crash precondition (recovery-outcome, not phase):** `crash` is emitted only when the operation's *own recovery path* is crashworthy — **either** the unresolved `dispatched` entry is itself prior-interruption residual (**residual-proof**: `job_creation`/`approval_resolution`; the recovery arm only closes the journal and deliberately does not re-touch job state), **or** recovery durably mutates job/handle/promotion state (**recovery-mutation**: `promotion`). The two bases are not interchangeable; the asymmetry is the contract boundary (Oracle 4). Phase is **not** a universal dispatch proof; the "pure no-op" determination is owned by each recovery method:

- **`thread_creation`** — `intent` is journaled strictly before `start_thread()`, so `intent` is a pure no-op (`_recover_thread_creation` resolves it terminally with no side effect) → **no** `crash`/`restart`. `dispatched` → dispatch occurred → `crash` (sentinel case (b) when the handle is created during recovery).
- **`turn_dispatch`** — a **two-phase lineage incident**. The runtime turn runs *between* the `intent` and `dispatched` writes, so `intent` does **not** imply no-dispatch; `_recover_turn_dispatch` verifies via `thread/read` for **both** phases. Phase-1 `_recover_turn_dispatch` only *reconciles the journal* (confirmed → finalize local state + advance journal; unconfirmed or finalize-failure → handle `unknown`); it does **not** reattach and does **not** add the `collaboration_id` to the phase-1 reattached set. The same handle therefore flows into **phase-2 `recover_startup` reattach** (`resume_thread` + `update_runtime`) — the literal `restart` definition. Emission is on the `lineage_handle` subject *at that phase-2 reattach*: reattach succeeds → `crash`+`restart` co-emitted, `recovery_result="handle_reattached"`; reattach fails or the handle stays `unknown` → `crash` only, `recovery_result="handle_quarantined_unknown"`. The handle is required (`_recover_turn_dispatch` raises without one) → real pre-existing `runtime_id`, never the sentinel. `recovery_result` is keyed on the **reattach outcome**, never on the phase-1 turn-confirmation. Only the driving entry's `operation` and `phase` ride in `extra` (`recovery_operation="turn_dispatch"`, `recovery_phase`) — both are defined sub-contract keys, populated from **in-memory same-pass** staging (best-effort/Conditional; a second crash before the phase-2 audit append degrades the event to the between-turn shape — see §Durability). The phase-1 turn confirm/quarantine sub-state is **recovery-local detail**, not part of the recovery audit sub-contract: the `extra` sub-contract defines no key for it and adding one is unnecessary. It is **not** durably joinable from the event — the journal trims completed entries (`recovery-and-journal.md` §Trimming), so a confirmed turn leaves no journal record, and `recovery_key` is the audit dedup key, not a journal index. Durable recovery truth is the journal/lineage/turn-store *state*; the audit event records the subject, operation, phase, and reattach outcome — the human-reconstruction layer over that state (§Durability).
- **`job_creation`** — `intent` is journaled strictly before any side effect ("no durable state beyond that") → `intent` is a pure no-op → no `crash`. `dispatched` (carries `runtime_id`) → `crash`.
- **`approval_resolution`** — **residual-proof, same basis as `job_creation`** (not a `promotion`-style carve-out). `intent` is journaled strictly before the decision is dispatched → pure no-op → **no `crash`**. A `dispatched` entry is a committed-but-unfinalized decision = prior-interruption residual → **`crash`**. The recovery arm only writes the journal-close (`write_phase(... "completed" ...)`) and touches **no** job/handle/promotion state; the residual `dispatched` entry — not a recovery mutation — is the crash basis, so it needs no recovery-mutation gate (Oracle 4).
- **`promotion`** — **recovery-mutation, not phase**: `crash` only when recovery durably normalizes a non-terminal job to `pending` (`intent`) **or** durably repairs state (`dispatched`: verify→`verified`, rollback→`rolled_back`, or writes a missing rollback audit). `entry.job_id is None`, a missing job, an already-terminal job with no mutation, the workspace-edits guard, and the git-checkout-failure path are pure no-ops → **no `crash`**. *Both* phases have no-op sub-paths; the gate is the recovery-pass-local durable-mutation predicate, never `entry.phase` (Oracle 4).

Governing rule: hook `crash` to the recovery method's own reconcile decision, never to `entry.phase` in the abstract. Emitting `crash` for a pure no-op would be a false forensic record asserting an interruption that did not occur. The `lineage_handle` subject has **two reattach loci** — `thread_creation:dispatched` reattaches *in phase-1 recovery* (its emission point), `turn_dispatch` reattaches *in phase-2 `recover_startup`* (its emission point) — and its `crash` precondition is the **cleanup contract**, not a journal-incident gate: a clean `server.run()` return removes the session store (`recovery-and-journal.md` §Retention Defaults, *Lineage/turn session stores*), so the mere presence of a persisted advisory handle at startup proves an unclean prior exit — it *is* the crash residual. Phase-2 reattach/quarantine of a persisted active/eligible-unknown advisory handle is therefore a `lineage_handle` incident, covering an in-flight `turn_dispatch` **and a between-turn crash with the journal fully `completed` (no unresolved entry)**. `thread_creation:dispatched` is **not** a phase-2 case — it reattaches in phase-1 (`_recover_thread_creation` returns its `collaboration_id` into `recovered_cids`, so phase-2 skips it) and is its own phase-1 `lineage_handle` emission point, as the two-loci sentence above states. A driving `OperationJournalEntry`, when one exists, rides in `extra` (`recovery_operation`/`recovery_phase`); for a between-turn crash those keys are simply absent (Conditional, per the `extra` sub-contract). There is no "clean restart with persisted active handles" case to suppress — the cleanup contract makes it unreachable; clean startup emits nothing because the store was removed, leaving nothing to enumerate.

### Identity shape — no schema change, narrow sentinel

`collaboration_id` is always real: `OperationJournalEntry`, `CollaborationHandle`, and `DelegationJob` each carry a required non-empty `collaboration_id`. `runtime_id` is real for `orphaned_active_job` (required on `DelegationJob`) and for any `lineage_handle` whose handle pre-existed (`CollaborationHandle.runtime_id` is required). Two paths can lack a recorded runtime identity: an `operation_journal` entry that never recorded one, and a `lineage_handle` whose handle is *created during recovery* from a runtime-less `thread_creation` `dispatched` entry — the dispatched thread had no prior handle and the `thread_creation` entry carries no `runtime_id` (only `codex_thread_id`).

Sentinel: `runtime_id = "recovery:unknown-runtime"`.

**Sentinel invariant (exact):** appears **iff** `action="crash"` **and** `detected_during="startup_recovery"` **and** no runtime was ever recorded for the subject — exactly one of: (a) `recovery_subject="operation_journal"` and the driving entry recorded no `runtime_id`; (b) `recovery_subject="lineage_handle"` and the handle was *created during recovery* from a `thread_creation` `dispatched` entry that recorded no `runtime_id` (no pre-existing handle). Never on `restart` (the resumed runtime is always real). Never on `orphaned_active_job`, nor on a `lineage_handle` whose handle pre-existed (model-guaranteed real IDs). The sentinel is a truthful "this runtime was never identified," not a placeholder for a knowable value.

### Duplicate prevention

Single owner: `OperationJournal`. New helper:

```python
def append_recovery_audit_event_once(self, event: AuditEvent, *, recovery_key: str) -> bool:
    """Append a recovery audit event unless (action, recovery_key) already exists.

    Dedupes against both in-memory state and persisted audit/events.jsonl.
    Returns True when appended, False when a duplicate was suppressed.
    """
```

- Dedup key: `(event.action, recovery_key)`. The caller constructs the event already carrying `extra["recovery_key"] == recovery_key`; the helper fails fast if they disagree.
- A dedicated recovery seen-set is loaded from `audit/events.jsonl` via the existing generic file-replay helper with a recovery-specific record callback. It is **separate** from the dialogue dedup set — the key shapes differ and sharing would corrupt dialogue dedup.
- Controllers MUST NOT keep their own duplicate sets. No process-level coordination flag on `McpServer` is needed: the persisted `(action, recovery_key)` check spans the whole process and disk, so eager `startup()` and lazy `_ensure_*_controller()` recovery cannot double-emit.

**Incident cardinality (deliberate):** dedup is **one recovery audit per residual subject `recovery_key`**, not one per real-world crash incident. The persisted `(action, recovery_key)` check keys on the subject's stable stem (`lineage_handle:{collaboration_id}` / `orphaned_active_job:{job_id}` / `operation_journal:{operation}:{idempotency_key}`); once a subject's `crash`/`restart` is recorded, a *later independent* crash of the same still-live subject that is recovered before normal cleanup is **intentionally not re-emitted**. This is consistent with the recovery-inferred model — the record's timestamp is recovery time and makes no original-crash-time claim (§Decision) — and is the deliberate price of the eager/lazy-retry dedup the `collaboration_id`-stable stem exists to provide. This phase does **not** claim per-incident crash fidelity; it claims **one durable forensic marker per residual recovery subject**. Per-incident fidelity, if ever required, is a future discriminator (an incident/attempt suffix) and a separate decision, explicitly out of scope here.

**`collaboration_id`-stability invariant (load-bearing):** the `lineage_handle` stem keys on `collaboration_id`, **never** `runtime_id`. Dialogue reattach calls `update_runtime(...)`, mutating the handle's `runtime_id`; a `runtime_id`-keyed stem would change between a failed lazy-recovery attempt and its retry, defeating persisted dedup on exactly the duplicate vector that matters. The duplicate vector is concrete: dialogue phase-2 reattach is driven by lineage-store enumeration (not the self-consuming journal worklist), so a retry re-enumerates an already-reattached handle and would re-emit `crash`+`restart` — only the persisted `(action, recovery_key)` check stops it. This makes the persisted dedup load-bearing, not belt-and-suspenders.

### Emission ordering and failure semantics

A recovery audit event is appended **only after** the local reconciliation write for that item succeeds:

- `operation_journal` `crash`: after `write_phase(... phase="completed" ...)` for the entry succeeds.
- `orphaned_active_job` `crash`: after the job transition to `unknown` is persisted.
- `lineage_handle` `crash`+`restart`: after the reattach write (`update_runtime`) succeeds — `crash` then `restart`. Failed reattach: after the quarantine write (`update_status(... "unknown")`), `crash` only.

A recovery failure before the reconciliation write emits nothing; it never produces a false successful `restart`. Controllers still pin only after recovery succeeds (existing `McpServer` ordering is preserved).

### `extra` contract

Mandatory on every recovery event: `recovery_key`, `recovery_subject`, `recovery_result`, `detected_during` (`="startup_recovery"` for this phase — all crash/restart is recovery-inferred).

Conditional: `recovery_operation` and `recovery_phase` are present iff a driving `OperationJournalEntry` exists. `crash_recovery_key` is present on `restart` only.

This is a **normative sub-contract** for `action ∈ {crash, restart}`, an explicit documented exception to the general "`extra` is untyped, consumers should not rely on keys" rule. The exception is recorded in `contracts.md`.

## Durability

The audit log is **best-effort append** (its retention class in `recovery-and-journal.md`). A crash/restart audit record is therefore best-effort: if the process dies between the reconciliation write and the audit append, the record may be absent. The **durable** truth of recovery is the journal/lineage/job state itself (journal advanced to `completed`, handle/job marked `unknown` or reattached). The audit event is the human-reconstruction layer over that durable state, consistent with the existing audit-log guarantee. This design does not claim — and must not be read as claiming — exactly-once durable crash/restart records.

Beyond whole-record loss, one **degraded-shape** case is accepted: `turn_dispatch`'s `recovery_operation`/`recovery_phase` come from **in-memory same-pass** staging (phase-1 holds the `OperationJournalEntry`; phase-2 emits). If a second crash intervenes between phase-1's durable journal finalize and the phase-2 audit append, the driving entry is gone (`completed` → trimmed) and the staged metadata did not survive; the next pass still reattaches the persisted handle, but the event legitimately **degrades to the between-turn shape** (oracle 12) — `recovery_operation`/`recovery_phase` absent, which is contract-valid (Conditional: "present iff a driving `OperationJournalEntry` exists"). Durable staging is **not** adopted: it would add a side-channel purely to harden best-effort forensic keys, against this section's stance. Tests assert these keys only within a single recovery pass, never across a second crash/retry.

## Justified deviation from the live plan's prescribed defaults

The live plan (`docs/superpowers/plans/2026-05-17-codex-collaboration-debt-active-rows.md`, Phase 2) pre-committed a default in which `restart` is emitted for *any* reconciled recovery item, including delegation orphaned active jobs (prescribed `recovery_key = f"orphaned_active_job:{job.job_id}:restart"`). The plan permits rejecting a default "with evidence." The evidence:

1. The owner doc defines `restart` literally as *"Runtime restarted after crash."*
2. Delegation crash recovery **quarantines** orphaned jobs to `unknown` for user decision (per `recovery-and-journal.md` §Delegation Runtime Crash). Nothing restarts.
3. The audit log's stated purpose is **human incident reconstruction**. Emitting `restart` for a quarantined job writes a false statement into the forensic trail.

The plan is therefore patched in lockstep (not merely annotated): orphaned jobs emit `crash` only; the three stems and the `collaboration_id` dedup invariant are named in the plan; the Phase 2 test oracle and the HL2 closeout definition are updated. This deviation changes the Phase 2 test oracle, so it is recorded here as the authoritative rationale and mirrored into the plan rather than left as a divergence.

## Spec changes (normative homes)

- **`recovery-and-journal.md`** — clean rewrite of the `crash`/`restart` trigger rows from reserved/runtime-level to the recovery-event model; rewrite of the Advisory Runtime Crash closing note ("restart links to its crash via `crash_recovery_key`; crash may stand alone"); new normative subsection carrying the three-subject table, sentinel invariant, dedup owner/key, `collaboration_id` invariant, emission ordering, and `extra`-by-subject. No "reserved/not emitted" language for `crash`/`restart` is left behind. `fork`/`rotate`/`freeze`/`reap` remain reserved.
- **`contracts.md`** — move `crash`/`restart` from the Reserved table to Currently emitted (`actor="system"`), cross-referencing the recovery section; add the normative `extra` sub-contract exception for `action ∈ {crash, restart}`; note the `runtime_id` recovery sentinel.
- **Status honesty** — specs are normative ahead of source (spec-first per the HL2 plan), so the `crash`/`restart` trigger rows in both owner docs carry an explicit "spec-normative ahead of source; emission lands with HL2 Task 2.2" qualifier. A reader of this docs commit is not misled into thinking the events are emitted at runtime yet. HL2 closeout removes the qualifier once Task 2.2 lands.

## Out of scope

No non-recovery, process-level crash trigger is invented — none exists in the code and fabricating one would require a real crash signal this phase does not add. All `crash`/`restart` emission in this phase is recovery-inferred, which is the honest and complete surface for HL2. No residual row is required: every reachable recovery subject is covered, so `DEBT-20260517-HL2-CRASH-RESTART-AUDIT` closes when source and tests match this design.

## Verification oracle

The implementation is correct when tests prove:

1. Emitted events are `AuditEvent(action="crash"|"restart")`, not ad hoc dicts.
2. `lineage_handle`: a successfully reattached advisory handle that pre-existed emits a `crash` (pre-existing runtime) + `restart` (new runtime) pair on the same stem; `restart.extra["crash_recovery_key"]` resolves to the emitted `crash`.
3. `orphaned_active_job`: a persisted `running`/`needs_escalation` job whose `job_creation` journal entry is already `completed` emits `crash` only, `runtime_id == DelegationJob.runtime_id`, `recovery_result="job_marked_unknown"`.
4. `operation_journal`: a reconciled delegation recovery entry emits `crash` **only when the operation's own recovery path is crashworthy**: either the unresolved `dispatched` entry is itself residual proof of a prior interruption (`job_creation`/`approval_resolution`), or this recovery pass durably mutates job/promotion state or writes the missing rollback audit (`promotion`). A pure journal-close with no residual-proof dispatched entry and no durable recovery mutation emits nothing. The runtime identity rule is unchanged: an entry with no recorded `runtime_id` emits `crash` with `runtime_id="recovery:unknown-runtime"` (sentinel case (a)), one with a recorded `runtime_id` uses it, the exact sentinel invariant holds, and `restart` is never emitted on this subject. Per delegation operation:
   - `job_creation:intent` / `approval_resolution:intent` — journaled strictly before that operation's side effect → pure no-op → **no `crash`**.
   - `job_creation:dispatched` — the dispatch (runtime subprocess spawn) occurred → real prior-runtime interruption → **`crash`**. The unresolved dispatched entry is itself the crash residual; recovery's journal-close acknowledges it (`phase` is the honest dispatch proof — the recovery arm intentionally does not re-touch job state because the dispatch already happened).
   - `approval_resolution:dispatched` — a committed-but-unfinalized decision is residual evidence of a prior interruption → **`crash`** (same residual-proof basis as `job_creation:dispatched`). The recovery arm touches no job/handle/promotion state, so this is **not** a promotion-style carve-out and needs no recovery-mutation gate.
   - `promotion:intent` — **`crash` only when** recovery durably normalizes an existing non-terminal job to `promotion_state="pending"`. `entry.job_id is None`, a missing job, or an already-terminal job (`verified`/`discarded`/`rolled_back`) are pure no-ops → **no `crash`**.
   - `promotion:dispatched` — **`crash` only when** recovery durably repairs state (verify→`verified`, rollback→`rolled_back`, or appends a missing rollback audit for an already-`rolled_back` job). A missing job, an already-terminal job with no mutation, the workspace-edits guard, and the git-checkout-failure path are no-ops → **no `crash`**.

   The discriminator is the operation-specific crashworthy basis above, never `entry.phase` in the abstract: `approval_resolution`/`job_creation` require the residual-proof `dispatched` entry (the unresolved `dispatched` entry *is* the interruption evidence), while `promotion` requires the recovery-pass-local "did this iteration durably mutate job/promotion state (or write a forensic rollback audit)" predicate. This realizes the §Decision *Crash precondition* and `recovery-and-journal.md` §Crash precondition ("recovery-outcome, not phase") as an enumerated test-contract item; the asymmetry is intentional and is the contract boundary.
5. Clean startup emits **no** `crash` and **no** `restart` — a clean `server.run()` return removes the lineage/turn session stores (cleanup contract), so phase-2 `recover_startup` enumerates **no** handles and there is nothing to emit. This is the *only* clean-startup mechanism; there is no journal-incident gate.
6. Recovery reached through both eager and lazy paths, and a retry after a failed lazy recovery, do not duplicate `crash` or `restart` (persisted `(action, recovery_key)` dedup; `collaboration_id`-keyed stem).
7. Recovery failure before the reconciliation write emits nothing and never a false successful `restart`; the controller is not pinned.
8. `append_recovery_audit_event_once` suppresses duplicate `(action, recovery_key)` pairs and allows distinct ones; it fails fast if `event.extra["recovery_key"]` disagrees with the `recovery_key` argument.
9. `thread_creation:dispatched` with no pre-existing handle (crash between the `dispatched` journal write and lineage persist): recovery creates the handle and emits a `lineage_handle` `crash` with `runtime_id="recovery:unknown-runtime"` (sentinel case (b)) plus a `restart` carrying the real new resumed runtime; `restart.extra["crash_recovery_key"]` resolves.
10. `thread_creation:intent`, `job_creation:intent`, and `approval_resolution:intent` (intent strictly precedes that operation's side effect — pure no-op) reconcile with **no** `crash` and **no** `restart`. (`promotion:intent` is **not** in this set — its recovery itself conditionally performs a durable normalize-to-pending; its emit-vs-no-op sub-paths are enumerated in item 4.)
11. `turn_dispatch` is a **two-phase lineage incident** (`intent` is **not** a no-op). Phase-1 `_recover_turn_dispatch` reconciles the journal (confirmed → finalize; unconfirmed/finalize-failure → handle `unknown`) and does **not** reattach; the handle then flows to phase-2 `recover_startup` reattach. Phase-2 reattach succeeds → `lineage_handle` `crash`+`restart` (real handle `runtime_id`; `restart.extra["crash_recovery_key"]` resolves to the `crash`), `recovery_result="handle_reattached"`. Phase-2 reattach fails / handle stays `unknown` → `lineage_handle` `crash` only, `recovery_result="handle_quarantined_unknown"`. `extra` carries `recovery_operation="turn_dispatch"` and `recovery_phase` (the driving entry's `operation`/`phase`) **on the single-pass path** — these are same-pass best-effort (Conditional); a second crash in the phase-1-finalize→phase-2-audit window degrades the event to the between-turn shape (oracle 12, keys absent), so tests assert them only within one recovery pass, never across a retry (see §Durability). `recovery_result` is the phase-2 **reattach** outcome, never the phase-1 turn-confirmation. The phase-1 turn confirm/quarantine sub-state is **not** an `extra` key (none is defined); it is recovery-local detail, not durably joinable (the journal trims completed entries; `recovery_key` is the audit dedup key, not a journal index).
12. **Between-turn advisory crash** (no journal anchor): a persisted `active` advisory handle whose journal is fully `completed` (no unresolved entry) — crash residual by the cleanup contract — is reattached by phase-2 and emits `lineage_handle` `crash`+`restart` with the pre-existing real `runtime_id`; `extra` carries **no** `recovery_operation`/`recovery_phase` (no driving `OperationJournalEntry`). A failed phase-2 reattach of the same handle emits `crash` only, `recovery_result="handle_quarantined_unknown"`.
