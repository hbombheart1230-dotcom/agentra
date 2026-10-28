"""RF-034 C3: alpha_research_board.write_alpha_research_board write-scope contract (tmp root).

Pins the exact output set: 10 files inside ``output_dir`` plus ``latest.json``/``latest.md`` written to ``output_dir.parent``
(outside the requested directory - current behavior that callers must account for), and that ``reports_root`` stays read-only.
"""
from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest

from libs.reporting.alpha_research_board import builder as b

IN_DIR = {
    "alpha_research_board.json", "alpha_research_board.md", "risk_high_30m_sensitivity.json", "risk_high_30m_sensitivity.md",
    "remaining_candidate_reviews.json", "remaining_candidate_reviews.md", "immediate_opening_runtime_validation.json",
    "immediate_opening_runtime_validation.md", "short_alpha_discriminator.json", "short_alpha_discriminator.md",
}


@pytest.fixture(autouse=True)
def _deny_network(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    monkeypatch.setattr(socket, "create_connection", _boom)


def _files(root: Path):
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def test_empty_sources_write_exact_file_set_and_latest_goes_to_parent(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    base = tmp_path / "board"
    out = base / "20260821"
    res = b.write_alpha_research_board(reports_root=reports, through_day="2026-08-21", output_dir=out)
    assert {p.name for p in out.iterdir()} == IN_DIR
    assert {p.name for p in base.iterdir() if p.is_file()} == {"latest.json", "latest.md"}   # parent of output_dir, not output_dir
    assert not (out / "latest.json").exists()
    assert list(reports.iterdir()) == []                                                      # reports_root untouched
    assert _files(tmp_path) == {f"board/20260821/{n}" for n in IN_DIR} | {"board/latest.json", "board/latest.md"}
    keys = {k for k in res if k.endswith("_path")}
    assert {Path(res[k]).name for k in keys} == IN_DIR | {"latest.json", "latest.md"}
    board = json.loads((out / "alpha_research_board.json").read_text(encoding="utf-8"))
    assert res["candidate_count"] == board["candidate_count"] == len(board["candidates"]) > 0
    assert res["integrity_status"] == board["integrity"]["status"] and board["through_day"] == "2026-08-21"


def test_latest_is_a_byte_copy_of_the_dated_board_and_is_overwritten_each_run(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    base = tmp_path / "board"
    b.write_alpha_research_board(reports_root=reports, through_day="2026-08-20", output_dir=base / "20260820")
    first = (base / "latest.json").read_text(encoding="utf-8")
    b.write_alpha_research_board(reports_root=reports, through_day="2026-08-21", output_dir=base / "20260821")
    dated = (base / "20260821" / "alpha_research_board.json").read_text(encoding="utf-8")
    latest = (base / "latest.json").read_text(encoding="utf-8")
    assert latest == dated
    assert json.loads(first)["through_day"] == "2026-08-20" and json.loads(latest)["through_day"] == "2026-08-21"
    assert (base / "latest.md").read_text(encoding="utf-8") == (base / "20260821" / "alpha_research_board.md").read_text(encoding="utf-8")
    assert (base / "20260820" / "alpha_research_board.json").exists()                          # older dated board is preserved


def test_output_dir_is_created_recursively_and_existing_outputs_overwritten(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    out = tmp_path / "a" / "b" / "c"
    out.mkdir(parents=True)
    (out / "alpha_research_board.json").write_text("OLD", encoding="utf-8")
    b.write_alpha_research_board(reports_root=reports, through_day="2026-08-21", output_dir=out)
    assert (out / "alpha_research_board.json").read_text(encoding="utf-8") != "OLD"
    assert json.loads((out / "alpha_research_board.json").read_text(encoding="utf-8"))


def test_output_dir_blocked_by_file_raises_without_partial_latest(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    with pytest.raises(OSError):
        b.write_alpha_research_board(reports_root=reports, through_day="2026-08-21", output_dir=blocker / "sub")
    assert blocker.read_text(encoding="utf-8") == "x" and _files(tmp_path) == {"blocker"}


def test_board_payload_is_deterministic_across_runs(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    for n in ("one", "two"):
        b.write_alpha_research_board(reports_root=reports, through_day="2026-08-21", output_dir=tmp_path / n / "d")
    a = json.loads((tmp_path / "one" / "d" / "alpha_research_board.json").read_text(encoding="utf-8"))
    c = json.loads((tmp_path / "two" / "d" / "alpha_research_board.json").read_text(encoding="utf-8"))
    assert a == c and "generated_at" not in a
