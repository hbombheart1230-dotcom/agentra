"""P1.1 item 12: fail-closed tamper tests against COPIES of the real run-1
UEF-7/UEF-8 authority objects. verify_formal_evaluation_authority() never
writes to disk itself, so these tests produce zero report artifacts --
nothing to clean up.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from libs.reporting.evaluation.uef9.authority import verify_formal_evaluation_authority
from libs.reporting.evaluation.uef9.model import UEF9AuthorityError
from libs.reporting.evaluation.uef9.run_identity import uef9_implementation_digest

CAPTURE_DIR = Path(__file__).resolve().parent

# Re-derive the exact uef7/uef8 dicts from the immutable capture (same
# path run_chain.py used) -- never load from a report file, so this is
# unambiguously the same input the real acceptance run verified.
from libs.reporting.evaluation.uef7.alpha_board_normalization import normalize_alpha_board
from libs.reporting.evaluation.uef7.run_identity import normalizer_implementation_digest
from libs.reporting.evaluation.uef8.fair_comparison import analyze_fair_comparisons
from libs.reporting.evaluation.uef8.run_identity import uef8_implementation_digest


def _base():
    board = json.loads((CAPTURE_DIR / "REAL_RUN_CAPTURE_A.json").read_text(encoding="utf-8"))
    uef7 = normalize_alpha_board(board, normalizer_implementation_digest_value=normalizer_implementation_digest()).to_dict()
    uef8 = analyze_fair_comparisons(uef7, uef8_implementation_digest_value=uef8_implementation_digest()).to_dict()
    return uef7, uef8


IMPL = uef9_implementation_digest()


def _expect_reject(label, uef7, uef8):
    try:
        verify_formal_evaluation_authority(uef7, uef8=uef8, uef9_implementation_digest_value=IMPL)
    except UEF9AuthorityError as exc:
        print(f"{label}: REJECTED ({exc})")
        return True
    print(f"{label}: ACCEPTED -- TAMPER TEST FAILED")
    return False


results = {}

# A. wrong UEF-7 run binding
uef7, uef8 = _base()
uef8 = copy.deepcopy(uef8)
uef8["source_uef7_run_id"] = "UEF7RUN_deadbeef00000000"
results["A_wrong_uef7_binding"] = _expect_reject("A_wrong_uef7_binding", uef7, uef8)

# B. pair count / pair id tamper
uef7, uef8 = _base()
uef8_count = copy.deepcopy(uef8)
uef8_count["pairs"] = uef8_count["pairs"][:-1]
results["B1_pair_count_tamper"] = _expect_reject("B1_pair_count_tamper", uef7, uef8_count)

uef8_id = copy.deepcopy(uef8)
uef8_id["pairs"][1]["comparison_pair_id"] = uef8_id["pairs"][0]["comparison_pair_id"]
results["B2_pair_id_collision_tamper"] = _expect_reject("B2_pair_id_collision_tamper", uef7, uef8_id)

# C. comparison status-count contradiction
uef7, uef8 = _base()
uef8_status = copy.deepcopy(uef8)
uef8_status["summary"]["conditional_count"] = 999
results["C_status_count_contradiction"] = _expect_reject("C_status_count_contradiction", uef7, uef8_status)

# D. current-schema injected COMPARABLE (self-consistent: pair status AND
# summary counts agree, isolating the capability-contradiction guard
# specifically, not the more general summary-mismatch guard)
uef7, uef8 = _base()
uef8_comparable = copy.deepcopy(uef8)
original_status = uef8_comparable["pairs"][0]["comparison_status"]
uef8_comparable["pairs"][0]["comparison_status"] = "COMPARABLE"
uef8_comparable["pairs"][0]["comparison_reasons"] = []
uef8_comparable["summary"]["comparable_count"] += 1
uef8_comparable["summary"][f"{original_status.lower()}_count"] -= 1
results["D_injected_comparable_capability_contradiction"] = _expect_reject(
    "D_injected_comparable_capability_contradiction", uef7, uef8_comparable
)

print()
print(json.dumps(results, indent=2))
all_rejected = all(results.values())
print("ALL_TAMPER_TESTS_REJECTED:", all_rejected)
