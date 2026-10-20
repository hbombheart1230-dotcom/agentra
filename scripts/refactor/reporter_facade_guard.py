"""Work proposal: exact BASE restoration, not a required CI gate until integrated.

No facade is imported or executed. The move inventory comes from a reviewed Git
object, never from an editable working-tree ledger. Run alongside the existing
R4 owner-body/lazy-binding proof; this checks the previously uncovered facade.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE = "d773709ba2f70471fad9badba4f92400f7818319"
REVIEWED = "443f90362ad5970a4731685311a45e8e0f6b55e4"
PINNED_INVENTORIES = {
    REVIEWED: 313,
    "8ce327ecc71c4c92074c1fa5fb6f00428ba9279b": 264,
    "523dd9ac227a33eb9e5aa9bed82957e4111c5d9b": 286,
    "dd0b378b46dff0c2ecf6699a4b08776fd4412b76": 313,
    # R10 is test/evidence-only on the 313-move R9 facade/owner tree. Verify git diff before admitting a SHA.
    "de99c8f0fa66bfc3e6be9a229f04fc6aad5ca06e": 313,
}
LEDGER = "docs/refactor/work_projects/evidence/reporter/r4_facade_ledger.json"
# P1.5 CODE BATCH01 DEV-A (Issue #20, peer PASS at ad4eed21d8303d4d8cb99f4097b4812cf2522f97): versioned, content-pinned
# Reporter transition. Exactly one owner import and one function body may differ; after reverting that delta to BASE the
# strict R7 restoration below must still hold. Any other facade/owner change, or an extra owner file, fails closed.
P15_TRANSITION_PROVENANCE = "ad4eed21d8303d4d8cb99f4097b4812cf2522f97"
P15_TRANSITIONS = {
    "libs/reporting/reporter_analysis.py": {
        "import": "from libs.agents.reporter.read_models import analysis_report_projection as _analysis_projection",
        "function": "generate_reporter_analysis_report",
        "function_ast_sha256": "0ffda4674e0457476a4cf069f9ed9dd5608a89af92f614c4f69aa4e8901421f7",
    },
}
P15_OWNERS = {
    "libs/agents/reporter/read_models/analysis_report_projection.py":
        "05fee281f89df834e52edf2a22338359c9069daab55fd6cc4957b3a0f02ad5e9",
}


def require(condition, message):
    # Must remain fail-closed with python -O.
    if not condition:
        raise AssertionError(message)


def dump(node):
    return ast.dump(node, include_attributes=False)


def git_text(root, sha, path):
    return subprocess.check_output(
        ["git", "show", f"{sha}:{path}"], cwd=root
    ).decode("utf-8-sig")


def moves(root, reviewed=REVIEWED):
    require(reviewed in PINNED_INVENTORIES, "unreviewed inventory SHA")
    count = PINNED_INVENTORIES[reviewed]
    doc = json.loads(git_text(root, reviewed, LEDGER))
    rows = doc["moves"]
    require(doc["base"] == BASE and len(rows) == count, "pinned inventory")
    require(len({(r["path"], r["name"]) for r in rows}) == count, "duplicate move")
    return rows


def docstring(node):
    return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str))


def wrapper_bodies(fn):
    """Two exact forwarding forms used by R7; expressions may only load args."""
    a = fn.args
    posonly = [p.arg for p in a.posonlyargs]
    positional = [p.arg for p in a.args]
    for named in (False, True):
        parts = list(posonly)
        parts += [f"{n}={n}" if named else n for n in positional]
        if a.vararg:
            # Positional forwarding is necessary to avoid duplicate binding.
            if named:
                continue
            parts.append("*" + a.vararg.arg)
        parts += [f"{p.arg}={p.arg}" for p in a.kwonlyargs]
        parts.append("facade=_r3_sys.modules[__name__]")
        if a.kwarg:
            parts.append("**" + a.kwarg.arg)
        yield ast.parse(f"return {fn.name}_r4_impl({', '.join(parts)})").body


def verify_facade(base_text, current_text, rows, path):
    base = ast.parse(base_text)
    current = current_text if isinstance(current_text, ast.Module) else ast.parse(current_text)
    expected = {}
    for r in rows:
        module = r["r4_owner"][:-3].replace("/", ".")
        expected.setdefault(module, set()).add(r["name"] + "_r4_impl")
    originals = {n.name: n for n in base.body if isinstance(n, ast.FunctionDef)}
    selected = {r["name"] for r in rows}
    require(selected <= originals.keys(), f"{path}: unknown BASE function")
    seen_imports, seen_functions = set(), set()
    restored = []
    base_sys = any(dump(n) == dump(ast.parse("import sys as _r3_sys").body[0])
                   for n in base.body)
    added_sys = 0
    seen_definition = False
    for node in current.body:
        if isinstance(node, ast.ImportFrom) and node.module in expected:
            require(not seen_definition, f"{path}: late owner import")
            require(node.level == 0, f"{path}: relative owner import")
            for alias in node.names:
                key = (node.module, alias.name)
                require(alias.asname is None and alias.name in expected[node.module]
                        and key not in seen_imports, f"{path}: owner import alias/extra/duplicate")
                seen_imports.add(key)
            continue
        if not base_sys and dump(node) == dump(ast.parse("import sys as _r3_sys").body[0]):
            require(not seen_definition, f"{path}: late sys import")
            added_sys += 1
            require(added_sys == 1, f"{path}: duplicate sys import")
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            seen_definition = True
        if isinstance(node, ast.FunctionDef) and node.name in selected:
            require(node.name not in seen_functions, f"{path}: duplicate wrapper")
            seen_functions.add(node.name)
            original = originals[node.name]
            header = copy.deepcopy(node)
            header.body = copy.deepcopy(original.body)
            require(dump(header) == dump(original), f"{path}:{node.name}: ABI/header changed")
            body = node.body
            if body and docstring(body[0]):
                require(docstring(original.body[0]) and dump(body[0]) == dump(original.body[0]),
                        f"{path}:{node.name}: changed docstring")
                body = body[1:]
            require(any([dump(n) for n in body] == [dump(n) for n in candidate]
                        for candidate in wrapper_bodies(original)),
                    f"{path}:{node.name}: non-forwarding wrapper")
            restored.append(copy.deepcopy(original))
        else:
            restored.append(node)
    require(seen_functions == selected, f"{path}: missing wrapper")
    require(seen_imports == {(m, n) for m, names in expected.items() for n in names},
            f"{path}: missing owner import")
    require(base_sys or added_sys == 1, f"{path}: missing facade sys binding")
    current.body = restored
    require(dump(current) == dump(base),
            f"{path}: unmoved definition/module statement/order differs from BASE")


def revert_p15_transition(base_text, current_text, path, transitions=P15_TRANSITIONS):
    """Return the facade AST with its pinned P1.5 delta replaced by BASE; reject any other form of that delta."""
    current = ast.parse(current_text)
    spec = transitions.get(path)
    if spec is None:
        return current
    allowed = dump(ast.parse(spec["import"]).body[0])
    first_def = next(i for i, n in enumerate(current.body)
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))
    hits = [i for i, n in enumerate(current.body) if dump(n) == allowed]
    require(len(hits) == 1 and hits[0] < first_def, f"{path}: P1.5 transition import missing/duplicate/late")
    fns = [i for i, n in enumerate(current.body) if isinstance(n, ast.FunctionDef) and n.name == spec["function"]]
    require(len(fns) == 1, f"{path}: P1.5 transition function missing/duplicate")
    digest = hashlib.sha256(dump(current.body[fns[0]]).encode("utf-8")).hexdigest()
    require(digest == spec["function_ast_sha256"], f"{path}:{spec['function']}: P1.5 transition body/ABI changed")
    original = [n for n in ast.parse(base_text).body if isinstance(n, ast.FunctionDef) and n.name == spec["function"]]
    require(len(original) == 1, f"{path}: P1.5 transition function absent at BASE")
    current.body[fns[0]] = copy.deepcopy(original[0])
    del current.body[hits[0]]
    return current


def verify_p15_owner(text, path, owners=P15_OWNERS):
    require(path in owners, f"{path}: unregistered P1.5 Reporter owner")
    digest = hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()
    require(digest == owners[path], f"{path}: P1.5 owner bytes differ from the pinned transition")


def verify_tree(root, overrides=None, reviewed=REVIEWED, transitions=P15_TRANSITIONS, owners=P15_OWNERS):
    """Current stage: R7 restoration after the pinned P1.5 delta. ``transitions={}, owners={}`` is the strict
    historical R7 stage, which must still hold on the pre-transition facade bytes."""
    root = Path(root)
    overrides = overrides or {}
    rows = moves(root, reviewed)
    paths = sorted({r["path"] for r in rows})
    require(set(transitions) <= set(paths), "P1.5 transition outside the registered R7 facades")
    for path in paths:
        text = overrides.get(path)
        if text is None:
            text = (root / path).read_text(encoding="utf-8-sig")
        base_text = git_text(root, BASE, path)
        verify_facade(base_text, revert_p15_transition(base_text, text, path, transitions),
                      [r for r in rows if r["path"] == path], path)
    for path in sorted(owners):
        text = overrides.get(path)
        if text is None:
            text = (root / path).read_text(encoding="utf-8-sig")
        verify_p15_owner(text, path, owners)
    return {"base": BASE, "reviewed": reviewed, "facades": len(paths), "moves": len(rows),
            "p15_transitions": len(transitions), "p15_owners": len(owners)}


if __name__ == "__main__":
    print(json.dumps(verify_tree(sys.argv[1], reviewed=sys.argv[2] if len(sys.argv) > 2 else REVIEWED),
                     sort_keys=True))
