from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from libs.reporting import baseline_candle_reader as _candle_reader


KST = timezone(timedelta(hours=9))


def _number(value: Any) -> float | None:
    return _candle_reader._number(value)


def _normalize_rows(value: Any, *, day: str = "") -> list[dict[str, Any]]:
    return _candle_reader._normalize_rows(value, day=day, _number_fn=_number)


def load_existing_candles(
    *,
    state_path: Path = Path("data/state.json"),
    day: str,
    symbols: tuple[str, ...],
    allow_fresh_fetch: bool = True,
    run_id_prefix: str = "baseline_samsung_hynix",
) -> dict[str, list[dict[str, Any]]]:
    return _candle_reader.load_existing_candles(
        state_path=state_path, day=day, symbols=symbols,
        allow_fresh_fetch=allow_fresh_fetch, run_id_prefix=run_id_prefix,
        _normalize_rows_fn=_normalize_rows,
    )


def load_market_change_pct(
    *,
    day: str,
    macro_root: Path = Path("data/logs/macro_indicators"),
) -> float | None:
    path = macro_root / day / "latest.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, Mapping):
        return None
    moves = payload.get("index_moves")
    moves = moves if isinstance(moves, Mapping) else {}
    return _number(moves.get("kospi_pct"))


def load_market_timeline(
    *,
    day: str,
    macro_root: Path = Path("data/logs/macro_indicators"),
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((macro_root / day).glob("*_macro_indicators.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, Mapping):
            continue
        try:
            epoch = int(
                datetime.fromisoformat(
                    str(payload.get("generated_at") or "").replace("Z", "+00:00")
                ).timestamp()
            )
        except Exception:
            continue
        moves = payload.get("index_moves")
        moves = moves if isinstance(moves, Mapping) else {}
        rows.append(
            {
                "ts": epoch,
                "kospi_pct": _number(moves.get("kospi_pct")),
                "source_path": str(path),
            }
        )
    deduped = {int(row["ts"]): row for row in rows if int(row["ts"]) > 0}
    return [deduped[epoch] for epoch in sorted(deduped)]


def market_snapshot_at(
    timeline: list[Mapping[str, Any]],
    *,
    epoch: int,
) -> dict[str, Any]:
    eligible = [dict(row) for row in timeline if int(row.get("ts") or 0) <= epoch]
    if not eligible:
        return {
            "available": False,
            "reason": "point_in_time_market_snapshot_missing",
            "snapshot_epoch": None,
            "snapshot_age_sec": None,
            "kospi_pct": None,
        }
    row = eligible[-1]
    source_epoch = int(row.get("ts") or 0)
    return {
        "available": True,
        "reason": "",
        "snapshot_epoch": source_epoch,
        "snapshot_age_sec": max(0, int(epoch) - source_epoch),
        "kospi_pct": _number(row.get("kospi_pct")),
        "source_path": str(row.get("source_path") or ""),
    }


def common_as_of_epoch(
    candles: Mapping[str, list[Mapping[str, Any]]],
    *,
    requested_epoch: int | None = None,
) -> int:
    if not candles or any(not rows for rows in candles.values()):
        return 0
    latest = [
        int(rows[-1].get("ts") or 0)
        for rows in candles.values()
        if rows and int(rows[-1].get("ts") or 0) > 0
    ]
    if not latest:
        return 0
    common = min(latest)
    return min(common, int(requested_epoch)) if requested_epoch else common
