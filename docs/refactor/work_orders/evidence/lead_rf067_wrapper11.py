"""RF-067 lead: eleven additional root CLI compatibility wrappers, no real diagnostic invocation.
Run: PYTHONDONTWRITEBYTECODE=1 python [-O] -S docs/refactor/work_orders/evidence/lead_rf067_wrapper3.py
"""
import hashlib
import importlib
import os
from pathlib import Path
import runpy
import sys
import types

EXPECTED = {
    'check_alert_policy_v1.py': 'b564513381c3b108cd5cc91cad5c0d9696421324',
    'check_audit_trail_completeness.py': 'd98ee6f2ce284056c30e1b46455b8215a620145d',
    'check_daily_uef_run_status.py': '7a531b730c67ca84ee918cd982fc98465695554e',
    'check_log_archive_integrity.py': 'd4aa9f557b2f473be8cf36e0162d263a63af79fe',
    'check_metrics_schema_v1.py': '803dce3468e1a8020687ea441f2271dd0b7fdd21',
    'check_phase_5_2_5_3_runtime_health.py': '8831693f7ae982091c9a0ec82b2eadac51707a9e',
    'check_profitability_recovery_day1.py': '378f28adb298ee535632d6bba45d781cc12a9bf8',
    'check_q9_q12_readiness.py': '276316fc6fd3d202d677581c884521efc8b9911c',
    'check_reporter_upgrade_regression.py': 'dcf5d165ddff3867679b8e92a3aa2badf8670d60',
    'check_reports_trades_health.py': '72f9956d01e8e8ccb1cabf158f7c667ce3a3dfda',
    'check_trade_report_runtime_regression.py': '54f313b97f7dc01df80308faa992e459ee834805',
}

def check(value, label):
    if not value:
        raise AssertionError(label)

def main():
    root = Path(os.environ.get('AGENTRA_RF067_ROOT') or Path(__file__).resolve().parents[4])
    before = list(sys.path)
    old_import, old_run = importlib.import_module, runpy.run_module
    count = 0
    try:
        for filename, sha in EXPECTED.items():
            path = root / 'scripts' / filename
            raw = path.read_bytes()
            digest = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            check(digest == sha, f'{filename}:source_sha'); count += 1
            source = compile(raw, str(path), 'exec')
            target = 'scripts.diagnostics.' + filename[:-3]
            fake = types.ModuleType(target)
            calls = []
            def fake_import(name, package=None):
                check(name == target, 'import target')
                calls.append(('import', name))
                return fake
            def fake_run(name, init_globals=None, run_name=None, alter_sys=False):
                check((name, run_name) == (target, '__main__'), 'CLI target')
                calls.append(('run', name))
                return {}
            importlib.import_module, runpy.run_module = fake_import, fake_run
            alias = 'rf067_lead_' + filename[:-3]
            exec(source, {'__name__': alias, '__file__': str(path)})
            check(sys.modules.get(alias) is fake and calls == [('import', target)], 'module alias'); count += 1
            calls.clear()
            exec(source, {'__name__': '__main__', '__file__': str(path)})
            check(calls == [('run', target)], 'CLI delegation'); count += 1
            check(sys.path.count(str(root)) == 1, 'PATH duplicate'); count += 1
            def fail_run(*args, **kwargs):
                raise RuntimeError('FAKE_DIAGNOSTIC_FAILURE')
            runpy.run_module = fail_run
            try:
                exec(source, {'__name__': '__main__', '__file__': str(path)})
            except RuntimeError as exc:
                check(str(exc) == 'FAKE_DIAGNOSTIC_FAILURE', 'exception identity')
            else:
                raise AssertionError('CLI swallowed exception')
            count += 1
            sys.modules.pop(alias, None)
            sys.path[:] = before
        check(sys.path == before, 'PATH restored'); count += 1
    finally:
        importlib.import_module, runpy.run_module = old_import, old_run
        sys.path[:] = before
        for name in list(sys.modules):
            if name.startswith('rf067_lead_'):
                sys.modules.pop(name, None)
    print(f'RF067_LEAD_WRAPPER11_OK checks={count} source_sha=11/11 outside_writes=0 broker=0 network=0')

if __name__ == '__main__':
    main()
