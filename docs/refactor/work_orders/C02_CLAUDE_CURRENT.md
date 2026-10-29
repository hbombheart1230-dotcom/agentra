# C02 — Claude A 이번 회차 실행 명령

작업 브랜치: `work/p15-a-reporter-pure-20261021`. 아래 작업을 순서대로 실제 구현한다. 이 파일만 작업 진입점으로 사용한다. 작업 선정·판단·다음 회차 설계는 지팀장이 담당한다.

1. `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py`: 실제 CLOSE가 없을 때 참고용 마지막 가격을 CLOSE/수익률에 사용하지 않는지 호출자까지 검증한다. 누락·시간 경계·0 거래량 입력의 실패 테스트를 추가하고, 재현된 결함은 A 소유 코드만 수정한다.
2. 같은 패키지의 `scoring.py`, `shadow_comparison.py`, `report.py`: 결측 반응 데이터와 불충분한 표본이 점수·비교·보고에 잘못 반영되는지 합성 데이터로 확인한다. 실제 오류가 있으면 최소 수정하고 전후 출력을 검증한다.
3. `libs/reporting/baseline_btc_woori_tech/forward_returns.py`와 `vnext/report.py`: 결측 시계열·0 기준값·출력 순서·표본 부족 입력을 임시 fixture로 확인하고, 재현된 결함만 수정한다.
4. 독립 검증: Codex B 커밋 `e33929dd`의 `libs/core/event_logger_compat.py` 수정이 실제 호출자의 start/end 누락을 복구했는지 기존 승인된 격리 환경의 임시 복사본·임시 JSONL로 검사한다. B 소스 수정 금지. 남은 결함은 정확한 재현 절차를 보고한다.

변경된 코드·테스트를 정상 및 `python -O`로 검증하고, A 브랜치에 커밋·푸시한 정확한 SHA와 실행 결과를 Issue #11 댓글에 보고한다. 첫 PASS나 첫 커밋으로 종료하지 말고 가능한 작업을 이어서 수행한다. 실제 실행 한도나 위험 경계에 걸리면 다음 안전 항목으로 넘어가고 중단점을 남긴다. 네트워크·실거래·Broker·Step5C·UEF·운영 파일은 실행하거나 변경하지 않는다. 외부 호출은 fake, 파일은 임시 경로로 격리한다. 문서·큐·상대 소스는 수정하지 않는다.
