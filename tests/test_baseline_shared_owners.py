"""WO02 shared baseline ownership; only synthetic state and stub freshness calls."""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from libs.reporting import baseline_artifact_io as io
from libs.reporting import baseline_candle_reader as owner
from libs.reporting.baseline_samsung_hynix import data_provider as q10
from libs.reporting.baseline_btc_woori_tech import data_provider as q12

DAY = '2026-06-24'
KEYS = ('recent_minute_ohlcv_by_symbol', 'minute_ohlcv_by_symbol',
        'monitor_minute_ohlcv_by_symbol', 'intraday_ohlcv_by_symbol', 'ohlcv_by_symbol')


def row(ts=1782262800, price=100):
    return {'ts': ts, 'raw_ts': '20260624100000', 'close': price}


@pytest.fixture(autouse=True)
def no_live_freshness(monkeypatch):
    calls = []
    def forbidden(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError('unconfigured external freshness call')
    monkeypatch.setattr('libs.reporting.post_exit_shadow_recap.fetch_fresh_minute_rows_for_symbol', forbidden)
    yield
    assert calls == []


@pytest.mark.parametrize('key', KEYS)
def test_state_priority_defaults_sort_and_strategy_isolation(tmp_path, key):
    path = tmp_path / 'state.json'
    index = KEYS.index(key)
    payload = {k: {} for k in KEYS[:index]}
    payload[key] = {'005930': [row(1782262860, 20), row(price=10), None,
        {'ts': -1, 'close': 2}, {'ts': 1782262800, 'close': 0},
        {'ts': 1782262800, 'raw_ts': '20260623100000', 'close': 999}],
        q12.TARGET_SYMBOL: {'rows': [row(price=30)]}}
    for k in KEYS[index + 1:]: payload[k] = {'005930': [row(price=999)]}
    path.write_text(json.dumps(payload), encoding='utf-8')
    result = q10.load_existing_candles(state_path=path, day=DAY,
                                      symbols=('005930',), allow_fresh_fetch=False)
    assert [r['close'] for r in result['005930']] == [10, 20]
    assert result['005930'][0]['open'] == result['005930'][0]['high'] == result['005930'][0]['low'] == 10
    assert result['005930'][0]['volume'] == 0.0
    assert q12.load_woori_candles(day=DAY, state_path=path, allow_fresh_fetch=False)[0]['close'] == 30
    assert set(result) == {'005930'}


@pytest.mark.parametrize('mode', ['empty', 'error', 'older', 'newer', 'tie_more', 'all_error'])
@pytest.mark.parametrize('loader', [owner.load_existing_candles, q10.load_existing_candles])
def test_freshness_attempts_selection_and_run_prefix(tmp_path, monkeypatch, mode, loader):
    path = tmp_path / 'state.json'
    path.write_text(json.dumps({KEYS[0]: {'FAKE': [row()]}}), encoding='utf-8')
    calls = []
    def fetch(symbol, *, run_id):
        calls.append((symbol, run_id))
        if mode == 'all_error' or (mode == 'error' and len(calls) == 1): raise RuntimeError('fixture only')
        if mode == 'empty' and len(calls) == 1: return [], {}
        if mode == 'older': return [row(1782262740, 20)], {}
        if mode == 'tie_more': return [row(1782262740, 20), row(price=30)], {}
        return [row(1782262860, 40)], {}
    monkeypatch.setattr('libs.reporting.post_exit_shadow_recap.fetch_fresh_minute_rows_for_symbol', fetch)
    result = loader(state_path=path, day=DAY, symbols=('FAKE',), run_id_prefix='custom')
    attempts = 2 if mode in ('empty', 'error', 'all_error') else 1
    assert calls == [('FAKE', f'custom_{DAY}_FAKE_{i}') for i in range(1, attempts + 1)]
    assert result['FAKE'][-1]['close'] == (100 if mode in ('older', 'all_error') else 30 if mode == 'tie_more' else 40)


@pytest.mark.parametrize('contents', [None, '', 'not-json', '[]'])
def test_missing_or_invalid_state_never_fetches(tmp_path, monkeypatch, contents):
    path = tmp_path / 'state.json'
    if contents is not None: path.write_text(contents, encoding='utf-8')
    calls = []
    monkeypatch.setattr('libs.reporting.post_exit_shadow_recap.fetch_fresh_minute_rows_for_symbol', lambda *a, **kw: calls.append(kw))
    assert q10.load_existing_candles(state_path=path, day=DAY, symbols=('FAKE',)) == {'FAKE': []}
    assert calls == []


def test_facade_number_monkeypatch_is_live_but_does_not_leak_to_q12(tmp_path, monkeypatch):
    path = tmp_path / 'state.json'
    path.write_text(json.dumps({KEYS[0]: {q12.TARGET_SYMBOL: [row()]}}), encoding='utf-8')
    original = q10._number
    monkeypatch.setattr(q10, '_number', lambda value: 123.0 if value == 100 else original(value))
    assert q10.load_existing_candles(state_path=path, day=DAY, symbols=(q12.TARGET_SYMBOL,), allow_fresh_fetch=False)[q12.TARGET_SYMBOL][0]['close'] == 123
    assert q12.load_woori_candles(state_path=path, day=DAY, allow_fresh_fetch=False)[0]['close'] == 100


def test_facade_normalizer_monkeypatch_used_for_state_and_fresh(tmp_path, monkeypatch):
    path = tmp_path / 'state.json'
    path.write_text(json.dumps({KEYS[0]: {'FAKE': [row()]}}), encoding='utf-8')
    calls = []
    original = q10._normalize_rows
    def normalize(value, *, day=''):
        calls.append(value)
        return original(value, day=day)
    monkeypatch.setattr(q10, '_normalize_rows', normalize)
    monkeypatch.setattr('libs.reporting.post_exit_shadow_recap.fetch_fresh_minute_rows_for_symbol',
                        lambda *a, **kw: ([row(1782262860)], {}))
    q10.load_existing_candles(state_path=path, day=DAY, symbols=('FAKE',))
    assert len(calls) == 2


def test_q12_local_loader_binding_remains_patchable(monkeypatch):
    calls = []
    def fake(**kwargs):
        calls.append(kwargs)
        return {q12.TARGET_SYMBOL: [{'fake': True}]}
    monkeypatch.setattr(q12, 'load_existing_candles', fake)
    assert q12.load_woori_candles(day=DAY, allow_fresh_fetch=False) == [{'fake': True}]
    assert calls[0]['run_id_prefix'] == 'baseline_btc_woori_tech'
    assert calls[0]['symbols'] == (q12.TARGET_SYMBOL,)
    assert calls[0]['allow_fresh_fetch'] is False


@pytest.mark.parametrize('package', ['baseline_samsung_hynix', 'baseline_btc_woori_tech'])
def test_pipeline_io_facades_preserve_bytes_and_error_contract(tmp_path, package):
    pipeline = importlib.import_module('libs.reporting.' + package + '.pipeline')
    path = tmp_path / 'nested/한글.json'
    payload = {'name': '한글', 'rows': [1, {'value': None}]}
    assert pipeline._read(path) == {}
    assert pipeline._write(path, payload) is None
    assert path.read_bytes() == (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    assert pipeline._read(path) == payload == io.read_json_dict(path)
    for invalid in ('', 'broken', '[]', '123', '"string"'):
        path.write_text(invalid, encoding='utf-8')
        assert pipeline._read(path) == {}
