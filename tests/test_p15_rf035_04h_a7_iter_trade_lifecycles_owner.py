"""P15 RF-035 (04h): symbol_trade_report._iter_trade_lifecycles moved to symbol_trade_lifecycle_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import symbol_trade_report as m
from libs.reporting import symbol_trade_lifecycle_projection as owner


def _mk(root, rel, payload):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def _both(root):
    return list(m._iter_trade_lifecycles(root)), list(owner._iter_trade_lifecycles(root, facade=m))


def _norm(bundle):
    return {"trade_id": bundle.get("trade_id"), "normalized": True}


def test_missing_root_plain_list(tmp_path):
    assert m._iter_trade_lifecycles(tmp_path) == [] and owner._iter_trade_lifecycles(tmp_path, facade=m) == []


def test_canonical_wins_and_bundle_normalized(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "_normalize_lifecycle_bundle", _norm)
    _mk(tmp_path, "trades/D/T1/lifecycle/trade_lifecycle.json", {"trade_id": "T1", "src": "canon"})
    _mk(tmp_path, "trades/D/T1/lifecycle_bundle.json", {"trade_id": "T1"})
    _mk(tmp_path, "trades/D/T2/lifecycle_bundle.json", {"trade_id": "T2"})
    _mk(tmp_path, "trades/D/T3/lifecycle_bundle.json", {})
    a, b = _both(tmp_path)
    assert a == b and [(p.name, o["trade_id"]) for p, o in a] == [("trade_lifecycle.json", "T1"), ("lifecycle_bundle.json", "T2")]
    assert a[1][1]["normalized"] is True


def test_helpers_resolved_at_iteration_time(monkeypatch, tmp_path):
    _mk(tmp_path, "trades/D/T1/lifecycle/trade_lifecycle.json", {"trade_id": "T1"})
    its = (m._iter_trade_lifecycles(tmp_path), owner._iter_trade_lifecycles(tmp_path, facade=m))
    monkeypatch.setattr(m, "_read_json", lambda p: {"trade_id": "PATCHED"})
    assert [[(p.name, o) for p, o in i] for i in its] == [[("trade_lifecycle.json", {"trade_id": "PATCHED"})]] * 2


def test_empty_normalized_skipped(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "_normalize_lifecycle_bundle", lambda b: {})
    _mk(tmp_path, "trades/D/T9/lifecycle_bundle.json", {"trade_id": "T9"})
    assert _both(tmp_path) == ([], [])
