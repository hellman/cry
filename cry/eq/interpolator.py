from sage.all import *

from itertools import product


# class Interpolator:
#     """
#     Interpolator(3)
#     Interpolator(("x1", "x2"))
#     """
#     def __init__(self, spec):
#         if isinstance(spec, int):
#             self.n = int(spec)
#             self.names = tuple("x%d" % i for i in range(self.n))
#         elif isinstance(spec, (tuple, list)):
#             self.n = len(spec)
#             self.names = tuple(spec)
#         self.monos = set()
#         self.data = []

#     def add_data(self, xs):
#         assert len(xs) == self.n
#         row = []
#         for es in self.monos:
#             row.append(prod(x**e for x, e in zip(xs, es)))
#         self.data.append(row)

#     def sort(self, key=sum, reverse=True):
#         assert not self.data
#         self.monos = sorted(self.monos, key=key, reverse=reverse)

#     def solve(self, order="deglex", groebner=False, debug=False):
#         assert isinstance(self.monos, list), "not sorted"
#         mat = self.matrix = matrix(self.data)
#         if debug:
#             print(f"matrix: {mat.nrows()} x {mat.ncols()} rank {mat.rank()}")

#         self.R = PolynomialRing(mat.base_ring(), names=self.names, order=order)
#         xs = self.R.gens()
#         res = []
#         rk = mat.right_kernel()
#         if debug:
#             print("kernel:", rk)
#         for sol in rk.matrix():
#             assert len(sol) == len(self.monos)
#             poly = 0
#             for c, es in zip(sol, self.monos):
#                 mono = prod(x**e for x, e in zip(xs, es))
#                 poly += c * mono
#             res.append(poly)
#         return res


class Interpolator:
    def __init__(self, n=None, field=None, names=None):
        self.n = n
        self.data = []
        self.monos = set()
        self.field = field

        if isinstance(names, str):
            names = names.split(",")
        self.names = names
        if names and self.n is None:
            self.n = len(names)

    def add_data(self, row):
        if self.n is None:
            self.n = len(row)

        if self.field is None:
            self.field = row[0].parent()
            assert self.field.is_field(), "only fields supported"

        assert len(row) == self.n
        self.data.append(tuple(row))

    def add_mono(self, es):
        self.monos.add(tuple(es))

    def add_mono_upto(self, maxes):
        for es in product(*[range(mx+1) for mx in maxes]):
            self.monos.add(es)

    def add_monos_degsum(self, degsum):
        for es in self.partition(degsum):
            self.add_mono(es)

    def add_monos_degsep(self, deg):
        for es in product(range(deg+1), repeat=self.n):
            self.add_mono(es)

    def partition(self, degsum, pos=0):
        for i in range(degsum + 1):
            if pos < self.n - 1:
                for sub in self.partition(degsum - i, pos + 1):
                    yield (i,) + sub
            else:
                yield (i,)

    def solve(self, order="deglex", groebner=False, debug=False):
        assert self.monos, "monos not added"
        #monos = list(self.monos)

        data = []
        for xs in self.data:
            row = []
            for es in self.monos:
                row.append(prod(x**e for x, e in zip(xs, es)))
            data.append(row)

        mat = self.matrix = matrix(data)

        if debug:
            print(f"matrix: {mat.nrows()} x {mat.ncols()} rank {mat.rank()}")

        if not self.names:
            names = ["x%d" % i for i in range(self.n)]

        self.R = PolynomialRing(
            mat.base_ring(), names=self.names, order=order
        )
        xs = self.R.gens()
        res = []
        rk = mat.right_kernel()
        if debug:
            print("kernel:", rk)
        for sol in rk.matrix():
            assert len(sol) == len(self.monos)
            poly = []
            for c, es in zip(sol, self.monos):
                mono = prod(x**e for x, e in zip(xs, es))
                poly.append(c * mono)
            poly = sum(poly)
            res.append(poly)

        if groebner and res:
            return Ideal(res).groebner_basis()
        return res
