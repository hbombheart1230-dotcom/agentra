"""P1.5.3 first pass (Fast Track Wave A / A2): moved Operator UI / Brief / period-summary / visibility bodies.

Ledger: docs/refactor/p1_5_3_operator_ui_moved_bodies_ledger.json (module, name, owner, pinned baseline SHA).
For every moved symbol:
1. the original module keeps the top-level ``def`` with an AST-identical signature/returns/decorators;
2. the Owner body equals the pinned baseline body once each ``facade.NAME`` qualification is stripped;
3. qualified names are exactly the former module globals; the Owner has no unresolved global but builtins;
4. use-time resolution: with every module-level callable stubbed, before-call and mid-call re-patching
   produce the same stub-call sequence/outcome as the pinned baseline function run against the live module;
5. Owner <= 350 LOC and imports neither the original module nor its package facade.
Names of module-level defs/classes in the three modules may not disappear (ABI).
"""
import ast
import builtins
import importlib
import inspect
import json
import subprocess
import symtable
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/refactor/p1_5_3_operator_ui_moved_bodies_ledger.json"
DOC = json.loads(LEDGER.read_text(encoding="utf-8"))
BASE = DOC["baseline_sha"]
MOVES = [(m["module"], m["name"], m["owner"]) for m in DOC["moves"]]
MODULES = sorted({m for m, _, _ in MOVES})
BUILTINS = set(dir(builtins))
FORBIDDEN = ("data_access_core", "operator_period_summary", "operator_visibility", "apps.operator_ui.data_access")


def _base_source(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode("utf-8-sig")


def _func(tree, name):
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def _bound(tree):
    s = set()
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            s.add(n.name)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                s.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            for t in ast.walk(n):
                if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store):
                    s.add(t.id)
    return s


def _globals(src, fname):
    tb = symtable.symtable(src, "<p153>", "exec")
    top = next(c for c in tb.get_children() if c.get_name() == fname and c.get_type() == "function")
    out = set()

    def walk(t):
        for sy in t.get_symbols():
            if sy.is_global() and sy.is_referenced():
                out.add(sy.get_name())
        for c in t.get_children():
            walk(c)

    walk(top)
    return out


def _is_fa(node):
    return (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "facade"
            and isinstance(node.ctx, ast.Load))


class _Un(ast.NodeTransformer):
    def __init__(self):
        self.names = set()

    def visit_Attribute(self, node):
        self.generic_visit(node)
        if _is_fa(node):
            self.names.add(node.attr)
            return ast.copy_location(ast.Name(id=node.attr, ctx=ast.Load()), node)
        return node


def _modname(path):
    return path[:-3].replace("/", ".")


def test_ledger_shape():
    assert len(MOVES) == len(set((m, n) for m, n, _ in MOVES)) >= 100
    assert set(MODULES) == {"apps/operator_ui/data_access_core.py", "libs/reporting/operator_period_summary.py",
                            "libs/reporting/operator_visibility.py"}


@pytest.mark.parametrize("path", MODULES)
def test_module_public_declarations_unchanged(path):
    before = ast.parse(_base_source(path))
    after = ast.parse((ROOT / path).read_text(encoding="utf-8-sig"))
    decl = lambda t: {n.name: n for n in t.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    b, a = decl(before), decl(after)
    assert b.keys() == a.keys(), (path, sorted(set(b) ^ set(a)))
    for name, node in b.items():
        cur = a[name]
        assert type(node) is type(cur)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for key in ("args", "returns"):
                l, r = getattr(node, key), getattr(cur, key)
                assert (ast.dump(l) if l else None) == (ast.dump(r) if r else None), (path, name, key)
            assert [ast.dump(d) for d in node.decorator_list] == [ast.dump(d) for d in cur.decorator_list]
    module = importlib.import_module(_modname(path))
    assert all(callable(getattr(module, n, None)) for n in b)


@pytest.mark.parametrize("path,name,owner", MOVES)
def test_use_site_qualification_is_the_only_body_change(path, name, owner):
    base_src = _base_source(path)
    base_tree = ast.parse(base_src)
    base_fn = _func(base_tree, name)
    owner_src = (ROOT / owner).read_text(encoding="utf-8")
    impl = _func(ast.parse(owner_src), f"{name}_r3_impl")
    for n in impl.body:
        assert not (isinstance(n, ast.Assign) and _is_fa(n.value)), (path, name, "entry-time capture")
    un = _Un()
    restored = [un.visit(n) for n in impl.body]
    assert [ast.dump(n) for n in restored] == [ast.dump(n) for n in base_fn.body], (path, name)
    expected = {g for g in _globals(base_src, name) if g in _bound(base_tree)}
    assert un.names == expected, (path, name, sorted(un.names ^ expected))
    assert not {g for g in _globals(owner_src, impl.name) if g not in BUILTINS}, (path, name)
    b, a = base_fn.args, impl.args
    assert [x.arg for x in b.posonlyargs] == [x.arg for x in a.posonlyargs]
    assert [x.arg for x in b.args] == [x.arg for x in a.args]
    assert [x.arg for x in b.kwonlyargs] + ["facade"] == [x.arg for x in a.kwonlyargs]
    assert (b.vararg and b.vararg.arg) == (a.vararg and a.vararg.arg)
    assert (b.kwarg and b.kwarg.arg) == (a.kwarg and a.kwarg.arg)


@pytest.mark.parametrize("owner", sorted({o for _, _, o in MOVES}))
def test_owner_bounded_and_never_imports_original_module(owner):
    src = (ROOT / owner).read_text(encoding="utf-8")
    assert len(src.splitlines()) <= 350, owner
    for n in ast.walk(ast.parse(src)):
        mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module or ""] if isinstance(n, ast.ImportFrom) else [])
        assert all(not any(f in m for f in FORBIDDEN) for m in mods), (owner, mods)


class _Stop(Exception):
    pass


@pytest.mark.parametrize("path,name,owner", MOVES)
def test_wrapper_injects_its_own_module(path, name, owner, monkeypatch):
    module = importlib.import_module(_modname(path))
    base_fn = _func(ast.parse(_base_source(path)), name)
    seen = {}

    def spy(*a, **k):
        seen.update(k)
        raise _Stop()

    monkeypatch.setattr(module, f"{name}_r3_impl", spy)
    a = base_fn.args
    with pytest.raises(_Stop):
        getattr(module, name)(*([None] * (len(a.posonlyargs) + len(a.args))), **{x.arg: None for x in a.kwonlyargs})
    assert seen["facade"] is module


def _reference(path, name, module):
    src = _base_source(path)
    seg = ast.get_source_segment(src, _func(ast.parse(src), name))
    ns = dict(module.__dict__)
    exec(compile("from __future__ import annotations" + chr(10) + seg, "<p153-base-%s>" % name, "exec"), ns)
    f = ns[name]
    ref = types.FunctionType(f.__code__, module.__dict__, name, f.__defaults__, f.__closure__)
    ref.__kwdefaults__ = f.__kwdefaults__
    return ref


def _run(fn, req, kwreq, mk, targets, module, scenario):
    originals = {n: getattr(module, n) for n in targets}
    events, state = [], {"sw": False}

    def make(n, ver):
        def stub(*a, **k):
            events.append((ver, n))
            if scenario == "within_call" and ver == "v1" and not state["sw"]:
                state["sw"] = True
                for m in targets:
                    setattr(module, m, make(m, "v2"))
            return MagicMock()
        return stub

    for n in targets:
        setattr(module, n, make(n, "v1"))
    outcome = "ok"
    try:
        try:
            fn(*[mk() for _ in req], **{p.name: mk() for p in kwreq})
        except Exception as exc:  # noqa
            outcome = "EXC:" + type(exc).__name__
    finally:
        for n, v in originals.items():
            setattr(module, n, v)
    return outcome, events


@pytest.mark.parametrize("path,name,owner", MOVES)
@pytest.mark.parametrize("shape", ["empty_dict", "mock", "text"])
def test_use_time_resolution_matches_baseline_before_and_within_call(path, name, owner, shape, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # any accidental relative write lands in the session tmp dir
    module = importlib.import_module(_modname(path))
    fn = getattr(module, name)
    ref = _reference(path, name, module)
    sig = inspect.signature(fn)
    req = [p for p in sig.parameters.values()
           if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    kwreq = [p for p in sig.parameters.values() if p.default is p.empty and p.kind == p.KEYWORD_ONLY]
    src = _base_source(path)
    bound = _bound(ast.parse(src))
    targets = [g for g in sorted(_globals(src, name)) if g in bound and g != name and callable(getattr(module, g, None))
               and not inspect.ismodule(getattr(module, g)) and not isinstance(getattr(module, g), type)]
    mk = {"empty_dict": dict, "mock": MagicMock, "text": lambda: "abc"}[shape]
    for scenario in ("pre_call", "within_call"):
        got = _run(fn, req, kwreq, mk, targets, module, scenario)
        want = _run(ref, req, kwreq, mk, targets, module, scenario)
        assert got == want, (name, scenario, got[1][:6], want[1][:6])
