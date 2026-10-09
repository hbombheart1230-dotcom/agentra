"""Read-only Monitor report-context small-owner tests."""
from pathlib import Path
import ast
import inspect
import pytest
from libs.reporting.trade_story_human_parts.monitor_context import prepare_monitor_review_context
from libs.reporting.trade_story_pipeline_human_payloads import build_monitor_reason_human


def _float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _merge_missing(base, incoming):
    result = dict(base or {})
    for key, value in (incoming or {}).items():
        if key not in result or result[key] in (None, ""):
            result[key] = value
    return result


def _deps():
    return {
        "build_monitor_blocker_trace": lambda d: {"source": d.get("entry_condition_path")},
        "build_monitor_stop_policy_trace": lambda monitor, thresholds: dict(thresholds),
        "list_text": lambda seq, **kwargs: [str(x) for x in (seq or []) if str(x)],
        "merge_missing_values": _merge_missing,
        "format_exit_label": str,
        "format_ratio_pct": lambda v: f"{_float(v) * 100:.2f}",
        "safe_float": _float,
        "safe_int": lambda v, default=0: int(_float(v, default)),
    }


@pytest.mark.parametrize("monitor,execution,expected", [
    ({}, {}, ("WAIT", False, False)),
    ({"entry_evaluated": True, "entry_triggered": True, "entry_reason": "confirmed",
      "entry_metrics": {"volume_ratio": 1.6}, "entry_thresholds": {"volume_ratio_min": 1.2}},
     {"action": "BUY"}, ("BUY", True, True)),
    ({"monitor_reason": "exit_signal_pending_confirmation",
      "guard_reason": "exit_confirmation_pending:2/3",
      "thresholds": {"hard_stop_pct": -0.02}}, {"action": "SELL"}, ("SELL", False, False)),
    ({"eod_carry_evaluated": True, "eod_carry_approved": True,
      "minutes_to_close": 5}, {"action": "HOLD"}, ("HOLD", False, False)),
])
def test_monitor_context_preserves_observed_fields(monitor, execution, expected):
    output = build_monitor_reason_human(monitor, execution, deps=_deps())
    assert (output["posture"], output["entry_evaluated"], output["entry_triggered"]) == expected
    if monitor.get("eod_carry_approved"):
        assert "overnight carry was approved" in output["summary"]
    if execution.get("action") == "SELL":
        assert output["monitor_execution_mismatch"] is True


def test_context_owner_is_bounded_without_reverse_facade_import():
    path = Path(inspect.getsourcefile(prepare_monitor_review_context))
    source = path.read_text(encoding="utf-8")
    assert len(source.splitlines()) <= 350
    assert not any(
        isinstance(n, ast.ImportFrom) and "trade_story_pipeline_human_payloads" in (n.module or "")
        for n in ast.walk(ast.parse(source))
    )
