"""RF-050 libs/llm/model_catalog_store: derivations, card building, fake-fetch sync and cached fallback (tmp catalog dir only).

``urlopen`` (imported into the module namespace) is replaced and socket.connect is denied. Every catalog directory is
under tmp_path; the default ``data/model_catalog`` is never touched. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
import socket

import pytest

from libs.llm import model_catalog_store as mc


@pytest.fixture(autouse=True)
def _offline(monkeypatch, tmp_path):
    def deny(*_a, **_k):
        raise AssertionError("real network attempted")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.chdir(tmp_path)


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


class _Resp:
    def __init__(self, body):
        self._b = body

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _models(*rows):
    return json.dumps({"data": list(rows)}).encode("utf-8")


def test_small_derivations():
    _eq((mc._safe_float("1.5"), mc._safe_float("x", 2), mc._safe_float(None)), (1.5, 2.0, 0.0))
    _eq((mc._provider_from_model_id("openai/gpt-4.1"), mc._provider_from_model_id("nope"), mc._provider_from_model_id(None)), ("openai", "", ""))
    _eq([mc._supports_json({"supported_parameters": p}) for p in (["response_format"], ["Structured_Outputs"], ["tools"], "x", None)], [True, True, False, False, False])
    price = lambda p, c: {"pricing": {"prompt": p, "completion": c}}
    _eq([mc._derive_cost_tier(r) for r in (price(0, 0), {}, price("0.000001", "0.000001"), price("0.00001", "0.000005"), price("0.00005", 0))],
        ["free", "free", "low", "medium", "high"])
    # boundaries: <= 2e-6 is low, <= 2e-5 is medium (inclusive), anything above is the next tier
    _eq([mc._derive_cost_tier(price(a, 0)) for a in ("0.000002", "0.0000025", "0.00002", "0.0000201")], ["low", "medium", "medium", "high"])
    _eq([mc._derive_latency_tier({"id": i, "name": n}) for i, n in (("x/fast-1", ""), ("x/m", "Gemini Flash"), ("x/a:free", ""), ("x/deep-r1", ""), ("x/claude-opus", ""), ("x/plain", "Plain"))],
        ["fast", "fast", "fast", "slow", "slow", "medium"])
    _eq(mc._derive_latency_tier({"id": "x/mini-reasoning"}), "fast")                      # a fast token wins over a slow token


def test_reliability_override_then_json_support_then_unknown():
    known = next(iter(mc.STATIC_MODEL_CARD_OVERRIDES))
    _eq(mc._derive_reliability({"id": known}), mc.STATIC_MODEL_CARD_OVERRIDES[known]["reliability"])
    _eq(mc._derive_reliability({"id": "x/unknown", "supported_parameters": ["response_format"]}), "medium")
    _eq(mc._derive_reliability({"id": "x/unknown"}), "unknown")


def test_tags_are_sorted_union_of_heuristics_and_static_overrides():
    row = {"id": "x/fast-kimi-k2.5", "context_length": 250_000, "pricing": {"prompt": 0, "completion": 0}, "supported_parameters": ["response_format"]}
    _eq(mc._derive_tags(row), ["cheap", "fast", "json_stable", "long_context", "reasoning", "report_quality"])
    _eq(mc._derive_tags({"id": "x/plain", "context_length": 1000, "pricing": {"prompt": "0.1", "completion": "0.1"}}), [])
    override_id = next(k for k, v in mc.STATIC_MODEL_CARD_OVERRIDES.items() if v.get("tags"))
    if not set(mc.STATIC_MODEL_CARD_OVERRIDES[override_id]["tags"]) <= set(mc._derive_tags({"id": override_id, "pricing": {"prompt": 1, "completion": 1}})):
        raise AssertionError("static override tags must always be merged")


def test_cards_payload_skips_bad_rows_sorts_by_id_and_applies_overrides():
    override_id = next(iter(mc.STATIC_MODEL_CARD_OVERRIDES))
    payload = {"model_count": 5, "data": [
        {"id": "z/last", "name": "Z", "context_length": "123", "pricing": {"prompt": "0.000001", "completion": 0}},
        "junk", {"id": ""}, {"name": "no id"},
        {"id": override_id, "name": "Over"},
        {"id": "a/first", "pricing": "bad"},
    ]}
    out = mc.build_model_cards_payload(payload)
    _eq([c["model_id"] for c in out["cards"]], sorted(["z/last", override_id, "a/first"]))
    _eq((out["card_count"], out["source_model_count"], out["source"]), (3, 5, "openrouter"))
    by = {c["model_id"]: c for c in out["cards"]}
    _eq((by["z/last"]["context_window"], by["z/last"]["cost_tier"], by["z/last"]["display_name"], by["z/last"]["provider"]), (123, "low", "Z", "z"))
    _eq(by["a/first"]["display_name"], "a/first")                                         # name falls back to the id
    ov = mc.STATIC_MODEL_CARD_OVERRIDES[override_id]
    _eq((by[override_id]["cost_tier"], by[override_id]["latency_tier"], by[override_id]["recommended_roles"]), (ov["cost_tier"], ov["latency_tier"], ov["recommended_roles"]))
    with pytest.raises(AttributeError):
        mc.build_model_cards_payload("junk")                                               # current contract: the data guard is bypassed by the later .get() on a non-dict
    _eq(mc.build_model_cards_payload({"data": []})["source_model_count"], 0)


def test_fetch_uses_float_timeout_and_wraps_the_payload(monkeypatch):
    seen = {}

    def fake(url, timeout):
        seen.update(url=url, timeout=timeout)
        return _Resp(_models({"id": "a/b"}, {"id": "c/d"}))

    monkeypatch.setattr(mc, "urlopen", fake)
    out = mc.fetch_openrouter_models(url="https://or.invalid/models", timeout_sec=3)
    _eq((seen["url"], seen["timeout"], out["model_count"], out["fetch_status"], out["source_url"]), ("https://or.invalid/models", 3.0, 2, "ok", "https://or.invalid/models"))
    monkeypatch.setattr(mc, "urlopen", lambda url, timeout: _Resp(b'["not-a-dict"]'))
    _eq(mc.fetch_openrouter_models()["model_count"], 0)                                   # a non-object body yields an empty list


def test_sync_success_writes_raw_and_cards_only_under_the_given_catalog_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(mc, "urlopen", lambda url, timeout: _Resp(_models({"id": "b/m", "context_length": 10}, {"id": "a/m"})))
    root = tmp_path / "catalog"
    out = mc.sync_openrouter_model_catalog(catalog_dir=root)
    _eq(out["fetch_source"], "remote")
    raw, cards = json.loads((root / "openrouter_models.json").read_text(encoding="utf-8")), json.loads((root / "model_cards.json").read_text(encoding="utf-8"))
    _eq((raw["fetch_status"], len(raw["data"]), cards["fetch_source"], [c["model_id"] for c in cards["cards"]]), ("ok", 2, "remote", ["a/m", "b/m"]))
    _eq(sorted(p.name for p in tmp_path.iterdir()), ["catalog"])                          # the default data/model_catalog is untouched
    _eq(mc.get_model_card("a/m", path=root / "model_cards.json")["model_id"], "a/m")
    _eq(mc.get_model_card("zzz", cards_payload=cards), {})
    _eq([c["model_id"] for c in mc.list_models_by_tag(" JSON_STABLE ", cards_payload={"cards": [{"model_id": "x", "tags": ["json_stable"]}, "junk", {"model_id": "y", "tags": ["fast"]}]})], ["x"])
    _eq(mc.list_models_by_tag("", cards_payload={"cards": [{"tags": ["a"]}]}), [])      # an empty tag matches nothing


def test_sync_failure_falls_back_to_the_cached_raw_file_and_rewrites_it(monkeypatch, tmp_path):
    root = tmp_path / "catalog"
    root.mkdir()
    (root / "openrouter_models.json").write_text(json.dumps({"fetched_at": "old", "model_count": 1, "data": [{"id": "c/cached"}]}), encoding="utf-8")

    def boom(url, timeout):
        raise TimeoutError("slow")

    monkeypatch.setattr(mc, "urlopen", boom)
    out = mc.sync_openrouter_model_catalog(catalog_dir=root)
    _eq(out["fetch_source"], "cached_fallback")
    raw = json.loads((root / "openrouter_models.json").read_text(encoding="utf-8"))
    _eq((raw["fetch_status"], raw["fetch_error"], raw["fetched_at"]), ("cached_fallback", "TimeoutError:slow", "old"))   # the cached copy is rewritten with the error marker
    _eq([c["model_id"] for c in json.loads((root / "model_cards.json").read_text(encoding="utf-8"))["cards"]], ["c/cached"])
    with pytest.raises(TimeoutError):
        mc.sync_openrouter_model_catalog(catalog_dir=root, allow_cached_fallback=False)
    with pytest.raises(TimeoutError):
        mc.sync_openrouter_model_catalog(catalog_dir=tmp_path / "empty")               # no cache -> the original error propagates
    if (tmp_path / "empty").exists():
        raise AssertionError("a failed sync without a cache must not create the directory")
