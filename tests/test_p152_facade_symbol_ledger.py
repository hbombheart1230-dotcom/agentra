import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json"


def test_facade_ledger_covers_every_top_level_definition_without_declaring_dead():
    document = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert document["schema_version"] == "p152-facade-ledger-v1"
    assert len(document["files"]) == 3
    for row in document["files"]:
        path = ROOT / row["path"]
        text = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(text)
        actual = [(node.name, node.lineno) for node in tree.body
                  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        expected = [(entry["name"], entry["start_line"]) for entry in row["symbols"]]
        assert actual == expected, row["path"]
        assert len(text.splitlines()) == row["physical_loc"]
        assert all(entry["disposition"] not in ("DEAD", "COMPLETE") for entry in row["symbols"])
        assert all(entry["current_consumer_proof"] == "NOT_RUN_LOCAL" for entry in row["symbols"])
