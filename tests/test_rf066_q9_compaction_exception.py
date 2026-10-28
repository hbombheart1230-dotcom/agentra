"""RF-066 C2/C3: Q9 compaction has explicit temp-file success and failure boundaries."""

from __future__ import annotations

import json

import pytest

from scripts.maintenance.compact_q9_decision_windows import compact_file


def test_rf066_q9_compaction_temp_payload_and_non_object_failure(tmp_path):
    valid_path = tmp_path / "valid.json"
    valid_path.write_text(json.dumps({"windows": [{"scanner_control": {"top10": []}}]}), encoding="utf-8")

    result = compact_file(valid_path, backup=False)

    assert result["path"] == str(valid_path)
    assert result["backup_path"] == ""
    assert json.loads(valid_path.read_text(encoding="utf-8"))["window_count"] == 1

    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="q9 decision payload must be a JSON object"):
        compact_file(invalid_path, backup=False)
