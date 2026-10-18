"""Test-only raw inputs, never authority outputs or production reports."""
import hashlib
import json
from pathlib import Path, PurePosixPath

FIXTURE = Path(__file__).parent / "fixtures/uef9_synthetic/reports_inputs.json"
FIXTURE_SHA256 = "3073b0b1e8b5bcdcdc5e444b1cade06946c84c6fa50e9fc0848aec0f2f413ed0"
THROUGH_DAY = "2026-09-25"


def fixture_payload(path=FIXTURE):
    raw = path.read_bytes()  # Missing/unreadable fixtures must fail, never fall back.
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA256:
        raise ValueError("UEF9 synthetic fixture digest mismatch")
    payload = json.loads(raw)
    if payload["schema_version"] != "agentra.synthetic.uef9-inputs.v1" or payload["through_day"] != THROUGH_DAY:
        raise ValueError("UEF9 synthetic fixture schema/day mismatch")
    return payload


def materialize_reports(reports_root, *, fixture_path=FIXTURE):
    payload = fixture_payload(fixture_path)
    root = Path(reports_root)
    if root.is_symlink() or root.exists():
        raise ValueError("UEF9 fixture requires a fresh nonsymlink reports_root")
    # Validate every path before creating anything. No fixture-controlled escape.
    paths = [PurePosixPath(name) for name in payload["artifacts"]]
    if any(p.is_absolute() or ".." in p.parts or "\\" in str(p) or ":" in str(p) for p in paths):
        raise ValueError("UEF9 fixture path escape")
    root.mkdir(parents=True)
    for name, data in payload["artifacts"].items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((json.dumps(data, sort_keys=True) + "\n").encode("utf-8"))
    return root


def validate_reports(reports_root):
    """Detect any missing/changed/extra raw input before invoking production code."""
    root = Path(reports_root)
    expected = fixture_payload()["artifacts"]
    if root.is_symlink() or set(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()) != set(expected):
        raise ValueError("UEF9 synthetic reports file set mismatch")
    for name, data in expected.items():
        path = root / name
        if path.is_symlink() or path.read_bytes() != (json.dumps(data, sort_keys=True) + "\n").encode("utf-8"):
            raise ValueError("UEF9 synthetic reports content mismatch: " + name)
