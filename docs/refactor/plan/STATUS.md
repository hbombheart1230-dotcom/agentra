# Agentra P1.5 — STATUS

정본: `integration/p1.5:docs/refactor/work_orders/CURRENT.md`. 정책 D00은 읽기 전용. 상세 재현은 기존 RF·HANDOFF와 Git 이력. **새 운영 source 통합 0 / 새 DONE 0**.

## 물리 큐·SHA

PENDING **61** / DEVELOPING **3** / PEER **1** / LEAD **14** / DONE **14** / REWORK **0** = **93 RF 단일 경로**(.gitkeep 제외, 중복 0). LEAD: 014,015,016,028,029,031,032,033,034,050,063,065,067,069.

- 기준 integration `ec1e302fbce72b7c56a74767bc5d474d65dd59b5`: 최근 변화는 RF-031·STATUS·CURRENT 문서만. A `61e6aadc03b3dba277e9c67f618067f25ef4647a`: 기존 `1fe4efe3` 이후 운영 source 0, 보존된 독립 CLI 경계 스크립트 7개와 HANDOFF. B `b2399dfb9310cc5f23afe376bd2ce910b6be0313`: 기존 `2b1cd7da` 이후 HANDOFF만, 운영 source 0·재현 peer 하네스 미보존.
- **A 독립 peer — 범위 한정:** RF-063 diagnostics `run_*` 46 CLI 및 효과형 `check_*` 4 CLI 실제 subprocess, RF-065 research 기본 실행 46 CLI + 필수 인자 정상경로 19, RF-067 위임 target 추가 6종 등. A 보고 BASE/integration × normal/`python -O` 동일·격리 tmp only, 현 지팀장 재실행 **NOT_RUN**. CLI 의미 완전성·실제 Windows Scheduler·보호 실호출 PASS 아님.
- **B 독립 peer — 보고 범위 한정:** RF-031 caller fake ledger/memory 및 강제 최종 Markdown OSError, normal/`-O` 각각 exit 0 **B 보고**(`RF031_CALLER_LEDGER_MEMORY`, `RF031_PARTIAL_CONSUMER`). 다른 014/015/016/028/029/032/033/034/050도 독립 scoped marker 보고. 하네스/정확 실행 명령 미보존이므로 재현 가능한 전체 peer PASS·DONE으로 확대 금지. RF-031 pytest 호출은 `No module named pytest` normal/`-O` 각 exit 1 **ENV**, CODE REWORK 아님.

## LEAD 최초 남은 게이트·책임

| RF | 첫 부족 경계 · 해제 담당 |
| --- | --- |
| 014 | shim→실 runtime Top1/ranking/NOOP 동적 소비자 · B |
| 015 | 역사 11 FAIL의 BASE node별 대응·B-only 2파일 실사용 확인 · B, 새 소비자 발생 시 A peer |
| 016 | news-query→strategic_answers 예외 projection·외부 dynamic 소비자 · B |
| 028 | 정식 rich schema memory/monitor→summary/full renderer·writer · B |
| 029 | external truth-root 실제 읽기/실패·State 예외 · B |
| 031 | 부분 파일 실패 뒤 Reporter **downstream 복구 소비자** · B (reproducible tmp-only 하네스·명령·exit 필요) |
| 032 | public validation_id 신뢰·Stage2 부분 OSError 및 보호 UEF 승인 · B/사용자 |
| 033 | provider→storage 실패 시 State/파일 부작용·복구 · B |
| 034 | casebook→Scanner 소비자; 이후 latent producer temp cache/output · B |
| 050 | model_catalog_store temp 캐시 artifact/부분실패 · B |
| 063 | effectful CLI 기본 외부 경로·실 Windows scheduler 소비자. BASE 기존 `run_m23_closeout_check` text-mode `day` NameError 확인, 변경은 별도 사용자 승인 · A/사용자 |
| 065 | 안전 범위 소진; 실데이터 의미·보호 CLI·Windows Scheduler/외부 소비자 · 사용자/검증 환경 소유자 |
| 067 | 보호 preflight/UEF 및 Windows Task Scheduler·PowerShell live 경계 · 사용자/검증 환경 소유자 |
| 069 | historical UEF5 snapshot **path/SHA/use-scope** 승인 전 SAFETY_HOLD · 사용자/증거 소유자 |

RF-063에서 기본 repo `data/reports` 쓰기, cwd별 경로 분기, 연구 CLI의 기본 Kiwoom 인증 진입도 A 안전 격리에서 관찰. 실 인증·브로커·운영 경로 실행은 **NOT_RUN**. 위는 기존 BASE 동작과 같아 신규 원개발 REWORK로 자동 분류하지 않음.

## 재사용 검증·RunLab·안전

- CI 재사용은 **동일 source/test/workflow tree에 한정**: Safety SUCCESS `40332899631@0da98a47`, Web SUCCESS `40073316192@1374d371`. 이번 최신 문서/peer-only 커밋에 대한 신규 CI **NOT_RUN**.
- RunLab #32 최신 확인 증거는 2026-10-27 **09:38 KST** 독립 검증. mock SELL `0045749` 체결·보유 출처 불명, 어제 SELL `0020349` 출처/로컬 누락, OCI `RUN_SOURCE_SHA=UNKNOWN` ⇒ 런타임 전체 BLOCKED; 무승인 재배포·주문·가드 수정 금지. 이 회차 후속 신규 Issue 증거 없음.
- D00·main·Broker/Supervisor/Executor/Step5C/UEF·frozen CI/테스트·운영 데이터·스케줄 변경 0. 기존 troubleshooting 4 open/1 closed 유지; 해결 근거 없어 이동 0. 사용자 승인 전 운영 소스 수정 0. 선별 통합 대상 없음.
