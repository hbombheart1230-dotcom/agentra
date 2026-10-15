"""T4-B structural gates for the Monitor decomposition.

Proven without running production code, against the IMMUTABLE BASE `c338ba3`:
* inlining every Owner call (statement-run windows, early-return ladder windows, value builders and
  `monitor_output` projections; `facade.NAME` -> `NAME`, injected `facade` -> `_r3_sys.modules[__name__]`) reproduces the
  BASE AST of `monitor_node`, `_evaluate_monitor_entry_candidate`, `evaluate_exit_policy` and
  `_build_account_pnl_crosscheck` exactly (signature, evaluation order, State writes, event/log/trace calls, control flow,
  guard precedence);
* every other top-level definition of the two modules is AST-identical to BASE;
* Owners: <= 350 lines, no I/O/env/clock tokens, no unresolved globals, imports only `__future__`/`typing`, and no second
  Monitor policy authority (no duplicate entry/exit decision constants);
* changed paths stay inside the Monitor scope and touch no authority surface.
"""
import ast
import builtins
import copy
import importlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "c338ba34276566b0b5f6de1e7f556778ec917968"
FREEZE = "c50db1749dbad7058fe0c45ab44a9c84cb12fb34"
LEDGER = ROOT / "docs/refactor/p1_5_third_pass_t4b_moved_segments_ledger.json"
MODULES = {
    "graphs/nodes/monitor_node.py": ("monitor_node", "_evaluate_monitor_entry_candidate"),
    "libs/runtime/exit_policy.py": ("evaluate_exit_policy", "_build_account_pnl_crosscheck"),
}
MAX_OWNER_LOC = 350
FORBIDDEN_TOKENS = ("os.environ", "os.getenv", "getenv(", "time.time(", "datetime.now", "datetime.utcnow", "uuid.uuid",
                    "subprocess", "sqlite3", "requests.", "print(", "open(", "logging.", "random.")
FORBIDDEN_PREFIXES = ("libs/execution/", "libs/broker/", "libs/supervisor/", "libs/risk/", "libs/llm/", "libs/executor/",
                      "graphs/nodes/execute_from_packet.py", "graphs/nodes/decide_trade.py",
                      "graphs/nodes/update_state_after_execution.py", "libs/runtime/controlled_mock_lanes/")
ALLOWED_CHANGED = ("graphs/nodes/monitor_node.py", "libs/runtime/exit_policy.py", "libs/runtime/monitor/",
                   "libs/runtime/monitor_exit/", "tests/", "docs/", "scripts/refactor/", ".github/workflows/",
                   "CLAUDE.md", "AGENTS.md")


def _ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _segments(module):
    return [s for s in _ledger()["segments"] if s["module"] == module]


def _base_tree(module):
    return ast.parse(subprocess.check_output(["git", "show", f"{BASE}:{module}"], cwd=ROOT).decode("utf-8-sig"))


def _cur_tree(module):
    return ast.parse((ROOT / module).read_text(encoding="utf-8-sig"))


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


class _OutToMonitorOutput(ast.NodeTransformer):
    """projection owner local `out` -> `state["monitor_output"]`."""

    def visit_Name(self, node):
        if node.id == "out":
            return ast.parse('state["monitor_output"]', mode="eval").body
        return node


def _owner_fn(seg):
    return _funcs(ast.parse((ROOT / seg["owner"]).read_text(encoding="utf-8-sig")))[seg["owner_function"]]


def _call_name(call):
    return call.func.id if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) else None


def _is_ret_guard(stmt):
    return (isinstance(stmt, ast.If) and not stmt.orelse and len(stmt.body) == 1
            and isinstance(stmt.body[0], ast.Return) and isinstance(stmt.body[0].value, ast.Name)
            and stmt.body[0].value.id == "_t4_ret" and ast.dump(stmt.test) == ast.dump(
                ast.parse("_t4_ret is not None", mode="eval").body))


def _run_body(owner_fn, projection=False):
    body = copy.deepcopy(owner_fn.body)
    assert isinstance(body[-1], ast.Return)
    stmts = body[:-1]
    if projection:
        assert ast.dump(stmts[0]) == ast.dump(ast.parse("out = {}").body[0])
        stmts = [_OutToMonitorOutput().visit(s) for s in stmts[1:]]
    return [_Unqualify().visit(s) for s in stmts]


class _Reconstruct(ast.NodeTransformer):
    def __init__(self, runs, builders, projections):
        self.runs, self.builders, self.projections, self.used = runs, builders, projections, set()

    def _inline_for(self, stmt, nxt):
        """(statements, consumed_next) when `stmt` is an Owner call site, else None."""
        v = getattr(stmt, "value", None)
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name) \
                and stmt.targets[0].id == "_t4_ret" and _call_name(v) in self.runs:
            assert nxt is not None and _is_ret_guard(nxt), "early-return window without its None-sentinel guard"
            name = _call_name(v)
            self.used.add(name)
            return [self.visit(b) for b in _run_body(self.runs[name])], True
        if isinstance(stmt, (ast.Assign, ast.Expr)) and _call_name(v) in self.runs:
            name = _call_name(v)
            self.used.add(name)
            return [self.visit(b) for b in _run_body(self.runs[name])], False
        if isinstance(stmt, ast.Expr) and isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) \
                and v.func.attr == "update" and ast.dump(v.func.value) == ast.dump(
                    ast.parse('state["monitor_output"]', mode="eval").body) \
                and len(v.args) == 1 and _call_name(v.args[0]) in self.projections:
            name = _call_name(v.args[0])
            self.used.add(name)
            return [self.visit(b) for b in _run_body(self.projections[name], projection=True)], False
        return None

    def generic_visit(self, node):
        for field, old in ast.iter_fields(node):
            if isinstance(old, list) and old and all(isinstance(x, ast.stmt) for x in old):
                new, i = [], 0
                while i < len(old):
                    stmt = old[i]
                    hit = self._inline_for(stmt, old[i + 1] if i + 1 < len(old) else None)
                    if hit:
                        new.extend(hit[0])
                        i += 2 if hit[1] else 1
                        continue
                    r = self.visit(stmt)
                    new.extend(r if isinstance(r, list) else [r])
                    i += 1
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


def _stage_maps(module):
    runs, builders, projections = {}, {}, {}
    for seg in _segments(module):
        target = {"run": runs, "builder": builders, "projection": projections}[seg["kind"]]
        target[seg["owner_function"]] = _owner_fn(seg)
    return runs, builders, projections


def test_inlining_every_owner_reproduces_the_base_monitor_function_asts_exactly():
    for module, names in MODULES.items():
        base, cur_all = _funcs(_base_tree(module)), _funcs(_cur_tree(module))
        runs, builders, projections = _stage_maps(module)
        rec = _Reconstruct(runs, builders, projections)
        for fname in names:
            cur = copy.deepcopy(cur_all[fname])
            rec.visit(cur)
            assert ast.dump(cur.args) == ast.dump(base[fname].args), fname
            assert [ast.dump(s) for s in cur.body] == [ast.dump(s) for s in base[fname].body], (module, fname)
        assert rec.used == set(runs) | set(builders) | set(projections), "every ledger stage must be called"


def test_non_moved_definitions_are_ast_identical_to_base():
    for module, names in MODULES.items():
        base_t, cur_t = _base_tree(module), _cur_tree(module)
        base, cur = _funcs(base_t), _funcs(cur_t)
        assert set(base) == set(cur), module
        for name, fn in base.items():
            if name in names:
                continue
            assert ast.dump(fn) == ast.dump(cur[name]), (module, name)
        keep = lambda t: [ast.dump(n) for n in t.body if not isinstance(n, (ast.FunctionDef, ast.Import, ast.ImportFrom))]  # noqa: E731
        assert keep(base_t) == keep(cur_t), module


def test_new_import_lines_are_only_the_ledger_owner_names():
    for module in MODULES:
        base_names = {(n.module, a.name) for n in _base_tree(module).body if isinstance(n, ast.ImportFrom) for a in n.names}
        cur_names = {(n.module, a.name) for n in _cur_tree(module).body if isinstance(n, ast.ImportFrom) for a in n.names}
        added = cur_names - base_names
        expected = {(s["owner"][:-3].replace("/", "."), s["owner_function"]) for s in _segments(module)}
        assert added == expected and base_names <= cur_names, module


def test_owner_modules_are_small_pure_and_resolve_only_allowed_names():
    mods = sorted({s["owner"] for s in _ledger()["segments"]})
    assert len(mods) >= 10
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
                elif isinstance(n, ast.ImportFrom):
                    # function-level import moved verbatim from BASE; only in-repo runtime modules are allowed
                    assert n.module and n.module.startswith("libs.runtime."), (rel, n.module)
                    bound |= {a.asname or a.name for a in n.names}
            for n in ast.walk(fn):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    assert n.id in bound or n.id in known, (rel, fn.name, n.id)
        importlib.import_module(rel[:-3].replace("/", "."))


def test_monitor_functions_are_substantially_smaller():
    expected = {("graphs/nodes/monitor_node.py", "monitor_node"): 0.65,
                ("graphs/nodes/monitor_node.py", "_evaluate_monitor_entry_candidate"): 0.60,
                ("libs/runtime/exit_policy.py", "evaluate_exit_policy"): 0.60,
                ("libs/runtime/exit_policy.py", "_build_account_pnl_crosscheck"): 0.80}
    for (module, fname), ratio in expected.items():
        base, cur = _funcs(_base_tree(module))[fname], _funcs(_cur_tree(module))[fname]
        base_loc, cur_loc = base.end_lineno - base.lineno + 1, cur.end_lineno - cur.lineno + 1
        assert cur_loc <= base_loc * ratio, (fname, base_loc, cur_loc)


def test_result_records_keep_sorted_output_order_and_are_tuples():
    seen = 0
    for seg in _ledger()["segments"]:
        if not seg.get("record"):
            continue
        mod = importlib.import_module(seg["owner"][:-3].replace("/", "."))
        rec = getattr(mod, seg["record"])
        assert issubclass(rec, tuple) and list(rec._fields) == seg["outputs"]
        values = tuple(range(len(seg["outputs"])))
        assert rec(*values) == values
        seen += 1
    assert seen >= 8


def test_call_sites_pass_exactly_the_declared_inputs():
    for module, names in MODULES.items():
        funcs = _funcs(_cur_tree(module))
        for seg in _segments(module):
            owner = _owner_fn(seg)
            params = [a.arg for a in owner.args.args]
            kwonly = [a.arg for a in owner.args.kwonlyargs]
            calls = [n for fname in names for n in ast.walk(funcs[fname])
                     if isinstance(n, ast.Call) and _call_name(n) == seg["owner_function"]]
            assert len(calls) == 1, seg["owner_function"]
            assert [k.arg for k in calls[0].keywords] == params + kwonly, seg["owner_function"]
            if kwonly:
                assert kwonly == ["facade"] and ast.unparse(calls[0].keywords[-1].value) == "_r3_sys.modules[__name__]"


def test_ledger_is_complete_and_names_the_base_and_freeze():
    doc = _ledger()
    assert doc["base_commit"] == BASE and doc["freeze_commit"] == FREEZE
    assert doc["segments"] and sum(s["loc"] for s in doc["segments"]) >= 1000
    assert {s["kind"] for s in doc["segments"]} == {"run", "builder", "projection"}
    freeze_file = (ROOT / "tests/fixtures/p1_5_t4b_monitor/FREEZE_COMMIT.txt").read_text(encoding="utf-8").strip()
    assert freeze_file == FREEZE


def test_no_duplicate_exit_decision_authority_in_the_new_owners():
    # the trigger ladder windows return `_finalize(...)` results of the orchestrator closure; no Owner defines its own
    # policy defaults or re-implements `evaluate_exit_policy`
    for rel in sorted({s["owner"] for s in _ledger()["segments"]}):
        text = (ROOT / rel).read_text(encoding="utf-8-sig")
        assert "def evaluate_exit_policy" not in text and "def monitor_node" not in text, rel
        assert "DEFAULT_" not in text, rel


def test_t4b_changed_paths_stay_in_monitor_scope_and_touch_no_authority_surface():
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", BASE, "HEAD"], cwd=ROOT).decode().split(chr(0))
    for p in [x for x in out if x]:
        assert p.startswith(ALLOWED_CHANGED), f"T4-B touched an out-of-scope path: {p}"
        assert not p.startswith(FORBIDDEN_PREFIXES), p
        assert not p.startswith("tests/fixtures/p1_5_t35_agent_outputs/"), "T3.5 golden fixtures must stay unchanged"
        assert not p.startswith("tests/fixtures/p1_5_t4a_scanner_node/"), "T4-A golden fixtures must stay unchanged"
