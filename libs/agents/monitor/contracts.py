"""Pure Monitor compatibility contracts for the staged P1.5.6 migration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


# Top-level keys written by ``graphs.nodes.monitor_node``.  The contract is a
# characterization boundary only: it neither evaluates a signal nor applies a
# patch to the live graph state.
MONITOR_STATE_COMPATIBILITY_KEYS = (
    "opening_rank1_controlled_probe",
    "_monitor_entry_cooldown_until",
    "selected",
    "scanner_selected_snapshot",
    "monitor_entry_cascade",
    "_monitor_exit_confirm",
    "_monitor_sell_cooldown_until",
    "_monitor_pending_exit_lock",
    "_monitor_prev_position_qty",
    "intents",
    "monitor",
    "monitor_output",
    "monitor_entry",
    "monitor_exit",
    "monitor_sizing",
    "monitor_posture",
    "monitor_threshold_snapshot",
    "monitor_state_transition",
    "monitor_no_trade_surface",
    "scanner_monitor_handoff",
    "monitor_entry_blocker_surface",
    "monitor_focus_context",
    "monitor_entry_decision_detail",
    "monitor_exit_decision_detail",
    "monitor_evaluation",
    "monitor_action_decision",
    "quant_shadow_candidates",
)


def _require_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError("Monitor role contracts require a mapping state")
    return value


@dataclass(frozen=True)
class MonitorAgentInput:
    """A shallow, read-only snapshot of the state consumed by Monitor."""

    state: Mapping[str, Any]

    @classmethod
    def from_state(cls, state: Mapping[str, Any]) -> "MonitorAgentInput":
        return cls(state=dict(_require_mapping(state)))


@dataclass(frozen=True)
class MonitorAgentResult:
    """A pure compatibility patch captured from an already-evaluated cycle."""

    state_patch: Mapping[str, Any]

    @classmethod
    def from_state(cls, state: Mapping[str, Any]) -> "MonitorAgentResult":
        source = _require_mapping(state)
        return cls(
            state_patch={key: source[key] for key in MONITOR_STATE_COMPATIBILITY_KEYS if key in source}
        )

    def as_state_patch(self) -> dict[str, Any]:
        return dict(self.state_patch)
