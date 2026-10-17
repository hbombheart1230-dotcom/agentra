"""M9 closes the unexecuted native mod1 gap without rerunning old mod4 suites."""
import hashlib
import json
import os
import socket
import importlib.util
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/refactor"))
import p163_monitor_freeze_tool as T


def test_m9_native_entire_variant_inventory_exact_and_offline(tmp_path):
    fix = ROOT / "tests/fixtures/p1_5_t4b_monitor"
    golden = T.load(fix)
    manifest = json.loads((fix / "manifest.json").read_text(encoding="utf-8"))
    started = time.perf_counter()
    # Use the UNCHANGED native gate's child-process/bootstrap contract, not an
    # in-process pytest replay whose session env alters canonical artifact paths.
    spec = importlib.util.spec_from_file_location("m9_original_native_gate", ROOT / "tests/test_p163_monitor_contract_freeze.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    actual, provenance = gate._compute(None, tmp_path, "m9_full", sample_mod=1)
    if os.name == "nt":
        errors = T.compare_native(golden, actual, 1, manifest)
    else:
        base_tree = gate._pinned_base_tree(tmp_path)
        oracle, base_provenance = gate._compute(base_tree, tmp_path, "m9_base_full", sample_mod=1)
        assert Path(base_provenance["module_file"]).resolve().is_relative_to(base_tree)
        integrity, checked, bound = T.golden_integrity(golden, oracle)
        assert integrity == [] and checked + bound == len(golden)
        errors = T.compare_portable(golden, actual, oracle, 1, manifest)
    counts = {"records": len(actual), "variants": sum(len(v["variants"]) for v in actual.values()),
              "effects": sum(len(v["effects"]) for v in actual.values())}
    evidence = {"schema": "monitor.m9.native_full.v1", "source_sha": "800841f229606c419dae67b0d6f794b9238676e9",
                "python": sys.version, "platform": sys.platform, "mode": "native" if os.name == "nt" else "same-host-pinned-base", "sample_mod": 1, **counts,
                "mismatches": len(errors), "first_mismatches": errors[:8], "provenance": provenance,
                "network_guard": "Existing T4-B _freeze_globals rejects socket.connect; no live callbacks introduced.",
                "seconds": time.perf_counter() - started,
                "fixture_sha256": hashlib.sha256((fix / "monitor_golden.json.gz").read_bytes()).hexdigest(),
                "claim": "Synthetic native contract/effect parity; NOT real report/LLM parity."}
    output = Path(os.environ.get("MONITOR_M9_EVIDENCE", str(tmp_path / "m9_full_summary.json")))
    if not output.is_absolute() or output.is_relative_to(ROOT):
        raise AssertionError("M9 evidence must be externally isolated")
    output.write_text(json.dumps(evidence, separators=(",", ":")), encoding="utf-8")
    assert Path(provenance["module_file"]).resolve().is_relative_to(ROOT)
    assert counts == {"records": 149, "variants": 2879, "effects": 1541}
    assert errors == [], errors[:8]
