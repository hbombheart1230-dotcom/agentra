"""P15 RF-035 (20261101-04h): eight more quant_tactic_report helpers moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import unittest
from types import MappingProxyType
from unittest import mock

from libs.reporting import quant_tactic_candidate_symbol_projection as symbol_owner
from libs.reporting import quant_tactic_entry_info_projection as info_owner
from libs.reporting import quant_tactic_entry_visibility_projection as visibility_owner
from libs.reporting import quant_tactic_exit_drifts_projection as drifts_owner
from libs.reporting import quant_tactic_mismatches_projection as mismatches_owner
from libs.reporting import quant_tactic_playbook_projection as playbook_owner
from libs.reporting import quant_tactic_report as qt
from libs.reporting import quant_tactic_scanner_chart_fit_projection as chart_fit_owner
from libs.reporting import quant_tactic_value_projection as value_owner

GOLDENS = {
    "a1": "b139bf5b672c966d40fadd60d52f4997d9d6f355f59e54b275ff4a14315e4999",
    "a2": "ae2ed38425ba2185d5d9855e6cf68739e912aec189b9a41fc5809ddb01864d56",
    "a3": "53cc6d5e885a8657fb0df4019b0df30dc3f53d90e6ff36d6477d19bbb761de8a",
    "a4": "3c98f83a2c7c529ba0efc89a736b5e57f86d94d4cfeed91af7033b19f0415a0f",
    "a5": "42b8a4e4575467cec3fd1ef9156272cf246db23ff3e86a930b222990c5f872a9",
    "a6": "59fc04bfb58bc876353cd41781e262545b313d392c5b69d0b8d7dbab215a587c",
    "a7": "1118b50b0acc24f56fb44aae750e6eb5df5c344b887c6dab06c321dab3c4b9da",
    "a8": "4b82970e0237ca5f9762e1746dcf2f19d0f2d78cf7ec9ddc6e7001f40e5b9d9a",
}


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, default=repr).encode()).hexdigest()


class _Odd:
    def __bool__(self):
        raise RuntimeError("odd-bool")

    def __str__(self):
        return " Odd "


def _a1(fn, mod):
    out = [
        _call(lambda: fn({"market_context": {"selected_playbook": "PB"}})),
        _call(lambda: fn({}, fallback="F")),
        _call(lambda: fn({})),
        _call(lambda: fn({"strategist_summary": {"playbook": " S "}, "market_context_at_entry": {"playbook": "E"}, "market_context": {"playbook": "M"}})),
        _call(lambda: fn({"strategist_summary": {"selected_playbook": "S2"}, "market_context": {"playbook": "M"}})),
        _call(lambda: fn({"strategist_summary": {"playbook": "", "selected_playbook": "S3"}})),
        _call(lambda: fn({"market_context_at_entry": {"playbook": "  "}, "market_context": {"playbook": "M"}})),
        _call(lambda: fn({"strategist_summary": [1], "market_context": "x"}, fallback=" fb ")),
        _call(lambda: fn({}, fallback=None)),
        _call(lambda: fn({}, fallback=5)),
        _call(lambda: fn(MappingProxyType({"market_context": {"playbook": "mp"}}))),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qt, "_mapping", lambda v: {"playbook": "PATCHED"} if v else {}):
        out.append(_call(lambda: fn({"strategist_summary": {"a": 1}})))
        out.append(_call(lambda: fn({}, fallback="F")))
    return out


def _a2(fn, mod):
    src = {"x": 1}
    res = fn({"entry_execution_visibility": src})
    out = [
        ["copy", [res == src, res is not src]],
        _call(lambda: fn({})),
        _call(lambda: fn({"entry_execution_visibility": [1]})),
        _call(lambda: fn({"entry_execution_visibility": None})),
        _call(lambda: fn(MappingProxyType({"entry_execution_visibility": {"m": 1}}))),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qt, "_mapping", lambda v: {"patched": v}):
        out.append(_call(lambda: fn({"entry_execution_visibility": 5})))
    return out


def _a3(fn, mod):
    focus = {"entry_triggered": True, "entry_decision": "go", "entry_guard_reason": "", "entry_reason": "ok", "entry_primary_failure_axis": "ax", "entry_cost_adjusted_edge_ok": False, "entry_cost_adjusted_edge_pct": 0.5, "entry_cost_drag_pct": 0, "entry_cost_filter": {"k": 1}}
    out = [
        _call(lambda: fn({"monitor_focus_context": {"entry_triggered": True, "entry_reason": "ok"}}, {})),
        _call(lambda: fn({}, {})),
        _call(lambda: fn({"monitor_focus_context": focus}, {"entry_triggered": False, "entry_decision": "m"})),
        _call(lambda: fn({"entry_grouped_logic_trace": {"reason": "g", "extra": 1}, "monitor_focus_context": {"entry_reason": "f"}}, {})),
        _call(lambda: fn({"monitor_entry_candidate_cascade": {"reason": "c", "primary_failure_axis": "cx"}}, {})),
        _call(lambda: fn({"entry_grouped_logic_trace": {"reason": "g"}, "monitor_entry_candidate_cascade": {"reason": "c", "primary_failure_axis": "cx"}}, {})),
        _call(lambda: fn({}, {"entry_triggered": 0, "entry_decision": "watch"})),
        _call(lambda: fn({}, {"entry_triggered": None, "entry_decision": ""})),
        _call(lambda: fn({"monitor_focus_context": [1], "entry_grouped_logic_trace": "x"}, [1])),
        _call(lambda: fn({"monitor_focus_context": {"entry_guard_reason": "gr", "entry_reason": "r"}}, {})),
        _call(lambda: fn(None, {})),
        _call(lambda: fn({})),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qt, "_mapping", lambda v: {"entry_reason": "pm", "reason": "pg"} if v else {}):
        out.append(_call(lambda: fn({"monitor_focus_context": 1, "entry_grouped_logic_trace": 1, "monitor_entry_candidate_cascade": 1}, {"entry_triggered": True})))
    return out


def _a4(fn, mod):
    values = [{"ticker": "005930"}, {}, {"symbol": " S ", "code": "C"}, {"code": "C", "stk_cd": "K"}, {"stk_cd": "K", "ticker": "T"}, {"symbol": "", "code": "", "stk_cd": "", "ticker": " t "}, {"symbol": 5}, {"symbol": None, "code": 7}, MappingProxyType({"symbol": "mp"}), [], None, {"symbol": _Odd()}]
    return [_call(lambda v=v: fn(v)) for v in values] + [_call(lambda: fn())]


def _a5(fn, mod):
    out = [
        _call(lambda: fn({"scanner_chart_fit_score": 2})),
        _call(lambda: fn({})),
        _call(lambda: fn({"scanner_chart_fit": {"explicit": 1}, "scanner_chart_fit_score": 5})),
        _call(lambda: fn({"scanner_chart_fit_components": {"c": 1}})),
        _call(lambda: fn({"scanner_chart_fit_score": 0, "scanner_chart_fit_authority": "auth", "scanner_chart_fit_components": {"c": 1}, "scanner_chart_fit_penalty": 0.5})),
        _call(lambda: fn({"scanner_chart_fit_score": "", "scanner_chart_fit_components": {}})),
        _call(lambda: fn({"scanner_chart_fit_score": None, "scanner_chart_fit_authority": "x"})),
        _call(lambda: fn({"scanner_chart_fit": [1], "scanner_chart_fit_score": 1, "scanner_chart_fit_authority": None})),
        _call(lambda: fn({"scanner_chart_fit_score": False})),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    src = {"scanner_chart_fit_components": {"c": 1}, "scanner_chart_fit_score": 1}
    res = fn(src)
    out.append(["copy", [res["components"] == {"c": 1}, res["components"] is not src["scanner_chart_fit_components"]]])
    with mock.patch.object(qt, "_mapping", lambda v: {"mp": 1} if v else {}):
        out.append(_call(lambda: fn({"scanner_chart_fit": 1})))
        out.append(_call(lambda: fn({"scanner_chart_fit_score": 3, "scanner_chart_fit_components": 1})))
        out.append(_call(lambda: fn({"scanner_chart_fit_score": None})))
    return out


def _a6(fn, mod):
    values = ["  A ", None, "", 0, 5, False, True, [], [1], {}, "ok", " \n ", _Odd(), 1.5]
    return [_call(lambda v=v: fn(v)) for v in values] + [_call(lambda: fn())]


_SOURCES = [("entry", "B"), ("exit_quant_decision", "C"), ("monitor", "A"), ("entry", "A"), ("exit_quant_decision", "A"), ("x", "")]


def _pairs_cases(fn, mod):
    return [
        _call(lambda: fn(_SOURCES[:2], "A")),
        _call(lambda: fn(_SOURCES[:2], "")),
        _call(lambda: fn(_SOURCES, "A")),
        _call(lambda: fn(_SOURCES, "B")),
        _call(lambda: fn([], "A")),
        _call(lambda: fn(_SOURCES, None)),
        _call(lambda: fn(iter(_SOURCES), "A")),
        _call(lambda: fn([("only",)], "A")),
        _call(lambda: fn([["entry", "B"]], "A")),
        _call(lambda: fn(None, "A")),
        _call(lambda: fn("ab", "A")),
        _call(lambda: fn(_SOURCES)),
        _call(lambda: fn()),
        _call(lambda: fn([("entry", 5), ("exit_quant_decision", None)], 5)),
    ]


CASES = {
    "a1": (_a1, "_playbook", lambda: playbook_owner._playbook, True, playbook_owner),
    "a2": (_a2, "_entry_visibility", lambda: visibility_owner._entry_visibility, True, visibility_owner),
    "a3": (_a3, "_entry_info_from_visibility", lambda: info_owner._entry_info_from_visibility, True, info_owner),
    "a4": (_a4, "_candidate_symbol", lambda: symbol_owner._candidate_symbol, False, symbol_owner),
    "a5": (_a5, "_scanner_chart_fit_from_row", lambda: chart_fit_owner._scanner_chart_fit_from_row, True, chart_fit_owner),
    "a6": (_a6, "_tactic_value", lambda: value_owner._tactic_value, False, value_owner),
    "a7": (_pairs_cases, "_tactic_mismatches", lambda: mismatches_owner._tactic_mismatches, False, mismatches_owner),
    "a8": (_pairs_cases, "_exit_tactic_drifts", lambda: drifts_owner._exit_tactic_drifts, False, drifts_owner),
}


def _run(key, which):
    scenario, name, owner_factory, facade, _ = CASES[key]
    if which == "wrapper":
        fn = getattr(qt, name)
    else:
        raw = owner_factory()
        fn = (lambda *a, **k: raw(*a, facade=qt, **k)) if facade else raw
    return json.loads(json.dumps(scenario(fn, qt), default=repr))


class Test(unittest.TestCase):
    def _parity(self, key):
        a = _run(key, "wrapper")
        b = _run(key, "owner")
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDENS[key])
        name, owner_mod = CASES[key][1], CASES[key][4]
        fn = ast.parse(inspect.getsource(getattr(qt, name))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import quant_tactic_report", inspect.getsource(owner_mod))
        return a

    def test_a1_playbook(self):
        out = self._parity("a1")
        self.assertEqual(qt._playbook({"market_context": {"selected_playbook": "PB"}}), "PB")
        self.assertEqual(qt._playbook({}, fallback="F"), "F")
        self.assertEqual(out[-2], ["ok", "PATCHED"])

    def test_a2_entry_visibility(self):
        out = self._parity("a2")
        self.assertEqual(qt._entry_visibility({"entry_execution_visibility": {"x": 1}}), {"x": 1})
        self.assertEqual(qt._entry_visibility({}), {})
        self.assertEqual(out[0], ["copy", [True, True]])

    def test_a3_entry_info_from_visibility(self):
        out = self._parity("a3")
        got = qt._entry_info_from_visibility({"monitor_focus_context": {"entry_triggered": True, "entry_reason": "ok"}}, {})
        self.assertEqual((got["triggered"], got["reason"], got["guard_reason"]), (True, "ok", "ok"))
        self.assertEqual(qt._entry_info_from_visibility({}, {}), {})
        self.assertEqual(out[1], ["ok", {}])

    def test_a4_candidate_symbol(self):
        self._parity("a4")
        self.assertEqual(qt._candidate_symbol({"ticker": "005930"}), "005930")
        self.assertEqual(qt._candidate_symbol({}), "")

    def test_a5_scanner_chart_fit_from_row(self):
        out = self._parity("a5")
        self.assertEqual(qt._scanner_chart_fit_from_row({"scanner_chart_fit_score": 2}), {"score": 2, "authority": "", "components": {}, "penalty": None})
        self.assertEqual(qt._scanner_chart_fit_from_row({}), {})
        self.assertEqual(out[11], ["copy", [True, True]])

    def test_a6_tactic_value(self):
        self._parity("a6")
        self.assertEqual(qt._tactic_value("  A "), "A")
        self.assertEqual(qt._tactic_value(None), "")

    def test_a7_tactic_mismatches(self):
        out = self._parity("a7")
        self.assertEqual(qt._tactic_mismatches([("entry", "B"), ("exit_quant_decision", "C")], "A"), [{"source": "entry", "tactic_id": "B"}])
        self.assertEqual(qt._tactic_mismatches([("entry", "B")], ""), [])
        self.assertEqual(out[0], ["ok", [{"source": "entry", "tactic_id": "B"}]])

    def test_a8_exit_tactic_drifts(self):
        out = self._parity("a8")
        self.assertEqual(qt._exit_tactic_drifts([("entry", "B"), ("exit_quant_decision", "C")], "A"), [{"source": "exit_quant_decision", "tactic_id": "C"}])
        self.assertEqual(qt._exit_tactic_drifts([("exit_quant_decision", "C")], ""), [])
        self.assertEqual(out[1], ["ok", []])


if __name__ == "__main__":
    unittest.main()
