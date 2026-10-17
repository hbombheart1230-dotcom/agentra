"""Compatibility facade: implementations live in ``libs.agents.reporter.narrative``; names re-exported as the same objects (no code here)."""
# BASE module-level imports kept verbatim for attribute compatibility (same objects as at BASE)
from typing import Any, Dict, List, Mapping  # noqa: F401
from libs.reporting.trade_report_common import clip_text as clip, format_pct, safe_float, safe_int  # noqa: F401
from libs.agents.reporter.narrative.scanner_basis import (  # noqa: F401
    _korea_indices_bullet,
    _top_numeric_drivers,
    _scanner_chart_fit_payload,
    _scanner_macro_chart_fit_payload,
    _candidate_sources_from_score_breakdown,
    _selection_basis_from_scores,
)
from libs.agents.reporter.narrative.scanner_selection_trace import (  # noqa: F401
    _scanner_candidate_row_from_evidence,
    _build_scanner_selection_trace,
)
from libs.agents.reporter.narrative.scanner_evidence_fit import (  # noqa: F401
    _scanner_chart_fit_from_scanner_evidence,
    _scanner_macro_chart_fit_from_scanner_evidence,
    _normalized_feature_coverage_from_scanner_evidence,
)
