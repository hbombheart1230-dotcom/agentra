"""P15 RF-035: strategist_llm_evaluation._format_perf moved to strategist_llm_evaluation_formatting; parity with the pre-move body."""
from __future__ import annotations

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_formatting as owner


ROW = {"name": "x", "count": 2, "win_rate": 0.5, "avg_return_pct": 1.25}


def test_values():
    for fn in (m._format_perf, lambda r, **k: owner._format_perf(r, facade=m, **k)):
        assert fn([ROW]) == "x (2, win 50.0%, avg 1.25%)"
        assert fn([]) == "none"
        assert fn([ROW], limit=0) == "none"
        assert fn([{"name": "-"}, ROW, {"name": "y"}], limit=3) == "x (2, win 50.0%, avg 1.25%), y (None, win 0.0%, avg 0.00%)"
        assert fn([{"name": "a", "count": 1}, ROW], limit=1) == "a (1, win 0.0%, avg 0.00%)"


def test_exception_parity():
    for fn in (m._format_perf, lambda r, **k: owner._format_perf(r, facade=m, **k)):
        with pytest.raises(ValueError):
            fn([{"name": "x", "win_rate": "bad"}])
        with pytest.raises(AttributeError):
            fn(["x"])


def test_facade_text_seam(monkeypatch):
    monkeypatch.setattr(m, "_text", lambda v: "T")
    assert m._format_perf([{"name": "q"}]) == owner._format_perf([{"name": "q"}], facade=m) == "T (None, win 0.0%, avg 0.00%)"
