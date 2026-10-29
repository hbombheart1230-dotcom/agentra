"""P15 A5: reporter_feedback ``_build_confidence`` moved to reporter_feedback_summary; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as F
from libs.reporting import reporter_feedback_summary as owner

GOLDEN = ["364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "b57c4299afe3cda154124bdb96ceaf618a9d8d9cd8d2c8f6580ff26faa5fe5ca", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "b57c4299afe3cda154124bdb96ceaf618a9d8d9cd8d2c8f6580ff26faa5fe5ca", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "60d4c90eee5e731df8d3ef2891de541d2e755ff8ee9db358e26bdec49f6e0db9", "b57c4299afe3cda154124bdb96ceaf618a9d8d9cd8d2c8f6580ff26faa5fe5ca", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "364bb7082249ee9fbc5247ee49735c4246f271b82c2745a35107ddda0d7cabcc", "EXC:AttributeError"]

CONF = []
for rt in (0, 9, 10, 49, 50):
    for nb in (0, 2, 3):
        CONF.append(dict(route_analysis={"route_selected_total": {"x": rt}}, blocker_analysis=[{"count": 1}] * nb))
for closed, broker in ((0, 0), (1, 0), (1, 1), (2, 2), (3, 1), (3, 2)):
    CONF.append(dict(route_analysis={}, blocker_analysis=[], trade_report_summary={"closed_trade_count": closed, "broker_truth_count": broker}))
for cnt, nb in ((4, 1), (5, 0), (5, 1), (19, 2), (20, 1), (20, 2), (4, 4)):
    CONF.append(dict(route_analysis={}, blocker_analysis=[{"count": cnt // nb if nb else cnt}] * nb if nb else []))
CONF.append(dict(route_analysis={}, blocker_analysis=[{"count": "bad"}]))
CONF.append(dict(route_analysis={}, blocker_analysis=None))
CONF.append(dict(route_analysis={}, blocker_analysis=[1]))


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(CONF)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    kw = CONF[i]
    snap = copy.deepcopy(kw)
    assert _safe(lambda: F._build_confidence(**kw)) == GOLDEN[i]
    assert _safe(lambda: owner.build_confidence(facade=F, **kw)) == GOLDEN[i]
    assert kw == snap


def _conf(**kw):
    return F._build_confidence(**kw)


def test_threshold_boundaries():
    route = lambda n, blockers=0: dict(route_analysis={"route_selected_total": {"x": n}}, blocker_analysis=[{"count": 1}] * blockers)
    assert [_conf(**route(n, 3)) for n in (0, 9, 10, 49, 50)] == ["low", "low", "medium", "medium", "high"]
    assert _conf(**route(50, 2)) == "medium" and _conf(**route(10, 0)) == "medium"
    trade = lambda c, b: dict(route_analysis={}, blocker_analysis=[], trade_report_summary={"closed_trade_count": c, "broker_truth_count": b})
    assert [_conf(**trade(c, b)) for c, b in ((0, 0), (1, 0), (1, 1), (2, 2), (3, 1), (3, 2))] == ["low", "low", "medium", "medium", "medium", "high"]
    blk_ = lambda total, n: dict(route_analysis={}, blocker_analysis=[{"count": total // n}] * n)
    assert [_conf(**blk_(t, n)) for t, n in ((4, 1), (5, 1), (19, 2), (20, 1), (20, 2))] == ["low", "medium", "medium", "medium", "high"]


def test_original_exceptions():
    with pytest.raises(AttributeError):
        F._build_confidence(route_analysis={}, blocker_analysis=[1])
    assert F._build_confidence(route_analysis={}, blocker_analysis=None) == "low"


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(F, "_safe_total", lambda c: 60)
    assert _conf(route_analysis={}, blocker_analysis=[{"count": 1}] * 3) == "high"
    monkeypatch.setattr(F, "_safe_int", lambda v, d=0: 25)
    monkeypatch.setattr(F, "_safe_total", lambda c: 0)
    assert _conf(route_analysis={}, blocker_analysis=[{"count": 1}] * 2) == "high"            # blocker total 2*25 = 50 >= 20 with 2 blockers


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(F._build_confidence).splitlines()) <= 8
