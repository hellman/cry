from sage.all import matrix, vector, GF, random_vector

F2 = GF(2)


class AffineSystem:
    def __init__(self, oracle, n_in, field=F2, ntests=10):
        self.oracle = oracle
        self.field = field
        self.n_in = int(n_in)

        self.zero = vector(field, oracle([0] * n_in))
        self.n_out = len(self.zero)
        cols = []
        for i in range(n_in):
            x = [0] * n_in
            x[i] = 1
            y = vector(field, oracle(x)) - self.zero
            cols.append(y)

        self.matrix = matrix(field, cols).transpose()
        self._kernel = None

        self.rank = self.matrix.rank()
        self.kernel_dimension = self.matrix.ncols() - self.rank

        self.test_oracle(ntests)

    def test_oracle(self, ntests=10):
        for i in range(ntests):
            x = random_vector(self.field, self.n_in)
            y_matrix = self.matrix * x + self.zero
            y_oracle = self.oracle(x)
            assert tuple(y_oracle) == tuple(y_matrix)
        return True

    @property
    def kernel(self):
        if self._kernel is None:
            self._kernel = self.matrix.right_kernel()
        return self._kernel

    def solve(self, target, all=False):
        target = vector(self.field, target) - self.zero
        x = self.matrix.solve_right(vector(self.field, target))
        if not all:
            return x
        for z in self.kernel:
            yield z + x


def test():
    from sage.all import randint, random_matrix, choice, primes

    ps = list(primes(20))
    for itr in range(100):
        fld = GF(choice(ps))
        m = random_matrix(fld, randint(2, 50), randint(2, 50))
        print(f"#{itr}", ":", m.nrows(), "x", m.ncols(), "rank", m.rank())

        def oracle(x):
            nonlocal m
            return m * vector(fld, x)

        A = AffineSystem(oracle, m.ncols(), field=fld)
        x = random_vector(fld, m.ncols())
        y = A.matrix * x

        num = 0
        for x in A.solve(y, all=True):
            assert tuple(oracle(x)) == tuple(y)
            num += 1
            if num > 10:
                break


if __name__ == '__main__':
    test()
