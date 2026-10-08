from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Mapping, Optional

from libs.llm.json_response import parse_llm_json_response
from libs.llm.model_catalog import build_execution_profile_observability
from libs.reporting.llm_artifacts import build_llm_response_artifact, classify_llm_exception, make_attempt
from libs.reporting.trade_report_ai_llm import run_trade_report_llm_attempts as _run_trade_report_llm_attempts_impl


def build_ai_trade_report_service(
    story_input: Dict[str, Any],
    *,
    enabled: Optional[bool] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    retry_max_override: Optional[int] = None,
    timeout_sec_override: Optional[float] = None,
    hard_timeout_sec_override: Optional[float] = None,
    local_debug_no_llm: bool = False,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    """AI trade-report service implementation behind the compatibility façade."""

    _resolve_intraday_report_model = deps["resolve_intraday_report_model"]
    _resolve_intraday_report_execution_profile = deps["resolve_intraday_report_execution_profile"]
    _failure_report = deps["failure_report"]
    _attach_report_status_matrix = deps["attach_report_status_matrix"]
    _fallback_report = deps["fallback_report"]
    LLMRouter = deps["llm_router_cls"]
    _build_messages = deps["build_messages"]
    _router_chat_with_hard_timeout = deps["router_chat_with_hard_timeout"]
    _trade_report_parse_meta = deps["trade_report_parse_meta"]
    _trade_report_language_meta = deps["trade_report_language_meta"]
    _build_repair_messages = deps["build_repair_messages"]
    _merge_trade_report_candidate = deps["merge_trade_report_candidate"]
    AI_TRADE_REPORT_REQUIRED_KEYS = deps["required_keys"]

    if enabled is None:
        applied_policy = story_input.get("applied_policy") if isinstance(story_input.get("applied_policy"), dict) else {}
        reporter_policy = applied_policy.get("reporter") if isinstance(applied_policy.get("reporter"), dict) else {}
        trade_report_policy = reporter_policy.get("trade_report") if isinstance(reporter_policy.get("trade_report"), dict) else {}
        commander = story_input.get("commander") if isinstance(story_input.get("commander"), dict) else {}
        commander_policy = commander.get("applied_policy") if isinstance(commander.get("applied_policy"), dict) else {}
        commander_reporter = commander_policy.get("reporter") if isinstance(commander_policy.get("reporter"), dict) else {}
        commander_trade_report = (
            commander_reporter.get("trade_report")
            if isinstance(commander_reporter.get("trade_report"), dict)
            else {}
        )
        reporter_fallback = story_input.get("reporter_policy") if isinstance(story_input.get("reporter_policy"), dict) else {}
        trade_report_fallback = (
            reporter_fallback.get("trade_report")
            if isinstance(reporter_fallback.get("trade_report"), dict)
            else {}
        )
        if trade_report_policy.get("enabled") is not None:
            is_enabled = bool(trade_report_policy.get("enabled"))
        elif commander_trade_report.get("enabled") is not None:
            is_enabled = bool(commander_trade_report.get("enabled"))
        elif trade_report_fallback.get("enabled") is not None:
            is_enabled = bool(trade_report_fallback.get("enabled"))
        else:
            is_enabled = True
    else:
        is_enabled = bool(enabled)
    chosen_model = _resolve_intraday_report_model(story_input, explicit_model=model)
    execution_profile = _resolve_intraday_report_execution_profile(story_input)
    trade_id = str(story_input.get("trade_id") or story_input.get("story_id") or "")
    run_id = str(story_input.get("run_id") or "")
    day = str(story_input.get("day") or "")
    env_retry_fallback = str(os.getenv("TRADE_REPORT_AI_RETRY_MAX", "") or "").strip()
    execution_slot_source = str(execution_profile.get("policy_source") or "").strip().lower()
    if retry_max_override is not None:
        retry_max = max(0, int(float(retry_max_override)))
        execution_profile_source = "explicit_override"
    elif execution_slot_source not in {"", "default_execution_profile", "default"}:
        retry_max = max(0, int(float(execution_profile.get("retry_max") or 0)))
        execution_profile_source = "applied_policy"
    elif env_retry_fallback:
        retry_max = max(0, int(float(env_retry_fallback or "2")))
        execution_profile_source = "fallback_env"
    elif execution_slot_source in {"", "default_execution_profile", "default"}:
        retry_max = max(0, int(float(os.getenv("TRADE_REPORT_AI_DEFAULT_RETRY_MAX", "1") or "1")))
        execution_profile_source = "default"
    else:
        retry_max = max(0, int(float(execution_profile.get("retry_max") or 2)))
        execution_profile_source = "default"
    execution_observability = build_execution_profile_observability(
        execution_profile,
        env_used=(execution_profile_source == "fallback_env"),
    )
    empty_required_meta = {
        "parse_mode": "none",
        "required_keys_expected": list(AI_TRADE_REPORT_REQUIRED_KEYS),
        "required_keys_present": [],
        "required_keys_missing": list(AI_TRADE_REPORT_REQUIRED_KEYS),
        "completeness_score": 0.0,
        "used_fallback_sections": [],
    }
    if not is_enabled:
        report = _failure_report(
            story_input,
            status="disabled",
            mode="fallback",
            model=chosen_model,
            reason="reporter.trade_report.enabled is false",
        )
        report["llm_response_artifact"] = build_llm_response_artifact(
            component="ai_trade_report",
            run_id=run_id,
            trade_id=trade_id,
            story_id=trade_id,
            day=day,
            status="fallback",
            attempts=[],
            parsed_output={},
            model_info={"provider": "OpenRouter", "model": chosen_model or "openrouter/free"},
            meta={"reason": "reporter.trade_report.enabled is false", **empty_required_meta, **build_execution_profile_observability(execution_profile, env_used=(execution_profile_source == "fallback_env"))},
        )
        return _attach_report_status_matrix(report, story_input, ai_trade_report_status="skipped")

    temp = float(
        temperature
        if temperature is not None
        else execution_profile.get("temperature") or 0.2
    )
    if max_tokens is not None:
        token_budget = int(max_tokens)
    else:
        profile_token_budget = max(600, int(float(execution_profile.get("max_tokens") or 8192)))
        if execution_slot_source in {"", "default_execution_profile", "default"}:
            default_cap = max(600, int(float(os.getenv("TRADE_REPORT_AI_DEFAULT_MAX_TOKENS", "3072") or "3072")))
            token_budget = min(profile_token_budget, default_cap)
        else:
            token_budget = profile_token_budget
    timeout_sec = max(
        1.0,
        float(timeout_sec_override if timeout_sec_override is not None else execution_profile.get("timeout_sec") or 15.0),
    )
    hard_timeout_sec = (
        max(0.1, float(hard_timeout_sec_override))
        if hard_timeout_sec_override not in (None, "", 0)
        else None
    )
    retry_backoff_sec = max(0.0, float(execution_profile.get("retry_backoff_sec") or 0.0))
    execution_observability = build_execution_profile_observability(
        execution_profile,
        env_used=(execution_profile_source == "fallback_env"),
        effective_overrides={
            "temperature": float(temp),
            "max_tokens": int(max(600, token_budget)),
            "timeout_sec": float(timeout_sec),
            "hard_timeout_sec": float(hard_timeout_sec) if hard_timeout_sec is not None else None,
            "retry": {
                "max_attempts": int(retry_max),
                "backoff_sec": float(retry_backoff_sec),
            },
        },
    )
    if local_debug_no_llm:
        report = _fallback_report(
            story_input,
            status="ok",
            mode="local_debug",
            model=chosen_model,
            reason="local_debug_no_llm",
        )
        report["llm_response_artifact"] = build_llm_response_artifact(
            component="ai_trade_report",
            run_id=run_id,
            trade_id=trade_id,
            story_id=trade_id,
            day=day,
            status="fallback",
            attempts=[],
            parsed_output={},
            model_info={"provider": "OpenRouter", "model": chosen_model or "openrouter/free"},
            meta={"reason": "local_debug_no_llm", **empty_required_meta, **execution_observability},
        )
        return _attach_report_status_matrix(
            report,
            story_input,
            ai_trade_report_status="skipped",
            deterministic_report_status="ok",
        )

    router = LLMRouter.from_env()
    if router.client is None:
        report = _failure_report(
            story_input,
            status="error",
            mode="ai",
            model=chosen_model,
            reason="OPENROUTER_API_KEY is not configured",
        )
        report["llm_response_artifact"] = build_llm_response_artifact(
            component="ai_trade_report",
            run_id=run_id,
            trade_id=trade_id,
            story_id=trade_id,
            day=day,
            status="error",
            attempts=[],
            parsed_output={},
            model_info={"provider": "OpenRouter", "model": chosen_model or "openrouter/free"},
            meta={"reason": "OPENROUTER_API_KEY is not configured", "error": "llm_client_unavailable", **empty_required_meta, **execution_observability},
        )
        return _attach_report_status_matrix(report, story_input, ai_trade_report_status="error")

    retry_token_budget = max(800, token_budget)
    messages = _build_messages(story_input)
    attempts: List[Dict[str, Any]] = []
    resolved_model = str(
        router.resolve(
            "trade_report",
            policy={
                "temperature": temp,
                "max_tokens": max(600, token_budget),
                "timeout_sec": float(timeout_sec),
                **({"model": chosen_model} if chosen_model else {}),
            },
        ).model
    )
    final_status = "error"
    final_reason = ""
    final_error = ""
    current_policy = {
        "temperature": temp,
        "max_tokens": max(600, token_budget),
        "timeout_sec": float(timeout_sec),
        "response_format": {"type": "json_object"},
        "plugins": [{"id": "response-healing"}],
        **({"model": chosen_model} if chosen_model else {}),
    }
    llm_result = _run_trade_report_llm_attempts_impl(
        router=router,
        story_input=story_input,
        messages=messages,
        current_policy=current_policy,
        retry_max=retry_max,
        retry_token_budget=retry_token_budget,
        retry_backoff_sec=retry_backoff_sec,
        hard_timeout_sec=hard_timeout_sec,
        chosen_model=chosen_model,
        resolved_model=resolved_model,
        execution_observability=execution_observability,
        router_chat_with_hard_timeout=_router_chat_with_hard_timeout,
        trade_report_parse_meta=_trade_report_parse_meta,
        trade_report_language_meta=_trade_report_language_meta,
        build_repair_messages=_build_repair_messages,
    )
    attempts = list(llm_result.get("attempts") or [])
    parsed = llm_result.get("parsed") if isinstance(llm_result.get("parsed"), dict) else None
    best_partial = llm_result.get("best_partial") if isinstance(llm_result.get("best_partial"), dict) else {}
    best_partial_meta = llm_result.get("best_partial_meta") if isinstance(llm_result.get("best_partial_meta"), dict) else {}
    raw = str(llm_result.get("raw") or "")
    final_status = str(llm_result.get("final_status") or final_status)
    final_reason = str(llm_result.get("final_reason") or final_reason)
    final_error = str(llm_result.get("final_error") or final_error)

    if not parsed and best_partial:
        final_status = "salvaged"
        final_reason = final_reason or "trade_report_ai returned incomplete JSON; deterministic sections were salvaged from the partial response"
        out = _merge_trade_report_candidate(
            story_input,
            best_partial,
            status=final_status,
            mode="ai",
            model=chosen_model or resolved_model,
            reason=final_reason,
        )
        out["llm_response_artifact"] = build_llm_response_artifact(
            component="ai_trade_report",
            run_id=run_id,
            trade_id=trade_id,
            story_id=trade_id,
            day=day,
            status=final_status,
            attempts=attempts,
            parsed_output=best_partial,
            model_info={"provider": "OpenRouter", "model": chosen_model or resolved_model},
            latency_ms=sum(int(row.get("latency_ms") or 0) for row in attempts),
            meta={
                "reason": final_reason,
                "error": final_error,
                **best_partial_meta,
                "used_fallback_sections": list(out.get("used_fallback_sections") or []),
                **execution_observability,
            },
        )
        return _attach_report_status_matrix(out, story_input, ai_trade_report_status=final_status)

    if not parsed:
        report = _failure_report(
            story_input,
            status=final_status,
            mode="ai",
            model=chosen_model or resolved_model,
            reason=final_reason or "AI trade report generation failed",
            error=final_error,
        )
        report["llm_response_artifact"] = build_llm_response_artifact(
            component="ai_trade_report",
            run_id=run_id,
            trade_id=trade_id,
            story_id=trade_id,
            day=day,
            status=final_status,
            attempts=attempts,
            parsed_output={},
            model_info={"provider": "OpenRouter", "model": chosen_model or resolved_model},
            latency_ms=sum(int(row.get("latency_ms") or 0) for row in attempts),
            meta={"reason": final_reason, "error": final_error, **empty_required_meta, **execution_observability},
        )
        return _attach_report_status_matrix(report, story_input, ai_trade_report_status=final_status)

    parse_meta = _trade_report_parse_meta(raw, parsed)
    out = _merge_trade_report_candidate(
        story_input,
        parsed,
        status=final_status,
        mode="ai",
        model=chosen_model or resolved_model,
        reason=final_reason,
    )
    out["llm_response_artifact"] = build_llm_response_artifact(
        component="ai_trade_report",
        run_id=run_id,
        trade_id=trade_id,
        story_id=trade_id,
        day=day,
        status=final_status,
        attempts=attempts,
        parsed_output=parsed,
        model_info={"provider": "OpenRouter", "model": chosen_model or resolved_model},
        latency_ms=sum(int(row.get("latency_ms") or 0) for row in attempts),
        meta={
            **parse_meta,
            "reason": final_reason,
            "used_fallback_sections": list(out.get("used_fallback_sections") or []),
            **execution_observability,
        },
    )
    return _attach_report_status_matrix(out, story_input, ai_trade_report_status=final_status)




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


