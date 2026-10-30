from __future__ import annotations
from typing import Any, Dict, List, Tuple


def _parse_case(raw: str, facade=None) -> Dict[str, str]:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    parts = [str(part or "").strip() for part in str(raw or "").split(":")]
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError(f"invalid case spec: {raw}")
    return {
        "day": parts[0],
        "trade_id": parts[1],
        "target_run_id": parts[2] if len(parts) >= 3 else "",
    }


def _normalize_cases(values: List[str], facade=None) -> List[Dict[str, str]]:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    if not values:
        return [{"day": day, "trade_id": trade_id, "target_run_id": ""} for day, trade_id in DEFAULT_GOLDEN_CASES]
    out: List[Dict[str, str]] = []
    seen: set[Tuple[str, str]] = set()
    for raw in values:
        case = _parse_case(raw)
        key = (case["day"], case["trade_id"])
        if key in seen:
            continue
        out.append(case)
        seen.add(key)
    return out
