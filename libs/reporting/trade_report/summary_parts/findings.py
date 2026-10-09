from __future__ import annotations

from typing import Any, Dict, List, Mapping


def collect_deterministic_summary_findings(
    *, truth_price: Dict[str, Any], truth_pnl: Dict[str, Any],
    strategist: Dict[str, Any], selection: Dict[str, Any],
    entry: Dict[str, Any], exit_decision: Dict[str, Any],
    memory_app: Dict[str, Any], carryover_exit: bool,
    recovered_partial_exit: bool, combined_blob: str,
    selection_rank: Any, scanner_chart_fit: Dict[str, Any],
    monitor_memory: Dict[str, Any], deps: Mapping[str, Any],
):
    """Return report-only observations; never approve or execute trades."""
    _listify = deps["listify"]
    _as_dict = deps["as_dict"]
    _num_opt = deps["num_opt"]
    deterministic_positives: List[str] = []
    if truth_price.get("broker_fill_price") not in (None, "") or truth_pnl.get("value") not in (None, ""):
        deterministic_positives.append("broker_truth_available")
    if strategist or selection or entry or exit_decision:
        deterministic_positives.append("agent_decision_flow_available")
    if memory_app:
        deterministic_positives.append("policy_memory_surface_available")
    if carryover_exit:
        deterministic_positives.append("carryover_exit_accounted_separately")
    if recovered_partial_exit:
        deterministic_positives.append("recovered_partial_exit_accounted_separately")
    
    deterministic_problems: List[str] = []
    if "monitor_only" in combined_blob or "monitor-only" in combined_blob or "monitor 단독" in combined_blob:
        deterministic_problems.append("monitor_only_path_ratio_high")
    if recovered_partial_exit:
        deterministic_problems.append("entry_evidence_missing_for_recovered_partial_exit")
    if carryover_exit:
        deterministic_problems.append("carryover_exit_requires_separate_date_basis")
    if "peak_drawdown" in combined_blob or "고점 대비 하락폭" in combined_blob:
        deterministic_problems.append("peak_drawdown_exit_needs_review")
    rank_num = _num_opt(selection_rank)
    scanner_chart_fit_score = _num_opt(scanner_chart_fit.get("score")) if scanner_chart_fit else None
    if rank_num is not None and rank_num > 1:
        deterministic_problems.append("entered_lower_rank_after_top_candidate_block")
    if scanner_chart_fit_score is not None and scanner_chart_fit_score < 0.25:
        deterministic_problems.append("scanner_chart_fit_low")
    if "pullback" in combined_blob:
        deterministic_problems.append("pullback_condition_repeated")
    
    root_cause_candidates: List[str] = []
    for row in _listify(monitor_memory.get("applied_deltas")):
        row_obj = _as_dict(row)
        if str(row_obj.get("field") or "") == "breakout_buffer_pct" and (_num_opt(row_obj.get("delta")) or 0.0) > 0:
            root_cause_candidates.append("entry_was_tightened_by_breakout_buffer")
            break
    for row in _listify(monitor_memory.get("exit_deltas")):
        row_obj = _as_dict(row)
        if "peak_drawdown" in str(row_obj.get("field") or "") and (_num_opt(row_obj.get("delta")) or 0.0) < 0:
            root_cause_candidates.append("exit_was_tightened_by_peak_drawdown")
            break
    if rank_num is not None and rank_num > 1:
        root_cause_candidates.append("scanner_monitor_reassessment_after_top_rank_block")
    if scanner_chart_fit_score is not None and scanner_chart_fit_score < 0.25:
        root_cause_candidates.append("scanner_selected_candidate_had_weak_chart_fit")
    if recovered_partial_exit:
        root_cause_candidates.append("recovered_partial_exit_excludes_new_entry_assessment")
    if carryover_exit:
        root_cause_candidates.append("carryover_position_excludes_same_day_scanner_selection_assessment")
    
    validation_questions: List[str] = []
    if recovered_partial_exit:
        validation_questions.append("회수/partial 청산을 완료 거래와 별도 집계했을 때 당일 실현 성과가 어떻게 달라지는가?")
    if carryover_exit:
        validation_questions.append("오버나이트 승인 근거와 당일 청산 컨텍스트가 분리되어 집계됐는가?")
    if "peak_drawdown_exit_needs_review" in deterministic_problems:
        validation_questions.append("peak_drawdown activation/confirm 조건이 실제 손익비를 악화시키는가?")
    if "entered_lower_rank_after_top_candidate_block" in deterministic_problems:
        validation_questions.append("1순위 탈락 후 차순위 진입의 기대값이 충분한가?")
    if "scanner_chart_fit_low" in deterministic_problems:
        validation_questions.append("scanner_chart_fit_score가 낮은 후보가 다른 점수 축 때문에 선택됐는지 확인해야 하는가?")
    if not validation_questions:
        validation_questions.append("진입/청산 정책 조합이 당일 반복 손익 패턴과 일치하는가?")
    
    return (deterministic_positives, deterministic_problems,
            root_cause_candidates, validation_questions)
