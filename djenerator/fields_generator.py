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


def generate_ip():
    return str.join('.', [str(randint(0, 255)) for _ in xrange(4)])


def generate_comma_separated_int(max_length):
    parts = randint(0, (max_length - 1) / 4)
    number = ['%.3d' % randint(0, 999) for _ in xrange(parts)]
    left = randint(1, min(3, max_length - 4 * parts))
    return '%d,%s' % (randint(1, 10 ** left - 1), str.join(',', number))


def generate_string(max_length, lower=True, upper=True, digits=True,
                           special=True, null_allowed=False, exact_len=False):
    vascii = dict([(chr(n), n) for n in xrange(128)])
    allowed_characters = []
    chars_in_range = lambda beg, end: [chr(n) for n in xrange(vascii[beg],
                                                              vascii[end] + 1)]
    if lower:
        allowed_characters.extend(chars_in_range('a', 'z'))
    if upper:
        allowed_characters.extend(chars_in_range('A', 'Z'))
    if digits:
        allowed_characters.extend(chars_in_range('0', '9'))
    if special:
        if special == True:
            allowed_characters.extend(chars_in_range('!', '/'))
            allowed_characters.extend(chars_in_range(':', '@'))
            allowed_characters.extend(chars_in_range('[', '`'))
            allowed_characters.extend(chars_in_range('{', '~'))
        else:
            if special.__class__ == list:
                allowed_characters.extend(special)
    length = max_length
    if not exact_len:
        length = randint(1 - null_allowed, max_length)
    return str.join('', [choice(allowed_characters) for _ in xrange(length)])
