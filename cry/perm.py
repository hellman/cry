from sage.all import matrix, GF, Permutation

F2 = GF(2)


class Perm:
    def __init__(self, p, n=None):
        self.p = tuple(p)
        self.n = n if n is not None else (max(self.p) + 1)
        self.m = len(self.p)
        assert all(0 <= i < self.n for i in self.p)

    @classmethod
    def from_matrix(cls, m):
        res = [None] * m.nrows()
        for y, x in m.support():
            res[y] = x
        return cls(res, n=m.ncols())

    def to_matrix(self, field=F2):
        m = matrix(Permutation([v + 1 for v in self.p]))
        m = m.transpose().change_ring(field)
        return m

    def complete(self, n):
        assert n >= self.n
        s = set(self.p)
        return self.Perm(self.p + tuple(v for v in range(n) if v not in s))

    def __invert__(self):
        res = [None] * len(self)
        for x, y in enumerate(self):
            res[y] = x
        return Perm(res)

    def apply(self, x, inverse=False):
        if inverse:
            assert self.n == self.m == len(x)
            res = [0] * len(x)
            for i, j in enumerate(self.p):
                res[j] = x[i]
            return tuple(res)
        else:
            return tuple(x[i] for i in self.p)

    def unapply(self, x):
        return self.apply(x, inverse=True)

    def __eq__(self, other):
        return self.p == other

    def __str__(self):
        return str(self.p)

    def __repr__(self):
        return f"Perm({self.p}, n={self.n})"

    def __len__(self):
        return self.m

    def __iter__(self):
        return iter(self.p)


def test_perm():
    p = (0, 3, 2, 6, 5, 4, 7, 1)
    assert Perm.from_matrix(Perm(p).to_matrix()) == p

    x = list(range(8))
    assert (~Perm(p)).apply(Perm(p).apply(x)) == tuple(range(8))
    assert Perm(p).unapply(Perm(p).apply(x)) == tuple(range(8))
    print("test ok")


if __name__ == '__main__':
    test_perm()
