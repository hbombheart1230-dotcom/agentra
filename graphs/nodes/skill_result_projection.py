"""Pure skill record, quote selection and fetch-summary projection; no runner or clock."""
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping

def _unique_symbols(candidates: Iterable[Any], *, limit: int = 5, facade) -> List[str]:
    out: List[str] = []
    seen = set()
    for row in candidates:
        if isinstance(row, dict):
            sym = facade._norm_symbol(row.get("symbol"))
        else:
            sym = facade._norm_symbol(row)
        if not sym or sym in seen:
            continue
        out.append(sym)
        seen.add(sym)
        if len(out) >= max(1, int(limit)):
            break
    return out


def _quote_hydration_symbols(state: Dict[str, Any], *, candidate_limit: int, facade) -> List[str]:
    candidates = state.get("candidates") if isinstance(state.get("candidates"), list) else []
    out = facade._unique_symbols(candidates, limit=candidate_limit)
    seen = set(out)

    selected = state.get("selected") if isinstance(state.get("selected"), dict) else {}
    selected_symbol = facade._norm_symbol(selected.get("symbol"))
    if selected_symbol and selected_symbol not in seen:
        out.append(selected_symbol)
        seen.add(selected_symbol)

    for symbol, row in facade.position_by_symbol(state).items():
        try:
            qty = int(float((row or {}).get("qty") or 0))
        except Exception:
            qty = 0
        normalized = facade._norm_symbol(symbol)
        if qty > 0 and normalized and normalized not in seen:
            out.append(normalized)
            seen.add(normalized)
    return out


def _to_plain(v: Any, *, facade) -> Any:
    if facade.is_dataclass(v):
        return facade.asdict(v)
    if isinstance(v, dict):
        return {k: facade._to_plain(x) for k, x in v.items()}
    if isinstance(v, list):
        return [facade._to_plain(x) for x in v]
    return v


def _skill_output_to_record(out: Any, *, facade) -> Dict[str, Any]:
    if isinstance(out, dict) and isinstance(out.get("result"), dict):
        return dict(out)

    action = str(getattr(out, "action", "") or "").strip().lower()
    if not action and isinstance(out, dict):
        action = str(out.get("action") or "").strip().lower()

    if action:
        if action == "ready":
            data = facade._to_plain(getattr(out, "data", None))
            if data is None and isinstance(out, dict):
                data = facade._to_plain(out.get("data"))
            rec: Dict[str, Any] = {"result": {"action": "ready", "data": data}}
            return rec

        meta = getattr(out, "meta", None)
        question = getattr(out, "question", None)
        if isinstance(out, dict):
            meta = out.get("meta", meta)
            question = out.get("question", question)
        rec = {"result": {"action": action}}
        if isinstance(meta, dict) and meta:
            rec["result"]["meta"] = dict(meta)
        if question:
            rec["result"]["question"] = str(question)
        return rec

    if isinstance(out, dict):
        return dict(out)

    return {"result": {"action": "error", "meta": {"error_type": "unsupported_skill_output"}}}


def _error_reason(rec: Mapping[str, Any], *, facade) -> str | None:
    result = rec.get("result")
    if not isinstance(result, dict):
        return None
    action = str(result.get("action") or "").strip().lower()
    if action in ("", "ready"):
        return None
    meta = result.get("meta") if isinstance(result.get("meta"), dict) else {}
    error_type = str(meta.get("error_type") or result.get("question") or "skill_not_ready")
    return f"{action}:{error_type}"


def fetch_counts(mq, ao, os, errors):
    return {
        "attempted": {
            "market.quote": int(mq.get("attempted") or 0),
            "account.orders": int(ao.get("attempted") or 0),
            "order.status": int(os.get("attempted") or 0),
        },
        "ready": {
            "market.quote": int(mq.get("ready") or 0),
            "account.orders": int(ao.get("ready") or 0),
            "order.status": int(os.get("ready") or 0),
        },
        "errors_total": len(errors),
        "errors": errors,
    }


def fetch_errors(runner_errors, mq, ao, os):
    return list(runner_errors) + list(mq.get("errors") or []) + list(ao.get("errors") or []) + list(os.get("errors") or [])
