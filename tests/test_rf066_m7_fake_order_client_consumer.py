"""RF-066 C2/C3: M7 demo builds an offline request through a fake order client."""

from __future__ import annotations

import json
from types import SimpleNamespace

from scripts.examples import demo_m7_dry_run_pipeline as demo


def test_rf066_m7_demo_uses_fake_order_client_in_a_temp_working_directory(tmp_path, monkeypatch, capsys):
    calls = []

    class _FakeOrderClient:
        def dry_run_order(self, request, *, intent, risk_context, dry_run_token):
            calls.append((request, intent, risk_context, dry_run_token))
            return SimpleNamespace(
                allowed=True,
                reason="fake-dry-run",
                url="https://example.invalid/fake-order",
                method="POST",
                headers={"x-fake": "yes"},
                query={},
                body={"symbol": "005930"},
            )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(demo, "OrderClient", _FakeOrderClient)

    demo.main()

    output = json.loads(capsys.readouterr().out)
    assert output["selected_api_id"] == "ORDER_SUBMIT"
    assert output["dry_run"] == {
        "allowed": True,
        "reason": "fake-dry-run",
        "url": "https://example.invalid/fake-order",
        "method": "POST",
        "headers": {"x-fake": "yes"},
        "query": {},
        "body": {"symbol": "005930"},
    }
    assert len(calls) == 1
    request, intent, risk_context, dry_run_token = calls[0]
    assert request.method == "POST"
    assert request.path == "/uapi/domestic-stock/v1/trading/order"
    assert intent == "buy"
    assert risk_context["open_positions"] == 0
    assert dry_run_token is True
    assert (tmp_path / "data/specs/api_catalog.demo.jsonl").is_file()


def test_rf066_m7_demo_does_not_construct_an_order_client_when_plan_needs_clarification(tmp_path, monkeypatch, capsys):
    class _ClarifyingPlanner:
        def plan(self, _matches):
            return SimpleNamespace(action="ask", selected=None, reason="fake clarification", candidates=[])

    class _UnexpectedOrderClient:
        def __init__(self):
            raise AssertionError("order client must not be constructed for a non-selected plan")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(demo, "ApiPlanner", _ClarifyingPlanner)
    monkeypatch.setattr(demo, "OrderClient", _UnexpectedOrderClient)

    demo.main()

    assert "[PLAN] need clarification: fake clarification" in capsys.readouterr().out
    assert (tmp_path / "data/specs/api_catalog.demo.jsonl").is_file()
