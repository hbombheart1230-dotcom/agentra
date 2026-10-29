from __future__ import annotations

import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from .collector_observations import collector_raw_row_impl
from .contracts import CHECKPOINTS, TARGETS
from .index_timeline import load_index_timeline_impl
from .stock_reaction import stock_reaction_impl
from libs.market.q10_observation_integrity import market_epoch


KST = timezone(timedelta(hours=9))


def _number(value: Any) -> float | None:
    try:
        return None if value in (None, "") else float(value)
    except (TypeError, ValueError):
        return None


def _pct(current: float | None, base: float | None) -> float | None:
    if current is None or base in (None, 0.0):
        return None
    return round((current / base - 1.0) * 100.0, 6)


def _checkpoint_epoch(day: str, label: str) -> int:
    parsed = time(15, 30) if label == "CLOSE" else time.fromisoformat(label)
    return int(datetime.combine(date.fromisoformat(day), parsed, tzinfo=KST).timestamp())


def _point_at(rows: list[Mapping[str, Any]], epoch: int, max_lag_sec: int) -> dict[str, Any] | None:
    candidate = next((row for row in rows if int(row.get("ts") or 0) >= epoch), None)
    if candidate is None or int(candidate.get("ts") or 0) - epoch > max_lag_sec:
        return None
    return dict(candidate)


def _opening_point(rows: list[Mapping[str, Any]], day: str) -> dict[str, Any] | None:
    """Return the first traded candle, never a zero-volume opening placeholder."""
    opening_epoch = _checkpoint_epoch(day, "09:00")
    latest_epoch = _checkpoint_epoch(day, "09:03")
    for row in rows:
        row_epoch = int(row.get("ts") or 0)
        if row_epoch < opening_epoch or row_epoch > latest_epoch:
            continue
        volume = _number(row.get("volume"))
        open_price = _number(row.get("open"))
        if volume is not None and volume > 0.0 and open_price is not None and open_price > 0.0:
            return dict(row)
    return None


def _close_point(rows: list[Mapping[str, Any]], day: str) -> dict[str, Any] | None:
    close_epoch = _checkpoint_epoch(day, "CLOSE")
    auction_start = close_epoch - 10 * 60
    eligible = [row for row in rows if auction_start <= int(row.get("ts") or 0) <= close_epoch + 60]
    return dict(eligible[-1]) if eligible else None


def _last_available_point_before_close(
    rows: list[Mapping[str, Any]], day: str, *, max_lookback_sec: int
) -> dict[str, Any] | None:
    """2026-09-03 daily audit (P2-A, revised): informational-only lookup of
    the most recent data point actually observed before the close
    checkpoint, for use ONLY when `_close_point` found nothing in the real
    close window. This value is NEVER written into `points["CLOSE"]`,
    never used for `return_from_previous_close_pct`, `forward_windows`, or
    any other Q10 reaction/scoring calculation -- it exists purely so a
    report reader can see "the last thing we actually observed was X, Y
    seconds before close" without that value ever being mistaken for a
    verified close print. Root cause: KOSPI/KOSDAQ macro-indicator
    snapshots are a byproduct of the Strategist node's own
    global_sentiment_breakdown cycle (compute_global_sentiment_signal),
    not a dedicated, independently-schedulable capture job -- there is no
    existing safe path to force one specifically at 15:30 KST close
    (confirmed: libs/market/opening_macro_snapshot_collector.py's own
    scheduled slots are hard-capped to the 08:50-09:20 preopen window by
    design, unrelated to this gap)."""
    close_epoch = _checkpoint_epoch(day, "CLOSE")
    prior = [row for row in rows if int(row.get("ts") or 0) <= close_epoch + 60]
    if not prior:
        return None
    candidate = prior[-1]
    lag = close_epoch - int(candidate.get("ts") or 0)
    if lag < 0 or lag > max_lookback_sec:
        return None
    return {
        "ts": int(candidate.get("ts") or 0),
        "price": _number(candidate.get("close")),
        "lag_sec": int(lag),
    }


def _forward_window(
    rows: list[Mapping[str, Any]], *, entry_ts: int, entry_price: float | None,
    authoritative_close: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """2026-09-05 PRE-STEP5C CLEANUP FIX 3 (item 2, second independent
    Codex re-audit): `return_to_close_pct` used to always come from
    `rows` (the legacy candle series) regardless of what `points["CLOSE"]`
    actually displayed -- so when a governed checkpoint's CLOSE came from
    the Q10 collector override (a different value than the legacy
    series's own last row), the displayed CLOSE and the calculated
    return_to_close_pct silently used two different close prices (Codex's
    exact fixture: OPEN=100, collector CLOSE=110 displayed, but
    return_to_close_pct computed from legacy's last price 90). Passing
    `authoritative_close` (points["CLOSE"], the SAME dict every consumer
    displays) makes this function use the identical value -- one
    authoritative observation set feeding both display and calculation, as
    required. Falls back to the legacy `rows`-derived last price exactly
    as before whenever no authoritative close is available (CLOSE still
    PENDING) or it predates `entry_ts`."""
    if entry_price in (None, 0.0):
        return {"status": "PENDING", "return_to_close_pct": None, "mfe_pct": None, "mae_pct": None}
    future = [row for row in rows if int(row.get("ts") or 0) >= entry_ts]
    prices = [_number(row.get("close")) for row in future]
    prices = [value for value in prices if value is not None]

    close_price = None
    if isinstance(authoritative_close, Mapping):
        candidate_price = _number(authoritative_close.get("price"))
        candidate_ts = int(authoritative_close.get("ts") or 0)
        if candidate_price is not None and candidate_ts >= entry_ts:
            close_price = candidate_price
            if close_price not in prices:
                prices = [*prices, close_price]

    if not prices:
        return {"status": "PENDING", "return_to_close_pct": None, "mfe_pct": None, "mae_pct": None}
    return_reference = close_price if close_price is not None else prices[-1]
    return {
        "status": "OBSERVED",
        "return_to_close_pct": _pct(return_reference, entry_price),
        "mfe_pct": _pct(max(prices), entry_price),
        "mae_pct": _pct(min(prices), entry_price),
    }


def _stock_reaction(
    *,
    day: str,
    target: Mapping[str, Any],
    rows: list[Mapping[str, Any]],
    previous_close: float | None,
    last_available_lookback_sec: int = 0,
    collector_override: Any = None,
) -> dict[str, Any]:
    return stock_reaction_impl(
        day=day,
        target=target,
        rows=rows,
        previous_close=previous_close,
        last_available_lookback_sec=last_available_lookback_sec,
        collector_override=collector_override,
        facade=sys.modules[__name__],
    )
def load_index_timeline(*, day: str, macro_root: Path, index_name: str) -> list[dict[str, Any]]:
    return load_index_timeline_impl(day=day, macro_root=macro_root, index_name=index_name, facade=sys.modules[__name__])

_INDEX_LAST_AVAILABLE_LOOKBACK_SEC = 30 * 60
"""2026-09-03 daily audit (P2-A, revised): bounded lookback for the
index-only `last_available_point_before_close` informational field --
covers the observed ~15.5 minute gap (last snapshot 15:15:32 KST vs.
close 15:30 KST) with margin. This value is NEVER written into
points["CLOSE"]; it only bounds how far back the informational lookup is
allowed to reach before giving up entirely."""


_COLLECTOR_GOVERNED_CHECKPOINTS = frozenset({"09:30", "10:00", "CLOSE"})


# 2026-09-05 PRE-STEP5C CLEANUP FIX 3 (item 2/6, second independent Codex
# re-audit): FIX 2's `_collector_raw_row` only ever returned a usable
# point or None -- meaning ANY non-usable collector state (LATE_MISSED,
# CORRUPT_STATE, or an unverified-but-captured observation) silently fell
# through to the legacy macro-timeline fallback, exactly as if the
# collector had genuinely captured nothing at all. That hides a proven
# integrity problem behind an apparently-normal legacy value. Per item 6:
# ABSENT (collector genuinely never captured anything for this slot) is
# NOT the same thing as INVALID (collector captured something but proved
# it untrustworthy) -- only ABSENT may fall back to legacy.
#
# `_collector_raw_row` now returns a tri-state signal:
#   None                              -> ABSENT (never attempted / MISSING)
#                                         -> legacy fallback allowed, unchanged
#   {"integrity_failure": True, ...}  -> INVALID (LATE_MISSED / CORRUPT_STATE /
#                                         ATTEMPT_INCOMPLETE / an unverified-
#                                         but-captured observation, per item 1
#                                         these are never calculation-usable)
#                                         -> legacy fallback FORBIDDEN; the
#                                         checkpoint is forced PENDING with the
#                                         integrity failure reason attached
#   {"ts": ..., "close": ..., ...}    -> VERIFIED (collector's AVAILABLE/
#                                         PARTIAL, evidence-backed -- see
#                                         q10_index_observation_collector.py's
#                                         _has_verification_evidence) -> used
#                                         directly, authoritative
_COLLECTOR_ABSENT_STATES = frozenset({"MISSING"})
_COLLECTOR_VERIFIED_STATES = frozenset({"AVAILABLE", "PARTIAL"})


def _collector_raw_row(
    *, day: str, index_name: str, slot: str, root: Path | str | None,
) -> dict[str, Any] | None:
    return collector_raw_row_impl(day=day, index_name=index_name, slot=slot, root=root, facade=sys.modules[__name__])

def _index_reaction(
    *, day: str, target: Mapping[str, Any], rows: list[Mapping[str, Any]],
    collector_root: Path | str | None = None,
) -> dict[str, Any]:
    previous_close = next((_number(row.get("previous_close")) for row in rows if _number(row.get("previous_close")) is not None), None)
    index_name = str(target.get("symbol") or "")

    def _override(label: str) -> dict[str, Any] | None:
        if label not in _COLLECTOR_GOVERNED_CHECKPOINTS:
            return None
        slot = "15:30" if label == "CLOSE" else label
        return _collector_raw_row(day=day, index_name=index_name, slot=slot, root=collector_root)

    result = _stock_reaction(
        day=day,
        target=target,
        rows=rows,
        previous_close=previous_close,
        last_available_lookback_sec=_INDEX_LAST_AVAILABLE_LOOKBACK_SEC,
        collector_override=_override,
    )
    result["source"] = "kiwoom_ka20009_macro_snapshots"
    return result


def build_actual_reactions(
    *, day: str, candle_map: Mapping[str, list[Mapping[str, Any]]], macro_root: Path, signal_inputs: Mapping[str, Any],
    collector_root: Path | str | None = None,
) -> dict[str, Any]:
    reactions: dict[str, Any] = {}
    for target in TARGETS:
        key = str(target["key"])
        if target["kind"] == "stock":
            previous_key = "hynix_previous_close" if key == "sk_hynix" else f"{key}_previous_close"
            reactions[key] = _stock_reaction(
                day=day,
                target=target,
                rows=list(candle_map.get(str(target["symbol"])) or []),
                previous_close=_number(signal_inputs.get(previous_key)),
            )
        else:
            reactions[key] = _index_reaction(
                day=day,
                target=target,
                rows=load_index_timeline(day=day, macro_root=macro_root, index_name=str(target["symbol"])),
                collector_root=collector_root,
            )
    return {"day": day, "targets": reactions}
