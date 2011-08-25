#!/usr/bin/env python
"""
This module contains tests for djenerator app.
"""
from django.test import TestCase
from model_reader import is_instance_of_model
from models import ExtendingModel
from models import NotExtendingModel
from models import TestModel0
from models import TestModel1
from models import TestModelA
from models import TestModelB
from models import TestModelC
from models import TestModelD
from models import TestModelE
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



