from random import randint, random, shuffle

from cry.sagestuff import (
    Integer, GF, PolynomialRing
)
from cry.utils import ranges
from cry.sbox2 import SBox2

from bint import Bin

register = SBox2.new.register


@register
def id(n):
    return SBox2(range(2**n))


identity = id


@register
def const(c, n):
    return SBox2([c] * 2**n)


@register
def swap(h):
    s = []
    for l, r in ranges(2**h, 2**h):
        s.append((r << h) | l)
    return SBox2(s)


@register
def parallel(funcs):
    input_sizes = [f.input_size() for f in funcs]
    output_sizes = [f.output_size() for f in funcs]
    s = []
    for xs in ranges(list=[2**w for w in input_sizes]):
        fully = 0
        for f, x, w in zip(funcs, xs, output_sizes):
            fully = (fully << w) | f(x)
        s.append(fully)
    return SBox2(s, m=sum(output_sizes))


@register
def concat(funcs):
    assert len(set(f.input_size() for f in funcs)) == 1
    sizes = tuple(f.output_size() for f in funcs)
    return SBox2(
        [Bin.concat(*Bin.array(ys, ns=sizes)) for ys in zip(*funcs)],
        m=sum(sizes)
    )


@register
def random_permutation(n, zero_zero=False):
    s = list(range(2**n))
    shuffle(s)
    if zero_zero:
        i = s.index(0)
        s[0], s[i] = s[i], s[0]
    return SBox2(s)


@register
def random_function(n, m=None, zero_zero=False):
    m = m or n
    s = [randint(0, 2**m-1) for i in range(2**n)]
    if zero_zero:
        s[0] = 0
    return SBox2(s, m=m)


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
def power(e, n=None, field=None):
    assert (n is not None) ^ (field is not None)
    field = field or GF(2**n, name='a')
    x = PolynomialRing(field, names='x').gen()
    return SBox2(x**e)
