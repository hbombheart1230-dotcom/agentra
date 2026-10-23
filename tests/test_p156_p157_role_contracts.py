from __future__ import annotations

import pytest

from libs.agents.commander import CommanderRuntimeInput, CommanderRuntimeResult
from libs.agents.commander.contracts import COMMANDER_STATE_COMPATIBILITY_KEYS
from libs.agents.monitor import MonitorAgentInput, MonitorAgentResult
from libs.agents.monitor.contracts import MONITOR_STATE_COMPATIBILITY_KEYS


def test_monitor_contracts_capture_only_the_frozen_compatibility_surface() -> None:
    state = {key: {"key": key} for key in MONITOR_STATE_COMPATIBILITY_KEYS}
    state["unrelated"] = "preserve outside patch"

    input_contract = MonitorAgentInput.from_state(state)
    result_contract = MonitorAgentResult.from_state(state)

    assert dict(input_contract.state) == state
    assert result_contract.as_state_patch() == {
        key: state[key] for key in MONITOR_STATE_COMPATIBILITY_KEYS
    }
    assert "unrelated" not in result_contract.as_state_patch()
    assert state["unrelated"] == "preserve outside patch"


def test_commander_contracts_capture_only_the_frozen_compatibility_surface() -> None:
    state = {key: {"key": key} for key in COMMANDER_STATE_COMPATIBILITY_KEYS}
    state["unrelated"] = "preserve outside patch"

    input_contract = CommanderRuntimeInput.from_state(state)
    result_contract = CommanderRuntimeResult.from_state(state)

    assert dict(input_contract.state) == state
    assert result_contract.as_state_patch() == {
        key: state[key] for key in COMMANDER_STATE_COMPATIBILITY_KEYS
    }
    assert "unrelated" not in result_contract.as_state_patch()
    assert state["unrelated"] == "preserve outside patch"


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (MonitorAgentInput.from_state, "Monitor role contracts"),
        (MonitorAgentResult.from_state, "Monitor role contracts"),
        (CommanderRuntimeInput.from_state, "Commander role contracts"),
        (CommanderRuntimeResult.from_state, "Commander role contracts"),
    ],
)
def test_role_contracts_reject_non_mapping_state(factory, message: str) -> None:
    with pytest.raises(TypeError, match=message):
        factory([])
