# P1.5.2 — Façade Static Consumer Evidence 26 (2026-10-09)

- Source baseline `3a3ca3097b267b8cd22edeb0e45ef87690cfe466` on `refactor/p1.5`.
- Added read-only AST source-index runner `scripts/refactor/p152_facade_consumer_scan.py` and focused tests `tests/test_p152_facade_consumer_static_index.py` to inspect the full checked-out Python repository for three public Reporting façades.
- Index classifies direct symbol imports, alias/module attribute usage, literal `getattr`/`setattr`, `unittest.mock.patch` string targets, `patch.object`, monkeypatch, wildcard, dynamic and parse uncertainty. Results uploaded by CI as separate JSON artifact, not production output.
- **Static absence is UNKNOWN, not DEAD**; none of the 436 façade symbols may be deleted from this evidence alone. The frozen ledger and all public Reporter/Story implementations are untouched.
- Local `C:\\Agentra` actual runtime consumers, plugin entrypoints and independently observed patch semantics NOT RUN. No UEF/R6.2/Step5C/D, Broker, Executor, Docker, or trading authority edits.
- CI tests and evidence artifact publication must pass before declaring this checkpoint accepted; P1.5.2 OPEN.
