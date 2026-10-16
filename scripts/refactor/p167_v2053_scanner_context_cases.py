"""V2-053 frozen-case generator/replayer for the five relocated Scanner context/scoring modules.

Calls the PUBLIC `graphs.nodes.scanner_node` wrappers (original caller signature, injected `facade`) on a fixed,
deterministic input set and records the canonical-JSON result or exception type/message. `generate` is run once on the
pinned BASE tree (PYTHONPATH = git-archive of the BASE commit); the test re-runs `compute` on the current tree.
Offline: environment keys read by the bodies are pinned, cwd is a disposable directory (the compatibility-bias reader
looks under `reports/canonical/<day>` relative to cwd, so an empty and a seeded directory are both covered).

  generate <out.json>     compute <out.json>
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ENV_KEYS = ("SCANNER_ENFORCE_LIVE_EQUITY_SYMBOLS", "PYTEST_CURRENT_TEST", "MEMORY_BIAS_OBSERVATION_ONLY",
            "SCANNER_MEMORY_BIAS_OBSERVATION_ONLY", "SCANNER_W_NEWS", "SCANNER_W_GLOBAL", "SCANNER_NEWS_WEIGHT",
            "SCANNER_GLOBAL_WEIGHT")

STATES = [
    {},
    {"global_sentiment_signal": {"score": 0.4, "status": "ok"}, "news_sentiment_signal": {"005930": {"score": -0.3}}},
    {"mock_global_sentiment": 2.5, "news_sentiment": {"005930": 0.7, "000660": "x"}},
    {"global_sentiment": {"score": -1.7}, "policy": {"global_sentiment": 0.2}},
    {"global_sentiment": 0.1, "memory_bias_observation_only": "true", "scanner_policy": {"enforce_live_equity_symbols": "0"}},
    {"policy": {"global_sentiment": {"score": 0.9}}, "news_sentiment_signal": {"A": {"score": "bad"}}},
]
POLICIES = [{}, {"scanner_weights": {"news": 0.3, "global": 0.1}}, {"w_news": "0.5", "w_global": -1},
            {"scanner_score_weights": {"momentum": 2}}, {"enforce_live_equity_symbols": True}]
CANDS = [[], ["005930", {"symbol": "000660"}, "SPY", "", None, {"symbol": "KRW-BTC"}],
         [{"symbol": "035420", "risk_score": 0.2}]]


def _cases():
    out = []
    for i, st in enumerate(STATES):
        for fn in ("_get_global_sentiment_score", "_get_news_sentiment_map", "_get_global_sentiment_signal",
                   "_get_news_sentiment_signal_map", "_memory_bias_observation_only"):
            out.append((fn, [st], {}))
        for j, pol in enumerate(POLICIES):
            out.append(("_enforce_live_equity_symbols", [st, pol], {}))
        out.append(("_resolve_compatibility_bias_context", [st], {"limit": 5}))
    for pol in POLICIES:
        out.append(("_get_scanner_weights", [pol], {}))
        out.append(("_resolve_scanner_score_weights", [pol], {}))
    for c in CANDS:
        out.append(("_filter_live_equity_candidates", [c], {}))
        for st in STATES[:3]:
            out.append(("_summarize_quote_metric_coverage", [c],
                        {"skill_quotes": {"005930": {"price": 70000}, "000660": {"cur": 0}}, "state": st}))
            out.append(("_should_refresh_scanner_features", [],
                        {"state": st, "candidates": c,
                         "quote_metric_coverage": {"live_equity_candidates": 2, "quote_rows_with_activity": 0}}))
    for txt in ("", "005930", "한글-테마", "x" * 200):
        out.append(("_stable_unit_hash", [txt], {}))
    for vals in (None, [], ["Momentum", " value ", "", None, "momentum"], "breakout,theme", {"a": 1}):
        out.append(("_normalize_priority_list", [vals], {}))
    for a, m in ((None, None), (1.0, 1.0), (0.98, 1.0), ("x", 1), (3, 0)):
        out.append(("_calc_reclaim_proximity", [], {"actual": a, "minimum": m}))
        out.append(("_calc_breakout_proximity", [], {"actual": a, "minimum": m}))
    for res in ({}, {"chart_structure_features": {"human_chart_context": {"exit_risk_score": 0.7, "entry_chart_score": 0.4}}},
                {"chart_structure_features": {"human_chart_context": "bad"}}, None):
        out.append(("_scanner_chart_fit_from_entry_result", [res], {}))
    for pb, pr, rt, ta in (("", None, "", ""), ("breakout", ["momentum", "theme"], "risk_off", "high"),
                           ("pullback", ["value"], "neutral", "low"), ("defensive", "x", "risk_on", "balanced")):
        out.append(("_scanner_macro_focus", [], {"playbook": pb, "scanner_priority": pr, "risk_tone": rt,
                                                   "trade_aggressiveness": ta}))
        for row in ({}, {"return20": 0.05, "ma20_gap": 0.02, "adx14": 30, "rolling_drawdown20": -0.04},
                    {"return20": -0.2, "ma20_gap": 0.2, "ma60_gap": 0.1, "ma120_gap": 0.1, "trend_strength": 0.6,
                     "adx14": 12, "volume_spike20": 3, "cross_section_rank": 0.9, "rolling_drawdown20": -0.3,
                     "volatility20": 0.09, "gap_pct": 0.05}):
            out.append(("_compute_scanner_macro_chart_fit", [], dict(
                feature_row=row, ma_alignment_component=0.6, trend_component=0.4, adx_component=0.5,
                momentum_component=0.3, volume_surge_component=0.7, vwap_alignment_component=0.2,
                cross_section_rank_component=0.8, volatility_penalty=0.1, gap_penalty=0.05, playbook=pb,
                scanner_priority=pr, risk_tone=rt, trade_aggressiveness=ta, bias_cap=0.06)))
    return out


def compute():
    import importlib
    node = importlib.import_module("graphs.nodes.scanner_node")
    saved = {k: os.environ.pop(k) for k in list(os.environ) if k in ENV_KEYS}
    os.environ["SCANNER_ENFORCE_LIVE_EQUITY_SYMBOLS"] = "1"
    cwd = os.getcwd()
    tmp = Path(tempfile.mkdtemp(prefix="v2053_"))
    rows = []
    try:
        os.chdir(tmp)
        for idx, (fn, args, kwargs) in enumerate(_cases()):
            if fn == "_resolve_compatibility_bias_context" and idx % 2:
                day_dir = tmp / "reports" / "canonical"
                day_dir.mkdir(parents=True, exist_ok=True)
            try:
                res = {"ok": getattr(node, fn)(*json.loads(json.dumps(args)), **json.loads(json.dumps(kwargs)))}
            except Exception as exc:  # noqa: BLE001
                res = {"exc": type(exc).__name__, "msg": str(exc)[:160]}
            rows.append({"fn": fn, "args": args, "kwargs": kwargs,
                         "result": json.loads(json.dumps(res, sort_keys=False, default=repr))})
    finally:
        os.chdir(cwd)
        shutil.rmtree(tmp, ignore_errors=True)
        for k in ENV_KEYS:
            os.environ.pop(k, None)
        os.environ.update(saved)
    return rows


if __name__ == "__main__":
    rows = compute()
    Path(sys.argv[2]).write_text(json.dumps({"cases": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(sys.argv[1].upper(), len(rows))
