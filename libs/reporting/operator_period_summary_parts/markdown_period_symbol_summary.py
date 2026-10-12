"""Operator period and symbol summary Markdown rendering (pure text composition).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def render_operator_period_summary_markdown_r3_impl(payload, *, facade):
    period_type = str(payload.get("period_type") or "").strip().lower()
    period_label = "Weekly" if period_type == "weekly" else "Monthly"
    period_key = str(payload.get("period_key") or "")
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {}
    patterns = payload.get("patterns") if isinstance(payload.get("patterns"), dict) else {}
    readout = payload.get("operator_readout") if isinstance(payload.get("operator_readout"), dict) else {}
    date_range = payload.get("date_range") if isinstance(payload.get("date_range"), dict) else {}
    symbols = payload.get("symbol_summary") if isinstance(payload.get("symbol_summary"), list) else []

    lines = [
        f"# {period_label} Summary ({period_key})",
        "",
        "---",
        "",
        "## 운영 요약",
        "",
        f"- 기간: {date_range.get('start') or '-'} ~ {date_range.get('end') or '-'}",
        f"- 총 거래: {facade._safe_int(metrics.get('trade_count'))}건",
        f"- 완료 거래: {facade._safe_int(metrics.get('closed_trade_count'))}건",
        f"- 성과: **승률 {float(metrics.get('win_rate') or 0.0) * 100:.2f}% / 평균 {float(metrics.get('avg_return_pct') or 0.0):.2f}%**",
        "",
        "### 잘된 점",
    ]
    if facade._safe_int(metrics.get("realized_exit_count")) > 0:
        lines.insert(
            -2,
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

    lines += ["", "---", "", "## 반복 패턴", ""]
    for label, key in (
        ("주요 진입 사유", "top_entry_reasons"),
        ("주요 청산 사유", "top_exit_reasons"),
        ("진입 패턴", "top_entry_pattern_types"),
        ("청산 패턴", "top_exit_pattern_types"),
        ("플레이북", "top_playbooks"),
    ):
        rows = patterns.get(key) if isinstance(patterns.get(key), list) else []
        text = ", ".join(f"{row.get('name')} ({row.get('count')})" for row in rows[:3] if isinstance(row, dict))
        lines.append(f"- {label}: {text or '없음'}")
    lines.extend(facade._render_pattern_performance_lines(payload))
    lines.extend(facade._render_quant_shadow_candidate_lines(payload))
    lines.extend(facade._render_market_regime_rail_lines(payload))
    lines.extend(facade._render_q8_shadow_blocker_review_lines(payload))
    lines.extend(facade._render_strategist_llm_evaluation_lines(payload))

    lines += ["", "---", "", "## 주요 종목", ""]
    if not symbols:
        lines.append("- 기간 내 종목별 요약이 없습니다.")
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
        "> 기간별 운영 요약은 reports/operator_summary/symbols/*/trade_history.json 집계를 기준으로 생성됩니다.",
        "",
    ]
    return "\n".join(lines)


def render_operator_symbol_summary_markdown_r3_impl(payload, *, facade):
    symbol = str(payload.get("symbol") or "")
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {}
    patterns = payload.get("patterns") if isinstance(payload.get("patterns"), dict) else {}
    readout = payload.get("operator_readout") if isinstance(payload.get("operator_readout"), dict) else {}
    memory = payload.get("symbol_memory") if isinstance(payload.get("symbol_memory"), dict) else {}
    risk_notes = list(payload.get("risk_notes") or [])

    lines = [
        f"# Symbol Summary ({symbol})",
        "",
        "---",
        "",
        "## 운영 요약",
        "",
        f"- 총 거래: {facade._safe_int(metrics.get('trade_count'))}건",
        f"- 완료 거래: {facade._safe_int(metrics.get('closed_trade_count'))}건",
        f"- 성과: **승률 {float(metrics.get('win_rate') or 0.0) * 100:.2f}% / 평균 {float(metrics.get('avg_return_pct') or 0.0):.2f}%**",
        "",
        "### 잘된 점",
    ]
    if facade._safe_int(metrics.get("realized_exit_count")) > 0:
        lines.insert(
            -2,
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

    lines += ["", "---", "", "## 패턴 분석", ""]
    for label, key in (
        ("주요 진입 사유", "top_entry_reasons"),
        ("주요 청산 사유", "top_exit_reasons"),
        ("진입 패턴", "top_entry_pattern_types"),
        ("청산 패턴", "top_exit_pattern_types"),
        ("플레이북", "top_playbooks"),
    ):
        rows = patterns.get(key) if isinstance(patterns.get(key), list) else []
        text = ", ".join(f"{row.get('name')} ({row.get('count')})" for row in rows[:3] if isinstance(row, dict))
        lines.append(f"- {label}: {text or '없음'}")
    lines.extend(facade._render_pattern_performance_lines(payload))
    lines.extend(facade._render_quant_shadow_candidate_lines(payload))
    lines.extend(facade._render_strategist_llm_evaluation_lines(payload))

    bias = memory.get("bias_recommendation") if isinstance(memory.get("bias_recommendation"), dict) else {}
    if bias or risk_notes:
        lines += ["", "---", "", "## 거래 특징", ""]
        if bias:
            lines.append(f"- 메모리 bias: {facade.json.dumps(bias, ensure_ascii=False)}")
        for note in risk_notes:
            lines.append(f"- 리스크 메모: {note}")

    lines += [
        "",
        "---",
        "",
        "## 상세 분석",
        "",
        "> 개별 ai_trade_report.md와 symbol_trade_report.md를 참조합니다.",
        "",
    ]
    return "\n".join(lines)
