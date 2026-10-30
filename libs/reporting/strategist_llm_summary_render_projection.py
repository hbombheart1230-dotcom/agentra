"""Strategist LLM summary markdown renderer (moved verbatim from strategist_llm_summary).

The active (last) ``render_strategist_llm_summary_markdown`` definition only. Every source helper is resolved on ``facade``
(the strategist_llm_summary module) at call time; this module never imports it. Pure formatting; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def render_strategist_llm_summary_markdown(payload: Dict[str, Any], *, facade: Any) -> str:
    meta = facade._as_dict(payload.get("llm_meta"))
    readout = facade._as_dict(payload.get("operator_readout"))
    stage_decision = facade._as_dict(payload.get("stage_decision"))
    if bool(stage_decision.get("is_stage_specific")):
        return facade._render_stage_specific_summary_markdown_clean(payload)

    frame = facade._as_dict(payload.get("strategy_frame"))
    detail = facade._as_dict(payload.get("strategy_detail"))
    changes = facade._as_dict(payload.get("policy_changes"))
    entry = facade._as_dict(payload.get("monitor_entry_policy"))
    memory = facade._as_dict(payload.get("memory_usage"))
    news = facade._as_dict(payload.get("news_usage"))
    refresh = facade._as_dict(payload.get("strategy_refresh_trace"))
    horizon = facade._as_dict(payload.get("strategy_horizon_feedback"))
    hold = facade._as_dict(horizon.get("expected_hold_window"))
    exit_guidance = facade._as_dict(horizon.get("exit_guidance"))
    handoff = facade._as_dict(horizon.get("monitor_handoff"))
    selected_themes = facade._as_list(frame.get("selected_themes"))
    theme_text = ", ".join(str(x) for x in selected_themes) if selected_themes else "-"
    watch = facade._as_dict(detail.get("candidate_watch_policy"))
    tactical_strategy = facade._text(detail.get("tactical_strategy"), "")
    strategy_scores = facade._as_dict(detail.get("strategy_scores"))
    rejected_reasons = facade._as_dict(detail.get("rejected_strategy_reasons"))

    lines: List[str] = [
        f"# Strategist LLM Summary ({facade._text(meta.get('day'), '-')})",
        "",
        "---",
        "",
        "## 전략가 원문 해석 출력",
        "",
        "> 아래 내용은 전략가 LLM 응답과 canonical 전략가 산출물을 사람이 읽기 좋게 재배열한 것입니다.",
        "",
        f"- 상태: {facade._text(meta.get('status'))} / model={facade._text(meta.get('model'))}",
        "",
        "### 전략 프레임",
        "",
        f"- 플레이북: **{facade._text(frame.get('playbook'))}**",
        f"- 선택 테마: {theme_text}",
        f"- 테마 선택 모드: {facade._text(frame.get('theme_selection_mode'))}",
        f"- fallback 사유: {facade._text(frame.get('fallback_reason'))}",
        "",
        "**전략가 rationale**",
        "",
        facade._text(frame.get("rationale")),
        "",
        "### 전략 디테일",
        "",
        f"- 전략 강화 필드: {facade._strategy_patch_status_clean(detail)}",
        f"- 플레이북 흐름: {facade._playbook_flow_label(detail)}",
        f"- LLM 요청 플레이북: {facade._text(detail.get('llm_requested_playbook'))}",
        f"- 최종 플레이북: {facade._text(detail.get('final_playbook'))}",
        f"- 선택 전술: {facade._text(detail.get('tactical_strategy'))}",
        f"- 후보 감시 제안: {facade._watch_scope_label_clean(watch) or '-'}",
        "",
        "#### 전략 점수",
        "",
        *facade._strategy_score_lines_clean(strategy_scores, selected=tactical_strategy),
        "",
        "#### 제외 전략 이유",
        "",
        *facade._rejected_strategy_lines(rejected_reasons, selected=tactical_strategy),
        "",
        "### 메모리 사용",
        "",
        *facade._memory_usage_lines_clean(memory),
        "",
        "### 뉴스 사용",
        "",
        *facade._news_usage_lines_clean(news),
        "",
        *facade._quality_audit_lines(payload),
        "### 정책 조정",
        "",
        facade._directive_line("플레이북", facade._as_dict(changes.get("playbook_action"))),
        facade._directive_line("진입 정책", facade._as_dict(changes.get("entry_policy_action"))),
        facade._directive_line("모니터 초점", facade._as_dict(changes.get("monitor_focus_action"))),
        facade._directive_line("성과 bias", facade._as_dict(changes.get("selected_symbol_bias_action"))),
        facade._directive_line("refresh", facade._as_dict(changes.get("refresh_action"))),
        "",
        "### 전략 Refresh 흐름",
        "",
        f"- 요약: {facade._text(refresh.get('summary'))}",
        "",
    ]
    lines.extend(facade._bullet_lines(facade._as_list(refresh.get("bullets"))))
    lines += ["", "#### 단계", ""]
    stages = facade._as_list(refresh.get("stages"))
    stage_line_count = 0
    for stage in stages:
        row = facade._as_dict(stage)
        if not row:
            continue
        stage_line_count += 1
        lines.append(
            f"- {facade._text(row.get('stage'))}: {facade._text(row.get('label'))}; "
            f"effective={row.get('effective')}; {facade._text(row.get('summary'))}"
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
        f"- strategy_horizon: {facade._text(horizon.get('strategy_horizon'))}",
        f"- hold_window_sec: min={hold.get('min_sec')}, target={hold.get('target_sec')}, max={hold.get('max_sec')}",
        f"- preferred_exit: {facade._text(handoff.get('preferred_exit') or exit_guidance.get('profit_take_style'))}",
        f"- hold_bias: {facade._text(handoff.get('hold_bias'))}",
        f"- do_not_force_hold: {handoff.get('do_not_force_hold')}",
        f"- allow_early_exit: {exit_guidance.get('allow_early_exit')}",
        "",
        "#### 무효화 조건",
        "",
        *facade._bullet_lines(facade._as_list(horizon.get("invalidation_conditions"))),
        "",
        "---",
        "",
        "## 운영자 검토 요약",
        "",
        "> 아래 내용은 전략가 원문을 기준으로 한 deterministic 검토입니다. 추가 LLM 호출은 포함하지 않습니다.",
        "",
        f"- 검토 결론: **{facade._text(readout.get('headline'))}**",
        f"- 주요 원인: {facade._text(readout.get('root_cause'))}",
        "",
        "### 잘 된 점",
        "",
        *facade._bullet_lines(facade._as_list(readout.get("good_points"))),
        "",
        "### 문제점",
        "",
        *facade._bullet_lines(facade._as_list(readout.get("issues"))),
        "",
        "### 권고 액션",
        "",
        *facade._bullet_lines(facade._as_list(readout.get("recommended_actions"))),
        "",
        "### 검증 포인트",
        "",
        *facade._bullet_lines(facade._as_list(readout.get("validation_questions"))),
        "",
        "---",
        "",
        "## 근거",
        "",
        f"- source_response_json: `{payload.get('source_response_json')}`",
        f"- source_canonical_strategist_json: `{payload.get('source_canonical_strategist_json')}`",
        f"- run_id: `{facade._text(meta.get('run_id'), '')}`",
        f"- saved_at: `{facade._text(meta.get('saved_at'), '')}`",
        f"- generated_at: `{facade._text(payload.get('generated_at'), '')}`",
        "",
    ]
    return "\n".join(lines)
