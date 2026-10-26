# RF-008: STATIC (nothing imported or executed). run 114 mapped the 4 static `from graphs.nodes.strategist_node import strategist_node` callers.
# This covers the remaining reachability classes for graphs/nodes/strategist_node.py: dynamic import (importlib/__import__/getattr/string module path),
# `python -m` / script entrypoints in non-Python files (workflows, shell/PowerShell/batch, Dockerfiles, pyproject/setup, JSON/YAML), and other import forms
# (`import graphs.nodes.strategist_node`, `from graphs.nodes import strategist_node`). Run from the repo root: python / python -O. Read-only.
import ast, os, sys, json, re
from pathlib import Path
repo = Path(os.getcwd()).resolve()
MOD = "graphs.nodes.strategist_node"; SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv"}
res = {"py_static_import_from": [], "py_import_module": [], "py_from_package_import": [], "py_dynamic": [], "py_string_literal": [], "non_py": [], "docs_mentions": 0}
for root, dirs, files in os.walk(repo):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        p = Path(root) / f; rel = p.relative_to(repo).as_posix()
        if rel.startswith("docs/refactor/work_orders/evidence/run103_boundary_scripts/"): continue
        try: txt = p.read_text(encoding="utf-8")
        except Exception: continue
        if "strategist_node" not in txt: continue
        if p.suffix == ".py":
            try: tree = ast.parse(txt)
            except Exception: res["py_dynamic"].append({"file": rel, "why": "unparsable"}); continue
            for n in ast.walk(tree):
                if isinstance(n, ast.ImportFrom):
                    if n.module == MOD: res["py_static_import_from"].append({"file": rel, "line": n.lineno, "names": [a.name for a in n.names]})
                    elif n.module == "graphs.nodes" and any(a.name == "strategist_node" for a in n.names): res["py_from_package_import"].append({"file": rel, "line": n.lineno})
                elif isinstance(n, ast.Import):
                    for a in n.names:
                        if a.name == MOD: res["py_import_module"].append({"file": rel, "line": n.lineno})
                elif isinstance(n, ast.Call):
                    fn = n.func; nm = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
                    if nm in ("import_module", "__import__", "spec_from_file_location", "run_module", "run_path", "reload"):
                        arg = ast.unparse(n.args[0]) if n.args else ""
                        if "strategist_node" in arg or not isinstance(n.args[0] if n.args else None, ast.Constant):
                            res["py_dynamic"].append({"file": rel, "line": n.lineno, "call": nm, "arg": arg[:80]})
                elif isinstance(n, ast.Constant) and isinstance(n.value, str) and "strategist_node" in n.value and n.value.strip() != "strategist_node":
                    res["py_string_literal"].append({"file": rel, "line": n.lineno, "text": n.value[:90]})
        elif rel.startswith("docs/"):
            res["docs_mentions"] += 1
        else:
            for i, line in enumerate(txt.splitlines(), 1):
                if "strategist_node" in line: res["non_py"].append({"file": rel, "line": i, "text": line.strip()[:110]})
for k in res:
    if isinstance(res[k], list): res[k].sort(key=lambda r: (r["file"], r.get("line", 0)))
# classify string literals: references vs. only the module's own path/names
res["summary"] = {k: (len(v) if isinstance(v, list) else v) for k, v in res.items()}
res["static_import_from_prod_files"] = sorted({r["file"] for r in res["py_static_import_from"] if not r["file"].startswith("tests/")})
res["static_import_from_test_files"] = sorted({r["file"] for r in res["py_static_import_from"] if r["file"].startswith("tests/")})
print("RF008_DYNAMIC_STATIC_OK prod_static=%d test_static=%d dynamic=%d non_py=%d debug=%s" % (len(res["static_import_from_prod_files"]), len(res["static_import_from_test_files"]), len(res["py_dynamic"]), len(res["non_py"]), __debug__), file=sys.stderr)
print(json.dumps(res, sort_keys=True, indent=1, ensure_ascii=True))
