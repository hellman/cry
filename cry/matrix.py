from collections import Counter

from copy import copy

from random import shuffle
from cry.sagestuff import (
    vector, matrix, identity_matrix, random_matrix,
    GF, LinearCode
)

from bint import Bin


def matrix_mult_int(mat, x):
    """
    MSB to LSB vector
    >>> matrix_mult_int( \
        matrix(GF(2), [[1, 0, 1], [1, 0, 0]]), \
        0b110) # read as 6 -> 1,1,0 -> 1,1 -> 3
    3
    """
    assert mat.base_ring() == GF(2)
    n = mat.ncols()
    x = vector(GF(2), Bin(x, n).tuple)
    y = mat * x
    return Bin(y).int


def matrix_mult_int_rev(mat, x):
    """
    LSB to MSB vector
    >>> matrix_mult_int_rev( \
        matrix(GF(2), [[1, 0, 1], [1, 0, 0]]), \
        0b110) # read as 6 -> 0,1,1 -> 1,0 -> 1
    1
    """
    assert mat.base_ring() == GF(2)
    n = mat.ncols()
    x = vector(GF(2), Bin(x, n).tuple[::-1])
    y = mat * x
    return Bin(y[::-1]).int


def matrix_is_mds(mat):
    """@mat is considered as operator M*x"""
    n = mat.ncols()
    m = mat.nrows()

    mat2 = matrix(mat.base_ring(), m * 2, n)
    mat2[:m, :n] = identity_matrix(mat.base_ring(), m, n)
    mat2[m:, :n] = mat

    # linear code: x -> (x || M*x)
    C = LinearCode(mat2.transpose())
    D = C.minimum_distance()
    K = n
    N = 2 * m

    # Singleton bound
    # MDS on equality
    assert D <= N - K + 1
    return D == N - K + 1


def mat_from_linear_func(m, n, func):
    mat = matrix(GF(2), n, m)
    for i, e in enumerate(reversed(range(m))):
        x = 1 << e
        mat.set_column(i, Bin(func(x), n).tuple)
    return mat


def mat_field_mul_const(field, c):
    assert field.base_ring() == GF(2)
    d = field.degree()
    m = matrix(GF(2), d, d)
    for i, e in enumerate(reversed(range(d))):
        x = 1 << e
        res = field.fetch_int(x) * field.fetch_int(c)
        res = res.integer_representation()
        m.set_column(i, Bin(res, d).tuple)
    return m


def mat_to_tuples(mat):
    """Useful for hashing matrices (set/dict)"""
    return tuple(map(tuple, mat))


def mat_max(mat):
    return max(max(v) for v in mat)


def mat_min(mat):
    return min(min(v) for v in mat)


def mat_distribution(mat):
    return Counter(sum(map(list, mat), []))


def mat_zero_zero(mat):
    mat = copy(mat)
    for y in range(mat.nrows()):
        mat[y, 0] = 0
    for x in range(mat.ncols()):
        mat[0, x] = 0
    return mat


def random_invertible_matrix(field, n):
    """Hack because GL(GF(2), n).random_element()
    uses weird own random generator state
    """
    while 1:
        m = random_matrix(field, n)
        if not m.is_singular():
            return m


def random_permutation_matrix(field, n):
    rows = list(identity_matrix(n))
    shuffle(rows)
    return matrix(field, rows)
