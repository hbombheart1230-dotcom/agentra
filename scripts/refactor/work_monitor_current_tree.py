"""Exact current-tree contract for authorized continuous Monitor batches.

Not a discover/follow mechanism: only literal registered pairs are accepted.
No production module imports, no policy/effect execution, no shared gate edits.
"""
from __future__ import annotations

import ast
import copy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "d773709ba2f70471fad9badba4f92400f7818319"
WHOLE_MOVES = {
    "libs/runtime/monitor/entry_evidence.py": "libs/agents/monitor/projections/entry_evidence.py",
    "libs/runtime/monitor_exit/observability.py": "libs/agents/monitor/projections/observability.py",
    "libs/runtime/monitor_exit/order_lifecycle.py": "libs/agents/monitor/projections/order_lifecycle.py",
}

# Explicit function sets only; no wildcard facade or generic shim following.
BODY_MOVES = {
    "libs/runtime/monitor_exit/selected_snapshot.py": {
        "owner": "libs/agents/monitor/projections/feature_context_views.py",
        "functions": {"feature_alias_map": (), "feature_context_from_state": ()},
    },
    "libs/runtime/monitor_entry_state.py": {
        "owner": "libs/agents/monitor/projections/entry_state_views.py",
        "functions": {"monitor_posture_for_cycle": (),
                      "build_monitor_entry_state_snapshot": ("_optional_float",),
                      "build_monitor_entry_transition_trace": ("_optional_float",)},
    },
}


def _dump(node):
    return ast.dump(node, include_attributes=False)


def _tree(text):
    return ast.parse(text.lstrip("\ufeff"))


def body_templates(path):
    """Generate the only permitted facade and Owner AST from immutable BASE.

    Every original module statement/unmoved function is retained. Selected body
    loads of explicitly declared globals are the ONLY allowed body substitutions.
    Added imports, wrappers, signatures and Owner statements are exact, not a
    token allowlist. Verification never executes production code.
    """
    spec = BODY_MOVES[path]
    base = _tree(base_source(path))
    facade = copy.deepcopy(base)
    owner = ast.parse('"""Monitor observation views; policy/effects remain at the facade."""\n'
                      'from __future__ import annotations\nfrom typing import Any, Dict\n')
    module = spec["owner"][:-3].replace("/", ".")
    imports = ast.parse(f"import sys as _monitor_view_sys\nimport {module} as _monitor_views\n").body
    index = next(i for i, node in enumerate(facade.body) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))
    facade.body[index:index] = imports
    found = set()
    for i, node in enumerate(facade.body):
        if not isinstance(node, ast.FunctionDef) or node.name not in spec["functions"]:
            continue
        found.add(node.name)
        moved = copy.deepcopy(node)
        if moved.decorator_list or moved.args.vararg or moved.args.kwarg:
            raise AssertionError("unreviewed extraction signature")
        globals_ = spec["functions"][node.name]
        class Qualify(ast.NodeTransformer):
            def visit_Name(self, value):
                if isinstance(value.ctx, ast.Load) and value.id in globals_:
                    return ast.copy_location(ast.Attribute(value=ast.Name(id="facade", ctx=ast.Load()), attr=value.id, ctx=ast.Load()), value)
                return value
        moved.body = [Qualify().visit(statement) for statement in moved.body]
        moved.args.kwonlyargs.append(ast.arg(arg="facade"))
        moved.args.kw_defaults.append(None)
        owner.body.append(moved)
        args = [ast.Name(id=a.arg, ctx=ast.Load()) for a in node.args.posonlyargs + node.args.args]
        keywords = [ast.keyword(arg=a.arg, value=ast.Name(id=a.arg, ctx=ast.Load())) for a in node.args.kwonlyargs]
        facade_value = ast.Subscript(value=ast.Attribute(value=ast.Name(id="_monitor_view_sys", ctx=ast.Load()), attr="modules", ctx=ast.Load()), slice=ast.Name(id="__name__", ctx=ast.Load()), ctx=ast.Load())
        keywords.append(ast.keyword(arg="facade", value=facade_value))
        call = ast.Call(func=ast.Attribute(value=ast.Name(id="_monitor_views", ctx=ast.Load()), attr=node.name, ctx=ast.Load()), args=args, keywords=keywords)
        doc = node.body[:1] if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str) else []
        node.body = doc + [ast.Return(value=call)]
    if found != set(spec["functions"]):
        raise AssertionError("missing BASE function")
    return ast.fix_missing_locations(facade), ast.fix_missing_locations(owner)


def verify_body_transfer(path, source, owner_source):
    facade, owner = body_templates(path)
    if _dump(_tree(source)) != _dump(facade):
        raise AssertionError(f"changed facade/unmoved AST: {path}")
    if _dump(_tree(owner_source)) != _dump(owner):
        raise AssertionError(f"changed extracted body/authority: {path}")
    # Once the exact projection was verified, restore every original definition
    # and remove ONLY the two known injected imports; compare the complete module.
    restored = _tree(source)
    base = _tree(base_source(path))
    originals = {n.name: n for n in base.body if isinstance(n, ast.FunctionDef)}
    restored.body = [copy.deepcopy(originals[n.name]) if isinstance(n, ast.FunctionDef) and n.name in BODY_MOVES[path]["functions"] else n for n in restored.body
                     if not (isinstance(n, ast.Import) and any(a.asname in {"_monitor_view_sys", "_monitor_views"} for a in n.names))]
    if _dump(restored) != _dump(base):
        raise AssertionError("full module reconstruction failed")
    return base_source(path)


def base_source(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode("utf-8")


def shim_source(legacy, canonical):
    parent, name = canonical[:-3].replace("/", ".").rsplit(".", 1)
    if Path(legacy).stem != name:
        raise AssertionError("registered basename mismatch")
    return ("import sys as _sys\n"
            f"from {parent} import {name} as _canonical\n"
            "_sys.modules[__name__] = _canonical\n")


def strict_shim(source, legacy, canonical):
    if WHOLE_MOVES.get(legacy) != canonical:
        raise AssertionError("unregistered Monitor pair")
    try:
        body = ast.parse(source).body
    except SyntaxError as exc:
        raise AssertionError("invalid shim syntax") from exc
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    expected = ast.parse(shim_source(legacy, canonical)).body
    dump = lambda seq: ast.dump(ast.Module(body=seq, type_ignores=[]), include_attributes=False)
    if dump(body) != dump(expected):
        raise AssertionError("Monitor shim differs from exact three-statement contract")
    return canonical


def verified_current_source(path, *, source=None, owners=None):
    """Return baseline-equivalent implementation source, never import a shim.

    Own-role retained-source tests may follow these exact registered transfers,
    but still check all body bytes. Any extra shim statement or changed canonical
    body fails closed. All other paths remain completely byte-protected.
    """
    current = source if source is not None else (ROOT / path).read_text(encoding="utf-8")
    if path in BODY_MOVES:
        target = BODY_MOVES[path]["owner"]
        actual = owners[target] if owners is not None and target in owners else (ROOT / target).read_text(encoding="utf-8")
        return verify_body_transfer(path, current, actual)
    if path in WHOLE_MOVES:
        target = strict_shim(current, path, WHOLE_MOVES[path])
        actual = owners[target] if owners is not None and target in owners else (ROOT / target).read_text(encoding="utf-8")
    else:
        actual = current
    if actual != base_source(path):
        raise AssertionError(f"BASE implementation changed: {path}")
    return actual
