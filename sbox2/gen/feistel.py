from .gen import register

from .simple import random_function, random_permutation, random_sbox_of_degree, random_minicipher


@register
def feistel_round_xor(n, func, do_swap=False):
    res = []
    for al in xrange(2**n):
        for ar in xrange(2**n):
            l, r = al, ar
            l ^= func(r)
            if do_swap:
                l, r = r, l
            res.append((l << n) | r)
    return res


@register
def feistel_round_add(n, func, do_swap=False):
    mask = (1 << n) - 1
    res = []
    for al in xrange(2**n):
        for ar in xrange(2**n):
            l, r = al, ar
            l = (l + func(r)) & mask
            if do_swap:
                l, r = r, l
            res.append((l << n) | r)
    return res


@register
def feistel_network_xor(n, nrounds=None, funcs=None, permutations=True, degree=None):
    if funcs is None:
        assert nrounds is not None
        assert (not permutations) or (degree is None), "Not implemented to generate permutations of arbitrary degree"
        gen = random_function
        if permutations:
            gen = random_permutation
        if degree:
            gen = lambda n: random_sbox_of_degree(n, degree)
        funcs = [gen(n) for i in xrange(nrounds)]

    res = []
    for al in xrange(2**n):
        for ar in xrange(2**n):
            l, r = al, ar
            for func in funcs:
                l ^= func[r]
                l, r = r, l
            l, r = r, l
            res.append((l << n) | r)
    return res


@register
def feistel_round_minicipher(n, func=None, do_swap=False):
    if func is None:
        func = random_minicipher(n)
    res = []
    for al in xrange(2**n):
        for ar in xrange(2**n):
            l, r = al, ar
            l = func[r][l]
            if do_swap:
                l, r = r, l
            res.append((l << n) | r)
    return res
