# Offline owner-boundary checks for RF-015 B-only libs/agents/monitor {__init__,contracts} (run with cwd = overlay of A tree + 2 B files; read-only).
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, hashlib
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
from pathlib import Path
tmp = Path(tempfile.mkdtemp(prefix="rf015_ov_")).resolve()
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
_wt, _mk = Path.write_text, Path.mkdir
def wt(self, *a, **k):
    if not inside(self): bad.append("write_text:" + str(self)); raise OSError("blocked")
    return _wt(self, *a, **k)
def mk(self, *a, **k):
    if not inside(self): bad.append("mkdir:" + str(self)); raise OSError("blocked")
    return _mk(self, *a, **k)
Path.write_text, Path.mkdir = wt, mk
def check(cond, msg):
    if not cond: raise SystemExit("CHECK_FAILED: " + msg)
def tree(root):
    return sorted((str(p.relative_to(root)), hashlib.sha1(p.read_bytes()).hexdigest()) for p in Path(root).rglob("*") if p.is_file())
import ast, glob, types
from collections.abc import Mapping
from dataclasses import FrozenInstanceError, is_dataclass
root = Path(os.getcwd()).resolve()
has_init = (root / "libs/agents/monitor/__init__.py").exists()
mods = sorted(p.replace("\\", "/") for p in glob.glob("libs/agents/monitor/events/*.py") + glob.glob("libs/agents/monitor/projections/*.py"))
names = ["libs.agents.monitor." + p.split("monitor/")[1][:-3].replace("/", ".") for p in mods if not p.endswith("__init__.py")]
check(len(names) == 19, "19 owner modules, got %d" % len(names))
pkg = importlib.import_module("libs.agents.monitor")
check(bool(getattr(pkg, "__file__", None)) == has_init, "package kind matches overlay")
owner_attrs = {}
for n in names:
    m = importlib.import_module(n)
    check(str(Path(m.__file__).resolve()).startswith(str(root)), "owner imported from cwd tree: " + n)
    owner_attrs[n] = sorted(a for a in dir(m) if not a.startswith("__"))
# legacy runtime/monitor wrappers must still alias the same canonical modules (consumer)
wr = []
for p in sorted(glob.glob("libs/runtime/monitor/*.py")):
    src = Path(p).read_text(encoding="utf-8")
    if "libs.agents.monitor" in src:
        wr.append(p.replace("\\", "/").split("/")[-1][:-3])
        importlib.import_module("libs.runtime.monitor." + wr[-1])
im = importlib.import_module("libs.runtime.intraday_monitor_signals")
before_mods = set(sys.modules)
if has_init:
    c = importlib.import_module("libs.agents.monitor.contracts")
    check(pkg.MonitorAgentInput is c.MonitorAgentInput and pkg.MonitorAgentResult is c.MonitorAgentResult and pkg.__all__ == ["MonitorAgentInput", "MonitorAgentResult"], "package re-exports")
    A, R, KEYS = c.MonitorAgentInput, c.MonitorAgentResult, c.MONITOR_STATE_COMPATIBILITY_KEYS
    check(is_dataclass(A) and is_dataclass(R) and len(KEYS) == 27 and len(set(KEYS)) == 27, "27 unique keys, dataclasses")
    # contract behaviour
    nested = {"a": [1]}
    src = {"selected": nested, "intents": [], "other_key": 1, "monitor_output": {"k": 1}}
    inp = A.from_state(src); src["new"] = 2; src["selected"] = "rebound"
    check("new" not in inp.state and inp.state["selected"] is nested and inp.state is not src, "input: shallow snapshot (top-level isolated, nested aliased)")
    nested["a"].append(2); check(inp.state["selected"]["a"] == [1, 2], "nested shared (documented)")
    check(isinstance(inp.state, dict), "state stored as dict copy")
    try: inp.state = {}; raise SystemExit("CHECK_FAILED: frozen")
    except FrozenInstanceError: pass
    inp.state["x"] = 1  # inner dict still mutable (frozen is shallow)
    ro = A.from_state(types.MappingProxyType({"selected": 1})); check(ro.state == {"selected": 1} and type(ro.state) is dict, "MappingProxy -> dict")
    class M(Mapping):
        def __getitem__(self, k): return {"selected": 7}[k]
        def __iter__(self): return iter(["selected"])
        def __len__(self): return 1
    check(A.from_state(M()).state == {"selected": 7} and R.from_state(M()).state_patch == {"selected": 7}, "custom Mapping accepted")
    errs = {}
    for label, bad_in in (("list", [("selected", 1)]), ("none", None), ("str", "selected"), ("int", 3), ("set", set())):
        for cls in (A, R):
            try: cls.from_state(bad_in); errs[(cls.__name__, label)] = "no_raise"
            except Exception as e: errs[(cls.__name__, label)] = type(e).__name__ + ":" + str(e)
    check(all(v.startswith("TypeError:Monitor role contracts require a mapping state") for v in errs.values()), "non-mapping -> TypeError (all 10)")
    full = {k: i for i, k in enumerate(KEYS)}; full.update({"junk": 1, "monitor_entry_decision": 9})
    r = R.from_state(full)
    check(list(r.state_patch) == list(KEYS) and "junk" not in r.state_patch and "monitor_entry_decision" not in r.state_patch, "patch = key whitelist in contract order")
    part = R.from_state({"selected": None, "intents": []}); check(part.state_patch == {"selected": None, "intents": []}, "present-but-falsy kept; absent omitted")
    check(R.from_state({}).state_patch == {} and R.from_state({}).as_state_patch() == {}, "empty")
    ap = r.as_state_patch(); ap["selected"] = "mut"; check(r.state_patch["selected"] != "mut" and ap is not r.state_patch, "as_state_patch returns a copy")
    shared = {"x": 1}; rr = R.from_state({"monitor": shared}); rr.as_state_patch()["monitor"]["x"] = 2; check(shared["x"] == 2, "values aliased (shallow)")
    try: r.state_patch = {}; raise SystemExit("CHECK_FAILED: frozen result")
    except FrozenInstanceError: pass
    # consumer / State patch boundary: monitor_node top-level writes vs contract keys (static AST on A's source)
    tree_ = ast.parse(Path("graphs/nodes/monitor_node.py").read_text(encoding="utf-8-sig"))
    writes = set()
    for node in ast.walk(tree_):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == "state" and isinstance(t.slice, ast.Constant) and isinstance(t.slice.value, str): writes.add(t.slice.value)
    cov = sorted(set(KEYS) - writes); extra = sorted(writes - set(KEYS))
    consumers = [p for p in (q.replace("\\", "/") for q in glob.glob("**/*.py", recursive=True)) if not p.startswith(("tests", "libs/agents/monitor")) and ("MonitorAgentInput" in Path(p).read_text(encoding="utf-8", errors="ignore") or "MonitorAgentResult" in Path(p).read_text(encoding="utf-8", errors="ignore"))]
    check(not consumers, "no repo consumer of the new contracts: %s" % consumers)
    extra_info = "contract_keys_not_statically_written=%d monitor_node_extra_writes=%d" % (len(cov), len(extra))
else:
    for n in ("contracts",):
        try: importlib.import_module("libs.agents.monitor.contracts"); raise SystemExit("CHECK_FAILED: contracts exists in baseline")
        except ModuleNotFoundError: pass
    extra_info = "contracts=absent"
new_mods = sorted(m for m in set(sys.modules) - before_mods if m.startswith("libs."))
check(not bad, "blocked operations: %s" % bad)
h = hashlib.sha1(json.dumps(owner_attrs, sort_keys=True).encode()).hexdigest()[:10]
print("RF015_MONITOR_CONTRACTS_PEER_OK mode=%s owners=%d runtime_wrappers=%d owner_attr_hash=%s %s writes_outside=0 blocked=%d debug=%s" % ("overlay" if has_init else "baseline", len(names), len(wr), h, extra_info, len(bad), __debug__))
if has_init: print("DETAIL not_written=%s extra_writes=%s" % (cov, extra))
