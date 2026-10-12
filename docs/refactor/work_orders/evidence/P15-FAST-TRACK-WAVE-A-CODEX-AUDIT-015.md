# Wave A — Codex independent audit result (recorded)

**Provenance:** result supplied by the user (Codex independent audit); not rerun by Claude in this record. Raw logs are not in Git.

- **VERDICT:** PASS_WITH_FINDINGS (GPT conditionally accepted the first-pass structural decomposition).
- **BASE** `fb8de628eb56b0941007e90ad2e98b4f684983ba` -> **HEAD** `318015a02b8378b0dbf7b0b24ec18c2786688d18`.
- Independent focused selection: **1,455 PASS / 1 policy FAIL**; A2 dedicated gate: **706 PASS**; production-write audit: **0**.
- The single failure was the R2-era scope guard `test_changes_remain_reporting_only_with_no_trading_authority_files`, which rejected the legitimate `apps/operator_ui/` change. Fixed in the Phase 1 closeout commit by pinning the historical guard to the Wave A end SHA (`318015a0`) with an explicit allowed set (`libs/reporting/`, `tests/`, `docs/`, `scripts/refactor/`, `apps/operator_ui/`) and unchanged always-forbidden set (`apps/api/`, `graphs/`, `conftest.py`, execution/broker/supervisor/executor/runtime/ai/core prefixes).
- The stale R3-era CURRENT.md checks and every ZIP packaging/upload step in `.github/workflows/p152-r2c-residual-regression.yml` were replaced/removed (Fast Track active-contract guard, JUnit + JSON inventory kept).

## Still OPEN / BLOCKED (not FINAL)
Actual frozen report Markdown/JSON/JSONL and LLM prompt/retry/timeout/call-count parity **BLOCKED / NOT RUN**; `controlled_mock_lanes` test write isolation **OPEN**; full native pytest **NOT RUN**. Wave A status: **FIRST_PASS_WITH_DEBT** — not FINAL_ACCEPTED.

## Phase 1 closeout verification (Claude, isolated clone)
- `tests/test_p152_facade_abi_and_authority_boundary.py` 4 passed (stage-pinned scope guard; 436 ABI and signature checks unchanged).
- `scripts/refactor/p152_integration_acceptance.py` inventory is pinned to the same Wave A end ref (`INVENTORY_END_REF`) with `apps/operator_ui/` added to its source scope; `tests/test_p152_integration_acceptance_inventory.py` 3 passed. (It had failed once HEAD contained the Wave A commit, a second R2-era stage guard of the same kind.)
- Focused Reporting + Operator UI selection (71 files): 2,372 passed / 1 skipped / 3 failed before the inventory fix; the 3 failures were: the known baseline API failure `test_api_routes_are_get_only`, the inventory scope guard (fixed above) and `tests/test_closeout_memory_bounds.py::test_daily_summary_payload_identical_with_streamed_and_materialised_rows`, which **passes in isolation (57 passed)** and passed in the earlier consolidated run — a load-dependent flake, recorded as OPEN/unreproduced, not attributed to Wave A. Production-write banner 0.
- GitHub Actions status: not observable from the isolated clone; verify on the pushed SHA (see CURRENT).

