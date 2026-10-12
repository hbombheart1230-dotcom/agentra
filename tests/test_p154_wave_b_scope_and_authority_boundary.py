"""Fast Track Wave B (P1.5.4 Strategist / P1.5.5 Scanner / P1.5.6 Monitor) scope + trading-authority boundary.

Stage-scoped: diffs the pinned Wave B start commit against the pinned Wave B end commit. Later waves get their own gate; this one never
loosens the Wave A guard (tests/test_p152_facade_abi_and_authority_boundary.py stays pinned to the Wave A end).
"""
import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVE_B_BASE = "877455db439e9e6f72af413216acc9758b91a2a9"
WAVE_B_END = "cba2124a85d2a3bf7cef96876920ba4912bd1c5e"  # stage pin: later waves have their own gate
LEDGER = ROOT / "docs/refactor/p1_5_wave_b_moved_bodies_ledger.json"

ALLOWED = (
    "graphs/nodes/strategist_node.py", "graphs/nodes/scanner_node.py", "graphs/nodes/monitor_node.py",
    "libs/runtime/strategist/", "libs/runtime/scanner/", "libs/runtime/monitor/",
    "tests/", "docs/", "scripts/refactor/",
)
ROOT_DOCS = {"AGENTS.md", "CLAUDE.md"}
WORKFLOW = ".github/workflows/p152-r2c-residual-regression.yml"
# trading authority / execution / persistence / LLM-routing surfaces that Wave B must never touch
FORBIDDEN_PREFIXES = (
    "graphs/nodes/executor_node.py", "graphs/nodes/commander_node.py", "graphs/nodes/portfolio_guard_node.py",
    "graphs/nodes/execute_order.py", "graphs/nodes/execute_from_packet.py", "graphs/nodes/decide_trade.py",
    "graphs/nodes/decision_node.py", "graphs/nodes/reporter_node.py",
    "apps/", "libs/execution/", "libs/broker/", "libs/supervisor/", "libs/executor/", "libs/llm/",
    "libs/runtime/commander/", "libs/runtime/executor", "libs/runtime/monitor_exit/", "libs/reporting/",
    "conftest.py", "Dockerfile", "docker-compose",
)
FORBIDDEN_IMPORT_PARTS = ("libs.execution", "libs.broker", "libs.supervisor", "libs.executor", "libs.llm",
                          "graphs.nodes", "requests", "httpx")


def _changed():
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", WAVE_B_BASE, WAVE_B_END], cwd=ROOT).decode().split(chr(0))
    return [p for p in out if p]


def test_wave_b_changes_stay_in_strategist_scanner_monitor_scope():
    for path in _changed():
        if path in ROOT_DOCS:
            continue
        if path.startswith(".github/workflows/"):
            assert path == WORKFLOW, path
            continue
        assert not path.startswith(FORBIDDEN_PREFIXES) or path.startswith(("tests/", "docs/", "scripts/refactor/")), \
            f"trading-authority / out-of-wave path mutated: {path}"
        assert path.startswith(ALLOWED), f"unexpected path mutated in Wave B: {path}"


def test_wave_b_owners_have_no_execution_or_llm_routing_imports():
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    owners = sorted({m["owner"] for m in doc["moves"]})
    assert owners, "Wave B ledger must list moved owners"
    for rel in owners:
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mods = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                ([node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            for m in mods:
                assert not any(m == f or m.startswith(f + ".") for f in FORBIDDEN_IMPORT_PARTS), (rel, m)
        assert len((ROOT / rel).read_text(encoding="utf-8").splitlines()) <= 350, rel


def test_monitor_stays_intent_only_and_no_new_llm_surface():
    """Moved Monitor/Strategist/Scanner bodies must not introduce broker/order/LLM-router attribute use that the
    pinned baseline body did not already have (identity of body is enforced by the moved-body gate; this checks
    the Owner sources textually for forbidden call surfaces)."""
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    banned = ("place_order(", "submit_order(", "send_order(", ".execute_order(", "LLMRouter(", ".chat(", "Executor(")
    for rel in sorted({m["owner"] for m in doc["moves"]}):
        text = (ROOT / rel).read_text(encoding="utf-8")
        base_names = {m["name"] for m in doc["moves"] if m["owner"] == rel}
        hits = [b for b in banned if b in text]
        assert not hits or rel.startswith("libs/runtime/strategist/llm/"), (rel, hits, sorted(base_names)[:3])
