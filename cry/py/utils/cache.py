#-*- coding:utf-8 -*-

import sys
import ast, pickle, marshal
import random
from functools import wraps
import hashlib
H = lambda s: hashlib.sha256(s).hexdigest()

def truncrepr(a, limit=128):
    s = repr(a)
    if len(s) > limit:
        s = s[:limit] + "..."
    return s

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
                    ", ".join(map(truncrepr, a)),
                    ", ".join("%s=%s" % (kk, truncrepr(vv)) for kk, vv in sorted(k.items()))
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
                    ", ".join(map(truncrepr, a)),
                    ", ".join("%s=%s" % (kk, truncrepr(vv)) for kk, vv in sorted(k.items()))
                ))
                pickle.dump(res, f)
            return res
        return wrapper
    return deco



def marshal_cache_iter(filename_prefix_or_func):
    if isinstance(filename_prefix_or_func, str):
        filename_prefix = filename_prefix_or_func
    else:
        filename_prefix = filename_prefix_or_func.__name__

    def deco(func):
        @wraps(func)
        def wrapper(*a, **k):
            cache_key = tuple(a) + tuple(sorted(k.items()))
            cache_key = H(str(cache_key))

            filename = filename_prefix + "." + cache_key
            try:
                f = open(filename)
                info = f.readline()
                assert info.startswith("Cache: ")
                token = marshal.load(f)
                while True:
                    obj = marshal.load(f)
                    if obj == token:
                        print >>sys.stderr, "Success loading cache:", func.__name__, filename
                        return
                    yield obj
            except KeyboardInterrupt:
                print >>sys.stderr, "KB received, raising..."
                raise
            except Exception as err:
                print >>sys.stderr, "Error loading cache:", func.__name__, filename, ":", err

            token = "%064x" % random.randrange(2**256)
            with open(filename, "w") as f:
                f.write("Cache: %s(%s; %s)\n" % (
                    func.__name__,
                    ", ".join(map(truncrepr, a)),
                    ", ".join("%s=%s" % (kk, truncrepr(vv)) for kk, vv in sorted(k.items()))
                ))
                f.flush()
                marshal.dump(token, f)
                for res in func(*a, **k):
                    marshal.dump(res, f)
                    yield res
                marshal.dump(token, f)
            return
        return wrapper

    if isinstance(filename_prefix_or_func, str):
        return deco
    else:
        return deco(filename_prefix_or_func)
