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
from model_reader import list_of_fields
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


def create_model(model, val):
    """ Create models
    
    Creates a new model given a reference to it's class and a list of the values
    of it's variables.
    
    Args : 
        model : A reference to the class of the model that will be created.
        val : A list of tuples having the format (field name, field value)
    
    Returns :
        A model with the values given.
    """
    vals_dictionary = dict(val)
    have_many_to_many_relation = any([x for x in list_of_fields(model) 
                                       if is_related(x) 
                                       and 'ManyToMany' in relation_type(x)])
    if not have_many_to_many_relation:
        mdl = model(**vals_dictionary)
        mdl.save()
        return mdl
    else:
        mdl = model()
        flds = list_of_fields(model)
        dict_T = {}
        for field in flds:
            dict_T[field.name] = relation_type(field)
        for key, val in vals_dictionary.items():
            if not 'ManyToMany' in dict_T[key]:
                setattr(mdl, key, val)
        mdl.save()
        for key, val in vals_dictionary.items():
            if 'ManyToMany' in dict_T[key]:
                for x in val:
                    getattr(mdl, key).add(x)
        mdl.save()
        return mdl


