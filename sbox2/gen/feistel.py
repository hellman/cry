from .gen import register, gen


@register
def feistel_round_xor(func, swap=False):
    func = gen.SBox2(func)
    n = func.in_bits
    res = []
    for al in xrange(2**n):
        for ar in xrange(2**n):
            l, r = al, ar
            l ^= func(r)
            if swap:
                l, r = r, l
            res.append((l << n) | r)
    return res


@register
def feistel_round_add(func, swap=False):
    func = gen.SBox2(func)
    n = func.in_bits
    mask = (1 << n) - 1
    res = []
    for al in xrange(2**n):
        for ar in xrange(2**n):
            l, r = al, ar
            l = (l + func(r)) & mask
            if swap:
                l, r = r, l
            res.append((l << n) | r)
    return res


@register
def feistel_network_xor(funcs=None, n=None, nrounds=None, permutations=False, degree=None):
    if funcs is None:
        assert n is not None
        assert nrounds is not None
        assert (not permutations) or (degree is None), "Not implemented to generate permutations of arbitrary degree"
        fgen = gen.random_function
        if permutations:
            fgen = gen.random_permutation
        if degree:
            fgen = lambda n: gen.random_sbox_of_degree(n, degree)
        funcs = [fgen(n) for i in xrange(nrounds)]
    else:
        funcs = map(gen.SBox2, funcs)
        n = funcs[0].in_bits

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
def feistel_round_minicipher(n, func=None, swap=False):
    if func is None:
        func = gen.random_minicipher(n)
    res = []
    for al in xrange(2**n):
        for ar in xrange(2**n):
            l, r = al, ar
            l = func[r][l]
            if swap:
                l, r = r, l
            res.append((l << n) | r)
    return res
