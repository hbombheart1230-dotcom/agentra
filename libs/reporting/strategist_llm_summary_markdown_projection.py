"""Strategist LLM summary Markdown projection (P1.5 BATCH04-A, DEV-A).

The effective (last-bound) ``render_strategist_llm_summary_markdown`` and the stage-specific/clean formatting
helpers it reaches, moved from ``libs.reporting.strategist_llm_summary``. The shadowed earlier renderer and its
legacy-only helpers stay untouched in the facade module; helpers resolve on the injected facade at call time.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List


def _json_inline(value: Any, *, facade: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


def _watch_scope_label_clean(value: Dict[str, Any], *, facade: Any) -> str:
    if not value:
        return ""
    rank = value.get("max_priority_rank")
    runner_ups = value.get("max_runner_ups")
    parts: List[str] = []
    if rank not in (None, ""):
        parts.append(f"{rank}위까지")
    if runner_ups not in (None, ""):
        parts.append(f"차순위 {runner_ups}개")
    if value.get("cascade_enabled") not in (None, ""):
        parts.append(f"cascade {'활성' if bool(value.get('cascade_enabled')) else '비활성'}")
    return " / ".join(parts)


def _strategy_patch_status_clean(detail: Dict[str, Any], *, facade: Any) -> str:
    required_keys = (
        "pre_llm_playbook",
        "llm_requested_playbook",
        "requested_playbook",
        "requested_playbook_source",
        "final_playbook",
        "tactical_strategy",
        "strategy_scores",
        "rejected_strategy_reasons",
        "candidate_watch_policy",
    )
    missing = [key for key in required_keys if not detail.get(key)]
    if not missing:
        return "적용됨"
    return f"일부 누락 ({', '.join(missing)})"


def _playbook_flow_label(detail: Dict[str, Any], *, facade: Any) -> str:
    pre = facade._text(detail.get("pre_llm_playbook"), "")
    requested = facade._text(detail.get("requested_playbook"), "")
    final = facade._text(detail.get("final_playbook"), "")
    parts = [part for part in (pre, requested, final) if part]
    if not parts:
        return "-"
    flow = " -> ".join(parts)
    source = facade._text(detail.get("requested_playbook_source"), "")
    return f"{flow} (source={source})" if source else flow


def _score_value(value: Any, *, facade: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("-inf")


def _score_label(value: Any, *, facade: Any) -> str:
    numeric = facade._score_value(value)
    if numeric != float("-inf"):
        return f"{numeric:.2f}".rstrip("0").rstrip(".")
    return facade._text(value)


def _strategy_score_lines_clean(scores: Dict[str, Any], *, selected: str, facade: Any) -> List[str]:
    if not scores:
        return ["- -"]
    rows = sorted(scores.items(), key=lambda row: (facade._score_value(row[1]), str(row[0])), reverse=True)
    lines: List[str] = []
    for name, score in rows:
        marker = " (선택)" if str(name) == selected else ""
        lines.append(f"- {name}: {facade._score_label(score)}{marker}")
    return lines


def _rejected_strategy_lines(reasons: Dict[str, Any], *, selected: str, facade: Any) -> List[str]:
    if not reasons:
        return ["- -"]
    lines: List[str] = []
    for name in sorted(reasons):
        if str(name) == selected:
            continue
        reason = reasons.get(name)
        if isinstance(reason, (dict, list)):
            reason_text = facade._json_inline(reason)
        else:
            reason_text = facade._text(reason)
        lines.append(f"- {name}: {reason_text}")
    return lines if lines else ["- -"]


def _bullet_lines(items: List[Any], *, empty: str = "-", facade: Any) -> List[str]:
    rows = [f"- {item}" for item in items if str(item or "").strip()]
    return rows if rows else [f"- {empty}"]


def _directive_line(label: str, value: Dict[str, Any], *, facade: Any) -> str:
    if not value:
        return f"- {label}: -"
    action = facade._text(value.get("action"))
    target = value.get("target")
    if target is None:
        target = value.get("target_fields") or value.get("target_axes")
    reason = facade._text(value.get("reason"), "")
    target_text = ", ".join(str(x) for x in target) if isinstance(target, list) else facade._text(target, "")
    if target_text and reason:
        return f"- {label}: **{action}** -> {target_text}; {reason}"
    if target_text:
        return f"- {label}: **{action}** -> {target_text}"
    if reason:
        return f"- {label}: **{action}**; {reason}"
    return f"- {label}: **{action}**"


def _memory_usage_lines_clean(memory: Dict[str, Any], *, facade: Any) -> List[str]:
    if not bool(memory.get("available")):
        return ["- 메모리 사용 trace: -"]
    lines = [
        f"- 활성 레이어: {', '.join(str(x) for x in facade._as_list(memory.get('active_layers'))) or '-'}",
        f"- 우선순위: {' -> '.join(str(x) for x in facade._as_list(memory.get('priority_order'))) or '-'}",
        f"- 요약: {facade._text(memory.get('human_summary'))}",
    ]
    applied = facade._as_dict(memory.get("applied_to_strategy"))
    if applied:
        lines.append(f"- 전략 반영: playbook={facade._text(applied.get('playbook_effect'))}, risk={facade._text(applied.get('risk_posture_effect'))}")
        lines.append(
            f"- scanner/monitor 반영: scanner={facade._text(applied.get('scanner_guidance_effect'))}, "
            f"monitor={facade._text(applied.get('monitor_policy_effect'))}"
        )
    layer_decisions = facade._as_dict(memory.get("layer_decisions"))
    for layer in ("daily", "weekly", "monthly", "symbol"):
        row = facade._as_dict(layer_decisions.get(layer))
        if not row:
            continue
        summary = facade._as_dict(row.get("operator_summary"))
        metrics = []
        if summary.get("trade_count") is not None:
            metrics.append(f"trades={summary.get('trade_count')}")
        if summary.get("win_rate") is not None:
            metrics.append(f"win_rate={summary.get('win_rate')}")
        if summary.get("avg_return_pct") is not None:
            metrics.append(f"avg_return_pct={summary.get('avg_return_pct')}")
        metric_text = f" ({', '.join(metrics)})" if metrics else ""
        lines.append(
            f"- {layer}: used={row.get('used')} status={facade._text(row.get('status'), '')} "
            f"effect={facade._text(row.get('effect'), '')}{metric_text}"
        )
    return lines


def _news_usage_lines_clean(news: Dict[str, Any], *, facade: Any) -> List[str]:
    if not bool(news.get("available")):
        return ["- 뉴스 사용 trace: -"]
    query_targets = ", ".join(str(x) for x in facade._as_list(news.get("query_targets"))[:10]) or "-"
    return [
        f"- 검색/수집 대상: {query_targets}",
        f"- 사용 요약: {facade._text(news.get('human_summary'))}",
        f"- 시장 효과: {facade._text(news.get('market_effect'))}",
        f"- 플레이북 효과: {facade._text(news.get('playbook_effect'))}",
        f"- 스캐너 반영: {facade._text(news.get('scanner_guidance_effect'))}",
        f"- 모니터 반영: {facade._text(news.get('monitor_policy_effect'))}",
        f"- 근거 헤드라인 수: market={news.get('market_headline_count')}, candidate={news.get('candidate_headline_count')}",
        f"- query reasoning: {facade._text(news.get('news_query_reasoning'))}",
    ]


def _quality_audit_lines(payload: Dict[str, Any], *, facade: Any) -> List[str]:
    rail = facade._as_dict(payload.get("market_regime_rail"))
    news = facade._as_dict(payload.get("news_quality_audit"))
    risk_policy = facade._as_dict(payload.get("risk_off_exception_policy"))
    risk_conditions = facade._as_list(payload.get("risk_off_exception_conditions"))
    news_event = facade._as_dict(payload.get("news_event_intelligence"))
    news_event_usage = facade._as_dict(payload.get("news_event_intelligence_usage"))
    output = facade._as_dict(payload.get("strategist_output_quality_audit"))
    metrics = facade._as_dict(rail.get("metrics"))
    rail_issues = facade._as_list(rail.get("issues"))
    news_issues = facade._as_list(news.get("issues"))
    output_issues = facade._as_list(output.get("issues"))

    def _issue_text(items: List[Any]) -> str:
        return ", ".join(str(x) for x in items if str(x or "").strip()) or "-"

    def _watch_text(items: List[Any], key: str) -> str:
        values: List[str] = []
        for item in items:
            if isinstance(item, dict):
                text = str(item.get(key) or "").strip()
            else:
                text = str(item or "").strip()
            if text:
                values.append(text)
        return ", ".join(values[:6]) or "-"

    return [
        "## Input/Output Quality Audit",
        "",
        "### Market Regime Rail",
        "",
        f"- market_regime: {facade._text(rail.get('market_regime'), '-')}",
        f"- market_regime_rail: {facade._text(rail.get('market_regime_rail'), '-')}",
        f"- risk_score: {rail.get('risk_score')}",
        f"- kospi_pct: {metrics.get('kospi_pct')}",
        f"- kosdaq_pct: {metrics.get('kosdaq_pct')}",
        f"- breadth_score: {metrics.get('breadth_score')}",
        f"- issues: {_issue_text(rail_issues)}",
        "",
        "### News Quality",
        "",
        f"- status: {facade._text(news.get('status'), '-')}",
        f"- headline_count: {news.get('headline_count')}",
        f"- market_headline_count: {news.get('market_headline_count')}",
        f"- candidate_headline_count: {news.get('candidate_headline_count')}",
        f"- query_target_count: {news.get('query_target_count')}",
        f"- issues: {_issue_text(news_issues)}",
        "",
        "### Risk-Off Exceptions",
        "",
        f"- risk_off_active: {risk_policy.get('risk_off_active')}",
        f"- allowed_exception_conditions: {_issue_text(facade._as_list(risk_policy.get('allowed_exception_conditions')))}",
        f"- strategist_reported_conditions: {_issue_text(risk_conditions)}",
        f"- instruction: {facade._text(risk_policy.get('instruction'), '-')}",
        "",
        "### News Event Intelligence",
        "",
        f"- behavior_effect: {facade._text(news_event.get('behavior_effect'), 'observation_only')}",
        f"- trading_action_allowed: {news_event.get('trading_action_allowed', False)}",
        f"- event_count: {facade._as_dict(news_event.get('input_summary')).get('event_count', 0)}",
        f"- theme_watchlist: {_watch_text(facade._as_list(news_event.get('theme_watchlist')), 'theme')}",
        f"- symbol_watchlist: {_watch_text(facade._as_list(news_event.get('symbol_watchlist')), 'symbol')}",
        f"- llm_usage_status: {facade._text(news_event_usage.get('status'), '-')}",
        f"- llm_usage_reason: {facade._text(news_event_usage.get('reason'), '-')}",
        "",
        "### Strategist Output Quality",
        "",
        f"- status: {facade._text(output.get('status'), '-')}",
        f"- decision: {facade._text(output.get('decision'), '-')}",
        f"- confidence: {output.get('confidence')}",
        f"- final_playbook: {facade._text(output.get('final_playbook'), '-')}",
        f"- tactical_strategy: {facade._text(output.get('tactical_strategy'), '-')}",
        f"- issues: {_issue_text(output_issues)}",
        "",
    ]


def _render_stage_specific_summary_markdown_clean(payload: Dict[str, Any], *, facade: Any) -> str:
    meta = facade._as_dict(payload.get("llm_meta"))
    readout = facade._as_dict(payload.get("operator_readout"))
    stage_decision = facade._as_dict(payload.get("stage_decision"))
    detail = facade._as_dict(payload.get("strategy_detail"))
    watch = facade._as_dict(detail.get("candidate_watch_policy"))
    monitor_instruction = facade._as_dict(stage_decision.get("monitor_instruction"))
    entry_policy_delta = facade._as_dict(stage_decision.get("entry_policy_delta"))
    commander_actionability = facade._as_dict(stage_decision.get("commander_actionability"))
    runners = ", ".join(str(x) for x in facade._as_list(stage_decision.get("runner_up_order"))) or "-"
    triggers = ", ".join(str(x) for x in facade._as_list(stage_decision.get("priority_exit_triggers"))) or "-"

    lines: List[str] = [
        f"# Strategist LLM Summary ({facade._text(meta.get('day'), '-')})",
        "",
        "---",
        "",
        "## 단계별 전략가 LLM 출력",
        "",
        f"- 상태: {facade._text(meta.get('status'))} / model={facade._text(meta.get('model'))}",
        f"- 단계: {stage_decision.get('stage_index')} / {facade._text(stage_decision.get('stage_name'))}",
        f"- 호출 종류: {facade._text(stage_decision.get('call_kind'))}",
        f"- stage component: {facade._text(stage_decision.get('stage_component') or meta.get('stage_component'))}",
        "",
        "### 결정",
        "",
        f"- decision: **{facade._text(stage_decision.get('decision'))}**",
        f"- target_symbol: {facade._text(stage_decision.get('target_symbol'))}",
        f"- target_rank: {stage_decision.get('target_rank')}",
        f"- runner_up_order: {runners}",
        f"- confidence: {stage_decision.get('confidence')}",
        f"- exit_pressure: {facade._text(stage_decision.get('exit_pressure'), '')}",
        f"- thesis_status: {facade._text(stage_decision.get('thesis_status'), '')}",
        f"- next_check_minutes: {stage_decision.get('next_check_minutes')}",
        f"- priority_exit_triggers: {triggers}",
        "",
        "### 모니터 지시",
        "",
    ]
    if monitor_instruction:
        for key in sorted(monitor_instruction):
            lines.append(f"- {key}: {facade._json_inline(monitor_instruction.get(key))}")
    else:
        lines.append("- -")
    lines += ["", "### 진입 정책 delta", ""]
    if entry_policy_delta:
        for key in sorted(entry_policy_delta):
            lines.append(f"- {key}: {facade._json_inline(entry_policy_delta.get(key))}")
    else:
        lines.append("- -")
    lines += ["", "### 지휘관 적용 가능성", ""]
    if commander_actionability:
        for key in sorted(commander_actionability):
            lines.append(f"- {key}: {facade._json_inline(commander_actionability.get(key))}")
    else:
        lines.append("- -")
    lines += [
        "",
        "### 사유",
        "",
        facade._text(stage_decision.get("reason")),
        "",
        "## Canonical 전략 컨텍스트",
        "",
        f"- final_playbook: {facade._text(detail.get('final_playbook'))}",
        f"- tactical_strategy: {facade._text(detail.get('tactical_strategy'))}",
        f"- playbook_flow: {facade._playbook_flow_label(detail)}",
        f"- candidate_watch: {facade._watch_scope_label_clean(watch) or '-'}",
        "",
        *facade._quality_audit_lines(payload),
        "## 운영 점검",
        "",
        f"- 요약: **{facade._text(readout.get('headline'))}**",
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
