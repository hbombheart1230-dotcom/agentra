"""Transitive I/O / clock / env purity analysis of the call closure of a statement run (static, project modules only)."""
import ast
import os
import sys

ROOT = "C:/AgentraEvidence/r3_seam_clone"
IO_ATTRS = {"read_text", "write_text", "read_bytes", "write_bytes", "exists", "is_file", "is_dir", "open", "mkdir",
            "unlink", "iterdir", "glob", "rglob", "stat", "rename", "replace", "touch", "rmdir", "makedirs", "listdir",
            "getenv", "system", "popen", "dump", "load", "now", "utcnow", "today", "time", "sleep", "write", "flush",
            "info", "warning", "error", "exception", "debug", "send", "post", "get_nowait", "put"}
IO_NAMES = {"open", "print", "_read_json", "read_json", "write_json", "iter_jsonl_events", "utc_now_iso", "_utc_now_iso",
            "_log_bundle_event", "getenv", "input", "_touch_background_job_lock"}
IO_ROOTS = {"os", "shutil", "subprocess", "time", "datetime", "logging", "socket", "sqlite3", "requests", "tempfile"}
_cache = {}


def mod_path(mod):
    p = ROOT + "/" + mod.replace(".", "/") + ".py"
    return p if os.path.isfile(p) else None


def load(path):
    if path not in _cache:
        src = open(path, encoding="utf-8-sig").read()
        tree = ast.parse(src)
        funcs = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        imports = {}
        for n in tree.body:
            if isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                for a in n.names:
                    imports[a.asname or a.name] = (n.module, a.name)
        for n in ast.walk(tree):  # function-local imports
            if isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                for a in n.names:
                    imports.setdefault(a.asname or a.name, (n.module, a.name))
        _cache[path] = (funcs, imports)
    return _cache[path]


def own_issues(fn):
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id in IO_NAMES:
                out.append(f"call {f.id}()")
            if isinstance(f, ast.Attribute):
                r = f
                while isinstance(r, (ast.Attribute, ast.Subscript, ast.Call)):
                    r = r.value if not isinstance(r, ast.Call) else r.func
                if isinstance(r, ast.Name) and r.id in IO_ROOTS and not (r.id == "datetime" and f.attr not in ("now", "utcnow", "today")):
                    out.append(f"call {r.id}.{f.attr}()")
                elif f.attr in IO_ATTRS and f.attr not in ("get", "load", "dump", "write", "info", "error", "time", "now", "post", "put", "send", "replace", "open", "debug", "warning", "exception", "flush"):
                    out.append(f"method .{f.attr}()")
                elif f.attr in ("read_text", "write_text", "exists", "mkdir", "open", "is_file", "is_dir", "unlink", "iterdir", "glob"):
                    out.append(f"method .{f.attr}()")
    return sorted(set(out))


def closure(path, name, seen, depth=0, chain=()):
    """Return list of (chain, issue) for the function and everything it calls (project code only)."""
    key = (path, name)
    if key in seen or depth > 6:
        return []
    seen.add(key)
    funcs, imports = load(path)
    fn = funcs.get(name)
    if fn is None:
        if name in imports:
            mod, orig = imports[name]
            p = mod_path(mod)
            if p:
                return closure(p, orig, seen, depth + 1, chain)
        return []
    res = [(chain + (name,), i) for i in own_issues(fn)]
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            res += closure(path, n.func.id, seen, depth + 1, chain + (name,))
    return res


def analyse_run(path, stmts):
    """Issues for all calls made directly by statements."""
    issues, callees = [], set()
    for s in stmts:
        for n in ast.walk(s):
            if isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name):
                    callees.add(f.id)
                    if f.id in IO_NAMES:
                        issues.append((("<run>",), f"call {f.id}()"))
                    else:
                        issues += closure(path, f.id, set(), 0, ("<run>",))
                elif isinstance(f, ast.Attribute):
                    r = f
                    while isinstance(r, (ast.Attribute, ast.Subscript, ast.Call)):
                        r = r.value if not isinstance(r, ast.Call) else r.func
                    if isinstance(r, ast.Name) and r.id in IO_ROOTS and not (r.id == "datetime" and f.attr not in ("now", "utcnow", "today")):
                        issues.append((("<run>",), f"call {r.id}.{f.attr}()"))
                    elif f.attr in ("read_text", "write_text", "exists", "mkdir", "is_file", "is_dir", "unlink", "iterdir", "glob", "open"):
                        issues.append((("<run>",), f"method .{f.attr}()"))
    return sorted(callees), issues


if __name__ == "__main__":
    path = ROOT + "/" + sys.argv[1]
    start, end = int(sys.argv[2]), int(sys.argv[3])
    tree = ast.parse(open(path, encoding="utf-8-sig").read())
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == sys.argv[4]][0]
    stmts = [n for n in ast.walk(fn) if isinstance(n, ast.stmt) and start <= n.lineno and n.end_lineno <= end]
    # only top-level statements within the range (avoid double counting)
    top = [s for s in stmts if not any(o is not s and o.lineno <= s.lineno and s.end_lineno <= o.end_lineno and o in stmts for o in stmts)]
    callees, issues = analyse_run(path, top)
    print("callees:", callees)
    seen = set()
    for chain, issue in issues:
        k = (chain[-1], issue)
        if k in seen:
            continue
        seen.add(k)
        print("  IMPURE:", " > ".join(chain[:5]), "::", issue)
    print("VERDICT:", "PURE (static)" if not issues else "NOT PURE")
