"""P15 A2: ``_existing_trade_run_ids`` moved to live_execution_bundle_runner_existing_trade_run_ids; tmp_path only."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import live_execution_bundle_runner as r
from libs.reporting import live_execution_bundle_runner_existing_trade_run_ids as owner

GOLDEN = ["4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "f348b3171de8a31cc62632b8f5aef7e089db17ca1c9e14df630345e4e8ea64c3", "d33b202c020cbde1c4a7bb26d0b02e66645407dcef42c63543cff899b8f979c8", "2da346fccd21168a1e45094716700baac89e2408c6d95562d90aeb817bbfbd48"]   # sha256 of the pre-move result per fixture

TRADE_RUN = [
    ("none", None),
    ("full", {"linked_run_ids": [" r2 ", "r1", "", None], "entry": {"run_id": "r1"}, "exit": {"run_id": "r3"}, "lifecycle": {"holding": {"run_ids": ["r3", "r4", 5, " ", None]}}}),
    ("junk", {"linked_run_ids": "abc", "entry": "x", "exit": None, "lifecycle": {"holding": "y"}}),
    ("numeric", {"linked_run_ids": [1, 2.5], "entry": {"run_id": 7}}),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


def _trade_dir(tmp_path, payload):
    d = tmp_path / "trade"
    d.mkdir()
    if payload is not None:
        (d / "lifecycle_bundle.json").write_text(json.dumps(payload), encoding="utf-8")
    return d


@pytest.mark.parametrize("i", range(len(TRADE_RUN)))
def test_wrapper_and_owner_match_pre_move_golden(tmp_path, i):
    d = _trade_dir(tmp_path, TRADE_RUN[i][1])
    before = {p.name: p.read_bytes() for p in d.iterdir()}
    assert _safe(lambda: r._existing_trade_run_ids(d)) == GOLDEN[i]
    assert _safe(lambda: owner._existing_trade_run_ids(d, facade=r)) == GOLDEN[i]
    assert {p.name: p.read_bytes() for p in d.iterdir()} == before                  # files untouched


def test_explicit_values(tmp_path):
    assert r._existing_trade_run_ids(_trade_dir(tmp_path, None)) == []
    d = tmp_path / "t2"
    d.mkdir()
    (d / "lifecycle_bundle.json").write_text(json.dumps(TRADE_RUN[1][1]), encoding="utf-8")
    assert r._existing_trade_run_ids(d) == ["r2", "r1", "r3", "r4", "5"]
    d3 = tmp_path / "t3"
    d3.mkdir()
    (d3 / "lifecycle_bundle.json").write_text(json.dumps({"linked_run_ids": ["a"], "entry": {"run_id": "a"}, "exit": {"run_id": "b"}, "lifecycle": {"holding": {"run_ids": ["b", "c"]}}}), encoding="utf-8")
    assert r._existing_trade_run_ids(d3) == ["a", "b", "c"]


def test_facade_use_time_patch_reaches_the_owner(tmp_path, monkeypatch):
    d = _trade_dir(tmp_path, {"linked_run_ids": ["x"]})
    seen = []
    monkeypatch.setattr(r, "_read_json_if_exists", lambda path: (seen.append(path), {"linked_run_ids": ["patched"]})[1])
    assert r._existing_trade_run_ids(d) == ["patched"] and seen == [d / "lifecycle_bundle.json"]
    seen.clear()
    assert r._existing_trade_run_ids(tmp_path / "missing") == [] and seen == []      # no file -> reader not consulted


def test_owner_does_not_import_the_runner_and_wrapper_is_thin():
    assert "from libs.reporting.live_execution_bundle_runner import" not in inspect.getsource(owner)
    assert len(inspect.getsource(r._existing_trade_run_ids).splitlines()) <= 3
