# P15 TREE MIGRATION V2-053

Scanner context/scoring 입력 모듈 5개(feature_coverage, sentiment_inputs, scoring_inputs, macro_focus, macro_chart_fit)를 `libs/agents/scanner/context/`로 byte-identical 이동, 기존 경로는 module-identity shim. BASE 트리에서 생성한 136개 frozen case 정확 재현, T4-A Scanner frozen 계약 통과. V1 Gap Matrix P2 문구 정정. Evidence: `docs/refactor/evidence/P15-TREE-MIGRATION-V2-053-CLAUDE.md`.
