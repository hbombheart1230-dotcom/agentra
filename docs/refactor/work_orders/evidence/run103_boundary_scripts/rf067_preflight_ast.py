# AST-only RF-067 check of scripts/check_real_execution_preflight.py wrapper, target main(), public consumers, env timing.
# Never imports or executes the wrapper/target/broker code; reads source text only.
import ast, os, sys, re
from pathlib import Path
root = Path(os.getcwd())
def parse(rel): return ast.parse((root / rel).read_text(encoding="utf-8"), filename=rel)
def check(cond, msg):
    if not cond: raise SystemExit("CHECK_FAILED: " + msg)

# 1) wrapper: only stdlib imports, alias/runpy to scripts.diagnostics target, PATH insert of repo root only
w = parse("scripts/check_real_execution_preflight.py")
mods = sorted({(a.name if isinstance(n, ast.Import) else n.module) for n in ast.walk(w) for a in (n.names if isinstance(n, (ast.Import, ast.ImportFrom)) else [])})
check(mods == ["importlib", "pathlib", "runpy", "sys"], "wrapper imports %r" % mods)
src = (root / "scripts/check_real_execution_preflight.py").read_text(encoding="utf-8")
target_strs = re.findall(r'"(scripts\.diagnostics\.[a-z_0-9]+)"', src)
check(target_strs == ["scripts.diagnostics.check_real_execution_preflight"] * 2, "wrapper targets %r" % target_strs)
ifs = [n for n in w.body if isinstance(n, ast.If)]
check(len(ifs) == 2 and "__main__" in ast.dump(ifs[1].test), "main guard + alias branch")
check(any("sys.path" in ast.unparse(n) or "_sys.path" in ast.unparse(n) for n in ifs[:1]), "repo-root sys.path insert")
check("parents[1]" in src, "ROOT=parents[1] (cwd independent)")
check(not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("print", "open", "exec", "eval") for n in ast.walk(w)), "no direct io calls")

# 2) target main(): parser flags, exit codes, no env/network/file IO of its own
t = parse("scripts/diagnostics/check_real_execution_preflight.py")
tsrc = (root / "scripts/diagnostics/check_real_execution_preflight.py").read_text(encoding="utf-8")
funcs = [n.name for n in t.body if isinstance(n, ast.FunctionDef)]
check(funcs == ["_build_req", "_build_parser", "main"], "target functions %r" % funcs)
flags = re.findall(r'add_argument\("(--[a-z-]+)"', tsrc); check(flags == ["--symbol", "--json"], "flags %r" % flags)
check("load_env_file" not in tsrc and "os.environ" not in tsrc and "getenv" not in tsrc and "open(" not in tsrc and "write_text" not in tsrc, "target main has no own env/file IO")
check(re.search(r"return 0 if out\[\"ok\"\] else 3", tsrc) is not None, "exit 0/3 contract")
main_calls = [ast.unparse(n.func) for n in ast.walk([f for f in t.body if isinstance(f, ast.FunctionDef) and f.name == "main"][0]) if isinstance(n, ast.Call)]
check("RealExecutor" in main_calls and "ex.preflight_check" in main_calls, "main calls RealExecutor() + preflight_check")
check([n.module for n in t.body if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("libs.")] == ["libs.catalog.api_request_builder", "libs.execution.executors.real_executor"], "libs imports")

# 3) RealExecutor env timing (static): Settings.from_env at construct, flags read inside preflight_check at call time
r = parse("libs/execution/executors/real_executor.py")
cls = [n for n in r.body if isinstance(n, ast.ClassDef) and n.name == "RealExecutor"][0]
meth = {m.name: m for m in cls.body if isinstance(m, ast.FunctionDef)}
init_src = ast.unparse(meth["__init__"]); pf_src = ast.unparse(meth["preflight_check"])
check("Settings.from_env()" in init_src, "construct-time Settings.from_env")
check("EXECUTION_ENABLED" in pf_src and "KIWOOM_MODE" in pf_src and "ALLOW_REAL_EXECUTION" in pf_src, "preflight reads flags at call time")
pf_calls = {ast.unparse(n.func) for n in ast.walk(meth["preflight_check"]) if isinstance(n, ast.Call)}
check(not any(re.search(r"(urlopen|\.http|\.post$|\.get$|\.request$|requests\.|socket)", c) for c in pf_calls), "preflight_check calls no http dispatch: %r" % sorted(pf_calls))
tok = sorted({k for k in ("EXECUTION_ENABLED", "KIWOOM_MODE", "ALLOW_REAL_EXECUTION", "SYMBOL_ALLOWLIST") if k in ast.unparse(cls)})

# 4) consumers: textual search over tracked non-doc files
hits = []
for p in root.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in (".py", ".bat", ".ps1", ".sh", ".yml", ".yaml", ".toml", ".cfg", ".json") and p.name.lower() != "dockerfile": continue
    rel = p.relative_to(root).as_posix()
    if rel.startswith((".git/", "docs/", "evidence/")) or "__pycache__" in rel or "node_modules" in rel: continue
    try: txt = p.read_text(encoding="utf-8")
    except Exception: continue
    if "check_real_execution_preflight" in txt: hits.append(rel)
check(sorted(hits) == ["scripts/check_real_execution_preflight.py", "scripts/diagnostics/check_real_execution_preflight.py", "tests/test_m24_5_real_execution_preflight.py"] or sorted(hits) == ["scripts/check_real_execution_preflight.py", "tests/test_m24_5_real_execution_preflight.py"], "consumers %r" % hits)
tst = (root / "tests/test_m24_5_real_execution_preflight.py").read_text(encoding="utf-8")
check("from scripts.check_real_execution_preflight import main as preflight_main" in tst, "test imports via root alias")
# no BAT/PS1/CI/compose/Dockerfile consumer (those hits would appear above)
print("RF067_PREFLIGHT_AST_OK wrapper_imports=4 targets=2 flags=2 exits=0/3 env_tokens=%d consumers=%d broker_exec=0 debug=%s" % (len(tok), len(hits), __debug__))
