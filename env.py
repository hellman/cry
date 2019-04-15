#-*- coding:utf-8 -*-

from collections import Counter, defaultdict
from itertools import product, combinations

from cryptools.py.env import *

from cryptools.sagestuff import *

from cryptools.sbox2 import SBox2
from cryptools.matrix import matrix_mult_int, mat_to_tuples
from cryptools.binary import * #tobin, frombin, hw, bit_product, scalar_bin, scalar_int, xorsum, allvecs
from cryptools.utils import IntervalCheck, sumbinom
from cryptools.plots import save_plot

from cryptools.fields import all_irreducible_polynomials, all_fields_of_dimension

from pprint import pprint
