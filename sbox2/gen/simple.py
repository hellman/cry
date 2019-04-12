#-*- coding:utf-8 -*-

from itertools import product

from cryptools.sagestuff import randint, Integer, shuffle
from cryptools.binary import hw, concat


from .gen import register, gen


@register
def id(n):
    return range(2**n)

@register
def identity(n):
    return range(2**n)


@register
def swap(n):
    res = []
    for al in xrange(2**n):
        for ar in xrange(2**n):
            l, r = ar, al
            res.append((l << n) | r)
    return res


@register
def parallel(funcs, width=None):
    m = len(funcs)
    widths_in = [width or f.m for f in funcs]
    widths_out = [width or f.n for f in funcs]
    res = []
    for xs in product(*[range(2**w) for w in widths_in]):
        fully = 0
        for f, x, w in zip(funcs, xs, widths_out):
            fully = (fully << w) | f(x)
        res.append(fully)
    return res


@register
def concat_output(funcs):
    sizes = tuple(f.out_bits for f in funcs)
    return [concat(*ys, sizes=sizes) for ys in zip(funcs)]


@register
def random_permutation(n, homo=False):
    res = range(1 if homo else 0, 2**n)
    shuffle(res)
    return ([0] if homo else []) + res


@register
def random_function(m, n=None, homo=False):
    n = n or m
    res = [randint(0, 2**n-1) for i in xrange(2**m)]
    if homo:
        res[0] = 0
    return res


@register
def random_sbox_of_degree(m, n, d, homo=False, force_all_maxterms=False):
    anfs = [list() for i in xrange(n)]
    for out_bit in xrange(n):
        mindeg = 1 if homo else 0
        for deg in xrange(mindeg, d + 1):
            for mask in hamming_masks(m, deg):
                if randint(0, 1) == 1 or (force_all_maxterms and deg == d):
                    anfs[out_bit].append(mask)
    res = []
    for x in xrange(2**m):
        y = 0
        for e, anf in enumerate(anfs):
            e = n - 1 - e
            val = 0
            for mask in anf:
                val ^= ((mask & x) == mask)
            val &= 1
            y |= val << e
        res.append(y)
    return res

@register
def random_Boolean_function_of_degree(m, d):
    anf = [randint(0, 1) if hw(x) <= d else 0 for x in xrange(2**m)]
    return gen.SBox2(anf, n=1).mobius()

@register
def random_involution(n):
    print 'WARNING: too low number of fixed points! not a uniform distribution'
    pairs = range(2**n)
    shuffle(pairs)
    s = [0] * 2**n
    while pairs:
        if len(pairs) == 1 or randint(1, len(pairs)) == 1:
            a = b = pairs.pop()
        else:
            a, b = pairs.pop(), pairs.pop()
        s[a] = b
        s[b] = a
    return s



def hamming_masks(n, h):
    if h == 0:
        yield 0
        return
    if h == 1:
        for e in xrange(n):
            yield 1 << e
        return
    if h == n:
        yield (1 << n) - 1
        return
    for x in xrange(2**n):
        if Integer(x).popcount() == h:
            yield x


@register
def random_minicipher(n):
    res = []
    for k in xrange(2**n):
        p = range(2**n)
        shuffle(p)
        res.append(tuple(p))
    return tuple(res)
