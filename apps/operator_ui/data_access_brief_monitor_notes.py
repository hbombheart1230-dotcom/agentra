"""Legacy import alias; canonical read-only implementation lives in a domain package."""
import sys
from apps.operator_ui.brief_parts.input import monitor_notes as _owner
sys.modules[__name__] = _owner
