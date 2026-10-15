"""Operator brief renderer: pure text/label/metric helper closures.

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `apps/operator_ui/data_access_core.py::_render_operator_brief_markdown` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def operator_brief_text_helpers(*, facade):
    def _action_label(action: facade.Any) -> str:
        mapping = {
            "BUY": "매수",
            "SELL": "매도",
            "HOLD": "보유 유지",
            "WAIT": "진입 보류",
        }
        return mapping.get(str(action or "").strip().upper(), str(action or "-").strip() or "-")

    def _metric_text(value: facade.Any) -> str:
        text = facade._sanitize_operator_brief_text(value)
        return text or "-"

    def _axis_label(value: facade.Any) -> str:
        raw = facade._sanitize_operator_brief_text(value)
        lowered = raw.lower()
        mapping = {
            "고정 손절 기준": "고정 손절 기준",
            "상황 대응형 손절 기준": "상황 대응형 손절 기준",
            "목표 수익 실현 기준": "목표 수익 실현 기준",
            "hard stop": "고정 손절 기준",
            "adaptive stop": "상황 대응형 손절 기준",
            "take profit": "목표 수익 실현 기준",
            "vwap breakdown": "VWAP 이탈",
            "vwap_breakdown": "VWAP 이탈",
            "peak drawdown": "고점 대비 하락폭 확대",
            "peak_drawdown": "고점 대비 하락폭 확대",
            "prior low break": "직전 저점 이탈",
            "prior_low_break": "직전 저점 이탈",
            "intraday low break": "장중 저점 이탈",
            "intraday_low_break": "장중 저점 이탈",
            "confirmed_exit_signal": "청산 확인 신호",
            "defensive exit": "방어형 청산 신호",
            "defensive_exit": "방어형 청산 신호",
            "방어형 청산": "방어형 청산 신호",
            "기록되지 않음": "기록된 기준 축 없음",
            "확인되지 않음": "기록된 기준 축 없음",
            "판단 정보 없음": "기록된 기준 축 없음",
            "포지션 없음": "포지션 없음",
        }
        return mapping.get(lowered, raw or "감시 조건 변화")

    def _axis_is_explicit(value: str) -> bool:
        return str(value or "").strip() not in {"", "-", "감시 조건 변화", "기록된 기준 축 없음", "포지션 없음", "판단 정보 없음"}

    def _narrative_text(text: facade.Any) -> str:
        raw_source = facade._trim_text(text, max_len=1000)
        cleaned = facade._sanitize_operator_brief_text(text)
        if not cleaned:
            return ""
        raw_lower = raw_source.lower()
        m = facade.re.fullmatch(r"universe scanned\s*:\s*(\d+)", raw_lower)
        if m:
            return f"총 {m.group(1)}개 후보를 비교했습니다."
        m = facade.re.fullmatch(r"selected rank\s*:\s*#?(\d+)", raw_lower)
        if m:
            return f"비교 대상 중 {m.group(1)}순위로 선정되었습니다."
        m = facade.re.fullmatch(r"posture\s*:\s*(buy|sell|hold|wait)", raw_lower)
        if m:
            return f"현재 포지션 판단은 {_action_label(m.group(1))}입니다."
        m = facade.re.fullmatch(r"trigger\s*:\s*(.+)", raw_lower)
        if m:
            trigger = m.group(1).strip()
            if trigger in {"-", "no", "none"}:
                return "추가 진입 또는 청산을 확정할 신호는 아직 확인되지 않았습니다."
            return f"현재 감시 신호는 {cleaned.split(':', 1)[-1].strip()}입니다."
        m = facade.re.fullmatch(r"exit trigger\s*:\s*(.+)", raw_lower)
        if m:
            trigger = m.group(1).strip()
            if trigger in {"-", "no", "none"}:
                return "아직 청산 신호는 확인되지 않았습니다."
            return f"현재 확인된 청산 신호는 {cleaned.split(':', 1)[-1].strip()}입니다."
        if raw_lower.startswith("runner-up symbols had weaker coverage"):
            return "후순위 후보는 차트 완성도와 보조 신호가 더 약했습니다."
        m = facade.re.fullmatch(r"chart / feature coverage\s*:\s*(\d+)/(\d+)", raw_lower)
        if m:
            return f"차트와 피처 확인 항목은 {m.group(1)}/{m.group(2)} 수준으로 확보되었습니다."
        m = facade.re.fullmatch(r"chart completeness filter\s*:\s*pass\s*-\s*(.+)", raw_lower)
        if m:
            return f"차트 확인 조건은 {m.group(1).strip()} 수준으로 충족되었습니다."
        if raw_lower.startswith("liquidity filter:"):
            return "유동성 조건은 충족되었습니다."
        if raw_lower.startswith("turnover filter:"):
            return "거래대금 조건은 충족되었습니다."
        if facade.re.match(r"^[A-Za-z][A-Za-z0-9 /_-]*:\s*", raw_source):
            return ""
        return cleaned

    def _append_list(lines: facade.List[str], items: facade.List[str], *, limit: int = 3) -> None:
        appended = 0
        for item in items:
            text = _narrative_text(item)
            if not text or facade._count_hangul_chars(text) <= 0:
                continue
            lines.append(f"- {text}")
            appended += 1
            if appended >= limit:
                break

    def _vwap_interpretation(value: facade.Any) -> str:
        raw = facade._safe_float(value, None)
        if raw is None:
            return "-"
        if raw >= 0.02:
            return f"{facade._format_percent(raw, 2)} (과도 확장으로 추격 진입에 주의가 필요한 구간입니다.)"
        if raw >= 0.0:
            return f"+{abs(raw) * 100:.2f}% (VWAP 위에서 흐름을 유지하고 있습니다.)"
        if raw <= -0.01:
            return f"{facade._format_percent(raw, 2)} (VWAP 아래로 밀리며 약세 압력이 커진 구간입니다.)"
        return f"{facade._format_percent(raw, 2)} (중립 범위 안에서 움직이고 있습니다.)"

    def _entry_reason_text(reason_code: str, pattern: str, metrics: facade.Dict[str, facade.Any], posture_action: str) -> str:
        reason = str(reason_code or "").strip().lower()
        metric_map = metrics if isinstance(metrics, dict) else {}
        recent_high = metric_map.get("recent_high")
        vwap = metric_map.get("vwap")
        volume_ratio = metric_map.get("volume_ratio")
        vwap_distance = metric_map.get("vwap_distance")
        pullback_pct = metric_map.get("pullback_pct")
        executed_trade = posture_action in {"BUY", "HOLD", "SELL"}
        if pattern in {"breakout_vwap_hold", "breakout"}:
            parts = ["분봉 기준으로 최근 고점 돌파와 VWAP 상회 유지, 거래량 확인이 함께 맞물려 진입했습니다."]
            if recent_high not in (None, ""):
                parts.append(f"최근 고점 기준값은 {facade._format_float(recent_high, 2)}였습니다.")
            if vwap not in (None, ""):
                parts.append(f"당시 VWAP 기준값은 {facade._format_float(vwap, 2)}였습니다.")
            if volume_ratio not in (None, ""):
                parts.append(f"거래량은 평시 대비 {facade._format_float(volume_ratio, 2)}배 수준으로 확인됐습니다.")
            return " ".join(parts)
        if pattern in {"pullback_rebound", "pullback_vwap_hold"}:
            parts = ["분봉 기준으로 눌림 이후 반등이 확인됐고, VWAP 재안착 흐름까지 확인되어 진입했습니다."]
            if pullback_pct not in (None, ""):
                parts.append(f"눌림 폭은 {facade._format_percent(pullback_pct, 2)} 수준이었습니다.")
            if volume_ratio not in (None, ""):
                parts.append(f"거래량은 평시 대비 {facade._format_float(volume_ratio, 2)}배 수준으로 확인됐습니다.")
            return " ".join(parts)
        mapping = {
            "minute_candle_missing": "이번 거래는 분봉 데이터가 확보되지 않아 진입 근거를 확인할 수 없었습니다. 따라서 신규 진입은 보류 대상으로 해석했습니다.",
            "data_incomplete": "체결 이전 분봉 기록이 충분하지 않아 진입 시점을 확정하기 어렵습니다. 현재 문서는 보유 관리와 청산 기준 중심으로 정리했습니다.",
            "no_breakout_signal": "저장된 분봉 범위에서는 최근 고점 돌파나 첫 눌림목 반등 신호가 확인되지 않았습니다. 따라서 진입은 보류 판단으로 정리했습니다.",
            "vwap_not_confirmed": "분봉 흐름에서 VWAP 상회 유지나 재안착이 확인되지 않았습니다. 추격 진입 위험을 피하기 위해 진입 보류로 해석했습니다.",
            "volume_insufficient": "분봉 거래량이 돌파 신호를 뒷받침할 만큼 충분하지 않았습니다. 따라서 이번 구간은 보수적으로 진입 보류로 판단했습니다.",
            "too_extended_from_vwap": "VWAP 대비 과도하게 확장된 상태여서 추격 진입을 피했습니다.",
            "post_exit_cooldown": "직전 청산 직후 재진입 쿨다운 구간이라 신규 진입을 보류했습니다.",
            "buy_blocked_open_position": "기존 보유 포지션이 있어 신규 진입을 차단했습니다.",
            "no_position": "저장된 데이터 범위 안에서는 체결 직전 분봉 진입 근거가 충분히 남아 있지 않았습니다. 이번 문서는 진입 해석보다 이후 보유 관리 기록을 중심으로 정리했습니다.",
            "peak_drawdown": "이번 저장값에는 진입 근거보다 청산 관리 신호가 더 선명하게 남아 있습니다. 진입 시점의 분봉 근거는 별도로 확인되지 않아 보수적으로 정리했습니다.",
            "hard_stop": "이번 저장값에는 진입 근거보다 손절 관리 신호가 더 분명하게 남아 있습니다. 진입 시점의 분봉 근거는 별도로 확인되지 않아 보수적으로 정리했습니다.",
            "pullback_structure_above_vwap_with_confirmation": "분봉 기준으로 VWAP 상단 눌림 이후 재확인 신호가 확인되어 진입했습니다.",
        }
        if mapping.get(reason):
            return mapping[reason]
        if str(reason_code or "").strip():
            reason_text = facade._sanitize_operator_brief_text(str(reason_code or "").strip())
            if executed_trade:
                return f"분봉 조건 점검 결과 {reason_text} 신호가 확인되어 진입했습니다."
            return f"분봉 조건 점검 결과 {reason_text} 상태로 해석되어 진입을 보류했습니다."
        if vwap_distance not in (None, ""):
            return f"분봉 조건을 점검 중이며 현재 VWAP 이격은 {facade._format_percent(vwap_distance, 2)} 수준입니다. 추가 확인 전까지는 보수적으로 접근합니다."
        return "분봉 데이터와 체결 근거를 보수적으로 점검한 결과, 당장 진입을 확정하기보다 추가 확인이 필요한 상태로 해석했습니다."

    def _default_next_checkpoints(entry: facade.Dict[str, facade.Any], monitor: facade.Dict[str, facade.Any], exit_plan: facade.Dict[str, facade.Any], posture_action: str) -> facade.List[str]:
        metrics = entry.get("metrics") if isinstance(entry.get("metrics"), dict) else {}
        watch_axes = [str(x or "").strip() for x in list(exit_plan.get("watch_axes") or monitor.get("watch_axes") or []) if str(x or "").strip()]
        derived: facade.List[str] = []
        if posture_action == "WAIT":
            if metrics.get("recent_high") not in (None, ""):
                derived.append("분봉 기준으로 최근 고점 재돌파 여부를 다음 체크포인트로 확인합니다.")
            if metrics.get("volume_ratio") not in (None, ""):
                derived.append("거래량 증가가 다시 동반되는지 확인합니다.")
            if not derived:
                derived.append("분봉 기준으로 재돌파 여부와 거래량 증가 여부를 다음 체크포인트로 설정합니다.")
        elif posture_action in {"BUY", "HOLD"}:
            derived.append("분봉 기준으로 지지선 유지 여부와 거래량 둔화 여부를 먼저 확인합니다.")
            if any("vwap" in axis.lower() for axis in watch_axes):
                derived.append("VWAP 재이탈 여부와 거래량 감소 여부를 중심으로 모니터링합니다.")
            derived.append("현재 보유 상태에서는 고점 대비 하락폭과 거래량 둔화를 주요 확인 지표로 봅니다.")
        else:
            derived.append("다음 거래에서는 분봉 진입 근거와 후보 비교 데이터가 충분히 남는지 먼저 확인합니다.")
            derived.append("청산 이후에는 동일 종목의 재돌파 여부와 거래대금 회복 여부를 다시 확인합니다.")
        return derived[:3]
    return (_action_label, _append_list, _axis_is_explicit, _axis_label, _default_next_checkpoints, _entry_reason_text, _metric_text, _narrative_text, _vwap_interpretation)
