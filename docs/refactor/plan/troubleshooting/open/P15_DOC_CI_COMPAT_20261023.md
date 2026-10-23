# P1.5 문서 개편 CI 호환성 및 예약 검증 오류

- **상태:** `OPEN / BLOCKED` · 담당 GPT 지팀장 · 기준 `integration/p1.5@a3705871`
- **범위:** ROOT→LEAF RF-001~093 문서 개편 / D00-D02 / CURRENT / UI patchnotes; 소스 런타임은 이 건의 변경 대상이 아님.

## 원격 증거
- 2026-10-23 SHA `a3705871`: 필수 GitHub Actions **5개 중 success 1개, failure 4개**. `95d04a4`에도 동일한 1/4 실패가 있었으므로 이전 SHA만 보는 예약 보고는 잘못.
- PASS: [Integration Scripts Linux Windows Contract](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39882696557).
- FAIL: [Shared Candidate Required Contracts](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39882696617), [Integration T4 Regression](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39882696531), [Integration Reporting and Web Compatibility](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39882696646), [Reporting Regression + Design Guard](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39882696542).
- T4/Design Guard: 과거 고정 검증이 `Issues #16–#19 are CLOSED`, `DOC_FREEZE`, `P1.5.2 OPEN`/`DOC-A`, Issue #20 등의 현재 운영문서 내 리터럴 표현을 요구함. 새 CURRENT 운영방식과 역사 고정 문자열 계약 충돌. 테스트 우회/더미 PASS 금지.
- Shared candidate: `scripts/refactor/shared_strategist_contracts.py:94`가 오래된 정확한 B-stage composed 파일 목록만 허용하여 RF93 및 새 문서 경로를 unexpected inventory로 차단. 구 역사 SHA 검증과 현재 docs-only 변경 승인 경계를 분리 설계해야 하며 임의 allowlist 확장 금지.
- Reporting compatibility: `tests/test_patch_notes_sync.py:57`에서 신규 JSON 두 항목에 필수 `impact` 누락; 추가로 최근 문서 `sources`에 디렉터리 경로가 있어 file provenance 검증 위험.
- 원격 브랜치 목록은 5개; 옛 `work/p15-b-operator-live-overview-20261020` ref는 404, 보존 태그 `archive/p15-20261022/b-operator-historical`는 `70843da4...` 그대로. 예약 보고의 구 브랜치 미삭제 주장은 사실과 다름.

## 현재 조치 / 다음 게이트
- [x] UI JSON 기존 두 레코드 `impact` 및 최근 source file-path 스키마 정정, Markdown 동기 기록. 이 조치만으로 CI 전체 PASS 선언 불가.
- [ ] 기존 DOC_FREEZE/역사 SHA 가드가 보존되는 신규 CURRENT 유효성 검사를 어떻게 추가할지 기술 검토/독립 리뷰. 기존 CI 오라클 단순 완화·삭제 금지.
- [ ] 과거 S5 B-stage 정확한 파일 인벤토리와 후속 docs-only 변경을 서로 다른 증명 대상으로 나눌 허용된 경로 검토. 무단 임의 allowlist/테스트 우회 금지.
- [ ] 해당 수정 후보를 독립 CLI와 normal/`python -O`로 검토한 후 **수정된 정확한 통합 SHA**의 5개 CI 확인, 그 전까지 RF DONE/통합 PASS 불가.
- [ ] 예약 실행은 항상 원격 `integration/p1.5` HEAD와 최신 CI를 기준으로 하고, 브랜치 삭제/보존 태그는 API로 재확인. 쓰기 실패는 해당 시도만 BLOCKED 보고하며 오래된 SHA로 덮어쓰기 금지.

**제약:** `main`·실거래·안전 권한·CI 검증 오라클을 수정/약화하지 않음. 이미 공개된 RF 계약은 유지하고 정확한 해결에는 별도 검증 필요.

## 지팀장 CI 호환성 수리 후보 (2026-10-23)
- **확인된 마지막 녹색 기준:** `51bb7130b2ba627be50800fa89c6108dd1a5018c` (필수 CI 6/6 PASS). RF93 문서 스냅샷 `3fb24fe01761bd8f68587ee48fd0014e807d0d8a`와 분리.
- **기존 실패:** `3fb24fe0` 5개 워크플로 최종 1 PASS / 4 FAIL. Shared/Reporting은 과거 B-stage 정확한 29경로 검사가 후속 120건 문서 변경을 source inventory로 오인. T4/Design Guard는 DOC_FREEZE/역사 provenance 표현 삭제로 실패.
- **수리 범위:** B-stage 기존 29경로 인벤토리·실제 Owner 바이트/AST/ABI·부정 mutation 검증 유지. 녹색 고정 SHA의 역사적 인벤토리와 RF93 문서 스냅샷을 분리하여, 스냅샷 이후 정확히 명시한 CI 수리 파일 외 변경을 거부한다. 문서 provenance는 재활성 지시가 아닌 과거 기록으로 복원한다. UI patchnotes JSON/MD 동기화.
- **판정:** 수리 커밋은 hosted exact-SHA normal/optimized CI 및 별도 독립 CLI verdict 이전까지 `VERIFY_PENDING`. CI 실패가 남으면 수정 완료 선언 금지; 기존 오라클/실거래 경계 변경 금지.

- **후속 실패 세부:** 최초 수리 SHA `419128e0`의 T4/Design Guard는 문서 검사 32번째 assertion에서 `docs/refactor/README.md`의 역사적 `DOC_FREEZE` 표식 누락을 발견. 해당 README에 비활성 provenance를 복원했고 CI 수리 경계에 정확한 경로 한 개만 추가. 기존 오라클/워크플로 수정 없음.
