#-*- coding:utf-8 -*-

def xor_closure(nums):
    res = {0}
    for x in nums:
        if x not in res:
            for y in res.copy():
                res.add(x ^ y)
    return tuple(res)


def complete_basis(basis, n):
    """Compute some basis2 such that basis2 with @basis span the whole space of dimensions n"""
    space = set(xor_closure(basis))
    res = []
    for v in xrange(1, 2**n):
        if v not in space:
            for u in space.copy():
                space.add(u ^ v)
            res.append(v)
    assert len(res) + len(basis) == n
    return tuple(res)
