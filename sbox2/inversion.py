#-*- coding:utf-8 -*-

from itertools import product
from collections import defaultdict, Counter

from .base import sbox_mixin

from cryptools.sagestuff import Integer


@sbox_mixin
class Inversion(object):
    def image(self):
        return tuple(sorted(set(self)))

    def inverse(self):
        assert self.in_bits == self.out_bits
        table = [None] * len(self)
        for x, y in self.graph():
            table[y] = x
        assert None not in table
        return self.new(table)
    __invert__ = inverse

    def preimage(self, elem):
        return self._S.index(elem)
    index = preimage

    def preimages(self, elem=None):
        if elem is None:
            res = defaultdict(list)
            for x, y in self.graph():
                res[y].append(x)
            return res
        else:
            return tuple(x for x, y in self.graph() if y == elem)

    def preimage_structure(self):
        return Counter(map(len, self.preimages().values()))



def test_inversion():
    from cryptools.sbox2 import SBox2
    s = SBox2([5, 6, 3, 2, 1, 7, 0, 4])

    assert ~s == s.inverse() == [6, 4, 3, 2, 7, 0, 1, 5]

    s = SBox2([3, 4, 7, 2, 1, 1, 6, 6], n=4)
    assert s.image() == (1, 2, 3, 4, 6, 7)
    assert s.preimage(2) == s.index(2) == 3
    assert s.preimage(1) == s.index(1) == 4
    assert s.preimage(6) == s.index(6) == 6
    assert s.preimages(2) == (3,)
    assert s.preimages(1) == (4, 5)
    assert s.preimages(6) == (6, 7)

    assert sorted(s.preimage_structure().items()) == [(1, 4), (2, 2)]
