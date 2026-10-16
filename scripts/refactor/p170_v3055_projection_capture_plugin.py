"""V3-055 capture plugin (run ONCE on the pinned BASE tree): records real caller inputs and BASE results of the pure
public projection functions while existing offline Scanner tests run. Writes JSON lines to $V3055_CAPTURE_OUT."""
from __future__ import annotations

import copy
import importlib
import json
import os

_OUT = os.environ.get("V3055_CAPTURE_OUT", "")
TARGETS = {
    "libs.runtime.scanner.control_eligibility": ("build_full_strategist_control_eligibility",),
    "libs.runtime.scanner.output_payloads": ("build_candidate_ranking_table_payload", "build_candidate_selection_reason_payload"),
    "libs.runtime.scanner.output_snapshots": ("compact_selected_snapshot", "feature_coverage_summary", "compact_feature_snapshot",
                                              "ranking_table_rows"),
}


def _j(o):
    return json.loads(json.dumps(o, ensure_ascii=False, default=repr))


def pytest_configure(config):
    if not _OUT:
        return
    for modname, names in TARGETS.items():
        mod = importlib.import_module(modname)
        for name in names:
            orig = getattr(mod, name)

            def make(name, orig, modname=modname):
                def w(*a, **k):
                    rec = {"fn": name, "mod": modname.rsplit(".", 1)[1], "args": _j(copy.deepcopy(list(a))), "kwargs": _j(copy.deepcopy(k))}
                    try:
                        res = orig(*a, **k)
                        rec["result"] = {"ok": _j(res)}
                        return res
                    except Exception as exc:  # noqa: BLE001
                        rec["result"] = {"exc": type(exc).__name__, "msg": str(exc)[:160]}
                        raise
                    finally:
                        with open(_OUT, "a", encoding="utf-8") as fh:
                            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                w.__wrapped__ = orig
                return w
            setattr(mod, name, make(name, orig, modname))
