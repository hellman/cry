#-*- coding:utf-8 -*-

from itertools import product

from cryptools.binary import tobin

from .base import sbox_mixin

@sbox_mixin
class Compose(object):
    def compose1(self, other):
        if not isinstance(other, self.cls):
            other = self.new(other)
        assert self.in_bits == other.out_bits
        return self.new((self[y] for x, y in other.graph()), n=self.n)

    def compose(self, *sboxes):
        return self.compose1(reduce(lambda s, o: s.compose1(o), sboxes))

    def power(self, n):
        if n == 0:
            return self.gen.identity(self.m)
        res = self if n & 1 else self.gen.identity(self.m)
        a = self
        while n > 1:
            n >>= 1
            a = a.compose1(a)
            if n & 1:
                res = res.compose1(a)
        return res

    def __mul__(self, other):
        return self.compose1(other)

    def __pow__(self, e):
        return self.power(e)
