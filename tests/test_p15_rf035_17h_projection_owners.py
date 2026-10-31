"""P15 RF-035 (17h): eight profitability_recovery_day1 bodies moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from libs.reporting import profitability_recovery_artifact_projection as artifact_owner
from libs.reporting import profitability_recovery_day1 as pr
from libs.reporting import profitability_recovery_evidence_projection as evidence_owner
from libs.reporting import profitability_recovery_io_projection as io_owner
from libs.reporting import profitability_recovery_status_projection as status_owner
from libs.reporting import profitability_recovery_weakness_projection as weakness_owner

GOLDENS = {
    "a1": "747201d3b544211056274d67dbb126da7107efba662d264aa3138ec70f64004b",
    "a2": "001fc84b701463b5baa929928744db8cb2976707421f8f157faf6dbdf4cdbfd6",
    "a3": "ba9d3c8b1f90a5181f80e1dd191b13e4c0c45670039db0869fa0f03fd0d1c4a4",
    "a4": "c8d93707be65ecdf06ca8cfd4ea8d3a33b63bb10ab1feb7cb1e6668c1a6b2bd8",
    "a5": "a9459f056bc7f50053212e4d93ae29ac44739226d3cdd74a9886ef3aeb1f27de",
    "a6": "b214b7804fce92be642b6dada5c33a256de404a4b742c49d90efb6f2f1c2eded",
    "a7": "8475a4483717bdaa833019fa981cdcc7d0d106a569d42fe270c373274d0fb671",
    "a8": "934b7bed4e22e127a22557277d033eda2f3057ec99d3a4318e5cc2ca4a067676",
}


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, default=repr).encode()).hexdigest()


_FULL = {k: 1 for k in ("order_status", "order_id", "execution_mode", "broker_env", "filled_qty", "avg_price")}


def _a1(fn, mod, root):
    out = [
        _call(lambda: fn({})),
        _call(lambda: fn(dict(_FULL))),
        _call(lambda: fn(dict(_FULL, order_id=""))),
        _call(lambda: fn(dict(_FULL, filled_qty=[], avg_price=None))),
        _call(lambda: fn(dict(_FULL, order_id=0))),
        _call(lambda: fn(None)),
        _call(lambda: fn([1])),
        _call(lambda: fn()),
    ]
    with mock.patch.object(mod, "REQUIRED_EXECUTION_FIELDS", ("x", "order_id")):
        out.append(_call(lambda: fn({"order_id": 1})))
    return out


def _dict_pick(key):
    def scenario(fn, mod, root):
        same = {key: {"x": 1}}
        r = fn(same)
        out = [["identity", r is same[key]], _call(lambda: fn({key: [1]})), _call(lambda: fn({})), _call(lambda: fn({key: None})), _call(lambda: fn([])), _call(lambda: fn(None)), _call(lambda: fn({key: {}})), _call(lambda: fn())]
        return out

    return scenario


def _a4(fn, mod, root):
    out = []
    for closed in (True, False):
        for exists in (True, False):
            for status in ("", "  ", "failed", "ERROR", " Skipped ", "ok", None, 0):
                out.append(_call(lambda c=closed, e=exists, s=status: fn(closed_trade=c, ai_trade_report_llm_exists=e, ai_status=s)))
    out.append(_call(lambda: fn(True, False, "")))
    out.append(_call(lambda: fn(closed_trade=True)))
    return out


def _a5(fn, mod, root):
    out = [
        _call(lambda: fn([])),
        _call(lambda: fn([{"same_day_linkage_missing": True}])),
        _call(lambda: fn([{"holding_evidence_thin": 1}, {"same_day_linkage_missing": 1}])),
        _call(lambda: fn([{"execution_missing_fields_count": "2"}, {"holding_evidence_thin": True}, {"holding_evidence_thin": True}])),
        _call(lambda: fn([{"closed_trade_report_generation_regression": 1, "closed_trade_decision_only_misclassification": 1}])),
        _call(lambda: fn(iter([{"holding_evidence_thin": 1}]))),
        _call(lambda: fn([{"execution_missing_fields_count": "bad"}])),
        _call(lambda: fn([1])),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(mod, "Counter", lambda: {}):
        out.append(_call(lambda: fn([{"holding_evidence_thin": True}])))
    return out


def _a6(fn, mod, root):
    out = [
        _call(lambda: fn({}, {}, True)),
        _call(lambda: fn({}, {}, False)),
        _call(lambda: fn({"ai_report_diagnostics": {"ai_trade_report_status": " Diag "}}, {}, False)),
        _call(lambda: fn({"ai_trade_report_status": "TOP"}, {"status": "FAILED"}, False)),
        _call(lambda: fn({"ai_trade_report_status": "TOP", "ai_report_diagnostics": {"ai_trade_report_status": "d"}}, {}, True)),
        _call(lambda: fn({"ai_report_diagnostics": [1]}, {"status": "  "}, True)),
        _call(lambda: fn({"ai_report_diagnostics": "x"}, {}, False)),
        _call(lambda: fn({"ai_trade_report_status": 0}, {"status": None}, False)),
        _call(lambda: fn(None, {}, True)),
        _call(lambda: fn({}, None, True)),
        _call(lambda: fn({})),
    ]
    return out


def _a7(fn, mod, root):
    root = Path(root)
    (root / "ok.json").write_text('{"a": 1}', encoding="utf-8")
    (root / "list.json").write_text("[1]", encoding="utf-8")
    (root / "bad.json").write_text("{nope", encoding="utf-8")
    (root / "bom.json").write_bytes(b"\xff\xfe\x00")
    (root / "dir.json").mkdir()
    out = [_call(lambda n=n: fn(root / n)) for n in ("missing.json", "ok.json", "list.json", "bad.json", "bom.json", "dir.json")]
    out.append(_call(lambda: fn(None)))
    out.append(_call(lambda: fn()))

    class _P:
        def exists(self):
            return True

        def read_text(self, encoding=None):
            return '{"fake": true}'

    out.append(_call(lambda: fn(_P())))
    with mock.patch.object(mod, "json", mock.Mock(loads=lambda text: {"patched": text})):
        out.append(_call(lambda: fn(root / "ok.json")))
    return out


def _a8(fn, mod, root):
    root = Path(root)
    (root / "b.json").write_text("{}", encoding="utf-8")
    (root / "c.json").write_text("{}", encoding="utf-8")
    out = [
        _call(lambda: fn(root, "a.json", "b.json")),
        _call(lambda: fn(root, "a.json", "x.json")),
        _call(lambda: fn(root, "c.json", "b.json")),
        _call(lambda: fn(root, "b.json")),
        _call(lambda: fn(root)),
        _call(lambda: fn(str(root), "b.json")),
        _call(lambda: fn(None, "b.json")),
    ]
    return out


CASES = {
    "a1": (_a1, "_execution_missing_fields", lambda: evidence_owner._execution_missing_fields, True, evidence_owner),
    "a2": (_dict_pick("artifacts"), "_bundle_artifacts", lambda: evidence_owner._bundle_artifacts, False, evidence_owner),
    "a3": (_dict_pick("section_provenance"), "_section_provenance", lambda: evidence_owner._section_provenance, False, evidence_owner),
    "a4": (_a4, "_is_closed_trade_report_generation_regression", lambda: status_owner._is_closed_trade_report_generation_regression, False, status_owner),
    "a5": (_a5, "_top_recurring_weakness", lambda: weakness_owner._top_recurring_weakness, True, weakness_owner),
    "a6": (_a6, "_resolve_ai_trade_report_status", lambda: status_owner._resolve_ai_trade_report_status, False, status_owner),
    "a7": (_a7, "_read_json", lambda: io_owner._read_json, True, io_owner),
    "a8": (_a8, "_artifact_path", lambda: artifact_owner._artifact_path, False, artifact_owner),
}


def _run(key, which):
    scenario, name, owner_factory, facade, _ = CASES[key]
    if which == "wrapper":
        fn = getattr(pr, name)
    else:
        raw = owner_factory()
        fn = (lambda *a, **k: raw(*a, facade=pr, **k)) if facade else raw
    with tempfile.TemporaryDirectory() as t:
        out = scenario(fn, pr, t)
        return json.loads(json.dumps(out, default=repr).replace(t, "<T>"))


class Test(unittest.TestCase):
    def _parity(self, key):
        a = _run(key, "wrapper")
        b = _run(key, "owner")
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDENS[key])
        name, owner_mod = CASES[key][1], CASES[key][4]
        fn = ast.parse(inspect.getsource(getattr(pr, name))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import profitability_recovery_day1", inspect.getsource(owner_mod))
        return a

    def test_a1_execution_missing_fields(self):
        out = self._parity("a1")
        self.assertEqual(pr._execution_missing_fields({}), list(pr.REQUIRED_EXECUTION_FIELDS))
        self.assertEqual(pr._execution_missing_fields(dict(_FULL)), [])
        self.assertEqual(out[-1], ["ok", ["x"]])

    def test_a2_bundle_artifacts(self):
        self._parity("a2")
        d = {"x": 1}
        self.assertIs(pr._bundle_artifacts({"artifacts": d}), d)
        self.assertEqual(pr._bundle_artifacts({"artifacts": [1]}), {})

    def test_a3_section_provenance(self):
        self._parity("a3")
        d = {"x": 1}
        self.assertIs(pr._section_provenance({"section_provenance": d}), d)
        self.assertEqual(pr._section_provenance({}), {})

    def test_a4_is_closed_trade_report_generation_regression(self):
        self._parity("a4")
        f = pr._is_closed_trade_report_generation_regression
        self.assertIs(f(closed_trade=True, ai_trade_report_llm_exists=False, ai_status=""), True)
        self.assertIs(f(closed_trade=False, ai_trade_report_llm_exists=False, ai_status="failed"), False)
        self.assertIs(f(closed_trade=True, ai_trade_report_llm_exists=True, ai_status=" Error "), True)
        self.assertIs(f(closed_trade=True, ai_trade_report_llm_exists=True, ai_status=""), False)

    def test_a5_top_recurring_weakness(self):
        out = self._parity("a5")
        self.assertEqual(pr._top_recurring_weakness([]), "none")
        self.assertEqual(pr._top_recurring_weakness([{"same_day_linkage_missing": True}]), "same_day_linkage_missing")
        self.assertEqual(out[-1][0], "exc")

    def test_a6_resolve_ai_trade_report_status(self):
        self._parity("a6")
        self.assertEqual(pr._resolve_ai_trade_report_status({}, {}, True), "ok")
        self.assertEqual(pr._resolve_ai_trade_report_status({"status": "x"}, {"status": "FAILED"}, False), "failed")
        self.assertEqual(pr._resolve_ai_trade_report_status({}, {}, False), "")

    def test_a7_read_json(self):
        out = self._parity("a7")
        self.assertEqual([o[1] for o in out[:6]][:3], [{}, {"a": 1}, {}])
        self.assertEqual(out[-1], ["ok", {"patched": '{"a": 1}'}])

    def test_a8_artifact_path(self):
        out = self._parity("a8")
        self.assertEqual(out[0], ["ok", "PosixPath('<T>/b.json')"])
        self.assertEqual(out[1], ["ok", "PosixPath('<T>/a.json')"])
        self.assertEqual(out[4][0], "exc")
        self.assertEqual(out[4][1], "IndexError")


if __name__ == "__main__":
    unittest.main()
