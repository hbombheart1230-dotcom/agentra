"""P15 C02-5: model card generation tolerates non-object input and malformed context_length rows."""
from __future__ import annotations

import copy
import json

import pytest

from libs.llm import model_catalog_store as mc


@pytest.mark.parametrize("junk", [None, "junk", [], 7, ["a"]])
def test_non_dict_input_yields_empty_valid_payload(junk):
    out = mc.build_model_cards_payload(junk)
    assert (out["cards"], out["card_count"], out["source_model_count"], out["source"]) == ([], 0, 0, "openrouter")
    assert "generated_at" in out
    json.dumps(out, allow_nan=False)


@pytest.mark.parametrize("data", ["abc", {"id": "x/y"}, None, 5])
def test_non_list_data_is_ignored(data):
    out = mc.build_model_cards_payload({"data": data})
    assert out["cards"] == [] and out["source_model_count"] == 0


def test_bad_context_length_rows_keep_good_cards_and_zero_window():
    payload = {"data": [{"id": "provider/good", "context_length": 2048}, {"id": "provider/bad", "context_length": "n/a"}, None]}
    snapshot = copy.deepcopy(payload)
    out = mc.build_model_cards_payload(payload)
    assert payload == snapshot                                                         # input unchanged
    assert [c["model_id"] for c in out["cards"]] == ["provider/bad", "provider/good"]
    by = {c["model_id"]: c for c in out["cards"]}
    assert by["provider/good"]["context_window"] == 2048 and by["provider/bad"]["context_window"] == 0
    assert "long_context" not in by["provider/good"]["tags"] and "long_context" not in by["provider/bad"]["tags"]
    assert out["card_count"] == 2 and out["source_model_count"] == 2
    json.dumps(out, allow_nan=False)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), -5, [], {}, object(), "", None])
def test_context_length_edge_values_normalize_to_zero_without_raising(value):
    out = mc.build_model_cards_payload({"data": [{"id": "p/m", "context_length": value}]})
    assert out["cards"][0]["context_window"] == 0 and "long_context" not in out["cards"][0]["tags"]
    assert mc._derive_tags({"id": "p/m", "context_length": value}) == out["cards"][0]["tags"]


def test_valid_large_context_keeps_long_context_and_numeric_strings_still_parse():
    out = mc.build_model_cards_payload({"data": [{"id": "p/big", "context_length": 200000}, {"id": "p/str", "context_length": "300000"}, {"id": "p/flt", "context_length": 250000.0}]})
    by = {c["model_id"]: c for c in out["cards"]}
    assert all("long_context" in c["tags"] for c in by.values())
    assert (by["p/big"]["context_window"], by["p/str"]["context_window"], by["p/flt"]["context_window"]) == (200000, 300000, 250000)
    assert "long_context" not in mc._derive_tags({"id": "p/small", "context_length": 199999})


@pytest.mark.parametrize("count", ["bad", [], {}, None, 0, ""])
def test_bad_model_count_falls_back_to_card_count(count):
    out = mc.build_model_cards_payload({"model_count": count, "data": [{"id": "a/x"}, {"id": "b/y"}]})
    assert out["source_model_count"] == 2


def test_valid_model_count_and_static_override_rows_regress_unchanged():
    override_id = next(iter(mc.STATIC_MODEL_CARD_OVERRIDES))
    out = mc.build_model_cards_payload({"model_count": 9, "data": [{"id": override_id, "context_length": "bad"}, {"id": "a/first", "pricing": "bad"}]})
    assert out["source_model_count"] == 9 and [c["model_id"] for c in out["cards"]] == sorted([override_id, "a/first"])
    card = next(c for c in out["cards"] if c["model_id"] == override_id)
    ov = mc.STATIC_MODEL_CARD_OVERRIDES[override_id]
    assert (card["cost_tier"], card["latency_tier"], card["reliability"], card["recommended_roles"]) == (ov["cost_tier"], ov["latency_tier"], ov["reliability"], ov["recommended_roles"])
    assert set(ov["tags"]) <= set(card["tags"]) and card["context_window"] == 0
