"""P15 RF-035: llm_artifacts symbol_artifact_paths moved to llm_artifacts_path_projection; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_path_projection as owner


KEYS = ["root_dir", "symbol_trade_report_json", "symbol_trade_report_md", "symbol_summary_json", "symbol_summary_md", "symbol_memory_json", "trade_history_json", "daily_index_json", "latest_snapshot_json"]


def _both(root, sym):
    return m.symbol_artifact_paths(root, sym), owner.symbol_artifact_paths(root, sym, facade=m)


def test_values():
    a, b = _both(Path("reports"), " 005930 ")
    assert a == b and list(a) == KEYS
    assert a["root_dir"] == Path("reports/operator_summary/symbols/005930")
    assert _both(Path("reports"), "abC")[0]["root_dir"].name == "ABC"
    for out in _both(Path("reports"), None):
        assert out["root_dir"] == Path("reports/operator_summary/symbols") and out["root_dir"].name == "symbols"


def test_facade_root_spy(monkeypatch):
    seen = []
    monkeypatch.setattr(m, "operator_summary_artifact_root", lambda r: (seen.append(r), Path("fake"))[1])
    a, b = _both(Path("reports"), "x")
    assert a == b and a["root_dir"] == Path("fake/symbols/X") and len(seen) == 2
