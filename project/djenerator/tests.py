
#!/usr/bin/env python
"""
This module contains tests for djenerator app.
"""
import itertools
import models as mdls
import tempfile
import time 
from django.db import models
from django.test import TestCase
from generate_test_data import create_model
from generate_test_data import dependencies
from generate_test_data import dfs
from generate_test_data import djenerator
from generate_test_data import field_sample_values
from generate_test_data import generate_model
from generate_test_data import generate_test_data
from generate_test_data import recompute
from generate_test_data import topological_sort
from model_reader import field_type
from model_reader import is_auto_field
from model_reader import is_instance_of_model
from model_reader import is_related
from model_reader import list_of_fields
from model_reader import list_of_models
from model_reader import module_import
from model_reader import names_of_fields
from model_reader import relation_type
from utility import sort_unique_tuple
from utility import sort_unique_tuples
from utility import unique_items
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


class TestInstanceOfModel(TestCase):
    def test(self):
        models = [TestModel0, TestModel1, TestModelA, TestModelB, TestModelC,
                  TestModelD, TestModelE, TestModelX, TestModelY, ExtendingModel]
        for model in models:
            self.assertTrue(is_instance_of_model(model))
        self.assertFalse(is_instance_of_model(NotExtendingModel))
        def not_extending_model_function():
            pass
        
        self.assertFalse(is_instance_of_model(not_extending_model_function))


class TestListOfModels(TestCase):
    def test(self):
        self.assertEqual(set([ExtendingModel, TestModel0, TestModel1, 
                              TestModelA, TestModelB, TestModelC, TestModelD, 
                              TestModelE, TestModelX, TestModelY, 
                              TestModelFields, SuperClass, ExtendAbstract, 
                              ExtendSuperClass, ProxyExtend, SuperAbstract, 
                              TestModelFieldsTwo, CycleA, CycleB, CycleC, 
                              CycleD, CycleE, CycleF]), 
                              set(list_of_models(mdls, keep_abstract=True)))
        self.assertEqual(set([ExtendingModel, TestModel0, TestModel1, 
                              TestModelA, TestModelB, TestModelC, TestModelD, 
                              TestModelE, TestModelX, TestModelY, 
                              TestModelFields, SuperClass, ExtendAbstract, 
                              ExtendSuperClass, TestModelFieldsTwo, ProxyExtend,
                              CycleA, CycleB, CycleC, CycleD, CycleE, CycleF]), 
                              set(list_of_models(mdls)))


class TestListOfFields(TestCase):
    def test(self):
        self.assertTrue(all([isinstance(*x) 
                             for x in zip(list_of_fields(TestModel1), 
                             [models.AutoField, models.CharField,
                              models.IntegerField, models.ForeignKey])]))
        self.assertTrue(all([isinstance(*x) 
                             for x in zip(list_of_fields(TestModel0),
                             [models.AutoField, models.BooleanField,
                              models.EmailField])]))
        self.assertTrue(all([isinstance(*x) 
                             for x in zip(list_of_fields(TestModelE),
                             [models.AutoField, models.OneToOneField,
                              models.ForeignKey, models.IntegerField,
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


class TestModuleImport(TestCase):
    def test(self):
        self.assertEqual(mdls, module_import('djenerator.models'))
 
 
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
        self.assertTrue(all([x in [a, b] for x in field_sample_values(fld)[0]]))
        vals = [int (x) for x in field_sample_values(list_of_fields(CycleF)[2])]
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
        kwargsa = {'field1D' : 77, 'field2D' : TestModelA.objects.all()}
        dtest = create_model(TestModelD, kwargsa.items())
        self.assertEqual(dtest, TestModelD.objects.get(**kwargsa))


class TestDependencies(TestCase):
    def test(self):
        self.assertEqual(dependencies(TestModelD), [])
        self.assertEqual(set(dependencies(TestModelE)), 
                         set([TestModelB, TestModelC]))
        self.assertEqual(dependencies(TestModelC), [TestModelB])
        self.assertEqual(dependencies(TestModelB), [TestModelA])


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
                                           ('fieldA', 'fieldD', 'fieldG', 
                                            'fieldX'))
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
                                            (('fieldA',), 
                                             ('fieldA', 'fieldC', 'fieldX'), 
                                             ('fieldA', 'fieldD'), 
                                             ('fieldB', 'fieldC', 'fieldX'), 
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
                                            (('fieldA', 'fieldD'), 
                                             ('fieldA', 'fieldD')))


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
        to_be_computed = []
        cur_tup = [('fieldA', 'X'), ('fieldB', 199), ('fieldC', 'general')]
        unique_together = TestModelFieldsTwo._meta.unique_together
        unique = list(unique_together)
        unique = sort_unique_tuples(unique, TestModelFieldsTwo)
        unique_constraints = [unique_items(un_tuple) for un_tuple in unique]
        constraints = [func] + unique_constraints
        dfs(cur_tup, 4, to_be_computed, constraints, TestModelFieldsTwo, False)
        self.assertEqual(len(list(TestModelFieldsTwo.objects.all())), 30)
        for mdl in list(TestModelFieldsTwo.objects.all()):
            self.assertEqual(mdl.fieldA, 'X')
            self.assertEqual(mdl.fieldB, 199)
            self.assertEqual(mdl.fieldC, 'general')
            self.assertTrue(mdl.fieldD in [13, 19, 31, 43])
            self.assertTrue(mdl.fieldF in [6, 28, 496, 8128, 33550336])
            self.assertTrue(mdl.fieldG in ['Mathematics', 'Physics', 'Chemistry', 'Biology'])
            self.assertTrue(not (mdl.fieldE ^ mdl.fieldH))


class TestGenerateModel(TestCase):
    def test(self):
        generate_model(TestModelX, 5)
        generate_model(TestModelY, 95)
        generated_models = list(TestModelY.objects.all())
        length = len(generated_models)
        self.assertTrue(len(TestModelX.objects.all()) * 18 == length)
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
        print '\n\n...entered... ', time.ctime()
        generate_test_data('djenerator.models', 10)
        length = len(list_of_models(mdls))
        visited = dict(zip(list_of_models(mdls), length * [False]))
        pairs = []
        data_base = dict([(mdl, list(mdl.objects.all())) 
                          for mdl in list_of_models(mdls)])
        generated_data = data_base.values()
        print '\n...generated... ', time.ctime(), ' ...testing...'
        nodes = 0
        edges = 0
        for list_model in generated_data:
            for model in list_model:
                visited[model.__class__] = True
                fields = list_of_fields(model.__class__)
                nodes += 1
                for field in fields:
                    if not is_auto_field(field):
                        val = getattr(model, field.name)
                        if is_related(field):
                            if 'ManyToMany' in relation_type(field):
                                r = data_base[field.rel.to]
                                self.assertTrue(list(val.all()))
                                self.assertTrue(all([x in r 
                                                     for x in list(val.all())]))
                            else:
                                r = data_base[field.rel.to]
                                self.assertTrue(val in r)
                            edges += 1 
                        else:
                            sample_values = map(lambda x : str(x),
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
                        "Not all of the models with sample data are generated.")
        print '\n...done...  %s  Nodes :  %d  ,   Edges :  %d' %(time.ctime(), 
                                                                 nodes, edges)


class TestDjenerator(TestCase):
    def test(self):
        fl = tempfile.TemporaryFile()
        djenerator('djenerator', 1, fl, printing=True)
        fl.seek(0)
        length = len(fl.read())
        self.assertGreater(length, 600)


