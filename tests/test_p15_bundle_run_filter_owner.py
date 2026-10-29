"""P15 A4: ``_filter_rows_by_run_ids`` moved to live_execution_bundle_runner_run_filter; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import live_execution_bundle_runner as r
from libs.reporting import live_execution_bundle_runner_run_filter as owner

GOLDEN = ["4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "438d898e579b777e949d6ecb8156e83bd1abcf20dd4a84119ccef09583c1dbfd", "e874843bc3ed868b82428b11c057115b0c49ac3ee91bf761c8597c497d713a77", "EXC:AttributeError", "635908dd7b4b374211dfaff65c118196647ce439c11d9b20768b0a6bfcf7e53b", "3b0d7cba6d08a9ab012e2c7276abadc00cdc4259b4063827eb02b50d5e6c8869"]

RUN_FILTER = [
    (None, None), ([], ["r1"]), ([{"run_id": "r1", "i": 1}, {"run_id": " r2 ", "i": 2}, {"run_id": "r1", "i": 3}, {"i": 4}, None], None),
    ([{"run_id": "r1", "i": 1}, {"run_id": " r2 ", "i": 2}, {"run_id": "r1", "i": 3}, {"i": 4}], [" r1 ", "r1", "", None]),
    ([{"run_id": "r1"}, "junk"], ["r1"]), ([{"run_id": "r1"}, None], ["r1"]), ([{"run_id": 5}], [5]),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(RUN_FILTER)))
def test_wrapper_and_owner_match_pre_move_golden_and_rows_unchanged(i):
    rows, run_ids = RUN_FILTER[i]
    snap = copy.deepcopy(rows)
    assert _safe(lambda: r._filter_rows_by_run_ids(rows, run_ids)) == GOLDEN[i]
    assert _safe(lambda: owner.filter_rows_by_run_ids(rows, run_ids)) == GOLDEN[i]
    assert rows == snap


def test_no_allowed_ids_returns_same_rows_in_order_by_reference():
    rows = [{"run_id": "r1"}, {"run_id": "r2"}]
    for allowed in (None, [], ["", None, " "]):
        out = r._filter_rows_by_run_ids(rows, allowed)
        assert out == rows and out is not rows and out[0] is rows[0] and out[1] is rows[1]
    assert r._filter_rows_by_run_ids(None, None) == []


def test_strip_dedupe_filter_and_duplicate_rows_kept():
    rows = RUN_FILTER[3][0]
    out = r._filter_rows_by_run_ids(rows, RUN_FILTER[3][1])
    assert [x["i"] for x in out] == [1, 3] and out[0] is rows[0]            # " r2 " is not requested here
    assert r._filter_rows_by_run_ids([{"run_id": " r1 "}, {"run_id": "r1"}], ["r1"]) == [{"run_id": " r1 "}, {"run_id": "r1"}]


def test_generator_run_ids_are_consumed_once():
    consumed = []

    def gen():
        for x in ["r1", "r1", "r2"]:
            consumed.append(x)
            yield x
    rows = [{"run_id": "r1"}, {"run_id": "r2"}, {"run_id": "r3"}]
    assert r._filter_rows_by_run_ids(rows, gen()) == rows[:2] and consumed == ["r1", "r1", "r2"]


def test_original_exceptions_for_non_dict_rows_are_preserved():
    with pytest.raises(AttributeError):
        r._filter_rows_by_run_ids([{"run_id": "r1"}, "junk"], ["r1"])
    assert r._filter_rows_by_run_ids([{"run_id": "r1"}, None], ["r1"]) == [{"run_id": "r1"}]        # None row is tolerated via (row or {})


def test_owner_does_not_import_the_runner_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.live_execution_bundle_runner import" not in src and "import live_execution_bundle_runner\n" not in src
    assert len(inspect.getsource(r._filter_rows_by_run_ids).splitlines()) <= 6
