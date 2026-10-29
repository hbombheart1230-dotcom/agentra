"""P15 A6: alpha board ``_btc_woori`` moved to builder_btc_woori; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting.alpha_research_board import builder as b
from libs.reporting.alpha_research_board import builder_btc_woori as owner

GOLDEN = ["de297d6693980d48fece7e5cd26e3f135ea6c32fe200653e4ee7291efd69a68d", "32effdd2e1905a9002116b8ce4a8cc19247833d774d98604fbc29a6d30828184", "73c7a98f2e0a8d2d939eede46b3de169e2793ad1eeac0f715267ae8e4d36bde6", "de297d6693980d48fece7e5cd26e3f135ea6c32fe200653e4ee7291efd69a68d"]

BTC = [
    {},
    {"conclusion": "OBSERVE", "episode_horizons": [{"horizon": "+5m", "real_net": {"count": 1}}, {"horizon": "+30m", "real_net": {"count": 5, "win_rate": 0.6, "expectancy_pct": 0.3}}, {"horizon": "+60m", "real_net": {"count": 9}}]},
    {"conclusion": "REJECTED", "episode_horizons": "junk"},
    {"episode_horizons": [None, "x", {"horizon": "+30m"}]},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(BTC)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = BTC[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: b._btc_woori(payload)) == GOLDEN[i]
    assert _safe(lambda: owner._btc_woori(payload, facade=b)) == GOLDEN[i]
    assert payload == snap


def test_default_status_and_plus_30m_real_net_selection():
    d = b._btc_woori({})
    assert d["candidate_id"] == "BTC_WOORI_V2_ONLY_LOCAL_CONFIRMATION" and d["source_status"] == "INSUFFICIENT_EVIDENCE" and d["board_bucket"] == "OBSERVE_FIXED"
    assert d["track_id"] == "BTC_WOORI" and d["responsibility_if_proven"] == "BTC_WOORI_BASELINE" and d["source_keys"] == ["btc_woori_history"]
    picked = b._btc_woori(BTC[1])
    assert picked["source_status"] == "OBSERVE" and picked["historical"] == b.metric_snapshot({"count": 5, "win_rate": 0.6, "expectancy_pct": 0.3})
    assert picked["evidence_note"] == "BTC 단독과 광범위 v2는 약하고, 독립 v2-only +30분 하위군만 양수임."
    assert picked["next_action"] == "고정된 현지 확인 하위군만 prospective로 수집."
    assert b._btc_woori(BTC[2])["source_status"] == "REJECTED" and b._btc_woori(BTC[2])["historical"] == b._btc_woori({})["historical"]


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    seen = []
    monkeypatch.setattr(b, "find_horizon", lambda rows, horizon: (seen.append((rows, horizon)), {"real_net": {"count": 1}})[1])
    calls = []
    real = b._candidate
    monkeypatch.setattr(b, "_candidate", lambda **kw: (calls.append(kw), real(**kw))[1])
    out = b._btc_woori(BTC[1])
    assert seen == [(BTC[1]["episode_horizons"], "+30m")] and len(calls) == 1 and out["historical"] == b.metric_snapshot({"count": 1})


def test_owner_does_not_import_the_builder_and_wrapper_is_thin():
    assert "from .builder import" not in inspect.getsource(owner) and "import builder\n" not in inspect.getsource(owner)
    assert len(inspect.getsource(b._btc_woori).splitlines()) <= 3
