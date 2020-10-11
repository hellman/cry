from cry.sbox2 import SBox2
from cry.sagestuff import Integer


def test_main():
    from cry.sbox2 import SBox2
    s = SBox2([3, 4, 7, 2, 1, 1, 6, 6], m=4)

    assert s.n == s.input_size() == 3
    assert s.m == s.output_size() == 4
    assert len(s) == 8

    assert list(s.input_range()) == list(range(8))
    assert list(s.output_range()) == list(range(16))

    assert list(s.graph()) == [
        (0, 3), (1, 4), (2, 7), (3, 2), (4, 1), (5, 1), (6, 6), (7, 6)
    ]

    assert s.as_hex(sep=":") == "3:4:7:2:1:1:6:6"
    assert s.as_hex(sep="") == "34721166"

    ss = SBox2([3, 4, 7, 2, 1, 1, 6, 6])
    assert s != ss
    assert s == ss.resize(4)

    ss = SBox2([3, 4, 7, 2, 1, 1, 6, 6], 4)
    assert s == ss

    ss = SBox2([2, 4, 7, 2, 1, 1, 6, 6], 4)
    assert s != ss

    assert s == [3, 4, 7, 2, 1, 1, 6, 6]
    assert s == (3, 4, 7, 2, 1, 1, 6, 6)
    assert s != (2, 4, 7, 2, 1, 1, 6, 6)

    assert hash(s) != 0

    assert s ^ 1 == s ^ 1 == s ^ Integer(1) == s ^ SBox2([1] * 8, m=4) \
        == (2, 5, 6, 3, 0, 0, 7, 7)
    assert s ^ s == [0] * 8

    assert s[0] == s(0) == s[0, 0, 0] == 3
    assert s[3] == s(3) == s[0, 1, 1] == 2
    assert s[7] == s(7) == s[1, 1, 1] == 6
    assert tuple(s)[1:3] == (4, 7)
    assert tuple(s)[-3:] == (1, 6, 6)


def props(s):
    fs = [
        s.is_involution,
        s.is_permutation,
        s.is_zero,
        s.is_identity,
        s.is_constant,
        s.is_linear,
        s.is_affine,
        s.is_balanced,
    ]
    return {f for f in fs if f()}


def test_properties():
    s = SBox2([5, 6, 3, 2, 1, 7, 0, 4])
    assert props(s) == {s.is_permutation, s.is_balanced}
    assert props(s.resize(4)) == set()

    s = SBox2((0, 13, 14, 3, 8, 5, 6, 11, 12, 1, 2, 15, 4, 9, 10, 7))
    assert props(s) == {
        s.is_permutation, s.is_balanced, s.is_affine, s.is_linear
    }

    s = SBox2((14, 13, 6, 5, 0, 3, 8, 11, 15, 12, 7, 4, 1, 2, 9, 10))
    assert props(s) == {s.is_permutation, s.is_balanced, s.is_affine}

    s = SBox2([1] * 16)
    assert props(s) == {s.is_affine, s.is_constant}

    s = SBox2([0] * 16)
    assert props(s) == {
        s.is_affine, s.is_constant, s.is_linear, s.is_zero, s.is_balanced
    }

    s = SBox2([0] * 15 + [1])
    assert props(s) == set()

    s = SBox2(range(16))
    assert props(s) == {
        s.is_identity, s.is_permutation, s.is_balanced,
        s.is_involution, s.is_affine, s.is_linear,
    }

    s = SBox2([0] * 8 + [1] * 8)
    assert props(s) == {s.is_balanced, s.is_affine, s.is_linear}

    s = SBox2([1] * 8 + [0] * 8)
    assert props(s) == {s.is_balanced, s.is_affine}

    s = SBox2(list(range(8, 16)) + list(range(8)))
    assert props(s) == {
        s.is_balanced, s.is_permutation, s.is_involution, s.is_affine,
    }


def test_transform():
    s = SBox2([5, 6, 3, 2, 1, 7, 0, 4])
    assert s.xor(0, 3) == s ^ 3
    assert s.mobius().mobius() == s


def test_degrees():
    s = SBox2([0] * 15 + [1])
    assert s.degrees() == (4,)
    assert str(s.anfs()) == "[x0*x1*x2*x3]"

    s = SBox2([1] * 8 + [0] * 8)
    assert s.degrees() == (1,)
    assert str(s.anfs()) == "[x0 + 1]"

    s = SBox2([0] * 16)
    assert s.degrees() == ()
    assert str(s.anfs()) == "[]"

    s = SBox2([1] * 16)
    assert s.degrees() == (0,)
    assert str(s.anfs()) == "[1]"


def test_inversion():
    s = SBox2([5, 6, 3, 2, 1, 7, 0, 4])

    assert ~s == s**(-1) == [6, 4, 3, 2, 7, 0, 1, 5]

    s = SBox2([3, 4, 7, 2, 1, 1, 6, 6], m=4)
    assert s.image() == {1, 2, 3, 4, 6, 7}
    assert s.preimage(2) == 3
    assert s.preimage(1) == 4
    assert s.preimage(6) == 6
    assert s.preimages(2) == (3,)
    assert s.preimages(1) == (4, 5)
    assert s.preimages(6) == (6, 7)

    assert sorted(s.preimage_structure().items()) == [(1, 4), (2, 2)]
