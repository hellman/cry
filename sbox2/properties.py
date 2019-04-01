#-*- coding:utf-8 -*-

from itertools import product

from .base import sbox_mixin


@sbox_mixin
class Properties(object):
    def is_involution(self):
        return all(self[self[x]] == x for x in xrange(self.insize))

    def is_permutation(self):
        if self.n != self.m:
            return False
        return sorted(self[x] for x in xrange(self.insize)) == range(self.insize)

    def is_zero(self):
        return max(self) == 0

    def is_identity(self):
        return list(self) == range(self.insize)

    def is_constant(self):
        return min(self) == max(self)

    def is_linear(self):
        return self[0] == 0 and self.is_affine()

    def is_affine(self):
        a = self[0]
        res = [a]
        for i in xrange(self.in_bits):
            delta = self[1 << i] ^ a
            res.extend([y ^ delta for y in res])
        return self == res

    def is_balanced(self):
        """require surjectivity or not?"""
        # return len(self.preimage_structure()) == 1 # not

        if self.in_bits < self.out_bits:
            return False
        return list(self.preimage_structure().items()) == \
               [(1 << (self.in_bits - self.out_bits), 1 << self.out_bits)]

def props(s):
    fs = [
        s.is_involution,
        s.is_permutation,
        s.is_zero,
        s.is_identity,
        s.is_constant,
        s.is_linear,
        s.is_affine,
        s.is_balanced,
    ]
    return {f for f in fs if f()}

def test_properties():
    from cryptools.sbox2 import SBox2

    s = SBox2([5, 6, 3, 2, 1, 7, 0, 4])
    assert props(s) == {s.is_permutation, s.is_balanced}
    assert props(s.resize(4)) == set()

    s = SBox2((0, 13, 14, 3, 8, 5, 6, 11, 12, 1, 2, 15, 4, 9, 10, 7))
    assert props(s) == {s.is_permutation, s.is_balanced, s.is_affine, s.is_linear}

    s = SBox2((14, 13, 6, 5, 0, 3, 8, 11, 15, 12, 7, 4, 1, 2, 9, 10))
    assert props(s) == {s.is_permutation, s.is_balanced, s.is_affine}

    s = SBox2([1] * 16)
    assert props(s) == {s.is_affine, s.is_constant}

    s = SBox2([0] * 16)
    assert props(s) == {s.is_affine, s.is_constant, s.is_linear, s.is_zero, s.is_balanced}

    s = SBox2([0] * 15 + [1])
    assert props(s) == set()

    s = SBox2(range(16))
    assert props(s) == {s.is_identity, s.is_permutation, s.is_balanced, s.is_involution, s.is_affine, s.is_linear}

    s = SBox2([0] * 8 + [1] * 8)
    assert props(s) == {s.is_balanced, s.is_affine, s.is_linear}

    s = SBox2([1] * 8 + [0] * 8)
    assert props(s) == {s.is_balanced, s.is_affine}

    s = SBox2(range(8, 16) + range(8))
    assert props(s) == {s.is_balanced, s.is_permutation, s.is_involution, s.is_affine}
