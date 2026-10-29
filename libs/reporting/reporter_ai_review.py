from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

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
from libs.reporting import reporter_ai_review_input as _input_owner
from libs.reporting import reporter_ai_review_result as _result_owner


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
    return canonical_llm_status(status, default="fallback")


def _clip_str(v: Any, *, max_len: int = 400) -> str:
    s = str(v or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max(0, max_len - 3)] + "..."


def _list_str(v: Any, *, max_items: int = 8, max_len: int = 240) -> List[str]:
    out: List[str] = []
    if not isinstance(v, list):
        return out
    for item in v:
        s = _clip_str(item, max_len=max_len)
        if s:
            out.append(s)
        if len(out) >= max_items:
            break
    return out


def _dict_str(v: Any, *, max_items: int = 8, max_key_len: int = 64, max_val_len: int = 120) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not isinstance(v, dict):
        return out
    for k, val in v.items():
        key = _clip_str(k, max_len=max_key_len)
        if not key:
            continue
        out[key] = _clip_str(val, max_len=max_val_len)
        if len(out) >= max_items:
            break
    return out


def _default_result(*, enabled: bool, status: str, reason: str = "", model: str = "") -> Dict[str, Any]:
    meta = required_key_metadata({}, REPORTER_AI_REVIEW_REQUIRED_KEYS)
    return {
        "enabled": bool(enabled),
        "status": str(status),
        "llm_status": _normalize_llm_status(status),
        "model": str(model or ""),
        "reason": _clip_str(reason, max_len=320),
        "parse_mode": "none",
        **meta,
        "ai_summary": "",
        "ai_findings": [],
        "ai_root_causes": [],
        "ai_improvement_suggestions": [],
        "ai_run_grade": "N/A",
        "ai_agent_evaluations": {},
        "ai_evidence_links": {"findings": [], "root_causes": [], "improvements": []},
    }


def _normalize_evidence_link_items(v: Any, *, max_items: int = 10) -> List[Dict[str, Any]]:
    return _result_owner.normalize_evidence_link_items(v, max_items=max_items, facade=sys.modules[__name__])


def _normalize_result(obj: Dict[str, Any], *, enabled: bool, model: str) -> Dict[str, Any]:
    return _result_owner.normalize_result(obj, enabled=enabled, model=model, facade=sys.modules[__name__])


def _build_compact_input(day: str, out: Dict[str, Any]) -> Dict[str, Any]:
    return _input_owner.build_compact_input(day, out, facade=sys.modules[__name__])


def _build_messages(day: str, compact_input: Dict[str, Any]) -> List[Dict[str, str]]:
    return _input_owner.build_messages(day, compact_input, facade=sys.modules[__name__])


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
    if enabled is None:
        applied_policy = reporter_output.get("applied_policy") if isinstance(reporter_output.get("applied_policy"), dict) else {}
        reporter_policy = applied_policy.get("reporter") if isinstance(applied_policy.get("reporter"), dict) else {}
        ai_review_policy = reporter_policy.get("ai_review") if isinstance(reporter_policy.get("ai_review"), dict) else {}
        policy_fallback = reporter_output.get("reporter_policy") if isinstance(reporter_output.get("reporter_policy"), dict) else {}
        ai_review_fallback = policy_fallback.get("ai_review") if isinstance(policy_fallback.get("ai_review"), dict) else {}
        payload_policy = reporter_output.get("policy") if isinstance(reporter_output.get("policy"), dict) else {}
        payload_reporter_policy = payload_policy.get("reporter") if isinstance(payload_policy.get("reporter"), dict) else {}
        payload_ai_review_policy = (
            payload_reporter_policy.get("ai_review")
            if isinstance(payload_reporter_policy.get("ai_review"), dict)
            else {}
        )
        if ai_review_policy.get("enabled") is not None:
            is_enabled = bool(ai_review_policy.get("enabled"))
        elif ai_review_fallback.get("enabled") is not None:
            is_enabled = bool(ai_review_fallback.get("enabled"))
        elif payload_ai_review_policy.get("enabled") is not None:
            is_enabled = bool(payload_ai_review_policy.get("enabled"))
        else:
            is_enabled = False
    else:
        is_enabled = bool(enabled)
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
    parse_mode = "full" if bool(parsed_result.get("is_full")) else "partial" if bool(parsed_result.get("is_partial")) else "none"

    if not isinstance(obj, dict) or bool(key_meta.get("required_keys_missing")):
        parse_reason = "ai_response_not_full_json"
        if not bool(parsed_result.get("raw_nonempty")):
            parse_reason = "ai_response_empty"
        elif bool(parsed_result.get("is_partial")):
            parse_reason = "ai_response_partial_json"
        elif bool(key_meta.get("required_keys_missing")):
            missing = ", ".join(list(key_meta.get("required_keys_missing") or []))
            parse_reason = f"ai_response_missing_required_keys:{missing}"
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
