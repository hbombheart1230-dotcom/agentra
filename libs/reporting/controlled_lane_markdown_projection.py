"""controlled_mock_lane_report projections (moved verbatim from controlled_mock_lane_report).

Module globals and helpers are resolved on ``facade`` (the controlled_mock_lane_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def render_controlled_lane_report_lines(report: Mapping[str, Any], *, facade: Any) -> list[str]:
    surface = facade.controlled_lane_surface_from_report(report)
    if not surface:
        return []
    evidence = facade._mapping(surface.get("evidence"))
    window = facade._mapping(surface.get("expected_hold_window"))
    lines = [
        f"* 실행 레인: **{facade._text(surface.get('lane_label')) or facade._text(surface.get('lane_id'))}**",
        f"* 신호 ID: `{facade._text(surface.get('signal_id')) or '-'}`",
        f"* 선택 권한: {facade._text(surface.get('selection_authority')) or 'deterministic_independent_lane'}",
        f"* Scanner 순위: {'해당 없음' if surface.get('scanner_rank_applicable') is False else '적용'}",
        f"* LLM 사용: {'예' if surface.get('llm_used') else '아니오'}",
    ]
    if surface.get("score") not in (None, ""):
        lines.append(f"* 신호 점수: {surface.get('score')}")
    if evidence:
        evidence_text = " / ".join(f"{key}={value}" for key, value in evidence.items() if value not in (None, "", [], {}))
        if evidence_text:
            lines.append(f"* 고정 가설 근거: {evidence_text}")
    if window:
        lines.append("* 고정 보유 구간: " f"최소 {window.get('min_sec', '-')}초 / 목표 {window.get('target_sec', '-')}초 / 최대 {window.get('max_sec', '-')}초")
    if surface.get("stage3_horizon_review_allowed"):
        lines.append("* R3 연결: 허용. 3차 전략가의 보유기간 재검토를 적용할 수 있습니다.")
    else:
        lines.append("* R3 연결: 차단. 독립 레인과 고정 horizon 비교를 위해 3차 전략가가 보유기간을 변경하지 않습니다.")
    lines.append("* 주문 범위: 키움 모의투자 검증 전용")
    return lines
