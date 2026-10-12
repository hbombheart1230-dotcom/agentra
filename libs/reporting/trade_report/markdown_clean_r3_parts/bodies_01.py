"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body except that every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module, no getattr fallback,
no entry-time capture), so late/use-time lookup and monkeypatching match the original
module-level resolution. Owner never imports the facade.
"""
from __future__ import annotations


def _same_day_current_result_r3_impl(report, *, facade):
    truth_surface = facade._as_dict(report.get("truth_surface"))
    status = facade._as_dict(truth_surface.get("status"))
    status_text = str(status.get("status") or report.get("status") or "").strip().lower()
    if status_text != "closed":
        return {}
    pnl = facade._as_dict(truth_surface.get("pnl"))
    pnl_value = facade._num_opt(pnl.get("value"))
    pnl_pct = facade._num_opt(pnl.get("pct"))
    if pnl_value is None and pnl_pct is None:
        return {}
    classification_value = pnl_value if pnl_value is not None else pnl_pct
    if classification_value is None:
        return {}
    pct_text = ""
    if pnl_pct is not None:
        pct_percent = pnl_pct * 100.0 if abs(pnl_pct) <= 1.0 else pnl_pct
        pct_text = f"{pct_percent:.2f}"
    return {
        "classification": 1 if classification_value > 0 else (-1 if classification_value < 0 else 0),
        "pct_text": pct_text,
    }


def render_trade_report_markdown_clean_r3_impl(report, *, facade):
    lines: List[str] = []

    trade_id = facade._clip(report.get("trade_id"), 80) or "-"
    action = facade._action_label(report.get("action"))
    symbol = facade._clip(report.get("symbol"), 32) or "해당 종목"
    status = facade._status_label(report.get("status"))
    story_type = facade._story_type_label(report.get("story_type"))
    execution_mode = facade._execution_mode_label(report.get("execution_mode_label"))

    lines.append(f"# AI 거래 리포트 ({trade_id})")
    lines.append("")
    lines.append(f"- 이번 거래는 {action} {symbol} 기준으로 정리했습니다.")
    lines.append(f"- 라이프사이클 상태는 {status}입니다.")
    lines.append(f"- 리포트 유형은 {story_type}입니다.")
    lines.append(f"- 실행 모드는 {execution_mode}입니다.")

    lines.extend(facade._section("생성 정보", facade._build_generation_info(report)))
    lines.extend(facade._section("Truth Surface", facade._build_truth_surface(report)))
    lines.extend(facade._section("전략가 프롬프트에서 직접 확인된 메모리", facade._build_prompt_proven_memory(report)))
    lines.extend(facade._section("거래 설명용 사후 복원 메모리", facade._build_reconstructed_trade_memory(report)))
    lines.extend(facade._section("실제로 적용된 결정론적 메모리 bias", facade._build_memory_application(report)))
    lines.extend(facade._section("시장 환경 요약", facade._build_market_context(report)))
    lines.extend(facade._section("전략가 요약", facade._build_strategist_summary(report)))
    lines.extend(facade._section("전략 보유 기간", facade._build_strategy_horizon_lines(report)))
    lines.extend(facade._section("통제 모의투자 레인 근거", facade._render_controlled_lane_report_lines(report)))
    lines.extend(facade._section("전략가 Refresh Trace", facade._build_strategist_refresh_trace(report)))
    lines.extend(facade._section("전략가 Quant Context 사용", facade._render_strategist_quant_context_usage_lines_impl(report)))
    lines.extend(facade._section("전략가 출력 근거", facade._build_strategist_output_surface(report)))
    lines.extend(facade._section("전술/퀀트 진단", facade._render_quant_tactic_report_lines_impl(report)))
    lines.extend(facade._section("선택된 종목 상세 분석", facade._build_symbol_selection(report)))
    lines.extend(facade._section("스캐너 후보 비교", facade._build_scanner_comparison(report)))
    lines.extend(facade._section("가드 승인 결과", facade._build_guard_approval(report)))
    lines.extend(facade._section("진입 상세 근거", facade._build_entry_decision(report)))
    lines.extend(facade._section("보유 경과", facade._build_holding_story(report)))
    lines.extend(facade._section("청산 판단 근거", facade._build_exit_decision(report)))
    post_exit_shadow_lines = facade._build_post_exit_shadow_summary_lines(report)
    if post_exit_shadow_lines:
        if str(post_exit_shadow_lines[0]).strip() == "### 매도 후 가격 추적 (관측-only)":
            post_exit_shadow_lines = post_exit_shadow_lines[2:]
        lines.extend(facade._section("매도 후 가격 추적 (관측-only)", post_exit_shadow_lines))
    lines.extend(facade._section("모니터 스냅샷", facade._build_monitor_snapshot(report)))
    lines.extend(facade._section("실행 결과", facade._build_execution_quality(report)))
    lines.extend(facade._section("결과 평가", facade._build_reporter_evaluation(report)))
    lines.extend(facade._section("보완 사안", facade._build_weaknesses(report)))
    lines.extend(facade._section("근거 출처", facade._build_provenance(report)))
    lines.extend(facade._section("전체 타임라인", facade._build_timeline(report)))
    lines.extend(facade._section("최종 운영 판단", facade._build_final_conclusion(report)))

    return "\n".join(facade._strip_trailing_blanks(lines)).strip() + "\n"


def render_trade_summary_markdown_with_evaluation_clean_r3_impl(report, summary_report, *, facade):
    """Render ai_trade_summary.md with deterministic diagnostics before the LLM draft."""

    base = facade.render_trade_summary_markdown_clean(report).rstrip()
    deterministic_section = facade._build_summary_deterministic_diagnostics_section(summary_report, report=report)
    llm_section = facade._build_summary_llm_evaluation_section(summary_report, report=report)
    section = list(deterministic_section)
    if deterministic_section and llm_section:
        section.append("")
    section.extend(llm_section)
    section = facade._strip_trailing_blanks(section)
    if not section:
        return base + "\n"
    marker = "\n---\n\n## 🧭 거래 개요"
    block = "\n".join(section)
    if marker in base:
        return base.replace(marker, f"\n{block}\n{marker}", 1).strip() + "\n"
    return f"{base}\n\n{block}\n"


def _is_recovered_partial_exit_report_r3_impl(report, *, facade):
    shared = facade._as_dict(report.get("shared_facts"))
    final = facade._as_dict(report.get("final_operator_conclusion"))
    status = str(report.get("status") or shared.get("status") or "").strip().lower()
    action_raw = str(final.get("current_action") or report.get("action") or shared.get("action") or "").strip()
    action_is_sell = action_raw.upper() == "SELL" or facade._action_label(action_raw) == "매도"
    if status != "partial" or not action_is_sell:
        return False

    explicit_markers = (
        bool(report.get("evidence_recovery_used"))
        or str(report.get("trade_origin") or "").strip().lower() == "recovered_partial"
        or str(report.get("lifecycle_completeness") or "").strip().lower() == "partial"
    )
    entry = facade._as_dict(report.get("entry_decision"))
    selection = facade._as_dict(report.get("why_this_symbol_was_chosen"))
    entry_text = " ".join([str(entry.get("summary") or "")] + [str(item or "") for item in facade._listify(entry.get("bullets"))]).lower()
    entry_missing = (
        "entry evidence was not captured" in entry_text
        or "entry execution evidence is incomplete" in entry_text
        or "진입 실행 근거가 불완전" in entry_text
        or "진입 근거가 미확인" in entry_text
    )
    selected_rank = facade._num_opt(selection.get("selected_rank"))
    universe_size = facade._num_opt(selection.get("universe_size"))
    scanner_empty = selected_rank == 0 and universe_size == 0
    return bool(explicit_markers or entry_missing or scanner_empty)


def _authoritative_hold_duration_seconds_r3_impl(report, *, facade):
    """Resolve actual hold time from entry/exit execution timestamps first."""

    entry_ts = facade._first_report_path(
        report,
        [
            "fact_payload.trade.entry_execution_details.ts",
            "entry_execution_details.ts",
            "fact_payload.trade.entry_summary.ts",
            "entry_summary.ts",
        ],
    )
    exit_ts = facade._first_report_path(
        report,
        [
            "fact_payload.trade.exit_execution_details.ts",
            "fact_payload.trade.execution_details.ts",
            "exit_execution_details.ts",
            "execution_details.ts",
            "fact_payload.trade.exit_summary.ts",
            "exit_summary.ts",
        ],
    )
    entry_dt = facade._parse_report_datetime(entry_ts)
    exit_dt = facade._parse_report_datetime(exit_ts)
    if entry_dt is not None and exit_dt is not None and exit_dt >= entry_dt:
        return float((exit_dt - entry_dt).total_seconds())

    return facade._num_opt(
        facade._first_report_path(
            report,
            [
                "fact_payload.trade.exit_vs_strategy_intent.actual_hold_sec",
                "fact_payload.trade.canonical_agent_artifacts.monitor.exit_vs_strategy_intent.actual_hold_sec",
                "monitor_snapshot.exit_vs_strategy_intent.actual_hold_sec",
                "exit_vs_strategy_intent.actual_hold_sec",
                "shared_facts.exit_vs_strategy_intent.actual_hold_sec",
            ],
        )
    )


def _authoritative_final_operator_summary_r3_impl(report, *, action, fallback, facade):
    """Keep the closed-trade conclusion on broker truth, not monitor marks."""

    shared = facade._as_dict(report.get("shared_facts"))
    truth = facade._get_truth_surface(report)
    pnl = facade._as_dict(truth.get("pnl"))
    truth_status = facade._as_dict(truth.get("status"))
    status = str(truth_status.get("status") or report.get("status") or shared.get("status") or "").lower()
    action_label = str(action or "").strip()
    pnl_value = facade._num_opt(pnl.get("value"))
    pnl_pct, _ = facade._operator_pnl_pct_impl(pnl, shared)
    if status != "closed" or action_label != "매도" or (pnl_value is None and pnl_pct is None):
        return facade._correct_final_operator_summary(fallback, action=action)

    symbol = facade._clip(report.get("symbol") or shared.get("symbol"), 32) or "해당 종목"
    duration = facade._authoritative_holding_duration_label(report)
    result_basis = pnl_value if pnl_value is not None else facade._num_opt(pnl_pct)
    result_label = "이익" if (result_basis or 0.0) > 0 else "손실" if (result_basis or 0.0) < 0 else "보합"
    details: List[str] = []
    if pnl_pct is not None:
        details.append(facade._fmt_pct(pnl_pct))
    if pnl_value is not None:
        details.append(f"{pnl_value:,.0f}원")
    detail_text = f" ({', '.join(details)})" if details else ""
    duration_text = f"{duration} 보유 후 " if duration else ""
    return (
        f"현재 판단은 청산 완료입니다. {symbol} 거래는 브로커 체결 기준 "
        f"{duration_text}{result_label}{detail_text}로 청산 완료됐습니다. "
        "모니터의 청산 전 시세 관측값은 실제 체결 손익과 구분합니다."
    )
