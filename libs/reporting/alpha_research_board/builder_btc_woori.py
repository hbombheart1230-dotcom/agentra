"""``_btc_woori`` moved verbatim from builder.py.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _btc_woori(payload: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    horizon = facade.find_horizon(payload.get("episode_horizons"), "+30m")
    return facade._candidate(
        candidate_id="BTC_WOORI_V2_ONLY_LOCAL_CONFIRMATION",
        track_id="BTC_WOORI",
        discriminator="BTC multi-horizon momentum + Woori local price/volume confirmation",
        target_horizon="+30m",
        source_status=str(payload.get("conclusion") or "INSUFFICIENT_EVIDENCE"),
        board_bucket="OBSERVE_FIXED",
        owner="BTC_WOORI_BASELINE",
        historical=facade.metric_snapshot(horizon.get("real_net")),
        evidence_note="BTC 단독과 광범위 v2는 약하고, 독립 v2-only +30분 하위군만 양수임.",
        next_action="고정된 현지 확인 하위군만 prospective로 수집.",
        source_keys=["btc_woori_history"],
    )
