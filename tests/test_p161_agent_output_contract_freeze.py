"""T3.5: BASE-frozen contract fixtures for `libs/contracts/agent_outputs.py`.

The golden files in `tests/fixtures/p1_5_t35_agent_outputs/` were generated ONCE on BASE `eb53dc1` (before any T3.5
change) from the existing offline suite plus a deterministic variant corpus. These tests replay the current tree:
exact public signatures, exact output bytes with field order, input non-mutation, runtime-dependency call trace and
single-key perturbation digests. Deterministic fixture parity only - NOT real Reporter/production artifact parity.
"""
import inspect
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "refactor"))
FIX = ROOT / "tests" / "fixtures" / "p1_5_t35_agent_outputs"

import p161_agent_output_freeze_tool as T  # noqa: E402
import p161_agent_output_freeze as F  # noqa: E402
import libs.contracts.agent_outputs as ao  # noqa: E402

BUILDERS = ("build_strategist_output_artifact", "build_scanner_output_artifact", "build_monitor_output_artifact",
            "build_commander_output_artifact")
# every 16th variant on the CI path; the stage-proof run uses the full corpus (`verify <dir>` with sample 1)
SAMPLE_MOD = 16


def _surface():
    return json.loads((FIX / "public_surface.json").read_text(encoding="utf-8"))


def test_public_signatures_names_and_constants_are_frozen_to_base():
    surface = _surface()
    now = {n: str(inspect.signature(f)) for n, f in sorted(vars(ao).items())
           if inspect.isfunction(f) and f.__module__ == ao.__name__ and not n.startswith("_")}
    assert now == surface["signatures"]
    public = sorted(n for n, v in vars(ao).items() if not n.startswith("_") and getattr(v, "__module__", ao.__name__) == ao.__name__)
    assert public == surface["public_names"]
    for k, v in surface["constants"].items():
        assert getattr(ao, k) == v


def test_golden_fixture_inventory_covers_all_four_large_builders():
    manifest = json.loads((FIX / "manifest.json").read_text(encoding="utf-8"))
    counts = manifest["counts"]
    for b in BUILDERS:
        assert counts[b] >= 16, (b, counts[b])
    assert manifest["variant_total"] >= 10000


def _pinned_base_tree(tmp_path):
    """The immutable BASE `libs/` tree (git archive of the pinned commit) - used only for portable replay."""
    import io
    import subprocess
    import tarfile
    data = subprocess.check_output(["git", "archive", "--format=tar", BASE_SHA, "libs"], cwd=ROOT)
    tree = tmp_path / "base_tree"
    tree.mkdir()
    with tarfile.open(fileobj=io.BytesIO(data)) as tf:
        try:
            tf.extractall(tree, filter="data")
        except TypeError:  # Python without the extraction-filter argument
            tf.extractall(tree)
    return tree


BASE_SHA = "eb53dc1fe56c2a70a21271faf2f3c25c9711e309"
# the golden fixtures were generated on Windows; any other host replays in portable mode (see verify() docstring)
PORTABLE = (os.name != "nt") or os.environ.get("T35_FIXTURE_MODE") == "portable"


def _git(*args):
    import subprocess
    return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()


def _compute_base_digests(tmp_path, fixture_dir=FIX, sample_mod=None):
    """Run the PINNED BASE tree in an isolated subprocess on this host and return (records, provenance)."""
    import subprocess
    tree = _pinned_base_tree(tmp_path)
    out = tmp_path / "base_digests.json"
    env = dict(os.environ, PYTHONPATH=str(tree))
    subprocess.run([sys.executable, str(ROOT / "scripts" / "refactor" / "p161_agent_output_freeze_tool.py"), "compute",
                    str(fixture_dir), str(sample_mod or SAMPLE_MOD), str(out)], cwd=str(tree), env=env, check=True,
                   timeout=1800)
    doc = json.loads(out.read_text(encoding="utf-8"))
    return doc["records"], doc["provenance"], tree


def test_native_mode_is_used_on_windows_when_required():
    """The hosted Windows gate sets T35_REQUIRE_NATIVE=1: it must run the NATIVE exact-golden replay, never portable."""
    if os.environ.get("T35_REQUIRE_NATIVE") == "1":
        assert os.name == "nt", "native T3.5 replay required but not running on Windows"
        assert PORTABLE is False, "native T3.5 replay required but portable mode is active"
        assert os.environ.get("T35_FIXTURE_MODE") in (None, "", "native")


def test_replay_matches_base_bytes_mutation_dependency_trace_and_variants(tmp_path):
    base_digests = None
    if PORTABLE:
        base_digests, prov, tree = _compute_base_digests(tmp_path)
        # provenance: the oracle ran from the isolated pinned-BASE archive, never from this checkout
        assert Path(prov["module_file"]).resolve().is_relative_to(tree.resolve()), prov
        assert not Path(prov["module_file"]).resolve().is_relative_to(ROOT.resolve()), prov
        assert _git("cat-file", "-t", BASE_SHA) == "commit"
        import subprocess
        pinned = subprocess.check_output(["git", "show", f"{BASE_SHA}:libs/contracts/agent_outputs.py"], cwd=ROOT)
        extracted = Path(prov["module_file"]).read_bytes()
        # `git archive` may apply the platform eol attribute; content must otherwise be the pinned blob
        crlf = bytes([13, 10])
        assert extracted.replace(crlf, bytes([10])) == pinned.replace(crlf, bytes([10])), "pinned BASE import provenance"
        golden, _ = T.load(FIX)
        assert len(golden) == 148 and set(base_digests) == {r["id"] for r in golden}
        # golden integrity is a SEPARATE accounting from the BASE<->FEATURE oracle
        errors, checked, bound = T.golden_integrity(golden, base_digests)
        assert errors == [], f"pinned BASE on this host != committed golden ({len(errors)}): {errors[:6]}"
        assert checked + bound == 148 and bound == 68 and checked == 80, (checked, bound)
    bad = T.verify(FIX, sample_mod=SAMPLE_MOD, portable=PORTABLE, base_digests=base_digests)
    kinds = {}
    for item in bad:
        k = (item[0].split("#")[0], item[1])
        kinds[k] = kinds.get(k, 0) + 1
    hints = [item for item in bad if item[1] != "variant"][:6]
    assert bad == [], f"{len(bad)} mismatches; by builder/kind={kinds}; first={hints}"


# ---- T3.5.1 portable oracle: exact BASE <-> FEATURE equality for every record --------------------------------------
def _mini_fixture(tmp_path, record_ids):
    """A fixture directory holding only the named committed records (golden files themselves are never touched)."""
    import gzip
    base, variants = T.load(FIX)
    sel = [r for r in base if r["id"] in record_ids]
    d = tmp_path / "mini_fixture"
    d.mkdir()
    with gzip.open(d / "golden_inputs_outputs.json.gz", "wt", encoding="utf-8") as fh:
        json.dump(sel, fh)
    with gzip.open(d / "golden_variant_digests.json.gz", "wt", encoding="utf-8") as fh:
        json.dump({r["id"]: variants[r["id"]] for r in sel}, fh)
    return d, sel


def _pick(builder, bound):
    base, _ = T.load(FIX)
    for r in base:
        if r["builder"] == builder and T.platform_bound([F.decode(r["args"]), F.decode(r["kwargs"])]) == bound:
            return r["id"]
    raise AssertionError((builder, bound))


def _swap_seps(o):
    """Simulated FEATURE regression that only changes path separators (toggles `/` <-> backslash in path-like strings)."""
    if isinstance(o, str):
        if "/" in o and set(o) <= T._PATH_CHARS:
            return o.replace("/", chr(92))
        if chr(92) in o and set(o) <= T._PATH_CHARS:
            return o.replace(chr(92), "/")
        return o
    if isinstance(o, list):
        return [_swap_seps(x) for x in o]
    if isinstance(o, dict):
        return {k: _swap_seps(v) for k, v in o.items()}
    return o


def _wrap(monkeypatch, builder, transform):
    original = getattr(ao, builder)

    def wrapper(*a, **k):
        return transform(original(*a, **k))
    monkeypatch.setattr(ao, builder, wrapper)


def _base_digests_here(fixture_dir):
    """BASE evidence for the mini fixture computed in-process from the CURRENT tree (identical to BASE for these
    stages; the subprocess/provenance path is covered by the replay test)."""
    return T.compute_digests(fixture_dir, sample_mod=SAMPLE_MOD)


def test_old_false_negative_is_closed_separator_only_regression_is_rejected(tmp_path, monkeypatch):
    """BASE `data/reports` vs FEATURE `data\\reports`: equal after normalisation, different exactly -> must FAIL."""
    base_value, feature_value = "data/reports", "data" + chr(92) + "reports"
    assert T.norm_seps(base_value) == T.norm_seps(feature_value)
    assert T.exact_sha({"p": base_value}) != T.exact_sha({"p": feature_value})
    # end-to-end on a real non-bound record: the old portable path (normalised golden) would have PASSED this
    rid = _pick("build_strategist_output_artifact", bound=False)
    fixture, sel = _mini_fixture(tmp_path, {rid})
    base_digests = _base_digests_here(fixture)
    assert T.verify(fixture, sample_mod=SAMPLE_MOD, portable=True, base_digests=base_digests) == []  # equal -> PASS
    with F.frozen_clock(ao):
        _k, baseline_out, _m = T._call(ao, sel[0]["builder"], F.decode(sel[0]["args"]), F.decode(sel[0]["kwargs"]))
    regressed = _swap_seps(F.encode(baseline_out))
    assert regressed != F.encode(baseline_out), "the simulated regression must change a path separator"
    # the OLD portable check (normalised comparison) would have accepted this FEATURE ...
    assert F.canonical(T.norm_seps(regressed)) == F.canonical(T.norm_seps(F.encode(baseline_out)))
    # ... while the exact digests differ
    assert T.exact_sha(regressed) != T.exact_sha(F.encode(baseline_out))
    changed = [True]

    def regress(out):
        res = _swap_seps(out)
        return res
    _wrap(monkeypatch, "build_strategist_output_artifact", regress)
    bad = T.verify(fixture, sample_mod=SAMPLE_MOD, portable=True, base_digests=base_digests)
    assert any(x[0] == rid and x[1] == "output_bytes" for x in bad), bad[:3]


@pytest.mark.parametrize("bound", [False, True])
def test_portable_oracle_uses_exact_equality_for_bound_and_non_bound_records(tmp_path, monkeypatch, bound):
    rid = _pick("build_supervisor_output_artifact" if bound else "build_strategist_output_artifact", bound)
    fixture, sel = _mini_fixture(tmp_path, {rid})
    base_digests = _base_digests_here(fixture)
    assert base_digests[rid]["bound"] is bound
    assert T.verify(fixture, sample_mod=SAMPLE_MOD, portable=True, base_digests=base_digests) == []
    builder = sel[0]["builder"]

    def mutate_number(out):
        out = json.loads(json.dumps(out))
        out["__t35_probe__"] = 1
        return out
    _wrap(monkeypatch, builder, mutate_number)
    assert any(x[0] == rid and x[1] == "output_bytes" for x in
               T.verify(fixture, sample_mod=SAMPLE_MOD, portable=True, base_digests=base_digests))


def test_portable_oracle_rejects_changed_value_and_changed_key_order(tmp_path, monkeypatch):
    rid = _pick("build_supervisor_output_artifact", bound=True)
    fixture, sel = _mini_fixture(tmp_path, {rid})
    base_digests = _base_digests_here(fixture)
    builder = sel[0]["builder"]
    original = getattr(ao, builder)

    def changed_value(*a, **k):
        out = original(*a, **k)
        for key, val in out.items():
            if isinstance(val, str) and val:
                out[key] = val + "x"
                break
        return out

    def reordered(*a, **k):
        out = original(*a, **k)
        keys = list(out)
        return {keys[-1]: out[keys[-1]], **{x: out[x] for x in keys[:-1]}}
    monkeypatch.setattr(ao, builder, changed_value)
    assert any(x[1] == "output_bytes" for x in T.verify(fixture, sample_mod=SAMPLE_MOD, portable=True, base_digests=base_digests))
    monkeypatch.setattr(ao, builder, reordered)
    assert any(x[1] == "output_bytes" for x in T.verify(fixture, sample_mod=SAMPLE_MOD, portable=True, base_digests=base_digests))


def test_portable_oracle_fails_closed_on_missing_or_malformed_base_evidence(tmp_path):
    rid = _pick("build_supervisor_output_artifact", bound=True)
    fixture, _sel = _mini_fixture(tmp_path, {rid})
    good = _base_digests_here(fixture)
    assert T.verify(fixture, sample_mod=SAMPLE_MOD, portable=True, base_digests=good) == []
    import copy
    for label, mutate in (
        ("missing_record", lambda d: d.pop(rid)),
        ("bad_sha", lambda d: d[rid].__setitem__("result_sha", "XYZ")),
        ("bad_kind", lambda d: d[rid].__setitem__("kind", "weird")),
        ("bad_shape", lambda d: d[rid].__setitem__("variants", [])),
        ("extra_record", lambda d: d.__setitem__("build_x#99", copy.deepcopy(d[rid]))),
    ):
        d = copy.deepcopy(good)
        mutate(d)
        assert T.verify(fixture, sample_mod=SAMPLE_MOD, portable=True, base_digests=d), label
    assert T.verify(fixture, sample_mod=SAMPLE_MOD, portable=True, base_digests=None), "None must fail closed"


def test_committed_golden_files_are_unchanged_since_the_freeze_commit():
    changed = _git("diff", "--name-only", "44333fdd225cea88dcc513c6cdc527fe84ff14f6", "HEAD", "--",
                   "tests/fixtures/p1_5_t35_agent_outputs/golden_inputs_outputs.json.gz",
                   "tests/fixtures/p1_5_t35_agent_outputs/golden_variant_digests.json.gz",
                   "tests/fixtures/p1_5_t35_agent_outputs/manifest.json",
                   "tests/fixtures/p1_5_t35_agent_outputs/public_surface.json")
    assert changed == "", changed


def test_commander_route_grid_covers_every_selected_route_and_blocked_reason_class():
    base, _ = T.load(FIX)
    rec = next(r for r in base if r["builder"] == "build_commander_output_artifact")
    args, kwargs = F.decode(rec["args"]), F.decode(rec["kwargs"])
    routes = set()
    for path in ("full_cycle", "monitor_only", "cached_strategist", "preopen", "closeout", "blocked"):
        k = dict(kwargs, path=path, status="ok")
        with F.frozen_clock(ao):
            routes.add(ao.build_commander_output_artifact(*[json.loads(json.dumps(args[0]))], **k)["selected_route"])
    assert {"full_cycle", "monitor_only", "cached_strategist", "preopen", "closeout", "blocked"} <= routes


def test_use_time_runtime_dependencies_are_resolved_through_the_facade_module(monkeypatch):
    """Replacing a runtime surface builder ON THE FACADE MODULE must change the artifact (monkeypatch seam)."""
    base, _ = T.load(FIX)
    rec = next(r for r in base if r["builder"] == "build_commander_output_artifact"
               and "build_commander_route_observability_surface" in r["dependency_trace"])
    args, kwargs = F.decode(rec["args"]), F.decode(rec["kwargs"])
    args[0].pop("commander_route_observability", None)
    sentinel = {"route_selected": "SENTINEL_ROUTE_T35", "strategist_call_decision": "SENTINEL_CALL"}
    monkeypatch.setattr(ao, "build_commander_route_observability_surface", lambda **_kw: dict(sentinel))
    with F.frozen_clock(ao):
        out = ao.build_commander_output_artifact(*args, **kwargs)
    assert out["route_selected"] == "SENTINEL_ROUTE_T35"
    assert out["route_observability"]["strategist_call_decision"] == "SENTINEL_CALL"


@pytest.mark.parametrize("name", BUILDERS)
def test_validation_block_is_produced_by_the_canonical_validate_artifact(name):
    base, _ = T.load(FIX)
    for rec in [r for r in base if r["builder"] == name][:6]:
        result = rec["result"]
        v = result["validation"]
        artifact = {k: val for k, val in F.decode(result).items() if k != "validation"}
        assert ao.validate_artifact(artifact) == F.decode(v)
