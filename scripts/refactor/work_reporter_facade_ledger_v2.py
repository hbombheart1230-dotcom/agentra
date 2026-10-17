"""Write the Reporter current-head facade ledger v2 (historical v1 ledger stays untouched and pinned to BASE).

v2 = v1 rows/symbols (same names, kinds and dispositions, in order) with current HEAD start_line/end_line/physical_loc, plus
``r4_owner`` for every symbol whose body moved under the R-4 facade-injection pattern (from r4_facade_ledger.json)."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V1 = ROOT / "docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json"
R4 = ROOT / "docs/refactor/work_projects/evidence/reporter/r4_facade_ledger.json"
V2 = ROOT / "docs/refactor/work_projects/evidence/reporter/facade_symbol_ledger_v2.json"

v1 = json.loads(V1.read_text(encoding="utf-8"))
r4 = {(m["path"], m["name"]): m["r4_owner"] for m in json.loads(R4.read_text(encoding="utf-8"))["moves"]}
files = []
for row in v1["files"]:
    text = (ROOT / row["path"]).read_text(encoding="utf-8-sig")
    nodes = {n.name: n for n in ast.parse(text).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    syms = []
    for s in row["symbols"]:
        n = nodes[s["name"]]
        e = dict(s, start_line=n.lineno, end_line=n.end_lineno, physical_loc=n.end_lineno - n.lineno + 1)
        if (row["path"], s["name"]) in r4:
            e["r4_owner"] = r4[(row["path"], s["name"])]
        syms.append(e)
    files.append({"path": row["path"], "physical_loc": len(text.splitlines()), "symbols": syms})
doc = {"schema_version": "p152-facade-ledger-v2-reporter", "base_v1": "docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json",
       "runtime_base": "d773709ba2f70471fad9badba4f92400f7818319", "files": files}
V2.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print("v2 written", [(f["path"], f["physical_loc"]) for f in files])
