"""Monitor entry candidate: opening rank-1 probe observation price and selection context.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/monitor_node.py::_evaluate_monitor_entry_candidate` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class OpeningProbeContext(NamedTuple):
    """Result of `resolve_opening_probe_context` (positional order = sorted output names)."""

    observation_price: Any
    opening_probe_selection_authority: Any
    probe_selected: Any
    same_symbol_reentry_detected: Any

def resolve_opening_probe_context(_probe_minutes, allow_opening_rank1_controlled_probe, entry_rows, last_trade_epoch, last_trade_side, last_trade_symbol, now_epoch_for_entry, probe_day, quote_for_entry, selected, state, symbol, *, facade):
    last_trade_day = (
        facade._opening_probe_session_clock(last_trade_epoch)[0]
        if last_trade_epoch > 0
        else ""
    )
    same_symbol_reentry_detected = bool(
        last_trade_side == "SELL"
        and last_trade_symbol == symbol
        and last_trade_day == probe_day
    )
    opening_probe_selection_authority = facade.resolve_opening_rank1_probe_authority(
        state=state,
        selected=selected,
    )
    observation_price = {"observed_price": None, "price_source": "unavailable"}
    probe_selected = selected
    if bool(allow_opening_rank1_controlled_probe) and 0 <= _probe_minutes <= 20:
        from libs.runtime.opening_rank1_observation_price import resolve_observation_price

        observation_price = resolve_observation_price(
            selected=selected,
            quote=quote_for_entry,
            rows=entry_rows,
            now_epoch=now_epoch_for_entry,
        )
        observed_price = facade._to_float(observation_price.get("observed_price"))
        if observed_price > 0.0 and facade._to_float(selected.get("price")) <= 0.0:
            probe_selected = dict(selected)
            probe_selected["price"] = float(observed_price)
            probe_selected["_monitor_price_source"] = str(
                observation_price.get("price_source") or "opening_rank1_observation"
            )
    return OpeningProbeContext(observation_price, opening_probe_selection_authority, probe_selected, same_symbol_reentry_detected)
