"""P15 RF-035: strategist_llm_evaluation._closed_rows moved to strategist_llm_evaluation_rows; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_rows as owner


def test_copies_and_filter():
    rows = [{"status": "closed"}, {"status": "open"}, "x", None, {"action": "SELL"}]
    for out in (m._closed_rows(rows), owner._closed_rows(rows, facade=m)):
        assert out == [{"status": "closed"}, {"action": "SELL"}]
        assert out[0] is not rows[0]
    assert rows[0] == {"status": "closed"}


def test_one_pass_iterable_and_empty():
    for call in (lambda it: m._closed_rows(it), lambda it: owner._closed_rows(it, facade=m)):
        assert call(iter([{"status": "closed"}])) == [{"status": "closed"}]
        assert call([]) == []


def test_facade_row_closed_seam(monkeypatch):
    seen = []
    monkeypatch.setattr(m, "_row_closed", lambda row: (seen.append(row), False)[1])
    rows = [{"status": "closed"}]
    assert m._closed_rows(rows) == [] and owner._closed_rows(rows, facade=m) == []
    assert len(seen) == 2
