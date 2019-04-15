from cryptools.sagestuff import binomial
from cryptools.py.utils import *
from .cache import *

def sumbinom(n, d):
    return sum(binomial(n, i) for i in xrange(d+1))
