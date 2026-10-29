# C01 — Codex B 이번 회차 실행 명령

작업 브랜치: `work/p15-b-operator-structure-20261022`. 아래 작업을 순서대로 실제 구현한다. 이 파일만 작업 진입점으로 사용한다. 작업 선정·판단·다음 회차 설계는 지팀장이 담당한다.

1. `libs/core/event_logger_compat.py`: 이전 start/end 로그 무음 누락 수정의 **실제 호출자**를 검사한다. `graphs/nodes/assemble_decision_packet.py` 등 기존 호출 경로에서 임시 JSONL에 start/end, stage, run_id가 정확히 기록되는 회귀 테스트를 추가한다. 결함이 재현되면 B 소유 파일만 최소 수정한다. Graph 소스는 건드리지 않는다.
2. `libs/core/log_maintenance.py::apply_log_move_candidates`: 임시 디렉터리에서 목적지 파일이 이미 존재할 때의 삭제·덮어쓰기와 중간 실패 시 원본 보존을 검증한다. 기존 소비자 호환 범위에서 안전하게 고칠 수 있는 결함은 수정한다. 정책 변경이 필요하면 변경하지 말고 보고하고 3번으로 진행한다.
3. `scripts/maintenance/sync_legacy_brief_llm.py::main`: 임시 `--reports-root`로 정상/비어 있는 입력/건조 실행/JSON 출력을 확인한다. 운영 데이터에 쓰지 않는다는 테스트를 추가하고, 재현된 결함만 수정한다.
4. 독립 검증: Claude A 커밋 `a68acfc5`의 `forward_validation/reaction_reader.py` 결측 CLOSE 처리와 호출자 출력만 기존 승인된 격리 환경의 임시 복사본에서 검증한다. A 소스 수정 금지.

변경된 코드·테스트를 정상 및 `python -O`로 검증하고, B 브랜치에 커밋·푸시한 정확한 SHA와 실행 결과를 Issue #12 댓글에 보고한다. 첫 PASS나 첫 커밋으로 종료하지 말고 가능한 작업을 이어서 수행한다. 실제 실행 한도나 위험 경계에 걸리면 다음 안전 항목으로 넘어가고 중단점을 남긴다. 네트워크·실거래·Broker·Step5C·UEF·운영 파일은 실행하거나 변경하지 않는다. 문서·큐·상대 소스는 수정하지 않는다.
