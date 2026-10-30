"""Strategist LLM summary stage-specific clean Markdown renderer (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def render_stage_specific_summary_markdown_clean(payload: Dict[str, Any], *, facade: Any) -> str:
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
