"""RF-031 libs/reporting/trade_report_runtime_generation: planning branches not reached by existing tests.

Covers the "forced regeneration on noisy artifact", "pending, no report",
"reuse existing report" and "deterministic only" modes of
``plan_live_trade_report_generation`` plus the small helpers (measured: lines
26-27, 139, 226, 238-276 uncovered before). tmp_path files only; no LLM.
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json

import pytest

from libs.reporting import trade_report_runtime_generation as gen


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _paths(tmp_path, write=True):
    j, m = tmp_path / "trade_report.json", tmp_path / "trade_report.md"
    if write:
        j.write_text("{}", encoding="utf-8")
        m.write_text("md", encoding="utf-8")
    return j, m


def _plan(tmp_path, **kw):
    j, m = _paths(tmp_path, kw.pop("files", True))
    args = dict(should_attempt_generation=True, report_requested=True, diagnostics={"report_status": "pending"},
                deterministic_report={"det": 1}, existing_trade_report_artifact=None, existing_ai_trade_report_llm_artifact=None,
                ai_trade_report_generation_state=None, ai_trade_report_fingerprint="fp1", trade_report_json_path=j,
                trade_report_md_path=m, configured_report_model="cfg/model", existing_report_noisy=False)
    args.update(kw)
    return gen.plan_live_trade_report_generation(**args)


def test_helpers_read_json_and_sanitize(tmp_path):
    p = tmp_path / "x.json"
    _eq(gen._read_json(p), {})
    p.write_text("{bad", encoding="utf-8")
    _eq(gen._read_json(p), {})
    p.write_text("[1]", encoding="utf-8")
    _eq(gen._read_json(p), {})
    p.write_text('{"a": 1}', encoding="utf-8")
    _eq(gen._read_json(p), {"a": 1})
    _eq(gen._sanitize_generation_error(None), "")
    _eq(gen._sanitize_generation_error("a\nb\r\nc"), "a b  c")
    _eq(gen._sanitize_generation_error("x" * 300), "x" * 257 + "...")
    _eq(gen.report_generation_state_path({"reports_dir": tmp_path}), tmp_path / "report_generation_state.json")
    if len(gen._utc_now_iso()) < 20 or "+00:00" not in gen._utc_now_iso():
        raise AssertionError("utc iso timestamp expected")


def test_load_and_write_state_defaults_and_roundtrip(tmp_path):
    p = tmp_path / "s.json"
    empty = {"schema_version": "report_generation_state.v1", "components": {}}
    _eq(gen.load_report_generation_state(p), empty)          # missing file -> default shell, never {}
    p.write_text("{bad", encoding="utf-8")
    _eq(gen.load_report_generation_state(p), empty)          # corrupt -> default shell
    p.write_text(json.dumps({"fingerprint": "f"}), encoding="utf-8")
    s = gen.load_report_generation_state(p)
    _eq((s["fingerprint"], s["schema_version"], s["components"]), ("f", "report_generation_state.v1", {}))
    p.write_text(json.dumps({"schema_version": "custom", "components": {"a": 1}}), encoding="utf-8")
    _eq(gen.load_report_generation_state(p), {"schema_version": "custom", "components": {"a": 1}})
    out = tmp_path / "sub" / "w.json"
    gen.write_report_generation_state(out, {"k": "한글"})
    _eq(json.loads(out.read_text(encoding="utf-8")), {"k": "한글"})


def test_first_generation_attempt_is_generate_ai(tmp_path):
    out = _plan(tmp_path, files=False)
    _eq((out["mode"], out["diagnostics"]["generation_attempted"], out["log_events"]), ("generate_ai", True, []))
    _eq(out["trade_report"], {"det": 1})
    _eq(out["ai_trade_report_llm_artifact"], {})


def test_matching_fingerprint_with_success_reuses_artifact_and_logs(tmp_path):
    out = _plan(tmp_path, existing_trade_report_artifact={"generation": {"status": "ok", "model": "used/model"}, "extra": 2},
                existing_ai_trade_report_llm_artifact={"llm_status": "ok", "k": 1}, ai_trade_report_generation_state={"fingerprint": "fp1"})
    d = out["diagnostics"]
    _eq((out["mode"], d["generation_attempted"], d["ai_trade_report_status"], d["llm_model_used"], d["report_generation_reason"]),
        ("reuse_existing_success", False, "ok", "used/model", "fingerprint_match_existing_success"))
    _eq(out["trade_report"]["det"], 1)
    _eq(out["trade_report"]["extra"], 2)   # existing artifact overlays the deterministic report
    _eq(out["log_events"][0]["event"], "report_generation_skipped_fingerprint_match")
    _eq(out["ai_trade_report_llm_artifact"], {"llm_status": "ok", "k": 1})


@pytest.mark.parametrize("override,why", [
    (dict(ai_trade_report_generation_state={"fingerprint": "OTHER"}), "fingerprint differs"),
    (dict(existing_ai_trade_report_llm_artifact={"llm_status": "error"}), "status not ok/salvaged/partial"),
    (dict(existing_trade_report_artifact=None), "no existing artifact object"),
])
def test_reuse_requires_every_condition(tmp_path, override, why):
    base = dict(existing_trade_report_artifact={"generation": {"status": "ok"}},
                existing_ai_trade_report_llm_artifact={"llm_status": "ok"}, ai_trade_report_generation_state={"fingerprint": "fp1"})
    base.update(override)
    out = _plan(tmp_path, **base)
    _eq((why, out["mode"]), (why, "generate_ai"))


def test_missing_artifact_files_block_reuse_and_noisy_existing_forces_regeneration(tmp_path):
    common = dict(existing_trade_report_artifact={"generation": {"status": "ok"}},
                  existing_ai_trade_report_llm_artifact={"llm_status": "ok"}, ai_trade_report_generation_state={"fingerprint": "fp1"})
    _eq(_plan(tmp_path, files=False, **common)["mode"], "generate_ai")
    noisy = _plan(tmp_path, existing_report_noisy=True, **common)
    _eq(noisy["mode"], "generate_ai")
    _eq([e["event"] for e in noisy["log_events"]], ["report_generation_forced_regen_noisy_existing_report"])
    _eq(noisy["log_events"][0]["reason"], "existing_report_contains_text_corruption_markers")
    # noisy with a NON-matching fingerprint regenerates without the forced-regen log
    quiet = _plan(tmp_path, existing_report_noisy=True, **{**common, "ai_trade_report_generation_state": {"fingerprint": "x"}})
    _eq((quiet["mode"], quiet["log_events"]), ("generate_ai", []))


def test_pending_without_generation_attempt_clears_report(tmp_path):
    out = _plan(tmp_path, should_attempt_generation=False, diagnostics={"report_status": " Pending ", "report_reason_human": "wait", "report_output_available": True,
                                                                            "report_artifact_available": True})
    d = out["diagnostics"]
    _eq((out["mode"], out["trade_report"]), ("pending_no_report", {}))
    _eq((d["generation_attempted"], d["report_output_available"], d["report_artifact_available"], d["report_generation_reason"]), (False, False, False, "wait"))
    _eq(len(d["generation_ts"]) > 10, True)


def test_not_attempted_and_not_pending_reuses_existing_report_or_falls_back(tmp_path):
    existing = {"ai_trade_report_status": "ok", "marker": 1}
    requested = _plan(tmp_path, should_attempt_generation=False, diagnostics={"report_status": "skipped"}, existing_trade_report_artifact=existing)
    d = requested["diagnostics"]
    _eq((requested["mode"], d["report_status"], d["report_reason_code"], d["ai_trade_report_status"], d["report_reason_human"]),
        ("reuse_existing_report", "available", "", "ok", "Existing trade report artifact was reused."))
    _eq((requested["trade_report"]["det"], requested["trade_report"]["marker"]), (1, 1))   # requested -> merged over deterministic
    not_requested = _plan(tmp_path, should_attempt_generation=False, report_requested=False, diagnostics={"report_status": "skipped"}, existing_trade_report_artifact=existing)
    _eq(not_requested["trade_report"], existing)   # not requested -> existing object kept as is
    _eq(not_requested["diagnostics"]["report_reason_human"], "Existing trade report artifact was preserved because AI generation was not requested.")
    _eq(not_requested["diagnostics"]["report_generation_reason"], not_requested["diagnostics"]["report_reason_human"])
    gen_status = _plan(tmp_path, should_attempt_generation=False, diagnostics={"report_status": "skipped"},
                       existing_trade_report_artifact={"generation": {"ai_trade_report_status": "partial"}})
    _eq(gen_status["diagnostics"]["ai_trade_report_status"], "partial")
    from_llm = _plan(tmp_path, should_attempt_generation=False, diagnostics={"report_status": "skipped"}, existing_trade_report_artifact={"m": 1},
                     existing_ai_trade_report_llm_artifact={"status": "salvaged"})
    _eq(from_llm["diagnostics"]["ai_trade_report_status"], "salvaged")
    nothing = _plan(tmp_path, should_attempt_generation=False, diagnostics={"report_status": "skipped"}, existing_trade_report_artifact={"m": 1})
    _eq(nothing["diagnostics"]["ai_trade_report_status"], "skipped")
    noisy = _plan(tmp_path, should_attempt_generation=False, diagnostics={"report_status": "skipped"}, existing_trade_report_artifact=existing, existing_report_noisy=True)
    _eq(noisy["mode"], "deterministic_only")   # a noisy existing report is never reused


def test_deterministic_only_fallback_when_nothing_else_applies(tmp_path):
    out = _plan(tmp_path, should_attempt_generation=False, diagnostics={"report_status": "skipped"})
    d = out["diagnostics"]
    _eq((out["mode"], d["report_status"], d["report_reason_code"], d["report_reason_human"]),
        ("deterministic_only", "available", "deterministic_only", "Deterministic report was generated without AI expansion."))
    _eq((d["next_expected_step"], d["report_generation_reason"]), ("Review deterministic report sections and evidence linkage.", d["report_reason_human"]))
    _eq(out["trade_report"], {"det": 1})
    # inputs are not mutated
    diag = {"report_status": "skipped"}
    _plan(tmp_path, should_attempt_generation=False, diagnostics=diag)
    _eq(diag, {"report_status": "skipped"})
