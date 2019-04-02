#-*- coding:utf-8 -*-

from cryptools.binary import swap_halves
from cryptools.sagestuff import randint, Integer
from cryptools.py.anf import mobius

from .base import sbox_mixin


@sbox_mixin
class Transform(object):
    def swap_halves_input(self):
        assert self.in_bits & 1 == 0
        h = self.in_bits >> 1
        table = [None] * len(self)
        for x, y in self.graph():
            table[swap_halves(x, h)] = y
        return self.new(table)

    def swap_halves_output(self):
        assert self.out_bits & 1 == 0
        h = self.out_bits >> 1
        table = [None] * len(self)
        for x, y in self.graph():
            table[x] = swap_halves(y, h)
        return self.new(table)

    def swap_halves(self):
        return self.swap_halves_input().swap_halves_output()

    def transform(self, func):
        table = [None] * len(self)
        for x, y in self.graph():
            x2, y2 = func(x, y)
            assert table[x2] is None
            table[x2] = y2
        return self.new(table)

    def fix_input_mask(self, mask, value):
        assert value & mask == value
        return self.new(y for x, y in self.graph() if x & mask == value)

    def truncate(self, mask):
        return self.new(squeeze_by_mask(y, mask) for x, y in self.graph())

    def xor(self, inp=0, out=0):
        return self.new([self[x ^ inp] ^ out for x in self.in_range()], n=self.n)

    def __xor__(self, other):
        if isinstance(other, int) or isinstance(other, long) or isinstance(other, Integer):
            return self.xor(0, other)
        assert isinstance(other, self.base)
        assert self.in_bits == other.in_bits
        assert self.out_bits == other.out_bits
        return self.new((a ^ b for a, b in zip(self, other)), n=self.out_bits)

    def randomize_xor(self):
        a = randint(0, self.insize - 1)
        b = randint(0, self.outsize - 1)
        return self.xor(a, b)

    def randomize_linear(self):
        A = self.SBox2.gen.random_linear_permutation(self.m)
        B = self.SBox2.gen.random_linear_permutation(self.n)
        return A * self * B

    def randomize_affine(self):
        A = self.SBox2.gen.random_affine_permutation(self.m)
        B = self.SBox2.gen.random_affine_permutation(self.n)
        return A * self * B

    def mobius(self):
        return self.SBox2(mobius(tuple(self)), n=self.n)


def squeeze_by_mask(x, mask):
    res = 0
    pos = 0
    while mask:
        if mask & 1:
            res |= (x & 1) << pos
            pos += 1
        mask >>= 1
        x >>= 1
    return res


def test_transform():
    from cryptools.sbox2 import SBox2

    s = SBox2([5, 6, 3, 2, 1, 7, 0, 4])
    assert s.xor(0, 3) == s ^ 3
    assert s.mobius().mobius() == s
