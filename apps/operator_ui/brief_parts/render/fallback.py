"""Operator brief markdown fallback narrative/metrics/output line fragments.

Second Pass (P1.5) intra-function extraction from `apps/operator_ui/data_access_core.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def brief_fallback_comparison_reasons_display_symbol(selected_symbol, _usable_narrative_text, _narrative_text, brief, status, headline, posture_action, selection, *, facade):
    display_symbol = selected_symbol if selected_symbol and selected_symbol != "-" else "\ud574\ub2f9 \uc885\ubaa9"
    executive_summary = _usable_narrative_text(brief.get("executive_summary")) or _narrative_text("" if status == "fallback" else (str(brief.get("executive_summary") or "").strip() or headline))
    scanner_reason = _usable_narrative_text(brief.get("scanner_reason")) or _usable_narrative_text(brief.get("scanner_summary")) or _narrative_text("" if status == "fallback" else str(brief.get("scanner_reason") or brief.get("scanner_summary") or "").strip())
    holding_summary = _usable_narrative_text(brief.get("holding_summary"))
    if not holding_summary and posture_action not in {"SELL", "WAIT"}:
        holding_summary = _usable_narrative_text(brief.get("monitor_summary"))
    if not holding_summary:
        holding_summary = _narrative_text("" if status == "fallback" else str(brief.get("holding_summary") or brief.get("monitor_summary") or "").strip())
    exit_plan_summary = _usable_narrative_text(brief.get("exit_plan_summary")) or _narrative_text("" if status == "fallback" else str(brief.get("exit_plan_summary") or "").strip())
    risk_summary = _usable_narrative_text(brief.get("risk_summary")) or _narrative_text("" if status == "fallback" else str(brief.get("risk_summary") or "").strip())
    if risk_summary.startswith("[") and risk_summary.endswith("]"):
        risk_summary = ""
    next_checkpoints = [_usable_narrative_text(x) for x in list(brief.get("next_checkpoints") or []) if _usable_narrative_text(x)]
    takeaways = [_narrative_text(x) for x in list(brief.get("operator_takeaways") or []) if _narrative_text(x)]

    universe_size_raw = facade._safe_int(selection.get("universe_size"), 0)
    selected_rank_raw = facade._safe_int(selection.get("selected_rank"), 0) or 1
    selection_reasons = [str(x or "").strip() for x in list(selection.get("selection_reasons") or []) if str(x or "").strip()]
    comparison_reasons = [str(x or "").strip() for x in list(selection.get("comparison_reasons") or []) if str(x or "").strip()]
    signal_source = " ".join([scanner_reason] + selection_reasons + comparison_reasons).lower()
    signal_phrases: facade.List[str] = []
    if any(token in signal_source for token in ["\uac70\ub798\ub7c9", "volume", "trading value", "\uac70\ub798\ub300\uae08"]):
        signal_phrases.append("\uac70\ub798\ub7c9\uacfc \uac70\ub798\ub300\uae08 \ud750\ub984\uc774 \ud568\uaed8 \ud655\uc778\ub418\uc5c8\uc2b5\ub2c8\ub2e4.")
    if any(token in signal_source for token in ["\ub3cc\ud30c", "breakout"]):
        signal_phrases.append("\ub2e8\uae30 \ub3cc\ud30c \uc2dc\ub3c4 \ud750\ub984\uc774 \ud3ec\ucc29\ub418\uc5c8\uc2b5\ub2c8\ub2e4.")
    if any(token in signal_source for token in ["\ubcc0\ub3d9\uc131", "volatility"]):
        signal_phrases.append("\ub2e8\uae30 \ubcc0\ub3d9\uc131 \ud655\ub300\uac00 \ud568\uaed8 \uad00\ucc30\ub418\uc5c8\uc2b5\ub2c8\ub2e4.")
    if any(token in signal_source for token in ["\ub20c\ub9bc", "pullback", "\ubc18\ub4f1", "rebound"]):
        signal_phrases.append("\ub20c\ub9bc \uc774\ud6c4 \ubc18\ub4f1 \uac00\ub2a5\uc131\uc744 \ud568\uaed8 \uc810\uac80\ud588\uc2b5\ub2c8\ub2e4.")
    if not scanner_reason or not any(token in scanner_reason for token in ["\ud6c4\ubcf4", "\uc120\uc815", "\uc21c\uc704", "\uac10\uc2dc"]):
        if universe_size_raw > 0:
            scanner_reason = f"\ucd1d {universe_size_raw}\uac1c \ud6c4\ubcf4 \uc911 {selected_rank_raw}\uc21c\uc704 \uac10\uc2dc \ub300\uc0c1\uc73c\ub85c \uc120\uc815\ub418\uc5c8\uc2b5\ub2c8\ub2e4."
        else:
            scanner_reason = "\uc774\ubc88 \uc2e4\ud589\uc5d0\uc11c\ub294 \ud6c4\ubcf4 \ube44\uad50 \ub370\uc774\ud130\uac00 \ucda9\ubd84\ud788 \uc800\uc7a5\ub418\uc9c0 \uc54a\uc544 \uc0c1\ub300 \uc21c\uc704\ub97c \uc790\uc138\ud788 \ubcf5\uc6d0\ud558\uae30 \uc5b4\ub835\uc2b5\ub2c8\ub2e4. \ub2e4\ub9cc \uc774\ud6c4 \ubcf4\uc720\u00b7\uccad\uc0b0 \ud750\ub984\uc740 \ud655\uc778\ub418\uc5b4 \ud574\ub2f9 \uc885\ubaa9 \uc911\uc2ec\uc73c\ub85c \uc815\ub9ac\ud588\uc2b5\ub2c8\ub2e4."
    if signal_phrases and all(phrase not in scanner_reason for phrase in signal_phrases[:2]):
        scanner_reason = " ".join([scanner_reason] + signal_phrases[:2])

    entry_summary = _usable_narrative_text(brief.get("entry_summary"))
    return (comparison_reasons, display_symbol, entry_summary, executive_summary, exit_plan_summary, holding_summary, next_checkpoints, risk_summary, scanner_reason, selection_reasons, takeaways)


def brief_fallback_lines(next_checkpoints, _narrative_text, operator_conclusion, takeaways, _default_next_checkpoints, entry, monitor, exit_plan, posture_action, executive_summary, scanner_reason, _append_list, selection_reasons, comparison_reasons, entry_summary, _vwap_interpretation, holding_summary, _action_label, _metric_text, final_action, exit_plan_summary, _axis_is_explicit, _axis_label, risk_summary, risk_alerts, market, *, facade):
    if not next_checkpoints:
        next_checkpoints = [_narrative_text(x) for x in list(operator_conclusion.get("watch_next") or []) if _narrative_text(x)]
    if not next_checkpoints and takeaways:
        next_checkpoints = takeaways[:3]
    if not next_checkpoints:
        next_checkpoints = _default_next_checkpoints(entry, monitor, exit_plan, posture_action)
    if not next_checkpoints:
        if posture_action == "SELL":
            next_checkpoints = [
                "\ub2e4\uc74c \uac70\ub798\uc5d0\uc11c\ub294 \ubd84\ubd09 \uc9c4\uc785 \uadfc\uac70\uc640 \ud6c4\ubcf4 \ube44\uad50 \ub370\uc774\ud130\uac00 \ucda9\ubd84\ud788 \ub0a8\ub294\uc9c0 \uba3c\uc800 \ud655\uc778\ud569\ub2c8\ub2e4."
            ]
        elif posture_action == "WAIT":
            next_checkpoints = [
                "\ubd84\ubd09 \uae30\uc900\uc73c\ub85c \uc7ac\ub3cc\ud30c \uc5ec\ubd80\uc640 \uac70\ub798\ub7c9 \uc99d\uac00 \uc5ec\ubd80\ub97c \ub2e4\uc74c \uccb4\ud06c\ud3ec\uc778\ud2b8\ub85c \uc124\uc815\ud569\ub2c8\ub2e4."
            ]
        else:
            next_checkpoints = [
                "\ud604\uc7ac \ubcf4\uc720 \uc0c1\ud0dc\uc5d0\uc11c\ub294 \uace0\uc810 \ub300\ube44 \ud558\ub77d\ud3ed\uacfc \uac70\ub798\ub7c9 \ub454\ud654\ub97c \uc8fc\uc694 \ud655\uc778 \uc9c0\ud45c\ub85c \ubd05\ub2c8\ub2e4."
            ]

    lines = [
        "# 운영자 브리프",
        "",
        "## 1. 최종 판단 요약",
        "",
        f"- {executive_summary}",
        "",
        "## 2. 종목 선정 이유",
        "",
        f"- {scanner_reason}",
    ]
    _append_list(lines, selection_reasons, limit=3)
    _append_list(lines, comparison_reasons, limit=2)

    lines.extend([
        "",
        "## 3. 진입 근거",
        "",
        f"- {entry_summary}",
    ])
    entry_metrics = entry.get("metrics") if isinstance(entry.get("metrics"), dict) else {}
    if entry_metrics.get("recent_high") not in (None, ""):
        lines.append(f"- 최근 고점 기준값은 {facade._format_float(entry_metrics.get('recent_high'), 2)}였습니다.")
    if entry_metrics.get("vwap") not in (None, ""):
        lines.append(f"- 당시 VWAP 기준값은 {facade._format_float(entry_metrics.get('vwap'), 2)}였습니다.")
    if entry_metrics.get("vwap_distance") not in (None, ""):
        lines.append(f"- VWAP 이격은 {_vwap_interpretation(entry_metrics.get('vwap_distance'))}")
    if entry_metrics.get("volume_ratio") not in (None, ""):
        lines.append(f"- 거래량은 평시 대비 {facade._format_float(entry_metrics.get('volume_ratio'), 2)}배 수준으로 확인됐습니다.")
    if entry_metrics.get("pullback_pct") not in (None, ""):
        lines.append(f"- 눌림 폭은 {facade._format_percent(entry_metrics.get('pullback_pct'), 2)} 수준이었습니다.")

    lines.extend([
        "",
        "## 4. 현재 상태",
        "",
        f"- {holding_summary}",
        f"- 현재 포지션 판단은 {_action_label(monitor.get('posture') or final_action)}입니다.",
        f"- 평균 단가는 {_metric_text(monitor.get('average_price'))}, 현재가는 {_metric_text(monitor.get('current_price'))}, 장중 고점은 {_metric_text(monitor.get('peak_price'))}입니다.",
        f"- 현재 손익은 {_metric_text(monitor.get('current_drawdown'))}이며, 고점 대비 하락폭은 {_metric_text(monitor.get('peak_drawdown'))}입니다.",
    ])
    hold_reasons = [str(x or "").strip() for x in list(monitor.get("hold_reasons") or []) if str(x or "").strip()]
    _append_list(lines, hold_reasons, limit=3)

    lines.extend([
        "",
        "## 5. 청산 계획",
        "",
        f"- {exit_plan_summary}",
        (
            f"- 현재 {_axis_label(exit_plan.get('effective_stop_reason') or monitor.get('effective_stop_reason'))}은 {_metric_text(exit_plan.get('effective_stop') or monitor.get('effective_stop'))} 수준으로 보고 있습니다."
            if _axis_is_explicit(_axis_label(exit_plan.get('effective_stop_reason') or monitor.get('effective_stop_reason')))
            else f"- 현재 저장된 손절 기준은 {_metric_text(exit_plan.get('effective_stop') or monitor.get('effective_stop'))} 수준으로 보고 있습니다."
        ),
        f"- 목표 수익 실현 기준은 {_metric_text(exit_plan.get('take_profit') or monitor.get('take_profit'))} 수준입니다.",
        f"- 주요 감시 조건은 {', '.join([_axis_label(x) for x in list(exit_plan.get('watch_axes') or monitor.get('watch_axes') or [])[:3] if str(x or '').strip()]) or '감시 조건 변화'}입니다.",
    ])
    exit_triggers = [str(x or "").strip() for x in list(exit_plan.get("exit_triggers") or monitor.get("exit_triggers") or []) if str(x or "").strip()]
    _append_list(lines, exit_triggers, limit=3)

    lines.extend([
        "",
        "## 6. 리스크 요인",
        "",
        f"- {risk_summary}",
    ])
    weak_factors = [str(x or "").strip() for x in list(risk_alerts.get("weak_factors") or []) if str(x or "").strip()]
    _append_list(lines, weak_factors, limit=3)
    if str(market.get("global_sentiment") or "-") != "-" or str(market.get("vix") or "-") != "-":
        lines.append(f"- 시장 맥락상 글로벌 감성은 {_metric_text(market.get('global_sentiment'))}, VIX는 {_metric_text(market.get('vix'))} 수준입니다.")

    lines.extend([
        "",
        "## 7. 다음 체크포인트",
        "",
    ])
    _append_list(lines, next_checkpoints or takeaways or ["다음 분봉과 거래량 흐름을 다시 확인합니다."], limit=4)
    if lines[-1] != "":
        lines.append("")
    return (lines,)
