from pathlib import Path
import inspect

import pytest

from libs.reporting.trade_report.operator_text import operatorize_report_text
from libs.reporting.trade_report.operator_parts.exact_phrases import resolve_exact_operator_phrase
from libs.reporting.trade_report.operator_parts.context_patterns import resolve_market_selection_phrase
from libs.reporting.trade_report.operator_parts.lifecycle_patterns import resolve_lifecycle_operator_phrase


@pytest.mark.parametrize("original,expected", [
    ("Selected rank: 1", "최종 선정 순위는 1입니다."),
    ("Market regime: bull", "시장 상태는 bull입니다."),
    ("Lifecycle status: closed", "라이프사이클 상태 종결"),
    ("Quantity: 3", "수량: 3"),
    ("execution quote snapshot spread was 7.2 bps", "실행 시점 호가 스냅샷 기준 스프레드는 7.2bps였습니다."),
])
def test_operator_phrase_examples_preserve_rendering(original, expected):
    assert operatorize_report_text(original) == expected


def test_exact_mapping_is_casefolded_at_entry_boundary():
    assert resolve_exact_operator_phrase("selection") == "선정 근거를 정리했습니다."
    assert resolve_exact_operator_phrase("no-matching-phrase") is None


def test_pattern_owners_remain_bounded_and_have_no_facade_import():
    for fn in (resolve_exact_operator_phrase, resolve_market_selection_phrase,
               resolve_lifecycle_operator_phrase):
        source = Path(inspect.getsourcefile(fn)).read_text(encoding="utf-8")
        assert len(source.splitlines()) <= 350
        assert "import libs.reporting.trade_report_ai" not in source
        assert "from libs.reporting.trade_report.operator_text import" not in source
