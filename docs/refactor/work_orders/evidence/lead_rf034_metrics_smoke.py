"""RF-034 lead-only offline smoke; no network, broker, filesystem writes, or repo mutation."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[4] / "libs/reporting/short_alpha_discriminator/metrics.py"
EXPECTED_BLOB = "c2a64b2bdec26c42eabaab6326324066a1417f85"


def check(condition: bool, label: str) -> None:
    if not condition:
        raise SystemExit(f"RF034_LEAD_METRICS_FAIL {label}")


def main() -> None:
    data = SOURCE.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    check(blob == EXPECTED_BLOB, "source_sha:" + blob)
    tree = ast.parse(data.decode("utf-8"))
    check(not any(isinstance(n, ast.ImportFrom) and n.module not in ("__future__", "statistics", "typing") for n in tree.body), "imports")
    check(not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("open", "exec", "eval", "__import__") for n in ast.walk(tree)), "effectful_calls")
    spec = importlib.util.spec_from_file_location("rf034_metrics", SOURCE)
    check(spec is not None and spec.loader is not None, "spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    check(module.number("bad") is None and module.number(None) is None and module.number("1.25") == 1.25, "number")
    values = [1, -.5, 0, None, "bad"]
    before = copy.deepcopy(values)
    result = module.performance(values)
    check(values == before and result["sample_count"] == 3 and result["win_count"] == 1 and result["loss_count"] == 1 and result["profit_factor"] == 2.0 and result["max_drawdown_pct"] == -.5, "performance")
    check(module.performance(["bad", None])["sample_count"] == 0, "empty")
    check(module.performance([1, 2])["profit_factor"] == 999.0, "no_loss")
    check(module.pearson([(1, 2), (2, 4), (3, 6)]) == 1.0, "pearson_positive")
    check(module.pearson([(1, 3), (2, 2), (3, 1)]) == -1.0, "pearson_negative")
    check(module.pearson([(1, 2), (1, 3)]) is None, "pearson_constant")
    check(module.pearson([("bad", 2), (1, 2)]) is None, "pearson_invalid")
    check(module.checkpoint_return({"checkpoints": {"+5m": {"live_net_return_pct": "0.8"}}}, "+5m") == .8, "checkpoint")
    check(module.checkpoint_return({}, "+5m") is None, "checkpoint_missing")
    check(module.feature_outcome({"outcomes": {"checkpoints": {"EOD": {"status": "OBSERVED", "net_return_pct": "-1.2"}}}}, "EOD") == -1.2, "feature_observed")
    check(module.feature_outcome({"outcomes": {"checkpoints": {"EOD": {"status": "MISSING", "net_return_pct": "-1.2"}}}}, "EOD") is None, "feature_unobserved")
    print(f"RF034_LEAD_METRICS_OK sha={blob} cases=12 io=none mode={'normal' if __debug__ else '-O'}")


if __name__ == "__main__":
    main()
