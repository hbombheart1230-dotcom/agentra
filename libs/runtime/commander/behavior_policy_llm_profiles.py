"""Commander behavior policy: LLM execution profiles for default, strategist and reporter.

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `graphs/commander_runtime.py::_resolve_commander_behavior_policy` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def build_llm_behavior_policy(default_execution_profile, reporter_daily_execution_profile, reporter_daily_llm, reporter_intraday_execution_profile, reporter_intraday_llm, strategist_execution_profile, strategist_llm, *, facade):
    return (
        {
            "execution_profile": {
                "profile_name": str(default_execution_profile.get("profile_name") or default_execution_profile.get("name") or "default_intraday"),
                "name": str(default_execution_profile.get("name") or "default_intraday"),
                "temperature": float(facade._runtime_float(default_execution_profile.get("temperature"), 0.2)),
                "max_tokens": max(256, facade._coerce_int(default_execution_profile.get("max_tokens"), 8192)),
                "timeout_sec": max(1, facade._coerce_int(default_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, facade._coerce_int((default_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(facade._runtime_float((default_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                    "retry_max": max(0, facade._coerce_int((default_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                    "retry_backoff_sec": max(0.0, float(facade._runtime_float((default_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    "policy_source": "commander_applied_policy",
                },
            "strategist": {
                "profile": str(strategist_llm.get("profile") or "balanced"),
                "primary": str(strategist_llm.get("primary") or ""),
                "fallback": str(strategist_llm.get("fallback") or ""),
                "execution_profile": {
                    "profile_name": str(strategist_execution_profile.get("profile_name") or strategist_execution_profile.get("name") or "balanced_reasoning"),
                    "name": str(strategist_execution_profile.get("name") or "balanced_reasoning"),
                    "temperature": float(facade._runtime_float(strategist_execution_profile.get("temperature"), 0.1)),
                    "max_tokens": max(256, facade._coerce_int(strategist_execution_profile.get("max_tokens"), 8192)),
                    "timeout_sec": max(1, facade._coerce_int(strategist_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, facade._coerce_int((strategist_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(facade._runtime_float((strategist_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                    "retry_max": max(0, facade._coerce_int(strategist_execution_profile.get("retry_max"), 2)),
                    "retry_backoff_sec": max(0.0, float(facade._runtime_float(strategist_execution_profile.get("retry_backoff_sec"), 0.0))),
                    "policy_source": "commander_applied_policy",
                },
                "policy_source": "commander_applied_policy",
            },
            "reporter": {
                "intraday": {
                    "profile": str(reporter_intraday_llm.get("profile") or "fast_free"),
                    "primary": str(reporter_intraday_llm.get("primary") or ""),
                    "fallback": str(reporter_intraday_llm.get("fallback") or ""),
                    "execution_profile": {
                        "profile_name": str(reporter_intraday_execution_profile.get("profile_name") or reporter_intraday_execution_profile.get("name") or "concise_review"),
                        "name": str(reporter_intraday_execution_profile.get("name") or "concise_review"),
                        "temperature": float(facade._runtime_float(reporter_intraday_execution_profile.get("temperature"), 0.2)),
                        "max_tokens": max(256, facade._coerce_int(reporter_intraday_execution_profile.get("max_tokens"), 8192)),
                        "timeout_sec": max(1, facade._coerce_int(reporter_intraday_execution_profile.get("timeout_sec"), 15)),
                        "retry": {
                            "max_attempts": max(0, facade._coerce_int((reporter_intraday_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                            "backoff_sec": max(0.0, float(facade._runtime_float((reporter_intraday_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                        },
                        "retry_max": max(0, facade._coerce_int(reporter_intraday_execution_profile.get("retry_max"), 2)),
                        "retry_backoff_sec": max(0.0, float(facade._runtime_float(reporter_intraday_execution_profile.get("retry_backoff_sec"), 0.0))),
                        "policy_source": "commander_applied_policy",
                    },
                    "policy_source": "commander_applied_policy",
                },
                "daily": {
                    "profile": str(reporter_daily_llm.get("profile") or "strong_reasoning"),
                    "primary": str(reporter_daily_llm.get("primary") or ""),
                    "fallback": str(reporter_daily_llm.get("fallback") or ""),
                    "execution_profile": {
                        "profile_name": str(reporter_daily_execution_profile.get("profile_name") or reporter_daily_execution_profile.get("name") or "deep_review"),
                        "name": str(reporter_daily_execution_profile.get("name") or "deep_review"),
                        "temperature": float(facade._runtime_float(reporter_daily_execution_profile.get("temperature"), 0.2)),
                        "max_tokens": max(256, facade._coerce_int(reporter_daily_execution_profile.get("max_tokens"), 8192)),
                        "timeout_sec": max(1, facade._coerce_int(reporter_daily_execution_profile.get("timeout_sec"), 15)),
                        "retry": {
                            "max_attempts": max(0, facade._coerce_int((reporter_daily_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                            "backoff_sec": max(0.0, float(facade._runtime_float((reporter_daily_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                        },
                        "retry_max": max(0, facade._coerce_int(reporter_daily_execution_profile.get("retry_max"), 2)),
                        "retry_backoff_sec": max(0.0, float(facade._runtime_float(reporter_daily_execution_profile.get("retry_backoff_sec"), 0.0))),
                        "policy_source": "commander_applied_policy",
                    },
                    "policy_source": "commander_applied_policy",
                },
            },
        }
    )

def build_strategist_behavior_policy(allow_legacy_rule, allow_legacy_strategy_v1, feedback_policy, memory_feedback_enabled, performance_memory_enabled, strategist_memory_usage_disabled, strategy_memory_persist_enabled, strategy_memory_recent_runs, strict_mode, *, facade):
    return (
        {
            "runtime": {
                "strict_mode": bool(strict_mode),
                "allow_legacy_rule": bool(allow_legacy_rule),
                "allow_legacy_strategy_v1": bool(allow_legacy_strategy_v1),
                "policy_source": "commander_applied_policy",
            },
            "memory_feedback": {
                "enabled": bool(memory_feedback_enabled),
                "recent_runs": max(1, facade._coerce_int(strategy_memory_recent_runs, 12)),
                "policy_source": "commander_applied_policy",
            },
            "performance_memory": {
                "enabled": bool(performance_memory_enabled),
                "persist_enabled": bool(strategy_memory_persist_enabled),
                "policy_source": "commander_applied_policy",
            },
            "memory_usage": {
                "disabled": bool(strategist_memory_usage_disabled),
                "policy_source": "commander_applied_policy",
            },
            "reporter_feedback_mode": str(feedback_policy.get("reporter_feedback_mode") or "auto"),
            "reporter_feedback_mode_source": str(
                feedback_policy.get("reporter_feedback_mode_source") or "commander_applied_policy"
            ),
            "reporter_feedback_mode_reason": str(feedback_policy.get("reporter_feedback_mode_reason") or ""),
            "reporter_feedback_semantics": "advisory_only",
        }
    )
