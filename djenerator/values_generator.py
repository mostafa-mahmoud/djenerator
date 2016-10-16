#!/usr/bin/env python
"""
This module has functions that generated random values for django fields.
"""
import datetime
from decimal import Decimal
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
        if special is True:
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


def generate_date_time(auto_now=False):
    if auto_now:
        return datetime.datetime.now()
    else:
        year = randint(1900, 2100)
        month = randint(1, 12)
        long_month = [1, 3, 5, 7, 8, 10, 12]
        day = 0
        if month in long_month:
            day = randint(1, 31)
        else:
            if month == 2:
                x = year
                leap_year = int((x % 4 == 0 and not x % 100 == 0)
                                or x % 400 == 0)
                day = randint(1, 28 + leap_year)
            else:
                day = randint(1, 30)
        hour = randint(0, 23)
        minute = randint(0, 59)
        second = randint(0, 59)
        microsecond = randint(0, 999999)
        return datetime.datetime(year, month, day, hour, minute,
                                 second, microsecond)


def generate_date(auto_now=False):
    return generate_date_time(auto_now).date()


def generate_time(auto_now=False):
    return generate_date_time(auto_now).time()


def generate_sentence(max_length, seperators=[' '], end_char=['.'],
                      exact=False):
    max_length -= bool(end_char)
    length = max_length
    #if not exact:
    #    length = randint(1, max_length)
    no_words = randint(1, (length + 1) / 2)
    average_word_length = (length - no_words + 1) / no_words * 2
    lengths = [randint(1, average_word_length) for _ in xrange(no_words)]
    tot = length - no_words + 1 - sum(lengths)
    if tot < 0:
        pass

    words = [generate_string(word_length, True, False, False, False,
                             False, True) for word_length in lengths[:-1]]
    words = map(lambda x: x + choice(seperators), words)
    words.append(generate_string(lengths[-1], True, False, False,
                                 False, False, True) + choice(end_char))
    return str.join('', words)


def generate_decimal(max_digits, decimal_places):
    integer_part_len = max_digits - decimal_places
    integer_part = generate_string(integer_part_len, False, False, True,
                                   False, False, False)
    decimal_part = generate_string(decimal_places, False, False, True,
                                   False, False, False)
    return Decimal('%s.%s' % (integer_part, decimal_part))


def generate_float(max_digits=50, decimal_places=30):
    return float(generate_decimal(max_digits, decimal_places))
