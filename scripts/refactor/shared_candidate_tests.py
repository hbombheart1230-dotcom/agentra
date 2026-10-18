"""Explicit mock-only matrix; every invocation owns verified ignored worktree scratch."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from importlib.metadata import version

ROOT = Path(__file__).resolve().parents[2]
SUITES = {
    "shared": [
        "test_shared_reporter_facade_guard.py", "test_shared_role_contracts.py", "test_shared_stage_provenance.py",
        "test_p152_integration_acceptance_inventory.py", "test_patch_notes_sync.py", "apps/api/test_patch_notes.py",
        "apps/api/test_isolation.py",  # Keep API paths together: pytest 9.1 conftest fixture visibility.
        "test_shared_strategist_contracts.py", "test_p172_strategist_s1_057_migration.py",
        "test_p15_strategist_s5_helper_moves.py", "test_p164_strategist_contract_freeze.py",
        "test_p173_p058_integration_contracts.py",
    ],
    "reporter": [
        "test_work_reporter_seed_migration.py", "test_work_reporter_r4_facade_bodies.py",
        "test_work_reporter_r8_read_contracts.py", "test_work_reporter_r8_read_via_callback_parity.py",
        "test_work_reporter_renderer_bytes.py", "test_work_reporter_r10_retained_io_contracts.py",
        "test_work_reporter_r10_artifact_parity.py", "test_work_reporter_r11_repo_hygiene.py",
        "test_p152_facade_symbol_ledger.py",
    ],
    "monitor": [
        "test_work_monitor_role_contracts.py", "test_work_monitor_continuous.py", "test_work_monitor_body_views.py",
        "test_work_monitor_observation_views.py", "test_work_monitor_exit_labels.py", "test_work_monitor_policy_trace_views.py",
        "test_work_monitor_annotation_views.py", "test_work_monitor_scope_accounting.py",
        "test_work_monitor_retained_boundary.py", "test_work_monitor_m9_offline.py",
        "test_monitor_evidence_ast.py",
        "test_m17_monitor_emits_intent_only.py", "test_monitor_candidate_cascade.py",
        "test_m29_4_monitor_position_sizing.py", "test_monitor_exit_guard.py",
        "test_monitor_exit_price_freshness.py", "test_monitor_price_source_resolution.py",
    ],
    "structural": [
        "test_p157_third_pass_t1_extraction_gates.py", "test_p158_third_pass_t2_extraction_gates.py",
        "test_p159_current_owner_contract_gates.py", "test_p159_static_purity_closure.py",
        "test_p159_ownership_matrix_provenance.py", "test_p161_t35_extraction_gates.py",
        "test_p162_t4a_extraction_gates.py", "test_p163_t4b_extraction_gates.py",
        "test_p164_t4c_extraction_gates.py", "test_p165_t4d_extraction_gates.py",
        "test_uef1_work_package_a_canonical_contract.py", "test_uef9_formal_authority.py",
        "test_scanner_candidate_risk.py", "test_p168_wave_b_shim_verifier_negatives.py",
    ],
    "native": ["test_work_monitor_m9_native.py"],
    "api": ["apps/api/test_isolation.py"],
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=[*SUITES, "all"], default="all")
    parser.add_argument("--optimized", action="store_true")
    parser.add_argument("--extra-site", help="Read-only dependency site for isolated API version probe")
    args = parser.parse_args()
    selected = list(SUITES)[:-1] if args.suite == "all" else [args.suite]
    paths = list(dict.fromkeys("tests/" + p for s in selected for p in SUITES[s]))
    missing = [p for p in paths if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit("Missing required tests: " + repr(missing))
    scratch = ROOT / ".agentra-worktmp"
    subprocess.run(["git", "check-ignore", "-q", ".agentra-worktmp/probe"], cwd=ROOT, check=True)
    scratch.mkdir(exist_ok=True)
    if scratch.is_symlink() or not scratch.resolve().is_relative_to(ROOT.resolve()):
        raise SystemExit("Untrusted scratch root")
    output = Path(tempfile.mkdtemp(prefix="shared-", dir=scratch))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
            stream.write("evidence=" + str(output) + "\n")
    env = dict(os.environ, TEMP=str(output), TMP=str(output), TMPDIR=str(output),
               DRY_RUN="1", TRADING_MODE="mock", PYTHONDONTWRITEBYTECODE="1")
    if args.optimized:
        env["PYTHONOPTIMIZE"] = "1"  # Also exercise fresh child interpreters under -O.
    for key in ("TRADING_AGENT_PYTEST_ROOT", "TRADING_AGENT_PYTEST"):
        env.pop(key, None)
    command = [sys.executable] + (["-O"] if args.optimized else [])
    if args.extra_site:
        bootstrap = "import sys; sys.path.append(" + repr(args.extra_site) + "); import pytest; raise SystemExit(pytest.main(sys.argv[1:]))"
        command += ["-c", bootstrap]
    else:
        command += ["-m", "pytest"]
    command += ["-q", "--tb=short", "-p", "no:cacheprovider", *paths, "--junitxml=" + str(output / "junit.xml")]
    print("OUTPUT=" + str(output), flush=True)
    result = subprocess.run(command, cwd=ROOT, env=env)
    summary = {"command": command, "exit": result.returncode, "suite": args.suite,
               "optimized": args.optimized, "python": sys.version,
               "fastapi": version("fastapi"),
               "sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "scratch": str(output), "retention": "Failed evidence retained for at most seven days; owner cleanup only."}
    if (output / "junit.xml").is_file():
        tree = ET.parse(output / "junit.xml")
        summary["counts"] = {k: sum(int(s.get(k, "0")) for s in tree.findall(".//testsuite"))
                             for k in ("tests", "failures", "errors", "skipped")}
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary), flush=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
