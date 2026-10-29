"""Pure Commander shadow advisory projections."""


def no_trade_reason_code(state, *, observations, actual_runtime, path, facade):
    monitor = facade._dict(state.get("monitor"))
    monitor_entry = facade._dict(state.get("monitor_entry"))
    monitor_output = facade._dict(state.get("monitor_output"))
    execution = facade._dict(state.get("execution"))
    portfolio_preflight = facade._dict(state.get("portfolio_preflight"))
    runtime_fast_path = facade._dict(state.get("runtime_fast_path"))
    strategist_llm = facade._dict(state.get("strategist_llm"))
    selected = facade._dict(state.get("selected"))
    symbol = facade._clip(selected.get("symbol") or monitor_output.get("selected_symbol"), max_len=24)

    monitor_decision = facade._clip(actual_runtime.get("monitor_decision"), max_len=24).upper()
    executor_action = facade._clip(actual_runtime.get("executor_action"), max_len=24).upper()
    if monitor_decision in {"BUY", "SELL"} or executor_action in {"BUY", "SELL"}:
        return "NONE"
    if facade._safe_int(monitor.get("open_position_count"), 0) > 0 and (bool(monitor.get("buy_blocked_open_position")) or "monitor_only" in str(path or "")):
        return "POSITION_ALREADY_OPEN"
    if bool(portfolio_preflight.get("blocked")) or facade._clip(state.get("decision_reason"), max_len=80) in {"risk_too_high", "portfolio_preflight_blocked"}:
        return "RISK_BLOCKED"
    if execution and execution.get("allowed") is False:
        reason = facade._clip(execution.get("reason"), max_len=120).lower()
        if reason not in {"", "noop_intent_skipped"}:
            return "EXECUTION_BLOCKED"
    failed_checks = [str(x or "").strip().lower() for x in list(monitor_entry.get("failed_checks") or []) if str(x or "").strip()]
    combined_reason = " ".join([facade._clip(monitor_entry.get("guard_reason"), max_len=120), facade._clip(monitor_entry.get("reason"), max_len=120), facade._clip(monitor_output.get("entry_exit_reason"), max_len=120)]).strip().lower()
    if any(token in combined_reason for token in ("minute_candle_missing", "data_incomplete", "insufficient_data", "missing_data")):
        return "DATA_INSUFFICIENT"
    if any(token in failed_checks for token in ("data_incomplete", "minute_candle_missing", "vwap_missing", "volume_missing")):
        return "DATA_INSUFFICIENT"
    if not symbol and not combined_reason and not failed_checks and not execution and not strategist_llm:
        return "DATA_INSUFFICIENT"
    llm_status = facade._clip(strategist_llm.get("status") or strategist_llm.get("llm_status"), max_len=40).lower()
    if bool(strategist_llm.get("blocked")) or llm_status in {"error", "fallback"}:
        return "LLM_UNSTABLE"
    if observations.get("repeated_same_context") is True:
        return "REPEATED_SAME_CONTEXT"
    if observations.get("market_changed") is False or facade._clip(runtime_fast_path.get("reason"), max_len=80) == "flat_position_cached_strategist":
        return "NO_MARKET_CHANGE"
    confidence = selected.get("confidence")
    try:
        confidence_value = float(confidence)
    except Exception:
        confidence_value = None
    if confidence_value is not None and confidence_value < 0.55:
        return "LOW_CONFIDENCE"
    if failed_checks or any(token in combined_reason for token in ("confirmation", "too_extended", "breakout", "pullback", "reclaim", "entry_wait", "wait")):
        return "WAIT_FOR_CONFIRMATION"
    if combined_reason:
        return "LOW_SIGNAL_QUALITY"
    return "NONE"


def strategist_recommendation(*, no_trade_reason_code, observations):
    llm_status = str(observations.get("last_llm_status") or "").strip().lower()
    if no_trade_reason_code in {"POSITION_ALREADY_OPEN", "NO_MARKET_CHANGE", "REPEATED_SAME_CONTEXT", "DATA_INSUFFICIENT", "WAIT_FOR_CONFIRMATION", "LOW_SIGNAL_QUALITY", "LOW_CONFIDENCE", "RISK_BLOCKED", "EXECUTION_BLOCKED"}:
        return "SKIP"
    if no_trade_reason_code == "LLM_UNSTABLE":
        if llm_status in {"partial", "salvaged", "repaired"}:
            return "RETRY_COMPACT"
        if llm_status == "fallback":
            return "USE_FALLBACK"
        if llm_status == "error":
            return "RETRY_MINIMAL"
    return "RUN"
