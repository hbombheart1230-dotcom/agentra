"""LLM artifacts: LLM attempt and response artifact payload builders (moved verbatim from llm_artifacts).

Helpers are resolved on ``facade`` (the llm_artifacts module) at call time where needed; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def make_attempt(
    *,
    step: str,
    messages: Any,
    raw_response_text: Any,
    parsed_output: Any,
    model: Any,
    provider: Any = "OpenRouter",
    latency_ms: Any = 0,
    status: Any = "ok",
    meta: Dict[str, Any] | None = None,
    facade: Any,
) -> Dict[str, Any]:
    system_prompt, user_prompt = facade.split_prompt_messages(messages)
    payload = {
        "step": str(step or "").strip() or "primary",
        "role": str(meta.get("role") if isinstance(meta, dict) and meta.get("role") is not None else "").strip() if isinstance(meta, dict) else "",
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "raw_response_text": str(raw_response_text or ""),
        "parsed_output": parsed_output if isinstance(parsed_output, (dict, list)) else {},
        "model_info": {
            "provider": str(provider or "OpenRouter"),
            "model": str(model or ""),
        },
        "latency_ms": int(float(latency_ms or 0)),
        "status": facade.normalize_llm_status(status),
        "llm_status": facade.canonical_llm_status(status),
    }
    if isinstance(meta, dict):
        for key, value in meta.items():
            if key in payload:
                continue
            payload[key] = value
    return payload


def build_llm_response_artifact(
    *,
    component: str,
    run_id: Any,
    trade_id: Any = "",
    story_id: Any = "",
    day: Any = "",
    status: Any = "ok",
    attempts: List[Dict[str, Any]] | None = None,
    parsed_output: Any = None,
    model_info: Dict[str, Any] | None = None,
    latency_ms: Any = 0,
    meta: Dict[str, Any] | None = None,
    facade: Any,
) -> Dict[str, Any]:
    out = {
        "schema_version": "llm_response_artifact.v1",
        "component": str(component or "").strip(),
        "role": str(component or "").strip(),
        "run_id": str(run_id or ""),
        "trade_id": str(trade_id or ""),
        "story_id": str(story_id or trade_id or ""),
        "day": str(day or ""),
        "saved_at": facade.utc_now_iso(),
        "status": facade.normalize_llm_status(status),
        "llm_status": facade.canonical_llm_status(status),
        "latency_ms": int(float(latency_ms or 0)),
        "parsed_output": parsed_output if isinstance(parsed_output, (dict, list)) else {},
        "model_info": dict(model_info or {}),
        "model": str((model_info or {}).get("model") or ""),
        "attempts": [dict(row) for row in list(attempts or []) if isinstance(row, dict)],
    }
    final_attempt = out["attempts"][-1] if out["attempts"] else {}
    out["system_prompt"] = str(final_attempt.get("system_prompt") or "")
    out["user_prompt"] = str(final_attempt.get("user_prompt") or "")
    out["raw_response_text"] = str(final_attempt.get("raw_response_text") or "")
    if not out["parsed_output"] and isinstance(final_attempt.get("parsed_output"), (dict, list)):
        out["parsed_output"] = final_attempt.get("parsed_output")
    if isinstance(final_attempt.get("model_info"), dict):
        if not out["model_info"]:
            out["model_info"] = dict(final_attempt.get("model_info") or {})
        if not str(out.get("model") or "").strip():
            out["model"] = str((final_attempt.get("model_info") or {}).get("model") or "")
    out["error"] = str(final_attempt.get("error") or "")
    out["retry_count"] = max(0, len(out["attempts"]) - 1)
    if isinstance(meta, dict):
        out["meta"] = dict(meta)
        if not out["error"] and meta.get("error") is not None:
            out["error"] = str(meta.get("error") or "")
        if "token_usage" in meta and isinstance(meta.get("token_usage"), dict):
            out["token_usage"] = dict(meta.get("token_usage") or {})
        if "response_truncated" in meta:
            out["response_truncated"] = bool(meta.get("response_truncated"))
        if "repair_used" in meta:
            out["repair_used"] = bool(meta.get("repair_used"))
        if "llm_error_type" in meta:
            out["llm_error_type"] = str(meta.get("llm_error_type") or "")
    metadata_sources = []
    if isinstance(meta, dict):
        metadata_sources.append(meta)
    if isinstance(final_attempt, dict):
        metadata_sources.append(final_attempt)
    for source in metadata_sources:
        for key in (
            "parse_mode",
            "required_keys_expected",
            "required_keys_present",
            "required_keys_missing",
            "completeness_score",
            "used_fallback_sections",
            "finish_reason",
            "llm_execution_profile_name",
            "llm_execution_profile_source",
            "llm_execution_effective_config",
        ):
            if key in out and out.get(key) not in (None, "", [], {}):
                continue
            value = source.get(key) if isinstance(source, dict) else None
            if value in (None, ""):
                continue
            if key == "completeness_score":
                try:
                    out[key] = float(value)
                except Exception:
                    continue
            elif key == "llm_execution_effective_config":
                if isinstance(value, dict):
                    out[key] = dict(value)
            elif key in {"required_keys_expected", "required_keys_present", "required_keys_missing", "used_fallback_sections"}:
                if isinstance(value, list):
                    out[key] = list(value)
            else:
                out[key] = value
    if "parse_mode" not in out:
        out["parse_mode"] = "none"
    if "required_keys_expected" not in out:
        out["required_keys_expected"] = []
    if "required_keys_present" not in out:
        out["required_keys_present"] = []
    if "required_keys_missing" not in out:
        out["required_keys_missing"] = []
    if "completeness_score" not in out:
        out["completeness_score"] = 0.0
    if "used_fallback_sections" not in out:
        out["used_fallback_sections"] = []
    if "finish_reason" not in out:
        out["finish_reason"] = ""
    if "llm_execution_profile_name" not in out:
        out["llm_execution_profile_name"] = ""
    if "llm_execution_profile_source" not in out:
        out["llm_execution_profile_source"] = ""
    if "llm_execution_effective_config" not in out:
        out["llm_execution_effective_config"] = {}
    if "token_usage" not in out:
        out["token_usage"] = {}
    if "response_truncated" not in out:
        out["response_truncated"] = False
    if "repair_used" not in out:
        out["repair_used"] = any(bool(row.get("repair_used")) for row in out["attempts"])
    if "llm_error_type" not in out:
        out["llm_error_type"] = ""
    return out
