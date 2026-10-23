"""Operator brief markdown status/section rendering fragments (exact text, spacing and newlines).

Second Pass (P1.5) intra-function extraction from `apps/operator_ui/data_access_core.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def brief_render_lines(brief, _metric_text, *, facade):
    if True:
        failure = brief.get("failure") if isinstance(brief.get("failure"), dict) else {}
        lines = [
            "# 운영자 브리프",
            "",
            "## 1. 최종 판단 요약",
            "",
            "- 저장된 요약 결과가 완전하지 않아 현재 판단을 보수적으로 다시 정리했습니다.",
            "",
            "## 2. 종목 선정 이유",
            "",
            "- 저장 범위가 제한되어 종목 선정 배경은 간단히만 확인됩니다.",
            "",
            "## 3. 진입 근거",
            "",
            "- 저장된 데이터가 부족해 진입 시점의 분봉 근거는 보수적으로 해석합니다.",
            "",
            "## 4. 현재 상태",
            "",
            f"- 현재 브리프 상태는 {_metric_text(brief.get('status'))}이며 추가 확인이 필요합니다.",
            "",
            "## 5. 청산 계획",
            "",
            "- 청산 계획은 저장된 데이터 범위 안에서 다시 확인해야 합니다.",
            "",
            "## 6. 리스크 요인",
            "",
            f"- 생성 과정에서 {_metric_text(failure.get('reason') or brief.get('reason'))} 이슈가 있어 일부 설명이 축약되었습니다.",
            "",
            "## 7. 다음 체크포인트",
            "",
            "- 저장 구조와 LLM 응답 상태를 다시 확인합니다.",
            "",
        ]
    return (lines,)


def brief_render_current_snapshot_entry(brief, *, facade):
    sections = brief.get("sections") if isinstance(brief.get("sections"), dict) else {}
    executive = sections.get("executive_decision") if isinstance(sections.get("executive_decision"), dict) else {}
    selection = sections.get("why_symbol_chosen") if isinstance(sections.get("why_symbol_chosen"), dict) else {}
    market = sections.get("market_context") if isinstance(sections.get("market_context"), dict) else {}
    monitor = sections.get("position_monitor_reasoning") if isinstance(sections.get("position_monitor_reasoning"), dict) else {}
    entry = sections.get("entry_timing") if isinstance(sections.get("entry_timing"), dict) else {}
    exit_plan = sections.get("exit_plan") if isinstance(exit_plan := sections.get("exit_plan"), dict) else {}
    operator_conclusion = sections.get("operator_conclusion") if isinstance(sections.get("operator_conclusion"), dict) else {}
    risk_alerts = sections.get("risk_alerts") if isinstance(sections.get("risk_alerts"), dict) else {}
    current_snapshot = sections.get("current_snapshot") if isinstance(sections.get("current_snapshot"), dict) else {}
    strategist_evidence = sections.get("strategist_evidence") if isinstance(sections.get("strategist_evidence"), dict) else {}
    scanner_focus = sections.get("scanner_focus") if isinstance(sections.get("scanner_focus"), dict) else {}
    monitor_guard_snapshot = sections.get("monitor_guard_snapshot") if isinstance(sections.get("monitor_guard_snapshot"), dict) else {}
    next_step_section = sections.get("next_step") if isinstance(sections.get("next_step"), dict) else {}

    selected_symbol = str(executive.get("symbol") or "-")
    final_action = str(executive.get("final_action") or operator_conclusion.get("current_action") or "").strip().upper()
    posture_action = str(monitor.get("posture") or final_action).strip().upper()
    headline = str(brief.get("headline") or "").strip()
    return (current_snapshot, entry, executive, exit_plan, final_action, headline, market, monitor, monitor_guard_snapshot, next_step_section, operator_conclusion, posture_action, risk_alerts, scanner_focus, selected_symbol, selection, strategist_evidence)


def brief_render_lines_market_headlines(_summary_text, current_snapshot, brief, strategist_evidence, scanner_focus, monitor_guard_snapshot, next_step_section, operator_conclusion, executive, _compact_items, *, facade):
    if True:
        snapshot_summary = _summary_text(
            current_snapshot,
            brief.get("executive_summary"),
            brief.get("headline"),
        ) or "현재 run 기준 핵심 상태를 요약했습니다."
        strategist_summary = _summary_text(
            strategist_evidence,
            brief.get("strategist_summary"),
        ) or "전략가 근거는 제한된 범위에서만 확인되었습니다."
        scanner_summary = _summary_text(
            scanner_focus,
            brief.get("scanner_summary"),
        ) or "스캐너 선정 근거는 제한된 범위에서만 확인되었습니다."
        monitor_summary = _summary_text(
            monitor_guard_snapshot,
            brief.get("monitor_summary"),
        ) or "모니터와 가드 상태를 중심으로 현재 상황을 정리했습니다."
        next_step_summary = _summary_text(
            next_step_section,
            operator_conclusion.get("watch_next"),
            brief.get("operator_takeaways"),
        ) or "다음 체크포인트를 계속 확인합니다."

        snapshot_focus = facade._sanitize_operator_brief_text(
            current_snapshot.get("current_focus")
            or current_snapshot.get("selected_symbol")
            or executive.get("symbol")
        )
        snapshot_action = facade._sanitize_operator_brief_text(
            current_snapshot.get("final_action")
            or executive.get("final_action")
            or operator_conclusion.get("current_action")
        )
        guard_status = facade._sanitize_operator_brief_text(
            monitor_guard_snapshot.get("guard_status") or current_snapshot.get("guard_status")
        )
        execution_status = facade._sanitize_operator_brief_text(
            monitor_guard_snapshot.get("execution_status") or current_snapshot.get("execution_status")
        )

        candidate_hints = _compact_items(strategist_evidence.get("candidate_hints"), limit=8, max_len=40)
        market_headlines = _compact_items(strategist_evidence.get("market_headlines"), limit=3, max_len=180)
        symbol_headlines = _compact_items(strategist_evidence.get("symbol_headlines"), limit=3, max_len=180)

        top_candidates = [row for row in list(scanner_focus.get("top_candidates") or []) if isinstance(row, dict)][:5]
        top_candidates_summary = ", ".join(
            f"#{idx} {(facade._sanitize_operator_brief_text(row.get('symbol')) or '-')}"
            for idx, row in enumerate(top_candidates, start=1)
            if facade._sanitize_operator_brief_text(row.get("symbol"))
        )
        selection_reason = facade._sanitize_operator_brief_text(scanner_focus.get("selection_reason"))
        score_drivers_map = scanner_focus.get("score_drivers") if isinstance(scanner_focus.get("score_drivers"), dict) else {}
        score_driver_items = [
            f"{facade._sanitize_operator_brief_text(key)}={facade._format_float(value, 3)}"
            for key, value in list(score_drivers_map.items())[:4]
            if facade._sanitize_operator_brief_text(key)
        ]

        stop_policy_summary = _compact_items(monitor_guard_snapshot.get("stop_policy_summary"), limit=5, max_len=140)
        monitor_reason = facade._sanitize_operator_brief_text(
            monitor_guard_snapshot.get("monitor_reason") or monitor_guard_snapshot.get("entry_reason")
        )
        next_watch = _compact_items(next_step_section.get("watch_next"), limit=4, max_len=180)
        takeaways = _compact_items(
            next_step_section.get("operator_takeaways") or brief.get("operator_takeaways"),
            limit=4,
            max_len=180,
        )

        lines = [
            "# 운영자 브리프",
            "",
            "## 1. 현재 스냅샷",
            "",
            f"- {snapshot_summary}",
        ]
        if snapshot_focus:
            lines.append(f"- 현재 포커스 종목: {snapshot_focus}")
        if snapshot_action:
            lines.append(f"- 현재 판단: {snapshot_action}")
        if guard_status:
            lines.append(f"- 가드 상태: {guard_status}")
        if execution_status:
            lines.append(f"- 실행 상태: {execution_status}")

        lines.extend([
            "",
            "## 2. 전략가 근거",
            "",
            f"- {strategist_summary}",
        ])
        if candidate_hints:
            lines.append(f"- 전략가 후보 힌트: {', '.join(candidate_hints)}")
    return (lines, market_headlines, monitor_reason, monitor_summary, next_step_summary, next_watch, scanner_summary, score_driver_items, selection_reason, stop_policy_summary, symbol_headlines, takeaways, top_candidates_summary)


def brief_render_effect_free_block_3748(lines, scanner_summary, scanner_focus, top_candidates_summary, selection_reason, score_driver_items, monitor_summary, monitor_reason, *, facade):
    if True:
        lines.extend([
            "",
            "## 3. 스캐너 포커스",
            "",
            f"- {scanner_summary}",
        ])
        if scanner_focus.get("selected_symbol"):
            lines.append(
                f"- 최종 선택: {scanner_focus.get('selected_symbol')} (rank {scanner_focus.get('selected_rank') or '-'})"
            )
        if top_candidates_summary:
            lines.append(f"- 상위 후보: {top_candidates_summary}")
        if selection_reason:
            lines.append(f"- 선정 이유: {selection_reason}")
        if score_driver_items:
            lines.append(f"- 주요 점수 요인: {', '.join(score_driver_items)}")

        lines.extend([
            "",
            "## 4. 모니터 / 가드",
            "",
            f"- {monitor_summary}",
        ])
        if monitor_reason:
            lines.append(f"- 핵심 모니터 이유: {monitor_reason}")
    return None
