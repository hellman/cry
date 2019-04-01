#-*- coding:utf-8 -*-

def mobius(bf):
    assert isinstance(bf, list) or isinstance(bf, tuple)
    if len(bf) == 1:
        return (bf[0],)
    assert len(bf) & 1 == 0
    h = len(bf) / 2
    sub0 = mobius(bf[:h])
    sub1 = mobius(bf[h:])
    return sub0 + tuple(a ^ b for a, b in zip(sub0, sub1))
