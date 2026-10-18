"""Strategist S5 helper-move observation runner (fresh interpreter per tree).

Usage: python -I p15_strategist_s5_runner.py <tree> <cases_dir>
`tree` holds libs/ and graphs/ (pinned-source `git archive` or this checkout) and is placed first on sys.path, so the
REAL graphs.nodes.strategist_node of that tree is exercised. `cases_dir` provides p15_strategist_s5_cases.CASES (stdlib only).
Each case builds its arguments and any facade patches itself (before-call or mid-call, via argument objects) and the runner
restores the facade module dict afterwards. Output: per case the typed result (type name + repr, so 3 vs 3.0, nan, -0.0 and
True vs 1 differ), exception type+message, and the recorded patch-call log."""
import importlib
import json
import re
import sys

tree, cases_dir = sys.argv[1], sys.argv[2]
sys.path[:] = [tree, cases_dir] + [p for p in sys.path if p not in ("", ".")]
sys.dont_write_bytecode = True
node = importlib.import_module("graphs.nodes.strategist_node")
cases = importlib.import_module("p15_strategist_s5_cases").CASES


def enc(v):
    if isinstance(v, (list, tuple)):
        return [type(v).__name__, [enc(x) for x in v]]
    return [type(v).__name__, re.sub(r" at 0x[0-9A-Fa-f]+", " at 0x?", repr(v))]  # scrub object addresses


out = []
for case in cases:
    saved = dict(node.__dict__)
    log = []
    rec = {"id": case["id"]}
    try:
        args = case["setup"](node, log)
        rec["result"] = enc(getattr(node, case["fn"])(*args))
    except BaseException as exc:  # noqa: BLE001 - control flow is the observation
        rec["exc"] = [type(exc).__name__, str(exc)]
    for k in [k for k in node.__dict__ if k not in saved]:
        del node.__dict__[k]
    node.__dict__.update(saved)
    rec["log"] = log
    out.append(rec)
sys.stdout.buffer.write((json.dumps(out, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
