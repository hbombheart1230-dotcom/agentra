# RF-043 OWNER verification (A): libs/catalog (6 files) -- responsibility/consumer map + behaviour/IO/exception contract, to decide MOVE vs KEEP_VERIFIED.
# In-process, tmp cwd only; network/subprocess/sqlite blocked; writes confined to tmp (builtins.open/io.open/os.*). Usage: (cd <repo>; python [-O] rf043_catalog_owner_verify.py)
import os, sys, io, json, re, ast, copy, socket, subprocess, sqlite3, builtins, importlib, tempfile, shutil, contextlib
from pathlib import Path
repo = Path(os.getcwd()).resolve(); sys.path.insert(0, str(repo))
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY")): del os.environ[k]
tmp = Path(tempfile.mkdtemp(prefix="rf043_")).resolve(); os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
def inside(p):
    try:
        if isinstance(p, int): return True
        ap = os.path.abspath(os.fspath(p)); return ap == str(tmp) or ap.startswith(str(tmp) + os.sep)
    except Exception: return False
_open = io.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write outside tmp")
    return _open(f, mode, *a, **k)
builtins.open = gopen; io.open = gopen
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: %s" % (sys._getframe(1).f_lineno, m))
def attempt(fn, *a, **k):
    try: return fn(*a, **k), None
    except Exception as e: return None, type(e).__name__
cat = importlib.import_module("libs.catalog.api_catalog"); bld = importlib.import_module("libs.catalog.api_catalog_builder")
dis = importlib.import_module("libs.catalog.api_discovery"); pln = importlib.import_module("libs.catalog.api_planner"); rqb = importlib.import_module("libs.catalog.api_request_builder")
out = {}
# ---- 0) static owner/consumer map (read-only)
mods = ["api_catalog", "api_catalog_builder", "api_discovery", "api_planner", "api_request_builder"]
cons = {m: set() for m in mods}
for p in repo.rglob("*.py"):
    rel = p.relative_to(repo).as_posix()
    if rel.startswith(("libs/catalog/", ".venv", "node_modules")) or "/site-packages/" in rel: continue
    try: t = ast.parse(p.read_text(encoding="utf-8"))
    except Exception: continue
    for n in ast.walk(t):
        if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("libs.catalog."):
            m = n.module.split(".")[-1]
            if m in cons: cons[m].add(rel.split("/")[0] + "/" + (rel.split("/")[1] if rel.count("/") > 1 else ""))
consumer_files = {m: 0 for m in mods}
for p in repo.rglob("*.py"):
    rel = p.relative_to(repo).as_posix()
    if rel.startswith("libs/catalog/") or "/site-packages/" in rel: continue
    try: src = p.read_text(encoding="utf-8")
    except Exception: continue
    for m in mods:
        if re.search(r"from libs\.catalog\.%s import" % m, src): consumer_files[m] += 1
out["consumer_files"] = consumer_files; out["consumer_areas"] = {m: sorted(v) for m, v in cons.items()}
check(consumer_files["api_request_builder"] >= 20 and consumer_files["api_catalog"] >= 15, consumer_files)  # PreparedRequest is the broker/executor DTO -> safety-adjacent
check(any(a.startswith("libs/execution") for a in cons["api_request_builder"]), "execution consumers of PreparedRequest")
init = (repo / "libs/catalog/__init__.py").read_text(encoding="utf-8"); check(init.strip() == "", "empty package marker")
# ---- 1) ApiSpec / ApiCatalog
S = cat.ApiSpec
s = S(api_id="A1"); check(s.tags == [] and s.params == {} and s.extra == {}, "defaults")
fd = S.from_dict({"id": "X", "title": 1, "tags": None, "params": None, "_flags": {"callable": False}, "foo": "bar"})
check(fd.api_id == "X" and fd.title == "1" and fd.tags == [] and fd.extra == {"_flags": {"callable": False}, "foo": "bar"}, fd)
out["from_dict_errors"] = {"missing_id": attempt(S.from_dict, {"title": "t"})[1], "id_not_str": attempt(S.from_dict, {"api_id": 5})[1]}
check(out["from_dict_errors"] == {"missing_id": "ApiCatalogLoadError", "id_not_str": "ApiCatalogLoadError"}, out["from_dict_errors"])
C = cat.ApiCatalog
c1 = C.from_obj([{"api_id": "b"}, {"api_id": "a"}]); check(c1.list_ids() == ["a", "b"] and c1.has("a") and not c1.has("z"), c1.list_ids())
c2 = C.from_obj({"apis": [{"api_id": "k"}]}); c3 = C.from_obj({"m1": {"title": "t"}, "m2": "not a dict"}); check(c2.list_ids() == ["k"] and c3.list_ids() == ["m1"], (c2.list_ids(), c3.list_ids()))  # non-dict mapping values silently skipped
out["catalog_errors"] = {"dup": attempt(C.from_obj, [{"api_id": "a"}, {"api_id": "a"}])[1], "list_nondict": attempt(C.from_obj, [1])[1], "type": attempt(C.from_obj, "x")[1], "get_missing": attempt(c1.get, "zz")[1]}
check(out["catalog_errors"] == {"dup": "ApiCatalogLoadError", "list_nondict": "ApiCatalogLoadError", "type": "ApiCatalogLoadError", "get_missing": "ApiNotFoundError"}, out["catalog_errors"])
check(issubclass(cat.ApiNotFoundError, cat.ApiCatalogError) and issubclass(cat.ApiCatalogLoadError, cat.ApiCatalogError), "error hierarchy")
td = C.from_obj([{"api_id": "a", "title": "T", "x": 1}]).to_dict(); check(td == {"a": {"api_id": "a", "title": "T", "description": "", "method": "", "path": "", "tags": [], "params": {}, "x": 1}}, td)
(tmp / "c.json").write_text(json.dumps([{"api_id": "j"}]), encoding="utf-8"); (tmp / "c.jsonl").write_text('{"api_id":"l1"}\n\n{"api_id":"l2"}\n', encoding="utf-8")
(tmp / "bad.jsonl").write_text('{"api_id":"l1"}\nnot json\n', encoding="utf-8"); (tmp / "bad.json").write_text("{", encoding="utf-8"); (tmp / "dup.jsonl").write_text('{"api_id":"d"}\n{"api_id":"d"}\n', encoding="utf-8")
check(C.load(tmp / "c.json").list_ids() == ["j"] and C.load(str(tmp / "c.jsonl")).list_ids() == ["l1", "l2"], "load json/jsonl")
out["load_errors"] = {"missing": attempt(C.load, tmp / "nope.json")[1], "bad_jsonl": attempt(C.load, tmp / "bad.jsonl")[1], "bad_json": attempt(C.load, tmp / "bad.json")[1], "dup_jsonl": attempt(C.load, tmp / "dup.jsonl")[1]}
check(set(out["load_errors"].values()) == {"ApiCatalogLoadError"}, out["load_errors"])
# ---- 2) builder (CLI scripts/build_api_catalog.py; runtime: libs/read/kiwoom_broker_truth_common.ensure_catalog_path)
src1, src2 = tmp / "specs/a.jsonl", tmp / "specs/b.jsonl"; src1.parent.mkdir()
src1.write_text("\n".join(json.dumps(r) for r in [{"api_id": "ka1", "name": "Quote", "http_method": "post", "endpoint": "/q", "tags": ["t1"]}, {"title": "no id"}, {"api_id": "ka2", "_flags": {"callable": False}}]) + "\n", encoding="utf-8")
src2.write_text(json.dumps({"api_id": "ka1", "tags": ["t1", "t2"], "method": "GET", "request": {"header": [{"element": "authorization", "required": "Y"}], "body": [{"element": "stk_cd", "required": "Y"}, {"name": "qty", "required": "N"}, "junk", {"type": "x"}]}}) + "\n", encoding="utf-8")
target = tmp / "out/api_catalog.jsonl"
buf = io.StringIO()
with contextlib.redirect_stdout(buf): ret = bld.build_api_catalog(input_files=[src1, src2], output_file=target)
rows = {json.loads(l)["api_id"]: json.loads(l) for l in target.read_text(encoding="utf-8").splitlines()}
check(ret == target and sorted(rows) == ["ka1", "ka2"] and buf.getvalue().strip() == f"[OK] Built 2 API records -> {target}", (sorted(rows), buf.getvalue()))
k1 = rows["ka1"]
check(k1["title"] == "Quote" and k1["method"] == "post" and k1["path"] == "/q" and k1["tags"] == ["t1", "t2"] and k1["_sources"] == ["a.jsonl", "b.jsonl"] and k1["_flags"] == {"callable": True, "merged": True}, k1)
check([p["name"] for p in k1["params"]["header"]] == ["authorization"] and [p["name"] for p in k1["params"]["query"]] == ["stk_cd", "qty"] and k1["params"]["query"][0]["required"] is True and k1["params"]["query"][1]["required"] is False and "body" not in k1["params"], k1["params"])  # request fields classified by THAT record's own method (GET -> query) even though the merged spec method is 'post'
check(rows["ka2"]["_flags"]["callable"] is False, rows["ka2"])
loaded = C.load(target); check(loaded.get("ka1").extra["_flags"]["merged"] is True, "builder output loads back")
recs = [{"api_id": "z", "name": "N"}]; before = copy.deepcopy(recs); bld.merge_records(recs); out["merge_mutates_input"] = recs != before  # observed: input record gains 'title'
out["builder_errors"] = {"missing_input": attempt(bld.build_api_catalog, input_files=[tmp / "nope.jsonl"], output_file=tmp / "o2.jsonl")[1], "bad_line": attempt(bld.build_api_catalog, input_files=[tmp / "bad.jsonl"], output_file=tmp / "o3.jsonl")[1]}
out["builder_partial_target_on_error"] = (tmp / "o3.jsonl").exists()
check(out["builder_errors"] == {"missing_input": "FileNotFoundError", "bad_line": "JSONDecodeError"}, out["builder_errors"])
out["builder_defaults"] = {"inputs": [str(p) for p in bld.INPUT_FILES], "output": str(bld.OUTPUT_FILE)}  # cwd-relative
# ---- 3) discovery / planner (pure)
dc = C.from_obj([{"api_id": "ka10001", "title": "주식기본정보", "description": "stock info", "tags": ["quote"], "method": "POST"}, {"api_id": "kt10000", "title": "매수주문", "tags": ["order"], "method": "POST", "_flags": {"callable": False}}, {"api_id": "ka2", "title": "stock list", "method": "GET"}])
D = dis.ApiDiscovery(dc)
r = D.search("stock"); check([m.spec.api_id for m in r] == ["ka2", "ka10001"] and r[0].score == 0.4 and r[1].score == 0.2, [(m.spec.api_id, m.score) for m in r])
check(D.search("kt10000") == [] and [m.spec.api_id for m in D.search("kt10000", callable_only=False)] == ["kt10000"], "callable filter")
check([m.spec.api_id for m in D.search("stock", method="GET")] == ["ka2"] and [m.spec.api_id for m in D.search("stock", require_tags=["quote"])] == ["ka10001"], "method/tag filter")
empty_q = D.search(""); out["empty_query_matches"] = [(m.spec.api_id, m.score) for m in empty_q]  # observed: '' matches every callable spec (score 1.0 where description present)
P = pln.ApiPlanner()
check(P.plan([]).action == "ask" and P.plan(r[:1]).action == "select" and P.plan(r).action == "ask", "planner branches")
M = dis.ApiMatch; hi = [M(spec=S(api_id="h"), score=1.0, reasons=[]), M(spec=S(api_id="l"), score=0.8, reasons=[])]
check(P.plan(hi).action == "select" and P.plan([M(spec=S(api_id="h"), score=0.9, reasons=[]), M(spec=S(api_id="l"), score=0.8, reasons=[])]).action == "ask", "threshold/margin")
check(len(P.plan([M(spec=S(api_id=str(i)), score=0.5, reasons=[]) for i in range(5)]).candidates) == 3, "ask returns top3")
# ---- 4) request builder (prepare-only DTO used by executors)
B = rqb.ApiRequestBuilder()
spec_q = S(api_id="q", method="GET", params={"query": [{"name": "ticker", "required": True}], "header": [{"name": "authorization", "required": True}]})
ok = B.prepare(spec_q, {"symbol": "005930"}); check(ok.action == "ready" and ok.request.query == {"ticker": "005930"} and ok.request.headers == {} and ok.request.body == {}, ok)  # alias + managed header skipped
ask = B.prepare(spec_q, {}); check(ask.action == "ask" and ask.missing == ["ticker"] and ask.question == "다음 값이 필요해요: ticker" and ask.request is None, ask)
spec_shape1 = S(api_id="s1", method="GET", params={"a": {"in": "header", "required": True}, "b": {"in": "path"}})
r1 = B.prepare(spec_shape1, {"a": 1, "b": 2}); check(r1.request.headers == {"a": 1} and r1.request.query == {"b": 2}, r1.request)  # path params land in query
spec_shape3 = S(api_id="s3", method="GET", params={"fields": [{"name": "f", "in": "body", "required": True}]}); check(B.prepare(spec_shape3, {"f": 9}).request.body == {"f": 9}, "shape3")
spec_post = S(api_id="o", method="POST", params={"body": [{"name": "ticker", "required": True}, {"name": "qty", "required": True}]})
po = B.prepare(spec_post, {"symbol": "005930", "quantity": 3, "note": "x", "empty": "", "none": None, "AppKey": "SECRET-K", "authorization": "Bearer T"})
out["post_passthrough_body"] = po.request.body
check(po.request.body.get("ticker") == "005930" and po.request.body.get("qty") == 3, po.request.body)
check("AppKey" not in po.request.body and "authorization" not in po.request.body and "empty" not in po.request.body and "none" not in po.request.body, po.request.body)
dup_alias = {"symbol", "quantity"} & set(po.request.body); out["post_alias_keys_duplicated_into_body"] = sorted(dup_alias)   # observed: alias keys used to resolve ticker/qty are ALSO copied into body
out["post_unrelated_context_into_body"] = "note" in po.request.body
check(B.prepare(S(api_id="g", method="GET"), {"x": 1}).request.body == {} and B.prepare(S(api_id="g2", method=""), {"x": 1}).request.query == {}, "no passthrough for GET/empty method")
try: ok.request.body = {}; out["prepared_request_frozen"] = False
except Exception as e: out["prepared_request_frozen"] = type(e).__name__
check(out["prepared_request_frozen"] == "FrozenInstanceError", out["prepared_request_frozen"])
out["prepare_nondict_params"] = attempt(B.prepare, S(api_id="n", params={"query": "x"}), {})[1]
check(not bad, bad)
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
print("RF043_CATALOG_OWNER_VERIFY_OK files=6 consumers(request_builder=%d,catalog=%d) catalog_errors=4 load_errors=4 builder=merge/params/flags discovery_planner=ok request_builder=ready/ask/shapes/passthrough alias_dup=%s network=0 debug=%s" % (consumer_files["api_request_builder"], consumer_files["api_catalog"], ",".join(out["post_alias_keys_duplicated_into_body"]) or "none", __debug__))
