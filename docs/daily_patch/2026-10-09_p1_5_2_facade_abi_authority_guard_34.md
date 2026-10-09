# P1.5.2 — Facade ABI & No Trading Authority Diff Guard 34 (2026-10-09)

- Source `9cd15b474f398fcb80cb5f6c1d37b8274c4b0c39`; new test `tests/test_p152_facade_abi_and_authority_boundary.py`.
- Pin all 436 top-level callable/function declarations across three public Reporting facades against Owner31 remote code SHA `52508ade9d0d246fa4e848525fe62f2fe067acb7`: ordered? name-set, declaration kind, arguments/defaults/annotations/returns, decorator structures, and importable callable presence.
- Git diff from initial R2/P1.5.2 code baseline `2fb4b8fcbaa68c34e80fbdbeb8e009c66d0cbc7c` may change only `libs/reporting/`, `tests/`, `docs/`, `scripts/refactor/` and the single P1.5.2 CI workflow. Reject Broker/Executor/Supervisor/trading/Docker/UEF changes by path.
- CI executes read-only static and public import tests; cannot certify internal report byte equality or actual Windows runtime/LLM behavior. Local independent Claude/Codex full acceptance remains NOT RUN, P1.5.2 OPEN, P1.5.3 not started.
