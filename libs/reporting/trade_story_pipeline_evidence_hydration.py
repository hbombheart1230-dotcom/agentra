from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from libs.reporting.trade_report_common import clip_text as clip, safe_float, safe_int


from .trade_story_evidence_parts.canonical import (
    safe_read_json_file,
    hydrate_canonical_agent_artifacts,
    resolve_selection_monitor_artifact,
)

from .trade_story_evidence_parts.scanner import (
    enrich_scanner_reason_from_evidence,
)

from .trade_story_evidence_parts.filters import (
    enrich_filters_from_evidence,
)
