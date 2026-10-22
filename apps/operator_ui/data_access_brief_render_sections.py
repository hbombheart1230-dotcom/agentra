"""Legacy import alias; canonical read-only implementation lives in a domain package."""
import sys
from apps.operator_ui.brief_parts.render import sections as _owner
sys.modules[__name__] = _owner
