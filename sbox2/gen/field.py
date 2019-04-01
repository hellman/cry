#-*- coding:utf-8 -*-

from itertools import product

from cryptools.sagestuff import GF, PolynomialRing

from .gen import register


@register
def from_poly(p, varname="x"):
    fld = p.base_ring()
    return [p.subs(**{varname: fld.fetch_int(i)}).integer_representation() for i in xrange(fld.order())]

@register
def exponent(n, e, fld=None):
    fld = fld or GF(2**n, name='a')
    x = PolynomialRing(fld, names='x').gen()
    return from_poly(x**e)
