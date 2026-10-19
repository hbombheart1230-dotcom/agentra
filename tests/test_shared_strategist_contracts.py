"""Prove the proposed S5 contract on Git blobs without installing S5 source."""
import ast
import copy
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.refactor import shared_strategist_contracts as S5

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/refactor"))
import shared_role_contracts as SHARED


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_exact_candidate_restores_the_entire_original_ast_without_installing_it(newline):
    sources = {p: s.replace("\n", newline) for p, s in S5.candidate_sources().items()}
    assert S5.dump(S5.restore_candidate(sources)) == S5.dump(ast.parse(S5.git_source(S5.SOURCE, S5.NODE)))
    assert len(S5.MOVED) == 8 and len(S5.import_pairs()) == 8 and len(S5.OWNERS) == 2


@pytest.mark.parametrize("name", sorted(S5.MOVED))
@pytest.mark.parametrize("kind", ["body", "default", "facade"])
def test_each_wrapper_rejects_body_abi_and_facade_mutations(name, kind):
    sources = S5.candidate_sources()
    tree = ast.parse(sources[S5.NODE])
    fn = S5.functions(tree)[name]
    if kind == "body":
        fn.body = ast.parse("return None").body
    elif kind == "default":
        fn.args.defaults.append(ast.Constant(value=None))
    else:
        fn.body[0].value.keywords[0].value = ast.Constant(value=None)
    sources[S5.NODE] = ast.unparse(tree)
    with pytest.raises(AssertionError):
        S5.restore_candidate(sources)


@pytest.mark.parametrize("kind", ["unmoved", "module_statement", "import_extra", "import_missing",
                                  "import_alias", "import_duplicate", "import_relative", "function_added"])
def test_unmoved_definitions_and_arbitrary_imports_cannot_hide_in_restoration(kind):
    sources = S5.candidate_sources()
    tree = ast.parse(sources[S5.NODE])
    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom) and n.module == S5.VALUE[:-3].replace("/", ".")]
    node = imports[0]
    if kind == "unmoved":
        S5.functions(tree)["_env_bool"].body = ast.parse("return True").body
    elif kind == "module_statement":
        tree.body.append(ast.parse("BROKER_CAPABILITY = True").body[0])
    elif kind == "function_added":
        tree.body.extend(ast.parse("def _rogue():\n return True").body)
    elif kind == "import_extra":
        node.names.append(ast.alias(name="_env_int_r3_impl"))
    elif kind == "import_missing":
        node.names.pop()
    elif kind == "import_alias":
        node.names[0].asname = "_rogue"
    elif kind == "import_duplicate":
        tree.body.append(copy.deepcopy(node))
    else:
        node.level = 1
    sources[S5.NODE] = ast.unparse(tree)
    with pytest.raises(AssertionError):
        S5.restore_candidate(sources)


@pytest.mark.parametrize("owner", sorted(S5.OWNERS))
def test_each_owner_is_exact_not_an_open_package_allowlist(owner):
    sources = S5.candidate_sources()
    sources[owner] += "\nimport os\n"
    with pytest.raises(AssertionError):
        S5.restore_candidate(sources)


def test_missing_and_additional_source_paths_are_rejected():
    for change in ("missing", "additional"):
        sources = S5.candidate_sources()
        if change == "missing":
            sources.pop(S5.TEXT)
        else:
            sources["libs/runtime/strategist/llm/rogue.py"] = "pass"
        with pytest.raises(AssertionError):
            S5.restore_candidate(sources)


def test_unreviewed_candidate_cannot_enter_the_current_runtime(monkeypatch):
    monkeypatch.setattr(S5, "ADMITTED_CODE", None)
    with pytest.raises(AssertionError, match="auditor PASS/admission pending"):
        SHARED.verify_runtime(S5.candidate_sources())


def test_future_exact_admission_branch_is_exercised_only_in_memory(monkeypatch):
    # Simulate a future approval to test contracts; never writes the pin or sources.
    monkeypatch.setattr(S5, "ADMITTED_CODE", S5.CANDIDATE_CODE)
    sources = S5.candidate_sources()
    S5.current_contract(sources)  # immutable historic candidate still independently admitted
    result = SHARED.verify_runtime()  # actual new stage, not an old-node override
    assert result["moves"] == 313 and result["monitor_bodies"] == 20
    for path in ["libs/broker/rogue.py", "libs/executor/rogue.py", "libs/supervisor/rogue.py",
                 "libs/runtime/strategist/context/rogue.py"]:
        with pytest.raises(AssertionError):
            SHARED.verify_runtime({path: "CAPABILITY = True\n"})


@pytest.mark.parametrize("path", ["libs/broker/rogue.py", "libs/executor/rogue.py", "libs/supervisor/rogue.py",
                                  "tests/test_uef9_unapproved_policy.py", "graphs/nodes/decide_trade.py",
                                  "docs/unapproved.md", "tests/fixtures/p1_5_t4c_strategist/golden.json"])
def test_reanchored_scope_keeps_changed_and_untracked_path_limits(path):
    for changed, untracked in (([path], []), ([], [path])):
        with pytest.raises(AssertionError):
            S5.verify_integration_scope(changed, untracked)


def test_prepared_integrated_scope_uses_exact_source_and_shared_paths():
    assert S5.verify_integration_scope(sorted(S5.S5_PATHS | S5.SHARED_PATHS), []) == S5.S5_PATHS | S5.SHARED_PATHS
    S5.verify_integration_scope()  # Pinned S5 source stage plus post-acceptance code freeze.


def test_latest_documents_do_not_reclassify_historical_source_changes():
    assert S5.verify_next_scope() == S5.NEXT_PATHS
    assert S5.ACCEPTED_SOURCE_INTEGRATION == "a50d6e4780ddccd810fb0708e756e1bf63d8ede0"


@pytest.mark.parametrize("path", [
    "libs/broker/rogue.py", "libs/supervisor/rogue.py", "libs/executor/rogue.py",
    "graphs/nodes/execute_from_packet.py", "apps/operator_ui/rogue.py",
    "scripts/refactor/rogue.py", "tests/fixtures/p1_5_t4d_commander_ui/golden.json",
])
def test_post_accepted_source_or_evidence_drift_fails_closed(path):
    with pytest.raises(AssertionError, match="post-accepted source/test drift"):
        S5.verify_post_acceptance_source_scope([path])
    assert S5.verify_post_acceptance_source_scope([]) == frozenset()


def test_unreviewed_source_and_broker_rejection_survive_optimized_python(tmp_path):
    code = '''from scripts.refactor import shared_strategist_contracts as s
s.ADMITTED_CODE = None  # Explicit unreviewed scenario, also after a future admission.
try:
    s.current_contract(s.candidate_sources())
except AssertionError:
    pass
else:
    raise SystemExit('unreviewed S5 accepted')
try:
    s.verify_integration_scope(['libs/broker/rogue.py'], [])
except AssertionError:
    pass
else:
    raise SystemExit('Broker path accepted')
'''
    subprocess.run([sys.executable, "-O", "-c", code], cwd=ROOT, check=True)


def test_configured_shared_cli_retains_api_fixture_visibility(tmp_path):
    """Regression: noncontiguous API CLI paths lose api_settings in pytest 9.1."""
    from scripts.refactor.shared_candidate_tests import SUITES
    paths = [str(ROOT / "tests" / p) for p in SUITES["shared"]]
    command = [sys.executable] + (["-O"] if sys.flags.optimize else [])
    command += ["-m", "pytest", "-q", "-p", "no:cacheprovider", *paths,
                "-k", "api_routes_are_get_only or original_node_consumers_bind_canonical or prepared_integrated_scope"]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout[-6000:] + result.stderr[-2000:]
    assert "3 passed" in result.stdout
