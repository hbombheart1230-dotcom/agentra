"""Public Monitor-trace wrappers keep call-time monkeypatch seams."""
from pathlib import Path
import inspect
import libs.reporting.trade_story_pipeline_human_payloads as api
from libs.reporting.trade_story_human_parts.monitor_traces import (
    resolve_strategist_adaptive_exit_impl,
    build_monitor_stop_policy_trace_impl,
    build_monitor_blocker_trace_impl,
)


def test_stop_policy_trace_keeps_public_patchable_helpers(monkeypatch):
    monkeypatch.setattr(api, "normalize_stop_thresholds", lambda _: {"hard_stop_pct": -.03})
    monkeypatch.setattr(api, "resolve_strategist_adaptive_exit", lambda _: {"stop_loss_pct": -.01})
    monkeypatch.setattr(api, "resolve_adaptive_stop_loss_pct", lambda *a: -.02)
    result = api.build_monitor_stop_policy_trace({}, {})
    assert result["hard_stop_pct"] == -.03
    assert result["adaptive_stop_loss_pct"] == -.02
    assert result["effective_stop_loss_pct"] == -.02
    assert result["strategist_baseline_stop_loss_pct"] == -.01


def test_blocker_trace_keeps_clipping_and_ratios(monkeypatch):
    monkeypatch.setattr(api, "safe_float", lambda x, default=0.0: float(x or default))
    monkeypatch.setattr(api, "format_ratio_pct", lambda x: f"{float(x)*100:.1f}")
    result = api.build_monitor_blocker_trace({
        "entry_metrics": {"volume_ratio": 0.4, "extended_from_vwap_pct": 0.03},
        "entry_thresholds": {"volume_ratio_min": 1.0, "max_extended_from_vwap_pct": 0.02},
        "entry_check_summary": "thresholds blocked",
    })
    assert "volume ratio 0.40 below min 1.00" in result["threshold_shortfalls"]
    assert "VWAP extension 3.0% above max 2.0%" in result["threshold_shortfalls"]
    assert result["entry_check_summary"] == "thresholds blocked"


def test_monitor_trace_parent_and_owner_are_bounded():
    parent=Path(inspect.getsourcefile(api.build_monitor_reason_human))
    owner=Path(inspect.getsourcefile(build_monitor_blocker_trace_impl))
    assert len(parent.read_text(encoding="utf-8").splitlines()) <= 350
    assert len(owner.read_text(encoding="utf-8").splitlines()) <= 350
    assert resolve_strategist_adaptive_exit_impl.__module__.endswith("monitor_traces")
    assert build_monitor_stop_policy_trace_impl.__module__.endswith("monitor_traces")
