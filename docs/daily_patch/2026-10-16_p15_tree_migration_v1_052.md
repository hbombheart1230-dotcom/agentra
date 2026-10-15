# P15 TREE MIGRATION V1-052

Scanner `candidate_risk.py`를 `libs/agents/scanner/`로 byte-identical 이동하고 기존 경로는 module-object identity shim으로 유지(old/new import identity, 115 frozen 입력 동일 결과, monkeypatch 공유). 다른 Scanner 경로·rank 로직·Broker/LLM 변경 없음. Evidence: `docs/refactor/evidence/P15-TREE-MIGRATION-V1-052-CLAUDE.md`.
