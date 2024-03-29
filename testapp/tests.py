import datetime
import itertools
import os
import random as rand
import re
from decimal import Decimal

from django.test import TestCase

from djenerator import generate_test_data
from djenerator.core.algos import topological_sort
from djenerator.core.utils import (
    dependencies,
    field_name,
    field_type,
    get_related_model,
    is_auto_field,
    # is_django_model_class,
    is_many_to_many_field,
    is_related,
    is_required,
    # is_reverse_related,
    is_unidirectional_related,
    is_unique,
    retrieve_fields,
    retrieve_generators,
    retrieve_models,
    validate_data
)
from djenerator.core.values_generator import (
    generate_big_integer,
    generate_boolean,
    generate_comma_separated_int,
    generate_date,
    generate_date_time,
    generate_decimal,
    generate_email,
    generate_file_name,
    generate_file_path,
    # generate_float,
    generate_int,
    generate_integer,
    generate_ip,
    generate_png,
    generate_positive_big_integer,
    generate_positive_integer,
    generate_positive_small_integer,
    generate_sentence,
    generate_small_integer,
    generate_string,
    generate_text,
    generate_time,
    generate_url,
    generate_uuid,
)
from testapp.models import (
    Extend_SuperClass, ExtendAbstract, ExtendExtendSuperClass,
    ExtendSuperClassNoProxy, ProxyExtend, TestModelA, TestModelE,
    TestModelFields, TestModelX, TestModelY, validate_mod91,
)


class UtilsTestCase(TestCase):
    def test_utils(self):

        models_abstract = retrieve_models('testapp.models', keep_abstract=True)

        models = retrieve_models('testapp.models')
        existing_models = [
            "ExtendingModel",
            "TestModel0",
            "TestModel1",
            "TestModelA",
            "TestModelB",
            "TestModelC",
            "TestModelD",
            "TestModelE",
            "TestModelX",
            "TestModelY",
            "SuperClass",
            "ExtendAbstract",
            "Extend_SuperClass",
            "ExtendExtendSuperClass",
            "ExtendSuperClassNoProxy",
            "ProxyExtend",
            "TestModelFieldsTwo",
            "TestModelFields",
            "CycleA",
            "CycleB",
            "CycleC",
            "CycleD",
            "CycleE",
            "CycleF",
            "AllFieldsModel",
        ]
        self.assertEqual(
            sorted(existing_models),
            sorted([cls.__name__ for cls in models])
        )
        self.assertEqual(
            sorted(existing_models + ["SuperAbstract"]),
            sorted([cls.__name__ for cls in models_abstract])
        )
        fields = retrieve_fields(TestModelFields)
        names = [field_name(field) for field in fields]
        self.assertEqual(
            set(names),
            set(["fieldY", "fieldA", "fieldB", "fieldC", "fieldD", "fieldE",
                "fieldF", "fieldG", "fieldH", "fieldX", "fieldZ"])
        )
        self.assertEqual(
            set([f.name for f in fields]),
            set(["fieldY", "fieldA", "fieldB", "fieldC", "fieldD", "fieldE",
                "fieldF", "fieldG", "fieldH", "fieldX", "fieldZ"])
        )
        non_required_fields = [f.name for f in fields if not is_required(f)]
        self.assertEqual(non_required_fields, ["fieldB", "fieldG"])
        unique_fields = set([f.name for f in fields if is_unique(f)])
        self.assertEqual(
            unique_fields, set(["fieldY", "fieldA", "fieldC", "fieldF"])
        )
        types = {
            "fieldY": "OneToOneField",
            "fieldA": "CharField",
            "fieldB": "IntegerField",
            "fieldC": "CharField",
            "fieldD": "IntegerField",
            "fieldE": "BooleanField",
            "fieldF": "IntegerField",
            "fieldG": "CharField",
            "fieldH": "BooleanField",
            "fieldX": "ForeignKey",
            "fieldZ": "ManyToManyField",
        }
        fields_types = {field.name: field_type(field) for field in fields}
        self.assertEqual(types, fields_types)
        self.assertEqual(field_name(TestModelFields.fieldZ.field), "fieldZ")
        self.assertEqual(
            set([f.name for f in fields if is_related(f)]),
            set(["fieldY", "fieldX", "fieldZ"])
        )
        self.assertEqual(
            set([f.name for f in fields if is_unidirectional_related(f)]),
            set(["fieldY", "fieldX"])
        )
        self.assertEqual(
            set([f.name for f in fields if is_many_to_many_field(f)]),
            set(["fieldZ"])
        )
        self.assertEqual(
            get_related_model(TestModelFields.fieldZ.field), TestModelE
        )
        self.assertEqual(
            set(dependencies(TestModelFields)),
            set([TestModelX, TestModelY])
        )

        f = next(filter(
            lambda x: field_name(x) == "id", TestModelE._meta.fields
        ))
        self.assertTrue(is_auto_field(f))
        self.assertFalse(is_auto_field(
            next(field_name(f) == 'fieldZ'
                 for f in retrieve_fields(TestModelFields))
        ))
        self.assertFalse(is_auto_field(
            next(field_name(f) == 'fieldA'
                 for f in retrieve_fields(TestModelFields))
        ))

        self.assertEqual(
            set([field_name(f) for f in retrieve_fields(ExtendAbstract)]),
            set(["fieldExAbs", "fieldZZZ", "fieldAbs"]),
            set([field_name(f) for f in retrieve_fields(ExtendAbstract)]),
        )
        self.assertEqual(
            set([field_name(f) for f in retrieve_fields(Extend_SuperClass)]),
            set(["fieldS", "fieldAbr", "fieldFak", "fieldMTM", "fieldExSup"]),
            set([field_name(f) for f in retrieve_fields(Extend_SuperClass)]),
        )
        self.assertEqual(
            set([field_name(f)
                 for f in retrieve_fields(ExtendExtendSuperClass)]),
            set(["fieldS", "fieldAbr", "fieldFak",
                 "fieldMTM", "fieldExSup", "fieldExSup2"]),
            set([field_name(f)
                 for f in retrieve_fields(ExtendExtendSuperClass)]),
        )

        self.assertEqual(
            set([field_name(f)
                 for f in retrieve_fields(ExtendSuperClassNoProxy)]),
            set(["fieldS", "fieldAbr", "fieldFak", "fieldMTM"]),
            set([field_name(f)
                 for f in retrieve_fields(ExtendSuperClassNoProxy)]),
        )

        self.assertEqual(
            set([field_name(f) for f in retrieve_fields(ProxyExtend)]),
            set(["fieldS", "fieldAbr", "fieldFak", "fieldMTM"]),
            set([field_name(f) for f in retrieve_fields(ProxyExtend)]),
        )


class MainTestCase(TestCase):
    def test_djenerator(self):
        models = retrieve_models("testapp.models")
        counts = {
            model_cls.__name__: model_cls.objects.count()
            for model_cls in models
        }
        first_models = [
            "TestModelFields", "TestModelE", "TestModelX", "TestModelY",
            "TestModelB", "TestModelC", "TestModelA"
        ]
        generate_test_data(
            "testapp", 200, allow_null=True, models_cls=["TestModelFields"]
        )
        for model_cls in models:
            if model_cls.__name__ in first_models:
                self.assertGreaterEqual(
                    model_cls.objects.count(),
                    200 + counts[model_cls.__name__],
                    model_cls.__name__
                )
        self.assertTrue(
            any(x is None for x in (
                list(TestModelY.objects.values_list("field2Y", flat=True)) +
                list(TestModelFields.objects.values_list("fieldG", flat=True))
                +
                list(TestModelFields.objects.values_list("fieldB", flat=True))
            ))
        )
        for x in TestModelFields.objects.values_list("fieldB", flat=True):
            self.assertIn(x, [1, 2, 3, 4, 5, None])
        counts = {
            model_cls.__name__: model_cls.objects.count()
            for model_cls in models
        }
        generate_test_data("testapp", 50, allow_external_instances=True)
        for model_cls in models:
            self.assertGreaterEqual(
                model_cls.objects.count(), 50 + counts[model_cls.__name__],
                model_cls.__name__
            )
        for a in list(TestModelA.objects.values_list("field1A", flat=True)):
            if a:
                self.assertIn(a, ["a", "b", "z"], a)
        for a in list(TestModelA.objects.values_list("field2A", flat=True)):
            self.assertIn(a, ["a", "b", "z"], a)


class AlgorithmsTestCase(TestCase):
    def test_topological_sorting(self):
        all_nodes = ["A", "B", "C", "D", "E", "F", "G"]

        func = (lambda x: {
            "A": ["B", "C"], "C": ["D", "E"], "D": ["F"]
        }.get(x, []))

        nodes, cycle = topological_sort(all_nodes, func)
        self.assertEqual(cycle, [])
        self.assertEqual(nodes, ['G', 'F', 'D', 'E', 'C', 'B', 'A'])

        func = (lambda x: {
            "A": ["B", "C"], "C": ["D", "E"], "D": ["F", "A"]
        }.get(x, []))
        nodes, cycle = topological_sort(all_nodes, func)
        self.assertEqual(nodes, [])
        self.assertEqual(set(cycle), set(["A", "C", "D"]))


class TestFieldsGeneratorNumbers(TestCase):
    def test(self):
        counts = {}
        for _ in range(100):
            for bits in range(2, 64):
                for negative_allowed in range(0, 2):
                    gen_val = generate_integer(bits, negative_allowed)

                    self.assertTrue(isinstance(gen_val, int))
                    if negative_allowed:
                        self.assertGreaterEqual(gen_val, -2 ** (bits - 1))
                        self.assertLess(gen_val, 2 ** (bits - 1))
                    else:
                        self.assertGreaterEqual(gen_val, 0)
                        self.assertLess(gen_val, 2 ** (bits - 1))

            gen_val = generate_int()
            self.assertTrue(isinstance(gen_val, int))
            self.assertLessEqual(abs(gen_val), 2 ** 31)
            self.assertLess(gen_val, 2 ** 31)

            gen_val = generate_int(mn=-2, mx=2)
            self.assertTrue(isinstance(gen_val, int))
            self.assertGreaterEqual(gen_val, -2)
            self.assertLess(gen_val, 3)

            gen_val = generate_int(mn=-2, mx=-1)
            self.assertTrue(isinstance(gen_val, int))
            self.assertGreaterEqual(gen_val, -2)
            self.assertLess(gen_val, 0)

            gen_val = generate_big_integer()
            self.assertTrue(isinstance(gen_val, int))
            self.assertLessEqual(abs(gen_val), 2 ** 63)
            self.assertLess(gen_val, 2 ** 63)

            gen_val = generate_small_integer()
            self.assertTrue(isinstance(gen_val, int))
            self.assertLessEqual(abs(gen_val), 2 ** 15)
            self.assertLess(gen_val, 2 ** 15)

            gen_val = generate_big_integer(mn=-100, mx=100, step=13)
            self.assertTrue(isinstance(gen_val, int))
            self.assertLessEqual(abs(gen_val), 100)
            self.assertEqual(gen_val % 13, 0)

            gen_val = generate_small_integer(mn=-150, mx=150, step=13)
            self.assertTrue(isinstance(gen_val, int))
            self.assertLessEqual(abs(gen_val), 150)
            self.assertEqual(gen_val % 13, 0)

            gen_val = generate_positive_integer()
            self.assertTrue(isinstance(gen_val, int))
            self.assertLess(gen_val, 2 ** 31)
            self.assertGreaterEqual(gen_val, 0)

            gen_val = generate_positive_small_integer()
            self.assertTrue(isinstance(gen_val, int))
            self.assertLess(gen_val, 2 ** 15)
            self.assertGreaterEqual(gen_val, 0)

            gen_val = generate_positive_big_integer()
            self.assertTrue(isinstance(gen_val, int))
            self.assertLess(gen_val, 2 ** 63)
            self.assertGreaterEqual(gen_val, 0)

            gen_val = generate_positive_integer(mn=1000, mx=10000)
            self.assertTrue(isinstance(gen_val, int))
            self.assertLess(gen_val, 10001)
            self.assertGreaterEqual(gen_val, 1000)

            gen_val = generate_positive_small_integer(mn=1000)
            self.assertTrue(isinstance(gen_val, int))
            self.assertLess(gen_val, 2 ** 15)
            self.assertGreaterEqual(gen_val, 1000)

            gen_val = generate_positive_big_integer(mx=10000)
            self.assertTrue(isinstance(gen_val, int))
            self.assertLess(gen_val, 10001)
            self.assertGreaterEqual(gen_val, 0)

            gen_val = generate_boolean()
            self.assertTrue(isinstance(gen_val, int))

            gen_val = generate_boolean(True)
            self.assertTrue(gen_val is None or isinstance(gen_val, bool))

            gen_val = generate_ip(v6=False)
            self.assertTrue(isinstance(gen_val, str))
            ip_regex = r'^(?:\d{1,3})(?:\.\d{1,3}){3}$'
            match = re.search(ip_regex, gen_val)
            self.assertRegexpMatches(gen_val, ip_regex)
            self.assertIsNotNone(match)
            match = map(int, match.groups())
            self.assertTrue(all([x in range(256) for x in match]))

            gen_val = generate_ip(v4=False)
            self.assertTrue(isinstance(gen_val, str))
            ip_regex = (
                r'^(?:[0123456789ABCDEF]{1,4})'
                r'(?:\:[0123456789ABCDEF]{1,4}){7}$'
            )
            match = re.search(ip_regex, gen_val)
            self.assertRegexpMatches(gen_val, ip_regex)
            self.assertIsNotNone(match)
            match = map(int, match.groups())
            self.assertTrue(all([x in range(256) for x in match]))

            gen_val = generate_comma_separated_int(rand.randint(1, 1000))
            self.assertTrue(isinstance(gen_val, str))
            comma_sep_regex = r'^[123456789]\d{0,2}(?:,\d{3})*$'
            comma_sep_regex = r'^(?:0)|(?:[123456789]\d{0,2}(?:,\d{3})*)$'
            self.assertRegexpMatches(gen_val, comma_sep_regex)

            for digits in range(50):
                for decimal in range(1, digits):
                    gen_val = generate_decimal(digits, decimal)
                    self.assertTrue(isinstance(gen_val, Decimal))

                    gen_val = str(gen_val)
                    if 'decimal_contains_dot' in counts.keys():
                        counts['decimal_contains_dot'] += 1
                    else:
                        counts['decimal_contains_dot'] = 1

                    self.assertLessEqual(len(gen_val), digits + 1, gen_val)
                    self.assertLessEqual(len(gen_val.split('.')[1]),
                                         decimal + (decimal == 0), gen_val)


class TestFieldsGeneratorStringGenerators(TestCase):
    def test(self):
        for length in range(1, 3):
            gen_sentence = generate_sentence(length)
            self.assertEqual(len(gen_sentence), length)

        for length in range(3, 50):
            seperators = ['.', '-_', '@']
            for sep in seperators:
                for _ in range(20):
                    gen_val = generate_sentence(length, seperators=sep)
                    self.assertTrue(isinstance(gen_val, str))
                    self.assertLessEqual(len(gen_val), length * 2)
                    reg = r'^(?:\w+(?:%s))*\w+\.$' % str.join('|', sep)
                    self.assertRegexpMatches(gen_val, reg)

            min_length = length * 8 // 10
            gen_text = generate_text(length, min_length)
            txt_re = r'^(?:(?:\w+\s?)+\.)+(?:\s(?:\w+\s?)+\.)*$'
            self.assertLessEqual(len(gen_text), length)
            self.assertGreaterEqual(len(gen_text), min_length)
            self.assertRegexpMatches(gen_text, txt_re, gen_text)

            gen_sentence = generate_sentence(length)
            self.assertEqual(len(gen_sentence), length)
            sent_re = r'^(?:\w+\s?)+\.$'
            self.assertRegexpMatches(gen_sentence, sent_re, gen_sentence)

            gen_sentence = generate_sentence(length, endchar=['', '.'])
            self.assertEqual(len(gen_sentence), length)
            sent_re = r'^(?:\w+\s?)+\.?$'
            self.assertRegexpMatches(gen_sentence, sent_re, gen_sentence)

            gen_sentence = generate_sentence(
                length, seperators='!', endchar=None
            )
            self.assertEqual(len(gen_sentence), length)
            sent_re = r'^(?:\w+\!?)+$'
            self.assertRegexpMatches(gen_sentence, sent_re, gen_sentence)

            gen_sentence = generate_sentence(length, endchar='.,')
            self.assertEqual(len(gen_sentence), length)
            sent_re = r'^(?:\w+\s?)+[\.,]$'
            self.assertRegexpMatches(gen_sentence, sent_re, gen_sentence)


class TestFieldsGeneratorChar(TestCase):
    def test(self):
        ascii_val = dict([(chr(n), n) for n in range(128)])
        ascii_rng = (
            lambda beg, end: range(ascii_val[beg], ascii_val[end] + 1)
        )
        chr_range = (lambda beg, end: map(chr, ascii_rng(beg, end)))
        for log in range(0, 4):
            lengths = rand.sample(
                range(1, 10 ** (log + 1) + 1 - bool(log)), 10
            )
            for length in lengths:
                for tup in itertools.product(*zip(4 * [True], 4 * [False])):
                    lower, upper, digits, special = tup
                    if rand.randint(1, 6) < 3:
                        special = ['@', '!', '~']
                    if not (lower or upper or digits or special):
                        continue
                    gen_val = generate_string(
                        length, 1, lower, upper, digits, special
                    )
                    existing_chars = set([])

                    for char in gen_val:
                        existing_chars.add(char)

                    excluded = []
                    if not upper:
                        excluded.extend(chr_range('A', 'Z'))

                    if not lower:
                        excluded.extend(chr_range('a', 'z'))

                    if not digits:
                        excluded.extend(chr_range('0', '9'))

                    if not special:
                        excluded.extend(chr_range('!', '/'))
                        excluded.extend(chr_range(':', '@'))
                        excluded.extend(chr_range('[', '`'))
                        excluded.extend(chr_range('{', '~'))
                    else:
                        if isinstance(special, list):
                            special_excluded = []
                            special_excluded.extend(chr_range('!', '/'))
                            special_excluded.extend(chr_range(':', '@'))
                            special_excluded.extend(chr_range('[', '`'))
                            special_excluded.extend(chr_range('{', '~'))
                            special_excluded = set(special_excluded)
                            special_excluded = special_excluded - set(special)
                            excluded.extend(list(special_excluded))

                    self.assertFalse(existing_chars & set(excluded),
                                     str(existing_chars) +
                                     str(set(excluded) & existing_chars))

                    self.assertGreaterEqual(len(gen_val), 0)
                    self.assertLessEqual(len(gen_val), length)

                if length >= 14:
                    min_length = max(14, length * 9 // 10)
                    email = generate_email(length, min_length=min_length)
                    self.assertTrue(isinstance(email, str), email)
                    self.assertLessEqual(len(email), length)
                    self.assertGreaterEqual(len(email), min_length)
                    email_reg = (
                        r'^\w+(?:\.?\-?\w+)*@'
                        r'(?:[A-Za-z0-9\-]+\.)*[A-Za-z0-9\-]+$'
                    )
                    self.assertRegexpMatches(email, email_reg)

                    email = generate_email(
                        length, min_length=min_length,
                        allowlist=["localhost", "mydomain"]
                    )
                    self.assertTrue(isinstance(email, str), email)
                    self.assertLessEqual(len(email), length)
                    self.assertGreaterEqual(len(email), min_length)
                    email_reg = (
                        r'^\w+(?:\.?\-?\w+)*@(?:localhost|mydomain)$'
                    )
                    self.assertRegexpMatches(email, email_reg)

                if length >= 16:
                    min_length = max(16, length * 9 // 10)
                    url = generate_url(length, min_length=min_length)
                    self.assertTrue(isinstance(url, str), url)
                    self.assertLessEqual(len(url), length)
                    self.assertGreaterEqual(len(url), min_length)
                    url_re = (
                        r'^(?:http|ftp|https|ftps)://(?:[a-z0-9_\-]+\.?)+/?'
                        r'(?:/[a-z0-9_\-]+)*/?$'
                    )
                    self.assertRegexpMatches(url, url_re)

                    url = generate_url(
                        length, min_length=min_length,
                        schemas=["tcp", "redis", "http"]
                    )
                    self.assertTrue(isinstance(url, str), url)
                    self.assertLessEqual(len(url), length)
                    self.assertGreaterEqual(len(url), min_length)
                    url_re = (
                        r'^(?:http|tcp|redis)://(?:[a-z0-9_\-]+\.?)+/?'
                        r'(?:/[a-z0-9_\-]+)*/?$'
                    )
                    self.assertRegexpMatches(url, url_re)

        for _ in range(10):
            uuid_regex = (
                r"^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-"
                r"[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$"
            )
            gen_value = str(generate_uuid())
            self.assertRegexpMatches(gen_value, uuid_regex, gen_value)


class TestFieldsGeneratorDateTime(TestCase):
    def test(self):
        for _ in range(1000):
            gen_val = generate_date_time()
            self.assertTrue(gen_val)
            self.assertTrue(isinstance(gen_val, datetime.datetime))

            gen_val = generate_time()
            self.assertTrue(gen_val)
            self.assertTrue(isinstance(gen_val, datetime.time))

            gen_val = generate_date()
            self.assertTrue(gen_val)
            self.assertTrue(isinstance(gen_val, datetime.date))

        for _ in range(100):
            gen_val = generate_date_time(True)
            self.assertTrue(gen_val)
            self.assertTrue(isinstance(gen_val, datetime.datetime))
            now = datetime.datetime.now()
            self.assertLess(abs((gen_val - now).total_seconds()), 10e-4)

            gen_val = generate_time(True)
            self.assertTrue(gen_val)
            self.assertTrue(isinstance(gen_val, datetime.time))
            now = datetime.datetime.now().time()
            gen_val_hash = (
                gen_val.hour * 3600 + gen_val.minute * 60 + gen_val.second
            )
            now_hash = now.hour * 3600 + now.minute * 60 + now.second
            self.assertLessEqual(gen_val_hash, now_hash + 1)

            gen_val = generate_date(True)
            self.assertTrue(gen_val)
            self.assertTrue(isinstance(gen_val, datetime.date))
            now = datetime.datetime.now().date()
            self.assertEqual(gen_val, now)


class TestFileGenerators(TestCase):
    def test(self):
        for _ in range(20):
            ext = rand.choice(['.txt', '.rst', '.md'])
            name = generate_file_name(12, extensions=[ext])
            self.assertTrue(isinstance(name, str), name)
            self.assertLessEqual(len(name), 12, name)
            self.assertRegexpMatches(name, r'[a-zA-Z_]*\.' + ext[1:], name)

            path = generate_file_path()
            self.assertTrue(os.path.exists(path), path)

            img = generate_png(500, 120)
            beg = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
            self.assertTrue(img.startswith(beg))
            self.assertTrue(b'IHDR' in img)
            self.assertTrue(b'IEND' in img)
            self.assertTrue(b'IDAT' in img)


class TestTrivia(TestCase):
    def test(self):
        self.assertFalse(
            retrieve_generators("testapp.fakemodule", ["TestModel1"])
        )
        self.assertFalse(validate_data(41, validate_mod91))
        self.assertTrue(validate_data(182, validate_mod91))
        try:
            generate_positive_small_integer(mn=-100, mx=-10)
            self.assertTrue(False)
        except AssertionError:
            self.assertTrue(True)
        try:
            generate_positive_small_integer(mn=1000000, mx=10000000)
            self.assertTrue(False)
        except AssertionError:
            self.assertTrue(True)
