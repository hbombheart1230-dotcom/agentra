"""Call-time patching remains observable across the R2-C extraction boundary."""

from libs.reporting import trade_story_pipeline as story


def test_news_headline_owner_resolves_patched_facade_helper(monkeypatch):
    monkeypatch.setattr(story, "_headline_text", lambda _row: "patched news title")
    assert story._collect_top_headlines([{"title": "original"}]) == ["patched news title"]


def test_news_scanner_trace_resolves_patched_headline_collector(monkeypatch):
    monkeypatch.setattr(story, "_collect_top_headlines", lambda _rows, **_kwargs: ["patched"])
    trace = story._build_news_scanner_contribution_trace(
        selected_symbol="005930",
        selected_score=1.2,
        selected_sources=[],
        score_breakdown={},
        component_snapshot={},
        strategist={"news_evidence_ranked": {"market_news_ranked": [], "candidate_news_ranked": []}},
    )
    assert trace["news_linkage_trace"]["market_headlines_used"] == ["patched"]
    assert trace["news_linkage_trace"]["symbol_headlines_used"] == ["patched"]


def test_scanner_trace_resolves_patched_score_helper(monkeypatch):
    monkeypatch.setattr(story, "_top_numeric_drivers", lambda *_args, **_kwargs: {"patched": 7.0})
    trace = story._build_scanner_selection_trace(
        {"selected_symbol": "005930", "score_breakdown": {"trading_value": 1.0}},
        {},
    )
    assert trace["selected_symbol_score_drivers"] == {"patched": 7.0}


def test_section_provenance_resolves_patched_evidence_derivation(monkeypatch):
    monkeypatch.setattr(story, "_derive_evidence_provenance", lambda _bundle: {"strategist": "canonical"})
    section = story.build_section_provenance({"artifacts": {"canonical_strategist_json": "canonical.json"}})
    assert section["market_context_human"]["source"] == "canonical"
    assert section["market_context_human"]["artifact_path"] == "canonical.json"


def test_completeness_resolves_patched_presence_check(monkeypatch):
    monkeypatch.setattr(story, "_is_present", lambda _value: False)
    completeness = story.compute_evidence_completeness({"market_context_human": {"summary": "present"}})
    assert completeness["completeness_score"] == 0.0
