"""Reporter R8 (P15-WORK-003): READ_VIA_CALLBACK functions moved in R-8 keep their BASE read/error/order behavior.

The moved bodies have no direct I/O; they read through late-bound facade helpers (``facade._iter_jsonl``) or an injected
``read_json`` callback. Here the pinned BASE function (exec'd from the BASE blob against the LIVE facade globals) and the
current facade wrapper are run on identical bounded temp-dir inputs: valid / missing / malformed / empty files, and
callback results {} / dict / raising. Return value, exception type+message, read paths and callback order must match, and a
mid-call re-patch of the facade helper must be honoured identically.
"""
import ast
import importlib
import json
import subprocess
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "d773709ba2f70471fad9badba4f92400f7818319"


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


def _outcome(fn, *a, **k):
    try:
        return ("ok", json.dumps(fn(*a, **k), ensure_ascii=False, sort_keys=False, default=repr))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


def _jsonl_cases(tmp):
    good = tmp / "good.jsonl"
    good.write_text('{"ts": "2026-10-15T01:00:00Z"}\n{"ts": "2026-10-16T23:59:00+09:00"}\n\n{"ts": 5}\n', encoding="utf-8")
    bad = tmp / "bad.jsonl"
    bad.write_text('{not json}\n{"ts": "2026-10-14T00:00:00Z"}\n[1,2]\n"str"\n', encoding="utf-8")
    empty = tmp / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    crlf = tmp / "crlf.jsonl"
    crlf.write_bytes(b'{"ts": "2026-10-13T00:00:00Z"}\r\n{"ts": "bad-ts"}\r\n')
    return [good, bad, empty, crlf, tmp / "missing.jsonl", tmp]


@pytest.mark.parametrize("path", ["libs/reporting/reporter_analysis.py", "libs/reporting/trade_explain.py"])
def test_latest_day_reads_via_facade_iter_jsonl_identically(path, tmp_path, monkeypatch):
    module, ref = _base_fn(path, "_latest_day")
    for case in _jsonl_cases(tmp_path):
        assert _outcome(module._latest_day, case) == _outcome(ref, case), case.name
    # read path + order through the late-bound helper, and a mid-call re-patch
    for fn in (module._latest_day, ref):
        seen = []
        original = module._iter_jsonl

        def spy(p, _orig=original):
            seen.append(Path(p).name)
            return _orig(p)
        monkeypatch.setattr(module, "_iter_jsonl", spy)
        fn(tmp_path / "good.jsonl")
        assert seen == ["good.jsonl"]
        monkeypatch.setattr(module, "_iter_jsonl", original)
    calls = {}
    for label, fn in (("cur", module._latest_day), ("base", ref)):
        log = []

        def utc_day(value, _log=log):
            _log.append(("utc", value))
            if len(_log) == 1:  # mid-call: re-patch the helper used for the remaining rows
                monkeypatch.setattr(module, "_utc_day", lambda v, _l=_log: (_l.append(("v2", v)), "2099-01-01")[1])
            return "2000-01-01"
        monkeypatch.setattr(module, "_utc_day", utc_day)
        result = fn(tmp_path / "good.jsonl")
        calls[label] = (result, log)
    assert calls["cur"] == calls["base"]


def test_load_reporter_snippet_for_run_callback_contract_is_base_equal(tmp_path):
    path = "libs/reporting/trade_read_model.py"
    module, ref = _base_fn(path, "load_reporter_snippet_for_run")
    report = {"decision_trace_chain_summary": {"chains": [{"run_id": "r1", "summary": "s"}, {"run_id": "r2"}]},
              "ai_summary": "x", "ai_run_grade": "B"}
    behaviours = {
        "missing": lambda p: {},
        "dict": lambda p: report,
        "no_chains": lambda p: {"ai_summary": "only"},
        "raises": lambda p: (_ for _ in ()).throw(ValueError("broken json")),
        "non_dict_chain": lambda p: {"decision_trace_chain_summary": "bad"},
    }
    for label, cb in behaviours.items():
        for run_id in ("r1", "r9", ""):
            got_calls, ref_calls = [], []

            def rec(log, f):
                return lambda p: (log.append(Path(p).as_posix()), f(p))[1]
            a = _outcome(module.load_reporter_snippet_for_run, tmp_path, run_id, "2026-10-17", read_json=rec(got_calls, cb))
            b = _outcome(ref, tmp_path, run_id, "2026-10-17", read_json=rec(ref_calls, cb))
            assert a == b, (label, run_id)
            assert got_calls == ref_calls, (label, run_id)
