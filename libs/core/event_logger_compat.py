from __future__ import annotations

import inspect
from typing import Any


class _NodeEventLogger:
    """Bridge legacy `start/end` node callers to the current JSONL logger."""

    def __init__(self, name: str, logger: Any) -> None:
        self.node = name
        self._logger = logger
        self._run_id = __import__("uuid").uuid4().hex

    def start(self, payload: Any = None) -> Any:
        return self._logger.log(
            run_id=self._run_id, stage=self.node, event="start", payload=payload if isinstance(payload, dict) else {}
        )

    def end(self, payload: Any = None) -> Any:
        return self._logger.log(
            run_id=self._run_id, stage=self.node, event="end", payload=payload if isinstance(payload, dict) else {}
        )

    def __getattr__(self, attr: str) -> Any:
        # ``copy`` may ask a partially constructed instance for special
        # methods before ``_logger`` has been restored.  Going through normal
        # attribute lookup here would recurse back into this method.
        logger = self.__dict__.get("_logger")
        if logger is None or attr == "_logger" or attr.startswith("__"):
            raise AttributeError(attr)
        return getattr(logger, attr)


def get_event_logger(name: str):
    """Create EventLogger in a backward-compatible way.

    Some project versions define EventLogger(__init__(node=...)),
    others define EventLogger(name) or EventLogger() with node set later.
    """
    from libs.core.event_logger import EventLogger  # local import to avoid circular deps

    # 1) keyword-style
    try:
        return EventLogger(node=name)  # type: ignore
    except TypeError:
        pass

    # The current dataclass accepts a positional `log_path`. Passing the
    # node name positionally therefore creates a logger at the wrong path and
    # leaves legacy `start/end` callers as silent no-ops. Adapt that shape
    # before considering historical positional-name implementations.
    try:
        if "log_path" in inspect.signature(EventLogger).parameters:
            from libs.core.event_logger import resolve_event_log_path

            return _NodeEventLogger(name, EventLogger(log_path=resolve_event_log_path()))
    except (TypeError, ValueError):
        pass

    # 2) positional name for historical implementations
    try:
        return EventLogger(name)  # type: ignore
    except TypeError:
        pass

    # 3) no-arg + set attribute if possible
    logger = EventLogger()  # type: ignore
    try:
        setattr(logger, "node", name)
    except Exception:
        pass
    return logger
