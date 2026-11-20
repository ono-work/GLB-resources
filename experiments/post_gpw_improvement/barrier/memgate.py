"""Memory gate for concurrent producer / verifier processes on Captain (48 GB).

Before a heavy binary starts, the caller reserves its projected peak (bytes).  A reservation is granted only while
the sum of live reservations + the request <= BUDGET; otherwise the caller waits.  Reservations are files
<DIR>/<pid>.<n> holding the byte count; files of dead processes are ignored/removed.  The check+write is done under
an exclusive flock, so two processes cannot both pass on the same free budget.
"""
import os, time, fcntl, contextlib
from pathlib import Path
DIR = Path(os.environ.get("GLB_MEMGATE_DIR", "/tmp/glb_memgate"))
BUDGET = int(float(os.environ.get("GLB_MEM_BUDGET_GIB", "38")) * 2 ** 30)


def _alive(pid):
    try: os.kill(pid, 0); return True
    except OSError: return False


def _live():
    tot = 0
    for f in DIR.glob("*.res"):
        pid = int(f.name.split(".")[0])
        if not _alive(pid): f.unlink(missing_ok=True); continue
        try: tot += int(f.read_text())
        except ValueError: pass
    return tot


@contextlib.contextmanager
def reserve(nbytes, label="", log=None):
    DIR.mkdir(exist_ok=True)
    nbytes = int(nbytes)
    if nbytes > BUDGET: raise MemoryError(f"projected peak {nbytes/2**30:.1f} GiB exceeds budget {BUDGET/2**30:.0f} GiB ({label})")
    me = DIR / f"{os.getpid()}.{time.time_ns()}.res"
    t0, said = time.time(), False
    while True:
        with open(DIR / "lock", "w") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            if _live() + nbytes <= BUDGET:
                me.write_text(str(nbytes)); break
        if log and not said:
            print(f"   [memgate] waiting: need {nbytes/2**30:.1f} GiB ({label})", file=log, flush=True); said = True
        time.sleep(20)
    if log and said: print(f"   [memgate] granted after {time.time()-t0:.0f}s", file=log, flush=True)
    try: yield
    finally: me.unlink(missing_ok=True)
