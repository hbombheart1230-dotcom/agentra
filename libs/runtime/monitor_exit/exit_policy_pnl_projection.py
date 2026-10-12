"""Exit-policy pnl/guard evidence projections (pure; trigger precedence stays in evaluate_exit_policy).

Second Pass (P1.5) intra-function extraction from `libs/runtime/exit_policy.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def exit_pnl_hs_news_shock_th(out, hold_sec, has_explicit_time_stop, *, facade):
    max_hold_sec = int(out["thresholds"]["max_hold_sec"])
    time_stop_sec = int(out["thresholds"]["time_stop_sec"])
    hold_limit = time_stop_sec if time_stop_sec > 0 else max_hold_sec
    hs = None if hold_sec is None else max(0, int(hold_sec))
    out["hold_sec"] = hs
    time_limit_reason = "time_stop" if has_explicit_time_stop and time_stop_sec > 0 else "max_hold"
    time_limit_reached = bool(hold_limit > 0 and hs is not None and hs >= hold_limit)
    out["hold_limit_sec"] = int(hold_limit)
    out["max_hold_reached"] = bool(max_hold_sec > 0 and hs is not None and hs >= max_hold_sec)
    out["time_stop_reached"] = bool(time_stop_sec > 0 and hs is not None and hs >= time_stop_sec)
    out["time_limit_reached"] = bool(time_limit_reached)
    out["time_limit_reason"] = time_limit_reason if time_limit_reached else ""
    out["time_limit_reassessment_required"] = bool(time_limit_reached)
    out["time_limit_reassessment_blocked"] = False
    out["time_limit_reassessment_blocked_reason"] = ""

    # News shock exit (optional): sentiment crash forces immediate flattening.
    news_shock_th = float(out["thresholds"]["news_shock_threshold"])
    return (hs, news_shock_th, time_limit_reached, time_limit_reason)


def exit_pnl_apx_crosscheck(avg_price, p, price, q, out, *, facade):
    apx = facade._to_float(avg_price, 0.0) if avg_price is not None else 0.0
    crosscheck = facade._build_account_pnl_crosscheck(
        p,
        price=price,
        avg_price=avg_price,
        qty=q,
    )
    out["account_crosscheck"] = dict(crosscheck)
    out["raw_price"] = crosscheck.get("raw_price")
    out["effective_price"] = crosscheck.get("effective_price")
    out["effective_price_source"] = str(crosscheck.get("effective_price_source") or "")
    out["account_current_price"] = crosscheck.get("account_current_price")
    out["account_current_price_source"] = str(crosscheck.get("account_current_price_source") or "")
    out["account_unrealized_pnl"] = crosscheck.get("account_unrealized_pnl")
    out["account_mark_price"] = crosscheck.get("account_mark_price")
    out["account_mark_price_source"] = str(crosscheck.get("account_mark_price_source") or "")
    out["account_pnl_ratio"] = crosscheck.get("account_pnl_ratio")
    out["account_pnl_ratio_source"] = str(crosscheck.get("account_pnl_ratio_source") or "")
    out["raw_pnl_ratio"] = crosscheck.get("raw_pnl_ratio")
    out["effective_pnl_ratio"] = crosscheck.get("effective_pnl_ratio")
    out["pnl_crosscheck_gap"] = crosscheck.get("pnl_ratio_gap")
    out["price_crosscheck_gap"] = crosscheck.get("price_gap")
    out["pnl_crosscheck_applied"] = bool(crosscheck.get("applied"))
    out["pnl_crosscheck_reason"] = str(crosscheck.get("reason") or "")
    out["price_anomaly_flag"] = bool(crosscheck.get("price_anomaly_flag"))
    out["price_anomaly_reason"] = str(crosscheck.get("price_anomaly_reason") or "")
    out["pnl_fallback_applied"] = bool(crosscheck.get("pnl_fallback_applied"))
    out["fallback_price_source"] = str(crosscheck.get("fallback_price_source") or "")

    px = facade._to_float(crosscheck.get("effective_price"), 0.0) if crosscheck.get("effective_price") is not None else 0.0
    raw_px = facade._to_float(crosscheck.get("raw_price"), 0.0) if crosscheck.get("raw_price") is not None else 0.0
    technical_px = float(raw_px if raw_px > 0.0 else px)
    out["technical_price"] = float(technical_px) if technical_px > 0.0 else None
    out["technical_price_source"] = "raw_price" if raw_px > 0.0 else str(out.get("effective_price_source") or "")
    return (apx, crosscheck, px, technical_px)


def exit_pnl_gross_pnl_ratio_gross_profit_floor_gap_p(px, apx, crosscheck, technical_px, out, *, facade):
    pnl_ratio = float((px / apx) - 1.0)
    raw_pnl_ratio = crosscheck.get("raw_pnl_ratio")
    gross_pnl_ratio = (
        float(raw_pnl_ratio)
        if raw_pnl_ratio is not None
        else float((technical_px / apx) - 1.0)
        if technical_px > 0.0 and apx > 0.0
        else pnl_ratio
    )
    out["pnl_ratio"] = pnl_ratio
    out["gross_pnl_ratio"] = gross_pnl_ratio
    out["technical_pnl_ratio"] = gross_pnl_ratio
    out["effective_pnl_ratio"] = pnl_ratio
    out["stop_pnl_ratio"] = gross_pnl_ratio
    out["stop_pnl_ratio_source"] = str(out.get("technical_price_source") or "technical_price")
    out["hard_stop_pnl_ratio"] = pnl_ratio
    out["hard_stop_pnl_ratio_source"] = str(out.get("effective_price_source") or "effective_price")
    if pnl_ratio < gross_pnl_ratio - 1e-9:
        out["cost_drag_pressure"] = True
        out["cost_drag_pressure_pct"] = float(gross_pnl_ratio - pnl_ratio)
        out["cost_drag_pressure_reason"] = str(out.get("pnl_crosscheck_reason") or "effective_pnl_below_gross_pnl")
    profit_floor_pct = float(out["thresholds"].get("cost_aware_profit_floor_pct") or 0.0)
    profit_floor_enabled = bool(out["thresholds"].get("cost_aware_profit_floor_enabled")) and profit_floor_pct > 0.0
    round_trip_cost_floor_pct = float(out["thresholds"].get("round_trip_cost_floor_pct") or 0.0)
    min_expected_net_profit_pct = float(out["thresholds"].get("min_expected_net_profit_pct") or 0.0)
    gross_net_profit_ratio = float(gross_pnl_ratio - round_trip_cost_floor_pct)
    gross_profit_floor_gap_pct = (
        float(
            max(
                profit_floor_pct - gross_pnl_ratio,
                min_expected_net_profit_pct - gross_net_profit_ratio,
                0.0,
            )
        )
        if profit_floor_enabled
        else 0.0
    )
    gross_profit_floor_met = bool(
        (not profit_floor_enabled)
        or (
            gross_pnl_ratio >= profit_floor_pct
            and gross_net_profit_ratio >= min_expected_net_profit_pct
        )
    )
    out["gross_net_profit_ratio"] = float(gross_net_profit_ratio)
    out["gross_profit_floor_met"] = bool(gross_profit_floor_met)
    out["gross_profit_floor_gap_pct"] = float(gross_profit_floor_gap_pct)
    return (gross_pnl_ratio, gross_profit_floor_gap_pct, gross_profit_floor_met, min_expected_net_profit_pct, pnl_ratio, profit_floor_enabled, profit_floor_pct, round_trip_cost_floor_pct)


def exit_pnl_expected_exit_floor_blocked_profit_exit(out, technical_px, px, _first_positive_price, apx, round_trip_cost_floor_pct, profit_floor_enabled, profit_floor_pct, min_expected_net_profit_pct, gross_profit_floor_met, gross_profit_floor_gap_pct, gross_pnl_ratio, *, facade):
    expected_exit_price = 0.0
    expected_exit_source = ""
    expected_exit_fallback_used = False
    expected_exit_slippage_buffer_pct = float(out["thresholds"].get("sell_slippage_buffer_pct") or 0.0)
    # Profit exits are evaluated against executable/raw price context, not
    # account PnL marks that may already include fee/tax drag. Otherwise the
    # round-trip floor is effectively counted twice.
    observed_exit_price = float(technical_px if technical_px > 0.0 else px)
    best_bid, best_bid_source = _first_positive_price(
        "expected_exit_best_bid",
        "best_bid",
        "quote_best_bid",
        "bid",
        "bid_price",
    )
    if best_bid > 0.0:
        expected_exit_price = float(min(best_bid, observed_exit_price))
        expected_exit_source = str(best_bid_source)
    elif expected_exit_slippage_buffer_pct > 0.0 and observed_exit_price > 0.0:
        expected_exit_price = float(observed_exit_price * max(0.0, 1.0 - expected_exit_slippage_buffer_pct))
        expected_exit_source = "observed_price_minus_slippage_buffer"
        expected_exit_fallback_used = True
    elif observed_exit_price > 0.0:
        expected_exit_price = float(observed_exit_price)
        expected_exit_source = "observed_price"

    expected_exit_pnl_ratio = (
        float((expected_exit_price / apx) - 1.0)
        if expected_exit_price > 0.0 and apx > 0.0
        else None
    )
    expected_exit_net_pnl_ratio = (
        float(expected_exit_pnl_ratio - round_trip_cost_floor_pct)
        if expected_exit_pnl_ratio is not None
        else None
    )
    expected_exit_profit_floor_met = bool(not profit_floor_enabled)
    expected_exit_profit_floor_gap_pct = None
    if profit_floor_enabled and expected_exit_pnl_ratio is not None:
        expected_exit_profit_floor_met = bool(
            expected_exit_pnl_ratio >= profit_floor_pct
            and (
                expected_exit_net_pnl_ratio is None
                or expected_exit_net_pnl_ratio >= min_expected_net_profit_pct
            )
        )
        expected_exit_profit_floor_gap_pct = float(
            max(
                profit_floor_pct - expected_exit_pnl_ratio,
                min_expected_net_profit_pct - float(expected_exit_net_pnl_ratio or 0.0),
                0.0,
            )
        )
    floor_source = "expected_exit_pnl_ratio" if expected_exit_pnl_ratio is not None else "gross_pnl_ratio"
    cost_aware_profit_floor_met = (
        bool(expected_exit_profit_floor_met)
        if profit_floor_enabled
        and bool(out["thresholds"].get("cost_aware_profit_floor_use_expected_exit"))
        and expected_exit_pnl_ratio is not None
        else bool(gross_profit_floor_met)
    )
    expected_exit_floor_blocked = bool(
        profit_floor_enabled
        and bool(out["thresholds"].get("cost_aware_profit_floor_use_expected_exit"))
        and gross_profit_floor_met
        and not expected_exit_profit_floor_met
    )
    out["cost_aware_profit_floor_met"] = bool(cost_aware_profit_floor_met)
    out["cost_aware_profit_floor_source"] = str(floor_source if profit_floor_enabled else "disabled")
    if profit_floor_enabled:
        out["cost_aware_profit_floor_gap_pct"] = (
            expected_exit_profit_floor_gap_pct
            if (
                bool(out["thresholds"].get("cost_aware_profit_floor_use_expected_exit"))
                and expected_exit_pnl_ratio is not None
            )
            else gross_profit_floor_gap_pct
        )
    out["expected_exit_price"] = expected_exit_price if expected_exit_price > 0.0 else None
    out["expected_exit_price_source"] = expected_exit_source
    out["expected_exit_price_fallback_used"] = bool(expected_exit_fallback_used)
    out["expected_exit_slippage_buffer_pct"] = float(expected_exit_slippage_buffer_pct)
    out["expected_exit_pnl_ratio"] = expected_exit_pnl_ratio
    out["expected_exit_net_pnl_ratio"] = expected_exit_net_pnl_ratio
    out["expected_exit_profit_floor_met"] = bool(expected_exit_profit_floor_met)
    out["expected_exit_profit_floor_gap_pct"] = expected_exit_profit_floor_gap_pct
    out["expected_exit_profit_floor_blocked"] = bool(expected_exit_floor_blocked)
    if expected_exit_floor_blocked:
        out["expected_exit_profit_floor_blocked_reason"] = "expected_exit_price_below_cost_aware_floor"
    profit_exit_pnl_ratio = (
        float(expected_exit_pnl_ratio)
        if expected_exit_pnl_ratio is not None
        and bool(out["thresholds"].get("cost_aware_profit_floor_use_expected_exit"))
        else float(gross_pnl_ratio)
    )
    profit_exit_metric_name = (
        "expected_exit_pnl_ratio"
        if expected_exit_pnl_ratio is not None
        and bool(out["thresholds"].get("cost_aware_profit_floor_use_expected_exit"))
        else "gross_pnl_ratio"
    )
    out["profit_exit_pnl_ratio"] = float(profit_exit_pnl_ratio)
    out["profit_exit_metric_name"] = str(profit_exit_metric_name)
    return (expected_exit_floor_blocked, profit_exit_metric_name, profit_exit_pnl_ratio)


def exit_pnl_effective_stop_candidates_effective_stop(out, p, *, facade):
    sl = float(out["thresholds"]["stop_loss_pct"])
    hard_sl = float(out["thresholds"]["hard_stop_pct"])
    tp = float(out["thresholds"]["take_profit_pct"])
    etf_deviation_pct = facade.normalize_deviation_pct(p.get("etf_deviation_pct"))
    etf_deviation_source = str(p.get("etf_deviation_source") or "")
    out["etf_deviation_pct"] = etf_deviation_pct
    out["etf_deviation_source"] = etf_deviation_source
    etf_premium_score = facade.score_etf_deviation_for_exit(
        etf_deviation_pct,
        premium_trigger_pct=float(out["thresholds"].get("etf_premium_take_profit_pct") or facade.DEFAULT_PREMIUM_TRIGGER_PCT),
    )
    out["etf_premium_take_profit_score"] = float(etf_premium_score)

    effective_stop_candidates = [
        (reason, threshold)
        for reason, threshold in (
            ("hard_stop", hard_sl),
            ("stop_loss", sl),
        )
        if threshold > 0.0
    ]
    effective_stop_reason = ""
    effective_stop_pct = 0.0
    return (effective_stop_candidates, effective_stop_pct, effective_stop_reason, etf_deviation_pct, etf_deviation_source, hard_sl, sl, tp)
