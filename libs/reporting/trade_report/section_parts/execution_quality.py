from __future__ import annotations

import json
from typing import Any, Dict, Mapping

def build_execution_quality_section(
    story_input: Dict[str, Any],
    execution_outcome: Dict[str, Any],
    lifecycle_summary: Dict[str, Any],
    *,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    _clip = deps["clip"]
    _dedupe_list = deps["dedupe_list"]
    _execution_mode_label = deps["execution_mode_label"]
    _fmt_price = deps["fmt_price"]
    _korean_euro_ro = deps["korean_euro_ro"]
    _operator_action_label = deps["operator_action_label"]
    _operatorize_report_text = deps["operatorize_report_text"]
    build_execution_truth_bullets = deps["build_execution_truth_bullets"]
    execution_details = story_input.get("execution_details") if isinstance(story_input.get("execution_details"), dict) else {}
    symbol = _clip(story_input.get("symbol"), max_len=24) or "종목"
    action = _operator_action_label(_clip(story_input.get("action"), max_len=24) or "WAIT")
    filled_qty = execution_details.get("filled_qty")
    filled_price = _fmt_price(execution_details.get("filled_price"))
    avg_price = _fmt_price(execution_details.get("avg_price"))
    order_status = _clip(execution_details.get("order_status"), max_len=80)
    order_id = _clip(execution_details.get("order_id"), max_len=120)
    execution_mode = _clip(execution_details.get("execution_mode"), max_len=80)
    execution_mode_label = _clip(story_input.get("execution_mode_label"), max_len=80)
    broker_env = _clip(execution_details.get("broker_env"), max_len=80)
    outcome = _clip(execution_outcome.get("outcome"), max_len=80)
    quantity = execution_outcome.get("quantity")
    order_status_label = {
        "allowed": "허용",
        "approved": "승인",
        "recorded": "기록 완료",
        "rejected": "거부",
    }.get(order_status.lower(), order_status) if order_status else ""
    mode_label = {
        "real": "실거래",
        "live": "실거래",
        "simulation": "시뮬레이션",
    }.get(execution_mode.lower(), execution_mode) if execution_mode else ""
    if execution_mode_label:
        mode_label = _execution_mode_label(execution_mode_label)

    summary_parts: List[str] = []
    if outcome == "recorded":
        qty_text = str(int(quantity)) if quantity not in (None, "") else (str(int(filled_qty)) if filled_qty not in (None, "") else "기록된 수량")
        summary_parts.append(f"{symbol} {qty_text}주 {action} 주문은 승인 및 기록까지 확인됐습니다.")
    elif _clip(execution_outcome.get("summary"), max_len=300):
        summary_parts.append(_operatorize_report_text(execution_outcome.get("summary")))
    elif _clip(lifecycle_summary.get("lifecycle_summary_human"), max_len=300):
        summary_parts.append(_operatorize_report_text(lifecycle_summary.get("lifecycle_summary_human")))
    else:
        summary_parts.append("실행 품질 세부 정보는 제한적으로만 확인됩니다.")
    if filled_price != "-":
        summary_parts.append(f"체결 기준 가격은 {filled_price}였습니다.")
    summary = " ".join(summary_parts)

    bullets: List[str] = []
    if outcome:
        outcome_label = {"recorded": "기록 완료", "approved": "승인", "rejected": "거부"}.get(outcome, outcome)
        bullets.append(f"주문 실행 결과는 {outcome_label}였습니다.")
    if quantity not in (None, ""):
        bullets.append(f"주문 수량은 {int(quantity)}주였습니다.")
    elif filled_qty not in (None, ""):
        bullets.append(f"체결 수량은 {int(filled_qty)}주였습니다.")
    if mode_label:
        bullets.append(f"실행 모드는 {mode_label}였습니다.")
    if broker_env:
        bullets.append(f"브로커 환경은 {broker_env}였습니다.")
    else:
        bullets.append("브로커 환경 정보는 별도로 기록되지 않았습니다.")
    if order_status_label:
        bullets.append(f"주문 상태는 {order_status_label}{_korean_euro_ro(order_status_label)} 확인됐습니다.")
    else:
        bullets.append("주문 상태는 별도로 기록되지 않았습니다.")
    if order_id:
        bullets.append(f"주문 번호는 {order_id}였습니다.")
    else:
        bullets.append("주문 번호는 별도로 기록되지 않았습니다.")
    if filled_price != "-":
        bullets.append(f"평균 체결가는 {filled_price}였습니다.")
    elif avg_price != "-":
        bullets.append(f"평균/포지션 기준가는 {avg_price}였지만 브로커 체결가는 직접 확보되지 않았습니다.")
    for bullet in build_execution_truth_bullets(execution_details=execution_details):
        if bullet not in bullets:
            bullets.append(bullet)

    return {
        "summary": summary,
        "bullets": _dedupe_list(bullets, max_items=12, max_len=260),
    }



