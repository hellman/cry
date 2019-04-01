# SageMath/Python Toolkit for Cryptanalytic Research

This repository contains a bunch of various crypto-related algorithms implemented in Python 2 and SageMath. Pure Python code is located in cryptools.py package and can be imported from python code. The other modules must be imported from the SageMath interpreter.

The most significant part is formed by S-Box analysis algorithms, implemented in the cryptools.sbox2.SBox2 class, which inherits from sage.crypto.SBox. 

WARNING: It is not well-shaped yet and many things (including API and structure) may change in future.

Currently, there is no documentation but examples will be added soon.
