# RF-031: which of the 22 owner files would trip the frozen RF-074 oracle if edited (static; reconstructs _scope_violations, runs no test).
import ast, csv, json, os, sys
from pathlib import Path
repo = Path(os.getcwd()).resolve()
files = sorted(r[0] for r in csv.reader(open(sys.argv[1], encoding="utf-8")) if len(r) > 1 and r[1] == "RF-031")
assert len(files) == 22, len(files)
tt = ast.parse((repo / "tests/test_work_reporter_seed_migration.py").read_text(encoding="utf-8"))
ns = {"Path": Path, "ROOT": repo, "json": json}
for node in tt.body:
    if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
        try: exec(compile(ast.Module(body=[node], type_ignores=[]), "c", "exec"), ns)
        except Exception: pass
    if isinstance(node, ast.FunctionDef) and node.name == "_scope_violations":
        exec(compile(ast.Module(body=[node], type_ignores=[]), "f", "exec"), ns)
forbidden = sorted(f for f in files if ns["_scope_violations"]([f], merged=True))
print(json.dumps({"forbidden": forbidden, "editable": sorted(set(files) - set(forbidden))}, indent=1))
print("RF031_ORACLE_SCOPE_OK files=22 forbidden=%d editable=%d" % (len(forbidden), 22 - len(forbidden)))
