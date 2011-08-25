#!/usr/bin/env python
"""
This module contains tests for djenerator app.
"""
import models as mdls
from django.test import TestCase
from model_reader import is_instance_of_model
from model_reader import list_of_models
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
                              set(list_of_models(mdls, abstract=True)))
        self.assertEqual(set([ExtendingModel, TestModel0, TestModel1, 
                              TestModelA, TestModelB, TestModelC, TestModelD, 
                              TestModelE, TestModelX, TestModelY, 
                              TestModelFields, SuperClass, ExtendAbstract, 
                              ExtendSuperClass, TestModelFieldsTwo, ProxyExtend,
                              CycleA, CycleB, CycleC, CycleD, CycleE, CycleF]), 
                              set(list_of_models(mdls)))



