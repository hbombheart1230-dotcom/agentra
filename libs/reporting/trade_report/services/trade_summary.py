from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Mapping, Optional

from libs.llm.json_response import parse_llm_json_response
from libs.llm.model_catalog import build_execution_profile_observability
from libs.reporting.llm_artifacts import build_llm_response_artifact, classify_llm_exception, make_attempt
from libs.reporting.trade_report_ai_llm import run_trade_report_llm_attempts as _run_trade_report_llm_attempts_impl

def build_trade_summary_report_service(
    summary_input: Dict[str, Any],
    *,
    enabled: bool = False,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    retry_max_override: Optional[int] = None,
    timeout_sec_override: Optional[float] = None,
    hard_timeout_sec_override: Optional[float] = None,
    local_debug_no_llm: bool = False,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    """Trade-summary LLM evaluation service behind the compatibility façade."""

    _as_dict = deps["as_dict"]
    _resolve_intraday_report_model = deps["resolve_intraday_report_model"]
    _deterministic_trade_summary_report = deps["deterministic_trade_summary_report"]
    LLMRouter = deps["llm_router_cls"]
    _build_trade_summary_evaluation_messages = deps["build_trade_summary_evaluation_messages"]
    _router_chat_with_hard_timeout = deps["router_chat_with_hard_timeout"]
    _trade_summary_parse_meta = deps["trade_summary_parse_meta"]
    _normalize_trade_summary_evaluation = deps["normalize_trade_summary_evaluation"]
    AI_TRADE_SUMMARY_EVALUATION_KEYS = deps["required_keys"]

    source = summary_input if isinstance(summary_input, dict) else {}
    trade = _as_dict(source.get("trade"))
    trade_id = str(trade.get("trade_id") or source.get("trade_id") or "")
    run_id = str(source.get("run_id") or "")
    day = str(trade.get("day") or source.get("day") or "")
    chosen_model = _resolve_intraday_report_model(source, explicit_model=model)
    temp = float(temperature if temperature is not None else 0.1)
    token_budget = int(max_tokens if max_tokens is not None else 1200)
    retry_max = int(retry_max_override if retry_max_override is not None else 1)
    timeout_sec = float(timeout_sec_override if timeout_sec_override is not None else 12.0)
    hard_timeout_sec = (
        max(0.1, float(hard_timeout_sec_override))
        if hard_timeout_sec_override not in (None, "", 0)
        else None
    )
    empty_meta = {
        "parse_mode": "none",
        "required_keys_expected": list(AI_TRADE_SUMMARY_EVALUATION_KEYS),
        "required_keys_present": [],
        "required_keys_missing": list(AI_TRADE_SUMMARY_EVALUATION_KEYS),
        "completeness_score": 0.0,
    }
    if not enabled or local_debug_no_llm:
        reason = "local_debug_no_llm" if local_debug_no_llm else "summary_llm_disabled"
        artifact = build_llm_response_artifact(
            component="ai_trade_summary",
            run_id=run_id,
            trade_id=trade_id,
            story_id=trade_id,
            day=day,
            status="fallback",
            attempts=[],
            parsed_output={},
            model_info={"provider": "OpenRouter", "model": chosen_model or "openrouter/free"},
            meta={"reason": reason, **empty_meta},
        )
        return _deterministic_trade_summary_report(
            source,
            status="skipped",
            mode="local_debug" if local_debug_no_llm else "deterministic",
            model=chosen_model,
            reason=reason,
            llm_response_artifact=artifact,
        )

    router = LLMRouter.from_env()
    if router.client is None:
        artifact = build_llm_response_artifact(
            component="ai_trade_summary",
            run_id=run_id,
            trade_id=trade_id,
            story_id=trade_id,
            day=day,
            status="error",
            attempts=[],
            parsed_output={},
            model_info={"provider": "OpenRouter", "model": chosen_model or "openrouter/free"},
            meta={"reason": "OPENROUTER_API_KEY is not configured", "error": "llm_client_unavailable", **empty_meta},
        )
        return _deterministic_trade_summary_report(
            source,
            status="error",
            mode="ai",
            model=chosen_model,
            reason="OPENROUTER_API_KEY is not configured",
            llm_response_artifact=artifact,
        )

    resolved_model = str(
        router.resolve(
            "trade_report",
            policy={
                "temperature": temp,
                "max_tokens": max(600, token_budget),
                "timeout_sec": timeout_sec,
                **({"model": chosen_model} if chosen_model else {}),
            },
        ).model
    )
    attempts: List[Dict[str, Any]] = []
    current_messages = _build_trade_summary_evaluation_messages(source)
    current_policy = {
        "temperature": temp,
        "max_tokens": max(600, token_budget),
        "timeout_sec": timeout_sec,
        "response_format": {"type": "json_object"},
        **({"model": chosen_model} if chosen_model else {}),
    }
    raw = ""
    parsed_eval: Dict[str, Any] = {}
    final_status = "error"
    final_reason = ""
    final_error = ""
    final_latency_ms = 0
    parse_meta = dict(empty_meta)
    for attempt_index in range(max(0, retry_max) + 1):
        step = "primary" if attempt_index == 0 else f"retry_{attempt_index}"
        t0 = time.perf_counter()
        try:
            raw = _router_chat_with_hard_timeout(
                router,
                "trade_report",
                current_messages,
                policy=current_policy,
                hard_timeout_sec=hard_timeout_sec,
            )
        except Exception as exc:
            final_latency_ms = int((time.perf_counter() - t0) * 1000)
            final_status = classify_llm_exception(exc)
            final_error = f"{type(exc).__name__}:{exc}"
            final_reason = f"trade_summary_ai_exception:{final_error}"
            attempts.append(
                make_attempt(
                    step=step,
                    messages=current_messages,
                    raw_response_text=f"ERROR:{final_error}",
                    parsed_output={},
                    model=chosen_model or resolved_model,
                    latency_ms=final_latency_ms,
                    status=final_status,
                    meta={"role": "ai_trade_summary", "error": final_error, **empty_meta},
                )
            )
        else:
            final_latency_ms = int((time.perf_counter() - t0) * 1000)
            parse_result = parse_llm_json_response(raw)
            candidate = parse_result.get("full_object") if isinstance(parse_result.get("full_object"), dict) else parse_result.get("partial_object")
            candidate = dict(candidate) if isinstance(candidate, dict) else {}
            parse_meta = _trade_summary_parse_meta(raw, candidate) if candidate else dict(empty_meta)
            evaluation = _normalize_trade_summary_evaluation(candidate)
            missing = list(parse_meta.get("required_keys_missing") or [])
            if candidate and not missing:
                parsed_eval = evaluation
                final_status = "ok"
                final_reason = ""
                attempts.append(
                    make_attempt(
                        step=step,
                        messages=current_messages,
                        raw_response_text=raw,
                        parsed_output=evaluation,
                        model=chosen_model or resolved_model,
                        latency_ms=final_latency_ms,
                        status="ok",
                        meta={"role": "ai_trade_summary", **parse_meta},
                    )
                )
                break
            final_status = "partial" if candidate else "parse_error"
            final_reason = (
                f"trade_summary_ai response is missing required keys: {', '.join(missing)}"
                if candidate
                else "trade_summary_ai returned non-JSON response"
            )
            attempts.append(
                make_attempt(
                    step=step,
                    messages=current_messages,
                    raw_response_text=raw,
                    parsed_output=evaluation if candidate else {},
                    model=chosen_model or resolved_model,
                    latency_ms=final_latency_ms,
                    status=final_status,
                    meta={"role": "ai_trade_summary", "error": final_reason, **parse_meta},
                )
            )
        if attempt_index < retry_max:
            current_messages = _build_trade_summary_evaluation_messages(
                source,
                previous_response_text=raw[:1800],
                repair=True,
            )
            current_policy = {**current_policy, "temperature": 0.0}

    artifact = build_llm_response_artifact(
        component="ai_trade_summary",
        run_id=run_id,
        trade_id=trade_id,
        story_id=trade_id,
        day=day,
        status=final_status,
        attempts=attempts,
        parsed_output=parsed_eval,
        model_info={"provider": "OpenRouter", "model": chosen_model or resolved_model},
        latency_ms=sum(int(row.get("latency_ms") or 0) for row in attempts),
        meta={"reason": final_reason, "error": final_error, **parse_meta},
    )
    return _deterministic_trade_summary_report(
        source,
        status=final_status,
        mode="ai",
        model=chosen_model or resolved_model,
        reason=final_reason,
        evaluation=parsed_eval,
        llm_response_artifact=artifact,
    )


