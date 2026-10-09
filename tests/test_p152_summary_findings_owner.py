from pathlib import Path
import inspect

from libs.reporting.trade_report.summary_parts.findings import collect_deterministic_summary_findings


def _findings(**kwargs):
    d=dict(truth_price={}, truth_pnl={}, strategist={}, selection={}, entry={},
           exit_decision={}, memory_app={}, carryover_exit=False,
           recovered_partial_exit=False, combined_blob="", selection_rank=1,
           scanner_chart_fit={}, monitor_memory={},
           deps={"listify": lambda x: x if isinstance(x, list) else [],
                 "as_dict": lambda x: x if isinstance(x, dict) else {},
                 "num_opt": lambda x: float(x) if x not in (None,"") else None})
    d.update(kwargs)
    return collect_deterministic_summary_findings(**d)


def test_deterministic_findings_default_validation_question():
    positives, problems, causes, questions = _findings()
    assert positives == []
    assert problems == []
    assert causes == []
    assert questions == ["진입/청산 정책 조합이 당일 반복 손익 패턴과 일치하는가?"]


def test_deterministic_findings_carryover_and_partial_keeps_precedence():
    positives, problems, causes, questions = _findings(
        carryover_exit=True, recovered_partial_exit=True, truth_pnl={"value": 3},
        selection_rank=2, scanner_chart_fit={"score": 0.1},
        combined_blob="monitor_only peak_drawdown pullback",
    )
    assert positives == ["broker_truth_available",
                         "carryover_exit_accounted_separately",
                         "recovered_partial_exit_accounted_separately"] or positives == [
                             "broker_truth_available",
                             "recovered_partial_exit_accounted_separately",
                             "carryover_exit_accounted_separately"]
    assert "peak_drawdown_exit_needs_review" in problems
    assert "scanner_chart_fit_low" in problems
    assert causes[-2:] == ["recovered_partial_exit_excludes_new_entry_assessment",
                            "carryover_position_excludes_same_day_scanner_selection_assessment"]
    assert len(questions) >= 3


def test_findings_owner_small_without_facade_import():
    text = Path(inspect.getsourcefile(collect_deterministic_summary_findings)).read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 350
    assert "from libs.reporting.trade_report_markdown_clean" not in text
