"""P15 RF-035 (16h): eight execution_truth_surface / profitability_recovery_day1 bodies moved to Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import unittest
from unittest import mock

from libs.reporting import execution_truth_bullet_projection as bullet_owner
from libs.reporting import execution_truth_scalar_projection as et_scalar
from libs.reporting import execution_truth_surface as et
from libs.reporting import profitability_recovery_day1 as pr
from libs.reporting import profitability_recovery_scalar_projection as pr_scalar
from libs.reporting import profitability_recovery_trade_projection as pr_trade

GOLDENS = {
    "a1": "724578e5f2fe33d0896393c152f027aa51dcd1a001f2caf8d1660b4c2ec89275",
    "a2": "4a9358be52232e6cca9aa661f876b631659d8333bac37aa78c7f93ecda831243",
    "a3": "3fa6785512e2dae253ecdc482e3c6cba91f94adf65e08b97df5e4c89a5413268",
    "a4": "402155c18d6cf244446ad94c6d47869b3551f7708aa3b27ad0a86c4c90fd92cc",
    "a5": "37f39077115e451ba5e6ef35aff3411c8ce70dea04d05d8f6263204ee65690fc",
    "a6": "860cb0d9e0c0915b33b3cf9844ebe5122b17d4b9decbf3c5c2d285dacdb8b263",
    "a7": "50191bf956dc78ddf6ed74c7f337d7836d0812b457993ff455280859ec78268e",
    "a8": "9f7cfaa214b86b96f51947ce7c9d6b504d227dbe57663d53543cc07e905c4760",
}


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, default=repr).encode()).hexdigest()


class _Bad:
    def __float__(self):
        raise ValueError("bad-float")

    def __str__(self):
        return "BAD"


_VALUES = [None, "", 0, 0.0, "0", "123.456", 0.125, "bad", "  ABC  ", -1, True, [], _Bad(), "Unavailable", "NOT_AVAILABLE", " none ", "-", "ok"]
_DETAILS = {"broker_truth_source": "paper", "filled_price": 100, "broker_buy_price": 100, "broker_realized_pnl": -1, "broker_realized_pnl_pct": -0.01, "broker_fee": 1}


def _a1(fn, mod):
    out = [_call(lambda v=v: fn(v)) for v in _VALUES]
    out += [_call(lambda: fn("  ABC  ", max_len=2)), _call(lambda: fn("abcdef", max_len=-1)), _call(lambda: fn("abc", max_len=0)), _call(lambda: fn("abc", 2)), _call(lambda: fn())]
    return out


def _a2(fn, mod):
    return [_call(lambda v=v: fn(v)) for v in _VALUES] + [_call(lambda: fn())]


def _a3(fn, mod):
    return [_call(lambda v=v: fn(v)) for v in _VALUES] + [_call(lambda: fn())]


def _a4(fn, mod):
    return [_call(lambda v=v: fn(v)) for v in _VALUES] + [_call(lambda: fn())]


def _a5(fn, mod):
    shared = {"broker_fill_price": 5, "broker_buy_price": 6, "broker_fee": 2, "broker_tax": 3, "pnl": "unavailable", "pnl_pct": 0.5, "price_truth_source": "kiwoom", "pnl_truth_source": "broker"}
    out = [
        _call(lambda: fn(execution_details=dict(_DETAILS))),
        _call(lambda: fn(execution_details=dict(_DETAILS, broker_realized_pnl_pct=None, broker_tax=0.5), shared_facts=shared)),
        _call(lambda: fn(shared_facts=shared)),
        _call(lambda: fn(shared_facts={"broker_fill_price": "x", "broker_buy_price": "y", "pnl": 3, "price_truth_source": "unavailable"})),
        _call(lambda: fn()),
        _call(lambda: fn(execution_details=None, shared_facts=None)),
        _call(lambda: fn(execution_details=[1])),
        _call(lambda: fn(execution_details={"a": 1}, shared_facts=[("k", 1)])),
    ]
    out.append(_call(lambda: _patch_a5(fn, mod)))
    return out


def _patch_a5(fn, mod):
    res = []
    with mock.patch.object(mod, "_clip", lambda v, **k: "CL"):
        res.append(fn(execution_details=dict(_DETAILS), shared_facts={"price_truth_source": "p", "pnl_truth_source": "q"}))
    with mock.patch.object(mod, "_fmt_price", lambda v: "FP"), mock.patch.object(mod, "_fmt_pct", lambda v: "FC"), mock.patch.object(mod, "_is_available", lambda v: True):
        res.append(fn(execution_details=dict(_DETAILS)))
    with mock.patch.object(mod, "with_ro_particle", lambda t: "WRP:" + t), mock.patch.object(mod, "price_truth_source_label", lambda t: "PL"), mock.patch.object(mod, "pnl_truth_source_label", lambda t: "NL"):
        res.append(fn(shared_facts={"price_truth_source": "k", "pnl_truth_source": "b"}))
    return res


def _a6(fn, mod):
    return [_call(lambda v=v: fn(v)) for v in _VALUES] + [_call(lambda: fn("1.25")), _call(lambda: fn("1e3")), _call(lambda: fn())]


_BUNDLES = [{"trade_lifecycle_status": "closed"}, {"status": " CLOSED "}, {"exit": {"action": "SELL"}}, {"exit": {"action": " sell "}}, {"exit": {"action": "BUY"}}, {"exit": "SELL"}, {"trade_lifecycle_status": "open", "exit": {"action": "SELL"}}, {"status": "open"}, {}, {"trade_lifecycle_status": "", "status": "closed"}, None, [], "x"]


def _a7(fn, mod):
    return [_call(lambda b=b: fn(b)) for b in _BUNDLES] + [_call(lambda: fn())]


_LINKS = [{"status": "missing", "linkage_reason": ""}, {"status": "missing", "linkage_reason": "x"}, {"status": "ok"}, {"status": " MISSING ", "linkage_reason": "  "}, {"status": ""}, {"linkage_reason": "r"}, {}, None, [], {"status": "ok", "linkage_reason": ""}, "x"]


def _a8(fn, mod):
    return [_call(lambda b=b: fn(b)) for b in _LINKS] + [_call(lambda: fn())]


def _owner_a5():
    def build_execution_truth_bullets(*, execution_details=None, shared_facts=None):
        return bullet_owner.build_execution_truth_bullets(execution_details=execution_details, shared_facts=shared_facts, facade=et)

    return build_execution_truth_bullets


# key -> (scenario, wrapper module, wrapper name, owner callable factory, module whose globals are patched)
CASES = {
    "a1": (_a1, et, "_clip", lambda: et_scalar._clip),
    "a2": (_a2, et, "_fmt_price", lambda: et_scalar._fmt_price),
    "a3": (_a3, et, "_fmt_pct", lambda: et_scalar._fmt_pct),
    "a4": (_a4, et, "_is_available", lambda: et_scalar._is_available),
    "a5": (_a5, et, "build_execution_truth_bullets", lambda: _owner_a5()),
    "a6": (_a6, pr, "_safe_float", lambda: pr_scalar._safe_float),
    "a7": (_a7, pr, "_is_closed_trade", lambda: pr_trade._is_closed_trade),
    "a8": (_a8, pr, "_linkage_surface_present", lambda: pr_trade._linkage_surface_present),
}
OWNER_MODULES = {"a1": et_scalar, "a2": et_scalar, "a3": et_scalar, "a4": et_scalar, "a5": bullet_owner, "a6": pr_scalar, "a7": pr_trade, "a8": pr_trade}


class Test(unittest.TestCase):
    def _parity(self, key):
        scenario, mod, name, owner_factory = CASES[key]
        a = scenario(getattr(mod, name), mod)
        b = scenario(owner_factory(), mod)
        self.assertEqual(json.dumps(a, default=repr), json.dumps(b, default=repr))
        self.assertEqual(_h(a), GOLDENS[key])
        self._thin(mod, name, OWNER_MODULES[key])
        return a

    def _thin(self, mod, name, owner_mod):
        fn = ast.parse(inspect.getsource(getattr(mod, name))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import " + mod.__name__.split(".")[-1], inspect.getsource(owner_mod))

    def test_a1_clip(self):
        out = self._parity("a1")
        self.assertEqual(self._get(et._clip, "  ABC  ", max_len=2), "AB")
        self.assertEqual(self._get(et._clip, None), "")
        self.assertEqual(self._get(et._clip, "abcdef", max_len=-1), "abcde")
        self.assertEqual(len(out), 23)

    def test_a2_fmt_price(self):
        self._parity("a2")
        self.assertEqual(et._fmt_price("123.456"), "123.46")
        self.assertEqual(et._fmt_price(None), "-")
        self.assertEqual(et._fmt_price("bad"), "bad")

    def test_a3_fmt_pct(self):
        self._parity("a3")
        self.assertEqual(et._fmt_pct(0.125), "12.50%")
        self.assertEqual(et._fmt_pct(None), "-")
        self.assertEqual(et._fmt_pct("bad"), "bad")

    def test_a4_is_available(self):
        self._parity("a4")
        self.assertIs(et._is_available("not_available"), False)
        self.assertIs(et._is_available("0"), True)
        self.assertIs(et._is_available(None), False)

    def test_a5_build_execution_truth_bullets(self):
        out = self._parity("a5")
        bullets = out[0][1]
        self.assertIn("브로커 체결 기준 가격은 100.00였습니다.", bullets)
        self.assertIn("브로커 실현 손익은 -1 / -1.00% 기준으로 정리했습니다.", bullets)
        self.assertIn("매수가와 매도가가 같았고, 손익은 가격 변동이 아니라 수수료와 세금에서 발생했습니다.", bullets)
        self.assertEqual(out[4], ["ok", []])
        self.assertEqual(out[-1][0], "ok")

    def test_a6_safe_float(self):
        self._parity("a6")
        self.assertEqual(pr._safe_float("1.25"), 1.25)
        self.assertIsNone(pr._safe_float(None))
        self.assertIsNone(pr._safe_float("bad"))

    def test_a7_is_closed_trade(self):
        self._parity("a7")
        self.assertIs(pr._is_closed_trade({"trade_lifecycle_status": "closed"}), True)
        self.assertIs(pr._is_closed_trade({"exit": {"action": "SELL"}}), True)
        self.assertIs(pr._is_closed_trade({}), False)

    def test_a8_linkage_surface_present(self):
        self._parity("a8")
        self.assertIs(pr._linkage_surface_present({"status": "missing", "linkage_reason": ""}), False)
        self.assertIs(pr._linkage_surface_present({"status": "missing", "linkage_reason": "x"}), True)
        self.assertIs(pr._linkage_surface_present({"status": "ok"}), True)

    def test_a5_post_import_patch_seams_reach_owner(self):
        with mock.patch.object(et, "_fmt_price", lambda v: "PATCHED"):
            self.assertIn("브로커 체결 기준 가격은 PATCHED였습니다.", et.build_execution_truth_bullets(execution_details=dict(_DETAILS)))
        with mock.patch.object(et, "_clip", lambda v, **k: ""):
            self.assertNotIn("체결 truth 소스는", " ".join(et.build_execution_truth_bullets(execution_details=dict(_DETAILS))))

    @staticmethod
    def _get(fn, *a, **k):
        return fn(*a, **k)


if __name__ == "__main__":
    unittest.main()
