"""Fast Track Wave C (P1.5.7 Commander, P1.5.8 naming aliases, P1.5.9 Executor read models) scope + trading-authority boundary.

Stage-scoped: diffs the pinned Wave C start (== Wave B end) against HEAD. Wave A/B guards stay pinned to their own end commits.
"""
import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVE_C_BASE = "cba2124a85d2a3bf7cef96876920ba4912bd1c5e"
LEDGER = ROOT / "docs/refactor/p1_5_wave_c_moved_bodies_ledger.json"

ALLOWED_EXACT = {
    "graphs/commander_runtime.py", "graphs/nodes/execute_from_packet.py",
    "libs/execution/executor_observability.py",
    "graphs/pipelines/live_cycle.py", "graphs/pipelines/runtime_tick.py", "graphs/pipelines/eod_report.py",
    "libs/runtime/entrypoints/live_loop.py", "libs/runtime/entrypoints/m13_live_loop.py",
    "libs/runtime/entrypoints/live_session_watch.py", "libs/runtime/entrypoints/offhours_validation_loop.py",
    "libs/runtime/entrypoints/mock_exam_day.py", "libs/runtime/entrypoint_common.py",
    "scripts/run_live_loop.py", "scripts/run_session.py", "scripts/restart_live_session.py",
    "AGENTS.md", "CLAUDE.md", ".github/workflows/p152-r2c-residual-regression.yml",
}
ALLOWED_PREFIXES = ("libs/runtime/commander/", "tests/", "docs/", "scripts/refactor/")
# trading authority / execution / persistence surfaces that Wave C must never touch
FORBIDDEN_PREFIXES = (
    "libs/execution/", "libs/broker/", "libs/supervisor/", "libs/executor/", "libs/llm/", "libs/agent/",
    "graphs/nodes/strategist_node.py", "graphs/nodes/scanner_node.py", "graphs/nodes/monitor_node.py",
    "graphs/nodes/executor_node.py", "graphs/nodes/commander_node.py", "graphs/nodes/decide_trade.py",
    "graphs/nodes/decision_node.py", "graphs/nodes/execute_order.py", "graphs/nodes/portfolio_guard_node.py",
    "apps/", "deploy/", "conftest.py", "Dockerfile", "docker-compose", "libs/runtime/monitor_exit/",
)
ALLOWED_FORBIDDEN_EXCEPTIONS = {"libs/execution/executor_observability.py", "graphs/nodes/execute_from_packet.py"}
FORBIDDEN_IMPORT_PARTS = ("libs.execution.intent", "libs.execution.guards", "libs.execution.executors", "libs.broker",
                          "libs.supervisor", "libs.executor", "libs.llm", "requests", "httpx")


def _changed():
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", WAVE_C_BASE, "HEAD"], cwd=ROOT).decode().split(chr(0))
    return [p for p in out if p]


def test_wave_c_changes_stay_in_commander_naming_and_executor_readmodel_scope():
    for path in _changed():
        if path in ALLOWED_EXACT or path.startswith(ALLOWED_PREFIXES):
            continue
        raise AssertionError(f"unexpected path mutated in Wave C: {path}")
    for path in _changed():
        if path.startswith(FORBIDDEN_PREFIXES) and path not in ALLOWED_EXACT:
            raise AssertionError(f"trading-authority / out-of-wave path mutated: {path}")
    assert (ROOT / "libs/execution/executor_observability.py").is_file()


def _base_tree(path):
    src = subprocess.check_output(["git", "show", f"{WAVE_C_BASE}:{path}"], cwd=ROOT).decode("utf-8-sig")
    return ast.parse(src)


def test_unmoved_functions_of_touched_modules_are_ast_identical_to_baseline():
    """Executor guard / admission / CAS / UNKNOWN / broker paths and Commander routing/orchestration are untouched:
    every top-level definition that is not a ledger-moved wrapper is byte-AST-identical to the Wave C baseline."""
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    moved = {}
    for m in doc["moves"]:
        moved.setdefault(m["module"], set()).add(m["name"])
    assert set(moved) <= {"graphs/commander_runtime.py", "graphs/nodes/execute_from_packet.py"}
    for module, names in moved.items():
        before = {n.name: n for n in _base_tree(module).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        after_tree = ast.parse((ROOT / module).read_text(encoding="utf-8-sig"))
        after = {n.name: n for n in after_tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        assert before.keys() == after.keys(), (module, sorted(set(before) ^ set(after)))
        for name, node in before.items():
            if name in names:
                continue
            assert ast.dump(node) == ast.dump(after[name]), (module, name)
        # module-level non-def statements (constants) unchanged except the added Owner imports / sys alias
        keep = lambda t: [ast.dump(n) for n in t.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))]
        assert keep(_base_tree(module)) == keep(after_tree), module


def test_executor_owner_is_observability_only_with_no_authority_imports():
    text = (ROOT / "libs/execution/executor_observability.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    assert len(text.splitlines()) <= 350
    for node in ast.walk(tree):
        mods = [a.name for a in node.names] if isinstance(node, ast.Import) else \
            ([node.module or ""] if isinstance(node, ast.ImportFrom) else [])
        for m in mods:
            assert not any(m.startswith(f) for f in FORBIDDEN_IMPORT_PARTS), m
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    ex = sorted(m["name"] for m in doc["moves"] if m["module"] == "graphs/nodes/execute_from_packet.py")
    assert ex == ["_append_execution_trace_entries", "_extract_strategy_policy", "_summarize_strategy_policy"], ex
    idents = set()
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        for node in ast.walk(fn):
            if isinstance(node, ast.Name):
                idents.add(node.id.lower())
            elif isinstance(node, ast.Attribute):
                idents.add(node.attr.lower())
    for banned in ("execute_owned_order", "submit", "place_order", "cancel_order", "admission", "quarantine", "cas_"):
        assert not any(banned in i for i in idents), banned


def test_commander_owners_import_no_execution_surface_and_no_new_llm_role():
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    for rel in sorted({m["owner"] for m in doc["moves"] if m["owner"].startswith("libs/runtime/commander/")}):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert len(text.splitlines()) <= 350, rel
        tree = ast.parse(text)
        for node in ast.walk(tree):
            mods = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                ([node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            for m in mods:
                assert not any(m.startswith(f) for f in FORBIDDEN_IMPORT_PARTS), (rel, m)
        assert "LLMRouter" not in text and ".chat(" not in text, rel
