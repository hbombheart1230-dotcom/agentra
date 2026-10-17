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
    life = root / "trades" / "2026-10-17" / "0930" / "TRD_20261017_005930_01" / "lifecycle"
    life.mkdir(parents=True)
    (life / "trade_lifecycle.json").write_text(json.dumps({
        "trade_id": "TRD_20261017_005930_01", "symbol": "005930", "day": "2026-10-17", "status": "closed",
        "input_timestamp": "2026-10-17T00:30:00+00:00",
        "entry": {"run_id": "e1"}, "exit": {"run_id": "x1"},
        "summary": {"entry_reason_human": "VWAP 돌파 확인", "exit_reason_human": "목표가 도달"}}, ensure_ascii=False), encoding="utf-8")
    (root / "trades" / "2026-10-17" / "carryover_exit_index.json").write_text(
        json.dumps({"rows": [{"trade_id": "TRD_20261016_000660_01", "symbol": "000660"}, "bad"]}), encoding="utf-8")
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
            if p.name == "day" or (p.name.endswith("_day") and "root" not in p.name):
                return ["2026-10-17", "", "2026-10-16", None][i]
            if p.name == "symbol":
                return ["005930", "", "000660", None][i]
            if "Callable" in str(p.annotation):
                return (lambda *a, **k: {}) if i % 2 == 0 else (lambda *a, **k: {"status": "ok"})
            return paths[i] if _is_pathlike(p) else payloads[i]
        out.append(([val(p) for p in req], {p.name: val(p) for p in kw}))
    return out


FROZEN = "2026-10-17T09:00:00+00:00"


class _FrozenDatetime(__import__("datetime").datetime):
    @classmethod
    def now(cls, tz=None):
        base = cls.fromisoformat(FROZEN)
        return base.astimezone(tz) if tz is not None else base.replace(tzinfo=None)

    @classmethod
    def utcnow(cls):
        return cls.fromisoformat(FROZEN).replace(tzinfo=None)


def _freeze_clock(monkeypatch):
    """P15-WORK-004: every loaded libs/graphs module attribute bound to ``datetime.datetime`` -> frozen subclass, so
    generated timestamps are deterministic and outputs are compared as RAW bytes (no timestamp normalisation)."""
    import datetime as _dt
    import sys
    for mod in list(sys.modules.values()):
        if getattr(mod, "__name__", "").startswith(("libs.", "graphs.")) and getattr(mod, "datetime", None) is _dt.datetime:
            monkeypatch.setattr(mod, "datetime", _FrozenDatetime)


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
            res = ("ok", json.dumps(fn(*args, **kwargs), ensure_ascii=False, default=repr))
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
    _freeze_clock(monkeypatch)
    root = _tree(tmp_path)
    before = _snapshot(root)
    results = []
    for args, kwargs in _arg_sets(cur, root):
        got = _run(cur, args, kwargs, monkeypatch)
        want = _run(ref, args, kwargs, monkeypatch)
        assert got == want, (name, args)
        results.append(got)
    assert _snapshot(root) == before, "no writes"
    if name in POSITIVE:  # the populated success branch must actually be exercised
        assert any(r[0][0] == "ok" and POSITIVE[name] in r[0][1] for r in results), (name, [r[0][:2] for r in results])


# readers whose populated success path is pinned by an expected token in the output
POSITIVE = {"build_daily_trade_index": "TRD_20261017_005930_01"}


def test_populated_daily_index_success_path_and_input_timestamp_sensitivity(tmp_path, monkeypatch):
    module, ref = _base_fn("libs/reporting/symbol_trade_report.py", "build_daily_trade_index")
    _freeze_clock(monkeypatch)
    root = _tree(tmp_path)
    out = module.build_daily_trade_index(root, "2026-10-17")
    assert [r["trade_id"] for r in out] == ["TRD_20261016_000660_01", "TRD_20261017_005930_01"]
    assert json.dumps(out, ensure_ascii=False) == json.dumps(ref(root, "2026-10-17"), ensure_ascii=False)
    # changing an input timestamp by one minute must change the compared bytes (no blanket normalisation)
    lc = next(root.rglob("trade_lifecycle.json"))
    data = json.loads(lc.read_text(encoding="utf-8"))
    outs = []
    for minute in ("31", "32"):
        data["summary"]["entry_reason_human"] = f"VWAP 돌파 확인 2026-10-17T00:{minute}:00+00:00"
        lc.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        outs.append(_run(module.build_daily_trade_index, [root, "2026-10-17"], {}, monkeypatch)[0])
    assert outs[0] != outs[1]


def test_frozen_clock_makes_generated_timestamps_byte_stable(tmp_path, monkeypatch):
    module, _ref = _base_fn("libs/reporting/post_exit_shadow_recap.py", "build_post_exit_shadow_recap")
    _freeze_clock(monkeypatch)
    root = _tree(tmp_path)
    oks = []
    for args, kwargs in _arg_sets(module.build_post_exit_shadow_recap, root):
        a = _run(module.build_post_exit_shadow_recap, args, kwargs, monkeypatch)[0]
        b = _run(module.build_post_exit_shadow_recap, args, kwargs, monkeypatch)[0]
        assert a == b
        if a[0] == "ok":
            oks.append(a[1])
    assert oks and any("2026-10-17T09:00:00" in o for o in oks), oks[:1]
