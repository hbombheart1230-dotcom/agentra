"""Additive Strategist contract namespace: zero behavioral migration."""

from __future__ import annotations

from dataclasses import fields

from libs.contracts.agents import strategist as facade
from libs.strategies import contracts as original


def test_facade_is_the_identical_contract_not_a_copied_schema() -> None:
    for name in facade.__all__:
        assert getattr(facade, name) is getattr(original, name), name


def test_default_strategist_output_shape_stays_unchanged() -> None:
    assert facade.StrategistOutput is original.StrategistOutput
    assert fields(facade.StrategistOutput) == fields(original.StrategistOutput)
    assert facade.StrategistOutput().to_dict() == original.StrategistOutput().to_dict()


def test_coercion_preserves_additive_fields_and_normalization() -> None:
    raw = {
        "market_regime": "risk_off",
        "themes": ["semiconductor"],
        "scanner_bias": "leader",
        "unrecognized_future_field": {"version": 2},
    }
    result = facade.coerce_strategist_output(raw)
    assert result == original.coerce_strategist_output(raw)
    assert result["market_regime"] == "risk_off"
    assert result["unrecognized_future_field"] == {"version": 2}


def test_existing_strategy_input_and_decision_contracts_stay_compatible() -> None:
    input_dto = facade.StrategyInput(symbol="005930")
    assert input_dto.to_dict() == original.StrategyInput(symbol="005930").to_dict()
    decision_dto = facade.StrategyDecision(action="NOOP", symbol="005930")
    assert decision_dto.to_dict() == original.StrategyDecision(action="NOOP", symbol="005930").to_dict()
