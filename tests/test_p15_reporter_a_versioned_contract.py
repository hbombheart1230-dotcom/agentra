"""Exact A composed-data preview; no A runtime/guard files are installed."""
import ast
import hashlib
import inspect
from pathlib import Path
import sys

import pytest

from scripts.refactor import shared_strategist_contracts as S

sys.path.insert(0, str(S.ROOT / "scripts/refactor"))
import shared_role_contracts as R


def _a():
    return {p: S.git_source(S.A_SOURCE, p) for p in S.A_STAGE_PATHS}


def _preview_green():
    original = _a()
    result = R.verify_runtime(original)
    assert (result["moves"], result["facades"], result["monitor_modules"], result["monitor_bodies"], result["reporter_a"]) == (313, 23, 14, 20, True)
    return original


def test_b_current_historical_and_composed_preview_are_distinct_green_stages():
    baseline = R.verify_runtime()
    assert baseline["moves"] == 313
    assert baseline["reporter_a"] is bool(S.verify_a_sources())
    assert R.verify_historical_reporter()["moves"] == 313
    original = _preview_green()
    assert S.verify_b_sources(original) == S.B_RUNTIME
    assert S.verify_next_stage(original) == frozenset(S.NEXT_RUNTIME)
    assert S.verify_historical_next_scope() == S.NEXT_PATHS
    # Actual scope is validated BEFORE B's legacy result view is returned.
    assert S.verify_b_scope(original) <= S.B_SOURCE_PATHS | S.B_CONTRACT_PATHS


def test_pre_a_exact_seed_inventory_is_preserved_and_current_adds_one_owner():
    from test_work_reporter_seed_migration import REGISTRY, DECOMPOSED, R4_OWNER_FILES, REPORTER_PACKAGES
    original = _preview_green()
    historical = R.reporter_inventory()
    if S.verify_a_sources():
        historical = historical - {S.A_OWNER}
    current = R.reporter_inventory(original)
    assert current - historical == {S.A_OWNER}
    for sub in REPORTER_PACKAGES:
        exact = sorted(["__init__.py"] + [f"{n}.py" for n, (s, _) in REGISTRY.items() if s == sub]
            + [f"{o}.py" for d_sub, owners in DECOMPOSED.values() if d_sub == sub for o in owners]
            + [Path(o).name for o in R4_OWNER_FILES if Path(o).parent.name == sub])
        assert sorted(Path(p).name for p in historical if Path(p).parent.name == sub) == exact
        admitted = [Path(S.A_OWNER).name] if sub == "read_models" else []
        assert sorted(Path(p).name for p in current if Path(p).parent.name == sub) == sorted(exact + admitted)


CASES = [
    ("facade_body", S.A_FACADE), ("facade_abi", S.A_FACADE),
    ("late_import", S.A_FACADE), ("owner_body", S.A_OWNER),
    ("owner_import", S.A_OWNER), ("guard_body", S.A_GUARD),
    ("old_moved_body", "libs/agents/reporter/read_models/reporter_analysis_bodies_01.py"),
    ("fake_owner", "libs/agents/reporter/read_models/fake_owner.py"),
    ("broker", "libs/broker/a_privilege.py"), ("executor", "libs/executor/a_privilege.py"),
    ("quant_not_admitted", "libs/reporting/quant_shadow_candidate_projection.py"),
    ("unknown_test", "tests/test_a_unapproved.py"),
]


@pytest.mark.parametrize("kind,path", CASES, ids=[x[0] for x in CASES])
def test_nonvacuous_composed_mutations_fail_for_the_injected_path(kind, path):
    original = _preview_green()  # Exactly three pinned A inputs, no checker weakening.
    if path in original:
        changed = original[path]
    elif kind == "old_moved_body":
        changed = (S.ROOT / path).read_text(encoding="utf-8")
    else:
        changed = ""
    if kind in {"facade_body", "facade_abi", "late_import"}:
        tree = ast.parse(changed)
        if kind == "late_import":
            node = next(n for n in tree.body if isinstance(n, ast.ImportFrom)
                        and n.module == "libs.agents.reporter.read_models" and any(a.asname == "_analysis_projection" for a in n.names))
            tree.body.remove(node)
            tree.body.append(node)
        else:
            fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "generate_reporter_analysis_report")
            if kind == "facade_body":
                fn.body.insert(0, ast.parse("raise RuntimeError('unauthorized')").body[0])
            else:
                fn.args.kwonlyargs.append(ast.arg(arg="broker_permission"))
                fn.args.kw_defaults.append(ast.Constant(value=True))
        changed = ast.unparse(tree)
    else:
        changed += "\n__import__('os')\nBROKER_AUTHORITY = True\n"
    with pytest.raises(AssertionError) as rejected:
        R.verify_runtime(original | {path: changed})
    assert path in str(rejected.value), (kind, str(rejected.value))


@pytest.mark.parametrize("path", sorted(S.A_STAGE_PATHS))
def test_historical_stage_rejects_each_a_input(path):
    assert R.verify_historical_reporter()["moves"] == 313
    with pytest.raises(AssertionError) as rejected:
        R.verify_historical_reporter({path: _a()[path]})
    assert path in str(rejected.value)


@pytest.mark.parametrize("path", sorted(S.A_STAGE_PATHS))
def test_current_stage_rejects_missing_or_old_input(path):
    original = _preview_green()
    if path == S.A_OWNER:
        original.pop(path)
        # An installed current A root cannot simulate a deleted file by omitting
        # an override. An explicit bad value represents that missing source.
        if (S.ROOT / path).exists():
            original[path] = ""
    else:
        original[path] = S.git_source(S.A_PRE_SOURCE, path)
    with pytest.raises(AssertionError) as rejected:
        R.verify_runtime(original)
    assert path in str(rejected.value)


def test_guard_is_validated_before_any_pinned_proof_executes(monkeypatch):
    original = _preview_green()
    def forbidden(*args):
        raise RuntimeError("proof executed before guard validation")
    monkeypatch.setattr(R, "_pinned_guard", forbidden)
    original[S.A_GUARD] += "\n__import__('os')\n"
    with pytest.raises(AssertionError, match=S.A_GUARD):
        R.verify_runtime(original)


def test_untracked_owner_is_detected_from_real_inventory_reader(monkeypatch):
    original = _preview_green()
    real = Path.rglob
    rogue = S.ROOT / "libs/agents/reporter/read_models/untracked_rogue.py"
    def planted(path, pattern):
        yield from real(path, pattern)
        if path == S.ROOT / "libs/agents/reporter":
            yield rogue
    monkeypatch.setattr(Path, "rglob", planted)
    with pytest.raises(AssertionError, match="untracked_rogue.py"):
        R.verify_runtime(original)


def test_ast_serializer_difference_preserves_literal_and_rejects_body_mutant(monkeypatch):
    original = _preview_green()
    proof = R._pinned_guard(S.A_SOURCE)
    literal = proof.P15_TRANSITIONS[S.A_FACADE]["function_ast_sha256"]
    reference = next(n for n in ast.parse(original[S.A_FACADE]).body
                     if isinstance(n, ast.FunctionDef) and n.name == "generate_reporter_analysis_report")
    if "show_empty" in inspect.signature(ast.dump).parameters:
        def expanded(node):
            return ast.dump(node, include_attributes=False, show_empty=True)
        monkeypatch.setattr(proof, "dump", expanded)
    # On Python3.12 native dump already includes the optional empty lists.
    digest = hashlib.sha256(proof.dump(reference).encode("utf-8")).hexdigest()
    assert digest != literal
    with pytest.raises(AssertionError, match=S.A_FACADE):
        proof.revert_p15_transition(R.git_text(R.BASE, S.A_FACADE), original[S.A_FACADE], S.A_FACADE)
    assert R.verify_runtime(original)["reporter_a"]
    spec = R._portable_a_transitions(proof)
    assert spec[S.A_FACADE]["function_ast_sha256"] == digest
    assert proof.P15_TRANSITIONS[S.A_FACADE]["function_ast_sha256"] == literal
    # The portable expectation comes only from Git. A candidate body change
    # still fails the actual restored-AST checker, even without the outer pin.
    tree = ast.parse(original[S.A_FACADE])
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "generate_reporter_analysis_report")
    fn.body.insert(0, ast.parse("raise RuntimeError('mutant')").body[0])
    with pytest.raises(AssertionError, match=S.A_FACADE):
        proof.revert_p15_transition(R.git_text(R.BASE, S.A_FACADE), ast.unparse(tree), S.A_FACADE,
                                   transitions=spec)
