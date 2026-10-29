"""RF-051 C1: exact import-surface pin for the eight libs/market owners (static AST, nothing executed).

An owner's effect capability is bounded by what it can import. Pinning the full import set (equality, not subset)
makes any new effect module (shutil, socket, subprocess, urllib, requests, sqlite3, os-level helpers ...) fail
loudly until the owner's C1 action record is revisited. ``korea_index_sanity`` must stay stdlib-pure (typing, math).
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "libs" / "market"

EXPECTED_IMPORTS = {
    "global_sentiment.py": {
        "__future__", "dataclasses", "datetime", "json", "libs.data_quality.signal_contract", "libs.market.korea_bond_yields",
        "libs.market.korea_index_sanity", "libs.market.yfinance_support", "libs.read.kiwoom_market_index_reader",
        "libs.read.krx_night_futures_reader", "math", "os", "pathlib", "time", "typing",
    },
    "korea_bond_yields.py": {"__future__", "datetime", "math", "os", "typing", "urllib.request", "xml.etree.ElementTree"},
    "korea_index_sanity.py": {"__future__", "math", "typing"},
    "opening_macro_snapshot_collector.py": {
        "__future__", "datetime", "json", "libs.market.preopen_macro_snapshot", "pathlib", "time", "typing", "zoneinfo",
    },
    "preopen_macro_snapshot.py": {
        "__future__", "json", "libs.core.settings", "libs.market.global_sentiment", "libs.market.yfinance_support", "pathlib", "typing",
    },
    "q10_index_observation_collector.py": {
        "__future__", "datetime", "json", "libs.market.q10_observation_integrity", "libs.read.kiwoom_market_index_reader",
        "os", "pathlib", "time", "typing", "zoneinfo",
    },
    "q10_observation_integrity.py": {"__future__", "contextlib", "datetime", "fcntl", "math", "msvcrt", "os", "pathlib", "tempfile", "typing"},
    "yfinance_support.py": {"__future__", "logging", "types", "typing", "yfinance"},
}

# modules that give an owner network / process / database / bulk-filesystem capability
CAPABILITY_MODULES = {"socket", "subprocess", "shutil", "sqlite3", "requests", "http", "http.client", "ftplib", "smtplib", "multiprocessing", "ctypes"}


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            found.add("." * node.level + (node.module or ""))
    return found


def test_the_owner_set_is_exactly_the_eight_pinned_files():
    actual = {p.name for p in ROOT.glob("*.py") if p.name != "__init__.py"}
    if actual != set(EXPECTED_IMPORTS):
        raise AssertionError((sorted(actual - set(EXPECTED_IMPORTS)), sorted(set(EXPECTED_IMPORTS) - actual)))


@pytest.mark.parametrize("owner", sorted(EXPECTED_IMPORTS))
def test_import_surface_is_pinned_exactly(owner):
    actual = _imports(ROOT / owner)
    expected = EXPECTED_IMPORTS[owner]
    if actual != expected:
        raise AssertionError(f"{owner}: new={sorted(actual - expected)} removed={sorted(expected - actual)}")


@pytest.mark.parametrize("owner", sorted(EXPECTED_IMPORTS))
def test_no_owner_imports_process_database_or_raw_network_capability(owner):
    bad = {m for m in _imports(ROOT / owner) if m.split(".")[0] in CAPABILITY_MODULES or m in CAPABILITY_MODULES}
    if bad:
        raise AssertionError(f"{owner}: {sorted(bad)}")


def test_only_two_owners_can_reach_the_network_and_only_one_the_kiwoom_reader_pair():
    net = {o for o, mods in EXPECTED_IMPORTS.items() if mods & {"urllib.request", "yfinance"}}
    _eq = lambda a, b: None if a == b else (_ for _ in ()).throw(AssertionError(f"{a!r} != {b!r}"))
    _eq(net, {"korea_bond_yields.py", "yfinance_support.py"})
    kiwoom = {o for o, mods in EXPECTED_IMPORTS.items() if "libs.read.kiwoom_market_index_reader" in mods}
    _eq(kiwoom, {"global_sentiment.py", "q10_index_observation_collector.py"})
    _eq(EXPECTED_IMPORTS["korea_index_sanity.py"], {"__future__", "math", "typing"})
