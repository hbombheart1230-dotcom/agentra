from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Mapping

from libs.market.korea_index_sanity import korea_index_sanity
from libs.reporting import market_regime_rail_review_scalar_projection as _scalar_owner
from libs.reporting import market_regime_rail_review_markdown_projection as _markdown_owner
from libs.reporting import market_regime_rail_review_read_projection as _read_projection_owner
from libs.reporting import market_regime_rail_classification_projection as _classification_owner


def _to_float(value: Any, default: float = 0.0) -> float:
    return _scalar_owner._to_float(value, default)


def _indicator(snapshot: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    return _scalar_owner._indicator(snapshot, key, facade=sys.modules[__name__])


def _change_pct(snapshot: Mapping[str, Any], key: str) -> float:
    return _scalar_owner._change_pct(snapshot, key, facade=sys.modules[__name__])


def load_latest_macro_snapshot(day: str, *, root: Path = Path("data/logs/macro_indicators")) -> Dict[str, Any]:
    return _read_projection_owner.load_latest_macro_snapshot(day, root=root, facade=sys.modules[__name__])


def classify_market_regime_rail(snapshot: Mapping[str, Any]) -> Dict[str, Any]:
    return _classification_owner.classify_market_regime_rail(snapshot, facade=sys.modules[__name__])


def render_market_regime_rail_markdown(rail: Mapping[str, Any], *, day: str) -> str:
    return _markdown_owner.render_market_regime_rail_markdown(rail, day=day, facade=sys.modules[__name__])


def generate_market_regime_rail_review(*, reports_root: Path, day: str) -> Dict[str, Any]:
    snapshot = load_latest_macro_snapshot(day)
    rail = classify_market_regime_rail(snapshot)
    out_dir = Path(reports_root) / "operator_summary" / "daily" / str(day)[:10]
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "market_regime_rail_review.json"
    md_path = out_dir / "market_regime_rail_review.md"
    json_path.write_text(json.dumps(rail, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_market_regime_rail_markdown(rail, day=str(day)[:10]), encoding="utf-8")
    return {**rail, "report_json_path": str(json_path), "report_md_path": str(md_path)}


__all__ = [
    "classify_market_regime_rail",
    "generate_market_regime_rail_review",
    "load_latest_macro_snapshot",
    "render_market_regime_rail_markdown",
]
