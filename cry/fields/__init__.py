#-*- coding:utf-8 -*-

from sage.all import PolynomialRing, GF

from .basis_change import *


def all_irreducible_polynomials(N, p=2):
    FR = PolynomialRing(GF(p), names=("X",))
    for poly in FR.polynomials(of_degree=N):
        if poly.is_irreducible():
            yield poly


def all_fields_of_dimension(N, p=2, name='a'):
    for poly in all_irreducible_polynomials(N, p):
        yield GF(p**N, name=name, modulus=poly)
