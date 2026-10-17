"""Reporter whole-role: BASE-first deterministic call capture for pure relocated owners (no I/O, no LLM, no network).

  generate <out.json> [--root DIR]   run on the pinned runtime BASE tree (git archive), calls go through the LEGACY import path
  compute  <out.json>                run on the current tree through the same legacy path

For every top-level function defined in a module, an input battery is built deterministically from the module's own
literal keys (no hand-picked expectations): scalar/empty probes plus key-driven dict/list payloads. Each call records the
JSON-normalised result or the exception type/message, whether inputs were mutated, and whether the result aliases an
argument. Key order is preserved so output bytes can be compared exactly.
"""
from __future__ import annotations

import ast
import copy
import importlib
import inspect
import json
import sys
from pathlib import Path

MODULES = [
    "libs.reporting.narrative_axes",
    "libs.reporting.trade_fallback_text",
    "libs.reporting.reasoning_trace",
    "libs.reporting.trade_execution_outcome_text",
    "libs.reporting.chart_structure_decision_hint_summary",
    "libs.reporting.policy_surface_summary",
    "libs.reporting.report_metadata",
]
MAX_KEYS = 160


def _literal_keys(path: Path) -> list[str]:
    keys: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and 0 < len(node.value) <= 48 and "\n" not in node.value:
            if node.value not in keys:
                keys.append(node.value)
    return keys[:MAX_KEYS]


def _payloads(keys: list[str]) -> list:
    out: list = [None, {}, [], "", 0, "text", 1.5, True, ["a", "b"], [{}], {"a": None}]
    for variant in range(4):
        row = {}
        for i, k in enumerate(keys):
            sel = (i + variant) % 6
            row[k] = (["x", k], {"nested": k, "n": i}, k, i * 1.5 + variant, bool((i + variant) % 2), None)[sel]
        out.append(row)
        out.append([copy.deepcopy(row), {}, copy.deepcopy(row)])
    return out


def _calls(fn, payloads):
    sig = inspect.signature(fn)
    params = [p for p in sig.parameters.values() if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]
    required = [p for p in params if p.default is p.empty and p.kind is not p.KEYWORD_ONLY]
    kwonly_required = [p for p in params if p.default is p.empty and p.kind is p.KEYWORD_ONLY]
    out = []
    for i, pl in enumerate(payloads):
        args = [pl] * len(required)
        kwargs = {p.name: pl for p in kwonly_required}
        out.append((args, kwargs))
        if len(required) >= 2:  # mixed: first payload rotates against a fixed empty mapping
            out.append(([pl] + [payloads[(i + j) % len(payloads)] for j in range(1, len(required))], dict(kwargs)))
    return out


def compute() -> list[dict]:
    rows = []
    for name in MODULES:
        mod = importlib.import_module(name)
        src = Path(inspect.getsourcefile(mod))
        payloads = _payloads(_literal_keys(src))
        fns = [(k, v) for k, v in vars(mod).items() if inspect.isfunction(v) and v.__module__ == mod.__name__]
        for fname, fn in sorted(fns):
            for args, kwargs in _calls(fn, payloads):
                a, k = copy.deepcopy(args), copy.deepcopy(kwargs)
                before = copy.deepcopy((a, k))
                try:
                    res = fn(*a, **k)
                    rec = {"ok": json.loads(json.dumps(res, ensure_ascii=False, default=repr)),
                           "alias": any(res is x for x in a) or any(res is x for x in k.values())}
                except Exception as exc:  # noqa: BLE001
                    rec = {"exc": type(exc).__name__, "msg": str(exc)[:160]}
                rec["mutated"] = (a, k) != before
                rows.append({"mod": name, "fn": fname, "n": len(args), "result": rec})
    return rows


if __name__ == "__main__":
    if "--root" in sys.argv:
        sys.path.insert(0, sys.argv[sys.argv.index("--root") + 1])
    rows = compute()
    Path(sys.argv[2]).write_text(json.dumps({"cases": rows}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(sys.argv[1].upper(), len(rows))
