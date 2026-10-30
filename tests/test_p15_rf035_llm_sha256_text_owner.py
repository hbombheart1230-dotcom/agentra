"""P15 RF-035: llm_artifacts _sha256_text moved to llm_artifacts_hash_projection; parity with the pre-move body."""
from __future__ import annotations

import hashlib

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_hash_projection as owner

import pytest

E = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


@pytest.mark.parametrize("raw,expected", [
    ("abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
    ("", E), (None, E), (0, E),
])
def test_values(raw, expected):
    assert m._sha256_text(raw) == expected
    assert owner.sha256_text(raw, facade=m) == expected


def test_unicode_bytes():
    assert m._sha256_text("한") == hashlib.sha256("한".encode("utf-8")).hexdigest() == owner.sha256_text("한", facade=m)


def test_facade_hashlib_seam(monkeypatch):
    calls = []
    real = hashlib.sha256
    monkeypatch.setattr(m.hashlib, "sha256", lambda b: (calls.append(b), real(b))[1])
    m._sha256_text("x")
    owner.sha256_text("x", facade=m)
    assert calls == [b"x", b"x"]
