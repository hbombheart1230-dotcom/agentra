"""OpenAI-style chat response projection (pure; moved verbatim from openai_provider).

Functions that depend on sibling helpers receive the ``facade`` module and resolve them at call time so use-time patches on
``libs.ai.providers.openai_provider`` keep working. This module never imports the facade and performs no IO.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


def extract_chat_content(resp: Dict[str, Any]) -> str:
    choices = resp.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    msg = choices[0] if isinstance(choices[0], dict) else {}
    msg = msg.get("message") if isinstance(msg.get("message"), dict) else msg
    content = msg.get("content") if isinstance(msg, dict) else ""

    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict) and isinstance(p.get("text"), str):
                parts.append(p.get("text") or "")
        return "".join(parts)
    return ""


def extract_chat_message(resp: Dict[str, Any]) -> Dict[str, Any]:
    choices = resp.get("choices")
    if not isinstance(choices, list) or not choices:
        return {}
    first = choices[0] if isinstance(choices[0], dict) else {}
    msg = first.get("message") if isinstance(first.get("message"), dict) else first
    return msg if isinstance(msg, dict) else {}


def extract_chat_finish_reason(resp: Dict[str, Any]) -> str:
    choices = resp.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0] if isinstance(choices[0], dict) else {}
    return str(first.get("finish_reason") or first.get("native_finish_reason") or "").strip().lower()


def chat_output_truncated_without_final_answer(resp: Dict[str, Any], *, facade: Any) -> bool:
    reason = facade._extract_chat_finish_reason(resp)
    if reason != "length":
        return False
    msg = facade._extract_chat_message(resp)
    content = msg.get("content")
    content_text = str(content or "").strip() if isinstance(content, str) else ""
    reasoning_text = str(msg.get("reasoning") or "").strip()
    return (not content_text) and bool(reasoning_text)


def extract_chat_structured_object(resp: Dict[str, Any], *, facade: Any) -> Optional[Dict[str, Any]]:
    """Extract structured JSON object from non-text chat response shapes."""
    choices = resp.get("choices")
    if not isinstance(choices, list) or not choices:
        return None

    first = choices[0] if isinstance(choices[0], dict) else {}
    msg = first.get("message") if isinstance(first.get("message"), dict) else first
    if not isinstance(msg, dict):
        return None

    # OpenAI structured outputs may expose parsed object directly.
    parsed = msg.get("parsed")
    if isinstance(parsed, dict):
        return dict(parsed)

    content = msg.get("content")
    if isinstance(content, dict):
        if isinstance(content.get("json"), dict):
            return dict(content.get("json") or {})
        if isinstance(content.get("parsed"), dict):
            return dict(content.get("parsed") or {})
    elif isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            if isinstance(part.get("json"), dict):
                return dict(part.get("json") or {})
            if isinstance(part.get("parsed"), dict):
                return dict(part.get("parsed") or {})
            if isinstance(part.get("input_json"), dict):
                return dict(part.get("input_json") or {})

    # Tool-call outputs can include function arguments as JSON.
    tool_calls = msg.get("tool_calls")
    if isinstance(tool_calls, list):
        for tc in tool_calls:
            if not isinstance(tc, dict):
                continue
            fn = tc.get("function")
            if not isinstance(fn, dict):
                continue
            args = fn.get("arguments")
            if isinstance(args, dict):
                return dict(args)
            if isinstance(args, str):
                obj = facade._extract_json_object(args)
                if isinstance(obj, dict):
                    return obj
    reasoning = msg.get("reasoning")
    if isinstance(reasoning, str):
        obj = facade._extract_json_object(reasoning)
        if isinstance(obj, dict):
            return obj
    return None


def to_nonneg_int(v: Any) -> Optional[int]:
    try:
        x = int(float(v))
    except Exception:
        return None
    if x < 0:
        return None
    return x


def extract_usage(resp: Dict[str, Any], *, facade: Any) -> Dict[str, int]:
    """Extract token usage from provider response (best-effort)."""
    usage = resp.get("usage")
    if not isinstance(usage, dict):
        return {}

    prompt_tokens = facade._to_nonneg_int(usage.get("prompt_tokens"))
    completion_tokens = facade._to_nonneg_int(usage.get("completion_tokens"))
    total_tokens = facade._to_nonneg_int(usage.get("total_tokens"))

    if total_tokens is None and prompt_tokens is not None and completion_tokens is not None:
        total_tokens = prompt_tokens + completion_tokens

    out: Dict[str, int] = {}
    if prompt_tokens is not None:
        out["prompt_tokens"] = prompt_tokens
    if completion_tokens is not None:
        out["completion_tokens"] = completion_tokens
    if total_tokens is not None:
        out["total_tokens"] = total_tokens
    return out
