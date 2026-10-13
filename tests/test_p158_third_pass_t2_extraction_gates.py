"""P1.5 Third Pass T2 (Reporter bundle runner pure projection cuts) structural gates.

Every moved segment is recorded in docs/refactor/p1_5_third_pass_t2_moved_segments_ledger.json. The gates prove, without
running any production code path, that:

* inlining every Owner call back into its orchestrator reproduces the pinned baseline function AST exactly
  (`facade.NAME` -> `NAME`, owner body spliced in place of the call);
* Owner functions have no unresolved module globals (only builtins and the injected `facade`) and import nothing;
* Owner modules are <= 350 physical lines;
* every non-moved top-level definition of a touched module is AST-identical to the baseline;
* owners only mutate caller-fresh local containers (never parameters/graph State aliases);
* changed paths stay inside the Second Pass scope and never touch broker/execution/supervisor/LLM authority files.
"""
import ast
import builtins
import copy
import json
import subprocess
import symtable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "af0a4489dc250d804854e27917d5e2d881261537"  # T1 evidence-closure commit (T2 start)
# stage pin: T1 scope is fixed to its completion commit; T2 and later have their own gates (never widen this list)
T2_END_SHA = "d4a5364bae817504c253e06b9150ee49c692e120"
LEDGER = ROOT / "docs/refactor/p1_5_third_pass_t2_moved_segments_ledger.json"
MAX_OWNER_LOC = 350
ALLOWED_PREFIXES = ("tests/", "docs/", "scripts/refactor/", "libs/reporting/reporter_bundle_runtime_parts/")
FORBIDDEN_PREFIXES = ("libs/execution/", "libs/broker/", "libs/supervisor/", "libs/risk/", "libs/llm/", "libs/executor/",
                      "graphs/nodes/execute_from_packet.py", "graphs/nodes/decide_trade.py",
                      "graphs/nodes/update_state_after_execution.py", "libs/runtime/controlled_mock_lanes/")
# the two NEW package markers only (docstring-only, no code)
PACKAGE_MARKERS = {"libs/reporting/reporter_bundle_runtime_parts/__init__.py"}
ALLOWED_EXACT = {"libs/reporting/live_execution_bundle_runner.py",
                 ".github/workflows/p152-r2c-residual-regression.yml", "CLAUDE.md", "AGENTS.md"}
FORBIDDEN_OWNER_IMPORT_ROOTS = ("libs.broker", "libs.execution", "libs.supervisor", "libs.llm", "requests", "httpx",
                                "sqlite3", "subprocess", "socket", "openai", "anthropic")


def _ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _git_show(path, sha=BASE):
    return subprocess.check_output(["git", "show", f"{sha}:{path}"], cwd=ROOT).decode("utf-8-sig")


def _snap(path):
    """Immutable historical snapshot of `path` at this stage's end commit (never the moving HEAD)."""
    return _git_show(path, T2_END_SHA)


def _func(tree, name):
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return n
    raise AssertionError(f"function {name} not found")


class _Unqualify(ast.NodeTransformer):
    def visit_Attribute(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id == "facade" and isinstance(node.ctx, ast.Load):
            return ast.copy_location(ast.Name(id=node.attr, ctx=ast.Load()), node)
        return node


def _owner_inline_body(owner_fn):
    body = copy.deepcopy(owner_fn.body)
    assert isinstance(body[-1], ast.Return)
    body = body[:-1]
    if len(body) == 1 and isinstance(body[0], ast.If) and isinstance(body[0].test, ast.Constant) and body[0].test.value is True:
        body = body[0].body
    return [_Unqualify().visit(s) for s in body]


def _owner_inline_expr(owner_fn):
    ret = owner_fn.body[-1]
    assert isinstance(ret, ast.Return) and len(owner_fn.body) == 1
    return _Unqualify().visit(copy.deepcopy(ret.value))


def _is_owner_call(node, owners):
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in owners


class _Inline(ast.NodeTransformer):
    def __init__(self, owner_fns):
        self.owners = owner_fns
        self.used = set()

    def _splice(self, stmts):
        out = []
        for s in stmts:
            call = None
            if isinstance(s, ast.Expr) and _is_owner_call(s.value, self.owners):
                call = s.value
            elif (isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.value, ast.Subscript)
                  and _is_owner_call(s.value.value, self.owners)):
                call = s.value.value
            elif isinstance(s, ast.Assign) and len(s.targets) == 1 and _is_owner_call(s.value, self.owners):
                call = s.value
            if call is not None and self.owners[call.func.id]["kind"] == "run":
                self.used.add(call.func.id)
                out.extend(_owner_inline_body(self.owners[call.func.id]["node"]))
                continue
            out.append(self.visit(s))
        return out

    def generic_visit(self, node):
        for field, old in ast.iter_fields(node):
            if isinstance(old, list) and old and all(isinstance(x, ast.stmt) for x in old):
                setattr(node, field, self._splice(old))
            elif isinstance(old, list):
                new = []
                for x in old:
                    if isinstance(x, ast.AST):
                        x = self.visit(x)
                        if x is None:
                            continue
                    new.append(x)
                setattr(node, field, new)
            elif isinstance(old, ast.AST):
                new = self.visit(old)
                if new is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new)
        return node

    def visit_Call(self, node):
        if _is_owner_call(node, self.owners) and self.owners[node.func.id]["kind"] == "builder":
            self.used.add(node.func.id)
            return _owner_inline_expr(self.owners[node.func.id]["node"])
        return self.generic_visit(node)


def _group():
    groups = {}
    for seg in _ledger()["segments"]:
        groups.setdefault((seg["module"], seg["function"]), []).append(seg)
    return groups


def _owner_nodes(segs):
    owners = {}
    for seg in segs:
        tree = ast.parse(_snap(seg["owner_module"]))
        owners[seg["owner_function"]] = {"kind": seg["kind"], "node": _func(tree, seg["owner_function"])}
    return owners


def test_ledger_is_complete_and_unique():
    doc = _ledger()
    assert doc["base_sha"] == BASE
    names = [s["owner_function"] for s in doc["segments"]]
    assert len(names) == len(set(names)), "duplicate owner function names in ledger"
    assert len(doc["segments"]) >= 6
    assert {s["function"] for s in doc["segments"]} >= {
        "main"}


def test_inlining_owner_calls_reconstructs_the_baseline_function_ast():
    for (module, function), segs in _group().items():
        base_fn = _func(ast.parse(_git_show(module)), function)
        cur_fn = copy.deepcopy(_func(ast.parse(_snap(module)), function))
        owners = _owner_nodes(segs)
        inl = _Inline(owners)
        new_fn = inl.visit(cur_fn)
        ast.fix_missing_locations(new_fn)
        assert inl.used == set(owners), (module, function, sorted(set(owners) - inl.used))
        assert ast.dump(new_fn) == ast.dump(base_fn), f"{module}::{function} does not reconstruct to the baseline body"


def test_unmoved_definitions_and_module_constants_are_baseline_identical():
    moved = {}
    for (module, function) in _group():
        moved.setdefault(module, set()).add(function)
    for module, names in moved.items():
        before_t = ast.parse(_git_show(module))
        after_t = ast.parse(_snap(module))
        before = {n.name: n for n in before_t.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        after = {n.name: n for n in after_t.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        assert before.keys() == after.keys(), (module, sorted(set(before) ^ set(after)))
        for name, node in before.items():
            if name not in names:
                assert ast.dump(node) == ast.dump(after[name]), (module, name)
        keep = lambda t: [ast.dump(n) for n in t.body
                          if not isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))]
        assert keep(before_t) == keep(after_t), module


def _free_globals(owner, fname):
    table = symtable.symtable(_snap(owner), owner, "exec")
    child = next(c for c in table.get_children() if c.get_name() == fname)
    out = set()
    for sym in child.get_symbols():
        if sym.is_global() and sym.is_referenced():
            out.add(sym.get_name())
    return out


def test_owner_functions_have_no_unresolved_globals_and_no_imports():
    builtin_names = set(dir(builtins))
    for owner in {s["owner_module"] for s in _ledger()["segments"]}:
        tree = ast.parse(_snap(owner))
        for node in tree.body:
            if isinstance(node, ast.Import):
                raise AssertionError(f"{owner}: plain import not allowed in a pure Owner")
            if isinstance(node, ast.ImportFrom):
                assert node.module == "__future__", (owner, node.module)
        for n in tree.body:
            if isinstance(n, ast.FunctionDef):
                bad = _free_globals(owner, n.name) - builtin_names
                assert not bad, (owner, n.name, sorted(bad))
                assert [a.arg for a in n.args.kwonlyargs] == ["facade"], (owner, n.name)


def test_owner_modules_respect_loc_budget():
    for owner in {s["owner_module"] for s in _ledger()["segments"]}:
        n = len(_snap(owner).splitlines())
        assert n <= MAX_OWNER_LOC, (owner, n)


def test_owners_do_not_import_or_reference_forbidden_authority_surfaces():
    for owner in {s["owner_module"] for s in _ledger()["segments"]}:
        text = _snap(owner)
        for part in FORBIDDEN_OWNER_IMPORT_ROOTS:
            assert f"import {part}" not in text and f"from {part}" not in text, (owner, part)
        for token in ("os.environ", "os.getenv", "getenv(", "time.time(", "datetime.now", "uuid.uuid", "open("):
            assert token not in text, (owner, token)


def _fresh_names(fn):
    params = {a.arg for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs}
    if fn.args.vararg:
        params.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        params.add(fn.args.kwarg.arg)

    def fresh(e):
        if isinstance(e, (ast.Dict, ast.List, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
            return True
        if isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id in {
                "dict", "list", "set", "sorted", "tuple", "defaultdict", "OrderedDict", "deque"}:
            return True
        return isinstance(e, ast.IfExp) and fresh(e.body) and fresh(e.orelse)

    good, bad = set(), set(params)
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    (good if fresh(n.value) else bad).add(t.id)
                else:
                    bad.update(y.id for y in ast.walk(t) if isinstance(y, ast.Name) and isinstance(y.ctx, ast.Store))
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            (good if (n.value is not None and fresh(n.value)) else bad).add(n.target.id)
        elif isinstance(n, (ast.For, ast.AugAssign, ast.NamedExpr, ast.comprehension)):
            bad.update(y.id for y in ast.walk(n.target) if isinstance(y, ast.Name))
        elif isinstance(n, ast.With):
            for it in n.items:
                if it.optional_vars is not None:
                    bad.update(y.id for y in ast.walk(it.optional_vars) if isinstance(y, ast.Name))
        elif isinstance(n, ast.ExceptHandler) and n.name:
            bad.add(n.name)
    return good - bad


def test_owners_only_mutate_caller_fresh_local_containers():
    for (module, function), segs in _group().items():
        base_fn = _func(ast.parse(_git_show(module)), function)
        fresh = _fresh_names(base_fn)
        for seg in segs:
            for name in seg["mutates_inputs"]:
                assert name in fresh, f"{seg['owner_function']} mutates non-fresh input {name!r} of {module}::{function}"


def test_t2_end_sha_is_an_ancestor_of_head():
    r = subprocess.run(["git", "merge-base", "--is-ancestor", T2_END_SHA, "HEAD"], cwd=ROOT)
    assert r.returncode == 0, "T2_END_SHA must be reachable from HEAD (shallow clone: fetch the pinned SHA)"


def test_t2_changes_stay_in_scope():
    """Scope is BASE..T2_END_SHA, not BASE..HEAD: later tranches are governed by their own gates."""
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", BASE, T2_END_SHA], cwd=ROOT).decode().split(chr(0))
    changed = [p for p in out if p]
    assert changed, "empty T1 diff"
    for path in changed:
        assert not path.startswith(FORBIDDEN_PREFIXES), f"authority surface changed: {path}"
        assert path in ALLOWED_EXACT or path.startswith(ALLOWED_PREFIXES), f"path outside T2 scope: {path}"
    ledger_modules = {s["module"] for s in _ledger()["segments"]}
    owners = {s["owner_module"] for s in _ledger()["segments"]}
    for path in [p for p in changed if p.endswith(".py") and not p.startswith(("tests/", "scripts/"))]:
        if path in PACKAGE_MARKERS:
            text = subprocess.check_output(["git", "show", f"{T2_END_SHA}:{path}"], cwd=ROOT).decode("utf-8")
            assert len(text.splitlines()) <= 2, path
            continue
        # every other changed production .py file is either a ledgered original module or a NEW ledgered Owner
        assert path in ledger_modules or path in owners, f"unledgered production change: {path}"


MAIN_MODULE = "libs/reporting/live_execution_bundle_runner.py"
# effect owners that must stay in main() (lock/queue/persist/log/LLM sequence); none may appear in any Owner module
RETAINED_EFFECT_CALLS = ("_touch_background_job_lock", "write_json", "_log_bundle_event", "persist_trade_report_outputs",
                         "persist_trade_llm_artifacts", "persist_live_story_input_artifacts",
                         "persist_trade_bundle_outputs", "_write_report_generation_state")


def _call_names(fn):
    return {n.func.id for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_main_shrank_and_public_signatures_are_unchanged():
    base_fn = _func(ast.parse(_git_show(MAIN_MODULE)), "main")
    cur_t = ast.parse(_snap(MAIN_MODULE))
    cur_fn = _func(cur_t, "main")
    base_loc = base_fn.end_lineno - base_fn.lineno + 1
    cur_loc = cur_fn.end_lineno - cur_fn.lineno + 1
    assert cur_loc < base_loc - 150, (base_loc, cur_loc)
    assert ast.dump(base_fn.args) == ast.dump(cur_fn.args)
    base_inproc = _func(ast.parse(_git_show(MAIN_MODULE)), "run_live_execution_bundle_inprocess")
    assert ast.dump(base_inproc) == ast.dump(_func(cur_t, "run_live_execution_bundle_inprocess"))


def test_ordered_effects_stay_in_main_and_never_in_owners():
    cur_t = ast.parse(_snap(MAIN_MODULE))
    base_calls = _call_names(_func(ast.parse(_git_show(MAIN_MODULE)), "main"))
    main_calls = _call_names(_func(cur_t, "main"))
    for name in RETAINED_EFFECT_CALLS:
        if name in base_calls:
            assert name in main_calls, f"effect call {name} left main()"
    for owner in {s["owner_module"] for s in _ledger()["segments"]}:
        tree = ast.parse(_snap(owner))
        for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
            attr_calls = {n.func.attr for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
            names = _call_names(fn) | attr_calls
            for name in RETAINED_EFFECT_CALLS:
                assert name not in names, f"{owner}:{fn.name} performs retained effect {name}"
            assert not ({"open", "print"} & names), (owner, fn.name)
