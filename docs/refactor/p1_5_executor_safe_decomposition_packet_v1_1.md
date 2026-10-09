# P1.5.9 Executor v1.1 — Aggressive Small-Owner Decomposition with a Single Safe Order

Date: 2026-10-09
Branch: refactor/p1.5
Original v1.0 EX1–EX6 still governs FIRST safety-constrained extraction, exact §7 guard-order frozen. This packet adds a conditional second pass, never a second broker mutation authority.

## Measured baseline and size goal
graphs/nodes/execute_from_packet.py: ~4,189 physical LOC, 101 top-level defs.
execute_from_packet() function: ~1,192 lines. Largest remaining helpers: _normalize_execution 183; _evaluate_open_order_reconciliation_guard 150; _prepare_request 126; _resolve_order_price_for_notional_with_source 119; _attempt_unfilled_order_recovery 98; _order_entry_chart_guard_snapshot 95; recent sell/buy order guard update 87/69; _append_execution_trace_entries 68.

**Interim safety-preserving façade 2,600–3,200 LOC; aspirational final 1,200–1,800 LOC.** These are estimates, not unconditional acceptance promises. All NEW or expanded extracted pure Owner modules MUST be 150–300 preferred, <=350 physical LOC HARD. The sole ordered execution coordinator is the only permitted over-cap unit while safety is verified. If actual safety/equivalence refuses a reduction, record SIZE_DEFERRED/SAFETY_BLOCKED and preserve current order instead of making changes for metrics.

## Critical frozen authority — never subdivide into independent submitters
Monitor Intent -> Commander eligibility -> execute_from_packet (single ordered coordinator) -> exact-existing readiness/guard chain -> Supervisor verdict -> request and immutable R6.2 evidence/current-owner/generation validation -> admission/Step5C physical and logical CAS -> execute_owned_order canonical mutation choke -> broker submit -> BrokerOutcome/UNKNOWN quarantine -> post-submit cancel/recovery/durable trace.

This is a conceptual overview. The **precise v1.0 §7 ordered chain and real source call/exception phases override this summary**. No guard reorder/short-circuit drift, no duplicate API submit, new broker executor, reconciliation weakening, mutation-owner change, evidence alteration, price/notional/freshness drift, or wrong NOT_SENT for a possibly submitted order. Existing libs/execution/intent_execution_owner.py, readiness_evidence.py, guards/broker_mutation.py, guards/unknown_quarantine.py, order lifecycle and supervisor remain canonical and not duplicated. Never issue real broker orders as a refactor test.

## Candidate target tree; create only when proved distinct
graphs/nodes/execute_from_packet.py                 1,200–1,800 stretch, one sequencing authority

libs/execution/
  executor_observability.py                        150–300   pure trace projection
  executor_artifacts.py                            150–300   canonical artifact coordination
  order_views.py                                   100–250   read-only order display
  executor_read_models/                            OPTIONAL
    intent_projection.py                           150–300
    execution_result.py                            150–300
    broker_status_labels.py                        100–250
    quote_snapshot.py                              150–300   read-only, NOT price/freshness authority
    guard_evidence.py                              150–300   evidence view, NOT guard verdict
  existing execution_readiness.py                 unchanged
  existing readiness_evidence.py                  SAFETY-LOCK
  existing intent_admission.py                    SAFETY-LOCK
  existing intent_identity.py                     SAFETY-LOCK
  existing intent_execution_owner.py              sole physical mutation authority
  existing guards/broker_mutation.py              SAFETY-LOCK
  existing guards/unknown_quarantine.py           SAFETY-LOCK
  existing recent_order_guard.py                  SAFETY-LOCK persistence ordering
  existing order_lifecycle_policy.py              SAFETY-LOCK
  existing executors/real_executor.py             unchanged
  existing executors/mock_executor.py             unchanged

No generic executor_helpers.py dump; a 1,000-line moved helper is NOT a completed extraction.

## Ordered gates
EX1 — local C:\Agentra clean branch/HEAD and immutable BEFORE R6.2/evidence/guard/UNKNOWN/Step5 real-case fixtures, mock execution parity. Preserve dirty Q12 worktrees.
EX2–EX3 — original observability/artifact first, tiny <=350-line Owners, exact trace/exception/IO path parity.
EX4–EX5 — optional pure read views, compatibility wrapper/monkeypatch consumer proof.
EX6 — independent safety acceptance of first pass; anything non-equivalent STOP.
EX7 — ledger all 101 defs and 1,192-line coordinator phases: pure vs state-read vs guard vs write vs mutation; exact exceptions/call order.
EX8 — one pure/read-only non-authority slice at a time into <=350-line Owners; targeted test and local mock replay per slice.
EX9 — OPTIONAL coordinator size pass: replace pure internal presentation/normalization blocks with call-outs while sole coordinator owns EVERY decision/order/error phase. No generic guard service, no movement of live price authority, no broker/CAS/UNKNOWN mutation logic.
EX10 — measure all file LOC, run Step5B/C/D, R6.2 readiness owner/generation, UNKNOWN and duplicate-order, guard precedence, mocked BUY/SELL, no production write + Codex independent code/diff/call graph audit. Advance only with evidence. Full P1.5.11 Docker/UEF/human freeze still applies.

## STOP/FAIL
A mismatched broker call count, Step5C claim order, readiness evidence byte/source/owner/generation, Supervisor timing, UNKNOWN classification, post-submit exception phase, fallback or source-of-truth => stop; revert only the new bounded slice. A cosmetic LOC target cannot authorize any execution behavior change. Never reset the entire Reporting prework or touch production Docker or live orders for this design.
