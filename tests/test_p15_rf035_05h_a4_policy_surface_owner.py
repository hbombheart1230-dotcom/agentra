"""P15 RF-035 (05h): report_source_helpers.build_policy_surface_quality_snapshot moved to report_source_policy_projection; parity with the pre-move body."""
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

from libs.reporting import report_source_helpers as m
from libs.reporting import report_source_policy_projection as owner

FN = "build_policy_surface_quality_snapshot"
GOLDEN = "037080b73652e230ec796b8426616892e3426cda6e30b0397c5b2d21e90c973e"


def _scenarios(fn, root, mod):
    out = []

    def with_health(health):
        def fake(**kw):
            if isinstance(health, BaseException):
                raise health
            return health
        return _patched(mod, "build_phase_5_2_5_3_runtime_health", fake, lambda: _call(lambda: fn(root / "ev.jsonl", root, "2026-10-30")))

    out.append(with_health({"policy_surface_quality_summary": {"n": 1}, "chart_structure_decision_hint_summary": {"c": 2}, "run_count": 2, "schema_version": "v9"}))
    out.append(with_health({"run_count": "3"}))
    out.append(with_health({"policy_surface_quality_summary": "bad", "chart_structure_decision_hint_summary": [1]}))
    out.append(with_health(FileNotFoundError("nf")))
    out.append(with_health(RuntimeError("boom")))
    out.append(with_health({"run_count": None}))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m.build_policy_surface_quality_snapshot, tmp_path, m)
    assert out[0][1]["source"]["run_count"] == 2 and out[0][1]["source"]["health_schema_version"] == "v9" and out[0][1]["summary"] == {"n": 1}
    assert out[3][1]["source"]["notes"] == ["no_canonical_monitor_runs_found"] and out[3][1]["source"]["run_count"] == 0
    assert out[4][1]["source"]["notes"] == ["policy_surface_quality_summary_unavailable"]
    assert out[1][1]["source"]["run_count"] == 3
    assert list(out[0][1]) == ["summary", "executive_summary", "chart_structure_summary", "chart_structure_executive_summary", "source"]


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


def _owner_fn(**fixed):
    return lambda *a, **k: getattr(owner, FN)(*a, facade=m, **k)


def test_wrapper_owner_and_pre_move_golden(tmp_path):
    a = _run(getattr(m, FN), tmp_path / "a", m)
    b = _run(_owner_fn(), tmp_path / "b", m)
    assert a == b and _h(a) == GOLDEN


def test_wrapper_is_thin():
    import inspect
    assert len(inspect.getsource(getattr(m, FN)).strip().splitlines()) <= 12
    assert "import symbol_trade_report" not in inspect.getsource(owner) and "import report_source_helpers" not in inspect.getsource(owner)
