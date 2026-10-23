"""Legacy import alias; canonical read-only implementation lives in a domain package."""
import sys
from apps.operator_ui.read_models import overview as _owner
sys.modules[__name__] = _owner
