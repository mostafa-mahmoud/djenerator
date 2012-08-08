#!/usr/bin/env python
"""
This module has functions that generated random values for django fields.
"""
from random import choice
from random import randint


def generate_integer(bits, negative_allowed=True):
    length = randint(1, bits - 1) - 1
    positive = True
    if negative_allowed:
        positive = bool(randint(0, 1))
    if positive:
        low = (1 << length)
        high = 2 * low - 1
        if low == 1:
            low = 0
        return randint(low, high)
    else:
        high = -(1 << length) - 1
        low = 2 * (high + 1)
        if high == -2:
            high = -1
        return randint(low, high)


def generate_big_integer():
    return generate_integer(64)


def generate_int():
    return generate_integer(32)


def generate_small_integer():
    return generate_integer(16)


def generate_positive_integer():
    return generate_integer(32, False)


def generate_positive_small_integer():
    return generate_integer(16, False)


def generate_boolean(null_allowed=False):
    res = randint(0, 1 + int(null_allowed))
    if res < 2:
        return bool(res)
