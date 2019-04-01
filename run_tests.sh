#!/bin/bash
# to run:
# sage -sh -c 'pip install nose'

# WARNING:
# sage wants to be imported before everything!
# need to add "import sage.all" to the beginning of sage/local/bin/nosetests ...

sage -sh -c 'nosetests --with-doctest --all-modules -v'
