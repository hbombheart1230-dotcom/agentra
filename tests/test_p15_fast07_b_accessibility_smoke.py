"""Integrated HTML structure and stylesheet smoke, not a pixel/viewport certification."""
from html.parser import HTMLParser
from pathlib import Path
import socket
import subprocess

import pytest
from test_p15_fast07_b_overview_render_smoke import render, overview, ROOT
from test_p15_fast07_b_detail_render_smoke import run_detail


class Markup(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.ids=[]; self.links=[]; self.tags=[]; self.errors=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs); self.tags.append((tag,attrs))
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='a':self.links.append(attrs.get('href',''))
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(tag)
    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1]!=tag:self.errors.append((tag,list(self.stack)))
        else:self.stack.pop()


@pytest.mark.parametrize('template, data', [
    ('overview.html', {'overview':overview()}),
    ('runs.html', {'runs':[], 'limit':50, 'activity_view':'all','mismatch_only':False}),
    ('run_detail.html', {'detail':run_detail()}),
    ('trade_report_detail.html', {'report':{'raw_report':{}}}),
    ('operator_brief_detail.html', {'brief':{'sections':{},'raw_brief':{}}}),
])
def test_all_pages_have_balanced_html_keyboard_targets_and_no_controls(template, data, monkeypatch):
    # The templates must not call runtime loaders, network or spawn an order process.
    def forbidden(*a,**kw):raise AssertionError('render attempted external effect')
    with monkeypatch.context() as m:
        m.setattr(socket.socket,'connect',forbidden);m.setattr(subprocess,'Popen',forbidden)
        text=render(template,**data)
    markup=Markup();markup.feed(text)
    assert not markup.errors and not markup.stack
    assert len(markup.ids)==len(set(markup.ids))
    for link in markup.links:
        if link.startswith('#'):assert link[1:] in markup.ids
        assert not link.lower().startswith('javascript:')
    assert sum(tag=='main' for tag,_ in markup.tags)==1
    assert not any(tag in {'form','button','script'} for tag,_ in markup.tags)
    assert 'No order, approval or execution controls' in text


def test_runs_table_is_scrollable_region_with_column_scope():
    text=render('runs.html',runs=[],limit=50,activity_view='all',mismatch_only=False)
    markup=Markup();markup.feed(text)
    assert any(tag=='section' and a.get('role')=='region' and a.get('tabindex')=='0' and a.get('aria-label') for tag,a in markup.tags)
    assert sum(tag=='th' and a.get('scope')=='col' for tag,a in markup.tags)==15
    assert any(tag=='caption' for tag,a in markup.tags)


def test_responsive_rules_neutral_tones_and_keyboard_focus_present():
    css=(ROOT/'apps/operator_ui/static/operator.css').read_text(encoding='utf-8')
    assert css.count('{')==css.count('}')
    for feature in ['max-width: 900px','max-width: 640px','min-width: 0',':focus-visible',
                    '.skip-link:focus','overflow-wrap: anywhere','prefers-reduced-motion','status-badge--neutral']:
        assert feature in css
    # Explicit text-color/background pairs exceed WCAG AA normal-text contrast.
    def luminance(hexcolor):
        c=[int(hexcolor[i:i+2],16)/255 for i in (0,2,4)]
        c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]
        return sum(v*w for v,w in zip(c,[.2126,.7152,.0722]))
    for bg,fg in [('edf0f4','334155'),('e6f4ea','14532d'),('fff3cd','713f12'),('fee2e2','7f1d1d')]:
        assert '#'+bg in css and '#'+fg in css
        assert (luminance(bg)+.05)/(luminance(fg)+.05)>=4.5
