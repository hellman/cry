from cry.sagestuff import matrix, ZZ, QQ, RR, copy, lcm, gcd

INF = float("+inf")


class Lattice:
    """
    Simple wrapper for LLL/BKZ.

    Main improvement is easy weighting.
    :meth:`set_bounds` allows to set approximate bounds for resulting
    vector's coordinates. This means that columns must be scaled
    inverse-proportional to bounds. LLL can work with QQ, so usually
    scaling can be done by multiplying columns by 1/w_i. However, BKZ only
    works for ZZ. This can be overcome by pre-multiplying everything by
    lcm of the bounds and then multiplying by 1/w_i keeps us in ZZ.
    Since bounds do not have to be precise, we can keep only few MSBs,
    to make lcm smaller. This is an optional argument for :meth:`set_bounds`,
    which by default is 8. On practice, 1 bit of precision is sufficient
    for most cases.

    In addition, after setting bounds, this wrapper allows to compute the bound
    given by LLL (function of the determinant) and/or the approximation factor.
    """
    def __init__(self, *args):
        self.matrix = matrix(*args)
        assert self.matrix.base_ring() in (ZZ, QQ)
        self.n = self.matrix.nrows()
        self.m = self.matrix.ncols()

        # bounds are relative
        self.set_bounds((1,) * self.matrix.ncols())

    def set_bounds(self, bounds, precision=8):
        assert precision >= 1, "less than 1 bit of precision?"
        assert len(bounds) == self.matrix.ncols()
        self.bounds = tuple(int(b) for b in bounds)
        self.precision = precision

        lst = []
        for b in self.bounds:
            b = int(b)
            s = max(0, int(b).bit_length() - precision)
            b = (b >> s) << s
            lst.append(b)
        g = gcd(lst)
        lst = [b // g for b in lst]
        l = lcm(lst)
        self.weights = tuple(l // b for b in lst)

        self._m_scaled = None
        self._m_scaled_reduced = None
        self._m_result = None

        self._det = None

    @property
    def matrix_scaled(self):
        assert self.matrix.ncols() == len(self.bounds) == len(self.weights)
        if self._m_scaled is None:
            self._m_scaled = copy(self.matrix)

            for x, w in enumerate(self.weights):
                col = w * self._m_scaled.column(x)
                self._m_scaled.set_column(x, col)
        return self._m_scaled

    @property
    def det(self):
        if self._det is None:
            self._det = self.matrix_scaled.determinant()
        return self._det

    def get_bound_LLL(self, delta=0.75):
        """
        Returns the bound on the first output vector (as a function of the
        determinant).
        https://en.wikipedia.org/wiki/Lenstra%E2%80%93Lenstra%E2%80%93Lov%C3%A1sz_lattice_basis_reduction_algorithm#Properties_of_LLL-reduced_basis
        """
        coef = self.get_apf_LLL(delta=delta)
        return int(coef.sqrt() * abs(self.det)**(1/RR(self.n)))

    def get_apf_LLL(self, delta=0.75):
        """
        Approximation factor of lattice is the bound on how much longer
        can be the first output vector than the real shortest vector.
        https://en.wikipedia.org/wiki/Lenstra%E2%80%93Lenstra%E2%80%93Lov%C3%A1sz_lattice_basis_reduction_algorithm#Properties_of_LLL-reduced_basis
        """
        return (QQ(4)/(4 * delta - 1))**(RR(self.n-1)/2.0)

    @property
    def matrix_result(self):
        assert self.matrix.ncols() == len(self.bounds) == len(self.weights)
        assert self._m_scaled_reduced is not None, "no result yet"
        if self._m_result is None:
            self._m_result = copy(self._m_scaled_reduced)
            for x, w in enumerate(self.weights):
                col = [v // w for v in self._m_result.column(x)]
                self._m_result.set_column(x, col)
        return self._m_result

    def LLL(self, *args):
        self._m_scaled_reduced = self.matrix_scaled.LLL(*args)
        return self.matrix_result

    def BKZ(self, *args):
        self._m_scaled_reduced = self.matrix_scaled.BKZ(*args)
        return self.matrix_result
