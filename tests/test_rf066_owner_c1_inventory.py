"""RF-066 C1: scripts are classified before any public CLI is considered runnable."""

from __future__ import annotations

import ast
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_EXPECTED = {
    "scripts/examples/__init__.py": ("KEEP_PURE", set()),
    "scripts/examples/demo_m22_graph_with_hydration.py": ("TEMP_FAKE_EFFECT_REQUIRED", set()),
    "scripts/examples/demo_m22_skill_flow.py": ("TEMP_FAKE_EFFECT_REQUIRED", set()),
    "scripts/examples/demo_m7_dry_run_pipeline.py": ("TEMP_FAKE_EFFECT_REQUIRED", {"dry_run_order", "mkdir", "open"}),
    "scripts/maintenance/__init__.py": ("KEEP_PURE", set()),
    "scripts/maintenance/clean_evaluation_test_contamination.py": ("TEMP_FAKE_EFFECT_REQUIRED", {"mkdir", "open", "write_text"}),
    "scripts/maintenance/compact_q9_decision_windows.py": ("TEMP_FAKE_EFFECT_REQUIRED", {"write_text"}),
    "scripts/maintenance/organize_llm_reports.py": ("TEMP_FAKE_EFFECT_REQUIRED", set()),
    "scripts/maintenance/reconcile_intent_state_store.py": ("SAFETY_HOLD_SQLITE", {"commit", "connect", "execute", "open"}),
    "scripts/maintenance/repair_q9_day_artifacts.py": ("TEMP_FAKE_EFFECT_REQUIRED", set()),
    "scripts/maintenance/repair_trade_symbol_context.py": ("TEMP_FAKE_EFFECT_REQUIRED", set()),
    "scripts/maintenance/run_broker_trade_reconciliation.py": ("SAFETY_HOLD_BROKER", {"mkdir", "write_text"}),
    "scripts/maintenance/run_log_maintenance.py": ("TEMP_FAKE_EFFECT_REQUIRED", set()),
    "scripts/maintenance/run_report_maintenance.py": ("TEMP_FAKE_EFFECT_REQUIRED", set()),
    "scripts/maintenance/step5d_crash_reconciliation.py": ("SAFETY_HOLD_STEP5D", {"mkdir", "open"}),
    "scripts/maintenance/sync_legacy_brief_llm.py": ("TEMP_FAKE_EFFECT_REQUIRED", set()),
    "scripts/maintenance/sync_openrouter_model_catalog.py": ("TEMP_FAKE_EFFECT_REQUIRED", set()),
}
_EFFECT_NAMES = {"commit", "connect", "dry_run_order", "execute", "mkdir", "open", "write_text"}


def _effect_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
            if name in _EFFECT_NAMES:
                found.add(name)
    return found


def test_rf066_all_script_owners_have_a_nonexecuting_action_class():
    """C1: public CLIs remain non-runnable until their class allows temp/fake proof."""
    owners = {
        str(path.relative_to(_ROOT))
        for directory in ("scripts/examples", "scripts/maintenance")
        for path in (_ROOT / directory).glob("*.py")
    }
    assert owners == set(_EXPECTED)
    assert {name: _effect_names(_ROOT / name) for name in _EXPECTED} == {
        name: expected[1] for name, expected in _EXPECTED.items()
    }
