# P15 TREE MIGRATION V4-056

Scanner 정책 helper 5개(symbol_prior, blocker_family_overlay, repeat_guard, guidance, compatibility)를 `libs/agents/scanner/policy/`로 byte-identical 이동, 기존 경로는 module-identity shim. 공개 wrapper로 BASE 트리에서 생성한 318개 케이스 정확 재현(시계/환경 고정), Wave B 허용목록은 정확한 V4 5쌍만 확장. Evidence: `docs/refactor/evidence/P15-TREE-MIGRATION-V4-056-CLAUDE.md`.
