from itertools import product
from random import randint, random, shuffle

from cryptools.sagestuff import (
    Integer, GF, PolynomialRing
)
from cryptools.binary import concat as concat_ints
from cryptools.sbox2 import SBox2

register = SBox2.registry.register


@register
def id(n):
    return SBox2(range(2**n))


identity = id


@register
def const(c, n):
    return SBox2([c] * 2**n)


@register
def swap(h):
    res = []
    for l in range(2**h):
        for r in range(2**h):
            res.append((r << h) | l)
    return SBox2(res)


@register
def parallel(funcs):
    input_size = [f.input_size() for f in funcs]
    output_size = [f.output_size() for f in funcs]
    res = []
    for xs in product(*[range(2**w) for w in input_size]):
        fully = 0
        for f, x, w in zip(funcs, xs, output_size):
            fully = (fully << w) | f(x)
        res.append(fully)
    return SBox2(res, m=output_size)


@register
def concat(funcs):
    assert len(set(f.input_size() for f in funcs)) == 1
    sizes = tuple(f.output_size() for f in funcs)
    return SBox2(
        [concat_ints(*ys, sizes=sizes) for ys in zip(*funcs)],
        m=sum(sizes)
    )


@register
def random_permutation(n, zero_zero=False):
    res = list(range(2**n))
    shuffle(res)
    if zero_zero:
        i = res.index(0)
        res[0], res[i] = res[i], res[0]
    return SBox2(res)


@register
def random_function(n, m=None, zero_zero=False):
    m = m or n
    res = [randint(0, 2**n-1) for i in range(2**m)]
    if zero_zero:
        res[0] = 0
    return res


@register
def random_function_of_degree(
        n, m, d, zero_zero=False,
        force_all_maxterms=False
    ):
    anf = [0] * m
    mindeg = 1 if zero_zero else 0
    for deg in range(mindeg, d + 1):
        for mask in hamming_masks(m, deg):
            for out_bit in range(m):
                take = int(randint(0, 1) or (force_all_maxterms and deg == d))
                anf[mask] = (anf[mask] << 1) | take
    return SBox2(anf, m=m).mobius()


@register
def random_involution(n, allow_fixed_points=True):
    s = list(range(2**n))
    if not allow_fixed_points:
        pairs = list(range(2**n))
        shuffle(pairs)
    else:
        """
        Uniform?
        n elements
        a(k): number of involutions with k transpositions
        a(k) / a(k-1) = (n-2*k+2) * (n-2*k+1) / (2*k)
        approximate by floats to avoid bigints, should be ok
        """
        ak = [1.0]
        for k in range(1, 2**(n-1)+1):
            ak.append(
                ak[-1] * (n-2*k+2) * (n-2*k+1) / (2*k)
            )
        r = random() * sum(ak)
        acc = 0
        for k in range(2**(n-1)+1):
            acc += ak[k]
            if acc >= r:
                break

        pairs = list(range(2**n))
        shuffle(pairs)
        pairs = pairs[:2*k]

    for i in range(0, len(pairs), 2):
        a, b = s[i:i+2]
        s[a] = b
        s[b] = a
    return SBox2(s)


def hamming_masks(n, h):
    if h == 0:
        yield 0
        return
    if h == 1:
        for e in range(n):
            yield 1 << e
        return
    if h == n:
        yield (1 << n) - 1
        return
    for x in range(2**n):
        if Integer(x).popcount() == h:
            yield x


@register
def random_minicipher(n, kn=None):
    s = []
    for k in range(2**kn):
        p = list(range(2**n))
        shuffle(p)
        s.extend(p)
    return SBox2(s)


@register
def power(e, n=None, fld=None):
    assert (n is not None) ^ (fld is not None)
    fld = fld or GF(2**n, name='a')
    x = PolynomialRing(fld, names='x').gen()
    return SBox2(x**e)
