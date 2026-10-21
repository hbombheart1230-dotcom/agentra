"""Pure cache read models; effects and orchestration remain in runtime adapters."""
from __future__ import annotations
from typing import Any, Dict

def runtime_float(value: Any, default: float = 0.0, *, facade) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def shadow_float(value: Any, *, facade) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def shadow_text(value: Any, *, max_len: int = 120, facade) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text[: max(1, int(max_len))]


def post_scanner_selected_symbol(state: Dict[str, Any], *, facade) -> str:
    selected = state.get("selected") if isinstance(state.get("selected"), dict) else {}
    if bool(selected.get("_monitor_synthetic_selected")) or bool(selected.get("_closeout_guard_selected")):
        return ""
    scanner_output = state.get("scanner_output") if isinstance(state.get("scanner_output"), dict) else {}
    return str(
        selected.get("symbol")
        or scanner_output.get("top_stock")
        or scanner_output.get("selected_symbol")
        or ""
    ).strip().upper()


def score_bucket(value: Any, *, step: float = 0.10, facade) -> str:
    numeric = facade.shadow_float(value)
    if numeric is None:
        return "unknown"
    if step <= 0.0:
        step = 0.10
    bucket = int(float(numeric) / float(step))
    return f"{round(bucket * step, 4):.2f}-{round((bucket + 1) * step, 4):.2f}"


def rank_bucket(value: Any, *, facade) -> str:
    rank = facade.coerce_int(value, 0)
    if rank <= 0:
        return "unknown"
    if rank == 1:
        return "rank1"
    if rank <= 3:
        return "rank2_3"
    if rank <= 10:
        return "rank4_10"
    return "rank11_plus"


def entry_gate_bucket(state: Dict[str, Any], *, facade) -> str:
    monitor_output = state.get("monitor_output") if isinstance(state.get("monitor_output"), dict) else {}
    monitor = state.get("monitor") if isinstance(state.get("monitor"), dict) else {}
    entry_detail = state.get("monitor_entry_decision_detail") if isinstance(state.get("monitor_entry_decision_detail"), dict) else {}
    for key in ("entry_guard_reason", "entry_exit_reason", "primary_reason_code", "reason"):
        value = (
            monitor_output.get(key)
            if monitor_output.get(key) not in (None, "")
            else monitor.get(key)
            if monitor.get(key) not in (None, "")
            else entry_detail.get(key)
        )
        text = str(value or "").strip().lower()
        if text:
            return text[:80]
    intent = str(monitor_output.get("intent_side") or monitor.get("intent_side") or "").strip().upper()
    if intent == "BUY":
        return "buy_ready"
    return "unknown"


def candidate_theme_tokens(row: Dict[str, Any], *, facade) -> list[str]:
    raw_values: list[Any] = []
    for key in ("theme", "primary_theme", "sector", "industry"):
        raw_values.append(row.get(key))
    for key in ("themes", "theme_names", "theme_tags", "matched_themes"):
        value = row.get(key)
        if isinstance(value, (list, tuple, set)):
            raw_values.extend(list(value))
        else:
            raw_values.append(value)
    out: list[str] = []
    for value in raw_values:
        if value in (None, ""):
            continue
        for token in str(value).replace("|", ",").replace("/", ",").split(","):
            text = token.strip().lower()
            if text and text not in out:
                out.append(text[:80])
    return out[:5]


def candidate_chart_fit_value(row: Dict[str, Any], *, facade) -> Any:
    for key in ("scanner_chart_fit_score", "scanner_macro_chart_fit_score", "entry_compatibility_score", "confidence"):
        if row.get(key) not in (None, ""):
            return row.get(key)
    return None


def candidate_edge_bucket(row: Dict[str, Any], state: Dict[str, Any], *, facade) -> str:
    for key in (
        "cost_adjusted_edge_pct",
        "estimated_gross_edge_pct",
        "expected_edge_pct",
        "expected_move_pct",
        "expected_return_pct",
    ):
        if row.get(key) not in (None, ""):
            value = facade.shadow_float(row.get(key))
            if value is None:
                continue
            if value < 0.0:
                return "negative"
            if value < 0.003:
                return "tiny"
            if value < 0.012:
                return "below_cost_floor"
            if value < 0.025:
                return "tradable"
            return "strong"
    gate = facade.entry_gate_bucket(state)
    if "cost" in gate and ("fail" in gate or "not" in gate or "below" in gate):
        return "below_cost_floor"
    if "ready" in gate or "buy" in gate:
        return "tradable"
    return "unknown"


def compact_post_scanner_candidate_row(row: Dict[str, Any], *, fallback_rank: int = 0, facade) -> Dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    symbol = str(row.get("symbol") or row.get("code") or row.get("ticker") or "").strip().upper()
    if not symbol:
        return {}
    score = None
    score_source = ""
    for key in (
        "score_total",
        "post_adjust_score_total",
        "selected_score_total",
        "scanner_score_total",
        "score",
        "final_score",
        "rank_score",
        "pre_adjust_score_total",
    ):
        score = facade.shadow_float(row.get(key))
        if score is not None:
            score_source = key
            break
    reason = str(
        row.get("selection_reason")
        or row.get("selection_reason_with_bias")
        or row.get("why")
        or row.get("reason")
        or row.get("reason_text")
        or row.get("source_reason")
        or ""
    ).strip()
    rank = facade.coerce_int(row.get("rank"), fallback_rank)
    score_breakdown: Dict[str, Any] = {}
    if isinstance(row.get("score_breakdown"), dict):
        for key, value in list(dict(row.get("score_breakdown") or {}).items())[:10]:
            numeric = facade.shadow_float(value)
            score_breakdown[str(key)[:50]] = (
                round(float(numeric), 6)
                if numeric is not None
                else facade.shadow_text(value, max_len=80)
            )
    compact = {
        "symbol": symbol,
        "rank": int(rank if rank > 0 else fallback_rank),
        "score": round(float(score), 6) if score is not None else None,
        "score_total": round(float(score), 6) if score is not None else None,
        "score_source": score_source,
        "reason": reason[:180],
        "source": str(row.get("source") or row.get("source_name") or "").strip()[:80],
    }
    if score_breakdown:
        compact["score_breakdown"] = score_breakdown
    for key in (
        "risk_score",
        "confidence",
        "entry_compatibility_score",
        "compatibility_bias",
        "scanner_chart_fit_score",
        "scanner_chart_fit_penalty",
        "scanner_macro_chart_fit_score",
        "scanner_macro_chart_fit_bias",
        "bias_adjustment",
        "pre_adjust_score_total",
        "post_adjust_score_total",
        "raw_entry_compatibility_bias",
        "effective_entry_compatibility_bias",
    ):
        value = facade.shadow_float(row.get(key))
        if value is not None:
            compact[key] = round(float(value), 6)
    chart_fit_components: Dict[str, Any] = {}
    if isinstance(row.get("scanner_chart_fit_components"), dict):
        for key, value in list(dict(row.get("scanner_chart_fit_components") or {}).items())[:10]:
            numeric = facade.shadow_float(value)
            chart_fit_components[str(key)[:50]] = (
                round(float(numeric), 6)
                if numeric is not None
                else facade.shadow_text(value, max_len=80)
            )
    if chart_fit_components:
        compact["scanner_chart_fit_components"] = chart_fit_components
    macro_chart_fit_components: Dict[str, Any] = {}
    if isinstance(row.get("scanner_macro_chart_fit_components"), dict):
        for key, value in list(dict(row.get("scanner_macro_chart_fit_components") or {}).items())[:10]:
            numeric = facade.shadow_float(value)
            macro_chart_fit_components[str(key)[:50]] = (
                round(float(numeric), 6)
                if numeric is not None
                else facade.shadow_text(value, max_len=80)
            )
    if macro_chart_fit_components:
        compact["scanner_macro_chart_fit_components"] = macro_chart_fit_components
    for key in (
        "expected_monitor_block_reason",
        "dominant_block_reason",
        "scanner_chart_fit_authority",
        "scanner_macro_chart_fit_authority",
        "market_representative_guard_reason",
        "selection_reason_with_bias",
        "status",
    ):
        text = facade.shadow_text(row.get(key), max_len=160)
        if text:
            compact[key] = text
    return compact


def _cached_candidate_hints(cached_output: Dict[str, Any], *, facade) -> list[str]:
    hints: list[str] = []
    for value in list(cached_output.get("candidate_hints") or []):
        symbol = str(value or "").strip().upper()
        if symbol and symbol not in hints:
            hints.append(symbol)
    for value in list(cached_output.get("candidate_symbols_hint") or []):
        symbol = str(value or "").strip().upper()
        if symbol and symbol not in hints:
            hints.append(symbol)
    for row in list(cached_output.get("candidates") or []):
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol") or "").strip().upper()
        if symbol and symbol not in hints:
            hints.append(symbol)
    return hints


def _monitor_entry_readiness_context(state: Dict[str, Any], *, facade) -> Dict[str, Any]:
    monitor_output = state.get("monitor_output") if isinstance(state.get("monitor_output"), dict) else {}
    monitor_state = state.get("monitor") if isinstance(state.get("monitor"), dict) else {}
    entry_detail = state.get("monitor_entry_decision_detail") if isinstance(state.get("monitor_entry_decision_detail"), dict) else {}
    transition_trace = entry_detail.get("transition_trace") if isinstance(entry_detail.get("transition_trace"), dict) else {}
    readiness_score = facade.shadow_float(
        monitor_output.get("entry_transition_readiness_score")
        if monitor_output.get("entry_transition_readiness_score") not in (None, "")
        else monitor_state.get("entry_transition_readiness_score")
        if monitor_state.get("entry_transition_readiness_score") not in (None, "")
        else transition_trace.get("transition_readiness_score")
    )
    became_ready = bool(
        monitor_output.get("entry_became_ready_this_cycle")
        or monitor_state.get("entry_became_ready_this_cycle")
        or transition_trace.get("became_ready_this_cycle")
    )
    prior_intent = str(monitor_output.get("intent_side") or monitor_state.get("intent_side") or "").strip().upper()
    prior_reason = str(
        monitor_output.get("entry_exit_reason")
        or entry_detail.get("primary_reason_code")
        or entry_detail.get("reason")
        or ""
    ).strip()
    actionable = bool(
        prior_intent == "BUY"
        or became_ready
        or (
            readiness_score is not None
            and readiness_score >= float(facade.PRE_BUY_STRATEGIST_REFRESH_READINESS_THRESHOLD)
        )
    )
    return {
        "actionable": bool(actionable),
        "transition_readiness_score": readiness_score,
        "became_ready_this_cycle": bool(became_ready),
        "prior_intent_side": prior_intent,
        "prior_reason": prior_reason,
    }


