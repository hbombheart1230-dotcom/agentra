"""Focused contracts for UEF-9 formal authority binding."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from libs.reporting.alpha_research_board import build_alpha_research_board
from libs.reporting.evaluation.uef7.alpha_board_normalization import normalize_alpha_board
from libs.reporting.evaluation.uef7.run_identity import normalizer_implementation_digest
from libs.reporting.evaluation.uef8.fair_comparison import analyze_fair_comparisons
from libs.reporting.evaluation.uef8.run_identity import (
    compute_uef8_run_id,
    uef7_normalized_rows_semantic_digest,
    uef8_implementation_digest,
)
from libs.reporting.evaluation.uef9.authority import verify_formal_evaluation_authority
from libs.reporting.evaluation.uef9.model import UEF9AuthorityError, VALID
from uef9_synthetic_reports import FIXTURE, materialize_reports, validate_reports


ROOT = Path(__file__).resolve().parents[1]
IMPL = "uef9-test-implementation"


def _base_inputs(*, reports_root):
    validate_reports(reports_root)
    board = build_alpha_research_board(reports_root=reports_root, through_day="2026-09-25")
    uef7 = normalize_alpha_board(board, normalizer_implementation_digest_value=normalizer_implementation_digest()).to_dict()
    uef8 = analyze_fair_comparisons(uef7, uef8_implementation_digest_value=uef8_implementation_digest()).to_dict()
    return uef7, uef8


@pytest.fixture()
def inputs(tmp_path):
    reports_root = materialize_reports(tmp_path / "synthetic-reports")
    return _base_inputs(reports_root=reports_root)


def _verify(uef7, uef8, *, impl=IMPL):
    return verify_formal_evaluation_authority(uef7, uef8=uef8, uef9_implementation_digest_value=impl)


def _refresh_uef8_binding(uef7, uef8):
    digest = uef7_normalized_rows_semantic_digest(uef7["normalized_rows"])
    uef8["source_uef7_run_id"] = uef7["uef7_run_id"]
    uef8["source_uef7_through_day"] = uef7["through_day"]
    uef8["uef7_normalized_semantic_digest"] = digest
    uef8["uef8_run_id"] = compute_uef8_run_id(
        source_uef7_run_id=uef8["source_uef7_run_id"],
        uef7_normalized_semantic_digest=digest,
        uef8_implementation_digest_value=uef8["uef8_implementation_digest"],
        schema_version=uef8["schema_version"],
        fair_comparison_policy_version=uef8["fair_comparison_policy_version"],
    )


def test_a_valid_current_authority(inputs):
    authority = _verify(*inputs)
    assert authority.authority_status == VALID
    assert authority.candidate_count == 14
    assert authority.pair_count == 91
    assert authority.comparison_status_counts == {"COMPARABLE": 0, "CONDITIONAL": 7, "NOT_COMPARABLE": 84}


@pytest.mark.parametrize("mutator", [
    lambda u7, u8: u8.__setitem__("source_uef7_run_id", "UEF7RUN_wrong"),
    lambda u7, u8: u8.__setitem__("uef7_normalized_semantic_digest", "wrong"),
    lambda u7, u8: u8.__setitem__("candidate_count", 99),
    lambda u7, u8: u8.__setitem__("candidate_ids", u8["candidate_ids"][1:]),
    lambda u7, u8: u7["normalized_rows"].append(copy.deepcopy(u7["normalized_rows"][0])),
    lambda u7, u8: u8.__setitem__("pairs", u8["pairs"][:-1]),
    lambda u7, u8: u8["pairs"][0].__setitem__("left_candidate_id", "UNKNOWN"),
    lambda u7, u8: u8["pairs"][0].__setitem__("right_candidate_id", u8["pairs"][0]["left_candidate_id"]),
    lambda u7, u8: u8["pairs"].__setitem__(1, copy.deepcopy(u8["pairs"][0])),
    lambda u7, u8: u8["pairs"][1].__setitem__("comparison_pair_id", u8["pairs"][0]["comparison_pair_id"]),
    lambda u7, u8: u8["summary"].__setitem__("conditional_count", 99),
    lambda u7, u8: u8["pairs"][0].__setitem__("comparison_status", "UNKNOWN"),
    lambda u7, u8: u8["pairs"][0].__setitem__("comparison_status", "COMPARABLE"),
])
def test_b_structural_contradictions_fail_closed(inputs, mutator):
    uef7, uef8 = copy.deepcopy(inputs)
    mutator(uef7, uef8)
    with pytest.raises(UEF9AuthorityError):
        _verify(uef7, uef8)


def test_b2_capability_contradiction_isolated_from_summary_mismatch(inputs):
    # Item N's exact scenario, isolated from the more general "summary
    # count mismatch" guard: an otherwise INTERNALLY SELF-CONSISTENT UEF-8
    # payload (pair status AND summary counts agree with each other) that
    # claims one COMPARABLE pair. The per-status summary cross-check alone
    # would NOT catch this (summary and pairs agree), so this isolates
    # the dedicated "current UEF-7 schema declares COMPARABLE unreachable"
    # capability-contradiction guard as the actual reason for failure.
    uef7, uef8 = copy.deepcopy(inputs)
    original_status = uef8["pairs"][0]["comparison_status"]
    assert original_status in ("CONDITIONAL", "NOT_COMPARABLE")
    uef8["pairs"][0]["comparison_status"] = "COMPARABLE"
    uef8["pairs"][0]["comparison_reasons"] = []
    uef8["summary"]["comparable_count"] += 1
    uef8["summary"][f"{original_status.lower()}_count"] -= 1
    with pytest.raises(UEF9AuthorityError, match="COMPARABLE unreachable"):
        _verify(uef7, uef8)


def test_c_candidate_and_pair_order_are_nonsemantic(inputs):
    uef7, uef8 = inputs
    baseline = _verify(uef7, uef8)
    reordered_uef7, reordered_uef8 = copy.deepcopy((uef7, uef8))
    reordered_uef7["normalized_rows"].reverse()
    reordered_uef7["candidate_ids"].reverse()
    reordered_uef8["candidate_ids"].reverse()
    reordered_uef8["pairs"].reverse()
    reordered = _verify(reordered_uef7, reordered_uef8)
    assert reordered.candidate_ids_digest == baseline.candidate_ids_digest
    assert reordered.comparison_pair_ids_digest == baseline.comparison_pair_ids_digest
    assert reordered.uef9_run_id == baseline.uef9_run_id


def test_d_semantic_upstream_mutations_change_run_identity(inputs):
    uef7, uef8 = inputs
    baseline = _verify(uef7, uef8)
    changed_uef7, changed_uef8 = copy.deepcopy((uef7, uef8))
    changed_uef7["normalized_rows"][0]["win_rate"] = 0.123456
    _refresh_uef8_binding(changed_uef7, changed_uef8)
    assert _verify(changed_uef7, changed_uef8).uef9_run_id != baseline.uef9_run_id

    changed_uef8 = copy.deepcopy(uef8)
    changed_uef8["pairs"][0]["comparison_reasons"] = ["SYNTHETIC_AUDIT_MUTATION"]
    assert _verify(uef7, changed_uef8).uef9_run_id != baseline.uef9_run_id


def test_e_implementation_digest_changes_run_identity(inputs):
    assert _verify(*inputs, impl="implementation-a").uef9_run_id != _verify(*inputs, impl="implementation-b").uef9_run_id


def test_f_no_ranking_or_execution_authority(inputs):
    payload = _verify(*inputs).to_dict()
    assert payload["prohibitions"] == {
        "ranking_authority": "NONE",
        "promotion_authority": "NONE",
        "trading_execution_authority": "NONE",
    }
    forbidden = {"score", "rank", "winner", "loser", "promotion_recommendation", "strategy_recommendation", "return_delta", "pf_delta"}

    def check(value):
        if isinstance(value, dict):
            for key, child in value.items():
                assert key.lower() not in forbidden
                check(child)
        elif isinstance(value, list):
            for child in value:
                check(child)

    check(payload)


def test_g_uef8_native_digest_is_explicitly_unavailable(inputs):
    authority = _verify(*inputs)
    assert authority.source_uef8_native_semantic_digest_available is False
    assert authority.uef9_derived_uef8_authority_digest


@pytest.mark.parametrize("damage", ["missing", "changed", "extra"])
def test_h_raw_fixture_damage_fails_before_authority(tmp_path, damage):
    root = materialize_reports(tmp_path / "reports")
    target = next(root.rglob("*.json"))
    if damage == "missing":
        target.unlink()
    elif damage == "changed":
        target.write_text("{}", encoding="utf-8")
    else:
        (root / "unexpected.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="UEF9 synthetic reports"):
        _base_inputs(reports_root=root)


@pytest.mark.parametrize("damage", ["missing", "changed"])
def test_i_fixture_package_missing_or_changed_never_falls_back(tmp_path, damage):
    source = tmp_path / "fixture.json"
    if damage == "changed":
        source.write_bytes(FIXTURE.read_bytes() + b" ")
    with pytest.raises((FileNotFoundError, ValueError)):
        materialize_reports(tmp_path / "reports", fixture_path=source)
    assert not (tmp_path / "reports").exists()


def test_j_unreadable_fixture_fails_closed(tmp_path, monkeypatch):
    original = Path.read_bytes

    def denied(path):
        if path == FIXTURE:
            raise PermissionError("synthetic read denial")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", denied)
    with pytest.raises(PermissionError):
        materialize_reports(tmp_path / "reports")
    assert not (tmp_path / "reports").exists()


@pytest.mark.parametrize("relative", ["../escape.json", "/escape.json", "C:\\escape.json"])
def test_k_fixture_cannot_escape_injected_root(tmp_path, monkeypatch, relative):
    import uef9_synthetic_reports as synthetic
    # Exercise defense beyond the package digest without modifying the fixture.
    monkeypatch.setattr(synthetic, "fixture_payload", lambda path=FIXTURE: {"artifacts": {relative: {}}})
    with pytest.raises(ValueError, match="path escape"):
        materialize_reports(tmp_path / "reports")
    assert not (tmp_path / "reports").exists()


def test_l_existing_root_cannot_supply_ambient_reports(tmp_path):
    root = tmp_path / "reports"
    root.mkdir()
    with pytest.raises(ValueError, match="fresh nonsymlink"):
        materialize_reports(root)


def test_m_production_inputs_really_depend_on_raw_evidence(tmp_path):
    root = materialize_reports(tmp_path / "reports")
    # Bypass only our test-package integrity check to show the real upstream
    # computation changes when evidence is absent; no result is synthesized.
    empty = tmp_path / "absent-reports"
    board = build_alpha_research_board(reports_root=empty, through_day="2026-09-25")
    u7 = normalize_alpha_board(board, normalizer_implementation_digest_value=normalizer_implementation_digest()).to_dict()
    u8 = analyze_fair_comparisons(u7, uef8_implementation_digest_value=uef8_implementation_digest()).to_dict()
    with pytest.raises(AssertionError):
        test_a_valid_current_authority((u7, u8))
    test_a_valid_current_authority(_base_inputs(reports_root=root))


def test_n_clock_and_hash_seed_do_not_change_authority(tmp_path):
    root = materialize_reports(tmp_path / "reports")
    code = ("import sys,time,json;sys.path[:0]=" + repr([str(ROOT), str(ROOT / "tests")]) + ";"
            "time.time=lambda:float(sys.argv[2]);"
            "from test_uef9_formal_authority import _base_inputs,_verify;"
            "a=_verify(*_base_inputs(reports_root=__import__('pathlib').Path(sys.argv[1])));"
            "print(json.dumps([a.uef9_run_id,a.comparison_status_counts],sort_keys=True))")
    values = []
    for seed, clock in [("0", "0"), ("17", "2000000000")]:
        env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONDONTWRITEBYTECODE="1")
        command = [sys.executable] + (["-O"] if sys.flags.optimize else [])
        result = subprocess.run(command + ["-c", code, str(root), clock], cwd=tmp_path,
                                env=env, check=True, capture_output=True, text=True, timeout=60)
        values.append(json.loads(result.stdout))
    assert values[0] == values[1]
    assert values[0][1] == {"COMPARABLE": 0, "CONDITIONAL": 7, "NOT_COMPARABLE": 84}
