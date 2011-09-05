#!/usr/bin/env python
"""
This file generates random test data from sample given data for
given models.
"""
import inspect
import random
import settings
from django.core.management import setup_environ
from django.db.models import Model
from model_reader import is_auto_field
from model_reader import is_related
from model_reader import relation_type

setup_environ(settings)

def field_sample_values(field):
    """ Field sample values
    
    Retrieves the list of sample values for a given field.
    
    Args : 
        field : a reference to the class of the field.
    
    Returns :
    a list of sample values for the given field.
    """
    list_field_values = []
    if not is_auto_field(field):
        if is_related(field):
            model = field.rel.to
            list_field_values = list(model.objects.all())
            if 'ManyToMany' in relation_type(field) and list_field_values:
                sz = random.randint(1, len(list_field_values))
                list_field_values = [random.sample(list_field_values, sz)]
        else:
            found = False
            if hasattr(field.model, 'TestData'):
                model = field.model
                while (model.__base__ != Model 
                       and not hasattr(model.TestData, field.name)):
                    model = model.__base__
                if field.name in model.TestData.__dict__.keys():
                    found = True
                    input_method = model.TestData.__dict__[field.name]
                    if isinstance(input_method, str):
                        input_file = open('TestTemplates/' + input_method, 'r')
                        list_field_values = [word[:-1] for word in input_file]
                    elif (isinstance(input_method, list) 
                          or isinstance(input_method, tuple)):
                        list_field_values = input_method
                    else:
                        if inspect.isfunction(input_method):
                            list_field_values = input_method()
            if not found:
                path = 'TestTemplates/sample__%s__%s' % (field.model.__name__,
                                                         field.name)
                input_file = open(path, 'r')
                list_field_values = [word[:-1] for word in input_file]
            # TODO(mostafa.amin93@gmail.com) : Generate totally randomized
            #                                  objects if the file is not found
    return list(list_field_values)


