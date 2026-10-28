"""RF-031 trade_report_markdown_strategy_memory: label helpers behind the façade (pure, injected callables)."""
from __future__ import annotations

from libs.reporting import trade_report_markdown_strategy_memory as m


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _meta(value):
    return str(value or "").strip()


def _num(value):
    try:
        return float(value)
    except Exception:
        return None


def _as_dict(value):
    return value if isinstance(value, dict) else {}


def test_alignment_and_horizon_labels():
    _eq(m.strategy_horizon_alignment_label("aligned", metadata_value=_meta), "전략 보유 구간과 충돌 없음")
    _eq(m.strategy_horizon_alignment_label("", metadata_value=_meta), "-")
    _eq(m.strategy_horizon_label("intraday", metadata_value=_meta), "단타/당일(intraday)")
    _eq(m.strategy_horizon_reason_label("trend", metadata_value=_meta), "trend")                  # unknown reasons pass through unchanged


def test_duration_label_compact_formats_seconds_and_rejects_non_numbers():
    _eq(m.duration_label_compact(90, num_opt=_num), "1분 30초")
    _eq(m.duration_label_compact(3700, num_opt=_num), "1시간 1분 40초")
    _eq(m.duration_label_compact(None, num_opt=_num), "")
    _eq(m.duration_label_compact("abc", num_opt=_num), "")


def test_hold_window_label_reads_min_target_max_seconds_keys_only():
    window = {"min_sec": 60, "target_sec": 300, "max_sec": 600}
    label = m.hold_window_label(window, as_dict=_as_dict, duration_label_compact_fn=lambda v: m.duration_label_compact(v, num_opt=_num))
    _eq(label, "최소 1분 / 목표 5분 / 최대 10분")
    partial = m.hold_window_label({"min_sec": 60}, as_dict=_as_dict, duration_label_compact_fn=lambda v: m.duration_label_compact(v, num_opt=_num))
    _eq(partial, "최소 1분 / 목표 - / 최대 -")
    _eq(m.hold_window_label({}, as_dict=_as_dict, duration_label_compact_fn=str), "-")
    # other key spellings are not recognised (current contract)
    other = m.hold_window_label({"min_seconds": 60}, as_dict=_as_dict, duration_label_compact_fn=lambda v: m.duration_label_compact(v, num_opt=_num))
    _eq(other, "최소 - / 목표 - / 최대 -")
