from __future__ import annotations

from typing import Any


def build_broker_alignment(
    *,
    _metadata_value: Any, broker_account_snapshot: Any, broker_alignment: Any, broker_alignment_summary: Any,
) -> dict:
    """Preserve the canonical broker_alignment input contract and value evaluation order."""
    return {
            "status": _metadata_value(broker_alignment.get("status")),
            "generated_at": _metadata_value(broker_alignment.get("generated_at")),
            "report_json_path": _metadata_value(broker_alignment.get("report_json_path")),
            "account_snapshot_path": _metadata_value(broker_account_snapshot.get("path")),
            "account_snapshot_status": _metadata_value(broker_account_snapshot.get("status")),
            "account_snapshot_api_call_count": broker_account_snapshot.get("api_call_count"),
            "account_snapshot_ok_count": broker_account_snapshot.get("ok_count"),
            "account_snapshot_error_count": broker_account_snapshot.get("error_count"),
            "local_total": broker_alignment_summary.get("local_total"),
            "broker_total": broker_alignment_summary.get("broker_total"),
            "matched_by_ord_no": broker_alignment_summary.get("matched_by_ord_no"),
            "missing_in_local_total": broker_alignment_summary.get("missing_in_local_total"),
            "missing_in_broker_total": broker_alignment_summary.get("missing_in_broker_total"),
            "error": _metadata_value(broker_alignment.get("error")),
        }
