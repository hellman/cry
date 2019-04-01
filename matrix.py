from collections import Counter

from copy import copy

from cryptools.sagestuff import vector, matrix, random_matrix as sage_random_matrix, GF
from cryptools.binary import tobin, frombin


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
    x = vector(GF(2), tobin(x, n))
    y = mat * x
    return frombin(y)

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
    x = vector(GF(2), tobin(x, n)[::-1])
    y = mat * x
    return frombin(y[::-1])


def matrix_is_mds(mat):
    """@mat is considered as operator M*x"""
    n = mat.ncols()
    m = mat.nrows()

    mat2 = matrix(mat.base_ring(), m * 2, n)
    mat2[:m,:n] = identity_matrix(mat.base_ring(), m, n)
    mat2[m:,:n] = mat

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
        res = tobin(func(x), n)
        mat.set_column(i, res)
    return mat


def mat_field_mul_const(field, c):
    assert field.base_ring() == GF(2)
    d = field.degree()
    m = matrix(GF(2), d, d)
    for i, e in enumerate(reversed(range(d))):
        x = 1 << e
        res = field.fetch_int(x) * field.fetch_int(c)
        res = tobin(res.integer_representation(), d)
        m.set_column(i, res)
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
    for y in xrange(mat.nrows()):
        mat[y, 0] = 0
    for x in xrange(mat.ncols()):
        mat[0, x] = 0
    return mat


def random_matrix(*args):
    return sage_random_matrix(GF(2), *args)


def random_invertible_matrix(n):
    """Hack because GL(GF(2), n).random_element()
    uses weird own random generator state
    """
    while 1:
        m = random_matrix(n)
        if not m.is_singular():
            return m


def random_bit_permutation_matrix(n):
    r = range(1, n + 1)
    shuffle(r)
    return Permutation(r).to_matrix()
