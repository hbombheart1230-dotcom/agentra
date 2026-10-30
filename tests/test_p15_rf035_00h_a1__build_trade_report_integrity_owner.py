"""P15 RF-035 (00h): daily_report_generator._build_trade_report_integrity moved to daily_report_generator_integrity_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import daily_report_generator as m
from libs.reporting import daily_report_generator_integrity_projection as owner


def _both(root, day, idx, ba=None):
    return m._build_trade_report_integrity(root, day, idx, ba), owner._build_trade_report_integrity(root, day, idx, ba, facade=m)


def _mk(root, day, tid, files=()):
    d = root / "trades" / day / tid / "reports"
    d.mkdir(parents=True)
    for f in files:
        (d / f).write_text("{}", encoding="utf-8")


def test_empty_index(tmp_path):
    a, b = _both(tmp_path, "2026-10-30", [])
    assert a == b
    assert list(a)[:3] and a.get("expected_trade_count") == 0 and a.get("checked_trade_count") == 0 and a.get("status") == "ok"


def test_missing_reports_and_complete(tmp_path):
    _mk(tmp_path, "D", "T1")
    _mk(tmp_path, "D", "T2", ["ai_trade_summary_input.json", "ai_trade_summary.json", "ai_trade_summary.md"])
    idx = [{"trade_id": "T1", "symbol": "005930", "status": "OPEN"}, {"trade_id": "T2", "symbol": "000660", "status": "closed"}, "x", {"trade_id": ""}]
    snap = copy.deepcopy(idx)
    a, b = _both(tmp_path, "D", idx)
    assert a == b and idx == snap
    assert a["status"] == "missing_reports" and a["missing_count"] == 1


def test_broker_closed_open_report(monkeypatch, tmp_path):
    _mk(tmp_path, "D", "T1", ["ai_trade_summary_input.json", "ai_trade_summary.json", "ai_trade_summary.md"])
    monkeypatch.setattr(m, "_broker_closed_symbols_from_alignment", lambda ba: {"005930"})
    a, b = _both(tmp_path, "D", [{"trade_id": "T1", "symbol": "005930", "status": "open"}], {"x": 1})
    assert a == b and a["broker_closed_report_open_count"] == 1


def test_facade_helper_seams(monkeypatch, tmp_path):
    seen = []
    monkeypatch.setattr(m, "_find_trade_dir", lambda r, d, t: (seen.append(t), None)[1])
    monkeypatch.setattr(m, "normalize_symbol", lambda s, allow_test_symbols=False: "SENT")
    a, b = _both(tmp_path, "D", [{"trade_id": "T9", "symbol": "x"}])
    assert a == b and seen == ["T9", "T9"] and a["missing_count"] == 1


def test_non_list_index_exception_parity(tmp_path):
    for fn in (lambda: m._build_trade_report_integrity(tmp_path, "D", None), lambda: owner._build_trade_report_integrity(tmp_path, "D", None, facade=m)):
        with pytest.raises(TypeError):
            fn()
