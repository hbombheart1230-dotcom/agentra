# T01 — .github/ 목표 폴더트리 및 CI 계약
> 담당 RF-092. **CI 통합 개수 이슈 종료:** 7→2 워크플로 재축소/재논쟁 금지. 운영·계약 검증은 계속 유지.

## 목표 폴더
```text
.github/
└── workflows/
    ├── p15-shared-candidate.yml                  # 운영·안전/normal/-O 오프라인 필수 검사
    └── p15-integration-crossbranch-compat.yml   # 웹 npm test/build 및 변경 범위 게이트
```
**현행 2개와 목표 2개가 일치.** 과거 7개 시절의 5개 workflow path는 새로 복원하거나 다시 제거할 대상이 아니다.

## 이미 확인된 증거 — 재감사 안건으로 되돌리지 말 것
- [Shared Offline Safety PASS — 1c4d191f SHA](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/40079749220) : Ubuntu Python 3.12, normal/-O matrix; mock, Broker credential blanks. 해당 소스 SHA에 한정.
- [Web Compatibility PASS — 1374d371 SHA](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/40073316192) : npm ci/test/build. 해당 웹 소스 SHA에 한정.
- 현행 workflow 파일과 트리 2개를 Git에서 확인. **축소 자체를 미검증 또는 RF-092의 반복 숙제로 재등록하지 않는다.** 위험·트리거·새 통합 SHA가 바뀌면 그 **변경분만** 검증한다.
- 과거 5개 제거 경로: `p15-integration-consumer-inventory.yml`, `p15-integration-scripts-contract.yml`, `p15-integration-t4-regression.yml`, `p152-r2c-residual-regression.yml`, `scripts-target-tree-contract.yml`. 이 이름들은 **역사적 추적용**이며 복원 계획이 아니다.
- 두 현재 workflow의 명령·트리거·매트릭스는 각 파일 내용이 정본. `p15-shared-candidate.yml`은 Python 경로에만 자동 트리거되며 문서 전용 변경에 무조건 실행되는 것은 아니다.

## 완료 판정
1. 실제 두 workflow 본문을 대상 SHA로 인용하여 책임·트리거·normal/-O, npm test/build를 기록한다.
2. CI 오라클·required checks·branch protection을 무승인 변경하지 않는다.
3. 두 성공 run은 **이미 수행된 축소 검증 근거로 재사용**한다. 최종 P1.5 Freeze는 새 exact SHA의 해당 필수 CI 상태를 별도로 확인한다(새 SHA CI NOT_RUN을 이전 PASS로 치환하지 않는다).
4. RF-092의 다른 책임(파일 소유권·CI 필요성 확인)은 DONE 조건으로 남지만, **5개가 사라졌다는 사실만으로 신규 Blocker 생성 금지.**

## 현행 파일명 전수
- `.github/workflows/p15-integration-crossbranch-compat.yml` — RF-092
- `.github/workflows/p15-shared-candidate.yml` — RF-092

## 공통 강제 게이트
- 본 T문서는 **목표 설계**다. 새 폴더를 만들거나 파일을 옮기는 자동 승인서가 아니다. 기존 소비자·동적 import·CLI·테스트·스케줄러·런타임 출력·인증·운영 경계의 parity 증명과 해당 RF 승인 후 실제 이동한다.
- D00/CURRENT 규칙, V3 SAFETY_LOCK, BASE/후보 SHA, 독립 read-only peer 검증, normal/`python -O`, 해당 통합 SHA CI를 유지한다. 과거 FAIL·SKIP은 PASS로 바꾸지 않는다.
- 각 RF 종료 증거: SOURCE_PATH → TARGET_PATH / 단일 Owner / KEEP·MOVE·COMPAT·SAFETY_HOLD·REMOVE_PROVEN / 소비자 / 독립 증거 / 통합 SHA. 없으면 RF DONE 불가.
- [T00 전체 목차](T00_TARGET_TREE.md) · [동결 V3](TREE_V3_FROZEN.md) · [RF 상태](../plan/STATUS.md) · [기준선 소유권 CSV](../plan/FILE_COVERAGE_63182ab2.csv).
