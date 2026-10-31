"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence


def iter_quant_shadow_candidate_payloads(
    *,
    reports_root: Path,
    days: Sequence[str],
    keys: Optional[Sequence[str]] = None,
    drop_q9_row_keys: Optional[Sequence[str]] = None,
    facade: Any,
) -> Iterable[Dict[str, Any]]:
    """Yield one payload dict per shadow file.

    `keys=None` (default) yields the complete payload, unchanged. With `keys`,
    each payload is projected onto those top-level keys as soon as it is parsed
    (the full parse is released immediately) and the q9 commander augmentation
    -- which only ever rewrites `q9_decision_candidates` -- is skipped together
    with its multi-hundred-MiB `q9_decision_windows.json` load, unless the
    caller asked for that key.
    """
    root = facade.shadow_candidate_root_for_reports(reports_root)
    seen: set[str] = set()
    wanted = tuple(keys) if keys is not None else None
    augment = wanted is None or "q9_decision_candidates" in wanted
    for day in days:
        q9_windows = facade._q9_windows_by_id(reports_root, day) if augment else {}
        for path in facade._json_paths_for_day(root, day):
            key = str(path)
            if key in seen:
                continue
            seen.add(key)
            payload = facade._read_json(path)
            if not isinstance(payload, dict):
                continue
            if wanted is not None:
                payload = {name: payload[name] for name in wanted if name in payload}
                if not augment:
                    yield facade._drop_q9_row_keys(payload, drop_q9_row_keys)
                    continue
            yield facade._drop_q9_row_keys(
                facade._augment_missing_q9_commander_candidate(
                    dict(payload),
                    windows_by_id=q9_windows,
                ),
                drop_q9_row_keys,
            )
