"""Strategist LLM summary stage / response projections (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

import json
from typing import Any, Dict


def infer_call_kind(payload: Dict[str, Any], raw: Dict[str, Any], meta: Dict[str, Any] | None = None, *, facade: Any) -> str:
    sidecar = facade._as_dict(meta)
    explicit = facade._text(
        raw.get("call_kind") or sidecar.get("call_kind") or payload.get("call_kind"),
        "",
    )
    if explicit:
        return explicit
    component = facade._text(
        raw.get("stage_component") or sidecar.get("stage_component") or raw.get("component") or sidecar.get("component"),
        "",
    )
    if component == "strategist_stage2_selected_symbol":
        return "selected_symbol_tactical_refresh"
    if component == "strategist_stage3_hold_review":
        return "stale_intraday_hold_review"
    if component == "strategist_stage4_carry_review":
        return "end_of_day_carry_review"
    if (
        payload.get("selected_symbol_decision") is not None
        or payload.get("target_symbol") is not None
        or payload.get("runner_up_order") is not None
    ):
        return "selected_symbol_tactical_refresh"
    if payload.get("hold_review_decision") is not None:
        return "stale_intraday_hold_review"
    if payload.get("carry_review_decision") is not None:
        return "end_of_day_carry_review"
    return ""


def stage_meta(payload: Dict[str, Any], raw: Dict[str, Any], meta: Dict[str, Any] | None = None, *, facade: Any) -> Dict[str, Any]:
    sidecar = facade._as_dict(meta)
    call_kind = facade._infer_call_kind(payload, raw, sidecar)
    inferred = dict(facade._STAGE_META_BY_CALL_KIND.get(call_kind) or {})
    return {
        "call_kind": call_kind,
        "stage_index": raw.get("stage_index") or sidecar.get("stage_index") or inferred.get("stage_index"),
        "stage_name": facade._first_text(
            "",
            raw.get("stage_name"),
            sidecar.get("stage_name"),
            inferred.get("stage_name"),
            call_kind,
        ),
        "stage_component": facade._first_text(
            "",
            raw.get("stage_component"),
            sidecar.get("stage_component"),
            inferred.get("stage_component"),
            raw.get("component"),
            sidecar.get("component"),
        ),
    }


def parse_response_body(raw: Dict[str, Any]) -> Dict[str, Any]:
    parsed = raw.get("parsed_output")
    if isinstance(parsed, dict) and parsed:
        return dict(parsed)

    response_text = raw.get("response_text")
    if isinstance(response_text, str) and response_text.strip():
        try:
            loaded = json.loads(response_text)
        except json.JSONDecodeError:
            return {}
        return dict(loaded) if isinstance(loaded, dict) else {}

    attempts = raw.get("attempts")
    if isinstance(attempts, list):
        for row in reversed(attempts):
            if not isinstance(row, dict):
                continue
            parsed = row.get("parsed_output")
            if isinstance(parsed, dict) and parsed:
                return dict(parsed)
            response_text = row.get("raw_response_text")
            if isinstance(response_text, str) and response_text.strip():
                try:
                    loaded = json.loads(response_text)
                except json.JSONDecodeError:
                    continue
                if isinstance(loaded, dict):
                    return dict(loaded)
    return {}
