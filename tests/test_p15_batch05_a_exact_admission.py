"""P1.5 BATCH05-A: exact, versioned source admission without changing frozen B/R3 proofs.

Both accepted pre-A baseline and all-ten-file A snapshot are valid states.
Every hostile case checks the real positive state before asking for rejection.
"""
from pathlib import Path
import sys

import pytest

from scripts.refactor import shared_strategist_contracts as S

sys.path.insert(0, str(S.ROOT / "scripts/refactor"))
import shared_role_contracts as R


def test_stage_a_pinned_positive_and_historical_proofs():
    changed = S.verify_b_scope()
    active = set(changed) & S.BATCH05_A_PATHS
    assert active == set() or active == S.BATCH05_A_PATHS
    if active:
        assert S.verify_batch05_a_sources() == frozenset(S.BATCH05_A_PATHS)
    assert S.verify_next_stage() == frozenset(S.NEXT_RUNTIME)
    assert R.verify_runtime()["moves"] == 313
    assert S.verify_historical_next_scope() == S.NEXT_PATHS


@pytest.mark.parametrize("path", sorted(S.BATCH05_A_PATHS))
def test_no_partial_or_mutated_batch05_a_can_pass(path):
    changed = S.verify_b_scope()  # green positive before hostile probe
    active = set(changed) & S.BATCH05_A_PATHS
    if active:
        source = (S.ROOT / path).read_text(encoding="utf-8-sig")
        with pytest.raises(AssertionError, match="BATCH05-A exact blob drift") as caught:
            S.verify_batch05_a_sources({path: source + "\n# unsafe drift\n"})
    else:
        with pytest.raises(AssertionError, match="BATCH05-A incomplete exact source stage") as caught:
            S.verify_b_scope({path: "# unapproved partial stage\n"})
    assert path in str(caught.value)


@pytest.mark.parametrize("path", [
    "libs/broker/batch05_a_rogue.py",
    "libs/supervisor/batch05_a_rogue.py",
    "apps/operator_ui/batch05_a_rogue.py",
    "tests/test_batch05_a_rogue.py",
    "tests/fixtures/batch05_a_rogue.json",
])
def test_new_stage_rejects_all_unlisted_paths(path):
    assert R.verify_runtime()["moves"] == 313  # non-vacuous positive
    with pytest.raises(AssertionError, match="B-stage unapproved source/test/fixture path") as caught:
        S.verify_b_scope({path: "BROKER_AUTHORITY = True\n"})
    assert path in str(caught.value)


def test_versioned_admission_test_itself_is_immutable():
    assert S.verify_b_scope()
    path = "tests/test_p15_batch05_a_exact_admission.py"
    source = (S.ROOT / path).read_text(encoding="utf-8-sig")
    with pytest.raises(AssertionError, match="BATCH05-A admission-test blob drift") as caught:
        S.verify_b_scope({path: source + "\n# delete negative cases\n"})
    assert path in str(caught.value)
