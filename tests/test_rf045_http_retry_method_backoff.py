"""RF-045 C2/C3: fake-only retry normalizes method and preserves backoff."""

from __future__ import annotations

from types import SimpleNamespace

from libs.core.http_client import HttpClient


class _FailTwiceThenReply:
    def __init__(self) -> None:
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) < 3:
            raise TimeoutError("fake timeout")
        return SimpleNamespace(status_code=200, headers={"x-fake": "ok"}, text="ok")


def test_rf045_fake_retry_uppercases_method_and_uses_exponential_backoff(monkeypatch):
    session = _FailTwiceThenReply()
    sleeps = []
    monkeypatch.setattr("libs.core.http_client.time.sleep", sleeps.append)
    client = HttpClient("https://example.invalid", session=session, retry_max=2, backoff_sec=0.25)

    url, response = client.request("patch", "orders/1", json_body={"symbol": "005930"})

    if url != "https://example.invalid/orders/1":
        raise AssertionError(url)
    if response is None or (response.status_code, response.text) != (200, "ok"):
        raise AssertionError(response)
    if [call["method"] for call in session.calls] != ["PATCH", "PATCH", "PATCH"]:
        raise AssertionError(session.calls)
    if sleeps != [0.25, 0.5]:
        raise AssertionError(sleeps)
