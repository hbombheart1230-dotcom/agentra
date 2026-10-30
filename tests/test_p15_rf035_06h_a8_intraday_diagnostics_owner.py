"""P15 RF-035 (06h): intraday_trade_reports._report_diagnostics_from_report moved to intraday_report_diagnostics_projection; parity with the pre-move body."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest


def _norm(obj, root):
    return json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).replace(str(root), "<T>")


def _h(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _write(root, rel, payload):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return p


def _patched(mod, name, value, fn):
    orig = getattr(mod, name)
    setattr(mod, name, value)
    try:
        return fn()
    finally:
        setattr(mod, name, orig)

from libs.reporting import intraday_trade_reports as m
from libs.reporting import intraday_report_diagnostics_projection as owner

FN = "_report_diagnostics_from_report"
GOLDEN = "10cafa44b48700f1833a4914f920907c0c7a67b4c99b9d25ddf0688f8726d273"

CASES = [
    ({"generation": {"status": "ok", "model": "fake"}}, {}),
    ({"generation": {"mode": "deterministic"}}, {}),
    ({"generation": {"mode": "local_debug", "deterministic_report_status": "d"}}, {"status": "x"}),
    ({"ai_trade_report_status": "skipped"}, {"status": "ok"}),
    ({}, {"status": "partial", "parse_mode": "p", "completeness_score": "0.5", "required_keys_missing": ["a", "", "b"]}),
    ({}, {"status": "salvaged", "model_info": {"model": "mi"}}),
    ({"generation": {"status": "repaired"}}, {"error": "e"}),
    ({}, {"status": "failed", "error": "boom"}),
    ({"generation": {"status": "disabled"}}, {}),
    ({}, {"status": "ok", "completeness_score": "invalid"}),
    ({"generation": "bad"}, {"model_info": None}),
    ({"llm_brief_status": "ok"}, {"status": "ok"}),
]


def _scenarios(fn, root, mod):
    return [_patched(mod, "_utc_now_iso", lambda: "2026-10-31T00:00:00+00:00", lambda c=c: _call(lambda: fn(*c))) for c in CASES]


def test_expected_values(tmp_path):
    out = _scenarios(m._report_diagnostics_from_report, tmp_path, m)
    assert out[0][1]["report_status"] == "available" and out[0][1]["ai_trade_report_status"] == "ok" and out[0][1]["llm_model_used"] == "fake"
    assert out[1][1]["ai_trade_report_status"] == "skipped" and out[1][1]["generation_attempted"] is False and out[1][1]["report_reason_code"] == "deterministic_only"
    assert out[4][1]["ai_trade_report_status"] == "partial" and out[4][1]["llm_required_keys_missing"] == ["a", "b"]
    assert out[7][1]["report_status"] == "failed" and out[7][1]["last_error_message"] == "boom" and out[7][1]["generation_ts"] == "2026-10-31T00:00:00+00:00"
    assert out[9][0] == "exc" and out[9][1] == "ValueError" and out[10][0] == "ok" and out[10][1]["ai_trade_report_status"] == "error"


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


def test_wrapper_owner_and_pre_move_golden(tmp_path):
    a = _run(getattr(m, FN), tmp_path / "a", m)
    b = _run(lambda *a, **k: getattr(owner, FN)(*a, facade=m, **k), tmp_path / "b", m)
    assert a == b and _h(a) == GOLDEN


def test_wrapper_is_thin():
    import ast
    import inspect
    fn = ast.parse(inspect.getsource(getattr(m, FN))).body[0]
    stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
    assert len(stmts) == 1 and isinstance(stmts[0], ast.Return)
    assert "import intraday_trade_reports" not in inspect.getsource(owner)
