"""P15 A5: alpha board ``_negative_control_candidate`` moved to canonical_negative_control; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting.alpha_research_board import canonical as c
from libs.reporting.alpha_research_board import canonical_negative_control as owner

GOLDEN = ["32c9db741c465e0f95fab2384d86ec09c142e469baef07d46fee8e8085cd42de", "32c9db741c465e0f95fab2384d86ec09c142e469baef07d46fee8e8085cd42de", "d6332c772bc3b443c80bbeb6db7c10f908cde4099e6066df9846b8de3e5bd886", "32c9db741c465e0f95fab2384d86ec09c142e469baef07d46fee8e8085cd42de", "32c9db741c465e0f95fab2384d86ec09c142e469baef07d46fee8e8085cd42de"]

NEG = [{}, {"cohort_review": {"cohorts": []}}, {"cohort_review": {"cohorts": [{"cohort_id": "OTHER", "day_count": 9}, "junk", {"cohort_id": "TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1", "day_count": 3, "largest_day_share": 0.4, "largest_symbol_share": 0.5,
        "horizons": {"+5m": {"count": 8, "win_rate": 0.3, "expectancy_pct": -0.2}}}, {"cohort_id": "TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1", "day_count": 99}]}},
       {"cohort_review": "junk"}, {"cohort_review": {"cohorts": ["x", None]}}]


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


@pytest.mark.parametrize("i", range(len(NEG)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = NEG[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: c._negative_control_candidate(payload)) == GOLDEN[i]
    assert _safe(lambda: owner.negative_control_candidate(payload, facade=c)) == GOLDEN[i]
    assert payload == snap


def test_first_matching_cohort_wins_and_fixed_fields():
    row = c._negative_control_candidate(NEG[2])
    assert row["historical"] == c.metric_snapshot({"count": 8, "win_rate": 0.3, "expectancy_pct": -0.2})
    assert row["concentration"] == {"day_count": 3, "largest_day_share": 0.4, "largest_symbol_share": 0.5}                 # not the later duplicate (day_count 99)
    assert list(row) == ["candidate_id", "target_horizon", "source_status", "board_bucket", "historical", "validation", "prospective", "concentration", "evidence_note", "next_action", "source_keys"]
    assert (row["source_status"], row["board_bucket"], row["target_horizon"], row["source_keys"]) == ("NEGATIVE_CONTROL", "OBSERVE_FIXED", "+5m", ["short_alpha_discriminator"])
    assert row["evidence_note"] == "거래대금·거래량만 높은 후보가 충분한 구분자인지 확인하는 고정 음성 대조군이다."
    default = c._negative_control_candidate({})
    assert default["historical"] == c.metric_snapshot({}) and default["concentration"] == {"day_count": None, "largest_day_share": None, "largest_symbol_share": None}


def test_facade_metric_snapshot_and_mapping_use_time_patches(monkeypatch):
    seen = []
    monkeypatch.setattr(c, "metric_snapshot", lambda v: (seen.append(v), "SNAP")[1])
    assert c._negative_control_candidate(NEG[2])["historical"] == "SNAP" and seen == [{"count": 8, "win_rate": 0.3, "expectancy_pct": -0.2}]
    real = c.mapping
    count = []
    monkeypatch.setattr(c, "mapping", lambda v: (count.append(1), real(v))[1])
    c._negative_control_candidate(NEG[2])
    assert len(count) >= 5


def test_owner_does_not_import_the_source_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from .c import" not in src and "import c\n" not in src
    assert len(inspect.getsource(c._negative_control_candidate).splitlines()) <= 3
