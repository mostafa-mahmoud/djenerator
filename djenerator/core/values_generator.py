"""
This module has functions that generated random values for django fields.
"""
import datetime
import math
import os
import random
import struct
import uuid
import zlib
from decimal import Decimal
from itertools import islice

from django.utils.text import slugify

from .exceptions import InconsistentDefinition
from .utils import choices, get_timezone


def generate_positive_log(mx):
    return min(mx, int(round(math.exp(math.log(mx) * random.random()))))


def generate_integer(bits=32, negative_allowed=True, mn=None, mx=None, step=1):
    if mn is not None and mx is not None:
        assert mn <= mx, (mn, mx)

    positive_allowed = mx is None or math.floor(mx / step) >= 0
    negative_allowed = (
        negative_allowed and (mn is None or math.ceil(mn / step) < 0)
    )
    assert negative_allowed or positive_allowed,\
        "No values are allowed with the given constraints"
    if negative_allowed and positive_allowed:
        positive = random.choice([True, False])
    else:
        positive = positive_allowed and not negative_allowed

    if positive:
        mx = mx or (2 ** (bits - 1) - 1)
        mn = max(mn or 0, 0)
        mx = math.floor(mx / step)
        mn = math.ceil(mn / step)
        assert mn <= mx, "No values are allowed with the given constraints"

        return (generate_positive_log(mx - mn) + mn) * step
    else:
        mn = mn or -(2 ** (bits - 1))
        mx = min(mx or -1, -1)
        mx = math.floor(mx / step)
        mn = math.ceil(mn / step)
        assert mn <= mx, "No values are allowed with the given constraints"
        return (mx - generate_positive_log(mx - mn)) * step


def generate_big_integer(mn=None, mx=None, step=1):
    return generate_integer(64, mn=mn, mx=mx, step=step)


def generate_int(mn=None, mx=None, step=1):
    return generate_integer(32, mn=mn, mx=mx, step=step)


def generate_small_integer(mn=None, mx=None, step=1):
    return generate_integer(16, mn=mn, mx=mx, step=step)


def generate_positive_big_integer(mn=None, mx=None, step=1):
    return generate_integer(64, False, mn=mn, mx=mx, step=step)


def generate_positive_integer(mn=None, mx=None, step=1):
    return generate_integer(32, False, mn=mn, mx=mx, step=step)


def generate_positive_small_integer(mn=None, mx=None, step=1):
    return generate_integer(16, False, mn=mn, mx=mx, step=step)


def generate_boolean(null_allowed=False):
    res = random.randint(0, 1 + int(null_allowed))
    if res < 2:
        return bool(res)


def generate_ip(v4=True, v6=True):
    ip4 = '.'.join([str(random.randint(0, 255)) for _ in range(4)])
    ip6 = ':'.join([hex(random.randint(0, 2 ** 16 - 1))[2:].upper()
                    for _ in range(8)])
    if v4 and v6:
        return random.choice([ip4, ip6])
    if v6:
        return ip6
    else:
        return ip4


def generate_comma_separated_int(max_length):
    parts = random.randint(0, (max_length - 1) // 4)
    left = random.randint(1, min(3, max_length - 4 * parts))
    number = [str(random.randint(int(bool(parts)), 10 ** left - 1))]
    number.extend('%.3d' % random.randint(0, 999) for _ in range(parts))
    return str.join(',', number)


def generate_string(
    max_length, min_length=1, lower=True, upper=True, digits=True, special=True
):
    allowed_characters = ""
    if lower:
        allowed_characters += "abcdefghijklmnopqrstuvwxyz"
    if upper:
        allowed_characters += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if digits:
        allowed_characters += "0123456789"
    if isinstance(special, (list, tuple, set, str)):
        allowed_characters += ''.join(special)
    elif special is True:
        allowed_characters += "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

    length = random.randint(min_length, max_length)
    return ''.join([random.choice(allowed_characters) for _ in range(length)])


def generate_date_time(auto_now=False, tz=None):
    if tz is not None:
        tz = get_timezone(tz)
    now = datetime.datetime.now(tz=tz)
    if auto_now:
        return now
    else:
        delta = generate_positive_log(3600 * 24 * 365 * 3)
        return datetime.datetime.fromtimestamp(now.timestamp() - delta, tz=tz)


def generate_date(auto_now=False, tz=None):
    return generate_date_time(auto_now, tz).date()


def generate_time(auto_now=False, tz=None):
    return generate_date_time(auto_now, tz).time()


def generate_dictionary():
    """
    Retrieve the list of words from the unix dictionary

    :rtype: List[Str]
    Returns: List of English words.
    """
    for fl in [os.path.join("usr", "dict", "words"),
               os.path.join("usr", "share", "dict", "words")]:
        if os.path.isfile(fl):
            with open(fl, "r") as f:
                words = f.read().split("\n")[:-1]
            words = list(filter(
                lambda x: len(x) in [3, 4, 5, 6, 7] and "'" not in x, words
            ))
    # precomputed list of random words in case the words file doesn't exist.
    words = [
        'Aerope', 'scowder', 'towmast', 'amla', 'choaty', 'Sosia', 'pagus',
        'gasper', 'mongery', 'pewing', 'chinkle', 'knyazi', 'darg', 'pomfret',
        'inure', 'reactor', 'phulwa', 'coseat', 'allege', 'attire', 'hardish',
        'expel', 'bounder', 'side', 'amidin', 'fogdom', 'chiefly', 'pontage',
        'valved', 'bib', 'postil', 'hominal', 'basidia', 'bobfly', 'barring',
        'retral', 'Laurus', 'unbosom', 'cooncan', 'Ophitic', 'lampers',
        'togate', 'doltish', 'awiggle', 'Scilla', 'lumbago', 'mirrory',
        'alkamin', 'tambour', 'Paulus', 'Succisa', 'Grewia', 'concha', 'ripup',
        'alloxan', 'eelfish', 'skookum', 'twee', 'clubbed', 'tow', 'khoja',
        'glazing', 'mulish', 'egilops', 'phallin', 'Kubanka', 'Kiowan',
        'becovet', 'Janus', 'incuse', 'adonite', 'mopus', 'baybush', 'proddle',
        'chol', 'Lolium', 'dull', 'dixie', 'becuna', 'brother', 'remould',
        'danger', 'prancy', 'collie', 'Alumel', 'admi', 'knockup', 'warsaw',
        'clue', 'bail', 'visaged', 'begowk', 'smiter', 'cityish', 'goli',
        'pokeout', 'Jambos', 'Dione', 'Sabuja', 'darter', 'wasty', 'insurge',
        'outre', 'surmise', 'Aniba', 'unsoled', 'grouper', 'sell', 'kickish',
        'pawkily', 'cytost', 'seraw', 'kanat', 'relish', 'pegbox', 'Sindhi',
        'Pravin', 'duet', 'uncost', 'swungen', 'hitchy', 'nidana', 'look',
        'Danny', 'canhoop', 'enhusk', 'ferrado', 'James', 'zaptieh', 'deva',
        'gaduin', 'sneezer', 'smout', 'clapnet', 'atter', 'thermit', 'Darin',
        'reif', 'Fidac', 'torpent', 'Alawi', 'prig', 'uranous', 'stenog',
        'datch', 'rewet', 'resaw', 'cleg', 'marcher', 'suimate', 'writhen',
        'ovology', 'upwound', 'myron', 'Picus', 'oration', 'protium',
        'ambrite', 'inflate', 'townee', 'octuple', 'Delbert', 'mix', 'Antonia',
    ]
    dic = {}
    for word in words:
        if len(word) not in dic.keys():
            dic[len(word)] = []
        dic[len(word)].append(word)
    return dic


WORDS_DICTIONARY = generate_dictionary()


def generate_text(max_length=None, min_length=0, sep=" "):
    max_length = max_length or 1000
    if max_length <= 8:
        return generate_sentence(max_length)

    sentences = random.randint(1, max(1, max_length // 40))

    lengths = [
        random.randint(5, min(40, max_length)) for _ in range(sentences)
    ]
    if sum(lengths) + max(len(lengths) - 1, 0) * len(sep) < min_length:
        rem = min_length - sum(lengths) - max(len(lengths) - 1, 0) * len(sep)
        if rem < 3:
            lengths[-1] += rem
        else:
            lengths.append(rem)

    res = sep.join((generate_sentence(length) for length in lengths))
    assert len(res) >= min_length and len(res) <= max_length,\
        (lengths, sum(lengths), min_length, max_length)
    return res

    # rem_length = max_length
    # text = []
    # for idx in range(sentences):
    #     length = rem_length // (sentences - idx)
    #     length = min((rem_length) // (sentences - idx) + int(bool(idx)),
    #                  random.randint(2, 7) * 6, rem_length - int(bool(idx)))
    #     if length > 0:
    #         text.append(generate_sentence(length, exact=exact))
    #         rem_length -= len(text[-1]) + int(bool(idx))
    # return str.join(' ', text)


# def generate_sentence(max_length, lower=True, upper=False, digits=False,
#                       seperator=' ', endchar=['.'], exact=False):
#     if max_length < 3:
#         return generate_string(max_length, lower, upper, digits,
#                                special=False, null_allowed=True,
#                                exact_len=True)
#     if not endchar:
#         endchar = ['']
#     # words = generate_dictionary()
#     max_length -= bool(endchar) and bool(any(endchar))

#     length = max_length
#     if not exact and length >= 5:
#         length = random.randint(1, max_length)
#     # total = ""
#     a = 5.0 / 6.0
#     no_words = random.randint(1, int(2 * length * (1 - a) + 1 - 2 * a) + 1)
#     max_word_length = int((length + 1) / no_words * a)
#     lengths = [random.randint(1, max_word_length) for _ in range(no_words)]
#     lengths.sort()
#     tot = length - no_words + 1 - sum(lengths)
#     while tot < 0 and lengths:
#         tot += lengths.pop()
#         tot += int(bool(lengths))
#         no_words -= 1
#     if tot > 1 and (exact or random.randint(0, 1) == 0 or not lengths):
#         lengths.append(tot - 1)
#         no_words += 1
#     random.shuffle(lengths)

#     words = [generate_string(word_length, lower, upper, digits, False,
#                              False, True) for word_length in lengths]
#     words_endings = [
#         random.choice(seperators) for _ in range(len(lengths) - 1)
#     ]
#     words_endings.append(random.choice(endchar))
#     words = map(lambda t: t[0] + t[1], zip(words, words_endings))
#     return str.join('', words)


def generate_sentence(length, seperators=" ", endchar="."):
    """
    Generate a sentence of a specific length, with specific seperators and
    ending character.
    """
    end = random.choice(endchar) if endchar else ""
    length -= len(end)

    res = ""
    while len(res) + int(bool(res)) < length:
        max_word_len = length - len(res) - int(bool(res))
        if res:
            res += random.choice(seperators)
        if max_word_len <= 2:
            for _ in range(max_word_len):
                res += random.choice("abcdefghijklmnopqrstuvwxyz")
            break
        else:
            res += random.choice(
                WORDS_DICTIONARY[random.randint(3, min(max_word_len, 7))]
            )
    while len(res) < length:
        res += random.choice("abcdefghijklmnopqrstuvwxyz")
    res = res[:length] + end
    return res


def generate_decimal(max_digits, decimal_places):
    integer_part_len = max_digits - decimal_places
    res = ""
    for _ in range(random.randint(0, integer_part_len)):
        res += str(random.randint(1 - int(bool(res)), 9))
    res = res or "0"
    res += "."
    for _ in range(random.randint(1, decimal_places)):
        res += str(random.randint(0, 9))
    if len(res) < max_digits + 1 and random.random() < 0.5:
        res = "-" + res

    return Decimal(res)


def generate_float(max_digits=30, decimal_places=20):
    return float(generate_decimal(max_digits, decimal_places))


def generate_domain_name(max_length=20):
    dom = ['com', 'de', 'it', 'uk', 'edu', 'es', 'fr', 'eg', 'ru',
           'pl', 'org', 'es', 'pk', 'jo', 'fe', 'se', 'tr', 'ch']
    end = '.' + random.choice(dom)
    return slugify(generate_sentence(
        max_length - len(end), seperators='-', endchar='.'
    ).lower()) + end


def generate_email(max_length, min_length=14, allowlist=None):
    if min_length < 14 or max_length < min_length:
        raise InconsistentDefinition(
            "An Email with the specified lengths is too short. Should "
            "be 14 <= min_length (%d) <= max_length (%d)" % (
                min_length, max_length
            )
        )
    domain = random.choice(allowlist) if allowlist else generate_domain_name(9)
    min_length -= len(domain) + 1
    max_length -= len(domain) + 1
    if max_length < 2:
        raise InconsistentDefinition(
            "The allowed domain names with the allowed length are too tight. "
            "Domain %s, remaining length: %d" % (domain, min_length)
        )

    email = slugify(generate_sentence(
        random.randint(max(min_length, 2), max_length), endchar=None
    )) + "@" + domain
    return email


def generate_url(
    max_length, min_length=16, schemas=["https", "http", "ftp", "ftps"]
):
    if min_length < 16 or max_length < min_length:
        raise InconsistentDefinition(
            "A Url with the specified lengths is too short. Should "
            "be 16 <= min_length (%d) <= max_length (%d)" % (
                min_length, max_length
            )
        )

    url = random.choice(schemas) + "://"

    domain = generate_domain_name(random.randint(6, min(max_length - 8, 30)))
    if len(url) + 4 + len(domain) < max_length:
        domain = random.choice(["www.", ""]) + domain
    url += domain

    max_length -= len(url)
    min_length -= len(url)
    if max_length == 0:
        return url
    elif max_length == 1:
        return url + "/"
    else:
        url += "/" + "/".join(map(
            slugify,
            generate_text(
                max_length - 1, min_length=min_length - 1, sep=""
            ).split(".")
        ))
    if len(url) < max_length and url[-1] != '/' and random.random() < 0.5:
        url += "/"
    return url


def generate_uuid():
    return uuid.uuid4()


def generate_file_path(root=os.getcwd(), max_length=256, min_length=1):
    walk = os.walk(root)
    flt = list(filter(
        lambda path: (
            not any(p.startswith('.') for p in path[0]) and
            min_length <= len(path[0]) <= max_length
        ), walk
    ))
    flt = list(map(lambda path: path[0], flt))
    flt = list(islice(flt, 1000))
    return random.choice(flt)


def generate_file_name(max_length=15, min_length=6, extensions=[]):
    if extensions:
        extension = random.choice(extensions)
    else:
        extension = ""
    return generate_sentence(
        random.randint(
            max(1, min_length - len(extension)), max_length - len(extension)
        ), seperators="-_", endchar=None
    ) + extension


def png_pack(png_tag, data):
    chunk_head = png_tag + data
    return (struct.pack("!I", len(data)) +
            chunk_head +
            struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))


def generate_png(width=128, height=128, max_length=None):
    buf = b''.join(
        [struct.pack('>I', (random.randint(0, (1 << 24) - 1) << 8) | 0xff)
         for _ in range(width * height)]
    )

    width_byte_4 = width * 4
    raw_data = b''.join(
        b'\x00' + buf[span:span + width_byte_4]
        for span in range((height - 1) * width_byte_4, -1, - width_byte_4)
    )

    return b''.join([
        b'\x89PNG\r\n\x1a\n',
        png_pack(b'IHDR', struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)),
        png_pack(b'IDAT', zlib.compress(raw_data, 9)),
        png_pack(b'IEND', b'')
    ])


def generate_integer_list(
    max_length=128, min_length=1, sep=',', allow_negative=True
):
    length = random.randint(min_length, max_length)
    res = ""
    while len(res) + 8 <= length:
        if res:
            res += sep
        if not allow_negative or random.random() < 0.5:
            res += str(random.randint(0, 999999))
        else:
            res += str(random.randint(-999999, 0))

    if length - len(res) == 0:
        return res
    if length - len(res) == 1:
        return res + str(random.randint(0, 9))
    else:
        if res:
            res += sep
        rem = length - len(res)
        if rem > 1 and allow_negative and random.random() < 0.5:
            rem -= 1
            res += str(-random.randint(10 ** (rem - 1), 10 ** rem - 1))
        elif rem == 1:
            res += str(random.randint(0, 9))
        else:
            res += str(random.randint(10 ** (rem - 1), 10 ** rem - 1))
    return res


def generate_json(depth=0, max_length=None):
    if random.random() < 1 - 1 / (1 + depth):
        return random.choice([
            generate_small_integer(),
            generate_small_integer(),
            generate_small_integer(),
            True,
            False,
            None,
        ] + (
            list(map(lambda x: x.lower(), choices(WORDS_DICTIONARY[3], 3))) +
            list(map(lambda x: x.lower(), choices(WORDS_DICTIONARY[4], 3))) +
            list(map(lambda x: x.lower(), choices(WORDS_DICTIONARY[5], 3))) +
            list(map(lambda x: x.lower(), choices(WORDS_DICTIONARY[7], 3)))
        ))

    values = [generate_json(depth + 1) for _ in range(0, 4)]
    words = [
        random.choice(WORDS_DICTIONARY[random.randint(3, 7)]).lower()
        for _ in values
    ]
    if random.random() < 0.5:
        return values
    else:
        return dict(zip(words, values))
