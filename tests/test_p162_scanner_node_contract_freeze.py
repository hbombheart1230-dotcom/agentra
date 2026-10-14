"""T4-A: BASE-frozen deterministic contract of `graphs/nodes/scanner_node.py::scanner_node`.

Golden (generated once on BASE `11a11df`, before any T4-A change): for 73 captured scanner States (+ deterministic
candidate-pool scenarios: tie, rank-1 flip, order, duplicate, single/empty pool, and single-key perturbations) the
final State (canonical JSON, key order kept), the ordered effect/event evidence, exception and returned-object identity.
Native replay (Windows, the platform of the golden): exact committed digests. Other hosts (portable mode): the pinned
BASE tree (`git archive 11a11df libs graphs`) is executed on the same host and FEATURE must equal it exactly for every
record and sampled variant; golden integrity is accounted separately. Fail closed on missing/malformed oracle evidence.
Deterministic fixture parity only - NOT real Reporter/production artifact parity.
"""
import io
import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "refactor"))
FIX = ROOT / "tests" / "fixtures" / "p1_5_t4a_scanner_node"
BASE_SHA = "11a11df58f8d846cd9824fcb37eced521a57e887"
SAMPLE_MOD = 4
PORTABLE = (os.name != "nt") or os.environ.get("T4A_FIXTURE_MODE") == "portable"

import p162_scanner_node_freeze_tool as T  # noqa: E402


def _pinned_base_tree(tmp_path):
    data = subprocess.check_output(["git", "archive", "--format=tar", BASE_SHA, "libs", "graphs"], cwd=ROOT)
    tree = tmp_path / "base_tree"
    tree.mkdir()
    with tarfile.open(fileobj=io.BytesIO(data)) as tf:
        try:
            tf.extractall(tree, filter="data")
        except TypeError:
            tf.extractall(tree)
    return tree


def _compute(tree, tmp_path, name, fixture_dir=FIX, sample_mod=SAMPLE_MOD):
    """Digests of the implementation under `tree`, computed in an isolated subprocess with a pinned hash seed (the BASE
    scanner ranking depends on string-hash iteration order)."""
    out = tmp_path / f"{name}.json"
    paths = [str(tree)] if tree else [str(ROOT)]
    from libs.core.path_isolation import SESSION_MARKER_ENV, SESSION_ROOT_ENV
    # the parent runs under pytest: do not leak pytest/path-isolation markers into the replay process
    clean = {k: v for k, v in os.environ.items()
             if not k.startswith("PYTEST") and k not in (SESSION_MARKER_ENV, SESSION_ROOT_ENV)}
    env = dict(clean, PYTHONHASHSEED="0",
               PYTHONPATH=os.pathsep.join(paths + [str(ROOT / "scripts" / "refactor")]))
    subprocess.run([sys.executable, str(ROOT / "scripts" / "refactor" / "p162_scanner_node_freeze_tool.py"), "compute",
                    str(fixture_dir), str(sample_mod), str(out)], cwd=str(tree or ROOT), env=env, check=True, timeout=3000)
    doc = json.loads(out.read_text(encoding="utf-8"))
    return doc["records"], doc["provenance"]


def test_native_mode_is_used_on_windows_when_required():
    if os.environ.get("T4A_REQUIRE_NATIVE") == "1":
        assert os.name == "nt" and PORTABLE is False


def test_golden_inventory_covers_selection_tie_empty_pool_and_scenarios():
    man = json.loads((FIX / "manifest.json").read_text(encoding="utf-8"))
    assert man["records"] >= 70 and man["variants"] >= 1500 and man["effects_total"] >= 1000
    golden = T.load(FIX)
    states = [r["golden"]["state"] for r in golden]
    assert any(s.get("top_stock") for s in states), "no selected rank-1 scenario"
    assert any(not s.get("top_stock") for s in states), "no empty / non-selecting scenario"
    ids = {vid for r in golden for vid in r["variants"]}
    for needle in ("scenario:all_scores_tied", "scenario:swap_top_two_scores", "scenario:reverse_candidates",
                   "scenario:empty_candidates", "scenario:single_candidate", "scenario:duplicate_first_candidate"):
        assert needle in ids, needle
    assert all(len(r["golden"]["effects"]) >= 1 for r in golden)


def test_replay_matches_frozen_base_state_effect_order_and_variants(tmp_path):
    try:  # the Scanner q9 snapshot capture needs the IANA zone; without it the replay would silently differ
        import zoneinfo
        zoneinfo.ZoneInfo("Asia/Seoul")
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"tzdata prerequisite missing (pip install tzdata): {type(exc).__name__}: {exc}")
    golden = T.load(FIX)
    computed, prov = _compute(None, tmp_path, "feature")
    assert Path(prov["module_file"]).resolve().is_relative_to(ROOT.resolve()), prov
    if not PORTABLE:
        bad = T.compare_native(golden, computed)
    else:
        tree = _pinned_base_tree(tmp_path)
        oracle, bprov = _compute(tree, tmp_path, "base")
        assert Path(bprov["module_file"]).resolve().is_relative_to(tree.resolve()), bprov
        assert not Path(bprov["module_file"]).resolve().is_relative_to(ROOT.resolve()), bprov
        pinned = subprocess.check_output(["git", "show", f"{BASE_SHA}:graphs/nodes/scanner_node.py"], cwd=ROOT)
        crlf = bytes([13, 10])
        assert Path(bprov["module_file"]).read_bytes().replace(crlf, bytes([10])) == pinned.replace(crlf, bytes([10]))
        errors, checked, bound = T.golden_integrity(golden, oracle)
        assert errors == [], f"{len(errors)} golden-vs-BASE(host) integrity errors; first: {errors[:3]}"
        assert checked + bound == len(golden)
        bad = T.compare_portable(golden, computed, oracle)
    assert bad == [], f"{len(bad)} mismatches: {bad[:8]}"


def test_portable_oracle_rejects_separator_only_regression_and_fails_closed(tmp_path, monkeypatch):
    """The oracle compares exactly (no separator normalisation) and fails closed on missing/malformed evidence."""
    golden = T.load(FIX)
    assert T.validate_oracle(golden, None) and T.validate_oracle(golden, {})
    good = {r["id"]: {"state_sha": "0" * 64, "effects_sha": "1" * 64, "effects": [], "variants": {},
                      "returned_is_state": True, "exception": None} for r in golden}
    assert T.validate_oracle(golden, good) == []
    bad = dict(good)
    bad[golden[0]["id"]] = dict(good[golden[0]["id"]], state_sha="XYZ")
    assert T.validate_oracle(golden, bad)
    assert T.sha({"p": "data/reports"}) != T.sha({"p": "data" + chr(92) + "reports"})
    assert T.norm_seps({"p": "data" + chr(92) + "reports"}) == {"p": "data/reports"}


def test_committed_golden_is_unchanged_since_the_freeze_commit():
    freeze = (ROOT / "tests" / "fixtures" / "p1_5_t4a_scanner_node" / "FREEZE_COMMIT.txt").read_text(encoding="utf-8").strip()
    changed = subprocess.check_output(["git", "diff", "--name-only", freeze, "HEAD", "--",
                                       "tests/fixtures/p1_5_t4a_scanner_node/scanner_node_golden.json.gz",
                                       "tests/fixtures/p1_5_t4a_scanner_node/manifest.json"], cwd=ROOT).decode().strip()
    assert changed == "", changed
