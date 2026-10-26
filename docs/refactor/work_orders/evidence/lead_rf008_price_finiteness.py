"""RF-008 adjacent RF-012 price-finiteness contract; exact Git blob, no real imports/IO.
Run from repository root: python docs/refactor/work_orders/evidence/lead_rf008_price_finiteness.py
Also run: python -O docs/refactor/work_orders/evidence/lead_rf008_price_finiteness.py
Optional AGENTRA_RF008_SOURCE points to an exact byte-identical detached copy.
"""
import hashlib
import importlib.util
import json
import math
import os
import pathlib
import sys
import types

sys.dont_write_bytecode = True
source = pathlib.Path(os.environ.get("AGENTRA_RF008_SOURCE", "graphs/nodes/build_market_snapshot.py"))
raw = source.read_bytes()
sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
if sha != "af11f9d64d6fa1965beb9f4140e2ce372aa1ce46":
    raise SystemExit("SOURCE_BLOB_MISMATCH:" + sha)

class Snapshot:
    def __init__(self, symbol, price): self.symbol, self.price = symbol, price
    def to_dict(self): return {"symbol": self.symbol, "price": self.price}
class MockPriceReader:
    def __init__(self, prices, default_price): self.prices, self.default_price = prices, default_price
    def get_market_snapshot(self, symbol): return Snapshot(symbol, self.prices.get(symbol, self.default_price))
class ForbiddenKiwoom:
    @classmethod
    def from_env(cls): raise SystemExit("SAFETY_VIOLATION: real Kiwoom reader construction")
for name in ("libs", "libs.read", "libs.read.price_reader", "libs.read.kiwoom_price_reader"):
    sys.modules[name] = types.ModuleType(name)
sys.modules["libs.read.price_reader"].PriceReader = object
sys.modules["libs.read.price_reader"].MockPriceReader = MockPriceReader
sys.modules["libs.read.kiwoom_price_reader"].KiwoomPriceReader = ForbiddenKiwoom
spec = importlib.util.spec_from_file_location("rf008_exact_source", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
class Fixed:
    def __init__(self, price): self.price = price
    def get_market_snapshot(self, symbol): return Snapshot(symbol, self.price)
class Fails:
    def get_market_snapshot(self, symbol): raise TimeoutError("synthetic offline")
def check(condition, label):
    if not condition: raise SystemExit("CHECK_FAILED:" + label)
def run(mode, price=None, fail=False, fallback=None, persisted=None):
    os.environ["KIWOOM_MODE"] = mode
    if fallback is None: os.environ.pop("MOCK_PRICE_FALLBACK", None)
    else: os.environ["MOCK_PRICE_FALLBACK"] = fallback
    state = {"symbol": "005930", "price_reader": Fails() if fail else Fixed(price)}
    if persisted is not None: state["persisted_state"] = {"last_market_price": persisted}
    result = module.build_market_snapshot(state)
    check(result is state, "state_identity")
    return result["market_snapshot"]["price"], result["market_snapshot_health"], result.get("persisted_state", {}).get("last_market_price")

rows = []
for mode, price in (("mock", float("nan")), ("mock", float("inf")), ("paper", float("nan")), ("real", float("inf")), ("paper", -1.0)):
    observed, health, persisted = run(mode, price)
    check(math.isnan(observed) if math.isnan(price) else observed == price, "pass_through_" + mode)
    check(health["reader_ok"] and not health["fallback_applied"], "health_" + mode)
    rows.append([mode, str(price), "pass_through"])
observed, health, _ = run("mock", fail=True, fallback="nan")
check(math.isnan(observed) and health["fallback_applied"], "mock_fallback_nan")
rows.append(["mock", "fallback_nan", "accepted"])
observed, health, persisted = run("mock", fail=True, persisted=float("inf"))
check(math.isinf(observed) and math.isinf(persisted), "persisted_inf")
rows.append(["mock", "persisted_inf", "accepted"])
observed, health, _ = run("mock", -1.0)
check(observed == 70000.0 and health["fallback_applied"], "mock_negative_fallback")
rows.append(["mock", "negative", "fallback_70000"])
print("RF008_FINITE_PRICE_LEAD_OBSERVED cases=8 source_sha=" + sha)
print(json.dumps(rows, ensure_ascii=False))
