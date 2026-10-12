"""Commander behavior-policy route/execution/stop/size normalization (same fallbacks).

Second Pass (P1.5) intra-function extraction from `graphs/commander_runtime.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def behavior_norm_carry_risk_bias_carry_risk_reason(_existing_value, commander_override, *, facade):
    position_sizing_min_qty = _existing_value("monitor", "entry", "position_sizing", "min_position_qty")
    if position_sizing_min_qty is None:
        position_sizing_min_qty = 1
    position_sizing_lot_size = _existing_value("monitor", "entry", "position_sizing", "lot_size")
    if position_sizing_lot_size is None:
        position_sizing_lot_size = 1
    strategy_memory_recent_runs = _existing_value("strategist", "memory_feedback", "recent_runs")
    if strategy_memory_recent_runs is None:
        strategy_memory_recent_runs = 12
    strategist_llm_profile = str(_existing_value("llm", "strategist", "profile") or "balanced").strip().lower() or "balanced"
    reporter_intraday_profile = str(_existing_value("llm", "reporter", "intraday", "profile") or "fast_free").strip().lower() or "fast_free"
    reporter_daily_profile = str(_existing_value("llm", "reporter", "daily", "profile") or "strong_reasoning").strip().lower() or "strong_reasoning"
    strategist_llm = facade.resolve_model_profile(strategist_llm_profile, default_profile="balanced")
    reporter_intraday_llm = facade.resolve_model_profile(reporter_intraday_profile, default_profile="fast_free")
    reporter_daily_llm = facade.resolve_model_profile(reporter_daily_profile, default_profile="strong_reasoning")
    default_execution_profile_name = (
        str(
            _existing_value("llm", "execution_profile", "profile_name")
            or _existing_value("llm", "execution_profile", "name")
            or "default_intraday"
        ).strip().lower()
        or "default_intraday"
    )
    default_execution_profile = facade.resolve_execution_profile(
        default_execution_profile_name,
        default_profile="default_intraday",
        defaults={
            "profile_name": "default_intraday",
            "name": "default_intraday",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": 15,
            "retry": {"max_attempts": 2, "backoff_sec": 0.0},
            "retry_max": 2,
            "retry_backoff_sec": 0.0,
        },
    )
    strategist_execution_profile_name = (
        str(_existing_value("llm", "strategist", "execution_profile", "name") or "balanced_reasoning").strip().lower()
        or "balanced_reasoning"
    )
    reporter_intraday_execution_profile_name = (
        str(_existing_value("llm", "reporter", "intraday", "execution_profile", "name") or "concise_review").strip().lower()
        or "concise_review"
    )
    reporter_daily_execution_profile_name = (
        str(_existing_value("llm", "reporter", "daily", "execution_profile", "name") or "deep_review").strip().lower()
        or "deep_review"
    )
    strategist_execution_profile = facade.resolve_execution_profile(
        strategist_execution_profile_name,
        default_profile="balanced_reasoning",
        defaults={
            "profile_name": "balanced_reasoning",
            "name": "balanced_reasoning",
            "temperature": 0.1,
            "max_tokens": 8192,
            "timeout_sec": 15,
            "retry": {
                "max_attempts": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
                "backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
            },
            "retry_max": 2,
            "retry_backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
        },
    )
    reporter_intraday_execution_profile = facade.resolve_execution_profile(
        reporter_intraday_execution_profile_name,
        default_profile="concise_review",
        defaults={
            "profile_name": "concise_review",
            "name": "concise_review",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": max(1, facade._coerce_int(default_execution_profile.get("timeout_sec"), 15)),
            "retry": {
                "max_attempts": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
                "backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
            },
            "retry_max": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
            "retry_backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
        },
    )
    reporter_daily_execution_profile = facade.resolve_execution_profile(
        reporter_daily_execution_profile_name,
        default_profile="deep_review",
        defaults={
            "profile_name": "deep_review",
            "name": "deep_review",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": max(1, facade._coerce_int(default_execution_profile.get("timeout_sec"), 15)),
            "retry": {
                "max_attempts": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
                "backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
            },
            "retry_max": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
            "retry_backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
        },
    )
    carry_state = str(commander_override.get("carry_state") or "").strip().lower()
    carry_risk_bias = str(commander_override.get("carry_risk_bias") or "").strip().lower()
    carry_risk_reason = str(commander_override.get("carry_risk_reason") or "")
    override_reason = str(commander_override.get("override_reason") or "").strip().lower()
    hold_repeat_count_max = max(0, facade._coerce_int(commander_override.get("hold_repeat_count_max"), 0))
    return (carry_risk_bias, carry_risk_reason, carry_state, default_execution_profile, hold_repeat_count_max, override_reason, position_sizing_lot_size, position_sizing_min_qty, reporter_daily_execution_profile, reporter_daily_llm, reporter_intraday_execution_profile, reporter_intraday_llm, strategist_execution_profile, strategist_llm, strategy_memory_recent_runs)
