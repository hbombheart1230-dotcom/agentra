"""Compatibility alias: canonical implementation moved to libs.reporting.trade_report.compact_helpers.

Do not add runtime logic here. Remove only after all legacy imports migrate.
"""

import importlib as _importlib
import sys as _sys

_sys.modules[__name__] = _importlib.import_module("libs.reporting.trade_report.compact_helpers")
