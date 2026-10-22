"""Pure result shaping for the passive reporter AI review (P1.5 DEV-A).

Bounded string/list/dict clipping, the default (disabled/failed) result and the normalized successful result. No I/O or
clock; every helper, the required-key list and the LLM-status canonicalizer are resolved on the injected ``facade``
(``libs.reporting.reporter_ai_review``) at call time, so patching a facade attribute behaves as before the move.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _normalize_llm_status_impl(status: str, *, facade: Any) -> str:
    return facade.canonical_llm_status(status, default="fallback")


def _clip_str_impl(v: Any, *, max_len: int = 400, facade: Any) -> str:
    s = str(v or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max(0, max_len - 3)] + "..."


def _list_str_impl(v: Any, *, max_items: int = 8, max_len: int = 240, facade: Any) -> List[str]:
    out: List[str] = []
    if not isinstance(v, list):
        return out
    for item in v:
        s = facade._clip_str(item, max_len=max_len)
        if s:
            out.append(s)
        if len(out) >= max_items:
            break
    return out


def _dict_str_impl(v: Any, *, max_items: int = 8, max_key_len: int = 64, max_val_len: int = 120, facade: Any) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not isinstance(v, dict):
        return out
    for k, val in v.items():
        key = facade._clip_str(k, max_len=max_key_len)
        if not key:
            continue
        out[key] = facade._clip_str(val, max_len=max_val_len)
        if len(out) >= max_items:
            break
    return out


def _default_result_impl(*, enabled: bool, status: str, reason: str = "", model: str = "", facade: Any) -> Dict[str, Any]:
    meta = facade.required_key_metadata({}, facade.REPORTER_AI_REVIEW_REQUIRED_KEYS)
    return {
        "enabled": bool(enabled),
        "status": str(status),
        "llm_status": facade._normalize_llm_status(status),
        "model": str(model or ""),
        "reason": facade._clip_str(reason, max_len=320),
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


def _normalize_evidence_link_items_impl(v: Any, *, max_items: int = 10, facade: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not isinstance(v, list):
        return out
    for item in v:
        if isinstance(item, dict):
            out.append(
                {
                    "text": facade._clip_str(item.get("text"), max_len=260),
                    "evidence_keys": facade._list_str(item.get("evidence_keys"), max_items=6, max_len=64),
                }
            )
        elif isinstance(item, str):
            key = facade._clip_str(item, max_len=64)
            if key:
                out.append({"text": "", "evidence_keys": [key]})
        if len(out) >= max_items:
            break
    return out


def _normalize_result_impl(obj: Dict[str, Any], *, enabled: bool, model: str, facade: Any) -> Dict[str, Any]:
    evidence_links = obj.get("ai_evidence_links") if isinstance(obj.get("ai_evidence_links"), dict) else {}
    meta = facade.required_key_metadata(obj, facade.REPORTER_AI_REVIEW_REQUIRED_KEYS)
    return {
        "enabled": bool(enabled),
        "status": "ok",
        "llm_status": "ok",
        "model": str(model or ""),
        "reason": "",
        "parse_mode": "full",
        **meta,
        "ai_summary": facade._clip_str(obj.get("ai_summary"), max_len=600),
        "ai_findings": facade._list_str(obj.get("ai_findings"), max_items=12, max_len=260),
        "ai_root_causes": facade._list_str(obj.get("ai_root_causes"), max_items=10, max_len=260),
        "ai_improvement_suggestions": facade._list_str(obj.get("ai_improvement_suggestions"), max_items=10, max_len=260),
        "ai_run_grade": facade._clip_str(obj.get("ai_run_grade") or "N/A", max_len=16),
        "ai_agent_evaluations": facade._dict_str(obj.get("ai_agent_evaluations"), max_items=10),
        "ai_evidence_links": {
            "findings": facade._normalize_evidence_link_items(evidence_links.get("findings")),
            "root_causes": facade._normalize_evidence_link_items(evidence_links.get("root_causes")),
            "improvements": facade._normalize_evidence_link_items(evidence_links.get("improvements")),
        },
    }
