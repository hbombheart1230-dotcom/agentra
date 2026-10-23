"""Legacy import alias; canonical read-only implementation lives in a domain package."""
import sys
from apps.operator_ui.read_models import trades as _owner
sys.modules[__name__] = _owner
