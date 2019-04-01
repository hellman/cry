#-*- coding:utf-8 -*-

from functools import partial

from itertools import product


def rol(x, n, bits):
    """
        >>> hex( rol(0x1234, 4, 16) )
        '0x2341'
        >>> hex( rol(0x1234, 12, 16) )
        '0x4123'
    """
    mask = (1 << bits) - 1
    n %= bits
    x &= mask
    return ((x << n) | (x >> (bits - n))) & mask

def ror(x, n, bits):
    """
        >>> hex( ror(0x1234, 4, 16) )
        '0x4123'
        >>> hex( ror(0x1234, 12, 16) )
        '0x2341'
    """
    return rol(x, bits - n, bits)

for w in (8, 16, 32, 64, 128):
    globals()["rol%d" % w] = partial(rol, bits=w)
    globals()["ror%d" % w] = partial(ror, bits=w)


def tobin(x, n):
    '''
    MSB to LSB binary form

        >>> tobin(1, 4)
        (0, 0, 0, 1)
        >>> tobin(8, 4)
        (1, 0, 0, 0)
        >>> tobin(16, 4)
        Traceback (most recent call last):
        ...
        AssertionError
    '''
    assert 0 <= x < 1<<n
    return tuple(map(int, bin(x).lstrip("0b").rjust(n, "0")))

def sbin(x, n):
    '''
    MSB to LSB binary form in string
    '''
    return bin(x).lstrip("0b").rjust(n, "0")

def frombin(v):
    '''
    MSB to LSB binary form

        >>> frombin((1, 0, 0, 0))
        8
        >>> frombin((0, 0, 0, 1))
        1
        >>> frombin(tobin(123123, 32))
        123123
    '''
    return int("".join(map(str, v)), 2 )

def bitrev(x, n):
    return frombin(tobin(x, n)[::-1])

def hamming(x):
    '''
    Sum of all bits in ZZ.

        >>> hamming(0)
        0
        >>> hamming(1)
        1
        >>> hamming(0xffffffff)
        32
        >>> hamming(2**64-1)
        64
        >>> hamming(int("10" * 999, 2))
        999
    '''
    ans = 0
    while x:
        ans += x & 1
        x >>= 1
    return int(ans)
hw = hamming

def parity(v):
    """
    Sum of all bits modulo 2.

        >>> parity(0)
        0
        >>> parity(1)
        1
        >>> parity(4)
        1
        >>> parity(6)
        0
        >>> parity(2**100)
        1
        >>> parity(2**100 + 1)
        0
        >>> parity(2**100 ^ 7)
        0
        >>> parity(2**100 ^ 3)
        1
    """
    return hamming(v) & 1

def scalar_int(a, b):
    """
    Scalar product of binary expansions of a and b (in integers)

        >>> scalar_int(0, 0)
        0
        >>> scalar_int(1, 1)
        1
        >>> scalar_int(0xf731, 0xffffff)
        10
        >>> scalar_int(1, 3)
        1
        >>> scalar_int(7, 15)
        3
    """
    return hamming(a & b)

def scalar_bin(a, b):
    """
    Scalar product of binary expansions of a and b (modulo 2)

        >>> scalar_bin(0, 0)
        0
        >>> scalar_bin(1, 1)
        1
        >>> scalar_bin(0xf731, 0xffffff)
        0
        >>> scalar_bin(1, 3)
        1
        >>> scalar_bin(7, 15)
        1
    """
    return parity(a & b)

def bit_product(x, mask):
    """
    Bit product function
        >>> bit_product(0x1111, 0x1111)
        1
        >>> bit_product(0x1111, 0x1110)
        1
        >>> bit_product(0x1111, 0x0111)
        1
        >>> bit_product(0x0111, 0x1111)
        0
        >>> bit_product(0x1110, 0x1111)
        0
    """
    return int(x & mask == mask)

def xorsum(*lst):
    """
    Xor variant of python's sum()
        >>> xorsum(1, 2, 4)
        7
        >>> xorsum(1, 1, 1)
        1
        >>> xorsum(1, 2, 4, 6, 3, 2, 4, 5, 1)
        0
        >>> xorsum(x for x in range(8))
        0
        >>> xorsum(xrange(8))
        0
        >>> xorsum()
        0
    """
    if len(lst) == 0:
        return 0
    if len(lst) == 1 and hasattr(lst[0], "__iter__"):
        lst = list(lst[0])
    return reduce(lambda a, b: a ^ b, lst)

def allvecs(*dims):
    return product(*[range(2**d) for d in dims])


def concat(*lst, **kwargs):
    """
    Actual sig:
    concat(*lst, size=None, sizes=None)

        >>> hex( concat(1, 2, 3, size=4) )
        '0x123'
        >>> hex( concat(1, 2, 3, sizes=(4, 8, 4)) )
        '0x1023'
        >>> hex( concat(*split(0x12345678, size=4, parts=8), size=4) )
        '0x12345678'
    """
    size = kwargs.pop("size", None)
    sizes = kwargs.pop("sizes", None)
    if size:
        assert sizes is None
        sizes = [size] * len(lst)
    else:
        assert sizes
    fully = 0
    for y, w in zip(lst, sizes):
        fully = (fully << w) | y
    return fully


def split(x, sizes=None, size=None, parts=None):
    """
        >>> split(0x123, size=4, parts=3)
        (1, 2, 3)
        >>> split(0x123, sizes=(8, 4))
        (18, 3)
    """
    res = []
    if parts:
        assert size
        assert sizes is None
        sizes = [size] * parts
    else:
        assert sizes
        assert parts is None
        assert size is None
        parts = len(sizes)
    for w in reversed(sizes):
        res.append(x & ((1 << w) - 1))
        x >>= w
    return tuple(res)[::-1]

def concat_halves(l, r, h):
    '''
        >>> hex(concat_halves(0x7, 0xa, 4))
        '0x7a'
    '''
    return (l << h) | r


def split_halves(x, h):
    '''
        >>> split_halves(0x79, 4)
        (7, 9)
    '''
    assert x < 4**h
    mask = (1 << h) - 1
    return (x >> h) & mask, (x & mask)


def swap_halves(x, h):
    '''
        >>> hex(swap_halves(0x79, 4))
        '0x97'
    '''
    l, r = split_halves(x, h)
    return concat_halves(r, l, h)


def concat(*lst, **kwargs):
    """
    Actual sig:
    concat(*lst, size=None, sizes=None)

        >>> hex( concat(1, 2, 3, size=4) )
        '0x123'
        >>> hex( concat(1, 2, 3, sizes=(4, 8, 4)) )
        '0x1023'
        >>> hex( concat(*split(0x12345678, size=4, parts=8), size=4) )
        '0x12345678'
    """
    size = kwargs.pop("size", None)
    sizes = kwargs.pop("sizes", None)
    if size:
        assert sizes is None
        sizes = [size] * len(lst)
    else:
        assert sizes
    fully = 0
    for y, w in zip(lst, sizes):
        fully = (fully << w) | y
    return fully


def split(x, sizes=None, size=None, parts=None):
    """
        >>> split(0x123, size=4, parts=3)
        (1, 2, 3)
        >>> split(0x123, sizes=(8, 4))
        (18, 3)
    """
    res = []
    if parts:
        assert size
        assert sizes is None
        sizes = [size] * parts
    else:
        assert sizes
        assert parts is None
        assert size is None
        parts = len(sizes)
    for w in reversed(sizes):
        res.append(x & ((1 << w) - 1))
        x >>= w
    return tuple(res)[::-1]


def test_binary():
    assert hamming(0) == hamming(0L) == 0
    assert hamming(1) == hamming(1L) == 1
    assert hamming(2) == hamming(2L) == 1
    v = 1889421344686260973171433197677248273467675043680169246693717736553773868585782209193108237
    assert hamming(int(v)) == hamming(long(v)) == 159

    assert tobin(0x1234, 20) == (0,0,0,0,  0,0,0,1,  0,0,1,0,   0,0,1,1,   0,1,0,0)
    assert frombin((0,0,0,0,  0,0,0,1,  0,0,1,0,   0,0,1,1,   0,1,0,0)) == 0x1234

    assert split(0x123, size=4, parts=3) == (1, 2, 3)
    assert concat(1, 2, 3, size=4) == 0x123
    assert swap_halves(0xab, 4) == 0xba
    assert split_halves(0xab, 4) == (0xa, 0xb)
