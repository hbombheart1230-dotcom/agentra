"""Report-only diagnostics ownership; no policy or order mutation."""
from pathlib import Path
import inspect
from libs.reporting.trade_report.summary_parts.render_diagnostics import collect_render_diagnostics


def _float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _deps():
    return {
        "is_not_captured": lambda value: value in (None, "", "-"),
        "fmt_pct": lambda value: f"{float(value):.2%}",
        "as_dict": lambda value: value if isinstance(value, dict) else {},
        "listify": lambda value: value if isinstance(value, list) else [],
        "num_opt": _float,
        "dedupe": lambda values: list(dict.fromkeys(values)),
    }


def _call(**overrides):
    values = dict(truth_price={}, truth_pnl={}, shared={}, carryover_exit=False,
                  recovered_partial_exit=False, rank_num=None, strategist={},
                  selection={}, entry={}, exit_decision={}, holding_duration_summary="",
                  memory_app={}, combined_texts=[], cost_analysis={}, cost_drag_pct=None,
                  selection_fallback_summary={}, scanner_top_pick="", symbol="005930",
                  entry_blob="", carryover_context={}, actual_take_profit=False,
                  actual_peak_exit=False, actual_hard_stop=False)
    values.update(overrides)
    return collect_render_diagnostics(
        **values, deps=_deps(), compact_number=str,
        first_matching_line=lambda values, needles: next(
            (str(value) for value in values if any(needle in str(value) for needle in needles)), ""),
    )


def test_empty_diagnostics_use_observational_fallback():
    positive, problems, causes, recommendations = _call()
    assert positive == ["핵심 거래 아티팩트가 보존됨"]
    assert problems == ["거래별 반복 패턴 판단을 위한 추가 표본 필요"]
    assert causes == ["진입/청산 구조의 반복성은 당일 패턴 섹션에서 추가 확인 필요"]
    assert recommendations == ["보유 구간 모니터 스냅샷 보강"]


def test_carryover_uses_separate_truth_and_avoids_overlong_actions():
    positive, problems, causes, recommendations = _call(
        truth_price={"broker_fill_price": 1200}, truth_pnl={"value": 12},
        carryover_exit=True, recovered_partial_exit=True, rank_num=2,
        cost_analysis={"mock_cost_warning": True}, cost_drag_pct=.003,
        selection_fallback_summary={"used": True}, scanner_top_pick="000660",
        actual_peak_exit=True,
    )
    assert positive[0] == "키움 체결가와 당일 실현손익 확보"
    assert "이월 청산" in positive[1]
    assert any("이월 포지션" in line for line in problems)
    assert any("peak_drawdown" in line for line in recommendations)
    assert len(recommendations) <= 4


def test_render_diagnostics_owner_is_bounded():
    source = Path(inspect.getsourcefile(collect_render_diagnostics)).read_text(encoding="utf-8")
    assert len(source.splitlines()) <= 350
    assert "import libs.reporting.trade_report_markdown_clean" not in source
