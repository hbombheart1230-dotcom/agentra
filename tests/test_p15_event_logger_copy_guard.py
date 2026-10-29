"""Regression coverage for copying the legacy node logger bridge."""

import copy
import unittest

from libs.core.event_logger_compat import _NodeEventLogger


class _FakeLogger:
    def __init__(self):
        self.events = []
        self.public_value = "delegated"

    def log(self, *, run_id, stage, event, payload):
        self.events.append((run_id, stage, event, payload))


class NodeEventLoggerCopyGuardTests(unittest.TestCase):
    def test_copying_and_delegation_preserve_bridge_contract(self):
        fake = _FakeLogger()
        logger = _NodeEventLogger("node_x", fake)

        shallow = copy.copy(logger)
        deep = copy.deepcopy(logger)

        for copied in (shallow, deep):
            self.assertEqual(copied.node, "node_x")
            self.assertEqual(copied._run_id, logger._run_id)

        logger.start("not-a-dict")
        logger.end(None)
        self.assertEqual(
            fake.events,
            [
                (logger._run_id, "node_x", "start", {}),
                (logger._run_id, "node_x", "end", {}),
            ],
        )
        self.assertEqual(logger.public_value, "delegated")
        with self.assertRaises(AttributeError):
            logger.missing_public_value


if __name__ == "__main__":
    unittest.main()
