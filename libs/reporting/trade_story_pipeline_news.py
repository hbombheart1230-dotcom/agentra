"""Compatibility facade: implementations live in ``libs.agents.reporter.narrative``; names re-exported as the same objects (no code here)."""
# BASE module-level imports kept verbatim for attribute compatibility (same objects as at BASE)
import html  # noqa: F401
import re  # noqa: F401
from typing import Any, Dict, List, Mapping  # noqa: F401
from libs.core.symbols import normalize_symbol  # noqa: F401
from libs.reporting.trade_report_common import clip_text as clip, list_text as _list_text, safe_float  # noqa: F401
from libs.agents.reporter.narrative.news_text import (  # noqa: F401
    _headline_text,
    _clean_news_fragment,
    _news_item_field,
    _news_sample_parts,
    _norm_symbol_text,
    _symbol_name_from_text,
    _sample_title_directly_matches_symbol,
    _format_symbol_news_headline,
)
from libs.agents.reporter.narrative.news_headlines import (  # noqa: F401
    _collect_symbol_headlines_from_ranked_rows,
    _headline_matches_symbol,
    _collect_top_headlines,
    _title_prefixed_symbol,
    _list_text_for_symbol,
    _optional_float,
)
from libs.agents.reporter.narrative.news_scanner_contribution import (  # noqa: F401
    _build_news_scanner_contribution_trace,
    _attach_news_scanner_contribution,
)
