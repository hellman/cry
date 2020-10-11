"""
Trying to import only required stuff from sage.
Single point of import is good.

Tried to import from inner modules, but probably worthless.
Seems sage.all must be imported.
"""

# sage is a gigantic mess

from sage.all_cmdline import (
    copy, power_mod,
    Integer, Zmod, ZZ, QQ, RR, CDF, Integer, GF,
    loads, dumps,
    matrix, identity_matrix, random_matrix, matrix_plot,
    vector, random_vector,
    binomial,
    lcm, gcd, log,
    Combinations, Permutation,
    LinearCode,
    floor, ceil, inverse_mod, floor,
)

from random import randint, shuffle, choice

# import sage.structure

# from sage.plot.matrix_plot import matrix_plot

# from sage.misc.persist import loads, dumps

# from sage.matrix.constructor import matrix, identity_matrix, random_matrix
# from sage.modules.free_module_element import vector
# Matrix = matrix

# from sage.rings.finite_rings.finite_field_constructor import GF
# from sage.rings.integer import Integer
# from sage.rings.integer_ring import ZZ
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.polynomial.polynomial_ring_constructor import BooleanPolynomialRing_constructor as BooleanPolynomialRing
# from sage.groups.matrix_gps.catalog import GL

# from sage.functions import log

# from sage.misc.prandom import randint, shuffle, choice
# from sage.arith.all import lcm, gcd

from sage.crypto.boolean_function import BooleanFunction

# from sage.combinat.combination import Combinations
# from sage.functions.other import binomial
