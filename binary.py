#-*- coding:utf-8 -*-

from cryptools.sagestuff import Integer

from cryptools.py.binary import *


def hamming(v):
    return Integer(v).popcount()
hw = hamming


def test_binary():
    assert hamming(0) == hamming(0L) == hamming(Integer(0)) == 0
    assert hamming(1) == hamming(1L) == hamming(Integer(1)) == 1
    assert hamming(2) == hamming(2L) == hamming(Integer(2)) == 1
    v = 1889421344686260973171433197677248273467675043680169246693717736553773868585782209193108237
    assert hamming(int(v)) == hamming(long(v)) == hamming(Integer(v)) == 159

    assert split(0x123, size=4, parts=3) == (1, 2, 3)
    assert concat(1, 2, 3, size=4) == 0x123
    assert swap_halves(0xab, 4) == 0xba
    assert split_halves(0xab, 4) == (0xa, 0xb)
