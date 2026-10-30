"""P15 RF-035 (06h): intraday_trade_reports.build_same_day_reporter_linkage moved to intraday_report_linkage_projection; parity with the pre-move body."""
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
from libs.reporting import intraday_report_linkage_projection as owner

FN = "build_same_day_reporter_linkage"
GOLDEN = "0247894a62bc1c9c58f2ea4c426bbce390ee5d1295ba873c659b4bebfbce04b0"


def _scenarios(fn, root, mod):
    root.mkdir(parents=True, exist_ok=True)
    def call(**o):
        kw = dict(reporter_obj={}, reporter_js=root / "r.json", reporter_md=root / "r.md", entry_run_id="", exit_run_id="", entry_bundle={}, exit_bundle={})
        kw.update(o)
        return _call(lambda: fn(**kw))
    out = [call()]
    out.append(call(entry_bundle={"reporter": {"reporter_analysis_found": True}}, entry_run_id="r1"))
    out.append(call(entry_bundle={"reporter": {"reporter_analysis_found": True}}, entry_run_id="r1", exit_bundle={"reporter": {"reporter_analysis_found": True}}, exit_run_id="r1"))
    out.append(call(entry_bundle={"reporter": {"reporter_analysis_found": True}}, entry_run_id="r1", exit_bundle={"reporter": {"reporter_analysis_found": True}}, exit_run_id="r2"))
    out.append(call(entry_bundle={"reporter": {"reporter_analysis_day_file_found": True}}))
    (root / "r.json").write_text("{}", encoding="utf-8")
    out.append(call(reporter_obj={"ai_summary": "S", "ai_run_grade": "A"}))
    out.append(call(reporter_obj="bad", entry_bundle={"reporter": "bad"}, exit_bundle={"reporter": []}))
    out.append(call(entry_bundle=None))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m.build_same_day_reporter_linkage, tmp_path, m)
    assert out[0][1]["status"] == "missing" and out[0][1]["linked_run_ids"] == []
    assert out[1][1]["status"] == "linked_run" and out[1][1]["linked_run_ids"] == ["r1"] and out[2][1]["linked_run_ids"] == ["r1"] and out[3][1]["linked_run_ids"] == ["r1", "r2"]
    assert out[4][1]["status"] == "linked_day_fallback" and out[5][1]["status"] == "linked_day_fallback" and out[5][1]["reporter_analysis_grade"] == "A" and out[5][1]["reporter_analysis_json_found"] is True
    assert out[6][1]["reporter_analysis_grade"] == "N/A" and out[7][0] == "exc"


def test_keyword_only():
    with pytest.raises(TypeError):
        m.build_same_day_reporter_linkage({}, Path("a"), Path("b"), "", "", {}, {})


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
