"""Reporting relocation identity contract for T4-compatible independent owners.

These nine migrations have byte-identical originals on T4. Conflicting T4
modules and canonical owner names are deliberately excluded from this test.
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
    ("libs.reporting.trade_report_ai_summary_adapter", "libs.reporting.trade_report.summary_adapter"),
    ("libs.reporting.trade_report_ai_compact_helpers", "libs.reporting.trade_report.compact_helpers"),
    ("libs.reporting.trade_report_ai_llm", "libs.reporting.trade_report.llm"),
    ("libs.reporting.trade_story_evidence", "libs.reporting.trade_story.evidence"),
]

@pytest.mark.parametrize("old_name,new_name", RELOCATIONS)
def test_independent_legacy_module_is_canonical(old_name: str, new_name: str) -> None:
    old = importlib.import_module(old_name)
    new = importlib.import_module(new_name)
    assert old is new


def test_legacy_flat_helpers_still_export_original_functions() -> None:
    # These flat paths are owned by T4 during eventual integration. They must
    # NOT alias the older copied PR5 implementations.
    common = importlib.import_module("libs.reporting.trade_report_common")
    reporter = importlib.import_module("libs.reporting.trade_reporter_status_text")
    assert common.safe_int("12") == 12
    assert common.safe_float("1.5") == 1.5
    assert callable(reporter.normalize_reporter_text)
