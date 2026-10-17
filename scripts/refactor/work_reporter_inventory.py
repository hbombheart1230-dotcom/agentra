"""R8 C3/C4: file-level Reporter responsibility inventory of libs/reporting (read-only, rule-based, evidence fields kept).

Categories: REPORTER_CANONICAL (implementation already under libs/agents/reporter, legacy path is shim/facade),
REPORTER_FACADE (legacy module that delegates moved bodies or re-exports), SHARED_CONTRACT, RESEARCH_EVALUATION,
OPS_SCHEDULER, EXTERNAL_AUTHORITY, BLOCKED_WITH_PROOF, REPORTER_RETAINED (Reporter code kept in place, reason recorded)."""
import ast
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVD = ROOT / "docs/refactor/work_projects/evidence/reporter"
RESEARCH = re.compile(r"(evaluation/|baseline_|short_alpha|alpha_research|opening_rank1|q8_|q1[0-2]|uef|quant_|strategist_llm_eval|scheduled_intelligence)")
OPS = re.compile(r"(daily_report|metrics_report|operator_|phase_runtime_health|report_source_helpers|alert_notifier|report_maintenance|closeout)")
AUTH = re.compile(r"(truth|broker|kiwoom|reconcil|carryover|execution_snapshot|live_execution|llm_artifacts|reporter_feedback|reporter_bundle_runtime)")


def main():
    led = json.loads((EVD / "r4_facade_ledger.json").read_text(encoding="utf-8"))
    facades = {m["path"] for m in led["moves"]}
    rows = []
    for p in sorted((ROOT / "libs/reporting").rglob("*.py")):
        rel = p.relative_to(ROOT).as_posix()
        text = p.read_text(encoding="utf-8-sig", errors="replace")
        loc = len(text.splitlines())
        consumers = subprocess.run(["git", "grep", "-l", rel[:-3].replace("/", "."), "--", "*.py"], cwd=ROOT, capture_output=True,
                                   text=True).stdout.split()
        consumers = [c for c in consumers if c != rel]
        if loc < 20 and ("_sys.modules[__name__] =" in text or "_canonical" in text):
            cat, why = "REPORTER_CANONICAL", "identity shim / alias to canonical owner"
        elif rel in facades:
            cat, why = "REPORTER_FACADE", "facade wrappers delegating R4..R8 moved bodies; remaining bodies in r8_function_triage.json"
        elif rel.endswith("controlled_mock_lane_report.py"):
            cat, why = "BLOCKED_WITH_PROOF", "reads controlled_mock_lanes ledger + Q10/Q12 lane labels; ownership decision for Work"
        elif RESEARCH.search(rel):
            cat, why = "RESEARCH_EVALUATION", "Research/evaluation/UEF/Q-series family (out of role)"
        elif AUTH.search(rel):
            cat, why = "EXTERNAL_AUTHORITY", "truth precedence / broker / LLM artifact / feedback / bundle runtime (protected)"
        elif "re-export" in text[:400] or "Compatibility facade" in text[:400]:
            cat, why = "REPORTER_FACADE", "import-only compatibility facade (R-2/R-3 decomposition)"
        elif OPS.search(rel):
            cat, why = "OPS_SCHEDULER", "operator/daily/metrics/maintenance reporting infrastructure (shared)"
        elif "/trade_report/" in rel or rel.split("/")[-2].endswith("_parts"):
            cat, why = "SHARED_CONTRACT", "earlier-pass owner parts pinned by R3/T1/T2 ledgers (path is part of historical contracts)"
        else:
            cat, why = "REPORTER_RETAINED", "Reporter module not moved in this pass (no proven move batch); see triage/function blockers"
        rows.append({"path": rel, "loc": loc, "category": cat, "reason": why, "consumers": len(consumers), "sample_consumers": consumers[:4]})
    (EVD / "r8_file_inventory.json").write_text(json.dumps({"schema": "agentra.work.reporter.r8_inventory.v1", "rows": rows},
                                                         ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    import collections
    c = collections.Counter(r["category"] for r in rows)
    print(c, len(rows))
    print([ (r["path"], r["loc"]) for r in rows if r["category"] == "REPORTER_RETAINED" and r["loc"] > 150][:40])


if __name__ == "__main__":
    main()
