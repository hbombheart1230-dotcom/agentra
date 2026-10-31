"""post_exit_shadow_recap projections (moved verbatim from post_exit_shadow_recap).

Module globals and helpers are resolved on ``facade`` (the post_exit_shadow_recap module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def opening_rank1_eod_fallback_row(
    *, reports_root: Path, day: str, symbol: str,
    facade: Any,
) -> tuple[Dict[str, Any] | None, Dict[str, Any]]:
    path = (
        facade.Path(reports_root)
        / "evaluation"
        / "opening_rank1_shadow"
        / str(day)
        / "opening_rank1_shadow_daily.json"
    )
    payload = facade._read_json(path)
    normalized = facade.normalize_symbol(symbol or "", allow_test_symbols=True)
    for raw in payload.get("episodes") or []:
        episode = facade._as_dict(raw)
        if facade.normalize_symbol(episode.get("symbol") or "", allow_test_symbols=True) != normalized:
            continue
        eod = facade._as_dict(facade._as_dict(episode.get("checkpoints")).get("EOD"))
        if str(eod.get("status") or "").strip().lower() != "observed":
            continue
        price = eod.get("price") if eod.get("price") not in (None, "") else eod.get("observed_price")
        try:
            close = float(price)
        except Exception:
            continue
        observed_epoch = facade._epoch_seconds(eod.get("observed_epoch") or eod.get("observed_ts"))
        if observed_epoch is None:
            try:
                observed_epoch = facade.datetime.fromisoformat(str(day)).replace(
                    hour=15, minute=30, tzinfo=facade.KST
                ).timestamp()
            except Exception:
                continue
        observed_kst = facade.datetime.fromtimestamp(observed_epoch, tz=facade.timezone.utc).astimezone(facade.KST)
        row = {
            "ts": int(observed_epoch),
            "raw_ts": observed_kst.strftime("%Y%m%d%H%M%S"),
            "open": close,
            "high": close,
            "low": close,
            "close": close,
            "volume": eod.get("volume"),
            "source": "opening_rank1_shadow.EOD",
            "eod_fallback": True,
        }
        return row, {
            "applied": True,
            "source": "opening_rank1_shadow.EOD",
            "source_path": str(path),
        }
    return None, {
        "applied": False,
        "reason": "matching_observed_opening_rank1_eod_not_found",
        "source_path": str(path),
    }
