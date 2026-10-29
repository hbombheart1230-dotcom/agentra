"""P15 A6: reporter_feedback ``_build_recommendations`` moved to reporter_feedback_recommendations; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as f
from libs.reporting import reporter_feedback_recommendations as owner

GOLDEN = ["0c1e6bd12afe949621861778a7dfacd54410f1c164febba8908622cf75a8a683", "0c1e6bd12afe949621861778a7dfacd54410f1c164febba8908622cf75a8a683", "628c6429f4c391aa3feaefb376940e1f5c955eb0590000084a290d7e955ef983", "5b9de536b6e6ee4bae4e5458cde064de98663843a8b06c786023d11717d05f58", "0c1e6bd12afe949621861778a7dfacd54410f1c164febba8908622cf75a8a683", "EXC:ValueError", "88e1203c4effe915e869743e5630cabc6edab8c8391d71bb656124f3adffd156", "EXC:TypeError"]

RECS = [
    dict(route_analysis={}, blocker_analysis=[]),
    dict(route_analysis={"monitor_only_ratio": 0.4999, "cached_strategist_ratio": 0.2499}, blocker_analysis=[]),
    dict(route_analysis={"monitor_only_ratio": 0.5, "cached_strategist_ratio": 0.25}, blocker_analysis=[]),
    dict(route_analysis={"monitor_only_ratio": 0.9, "cached_strategist_ratio": 0.9}, blocker_analysis=[{"blocker": "vwap_reclaim_fail"}], trade_report_summary={"closed_trade_count": 5, "same_price_cost_loss_count": 2, "win_count": 1, "loss_count": 3}),
    dict(route_analysis={}, blocker_analysis=[{"blocker": ""}], trade_report_summary={"closed_trade_count": 2, "win_count": 2, "loss_count": 0}),
    dict(route_analysis={"monitor_only_ratio": "x"}, blocker_analysis=[]), dict(route_analysis={"monitor_only_ratio": None}, blocker_analysis=[{"blocker": "b"}], trade_report_summary={"closed_trade_count": 1, "loss_count": 1}),
    dict(route_analysis={"monitor_only_ratio": [1]}, blocker_analysis=[]),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(RECS)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    args = RECS[i]
    snap = copy.deepcopy(args)
    assert _safe(lambda: f._build_recommendations(**args)) == GOLDEN[i]
    assert _safe(lambda: owner.build_recommendations(facade=f, **args)) == GOLDEN[i]
    assert args == snap


BALANCED = "Route and blocker mix look balanced; continue observing for stable multi-session patterns before changing strategy."


def test_default_boundaries_and_cap():
    assert f._build_recommendations(**RECS[0]) == [BALANCED]
    assert f._build_recommendations(**RECS[1]) == [BALANCED]                                                                      # 0.4999 / 0.2499 below thresholds
    two = f._build_recommendations(**RECS[2])
    assert len(two) == 2 and two[0].startswith("Monitor-only share is high") and two[1].startswith("Cached strategist reuse is elevated")
    full = f._build_recommendations(**RECS[3])
    assert len(full) == 4 and full[2] == "Top blocker is vwap_reclaim_fail; inspect whether this gate is dominating no-trade outcomes."          # monitor, cached, top blocker, reclaim -> trade items cut by [:4]
    assert full[3].startswith("VWAP reclaim-related failures are prominent")
    loss = f._build_recommendations(**RECS[4])
    assert loss == [BALANCED]                                                                                                     # blank blocker name and win >= loss adds nothing


def test_malformed_numeric_original_exceptions():
    with pytest.raises(ValueError):
        f._build_recommendations(**RECS[5])
    with pytest.raises(TypeError):
        f._build_recommendations(**RECS[7])
    both = f._build_recommendations(**RECS[6])
    assert len(both) == 2 and both[0].startswith("Top blocker is b;") and both[1].startswith("Same-day closed trades are loss-heavy")


def test_facade_safe_int_use_time_patch_reaches_the_owner(monkeypatch):
    monkeypatch.setattr(f, "_safe_int", lambda v, d=0: 5)
    out = f._build_recommendations(route_analysis={}, blocker_analysis=[], trade_report_summary={"closed_trade_count": 1})
    assert out[0].startswith("Same-price round trips produced fee/tax drag")


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(f._build_recommendations).splitlines()) <= 8
