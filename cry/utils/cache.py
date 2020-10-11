import time, os, logging
import ast
from functools import wraps

import hashlib
H = lambda s: hashlib.sha256(s).hexdigest()

from cry.sagestuff import loads, dumps

log = logging.getLogger("cry.cache")

# old
# def pickle_cache(fn):
#     fname = ".cache:%s:%s" % (fn.func_name, permanent_func_hash(fn)[:16])
#     try:
#         res = loads(open(fname).read())
#         msg("[i] reusing %s" % fname)
#         return res
#     except (EOFError, IOError):
#         msg("[i] calculating %s" % fname)
#         result = fn()
#         open(fname, "wb").write(dumps(result))
#         return result


def msg(*args):
    log.debug(" ".join(map(str, args)))


def sage_cache(path):
    if not os.path.exists(path):
        os.makedirs(path)

    def deco(func):
        @wraps(func)
        def wrapper(*a, **k):
            cache_key = tuple(a) + tuple(sorted(k.items()))
            cache_key = H(str(cache_key))

            filename = os.path.join(path, cache_key)
            try:
                f = open(filename)
                while True:
                    line = f.readline()
                    if line.strip() == "===":
                        break
                    if not line.strip():
                        raise EOFError()
                return loads(f.read())
            except:
                pass

            with open(filename, "w") as f:
                t0 = time.time()
                res = func(*a, **k)
                t1 = time.time()
                # some metadata
                f.write("cache: %s(%s; %s)\n" % (
                    func.__name__,
                    ", ".join(map(repr, a)),
                    ", ".join("%s=%r" % item for item in sorted(k.items())),
                ))
                f.write("key: %s\n" % cache_key)
                f.write("time: %r\n" % (t1 - t0))
                f.write("===\n")
                f.write(dumps(res))
            return res
        return wrapper
    return deco


def single_cache(filename=None):
    def cacher(fn):
        fname = filename or ".cache:%s" % fn.func_name

        hash = None
        try:
            hash, result = loads(open(fname).read())
        except (EOFError, IOError):
            pass

        new_hash = permanent_func_hash(fn)
        if hash == new_hash:
            msg("[i] reusing %s (%s)" % (fname, new_hash))
        else:
            msg("[i] calculating %s (%s)" % (fname, new_hash))
            result = fn()
            msg("[i] saving %s (%s)" % (fname, new_hash))
            open(fname, "wb").write(dumps((new_hash, result)))
        return result
    return cacher


def single_load(filename):
    return loads(open(filename).read())[1]


def line_cache(fn):
    fname = ".cache:%s:%s" % (fn.func_name, permanent_func_hash(fn)[:16])
    try:
        res = []
        for line in open(fname):
            line = line.strip()
            if line == ":cache:finished:":
                break
            if line:
                res.append(ast.literal_eval(line))
        else:
            msg("[i] cache incomplete %s: %s items" % (fname, len(res)))
            raise EOFError("Cache incomplete")
        msg("[i] reusing %s: %s items" % (fname, len(res)))
        return res
    except (EOFError, IOError):
        msg("[i] calculating %s" % fname)
        fo = open(fname, "wb")
        res = []
        for obj in fn():
            fo.write(repr(obj) + "\n")
            res.append(obj)
        fo.write(":cache:finished:")
        fo.close()
        msg("[i] calculated %s: %s items" % (fname, len(res)))
        return res


def permanent_func_hash(fn):
    res = []
    code = fn.func_code
    for attr in dir(code):
        if attr == "co_consts":
            for c in getattr(code, attr):
                if "at 0x" in str(c):
                    continue
                res.append(c)
            continue
        if attr.startswith("co_") and attr != "co_firstlineno":
            res.append(getattr(code, attr))
    for g in code.co_names:
        v = fn.func_globals.get(g, None)
        if not callable(v):
            res.append(str(fn.func_globals.get(g, None)))
    return H(str(res))
