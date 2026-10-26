"""Lead-only isolated failure-boundary test of exact extracted RF-032 writer.
Source: libs/reporting/evaluation/scanner_alignment_root_cause.py
Git blob 8774bea29dd8ebd83283b28c5109e5fc6210fd1a
Extracted function FNV32 9ee11dea (ASCII source, no trailing newline).
No import of repository modules, no operational data or network.
"""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory

SOURCE = '''def write_scanner_alignment_root_cause_range(
    *,
    reports_root: Path = Path("reports"),
    start: str,
    end: str,
) -> dict[str, str]:
    reports_root = Path(reports_root)
    payload = build_scanner_alignment_root_cause_range(
        reports_root=reports_root,
        start=start,
        end=end,
    )
    out_dir = reports_root / "evaluation" / "range" / f"{start}_{end}"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "scanner_alignment_root_cause_report.json"
    md_path = out_dir / "scanner_alignment_root_cause_report.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    md_path.write_text(render_scanner_alignment_root_cause_report(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}'''

def fnv32(s):
    h=2166136261
    for b in s.encode('utf-8'):
        h=((h^b)*16777619)&0xffffffff
    return f'{h:08x}'
assert fnv32(SOURCE)=='9ee11dea', fnv32(SOURCE)

calls=[]
def build_scanner_alignment_root_cause_range(*,reports_root,start,end):
    calls.append(('build',reports_root,start,end))
    if start=='FAIL_BUILD': raise ValueError('synthetic build failure')
    return {'start':start,'end':end,'status':'NEW','unicode':'검증'}
def render_scanner_alignment_root_cause_report(payload):
    calls.append(('render',payload['status']))
    if payload['start']=='FAIL_RENDER': raise RuntimeError('synthetic render failure')
    return 'new markdown\n'
ns={'Path':Path,'json':json,'build_scanner_alignment_root_cause_range':build_scanner_alignment_root_cause_range,'render_scanner_alignment_root_cause_report':render_scanner_alignment_root_cause_report}
exec(compile(SOURCE,'github_extracted_writer.py','exec'),ns)
writer=ns['write_scanner_alignment_root_cause_range']
checks=0
def check(ok,label):
    global checks
    if not ok: raise AssertionError(label)
    checks+=1

with TemporaryDirectory(prefix='agentra_lead_rf032_') as d:
    root=Path(d)
    sub=root/'evaluation'/'range'/'2026-10-20_2026-10-21'
    sub.mkdir(parents=True)
    jp=sub/'scanner_alignment_root_cause_report.json'
    mp=sub/'scanner_alignment_root_cause_report.md'
    jp.write_text('OLD_JSON',encoding='utf-8')
    mp.write_text('OLD_MD',encoding='utf-8')
    original=Path.write_text
    try:
        def fail_md(self,*args,**kwargs):
            if self==mp: raise OSError('synthetic markdown write failure')
            return original(self,*args,**kwargs)
        Path.write_text=fail_md
        try: writer(reports_root=root,start='2026-10-20',end='2026-10-21')
        except OSError as e: check('markdown' in str(e),'md failure propagates')
        else: raise AssertionError('md error swallowed')
    finally: Path.write_text=original
    check(json.loads(jp.read_text())['status']=='NEW','JSON updated before md failure')
    check(mp.read_text()=='OLD_MD','old markdown remains')
    check(calls[:2]==[('build',root,'2026-10-20','2026-10-21'),('render','NEW')],'build render order')

    jp.write_text('OLD_JSON',encoding='utf-8')
    mp.write_text('OLD_MD',encoding='utf-8')
    try:
        def fail_json(self,*args,**kwargs):
            if self==jp: raise PermissionError('synthetic json permission')
            return original(self,*args,**kwargs)
        Path.write_text=fail_json
        try: writer(reports_root=root,start='2026-10-20',end='2026-10-21')
        except PermissionError: check(True,'json failure propagates')
        else: raise AssertionError('json error swallowed')
    finally: Path.write_text=original
    check(jp.read_text()=='OLD_JSON','json preserved when first write fails')
    check(mp.read_text()=='OLD_MD','md preserved when first write fails')

    jp.write_text('OLD_JSON',encoding='utf-8')
    mp.write_text('OLD_MD',encoding='utf-8')
    try: writer(reports_root=root,start='FAIL_RENDER',end='2026-10-21')
    except RuntimeError: check(True,'render failure propagates')
    else: raise AssertionError('render error swallowed')
    check((root/'evaluation'/'range'/'FAIL_RENDER_2026-10-21'/'scanner_alignment_root_cause_report.json').exists(),'render failure leaves newly written JSON')
    check(not (root/'evaluation'/'range'/'FAIL_RENDER_2026-10-21'/'scanner_alignment_root_cause_report.md').exists(),'render failure leaves markdown absent')

    try: writer(reports_root=root,start='FAIL_BUILD',end='2026-10-21')
    except ValueError: check(True,'build failure propagates')
    else: raise AssertionError('build error swallowed')
    check(not (root/'evaluation'/'range'/'FAIL_BUILD_2026-10-21').exists(),'build failure before mkdir')

    out=writer(reports_root=root,start='2026-10-20',end='2026-10-21')
    check(set(out)=={'json','markdown'},'returned paths')
    check(jp.read_text().endswith('\n'),'JSON newline')
    check(mp.read_text()=='new markdown\n','MD success')
    check(json.loads(jp.read_text())['unicode']=='검증','unicode json')
    check(all(str(Path(x).resolve()).startswith(str(root.resolve())+'/') for x in out.values()),'all outputs temp only')
print(f'RF032_SCANNER_ALIGNMENT_PARTIAL_LEAD_OK cases={checks} source_blob=8774bea2 fnv32={fnv32(SOURCE)} partial_json_new_md_old=YES writes=tmp_only net=0 broker=0')
