"""P15 RF-035: llm_artifacts monthly_artifact_paths moved to llm_artifacts_path_projection; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_path_projection as owner


KEYS = ["root_dir", "monthly_root", "monthly_summary_json", "monthly_summary_md"]


def _both(root, v):
    return m.monthly_artifact_paths(root, v), owner.monthly_artifact_paths(root, v, facade=m)


def test_values_and_empty():
    a, b = _both(Path("reports"), " 2026-10 ")
    assert a == b and list(a) == KEYS
    assert a["root_dir"] == Path("reports/operator_summary/monthly/2026-10")
    assert a["monthly_summary_md"].name == "monthly_summary.md" and a["monthly_summary_json"].name == "monthly_summary.json"
    for out in _both(Path("reports"), ""):
        assert out["root_dir"] == Path("reports/operator_summary/monthly")


def test_facade_root_seam(monkeypatch):
    monkeypatch.setattr(m, "operator_summary_artifact_root", lambda r: Path("fake"))
    a, b = _both(Path("reports"), "2026-10")
    assert a == b and a["root_dir"] == Path("fake/monthly/2026-10")
