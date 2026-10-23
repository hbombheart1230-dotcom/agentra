"""Pure Commander compatibility contracts for the staged P1.5.7 migration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


# The established graph facade writes these keys.  Capturing them here freezes
# the compatibility surface without moving routing, execution, or ownership.
COMMANDER_STATE_COMPATIBILITY_KEYS = (
    "applied_policy",
    "auto_skill_runner",
    "candidates",
    "commander_applied_policy",
    "commander_applied_policy_meta",
    "commander_applied_policy_summary",
    "commander_behavior_policy",
    "commander_decision",
    "commander_decision_frame",
    "commander_horizon_policy",
    "commander_open_position_override",
    "commander_open_position_refresh_context",
    "commander_pre_entry_exit_sweep",
    "commander_reporter_feedback_policy",
    "commander_route_observability",
    "commander_shadow_runtime",
    "decision",
    "decision_packet",
    "decision_reason",
    "execution",
    "force_refresh_strategist",
    "intents",
    "market_context",
    "monitor_entry_policy",
    "monitor_feature_hydration",
    "monitor_memory_bias",
    "path",
    "persisted_state",
    "portfolio_preflight",
    "portfolio_preflight_closeout_fallback",
    "post_exit_shadow_recap_runtime",
    "reporter_hook_results",
    "reporter_hook_summary",
    "resilience",
    "run_id",
    "runtime_fast_path",
    "runtime_phase",
    "runtime_retry_count",
    "runtime_status",
    "runtime_transition",
    "scanner_bias_context",
    "scanner_memory_bias",
    "selected",
    "snapshots",
    "strategist_output",
    "strategy_policy",
)


def _require_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError("Commander role contracts require a mapping state")
    return value


@dataclass(frozen=True)
class CommanderRuntimeInput:
    """A shallow, deterministic snapshot of Commander runtime input state."""

    state: Mapping[str, Any]

    @classmethod
    def from_state(cls, state: Mapping[str, Any]) -> "CommanderRuntimeInput":
        return cls(state=dict(_require_mapping(state)))


@dataclass(frozen=True)
class CommanderRuntimeResult:
    """A pure compatibility patch captured from an existing runtime result."""

    state_patch: Mapping[str, Any]

    @classmethod
    def from_state(cls, state: Mapping[str, Any]) -> "CommanderRuntimeResult":
        source = _require_mapping(state)
        return cls(
            state_patch={key: source[key] for key in COMMANDER_STATE_COMPATIBILITY_KEYS if key in source}
        )

    def as_state_patch(self) -> dict[str, Any]:
        return dict(self.state_patch)
