"""P15 A6: ``_find_existing_trade_id_for_run_ids`` moved to live_execution_bundle_runner_trade_lookup; tmp_path only, read-only."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import live_execution_bundle_runner as r
from libs.reporting import live_execution_bundle_runner_trade_lookup as owner

GOLDEN = ["711b336ac7f92b3fdddb8aecd0b0689cdadc08ed6462b1349c08f37eb4f2958b", "ba5f015673422680b577045c35248e78d716521f30a17cf937bc546ac464119b", "ba5f015673422680b577045c35248e78d716521f30a17cf937bc546ac464119b", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "711b336ac7f92b3fdddb8aecd0b0689cdadc08ed6462b1349c08f37eb4f2958b", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126"]

TRADES = (("TRD_20261020_005930_02", ["r1", "r9"]), ("TRD_20261020_005930_10", ["r1"]), ("TRD_20261020_000660_01", ["r1"]), ("TRD_20261020_005930_x", ["r1"]), ("TRD_20261020_005930_03", ["rz"]))
CASES = [dict(day="2026-10-20", symbol="005930", run_ids=["r1"]), dict(day="2026-10-20", symbol="000660", run_ids=["r1"]), dict(day="2026-10-20", symbol="", run_ids=["r1"]),
         dict(day="2026-10-20", symbol="005930", run_ids=[]), dict(day="2099-01-01", symbol="005930", run_ids=["r1"]), dict(day="2026-10-20", symbol="005930", run_ids=["rz", " r9 "]),
         dict(day="2026-10-20", symbol="005930", run_ids=["nomatch"]), dict(day="2026-10-20", symbol="123456", run_ids=["r1"])]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.fixture
def root(tmp_path):
    day = tmp_path / "trades" / "2026-10-20"
    for tid, runs in TRADES:
        d = day / tid
        d.mkdir(parents=True)
        (d / "lifecycle_bundle.json").write_text(json.dumps({"linked_run_ids": runs}), encoding="utf-8")
    return tmp_path


def _tree_hash(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


@pytest.mark.parametrize("i", range(len(CASES)))
def test_wrapper_and_owner_match_pre_move_golden_and_tree_is_unchanged(root, i):
    before = _tree_hash(root)
    assert _safe(lambda: r._find_existing_trade_id_for_run_ids(reports_root=root, **CASES[i])) == GOLDEN[i]
    assert _safe(lambda: owner.find_existing_trade_id_for_run_ids(reports_root=root, facade=r, **CASES[i])) == GOLDEN[i]
    assert _tree_hash(root) == before


def test_explicit_results_sequence_ordering_and_symbol_filter(root):
    f = lambda **kw: r._find_existing_trade_id_for_run_ids(reports_root=root, **kw)
    assert f(day="2026-10-20", symbol="005930", run_ids=["r1"]) == "TRD_20261020_005930_02"             # seq 02 beats 10; non-numeric seq sorts last
    assert f(day="2026-10-20", symbol="000660", run_ids=["r1"]) == "TRD_20261020_000660_01"
    assert f(day="2026-10-20", symbol="", run_ids=["r1"]) == "TRD_20261020_000660_01"                  # no symbol filter: lowest sequence overall
    assert f(day="2026-10-20", symbol="005930", run_ids=["rz", " r9 "]) == "TRD_20261020_005930_02"
    assert f(day="2026-10-20", symbol="005930", run_ids=[]) == "" and f(day="2099-01-01", symbol="005930", run_ids=["r1"]) == ""
    assert f(day="2026-10-20", symbol="005930", run_ids=["nomatch"]) == "" and f(day="2026-10-20", symbol="123456", run_ids=["r1"]) == ""


def test_facade_helper_use_time_patches_reach_the_owner(tmp_path, monkeypatch):
    (tmp_path / "trades" / "D").mkdir(parents=True)
    class FakeDir:
        def __init__(self, name):
            self.name = name
    seen = []
    monkeypatch.setattr(r, "iter_trade_dirs", lambda day_root: [FakeDir("T_005930_9"), FakeDir("T_005930_4"), FakeDir("T_000660_1")])
    monkeypatch.setattr(r, "_existing_trade_run_ids", lambda d: (seen.append(d.name), ["r1"])[1])
    monkeypatch.setattr(r, "_trade_id_sequence", lambda tid: {"T_005930_9": 5, "T_005930_4": 5}.get(tid, 1))
    assert r._find_existing_trade_id_for_run_ids(reports_root=tmp_path, day="D", symbol="005930", run_ids=["r1"]) == "T_005930_4"      # tie on sequence -> trade_id order
    assert seen == ["T_005930_9", "T_005930_4"]
    monkeypatch.setattr(r, "normalize_symbol", lambda value, allow_test_symbols=False: "000660")
    assert r._find_existing_trade_id_for_run_ids(reports_root=tmp_path, day="D", symbol="whatever", run_ids=["r1"]) == "T_000660_1"     # patched normalize_symbol reached the owner


def test_missing_day_root_does_not_touch_the_helpers(tmp_path, monkeypatch):
    monkeypatch.setattr(r, "iter_trade_dirs", lambda root: (_ for _ in ()).throw(AssertionError("must not be called")))
    assert r._find_existing_trade_id_for_run_ids(reports_root=tmp_path / "nope", day="2026-10-20", symbol="005930", run_ids=["r1"]) == ""


def test_owner_does_not_import_the_runner_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.live_execution_bundle_runner import" not in src and "import live_execution_bundle_runner\n" not in src
    assert len(inspect.getsource(r._find_existing_trade_id_for_run_ids).splitlines()) <= 10
