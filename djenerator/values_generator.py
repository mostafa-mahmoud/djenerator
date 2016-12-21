#!/usr/bin/env python
"""
This module has functions that generated random values for django fields.
"""
import datetime
import pytz
import os
import struct
import uuid
import zlib
from decimal import Decimal
from itertools import ifilter
from itertools import imap
from itertools import islice
from random import choice
from random import randint
from random import shuffle


def generate_integer(bits=32, negative_allowed=True):
    length = randint(1, bits - 1) - 1
    positive = True
    if negative_allowed:
        positive = choice([True, False])
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
    left = randint(1, min(3, max_length - 4 * parts))
    number = [str(randint(int(bool(parts)), 10 ** left - 1))]
    number.extend('%.3d' % randint(0, 999) for _ in xrange(parts))
    return str.join(',', number)


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
        if (isinstance(special, list) or isinstance(special, tuple) or
           isinstance(special, set)):
            allowed_characters.extend(special)
        elif special is True:
            allowed_characters.extend(chars_in_range('!', '/'))
            allowed_characters.extend(chars_in_range(':', '@'))
            allowed_characters.extend(chars_in_range('[', '`'))
            allowed_characters.extend(chars_in_range('{', '~'))
    length = max_length
    if not exact_len:
        length = randint(1 - null_allowed, max_length)
    return str.join('', [choice(allowed_characters) for _ in xrange(length)])


def generate_date_time(auto_now=False, tz=None):
    if auto_now:
        if tz:
            return datetime.datetime.now(tzinfo=pytz.timezone(tz))
        else:
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
        if tz:
            return datetime.datetime(year, month, day, hour, minute,
                                     second, microsecond,
                                     tzinfo=pytz.timezone(tz))
        else:
            return datetime.datetime(year, month, day, hour, minute,
                                     second, microsecond)


def generate_date(auto_now=False, tz=None):
    return generate_date_time(auto_now, tz).date()


def generate_time(auto_now=False, tz=None):
    return generate_date_time(auto_now, tz).time()


def generate_text(max_length, exact=False):
    sentences = randint(1, max((max_length + 39) / 60, (max_length + 39) / 40))
    rem_length = max_length
    text = []
    for idx in xrange(sentences):
        length = rem_length / (sentences - idx)
        length = min((rem_length) / (sentences - idx) + int(bool(idx)),
                     randint(2, 7) * 6, rem_length - int(bool(idx)))
        if length > 0:
            text.append(generate_sentence(length, exact=exact))
            rem_length -= len(text[-1]) + int(bool(idx))
    return str.join(' ', text)


def generate_sentence(max_length, lower=True, upper=False, digits=False,
                      seperators=[' '], end_char=['.'], exact=False):
    if max_length < 3:
        return generate_string(max_length, lower, upper, digits, special=False,
                               null_allowed=True, exact_len=True)
    if not end_char:
        end_char = ['']
    max_length -= bool(end_char) and bool(any(char for char in end_char))
    length = max_length
    if not exact and length >= 5:
        length = randint(1, max_length)
    a = 5.0 / 6.0
    no_words = randint(1, int(2 * length * (1 - a) + 1 - 2 * a) + 1)
    max_word_length = int((length + 1) / no_words * a)
    lengths = [randint(1, max_word_length) for _ in xrange(no_words)]
    lengths.sort()
    tot = length - no_words + 1 - sum(lengths)
    while tot < 0 and lengths:
        tot += lengths.pop()
        tot += int(bool(lengths))
        no_words -= 1
    if tot > 1 and (exact or randint(0, 1) == 0 or not lengths):
        lengths.append(tot - 1)
        no_words += 1
    shuffle(lengths)

    words = [generate_string(word_length, lower, upper, digits, False,
                             False, True) for word_length in lengths]
    words_endings = [choice(seperators) for _ in xrange(len(lengths) - 1)]
    words_endings.append(choice(end_char))
    words = map(lambda t: t[0] + t[1], zip(words, words_endings))
    return str.join('', words)


def generate_decimal(max_digits, decimal_places):
    integer_part_len = max_digits - decimal_places
    integer_part = generate_string(integer_part_len, False, False, True,
                                   False, False, False)
    integer_part = str(int(integer_part))
    decimal_part = generate_string(decimal_places, False, False, True,
                                   False, False, False)
    return Decimal('%s.%s' % (integer_part, decimal_part))


def generate_float(max_digits=50, decimal_places=30):
    return float(generate_decimal(max_digits, decimal_places))


def generate_email(max_length, exact_len=False):
    if max_length < 7:
        return ''
    dom = ['com', 'de', 'it', 'uk', 'edu', 'es', 'fr', 'eg', 'ru', 'pl', 'org',
           'es', 'pk', 'jo', 'fe', 'se', 'tr', 'ch']
    tot_length = (max_length - 5) / 2
    parts = [generate_string(tot_length, lower=True, upper=False, digits=True,
                             special=False, null_allowed=False,
                             exact_len=exact_len) for _ in xrange(2)]

    return '%s@%s.%s' % (parts[0], parts[1], choice(dom))


def generate_url(max_length):
    if max_length < 16:
        return ''
    dom = ['com', 'de', 'it', 'uk', 'edu', 'es', 'fr', 'eg', 'ru', 'pl', 'org',
           'es', 'pk', 'jo', 'fe', 'se', 'tr', 'ch']
    domain = generate_sentence(randint(3, max_length - 11), lower=True,
                               digits=True, seperators=['.'], end_char=['.'])
    domain += choice(dom)
    suburl = ''
    if len(domain) + 8 < max_length:
        suburl = choice(['', '/'])
    if randint(1, 6) > 2 and len(domain) + len(suburl) + 10 < max_length:
        suburl = '/'
        suburl += generate_sentence(max_length - len(domain) - 8 - len(suburl),
                                    digits=True, seperators=[''],
                                    end_char=['/', ''])
    return '%s://%s%s' % (choice(['http', 'ftp', 'https']), domain, suburl)


def generate_uuid():
    return uuid.uuid4()


def generate_file_path():
    walk = os.walk(os.getcwd())
    flt = ifilter(lambda path: not any(p.startswith('.')
                                       for p in path[0]), walk)
    flt = imap(lambda path: path[0], flt)
    flt = islice(flt, 1000)
    return choice(list(flt))


def generate_file_name(length=15, extension=''):
    return "%s.%s" % (generate_string(length - len(extension) - 1,
                                      digits=False, special=['_']), extension)


def generate_png(width=128, height=128):
    buf = b''.join([struct.pack('>I', (randint(0, (1 << 24) - 1) << 8) | 0xff)
                    for _ in xrange(width * height)])

    width_byte_4 = width * 4
    raw_data = b''.join(b'\x00' + buf[span:span + width_byte_4]
                        for span in range((height - 1) * width_byte_4, -1,
                                          - width_byte_4))

    def png_pack(png_tag, data):
        chunk_head = png_tag + data
        return (struct.pack("!I", len(data)) +
                chunk_head +
                struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))

    return b''.join([
        b'\x89PNG\r\n\x1a\n',
        png_pack(b'IHDR', struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)),
        png_pack(b'IDAT', zlib.compress(raw_data, 9)),
        png_pack(b'IEND', b'')])
