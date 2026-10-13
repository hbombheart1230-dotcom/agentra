"""T3-0.1: the ownership matrix is reproducible from ONE reachable immutable commit and its flags are not conflated."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "refactor"))

import p159_ownership_matrix as M  # noqa: E402

JSON = ROOT / M.MATRIX_JSON


def _doc():
    return json.loads(JSON.read_text(encoding="utf-8"))


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)


def test_source_sha_is_a_reachable_commit_and_an_ancestor_of_head():
    sha = _doc()["source_sha"]
    assert len(sha) == 40
    assert _git("cat-file", "-t", sha).stdout.strip() == "commit"
    assert _git("merge-base", "--is-ancestor", sha, "HEAD").returncode == 0, "matrix source SHA is not reachable from HEAD"
    assert sha != "bcb83a6" and not sha.startswith("bcb83a6")


def test_every_row_exists_in_the_source_tree_and_rows_reproduce_exactly():
    doc = _doc()
    tree = set(_git("ls-tree", "-r", "--name-only", doc["source_sha"]).stdout.split("\n"))
    assert len(doc["rows"]) == len({r["module"] for r in doc["rows"]}) and len(doc["rows"]) >= 200
    for r in doc["rows"]:
        assert r["module"] in tree, r["module"]
    fresh = M.generate(doc["source_sha"])
    assert fresh["rows"] == doc["rows"], "committed matrix rows differ from a regeneration at the recorded source SHA"
    assert fresh["summary"] == doc["summary"]


def test_contract_and_rename_candidates_are_independent_flags_not_classes():
    doc = _doc()
    assert doc["schema"] == "p159_t3_ownership_matrix.v2"
    allowed = {"CANONICAL_OWNER", "COMPAT_FACADE", "SAFETY_LOCK", "KEEP", "UNKNOWN"}
    for r in doc["rows"]:
        assert r["class"] in allowed, r
        assert set(r["flags"]) <= {"CONTRACT_CANDIDATE", "RENAME_CANDIDATE"}
        if "CONTRACT_CANDIDATE" in r["flags"]:
            assert r["max_unconverted_output_arity"] > 8
        if r["max_unconverted_output_arity"] > 8:
            assert "CONTRACT_CANDIDATE" in r["flags"]
        if "RENAME_CANDIDATE" in r["flags"]:
            assert r["generated_name_functions"] > 0
    # a module can carry both flags independently; the counts are reported separately
    assert set(doc["summary"]["flags"]) <= {"CONTRACT_CANDIDATE", "RENAME_CANDIDATE"}


def test_generation_procedure_and_tree_delta_are_recorded_and_the_overlay_names_the_same_commit():
    doc = _doc()
    g = doc["generator"]
    assert "p159_ownership_matrix.py" in g["command"] and doc["source_sha"] in g["command"]
    assert g["verify"].endswith("--verify") and len(g["script_sha256"]) == 64
    delta = doc["tree_delta"]
    assert delta["from"] == doc["source_sha"] and isinstance(delta["production_paths_changed"], list)
    overlay = (ROOT / M.OVERLAY_DOC).read_text(encoding="utf-8")
    assert f"verified against Git commit `{doc['source_sha']}`" in overlay
    assert "bcb83a6" not in overlay[overlay.index("## G. Current status overlay"):]
    md = (ROOT / M.MATRIX_MD).read_text(encoding="utf-8")
    assert doc["source_sha"] in md and "--verify" in md


def test_no_module_was_created_or_removed_only_to_match_the_historical_design():
    doc = _doc()
    overlay = (ROOT / M.OVERLAY_DOC).read_text(encoding="utf-8")
    assert "do NOT create without a genuine responsibility" in overlay
    assert not any(r["module"].endswith("scanner/ranking_core.py") for r in doc["rows"])
