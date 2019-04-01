from cryptools.sagestuff import lcm

from .base import sbox_mixin


@sbox_mixin
class Cycles(object):
    def cycles(self):
        assert self.is_permutation()

        xs = set(xrange(len(self)))
        _cycles = []
        cycle = []
        while xs:
            x = xs.pop()
            cycle.append(x)
            while 1:
                x = self[x]
                if x == cycle[0]:
                    break
                cycle.append(x)
                xs.remove(x)
            _cycles.append(cycle)
            cycle = []
        return _cycles

    def cycles_sizes(self):
        return sorted(map(len, self.cycles()))
    cycle_structure = cycles_sizes

    def order(self):
        return lcm(self.cycle_structure())
