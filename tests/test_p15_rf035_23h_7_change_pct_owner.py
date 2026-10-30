"""P15 RF-035 (23h): market_regime_rail_review._change_pct moved to market_regime_rail_review_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import market_regime_rail_review as m
from libs.reporting import market_regime_rail_review_scalar_projection as owner


def _both(snap, key):
    return m._change_pct(snap, key), owner._change_pct(snap, key, facade=m)


def test_values():
    assert _both({"index_moves": {"kospi_pct": "1.2"}}, "kospi") == (1.2, 1.2)
    assert _both({"macro_indicators": {"indicators": {"kospi": {"change_pct": "-0.4"}}}}, "kospi") == (-0.4, -0.4)
    assert _both({}, "kospi") == (0.0, 0.0)
    assert _both({"index_moves": {"kospi_pct": None}, "macro_indicators": {"indicators": {"kospi": {"change_pct": 5}}}}, "kospi") == (0.0, 0.0)
    assert _both({"index_moves": {"other_pct": 3}, "macro_indicators": {"indicators": {"kospi": {"change_pct": 5}}}}, "kospi") == (5.0, 5.0)


def test_facade_seams(monkeypatch):
    monkeypatch.setattr(m, "_to_float", lambda v, d=0.0: 99.0)
    assert _both({"index_moves": {"k_pct": 1}}, "k") == (99.0, 99.0)
    monkeypatch.undo()
    monkeypatch.setattr(m, "_indicator", lambda s, k: {"change_pct": "7"})
    assert _both({}, "k") == (7.0, 7.0)
