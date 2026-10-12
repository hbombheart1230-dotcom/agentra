"""Operator period/symbol summary payload builders and period-key helpers (pure aggregation).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def build_operator_period_summary_r3_impl(*, reports_root, period_type, period_key, facade):
    normalized_type = str(period_type or "").strip().lower()
    if normalized_type == "weekly":
        normalized_key, start, end = facade._period_from_week(period_key)
    elif normalized_type == "monthly":
        normalized_key, start, end = facade._period_from_month(period_key)
    else:
        raise ValueError(f"unsupported period_type: {period_type!r}")

    rows: List[Dict[str, Any]] = []
    for row in facade._iter_symbol_trade_history(reports_root):
        row_day = facade._parse_day(row.get("date"))
        if row_day is None or row_day < start or row_day > end:
            continue
        rows.append(row)

    rows = facade._enrich_rows_with_truth_surface(rows, reports_root)
    metrics = facade._trade_metrics(rows)
    counters = facade._pattern_counters(rows)
    shadow_payloads = facade.load_quant_shadow_candidate_payloads_for_range(
        reports_root=reports_root,
        start=start.isoformat(),
        end=end.isoformat(),
    )

    summary = {
        "schema_version": "operator_period_summary.v1",
        "period_type": normalized_type,
        "period_key": normalized_key,
        "date_range": {"start": start.isoformat(), "end": end.isoformat()},
        "generated_at": facade._utc_now_iso(),
        "source": {
            "type": "operator_symbol_trade_history",
            "root": str(facade.operator_summary_artifact_root(reports_root) / "symbols"),
        },
        "metrics": {
            **metrics,
        },
        "patterns": facade._pattern_payload(counters),
        "pattern_performance": facade._pattern_performance_payload(rows),
        "quant_tactic_evaluation": facade.build_quant_tactic_evaluation(rows),
        "quant_shadow_candidate_evaluation": facade.build_quant_shadow_candidate_evaluation(shadow_payloads),
        "strategist_llm_evaluation": facade.build_strategist_llm_evaluation(rows, shadow_payloads),
        "symbol_summary": facade._symbol_rows(rows),
    }
    summary["operator_readout"] = facade._operator_readout(
        trade_count=len(rows),
        avg_return_pct=float(metrics.get("avg_return_pct") or 0.0),
        win_rate=float(metrics.get("win_rate") or 0.0),
        exit_counts=counters.get("exit_reasons") or facade.Counter(),
        entry_counts=counters.get("entry_reasons") or facade.Counter(),
    )
    return summary


def build_operator_symbol_summary_artifact_payload_r3_impl(
    *,
    reports_root,
    symbol,
    symbol_trade_report_payload,
    symbol_memory_payload,
    facade,
):
    normalized_symbol = str(symbol or "").strip().upper()
    payload = dict(symbol_trade_report_payload or {})
    history = payload.get("history_index") if isinstance(payload.get("history_index"), list) else []
    rows = [dict(row, symbol=normalized_symbol) for row in history if isinstance(row, dict)]
    rows = facade._enrich_rows_with_truth_surface(rows, reports_root)
    metrics = facade._trade_metrics(rows)
    counters = facade._pattern_counters(rows)
    days = sorted(
        {
            str(row.get("date") or row.get("day") or "")[:10]
            for row in rows
            if str(row.get("date") or row.get("day") or "").strip()
        }
    )
    shadow_payloads = facade.load_quant_shadow_candidate_payloads(reports_root=reports_root, days=days)
    pattern_insights = payload.get("pattern_insights") if isinstance(payload.get("pattern_insights"), dict) else {}
    memory = dict(symbol_memory_payload or {})

    summary = {
        "schema_version": "operator_symbol_summary.v1",
        "period_type": "symbol",
        "symbol": normalized_symbol,
        "generated_at": facade._utc_now_iso(),
        "source": {
            "type": "symbol_trade_report",
            "symbol_trade_report_json": str(facade.symbol_artifact_paths(reports_root, normalized_symbol)["symbol_trade_report_json"]),
            "symbol_memory_json": str(facade.symbol_artifact_paths(reports_root, normalized_symbol)["symbol_memory_json"]),
        },
        "metrics": metrics,
        "patterns": facade._pattern_payload(counters),
        "pattern_performance": facade._pattern_performance_payload(rows),
        "quant_tactic_evaluation": facade.build_quant_tactic_evaluation(rows),
        "quant_shadow_candidate_evaluation": facade.build_quant_shadow_candidate_evaluation(
            shadow_payloads,
            symbol=normalized_symbol,
        ),
        "strategist_llm_evaluation": facade.build_strategist_llm_evaluation(rows, shadow_payloads),
        "symbol_memory": {
            "available": bool(memory),
            "trade_stats": dict(memory.get("trade_stats") or {}) if isinstance(memory.get("trade_stats"), dict) else {},
            "bias_recommendation": dict(memory.get("bias_recommendation") or {}) if isinstance(memory.get("bias_recommendation"), dict) else {},
            "latest_snapshot": dict(memory.get("latest_snapshot") or {}) if isinstance(memory.get("latest_snapshot"), dict) else {},
        },
        "risk_notes": list(pattern_insights.get("risk_notes") or []),
    }
    summary["operator_readout"] = facade._operator_readout(
        trade_count=int(metrics.get("trade_count") or 0),
        avg_return_pct=float(metrics.get("avg_return_pct") or 0.0),
        win_rate=float(metrics.get("win_rate") or 0.0),
        exit_counts=counters.get("exit_reasons") or facade.Counter(),
        entry_counts=counters.get("entry_reasons") or facade.Counter(),
    )
    return summary


def _period_from_week_r3_impl(week, *, facade):
    text = str(week or "").strip()
    match = facade._WEEK_RE.match(text)
    if not match:
        raise ValueError(f"invalid week key: {text!r}; expected YYYY-Www")
    year = int(match.group(1))
    week_num = int(match.group(2))
    start = facade.date.fromisocalendar(year, week_num, 1)
    end = facade.date.fromisocalendar(year, week_num, 7)
    return f"{year:04d}-W{week_num:02d}", start, end


def _period_from_month_r3_impl(month, *, facade):
    text = str(month or "").strip()
    match = facade._MONTH_RE.match(text)
    if not match:
        raise ValueError(f"invalid month key: {text!r}; expected YYYY-MM")
    year = int(match.group(1))
    month_num = int(match.group(2))
    last_day = facade.calendar.monthrange(year, month_num)[1]
    return f"{year:04d}-{month_num:02d}", facade.date(year, month_num, 1), facade.date(year, month_num, last_day)


def _decision_is_weekend_carry_r3_impl(decision, *, facade):
    if bool(decision.get("weekend_carry")):
        return True
    calendar_ctx = decision.get("carry_calendar") if isinstance(decision.get("carry_calendar"), dict) else {}
    if bool(calendar_ctx.get("weekend_carry")):
        return True
    epoch = facade._safe_int(decision.get("decided_at_epoch"))
    if epoch <= 0:
        return False
    kst = facade.timezone(facade.timedelta(hours=9))
    try:
        return facade.datetime.fromtimestamp(epoch, tz=facade.timezone.utc).astimezone(kst).weekday() == 4
    except Exception:
        return False


def _is_carryover_exit_marker_r3_impl(row, *, facade):
    if facade._trade_action(row) != "SELL" and not facade._is_closed_trade(row):
        return False
    report_day = facade._row_report_day(row)
    trade_day = facade._trade_id_day(row.get("trade_id"))
    if report_day and trade_day and report_day != trade_day:
        return True
    for key in ("entry_ts", "entry_time", "entry_timestamp"):
        entry_day = str(row.get(key) or "").strip()[:10]
        if report_day and entry_day and entry_day != report_day:
            return True
    reason = f"{row.get('entry_reason') or ''} {row.get('exit_reason') or ''}".lower()
    return "carryover" in reason or "overnight" in reason or "recovered open position" in reason


def _find_key_recursive_r3_impl(source, key, *, max_nodes, facade):
    seen = 0
    stack = [source]
    while stack and seen < max_nodes:
        current = stack.pop()
        seen += 1
        if isinstance(current, dict):
            if key in current and current.get(key) not in (None, ""):
                return current.get(key)
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return None


def _iso_to_kst_dt_r3_impl(value, *, facade):
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        dt = facade.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=facade.timezone.utc)
    return dt.astimezone(facade.timezone(facade.timedelta(hours=9)))


def _epoch_to_kst_text_r3_impl(epoch, *, facade):
    value = facade._safe_int(epoch)
    if value <= 0:
        return ""
    try:
        kst = facade.timezone(facade.timedelta(hours=9))
        return facade.datetime.fromtimestamp(value, tz=facade.timezone.utc).astimezone(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    except Exception:
        return ""


def _epoch_day_kst_r3_impl(epoch, *, facade):
    value = facade._safe_int(epoch)
    if value <= 0:
        return ""
    try:
        kst = facade.timezone(facade.timedelta(hours=9))
        return facade.datetime.fromtimestamp(value, tz=facade.timezone.utc).astimezone(kst).strftime("%Y-%m-%d")
    except Exception:
        return ""


def _parse_day_r3_impl(value, *, facade):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return facade.date.fromisoformat(text[:10])
    except Exception:
        return None


def _trade_id_day_r3_impl(value, *, facade):
    text = str(value or "").strip()
    match = facade.re.match(r"^TRD_(\d{8})_", text)
    if not match:
        return ""
    raw = match.group(1)
    return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"


def _dig_r3_impl(source, *keys, facade):
    current: Any = source
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
