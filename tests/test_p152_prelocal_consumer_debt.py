"""Never turn missing static facade references into deletion authority."""
from scripts.refactor.p152_prelocal_consumer_debt import build_debt_inventory


def test_every_public_facade_symbol_has_conservative_decision():
    record = build_debt_inventory()
    assert record["public_symbol_total"] == 436
    assert len(record["symbol_cases"]) == 436
    assert len(record["facades"]) == 3
    assert sum(q["public_symbols"] for q in record["facades"]) == 436
    assert record["statically_referenced_symbols"] + record["not_statically_found_not_dead"] == 436
    assert all(item["remote_recommendation"].startswith("KEEP_") for item in record["symbol_cases"])


def test_static_absence_is_never_dead_or_migration_approval():
    record = build_debt_inventory()
    assert record["evidence_scope"] == "STATIC_OFFLINE_ONLY_NO_LOCAL_RUNTIME_OR_DYNAMIC_PROOF"
    assert not record["deletion_authorized"]
    assert record["local_abi_and_runtime_consumer_gates"] == "NOT_RUN"
    assert record["p152"] == "OPEN" and record["p153"] == "NOT_AUTHORIZED"
    assert record["size_debt_requires_operator_decision"]
    for item in record["symbol_cases"]:
        assert item["dynamic_consumer_status"] == "UNRESOLVED_NO_LOCAL_CONSUMER_PROOF"
        assert not item["authority_to_delete_or_rename"]
        if item["external_static_references"] == 0:
            assert "KEEP" in item["remote_recommendation"]


def test_compatibility_wrapper_still_has_no_retirement_authority():
    record = build_debt_inventory()
    wrappers = [x for x in record["symbol_cases"] if x["declared_disposition"] == "WRAPPER"]
    assert wrappers
    assert all(x["remote_recommendation"] == "KEEP_WRAPPER_PENDING_LOCAL_PROOF" for x in wrappers)
