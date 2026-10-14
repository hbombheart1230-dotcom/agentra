"""T4-B: BASE-frozen deterministic contract of the Monitor targets.

Golden (generated once on BASE `c338ba3`, before any T4-B implementation change): 149 captured inputs of
`monitor_node` (State in/out + ordered effects), `_evaluate_monitor_entry_candidate` and `evaluate_exit_policy`
(keyword inputs -> result + mutated inputs) plus deterministic single-key perturbations and guard/price scenarios.
Native replay (Windows, the platform of the golden): exact committed digests. Other hosts: the pinned BASE tree
(`git archive` of the BASE commit) is executed on the same host and FEATURE must equal it exactly for every record and
sampled variant; golden integrity is accounted separately. Strict variant conservation (expected sampled IDs ==
BASE IDs == FEATURE IDs, inventory re-derived, manifest totals) and fail-closed oracle validation.
Deterministic fixture parity only - NOT real Reporter/production artifact parity.
"""
import copy
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
FIX = ROOT / "tests" / "fixtures" / "p1_5_t4b_monitor"
BASE_SHA = "c338ba34276566b0b5f6de1e7f556778ec917968"
SAMPLE_MOD = 4
PORTABLE = (os.name != "nt") or os.environ.get("T4B_FIXTURE_MODE") == "portable"

import p163_monitor_freeze_tool as T  # noqa: E402


def _manifest():
    return json.loads((FIX / "manifest.json").read_text(encoding="utf-8"))


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


def _compute(tree, tmp_path, name, sample_mod=SAMPLE_MOD):
    from libs.core.path_isolation import SESSION_MARKER_ENV, SESSION_ROOT_ENV
    out = tmp_path / f"{name}.json"
    clean = {k: v for k, v in os.environ.items()
             if not k.startswith("PYTEST") and k not in (SESSION_MARKER_ENV, SESSION_ROOT_ENV)}
    paths = [str(tree)] if tree else [str(ROOT)]
    env = dict(clean, PYTHONHASHSEED="0", PYTHONPATH=os.pathsep.join(paths + [str(ROOT / "scripts" / "refactor")]))
    subprocess.run([sys.executable, str(ROOT / "scripts" / "refactor" / "p163_monitor_freeze_tool.py"), "compute",
                    str(FIX), str(sample_mod), str(out)], cwd=str(tree or ROOT), env=env, check=True, timeout=3000)
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["sample_mod"] == sample_mod
    return doc["records"], doc["provenance"]


def test_native_mode_is_used_on_windows_when_required():
    if os.environ.get("T4B_REQUIRE_NATIVE") == "1":
        assert os.name == "nt" and PORTABLE is False


def test_golden_inventory_covers_the_three_monitor_targets_and_scenarios():
    man = _manifest()
    assert man["records"] >= 140 and man["variants"] >= 2500 and man["effects_total"] >= 1000
    for t in ("monitor_node", "entry_candidate", "exit_policy"):
        assert man["by_target"][t] >= 40, t
    golden = T.load(FIX)
    ids = {vid for r in golden for vid in r["variants"]}
    assert any(v.startswith("scenario:price_") for v in ids) and any(v.startswith("scenario:execution_pending") for v in ids)
    assert any(v.startswith("scenario:qty_zero") for v in ids)


def test_replay_matches_frozen_base_result_mutation_effect_order_and_variants(tmp_path):
    try:
        import zoneinfo
        zoneinfo.ZoneInfo("Asia/Seoul")
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"tzdata prerequisite missing (pip install tzdata): {type(exc).__name__}: {exc}")
    golden = T.load(FIX)
    computed, prov = _compute(None, tmp_path, "feature")
    assert Path(prov["module_file"]).resolve().is_relative_to(ROOT.resolve()), prov
    if not PORTABLE:
        bad = T.compare_native(golden, computed, SAMPLE_MOD, _manifest())
    else:
        tree = _pinned_base_tree(tmp_path)
        oracle, bprov = _compute(tree, tmp_path, "base")
        assert Path(bprov["module_file"]).resolve().is_relative_to(tree.resolve()), bprov
        pinned = subprocess.check_output(["git", "show", f"{BASE_SHA}:graphs/nodes/monitor_node.py"], cwd=ROOT)
        crlf = bytes([13, 10])
        assert Path(bprov["module_file"]).read_bytes().replace(crlf, bytes([10])) == pinned.replace(crlf, bytes([10]))
        errors, checked, bound = T.golden_integrity(golden, oracle)
        assert errors == [], f"{len(errors)} golden-vs-BASE(host) integrity errors: {errors[:3]}"
        assert checked + bound == len(golden)
        bad = T.compare_portable(golden, computed, oracle, SAMPLE_MOD, _manifest())
    assert bad == [], f"{len(bad)} mismatches: {bad[:8]}"


def _synthetic(golden, sample_mod):
    comp = {}
    for r in golden:
        g = r["golden"]
        keep = T.expected_sample_ids(r, sample_mod)
        comp[r["id"]] = {"out_sha": g["out_sha"], "effects_sha": g["effects_sha"], "exception": g["exception"],
                         "returned_is_input": g["returned_is_input"], "effects": g["effects"],
                         "variants": {v: list(r["variants"][v]) for v in keep}, "bound": r["bound"]}
    return comp


def test_variant_conservation_and_oracle_fail_closed_negative_cases():
    golden, man = T.load(FIX), _manifest()
    feature = _synthetic(golden, SAMPLE_MOD)
    oracle = copy.deepcopy(feature)
    assert T.compare_native(golden, feature, SAMPLE_MOD, man) == []
    assert T.compare_portable(golden, feature, oracle, SAMPLE_MOD, man) == []
    rec = next(r for r in golden if len(T.expected_sample_ids(r, SAMPLE_MOD)) >= 2)
    rid = rec["id"]
    victim = sorted(T.expected_sample_ids(rec, SAMPLE_MOD))[0]
    f = copy.deepcopy(feature)
    del f[rid]["variants"][victim]                      # omission with every remaining digest equal
    assert T.compare_native(golden, f, SAMPLE_MOD, man) and T.compare_portable(golden, f, oracle, SAMPLE_MOD, man)
    o = copy.deepcopy(oracle)
    del o[rid]["variants"][victim]
    assert T.compare_portable(golden, feature, o, SAMPLE_MOD, man)
    f = copy.deepcopy(feature)
    f[rid]["variants"][victim][0] = "0" * 64            # equal ID set, changed digest
    assert any(e[1] == "variant" for e in T.compare_native(golden, f, SAMPLE_MOD, man))
    g2 = copy.deepcopy(golden)
    del next(r for r in g2 if r["id"] == rid)["variants"][victim]
    assert T.compare_native(g2, feature, SAMPLE_MOD, man)
    m2 = dict(man)
    m2["variants"] = man["variants"] + 1
    assert T.compare_native(golden, feature, SAMPLE_MOD, m2)
    assert T.validate_oracle(golden, None) and T.validate_oracle(golden, {})
    sep_only = {"p": "data/reports"}, {"p": "data" + chr(92) + "reports"}
    assert T.norm_seps(sep_only[1]) == sep_only[0] and T.sha(sep_only[0]) != T.sha(sep_only[1])


def test_committed_golden_is_unchanged_since_the_freeze_commit():
    freeze = (FIX / "FREEZE_COMMIT.txt").read_text(encoding="utf-8").strip()
    changed = subprocess.check_output(["git", "diff", "--name-only", freeze, "HEAD", "--",
                                       "tests/fixtures/p1_5_t4b_monitor/monitor_golden.json.gz",
                                       "tests/fixtures/p1_5_t4b_monitor/manifest.json"], cwd=ROOT).decode().strip()
    assert changed == "", changed
