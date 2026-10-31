"""execution_truth_surface projections (moved verbatim from execution_truth_surface).

Module globals and helpers are resolved on ``facade`` (the execution_truth_surface module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def build_execution_truth_bullets(
    *,
    execution_details: Dict[str, Any] | None = None,
    shared_facts: Dict[str, Any] | None = None,
    facade: Any,
) -> List[str]:
    details = dict(execution_details or {})
    facts = dict(shared_facts or {})

    broker_truth_source = facade._clip(details.get("broker_truth_source"), max_len=80)
    broker_fill_price = details.get("filled_price") if broker_truth_source else facts.get("broker_fill_price")
    broker_buy_price = (
        details.get("broker_buy_price")
        if details.get("broker_buy_price") not in (None, "")
        else facts.get("broker_buy_price")
    )
    broker_fee = details.get("broker_fee") if details.get("broker_fee") not in (None, "") else facts.get("broker_fee")
    broker_tax = details.get("broker_tax") if details.get("broker_tax") not in (None, "") else facts.get("broker_tax")
    pnl_value = details.get("broker_realized_pnl") if details.get("broker_realized_pnl") not in (None, "") else facts.get("pnl")
    pnl_pct = details.get("broker_realized_pnl_pct") if details.get("broker_realized_pnl_pct") not in (None, "") else facts.get("pnl_pct")
    price_truth_source = facade._clip(facts.get("price_truth_source"), max_len=40)
    pnl_truth_source = facade._clip(details.get("pnl_truth_source") or facts.get("pnl_truth_source"), max_len=80)
    same_price_round_trip = False
    try:
        same_price_round_trip = (
            broker_buy_price not in (None, "")
            and broker_fill_price not in (None, "")
            and float(broker_buy_price) == float(broker_fill_price)
        )
    except Exception:
        same_price_round_trip = False

    bullets: List[str] = []
    if broker_fill_price not in (None, ""):
        bullets.append(f"브로커 체결 기준 가격은 {facade._fmt_price(broker_fill_price)}였습니다.")
    if facade._is_available(pnl_value):
        if pnl_pct not in (None, ""):
            bullets.append(f"브로커 실현 손익은 {pnl_value} / {facade._fmt_pct(pnl_pct)} 기준으로 정리했습니다.")
        else:
            bullets.append(f"브로커 실현 손익은 {pnl_value} 기준으로 정리했습니다.")
    if broker_fee not in (None, "") or broker_tax not in (None, ""):
        bullets.append(
            f"브로커 수수료/세금은 {broker_fee if broker_fee not in (None, '') else '-'} / {broker_tax if broker_tax not in (None, '') else '-'}였습니다."
        )
    if same_price_round_trip and facade._is_available(pnl_value):
        bullets.append("매수가와 매도가가 같았고, 손익은 가격 변동이 아니라 수수료와 세금에서 발생했습니다.")
    if broker_truth_source:
        bullets.append(f"체결 truth 소스는 {broker_truth_source}였습니다.")
    if price_truth_source and price_truth_source not in {"", "unavailable"}:
        bullets.append(f"가격 truth 소스는 {facade.with_ro_particle(facade.price_truth_source_label(price_truth_source))} 확인했습니다.")
    if pnl_truth_source and pnl_truth_source not in {"", "unavailable"}:
        bullets.append(f"손익 truth 소스는 {facade.with_ro_particle(facade.pnl_truth_source_label(pnl_truth_source))} 확인했습니다.")
    return bullets
