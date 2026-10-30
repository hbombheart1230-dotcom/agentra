"""P15 RF-035: llm_artifacts canonical_llm_status moved to llm_artifacts_status_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_status_projection as owner

import pytest


@pytest.mark.parametrize("raw,kw,expected", [
    ("timeout", {}, "error"), ("line_repaired", {}, "salvaged"), ("partial", {}, "partial"),
    ("network_error", {}, "error"), ("parse_error", {}, "error"), ("empty_response", {}, "error"),
    ("mystery", {"default": "d"}, "d"), ("disabled", {}, "fallback"),
])
def test_cases(raw, kw, expected):
    assert m.canonical_llm_status(raw, **kw) == expected
    assert owner.canonical_llm_status(raw, facade=m, **kw) == expected


def test_facade_normalize_seam(monkeypatch):
    monkeypatch.setattr(m, "normalize_llm_status", lambda value, *, default="fallback": "network_error")
    assert m.canonical_llm_status("ok") == "error"
    assert owner.canonical_llm_status("ok", facade=m) == "error"
