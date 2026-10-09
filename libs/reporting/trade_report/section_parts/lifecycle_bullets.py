from __future__ import annotations

import json
from typing import Any, Dict, Mapping

def build_holding_story_bullets(holding_summary: Dict[str, Any], monitor_reason: Dict[str, Any], *, deps: Mapping[str, Any]) -> List[str]:
    _clip = deps["clip"]
    _decision_chain_label = deps["decision_chain_label"]
    _dedupe_list = deps["dedupe_list"]
    _fmt_pct = deps["fmt_pct"]
    _fmt_price = deps["fmt_price"]
    _is_low_information_bullet = deps["is_low_information_bullet"]
    _korean_predicate = deps["korean_predicate"]
    _listify = deps["listify"]
    _operator_action_label = deps["operator_action_label"]
    _operator_axis_label = deps["operator_axis_label"]
    hold_count = len(list(holding_summary.get("run_ids") or []))
    watch_axes = ", ".join(_operator_axis_label(item) for item in _listify(monitor_reason.get("watch_axes"), max_items=6, max_len=80))
    decision_chain = " -> ".join(_decision_chain_label(item) for item in _listify(monitor_reason.get("decision_reason_chain"), max_items=5, max_len=60))
    hard_stop = _fmt_pct(monitor_reason.get("hard_stop_pct"))
    adaptive_stop = _fmt_pct(monitor_reason.get("adaptive_stop_loss_pct"))
    effective_stop = _fmt_pct(monitor_reason.get("effective_stop_loss_pct"))
    trailing_stop = _fmt_pct(monitor_reason.get("trailing_stop_pct"))
    take_profit = _fmt_pct(monitor_reason.get("take_profit_pct"))
    current_price = _fmt_price(monitor_reason.get("current_price"))
    average_price = _fmt_price(monitor_reason.get("average_price"))
    peak_price = _fmt_price(monitor_reason.get("peak_price"))
    current_drawdown = _fmt_pct(monitor_reason.get("current_drawdown"))
    peak_drawdown = _fmt_pct(monitor_reason.get("peak_drawdown"))
    bullets: List[str] = []
    if hold_count:
        bullets.append(f"모니터는 총 {hold_count}회 실행되었습니다.")
        bullets.append(f"Monitor runs: {hold_count}")
    if _clip(monitor_reason.get("posture"), max_len=48):
        bullets.append(f"현재 포지션 판단은 {_operator_action_label(monitor_reason.get('posture'))}입니다.")
    if _clip(monitor_reason.get("trigger_type"), max_len=64):
        trigger_label = _operator_axis_label(monitor_reason.get("trigger_type"))
        bullets.append(f"보유 중 가장 강하게 감시된 신호는 {trigger_label}{_korean_predicate(trigger_label)}")
    if monitor_reason.get("position_age_seconds") not in (None, ""):
        bullets.append(f"포지션 보유 시간은 약 {int(monitor_reason.get('position_age_seconds') or 0)}초입니다.")
    if effective_stop != "-":
        stop_reason = _clip(monitor_reason.get("effective_stop_reason"), max_len=64)
        suffix = f", 기준 축은 {_operator_axis_label(stop_reason)}입니다." if stop_reason else ""
        bullets.append(f"유효 손절 기준은 {effective_stop}입니다{suffix}")
    if take_profit != "-":
        bullets.append(f"목표 수익 실현 기준은 {take_profit} 수준입니다.")
    if _clip(monitor_reason.get("active_exit_axis"), max_len=80):
        axis_label = _operator_axis_label(monitor_reason.get("active_exit_axis"))
        bullets.append(f"당시 우선 감시 중이던 청산 축은 {axis_label}{_korean_predicate(axis_label)}")
    if monitor_reason.get("confirm_required") is not None:
        bullets.append(f"청산 확인 조건은 {int(monitor_reason.get('confirm_count') or 0)}/{int(monitor_reason.get('confirm_required') or 0)} 단계로 기록되었습니다.")
    if watch_axes:
        bullets.append(f"주요 감시 축은 {watch_axes}입니다.")
    if decision_chain:
        bullets.append(f"판단 흐름은 {decision_chain} 순서로 이어졌습니다.")
    if current_price != "-" or average_price != "-" or peak_price != "-":
        bullets.append(f"현재가, 평균가, 고점 기준 값은 {current_price} / {average_price} / {peak_price}입니다.")
    if current_drawdown != "-" or peak_drawdown != "-":
        bullets.append(f"현재 손익 변동과 고점 대비 하락폭은 {current_drawdown} / {peak_drawdown}입니다.")
    if _clip(monitor_reason.get("price_source"), max_len=80):
        bullets.append(f"가격 기준 소스는 {_clip(monitor_reason.get('price_source'), max_len=80)}입니다.")
    if _clip(monitor_reason.get("feature_source"), max_len=80):
        bullets.append(f"지표 기준 소스는 {_clip(monitor_reason.get('feature_source'), max_len=80)}입니다.")

    recent_updates = [
        _clip(item, max_len=180)
        for item in list(holding_summary.get("monitor_updates") or [])[-4:]
        if str(item or "").strip() and not _is_low_information_bullet(item)
    ]
    for item in recent_updates:
        bullets.append(f"최근 모니터 업데이트는 다음과 같습니다: {item}")
    return _dedupe_list(bullets, max_items=14, max_len=260)



def build_exit_decision_bullets(
    exit_summary: Dict[str, Any],
    monitor_context: Dict[str, Any],
    *,
    status_text: str,
    deps: Mapping[str, Any],
) -> List[str]:
    _clip = deps["clip"]
    _decision_chain_label = deps["decision_chain_label"]
    _dedupe_list = deps["dedupe_list"]
    _exit_reason_label = deps["exit_reason_label"]
    _fmt_pct = deps["fmt_pct"]
    _fmt_price = deps["fmt_price"]
    _korean_predicate = deps["korean_predicate"]
    _listify = deps["listify"]
    _operator_action_label = deps["operator_action_label"]
    _operator_axis_label = deps["operator_axis_label"]
    guard_context = exit_summary.get("guard_context") if isinstance(exit_summary.get("guard_context"), dict) else {}
    execution_context = exit_summary.get("execution_context") if isinstance(exit_summary.get("execution_context"), dict) else {}
    reason_label = _exit_reason_label(exit_summary.get("reason_human"))
    decision_chain = " -> ".join(_decision_chain_label(item) for item in _listify(monitor_context.get("decision_reason_chain"), max_items=5, max_len=60))
    bullets: List[str] = [
        f"청산 판단이 기록된 run은 {_clip(exit_summary.get('run_id'), max_len=80) or 'not_captured'}입니다.",
        f"청산 시각은 {_clip(exit_summary.get('ts'), max_len=80) or 'not_captured'}입니다.",
        f"청산 액션은 {_operator_action_label(_clip(exit_summary.get('action'), max_len=40) or ('HOLD' if status_text == 'open' else 'not_captured'))}입니다.",
        f"청산 사유는 {reason_label or ('포지션이 아직 열려 있음' if status_text == 'open' else '기록 없음')}입니다.",
    ]
    if _clip(monitor_context.get("trigger_type"), max_len=80):
        trigger_label = _operator_axis_label(monitor_context.get("trigger_type"))
        bullets.append(f"청산을 직접 촉발한 신호는 {trigger_label}{_korean_predicate(trigger_label)}")
        bullets.append(f"Trigger type: {trigger_label}")
    if _clip(monitor_context.get("active_exit_axis"), max_len=120):
        axis_label = _operator_axis_label(monitor_context.get("active_exit_axis"))
        bullets.append(f"청산 시점 우선 감시 축은 {axis_label}{_korean_predicate(axis_label)}")
    if monitor_context.get("confirm_required") is not None:
        bullets.append(f"청산 확인 조건은 {int(monitor_context.get('confirm_count') or 0)}/{int(monitor_context.get('confirm_required') or 0)} 단계로 기록되었습니다.")
    effective_stop = _fmt_pct(monitor_context.get("effective_stop_loss_pct"))
    if effective_stop != "-":
        stop_reason = _clip(monitor_context.get("effective_stop_reason"), max_len=64)
        suffix = f", 기준 축은 {_operator_axis_label(stop_reason)}입니다." if stop_reason else ""
        bullets.append(f"청산 시점의 유효 손절 기준은 {effective_stop}입니다{suffix}")
    take_profit = _fmt_pct(monitor_context.get("take_profit_pct"))
    if take_profit != "-":
        bullets.append(f"청산 시점의 목표 수익 실현 기준은 {take_profit} 수준입니다.")
    current_price = _fmt_price(monitor_context.get("current_price"))
    average_price = _fmt_price(monitor_context.get("average_price"))
    peak_price = _fmt_price(monitor_context.get("peak_price"))
    if current_price != "-" or average_price != "-" or peak_price != "-":
        bullets.append(f"현재가, 평균가, 고점 기준 값은 {current_price} / {average_price} / {peak_price}입니다.")
    current_drawdown = _fmt_pct(monitor_context.get("current_drawdown"))
    peak_drawdown = _fmt_pct(monitor_context.get("peak_drawdown"))
    if current_drawdown != "-" or peak_drawdown != "-":
        bullets.append(f"현재 손익 변동과 고점 대비 하락폭은 {current_drawdown} / {peak_drawdown}입니다.")
    if not decision_chain:
        decision_chain = reason_label
    if decision_chain:
        bullets.append(f"판단 흐름은 {decision_chain} 기준으로 이어졌습니다.")
    if _clip(guard_context.get("summary"), max_len=220):
        bullets.append(f"가드 판단 결과는 {_clip(guard_context.get('summary'), max_len=220)}입니다.")
    if _clip(execution_context.get("summary"), max_len=220):
        bullets.append(f"주문 실행 결과는 {_clip(execution_context.get('summary'), max_len=220)}입니다.")
    if _clip(monitor_context.get("price_source"), max_len=80):
        bullets.append(f"가격 기준 소스는 {_clip(monitor_context.get('price_source'), max_len=80)}입니다.")
    if _clip(monitor_context.get("feature_source"), max_len=80):
        bullets.append(f"지표 기준 소스는 {_clip(monitor_context.get('feature_source'), max_len=80)}입니다.")
    return _dedupe_list(bullets, max_items=16, max_len=260)


