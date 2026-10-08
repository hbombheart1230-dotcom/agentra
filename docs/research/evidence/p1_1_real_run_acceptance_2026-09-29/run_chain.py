"""P1.1 real-run acceptance driver.

Loads the immutable REAL_RUN_CAPTURE_A.json (already captured, never
rebuilt here) and runs the frozen UEF-7 -> UEF-8 -> UEF-9 chain against it,
using the actual frozen library APIs (the same functions the CLIs call),
writing outputs to the approved canonical report paths only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from libs.reporting.evaluation.uef7.alpha_board_normalization import normalize_alpha_board
from libs.reporting.evaluation.uef7.run_identity import normalizer_implementation_digest
from libs.reporting.evaluation.uef7.reporter import write_uef7_normalization_outputs
from libs.reporting.evaluation.uef8.fair_comparison import analyze_fair_comparisons
from libs.reporting.evaluation.uef8.run_identity import uef8_implementation_digest
from libs.reporting.evaluation.uef8.reporter import write_uef8_fair_comparison_outputs
from libs.reporting.evaluation.uef9.authority import verify_formal_evaluation_authority
from libs.reporting.evaluation.uef9.run_identity import uef9_implementation_digest
from libs.reporting.evaluation.uef9.reporter import write_formal_evaluation_authority

CAPTURE_DIR = Path(__file__).resolve().parent


def run(capture_path: Path, out_report: Path) -> dict:
    board = json.loads(capture_path.read_text(encoding="utf-8"))

    uef7 = normalize_alpha_board(board, normalizer_implementation_digest_value=normalizer_implementation_digest())
    uef7_dict = uef7.to_dict()
    uef7_out = write_uef7_normalization_outputs(uef7, repo_root=ROOT)

    uef8 = analyze_fair_comparisons(uef7_dict, uef8_implementation_digest_value=uef8_implementation_digest())
    uef8_dict = uef8.to_dict()
    uef8_out = write_uef8_fair_comparison_outputs(uef8, repo_root=ROOT)

    uef9 = verify_formal_evaluation_authority(uef7_dict, uef8=uef8_dict, uef9_implementation_digest_value=uef9_implementation_digest())
    uef9_out = write_formal_evaluation_authority(uef9, repo_root=ROOT)

    result = {
        "uef7_run_id": uef7.uef7_run_id,
        "uef7_candidate_count": uef7.candidate_row_count,
        "uef7_candidate_ids": list(uef7.candidate_ids),
        "uef7_shared_source_group_count": uef7.normalization_summary.shared_source_group_count,
        "uef7_unresolved_population_candidate_count": uef7.normalization_summary.unresolved_population_candidate_count,
        "uef7_out_dir": str(uef7_out),
        "uef8_run_id": uef8.uef8_run_id,
        "uef8_candidate_count": uef8.candidate_count,
        "uef8_pair_count": uef8.summary.pair_count,
        "uef8_comparable": uef8.summary.comparable_count,
        "uef8_conditional": uef8.summary.conditional_count,
        "uef8_not_comparable": uef8.summary.not_comparable_count,
        "uef8_unique_pair_ids": len({p.comparison_pair_id for p in uef8.pairs}),
        "uef8_reason_counts": dict(uef8.summary.reason_counts),
        "uef8_out_dir": str(uef8_out),
        "uef9_run_id": uef9.uef9_run_id,
        "uef9_authority_status": uef9.authority_status,
        "uef9_candidate_count": uef9.candidate_count,
        "uef9_pair_count": uef9.pair_count,
        "uef9_comparison_status_counts": dict(uef9.comparison_status_counts),
        "uef9_candidate_ids_digest": uef9.candidate_ids_digest,
        "uef9_comparison_pair_ids_digest": uef9.comparison_pair_ids_digest,
        "uef9_source_uef7_run_id": uef9.source_uef7_run_id,
        "uef9_source_uef8_run_id": uef9.source_uef8_run_id,
        "uef9_out_dir": str(uef9_out),
    }
    out_report.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return result


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "run1"
    capture = Path(sys.argv[2]) if len(sys.argv) > 2 else CAPTURE_DIR / "REAL_RUN_CAPTURE_A.json"
    out = CAPTURE_DIR / f"chain_result_{label}.json"
    result = run(capture, out)
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
