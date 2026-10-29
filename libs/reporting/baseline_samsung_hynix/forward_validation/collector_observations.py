"""Q10 index-observation collector integrity Owner (moved from reaction_reader._collector_raw_row).

Tri-state result: ``None`` = ABSENT (legacy fallback allowed), ``{"integrity_failure": True, ...}`` = INVALID (legacy
fallback forbidden), plain row = VERIFIED. ``facade`` is the ``reaction_reader`` module; this module does not import it.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


def collector_raw_row_impl(
    *, day: str, index_name: str, slot: str, root: Path | str | None, facade: Any,
) -> dict[str, Any] | None:
    from libs.market.q10_index_observation_collector import observation_for_slot, _has_verification_evidence

    observation = observation_for_slot(day, slot, root=root)
    availability = str(observation.get("availability") or "")
    indices = observation.get("indices") if isinstance(observation.get("indices"), Mapping) else {}
    index_row = indices.get(index_name) if isinstance(indices.get(index_name), Mapping) else None

    def _unverified_observation() -> dict[str, Any] | None:
        price = facade._number((index_row or {}).get("current"))
        if price is None:
            return None
        return {
            "price": price,
            "source": str(observation.get("source") or "kiwoom.ka20009"),
            "capture_status": availability,
            "requested_at_kst": observation.get("requested_at_kst"),
            "observed_at_kst": observation.get("actual_observed_at_kst"),
            "calculation_usable": False,
        }

    if availability in facade._COLLECTOR_ABSENT_STATES and observation.get('never_attempted') is True:
        return None  # genuinely never captured -- legacy fallback allowed

    if availability not in facade._COLLECTOR_VERIFIED_STATES:
        # INVALID: captured but proven not calculation-usable (item 1's
        # unverified-time/unverified-close states, a too-late fetch, or
        # corrupted/incomplete persistent state). Never silently fall back
        # to legacy -- surface the integrity failure instead.
        return {
            "integrity_failure": True,
            "collector_status": availability,
            "reason": str(observation.get("error") or "collector_observation_not_calculation_usable"),
            "requested_at_kst": observation.get("requested_at_kst"),
            "actual_observed_at_kst": observation.get("actual_observed_at_kst"),
            "unverified_observation": _unverified_observation(),
        }

    try:
        observed = int(datetime.fromisoformat(str(observation.get('actual_observed_at_kst'))).timestamp())
    except (TypeError, ValueError):
        observed = 0
    if not _has_verification_evidence(indices, slot=slot, day=day, observed_epoch=observed):
        return {'integrity_failure': True, 'collector_status': availability, 'reason': 'verification_evidence_invalid'}
    price = facade._number((index_row or {}).get("current"))
    if price is None:
        # VERIFIED overall, but this specific index's component is not
        # among the validated components (e.g. a VERIFIED PARTIAL missing
        # this index) -- also an integrity condition for THIS index, not
        # a genuine absence, so legacy fallback stays forbidden.
        return {
            "integrity_failure": True,
            "collector_status": availability,
            "reason": "index_component_not_present_in_verified_observation",
            "requested_at_kst": observation.get("requested_at_kst"),
            "actual_observed_at_kst": observation.get("actual_observed_at_kst"),
        }
    observed_text = str(observation.get("actual_observed_at_kst") or "")
    try:
        observed_epoch = int(datetime.fromisoformat(observed_text).timestamp())
    except (TypeError, ValueError):
        return {
            "integrity_failure": True,
            "collector_status": availability,
            "reason": "observed_timestamp_unparseable",
            "requested_at_kst": observation.get("requested_at_kst"),
            "actual_observed_at_kst": observation.get("actual_observed_at_kst"),
        }
    market_ts = facade.market_epoch(index_row)
    if market_ts is None:
        # VERIFIED overall but the component carries no market-side timestamp: integrity condition, never a
        # silent legacy fallback (previously int(None) raised TypeError).
        return {
            "integrity_failure": True,
            "collector_status": availability,
            "reason": "market_timestamp_missing",
            "requested_at_kst": observation.get("requested_at_kst"),
            "actual_observed_at_kst": observation.get("actual_observed_at_kst"),
        }
    return {
        "ts": int(market_ts),
        "close": price,
        "open": price,
        "volume": None,
        "source": "q10_index_observation_collector",
        "capture_status": availability,
    }

