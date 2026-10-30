"""P15 RF-035 (23h): market_regime_rail_review._indicator moved to market_regime_rail_review_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from collections import OrderedDict

import pytest

from libs.reporting import market_regime_rail_review as m
from libs.reporting import market_regime_rail_review_scalar_projection as owner


def _both(snap, key):
    return m._indicator(snap, key), owner._indicator(snap, key, facade=m)


def test_identity_and_missing():
    row = {"change_pct": 1}
    snap = {"macro_indicators": {"indicators": {"kospi": row}}}
    a, b = _both(snap, "kospi")
    assert a is row and b is row
    assert _both(snap, "x") == ({}, {})
    assert _both({}, "kospi") == ({}, {})
    assert _both({"macro_indicators": []}, "kospi") == ({}, {})
    assert _both({"macro_indicators": {"indicators": "x"}}, "kospi") == ({}, {})
    assert _both({"macro_indicators": {"indicators": {"kospi": 5}}}, "kospi") == ({}, {})


def test_facade_mapping_seam(monkeypatch):
    od = OrderedDict(change_pct=2)
    snap = {"macro_indicators": {"indicators": {"k": od}}}
    a, b = _both(snap, "k")
    assert a is od and b is od

    class Never:
        pass

    monkeypatch.setattr(m, "Mapping", Never)
    assert _both(snap, "k") == ({}, {})
