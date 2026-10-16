"""S1-057 identity compatibility alias; one canonical implementation."""
import sys as _sys
from libs.agents.strategist.context import market_key_events as _canonical
_sys.modules[__name__] = _canonical
