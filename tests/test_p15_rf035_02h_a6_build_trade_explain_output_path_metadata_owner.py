"""P15 RF-035 (02h): trade_explain.build_trade_explain_output_path_metadata moved to trade_explain_path_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from libs.reporting import trade_explain as m
from libs.reporting import trade_explain_path_projection as owner


def _both(d):
    return m.build_trade_explain_output_path_metadata(d), owner.build_trade_explain_output_path_metadata(d, facade=m)


def test_official_and_custom(tmp_path):
    root = tmp_path / "reports"
    official = root / "dev" / "analysis" / "trade_explain"
    a, b = _both(official)
    assert a == b and a["path_status"] == "official" and a["deprecated_note"] == ""
    assert list(a) == ["official_report_dir", "requested_report_dir", "path_status", "deprecated_note"]
    assert a["official_report_dir"] == str(official) and a["requested_report_dir"] == str(official)
    a, b = _both(root / "other")
    assert a == b and a["path_status"] == "custom_nonofficial"
    assert a["deprecated_note"] == f"Official trade_explain path is `{a['official_report_dir']}`; custom output path is supported but non-canonical."


def test_facade_seams(monkeypatch):
    monkeypatch.setattr(m, "_canonical_report_root", lambda d: Path("CANON"))
    seen = []
    monkeypatch.setattr(m, "official_trade_explain_report_dir", lambda r: (seen.append(r), Path("OFF"))[1])
    a, b = _both(Path("OFF"))
    assert a == b and a["path_status"] == "official" and a["deprecated_note"] == "" and seen == [Path("CANON")] * 2
    a, b = _both(Path("elsewhere"))
    assert a == b and a["path_status"] == "custom_nonofficial" and "`OFF`" in a["deprecated_note"]
