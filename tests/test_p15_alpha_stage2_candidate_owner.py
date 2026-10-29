"""P15 A4: alpha board ``_stage2_candidate`` moved to canonical_stage2_candidate; fake source only."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting.alpha_research_board import canonical as c
from libs.reporting.alpha_research_board import canonical_stage2_candidate as owner

GOLDEN = ["a85ea7b50fc939005c843b499308c99c93b4b37a9b35a65f09966f198e4565fd", "bf6a35c7999719e88561801a8856206953fd6cf50b0bc7e22443ce464eaa8181", "a85ea7b50fc939005c843b499308c99c93b4b37a9b35a65f09966f198e4565fd", "a85ea7b50fc939005c843b499308c99c93b4b37a9b35a65f09966f198e4565fd"]

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


SOURCE = {"path": "P", "error": None}


@pytest.mark.parametrize("i", range(len(STAGE2_PAYLOADS)))
def test_wrapper_and_owner_match_pre_move_golden_and_payload_unchanged(monkeypatch, i):
    payload = STAGE2_PAYLOADS[i]
    snap = copy.deepcopy(payload)
    monkeypatch.setattr(c, "_latest_stage2_source", lambda rr, td: (payload, SOURCE))
    assert _safe(lambda: c._stage2_candidate(Path("/x"), "2026-10-20")) == GOLDEN[i]
    assert _safe(lambda: owner.stage2_candidate(Path("/x"), "2026-10-20", facade=c)) == GOLDEN[i]
    assert payload == snap


def test_empty_and_populated_fields_and_key_order(monkeypatch):
    monkeypatch.setattr(c, "_latest_stage2_source", lambda rr, td: ({}, SOURCE))
    row, source = c._stage2_candidate(Path("/x"), "D")
    assert source is SOURCE and row["historical"]["sample_count"] == 0 and row["historical"]["win_rate"] is None and row["concentration"] == {"day_count": None, "max_single_day_share": None}
    monkeypatch.setattr(c, "_latest_stage2_source", lambda rr, td: (STAGE2_PAYLOADS[1], SOURCE))
    row, _ = c._stage2_candidate(Path("/x"), "D")
    assert list(row) == ["candidate_id", "target_horizon", "source_status", "board_bucket", "historical", "validation", "prospective", "concentration", "agent_attribution", "evidence_note", "next_action", "source_keys"]
    assert row["historical"]["sample_count"] == 4 and row["historical"]["window_count"] == 9 and row["historical"]["avg_net_return_pct"] == 0.3
    assert row["agent_attribution"]["interpretation"] == "경계 설명" and row["agent_attribution"]["average_delta_pct"] == 0.4 and row["agent_attribution"]["refresh_records"] == 10
    assert row["source_status"] == "OBSERVATION_ONLY" and row["evidence_note"] == "R2는 2차 전략가 이후 Scanner 재실행 결과이며 LLM의 명시적 종목 교체와 동일하지 않다."
    assert row["next_action"] == "재순위·후보 교체·진입 강화·no-trade 권한별 표본만 누적한다."


def test_facade_source_and_mapping_use_time_patches_reach_the_owner(monkeypatch):
    calls = []
    monkeypatch.setattr(c, "_latest_stage2_source", lambda rr, td: (calls.append((rr, td)), (STAGE2_PAYLOADS[1], SOURCE))[1])
    seen = []
    real = c.mapping
    monkeypatch.setattr(c, "mapping", lambda v: (seen.append(1), real(v))[1])
    c._stage2_candidate(Path("/root"), "2026-10-20")
    assert calls == [(Path("/root"), "2026-10-20")] and len(seen) >= 4
    monkeypatch.setattr(c, "_latest_stage2_source", lambda rr, td: (_ for _ in ()).throw(OSError("x")))
    with pytest.raises(OSError):
        c._stage2_candidate(Path("/root"), "D")


def test_owner_does_not_import_the_source_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from .c import" not in src and "import c\n" not in src
    assert len(inspect.getsource(c._stage2_candidate).splitlines()) <= 3
