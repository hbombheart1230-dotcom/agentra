"""T3.5 deterministic freeze helpers for `libs/contracts/agent_outputs.py` (offline, no I/O, no network).

* `frozen_clock(module)`: swaps the module-level `datetime` name for a subclass whose `now()` is a constant, so every
  timestamp the builders derive from the clock is reproducible;
* `canonical(obj)`: canonical JSON text that PRESERVES dict insertion order (no `sort_keys`), so field order is part
  of the parity check;
* `encode` / `decode`: lossless tagged JSON encoding of the builder *inputs* (tuples, sets, Path, datetime), used by
  the golden fixtures.
"""
from __future__ import annotations

import contextlib
import json
from datetime import datetime, timezone
from pathlib import Path

FROZEN_BASE = datetime(2026, 10, 14, 12, 0, 0, 123456, tzinfo=timezone.utc)


class FrozenDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return FROZEN_BASE.astimezone(tz) if tz is not None else FROZEN_BASE.replace(tzinfo=None)


@contextlib.contextmanager
def frozen_clock(module):
    original = module.datetime
    module.datetime = FrozenDatetime
    try:
        yield
    finally:
        module.datetime = original


def canonical(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), default=_default)


def _default(o):
    if isinstance(o, (set, frozenset)):
        return {"__set__": sorted((repr(x) for x in o))}
    if isinstance(o, Path):
        return {"__path__": str(o)}
    if isinstance(o, datetime):
        return {"__datetime__": o.isoformat()}
    if isinstance(o, tuple):
        return list(o)
    return {"__repr__": repr(o)}


def encode(o):
    """Lossless tagged encoding (dict key order kept)."""
    if isinstance(o, dict):
        if all(isinstance(k, str) for k in o):
            return {k: encode(v) for k, v in o.items()}
        return {"__dict_items__": [[encode(k), encode(v)] for k, v in o.items()]}
    if isinstance(o, list):
        return [encode(x) for x in o]
    if isinstance(o, tuple):
        return {"__tuple__": [encode(x) for x in o]}
    if isinstance(o, (set, frozenset)):
        return {"__set__": [encode(x) for x in sorted(o, key=repr)], "frozen": isinstance(o, frozenset)}
    if isinstance(o, Path):
        return {"__path__": str(o)}
    if isinstance(o, datetime):
        return {"__datetime__": o.isoformat()}
    if o is None or isinstance(o, (str, bool, int)):
        return o
    if isinstance(o, float):
        if o != o or o in (float("inf"), float("-inf")):
            return {"__float__": repr(o)}
        return o
    raise TypeError(f"not freezable: {type(o).__name__}")


def decode(o):
    if isinstance(o, dict):
        if len(o) == 1 and "__dict_items__" in o:
            return {decode(k): decode(v) for k, v in o["__dict_items__"]}
        if len(o) == 1 and "__tuple__" in o:
            return tuple(decode(x) for x in o["__tuple__"])
        if "__set__" in o and set(o) <= {"__set__", "frozen"}:
            items = [decode(x) for x in o["__set__"]]
            return frozenset(items) if o.get("frozen") else set(items)
        if len(o) == 1 and "__path__" in o:
            return Path(o["__path__"])
        if len(o) == 1 and "__datetime__" in o:
            return datetime.fromisoformat(o["__datetime__"])
        if len(o) == 1 and "__float__" in o:
            return float(o["__float__"])
        return {k: decode(v) for k, v in o.items()}
    if isinstance(o, list):
        return [decode(x) for x in o]
    return o
