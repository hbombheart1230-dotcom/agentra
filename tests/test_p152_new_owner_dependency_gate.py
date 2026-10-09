"""P1.5.2 Reporting-only Owner cap, import direction and DAG guard."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER_FILES = (
    "libs/reporting/trade_story_assembly_parts/lifecycle_human.py",
    "libs/reporting/trade_story_assembly_parts/reasoning_provenance.py",
    "libs/reporting/trade_story_assembly_parts/direct_story.py",
    "libs/reporting/trade_story_assembly_parts/lifecycle_evidence.py",
    "libs/reporting/trade_story_human_parts/monitor_diagnostics.py",
    "libs/reporting/trade_story_human_parts/monitor_policy_bullets.py",
    "libs/reporting/trade_story_human_parts/monitor_entry_review.py",
    "libs/reporting/trade_story_human_parts/monitor_context.py",
    "libs/reporting/trade_story_human_parts/monitor_traces.py",
    "libs/reporting/trade_report/operator_parts/exact_phrases.py",
    "libs/reporting/trade_report/operator_parts/context_patterns.py",
    "libs/reporting/trade_report/operator_parts/lifecycle_patterns.py",
    "libs/reporting/trade_report/operator_parts/language.py",
    "libs/reporting/trade_report/summary_parts/findings.py",
    "libs/reporting/trade_report/summary_parts/render_diagnostics.py",
    "libs/reporting/trade_report/summary_render_parts/overview.py",
    "libs/reporting/trade_report/summary_render_parts/market_news.py",
    "libs/reporting/trade_report/summary_render_parts/decision_lifecycle.py",
    "libs/reporting/trade_report/summary_render_parts/closing.py",
    "libs/reporting/trade_report/summary_input_parts/broker_alignment.py",
    "libs/reporting/trade_report/summary_input_parts/market_and_strategy.py",
    "libs/reporting/trade_report/summary_input_parts/decision_flow.py",
    "libs/reporting/trade_report/summary_input_parts/main_builder.py",
    "libs/reporting/trade_report/summary_render_parts/main_renderer.py",
    "libs/reporting/trade_report/summary_render_parts/render_helpers.py",
    "libs/reporting/trade_story_facade_parts/strategist_evidence.py",
    "libs/reporting/trade_story_facade_parts/filter_checklist.py",
    "libs/reporting/trade_story_facade_parts/human_judgments.py",
    "libs/reporting/trade_story_facade_parts/story_contracts.py",
)
FORBIDDEN = (
    "trade_report_ai", "trade_report_markdown_clean",
    "trade_story_pipeline_human_payloads", "trade_story_pipeline_story_assembly",
    "libs.execution", "libs.broker", "libs.supervisor", "libs.executor",
)


def test_new_reporting_owners_are_bounded_and_acyclic():
    paths = {Path(p) for p in OWNER_FILES}
    assert len(paths) == 29
    deps = {}
    for path in paths:
        source = (ROOT / path).read_text(encoding="utf-8")
        assert len(source.splitlines()) <= 350, str(path)
        edges = set()
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            modules = ([name.name for name in node.names] if isinstance(node, ast.Import)
                       else [node.module or ""])
            assert not any(bad in module for module in modules for bad in FORBIDDEN), str(path)
            if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
                target = path.parent.joinpath(*node.module.split(".")).with_suffix(".py")
                if target in paths:
                    edges.add(target)
        deps[path] = edges
    visited, active = set(), set()
    def visit(path):
        assert path not in active, f"Reporting Owner cycle: {path}"
        if path in visited:
            return
        active.add(path)
        for dep in deps[path]:
            visit(dep)
        active.remove(path)
        visited.add(path)
    for path in paths:
        visit(path)
    assert visited == paths
