"""trade_bundle_assembly projections (moved verbatim from trade_bundle_assembly).

Module globals and helpers are resolved on ``facade`` (the trade_bundle_assembly module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping


def attach_strategy_anchor(
    payload: Mapping[str, Any] | None,
    *,
    strategy_anchor_run_id: str,
    strategist_input_path: Path,
    strategist_compact_input_path: Path,
    strategist_llm_response_path: Path,
) -> Dict[str, Any]:
    out = dict(payload or {})
    out["entry_strategist_run_id"] = str(strategy_anchor_run_id or "")
    out["strategy_anchor_run_id"] = str(strategy_anchor_run_id or "")
    out["strategy_anchor"] = {
        "run_id": str(strategy_anchor_run_id or ""),
        "artifacts": {
            "strategist_input_json": str(strategist_input_path),
            "strategist_compact_input_json": str(strategist_compact_input_path),
            "strategist_llm_response_json": str(strategist_llm_response_path),
        },
    }
    return out



def apply_strategy_anchor_metadata(
    *,
    lifecycle: Dict[str, Any],
    lifecycle_bundle: Dict[str, Any],
    strategy_anchor_run_id: str,
    strategist_input_path: Path,
    strategist_compact_input_path: Path,
    strategist_llm_response_path: Path,
    facade: Any,
) -> Dict[str, Any]:
    lifecycle["entry_strategist_run_id"] = strategy_anchor_run_id
    lifecycle["strategy_anchor_run_id"] = strategy_anchor_run_id
    lifecycle["strategy_anchor"] = {
        "run_id": strategy_anchor_run_id,
        "source": "strategist_input_artifact" if strategy_anchor_run_id else "missing",
        "artifacts": {
            "strategist_input_json": str(strategist_input_path),
            "strategist_compact_input_json": str(strategist_compact_input_path),
            "strategist_llm_response_json": str(strategist_llm_response_path),
        },
    }
    lifecycle_bundle["entry_strategist_run_id"] = strategy_anchor_run_id
    lifecycle_bundle["strategy_anchor_run_id"] = strategy_anchor_run_id
    lifecycle_bundle["market_context_human"] = facade.attach_strategy_anchor(
        lifecycle_bundle.get("market_context_human") if isinstance(lifecycle_bundle.get("market_context_human"), dict) else {},
        strategy_anchor_run_id=strategy_anchor_run_id,
        strategist_input_path=strategist_input_path,
        strategist_compact_input_path=strategist_compact_input_path,
        strategist_llm_response_path=strategist_llm_response_path,
    )
    lifecycle_bundle["scanner_reason_human"] = facade.attach_strategy_anchor(
        lifecycle_bundle.get("scanner_reason_human") if isinstance(lifecycle_bundle.get("scanner_reason_human"), dict) else {},
        strategy_anchor_run_id=strategy_anchor_run_id,
        strategist_input_path=strategist_input_path,
        strategist_compact_input_path=strategist_compact_input_path,
        strategist_llm_response_path=strategist_llm_response_path,
    )
    lifecycle_bundle["monitor_reason_human"] = facade.attach_strategy_anchor(
        lifecycle_bundle.get("monitor_reason_human") if isinstance(lifecycle_bundle.get("monitor_reason_human"), dict) else {},
        strategy_anchor_run_id=strategy_anchor_run_id,
        strategist_input_path=strategist_input_path,
        strategist_compact_input_path=strategist_compact_input_path,
        strategist_llm_response_path=strategist_llm_response_path,
    )
    return {
        "lifecycle": lifecycle,
        "lifecycle_bundle": lifecycle_bundle,
        "strategy_anchor_run_id": strategy_anchor_run_id,
    }
