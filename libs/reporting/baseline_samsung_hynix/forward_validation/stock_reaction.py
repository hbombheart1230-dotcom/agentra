"""Stock/index reaction calculation Owner (moved from reaction_reader._stock_reaction).

``facade`` is the ``reaction_reader`` module; helpers are resolved on it at call time so monkeypatching the
facade keeps working.
"""
from __future__ import annotations

from typing import Any, Mapping


def stock_reaction_impl(
    *,
    day: str,
    target: Mapping[str, Any],
    rows: list[Mapping[str, Any]],
    previous_close: float | None,
    last_available_lookback_sec: int = 0,
    collector_override: Any = None,
    facade: Any,
) -> dict[str, Any]:
    valid = sorted(
        (dict(row) for row in rows if int(row.get("ts") or 0) > 0 and facade._number(row.get("close")) is not None),
        key=lambda row: int(row["ts"]),
    )
    points: dict[str, Any] = {}
    for label in facade.CHECKPOINTS:
        # 2026-09-05 PRE-STEP5C FIX 2/FIX 3 (item 2/6): the dedicated Q10
        # index observation collector (libs/market/q10_index_observation_
        # collector.py) is the AUTHORITATIVE source for the 09:30/10:00/
        # CLOSE checkpoints when it has a genuinely evidence-VERIFIED
        # observation. `collector_override(label)` returns a tri-state
        # signal: None (ABSENT -- collector never captured anything for
        # this checkpoint; falls through to the legacy-timeline logic
        # below, completely unchanged), a dict with `integrity_failure`
        # (INVALID -- the collector captured something but proved it not
        # calculation-usable, e.g. LATE_MISSED/CORRUPT_STATE/an unverified-
        # time observation; legacy fallback is FORBIDDEN here -- silently
        # substituting a legacy value would hide a proven integrity
        # problem), or a plain raw-row dict (VERIFIED -- used directly,
        # exactly as before). Historical days with no collector data (and
        # all stock targets, which never pass collector_override) behave
        # byte-for-byte as before.
        override_point = collector_override(label) if collector_override else None
        integrity_failure = isinstance(override_point, Mapping) and bool(override_point.get("integrity_failure"))
        if integrity_failure:
            point = None
        elif override_point is not None:
            point = override_point
        elif label == "09:00":
            point = facade._opening_point(valid, day)
        elif label == "CLOSE":
            point = facade._close_point(valid, day)
        else:
            point = facade._point_at(valid, facade._checkpoint_epoch(day, label), 90)
        price_field = "open" if label == "09:00" else "close"
        if point:
            points[label] = {
                "status": "OBSERVED",
                "ts": int(point["ts"]),
                "price": facade._number(point.get(price_field)),
                "volume": facade._number(point.get("volume")),
                "return_from_previous_close_pct": facade._pct(facade._number(point.get(price_field)), previous_close),
                # Additive provenance, present only when this point came
                # from the Q10 index collector override above -- never
                # required by, or breaking, any existing consumer.
                **({"source": point["source"], "capture_status": point.get("capture_status")} if "source" in point else {}),
            }
        elif integrity_failure:
            # item 6: INVALID, never silently treated as ABSENT. Still
            # PENDING for calculation purposes (no return/forward-window
            # math uses it), but carries the reason so the failure is
            # visible rather than hidden behind an ordinary legacy PENDING.
            points[label] = {
                "status": "PENDING",
                "price": None,
                "volume": None,
                "integrity_failure": True,
                "integrity_reason": override_point.get("reason"),
                "collector_status": override_point.get("collector_status"),
                "unverified_observation": override_point.get("unverified_observation"),
            }
        else:
            points[label] = {"status": "PENDING", "price": None, "volume": None}
    # 2026-09-03 daily audit (P2-A, revised): when CLOSE has no real
    # close-window data, surface the last actually-observed point as a
    # SEPARATE, additive, clearly-labeled field -- never as the CLOSE
    # value itself, and never fed into return/forward-window math. Only
    # computed when a caller opts in (last_available_lookback_sec > 0,
    # currently only _index_reaction); stocks are unaffected.
    last_available_point_before_close = None
    if points["CLOSE"]["status"] != "OBSERVED" and last_available_lookback_sec > 0:
        last_available_point_before_close = facade._last_available_point_before_close(
            valid, day, max_lookback_sec=last_available_lookback_sec
        )
    regular = [
        row for row in valid
        if facade._checkpoint_epoch(day, "09:00") <= int(row["ts"]) <= facade._checkpoint_epoch(day, "CLOSE") + 300
    ]
    highs = [facade._number(row.get("high")) for row in regular]
    lows = [facade._number(row.get("low")) for row in regular]
    highs = [value for value in highs if value is not None]
    lows = [value for value in lows if value is not None]
    open_price = (points.get("09:00") or {}).get("price")
    # item 2: pass the SAME authoritative CLOSE point every display
    # consumer sees, so return_to_close_pct/mfe/mae can never silently
    # diverge from what points["CLOSE"] itself shows.
    authoritative_close = points.get("CLOSE") if (points.get("CLOSE") or {}).get("status") == "OBSERVED" else None
    forward_windows = {
        label: facade._forward_window(
            regular,
            entry_ts=int((points.get(label) or {}).get("ts") or 0),
            entry_price=facade._number((points.get(label) or {}).get("price")),
            authoritative_close=authoritative_close,
        )
        for label in facade.CHECKPOINTS[:-1]
    }
    if (points.get("CLOSE") or {}).get("status") != "OBSERVED":
        for window in forward_windows.values():
            if window.get("status") == "OBSERVED":
                window["status"] = "PARTIAL"
                window["return_to_close_pct"] = None
    return {
        "target": dict(target),
        "source": "q10_current_day_minute_candles",
        "previous_close": previous_close,
        "opening_gap_pct": facade._pct(facade._number(open_price), previous_close),
        "points": points,
        "forward_windows": forward_windows,
        "day_high": max(highs) if highs else None,
        "day_low": min(lows) if lows else None,
        "day_high_return_pct": facade._pct(max(highs), previous_close) if highs else None,
        "day_low_return_pct": facade._pct(min(lows), previous_close) if lows else None,
        "evidence_status": "AVAILABLE" if open_price is not None else "INSUFFICIENT_EVIDENCE",
        "actual_open_policy": "first_positive_volume_candle_0900_to_0903",
        "path": regular,
        # 2026-09-03 daily audit (P2-A, revised): informational only --
        # never a substitute CLOSE value. See facade._last_available_point_before_close.
        "last_available_point_before_close": last_available_point_before_close,
    }


