#-*- coding:utf-8 -*-

from .gen import register

from cryptools.sagestuff import randint

from cryptools.matrix import matrix_mult_int
from cryptools.matrix import random_invertible_matrix, random_matrix, random_bit_permutation_matrix

@register
def from_matrix(mat):
    m = mat.ncols()
    res = []
    for x in xrange(2**m):
        res.append(matrix_mult_int(mat, x))
    return res


@register
def random_linear_permutation(n):
    return from_matrix(random_invertible_matrix(n))


@register
def random_affine_permutation(n):
    xor = randint(0, 2**n-1)
    return [y ^ xor for y in from_matrix(random_invertible_matrix(n))]


@register
def random_linear(*args):
    return from_matrix(random_matrix(*args))


@register
def random_affine(*args):
    lin = random_linear(*args)
    xor = randint(0, max(lin))
    return [y ^ xor for y in lin]


@register
def random_bit_permutation(n):
    return from_matrix(random_bit_permutation_matrix(n))
