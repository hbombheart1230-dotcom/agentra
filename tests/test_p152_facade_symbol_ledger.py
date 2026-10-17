import ast
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json"
# Reporter R-4: the historical v1 ledger is pinned to the runtime BASE tree (unchanged expectations); the current HEAD is
# pinned by the versioned v2 ledger with the same strictness plus R-4 owner provenance.
BASE = "d773709ba2f70471fad9badba4f92400f7818319"
LEDGER_V2 = ROOT / "docs/refactor/work_projects/evidence/reporter/facade_symbol_ledger_v2.json"
R4 = ROOT / "docs/refactor/work_projects/evidence/reporter/r4_facade_ledger.json"


def _defs(text):
    return [(node.name, node.lineno) for node in ast.parse(text).body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]


def test_facade_ledger_covers_every_top_level_definition_without_declaring_dead():
    document = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert document["schema_version"] == "p152-facade-ledger-v1"
    assert len(document["files"]) == 3
    for row in document["files"]:
        text = subprocess.check_output(["git", "show", f"{BASE}:{row['path']}"], cwd=ROOT).decode("utf-8-sig")
        actual = _defs(text)
        expected = [(entry["name"], entry["start_line"]) for entry in row["symbols"]]
        assert actual == expected, row["path"]
        assert len(text.splitlines()) == row["physical_loc"]
        assert all(entry["disposition"] not in ("DEAD", "COMPLETE") for entry in row["symbols"])
        assert all(entry["current_consumer_proof"] == "NOT_RUN_LOCAL" for entry in row["symbols"])


def test_current_head_facade_ledger_v2_covers_every_definition_and_records_every_r4_move():
    v1 = json.loads(LEDGER.read_text(encoding="utf-8"))
    v2 = json.loads(LEDGER_V2.read_text(encoding="utf-8"))
    assert v2["schema_version"] == "p152-facade-ledger-v2-reporter" and v2["runtime_base"] == BASE
    assert [r["path"] for r in v2["files"]] == [r["path"] for r in v1["files"]]
    moves = {(m["path"], m["name"]): m["r4_owner"] for m in json.loads(R4.read_text(encoding="utf-8"))["moves"]}
    seen = set()
    for old, row in zip(v1["files"], v2["files"]):
        text = (ROOT / row["path"]).read_text(encoding="utf-8-sig")
        assert _defs(text) == [(e["name"], e["start_line"]) for e in row["symbols"]], row["path"]
        assert len(text.splitlines()) == row["physical_loc"]
        # no definition disappears, renames or changes kind/disposition (facade ABI kept)
        assert [(e["name"], e["kind"], e["disposition"]) for e in row["symbols"]] == \
            [(e["name"], e["kind"], e["disposition"]) for e in old["symbols"]], row["path"]
        for e in row["symbols"]:
            key = (row["path"], e["name"])
            assert e.get("r4_owner") == moves.get(key), key
            if key in moves:
                seen.add(key)
                assert (ROOT / e["r4_owner"]).is_file()
        assert all(e["disposition"] not in ("DEAD", "COMPLETE") for e in row["symbols"])
    assert seen == set(moves)
