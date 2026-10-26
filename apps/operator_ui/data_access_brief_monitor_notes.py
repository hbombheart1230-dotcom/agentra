"""Operator Brief Monitor stop-policy trace, threshold shortfall and watch-axis notes (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _brief_build_stop_policy_trace_r3_impl(monitor, *, facade):
    data = monitor if isinstance(monitor, dict) else {}
    policy_trace = data.get("monitor_stop_policy_trace") if isinstance(data.get("monitor_stop_policy_trace"), dict) else {}
    adaptive_exit = data.get("adaptive_exit") if isinstance(data.get("adaptive_exit"), dict) else {}
    policy_ref = data.get("policy_ref") if isinstance(data.get("policy_ref"), dict) else {}
    decision_trace = data.get("decision_trace") if isinstance(data.get("decision_trace"), dict) else {}
    decision_policy_ref = decision_trace.get("policy_ref") if isinstance(decision_trace.get("policy_ref"), dict) else {}
    strategist_adaptive_exit = (
        (policy_ref.get("exit_plan") or {}).get("adaptive_exit")
        if isinstance((policy_ref.get("exit_plan") or {}).get("adaptive_exit"), dict)
        else {}
    )
    if not strategist_adaptive_exit:
        strategist_adaptive_exit = (
            (decision_policy_ref.get("exit_plan") or {}).get("adaptive_exit")
            if isinstance((decision_policy_ref.get("exit_plan") or {}).get("adaptive_exit"), dict)
            else {}
        )
    hard_stop_pct = data.get("hard_stop_pct")
    if hard_stop_pct in (None, ""):
        hard_stop_pct = policy_trace.get("hard_stop_pct")
    adaptive_stop_loss_pct = data.get("adaptive_stop_loss_pct")
    if adaptive_stop_loss_pct in (None, ""):
        adaptive_stop_loss_pct = adaptive_exit.get("stop_loss_pct")
    if adaptive_stop_loss_pct in (None, ""):
        adaptive_stop_loss_pct = policy_trace.get("adaptive_stop_loss_pct")
    effective_stop_loss_pct = data.get("effective_stop_loss_pct")
    if effective_stop_loss_pct in (None, ""):
        effective_stop_loss_pct = (
            policy_trace.get("effective_stop_loss_pct")
            if policy_trace.get("effective_stop_loss_pct") not in (None, "")
            else adaptive_stop_loss_pct
            if adaptive_stop_loss_pct not in (None, "")
            else hard_stop_pct
        )
    trailing_stop_pct = data.get("trailing_stop_pct")
    if trailing_stop_pct in (None, ""):
        trailing_stop_pct = policy_trace.get("trailing_stop_pct")
    take_profit_pct = data.get("take_profit_pct")
    if take_profit_pct in (None, ""):
        take_profit_pct = policy_trace.get("take_profit_pct")
    return {
        "hard_stop_pct": hard_stop_pct,
        "adaptive_stop_loss_pct": adaptive_stop_loss_pct,
        "effective_stop_loss_pct": effective_stop_loss_pct,
        "trailing_stop_pct": trailing_stop_pct,
        "take_profit_pct": take_profit_pct,
        "strategist_baseline_stop_loss_pct": strategist_adaptive_exit.get("stop_loss_pct")
        if strategist_adaptive_exit.get("stop_loss_pct") not in (None, "")
        else policy_trace.get("strategist_baseline_stop_loss_pct"),
        "strategist_baseline_take_profit_pct": strategist_adaptive_exit.get("take_profit_pct")
        if strategist_adaptive_exit.get("take_profit_pct") not in (None, "")
        else policy_trace.get("strategist_baseline_take_profit_pct"),
        "strategist_baseline_trailing_stop_pct": strategist_adaptive_exit.get("trailing_stop_pct")
        if strategist_adaptive_exit.get("trailing_stop_pct") not in (None, "")
        else policy_trace.get("strategist_baseline_trailing_stop_pct"),
    }


def _monitor_threshold_shortfall_notes_r3_impl(entry_metrics, entry_thresholds, *, facade):
    metrics = entry_metrics if isinstance(entry_metrics, dict) else {}
    thresholds = entry_thresholds if isinstance(entry_thresholds, dict) else {}
    notes: List[str] = []

    volume_ratio = metrics.get("volume_ratio")
    volume_ratio_min = thresholds.get("volume_ratio_min")
    if volume_ratio not in (None, "") and volume_ratio_min not in (None, ""):
        actual = facade._safe_float(volume_ratio)
        limit = facade._safe_float(volume_ratio_min)
        if actual < limit:
            notes.append(f"volume_ratio {actual:.3f} < min {limit:.3f}")

    extended_from_vwap_pct = metrics.get("extended_from_vwap_pct")
    max_extended_from_vwap_pct = thresholds.get("max_extended_from_vwap_pct")
    if extended_from_vwap_pct not in (None, "") and max_extended_from_vwap_pct not in (None, ""):
        actual = facade._safe_float(extended_from_vwap_pct)
        limit = facade._safe_float(max_extended_from_vwap_pct)
        if actual > limit:
            notes.append(f"extended_from_vwap_pct {actual:.3f} > max {limit:.3f}")

    pullback_depth_pct = metrics.get("pullback_depth_pct")
    pullback_min_pct = thresholds.get("pullback_min_pct")
    if pullback_depth_pct not in (None, "") and pullback_min_pct not in (None, ""):
        actual = facade._safe_float(pullback_depth_pct)
        limit = facade._safe_float(pullback_min_pct)
        if actual < limit:
            notes.append(f"pullback_depth_pct {actual:.3f} < min {limit:.3f}")

    return notes[:6]


def _monitor_watch_axes_r3_impl(thresholds, *, facade):
    if not isinstance(thresholds, dict):
        return []
    out: List[str] = []
    if facade._safe_float(thresholds.get("hard_stop_pct"), 0.0) > 0.0:
        out.append("Hard stop")
    if facade._safe_float(thresholds.get("effective_stop_loss_pct"), 0.0) > 0.0:
        reason = facade._friendly_exit_reason(thresholds.get("effective_stop_reason") or "stop_loss")
        out.append(reason)
    if facade._safe_float(thresholds.get("take_profit_pct"), 0.0) > 0.0:
        out.append("Take profit")
    if facade._safe_float(thresholds.get("peak_drawdown_exit_pct"), 0.0) > 0.0:
        out.append("Peak drawdown")
    if facade._safe_float(thresholds.get("vwap_breakdown_pct"), 0.0) > 0.0:
        out.append("VWAP breakdown")
    if facade._safe_float(thresholds.get("intraday_low_break_pct"), 0.0) > 0.0:
        out.append("Intraday low break")
    if facade._safe_float(thresholds.get("trend_strength_floor"), 0.0) > 0.0:
        out.append("Trend breakdown")
    if facade._safe_float(thresholds.get("trailing_stop_pct"), 0.0) > 0.0:
        out.append("Trailing stop")
    if facade._safe_float(thresholds.get("vol_expansion_ratio"), 0.0) > 0.0:
        out.append("Volatility expansion")
    seen: List[str] = []
    for item in out:
        if item not in seen:
            seen.append(item)
    return seen[:6]


def _monitor_row_summary_r3_impl(monitor_summary, monitor_trace, *, facade):
    summary = monitor_summary if isinstance(monitor_summary, dict) else {}
    trace = monitor_trace if isinstance(monitor_trace, dict) else {}
    thresholds = trace.get("thresholds") if isinstance(trace.get("thresholds"), dict) else {}
    live_monitor_reason = str(summary.get("monitor_reason") or trace.get("monitor_reason") or "").strip()
    live_exit_reason = str(summary.get("exit_reason") or trace.get("exit_reason") or "").strip()
    effective_stop_loss = thresholds.get("effective_stop_loss_pct")
    peak_drawdown_raw = trace.get("peak_drawdown")
    if peak_drawdown_raw in (None, ""):
        peak_drawdown_raw = summary.get("peak_drawdown")
    return {
        "active_exit_axis": facade._friendly_exit_reason(live_exit_reason or str(thresholds.get("effective_stop_reason") or "").strip() or live_monitor_reason or "hold"),
        "effective_stop": facade._format_percent(effective_stop_loss, 2) if effective_stop_loss not in (None, "") else "-",
        "peak_drawdown": facade._format_percent(peak_drawdown_raw, 2) if peak_drawdown_raw not in (None, "") else "-",
        "watch_axes": facade._monitor_watch_axes(thresholds),
    }


def _should_replace_brief_monitor_summary_r3_impl(detail, summary_text, *, facade):
    raw = str(summary_text or "").strip().lower()
    if not raw:
        return True
    if "no_position" not in raw and "포지션 없음" not in raw:
        return False
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    lifecycle_status = str(trade_report.get("lifecycle_status") or "").strip().lower()
    report_action = str(trade_report.get("action") or "").strip().upper()
    executor = detail.get("executor") if isinstance(detail.get("executor"), dict) else {}
    execution = executor.get("execution") if isinstance(executor.get("execution"), dict) else {}
    execution_action = str(execution.get("action") or "").strip().upper()
    if lifecycle_status == "open" and (report_action == "BUY" or execution_action == "BUY"):
        return True
    if lifecycle_status == "closed" and (report_action == "SELL" or execution_action == "SELL"):
        return True
    return False


def _prefer_richer_brief_text_r3_impl(primary, fallback, *, min_primary_len, facade):
    cleaned_primary = facade._sanitize_operator_brief_text(primary)
    cleaned_fallback = facade._sanitize_operator_brief_text(fallback)
    if not cleaned_primary:
        return cleaned_fallback
    if not cleaned_fallback:
        return cleaned_primary
    primary_hangul = facade._count_hangul_chars(cleaned_primary) > 0
    fallback_hangul = facade._count_hangul_chars(cleaned_fallback) > 0
    if fallback_hangul and not primary_hangul and len(cleaned_fallback) >= len(cleaned_primary) + 16:
        return cleaned_fallback
    if len(cleaned_primary) < min_primary_len and len(cleaned_fallback) >= len(cleaned_primary) + 20:
        return cleaned_fallback
    return cleaned_primary


def _strategist_nested_value_r3_impl(payload, key, *, facade):
    if not isinstance(payload, dict):
        return None

    def _lookup(container: Any) -> Any:
        if not isinstance(container, dict):
            return None
        value = container.get(key)
        return value if facade._filled_strategy_scalar(value) else None

    section_names = (
        "summary",
        "trace_summary",
        "strategist_trace_summary",
        "strategy_frame",
        "policy_selected",
        "decision_frame",
        "market_context",
        "llm_frame",
    )
    containers: List[Any] = [payload]
    containers.extend(payload.get(name) for name in section_names)
    artifact = payload.get("artifact")
    if isinstance(artifact, dict):
        containers.append(artifact)
        containers.extend(artifact.get(name) for name in section_names)

    for container in containers:
        value = _lookup(container)
        if value is not None:
            return value
    return None


def _strategist_risk_tone_r3_impl(payload, *, facade):
    value = facade._strategist_nested_value(payload, "risk_tone")
    if value is None:
        value = facade._strategist_nested_value(payload, "risk_mode")
    return str(value or "").strip()


def _strategist_monitor_guidance_r3_impl(payload, *, facade):
    value = facade._strategist_nested_value(payload, "monitor_guidance")
    return str(value or "").strip()
