"""P15 RF-035: llm_artifacts llm_artifact_paths moved to llm_artifacts_run_paths; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_run_paths as owner


def _both(*args):
    return m.llm_artifact_paths(*args), owner.llm_artifact_paths(*args, facade=m)


def test_missing_run_and_trim(tmp_path):
    a, b = _both(tmp_path, " 2026-10-30 ", " R ", " comp ")
    assert a == b
    base = tmp_path / "llm" / "2026-10-30" / "R" / "comp"
    assert a["base_dir"] == base and list(a) == ["base_dir", "prompt_json", "response_json", "meta_json"]
    assert a["prompt_json"] == base / "prompt.json" and a["meta_json"] == base / "meta.json"


def test_categorized_run(tmp_path):
    from libs.runtime.llm_report_classifier import LLM_REPORT_CATEGORIES

    cat = LLM_REPORT_CATEGORIES[0]
    (tmp_path / "llm" / "D" / cat / "R").mkdir(parents=True)
    a, b = _both(tmp_path, "D", "R", "c")
    assert a == b and a["base_dir"] == tmp_path / "llm" / "D" / cat / "R" / "c"


def test_facade_find_seam(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "find_llm_run_dir", lambda r, d, rid: Path("fake"))
    a, b = _both(tmp_path, "D", "R", "c")
    assert a == b and a["base_dir"] == Path("fake/c") and a["response_json"] == Path("fake/c/response.json")
