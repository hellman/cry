from cry.sagestuff import (
    inverse_mod, floor, power_mod, ceil,
    Zmod, PolynomialRing, RR, log, gcd, lcm, ZZ
)
import warnings

from binteger import Bin


class RSA:
    def __init__(self, n=None, *, p=None, q=None, e=0x10001, d=None, phi=None):
        self.n = self.p = self.q = self.e = self.d = self.phi = self.carm = None
        self.update(n=n, p=p, q=q, e=e, d=d, phi=phi)

        self._n_sqrt = None

    def update(self, n=None, p=None, q=None, e=None, d=None, phi=None):
        if n is not None:
            self.n = int(n)
        if p is not None:
            self.p = int(p)
        if q is not None:
            self.q = int(q)
        if e is not None:
            self.e = int(e)
        if d is not None:
            self.d = int(d)
        if phi is not None:
            self.phi = phi

        if self.p and self.q:
            self.phi = self.n - self.p - self.q + 1
            self.carm = lcm(self.p-1, self.q-1)
            self.d = inverse_mod(self.e, self.phi)

    def decrypt(self, msg):
        msg = Bin(msg).int
        msg = power_mod(msg, self.d, self.n)
        return Bin(msg).bytes

    def n_sqrt(self):
        if self._n_sqrt is None:
            self._n_sqrt = floor(ZZ(self.n).sqrt())
        return self._n_sqrt

    def polyring(self, n=None, names=None):
        if isinstance(names, str):
            assert n is None
            names = names.replace(",", " ").split()
        elif isinstance(names, (tuple, list)):
            assert n is None
        else:
            if n is None:
                n = 1
            assert names is None
            names = list("xyzwuv")[:n]
        PR = PolynomialRing(Zmod(self.n), names=",".join(names))
        return (PR,) + tuple(PR.gens())

    def bound_primes_from_approximate_sum(self, sumpq, eps):
        """
        p + q = s + e, 0 <= e < eps
        p + n/p = s+e
        p**2 - (s+e)*p + n = 0

        p = (s + e - sqrt((s + e)**2 - 4*n)) / 2
        q = (s + e + sqrt((s + e)**2 - 4*n)) / 2
        """
        n = self.n
        if sumpq**2 <= 4*n:
            mx = sumpq + eps
            sumpq = ceil(ZZ(4*n).sqrt())
            eps = mx - sumpq
        assert (sumpq + eps)**2 > 4*n
        assert eps >= 0

        Dmin = floor(ZZ(sumpq**2 - 4 * n).sqrt())
        Dmax = ceil(ZZ((sumpq + eps)**2 - 4 * n).sqrt())

        p_max = (sumpq - Dmin) // 2
        p_min = (sumpq + eps - Dmax) // 2
        assert p_min <= p_max

        q_min = (sumpq + Dmin) // 2
        q_max = (sumpq + eps + Dmax) // 2
        assert q_min <= q_max

        # do not have to hold
        if not (p_max * q_min <= n) or not(p_min * q_max >= n):
            warnings.warn("strangely, bounds can be improved")
            q_min = max(q_min, n // p_max + 1)
            q_max = min(q_max, n // p_min)
        return (p_min, p_max), (q_min, q_max)

    def factor_with_prime_hint(self, low_mod=None, bounds=None, beta=0.49):
        """
        """
        if low_mod is None:
            low_mod = 0, 1
        low, mod = low_mod
        assert 0 <= low < mod

        if bounds is None:
            bounds = 0, self.n_sqrt()
        pmin, pmax = bounds

        if beta < 0.5:
            assert pmax <= self.n_sqrt(), \
                "upper bound must be <= sqrt(n) when beta < 0.5"
        else:
            assert pmin >= self.n_sqrt(), \
                "lower bound must be >= sqrt(n) when beta >= 0.5"
        assert 1 <= pmin <= pmax

        # next value hitting low % mod
        if pmin % mod <= low:
            pmin = pmin - pmin % mod + low
        else:
            pmin = pmin - pmin % mod + mod + low

        xmax = ZZ(pmax - pmin) // mod

        PR, x = self.polyring()
        poly = (mod * x + pmin).monic()

        # for debugging
        # global p
        # assert p % mod == low
        # sol = (p-pmin)//mod
        # print("sol size", ZZ(sol).nbits(), "<xmax?", 0 <= sol <= xmax)
        # print(poly.subs(x=sol) % p )
        # print("poly", poly)

        # X = 1/2 n**(beta**2/degree - epsilon)
        # log_n 2X = beta**2 - epsilon
        # epsilon = beta**2 - log_n 2X
        epsilon = beta**2 - RR(log(2*xmax, self.n))
        assert epsilon > 0, "impossible attack"

        roots = poly.small_roots(X=xmax, beta=beta, epsilon=epsilon)
        for sol in roots:
            p = int(poly.subs(x=sol))
            p = abs(gcd(p, self.n))
            if 1 < p < self.n:
                q = self.n // p
                assert self.n == p * q, "multi-prime? ouch"
                self.update(p=p, q=q)
                break
        else:
            raise RuntimeError("attack failed")
        return p, q
