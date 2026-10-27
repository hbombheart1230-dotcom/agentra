# RF-035 OWNER inventory (A): static, read-only inventory of the 119 RF-035 files (libs/reporting/** "remaining services / publishing").
# Per file: lines, top-level defs, IO/effect signals (write / read / subprocess / network / env / sqlite / LLM), facade-or-wrapper shape, repo importers,
# and whether editing it would trip the frozen RF-074 oracle (tests/test_work_reporter_seed_migration.py::_scope_violations(merged=True), evaluated by importing
# ONLY that helper's constants via AST -- the frozen test file is not executed or modified). Usage: (cd <repo>; python [-O] rf035_owner_inventory.py <coverage_csv>)
import os, sys, ast, csv, re, json, hashlib, subprocess
from pathlib import Path
repo = Path(os.getcwd()).resolve(); cov = Path(sys.argv[1])
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: %s" % (sys._getframe(1).f_lineno, m))
files = sorted(r[0] for r in csv.reader(cov.open(encoding="utf-8")) if len(r) > 1 and r[1] == "RF-035")
check(len(files) == 119, len(files))
present = [f for f in files if (repo / f).exists()]
# --- frozen oracle allowlist, reconstructed by evaluating the test module's top-level constant assignments only (no test execution)
tsrc = (repo / "tests/test_work_reporter_seed_migration.py").read_text(encoding="utf-8"); tt = ast.parse(tsrc)
ns = {"Path": Path, "ROOT": repo, "json": json}
for node in tt.body:
    if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
        try: exec(compile(ast.Module(body=[node], type_ignores=[]), "oracle_consts", "exec"), ns)
        except Exception: pass
    if isinstance(node, ast.FunctionDef) and node.name == "_scope_violations":
        exec(compile(ast.Module(body=[node], type_ignores=[]), "oracle_fn", "exec"), ns)
check("_scope_violations" in ns, "oracle helper reconstructed")
violations = set(ns["_scope_violations"](present, merged=True))
PAT = {"write": r"write_text|write_bytes|\.open\([^)]*['\"][wa]|open\([^)]*['\"][wa]|json\.dump\(|\.mkdir\(|os\.replace|shutil\.(copy|move|rmtree)|\.unlink\(",
       "read": r"read_text|read_bytes|json\.load\(|open\(", "subprocess": r"subprocess|run_hidden|popen_hidden|os\.system", "network": r"requests\.|urllib|http\.client|socket\.|httpx",
       "env": r"os\.getenv|os\.environ|load_env_file", "sqlite": r"sqlite3", "llm": r"openrouter|llm_client|chat_completion|call_llm|OpenRouter"}
importers = {}
allpy = [p for p in repo.rglob("*.py") if "/site-packages/" not in p.as_posix() and ".venv" not in p.parts]
srcs = {}
for p in allpy:
    try: srcs[p.relative_to(repo).as_posix()] = p.read_text(encoding="utf-8-sig")
    except Exception: pass
rows = []
for f in present:
    src = srcs.get(f) or (repo / f).read_text(encoding="utf-8-sig"); t = ast.parse(src.lstrip("\ufeff"))
    defs = [n for n in t.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    mod = f[:-3].replace("/", ".");
    if mod.endswith(".__init__"): mod = mod[:-9]
    imp = sum(1 for k, v in srcs.items() if k != f and (re.search(r"(from|import)\s+%s(\s|\.|$)" % re.escape(mod), v) or re.search(r"from\s+%s\s+import" % re.escape(mod.rsplit(".", 1)[0]) + r"[^\n]*\b%s\b" % re.escape(mod.rsplit(".", 1)[-1]), v)))
    flags = [k for k, pat in PAT.items() if re.search(pat, src)]
    shape = "empty" if not src.strip() else "wrapper" if (len(defs) == 0 and len(src.splitlines()) < 40) else "facade_r3" if "_r3_sys.modules" in src or "facade=" in src else "module"
    rows.append({"file": f, "lines": len(src.splitlines()), "defs": len(defs), "shape": shape, "effects": flags, "importers": imp, "oracle_forbidden": f in violations,
                 "blob": subprocess.run(["git", "hash-object", str(repo / f)], capture_output=True, text=True).stdout.strip()[:8]})
summ = {"files": len(files), "present": len(present), "missing": len(files) - len(present), "lines_total": sum(r["lines"] for r in rows),
        "oracle_forbidden": sum(r["oracle_forbidden"] for r in rows), "oracle_editable": sum(not r["oracle_forbidden"] for r in rows),
        "with_write": sum("write" in r["effects"] for r in rows), "with_subprocess": sum("subprocess" in r["effects"] for r in rows), "with_network": sum("network" in r["effects"] for r in rows),
        "with_env": sum("env" in r["effects"] for r in rows), "with_llm": sum("llm" in r["effects"] for r in rows), "with_sqlite": sum("sqlite" in r["effects"] for r in rows),
        "no_importers": sum(r["importers"] == 0 for r in rows), "shape": {s: sum(r["shape"] == s for r in rows) for s in ("empty", "wrapper", "facade_r3", "module")}}
editable_effectless = [r["file"] for r in rows if not r["oracle_forbidden"] and not set(r["effects"]) & {"write", "subprocess", "network", "llm", "sqlite"}]
summ["editable_and_effect_free"] = len(editable_effectless)
digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()[:12]
print(json.dumps({"summary": summ, "editable_effect_free": editable_effectless, "largest": sorted(((r["lines"], r["file"]) for r in rows), reverse=True)[:10],
                  "write_subprocess_network": sorted(r["file"] for r in rows if set(r["effects"]) & {"subprocess", "network", "llm"}), "rows_digest": digest}, ensure_ascii=False, sort_keys=True))
print(json.dumps(rows, ensure_ascii=False, sort_keys=True))
print("RF035_OWNER_INVENTORY_OK files=%d lines=%d oracle_forbidden=%d editable=%d write=%d subprocess=%d network=%d llm=%d editable_effect_free=%d digest=%s" % (summ["present"], summ["lines_total"], summ["oracle_forbidden"], summ["oracle_editable"], summ["with_write"], summ["with_subprocess"], summ["with_network"], summ["with_llm"], len(editable_effectless), digest))
