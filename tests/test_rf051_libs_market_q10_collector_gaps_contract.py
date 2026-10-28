"""RF-051 q10_index_observation_collector: manifest validation, claims and snapshot capture gaps.

Measured 88% before (lines 110, 128-136, 168, 176-180, 351-360, 389...). Everything uses tmp roots and
fake readers: no Kiwoom call, no broker, no network. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
import pytest

from libs.market import q10_index_observation_collector as q


DAY = "2026-10-28"


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _row(slot="09:30", availability="AVAILABLE", **kw):
    return {"requested_slot": slot, "availability": availability, "indices": {}, **kw}


def test_default_indices_slot_epoch_and_paths(tmp_path):
    _eq(q.default_indices(), ("KOSPI", "KOSDAQ"))
    _eq(q._slot_epoch("2026-10-28T10:00:00", "09:30"), q._slot_epoch(DAY, "09:30"))     # day truncated to 10 chars
    if q._slot_epoch(DAY, "10:00") - q._slot_epoch(DAY, "09:30") != 1800:
        raise AssertionError("slots are 30 minutes apart")
    p = q._manifest_path("2026-10-28 extra", root=tmp_path)
    _eq(p, tmp_path / DAY / "capture_manifest.json")
    _eq(q._claim_path(DAY, "09:30", root=tmp_path), tmp_path / DAY / "claims" / "0930.claim.json")
    _eq(q._empty_manifest("2026-10-28T09:00")["day"], DAY)


@pytest.mark.parametrize("value,reason_prefix", [
    ([], "top_level_not_dict:list"),
    ({"day": "2000-01-01", "slots": []}, "day_mismatch"),
    ({"day": DAY, "slots": "x"}, "slots_not_list:str"),
    ({"day": DAY, "slots": ["x"]}, "slot_row_not_dict:str"),
    ({"day": DAY, "slots": [{"requested_slot": "01:00", "availability": "AVAILABLE"}]}, "slot_row_missing_requested_slot"),
    ({"day": DAY, "slots": [_row(), _row()]}, "slot_row_missing_requested_slot"),        # duplicate slot
    ({"day": DAY, "slots": [_row(availability="NOPE")]}, "slot_state_invalid"),
    ({"day": DAY, "slots": [_row(indices="x")]}, "slot_indices_invalid"),
])
def test_manifest_structure_errors_are_never_silently_empty(value, reason_prefix):
    with pytest.raises(q.ManifestCorruptError) as exc:
        q._validate_manifest_structure(value, DAY)
    if not str(exc.value).startswith(reason_prefix):
        raise AssertionError((reason_prefix, str(exc.value)))


def test_valid_manifest_is_normalized_and_read_manifest_raises_on_corrupt_file(tmp_path):
    ok = q._validate_manifest_structure({"day": DAY, "slots": [_row("09:30"), _row("10:00", "PARTIAL")], "extra": 1}, DAY)
    _eq((ok["schema_version"], ok["behavior_effect"], [r["requested_slot"] for r in ok["slots"]]), (q.SCHEMA_VERSION, "observation_only", ["09:30", "10:00"]))
    if "extra" in ok:
        raise AssertionError("unknown top-level keys are dropped")
    p = tmp_path / "m.json"
    _eq(q._read_manifest(p, DAY), q._empty_manifest(DAY))          # missing file -> fresh manifest
    p.write_text("{bad", encoding="utf-8")
    with pytest.raises(q.ManifestCorruptError):
        q._read_manifest(p, DAY)                                   # corrupt file is an error, not "empty"
    p.write_text(json.dumps({"day": "other", "slots": []}), encoding="utf-8")
    with pytest.raises(q.ManifestCorruptError):
        q._read_manifest(p, DAY)
    p.write_text(json.dumps({"day": DAY, "slots": [_row()]}), encoding="utf-8")
    _eq(len(q._read_manifest(p, DAY + "T09:00")["slots"]), 1)       # day argument is truncated to 10 chars


def test_slot_claim_is_strictly_at_most_once_and_never_released(tmp_path):
    _eq(q._acquire_slot_claim(DAY, "09:30", root=tmp_path, current_pid=4242), True)
    _eq(q._acquire_slot_claim(DAY, "09:30", root=tmp_path, current_pid=1), False)       # existing claim is never reclaimed
    payload = json.loads(q._claim_path(DAY, "09:30", root=tmp_path).read_text(encoding="utf-8"))
    _eq((payload["pid"], payload["day"], payload["requested_slot"]), (4242, DAY, "09:30"))
    _eq(q._release_slot_claim(DAY, "09:30", root=tmp_path), None)                       # release is an intentional no-op
    _eq(q._acquire_slot_claim(DAY, "09:30", root=tmp_path), False)
    _eq(q._acquire_slot_claim(DAY, "10:00", root=tmp_path), True)                       # other slots are independent
    # Quirk pinned (no change made): `path.parent.mkdir(...)` runs OUTSIDE the try block, so an unusable claims
    # directory raises (NotADirectoryError) instead of failing closed with False; only open()/write errors give False.
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    with pytest.raises(OSError):
        q._acquire_slot_claim(DAY, "09:30", root=blocker)
    existing_dir_as_claim = q._claim_path(DAY, "11:00", root=tmp_path)
    existing_dir_as_claim.mkdir(parents=True)                                            # claim path is a directory
    _eq(q._acquire_slot_claim(DAY, "11:00", root=tmp_path), False)                        # open("x") fails -> fail closed


def test_capture_snapshot_success_failure_and_index_arguments():
    seen = {}

    class Reader:
        def get_index_packet(self, indices):
            seen["indices"] = indices
            return {"status": "ok", "indices": {"KOSPI": {"current": 1}}}

    out = q.capture_q10_index_snapshot(reader_factory=lambda: Reader())
    _eq((out["status"], seen["indices"]), ("ok", ("KOSPI", "KOSDAQ")))
    q.capture_q10_index_snapshot(indices=["KOSPI"], reader_factory=lambda: Reader())
    _eq(seen["indices"], ("KOSPI",))

    def boom():
        raise RuntimeError("no credentials")

    bad = q.capture_q10_index_snapshot(reader_factory=boom)
    _eq((bad["status"], bad["source"], bad["indices"], bad["error"]), ("unavailable", "kiwoom.ka20009", {}, "RuntimeError: no credentials"))

    class BadReader:
        def get_index_packet(self, indices):
            raise TimeoutError("slow")

    _eq(q.capture_q10_index_snapshot(reader_factory=lambda: BadReader())["error"], "TimeoutError: slow")   # never raises


def test_verification_evidence_requires_a_day_and_market_side_timestamps():
    row = {"KOSPI": {"current": 100.0}}
    _eq(q._has_verification_evidence(row, slot="09:30"), False)                                        # no day -> False
    _eq(q._has_verification_evidence(row, slot="09:30", day=DAY, observed_epoch=q._slot_epoch(DAY, "09:30")), False)   # no market timestamp
    epoch = q._slot_epoch(DAY, "09:30")
    from datetime import datetime, timezone
    iso = datetime.fromtimestamp(epoch + 10, tz=timezone.utc).isoformat()
    good = {"KOSPI": {"current": 100.0, "market_observed_at": iso}}
    _eq(q._has_verification_evidence(good, slot="09:30", day=DAY, observed_epoch=epoch + 20), True)
    _eq(q._has_verification_evidence(good, slot="15:30", day=DAY, observed_epoch=epoch + 20), False)    # close slot also needs finalization
