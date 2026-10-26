# Offline fake/monkeypatch checks for RF-050 libs/llm policy -> role env -> model fallback resolution (no API, no writes).
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib
from pathlib import Path
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+"): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
Path.write_text = blocked("write_text"); Path.mkdir = blocked("mkdir")
def check(cond, msg):
    if not cond: raise SystemExit("CHECK_FAILED: " + msg)

names = importlib.import_module("libs.llm.model_names")
cat = importlib.import_module("libs.llm.model_catalog")
lr = importlib.import_module("libs.llm.llm_router")
legacy = importlib.import_module("libs.llm.router")
pkg = importlib.import_module("libs.llm")
out = {}

# model_names
n = names.normalize_openrouter_model_name
check([n("auto"), n(" FREE "), n("openrouter/free"), n("a/b"), n(None)] == ["openrouter/auto", "openrouter/free", "openrouter/free", "a/b", ""], "model_names")
out["names"] = 5

# model_catalog.resolve_model_profile
r = cat.resolve_model_profile("fast_free")
check(r["primary"] == "minimax/minimax-m2.5" and r["fallback"] == "deepseek/deepseek-v3.2" and len(r["cards"]) == 2, "profile fast_free")
r2 = cat.resolve_model_profile("nope", default_profile="strong_reasoning")
check(r2["profile"] == "strong_reasoning" and r2["requested_profile"] == "nope", "unknown profile -> default")
r3 = cat.resolve_model_profile(None, default_profile="also_unknown")
check(r3["profile"] == "also_unknown" and r3["primary"] == "deepseek/deepseek-v3.2", "unknown default -> balanced models, chosen name retained")
check(cat.get_model_card("x/custom")["tier"] == "custom" and cat.get_model_card("auto")["name"] == "openrouter/auto", "model card custom")
out["profile"] = 4

# resolve_policy_llm_slot: source precedence (synthetic policies only)
def slot(policy, *path, dp="balanced"): return cat.resolve_policy_llm_slot(policy, *path, default_profile=dp)
sl = {"primary": "syn/primary", "fallback": "syn/fb", "profile": "fast_free"}
pol = {
    "applied_policy": {"llm": {"s": dict(sl, primary="syn/p1")}},
    "commander": {"applied_policy": {"llm": {"s": dict(sl, primary="syn/p2")}}},
    "reporter_output": {"applied_policy": {"llm": {"s": dict(sl, primary="syn/p3")}}},
    "llm": {"s": dict(sl, primary="syn/p4")},
    "reporter_policy": {"llm": {"s": dict(sl, primary="syn/p5")}},
}
order = [("applied_policy.llm", "applied_policy"), ("commander.applied_policy.llm", "commander"),
         ("reporter_output.applied_policy.llm", "reporter_output"), ("llm", "llm"), ("reporter_policy.llm", "reporter_policy")]
cur = json.loads(json.dumps(pol))
for i, (src, key) in enumerate(order):
    s = slot(cur, "s")
    check(s["profile_source"] == src and s["primary"] == "syn/p%d" % (i + 1), "slot precedence " + src)
    cur.pop(key)
s = slot(cur, "s"); check(s["profile_source"] == "default_profile" and s["primary"] == "deepseek/deepseek-v3.2" and s["fallback"] == "minimax/minimax-m2.5", "slot default")
s = slot({"applied_policy": {"llm": {"s": {"model": "auto"}}}}, "s")
check(s["primary"] == "openrouter/auto" and s["fallback"] == "minimax/minimax-m2.5", "slot model alias + profile fallback")
s = slot({"applied_policy": {"llm": {"s": {}}}}, "s", dp="fast_free")
check(s["profile_source"] == "default_profile" and s["primary"] == "minimax/minimax-m2.5", "empty slot ignored")
check(slot(None, "s")["profile_source"] == "default_profile" and slot("notdict", "s")["primary"], "non-dict policy")
s = slot({"applied_policy": {"llm": {"s": {"primary": "p", "fallback": "p"}}}}, "s"); check(s["models"] == ["p"], "dedupe")
out["slot"] = 9

# llm_router.LLMRouter.resolve: policy > role env chain > default env > role default
class FakeClient:
    def __init__(self): self.calls = []
    def chat_completions(self, payload): self.calls.append(dict(payload)); return {"echo": payload["model"]}
    def extract_text(self, resp): return "T:" + str(resp.get("echo"))
R = lr.LLMRouter
def env(**kv):
    for k in [k for k in os.environ if k.startswith("OPENROUTER_")]: del os.environ[k]
    os.environ.update(kv)
router = R(client=None)
env(); r = router.resolve("strategist"); check(r.model == "deepseek/deepseek-v3.2" and r.temperature == 0.2 and r.max_tokens == 512, "role default")
check(router.resolve("daily_report").model == "moonshotai/kimi-k2.5" and router.resolve("unknown_role").model == "", "role default 2 / unknown empty")
env(OPENROUTER_DEFAULT_MODEL="syn/default"); check(router.resolve("strategist").model == "syn/default", "default env over role default")
env(OPENROUTER_DEFAULT_MODEL="syn/default", OPENROUTER_MODEL_STRATEGIST="syn/role"); check(router.resolve("strategist").model == "syn/role", "role env over default")
check(router.resolve("strategist", policy={"openrouter_model": "syn/pol", "model": "syn/pol2"}).model == "syn/pol", "policy openrouter_model first")
check(router.resolve("strategist", policy={"model": "syn/pol2"}).model == "syn/pol2", "policy model")
env(OPENROUTER_MODEL_REPORTER="syn/rep", OPENROUTER_MODEL_OPERATOR_UI="syn/ui", OPENROUTER_MODEL_REPORTER_FINAL="syn/fin")
check(router.resolve("reporter_final").model == "syn/fin" and router.resolve("daily_report").model == "syn/fin", "final/daily chain")
check(router.resolve("operator_ui").model == "syn/ui" and router.resolve("reporter_intraday").model == "syn/ui", "ui/intraday chain")
env(OPENROUTER_MODEL_REPORTER="syn/rep")
check(all(router.resolve(x).model == "syn/rep" for x in ("reporter_final", "daily_report", "operator_ui", "reporter_intraday")), "REPORTER alias fallback")
check(router.resolve("trade_report").model == "nvidia/nemotron-3-ultra-550b-a55b:free", "trade_report not covered by REPORTER alias")
env(OPENROUTER_DEFAULT_MODEL="auto", OPENROUTER_MODEL_STRATEGIST="free")
check(router.resolve("strategist").model == "openrouter/free", "free kept")
env(OPENROUTER_DEFAULT_MODEL="auto"); check(router.resolve("strategist").model == "deepseek/deepseek-v3.2", "auto env -> skipped -> role default")
check(router.resolve("strategist", policy={"model": "auto"}).model == "deepseek/deepseek-v3.2", "auto policy sanitized")
env(OPENROUTER_DEFAULT_TEMPERATURE="0.7", OPENROUTER_DEFAULT_MAX_TOKENS="1024")
r = router.resolve("strategist"); check((r.temperature, r.max_tokens) == (0.7, 1024), "sampling env")
r = router.resolve("strategist", policy={"temperature": 0.1, "max_tokens": 9}); check((r.temperature, r.max_tokens) == (0.1, 9), "sampling policy")
r = router.resolve("strategist", policy={"temperature": 0}); check(r.temperature == 0.7, "falsy temperature 0 falls to env (observed)")
env(OPENROUTER_DEFAULT_MAX_TOKENS="x")
try:
    router.resolve("strategist"); check(False, "bad max tokens should raise")
except ValueError:
    pass
env()
check(R(client=None).chat("strategist", []) == "", "chat no client empty")
fc = FakeClient(); rr = R(client=fc)
check(rr.chat("strategist", [{"role": "user", "content": "x"}], policy={"top_p": 0.5, "timeout_sec": 3, "bogus": 1, "response_format": {"type": "json_object"}}) == "T:deepseek/deepseek-v3.2", "chat text")
p = fc.calls[0]; check(p["top_p"] == 0.5 and p["__timeout_sec"] == 3 and "bogus" not in p and p["response_format"] == {"type": "json_object"}, "chat passthrough")
out["router"] = 22

# legacy router: thin wrapper over text router resolve; raw response; None client; extra override
lg = legacy.LLMRouter(client=fc)
fc.calls.clear()
raw = lg.chat(role="operator_ui", policy={"model": "syn/lg", "timeout_sec": 4, "response_format": "j"}, messages=[{"role": "user", "content": "q"}], extra={"max_tokens": 77})
check(raw == {"echo": "syn/lg"} and fc.calls[0]["max_tokens"] == 77 and fc.calls[0]["__timeout_sec"] == 4 and fc.calls[0]["response_format"] == "j", "legacy raw")
check(legacy.TextLLMRouter is lr.LLMRouter and legacy.ModelSpec("m").max_tokens == 256, "legacy aliases")
lg.client = None; check(lg.chat(role="x", policy={}, messages=[]) == {}, "legacy no client")
check(pkg.LLMRouter is lr.LLMRouter and pkg.LLMRouter is not legacy.LLMRouter and set(pkg.__all__) == {"LLMRoute", "LLMRouter", "OpenRouterClient"}, "package exports text router only")
out["legacy"] = 5

check(not bad, "blocked attempts: %r" % bad)
print("RF050_POLICY_LOOKUP_OK names=%d profile=%d slot=%d router=%d legacy=%d blocked=0 api_calls=0 debug=%s" % (out["names"], out["profile"], out["slot"], out["router"], out["legacy"], __debug__))
