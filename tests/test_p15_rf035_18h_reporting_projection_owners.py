"""P15 RF-035 (18h): eight profitability_recovery_day1 bodies moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from libs.reporting import profitability_recovery_audit_projection as audit_owner
from libs.reporting import profitability_recovery_day1 as pr
from libs.reporting import profitability_recovery_diagnostic_row_projection as diag_owner
from libs.reporting import profitability_recovery_execution_projection as exec_owner
from libs.reporting import profitability_recovery_hold_projection as hold_owner
from libs.reporting import profitability_recovery_linkage_projection as linkage_owner
from libs.reporting import profitability_recovery_row_iteration_projection as iter_owner
from libs.reporting import profitability_recovery_scorecard_projection as score_owner
from libs.reporting import profitability_recovery_trade_dirs_projection as dirs_owner

GOLDENS = {
    "a1": "44ebd4b0fad9d39170a653cb248884b8869d6e5057dfc8b443d222705107bffc",
    "a2": "8c425bb1b1b139dbc98bb380422fd9ac3dd983a6b6984b78eb917e7304c15df5",
    "a3": "b05b0c3c559b64db8d78ac04a9fd737decb2204f72b9ac031578a51b4edcc7cb",
    "a4": "4316c7a6af63d89fd9a6fefa6eb3ecb11c1a9c1d0862565177eaea0fdea3e642",
    "a5": "e109e8fb3b6bdaa59b65bf4333396579365bf8949865bd5c436fe10e7b98b9d3",
    "a6": "35703ea099ed81011aea49b70a0a5b74432a10584ab2026eeeee224721a69df1",
    "a7": "821db58810bdff9b80566c01c3f15095cc3bbf80a2bbe9a9933f2d36be42e2b7",
    "a8": "8cfe67e2518337b9d25617f0ea2598415b4cb5941e3a0bde165765d4d8732455",
}


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, default=repr, sort_keys=False).encode()).hexdigest()


def _w(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def _fixture(root):
    """Fake reports tree: one rich closed trade, one empty trade, one non-trade dir."""
    root = Path(root)
    day = root / "trades" / "2026-10-31"
    rich = day / "TRD_B"
    _w(rich / "lifecycle_bundle.json", {
        "trade_id": "TRD_B", "symbol": "005930", "story_type": "decision_only", "trade_lifecycle_status": "closed",
        "execution": {"ord_no": "77", "qty": 3, "avg_price": 100, "status": "filled"},
        "story_contract": {"execution_mode_label": "Mock simulation"},
        "trade_outcome": {"return_pct": -1.5, "holding_time": "5m"},
        "same_day_reporter_linkage": {"status": "linked", "linkage_reason": "x"},
        "ai_report_diagnostics": {"ai_trade_report_status": "FAILED"},
    })
    _w(rich / "hold.json", {"hold_duration_sec": 300, "holding_events": [{"monitor_context": {"a": 1}}, "junk"]})
    _w(rich / "reports" / "report_generation_state.json", {"components": {"ai_trade_report": {"status": "failed"}}})
    _w(rich / "entry.json", {"price": 99})
    (day / "TRD_A").mkdir(parents=True)
    (day / "not_a_trade").mkdir()
    return root, day


def _a1(fn, mod, root):
    root = Path(root)
    out = [_call(lambda: fn(root, "none"))]
    _fixture(root)
    out.append(_call(lambda: fn(root, "2026-10-31")))
    out.append(_call(lambda: fn(str(root), 20261031)))
    out.append(_call(lambda: fn(None, "d")))
    out.append(_call(lambda: fn()))
    with mock.patch.object(mod, "_iter_trade_dirs", lambda p: [Path("/z"), Path("/a")]):
        out.append(_call(lambda: fn(root, "2026-10-31")))
    with mock.patch.object(mod, "Path", lambda *a: root / "nothing"):
        out.append(_call(lambda: fn(root, "2026-10-31")))
    return out


def _a2(fn, mod, root):
    root, day = _fixture(root)
    out = [_call(lambda: fn(day / "TRD_B")), _call(lambda: fn(day / "TRD_A")), _call(lambda: fn(day / "missing")), _call(lambda: fn(None)), _call(lambda: fn())]
    _w(day / "TRD_A" / "hold.json", "[1]")
    out.append(_call(lambda: fn(day / "TRD_A")))
    with mock.patch.object(mod, "_read_json", lambda p: {"patched": str(p.name)}):
        out.append(_call(lambda: fn(day / "TRD_A")))
    return out


def _a3(fn, mod, root):
    root = Path(root)
    art = _w(root / "art.json", "{}")
    rel = Path("relative_art_for_test.json")
    out = [
        _call(lambda: fn({"same_day_reporter_linkage": {"status": "linked", "linkage_reason": "r"}}, root)),
        _call(lambda: fn({"same_day_reporter_linkage": {"status": "missing", "linkage_reason": ""}}, root)),
        _call(lambda: fn({"artifacts": {"reporter_analysis_json": str(art)}}, root)),
        _call(lambda: fn({"artifacts": {"reporter_analysis_md": str(root / "nope.md")}}, root)),
        _call(lambda: fn({"section_provenance": {"reporter_status_human": {"artifact_path": str(art)}}}, root)),
        _call(lambda: fn({"section_provenance": {"reporter_status_human": "x"}}, root)),
        _call(lambda: fn({}, root)),
        _call(lambda: fn({"same_day_reporter_linkage": [1]}, root)),
        _call(lambda: fn({"artifacts": {"reporter_analysis_json": str(rel)}}, root)),
        _call(lambda: fn(None, root)),
        _call(lambda: fn({})),
    ]
    with mock.patch.object(mod, "_linkage_surface_present", lambda l: False):
        out.append(_call(lambda: fn({"same_day_reporter_linkage": {"status": "linked"}}, root)))
    with mock.patch.object(mod, "_bundle_artifacts", lambda b: {"reporter_analysis_json": str(art)}):
        out.append(_call(lambda: fn({}, root)))
    return out


def _a4(fn, mod, root):
    root, day = _fixture(root)
    out = [_call(lambda: fn(root, "none")), _call(lambda: fn(root, "2026-10-31")), _call(lambda: fn()), _call(lambda: fn(None, "d"))]
    with mock.patch.object(mod, "read_trade_diagnostic_row", lambda d: {"d": d.name}):
        out.append(_call(lambda: fn(root, "2026-10-31")))
    with mock.patch.object(mod, "iter_trade_dirs", lambda r, d: [Path("/x/T1")]):
        out.append(_call(lambda: fn(root, "any")))
    return out


def _a5(fn, mod, root):
    root, day = _fixture(root)
    out = [_call(lambda: fn(root, "none")), _call(lambda: fn(root, "2026-10-31")), _call(lambda: fn(root)), _call(lambda: fn(None, "d"))]
    rows = [{"closed_trade": True, "closed_trade_report_generation_regression": True, "execution_missing_fields_count": "2"}, {"holding_evidence_thin": True, "same_day_linkage_missing": 1}, {"execution_missing_fields_count": None}]
    with mock.patch.object(mod, "iter_trade_diagnostic_rows", lambda r, d: rows):
        out.append(_call(lambda: fn(root, 7)))
    with mock.patch.object(mod, "_top_recurring_weakness", lambda rs: "PATCHED"):
        out.append(_call(lambda: fn(root, "none")))
    return out


def _a6(fn, mod, root):
    root, day = _fixture(root)
    out = [_call(lambda: fn(root, "none")), _call(lambda: fn(root, "2026-10-31")), _call(lambda: fn(root)), _call(lambda: fn(None, "d"))]
    audit = {"trade_count": "2", "closed_trade_count": 1, "same_day_linkage_missing_count": 3, "holding_evidence_thin_count": None, "execution_fields_missing_count": 4,
             "closed_trade_report_generation_regression_count": 5, "closed_trade_decision_only_misclassification_count": 6,
             "top_recurring_diagnostic_weakness": "", "rows": [{"loss_trade": True}, {"loss_trade": False}, {"loss_trade": 1}]}
    with mock.patch.object(mod, "audit_profitability_recovery_day", lambda r, d: audit):
        out.append(_call(lambda: fn(root, 1)))
    with mock.patch.object(mod, "audit_profitability_recovery_day", lambda r, d: {}):
        out.append(_call(lambda: fn(root, 1)))
    return out


def _a7(fn, mod, root):
    root, day = _fixture(root)
    rich, empty = day / "TRD_B", day / "TRD_A"
    out = [
        _call(lambda: fn({"execution_details": {"order_id": "X"}}, empty)),
        _call(lambda: fn({}, empty)),
        _call(lambda: fn({"execution": {"ord_no": "77", "qty": 3}, "story_contract": {"execution_mode_label": "Mock simulation"}}, rich)),
        _call(lambda: fn({"execution_details": {}}, empty)),
        _call(lambda: fn({"exit_execution_details": {"order_id": "E", "avg_price": 5}, "story_contract": {"execution_mode_label": "Paper"}}, empty)),
        _call(lambda: fn({"entry_execution_details": {"order_id": "N"}, "execution": {"action": "BUY"}}, empty)),
        _call(lambda: fn({"exit": {"price": "7.5"}, "entry": {"price": 1}}, empty)),
        _call(lambda: fn({"monitor_snapshot": {"average_price": "3"}}, empty)),
        _call(lambda: fn({"execution": {"status": "", "qty": [], "price": 0}}, empty)),
        _call(lambda: fn({"execution": [1], "story_contract": [1]}, empty)),
        _call(lambda: fn({}, root / "no-dir")),
        _call(lambda: fn(None, empty)),
        _call(lambda: fn({})),
    ]
    with mock.patch.object(mod, "_read_json", lambda p: {"price": 42} if p.name == "entry.json" else {}):
        out.append(_call(lambda: fn({}, empty)))
    with mock.patch.object(mod, "_safe_float", lambda v: 9.0):
        out.append(_call(lambda: fn({"exit": {}, "entry": {}, "monitor_snapshot": {}}, empty)))
    return out


def _a8(fn, mod, root):
    root, day = _fixture(root)
    rich, empty = day / "TRD_B", day / "TRD_A"
    out = [
        _call(lambda: fn(empty)),
        _call(lambda: fn(rich)),
        _call(lambda: fn(root / "trades" / "2026-10-31" / "T123")),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    _w(empty / "lifecycle_bundle.json", {"trade_id": 5, "day": "dd", "symbol": None, "status": "closed", "hold_evidence_thin": True, "story_contract": {"story_type": "Decision_Only"}})
    _w(empty / "reports" / "ai_trade_report_llm_response.json", "{}")
    out.append(_call(lambda: fn(empty)))
    for name, value in (
        ("_is_closed_trade", lambda b: True),
        ("_resolve_execution_details", lambda b, d: {"order_id": 1}),
        ("_resolve_ai_trade_report_status", lambda b, c, e: "okk"),
        ("_safe_float", lambda v: -2.0),
        ("_linkage_surface_present", lambda l: True),
        ("_is_closed_trade_report_generation_regression", lambda **k: "REG"),
        ("_execution_missing_fields", lambda d: ["a", "b"]),
        ("_read_json", lambda p: {}),
        ("_resolve_same_day_linkage", lambda b, d: {"status": "S"}),
        ("_resolve_holding_evidence", lambda b, d: {"hold_events_count": 2, "monitor_context_snapshots": [{"a": 1}, 3], "holding_phase_summary": " p "}),
        ("_artifact_path", lambda d, *c: d / c[0]),
    ):
        with mock.patch.object(mod, name, value):
            out.append([name, _call(lambda: fn(rich))])
    return out


CASES = {
    "a1": (_a1, "iter_trade_dirs", lambda: dirs_owner.iter_trade_dirs, dirs_owner),
    "a2": (_a2, "_read_hold_payload", lambda: hold_owner._read_hold_payload, hold_owner),
    "a3": (_a3, "_resolve_same_day_linkage", lambda: linkage_owner._resolve_same_day_linkage, linkage_owner),
    "a4": (_a4, "iter_trade_diagnostic_rows", lambda: iter_owner.iter_trade_diagnostic_rows, iter_owner),
    "a5": (_a5, "audit_profitability_recovery_day", lambda: audit_owner.audit_profitability_recovery_day, audit_owner),
    "a6": (_a6, "build_daily_profitability_scorecard", lambda: score_owner.build_daily_profitability_scorecard, score_owner),
    "a7": (_a7, "_resolve_execution_details", lambda: exec_owner._resolve_execution_details, exec_owner),
    "a8": (_a8, "read_trade_diagnostic_row", lambda: diag_owner.read_trade_diagnostic_row, diag_owner),
}


def _run(key, which):
    scenario, name, owner_factory, _ = CASES[key]
    if which == "wrapper":
        fn = getattr(pr, name)
    else:
        raw = owner_factory()
        fn = lambda *a, **k: raw(*a, facade=pr, **k)  # noqa: E731
    with tempfile.TemporaryDirectory() as t:
        out = scenario(fn, pr, t)
        return json.loads(json.dumps(out, default=repr).replace(t, "<T>").replace(str(Path(t).resolve()), "<T>"))


class Test(unittest.TestCase):
    def _parity(self, key):
        a = _run(key, "wrapper")
        b = _run(key, "owner")
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDENS[key])
        name, owner_mod = CASES[key][1], CASES[key][3]
        fn = ast.parse(inspect.getsource(getattr(pr, name))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import profitability_recovery_day1", inspect.getsource(owner_mod))
        return a

    def test_a1_iter_trade_dirs(self):
        out = self._parity("a1")
        self.assertEqual(out[0], ["ok", []])
        self.assertEqual(len(out[1][1]), 2)
        self.assertEqual(out[1][1], sorted(out[1][1]))
        self.assertEqual(out[5], ["ok", ["PosixPath('/a')", "PosixPath('/z')"]])

    def test_a2_read_hold_payload(self):
        out = self._parity("a2")
        self.assertEqual(out[0][1]["hold_duration_sec"], 300)
        self.assertEqual(out[1], ["ok", {}])
        self.assertEqual(out[2], ["ok", {}])
        self.assertEqual(out[-1], ["ok", {"patched": "hold.json"}])

    def test_a3_resolve_same_day_linkage(self):
        out = self._parity("a3")
        self.assertEqual(out[0], ["ok", {"status": "linked", "linkage_reason": "r"}])
        self.assertEqual(out[2][1]["status"], "linked_day_fallback")
        self.assertEqual(out[6], ["ok", {}])
        self.assertEqual(out[7], ["ok", {}])

    def test_a4_iter_trade_diagnostic_rows(self):
        out = self._parity("a4")
        self.assertEqual(out[0], ["ok", []])
        self.assertEqual(len(out[1][1]), 2)
        self.assertEqual(out[4], ["ok", [{"d": "TRD_A"}, {"d": "TRD_B"}]])

    def test_a5_audit_profitability_recovery_day(self):
        out = self._parity("a5")
        empty = out[0][1]
        self.assertEqual((empty["trade_count"], empty["top_recurring_diagnostic_weakness"], empty["rows"]), (0, "none", []))
        self.assertEqual(empty["schema_version"], "profitability_recovery_day1_audit.v1")
        self.assertEqual(out[4][1]["execution_fields_missing_count"], 2)
        self.assertEqual(out[5][1]["top_recurring_diagnostic_weakness"], "PATCHED")

    def test_a6_build_daily_profitability_scorecard(self):
        out = self._parity("a6")
        e = out[0][1]
        self.assertEqual((e["total_trades"], e["closed_trades"], e["loss_trades"]), (0, 0, 0))
        self.assertEqual(out[4][1]["loss_trades"], 2)
        self.assertEqual(out[4][1]["top_recurring_diagnostic_weakness"], "none")
        self.assertEqual(out[5][1]["total_trades"], 0)

    def test_a7_resolve_execution_details(self):
        out = self._parity("a7")
        self.assertEqual(out[0], ["ok", {"order_id": "X"}])
        self.assertEqual(out[1][1], {"order_status": None, "order_id": None, "execution_mode": None, "broker_env": None, "filled_qty": None, "avg_price": None})
        self.assertEqual(out[2][1]["order_id"], "77")
        self.assertEqual(out[2][1]["broker_env"], "mock")
        self.assertEqual(out[-1][1]["avg_price"], 9.0)

    def test_a8_read_trade_diagnostic_row(self):
        out = self._parity("a8")
        row = out[0][1]
        self.assertEqual((row["closed_trade"], row["execution_missing_fields_count"]), (False, 6))
        self.assertEqual(out[2][1]["trade_id"], "T123")
        self.assertEqual(out[1][1]["closed_trade_report_generation_regression"], True)
        self.assertEqual(out[1][1]["loss_trade"], True)


if __name__ == "__main__":
    unittest.main()
