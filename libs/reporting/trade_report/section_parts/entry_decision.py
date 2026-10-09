from __future__ import annotations

import json
from typing import Any, Dict, Mapping

def build_entry_decision_summary(
    entry_summary: Dict[str, Any],
    scanner_reason: Dict[str, Any],
    market_context: Dict[str, Any],
    monitor_reason: Dict[str, Any],
    action: str,
    *,
    deps: Mapping[str, Any],
) -> str:
    _build_scanner_choice_summary = deps["build_scanner_choice_summary"]
    _clip = deps["clip"]
    _entry_gate_score_relation = deps["entry_gate_score_relation"]
    _entry_path_label = deps["entry_path_label"]
    _entry_reason_label = deps["entry_reason_label"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _operator_action_label = deps["operator_action_label"]
    _scanner_monitor_fallback_context = deps["scanner_monitor_fallback_context"]
    reason_human = _clip(entry_summary.get("reason_human"), max_len=600)
    reason_label = _entry_reason_label(reason_human)
    grouped_trace = (
        monitor_reason.get("entry_grouped_logic_trace")
        if isinstance(monitor_reason.get("entry_grouped_logic_trace"), dict)
        else {}
    )
    entry_scores = (
        monitor_reason.get("entry_condition_scores")
        if isinstance(monitor_reason.get("entry_condition_scores"), dict)
        else {}
    )
    symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24)
    rank = scanner_reason.get("selected_rank")
    triggered_path = _entry_path_label(
        grouped_trace.get("triggered_path")
        or monitor_reason.get("entry_condition_path")
    )
    playbook = _market_token_label(market_context.get("playbook")) or _clip(market_context.get("playbook"), max_len=32)
    confidence_score = _num_opt(entry_scores.get("confidence_score"))
    confidence_threshold = _num_opt(entry_scores.get("confidence_threshold"))
    entry_quality_score = _num_opt(entry_scores.get("entry_quality_score"))
    entry_quality_tier = _clip(entry_scores.get("entry_quality_tier"), max_len=24)
    entry_quality_path = _entry_path_label(entry_scores.get("entry_quality_path"))
    entry_hard_gate_passed = entry_scores.get("entry_hard_gate_passed")
    entry_hard_gate_blockers = entry_scores.get("entry_hard_gate_blockers")
    if not isinstance(entry_hard_gate_blockers, list):
        entry_hard_gate_blockers = []
    fallback_ctx = _scanner_monitor_fallback_context(scanner_reason)

    summary_parts: List[str] = []
    if reason_label:
        summary_parts.append(f"진입은 {reason_label} 조건에서 실행됐습니다.")
    if fallback_ctx["used"] and fallback_ctx["scanner_top_pick_symbol"]:
        rank_text = f"{rank}위" if rank not in (None, "") else "후보"
        fallback_sentence = (
            f"스캐너 상위 후보 {fallback_ctx['scanner_top_pick_symbol']}은 모니터 단계에서 보류됐고 "
            f"{symbol} 차순위 재평가 {rank_text} 진입으로 전환됐습니다."
        )
        if fallback_ctx["reason"]:
            fallback_sentence = (
                f"스캐너 상위 후보 {fallback_ctx['scanner_top_pick_symbol']}은 {fallback_ctx['reason']} 이유로 보류됐고 "
                f"{symbol} 차순위 재평가 {rank_text} 진입으로 전환됐습니다."
            )
        if fallback_ctx["trigger_reason"]:
            fallback_sentence += f" 실제 트리거는 {fallback_ctx['trigger_reason']}였습니다."
        summary_parts.append(fallback_sentence)
    elif symbol and rank not in (None, ""):
        summary_parts.append(f"{symbol}이 스캐너 {rank}위 후보로 올라온 뒤 매수로 이어졌습니다.")
    elif symbol:
        summary_parts.append(f"{symbol}에 대한 매수 판단으로 진입이 이어졌습니다.")
    if playbook and triggered_path:
        if playbook == "눌림목" and triggered_path != "눌림목·거래량 경로":
            summary_parts.append(f"전략가 플레이북은 {playbook}이었지만 실제 엔트리는 {triggered_path}에서 확정됐습니다.")
        else:
            summary_parts.append(f"실제 엔트리 경로는 {triggered_path}였습니다.")
    elif triggered_path:
        summary_parts.append(f"실제 엔트리 경로는 {triggered_path}였습니다.")
    if confidence_score is not None and confidence_threshold is not None:
        relation = _entry_gate_score_relation(confidence_score, confidence_threshold)
        particle = "과" if relation == "동일했습니다" else "을"
        summary_parts.append(
            f"진입 게이트 점수는 {confidence_score:.4f}이며 기준 {confidence_threshold:.4f}{particle} {relation}. "
            "이 값은 확률형 신뢰도가 아니라 모니터 진입 조건의 경로 점수입니다."
        )
    if entry_quality_score is not None:
        quality_bits = [f"진입 품질 점수는 {entry_quality_score:.4f}"]
        if entry_quality_tier:
            quality_bits.append(f"등급 {entry_quality_tier}")
        if entry_quality_path:
            quality_bits.append(f"우세 경로 {entry_quality_path}")
        summary_parts.append(" / ".join(quality_bits) + "였습니다. 이 값은 관측용이며 매수 허용 기준으로 쓰지 않습니다.")
        if entry_hard_gate_passed is False:
            blocker_text = ", ".join(str(x or "").replace("_", " ") for x in entry_hard_gate_blockers[:4] if str(x or "").strip())
            if blocker_text:
                summary_parts.append(
                    f"따라서 품질 점수가 높아도 hard gate는 미통과였으며 차단 축은 {blocker_text}였습니다."
                )
            else:
                summary_parts.append("따라서 품질 점수가 높아도 hard gate는 미통과였고 매수 허가로 해석하지 않습니다.")
        elif entry_hard_gate_passed is True:
            summary_parts.append("hard gate도 통과해 품질 점수와 실제 진입 허가가 같은 방향이었습니다.")
    if summary_parts:
        return " ".join(summary_parts)
    scanner_summary = _build_scanner_choice_summary(scanner_reason, market_context)
    if scanner_summary:
        entry_action = _operator_action_label(_clip(entry_summary.get("action"), max_len=24) or action or "BUY")
        return f"{scanner_summary} 이에 따라 진입 판단은 {entry_action}로 이어졌습니다."
    return "진입 판단 근거는 저장된 데이터 범위 안에서 충분히 확인되지 않았습니다."



def select_entry_decision_detail(story_input: Dict[str, Any], entry_summary: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _as_dict = deps["as_dict"]
    _clip = deps["clip"]
    monitor_timeline = _as_dict(story_input.get("monitor_timeline"))
    rows = monitor_timeline.get("entry_decision_details")
    if not isinstance(rows, list) or not rows:
        artifacts = _as_dict(story_input.get("artifacts"))
        monitor_evidence_path = _clip(artifacts.get("monitor_evidence_json"), max_len=500)
        if monitor_evidence_path:
            try:
                from pathlib import Path

                path = Path(monitor_evidence_path)
                if path.exists():
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(payload, dict):
                        rows = payload.get("entry_decision_details")
            except Exception:
                rows = rows if isinstance(rows, list) else []
    if not isinstance(rows, list):
        return {}
    entry_run_id = _clip(entry_summary.get("run_id"), max_len=120)
    best: Dict[str, Any] = {}
    best_score = -1
    for row in rows:
        event = _as_dict(row)
        payload = _as_dict(event.get("payload"))
        if not payload:
            continue
        decision = _clip(payload.get("decision"), max_len=24).upper()
        entry_triggered = bool(payload.get("entry_triggered"))
        buy_submitted = bool(payload.get("buy_submitted"))
        if decision != "BUY" and not entry_triggered and not buy_submitted:
            continue
        score = 0
        if entry_run_id and _clip(event.get("run_id"), max_len=120) == entry_run_id:
            score += 100
        if decision == "BUY":
            score += 40
        if entry_triggered:
            score += 30
        if buy_submitted:
            score += 20
        if payload.get("entry_condition_path") or _as_dict(payload.get("grouped_logic_trace")).get("triggered_path"):
            score += 10
        if score > best_score:
            best_score = score
            best = event
    return best



def resolve_entry_monitor_reason(
    story_input: Dict[str, Any],
    monitor_reason: Dict[str, Any],
    entry_summary: Dict[str, Any],
    *,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    _as_dict = deps["as_dict"]
    _compact_entry_gate_snapshot = deps["compact_entry_gate_snapshot"]
    _entry_gate_signature = deps["entry_gate_signature"]
    _entry_snapshot_as_post_entry_observation = deps["entry_snapshot_as_post_entry_observation"]
    _looks_like_post_entry_monitor_snapshot = deps["looks_like_post_entry_monitor_snapshot"]
    _select_entry_decision_detail = deps["select_entry_decision_detail"]
    entry_detail = _select_entry_decision_detail(story_input, entry_summary)
    payload = _as_dict(entry_detail.get("payload"))
    if not payload:
        if _looks_like_post_entry_monitor_snapshot(story_input, monitor_reason):
            return _entry_snapshot_as_post_entry_observation(monitor_reason)
        return monitor_reason

    resolved = dict(monitor_reason or {})
    post_entry_snapshot = _compact_entry_gate_snapshot(monitor_reason)

    grouped_trace = _as_dict(payload.get("grouped_logic_trace"))
    condition_scores = _as_dict(payload.get("condition_scores"))
    entry_thresholds = (
        _as_dict(payload.get("applied_policy"))
        or _as_dict(payload.get("effective_policy"))
        or _as_dict(payload.get("received_policy"))
    )
    entry_metrics = _as_dict(payload.get("metrics")) or _as_dict(payload.get("entry_metrics"))
    if grouped_trace:
        resolved["entry_grouped_logic_trace"] = grouped_trace
    if condition_scores:
        resolved["entry_condition_scores"] = condition_scores
    if entry_metrics:
        resolved["entry_metrics"] = entry_metrics
    if payload.get("entry_condition_path") not in (None, ""):
        resolved["entry_condition_path"] = payload.get("entry_condition_path")
    if isinstance(payload.get("entry_condition_paths_passed"), list):
        resolved["entry_condition_paths_passed"] = list(payload.get("entry_condition_paths_passed") or [])
    if entry_thresholds:
        resolved["entry_thresholds"] = entry_thresholds
    if payload.get("entry_reason") not in (None, ""):
        resolved["entry_reason"] = payload.get("entry_reason")
    resolved["entry_gate_snapshot_source"] = "entry_decision_detail"
    if entry_detail.get("ts") not in (None, ""):
        resolved["entry_gate_snapshot_ts"] = entry_detail.get("ts")
    if entry_detail.get("run_id") not in (None, ""):
        resolved["entry_gate_snapshot_run_id"] = entry_detail.get("run_id")

    if post_entry_snapshot and _entry_gate_signature(post_entry_snapshot) != _entry_gate_signature(resolved):
        resolved["post_entry_gate_observation"] = post_entry_snapshot
    return resolved



