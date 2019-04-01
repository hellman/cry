#-*- coding:utf-8 -*-

import sys
import ast
from hashlib import sha1

from cryptools.sagestuff import loads, dumps


def pickle_cache(fn):
    fname = ".cache:%s:%s" % (fn.func_name, permanent_func_hash(fn)[:16])
    try:
        res = loads(open(fname).read())
        print >>sys.stderr, "[i] reusing %s" % fname
        return res
    except (EOFError, IOError):
        print >>sys.stderr, "[i] calculating %s" % fname
        result = fn()
        open(fname, "wb").write(dumps(result))
        return result


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
            print >>sys.stderr, "[i] reusing %s (%s)" % (fname, new_hash)
        else:
            print >>sys.stderr, "[i] calculating %s (%s)" % (fname, new_hash)
            result = fn()
            print >>sys.stderr, "[i] saving %s (%s)" % (fname, new_hash)
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
            print >>sys.stderr, "[i] cache incomplete %s: %s items" % (fname, len(res))
            raise EOFError("Cache incomplete")
        print >>sys.stderr, "[i] reusing %s: %s items" % (fname, len(res))
        return res
    except (EOFError, IOError):
        print >>sys.stderr, "[i] calculating %s" % fname
        fo = open(fname, "wb")
        res = []
        for obj in fn():
            fo.write(repr(obj) + "\n")
            res.append(obj)
        fo.write(":cache:finished:")
        fo.close()
        print >>sys.stderr, "[i] calculated %s: %s items" % (fname, len(res))
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
    return sha1(str(res)).hexdigest()
