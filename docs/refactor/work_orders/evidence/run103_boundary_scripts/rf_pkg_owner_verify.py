# A OWNER verification for small libs/* package RFs (RF-046 data_quality, RF-047 diagnostics, RF-052 market_data, RF-054 performance, RF-058 storage).
# Per package: file list + blob, lines, top-level public API, AST effect signals, repo importers per module (static), public-API fingerprint after a real import
# (child process: network/subprocess blocked, writes confined to a tmp cwd), and the package's existing repo tests run via pytest (normal python only; pytest's
# assertion rewriting is disabled under -O so -O runs only the import/fingerprint part). Usage: (cd <repo>; python [-O] rf_pkg_owner_verify.py [--no-tests])
import os, sys, ast, re, json, hashlib, subprocess, tempfile, shutil
from pathlib import Path
repo = Path(os.getcwd()).resolve(); RUN_TESTS = "--no-tests" not in sys.argv[1:] and __debug__
PKGS = dict(x.split("=") for x in os.environ["RF_PKGS"].split(",")) if os.environ.get("RF_PKGS") else {"RF-046": "data_quality", "RF-047": "diagnostics", "RF-052": "market_data", "RF-054": "performance", "RF-058": "storage"}
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: %s" % (sys._getframe(1).f_lineno, m))
srcs = {}
for p in repo.rglob("*.py"):
    rel = p.relative_to(repo).as_posix()
    if "/site-packages/" in rel or rel.startswith(".venv"): continue
    try: srcs[rel] = p.read_text(encoding="utf-8-sig")
    except Exception: pass
PAT = {"write": r"write_text|write_bytes|open\([^)]*['\"][wa]|json\.dump\(|\.mkdir\(|os\.replace|shutil\.", "subprocess": r"subprocess|os\.system|run_hidden",
       "network": r"requests\.|urllib|http\.client|socket\.", "env": r"os\.getenv|os\.environ", "sqlite": r"sqlite3", "time_now": r"datetime\.now|time\.time\("}
FP = r'''
import sys, os, io, json, hashlib, importlib, socket, subprocess, builtins, inspect
root = os.path.abspath(os.getcwd())
def blk(*a, **k): raise OSError("blocked")
socket.socket.connect = blk; socket.create_connection = blk
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blk)
_o = io.open
def g(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not (isinstance(f, int) or os.path.abspath(os.fspath(f)).startswith(root)): raise OSError("blocked write")
    return _o(f, mode, *a, **k)
builtins.open = g; io.open = g
sys.path.insert(0, sys.argv[1]); out = {}
for m in sys.argv[2:]:
    mod = importlib.import_module(m)
    names = sorted(n for n in dir(mod) if not n.startswith("_"))
    sig = []
    for n in names:
        o = getattr(mod, n)
        if getattr(o, "__module__", None) != mod.__name__: continue
        try: s = str(inspect.signature(o)) if callable(o) else type(o).__name__
        except Exception: s = "?"
        sig.append(n + s)
    out[m] = hashlib.sha256("\n".join(sig).encode()).hexdigest()[:12] + ":%d" % len(sig)
print(json.dumps(out, sort_keys=True))
'''
report = {}
for rf, pkg in PKGS.items():
    files = sorted(k for k in srcs if k.startswith(f"libs/{pkg}/") and k.count("/") == 2)
    check(files, (rf, pkg))
    mods, info = [], {}
    for f in files:
        src = srcs[f]; t = ast.parse(src)
        mod = f[:-3].replace("/", "."); mod = mod[:-9] if mod.endswith(".__init__") else mod; mods.append(mod)
        api = [n.name for n in t.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and not n.name.startswith("_")]
        imp = sorted({k for k, v in srcs.items() if k != f and not k.startswith(f"libs/{pkg}/") and (re.search(r"from\s+%s\s+import" % re.escape(mod), v) or re.search(r"import\s+%s\b" % re.escape(mod), v))})
        info[f] = {"lines": len(src.splitlines()), "public_api": len(api), "effects": [k for k, p in PAT.items() if re.search(p, src)],
                   "importers": len(imp), "importer_areas": sorted({"/".join(x.split("/")[:2]) for x in imp}),
                   "blob": subprocess.run(["git", "hash-object", str(repo / f)], capture_output=True, text=True).stdout.strip()[:8]}
    tmp = Path(tempfile.mkdtemp(prefix="pkgfp_"))
    env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "PROXY"))}; env["PYTHONDONTWRITEBYTECODE"] = "1"
    fp = subprocess.run([sys.executable, *(["-O"] if not __debug__ else []), "-c", FP, str(repo), *mods], cwd=tmp, env=env, capture_output=True, text=True, timeout=120)
    check(fp.returncode == 0, (rf, fp.stderr[-400:]))
    leftovers = sorted(str(p.relative_to(tmp)) for p in tmp.rglob("*"))
    shutil.rmtree(tmp, ignore_errors=True)
    tests = sorted(k for k, v in srcs.items() if k.startswith("tests/") and re.search(r"libs\.%s\b" % pkg, v))
    tres = None
    if RUN_TESTS and tests:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *tests], cwd=repo, env=env, capture_output=True, text=True, timeout=600)
        tres = {"exit": r.returncode, "summary": (r.stdout.strip().splitlines() or [""])[-1].split(" in ")[0]}
    report[rf] = {"package": f"libs/{pkg}", "files": info, "api_fingerprint": json.loads(fp.stdout), "import_side_files": leftovers, "tests": tests, "test_result": tres}
print(json.dumps(report, sort_keys=True, ensure_ascii=False))
summary = {rf: {"files": len(v["files"]), "lines": sum(x["lines"] for x in v["files"].values()), "importers": sum(x["importers"] for x in v["files"].values()),
                "effects": sorted({e for x in v["files"].values() for e in x["effects"]}), "tests": (v["test_result"] or {}).get("summary", "NOT_RUN" if v["tests"] else "none")} for rf, v in report.items()}
print("RF_PKG_OWNER_VERIFY_OK " + json.dumps(summary, sort_keys=True, ensure_ascii=False) + " debug=%s" % __debug__)
