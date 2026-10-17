"""Reporter R8 (NEXT_READY2): real-output byte parity of moved Markdown/text renderers (BASE body vs current wrapper).

Covers every moved function (R-4..R-9 ledger) whose name marks it as a renderer (markdown / render / _md / lines / text /
label / summary). Both run against the LIVE facade globals with the same deterministic report-shaped payloads; outputs are
compared as exact UTF-8 bytes (strings/lists of strings) or JSON bytes, exceptions as type+message. Line endings inside the
produced text are compared byte-for-byte (no normalisation)."""
import ast
import importlib
import inspect
import json
import re
import subprocess
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "d773709ba2f70471fad9badba4f92400f7818319"
LEDGER = ROOT / "docs/refactor/work_projects/evidence/reporter/r4_facade_ledger.json"
RENDER = re.compile(r"(markdown|render|_md\b|_md_|lines|text|label|summary)")
MOVES = [(m["path"], m["name"]) for m in json.loads(LEDGER.read_text(encoding="utf-8"))["moves"] if RENDER.search(m["name"])]

PAYLOADS = [
    {},
    {"symbol": "005930", "symbol_name": "삼성전자", "trade_id": "TRD_1", "action": "BUY", "status": "ok",
     "summary": "진입 근거\r\n- VWAP 확인", "bullets": ["a", "b"], "pnl": 1200, "pnl_pct": 0.012,
     "lifecycle": {"entry": {"price": 81000, "ts": "2026-10-15T00:01:00Z"}, "exit": {"price": 82000}},
     "strategist": {"summary": "s", "confidence": 0.7}, "scanner": {"rank": 1, "score": 3.2},
     "memory": {"packets": [{"kind": "k", "text": "t"}]}, "market_context": {"summary": "bull", "vix_level": 19.4}},
    {"symbol": None, "summary": None, "bullets": "not-a-list", "pnl": "n/a", "lifecycle": []},
]


def _base_fn(path, name):
    src = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode("utf-8-sig")
    node = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name][-1]
    module = importlib.import_module(path[:-3].replace("/", "."))
    ns = dict(module.__dict__)
    exec(compile("from __future__ import annotations\n" + ast.get_source_segment(src, node), f"<base-{name}>", "exec"), ns)
    f = ns[name]
    ref = types.FunctionType(f.__code__, module.__dict__, name, f.__defaults__, f.__closure__)
    ref.__kwdefaults__ = f.__kwdefaults__
    return module, ref


def _bytes(value):
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, list) and all(isinstance(x, str) for x in value):
        return "\x00".join(value).encode("utf-8")
    return json.dumps(value, ensure_ascii=False, default=repr).encode("utf-8")


def _outcome(fn, args, kwargs):
    try:
        return ("ok", _bytes(fn(*args, **kwargs)))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


def _calls(fn):
    sig = inspect.signature(fn)
    req = [p for p in sig.parameters.values() if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    kw = [p for p in sig.parameters.values() if p.default is p.empty and p.kind is p.KEYWORD_ONLY]
    out = []
    for pl in PAYLOADS:
        def val(p, pl=pl):
            if "Callable" in str(p.annotation):
                return lambda *a, **k: str(a[0]) if a else ""
            return json.loads(json.dumps(pl))
        out.append(([val(p) for p in req], {p.name: val(p) for p in kw}))
    return out


def test_renderer_selection_is_not_empty():
    assert len(MOVES) >= 20


@pytest.mark.parametrize("path,name", MOVES)
def test_moved_renderer_output_bytes_equal_base(path, name):
    module, ref = _base_fn(path, name)
    cur = getattr(module, name)
    for args, kwargs in _calls(cur):
        assert _outcome(cur, args, kwargs) == _outcome(ref, args, kwargs), (name, args)
