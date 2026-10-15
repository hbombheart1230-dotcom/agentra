"""Import-only regression for relocating the Reporting helper modules.

Every former absolute import path must remain a module-object alias to the new
canonical location; exported functions, private helpers, and monkeypatch targets
must remain the same Python objects.
"""

from __future__ import annotations

import importlib

import pytest


RELOCATIONS = [
    ("libs.reporting.trade_report_ai_merge_policy", "libs.reporting.trade_report.merge_policy"),
    ("libs.reporting.trade_report_ai_prompting", "libs.reporting.trade_report.prompting"),
    ("libs.reporting.trade_report_ai_shared_facts", "libs.reporting.trade_report.shared_facts"),
    ("libs.reporting.trade_report_markdown_monitor", "libs.reporting.trade_report_markdown.monitor"),
    ("libs.reporting.trade_report_markdown_scanner", "libs.reporting.trade_report_markdown.scanner"),
    ("libs.reporting.trade_report_common", "libs.reporting.trade_report.normalization"),
    ("libs.reporting.trade_reporter_status_text", "libs.reporting.trade_report.operator_text"),
    ("libs.reporting.trade_report_ai_summary_adapter", "libs.reporting.trade_report.summary_adapter"),
    ("libs.reporting.trade_report_ai_compact_helpers", "libs.reporting.trade_report.compact_helpers"),
    ("libs.reporting.trade_report_ai_compact_input", "libs.reporting.trade_report.compact_input"),
    ("libs.reporting.trade_report_ai_llm", "libs.reporting.trade_report.llm"),
    ("libs.reporting.trade_report_markdown_strategy_memory", "libs.reporting.trade_report_markdown.memory"),
    ("libs.reporting.trade_report_markdown_truth", "libs.reporting.trade_report_markdown.truth"),
    ("libs.reporting.trade_story_evidence", "libs.reporting.trade_story.evidence"),
    ("libs.reporting.trade_story_pipeline_evidence_hydration", "libs.reporting.trade_story.evidence_hydration"),
    ("libs.reporting.trade_story_pipeline_human_payloads", "libs.reporting.trade_story.human_payloads"),
    ("libs.reporting.trade_story_pipeline_story_assembly", "libs.reporting.trade_story.assembly"),
]


@pytest.mark.parametrize("old_name,new_name", RELOCATIONS)
def test_legacy_module_is_identical_to_new_owner(old_name: str, new_name: str) -> None:
    old = importlib.import_module(old_name)
    new = importlib.import_module(new_name)
    assert old is new


def test_normalization_preserves_existing_public_and_private_exports() -> None:
    old = importlib.import_module("libs.reporting.trade_report_common")
    new = importlib.import_module("libs.reporting.trade_report.normalization")
    assert old.safe_int is new.safe_int
    assert old.safe_int("12") == 12
    assert old.safe_float("1.5") == 1.5


def test_old_reporter_text_path_is_not_independently_implemented() -> None:
    old = importlib.import_module("libs.reporting.trade_reporter_status_text")
    new = importlib.import_module("libs.reporting.trade_report.operator_text")
    assert old.normalize_reporter_text is new.normalize_reporter_text
