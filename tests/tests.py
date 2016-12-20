#!/usr/bin/env python
"""
This module contains tests for djenerator app.
"""
import datetime
import itertools
import os
import random
import re
import tempfile
import uuid
from decimal import Decimal
from django.core.files import File
from django.db import models
from django.db.models import Model
from django.db.models.fields import BigIntegerField
from django.db.models.fields import BooleanField
from django.db.models.fields import BinaryField
from django.db.models.fields import CharField
from django.db.models.fields import CommaSeparatedIntegerField
from django.db.models.fields import DateField
from django.db.models.fields import DateTimeField
from django.db.models.fields import DecimalField
from django.db.models.fields import DurationField
from django.db.models.fields import EmailField
from django.db.models.fields import FilePathField
from django.db.models.fields import FloatField
from django.db.models.fields import GenericIPAddressField
from django.db.models.fields import IntegerField
from django.db.models.fields import NullBooleanField
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields import PositiveSmallIntegerField
from django.db.models.fields import SmallIntegerField
from django.db.models.fields import SlugField
from django.db.models.fields import TextField
from django.db.models.fields import TimeField
from django.db.models.fields import URLField
from django.db.models.fields import UUIDField
from django.db.models.fields.files import FileField
from django.db.models.fields.files import ImageField
from django.test import TestCase
from djenerator.djenerator import djenerator
from djenerator.fields_generator import generate_random_values
from djenerator.generate_test_data import create_model
from djenerator.generate_test_data import dependencies
from djenerator.generate_test_data import dfs
from djenerator.generate_test_data import field_sample_values
from djenerator.generate_test_data import generate_model
from djenerator.generate_test_data import generate_test_data
from djenerator.generate_test_data import recompute
from djenerator.generate_test_data import topological_sort
from djenerator.model_reader import field_type
from djenerator.model_reader import is_auto_field
from djenerator.model_reader import is_instance_of_django_model
from djenerator.model_reader import is_related
from djenerator.model_reader import is_required
from djenerator.model_reader import is_reverse_related
from djenerator.model_reader import list_of_fields
from djenerator.model_reader import list_of_models
from djenerator.model_reader import module_import
from djenerator.model_reader import names_of_fields
from djenerator.model_reader import relation_type
from djenerator.values_generator import generate_big_integer
from djenerator.values_generator import generate_boolean
from djenerator.values_generator import generate_comma_separated_int
from djenerator.values_generator import generate_date
from djenerator.values_generator import generate_date_time
from djenerator.values_generator import generate_decimal
from djenerator.values_generator import generate_email
from djenerator.values_generator import generate_file_name
from djenerator.values_generator import generate_file_path
from djenerator.values_generator import generate_int
from djenerator.values_generator import generate_integer
from djenerator.values_generator import generate_ip
from djenerator.values_generator import generate_png
from djenerator.values_generator import generate_positive_integer
from djenerator.values_generator import generate_positive_small_integer
from djenerator.values_generator import generate_small_integer
from djenerator.values_generator import generate_sentence
from djenerator.values_generator import generate_string
from djenerator.values_generator import generate_text
from djenerator.values_generator import generate_time
from djenerator.values_generator import generate_url
from djenerator.utility import sort_unique_tuple
from djenerator.utility import sort_unique_tuples
from djenerator.utility import unique_items
import models as mdls
from models import AllFieldsModel
from models import CycleA
from models import CycleB
from models import CycleC
from models import CycleD
from models import CycleE
from models import CycleF
from models import ExtendAbstract
from models import ExtendSuperClass
from models import ExtendingModel
from models import NotExtendingModel
from models import ProxyExtend
from models import SuperAbstract
from models import SuperClass
from models import TestModel0
from models import TestModel1
from models import TestModelA
from models import TestModelB
from models import TestModelC
from models import TestModelD
from models import TestModelE
from models import TestModelFields
from models import TestModelFieldsTwo
from models import TestModelX
from models import TestModelY


class TestFieldToRandomGeneratorMatcher(TestCase):
    def test(self):
        fields = list_of_fields(AllFieldsModel)
        present_types = list(map(lambda field: field.__class__, fields))
        field_types = [BigIntegerField, BooleanField, CharField,
                       CommaSeparatedIntegerField, DateField, DateTimeField,
                       DecimalField, DurationField, EmailField, FloatField,
                       GenericIPAddressField, IntegerField, NullBooleanField,
                       PositiveIntegerField, PositiveSmallIntegerField,
                       SmallIntegerField, TextField, TimeField]
        self.assertFalse(set(field_types) - set(present_types),
                         "All types should be present." +
                         str(set(field_types) - set(present_types)))
        for field in fields:
            sample_siz = 10
            values = generate_random_values(field, sample_siz)
            self.assertLessEqual(len(values), sample_siz)
            self.assertGreaterEqual(len(values), 1)
            for val in values:
                if isinstance(field, IntegerField):
                    self.assertTrue(isinstance(val, int), val)
                if isinstance(field, EmailField):
                    self.assertTrue(isinstance(val, str), val)
                    email_reg = r'^\w+(?:\.\w+)*@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$'
                    self.assertRegexpMatches(val, email_reg, val)
                if isinstance(field, BooleanField):
                    self.assertTrue(isinstance(val, bool), val)
                if isinstance(field, CharField):
                    self.assertTrue(isinstance(val, str), val)
                    self.assertLessEqual(len(val), field.max_length, val)
                if isinstance(field, CommaSeparatedIntegerField):
                    self.assertTrue(isinstance(val, str), val)
                    comma_sep_int_re = r'^\d{1,3}(?:,\d{3})*$'
                    self.assertRegexpMatches(val, comma_sep_int_re, val)
                if isinstance(field, DateField):
                    self.assertTrue(isinstance(val, datetime.date), val)
                if isinstance(field, DateTimeField):
                    self.assertTrue(isinstance(val, datetime.datetime), val)
                if isinstance(field, DecimalField):
                    self.assertTrue(isinstance(val, Decimal), val)
                if isinstance(field, FloatField):
                    self.assertTrue(isinstance(val, float), val)
                if isinstance(field, GenericIPAddressField):
                    self.assertTrue(isinstance(val, str), val)
                    ip_regex = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
                    self.assertRegexpMatches(val, ip_regex, val)
                if isinstance(field, PositiveIntegerField):
                    self.assertTrue(isinstance(val, int), val)
                    self.assertLessEqual(val, 2147483647, val)
                    self.assertGreaterEqual(val, 0, val)
                if isinstance(field, PositiveSmallIntegerField):
                    self.assertTrue(isinstance(val, int), val)
                    self.assertLessEqual(val, 32767, val)
                    self.assertGreaterEqual(val, 0, val)
                if isinstance(field, SmallIntegerField):
                    self.assertTrue(isinstance(val, int), val)
                    self.assertLessEqual(val, 32767, val)
                    self.assertGreaterEqual(val, -32768, val)
                if isinstance(field, TimeField):
                    self.assertTrue(isinstance(val, datetime.time), val)
                if isinstance(field, TextField):
                    self.assertTrue(isinstance(val, str), val)
                    self.assertLessEqual(len(val), field.max_length)
                    text_re = r'^(?:(?:\w+\s?)+\.\s?)+$'
                    self.assertRegexpMatches(val, text_re, val)
                if isinstance(field, DurationField):
                    self.assertTrue(isinstance(val, datetime.timedelta), val)
                if isinstance(field, SlugField):
                    self.assertTrue(isinstance(val, str), val)
                    slug_re = r'^[a-zA-Z0-9_\-]+$'
                    self.assertRegexpMatches(val, slug_re, val)
                if isinstance(field, URLField):
                    url_re = r'^(?:http|ftp|https)://(?:[a-z0-9_\-]+\.?)+/?'
                    url_re += r'(?:/[a-z0-9_\-]+)*/?$'
                    self.assertTrue(isinstance(val, str), val)
                    self.assertRegexpMatches(val, url_re, val)
                if isinstance(field, UUIDField):
                    self.assertTrue(isinstance(val, uuid.UUID), val)
                if isinstance(field, FilePathField):
                    self.assertTrue(isinstance(val, str), val)
                    self.assertTrue(os.path.exists(val), val)
                if isinstance(field, ImageField):
                    self.assertTrue(isinstance(val, File), val)
                    beg = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
                    img = val.read()
                    self.assertTrue(img.startswith(beg))
                    self.assertTrue(val.name.endswith('.png'))
                if isinstance(field, FileField):
                    self.assertTrue(isinstance(val, File), val)
                    if not isinstance(field, ImageField):
                        content = val.read()
                        text_re = r'^(?:(?:\w+\s?)+\.\s?)+$'
                        self.assertRegexpMatches(content, text_re, content)
                        self.assertTrue(val.name.endswith('.txt'))
                if isinstance(field, BinaryField):
                    self.assertTrue(isinstance(val, str), val)


class TestInstanceOfDjangoModel(TestCase):
    def test(self):
        models = [TestModel0, TestModel1, TestModelA, TestModelB,
                  TestModelC, TestModelD, TestModelE, TestModelX,
                  TestModelY, ExtendingModel]
        for model in models:
            self.assertTrue(is_instance_of_django_model(model))
        self.assertFalse(is_instance_of_django_model(NotExtendingModel))

        def not_extending_model_func():
            pass

        self.assertFalse(is_instance_of_django_model(not_extending_model_func))


class TestListOfModels(TestCase):
    def test(self):
        self.assertEqual(set([ExtendingModel, TestModel0, TestModel1,
                              TestModelA, TestModelB, TestModelC, TestModelD,
                              TestModelE, TestModelX, TestModelY,
                              TestModelFields, SuperClass, ExtendAbstract,
                              ExtendSuperClass, ProxyExtend, SuperAbstract,
                              TestModelFieldsTwo, CycleA, CycleB, CycleC,
                              CycleD, CycleE, CycleF, AllFieldsModel]),
                         set(list_of_models(mdls, keep_abstract=True)))
        self.assertEqual(set([ExtendingModel, TestModel0, TestModel1,
                              TestModelA, TestModelB, TestModelC, TestModelD,
                              TestModelE, TestModelX, TestModelY,
                              TestModelFields, SuperClass, ExtendAbstract,
                              ExtendSuperClass, TestModelFieldsTwo,
                              ProxyExtend, CycleA, CycleB, CycleC, CycleD,
                              CycleE, CycleF, AllFieldsModel]),
                         set(list_of_models(mdls)))


class TestListOfFields(TestCase):
    def test(self):
        self.assertTrue(all(isinstance(*x)
                            for x in zip(list_of_fields(TestModel1),
                                         [models.AutoField, models.CharField,
                                          models.IntegerField,
                                          models.ForeignKey])))
        self.assertTrue(all([isinstance(*x)
                             for x in zip(list_of_fields(TestModel0),
                                          [models.AutoField,
                                           models.BooleanField,
                                           models.EmailField])]))
        self.assertTrue(all([isinstance(*x)
                             for x in zip(list_of_fields(TestModelE),
                                          [models.AutoField,
                                           models.OneToOneField,
                                           models.ForeignKey,
                                           models.IntegerField,
                                           models.ManyToManyField])]))


class TestNamesOfFields(TestCase):
    def test(self):
        self.assertEqual(['id', 'field1E', 'field3E', 'field4E', 'field2E'],
                         names_of_fields(TestModelE))
        self.assertEqual(['id', 'field1', 'field2', 'field3'],
                         names_of_fields(TestModel1))
        self.assertEqual(['id', 'field1', 'field2'],
                         names_of_fields(TestModel0))


class TestFieldType(TestCase):
    def test(self):
        self.assertEqual(field_type(models.CharField()),
                         'CharField')
        self.assertEqual(field_type(models.IntegerField()),
                         'IntegerField')
        self.assertEqual(field_type(models.EmailField()),
                         'CharField')
        self.assertEqual(field_type(models.BooleanField()),
                         'BooleanField')
        self.assertEqual(field_type(models.ForeignKey(ExtendingModel)),
                         'ForeignKey')
        self.assertEqual(field_type(models.OneToOneField(ExtendingModel)),
                         'OneToOneField')
        self.assertEqual(field_type(models.ManyToManyField(ExtendingModel)),
                         'ManyToManyField')


class TestIsAutoField(TestCase):
    def test(self):
        self.assertTrue(is_auto_field(models.AutoField(primary_key=True)))
        self.assertFalse(is_auto_field(models.CharField()))
        self.assertFalse(is_auto_field(models.BooleanField()))
        self.assertFalse(is_auto_field(models.IntegerField()))
        self.assertFalse(is_auto_field(models.ForeignKey(ExtendingModel)))


class TestIsRelated(TestCase):
    def test(self):
        self.assertTrue(is_related(models.ForeignKey))
        self.assertTrue(is_related(models.OneToOneField))
        self.assertTrue(is_related(models.ManyToManyField))
        self.assertFalse(is_related(models.CharField))
        self.assertFalse(is_related(models.BooleanField))
        self.assertFalse(is_related(models.EmailField))
        self.assertFalse(is_related(models.IntegerField))


class TestRelationType(TestCase):
    def test(self):
        self.assertEqual(relation_type(models.OneToOneField(ExtendingModel)),
                         'OneToOneRel')
        self.assertEqual(relation_type(models.ManyToManyField(ExtendingModel)),
                         'ManyToManyRel')
        self.assertEqual(relation_type(models.ForeignKey(ExtendingModel)),
                         'ManyToOneRel')


class TestIsRequired(TestCase):
    def test(self):
        field = models.CharField(max_length=20, null=True)
        self.assertFalse(is_required(field))
        field = models.IntegerField(null=True)
        self.assertFalse(is_required(field))
        field = models.IntegerField()
        self.assertTrue(is_required(field))
        field = models.ForeignKey(ExtendingModel)
        self.assertTrue(is_required(field))
        field = models.ForeignKey(ExtendingModel, null=True)
        self.assertFalse(is_required(field))


class TestModuleImport(TestCase):
    def test(self):
        self.assertEqual(mdls, module_import('tests.models'))


class TestListOfSampleFieldValues(TestCase):
    def test(self):
        Y = list_of_fields(TestModelY)
        X = list_of_fields(TestModelX)
        A = list_of_fields(TestModelA)
        B = list_of_fields(TestModelB)
        C = list_of_fields(TestModelC)
        D = list_of_fields(TestModelD)
        E = list_of_fields(TestModelE)
        self.assertFalse(field_sample_values(X[0]))
        self.assertEqual(field_sample_values(Y[1]), [2, 3, 5, 7, 11, 13])
        self.assertEqual(field_sample_values(Y[2]), ['MMa', 'XXa', 'azz'])
        self.assertEqual(field_sample_values(X[1]),
                         [x * x * x for x in range(10)])
        self.assertEqual(field_sample_values(E[3]), [1000000009, 1000003, 101])
        self.assertEqual(field_sample_values(D[1]),
                         [x * x * x for x in range(10)])
        self.assertEqual(field_sample_values(C[1]),
                         ['Hello I am C', 'MUHAHAHAHAHA', 'CCCC', '^_^'])
        self.assertEqual(field_sample_values(B[1]),
                         ['Hello Universe', 'Hello Parallel Universe!'])
        self.assertEqual(field_sample_values(A[1]),
                         ['Hello World', 'Hello Africa', 'axxx!!'])
        self.assertEqual(field_sample_values(A[2]),
                         ['Hello Second Field', 'field 2'])
        a = TestModelX(field1X=12)
        b = TestModelX(field1X=15)
        a.save()
        b.save()
        self.assertEqual((field_sample_values(models.ForeignKey(TestModelX))),
                         ([a, b]))
        fld = models.ManyToManyField(TestModelX)
        self.assertTrue(all([x in [a, b]
                             for x in field_sample_values(fld)[0]]))
        vals = [int(x) for x in field_sample_values(list_of_fields(CycleF)[2])]
        self.assertEqual(vals, range(4000, 5000))


class TestCreateModel(TestCase):
    def test(self):
        kwargsa = {'field1A': 'Hrr', 'field2A': 'HxxA'}
        atest = create_model(TestModelA, kwargsa.items())
        self.assertEqual(atest, TestModelA.objects.get(**kwargsa))
        kwargsa = {'field1B': 'Hello Worrd', 'field2B': atest}
        btest = create_model(TestModelB, kwargsa.items())
        self.assertEqual(btest, TestModelB.objects.get(**kwargsa))
        kwargsa = {'field1C': 'Hello Egypt!!', 'field2C': btest}
        ctest = create_model(TestModelC, kwargsa.items())
        self.assertEqual(ctest, TestModelC.objects.get(**kwargsa))
        kwargsa = {'field1D': 77, 'field2D': TestModelA.objects.all()}
        dtest = create_model(TestModelD, kwargsa.items())
        self.assertEqual(dtest, TestModelD.objects.get(**kwargsa))


class TestDependencies(TestCase):
    def test(self):
        self.assertEqual(dependencies(TestModelD), [])
        self.assertEqual(set(dependencies(TestModelE)),
                         set([TestModelB, TestModelC]))
        self.assertEqual(dependencies(TestModelC), [TestModelB])
        self.assertEqual(dependencies(TestModelB), [TestModelA])
        self.assertEqual(dependencies(CycleD), [CycleC])
        self.assertFalse(dependencies(CycleC))
        self.assertEqual(set(dependencies(TestModelFields)),
                         set([TestModelY, TestModelX]))


class TestTopologicalSorting(TestCase):
    def test(self):
        self.assertEqual(topological_sort([ExtendingModel, TestModel1,
                                           TestModel0]),
                         [ExtendingModel, TestModel0, TestModel1])
        self.assertEqual(topological_sort([TestModel1, TestModel0]),
                         [TestModel0, TestModel1])
        self.assertEqual(topological_sort([TestModel0, TestModel1]),
                         [TestModel0, TestModel1])

        def assertions(sorted_list):
            self.assertTrue(sorted_list.index(TestModelA) <
                            sorted_list.index(TestModelB))
            self.assertTrue(sorted_list.index(TestModelB) <
                            sorted_list.index(TestModelC))
            self.assertTrue(sorted_list.index(TestModelB) <
                            sorted_list.index(TestModelE))
            self.assertTrue(sorted_list.index(TestModelC) <
                            sorted_list.index(TestModelE))
            self.assertTrue(ExtendingModel in sorted_list)

        for perm in itertools.permutations([TestModelA, TestModelB, TestModelD,
                                            TestModelC, TestModelE,
                                            ExtendingModel]):
            assertions(topological_sort(list(perm)))


class TestUniqueConstraints(TestCase):
    def test(self):
        constraint = unique_items(('fieldA', 'fieldD',))
        model = TestModelFieldsTwo(fieldA='A', fieldD=5, fieldB=10,
                                   fieldC='Winner', fieldE=True, fieldF=6,
                                   fieldG='Mathematics', fieldH=False)
        model.save()
        fields = list_of_fields(TestModelFields)
        self.assertFalse(constraint([('fieldA', 'A'), ('fieldD', 5)],
                                    TestModelFieldsTwo, fields[5]))
        self.assertTrue(constraint([('fieldA', 'A')],
                                   TestModelFields, fields[5]))
        self.assertFalse(constraint([('fieldA', 'A'), ('fieldD', 5)],
                                    TestModelFieldsTwo, fields[5]))
        self.assertTrue(constraint([('fieldA', 'A'), ('fieldD', 3)],
                                   TestModelFieldsTwo, fields[5]))
        self.assertTrue(constraint([('fieldA', 'A')],
                                   TestModelFieldsTwo, fields[5]))
        self.assertTrue(constraint([('fieldA', 'A'), ('fieldD', 3)],
                                   TestModelFieldsTwo, fields[5]))


class TestSortTuple(TestCase):
    def test(self):
        flds = tuple(names_of_fields(TestModelFields))
        self.assertEqual(sort_unique_tuple(('fieldA', 'fieldX', 'fieldG',
                                            'fieldD'), TestModelFields),
                         ('fieldA', 'fieldD', 'fieldG', 'fieldX'))
        self.assertEqual(sort_unique_tuple(flds[::-1], TestModelFields), flds)
        self.assertEqual(sort_unique_tuple(('fieldD', 'fieldH', 'fieldF'),
                                           TestModelFields),
                         ('fieldD', 'fieldF', 'fieldH'))


class TestSortTuples(TestCase):
    def test(self):
        self.assertEqual(sort_unique_tuples((('fieldA',), ('fieldA', 'fieldD'),
                                             ('fieldC', 'fieldX', 'fieldB'),
                                             ('fieldC', 'fieldE', 'fieldH'),
                                             ('fieldA', 'fieldX', 'fieldC')),
                                            TestModelFields),
                         (('fieldA',), ('fieldA', 'fieldC', 'fieldX'),
                          ('fieldA', 'fieldD'), ('fieldB', 'fieldC', 'fieldX'),
                          ('fieldC', 'fieldE', 'fieldH')))
        self.assertEqual(sort_unique_tuples((('fieldA', 'fieldD'),
                                             ('fieldA', 'fieldE', 'fieldX')),
                                            TestModelFields),
                         (('fieldA', 'fieldD'),
                          ('fieldA', 'fieldE', 'fieldX')))
        self.assertEqual(sort_unique_tuples((('fieldA', 'fieldE', 'fieldX'),
                                             ('fieldA', 'fieldD')),
                                            TestModelFields),
                         (('fieldA', 'fieldD'),
                          ('fieldA', 'fieldE', 'fieldX')))
        self.assertEqual(sort_unique_tuples((('fieldA', 'fieldD', 'fieldX'),
                                             ('fieldA', 'fieldD')),
                                            TestModelFields),
                         (('fieldA', 'fieldD'),
                          ('fieldA', 'fieldD', 'fieldX')))
        self.assertEqual(sort_unique_tuples((('fieldA', 'fieldE'),
                                             ('fieldA', 'fieldE', 'fieldX')),
                                            TestModelFields),
                         (('fieldA', 'fieldE'),
                          ('fieldA', 'fieldE', 'fieldX')))
        self.assertEqual(sort_unique_tuples((('fieldA', 'fieldD'),
                                             ('fieldA', 'fieldD')),
                                            TestModelFields),
                         (('fieldA', 'fieldD'), ('fieldA', 'fieldD')))


class TestDFS(TestCase):
    def test(self):
        def func(cur_tuple, models, field):
            dic = dict(cur_tuple)
            keys = dic.keys()
            if not 'fieldD' in keys:
                return True
            elif dic['fieldD'] % 3 != 1:
                return False
            if not ('fieldE' in keys and 'fieldH' in keys):
                return True
            elif dic['fieldE'] ^ dic['fieldH']:
                return False
            return True

        dfs.size = 30
        dfs.total = 0
        to_be_computed = []
        cur_tup = [('fieldA', 'X'), ('fieldB', 199), ('fieldC', 'general')]
        unique_together = TestModelFieldsTwo._meta.unique_together
        unique = list(unique_together)
        unique = sort_unique_tuples(unique, TestModelFieldsTwo)
        unique_constraints = [unique_items(un_tuple) for un_tuple in unique]
        constraints = [func] + unique_constraints
        dfs(30, cur_tup, 4, to_be_computed, constraints,
            TestModelFieldsTwo, False)
        self.assertEqual(len(list(TestModelFieldsTwo.objects.all())), 30)
        for mdl in list(TestModelFieldsTwo.objects.all()):
            self.assertEqual(mdl.fieldA, 'X')
            self.assertEqual(mdl.fieldB, 199)
            self.assertEqual(mdl.fieldC, 'general')
            self.assertTrue(mdl.fieldD in [13, 19, 31, 43])
            self.assertTrue(mdl.fieldF in [6, 28, 496, 8128, 33550336])
            self.assertTrue(mdl.fieldG in ['Mathematics', 'Physics',
                                           'Chemistry', 'Biology'])
            self.assertTrue(not (mdl.fieldE ^ mdl.fieldH))


class TestGenerateModel(TestCase):
    def test(self):
        generate_model(TestModelX, 5)
        self.assertEqual(len(TestModelX.objects.all()), 5)
        generate_model(TestModelY, 95)
        generated_models = list(TestModelY.objects.all())
        length = len(generated_models)
        self.assertEqual(len(TestModelX.objects.all()) * 18, length)
        generate_model(TestModelA, 7)
        self.assertEqual(len(TestModelA.objects.all()), 6)
        generate_model(TestModelB, 17)
        self.assertEqual(len(TestModelB.objects.all()), 12)
        generate_model(TestModelC, 53)
        self.assertEqual(len(TestModelC.objects.all()), 12)
        for model in generated_models:
            self.assertTrue(isinstance(model, TestModelY))
            self.assertTrue(model.field1Y in [2, 3, 5, 7, 11, 13])
            self.assertTrue(model.field2Y in ['MMa', 'XXa', 'azz'])
            self.assertTrue(model.field3Y in TestModelX.objects.all())
        to_be_computed_test = generate_model(TestModelFieldsTwo, 50)
        self.assertTrue(to_be_computed_test)
        self.assertEqual(TestModelFieldsTwo, to_be_computed_test[0])
        self.assertTrue(to_be_computed_test[1])
        for fld in to_be_computed_test[1]:
            self.assertTrue(is_related(fld)
                            and 'ManyToMany' in relation_type(fld))
            self.assertEqual(fld.rel.to, TestModelE)
        generate_model(TestModelE, 2, shuffle=False)[0]
        generated_models = list(TestModelE.objects.all())
        for model in generated_models:
            self.assertTrue(isinstance(model, TestModelE))
            self.assertTrue(model.field4E in [1000000009, 1000003, 101])
            self.assertTrue(model.field1E in TestModelB.objects.all())
            self.assertTrue(all([x in TestModelA.objects.all()
                                 for x in model.field2E.all()]))
            self.assertTrue(model.field3E in TestModelC.objects.all())


class TestRecompute(TestCase):
    def test(self):
        c = CycleC(c='3.14159')
        c.save()
        d = CycleD(d=53, dc=c)
        d.save()
        b = CycleB(b=1000000009, bc=c)
        b.save()
        e = CycleE(e=17, ec=c, ed=d)
        e.save()
        a = CycleA(a=999, ab=b, ae=e)
        a.save()
        f = CycleF(f=123, fd=d)
        f.save()
        recompute(CycleD, list_of_fields(CycleD)[2])
        recompute(CycleC, list_of_fields(CycleC)[1])
        recompute(CycleC, list_of_fields(CycleC)[3])
        self.assertTrue(CycleD.objects.all()[0].df)
        self.assertTrue(CycleC.objects.all()[0].ca)
        self.assertTrue(CycleC.objects.all()[0].cc.all())


class TestGenerateData(TestCase):
    def test(self):
        generate_test_data('tests.models', 10)
        length = len(list_of_models(mdls))
        visited = dict(zip(list_of_models(mdls), length * [False]))
        pairs = []
        data_base = dict([(mdl, list(mdl.objects.all()))
                          for mdl in list_of_models(mdls)])
        generated_data = data_base.values()
        nodes = 0
        edges = 0
        for list_model in generated_data:
            for model in list_model:
                visited[model.__class__] = True
                fields = list_of_fields(model.__class__)
                nodes += 1
                for field in fields:
                    if (not is_auto_field(field) and
                       not is_reverse_related(field)):
                        val = getattr(model, field.name)
                        if is_related(field):
                            if 'ManyToMany' in relation_type(field):
                                r = data_base[field.rel.to]
                                self.assertTrue(list(val.all()))
                                self.assertTrue(all([x in r for
                                                     x in list(val.all())]))
                            else:
                                r = data_base[field.rel.to]
                                self.assertTrue(val in r)
                            edges += 1
                        else:
                            this_model = field.model
                            while (this_model != Model and not
                                   (hasattr(this_model, 'TestData') and
                                    hasattr(this_model.TestData, field.name))
                                   and not os.path.exists(
                                    '%s/TestTemplates/sample__%s__%s' %
                                    (this_model._meta.app_label,
                                     this_model.__name__, field.name))):
                                this_model = this_model.__base__
                            if this_model == Model:
                                self.assertEqual(model.__class__,
                                                 AllFieldsModel)
                                sample_values = field_sample_values(field)
                                if val.__class__ == unicode:
                                    val = str(val)
                                self.assertTrue(val.__class__ in
                                                map(lambda val: val.__class__,
                                                    sample_values))
                            elif (field.__class__.__name__ == 'DecimalField' or
                                  field.__class__.__name__ == 'FloatField'):
                                sample_values = map(float,
                                                    field_sample_values(field))
                                val = float(val)
                                self.assertTrue(any(abs(val - fld_value) < 1e-5
                                                    for fld_value in
                                                    sample_values))
                            else:
                                sample_values = map(str,
                                                    field_sample_values(field))
                                val = str(val)
                                self.assertTrue(val in sample_values)
                if model.__class__ == TestModelFields:
                    pr = (model.fieldC, model.fieldA)
                    self.assertFalse(pr in pairs)
                    pairs.append(pr)
                    self.assertTrue((model.fieldB < 50)
                                    or (model.fieldD / 2 % 2 == 1))
        self.assertTrue(all(visited.values()),
                        "Not all the models with sample data are generated.")


class TestDjenerator(TestCase):
    def test(self):
        fl = tempfile.TemporaryFile()
        djenerator('tests', 1, fl, **{'AllFieldsModel': 20})
        self.assertEqual(len(AllFieldsModel.objects.all()), 20)
        fl.seek(0)
        length = len(fl.read())
        self.assertGreater(length, 600)


class TestFieldsGeneratorNumbers(TestCase):
    def test(self):
        counts = {}
        for times in xrange(100):
            for bits in xrange(2, 64):
                for negative_allowed in xrange(0, 2):
                    gen_val = generate_integer(bits, negative_allowed)

                    self.assertIn(gen_val.__class__, [int, long])
                    if not negative_allowed:
                        self.assertGreaterEqual(gen_val, 0)
                        self.assertLess(gen_val, 2 ** (bits - 1))
                    else:
                        self.assertGreaterEqual(gen_val, -2 ** (bits - 1))
                        self.assertLess(gen_val, 2 ** (bits - 1))

            gen_val = generate_int()
            self.assertEqual(gen_val.__class__, int)
            self.assertLessEqual(abs(gen_val), 2 ** 31)
            self.assertLess(gen_val, 2 ** 31)

            gen_val = generate_big_integer()
            self.assertIn(gen_val.__class__, [int, long])
            self.assertLessEqual(abs(gen_val), 2 ** 63)
            self.assertLess(gen_val, 2 ** 63)

            gen_val = generate_small_integer()
            self.assertEqual(gen_val.__class__, int)
            self.assertLessEqual(abs(gen_val), 2 ** 15)
            self.assertLess(gen_val, 2 ** 15)

            gen_val = generate_positive_integer()
            self.assertIn(gen_val.__class__, [int, long])
            self.assertLess(gen_val, 2 ** 31)
            self.assertGreaterEqual(gen_val, 0)

            gen_val = generate_positive_small_integer()
            self.assertEqual(gen_val.__class__, int)
            self.assertLess(gen_val, 2 ** 15)
            self.assertGreaterEqual(gen_val, 0)

            gen_val = generate_boolean()
            self.assertEqual(gen_val.__class__, bool)

            gen_val = generate_boolean(True)
            self.assertTrue((gen_val is None) or (gen_val.__class__ == bool))

            gen_val = generate_ip()
            self.assertEqual(gen_val.__class__, str)
            ip_regex = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
            match = re.search(ip_regex, gen_val)
            self.assertRegexpMatches(gen_val, ip_regex)
            self.assertIsNotNone(match)
            match = map(int, match.groups())
            self.assertTrue(all([x in range(256) for x in match]))

            gen_val = generate_comma_separated_int(random.randint(1, 1000))
            self.assertEqual(gen_val.__class__, str)
            comma_sep_regex = r'^\d{1,3}(?:,\d{3})*$'
            self.assertRegexpMatches(gen_val, comma_sep_regex)

            for digits in xrange(50):
                for decimal in xrange(1, digits):
                    gen_val = generate_decimal(digits, decimal)
                    self.assertEqual(gen_val.__class__, Decimal)

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
        for length in xrange(1, 3):
            gen_sentence = generate_sentence(length)
            self.assertEqual(len(gen_sentence), length)

        for length in xrange(3, 50):
            seperators = [['.'], ['-', '_'], ['@']]
            for sep in seperators:
                for _ in xrange(20):
                    gen_val = generate_sentence(length, seperators=sep)
                    self.assertEqual(gen_val.__class__, str)
                    self.assertLessEqual(len(gen_val), length * 2)
                    reg = r'^(?:\w+(?:%s))*\w+\.$' % str.join('|', sep)
                    self.assertRegexpMatches(gen_val, reg)

            gen_text = generate_text(length)
            txt_re = r'^(?:(?:\w+\s?)+\.)+(?:\s(?:\w+\s?)+\.)*$'
            self.assertLessEqual(len(gen_text), length)
            self.assertRegexpMatches(gen_text, txt_re, gen_text)

            gen_sentence = generate_sentence(length)
            self.assertLessEqual(len(gen_sentence), length)
            sent_re = r'^(?:\w+\s?)+\.$'
            self.assertRegexpMatches(gen_sentence, sent_re, gen_sentence)

            gen_sentence = generate_sentence(length, end_char=['', '.'])
            self.assertLessEqual(len(gen_sentence), length)
            sent_re = r'^(?:\w+\s?)+\.?$'
            self.assertRegexpMatches(gen_sentence, sent_re, gen_sentence)

            gen_sentence = generate_sentence(length, end_char=None)
            self.assertLessEqual(len(gen_sentence), length)
            sent_re = r'^(?:\w+\s?)+$'
            self.assertRegexpMatches(gen_sentence, sent_re, gen_sentence)

            gen_sentence = generate_sentence(length, end_char=['.', ','])
            self.assertLessEqual(len(gen_sentence), length)
            sent_re = r'^(?:\w+\s?)+[\.,]$'
            self.assertRegexpMatches(gen_sentence, sent_re, gen_sentence)


class TestFieldsGeneratorChar(TestCase):
    def test(self):
        ascii_val = dict([(chr(n), n) for n in xrange(128)])
        ascii_rng = lambda beg, end: xrange(ascii_val[beg], ascii_val[end] + 1)
        chr_range = lambda beg, end: map(chr, ascii_rng(beg, end))
        for log in xrange(0, 6):
            lengths = random.sample(range(10 ** log,
                                          10 ** (log + 1) + 1 - bool(log)), 10)
            for length in lengths:
                for tup in itertools.product(*zip(6 * [True], 6 * [False])):
                    lower, upper, digits, special, null_allowed, exact = tup
                    if random.randint(1, 6) < 3:
                        special = ['@', '!', '~']
                    if not (lower or upper or digits or special):
                        continue
                    gen_val = generate_string(length, lower, upper, digits,
                                              special, null_allowed, exact)
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
                    if exact:
                        self.assertEqual(len(gen_val), length)
                    elif not null_allowed:
                        self.assertGreater(len(gen_val), 0)

                    self.assertGreaterEqual(len(gen_val), 0)
                    self.assertLessEqual(len(gen_val), length)

                email = generate_email(length)
                self.assertTrue(isinstance(email, str), email)
                self.assertLessEqual(len(email), length)
                if length >= 7:
                    email_reg = r'^\w+(?:\.\w+)*@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$'
                    self.assertRegexpMatches(email, email_reg)

                url = generate_url(length)
                self.assertTrue(isinstance(url, str), url)
                self.assertLessEqual(len(url), length)
                if length >= 16:
                    url_re = r'^(?:http|ftp|https)://(?:[a-z0-9_\-]+\.?)+/?'
                    url_re += r'(?:/[a-z0-9_\-]+)*/?$'
                    self.assertRegexpMatches(url, url_re)


class TestFieldsGeneratorDateTime(TestCase):
    def test(self):
        for _ in xrange(10000):
            gen_val = generate_date_time()
            self.assertTrue(gen_val)
            self.assertEqual(gen_val.__class__, datetime.datetime)

            gen_val = generate_time()
            self.assertTrue(gen_val)
            self.assertEqual(gen_val.__class__, datetime.time)

            gen_val = generate_date()
            self.assertTrue(gen_val)
            self.assertEqual(gen_val.__class__, datetime.date)

        for _ in xrange(100):
            gen_val = generate_date_time(True)
            self.assertTrue(gen_val)
            self.assertEqual(gen_val.__class__, datetime.datetime)
            now = datetime.datetime.now()
            self.assertLess(abs((gen_val - now).total_seconds()), 10e-4)

            gen_val = generate_time(True)
            self.assertTrue(gen_val)
            self.assertEqual(gen_val.__class__, datetime.time)
            now = datetime.datetime.now().time()
            gen_val_hash = gen_val.second
            gen_val_hash += gen_val.hour * 3600 + gen_val.minute * 60
            now_hash = now.hour * 3600 + now.minute * 60 + now.second
            self.assertLessEqual(gen_val_hash, now_hash + 1)

            gen_val = generate_date(True)
            self.assertTrue(gen_val)
            self.assertEqual(gen_val.__class__, datetime.date)
            now = datetime.datetime.now().date()
            self.assertEqual(gen_val, now)


class TestFileGenerators(TestCase):
    def test(self):
        for _ in xrange(20):
            ext = random.choice(['txt', 'rst', 'md'])
            name = generate_file_name(12, ext)
            self.assertTrue(isinstance(name, str), name)
            self.assertLessEqual(len(name), 12, name)
            self.assertRegexpMatches(name, r'[a-zA-Z_]*\.' + ext, name)

            path = generate_file_path()
            self.assertTrue(os.path.exists(path), path)

            img = generate_png(500, 120)
            beg = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
            # TODO(mostafa-mahmoud): More tests for png format
            self.assertTrue(img.startswith(beg))
