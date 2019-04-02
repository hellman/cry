import ast, pickle
from functools import wraps
import hashlib
H = lambda s: hashlib.sha256(s).hexdigest()

def ast_cache(filename_prefix):
    def deco(func):
        @wraps(func)
        def wrapper(*a, **k):
            cache_key = tuple(a) + tuple(sorted(k.items()))
            cache_key = H(str(cache_key))

            filename = filename_prefix + "." + cache_key
            try:
                lines = list(open(filename))
                assert lines[-1] == "EndCache"
                cache_exists = True
            except:
                cache_exists = False

            if cache_exists:
                res = ast.literal_eval(lines[1])
                # print "loaded cache"
                return res
            # print "computing & writing cache.."
            with open(filename, "w") as f:
                res = func(*a, **k)
                f.write("Cache: %s(%s; %s)\n" % (
                    func.__name__,
                    ", ".join(map(repr, a)),
                    ", ".join("%s=%r" % item for item in sorted(k.items()))
                ))
                assert ast.literal_eval(repr(res)) == res, "non-serializable res"
                f.write(repr(res) + "\n")
                f.write("EndCache")
            return res
        return wrapper
    return deco

def pypickle_cache(filename_prefix):
    def deco(func):
        @wraps(func)
        def wrapper(*a, **k):
            cache_key = tuple(a) + tuple(sorted(k.items()))
            cache_key = H(str(cache_key))

            filename = filename_prefix + "." + cache_key
            try:
                f = open(filename)
                f.readline()
                return pickle.load(f)
            except:
                pass

            with open(filename, "w") as f:
                res = func(*a, **k)
                f.write("Cache: %s(%s; %s)\n" % (
                    func.__name__,
                    ", ".join(map(repr, a)),
                    ", ".join("%s=%r" % item for item in sorted(k.items()))
                ))
                pickle.dump(res, f)
            return res
        return wrapper
    return deco
