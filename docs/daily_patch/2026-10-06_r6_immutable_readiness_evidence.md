# 2026-10-06 -- R6 immutable per-intent execution-readiness evidence

Evidence/observability hardening. No strategy, scoring, UEF, Step5C, Step5D, ownership (R1-R5), guard
ordering or broker-routing semantics changed. Docker was not rebuilt or restarted (market live).

## Problem

`data/state/execution_readiness.json` is only the latest mutable snapshot. For the 2026-10-06 orders
(BUY 217590 x41 at 09:02:36-38, order 0015433; SELL 217590 x41 at 09:05:46, order 0021826) the exact
readiness value used at execution time cannot be proven. Both passed the outermost readiness guard (no
`execution_readiness_guard_block` events, guard default-enabled, real execution mode), but the in-memory
value was not persisted. Independent review verdict: `INSUFFICIENT_EVIDENCE`.

## Contract

- One append-only JSONL record per BUY/SELL execution decision:
  `data/logs/execution_readiness_evidence/<KST day>.jsonl` (O_APPEND, fsync, never truncated).
- Fields: `schema_version`, `record_id`, `recorded_at`, `phase` (`readiness_guard_block` |
  `pre_broker_submit`), `intent_id`, `run_id`, `runtime_instance_id`, `ownership_generation`,
  `recovery_required`, `portfolio_reconciled`, `open_orders_reconciled`, `orphan_claim_count`,
  `execution_readiness_ready/reasons/computed_at`, `guard_enabled`, `guard_verdict`, `guard_reason`,
  `broker_submission_allowed`, `execution_mode`, `symbol`, `side`, `quantity`, `correlation`
  (entry_reason, exit_reason, signal_source, rationale), `intent_sequence`, `record_hash`.
- Identity: `record_id` is a deterministic digest of the decision identity; an exact duplicate is detected and
  not written twice; replays of one intent get an ordered `intent_sequence`; `record_hash` makes each line
  tamper-evident. Prior lines are never rewritten.
- Authority: EVIDENCE ONLY. Never read by readiness, execution, ownership, Step5C or Step5D code (pinned by
  tests). The in-memory readiness value and guard decision remain authoritative. `execution_readiness.json`
  is not reused.

## Write order (graphs/nodes/execute_from_packet.py)

readiness guard evaluated -> verdict determined -> evidence persisted -> intent admission -> Step5C claim ->
broker submission. A readiness-guard BLOCK is recorded with `broker_submission_allowed=false`. The result carries
`execution.readiness_evidence.record_id` for intent -> evidence -> Step5C/5D -> broker order matching.

## Fail-closed

If the evidence cannot be persisted for a BUY/SELL in real execution mode, nothing is admitted or submitted;
the execution is blocked with `readiness_evidence_write_failed`. This applies only to this evidence contract.
If a readiness-guard block cannot be recorded, the existing block reason is returned unchanged.

## Scope

BUY/SELL in real execution mode inside `execute_from_packet` (same scoping as the readiness guard). CANCEL/MODIFY and
mock mode write nothing. Other `execute_owned_order` callers (skills runner / approval service, `execute_order`
node) do not evaluate the readiness guard and are unchanged. `build_execution_readiness` additionally stamps
`state["execution_readiness_computed_at_epoch"]` (evidence metadata only; the readiness dict is unchanged).

## Historical handling

Prospective only. Nothing back-fills evidence. 2026-10-06 09:02 BUY and 09:05 SELL remain
`READINESS_AT_EXECUTION = UNKNOWN`, root cause `HISTORICAL_OBSERVABILITY_GAP`.

## Verification

- `tests/test_r6_readiness_evidence.py`: 30 tests (ready/not-ready/recovery, instance id, generation, portfolio and
  open-order reconciliation, readiness computed-at, ordering before submit and before admission, fail-closed with
  patched and real I/O failure, append-only/idempotency/duplicate/tamper hash, BUY/SELL/opening_rank1_controlled_probe/
  stop_loss, unchanged guard reasons/routing/Step5C/5D/strategy, evidence never an authority input).
- Regression: 71 execution/readiness/Step5/ownership test files, 749 passed. 8 `tests/test_step5b_fix4.py` tests
  fail identically on the pre-R6 baseline commit c03e205 (`EXECUTION_ENABLED` environment dependence) and were
  not changed.

## Rollout

The running `trading-agent-live` image (`trading-agent-20261002:61586ae`) contains neither yfinance nor R6. After the
session closes: confirm flat/clean state, build an exact-SHA image from the pushed HEAD, one controlled after-hours
restart. R6 live acceptance is prospective: the next real/mock order must show a durable `pre_broker_submit` record
(intent_id, instance_id, generation, recovery_required, reconciliation inputs, readiness verdict, guard verdict,
broker_submission_allowed) that matches the intent, Step5C/5D state, broker order number and fill.
