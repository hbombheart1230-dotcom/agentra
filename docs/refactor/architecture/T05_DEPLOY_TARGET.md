# T05 — deploy/ Docker·Compose·스케줄러 목표트리
> RF-087~089. 현행 파일 33개. 운영 재시작, 실제 브로커/실거래, 배포 모드·접근권한 변경은 별도 승인 대상이다.

## 목표 디렉터리·파일
```text
deploy/
├── compose/
│   ├── .env.example
│   ├── README.md
│   ├── compose.yaml
│   ├── compose.public.yaml
│   └── compose.cloudflare.yaml
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.api.dockerignore
│   ├── Dockerfile.web
│   ├── Dockerfile.web.dockerignore
│   └── nginx.conf
├── trading/                              # SAFETY_LOCK
│   ├── .env.real.example
│   ├── .env.test
│   ├── Dockerfile
│   ├── compose.trading.yaml
│   ├── compose.trading.real.yaml
│   ├── compose.trading.real.dryrun-override.yaml
│   ├── cutover-to-docker.ps1
│   ├── rollback-to-host.ps1
│   └── trading-docker.ps1
├── m28_launch_templates/
│   ├── linux/{scheduler.service,worker.service}
│   └── windows/{scheduler_task,worker_task,daily_uef_evaluation_task}.xml
├── m28_registration_helpers/
│   ├── linux/{install_scheduler_service,install_worker_service}.sh
│   └── windows/{register_scheduler_task,register_worker_task,register_daily_uef_evaluation_task}.ps1
└── m31_registration_helpers/
    └── windows/{register_mock_session_tasks,start_mock_session,stop_mock_session,unregister_mock_session_tasks}.ps1
```

## 세부 목표
| 파일·범위 | 단일 책임·개선 | 처리 |
|---|---|---|
| `compose/compose.yaml`, `compose.public.yaml`, `compose.cloudflare.yaml` | web/api/cloudflared 구성 차이 명시; 중복 진실 설정 최소화 | RF-087 KEEP/COMPARE |
| `docker/Dockerfile.api`, `Dockerfile.web`, `nginx.conf` | 빌드/서빙 각 1 Owner, 계약된 health/ports | RF-088 KEEP |
| `trading/compose.trading.*.yaml`, `trading-docker.ps1` | real/mock/dryrun 절대 혼동 금지, 기존 안전 경로 | RF-089 SAFETY_LOCK |
| `trading/cutover-to-docker.ps1`, `rollback-to-host.ps1` | 실제 운영 전환/롤백 공개 진입점 | RF-089 KEEP, 실행 NOT_RUN |
| `m28_launch_templates/linux/*.service` | systemd 정확한 unit/working directory 경로 | RF-087~089 KEEP |
| `m28_launch_templates/windows/*.xml` | 기존 Task Scheduler 호출 문자열 고정 | RF-087~089 KEEP |
| `m28_registration_helpers/*`, `m31_registration_helpers/windows/*.ps1` | OS별 helper Owner 유지, mock/real 분리 | RF-087~089 KEEP |

## 반드시 확인할 소비자·검증
- scripts root 공개 진입점과 Windows Task Scheduler, Linux systemd, Compose 참조를 먼저 기록. 이름만 바꿔도 호출 중단 가능하므로 대량 이동 금지.
- 기존 Docker restart/crash/SIGTERM drain, volume/secret isolation, dry-run, Broker authority, UEF daily job parity.
- 성공 여부와 실패를 SHA/OS/환경별로 분리. 실제 배포 테스트를 하지 않았다면 NOT_RUN.
- 현행 33파일은 목표 위치를 기본 KEEP. 중복 Compose 키를 검증 없이 병합하거나 real↔mock 기본값 변경 금지.

## 실제 파일명 전수
- `deploy/compose/.env.example` — RF-087
- `deploy/compose/README.md` — RF-087
- `deploy/compose/compose.cloudflare.yaml` — RF-087
- `deploy/compose/compose.public.yaml` — RF-087
- `deploy/compose/compose.yaml` — RF-087
- `deploy/docker/Dockerfile.api` — RF-087
- `deploy/docker/Dockerfile.api.dockerignore` — RF-087
- `deploy/docker/Dockerfile.web` — RF-087
- `deploy/docker/Dockerfile.web.dockerignore` — RF-087
- `deploy/docker/nginx.conf` — RF-087
- `deploy/m28_launch_templates/linux/scheduler.service` — RF-089
- `deploy/m28_launch_templates/linux/worker.service` — RF-089
- `deploy/m28_launch_templates/windows/daily_uef_evaluation_task.xml` — RF-089
- `deploy/m28_launch_templates/windows/scheduler_task.xml` — RF-089
- `deploy/m28_launch_templates/windows/worker_task.xml` — RF-089
- `deploy/m28_registration_helpers/linux/install_scheduler_service.sh` — RF-089
- `deploy/m28_registration_helpers/linux/install_worker_service.sh` — RF-089
- `deploy/m28_registration_helpers/windows/register_daily_uef_evaluation_task.ps1` — RF-089
- `deploy/m28_registration_helpers/windows/register_scheduler_task.ps1` — RF-089
- `deploy/m28_registration_helpers/windows/register_worker_task.ps1` — RF-089
- `deploy/m31_registration_helpers/windows/register_mock_session_tasks.ps1` — RF-089
- `deploy/m31_registration_helpers/windows/start_mock_session.ps1` — RF-089
- `deploy/m31_registration_helpers/windows/stop_mock_session.ps1` — RF-089
- `deploy/m31_registration_helpers/windows/unregister_mock_session_tasks.ps1` — RF-089
- `deploy/trading/.env.real.example` — RF-088
- `deploy/trading/.env.test` — RF-088
- `deploy/trading/Dockerfile` — RF-088
- `deploy/trading/compose.trading.real.dryrun-override.yaml` — RF-088
- `deploy/trading/compose.trading.real.yaml` — RF-088
- `deploy/trading/compose.trading.yaml` — RF-088
- `deploy/trading/cutover-to-docker.ps1` — RF-088
- `deploy/trading/rollback-to-host.ps1` — RF-088
- `deploy/trading/trading-docker.ps1` — RF-088

## 공통 RF 완료 게이트
- **계획이지 이동 승인은 아님.** 실제 import·API·launcher·scheduler·State·serialization·effect 소비자를 확인한 뒤 해당 RF에 path별 MOVE / KEEP_VERIFIED / COMPAT / SAFETY_HOLD / REMOVE_PROVEN 결정을 남긴다.
- 기존 baseline normal/optimized, 신규 exact-SHA independent read-only review, integration SHA hosted CI, 롤백 기준을 증명한다. 승인 없는 main·실거래·CI oracle 변경 금지.
- 정본 링크: [T00](T00_TARGET_TREE.md) / [D00](../../ENGINEERING_DELIVERY_POLICY.md) / [STATUS](../plan/STATUS.md) / [RF baseline CSV](../plan/FILE_COVERAGE_63182ab2.csv).
