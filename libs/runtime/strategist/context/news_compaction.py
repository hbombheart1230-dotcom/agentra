"""S1-057 identity compatibility alias; one canonical implementation."""
import sys as _sys
from libs.agents.strategist.context import news_compaction as _canonical
_sys.modules[__name__] = _canonical
