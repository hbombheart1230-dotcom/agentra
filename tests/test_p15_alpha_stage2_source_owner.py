"""P15 A3: alpha board ``_latest_stage2_source`` moved to canonical_stage2_source; tmp_path read-only."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting.alpha_research_board import canonical as c
from libs.reporting.alpha_research_board import canonical_stage2_source as owner

GOLDEN = ["d2ee5b2b72d89be9d09711d2717e7a0c85d17f88c6d4c3f84249ac5fb9e8e465", "0b4ed46e9c67155bcddaad811b69c871abf595e223572f4811c725749a2b5400", "d8a080f12f8946580fc50964471dd17d64d6dc48e5b51f2d806237cb4817483f", "67f5c696c5695bff88760a8faec18edddcbd9f0b026ac26511cb69ff524171f6", "d2ee5b2b72d89be9d09711d2717e7a0c85d17f88c6d4c3f84249ac5fb9e8e465"]   # computed with root /tmp/claude-0/stage2root (normalized in _h)

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


@pytest.fixture
def root(tmp_path):
    for rel, payload in STAGE2_FILES.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("i", range(len(STAGE2_THROUGH)))
def test_wrapper_and_owner_match_pre_move_golden_and_files_unchanged(root, i):
    before = _tree(root)
    assert _safe(lambda: c._latest_stage2_source(root, STAGE2_THROUGH[i]), root) == GOLDEN[i]
    assert _safe(lambda: owner.latest_stage2_source(root, STAGE2_THROUGH[i], facade=c), root) == GOLDEN[i]
    assert _tree(root) == before


def test_selection_rules(root, tmp_path_factory):
    assert c._latest_stage2_source(root, "2026-10-21")[0] == {"tag": "c20"}              # newest cumulative end_day <= cutoff
    assert c._latest_stage2_source(root, "2026-10-30")[0] == {"tag": "c25"}
    assert c._latest_stage2_source(root, "2026-09-01")[1].get("error")                   # none <= cutoff -> daily path, which does not exist
    empty = tmp_path_factory.mktemp("empty")
    assert c._latest_stage2_source(empty, "2026-10-19")[1].get("error")


def test_facade_load_json_use_time_patch_and_order(root, monkeypatch):
    seen = []
    monkeypatch.setattr(c, "load_json", lambda path: (seen.append(path.parent.name), ({"x": 1}, {"path": str(path)}))[1])
    out = c._latest_stage2_source(root, "2026-10-21")
    assert out[0] == {"x": 1} and seen == ["cumulative_20261001_20261020"]
    seen.clear()
    c._latest_stage2_source(root, "2026-09-01")
    assert seen == ["2026-09-01"]
    monkeypatch.setattr(c, "load_json", lambda path: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError):
        c._latest_stage2_source(root, "2026-10-21")


def test_owner_does_not_import_the_source_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from .c import" not in src and "import c\n" not in src
    assert len(inspect.getsource(c._latest_stage2_source).splitlines()) <= 3
