from typing import Any, Dict, List


def has_open_order(state: Dict[str, Any], *, facade) -> Any:
    monitor = facade._dict(state.get("monitor"))
    order_lifecycle = facade._dict(monitor.get("order_lifecycle"))
    if not order_lifecycle:
        return None
    stage = facade._clip(order_lifecycle.get("stage"), max_len=40).lower()
    terminal = order_lifecycle.get("terminal")
    if stage:
        return stage not in {"filled", "cancelled", "canceled", "rejected"} and terminal is not True
    if terminal in (True, False):
        return not bool(terminal)
    return None


def gate_pass(metrics: Dict[str, Any], passed_checks: List[str], failed_checks: List[str], key: str, *, facade) -> Any:
    if key in metrics and isinstance(metrics.get(key), bool):
        return metrics.get(key)
    if key in passed_checks:
        return True
    if key in failed_checks:
        return False
    return None


def score_from_checks(*, passed_checks: List[str], failed_checks: List[str], fallback: Any, facade) -> Any:
    try:
        if fallback not in (None, ""):
            return round(float(fallback), 4)
    except Exception:
        pass
    total = len(passed_checks) + len(failed_checks)
    return None if total <= 0 else round(float(len(passed_checks)) / float(total), 4)
