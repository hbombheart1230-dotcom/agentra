from __future__ import annotations
from typing import Any, Dict, List


def build_supervisor_output_artifact(
    state: Dict[str, Any],
    *,
    order: Dict[str, Any],
    allowed: bool,
    reason: str,
    details: Dict[str, Any] | None = None,
    strategy_policy_summary: Dict[str, Any] | None = None,
 facade) -> Dict[str, Any]:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    symbol = str(order.get("symbol") or order.get("stk_cd") or "").strip()
    artifact = _base_output(state, agent="supervisor", symbol=symbol, status="ok" if allowed else "blocked")
    artifact.update(
        {
            "invoked_agents": ["supervisor"],
            "intent_id": str(order.get('intent_id') or ''),
            "command": str(order.get("action") or "").strip().upper(),
            "decision": "approve" if allowed else "block",
            "approval_result": bool(allowed),
            "reason": _clip(reason, max_len=220),
            "blocked_allowed_details": _dict(details),
            "supervisor_allow": bool(allowed),
            "verdict": "approve" if allowed else "block",
            "supervisor_reason": _clip(reason, max_len=220),
            "guard_reason": _clip(reason, max_len=220),
            "action": str(order.get("action") or "").strip().upper(),
            "symbol": symbol,
            "order_request_summary": {
                "action": str(order.get("action") or "").strip().upper(),
                "symbol": symbol,
                "qty": _safe_int(order.get("qty")),
                "order_type": _clip(order.get("order_type"), max_len=32),
            },
            "strategy_policy_summary": _dict(strategy_policy_summary),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact


def build_executor_output_artifact(
    state: Dict[str, Any],
    *,
    execution: Dict[str, Any],
    order: Dict[str, Any] | None = None,
 facade) -> Dict[str, Any]:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    execution = _dict(execution)
    order = _dict(order)
    execution_payload = _dict(execution.get("payload"))
    response_payload = _dict(execution_payload.get("response_payload"))
    quote_snapshot = _dict(execution.get("quote_snapshot"))
    symbol = str(execution.get("symbol") or order.get("symbol") or "").strip()
    if "execution_ok" in execution:
        execution_ok = bool(execution.get("execution_ok"))
    elif "ok" in execution:
        execution_ok = bool(execution.get("ok"))
    else:
        execution_ok = bool(execution.get("allowed"))
    artifact = _base_output(
        state,
        agent="executor",
        symbol=symbol,
        status="ok" if bool(execution.get("allowed")) and execution_ok else "error",
    )
    artifact.update(
        {
            "action": str(execution.get("action") or order.get("action") or "").strip().upper(),
            "allowed": bool(execution.get("allowed")),
            "symbol": symbol,
            "qty": _safe_int(order.get("qty") or execution.get("qty")),
            "status": _clip(
                execution.get("status")
                or execution_payload.get("status")
                or response_payload.get("return_msg"),
                max_len=80,
            ),
            "reason": _clip(execution.get("reason"), max_len=220),
            "broker_env": _clip(execution.get("broker_env") or execution_payload.get("broker_env"), max_len=32),
            "effective_mode": _clip(execution.get("effective_mode") or execution_payload.get("effective_mode"), max_len=64),
            "broker_message": _clip(
                execution.get("broker_message")
                or execution_payload.get("broker_message")
                or response_payload.get("return_msg"),
                max_len=200,
            ),
            "ord_no": _clip(
                execution.get("ord_no")
                or execution.get("order_id")
                or execution_payload.get("ord_no")
                or execution_payload.get("order_id")
                or response_payload.get("ord_no")
                or response_payload.get("order_id"),
                max_len=64,
            ),
            "execution_ok": execution_ok,
            # Phase 1 Step 5B: additive BrokerOutcome provenance. `execution_ok`
            # stays a plain bool for backward compatibility; `broker_outcome`
            # lets downstream consumers tell UNKNOWN (broker acceptance
            # unconfirmed, must not be treated as a firm reject) apart from a
            # true NOT_SENT/REJECTED.
            "broker_outcome": _clip(execution.get("broker_outcome"), max_len=32),
            "intent_id": str(execution.get('intent_id') or order.get('intent_id') or ''),
            "intent_claim": _dict(execution.get('intent_claim')),
            "intent_state_persistence_error": str(execution.get('intent_state_persistence_error') or ''),
            "submission_phase": _clip(execution.get("submission_phase"), max_len=64),
            "submission_attempts": _safe_int(execution.get("submission_attempts")),
            "exception_type": _clip(execution.get("exception_type"), max_len=120),
            "reconciliation_required": bool(execution.get("reconciliation_required")),
            "broker_reference_missing": bool(execution.get("broker_reference_missing")),
            "quote_snapshot": quote_snapshot,
            "opening_alpha_execution_price_guard": _dict(execution.get("opening_alpha_execution_price_guard")),
            "best_bid": _safe_float(execution.get("best_bid") if execution.get("best_bid") not in (None, "") else quote_snapshot.get("best_bid")),
            "best_ask": _safe_float(execution.get("best_ask") if execution.get("best_ask") not in (None, "") else quote_snapshot.get("best_ask")),
            "spread_bps": _safe_float(execution.get("spread_bps") if execution.get("spread_bps") not in (None, "") else quote_snapshot.get("spread_bps")),
            "order_request_summary": {
                "action": str(order.get("action") or execution.get("action") or "").strip().upper(),
                "symbol": symbol,
                "qty": _safe_int(order.get("qty") or execution.get("qty")),
                "order_type": _clip(order.get("order_type"), max_len=32),
                "best_bid": _safe_float(execution.get("best_bid") if execution.get("best_bid") not in (None, "") else quote_snapshot.get("best_bid")),
                "best_ask": _safe_float(execution.get("best_ask") if execution.get("best_ask") not in (None, "") else quote_snapshot.get("best_ask")),
                "spread_bps": _safe_float(execution.get("spread_bps") if execution.get("spread_bps") not in (None, "") else quote_snapshot.get("spread_bps")),
            },
            "execution_enabled": bool(execution.get("allowed")),
            "approval_mode": _clip(execution.get("approval_mode"), max_len=32),
            "broker_result": {
                "status": _clip(
                    execution.get("status")
                    or execution_payload.get("status")
                    or response_payload.get("return_msg"),
                    max_len=80,
                ),
                "broker_message": _clip(
                    execution.get("broker_message")
                    or execution_payload.get("broker_message")
                    or response_payload.get("return_msg"),
                    max_len=200,
                ),
                "ord_no": _clip(
                    execution.get("ord_no")
                    or execution.get("order_id")
                    or execution_payload.get("ord_no")
                    or execution_payload.get("order_id")
                    or response_payload.get("ord_no")
                    or response_payload.get("order_id"),
                    max_len=64,
                ),
                "effective_mode": _clip(execution.get("effective_mode") or execution_payload.get("effective_mode"), max_len=64),
                "broker_env": _clip(execution.get("broker_env") or execution_payload.get("broker_env"), max_len=32),
            },
            "final_execution_status": _clip(
                execution.get("status")
                or execution_payload.get("status")
                or response_payload.get("return_msg"),
                max_len=80,
            ) or ("allowed" if execution.get("allowed") else "blocked"),
            "failure_reason": _clip(execution.get("reason"), max_len=220),
            "strategy_policy_summary": _dict(execution.get("strategy_policy_summary")),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact
