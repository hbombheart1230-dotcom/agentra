"""P15 RF-035: llm_artifacts canonical_trade_day_root moved to llm_artifacts_path_projection; parity with the pre-move body."""
from __future__ import annotations

from pathlib import Path

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_path_projection as owner


def test_values_and_no_fs_access(tmp_path):
    for fn in (m.canonical_trade_day_root, owner.canonical_trade_day_root):
        assert fn(Path("reports"), " 2026-10-30 ") == Path("reports/trades/2026-10-30")
        assert fn(Path("reports"), None) == Path("reports/trades")
        assert fn(Path("/tmp/r"), "D") == Path("/tmp/r/trades/D")
        assert fn("reports", "D") == Path("reports/trades/D")
        assert not fn(tmp_path, "D").exists()
