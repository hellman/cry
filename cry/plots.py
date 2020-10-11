#-*- coding:utf-8 -*-

import sys
from cryptools.sagestuff import matrix_plot
from cryptools.matrix import mat_min, mat_max, mat_distribution


def save_plot(mat, fname, **kwargs):
    print >>sys.stderr, "[i] Saving %s" % fname
    print >>sys.stderr, "min %d max %d: distrib %s\n" % (mat_min(mat), mat_max(mat), mat_distribution(mat))

    absolute = kwargs.pop("abs", False)
    if absolute:
        for y in xrange(mat.nrows()):
            for x in xrange(mat.ncols()):
                mat[y, x] = abs(mat[y, x])

    opts = dict(
        colorbar=True,
        figsize=15,
        cmap="gist_earth_r"
    )
    opts.update(kwargs)

    plt = matrix_plot(mat, **opts)
    plt.save(fname)
    return plt


def save_plot_lat(s, fname, **kwargs):
    print >>sys.stderr, "[i] Saving %s" % fname
    m = s.lat()
    absolute = kwargs.pop("abs", False)
    if absolute:
        for y in xrange(m.nrows()):
            for x in xrange(m.ncols()):
                m[y, x] = abs(m[y, x])
    return save_plot(m, fname, **kwargs)


def save_plot_ddt(s, fname, **kwargs):
    print >>sys.stderr, "[i] Saving %s" % fname
    m = s.ddt()
    absolute = kwargs.pop("abs", False)
    if absolute:
        for y in xrange(m.nrows()):
            for x in xrange(m.ncols()):
                m[y, x] = abs(m[y, x])
    return save_plot(m, fname, **kwargs)
