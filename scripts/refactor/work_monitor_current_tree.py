"""Exact current-tree contract for authorized continuous Monitor batches.

Not a discover/follow mechanism: only literal registered pairs are accepted.
No production module imports, no policy/effect execution, no shared gate edits.
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "d773709ba2f70471fad9badba4f92400f7818319"
WHOLE_MOVES = {
    "libs/runtime/monitor/entry_evidence.py": "libs/agents/monitor/projections/entry_evidence.py",
    "libs/runtime/monitor_exit/observability.py": "libs/agents/monitor/projections/observability.py",
    "libs/runtime/monitor_exit/order_lifecycle.py": "libs/agents/monitor/projections/order_lifecycle.py",
}


def base_source(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode("utf-8")


def shim_source(legacy, canonical):
    parent, name = canonical[:-3].replace("/", ".").rsplit(".", 1)
    if Path(legacy).stem != name:
        raise AssertionError("registered basename mismatch")
    return ("import sys as _sys\n"
            f"from {parent} import {name} as _canonical\n"
            "_sys.modules[__name__] = _canonical\n")


def strict_shim(source, legacy, canonical):
    if WHOLE_MOVES.get(legacy) != canonical:
        raise AssertionError("unregistered Monitor pair")
    try:
        body = ast.parse(source).body
    except SyntaxError as exc:
        raise AssertionError("invalid shim syntax") from exc
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    expected = ast.parse(shim_source(legacy, canonical)).body
    dump = lambda seq: ast.dump(ast.Module(body=seq, type_ignores=[]), include_attributes=False)
    if dump(body) != dump(expected):
        raise AssertionError("Monitor shim differs from exact three-statement contract")
    return canonical


def verified_current_source(path, *, source=None, owners=None):
    """Return baseline-equivalent implementation source, never import a shim.

    Own-role retained-source tests may follow these exact registered transfers,
    but still check all body bytes. Any extra shim statement or changed canonical
    body fails closed. All other paths remain completely byte-protected.
    """
    current = source if source is not None else (ROOT / path).read_text(encoding="utf-8")
    if path in WHOLE_MOVES:
        target = strict_shim(current, path, WHOLE_MOVES[path])
        actual = owners[target] if owners is not None and target in owners else (ROOT / target).read_text(encoding="utf-8")
    else:
        actual = current
    if actual != base_source(path):
        raise AssertionError(f"BASE implementation changed: {path}")
    return actual
