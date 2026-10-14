"""T3.5: BASE-frozen contract fixtures for `libs/contracts/agent_outputs.py`.

The golden files in `tests/fixtures/p1_5_t35_agent_outputs/` were generated ONCE on BASE `eb53dc1` (before any T3.5
change) from the existing offline suite plus a deterministic variant corpus. These tests replay the current tree:
exact public signatures, exact output bytes with field order, input non-mutation, runtime-dependency call trace and
single-key perturbation digests. Deterministic fixture parity only - NOT real Reporter/production artifact parity.
"""
import inspect
import json
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


def test_replay_matches_base_bytes_mutation_dependency_trace_and_variants():
    bad = T.verify(FIX, sample_mod=SAMPLE_MOD)
    assert bad == [], bad[:10]


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
