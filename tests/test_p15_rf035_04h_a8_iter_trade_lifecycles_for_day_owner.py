"""P15 RF-035 (04h): symbol_trade_report._iter_trade_lifecycles_for_day moved to symbol_trade_lifecycle_projection; parity with the pre-move body."""
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


def _both(root, day):
    return list(m._iter_trade_lifecycles_for_day(root, day)), list(owner._iter_trade_lifecycles_for_day(root, day, facade=m))


def _norm(bundle):
    return {"trade_id": bundle.get("trade_id"), "normalized": True}


def test_missing_day_plain_list(tmp_path):
    assert m._iter_trade_lifecycles_for_day(tmp_path, "D") == [] and owner._iter_trade_lifecycles_for_day(tmp_path, "D", facade=m) == []


def test_dedup_and_day_strip(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "_normalize_lifecycle_bundle", _norm)
    day_root = tmp_path / "trades" / "2026-10-30"
    _mk(day_root, "T1/lifecycle/trade_lifecycle.json", {"trade_id": "T1"})
    _mk(day_root, "T1/lifecycle_bundle.json", {"trade_id": "T1"})
    _mk(day_root, "T2/lifecycle_bundle.json", {"trade_id": "T2"})
    a, b = _both(tmp_path, " 2026-10-30 ")
    assert a == b and [o["trade_id"] for p, o in a] == ["T1", "T2"]


def test_facade_resolve_seam_and_strip(monkeypatch, tmp_path):
    seen = []
    fake = tmp_path / "fakeday"
    _mk(fake, "T1/lifecycle/trade_lifecycle.json", {"trade_id": "T1"})
    monkeypatch.setattr(m, "resolve_trade_day_root", lambda root, day: (seen.append(day), fake)[1])
    a, b = _both(tmp_path, "  D  ")
    assert a == b and [o["trade_id"] for p, o in a] == ["T1"] and seen == ["D", "D"]
    monkeypatch.setattr(m, "resolve_trade_day_root", lambda root, day: tmp_path / "absent")
    assert _both(tmp_path, "D") == ([], [])


def test_helpers_resolved_at_iteration_time(monkeypatch, tmp_path):
    fake = tmp_path / "fakeday"
    _mk(fake, "T1/lifecycle_bundle.json", {"trade_id": "T1"})
    monkeypatch.setattr(m, "resolve_trade_day_root", lambda root, day: fake)
    its = (m._iter_trade_lifecycles_for_day(tmp_path, "D"), owner._iter_trade_lifecycles_for_day(tmp_path, "D", facade=m))
    monkeypatch.setattr(m, "_normalize_lifecycle_bundle", lambda b: {"late": True})
    assert [[o for p, o in i] for i in its] == [[{"late": True}]] * 2
