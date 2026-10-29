"""``_pid_active`` moved verbatim from live_execution_bundle_runner.py.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _pid_active(pid: int, *, facade: Any) -> bool:
    if int(pid or 0) <= 0:
        return False
    if facade.os.name == "nt":
        try:
            import ctypes

            process_query_limited_information = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(  # type: ignore[attr-defined]
                process_query_limited_information,
                False,
                int(pid),
            )
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)  # type: ignore[attr-defined]
                return True
            return False
        except Exception:
            return False
    try:
        facade.os.kill(int(pid), 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False
