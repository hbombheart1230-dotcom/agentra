"""Pure policy and response classification for the passive reporter AI review (P1.5 DEV-A).

Decides whether the review is enabled from the explicit flag or the applied/fallback/payload reporter policy, and
classifies an already parsed LLM response (parse mode and failure reason). No LLM call, ledger write, environment read
or clock: ``libs.reporting.reporter_ai_review.build_ai_reporter_review`` keeps all of those.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional


def resolve_ai_review_enabled(reporter_output: Dict[str, Any], enabled: Optional[bool]) -> bool:
    if enabled is None:
        applied_policy = reporter_output.get("applied_policy") if isinstance(reporter_output.get("applied_policy"), dict) else {}
        reporter_policy = applied_policy.get("reporter") if isinstance(applied_policy.get("reporter"), dict) else {}
        ai_review_policy = reporter_policy.get("ai_review") if isinstance(reporter_policy.get("ai_review"), dict) else {}
        policy_fallback = reporter_output.get("reporter_policy") if isinstance(reporter_output.get("reporter_policy"), dict) else {}
        ai_review_fallback = policy_fallback.get("ai_review") if isinstance(policy_fallback.get("ai_review"), dict) else {}
        payload_policy = reporter_output.get("policy") if isinstance(reporter_output.get("policy"), dict) else {}
        payload_reporter_policy = payload_policy.get("reporter") if isinstance(payload_policy.get("reporter"), dict) else {}
        payload_ai_review_policy = (
            payload_reporter_policy.get("ai_review")
            if isinstance(payload_reporter_policy.get("ai_review"), dict)
            else {}
        )
        if ai_review_policy.get("enabled") is not None:
            return bool(ai_review_policy.get("enabled"))
        elif ai_review_fallback.get("enabled") is not None:
            return bool(ai_review_fallback.get("enabled"))
        elif payload_ai_review_policy.get("enabled") is not None:
            return bool(payload_ai_review_policy.get("enabled"))
        else:
            return False
    return bool(enabled)


def resolve_parse_mode(parsed_result: Mapping[str, Any]) -> str:
    return "full" if bool(parsed_result.get("is_full")) else "partial" if bool(parsed_result.get("is_partial")) else "none"


def resolve_parse_failure_reason(parsed_result: Mapping[str, Any], key_meta: Mapping[str, Any]) -> str:
    parse_reason = "ai_response_not_full_json"
    if not bool(parsed_result.get("raw_nonempty")):
        parse_reason = "ai_response_empty"
    elif bool(parsed_result.get("is_partial")):
        parse_reason = "ai_response_partial_json"
    elif bool(key_meta.get("required_keys_missing")):
        missing = ", ".join(list(key_meta.get("required_keys_missing") or []))
        parse_reason = f"ai_response_missing_required_keys:{missing}"
    return parse_reason
