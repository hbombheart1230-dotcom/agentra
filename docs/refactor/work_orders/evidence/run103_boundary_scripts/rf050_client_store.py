# RF-050 libs/llm: openrouter_client (fake urlopen) + model_catalog_store (fake urlopen, tmp-only writes).
import os, sys, json, io, shutil, socket, subprocess, sqlite3, builtins, importlib, urllib.request, urllib.error
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "AI_STRATEGIST")): del os.environ[k]
root = Path("/tmp/rf050_fixed"); shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
import ssl, http.client
oc = importlib.import_module("libs.llm.openrouter_client"); st = importlib.import_module("libs.llm.model_catalog_store")
bad, outside = [], []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
def inside(p):
    try: return Path(os.path.abspath(str(p))).is_relative_to(root)
    except Exception: return False
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): outside.append("open:" + str(f)); raise OSError("blocked")
    return _open(f, mode, *a, **k)
builtins.open = gopen
_wt, _mk = Path.write_text, Path.mkdir
Path.write_text = lambda self, *a, **k: (outside.append("write_text:" + str(self)) or (_ for _ in ()).throw(OSError("blocked"))) if not inside(self) else _wt(self, *a, **k)
Path.mkdir = lambda self, *a, **k: (outside.append("mkdir:" + str(self)) or (_ for _ in ()).throw(OSError("blocked"))) if not inside(self) else _mk(self, *a, **k)
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
out = {}
# ---- fake urlopen
seen = []
class Resp:
    def __init__(self, body): self.body = body
    def read(self): return self.body
    def __enter__(self): return self
    def __exit__(self, *a): return False
def set_urlopen(behaviour):
    def u(req, timeout=None, *a, **k):
        url = req if isinstance(req, str) else req.full_url
        seen.append({"url": url, "timeout": timeout, "method": getattr(req, "method", None), "headers": dict(getattr(req, "headers", {}) or {}), "data": getattr(req, "data", None)})
        r = behaviour(req)
        if isinstance(r, Exception): raise r
        return Resp(r)
    urllib.request.urlopen = u; st.urlopen = u
    return u
# constructor / from_env
try: oc.OpenRouterClient(oc.OpenRouterConfig(api_key="")); out["ctor_empty"] = "no-raise"
except ValueError as e: out["ctor_empty"] = "ValueError"
out["from_env_none"] = oc.OpenRouterClient.from_env() is None
os.environ["AI_STRATEGIST_API_KEY"] = "k-ai"; c = oc.OpenRouterClient.from_env(); out["from_env_ai_key"] = [c.cfg.api_key, c.cfg.base_url, c.cfg.timeout_sec, c.cfg.x_title, c.cfg.http_referer]
os.environ.update({"OPENROUTER_API_KEY": "k-or", "OPENROUTER_BASE_URL": "  https://x.example/api/  ", "OPENROUTER_HTTP_REFERER": "http://ref", "AI_STRATEGIST_TIMEOUT_SEC": "7"}); c = oc.OpenRouterClient.from_env()
out["from_env_full"] = [c.cfg.api_key, c.cfg.base_url, c.cfg.timeout_sec, c.cfg.http_referer]
os.environ["OPENROUTER_TIMEOUT_SEC"] = "3"; out["from_env_timeout_pref"] = oc.OpenRouterClient.from_env().cfg.timeout_sec
os.environ["OPENROUTER_TIMEOUT_SEC"] = "abc"
try: oc.OpenRouterClient.from_env(); out["from_env_bad_timeout"] = "no-raise"
except ValueError: out["from_env_bad_timeout"] = "ValueError"
os.environ["OPENROUTER_BASE_URL"] = "   "; os.environ["OPENROUTER_TIMEOUT_SEC"] = "5"; out["from_env_blank_base"] = oc.OpenRouterClient.from_env().cfg.base_url
for k in ("OPENROUTER_API_KEY", "AI_STRATEGIST_API_KEY", "OPENROUTER_BASE_URL", "OPENROUTER_HTTP_REFERER", "OPENROUTER_TIMEOUT_SEC", "AI_STRATEGIST_TIMEOUT_SEC"): os.environ.pop(k, None)
# chat_completions
cl = oc.OpenRouterClient(oc.OpenRouterConfig(api_key="k", base_url="https://h.example/v1/", http_referer="http://r", x_title="T", timeout_sec=9))
set_urlopen(lambda req: json.dumps({"choices": [{"message": {"content": "hi"}}]}).encode())
payload = {"model": "m", "messages": [], "__timeout_sec": 2}
r = cl.chat_completions(payload); out["chat_ok"] = [r, seen[-1]["url"], seen[-1]["timeout"], seen[-1]["method"], seen[-1]["headers"], json.loads(seen[-1]["data"]), sorted(payload)]
cl.chat_completions({"model": "m", "__timeout_sec": 0}); out["chat_timeout_zero_uses_cfg"] = seen[-1]["timeout"]
cl.chat_completions({"model": "m"}); out["chat_timeout_default"] = seen[-1]["timeout"]
cl2 = oc.OpenRouterClient(oc.OpenRouterConfig(api_key="k", x_title=None)); cl2.chat_completions({"model": "m"}); out["chat_min_headers"] = [seen[-1]["url"], sorted(seen[-1]["headers"])]
class HE(urllib.error.HTTPError):
    def __init__(self, code, body, reason="R"): super().__init__("u", code, reason, {}, io.BytesIO(body) if body is not None else None); self._b = body
    def read(self): 
        if self._b is None: raise OSError("no body")
        return self._b
for name, exc in (("http429_body", HE(429, b'{"e":"rate"}')), ("http500_nobody", HE(500, None, "Server Err")), ("http_emptybody", HE(502, b"", "Bad GW")), ("urlerror", urllib.error.URLError("nodns")), ("badjson", None), ("timeout", TimeoutError("t")), ("oserror", OSError("o"))):
    set_urlopen((lambda req, e=exc: e) if exc is not None else (lambda req: b"not json"))
    try: cl.chat_completions({"model": "m"}); out["chat_" + name] = "no-raise"
    except Exception as e: out["chat_" + name] = [type(e).__name__, str(e)[:80], type(e.__cause__).__name__ if e.__cause__ else None]
# extract_text variants
ex = oc.OpenRouterClient.extract_text
out["extract"] = [ex(x) for x in ({}, {"choices": []}, {"choices": [{"text": " t "}]}, {"choices": [{"message": "x"}]}, {"choices": [{"message": {"parsed": {"a": 1}}}]}, {"choices": [{"message": {"content": "c"}}]}, {"choices": [{"message": {"content": {"json": {"b": 2}}}}]}, {"choices": [{"message": {"content": ["p1", {"text": "p2"}, 5, {"json": {"z": 1}}]}}]}, {"choices": [{"message": {"content": ["p1", {"text": "p2"}, 5]}}]}, {"choices": [{"message": {"content": "", "tool_calls": [{"function": {"arguments": "{\"x\":1}"}}]}}]}, {"choices": [{"message": {"content": "", "tool_calls": [{"function": {"arguments": {"y": 2}}}, "bad"]}}]}, {"choices": [{"message": {"reasoning": "why"}}]}, {"choices": [{"message": {}}], "output_text": "ot"}, {"choices": [{"message": {}}], "output": [{"content": [{"text": "a"}, {"text": "b"}]}, "bad"]}, {"choices": [{"message": {}}], "output": []}, {"choices": [None]})]
# ---- model_catalog_store (tmp-only)
cat = root / "catalog"
models = {"data": [{"id": "minimax/minimax-m2.5", "name": "MiniMax M2.5", "context_length": 200000, "pricing": {"prompt": "0", "completion": "0"}, "supported_parameters": ["response_format"]},
                   {"id": "anthropic/claude-opus-4", "name": "Opus", "context_length": 300000, "pricing": {"prompt": "0.00001", "completion": "0.00005"}, "supported_parameters": ["tools"]},
                   {"id": "x/flash-mini:free", "name": "Flash", "context_length": "bad" if False else 8000, "pricing": {"prompt": "0.000001", "completion": "0.0000005"}, "supported_parameters": ["structured_outputs"]},
                   {"id": "", "name": "noid"}, "notadict", {"id": "deepseek/deepseek-v3.2", "pricing": "x"}, {"id": "z/reasoning-r1", "pricing": {"prompt": "0.001", "completion": 0.001}}]}
set_urlopen(lambda req: json.dumps(models).encode())
f = st.fetch_openrouter_models(); out["store_fetch"] = [f["fetch_status"], f["model_count"], f["source_url"], seen[-1]["timeout"]]
res = st.sync_openrouter_model_catalog(catalog_dir=cat); out["store_sync_remote"] = {k: (v.replace(str(root), "ROOT") if isinstance(v, str) else v) for k, v in res.items()}
cards = st.load_model_cards(cat / "model_cards.json"); out["store_cards"] = [{k: c[k] for k in ("model_id", "cost_tier", "latency_tier", "reliability", "supports_json", "tags", "context_window")} for c in cards["cards"]]
out["store_card_lookup"] = [st.get_model_card("minimax/minimax-m2.5", cards_payload=cards).get("recommended_roles"), st.get_model_card("nope", cards_payload=cards), [c["model_id"] for c in st.list_models_by_tag("JSON_stable", cards_payload=cards)], st.list_models_by_tag("", cards_payload=cards)]
out["store_lookup_from_path"] = st.get_model_card("x/flash-mini:free", path=cat / "model_cards.json").get("cost_tier")
set_urlopen(lambda req: urllib.error.URLError("down"))
res = st.sync_openrouter_model_catalog(catalog_dir=cat); out["store_sync_cached_fallback"] = [res["fetch_source"], res["model_count"]]
raw = json.loads((cat / "openrouter_models.json").read_text(encoding="utf-8")); out["store_cached_marks"] = [raw.get("fetch_status"), raw.get("fetch_error")]
try: st.sync_openrouter_model_catalog(catalog_dir=cat, allow_cached_fallback=False); out["store_no_fallback"] = "no-raise"
except Exception as e: out["store_no_fallback"] = type(e).__name__
try: st.sync_openrouter_model_catalog(catalog_dir=root / "empty_catalog"); out["store_no_cache"] = "no-raise"
except Exception as e: out["store_no_cache"] = type(e).__name__
out["store_no_cache_files"] = sorted(str(p.relative_to(root)) for p in (root / "empty_catalog").rglob("*")) if (root / "empty_catalog").exists() else []
try: st.load_model_cards(root / "missing.json"); out["store_load_missing"] = "no-raise"
except Exception as e: out["store_load_missing"] = type(e).__name__
out["store_derive"] = [st._derive_cost_tier({"pricing": {"prompt": p, "completion": c}}) for p, c in (("0", "0"), ("0.000001", "0.0000005"), ("0.00001", "0.00001"), ("0.1", "0.1"), ("x", None))]
out["files"] = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()); out["bad"] = bad; out["outside"] = outside
check(not bad and not outside, "blocked/outside: %r %r" % (bad, outside))
check(out["chat_urlerror"][0] == "OpenRouterError" and out["chat_http429_body"][0] == "OpenRouterError", "error wrapping")
check(out["store_sync_cached_fallback"][0] == "cached_fallback" and out["store_no_cache"] != "no-raise", "cache fallback")
print("RF050_CLIENT_STORE_OK client=%d store=%d extract=%d files=%d blocked=0 outside=0 debug=%s" % (sum(k.startswith(("chat_", "from_env", "ctor")) for k in out), sum(k.startswith("store_") for k in out), len(out["extract"]), len(out["files"]), __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=repr))
