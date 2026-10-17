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
import subprocess
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
    "libs.reporting.trade_reporter_status_text",
    "libs.reporting.truth_source_labels",
    "libs.reporting.trade_pnl_estimate",
    "libs.reporting.strategist_quant_context_report",
    "libs.reporting.trade_report_post_exit_shadow",
    "libs.reporting.trade_report_symbol_metadata",
    "libs.reporting.trade_story_pipeline_news",
]
BASE = "d773709ba2f70471fad9badba4f92400f7818319"
# decomposed facades: functions are taken from the named owner package instead of the facade module itself
DECOMPOSED = {"libs.reporting.trade_report_symbol_metadata": "libs.agents.reporter.read_models.symbol_metadata_",
              "libs.reporting.trade_story_pipeline_news": "libs.agents.reporter.narrative.news_"}
MAX_KEYS = 160


def _base_source(modname: str) -> str:
    """Literal-key source is always the pinned BASE blob, so keys are identical before and after any relocation/decomposition."""
    root = Path(__file__).resolve().parents[2]
    rel = modname.replace(".", "/") + ".py"
    return subprocess.check_output(["git", "show", f"{BASE}:{rel}"], cwd=root).decode("utf-8-sig")


def _literal_keys(source: str) -> list[str]:
    keys: list[str] = []
    for node in ast.walk(ast.parse(source)):
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


def _identity_callback(value):
    return str(value or "")


def _upper_callback(value):
    return str(value or "").upper() + "!"


def _num_callback(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _calls(fn, payloads):
    sig = inspect.signature(fn)
    params = [p for p in sig.parameters.values() if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]
    required = [p for p in params if p.default is p.empty and p.kind is not p.KEYWORD_ONLY]
    kwonly_required = [p for p in params if p.default is p.empty and p.kind is p.KEYWORD_ONLY]
    out = []
    is_cb = lambda p: "Callable" in str(p.annotation)  # noqa: E731 - injected text/metadata callbacks get real callables
    cb_for = lambda p, cb: _num_callback if "Optional[float]" in str(p.annotation) else cb  # noqa: E731
    for i, pl in enumerate(payloads):
        for cb in (_identity_callback, _upper_callback) if any(is_cb(p) for p in params) else (None,):
            args = [(cb_for(p, cb) if is_cb(p) else copy.deepcopy(pl)) for p in required]  # distinct objects: no accidental self-aliasing
            kwargs = {p.name: (cb_for(p, cb) if is_cb(p) else copy.deepcopy(pl)) for p in kwonly_required}
            out.append((args, kwargs))
            if not any(is_cb(p) for p in params):
                break
        if len(required) >= 2:  # mixed: first payload rotates against a fixed empty mapping
            out.append(([copy.deepcopy(pl)] + [copy.deepcopy(payloads[(i + j) % len(payloads)]) for j in range(1, len(required))], dict(kwargs)))
    return out


def compute() -> list[dict]:
    rows = []
    for name in MODULES:
        mod = importlib.import_module(name)
        payloads = _payloads(_literal_keys(_base_source(name)))
        fns = [(k, v) for k, v in vars(mod).items() if inspect.isfunction(v) and (v.__module__ == mod.__name__ or v.__module__.startswith(DECOMPOSED.get(name, "~")))]
        for fname, fn in sorted(fns):
            for args, kwargs in _calls(fn, payloads):
                a, k = copy.deepcopy(args), copy.deepcopy(kwargs)
                before = copy.deepcopy((a, k))
                try:
                    res = fn(*a, **k)
                    if inspect.isgenerator(res):  # materialise lazily-produced results (repr would carry an address)
                        res = list(res)
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
