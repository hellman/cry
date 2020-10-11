class Bit(object):
    def __init__(self, v):
        if isinstance(v, set):
            self.anf = v
            # TODO: checks on the anf structure?
        elif isinstance(v, int):
            v = int(v)
            self.anf = {()} if v else set()
        elif isinstance(v, str):
            # may be expression str?
            self.anf = {(v,)}
        else:
            assert 0, "Bit(%s) = ?" % type(v)

    def __eq__(self, other):
        if isinstance(other, int) or isinstance(other, str):
            return self == Bit(other)
        assert isinstance(other, Bit)
        return self.anf == other.anf

    def __hash__(self):
        # to make {Bit(0): 3}[0] return 3
        if self.is_const():
            return hash(self.const())
        if self.is_var():
            return hash(self.var())
        return hash(tuple(sorted(self.anf)))

    def __xor__(self, other):
        if not isinstance(other, Bit):
            other = Bit(other)
        return Bit(self.anf ^ other.anf)
    __add__ = __xor__
    __rxor__ = __xor__
    __radd__ = __add__

    def __and__(self, other):
        # heavy!
        res = set()
        for t1 in self.anf:
            for t2 in other.anf:
                res ^= {self._merge_products(t1, t2)}
        return Bit(res)
    __mul__ = __and__
    __rand__ = __and__
    __rmul__ = __mul__

    def __invert__(self):
        return self ^ Bit.ONE

    def __or__(self, other):
        # ok?
        return ~((~self) & (~other))

    def _merge_products(self, t1, t2):
        assert isinstance(t1, tuple)
        assert isinstance(t2, tuple)
        res = set(t1) | set(t2)
        return tuple(sorted(res))

    def __str__(self):
        res = []
        for t in sorted(self.anf):
            if t == ():
                res.append("1")
            else:
                res.append("*".join(map(str, sorted(t))))
        return " ^ ".join(sorted(res)) or "0"

    def __repr__(self):
        return "Bit(%r)" % self.anf

    def degree(self, filter_func=None):
        if filter_func is None:
            return max(len(t) for t in self.anf) if self.anf else -1  # -inf?
        else:
            res = 0
            for t in self.anf:
                res = max(res, sum(1 for v in t if filter_func(v)))
            return res

    def variables(self, filter_func=None):
        vs = set()
        for t in self.anf:
            for v in t:
                if not filter_func or filter_func(v):
                    vs.add(v)
        return vs

    def varcount(self, filter_func=None):
        return len(self.variables(filter_func=filter_func))

    def subs(self, lst):
        if len(lst) == 0:
            return self
        if len(lst) > 1:
            res = self.subs([lst[0]])
            return res.subs(lst[1:])

        var, bit = lst[0]
        # print("subs", var, bit)
        if isinstance(var, Bit):
            var = var.var()
        if isinstance(bit, int):
            bit = Bit(bit)
        assert isinstance(var, str)
        assert isinstance(bit, Bit)
        res = self.anf.copy()
        for t1 in self.anf:
            if var in t1:
                res ^= {t1}
                i = t1.index(var)
                t1 = t1[:i] + t1[i+1:]
                for t2 in bit.anf:
                    res ^= {self._merge_products(t1, t2)}
        return Bit(res)

    def is_const(self):
        if self.anf == {()}:
            return True
        if self.anf == set():
            return True
        return False

    def const(self):
        return int(() in self.anf)

    def __nonzero__(self):
        return self.anf != {}

    def __int__(self):
        if self.anf == {1}:
            return 1
        if self.anf == set():
            return 0
        raise ValueError("Not constant expression!")

    def is_var(self):
        if len(self.anf) == 1:
            for t in self.anf:
                if len(t) == 1:
                    return True
        return False

    def var(self):
        if len(self.anf) == 1:
            for t in self.anf:
                if len(t) == 1:
                    return t[0]
        raise ValueError("Not a single variable!")


Bit.ZERO = Bit(0)
Bit.ONE = Bit(1)


def test_bit():
    from cry.py.anf.symbolic import Bit
    assert str(Bit(0)) == "0"
    assert str(Bit(1)) == "1"
    assert str(Bit("x1")) == "x1"
    assert str(Bit("x2")) == "x2"
    assert str(Bit("x1") & Bit("x2")) == "x1*x2"
    assert str(Bit("x1") ^ Bit("x2")) == "x1 ^ x2"
    assert str(
        Bit(1) * Bit("x1") * Bit("x2") * Bit(1) +
        Bit(0) * Bit("x3") + Bit(1)
    ) == "1 ^ x1*x2"

    ex = Bit("a") * Bit("b") + Bit("R") * Bit("b")
    bb = Bit(1) + Bit("Q") + Bit("c") * Bit("b")
    assert str(ex.subs([("b", bb)]) + 1) \
        == "1 ^ Q*R ^ Q*a ^ R ^ R*b*c ^ a ^ a*b*c"
    assert {Bit(0): 123}[0] == 123
