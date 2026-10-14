"""T3.5 first-difference diagnostics for the frozen agent-output fixtures (read-only, bounded output).

usage: p161_agent_output_diagnose.py <tree-root> [--builder NAME] [--max-records N] [--variants N]

Replays the COMMITTED golden fixtures (never regenerated here) against the implementation found under <tree-root>
(`libs/contracts/agent_outputs.py` is imported from that tree) and prints, for the first mismatching records:
builder id, variant id, first differing JSON path, golden vs actual value/type (short synthetic-fixture snippets),
dictionary key-order differences, the stage Owner function that produces the top-level key, and the run context
(Python, OS, TZ). Output is bounded and contains no full evidence payloads.
"""
from __future__ import annotations

import json
import os
import platform
import re
import sys
import time
from pathlib import Path

ROOT_SCRIPTS = Path(__file__).resolve().parent
FIX = ROOT_SCRIPTS.parents[1] / "tests" / "fixtures" / "p1_5_t35_agent_outputs"


def _snip(v, n=90):
    s = json.dumps(v, ensure_ascii=False, default=str) if not isinstance(v, str) else v
    return (s[:n] + "...") if len(s) > n else s


def first_diff(a, b, path=""):
    """-> (path, golden, actual, note) of the first difference, or None."""
    if type(a) is not type(b):
        return path, a, b, f"type {type(a).__name__} != {type(b).__name__}"
    if isinstance(a, dict):
        ka, kb = list(a), list(b)
        if set(ka) != set(kb):
            return path, [k for k in ka if k not in b][:5], [k for k in kb if k not in a][:5], "key set differs (golden-only vs actual-only)"
        if ka != kb:
            i = next(i for i, (x, y) in enumerate(zip(ka, kb)) if x != y)
            return path, ka[i:i + 4], kb[i:i + 4], "key INSERTION ORDER differs"
        for k in ka:
            d = first_diff(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return path, f"len={len(a)}", f"len={len(b)}", "list length differs"
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_diff(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    return None if a == b else (path, a, b, "value differs")


def _owner_for(key, tree_root):
    pat = re.compile(r'^\s+"%s":' % re.escape(key), re.M)
    for f in sorted((Path(tree_root) / "libs" / "contracts").glob("*_output_*.py")):
        text = f.read_text(encoding="utf-8", errors="replace")
        if pat.search(text):
            fn = None
            for m in re.finditer(r"^def (\w+)\(", text, re.M):
                if m.start() < pat.search(text).start():
                    fn = m.group(1)
            return f"{f.name}::{fn}"
    ag = Path(tree_root) / "libs" / "contracts" / "agent_outputs.py"
    if ag.exists() and pat.search(ag.read_text(encoding="utf-8", errors="replace")):
        return "agent_outputs.py (public builder body)"
    return "unknown"


def main(argv):
    tree = Path(argv[1]).resolve()
    builder = "build_strategist_output_artifact"
    max_rec, n_var = 4, 3
    if "--builder" in argv:
        builder = argv[argv.index("--builder") + 1]
    if "--max-records" in argv:
        max_rec = int(argv[argv.index("--max-records") + 1])
    if "--variants" in argv:
        n_var = int(argv[argv.index("--variants") + 1])
    sys.path.insert(0, str(tree))
    sys.path.insert(0, str(ROOT_SCRIPTS))
    import p161_agent_output_freeze as F
    import p161_agent_output_freeze_tool as T
    import p161_agent_output_variants as V
    import libs.contracts.agent_outputs as ao
    loaded = Path(ao.__file__).resolve()
    ctx = {"tree": str(tree), "module_file": str(loaded), "python": platform.python_version(), "os": platform.platform(),
           "tz": time.tzname, "TZ_env": os.environ.get("TZ"), "cwd": os.getcwd(),
           "frozen_clock_base": F.FROZEN_BASE.isoformat(), "implementation_under_tree": str(loaded).startswith(str(tree))}
    print("CONTEXT", json.dumps(ctx))
    base, variants = T.load(FIX)
    recs = [r for r in base if r["builder"] == builder]
    out_bad = var_bad = checked = 0
    shown = 0
    for rec in recs:
        args, kwargs = F.decode(rec["args"]), F.decode(rec["kwargs"])
        kind, payload, _m = T._call(ao, rec["builder"], args, kwargs, [])
        got = json.loads(F.canonical(F.encode(payload))) if kind == "result" else payload
        want = rec["result"]
        checked += 1
        d = first_diff(want, got)
        if d:
            out_bad += 1
            if shown < max_rec:
                shown += 1
                top = d[0].split(".")[1].split("[")[0] if d[0].startswith(".") else ""
                print("OUTPUT_MISMATCH", json.dumps({"id": rec["id"], "path": d[0], "golden": _snip(d[1]), "actual": _snip(d[2]),
                                                    "note": d[3], "golden_type": type(d[1]).__name__,
                                                    "actual_type": type(d[2]).__name__,
                                                    "owner": _owner_for(top, tree) if top else "-"}))
        shown_v = tested = 0
        for vid, va, vk in V.variants(rec["builder"], args, kwargs):
            if shown_v >= n_var or tested >= 40:
                break
            tested += 1
            k2, p2, _ = T._call(ao, rec["builder"], va, vk)
            if [k2, T.digest(p2), False] != variants[rec["id"]].get(vid, [None, None, None])[:2] + [False]:
                var_bad += 1
                shown_v += 1
                print("VARIANT_MISMATCH", rec["id"], vid)
    print("SUMMARY", json.dumps({"builder": builder, "records": len(recs), "checked": checked,
                                 "output_mismatches": out_bad, "variant_mismatches_sampled": var_bad}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
