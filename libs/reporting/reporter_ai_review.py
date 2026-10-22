from __future__ import annotations

import json
import sys as _sys
import os
from typing import Any, Dict, List, Optional

from libs.reporting.reporter_ai_review_parts.prompting import (  # noqa: F401 - facade ABI re-exports
    _build_messages_impl,
)
from libs.reporting.reporter_ai_review_parts.compact_input import (  # noqa: F401 - facade ABI re-exports
    _build_compact_input_impl,
)
from libs.reporting.reporter_ai_review_parts.review_resolution import (
    resolve_ai_review_enabled,
    resolve_parse_failure_reason,
    resolve_parse_mode,
)
from libs.reporting.reporter_ai_review_parts.result_shaping import (  # noqa: F401 - facade ABI re-exports
    _clip_str_impl,
    _default_result_impl,
    _dict_str_impl,
    _list_str_impl,
    _normalize_evidence_link_items_impl,
    _normalize_llm_status_impl,
    _normalize_result_impl,
)
from libs.llm.model_catalog import build_execution_profile_observability, resolve_policy_llm_execution_slot, resolve_policy_llm_slot
from libs.llm.model_names import normalize_openrouter_model_name
from libs.llm.llm_router import LLMRouter
from libs.llm.json_response import (
    parse_llm_json_response,
    required_key_metadata,
    strip_fenced_code_block,
)
from libs.research.evidence_ledger import record_llm_prompt, record_llm_response, record_raw_input
from libs.reporting.llm_artifacts import canonical_llm_status


def _env_bool(name: str, default: bool = False) -> bool:
    raw = str(os.getenv(name, "1" if default else "0")).strip().lower()
    return raw in ("1", "true", "yes", "on")


def _strip_fenced_block(text: str) -> str:
    return strip_fenced_code_block(text)


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    parsed = parse_llm_json_response(text)
    if isinstance(parsed.get("full_object"), dict):
        return dict(parsed.get("full_object") or {})
    return None


REPORTER_AI_REVIEW_REQUIRED_KEYS = [
    "ai_summary",
    "ai_findings",
    "ai_root_causes",
    "ai_improvement_suggestions",
    "ai_run_grade",
    "ai_agent_evaluations",
    "ai_evidence_links",
]


def _normalize_llm_status(status: str) -> str:
    return _normalize_llm_status_impl(status, facade=_sys.modules[__name__])


def _clip_str(v: Any, *, max_len: int = 400) -> str:
    return _clip_str_impl(v, max_len=max_len, facade=_sys.modules[__name__])


def _list_str(v: Any, *, max_items: int = 8, max_len: int = 240) -> List[str]:
    return _list_str_impl(v, max_items=max_items, max_len=max_len, facade=_sys.modules[__name__])


def _dict_str(v: Any, *, max_items: int = 8, max_key_len: int = 64, max_val_len: int = 120) -> Dict[str, str]:
    return _dict_str_impl(v, max_items=max_items, max_key_len=max_key_len, max_val_len=max_val_len, facade=_sys.modules[__name__])


def _default_result(*, enabled: bool, status: str, reason: str = "", model: str = "") -> Dict[str, Any]:
    return _default_result_impl(enabled=enabled, status=status, reason=reason, model=model, facade=_sys.modules[__name__])


def _normalize_evidence_link_items(v: Any, *, max_items: int = 10) -> List[Dict[str, Any]]:
    return _normalize_evidence_link_items_impl(v, max_items=max_items, facade=_sys.modules[__name__])


def _normalize_result(obj: Dict[str, Any], *, enabled: bool, model: str) -> Dict[str, Any]:
    return _normalize_result_impl(obj, enabled=enabled, model=model, facade=_sys.modules[__name__])


def _build_compact_input(day: str, out: Dict[str, Any]) -> Dict[str, Any]:
    return _build_compact_input_impl(day, out, facade=_sys.modules[__name__])


def _build_messages(day: str, compact_input: Dict[str, Any]) -> List[Dict[str, str]]:
    return _build_messages_impl(day, compact_input, facade=_sys.modules[__name__])


def build_ai_reporter_review(
    *,
    day: str,
    reporter_output: Dict[str, Any],
    enabled: Optional[bool] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: int = 900,
) -> Dict[str, Any]:
    """Optional passive AI review stage layered on deterministic reporter analysis."""
    run_id = f"reporter-{str(day)}"
    is_enabled = resolve_ai_review_enabled(reporter_output, enabled)
    if not is_enabled:
        return _default_result(enabled=False, status="disabled", reason="reporter.ai_review.enabled is false")
    if _env_bool("DRY_RUN", False):
        return _default_result(enabled=True, status="dry_run", reason="DRY_RUN mode")

    router = LLMRouter.from_env()
    if router.client is None:
        return _default_result(enabled=True, status="unavailable", reason="LLM client unavailable")

    llm_slot = resolve_policy_llm_slot(reporter_output, "reporter", "daily", default_profile="strong_reasoning")
    execution_slot = resolve_policy_llm_execution_slot(
        reporter_output,
        "reporter",
        "daily",
        default_profile="deep_review",
        defaults={
            "profile_name": "deep_review",
            "name": "deep_review",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": 15,
            "retry": {"max_attempts": 2, "backoff_sec": 0.0},
            "retry_max": 2,
            "retry_backoff_sec": 0.0,
        },
    )
    env_model = str(llm_slot.get("primary") or "moonshotai/kimi-k2.5").strip()
    execution_slot_source = str(execution_slot.get("policy_source") or "").strip().lower()
    env_temp = _clip_str(os.getenv("REPORTER_AI_REVIEW_TEMPERATURE") or "", max_len=32)
    env_max_tokens = _clip_str(os.getenv("REPORTER_AI_REVIEW_MAX_TOKENS") or "", max_len=32)
    env_execution_fallback_used = False
    if execution_slot_source in {"", "default_execution_profile", "default"} and (env_temp or env_max_tokens):
        env_execution_fallback_used = True
    resolved_model = normalize_openrouter_model_name(model or env_model or "")
    if temperature is not None:
        resolved_temp = float(temperature)
    elif env_execution_fallback_used and env_temp:
        resolved_temp = float(env_temp)
    else:
        resolved_temp = float(execution_slot.get("temperature") or 0.2)
    resolved_max_tokens = int(max_tokens)
    if max_tokens == 900 and env_execution_fallback_used and env_max_tokens:
        resolved_max_tokens = int(float(env_max_tokens))
    elif max_tokens == 900:
        resolved_max_tokens = int(float(execution_slot.get("max_tokens") or 8192))
    resolved_timeout_sec = max(1.0, float(execution_slot.get("timeout_sec") or 15.0))
    execution_observability = build_execution_profile_observability(
        execution_slot,
        env_used=env_execution_fallback_used,
        effective_overrides={
            "temperature": float(resolved_temp),
            "max_tokens": max(256, int(resolved_max_tokens)),
            "timeout_sec": float(resolved_timeout_sec),
        },
    )

    policy: Dict[str, Any] = {
        "max_tokens": max(256, int(resolved_max_tokens)),
        "temperature": float(resolved_temp),
        "timeout_sec": float(resolved_timeout_sec),
    }
    if resolved_model:
        policy["model"] = resolved_model
    route = router.resolve("reporter_final", policy=policy)

    compact_input = _build_compact_input(day, reporter_output)
    messages = _build_messages(day, compact_input)
    prompt_text = "\n\n".join(
        [f"[{str(m.get('role') or '').strip().lower() or 'unknown'}]\n{str(m.get('content') or '')}" for m in messages]
    ).strip()
    try:
        record_raw_input(
            run_id=run_id,
            agent="reporter",
            stage="post_run_analysis",
            raw_input={"compact_input": compact_input},
            decision_link={"stage": "ai_review_input"},
        )
        record_llm_prompt(
            run_id=run_id,
            agent="reporter",
            stage="post_run_analysis",
            llm_prompt=prompt_text,
            raw_input={"compact_input": compact_input},
            decision_link={"model": str(route.model or ""), "provider": "reporter_router"},
        )
    except Exception:
        pass
    try:
        raw = router.chat("reporter_final", messages, policy=policy)
    except Exception as e:
        try:
            record_llm_response(
                run_id=run_id,
                agent="reporter",
                stage="post_run_analysis",
                llm_response=f"ERROR:{type(e).__name__}:{e}",
                parsed_output={},
                decision_link={"status": "error"},
            )
        except Exception:
            pass
        result = _default_result(enabled=True, status="error", reason=f"ai_call_failed:{e}", model=route.model)
        result.update(execution_observability)
        return result

    parsed_result = parse_llm_json_response(raw)
    obj = parsed_result.get("full_object") if isinstance(parsed_result.get("full_object"), dict) else None
    candidate = obj
    if candidate is None and isinstance(parsed_result.get("partial_object"), dict):
        candidate = dict(parsed_result.get("partial_object") or {})
    key_meta = required_key_metadata(candidate if isinstance(candidate, dict) else {}, REPORTER_AI_REVIEW_REQUIRED_KEYS)
    parse_mode = resolve_parse_mode(parsed_result)

    if not isinstance(obj, dict) or bool(key_meta.get("required_keys_missing")):
        parse_reason = resolve_parse_failure_reason(parsed_result, key_meta)
        try:
            record_llm_response(
                run_id=run_id,
                agent="reporter",
                stage="post_run_analysis",
                llm_response=str(raw or ""),
                parsed_output=dict(candidate or {}) if isinstance(candidate, dict) else {},
                decision_link={"status": "parse_error", "parse_mode": parse_mode, **key_meta},
            )
        except Exception:
            pass
        result = _default_result(
            enabled=True,
            status="parse_error",
            reason=f"{parse_reason}:{_clip_str(raw, max_len=220)}",
            model=route.model,
        )
        result["parse_mode"] = parse_mode
        result.update(key_meta)
        result.update(execution_observability)
        return result
    try:
        record_llm_response(
            run_id=run_id,
            agent="reporter",
            stage="post_run_analysis",
            llm_response=str(raw or ""),
            parsed_output=dict(obj),
            decision_link={"status": "ok", "model": str(route.model or "")},
        )
    except Exception:
        pass
    result = _normalize_result(obj, enabled=True, model=route.model)
    result.update(execution_observability)
    return result
