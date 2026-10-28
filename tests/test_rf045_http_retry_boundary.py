"""RF-045 C2/C3: HTTP retry stays inside a fake session and preserves response data."""

from __future__ import annotations

from types import SimpleNamespace

from libs.core.http_client import HttpClient


class _FlakySession:
    def __init__(self) -> None:
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            raise TimeoutError("fake timeout")
        return SimpleNamespace(status_code=201, headers={"x-fake": "yes"}, text="created")


def test_rf045_http_client_retries_fake_timeout_then_returns_fake_response(monkeypatch):
    session = _FlakySession()
    monkeypatch.setattr("libs.core.http_client.time.sleep", lambda _seconds: None)
    client = HttpClient("https://example.invalid", session=session, retry_max=1, backoff_sec=0.0)

    url, response = client.request("post", "/orders", json_body={"symbol": "005930"})

    assert url == "https://example.invalid/orders"
    assert response is not None
    assert (response.status_code, response.headers, response.text) == (201, {"x-fake": "yes"}, "created")
    assert len(session.calls) == 2
    assert all(call["url"] == "https://example.invalid/orders" for call in session.calls)
