class GeneratorCollector(object):
    def __init__(self):
        self.gens = {}
        self.SBox2 = self.new = None

    def register(self, func, name=None):
        if name is None:
            name = func.__name__
        assert name not in self.gens, "name collision"
        self.gens[name] = func
        return func

    def __getattr__(self, name):
        if name not in self.gens:
            raise AttributeError(f"No generator with name {name}")
        f = self.gens[name]
        return SBox2Wrapper(f, self.new)

    def __hasattr__(self, name):
        return name in self.__dict__ or name in self.gens

    make = None


class SBox2Wrapper(object):
    def __init__(self, f, cls):
        self.f = f
        self.cls = cls

    def __call__(self, *a, **k):
        res = self.f(*a, **k)
        if not isinstance(res, self.cls):
            res = self.cls(res)
        return res


gen = GeneratorCollector()
register = gen.register
