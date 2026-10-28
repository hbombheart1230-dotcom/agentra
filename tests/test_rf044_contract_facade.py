"""RF-044: offline public-facade contract coverage.

The contracts package is intentionally a pure DTO/serialization boundary.  This
test exercises its public facade with only in-memory state while making any
unexpected network use fail loudly.
"""

from __future__ import annotations

import importlib
import json
import socket

from libs.contracts.agent_outputs import build_commander_output_artifact


_RF044_LEAF_MODULES = (
    "agent_output_values",
    "commander_output_context",
    "commander_output_fields",
    "commander_output_policy",
    "monitor_output_context",
    "monitor_output_decision",
    "monitor_output_exit_fields",
    "monitor_output_fields",
    "monitor_output_memory_bias",
    "monitor_output_policy_fields",
    "scanner_output_context",
    "scanner_output_fields",
    "strategist_output_context",
    "strategist_output_fields",
    "strategist_output_plan_fields",
)


def test_rf044_contract_facade_imports_and_serializes_without_network(monkeypatch):
    def deny_network(*_args, **_kwargs):
        raise AssertionError("RF-044 contracts facade unexpectedly used network")

    monkeypatch.setattr(socket.socket, "connect", deny_network)
    for name in _RF044_LEAF_MODULES:
        module = importlib.import_module(f"libs.contracts.{name}")
        assert module.__name__ == f"libs.contracts.{name}"

    artifact = build_commander_output_artifact(
        {
            "run_id": "rf044-offline",
            "started_at": "2026-10-28T12:00:00+09:00",
            "runtime_phase": "preopen",
            "runtime_status": "ready",
            "path": "offline_contract_test",
        },
        mode="graph_spine",
        phase="preopen",
        path="offline_contract_test",
        status="ready",
    )

    assert artifact["schema_version"] == "agent_output.v1"
    assert artifact["agent"] == "commander"
    assert json.loads(json.dumps(artifact))["run_id"] == "rf044-offline"
