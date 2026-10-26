# P1.5 RF-012 시장가격 유한성 — 기존 BASE 안전 관측 (2026-10-26 22:38 KST)

- **상태:** `OPEN / SAFETY_REVIEW_REQUIRED / BASELINE_BEHAVIOR / RUNTIME_IMPACT_UNKNOWN`. 지팀장 소유 증거 판정, 실제 원개발 소유 RF-012는 현재 `01_PENDING/UNASSIGNED`(RF-008 소유 아님). 사용자 승인 전 거래 안전 계약/운영 코드 변경 금지.
- **정확 소스:** `graphs/nodes/build_market_snapshot.py` Git blob `af11f9d64d6fa1965beb9f4140e2ce372aa1ce46` (4,127 bytes), BASE `63182ab2` = A = integration. 원격 FILE_COVERAGE CSV에 RF-012 소유, `graphs/nodes/strategist_node.py`는 RF-008 소유.
- **지팀장 신규 재현:** 로컬 격리 byte-identical source + importlib 가짜 PriceReader/KiwoomReader(trap, 실 HTTP/주문/파일/SQLite 없음), `AGENTRA_RF008_SOURCE=build_market_snapshot.py PYTHONDONTWRITEBYTECODE=1 python lead_rf008_price_finiteness.py` / `python -O` **각 8/8 PASS exit0**, 새 pyc 0. 재현 하네스 `docs/refactor/work_orders/evidence/lead_rf008_price_finiteness.py` blob `36445c0d438380ff458b20b6671489d38f2896e7`, commit `0da98a4758c034f052fff2a132b17c85c84f06c0`. PASS는 **현재 동작을 재현했다는 의미**이며 가격 유효성 보장 PASS가 아니다.
- **실제 관찰:** `mock/paper/real`의 injected reader가 반환한 NaN/Infinity가 `market_snapshot`에 그대로 들어가며 `reader_ok=True` 유지; paper 음수도 통과. mock reader 실패 후 `MOCK_PRICE_FALLBACK=nan` 또는 persisted Infinity가 그대로 수용된다. mock 음수는 기본 70000으로 대체된다. `KIWOOM_MODE` 미설정은 기본 mock이며 실패 시 fallback 동작. `NaN/Infinity` 가격의 downstream 사용·주문 영향, 실제 브로커 유입 여부는 **NOT_RUN/UNKNOWN**.
- **분류:** 새 P1.5 원개발 회귀 **아님**(BASE 동일). RF-008의 기존 graph consumer 인수와는 별도 **RF-012 교차 소유 안전 검토**. Issue #32의 SELL provenance/OCI source 미확정과 동일 원인이라고 추정하지 않는다. 원개발 RF-008을 REWORK로 옮기거나 안전 계약을 고치지 않는다.

## 해제 조건 및 책임

1. **지팀장:** RF-012 원소유·상류 reader/downstream consumer(가격 finite guard/State/eligibility/주문 효과)를 읽기 전용으로 매핑하고 실제 위험 범위를 결정. 기존 안전 정책 변경이 필요하면 사용자에게 정확한 범위·영향·회귀 계획을 제시해 사전 승인 받는다.
2. **승인된 RF-012 소유자:** 승인된 경우에만 최소 안전 변경을 격리 브랜치에서 수행하고, BASE/후보 normal·`python -O` 동일 합성 경계와 효과 차단·정확 SHA를 제출. 원본 테스트/CI 오라클 무승인 수정 금지.
3. **상대 독립 peer → 지팀장:** 신규 변경 경계만 검증하고, 정확 통합 source/test/workflow tree·필수 CI 판정 후 본 open을 closed로 이동할지 결정. 운영 재배포/실거래/예약 변경은 별도 승인.

**현재 결론:** 실제 테스트로 유한성 미검증 경계가 확인되었으나 실제 거래 영향은 미확정. 승인 없는 코드 FIX/REWORK/재배포 없음. `OPEN` 유지.


## 지팀장 2026-10-26 23시 KST — RF-012 다운스트림 신규 정적 추적 (OPEN 유지)

- **정확한 GitHub source/tree read-only:** `build_market_snapshot.py` blob `af11f9d6`의 `state["market_snapshot"] = snap.to_dict()` 및 `persisted_state.last_market_price` 갱신(89~97행). 실제 호출자는 `graphs/pipelines/m11_2_live_pipeline.py`(blob `41766fe2`, 8/21행), `graphs/pipelines/offhours_validation.py`(blob `9a5c7576`, 198/237행)에서 확인. RF-008 owner facade와 별개.
- **주문 경계의 직접 읽기:** `graphs/nodes/execute_from_packet.py` blob `1a10af59`(보호 계약, **읽기만**). `_coerce_float` 162~166행은 `float(value)` 후 예외만 처리하여 Infinity를 제거하지 않음; `_positive_price_from_row` 1634~1642행은 `abs(px)>0`로 필터해 **양의 Infinity를 후보로 허용할 수 있음**; `_resolve_order_price_for_notional_with_source` 1756~1763행은 `state.market_snapshot`을 후보에 추가하고 1776행 `max(price_candidates)`로 선택. 따라서 **합성/정적 경로상 비유한 가격이 notional price 후보에 들어갈 수 있는 가능성** 확인. NaN은 비교에서 걸러질 수 있으나 모든 경로 안전성은 증명되지 않음. 보호 실행/실주문/런타임 재현 **NOT_RUN**; 실제 주문 유입·계좌 영향 **UNKNOWN**.
- **지팀장 분류:** `BASELINE_BEHAVIOR / SAFETY_REVIEW_REQUIRED / CROSS_RF012`, 새 RF-008 회귀나 Issue #32 SELL 원인으로 연결하지 않음. `RF-008` 기존 strategist owner KEEP 종결과 별도로 이 OPEN은 유지. 다음 최초 해제 행동: RF-012 원소유 및 실행 안전 승인권자가 `_resolve_order_price_for_notional_with_source` downstream에서 Infinity 후보가 주문 금액/eligibility까지 도달하는지 **보호 코드 수정 없이** detached fake-only normal/-O 검증; 명령/정확 SHA/State·외부효과 0 제출. 실제 변경은 사용자 사전 승인 필요.

## 지팀장 B 슬롯 — 보호 주문가격 순수 경계 신규 격리 실행 (2026-10-26 23시 KST)

- **신규 직접 실행:** `graphs/nodes/execute_from_packet.py` Git blob `1a10af59e5e9b4035f1c7403e5aeb814f65c8e3a`의 `_coerce_float` / `_positive_price_from_row` / `_resolve_order_price_for_notional_with_source` **함수 정의만** 별도 임시 복사본에서 AST 추출·compile. 외부 의존성 `_extract_order_symbol`, `_symbol_matches_row`, `_extract_market_quotes_safe`, `_canonical_artifact_row`는 in-memory fake. 실제 보호 모듈 import·broker/order/fetch/file write 없음. **운영 원본 실행 아님**.
- **정상/-O 각각 9/9 관찰 PASS, exit 0:** `RF012_SOURCE=<격리된_함수_복사본> PYTHONDONTWRITEBYTECODE=1 python /mnt/data/agentra_lead_20261026/lead_rf012_notional_ast.py` 및 `python -O`에서 `RF012_NOTIONAL_AST_OK cases=9 inf=6 nan_ignored=1 writes=0`. Infinity가 `order.price`, `order.meta.price`, `market_snapshot.price`, `selected.price`, `market.quote.best_ask` 및 finite 후보와 경쟁하는 `max` 경로에서 선택되는 **6건을 동적 재현**. NaN 단독 후보는 0으로 제외(1건), 정상 finite 및 음수 절댓값 변환 2건. 입력 State 변형 0. 이 PASS는 **위험 동작의 재현**이지 가격 안전성 PASS가 아님.
- **재현 증거:** GitHub `docs/refactor/work_orders/evidence/lead_rf012_notional_ast.py` (commit `23c6410b8a53a7e69dc4767e18f6172ba257108f`)에 **정확 원본 Git blob SHA fail-closed 검사**와 위 9개 AST 격리 시나리오를 보존. 지팀장 로컬 실행은 격리 복사본 기반이며, **GitHub 저장본을 원본 4,106행 전체와 함께 직접 재실행한 결과는 NOT_RUN**. 로컬 실행 스크립트 SHA256 `e3c10bab7fb575f00bd71b7ce4f2df69cdcea3d317da1a7edb052b0faa4efd5f`; GitHub 저장본과 바이트 동일이라고 주장하지 않는다.
- **판정/해제:** `BASELINE_EXISTING / SAFETY_REVIEW_REQUIRED / NO_SOURCE_CHANGE / OPEN`. 이 순수 resolver가 Infinity를 반환할 수 있다는 범위는 입증됐으나 **후속 notional/eligibility/실주문 도달·런타임 영향은 여전히 UNKNOWN**. 다음 최초 행동은 **승인된 RF-012 안전 검증 담당자**가 detached repo에서 저장본을 normal/-O 최초 실행하여 원본 blob 일치와 9/9 재현을 독립 확인하고, 그 결과가 downstream guard에서 fail-closed 되는지 주문 효과 0인 synthetic 경계로 확인하는 것. 안전 구현 수정·재배포·실거래는 사용자 사전 승인 필요. RF-008 DONE 및 Issue #32 SELL 출처 문제와 원인 혼동 금지.

