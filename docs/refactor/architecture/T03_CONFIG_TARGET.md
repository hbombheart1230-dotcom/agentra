# T03 — config/ 목표 설정·스킬 트리
> 담당 RF-090. 실제 파일 8개. **실거래 기본값, 암호/credential, broker capability를 변경하지 않는다.**

## 목표 폴더 및 정확한 파일
```text
config/
├── .env.example                      # example only, live secrets 금지
├── exam_strategy_baseline.yaml       # 구 기준 계약 KEEP
├── strategy_v1_exam_baseline.json    # versioned baseline KEEP
└── skills/
    ├── account.orders.yaml
    ├── market.minute_ohlcv.yaml
    ├── market.quote.yaml
    ├── order.place.yaml
    └── order.status.yaml
```

## 목표 개선 내용
| 현재 | 목표 | 판정 게이트 |
|---|---|---|
| `.env.example` | 실제 credential이 없는 명시적 example; 기존 변수·기본값 유지 | secret scan, runtime/default 읽기 동일 |
| `exam_strategy_baseline.yaml`, `strategy_v1_exam_baseline.json` | 각 버전·시험 lane의 명확한 단일 소유권; schema 중복 증명 전 KEEP | mock/optimized/replay parity |
| `skills/account.orders.yaml`, `skills/market.*.yaml` | 조회 skill 정의, read-only 계약 | 권한·파라미터·실패 경계 |
| `skills/order.place.yaml`, `skills/order.status.yaml` | 호출/조회 skill 스펙만 보존; 주문 승인을 우회하지 않음 | Executor/Approval/Step5C 경계 안전 검증 |

**결정:** 신규 config 하위 패키지 없음. 중복 설정이 검증될 경우 실제 소비자와 모드별 env precedence 입증 후 개별 RF 수정. 예제 env를 실거래 활성값으로 사용하거나 runtime profile을 바꾸는 작업은 범위 밖.

## 현행 파일명 전수 및 RF
- `config/.env.example` — RF-090
- `config/exam_strategy_baseline.yaml` — RF-090
- `config/skills/account.orders.yaml` — RF-090
- `config/skills/market.minute_ohlcv.yaml` — RF-090
- `config/skills/market.quote.yaml` — RF-090
- `config/skills/order.place.yaml` — RF-090
- `config/skills/order.status.yaml` — RF-090
- `config/strategy_v1_exam_baseline.json` — RF-090

## 공통 강제 게이트
- 본 T문서는 **목표 설계**다. 새 폴더를 만들거나 파일을 옮기는 자동 승인서가 아니다. 기존 소비자·동적 import·CLI·테스트·스케줄러·런타임 출력·인증·운영 경계의 parity 증명과 해당 RF 승인 후 실제 이동한다.
- D00/CURRENT 규칙, V3 SAFETY_LOCK, BASE/후보 SHA, 독립 read-only peer 검증, normal/`python -O`, 해당 통합 SHA CI를 유지한다. 과거 FAIL·SKIP은 PASS로 바꾸지 않는다.
- 각 RF 종료 증거: SOURCE_PATH → TARGET_PATH / 단일 Owner / KEEP·MOVE·COMPAT·SAFETY_HOLD·REMOVE_PROVEN / 소비자 / 독립 증거 / 통합 SHA. 없으면 RF DONE 불가.
- [T00 전체 목차](T00_TARGET_TREE.md) · [동결 V3](TREE_V3_FROZEN.md) · [RF 상태](../plan/STATUS.md) · [기준선 소유권 CSV](../plan/FILE_COVERAGE_63182ab2.csv).
