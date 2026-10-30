from typing import Any, Dict, List


def monitor_decision_summary(*, decision_phase: str, primary_reason_text: str, threshold_snapshot: Dict[str, Any], signal_snapshot: Dict[str, Any], missing_inputs: List[str], facade) -> str:
    if missing_inputs:
        missing = ",".join([facade._clip(item, max_len=24) for item in list(missing_inputs)[:3] if facade._clip(item, max_len=24)])
        return facade._clip(f"Decision: insufficient data ({missing or 'unavailable'})", max_len=120)
    phase = str(decision_phase or "").strip().lower()
    reason = facade._clip(primary_reason_text, max_len=64) or "unavailable"
    if phase == "entry":
        entry_signal = facade._clip(facade._dict(signal_snapshot).get("entry_pattern"), max_len=42) or reason
        thresholds = facade._dict(facade._dict(threshold_snapshot).get("entry_thresholds"))
        threshold_text = facade._clip(thresholds.get("max_extended_from_vwap_pct"), max_len=24) or facade._clip(thresholds.get("volume_ratio_min"), max_len=24) or "thresholds"
        return facade._clip(f"Entry: {entry_signal} met with {threshold_text} -> BUY", max_len=120)
    if phase == "exit":
        trigger = facade._clip(facade._dict(signal_snapshot).get("exit_triggered_rule"), max_len=48) or reason
        return facade._clip(f"Exit: {trigger}", max_len=120)
    if phase == "hold":
        return "Hold: conditions stable, no exit trigger"
    return facade._clip(f"No action: {reason}", max_len=120)
