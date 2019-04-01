#-*- coding:utf-8 -*-

from .base import sbox_mixin

from cryptools.sagestuff import BooleanFunction, BooleanPolynomialRing, Integer, log

from cryptools.binary import tobin


@sbox_mixin
class Degrees(object):
    def anfs_sage(self):
        """
        ANFs for bits (MSB to LSB)
        /!\ warning: sage's implementation leaks a lot of memory
        """
        res = []
        for i in xrange(self.out_bits):
            f = BooleanFunction([(y >> i) & 1 for y in self])
            res.append( f.algebraic_normal_form() )
        return tuple(reversed(res))

    def anfs(self):
        names = ["x%d" % e for e in xrange(self.in_bits)]
        bpr = BooleanPolynomialRing(names=names)
        vs = list((bpr.gens()))
        res = []
        for f in self.coordinates():
            anf = bpr(0)
            for mask, take in enumerate(mobius(tuple(f))):
                if not take:
                    continue
                clause = bpr(1)
                for b, v in zip(tobin(mask, self.in_bits), vs):
                    if b:
                        clause *= v
                anf += clause
            res.append(anf)
        return res

    def degrees(self):
        return tuple(f.degree() for f in self.anfs())

    def degree(self):
        return max(self.degrees())

    def coordinates(self):
        for e in xrange(self.out_bits):
            tt = [(y >> (self.out_bits - 1 - e)) & 1 for x, y in self.graph()]
            yield BooleanFunction(tt)

    def components(self, with_masks=False, with_anfs=False):
        if with_anfs:
            anfs = self.anfs()
        for mask in range(1, 2**(self.n)):
            mask = Integer(mask)
            tt = [(self[x] & mask).popcount() & 1 for x in xrange(self.insize)]
            res = BooleanFunction(tt)
            if with_masks or with_anfs:
                res = [res]
                if with_masks:
                    res.append(mask)
                if with_anfs:
                    a = 0
                    for i, a2 in enumerate(anfs):
                        if mask & (1 << (self.n - 1 - i)):
                            a += a2
                    res.append(a)
            yield res

def mobius(bf):
    assert isinstance(bf, list) or isinstance(bf, tuple)
    if len(bf) == 1:
        return (bf[0],)
    assert len(bf) & 1 == 0
    h = len(bf) / 2
    sub0 = mobius(bf[:h])
    sub1 = mobius(bf[h:])
    return sub0 + tuple(a ^ b for a, b in zip(sub0, sub1))

def test_TODO_DIVISION_TRANSITION_TABLE():
    pass
    # assert False

def test_degrees():
    from cryptools.sbox2 import SBox2

    s = SBox2([0] * 15 + [1])
    assert s.degrees() == (4,)
    assert str(s.anfs()) == "[x0*x1*x2*x3]"

    s = SBox2([1] * 8 + [0] * 8)
    assert s.degrees() == (1,)
    assert str(s.anfs()) == "[x0 + 1]"

    s = SBox2([0] * 16)
    assert s.degrees() == ()
    assert str(s.anfs()) == "[]"

    s = SBox2([1] * 16)
    assert s.degrees() == (0,)
    assert str(s.anfs()) == "[1]"
