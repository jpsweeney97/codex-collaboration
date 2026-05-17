---
module: recovery-and-journal
status: active
normative: true
authority: recovery-contract
---

# Recovery and Journal

Contracts for crash recovery, operation journaling, audit logging, concurrency control, and resource retention.

## Two-Log Architecture

The plugin maintains two separate logs with different purposes, write disciplines, and retention policies.

| Property | Operation Journal | Audit Log |
|---|---|---|
| Purpose | Idempotent replay after crash | Human incident reconstruction |
| Write discipline | fsync before dispatch | Best-effort append |
| Retention | Trim on operation completion | TTL-based (30 days from event timestamp), pruned at plugin startup |
| Scope | Session-bounded (v1) | Cross-session |
| Consumer | Control plane (automatic recovery) | Claude + user (diagnostics) |
| Format | Operation records with idempotency keys | [AuditEvent](contracts.md#auditevent) records (JSONL) |

### Why Two Logs

The audit log answers "what happened?" The operation journal answers "what was I in the middle of doing?" They have different write patterns, different retention windows, and different consumers. Merging them would either over-retain operational state or under-protect the audit trail.

### Operational Outcomes

A third file, `${CLAUDE_PLUGIN_DATA}/analytics/outcomes.jsonl`, holds delegation and dialogue terminal outcome records (`OutcomeRecord` and `DelegationOutcomeRecord`). It shares the Audit Log's retention class - best-effort append, 30-day TTL, startup-pruned, single-writer ownership - but uses a different record format (typed terminal outcomes rather than per-event audit entries) and a different consumer (retrospective diagnostics rather than incident reconstruction).

**Outcomes are operational diagnostics with a 30-day operational horizon, not long-term analytics history.** A future feature that consumes outcomes for long-term analytics must introduce a separate retention class before shipping.

## Operation Journal

The operation journal ensures that crash recovery is deterministic replay, not inspection-based guessing.

### Write Ordering

**Journal before dispatch.** Every dispatched operation is written to the journal before the corresponding App Server request is sent. This guarantees that:

- If the control plane crashes after journal write but before dispatch, the operation can be retried.
- If the control plane crashes after dispatch, the journal records what was in flight.
- If the control plane crashes before journal write, no operation was dispatched and no cleanup is needed.

### Idempotency Keys

Each journaled operation carries a unique idempotency key. If the same key is replayed, the control plane checks the operation's outcome rather than re-dispatching.

| Operation | Idempotency Key Components | Effect of Replay |
|---|---|---|
| Job creation | `claude_session_id` + `delegation_request_hash` | Check if job already exists |
| Thread creation | `claude_session_id` + `collaboration_id` | Check if thread already started |
| Turn dispatch | `runtime_id` + `thread_id` + `turn_sequence` | Check if turn already started |
| Approval resolution | `request_id` + `decision` | Check if already resolved |
| Promotion | `job_id` + `promotion_attempt` | Check promotion state |

`promotion_attempt` is a controller-owned monotonic counter persisted on the [DelegationJob](contracts.md#delegationjob). It increments before each new promote attempt writes its `promotion` journal `intent` phase.

### Session Scope

In v1, the operation journal is session-bounded. It does not survive across Claude sessions.

**Rationale:** Restarting a delegation that was running when Claude crashed is more likely to surprise the user than to help. The correct recovery for cross-session crashes is: mark the job `unknown`, preserve the worktree and artifacts for inspection, and let the user decide whether to restart or discard.

### Trimming

Completed operations are trimmed from the journal after their outcome is confirmed. The journal should be near-empty during normal operation and only accumulate records for in-flight operations.

### Promotion Replay

Promotion is the only operation journaled in v1 that mutates the primary workspace directly rather than dispatching an App Server request. The phase meanings are therefore workspace-centric:

| Phase | Meaning | Workspace mutation may already have happened? |
|---|---|---|
| `intent` | All promotion prechecks passed; no primary-workspace mutation yet | No |
| `dispatched` | Crossed the mutation boundary; `git apply` may have run | Yes |
| `completed` | Promote reached `verified` or `rolled_back` | Already happened |

Replay rules:

- If recovery finds `promotion:intent` with no later `dispatched`, no primary-workspace mutation occurred. The job normalizes back to `promotion_state="pending"`.
- If recovery finds `promotion:dispatched` with no later `completed`, the journal is authoritative that workspace mutation may have happened. Recovery re-runs post-apply verification, then repairs the job store to `verified` or `rolled_back` as appropriate. If rollback itself fails, recovery leaves the journal entry unresolved and the job at `rollback_needed` so the next startup re-enters recovery.
- If the journal and job store disagree, the journal wins for the "has workspace mutation occurred?" question. A `dispatched` record outranks stale job-store state such as `prechecks_passed`.

`promotion:completed` is a resolution marker, not a terminal-state payload. By write ordering, the controller writes `promotion:completed` only after the job store has already been updated to terminal `promotion_state="verified"` or `promotion_state="rolled_back"`. Recovery reads the job store to learn which terminal state was reached. If a `completed` journal record exists but the job store still reports a pre-terminal promotion state, treat that as inconsistency to surface and repair explicitly rather than guessing from the journal alone.

### Stale Advisory Context Marker

When a successful promotion changes primary-workspace content and an advisory runtime exists for the same repo root, the control plane writes a session-scoped `stale_advisory_context` marker to the operation journal before acknowledging promotion success. The marker stores:

- `repo_root`
- `promoted_artifact_hash`
- `job_id`
- `recorded_at`

The marker is crash-recovery state, not a dispatchable App Server operation. It guarantees that the next advisory turn for that repo root applies the post-promotion coherence protocol in [advisory-runtime-policy.md §Post-Promotion Coherence](advisory-runtime-policy.md#post-promotion-coherence).

If multiple promotions occur before the next advisory turn, the marker is replaced with the newest promoted artifact hash / job id pair for that repo root.

The marker is trimmed after the first successful advisory turn dispatched with the required workspace-changed injection, or when the Claude session ends.

## Audit Log

The audit log records [AuditEvent](contracts.md#auditevent) records for human reconstruction and diagnostics.

### Write Triggers

An audit event is emitted for every state transition that crosses a trust or capability boundary.

**Currently emitted:**

| Trigger | Action Value | Required Fields |
|---|---|---|
| Consultation initiated | `consult` | `collaboration_id`, `runtime_id`, `context_size`, `policy_fingerprint`, `turn_id` |
| Dialogue turn dispatched | `dialogue_turn` | `collaboration_id`, `runtime_id`, `context_size`, `turn_id` |
| Delegation started | `delegate_start` | `collaboration_id`, `job_id`, `runtime_id` |
| Escalation approved | `approve` | `job_id`, `request_id`, `decision` |
| Escalation denied | `deny` | `job_id`, `request_id`, `decision` |
| Escalation surfaced | `escalate` | `collaboration_id`, `job_id`, `request_id` |
| Promotion completed | `promote` | `job_id`, `decision` |
| Promotion rolled back after post-apply verification failed | `rollback` | `collaboration_id`, `job_id`, `runtime_id` |
| Result discarded | `discard` | `job_id` |
| Server request timed out | `approval_timeout` | `job_id`, `request_id` |
| Parked request aborted internally | `internal_abort` | `job_id`, `request_id` |
| Operator decision dispatch failed | `dispatch_failed` | `job_id`, `request_id` |
| Startup recovery detected residual state implying prior interruption | `crash` | `collaboration_id`, `runtime_id` (real, or the `operation_journal` sentinel), `extra` recovery sub-contract — see [§Recovery-Inferred Crash/Restart Audit](#recovery-inferred-crashrestart-audit) |
| A runtime was actually reattached/resumed for a subject during recovery | `restart` | `collaboration_id`, `runtime_id` (new resumed runtime), `extra` recovery sub-contract incl. `crash_recovery_key` — see [§Recovery-Inferred Crash/Restart Audit](#recovery-inferred-crashrestart-audit) |

**Reserved (not currently emitted):**

| Trigger | Action Value | Required Fields |
|---|---|---|
| Thread forked | `fork` | `collaboration_id` |
| Advisory runtime rotated | `rotate` | `runtime_id`, `policy_fingerprint` |
| Advisory runtime frozen | `freeze` | `runtime_id` |
| Frozen runtime reaped | `reap` | `runtime_id` |

**Notes on reserved triggers:** `fork` will be produced by `seed_from` on `codex.dialogue.start` when implemented; provenance is tracked via [CollaborationHandle.parent_collaboration_id](contracts.md#collaborationhandle) (see [decisions.md §Dialogue Fork Scope](decisions.md#dialogue-fork-scope)). `rotate`, `freeze`, `reap` are future-scope freeze-and-rotate design, not current Packet 1 runtime behavior (see [advisory-runtime-policy.md §Future-Scope: Freeze-and-Rotate Design](advisory-runtime-policy.md#future-scope-freeze-and-rotate-design)). `crash` and `restart` are emitted as recovery-inferred events — see [§Recovery-Inferred Crash/Restart Audit](#recovery-inferred-crashrestart-audit).

### Retention

- **Default TTL:** Operational retention for audit and outcome JSONL records uses the same 30-day TTL. `audit/events.jsonl` and `analytics/outcomes.jsonl` are pruned from each record's event timestamp.
- **Retain-on-uncertainty:** Records with missing, non-string, unparseable, or timezone-naive timestamps are retained and counted. They are **TTL-exempt by design** because the system cannot prove they are outside the retention window without risking diagnostic data loss.
- **Storage and rewrite:** Audit records are stored as JSONL in `${CLAUDE_PLUGIN_DATA}/audit/events.jsonl`; outcome records are stored as JSONL in `${CLAUDE_PLUGIN_DATA}/analytics/outcomes.jsonl`. Pruning is atomic per file, preserves retained record text, removes blank lines, and keeps UTF-8 with LF-only line endings.
- **Corruption handling:** Invalid UTF-8 is file-level corruption with automatic quarantine. The affected file is renamed to a forensic sibling matching `<stem>.corrupt-<utc-ts><suffix>`, with deterministic numeric suffixes on collisions. JSON parse failures stay record-local and follow retain-on-uncertainty instead of quarantine.
- **Cleanup trigger:** Old records are pruned on plugin startup. Periodic-during-session pruning is not implemented in v1.

## Crash Recovery Paths

### Advisory Runtime Crash

1. Restart the advisory runtime.
2. Rebuild handle mappings from the [lineage store](contracts.md#lineage-store).
3. Use `thread/read` and `thread/resume` to recover the latest completed state.
4. Reload any `stale_advisory_context` marker from the operation journal and preserve the post-promotion injection requirement for the next advisory turn.
5. Mark any pending server requests as canceled.
6. Allow Claude to continue from the last completed turn. Seeding a new dialogue from the interrupted snapshot remains deferred until `seed_from` on `codex.dialogue.start` enters scope (see [decisions.md §Dialogue Fork Scope](decisions.md#dialogue-fork-scope)).

Startup recovery emits recovery-inferred `crash`/`restart` audit events for advisory handles via the `lineage_handle` subject: a successful reattach co-emits `crash` (the dead runtime) and `restart` (the resumed runtime); a failed reattach emits `crash` only. `restart` links to its `crash` via `extra.crash_recovery_key`; a `crash` may stand alone. See [§Recovery-Inferred Crash/Restart Audit](#recovery-inferred-crashrestart-audit) and [Audit Event Actions](contracts.md#audit-event-actions).

### Delegation Runtime Crash

1. Preserve the worktree and artifacts.
2. Mark the job `unknown` in the [DelegationJob](contracts.md#delegationjob) record.
3. Expose inspection data through `codex.delegate.poll`.
4. Allow either:
   - **Restart from brief:** Create a new execution runtime in the existing worktree and re-delegate with the original prompt.
   - **Discard and cleanup:** Mark the job as discarded and schedule the worktree for cleanup per [retention defaults](#retention-defaults).

### Recovery-Inferred Crash/Restart Audit

There is no concrete process-level crash signal. `crash`/`restart` are **recovery-inferred**: produced by startup recovery from residual state, never by a live runtime event. `crash` means *recovery detected residual state implying a prior interruption*; it makes no claim about the original crash time. `restart` means *a runtime was actually reattached/resumed for a subject* — it is **not** "recovery touched this item." Detect-and-quarantine outcomes emit `crash` only.

Identity is whatever the subject itself records. Three subjects, each keyed on its own stable identity:

| `recovery_subject` | stem | events | `runtime_id` | `recovery_result` |
|---|---|---|---|---|
| `lineage_handle` | `lineage_handle:{collaboration_id}` | `crash`+`restart` co-emitted at reattach success | `crash`: handle's pre-reattach (dead) runtime; `restart`: new resumed runtime | `handle_reattached` |
| `lineage_handle` | `lineage_handle:{collaboration_id}` | `crash` only (reattach failed → `unknown`) | handle's pre-reattach runtime (real, required) | `handle_quarantined_unknown` |
| `orphaned_active_job` | `orphaned_active_job:{job_id}` | `crash` only | `DelegationJob.runtime_id` (real, required, now dead) | `job_marked_unknown` |
| `operation_journal` | `operation_journal:{operation}:{idempotency_key}` | `crash` only | `entry.runtime_id` if recorded, else the sentinel | `journal_reconciled` |

`recovery_key = "{stem}:{action}"`. `restart` carries `extra.crash_recovery_key` pointing at the **same subject's** `crash` `recovery_key`, so the link resolves by construction; a `crash` may stand alone.

**Precedence (no double-crash):** if recovery reattaches a handle, the incident is recorded on `lineage_handle`; no separate `operation_journal` crash is emitted for that handle's driving entry — the entry's `operation`/`phase` ride in `extra` instead. `operation_journal` crash covers only reconciled operations with no reattached handle (in practice, the delegation `job_creation`/`approval_resolution` reconciles, which never reattach — delegation crash recovery quarantines to `unknown` by policy, see [§Delegation Runtime Crash](#delegation-runtime-crash)).

**Runtime sentinel:** `runtime_id = "recovery:unknown-runtime"`. Appears **iff** `action="crash"` **and** `extra.detected_during="startup_recovery"` **and** `recovery_subject="operation_journal"` **and** the driving entry recorded no `runtime_id`. Never on `restart`; never on `lineage_handle` or `orphaned_active_job` (model-guaranteed real IDs). It is a truthful "this runtime was never identified," not a placeholder for a knowable value.

**Duplicate prevention:** owned solely by `OperationJournal` via `append_recovery_audit_event_once(event, *, recovery_key) -> bool`, deduping on `(action, recovery_key)` against in-memory state **and** persisted `audit/events.jsonl`. Controllers MUST NOT keep their own duplicate sets; no `McpServer` coordination flag is needed because the persisted check spans the whole process and disk (eager `startup()` and lazy `_ensure_*_controller()` recovery cannot double-emit). **`collaboration_id`-stability invariant:** the `lineage_handle` stem keys on `collaboration_id`, never `runtime_id` — reattach mutates the handle's `runtime_id`, so a `runtime_id`-keyed stem would change between a failed lazy-recovery attempt and its retry and defeat persisted dedup on the real duplicate vector (phase-2 reattach is driven by lineage-store enumeration, not the self-consuming journal worklist).

**Emission ordering:** a recovery audit event is appended only **after** the local reconciliation write for that item succeeds (journal advanced to `completed`; job/handle transitioned; or reattach `update_runtime` written). A failure before that write emits nothing and never a false successful `restart`; controllers still pin only after recovery succeeds.

The `extra` keys, types, and mandatory/conditional presence are the normative [contracts.md §Recovery Audit Extra Sub-Contract](contracts.md#recovery-audit-extra-sub-contract). `extra.detected_during` is `"startup_recovery"` for all such events in this scope.

**Durability:** these records inherit the audit log's **best-effort** class (see [§Retention](#retention)), not exactly-once durability. The durable truth of recovery is the journal/lineage/job state itself; the audit event is the human-reconstruction layer over it. A process death between the reconciliation write and the audit append may leave the record absent — by design.

### Pending Request Ordering

App Server's `serverRequest/resolved` is authoritative for closing approval and user-input prompts. Pending-request state is not cleared on optimistic assumptions.

- If the control plane resolves a request but crashes before receiving `serverRequest/resolved`, the journal's idempotency key ensures the resolution is not re-sent.
- If `serverRequest/resolved` arrives for a request the control plane does not recognize (e.g., after crash recovery), the event is logged as an audit event but not acted upon.

### Unknown Request Handling

Under current architecture, server-request handling is implemented only in execution-domain turns (advisory turns do not install a `server_request_handler`). Advisory-domain server-request handling is future-scope advisory policy, not current Packet 1 runtime behavior — see [advisory-runtime-policy.md §Future-Scope: Freeze-and-Rotate Design](advisory-runtime-policy.md#future-scope-freeze-and-rotate-design).

When the execution-domain control plane receives a server request with an unrecognized `kind` (captured as `unknown` in [PendingServerRequest](contracts.md#pendingserverrequest)), the delegation job terminalizes as `unknown`. The request does not enter [PendingEscalationView](contracts.md#pending-escalation-view) and is not resolved via `codex.delegate.decide`. Two code paths produce this terminal state with different diagnostic quality:

- **Parse failure:** The request lacks required context fields (`itemId`, `threadId`, or `turnId`). A minimal `PendingServerRequest(kind="unknown")` causal record is created with empty context and only `raw_method` in `requested_scope`. The running turn is interrupted. The causal record may remain in `pending` status.
- **Known-parsed non-parkable:** The request parses successfully (has all context fields) but its `kind` is not in the Packet 1 parkable set (`command_approval`, `file_change`, `request_user_input`). A full-context `PendingServerRequest(kind="unknown")` is created with preserved context fields and non-context `requested_scope` (context keys are stripped by the parser into dedicated fields). The running turn is interrupted. The finalizer may mark the request `resolved`.

Unknown requests are **never auto-approved**. This is the fail-closed default: no automatic grant of unrecognized permissions.

No `action: escalate` [audit event](contracts.md#auditevent) is emitted for unknown terminalization. Terminal evidence is the persisted request record plus `DelegationOutcomeRecord(outcome_type="delegation_terminal", terminal_status="unknown")`.

Unknown terminalization continues to use the persisted `PendingServerRequest(kind="unknown")` plus `DelegationOutcomeRecord(terminal_status="unknown")` as its provenance record. It does not emit an `AuditEvent` unless a later ADR changes the AuditEvent-vs-OutcomeRecord split.

[T-20260429-02](../../../tickets/2026-04-29-codex-collaboration-unsupported-server-request-reachability.md) classifies each unsupported App Server method individually — methods may be promoted to the parkable/supported set, proven as intentionally safe-terminal, or proven non-reachable in current flows.

## Concurrency Limits

### Max Concurrent Delegation Jobs

**v1: exactly 1 user-attention job.** If Claude calls `codex.delegate.start` while any user-attention-required job exists, the controller returns a [Job Busy](contracts.md#job-busy) response with the attention-active job's ID and status. The busy gate covers not just runtime-active jobs (queued/running/needs_escalation) but also completed jobs awaiting review, failed/unknown jobs needing inspection, and partial promotion states needing recovery. A user must promote, discard, or otherwise terminalize the current job before starting a new delegation.

This eliminates queueing, admission control, and contention management for v1. The delegation flow is strictly sequential — one job requiring user attention at a time.

### Advisory-Delegation Race

Advisory turns and promotion checks can race with workspace drift:

1. Advisory consult reads workspace state.
2. Delegation runs and produces artifacts.
3. Promotion applies reviewed workspace content.
4. Next advisory turn has stale context.

This does not break safety — the advisory runtime's read-only sandbox prevents writes. It breaks **coherence**: Codex's advisory responses are grounded in a workspace state that no longer exists.

v1 resolves this with same-thread next-turn context injection. Successful promotion marks advisory context stale; the next advisory turn receives a workspace-changed summary plus refreshed repository identity/context, and the stale marker is cleared after that turn is successfully dispatched. See [advisory-runtime-policy.md §Post-Promotion Coherence](advisory-runtime-policy.md#post-promotion-coherence).

## Retention Defaults

Canonical retention values. TTL triggers vary by resource: see the Trigger column. Most TTLs are measured from `last_touched_at`; audit log and outcome records use their event timestamp.

| Resource | TTL | Trigger |
|---|---|---|
| Completed worktree | 1 hour | After promotion or discard |
| Failed/crashed worktree | 24 hours | After crash detection or failure |
| Audit log records (`events.jsonl`) | 30 days | From event timestamp |
| Outcome records (`outcomes.jsonl`) | 30 days | From event timestamp |
| Lineage/turn session stores | Session end | Normal `server.run()` return cleans registered directories |
| Advisory runtime | Session end | Claude session termination |
| Abandoned sessions | Next startup | Scan for orphaned runtimes/worktrees |
| Diff/test summary | Survives worktree cleanup | Retained in `${CLAUDE_PLUGIN_DATA}` after worktree removal |

The diff/test summary is explicitly retained after worktree cleanup so that delegation history remains inspectable even after the worktree is removed.

Lineage and turn session-store cleanup is a normal-exit action only. Bootstrap registers lazily constructed stores and deduplicates them by session directory, then removes the registered directories after `server.run()` returns. In-process server exceptions, hard crashes, process kills, and machine shutdowns preserve these stores for recovery and forensic inspection until a separate startup-prune owner is specified.
