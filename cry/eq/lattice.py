from sage.all import matrix, ZZ, QQ, RR, copy, lcm, gcd

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
        """
        coef = self.get_apf_LLL(delta=delta)
        return int(coef.sqrt() * abs(self.det)**(1/RR(self.n)))

    def get_apf_LLL(self, delta=0.75):
        """
        Approximation factor of lattice is the bound on how much longer
        can be the first output vector than the real shortest vector.
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


def test_SECCON_2020_sharsable():
    from bint import Bin

    # SECCON 2020 - sharsable
    n = 142793817321992828777925840162504083304079023834001118099549928854335392622287928254035247188624975743042449746066633491912316354241339908190889792327014012472372654378644158878787350693992259970146885854641856991605625756536504266728483088687985429310233421251081614258665472164668993082471923690196082829593  # noqa
    e1, c1 = [
        82815162880874815458042429141267540989513396527359063805652845923737062346339641683097075730151688566721221542188377672708478777831586255213972947470222613130635483227797717393291856129771004300757155687587305350059401683671715424063527610425941387424425367153041852997937972925839362190900175155479532582934, # noqa
        108072697038795075732704334514926058617161875495016327352871122917196026504758904760148391499245235850616838765611460630089577948665981247735905622903872682862860306107704253287284051312867625831877418240290183661755993649928399992531008191618616452091127799880839665225093055618092869662205901927957599941568,  # noqa
    ]
    e2, c2 = [
        84856171747859965508406237198459622554468224770252249975158471902036102010991476445962577679301719179079633469099994226630172251817358960347828156301869905575867853640850107406452911333646573296923235424617864473580743418995994067645338437540627399276292679100115018844287273293945121023787594592185295794983,  # noqa
        101960082023987498941061751761131381167414505957511290567652602520714324823481487410890478130601013005035303795327512367595187718926017321227779179404306882163521882309833982882201152721855538832465833869251505131262098978117904455226014402089126682222497271578420753565370375178303927777655414023662528363360,  # noqa
    ]

    m = Lattice([
        [e1, 1, 0],
        [e2, 0, 1],
        [n,  0, 0],
    ])
    m.set_bounds([n**0.66, n**0.16, n**0.16], precision=1)
    d1, d2 = m.LLL().apply_map(abs)[0][1:]
    msg = int(pow(c1, int(d1), n) * pow(c2, int(d2), n) % n)
    assert Bin(msg).bytes == b'SECCON{sh4r4bl3_r54_1s_useful?}'

    assert d1, d2 == m.BKZ().apply_map(abs)[0][1:]


def test_bound():
    from random import randrange
    for delta in (0.4, 0.5, 0.75, 0.9, 0.99):
        for n in (10, 20, 50, 100, 200, 256, 512, 1024, 2048):
            for d in (2, 3, 5, 10, 15):
                m = Lattice([
                    [randrange(2**n) for _ in range(d)]
                    for _ in range(d)
                ])
                m.set_bounds([2**randrange(n) for _ in range(d)], precision=1)
                bound = m.get_bound_LLL()
                ml = m.LLL()
                norm = int(RR(ml[0].norm()))
                print(
                    "delta", delta, "n", n, "d", d,
                    "logs:",
                    int(norm).bit_length(), "<?", int(bound).bit_length())
                assert norm <= bound + 1


if __name__ == '__main__':
    test_SECCON_2020_sharsable()
    test_bound()
    print("tests ok!")
