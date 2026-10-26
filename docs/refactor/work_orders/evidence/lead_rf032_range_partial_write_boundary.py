"""RF-032 independent lead synthetic partial-write boundary, extracted exact function.
Source: integration/p1.5 libs/reporting/evaluation/attribution_score_range.py
Git blob: ea17c616ea0034b3711480aeb82a5021b2c2d52c
Function FNV32: 56b1c387 (ASCII exact source).
Local lead test (same extracted function and scenarios): normal 16 PASS, -O 16 PASS, exit 0.
Do not run on operating data; tmp-only.
"""
import json
import tempfile
from pathlib import Path

EXACT_FUNCTION = "def write_attribution_score_range(\n    *,\n    reports_root: Path = Path(\"reports\"),\n    start: str,\n    end: str,\n    include_empty_days: bool = False,\n) -> dict[str, str]:\n    reports_root = Path(reports_root)\n    payload = build_attribution_score_range(\n        reports_root=reports_root,\n        start=start,\n        end=end,\n        include_empty_days=include_empty_days,\n    )\n    out_dir = reports_root / \"evaluation\" / \"range\" / f\"{start}_{end}\"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    json_path = out_dir / \"attribution_score_range.json\"\n    md_path = out_dir / \"attribution_score_range.md\"\n    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + \"\\n\", encoding=\"utf-8\")\n    md_path.write_text(render_attribution_score_range(payload), encoding=\"utf-8\")\n    return {\"json\": str(json_path), \"markdown\": str(md_path)}"
def fnv32(value):
    h = 2166136261
    for byte in value.encode("utf-8"):
        h = ((h ^ byte) * 16777619) & 0xffffffff
    return f"{h:08x}"
def check(ok, label):
    global count
    if not ok: raise SystemExit("FAIL " + label)
    count += 1
count = 0
check(fnv32(EXACT_FUNCTION) == "56b1c387", "exact function")
with tempfile.TemporaryDirectory(prefix="rf032_lead_") as temp:
    root = Path(temp).resolve()
    calls, generation, fault, attempted = [], [1], [None], []
    def build_attribution_score_range(*, reports_root, start, end, include_empty_days):
        calls.append((reports_root, start, end, include_empty_days))
        if start == "BAD": raise ValueError("synthetic date")
        return {"schema_version":"attribution_score_range.v1", "revision":generation[0], "ko":"테스트"}
    def render_attribution_score_range(payload):
        return f"# revision {payload['revision']}\n"
    scope = {"Path":Path, "json":json, "build_attribution_score_range":build_attribution_score_range,
             "render_attribution_score_range":render_attribution_score_range}
    exec(compile(EXACT_FUNCTION, "<RF032 exact function>", "exec"), scope)
    run = scope["write_attribution_score_range"]
    original = Path.write_text
    def guarded(path, content, *args, **kwargs):
        dest = path.resolve()
        if not dest.is_relative_to(root): raise SystemExit("FAIL OUTSIDE_WRITE")
        attempted.append(str(dest))
        if fault[0] == dest.name: raise OSError("synthetic write error")
        return original(path, content, *args, **kwargs)
    Path.write_text = guarded
    try:
        result = run(reports_root=root, start="2026-10-01", end="2026-10-02", include_empty_days=True)
        j, m = Path(result["json"]), Path(result["markdown"])
        check(j.is_file() and m.is_file(), "two files")
        check(j.resolve().is_relative_to(root) and m.resolve().is_relative_to(root), "tmp paths")
        check(json.loads(j.read_text())["ko"] == "테스트", "unicode json")
        check(m.read_text() == "# revision 1\n", "markdown")
        check(calls[-1] == (root, "2026-10-01", "2026-10-02", True), "args")
        oldj, oldm = j.read_bytes(), m.read_bytes()
        run(reports_root=root, start="2026-10-01", end="2026-10-02", include_empty_days=True)
        check(j.read_bytes() == oldj and m.read_bytes() == oldm, "idempotent")
        check(len(attempted) == 4, "writes")
        generation[0] = 2
        fault[0] = "attribution_score_range.json"
        try: run(reports_root=root, start="2026-10-01", end="2026-10-02")
        except OSError: check(True, "json OSError")
        else: check(False, "json must fail")
        check(j.read_bytes() == oldj and m.read_bytes() == oldm, "json fail unchanged")
        fault[0] = "attribution_score_range.md"
        try: run(reports_root=root, start="2026-10-01", end="2026-10-02")
        except OSError: check(True, "md OSError")
        else: check(False, "md must fail")
        check(json.loads(j.read_text())["revision"] == 2, "json updated")
        check(m.read_bytes() == oldm, "md stale")
        fault[0] = None
        try: run(reports_root=root, start="BAD", end="2026-10-02")
        except ValueError: check(True, "build ValueError")
        else: check(False, "bad date")
        check(not (root/"evaluation"/"range"/"BAD_2026-10-02").exists(), "no failed output")
        check(all(Path(p).is_relative_to(root) for p in attempted), "no outside write")
    finally:
        Path.write_text = original
print(f"RF032_LEAD_RANGE_PARTIAL_WRITE_OK cases={count} source_fnv=56b1c387 partial_md_failure=json_new_md_stale outside_writes=0")
