# P15 TREE MIGRATION V3-055

Scanner projection 모듈 5개(candidate_context_projection, control_eligibility, output_payloads, output_snapshots, selection_evidence_projection)를 `libs/agents/scanner/projections/`로 byte-identical 이동, 기존 경로는 module-identity shim. BASE 트리에서 기록한 218개 케이스 정확 재현, T4-A Scanner 계약·Wave B 768/768 통과. Evidence: `docs/refactor/evidence/P15-TREE-MIGRATION-V3-055-CLAUDE.md`.
