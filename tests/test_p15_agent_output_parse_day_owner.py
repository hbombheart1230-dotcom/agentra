from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from libs.contracts.agent_output_parts.artifact_metadata import parse_day_from_timestamp
def test_parse_day_cases():
    f=SimpleNamespace(datetime=datetime,kst_day_str=lambda d:(d+timedelta(hours=9)).date().isoformat())
    assert parse_day_from_timestamp('2026-10-29T18:00:00Z',facade=f)=='2026-10-30'; assert parse_day_from_timestamp('2026-10-29',facade=f)=='2026-10-29'; assert parse_day_from_timestamp('2026-10-29 bad',facade=f)=='2026-10-29'; assert parse_day_from_timestamp('invalid',facade=f)==''
