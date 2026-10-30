"""P15 RF-035: llm_artifacts normalize_llm_status moved to llm_artifacts_status_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_status_projection as owner

import pytest


@pytest.mark.parametrize("raw,kw,expected", [
    (" OK ", {}, "ok"), ("line_repaired", {}, "salvaged"), ("disabled", {}, "fallback"),
    ("unavailable", {}, "fallback"), ("dry_run", {}, "fallback"), ("mystery", {"default": "error"}, "error"),
    ("mystery", {}, "fallback"), (None, {"default": "x"}, "x"), ("TIMEOUT", {}, "timeout"),
    ("empty_response", {}, "empty_response"), ("parse_error", {}, "parse_error"),
])
def test_cases(raw, kw, expected):
    for fn in (m.normalize_llm_status, owner.normalize_llm_status):
        assert fn(raw, **kw) == expected
