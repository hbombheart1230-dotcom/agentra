from __future__ import annotations

from typing import Any, Dict, List, Mapping


def enrich_exit_signal_snapshot_from_monitor(
    snapshot: Dict[str, Any],
    monitor: Dict[str, Any],
    *,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    _as_dict = deps["as_dict"]
    out = dict(snapshot or {})
    monitor = _as_dict(monitor)
    if not monitor:
        return out

    def _first_present(*keys: str) -> Any:
        for key in keys:
            value = monitor.get(key)
            if value not in (None, ""):
                return value
        return None

    def _set_if_present(key: str, *candidates: str) -> None:
        if out.get(key) not in (None, ""):
            return
        value = _first_present(*candidates)
        if value not in (None, ""):
            out[key] = value

    _set_if_present("gross_pnl_ratio", "gross_pnl_ratio", "exit_gross_pnl_ratio")
    _set_if_present("technical_pnl_ratio", "technical_pnl_ratio", "exit_technical_pnl_ratio")
    _set_if_present("effective_pnl_ratio", "effective_pnl_ratio", "exit_effective_pnl_ratio", "pnl_ratio", "exit_pnl_ratio")
    _set_if_present("stop_pnl_ratio", "stop_pnl_ratio", "exit_stop_pnl_ratio")
    _set_if_present("stop_pnl_ratio_source", "stop_pnl_ratio_source", "exit_stop_pnl_ratio_source")
    _set_if_present("hard_stop_pnl_ratio", "hard_stop_pnl_ratio", "exit_hard_stop_pnl_ratio")
    _set_if_present("hard_stop_pnl_ratio_source", "hard_stop_pnl_ratio_source", "exit_hard_stop_pnl_ratio_source")
    _set_if_present("cost_drag_pressure_pct", "cost_drag_pressure_pct", "exit_cost_drag_pressure_pct")
    _set_if_present("cost_drag_pressure_reason", "cost_drag_pressure_reason", "exit_cost_drag_pressure_reason")
    _set_if_present("expected_exit_price", "expected_exit_price", "exit_expected_exit_price")
    _set_if_present("expected_exit_price_source", "expected_exit_price_source", "exit_expected_exit_price_source")
    _set_if_present("expected_exit_pnl_ratio", "expected_exit_pnl_ratio", "exit_expected_exit_pnl_ratio")
    _set_if_present("expected_exit_net_pnl_ratio", "expected_exit_net_pnl_ratio", "exit_expected_exit_net_pnl_ratio")
    _set_if_present(
        "expected_exit_profit_floor_gap_pct",
        "expected_exit_profit_floor_gap_pct",
        "exit_expected_exit_profit_floor_gap_pct",
    )
    _set_if_present(
        "expected_exit_profit_floor_blocked_reason",
        "expected_exit_profit_floor_blocked_reason",
        "exit_expected_exit_profit_floor_blocked_reason",
    )
    _set_if_present(
        "stop_loss_cost_drag_blocked_reason",
        "stop_loss_cost_drag_blocked_reason",
        "exit_stop_loss_cost_drag_blocked_reason",
    )
    _set_if_present("technical_price", "technical_price", "exit_technical_price")
    _set_if_present("technical_price_source", "technical_price_source", "exit_technical_price_source")
    _set_if_present("vwap", "vwap", "exit_vwap")
    _set_if_present("vwap_distance", "vwap_distance", "exit_vwap_distance")
    _set_if_present("vwap_distance_source", "vwap_distance_source", "exit_vwap_distance_source")
    _set_if_present("exit_trigger_metric_name", "exit_trigger_metric_name")
    _set_if_present("exit_trigger_metric_value", "exit_trigger_metric_value")
    _set_if_present("exit_trigger_metric_source", "exit_trigger_metric_source")
    _set_if_present("trend_strength", "trend_strength", "engine_trend_strength", "exit_trend_strength")
    _set_if_present("trend_strength_floor", "trend_strength_floor", "exit_trend_strength_floor")

    thresholds = _as_dict(_as_dict(monitor.get("thresholds_guards_used")).get("thresholds")) or _as_dict(monitor.get("thresholds"))
    if out.get("trend_strength_floor") in (None, "") and thresholds.get("trend_strength_floor") not in (None, ""):
        out["trend_strength_floor"] = thresholds.get("trend_strength_floor")
    if out.get("vwap_breakdown_pct") in (None, ""):
        threshold = _first_present(
            "vwap_breakdown_pct",
            "exit_vwap_breakdown_pct",
            "monitor_vwap_breakdown_pct",
        )
        if threshold in (None, ""):
            threshold = thresholds.get("vwap_breakdown_pct")
        if threshold not in (None, ""):
            out["vwap_breakdown_pct"] = threshold

    for key, candidates in {
        "cost_drag_pressure": ("cost_drag_pressure", "exit_cost_drag_pressure"),
        "stop_loss_cost_drag_blocked": (
            "stop_loss_cost_drag_blocked",
            "exit_stop_loss_cost_drag_blocked",
        ),
        "expected_exit_profit_floor_met": (
            "expected_exit_profit_floor_met",
            "exit_expected_exit_profit_floor_met",
        ),
        "expected_exit_profit_floor_blocked": (
            "expected_exit_profit_floor_blocked",
            "exit_expected_exit_profit_floor_blocked",
        ),
    }.items():
        if out.get(key) not in (None, ""):
            continue
        value = _first_present(*candidates)
        if value not in (None, ""):
            out[key] = bool(value)

    if out:
        out.setdefault("basis", "monitor_signal_snapshot")
        out.setdefault("truth_note", "체결가와 실현손익은 Truth Surface 기준입니다.")
    return out


def build_summary_exit_trigger_lines(
    exit_trigger: Any,
    exit_signal_snapshot: Dict[str, Any],
    *,
    fallback_reason: Any = "",
    buy_price: Any = "",
    exit_price: Any = "",
    pnl_pct: Any = "",
    truth_source: Any = "",
    deps: Mapping[str, Any],
) -> List[str]:
    _fmt_pct = deps["fmt_pct"]
    _fmt_signed_pct = deps["fmt_signed_pct"]
    _metadata_value = deps["metadata_value"]
    _normalize_exit_trigger_label = deps["normalize_exit_trigger_label"]
    _num_opt = deps["num_opt"]
    _summary_money = deps["summary_money"]
    _truth_source_label = deps["truth_source_label"]
    raw_trigger_value = exit_signal_snapshot.get("trigger") or exit_trigger
    raw_trigger_text = " ".join(
        str(part or "")
        for part in (raw_trigger_value, fallback_reason)
        if str(part or "").strip()
    )
    trigger_label = _normalize_exit_trigger_label(
        raw_trigger_value,
        fallback_reason,
    )
    raw_trigger_lower = raw_trigger_text.strip().lower()
    execution_only_exit = (
        "sell_execution_confirmed" in raw_trigger_lower
        or "full_sell_quantity_reconciled" in raw_trigger_lower
        or "sell 실행 및 잔여수량" in raw_trigger_text
        or "매도 실행 확인" in trigger_label
        or "전량 매도 수량 확인" in trigger_label
    )
    missing_trigger = (
        execution_only_exit
        or "exit_trigger_not_captured" in raw_trigger_lower
        or "monitor_exit_trigger_not_captured" in raw_trigger_lower
        or "청산 트리거 미확인" in raw_trigger_text
        or "청산 이유는 기록되지" in raw_trigger_text
        or "exit reasoning was not captured" in raw_trigger_lower
    )
    if missing_trigger:
        trigger_label = "모니터 청산 트리거 미확인"
    lines = [f"트리거: {trigger_label}"]
    if execution_only_exit:
        lines.append("체결 상태: SELL 실행 및 잔여수량 0 확인으로 전량 청산")
    trigger_metric_name = str(exit_signal_snapshot.get("exit_trigger_metric_name") or "").strip().lower()
    trigger_metric_value = exit_signal_snapshot.get("exit_trigger_metric_value")
    vwap_distance = exit_signal_snapshot.get("vwap_distance")
    if vwap_distance in (None, "") and trigger_metric_name == "vwap_distance":
        vwap_distance = trigger_metric_value
    vwap_distance_num = _num_opt(vwap_distance)
    is_vwap_trigger = "VWAP" in trigger_label or "vwap" in trigger_label.lower() or trigger_metric_name == "vwap_distance"
    if is_vwap_trigger and vwap_distance_num is not None:
        lines[0] = f"트리거: {trigger_label} (VWAP 대비 {_fmt_signed_pct(vwap_distance_num)})"

    trend_strength = exit_signal_snapshot.get("trend_strength")
    if trend_strength in (None, "") and trigger_metric_name == "trend_strength":
        trend_strength = trigger_metric_value
    trend_strength_num = _num_opt(trend_strength)
    trend_floor_num = _num_opt(exit_signal_snapshot.get("trend_strength_floor"))
    is_trend_trigger = (
        trigger_metric_name == "trend_strength"
        or "추세" in trigger_label
        or "trend" in str(trigger_label or "").lower()
    )
    if is_trend_trigger and trend_strength_num is not None:
        floor_text = f" <= 기준 {trend_floor_num:.4f}" if trend_floor_num is not None else ""
        lines[0] = f"트리거: 추세 훼손 (추세강도 {trend_strength_num:.4f}{floor_text})"

    observation_parts: List[str] = []
    if exit_signal_snapshot.get("confirm_state"):
        observation_parts.append(f"확인 조건 {exit_signal_snapshot.get('confirm_state')}")
    if exit_signal_snapshot.get("monitor_current_price") not in (None, ""):
        observation_parts.append(f"현재가 {_summary_money(exit_signal_snapshot.get('monitor_current_price'))}")
    if is_vwap_trigger and vwap_distance_num is not None:
        vwap_value = _num_opt(exit_signal_snapshot.get("vwap"))
        current_value = _num_opt(exit_signal_snapshot.get("monitor_current_price"))
        if vwap_value is None and current_value is not None and (1.0 + vwap_distance_num) > 0.0:
            vwap_value = current_value / (1.0 + vwap_distance_num)
        vwap_parts = []
        if vwap_value is not None:
            vwap_parts.append(f"VWAP {_summary_money(vwap_value)}")
        vwap_parts.append(f"VWAP 대비 {_fmt_signed_pct(vwap_distance_num)}")
        threshold_num = _num_opt(exit_signal_snapshot.get("vwap_breakdown_pct"))
        if threshold_num is not None:
            vwap_parts.append(f"이탈 기준 {_fmt_signed_pct(-abs(threshold_num))}")
        observation_parts.append(" / ".join(vwap_parts))
    if is_trend_trigger and trend_strength_num is not None:
        trend_parts = [f"추세강도 {trend_strength_num:.4f}"]
        if trend_floor_num is not None:
            trend_parts.append(f"훼손 기준 {trend_floor_num:.4f}")
        source = _metadata_value(exit_signal_snapshot.get("exit_trigger_metric_source"))
        if source and source != "-":
            trend_parts.append(f"소스 {source}")
        observation_parts.append(" / ".join(trend_parts))
    if exit_signal_snapshot.get("position_avg_price") not in (None, ""):
        observation_parts.append(
            f"포지션 평균단가(모니터 신호 계산용) {_summary_money(exit_signal_snapshot.get('position_avg_price'))}"
        )
    if exit_signal_snapshot.get("peak_price") not in (None, ""):
        observation_parts.append(f"고점 {_summary_money(exit_signal_snapshot.get('peak_price'))}")
    monitor_drawdown_pct = (
        exit_signal_snapshot.get("monitor_drawdown_pct_text")
        or exit_signal_snapshot.get("monitor_pnl_pct_text")
    )
    if monitor_drawdown_pct:
        observation_parts.append(f"고점 대비 하락폭 {monitor_drawdown_pct}")
    if observation_parts:
        observation_label = (
            "마지막 모니터 관측값(청산 트리거 아님)"
            if missing_trigger
            else "모니터 관측값(신호 판단용)"
        )
        lines.append(f"{observation_label}: " + " / ".join(observation_parts))

    pnl_basis_parts: List[str] = []
    gross_pnl = exit_signal_snapshot.get("gross_pnl_ratio")
    effective_pnl = exit_signal_snapshot.get("effective_pnl_ratio")
    stop_pnl = exit_signal_snapshot.get("stop_pnl_ratio")
    hard_stop_pnl = exit_signal_snapshot.get("hard_stop_pnl_ratio")
    if gross_pnl not in (None, ""):
        pnl_basis_parts.append(f"가격 기준 손익 {_fmt_pct(gross_pnl)}")
    if effective_pnl not in (None, ""):
        pnl_basis_parts.append(f"비용/계좌 반영 손익 {_fmt_pct(effective_pnl)}")
    if stop_pnl not in (None, ""):
        source = _metadata_value(exit_signal_snapshot.get("stop_pnl_ratio_source"))
        suffix = f", {source}" if source and source != "-" else ""
        pnl_basis_parts.append(f"일반 손절 판단 기준 {_fmt_pct(stop_pnl)}{suffix}")
    if hard_stop_pnl not in (None, ""):
        source = _metadata_value(exit_signal_snapshot.get("hard_stop_pnl_ratio_source"))
        suffix = f", {source}" if source and source != "-" else ""
        pnl_basis_parts.append(f"하드스탑 판단 기준 {_fmt_pct(hard_stop_pnl)}{suffix}")
    if pnl_basis_parts:
        lines.append("손익 기준 분리: " + " / ".join(pnl_basis_parts))

    if exit_signal_snapshot.get("cost_drag_pressure"):
        pressure_pct = _fmt_pct(exit_signal_snapshot.get("cost_drag_pressure_pct"))
        reason = _metadata_value(exit_signal_snapshot.get("cost_drag_pressure_reason"))
        detail = f" ({pressure_pct})" if pressure_pct != "-" else ""
        if reason and reason != "-":
            detail += f", {reason}"
        lines.append("비용 압박: 비용/계좌 반영 손익이 가격 기준보다 낮게 잡혔습니다" + detail)
    if exit_signal_snapshot.get("stop_loss_cost_drag_blocked"):
        reason = _metadata_value(exit_signal_snapshot.get("stop_loss_cost_drag_blocked_reason"))
        suffix = f" ({reason})" if reason and reason != "-" else ""
        lines.append("일반 손절 차단: 가격 기준 손절선은 미통과했고 비용 반영 손익만 손절선을 건드렸습니다" + suffix)
    if exit_signal_snapshot.get("expected_exit_price") not in (None, ""):
        source = _metadata_value(exit_signal_snapshot.get("expected_exit_price_source"))
        source_suffix = f", {source}" if source and source != "-" else ""
        expected_parts = [
            f"예상 체결가 {_summary_money(exit_signal_snapshot.get('expected_exit_price'))}{source_suffix}",
        ]
        if exit_signal_snapshot.get("expected_exit_pnl_ratio") not in (None, ""):
            expected_parts.append(f"예상 가격 손익 {_fmt_pct(exit_signal_snapshot.get('expected_exit_pnl_ratio'))}")
        if exit_signal_snapshot.get("expected_exit_net_pnl_ratio") not in (None, ""):
            expected_parts.append(f"예상 비용 차감 손익 {_fmt_pct(exit_signal_snapshot.get('expected_exit_net_pnl_ratio'))}")
        if exit_signal_snapshot.get("expected_exit_profit_floor_met") not in (None, ""):
            expected_parts.append(
                "비용 바닥 통과" if exit_signal_snapshot.get("expected_exit_profit_floor_met") else "비용 바닥 미통과"
            )
        lines.append("예상 체결가 비용 점검: " + " / ".join(expected_parts))
    if exit_signal_snapshot.get("expected_exit_profit_floor_blocked"):
        reason = _metadata_value(exit_signal_snapshot.get("expected_exit_profit_floor_blocked_reason"))
        suffix = f" ({reason})" if reason and reason != "-" else ""
        lines.append("익절 보류: 예상 체결가 기준 비용 바닥을 통과하지 못했습니다" + suffix)

    truth_parts: List[str] = []
    if buy_price not in (None, ""):
        truth_parts.append(f"매수가 {_summary_money(buy_price)}")
    if exit_price not in (None, ""):
        truth_parts.append(f"매도가 {_summary_money(exit_price)}")
    elif buy_price not in (None, ""):
        truth_parts.append("매도 체결가 미확정")
    if pnl_pct not in (None, ""):
        truth_parts.append(f"실현손익률 {_fmt_pct(pnl_pct)}")
    truth_label = _truth_source_label(truth_source)
    if truth_label and truth_label != "-":
        truth_parts.append(truth_label)
    if truth_parts:
        lines.append("체결/실현손익 기준: Truth Surface의 " + " / ".join(truth_parts))
    return lines


