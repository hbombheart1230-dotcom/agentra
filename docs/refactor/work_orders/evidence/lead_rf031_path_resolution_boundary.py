from pathlib import Path
import os
from unittest.mock import patch

# Exact pure functions extracted from integration/p1.5 source blobs:
# reporter_analysis.py 9b7963ffa5930d4cbbbc27dca1f48cc58402677f
# event_log_reader.py e1d39ff2571e9c66d987a040cae62004b519e839
# Full modules and writer entrypoints NOT executed.
def _canonical_reports_root(path: Path) -> Path:
    candidate = Path(path)
    for parent in (candidate, *candidate.parents):
        if parent.name == "reports":
            return parent
    return candidate


def _cache_dir(path: Path) -> Path:
    configured = str(os.getenv("EVENT_LOG_DAY_CACHE_DIR") or "").strip()
    if configured:
        return Path(configured)
    return Path(path).parent / ".day_cache"


def check(ok, label):
    if not ok:
        raise SystemExit("FAIL:" + label)

cases = [
    ("/tmp/lead/reports", "/tmp/lead/reports"),
    ("/tmp/lead/reports/reporter", "/tmp/lead/reports"),
    ("/tmp/lead/reports/a/b/c", "/tmp/lead/reports"),
    ("/tmp/lead/Reports/a", "/tmp/lead/Reports/a"),
    ("/tmp/lead/myreports/a", "/tmp/lead/myreports/a"),
    ("/tmp/lead/notreports/a", "/tmp/lead/notreports/a"),
    ("/tmp/lead/reports/a/reports/b", "/tmp/lead/reports/a/reports"),
    ("/tmp/lead/elsewhere", "/tmp/lead/elsewhere"),
    ("relative/reports/sub", "relative/reports"),
    ("relative/elsewhere", "relative/elsewhere"),
]
for index, (src, expected) in enumerate(cases):
    check(_canonical_reports_root(Path(src)) == Path(expected), `root_${index}`)

with patch.dict(os.environ, {}, clear=True):
    check(_cache_dir(Path('/tmp/lead/events.jsonl')) == Path('/tmp/lead/.day_cache'), 'cache_default')
    os.environ['EVENT_LOG_DAY_CACHE_DIR'] = '/tmp/lead/cache-override'
    check(_cache_dir(Path('/tmp/lead/events.jsonl')) == Path('/tmp/lead/cache-override'), 'cache_absolute')
    os.environ['EVENT_LOG_DAY_CACHE_DIR'] = ' relative_cache '
    check(_cache_dir(Path('/tmp/lead/events.jsonl')) == Path('relative_cache'), 'cache_relative')
    os.environ['EVENT_LOG_DAY_CACHE_DIR'] = '  '
    check(_cache_dir(Path('/tmp/lead/events.jsonl')) == Path('/tmp/lead/.day_cache'), 'cache_blank')
    del os.environ['EVENT_LOG_DAY_CACHE_DIR']
    check(_cache_dir(Path('events.jsonl')) == Path('.day_cache'), 'cache_relative_default')

print('RF031_PATH_RESOLUTION_EXTRACT_OK cases=15 writes=0 network=0 full_module=NOT_RUN')
