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


def test_number_and_pct_formatters():
    _eq([m._fmt_multiple(v) for v in (1.5, "2", None, "x", 0)], ["1.50배", "2.00배", "-", "-", "0.00배"])
    # signed pct takes a RATIO (x100) and renders an explicit sign
    _eq([m._fmt_signed_pct(v) for v in (1.234, -0.5, 0, None, "x", "3")], ["+123.40%", "-50.00%", "0.00%", "-", "-", "+300.00%"])
    _eq([m._korea_index_lines({})], [[]])
    _eq(m._korea_index_lines({"korea_indices": {"indices": {"KOSPI": {"current": 2500.5, "change_pct": 1.2}}}}), ["KOSPI 현재 2,500.50 등락률 +1.20%"])


def test_first_present_boolish_and_checkpoint_label():
    _eq((m._first_present(None, "", 0, "a"), m._first_present(None, ""), m._first_present()), (0, "", ""))          # 0 counts as present
    _eq([m._boolish(v) for v in (True, "true", "1", "yes", "Y", "no", "", None, 0, 2)], [True, True, True, True, True, False, False, False, False, False])
    _eq([m._checkpoint_label(v) for v in ("entry", "exit", "hold", "unknown_x", "")], ["entry", "exit", "hold", "unknown_x", ""])


def test_label_wrappers_delegate_to_the_strategy_memory_helpers():
    _eq(m._strategy_horizon_alignment_label("aligned"), "전략 보유 구간과 충돌 없음")
    _eq((m._strategy_horizon_alignment_label(""), m._strategy_horizon_alignment_label("conflict")), ("-", "conflict"))
    _eq((m._duration_label_compact(65), m._duration_label_compact("x")), ("1분 5초", ""))
    _eq((m._hold_window_label({"min_sec": 60, "target_sec": 300, "max_sec": 600}), m._hold_window_label({})), ("최소 1분 / 목표 5분 / 최대 10분", "-"))


def test_operator_pnl_pct_prefers_truth_then_shared_and_reports_no_inference():
    _eq(m._operator_pnl_pct({"pct": 1.5}, {}), (1.5, False))
    _eq(m._operator_pnl_pct({}, {"pnl_pct": 2}), (2, False))
    _eq(m._operator_pnl_pct({}, {}), ("", False))


def test_quantity_inference_from_costs_and_name_inference():
    f = m._infer_trade_quantity_from_costs
    _eq(f(buy_price=100, sell_price=110, pnl=100, fee=0, tax=0), 10.0)
    _eq(f(buy_price=100, sell_price=110, pnl=80, fee=10, tax=10), 10.0)                 # costs are added back to pnl before dividing
    _eq(f(buy_price=110, sell_price=100, pnl=-100, fee=0, tax=0), 10.0)
    for bad in (dict(buy_price=100, sell_price=100, pnl=-5, fee=3, tax=2), dict(buy_price=None, sell_price=110, pnl=1, fee=0, tax=0),
                dict(buy_price=100, sell_price=110, pnl=None, fee=0, tax=0), dict(buy_price="x", sell_price=1, pnl=1, fee=0, tax=0)):
        _eq(f(**bad), None)                                                           # equal prices or missing inputs cannot infer a quantity
    _eq(m._infer_symbol_name_from_report_text({"summary": "삼성전자(005930) 매수 후 청산"}, "005930"), "삼성전자")
    _eq(m._infer_symbol_name_from_report_text({}, "005930"), "")


def test_reporter_pattern_humanizer_known_and_unknown_names():
    _eq(m._humanize_reporter_pattern("monitor_only_ratio", "monitor_only 3/4 runs", 0.75), "모니터 단독 경로가 전체 4회 중 3회로 반복됐습니다.")
    _eq(m._humanize_reporter_pattern("zzz", "d", 1), "d")                              # unknown pattern falls back to its detail text
