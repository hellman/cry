from ..base import sbox_mixin
from .gen import gen


@sbox_mixin
class Generators(object):
    gen = gen
