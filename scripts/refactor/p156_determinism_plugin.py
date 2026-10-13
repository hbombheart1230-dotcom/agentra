"""P1.5 Second Pass parity-evidence harness: deterministic-environment pytest plugin (test/harness only).

Activated ONLY when P156_DETERMINISM=1 (`-p p156_determinism_plugin`). It removes the environment nondeterminism that
made the first differential inconclusive, identically for BASE and FEATURE sessions:

* wall clock: ``time.time/time_ns/monotonic/perf_counter`` and ``datetime.datetime.now/utcnow/today`` return a fixed anchor plus
  a per-call deterministic tick (reset at every test), ``time.sleep`` advances that clock instead of sleeping;
* ``os.getpid`` is constant ONLY while conftest.py/path_isolation derive the session temp root (``<pid>-<hash>`` reaches
  prompt lengths/hashes); the real pid is restored at ``pytest_sessionstart`` so pid-based liveness/lock tests behave;
* ``uuid.uuid4`` returns a per-test deterministic sequence; ``random`` is re-seeded per test;
* network: non-loopback ``socket`` connects / name lookups and the yfinance / curl_cffi / requests client entry points
  raise ``OSError`` (no live market data, no broker, no LLM); callers take their documented offline fallbacks.

Equivalence evidence is therefore also a *call-sequence* check: if the feature tree performed a different number of
clock/uuid calls, the derived values would differ. Nothing here touches production code.
"""
import datetime as _dt
import hashlib
import os
import random
import socket
import sys
import time
import uuid

_ACTIVE = os.environ.get("P156_DETERMINISM") == "1"
ANCHOR_EPOCH = 1772587800.0  # 2026-03-04T01:30:00Z == 10:30 KST on a Wednesday
TICK = 2.0 ** -10  # exactly representable: durations derived from tick differences carry no rounding noise

_state = {"n": 0, "u": 0, "offset": 0.0}
_real = {
    "time": time.time, "time_ns": time.time_ns, "monotonic": time.monotonic, "perf_counter": time.perf_counter,
    "sleep": time.sleep, "uuid4": uuid.uuid4, "connect": socket.socket.connect,
    "create_connection": socket.create_connection, "getaddrinfo": socket.getaddrinfo,
    "datetime": _dt.datetime, "date": _dt.date, "getpid": os.getpid,
}


def _now():
    _state["n"] += 1
    return ANCHOR_EPOCH + _state["offset"] + _state["n"] * TICK


def _reset():
    _state["n"] = 0
    _state["u"] = 0
    _state["offset"] = 0.0
    random.seed(0)


class _FakeDateTime(_real["datetime"]):
    @classmethod
    def now(cls, tz=None):
        return cls.fromtimestamp(_now(), tz)

    @classmethod
    def utcnow(cls):
        return cls.utcfromtimestamp(_now())

    @classmethod
    def today(cls):
        return cls.fromtimestamp(_now())


def _fake_sleep(seconds):
    try:
        _state["offset"] += max(0.0, float(seconds))
    except Exception:
        pass


def _fake_uuid4():
    _state["u"] += 1
    digest = hashlib.sha256(("p156-uuid-%d" % _state["u"]).encode()).digest()[:16]
    return uuid.UUID(bytes=digest, version=4)


def _is_loopback(addr):
    host = addr[0] if isinstance(addr, tuple) and addr else addr
    return str(host) in ("127.0.0.1", "::1", "localhost", "0.0.0.0", "")


def _blocked_connect(self, address, *a, **k):
    if _is_loopback(address):
        return _real["connect"](self, address, *a, **k)
    raise OSError("network disabled by p156_determinism_plugin")


def _blocked_create_connection(address, *a, **k):
    if _is_loopback(address):
        return _real["create_connection"](address, *a, **k)
    raise OSError("network disabled by p156_determinism_plugin")


def _blocked_getaddrinfo(host, *a, **k):
    if _is_loopback((host,)):
        return _real["getaddrinfo"](host, *a, **k)
    raise OSError("name lookup disabled by p156_determinism_plugin")


def _block_http_clients():
    """yfinance 1.x talks through curl_cffi (libcurl), which bypasses python sockets: cut the client entry points."""
    def _deny(*a, **k):
        raise OSError("live market-data fetch disabled by p156_determinism_plugin")

    try:
        import yfinance as yf
        yf.download = _deny
        for cls_name in ("Ticker", "Tickers"):
            cls = getattr(yf, cls_name, None)
            if cls is not None and hasattr(cls, "history"):
                cls.history = _deny
        if hasattr(yf, "Ticker"):
            for attr in ("get_info", "get_news", "get_actions", "get_fast_info"):
                if hasattr(yf.Ticker, attr):
                    setattr(yf.Ticker, attr, _deny)
    except Exception:
        pass
    try:
        from curl_cffi import requests as cr
        for attr in ("request", "get", "post"):
            if hasattr(cr.Session, attr):
                setattr(cr.Session, attr, _deny)
    except Exception:
        pass
    try:
        import requests as rq
        rq.sessions.Session.request = _deny
    except Exception:
        pass


def _install():
    time.time = _now
    time.time_ns = lambda: int(_now() * 1e9)
    time.monotonic = lambda: _now() - ANCHOR_EPOCH
    time.perf_counter = lambda: _now() - ANCHOR_EPOCH
    time.sleep = _fake_sleep
    _dt.datetime = _FakeDateTime  # `date.today()` stays real: C extensions break if `datetime.date` is replaced
    uuid.uuid4 = _fake_uuid4
    os.getpid = lambda: 4242  # only until pytest_sessionstart (see below)
    socket.socket.connect = _blocked_connect
    socket.create_connection = _blocked_create_connection
    socket.getaddrinfo = _blocked_getaddrinfo


def _preimport_c_extensions():
    """numpy/pandas (and libraries built on them) bind the real datetime C types at import; load them BEFORE the
    datetime class is replaced so only project code sees the deterministic subclass."""
    for name in ("numpy", "pandas", "requests", "yfinance"):
        try:
            __import__(name)
        except Exception:
            pass


if _ACTIVE:
    _preimport_c_extensions()
    _block_http_clients()
    _install()  # before any project module is imported (plugins load before collection)
    _reset()


def pytest_sessionstart(session):
    if _ACTIVE:
        os.getpid = _real["getpid"]


def pytest_runtest_protocol(item, nextitem):
    if _ACTIVE:
        _reset()
    return None
