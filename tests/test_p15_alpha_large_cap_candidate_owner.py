"""P15 A2: alpha board ``_large_cap_candidate`` moved to builder_large_cap_candidate; fake review only."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting.alpha_research_board import builder as b
from libs.reporting.alpha_research_board import builder_large_cap_candidate as owner

GOLDEN = ["e50171cb03585e7a6a3155cf43ae34f32c2f8ab88b879292c2bc73474fa688f4", "624852659f3a59ada83bb19cd747c40eb9cf21f64838a6b8fc484c98e703a66f", "0b3272c8336eccc7faa395d82be81205d883fbda8a5899d7099d7e92b577cd18", "2b4de6d7e8ae6e1fcc6f64bf0413c7e1a86a0c7f4b644897257facd519431673", "d2303039916908f39fabb5da9b219ab3e24fbb3739ca3f7e2900db7b4e3d6aa6"]

LARGE_REVIEWS = [{}, {"source_count": 0}, {"source_count": 3, "invalid_sources": ["x"], "decision": "REJECTED", "base": {"window_count": "7", "count": 4, "win_rate": 0.5}},
                 {"source_count": 2, "base": {"window_count": None}}, {"source_count": 1, "base": "junk", "invalid_sources": []}]
STAGE2_FILES = {
    "evaluation/agent_effectiveness/cumulative_20261001_20261018/strategist_stage2_effectiveness_deep_dive.json": {"tag": "c18"},
    "evaluation/agent_effectiveness/cumulative_20261001_20261020/strategist_stage2_effectiveness_deep_dive.json": {"tag": "c20"},
    "evaluation/agent_effectiveness/cumulative_20261001_20261025/strategist_stage2_effectiveness_deep_dive.json": {"tag": "c25"},
    "evaluation/agent_effectiveness/2026-10-19/strategist_stage2_effectiveness_deep_dive.json": {"tag": "daily19"},
}
STAGE2_THROUGH = ["2026-10-19", "2026-10-21", "2026-10-30", "2026-09-01", "2026-10-19"]
STAGE2_PAYLOADS = [
    {}, {"changed_symbol_by_horizon": {"+30m": {"comparison_count": "4", "observation_count": 9, "after_positive_rate": 0.6, "after_average_return_pct": 0.3, "day_count": 3, "max_single_day_share": 0.5,
                                                "before_average_return_pct": -0.1, "average_delta_pct": 0.4}}, "coverage": {"refresh_records": 10, "stage2_attributable_records": 8, "same_symbol_records": 5, "changed_symbol_records": 3},
         "role_definition": {"important_boundary": "경계 설명"}},
    {"changed_symbol_by_horizon": "junk", "coverage": None}, {"changed_symbol_by_horizon": {"+30m": {"comparison_count": None}}},
]


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


@pytest.mark.parametrize("i", range(len(LARGE_REVIEWS)))
def test_wrapper_and_owner_match_pre_move_golden_and_review_unchanged(monkeypatch, i):
    review = LARGE_REVIEWS[i]
    snap = copy.deepcopy(review)
    monkeypatch.setattr(b, "build_large_cap_daily_review", lambda **kw: review)
    assert _safe(lambda: b._large_cap_candidate(Path("/x"), "2026-10-20")) == GOLDEN[i]
    assert _safe(lambda: owner.large_cap_candidate(Path("/x"), "2026-10-20", facade=b)) == GOLDEN[i]
    assert review == snap


def test_metadata_tuple_and_candidate_fields(monkeypatch):
    monkeypatch.setattr(b, "build_large_cap_daily_review", lambda **kw: LARGE_REVIEWS[2])
    row, meta = b._large_cap_candidate(Path("/x"), "2026-10-20")
    assert list(meta) == ["path", "available", "error", "through_day", "source_count"]
    assert meta == {"path": "multiple_daily_artifacts", "available": True, "error": "INVALID_DAILY_ARTIFACT", "through_day": "2026-10-20", "source_count": 3}
    assert row["candidate_id"] == "SAMSUNG_HYNIX_FIXED_UNIVERSE_TOP1" and row["source_status"] == "REJECTED" and row["prospective"]["window_count"] == 7
    assert row["evidence_note"] == "정합성 수정 이후 하루만 비교 가능하며 반복 window는 독립 거래가 아님."
    monkeypatch.setattr(b, "build_large_cap_daily_review", lambda **kw: LARGE_REVIEWS[1])
    row, meta = b._large_cap_candidate(Path("/x"), "D")
    assert meta["available"] is False and meta["error"] is None and row["source_status"] == "RUNTIME_DATA_REQUIRED" and row["prospective"]["window_count"] == 0


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    calls = []
    monkeypatch.setattr(b, "build_large_cap_daily_review", lambda **kw: (calls.append(kw), {"source_count": 1})[1])
    cand = []
    real = b._candidate
    monkeypatch.setattr(b, "_candidate", lambda **kw: (cand.append(kw), real(**kw))[1])
    b._large_cap_candidate(Path("/root"), "2026-10-20")
    assert calls == [{"reports_root": Path("/root"), "through_day": "2026-10-20"}] and len(cand) == 1 and cand[0]["source_keys"] == ["large_cap_daily"]


def test_owner_does_not_import_the_source_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from .b import" not in src and "import b\n" not in src
    assert len(inspect.getsource(b._large_cap_candidate).splitlines()) <= 5
