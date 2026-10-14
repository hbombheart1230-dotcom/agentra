"""Pure value-normalisation helpers shared by the agent output builders and their projection stages.

T3.5: moved verbatim (AST-identical) from `libs/contracts/agent_outputs.py`, which re-exports the same names so every
existing reference keeps working. No I/O, clock, environment, logging or state; no dependency on the facade module.
"""
from __future__ import annotations

from typing import Any, Dict, List

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)

def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return int(default)

def _clip(value: Any, *, max_len: int = 280) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 3)] + "..."

def _listify(values: Any, *, limit: int = 8, max_len: int = 180) -> List[str]:
    if not isinstance(values, list):
        return []
    out: List[str] = []
    for value in values:
        text = _clip(value, max_len=max_len)
        if text:
            out.append(text)
        if len(out) >= limit:
            break
    return out

def _dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}

def _dict_list(value: Any, *, limit: int = 8) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: List[Dict[str, Any]] = []
    for row in value:
        if isinstance(row, dict):
            out.append(dict(row))
        if len(out) >= max(1, int(limit)):
            break
    return out

def _scanner_candidate_visibility_limit(scanner_output: Dict[str, Any]) -> int:
    policy = _dict(scanner_output.get("applied_scanner_policy"))
    entry_control = _dict(policy.get("entry_control"))
    raw = (
        entry_control.get("max_priority_rank")
        or policy.get("max_priority_rank")
        or scanner_output.get("max_priority_rank")
        or 5
    )
    return min(10, max(5, _safe_int(raw, 5)))

def _dedupe_text(values: List[str], *, limit: int = 10, max_len: int = 180) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for value in values:
        text = _clip(value, max_len=max_len)
        if not text or text in seen:
            continue
        out.append(text)
        seen.add(text)
        if len(out) >= max(1, int(limit)):
            break
    return out

def _format_trace_number(value: Any, *, digits: int = 3, missing: str = "not_captured") -> str:
    if value in (None, ""):
        return missing
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return _clip(value, max_len=24) or missing

def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True
