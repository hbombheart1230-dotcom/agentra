# D02 — Claude A 실행 규칙

> [CURRENT](docs/refactor/work_orders/CURRENT.md) 우선 → [D00](docs/ENGINEERING_DELIVERY_POLICY.md) 공통 계약. D00은 변경·충돌·안전 판단 때만 재독.

- **브랜치:** `work/p15-a-reporter-pure-20261021`; 로컬 `C:\Users\홍훈\Agentra-P15\dev-a` 또는 클라우드 checkout. ROOT·checkout·origin HEAD 확인. 신규 브랜치/force push 금지.
- **개발:** CURRENT의 **Claude A 개발** RF 전부를 소유권 범위에서 진행. 차단된 RF는 BLOCKED로 인계하고 나머지 계속. normal/-O·위험 표적 회귀·UI patchnotes JSON/MD는 D00 준수.
- **상대 검증:** CURRENT의 **Claude A 독립 검증** 링크(`verification/codex/`, Codex 작성 RF)를 별도 read-only 세션에서 exact SHA 검증. 자기 변경 self PASS 금지, 상대 CLI 직접 호출 금지.
- **검증 결함 수정 루프:** Claude A가 Codex B RF를 read-only 검증 중 실제 결함을 발견하면 정확한 실패 node·경로·BASE/후보 SHA·최소 패치를 `FIX_REQUIRED/REWORK`로 제출한다. **Codex B가 승인된 자기 RF 경로를 직접 수정**하도록 하고 신규 SHA만 재검증한다. 문제가 Claude A의 **현재 개발 배정 RF/독점 경로**에 있으면 read-only 검증을 종료하고 별도 개발 세션에서 **Claude A가 직접 소스 수정·normal/-O·push**한다. Codex 작성 RF를 Claude A가 직접 수정할 필요가 있으면 지팀장이 **사전에 RF+CURRENT로 writer 역할을 인계한 경우**에만 별도 개발 세션에서 수행한다. 수정한 신규 delta에 대한 Claude 자기 peer PASS 불가. 안전·공개 계약·교차 RF·CI oracle 권한은 D00 그대로.
- **인수인계:** 자기 브랜치 `docs/refactor/work_orders/HANDOFF_A.md` **최신 회차 10~20줄만 유지**, 이전 기록은 Git 이력. 코드 후보 SHA·normal/-O·peer verdict·BLOCKED·CI·GPT_ACTION_REQUIRED·push 재조회 결과만 간결히 기재. RF/STATUS 공용 상태는 GPT가 관리. 빈 영수증 커밋 금지.
- **통합:** 독립 PASS한 Codex RF만 별도 승인 경로·writer/CAS·exact integration SHA normal/-O·hosted CI 확인. GPT만 done. Quick Fix는 D00의 사전 명시 승인에 한함.
- **안전:** main/실거래/안전 계약/CI 오라클 무승인 변경 금지. 불가한 일은 NOT_RUN/UNKNOWN/BLOCKED로 보고.
