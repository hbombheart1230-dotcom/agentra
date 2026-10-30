"""P15: strategist_llm_summary ``_watch_scope_label_clean`` moved to strategist_llm_summary_watch_status.watch_scope_label_clean; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_watch_status as owner

GOLDEN = ["12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "67943e34d4adfbe518913fe8c8def5258042291b3fcaad75ee8f3f8553510bc7", "2f965387a21db2d607ce542f41ff89b693b4232d629d3969fd04d126ebc94939", "996ef5b60334731b36cc519047aa379b9d92fa18db9f2b8162f4fa394b590017", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "e8d66f7d8a5c50c8ba3883a43111d28581bfb81bf2ed2559aa873e3a4dfb328d", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126"]

WATCH = [{}, None, {"max_priority_rank": 3}, {"max_priority_rank": 3, "max_runner_ups": 2, "cascade_enabled": True}, {"max_priority_rank": 0, "max_runner_ups": "", "cascade_enabled": False}, {"cascade_enabled": None}, {"cascade_enabled": ""}, {"max_runner_ups": 0, "cascade_enabled": 0}, {"unrelated": 1}
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(WATCH)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = WATCH[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._watch_scope_label_clean(a)) == GOLDEN[i]
    assert _safe(lambda: owner.watch_scope_label_clean(a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_boundaries_false_and_zero_included_none_and_empty_excluded():
    f = m._watch_scope_label_clean
    assert f({}) == "" and f(None) == "" and f({"unrelated": 1}) == ""
    assert f({"max_priority_rank": 3}) == "3위까지"
    assert f({"max_priority_rank": 3, "max_runner_ups": 2, "cascade_enabled": True}) == "3위까지 / 차순위 2개 / cascade 활성"
    assert f({"max_priority_rank": 0, "max_runner_ups": "", "cascade_enabled": False}) == "0위까지 / cascade 비활성"
    assert f({"cascade_enabled": None}) == "" and f({"cascade_enabled": ""}) == "" and f({"max_runner_ups": 0, "cascade_enabled": 0}) == "차순위 0개 / cascade 비활성"


def test_normal_non_clean_variant_still_exists_separately():
    assert hasattr(m, "_watch_scope_label") and m._watch_scope_label is not m._watch_scope_label_clean
    assert owner.watch_scope_label_clean.__module__ == "libs.reporting.strategist_llm_summary_watch_status"


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._watch_scope_label_clean).splitlines()) <= 3
