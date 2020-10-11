from sage.all import *

from cry.sbox2 import SBox2

N = 6


def gen():
    return SBox2.new.random_permutation(N)
    # return SBox2.new.random_function(N)


def try_good():
    A = SBox2.new.random_linear_permutation(N)
    B = SBox2.new.random_linear_permutation(N)
    s1 = gen()
    s2 = B * s1 * A
    At, Bt = SBox2.are_linear_equivalent(s1, s2)
    assert Bt * s1 * At == s2
    assert At.is_linear()
    assert Bt.is_linear()
    assert At.is_permutation()
    assert Bt.is_permutation()
    # print "GOOD OK"


def try_bad():
    s1 = gen()
    s2 = gen()
    res = SBox2.are_linear_equivalent(s1, s2)
    assert res is False
    # print "BAD OK"


def main():
    for i in range(100):
        try_good()
        try_bad()


if __name__ == '__main__':
    main()
