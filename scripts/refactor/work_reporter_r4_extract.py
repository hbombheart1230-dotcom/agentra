"""Reporter R-4+: move facade function bodies into Reporter owners with the proven P1.5.2 R3 late-binding pattern.

  python work_reporter_r4_extract.py <facade.py> <owner_dir> <owner_stem> <ledger.json> [--min-lines N] [--exclude a,b]

For every eligible top-level function F of the facade (read from the CURRENT tree, which must equal the pinned runtime
BASE for that function):
  * owner  ``def F_r4_impl(<same parameter names, no defaults>, *, facade)``: body identical to F except that every
    reference to a former facade module global is qualified at its use site as ``facade.NAME`` (no entry-time capture,
    no getattr fallback, owner never imports the facade);
  * facade ``def F(<unchanged signature/decorators/returns>): return F_r4_impl(..., facade=_r3_sys.modules[__name__])``.
Ineligible (left untouched, reason recorded): decorators, async, ``global``/``nonlocal``, nested scopes shadowing a facade
global, existing thin delegations, functions whose source mentions an effect/authority token, bodies shorter than N lines.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import symtable
from pathlib import Path

EFFECT_TOKENS = re.compile(
    r"\b(open|write_text|read_text|write_bytes|mkdir|unlink|rename|replace_file|json\.dump|Path|os\.|subprocess|requests|"
    r"httpx|socket|time\.|sleep|datetime\.now|utcnow|logging|logger|print|llm|LLM|openai|anthropic|client|retry|"
    r"timeout|queue|lock|Lock|thread|asyncio|broker|kiwoom|order_|submit|execute|truth|precedence|environ|getenv)\b")
OWNER_MAX = 330


def module_bound_names(tree):
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


def scope_info(src, name):
    table = symtable.symtable(src, "<r4>", "exec")
    top = next(c for c in table.get_children() if c.get_name() == name and c.get_type() == "function")
    refs, child_locals = set(), set()

    def walk(tb, depth):
        for s in tb.get_symbols():
            if s.is_global() and s.is_referenced():
                refs.add(s.get_name())
            if depth > 0 and (s.is_local() or s.is_parameter()):
                child_locals.add(s.get_name())
            if s.is_declared_global() or s.is_nonlocal():
                raise ValueError("global/nonlocal")
        for c in tb.get_children():
            walk(c, depth + 1)

    walk(top, 0)
    return refs, child_locals


class Qualify(ast.NodeTransformer):
    def __init__(self, names):
        self.names = names

    def visit_Name(self, node):
        if node.id in self.names and isinstance(node.ctx, ast.Load):
            return ast.copy_location(ast.Attribute(value=ast.Name(id="facade", ctx=ast.Load()), attr=node.id, ctx=ast.Load()), node)
        return node


def is_thin_delegation(fn):
    body = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
    return len(body) == 1 and isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Call)


def impl_args(a):
    def strip(x):
        return ast.arg(arg=x.arg, annotation=None)
    return ast.arguments(posonlyargs=[strip(x) for x in a.posonlyargs], args=[strip(x) for x in a.args],
                         vararg=strip(a.vararg) if a.vararg else None,
                         kwonlyargs=[strip(x) for x in a.kwonlyargs] + [ast.arg(arg="facade", annotation=None)],
                         kw_defaults=[None] * (len(a.kwonlyargs) + 1), kwarg=strip(a.kwarg) if a.kwarg else None, defaults=[])


def wrapper_call(fn, impl_name):
    a = fn.args
    pos = [ast.Name(id=x.arg, ctx=ast.Load()) for x in a.posonlyargs + a.args]
    if a.vararg:
        pos.append(ast.Starred(value=ast.Name(id=a.vararg.arg, ctx=ast.Load()), ctx=ast.Load()))
    kws = [ast.keyword(arg=x.arg, value=ast.Name(id=x.arg, ctx=ast.Load())) for x in a.kwonlyargs]
    kws.append(ast.keyword(arg="facade", value=ast.Subscript(
        value=ast.Attribute(value=ast.Name(id="_r3_sys", ctx=ast.Load()), attr="modules", ctx=ast.Load()),
        slice=ast.Name(id="__name__", ctx=ast.Load()), ctx=ast.Load())))
    if a.kwarg:
        kws.append(ast.keyword(arg=None, value=ast.Name(id=a.kwarg.arg, ctx=ast.Load())))
    return ast.Return(value=ast.Call(func=ast.Name(id=impl_name, ctx=ast.Load()), args=pos, keywords=kws))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facade")
    ap.add_argument("owner_dir")
    ap.add_argument("owner_stem")
    ap.add_argument("ledger")
    ap.add_argument("--min-lines", type=int, default=6)
    ap.add_argument("--exclude", default="")
    ns = ap.parse_args()
    facade = Path(ns.facade)
    raw = facade.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    src = raw.decode("utf-8-sig")
    crlf = "\r\n" in src
    src = src.replace("\r\n", "\n")
    tree = ast.parse(src)
    bound = module_bound_names(tree)
    lines = src.split("\n")
    excluded = set(filter(None, ns.exclude.split(",")))
    chosen, skipped = [], {}
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        seg = "\n".join(lines[fn.lineno - 1:fn.end_lineno])
        reason = None
        if fn.name in excluded:
            reason = "excluded by caller"
        elif fn.decorator_list:
            reason = "decorated"
        elif is_thin_delegation(fn):
            reason = "already thin delegation"
        elif fn.end_lineno - fn.lineno + 1 < ns.min_lines:
            reason = "short"
        elif EFFECT_TOKENS.search(seg):
            reason = "effect/authority token: " + EFFECT_TOKENS.search(seg).group(0)
        else:
            try:
                refs, child_locals = scope_info(src, fn.name)
            except ValueError as exc:
                reason = str(exc)
            else:
                qualified = {g for g in refs if g in bound}
                if qualified & child_locals:
                    reason = "nested scope shadows facade global: " + ",".join(sorted(qualified & child_locals))
        if reason:
            skipped[fn.name] = reason
        else:
            chosen.append(fn)
    owner_dir = Path(ns.owner_dir)
    pkg = owner_dir.as_posix().replace("/", ".")
    # pack into owners <= OWNER_MAX lines
    header = ('"""Behavior-preserving Reporter R-4 implementation bodies moved from ``{facade}``.\n\n'
              "Each function keeps its original body except that every former facade module global is qualified at its use\n"
              "site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup\n"
              'and monkeypatching match the original module-level resolution. This owner never imports the facade.\n"""\n'
              "from __future__ import annotations\n").format(facade=facade.as_posix())
    owners, cur, cur_lines, idx = {}, [], len(header.split("\n")), 1
    moved = []
    for fn in chosen:
        refs, _ = scope_info(src, fn.name)
        q = {g for g in refs if g in bound}
        body = [Qualify(q).visit(ast.parse(ast.unparse(n)).body[0]) for n in fn.body]
        impl = ast.FunctionDef(name=f"{fn.name}_r4_impl", args=impl_args(fn.args), body=body, decorator_list=[], returns=None,
                               type_params=[])
        ast.fix_missing_locations(impl)
        text = ast.unparse(impl)
        n = len(text.split("\n")) + 2
        if cur and cur_lines + n > OWNER_MAX:
            owners[f"{ns.owner_stem}_{idx:02d}"] = cur
            cur, cur_lines, idx = [], len(header.split("\n")), idx + 1
        if n > OWNER_MAX:
            skipped[fn.name] = "body longer than owner budget"
            continue
        cur.append((fn, text))
        cur_lines += n
    if cur:
        owners[f"{ns.owner_stem}_{idx:02d}"] = cur
    owner_dir.mkdir(parents=True, exist_ok=True)
    replace = {}
    for owner, items in owners.items():
        path = owner_dir / f"{owner}.py"
        path.write_text(header + "\n\n" + "\n\n\n".join(t for _, t in items) + "\n", encoding="utf-8", newline="\n")
        for fn, _ in items:
            moved.append({"path": facade.as_posix(), "name": fn.name, "r4_owner": path.as_posix()})
            replace[fn.name] = owner
    # rewrite facade: replace each moved body by the delegating return, keep signature lines verbatim
    out, i = [], 0
    by_start = {fn.lineno: fn for fn in chosen if fn.name in replace}
    while i < len(lines):
        fn = by_start.get(i + 1)
        if fn is None:
            out.append(lines[i])
            i += 1
            continue
        head_end = fn.body[0].lineno - 1
        if isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant) and isinstance(fn.body[0].value.value, str):
            head_end = fn.body[0].end_lineno  # keep the docstring on the facade too (``__doc__`` unchanged)
        head = lines[fn.lineno - 1:head_end]
        if fn.body[0].lineno == fn.lineno:  # one-line def
            raise SystemExit(f"one-line def not supported: {fn.name}")
        out.extend(head)
        indent = " " * (fn.body[0].col_offset)
        out.append(indent + ast.unparse(wrapper_call(fn, f"{fn.name}_r4_impl")))
        i = fn.end_lineno
    imports = []
    for owner, items in owners.items():
        imports.append(f"from {pkg}.{owner} import (  # R-4 owner bodies (facade-injected)")
        imports.extend(f"    {fn.name}_r4_impl," for fn, _ in items)
        imports.append(")")
    text = "\n".join(out)
    if "import sys as _r3_sys" not in text:
        imports.insert(0, "import sys as _r3_sys")
    # insert after the last top-level import statement
    last_import = max(n.end_lineno for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom)))
    shift = 0
    out_lines = text.split("\n")
    # map: lines before the first moved function are unchanged, so last_import index is stable
    assert min(by_start) > last_import, "moved function precedes imports"
    out_lines[last_import:last_import] = imports
    final = "\n".join(out_lines)
    if crlf:
        final = final.replace("\n", "\r\n")
    facade.write_bytes((b"\xef\xbb\xbf" if bom else b"") + final.encode("utf-8"))
    led = Path(ns.ledger)
    doc = json.loads(led.read_text(encoding="utf-8")) if led.exists() else {"schema": "agentra.work.reporter.r4_ledger.v1",
                                                                             "base": "d773709ba2f70471fad9badba4f92400f7818319",
                                                                             "moves": [], "skipped": {}}
    doc["moves"].extend(moved)
    doc["skipped"][facade.as_posix()] = skipped
    led.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"moved {len(moved)} into {len(owners)} owners; skipped {len(skipped)}")


if __name__ == "__main__":
    main()
