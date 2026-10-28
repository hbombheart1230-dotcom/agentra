"""RF-031 trade_report_markdown_clean: thin wrapper helpers and scanner-line classifiers (pure, no I/O)."""
from __future__ import annotations

import pytest

from libs.reporting import trade_report_markdown_clean as m


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_append_unique_text_strips_dedups_clips_and_ignores_blanks():
    out = []
    for value in (" 반도체 ", "반도체", "", None):
        m._append_unique_text(out, value)
    m._append_unique_text(out, "x" * 200, max_len=5)
    _eq(out, ["반도체", "xx..."])


def test_append_theme_values_keeps_distinct_theme_strings_as_given():
    out = []
    m._append_theme_values(out, ["AI", "ai", " "])
    m._append_theme_values(out, "반도체,2차전지")
    m._append_theme_values(out, None)
    _eq(out, ["AI", "ai", "반도체,2차전지"])                       # case-sensitive; a comma-joined string stays one entry


def test_metadata_sources_and_nested_dict_iteration():
    report = {"a": 1, "market_context_human": {"x": 1}}
    sources = list(m._iter_trade_symbol_metadata_sources(report))
    _eq(sources[0], report)
    _eq(len(sources), 3)
    nested = list(m._iter_nested_dicts({"a": {"b": {"c": {}}}, "l": [{"z": 1}, [{"y": 2}]]}, max_depth=2))
    _eq([sorted(d) for d in nested], [["a", "l"], ["b"], ["c"], ["z"]])      # depth-limited walk: the list-in-list dict is not reached


def test_symbol_in_theme_components_and_component_themes():
    _eq(m._symbol_in_theme_components("005930", [{"symbol": "005930"}, {"stk_cd": "000660"}]), True)
    _eq(m._symbol_in_theme_components("1", []), False)
    _eq(m._symbol_in_theme_components("005930", "005930,000660"), False)       # string components are not parsed
    _eq(m._component_themes_for_symbol({}, "005930"), [])


@pytest.mark.parametrize("text,expected", [
    ("스캐너 선정과 실행 종목이 불일치합니다", True),
    ("Scanner and execution symbol mismatch", True),
    ("스캐너 불일치", False),                                              # needs an execution/entry/selected token too
    ("실행 불일치", False),                                                # and a scanner token
    ("", False), (None, False),
])
def test_scanner_execution_mismatch_line(text, expected):
    _eq(m._is_scanner_execution_mismatch_line(text), expected)


@pytest.mark.parametrize("text,expected", [
    ("스캐너 선택 종목: 삼성전자", True), ("실행 종목: 하이닉스", True),
    ("Scanner selected symbol: 005930", True), ("Execution symbol: 000660", True),
    ("스캐너가 선택한 종목", False), ("", False),
])
def test_scanner_selection_label_line(text, expected):
    _eq(m._is_scanner_selection_label_line(text), expected)


@pytest.mark.parametrize("text,expected", [
    ("", True), (None, True),
    ("상위 후보는 A입니다", True), ("스캐너 1순위 종목", True), ("총 3개", True), ("종합 점수 0.8", True),
    ("전혀 다른 문장입니다", False),
])
def test_redundant_symbol_selection_line(text, expected):
    _eq(m._is_redundant_symbol_selection_line(text), expected)
