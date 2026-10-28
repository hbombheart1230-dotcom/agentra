"""RF-045: temp/fake coverage for the previously unexercised core owners."""

from __future__ import annotations

from pathlib import Path

import pytest

from libs.core.api_response import ApiResponse
from libs.core.evidence_identity import stable_evidence_id
from libs.core.http_client import HttpClient, HttpClientError
from libs.core.log_maintenance import detect_log_move_candidates
from libs.core.path_isolation import resolve_runtime_write_path
from libs.core.symbols import normalize_symbol


class _FailingSession:
    def __init__(self) -> None:
        self.calls = 0

    def request(self, **_kwargs):
        self.calls += 1
        raise RuntimeError("offline fake session")


def test_rf045_pure_and_temp_boundaries(tmp_path, monkeypatch):
    """Keep parsing, identity, paths, log inventory and HTTP failure offline."""
    error = ApiResponse.from_http(400, '{"rt_cd":"E1","msg":"bad"}')
    malformed = ApiResponse.from_http(500, "not-json")
    assert (error.ok, error.error_code, error.error_message) == (False, "E1", "bad")
    assert malformed.payload == {"_raw": "not-json"}

    assert stable_evidence_id("RF 045", {"a": 1, "generated_at": "old"}) == stable_evidence_id(
        "RF 045", {"generated_at": "new", "a": 1}
    )
    assert normalize_symbol(" A005930 ") == "005930"
    assert normalize_symbol("0082N0") == ""

    root = tmp_path / "logs"
    root.mkdir()
    (root / "offhours_probe.jsonl").write_text("{}\n", encoding="utf-8")
    candidates = detect_log_move_candidates(root)
    assert [(item.rel_path, item.category) for item in candidates] == [
        ("offhours_probe.jsonl", "dev_offhours")
    ]

    monkeypatch.setenv("TRADING_AGENT_PYTEST", "1")
    monkeypatch.setenv("TRADING_AGENT_PYTEST_ROOT", str(tmp_path / "isolated"))
    resolved = resolve_runtime_write_path("data/logs/events.jsonl")
    assert resolved == tmp_path / "isolated" / "data" / "logs" / "events.jsonl"
    assert not resolved.is_relative_to(Path.cwd())

    session = _FailingSession()
    client = HttpClient("https://example.invalid", session=session, retry_max=0)
    with pytest.raises(HttpClientError, match="offline fake session"):
        client.request("GET", "/never-network")
    assert session.calls == 1
