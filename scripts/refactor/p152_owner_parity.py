"""P1.5.2 read-only source-body and owner-size parity gate (pinned R2 starting HEAD)."""
from __future__ import annotations

import ast
import importlib
import subprocess
from pathlib import Path

BASELINE = "2fb4b8fcbaa68c34e80fbdbeb8e009c66d0cbc7c"
MOVES = [
  {
    "original": "libs/reporting/trade_report/sections.py",
    "target": "libs/reporting/trade_report/section_parts/market_context.py",
    "names": [
      "build_market_context_summary",
      "build_market_context_bullets"
    ]
  },
  {
    "original": "libs/reporting/trade_report/sections.py",
    "target": "libs/reporting/trade_report/section_parts/strategist.py",
    "names": [
      "build_strategist_summary_section"
    ]
  },
  {
    "original": "libs/reporting/trade_report/sections.py",
    "target": "libs/reporting/trade_report/section_parts/scanner_selection.py",
    "names": [
      "build_market_scanner_linkage_bullet",
      "build_scanner_choice_bullets",
      "build_scanner_choice_summary",
      "build_scanner_candidate_comparison_section"
    ]
  },
  {
    "original": "libs/reporting/trade_report/sections.py",
    "target": "libs/reporting/trade_report/section_parts/entry_decision.py",
    "names": [
      "build_entry_decision_summary",
      "select_entry_decision_detail",
      "resolve_entry_monitor_reason"
    ]
  },
  {
    "original": "libs/reporting/trade_report/sections.py",
    "target": "libs/reporting/trade_report/section_parts/entry_bullets.py",
    "names": [
      "build_entry_decision_bullets"
    ]
  },
  {
    "original": "libs/reporting/trade_report/sections.py",
    "target": "libs/reporting/trade_report/section_parts/lifecycle_bullets.py",
    "names": [
      "build_holding_story_bullets",
      "build_exit_decision_bullets"
    ]
  },
  {
    "original": "libs/reporting/trade_report/sections.py",
    "target": "libs/reporting/trade_report/section_parts/reporter_evaluation.py",
    "names": [
      "build_reporter_evaluation_section",
      "build_reporter_evaluation_from_feedback"
    ]
  },
  {
    "original": "libs/reporting/trade_report/sections.py",
    "target": "libs/reporting/trade_report/section_parts/execution_quality.py",
    "names": [
      "build_execution_quality_section"
    ]
  },
  {
    "original": "libs/reporting/trade_story_pipeline_story_assembly.py",
    "target": "libs/reporting/trade_story_assembly_parts/timeline.py",
    "names": [
      "build_timeline",
      "collect_story_warnings",
      "compact_canonical_monitor"
    ]
  },
  {
    "original": "libs/reporting/trade_story_pipeline_story_assembly.py",
    "target": "libs/reporting/trade_story_assembly_parts/lifecycle_normalization.py",
    "names": [
      "normalize_trade_lifecycle_for_story_input"
    ]
  },
  {
    "original": "libs/reporting/trade_story_pipeline_story_assembly.py",
    "target": "libs/reporting/trade_story_assembly_parts/lifecycle_bundle.py",
    "names": [
      "build_lifecycle_bundle"
    ]
  },
  {
    "original": "libs/reporting/trade_story_pipeline_story_assembly.py",
    "target": "libs/reporting/trade_story_assembly_parts/report_seeds.py",
    "names": [
      "build_report_section_seeds"
    ]
  },
  {
    "original": "libs/reporting/trade_story_pipeline_human_payloads.py",
    "target": "libs/reporting/trade_story_human_parts/market_context.py",
    "names": [
      "build_market_context_human"
    ]
  },
  {
    "original": "libs/reporting/trade_story_pipeline_human_payloads.py",
    "target": "libs/reporting/trade_story_human_parts/scanner_reason.py",
    "names": [
      "build_scanner_reason_human"
    ]
  },
  {
    "original": "libs/reporting/trade_report/markdown_signals.py",
    "target": "libs/reporting/trade_report/markdown_signal_parts/entry_watch.py",
    "names": [
      "entry_watch_execution_lines",
      "entry_watch_summary_lines",
      "resolve_entry_signal_snapshot"
    ]
  },
  {
    "original": "libs/reporting/trade_report/markdown_signals.py",
    "target": "libs/reporting/trade_report/markdown_signal_parts/entry_metrics.py",
    "names": [
      "entry_signal_metric_summary_lines",
      "resolve_entry_execution_visibility"
    ]
  },
  {
    "original": "libs/reporting/trade_report/markdown_signals.py",
    "target": "libs/reporting/trade_report/markdown_signal_parts/exit.py",
    "names": [
      "enrich_exit_signal_snapshot_from_monitor",
      "build_summary_exit_trigger_lines"
    ]
  },
  {
    "original": "libs/reporting/trade_story_pipeline_evidence_hydration.py",
    "target": "libs/reporting/trade_story_evidence_parts/canonical.py",
    "names": [
      "safe_read_json_file",
      "hydrate_canonical_agent_artifacts",
      "resolve_selection_monitor_artifact"
    ]
  },
  {
    "original": "libs/reporting/trade_story_pipeline_evidence_hydration.py",
    "target": "libs/reporting/trade_story_evidence_parts/scanner.py",
    "names": [
      "enrich_scanner_reason_from_evidence"
    ]
  },
  {
    "original": "libs/reporting/trade_story_pipeline_evidence_hydration.py",
    "target": "libs/reporting/trade_story_evidence_parts/filters.py",
    "names": [
      "enrich_filters_from_evidence"
    ]
  },
  {
    "original": "libs/reporting/trade_report/service.py",
    "target": "libs/reporting/trade_report/services/ai_report.py",
    "names": [
      "build_ai_trade_report_service"
    ]
  },
  {
    "original": "libs/reporting/trade_report/service.py",
    "target": "libs/reporting/trade_report/services/trade_summary.py",
    "names": [
      "build_trade_summary_report_service"
    ]
  }
]


def function_node(src: str, name: str) -> ast.FunctionDef:
    matches = [n for n in ast.parse(src).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    assert len(matches) == 1, (name, "expected one top-level function", len(matches))
    return matches[0]


def as_module(path: str) -> str:
    assert path.endswith(".py")
    return path[:-3].replace("/", ".")


def check() -> None:
    original_cache: dict[str, str] = {}
    total = 0
    owners: set[str] = set()
    for item in MOVES:
        original, owner = item["original"], item["target"]
        if original not in original_cache:
            original_cache[original] = subprocess.check_output(["git", "show", f"{BASELINE}:{original}"], text=True)
        target_text = Path(owner).read_text(encoding="utf-8")
        loc = len(target_text.splitlines())
        assert loc <= 350, f"new Owner too large: {owner} {loc} physical LOC"
        owners.add(owner)
        legacy_module = importlib.import_module(as_module(original))
        owner_module = importlib.import_module(as_module(owner))
        for name in item["names"]:
            former = function_node(original_cache[original], name)
            current = function_node(target_text, name)
            assert ast.dump(former, include_attributes=False) == ast.dump(current, include_attributes=False), (original, owner, name, "source AST body changed")
            assert getattr(legacy_module, name) is getattr(owner_module, name), (name, "legacy export identity changed")
            total += 1
    # Genuine seed decomposition is not body-AST-identical; still enforce owner size.
    for owner in [
        "libs/reporting/trade_report/section_seed_parts/commander.py",
        "libs/reporting/trade_report/section_seed_parts/scanner.py",
        "libs/reporting/trade_report/section_seed_parts/monitor.py",
        "libs/reporting/trade_report/section_seed_parts/strategist.py",
    ]:
        loc = len(Path(owner).read_text(encoding="utf-8").splitlines())
        assert loc <= 350, f"seed owner too large: {owner} {loc} LOC"
        owners.add(owner)
    expected = 38
    assert total == expected, (total, expected)
    print(f"P1.5.2 OWNER PARITY PASS: {total} unchanged function ASTs in {len(owners)} <=350-LOC owners")


if __name__ == "__main__":
    check()
