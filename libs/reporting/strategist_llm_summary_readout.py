"""Strategist LLM summary operator readouts (moved verbatim; the two variants are intentionally kept separate).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def operator_readout(payload: Dict[str, Any], stage_decision: Dict[str, Any] | None = None, *, facade: Any) -> Dict[str, Any]:
    stage_decision = facade._as_dict(stage_decision)
    if bool(stage_decision.get("is_stage_specific")):
        stage_name = facade._text(stage_decision.get("stage_name"), "stage_specific")
        decision = facade._text(stage_decision.get("decision"), "-")
        reason = facade._text(stage_decision.get("reason"), "")
        return {
            "headline": f"{stage_name} / decision={decision}",
            "good_points": [
                "Stage-specific strategist response was parsed.",
                "Market-frame fields such as selected_themes are not required for this stage.",
            ],
            "issues": [] if reason else ["stage-specific reason is empty"],
            "root_cause": reason or "stage-specific response did not include a reason",
            "recommended_actions": ["Review the stage decision fields instead of the market-frame section."],
            "validation_questions": ["Confirm monitor/executor behavior followed the stage decision."],
        }

    theme_strategy = facade._as_dict(payload.get("theme_strategy"))
    rationale = facade._text(payload.get("rationale"), "")
    selected_themes = facade._as_list(payload.get("selected_themes"))
    fallback_reason = facade._text(theme_strategy.get("fallback_reason"), "")
    selected_symbol_bias = facade._directive(payload, "selected_symbol_bias_action")

    good_points: List[str] = []
    issues: List[str] = []
    actions: List[str] = []
    validation: List[str] = []

    entry_policy = facade._directive(payload, "entry_policy_action")
    monitor_focus = facade._directive(payload, "monitor_focus_action")
    refresh_action = facade._directive(payload, "refresh_action")

    if entry_policy:
        good_points.append("최근 손실/과매매 피드백을 진입 정책 조정 근거로 명시했습니다.")
    if monitor_focus:
        good_points.append("모니터가 집중해야 할 축을 volume/reclaim처럼 실행 가능한 형태로 남겼습니다.")
    if refresh_action:
        good_points.append("전략 refresh가 요청된 이유와 최종 적용 단계를 분리해 남겼습니다.")

    if not selected_themes:
        issues.append("selected_themes가 비어 있어 테마 기반 전략 분기가 실제로 작동하지 않았습니다.")
        actions.append("다음 실행에서 Commander가 available_themes/theme_strength_packet을 전략가 호출 전에 채우는지 확인합니다.")
        validation.append("다음 전략가 요약에서 selected_themes가 실제 테마명으로 채워지는가?")
    if "best 및 worst" in rationale or "best and worst" in rationale.lower():
        issues.append("전략 메모리에서 같은 플레이북이 best/worst에 동시에 잡혀 방향성 신호가 약합니다.")
        actions.append("best/worst 중복 플레이북은 방향성 bias가 아니라 memory_quality_flag로만 표시합니다.")
    if str(selected_symbol_bias.get("action") or "").strip().lower() == "none":
        issues.append("심볼 메모리 근거가 없어 특정 종목 편향 조정은 적용되지 않았습니다.")
        validation.append("심볼 summary/memory가 누적된 뒤 selected_symbol_bias_action이 계속 none인지 확인합니다.")

    if not good_points:
        good_points.append("전략가 출력은 파싱 가능하며 playbook, entry policy, refresh trace를 포함합니다.")
    if not issues:
        issues.append("즉시 확인할 구조적 문제는 요약에서 감지되지 않았습니다.")
    if not actions:
        actions.append("다음 실행 결과와 비교해 같은 playbook 반복 여부를 확인합니다.")
    if not validation:
        validation.append("다음 실행에서 playbook/theme/entry policy가 시장 입력에 따라 달라지는가?")

    headline_parts = [facade._text(payload.get("playbook"), "unknown")]
    if selected_themes:
        headline_parts.append(f"themes={', '.join(str(x) for x in selected_themes[:3])}")
    else:
        headline_parts.append("theme=none")
    if theme_strategy.get("selection_mode"):
        headline_parts.append(f"mode={theme_strategy.get('selection_mode')}")

    root_cause = fallback_reason or rationale or "전략가 출력의 rationale 확인 필요"
    return {
        "headline": " / ".join(headline_parts),
        "good_points": good_points[:4],
        "issues": issues[:4],
        "root_cause": root_cause,
        "recommended_actions": actions[:4],
        "validation_questions": validation[:4],
    }


def operator_readout_clean(payload: Dict[str, Any], stage_decision: Dict[str, Any] | None = None, *, facade: Any) -> Dict[str, Any]:
    stage_decision = facade._as_dict(stage_decision)
    if bool(stage_decision.get("is_stage_specific")):
        stage_name = facade._text(stage_decision.get("stage_name"), "stage_specific")
        decision = facade._text(stage_decision.get("decision"), "-")
        reason = facade._text(stage_decision.get("reason"), "")
        return {
            "headline": f"{stage_name} / decision={decision}",
            "good_points": [
                "단계별 전략가 응답이 파싱됐습니다.",
                "이 단계는 시장 프레임이 아니므로 selected_themes 같은 1차 필드는 필수가 아닙니다.",
            ],
            "issues": [] if reason else ["단계별 응답의 reason이 비어 있습니다."],
            "root_cause": reason or "단계별 응답에 reason이 포함되지 않았습니다.",
            "recommended_actions": ["시장 프레임 섹션이 아니라 단계별 decision 필드를 확인합니다."],
            "validation_questions": ["모니터/집행 흐름이 이 단계별 decision을 따랐는지 확인합니다."],
        }

    theme_strategy = facade._as_dict(payload.get("theme_strategy"))
    rationale = facade._text(payload.get("rationale"), "")
    selected_themes = facade._as_list(payload.get("selected_themes"))
    fallback_reason = facade._text(theme_strategy.get("fallback_reason"), "")
    selected_symbol_bias = facade._directive(payload, "selected_symbol_bias_action")
    entry_policy = facade._directive(payload, "entry_policy_action")
    monitor_focus = facade._directive(payload, "monitor_focus_action")
    refresh_action = facade._directive(payload, "refresh_action")

    good_points: List[str] = []
    issues: List[str] = []
    actions: List[str] = []
    validation: List[str] = []

    if entry_policy:
        good_points.append("최근 손실/과매매 피드백을 진입 정책 조정 근거로 명시했습니다.")
    if monitor_focus:
        good_points.append("모니터가 집중할 축을 volume/reclaim처럼 실행 가능한 형태로 넘겼습니다.")
    if refresh_action:
        good_points.append("전략 refresh 요청 사유와 최종 적용 단계를 분리해 남겼습니다.")
    if not selected_themes:
        issues.append("selected_themes가 비어 있어 테마 기반 전략 분기가 약합니다.")
        actions.append("다음 실행에서 Commander가 available_themes/theme_strength_packet을 전략가 호출 전에 채우는지 확인합니다.")
        validation.append("다음 전략가 요약에서 selected_themes가 실제 테마명으로 채워지는지 확인합니다.")
    if ("best" in rationale.lower() and "worst" in rationale.lower()) or "best 諛?worst" in rationale:
        issues.append("전략 메모리에서 같은 플레이북이 best/worst에 동시에 잡혀 방향 신호가 혼합됩니다.")
        actions.append("best/worst 중복 플레이북은 방향성 bias가 아니라 memory_quality_flag로만 표시합니다.")
    if str(selected_symbol_bias.get("action") or "").strip().lower() == "none":
        issues.append("성과 메모리 근거가 없어 특정 종목 영향 조정은 적용되지 않았습니다.")
        validation.append("성과 summary/memory가 누적돼도 selected_symbol_bias_action이 계속 none인지 확인합니다.")

    if not good_points:
        good_points.append("전략가 출력은 파싱 가능하며 playbook, entry policy, refresh trace를 포함합니다.")
    if not issues:
        issues.append("즉시 확인할 구조적 문제는 요약에서 감지되지 않았습니다.")
    if not actions:
        actions.append("다음 실행 결과를 비교해 같은 playbook 반복 여부를 확인합니다.")
    if not validation:
        validation.append("다음 실행에서 playbook/theme/entry policy가 시장 입력에 따라 달라지는지 확인합니다.")

    headline_parts = [facade._text(payload.get("playbook"), "unknown")]
    if selected_themes:
        headline_parts.append(f"themes={', '.join(str(x) for x in selected_themes[:3])}")
    else:
        headline_parts.append("theme=none")
    if theme_strategy.get("selection_mode"):
        headline_parts.append(f"mode={theme_strategy.get('selection_mode')}")

    return {
        "headline": " / ".join(headline_parts),
        "good_points": good_points[:4],
        "issues": issues[:4],
        "root_cause": fallback_reason or rationale or "전략가 출력의 rationale 확인 필요",
        "recommended_actions": actions[:4],
        "validation_questions": validation[:4],
    }
