"""P15 A6: ``resolve_policy_llm_slot`` moved to model_catalog_resolve_policy_llm_slot; parity with the pre-move result."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.llm import model_catalog as mc
from libs.llm import model_catalog_resolve_policy_llm_slot as owner

GOLDEN = ["ac40b046a000e12097f5c2764f6771f22d7bd62685226a195005cc8606b0745b", "c5d14bb54dde31c7d3506e3651052ff15cdf65589a67e683d00ef8bdcd225872", "733b78554f9f276aa89e0ddbb755654e3d5034f12be078266ad3ac15026ade0c", "d72c2e44eb8a38f433423a5a8855d1aeb14090001d123ff738f51110cc47540c", "ac40b046a000e12097f5c2764f6771f22d7bd62685226a195005cc8606b0745b"]   # sha256 of the pre-move mc.resolve_policy_llm_slot result per fixture

SLOT_POLICIES = [
    (None, ("strategist",), "balanced"),
    ({"applied_policy": {"llm": {"strategist": {"profile": "fast_free", "primary": "minimax/minimax-m2.5"}}}, "llm": {"strategist": {"profile": "strong_reasoning"}}}, ("strategist",), "balanced"),
    ({"commander": {"applied_policy": {"llm": {"reporter": {"daily": {"primary": "moonshotai/kimi-k2.5", "fallback": "moonshotai/kimi-k2.5", "policy_source": "custom"}}}}}}, ("reporter", "daily"), "strong_reasoning"),
    ({"reporter_policy": {"llm": {"x": {"model": "deepseek/deepseek-v3.2"}}}, "llm": {"x": {}}}, ("x",), "fast_free"),
    ("junk", ("a", "b"), "balanced"),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


@pytest.mark.parametrize("i", range(len(SLOT_POLICIES)))
def test_wrapper_and_owner_match_pre_move_golden_and_policy_is_unchanged(i):
    policy, path, default = SLOT_POLICIES[i]
    snap = copy.deepcopy(policy)
    assert _h(mc.resolve_policy_llm_slot(policy, *path, default_profile=default)) == GOLDEN[i]
    assert _h(owner.resolve_policy_llm_slot(policy, *path, default_profile=default, facade=mc)) == GOLDEN[i]
    assert policy == snap


def test_priority_and_dedupe_and_card_order():
    top = mc.resolve_policy_llm_slot(SLOT_POLICIES[1][0], "strategist", default_profile="balanced")
    assert top["profile_source"] == "applied_policy.llm" and top["profile"] == "fast_free" and top["primary"] == "minimax/minimax-m2.5"
    dup = mc.resolve_policy_llm_slot(SLOT_POLICIES[2][0], "reporter", "daily", default_profile="strong_reasoning")
    assert dup["profile_source"] == "commander.applied_policy.llm" and dup["policy_source"] == "custom"
    assert dup["primary"] == dup["fallback"] == "moonshotai/kimi-k2.5" and dup["models"] == ["moonshotai/kimi-k2.5"] and len(dup["cards"]) == 1
    none = mc.resolve_policy_llm_slot(None, "strategist", default_profile="balanced")
    assert none["profile_source"] == "default_profile" and none["policy_source"] == "default_profile" and none["models"]


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    seen = []
    monkeypatch.setattr(mc, "normalize_openrouter_model_name", lambda v: (seen.append(v), "NORM")[1])
    out = mc.resolve_policy_llm_slot(SLOT_POLICIES[1][0], "strategist", default_profile="balanced")
    assert out["primary"] == "NORM" and out["fallback"] == "NORM" and seen
    monkeypatch.setattr(mc, "get_model_card", lambda m: {"card": m})
    monkeypatch.setattr(mc, "_dedupe_models", lambda *m: ["ONLY"])
    out = mc.resolve_policy_llm_slot(None, "x", default_profile="balanced")
    assert out["models"] == ["ONLY"] and out["cards"] == [{"card": "ONLY"}]
    monkeypatch.setattr(mc, "_nested_get", lambda obj, *path: {"profile": "from_patch"} if path[:2] == ("applied_policy", "llm") else None)
    assert mc.resolve_policy_llm_slot({}, "x", default_profile="balanced")["profile"] == "from_patch"


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    assert "from libs.llm.model_catalog import" not in inspect.getsource(owner) and "import model_catalog\n" not in inspect.getsource(owner)
    assert len(inspect.getsource(mc.resolve_policy_llm_slot).splitlines()) <= 3
