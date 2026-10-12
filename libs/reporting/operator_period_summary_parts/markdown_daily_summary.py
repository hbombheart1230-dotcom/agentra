"""Operator daily summary Markdown rendering and its shadow-blocker/regime/pattern line renderers (pure text composition).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def render_operator_daily_summary_markdown_r3_impl(payload, *, facade):
    day = str(payload.get("day") or "")
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {}
    runtime = payload.get("runtime_activity") if isinstance(payload.get("runtime_activity"), dict) else {}
    patterns = payload.get("patterns") if isinstance(payload.get("patterns"), dict) else {}
    readout = payload.get("operator_readout") if isinstance(payload.get("operator_readout"), dict) else {}
    symbols = payload.get("symbol_summary") if isinstance(payload.get("symbol_summary"), list) else []
    residual = payload.get("residual_positions") if isinstance(payload.get("residual_positions"), dict) else {}
    residual_positions = residual.get("positions") if isinstance(residual.get("positions"), list) else []

    lines = [
        f"# Daily Summary ({day})",
        "",
        "---",
        "",
        "## 운영 요약",
        "",
        f"- 총 거래: {facade._safe_int(metrics.get('trade_count'))}건",
        f"- 완료 거래: {facade._safe_int(metrics.get('closed_trade_count'))}건",
        f"- 성과: **승률 {float(metrics.get('win_rate') or 0.0) * 100:.2f}% / 평균 {float(metrics.get('avg_return_pct') or 0.0):.2f}%**",
        (
            f"- 당일 신규 진입 성과: {facade._safe_int(metrics.get('same_day_new_closed_trade_count'))}건 / "
            f"승률 {float(metrics.get('same_day_new_win_rate') or 0.0) * 100:.2f}% / "
            f"평균 {float(metrics.get('same_day_new_avg_return_pct') or 0.0):.2f}%"
            if facade._safe_int(metrics.get("carryover_closed_trade_count")) > 0
            else ""
        ),
        (
            f"- 이월/정리 청산 제외: {facade._safe_int(metrics.get('carryover_closed_trade_count'))}건"
            if facade._safe_int(metrics.get("carryover_closed_trade_count")) > 0
            else ""
        ),
        (
            "- 런타임 이벤트: 미집계"
            if str(runtime.get("source") or "") == "not_available"
            else f"- 런타임 이벤트: {runtime.get('events') or 0}건"
        ),
        (
            "- 승인/차단: 미집계"
            if str(runtime.get("source") or "") == "not_available"
            else f"- 승인/차단: {runtime.get('approvals') or 0} / {runtime.get('blocks') or 0}"
        ),
        "",
        "### 잘된 점",
    ]
    if facade._safe_int(metrics.get("realized_exit_count")) > 0:
        lines.insert(
            -4,
            f"- 완료 외 실현 청산(회수/partial 포함): {facade._safe_int(metrics.get('realized_exit_count'))}건 / "
            f"승패 {facade._safe_int(metrics.get('realized_exit_win_count'))}/{facade._safe_int(metrics.get('realized_exit_loss_count'))} / "
            f"평균 {float(metrics.get('realized_exit_avg_return_pct') or 0.0):.2f}%",
        )
    for item in list(readout.get("good_points") or []):
        lines.append(f"- {item}")
    lines += ["", "### 문제점"]
    for idx, item in enumerate(list(readout.get("issues") or []), start=1):
        lines.append(f"{idx}. {item}")
    lines += [
        "",
        "### 원인 해석",
        f"**{readout.get('root_cause') or '-'}**",
        "",
        "### 권고 액션",
    ]
    for idx, item in enumerate(list(readout.get("recommended_actions") or []), start=1):
        lines.append(f"{idx}. {item}")

    lines += ["", "---", "", "## 장마감 잔여 보유 종목", ""]
    closeout_risk = (
        residual.get("closeout_operational_risk")
        if isinstance(residual.get("closeout_operational_risk"), dict)
        else {}
    )
    if str(closeout_risk.get("severity") or "").strip().lower() == "critical":
        symbols_text = ", ".join(
            str(item or "").strip()
            for item in list(closeout_risk.get("unresolved_symbols") or [])
            if str(item or "").strip()
        )
        lines += [
            "- CRITICAL: broker truth shows unclosed position(s) after closeout.",
            f"- required_action: `{closeout_risk.get('operator_action') or 'next_open_market_flatten_required'}`",
            f"- unresolved_symbols: `{symbols_text or '-'}`",
        ]
    account_snapshot = (
        residual.get("account_snapshot_reconciliation")
        if isinstance(residual.get("account_snapshot_reconciliation"), dict)
        else {}
    )
    if account_snapshot:
        snapshot_status = (
            "fresh_after_1520"
            if bool(account_snapshot.get("fresh_after_closeout_window"))
            else "stale_or_unavailable"
        )
        snapshot_time = str(account_snapshot.get("generated_at_kst") or "").strip()
        snapshot_position_count = facade._safe_int(account_snapshot.get("position_count"))
        lines.append(
            f"- account snapshot: {snapshot_status} / positions {snapshot_position_count}"
            + (f" / {snapshot_time}" if snapshot_time else "")
        )
    if not bool(residual.get("available")):
        lines.append("- 상태 스냅샷을 읽지 못해 잔여 보유 종목을 확인하지 못했습니다.")
    elif not residual_positions:
        lines.append("- 장마감 기준 잔여 보유 종목이 없습니다.")
        reconciled = (
            residual.get("reconciled_closed_positions")
            if isinstance(residual.get("reconciled_closed_positions"), list)
            else []
        )
        reconciled_symbols_text = ", ".join(
            str(row.get("symbol") or "").strip()
            for row in reconciled
            if isinstance(row, dict) and str(row.get("symbol") or "").strip()
        )
        if reconciled_symbols_text:
            lines.append(f"- 장중 청산 확인: {reconciled_symbols_text}은 당일 전량 매도 기록으로 잔여 보유에서 제외했습니다.")
    else:
        closeout = residual.get("closeout_state") if isinstance(residual.get("closeout_state"), dict) else {}
        reconciled = (
            residual.get("reconciled_closed_positions")
            if isinstance(residual.get("reconciled_closed_positions"), list)
            else []
        )
        closeout_mode = str(closeout.get("mode") or "").strip()
        closeout_reason = str(closeout.get("reason") or "").strip()
        if closeout_mode or closeout_reason:
            closeout_line = f"- closeout 상태: {closeout_mode or '-'} / {closeout_reason or '-'}"
            closeout_note = str(closeout.get("report_note") or "").strip()
            if closeout_note:
                closeout_line += f" ({closeout_note})"
            lines.append(closeout_line)
        if reconciled:
            reconciled_symbols_text = ", ".join(
                str(row.get("symbol") or "").strip()
                for row in reconciled
                if isinstance(row, dict) and str(row.get("symbol") or "").strip()
            )
            if reconciled_symbols_text:
                lines.append(f"- 장중 청산 확인: {reconciled_symbols_text}은 당일 전량 매도 기록으로 잔여 보유에서 제외했습니다.")
        for row in residual_positions:
            if not isinstance(row, dict):
                continue
            symbol = str(row.get("symbol") or "-")
            status = str(row.get("status") or "잔여 보유")
            qty = facade._safe_int(row.get("qty"))
            avg_price = row.get("avg_price")
            current_price = row.get("current_price")
            pnl_ratio = row.get("account_pnl_ratio")
            reason = str(row.get("overnight_reason") or "").strip()
            decision_label = str(row.get("overnight_decision_label") or "").strip()
            signals = [str(x) for x in list(row.get("overnight_positive_signals") or []) if str(x or "").strip()]
            blockers = [str(x) for x in list(row.get("overnight_blockers") or []) if str(x or "").strip()]
            price_text = f"평균 {avg_price:,.0f}" if isinstance(avg_price, (int, float)) and avg_price else "평균 -"
            current_text = f"현재 {current_price:,.0f}" if isinstance(current_price, (int, float)) and current_price else "현재 -"
            ratio_text = f" / 평가손익률 {float(pnl_ratio) * 100:.2f}%" if isinstance(pnl_ratio, (int, float)) else ""
            detail = f"- {symbol}: {status} / {qty}주 / {price_text} / {current_text}{ratio_text}"
            if decision_label:
                detail += f" / 오버나이트 판단: {decision_label}"
            if reason and not bool(row.get("overnight_decision_missing")):
                detail += f" / 사유 {reason}"
            if bool(row.get("weekend_carry")):
                detail += f" / 주말보유 {int(row.get('holding_gap_days') or 3)}일"
            lines.append(detail)
            if bool(row.get("weekend_carry")) and not bool(row.get("allow_weekend_carry")):
                lines.append("  - 주의: 금요일 carry 승인이라 주말 갭 리스크가 포함됩니다.")
            missing_detail = str(row.get("overnight_missing_detail") or "").strip()
            if bool(row.get("overnight_decision_missing")) and missing_detail:
                lines.append(f"  - 판단 기록 근거: {missing_detail}")
            if signals:
                lines.append(f"  - 승인 근거: {', '.join(signals[:5])}")
            if blockers:
                lines.append(f"  - 차단/주의 근거: {', '.join(blockers[:5])}")

    lines += ["", "---", "", "## 핵심 패턴", ""]
    for label, key in (
        ("주요 진입 사유", "top_entry_reasons"),
        ("주요 청산 사유", "top_exit_reasons"),
        ("진입 패턴", "top_entry_pattern_types"),
        ("청산 패턴", "top_exit_pattern_types"),
    ):
        rows = patterns.get(key) if isinstance(patterns.get(key), list) else []
        text = ", ".join(f"{row.get('name')} ({row.get('count')})" for row in rows[:3] if isinstance(row, dict))
        lines.append(f"- {label}: {text or '없음'}")
    lines.extend(facade._render_pattern_performance_lines(payload))
    lines.extend(facade._render_quant_shadow_candidate_lines(payload))
    lines.extend(facade._render_market_regime_rail_lines(payload))
    lines.extend(facade._render_q8_shadow_blocker_review_lines(payload))
    lines.extend(facade._render_strategist_llm_evaluation_lines(payload))
    controlled_validation = payload.get("controlled_validation")
    if isinstance(controlled_validation, dict):
        lines.extend(facade.render_controlled_validation_daily_lines(controlled_validation))

    lines += ["", "---", "", "## 종목별 요약", ""]
    if not symbols:
        lines.append("- 당일 종목별 요약이 없습니다.")
    for row in symbols[:8]:
        if not isinstance(row, dict):
            continue
        realized_suffix = ""
        if facade._safe_int(row.get("realized_exit_count")) > 0:
            realized_suffix = (
                f" / 회수청산 {row.get('realized_exit_count')}건 "
                f"{row.get('realized_exit_win_count')}/{row.get('realized_exit_loss_count')} "
                f"평균 {float(row.get('realized_exit_avg_return_pct') or 0.0):.2f}%"
            )
        lines.append(
            f"- {row.get('symbol')}: 거래 {row.get('trade_count')}건 / 완료 {row.get('closed_trade_count')}건 / "
            f"승패 {row.get('win_count')}/{row.get('loss_count')} / 평균 {float(row.get('avg_return_pct') or 0.0):.2f}%"
            f"{realized_suffix}"
        )

    lines += [
        "",
        "---",
        "",
        "## 상세 분석",
        "",
        "> 세부 거래 및 로그 기반 분석은 같은 일자의 daily_report.md와 개별 ai_trade_report.md를 참조합니다.",
        "",
    ]
    return "\n".join(lines)


def _render_q8_shadow_blocker_review_lines_r3_impl(payload, *, facade):
    review = payload.get("q8_shadow_blocker_review")
    if not isinstance(review, dict) or not review:
        return []
    groups = review.get("groups") if isinstance(review.get("groups"), list) else []
    lines = [
        "",
        "## Q8 Shadow Blocker Forward Review",
        "",
        f"- behavior_effect: `{review.get('behavior_effect') or 'evaluation_only'}`",
        f"- reviewed candidates: **{int(review.get('observed_review_candidate_count') or 0)}** observed / "
        f"**{int(review.get('candidate_count') or 0)}** total",
        f"- dedupe: raw **{int(review.get('raw_candidate_count') or review.get('candidate_count') or 0)}**, "
        f"deduped **{int(review.get('deduped_candidate_count') or review.get('candidate_count') or 0)}**, "
        f"duplicates **{int(review.get('duplicate_count') or 0)}**",
    ]
    for group in groups[:5]:
        if not isinstance(group, dict):
            continue
        lines.append(
            f"- `{group.get('reason') or '-'}`: "
            f"n={int(group.get('candidate_count') or 0)}, "
            f"obs={int(group.get('observed_count') or 0)}, "
            f"avg_latest={float(group.get('avg_latest_return_pct') or 0.0):.4f}%, "
            f"mfe={float(group.get('avg_max_favorable_pct') or 0.0):.4f}%, "
            f"mae={float(group.get('avg_max_adverse_pct') or 0.0):.4f}%, "
            f"decision=`{group.get('decision') or 'retain_under_observation'}`"
        )
    return lines


def _render_market_regime_rail_lines_r3_impl(payload, *, facade):
    rail = payload.get("market_regime_rail_review")
    if not isinstance(rail, dict) or not rail:
        return []
    inputs = rail.get("market_inputs") if isinstance(rail.get("market_inputs"), dict) else {}
    return [
        "",
        "## Market Regime Rail",
        "",
        f"- rail_id: `{rail.get('rail_id') or 'not_available'}` ({rail.get('rail_confidence') or 'none'})",
        f"- behavior_effect: `{rail.get('behavior_effect') or 'evaluation_only'}`",
        f"- rationale: {rail.get('rationale') or '-'}",
        (
            "- key inputs: "
            f"kospi {float(inputs.get('kospi_pct') or 0.0):.2f}%, "
            f"kosdaq {float(inputs.get('kosdaq_pct') or 0.0):.2f}%, "
            f"kospi200 {float(inputs.get('kospi200_pct') or 0.0):.2f}%, "
            f"krx_night {float(inputs.get('krx_night_futures_pct') or 0.0):.2f}% "
            f"({inputs.get('krx_night_futures_pressure') or '-'}), "
            f"breadth {float(inputs.get('breadth') or 0.0):.3f}, "
            f"nasdaq {float(inputs.get('nasdaq_pct') or 0.0):.2f}%, "
            f"usdkrw {float(inputs.get('usdkrw_pct') or 0.0):.2f}%"
        ),
        f"- q8_focus: `{', '.join(str(x) for x in list(rail.get('q8_review_focus') or [])) or '-'}`",
    ]


def _render_pattern_performance_lines_r3_impl(payload, *, facade):
    perf = payload.get("pattern_performance") if isinstance(payload.get("pattern_performance"), dict) else {}
    if not perf or int(perf.get("trade_count") or 0) <= 0:
        return []
    lines = [
        "",
        "---",
        "",
        "## Pattern Performance",
        "",
        facade._pattern_perf_line("Strategist tactical", facade._pattern_perf_rows(perf, "strategist", "by_tactical_strategy")),
        facade._pattern_perf_line("Strategist horizon", facade._pattern_perf_rows(perf, "strategist", "by_strategy_horizon")),
        facade._pattern_perf_line("Scanner rank", facade._pattern_perf_rows(perf, "scanner", "by_scanner_rank_bucket")),
        facade._pattern_perf_line("Monitor entry", facade._pattern_perf_rows(perf, "monitor_entry", "by_entry_pattern_type")),
        facade._pattern_perf_line("Monitor exit", facade._pattern_perf_rows(perf, "monitor_exit", "by_exit_pattern_type")),
        facade._pattern_perf_line("Quant tactic", facade._pattern_perf_rows(perf, "quant", "by_tactic_id")),
        facade._pattern_perf_line("Quant entry blockers", facade._pattern_perf_rows(perf, "quant", "by_entry_primary_blocker")),
        facade._pattern_perf_line("Quant exit quality", facade._pattern_perf_rows(perf, "quant", "by_exit_decision")),
        facade._pattern_perf_line(
            "Combined",
            facade._pattern_perf_rows(perf, "combined", "by_strategy_scanner_entry_exit"),
            limit=2,
        ),
    ]
    quant_eval = payload.get("quant_tactic_evaluation")
    if isinstance(quant_eval, dict):
        lines += [""] + facade.render_quant_tactic_evaluation_lines(quant_eval)
    return lines


def _pattern_perf_line_r3_impl(label, rows, *, limit, facade):
    parts: List[str] = []
    for row in rows[:limit]:
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        parts.append(
            f"{name} ({row.get('count')}, win {float(row.get('win_rate') or 0.0) * 100:.1f}%, "
            f"avg {float(row.get('avg_return_pct') or 0.0):.2f}%, 비용역전 {row.get('cost_drag_loss_count') or 0}건)"
        )
    return f"- {label}: {', '.join(parts) if parts else 'none'}"
