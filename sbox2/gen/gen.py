class GeneratorCollector(object):
    def __init__(self):
        self.gens = {}
        self.new = None

    def register(self, func, name=None):
        if name is None:
            name = func.__name__
        assert name not in self.gens, "name collision"
        self.gens[name] = func
        return func

    def __getattr__(self, name):
        f = self.gens[name]
        return Sbox2Wrapper(f, self.new)

    make = None


class Sbox2Wrapper(object):
    def __init__(self, f, cls):
        self.f = f
        self.cls = cls

    def __call__(self, *a, **k):
        res = self.f(*a, **k)
        return self.cls(res)


gen = GeneratorCollector()
register = gen.register

