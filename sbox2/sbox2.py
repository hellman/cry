from random import randint
from collections import defaultdict, Counter

from sage.crypto.sbox import SBox as Sage_SBox
from sage.rings.polynomial.polynomial_element import is_Polynomial
from sage.structure.element import is_Vector

from cryptools.sagestuff import ZZ, Integer, lcm, matrix, GF
from cryptools.sagestuff import BooleanFunction, BooleanPolynomialRing
from cryptools.matrix import mat_distribution

from cryptools.py.binary import frombin, tobin, parity, swap_halves, hw
from cryptools.py.binary import squeeze_by_mask
from cryptools.py.anf import mobius

from .gen import gen


class SBox2:
    """
    Attrs:
        n (int): input bits
        m (int): output bits
    """
    new = gen

    def __init__(self, spec, m=None):
        if is_Polynomial(spec):
            raise NotImplementedError("todo")

        self._S = tuple(map(int, spec))
        self.n = ZZ(len(self._S)).nbits()
        self.m = ZZ(max(self._S)).nbits()
        if m is not None:
            self.m = int(m)
            lim = 1 << self.m
            assert all(0 <= y < lim for y in self._S)
        else:
            m = ZZ(max(self._S)).nbits()
        assert self.input_size() >= 1
        assert self.output_size() >= 1

    def to_sage(self):
        return Sage_SBox(self._S)

    def input_size(self):
        return self.n

    def output_size(self):
        return self.m

    def __len__(self):
        return (1 << self.n)

    def tuple(self):
        return self._S

    def list(self):
        return list(self._S)

    def input_range(self):
        return range(1 << self.input_size())
    domain = input_size

    def output_range(self):
        return range(1 << self.output_size())
    codomain = output_range

    def image(self):
        return set(self)

    def graph(self):
        return enumerate(self)

    def __eq__(self, other):
        # override: allow comparison with tuple
        if isinstance(other, type(self)):
            return (
                self.output_size() == other.output_size()
                and self._S == other._S
            )
        return self.tuple() == tuple(other)

    def __hash__(self):
        """
        Warning: does not match hash of the tuple, so will not match tuple in
        a set or dict
        """
        return hash((self.output_size(), self.tuple()))

    def __iter__(self):
        return iter(self.tuple())

    def __getitem__(self, x):
        x = int_tuple_list_vector(x)
        return self._S[x]
    __call__ = __getitem__

    # =================================================
    # REPRESENTATION
    # =================================================
    def as_table(self, height=None, width=None):
        assert (width is None) ^ (height is None)
        if width is not None:
            height = self.input_size() // width
        else:
            width = self.input_size() // height
        assert height * width == self.input_size()
        m = matrix(ZZ, height, width)
        for x, y in self.graph():
            m[divmod(x, width)] = y
        return m

    def as_matrix(self):
        assert self.is_linear()

        m = matrix(GF(2), self.output_size(), self.input_size())
        for e in range(self.input_size()):
            vec = tobin(self[2**e], self.output_size())
            m.set_column(self.input_size() - 1 - e, vec)
        return m

    def hex_str(self, sep=""):
        numhex = (self.output_size() + 3) // 4
        hexformat = "%0" + str(numhex) + "x"
        return sep.join(hexformat % y for y in self)

    # =================================================
    # COMPOSITION
    # =================================================
    def __mul__(self, other):
        if not isinstance(other, type(self)) \
           or other.output_size() != self.input_size():
            other = type(self)(other, m=self.input_size())
        return self.new((self[y] for x, y in other.graph()), m=self.m)

    def __pow__(self, e):
        if e < 0:
            return (~self)**(-e)
        if e == 0:
            return self.new.identity(self.input_size)
        res = self if e & 1 else self.new.identity(self.input_size)
        a = self
        while e > 1:
            e >>= 1
            a = a * a
            if e & 1:
                res = res * a
        return res

    # =================================================
    # CYCLES
    # =================================================
    def cycles(self):
        assert self.is_permutation()
        xs = set(self.input_range())
        _cycles = []
        cycle = []
        while xs:
            x = xs.pop()
            cycle.append(x)
            while 1:
                x = self[x]
                if x == cycle[0]:
                    break
                cycle.append(x)
                xs.remove(x)
            _cycles.append(cycle)
            cycle = []
        return _cycles

    def cycle_structure(self):
        return sorted(map(len, self.cycles()))

    def order(self):
        return lcm(self.cycle_structure())

    # =================================================
    # INVERSION
    # =================================================
    def __invert__(self):
        assert self.is_permutation()
        table = [None] * len(self)
        for x, y in self.graph():
            table[y] = x
        assert None not in table
        return type(self)(table)

    def preimage(self, x):
        x = int_tuple_list_vector(x)
        return self._S.index(x)

    def preimages(self, x):
        x = int_tuple_list_vector(x)
        return tuple(xx for xx, y in self.graph() if y == x)

    def preimages_all(self):
        res = defaultdict(list)
        for x, y in self.graph():
            res[y].append(x)
        return res

    def preimage_structure(self):
        return Counter(map(len, self.preimages_all().values()))

    # =================================================
    # PROPERTIES
    # =================================================
    def is_involution(self):
        # override
        return all(self[y] == x for x, y in self.graph())

    def is_permutation(self):
        if self.input_size() != self.output_size():
            return False
        ret = [None] * 2**self.output_size()
        for x, y in self.graph():
            ret[y] = 1
        return None not in ret

    def is_zero(self):
        return max(self) == 0

    def is_identity(self):
        return all(x == y for x, y in self.graph())

    def is_constant(self):
        return min(self) == max(self)

    def is_linear(self):
        return self[0] == 0 and self.is_affine()

    def is_affine(self):
        a = self[0]
        res = [a]
        for i in range(self.in_bits):
            delta = self[1 << i] ^ a
            for y in res[::]:
                res.append(y ^ delta)
                if res[-1] != self[len(res)-1]:
                    return False
        return True

    def is_balanced(self):
        expected_size = self.input_size() - self.output_size()
        if expected_size < 1:
            return False
        return (
            list(self.preimage_structure().items()) ==
            [2**expected_size, 2**self.output_size()]
        )

    # =================================================
    # TRANSFORMATION
    # =================================================
    def resize(self, m):
        return type(self)(self, m=m)

    def xor(self, input, output):
        input = int_tuple_list_vector(input)
        output = int_tuple_list_vector(output)
        assert input in self.input_range()
        assert output in self.output_range()
        return type(self)(
            [
                self[x.__xor__(input)].__xor__(output)
                for x in self.input_range()
            ],
            m=self.m
        )

    def __xor__(self, other):
        if isinstance(other, type(self)):
            assert self.input_size() == other.input_size()
            assert self.output_size() == other.output_size()
            return type(self)(
                [a.__xor__(b) for a, b in zip(self, other)],
                m=self.m
            )
        other = int_tuple_list_vector(other)
        return type(self)([y ^ other for y in self], m=self.m)

    def __and__(self, other):
        if isinstance(other, int) or isinstance(other, Integer):
            assert self.input_size() == other.input_size()
            assert self.output_size() == other.output_size()
            return type(self)(
                [a.__and__(b) for a, b in zip(self, other)],
                m=self.m
            )
        other = int_tuple_list_vector(other)
        return type(self)([y & other for y in self], m=self.m)

    def randomize_xor(self):
        a = randint(0, 2**self.input_size()-1)
        b = randint(0, 2**self.output_size()-1)
        return self.xor(a, b)

    def randomize_linear(self):
        A = self.SBox2.new.random_linear_permutation(self.input_size())
        B = self.SBox2.new.random_linear_permutation(self.output_size())
        return B * self * A

    def randomize_affine(self):
        A = self.SBox2.new.random_affine_permutation(self.input_size())
        B = self.SBox2.new.random_affine_permutation(self.output_size())
        return B * self * A

    def transform_graph(self, func):
        table = [None] * len(self)
        for x, y in self.graph():
            x2, y2 = func(x, y)
            assert table[x2] is None
            table[x2] = y2
        return type(self)(table)

    def swap_halves(self, input=True, output=True):
        if input:
            assert self.input_size() & 1 == 0
            hx = self.input_size() // 2
            fx = lambda x: swap_halves(x, hx)
        else:
            fx = lambda x: x
        if output:
            assert self.output_size() & 1 == 0
            hy = self.output_size() // 2
            fy = lambda y: swap_halves(y, hy)
        else:
            fy = lambda y: y
        return self.transform_graph(
            lambda x, y: (fx(x), fy(y))
        )

    def squeeze_by_mask(self, mask):
        mask = int_tuple_list_vector(mask)
        assert mask in self.output_range()
        return type(self)(
            [squeeze_by_mask(y, mask) for y in self],
            m=hw(mask)
        )

    # =================================================
    # DEGREE STUFF
    # =================================================
    def mobius(self):
        return type(self)(mobius(self.tuple()), m=self.m)

    def anfs(self):
        names = ["x%d" % e for e in range(self.in_bits)]
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

    # =================================================
    # TABLES
    # =================================================
    def difference_distribution_table(self, zero_zero=True):
        ddt = matrix(ZZ, self.input_size(), self.output_size())
        for x in self.input_range():
            for dx in self.input_range()[1:]:
                dy = self[x] ^ self[x ^ dx]
                ddt[dx, dy] += 1
        if zero_zero:
            ddt[0, 0] = 0
        return ddt
    DDT = difference_distribution_table

    def linear_approximation_table(self, zero_zero=True):
        lat = matrix(ZZ, self.input_size(), self.output_size(), [
            self.component(mask).to_sage_BF().walsh_hadamard_transform()
            for mask in self.output_range()
        ]).transpose()
        if zero_zero:
            lat[0, 0] = 0
        if abs:
            lat = lat.apply_map(abs)
        return lat
    LAT = linear_approximation_table

    def DDT_distrib(self, *a, **k):
        return mat_distribution(self.DDT(*a, **k))

    def LAT_distrib(self, *a, **k):
        return mat_distribution(self.LAT(*a, **k))

    def coordinate(self, i):
        assert 0 <= i < self.output_size()
        tt = [
            (y >> (self.output_size() - 1 - i)) & 1
            for y in self
        ]
        yield type(self)(tt, m=1)

    def coordinates(self):
        for i in range(self.output_size()):
            yield self.coordinate(i)

    def component(self, mask):
        mask = int_tuple_list_vector(mask)
        tt = [
            parity(y & mask)
            for y in self
        ]
        yield type(self)(tt, m=1)

    # TBD
    # def components(self, with_masks=False, with_anfs=False):
    #     if with_anfs:
    #         anfs = self.anfs()
    #     for mask in range(1, 2**(self.n)):
    #         mask = Integer(mask)
    #         tt = [
    #             Integer(self[x] & mask).popcount() & 1
    #             for x in range(self.insize)
    #         ]
    #         res = BooleanFunction(tt)
    #         if with_masks or with_anfs:
    #             res = [res]
    #             if with_masks:
    #                 res.append(mask)
    #             if with_anfs:
    #                 a = 0
    #                 for i, a2 in enumerate(anfs):
    #                     if mask & (1 << (self.n - 1 - i)):
    #                         a += a2
    #                 res.append(a)
    #         yield res

    # =================================================
    # Boolean Function only (m=1)
    # =================================================
    def to_sage_BF(self):
        return

    def weight(self):
        if self.output_size() != 1:
            raise TypeError("Weight is defined only for Boolean Functions")
        return sum(map(int, self))


def int_tuple_list_vector(v):
    if isinstance(v, int):
        return v
    if isinstance(v, Integer):
        return int(v)
    if isinstance(v, tuple):
        return frombin(v)
    if isinstance(v, list):
        return frombin(v)
    if is_Vector(v):
        return frombin(tuple(v))
    raise TypeError("%r is not tuple, list, vector or integer")


# ====================================================
# TESTS
# ====================================================
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
    assert props(s) == {
        s.is_permutation, s.is_balanced, s.is_affine, s.is_linear
    }

    s = SBox2((14, 13, 6, 5, 0, 3, 8, 11, 15, 12, 7, 4, 1, 2, 9, 10))
    assert props(s) == {s.is_permutation, s.is_balanced, s.is_affine}

    s = SBox2([1] * 16)
    assert props(s) == {s.is_affine, s.is_constant}

    s = SBox2([0] * 16)
    assert props(s) == {
        s.is_affine, s.is_constant, s.is_linear, s.is_zero, s.is_balanced,
    }

    s = SBox2([0] * 15 + [1])
    assert props(s) == set()

    s = SBox2(range(16))
    assert props(s) == {
        s.is_identity, s.is_permutation, s.is_balanced,
        s.is_involution, s.is_affine, s.is_linear,
    }

    s = SBox2([0] * 8 + [1] * 8)
    assert props(s) == {s.is_balanced, s.is_affine, s.is_linear}

    s = SBox2([1] * 8 + [0] * 8)
    assert props(s) == {s.is_balanced, s.is_affine}

    s = SBox2(list(range(8, 16)) + list(range(8)))
    assert props(s) == {
        s.is_balanced, s.is_permutation, s.is_involution, s.is_affine,
    }


def test_transform():
    from cryptools.sbox2 import SBox2

    s = SBox2([5, 6, 3, 2, 1, 7, 0, 4])
    assert s.xor(0, 3) == s ^ 3
    assert s.mobius().mobius() == s
