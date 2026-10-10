# P1.5.2 Remote Eligible Linux Offline Sweep — Full Without Early Failure Abort

Date: 2026-10-10
Remote code SHA: `bf961767f7effa7a11a906f26bd454f5614778ac`
GitHub Actions: https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38036400641

## Verified outcomes
- P1.5.2 selected Reporting/Owner/ABI/UI + prelocal static keep/compatibility job: **SUCCESS**. Existing 709 selected tests plus 3 new consumer debt cases PASS.
- Separate eligible-Linux repository `python -m pytest -q tests -m "not heavy and not docker and not benchmark" --disable-warnings`: **4,919 passed; 41 failed; 2 setup errors; 25 skipped; 9 deselected; 1 warning**, in 161.47 seconds.
- API get-only standalone test also independently FAILED.
- Full failing pytest/JUnit artifact: https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38036400641/artifacts/11663423777.
- This is a **FAILED broad job, not a P1.5.2 PASS**. All observed failures retained; no tests excluded post hoc to improve the score.

## Main failure groups (41 FAILED + 2 ERROR)
- Windows-vs-Linux path/process semantics and unrelated FastAPI route assertion; Windows-specific tests include 3 closeout-lock, market receipts Windows path, Operator UI Windows path, Windows env path, two Windows subprocess tests; API route get-only isolated FAIL.
- Scanner canonical rank runner-up fixture assertion FAIL (source/test identical pre-P1.5.2).
- Step5B mutation recovery mock tests FAIL with ExecutionDisabledError because enabling real physical broker mutations in hosted CI was deliberately not allowed; do not enable EXECUTION_ENABLED globally as a test workaround.
- UEF2A/Q10/Q12 historical forward recipe tests and UEF5.2 historical recompute/UEF6C/UEF9 depend on actual local `reports/` and `data/` evidence missing from the clean Github checkout; no synthetic substitute can be declared equivalent.
- UEF5.1 clean evidence registry source audit FAIL on existing UEF6 validation import. Source and tests unchanged relative to pre-P1.5.2; whether there is an old contractual gap must be separately verified, not patched within Reporting R2.

## Baseline source identity, no authority mutation
- Checked SHA256/Git blob identities at original `2fb4b8fcbaa68c34e80fbdbeb8e009c66d0cbc7c` and current for API main/test, closeout lock/test, market receipts/test, operator UI data/test, strategist/test, Scanner node/rank test/opening probe, Step5B tests, UEF5 registry test and UEF6 validation replay. All compared file blobs identical.
- An identical source file is not evidence of unchanged cross-module behavior or test result. Do not classify scanner rank or UEF5 failures as harmless.
- The remote clean runner has no access to actual `C:\Agentra`, Kiwoom session, SQLite or Q12 dirty worktrees. **Local Windows/LLM/reports equivalence remains NOT RUN.**

## Policy / scope decision
- Further full Linux broad sweeps are available as manual `workflow_dispatch` CI diagnostic; not automatic blockers to the 709 selected Reporting checks on every docs-only commit. Do not mask failures or redefine 4919/41/2 as PASS.
- Dedicated clean Windows GitHub-hosted compatibility job will run on next push; it is not the user's PC and cannot prove production artifacts.
- P1.5.2 OPEN; P1.5.3 not authorized; no main merge, production orders or source changes to Scanner/UEF/Step5B/Docker/Executor.
