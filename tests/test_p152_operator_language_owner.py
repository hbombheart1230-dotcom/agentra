from pathlib import Path
import inspect

import libs.reporting.trade_report.operator_text as api
from libs.reporting.trade_report.operator_parts.language import normalize_trade_report_language_impl


def test_language_owner_is_bounded_and_original_public_path_works():
    assert len(Path(inspect.getsourcefile(normalize_trade_report_language_impl)).read_text(encoding="utf-8").splitlines()) <= 350
    assert api.normalize_trade_report_language("Entry reason was not captured.") == "진입 이유는 기록되지 않았습니다."
    assert api.normalize_trade_report_language("Exit reason was not captured.") == "청산 이유는 기록되지 않았습니다."


def test_public_normalizer_preserves_call_time_monkeypatch(monkeypatch):
    monkeypatch.setattr(api, "sanitize_forbidden_scripts_text", lambda value: "known patch output")
    assert api.normalize_trade_report_language("any input") == "known patch output"


def test_direct_language_owner_and_public_wrapper_match():
    values = ["Market Sentiment bullish", "Trailing stop", "unknown", "not captured",
              "Scanner selected 005930 as rank 1 out of 10 candidates with score 1.2 because signal."]
    for value in values:
        assert api.normalize_trade_report_language(value) == normalize_trade_report_language_impl(
            value, sanitize_forbidden_scripts_text=api.sanitize_forbidden_scripts_text, _clip=api._clip,
        )
