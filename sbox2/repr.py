from .base import sbox_mixin

from cryptools.sagestuff import matrix, GF
from cryptools.binary import tobin


@sbox_mixin
class Repr(object):
    def as_table(self, h, w=None):
        if w is None:
            assert 2**self.m % h == 0
            w = 2**self.m // h
        else:
            assert h * w == 2**self.m
        m = matrix(h, w)
        for x in xrange(self.insize):
            m[divmod(x, w)] = self[x]
        return m

    def as_matrix(self):
        assert self.is_linear()

        m = matrix(GF(2), self.n, self.m)
        for e in xrange(self.m):
            x = 1 << e
            m.set_column(self.m - 1 - e, tobin(self[x], self.n))
        return m
