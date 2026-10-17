"""Read-only Strategist inventory over an extracted tree (git archive of the analysed SHA).
Usage: python -I strategist_readonly_inventory.py <tree> <out.json> <sha>. Effect labels are token heuristics, not proofs."""
import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

tree = Path(sys.argv[1])
NODE = "graphs/nodes/strategist_node.py"
PKGS = ["libs/runtime/strategist", "libs/agents/strategist"]

EFFECT_RULES = {
    "LLM": re.compile(r"\b(LLMRouter|llm_router|\.chat\(|\.complete\(|openrouter|call_llm|_invoke_llm|route_llm|model_name)\b", re.I),
    "FILE_WRITE": re.compile(r"\b(write_text|write_bytes|json\.dump\(|\.mkdir\(|append_decision_trace|append_[a-z_]+\(|os\.replace|shutil\.|unlink\()"),
    "FILE_READ": re.compile(r"\b(open\(|read_text|read_bytes|json\.load\(|\.exists\(|\.glob\(|\.iterdir\(|load_[a-z_]+\()"),
    "CLOCK": re.compile(r"\b(datetime\.now|datetime\.utcnow|time\.time\(|time\.monotonic|date\.today)"),
    "ENV": re.compile(r"\b(os\.environ|os\.getenv|getenv\()"),
    "NETWORK_DATA": re.compile(r"\b(collect_news_items|compute_global_sentiment_signal|requests\.|httpx\.|yfinance|kiwoom)", re.I),
    "BROKER_EXECUTION": re.compile(r"\b(broker|order_|place_order|execution|executor|supervisor)", re.I),
    "IDENTITY": re.compile(r"_r3_sys|__name__|sys\.modules"),
    "POLICY_THRESHOLD": re.compile(r"\b(threshold|max_|min_|cutoff|risk_off|position_size|sizing|stop_loss|take_profit)", re.I),
}


def loc(text):
    return sum(1 for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#"))


def py_files():
    for p in tree.rglob("*.py"):
        rel = p.relative_to(tree).as_posix()
        if "/__pycache__/" in rel or rel.startswith(("venv", ".venv")):
            continue
        yield rel, p


# import graph: which files import which strategist modules / node symbols
importers = defaultdict(set)
node_symbol_users = defaultdict(set)
for rel, p in py_files():
    try:
        mod = ast.parse(p.read_text(encoding="utf-8-sig"))
    except (SyntaxError, UnicodeDecodeError):
        continue
    for n in ast.walk(mod):
        if isinstance(n, ast.ImportFrom) and n.module:
            target = n.module
            if target.startswith(("libs.runtime.strategist", "libs.agents.strategist")) or target == "graphs.nodes.strategist_node":
                importers[target].add(rel)
            if target == "graphs.nodes.strategist_node":
                for a in n.names:
                    node_symbol_users[a.name].add(rel)
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith(("libs.runtime.strategist", "libs.agents.strategist", "graphs.nodes.strategist_node")):
                    importers[a.name].add(rel)
    # attribute use: strategist_node.X / sn.X via `import graphs.nodes.strategist_node as sn`
    text = p.read_text(encoding="utf-8-sig", errors="replace")
    if "strategist_node" in text and rel != NODE:
        for m in re.finditer(r"strategist_node\.([A-Za-z_][A-Za-z0-9_]*)", text):
            node_symbol_users[m.group(1)].add(rel)
        for m in re.finditer(r"""["']graphs\.nodes\.strategist_node\.([A-Za-z_][A-Za-z0-9_]*)["']""", text):
            node_symbol_users[m.group(1)].add(rel)


def classify(src):
    return sorted(k for k, rx in EFFECT_RULES.items() if rx.search(src))


def functions(rel):
    text = (tree / rel).read_text(encoding="utf-8-sig")
    mod = ast.parse(text)
    lines = text.splitlines()
    out = []
    names = defaultdict(int)
    for n in mod.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names[n.name] += 1
    for n in mod.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            src = "\n".join(lines[n.lineno - 1:n.end_lineno])
            body = [b for b in getattr(n, "body", []) if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))]
            call = body[0].value if len(body) == 1 and isinstance(body[0], (ast.Return, ast.Expr)) else None
            wrapper = isinstance(call, ast.Call) and any(k.arg == "facade" for k in call.keywords)
            out.append({"name": n.name, "kind": type(n).__name__, "line": n.lineno, "loc": loc(src),
                        "r3_wrapper": wrapper, "wrapper_target": ast.unparse(call.func) if wrapper else None,
                        "effects": [] if wrapper else classify(src), "redefined": names[n.name] > 1,
                        "external_users": sorted(node_symbol_users.get(n.name, ())) if rel == NODE else None})
    return text, mod, out


def is_identity_shim(text):
    return "sys.modules[__name__]" in text or ("_sys.modules" in text and loc(text) < 15)


node_text, node_mod, node_funcs = functions(NODE)
node_imports = sorted({n.module for n in node_mod.body if isinstance(n, ast.ImportFrom) and n.module})
module_level_stmts = [type(n).__name__ for n in node_mod.body
                      if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))
                      and not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]

pkg_files = []
for pkg in PKGS:
    for p in sorted((tree / pkg).rglob("*.py")):
        rel = p.relative_to(tree).as_posix()
        text = p.read_text(encoding="utf-8-sig")
        modname = rel[:-3].replace("/", ".").removesuffix(".__init__")
        _t, _m, fns = functions(rel)
        users = sorted(importers.get(modname, ()))
        pkg_files.append({"path": rel, "loc": loc(text), "physical_loc": len(text.splitlines()),
                          "identity_shim": is_identity_shim(text), "defs": len(fns),
                          "effects": sorted({e for f in fns for e in f["effects"]}),
                          "importers": users, "test_importers": [u for u in users if u.startswith("tests/")],
                          "functions": [{k: f[k] for k in ("name", "loc", "effects")} for f in fns]})

tests = sorted(rel for rel, p in py_files() if rel.startswith("tests/") and re.search(
    r"strategist|strategies\.contracts", p.read_text(encoding="utf-8-sig", errors="replace")))

doc = {
    "schema": "agentra.p15.strategist_readonly_inventory.v1",
    "tree_sha": sys.argv[3] if len(sys.argv) > 3 else None,
    "node": {"path": NODE, "physical_loc": len(node_text.splitlines()), "loc": loc(node_text),
             "top_level_defs": len(node_funcs), "imports_from": node_imports, "module_level_statements": module_level_stmts,
             "functions": node_funcs},
    "packages": pkg_files,
    "tests_mentioning_strategist": tests,
    "node_importers": sorted(importers.get("graphs.nodes.strategist_node", ())),
}
Path(sys.argv[2]).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# console summary
wr = [f for f in node_funcs if f["r3_wrapper"]]
print("R3 wrappers", len(wr), "loc", sum(f["loc"] for f in wr))
node_funcs_all = node_funcs
node_funcs = [f for f in node_funcs if not f["r3_wrapper"]]
print("residual bodies", len(node_funcs), "loc", sum(f["loc"] for f in node_funcs))
eff = defaultdict(int)
for f in node_funcs:
    for e in f["effects"] or ["NONE"]:
        eff[e] += 1
pure = [f for f in node_funcs if not set(f["effects"]) - {"POLICY_THRESHOLD"}]
print("node defs", len(node_funcs), "loc", loc(node_text), "effects", dict(eff))
print("node defs with no effect token (excluding POLICY_THRESHOLD):", len(pure), "loc", sum(f["loc"] for f in pure))
print("redefined:", sorted({f["name"] for f in node_funcs if f["redefined"]}))
print("externally used node symbols:", sum(1 for f in node_funcs if f["external_users"]))
print("pkg files", len(pkg_files), "shims", sum(f["identity_shim"] for f in pkg_files), "loc", sum(f["loc"] for f in pkg_files))
print("tests", len(tests), "node importers", len(doc["node_importers"]))
