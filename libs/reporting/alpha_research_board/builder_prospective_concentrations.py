"""``_prospective_concentrations`` moved verbatim from builder.py as ``prospective_concentrations``.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections import Counter


def prospective_concentrations(
    *, reports_root: Path, first_day: str, through_day: str,
    facade: Any,
) -> dict[str, dict[str, Any]]:
    daily_root = (
        reports_root
        / "evaluation"
        / "feature_mart"
        / "opening_rank1"
        / "prospective"
    )
    day_symbols: dict[str, set[tuple[str, str]]] = {}
    for path in sorted(daily_root.glob("20??-??-??/rank1_candidate_shadow_daily.json")):
        day = path.parent.name
        if day < first_day or day > through_day:
            continue
        payload, source = facade.load_json(path)
        if source.get("error"):
            continue
        for value in payload.get("observations") or []:
            row = facade.mapping(value)
            if not row.get("matched"):
                continue
            candidate_id = str(row.get("candidate_id") or "")
            symbol = str(row.get("symbol") or "")
            row_day = str(row.get("day") or day)
            if candidate_id and symbol:
                day_symbols.setdefault(candidate_id, set()).add((row_day, symbol))

    def _largest_key(counts: Counter[str]) -> str | None:
        """Return a reproducible mode: count descending, key ascending.

        ``Counter.most_common(1)`` preserves first-seen order for ties.  The
        source population above is accumulated in sets, whose iteration order
        intentionally varies between Python hash seeds, so it cannot define
        daily authority identity.
        """
        if not counts:
            return None
        return min(counts, key=lambda key: (-counts[key], key))

    result: dict[str, dict[str, Any]] = {}
    for candidate_id, pairs in day_symbols.items():
        days = facade.Counter(day for day, _symbol in pairs)
        symbols = facade.Counter(symbol for _day, symbol in pairs)
        count = len(pairs)
        result[candidate_id] = {
            "independent_day_symbol_count": count,
            "observed_day_count": len(days),
            "largest_day_share": round(max(days.values()) / count, 4) if count else None,
            "largest_symbol_share": round(max(symbols.values()) / count, 4) if count else None,
            "largest_day": _largest_key(days),
            "largest_symbol": _largest_key(symbols),
        }
    return result
