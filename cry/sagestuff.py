"""
Trying to import only required stuff from sage.
Single point of import is good.
"""

# sage is a gigantic mess


try:
    import sage.all_cmdline
except ImportError:
    import sage.all__sagemath_modules

from copy import copy
from random import randint, shuffle, choice

from sage.arith.functions import lcm
from sage.arith.misc import GCD as gcd, inverse_mod, power_mod
from sage.coding.linear_code import LinearCode
from sage.combinat.combination import Combinations
from sage.combinat.permutation import Permutation
from sage.crypto.boolean_function import BooleanFunction
from sage.functions.other import binomial, ceil, floor
from sage.matrix.constructor import Matrix as matrix
from sage.matrix.special import identity_matrix, random_matrix
from sage.misc.functional import log
from sage.misc.persist import dumps, loads
from sage.modules.free_module_element import free_module_element as vector
from sage.modules.free_module_element import random_vector
from sage.plot.matrix_plot import matrix_plot
from sage.rings.complex_double import CDF
from sage.rings.finite_rings.finite_field_constructor import FiniteField as GF
from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as Zmod
from sage.rings.integer import Integer
from sage.rings.integer_ring import ZZ
from sage.rings.polynomial.polynomial_ring_constructor import BooleanPolynomialRing_constructor as BooleanPolynomialRing
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.rational_field import QQ
from sage.rings.real_mpfr import RR
