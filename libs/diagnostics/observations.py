"""Read-only broker-code and nearest-index numeric observations."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional


def broker_code_success(value: Any) -> Optional[bool]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        code = Decimal(s)
        return code.is_finite() and code == 0
    except (InvalidOperation, ValueError):
        pass
    t = s.lower()
    if t in ("ok", "success", "accepted"):
        return True
    if t in ("error", "failed", "rejected"):
        return False
    return False


def numeric_summary(values: List[float]) -> Dict[str, float]:
    vals = sorted(float(v) for v in values if float(v) >= 0.0)
    if not vals:
        return {"count": 0.0, "avg": 0.0, "p50": 0.0, "p95": 0.0, "max": 0.0}

    n = len(vals)

    def _pct(p: float) -> float:
        if n == 1:
            return float(vals[0])
        idx = int(round((n - 1) * p))
        idx = max(0, min(n - 1, idx))
        return float(vals[idx])

    return {
        "count": float(n),
        "avg": float(sum(vals) / float(n)),
        "p50": _pct(0.50),
        "p95": _pct(0.95),
        "max": float(vals[-1]),
    }
