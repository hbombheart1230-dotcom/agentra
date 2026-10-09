import ast
import inspect
from pathlib import Path

from libs.reporting.trade_story_assembly_parts.lifecycle_evidence import enrich_lifecycle_story_evidence


def test_lifecycle_evidence_is_small_canonical_reporting_only_owner():
    owner_path = Path(inspect.getsourcefile(enrich_lifecycle_story_evidence))
    source = owner_path.read_text(encoding="utf-8")
    assert len(source.splitlines()) <= 350
    tree = ast.parse(source)
    assert any(isinstance(node, ast.FunctionDef) and node.name == "enrich_lifecycle_story_evidence"
               for node in tree.body)
    assert not any(
        isinstance(node, ast.ImportFrom)
        and any(token in (node.module or "") for token in
                ("trade_story_pipeline_story_assembly", "trade_story_pipeline", "executor"))
        for node in ast.walk(tree)
    )


def test_lifecycle_evidence_preserves_source_preference_and_monitor_context():
    def empty(*args, **kwargs):
        return {}
    deps = {
        "_attach_news_scanner_contribution": empty,
        "_build_monitor_blocker_trace": lambda _: {"blocked": False},
        "_build_monitor_stop_policy_trace": lambda *args: {"stop": "canonical"},
        "_build_scanner_selection_trace": lambda *args: {"ranked_candidates": []},
        "_build_strategist_evidence_trace": lambda *args, **kwargs: {"symbol_headlines": ["a"]},
        "_raw_strategist_evidence": empty,
        "_resolve_selection_monitor_artifact": empty,
        "_set_or_replace_placeholder": lambda target, key, value: target.setdefault(key, value),
        "_strategist_trace_source": empty,
        "build_news_symbol_linkage_view": lambda **kwargs: {"link": "canonical"},
        "reanchor_scanner_selection_for_monitor_fallback": lambda **kw: (
            kw["scanner_reason_human"], kw["scanner_selection_trace"], "005930"
        ),
    }
    market = {}
    monitor = {}
    result = enrich_lifecycle_story_evidence(
        {"post_exit_shadow": {"source": "original"}, "strategy_horizon_feedback": {"h": 1}},
        lifecycle={}, exit_ctx={}, canonical_agent_artifacts={
            "strategist": {"strategy_horizon": "daily"},
            "scanner": {"selected_symbol": "005930"}, "monitor": {"thresholds": {}},
        },
        symbol="005930", market_context_human=market, scanner_reason_human={},
        monitor_reason_human=monitor, deps=deps,
    )
    assert result[3] == {"h": 1}
    assert result[5] == {"source": "original"}
    assert result[10] == {"link": "canonical"}
    assert market["symbol_headlines"] == ["a"]
    assert monitor["monitor_stop_policy_trace"] == {"stop": "canonical"}
