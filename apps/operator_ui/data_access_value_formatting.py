"""Operator UI value, time, percent and feature-coverage formatting helpers (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _to_datetime_r3_impl(ts, *, facade):
    if ts is None:
        return None
    if isinstance(ts, facade.datetime):
        dt = ts
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return dt.astimezone(facade.KST)
    if isinstance(ts, (int, float)):
        try:
            return facade.datetime.fromtimestamp(int(ts), tz=facade.timezone.utc).astimezone(facade.KST)
        except Exception:
            return None
    raw = str(ts).strip()
    if not raw:
        return None
    s = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        dt = facade.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return dt.astimezone(facade.KST)
    except Exception:
        return None


def _to_epoch_r3_impl(ts, *, facade):
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return int(ts)
    raw = str(ts).strip()
    if not raw:
        return None
    try:
        return int(float(raw))
    except Exception:
        pass
    s = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        dt = facade.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None


def _format_percent_r3_impl(v, digits, *, facade):
    if v is None or v == "":
        return "-"
    try:
        num = float(v)
    except Exception:
        return str(v)
    if abs(num) <= 1.0:
        num *= 100.0
    return f"{num:.{digits}f}%"


def _format_duration_r3_impl(seconds, *, facade):
    total = facade._safe_int(seconds, -1)
    if total < 0:
        return "-"
    if total < 60:
        return f"{total}s"
    if total < 3600:
        return f"{total / 60.0:.1f}m"
    return f"{total / 3600.0:.1f}h"


def _format_float_r3_impl(v, digits, *, facade):
    if v is None or v == "":
        return "-"
    try:
        return f"{float(v):.{digits}f}"
    except Exception:
        return str(v)


def _friendly_exit_reason_r3_impl(reason, *, facade):
    raw = str(reason or "").strip().lower()
    normalized = raw.replace(" ", "_")
    mapping = {
        "hard_stop": "Hard stop",
        "stop_loss": "Adaptive stop",
        "take_profit": "Take profit",
        "trailing_stop": "Trailing stop",
        "peak_drawdown": "Peak drawdown",
        "vwap_breakdown": "VWAP breakdown",
        "intraday_low_break": "Intraday low break",
        "trend_breakdown": "Trend breakdown",
        "volatility_expansion": "Volatility expansion",
        "news_shock": "News shock",
        "hold": "No trigger yet",
        "no_position": "No position",
        "price_unavailable": "Price unavailable",
    }
    return mapping.get(normalized, str(reason or "-").replace("_", " ") if str(reason or "").strip() else "-")


def _friendly_feature_name_r3_impl(key, *, facade):
    k = str(key or "").strip()
    if not k:
        return "-"
    if k in facade._FEATURE_NAME_MAP:
        return facade._FEATURE_NAME_MAP[k]
    return k.replace("engine_", "").replace("_", " ")


def _feature_coverage_r3_impl(feature_snapshot, *, facade):
    if not isinstance(feature_snapshot, dict) or not feature_snapshot:
        return {"present": 0, "total": 0, "coverage_ratio": 0.0, "quality": "missing", "present_keys": [], "missing_keys": []}
    key_fields = [
        "engine_ma20_gap",
        "engine_ma60",
        "engine_ma120",
        "engine_adx14",
        "engine_trend_strength",
        "engine_volume_spike20",
        "engine_volatility20",
        "engine_vwap_distance",
        "engine_sector_relative_strength",
        "engine_cross_section_rank",
        "engine_regime",
        "engine_signal_score",
    ]
    present: List[str] = []
    missing: List[str] = []
    for key in key_fields:
        value = feature_snapshot.get(key)
        if value is None:
            missing.append(key)
        else:
            present.append(key)
    total = len(key_fields)
    present_total = len(present)
    ratio = float(present_total) / float(total) if total else 0.0
    if ratio >= 0.75:
        quality = "strong"
    elif ratio >= 0.35:
        quality = "partial"
    else:
        quality = "missing"
    return {
        "present": present_total,
        "total": total,
        "coverage_ratio": ratio,
        "quality": quality,
        "present_keys": present,
        "missing_keys": missing,
    }


def _normalized_feature_coverage_r3_impl(reported, feature_snapshot, *, facade):
    computed = facade._feature_coverage(feature_snapshot)
    if not isinstance(reported, dict) or not reported:
        return computed
    present = facade._safe_int(reported.get("present"), facade._safe_int(computed.get("present"), 0))
    total = facade._safe_int(reported.get("total"), facade._safe_int(computed.get("total"), 0))
    ratio = facade._safe_float(reported.get("coverage_ratio"), (float(present) / float(total) if total else 0.0))
    quality = str(reported.get("quality") or "").strip().lower()
    if not quality:
        if total <= 0:
            quality = "missing"
        elif ratio >= 0.75:
            quality = "strong"
        elif ratio >= 0.35:
            quality = "partial"
        else:
            quality = "missing"
    return {
        "present": present,
        "total": total,
        "coverage_ratio": ratio,
        "quality": quality,
        "present_keys": list(reported.get("present_keys") or computed.get("present_keys") or []),
        "missing_keys": list(reported.get("missing_keys") or computed.get("missing_keys") or []),
    }


def _chart_filter_status_and_note_r3_impl(feature_coverage, *, facade):
    present = facade._safe_int(feature_coverage.get("present"), 0)
    total = facade._safe_int(feature_coverage.get("total"), 0)
    ratio = facade._safe_float(feature_coverage.get("coverage_ratio"), 0.0)
    if total <= 0:
        return "SKIPPED", "feature snapshot not available"
    if ratio >= 0.75:
        status = "PASS"
    elif ratio >= 0.5:
        status = "PARTIAL"
    else:
        status = "FAIL"
    return status, f"{present}/{total} filled"


def _quote_metrics_snapshot_r3_impl(feature_snapshot, *, facade):
    if not isinstance(feature_snapshot, dict) or not feature_snapshot:
        return {
            "present": False,
            "skill_quote_price": None,
            "quote_volume": None,
            "quote_trading_value": None,
            "intraday_change_pct": None,
        }
    price = feature_snapshot.get("skill_quote_price")
    volume = feature_snapshot.get("quote_volume")
    trading_value = feature_snapshot.get("quote_trading_value")
    change_pct = feature_snapshot.get("intraday_change_pct")
    return {
        "present": any(v is not None and v != 0 for v in (price, volume, trading_value, change_pct)),
        "skill_quote_price": price,
        "quote_volume": volume,
        "quote_trading_value": trading_value,
        "intraday_change_pct": change_pct,
    }


def _normalize_execution_payload_r3_impl(payload, *, facade):
    if not isinstance(payload, dict):
        return {
            "action": "",
            "symbol": "",
            "qty": 0,
            "status": "",
            "ord_no": "",
        }
    order = payload.get("order") if isinstance(payload.get("order"), dict) else {}
    broker = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
    response_payload = broker.get("response_payload") if isinstance(broker.get("response_payload"), dict) else {}
    return {
        "action": str(payload.get("action") or order.get("action") or "").upper(),
        "symbol": str(payload.get("symbol") or order.get("symbol") or order.get("stk_cd") or "").strip(),
        "qty": facade._safe_int(payload.get("qty"), facade._safe_int(order.get("qty"), facade._safe_int(order.get("ord_qty"), 0))),
        "status": str(payload.get("fill_status_summary") or payload.get("status") or broker.get("broker_message") or response_payload.get("return_msg") or ""),
        "ord_no": str(payload.get("ord_no") or broker.get("order_id") or response_payload.get("ord_no") or ""),
    }


def _clean_str_list_r3_impl(values, *, limit, max_len, facade):
    if not isinstance(values, list):
        return []
    out: List[str] = []
    for row in values:
        text = facade._trim_text(row, max_len=max_len)
        if text:
            out.append(text)
        if len(out) >= max(1, int(limit)):
            break
    return out


def _latest_evidence_r3_impl(rows, *, agent, stage, facade):
    for row in reversed(rows):
        if str(row.get("agent") or "").strip() != agent:
            continue
        if str(row.get("stage") or "").strip() != stage:
            continue
        return row
    return {}


def _count_stages_r3_impl(rows, *, facade):
    counts: Dict[str, int] = {}
    for row in rows:
        key = str(row.get("stage") or "").strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return counts
