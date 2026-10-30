"""P15 RF-035 (00h): llm_daily_summary._is_dry_run moved to llm_daily_summary_env_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import llm_daily_summary as m
from libs.reporting import llm_daily_summary_env_projection as owner


@pytest.mark.parametrize("val,expected", [("1", True), ("true", True), ("True", True), (" 1 ", True), ("TRUE", False), ("0", False), ("", False), ("yes", False)])
def test_values(monkeypatch, val, expected):
    monkeypatch.setenv("DRY_RUN", val)
    assert m._is_dry_run() is expected and owner._is_dry_run(facade=m) is expected


def test_unset_defaults_false(monkeypatch):
    monkeypatch.delenv("DRY_RUN", raising=False)
    assert m._is_dry_run() is False and owner._is_dry_run(facade=m) is False


def test_getenv_read_at_use_time(monkeypatch):
    calls = []
    monkeypatch.setattr(m.os, "getenv", lambda k, d=None: (calls.append((k, d)), "1")[1])
    assert m._is_dry_run() is True and owner._is_dry_run(facade=m) is True
    assert calls == [("DRY_RUN", "0"), ("DRY_RUN", "0")]
    monkeypatch.setattr(m.os, "getenv", lambda k, d=None: None)
    assert m._is_dry_run() is False and owner._is_dry_run(facade=m) is False
