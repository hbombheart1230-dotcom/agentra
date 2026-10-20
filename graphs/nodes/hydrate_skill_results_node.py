from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import os
import sys

from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from graphs.nodes import skill_result_projection as _skill_projection

from libs.core.symbols import normalize_symbol
from libs.runtime.monitor_entry_sizing import position_by_symbol

def _norm_symbol(v: Any) -> str:
    return normalize_symbol(v)


def _is_trueish(v: Any) -> bool:
    return str(v or "").strip().lower() in ("1", "true", "yes", "y", "on")


def _unique_symbols(candidates: Iterable[Any], *, limit: int = 5) -> List[str]:
    return _skill_projection._unique_symbols(candidates, limit=limit, facade=sys.modules[__name__])


def _quote_hydration_symbols(state: Dict[str, Any], *, candidate_limit: int) -> List[str]:
    return _skill_projection._quote_hydration_symbols(state, candidate_limit=candidate_limit, facade=sys.modules[__name__])


def _to_plain(v: Any) -> Any:
    return _skill_projection._to_plain(v, facade=sys.modules[__name__])


def _build_composite_skill_runner(state: Dict[str, Any]) -> Any:
    from libs.skills.runner import CompositeSkillRunner
    return CompositeSkillRunner.from_env()


def _make_event_logger(state: Dict[str, Any]) -> Any:
    injected = state.get("event_logger")
    if injected is not None and hasattr(injected, "log"):
        return injected
    from libs.core.event_logger import EventLogger
    log_path = os.getenv("EVENT_LOG_PATH", "./data/logs/events.jsonl")
    return EventLogger(log_path=Path(log_path))


def _log_skill_fetch_summary(state: Dict[str, Any], payload: Dict[str, Any]) -> None:
    try:
        logger = _make_event_logger(state)
        run_id = str(state.get("run_id") or "m22-skill-fetch")
        logger.log(run_id=run_id, stage="skill_hydration", event="summary", payload=dict(payload))
    except Exception:
        return


def _resolve_runner(state: Dict[str, Any]) -> Tuple[Any, str, List[str]]:
    errors: List[str] = []

    runner = state.get("skill_runner")
    if runner is not None and hasattr(runner, "run"):
        return runner, "state.skill_runner", errors

    factory = state.get("skill_runner_factory")
    if callable(factory):
        try:
            try:
                built = factory(state)
            except TypeError:
                built = factory()
            if built is not None and hasattr(built, "run"):
                state["skill_runner"] = built
                return built, "state.skill_runner_factory", errors
            errors.append("runner_factory:invalid_runner")
        except Exception as e:
            errors.append(f"runner_factory:exception:{type(e).__name__}")

    auto_requested = _is_trueish(state.get("auto_skill_runner")) or _is_trueish(
        os.getenv("M22_AUTO_SKILL_RUNNER", "")
    )
    if auto_requested:
        try:
            built = _build_composite_skill_runner(state)
            if built is not None and hasattr(built, "run"):
                state["skill_runner"] = built
                return built, "auto.composite_skill_runner", errors
            errors.append("auto_runner:invalid_runner")
        except Exception as e:
            errors.append(f"auto_runner:exception:{type(e).__name__}")

    return None, "none", errors


def _skill_output_to_record(out: Any) -> Dict[str, Any]:
    return _skill_projection._skill_output_to_record(out, facade=sys.modules[__name__])


def _error_reason(rec: Mapping[str, Any]) -> str | None:
    return _skill_projection._error_reason(rec, facade=sys.modules[__name__])


def _fetch_market_quotes(
    runner: Any,
    *,
    run_id: str,
    symbols: List[str],
) -> Tuple[Any, Dict[str, Any]]:
    ready_map: Dict[str, Dict[str, Any]] = {}
    errors: List[str] = []
    attempted = 0
    observed_at = datetime.now(timezone.utc).replace(microsecond=0)
    observed_epoch = int(observed_at.timestamp())
    for sym in symbols:
        attempted += 1
        raw = runner.run(run_id=run_id, skill="market.quote", args={"symbol": sym})
        rec = _skill_output_to_record(raw)
        result = rec.get("result") if isinstance(rec, dict) else {}
        if isinstance(result, dict) and str(result.get("action") or "").lower() == "ready":
            data = result.get("data")
            if isinstance(data, dict):
                row = dict(data)
                row.setdefault("symbol", sym)
                row["_observed_epoch"] = observed_epoch
                row["_observed_at_utc"] = observed_at.isoformat()
                ready_map[sym] = row
        else:
            reason = _error_reason(rec) or "error:unknown"
            errors.append(f"market.quote({sym}):{reason}")

    if ready_map:
        value: Any = ready_map
    elif errors:
        first = str(errors[0])
        error_type = first.rsplit(":", 1)[-1] if ":" in first else first
        value = {"action": "error", "meta": {"error_type": error_type}}
    else:
        value = {}

    meta = {
        "attempted": attempted,
        "ready": len(ready_map),
        "errors": errors,
    }
    return value, meta


def _fetch_account_orders(runner: Any, *, run_id: str) -> Tuple[Any, Dict[str, Any]]:
    raw = runner.run(run_id=run_id, skill="account.orders", args={})
    rec = _skill_output_to_record(raw)
    reason = _error_reason(rec)
    return rec, {"attempted": 1, "ready": 0 if reason else 1, "errors": ([f"account.orders:{reason}"] if reason else [])}


def _fetch_order_status(
    runner: Any,
    *,
    run_id: str,
    order_ref: Dict[str, Any] | None,
) -> Tuple[Any, Dict[str, Any]]:
    ref = dict(order_ref or {})
    ord_no = str(ref.get("ord_no") or "").strip()
    symbol = str(ref.get("symbol") or "").strip()
    ord_dt = str(ref.get("ord_dt") or "").strip()
    qry_tp = str(ref.get("qry_tp") or "3").strip() or "3"

    if not (ord_no and symbol and ord_dt):
        return None, {"attempted": 0, "ready": 0, "errors": []}

    raw = runner.run(
        run_id=run_id,
        skill="order.status",
        args={
            "ord_no": ord_no,
            "symbol": symbol,
            "ord_dt": ord_dt,
            "qry_tp": qry_tp,
        },
    )
    rec = _skill_output_to_record(raw)
    reason = _error_reason(rec)
    return rec, {"attempted": 1, "ready": 0 if reason else 1, "errors": ([f"order.status:{reason}"] if reason else [])}


def hydrate_skill_results_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch skill outputs and store them in canonical `state["skill_results"]`.

    Required state input:
      - `skill_runner`: object with `run(run_id, skill, args)` method
    Optional:
      - `candidates`: scanner candidates (for market.quote fan-out)
      - `order_ref`: {ord_no, symbol, ord_dt, qry_tp} for order.status
      - `run_id`: existing run id
    """
    runner, runner_source, runner_errors = _resolve_runner(state)
    if runner is None or not hasattr(runner, "run"):
        errs = list(runner_errors)
        state["skill_fetch"] = {
            "used_runner": False,
            "runner_source": runner_source,
            "attempted": {"market.quote": 0, "account.orders": 0, "order.status": 0},
            "ready": {"market.quote": 0, "account.orders": 0, "order.status": 0},
            "errors_total": len(errs),
            "errors": errs,
        }
        _log_skill_fetch_summary(state, state["skill_fetch"])
        return state

    run_id = str(state.get("run_id") or "m22-skill-fetch")
    candidate_k = 5
    if isinstance(state.get("policy"), dict):
        try:
            candidate_k = int(state["policy"].get("candidate_k") or candidate_k)
        except Exception:
            candidate_k = 5
    symbols = _quote_hydration_symbols(state, candidate_limit=candidate_k)
    order_ref = state.get("order_ref") if isinstance(state.get("order_ref"), dict) else None

    market_quote_value, mq = _fetch_market_quotes(runner, run_id=run_id, symbols=symbols)
    account_orders_value, ao = _fetch_account_orders(runner, run_id=run_id)
    order_status_value, os = _fetch_order_status(runner, run_id=run_id, order_ref=order_ref)

    skill_results = dict(state.get("skill_results") or {}) if isinstance(state.get("skill_results"), dict) else {}
    skill_results["market.quote"] = market_quote_value
    skill_results["account.orders"] = account_orders_value
    if order_status_value is not None:
        skill_results["order.status"] = order_status_value
    state["skill_results"] = skill_results

    errors = _skill_projection.fetch_errors(runner_errors, mq, ao, os)
    state["skill_fetch"] = {
        "used_runner": True,
        "runner_source": runner_source,
        "ts_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        **_skill_projection.fetch_counts(mq, ao, os, errors),
    }
    _log_skill_fetch_summary(state, state["skill_fetch"])
    return state
