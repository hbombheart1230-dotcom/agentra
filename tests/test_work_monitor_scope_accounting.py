"""Current scope evidence is pinned, bounded and source-verifiable; not acceptance."""
import ast
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/refactor"))
import work_monitor_current_tree as T

PATH = ROOT / "docs/refactor/work_projects/evidence/monitor/continuous/current_scope.json"


def test_m007_current_role_sources_match_the_exact_pinned_code():
    doc = json.loads(PATH.read_text(encoding="utf-8"))
    assert doc["code_sha"] == "800841f229606c419dae67b0d6f794b9238676e9"
    sources = [row["path"] for row in doc["modules"]]
    assert len(sources) == len(set(sources)) == doc["module_count"] == 100
    assert subprocess.check_output(["git", "diff", "--name-only", doc["code_sha"], "--", *sources], cwd=ROOT).strip() == b""
    for row in doc["modules"]:
        current = (ROOT / row["path"]).read_text(encoding="utf-8")
        assert hashlib.sha256(current.encode()).hexdigest() == row["source_sha256"]
        assert len(current.splitlines()) == row["LOC"]


def test_m007_counts_and_dispositions_are_accounting_not_self_acceptance():
    doc = json.loads(PATH.read_text(encoding="utf-8"))
    assert doc["state"] == "PARTIAL_WITH_BLOCKERS_NOT_ROLE_READY"
    assert Counter(row["kind"] for row in doc["modules"]) == doc["module_kinds"]
    symbols = [s for row in doc["modules"] for s in row["symbols"]]
    assert len(symbols) == doc["symbol_count"] == 428
    assert Counter(s["disposition"] for s in symbols) == doc["dispositions"]
    assert doc["dispositions"]["KEEP_REVIEWABLE_COLOCATION"] == 2
    assert doc["canonical_max_LOC"] == 337
    assert doc["protected_changes"] == []
    assert len(doc["whole_moves"]) == 14
    assert len(doc["named_transfers"]) == 8
    assert sum(len(s["functions"]) for s in doc["named_transfers"].values()) == 20


def test_m007_base_fixtures_are_exact_pinned_git_objects_not_checkout_line_endings():
    doc = json.loads(PATH.read_text(encoding="utf-8"))
    assert len(doc["fixtures"]) == 7
    assert sum(f["cases"] for f in doc["fixtures"]) == 420
    for row in doc["fixtures"]:
        raw = subprocess.check_output(["git", "show", doc["code_sha"] + ":" + row["path"]], cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest() == row["sha256"]
        assert len(raw) == row["bytes"]
        assert json.loads(raw) == json.loads((ROOT / row["path"]).read_text(encoding="utf-8"))


def test_m007_recorded_symbol_ast_is_the_current_source_not_a_fabricated_inventory():
    doc = json.loads(PATH.read_text(encoding="utf-8"))
    for row in doc["modules"]:
        found = {}
        for node in T._tree((ROOT / row["path"]).read_text(encoding="utf-8")).body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                found[node.name] = node
                if isinstance(node, ast.ClassDef):
                    found.update({node.name + "." + n.name: n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))})
        assert set(found) == {s["symbol"] for s in row["symbols"]}
        for symbol in row["symbols"]:
            node = found[symbol["symbol"]]
            assert hashlib.sha256(T._dump(node).encode()).hexdigest() == symbol["ast_sha256"]


def test_m007_generator_source_and_no_workflow_or_trade_authority_changes():
    doc = json.loads(PATH.read_text(encoding="utf-8"))
    source = ROOT / "scripts/refactor/work_monitor_scope_accounting.py"
    assert hashlib.sha256(source.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == doc["producer_sha256"]
    import work_monitor_scope_accounting as S
    assert subprocess.check_output(["git", "diff", "--name-only", doc["program_start"], "--", *S.PROTECTED], cwd=ROOT).strip() == b""
