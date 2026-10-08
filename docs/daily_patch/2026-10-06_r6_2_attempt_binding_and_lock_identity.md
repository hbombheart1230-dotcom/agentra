# 2026-10-06 -- R6.2: evidence is proof, not a capability token; strict evidence-lock identity

Independent audit verdict on R6.1: `R6_1_CORRECTION_REQUIRED`. Two proven blockers only. No strategy, readiness,
Step5C, Step5D, UEF or broker-routing semantics changed. Not deployed; Docker untouched.

## A. Evidence-as-capability removed

- Removed: valid ALLOW evidence + age <= 600 s -> execution permitted. The constant is deleted; `recorded_at` is audit only.
- `execution_attempt_id` (one per execution attempt) is generated where the readiness/guard decision is made and flows
  readiness/guard -> R6 evidence -> admission -> `execute_owned_order` -> broker submit:
  `execute_from_packet` (uuid per attempt), `execute_order` node, and the approval / ToolFacade / ExecutorAgent /
  skills-runner chain (`prepare_readiness_evidence` mints it; it travels in the intent copy and skill args).
- The attempt id is part of the deterministic `record_id` and of the evidence reference
  (`record_id, intent_id, execution_attempt_id, runtime_instance_id, ownership_generation, day, phase`).

## B. Choke point (`execute_owned_order`) -- proof + current safety

For real-mode new BUY/SELL (kt10000/kt10001/ORDER_SUBMIT):

1. exactly one hash-valid `pre_broker_submit` ALLOW record, same intent/side/symbol/quantity, and the SAME
   `execution_attempt_id` as the call (else `readiness_evidence_required` / `readiness_evidence_invalid`);
2. evidence runtime instance + generation must equal the CURRENT canonical owner row (read-only `mode=ro`) with a
   live lease (else `readiness_evidence_stale`);
3. the CURRENT readiness value (caller's in-memory dict; otherwise the persisted snapshot only if <= 120 s old) must
   still be `ready`, `recovery_required=false`, same instance/generation (else `readiness_evidence_stale`).

All failures return `NOT_SENT` before any physical/intent claim and with no broker call. Nothing is recomputed:
strategy and readiness remain with their owners. Consumption: same attempt, concurrent duplicates -> one immutable
record; Step5C/idempotency allows one broker mutation. A later attempt needs new evidence.

Documented limitation: evidence recorded with `guard_enabled=false` and no readiness context (operator disabled
`EXECUTION_READINESS_GATE_ENABLED`) has no readiness ALLOW to go stale; it stays attempt-bound but owner/readiness
revalidation is skipped. With readiness present it is still revalidated.

## C. Evidence-storage lock

`_EvidenceLock` (per-day `<day>.jsonl.lock`), built on `live_loop_lock` process-identity primitives:

| situation | result |
|---|---|
| same live pid + same process start identity | lock stays valid regardless of age (wait, then timeout -> fail closed) |
| dead owner | reclaim (exclusive reclaim-guard) |
| same pid, different start identity (PID reuse) | reclaim |
| live pid, identity unverifiable | fail closed (`IDENTITY_UNVERIFIABLE`) |
| malformed / incomplete lock | fail closed (`LOCK_METADATA_INVALID`) |
| lock from another host / PID namespace | never reclaimed (wait, then fail closed) |
| release | exact owner (pid + start identity + token) only |

The lock is published atomically (tmp file + hard link). mtime-only stale breaking is removed. It is storage
serialisation only and unrelated to trading runtime ownership.

## D. Critical section

lock -> read valid records -> dedup -> allocate `intent_sequence` -> append -> flush/fsync -> read-back hash verify ->
release. Dead writer: lock reclaimable. Torn final record: invalid. No submit from an unverified record.

## E/F. Tests and AST guard

`tests/test_r62_attempt_and_lock.py` (30): readiness BLOCK after evidence, generation N->N+1, other instance, expired
lease, new attempt vs old evidence, concurrent duplicate callers (one Step5C winner), age-not-authority both ways,
live writer > 30 s never broken, dead writer, PID reuse, unverifiable identity, malformed lock, foreign host, non-owner
vs exact-owner release, lock released after failure, lock-is-not-ownership, AST guard cases (direct, aliased import,
module alias, dotted chain, name alias, lazy import), gate-disabled limitation. R6 (30) and R6.1 (33) suites updated.
The 8 pre-existing `test_step5b_fix4.py` failures are unchanged.
