"""Reporter R8 (P15-WORK-003 follow-up): runtime BASE-vs-current parity for every R-8 READ_VIA_CALLBACK move.

For each R-8 moved function the pinned BASE body (exec'd against the LIVE facade globals) and the current facade wrapper
are called with identical arguments on a bounded temp-dir tree: path-like parameters receive a populated report tree, an
empty dir, a missing path and a file; other parameters receive a deterministic payload battery. Outcomes (JSON bytes or
exception type/message) must be equal, every file read through ``open``/``Path.read_text`` must be the same ordered list,
and the temp tree must be byte-identical afterwards (no writes)."""
import ast
import builtins
import importlib
import inspect
import json
import subprocess
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "d773709ba2f70471fad9badba4f92400f7818319"
LEDGER = ROOT / "docs/refactor/work_projects/evidence/reporter/r4_facade_ledger.json"
R8 = [(m["path"], m["name"]) for m in json.loads(LEDGER.read_text(encoding="utf-8"))["moves"][264:286]]


def _base_fn(path, name):
    src = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode("utf-8-sig")
    node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name)
    module = importlib.import_module(path[:-3].replace("/", "."))
    ns = dict(module.__dict__)
    exec(compile("from __future__ import annotations\n" + ast.get_source_segment(src, node), f"<base-{name}>", "exec"), ns)
    f = ns[name]
    ref = types.FunctionType(f.__code__, module.__dict__, name, f.__defaults__, f.__closure__)
    ref.__kwdefaults__ = f.__kwdefaults__
    return module, ref


def _tree(root):
    day = root / "2026-10-17"
    trade = day / "0930" / "TRD_20261017_005930_01"
    (trade / "reports").mkdir(parents=True)
    (trade / "lifecycle_bundle.json").write_text(json.dumps({"symbol": "005930", "lifecycle": {"entry": {"price": 1}},
                                                             "trade_lifecycle_status": "open"}), encoding="utf-8")
    (trade / "story_input.json").write_text('{"symbol": "005930", "trade_id": "TRD_20261017_005930_01"}', encoding="utf-8")
    (trade / "reports" / "broken.json").write_text("{not json", encoding="utf-8")
    (root / "events.jsonl").write_text('{"ts": "2026-10-17T01:00:00Z", "symbol": "005930"}\n{bad}\n', encoding="utf-8")
    return root


def _snapshot(root):
    return sorted((p.relative_to(root).as_posix(), p.read_bytes() if p.is_file() else b"<dir>") for p in root.rglob("*"))


def _is_pathlike(p):
    ann = str(p.annotation)
    return "Path" in ann or any(t in p.name for t in ("root", "dir", "path", "file"))


def _arg_sets(fn, tmp):
    sig = inspect.signature(fn)
    req = [p for p in sig.parameters.values() if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    kw = [p for p in sig.parameters.values() if p.default is p.empty and p.kind is p.KEYWORD_ONLY]
    out = []
    paths = [tmp, tmp / "2026-10-17", tmp / "missing", tmp / "events.jsonl"]
    payloads = [{}, {"symbol": "005930", "trade_id": "TRD_20261017_005930_01", "day": "2026-10-17"}, "005930", None]
    for i in range(4):
        def val(p, i=i):
            if "Callable" in str(p.annotation):
                return (lambda *a, **k: {}) if i % 2 == 0 else (lambda *a, **k: {"status": "ok"})
            return paths[i] if _is_pathlike(p) else payloads[i]
        out.append(([val(p) for p in req], {p.name: val(p) for p in kw}))
    return out


_ISO = __import__("re").compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:\+00:00|Z)?")


def _wallclock_normalized(text):
    """Only timestamps produced by the wall clock during this call (within 10 minutes of now) are normalised;
    fixture/input timestamps are compared verbatim."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    def sub(m):
        raw = m.group(0).replace("Z", "+00:00")
        try:
            ts = datetime.fromisoformat(raw)
        except ValueError:
            return m.group(0)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return "<WALLCLOCK>" if abs((now - ts).total_seconds()) < 600 else m.group(0)
    return _ISO.sub(sub, text)


def _run(fn, args, kwargs, monkeypatch):
    reads = []
    real_open, real_read_text = builtins.open, Path.read_text

    def spy_open(file, *a, **k):
        reads.append(("open", str(file)))
        return real_open(file, *a, **k)

    def spy_read_text(self, *a, **k):
        reads.append(("read_text", str(self)))
        return real_read_text(self, *a, **k)
    monkeypatch.setattr(builtins, "open", spy_open)
    monkeypatch.setattr(Path, "read_text", spy_read_text)
    try:
        try:
            res = ("ok", _wallclock_normalized(json.dumps(fn(*args, **kwargs), ensure_ascii=False, default=repr)))
        except Exception as exc:  # noqa: BLE001
            res = ("exc", type(exc).__name__, str(exc))
    finally:
        monkeypatch.setattr(builtins, "open", real_open)
        monkeypatch.setattr(Path, "read_text", real_read_text)
    return res, reads


def test_r8_set_is_the_22_recorded_moves():
    assert len(R8) == 22 and len(set(R8)) == 22


@pytest.mark.parametrize("path,name", R8)
def test_read_via_callback_move_is_runtime_base_equal(path, name, tmp_path, monkeypatch):
    module, ref = _base_fn(path, name)
    cur = getattr(module, name)
    root = _tree(tmp_path)
    before = _snapshot(root)
    for args, kwargs in _arg_sets(cur, root):
        got = _run(cur, args, kwargs, monkeypatch)
        want = _run(ref, args, kwargs, monkeypatch)
        assert got == want, (name, args)
    assert _snapshot(root) == before, "no writes"
