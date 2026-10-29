"""RF-066 C1/C2: deprecated brief-LLM CLI is temp-root inspection only."""

from __future__ import annotations

import json

from scripts.maintenance import sync_legacy_brief_llm


def test_rf066_sync_legacy_brief_llm_cli_reads_explicit_temp_root_without_cwd_effects(monkeypatch, tmp_path, capsys):
    reports_root = tmp_path / "reports"
    primary = reports_root / "trades" / "20261029" / "TRD_1" / "reports" / "brief_llm_response.json"
    primary.parent.mkdir(parents=True)
    primary.write_text('{"summary":"canonical"}\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    exit_code = sync_legacy_brief_llm.main(
        ["--day", "20261029", "--reports-root", str(reports_root), "--dry-run", "--json"]
    )

    output = json.loads(capsys.readouterr().out)
    if exit_code != 0:
        raise AssertionError(exit_code)
    if output["trade_count"] != 1 or output["rows"][0]["status"] != "canonical_present":
        raise AssertionError(output)
    if output["rows"][0]["canonical_path"] != str(primary):
        raise AssertionError(output)
    if list(tmp_path.glob("**/brief_llm_response.json")) != [primary]:
        raise AssertionError("CLI created or rewrote a legacy brief artifact")
    if (tmp_path / "reports").resolve() != reports_root.resolve():
        raise AssertionError("relative default reports root was used despite explicit temporary root")
