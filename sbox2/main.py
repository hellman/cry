from cryptools.sagestuff import Integer


def test_main():
    from cryptools.sbox2 import SBox2
    s = SBox2([3, 4, 7, 2, 1, 1, 6, 6], n=4)

    assert s.in_bits == 3
    assert s.out_bits == 4
    assert len(s) == 8

    assert list(s.in_range()) == list(range(8))
    assert list(s.out_range()) == list(range(16))

    assert list(s.graph()) == [
        (0, 3), (1, 4), (2, 7), (3, 2), (4, 1), (5, 1), (6, 6), (7, 6)
    ]

    assert s.as_hex_str(format="%sh", sep=":") == "3h:4h:7h:2h:1h:1h:6h:6h"
    assert s.as_hex_str(format="%s", sep="") == "34721166"

    ss = SBox2([3, 4, 7, 2, 1, 1, 6, 6])
    assert s != ss
    assert s == ss.resize(4)
    assert s.resize(2) == (3, 0, 3, 2, 1, 1, 2, 2)
    ss = SBox2([3, 4, 7, 2, 1, 1, 6, 6], 4)
    assert s == ss
    ss = SBox2([3, 4, 7, 2, 1, 1, 6, 6], 4)
    assert s == ss
    ss = SBox2([2, 4, 7, 2, 1, 1, 6, 6], 4)
    assert s != ss
    assert s == [3, 4, 7, 2, 1, 1, 6, 6]
    assert s == (3, 4, 7, 2, 1, 1, 6, 6)
    assert s == (3, 4, 7, 2, 1, 1, 6, 6)
    assert s != (2, 4, 7, 2, 1, 1, 6, 6)

    assert hash(s) != 0

    assert s ^ 1 == s ^ 1 == s ^ Integer(1) == s ^ SBox2([1] * 8, n=4) \
        == (2, 5, 6, 3, 0, 0, 7, 7)
    assert s ^ s == [0] * 8

    assert s.get(0) == s[0] == s(0) == s[0, 0, 0] == 3
    assert s.get(3) == s[3] == s(3) == s[0, 1, 1] == 2
    assert s.get(7) == s[7] == s(7) == s[1, 1, 1] == 6
    assert tuple(s)[1:3] == (4, 7)
    assert tuple(s)[-3:] == (1, 6, 6)
