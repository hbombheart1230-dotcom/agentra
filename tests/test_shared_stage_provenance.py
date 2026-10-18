"""Original inventory guard must still reject either missing historical marker."""
from pathlib import Path
import pytest
from scripts.refactor.p152_integration_acceptance import ROOT, build_inventory


@pytest.mark.parametrize("marker", ["P1.5.2 OPEN", "P1.5.3"])
def test_removed_historical_marker_fails_original_inventory(marker, tmp_path, monkeypatch):
    current = ROOT / "docs/refactor/work_orders/CURRENT.md"
    original_read = Path.read_text
    temporary = tmp_path / "CURRENT.md"
    temporary.write_text(original_read(current, encoding="utf-8").replace(marker, "REMOVED"), encoding="utf-8")

    def read(path, *args, **kwargs):
        return original_read(temporary if path == current else path, *args, **kwargs)

    assert build_inventory(ROOT)["source_inventory"]["all_source_checks_pass"]
    monkeypatch.setattr(Path, "read_text", read)
    assert not build_inventory(ROOT)["source_inventory"]["all_source_checks_pass"]
