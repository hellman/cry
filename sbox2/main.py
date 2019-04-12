#-*- coding:utf-8 -*-

from .base import sbox_mixin

from collections import defaultdict, Counter

from cryptools.sagestuff import Integer
from cryptools.binary import frombin


@sbox_mixin
class Main(object):
    def __init__(self, sbox, n=None):
        s = tuple(map(Integer, sbox))
        n = n or max(y.nbits() for y in s)
        super(Main, self).__init__(s, n=n)
        self.n = n
        self.in_bits = self.m
        self.out_bits = self.n

    def in_range(self):
        return xrange(1 << self.in_bits)

    def out_range(self):
        return xrange(1 << self.out_bits)

    def graph(self):
        return enumerate(self)

    def __len__(self):
        return (1 << self.m)

    def resize(self, n):
        mask = (1 << n) - 1
        return self.new((y & mask for y in self), n=n)

    # todo: remove as ambiguous
    @property
    def insize(self):
        return (1 << self.m)

    @property
    def outsize(self):
        return (1 << self.n)

    def as_hex_str(self, format="", sep=""):
        numhex = (self.n + 3)/ 4
        hexformat = "%0" + str(numhex) + "x"
        return sep.join(format % (hexformat % y) for y in self)

    def __eq__(self, other):
        if isinstance(other, self.base):
            return (self.n, self._S) == (other.n, other._S)
        return tuple(self._S) == tuple(other)

    def __hash__(self):
        """
        Warning: does not match hash of the tuple, so will not match tuple in a set or dict
        """
        return hash((self.n, tuple(self._S)))

    def get(self, index):
        return self.base.__getitem__(self, index)

    def __getitem__(self, index):
        if isinstance(index, int) or isinstance(index, Integer):
            return self.get(index)
        if isinstance(index, slice):
            return self.new( [self.get(index) for index in xrange(*index.indices(self.insize))], n=self.n )
        if isinstance(index, tuple) or isinstance(index, list):
            # binary vector (msb to lsb)
            # not sure if confusing, maybe remove this API
            assert len(index) == self.m
            assert 0 <= min(index) <= max(index) <= 1
            return self.get(frombin(index))
        raise ValueError("evaluate at what?", type(index), `index`)


def test_main():
    from cryptools.sbox2 import SBox2
    s = SBox2([3, 4, 7, 2, 1, 1, 6, 6], n=4)

    assert s.in_bits == 3
    assert s.out_bits == 4
    assert len(s) == 8

    assert list(s.in_range()) == range(8)
    assert list(s.out_range()) == range(16)

    assert list(s.graph()) ==  [(0, 3), (1, 4), (2, 7), (3, 2), (4, 1), (5, 1), (6, 6), (7, 6)]

    assert s.as_hex_str(format="%sh", sep=":") == "3h:4h:7h:2h:1h:1h:6h:6h"
    assert s.as_hex_str(format="%s", sep="") == "34721166"

    ss = SBox2([3, 4, 7, 2, 1, 1, 6, 6])
    assert s != ss
    assert s == ss.resize(4)
    assert s.resize(2) == (3, 0, 3, 2, 1, 1, 2, 2)
    ss = SBox2([3, 4, 7, 2, 1, 1, 6, 6], 4)
    assert s == ss
    ss = SBox2([3L, 4, 7, 2, 1, 1, 6, 6], 4)
    assert s == ss
    ss = SBox2([2, 4, 7, 2, 1, 1, 6, 6], 4)
    assert s != ss
    assert s == [3, 4, 7, 2, 1, 1, 6, 6]
    assert s == (3, 4, 7, 2, 1, 1, 6, 6)
    assert s == (3L, 4, 7, 2, 1, 1, 6, 6)
    assert s != (2, 4, 7, 2, 1, 1, 6, 6)

    assert hash(s) != 0

    assert s ^ 1 == s ^ 1L == s ^ Integer(1) == s ^ SBox2([1]*8, n=4) == (2, 5, 6, 3, 0, 0, 7, 7)
    assert s ^ s == [0] * 8

    assert s.get(0) == s[0] == s(0) == s[0,0,0] == 3
    assert s.get(3) == s[3] == s(3) == s[0,1,1] == 2
    assert s.get(7) == s[7] == s(7) == s[1,1,1] == 6
    assert s[1:3] == (4, 7)
    assert s[-3:] == (1, 6, 6)
