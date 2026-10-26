# RF-016: STATIC (AST-only, nothing imported or executed) -- does any in-repo consumer mutate the dict returned by
# _build_strategic_answers / the `strategic_answers` name, in particular the nested objects that run 115 showed are shared with the inputs?
# Run from the repo root: python / python -O. Read-only.
import ast, os, sys, json
from pathlib import Path
repo = Path(os.getcwd()).resolve()
MUT = {"update", "setdefault", "pop", "popitem", "clear", "append", "extend", "insert", "remove", "sort", "reverse", "__setitem__", "__delitem__"}
ALIAS_KEYS = {"entry_state", "scanner_primary_candidate", "q14_recent_playbook_performance", "recent_playbook_performance", "session_open_recovery_assessment", "q15_commander_refresh_context"}
def root_name(n):
    while isinstance(n, (ast.Subscript, ast.Attribute)): n = n.value
    return n.id if isinstance(n, ast.Name) else None
def is_sa(n):  # an expression rooted at a strategic_answers-like name
    r = root_name(n); return bool(r) and "strategic_answers" in r
refs, writes = {}, []
for base in ("libs", "graphs", "scripts", "apps"):
    for p in sorted((repo / base).rglob("*.py")) if (repo / base).is_dir() else []:
        if "scripts/refactor" in p.as_posix(): continue
        try: tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception: continue
        rel = p.relative_to(repo).as_posix(); n_ref = 0
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and "strategic_answers" in n.id: n_ref += 1
            if isinstance(n, ast.Constant) and n.value == "strategic_answers": n_ref += 1
            tgts = []
            if isinstance(n, ast.Assign): tgts = n.targets
            elif isinstance(n, (ast.AugAssign, ast.AnnAssign)): tgts = [n.target]
            elif isinstance(n, ast.Delete): tgts = n.targets
            for t in tgts:
                if isinstance(t, ast.Subscript) and is_sa(t):
                    key = t.slice.value if isinstance(t.slice, ast.Constant) else "<dyn>"
                    writes.append({"file": rel, "line": n.lineno, "kind": "subscript_store", "root": root_name(t), "depth": sum(isinstance(x, ast.Subscript) for x in ast.walk(t) if x is not t) + 1, "key": key})
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in MUT and is_sa(n.func.value):
                writes.append({"file": rel, "line": n.lineno, "kind": "method:" + n.func.attr, "root": root_name(n.func.value), "depth": 0, "key": ""})
        if n_ref: refs[rel] = n_ref
# subscripted reads of alias keys outside the owner module (could be a mutation via alias -- checked as store targets below)
alias_stores = []
for base in ("libs", "graphs", "scripts", "apps"):
    for p in sorted((repo / base).rglob("*.py")) if (repo / base).is_dir() else []:
        if "scripts/refactor" in p.as_posix(): continue
        try: tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception: continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    for s in ast.walk(t):
                        if isinstance(s, ast.Subscript) and isinstance(s.slice, ast.Constant) and s.slice.value in ALIAS_KEYS and p.relative_to(repo).as_posix() != "libs/agents/strategist/output/strategic_answers.py":
                            alias_stores.append({"file": p.relative_to(repo).as_posix(), "line": n.lineno, "key": s.slice.value})
out = {"files_referencing": refs, "writes_to_strategic_answers_name": writes, "alias_key_stores_outside_owner": alias_stores}
print("RF016_STATIC_OK files=%d writes=%d alias_key_stores=%d debug=%s" % (len(refs), len(writes), len(alias_stores), __debug__), file=sys.stderr)
print(json.dumps(out, sort_keys=True, indent=1))
