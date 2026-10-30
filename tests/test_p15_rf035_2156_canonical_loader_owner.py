"""P15 RF-035 (2156): strategist_llm_summary._load_canonical_strategist moved to strategist_llm_summary_canonical_loader; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_canonical_loader as owner


def _both(p):
    return m._load_canonical_strategist(p), owner._load_canonical_strategist(p, facade=m)


def _setup(tmp_path, monkeypatch, canonical=None, input_=None):
    cpath, ipath = tmp_path / "canonical.json", tmp_path / "input.json"
    if canonical is not None:
        cpath.write_text(canonical if isinstance(canonical, str) else json.dumps(canonical), encoding="utf-8")
    if input_ is not None:
        ipath.write_text(input_ if isinstance(input_, str) else json.dumps(input_), encoding="utf-8")
    monkeypatch.setattr(m, "_canonical_strategist_path_for_response", lambda p: cpath)
    monkeypatch.setattr(m, "_trade_strategist_input_path_for_response", lambda p: ipath if ipath.exists() else None)
    return cpath, ipath


def test_canonical_wins(tmp_path, monkeypatch):
    cpath, _ = _setup(tmp_path, monkeypatch, canonical={"run_id": "r"})
    a, b = _both(tmp_path / "response.json")
    assert a == b == (cpath, {"run_id": "r"})


def test_input_fallback(tmp_path, monkeypatch):
    _, ipath = _setup(tmp_path, monkeypatch, input_={"source_input": {"x": 1}, "saved_at": "t", "run_id": "r"})
    a, b = _both(tmp_path / "response.json")
    assert a == b == (ipath, {"x": 1, "generated_at": "t", "run_id": "r"})
    assert list(a[1]) == ["x", "generated_at", "run_id"]


def test_invalid_variants(tmp_path, monkeypatch):
    cpath, ipath = _setup(tmp_path, monkeypatch, canonical="{bad", input_="[1]")
    assert _both(tmp_path / "r.json") == ((ipath, {}),) * 2
    ipath.write_text("{bad", encoding="utf-8")
    assert _both(tmp_path / "r.json") == ((ipath, {}),) * 2
    ipath.write_text(json.dumps({"source_input": {}}), encoding="utf-8")
    assert _both(tmp_path / "r.json") == ((ipath, {}),) * 2
    ipath.unlink()
    assert _both(tmp_path / "r.json") == ((cpath, {}),) * 2


def test_facade_json_loads_seam(tmp_path, monkeypatch):
    cpath, _ = _setup(tmp_path, monkeypatch, canonical={"a": 1})
    monkeypatch.setattr(m.json, "loads", lambda s: {"patched": True})
    assert _both(tmp_path / "r.json") == ((cpath, {"patched": True}),) * 2
