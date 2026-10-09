"""P1.5.2 conservative façade consumer recognition tests."""
from scripts.refactor.p152_facade_consumer_scan import scan_source, TARGETS


def test_direct_import_alias_attr_and_patch_detection():
    mod = "libs.reporting.trade_story_pipeline"
    src = f"""
from {mod} import build_filters_human as filters
from libs.reporting import trade_story_pipeline as story
import {mod} as full_story
from unittest.mock import patch
filters({{}},{{}},{{}})
story.build_guard_reason_human({{}})
full_story.build_filters_human({{}},{{}},{{}})
with patch("{mod}.build_guard_reason_human"):
    pass
getattr(story, "build_filters_human")
monkeypatch.setattr(story, "build_guard_reason_human", lambda x: x)
"""
    refs, hazards = scan_source("sample.py", src, {
        mod: {"build_filters_human", "build_guard_reason_human"},
    })
    actual = {(x["symbol"], x["kind"]) for x in refs}
    assert ("build_filters_human", "DIRECT_IMPORT") in actual
    assert ("build_filters_human", "IMPORTED_NAME_USAGE") in actual
    assert ("build_filters_human", "MODULE_ATTRIBUTE") in actual
    assert ("build_guard_reason_human", "STRING_PATCH") in actual
    assert ("build_guard_reason_human", "MONKEYPATCH") in actual
    assert not hazards


def test_wildcard_and_computed_getattr_never_prove_dead():
    mod = "libs.reporting.trade_report_ai"
    src = f"""
from {mod} import *
import {mod} as mod
name="build_ai_trade_report"
getattr(mod,name)
"""
    refs, hazards = scan_source("sample.py", src, {mod: {"build_ai_trade_report"}})
    assert not any(x["kind"] == "LITERAL_ATTR" for x in refs)
    assert {"WILDCARD_IMPORT", "DYNAMIC_ATTR"} <= {x["kind"] for x in hazards}


def test_parse_error_yields_hazard_instead_of_silently_omitting_file():
    mod = "libs.reporting.trade_report_markdown_clean"
    refs, hazards = scan_source("bad.py", "def broken(:\n", {mod: {"render_trade_report_markdown_clean"}})
    assert not refs
    assert hazards[0]["kind"] == "PARSE_ERROR"


def test_targets_are_only_three_reporting_facades():
    assert set(TARGETS) == {
        "libs.reporting.trade_report_ai",
        "libs.reporting.trade_report_markdown_clean",
        "libs.reporting.trade_story_pipeline",
    }
