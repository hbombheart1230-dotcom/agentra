"""Public pure Monitor role contracts.

The graph node remains the compatibility facade while P1.5.6 moves only
verified deterministic boundaries behind this package.
"""

from .contracts import MonitorAgentInput, MonitorAgentResult

__all__ = ["MonitorAgentInput", "MonitorAgentResult"]
