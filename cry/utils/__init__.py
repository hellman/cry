from cry.sagestuff import binomial
from cry.py.utils import *
from cry.utils.cache import *


def sumbinom(n, d):
    return sum(binomial(n, i) for i in range(d+1))
