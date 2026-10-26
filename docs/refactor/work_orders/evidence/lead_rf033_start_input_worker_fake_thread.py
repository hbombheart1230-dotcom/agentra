"""RF-033 isolated scheduler function with fake Event/Thread/clock/worker.
Transcribed from libs/reporting/baseline_btc_woori_tech/input_worker.py
Git blob 2184c9ee571411baadc728c71863cfa0af3c3967.
Not a full-module import, real thread, Windows scheduler, or network test.
"""
import sys, io, contextlib
sys.dont_write_bytecode = True


def start_input_worker(*, day, reports_root, state_path):
    stop = threading.Event()
    worker = InputWorker(day, reports_root, state_path)

    def loop():
        while not stop.is_set():
            now = datetime.now(KST)
            if now.date().isoformat() != day or int(now.timestamp()) > epoch(day, '09:12'):
                return
            if int(now.timestamp()) >= epoch(day, '08:50'):
                try:
                    worker.tick(int(now.timestamp()))
                except Exception as exc:
                    # Invalid/missing producer output cannot be masked by an old healthy row.
                    print(f'q12_input_delivery_error={type(exc).__name__}', flush=True)
            stop.wait(15)
    thread = threading.Thread(target=loop, name='q12-opening-input', daemon=True)
    thread.start()
    return stop


count = 0
def check(cond, label):
    global count
    if not cond: raise RuntimeError('FAIL '+label)
    count += 1

class FakeEvent:
    def __init__(self): self.stopped=False; self.waits=[]
    def is_set(self): return self.stopped
    def wait(self, secs): self.waits.append(secs); self.stopped=True

class FakeThread:
    def __init__(self, *, target, name, daemon):
        self.target=target; self.name=name; self.daemon=daemon; self.started=False
    def start(self): self.started=True; self.target()

class FakeThreading:
    Event=FakeEvent
    Thread=FakeThread
threading=FakeThreading

class FakeDay:
    def __init__(self, day): self.day=day
    def isoformat(self): return self.day
class FakeMoment:
    def __init__(self, day, sec): self.day=day; self.sec=sec
    def date(self): return FakeDay(self.day)
    def timestamp(self): return self.sec
class FakeDateTime:
    moment=None
    @classmethod
    def now(cls, zone):
        check(zone is KST,'timezone passed')
        return cls.moment
datetime=FakeDateTime
KST=object()

def epoch(day, time):
    check(day=='2026-10-27','epoch day')
    return {'08:50':1000,'09:12':1100}[time]

class FakeWorker:
    def __init__(self, day, reports_root, state_path):
        self.day=day; self.reports_root=reports_root; self.state_path=state_path; self.calls=[]
    def tick(self, sec):
        self.calls.append(sec)
        if should_raise: raise PermissionError('fake publish failure')
workers=[]
def InputWorker(day, reports_root, state_path):
    w=FakeWorker(day,reports_root,state_path);workers.append(w);return w

should_raise=False

def scenario(now_day,sec,raises=False):
    global should_raise
    should_raise=raises
    datetime.moment=FakeMoment(now_day,sec)
    output=io.StringIO()
    with contextlib.redirect_stdout(output):
        stop=start_input_worker(day='2026-10-27',reports_root='/fake/reports',state_path='/fake/state')
    return stop,workers[-1],output.getvalue()

stop,worker,out=scenario('2026-10-27',999)
check(worker.calls==[],'before 08:50 no tick')
check(stop.waits==[15],'before gate waits 15')
check(out=='','before gate quiet')
stop,worker,out=scenario('2026-10-27',1000)
check(worker.calls==[1000],'08:50 inclusive tick')
check(stop.waits==[15],'at gate waits 15')
check(worker.reports_root=='/fake/reports' and worker.state_path=='/fake/state','constructor args')
stop,worker,out=scenario('2026-10-27',1100)
check(worker.calls==[1100],'09:12 inclusive tick')
check(stop.waits==[15],'09:12 wait')
stop,worker,out=scenario('2026-10-27',1101)
check(worker.calls==[],'09:12+ no tick')
check(stop.waits==[],'09:12+ return no wait')
stop,worker,out=scenario('2026-10-26',1000)
check(worker.calls==[],'other date no tick')
check(stop.waits==[],'other date no wait')
stop,worker,out=scenario('2026-10-27',1050,True)
check(worker.calls==[1050],'failed tick attempted')
check(out=='q12_input_delivery_error=PermissionError\n','exception log')
check(stop.waits==[15],'exception still waits')
check(stop.stopped,'stop returned')
check(len(workers)==6,'one worker per start')
print(f'RF033_START_INPUT_WORKER_FAKE_OK cases={count} real_threads=0 writes=0 network=0 broker=0')
