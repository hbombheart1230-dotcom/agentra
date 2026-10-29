"""Model catalog: ``resolve_policy_llm_slot`` (moved verbatim from model_catalog).

Helpers are resolved on ``facade`` (model_catalog) at call time; this module never imports model_catalog.
"""
from __future__ import annotations

from typing import Any, Dict


def resolve_policy_llm_slot(policy: Dict[str, Any] | None, *path: str, default_profile: str, facade: Any) -> Dict[str, Any]:
    container = policy if isinstance(policy, dict) else {}
    slot: Dict[str, Any] = {}
    slot_source = "default_profile"
    for candidate, source in (
        (facade._nested_get(container, "applied_policy", "llm", *path), "applied_policy.llm"),
        (facade._nested_get(container, "commander", "applied_policy", "llm", *path), "commander.applied_policy.llm"),
        (facade._nested_get(container, "reporter_output", "applied_policy", "llm", *path), "reporter_output.applied_policy.llm"),
        (facade._nested_get(container, "llm", *path), "llm"),
        (facade._nested_get(container, "reporter_policy", "llm", *path), "reporter_policy.llm"),
    ):
        if isinstance(candidate, dict) and candidate:
            slot = dict(candidate)
            slot_source = source
            break

    resolved = facade.resolve_model_profile(str(slot.get("profile") or ""), default_profile=default_profile)
    primary = facade.normalize_openrouter_model_name(
        str(slot.get("primary") or slot.get("model") or resolved.get("primary") or "")
    )
    fallback = facade.normalize_openrouter_model_name(
        str(slot.get("fallback") or resolved.get("fallback") or "")
    )
    cards = [facade.get_model_card(model) for model in facade._dedupe_models(primary, fallback)]
    return {
        "profile": str(slot.get("profile") or resolved.get("profile") or default_profile),
        "requested_profile": str(slot.get("profile") or resolved.get("requested_profile") or default_profile),
        "primary": primary,
        "fallback": fallback,
        "models": facade._dedupe_models(primary, fallback),
        "cards": cards,
        "policy_source": str(slot.get("policy_source") or slot_source or "default_profile"),
        "profile_source": slot_source,
    }
