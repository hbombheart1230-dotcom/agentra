"""Integration-closeout inventory must never turn remote CI into local PASS."""
from scripts.refactor.p152_integration_acceptance import (
    FACADES, LOCAL_GATES, REQUIRED_REMOTE_GATES, ROOT, build_inventory, owner_files,
)


def test_offline_inventory_is_read_only_and_retains_436_abi():
    inventory = build_inventory(ROOT)
    source = inventory["source_inventory"]
    assert source["all_source_checks_pass"]
    assert sum(FACADES.values()) == 436
    assert source["façade_public_callable_total"] == 436
    assert source["forbidden_modified_paths"] == []
    assert len(owner_files(ROOT)) == 37
    assert source["new_small_owner_count"] == 37
    assert source["new_small_owner_max_loc"] <= 350
    assert all(item["count_matches"] for item in source["facades"].values())


def test_remote_green_cannot_close_p152_or_unlock_p153():
    inventory = build_inventory(ROOT)
    assert inventory["closeout_allowed"] is False
    assert inventory["p152_stage"] == "OPEN"
    assert inventory["p153_stage"] == "NOT_AUTHORIZED"
    assert inventory["final_acceptance"].startswith("BLOCKED")
    assert set(inventory["remote_suite_gates"]) == set(REQUIRED_REMOTE_GATES)
    assert all(x == "PASS_IF_PRIOR_CI_STEP_SUCCESS" for x in inventory["remote_suite_gates"].values())
    assert set(inventory["local_acceptance_gates"]) == set(LOCAL_GATES)
    assert all(x == "NOT_RUN_NOT_IN_GITHUB" for x in inventory["local_acceptance_gates"].values())


def test_head_and_original_commit_are_explicit():
    inventory = build_inventory(ROOT)
    assert len(inventory["git_sha"]) == 40
    assert len(inventory["pinned_before_code_sha"]) == 40
    assert inventory["git_sha"] != inventory["pinned_before_code_sha"]
    assert inventory["no_real_broker_or_llm_invocation"] is True
