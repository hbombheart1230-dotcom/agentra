"""Shared baseline candle supply; compatibility facades may inject their local seams."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

KST = timezone(timedelta(hours=9))


def _number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_rows(
    value: Any, *, day: str = "", _number_fn: Callable[[Any], float | None] | None = None,
) -> list[dict[str, Any]]:
    number = _number if _number_fn is None else _number_fn
    raw_rows = value.get("rows") if isinstance(value, Mapping) else value
    if not isinstance(raw_rows, list):
        return []
    compact_day = day.replace("-", "")
    rows: list[dict[str, Any]] = []
    for raw in raw_rows:
        if not isinstance(raw, Mapping):
            continue
        ts = int(number(raw.get("ts")) or 0)
        close = number(raw.get("close") or raw.get("price"))
        if ts <= 0 or close is None or close <= 0:
            continue
        raw_ts = str(raw.get("raw_ts") or raw.get("datetime") or raw.get("time") or "")
        row_day = (
            raw_ts[:8]
            if len(raw_ts) >= 8 and raw_ts[:8].isdigit()
            else datetime.fromtimestamp(ts, tz=KST).strftime("%Y%m%d")
        )
        if compact_day and row_day != compact_day:
            continue
        volume = number(raw.get("volume"))
        rows.append(
            {
                "ts": ts,
                "raw_ts": raw_ts,
                "open": number(raw.get("open")) or close,
                "high": number(raw.get("high")) or close,
                "low": number(raw.get("low")) or close,
                "close": close,
                "volume": volume or 0.0,
            }
        )
    rows.sort(key=lambda row: int(row["ts"]))
    return rows


def load_existing_candles(
    *,
    state_path: Path = Path("data/state.json"),
    day: str,
    symbols: tuple[str, ...],
    allow_fresh_fetch: bool = True,
    run_id_prefix: str = "baseline_samsung_hynix",
    _normalize_rows_fn: Callable[..., list[dict[str, Any]]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    normalize_rows = _normalize_rows if _normalize_rows_fn is None else _normalize_rows_fn
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return {symbol: [] for symbol in symbols}
    if not isinstance(state, Mapping):
        return {symbol: [] for symbol in symbols}
    root: Mapping[str, Any] = {}
    for key in (
        "recent_minute_ohlcv_by_symbol",
        "minute_ohlcv_by_symbol",
        "monitor_minute_ohlcv_by_symbol",
        "intraday_ohlcv_by_symbol",
        "ohlcv_by_symbol",
    ):
        value = state.get(key)
        if isinstance(value, Mapping) and value:
            root = value
            break
    result = {
        symbol: normalize_rows(root.get(symbol), day=day)
        for symbol in symbols
    }
    if not allow_fresh_fetch:
        return result
    for symbol in symbols:
        for attempt in range(2):
            try:
                from libs.reporting.post_exit_shadow_recap import (
                    fetch_fresh_minute_rows_for_symbol,
                )

                fresh, _meta = fetch_fresh_minute_rows_for_symbol(
                    symbol,
                    run_id=(
                        f"{str(run_id_prefix or 'minute_ohlcv_recovery')}_"
                        f"{day}_{symbol}_{attempt + 1}"
                    ),
                )
                normalized = normalize_rows(fresh, day=day)
                existing = result.get(symbol) or []
                existing_latest = int(existing[-1].get("ts") or 0) if existing else 0
                fresh_latest = int(normalized[-1].get("ts") or 0) if normalized else 0
                if fresh_latest > existing_latest or (
                    fresh_latest == existing_latest and len(normalized) > len(existing)
                ):
                    result[symbol] = normalized
                if normalized:
                    break
            except Exception:
                if attempt == 1:
                    break
    return result


