"""Separate immutable historical proofs and exact current B admission.

Every hostile probe first proves the actual unmodified contract green and
checks that rejection identifies its own injected path, never a baseline red.
"""
import ast
from pathlib import Path
import sys

import pytest

from scripts.refactor import shared_strategist_contracts as S

sys.path.insert(0, str(S.ROOT / "scripts/refactor"))
import shared_role_contracts as R


def test_original_five_functions_and_eight_s5_helpers_remain_provable():
    original = {path: S.git_source(pin, path) for path, pin in S.NEXT_RUNTIME.items()}
    assert S._verify_five_function_stage(original) == frozenset(S.NEXT_RUNTIME)
    assert S.dump(S.restore_candidate(S.candidate_sources())) == S.dump(ast.parse(S.git_source(S.SOURCE, S.NODE)))
    assert S.verify_historical_next_scope() == S.NEXT_PATHS
    assert S.verify_next_stage() == frozenset(S.NEXT_RUNTIME)
    assert S.verify_b_sources() == S.B_RUNTIME
    result = R.verify_runtime()
    assert (result["moves"], result["facades"], result["monitor_modules"], result["monitor_bodies"]) == (313, 23, 14, 20)


def test_old_and_current_shapes_cannot_be_substituted_for_each_other():
    S.verify_b_sources()
    with pytest.raises(AssertionError, match="new-stage source.*" + S.UI_CORE):
        S.verify_b_sources({S.UI_CORE: S.git_source(S.UI_PIN, S.UI_CORE)})
    original = {path: S.git_source(pin, path) for path, pin in S.NEXT_RUNTIME.items()}
    S._verify_five_function_stage(original)
    original[S.UI_CORE] = S.git_source(S.B_SOURCE, S.UI_CORE)
    with pytest.raises(AssertionError, match="new-stage source.*" + S.UI_CORE):
        S._verify_five_function_stage(original)
    # Explicit old-stage path probes have NOT acquired a generic new Owner rule.
    with pytest.raises(AssertionError, match="out-of-scope integration completion"):
        S.verify_historical_next_scope(sorted(S.B_OWNERS), [])


CASES = [
    ("unknown_app_owner", "apps/operator_ui/unapproved_projection.py", "runtime"),
    ("broker_authority", "libs/broker/unapproved_authority.py", "runtime"),
    ("core_unmoved", S.UI_CORE, "stage"),
    ("core_wrapper_args", S.UI_CORE, "stage"),
    ("owner_body", "apps/operator_ui/data_access_trade_index_projection.py", "stage"),
    ("owner_dynamic_import", "apps/operator_ui/data_access_overview_projection.py", "stage"),
    ("owner_extra_llm", "apps/operator_ui/data_access_run_detail_projection.py", "stage"),
    ("state_change", S.UI_CORE, "stage"),
    ("historical_s5_body", S.VALUE, "runtime"),
    ("historical_monitor_body", "libs/runtime/monitor_exit/reasons.py", "runtime"),
    ("unknown_test", "tests/test_unapproved_future_stage.py", "scope"),
    ("unknown_fixture", "tests/fixtures/unapproved/golden.json", "scope"),
    ("old_fixture", "tests/fixtures/p1_5_t4d_commander_ui/golden.json", "scope"),
    ("b_regression_test", "tests/test_p15_operator_run_detail_projection.py", "scope"),
]


@pytest.mark.parametrize("kind,path,gate", CASES, ids=[row[0] for row in CASES])
def test_current_negative_probes_have_green_base_and_path_specific_failures(kind, path, gate):
    # These are real, default current-tree checks, not mocked green preconditions.
    assert R.verify_runtime()["moves"] == 313
    S.verify_next_stage()
    S.verify_b_scope()
    if kind in {"unknown_app_owner", "broker_authority", "unknown_test", "unknown_fixture", "old_fixture"}:
        changed = "BROKER_AUTHORITY = True\n"
    else:
        changed = (S.ROOT / path).read_text(encoding="utf-8-sig")
        if kind == "core_unmoved":
            tree = ast.parse(changed)
            S.functions(tree)["_trade_report_meta_for_run"].body = ast.parse("return {} # unauthorized").body
            changed = ast.unparse(tree)
        elif kind == "core_wrapper_args":
            assert "canonical_sources=canonical_sources" in changed
            changed = changed.replace("canonical_sources=canonical_sources", "canonical_sources={}", 1)
        elif kind == "owner_dynamic_import":
            changed += "\n__import__('os')\n"
        elif kind == "owner_extra_llm":
            changed += "\nfacade.LLMRouter.from_env()\n"
        elif kind == "b_regression_test":
            changed += "\n# unauthorized oracle edit\n"
        else:
            changed += "\nState = {'broker_permission': True}\n"
    checker = {"runtime": R.verify_runtime, "stage": S.verify_next_stage, "scope": S.verify_b_scope}[gate]
    with pytest.raises(AssertionError) as rejected:
        checker({path: changed})
    assert path in str(rejected.value), (kind, str(rejected.value))
    if gate == "scope":
        assert "B-stage" in str(rejected.value)


@pytest.mark.parametrize("path", sorted(S.B_OWNERS))
def test_historical_projection_checks_actual_owner_before_using_old_bytes(path, monkeypatch):
    assert S.historical_source(S.UI_CORE) == S.git_source(S.HISTORICAL_STAGE, S.UI_CORE)
    read = Path.read_text
    def changed(p, *args, **kwargs):
        value = read(p, *args, **kwargs)
        return value + "\n__import__('os')\n" if p == S.ROOT / path else value
    monkeypatch.setattr(Path, "read_text", changed)
    with pytest.raises(AssertionError) as rejected:
        S.historical_source(S.UI_CORE)
    assert path in str(rejected.value)
