"""T4-A structural gates for `graphs/nodes/scanner_node.py::scanner_node`.

Proven without running production code, against the IMMUTABLE BASE `11a11df`:
* inlining every Owner call (statement-run windows and value builders; `facade.NAME` -> `NAME`, injected `facade` ->
  `_r3_sys.modules[__name__]`) reproduces the BASE `scanner_node` AST exactly (signature, evaluation order, State writes,
  event/log/trace calls, control flow);
* every other top-level definition of the node module is AST-identical to BASE;
* Owners: <= 350 lines, no I/O/env/clock tokens, no unresolved globals (builtins, `facade` and own definitions only),
  imports only `__future__`/`typing`, one canonical ranking implementation (no duplicate rank/tie-break code);
* changed paths stay inside the Scanner scope and touch no authority surface.
"""
import ast
import builtins
import copy
import importlib
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "11a11df58f8d846cd9824fcb37eced521a57e887"
NODE = "graphs/nodes/scanner_node.py"
FUNC = "scanner_node"
LEDGER = ROOT / "docs/refactor/p1_5_third_pass_t4a_moved_segments_ledger.json"
T4A_END_SHA = "c338ba34276566b0b5f6de1e7f556778ec917968"
MAX_OWNER_LOC = 350
FORBIDDEN_TOKENS = ("os.environ", "os.getenv", "getenv(", "time.time(", "datetime.now", "datetime.utcnow", "uuid.uuid",
                    "subprocess", "sqlite3", "requests.", "print(", "open(", "logging.", "random.")
FORBIDDEN_PREFIXES = ("libs/execution/", "libs/broker/", "libs/supervisor/", "libs/risk/", "libs/llm/", "libs/executor/",
                      "graphs/nodes/execute_from_packet.py", "graphs/nodes/decide_trade.py",
                      "graphs/nodes/update_state_after_execution.py", "libs/runtime/controlled_mock_lanes/")
ALLOWED_CHANGED = ("graphs/nodes/scanner_node.py", "libs/runtime/scanner/", "tests/", "docs/", "scripts/refactor/",
                   ".github/workflows/", "CLAUDE.md", "AGENTS.md")


def _ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _base_tree():
    return ast.parse(subprocess.check_output(["git", "show", f"{BASE}:{NODE}"], cwd=ROOT).decode("utf-8-sig"))


def _cur_tree():
    return ast.parse((ROOT / NODE).read_text(encoding="utf-8-sig"))


def _funcs(tree):
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _sys_modules_name():
    return ast.parse("_r3_sys.modules[__name__]", mode="eval").body


class _Unqualify(ast.NodeTransformer):
    """facade.NAME -> NAME ; bare facade -> _r3_sys.modules[__name__]."""

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == "facade" and isinstance(node.ctx, ast.Load):
            return ast.copy_location(ast.Name(id=node.attr, ctx=ast.Load()), node)
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if node.id == "facade" and isinstance(node.ctx, ast.Load):
            return ast.copy_location(_sys_modules_name(), node)
        return node


def _owner_fn(seg):
    return _funcs(ast.parse((ROOT / seg["owner"]).read_text(encoding="utf-8-sig")))[seg["owner_function"]]


def _call_name(call):
    return call.func.id if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) else None


def _run_body(owner_fn):
    body = copy.deepcopy(owner_fn.body)
    assert isinstance(body[-1], ast.Return)
    return [_Unqualify().visit(s) for s in body[:-1]]


class _Reconstruct(ast.NodeTransformer):
    def __init__(self, runs, builders):
        self.runs, self.builders, self.used = runs, builders, set()

    def _stage_name(self, stmt):
        v = getattr(stmt, "value", None)
        name = _call_name(v)
        return name if name in self.runs else None

    def generic_visit(self, node):
        for field, old in ast.iter_fields(node):
            if isinstance(old, list) and old and all(isinstance(x, ast.stmt) for x in old):
                new = []
                for stmt in old:
                    name = self._stage_name(stmt) if isinstance(stmt, (ast.Assign, ast.Expr)) else None
                    if name:
                        self.used.add(name)
                        new.extend(self.visit(b) for b in _run_body(self.runs[name]))
                    else:
                        r = self.visit(stmt)
                        new.extend(r if isinstance(r, list) else [r])
                setattr(node, field, new)
            elif isinstance(old, list):
                setattr(node, field, [self.visit(x) if isinstance(x, ast.AST) else x for x in old])
            elif isinstance(old, ast.AST):
                setattr(node, field, self.visit(old))
        return node

    def visit_Call(self, node):
        name = _call_name(node)
        if name in self.builders:
            self.used.add(name)
            ret = self.builders[name].body[-1]
            assert isinstance(ret, ast.Return)
            return self.visit(_Unqualify().visit(copy.deepcopy(ret.value)))
        self.generic_visit(node)
        return node


def _stage_maps():
    runs, builders = {}, {}
    for seg in _ledger()["segments"]:
        (runs if seg["kind"] == "run" else builders)[seg["owner_function"]] = _owner_fn(seg)
    return runs, builders


def test_inlining_every_owner_reproduces_the_base_scanner_node_ast_exactly():
    base = _funcs(_base_tree())[FUNC]
    cur = copy.deepcopy(_funcs(_cur_tree())[FUNC])
    runs, builders = _stage_maps()
    rec = _Reconstruct(runs, builders)
    rec.visit(cur)
    assert rec.used == set(runs) | set(builders), "every ledger stage must be called from scanner_node"
    assert ast.dump(cur.args) == ast.dump(base.args)
    assert [ast.dump(s) for s in cur.body] == [ast.dump(s) for s in base.body]


def test_non_moved_node_definitions_are_ast_identical_to_base():
    base_t, cur_t = _base_tree(), _cur_tree()
    base, cur = _funcs(base_t), _funcs(cur_t)
    assert set(base) == set(cur)
    for name, fn in base.items():
        if name == FUNC:
            continue
        assert ast.dump(fn) == ast.dump(cur[name]), name
    # non-function top-level statements (imports excluded) unchanged
    keep = lambda t: [ast.dump(n) for n in t.body if not isinstance(n, (ast.FunctionDef, ast.Import, ast.ImportFrom))]  # noqa: E731
    assert keep(base_t) == keep(cur_t)


def test_new_import_lines_are_only_the_ledger_owner_names():
    base_names = {(n.module, a.name) for n in _base_tree().body if isinstance(n, ast.ImportFrom) for a in n.names}
    cur_names = {(n.module, a.name) for n in _cur_tree().body if isinstance(n, ast.ImportFrom) for a in n.names}
    added = cur_names - base_names
    expected = {(s["owner"][:-3].replace("/", "."), s["owner_function"]) for s in _ledger()["segments"]}
    assert added == expected and base_names <= cur_names


def test_owner_modules_are_small_pure_and_resolve_only_allowed_names():
    mods = sorted({s["owner"] for s in _ledger()["segments"]})
    assert len(mods) >= 4
    for rel in mods:
        text = (ROOT / rel).read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= MAX_OWNER_LOC, rel
        for tok in FORBIDDEN_TOKENS:
            assert tok not in text, (rel, tok)
        tree = ast.parse(text)
        known = set(dir(builtins)) | {"facade"}
        for n in tree.body:
            if isinstance(n, ast.Import):
                raise AssertionError(f"{rel}: plain import")
            if isinstance(n, ast.ImportFrom):
                assert n.module in ("__future__", "typing"), (rel, n.module)
                known |= {a.asname or a.name for a in n.names}
            elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
                known.add(n.name)
        for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
            bound = {a.arg for a in fn.args.args + fn.args.kwonlyargs}
            for n in ast.walk(fn):
                if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
                    bound.add(n.id)
                elif isinstance(n, ast.arg):
                    bound.add(n.arg)
                elif isinstance(n, ast.ExceptHandler) and n.name:
                    bound.add(n.name)
            for n in ast.walk(fn):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    assert n.id in bound or n.id in known, (rel, fn.name, n.id)
        importlib.import_module(rel[:-3].replace("/", "."))


def test_scanner_node_is_substantially_smaller_and_no_second_ranking_implementation():
    base, cur = _funcs(_base_tree())[FUNC], _funcs(_cur_tree())[FUNC]
    base_loc, cur_loc = base.end_lineno - base.lineno + 1, cur.end_lineno - cur.lineno + 1
    assert base_loc >= 1200 and cur_loc <= base_loc * 0.45, (base_loc, cur_loc)
    # one canonical sort: the ranking sort (`sorted(scan_results, ...)`) and its overlay re-sorts exist exactly where they
    # existed at BASE (inlined AST equality above) and nowhere else in the new Owners
    for seg in {s["owner"] for s in _ledger()["segments"]}:
        text = (ROOT / seg).read_text(encoding="utf-8-sig")
        assert text.count("sorted(scan_results") == 0, seg


def test_result_records_keep_sorted_output_order_and_are_tuples():
    for seg in _ledger()["segments"]:
        if not seg.get("record"):
            continue
        mod = importlib.import_module(seg["owner"][:-3].replace("/", "."))
        rec = getattr(mod, seg["record"])
        assert issubclass(rec, tuple) and list(rec._fields) == seg["outputs"]
        values = tuple(range(len(seg["outputs"])))
        assert rec(*values) == values and tuple(rec(*values)) == values


def test_call_sites_pass_exactly_the_declared_inputs():
    cur = _funcs(_cur_tree())[FUNC]
    for seg in _ledger()["segments"]:
        owner = _owner_fn(seg)
        params = [a.arg for a in owner.args.args]
        kwonly = [a.arg for a in owner.args.kwonlyargs]
        calls = [n for n in ast.walk(cur) if isinstance(n, ast.Call) and _call_name(n) == seg["owner_function"]]
        assert len(calls) == 1, seg["owner_function"]
        assert [k.arg for k in calls[0].keywords] == params + kwonly, seg["owner_function"]
        if kwonly:
            assert kwonly == ["facade"] and ast.unparse(calls[0].keywords[-1].value) == "_r3_sys.modules[__name__]"


def test_t4a_changed_paths_stay_in_scanner_scope_and_touch_no_authority_surface():
    # stage-pinned: T4-A scope is evaluated up to the T4-A.1 closing commit (T4-B legitimately touches the Monitor scope)
    assert subprocess.run(["git", "merge-base", "--is-ancestor", T4A_END_SHA, "HEAD"], cwd=ROOT).returncode == 0
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", BASE, T4A_END_SHA], cwd=ROOT).decode().split(chr(0))
    for p in [x for x in out if x]:
        assert p.startswith(ALLOWED_CHANGED), f"T4-A touched an out-of-scope path: {p}"
        assert not p.startswith(FORBIDDEN_PREFIXES), p
        assert not p.startswith("tests/fixtures/p1_5_t35_agent_outputs/"), "T3.5 golden fixtures must stay unchanged"
