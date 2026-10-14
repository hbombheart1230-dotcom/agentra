"""T3.5 structural gates for the agent output builders (`libs/contracts/agent_outputs.py`).

Without executing production code paths these prove, against the IMMUTABLE BASE snapshot (`eb53dc1`):

* inlining every stage call back into its public builder (statement-run stages and dict-item-range stages, with
  `facade.NAME` -> `NAME`) reproduces the BASE builder AST exactly (signature, body, evaluation order, key order);
* moved value helpers are AST-identical to BASE and still exported by the facade under the same names;
* every non-moved top-level definition of the facade is AST-identical to BASE;
* stage modules: <= 350 lines, import only `__future__`, `typing` and the value helpers, no I/O/clock/env tokens,
  no unresolved module globals (only builtins, `facade` and imported helpers);
* result records keep the legacy positional order; changed paths never touch broker/execution/supervisor/LLM authority.
Behavioral (byte) parity is the separate frozen-fixture test `test_p161_agent_output_contract_freeze.py`.
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
BASE = "eb53dc1fe56c2a70a21271faf2f3c25c9711e309"
T35_END_SHA = "11a11df58f8d846cd9824fcb37eced521a57e887"  # accepted T3.5.1 end (= T4-A BASE)
FACADE = "libs/contracts/agent_outputs.py"
LEDGER = ROOT / "docs/refactor/p1_5_third_pass_t35_moved_segments_ledger.json"
BUILDERS = ("build_strategist_output_artifact", "build_scanner_output_artifact", "build_monitor_output_artifact",
            "build_commander_output_artifact")
MAX_OWNER_LOC = 350
ALLOWED_IMPORTS = {"__future__": {"annotations"}, "typing": {"Any", "NamedTuple"},
                   "libs.contracts.agent_output_values": None}  # None = any of the moved value helpers
FORBIDDEN_TOKENS = ("os.environ", "os.getenv", "getenv(", "time.time(", "datetime", "uuid.uuid", "subprocess", "sqlite3",
                    "requests.", "print(", "open(", "logging.", "random.")
FORBIDDEN_PREFIXES = ("libs/execution/", "libs/broker/", "libs/supervisor/", "libs/risk/", "libs/llm/", "libs/executor/",
                      "graphs/nodes/execute_from_packet.py", "graphs/nodes/decide_trade.py",
                      "graphs/nodes/update_state_after_execution.py", "libs/runtime/controlled_mock_lanes/")


def _ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _base_src():
    return subprocess.check_output(["git", "show", f"{BASE}:{FACADE}"], cwd=ROOT).decode("utf-8-sig")


def _tree(path):
    return ast.parse((ROOT / path).read_text(encoding="utf-8-sig"))


def _funcs(tree):
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


class _Unqualify(ast.NodeTransformer):
    def visit_Attribute(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id == "facade" and isinstance(node.ctx, ast.Load):
            return ast.copy_location(ast.Name(id=node.attr, ctx=ast.Load()), node)
        return node


def _owner_fn(seg):
    return _funcs(_tree(seg["owner"]))[seg["owner_function"]]


def _call_name(call):
    return call.func.id if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) else None


def _inline_run(owner_fn):
    body = copy.deepcopy(owner_fn.body)
    ret = body[-1]
    assert isinstance(ret, ast.Return)
    return [_Unqualify().visit(s) for s in body[:-1]], ret.value


class _Reconstruct(ast.NodeTransformer):
    """Splice stage bodies / dict items back into the public builder."""

    def __init__(self, runs, items):
        self.runs, self.items, self.used = runs, items, set()

    def _stage_call(self, stmt):
        v = getattr(stmt, "value", None)
        if isinstance(v, ast.Subscript):  # single-output stages are called as `f(...)[0]`
            v = v.value
        name = _call_name(v)
        return name if name in self.runs else None

    def generic_visit(self, node):
        for field, old in ast.iter_fields(node):
            if isinstance(old, list) and old and all(isinstance(x, ast.stmt) for x in old):
                new = []
                for stmt in old:
                    name = self._stage_call(stmt) if isinstance(stmt, ast.Assign) else None
                    if name:
                        self.used.add(name)
                        body, _ret = _inline_run(self.runs[name])
                        new.extend(self.visit(b) for b in body)
                    else:
                        r = self.visit(stmt)
                        new.extend(r if isinstance(r, list) else [r])
                setattr(node, field, new)
            elif isinstance(old, list):
                setattr(node, field, [self.visit(x) if isinstance(x, ast.AST) else x for x in old])
            elif isinstance(old, ast.AST):
                setattr(node, field, self.visit(old))
        return node

    def visit_Dict(self, node):
        keys, values = [], []
        for k, v in zip(node.keys, node.values):
            name = _call_name(v) if k is None else None
            if name in self.items:
                self.used.add(name)
                ret = self.items[name].body[-1].value
                assert isinstance(ret, ast.Dict)
                u = _Unqualify()
                for kk, vv in zip(ret.keys, ret.values):
                    keys.append(u.visit(copy.deepcopy(kk)) if kk is not None else None)
                    values.append(self.visit(u.visit(copy.deepcopy(vv))))
            else:
                keys.append(self.visit(k) if k is not None else None)
                values.append(self.visit(v))
        node.keys, node.values = keys, values
        return node


def _stage_maps(function):
    runs, items = {}, {}
    for seg in _ledger()["segments"]:
        if seg["function"] != function:
            continue
        (runs if seg["kind"] == "run" else items)[seg["owner_function"]] = _owner_fn(seg)
    return runs, items


@pytest.mark.parametrize("function", BUILDERS)
def test_inlining_every_stage_reproduces_the_base_builder_ast_exactly(function):
    base = _funcs(ast.parse(_base_src()))[function]
    cur = copy.deepcopy(_funcs(_tree(FACADE))[function])
    runs, items = _stage_maps(function)
    assert runs or items
    rec = _Reconstruct(runs, items)
    rec.visit(cur)
    assert rec.used == set(runs) | set(items), "every ledger stage must be called by its public builder"
    assert ast.dump(cur.args) == ast.dump(base.args)
    assert [ast.dump(s) for s in cur.body] == [ast.dump(s) for s in base.body], function


def test_moved_value_helpers_are_ast_identical_and_still_exported_by_the_facade():
    base = _funcs(ast.parse(_base_src()))
    moved = _ledger()["moved_helpers"]
    now = _funcs(_tree(moved["module"]))
    facade = importlib.import_module("libs.contracts.agent_outputs")
    values = importlib.import_module("libs.contracts.agent_output_values")
    for name in moved["functions"]:
        assert ast.dump(now[name]) == ast.dump(base[name]), name
        assert getattr(facade, name) is getattr(values, name), name


def test_non_moved_facade_definitions_are_ast_identical_to_base():
    base, cur = _funcs(ast.parse(_base_src())), _funcs(_tree(FACADE))
    moved = set(_ledger()["moved_helpers"]["functions"])
    for name, fn in base.items():
        if name in moved or name in BUILDERS:
            assert name in cur or name in moved
            continue
        assert ast.dump(fn) == ast.dump(cur[name]), name
    assert set(cur) == set(base) - moved


def test_stage_modules_are_small_pure_and_resolve_only_allowed_names():
    seg_modules = sorted({s["owner"] for s in _ledger()["segments"]})
    assert len(seg_modules) >= 12
    values = set(_ledger()["moved_helpers"]["functions"])
    for rel in seg_modules:
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
                assert n.module in ALLOWED_IMPORTS, (rel, n.module)
                allowed = ALLOWED_IMPORTS[n.module]
                names = {a.name for a in n.names}
                assert names <= (allowed if allowed is not None else values), (rel, names)
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
            first = fn.body[0]
            assert not (isinstance(first, ast.If) and isinstance(first.test, ast.Constant) and first.test.value is True
                        and len(fn.body) >= 2), f"{rel}:{fn.name}: mechanical `if True:` scaffold"


def test_public_builders_are_small_and_the_facade_keeps_final_assembly_and_validation():
    cur = _funcs(_tree(FACADE))
    for name in BUILDERS:
        loc = cur[name].end_lineno - cur[name].lineno + 1
        assert loc <= 350, (name, loc)
        src = ast.unparse(cur[name])
        assert "validate_artifact(" in src and "_base_output(" in src, name  # assembly + validation stay public
    assert "validate_artifact" in cur and "_base_output" in cur


def test_result_records_keep_the_legacy_positional_order_and_are_tuples():
    for seg in _ledger()["segments"]:
        if not seg.get("record"):
            continue
        mod = importlib.import_module(seg["owner"][:-3].replace("/", "."))
        rec = getattr(mod, seg["record"])
        assert issubclass(rec, tuple) and list(rec._fields) == seg["outputs"], seg["record"]
        values = tuple(range(len(seg["outputs"])))
        r = rec(*values)
        assert r == values and tuple(r) == values and hash(r) == hash(values)
        fn = _owner_fn(seg)
        ret = fn.body[-1].value
        assert isinstance(ret, ast.Call) and ret.func.id == seg["record"]
        assert [a.id for a in ret.args] == seg["outputs"] and not ret.keywords


def test_stage_call_sites_pass_exactly_the_declared_inputs_and_facade_only_when_needed():
    cur = _funcs(_tree(FACADE))
    for seg in _ledger()["segments"]:
        owner = _owner_fn(seg)
        params = [a.arg for a in owner.args.args]
        kwonly = [a.arg for a in owner.args.kwonlyargs]
        assert kwonly in ([], ["facade"]) and params == seg["inputs"] or kwonly in ([], ["facade"]) and sorted(params) == sorted(seg["inputs"]), seg["owner_function"]
        calls = [n for n in ast.walk(cur[seg["function"]]) if isinstance(n, ast.Call) and _call_name(n) == seg["owner_function"]]
        assert len(calls) == 1, seg["owner_function"]
        kws = [k.arg for k in calls[0].keywords]
        assert kws == params + kwonly, (seg["owner_function"], kws, params, kwonly)
        if kwonly:
            facade_arg = calls[0].keywords[-1].value
            assert ast.unparse(facade_arg) == "_r3_sys.modules[__name__]"


def test_t35_changed_paths_stay_inside_the_contract_scope_and_touch_no_authority_surface():
    # stage-pinned: T3.5 scope is fixed to its accepted end commit (later stages have their own scope gates)
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", BASE, T35_END_SHA], cwd=ROOT).decode().split(chr(0))
    allowed = ("libs/contracts/", "tests/", "docs/", "scripts/refactor/", ".github/workflows/", "CLAUDE.md", "AGENTS.md")
    for p in [x for x in out if x]:
        assert p.startswith(allowed), f"T3.5 touched an out-of-scope path: {p}"
        assert not p.startswith(FORBIDDEN_PREFIXES), p
