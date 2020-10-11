r"""

Some simple checks for multiset properties in S-Boxes.

EXAMPLES::

    >>> from cry.sbox2 import SBox2
    >>> from cry.utils import ranges
    >>> from itertools import product
    >>> from pprint import pprint
    >>> from bint import Bin

Simple example:

    >>> a, b, c = (SBox2.new.random_permutation(4) for _ in range(3))
    >>> s = SBox2.new.parallel([a, b, c])
    >>> split = Split(s, 3, 3)

Manual specification of input permutation position:

    >>> split.propagate_single_permutation(pos=0)
    'pcc'
    >>> split.propagate_single_permutation(pos=1)
    'cpc'
    >>> split.propagate_single_permutation(pos=2)
    'ccp'

Automatic check of all positions:

    >>> pprint( split.check_single_permutation() )
    {'ccp': 'ccp', 'cpc': 'cpc', 'pcc': 'pcc'}

Example with balanced and unknown:

    >>> f = SBox2.new.random_function(6, 3)
    >>> s = SBox2(
    ...       Bin.concat(x, x^y, f((x << 3) | y), n=3)
    ...       for x, y in ranges(8, 8) )
    >>> s = SBox2.new.parallel([a, b, c])
    >>> split = Split(s, 3, 3)

    >>> pprint( split.check_single_permutation() )
    {'ccp': 'ccp', 'cpc': 'cpc', 'pcc': 'pcc'}

"""

from collections import defaultdict
from itertools import product

from bint import Bin

PERM = "p"
CONST = "c"
BALANCED = "b"
UNKNOWN = "?"


class Split(object):
    """
    Split input and output bits in equal portions.
    Used further for checking for simple multiset properties.
    """
    def __init__(self, sbox, num_in, num_out):
        self.s = sbox
        assert sbox.input_size() % num_in == 0
        assert sbox.output_size() % num_out == 0
        self.width_in = sbox.input_size() // num_in
        self.width_out = sbox.output_size() // num_out
        self.num_in = num_in
        self.num_out = num_out

    def check_single_permutation(self):
        res = {}
        for pos in range(self.num_in):
            inp = [CONST] * self.num_in
            inp[pos] = PERM
            inp = "".join(inp)
            out = self.propagate_single_permutation(pos)
            if out:
                res[inp] = out
        return res

    def propagate_single_permutation(self, pos):
        outs_by_consts = [defaultdict(dict) for _ in range(self.num_out)]
        for x, y in self.s.graph():
            xs = Bin(x, self.num_in * self.width_in).split(parts=self.num_in)
            ys = Bin(y, self.num_out * self.width_out).split(parts=self.num_out)
            key = tuple(xs[i] for i in range(self.num_in) if i != pos)
            for j, y in enumerate(ys):
                d = outs_by_consts[j][key]
                d.setdefault(y, 0)
                d[y] += 1

        out_prop = []
        for j in range(self.num_out):
            has_const = False
            has_perm = False
            has_balanced = False
            has_unknown = False
            for key, d in outs_by_consts[j].items():
                if self.width_in == self.width_out and\
                   len(d) == 2**self.width_in:
                    has_perm = True
                    continue
                if len(d) == 1:
                    has_const = True
                    continue

                xorsum = 0
                for y, cnt in d.items():
                    if cnt & 1:
                        xorsum ^= y
                if xorsum == 0:
                    has_balanced = True
                else:
                    has_unknown = True
                    break

            if has_unknown:
                result = UNKNOWN
            elif has_balanced:
                result = BALANCED
            elif has_const and not has_perm:
                result = CONST
            elif has_perm and not has_const:
                result = PERM
            else:
                assert False
            out_prop.append(result)
        return "".join(out_prop)

    def __getitem__(self, lst):
        assert len(lst) == self.num_in
        x = Bin.concat(Bin.array(lst, n=self.width_in))
        y = self.s[x]
        return Bin(y, self.width_out).split(parts=self.num_out)

    def TU_decomposition(self):
        '''
        Return None on fail or
        {
            T: [T0, T1, ...],
            U: [U0, U1, ...],
            swap_input: True,
            swap_output: False,
        }
        '''
        assert self.num_in == self.num_out == 2
        assert self.width_in == self.width_out
        w = self.width_in
        mask = (1 << w) - 1
        for mi, mo in self.check_single_permutation().items():
            if "p" not in mo:
                continue
            assert "p" in mi

            iswap = False
            oswap = False

            s = self.s
            if mi[1] != "p":
                s = s.swap_halves_input()
                iswap = True
            if mo[1] != "p":
                s = s.swap_halves_output()
                oswap = True

            T = []
            for lk in range(2**w):
                t = []
                for r in range(2**w):
                    x = (lk << w) | r
                    t.append(s[x] & mask)
                T.append(t)

            U = [list() for i in range(2**w)]
            for l, r in product(range(2**w), repeat=2):
                x = (l << w) | r
                r = T[l][r]
                U[r].append(s[x] >> w)
            return dict(T=T, U=U, swap_input=iswap, swap_output=oswap)
        raise RuntimeError("TU-decomposition failed!")


def print_minicipher(T, latex_letter=None):
    for k, t in enumerate(T):
        if latex_letter:
            print(
                "$%s_%x$ &" % (latex_letter, k), " & ".join(map(hex, t)), r"\\"
            )
        else:
            print("%x" % k, t)
