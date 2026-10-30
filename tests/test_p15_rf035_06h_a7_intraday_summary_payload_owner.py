"""P15 RF-035 (06h): intraday_trade_reports.build_live_execution_summary_payload moved to intraday_report_payload_projection; parity with the pre-move body."""
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

FN = "build_live_execution_summary_payload"
GOLDEN = "dad48f4d2b844f7c2a5783101336f822cb8a46f31f2ee5481ffe4348c4476962"


def _kw(root, **o):
    base = dict(day="2026-10-30", role="reporter", event_log_path=root / "ev.jsonl", evidence_log_path=root / "evd.jsonl", lifecycle_rows=[{"report_status": "ok"}, {"report_status": "FAILED"}],
                run_bundle_rows=[], lifecycle_story_type_counts={"a": 1}, run_story_type_counts=None, target_ctx={"targeted_mode": 1, "target_run_id": "r", "execution_run_count": "2"},
                canonical_trades_root=root / "trades", trade_js=root / "t.json", trade_md=root / "t.md", reporter_js=root / "rj.json", reporter_md=root / "rm.md",
                operator_summary_json=root / "os.json", operator_summary_md=root / "os.md")
    base.update(o)
    return base


def _scenarios(fn, root, mod):
    root.mkdir(parents=True, exist_ok=True)
    out = []
    out.append(_patched(mod, "_utc_now_iso", lambda: "2026-10-31T00:00:00+00:00", lambda: _call(lambda: fn(**_kw(root)))))
    (root / "rj.json").write_text("{}", encoding="utf-8")
    (root / "os.md").write_text("x", encoding="utf-8")
    out.append(_patched(mod, "_utc_now_iso", lambda: "T", lambda: _call(lambda: fn(**_kw(root, lifecycle_rows=[None, {}, {"report_status": " Ok "}], target_ctx=None)))))
    out.append(_patched(mod, "_utc_now_iso", lambda: "T", lambda: _call(lambda: fn(**_kw(root, lifecycle_rows=None, run_bundle_rows=[{"a": 1}], lifecycle_story_type_counts=None)))))
    out.append(_patched(mod, "_utc_now_iso", lambda: "T", lambda: _call(lambda: fn(**_kw(root, target_ctx={"execution_run_count": "bad"})))))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m.build_live_execution_summary_payload, tmp_path, m)
    r = out[0][1]
    assert r["report_status_counts"] == {"ok": 1, "failed": 1} and r["bundle_count"] == 2 and r["ts"] == "2026-10-31T00:00:00+00:00"
    assert r["day_artifacts"]["reporter_analysis_json"] == ""  # fixture file is created after the first scenario
    r2 = out[1][1]
    assert r2["day_artifacts"]["reporter_analysis_json"] == str(tmp_path / "rj.json") and r2["day_artifacts"]["operator_summary_md"] == str(tmp_path / "os.md")
    assert r2["report_status_counts"] == {"unknown": 2, "ok": 1} and out[3][0] == "exc" and out[3][1] == "ValueError"
    assert r["targeted_mode"] is True and r["targeted_execution_run_count"] == 2 and out[2][1]["bundle_count"] == 0


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
