"""P15 RF-035: llm_artifacts iter_trade_dirs moved to llm_artifacts_trade_lookup; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_trade_lookup as owner


def _both(root):
    return m.iter_trade_dirs(root), owner.iter_trade_dirs(root)


def test_missing_and_file_root(tmp_path):
    f = tmp_path / "f"
    f.write_text("x")
    for r in (tmp_path / "nope", f):
        a, b = _both(r)
        assert a == b == []


def test_single_and_sorted(tmp_path):
    day = tmp_path / "trades" / "2026-10-30"
    (day / "TRD_1").mkdir(parents=True)
    a, b = _both(day)
    assert a == b == [day / "TRD_1"]
    (day / "TRD_0").mkdir()
    (day / "09" / "TRD_5").mkdir(parents=True)
    a, b = _both(day)
    assert a == b
    assert [(p.parent.name, p.name) for p in a] == sorted((p.parent.name, p.name) for p in a)
    assert {p.name for p in a} == {"TRD_5", "TRD_0", "TRD_1"}


def test_nested_special_dirs_dedupe(tmp_path):
    day = tmp_path / "d"
    (day / "TRD_2" / "brief").mkdir(parents=True)
    (day / "TRD_2" / "lifecycle").mkdir()
    a, b = _both(day)
    assert a == b == [day / "TRD_2"]


def test_marker_without_trd_prefix(tmp_path):
    day = tmp_path / "d"
    (day / "other").mkdir(parents=True)
    (day / "other" / "lifecycle_bundle.json").write_text("{}")
    a, b = _both(day)
    assert a == b == [day / "other"]


def test_owner_does_not_import_source():
    import inspect
    assert "import llm_artifacts " not in inspect.getsource(owner)
