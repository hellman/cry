#!/bin/bash
# to run:
# sage -sh -c 'pip install nose'

# WARNING:
# sage wants to be imported before everything!
# need to add "import sage.all" to the beginning of sage/local/bin/nosetests ...

# ALSO:
# SageMath/local/lib/python3.7/site-packages/sage/interacts/all.py
# remove all imports

# sage ecosystem is a mess

sage -sh -c 'nosetests --with-doctest --all-modules -v'
