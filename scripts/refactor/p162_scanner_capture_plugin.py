"""pytest plugin (T4-A fixture generator): records the INPUT state of `graphs.nodes.scanner_node.scanner_node` while an
existing offline suite runs. Offline only; used once on BASE to freeze scanner scenarios. Writes JSON lines to
$T4A_CAPTURE_OUT. The real call is untouched. Values that cannot be frozen (objects, callables) are replaced by an
`{"__opaque__": <type>}` marker: the replay re-injects a recording event logger for `event_logger` and treats other
opaque values as absent-equivalent markers (such records are flagged `opaque_paths`).

Usage: PYTHONPATH=scripts/refactor T4A_CAPTURE_OUT=out.jsonl pytest -p p162_scanner_capture_plugin <tests>
"""
from __future__ import annotations

import copy
import json
import os
from datetime import datetime
from pathlib import Path

_OUT = os.environ.get("T4A_CAPTURE_OUT", "")
_CURRENT = {"test": ""}


def _enc(o, path, opaque):
    if isinstance(o, dict):
        if all(isinstance(k, str) for k in o):
            return {k: _enc(v, f"{path}.{k}", opaque) for k, v in o.items()}
        return {"__dict_items__": [[_enc(k, path, opaque), _enc(v, path, opaque)] for k, v in o.items()]}
    if isinstance(o, list):
        return [_enc(x, f"{path}[]", opaque) for x in o]
    if isinstance(o, tuple):
        return {"__tuple__": [_enc(x, f"{path}()", opaque) for x in o]}
    if isinstance(o, (set, frozenset)):
        return {"__set__": [_enc(x, path, opaque) for x in sorted(o, key=repr)], "frozen": isinstance(o, frozenset)}
    if isinstance(o, Path):
        return {"__path__": str(o)}
    if isinstance(o, datetime):
        return {"__datetime__": o.isoformat()}
    if o is None or isinstance(o, (str, bool, int)):
        return o
    if isinstance(o, float):
        return o if o == o and o not in (float("inf"), float("-inf")) else {"__float__": repr(o)}
    opaque.append(path)
    return {"__opaque__": type(o).__name__}


def pytest_configure(config):
    if not _OUT:
        return
    import graphs.nodes.scanner_node as sn

    original = sn.scanner_node

    def wrapper(state, *a, **k):
        try:
            snap = copy.deepcopy(state)
            opaque = []
            enc = _enc(snap, "state", opaque)
            rec = {"test": _CURRENT["test"], "state": enc, "opaque_paths": opaque, "args": len(a), "kwargs": sorted(k)}
            with open(_OUT, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            pass
        return original(state, *a, **k)

    wrapper.__wrapped__ = original
    sn.scanner_node = wrapper


def pytest_runtest_setup(item):
    _CURRENT["test"] = item.nodeid
