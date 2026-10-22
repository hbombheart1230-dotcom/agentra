from __future__ import annotations

import json
import sys as _sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from libs.reporting.evaluation.q8_trusted_reaggregation_projection_p15 import (  # noqa: F401 - facade ABI re-exports
    _fmt_num,
    _fmt_pct,
    _watchlist_rows,
    daily_row_impl,
    reaggregation_payload_impl,
    render_q8_trusted_reaggregation_markdown_impl,
)
from libs.reporting.q8_evaluation_contract import (
    DUPLICATE_RATE_MAX,
    PROMOTION_CANDIDATE_MIN_DAYS,
    PROMOTION_CANDIDATE_MIN_OBSERVED,
    TRUSTED_FORWARD_MIN_COUNT,
    TRUSTED_FORWARD_MIN_COVERAGE,
)
from libs.reporting.quant_shadow_candidate_evaluation import (
    build_quant_shadow_candidate_evaluation,
    load_quant_shadow_candidate_payloads,
)


def _iter_days(start: str, end: str) -> Iterable[str]:
    current = date.fromisoformat(str(start)[:10])
    final = date.fromisoformat(str(end)[:10])
    while current <= final:
        yield current.isoformat()
        current += timedelta(days=1)


def build_q8_trusted_reaggregation(*, reports_root: Path, start: str, end: str) -> Dict[str, Any]:
    daily: List[Dict[str, Any]] = []
    all_payloads: List[Dict[str, Any]] = []
    promotion_allowed_day_count = 0
    for day in _iter_days(start, end):
        payloads = load_quant_shadow_candidate_payloads(reports_root=reports_root, days=[day])
        if not payloads:
            continue
        all_payloads.extend(payloads)
        evaluation = build_quant_shadow_candidate_evaluation(payloads)
        row = daily_row_impl(day, evaluation, facade=_sys.modules[__name__])
        daily.append(row)
        if row["promotion_allowed"]:
            promotion_allowed_day_count += 1

    cumulative_evaluation = build_quant_shadow_candidate_evaluation(all_payloads) if all_payloads else {}
    return reaggregation_payload_impl(
        start=start,
        end=end,
        daily=daily,
        promotion_allowed_day_count=promotion_allowed_day_count,
        cumulative_evaluation=cumulative_evaluation,
        facade=_sys.modules[__name__],
    )


def render_q8_trusted_reaggregation_markdown(payload: Mapping[str, Any]) -> str:
    return render_q8_trusted_reaggregation_markdown_impl(payload, facade=_sys.modules[__name__])


def write_q8_trusted_reaggregation(
    *,
    reports_root: Path,
    start: str,
    end: str,
    output_dir: Path,
) -> Dict[str, Path]:
    payload = build_q8_trusted_reaggregation(reports_root=reports_root, start=start, end=end)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"q8_trusted_reaggregation_{str(start)[:10]}_to_{str(end)[:10]}"
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_q8_trusted_reaggregation_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}
