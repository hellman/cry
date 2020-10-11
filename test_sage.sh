#!/bin/bash
# prereq:
# sage -pip install -U pytest

sage -sh -c 'pytest --doctest-modules cry/ tests_sage/'
