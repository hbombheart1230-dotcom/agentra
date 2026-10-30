from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from libs.runtime.quant.market_regime_observation import classify_market_regime_rail
from libs.runtime.strategist_input_quality import build_risk_off_exception_policy
from libs.reporting import strategist_llm_summary_stage as _stage_owner
from libs.reporting import strategist_llm_summary_usage as _usage_owner
from libs.reporting import strategist_llm_summary_decision as _decision_owner
from libs.reporting import strategist_llm_summary_readout as _readout_owner
from libs.reporting import strategist_llm_summary_strategy as _strategy_owner
from libs.reporting import strategist_llm_summary_quality_lines as _quality_lines_owner
from libs.reporting import strategist_llm_summary_usage_lines as _usage_lines_owner
from libs.reporting import strategist_llm_summary_strategy_lines as _strategy_lines_owner
from libs.reporting import strategist_llm_summary_stage_markdown as _stage_markdown_owner
from libs.reporting import strategist_llm_summary_directive_line as _directive_line_owner
from libs.reporting import strategist_llm_summary_watch_status as _watch_status_owner
from libs.reporting import strategist_llm_summary_playbook_flow as _playbook_flow_owner
from libs.reporting import strategist_llm_summary_operator_projection as _operator_projection_owner
from libs.reporting import strategist_llm_summary_path_projection as _path_projection_owner
from libs.reporting import strategist_llm_summary_sample_counts as _sample_counts_owner
from libs.reporting import strategist_llm_summary_first_values as _first_values_owner
from libs.reporting import strategist_llm_summary_legacy_watch_status as _legacy_watch_status_owner
from libs.reporting import strategist_llm_summary_legacy_scores as _legacy_scores_owner
from libs.reporting import strategist_llm_summary_primitives as _primitives_owner
from libs.reporting import strategist_llm_summary_directive_projection as _directive_projection_owner
from libs.reporting import strategist_llm_summary_json_projection as _json_projection_owner
from libs.reporting import strategist_llm_summary_markdown_helpers as _markdown_helpers_owner
from libs.reporting import strategist_llm_summary_read_projection as _read_projection_owner
from libs.reporting import strategist_llm_summary_canonical_loader as _canonical_loader_owner
from libs.reporting import strategist_llm_summary_market_rail as _market_rail_owner


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_dict(value: Any) -> Dict[str, Any]:
    return _primitives_owner.as_dict(value)


def _as_list(value: Any) -> List[Any]:
    return _primitives_owner.as_list(value)


def _text(value: Any, default: str = "-") -> str:
    return _primitives_owner.text(value, default)


def _read_json(path: Path) -> Dict[str, Any]:
    return _read_projection_owner._read_json(path, facade=sys.modules[__name__])


_STAGE_META_BY_CALL_KIND: Dict[str, Dict[str, Any]] = {
    "selected_symbol_tactical_refresh": {
        "stage_index": 2,
        "stage_name": "selected_symbol_tactical_refresh",
        "stage_component": "strategist_stage2_selected_symbol",
    },
    "stale_intraday_hold_review": {
        "stage_index": 3,
        "stage_name": "stale_intraday_hold_review",
        "stage_component": "strategist_stage3_hold_review",
    },
    "end_of_day_carry_review": {
        "stage_index": 4,
        "stage_name": "end_of_day_carry_review",
        "stage_component": "strategist_stage4_carry_review",
    },
}


def _infer_call_kind(payload: Dict[str, Any], raw: Dict[str, Any], meta: Dict[str, Any] | None = None) -> str:
    return _stage_owner.infer_call_kind(payload, raw, meta, facade=sys.modules[__name__])


def _stage_meta(payload: Dict[str, Any], raw: Dict[str, Any], meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return _stage_owner.stage_meta(payload, raw, meta, facade=sys.modules[__name__])


def _parse_response_body(raw: Dict[str, Any]) -> Dict[str, Any]:
    return _stage_owner.parse_response_body(raw)


def _canonical_strategist_path_for_response(source_path: Path) -> Path | None:
    return _path_projection_owner.canonical_strategist_path_for_response(source_path)


def _trade_strategist_input_path_for_response(source_path: Path) -> Path | None:
    return _path_projection_owner.trade_strategist_input_path_for_response(source_path)


def _load_canonical_strategist(source_path: Path) -> Tuple[Path | None, Dict[str, Any]]:
    return _canonical_loader_owner._load_canonical_strategist(source_path, facade=sys.modules[__name__])


def _headline_count_from_sample_map(value: Any) -> int:
    return _sample_counts_owner.headline_count_from_sample_map(value)


def _directive(payload: Dict[str, Any], key: str) -> Dict[str, Any]:
    return _directive_projection_owner.directive(payload, key, facade=sys.modules[__name__])


def _compact_operator_summary(value: Dict[str, Any]) -> Dict[str, Any]:
    return _operator_projection_owner.compact_operator_summary(value, facade=sys.modules[__name__])


def _memory_usage_from_canonical(canonical: Dict[str, Any]) -> Dict[str, Any]:
    return _usage_owner.memory_usage_from_canonical(canonical, facade=sys.modules[__name__])


def _news_usage_from_canonical(canonical: Dict[str, Any]) -> Dict[str, Any]:
    return _usage_owner.news_usage_from_canonical(canonical, facade=sys.modules[__name__])


def _market_rail_from_canonical(canonical: Dict[str, Any]) -> Dict[str, Any]:
    return _market_rail_owner._market_rail_from_canonical(canonical, facade=sys.modules[__name__])


def _news_quality_audit(canonical: Dict[str, Any], news_usage: Dict[str, Any]) -> Dict[str, Any]:
    return _usage_owner.news_quality_audit(canonical, news_usage, facade=sys.modules[__name__])


def _strategist_output_quality_audit(
    *,
    payload: Dict[str, Any],
    canonical: Dict[str, Any],
    stage_decision: Dict[str, Any],
    strategy_detail: Dict[str, Any],
    market_rail: Dict[str, Any],
    news_quality: Dict[str, Any],
) -> Dict[str, Any]:
    return _decision_owner.strategist_output_quality_audit(payload=payload, canonical=canonical, stage_decision=stage_decision, strategy_detail=strategy_detail, market_rail=market_rail, news_quality=news_quality, facade=sys.modules[__name__])


def _stage_decision_from_payload(
    payload: Dict[str, Any],
    raw: Dict[str, Any],
    meta: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _decision_owner.stage_decision_from_payload(payload, raw, meta, facade=sys.modules[__name__])


def _operator_readout(payload: Dict[str, Any], stage_decision: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return _readout_owner.operator_readout(payload, stage_decision, facade=sys.modules[__name__])


def _first_text(default: str, *values: Any) -> str:
    return _first_values_owner.first_text(default, *values, facade=sys.modules[__name__])


def _operator_readout_clean(payload: Dict[str, Any], stage_decision: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return _readout_owner.operator_readout_clean(payload, stage_decision, facade=sys.modules[__name__])


def _first_dict(*values: Any) -> Dict[str, Any]:
    return _first_values_owner.first_dict(*values, facade=sys.modules[__name__])


def _strategy_detail_from_sources(payload: Dict[str, Any], canonical: Dict[str, Any]) -> Dict[str, Any]:
    return _strategy_owner.strategy_detail_from_sources(payload, canonical, facade=sys.modules[__name__])


def _json_inline(value: Any) -> str:
    return _json_projection_owner.json_inline(value)


def _watch_scope_label(value: Dict[str, Any]) -> str:
    return _legacy_watch_status_owner.watch_scope_label(value, facade=sys.modules[__name__])


def _strategy_patch_status(detail: Dict[str, Any]) -> str:
    return _legacy_watch_status_owner.strategy_patch_status(detail, facade=sys.modules[__name__])


def _playbook_flow_label(detail: Dict[str, Any]) -> str:
    return _playbook_flow_owner.playbook_flow_label(detail, facade=sys.modules[__name__])


def _score_value(value: Any) -> float:
    return _legacy_scores_owner.score_value(value)


def _score_label(value: Any) -> str:
    return _legacy_scores_owner.score_label(value, facade=sys.modules[__name__])


def _strategy_score_lines(scores: Dict[str, Any], *, selected: str) -> List[str]:
    return _legacy_scores_owner.strategy_score_lines(scores, selected=selected, facade=sys.modules[__name__])


def _watch_scope_label_clean(value: Dict[str, Any]) -> str:
    return _watch_status_owner.watch_scope_label_clean(value, facade=sys.modules[__name__])


def _strategy_patch_status_clean(detail: Dict[str, Any]) -> str:
    return _watch_status_owner.strategy_patch_status_clean(detail, facade=sys.modules[__name__])


def _strategy_score_lines_clean(scores: Dict[str, Any], *, selected: str) -> List[str]:
    return _strategy_lines_owner.strategy_score_lines_clean(scores, selected=selected, facade=sys.modules[__name__])


def _rejected_strategy_lines(reasons: Dict[str, Any], *, selected: str) -> List[str]:
    return _strategy_lines_owner.rejected_strategy_lines(reasons, selected=selected, facade=sys.modules[__name__])


def build_strategist_llm_summary_payload(response_json_path: Path) -> Dict[str, Any]:
    source_path = Path(response_json_path)
    raw = json.loads(source_path.read_text(encoding="utf-8"))
    sidecar_meta = _read_json(source_path.with_name("meta.json"))
    payload = _parse_response_body(raw)
    canonical_path, canonical = _load_canonical_strategist(source_path)
    theme_strategy = _as_dict(payload.get("theme_strategy"))
    refresh_trace = _as_dict(payload.get("strategy_refresh_trace"))
    horizon = _as_dict(payload.get("strategy_horizon_feedback"))
    strategy_detail = _strategy_detail_from_sources(payload, canonical)
    stage_decision = _stage_decision_from_payload(payload, raw, sidecar_meta)
    stage_meta = _stage_meta(payload, raw, sidecar_meta)
    news_usage = _news_usage_from_canonical(canonical)
    market_regime_rail = _market_rail_from_canonical(canonical)
    news_quality = _news_quality_audit(canonical, news_usage)
    risk_off_exception_policy = _as_dict(canonical.get("risk_off_exception_policy")) or build_risk_off_exception_policy(
        market_regime_rail=market_regime_rail,
        news_quality=news_quality,
    )
    output_quality = _strategist_output_quality_audit(
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
        "generated_at": _utc_now_iso(),
        "llm_meta": {
            "stage": _first_text("", raw.get("stage"), sidecar_meta.get("stage")),
            "stage_index": stage_meta.get("stage_index"),
            "stage_name": _text(stage_meta.get("stage_name"), ""),
            "call_kind": _text(stage_meta.get("call_kind"), ""),
            "stage_component": _text(stage_meta.get("stage_component"), ""),
            "provider": _first_text("", raw.get("provider"), sidecar_meta.get("provider")),
            "model": _first_text("", raw.get("model"), sidecar_meta.get("model")),
            "status": _first_text("", raw.get("status"), raw.get("llm_status"), sidecar_meta.get("status"), sidecar_meta.get("llm_status")),
            "reason": _first_text("", raw.get("reason"), sidecar_meta.get("reason")),
            "run_id": _first_text("", raw.get("run_id"), sidecar_meta.get("run_id")),
            "day": _first_text("", raw.get("day"), sidecar_meta.get("day")),
            "saved_at": _first_text("", raw.get("saved_at"), sidecar_meta.get("saved_at")),
            "repair_used": bool(raw.get("repair_used") or sidecar_meta.get("repair_used")),
            "profile_name": _first_text("", raw.get("llm_execution_profile_name"), sidecar_meta.get("llm_execution_profile_name")),
            "profile_source": _first_text("", raw.get("llm_execution_profile_source"), sidecar_meta.get("llm_execution_profile_source")),
        },
        "operator_readout": _operator_readout_clean(payload, stage_decision),
        "stage_decision": stage_decision,
        "strategy_frame": {
            "playbook": _text(payload.get("playbook")),
            "selected_themes": _as_list(payload.get("selected_themes")),
            "theme_selection_mode": _text(theme_strategy.get("selection_mode")),
            "fallback_reason": _text(theme_strategy.get("fallback_reason"), ""),
            "rationale": _text(payload.get("rationale"), ""),
        },
        "strategy_detail": strategy_detail,
        "policy_changes": {
            "playbook_action": _directive(payload, "playbook_action"),
            "entry_policy_action": _directive(payload, "entry_policy_action"),
            "monitor_focus_action": _directive(payload, "monitor_focus_action"),
            "selected_symbol_bias_action": _directive(payload, "selected_symbol_bias_action"),
            "refresh_action": _directive(payload, "refresh_action"),
        },
        "monitor_entry_policy": _as_dict(payload.get("monitor_entry_policy")),
        "memory_usage": _memory_usage_from_canonical(canonical),
        "news_usage": news_usage,
        "news_event_intelligence": _as_dict(
            payload.get("news_event_intelligence") or canonical.get("news_event_intelligence")
        ),
        "news_event_intelligence_usage": _as_dict(payload.get("news_event_intelligence_usage")),
        "market_regime_rail": market_regime_rail,
        "news_quality_audit": news_quality,
        "risk_off_exception_policy": risk_off_exception_policy,
        "risk_off_exception_conditions": _as_list(payload.get("risk_off_exception_conditions")),
        "strategist_output_quality_audit": output_quality,
        "strategy_refresh_trace": {
            "summary": _text(refresh_trace.get("summary"), ""),
            "bullets": _as_list(refresh_trace.get("bullets")),
            "stages": _as_list(refresh_trace.get("stages")),
        },
        "strategy_horizon_feedback": horizon,
    }


def _bullet_lines(items: List[Any], *, empty: str = "-") -> List[str]:
    return _markdown_helpers_owner.bullet_lines(items, empty=empty)


def _directive_line(label: str, value: Dict[str, Any]) -> str:
    return _directive_line_owner.directive_line(label, value, facade=sys.modules[__name__])


def _memory_usage_lines(memory: Dict[str, Any]) -> List[str]:
    return _usage_lines_owner.memory_usage_lines(memory, facade=sys.modules[__name__])


def _news_usage_lines(news: Dict[str, Any]) -> List[str]:
    return _usage_lines_owner.news_usage_lines(news, facade=sys.modules[__name__])


def render_strategist_llm_summary_markdown(payload: Dict[str, Any]) -> str:
    meta = _as_dict(payload.get("llm_meta"))
    readout = _as_dict(payload.get("operator_readout"))
    stage_decision = _as_dict(payload.get("stage_decision"))
    if bool(stage_decision.get("is_stage_specific")):
        return _render_stage_specific_summary_markdown(payload)

    frame = _as_dict(payload.get("strategy_frame"))
    detail = _as_dict(payload.get("strategy_detail"))
    changes = _as_dict(payload.get("policy_changes"))
    entry = _as_dict(payload.get("monitor_entry_policy"))
    memory = _as_dict(payload.get("memory_usage"))
    news = _as_dict(payload.get("news_usage"))
    refresh = _as_dict(payload.get("strategy_refresh_trace"))
    horizon = _as_dict(payload.get("strategy_horizon_feedback"))
    hold = _as_dict(horizon.get("expected_hold_window"))
    exit_guidance = _as_dict(horizon.get("exit_guidance"))
    handoff = _as_dict(horizon.get("monitor_handoff"))

    selected_themes = _as_list(frame.get("selected_themes"))
    theme_text = ", ".join(str(x) for x in selected_themes) if selected_themes else "-"
    watch = _as_dict(detail.get("candidate_watch_policy"))
    watch_scope = _watch_scope_label(watch)
    tactical_strategy = _text(detail.get("tactical_strategy"), "")
    strategy_scores = _as_dict(detail.get("strategy_scores"))
    rejected_reasons = _as_dict(detail.get("rejected_strategy_reasons"))

    lines: List[str] = [
        f"# Strategist LLM Summary ({_text(meta.get('day'), '-')})",
        "",
        "---",
        "",
        "## 전략가 원문 해석 출력",
        "",
        "> 아래 내용은 전략가 LLM 응답의 구조화 필드를 재배치한 것입니다. 리포터가 새로 해석한 문장이 아니라 `response.json`에 저장된 전략가 출력입니다.",
        "",
        f"- 상태: {_text(meta.get('status'))} / model={_text(meta.get('model'))}",
        "",
        "### 전략 프레임",
        "",
        f"- 플레이북: **{_text(frame.get('playbook'))}**",
        f"- 선택 테마: {theme_text}",
        f"- 테마 선택 모드: {_text(frame.get('theme_selection_mode'))}",
        f"- fallback 사유: {_text(frame.get('fallback_reason'))}",
        "",
        "**전략가 rationale**",
        "",
        _text(frame.get("rationale")),
        "",
        "### 전략 디테일",
        "",
        f"- 전략 강화 필드: {_strategy_patch_status(detail)}",
        f"- 플레이북 흐름: {_playbook_flow_label(detail)}",
        f"- LLM 요청 플레이북: {_text(detail.get('llm_requested_playbook'))}",
        f"- 최종 플레이북: {_text(detail.get('final_playbook'))}",
        f"- 선택 전술: {_text(detail.get('tactical_strategy'))}",
        f"- 후보 감시 제안: {watch_scope or '-'}",
        "",
        "#### 전략 점수",
        "",
        *_strategy_score_lines(strategy_scores, selected=tactical_strategy),
        "",
        "#### 탈락 전략 이유",
        "",
        *_rejected_strategy_lines(rejected_reasons, selected=tactical_strategy),
        "",
        "### 메모리 사용",
        "",
        *_memory_usage_lines(memory),
        "",
        "### 뉴스 사용",
        "",
        *_news_usage_lines(news),
        "",
        *_quality_audit_lines(payload),
        "### 정책 조정",
        "",
        _directive_line("플레이북", _as_dict(changes.get("playbook_action"))),
        _directive_line("진입 정책", _as_dict(changes.get("entry_policy_action"))),
        _directive_line("모니터 초점", _as_dict(changes.get("monitor_focus_action"))),
        _directive_line("심볼 bias", _as_dict(changes.get("selected_symbol_bias_action"))),
        _directive_line("refresh", _as_dict(changes.get("refresh_action"))),
        "",
        "### 전략 Refresh 흐름",
        "",
        f"- 요약: {_text(refresh.get('summary'))}",
        "",
    ]
    lines.extend(_bullet_lines(_as_list(refresh.get("bullets"))))
    lines += ["", "#### 단계", ""]
    stages = _as_list(refresh.get("stages"))
    stage_line_count = 0
    for stage in stages:
        row = _as_dict(stage)
        if not row:
            continue
        stage_line_count += 1
        lines.append(
            f"- {_text(row.get('stage'))}: {_text(row.get('label'))}; "
            f"effective={row.get('effective')}; {_text(row.get('summary'))}"
        )
    if stage_line_count == 0:
        lines.append("- -")

    lines += [
        "",
        "### 모니터 진입 정책",
        "",
        f"- enabled: {entry.get('enabled')}",
        f"- timeframe_minutes: {entry.get('timeframe_minutes')}",
        f"- volume_ratio_min: {entry.get('volume_ratio_min')}",
        f"- vwap 확장 허용: min={entry.get('min_extended_from_vwap_pct')}, max={entry.get('max_extended_from_vwap_pct')}",
        f"- pullback 범위: min={entry.get('pullback_min_pct')}, max={entry.get('pullback_max_pct')}",
        f"- reclaim_tolerance_pct: {entry.get('reclaim_tolerance_pct')}",
        f"- intent_cooldown_sec: {entry.get('intent_cooldown_sec')}",
        f"- require_vwap_reclaim / require_rebound: {entry.get('require_vwap_reclaim')} / {entry.get('require_rebound')}",
        "",
        "### 운용 Horizon",
        "",
        f"- strategy_horizon: {_text(horizon.get('strategy_horizon'))}",
        f"- hold_window_sec: min={hold.get('min_sec')}, target={hold.get('target_sec')}, max={hold.get('max_sec')}",
        f"- preferred_exit: {_text(handoff.get('preferred_exit') or exit_guidance.get('profit_take_style'))}",
        f"- hold_bias: {_text(handoff.get('hold_bias'))}",
        f"- do_not_force_hold: {handoff.get('do_not_force_hold')}",
        f"- allow_early_exit: {exit_guidance.get('allow_early_exit')}",
        "",
        "#### 무효화 조건",
        "",
        *_bullet_lines(_as_list(horizon.get("invalidation_conditions"))),
        "",
        "---",
        "",
        "## 운영자 검수 요약",
        "",
        "> 아래 내용은 전략가 원문을 기준으로 한 deterministic 검수입니다. 추가 LLM 호출이나 새 전략 해석은 포함하지 않습니다.",
        "",
        f"- 검수 결론: **{_text(readout.get('headline'))}**",
        f"- 주요 원인: {_text(readout.get('root_cause'))}",
        "",
        "### 잘된 점",
        "",
        *_bullet_lines(_as_list(readout.get("good_points"))),
        "",
        "### 문제점",
        "",
        *_bullet_lines(_as_list(readout.get("issues"))),
        "",
        "### 권고 액션",
        "",
        *_bullet_lines(_as_list(readout.get("recommended_actions"))),
        "",
        "### 검증 포인트",
        "",
        *_bullet_lines(_as_list(readout.get("validation_questions"))),
        "",
        "---",
        "",
        "## 근거",
        "",
        f"- source_response_json: `{payload.get('source_response_json')}`",
        f"- source_canonical_strategist_json: `{payload.get('source_canonical_strategist_json')}`",
        f"- run_id: `{_text(meta.get('run_id'), '')}`",
        f"- saved_at: `{_text(meta.get('saved_at'), '')}`",
        f"- generated_at: `{_text(payload.get('generated_at'), '')}`",
        "",
    ]
    return "\n".join(lines)


def _monitor_adjustment_lines(value: Dict[str, Any]) -> List[str]:
    return _markdown_helpers_owner.monitor_adjustment_lines(value)


def _render_stage_specific_summary_markdown(payload: Dict[str, Any]) -> str:
    meta = _as_dict(payload.get("llm_meta"))
    readout = _as_dict(payload.get("operator_readout"))
    stage_decision = _as_dict(payload.get("stage_decision"))
    detail = _as_dict(payload.get("strategy_detail"))
    watch = _as_dict(detail.get("candidate_watch_policy"))
    triggers = ", ".join(str(x) for x in _as_list(stage_decision.get("priority_exit_triggers"))) or "-"
    monitor_adjustment = _as_dict(stage_decision.get("monitor_adjustment"))

    lines: List[str] = [
        f"# Strategist LLM Summary ({_text(meta.get('day'), '-')})",
        "",
        "---",
        "",
        "## Stage-Specific LLM Output",
        "",
        f"- status: {_text(meta.get('status'))} / model={_text(meta.get('model'))}",
        f"- stage: {stage_decision.get('stage_index')} / {_text(stage_decision.get('stage_name'))}",
        f"- call_kind: {_text(stage_decision.get('call_kind'))}",
        f"- stage_component: {_text(meta.get('stage_component'))}",
        "",
        "### Decision",
        "",
        f"- decision: **{_text(stage_decision.get('decision'))}**",
        f"- exit_pressure: {_text(stage_decision.get('exit_pressure'))}",
        f"- thesis_status: {_text(stage_decision.get('thesis_status'))}",
        f"- next_check_minutes: {stage_decision.get('next_check_minutes')}",
        f"- priority_exit_triggers: {triggers}",
        "",
        "### Monitor Adjustment",
        "",
        *_monitor_adjustment_lines(monitor_adjustment),
        "",
        "### Reason",
        "",
        _text(stage_decision.get("reason")),
        "",
        "## Strategy Context From Canonical",
        "",
        f"- final_playbook: {_text(detail.get('final_playbook'))}",
        f"- tactical_strategy: {_text(detail.get('tactical_strategy'))}",
        f"- playbook_flow: {_playbook_flow_label(detail)}",
        f"- candidate_watch: {_watch_scope_label_clean(watch) or '-'}",
        "",
        *_quality_audit_lines(payload),
        "## Operator Check",
        "",
        f"- summary: **{_text(readout.get('headline'))}**",
        f"- main_reason: {_text(readout.get('root_cause'))}",
        "",
        "### Good Points",
        "",
        *_bullet_lines(_as_list(readout.get("good_points"))),
        "",
        "### Issues",
        "",
        *_bullet_lines(_as_list(readout.get("issues"))),
        "",
        "### Recommended Actions",
        "",
        *_bullet_lines(_as_list(readout.get("recommended_actions"))),
        "",
        "---",
        "",
        "## Evidence",
        "",
        f"- source_response_json: `{payload.get('source_response_json')}`",
        f"- source_canonical_strategist_json: `{payload.get('source_canonical_strategist_json')}`",
        f"- run_id: `{_text(meta.get('run_id'), '')}`",
        f"- saved_at: `{_text(meta.get('saved_at'), '')}`",
        f"- generated_at: `{_text(payload.get('generated_at'), '')}`",
        "",
    ]
    return "\n".join(lines)


def _memory_usage_lines_clean(memory: Dict[str, Any]) -> List[str]:
    return _usage_lines_owner.memory_usage_lines_clean(memory, facade=sys.modules[__name__])


def _news_usage_lines_clean(news: Dict[str, Any]) -> List[str]:
    return _usage_lines_owner.news_usage_lines_clean(news, facade=sys.modules[__name__])


def _quality_audit_lines(payload: Dict[str, Any]) -> List[str]:
    return _quality_lines_owner.quality_audit_lines(payload, facade=sys.modules[__name__])


def _render_stage_specific_summary_markdown_clean(payload: Dict[str, Any]) -> str:
    return _stage_markdown_owner.render_stage_specific_summary_markdown_clean(payload, facade=sys.modules[__name__])


def render_strategist_llm_summary_markdown(payload: Dict[str, Any]) -> str:
    meta = _as_dict(payload.get("llm_meta"))
    readout = _as_dict(payload.get("operator_readout"))
    stage_decision = _as_dict(payload.get("stage_decision"))
    if bool(stage_decision.get("is_stage_specific")):
        return _render_stage_specific_summary_markdown_clean(payload)

    frame = _as_dict(payload.get("strategy_frame"))
    detail = _as_dict(payload.get("strategy_detail"))
    changes = _as_dict(payload.get("policy_changes"))
    entry = _as_dict(payload.get("monitor_entry_policy"))
    memory = _as_dict(payload.get("memory_usage"))
    news = _as_dict(payload.get("news_usage"))
    refresh = _as_dict(payload.get("strategy_refresh_trace"))
    horizon = _as_dict(payload.get("strategy_horizon_feedback"))
    hold = _as_dict(horizon.get("expected_hold_window"))
    exit_guidance = _as_dict(horizon.get("exit_guidance"))
    handoff = _as_dict(horizon.get("monitor_handoff"))
    selected_themes = _as_list(frame.get("selected_themes"))
    theme_text = ", ".join(str(x) for x in selected_themes) if selected_themes else "-"
    watch = _as_dict(detail.get("candidate_watch_policy"))
    tactical_strategy = _text(detail.get("tactical_strategy"), "")
    strategy_scores = _as_dict(detail.get("strategy_scores"))
    rejected_reasons = _as_dict(detail.get("rejected_strategy_reasons"))

    lines: List[str] = [
        f"# Strategist LLM Summary ({_text(meta.get('day'), '-')})",
        "",
        "---",
        "",
        "## 전략가 원문 해석 출력",
        "",
        "> 아래 내용은 전략가 LLM 응답과 canonical 전략가 산출물을 사람이 읽기 좋게 재배열한 것입니다.",
        "",
        f"- 상태: {_text(meta.get('status'))} / model={_text(meta.get('model'))}",
        "",
        "### 전략 프레임",
        "",
        f"- 플레이북: **{_text(frame.get('playbook'))}**",
        f"- 선택 테마: {theme_text}",
        f"- 테마 선택 모드: {_text(frame.get('theme_selection_mode'))}",
        f"- fallback 사유: {_text(frame.get('fallback_reason'))}",
        "",
        "**전략가 rationale**",
        "",
        _text(frame.get("rationale")),
        "",
        "### 전략 디테일",
        "",
        f"- 전략 강화 필드: {_strategy_patch_status_clean(detail)}",
        f"- 플레이북 흐름: {_playbook_flow_label(detail)}",
        f"- LLM 요청 플레이북: {_text(detail.get('llm_requested_playbook'))}",
        f"- 최종 플레이북: {_text(detail.get('final_playbook'))}",
        f"- 선택 전술: {_text(detail.get('tactical_strategy'))}",
        f"- 후보 감시 제안: {_watch_scope_label_clean(watch) or '-'}",
        "",
        "#### 전략 점수",
        "",
        *_strategy_score_lines_clean(strategy_scores, selected=tactical_strategy),
        "",
        "#### 제외 전략 이유",
        "",
        *_rejected_strategy_lines(rejected_reasons, selected=tactical_strategy),
        "",
        "### 메모리 사용",
        "",
        *_memory_usage_lines_clean(memory),
        "",
        "### 뉴스 사용",
        "",
        *_news_usage_lines_clean(news),
        "",
        *_quality_audit_lines(payload),
        "### 정책 조정",
        "",
        _directive_line("플레이북", _as_dict(changes.get("playbook_action"))),
        _directive_line("진입 정책", _as_dict(changes.get("entry_policy_action"))),
        _directive_line("모니터 초점", _as_dict(changes.get("monitor_focus_action"))),
        _directive_line("성과 bias", _as_dict(changes.get("selected_symbol_bias_action"))),
        _directive_line("refresh", _as_dict(changes.get("refresh_action"))),
        "",
        "### 전략 Refresh 흐름",
        "",
        f"- 요약: {_text(refresh.get('summary'))}",
        "",
    ]
    lines.extend(_bullet_lines(_as_list(refresh.get("bullets"))))
    lines += ["", "#### 단계", ""]
    stages = _as_list(refresh.get("stages"))
    stage_line_count = 0
    for stage in stages:
        row = _as_dict(stage)
        if not row:
            continue
        stage_line_count += 1
        lines.append(
            f"- {_text(row.get('stage'))}: {_text(row.get('label'))}; "
            f"effective={row.get('effective')}; {_text(row.get('summary'))}"
        )
    if stage_line_count == 0:
        lines.append("- -")

    lines += [
        "",
        "### 모니터 진입 정책",
        "",
        f"- enabled: {entry.get('enabled')}",
        f"- timeframe_minutes: {entry.get('timeframe_minutes')}",
        f"- volume_ratio_min: {entry.get('volume_ratio_min')}",
        f"- vwap 확장 허용: min={entry.get('min_extended_from_vwap_pct')}, max={entry.get('max_extended_from_vwap_pct')}",
        f"- pullback 범위: min={entry.get('pullback_min_pct')}, max={entry.get('pullback_max_pct')}",
        f"- reclaim_tolerance_pct: {entry.get('reclaim_tolerance_pct')}",
        f"- intent_cooldown_sec: {entry.get('intent_cooldown_sec')}",
        f"- require_vwap_reclaim / require_rebound: {entry.get('require_vwap_reclaim')} / {entry.get('require_rebound')}",
        "",
        "### 보유 Horizon",
        "",
        f"- strategy_horizon: {_text(horizon.get('strategy_horizon'))}",
        f"- hold_window_sec: min={hold.get('min_sec')}, target={hold.get('target_sec')}, max={hold.get('max_sec')}",
        f"- preferred_exit: {_text(handoff.get('preferred_exit') or exit_guidance.get('profit_take_style'))}",
        f"- hold_bias: {_text(handoff.get('hold_bias'))}",
        f"- do_not_force_hold: {handoff.get('do_not_force_hold')}",
        f"- allow_early_exit: {exit_guidance.get('allow_early_exit')}",
        "",
        "#### 무효화 조건",
        "",
        *_bullet_lines(_as_list(horizon.get("invalidation_conditions"))),
        "",
        "---",
        "",
        "## 운영자 검토 요약",
        "",
        "> 아래 내용은 전략가 원문을 기준으로 한 deterministic 검토입니다. 추가 LLM 호출은 포함하지 않습니다.",
        "",
        f"- 검토 결론: **{_text(readout.get('headline'))}**",
        f"- 주요 원인: {_text(readout.get('root_cause'))}",
        "",
        "### 잘 된 점",
        "",
        *_bullet_lines(_as_list(readout.get("good_points"))),
        "",
        "### 문제점",
        "",
        *_bullet_lines(_as_list(readout.get("issues"))),
        "",
        "### 권고 액션",
        "",
        *_bullet_lines(_as_list(readout.get("recommended_actions"))),
        "",
        "### 검증 포인트",
        "",
        *_bullet_lines(_as_list(readout.get("validation_questions"))),
        "",
        "---",
        "",
        "## 근거",
        "",
        f"- source_response_json: `{payload.get('source_response_json')}`",
        f"- source_canonical_strategist_json: `{payload.get('source_canonical_strategist_json')}`",
        f"- run_id: `{_text(meta.get('run_id'), '')}`",
        f"- saved_at: `{_text(meta.get('saved_at'), '')}`",
        f"- generated_at: `{_text(payload.get('generated_at'), '')}`",
        "",
    ]
    return "\n".join(lines)


def generate_strategist_llm_summary(response_json_path: Path) -> Tuple[Path, Path, Dict[str, Any]]:
    source_path = Path(response_json_path)
    payload = build_strategist_llm_summary_payload(source_path)
    md_path = source_path.with_name("strategist_summary.md")
    json_path = source_path.with_name("strategist_summary.json")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_strategist_llm_summary_markdown(payload), encoding="utf-8-sig", newline="\n")
    return md_path, json_path, payload
