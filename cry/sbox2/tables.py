import os.path as Path
import subprocess
from functools import reduce

import ast
from collections import Counter

from bint import Bin

from cry.sagestuff import ZZ, GF, Integer, matrix, randint, Combinations

from cry.py.anf import mobius

DDT_EXE = Path.join(Path.abspath(Path.dirname(__file__)), "ddt")


class Tables(object):
    def branch_number(self):
        res = self.m + self.n
        for x in range(self.insize):
            for dx in range(1, self.insize):
                y = self[x]
                y2 = self[x ^ dx]
                dy = y ^ y2
                res = min(res, Integer(dy).popcount() + Integer(dx).popcount)
        return res

    def kddt(self, k=3, zero_zero=False):
        kddt = matrix(ZZ, self.insize, self.outsize)
        for xs in Combinations(range(self.insize), k):
            ys = map(self, xs)
            dx = reduce(lambda a, b: a ^ b, xs)
            dy = reduce(lambda a, b: a ^ b, ys)
            kddt[dx, dy] += 1
        if zero_zero:
            kddt[0, 0] = 0
        return kddt

    def add_add_ddt(self):
        addt = matrix(ZZ, self.insize, self.outsize)
        for x in range(self.insize):
            for dx in range(1, self.insize):
                x2 = (x + dx) % self.insize
                y = self[x]
                y2 = self[x2]
                dy = (y2 - y) % self.outsize
                addt[dx, dy] += 1
        return addt

    def add_xor_ddt(self):
        axddt = matrix(ZZ, self.insize, self.outsize)
        for x in range(self.insize):
            for dx in range(1, self.insize):
                x2 = (x + dx) % self.insize
                y = self[x]
                y2 = self[x2]
                dy = y ^ y2
                axddt[dx, dy] += 1
        return axddt

    def xor_add_ddt(self):
        axddt = matrix(ZZ, self.insize, self.outsize)
        for x in range(self.insize):
            for dx in range(1, self.insize):
                x2 = x ^ dx
                y = self[x]
                y2 = self[x2]
                dy = (y2 - y) % self.outsize
                axddt[dx, dy] += 1
        return axddt

    def cmul_xor_ddt(self, F=None):
        if F is None:
            F = GF(self.insize, name='a')
        cxddt = matrix(ZZ, self.insize, self.outsize)
        for x in range(1, self.insize):
            for dx in range(2, self.insize):
                x2 = (F.fetch_int(x) * F.fetch_int(dx)).integer_representation()
                y = self[x]
                y2 = self[x2]
                dy = y2 ^ y
                cxddt[dx, dy] += 1
        return cxddt

    def cmul_cmul_ddt(self, F=None):
        if F is None:
            F = GF(self.insize, name='a')
        ccddt = matrix(ZZ, self.insize, self.outsize)
        for x in range(1, self.insize):
            for dx in range(2, self.insize):
                x2 = (F.fetch_int(x) * F.fetch_int(dx)).integer_representation()
                y = self[x]
                y2 = self[x2]
                dy = (
                    F.fetch_int(y2) * F.fetch_int(y)**(self.outsize - 2)
                ).integer_representation()
                ccddt[dx, dy] += 1
        return ccddt

    def xor_cmul_ddt(self, F=None):
        if F is None:
            F = GF(self.insize, name='a')
        xcddt = matrix(ZZ, self.insize, self.outsize)
        for x in range(self.insize):
            for dx in range(1, self.insize):
                x2 = x ^ dx
                y = self[x]
                y2 = self[x2]
                dy = (
                    F.fetch_int(y2) * F.fetch_int(y)**(self.outsize - 2)
                ).integer_representation()
                xcddt[dx, dy] += 1
        return xcddt

    def minilat(self, abs=False):
        """LAT taken on a basis points"""
        res = matrix(ZZ, self.m, self.n)
        for eu in range(self.m):
            for ev in range(self.n):
                u = Integer(2**eu)
                v = Integer(2**ev)
                for x in range(2**self.m):
                    res[eu, ev] += (
                        (u & x).popcount() & 1 == (v & self[x]).popcount() & 1
                    )
        if abs:
            res = res.apply_map(_abs)
        return res

    def minilat_binary(self, mod=4):
        """minilat % mod and then mod/2 -> 1, 0 -> 0"""
        mat = self.minilat() % 4
        for x in mat.list():
            assert x in (0, mod / 2), "invalid mod for given function"
        return (mat.lift() / (mod / 2)).change_ring(GF(2))

    def hdim(self, right_to_left=False):
        """
        hdim[i,j] = i-th output bit contains monomial x1...xn/xj
        """
        res = matrix(GF(2), self.in_bits, self.out_bits)
        anf = mobius(tuple(self))
        for j in range(self.in_bits):
            mask = (1 << self.in_bits) - 1
            mask ^= 1 << (self.in_bits - 1 - j)
            res.set_column(j, Bin(anf[mask], self.out_bits).tuple)
        if right_to_left:
            res = res[::-1,::-1]
        return res

    def ddt_distrib_fast(self):
        inp = "%d\n" % self.insize
        inp += " ".join(map(str, self))
        p = subprocess.Popen(DDT_EXE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        s = p.communicate(inp)[0]
        return Counter(ast.literal_eval(s))

    def ddt_max_estimation(self, iter=100, limit=None):
        mx = 0
        for i in range(iter):
            dx = randint(1, self.insize - 1)
            cnt = 0
            dys = Counter()
            for x in range(self.insize):
                dy = self[x] ^ self[x^dx]
                dys[dy] += 1
                if limit is not None and dys[dy] > limit:
                    return dys[dy]
                mx = max(mx, dys[dy])
        return mx

    def max_ddt(self):
        return max(self.ddt_distrib_fast().keys())
        #return max(self.ddt(zero_zero=True).list())

    def max_lat(self):
        return max(self.lat(zero_zero=True, abs=True).list())

    def nonlinearity(self):
        #return min(c.nonlinearity() for c in self.components())
        return 2**(self.m - 1) - self.max_lat()

    def is_APN(self):
        """
        self.max_ddt() == 2
        """
        if self.ddt_max_estimation(limit=2) > 2:
            return False
        return max(self.ddt_distrib_fast().keys()) <= 2

    def is_almost_bent(self):
        """
        Achieving bound: (Sidelnikov-Chabaud-Vaudenay bound)
            self.nonlinearity() <= 2**(self.m-1) - 2**((self.m-1)/2
            <=>
            self.max_lat() >= 2**((self.m-1)/2) = sqrt(2**m) / sqrt(2)

        Defined only if self.n == self.m ???
        Only possible if:
            self.m is odd
        Also, almost_bent => APN
        """
        assert self.n == self.m
        if self.m & 1 == 0:
            return False
        max_lat = self.max_lat()
        assert max_lat >= 2**((self.m - 1)/2), "Bound fail"
        return max_lat == 2**((self.m - 1)/2)

    def is_bent(self):
        """
        Achieving bound: (covering radius bound)
            self.nonlinearity() <= 2**(self.m-1) - 2**(self.m/2 - 1)
            <=>
            self.max_lat() >= 2**(self.m/2 - 1) = sqrt(2**m) / 2

        Only possible if:
            self.m is even
            and
            self.m >= self.n * 2
        """
        max_lat = self.max_lat()
        if self.m & 1:
            return False
        assert max_lat >= 2**(self.m / 2 - 1), "Bound fail"
        return max_lat == 2**(self.m / 2 - 1)
