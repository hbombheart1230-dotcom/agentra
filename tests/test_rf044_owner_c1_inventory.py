"""RF-044 C1: contracts remain an in-memory DTO boundary."""

from __future__ import annotations

import ast
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_OWNERS = {
    "agent_output_values.py",
    "agent_outputs.py",
    "commander_output_context.py",
    "commander_output_fields.py",
    "commander_output_policy.py",
    "monitor_output_context.py",
    "monitor_output_decision.py",
    "monitor_output_exit_fields.py",
    "monitor_output_fields.py",
    "monitor_output_memory_bias.py",
    "monitor_output_policy_fields.py",
    "scanner_output_context.py",
    "scanner_output_fields.py",
    "strategist_output_context.py",
    "strategist_output_fields.py",
    "strategist_output_plan_fields.py",
}
_EFFECT_NAMES = {"open", "write_text", "write_bytes", "mkdir", "unlink", "request", "connect", "run", "Popen"}


def _effect_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
            if name in _EFFECT_NAMES:
                names.add(name)
    return names


def test_rf044_all_contract_owners_are_keep_pure_dto_modules():
    """C1 classification: all 16 owners are KEEP, no direct I/O effect seam."""
    owners = {path.name for path in (_ROOT / "libs/contracts").glob("*.py")}
    assert owners == _OWNERS
    assert {_path.name: _effect_names(_path) for _path in (_ROOT / "libs/contracts").glob("*.py")} == {
        name: set() for name in _OWNERS
    }
