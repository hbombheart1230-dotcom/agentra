from __future__ import annotations
import html, json, sys
from pathlib import Path

def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print('usage: render_p15_import_matrix.py input.json output.svg', file=sys.stderr)
        return 2
    d=json.loads(Path(argv[1]).read_text(encoding='utf-8'))
    groups=d['columns']; roots=d['rows']; rows=d['values']
    assert len(roots)==len(rows) and all(len(r)==len(groups) for r in rows)
    cw,rh,x0,y0,H,W=95,30,470,152,610,1510
    pin=d['source_sha']
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="1510" height="610" viewBox="0 0 1510 610">',
       '<title>Agentra source-pinned partial direct import matrix</title>',
       '<desc>Static import snapshot at '+pin+'. Twelve selected entry files, not exhaustive repo dependency/call graph.</desc>',
       '<rect width="1510" height="610" fill="#ffffff" rx="16"/>',
       '<text x="24" y="40" font-size="24" font-family="sans-serif" font-weight="bold" fill="#17243d">Agentra — measured import sample (not full DAG)</text>',
       '<text x="24" y="67" font-size="13" font-family="sans-serif" fill="#4f5e74">SHA '+pin[:12]+'; 12 source entry files; direct absolute import prefixes only.</text>',
       '<text x="24" y="92" font-size="12" font-family="sans-serif" fill="#a34b31">Dynamic imports, relative imports, module aliases, State/event and runtime injection are NOT captured.</text>']
    for j,g in enumerate(groups):
        p.append(f'<text transform="translate({x0+j*cw+cw/2},139) rotate(-41)" font-family="sans-serif" font-size="11" fill="#334155">{html.escape(g)}</text>')
    for i,name in enumerate(roots):
        y=y0+i*rh
        p.append(f'<text x="{x0-8}" y="{y+18}" text-anchor="end" font-family="monospace" font-size="11" fill="#26344a">{html.escape(name)}</text>')
        for j,n in enumerate(rows[i]):
            color='#edf1f5' if n==0 else '#85afd8'
            p.append(f'<rect x="{x0+j*cw+2}" y="{y}" width="{cw-5}" height="{rh-3}" rx="4" fill="{color}" />')
            if n:
                p.append(f'<text x="{x0+j*cw+cw/2}" y="{y+19}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#14243b">{n}</text>')
    p.extend(['<text x="24" y="575" font-family="sans-serif" font-size="11" fill="#4b5563">Cell counts distinct import module targets by group. See import_sample.json for complete verified input paths.</text>','</svg>'])
    Path(argv[2]).parent.mkdir(parents=True,exist_ok=True)
    Path(argv[2]).write_text('\n'.join(p)+'\n',encoding='utf-8')
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
