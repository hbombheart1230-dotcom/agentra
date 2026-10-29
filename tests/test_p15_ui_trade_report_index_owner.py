from pathlib import Path

from apps.operator_ui.data_access_core import OperatorUIConfig, _trade_report_index
from apps.operator_ui.data_access_report_index import trade_report_index
import apps.operator_ui.data_access_core as facade


def _config(root: Path) -> OperatorUIConfig:
    return OperatorUIConfig(root, root / "reports", root / "events.jsonl", root / "evidence.jsonl", root / "memory", root / "cache")


def test_empty_report_root_keeps_empty_indexes_and_wrapper_owner_parity(tmp_path):
    config = _config(tmp_path)
    expected = {"by_run_id": {}, "by_story_id": {}}
    assert _trade_report_index(config) == expected
    assert trade_report_index(config, facade=facade) == expected
