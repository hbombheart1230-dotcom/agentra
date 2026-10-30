"""P15 RF-035 (2156): controlled_validation_daily._rows moved to controlled_validation_daily_read_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import controlled_validation_daily as m
from libs.reporting import controlled_validation_daily_read_projection as owner


def _both(payload, key):
    return m._rows(payload, key), owner._rows(payload, key, facade=m)


def test_values_and_copies():
    payload = {"x": [{"a": 1}, 4, {"b": 2}], "y": None}
    snap = copy.deepcopy(payload)
    a, b = _both(payload, "x")
    assert a == b == [{"a": 1}, {"b": 2}]
    a[0]["a"] = 99
    b[1]["b"] = 99
    assert payload == snap
    assert _both(payload, "absent") == ([], [])
    assert _both(payload, "y") == ([], [])


def test_facade_mapping_seam(monkeypatch):
    class Never:
        pass

    monkeypatch.setattr(m, "Mapping", Never)
    assert _both({"x": [{"a": 1}]}, "x") == ([], [])


def test_non_iterable_value_exception_parity():
    for fn in (lambda: m._rows({"x": 5}, "x"), lambda: owner._rows({"x": 5}, "x", facade=m)):
        with pytest.raises(TypeError):
            fn()
