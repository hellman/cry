import sys

from cry.sagestuff import matrix_plot
from cry.matrix import mat_min, mat_max, mat_distribution


def save_plot(mat, fname, **kwargs):
    print("[i] Saving %s" % fname, file=sys.stderr)
    print(
        "min %d max %d: distrib %s\n" %
        (mat_min(mat), mat_max(mat), mat_distribution(mat)),
        file=sys.stderr
    )

    absolute = kwargs.pop("abs", False)
    if absolute:
        for y in range(mat.nrows()):
            for x in range(mat.ncols()):
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
    print("[i] Saving %s" % fname, file=sys.stderr)
    m = s.lat()
    absolute = kwargs.pop("abs", False)
    if absolute:
        for y in range(m.nrows()):
            for x in range(m.ncols()):
                m[y, x] = abs(m[y, x])
    return save_plot(m, fname, **kwargs)


def save_plot_ddt(s, fname, **kwargs):
    print("[i] Saving %s" % fname, file=sys.stderr)
    m = s.ddt()
    absolute = kwargs.pop("abs", False)
    if absolute:
        for y in range(m.nrows()):
            for x in range(m.ncols()):
                m[y, x] = abs(m[y, x])
    return save_plot(m, fname, **kwargs)
