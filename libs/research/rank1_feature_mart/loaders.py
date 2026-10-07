from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from libs.research.opening_rank1_deep_dive.microstructure import load_minute_rows
from libs.research.opening_rank1_longitudinal.daily_provider import load_daily_cache, refresh_daily_cache
from libs.research.post_reclaim_alpha.kiwoom_history import KiwoomHistoricalMinuteReader


KST = timezone(timedelta(hours=9))


def read_json(path: Path) -> Any:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload


def iso_epoch(value: Any) -> int:
    try:
        return int(datetime.fromisoformat(str(value or "").replace("Z", "+00:00")).timestamp())
    except (TypeError, ValueError):
        return 0


def historical_episodes(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path)
    return [dict(row) for row in payload if isinstance(row, Mapping)] if isinstance(payload, list) else []


def prospective_episodes(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path)
    if not isinstance(payload, Mapping):
        return []
    return [dict(row) for row in payload.get("episodes") or [] if isinstance(row, Mapping)]


def longitudinal_events(path: Path) -> dict[str, dict[str, Any]]:
    payload = read_json(path)
    if not isinstance(payload, Mapping):
        return {}
    return {
        str(row.get("episode_id") or ""): dict(row)
        for row in payload.get("events") or []
        if isinstance(row, Mapping) and row.get("episode_id")
    }


_STREAM_CHUNK_CHARS = 4 * 1024 * 1024


def iter_json_array(path: Path, key: str):
    """Yield the items of the top-level array `key` of a JSON object file, one at a time.

    The q9 decision-window files reach ~130 MB; `json.loads` of one transiently needs
    ~860 MiB of Python objects, which alone overflows the 1 GiB container. This reads the
    file in chunks and decodes one array item at a time instead. It relies on the file
    being the indent=2 dump this repository writes (`"key": [` on its own top-level line)
    and falls back to a plain `json.loads` for any other layout. A truncated/corrupt file
    raises ValueError part-way; the caller discards what it collected, which matches the
    `read_json` -> `{}` behaviour (no windows at all) that this replaces.
    """
    marker = f'\n  "{key}": ['
    try:
        handle = path.open("r", encoding="utf-8")
    except OSError:
        return
    with handle:
        buffer = handle.read(_STREAM_CHUNK_CHARS)
        start = buffer.find(marker)
        if start < 0:
            try:
                payload = json.loads(buffer + handle.read())
            except ValueError:
                return
            for item in (payload.get(key) or []) if isinstance(payload, Mapping) else []:
                yield item
            return
        decoder = json.JSONDecoder()
        position = start + len(marker)
        exhausted = False
        while True:
            while True:
                while position < len(buffer) and buffer[position] in " \n\r\t,":
                    position += 1
                if position < len(buffer) or exhausted:
                    break
                chunk = handle.read(_STREAM_CHUNK_CHARS)
                if not chunk:
                    exhausted = True
                else:
                    buffer = buffer[position:] + chunk
                    position = 0
            if position >= len(buffer) or buffer[position] == "]":
                return
            while True:
                try:
                    item, end = decoder.raw_decode(buffer, position)
                    break
                except ValueError:
                    chunk = "" if exhausted else handle.read(_STREAM_CHUNK_CHARS)
                    if not chunk:
                        raise
                    buffer = buffer[position:] + chunk
                    position = 0
            yield item
            position = end
            if position > _STREAM_CHUNK_CHARS:
                buffer = buffer[position:]
                position = 0


def _project_window(enriched: dict[str, Any]) -> dict[str, Any]:
    """Keep only the q9-window fields `builder.build_episode` reads (see builder.py).

    Retaining every full window plus its canonical strategist/scanner documents for all
    ~290 historical episodes held ~410 MiB. Truthiness of `_canonical_scanner` is also
    observable (`canonical_scanner_present`), so a non-empty value that projects to
    nothing stays non-empty.
    """
    universe = enriched.get("scanner_pre_strategist_universe")
    scanner = enriched.get("_canonical_scanner")
    table = scanner.get("candidate_ranking_table") if isinstance(scanner, Mapping) else None
    projected: dict[str, Any] = {
        key: enriched[key]
        for key in ("decision_id", "run_id", "strategist_selection", "commander_final", "_canonical_strategist")
        if key in enriched
    }
    if "scanner_pre_strategist_universe" in enriched:
        projected["scanner_pre_strategist_universe"] = (
            {"intrinsic_ranked_top20": universe.get("intrinsic_ranked_top20")}
            if isinstance(universe, Mapping)
            else universe
        )
    if "_canonical_scanner" in enriched:
        projected["_canonical_scanner"] = (
            {"candidate_ranking_table": table}
            if isinstance(table, Mapping)
            else ({"_projected_non_empty": True} if scanner else scanner)
        )
    return projected


def q9_windows(
    reports_root: Path,
    episodes: list[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    wanted: dict[str, set[str]] = {}
    for row in episodes:
        day = str(row.get("day") or "")
        decision_id = str(row.get("decision_id") or "")
        if day and decision_id:
            wanted.setdefault(day, set()).add(decision_id)
    found: dict[str, dict[str, Any]] = {}
    for day, decision_ids in sorted(wanted.items()):
        windows_path = reports_root / "operator_summary" / "daily" / day / "q9_decision_windows.json"
        day_found: dict[str, dict[str, Any]] = {}
        try:
            for row in iter_json_array(windows_path, "windows"):
                if not isinstance(row, Mapping):
                    continue
                decision_id = str(row.get("decision_id") or "")
                if decision_id in decision_ids:
                    enriched = dict(row)
                    run_id = str(row.get("run_id") or "")
                    canonical_root = reports_root / "canonical" / day / run_id
                    enriched["_canonical_strategist"] = read_json(
                        canonical_root / "strategist.json"
                    )
                    enriched["_canonical_scanner"] = read_json(
                        canonical_root / "scanner.json"
                    )
                    day_found[decision_id] = _project_window(enriched)
        except ValueError:
            day_found = {}  # unreadable windows file == no windows for that day (as before)
        found.update(day_found)
    return found


def source_rows_for_symbol(
    *,
    symbol: str,
    minute_cache_root: Path,
    daily_cache_root: Path,
    additional_minute_cache_roots: tuple[Path, ...] = (),
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Merged minute rows and daily rows for ONE symbol (the per-symbol unit of `source_rows`).

    Loading every symbol up front held ~540 MiB (725k minute rows, copied during the merge);
    callers that process symbol by symbol keep only one symbol's rows alive.
    """
    only = {symbol}
    minute_sources = [load_minute_rows(minute_cache_root, only)]
    minute_sources.extend(load_minute_rows(root, only) for root in additional_minute_cache_roots)
    by_epoch = {
        int(row.get("ts") or 0): dict(row)
        for source in minute_sources
        for row in source.get(symbol, [])
        if int(row.get("ts") or 0) > 0
    }
    minutes = [by_epoch[key] for key in sorted(by_epoch)]
    daily_rows = load_daily_cache(daily_cache_root, only).get(symbol, [])
    derived = _daily_rows_from_minutes(minutes)
    by_day = {str(row.get("day") or _raw_day(row)): dict(row) for row in daily_rows}
    by_day.update({str(row["day"]): row for row in derived})
    return minutes, [by_day[key] for key in sorted(by_day) if key]


def source_rows(
    *,
    minute_cache_root: Path,
    daily_cache_root: Path,
    symbols: set[str],
    additional_minute_cache_roots: tuple[Path, ...] = (),
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    merged_minutes: dict[str, list[dict[str, Any]]] = {}
    daily: dict[str, list[dict[str, Any]]] = {}
    for symbol in sorted(symbols):
        merged_minutes[symbol], daily[symbol] = source_rows_for_symbol(
            symbol=symbol,
            minute_cache_root=minute_cache_root,
            daily_cache_root=daily_cache_root,
            additional_minute_cache_roots=additional_minute_cache_roots,
        )
    return merged_minutes, daily


def _raw_day(row: Mapping[str, Any]) -> str:
    raw = str(row.get("raw_ts") or "")
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}" if len(raw) >= 8 and raw[:8].isdigit() else ""


def _daily_rows_from_minutes(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        day = _raw_day(row)
        if day:
            grouped.setdefault(day, []).append(row)
    result = []
    for day, day_rows in sorted(grouped.items()):
        ordered = sorted(day_rows, key=lambda row: int(row.get("ts") or 0))
        closes = [float(row.get("close") or 0.0) for row in ordered if float(row.get("close") or 0.0) > 0.0]
        if not closes:
            continue
        result.append(
            {
                "day": day,
                "raw_ts": day.replace("-", "") + "152000",
                "ts": int(ordered[-1].get("ts") or 0),
                "open": float(ordered[0].get("open") or closes[0]),
                "high": max(float(row.get("high") or 0.0) for row in ordered),
                "low": min(float(row.get("low") or closes[0]) for row in ordered),
                "close": closes[-1],
                "volume": sum(float(row.get("volume") or 0.0) for row in ordered),
                "source": "derived_from_minute_cache",
            }
        )
    return result


def refresh_source_caches(
    *,
    minute_cache_root: Path,
    daily_cache_root: Path,
    symbols: set[str],
    refresh_from_day: str,
    base_day: str,
    max_pages: int = 8,
) -> dict[str, Any]:
    reader = KiwoomHistoricalMinuteReader.from_env()
    minimum_epoch = int(datetime.fromisoformat(refresh_from_day).replace(hour=9, tzinfo=KST).timestamp())
    existing = load_minute_rows(minute_cache_root, symbols)
    minute_meta: dict[str, Any] = {}
    minute_cache_root.mkdir(parents=True, exist_ok=True)
    for symbol in sorted(symbols):
        try:
            fetched, meta = reader.fetch_until(symbol=symbol, minimum_epoch=minimum_epoch, max_pages=max_pages)
            merged = {
                int(row.get("ts") or 0): dict(row)
                for row in [*existing.get(symbol, []), *fetched]
                if int(row.get("ts") or 0) > 0
            }
            rows = [merged[key] for key in sorted(merged)]
            (minute_cache_root / f"{symbol}.json").write_text(
                json.dumps(
                    {"schema_version": "kiwoom_historical_minute_cache.v1", "symbol": symbol, "row_count": len(rows), "rows": rows},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            minute_meta[symbol] = {**meta, "merged_row_count": len(rows)}
        except Exception as exc:
            minute_meta[symbol] = {"error": f"{type(exc).__name__}:{exc}"}
    daily_meta = refresh_daily_cache(cache_root=daily_cache_root, symbols=symbols, base_day=base_day)
    return {"refresh_from_day": refresh_from_day, "base_day": base_day, "minute": minute_meta, "daily": daily_meta}


def intrinsic_candidate(window: Mapping[str, Any], symbol: str) -> dict[str, Any]:
    universe = window.get("scanner_pre_strategist_universe")
    universe = universe if isinstance(universe, Mapping) else {}
    rows = [row for row in universe.get("intrinsic_ranked_top20") or [] if isinstance(row, Mapping)]
    normalized = str(symbol or "").zfill(6)
    match = next((row for row in rows if str(row.get("symbol") or "").zfill(6) == normalized), None)
    if match is None:
        match = next((row for row in rows if int(row.get("rank") or 0) == 1), None)
    return dict(match or {})


def canonical_scanner_candidate(
    window: Mapping[str, Any], symbol: str
) -> dict[str, Any]:
    scanner = window.get("_canonical_scanner")
    scanner = scanner if isinstance(scanner, Mapping) else {}
    table = scanner.get("candidate_ranking_table")
    table = table if isinstance(table, Mapping) else {}
    rows = [row for row in table.get("rows") or [] if isinstance(row, Mapping)]
    normalized = str(symbol or "").zfill(6)
    match = next(
        (
            row
            for row in rows
            if str(row.get("symbol") or "").zfill(6) == normalized
        ),
        None,
    )
    return dict(match or {})
