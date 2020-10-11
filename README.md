# Cry: SageMath/Python Toolkit for Cryptanalytic Research

This repository contains a bunch of various crypto-related algorithms implemented in Python 3 and SageMath. Pure Python code is located in cry/py package and can be imported from python code. The other modules must be imported from the SageMath interpreter.

The most significant part is formed by S-Box analysis algorithms, implemented in the cry.sbox2.SBox2 class, which is similar to from sage.crypto.SBox but is much more rich. Another cool S-Box library is [SboxU](https://github.com/lpp-crypto/sboxU) by Léo Perrin. It contains some more advanced algorithms, highly recommended!

**WARNING:** This library is not well-shaped yet and many things (including API and structure) may change in future. For now, I will try to keep compatability only for minor versions. That is, lock to the minor version if you use this package.

**NOTE** Before, this library was called *cryptools*, but since this name is used on PyPI, I decided to switch to *cry*, which is shorter.

Currently, there is no documentation but examples will be added soon.

## Installation

```bash
# for SageMath
$ sage pip install -U cry
# for python3
$ pip3 install -U cry
```

Previous python2 version (cryptools) can be found in the tag *py2-arhived*.

## Development

For development or building this repository, [poetry](https://python-poetry.org/) is needed.
