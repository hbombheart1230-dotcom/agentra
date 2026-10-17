"""Work proposal: exact BASE restoration, not a required CI gate until integrated.

No facade is imported or executed. The move inventory comes from a reviewed Git
object, never from an editable working-tree ledger. Run alongside the existing
R4 owner-body/lazy-binding proof; this checks the previously uncovered facade.
"""
import ast
import copy
import json
from pathlib import Path
import subprocess
import sys

BASE = "d773709ba2f70471fad9badba4f92400f7818319"
REVIEWED = "8ce327ecc71c4c92074c1fa5fb6f00428ba9279b"
PINNED_INVENTORIES = {
    REVIEWED: 264,
    "523dd9ac227a33eb9e5aa9bed82957e4111c5d9b": 286,
    "dd0b378b46dff0c2ecf6699a4b08776fd4412b76": 313,
}
LEDGER = "docs/refactor/work_projects/evidence/reporter/r4_facade_ledger.json"


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
    base, current = ast.parse(base_text), ast.parse(current_text)
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


def verify_tree(root, overrides=None, reviewed=REVIEWED):
    root = Path(root)
    overrides = overrides or {}
    rows = moves(root, reviewed)
    paths = sorted({r["path"] for r in rows})
    for path in paths:
        text = overrides.get(path)
        if text is None:
            text = (root / path).read_text(encoding="utf-8-sig")
        verify_facade(git_text(root, BASE, path), text,
                      [r for r in rows if r["path"] == path], path)
    return {"base": BASE, "reviewed": reviewed, "facades": len(paths), "moves": len(rows)}


if __name__ == "__main__":
    print(json.dumps(verify_tree(sys.argv[1], reviewed=sys.argv[2] if len(sys.argv) > 2 else REVIEWED),
                     sort_keys=True))
