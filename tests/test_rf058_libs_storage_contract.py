"""RF-058 libs/storage C2/C3: ProposalStore / StateStore contracts, tmp_path only.

No operational data/State path is touched: every store points into tmp_path and
``time.sleep`` / ``os.replace`` are patched where retry behaviour is pinned.
Complements tests/test_state_store.py (roundtrip, stale-broker-truth, replace
retry) with defaults, corruption, ordering, tmp-file cleanup and the pure
helper contracts. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import libs.storage as storage_pkg
from libs.storage import state_store as ss
from libs.storage.proposal_store import ProposalStore
from libs.storage.state_store import StateStore

DEFAULT = {
    "last_order_epoch": 0, "open_positions": 0, "daily_pnl_ratio": 0.0, "mock_cash": 0.0,
    "mock_positions": [], "mock_realized_pnl": 0.0, "last_trade_side": "", "last_trade_epoch": 0,
}


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_package_init_is_empty_and_exports_nothing():
    _eq(getattr(storage_pkg, "__all__", None), None)
    _eq(Path(storage_pkg.__file__).read_text(encoding="utf-8"), "")


def test_proposal_store_creates_parent_and_appends_jsonl_in_order(tmp_path):
    p = tmp_path / "deep" / "dir" / "proposals.jsonl"
    s = ProposalStore(p)
    _eq(p.parent.is_dir(), True)
    _eq(p.exists(), False)  # constructor does not create the file
    s.save({"id": 1, "note": "한글"})
    s.save({"id": 2})
    ProposalStore(str(p)).save({"id": 3})  # str path, second instance appends
    raw = p.read_text(encoding="utf-8")
    if "한글" not in raw:
        raise AssertionError("ensure_ascii=False must keep non-ASCII text")
    _eq([json.loads(l)["id"] for l in raw.splitlines()], [1, 2, 3])


def test_proposal_store_non_serializable_raises_after_opening_file(tmp_path):
    p = tmp_path / "p.jsonl"
    s = ProposalStore(p)
    with pytest.raises(TypeError):
        s.save({"bad": object()})
    _eq(p.read_text(encoding="utf-8"), "")  # opened for append, nothing written


def test_state_store_load_defaults_for_missing_corrupt_and_non_dict(tmp_path):
    p = tmp_path / "s.json"
    st = StateStore(str(p))
    _eq(st.load(), DEFAULT)
    p.write_text("{not json", encoding="utf-8")
    _eq(st.load(), DEFAULT)
    p.write_text("[1, 2]", encoding="utf-8")
    _eq(st.load(), DEFAULT)
    # defaults are a fresh copy each call (mutation does not leak)
    a = st.load()
    a["mock_positions"].append("x")
    _eq(st.load()["mock_positions"], [])


def test_state_store_load_merges_over_defaults_and_keeps_extra_keys(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"mock_cash": 5.5, "custom": {"a": 1}}), encoding="utf-8")
    out = StateStore(p).load()
    _eq(out["mock_cash"], 5.5)
    _eq(out["custom"], {"a": 1})
    _eq(out["last_order_epoch"], 0)


def test_state_store_save_creates_dirs_pretty_prints_and_leaves_no_tmp(tmp_path):
    p = tmp_path / "a" / "b" / "s.json"
    StateStore(p).save({"한글": 1, "n": [1, 2]})
    raw = p.read_text(encoding="utf-8")
    if "한글" not in raw or "\n  " not in raw:
        raise AssertionError(raw)
    _eq(sorted(x.name for x in p.parent.iterdir()), ["s.json"])


def test_state_store_save_non_serializable_raises_before_touching_file(tmp_path):
    p = tmp_path / "s.json"
    StateStore(p).save({"v": 1})
    before = p.read_text(encoding="utf-8")
    with pytest.raises(TypeError):
        StateStore(p).save({"v": object()})
    _eq(p.read_text(encoding="utf-8"), before)
    _eq(sorted(x.name for x in tmp_path.iterdir()), ["s.json"])


def test_state_store_save_replaces_corrupt_existing_file(tmp_path):
    p = tmp_path / "s.json"
    p.write_text("garbage", encoding="utf-8")
    StateStore(p).save({"v": 2})
    _eq(json.loads(p.read_text(encoding="utf-8")), {"v": 2})


def test_replace_failure_other_than_permission_cleans_tmp_and_keeps_old(tmp_path, monkeypatch):
    p = tmp_path / "s.json"
    StateStore(p).save({"v": 1})
    monkeypatch.setattr(ss.os, "replace", lambda a, b: (_ for _ in ()).throw(OSError("disk")))
    with pytest.raises(OSError):
        StateStore(p).save({"v": 2})
    _eq(json.loads(p.read_text(encoding="utf-8")), {"v": 1})
    _eq(sorted(x.name for x in tmp_path.iterdir()), ["s.json"])


def test_replace_with_retry_delays_and_exhaustion(tmp_path, monkeypatch):
    slept, calls = [], []
    monkeypatch.setattr(ss.time, "sleep", slept.append)

    def always_locked(a, b):
        calls.append((a, b))
        raise PermissionError("locked")

    monkeypatch.setattr(ss.os, "replace", always_locked)
    with pytest.raises(PermissionError):
        ss._replace_with_retry(tmp_path / "a", tmp_path / "b")
    _eq(len(calls), len(ss._REPLACE_RETRY_DELAYS_SEC) + 1)
    _eq(tuple(slept), ss._REPLACE_RETRY_DELAYS_SEC)

    n = {"c": 0}

    def flaky(a, b):
        n["c"] += 1
        if n["c"] < 3:
            raise PermissionError("locked")

    slept.clear()
    monkeypatch.setattr(ss.os, "replace", flaky)
    ss._replace_with_retry(tmp_path / "a", tmp_path / "b")
    _eq((n["c"], slept), (3, [0.05, 0.1]))


def test_broker_truth_revision_parsing():
    rev = ss._broker_truth_revision
    _eq(rev({}), 0.0)
    _eq(rev({"broker_truth_position_reconciliation": "x"}), 0.0)
    _eq(rev({"broker_truth_position_reconciliation": {"authoritative": False, "generated_at": "2026-10-28T00:00:00Z"}}), 0.0)
    _eq(rev({"broker_truth_position_reconciliation": {"authoritative": True, "generated_at": ""}}), 0.0)
    _eq(rev({"broker_truth_position_reconciliation": {"authoritative": True, "generated_at": "garbage"}}), 0.0)
    z = rev({"broker_truth_position_reconciliation": {"authoritative": True, "generated_at": "2026-10-28T00:00:00Z"}})
    o = rev({"broker_truth_position_reconciliation": {"authoritative": True, "generated_at": "2026-10-28T00:00:00+00:00"}})
    _eq(z, o)
    if z <= 0:
        raise AssertionError(z)


def _truth(ts, positions):
    return {"broker_truth_position_reconciliation": {"authoritative": True, "generated_at": ts},
            "mock_positions": positions, "open_positions": len(positions)}


def test_preserve_newer_broker_truth_keeps_only_protected_keys():
    cur = _truth("2026-10-28T02:00:00Z", ["NEW"])
    cur["closeout_backup_liquidation"] = {"x": 1}
    stale = {**_truth("2026-10-28T01:00:00Z", ["OLD"]), "unrelated": "keep", "closeout_unresolved_flatten_by_symbol": {"S": 1}}
    out = ss._preserve_newer_broker_truth(dict(stale), cur)
    _eq((out["mock_positions"], out["open_positions"], out["unrelated"]), (["NEW"], 1, "keep"))
    _eq(out["closeout_backup_liquidation"], {"x": 1})
    if "closeout_unresolved_flatten_by_symbol" in out:  # absent in current -> removed from stale state
        raise AssertionError("protected key missing in newer truth must be dropped")
    # equal or older current truth leaves the incoming state untouched (same object)
    same = _truth("2026-10-28T01:00:00Z", ["OLD"])
    if ss._preserve_newer_broker_truth(stale, same) is not stale:
        raise AssertionError("equal revision must return the incoming state")
    if ss._preserve_newer_broker_truth(stale, {}) is not stale:
        raise AssertionError("no current truth must return the incoming state")


def test_store_save_applies_broker_truth_protection_end_to_end(tmp_path):
    p = tmp_path / "s.json"
    StateStore(p).save(_truth("2026-10-28T02:00:00Z", ["NEW"]))
    StateStore(p).save({**_truth("2026-10-28T01:00:00Z", ["OLD"]), "extra": 1})
    out = json.loads(p.read_text(encoding="utf-8"))
    _eq((out["mock_positions"], out["extra"]), (["NEW"], 1))
    StateStore(p).save(_truth("2026-10-28T03:00:00Z", ["NEWER"]))
    _eq(json.loads(p.read_text(encoding="utf-8"))["mock_positions"], ["NEWER"])
