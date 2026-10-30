"""P15 RF-035: llm_artifacts _repo_root_from_reports_root moved to llm_artifacts_path_projection; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_path_projection as owner


def test_values():
    for fn in (m._repo_root_from_reports_root, owner._repo_root_from_reports_root):
        assert fn(Path("/x/reports")) == Path("/x")
        assert fn(Path("/x/other")) == Path("/x/other")
        assert fn(Path("reports")) == Path(".")
        assert fn(Path("/x/reports/sub")) == Path("/x/reports/sub")
        assert fn("/x/reports") == Path("/x")
