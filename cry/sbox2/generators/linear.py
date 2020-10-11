from random import randint

from cry.sagestuff import GF

from cry.matrix import matrix_mult_int
from cry.matrix import (
    random_matrix,
    random_invertible_matrix,
    random_permutation_matrix,
)

from cry.sbox2 import SBox2

register = SBox2.new.register


@register
def from_matrix(mat):
    s = []
    for x in range(2**mat.ncols()):
        s.append(matrix_mult_int(mat, x))
    return SBox2(s, m=mat.nrows())


@register
def random_linear_permutation(n):
    return from_matrix(random_invertible_matrix(n))


@register
def random_affine_permutation(n):
    xor = randint(0, 2**n-1)
    return SBox2(y ^ xor for y in from_matrix(random_invertible_matrix(n)))


@register
def random_linear(n, m=None):
    if m is None:
        m = n
    return from_matrix(random_matrix(GF(2), m, n))


@register
def random_affine(*args):
    lin = random_linear(*args)
    xor = randint(0, max(lin))
    return SBox2(y ^ xor for y in lin)


@register
def random_bit_permutation(n):
    return from_matrix(random_permutation_matrix(GF(2), n))
