from .sagestuff import *

from .py.env import *

from .sbox2 import SBox2
from .matrix import matrix_mult_int, mat_to_tuples
from .utils import IntervalCheck, sumbinom
from .plots import save_plot

from .fields import all_irreducible_polynomials, all_fields_of_dimension

from .eq.affine import AffineSystem
from .eq.lattice import Lattice

from .rsa.rsa import RSA


def gcd_generic(u, v):
    while v != 0:
        u, v = v, u % v
    return u
