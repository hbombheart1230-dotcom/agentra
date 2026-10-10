# P1.5.2 Broad Repo Safe-CI Sweep — first attempted remote run

2026-10-10, tested remote SHA `b43ac8b8d3b259ea02478bca4fb49e0203f361d2` on Linux GitHub Actions:
https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38035524693

## PASS, but broad job FAIL
- Original selected regression job **SUCCESS**: 709 selected tests plus 3 prelocal static compatibility contract tests.
- Extra repo-wide non-heavy/non-Docker/non-benchmark suite: **2,114 PASS, 12 FAIL, 9 DESELECTED**, terminated at `--maxfail=12` after ~114 seconds. JUnit: https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38035524693/artifacts/11664211570
- 436-symbol static compatibility ledger emitted; 1,778 Python files scanned; 106 symbols with references, 330 without **NOT DEAD**; 8 dynamic hazards. No removal approved.

## Initial 12 failure inventory; no root cause claim without rerun
- 3: global `DRY_RUN=1` caused mocked LLM tests to return `dry_run` or skip attempts; remove unintended harness override.
- 3: `test_p152_ai_duration_language_owner` invoked git show on historic SHA `ef22bec`, unavailable in separate shallow checkout; fetch exact pinned revisions in sweep job.
- 5: Linux/Windows environment/path/lock identity behavior under test in `test_closeout_single_owner_guard` (3), `test_market_data_receipts` (1), `test_operator_ui` (1). Preserve test source; platform-specific expected vs actual requires independent historical/baseline comparison before classifying as existing bug.
- 1: `tests/apps/api/test_isolation.py::test_api_routes_are_get_only` found no routes of the imported APIRoute class. Could be import order/test pollution or true app issue; add isolated fresh-process check.
- Do not patch non-Reporting runtime or weakening tests to artificially greenlight P1.5.2.

## Remaining barriers
- Broad CI was not all-green; remote source compatibility is not live/regression equality.
- Real local data/LLM and full Windows repository pytest with Q12/production isolation, two independent auditors and operator size-debt acceptance NOT RUN.
- P1.5.2 OPEN, P1.5.3 not authorized; no trading order or Docker/scheduler modification.
