from pathlib import Path
from typing import Any, Dict, Tuple


def _load_close_price_by_symbol(path: Path, *, day: str, facade: Any) -> Dict[str, float]:
    out: Dict[str, Tuple[str, float]] = {}
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = facade.csv.DictReader(f)
        for row in reader:
            symbol = str(row.get("symbol") or "").strip()
            if not symbol:
                continue
            ts = str(row.get("ts") or "").strip()
            d = facade._utc_day(ts)
            close = facade._safe_float(row.get("close"), default=0.0)
            if close <= 0.0:
                continue
            prev = out.get(symbol)
            if day:
                if d != day:
                    continue
                if prev is None or d >= prev[0]:
                    out[symbol] = (d, close)
            elif prev is None or d >= prev[0]:
                out[symbol] = (d, close)
    return {k: v[1] for k, v in out.items()}
