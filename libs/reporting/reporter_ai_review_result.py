"""Reporter AI review: evidence-link and result normalization (pure; moved verbatim from reporter_ai_review).

Helpers (``_clip_str``/``_list_str``/``_dict_str``/``required_key_metadata``/the required-key list) are resolved on the
``facade`` module at call time so patches on ``libs.reporting.reporter_ai_review`` keep working. Never imports the facade.
"""
from __future__ import annotations

from typing import Any, Dict, List


def normalize_evidence_link_items(v: Any, *, facade: Any, max_items: int = 10) -> List[Dict[str, Any]]:
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


def normalize_result(obj: Dict[str, Any], *, enabled: bool, model: str, facade: Any) -> Dict[str, Any]:
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


def default_result(*, enabled: bool, status: str, reason: str = "", model: str = "", facade: Any) -> Dict[str, Any]:
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
