"""P15 RF-035: llm_artifacts classify_llm_exception moved to llm_artifacts_status_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_status_projection as owner

import pytest


@pytest.mark.parametrize("exc,expected", [
    (TimeoutError("x"), "timeout"), (RuntimeError("timed out"), "timeout"), (RuntimeError("Timeout!"), "timeout"),
    (ConnectionError("dns failure"), "network_error"), (OSError("Connection reset by peer"), "network_error"),
    (RuntimeError("temporarily unavailable"), "network_error"), (ValueError("bad"), "error"),
    (RuntimeError("timeout connection"), "timeout"), (TimeoutError(), "timeout"),
])
def test_cases(exc, expected):
    for fn in (m.classify_llm_exception, owner.classify_llm_exception):
        assert fn(exc) == expected
