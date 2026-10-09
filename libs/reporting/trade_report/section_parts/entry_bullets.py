from __future__ import annotations

import json
from typing import Any, Dict, Mapping

def build_entry_decision_bullets(
    entry_summary: Dict[str, Any],
    scanner_reason: Dict[str, Any],
    market_context: Dict[str, Any],
    monitor_reason: Dict[str, Any],
    action: str,
    *,
    deps: Mapping[str, Any],
) -> List[str]:
    _as_dict = deps["as_dict"]
    _clip = deps["clip"]
    _dedupe_list = deps["dedupe_list"]
    _entry_gate_bits = deps["entry_gate_bits"]
    _entry_gate_score_relation = deps["entry_gate_score_relation"]
    _entry_path_label = deps["entry_path_label"]
    _entry_reason_label = deps["entry_reason_label"]
    _korean_predicate = deps["korean_predicate"]
    _listify = deps["listify"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _operator_action_label = deps["operator_action_label"]
    bullets: List[str] = [
        f"진입 run은 {_clip(entry_summary.get('run_id'), max_len=80) or '기록 없음'}입니다.",
        f"진입 시각은 {_clip(entry_summary.get('ts'), max_len=80) or '기록 없음'}입니다.",
        f"진입 액션은 {_operator_action_label(_clip(entry_summary.get('action'), max_len=40) or action)}였습니다.",
    ]
    reason_label = _entry_reason_label(entry_summary.get("reason_human"))
    if reason_label:
        bullets.append(f"진입 사유는 {reason_label}{_korean_predicate(reason_label)}")

    symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24)
    rank = scanner_reason.get("selected_rank")
    selected_score = _num_opt(scanner_reason.get("selected_score"))
    if symbol and rank not in (None, "") and selected_score is not None:
        bullets.append(f"진입 시점 스캐너에서는 {symbol}이 {rank}위, 종합 점수 {selected_score:.3f}였습니다.")

    grouped_trace = (
        monitor_reason.get("entry_grouped_logic_trace")
        if isinstance(monitor_reason.get("entry_grouped_logic_trace"), dict)
        else {}
    )
    triggered_path = _entry_path_label(grouped_trace.get("triggered_path") or monitor_reason.get("entry_condition_path"))
    paths_passed = [
        _entry_path_label(item)
        for item in _listify(
            grouped_trace.get("paths_passed") or monitor_reason.get("entry_condition_paths_passed"),
            max_items=4,
            max_len=80,
        )
        if _entry_path_label(item)
    ]
    if triggered_path or paths_passed:
        parts: List[str] = []
        if triggered_path:
            parts.append(f"실제 진입 경로는 {triggered_path}였습니다")
        if paths_passed:
            parts.append(f"통과 경로는 {', '.join(paths_passed)}였습니다")
        bullets.append(". ".join(parts) + ".")

    gate_bits = _entry_gate_bits(grouped_trace)
    if gate_bits:
        bullets.append("진입 게이트 상태는 " + ", ".join(gate_bits) + "였습니다.")

    entry_scores = (
        monitor_reason.get("entry_condition_scores")
        if isinstance(monitor_reason.get("entry_condition_scores"), dict)
        else {}
    )
    confidence_score = _num_opt(entry_scores.get("confidence_score"))
    confidence_threshold = _num_opt(entry_scores.get("confidence_threshold"))
    if confidence_score is not None and confidence_threshold is not None:
        relation = _entry_gate_score_relation(confidence_score, confidence_threshold)
        particle = "과" if relation == "동일했습니다" else "을"
        bullets.append(
            f"진입 게이트 점수는 {confidence_score:.4f}이며 기준 {confidence_threshold:.4f}{particle} {relation}. "
            "표시 목적은 확률형 신뢰도보다 진입 조건 통과 여부 확인입니다."
        )
    entry_quality_score = _num_opt(entry_scores.get("entry_quality_score"))
    if entry_quality_score is not None:
        entry_quality_tier = _clip(entry_scores.get("entry_quality_tier"), max_len=24) or "-"
        entry_quality_path = _entry_path_label(entry_scores.get("entry_quality_path")) or "-"
        bullets.append(
            f"진입 품질 점수는 {entry_quality_score:.4f}, 등급은 {entry_quality_tier}, 우세 경로는 {entry_quality_path}였습니다. "
            "이 점수는 관측용이며 매수 허용 여부를 직접 바꾸지 않습니다."
        )
        entry_hard_gate_passed = entry_scores.get("entry_hard_gate_passed")
        entry_hard_gate_blockers = entry_scores.get("entry_hard_gate_blockers")
        if not isinstance(entry_hard_gate_blockers, list):
            entry_hard_gate_blockers = []
        if entry_hard_gate_passed is False:
            blocker_text = ", ".join(
                str(x or "").replace("_", " ")
                for x in entry_hard_gate_blockers[:4]
                if str(x or "").strip()
            )
            if blocker_text:
                bullets.append(
                    f"품질 점수가 높아도 hard gate는 미통과였습니다. 차단 축은 {blocker_text}였습니다."
                )
            else:
                bullets.append("품질 점수가 높아도 hard gate는 미통과였으므로 매수 허가로 해석하지 않습니다.")
        elif entry_hard_gate_passed is True:
            bullets.append("hard gate도 통과해 품질 점수와 실제 진입 허가가 같은 방향이었습니다.")

    post_entry_observation = _as_dict(monitor_reason.get("post_entry_gate_observation"))
    post_grouped_trace = _as_dict(post_entry_observation.get("entry_grouped_logic_trace"))
    post_entry_scores = _as_dict(post_entry_observation.get("entry_condition_scores"))
    post_gate_bits = _entry_gate_bits(post_grouped_trace, post_entry_scores)
    if post_gate_bits:
        post_score = _num_opt(post_entry_scores.get("confidence_score"))
        post_threshold = _num_opt(post_entry_scores.get("confidence_threshold"))
        score_text = ""
        if post_score is not None and post_threshold is not None:
            score_text = f" 점수는 {post_score:.4f} / 기준 {post_threshold:.4f}였습니다."
        bullets.append(
            "사후 모니터 재평가 게이트는 "
            + ", ".join(post_gate_bits)
            + f"였습니다.{score_text} 이는 매수 후 보유·청산 구간의 재평가 상태입니다."
        )

    entry_thresholds = (
        monitor_reason.get("entry_thresholds")
        if isinstance(monitor_reason.get("entry_thresholds"), dict)
        else {}
    )
    timeframe = entry_thresholds.get("timeframe_minutes")
    breakout_lookback = entry_thresholds.get("breakout_lookback")
    volume_ratio_min = _num_opt(entry_thresholds.get("volume_ratio_min"))
    require_vwap_reclaim = entry_thresholds.get("require_vwap_reclaim")
    require_rebound = entry_thresholds.get("require_rebound")
    threshold_bits: List[str] = []
    if timeframe not in (None, ""):
        threshold_bits.append(f"{int(float(timeframe))}분봉")
    if breakout_lookback not in (None, ""):
        threshold_bits.append(f"돌파 확인 기준 봉 수 {int(float(breakout_lookback))}")
    if volume_ratio_min is not None:
        threshold_bits.append(f"최소 거래량 비율 {volume_ratio_min:.2f}")
    if require_vwap_reclaim is not None:
        threshold_bits.append(f"VWAP 재회복 {'필수' if require_vwap_reclaim else '비필수'}")
    if require_rebound is not None:
        threshold_bits.append(f"반등 확인 {'필수' if require_rebound else '비필수'}")
    if threshold_bits:
        bullets.append("적용 정책은 " + ", ".join(threshold_bits) + "였습니다.")

    playbook = _market_token_label(market_context.get("playbook")) or _clip(market_context.get("playbook"), max_len=32)
    if playbook and triggered_path:
        bullets.append(f"전략가 플레이북은 {playbook}, 실제 진입 경로는 {triggered_path}였습니다.")

    return _dedupe_list(bullets, max_items=12, max_len=260)



