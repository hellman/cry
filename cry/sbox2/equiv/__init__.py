from itertools import product

from bint import Bin

from sage.crypto.boolean_function import BooleanFunction
from sage.all import BooleanPolynomialRing, Integer, Matrix, GF, LinearCode

from .linear import LEContext
from .linear_generic import LEContext as LEContextGeneric


class Equiv(object):
    @staticmethod
    def are_XOR_equivalent(s1, s2):
        """
        If yes, return (cx, cy) such that
            s1[x] = cy + s2[x + cx]
        (+ is xor)
        """
        s1, s2 = convert_sboxes(s1, s2)
        assert_equal_sizes(s1, s2)
        n = s1.n
        for cx in range(2**n):
            cy = s1[0] ^ s2[0 ^ cx]
            for x in range(1, 2**n):
                if s1[x] ^ s2[x ^ cx] != cy:
                    break
            else:
                return (cx, cy)

    def is_XOR_equivalent(self, other):
        return Equiv.are_XOR_equivalent(self, other)

    @staticmethod
    def are_linear_equivalent(s1, s2, findall=False):
        """
        Algorithm is described in the following paper:
        @inproceedings{eurocrypt-2003-2059,
          title={A Toolbox for Cryptanalysis: Linear and Affine Equivalence Algorithms},
          booktitle={Advances in Cryptology - EUROCRYPT 2003, International Conference on the Theory and Applications of Cryptographic Techniques, Warsaw, Poland, May 4-8, 2003, Proceedings},
          series={Lecture Notes in Computer Science},
          publisher={Springer},
          volume={2656},
          pages={33-50},
          url={http://www.iacr.org/cryptodb/archive/2003/EUROCRYPT/2059/2059.pdf},
          doi={10.1007/3-540-39200-9_3},
          author={Alex Biryukov and Christophe De Cannière and An Braeken and Bart Preneel},
          year=2003
        }
        """
        s1, s2 = convert_sboxes(s1, s2)
        assert_equal_sizes(s1, s2)
        # currently
        # assert_permutations(s1, s2)

        LEcls = LEContext if s1.is_permutation() and s2.is_permutation() else LEContextGeneric
        LEcls.sbox = Equiv.new
        ctx = LEcls(s1, s2, findall=findall)
        res = ctx.run()
        if findall and res:
            for A, B in res:
                assert B * s1 * A == s2
                assert A.is_permutation()
                assert B.is_permutation()
                assert A.is_linear()
                assert B.is_linear()
            return res
        elif res:
            A, B = res
            assert B * s1 * A == s2
            assert A.is_permutation()
            assert B.is_permutation()
            return A, B
        return res

    def is_linear_equivalent(self, other, **kwargs):
        return self.are_linear_equivalent(self, other, **kwargs)

    @staticmethod
    def are_affine_equivalent(s1, s2, findall=False, counts_only=False):
        s1, s2 = convert_sboxes(s1, s2)
        assert_equal_sizes(s1, s2)
        # currently
        # assert_permutations(s1, s2)

        full_res = {}

        # temporary unoptimal algorithm
        for a, b in product(range(s1.input_range()), range(s1.output_range())):
            xor_s1 = Equiv.new(s1[x ^ a] ^ b for x in range(s1.input_range()))
            lin_res = xor_s1.is_linear_equivalent(s2, findall=findall)
            if findall and lin_res:
                for A, B in lin_res:
                    assert A.is_permutation()
                    assert B.is_permutation()
                    assert (B * xor_s1 * A) == s2
                    assert (B * s1.xor(a, b) * A) == s2
                    xa = A.preimage(a)
                    xb = B[b]
                    assert (B * s1 * A).xor(xa, xb) == s2
                if counts_only:
                    full_res.setdefault((a, b), 0)
                    full_res[a, b] += len(lin_res)
                else:
                    full_res.setdefault((a, b), [])
                    full_res[a, b] += lin_res
            elif lin_res:
                A, B = lin_res
                assert A.is_permutation()
                assert B.is_permutation()
                assert (B * xor_s1 * A) == s2
                assert (B * s1.xor(a, b) * A) == s2
                xa = A.preimage(a)
                xb = B[b]
                assert (B * s1 * A).xor(xa, xb) == s2
                return xa, A, B, xb
        return full_res if findall else False

    def is_affine_equivalent(self, other, **kwargs):
        return self.are_affine_equivalent(self, other, **kwargs)

    @staticmethod
    def are_CCZ_equivalent(s1, s2):
        s1, s2 = convert_sboxes(s1, s2)
        assert_equal_sizes(s1, s2)
        lin1 = s1.is_linear()
        lin2 = s2.is_linear()
        if lin1 ^ lin2:
            return False
        if lin1 and lin2:
            return True

        inp, out = s1.n, s1.m
        M1 = Matrix(GF(2), 1 + inp + out, 2**inp)
        M2 = Matrix(GF(2), 1 + inp + out, 2**inp)
        for x in range(2**inp):
            M1.set_column(
                x,
                Bin.concat(Bin(1, 1) + Bin(x, inp) + Bin(s1[x], out)).tuple
            )
            M2.set_column(
                x,
                Bin.concat(Bin(1, 1) + Bin(x, inp) + Bin(s2[x], out)).tuple
            )

        L1 = LinearCode(M1)
        L2 = LinearCode(M2)
        # Annoying: this is not checked in "is_permutation_equivalent" code!
        # raises a TypeError instead
        if L1.generator_matrix().nrows() != L2.generator_matrix().nrows():
            return False
        return L1.is_permutation_equivalent(L2)

    def is_CCZ_equivalent(self, other):
        return self.are_CCZ_equivalent(self, other)


def assert_equal_sizes(s1, s2):
    assert s1.m == s2.m
    assert s1.n == s2.n


def convert_sboxes(s1, s2):
    if not isinstance(s1, Equiv.cls):
        s1 = Equiv.new(s1)
    if not isinstance(s2, Equiv.cls):
        s2 = Equiv.new(s2)
    assert isinstance(s1, Equiv.cls)
    assert isinstance(s2, Equiv.cls)
    return s1, s2


def assert_permutations(s1, s2):
    assert s1.is_permutation()
    assert s2.is_permutation()
