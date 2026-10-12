"""P1.5.2 R3: moved implementation bodies keep the pinned façade contract and call-time seams.

Contract (names/signatures/decorators of the 436 façade callables) is pinned separately by
test_p152_facade_abi_and_authority_boundary.py. This file verifies the *implementation
location*: every ledger symbol with ``r3_owner`` must (1) keep an AST-identical body from the
pinned R3 baseline, (2) resolve every former façade global through the injected ``facade``
object at call entry, (3) have no unresolved global, and (4) stay a bounded Owner that never
imports a façade.
"""
import ast
import builtins
import importlib
import json
import subprocess
import symtable
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "ba6618d483e6d617f4ee56b2cb5647392c777071"
LEDGER = ROOT / "docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json"
BUILTINS = set(dir(builtins))
FORBIDDEN_IMPORT = ("trade_report_ai", "trade_report_markdown_clean", "trade_story_pipeline")


def _moved():
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    rows = []
    for f in doc["files"]:
        for s in f["symbols"]:
            if s.get("r3_owner"):
                rows.append((f["path"], s["name"], s["r3_owner"]))
    return rows


MOVED = _moved()


def _base_source(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode("utf-8-sig")


def _func(tree, name):
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def _is_prelude(node):
    return (
        isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "facade" and node.value.attr == node.targets[0].id
    )


def _module_bound_names(tree):
    names = set()
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(n.name)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                names.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            for t in ast.walk(n):
                if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store):
                    names.add(t.id)
    return names


def _global_refs(src, func_name):
    table = symtable.symtable(src, "<r3>", "exec")
    top = next(c for c in table.get_children() if c.get_name() == func_name and c.get_type() == "function")
    refs = set()

    def walk(tb):
        for s in tb.get_symbols():
            if s.is_global() and s.is_referenced():
                refs.add(s.get_name())
        for c in tb.get_children():
            walk(c)

    walk(top)
    return refs


def test_expected_r3_moves_present():
    assert len(MOVED) >= 3, "ledger must record R3 moved implementation bodies"


@pytest.mark.parametrize("path,name,owner", MOVED)
def test_body_ast_prelude_and_no_unbound_globals(path, name, owner):
    base_src = _base_source(path)
    base_tree = ast.parse(base_src)
    base_fn = _func(base_tree, name)
    owner_src = (ROOT / owner).read_text(encoding="utf-8")
    owner_tree = ast.parse(owner_src)
    impl = _func(owner_tree, f"{name}_r3_impl")

    # (1) body identical modulo the explicit `x = facade.x` prelude
    impl_body = [n for n in impl.body if not _is_prelude(n)]
    assert [ast.dump(n) for n in impl_body] == [ast.dump(n) for n in base_fn.body], (path, name)

    # (2) prelude == exactly the former façade globals
    prelude = [n.targets[0].id for n in impl.body if _is_prelude(n)]
    expected = sorted(g for g in _global_refs(base_src, name) if g in _module_bound_names(base_tree))
    assert prelude == expected, (path, name)

    # (3) owner function has no global other than builtins
    unresolved = {g for g in _global_refs(owner_src, impl.name) if g not in BUILTINS}
    assert not unresolved, (path, name, unresolved)

    # signature: same parameter names/kinds (annotations/defaults live on the façade), plus kw-only `facade`
    b, a = base_fn.args, impl.args
    assert [x.arg for x in b.posonlyargs] == [x.arg for x in a.posonlyargs]
    assert [x.arg for x in b.args] == [x.arg for x in a.args]
    assert [x.arg for x in b.kwonlyargs] + ["facade"] == [x.arg for x in a.kwonlyargs]
    assert (b.vararg and b.vararg.arg) == (a.vararg and a.vararg.arg)
    assert (b.kwarg and b.kwarg.arg) == (a.kwarg and a.kwarg.arg)


@pytest.mark.parametrize("owner", sorted({o for _, _, o in MOVED}))
def test_owner_is_bounded_and_never_imports_a_facade(owner):
    src = (ROOT / owner).read_text(encoding="utf-8")
    assert len(src.splitlines()) <= 350
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Import):
            mods = [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            mods = [n.module or ""]
        else:
            continue
        assert all(not any(f in m for f in FORBIDDEN_IMPORT) for m in mods), (owner, mods)


@pytest.mark.parametrize("path,name,owner", MOVED)
def test_facade_wrapper_keeps_contract_and_injects_its_own_module(path, name, owner, monkeypatch):
    base_fn = _func(ast.parse(_base_source(path)), name)
    cur_fn = _func(ast.parse((ROOT / path).read_text(encoding="utf-8-sig")), name)
    for key in ("args", "returns"):
        assert ast.dump(getattr(base_fn, key)) == ast.dump(getattr(cur_fn, key)), (path, name, key)
    assert [ast.dump(d) for d in base_fn.decorator_list] == [ast.dump(d) for d in cur_fn.decorator_list]

    module = importlib.import_module(path[:-3].replace("/", "."))
    seen = {}

    def spy(*args, **kwargs):
        seen["args"], seen["kwargs"] = args, kwargs
        raise _Stop()

    monkeypatch.setattr(module, f"{name}_r3_impl", spy)
    a = base_fn.args
    call_args = [None] * (len(a.posonlyargs) + len(a.args))
    call_kwargs = {x.arg: None for x in a.kwonlyargs}
    with pytest.raises(_Stop):
        getattr(module, name)(*call_args, **call_kwargs)
    assert seen["kwargs"]["facade"] is sys.modules[module.__name__]


class _Stop(Exception):
    pass


class _Recorder:
    def __init__(self):
        self.requested = []

    def __getattr__(self, item):
        self.requested.append(item)
        return lambda *a, **k: (_ for _ in ()).throw(_Stop())


@pytest.mark.parametrize("path,name,owner", MOVED)
def test_owner_reads_former_globals_from_injected_facade_at_entry(path, name, owner):
    owner_mod = importlib.import_module(owner[:-3].replace("/", "."))
    impl = getattr(owner_mod, f"{name}_r3_impl")
    tree = ast.parse((ROOT / owner).read_text(encoding="utf-8"))
    fn = _func(tree, impl.__name__)
    prelude = [n.targets[0].id for n in fn.body if _is_prelude(n)]
    a = fn.args
    n_pos = len(a.posonlyargs) + len(a.args)
    rec = _Recorder()
    try:
        impl(*([None] * n_pos), **{x.arg: None for x in a.kwonlyargs if x.arg != "facade"}, facade=rec)
    except Exception:
        pass  # body may fail on None inputs; the prelude has already run
    assert rec.requested[: len(prelude)] == prelude
