"""RF-051 C1: conservative action inventory for all eight market owners.

This is intentionally static: it establishes which owners are pure KEEP
candidates and which require temp/fake effect verification.  It does not call
any market provider or touch an operational root.
"""
from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "libs" / "market"


def _names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Import):
            names.update(f"import:{alias.name}" for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(f"from:{node.module}")
    return names


def test_all_rf051_owners_have_a_conservative_effect_action_classification():
    expected = {
        "global_sentiment.py": {"try_yfinance", "write_text"},
        "korea_bond_yields.py": {"urlopen"},
        "korea_index_sanity.py": set(),
        "opening_macro_snapshot_collector.py": {"write_text", "replace", "sleep"},
        "preopen_macro_snapshot.py": {"require_yfinance", "read_text"},
        "q10_index_observation_collector.py": {"atomic_write", "KiwoomMarketIndexReader"},
        "q10_observation_integrity.py": {"replace", "open"},
        "yfinance_support.py": {"import:yfinance"},
    }
    actual = {path.name: _names(path) for path in ROOT.glob("*.py") if path.name != "__init__.py"}
    if set(actual) != set(expected):
        raise AssertionError((sorted(actual), sorted(expected)))
    for owner, effect_names in expected.items():
        missing = effect_names - actual[owner]
        if missing:
            raise AssertionError(f"{owner}: {sorted(missing)}")
    # This sole pure owner can remain a KEEP candidate; every other owner has a
    # concrete read/write/network/scheduling effect that needs its own fake or
    # tmp-root contract before C1 can become final.
    if actual["korea_index_sanity.py"] & {"Path", "open", "urlopen", "write_text", "replace", "sleep", "try_yfinance", "require_yfinance"}:
        raise AssertionError("korea_index_sanity must stay pure")
