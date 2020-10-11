from itertools import product

from cry.sagestuff import GF
from cry.sbox2 import SBox2

BASIS_LIST = "polynomial normal".split()


class SubfieldDecomposition(object):
    '''
    Decomposing @flarge as product of two @fsmall
    Using @polynomial(?) basis with irreducible polynomial
    y**2 + A*y + B
    '''
    def __init__(self, flarge, fsmall):
        self.flarge = flarge
        self.fsmall = fsmall

        assert flarge.characteristic() == 2
        assert fsmall.characteristic() == 2
        self.N = self.flarge.degree()
        self.D = self.fsmall.degree()
        assert self.N == self.D * 2
        self.mask = (1 << self.D) - 1

        self.X = self.fsmall.polynomial_ring().gen()

        self.g1 = self.flarge.gen()
        self.exp1, self.log1 = self.compute_explog(self.g1, in_field=True)

    def set_poly(self, A, B, basis="polynomial"):
        self.intA = A
        self.intB = B
        self.A = self.fsmall.fetch_int(A)
        self.iA = 1/self.A
        self.B = self.fsmall.fetch_int(B)
        self.basis = basis
        assert basis in BASIS_LIST

        X = self.X
        p = X**2 + self.A*X + self.B
        if not p.is_irreducible():
            return

    def check_gens(self, only_linear=True):
        for g2 in xrange(2, 2**self.N):
            try:
                exp2, log2 = self.compute_explog(g2, in_field=False, mulfunc=self.mul)
            except ValueError:
                continue
            large_to_double = self.make_transition(exp2, log2)
            if not only_linear or large_to_double.is_linear():
                yield ((self.basis, self.intA, self.intB, g2), large_to_double)

    def iterate_polys(self, only_linear=True, polynomial=True, normal=False):
        '''
        For GF(2**6) -> GF(2**3) decomposition,
        polynomial covers all normal basis
        '''
        for a, b in product(range(1, 2**self.D), repeat=2):
            if polynomial:
                self.set_poly(a, b, basis="polynomial")
                for res in self.check_gens(only_linear=only_linear):
                    yield res
            if normal:
                self.set_poly(a, b, basis="normal")
                for res in self.check_gens(only_linear=only_linear):
                    yield res

    def make_transition(self, exp2, log2):
        large_to_double = [0, 1]
        for x in xrange(2, 2**self.N):
            l = self.log1[x]
            y = exp2[l]
            large_to_double.append(y)
        large_to_double = SBox2(large_to_double)
        return large_to_double

    def compute_explog(self, g, in_field, mulfunc=None):
        exp = []
        log = [None] * 2**self.N

        cur = self.flarge(1) if in_field else 1
        seen = set()
        for e in xrange(2**self.N-1):
            toput = cur.integer_representation() if in_field else cur
            exp.append(toput)
            log[toput] = e
            if toput in seen:
                raise ValueError("Not a generator: %r: powers %r" % (g, exp))
            seen.add(toput)
            cur = g * cur if not mulfunc else mulfunc(g, cur)
        return exp, log

    def mul(self, x, y):
        toF = self.fsmall.fetch_int
        a, b = toF(x >> self.D), toF(x & self.mask)
        c, d = toF(y >> self.D), toF(y & self.mask)

        if self.basis == "polynomial":
            a, b = (
                (a*d + b*c + self.A*a*c).integer_representation(),
                (b*d + self.B*a*c).integer_representation()
            )
        elif self.basis == "normal":
            t = (a + b)*(c + d)*self.iA*self.B
            a, b = (
                (a*c*self.A + t).integer_representation(),
                (b*d*self.A + t).integer_representation()
            )
        else:
            assert 0
        return (a << self.D) | b
