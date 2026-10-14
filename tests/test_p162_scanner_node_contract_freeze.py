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
    assert doc["sample_mod"] == sample_mod
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
        bad = T.compare_native(golden, computed, SAMPLE_MOD, _manifest())
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
        bad = T.compare_portable(golden, computed, oracle, SAMPLE_MOD, _manifest())
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


# ---- T4-A.1 strict variant conservation ---------------------------------------------------------------------------
import copy  # noqa: E402


def _legacy_compare_native(golden, computed):
    """VERBATIM logic of the T4-A comparator (before T4-A.1): iterates the COMPUTED variants only."""
    bad = []
    for rec in golden:
        c = computed.get(rec["id"])
        if c is None:
            bad.append((rec["id"], "not_computed"))
            continue
        for vid, got in c["variants"].items():
            if rec["variants"].get(vid) != got:
                bad.append((rec["id"], "variant", vid))
    return bad


def _legacy_compare_portable(golden, computed, oracle):
    """VERBATIM variant logic of the T4-A portable comparator: set(oracle ids) != set(computed ids) only."""
    bad = []
    for rec in golden:
        c, o = computed[rec["id"]], oracle[rec["id"]]
        if set(o["variants"]) != set(c["variants"]):
            bad.append((rec["id"], "variant_selection"))
        for vid, got in c["variants"].items():
            if o["variants"].get(vid) != got:
                bad.append((rec["id"], "variant", vid))
    return bad


def _synthetic(golden, sample_mod):
    """computed / oracle structures that conserve every expected sampled variant (built from the committed golden)."""
    comp = {}
    for r in golden:
        g = r["golden"]
        keep = T.expected_sample_ids(r, sample_mod)
        comp[r["id"]] = {"state_sha": g["state_sha"], "effects_sha": g["effects_sha"], "exception": g["exception"],
                         "returned_is_state": g["returned_is_state"], "effects": g["effects"],
                         "variants": {v: list(r["variants"][v]) for v in keep}, "bound": r["bound"]}
    return comp


def _pick_record(golden, sample_mod):
    for r in golden:
        if len(T.expected_sample_ids(r, sample_mod)) >= 2:
            return r
    raise AssertionError("no record with >= 2 expected sampled variants")


def test_variant_conservation_old_false_negative_is_reproduced_and_rejected_by_both_comparators():
    golden, man = T.load(FIX), _manifest()
    feature = _synthetic(golden, SAMPLE_MOD)
    oracle = copy.deepcopy(feature)
    rec = _pick_record(golden, SAMPLE_MOD)
    victim = sorted(T.expected_sample_ids(rec, SAMPLE_MOD))[0]
    # a valid, complete execution passes everywhere
    assert T.compare_native(golden, feature, SAMPLE_MOD, man) == []
    assert T.compare_portable(golden, feature, oracle, SAMPLE_MOD, man) == []
    # FEATURE silently omits an expected variant while every remaining digest matches
    dropped = copy.deepcopy(feature)
    del dropped[rec["id"]]["variants"][victim]
    assert _legacy_compare_native(golden, dropped) == [], "the OLD native comparator accepted the omission (false negative)"
    assert any(e[0] == rec["id"] and "variant_ids_ne_expected_sample" in e[1]
               for e in T.compare_native(golden, dropped, SAMPLE_MOD, man))
    # BASE and FEATURE both omit it: the old portable comparator saw equal ID sets
    both = copy.deepcopy(oracle)
    del both[rec["id"]]["variants"][victim]
    assert _legacy_compare_portable(golden, dropped, both) == [], "OLD portable comparator accepted the omission"
    errs = T.compare_portable(golden, dropped, both, SAMPLE_MOD, man)
    assert any(e[0] == rec["id"] and "variant_ids_ne_expected_sample" in e[1] for e in errs)


def test_variant_inventory_rejects_missing_extra_malformed_and_manifest_mismatch():
    golden, man = T.load(FIX), _manifest()
    feature = _synthetic(golden, SAMPLE_MOD)
    oracle = copy.deepcopy(feature)
    rec = _pick_record(golden, SAMPLE_MOD)
    rid = rec["id"]
    victim = sorted(T.expected_sample_ids(rec, SAMPLE_MOD))[0]

    def native(f, g=golden, m=man):
        return T.compare_native(g, f, SAMPLE_MOD, m)

    def portable(f, o, g=golden, m=man):
        return T.compare_portable(g, f, o, SAMPLE_MOD, m)

    # missing expected variant in FEATURE (native + portable) / in pinned BASE (portable)
    f = copy.deepcopy(feature)
    del f[rid]["variants"][victim]
    assert native(f) and portable(f, oracle)
    o = copy.deepcopy(oracle)
    del o[rid]["variants"][victim]
    assert portable(feature, o)
    # extra unexpected variant (an ID outside the expected sample) in FEATURE / BASE / both
    outside = sorted(set(T.variant_inventory(rec)) - T.expected_sample_ids(rec, SAMPLE_MOD))[0]
    f = copy.deepcopy(feature)
    f[rid]["variants"][outside] = list(rec["variants"][outside])
    assert native(f) and portable(f, oracle)
    o = copy.deepcopy(oracle)
    o[rid]["variants"][outside] = list(rec["variants"][outside])
    assert portable(feature, o)
    f = copy.deepcopy(feature)
    f[rid]["variants"]["unknown:variant"] = list(rec["variants"][victim])
    assert native(f)
    # equal ID sets but a changed digest
    f = copy.deepcopy(feature)
    f[rid]["variants"][victim][0] = "0" * 64
    assert any(e[1] == "variant" for e in native(f))
    assert any(e[1] == "variant" for e in portable(f, oracle))
    # malformed rows / not-a-dict
    f = copy.deepcopy(feature)
    f[rid]["variants"][victim] = ["x"]
    assert native(f)
    f = copy.deepcopy(feature)
    f[rid]["variants"] = [victim]
    assert native(f) and portable(f, oracle)
    # synthetic copy of the frozen golden missing a variant (inventory not conserved)
    g2 = copy.deepcopy(golden)
    del next(r for r in g2 if r["id"] == rid)["variants"][victim]
    assert any("golden_variant_inventory_mismatch" in e[1] for e in native(feature, g=g2))
    assert any("golden_variant_inventory_mismatch" in e[1] for e in portable(feature, oracle, g=g2))
    # golden record removed / duplicated record id
    assert native(feature, g=golden[:-1])
    assert native(feature, g=golden + [golden[0]])
    # manifest counts corrupt / inconsistent
    for key in ("records", "variants"):
        m2 = dict(man)
        m2[key] = man[key] + 1
        assert native(feature, m=m2) and portable(feature, oracle, m=m2)
    # computed record set inconsistent
    f = copy.deepcopy(feature)
    f.pop(rid)
    assert native(f) and portable(f, oracle)


def test_valid_complete_fixture_and_full_sample_pass_variant_conservation():
    golden, man = T.load(FIX), _manifest()
    assert T.inventory_errors(golden, man) == []
    assert man["records"] == 73 and man["variants"] == 1575
    assert sum(len(r["variants"]) for r in golden) == 1575
    for mod in (SAMPLE_MOD, 1):
        feature = _synthetic(golden, mod)
        oracle = copy.deepcopy(feature)
        assert T.compare_native(golden, feature, mod, man) == []
        assert T.compare_portable(golden, feature, oracle, mod, man) == []
    full = _synthetic(golden, 1)
    assert sum(len(v["variants"]) for v in full.values()) == 1575
    # sampling is a strict subset for sample_mod=4 (the inventory and the executed set are different concepts)
    part = _synthetic(golden, SAMPLE_MOD)
    assert 0 < sum(len(v["variants"]) for v in part.values()) < 1575
