"""P1.5.2 saved snapshot compare: fail closed, no broker, no raw text leaks."""
import json

import pytest

from scripts.refactor.p152_snapshot_parity import compare_snapshots, main


def _put(root, relative, value):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return path


def test_identical_json_markdown_and_llm_trace_pass(tmp_path):
    before, after, out = (tmp_path / n for n in ("before", "after", "evidence.json"))
    for root in (before, after):
        _put(root, "reports/trades/TRD_1/reports/report.md", "# 한글 보고서\n")
        _put(root, "reports/trades/TRD_1/summary.json", '{"qty":1,"rank":2}\n')
        _put(root, "reports/trades/TRD_1/llm.jsonl", '{"model":"fake","retry":0,"messages":[{"content":"비밀"}]}\n')
    result = compare_snapshots(before, after, out=out,
                               llm_relative_path="reports/trades/TRD_1/llm.jsonl")
    assert result["byte_parity"] == "PASS"
    assert result["difference_count"] == 0
    assert result["compared_path_count"] == 3
    assert result["llm_capture"]["json_semantic_equal"]
    assert not result["authorizes_p152_completion"]
    assert out.is_file()
    assert "비밀" not in out.read_text(encoding="utf-8")


def test_reordered_json_keys_are_still_byte_drift(tmp_path):
    before, after = tmp_path / "before", tmp_path / "after"
    _put(before, "summary.json", '{"selected":"005930","rank":1}\n')
    _put(after, "summary.json", '{"rank":1,"selected":"005930"}\n')
    result = compare_snapshots(before, after)
    assert result["byte_parity"] == "FAIL"
    assert result["differences"][0]["kind"] == "BYTE_FORMAT_ONLY"


def test_semantic_drift_and_missing_files_are_not_silent(tmp_path):
    before, after = tmp_path / "before", tmp_path / "after"
    _put(before, "trade.json", '{"selected":"000660","rank":1}')
    _put(after, "trade.json", '{"selected":"041190","rank":1}')
    _put(before, "old.md", "old")
    _put(after, "new.md", "new")
    result = compare_snapshots(before, after)
    assert result["difference_count"] == 3
    assert {x["kind"] for x in result["differences"]} == {
        "CONTENT_OR_SEMANTIC_DRIFT", "ADDED", "MISSING"
    }
    assert all("selected" not in json.dumps(x) for x in result["differences"])


def test_empty_roots_no_false_pass(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    with pytest.raises(ValueError, match="No JSON/JSONL/Markdown"):
        compare_snapshots(a, b)


def test_output_inside_frozen_root_rejected(tmp_path):
    _put(tmp_path / "a", "report.md", "A")
    _put(tmp_path / "b", "report.md", "B")
    with pytest.raises(ValueError, match="OUTSIDE"):
        compare_snapshots(tmp_path / "a", tmp_path / "b", out=tmp_path / "a" / "evidence.json")


def test_same_root_and_missing_llm_capture_refused(tmp_path):
    _put(tmp_path / "a", "report.md", "A")
    _put(tmp_path / "b", "report.md", "A")
    with pytest.raises(ValueError, match="distinct"):
        compare_snapshots(tmp_path / "a", tmp_path / "a")
    with pytest.raises(ValueError, match="BOTH frozen roots"):
        compare_snapshots(tmp_path / "a", tmp_path / "b", llm_relative_path="prompt.json")


def test_secret_bodies_never_recorded_and_failed_cli_returns_one(tmp_path, monkeypatch):
    _put(tmp_path / "a", "report.md", "PRIVATE SECRET REPORT")
    _put(tmp_path / "b", "report.md", "CHANGED SECRET REPORT")
    args = ["p152_snapshot_parity", "--before", str(tmp_path / "a"), "--after", str(tmp_path / "b"),
            "--out", str(tmp_path / "out.json")]
    monkeypatch.setattr("sys.argv", args)
    assert main() == 1
    report = (tmp_path / "out.json").read_text(encoding="utf-8")
    assert "PRIVATE SECRET" not in report and "CHANGED SECRET" not in report


def test_symlinks_refused(tmp_path):
    _put(tmp_path / "a", "report.md", "A")
    _put(tmp_path / "b", "report.md", "A")
    link = tmp_path / "a" / "alias.md"
    try:
        link.symlink_to(tmp_path / "a" / "report.md")
    except (OSError, NotImplementedError):
        pytest.skip("symlink privilege unavailable on test platform")
    with pytest.raises(ValueError, match="Symlink forbidden"):
        compare_snapshots(tmp_path / "a", tmp_path / "b")


def test_bad_sha_and_file_cap_fail_closed(tmp_path):
    _put(tmp_path / "a", "report.md", "A")
    _put(tmp_path / "b", "report.md", "A")
    with pytest.raises(ValueError, match="before_sha"):
        compare_snapshots(tmp_path / "a", tmp_path / "b", before_sha="not-a-sha")
    with pytest.raises(ValueError, match="cap=1"):
        _put(tmp_path / "a", "extra.json", "{}")
        compare_snapshots(tmp_path / "a", tmp_path / "b", max_files=1)
