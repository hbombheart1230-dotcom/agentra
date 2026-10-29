"""P15 C02-5: StateStore keeps newer broker truth and replaces atomically; temp files never linger. Tmp root only."""
from __future__ import annotations

import copy
import hashlib
import json

import pytest

from libs.storage import state_store as ss

NEW = "2026-10-29T10:00:00Z"
OLD = "2026-10-29T09:00:00Z"


def _marker(ts, authoritative=True):
    return {"authoritative": authoritative, "generated_at": ts}


def _write(path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tmps(root):
    return [p.name for p in root.iterdir() if ".tmp." in p.name]


def test_newer_current_truth_overrides_protected_keys_but_not_general_keys(tmp_path):
    path = tmp_path / "state.json"
    _write(path, {ss._BROKER_TRUTH_MARKER: _marker(NEW), "mock_positions": [{"symbol": "A"}], "open_positions": 1, "mock_cash": 5.0})
    incoming = {ss._BROKER_TRUTH_MARKER: _marker(OLD), "mock_positions": [], "open_positions": 0, "mock_cash": 99.0, "extra": "kept"}
    snap = copy.deepcopy(incoming)
    ss.StateStore(str(path)).save(incoming)
    assert incoming == snap                                                       # input dict not mutated
    out = _read(path)
    assert out["mock_positions"] == [{"symbol": "A"}] and out["open_positions"] == 1 and out[ss._BROKER_TRUTH_MARKER] == _marker(NEW)
    assert out["mock_cash"] == 99.0 and out["extra"] == "kept"
    assert _tmps(tmp_path) == []


def test_protected_key_absent_in_current_is_removed_from_merge(tmp_path):
    path = tmp_path / "state.json"
    _write(path, {ss._BROKER_TRUTH_MARKER: _marker(NEW)})
    ss.StateStore(str(path)).save({ss._BROKER_TRUTH_MARKER: _marker(OLD), "mock_positions": [{"symbol": "Z"}], "closeout_backup_liquidation": {"x": 1}})
    out = _read(path)
    assert "mock_positions" not in out and "closeout_backup_liquidation" not in out and out[ss._BROKER_TRUTH_MARKER] == _marker(NEW)


def test_older_or_non_authoritative_current_lets_incoming_values_win(tmp_path):
    path = tmp_path / "state.json"
    _write(path, {ss._BROKER_TRUTH_MARKER: _marker(OLD), "mock_positions": [{"symbol": "A"}]})
    ss.StateStore(str(path)).save({ss._BROKER_TRUTH_MARKER: _marker(NEW), "mock_positions": [{"symbol": "B"}]})
    assert _read(path)["mock_positions"] == [{"symbol": "B"}]
    _write(path, {ss._BROKER_TRUTH_MARKER: _marker(NEW, authoritative=False), "mock_positions": [{"symbol": "A"}]})
    ss.StateStore(str(path)).save({"mock_positions": [{"symbol": "C"}]})
    assert _read(path)["mock_positions"] == [{"symbol": "C"}]
    _write(path, {ss._BROKER_TRUTH_MARKER: _marker(OLD), "mock_positions": [{"symbol": "A"}]})
    ss.StateStore(str(path)).save({ss._BROKER_TRUTH_MARKER: _marker(OLD), "mock_positions": [{"symbol": "D"}]})        # equal revision -> incoming
    assert _read(path)["mock_positions"] == [{"symbol": "D"}]


@pytest.mark.parametrize("marker,rev", [(None, 0.0), ("x", 0.0), ({"authoritative": True}, 0.0), ({"authoritative": True, "generated_at": "bad"}, 0.0),
                                       ({"authoritative": False, "generated_at": NEW}, 0.0)])
def test_revision_is_zero_for_invalid_markers(marker, rev):
    assert ss._broker_truth_revision({ss._BROKER_TRUTH_MARKER: marker}) == rev
    assert ss._broker_truth_revision({}) == 0.0


def test_revision_orders_z_and_offset_timestamps():
    a = ss._broker_truth_revision({ss._BROKER_TRUTH_MARKER: _marker("2026-10-29T10:00:00Z")})
    b = ss._broker_truth_revision({ss._BROKER_TRUTH_MARKER: _marker("2026-10-29T18:59:59+09:00")})
    assert a > b > 0


def test_corrupt_json_loads_defaults_and_save_writes_valid_json(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{not json", encoding="utf-8")
    store = ss.StateStore(str(path))
    st = store.load()
    assert st["mock_positions"] == [] and st["last_order_epoch"] == 0 and st["last_trade_side"] == ""
    store.save({"a": 1})
    assert _read(path) == {"a": 1} and _tmps(tmp_path) == []
    path.write_text("[1,2]", encoding="utf-8")
    assert store.load()["mock_cash"] == 0.0
    assert ss.StateStore(str(tmp_path / "missing.json")).load()["open_positions"] == 0


def test_permission_error_then_success_retries_with_fake_sleep_and_leaves_no_tmp(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    _write(path, {"v": "old"})
    real_replace = ss.os.replace
    calls, sleeps, fsyncs = [], [], []

    def flaky(src, dst):
        calls.append(str(src))
        if len(calls) == 1:
            raise PermissionError("locked")
        return real_replace(src, dst)

    monkeypatch.setattr(ss.os, "replace", flaky)
    monkeypatch.setattr(ss.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(ss.os, "fsync", lambda fd: fsyncs.append(fd))
    ss.StateStore(str(path)).save({"v": "new"})
    assert len(calls) == 2 and calls[0] == calls[1] and sleeps == [ss._REPLACE_RETRY_DELAYS_SEC[0]] and len(fsyncs) == 1
    assert _read(path) == {"v": "new"} and _tmps(tmp_path) == []


def test_all_retries_fail_raises_keeps_original_bytes_and_removes_tmp(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    _write(path, {"v": "old"})
    before = _sha(path)
    sleeps, calls = [], []

    def always(src, dst):
        calls.append(1)
        raise PermissionError("locked")

    monkeypatch.setattr(ss.os, "replace", always)
    monkeypatch.setattr(ss.time, "sleep", lambda s: sleeps.append(s))
    with pytest.raises(PermissionError):
        ss.StateStore(str(path)).save({"v": "new"})
    assert len(calls) == len(ss._REPLACE_RETRY_DELAYS_SEC) + 1 and tuple(sleeps) == ss._REPLACE_RETRY_DELAYS_SEC
    assert _sha(path) == before and _tmps(tmp_path) == []


def test_non_permission_replace_error_propagates_without_retry_and_cleans_tmp(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    _write(path, {"v": "old"})
    before = _sha(path)
    sleeps = []

    def broken(src, dst):
        raise OSError("disk")

    monkeypatch.setattr(ss.os, "replace", broken)
    monkeypatch.setattr(ss.time, "sleep", lambda s: sleeps.append(s))
    with pytest.raises(OSError, match="disk"):
        ss.StateStore(str(path)).save({"v": "new"})
    assert sleeps == [] and _sha(path) == before and _tmps(tmp_path) == []


def test_unserializable_state_raises_before_any_temp_file(tmp_path):
    path = tmp_path / "state.json"
    _write(path, {"v": "old"})
    before = _sha(path)
    with pytest.raises(TypeError):
        ss.StateStore(str(path)).save({"bad": object()})
    assert _sha(path) == before and _tmps(tmp_path) == []


def test_protected_key_set_is_pinned():
    assert ss._BROKER_TRUTH_PROTECTED_KEYS == ("mock_positions", "open_positions", "closeout_unresolved_flatten_by_symbol", "closeout_backup_liquidation", "broker_truth_position_reconciliation")
