def mobius(bf):
    assert isinstance(bf, list) or isinstance(bf, tuple)
    if len(bf) == 1:
        return (bf[0],)
    assert len(bf) & 1 == 0
    h = len(bf) // 2
    sub0 = mobius(bf[:h])
    sub1 = mobius(bf[h:])
    return sub0 + tuple(a ^ b for a, b in zip(sub0, sub1))


def walsh(bf):
    assert isinstance(bf, list) or isinstance(bf, tuple)
    if len(bf) == 1:
        return (bf[0],)
    assert len(bf) & 1 == 0
    h = len(bf) // 2
    sub0 = walsh(bf[:h])
    sub1 = walsh(bf[h:])
    res0 = tuple(a + b for a, b in zip(sub0, sub1))
    res1 = tuple(a - b for a, b in zip(sub0, sub1))
    return res0 + res1


def submask_sum(f):
    assert isinstance(f, list) or isinstance(f, tuple)
    if len(f) == 1:
        return (f[0],)
    assert len(f) & 1 == 0
    h = len(f) // 2
    sub0 = submask_sum(f[:h])
    sub1 = submask_sum(f[h:])
    return sub0 + tuple(a + b for a, b in zip(sub0, sub1))


def undo_submask_sum(f):
    assert isinstance(f, list) or isinstance(f, tuple)
    if len(f) == 1:
        return (f[0],)
    assert len(f) & 1 == 0
    h = len(f) // 2
    f0 = f[:h]
    f1 = tuple(a - b for a, b in zip(f[:h], f[h:]))
    sub0 = undo_submask_sum(f0)
    sub1 = undo_submask_sum(f1)
    return sub0 + sub1
