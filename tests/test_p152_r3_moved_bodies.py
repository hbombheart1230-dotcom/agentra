"""P1.5.2 R3: moved implementation bodies keep the pinned façade contract AND use-time global resolution.

Contract (names/signatures/decorators of the 436 façade callables) is pinned separately by
test_p152_facade_abi_and_authority_boundary.py. This file verifies the *implementation location*:
every ledger symbol with ``r3_owner`` must

1. equal the pinned R3-baseline body once each ``facade.NAME`` qualification is stripped back to
   ``NAME`` (so the only edit is explicit use-site qualification of former façade globals),
2. qualify exactly the former façade globals (no more, no fewer) and have no entry-time capture,
3. leave no unresolved global other than builtins,
4. resolve façade globals lazily at each use (patch before the call and from a callback within the
   call behave like the original module-level lookup),
5. stay a bounded Owner (<=350 LOC) that never imports a façade.
"""
import ast
import builtins
import importlib
import inspect
import json
import subprocess
import symtable
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "ba6618d483e6d617f4ee56b2cb5647392c777071"
LEDGER = ROOT / "docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json"
BUILTINS = set(dir(builtins))
FORBIDDEN_IMPORT = ("trade_report_ai", "trade_report_markdown_clean", "trade_story_pipeline")


def _moved():
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    return [(f["path"], s["name"], s["r3_owner"]) for f in doc["files"] for s in f["symbols"] if s.get("r3_owner")]


MOVED = _moved()


def _base_source(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode("utf-8-sig")


def _func(tree, name):
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


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


def _is_facade_attr(node):
    return (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "facade"
            and isinstance(node.ctx, ast.Load))


class _Unqualify(ast.NodeTransformer):
    def visit_Attribute(self, node):
        self.generic_visit(node)
        if _is_facade_attr(node):
            self.names.add(node.attr)
            return ast.copy_location(ast.Name(id=node.attr, ctx=ast.Load()), node)
        return node

    def __init__(self):
        self.names = set()


def test_expected_r3_moves_present():
    assert len(MOVED) == 57, "ledger must record the 57 R3 moved implementation bodies"


@pytest.mark.parametrize("path,name,owner", MOVED)
def test_use_site_qualification_is_the_only_body_change(path, name, owner):
    base_src = _base_source(path)
    base_tree = ast.parse(base_src)
    base_fn = _func(base_tree, name)
    owner_src = (ROOT / owner).read_text(encoding="utf-8")
    impl = _func(ast.parse(owner_src), f"{name}_r3_impl")

    # no entry-time capture prelude: `x = facade.x` as a top-level statement is forbidden
    for n in impl.body:
        assert not (isinstance(n, ast.Assign) and _is_facade_attr(n.value)), (path, name, "entry-time capture")

    # (1) strip the explicit qualification -> pinned baseline body
    un = _Unqualify()
    restored = [un.visit(n) for n in impl.body]
    assert [ast.dump(n) for n in restored] == [ast.dump(n) for n in base_fn.body], (path, name)

    # (2) qualified names == exactly the former façade globals
    expected = {g for g in _global_refs(base_src, name) if g in _module_bound_names(base_tree)}
    assert un.names == expected, (path, name, sorted(un.names ^ expected))

    # (3) every other Name `facade` use is forbidden; owner has no unresolved global but builtins
    bare = [n for n in ast.walk(impl) if isinstance(n, ast.Name) and n.id == "facade" and isinstance(n.ctx, ast.Load)]
    assert len(bare) == len([n for n in ast.walk(impl) if _is_facade_attr(n)]), (path, name, "bare facade use")
    unresolved = {g for g in _global_refs(owner_src, impl.name) if g not in BUILTINS}
    assert not unresolved, (path, name, unresolved)

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


class _Stop(Exception):
    pass


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
        seen["kwargs"] = kwargs
        raise _Stop()

    monkeypatch.setattr(module, f"{name}_r3_impl", spy)
    a = base_fn.args
    with pytest.raises(_Stop):
        getattr(module, name)(*([None] * (len(a.posonlyargs) + len(a.args))), **{x.arg: None for x in a.kwonlyargs})
    assert seen["kwargs"]["facade"] is sys.modules[module.__name__]


_SWITCHED = {"functions_with_v2": 0, "cases": 0}


def _facade_free_names(path, name):
    tree = _module_bound_names(ast.parse(_base_source(path)))
    return sorted(g for g in _global_refs(_base_source(path), name) if g in tree)


@pytest.mark.parametrize("path,name,owner", MOVED)
@pytest.mark.parametrize("shape", ["empty_dict", "mock", "text"])
def test_lazy_use_time_lookup_before_and_within_call(path, name, owner, shape):
    """Before the call every stub is used; when a callback re-patches ALL façade globals mid-call,
    every later use must hit the new binding (original module-level late lookup)."""
    _SWITCHED["cases"] += 1
    module = importlib.import_module(path[:-3].replace("/", "."))
    fn = getattr(module, name)
    sig = inspect.signature(fn)
    req = [p for p in sig.parameters.values()
           if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    kwreq = [p for p in sig.parameters.values() if p.default is p.empty and p.kind == p.KEYWORD_ONLY]
    targets = [n for n in _facade_free_names(path, name)
               if n != name and callable(getattr(module, n, None)) and not inspect.ismodule(getattr(module, n))
               and not isinstance(getattr(module, n), type)]
    mk = {"empty_dict": dict, "mock": MagicMock, "text": lambda: "abc"}[shape]
    for scenario in ("pre_call", "within_call"):
        originals = {n: getattr(module, n) for n in targets}
        events, state = [], {"switched": False}

        def make(n, ver):
            def stub(*a, **k):
                events.append((ver, n))
                if scenario == "within_call" and ver == "v1" and not state["switched"]:
                    state["switched"] = True
                    for m in targets:
                        setattr(module, m, make(m, "v2"))
                return MagicMock()
            return stub

        for n in targets:
            setattr(module, n, make(n, "v1"))
        try:
            try:
                fn(*[mk() for _ in req], **{p.name: mk() for p in kwreq})
            except Exception:
                pass
        finally:
            for n, v in originals.items():
                setattr(module, n, v)
        if scenario == "pre_call":
            assert all(v == "v1" for v, _ in events), (name, events)
        else:
            assert all(v == "v2" for v, _ in events[1:]), (name, events[:8])
            if any(v == "v2" for v, _ in events):
                _SWITCHED["functions_with_v2"] += 1


def test_lazy_lookup_was_actually_exercised():
    # runs after the parametrised cases (file order); guards against a vacuous pass
    if _SWITCHED["cases"] < len(MOVED) * 3:
        pytest.skip("lazy-lookup cases were deselected")
    assert _SWITCHED["functions_with_v2"] >= 36
