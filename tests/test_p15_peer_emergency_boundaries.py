"""P15 C02-6 peer probes for the emergency SOURCE (log inventory write boundary, non-finite limit price).

These only run against an isolated checkout of the emergency tree: set ``P15_EMERGENCY_TREE`` to its root and put it first on
PYTHONPATH.  In the A tree itself (without the patch) the module is skipped so it never asserts on code A does not carry.
"""
from __future__ import annotations

import copy
import hashlib
import math
import os
from pathlib import Path

import pytest

_TREE = os.environ.get("P15_EMERGENCY_TREE", "")
if not _TREE:
    pytest.skip("P15_EMERGENCY_TREE not set (peer probe for the emergency checkout only)", allow_module_level=True)

from libs.ai import intent_schema  # noqa: E402
from libs.core import log_maintenance as lm  # noqa: E402

assert Path(lm.__file__).resolve().is_relative_to(Path(_TREE).resolve()), lm.__file__
assert Path(intent_schema.__file__).resolve().is_relative_to(Path(_TREE).resolve()), intent_schema.__file__


def _snap(root):
    out = {}
    for p in sorted(Path(root).rglob("*")):
        rel = str(p.relative_to(root))
        out[rel] = ("link", os.readlink(p)) if p.is_symlink() else ("file", hashlib.sha256(p.read_bytes()).hexdigest()) if p.is_file() else ("dir",)
    return out


def _inv(logs):
    return lm.build_log_inventory(logs)


@pytest.fixture
def env(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    outside = tmp_path / "outside_dir"
    outside.mkdir()
    (tmp_path / "outside.txt").write_text("OUTSIDE-ORIGINAL", encoding="utf-8")
    return tmp_path, logs, outside


# ---- (a) write_log_inventory ---------------------------------------------------------------------
def test_normal_temp_write_creates_exactly_the_two_catalog_files(env):
    t, logs, _ = env
    md, js = lm.write_log_inventory(logs, _inv(logs))
    assert Path(md) == logs / "dev/catalog/log_inventory_latest.md" and Path(js) == logs / "dev/catalog/log_inventory_latest.json"
    assert sorted(str(p.relative_to(logs)) for p in logs.rglob("*") if p.is_file()) == ["dev/catalog/log_inventory_latest.json", "dev/catalog/log_inventory_latest.md"]
    assert "# Log Inventory" in Path(md).read_text(encoding="utf-8")


def test_second_write_overwrites_inside_root(env):
    t, logs, _ = env
    lm.write_log_inventory(logs, _inv(logs))
    (logs / "offhours_a.txt").write_text("x", encoding="utf-8")
    lm.write_log_inventory(logs, _inv(logs))
    assert "offhours_a.txt" in (logs / "dev/catalog/log_inventory_latest.md").read_text(encoding="utf-8")


def test_dev_symlink_to_outside_dir_is_denied_and_outside_unchanged(env):
    t, logs, outside = env
    os.symlink(outside, logs / "dev")
    before = _snap(t)
    with pytest.raises(ValueError):
        lm.write_log_inventory(logs, _inv(logs))
    assert _snap(t) == before and list(outside.iterdir()) == []


def test_catalog_symlink_to_outside_dir_is_denied(env):
    t, logs, outside = env
    (logs / "dev").mkdir()
    os.symlink(outside, logs / "dev" / "catalog")
    before = _snap(t)
    with pytest.raises(ValueError):
        lm.write_log_inventory(logs, _inv(logs))
    assert _snap(t) == before and list(outside.iterdir()) == []


@pytest.mark.parametrize("which", ["json", "md"])
def test_output_file_symlink_to_outside_file_is_denied_before_any_write(env, which):
    t, logs, _ = env
    cat = logs / "dev" / "catalog"
    cat.mkdir(parents=True)
    os.symlink(t / "outside.txt", cat / f"log_inventory_latest.{which}")
    before = _snap(t)
    with pytest.raises(ValueError):
        lm.write_log_inventory(logs, _inv(logs))
    assert _snap(t) == before and (t / "outside.txt").read_text(encoding="utf-8") == "OUTSIDE-ORIGINAL"
    assert not (cat / "log_inventory_latest.json").exists() or which == "json"            # the other output was not written either


def test_dangling_symlink_to_new_outside_file_does_not_create_it(env):
    t, logs, _ = env
    cat = logs / "dev" / "catalog"
    cat.mkdir(parents=True)
    os.symlink(t / "created_outside.json", cat / "log_inventory_latest.json")
    with pytest.raises(ValueError):
        lm.write_log_inventory(logs, _inv(logs))
    assert not (t / "created_outside.json").exists()


def test_symlink_staying_inside_root_is_still_refused_as_symlink(env):
    t, logs, _ = env
    (logs / "real_dev").mkdir()
    os.symlink(logs / "real_dev", logs / "dev")
    with pytest.raises(ValueError):
        lm.write_log_inventory(logs, _inv(logs))
    assert list((logs / "real_dev").iterdir()) == []


def test_log_root_given_via_symlink_to_real_dir_is_allowed(env):
    t, logs, _ = env
    link = t / "logs_link"
    os.symlink(logs, link)
    lm.write_log_inventory(link, _inv(logs))
    assert (logs / "dev/catalog/log_inventory_latest.json").is_file()


# ---- (b) non-finite limit prices -----------------------------------------------------------------
@pytest.mark.parametrize("action", ["BUY", "SELL"])
@pytest.mark.parametrize("price", ["nan", "NaN", "inf", "-inf", "Infinity", float("nan"), float("inf"), float("-inf")])
def test_nonfinite_limit_price_becomes_noop(action, price):
    raw = {"action": action, "symbol": "005930", "qty": 1, "price": price}
    snap = copy.deepcopy(raw) if not isinstance(price, float) else dict(raw)
    out, _ = intent_schema.normalize_intent(raw)
    assert out["action"] == "NOOP" and out.get("reason") == "invalid_intent_missing_price_for_limit"
    assert out["price"] is None or math.isfinite(out["price"])
    assert out["qty"] == 0 or out["action"] == "NOOP"
    assert raw.keys() == snap.keys() and all(raw[k] == snap[k] or (isinstance(snap[k], float) and math.isnan(snap[k])) for k in raw)


@pytest.mark.parametrize("action", ["BUY", "SELL"])
def test_default_price_nonfinite_is_also_rejected(action):
    out, _ = intent_schema.normalize_intent({"action": action, "symbol": "005930", "qty": 1}, default_price=float("nan"))
    assert out["action"] == "NOOP"


@pytest.mark.parametrize("action", ["BUY", "SELL"])
def test_finite_limit_and_market_orders_unchanged(action):
    ok, _ = intent_schema.normalize_intent({"action": action, "symbol": "005930", "qty": 2, "price": "70100.5"})
    assert (ok["action"], ok["qty"], ok["price"], ok["order_type"]) == (action, 2, 70100.5, "limit")
    mk, _ = intent_schema.normalize_intent({"action": action, "symbol": "005930", "qty": 2, "order_type": "market"})
    assert (mk["action"], mk["price"], mk["order_type"]) == (action, None, "market")


def test_noop_and_other_invalid_paths_unchanged():
    n, _ = intent_schema.normalize_intent({"action": "NOOP", "price": "nan"})
    assert n["action"] == "NOOP" and n["price"] is None
    z, _ = intent_schema.normalize_intent({"action": "BUY", "symbol": "005930", "qty": 1, "price": 0})
    assert z["action"] == "NOOP" and z["reason"] == "invalid_intent_missing_price_for_limit"
    q, _ = intent_schema.normalize_intent({"action": "BUY", "symbol": "005930", "qty": 0, "price": 1})
    assert q["reason"] == "invalid_intent_missing_symbol_or_qty"
