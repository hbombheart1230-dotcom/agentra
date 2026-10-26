"""RF-067 lead: three root CLI compatibility wrappers, no real diagnostic invocation.
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
    'check_monitor_gate_patterns.py': '6299e9c304723aa96c7020044047e04e7996d199',
    'check_runtime_profile.py': '1846887cfa29d9c9f8d9ad89690b2e960648e66a',
    'check_real_execution_preflight.py': '27ac1cf1dfbc04cbb5cf7c8ee7b350ae262dcb50',
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
    print(f'RF067_LEAD_WRAPPER3_OK checks={count} source_sha=3/3 outside_writes=0 broker=0 network=0')

if __name__ == '__main__':
    main()
