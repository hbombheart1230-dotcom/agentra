"""RF-016 LEAD independent isolated news query target boundary.
GitHub source: libs/agents/strategist/context/news_compaction.py @ blob c4ba0ddfb70b34b681f3043f897d19803dde3b25
The embedded function is extracted byte-for-byte from the named GitHub blob; only the pure
function is compiled. No import of the production facade, network, broker or filesystem.
Run: PYTHONDONTWRITEBYTECODE=1 python docs/refactor/work_orders/evidence/lead_rf016_news_query_targets.py
     PYTHONDWRITEBYTECODE=1 python -O docs/refactor/work_orders/evidence/lead_rf016_news_query_targets.py
"""
import copy
from types import SimpleNamespace
from typing import Any, List
SOURCE = "def _build_market_news_query_targets_r3_impl(\n    *,\n    state,\n    policy,\n    global_signal,\n    market_context_inputs,\n    theme_hints,\n    facade,\n):\n    limit = max(\n        3,\n        facade._to_int(\n            policy.get(\"strategist_news_query_limit\")\n            if policy.get(\"strategist_news_query_limit\") is not None\n            else facade.os.getenv(\"STRATEGIST_NEWS_QUERY_LIMIT\", \"10\"),\n            10,\n        ),\n    )\n    out: List[str] = []\n    seen: set[str] = set()\n\n    explicit_targets: List[Any] = []\n    if isinstance(state.get(\"news_query_targets\"), list):\n        explicit_targets.extend(list(state.get(\"news_query_targets\") or []))\n    if isinstance(policy.get(\"news_query_targets\"), list):\n        explicit_targets.extend(list(policy.get(\"news_query_targets\") or []))\n    env_targets = str(facade.os.getenv(\"NEWS_QUERY_TARGETS\", \"\") or \"\").strip()\n    if env_targets:\n        explicit_targets.extend([x.strip() for x in env_targets.split(\",\") if str(x).strip()])\n    for raw in explicit_targets:\n        facade._append_unique_text(out, seen, raw)\n\n    global_score = facade._signal_score(global_signal)\n    macro_risk = facade._to_float(market_context_inputs.get(\"macro_risk\"), 0.0)\n    index_trend = facade._to_float(market_context_inputs.get(\"index_trend\"), 0.0)\n    realized_volatility = facade._to_float(market_context_inputs.get(\"realized_volatility\"), 0.0)\n    market_breadth = facade._to_float(market_context_inputs.get(\"market_breadth\"), 0.0)\n    fear_index = global_signal.get(\"fear_index\") if isinstance(global_signal.get(\"fear_index\"), dict) else {}\n    vix_level = facade._to_float(fear_index.get(\"level\"), 0.0)\n    vix_pressure = facade._to_float(fear_index.get(\"level_pressure\"), 0.0)\n    elevated_fear = vix_level >= 25.0 or vix_pressure >= 0.25\n    theme_news_terms = facade._theme_news_query_terms(theme_hints, limit=4)\n    for raw in theme_news_terms:\n        facade._append_unique_text(out, seen, raw)\n    if global_score <= -0.20 or macro_risk >= 0.65 or elevated_fear:\n        base_queries = [\"코스피\", \"미국 증시\", \"국제유가\", \"환율\", \"중동\"]\n    elif global_score >= 0.20 and index_trend >= -0.05:\n        base_queries = [\"코스피\", \"코스닥\", \"미국 증시\", \"위험선호\", \"주도주\"]\n    else:\n        base_queries = [\"코스피\", \"코스닥\", \"미국 증시\", \"증시 전망\", \"거시경제\"]\n    for raw in base_queries:\n        facade._append_unique_text(out, seen, raw)\n\n    if not theme_news_terms:\n        for raw in list(theme_hints or [])[:5]:\n            for q in facade._theme_to_news_queries(raw)[:2]:\n                facade._append_unique_text(out, seen, q)\n\n    if realized_volatility >= 0.03:\n        facade._append_unique_text(out, seen, \"변동성 확대\")\n    if market_breadth <= 0.40:\n        for raw in (\"하락 종목 수\", \"약세 업종\"):\n            facade._append_unique_text(out, seen, raw)\n    elif market_breadth >= 0.60:\n        for raw in (\"상승 종목 수\", \"주도 섹터\"):\n            facade._append_unique_text(out, seen, raw)\n\n    if macro_risk >= 0.65 or elevated_fear:\n        for raw in (\"국제유가\", \"환율\", \"달러\", \"중동\", \"방산\", \"금\"):\n            facade._append_unique_text(out, seen, raw)\n    elif global_score <= -0.20:\n        for raw in (\"환율\", \"달러\", \"국채금리\", \"금\", \"방어주\"):\n            facade._append_unique_text(out, seen, raw)\n    elif global_score >= 0.20 and index_trend >= 0.10:\n        for raw in (\"주도주\", \"실적주\", \"수출주\"):\n            facade._append_unique_text(out, seen, raw)\n\n    for key in (\"macro_events\", \"global_events\", \"major_events\"):\n        values = state.get(key)\n        if not isinstance(values, list):\n            continue\n        for raw in list(values)[:3]:\n            facade._append_unique_text(out, seen, raw)\n        if values:\n            break\n\n    return out[:limit]\n"
def check(cond, label):
    if not cond: raise SystemExit("FAIL " + label)
def fnv32(s):
    h = 2166136261
    for c in s: h = ((h ^ ord(c)) * 16777619) & 0xffffffff
    return h
check(len(SOURCE) == 3658 and fnv32(SOURCE) == 0x0da63247, "source checksum")
ns = {"Any": Any, "List": List}
exec(compile(SOURCE, "<RF016 isolated GitHub function>", "exec"), ns)
fn = ns["_build_market_news_query_targets_r3_impl"]
class Facade:
    def __init__(self, env=None, terms=None):
        self.env, self.terms = env or {}, terms or []
        self.os = SimpleNamespace(getenv=lambda key, default="": self.env.get(key, default))
    def _to_int(self, x, default):
        try: return int(x)
        except (TypeError, ValueError): return default
    def _to_float(self, x, default):
        try: return float(x)
        except (TypeError, ValueError): return default
    def _signal_score(self, x): return self._to_float(x.get("score"), 0.0)
    def _theme_news_query_terms(self, themes, *, limit): return self.terms[:limit]
    def _theme_to_news_queries(self, x): return [str(x)+" 뉴스", str(x)+" 동향"]
    def _append_unique_text(self, out, seen, x):
        x = str(x or "").strip()
        if x and x not in seen: seen.add(x); out.append(x)
count = 0
def run(state=None, policy=None, signal=None, market=None, themes=None, facade=None):
    global count
    state, policy, signal, market = ({} if x is None else x for x in (state, policy, signal, market))
    themes, facade = ([] if themes is None else themes), (facade or Facade())
    original = copy.deepcopy((state, policy, signal, market, themes))
    out = fn(state=state, policy=policy, global_signal=signal,
             market_context_inputs=market, theme_hints=themes, facade=facade)
    check(original == (state, policy, signal, market, themes), "input mutation")
    count += 1
    return out
r=run();check(r[:3]==["코스피","코스닥","미국 증시"],"neutral")
r=run(state={"news_query_targets":[" A ","A","B"]},policy={"news_query_targets":["B","C"],"strategist_news_query_limit":3},facade=Facade(env={"NEWS_QUERY_TARGETS":"C,D"}));check(r==["A","B","C"],"priority and cap")
r=run(policy={"strategist_news_query_limit":"bad"},facade=Facade(env={"STRATEGIST_NEWS_QUERY_LIMIT":"4"}));check(len(r)==7,"invalid policy fallback")
r=run(facade=Facade(env={"STRATEGIST_NEWS_QUERY_LIMIT":"4"}));check(len(r)==4,"env limit")
r=run(policy={"strategist_news_query_limit":1});check(len(r)==3,"min cap")
r=run(signal={"score":-.3});check(r[:3]==["코스피","미국 증시","국제유가"],"bearish")
r=run(signal={"score":.4},market={"index_trend":.15,"market_breadth":.8},policy={"strategist_news_query_limit":20});check("실적주" in r and "상승 종목 수" in r,"bull")
r=run(signal={"score":.4},market={"index_trend":-.06},policy={"strategist_news_query_limit":20});check("증시 전망" in r and "위험선호" not in r,"trend")
r=run(market={"macro_risk":.65},policy={"strategist_news_query_limit":20});check("방산" in r,"risk")
r=run(signal={"fear_index":{"level":25}},policy={"strategist_news_query_limit":20});check("방산" in r,"fear level")
r=run(signal={"fear_index":{"level_pressure":.25}},policy={"strategist_news_query_limit":20});check("방산" in r,"fear pressure")
r=run(market={"realized_volatility":.03,"market_breadth":.6},policy={"strategist_news_query_limit":20});check("변동성 확대" in r and "주도 섹터" in r,"volatility")
r=run(themes=["반도체"],policy={"strategist_news_query_limit":20});check("반도체 뉴스" in r,"theme fallback")
r=run(themes=["ignored"],facade=Facade(terms=["양자","비만"]),policy={"strategist_news_query_limit":20});check("양자" in r and "ignored 뉴스" not in r,"theme terms")
r=run(state={"macro_events":["M1","M2","M3","M4"],"global_events":["G1"]},policy={"strategist_news_query_limit":20});check("M1" in r and "M4" not in r and "G1" not in r,"event priority")
r=run(state={"macro_events":[],"global_events":["G1"]},policy={"strategist_news_query_limit":20});check("G1" in r,"event fallback")
facade=Facade(env={"NEWS_QUERY_TARGETS":"E1"})
check(run(facade=facade,policy={"strategist_news_query_limit":20})[0]=="E1","env initial")
facade.env["NEWS_QUERY_TARGETS"]="E2"
check(run(facade=facade,policy={"strategist_news_query_limit":20})[0]=="E2","env use-time")
for args in ({"state":[]},{"policy":[]},{"signal":[]},{"market":[]}):
    try: run(**args)
    except AttributeError: count += 1
    else: raise SystemExit("FAIL expected AttributeError")
print("RF016_NEWS_QUERY_LEAD_OK cases=%d source=c4ba0ddf fnv=da63247 io=none mode=%s" % (count, "normal" if __debug__ else "-O"))
