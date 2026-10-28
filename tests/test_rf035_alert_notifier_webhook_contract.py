"""RF-035 libs/reporting/alert_notifier: the only external-publish path, verified with a FAKE ``urlopen``.

``urllib_request.urlopen`` and ``time.sleep`` are replaced in the module namespace, so no socket is ever
opened and no webhook receives anything; state files live under tmp_path. Complements
tests/test_m25_6_alert_notification_adapter.py (measured 79% before). Explicit raises keep the checks
live under ``python -O``.
"""
from __future__ import annotations

import io
import json
import urllib.error

import pytest

from libs.reporting import alert_notifier as an


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


class _Resp:
    def __init__(self, code):
        self.status = code

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def getcode(self):
        return self.status


@pytest.fixture()
def net(monkeypatch):
    log = {"calls": [], "sleeps": [], "script": []}

    def fake_urlopen(req, timeout):
        log["calls"].append({"url": req.full_url, "method": req.get_method(), "timeout": timeout, "body": json.loads(req.data.decode("utf-8")),
                             "ct": req.get_header("Content-type")})
        step = log["script"].pop(0) if log["script"] else 200
        if isinstance(step, Exception):
            raise step
        return _Resp(step)

    monkeypatch.setattr(an.urllib_request, "urlopen", fake_urlopen)
    monkeypatch.setattr(an.time, "sleep", log["sleeps"].append)
    return log


def _http_error(code):
    return urllib.error.HTTPError("http://x", code, "err", {}, io.BytesIO(b""))


def test_missing_url_and_dry_run_never_touch_the_network(net):
    r = an.send_webhook_json(webhook_url="  ", payload={"a": 1})
    _eq((r.ok, r.sent, r.skipped, r.reason), (False, False, True, "missing_webhook_url"))
    d = an.send_webhook_json(webhook_url="http://hook", payload={"a": 1}, dry_run=True)
    _eq((d.ok, d.sent, d.skipped, d.reason), (True, False, True, "dry_run"))
    _eq(net["calls"], [])


def test_success_posts_json_and_classifies_status_codes(net):
    r = an.send_webhook_json(webhook_url=" http://hook ", payload={"k": "한글"}, timeout_sec=0)
    _eq((r.ok, r.sent, r.reason, r.status_code), (True, True, "sent", 200))
    c = net["calls"][0]
    _eq((c["url"], c["method"], c["body"], c["timeout"], c["ct"]), ("http://hook", "POST", {"k": "한글"}, 1, "application/json; charset=utf-8"))   # timeout floors at 1
    net["script"][:] = [204]
    _eq(an.send_webhook_json(webhook_url="http://h", payload={}).reason, "sent")
    net["script"][:] = [302]
    r3 = an.send_webhook_json(webhook_url="http://h", payload={})
    _eq((r3.ok, r3.sent, r3.reason, r3.status_code), (False, True, "non_2xx", 302))      # non-2xx is reported, never retried


def test_retryable_http_errors_retry_with_linear_backoff_then_succeed(net):
    net["script"][:] = [_http_error(503), _http_error(429), 200]
    r = an.send_webhook_json(webhook_url="http://h", payload={}, retry_max=3, retry_backoff_sec=0.5)
    _eq((r.ok, r.reason, r.status_code, len(net["calls"]), net["sleeps"]), (True, "sent_after_retry", 200, 3, [0.5, 1.0]))


def test_non_retryable_http_error_and_exhausted_retries_report_http_error(net):
    net["script"][:] = [_http_error(404)]
    r = an.send_webhook_json(webhook_url="http://h", payload={}, retry_max=5)
    _eq((r.ok, r.sent, r.reason, r.status_code, len(net["calls"]), net["sleeps"]), (False, True, "http_error", 404, 1, []))
    net["calls"].clear()
    net["script"][:] = [_http_error(500)] * 3
    r2 = an.send_webhook_json(webhook_url="http://h", payload={}, retry_max=2, retry_backoff_sec=0.0)
    _eq((r2.reason, r2.status_code, len(net["calls"]), net["sleeps"]), ("http_error", 500, 3, []))                 # backoff 0 -> no sleep
    if "500" not in r2.error:
        raise AssertionError(r2.error)


def test_generic_exceptions_retry_then_report_send_error(net):
    net["script"][:] = [TimeoutError("slow"), ConnectionError("reset"), TimeoutError("slow again")]
    r = an.send_webhook_json(webhook_url="http://h", payload={}, retry_max=2, retry_backoff_sec=0.25)
    _eq((r.ok, r.sent, r.reason, r.status_code, r.error, len(net["calls"]), net["sleeps"]), (False, True, "send_error", 0, "slow again", 3, [0.25, 0.5]))
    net["calls"].clear()
    net["script"][:] = [OSError("down")]
    r1 = an.send_webhook_json(webhook_url="http://h", payload={})            # retry_max defaults to 0 -> a single attempt
    _eq((r1.reason, len(net["calls"])), ("send_error", 1))


def test_negative_or_garbage_retry_settings_fall_back_to_single_attempt(net):
    net["script"][:] = [OSError("x")]
    an.send_webhook_json(webhook_url="http://h", payload={}, retry_max=-4, retry_backoff_sec="bad")
    _eq(len(net["calls"]), 1)


def test_state_file_helpers_roundtrip_prune_and_tolerate_garbage(tmp_path):
    p = tmp_path / "sub" / "state.json"
    _eq(an._load_notify_state(p), [])
    an._save_notify_state(p, [{"ts": 100, "key": "a"}, {"ts": 200, "key": "b"}])
    _eq(an._load_notify_state(p), [{"ts": 100, "key": "a"}, {"ts": 200, "key": "b"}])
    p.write_text(json.dumps({"events": [{"ts": 0, "key": "z"}, {"ts": 5, "key": ""}, "junk", {"ts": "7", "key": "ok"}]}), encoding="utf-8")
    _eq(an._load_notify_state(p), [{"ts": 7, "key": "ok"}])                      # invalid rows dropped, numeric strings accepted
    p.write_text("{bad", encoding="utf-8")
    _eq(an._load_notify_state(p), [])
    p.write_text(json.dumps({"events": "no"}), encoding="utf-8")
    _eq(an._load_notify_state(p), [])
    ev = [{"ts": 10, "key": "a"}, {"ts": 90, "key": "b"}]
    _eq(an._prune_events(ev, now_epoch=100, keep_window_sec=20), [{"ts": 90, "key": "b"}])
    _eq(len(an._prune_events([{"ts": i, "key": "k"} for i in range(300)], now_epoch=1000, keep_window_sec=0)), 200)   # bounded when no window


def test_suppression_reason_dedup_then_rate_limit_then_none():
    ev = [{"ts": 950, "key": "k"}, {"ts": 960, "key": "other"}, {"ts": 970, "key": "other2"}]
    kw = dict(events=ev, now_epoch=1000, dedup_window_sec=100, rate_limit_window_sec=100, max_per_window=3)
    _eq(an._suppression_reason(dedup_key="k", **kw), "dedup_suppressed")                       # dedup wins over rate limit
    _eq(an._suppression_reason(dedup_key="fresh", **kw), "rate_limited")                        # 3 events in window >= 3
    _eq(an._suppression_reason(dedup_key="fresh", **{**kw, "max_per_window": 4}), "")
    _eq(an._suppression_reason(dedup_key="k", **{**kw, "dedup_window_sec": 0, "max_per_window": 0}), "")           # both guards disabled
    _eq(an._suppression_reason(dedup_key="k", **{**kw, "now_epoch": 5000}), "")                  # old events fall out of both windows


def test_retryable_status_set():
    _eq([an._is_retryable_http_status(c) for c in (200, 400, 404, 429, 499, 500, 503, 599, 600, 0, None)],
        [False, False, False, True, False, True, True, True, False, False, False])


def test_provider_none_and_notify_on_gate_never_send(net, tmp_path):
    batch = {"ok": False}
    r = an.notify_batch_result(batch_result=batch, provider="none")
    _eq((r["sent"], r["skipped"], r["reason"]), (False, True, "provider_none"))
    ok_batch = an.notify_batch_result(batch_result={"ok": True}, provider="webhook", webhook_url="http://h", notify_on="failure")
    _eq((ok_batch["sent"], ok_batch["reason"]), (False, "notify_on_failure_skip"))
    fail_skip = an.notify_batch_result(batch_result={"ok": False}, provider="webhook", webhook_url="http://h", notify_on="success")
    _eq((fail_skip["sent"], fail_skip["reason"]), (False, "notify_on_success_skip"))
    garbage_trigger = an.notify_batch_result(batch_result={"ok": True}, provider="webhook", webhook_url="http://h", notify_on="weird")
    _eq(garbage_trigger["reason"], "notify_on_failure_skip")                                      # unknown trigger falls back to "failure"
    _eq(net["calls"], [])


def test_end_to_end_dedup_state_dry_run_unsupported_provider_and_slack_payload(net, tmp_path):
    st = tmp_path / "notify" / "state.json"
    batch = {"ok": False}
    first = an.notify_batch_result(batch_result=batch, provider="webhook", webhook_url="http://h", state_path=str(st), notify_on="always")
    _eq((first["sent"], first["reason"], first["status_code"]), (True, "sent", 200))
    _eq(len(net["calls"]), 1)
    events = json.loads(st.read_text(encoding="utf-8"))["events"]
    _eq(len(events), 1)                                                                   # a send is recorded
    again = an.notify_batch_result(batch_result=batch, provider="webhook", webhook_url="http://h", state_path=str(st), notify_on="always")
    _eq((again["sent"], again["skipped"], again["reason"]), (False, True, "dedup_suppressed"))
    _eq(len(net["calls"]), 1)                                                             # suppressed: no second POST
    # a dry run is never recorded in the state file, so it never suppresses a later real send
    st2 = tmp_path / "notify" / "state2.json"
    dry = an.notify_batch_result(batch_result=batch, provider="webhook", webhook_url="http://h", state_path=str(st2), dry_run=True, notify_on="always")
    _eq((dry["sent"], dry["reason"]), (False, "dry_run"))
    _eq(st2.exists(), False)
    # a failed send (non-2xx) still counts as sent=True and is recorded
    st3 = tmp_path / "notify" / "state3.json"
    net["script"][:] = [500]
    bad = an.notify_batch_result(batch_result=batch, provider="webhook", webhook_url="http://h", state_path=str(st3), notify_on="always")
    _eq((bad["ok"], bad["sent"], bad["reason"]), (False, True, "non_2xx"))
    _eq(len(json.loads(st3.read_text(encoding="utf-8"))["events"]), 1)
    # without a state path nothing is persisted and nothing is suppressed
    n_before = len(net["calls"])
    an.notify_batch_result(batch_result=batch, provider="webhook", webhook_url="http://h", notify_on="always")
    an.notify_batch_result(batch_result=batch, provider="webhook", webhook_url="http://h", notify_on="always")
    _eq(len(net["calls"]) - n_before, 2)
    # slack_webhook sends the slack-shaped body, webhook the raw batch payload
    net["calls"].clear()
    an.notify_batch_result(batch_result=batch, provider="slack_webhook", webhook_url="http://h", notify_on="always")
    an.notify_batch_result(batch_result=batch, provider="webhook", webhook_url="http://h", notify_on="always")
    slack_body, raw_body = net["calls"][0]["body"], net["calls"][1]["body"]
    _eq(slack_body != raw_body, True)
    _eq(slack_body, an.build_slack_webhook_payload(an.build_batch_notification_payload(batch)))
    _eq(raw_body, an.build_batch_notification_payload(batch))
    # unknown providers are rejected without any network call
    net["calls"].clear()
    u = an.notify_batch_result(batch_result=batch, provider="telegram", webhook_url="http://h", notify_on="always")
    _eq((u["ok"], u["sent"], u["reason"]), (False, False, "unsupported_provider"))
    _eq(net["calls"], [])
