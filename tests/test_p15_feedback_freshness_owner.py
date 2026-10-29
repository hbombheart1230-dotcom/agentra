"""P15 A3: reporter_feedback ``_extract_freshness`` moved to reporter_feedback_freshness; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as f
from libs.reporting import reporter_feedback_freshness as owner

GOLDEN = ["f018bdbae15b8e3d84a8fd9f9a225632471bbbca38cf32b13e2e485c6f6218bb", "f018bdbae15b8e3d84a8fd9f9a225632471bbbca38cf32b13e2e485c6f6218bb", "9e226eecfbc8b9632e837bbc5f5141a2ecd18cf05b9114a2236d25a632faa89c", "48e24dfb4546928f60edd90a38c4e86dcf4f3017a64cf8f674bd9e3bce2db3a1", "fa49092a6841e89b1c971f74c96775111bf3ade0e5a16898c44d9998962e5e2c", "f018bdbae15b8e3d84a8fd9f9a225632471bbbca38cf32b13e2e485c6f6218bb"]

FRESH = [
    None, {}, {"generated_at": "2026-10-20T00:00:00Z", "source_run_count": "3", "latest_run_id": "r9", "latest_run_ts": 5},
    {"data_freshness": {"freshness_status": "stale", "x": [1]}, "generated_at": "g"}, {"data_freshness": {}, "generated_at": "g"}, {"data_freshness": "junk", "source_run_count": "bad"},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(FRESH)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = FRESH[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: f._extract_freshness(payload)) == GOLDEN[i]
    assert _safe(lambda: owner.extract_freshness(payload, facade=f)) == GOLDEN[i]
    assert payload == snap


def test_fallback_and_nested_copy_behaviour():
    unk = f._extract_freshness(None)
    assert list(unk) == ["generated_at", "source_run_count", "latest_run_id", "latest_run_ts", "freshness_status", "stale", "stale_reason", "source_window_summary"]
    assert (unk["freshness_status"], unk["stale_reason"], unk["stale"]) == ("unknown", "source_not_declared", False)
    fresh = f._extract_freshness(FRESH[2])
    assert (fresh["freshness_status"], fresh["stale_reason"], fresh["source_run_count"], fresh["latest_run_ts"]) == ("fresh", "aligned_with_source_window", 3, "5")
    nested = FRESH[3]["data_freshness"]
    out = f._extract_freshness(FRESH[3])
    assert out == nested and out is not nested and out["x"] is nested["x"]                                                        # shallow copy
    assert f._extract_freshness(FRESH[4])["generated_at"] == "g" and f._extract_freshness(FRESH[5])["source_run_count"] == 0


def test_facade_safe_int_use_time_patch_reaches_the_owner(monkeypatch):
    monkeypatch.setattr(f, "_safe_int", lambda v, d=0: 42)
    assert f._extract_freshness(FRESH[2])["source_run_count"] == 42
    assert f._extract_freshness(FRESH[3])["freshness_status"] == "stale"                                                          # nested path never consults the helper


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(f._extract_freshness).splitlines()) <= 3
