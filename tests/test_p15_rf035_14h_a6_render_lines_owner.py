"""P15 RF-035 (14h): controlled_mock_lane_report.render_controlled_lane_report_lines moved to controlled_lane_markdown_projection; parity with the pre-move body (stdlib unittest)."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from libs.reporting import controlled_mock_lane_report as m
from libs.reporting import controlled_lane_markdown_projection as owner

FN = "render_controlled_lane_report_lines"
GOLDEN = "dd8f63985f3174b84285c496d6125ee8d5a00714c3746f7d4ebdae6acd82d016"


def _norm(obj, root):
    return json.dumps(obj, ensure_ascii=False, default=repr).replace(str(root), "<T>")


def _h(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _patched(mod, name, value, fn):
    with mock.patch.object(mod, name, value):
        return fn()


def _ledger(root, day, rows):
    p = Path(root) / "data" / "logs" / "controlled_mock_lanes" / day / "lane_submissions.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(rows if isinstance(rows, str) else json.dumps({"submissions": rows}), encoding="utf-8")


LANE = {"lane_id": "BTC_WOORI", "symbol": "005930", "signal_id": "s1", "signal_epoch": 5, "run_id": "r1", "order_id": "0007", "score": 3, "evidence": {"a": 1}, "daily_limit": 2, "reservation": {"k": "v"}}
STRAT = {"controlled_mock_lane": True, "strategy_horizon": "intraday", "expected_hold_window": {"min_sec": 1}, "llm_used": False, "horizon_revision_allowed": False}
REPORT = {"controlled_mock_lane": {"lane_id": "Q10_INDEX", "lane_label": "L", "signal_id": "sx", "evidence": {"x": 1, "y": ""}, "expected_hold_window": {"min_sec": 1, "target_sec": 2}, "score": 0.5, "scanner_rank_applicable": False}}

def _scenarios(fn, root, mod):
    full = {"controlled_mock_lane": {"lane_id": "Q10_INDEX", "lane_label": "L", "signal_id": "sx", "evidence": {"x": 1, "y": "", "z": None}, "expected_hold_window": {"min_sec": 1, "target_sec": 2}, "score": 0.5, "scanner_rank_applicable": False, "llm_used": True, "stage3_horizon_review_allowed": True}}
    out = [
        _call(lambda: fn(REPORT)),
        _call(lambda: fn(full)),
        _call(lambda: fn({"controlled_mock_lane": {"lane_id": "Only"}})),
        _call(lambda: fn({"controlled_mock_lane": {"lane_id": "S", "score": 0, "evidence": {"y": ""}}})),
        _call(lambda: fn({})),
        _call(lambda: fn(None)),
    ]
    out.append(_patched(mod, "controlled_lane_surface_from_report", lambda r: {"lane_id": "P", "scanner_rank_applicable": True}, lambda: _call(lambda: fn({}))))
    out.append(_patched(mod, "_text", lambda v: "T", lambda: _call(lambda: fn(REPORT))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0][1][0], "* 실행 레인: **L**")
    tc.assertEqual(out[0][1][-1], "* 주문 범위: 키움 모의투자 검증 전용")
    tc.assertIn("* R3 연결: 차단.", out[0][1][-2])
    tc.assertIn("* 신호 점수: 0.5", out[1][1])
    tc.assertIn("* 고정 가설 근거: x=1", out[1][1])
    tc.assertIn("* LLM 사용: 예", out[1][1])
    tc.assertIn("* R3 연결: 허용.", out[1][1][-2])
    tc.assertEqual(out[2][1][0], "* 실행 레인: **Only**")
    tc.assertIn("* Scanner 순위: 적용", out[2][1])
    tc.assertEqual(out[4], ["ok", []])
    tc.assertEqual(out[5][0], "exc")
    tc.assertIn("* Scanner 순위: 적용", out[6][1])
    tc.assertEqual(out[7][1][0], "* 실행 레인: **T**")


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


class Test(unittest.TestCase):
    def test_wrapper_owner_and_pre_move_golden(self):
        with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
            a = _run(getattr(m, FN), Path(ta), m)
            b = _run(lambda *x, **k: getattr(owner, FN)(*x, facade=m, **k), Path(tb), m)
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDEN)

    def test_wrapper_is_thin_and_owner_does_not_import_source(self):
        import ast
        import inspect
        fn = ast.parse(inspect.getsource(getattr(m, FN))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import controlled_mock_lane_report", inspect.getsource(owner))

    def test_expected_values(self):
        with tempfile.TemporaryDirectory() as t:
            _expected(self, _scenarios(getattr(m, FN), Path(t), m), Path(t))


if __name__ == "__main__":
    unittest.main()
