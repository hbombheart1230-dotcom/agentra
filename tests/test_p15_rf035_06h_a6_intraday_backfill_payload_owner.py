"""P15 RF-035 (06h): intraday_trade_reports.build_live_bundle_backfill_payload moved to intraday_report_payload_projection; parity with the pre-move body."""
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
from libs.reporting import intraday_report_payload_projection as owner

FN = "build_live_bundle_backfill_payload"
GOLDEN = "7549e0be22ccb479095c4a751cf37ad51728c092a31bf4a825c1e221f8a39a46"


def _kw(root, **o):
    p = lambda n: root / n
    base = dict(trade_id="T1", status="closed", story_type="completed", execution_mode_label="mock", symbol="005930", entry_run_id="e1", hold_run_ids=["h1", "h2"], exit_run_id="x1", linked_run_ids=["r1"],
                lifecycle_summary="sum", lifecycle_bundle_path=p("lb.json"), story_input_path=p("si.json"), story_compact_input_path=p("sci.json"), trade_report_json_written="rep.json", trade_report_md_written="",
                strategist_llm_response_path=p("sl.json"), ai_trade_report_llm_response_written="llm.json", entry_artifact_path=p("en.json"), hold_artifact_path=p("ho.json"), exit_artifact_path=p("ex.json"),
                strategist_evidence_path=p("se.json"), scanner_evidence_path=p("sc.json"), monitor_evidence_path=p("mo.json"), commander_evidence_path=p("co.json"), trade_provenance_path=p("pr.json"),
                trade_health_path=p("he.json"), trade_artifact_links_path=p("li.json"), trade_root=p("root"), trade_report_summary="trs", diagnostics={"report_status": "available", "generation_attempted": False})
    base.update(o)
    return base


def _scenarios(fn, root, mod):
    out = [_call(lambda: fn(**_kw(root)))]
    out.append(_call(lambda: fn(**_kw(root, diagnostics=None))))
    out.append(_call(lambda: fn(**_kw(root, diagnostics={"report_status": "failed", "last_error_message": "boom", "llm_model_used": "m", "ai_trade_report_status": "error"}, linked_run_ids=[], hold_run_ids=[]))))
    out.append(_call(lambda: fn(**_kw(root, trade_report_json_written=None, ai_trade_report_llm_response_written=None))))
    out.append(_call(lambda: fn(**{k: v for k, v in _kw(root).items() if k != "symbol"})))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m.build_live_bundle_backfill_payload, tmp_path, m)
    r = out[0][1]
    assert list(r) == ["lifecycle_row", "run_bundle_row_patch", "bundle_artifacts_patch"]
    assert r["lifecycle_row"]["trade_id"] == "T1" and r["run_bundle_row_patch"]["report_status"] == "available"
    assert r["bundle_artifacts_patch"]["lifecycle_bundle_json"] == str(tmp_path / "lb.json")
    assert out[2][1]["run_bundle_row_patch"]["report_status"] == "failed" and out[4][0] == "exc"
    kw = _kw(tmp_path)
    before = list(kw["hold_run_ids"])
    m.build_live_bundle_backfill_payload(**kw)
    assert kw["hold_run_ids"] == before


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
