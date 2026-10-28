from __future__ import annotations

from libs.core.event_logger import EventLogger
from libs.core.http_client import HttpClient
from libs.core.settings import Settings


class _NoNetworkSession:
    def request(self, **_kwargs):  # pragma: no cover - a dry run must not call it
        raise AssertionError("RF-045 dry-run unexpectedly attempted HTTP")


def test_rf045_core_tmp_effects_and_dry_run_contract(tmp_path, monkeypatch):
    """Exercise only temp-file and fake-session boundaries of RF-045 owners."""
    env_file = tmp_path / "settings.env"
    env_file.write_text("KIWOOM_MODE=mock\nEVENT_LOG_PATH=" + str(tmp_path / "from-env.jsonl") + "\n", encoding="utf-8")
    monkeypatch.delenv("KIWOOM_MODE", raising=False)
    monkeypatch.delenv("EVENT_LOG_PATH", raising=False)

    settings = Settings.from_env(env_file)
    assert settings.kiwoom_mode == "mock"
    assert settings.event_log_path == str(tmp_path / "from-env.jsonl")

    log_path = tmp_path / "events.jsonl"
    logger = EventLogger(log_path)
    record = logger.log(run_id="rf045", stage="test", event="tmp", payload={"safe": True})
    assert record["payload"] == {"safe": True}
    assert logger.read_all()[0]["run_id"] == "rf045"

    client = HttpClient("https://example.invalid", session=_NoNetworkSession())
    url, response = client.request("POST", "/safe", json_body={"x": 1}, dry_run=True)
    assert url == "https://example.invalid/safe"
    assert response is None
