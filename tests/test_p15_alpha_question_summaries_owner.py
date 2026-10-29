"""P15 A6: alpha board ``_question_summaries`` moved to canonical_question_summaries; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting.alpha_research_board import canonical as c
from libs.reporting.alpha_research_board import canonical_question_summaries as owner

GOLDEN = ["bb8f647d5104bee35156c384e5064d041f62f57ea5023a94438109936df144db", "87716f73cbd6592264843c49a68e445ed11c184666e114bdc0d2e35811eac7c8", "EXC:KeyError"]

QROWS = [[], [{"question_id": "A", "status": "DISCOVERY", "candidate_id": "a"}, {"question_id": "A", "status": "CLOSED", "candidate_id": "b"}, {"question_id": "A", "status": "DISCOVERY", "candidate_id": "a"},
              {"question_id": "B", "status": "REVIEW_READY", "candidate_id": "c"}, {"question_id": "zzz", "status": "CLOSED", "candidate_id": "d"}, {"question_id": "A", "status": "PROSPECTIVE", "candidate_id": "e"}, {"question_id": "C", "status": "PROMOTED", "candidate_id": "f"}],
         [{"question_id": "A", "candidate_id": "a"}]]


def _h(obj, root=None):
    text = json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr)
    if root is not None:
        text = text.replace(json.dumps(str(root))[1:-1], "/tmp/claude-0/stage2root")
    return hashlib.sha256(text.encode()).hexdigest()


def _safe(fn, root=None):
    try:
        return _h(fn(), root)
    except Exception as exc:
        return "EXC:" + type(exc).__name__


def _tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(root).rglob("*")) if p.is_file()}


@pytest.mark.parametrize("i", range(len(QROWS)))
def test_wrapper_and_owner_match_pre_move_golden_and_rows_unchanged(i):
    rows = QROWS[i]
    snap = copy.deepcopy(rows)
    assert _safe(lambda: c._question_summaries(rows)) == GOLDEN[i]
    assert _safe(lambda: owner.question_summaries(rows, facade=c)) == GOLDEN[i]
    assert rows == snap


def test_counts_active_closed_and_question_order():
    assert [q["question_id"] for q in c._question_summaries([])] == [q["question_id"] for q in c.QUESTIONS]
    empty = c._question_summaries([])[0]
    assert empty["candidate_count"] == 0 and list(empty["status_counts"]) == list(c.ALLOWED_STATUSES) and set(empty["status_counts"].values()) == {0}
    out = {s["question_id"]: s for s in c._question_summaries(QROWS[1])}
    a = out["A"]
    assert a["candidate_count"] == 4 and a["status_counts"]["DISCOVERY"] == 2 and a["status_counts"]["CLOSED"] == 1 and a["status_counts"]["PROSPECTIVE"] == 1
    assert a["active_candidate_ids"] == ["a", "a", "e"] and a["closed_candidate_ids"] == ["b"]                           # duplicates kept, input order
    assert out["B"]["active_candidate_ids"] == ["c"] and out["C"]["active_candidate_ids"] == [] and out["C"]["status_counts"]["PROMOTED"] == 1
    assert list(a)[-4:] == ["candidate_count", "status_counts", "active_candidate_ids", "closed_candidate_ids"]


def test_missing_row_keys_keep_the_original_key_error():
    with pytest.raises(KeyError):
        c._question_summaries(QROWS[2])
    with pytest.raises(KeyError):
        owner.question_summaries(QROWS[2], facade=c)


def test_facade_constants_use_time_patch_reaches_the_owner(monkeypatch):
    monkeypatch.setattr(c, "QUESTIONS", [{"question_id": "Z", "title": "t"}])
    monkeypatch.setattr(c, "ALLOWED_STATUSES", ("CLOSED", "DISCOVERY"))
    out = c._question_summaries([{"question_id": "Z", "status": "CLOSED", "candidate_id": "x"}])
    assert out == [{"question_id": "Z", "title": "t", "candidate_count": 1, "status_counts": {"CLOSED": 1, "DISCOVERY": 0}, "active_candidate_ids": [], "closed_candidate_ids": ["x"]}]


def test_owner_does_not_import_the_source_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from .c import" not in src and "import c\n" not in src
    assert len(inspect.getsource(c._question_summaries).splitlines()) <= 3
