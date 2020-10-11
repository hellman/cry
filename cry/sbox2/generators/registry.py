from ..sbox2 import SBox2


class GeneratorRegistry(object):
    def register(self, func):
        setattr(self, func.__name__, func)


def initialize_registry():
    if getattr(SBox2, SBox2.GENERATORS_ATTRIBUTE, None) is None:
        setattr(SBox2, SBox2.GENERATORS_ATTRIBUTE, GeneratorRegistry())
