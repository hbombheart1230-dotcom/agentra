# C02 — Claude A | RF-031 실제 구조 분리 (다음 실행)

**진입:** 원격 `integration/p1.5`의 이 C02 파일만 먼저 읽고 `CANONICAL_HEAD / ORDER_BLOB_SHA / A_REMOTE_SHA` 고정. A 허용 브랜치 `work/p15-a-reporter-pure-20261021`의 **code/test만** 수정. D00 §2 FAST-3, 실계좌·주문·운영 State/파일·외부 LLM/네트워크·보호 Guard·타인 브랜치·문서·force push 금지.

## 1. 최우선 — RF-031 Reporter AI 입력 구성의 **실제 코드 분리**

- **SOURCE:** `libs/reporting/reporter_ai_review.py` Git blob `a8c2507f70d2293b0a106830d9366b64b498236c` (integration/A/emergency 동일, 약 500줄). 시작할 때 A 원격을 재조회해 변경·충돌 없는지 확인.
- **Owner C03 승인 경로:** 신규 `libs/reporting/reporter_ai_review_input.py`는 RF-031의 기존 독점 패턴 `libs/reporting/(trade_report_|reporter_|trade_story_)*.py`에 해당. 새 테스트 `tests/test_rf031_reporter_ai_review_input_extraction.py`는 RF-031에 귀속. 경로 충돌 시 중단·보고, 다른 RF 파일 수정 금지. C05가 통합 시 파일 매니페스트/소유권 동기화.
- **실제 구현:** 원래 `_build_compact_input(day,out)` 150~259행(약 110줄) 및 `_build_messages(day,compact_input)` 262~305행(약 44줄)의 **함수 몸체**를 새 모듈로 이전한다. 함수 내부 사소한 정리로 코드 중복을 늘리지 말고, `reporter_ai_review.py`에는 기존 두 함수명·시그니처의 **얇은 위임 facade만** 남긴다. 기존 모듈의 `_clip_str`, `_list_str` 및 `json.dumps`를 monkeypatch하는 소비자가 있을 수 있으므로 사용 시점 주입/위임으로 동작을 보존한다. 출력 dict/LLM prompt의 키 순서·UTF-8 문자열·truncation·기존 malformed 예외 및 중첩 alias, 입력 원본 불변 계약은 그대로. 신규 module은 순수 데이터 투영·메시지 구성만 담당하고 LLMRouter·ledger·운영 IO import 금지.
- **검증:** A 고정 SOURCE의 old/new 함수에 동일 정상·누락/malformed·중첩 변형·JSON 한글·monkeypatch 입력을 주어 **bytes/key order/output/exception/원본 불변성** 비교하는 새 pytest를 작성. 관련 기존 `reporter_ai_review`/reporter tests와 함께 `python -m pytest` 정상 exit0 확보; 가능하면 `python -O` 추가하되 필수는 아님. pytest 장애면 재현 가능한 임시 stdlib smoke exit0를 확보하되 원본 테스트 미실행은 NOT_RUN으로 구분.
- **계량 인수 기준:** `reporter_ai_review.py`에서 실제 함수 로직 **140줄 이상 감소**, 새 모듈에 해당 원본 로직 이동, 공개 진입 API 유지, 두 source 파일의 원격 Git blob 변화 및 테스트 exit0. **테스트만 추가하거나 KEEP_VERIFIED만 제출하면 이번 과제 미완료.** 새 코드가 더 복잡해지거나 순환 import·기존 monkeypatch 호환 실패면 무리한 푸시 대신 정확 BLOCKED/REWORK 제출.

## 2. 인계

- 작업 후 A 허용 브랜치에 **code/test만 정상 commit/push**, 정확 원격 SHA·변경 2 source+test blob 재조회. 기존 `bed173058613ad97f830001771d0bd7b3c191f30` 작업/테스트 반복 금지.
- #11에 `SOURCE_SHA | BEFORE→AFTER lines | MOVED_FUNCTIONS | TEST_CMD/EXIT | PUSH_REMOTE_SHA/BLOCKED | NEXT`만 보고. 현행 G1/G2는 유효한 source+정상 테스트로 판단. C04/C05가 최소 통합·G3/DONE 수용; **실제 리팩터링 성과는 MOVED_FUNCTIONS/책임분리로만 집계**.
