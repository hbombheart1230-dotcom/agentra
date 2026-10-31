from typing import Any
def _build_parser(*,facade:Any)->Any:
    p=facade.argparse.ArgumentParser(description="M31-3 weekly post-go-live health summary generator.")
    p.add_argument("--event-log-path",default="data/logs/events.jsonl");p.add_argument("--policy-report-dir",default="reports/milestones/m30_post_golive");p.add_argument("--signoff-report-dir",default="reports/milestones/m30_golive");p.add_argument("--report-dir",default="reports/milestones/m31_weekly_health");p.add_argument("--week-end",default="2026-02-21");p.add_argument("--days",type=int,default=7);p.add_argument("--max-error-rate",type=float,default=.20);p.add_argument("--max-incident-days",type=int,default=1);p.add_argument("--inject-fail",action="store_true");p.add_argument("--json",action="store_true")
    return p
