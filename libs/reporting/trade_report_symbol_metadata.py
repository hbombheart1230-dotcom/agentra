"""Compatibility facade: Reporter symbol-metadata helpers live in ``libs.agents.reporter.read_models.symbol_metadata_*``.

Public names are re-exported (same function/dict objects); there is no second implementation here."""
# BASE module-level imports kept verbatim for attribute compatibility (same objects as at BASE)
import re  # noqa: F401
from typing import Any, Callable, Dict, Iterable, List  # noqa: F401
from libs.agents.reporter.read_models.symbol_metadata_fallbacks import (  # noqa: F401
    SYMBOL_NAME_FALLBACKS,
    SYMBOL_THEME_FALLBACKS,
)
from libs.agents.reporter.read_models.symbol_metadata_text import (  # noqa: F401
    clip_text,
    as_dict,
    listify,
    append_unique_text,
    append_theme_values,
)
from libs.agents.reporter.read_models.symbol_metadata_sources import (  # noqa: F401
    iter_trade_symbol_metadata_sources,
    symbol_in_theme_components,
    iter_nested_dicts,
    component_themes_for_symbol,
)
from libs.agents.reporter.read_models.symbol_metadata_name_inference import (  # noqa: F401
    looks_like_symbol_name,
    infer_symbol_name_from_report_text,
)
from libs.agents.reporter.read_models.symbol_metadata_resolution import (  # noqa: F401
    resolve_trade_symbol_metadata,
)
