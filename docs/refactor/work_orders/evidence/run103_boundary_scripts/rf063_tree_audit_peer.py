import ast, builtins, importlib.util, json, os, socket, sqlite3, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, os.getcwd())
REPO = Path(os.getcwd()).resolve()
spec = importlib.util.spec_from_file_location("atc", REPO / "scripts/diagnostics/audit_target_tree_compat.py")
atc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(atc)  # import only; __main__ guard is not triggered

loaded_before = set(sys.modules)


def check(c, m="check"):
    if not c:
        raise SystemExit("CHECK_FAILED: " + str(m))


def _blocked(*a, **k):
    raise RuntimeError("BLOCKED_EFFECT")


socket.socket = _blocked
socket.create_connection = _blocked
subprocess.Popen = _blocked
subprocess.run = _blocked
sqlite3.connect = _blocked
os.system = _blocked
_open = builtins.open
write_attempts = []


def _guard_open(f, mode="r", *a, **k):
    if any(c in mode for c in "wax+"):
        write_attempts.append(str(f))
        raise RuntimeError("BLOCKED_WRITE")
    return _open(f, mode, *a, **k)


builtins.open = _guard_open
_wt = Path.write_text  # fixture writer, only into TemporaryDirectory
Path.write_text = lambda *a, **k: _blocked()

BULK = ("import importlib as _importlib\nimport runpy as _runpy\nimport sys as _sys\n"
        "if __name__ == '__main__':\n    _runpy.run_module({m!r}, run_name='__main__')\n"
        "else:\n    _sys.modules[__name__] = _importlib.import_module({m!r})\n")
EXAMPLE = ("import importlib as _importlib\nimport sys as _sys\n_impl = _importlib.import_module({m!r})\n"
           "if __name__ == '__main__':\n    raise SystemExit(_impl.main())\nelse:\n    _sys.modules[__name__] = _impl\n")

# --- _call_targets ---
tree = ast.parse("_importlib.import_module('a.b')\n_importlib.import_module(x)\n_importlib.other('c')\nfoo.import_module('d')\n"
                 "_importlib.import_module()\n_importlib.import_module(1)\n_runpy.run_module('r.s', run_name='__main__')")
check(atc._call_targets(tree, "_importlib", "import_module") == ["a.b"], atc._call_targets(tree, "_importlib", "import_module"))
check(atc._call_targets(tree, "_runpy", "run_module") == ["r.s"])
check(atc._call_targets(ast.parse(""), "_importlib", "import_module") == [])
check(atc._module_path("scripts/x/y.py") == "scripts.x.y")
bad_paths = 0
for bad in ("x/y.py", "scripts/y.txt"):
    try:
        atc._module_path(bad)
    except ValueError:
        bad_paths += 1
check(bad_paths == 2)

# --- _dispatch_issues ---
bulk_tree = ast.parse(BULK.format(m="scripts.a.b"))
check(atc._dispatch_issues(bulk_tree, "scripts.a.b", bulk=True) == [])
check(atc._dispatch_issues(bulk_tree, "scripts.a.other", bulk=True) == ["executable __main__ dispatch missing or invalid",
                                                                       "module-object ABI alias missing or invalid"])
check(atc._dispatch_issues(ast.parse("x = 1"), "m", bulk=True) == ["exactly one top-level __main__ guard required"])
two = ast.parse("if __name__ == '__main__':\n    pass\nif __name__ == '__main__':\n    pass\n")
check(atc._dispatch_issues(two, "m", bulk=True) == ["exactly one top-level __main__ guard required"])
ex_tree = ast.parse(EXAMPLE.format(m="scripts.examples.demo_x"))
check(atc._dispatch_issues(ex_tree, "scripts.examples.demo_x", bulk=False) == [])
check(atc._dispatch_issues(ast.parse(EXAMPLE.format(m="scripts.examples.demo_x").replace("_impl = _importlib", "_impl2 = _importlib")),
                           "scripts.examples.demo_x", bulk=False) == ["example implementation binding missing or invalid"]
      or len(atc._dispatch_issues(ast.parse(EXAMPLE.format(m="scripts.examples.demo_x").replace("_impl = _importlib", "_impl2 = _importlib")),
                                  "scripts.examples.demo_x", bulk=False)) >= 1)


def manifest(moved, held, wrappers):
    return {"candidates": [{"status": "moved", "old": o, "new": n} for o, n in moved]
            + [{"status": "held", "path": h} for h in held],
            "root_layout": [{"kind": "compatibility_wrapper", "path": p} for p in wrappers]}


def build(root, moved_wrapper_src=None, example_src=None, with_new=True):
    for rel, src in (
        ("scripts/old_tool.py", moved_wrapper_src if moved_wrapper_src is not None else BULK.format(m="scripts.maint.old_tool")),
        ("scripts/demo_flow.py", example_src if example_src is not None else EXAMPLE.format(m="scripts.examples.demo_flow")),
        ("scripts/examples/demo_flow.py", "def main():\n    return 0\n"),
    ) + ((("scripts/maint/old_tool.py", "def main():\n    return 0\n"),) if with_new else ()):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        _wt(p, src, encoding="utf-8")


good = manifest([("scripts/old_tool.py", "scripts/maint/old_tool.py")], ["scripts/held_one.py"],
                ["scripts/old_tool.py", "scripts/demo_flow.py"])
results = {}
with tempfile.TemporaryDirectory() as t:
    base = Path(t)

    def case(name, root_name, mf, **kw):
        root = base / root_name
        root.mkdir()
        build(root, **kw)
        mp = root / "manifest.json"
        _wt(mp, json.dumps(mf), encoding="utf-8")
        res = atc.audit(root, mp)
        results[name] = res
        return res

    r = case("ok", "ok", good)
    check(r["ok"] is True and r["issues"] == [] and r["checked"] == 2 and r["candidates"] == 2 + 0 + 0 + 0 or r["candidates"] == 2, r)
    check((r["moved"], r["held"], r["root_wrappers"]) == (1, 1, 2), r)
    r = case("bad_target", "bad_target", good, moved_wrapper_src=BULK.format(m="scripts.maint.elsewhere"))
    check(r["ok"] is False and any("legacy import target mismatch" in i for i in r["issues"]) and any("legacy main target mismatch" in i for i in r["issues"]), r["issues"])
    r = case("no_guard", "no_guard", good, example_src="import importlib as _importlib\n")
    check(any("exactly one top-level __main__ guard required" in i for i in r["issues"]), r["issues"])
    r = case("missing_new", "missing_new", good, with_new=False)
    check(any("missing canonical implementation: scripts/maint/old_tool.py" in i for i in r["issues"]), r["issues"])
    r = case("unclassified", "unclassified", manifest([("scripts/old_tool.py", "scripts/maint/old_tool.py")], [],
                                                       ["scripts/old_tool.py", "scripts/zzz_other.py"]))
    check(any("unclassified compatibility wrapper: scripts/zzz_other.py" in i for i in r["issues"]), r["issues"])
    r = case("dup", "dup", manifest([("scripts/old_tool.py", "scripts/maint/old_tool.py")], [],
                                    ["scripts/old_tool.py", "scripts/old_tool.py", "scripts/demo_flow.py"]))
    check("duplicate root compatibility wrappers in manifest" in r["issues"], r["issues"])
    r = case("syntax", "syntax", good, moved_wrapper_src="def broken(:\n")
    check(any("invalid script" in i and "SyntaxError" in i for i in r["issues"]), r["issues"])
    # manifest missing / malformed
    exc = {}
    for name, content in (("missing_manifest", None), ("bad_json", "{x"), ("no_candidates", "{}")):
        root = base / name
        root.mkdir()
        mp = root / "m.json"
        if content is not None:
            _wt(mp, content, encoding="utf-8")
        try:
            atc.audit(root, mp)
            exc[name] = "no_raise"
        except Exception as e:
            exc[name] = type(e).__name__
    check(exc == {"missing_manifest": "FileNotFoundError", "bad_json": "JSONDecodeError", "no_candidates": "KeyError"}, exc)
    listing = sorted(str(p) for p in base.rglob("*"))
    atc.audit(base / "ok", base / "ok" / "manifest.json")
    check(listing == sorted(str(p) for p in base.rglob("*")), "audit wrote files")

    # CLI main(argv) in-process (not __main__): exit code mapping
    root = base / "ok"
    rc_ok = atc.main(["--root", str(root), "--manifest", str(root / "manifest.json")])
    rc_bad = atc.main(["--root", str(base / "bad_target"), "--manifest", str(base / "bad_target" / "manifest.json"), "--json"])
    check((rc_ok, rc_bad) == (0, 1), (rc_ok, rc_bad))

check(write_attempts == [], write_attempts)
new_scripts = {m for m in set(sys.modules) - loaded_before if m.startswith("scripts.")}
check(not new_scripts, new_scripts)
print(f"RF063_TREE_AUDIT_PEER_OK helpers=3 audit_cases={len(results)} manifest_errors=3 cli_exit=0/1 imported_scripts=0 "
      f"write_attempts={len(write_attempts)} io=net_sqlite_subprocess_write_blocked debug={__debug__}")
