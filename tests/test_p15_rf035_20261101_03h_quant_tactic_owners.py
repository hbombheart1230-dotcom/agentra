"""P15 RF-035 (20261101-03h): eight more quant_tactic_report helpers moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import unittest
from types import MappingProxyType
from unittest import mock

from libs.reporting import quant_tactic_decision_label_projection as label_owner
from libs.reporting import quant_tactic_first_nested_mapping_projection as first_nested_owner
from libs.reporting import quant_tactic_mapping_projection as mapping_owner
from libs.reporting import quant_tactic_monitor_projection as monitor_owner
from libs.reporting import quant_tactic_nested_dicts_projection as nested_owner
from libs.reporting import quant_tactic_pct_projection as pct_owner
from libs.reporting import quant_tactic_reason_text_projection as reason_owner
from libs.reporting import quant_tactic_report as qt
from libs.reporting import quant_tactic_symbol_projection as symbol_owner

GOLDENS = {
    "a1": "445cac81385a087f40dcc9111132c7ff23bde543b93096e9e5abd195ead1aa04",
    "a2": "e5177ff4516f71dfb4c5823e99001819652826016dacd95e7fb7d020ba7303c1",
    "a3": "ef5fd5ae1d410607b89e75a55b79b614177b02e1fc2d91a5bf157c72f2122cb1",
    "a4": "fb320cb1567bc3af3054e98ad29fdf90af04ff55cdb1dbaab37fdee8a64211f1",
    "a5": "3854385fb59ce54f2fafedff1d7834346a09b6a666ed33ae2a76fcea2dd73cad",
    "a6": "caf0c8bd263af6baabe4c29a6ea178fd6fd30b82568307fca60d9775e991f4be",
    "a7": "b17bf6b4df26cb5e57a2520984438dca1d8da5ea876caffa4d9ef5276fc543cb",
    "a8": "a7932a952c33f2d7b298bba9bed2620dbffd16f5c7da9ba0f4786cfb6b96ebc9",
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
    src = {"x": 1}
    res = fn(src)
    out = [
        ["copy", [res == src, res is not src]],
        _call(lambda: fn([])),
        _call(lambda: fn(None)),
        _call(lambda: fn({})),
        _call(lambda: fn(MappingProxyType({"m": 1}))),
        _call(lambda: fn("abc")),
        _call(lambda: fn([("a", 1)])),
        _call(lambda: fn(0)),
        _call(lambda: fn()),
        _call(lambda: fn(_Odd())),
    ]
    with mock.patch.object(qt, "Mapping", tuple):
        out.append(_call(lambda: fn({"x": 1})))
        out.append(_call(lambda: fn((1, 2))))
    with mock.patch.object(qt, "Mapping", dict):
        out.append(_call(lambda: fn(MappingProxyType({"m": 1}))))
    return out


def _a2(fn, mod):
    values = [0.125, None, "", "bad", 0, 1, 1.5, -0.5, "0.5", True, False, [], [1], float("inf"), float("nan"), 1e-9, 12345.678, _Odd()]
    return [_call(lambda v=v: fn(v)) for v in values] + [_call(lambda: fn())]


def _a3(fn, mod):
    values = ["entry_ready", "unknown", "", None, "block_recommended", " wait ", "hold_watch", "hard_exit", "confirm_before_exit_recommended", "early_exit_warning", "exit_aligned", 0, 5, True, [], _Odd(), "ENTRY_READY"]
    return [_call(lambda v=v: fn(v)) for v in values] + [_call(lambda: fn())]


def _a4(fn, mod):
    out = [
        _call(lambda: fn(["a", "b"])),
        _call(lambda: fn([])),
        _call(lambda: fn(list("abcdefg"))),
        _call(lambda: fn(("x", " y ", None, ""))),
        _call(lambda: fn({"k": 1})),
        _call(lambda: fn(None)),
        _call(lambda: fn("text")),
        _call(lambda: fn([" ", ""])),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qt, "_items", lambda v: ["P%d" % i for i in range(8)]):
        out.append(_call(lambda: fn(["ignored"])))
    with mock.patch.object(qt, "_items", lambda v: []):
        out.append(_call(lambda: fn(["a"])))
    return out


def _a5(fn, mod):
    snap = {"y": 2}
    res = fn({"monitor_snapshot": snap, "monitor_output": {"x": 1}})
    out = [
        ["copy", [res == snap, res is not snap]],
        _call(lambda: fn({"monitor_output": {"x": 1}})),
        _call(lambda: fn({"monitor_snapshot": {}, "monitor_output": {"x": 1}})),
        _call(lambda: fn({"monitor_snapshot": [1], "monitor_output": [2]})),
        _call(lambda: fn({})),
        _call(lambda: fn(MappingProxyType({"monitor_output": {"z": 3}}))),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qt, "_mapping", lambda v: {"patched": bool(v)} if v else {}):
        out.append(_call(lambda: fn({"monitor_snapshot": {"a": 1}})))
        out.append(_call(lambda: fn({})))
    return out


def _tree():
    return {"a": {"b": 1}, "l": [{"x": 1}, ({"y": 2},), 5, [[{"deep": 1}]]], "t": ({"u": 3},)}


def _a6(fn, mod):
    deep = {"d0": {"d1": {"d2": {"d3": 1}}}}
    out = [
        _call(lambda: fn({"a": {"b": 1}}, max_depth=1)),
        _call(lambda: fn({"a": {"b": 1}}, max_depth=-1)),
        _call(lambda: fn({"a": {"b": 1}}, max_depth=0)),
        _call(lambda: fn(_tree())),
        _call(lambda: fn(deep, max_depth=2)),
        _call(lambda: fn(deep)),
        _call(lambda: fn([{"a": 1}, {"b": {"c": 2}}])),
        _call(lambda: fn(MappingProxyType({"p": {"q": 1}}))),
        _call(lambda: fn(None)),
        _call(lambda: fn("text")),
        _call(lambda: fn(5, max_depth=3)),
        _call(lambda: fn({"a": 1}, max_depth="x")),
        _call(lambda: fn()),
    ]
    src = {"a": {"b": 1}}
    res = fn(src)
    out.append(["identity", [res[0] == src, res[0] is not src, res[1] is src["a"] or res[1] == src["a"]]])
    with mock.patch.object(qt, "Mapping", tuple):
        out.append(_call(lambda: fn({"a": {"b": 1}})))
    calls = []
    real = qt._nested_dicts
    with mock.patch.object(qt, "_nested_dicts", lambda v, max_depth=9: calls.append(max_depth) or []):
        out.append(_call(lambda: fn({"a": {"b": 1}, "c": [1]})))
    out.append(["recursion-calls", calls])
    del real
    return out


def _a7(fn, mod):
    out = [
        _call(lambda: fn({"x": {"q": {"a": 1}}}, "q")),
        _call(lambda: fn({"x": {"q": {"a": 1}}}, "missing")),
        _call(lambda: fn({"q": {"top": 1}, "x": {"q": {"a": 1}}}, "q")),
        _call(lambda: fn({"x": {"q": {}}, "y": {"q": {"later": 1}}}, "q")),
        _call(lambda: fn({"x": {"q": [1]}}, "q")),
        _call(lambda: fn([{"q": {"in_list": 1}}], "q")),
        _call(lambda: fn({}, "q")),
        _call(lambda: fn(None, "q")),
        _call(lambda: fn({"q": {"a": 1}})),
        _call(lambda: fn()),
    ]
    src = {"x": {"q": {"a": 1}}}
    found = fn(src, "q")
    out.append(["copy", [found == {"a": 1}, found is not src["x"]["q"]]])
    with mock.patch.object(qt, "_nested_dicts", lambda root: [{"q": {"patched": 1}}]):
        out.append(_call(lambda: fn({}, "q")))
    with mock.patch.object(qt, "_mapping", lambda v: {"mp": 1} if v else {}):
        out.append(_call(lambda: fn({"x": {"q": {"a": 1}}}, "q")))
    return out


def _a8(fn, mod):
    out = [
        _call(lambda: fn({"symbol": "005930"})),
        _call(lambda: fn({"fact_payload": {"trade": {"symbol": "A"}}})),
        _call(lambda: fn({})),
        _call(lambda: fn({"shared_facts": {"symbol": " S "}})),
        _call(lambda: fn({"symbol": "005930", "fact_payload": {"trade": {"symbol": "A"}}, "shared_facts": {"symbol": "S"}})),
        _call(lambda: fn({"symbol": "", "fact_payload": {"trade": {"symbol": "A"}}, "shared_facts": {"symbol": "S"}})),
        _call(lambda: fn({"fact_payload": {"trade": {"symbol": ""}}, "shared_facts": {"symbol": "S"}})),
        _call(lambda: fn({"fact_payload": [1], "shared_facts": [2]})),
        _call(lambda: fn({"symbol": 5})),
        _call(lambda: fn({"symbol": None})),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qt, "_mapping", lambda v: {"symbol": "PM", "trade": {"symbol": "PT"}} if v else {}):
        out.append(_call(lambda: fn({"x": 1})))
        out.append(_call(lambda: fn({})))
    return out


CASES = {
    "a1": (_a1, "_mapping", lambda: mapping_owner._mapping, True, mapping_owner),
    "a2": (_a2, "_pct", lambda: pct_owner._pct, False, pct_owner),
    "a3": (_a3, "_decision_label", lambda: label_owner._decision_label, False, label_owner),
    "a4": (_a4, "_reason_text", lambda: reason_owner._reason_text, True, reason_owner),
    "a5": (_a5, "_monitor", lambda: monitor_owner._monitor, True, monitor_owner),
    "a6": (_a6, "_nested_dicts", lambda: nested_owner._nested_dicts, True, nested_owner),
    "a7": (_a7, "_first_nested_mapping", lambda: first_nested_owner._first_nested_mapping, True, first_nested_owner),
    "a8": (_a8, "_symbol", lambda: symbol_owner._symbol, True, symbol_owner),
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

    def test_a1_mapping(self):
        out = self._parity("a1")
        self.assertEqual(qt._mapping({"x": 1}), {"x": 1})
        self.assertEqual(qt._mapping([]), {})
        self.assertEqual(out[-3], ["ok", {}])
        self.assertEqual(out[-1], ["ok", {}])
        self.assertEqual(out[-2][0], "exc")

    def test_a2_pct(self):
        self._parity("a2")
        self.assertEqual(qt._pct(0.125), "12.50%")
        self.assertEqual(qt._pct(None), "-")
        self.assertEqual(qt._pct("bad"), "bad")

    def test_a3_decision_label(self):
        self._parity("a3")
        self.assertEqual(qt._decision_label("entry_ready"), "진입 준비")
        self.assertEqual(qt._decision_label("unknown"), "unknown")
        self.assertEqual(qt._decision_label(""), "-")

    def test_a4_reason_text(self):
        out = self._parity("a4")
        self.assertEqual(qt._reason_text(["a", "b"]), "a, b")
        self.assertEqual(qt._reason_text([]), "-")
        self.assertEqual(qt._reason_text(list("abcdefg")), "a, b, c, d, e")
        self.assertEqual(out[-2], ["ok", "P0, P1, P2, P3, P4"])

    def test_a5_monitor(self):
        out = self._parity("a5")
        self.assertEqual(qt._monitor({"monitor_output": {"x": 1}}), {"x": 1})
        self.assertEqual(qt._monitor({"monitor_snapshot": {"y": 2}, "monitor_output": {"x": 1}}), {"y": 2})
        self.assertEqual(out[0], ["copy", [True, True]])

    def test_a6_nested_dicts(self):
        out = self._parity("a6")
        self.assertEqual(qt._nested_dicts({"a": {"b": 1}}, max_depth=1), [{"a": {"b": 1}}, {"b": 1}])
        self.assertEqual(qt._nested_dicts({"a": {"b": 1}}, max_depth=-1), [])
        self.assertEqual(qt._nested_dicts([{"a": 1}, {"b": {"c": 2}}]), [{"a": 1}, {"b": {"c": 2}}, {"c": 2}])
        self.assertEqual(out[-1], ["recursion-calls", [8, 8]])

    def test_a7_first_nested_mapping(self):
        out = self._parity("a7")
        self.assertEqual(qt._first_nested_mapping({"x": {"q": {"a": 1}}}, "q"), {"a": 1})
        self.assertEqual(qt._first_nested_mapping({"x": {"q": {"a": 1}}}, "missing"), {})
        self.assertEqual(out[-3], ["copy", [True, True]])

    def test_a8_symbol(self):
        self._parity("a8")
        self.assertEqual(qt._symbol({"symbol": "005930"}), "005930")
        self.assertEqual(qt._symbol({"fact_payload": {"trade": {"symbol": "A"}}}), "A")
        self.assertEqual(qt._symbol({}), "")


if __name__ == "__main__":
    unittest.main()
