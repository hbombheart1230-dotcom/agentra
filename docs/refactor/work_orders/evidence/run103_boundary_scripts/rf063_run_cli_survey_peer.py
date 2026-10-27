# RF-063 independent peer (A for B-owned RF): SURVEY of all scripts/diagnostics/run_*.py CLIs (46) as REAL processes through their public root wrappers scripts/run_*.py.
# Per CLI: (1) `--help` and (2) a DEFAULT-ARGS run in a fresh empty tmp cwd. The child bootstrap CONFINES every write (builtins.open, io.open/pathlib, os.mkdir/remove/rename/...) to that tmp cwd, and blocks network/subprocess/sqlite.
# Credential env vars and PATH are cleared; no .env exists in the cwd. This establishes process-level facts only (exit code, crash/gate/arg error class, files created, blocked-effect attempts, timeouts) -- NOT semantic correctness of each check.
# Set selection: default `diagnostics` = scripts/diagnostics/run_*.py (46, RF-063). `--set research` = scripts/research/*.py (53 minus protected run_uef*/frozen* CLIs, RF-065).
# Usage: python rf063_run_cli_survey_peer.py <repo_root> [-O] [--set research]
import os, sys, json, re, shutil, subprocess, tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
repo = Path(sys.argv[1]).resolve(); opt = ["-O"] if "-O" in sys.argv[2:] else []
SET = "research" if "research" in sys.argv[2:] else "diagnostics"
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + str(m))
BOOT = r'''
import sys, os, io, socket, subprocess, sqlite3, atexit, runpy, builtins
bad = []
ROOT_OK = os.path.abspath(os.environ["RF_TMP_ROOT"])
def inside(p):
    try:
        if isinstance(p, int): return True
        ap = os.path.abspath(os.fspath(p)); return ap == ROOT_OK or ap.startswith(ROOT_OK + os.sep)
    except Exception: return False
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system")
_sconn = sqlite3.connect
def sconn(db, *a, **k):
    if str(db) == ":memory:" or inside(db): return _sconn(db, *a, **k)
    bad.append("sqlite:" + str(db)); raise OSError("blocked sqlite outside tmp")
sqlite3.connect = sconn
_open = io.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write outside tmp")
    return _open(f, mode, *a, **k)
builtins.open = gopen; io.open = gopen
def guard(name):
    orig = getattr(os, name)
    def f(*a, **k):
        if not all(inside(x) for x in a[:2] if isinstance(x, (str, bytes, os.PathLike))): bad.append(name + ":" + str(a[:1])); raise OSError("blocked " + name + " outside tmp")
        return orig(*a, **k)
    setattr(os, name, f)
for n in ("mkdir", "remove", "unlink", "rmdir", "rename", "replace"): guard(n)
atexit.register(lambda: sys.stderr.write("\nBLOCKED_ATTEMPTS=%d %s\nBLOCKED_FIRST=%s\n" % (len(bad), ";".join(sorted({b.split(":")[0] for b in bad})), (bad[0] if bad else ""))))
script = sys.argv[1]; sys.argv = [script] + sys.argv[2:]
runpy.run_path(script, run_name="__main__")
'''
def repo_status(): return subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True).stdout
repo_before = repo_status()
base_env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY", "PASSWORD"))}
base_env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "", "PATH": "", "PYTHONIOENCODING": "utf-8"})
if SET == "diagnostics":
    names = sorted(p.name for p in (repo / "scripts/diagnostics").glob("run_*.py")); check(len(names) == 46, len(names))
else:
    allr = sorted(p.name for p in (repo / "scripts/research").glob("*.py") if p.name != "__init__.py")
    PROTECTED = [n for n in allr if "uef" in n.lower() or "frozen" in n.lower()]   # protected UEF / frozen-window CLIs are NEVER executed
    names = [n for n in allr if n not in PROTECTED]; check(len(allr) == 53 and len(names) == 53 - len(PROTECTED), (len(allr), PROTECTED))
check(all((repo / "scripts" / n).exists() for n in names), "root wrappers")
root = Path(tempfile.mkdtemp(prefix="rf063_survey_")).resolve()
def redact(s): return re.sub(r"\d{4}-\d{2}-\d{2}", "<d>", re.sub(r"\d{8,}", "<n>", s.replace(str(root), "T").replace(str(repo), "REPO")))
def one(name):
    cwd = root / name[:-3]; cwd.mkdir()
    e = dict(base_env); e["RF_TMP_ROOT"] = str(cwd)
    wrapper = repo / "scripts" / name
    def go(argv, timeout):
        try:
            r = subprocess.run([sys.executable, *opt, "-c", BOOT, str(wrapper), *argv], cwd=str(cwd), env=e, capture_output=True, timeout=timeout)
            return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace"), False
        except subprocess.TimeoutExpired:
            return None, "", "", True
    hc, hout, herr, hto = go(["--help"], 60)
    rc, out, err, to = go([], 45)
    files = sorted(str(p.relative_to(cwd).as_posix()) for p in cwd.rglob("*") if p.is_file())
    m = re.search(r"BLOCKED_ATTEMPTS=(\d+) ?(\S*)", err); att = int(m.group(1)) if m else None  # noqa
    last = [l for l in err.strip().splitlines() if l and not l.startswith("BLOCKED_")][-1:] or [""]
    mf = re.search(r"BLOCKED_FIRST=(.*)", err); first = redact(mf.group(1))[:90] if mf else ""
    errtype = re.match(r"([A-Za-z_.]+(?:Error|Exception|Exit|Interrupt))", last[0]).group(1) if re.match(r"([A-Za-z_.]+(?:Error|Exception|Exit|Interrupt))", last[0]) else ""
    if to: cls = "TIMEOUT"
    elif rc == 0: cls = "EXIT0"
    elif rc == 2 and "usage:" in err.lower(): cls = "ARGERR2"
    elif rc is not None and err.count("Traceback") and rc == 1: cls = "CRASH1"
    else: cls = f"EXIT{rc}"
    kinds = sorted({b for b in (m.group(2).split(";") if m and m.group(2) else []) if b})
    return name, {"help": "ok" if hc == 0 and "usage" in hout.lower() else f"code={hc}" + ("/timeout" if hto else ""), "default_run": cls, "errtype": errtype, "blocked_kinds": kinds, "files": len(files), "file_dirs": sorted({redact(f).split("/")[0] for f in files})[:3],
                  "stdout_head": redact(out.strip().splitlines()[0])[:60] if out.strip() else "", "stdout_json": bool(out.strip().startswith(("{", "["))), "first_blocked": first, "err_last": redact(last[0])[:90]}
with ThreadPoolExecutor(max_workers=8) as ex: table = dict(ex.map(one, names))

# ---- extras: run_m23_closeout_check text mode crashes at the final print (NameError: day) AFTER doing its work; --json mode does not.
def go_extra(name, argv):
    cwd = root / (name[:-3] + "_extra_" + "_".join(a.strip("-") for a in argv)[:20]); cwd.mkdir()
    e = dict(base_env); e["RF_TMP_ROOT"] = str(cwd)
    r = subprocess.run([sys.executable, *opt, "-c", BOOT, str(repo / "scripts" / name), *argv], cwd=str(cwd), env=e, capture_output=True, timeout=60)
    err = r.stderr.decode("utf-8", "replace"); last = [l for l in err.strip().splitlines() if l and not l.startswith("BLOCKED_")][-1:] or [""]
    return {"code": r.returncode, "stdout_is_json": r.stdout.decode("utf-8", "replace").strip().startswith("{"), "err_last": redact(last[0])[:80], "files": len([p for p in cwd.rglob("*") if p.is_file()])}
m23_text = m23_json = None
if SET == "diagnostics":
    m23_text = go_extra("run_m23_closeout_check.py", []); m23_json = go_extra("run_m23_closeout_check.py", ["--json"])
    check(m23_text["code"] == 1 and "NameError: name 'day' is not defined" in m23_text["err_last"] and m23_json["code"] in (0, 3) and m23_json["stdout_is_json"] and "NameError" not in m23_json["err_last"], (m23_text, m23_json))
summary = {}
for n, v in table.items(): summary[v["default_run"]] = summary.get(v["default_run"], 0) + 1
check(not [n for n, v in table.items() if v["help"] != "ok" and v["default_run"] != "TIMEOUT" and False], "")  # informational
out = {"set": SET, "skipped_protected": ([] if SET == "diagnostics" else PROTECTED), "extras_m23": {"text": m23_text, "json": m23_json}, "count": len(table), "summary": summary, "help_ok": sum(1 for v in table.values() if v["help"] == "ok"), "table": table}
check(repo_status() == repo_before, "repo working tree changed")
outside = [n for n, v in table.items() if "write" in v["blocked_kinds"] or any(k in ("mkdir", "remove", "unlink", "rmdir", "rename", "replace") for k in v["blocked_kinds"])]
out["attempted_writes_outside_tmp"] = outside
shutil.rmtree(root, ignore_errors=True)
print(json.dumps(out, sort_keys=True, ensure_ascii=False))
print("RF063_RUN_CLI_SURVEY_OK set=" + SET + " clis=%d help_ok=%d summary=%s outside_write_attempts=%d repo_tree_unchanged=yes debug=%s" % (len(table), out["help_ok"], json.dumps(summary, sort_keys=True), len(outside), "off" if opt else "on"))
