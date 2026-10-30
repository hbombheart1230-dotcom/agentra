"""P15: strategist_llm_summary _trade_strategist_input_path_for_response moved to strategist_llm_summary_path_projection.trade_strategist_input_path_for_response; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_path_projection as owner


def test_sibling_exists(tmp_path):
    (tmp_path / "run" / "reports").mkdir(parents=True)
    sib = tmp_path / "run" / "strategist_input.json"
    sib.write_text("{}")
    p = tmp_path / "run" / "reports" / "response.json"
    for fn in (m._trade_strategist_input_path_for_response, owner.trade_strategist_input_path_for_response):
        assert fn(p) == sib


def test_missing_and_other_parent_and_no_writes(tmp_path):
    (tmp_path / "run" / "reports").mkdir(parents=True)
    (tmp_path / "o" / "other").mkdir(parents=True)
    before = sorted(str(x) for x in tmp_path.rglob("*"))
    for fn in (m._trade_strategist_input_path_for_response, owner.trade_strategist_input_path_for_response):
        assert fn(tmp_path / "run" / "reports" / "response.json") is None
        assert fn(tmp_path / "o" / "other" / "response.json") is None
        assert fn(Path("response.json")) is None
    assert sorted(str(x) for x in tmp_path.rglob("*")) == before
