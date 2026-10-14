# T4-A.1 independent Codex corrective audit — user-delivered result, 2026-10-15

**FINAL T4-A: ACCEPT. P1 variant omission: CLOSED. T4-B: CI-GATED.**

- 73 records and 1,575 variants inventory match; expected sample_mod=4 IDs 396; sample_mod=1 IDs 1,575.
- NATIVE_ORACLE PASS: missing/extra/malformed/digest mismatch/record set failure all rejected.
- PORTABLE_ORACLE PASS: expected sample IDs == pinned BASE IDs == FEATURE IDs; previous shared omission false negative rejected.
- FULL_CORPUS PASS **only for inventory and comparator accounting**. The Codex audit did not collect new actual full Scanner replay results. Claude's prior report separately claimed full replay with 0 mismatches.
- No new P0/P1. New P2: invoking freeze_tool.py verify directly may raise ModuleNotFoundError: graphs without PYTHONPATH repo root; CI pytest route unaffected.
- Existing cross-seed telemetry P2 (not rank-1 change), NTFS mtime P2, REAL_REPORT_PARITY_BLOCKED retained.
- CODE f6a52ea CI 38648709904 SUCCESS. FINAL a55045a CI 38650256009 still IN_PROGRESS at report/lookup. GPT later added the post-T4 architecture gate in 4c49d6f; its patch_notes.json status planned breached required current|historical test and caused latest regression FAIL. This commit fixes status without changing acceptance semantics.
- Do not start T4-B until **current HEAD** required Linux and Windows CI both SUCCESS. T5, Wave D, main merge and production deployment are not authorized.

Only user-delivered audit conclusion is recorded here; no new Codex execution is claimed. Trading/Broker/LLM/Step5C/fixture files unchanged. Post-T4 visual architecture gate remains mandatory.
