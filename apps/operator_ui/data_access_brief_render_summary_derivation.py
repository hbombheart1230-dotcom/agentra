"""Operator brief renderer: complete early fallback Markdown when the narrative quality guard trips.

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `apps/operator_ui/data_access_core.py::_render_operator_brief_markdown` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def operator_brief_early_fallback(_compact_items, _summary_text, brief, current_snapshot, executive, monitor_guard_snapshot, next_step_section, operator_conclusion, scanner_focus, strategist_evidence, *, facade):
    if any(
        isinstance(section, dict) and section
        for section in (
            current_snapshot,
            strategist_evidence,
            scanner_focus,
            monitor_guard_snapshot,
            next_step_section,
        )
    ):
        lines, market_headlines, monitor_reason, monitor_summary, next_step_summary, next_watch, scanner_summary, score_driver_items, selection_reason, stop_policy_summary, symbol_headlines, takeaways, top_candidates_summary = facade.brief_render_lines_market_headlines(_summary_text=_summary_text, current_snapshot=current_snapshot, brief=brief, strategist_evidence=strategist_evidence, scanner_focus=scanner_focus, monitor_guard_snapshot=monitor_guard_snapshot, next_step_section=next_step_section, operator_conclusion=operator_conclusion, executive=executive, _compact_items=_compact_items, facade=facade)
        if market_headlines:
            lines.append("- 시장 헤드라인:")
            for item in market_headlines:
                lines.append(f"  - {item}")
        if symbol_headlines:
            lines.append("- 선택 종목 관련 헤드라인:")
            for item in symbol_headlines:
                lines.append(f"  - {item}")

        facade.brief_render_effect_free_block_3748(lines=lines, scanner_summary=scanner_summary, scanner_focus=scanner_focus, top_candidates_summary=top_candidates_summary, selection_reason=selection_reason, score_driver_items=score_driver_items, monitor_summary=monitor_summary, monitor_reason=monitor_reason, facade=facade)
        if stop_policy_summary:
            lines.append("- 활성 스톱 정책:")
            for item in stop_policy_summary:
                lines.append(f"  - {item}")

        lines.extend([
            "",
            "## 5. 다음 예상 단계",
            "",
            f"- {next_step_summary}",
        ])
        for item in next_watch:
            lines.append(f"- {item}")

        lines.extend([
            "",
            "## 6. 운영자 포인트",
            "",
        ])
        if takeaways:
            for item in takeaways:
                lines.append(f"- {item}")
        else:
            lines.append("- 현재 snapshot 기준 핵심 판단과 다음 체크포인트를 우선 확인합니다.")

        if lines[-1] != "":
            lines.append("")
        return "\n".join(lines)
    return None

def derive_operator_summary_fallbacks(_action_label, _axis_is_explicit, _axis_label, _entry_reason_text, _metric_text, _narrative_text, display_symbol, entry, entry_summary, executive_summary, exit_plan, exit_plan_summary, final_action, holding_summary, monitor, posture_action, risk_alerts, risk_summary, status, *, facade):
    if not entry_summary:
        entry_reason_text = _narrative_text(str(entry.get("reason_text") or "").strip())
        if facade._count_hangul_chars(entry_reason_text) > 0 and status != "fallback":
            entry_summary = entry_reason_text
        else:
            entry_summary = _entry_reason_text(
                str(entry.get("reason_code") or ""),
                str(entry.get("pattern") or ""),
                entry.get("metrics") if isinstance(entry.get("metrics"), dict) else {},
                posture_action,
            )

    if not executive_summary:
        if posture_action == "SELL":
            executive_summary = f"{display_symbol} \uac70\ub798\ub294 \uccad\uc0b0\uae4c\uc9c0 \ub9c8\ubb34\ub9ac\ub418\uc5c8\uace0, \ud655\uc778\ub41c \uc190\uc775\uacfc \ud558\ub77d\ud3ed \uae30\uc900\uc73c\ub85c \ub9e4\ub3c4 \ud310\ub2e8\uc774 \uc2e4\ud589\ub418\uc5c8\uc2b5\ub2c8\ub2e4."
        elif posture_action == "WAIT":
            executive_summary = f"{display_symbol}\uc5d0 \ub300\ud574\uc11c\ub294 \uc2e0\uaddc \uc9c4\uc785\uc744 \ubcf4\ub958\ud558\uace0 \ucd94\uac00 \ud655\uc778\uc744 \uc774\uc5b4\uac00\ub294 \ud310\ub2e8\uc785\ub2c8\ub2e4."
        else:
            executive_summary = f"{display_symbol}\uc758 \ud604\uc7ac \ucd5c\uc885 \ud310\ub2e8\uc740 {_action_label(posture_action)}\uc785\ub2c8\ub2e4."

    if not holding_summary:
        if posture_action == "SELL":
            holding_summary = (
                f"{display_symbol} \uac70\ub798\ub294 \uc774\ubbf8 \ub9e4\ub3c4\ub85c \uc885\ub8cc\ub418\uc5c8\uc2b5\ub2c8\ub2e4. \ud3c9\uade0 \ub9e4\uc218\uac00\ub294 {_metric_text(monitor.get('average_price'))}\uc600\uace0, "
                f"\uccad\uc0b0 \ud310\ub2e8 \ub2f9\uc2dc \uac00\uaca9\uc740 {_metric_text(monitor.get('current_price'))}\uc600\uc2b5\ub2c8\ub2e4. "
                f"\uace0\uc810 \ub300\ube44 \ud558\ub77d\ud3ed\uc740 {_metric_text(monitor.get('peak_drawdown'))} \uc218\uc900\uc73c\ub85c \ud655\uc778\ub429\ub2c8\ub2e4."
            )
        elif posture_action == "WAIT":
            holding_summary = (
                f"{display_symbol}\uc5d0 \ub300\ud574\uc11c\ub294 \uc544\uc9c1 \uc2e0\uaddc \uc9c4\uc785\uc744 \uc2e4\ud589\ud558\uc9c0 \uc54a\uc558\uc2b5\ub2c8\ub2e4. "
                f"\ud604\uc7ac \ubb38\uc11c\ub294 \ubcf4\uc720 \uad00\ub9ac \uae30\ub85d\ubcf4\ub2e4 \uc9c4\uc785 \ubcf4\ub958 \uc0ac\uc720\uc640 \ub2e4\uc74c \ud655\uc778 \ud56d\ubaa9\uc744 \uc911\uc2ec\uc73c\ub85c \uc815\ub9ac\ud588\uc2b5\ub2c8\ub2e4."
            )
        else:
            active_axis = _axis_label(monitor.get("active_exit_axis") or "-")
            active_axis_text = (
                f"현재 관리는 {active_axis} 기준으로 이어가고 있습니다."
                if _axis_is_explicit(active_axis)
                else "현재 관리는 저장된 손절·청산 기준을 중심으로 이어가고 있습니다."
            )
            holding_summary = (
                f"{display_symbol}\uc740 \ud604\uc7ac {_action_label(monitor.get('posture') or final_action)} \uc0c1\ud0dc\uc785\ub2c8\ub2e4. "
                f"\ud604\uc7ac\uac00\ub294 {_metric_text(monitor.get('current_price'))}, \ud3c9\uade0 \ub2e8\uac00\ub294 {_metric_text(monitor.get('average_price'))}\uc774\uba70, "
                f"{active_axis_text}"
            )

    if not exit_plan_summary:
        effective_stop = _metric_text(exit_plan.get("effective_stop") or monitor.get("effective_stop"))
        effective_stop_reason = _axis_label(exit_plan.get("effective_stop_reason") or monitor.get("effective_stop_reason"))
        take_profit = _metric_text(exit_plan.get("take_profit") or monitor.get("take_profit"))
        watch_axes = [_axis_label(x) for x in list(exit_plan.get("watch_axes") or monitor.get("watch_axes") or [])[:2] if str(x or "").strip()]
        axes_text = ", ".join(watch_axes) if watch_axes else "\uc8fc\uc694 \uac10\uc2dc \uc870\uac74 \ubcc0\ud654"
        if posture_action == "SELL":
            axis_prefix = (
                f"{effective_stop_reason} 기준과"
                if _axis_is_explicit(effective_stop_reason)
                else "저장된 손절 기준과"
            )
            exit_plan_summary = (
                f"\uc774\ubc88 \uac70\ub798\ub294 {axis_prefix} \uace0\uc810 \ub300\ube44 \ud558\ub77d\ud3ed \uc870\uac74\uc744 \uc6b0\uc120 \ud655\uc778\ud55c \ub4a4 \uccad\uc0b0\uc744 \uc2e4\ud589\ud588\uc2b5\ub2c8\ub2e4. "
                f"\ucc38\uace0 \uc190\uc808 \uae30\uc900\uc740 {effective_stop} \uc218\uc900\uc774\uc5c8\uace0, \ubaa9\ud45c \uc218\uc775 \uc2e4\ud604 \uae30\uc900\uc740 {take_profit} \uc218\uc900\uc774\uc5c8\uc2b5\ub2c8\ub2e4."
            )
        elif posture_action == "WAIT":
            exit_plan_summary = (
                f"\uc2e0\uaddc \uc9c4\uc785 \uc804\uae4c\uc9c0\ub294 {axes_text}\ub97c \uba3c\uc800 \uc810\uac80\ud558\uace0, \ubd84\ubd09 \uae30\uc900\uc774 \ub2e4\uc2dc \ub9de\uc544\ub5a8\uc5b4\uc9c8 \ub54c\uae4c\uc9c0 \ubcf4\uc218\uc801\uc73c\ub85c \ub300\uae30\ud569\ub2c8\ub2e4."
            )
        else:
            axis_prefix = (
                f"\uc6b0\uc120 {effective_stop_reason}\uc744 \uae30\uc900\uc73c\ub85c \ub300\uc751\ud558\uace0"
                if _axis_is_explicit(effective_stop_reason)
                else "\uc6b0\uc120 \uc800\uc7a5\ub41c \uc190\uc808 \uae30\uc900\uc744 \uc911\uc2ec\uc73c\ub85c \ub300\uc751\ud558\uace0"
            )
            exit_plan_summary = (
                f"{axis_prefix} \uae30\uc900\uac12\uc740 {effective_stop} \uc218\uc900\uc73c\ub85c \ubcf4\uace0 \uc788\uc2b5\ub2c8\ub2e4. "
                f"\ubaa9\ud45c \uc218\uc775 \uc2e4\ud604 \uae30\uc900\uc740 {take_profit} \uc218\uc900\uc774\uba70, {axes_text}\uac00 \ud754\ub4e4\ub9ac\uba74 \ub2e4\uc2dc \ud310\ub2e8\ud569\ub2c8\ub2e4."
            )

    if not risk_summary:
        weak_factors = [_narrative_text(x) for x in list(risk_alerts.get("weak_factors") or []) if _narrative_text(x)]
        if weak_factors and status != "fallback":
            risk_summary = " ".join(weak_factors[:3])
        elif bool(risk_alerts.get("defensive_mode")):
            risk_summary = "\uac70\uc2dc \uc2a4\ud2b8\ub808\uc2a4 \uc2e0\ud638\uac00 \ub192\uc544 \uc788\uc5b4 \ubc29\uc5b4\uc801\uc73c\ub85c \ub300\uc751\ud560 \ud544\uc694\uac00 \uc788\uc2b5\ub2c8\ub2e4."
        else:
            risk_summary = "\ud604\uc7ac \uc815\ubcf4 \ubc94\uc704\uc5d0\uc11c\ub294 \ucd94\uac00 \ub9ac\uc2a4\ud06c\uac00 \uc81c\ud55c\uc801\uc774\uc9c0\ub9cc \ubd84\ubd09 \uad6c\uc870 \ubcc0\ud654\uc640 \uac70\ub798\ub7c9 \ub454\ud654 \uc5ec\ubd80\ub97c \uacc4\uc18d \ud655\uc778\ud574\uc57c \ud569\ub2c8\ub2e4."
    return (entry_summary, executive_summary, exit_plan_summary, holding_summary, risk_summary)
