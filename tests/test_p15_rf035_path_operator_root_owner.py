"""P15 RF-035: llm_artifacts operator_summary_artifact_root moved to llm_artifacts_path_projection; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_path_projection as owner


def test_values():
    for fn in (m.operator_summary_artifact_root, owner.operator_summary_artifact_root):
        assert fn(Path("reports")) == Path("reports/operator_summary")
        assert fn(Path("reports/operator_summary")) == Path("reports/operator_summary")
        for sub in ("daily", "weekly", "monthly", "symbols"):
            assert fn(Path("reports/operator_summary") / sub) == Path("reports/operator_summary")
        assert fn(Path("reports/other")) == Path("reports/other/operator_summary")
        assert fn(Path("reports/daily")) == Path("reports/daily/operator_summary")


def test_docstring_kept_on_wrapper():
    assert "double nesting" in (m.operator_summary_artifact_root.__doc__ or "")
