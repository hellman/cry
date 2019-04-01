#-*- coding:utf-8 -*-

bases = []

def sbox_mixin(cls):
    bases.append(cls)
    return cls
