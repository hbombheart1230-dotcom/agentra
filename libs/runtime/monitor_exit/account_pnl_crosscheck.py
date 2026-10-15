"""Account PnL cross-check: account quantity/average/mark evidence and reference price.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `libs/runtime/exit_policy.py::_build_account_pnl_crosscheck` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class AccountPnlEvidence(NamedTuple):
    """Result of `resolve_account_pnl_evidence` (positional order = sorted output names)."""

    account_current_price: Any
    account_pnl_ratio: Any
    account_pnl_ratio_source: Any
    account_ratio_mark_price: Any
    account_unrealized_mark_price: Any
    account_unrealized_pnl: Any
    reference_price: Any

class AccountMarkPrice(NamedTuple):
    """Result of `resolve_account_mark_price` (positional order = sorted output names)."""

    account_mark_price: Any
    account_mark_price_source: Any
    fallback_price_source: Any
    pnl_fallback_applied: Any
    price_anomaly_flag: Any
    price_anomaly_reason: Any

class EffectivePriceResolution(NamedTuple):
    """Result of `resolve_effective_price` (positional order = sorted output names)."""

    applied: Any
    effective_price: Any
    effective_source: Any
    reason: Any

def resolve_account_pnl_evidence(avg, policy, q, raw_price, *, facade):
    account_qty_raw = policy.get("account_qty")
    account_qty = max(0, int(facade._to_float(account_qty_raw, float(q)))) if account_qty_raw not in (None, "") else q
    account_avg_raw = policy.get("account_avg_price")
    account_avg = facade._to_float(account_avg_raw, avg) if account_avg_raw not in (None, "") else avg
    account_current_price = None
    if policy.get("account_current_price") not in (None, ""):
        px = facade._to_float(policy.get("account_current_price"), 0.0)
        if px > 0.0:
            account_current_price = float(px)
    account_pnl_ratio = facade._to_ratio(policy.get("account_pnl_ratio"))
    account_pnl_ratio_source = str(policy.get("account_pnl_ratio_source") or "")

    account_unrealized_pnl = None
    if policy.get("account_unrealized_pnl") not in (None, ""):
        account_unrealized_pnl = float(facade._to_float(policy.get("account_unrealized_pnl"), 0.0))

    account_ratio_mark_price = None
    if account_pnl_ratio is not None and account_avg > 0.0:
        account_mark = float(account_avg * (1.0 + float(account_pnl_ratio)))
        if account_mark > 0.0:
            account_ratio_mark_price = float(account_mark)

    account_unrealized_mark_price = None
    if account_unrealized_pnl is not None and account_qty > 0 and account_avg > 0.0:
        account_mark = account_avg + (account_unrealized_pnl / float(account_qty))
        if account_mark > 0.0:
            account_unrealized_mark_price = float(account_mark)
        notional = float(account_avg * float(account_qty))
        if notional > 0.0 and account_pnl_ratio is None:
            account_pnl_ratio = float(account_unrealized_pnl / notional)
            if not account_pnl_ratio_source:
                account_pnl_ratio_source = "account_unrealized_pnl"

    reference_price = 0.0
    if raw_price > 0.0:
        reference_price = float(raw_price)
    elif account_current_price is not None and account_current_price > 0.0:
        reference_price = float(account_current_price)
    return AccountPnlEvidence(account_current_price, account_pnl_ratio, account_pnl_ratio_source, account_ratio_mark_price, account_unrealized_mark_price, account_unrealized_pnl, reference_price)

def resolve_account_mark_price(_price_anomaly_reason, account_ratio_mark_price, account_unrealized_mark_price, raw_price):
    ratio_mark_anomaly_reason = _price_anomaly_reason(account_ratio_mark_price, source="account_pnl_ratio_mark")
    unrealized_mark_anomaly_reason = _price_anomaly_reason(
        account_unrealized_mark_price,
        source="account_unrealized_mark",
    )

    account_mark_price = None
    account_mark_price_source = ""
    price_anomaly_flag = False
    price_anomaly_reason = ""
    pnl_fallback_applied = False
    fallback_price_source = ""

    if account_ratio_mark_price is not None and not ratio_mark_anomaly_reason:
        account_mark_price = float(account_ratio_mark_price)
        account_mark_price_source = "account_pnl_ratio_mark"
    elif account_unrealized_mark_price is not None and not unrealized_mark_anomaly_reason:
        account_mark_price = float(account_unrealized_mark_price)
        account_mark_price_source = "account_unrealized_mark"
        if account_ratio_mark_price is not None and bool(ratio_mark_anomaly_reason):
            price_anomaly_flag = True
            price_anomaly_reason = str(ratio_mark_anomaly_reason)
            pnl_fallback_applied = True
            fallback_price_source = "account_unrealized_mark"
    elif account_ratio_mark_price is not None and bool(ratio_mark_anomaly_reason):
        price_anomaly_flag = True
        price_anomaly_reason = str(ratio_mark_anomaly_reason)
        pnl_fallback_applied = True
        fallback_price_source = "raw_price" if raw_price > 0.0 else "account_current_price"
    elif account_unrealized_mark_price is not None and bool(unrealized_mark_anomaly_reason):
        price_anomaly_flag = True
        price_anomaly_reason = str(unrealized_mark_anomaly_reason)
        pnl_fallback_applied = True
        fallback_price_source = "raw_price" if raw_price > 0.0 else "account_current_price"
    return AccountMarkPrice(account_mark_price, account_mark_price_source, fallback_price_source, pnl_fallback_applied, price_anomaly_flag, price_anomaly_reason)

def resolve_effective_price(account_mark_price, account_mark_price_source, account_pnl_ratio, fallback_price_source, pnl_fallback_applied, policy, raw_pnl_ratio, raw_price):
    effective_price = None
    effective_source = "unavailable"
    applied = False
    reason = "unavailable"

    if raw_price > 0.0:
        effective_price = float(raw_price)
        effective_source = "raw_price"
        reason = "raw_price_only"

    if account_mark_price is not None and account_mark_price > 0.0:
        if effective_price is None or effective_price <= 0.0:
            effective_price = float(account_mark_price)
            effective_source = str(account_mark_price_source or "account_unrealized_mark")
            applied = True
            reason = "account_mark_fallback" if not pnl_fallback_applied else f"price_anomaly_fallback:{effective_source}"
        elif str(policy.get("account_crosscheck_mode") or "conservative").strip().lower() == "conservative":
            if account_mark_price < effective_price - 1e-9:
                effective_price = float(account_mark_price)
                effective_source = str(account_mark_price_source or "account_unrealized_mark")
                applied = True
                if effective_source == "account_pnl_ratio_mark":
                    reason = "account_pnl_ratio_more_conservative"
                elif pnl_fallback_applied:
                    reason = f"price_anomaly_fallback:{effective_source}"
                else:
                    reason = "account_unrealized_pnl_more_conservative"
            elif raw_pnl_ratio is not None and account_pnl_ratio is not None:
                gap = float(account_pnl_ratio - raw_pnl_ratio)
                if abs(gap) <= 1e-6:
                    reason = "aligned"
                else:
                    reason = "account_mark_higher_than_raw_price"
    elif pnl_fallback_applied and effective_price is not None and effective_price > 0.0:
        effective_source = str(fallback_price_source or effective_source)
        reason = f"price_anomaly_fallback:{effective_source}"

    if (
        pnl_fallback_applied
        and account_mark_price is not None
        and effective_price is not None
        and abs(float(account_mark_price) - float(effective_price)) <= 1e-9
    ):
        effective_source = str(account_mark_price_source or effective_source)
        applied = True
        reason = f"price_anomaly_fallback:{effective_source}"
    return EffectivePriceResolution(applied, effective_price, effective_source, reason)
