"""P15 A1: alpha board ``_prospective_concentrations`` moved to builder_prospective_concentrations; tmp_path only."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting.alpha_research_board import builder as b
from libs.reporting.alpha_research_board import builder_prospective_concentrations as owner

GOLDEN = ["44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "8040df8e61edd86ac72bed10914d5fae7f9e9a0d1067ba2b178608742cab607a", "e7c70c8a3b208a76284d1865473e458153df41d09a40515d665be8dedba85d52", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"]

CONC_FILES = {
    "2026-10-19": {"observations": [{"matched": True, "candidate_id": "C1", "symbol": "A"}, {"matched": True, "candidate_id": "C1", "symbol": "A"}, {"matched": False, "candidate_id": "C1", "symbol": "B"},
                                    {"matched": True, "candidate_id": "C1", "symbol": "B", "day": "2026-10-19"}, {"matched": True, "candidate_id": "", "symbol": "Z"}, "junk", {"matched": True, "candidate_id": "C2", "symbol": "A"}]},
    "2026-10-20": {"observations": [{"matched": True, "candidate_id": "C1", "symbol": "A"}, {"matched": True, "candidate_id": "C1", "symbol": "C"}]},
    "2026-10-21": "BAD",
    "2026-10-30": {"observations": [{"matched": True, "candidate_id": "C1", "symbol": "OUT"}]},
}
CONC_CASES = [("none", {}, "2026-10-01", "2026-10-31"), ("all", CONC_FILES, "2026-10-01", "2026-10-31"), ("range", CONC_FILES, "2026-10-20", "2026-10-20"), ("empty_range", CONC_FILES, "2027-01-01", "2027-12-31")]
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


def _write(root, files):
    for day, payload in files.items():
        d = root / "evaluation/feature_mart/opening_rank1/prospective" / day
        d.mkdir(parents=True)
        (d / "rank1_candidate_shadow_daily.json").write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")


@pytest.mark.parametrize("i", range(len(CONC_CASES)))
def test_wrapper_and_owner_match_pre_move_golden_and_files_unchanged(tmp_path, i):
    _name, files, first, through = CONC_CASES[i]
    _write(tmp_path, files)
    before = _tree(tmp_path)
    assert _safe(lambda: b._prospective_concentrations(reports_root=tmp_path, first_day=first, through_day=through)) == GOLDEN[i]
    assert _safe(lambda: owner.prospective_concentrations(reports_root=tmp_path, first_day=first, through_day=through, facade=b)) == GOLDEN[i]
    assert _tree(tmp_path) == before


def test_explicit_values_dedup_range_and_deterministic_ties(tmp_path):
    assert b._prospective_concentrations(reports_root=tmp_path, first_day="2026-10-01", through_day="2026-10-31") == {}
    _write(tmp_path, CONC_FILES)
    out = b._prospective_concentrations(reports_root=tmp_path, first_day="2026-10-01", through_day="2026-10-31")
    c1 = out["C1"]
    assert c1["independent_day_symbol_count"] == 5 and c1["observed_day_count"] == 3                      # (19,A) (19,B) (20,A) (20,C) (30,OUT); duplicates and unmatched rows dropped; broken 10-21 file skipped
    assert c1["largest_day_share"] == 0.4 and c1["largest_symbol_share"] == 0.4
    assert c1["largest_day"] == "2026-10-19" and c1["largest_symbol"] == "A"                              # ties: count desc, key asc
    assert out["C2"]["independent_day_symbol_count"] == 1 and "" not in out and list(out) == ["C1", "C2"]
    assert "OUT" not in json.dumps(b._prospective_concentrations(reports_root=tmp_path, first_day="2026-10-01", through_day="2026-10-29"))
    narrowed = b._prospective_concentrations(reports_root=tmp_path, first_day="2026-10-01", through_day="2026-10-29")
    assert narrowed["C1"]["independent_day_symbol_count"] == 4                                              # range filter excludes the 10-30 file
    only20 = b._prospective_concentrations(reports_root=tmp_path, first_day="2026-10-20", through_day="2026-10-20")
    assert only20["C1"]["independent_day_symbol_count"] == 2 and "C2" not in only20


def test_facade_use_time_patches_reach_the_owner(tmp_path, monkeypatch):
    _write(tmp_path, CONC_FILES)
    seen = []
    real = b.load_json
    monkeypatch.setattr(b, "load_json", lambda path: (seen.append(path.parent.name), real(path))[1])
    b._prospective_concentrations(reports_root=tmp_path, first_day="2026-10-19", through_day="2026-10-21")
    assert seen == ["2026-10-19", "2026-10-20", "2026-10-21"]                                              # sorted glob order; out-of-range day never loaded


def test_owner_does_not_import_the_source_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from .b import" not in src and "import b\n" not in src
    assert len(inspect.getsource(b._prospective_concentrations).splitlines()) <= 7
