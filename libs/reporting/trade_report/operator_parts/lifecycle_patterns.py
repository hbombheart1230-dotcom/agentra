from __future__ import annotations

import re
from typing import Any, Optional


def resolve_lifecycle_operator_phrase(
    cleaned: str, *, safe_fullmatch: Any, _clip: Any,
    operator_action_label: Any, operator_axis_label: Any,
    operator_filter_label: Any, operator_filter_status: Any,
) -> Optional[str]:
    """Resolve observed lifecycle and execution/approval text, never change policy."""
    m = safe_fullmatch(r"Entry run:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        if value == "not_captured":
            return "진입 판단이 기록된 run 정보는 남아 있지 않습니다."
        return f"진입 판단이 기록된 run은 {value}입니다."
    m = safe_fullmatch(r"Entry time:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        if value == "not_captured":
            return "진입 시각은 별도로 기록되지 않았습니다."
        return f"진입 시각은 {value}입니다."
    m = safe_fullmatch(r"Entry action:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"진입 액션은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Entry reason:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=240)
        if value == "not_captured":
            return "진입 판단 사유는 별도로 기록되지 않았습니다."
        return f"진입 판단 근거는 {value}입니다."
    m = safe_fullmatch(r"보유 기간:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"보유 기간은 {_clip(m.group(1), max_len=140)}입니다."
    m = safe_fullmatch(r"모니터 실행:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"모니터 실행 기록은 {_clip(m.group(1), max_len=180)}입니다."
    m = safe_fullmatch(r"모니터 판단:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"모니터 판단 흐름은 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"Monitor runs:\s*(\d+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"모니터는 총 {m.group(1)}회 실행되었습니다."
    m = safe_fullmatch(r"Posture:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"현재 포지션 판단은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Trigger type:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"감지된 핵심 신호는 {operator_axis_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Position age:\s*(\d+)\s*seconds", cleaned, flags=re.IGNORECASE)
    if m:
        return f"포지션 보유 시간은 약 {m.group(1)}초입니다."
    m = safe_fullmatch(r"Effective stop:\s*([^(]+?)(?:\s*\((.+)\))?", cleaned, flags=re.IGNORECASE)
    if m:
        level = _clip(m.group(1), max_len=80)
        reason = operator_axis_label(m.group(2))
        if reason and reason != "-":
            return f"유효 손절 기준은 {level} 수준이며, 기준 축은 {reason}입니다."
        return f"유효 손절 기준은 {level} 수준입니다."
    m = safe_fullmatch(r"Take profit:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"목표 수익 실현 기준은 {_clip(m.group(1), max_len=80)} 수준입니다."
    m = safe_fullmatch(r"Active exit axis:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"현재 우선 감시 중인 청산 축은 {operator_axis_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Exit confirmation:\s*(\d+)/(\d+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"청산 확인 조건은 {m.group(1)}/{m.group(2)} 단계로 기록되었습니다."
    m = safe_fullmatch(r"Watch axes:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        axes = ", ".join(operator_axis_label(part.strip()) for part in m.group(1).split(","))
        return f"주요 감시 축은 {axes}입니다."
    m = safe_fullmatch(r"Decision chain:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"판단 흐름은 {_clip(m.group(1), max_len=220)} 순서로 이어졌습니다."
    m = safe_fullmatch(r"Current price / avg / peak:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"현재가, 평균가, 고점 기준 값은 {_clip(m.group(1), max_len=200)}입니다."
    m = safe_fullmatch(r"Current drawdown / peak drawdown:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"현재 손익 변동과 고점 대비 하락폭은 {_clip(m.group(1), max_len=200)}입니다."
    m = safe_fullmatch(r"Price source:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"가격 기준 소스는 {_clip(m.group(1), max_len=140)}입니다."
    m = safe_fullmatch(r"Feature source:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"지표 기준 소스는 {_clip(m.group(1), max_len=140)}입니다."
    m = safe_fullmatch(r"Recent monitor update:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"최근 모니터 업데이트는 다음과 같습니다: {_clip(m.group(1), max_len=240)}"
    m = safe_fullmatch(r"Exit run:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        if value == "not_captured":
            return "청산 판단이 기록된 run 정보는 남아 있지 않습니다."
        return f"청산 판단이 기록된 run은 {value}입니다."
    m = safe_fullmatch(r"Exit time:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        if value == "not_captured":
            return "청산 시각은 별도로 기록되지 않았습니다."
        return f"청산 시각은 {value}입니다."
    m = safe_fullmatch(r"Exit action:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"청산 액션은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Exit reason:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=240)
        if value in {"position still open", "still open"}:
            return "현재 포지션은 아직 열려 있어 확정된 청산 사유는 없습니다."
        if value == "not_captured":
            return "청산 사유는 별도로 기록되지 않았습니다."
        return f"청산 사유는 {value}입니다."
    m = safe_fullmatch(r"Execution outcome:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"주문 실행 결과는 {_clip(m.group(1), max_len=180)}입니다."
    m = safe_fullmatch(r"Quantity:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"수량: {_clip(m.group(1), max_len=80)}"
    m = safe_fullmatch(r"수량:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"수량: {_clip(m.group(1), max_len=80)}"
    m = safe_fullmatch(r"Execution mode:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"실행 모드: {_clip(m.group(1), max_len=120)}"
    m = safe_fullmatch(r"Broker environment:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        if value == "not_captured":
            return "브로커 환경 정보는 별도로 기록되지 않았습니다."
        return f"브로커 환경은 {value}입니다."
    m = safe_fullmatch(r"Supervisor verdict:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"감독 승인 판단은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Supervisor allow:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"주문 허용 여부는 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Guard reason:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"가드 판단 사유는 {_clip(m.group(1), max_len=200)}입니다."
    m = safe_fullmatch(r"Action reviewed:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"검토한 액션은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Symbol reviewed:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"검토한 종목은 {_clip(m.group(1), max_len=60)}입니다."
    m = safe_fullmatch(r"Approval mode:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        lowered_value = value.lower()
        if lowered_value == "not captured in the execution trace" or (
            "execution trace" in lowered_value and ("not captured" in lowered_value or "기록되지 않음" in value)
        ):
            return "승인 모드는 실행 추적에는 별도로 남아 있지 않습니다."
        return f"승인 모드는 {value}입니다."
    m = safe_fullmatch(r"Lifecycle status:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        status_token = _clip(m.group(1), max_len=80).strip().lower()
        status_label = {
            "closed": "종결",
            "open": "진행 중",
            "pending": "대기",
        }.get(status_token, _clip(m.group(1), max_len=80))
        return f"라이프사이클 상태 {status_label}"
    m = safe_fullmatch(r"Entry\s+([A-Z_]+)\s+was executed by run\s+([A-Za-z0-9_-]+)\.?", cleaned, flags=re.IGNORECASE)
    if m:
        return f"run {_clip(m.group(2), max_len=80)}에서 {operator_action_label(m.group(1))} 진입이 실행됐습니다."
    m = safe_fullmatch(r"Exit\s+([A-Z_]+)\s+was executed by run\s+([A-Za-z0-9_-]+)\.?", cleaned, flags=re.IGNORECASE)
    if m:
        return f"run {_clip(m.group(2), max_len=80)}에서 {operator_action_label(m.group(1))} 청산이 실행됐습니다."
    m = safe_fullmatch(r"슈퍼바이저 판단:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"감독 승인 판단은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"슈퍼바이저 허용:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"주문 허용 여부는 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"가드 이유:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"가드 판단 사유는 {_clip(m.group(1), max_len=200)}입니다."
    m = safe_fullmatch(r"검토된 액션:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"검토한 액션은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"(.+?):\s*(PASS|FAIL|NOT_AVAILABLE)\s*-\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"{operator_filter_label(m.group(1))}은 {operator_filter_status(m.group(2))}였습니다. 근거: {_clip(m.group(3), max_len=220)}"
    
    return None
