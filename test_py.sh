#!/bin/bash
# prereq:
# pip3 install -U pytest

pytest --doctest-modules cry/py tests_py/
