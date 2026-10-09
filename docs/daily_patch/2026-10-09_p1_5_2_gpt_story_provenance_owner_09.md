# 2026-10-09 — P1.5.2 GPT Story Provenance Owner 09

- Pinned base code SHA `a010f53d5e7bebe2b743ac16893bf47fa810e42d`.
- Both lifecycle v2 and direct v1 paths contained 67 AST-identical lines of reasoning-provenance derivation. Introduced ONE canonical `reasoning_provenance.py` Owner (85 LOC), used from both paths.
- Parent story assembly size after slice: 644 physical LOC (was 762). Strict new Owner cap <=350.
- Source-preference / canonical artifact references / reasoning flags and call-time dependency injection preserved.
- Isolated BEFORE vs candidate AST-invocation smoke: 2 fixture paths both output-equal; added deterministic focused owner tests to Reporting CI.
- Prior run 37879379703 failed only in static CURRENT.md work-order string guard. Work-order wording was restored by follow-up commit a010f53; that run was NOT reported as code-test PASS. The new commit must pass CI before this tranche is accepted.
- No production or broker, LLM, trading, UEF, Docker, Step5C/D or R6.2 writes.
- Remaining P1.5.2 size/real-data/independent gates explicitly OPEN.
