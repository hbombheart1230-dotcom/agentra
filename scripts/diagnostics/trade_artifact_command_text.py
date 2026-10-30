from __future__ import annotations
from typing import Any, Dict, List, Tuple


def _command_to_text(command: List[str], facade=None) -> str:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    return " ".join(str(part) for part in command)
