# P1.5 검증된 A/B 변경 선별 통합

- **상태:** `STAGE_ADMISSION_PENDING` — 실제 구성 통합 SHA/CI 미확인
- **담당:** 지팀장 GPT (수용/선별 통합/CI 최종 책임)
- **연관:** [PR #31 (초안)](https://github.com/hbombheart1230-dotcom/agentra/pull/31), [한글 CURRENT](../../../work_orders/CURRENT.md), [기존 P1.5 마스터 계획](../../../p1_5_p1_6_master_plan.md)
- **현재 확인 기준점(이력, 매 작업 직전 재조회):** integration 문서 기준 SHA `1ce79193`; A `a21401db`; B `a3d60e37`; draft stage `8b98fe74`. 이것은 미래 고정 SHA 승인값이 아니다.
- **원칙:** PR31 문서 T00–T09를 신규 작업으로 활성화하지 않는다. PR31/개발 브랜치를 통째로 병합하지 않는다. 공통 계약·안전·역사적 핀/CI 오라클 완화 금지.

## 지팀장 수행/완료 확인
- [ ] 실제 A/B/stage/integration HEAD 및 각 커밋별 허용 소유 경로 재검증
- [ ] A/B 후속 소스·테스트·검토 stdout/exit/판정 및 PEER_DEFERRED 구분
- [ ] 이미 수용된 변경만 정확한 파일 단위로 선별, 기존 전역 실행 계약/동결 증거 보존
- [ ] 양쪽 UI 패치노트 JSON/MD의 고유 항목 보존·카운트 정합성 확인
- [ ] 새로운 **실제 integration SHA** 대상으로 기존 normal/`python -O`·필수 회귀/CI PASS
- [ ] PR31 stage에 남은 고유 변경을 보존·검증한 후, 별도 승인된 안전한 PR·브랜치 정리로 총 4개 목표
- [ ] 통합/CI 증명과 실패·제외 사유 기록; 충족 시 GPT가 `closed/`로 이동하고 CURRENT 상태 갱신

**금지:** CI 미검증을 INTEGRATED 표시, 미검토 SOURCE 승인, `main` 병합, 실거래 활성화, Executor/Supervisor/Step5C 수정.
