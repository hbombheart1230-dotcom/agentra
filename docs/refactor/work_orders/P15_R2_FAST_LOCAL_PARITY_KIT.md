# P1.5.2 Fast Local Parity Kit — GPT frozen-source handoff

Status: **TOOL IMPLEMENTED/TESTED IN REMOTE SYNTHETIC FIXTURES ONLY**; user-local data NOT RUN.
Current branch `refactor/p1.5`; Reporting source baseline frozen at Owner38 code SHA `80f56edfbbda8d336b09e7c5f0b18069d77785b9`; historical pre-P1.5.2 original code SHA `2fb4b8fcbaa68c34e80fbdbeb8e009c66d0cbc7c`.
Do not perform checkout/reset/clean of either local dirty Q12 worktree, touch live reports/data, run live LLM/order, or restart Docker/scheduler. Do not start P1.5.3.

## Purpose of script
`scripts/refactor/p152_snapshot_parity.py` reads two **existing independent immutable snapshot COPY directories**. Exact SHA256/bytes comparison for .json, .jsonl, .md; canonical JSON hash distinguishes formatting-only from semantic/content drift. Missing or added files fail. Optional `--llm-relative-path` validates pre-saved prompt/call trace presence in both, never calls LLM or prints prompt contents. Its evidence JSON contains paths + hashes only, no raw report body, no model response text. Failed bytes return exit code 1. Configuration invalid returns 2. Empty roots/identical directories/symlinks and evidence output inside either root are rejected.

**It does NOT create a before-version snapshot, extract secret historical data or certify input provenance.** Captures must already exist or be prepared by locally authorized safe methods. A synthetic PASS does NOT stand for production equivalence.

## Local example (ONLY after separate safety review)
```powershell
cd C:\Agentra
python -m scripts.refactor.p152_snapshot_parity --before C:\AgentraEvidence\p152_before_copy --after C:\AgentraEvidence\p152_after_copy --out C:\AgentraEvidence\p152_results\parity.json --before-sha 2fb4b8fcbaa68c34e80fbdbeb8e009c66d0cbc7c --after-sha 80f56edfbbda8d336b09e7c5f0b18069d77785b9
```
If captured LLM transcript exists **as the same JSON/JSONL relative path inside both snapshot trees**, add `--llm-relative-path reports/trades/sample/llm_trace.json`. Script checks equality but the independent verifier still must attest completeness (model/parameters/prompt/calls/retry/timeout and external call disabled) and SHA-authenticity of snapshots.

## Local Codex batch (implementation/test primary)
1. Inspect `git status --short`, branch/HEAD, `git worktree list` in `C:\Agentra`, preserve dirty Q12 worktrees. Check origin `refactor/p1.5` but do not silently pull/checkout; user-local root authoritative for reports and operational history.
2. Reuse real captured historical outputs and LLM traces when available; do not invent missing baseline. Run read-only script against two safe frozen copy folders outside repo. Run isolated safe pytest including Windows-native full suite **only after confirming zero production writes**; collect baseline discrepancies and FAIL/NOT RUN separately.
3. Inspect API GET-only and Scanner runner-up rank failures reproduced on Linux + GitHub Windows (report `docs/refactor/work_orders/evidence/P15-R2-GPT-PRELOCAL-004-WINDOWS-HOSTED.md`). **Separate concerns**: do not edit Scanner/UEF/Executor, or silently "fix" these just to satisfy P1.5.2.
4. Produce concise SHA-specific evidence with totals and failures, changed paths, actual snapshot hashes; never re-read the entire historical work-order backlog. New fixes only if authorized, small transaction, commit/test/patch notes.

## Local Claude (independent verifier AFTER Codex)
Verify actual frozen-input provenance, SHA parity, captured LLM semantics, public ABI 436, monkeypatch seams and import direction. Audit, do not repeat unrelated implementation. Mark PASS/PASS_WITH_FINDINGS/BLOCKED and return evidence to GPT/user.

## Remote findings retained as evidence, not passed
- Core selected Reporting: 709 targeted PASS + 3 consumer debt tests; 37 Owner modules remain bounded.
- Broad offline Linux: 4,919 PASS / 41 FAIL / 2 setup ERROR / 25 SKIP / 9 deselected (clean hosted env; local UEF artifacts absent).
- Windows GitHub-hosted: 123 path/lock tests PASS; API/Scanner group 11 PASS / 2 FAIL.
- Legacy facade LOC 2,761 / 2,658 / 636 **SIZE GOAL STILL OPEN**; static scan 106 of 436 externally referenced, 330 UNKNOWN (not DEAD); wrapper retirement prohibited without live/local consumer proof.

Gate: P1.5.2 remains OPEN and user has NOT approved size exceptions. P1.5.3 blocked.
