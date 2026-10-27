# C02 — Claude A 현재 작업

**목표:** B 소유 RF의 새 peer 게이트를 해소하고 A 소유 RF를 계속 개발한다. **한 건 뒤 다음 건.**
브랜치: `work/p15-a-reporter-pure-20261021` · 고정 규칙: `D00_ENGINEERING_DELIVERY_POLICY.md` · 증거: A 브랜치 `HANDOFF_A.md`

## 지금 할 일 — 완료된 CLI 전수검증 반복 금지

| 순서 | RF | 다음 실행 |
|---|---|---|
| 1 | **063 (06_REWORK, B 수정 후 A 독립 peer)** | A의 pinned NameError와 B 현재 미재현 SHA 차이 확인, 신규 B 수정 시 해당 경계만 peer; diagnostics 46+4 CLI 재실행 금지 |
| 2 | **065 / 067** | 새 B 변경/안전한 실제 소비자 증거에만 peer; 기존 research 46+19·delegated target 재실행 금지 |
| 3 | **015** | B의 Monitor 역사 BASE FAIL·B-only 소비자 **새 근거 도착 시** 독립 peer |
| HOLD | **069** | historical UEF5 snapshot 승인 전 실행 금지 |

**현재 안전한 Linux peer 범위는 대부분 소진.** 새 B 근거가 없으면 검증을 발명하지 말고 아래 원개발 큐로 **즉시** 이동한다.

## 신규 지팀장 물리 Owner 배정 (integration `a8a81430`)

| 우선 | RF | 작업 |
|---|---|---|
| 1 | **043 — catalog 6파일** | `01_PENDING/CLAUDE_A/RF-043.md`에서 시작. 파일별 owner·실제 소비자·import·IO·예외 정적/안전한 temp 검증 후 필요한 최소 구현 또는 KEEP. B 독립 peer 요청; 운영/보호 쓰기 금지 |
| 2 | **035 — reporting 서비스/발행 119파일** | `01_PENDING/CLAUDE_A/RF-035.md`. 기존 RF-074 frozen oracle 차이·외부 발행 writer는 HOLD, 우선 안전한 소비자/State/IO·효과 인벤토리. source 변경 시 별도 peer·patchnotes 검증 |

RF-030은 frozen oracle 승인 HOLD 유지. 신규 B RF-063 수정이 도착하면 A가 그 변경 SHA의 TEXT+JSON 정상/`-O` 분기만 독립 peer한다. 두 RF는 원격 큐 소유권 **배정만 완료**, 구현·테스트 `NOT_RUN`.

## 다음 개발 큐

| 우선 | 실제 작업 |
|---|---|
| 1 | 자기 `02_DEVELOPING/CLAUDE_A` 미완료 구현 |
| 2 | 자기 `06_REWORK/CLAUDE_A` 결함 수정 |
| 3 | `03_PEER_REVIEW/CLAUDE_A` 신규 B 소유 peer |
| 4 | 자기 `01_PENDING/CLAUDE_A` 다음 RF 개발 |

**일반 RF는 사용자·지팀장 개별 승인 대기 없이** 자기 브랜치에서 **구현→테스트→커밋·푸시→HANDOFF·#11→다음 RF**를 반복한다. 자기 큐가 보호 HOLD뿐이면 양쪽 HEAD·HANDOFF·Issue를 확인하여 중복 없는 `01_PENDING/UNASSIGNED` 일반 RF를 **자율 CLAIM하고 즉시 개발**한다. 지팀장은 다음 회차 물리 Owner를 동기화한다. 다른 RF가 가능하면 대기 때문에 종료하지 않는다.
