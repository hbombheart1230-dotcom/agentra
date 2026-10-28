"""RF-040 C1/C2: ``libs/agent/executor.py`` is shadowed by the ``libs/agent/executor/`` package.

AST/import-resolution only: nothing is constructed or executed, no broker/Settings/Supervisor touched.
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import ast
import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FILE = ROOT / "libs" / "agent" / "executor.py"
PACKAGE_INIT = ROOT / "libs" / "agent" / "executor" / "__init__.py"
PACKAGE_COPY = ROOT / "libs" / "agent" / "executor" / "agent_executor.py"


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _class_body(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
    return [ast.dump(n) for n in cls.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]


def test_dotted_name_resolves_to_the_package_not_the_sibling_module():
    mod = importlib.import_module("libs.agent.executor")
    _eq(Path(mod.__file__).resolve(), PACKAGE_INIT.resolve())
    _eq(sorted(mod.__all__), ["AgentExecutor", "ExecutorAgent"])
    if not hasattr(mod, "__path__"):
        raise AssertionError("libs.agent.executor must be a package")


def test_shadowed_module_agentexecutor_is_ast_identical_to_the_package_copy():
    if not MODULE_FILE.exists():
        raise AssertionError("sibling module removed: update the RF-040 ACTION record, then this test")
    _eq(_class_body(MODULE_FILE, "AgentExecutor"), _class_body(PACKAGE_COPY, "AgentExecutor"))


def test_package_exports_the_same_class_object_as_its_submodule():
    mod = importlib.import_module("libs.agent.executor")
    sub = importlib.import_module("libs.agent.executor.agent_executor")
    if mod.AgentExecutor is not sub.AgentExecutor:
        raise AssertionError("package AgentExecutor must be the submodule class")
    _eq(mod.AgentExecutor.__module__, "libs.agent.executor.agent_executor")


def test_agent_executor_submit_maps_intent_shapes_with_a_fake_agent():
    from libs.agent.executor import AgentExecutor

    class FakeAgent:
        def __init__(self):
            self.calls = []

        def submit_order_intent(self, **kw):
            self.calls.append(kw)
            return {"fake": True}

    agent = FakeAgent()
    ex = AgentExecutor(executor_agent=agent)
    _eq(ex.submit(intent={"side": "buy", "symbol": "005930", "qty": "3", "price": 70000})["fake"], True)
    first = agent.calls[0]
    _eq((first["side"], first["symbol"], first["qty"], first["price"], first["order_type"], first["approval_mode"], first["execution_enabled"]),
        ("buy", "005930", 3, 70000, "market", "manual", False))
    ex.submit(intent={"action": "SELL", "symbol": "000660", "qty": 1, "order_type": "limit", "rationale": "r"}, approval_mode="auto", execution_enabled=True)
    second = agent.calls[1]
    _eq((second["side"], second["order_type"], second["price"], second["rationale"], second["execution_enabled"]), ("sell", "limit", None, "r", True))
    rejected = ex.submit(intent={"action": "HOLD", "symbol": "x", "qty": 1})
    _eq(rejected["decision"]["status"], "rejected")
    _eq(len(agent.calls), 2)                                  # unsupported shape never reaches the agent
