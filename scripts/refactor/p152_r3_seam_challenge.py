"""P1.5.2 R3 evidence tool: direct synthetic differential + call-time seam challenge (offline, no LLM/broker).

Run with cwd = a source tree (baseline or feature). Env: R3_MOVED_FREE (module->{function->[facade globals]}), R3_OUT.
Scenarios patch façade globals before the call and from inside a callback during the call.
"""
import importlib, inspect, json, os, sys
from unittest.mock import MagicMock

sys.path.insert(0, os.getcwd())
MOVED = json.load(open(os.environ["R3_MOVED_FREE"], encoding="utf-8"))  # {module: {name: [free names]}}
out = {"direct": {}, "seam": {}}


def norm(o):
    if isinstance(o, dict):
        return {str(k): norm(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
    if isinstance(o, (list, tuple)):
        return [norm(v) for v in o]
    if isinstance(o, (str, int, float, bool)) or o is None:
        return o
    return "<%s>" % type(o).__qualname__


# ---- Part A: direct synthetic differential for the 2 functions no recorded test exercised
md = importlib.import_module("libs.reporting.trade_report_markdown_clean")
ai = importlib.import_module("libs.reporting.trade_report_ai")
cases = []
vals = [None, "", "x", 0, 1, 3, 0.5, -2, {}, {"count": 2}, [1, 2], True]
names = [None, "", "win_rate", "stop_loss", "momentum", "late_entry", "overextended", "mean_reversion", "손절", "추격매수"]
for n in names:
    for d in (None, "", "detail text", "반복 손실", {"k": 1}):
        for v in (None, "", 0, 3, 0.25, "high", {"x": 1}):
            try:
                r = md._humanize_reporter_pattern(n, d, v)
            except Exception as e:  # noqa
                r = "EXC:%s:%s" % (type(e).__name__, str(e)[:60])
            cases.append(["humanize", repr((n, d, v)), r])
stories = [
    {}, None, {"symbol": "005930"}, {"trade_id": "t1", "day": "2026-10-12", "symbol": "005930", "action": "BUY"},
    {"execution": {"action": "BUY", "qty": 3, "avg_price": 71000}, "strategist": {"selected_symbol": "005930"}},
    {"trade_lifecycle": {"entry": {"price": 70000, "qty": 2}, "exit": {"price": 71500, "qty": 2, "reason": "take_profit"}},
     "scanner": {"selected_symbol": "000660"}, "monitor": {"pnl_pct": 1.2}},
    {"execution": {"action": "SELL", "fills": [{"price": 70000, "qty": 1}, {"price": 70100, "qty": 1}]}},
]
for s in stories:
    try:
        r = norm(ai.resolve_shared_trade_facts(s))
    except Exception as e:  # noqa
        r = "EXC:%s:%s" % (type(e).__name__, str(e)[:60])
    cases.append(["shared_facts", json.dumps(norm(s), sort_keys=True, default=str), r])
out["direct"] = cases

# ---- Part B: call-time seam challenge (patch before call / within call via callback)
for modname, funcs in MOVED.items():
    mod = importlib.import_module(modname)
    for fname, free in funcs.items():
        fn = getattr(mod, fname)
        sig = inspect.signature(fn)
        req = [p for p in sig.parameters.values() if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        kwreq = [p for p in sig.parameters.values() if p.default is p.empty and p.kind == p.KEYWORD_ONLY]
        targets = [n for n in free if n != fname and callable(getattr(mod, n, None)) and not inspect.ismodule(getattr(mod, n))
                   and not isinstance(getattr(mod, n), type)]
        rec_by_scenario = {}
        for label, mk in (("empty_dict", lambda: {}), ("mock", lambda: MagicMock()), ("text", lambda: "abc")):
            for scenario in ("pre_call", "within_call"):
                orig = {n: getattr(mod, n) for n in targets}
                events = []
                state = {"switched": False}

                def make(n, ver):
                    def stub(*a, **k):
                        events.append("%s:%s" % (ver, n))
                        if scenario == "within_call" and ver == "v1" and not state["switched"]:
                            state["switched"] = True
                            for m in targets:
                                setattr(mod, m, make(m, "v2"))
                        return MagicMock()
                    return stub
                for n in targets:
                    setattr(mod, n, make(n, "v1"))
                try:
                    try:
                        fn(*[mk() for _ in req], **{p.name: mk() for p in kwreq})
                        res = "ok"
                    except Exception as e:  # noqa
                        res = "EXC:" + type(e).__name__
                finally:
                    for n, v in orig.items():
                        setattr(mod, n, v)
                rec_by_scenario["%s/%s" % (label, scenario)] = [res, events]
        out["seam"]["%s.%s" % (modname.rsplit(".", 1)[-1], fname)] = {"targets": len(targets), "runs": rec_by_scenario,
                                                                       "recursive": fname in free}
json.dump(out, open(os.environ["R3_OUT"], "w", encoding="utf-8"), ensure_ascii=False)
print("done", len(out["direct"]), len(out["seam"]))
