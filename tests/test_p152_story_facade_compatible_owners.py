"""P1.5.2 Story façade extraction: pinned AST bodies + public monkeypatch fidelity."""
import ast
import subprocess
from pathlib import Path
import pytest
import libs.reporting.trade_story_pipeline as facade
from libs.reporting.trade_story_facade_parts import strategist_evidence, filter_checklist

BASE = "f381772d2118aca6444108fab429e4a0e0fba056"
PATH = "libs/reporting/trade_story_pipeline.py"
MOVED = {
    "_raw_strategist_evidence": (strategist_evidence, "_raw_strategist_evidence_impl", 0),
    "_strategist_trace_source": (strategist_evidence, "_strategist_trace_source_impl", 0),
    "_build_strategist_evidence_trace": (strategist_evidence, "_build_strategist_evidence_trace_impl", 4),
    "build_filters_human": (filter_checklist, "build_filters_human_impl", 0),
}


def before_function(name):
    old = subprocess.check_output(["git", "show", f"{BASE}:{PATH}"], text=True, encoding="utf-8-sig")
    fn = next(n for n in ast.parse(old).body if isinstance(n, ast.FunctionDef) and n.name == name)
    space = vars(facade).copy()
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<pre-split-story-facade>", "exec"), space)
    return fn, space[name]


@pytest.mark.parametrize("name", sorted(MOVED))
def test_body_ast_and_owner_cap(name):
    original, _ = before_function(name)
    module, owner_name, extra = MOVED[name]
    source = Path(module.__file__).read_text(encoding="utf-8")
    implementation = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == owner_name)
    assert ast.dump(ast.Module(body=original.body, type_ignores=[]), include_attributes=False) == ast.dump(
        ast.Module(body=implementation.body[extra:], type_ignores=[]), include_attributes=False)
    assert len(source.splitlines()) <= 350


def test_strategist_trace_matches_precise_pre_split_behavior():
    values = [
        ({}, dict(selected_symbol="005930")),
        ({"global_sentiment_signal": {"fear_index": {"score": 22}},
          "news_evidence_ranked": {"market_news_ranked": [],
                                   "candidate_news_ranked": []}}, dict(selected_symbol="005930")),
        ({"news_evidence_ranked": [{"payload": {"market_news_ranked": [], "candidate_news_ranked": []}}],
          "candidate_symbols_hint": ["005930"], "key_events": ["trend"]}, dict(selected_symbol="005930")),
    ]
    _, original = before_function("_build_strategist_evidence_trace")
    for value, extra in values:
        assert facade._build_strategist_evidence_trace(value, **extra) == original(value, **extra)


def test_raw_strategist_source_and_filter_human_match_pre_split_behavior():
    for name, args in [
        ("_raw_strategist_evidence", ({"evidence": {"strategist": {"a": 1}}},)),
        ("_raw_strategist_evidence", ({},)),
        ("_strategist_trace_source", ({"global_sentiment_score": 0.2},
                                        {"news_evidence_ranked": {"market_news_ranked": []}})),
        ("build_filters_human", ({"selected_candidate": {
            "sources": ["top_value", "sector_theme"],
            "score_breakdown": {"volume_surge": 0.8, "theme_boost": 0.5},
            "component_snapshot": {"trading_value_component": 1.0},
            "feature_snapshot": {"quote_spread_bps": 10.0},
            "risk_score": 0.4}},
            {"global_sentiment_score": 0.1}, {"supervisor_allow": True})),
        ("build_filters_human", ({}, {}, {})),
    ]:
        _, original = before_function(name)
        assert getattr(facade, name)(*args) == original(*args)


def test_call_time_monkeypatch_seams_are_live(monkeypatch):
    calls = []
    old_headlines = facade._collect_top_headlines
    def patched(*args, **kwargs):
        calls.append("headlines")
        return old_headlines(*args, **kwargs)
    monkeypatch.setattr(facade, "_collect_top_headlines", patched)
    facade._build_strategist_evidence_trace({}, selected_symbol="005930")
    assert calls
    old_float = facade.safe_float
    def float_spy(*args, **kwargs):
        calls.append("safe_float")
        return old_float(*args, **kwargs)
    monkeypatch.setattr(facade, "safe_float", float_spy)
    facade.build_filters_human({}, {}, {})
    assert "safe_float" in calls
