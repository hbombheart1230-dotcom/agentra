# T04 — data/ 목표 정본 데이터·평가 fixture·개인자료 분리
> 담당 RF-091. 현재 추적 25파일. **데이터 공개/삭제 또는 운영 state 이동을 허용하는 문서가 아니다.**

## 목표 트리
```text
data/
├── specs/
│   ├── api_catalog.jsonl
│   ├── default_rules.json
│   ├── kiwoom_api_list_tagged.jsonl
│   └── kiwoom_apis.jsonl
├── eval/
│   └── m26_fixed_dataset_v1/
│       ├── manifest.json
│       ├── execution/{fills,intents,order_status}.jsonl
│       ├── features/scanner_monitor_features.jsonl
│       ├── market/{corporate_actions,ohlcv_1d,ohlcv_1m,ohlcv_5m}.csv
│       ├── microstructure/top_of_book.jsonl
│       └── news/{headlines,sentiment_by_symbol,sentiment_daily}.jsonl
├── originals/                  # RESTRICTED_REVIEW: historical originals only
├── m15_demo_events.jsonl       # compatibility fixture review
├── m15_demo_intents.jsonl      # compatibility fixture review
└── state*.json                 # HISTORICAL/RESTRICTED_REVIEW, NOT runtime authority
```

## 파일별 개선 목표
| 기존 파일·그룹 | 목표 처리 | 근거·검증 |
|---|---|---|
| `specs/api_catalog.jsonl`, `kiwoom_apis.jsonl`, `kiwoom_api_list_tagged.jsonl` | canonical spec vs derived catalog 1개 권위 확인, path는 KEEP 우선 | 생성 스크립트 소비자·구문·해시 parity |
| `specs/default_rules.json` | source-of-truth 규칙 보호 | 권한·전략 기본값·계약 불변 |
| `eval/m26_fixed_dataset_v1/manifest.json` 및 12개 하위 데이터 파일 | 버전 고정 deterministic fixture; 진단/운영 데이터 혼용 금지 | manifest/fixture hash, deterministic replay |
| `m15_demo_*.jsonl` | 역사적 demo fixture 분류 | 참조 테스트·CLI 확인 후 KEEP/ARCHIVE |
| `originals/키움 REST API 문서.xlsx` | 비실행 참조자료; 공개 여부 검토 | 라이선스·민감정보·링크 확인 |
| `originals/- 복사본.env` | **POTENTIAL_SECRET_REVIEW**: 내용 불러오거나 공개하지 않고 보안 담당 확인 필요 | 민감 파일은 경로만 기록, 사용자 승인 전 수정/삭제/이동 금지 |
| `state.json.bak_*`, `state.pre_*.json` | 운영 state authority가 아닌 과거 snapshot 후보; 무단 삭제 금지 | 실제 프로덕션 참조, 비밀·계좌자료, provenance·restore chain |

**예외:** 예전 파일을 정리한다는 명목으로 운영 상태·실계좌 데이터·지금까지의 감사 자료를 repo 밖으로 내보내거나 출력하지 않는다. 경로 책임 검토와 민감정보 점검의 필요성만 기록한다.

## 실제 파일명 전수
- `data/eval/m26_fixed_dataset_v1/execution/fills.jsonl` — RF-091
- `data/eval/m26_fixed_dataset_v1/execution/intents.jsonl` — RF-091
- `data/eval/m26_fixed_dataset_v1/execution/order_status.jsonl` — RF-091
- `data/eval/m26_fixed_dataset_v1/features/scanner_monitor_features.jsonl` — RF-091
- `data/eval/m26_fixed_dataset_v1/manifest.json` — RF-091
- `data/eval/m26_fixed_dataset_v1/market/corporate_actions.csv` — RF-091
- `data/eval/m26_fixed_dataset_v1/market/ohlcv_1d.csv` — RF-091
- `data/eval/m26_fixed_dataset_v1/market/ohlcv_1m.csv` — RF-091
- `data/eval/m26_fixed_dataset_v1/market/ohlcv_5m.csv` — RF-091
- `data/eval/m26_fixed_dataset_v1/microstructure/top_of_book.jsonl` — RF-091
- `data/eval/m26_fixed_dataset_v1/news/headlines.jsonl` — RF-091
- `data/eval/m26_fixed_dataset_v1/news/sentiment_by_symbol.jsonl` — RF-091
- `data/eval/m26_fixed_dataset_v1/news/sentiment_daily.jsonl` — RF-091
- `data/m15_demo_events.jsonl` — RF-091
- `data/m15_demo_intents.jsonl` — RF-091
- `data/originals/- 복사본.env` — RF-091
- `data/originals/키움 REST API 문서.xlsx` — RF-091
- `data/specs/api_catalog.jsonl` — RF-091
- `data/specs/default_rules.json` — RF-091
- `data/specs/kiwoom_api_list_tagged.jsonl` — RF-091
- `data/specs/kiwoom_apis.jsonl` — RF-091
- `data/state.json.bak_20260317_1023` — RF-091
- `data/state.json.bak_reset_20260317_103653` — RF-091
- `data/state.pre_force_sell_20260331_134241.json` — RF-091
- `data/state.pre_restart_20260331_1.json` — RF-091

## 공통 RF 완료 게이트
- **계획이지 이동 승인은 아님.** 실제 import·API·launcher·scheduler·State·serialization·effect 소비자를 확인한 뒤 해당 RF에 path별 MOVE / KEEP_VERIFIED / COMPAT / SAFETY_HOLD / REMOVE_PROVEN 결정을 남긴다.
- 기존 baseline normal/optimized, 신규 exact-SHA independent read-only review, integration SHA hosted CI, 롤백 기준을 증명한다. 승인 없는 main·실거래·CI oracle 변경 금지.
- 정본 링크: [T00](T00_TARGET_TREE.md) / [D00](../../ENGINEERING_DELIVERY_POLICY.md) / [STATUS](../plan/STATUS.md) / [RF baseline CSV](../plan/FILE_COVERAGE_63182ab2.csv).
