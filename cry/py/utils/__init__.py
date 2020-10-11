import sys
import time
from .cache import *


class IntervalCheck(object):
    def __init__(self, interval, total=None):
        self.start_time = self.last_hit = time.time()
        self.total = total
        self.itr = 0

        self.last_hit = time.time()
        self.interval = float(interval)
        assert self.interval > 0

    def touch(self):
        self.last_hit = time.time()

    def check(self):
        self.itr += 1

        t = time.time()
        if t - self.last_hit >= self.interval:
            self.last_hit = t
            return True

    def check_print(self, itr=None, total=None):
        if not self.check():
            return

        elapsed = time.time() - self.start_time
        if self.total is None:
            print >>sys.stderr, "#%d/?. Elapsed: %ds (%.2f hours)." % (self.itr, elapsed, elapsed / 3600.0)
        else:
            remaining = elapsed * (self.total * 1.0 / self.itr - 1)
            perc = (self.itr * 100.0 / self.total)
            print >>sys.stderr, "#%d/%d (%.2f%%)." % (self.itr, self.total, perc),
            print >>sys.stderr, "Elapsed: %ds (%.2f hours);" % (elapsed, elapsed / 3600.0),
            print >>sys.stderr, "remaining: %ds (%.2f hours)" % (remaining, remaining / 3600.0),
            print >>sys.stderr
        return True


def tmap(*a, **k):
    return tuple(map(*a, **k))


def isiterable(s):
    try:
        list(s)
        return True
    except TypeError:
        return False


from itertools import product


def ranges(*ns, list=None):
    if list:
        assert not ns
        ns = list
    return product(*[range(n) for n in ns])
