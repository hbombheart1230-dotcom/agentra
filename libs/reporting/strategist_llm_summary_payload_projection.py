"""strategist_llm_summary build_strategist_llm_summary_payload (moved verbatim from strategist_llm_summary).

Module globals and helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def build_strategist_llm_summary_payload(response_json_path: Path, *, facade: Any) -> Dict[str, Any]:
    source_path = facade.Path(response_json_path)
    raw = facade.json.loads(source_path.read_text(encoding="utf-8"))
    sidecar_meta = facade._read_json(source_path.with_name("meta.json"))
    payload = facade._parse_response_body(raw)
    canonical_path, canonical = facade._load_canonical_strategist(source_path)
    theme_strategy = facade._as_dict(payload.get("theme_strategy"))
    refresh_trace = facade._as_dict(payload.get("strategy_refresh_trace"))
    horizon = facade._as_dict(payload.get("strategy_horizon_feedback"))
    strategy_detail = facade._strategy_detail_from_sources(payload, canonical)
    stage_decision = facade._stage_decision_from_payload(payload, raw, sidecar_meta)
    stage_meta = facade._stage_meta(payload, raw, sidecar_meta)
    news_usage = facade._news_usage_from_canonical(canonical)
    market_regime_rail = facade._market_rail_from_canonical(canonical)
    news_quality = facade._news_quality_audit(canonical, news_usage)
    risk_off_exception_policy = facade._as_dict(canonical.get("risk_off_exception_policy")) or facade.build_risk_off_exception_policy(
        market_regime_rail=market_regime_rail,
        news_quality=news_quality,
    )
    output_quality = facade._strategist_output_quality_audit(
        payload=payload,
        canonical=canonical,
        stage_decision=stage_decision,
        strategy_detail=strategy_detail,
        market_rail=market_regime_rail,
        news_quality=news_quality,
    )

    return {
        "schema_version": "strategist_llm_summary.v1",
        "artifact_type": "strategist_llm_summary",
        "source_response_json": str(source_path),
        "source_canonical_strategist_json": str(canonical_path) if canonical_path else "",
        "generated_at": facade._utc_now_iso(),
        "llm_meta": {
            "stage": facade._first_text("", raw.get("stage"), sidecar_meta.get("stage")),
            "stage_index": stage_meta.get("stage_index"),
            "stage_name": facade._text(stage_meta.get("stage_name"), ""),
            "call_kind": facade._text(stage_meta.get("call_kind"), ""),
            "stage_component": facade._text(stage_meta.get("stage_component"), ""),
            "provider": facade._first_text("", raw.get("provider"), sidecar_meta.get("provider")),
            "model": facade._first_text("", raw.get("model"), sidecar_meta.get("model")),
            "status": facade._first_text("", raw.get("status"), raw.get("llm_status"), sidecar_meta.get("status"), sidecar_meta.get("llm_status")),
            "reason": facade._first_text("", raw.get("reason"), sidecar_meta.get("reason")),
            "run_id": facade._first_text("", raw.get("run_id"), sidecar_meta.get("run_id")),
            "day": facade._first_text("", raw.get("day"), sidecar_meta.get("day")),
            "saved_at": facade._first_text("", raw.get("saved_at"), sidecar_meta.get("saved_at")),
            "repair_used": bool(raw.get("repair_used") or sidecar_meta.get("repair_used")),
            "profile_name": facade._first_text("", raw.get("llm_execution_profile_name"), sidecar_meta.get("llm_execution_profile_name")),
            "profile_source": facade._first_text("", raw.get("llm_execution_profile_source"), sidecar_meta.get("llm_execution_profile_source")),
        },
        "operator_readout": facade._operator_readout_clean(payload, stage_decision),
        "stage_decision": stage_decision,
        "strategy_frame": {
            "playbook": facade._text(payload.get("playbook")),
            "selected_themes": facade._as_list(payload.get("selected_themes")),
            "theme_selection_mode": facade._text(theme_strategy.get("selection_mode")),
            "fallback_reason": facade._text(theme_strategy.get("fallback_reason"), ""),
            "rationale": facade._text(payload.get("rationale"), ""),
        },
        "strategy_detail": strategy_detail,
        "policy_changes": {
            "playbook_action": facade._directive(payload, "playbook_action"),
            "entry_policy_action": facade._directive(payload, "entry_policy_action"),
            "monitor_focus_action": facade._directive(payload, "monitor_focus_action"),
            "selected_symbol_bias_action": facade._directive(payload, "selected_symbol_bias_action"),
            "refresh_action": facade._directive(payload, "refresh_action"),
        },
        "monitor_entry_policy": facade._as_dict(payload.get("monitor_entry_policy")),
        "memory_usage": facade._memory_usage_from_canonical(canonical),
        "news_usage": news_usage,
        "news_event_intelligence": facade._as_dict(
            payload.get("news_event_intelligence") or canonical.get("news_event_intelligence")
        ),
        "news_event_intelligence_usage": facade._as_dict(payload.get("news_event_intelligence_usage")),
        "market_regime_rail": market_regime_rail,
        "news_quality_audit": news_quality,
        "risk_off_exception_policy": risk_off_exception_policy,
        "risk_off_exception_conditions": facade._as_list(payload.get("risk_off_exception_conditions")),
        "strategist_output_quality_audit": output_quality,
        "strategy_refresh_trace": {
            "summary": facade._text(refresh_trace.get("summary"), ""),
            "bullets": facade._as_list(refresh_trace.get("bullets")),
            "stages": facade._as_list(refresh_trace.get("stages")),
        },
        "strategy_horizon_feedback": horizon,
    }
