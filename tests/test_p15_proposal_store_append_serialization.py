"""P15 C02-4 (FAST-3): ProposalStore serializes before opening the file; failures never touch it. Explicit tmp path only."""
from __future__ import annotations

import hashlib
import json

import pytest

from libs.storage.proposal_store import ProposalStore


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_two_appends_keep_order_utf8_and_jsonl(tmp_path):
    path = tmp_path / "proposals.jsonl"
    store = ProposalStore(path)
    first, second = {"symbol": "005930", "memo": "한글"}, {"symbol": "000660", "memo": "ascii"}
    store.save(first)
    store.save(second)
    raw = path.read_bytes().decode("utf-8")
    assert raw.endswith("\n") and "한글" in raw and "\\u" not in raw
    assert [json.loads(l) for l in raw.splitlines()] == [first, second]
    assert first == {"symbol": "005930", "memo": "한글"}                          # input unchanged


def test_serialization_failure_leaves_existing_file_untouched(tmp_path):
    path = tmp_path / "proposals.jsonl"
    store = ProposalStore(path)
    store.save({"symbol": "005930", "memo": "한글"})
    before, size = _sha(path), path.stat().st_size
    with pytest.raises(TypeError):
        store.save({"bad": object()})
    assert _sha(path) == before and path.stat().st_size == size
    store.save({"after": 1})
    assert len(path.read_text(encoding="utf-8").splitlines()) == 2


def test_first_save_failure_on_new_path_creates_no_file(tmp_path):
    path = tmp_path / "sub" / "new.jsonl"
    store = ProposalStore(path)
    assert path.parent.is_dir() and not path.exists()                           # parent creation is the existing constructor contract
    with pytest.raises(TypeError):
        store.save({"bad": {1, 2}})
    assert not path.exists() and list(path.parent.iterdir()) == []


def test_nothing_is_created_outside_the_temp_root(tmp_path):
    before = {p for p in tmp_path.rglob("*")}
    store = ProposalStore(tmp_path / "p.jsonl")
    store.save({"a": 1})
    with pytest.raises(TypeError):
        store.save({"x": object()})
    assert {p.name for p in set(tmp_path.rglob("*")) - before} == {"p.jsonl"}


def test_default_path_constant_is_unchanged_statically():
    import inspect
    assert 'path="data/proposals.jsonl"' in inspect.getsource(ProposalStore.__init__)
