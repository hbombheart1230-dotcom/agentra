"""P15 A5: alpha research board ``_attention_order`` moved to ``builder_attention_order`` (pure); parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting.alpha_research_board import builder as b
from libs.reporting.alpha_research_board import builder_attention_order as owner

GOLDEN = ["4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "3554d2b8a1e34099053865de8576d1460b807430ec8c6b85315c9607ba93d308", "cbd9c82c7c0334742eb2a0743ecbc29278d38186483a747d4f112677cfbf8c1c", "EXC:KeyError"]   # sha256 (or exception name) of the pre-move builder._attention_order output

ATTENTION = [
    [],
    [{"candidate_id": "b", "board_bucket": "CLOSED"}, {"candidate_id": "a", "board_bucket": "RUNTIME_VALIDATION_NEXT"}],
    [{"candidate_id": "z", "board_bucket": "OBSERVE_FIXED"}, {"candidate_id": "c", "board_bucket": "OBSERVE_FIXED"}, {"candidate_id": "m", "board_bucket": "unknown"}, {"candidate_id": "d", "board_bucket": None},
     {"candidate_id": "e", "board_bucket": "CLOSED_AFTER_SENSITIVITY_REVIEW"}, {"candidate_id": "f", "board_bucket": "DATA_REPAIR_BOUNDARY"}, {"candidate_id": "g", "board_bucket": "ACTION_REVIEW"},
     {"candidate_id": "h", "board_bucket": "BACKGROUND_RUNTIME_REQUIRED"}, {"candidate_id": "i", "board_bucket": "CLOSED_NEGATIVE_PROSPECTIVE"}],
    [{"board_bucket": "CLOSED"}],
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _run(fn, rows):
    try:
        return _h(fn(rows))
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(ATTENTION)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    rows = ATTENTION[i]
    snap = copy.deepcopy(rows)
    assert _run(b._attention_order, rows) == GOLDEN[i]
    assert _run(owner._attention_order, rows) == GOLDEN[i]
    assert rows == snap


def test_explicit_orderings():
    assert b._attention_order([]) == []
    assert b._attention_order(ATTENTION[1]) == ["a", "b"]                          # RUNTIME_VALIDATION_NEXT before CLOSED
    assert b._attention_order(ATTENTION[2]) == ["h", "g", "c", "z", "f", "e", "i", "d", "m"]   # priority order, id asc within a bucket, unknown/None (priority 9) last, id asc
    assert b._attention_order([{"candidate_id": "2", "board_bucket": "CLOSED"}, {"candidate_id": "1", "board_bucket": "CLOSED"}]) == ["1", "2"]


def test_missing_candidate_id_keeps_the_original_key_error():
    with pytest.raises(KeyError):
        b._attention_order(ATTENTION[3])
    with pytest.raises(KeyError):
        owner._attention_order(ATTENTION[3])


def test_owner_is_pure_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "facade" not in src.split('"""')[2] and "import" not in src.split('"""')[2].replace("from __future__ import annotations", "").replace("from typing import Any", "")
    assert len(inspect.getsource(b._attention_order).splitlines()) <= 3
