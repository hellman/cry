def test_inversion():
    from cryptools.sbox2 import SBox2
    s = SBox2([5, 6, 3, 2, 1, 7, 0, 4])

    assert ~s == s.inverse() == [6, 4, 3, 2, 7, 0, 1, 5]

    s = SBox2([3, 4, 7, 2, 1, 1, 6, 6], n=4)
    assert s.image() == (1, 2, 3, 4, 6, 7)
    assert s.preimage(2) == s.index(2) == 3
    assert s.preimage(1) == s.index(1) == 4
    assert s.preimage(6) == s.index(6) == 6
    assert s.preimages(2) == (3,)
    assert s.preimages(1) == (4, 5)
    assert s.preimages(6) == (6, 7)

    assert sorted(s.preimage_structure().items()) == [(1, 4), (2, 2)]
